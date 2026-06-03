#!/usr/bin/env python3
"""Validate compile-only firmware targets (FW-COMPILE-MATRIX-001).

This script consumes ``config/compile-only-targets.json`` and runs one
of two validation modes against the listed product YAMLs:

* ``--metadata-only``: validate the structure and cross-references of
  the target list itself (default-safe; runnable without ESPHome
  installed). The script asserts that every target's ``product_yaml``
  exists, that every target carrying a ``config_string`` appears in
  ``config/firmware-combination-matrix.json``, that every target with
  ``shipment_status`` ``webflash-current`` or ``preview-current``
  appears in ``config/webflash-builds.json``, and that no blocked
  FanTRIAC / PWR target is included unless it is explicitly marked
  ``blocked: true`` and ``webflash_exposure_allowed_now: false``.

* ``--compile``: actually invoke ``esphome compile`` against each
  target's ``product_yaml``. Requires the ``esphome`` CLI on
  ``PATH``. If ESPHome is not available, the script exits non-zero with
  a clear error rather than faking a pass. Each target is logged
  *before* it starts (index/total, config string, YAML path,
  channel/status) and *after* it finishes (PASS / FAIL / TIMEOUT plus
  duration), with output flushed immediately so CI surfaces progress
  live. A per-target timeout (default 20 minutes, ``--timeout-minutes``)
  terminates a single hung ESPHome/PlatformIO compile and records it as
  a ``TIMEOUT`` failure so one stuck target cannot silently stall the
  whole run; the remaining targets still run and a final summary lists
  passed / failed / timed-out / skipped counts and the total duration.

This script is a CI validation lane only. It does not expose new
WebFlash builds, create release artifacts, import firmware, promote
any product, or add any product YAML. See
``docs/compile-only-firmware-validation.md``.

Run with::

    python3 scripts/validate_compile_targets.py --metadata-only
    python3 scripts/validate_compile_targets.py --compile

The default (no flag) is ``--metadata-only`` so the script is safe to
run in environments without ESPHome.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGETS_PATH = REPO_ROOT / "config" / "compile-only-targets.json"
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
MATRIX_PATH = REPO_ROOT / "config" / "firmware-combination-matrix.json"
CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"

REQUIRED_TARGET_FIELDS = (
    "id",
    "product_yaml",
    "reason",
    "shipment_status",
    "hardware_required_for_validation",
    "webflash_exposure_allowed_now",
)

ALLOWED_SHIPMENT_STATUSES = frozenset(
    {"webflash-current", "preview-current", "compile-only"}
)

WEBFLASH_EXPOSED_SHIPMENT_STATUSES = frozenset({"webflash-current", "preview-current"})

BLOCKED_FAN_TOKENS = frozenset({"FanTRIAC"})
BLOCKED_POWER_TOKENS = frozenset({"PWR"})

# Per-target compile timeout. A single ESPHome / PlatformIO compile that
# hangs (toolchain download stall, deadlocked subprocess, etc.) must not
# silently stall the whole --compile run, so each target is bounded by
# this wall-clock limit. No existing repo-wide standard exists, so the
# default is 20 minutes; tune it with --timeout-minutes.
DEFAULT_PER_TARGET_TIMEOUT_MINUTES = 20.0
DEFAULT_PER_TARGET_TIMEOUT_SECONDS = DEFAULT_PER_TARGET_TIMEOUT_MINUTES * 60

# Per-target compile outcomes.
OUTCOME_PASS = "PASS"
OUTCOME_FAIL = "FAIL"
OUTCOME_TIMEOUT = "TIMEOUT"
OUTCOME_SKIP = "SKIP"

# All outcomes in the order they are reported in the summary.
OUTCOME_ORDER = (OUTCOME_PASS, OUTCOME_FAIL, OUTCOME_TIMEOUT, OUTCOME_SKIP)

_OUTCOME_ICONS = {
    OUTCOME_PASS: "✅",
    OUTCOME_FAIL: "❌",
    OUTCOME_TIMEOUT: "⏱",
    OUTCOME_SKIP: "⏭",
}

# A compile runner takes the resolved YAML path and a timeout in seconds
# and returns ``(returncode, combined_output, timed_out)``. ``returncode``
# is ``None`` when the compile timed out (``timed_out`` is then ``True``).
CompileRunner = Callable[[Path, float], Tuple[Optional[int], str, bool]]


@dataclass
class CompileTargetResult:
    """Outcome of one compile-only target's ``esphome compile`` attempt."""

    target_id: str
    config_string: str
    product_yaml: str
    channel: str
    shipment_status: str
    outcome: str
    returncode: Optional[int] = None
    duration_seconds: float = 0.0
    message: str = ""
    output_tail: str = ""

    @property
    def passed(self) -> bool:
        return self.outcome == OUTCOME_PASS


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _config_string_tokens(config_string: str) -> List[str]:
    return config_string.split("-") if config_string else []


class TargetValidationError(Exception):
    pass


def validate_metadata(
    targets_doc: Dict[str, Any],
    builds_doc: Dict[str, Any],
    matrix_doc: Dict[str, Any],
) -> Tuple[int, List[str]]:
    """Return (failed_count, errors) for the metadata-only validation."""
    errors: List[str] = []

    schema_version = targets_doc.get("schema_version")
    if schema_version != 1:
        errors.append(f"schema_version must be 1; got {schema_version!r}")

    targets = targets_doc.get("targets")
    if not isinstance(targets, list):
        errors.append("top-level 'targets' must be a JSON array")
        return len(errors), errors

    builds_index = {
        entry.get("config_string"): entry
        for entry in builds_doc.get("builds", []) or []
        if isinstance(entry, dict) and entry.get("config_string")
    }
    matrix_index = {
        row.get("config_string"): row
        for row in matrix_doc.get("combinations", []) or []
        if isinstance(row, dict) and row.get("config_string")
    }

    seen_ids: Dict[str, int] = {}
    failed = 0

    for idx, target in enumerate(targets, start=1):
        if not isinstance(target, dict):
            errors.append(f"target #{idx}: must be a JSON object")
            failed += 1
            continue

        target_errors: List[str] = []

        for field in REQUIRED_TARGET_FIELDS:
            if field not in target or target[field] in (None, ""):
                target_errors.append(f"target #{idx}: missing required field {field!r}")

        target_id = target.get("id")
        if target_id:
            if target_id in seen_ids:
                target_errors.append(
                    f"target #{idx}: duplicate id {target_id!r} "
                    f"(also at #{seen_ids[target_id]})"
                )
            else:
                seen_ids[target_id] = idx

        product_yaml = target.get("product_yaml")
        if product_yaml:
            path = REPO_ROOT / product_yaml
            if not path.is_file():
                target_errors.append(
                    f"target {target_id!r}: product_yaml not found: {product_yaml}"
                )

        shipment_status = target.get("shipment_status")
        if shipment_status and shipment_status not in ALLOWED_SHIPMENT_STATUSES:
            target_errors.append(
                f"target {target_id!r}: shipment_status {shipment_status!r} "
                f"not in {sorted(ALLOWED_SHIPMENT_STATUSES)}"
            )

        config_string = target.get("config_string")
        if config_string:
            if config_string not in matrix_index:
                if target.get("webflash_grammar_excluded") is True:
                    # The config string is intentionally absent from the
                    # WebFlash one-click firmware-combination grammar — e.g.
                    # the fandac_conflicts_with_airiq mutex keeps AirIQ+FanDAC
                    # out of the token grammar, which cannot encode the
                    # required FanDAC DIP-switch address override (IC2 -> 0x5A).
                    # Such a target is still compile-validated, but it must
                    # document why it is grammar-excluded.
                    if not target.get("webflash_grammar_excluded_reason"):
                        target_errors.append(
                            f"target {target_id!r}: "
                            "webflash_grammar_excluded=true requires a "
                            "non-empty webflash_grammar_excluded_reason"
                        )
                else:
                    target_errors.append(
                        f"target {target_id!r}: config_string "
                        f"{config_string!r} not present in "
                        "config/firmware-combination-matrix.json"
                    )

        if shipment_status in WEBFLASH_EXPOSED_SHIPMENT_STATUSES:
            if not config_string:
                target_errors.append(
                    f"target {target_id!r}: shipment_status "
                    f"{shipment_status!r} requires a config_string"
                )
            elif config_string not in builds_index:
                target_errors.append(
                    f"target {target_id!r}: shipment_status "
                    f"{shipment_status!r} requires config_string "
                    f"{config_string!r} to be in config/webflash-builds.json"
                )
            if target.get("webflash_exposure_allowed_now") is not True:
                target_errors.append(
                    f"target {target_id!r}: shipment_status "
                    f"{shipment_status!r} requires "
                    "webflash_exposure_allowed_now=true"
                )
        elif shipment_status == "compile-only":
            if target.get("webflash_exposure_allowed_now") is True:
                target_errors.append(
                    f"target {target_id!r}: shipment_status compile-only "
                    "must not set webflash_exposure_allowed_now=true"
                )

        # webflash_build_matrix is a product-catalog-level flag and must
        # never be redefined on a compile-only target row; including the
        # key here would imply that flipping it is a compile-only PR's
        # responsibility, which it is not.
        if "webflash_build_matrix" in target:
            target_errors.append(
                f"target {target_id!r}: must not declare "
                "webflash_build_matrix; that flag is owned by "
                "config/product-catalog.json"
            )

        tokens = _config_string_tokens(config_string or "")
        has_blocked_fan = bool(set(tokens) & BLOCKED_FAN_TOKENS)
        has_blocked_power = bool(set(tokens) & BLOCKED_POWER_TOKENS)
        if has_blocked_fan or has_blocked_power:
            if not target.get("blocked"):
                target_errors.append(
                    f"target {target_id!r}: carries blocked token "
                    f"(FanTRIAC and/or PWR) but is not explicitly "
                    "marked blocked=true"
                )
            if target.get("webflash_exposure_allowed_now") is True:
                target_errors.append(
                    f"target {target_id!r}: blocked FanTRIAC / PWR "
                    "target must not claim webflash_exposure_allowed_now=true"
                )
            if shipment_status in WEBFLASH_EXPOSED_SHIPMENT_STATUSES:
                target_errors.append(
                    f"target {target_id!r}: blocked FanTRIAC / PWR "
                    "target must not claim shipment_status "
                    f"{shipment_status!r}"
                )

        if target_errors:
            failed += 1
            errors.extend(target_errors)

    totals = targets_doc.get("totals", {})
    declared_total = totals.get("targets") if isinstance(totals, dict) else None
    if declared_total is not None and declared_total != len(targets):
        errors.append(
            f"totals.targets {declared_total!r} does not match the "
            f"length of the targets array ({len(targets)})"
        )

    return failed, errors


def find_esphome_cli() -> Optional[str]:
    return shutil.which("esphome")


def _make_esphome_compile_runner(esphome: str) -> CompileRunner:
    """Return a :data:`CompileRunner` that shells out to ``esphome compile``.

    The returned callable enforces ``timeout_seconds`` via
    ``subprocess.run(timeout=...)``; on timeout it terminates the
    compile and reports ``timed_out=True`` (with whatever partial output
    was captured) rather than raising.
    """

    def _runner(path: Path, timeout_seconds: float) -> Tuple[Optional[int], str, bool]:
        try:
            proc = subprocess.run(
                [esphome, "compile", str(path)],
                cwd=REPO_ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            output = exc.output or ""
            if isinstance(output, bytes):
                output = output.decode("utf-8", errors="replace")
            return None, output, True
        return proc.returncode, proc.stdout or "", False

    return _runner


def _target_display_fields(target: Dict[str, Any]) -> Tuple[str, str, str, str, str]:
    """Pull the human-facing identity fields out of a target row."""
    target_id = str(target.get("id") or "<unknown>")
    product_yaml = str(target.get("product_yaml") or "")
    config_string = str(target.get("config_string") or "(none)")
    channel = str(target.get("expected_channel") or "-")
    shipment_status = str(target.get("shipment_status") or "(unknown)")
    return target_id, product_yaml, config_string, channel, shipment_status


def _emit(stream: Any, line: str = "") -> None:
    """Write ``line`` and flush immediately so CI shows progress live."""
    stream.write(line + "\n")
    stream.flush()


def run_compile(
    targets_doc: Dict[str, Any],
    *,
    timeout_seconds: float = DEFAULT_PER_TARGET_TIMEOUT_SECONDS,
    compile_runner: Optional[CompileRunner] = None,
    stream: Any = None,
) -> List[CompileTargetResult]:
    """Invoke ``esphome compile`` against each target with live logging.

    Each target is announced before it starts (``index/total``, config
    string, YAML path, channel/status) and reported after it finishes
    (PASS / FAIL / TIMEOUT plus duration). Output is flushed immediately
    so GitHub Actions surfaces per-target progress live instead of going
    dark inside the compile step.

    A per-target wall-clock ``timeout_seconds`` bounds every compile so a
    single hung ESPHome / PlatformIO build is terminated and recorded as
    a ``TIMEOUT`` failure; the loop then continues to the remaining
    targets (matching the existing "run every target, fail at the end"
    behaviour) so the summary always shows every completed target plus
    any that timed out.

    Returns the list of :class:`CompileTargetResult` in target order.
    ``compile_runner`` is injectable for tests; when omitted the ESPHome
    CLI must be on ``PATH`` (otherwise :class:`TargetValidationError` is
    raised before any target runs, exactly as before).
    """
    if stream is None:
        stream = sys.stdout

    if compile_runner is None:
        esphome = find_esphome_cli()
        if esphome is None:
            raise TargetValidationError(
                "esphome CLI not found on PATH; install ESPHome or rerun "
                "with --metadata-only"
            )
        compile_runner = _make_esphome_compile_runner(esphome)

    targets = targets_doc.get("targets", []) or []
    total = len(targets)
    timeout_minutes = timeout_seconds / 60.0

    _emit(
        stream,
        f"Compiling {total} target(s); per-target timeout "
        f"{timeout_seconds:.0f}s (~{timeout_minutes:.1f} min). "
        "A hung target is terminated at the timeout and recorded as "
        "TIMEOUT; the run continues.",
    )

    results: List[CompileTargetResult] = []
    for idx, target in enumerate(targets, start=1):
        (
            target_id,
            product_yaml,
            config_string,
            channel,
            shipment_status,
        ) = _target_display_fields(target)

        _emit(stream)
        _emit(stream, f"[{idx}/{total}] ▶ START {target_id}")
        _emit(stream, f"           config_string : {config_string}")
        _emit(stream, f"           product_yaml  : {product_yaml or '(missing)'}")
        _emit(
            stream,
            f"           channel/status: {channel} / {shipment_status}",
        )

        def _record(
            outcome: str,
            returncode: Optional[int],
            duration: float,
            message: str = "",
            tail: str = "",
        ) -> None:
            result = CompileTargetResult(
                target_id=target_id,
                config_string=config_string,
                product_yaml=product_yaml,
                channel=channel,
                shipment_status=shipment_status,
                outcome=outcome,
                returncode=returncode,
                duration_seconds=duration,
                message=message,
                output_tail=tail,
            )
            results.append(result)
            icon = _OUTCOME_ICONS.get(outcome, "•")
            suffix = f" — {message}" if message else ""
            _emit(
                stream,
                f"[{idx}/{total}] {icon} {outcome} {target_id} "
                f"({duration:.1f}s){suffix}",
            )
            if outcome != OUTCOME_PASS and tail:
                _emit(stream, tail)

        if not product_yaml:
            _record(OUTCOME_FAIL, None, 0.0, message="missing product_yaml")
            continue

        path = REPO_ROOT / product_yaml
        if not path.is_file():
            _record(
                OUTCOME_FAIL,
                None,
                0.0,
                message=f"product_yaml not found: {product_yaml}",
            )
            continue

        start = time.monotonic()
        try:
            returncode, output, timed_out = compile_runner(path, timeout_seconds)
        except Exception as exc:  # noqa: BLE001 - a runner crash is a target failure
            duration = time.monotonic() - start
            _record(
                OUTCOME_FAIL,
                None,
                duration,
                message=f"compile runner raised {type(exc).__name__}: {exc}",
            )
            continue
        duration = time.monotonic() - start
        tail = "\n".join((output or "").splitlines()[-40:])

        if timed_out:
            _record(
                OUTCOME_TIMEOUT,
                None,
                duration,
                message=(
                    f"esphome compile exceeded the per-target timeout of "
                    f"{timeout_seconds:.0f}s (~{timeout_minutes:.1f} min) and "
                    "was terminated; treat as a compile failure and "
                    "investigate the hung target"
                ),
                tail=tail,
            )
        elif returncode == 0:
            _record(OUTCOME_PASS, returncode, duration, tail=tail)
        else:
            _record(
                OUTCOME_FAIL,
                returncode,
                duration,
                message=f"esphome compile exited with rc={returncode}",
                tail=tail,
            )

    return results


def summarize_results(
    results: List[CompileTargetResult],
) -> Dict[str, List[CompileTargetResult]]:
    """Bucket ``results`` by outcome (every known outcome key present)."""
    buckets: Dict[str, List[CompileTargetResult]] = {
        outcome: [] for outcome in OUTCOME_ORDER
    }
    for result in results:
        buckets.setdefault(result.outcome, []).append(result)
    return buckets


def render_summary(
    results: List[CompileTargetResult],
    total_duration_seconds: float,
) -> str:
    """Render the final passed / failed / timed-out / skipped summary."""
    buckets = summarize_results(results)
    passed = buckets[OUTCOME_PASS]
    failed = buckets[OUTCOME_FAIL]
    timed_out = buckets[OUTCOME_TIMEOUT]
    skipped = buckets[OUTCOME_SKIP]

    lines = [
        "=" * 64,
        "Compile-only validation summary",
        "=" * 64,
        f"  Total targets : {len(results)}",
        f"  Passed        : {len(passed)}",
        f"  Failed        : {len(failed)}",
        f"  Timed out     : {len(timed_out)}",
        f"  Skipped       : {len(skipped)}",
        f"  Total duration: {total_duration_seconds:.1f}s "
        f"(~{total_duration_seconds / 60.0:.1f} min)",
    ]

    detail_sections = (
        ("Failed targets", failed),
        ("Timed-out targets", timed_out),
        ("Skipped targets", skipped),
    )
    for heading, rows in detail_sections:
        if not rows:
            continue
        lines.append("")
        lines.append(f"  {heading}:")
        for result in rows:
            icon = _OUTCOME_ICONS.get(result.outcome, "•")
            message = result.message or "(no detail)"
            lines.append(
                f"    {icon} {result.target_id} ({result.config_string}) "
                f"[{result.product_yaml or 'missing product_yaml'}] "
                f"after {result.duration_seconds:.1f}s — {message}"
            )

    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--metadata-only",
        action="store_true",
        help=(
            "Validate compile-only target metadata without invoking the "
            "ESPHome CLI. Default mode."
        ),
    )
    mode.add_argument(
        "--compile",
        action="store_true",
        help=(
            "Invoke `esphome compile` against every target. Requires the "
            "esphome CLI on PATH; fails clearly if not available."
        ),
    )
    parser.add_argument(
        "--timeout-minutes",
        type=float,
        default=DEFAULT_PER_TARGET_TIMEOUT_MINUTES,
        metavar="MINUTES",
        help=(
            "Per-target compile timeout in minutes for --compile mode "
            "(default: %(default)s). A target that exceeds this wall-clock "
            "limit is terminated and recorded as TIMEOUT; the run continues."
        ),
    )
    args = parser.parse_args(argv)

    if args.timeout_minutes <= 0:
        parser.error("--timeout-minutes must be greater than 0")

    targets_doc = _load_json(TARGETS_PATH)
    builds_doc = _load_json(BUILDS_PATH)
    matrix_doc = _load_json(MATRIX_PATH)

    failed, errors = validate_metadata(targets_doc, builds_doc, matrix_doc)

    print("🔍 Validating compile-only firmware targets...\n")
    targets = targets_doc.get("targets", []) or []
    print(
        f"Read {len(targets)} compile-only target(s) from "
        f"{TARGETS_PATH.relative_to(REPO_ROOT)}."
    )

    if errors:
        print(f"\nMetadata errors ({len(errors)}):")
        for error in errors:
            print(f"  ❌ {error}")
        return 1

    print("✅ Metadata validation passed.")

    if not args.compile:
        return 0

    print("\n🔧 Invoking esphome compile for each target...", flush=True)
    timeout_seconds = args.timeout_minutes * 60.0
    start = time.monotonic()
    try:
        results = run_compile(targets_doc, timeout_seconds=timeout_seconds)
    except TargetValidationError as exc:
        print(f"❌ {exc}")
        return 1
    total_duration = time.monotonic() - start

    print()
    print(render_summary(results, total_duration), flush=True)

    buckets = summarize_results(results)
    not_passed = len(buckets[OUTCOME_FAIL]) + len(buckets[OUTCOME_TIMEOUT])
    if not_passed:
        print(
            f"\n❌ {not_passed} compile target(s) did not pass "
            f"({len(buckets[OUTCOME_FAIL])} failed, "
            f"{len(buckets[OUTCOME_TIMEOUT])} timed out).",
            flush=True,
        )
        return 1
    print(f"\n✅ All {len(results)} compile target(s) passed.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

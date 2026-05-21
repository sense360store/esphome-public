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
  a clear error rather than faking a pass.

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
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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
                target_errors.append(
                    f"target {target_id!r}: config_string {config_string!r} "
                    "not present in config/firmware-combination-matrix.json"
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


def run_compile(
    targets_doc: Dict[str, Any],
) -> Tuple[int, List[Tuple[str, int, str]]]:
    """Invoke ``esphome compile`` against each target.

    Returns ``(failed_count, results)`` where ``results`` is a list of
    ``(target_id, return_code, output_tail)`` tuples.
    """
    esphome = find_esphome_cli()
    if esphome is None:
        raise TargetValidationError(
            "esphome CLI not found on PATH; install ESPHome or rerun "
            "with --metadata-only"
        )

    failed = 0
    results: List[Tuple[str, int, str]] = []
    for target in targets_doc.get("targets", []) or []:
        target_id = target.get("id", "<unknown>")
        product_yaml = target.get("product_yaml")
        if not product_yaml:
            results.append((target_id, 1, "missing product_yaml"))
            failed += 1
            continue
        path = REPO_ROOT / product_yaml
        if not path.is_file():
            results.append((target_id, 1, f"product_yaml not found: {product_yaml}"))
            failed += 1
            continue
        proc = subprocess.run(
            [esphome, "compile", str(path)],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        tail = "\n".join(proc.stdout.splitlines()[-40:])
        results.append((target_id, proc.returncode, tail))
        if proc.returncode != 0:
            failed += 1
    return failed, results


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
    args = parser.parse_args(argv)

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

    print("\n🔧 Invoking esphome compile for each target...")
    try:
        compile_failed, results = run_compile(targets_doc)
    except TargetValidationError as exc:
        print(f"❌ {exc}")
        return 1

    for target_id, rc, tail in results:
        status = "✅" if rc == 0 else "❌"
        print(f"{status} {target_id}: rc={rc}")
        if rc != 0 and tail:
            print(tail)

    if compile_failed:
        print(f"\n❌ {compile_failed} compile target(s) failed.")
        return 1
    print(f"\n✅ All {len(results)} compile target(s) passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

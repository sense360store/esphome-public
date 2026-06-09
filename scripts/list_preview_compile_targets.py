#!/usr/bin/env python3
"""Enumerate the preview / manual-preview compile dry-run scope.

RELEASE-PREVIEW-COMPILE-DRYRUN-001.

Read-only helper that derives the set of preview / manual-preview release
targets the hosted compile dry-run lane
(``.github/workflows/preview-compile-dryrun.yml``) should ``esphome compile``,
**scoped to preview targets only**. The scope is read from
``config/preview-release-targets.json``: every ``preview`` /
``advanced-preview`` target EXCEPT the mains-voltage TRIAC target, which is
excluded because it is delivered on the ``advanced-manual-preview`` lane and is
compile-validated via the compile-only lane
(``config/compile-only-targets.json`` / ``compile-only.yml``), not this
preview-compile-dryrun lane. (Its ``HW-005`` buildability blocker is resolved
by TRIAC-UNBLOCK-BUILD-001; it is reported separately rather than compiled
here.)

The current in-scope set is the five preview / manual-preview targets:

  * ``Ceiling-POE-VentIQ-RoomIQ-LED``   (webflash preview, already published)
  * ``Ceiling-POE-RoomIQ-LED``          (webflash preview)
  * ``Ceiling-POE-VentIQ-FanRelay-RoomIQ`` (manual-preview)
  * ``Ceiling-POE-FanPWM``              (manual-preview)
  * ``Ceiling-POE-FanDAC``              (manual-preview)

``Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`` (advanced-manual-preview) is excluded
(``HW-005``) and surfaced by ``--report-excluded``. Stable targets are never
in scope: the baseline ``Ceiling-POE-VentIQ-RoomIQ`` plus the two owner-waiver
promotions ``Ceiling-POE-RoomIQ`` (stable v1.0.5, 2026-06-08) and
``Ceiling-POE-AirIQ-RoomIQ`` (stable v1.0.6, 2026-06-09;
STABLE-PROMOTION-RECONCILE-001) are built by the release workflow, not this
preview dry-run lane.

This script is read-only metadata only. It does **not** publish, build, or
attach any firmware artifact; it does not write ``firmware/sources.json`` or
``manifest.json``; it adds no ``config/webflash-builds.json`` row; it flips no
``config/product-catalog.json`` status; and it claims no compile / build /
hardware proof. A ``compile_validation_status`` it prints is **cited** from
``config/compile-only-targets.json`` (previously-recorded CI status), never
re-proven here.

Usage::

    python3 scripts/list_preview_compile_targets.py                 # table
    python3 scripts/list_preview_compile_targets.py --json          # full JSON
    python3 scripts/list_preview_compile_targets.py --matrix        # GH matrix
    python3 scripts/list_preview_compile_targets.py --config-strings
    python3 scripts/list_preview_compile_targets.py --report-excluded
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "config" / "preview-release-targets.json"
COMPILE_TARGETS_PATH = REPO_ROOT / "config" / "compile-only-targets.json"


class PreviewCompileScopeError(Exception):
    """Raised when the preview compile scope cannot be derived."""


def _load_json(path: Path) -> Any:
    if not path.is_file():
        raise PreviewCompileScopeError(f"not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
        raise PreviewCompileScopeError(f"{path} is not valid JSON: {exc}")


def _is_preview(target: Dict[str, Any]) -> bool:
    return bool(target.get("is_preview_target"))


def _is_triac(target: Dict[str, Any]) -> bool:
    return bool(target.get("is_triac"))


def in_compile_scope(target: Dict[str, Any]) -> bool:
    """A target is compiled by this dry-run iff it is a preview target that is
    not the mains-voltage TRIAC target. TRIAC is excluded here because it is
    delivered on the advanced-manual-preview lane and is compile-validated via
    the compile-only lane (config/compile-only-targets.json), not this preview
    lane (TRIAC-UNBLOCK-BUILD-001 resolved its HW-005 buildability blocker)."""
    return _is_preview(target) and not _is_triac(target)


def is_excluded_preview(target: Dict[str, Any]) -> bool:
    """A preview target deliberately excluded from this compile scope (currently
    only the TRIAC target, compile-validated via the compile-only lane and
    reported separately rather than compiled here)."""
    return _is_preview(target) and _is_triac(target)


def _compile_status_index(compile_doc: Dict[str, Any]) -> Dict[str, str]:
    """Map product_yaml -> compile_validation_status (best-effort, cited only)."""
    index: Dict[str, str] = {}
    for row in compile_doc.get("targets", []) or []:
        if not isinstance(row, dict):
            continue
        yaml_path = row.get("product_yaml")
        status = row.get("compile_validation_status")
        if yaml_path and status and yaml_path not in index:
            index[yaml_path] = status
    return index


def scope_targets(
    manifest: Optional[Dict[str, Any]] = None,
    compile_doc: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Return the in-scope preview compile targets in manifest order."""
    manifest = manifest if manifest is not None else _load_json(MANIFEST_PATH)
    compile_doc = compile_doc if compile_doc is not None else _load_json(
        COMPILE_TARGETS_PATH
    )
    status_by_yaml = _compile_status_index(compile_doc)

    out: List[Dict[str, Any]] = []
    for target in manifest.get("targets", []) or []:
        if not isinstance(target, dict) or not in_compile_scope(target):
            continue
        yaml_path = target.get("yaml_path", "")
        out.append(
            {
                "id": target.get("target_id", ""),
                "config_string": target.get("config_string", ""),
                "product_yaml": yaml_path,
                "channel_tier": target.get("channel_tier", ""),
                "build_channel": target.get("build_channel", ""),
                "delivery_lane": target.get("delivery_lane", ""),
                "is_fan": bool(target.get("is_fan")),
                "expected_artifact_name": target.get("expected_artifact_name", ""),
                # Cited previously-recorded CI status only (or "none" if no
                # product-level compile-only row exists). NOT a fresh proof.
                "prior_compile_validation_status": status_by_yaml.get(
                    yaml_path, "none"
                ),
            }
        )
    return out


def excluded_targets(
    manifest: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Return preview targets excluded from the compile scope (TRIAC / HW-005)."""
    manifest = manifest if manifest is not None else _load_json(MANIFEST_PATH)
    out: List[Dict[str, Any]] = []
    for target in manifest.get("targets", []) or []:
        if not isinstance(target, dict) or not is_excluded_preview(target):
            continue
        out.append(
            {
                "id": target.get("target_id", ""),
                "config_string": target.get("config_string", ""),
                "product_yaml": target.get("yaml_path", ""),
                "channel_tier": target.get("channel_tier", ""),
                "delivery_lane": target.get("delivery_lane", ""),
                # TRIAC-UNBLOCK-BUILD-001: the HW-005 buildability blocker is
                # resolved (build_blocker is now null), so the exclusion reason is
                # no longer "not buildable". TRIAC is excluded from THIS
                # preview-compile-dryrun lane because it is delivered on the
                # advanced-manual-preview lane and is compile-validated via the
                # compile-only lane (config/compile-only-targets.json /
                # compile-only.yml), not this preview lane.
                "reason": (
                    "advanced-manual-preview lane; compile-validated via the "
                    "compile-only lane (config/compile-only-targets.json), not "
                    "this preview-compile-dryrun lane; HW-005 buildability "
                    "resolved (TRIAC-UNBLOCK-BUILD-001)"
                ),
                "build_blocker": target.get("build_blocker"),
            }
        )
    return out


def build_matrix(targets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Return a GitHub Actions ``matrix`` object for the compile job."""
    return {
        "include": [
            {
                "id": t["id"],
                "config_string": t["config_string"],
                "product_yaml": t["product_yaml"],
                "channel_tier": t["channel_tier"],
                "delivery_lane": t["delivery_lane"],
            }
            for t in targets
        ]
    }


def _render_table(targets: List[Dict[str, Any]]) -> str:
    headers = (
        "config_string",
        "channel_tier",
        "delivery_lane",
        "prior_compile_validation_status",
        "product_yaml",
    )
    rows = [headers] + [tuple(str(t[h]) for h in headers) for t in targets]
    widths = [max(len(row[i]) for row in rows) for i in range(len(headers))]
    lines = []
    for r, row in enumerate(rows):
        lines.append("  ".join(row[i].ljust(widths[i]) for i in range(len(headers))))
        if r == 0:
            lines.append("  ".join("-" * widths[i] for i in range(len(headers))))
    lines.append("")
    lines.append(
        f"{len(targets)} preview / manual-preview target(s) in compile-dryrun "
        "scope. 'prior_compile_validation_status' is cited from "
        "config/compile-only-targets.json (previously-recorded CI status only, "
        "not a fresh compile proof)."
    )
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "List the preview / manual-preview compile dry-run scope from "
            "config/preview-release-targets.json. Read-only: publishes, builds, "
            "and attaches nothing."
        ),
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--json",
        action="store_true",
        help="Emit the in-scope target list as a JSON array.",
    )
    mode.add_argument(
        "--matrix",
        action="store_true",
        help="Emit a single-line GitHub Actions matrix object for the compile job.",
    )
    mode.add_argument(
        "--config-strings",
        action="store_true",
        help="Emit only the in-scope config_string values, one per line.",
    )
    mode.add_argument(
        "--report-excluded",
        action="store_true",
        help=(
            "Report preview targets excluded from the compile scope (the TRIAC "
            "HW-005 buildability blocker), one per line, instead of the scope."
        ),
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        if args.report_excluded:
            excluded = excluded_targets()
            if not excluded:
                print("No preview targets are excluded from the compile scope.")
                return 0
            for t in excluded:
                print(
                    f"EXCLUDED {t['config_string']} ({t['delivery_lane']}): "
                    f"{t['reason']}"
                )
            return 0

        targets = scope_targets()
    except PreviewCompileScopeError as exc:
        print(f"list-preview-compile-targets: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(targets, indent=2))
        return 0
    if args.matrix:
        print(json.dumps(build_matrix(targets), separators=(",", ":")))
        return 0
    if args.config_strings:
        for t in targets:
            print(t["config_string"])
        return 0

    print(_render_table(targets))
    return 0


if __name__ == "__main__":
    sys.exit(main())

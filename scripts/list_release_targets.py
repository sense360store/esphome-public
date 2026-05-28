#!/usr/bin/env python3
"""RELEASE-PRODUCT-SELECTION-001: enumerate selectable release targets.

Read-only helper that lists the canonical set of release-eligible
firmware targets the release / release-notes / dry-run workflows can
operate on. Release-eligibility is driven **exclusively** by
``config/webflash-builds.json`` — the same single source of truth the
release workflow (``.github/workflows/firmware-build-release.yml``)
filters by ``version`` + ``channel`` to generate its build matrix.

This script does **not**:

  * publish, build, or attach any firmware artifact;
  * write ``firmware/sources.json`` or ``manifest.json``;
  * invent a target that does not exist in
    ``config/webflash-builds.json``;
  * flip any ``webflash_build_matrix`` value;
  * change any product YAML or WebFlash wrapper.

Usage::

    python3 scripts/list_release_targets.py
    python3 scripts/list_release_targets.py --json
    python3 scripts/list_release_targets.py --config-strings
    python3 scripts/list_release_targets.py \\
        --validate Ceiling-POE-VentIQ-RoomIQ

The ``--validate`` flag exits ``0`` when the given identifier is a
release-eligible target (matching a ``config_string`` in
``config/webflash-builds.json``) **or** the special sentinel
``all-release-eligible``; otherwise it exits ``2`` with a
human-readable error message. FanRelay / FanPWM / FanDAC are not
release-eligible (they are manual-candidate-only, tracked in
``config/manual-firmware-artifacts.json``) and therefore are not
selectable here.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"

# Sentinel for "every release-eligible target in config/webflash-builds.json".
# Mirrored by the release-notes / dry-run workflows so an operator can scope a
# manual dispatch to a single target or to every release-eligible target.
ALL_TARGETS_SENTINEL = "all-release-eligible"

# Fan families that are manual-candidate-only (config/manual-firmware-
# artifacts.json) and must never appear as a release target. Mirrored from
# scripts/plan_room_release_notes.py so the exclusion holds even if a future
# edit accidentally adds a fan token to config/webflash-builds.json.
FAN_FAMILY_TOKENS = ("FanRelay", "FanPWM", "FanDAC")


class ListReleaseTargetsError(Exception):
    """Raised when the release-target catalog cannot be loaded or used."""


def _load_builds(builds_path: Path) -> Dict[str, Any]:
    if not builds_path.is_file():
        raise ListReleaseTargetsError(f"webflash-builds.json not found: {builds_path}")
    try:
        return json.loads(builds_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ListReleaseTargetsError(
            f"webflash-builds.json is not valid JSON: {exc}"
        )


def list_targets(builds_path: Path = DEFAULT_BUILDS_PATH) -> List[Dict[str, Any]]:
    """Return the release-target catalog from ``config/webflash-builds.json``.

    Each entry has ``config_string``, ``channel``, ``version``,
    ``artifact_name``, and ``product_yaml``. Raises
    ``ListReleaseTargetsError`` if a fan family token leaks into the
    release matrix (a guardrail violation).
    """
    builds_doc = _load_builds(builds_path)
    builds = builds_doc.get("builds", [])
    if not isinstance(builds, list):
        raise ListReleaseTargetsError(
            "config/webflash-builds.json: 'builds' must be a list"
        )

    out: List[Dict[str, Any]] = []
    for entry in builds:
        if not isinstance(entry, dict):
            continue
        config_string = str(entry.get("config_string", ""))
        if not config_string:
            continue
        for token in FAN_FAMILY_TOKENS:
            if token.lower() in config_string.lower():
                raise ListReleaseTargetsError(
                    f"guardrail violation: release target {config_string!r} "
                    f"carries fan family token {token!r}; FanRelay / FanPWM / "
                    "FanDAC are manual-candidate-only and must never be "
                    "release-eligible"
                )
        out.append(
            {
                "config_string": config_string,
                "channel": str(entry.get("channel", "")),
                "version": str(entry.get("version", "")),
                "artifact_name": str(entry.get("artifact_name", "")),
                "product_yaml": str(entry.get("product_yaml", "")),
            }
        )

    if not out:
        raise ListReleaseTargetsError(
            "config/webflash-builds.json has no builds; no release targets "
            "are selectable"
        )
    return out


def selectable_config_strings(
    builds_path: Path = DEFAULT_BUILDS_PATH,
) -> List[str]:
    """Return only the ``config_string`` values, preserving file order."""
    return [t["config_string"] for t in list_targets(builds_path)]


def validate_target(
    identifier: str, builds_path: Path = DEFAULT_BUILDS_PATH
) -> Optional[str]:
    """Return ``None`` if ``identifier`` is a release-eligible selection.

    Accepts a release-eligible ``config_string`` from
    ``config/webflash-builds.json`` or the literal
    ``all-release-eligible`` sentinel. Returns a human-readable error
    string otherwise.
    """
    if not identifier:
        return "release target identifier is empty"
    if identifier == ALL_TARGETS_SENTINEL:
        return None
    valid = selectable_config_strings(builds_path)
    if identifier in valid:
        return None
    options = ", ".join([ALL_TARGETS_SENTINEL] + valid)
    return (
        f"{identifier!r} is not a selectable release target; "
        f"valid options are: {options}"
    )


def _render_table(targets: List[Dict[str, Any]]) -> str:
    headers = ("config_string", "channel", "version", "artifact_name")
    rows = [headers] + [
        tuple(t[h] for h in headers) for t in targets  # type: ignore[misc]
    ]
    widths = [max(len(str(row[i])) for row in rows) for i in range(len(headers))]
    lines = []
    for r, row in enumerate(rows):
        lines.append(
            "  ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row))
        )
        if r == 0:
            lines.append("  ".join("-" * widths[i] for i in range(len(headers))))
    lines.append("")
    lines.append(
        f"Special selection: {ALL_TARGETS_SENTINEL!r} expands to every row above."
    )
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "List the canonical selectable release targets from "
            "config/webflash-builds.json. Read-only: does not publish, "
            "build, or attach any firmware artifact."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the target list as JSON (one object per target).",
    )
    parser.add_argument(
        "--config-strings",
        action="store_true",
        help=(
            "Emit only the config_string values, one per line, suitable for "
            "piping into a release dispatch."
        ),
    )
    parser.add_argument(
        "--validate",
        metavar="TARGET",
        default=None,
        help=(
            "Exit 0 if TARGET is a release-eligible selection (a "
            "config_string in config/webflash-builds.json or the literal "
            f"{ALL_TARGETS_SENTINEL!r}); otherwise exit 2."
        ),
    )
    parser.add_argument(
        "--builds",
        type=Path,
        default=DEFAULT_BUILDS_PATH,
        help=argparse.SUPPRESS,
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        targets = list_targets(args.builds)
    except ListReleaseTargetsError as exc:
        print(f"list-release-targets: {exc}", file=sys.stderr)
        return 2

    if args.validate is not None:
        err = validate_target(args.validate, args.builds)
        if err is None:
            print(f"OK: {args.validate!r} is a selectable release target")
            return 0
        print(f"list-release-targets: {err}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(targets, indent=2))
        return 0

    if args.config_strings:
        for t in targets:
            print(t["config_string"])
        return 0

    print(_render_table(targets))
    return 0


if __name__ == "__main__":
    sys.exit(main())

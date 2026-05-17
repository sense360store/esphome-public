#!/usr/bin/env python3
"""Assert WebFlash matrix .bin assets are present in a release-asset directory.

Loads ``config/webflash-builds.json``, filters builds matching the release's
``(version, channel)``, and asserts each matching entry's ``artifact_name``
exists in the asset directory and is at least ``--min-size-bytes`` bytes.

Default behavior is fail-closed: if no matrix entries match
``(version, channel)``, the script fails. A release with no matching matrix
entry is drift, not a harmless no-op. Pass ``--allow-no-matching-builds`` to
relax this for manual / dry-run flows. The release-attach workflow MUST NOT
pass that flag.

Usage:
    python3 scripts/check-webflash-release-assets.py \\
        --dir all-firmware --version 1.0.0 --channel stable

Exits 0 on pass, 1 on failure.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

DEFAULT_MIN_SIZE_BYTES = 100 * 1024  # 100 KB
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Assert WebFlash matrix .bin assets are present in a release-asset "
            "directory."
        ),
    )
    parser.add_argument(
        "--dir",
        required=True,
        help="Directory containing release-asset .bin files",
    )
    parser.add_argument("--version", required=True, help="Release version, e.g. 1.0.0")
    parser.add_argument(
        "--channel",
        required=True,
        help="Release channel (stable, preview, beta)",
    )
    parser.add_argument(
        "--builds",
        default=str(DEFAULT_BUILDS_PATH),
        help="Path to webflash-builds.json (default: config/webflash-builds.json)",
    )
    parser.add_argument(
        "--min-size-bytes",
        type=int,
        default=DEFAULT_MIN_SIZE_BYTES,
        help=f"Minimum acceptable .bin size (default: {DEFAULT_MIN_SIZE_BYTES})",
    )
    parser.add_argument(
        "--allow-no-matching-builds",
        action="store_true",
        help=(
            "Permit zero matrix entries matching (version, channel). "
            "Intended for manual / dry-run flows only. "
            "DO NOT pass for real GitHub Release events."
        ),
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    builds_path = Path(args.builds)
    if not builds_path.is_file():
        print(
            f"FAIL: builds matrix not found at {builds_path}",
            file=sys.stderr,
        )
        return 1

    try:
        builds_doc = json.loads(builds_path.read_text())
    except json.JSONDecodeError as e:
        print(f"FAIL: cannot parse {builds_path}: {e}", file=sys.stderr)
        return 1

    builds = builds_doc.get("builds", [])
    if not isinstance(builds, list):
        print(
            f"FAIL: {builds_path} 'builds' must be a list",
            file=sys.stderr,
        )
        return 1

    matching = [
        b
        for b in builds
        if isinstance(b, dict)
        and b.get("version") == args.version
        and b.get("channel") == args.channel
    ]

    if not matching:
        msg = (
            f"No webflash-builds.json entries match version={args.version} "
            f"channel={args.channel}"
        )
        if args.allow_no_matching_builds:
            print(f"NOTICE: {msg}; bypass flag set, skipping asset check.")
            return 0
        print(
            f"FAIL: {msg}; refusing to publish a release that is not declared "
            f"in the WebFlash build matrix. If this release is intentional, "
            f"add a matching entry to {builds_path} first.",
            file=sys.stderr,
        )
        return 1

    asset_dir = Path(args.dir)
    if not asset_dir.is_dir():
        print(
            f"FAIL: asset directory not found: {asset_dir}",
            file=sys.stderr,
        )
        return 1

    errors: List[str] = []
    checked: List[str] = []
    for entry in matching:
        name = entry.get("artifact_name")
        if not name:
            errors.append(f"matrix entry missing artifact_name: {entry}")
            continue
        path = asset_dir / name
        if not path.is_file():
            errors.append(f"missing asset: {name}")
            continue
        size = path.stat().st_size
        if size < args.min_size_bytes:
            errors.append(f"{name} too small: {size} bytes < min {args.min_size_bytes}")
            continue
        checked.append(f"{name} ({size} bytes)")

    if errors:
        print(
            "FAIL: WebFlash release-asset check failed:",
            file=sys.stderr,
        )
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(
        f"OK: {len(checked)} WebFlash matrix asset(s) present "
        f"and >= {args.min_size_bytes} bytes."
    )
    for line in checked:
        print(f"  - {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

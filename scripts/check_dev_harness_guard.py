#!/usr/bin/env python3
"""DEV-HARNESS-001: CI guard for the bench dev harness (``dev/``).

Two fail-closed checks, run on every push / PR by ``validate.yml``:

1. **The committed overlay must be empty.** ``dev/dev-overlay.yaml`` is the
   bench scratch layer (see ``docs/DEV_WORKFLOW.md``). Its committed state
   must contain only comments and blank lines: finished bench work is
   promoted into the proper package layer (``packages/`` / ``products/``)
   and never merged as overlay content. Any functional line fails the PR.

2. **No build / release declaration may select ``dev/``.** Every build,
   compile, and release matrix in this repo is declaration-driven from
   ``config/*.json`` (ESP-007 and companions) or enumerates ``products/``
   only. This guard walks every string value in every ``config/*.json`` and
   fails if any references a path under ``dev/``, so nothing under ``dev/``
   can ever become a build target or release artifact.

Usage::

    python3 scripts/check_dev_harness_guard.py

Exit code is non-zero if either check fails.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

OVERLAY_PATH = REPO_ROOT / "dev" / "dev-overlay.yaml"
CONFIG_DIR = REPO_ROOT / "config"

OVERLAY_FAILURE_MESSAGE = "promote overlay content into a package layer before merge"


def overlay_problems(overlay_path: Path) -> list[str]:
    """Return problems if the overlay carries anything beyond comments/blanks."""
    if not overlay_path.is_file():
        return [
            f"{overlay_path}: missing — dev/dev-overlay.yaml is a committed "
            "contract file and must exist (empty apart from comments)."
        ]
    try:
        text = overlay_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [f"{overlay_path}: unreadable — {exc}"]

    problems: list[str] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        problems.append(
            f"{overlay_path}:{lineno}: functional content in the committed "
            f"dev overlay: {stripped!r} — {OVERLAY_FAILURE_MESSAGE}."
        )
    return problems


def _iter_strings(node):
    """Yield every string value anywhere inside a parsed JSON document."""
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for key, value in node.items():
            yield from _iter_strings(key)
            yield from _iter_strings(value)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_strings(item)


def _references_dev(value: str) -> bool:
    """True iff the string references a path under the repo's dev/ directory."""
    return value.startswith("dev/") or "/dev/" in value


def config_dev_references(config_dir: Path) -> list[str]:
    """Return problems for any dev/ path referenced by config/*.json."""
    problems: list[str] = []
    if not config_dir.is_dir():
        return [f"{config_dir}: missing — cannot verify build declarations."]
    for path in sorted(config_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            problems.append(f"{path}: unreadable / unparseable JSON — {exc}")
            continue
        for value in _iter_strings(data):
            if _references_dev(value):
                problems.append(
                    f"{path}: declaration references a dev/ path: {value!r} "
                    "— dev/ is bench-only and must never be a build or "
                    "release target."
                )
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--overlay",
        type=Path,
        default=OVERLAY_PATH,
        help="path to the dev overlay YAML (default: dev/dev-overlay.yaml)",
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=CONFIG_DIR,
        help="directory holding the build-declaration JSONs (default: config/)",
    )
    args = parser.parse_args(argv)

    problems = overlay_problems(args.overlay) + config_dev_references(args.config_dir)

    if problems:
        print("DEV-HARNESS-001 guard FAILED:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    print(
        "DEV-HARNESS-001 guard passed: dev overlay is empty and no "
        "config/*.json declaration references dev/."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

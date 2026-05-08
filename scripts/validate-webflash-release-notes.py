#!/usr/bin/env python3
"""Validate a GitHub Release body against the WebFlash release-notes contract.

WebFlash's release importer (``scripts/sync-from-releases.py`` in the
``sense360store/WebFlash`` repo) parses the release body into the sidecar
metadata it stores alongside each ``.bin``. The body must contain four
H2 sections:

    ## Changelog
    ## Known Issues
    ## Features
    ## Hardware Requirements

For ``stable`` channel releases, ``## Changelog`` must be human-authored;
filler text is rejected.

Usage:
    python3 scripts/validate-webflash-release-notes.py path/to/release-notes.md
    python3 scripts/validate-webflash-release-notes.py --text "$RELEASE_BODY"

Optional:
    --channel stable|preview|beta   # default: stable

Exits 0 on pass, 1 on validation failure.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

REQUIRED_SECTIONS = [
    "Changelog",
    "Known Issues",
    "Features",
    "Hardware Requirements",
]

# Sections that must contain at least one non-empty bullet.
NON_EMPTY_SECTIONS = ["Changelog", "Features", "Hardware Requirements"]

# Filler bullets that fail for stable releases. Matched case-insensitively
# after trimming whitespace and trailing punctuation.
FILLER_CHANGELOG_BULLETS = {
    "tbd",
    "todo",
    "placeholder",
    "initial release",
    "first release",
    "firmware release",
    "no changes",
    "n/a",
    "see release notes",
    "nothing to report",
}

H2_RE = re.compile(r"^##\s+(.+?)\s*$")
BULLET_RE = re.compile(r"^\s*[-*+]\s+(.*)$")


def _normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _parse_sections(body: str) -> Dict[str, List[str]]:
    """Parse a Markdown body into ``{section_name: [bullet_text, ...]}``."""
    sections: Dict[str, List[str]] = {}
    current: Optional[str] = None
    for line in body.split("\n"):
        h2 = H2_RE.match(line)
        if h2:
            current = h2.group(1).strip()
            sections.setdefault(current, [])
            continue
        if current is None:
            continue
        bullet = BULLET_RE.match(line)
        if bullet:
            text = bullet.group(1).strip()
            if text:
                sections[current].append(text)
    return sections


def _is_filler(bullet_text: str) -> bool:
    cleaned = bullet_text.strip().rstrip(".:;!? ").strip().lower()
    return cleaned in FILLER_CHANGELOG_BULLETS


def validate_body(body: str, channel: str = "stable") -> List[str]:
    """Return a list of error strings; an empty list means valid."""
    errors: List[str] = []
    body = _normalize_newlines(body or "")
    sections = _parse_sections(body)

    for required in REQUIRED_SECTIONS:
        if required not in sections:
            errors.append(f"Missing required section: ## {required}")

    for section in NON_EMPTY_SECTIONS:
        if section in sections and not sections[section]:
            errors.append(
                f"Section ## {section} must contain at least one bullet"
            )

    if channel == "stable" and sections.get("Changelog"):
        non_filler = [b for b in sections["Changelog"] if not _is_filler(b)]
        if not non_filler:
            errors.append(
                "## Changelog contains only filler text on a stable release; "
                "write a human-authored changelog entry"
            )

    return errors


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a GitHub Release body against the WebFlash contract.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="Path to the release-notes Markdown file",
    )
    parser.add_argument(
        "--text",
        help="Raw release body text (overrides path)",
    )
    parser.add_argument(
        "--channel",
        default="stable",
        help="Release channel (stable, preview, beta). Default: stable.",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.text is None and not args.path:
        parser.error("provide a path or --text")

    if args.text is not None:
        body = args.text
    else:
        body = Path(args.path).read_text(encoding="utf-8")

    errors = validate_body(body, channel=args.channel)
    if errors:
        print("WebFlash release-notes validation FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print(
        f"WebFlash release-notes validation passed (channel={args.channel}).",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

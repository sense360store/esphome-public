#!/usr/bin/env python3
"""SEC-ESP-FALLBACK-AP-001: reject known fallback-AP password literals.

Finding #1 of security.md: the fallback access-point password used to be a
plaintext literal committed in YAML and baked identically into every shipped
unit (``Sense360Fallback`` in ``packages/base/wifi.yaml`` and ``sense360poe``
in ``products/sense360-poe.yaml``). ``packages/base/wifi.yaml`` now reads the
value from ``!secret fallback_ap_password`` instead, so the password is a
per-build secret.

This build-time guard fails if either of those historical literals reappears,
either:

  * as the effective ``fallback_ap_password`` in a provisioned ``secrets.yaml``
    (pass ``--secrets secrets.yaml``), or
  * as a committed ``fallback_ap_password:`` assignment under ``packages/`` or
    ``products/`` (a defence against a revert of the wifi.yaml change).

It is intentionally an EXACT, case-sensitive match against the two banned
literals only. The disposable test/build credentials the CI lanes inject
(``fallback123``, ``sense360fallback``) are deliberately NOT banned, so every
compile-only / preview / release lane stays green.

Usage::

    # committed-config scan only (e.g. on every push / PR):
    python3 scripts/check_fallback_ap_password.py

    # also check a provisioned secrets.yaml (e.g. inside a build lane):
    python3 scripts/check_fallback_ap_password.py --secrets secrets.yaml

Exit code is non-zero if any banned literal is found.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# The two hardcoded literals called out by SEC-ESP-FALLBACK-AP-001 finding #1.
# EXACT, case-sensitive: the CI/build test credentials "fallback123" and
# "sense360fallback" are disposable and intentionally allowed.
BANNED_LITERALS = ("Sense360Fallback", "sense360poe")

# Directories whose committed YAML compiles into firmware.
SCAN_DIRS = ("packages", "products")

# Matches `fallback_ap_password: <value>` with optional quotes, capturing the
# value so it can be compared against BANNED_LITERALS.
_ASSIGN_RE = re.compile(
    r"""^\s*fallback_ap_password\s*:\s*["']?(?P<value>[^"'\s#]+)["']?""",
    re.MULTILINE,
)


def is_banned(value: str) -> bool:
    """True iff value is one of the banned committed literals (exact match)."""
    return value in BANNED_LITERALS


def scan_committed(root: Path) -> list[str]:
    """Return human-readable problems for banned literals in committed YAML."""
    problems: list[str] = []
    for rel in SCAN_DIRS:
        base = root / rel
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.yaml")) + sorted(base.rglob("*.yml")):
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for match in _ASSIGN_RE.finditer(text):
                value = match.group("value")
                if is_banned(value):
                    problems.append(
                        f"{path.relative_to(root)}: fallback_ap_password is the "
                        f"banned literal {value!r}; use a per-build "
                        "`!secret fallback_ap_password` value instead."
                    )
    return problems


def check_secrets(path: Path) -> list[str]:
    """Return problems if secrets.yaml sets a banned fallback_ap_password."""
    if not path.is_file():
        # No provisioned secrets to check (e.g. a metadata-only lane). The
        # committed-config scan still runs; this is not an error.
        return []
    problems: list[str] = []
    text = path.read_text(encoding="utf-8")
    for match in _ASSIGN_RE.finditer(text):
        value = match.group("value")
        if is_banned(value):
            problems.append(
                f"{path}: fallback_ap_password is the banned literal "
                f"{value!r}; generate a unique per-build value "
                "(see secrets.example.yaml)."
            )
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--secrets",
        default=None,
        help="Path to a provisioned secrets.yaml to also check (optional).",
    )
    parser.add_argument(
        "--root",
        default=str(REPO_ROOT),
        help="Repo root to scan (defaults to the repository root).",
    )
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    problems = scan_committed(root)
    if args.secrets:
        problems += check_secrets(Path(args.secrets))

    if problems:
        sys.stderr.write(
            "ERROR: banned fallback-AP password literal(s) found "
            "(SEC-ESP-FALLBACK-AP-001):\n"
        )
        for problem in problems:
            sys.stderr.write(f"  - {problem}\n")
        return 1

    print(
        "OK: no banned fallback-AP password literals "
        f"({', '.join(repr(x) for x in BANNED_LITERALS)})."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

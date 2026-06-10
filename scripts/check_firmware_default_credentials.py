#!/usr/bin/env python3
"""SEC-ESP-BUILD-GATES-001: refuse to ship firmware carrying default credentials.

SECURITY-AUDIT-2026-06 finding H1: the release pipeline used to bake a fixed,
public credential set into every released ``.bin`` (the placeholder API
encryption key plus shared OTA / web / fallback-AP passwords), so one
public-repo read controlled every device still on defaults. Finding H2:
two earlier fallback-AP literals remain readable in public git history
forever and are permanently burned.

This gate is the permanent backstop, independent of HOW build secrets are
sourced: it scans every produced firmware binary for a denylist of known
default / placeholder / burned credential byte-strings and FAILS the release
if any appears in any artifact. It runs in firmware-build-release.yml after
compile (per product) and again in the release job over the full downloaded
artifact set, before anything is attached to the GitHub Release.

The denylist values below are not secrets: every one of them is already
public (in workflow history, in the public audit, or extractable from
previously published binaries). They exist here solely as scan needles.
New text elsewhere should reference them by credential-class name, not value.

Exit codes:
  0  all scanned binaries are clean
  1  at least one binary matched a denylisted credential (release must fail)
  2  usage error / nothing to scan (fail closed: an empty artifact set must
     never pass the gate silently)

Usage::

    python3 scripts/check_firmware_default_credentials.py FILE [FILE ...]
    python3 scripts/check_firmware_default_credentials.py --dir all-firmware
"""

from __future__ import annotations

import argparse
import base64
import sys
from pathlib import Path

# The all-'a' placeholder API encryption key (secrets.example.yaml ships it so
# `esphome config` validates on a fresh checkout; it must never ship in a
# binary). ESPHome stores the key in flash as the DECODED 32-byte material,
# not the base64 literal, so both forms are denylisted.
API_KEY_PLACEHOLDER_B64 = b"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa="
API_KEY_PLACEHOLDER_RAW = base64.b64decode(API_KEY_PLACEHOLDER_B64)

# ---------------------------------------------------------------------------
# Denylist: (credential_class, needle_label, needle_bytes)
#
# credential_class matches the secrets.yaml key the value belonged to. The
# four device-control credential classes — api_encryption_key, ota_password,
# web (username/password), fallback_ap_password — are NEVER excluded from
# this list. Case-sensitive exact byte search.
# ---------------------------------------------------------------------------
DENYLIST: tuple[tuple[str, str, bytes], ...] = (
    # --- api_encryption_key (native API control of the device) ---
    ("api_encryption_key", "placeholder key, base64 literal", API_KEY_PLACEHOLDER_B64),
    (
        "api_encryption_key",
        "placeholder key, decoded 32-byte material",
        API_KEY_PLACEHOLDER_RAW,
    ),
    # --- ota_password (persistent firmware overwrite) ---
    ("ota_password", "shipped release default", b"sense360-ota-default"),
    ("ota_password", "CI test-lane value", b"test-ota-password"),
    # --- web_password (web UI auth on :80) ---
    # web_username "admin" is intentionally NOT a standalone needle: a bare
    # 5-byte generic token false-positives on legitimate binary content
    # (e.g. embedded web assets). The web credential class is enforced via
    # its password needles, which are the actual secret material.
    ("web_password", "shipped release default", b"sense360admin"),
    ("web_password", "CI test-lane value", b"test_web_password"),
    # --- fallback_ap_password (RF-range captive-portal access) ---
    ("fallback_ap_password", "shipped release default", b"sense360fallback"),
    ("fallback_ap_password", "CI test-lane value", b"fallback123"),
    # Audit H2 forward half: the two pre-SEC-ESP-FALLBACK-AP-001 literals are
    # readable in public git history forever and are treated as permanently
    # burned. They must never appear in a future release binary.
    (
        "fallback_ap_password",
        "burned historical literal (audit H2)",
        b"Sense360Fallback",
    ),
    ("fallback_ap_password", "burned historical literal (audit H2)", b"sense360poe"),
    # --- wifi_ssid / wifi_password (CI test-lane values only; see below) ---
    ("wifi_ssid", "CI test-lane value", b"TestNetwork"),
    ("wifi_password", "CI test-lane value", b"TestPassword123"),
)

# ---------------------------------------------------------------------------
# Intentionally-public setup-network credentials — EXCLUDED from the denylist.
#
# Released firmware deliberately ships trying to join the fixed first-boot
# setup network (wifi_ssid "Sense360_Setup" / wifi_password "sense360setup")
# so a user can bring a fresh device online by creating a hotspot with that
# name. These two values are setup-only UX, are documented as public in
# docs/security/release-firmware-credential-posture.md, and grant no control
# over the device's API / OTA / web surfaces. ONLY these two values are
# excluded; the api/ota/web/fallback credential classes are never excluded.
# ---------------------------------------------------------------------------
INTENTIONALLY_PUBLIC_SETUP_CREDENTIALS: tuple[bytes, ...] = (
    b"Sense360_Setup",
    b"sense360setup",
)

# Classes that must always be represented in DENYLIST (regression pin; the
# unit test asserts this too).
NEVER_EXCLUDED_CLASSES = (
    "api_encryption_key",
    "ota_password",
    "web_password",
    "fallback_ap_password",
)


def scan_blob(data: bytes) -> list[tuple[str, str]]:
    """Return (credential_class, needle_label) for every denylist match."""
    return [
        (cred_class, label) for cred_class, label, needle in DENYLIST if needle in data
    ]


def scan_files(paths: list[Path]) -> list[str]:
    """Scan binaries; return human-readable problems (empty when clean)."""
    problems: list[str] = []
    for path in paths:
        try:
            data = path.read_bytes()
        except OSError as exc:
            problems.append(f"{path}: cannot read artifact: {exc}")
            continue
        for cred_class, label in scan_blob(data):
            problems.append(
                f"{path}: contains a denylisted default credential — "
                f"class [{cred_class}] ({label})"
            )
    return problems


def collect_binaries(args_paths: list[str], directory: str | None) -> list[Path]:
    """Resolve positional paths plus --dir/*.bin into a sorted file list."""
    paths: list[Path] = []
    for raw in args_paths:
        paths.append(Path(raw))
    if directory is not None:
        paths.extend(sorted(Path(directory).glob("*.bin")))
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail if any firmware binary carries a known default/"
        "placeholder credential (SEC-ESP-BUILD-GATES-001).",
    )
    parser.add_argument(
        "binaries",
        nargs="*",
        help="Firmware .bin file(s) to scan.",
    )
    parser.add_argument(
        "--dir",
        dest="directory",
        default=None,
        help="Also scan every *.bin directly inside this directory.",
    )
    args = parser.parse_args(argv)

    paths = collect_binaries(args.binaries, args.directory)

    if not paths:
        sys.stderr.write(
            "ERROR: no firmware binaries to scan (SEC-ESP-BUILD-GATES-001 "
            "fails closed: an empty artifact set must not pass the gate).\n"
        )
        return 2

    missing = [p for p in paths if not p.is_file()]
    if missing:
        for p in missing:
            sys.stderr.write(f"ERROR: artifact does not exist: {p}\n")
        return 2

    problems = scan_files(paths)
    if problems:
        sys.stderr.write(
            "ERROR: default/placeholder credential material found in release "
            "artifact(s) (SEC-ESP-BUILD-GATES-001 / SECURITY-AUDIT-2026-06 "
            "H1, H2):\n"
        )
        for problem in problems:
            sys.stderr.write(f"  - {problem}\n")
        sys.stderr.write(
            "The release must not ship. Fix the build secret posture "
            "(scripts/apply_release_secret_posture.py) before publishing.\n"
        )
        return 1

    print(
        f"OK: {len(paths)} firmware binar{'y' if len(paths) == 1 else 'ies'} "
        f"scanned against {len(DENYLIST)} denylisted credential needles; "
        "no default/placeholder credential material found."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

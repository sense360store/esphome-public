#!/usr/bin/env python3
"""SEC-ESP-BUILD-GATES-001: strip shared compile-time credentials for release.

SECURITY-AUDIT-2026-06 finding H1: release builds used to bake one fixed,
public credential set (placeholder API encryption key, shared OTA / web /
fallback-AP passwords) into every published binary. A prebuilt ``.bin``
cannot carry per-device secrets, and no first-boot flow exists yet that
could set them on the user's own install (Improv-style provisioning covers
WiFi only and is not present in this tree). Until that provisioning flow
lands (queue item SEC-ESP-PROVISIONING-001), released firmware ships
UNPROVISIONED instead of falsely secured:

  * ``api:`` without an ``encryption:`` block — the native API is
    unencrypted rather than "encrypted" with a publicly known key;
  * ``ota: - platform: esphome`` without a ``password:`` — OTA is
    unauthenticated rather than gated by a public shared password;
  * ``web_server:`` without an ``auth:`` block — the web UI is open
    rather than guarded by public shared credentials;
  * ``wifi: ap:`` without a ``password:`` — the fallback/setup AP is an
    open captive-portal hotspot rather than "protected" by a public
    shared password.

Attacker capability is unchanged (every removed value was already public);
what changes is that the firmware no longer asserts security it does not
have, and no shared credential class exists for a public-repo read to
unlock. See docs/security/release-firmware-credential-posture.md for the
resulting fresh-flash posture and the user-facing first-boot steps.

This script rewrites the four ``packages/base/`` files IN THE RELEASE
WORKSPACE ONLY (the same pattern as the workflow's external_components
rewrite — never committed). The committed YAML keeps its ``!secret``
references so self-builders still compile fully secured firmware from
their own ``secrets.yaml``. Every transform is an exact one-shot match:
if a base package no longer has the expected shape, this script FAILS
CLOSED and the release fails loudly instead of silently baking a shared
secret. The artifact-level denylist gate
(scripts/check_firmware_default_credentials.py) remains the final
backstop regardless of what happens here.

Exit codes: 0 = posture applied and verified; 1 = failure (release must
not proceed).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

MARKER = "CI-only release-posture override (SEC-ESP-BUILD-GATES-001)"

HEADER_TEMPLATE = (
    "# {marker}:\n"
    "# {description}\n"
    "# Applied in the release workspace only — never committed. The committed\n"
    "# file keeps its !secret reference for self-builders. See\n"
    "# docs/security/release-firmware-credential-posture.md.\n"
)

# (relative path, description for the header, exact block to remove)
# Exact one-shot matches on the committed shapes. yamllint keeps these files
# style-stable; if one is reshaped, the release lane fails closed here until
# this script is updated in the same PR.
TRANSFORMS: tuple[tuple[str, str, str], ...] = (
    (
        "packages/base/api_encrypted.yaml",
        "api.encryption removed: the native API ships unencrypted instead of"
        " keyed with the public placeholder.",
        "  encryption:\n    key: !secret api_encryption_key\n",
    ),
    (
        "packages/base/ota.yaml",
        "ota password removed: OTA ships unauthenticated instead of gated by"
        " a public shared password.",
        "    password: !secret ota_password\n",
    ),
    (
        "packages/base/logging.yaml",
        "web_server.auth removed: the web UI ships open instead of guarded by"
        " public shared credentials.",
        "  auth:\n    username: !secret web_username\n    password: !secret web_password\n",
    ),
    (
        "packages/base/wifi.yaml",
        "fallback-AP password removed: the setup/fallback AP ships as an open"
        " captive-portal hotspot instead of using a public shared password.",
        "    password: !secret fallback_ap_password\n",
    ),
)

# After the transforms, no packages/base YAML may still reference any of the
# four stripped secret keys.
STRIPPED_SECRET_RE = re.compile(
    r"!secret\s+(api_encryption_key|ota_password|web_username|web_password|"
    r"fallback_ap_password)\b"
)

# The setup path must survive the patch: released firmware still joins the
# intentionally-public setup network and still serves the captive portal.
WIFI_REQUIRED_FRAGMENTS = (
    "!secret wifi_ssid",
    "!secret wifi_password",
    "captive_portal:",
)


def apply_posture(root: Path) -> list[str]:
    """Apply all transforms under root; return problems (empty on success)."""
    problems: list[str] = []

    for rel_path, description, block in TRANSFORMS:
        path = root / rel_path
        if not path.is_file():
            problems.append(f"{rel_path}: file does not exist")
            continue
        text = path.read_text(encoding="utf-8")
        if MARKER in text:
            problems.append(
                f"{rel_path}: release posture already applied (one-shot "
                "transform refused)"
            )
            continue
        count = text.count(block)
        if count != 1:
            problems.append(
                f"{rel_path}: expected exactly 1 occurrence of the secret "
                f"block to strip, found {count}; the committed file shape "
                "changed — update scripts/apply_release_secret_posture.py "
                "in the same PR (failing closed)"
            )
            continue
        new_text = HEADER_TEMPLATE.format(marker=MARKER, description=description)
        new_text += text.replace(block, "", 1)
        path.write_text(new_text, encoding="utf-8")
        print(f"stripped shared credential config from {rel_path}")

    if problems:
        return problems

    # Post-conditions (defence in depth).
    base_dir = root / "packages" / "base"
    for path in sorted(base_dir.glob("*.yaml")):
        match = STRIPPED_SECRET_RE.search(path.read_text(encoding="utf-8"))
        if match:
            problems.append(
                f"{path.relative_to(root)}: still references "
                f"!secret {match.group(1)} after the posture patch"
            )

    wifi_text = (root / "packages/base/wifi.yaml").read_text(encoding="utf-8")
    for fragment in WIFI_REQUIRED_FRAGMENTS:
        if fragment not in wifi_text:
            problems.append(
                f"packages/base/wifi.yaml: required setup-path fragment "
                f"{fragment!r} missing after the posture patch"
            )

    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=str(REPO_ROOT),
        help="Tree to patch (defaults to the repository root; tests pass a "
        "temporary copy).",
    )
    args = parser.parse_args(argv)

    problems = apply_posture(Path(args.root).resolve())
    if problems:
        sys.stderr.write(
            "ERROR: release credential posture could NOT be applied "
            "(SEC-ESP-BUILD-GATES-001 fails closed — do not release):\n"
        )
        for problem in problems:
            sys.stderr.write(f"  - {problem}\n")
        return 1

    print(
        "OK: release credential posture applied — released firmware carries "
        "no shared api/ota/web/fallback credential material; only the "
        "intentionally-public setup-network credentials remain."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""SEC-ESP-BUILD-GATES-001: reject the placeholder api_encryption_key on
release/production builds (security.md finding #4).

The example/CI ``api_encryption_key`` is an obvious all-"a" base64 placeholder
so ``esphome config`` validates on a fresh checkout. Nothing previously stopped
a real *release/production* firmware from compiling with that placeholder,
which would leave the native-API encryption effectively public.

This pre-build gate fails a production build (``--channel stable`` or
``--release``) whose ``api_encryption_key`` is a known placeholder / CI literal,
while still allowing the placeholder for ``compile-only`` / ``preview`` / ``beta``
validation. To publish a stable release, set a unique ``API_ENCRYPTION_KEY``
GitHub Actions secret (the workflow feeds it into the build's secrets.yaml);
otherwise the build fails closed here rather than shipping the placeholder.

Usage::

    # inside the release build job, after secrets.yaml is provisioned:
    python3 scripts/check_api_encryption_key.py \\
        --secrets secrets.yaml --channel "$CHANNEL"

    # or check an explicit value:
    python3 scripts/check_api_encryption_key.py --value "$KEY" --release

Exit codes: 0 = allowed, 1 = rejected (placeholder on a production build),
2 = usage error (e.g. no key found for a production build).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# The obvious all-"a" placeholder shipped in secrets.example.yaml and injected
# by every CI lane's throwaway secrets.
EXAMPLE_KEY = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa="

# Channels that ship a real, production firmware artifact. Only these are
# gated; preview / beta / compile-only intentionally keep using the placeholder.
PRODUCTION_CHANNELS = {"stable"}

# A real 256-bit key is never a single repeated base64 character; this catches
# all-"a", all-"b", ... placeholders even if a new one is introduced.
_SINGLE_CHAR_B64 = re.compile(r"^(.)\1{42}=$")

_KEY_LINE_RE = re.compile(
    r"""^\s*api_encryption_key\s*:\s*["']?(?P<value>[^"'\s#]+)["']?""",
    re.MULTILINE,
)


def is_placeholder_key(value: str | None) -> bool:
    """True for an empty/missing key or a known placeholder/CI literal."""
    if value is None:
        return True
    value = value.strip()
    if value == "":
        return True
    if value == EXAMPLE_KEY:
        return True
    if _SINGLE_CHAR_B64.match(value):
        return True
    return False


def is_production(channel: str | None, release: bool) -> bool:
    if release:
        return True
    return (channel or "").strip().lower() in PRODUCTION_CHANNELS


def read_key_from_secrets(path: Path) -> str | None:
    if not path.is_file():
        return None
    match = _KEY_LINE_RE.search(path.read_text(encoding="utf-8"))
    return match.group("value") if match else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--secrets", default="secrets.yaml",
                        help="Path to the provisioned secrets.yaml (default: secrets.yaml).")
    parser.add_argument("--value", default=None,
                        help="Check this explicit key value instead of reading --secrets.")
    parser.add_argument("--channel", default=None,
                        help="Release channel (stable / preview / beta).")
    parser.add_argument("--release", action="store_true",
                        help="Force production semantics regardless of --channel.")
    args = parser.parse_args(argv)

    production = is_production(args.channel, args.release)

    if args.value is not None:
        key = args.value
        source = "--value"
    else:
        key = read_key_from_secrets(Path(args.secrets))
        source = args.secrets

    if not production:
        print(
            f"OK: non-production build (channel={args.channel!r}); "
            "placeholder api_encryption_key is allowed."
        )
        return 0

    if key is None:
        sys.stderr.write(
            f"ERROR: production build (channel={args.channel!r}) but no "
            f"api_encryption_key found in {source} (SEC-ESP-BUILD-GATES-001).\n"
            "Set a unique API_ENCRYPTION_KEY secret before publishing.\n"
        )
        return 2

    if is_placeholder_key(key):
        sys.stderr.write(
            "ERROR: production build (channel="
            f"{args.channel!r}) is using a placeholder / CI api_encryption_key "
            "(SEC-ESP-BUILD-GATES-001).\n"
            "Set a unique API_ENCRYPTION_KEY GitHub Actions secret (generate one "
            "with `openssl rand -base64 32`) so the release does not ship the "
            "public placeholder key.\n"
        )
        return 1

    print(
        f"OK: production build (channel={args.channel!r}) has a non-placeholder "
        "api_encryption_key."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

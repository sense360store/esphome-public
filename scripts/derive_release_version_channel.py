#!/usr/bin/env python3
"""RELEASE-004: Normalize a GitHub release tag to (version, channel).

The Build & Release Firmware workflow filters
``config/webflash-builds.json`` by ``(version, channel)``. Stable releases
use plain semantic tags like ``v1.0.0``. Preview releases need a suffix
so a preview tag can coexist with the stable tag of the same firmware
version (e.g. ``v1.0.0`` is already taken by stable Release-One, so the
LED preview cannot reuse that tag).

This script encodes the agreed mapping:

    v1.0.0               + prerelease=false -> version=1.0.0, channel=stable
    v1.0.0-led-preview   + prerelease=true  -> version=1.0.0, channel=preview
    v1.0.0-preview       + prerelease=true  -> version=1.0.0, channel=preview
    v1.0.0-experimental  + prerelease=true  -> version=1.0.0, channel=experimental

Fail-closed:

* Any unknown suffix on a prerelease tag is rejected so an operator typo
  fails at this step with a clear message rather than later in the
  matrix-filter step with the less informative
  "no config/webflash-builds.json entries matched ..." error.
* Any suffix on a non-prerelease tag is rejected — stable releases must
  use plain semantic tags.

Invocation: env-driven so the workflow can pass ``GITHUB_REF_NAME`` and
``PRERELEASE`` without quoting risks.

    GITHUB_REF_NAME=v1.0.0-led-preview PRERELEASE=true \\
        python3 scripts/derive_release_version_channel.py

Emits two lines to stdout::

    version=1.0.0
    channel=preview

If ``GITHUB_OUTPUT`` is set, the same two lines are appended to that file
in the GitHub Actions ``name=value`` format. Exits non-zero with a
human-readable message on any rejection.
"""

from __future__ import annotations

import os
import sys
from typing import Dict, Tuple

# RELEASE-004 + TRIAC-COMMISSIONING-001: prerelease tag suffix -> build channel.
# ``-led-preview`` / ``-preview`` map to the ``preview`` channel; ``-experimental``
# maps to the ``experimental`` self-build mains channel (the experimental_lane
# defined by docs/decisions/COMPLIANCE-001-RESOLUTION-001.md and recorded in
# config/release-channel-policy.json). A bare prerelease tag (no suffix) stays
# ``preview``. Insertion order matters: ``-led-preview`` must be tested before
# ``-preview`` because the longer suffix also ends with ``-preview``.
PRERELEASE_SUFFIX_TO_CHANNEL: Dict[str, str] = {
    "-led-preview": "preview",
    "-preview": "preview",
    "-experimental": "experimental",
}

# Back-compat alias: the preview-only subset of the suffix map. Retained for any
# importer that referenced the original tuple.
ALLOWED_PREVIEW_SUFFIXES: Tuple[str, ...] = tuple(
    suffix for suffix, channel in PRERELEASE_SUFFIX_TO_CHANNEL.items() if channel == "preview"
)

# Every recognised prerelease suffix (preview + experimental), used in the
# unrecognised-suffix error message.
ALLOWED_PRERELEASE_SUFFIXES: Tuple[str, ...] = tuple(PRERELEASE_SUFFIX_TO_CHANNEL)


class DeriveError(Exception):
    """Raised when a tag cannot be normalized."""


def derive(tag: str, prerelease: bool) -> Tuple[str, str]:
    """Return ``(version, channel)`` for ``tag`` and ``prerelease``.

    ``tag`` may or may not have a leading ``v``. Raises ``DeriveError`` on
    any tag shape that is not in the allowed set for ``prerelease``.
    """
    if not tag:
        raise DeriveError("release tag is empty")

    raw = tag[1:] if tag.startswith("v") else tag

    if not raw:
        raise DeriveError(f"release tag {tag!r} is empty after stripping 'v'")

    if prerelease:
        for suffix, channel in PRERELEASE_SUFFIX_TO_CHANNEL.items():
            if raw.endswith(suffix):
                version = raw[: -len(suffix)]
                if not version:
                    raise DeriveError(
                        f"prerelease tag {tag!r} has suffix {suffix!r} but no "
                        "version part; expected something like "
                        f"v1.0.0{suffix}"
                    )
                if "-" in version:
                    raise DeriveError(
                        f"prerelease tag {tag!r} has a nested '-' in the "
                        f"version part {version!r}; expected a plain "
                        f"semantic version before {suffix!r}"
                    )
                return version, channel

        if "-" in raw:
            allowed = ", ".join(ALLOWED_PRERELEASE_SUFFIXES)
            raise DeriveError(
                f"prerelease tag {tag!r} has an unrecognized suffix; "
                f"allowed prerelease suffixes are: {allowed}"
            )

        return raw, "preview"

    if "-" in raw:
        raise DeriveError(
            f"stable release tag {tag!r} must be a plain semantic tag "
            f"like vX.Y.Z; suffixed tags are reserved for prereleases"
        )
    return raw, "stable"


def _parse_bool(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in ("true", "1", "yes"):
        return True
    if lowered in ("false", "0", "no", ""):
        return False
    raise DeriveError(f"PRERELEASE must be 'true' or 'false', got {value!r}")


def main() -> int:
    tag = os.environ.get("GITHUB_REF_NAME", "")
    prerelease_raw = os.environ.get("PRERELEASE", "")

    try:
        prerelease = _parse_bool(prerelease_raw)
        version, channel = derive(tag, prerelease)
    except DeriveError as exc:
        print(f"derive-release-version-channel: {exc}", file=sys.stderr)
        return 2

    sys.stdout.write(f"version={version}\n")
    sys.stdout.write(f"channel={channel}\n")

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as fh:
            fh.write(f"version={version}\n")
            fh.write(f"channel={channel}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

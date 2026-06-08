#!/usr/bin/env python3
"""RELEASE-CREATE-001: plan a WebFlash GitHub Release.

Resolve the ``(tag, channel, prerelease)`` triple for a config at a
version, reading the channel from ``config/product-catalog.json`` so the
caller never has to choose one. This is the fail-closed front gate of the
one-button "Release: Create GitHub Release" workflow
(``.github/workflows/create-release.yml``).

Why the channel is read, not chosen
-----------------------------------
``Release 3: Build & Release`` builds its matrix by filtering
``config/webflash-builds.json`` on ``version`` **and** ``channel`` and
exits non-zero on an empty match. The release tag is normalized back to
``(version, channel)`` by ``scripts/derive_release_version_channel.py``.
If an operator released a *stable* config under a *preview* tag (or vice
versa) the derived channel would not match the config's declared channel
and Release 3 would build an empty matrix. Taking the channel from the
catalog removes that whole failure class: the channel is always the
config's declared channel, so the tag this script computes always
normalizes back to a matrix that has at least the selected config.

Read-only. This script creates no release, no tag, and no firmware. It
only prints the plan (and appends it to ``$GITHUB_OUTPUT`` when set).

Pure logic is separated from I/O for unit testing:

* ``compute_tag(version, channel, suffix)`` and ``is_prerelease(channel)``
  are pure and unit-tested directly;
* ``plan_release(...)`` takes an already-loaded catalog dict (no file
  I/O) so the catalog-lookup rules can be tested offline;
* ``main`` does the file reading and stdout / ``$GITHUB_OUTPUT`` writing.

Usage::

    python3 scripts/plan_release.py \\
        --config Ceiling-POE-VentIQ-RoomIQ --version 1.0.1

    python3 scripts/plan_release.py \\
        --config Ceiling-POE-RoomIQ-LED --version 1.0.0 \\
        --tag-suffix led-preview

Emits three lines to stdout (and to ``$GITHUB_OUTPUT`` when set)::

    tag=v1.0.1
    channel=stable
    prerelease=false

Exits 0 on success, 2 on any rejection (fail closed).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"

# The one channel that ships under a plain ``vX.Y.Z`` tag with
# prerelease=false. Everything else (preview, beta, ...) is a prerelease
# and carries a tag suffix so it can coexist with the stable tag of the
# same firmware version.
STABLE_CHANNEL = "stable"

# Bare MAJOR.MINOR.PATCH, no leading ``v`` and no pre-release / build
# metadata. The catalog version is a plain semantic version, so the input
# must match it exactly.
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


class PlanReleaseError(Exception):
    """Raised when a release cannot be planned (fail closed)."""


def is_prerelease(channel: str) -> bool:
    """Return True for any channel other than the stable channel."""
    return channel != STABLE_CHANNEL


def compute_tag(version: str, channel: str, suffix: Optional[str] = None) -> str:
    """Return the git tag for ``version`` + ``channel`` (+ optional suffix).

    Stable releases use a plain ``vX.Y.Z`` tag and reject a suffix.
    Non-stable releases use ``vX.Y.Z-<suffix or channel>`` so a preview
    tag can coexist with the stable tag of the same firmware version. The
    returned tag is what ``scripts/derive_release_version_channel.py``
    normalizes back to ``(version, channel)``.
    """
    suffix = (suffix or "").strip()
    if channel == STABLE_CHANNEL:
        if suffix:
            raise PlanReleaseError(
                "--tag-suffix is only valid for non-stable channels; the "
                f"channel resolved to {STABLE_CHANNEL!r} for this config, so "
                "omit --tag-suffix"
            )
        return f"v{version}"
    chosen = suffix or channel
    return f"v{version}-{chosen}"


def normalize_version(version: str) -> str:
    """Return the bare semver for ``version``, tolerating a leading ``v``.

    Trims surrounding whitespace and strips a single leading ``v`` or
    ``V`` so ``1.0.5``, ``v1.0.5``, and ``V1.0.5`` all normalize to the
    bare ``1.0.5`` (which equals the bare catalog version). A pre-release
    or build suffix is NOT stripped: ``v1.0.5-preview`` normalizes to
    ``1.0.5-preview``, which then fails the bare-semver check, so the
    fail-closed behaviour for non-bare versions is preserved.

    Raises ``PlanReleaseError`` for an empty value or anything that is not
    MAJOR.MINOR.PATCH after the leading ``v`` is stripped.
    """
    if not version or not version.strip():
        raise PlanReleaseError("--version must be a non-empty value")
    candidate = version.strip()
    if candidate[:1] in ("v", "V"):
        candidate = candidate[1:]
    if not SEMVER_RE.match(candidate):
        raise PlanReleaseError(
            f"--version {version!r} is not semver-shaped; expected "
            "MAJOR.MINOR.PATCH with an optional leading 'v' "
            "(e.g. 1.0.0 or v1.0.0)"
        )
    return candidate


def find_entry(catalog: Dict[str, Any], config_string: str) -> Optional[Dict[str, Any]]:
    """Return the catalog product whose ``config_string`` matches, else None."""
    for entry in catalog.get("products", []) or []:
        if isinstance(entry, dict) and entry.get("config_string") == config_string:
            return entry
    return None


def plan_release(
    *,
    config_string: str,
    version: str,
    catalog: Dict[str, Any],
    tag_suffix: Optional[str] = None,
) -> Dict[str, Any]:
    """Resolve the release plan for ``config_string`` at ``version``.

    Pure logic: takes an already-loaded ``catalog`` dict (no file I/O) so
    it can be unit tested offline. The channel is read from the catalog
    entry and is authoritative — there is deliberately no channel input.

    Returns a dict with ``config_string``, ``version``, ``channel``,
    ``tag``, and ``prerelease``. Raises ``PlanReleaseError`` (fail closed)
    on any inconsistency.
    """
    if not config_string:
        raise PlanReleaseError("--config is empty")
    # Tolerate a leading 'v' (any case) and surrounding whitespace, then
    # compare the resulting bare version against the bare catalog version.
    version = normalize_version(version)

    entry = find_entry(catalog, config_string)
    if entry is None:
        raise PlanReleaseError(
            f"config {config_string!r} not found in the product catalog; "
            "check config/product-catalog.json (and the workflow picker)"
        )

    catalog_version = entry.get("version")
    if not catalog_version:
        raise PlanReleaseError(
            f"catalog entry for {config_string!r} has no 'version' field"
        )
    if catalog_version != version:
        # The exact, operator-actionable message the workflow surfaces when
        # the bump PR has not been merged yet.
        raise PlanReleaseError(
            f"Catalog declares {catalog_version} for {config_string}, not "
            f"{version}. Run Release 1: Bump Version and MERGE its PR first."
        )

    channel = entry.get("channel")
    if not channel:
        raise PlanReleaseError(
            f"catalog entry for {config_string!r} has no 'channel' field"
        )

    tag = compute_tag(version, channel, tag_suffix)
    return {
        "config_string": config_string,
        "version": version,
        "channel": channel,
        "tag": tag,
        "prerelease": is_prerelease(channel),
    }


def load_catalog(path: Path) -> Dict[str, Any]:
    """Load and parse the product catalog (the only file I/O entry point)."""
    if not path.is_file():
        raise PlanReleaseError(f"catalog not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PlanReleaseError(f"catalog is not valid JSON: {exc}")


def _emit(plan: Dict[str, Any]) -> None:
    """Write the plan to stdout and (when set) to ``$GITHUB_OUTPUT``."""
    lines = [
        f"tag={plan['tag']}",
        f"channel={plan['channel']}",
        f"prerelease={'true' if plan['prerelease'] else 'false'}",
        # Normalized (bare, leading-'v'-stripped) version so downstream
        # workflow steps that compare against the bare catalog/derived
        # version use the same value the plan validated.
        f"version={plan['version']}",
    ]
    for line in lines:
        sys.stdout.write(line + "\n")
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as fh:
            for line in lines:
                fh.write(line + "\n")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Plan a WebFlash GitHub Release: resolve the git tag, channel, "
            "and prerelease flag for a config at a version. The channel is "
            "read from config/product-catalog.json and is authoritative "
            "(there is no channel input). Read-only: creates no release, "
            "tag, or firmware."
        )
    )
    parser.add_argument(
        "--config", required=True, help="WebFlash config_string to release"
    )
    parser.add_argument(
        "--version",
        required=True,
        help="Release version, leading 'v' optional (e.g. 1.0.1 or v1.0.1)",
    )
    parser.add_argument(
        "--tag-suffix",
        default=None,
        help=(
            "Tag suffix for non-stable channels (e.g. preview, led-preview). "
            "Rejected for the stable channel."
        ),
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=DEFAULT_CATALOG_PATH,
        help="Path to config/product-catalog.json",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        catalog = load_catalog(args.catalog)
        plan = plan_release(
            config_string=args.config,
            version=args.version,
            catalog=catalog,
            tag_suffix=args.tag_suffix,
        )
    except PlanReleaseError as exc:
        print(f"plan-release: {exc}", file=sys.stderr)
        return 2
    _emit(plan)
    return 0


if __name__ == "__main__":
    sys.exit(main())

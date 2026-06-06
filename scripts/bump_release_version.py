#!/usr/bin/env python3
"""RELEASE-BUMP-001: Bump a release version in lock-step across both files.

The release version of a WebFlash-shippable config is declared in two
places that must always agree:

  * ``config/product-catalog.json``  (the product lifecycle catalog)
  * ``config/webflash-builds.json``  (the WebFlash build matrix)

In each file the version appears twice for a given config: once as the
``version`` field and once embedded in the ``artifact_name``
(``Sense360-{config_string}-v{version}-{channel}.bin``).
``scripts/validate_product_catalog_consistency.py`` regenerates the
filename from ``version`` + ``channel`` and compares it to
``artifact_name``, so ``version`` and ``artifact_name`` MUST move together
or that validator fails. Historically a bump meant hand-editing four
fields across two files and hoping they stayed coherent.

This script does that edit mechanically. For a single ``config_string`` it
rewrites only the ``version`` and the version-bearing ``artifact_name`` in
both files and nothing else.

Channel is NOT changed by a version bump. The existing channel is read
from the catalog entry and reused when rebuilding ``artifact_name``; the
script never accepts a channel input. If the two files disagree on the
current channel the bump fails closed rather than guessing.

The mutating helpers operate on plain dicts so they stay API-free and unit
testable (see ``tests/test_bump_release_version.py``). The on-disk files
are serialized with 2-space indentation and a trailing newline, which is
the exact committed form, so a real bump produces a minimal diff: only the
two changed lines per file for the one config.

Usage::

    # Preview (prints the planned change, writes nothing):
    python3 scripts/bump_release_version.py \\
        --config Ceiling-POE-VentIQ-RoomIQ --version 2.0.0

    # Apply:
    python3 scripts/bump_release_version.py \\
        --config Ceiling-POE-VentIQ-RoomIQ --version 2.0.0 --write

Exit codes: 0 on success (including a no-op when the files are already at
the requested version), 1 on a fail-closed condition or I/O error, 2 on a
CLI usage error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG = REPO_ROOT / "config" / "product-catalog.json"
DEFAULT_BUILDS = REPO_ROOT / "config" / "webflash-builds.json"

# A plain MAJOR.MINOR.PATCH semantic version, no leading zeros. The release
# version is embedded in the artifact filename as ``vX.Y.Z-{channel}.bin``;
# the preview/stable distinction is carried by the channel, not by a
# semver pre-release suffix, so the version itself stays a clean core triple.
_SEMVER_CORE_RE = re.compile(r"^(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)$")


class BumpError(Exception):
    """Raised when a bump cannot be applied (fail-closed)."""


# ---------------------------------------------------------------------------
# Pure functions (no file I/O) — unit tested directly.
# ---------------------------------------------------------------------------


def compute_artifact_name(config_string: str, version: str, channel: str) -> str:
    """Return the canonical firmware filename for a config/version/channel.

    Matches ``generate_webflash_filename`` in ``scripts/product_name_mapper.py``
    for the release-eligible configs, so the rebuilt name stays in agreement
    with ``scripts/validate_product_catalog_consistency.py``.
    """
    return f"Sense360-{config_string}-v{version}-{channel}.bin"


def validate_version(version: str) -> None:
    """Fail closed unless ``version`` is a bare MAJOR.MINOR.PATCH triple."""
    if not isinstance(version, str) or version == "":
        raise BumpError("version is required and must be a non-empty string")
    if version != version.strip():
        raise BumpError(f"version {version!r} has leading/trailing whitespace")
    if version[:1] in ("v", "V"):
        raise BumpError(
            f"version {version!r} must not have a leading 'v'; pass the bare "
            "version, e.g. 2.0.0 (the 'v' is added when building artifact_name)"
        )
    if not _SEMVER_CORE_RE.match(version):
        raise BumpError(
            f"version {version!r} is not semver-shaped; expected a plain "
            "MAJOR.MINOR.PATCH triple with no leading 'v' and no pre-release "
            "or build suffix, e.g. 2.0.0"
        )


def find_entry(
    entries: List[Dict[str, Any]], config_string: str
) -> Optional[Dict[str, Any]]:
    """Return the dict in ``entries`` whose ``config_string`` matches, else None."""
    for entry in entries:
        if isinstance(entry, dict) and entry.get("config_string") == config_string:
            return entry
    return None


def apply_update(entry: Dict[str, Any], version: str, artifact_name: str) -> None:
    """Set ``version`` and ``artifact_name`` on ``entry`` in place.

    Only those two keys are touched; their position in the dict (and hence in
    the serialized file) is preserved because the keys already exist.
    """
    entry["version"] = version
    entry["artifact_name"] = artifact_name


# ---------------------------------------------------------------------------
# Plan / apply over the two parsed documents (still no file I/O).
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BumpPlan:
    """The fully-resolved, validated description of a single bump."""

    config_string: str
    channel: str
    new_version: str
    new_artifact_name: str
    catalog_old_version: str
    catalog_old_artifact: str
    builds_old_version: str
    builds_old_artifact: str

    @property
    def changed(self) -> bool:
        """True if applying the plan would actually alter either file."""
        return (
            self.catalog_old_version != self.new_version
            or self.catalog_old_artifact != self.new_artifact_name
            or self.builds_old_version != self.new_version
            or self.builds_old_artifact != self.new_artifact_name
        )


def _catalog_entries(catalog: Dict[str, Any]) -> List[Dict[str, Any]]:
    products = catalog.get("products", [])
    return products if isinstance(products, list) else []


def _builds_entries(builds: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = builds.get("builds", [])
    return rows if isinstance(rows, list) else []


def resolve_channel(
    catalog_entry: Dict[str, Any],
    builds_entry: Dict[str, Any],
    config_string: str,
) -> str:
    """Return the channel to reuse, failing closed if the files disagree.

    The catalog entry is authoritative; the build-matrix channel is only
    consulted to detect (and reject) drift between the two files.
    """
    cat_channel = catalog_entry.get("channel")
    bld_channel = builds_entry.get("channel")
    if not isinstance(cat_channel, str) or cat_channel == "":
        raise BumpError(
            f"catalog entry for {config_string!r} has no usable 'channel'; "
            "cannot rebuild artifact_name without it"
        )
    if not isinstance(bld_channel, str) or bld_channel == "":
        raise BumpError(
            f"build-matrix entry for {config_string!r} has no usable 'channel'; "
            "cannot confirm channel agreement"
        )
    if cat_channel != bld_channel:
        raise BumpError(
            f"channel disagreement for {config_string!r}: "
            f"product-catalog.json says {cat_channel!r} but "
            f"webflash-builds.json says {bld_channel!r}. A version bump must "
            "not change the channel; reconcile the two files first"
        )
    return cat_channel


def build_plan(
    catalog: Dict[str, Any],
    builds: Dict[str, Any],
    config_string: str,
    version: str,
) -> BumpPlan:
    """Validate inputs and resolve a :class:`BumpPlan` without mutating anything."""
    validate_version(version)

    catalog_entry = find_entry(_catalog_entries(catalog), config_string)
    if catalog_entry is None:
        raise BumpError(
            f"config_string {config_string!r} is not present in the product "
            "catalog (config/product-catalog.json)"
        )

    builds_entry = find_entry(_builds_entries(builds), config_string)
    if builds_entry is None:
        raise BumpError(
            f"config_string {config_string!r} is not present in the WebFlash "
            "build matrix (config/webflash-builds.json)"
        )

    channel = resolve_channel(catalog_entry, builds_entry, config_string)
    new_artifact = compute_artifact_name(config_string, version, channel)

    return BumpPlan(
        config_string=config_string,
        channel=channel,
        new_version=version,
        new_artifact_name=new_artifact,
        catalog_old_version=str(catalog_entry.get("version", "")),
        catalog_old_artifact=str(catalog_entry.get("artifact_name", "")),
        builds_old_version=str(builds_entry.get("version", "")),
        builds_old_artifact=str(builds_entry.get("artifact_name", "")),
    )


def apply_plan(
    catalog: Dict[str, Any],
    builds: Dict[str, Any],
    plan: BumpPlan,
) -> None:
    """Apply ``plan`` to both parsed documents in place.

    Re-locates the entries (rather than trusting a stale reference) and writes
    the new version + artifact_name into each.
    """
    catalog_entry = find_entry(_catalog_entries(catalog), plan.config_string)
    builds_entry = find_entry(_builds_entries(builds), plan.config_string)
    if catalog_entry is None or builds_entry is None:
        # build_plan already proved both exist; guard anyway so a caller that
        # mutated the docs between plan and apply fails loudly.
        raise BumpError(
            f"config_string {plan.config_string!r} disappeared from one of the "
            "documents between planning and applying"
        )
    apply_update(catalog_entry, plan.new_version, plan.new_artifact_name)
    apply_update(builds_entry, plan.new_version, plan.new_artifact_name)


# ---------------------------------------------------------------------------
# File I/O.
# ---------------------------------------------------------------------------


def load_document(path: Path) -> Dict[str, Any]:
    """Parse a JSON object from ``path``, failing closed on shape problems."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise BumpError(f"file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise BumpError(f"{path}: JSON parse error - {exc}") from exc
    if not isinstance(data, dict):
        raise BumpError(f"{path}: expected a JSON object at the top level")
    return data


def dump_document(path: Path, document: Dict[str, Any]) -> None:
    """Write ``document`` back as 2-space-indented JSON with a trailing newline.

    This is the exact committed form of both config files, so re-serializing
    after changing only two values yields a minimal diff.
    """
    path.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------


def _format_plan(plan: BumpPlan, catalog_path: Path, builds_path: Path) -> str:
    arrow = "  ->  "
    lines = [
        f"Bump plan for config {plan.config_string!r}",
        f"  channel (reused, unchanged): {plan.channel}",
        f"  {catalog_path}",
        f"    version:       {plan.catalog_old_version}{arrow}{plan.new_version}",
        f"    artifact_name: {plan.catalog_old_artifact}{arrow}"
        f"{plan.new_artifact_name}",
        f"  {builds_path}",
        f"    version:       {plan.builds_old_version}{arrow}{plan.new_version}",
        f"    artifact_name: {plan.builds_old_artifact}{arrow}"
        f"{plan.new_artifact_name}",
    ]
    return "\n".join(lines)


def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Bump a release version in lock-step across "
            "config/product-catalog.json and config/webflash-builds.json. "
            "Rewrites only the 'version' and the version-bearing "
            "'artifact_name' for one config; the channel is read from the "
            "catalog entry and reused."
        )
    )
    parser.add_argument(
        "--config",
        required=True,
        metavar="CONFIG_STRING",
        help="config_string to bump, e.g. Ceiling-POE-VentIQ-RoomIQ",
    )
    parser.add_argument(
        "--version",
        required=True,
        metavar="VERSION",
        help="new version, no leading 'v', MAJOR.MINOR.PATCH (e.g. 2.0.0)",
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=DEFAULT_CATALOG,
        help="path to product-catalog.json (default: config/product-catalog.json)",
    )
    parser.add_argument(
        "--builds",
        type=Path,
        default=DEFAULT_BUILDS,
        help="path to webflash-builds.json (default: config/webflash-builds.json)",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="apply the change in place; without it the plan is only printed",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = _parse_args(argv)
    try:
        catalog = load_document(args.catalog)
        builds = load_document(args.builds)
        plan = build_plan(catalog, builds, args.config, args.version)
    except BumpError as exc:
        print(f"bump-release-version: {exc}", file=sys.stderr)
        return 1

    print(_format_plan(plan, args.catalog, args.builds))

    if not args.write:
        print("Dry run: re-run with --write to apply.")
        return 0

    if not plan.changed:
        print(
            "No changes needed: both files are already at version "
            f"{plan.new_version} for {plan.config_string!r}."
        )
        return 0

    apply_plan(catalog, builds, plan)
    dump_document(args.catalog, catalog)
    dump_document(args.builds, builds)
    print(f"Wrote {args.catalog} and {args.builds}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

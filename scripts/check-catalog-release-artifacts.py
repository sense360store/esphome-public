#!/usr/bin/env python3
"""Assert every WebFlash-build catalog config maps to a real RELEASED artifact.

Sibling of ``scripts/check-webflash-release-assets.py``. That script runs at
release time and asserts each WebFlash-matrix ``artifact_name`` is present in
the freshly built asset directory before the assets are uploaded. This script
runs in normal CI (the catalog-validator workflow) and closes the opposite
gap: it asserts that every ``artifact_name`` the *catalog* declares for a
shipping config actually exists as a published GitHub release asset.

Why this guard exists
---------------------
``scripts/validate_product_catalog_consistency.py`` already proves the catalog
is *internally* consistent: it checks ``artifact_name`` equals the value the
name mapper derives from ``(product_yaml, version, channel)``. That check
passes even when someone bumps a config to a version that was never built and
released, because the version and the artifact_name are bumped together and
still agree with each other. That is exactly what happened when
``Ceiling-POE-VentIQ-RoomIQ-LED`` was set to ``1.0.3`` with artifact
``Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.3-preview.bin`` while no 1.0.3
build was ever released; the catalog looked consistent but named a phantom
version, and the downstream WebFlash deploy gate broke trying to fetch it.

This guard verifies the artifact against reality, by the same mechanism the
release-time check uses: match the catalog's ``artifact_name`` against the set
of asset names that actually exist (here, the assets attached to published
GitHub releases instead of a local build directory).

What is checked
---------------
For every ``config/product-catalog.json`` product that BOTH

  * is marked ``webflash_build_matrix: true``, AND
  * declares a non-empty ``artifact_name``

the asset named ``artifact_name`` must exist in some published (non-draft)
GitHub release. When asset sizes are available (the GitHub API path), the
asset must also be at least ``--min-size-bytes`` bytes, mirroring the
release-time check's size floor.

What is exempt
--------------
Configs that intentionally have no built artifact are simply not selected:
anything without an ``artifact_name`` (the open-source mains boards published
under CERN-OHL-P, plus every ``blocked`` / ``hardware-pending`` /
``compile-only`` / ``legacy-compatible`` / ``removed`` entry) is skipped. The
catalog's own status rules already forbid ``artifact_name`` on those entries.

Released-asset source (pick one; default queries GitHub via the gh CLI)
-----------------------------------------------------------------------
``--repo OWNER/NAME`` (or ``$GITHUB_REPOSITORY``, default
``sense360store/esphome-public``)
    Query published releases via ``gh api --paginate repos/OWNER/NAME/releases``
    and collect every release asset's name and size. Honors ``GH_TOKEN`` /
    ``GITHUB_TOKEN`` the way the gh CLI already does. This is the live CI path.

``--released-assets FILE`` (use ``-`` for stdin)
    Read released asset names from FILE instead of querying GitHub. FILE may be
    the raw JSON returned by ``gh api .../releases`` (a JSON array of release
    objects, or a single release object), a JSON array of asset-name strings,
    or a newline-delimited list of asset names. Intended for offline / dry-run
    / unit-test flows. Sizes are only known for the release-JSON shape; the
    size floor is skipped for shapes that carry no size.

Exit codes
----------
0   every selected catalog artifact has a matching released asset.
1   guard failure: at least one selected artifact is missing from the released
    assets (a phantom version/artifact), or zero configs were selected and
    ``--allow-no-build-configs`` was not passed.
2   usage / environment error (catalog unreadable, gh missing/failed, bad
    ``--released-assets`` input).

Usage:
    python3 scripts/check-catalog-release-artifacts.py
    python3 scripts/check-catalog-release-artifacts.py --repo sense360store/esphome-public
    gh api --paginate repos/sense360store/esphome-public/releases \\
        | python3 scripts/check-catalog-release-artifacts.py --released-assets -
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional

DEFAULT_MIN_SIZE_BYTES = 100 * 1024  # 100 KB; matches check-webflash-release-assets.py
DEFAULT_REPO = "sense360store/esphome-public"
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"


class UsageError(Exception):
    """Raised for an operational / usage error (exit code 2)."""


class BuildConfig(NamedTuple):
    """A catalog config that declares a shipping WebFlash artifact."""

    label: str  # config_string (falls back to product_yaml / legacy id) for messages
    version: Optional[str]
    channel: Optional[str]
    artifact_name: str


# ---------------------------------------------------------------------------
# Catalog selection
# ---------------------------------------------------------------------------
def select_build_configs(catalog: dict) -> List[BuildConfig]:
    """Return catalog products that declare a shipping WebFlash artifact.

    Selection is the intersection the task defines: ``webflash_build_matrix``
    is exactly ``True`` AND ``artifact_name`` is a non-empty string. Every
    other entry (no artifact_name, or not a build-matrix entry) is exempt and
    not returned.
    """
    products = catalog.get("products")
    if not isinstance(products, list):
        raise UsageError("product catalog 'products' must be a list")

    selected: List[BuildConfig] = []
    for entry in products:
        if not isinstance(entry, dict):
            continue
        if entry.get("webflash_build_matrix") is not True:
            continue
        artifact = entry.get("artifact_name")
        if not isinstance(artifact, str) or not artifact.strip():
            continue
        label = (
            entry.get("config_string")
            or entry.get("legacy_config_id")
            or entry.get("product_yaml")
            or "<unknown config>"
        )
        selected.append(
            BuildConfig(
                label=str(label),
                version=entry.get("version"),
                channel=entry.get("channel"),
                artifact_name=artifact.strip(),
            )
        )
    return selected


# ---------------------------------------------------------------------------
# Released-asset collection
# ---------------------------------------------------------------------------
def collect_released_assets(releases: list) -> Dict[str, Optional[int]]:
    """Map asset name -> size across published (non-draft) releases.

    ``releases`` is the parsed ``gh api .../releases`` payload (a list of
    release objects). Draft releases are skipped because their assets are not
    publicly downloadable and therefore are not "released". Prereleases are
    included: the preview / LED artifacts live on prerelease tags. When an
    asset name appears in more than one release the larger size wins.
    """
    assets: Dict[str, Optional[int]] = {}
    for release in releases:
        if not isinstance(release, dict):
            continue
        if release.get("draft") is True:
            continue
        for asset in release.get("assets") or []:
            if not isinstance(asset, dict):
                continue
            name = asset.get("name")
            if not isinstance(name, str) or not name:
                continue
            size = asset.get("size")
            size_int = size if isinstance(size, int) else None
            prev = assets.get(name)
            if name not in assets:
                assets[name] = size_int
            elif size_int is not None and (prev is None or size_int > prev):
                assets[name] = size_int
    return assets


def parse_released_assets_text(text: str) -> Dict[str, Optional[int]]:
    """Parse a ``--released-assets`` source into a name -> size map.

    Accepts (auto-detected):
      * raw ``gh api .../releases`` JSON (array of release objects),
      * a single release object,
      * a JSON array of asset-name strings,
      * a newline-delimited list of asset names.
    Sizes are only recovered from the release-object shapes; other shapes map
    to ``None`` (size floor skipped).
    """
    stripped = text.strip()
    if not stripped:
        return {}

    try:
        data = json.loads(stripped)
    except json.JSONDecodeError:
        # Newline-delimited list of asset names.
        names = [line.strip() for line in stripped.splitlines() if line.strip()]
        return {name: None for name in names}

    if isinstance(data, dict):
        # Either a single release object or {"releases": [...]}.
        if isinstance(data.get("releases"), list):
            return collect_released_assets(data["releases"])
        return collect_released_assets([data])

    if isinstance(data, list):
        if all(isinstance(item, str) for item in data):
            return {item: None for item in data}
        return collect_released_assets(data)

    raise UsageError("unrecognized --released-assets JSON shape")


def fetch_released_assets_via_gh(repo: str) -> Dict[str, Optional[int]]:
    """Query published releases for ``repo`` via the gh CLI.

    Uses ``gh api --paginate``, which merges top-level array pages into a
    single JSON array. Raises ``UsageError`` (exit 2) if gh is unavailable or
    the call fails, with a hint to use ``--released-assets`` for offline runs.
    """
    cmd = [
        "gh",
        "api",
        "--paginate",
        f"repos/{repo}/releases",
        "-H",
        "Accept: application/vnd.github+json",
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise UsageError(
            "the 'gh' CLI is required to query releases but was not found on "
            "PATH. Install gh, or pass --released-assets to verify against a "
            "pre-fetched release list."
        ) from exc

    if proc.returncode != 0:
        raise UsageError(
            f"`gh api repos/{repo}/releases` failed (exit {proc.returncode}). "
            f"Set GH_TOKEN/GITHUB_TOKEN and ensure repo access, or pass "
            f"--released-assets. stderr:\n{proc.stderr.strip()}"
        )

    try:
        releases = json.loads(proc.stdout or "[]")
    except json.JSONDecodeError as exc:
        raise UsageError(f"could not parse gh api output as JSON: {exc}") from exc

    if not isinstance(releases, list):
        raise UsageError("gh api releases output was not a JSON array")
    return collect_released_assets(releases)


# ---------------------------------------------------------------------------
# Core evaluation
# ---------------------------------------------------------------------------
def evaluate(
    configs: List[BuildConfig],
    released_assets: Dict[str, Optional[int]],
    min_size_bytes: int,
) -> tuple[List[str], List[str]]:
    """Return ``(errors, checked)`` for ``configs`` against ``released_assets``.

    An error is recorded when a config's ``artifact_name`` is absent from the
    released assets (a phantom version), or when the released asset is smaller
    than ``min_size_bytes`` (only when the size is known).
    """
    errors: List[str] = []
    checked: List[str] = []
    for cfg in configs:
        descriptor = (
            f"{cfg.label} (version={cfg.version}, channel={cfg.channel})"
            f" -> {cfg.artifact_name}"
        )
        if cfg.artifact_name not in released_assets:
            errors.append(
                f"no released artifact named {cfg.artifact_name!r} for "
                f"{cfg.label} (version={cfg.version}, channel={cfg.channel}). "
                f"The catalog names this artifact but no published release "
                f"provides it. Either publish the build for this version or "
                f"correct the catalog version/artifact_name."
            )
            continue
        size = released_assets[cfg.artifact_name]
        if size is not None and size < min_size_bytes:
            errors.append(
                f"released artifact {cfg.artifact_name!r} for {cfg.label} is "
                f"too small: {size} bytes < min {min_size_bytes}"
            )
            continue
        size_note = f"{size} bytes" if size is not None else "size unknown"
        checked.append(f"{descriptor} [{size_note}]")
    return errors, checked


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Assert every WebFlash-build catalog config maps to a real "
            "released artifact (catches phantom catalog versions)."
        ),
    )
    parser.add_argument(
        "--catalog",
        default=str(DEFAULT_CATALOG_PATH),
        help="Path to product-catalog.json (default: config/product-catalog.json)",
    )
    parser.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPOSITORY") or DEFAULT_REPO,
        help=(
            "OWNER/NAME to query published releases for via the gh CLI "
            f"(default: $GITHUB_REPOSITORY or {DEFAULT_REPO}). Ignored when "
            "--released-assets is given."
        ),
    )
    parser.add_argument(
        "--released-assets",
        metavar="FILE",
        help=(
            "Read released asset names from FILE instead of querying GitHub "
            "(use '-' for stdin). Accepts gh-api releases JSON, a JSON array "
            "of names, or a newline-delimited list."
        ),
    )
    parser.add_argument(
        "--min-size-bytes",
        type=int,
        default=DEFAULT_MIN_SIZE_BYTES,
        help=(
            "Minimum acceptable released .bin size when the size is known "
            f"(default: {DEFAULT_MIN_SIZE_BYTES})"
        ),
    )
    parser.add_argument(
        "--allow-no-build-configs",
        action="store_true",
        help=(
            "Permit zero catalog configs to be selected. Without this flag a "
            "catalog that declares no WebFlash-build artifacts fails closed "
            "(it almost certainly means a parsing/selection regression)."
        ),
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    catalog_path = Path(args.catalog)
    if not catalog_path.is_file():
        print(f"FAIL: product catalog not found at {catalog_path}", file=sys.stderr)
        return 2
    try:
        catalog = json.loads(catalog_path.read_text())
    except json.JSONDecodeError as exc:
        print(f"FAIL: cannot parse {catalog_path}: {exc}", file=sys.stderr)
        return 2

    try:
        configs = select_build_configs(catalog)
    except UsageError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2

    if not configs:
        msg = (
            "no catalog configs are marked webflash_build_matrix=true with an "
            "artifact_name"
        )
        if args.allow_no_build_configs:
            print(f"NOTICE: {msg}; bypass flag set, nothing to verify.")
            return 0
        print(
            f"FAIL: {msg}; refusing to pass a catalog that declares no WebFlash "
            f"build artifacts. If this is intentional, pass "
            f"--allow-no-build-configs.",
            file=sys.stderr,
        )
        return 1

    try:
        if args.released_assets:
            if args.released_assets == "-":
                text = sys.stdin.read()
                source_desc = "stdin"
            else:
                assets_path = Path(args.released_assets)
                if not assets_path.is_file():
                    print(
                        f"FAIL: --released-assets file not found: {assets_path}",
                        file=sys.stderr,
                    )
                    return 2
                text = assets_path.read_text()
                source_desc = str(assets_path)
            released_assets = parse_released_assets_text(text)
        else:
            released_assets = fetch_released_assets_via_gh(args.repo)
            source_desc = f"published releases of {args.repo}"
    except UsageError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2

    errors, checked = evaluate(configs, released_assets, args.min_size_bytes)

    if errors:
        print(
            "FAIL: catalog declares artifacts with no released build:", file=sys.stderr
        )
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        if checked:
            print(
                f"\n({len(checked)} other catalog artifact(s) verified OK.)",
                file=sys.stderr,
            )
        return 1

    print(
        f"OK: {len(checked)} catalog WebFlash-build artifact(s) verified against "
        f"{source_desc}."
    )
    for line in checked:
        print(f"  - {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

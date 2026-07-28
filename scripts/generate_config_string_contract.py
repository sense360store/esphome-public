#!/usr/bin/env python3
"""Generate the canonical firmware-configuration contract.

SENSE360-CANONICALISATION-001 PR 06. The contract answers one question for
every declared Sense360 firmware configuration: **which boards does this
config string compose, and which lane does it occupy?**

The board composition is *derived*, never hand-authored. For each
configuration the generator walks the ESPHome ``packages:`` / ``!include``
graph from the configuration's canonical YAML and collects the board SKU
that each visited hardware-layer package declares in
``config/board-package-bindings.json``. Because the walk follows includes,
a legacy alias contributes the SKU of whatever it resolves to, so the
answer does not change when PR 07 removes the alias.

The classification lane is derived from the existing declarations
(``config/product-catalog.json``, ``config/webflash-builds.json``,
``config/preview-release-targets.json``, ``config/compile-only-targets.json``
and ``config/room-bundle-skus.json``) in a fixed precedence order, so no
configuration can sit in two lanes and none can sit in none.

The output is written to ``config/config-string-contract.json``. The
generated file is a *contract record*: it builds no firmware, publishes
nothing, promotes nothing, and changes no channel, status or artifact.

Run with::

    python3 scripts/generate_config_string_contract.py

Add ``--check`` to verify the on-disk contract matches the regenerated
contract without writing.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

BINDINGS_PATH = REPO_ROOT / "config" / "board-package-bindings.json"
CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
COMPAT_PATH = REPO_ROOT / "config" / "webflash-compatibility.json"
COMPILE_ONLY_PATH = REPO_ROOT / "config" / "compile-only-targets.json"
PREVIEW_TARGETS_PATH = REPO_ROOT / "config" / "preview-release-targets.json"
ROOM_BUNDLES_PATH = REPO_ROOT / "config" / "room-bundle-skus.json"
HARDWARE_CATALOG_PATH = REPO_ROOT / "config" / "hardware-catalog.json"
CONTRACT_PATH = REPO_ROOT / "config" / "config-string-contract.json"

# Classification lanes, in precedence order. The first lane whose rule
# matches wins, so every configuration lands in exactly one.
LANE_REMOVED = "removed"
LANE_COMPILE_ONLY = "compile-only"
LANE_ADVANCED = "advanced"
LANE_EXPERIMENTAL = "experimental"
LANE_PREVIEW = "preview"
LANE_ROOM = "room"

LANES = (
    LANE_ROOM,
    LANE_ADVANCED,
    LANE_PREVIEW,
    LANE_EXPERIMENTAL,
    LANE_COMPILE_ONLY,
    LANE_REMOVED,
)

LANE_RULES = {
    LANE_REMOVED: (
        "config/product-catalog.json status=removed. A tombstone reserving a "
        "retired legacy_config_id; the product YAML no longer exists, so the "
        "composition is empty by construction."
    ),
    LANE_COMPILE_ONLY: (
        "config/product-catalog.json status=compile-only, or declared only in "
        "config/compile-only-targets.json. Buildability validation only: never "
        "WebFlash-exposed, never a release artifact, never hardware proof."
    ),
    LANE_ADVANCED: (
        "config/preview-release-targets.json channel_tier=advanced-preview. "
        "The advanced / manual-warning lane; reachable only through the "
        "advanced path behind an acknowledgement gate, never a room preset."
    ),
    LANE_EXPERIMENTAL: ("config/webflash-builds.json channel=experimental."),
    LANE_PREVIEW: (
        "config/webflash-builds.json channel=preview, or "
        "config/product-catalog.json status=preview with no build row."
    ),
    LANE_ROOM: (
        "config/webflash-builds.json channel=stable AND the config string is a "
        "room bundle's firmware target in config/room-bundle-skus.json."
    ),
}


# ---------------------------------------------------------------------------
# YAML loading
#
# ESPHome custom tags are parsed structurally only, exactly as
# tests/validate_configs.py does: never yaml.unsafe_load. `!include` is the
# one tag whose payload the generator needs, so it is preserved as a marked
# string subclass that the include walker can recognise.
# ---------------------------------------------------------------------------


class IncludePath(str):
    """An ``!include`` target, preserved through the structural parse."""


def _structural(loader: yaml.Loader, node: yaml.Node) -> Any:
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None


def _include(loader: yaml.Loader, node: yaml.Node) -> Any:
    value = _structural(loader, node)
    if isinstance(value, str):
        return IncludePath(value)
    # ESPHome also allows `!include {file: ..., vars: {...}}`.
    if isinstance(value, dict) and isinstance(value.get("file"), str):
        return IncludePath(value["file"])
    return value


class ContractLoader(yaml.SafeLoader):
    """SafeLoader plus structural handling of the ESPHome custom tags."""


for _tag in ("!secret", "!extend", "!lambda", "!remove"):
    yaml.add_constructor(_tag, _structural, Loader=ContractLoader)
yaml.add_constructor("!include", _include, Loader=ContractLoader)
yaml.add_multi_constructor("!include_dir_", _structural, Loader=ContractLoader)


def load_yaml(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.load(handle, Loader=ContractLoader) or {}


def load_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


# ---------------------------------------------------------------------------
# Include-graph resolution
# ---------------------------------------------------------------------------


def iter_include_targets(node: Any) -> Iterable[str]:
    """Yield every ``!include`` target reachable inside a parsed document."""
    if isinstance(node, IncludePath):
        yield str(node)
    elif isinstance(node, dict):
        for value in node.values():
            yield from iter_include_targets(value)
    elif isinstance(node, list):
        for value in node:
            yield from iter_include_targets(value)


def walk_includes(entry: Path) -> Tuple[List[str], List[str]]:
    """Resolve the full include closure of ``entry``.

    Returns ``(visited, missing)`` where ``visited`` is every repository-
    relative YAML path reachable from ``entry`` (including ``entry`` itself)
    and ``missing`` is every include target that does not resolve to a file.
    Both are sorted and de-duplicated so the output is order-independent.
    """
    visited: Set[Path] = set()
    missing: Set[str] = set()
    stack = [entry.resolve()]

    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        for target in iter_include_targets(load_yaml(current)):
            resolved = (current.parent / target).resolve()
            if resolved.is_file():
                stack.append(resolved)
            else:
                missing.add(target)

    relative = sorted(
        path.relative_to(REPO_ROOT).as_posix()
        for path in visited
        if REPO_ROOT in path.parents
    )
    return relative, sorted(missing)


def resolve_composition(
    entry_yaml: str, binding_index: Dict[str, Optional[str]]
) -> Dict[str, Any]:
    """Resolve one configuration YAML to its exact board composition."""
    visited, missing = walk_includes(REPO_ROOT / entry_yaml)

    skus: Set[str] = set()
    contributing: List[Dict[str, str]] = []
    for path in visited:
        sku = binding_index.get(path)
        if sku:
            skus.add(sku)
            contributing.append({"package": path, "board_sku": sku})

    return {
        "board_composition": sorted(skus),
        "board_packages": [c["package"] for c in contributing],
        "resolved_yaml_count": len(visited),
        "unresolved_includes": missing,
    }


# ---------------------------------------------------------------------------
# Declaration indexes
# ---------------------------------------------------------------------------


def catalog_index(catalog: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {
        entry["config_string"]: entry
        for entry in catalog["products"]
        if entry.get("config_string")
    }


def catalog_tombstones(catalog: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [entry for entry in catalog["products"] if entry.get("status") == "removed"]


def builds_index(builds: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {row["config_string"]: row for row in builds["builds"]}


def preview_target_index(targets: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {
        row["config_string"]: row
        for row in targets["targets"]
        if row.get("config_string")
    }


def compile_only_index(targets: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    index: Dict[str, List[Dict[str, Any]]] = {}
    for row in targets["targets"]:
        config_string = row.get("config_string")
        if config_string:
            index.setdefault(config_string, []).append(row)
    return index


def room_bundle_targets(room_bundles: Dict[str, Any]) -> Dict[str, List[str]]:
    """Map each room bundle's firmware target to the bundle SKUs using it."""
    index: Dict[str, List[str]] = {}
    for bundle in room_bundles["bundles"]:
        target = bundle.get("likely_firmware_config_target")
        if target:
            index.setdefault(target, []).append(bundle["bundle_sku"])
    return {target: sorted(skus) for target, skus in index.items()}


# ---------------------------------------------------------------------------
# Config-string grammar
# ---------------------------------------------------------------------------


def grammar_tokens(compat: Dict[str, Any]) -> Set[str]:
    return set(
        compat["canonical_mounting"]
        + compat["canonical_power"]
        + compat["canonical_modules"]
    )


def grammar_verdict(config_string: str, tokens: Set[str]) -> Dict[str, Any]:
    """Classify a config string against the canonical grammar.

    The SOT identifier schema admits a config string only as
    ``^Ceiling(-[A-Za-z0-9]+)+$`` and every segment must be a canonical
    token. A string that fails either test is *impossible*: no board
    composition can make it valid, because no board answers to the token.
    """
    segments = config_string.split("-")
    shape_ok = bool(re.fullmatch(r"Ceiling(-[A-Za-z0-9]+)+", config_string))
    unknown = [segment for segment in segments if segment not in tokens]
    return {
        "matches_sot_schema": shape_ok,
        "tokens": segments,
        "unknown_tokens": unknown,
        "valid": shape_ok and not unknown,
    }


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


def classify(
    config_string: str,
    catalog_entry: Optional[Dict[str, Any]],
    build_row: Optional[Dict[str, Any]],
    preview_row: Optional[Dict[str, Any]],
    compile_rows: List[Dict[str, Any]],
    room_targets: Dict[str, List[str]],
) -> str:
    """Return the single lane this configuration occupies.

    Precedence is fixed and total. ``advanced`` is tested before the channel
    lanes so the advanced / manual-warning lane is never reported as an
    ordinary preview or experimental build.
    """
    catalog_status = (catalog_entry or {}).get("status")
    if catalog_status == "removed":
        return LANE_REMOVED
    if catalog_status == "compile-only":
        return LANE_COMPILE_ONLY
    if build_row is None and catalog_entry is None and compile_rows:
        return LANE_COMPILE_ONLY
    if (preview_row or {}).get("channel_tier") == "advanced-preview":
        return LANE_ADVANCED

    channel = (build_row or {}).get("channel")
    if channel == "experimental":
        return LANE_EXPERIMENTAL
    if channel == "preview":
        return LANE_PREVIEW
    if channel == "stable" and config_string in room_targets:
        return LANE_ROOM
    if catalog_status == "preview":
        return LANE_PREVIEW
    return LANE_COMPILE_ONLY


# ---------------------------------------------------------------------------
# Contract generation
# ---------------------------------------------------------------------------


def build_binding_index(bindings: Dict[str, Any]) -> Dict[str, Optional[str]]:
    return {row["package"]: row.get("board_sku") for row in bindings["bindings"]}


def generate(  # noqa: C901 - one flat assembly pass, deliberately linear
    bindings: Dict[str, Any],
    catalog: Dict[str, Any],
    builds: Dict[str, Any],
    compat: Dict[str, Any],
    compile_only: Dict[str, Any],
    preview_targets: Dict[str, Any],
    room_bundles: Dict[str, Any],
) -> Dict[str, Any]:
    binding_index = build_binding_index(bindings)
    catalog_by_cs = catalog_index(catalog)
    builds_by_cs = builds_index(builds)
    preview_by_cs = preview_target_index(preview_targets)
    compile_by_cs = compile_only_index(compile_only)
    room_targets = room_bundle_targets(room_bundles)
    tokens = grammar_tokens(compat)

    declared: Set[str] = set(catalog_by_cs) | set(builds_by_cs)
    declared |= set(preview_by_cs) | set(compile_by_cs)

    configurations: List[Dict[str, Any]] = []
    for config_string in sorted(declared):
        catalog_entry = catalog_by_cs.get(config_string)
        build_row = builds_by_cs.get(config_string)
        preview_row = preview_by_cs.get(config_string)
        compile_rows = compile_by_cs.get(config_string, [])

        canonical_yaml = (catalog_entry or {}).get("product_yaml")
        if canonical_yaml is None and compile_rows:
            canonical_yaml = compile_rows[0].get("product_yaml")

        row: Dict[str, Any] = {
            "config_string": config_string,
            "classification": classify(
                config_string,
                catalog_entry,
                build_row,
                preview_row,
                compile_rows,
                room_targets,
            ),
            "grammar": grammar_verdict(config_string, tokens),
            "canonical_yaml": canonical_yaml,
            "catalog_status": (catalog_entry or {}).get("status"),
            "channel": (build_row or {}).get("channel"),
            "version": (build_row or {}).get("version"),
            "artifact_name": (build_row or {}).get("artifact_name"),
            "room_bundle_skus": room_targets.get(config_string, []),
            "declared_in": sorted(
                name
                for name, present in (
                    ("product-catalog", catalog_entry is not None),
                    ("webflash-builds", build_row is not None),
                    ("preview-release-targets", preview_row is not None),
                    ("compile-only-targets", bool(compile_rows)),
                )
                if present
            ),
        }

        if canonical_yaml and (REPO_ROOT / canonical_yaml).is_file():
            row.update(resolve_composition(canonical_yaml, binding_index))
        else:
            row.update(
                {
                    "board_composition": [],
                    "board_packages": [],
                    "resolved_yaml_count": 0,
                    "unresolved_includes": [],
                }
            )

        declared_requirements = (build_row or {}).get("hardware_requirements")
        if declared_requirements is not None:
            row["declared_hardware_requirements"] = declared_requirements

        configurations.append(row)

    tombstones = [
        {
            "legacy_config_id": entry.get("legacy_config_id"),
            "classification": LANE_REMOVED,
            "removed_since": entry.get("removed_since"),
        }
        for entry in catalog_tombstones(catalog)
    ]
    tombstones.sort(key=lambda row: row["legacy_config_id"] or "")

    counts: Dict[str, int] = {lane: 0 for lane in LANES}
    for row in configurations:
        counts[row["classification"]] += 1
    counts[LANE_REMOVED] += len(tombstones)

    compositions: Dict[str, List[str]] = {}
    for row in configurations:
        if not row["board_composition"]:
            continue
        key = "+".join(row["board_composition"])
        compositions.setdefault(key, []).append(row["config_string"])

    return {
        "schema_version": 1,
        "work_item": "SENSE360-CANONICALISATION-001 PR 06",
        "description": (
            "Generated canonical firmware-configuration contract. For every "
            "declared Sense360 config string this records the one exact board "
            "composition it resolves to, derived by walking the ESPHome "
            "package include graph, plus the single classification lane it "
            "occupies. Generated by scripts/generate_config_string_contract.py "
            "and validated by tests/test_config_string_contract.py. This file "
            "is a contract record only: it builds no firmware, publishes "
            "nothing, and promotes no product, channel or artifact."
        ),
        "sources": {
            "bindings": "config/board-package-bindings.json",
            "catalog": "config/product-catalog.json",
            "builds": "config/webflash-builds.json",
            "compatibility": "config/webflash-compatibility.json",
            "compile_only": "config/compile-only-targets.json",
            "preview_targets": "config/preview-release-targets.json",
            "room_bundles": "config/room-bundle-skus.json",
        },
        "classification_lanes": {lane: LANE_RULES[lane] for lane in LANES},
        "evidence_ceiling": (
            "Static inspection of declarations and the YAML include graph "
            "only. A resolved composition is a compile-time composition fact; "
            "it is never hardware, bench, compliance, safety or "
            "commercial-availability proof, and it never claims that a "
            "connector-attached sensor is supplied."
        ),
        "totals": {
            "configurations": len(configurations),
            "tombstones": len(tombstones),
            "by_classification": counts,
            "distinct_compositions": len(compositions),
        },
        "compositions": {
            key: sorted(value) for key, value in sorted(compositions.items())
        },
        "configurations": configurations,
        "tombstones": tombstones,
    }


def _dump(doc: Dict[str, Any]) -> str:
    # ensure_ascii=False matches the hand-authored config/ files, which carry
    # literal em dashes and arrows. Escaping them here would make the contract
    # render prose copied from those files differently from its source.
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


def build_contract() -> Dict[str, Any]:
    """Load every source declaration and return the generated contract."""
    return generate(
        load_json(BINDINGS_PATH),
        load_json(CATALOG_PATH),
        load_json(BUILDS_PATH),
        load_json(COMPAT_PATH),
        load_json(COMPILE_ONLY_PATH),
        load_json(PREVIEW_TARGETS_PATH),
        load_json(ROOM_BUNDLES_PATH),
    )


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "Do not write; exit non-zero if the on-disk contract differs "
            "from the regenerated contract."
        ),
    )
    args = parser.parse_args(argv)

    doc = build_contract()
    rendered = _dump(doc)
    relative = CONTRACT_PATH.relative_to(REPO_ROOT)

    if args.check:
        if not CONTRACT_PATH.exists():
            print(
                f"❌ {relative} does not exist; run "
                "`python3 scripts/generate_config_string_contract.py`."
            )
            return 1
        if CONTRACT_PATH.read_text() != rendered:
            print(
                f"❌ {relative} is stale; run "
                "`python3 scripts/generate_config_string_contract.py`."
            )
            return 1
        print(
            f"✅ {relative} is up to date "
            f"({doc['totals']['configurations']} configurations)."
        )
        return 0

    CONTRACT_PATH.write_text(rendered)
    print(
        f"✅ Wrote {relative} "
        f"({doc['totals']['configurations']} configurations, "
        f"{doc['totals']['tombstones']} tombstones)."
    )
    for lane, count in doc["totals"]["by_classification"].items():
        print(f"    {lane}: {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

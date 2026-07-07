#!/usr/bin/env python3
"""Generate customer-facing Home Assistant entity tables for the served products.

PRODUCT-GUIDES-001 (G1). For each config string served to customers via
WebFlash (see ``SERVED_CONFIG_STRINGS``), this script resolves the product's
package composition — the ``products/webflash/`` wrapper declared in
``config/webflash-builds.json``, through the ``products/`` compat shim and the
``products/bundles/`` bundle, down every local ``!include`` in each
``packages:`` block — and mechanically derives the Home Assistant entities the
firmware exposes (name, type, unit, notes). One markdown include per config is
written under ``site/generated/`` for the mkdocs product-guides site to embed.

PRODUCT-GUIDES-001 (G2) extends the derivation with the four-product
comparison matrix (``site/generated/compare-matrix.md``): module composition
and hardware SKUs come from ``config/product-catalog.json``, the release
channel and version from ``config/webflash-builds.json``, and every
capability cell is a mechanical membership test against the same derived
entity sets the tables are built from — so the matrix can never drift from
the catalog or the firmware YAML.

The tables are DERIVED, never hand-edited: every row traces to an entity
definition in the resolved YAML. Entities marked ``internal: true`` are
firmware-internal and never reach Home Assistant, so they are excluded.

Run with::

    python3 scripts/generate_product_entity_tables.py

Add ``--check`` to verify the on-disk tables match the regenerated output
without writing (the freshness gate used by CI and the local gate).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import json

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"
OUTPUT_DIR = REPO_ROOT / "site" / "generated"
COMPARE_OUTPUT_NAME = "compare-matrix.md"

# The four customer-served configs in PRODUCT-GUIDES-001 scope. Each MUST have
# a row in config/webflash-builds.json (the release-eligibility source of
# truth), which supplies the product YAML the derivation starts from.
SERVED_CONFIG_STRINGS = (
    "Ceiling-POE-RoomIQ",
    "Ceiling-POE-AirIQ-RoomIQ",
    "Ceiling-POE-VentIQ-RoomIQ",
    "Ceiling-POE-VentIQ-RoomIQ-LED",
)

# ESPHome component blocks whose list items define Home Assistant entities,
# with the customer-facing type label used in the table. Order fixes the
# grouping order of the generated tables.
ENTITY_COMPONENTS = (
    ("sensor", "Sensor"),
    ("binary_sensor", "Binary sensor"),
    ("text_sensor", "Text sensor"),
    ("switch", "Switch"),
    ("number", "Number"),
    ("select", "Select"),
    ("button", "Button"),
    ("light", "Light"),
    ("fan", "Fan"),
    ("climate", "Climate"),
    ("cover", "Cover"),
    ("lock", "Lock"),
    ("valve", "Valve"),
    ("event", "Event"),
    ("text", "Text"),
    ("datetime", "Datetime"),
)

# Default units for sensor platforms that expose a fixed unit without
# declaring ``unit_of_measurement`` in YAML. Values are the ESPHome component
# defaults (see the matching component pages at esphome.io). Only platforms
# actually reaching the tables need an entry; unknown platforms without an
# explicit unit render as "—".
PLATFORM_DEFAULT_UNITS = {
    "wifi_signal": "dBm",
    "uptime": "s",
    "internal_temperature": "°C",
    "duty_time": "s",
}

# Column labels for the comparison matrix, mirroring the product-guide nav
# titles in site/mkdocs.yml. Each column header links to the guide page,
# whose filename is the lower-cased config string (compare.md lives in the
# same site/docs/products/ directory).
MATRIX_COLUMN_LABELS = {
    "Ceiling-POE-RoomIQ": "RoomIQ",
    "Ceiling-POE-AirIQ-RoomIQ": "AirIQ + RoomIQ",
    "Ceiling-POE-VentIQ-RoomIQ": "VentIQ + RoomIQ",
    "Ceiling-POE-VentIQ-RoomIQ-LED": "VentIQ + RoomIQ + LED",
}

# Comparison-matrix capability rows. The row LABELS are curated for
# customers; every cell VALUE is a mechanical membership test — "✓" exactly
# when the product's resolved firmware YAML exposes at least one of the
# named entities (same derivation, same internal:true exclusion as the
# entity tables). A capability never shows without a matching Home
# Assistant entity, so the matrix cannot drift from the firmware source.
# Row shape: (customer label, entity type label, candidate entity names).
MATRIX_CAPABILITY_SECTIONS = (
    (
        "Room sensing",
        (
            ("Presence detection (radar)", "Binary sensor", ("Presence",)),
            ("Presence score", "Sensor", ("Presence Score",)),
            ("Temperature", "Sensor", ("RoomIQ Temperature",)),
            ("Humidity", "Sensor", ("RoomIQ Humidity",)),
            ("Feels-like temperature", "Sensor", ("RoomIQ Feels Like",)),
            ("Ambient light level", "Sensor", ("RoomIQ Light Level",)),
            ("Comfort score", "Sensor", ("RoomIQ Comfort Score",)),
        ),
    ),
    (
        "Air quality",
        (
            ("VOC index", "Sensor", ("VentIQ VOC Index",)),
            ("NOx index", "Sensor", ("VentIQ NOx Index",)),
            ("Barometric pressure", "Sensor", ("VentIQ Pressure",)),
            ("Dew point", "Sensor", ("VentIQ Dew Point",)),
            # NOTE: the AirIQ profile's "Air Quality State" text sensor is a
            # placeholder that always reads "unknown" (see
            # packages/features/airiq_basic_profile.yaml), so it deliberately
            # does NOT count as an air-quality summary capability here.
            ("Air-quality summary", "Text sensor", ("Air Quality",)),
        ),
    ),
    (
        "Bathroom intelligence",
        (
            ("Shower detection", "Binary sensor", ("Shower Active",)),
            ("Mould-risk tracking", "Sensor", ("Mold Risk Level",)),
            ("Mould-risk warning", "Binary sensor", ("Mold Risk Warning",)),
            ("Odour detection", "Binary sensor", ("Odor Detected",)),
            ("Ventilation-needed alert", "Binary sensor", ("Ventilation Needed",)),
            ("Recommended fan speed", "Sensor", ("Recommended Fan Speed",)),
        ),
    ),
    (
        "Outputs and controls",
        (
            ("LED ring light", "Light", ("LED Ring",)),
            ("LED night mode", "Switch", ("Night Mode",)),
            ("Relay output", "Switch", ("Relay",)),
            ("Auto-ventilation control", "Switch", ("Auto Ventilation",)),
        ),
    ),
)

SUBSTITUTION_RE = re.compile(r"\$\{(\w+)\}|\$(\w+)")

GENERATED_BANNER = (
    "<!--\n"
    "  AUTO-GENERATED — DO NOT EDIT.\n"
    "  Generated by scripts/generate_product_entity_tables.py from the\n"
    "  firmware YAML composition listed below (PRODUCT-GUIDES-001).\n"
    "  Regenerate:      python3 scripts/generate_product_entity_tables.py\n"
    "  Freshness gate:  python3 scripts/generate_product_entity_tables.py"
    " --check\n"
    "-->\n"
)


class IncludeRef(str):
    """Marker for a scalar ``!include`` value so package includes can be
    followed. Subclassing ``str`` keeps every other consumer behaviour
    identical to the plain scalar the generic constructor would return."""


class _DocsLoader(yaml.SafeLoader):
    """SafeLoader subclass with ESPHome tag constructors registered locally
    (per CLAUDE.md: safe loading with registered tag constructors — never
    unsafe loading). A subclass is used so the registrations cannot leak
    into other SafeLoader users in the same process."""


def _generic_constructor(loader: yaml.Loader, node: yaml.Node) -> Any:
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None


def _include_constructor(loader: yaml.Loader, node: yaml.Node) -> Any:
    if isinstance(node, yaml.ScalarNode):
        return IncludeRef(loader.construct_scalar(node))
    return _generic_constructor(loader, node)


_DocsLoader.add_constructor("!include", _include_constructor)
for _tag in ("!secret", "!extend", "!lambda", "!remove"):
    _DocsLoader.add_constructor(_tag, _generic_constructor)
_DocsLoader.add_multi_constructor("!include_dir_", _generic_constructor)


def load_yaml(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.load(handle, Loader=_DocsLoader)
    return data if isinstance(data, dict) else {}


def _collect_named_dicts(node: Dict[str, Any], out: List[Dict[str, Any]]) -> None:
    """Collect entity-defining dicts: the node itself if it carries a ``name``,
    plus nested sub-entity dicts (e.g. ``sht4x`` temperature/humidity,
    ``ld2450`` targets, ``wifi_info`` fields). Only dict values are recursed —
    list values (``filters``, ``effects``, ``on_*`` automations) never define
    additional Home Assistant entities."""
    if isinstance(node.get("name"), str):
        out.append(node)
    for key, value in node.items():
        if key == "name" or key.startswith("on_"):
            continue
        if isinstance(value, dict):
            _collect_named_dicts(value, out)


def _render_name(raw_name: str, subs: Dict[str, str]) -> str:
    """Render an entity name for the docs table: the user-configurable
    ``${friendly_name}`` prefix is stripped (documented once per table), and
    any other substitution is resolved from the merged substitution context."""

    def _replace(match: "re.Match[str]") -> str:
        var = match.group(1) or match.group(2)
        if var == "friendly_name":
            return ""
        value = subs.get(var)
        return str(value) if value is not None else match.group(0)

    return SUBSTITUTION_RE.sub(_replace, raw_name).strip()


class EntityCollector:
    """Walks a product YAML's local package includes and collects the Home
    Assistant entities the resolved configuration exposes."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.entities: List[Dict[str, Any]] = []
        self.source_files: List[Path] = []
        self.substitutions: Dict[str, str] = {}
        self._visited: set = set()

    def walk(self, path: Path, parent_subs: Optional[Dict[str, str]] = None) -> None:
        path = path.resolve()
        if path in self._visited:
            return
        self._visited.add(path)
        self.source_files.append(path)

        config = load_yaml(path)

        # ESPHome substitution semantics: the including file's substitutions
        # override the included package's defaults, so the parent context wins.
        file_subs = config.get("substitutions")
        subs: Dict[str, str] = {}
        if isinstance(file_subs, dict):
            subs.update({str(k): v for k, v in file_subs.items()})
            # Effective top-down view (outermost definition wins), used for
            # the table's "firmware default" friendly-name annotation.
            for key, value in file_subs.items():
                self.substitutions.setdefault(str(key), value)
        if parent_subs:
            subs.update(parent_subs)

        for component_key, type_label in ENTITY_COMPONENTS:
            block = config.get(component_key)
            if isinstance(block, dict):
                block = [block]
            if not isinstance(block, list):
                continue
            for item in block:
                if not isinstance(item, dict):
                    continue
                named: List[Dict[str, Any]] = []
                _collect_named_dicts(item, named)
                platform = item.get("platform")
                for node in named:
                    self._record(node, platform, type_label, subs, path)

        self._walk_packages(config.get("packages"), path, subs)

    def _walk_packages(self, packages: Any, path: Path, subs: Dict[str, str]) -> None:
        if isinstance(packages, dict):
            values = list(packages.values())
        elif isinstance(packages, list):
            values = packages
        else:
            return
        for value in values:
            if isinstance(value, IncludeRef):
                self.walk((path.parent / str(value)).resolve(), subs)
            # Remote packages (dicts with url/files) and non-include values
            # cannot be resolved locally and are intentionally skipped; the
            # served products compose exclusively via local !include.

    def _record(
        self,
        node: Dict[str, Any],
        platform: Optional[str],
        type_label: str,
        subs: Dict[str, str],
        path: Path,
    ) -> None:
        if node.get("internal") is True:
            return  # never exposed to Home Assistant
        name = _render_name(str(node["name"]), subs)
        unit = node.get("unit_of_measurement")
        if unit is None and platform in PLATFORM_DEFAULT_UNITS:
            unit = PLATFORM_DEFAULT_UNITS[platform]
        self.entities.append(
            {
                "name": name,
                "type": type_label,
                "unit": str(unit) if unit is not None else "",
                "device_class": node.get("device_class", ""),
                "entity_category": node.get("entity_category", ""),
                "disabled_by_default": node.get("disabled_by_default") is True,
                "source": str(path.relative_to(self.repo_root)),
            }
        )


def load_build_rows() -> Dict[str, Dict[str, Any]]:
    data = json.loads(BUILDS_PATH.read_text(encoding="utf-8"))
    return {row["config_string"]: row for row in data.get("builds", [])}


def collect_for_config(config_string: str) -> EntityCollector:
    rows = load_build_rows()
    if config_string not in rows:
        raise KeyError(
            f"config string {config_string!r} has no row in {BUILDS_PATH.name}"
        )
    product_yaml = REPO_ROOT / rows[config_string]["product_yaml"]
    collector = EntityCollector(REPO_ROOT)
    collector.walk(product_yaml)
    return collector


def _entity_notes(entity: Dict[str, Any]) -> str:
    notes = []
    if entity["device_class"]:
        notes.append(f"device class: {entity['device_class']}")
    if entity["entity_category"]:
        notes.append(f"{entity['entity_category']} entity")
    if entity["disabled_by_default"]:
        notes.append("disabled by default")
    return "; ".join(notes) if notes else "—"


def render_table(config_string: str, collector: EntityCollector) -> str:
    rows = load_build_rows()[config_string]
    type_order = {label: i for i, (_, label) in enumerate(ENTITY_COMPONENTS)}

    seen: set = set()
    entities = []
    for entity in collector.entities:
        key = (entity["type"], entity["name"])
        if key in seen:
            continue
        seen.add(key)
        entities.append(entity)
    entities.sort(key=lambda e: (type_order[e["type"]], e["name"].lower()))

    friendly_name = collector.substitutions.get("friendly_name", "")
    sources = sorted(str(p.relative_to(REPO_ROOT)) for p in collector.source_files)

    lines: List[str] = [GENERATED_BANNER]
    lines.append(f"<!-- Config string: {config_string} -->")
    lines.append(f"<!-- Derived from: {rows['product_yaml']} -->")
    lines.append("<!-- Resolved package composition:")
    for source in sources:
        lines.append(f"       {source}")
    lines.append("-->")
    lines.append("")
    lines.append(
        f"The `{config_string}` firmware exposes **{len(entities)} entities** "
        "to Home Assistant."
    )
    lines.append("")
    lines.append(
        "Entity names below appear in Home Assistant prefixed with the "
        "device's friendly name, which you choose during setup (firmware "
        f"default: `{friendly_name}`). Firmware-internal measurements "
        "(marked `internal` in the YAML) never reach Home Assistant and are "
        "not listed."
    )
    lines.append("")
    lines.append("| Entity | Type | Unit | Notes |")
    lines.append("|---|---|---|---|")
    for entity in entities:
        unit = entity["unit"] if entity["unit"] else "—"
        lines.append(
            f"| {entity['name']} | {entity['type']} | {unit} "
            f"| {_entity_notes(entity)} |"
        )
    lines.append("")
    return "\n".join(lines)


def load_catalog_products() -> Dict[str, Dict[str, Any]]:
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    return {
        product["config_string"]: product
        for product in data.get("products", [])
        if "config_string" in product
    }


def _module_cell(product: Dict[str, Any], module_key: str) -> str:
    """Render a module cell from the catalog entry: the module token plus
    its hardware SKU (matched by the lower-cased token), or an em dash when
    the module slot is 'none'."""
    token = product.get("modules", {}).get(module_key, "none")
    if token in ("none", None):
        return "—"
    sku = product.get("hardware", {}).get(str(token).lower())
    return f"{token} ({sku})" if sku else str(token)


def render_compare_matrix(collectors: Dict[str, "EntityCollector"]) -> str:
    build_rows = load_build_rows()
    catalog = load_catalog_products()

    entity_sets: Dict[str, set] = {}
    entity_counts: Dict[str, int] = {}
    for config_string, collector in collectors.items():
        keys = {(e["type"], e["name"]) for e in collector.entities}
        entity_sets[config_string] = keys
        entity_counts[config_string] = len(keys)

    def row(label: str, cells: List[str]) -> str:
        return "| " + " | ".join([label] + cells) + " |"

    lines: List[str] = [GENERATED_BANNER]
    lines.append("<!-- Comparison matrix for the served products.")
    lines.append(
        "     Modules/hardware: config/product-catalog.json ·"
        " channel/version: config/webflash-builds.json ·"
    )
    lines.append(
        "     capability cells: membership tests against the derived"
        " Home Assistant entity sets. -->"
    )
    lines.append("")
    headers = [""]
    for config_string in SERVED_CONFIG_STRINGS:
        label = MATRIX_COLUMN_LABELS.get(config_string, config_string)
        headers.append(f"[{label}]({config_string.lower()}.md)")
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|---" * len(headers) + "|")

    lines.append(
        row(
            "**Config string**",
            [f"`{c}`" for c in SERVED_CONFIG_STRINGS],
        )
    )
    channel_cells = []
    for config_string in SERVED_CONFIG_STRINGS:
        build = build_rows[config_string]
        channel = str(build["channel"])
        badge = f'<span class="s360-badge s360-badge--{channel}">{channel}</span>'
        channel_cells.append(f"{badge} v{build['version']}")
    lines.append(row("**Channel / version**", channel_cells))

    for module_label, module_key in (
        ("**Power**", "power"),
        ("**Air-quality module**", "air_quality"),
        ("**Room-sensing module**", "room_sense"),
        ("**LED module**", "led"),
    ):
        cells = [_module_cell(catalog[c], module_key) for c in SERVED_CONFIG_STRINGS]
        lines.append(row(module_label, cells))

    for section_title, capability_rows in MATRIX_CAPABILITY_SECTIONS:
        lines.append(row(f"**{section_title}**", [""] * len(SERVED_CONFIG_STRINGS)))
        for label, type_label, candidates in capability_rows:
            cells = []
            for config_string in SERVED_CONFIG_STRINGS:
                exposed = any(
                    (type_label, name) in entity_sets[config_string]
                    for name in candidates
                )
                cells.append("✓" if exposed else "—")
            lines.append(row(label, cells))

    lines.append(
        row(
            "**Home Assistant entities**",
            [str(entity_counts[c]) for c in SERVED_CONFIG_STRINGS],
        )
    )
    lines.append("")
    return "\n".join(lines)


def expected_outputs() -> Dict[Path, str]:
    outputs: Dict[Path, str] = {}
    collectors: Dict[str, EntityCollector] = {}
    for config_string in SERVED_CONFIG_STRINGS:
        collector = collect_for_config(config_string)
        collectors[config_string] = collector
        out_path = OUTPUT_DIR / f"{config_string.lower()}-entities.md"
        outputs[out_path] = render_table(config_string, collector)
    outputs[OUTPUT_DIR / COMPARE_OUTPUT_NAME] = render_compare_matrix(collectors)
    return outputs


def write_outputs() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path, content in expected_outputs().items():
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path.relative_to(REPO_ROOT)}")
    return 0


def check_outputs() -> int:
    outputs = expected_outputs()
    stale: List[str] = []
    for path, content in outputs.items():
        rel = str(path.relative_to(REPO_ROOT))
        if not path.exists():
            stale.append(f"{rel}: missing")
        elif path.read_text(encoding="utf-8") != content:
            stale.append(f"{rel}: out of date")
    if OUTPUT_DIR.exists():
        expected_names = {path.name for path in outputs}
        for existing in sorted(OUTPUT_DIR.glob("*.md")):
            if existing.name not in expected_names:
                stale.append(
                    f"{existing.relative_to(REPO_ROOT)}: unexpected file "
                    "(not produced by the generator)"
                )
    if stale:
        print("Entity tables are STALE:")
        for line in stale:
            print(f"  - {line}")
        print("Regenerate with: python3 scripts/generate_product_entity_tables.py")
        return 1
    print(f"Entity tables are fresh ({len(outputs)} files).")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the on-disk tables match the regenerated output",
    )
    args = parser.parse_args(argv)
    return check_outputs() if args.check else write_outputs()


if __name__ == "__main__":
    sys.exit(main())

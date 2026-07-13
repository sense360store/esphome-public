#!/usr/bin/env python3
"""PRESENCE-FRAMEWORK-001 — tri-sensor customer Presence experience contract.

These tests define (and then pin) the coordinated three-sensor Presence
framework for the Sense360 RoomIQ board (S360-200): PIR (immediate movement),
HLK-LD2450 (movement / target tracking / radar target count) and DFRobot
SEN0609 (static presence), fused into ONE customer-facing occupancy
capability.

Contract highlights enforced here:

* Customer entities are exactly: Occupancy, Presence Status, Radar Target
  Count, Presence Mode, Clear Delay — stable ``s360_``-prefixed IDs,
  product-facing names, enabled by default. There is deliberately NO
  "Presence Sensitivity" entity (no honest common runtime sensitivity
  contract exists across the three sensors) and NO "People Count" entity
  (radar targets are not verified people).
* Technical detail (individual sensor states, per-target radar data,
  moving/still counts, stale-data timers) is diagnostic and/or disabled by
  default; LD2450 per-target coordinates keep stable IDs for future
  Sense360Zones consumption.
* The fusion logic is a single header-only implementation
  (``include/sense360/presence_fusion.h``) shared by production YAML and the
  deterministic simulation tests (``tests/unit/test_presence_fusion.cpp``) —
  no second implementation that can drift.
* Fail-safe clear rules: stale/unavailable data is unknown (never clear);
  the LD2450 adapter carries a real freshness signal; the arbitrary
  synthetic confidence tiers (0.95 / 0.7 / 0.6) are removed.
* The Presence module status is wired to the Core-Framework reserved runtime
  vocabulary (Initialising / Available / Degraded / Unavailable / Fault) by
  a real supported signal, and ``config/core-framework.json`` records that
  wiring (PD-07 / CORE-FRAMEWORK-001 extension rules).
* Firmware-build / simulation proof only — no hardware, bench, compliance or
  commercial claim anywhere.

Uses Python's stdlib unittest (repo convention). Run with::

    python3 tests/test_presence_framework.py
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any, Dict, List

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

FUSION_PACKAGE = REPO_ROOT / "packages" / "features" / "presence_framework.yaml"
PIR_PACKAGE = REPO_ROOT / "packages" / "boards" / "s360-200-roomiq-pir.yaml"
SEN0609_PACKAGE = REPO_ROOT / "packages" / "boards" / "s360-200-roomiq-sen0609.yaml"
RADAR_PACKAGE = REPO_ROOT / "packages" / "boards" / "s360-200-roomiq-radar.yaml"
HEADER = REPO_ROOT / "include" / "sense360" / "presence_fusion.h"
CPP_TEST = REPO_ROOT / "tests" / "unit" / "test_presence_fusion.cpp"
DOC = REPO_ROOT / "docs" / "architecture" / "sense360-presence-framework.md"
CHECKLIST = REPO_ROOT / "docs" / "hardware" / "presence-framework-bench-checklist.md"
COMPILE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "core-framework-compile.yml"
VALIDATE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "validate.yml"
CONTRACT = REPO_ROOT / "config" / "core-framework.json"
MATRIX = REPO_ROOT / "config" / "feature-entity-matrix.json"
ROADMAP = REPO_ROOT / "docs" / "sense360-roadmap-status.md"
BUNDLES_DIR = REPO_ROOT / "products" / "bundles"

CUSTOMER_STATUS_VALUES = (
    "Initialising",
    "Clear",
    "Movement detected",
    "Still presence",
    "Multiple people",
    "Sensor degraded",
    "Unavailable",
)

MODULE_HEALTH_VALUES = (
    "Initialising",
    "Available",
    "Degraded",
    "Unavailable",
    "Fault",
)

MODE_OPTIONS = ["Balanced", "Responsive", "Stable", "Custom"]

ADAPTER_INCLUDES = (
    "!include ../../packages/boards/s360-200-roomiq-pir.yaml",
    "!include ../../packages/boards/s360-200-roomiq-sen0609.yaml",
    "!include ../../packages/features/presence_framework.yaml",
)

ENTITY_PLATFORM_KEYS = (
    "sensor",
    "binary_sensor",
    "text_sensor",
    "switch",
    "number",
    "button",
    "select",
)


# --- ESPHome-tag-tolerant YAML loading --------------------------------------


def _esphome_tag(loader, node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None


for _tag in ("!secret", "!include", "!extend", "!lambda", "!remove"):
    yaml.add_constructor(_tag, _esphome_tag, Loader=yaml.SafeLoader)
yaml.add_multi_constructor("!include_dir_", _esphome_tag, Loader=yaml.SafeLoader)


def load_yaml(path: Path) -> Dict[str, Any]:
    doc = yaml.safe_load(path.read_text())
    return doc if isinstance(doc, dict) else {}


def entities_by_id(doc: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Flatten all top-level entity entries keyed by id."""
    out: Dict[str, Dict[str, Any]] = {}
    for platform in ENTITY_PLATFORM_KEYS:
        for entry in doc.get(platform) or []:
            if isinstance(entry, dict) and isinstance(entry.get("id"), str):
                out[entry["id"]] = dict(entry, _platform=platform)
    return out


def presence_bundles() -> List[Path]:
    """Bundle files whose contract entry declares the presence capability."""
    contract = json.loads(CONTRACT.read_text())
    paths = []
    for entry in contract.get("configs", {}).values():
        if "presence" in (entry.get("capabilities") or []):
            paths.append(REPO_ROOT / entry["bundle"])
    return sorted(paths)


# --- Package existence -------------------------------------------------------


class PackageFilesExistTests(unittest.TestCase):
    def test_new_files_exist(self) -> None:
        for path in (
            FUSION_PACKAGE,
            PIR_PACKAGE,
            SEN0609_PACKAGE,
            HEADER,
            CPP_TEST,
            DOC,
            CHECKLIST,
        ):
            self.assertTrue(
                path.is_file(), f"missing PRESENCE-FRAMEWORK-001 file: {path}"
            )

    def test_no_secret_material_in_new_packages(self) -> None:
        for path in (FUSION_PACKAGE, PIR_PACKAGE, SEN0609_PACKAGE):
            raw = path.read_text().lower()
            self.assertNotIn("!secret", raw, path.name)
            for needle in ("password", "api_encryption", "token"):
                self.assertNotIn(needle, raw, path.name)


# --- Customer entity layer ----------------------------------------------------


class CustomerEntityContractTests(unittest.TestCase):
    """The default-enabled customer surface is exactly the accepted set."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = load_yaml(FUSION_PACKAGE)
        cls.raw = FUSION_PACKAGE.read_text()
        cls.entities = entities_by_id(cls.doc)

    def _entity(self, entity_id: str) -> Dict[str, Any]:
        self.assertIn(entity_id, self.entities, f"missing entity id {entity_id}")
        return self.entities[entity_id]

    def test_occupancy_entity(self) -> None:
        entity = self._entity("s360_occupancy")
        self.assertEqual(entity["_platform"], "binary_sensor")
        self.assertEqual(entity.get("name"), "Occupancy")
        self.assertEqual(entity.get("device_class"), "occupancy")
        self.assertFalse(entity.get("disabled_by_default", False))
        self.assertNotIn("entity_category", entity)
        self.assertNotEqual(entity.get("internal"), True)

    def test_presence_status_entity(self) -> None:
        entity = self._entity("s360_presence_status")
        self.assertEqual(entity["_platform"], "text_sensor")
        self.assertEqual(entity.get("name"), "Presence Status")
        self.assertFalse(entity.get("disabled_by_default", False))

    def test_radar_target_count_entity(self) -> None:
        entity = self._entity("s360_radar_target_count")
        self.assertEqual(entity["_platform"], "sensor")
        self.assertEqual(entity.get("name"), "Radar Target Count")
        self.assertFalse(entity.get("disabled_by_default", False))
        self.assertEqual(entity.get("state_class"), "measurement")
        self.assertEqual(entity.get("accuracy_decimals"), 0)
        # A count of radar targets is dimensionless: no unit that could imply
        # a cumulative or physical measurement.
        self.assertNotIn("unit_of_measurement", entity)

    def test_presence_mode_entity(self) -> None:
        entity = self._entity("s360_presence_mode")
        self.assertEqual(entity["_platform"], "select")
        self.assertEqual(entity.get("name"), "Presence Mode")
        self.assertEqual(entity.get("options"), MODE_OPTIONS)
        self.assertTrue(entity.get("restore_value"))
        self.assertEqual(entity.get("initial_option"), "Balanced")
        self.assertFalse(entity.get("disabled_by_default", False))

    def test_clear_delay_entity(self) -> None:
        entity = self._entity("s360_presence_clear_delay")
        self.assertEqual(entity["_platform"], "number")
        self.assertEqual(entity.get("name"), "Clear Delay")
        self.assertEqual(float(entity.get("min_value")), 5.0)
        self.assertEqual(float(entity.get("max_value")), 600.0)
        self.assertEqual(float(entity.get("step")), 5.0)
        self.assertEqual(float(entity.get("initial_value")), 30.0)
        self.assertTrue(entity.get("restore_value"))
        self.assertEqual(entity.get("unit_of_measurement"), "s")
        self.assertFalse(entity.get("disabled_by_default", False))

    def test_no_sensitivity_entity(self) -> None:
        # PD-05: a single numeric sensitivity cannot be honestly mapped onto
        # PIR + LD2450 + SEN0609 today, so mode-based tuning ships first.
        for entity in self.entities.values():
            name = str(entity.get("name", ""))
            self.assertNotIn("sensitivity", name.lower(), name)

    def test_no_people_count_entity(self) -> None:
        # PD-09: radar targets are not verified people.
        for entity in self.entities.values():
            name = str(entity.get("name", "")).lower()
            self.assertNotIn("people count", name)
            self.assertNotIn("person count", name)

    def test_no_confidence_entity(self) -> None:
        # No unsupported confidence claim is exposed to customers.
        for entity in self.entities.values():
            name = str(entity.get("name", "")).lower()
            self.assertNotIn("confidence", name)

    def test_legacy_compat_entities_are_fusion_driven_and_disabled(self) -> None:
        # The pre-framework customer entities keep their exact IDs and names
        # (Home Assistant entity IDs stay stable for existing installs) but
        # are disabled by default for new installs; the customer set above is
        # the default surface.
        binary = self._entity("presence_binary")
        self.assertEqual(binary.get("name"), "${friendly_name} Presence")
        self.assertTrue(binary.get("disabled_by_default"))
        score = self._entity("presence_score")
        self.assertEqual(score.get("name"), "${friendly_name} Presence Score")
        self.assertTrue(score.get("disabled_by_default"))

    def test_stale_data_timer_is_diagnostic_and_disabled(self) -> None:
        entity = self._entity("s360_radar_data_age")
        self.assertEqual(entity.get("entity_category"), "diagnostic")
        self.assertTrue(entity.get("disabled_by_default"))

    def test_module_status_is_published_from_a_real_signal(self) -> None:
        # The fusion layer drives the framework's Presence Module Status
        # entity (reserved runtime vocabulary) — CORE-FRAMEWORK-001
        # extension rule 2.
        self.assertIn("s360_module_status_presence", self.raw)
        self.assertIn("health_to_string", self.raw)

    def test_fusion_uses_the_shared_header(self) -> None:
        # Single implementation: the production YAML includes the same
        # header the simulation tests exercise.
        self.assertIn("include/sense360/presence_fusion.h", self.raw)


# --- Sensor adapters -----------------------------------------------------------


class PirAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = load_yaml(PIR_PACKAGE)
        cls.raw = PIR_PACKAGE.read_text()
        cls.entities = entities_by_id(cls.doc)

    def test_pir_uses_authoritative_pin(self) -> None:
        # Schematic PIR net: IO15, declared by the Core board package as
        # pir_sensor_pin. The adapter must consume that substitution, never
        # hard-code a pin.
        self.assertIn("${pir_sensor_pin}", self.raw)

    def test_pir_raw_state_is_diagnostic_and_disabled(self) -> None:
        entity = self.entities.get("s360_pir_motion")
        self.assertIsNotNone(entity, "missing s360_pir_motion")
        self.assertEqual(entity["_platform"], "binary_sensor")
        self.assertEqual(entity.get("platform"), "gpio")
        self.assertEqual(entity.get("device_class"), "motion")
        self.assertEqual(entity.get("entity_category"), "diagnostic")
        self.assertTrue(entity.get("disabled_by_default"))

    def test_pir_health_limitation_documented(self) -> None:
        # A permanently low PIR input may be healthy or disconnected; the
        # adapter must not fabricate health detection.
        lowered = self.raw.lower()
        self.assertIn("cannot", lowered)
        self.assertIn("disconnected", lowered)


class Sen0609AdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = load_yaml(SEN0609_PACKAGE)
        cls.raw = SEN0609_PACKAGE.read_text()
        cls.entities = entities_by_id(cls.doc)

    def test_sen0609_uses_authoritative_output_pin(self) -> None:
        # Schematic: IO6 = out(gpio6) — the SEN0609 digital presence output
        # line declared by the Core board package.
        self.assertIn("${roomiq_sen0609_output_pin}", self.raw)

    def test_sen0609_defines_no_uart(self) -> None:
        # The authoritative SEN0609 UART (roomiq_sen0609_uart, 115200 baud)
        # is owned by the Core board package; the adapter must not redefine
        # a bus. (ESPHome 2026.4.5 carries no supported C4001/SEN0609 UART
        # component, so the adapter uses the documented digital output.)
        self.assertNotIn("uart", set(self.doc.keys()))

    def test_sen0609_state_is_diagnostic_and_disabled(self) -> None:
        entity = self.entities.get("s360_sen0609_presence")
        self.assertIsNotNone(entity, "missing s360_sen0609_presence")
        self.assertEqual(entity["_platform"], "binary_sensor")
        self.assertEqual(entity.get("platform"), "gpio")
        self.assertEqual(entity.get("device_class"), "occupancy")
        self.assertEqual(entity.get("entity_category"), "diagnostic")
        self.assertTrue(entity.get("disabled_by_default"))

    def test_sen0609_invents_no_detail(self) -> None:
        # SEN0609 via its digital output provides presence only: no target
        # count, distance, speed or movement detail may be fabricated.
        for entity in self.entities.values():
            name = str(entity.get("name", "")).lower()
            for forbidden in ("distance", "speed", "count", "angle"):
                self.assertNotIn(forbidden, name)


class RadarAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = load_yaml(RADAR_PACKAGE)
        cls.raw = RADAR_PACKAGE.read_text()

    def test_radar_has_real_freshness_signal(self) -> None:
        # Freshness must come from a supported update callback (on_value of
        # the LD2450 frame-driven sensors), not from re-reading unchanged
        # values in a periodic lambda.
        self.assertIn("s360_radar_last_frame_ms", self.raw)
        self.assertIn("on_value", self.raw)

    def test_synthetic_confidence_tiers_removed(self) -> None:
        # The arbitrary 0.95 / 0.7 / 0.6 tiers had no evidence basis.
        for needle in ("0.95f", "0.7f", "0.6f"):
            self.assertNotIn(needle, self.raw)

    def test_zones_coordinate_ids_stay_stable(self) -> None:
        # Sense360Zones consumes the per-target coordinate stream; the IDs
        # are a stable API surface.
        for target in (1, 2, 3):
            for axis in ("x", "y", "speed", "distance", "angle"):
                self.assertIn(f"ld2450_t{target}_{axis}", self.raw)

    def test_target_detail_is_diagnostic_or_internal(self) -> None:
        doc = self.doc
        for entry in doc.get("sensor") or []:
            if not isinstance(entry, dict) or entry.get("platform") != "ld2450":
                continue
            nested: List[Dict[str, Any]] = []
            for key, value in entry.items():
                if key.startswith("target_") and isinstance(value, dict):
                    nested.extend(v for v in value.values() if isinstance(v, dict))
                elif key.endswith("_count") and isinstance(value, dict):
                    nested.append(value)
            self.assertTrue(nested, "no ld2450 nested sensors parsed")
            for sub in nested:
                internal = sub.get("internal") is True
                diagnostic_disabled = sub.get(
                    "entity_category"
                ) == "diagnostic" and sub.get("disabled_by_default")
                self.assertTrue(
                    internal or diagnostic_disabled,
                    f"{sub.get('id')}: radar detail must stay internal or "
                    "diagnostic+disabled",
                )


# --- Bundle wiring --------------------------------------------------------------


class BundleWiringTests(unittest.TestCase):
    def test_every_presence_bundle_composes_the_tri_sensor_set(self) -> None:
        bundles = presence_bundles()
        self.assertGreaterEqual(len(bundles), 10, "presence bundles not found")
        for bundle in bundles:
            raw = bundle.read_text()
            for include in ADAPTER_INCLUDES:
                self.assertIn(
                    include,
                    raw,
                    f"{bundle.name}: missing tri-sensor include {include}",
                )
            self.assertNotIn(
                "presence_basic_profile.yaml",
                raw,
                f"{bundle.name}: presence_basic_profile is superseded by the "
                "presence framework in bundles (legacy products keep it)",
            )

    def test_non_presence_bundles_do_not_compose_the_framework(self) -> None:
        presence = {p.resolve() for p in presence_bundles()}
        for bundle in sorted(BUNDLES_DIR.glob("*.yaml")):
            if bundle.resolve() in presence:
                continue
            raw = bundle.read_text()
            self.assertNotIn("presence_framework.yaml", raw, bundle.name)
            self.assertNotIn("s360-200-roomiq-pir.yaml", raw, bundle.name)

    def test_legacy_profile_and_alias_paths_still_resolve(self) -> None:
        # Customers pin legacy paths; they must keep existing.
        for rel in (
            "packages/features/presence_basic_profile.yaml",
            "packages/expansions/presence_ceiling.yaml",
        ):
            self.assertTrue((REPO_ROOT / rel).is_file(), rel)


# --- Fusion header / simulation layer -------------------------------------------


class FusionHeaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = HEADER.read_text() if HEADER.is_file() else ""

    def test_header_exists(self) -> None:
        self.assertTrue(HEADER.is_file(), f"missing {HEADER}")

    def test_customer_status_strings_are_single_sourced(self) -> None:
        for value in CUSTOMER_STATUS_VALUES:
            self.assertIn(f'"{value}"', self.raw, value)

    def test_module_health_strings_are_single_sourced(self) -> None:
        for value in MODULE_HEALTH_VALUES:
            self.assertIn(f'"{value}"', self.raw, value)

    def test_namespace_and_engine(self) -> None:
        self.assertIn("namespace sense360", self.raw)
        self.assertIn("class FusionEngine", self.raw)

    def test_simulation_tests_exist(self) -> None:
        # tests/Makefile auto-discovers tests/unit/test_*.cpp; the simulation
        # suite exercises the same header the production YAML compiles.
        self.assertTrue(CPP_TEST.is_file(), f"missing {CPP_TEST}")
        cpp = CPP_TEST.read_text()
        self.assertIn("presence_fusion.h", cpp)


# --- Contract file / core framework integration ---------------------------------


class CoreFrameworkContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text())

    def test_presence_capability_describes_tri_sensor_firmware(self) -> None:
        description = self.contract["capabilities"]["presence"]["description"]
        for term in ("LD2450", "PIR", "SEN0609"):
            self.assertIn(term, description)
        # PIR / SEN0609 are compiled now; the old "not compiled" marker and
        # any connector claim must be gone.
        self.assertNotIn("not compiled", description.lower())
        self.assertNotIn("connector", description.lower())

    def test_presence_runtime_status_is_recorded(self) -> None:
        runtime = self.contract.get("module_runtime_status") or {}
        self.assertIn("presence", runtime, "presence runtime wiring missing")
        entry = runtime["presence"]
        self.assertEqual(entry.get("work_item"), "PRESENCE-FRAMEWORK-001")
        self.assertEqual(entry.get("entity_id"), "s360_module_status_presence")
        self.assertEqual(sorted(entry.get("values") or []), sorted(MODULE_HEALTH_VALUES))
        signals = " ".join(entry.get("signals") or []).lower()
        self.assertIn("ld2450", signals)
        # Honesty: the GPIO-only sensors (PIR / SEN0609 digital output)
        # cannot prove communication health; the contract must say so.
        notes = str(entry.get("notes", "")).lower()
        self.assertIn("pir", notes)
        self.assertIn("cannot", notes)


# --- Feature-entity matrix -------------------------------------------------------


class FeatureEntityMatrixTests(unittest.TestCase):
    def test_pir_and_sen0609_rows_flipped_to_present(self) -> None:
        matrix = json.loads(MATRIX.read_text())
        board = next(b for b in matrix["boards"] if b["sku"] == "S360-200")
        wanted = {"SEN0609": False, "PIR": False}
        for row in board["rows"]:
            row_name = row["row"]
            for key in wanted:
                if key in row_name:
                    wanted[key] = True
                    self.assertEqual(row["status"], "present", row_name)
                    self.assertIsNone(row["queued_fill_slice"], row_name)
                    self.assertTrue(row["defined_in"], row_name)
                    self.assertTrue(row["present_as"], row_name)
        self.assertTrue(all(wanted.values()), f"rows not found: {wanted}")


# --- Compile lane / CI wiring ------------------------------------------------------


class CompileLaneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = COMPILE_WORKFLOW.read_text()
        cls.doc = yaml.safe_load(cls.raw)

    def _paths(self) -> List[str]:
        triggers = self.doc.get("on", self.doc.get(True)) or {}
        return (triggers.get("pull_request") or {}).get("paths") or []

    def test_paths_cover_presence_framework_surfaces(self) -> None:
        paths = self._paths()
        for needed in (
            "packages/boards/**",
            "packages/features/**",
            "include/sense360/**",
            "tests/unit/**",
            "tests/test_presence_framework.py",
        ):
            self.assertIn(needed, paths)

    def test_contract_gate_runs_presence_tests(self) -> None:
        self.assertIn("tests/test_presence_framework.py", self.raw)
        # The deterministic C++ simulation suite runs in the cheap gate job.
        self.assertIn("make -C tests test", self.raw)

    def test_lane_guarantees_unchanged(self) -> None:
        triggers = self.doc.get("on", self.doc.get(True)) or {}
        self.assertEqual(set(triggers), {"pull_request", "workflow_dispatch"})
        self.assertEqual(self.doc.get("permissions"), {"contents": "read"})
        self.assertNotIn("upload-artifact", self.raw)

    def test_quick_validation_gate_runs_presence_contract(self) -> None:
        self.assertIn(
            "tests/test_presence_framework.py", VALIDATE_WORKFLOW.read_text()
        )


# --- Documentation ------------------------------------------------------------------


class DocumentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = DOC.read_text() if DOC.is_file() else ""
        cls.lowered = cls.text.lower()

    def test_doc_exists_and_names_the_work_item(self) -> None:
        self.assertTrue(DOC.is_file(), f"missing {DOC}")
        self.assertIn("PRESENCE-FRAMEWORK-001", self.text)

    def test_customer_contract_documented(self) -> None:
        for value in CUSTOMER_STATUS_VALUES:
            self.assertIn(value, self.text, value)
        for name in (
            "Occupancy",
            "Presence Status",
            "Radar Target Count",
            "Presence Mode",
            "Clear Delay",
        ):
            self.assertIn(name, self.text, name)
        for mode in MODE_OPTIONS:
            self.assertIn(mode, self.text, mode)

    def test_health_and_precedence_documented(self) -> None:
        for value in MODULE_HEALTH_VALUES:
            self.assertIn(value, self.text, value)
        self.assertIn("precedence", self.lowered)

    def test_zones_contract_documented(self) -> None:
        self.assertIn("Zones", self.text)
        self.assertIn("ld2450_t1_x", self.text)

    def test_limitations_documented_honestly(self) -> None:
        self.assertIn("no hardware", self.lowered)
        self.assertIn("disabled by default", self.lowered)
        self.assertIn("pir", self.lowered)
        self.assertIn("sen0609", self.lowered)
        self.assertIn("cannot", self.lowered)
        for forbidden in ("hardware verified", "bench verified", "hardware-proven"):
            self.assertNotIn(forbidden, self.lowered)

    def test_radar_targets_not_claimed_as_people(self) -> None:
        # "Multiple people" is accepted customer wording, but the doc must
        # explain it is radar-derived and pending physical validation.
        self.assertIn("radar-derived", self.lowered)


class BenchChecklistTests(unittest.TestCase):
    def test_checklist_prepared_without_results(self) -> None:
        self.assertTrue(CHECKLIST.is_file(), f"missing {CHECKLIST}")
        text = CHECKLIST.read_text()
        lowered = text.lower()
        for topic in (
            "latency",
            "false trigger",
            "target count",
            "coordinate",
            "static presence",
            "seated",
            "sleeping",
            "walking",
            "exit",
            "multiple occupants",
            "disconnected",
            "uart recovery",
            "startup",
            "clear delay",
            "mode",
            "zones",
        ):
            self.assertIn(topic, lowered, topic)
        # Prepared, not executed: unchecked boxes only, no results, no
        # machine-written attestation (standing rule).
        self.assertIn("[ ]", text)
        self.assertNotIn("[x]", lowered)
        self.assertIn("no results", lowered)


class RoadmapTests(unittest.TestCase):
    def test_roadmap_records_presence_framework(self) -> None:
        text = ROADMAP.read_text()
        self.assertIn("PRESENCE-FRAMEWORK-001", text)
        section = text[text.index("PRESENCE-FRAMEWORK-001"):][:5000]
        lowered = section.lower()
        self.assertIn("SOT", section)
        self.assertIn("hardware", lowered)
        self.assertIn("pending", lowered)


if __name__ == "__main__":
    unittest.main(verbosity=2)

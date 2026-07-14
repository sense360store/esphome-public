#!/usr/bin/env python3
"""ROOMIQ-FRAMEWORK-001 — canonical comfort and environmental service contract.

These tests define (and then pin) the customer-focused Sense360 RoomIQ
environmental framework for the S360-200 RoomIQ climate half: calibrated
Temperature / Humidity / Illuminance, a human-friendly Comfort state, one
headline Environment State, a Brightness category, honest sensor freshness
and module health — all produced by ONE shared engine that other frameworks
(LED today; VentIQ / AirIQ / Zones later) consume instead of re-reading raw
sensors.

Contract highlights enforced here:

* Default-enabled customer entities are exactly: Temperature, Humidity,
  Illuminance, Comfort, Environment State, Brightness, plus the three
  calibration controls (Temperature Offset, Humidity Offset, Illuminance
  Calibration). No customer-facing numeric comfort score is enabled by
  default; no raw sensor model name (VEML7700 / LTR-303ALS / SHT4x) appears
  in any customer entity name.
* Calibration is applied exactly once (inside the shared engine); raw board
  sensors stay internal/diagnostic; downstream consumers (LED darkness,
  legacy compatibility entities) receive calibrated canonical values.
* The behaviour logic is a single header-only implementation
  (``include/sense360/roomiq_engine.h``) shared by production YAML and the
  deterministic simulation tests (``tests/unit/test_roomiq_engine.cpp``) —
  no second implementation that can drift.
* Honesty: stale or missing sensor data is never interpreted as a real
  value; the RoomIQ module runtime status (Initialising / Available /
  Degraded / Unavailable) comes from real value-update freshness signals
  only; the unresolved light-sensor identity (catalog LTR-303ALS vs
  compiled VEML7700) is surfaced, never papered over.
* Backwards compatibility: every pre-framework customer entity id keeps
  existing (disabled by default, engine-driven); nothing is silently
  removed or renamed.
* Firmware-build / simulation proof only — no hardware, bench, medical,
  compliance or commercial claim anywhere. No release declaration changes.

Uses Python's stdlib unittest (repo convention). Run with::

    python3 tests/test_roomiq_framework.py
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any, Dict, List

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

FRAMEWORK_PACKAGE = REPO_ROOT / "packages" / "features" / "roomiq_framework.yaml"
LEGACY_PROFILE = REPO_ROOT / "packages" / "features" / "comfort_basic_profile.yaml"
CLIMATE_BOARD = REPO_ROOT / "packages" / "boards" / "s360-200-roomiq-climate.yaml"
LED_FRAMEWORK = REPO_ROOT / "packages" / "features" / "led_framework.yaml"
HEADER = REPO_ROOT / "include" / "sense360" / "roomiq_engine.h"
LED_HEADER = REPO_ROOT / "include" / "sense360" / "led_controller.h"
CPP_TEST = REPO_ROOT / "tests" / "unit" / "test_roomiq_engine.cpp"
DOC = REPO_ROOT / "docs" / "architecture" / "sense360-roomiq-framework.md"
CHECKLIST = REPO_ROOT / "docs" / "hardware" / "roomiq-framework-bench-checklist.md"
COMPILE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "core-framework-compile.yml"
VALIDATE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "validate.yml"
CONTRACT = REPO_ROOT / "config" / "core-framework.json"
MATRIX = REPO_ROOT / "config" / "feature-entity-matrix.json"
ROADMAP = REPO_ROOT / "docs" / "sense360-roadmap-status.md"
BUNDLES_DIR = REPO_ROOT / "products" / "bundles"

FRAMEWORK_INCLUDE = "!include ../../packages/features/roomiq_framework.yaml"
LEGACY_PROFILE_INCLUDES = (
    "comfort_basic_profile.yaml",
    "roomiq_profile.yaml",
)

# Customer state vocabularies — single-sourced in the engine header.
COMFORT_STRINGS = (
    "Initialising",
    "Comfortable",
    "Cool",
    "Cold",
    "Warm",
    "Hot",
    "Dry",
    "Humid",
    "Warm and humid",
    "Unavailable",
)
BRIGHTNESS_STRINGS = (
    "Initialising",
    "Dark",
    "Dim",
    "Normal",
    "Bright",
    "Very bright",
    "Unavailable",
)
HEALTH_STRINGS = ("Initialising", "Available", "Degraded", "Unavailable", "Fault")

# Raw sensor part numbers / technical jargon that must never appear in a
# customer entity name (they belong in diagnostics and documentation only).
FORBIDDEN_CUSTOMER_NAME_TOKENS = (
    "veml7700",
    "ltr-303",
    "ltr303",
    "sht4x",
    "sht4",
    "raw",
    "filtered",
    "framework",
    "component",
    "bus",
    "i2c",
    "timestamp",
    "gpio",
)

ENTITY_PLATFORM_KEYS = (
    "sensor",
    "binary_sensor",
    "text_sensor",
    "switch",
    "number",
    "button",
    "select",
    "light",
)

# Legacy pre-framework customer entities (published by comfort_basic_profile
# in every RoomIQ composition). Ids and names must keep existing so no
# Home Assistant entity id ever breaks; they become disabled-by-default
# compatibility entities driven by the calibrated canonical outputs.
LEGACY_COMPAT_ENTITIES = {
    "comfort_temperature_display": "${friendly_name} RoomIQ Temperature",
    "comfort_humidity_display": "${friendly_name} RoomIQ Humidity",
    "comfort_light_display": "${friendly_name} RoomIQ Light Level",
    "comfort_feels_like": "${friendly_name} RoomIQ Feels Like",
    "comfort_score_display": "${friendly_name} RoomIQ Comfort Score",
    "comfort_status": "${friendly_name} Comfort Status",
    "comfort_light_status": "${friendly_name} Light Status",
    "comfort_temp_advice": "${friendly_name} Temperature Advice",
    "comfort_humidity_advice": "${friendly_name} Humidity Advice",
}


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


def roomiq_bundles() -> List[Path]:
    """Bundle files whose contract entry declares the roomiq capability."""
    contract = json.loads(CONTRACT.read_text())
    paths = []
    for entry in contract.get("configs", {}).values():
        if "roomiq" in (entry.get("capabilities") or []):
            paths.append(REPO_ROOT / entry["bundle"])
    return sorted(paths)


def non_roomiq_bundles() -> List[Path]:
    contract = json.loads(CONTRACT.read_text())
    paths = []
    for entry in contract.get("configs", {}).values():
        if "roomiq" not in (entry.get("capabilities") or []):
            paths.append(REPO_ROOT / entry["bundle"])
    return sorted(paths)


# --- Package existence -------------------------------------------------------


class PackageFilesExistTests(unittest.TestCase):
    def test_new_files_exist(self) -> None:
        for path in (
            FRAMEWORK_PACKAGE,
            HEADER,
            CPP_TEST,
            DOC,
            CHECKLIST,
        ):
            self.assertTrue(
                path.is_file(), f"missing ROOMIQ-FRAMEWORK-001 file: {path}"
            )

    def test_no_secret_material_in_roomiq_packages(self) -> None:
        for path in (FRAMEWORK_PACKAGE, CLIMATE_BOARD):
            if not path.is_file():
                continue
            raw = path.read_text().lower()
            self.assertNotIn("!secret", raw, path.name)
            for needle in ("password", "api_encryption", "token"):
                self.assertNotIn(needle, raw, path.name)


# --- Customer entity contract --------------------------------------------------


class CustomerEntityContractTests(unittest.TestCase):
    """The default-enabled customer surface is exactly the accepted set."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = load_yaml(FRAMEWORK_PACKAGE) if FRAMEWORK_PACKAGE.is_file() else {}
        cls.raw = FRAMEWORK_PACKAGE.read_text() if FRAMEWORK_PACKAGE.is_file() else ""
        cls.entities = entities_by_id(cls.doc)

    def _entity(self, entity_id: str) -> Dict[str, Any]:
        self.assertIn(entity_id, self.entities, f"missing entity id {entity_id}")
        return self.entities[entity_id]

    def test_canonical_temperature(self) -> None:
        entity = self._entity("s360_temperature")
        self.assertEqual(entity["_platform"], "sensor")
        self.assertEqual(entity.get("name"), "Temperature")
        self.assertEqual(entity.get("unit_of_measurement"), "°C")
        self.assertEqual(entity.get("device_class"), "temperature")
        self.assertEqual(entity.get("state_class"), "measurement")
        self.assertFalse(entity.get("disabled_by_default", False))
        self.assertNotEqual(entity.get("internal"), True)
        self.assertNotIn("entity_category", entity)

    def test_canonical_humidity(self) -> None:
        entity = self._entity("s360_humidity")
        self.assertEqual(entity["_platform"], "sensor")
        self.assertEqual(entity.get("name"), "Humidity")
        self.assertEqual(entity.get("unit_of_measurement"), "%")
        self.assertEqual(entity.get("device_class"), "humidity")
        self.assertEqual(entity.get("state_class"), "measurement")
        self.assertFalse(entity.get("disabled_by_default", False))

    def test_canonical_illuminance(self) -> None:
        entity = self._entity("s360_illuminance")
        self.assertEqual(entity["_platform"], "sensor")
        # Customer wording is "Illuminance" — never an unverified sensor
        # model name (the LTR-303ALS-vs-VEML7700 identity is unresolved).
        self.assertEqual(entity.get("name"), "Illuminance")
        self.assertEqual(entity.get("unit_of_measurement"), "lx")
        self.assertEqual(entity.get("device_class"), "illuminance")
        self.assertEqual(entity.get("state_class"), "measurement")
        self.assertFalse(entity.get("disabled_by_default", False))

    def test_comfort_text_sensor(self) -> None:
        entity = self._entity("s360_comfort")
        self.assertEqual(entity["_platform"], "text_sensor")
        self.assertEqual(entity.get("name"), "Comfort")
        self.assertFalse(entity.get("disabled_by_default", False))
        self.assertNotIn("entity_category", entity)

    def test_environment_state_text_sensor(self) -> None:
        entity = self._entity("s360_environment_state")
        self.assertEqual(entity["_platform"], "text_sensor")
        self.assertEqual(entity.get("name"), "Environment State")
        self.assertFalse(entity.get("disabled_by_default", False))

    def test_brightness_text_sensor(self) -> None:
        entity = self._entity("s360_brightness")
        self.assertEqual(entity["_platform"], "text_sensor")
        self.assertEqual(entity.get("name"), "Brightness")
        self.assertFalse(entity.get("disabled_by_default", False))

    def test_temperature_offset_control(self) -> None:
        entity = self._entity("s360_temperature_offset")
        self.assertEqual(entity["_platform"], "number")
        self.assertEqual(entity.get("name"), "Temperature Offset")
        self.assertEqual(entity.get("entity_category"), "config")
        self.assertEqual(entity.get("unit_of_measurement"), "°C")
        self.assertEqual(float(entity.get("min_value")), -5.0)
        self.assertEqual(float(entity.get("max_value")), 5.0)
        self.assertEqual(float(entity.get("initial_value")), 0.0)
        self.assertTrue(entity.get("restore_value"))
        self.assertFalse(entity.get("disabled_by_default", False))

    def test_humidity_offset_control(self) -> None:
        entity = self._entity("s360_humidity_offset")
        self.assertEqual(entity["_platform"], "number")
        self.assertEqual(entity.get("name"), "Humidity Offset")
        self.assertEqual(entity.get("entity_category"), "config")
        self.assertEqual(entity.get("unit_of_measurement"), "%")
        self.assertEqual(float(entity.get("min_value")), -10.0)
        self.assertEqual(float(entity.get("max_value")), 10.0)
        self.assertEqual(float(entity.get("initial_value")), 0.0)
        self.assertTrue(entity.get("restore_value"))

    def test_illuminance_calibration_control(self) -> None:
        # A multiplier, not an offset: ambient-light error is dominated by
        # multiplicative effects (gain, diffuser attenuation, mounting), so
        # a scale factor is the least misleading calibration model.
        entity = self._entity("s360_illuminance_scale")
        self.assertEqual(entity["_platform"], "number")
        self.assertEqual(entity.get("name"), "Illuminance Calibration")
        self.assertEqual(entity.get("entity_category"), "config")
        self.assertEqual(float(entity.get("min_value")), 0.2)
        self.assertEqual(float(entity.get("max_value")), 5.0)
        self.assertEqual(float(entity.get("initial_value")), 1.0)
        self.assertTrue(entity.get("restore_value"))

    def test_no_customer_numeric_comfort_score(self) -> None:
        # Accepted owner decision: human-friendly comfort states, never a
        # default customer-facing 0-100 score. The legacy score entity stays
        # for compatibility but is disabled by default (tested below).
        for entity_id, entity in self.entities.items():
            name = str(entity.get("name", "")).lower()
            if "score" in name:
                self.assertTrue(
                    entity.get("disabled_by_default"),
                    f"{entity_id}: a numeric comfort score must never be "
                    "enabled by default",
                )

    def test_no_raw_model_names_or_jargon_in_customer_entities(self) -> None:
        for entity_id, entity in self.entities.items():
            if entity.get("disabled_by_default") or entity.get("internal"):
                continue
            name = str(entity.get("name", "")).lower()
            for forbidden in FORBIDDEN_CUSTOMER_NAME_TOKENS:
                self.assertNotIn(
                    forbidden,
                    name,
                    f"{entity_id}: customer entity name {name!r} contains "
                    f"technical token {forbidden!r}",
                )

    def test_default_enabled_customer_set_is_exact(self) -> None:
        expected = {
            "s360_temperature",
            "s360_humidity",
            "s360_illuminance",
            "s360_comfort",
            "s360_environment_state",
            "s360_brightness",
            "s360_temperature_offset",
            "s360_humidity_offset",
            "s360_illuminance_scale",
        }
        enabled = {
            entity_id
            for entity_id, entity in self.entities.items()
            if not entity.get("disabled_by_default", False)
            and not entity.get("internal", False)
        }
        self.assertEqual(
            enabled,
            expected,
            "default-enabled RoomIQ surface must be exactly the accepted "
            "customer set",
        )

    def test_diagnostics_are_diagnostic_and_disabled(self) -> None:
        for entity_id, entity in self.entities.items():
            if entity.get("internal", False):
                continue
            category = entity.get("entity_category")
            if category == "diagnostic":
                self.assertTrue(
                    entity.get("disabled_by_default"),
                    f"{entity_id}: diagnostic entities ship disabled by "
                    "default",
                )

    def test_raw_sensor_diagnostics_exist(self) -> None:
        # Raw (uncalibrated) readings stay available for support work —
        # diagnostic and disabled by default, never the customer surface.
        for entity_id in (
            "s360_roomiq_raw_temperature",
            "s360_roomiq_raw_humidity",
            "s360_roomiq_raw_illuminance",
        ):
            entity = self._entity(entity_id)
            self.assertEqual(entity.get("entity_category"), "diagnostic")
            self.assertTrue(entity.get("disabled_by_default"))

    def test_sensor_verification_diagnostic_states_identity_limit(self) -> None:
        # Honesty companion: the light-sensor part identity is unresolved
        # (catalog/BOM: LTR-303ALS-01; compiled firmware: VEML7700). The
        # diagnostic states the limit on-device; customer entities never
        # carry a sensor model name.
        entity = self._entity("s360_roomiq_sensor_verification")
        self.assertEqual(entity.get("entity_category"), "diagnostic")
        self.assertTrue(entity.get("disabled_by_default"))
        value = str(entity.get("lambda", ""))
        self.assertIn("LTR-303", value)
        self.assertIn("VEML7700", value)

    def test_legacy_compat_entities_preserved_and_disabled(self) -> None:
        for entity_id, expected_name in LEGACY_COMPAT_ENTITIES.items():
            entity = self._entity(entity_id)
            self.assertEqual(entity.get("name"), expected_name, entity_id)
            self.assertTrue(
                entity.get("disabled_by_default"),
                f"{entity_id}: legacy compatibility entities are disabled "
                "by default (the canonical surface replaces them)",
            )

    def test_legacy_numeric_compat_entities_receive_calibrated_values(self) -> None:
        # No double calibration: the legacy display entities copy the
        # calibrated canonical sensors (calibration applied exactly once,
        # inside the engine).
        for entity_id, source in (
            ("comfort_temperature_display", "s360_temperature"),
            ("comfort_humidity_display", "s360_humidity"),
            ("comfort_light_display", "s360_illuminance"),
        ):
            entity = self._entity(entity_id)
            self.assertEqual(entity.get("platform"), "copy", entity_id)
            self.assertEqual(entity.get("source_id"), source, entity_id)

    def test_framework_uses_the_shared_header(self) -> None:
        self.assertIn("include/sense360/roomiq_engine.h", self.raw)

    def test_freshness_comes_from_update_callbacks(self) -> None:
        # Freshness must come from real sensor update callbacks, never from
        # re-reading a cached value.
        self.assertIn("on_value", self.raw)
        for hook in ("input_temperature", "input_humidity", "input_lux"):
            self.assertIn(hook, self.raw, hook)

    def test_module_status_driven_with_reserved_vocabulary(self) -> None:
        # The framework drives the Core-Framework RoomIQ module status
        # entity with the reserved runtime vocabulary from real freshness
        # signals (the second wired module after Presence).
        self.assertIn("s360_module_status_roomiq", self.raw)
        self.assertIn("health_to_string", self.raw)

    def test_no_fabricated_fault_producer(self) -> None:
        # Fault is an engine contract with no production producer: no
        # composed component exposes a supported explicit fault signal.
        self.assertNotIn("set_fault(true)", self.raw)

    def test_calibration_values_are_not_applied_twice(self) -> None:
        # The engine owns calibration. The YAML must not add offset/multiply
        # filters on the canonical or legacy entities (that would calibrate
        # twice).
        doc = self.doc
        for platform in ("sensor",):
            for entry in doc.get(platform) or []:
                if not isinstance(entry, dict):
                    continue
                filters = entry.get("filters") or []
                for f in filters:
                    if isinstance(f, dict):
                        self.assertNotIn("offset", f, entry.get("id"))
                        self.assertNotIn("multiply", f, entry.get("id"))
                        self.assertNotIn("calibrate_linear", f, entry.get("id"))


# --- Board package: raw sensors stay raw, legacy engine moves out ---------------


class BoardPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = load_yaml(CLIMATE_BOARD)
        cls.raw = CLIMATE_BOARD.read_text()
        cls.entities = entities_by_id(cls.doc)

    def test_raw_sensors_unchanged_and_internal(self) -> None:
        # Firmware behaviour gate: the unresolved sensor-identity conflict
        # (catalog LTR-303ALS vs compiled VEML7700) means the compiled
        # sensor set must NOT change in this work item.
        for entity_id in (
            "comfort_ceiling_veml7700",
            "comfort_ceiling_sht4x",
        ):
            self.assertIn(entity_id, self.entities, entity_id)
        for entity_id in (
            "comfort_ceiling_illuminance",
            "comfort_ceiling_temperature",
            "comfort_ceiling_humidity",
        ):
            self.assertTrue(
                self.entities[entity_id].get("internal"),
                f"{entity_id}: raw board sensors stay internal",
            )
        self.assertIn("address: 0x10", self.raw)
        self.assertIn("address: 0x44", self.raw)

    def test_no_raw_calibration_filters(self) -> None:
        # Calibration lives in the engine only — never on the raw sensors
        # (that would double-apply offsets).
        self.assertNotIn("calibrate_linear", self.raw)
        self.assertNotIn("- offset:", self.raw)
        self.assertNotIn("- multiply:", self.raw)

    def test_legacy_comfort_engine_moved_out_of_board_layer(self) -> None:
        # The pre-framework comfort/dew-point/heat-index/light-level
        # calculation moves to the legacy profile so that framework-bearing
        # bundles compile exactly ONE environmental engine (no duplicate
        # threshold logic), while legacy include paths keep resolving to the
        # identical behaviour.
        for legacy_global in (
            "comfort_ceiling_index_value",
            "comfort_ceiling_dew_point",
            "comfort_ceiling_heat_index",
            "comfort_ceiling_light_level",
        ):
            self.assertNotIn(legacy_global, self.raw, legacy_global)
        legacy_profile_raw = LEGACY_PROFILE.read_text()
        for legacy_global in (
            "comfort_ceiling_index_value",
            "comfort_ceiling_heat_index",
            "comfort_ceiling_light_level",
        ):
            self.assertIn(legacy_global, legacy_profile_raw, legacy_global)


# --- Engine header / simulation layer -----------------------------------------


class EngineHeaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = HEADER.read_text() if HEADER.is_file() else ""

    def test_header_exists(self) -> None:
        self.assertTrue(HEADER.is_file(), f"missing {HEADER}")

    def test_namespace_and_engine(self) -> None:
        self.assertIn("namespace sense360", self.raw)
        self.assertIn("namespace roomiq", self.raw)
        self.assertIn("class RoomIQEngine", self.raw)

    def test_state_strings_are_single_sourced(self) -> None:
        for value in set(COMFORT_STRINGS) | set(BRIGHTNESS_STRINGS) | set(
            HEALTH_STRINGS
        ):
            self.assertIn(f'"{value}"', self.raw, value)

    def test_darkness_service_lives_in_the_roomiq_engine(self) -> None:
        # The canonical darkness decision (threshold, hysteresis, staleness)
        # is a RoomIQ service consumed by LED — one implementation.
        for needle in (
            "set_darkness_threshold",
            "set_darkness_hysteresis",
            "darkness()",
        ):
            self.assertIn(needle, self.raw, needle)

    def test_no_hardware_validation_claim(self) -> None:
        lowered = self.raw.lower()
        self.assertIn("provisional", lowered)
        self.assertNotIn("hardware verified", lowered)
        self.assertNotIn("bench verified", lowered)
        self.assertNotIn("medical", lowered)

    def test_simulation_tests_exist(self) -> None:
        self.assertTrue(CPP_TEST.is_file(), f"missing {CPP_TEST}")
        cpp = CPP_TEST.read_text()
        self.assertIn("roomiq_engine.h", cpp)


# --- LED integration: canonical outputs, no duplicate darkness engine ----------


class LedIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.led_raw = LED_FRAMEWORK.read_text()
        cls.led_header_raw = LED_HEADER.read_text()

    def test_led_consumes_canonical_darkness(self) -> None:
        self.assertIn("sense360::roomiq", self.led_raw)
        self.assertIn("input_darkness", self.led_raw)

    def test_led_does_not_read_raw_lux(self) -> None:
        # LED must consume the canonical RoomIQ outputs, never the raw
        # board sensor.
        self.assertNotIn("comfort_ceiling_illuminance", self.led_raw)

    def test_led_controller_has_no_duplicate_lux_engine(self) -> None:
        # Regression guard: exactly one lux-threshold implementation exists
        # (the RoomIQ engine). The LED controller consumes the decision.
        self.assertNotIn("input_lux", self.led_header_raw)
        self.assertIn("input_darkness", self.led_header_raw)

    def test_led_keeps_its_customer_threshold_control(self) -> None:
        # The Darkness Threshold number stays an LED customer control (its
        # id and semantics are published); LED passes the value into the
        # RoomIQ darkness service at runtime.
        doc = load_yaml(LED_FRAMEWORK)
        entities = entities_by_id(doc)
        self.assertIn("s360_led_darkness_threshold", entities)
        self.assertIn("set_darkness_threshold", self.led_raw)


# --- Bundle wiring --------------------------------------------------------------


class BundleWiringTests(unittest.TestCase):
    def test_roomiq_bundle_authority_is_the_contract(self) -> None:
        # Every catalog-declared RoomIQ-bearing config (and only those)
        # composes the framework.
        bundles = roomiq_bundles()
        self.assertGreaterEqual(len(bundles), 10)
        for bundle in bundles:
            raw = bundle.read_text()
            self.assertIn(FRAMEWORK_INCLUDE, raw, bundle.name)

    def test_roomiq_bundles_drop_the_legacy_profile(self) -> None:
        # The framework supersedes the legacy display profile in bundles —
        # composing both would duplicate entities and calibrate twice.
        for bundle in roomiq_bundles():
            raw = bundle.read_text()
            for legacy in LEGACY_PROFILE_INCLUDES:
                self.assertNotIn(legacy, raw, bundle.name)

    def test_non_roomiq_bundles_gain_nothing(self) -> None:
        for bundle in non_roomiq_bundles():
            raw = bundle.read_text()
            self.assertNotIn("roomiq_framework.yaml", raw, bundle.name)
            self.assertNotIn("s360-200-roomiq", raw, bundle.name)

    def test_roomiq_bundles_keep_the_board_and_presence_composition(self) -> None:
        # Presence and LED compositions keep working: the framework changes
        # the display/service layer only, never the board or Presence
        # wiring.
        for bundle in roomiq_bundles():
            raw = bundle.read_text()
            self.assertIn("s360-200-roomiq.yaml", raw, bundle.name)
            self.assertIn("presence_framework.yaml", raw, bundle.name)

    def test_legacy_include_paths_still_resolve(self) -> None:
        # Customers pin these paths at release tags; they must keep
        # existing and resolving.
        for rel in (
            "packages/features/comfort_basic_profile.yaml",
            "packages/features/roomiq_profile.yaml",
            "packages/expansions/comfort_ceiling.yaml",
        ):
            self.assertTrue((REPO_ROOT / rel).is_file(), rel)


# --- Core framework contract ------------------------------------------------------


class CoreFrameworkContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text())

    def test_roomiq_capability_names_the_framework(self) -> None:
        description = self.contract["capabilities"]["roomiq"]["description"]
        self.assertIn("ROOMIQ-FRAMEWORK-001", description)

    def test_roomiq_module_runtime_status_declared(self) -> None:
        runtime = self.contract.get("module_runtime_status") or {}
        self.assertIn("roomiq", runtime, "RoomIQ is the second wired module")
        entry = runtime["roomiq"]
        self.assertEqual(entry.get("entity_id"), "s360_module_status_roomiq")
        self.assertEqual(
            entry.get("package"), "packages/features/roomiq_framework.yaml"
        )
        self.assertEqual(entry.get("work_item"), "ROOMIQ-FRAMEWORK-001")
        self.assertEqual(
            entry.get("values"),
            ["Initialising", "Available", "Degraded", "Unavailable", "Fault"],
        )
        # Available must be defined strictly from real freshness signals.
        definition = str(entry.get("available_definition", "")).lower()
        self.assertIn("fresh", definition)
        for forbidden in ("bench", "hardware proof"):
            self.assertNotIn(forbidden + " verified", definition)

    def test_presence_runtime_status_unchanged(self) -> None:
        runtime = self.contract.get("module_runtime_status") or {}
        self.assertIn("presence", runtime)
        self.assertEqual(
            runtime["presence"].get("work_item"), "PRESENCE-FRAMEWORK-001"
        )


# --- Compile lane / CI wiring ------------------------------------------------------


class CompileLaneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = COMPILE_WORKFLOW.read_text()
        cls.doc = yaml.safe_load(cls.raw)

    def _matrix_configs(self) -> Dict[str, str]:
        jobs = self.doc.get("jobs") or {}
        for job in jobs.values():
            include = ((job.get("strategy") or {}).get("matrix") or {}).get("include")
            if include:
                return {row["config_string"]: row["product_yaml"] for row in include}
        return {}

    def test_matrix_covers_the_required_roomiq_compositions(self) -> None:
        configs = self._matrix_configs()
        for required in (
            "Ceiling-POE-RoomIQ",
            "Ceiling-USB-RoomIQ",
            "Ceiling-POE-AirIQ-RoomIQ",
            "Ceiling-POE-VentIQ-RoomIQ",
            "Ceiling-POE-VentIQ-RoomIQ-LED",
            "Ceiling-POE-RoomIQ-LED",
        ):
            self.assertIn(required, configs, required)

    def test_matrix_includes_a_non_roomiq_regression_target(self) -> None:
        # A framework-bearing non-RoomIQ product compiles as the regression
        # proof that non-RoomIQ products gain no RoomIQ entities.
        configs = self._matrix_configs()
        self.assertEqual(
            configs.get("Ceiling-POE-FanDAC"),
            "products/sense360-ceiling-poe-fandac.yaml",
        )

    def test_contract_gate_runs_roomiq_tests(self) -> None:
        self.assertIn("tests/test_roomiq_framework.py", self.raw)
        self.assertIn("make -C tests test", self.raw)

    def test_paths_cover_roomiq_framework_surfaces(self) -> None:
        triggers = self.doc.get("on", self.doc.get(True)) or {}
        paths = (triggers.get("pull_request") or {}).get("paths") or []
        for needed in (
            "packages/boards/**",
            "packages/features/**",
            "include/sense360/**",
            "tests/unit/**",
            "tests/test_roomiq_framework.py",
        ):
            self.assertIn(needed, paths)

    def test_lane_guarantees_unchanged(self) -> None:
        triggers = self.doc.get("on", self.doc.get(True)) or {}
        self.assertEqual(set(triggers), {"pull_request", "workflow_dispatch"})
        self.assertEqual(self.doc.get("permissions"), {"contents": "read"})
        self.assertNotIn("upload-artifact", self.raw)

    def test_quick_validation_gate_runs_roomiq_contract(self) -> None:
        self.assertIn(
            "tests/test_roomiq_framework.py", VALIDATE_WORKFLOW.read_text()
        )


# --- Feature-entity matrix -----------------------------------------------------


class FeatureEntityMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        matrix = json.loads(MATRIX.read_text())
        cls.board = next(b for b in matrix["boards"] if b["sku"] == "S360-200")

    def test_comfort_indices_row_points_at_the_framework(self) -> None:
        rows = [
            r for r in self.board["rows"] if "Comfort indices" in r["row"]
        ]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["status"], "present")
        self.assertIn("s360_comfort", str(row["present_as"]))
        self.assertIn("roomiq_framework.yaml", str(row["defined_in"]))


# --- Documentation ------------------------------------------------------------------


class DocumentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = DOC.read_text() if DOC.is_file() else ""
        cls.lowered = cls.text.lower()
        cls.normalised = " ".join(cls.lowered.split())

    def test_doc_exists_and_names_the_work_item(self) -> None:
        self.assertTrue(DOC.is_file(), f"missing {DOC}")
        self.assertIn("ROOMIQ-FRAMEWORK-001", self.text)

    def test_customer_contract_documented(self) -> None:
        for name in (
            "Temperature",
            "Humidity",
            "Illuminance",
            "Comfort",
            "Environment State",
            "Brightness",
            "Temperature Offset",
            "Humidity Offset",
            "Illuminance Calibration",
        ):
            self.assertIn(name, self.text, name)

    def test_state_vocabularies_documented(self) -> None:
        for value in COMFORT_STRINGS + BRIGHTNESS_STRINGS:
            self.assertIn(value, self.text, value)

    def test_thresholds_documented_as_provisional_heuristics(self) -> None:
        self.assertIn("provisional", self.normalised)
        self.assertIn("comfort heuristic", self.normalised)
        self.assertIn("physical validation pending", self.normalised)

    def test_no_forbidden_claims(self) -> None:
        for forbidden in (
            "medical",
            "mould prevention",
            "mold prevention",
            "condensation prevention",
            "hardware verified",
            "bench verified",
            "lighting-standard compliance",
        ):
            self.assertNotIn(forbidden, self.normalised, forbidden)

    def test_sensor_identity_conflict_reported(self) -> None:
        # Designed hardware (schematic/BOM): LTR-303ALS-01. Compiled
        # firmware: VEML7700 at 0x10. Runtime identity unresolved until the
        # bench checklist runs — the doc must state all layers.
        self.assertIn("LTR-303", self.text)
        self.assertIn("VEML7700", self.text)
        self.assertIn("0x10", self.text)

    def test_internal_reuse_contract_documented(self) -> None:
        for needle in (
            "s360_temperature",
            "s360_humidity",
            "s360_illuminance",
            "darkness",
            "VentIQ",
            "AirIQ",
        ):
            self.assertIn(needle, self.text, needle)

    def test_calibration_model_documented(self) -> None:
        self.assertIn("calibration", self.lowered)
        self.assertIn("once", self.lowered)
        self.assertIn("restart", self.lowered)

    def test_led_migration_documented(self) -> None:
        self.assertIn("led", self.lowered)
        self.assertIn("darkness", self.lowered)


class BenchChecklistTests(unittest.TestCase):
    def test_checklist_prepared_without_results(self) -> None:
        self.assertTrue(CHECKLIST.is_file(), f"missing {CHECKLIST}")
        text = CHECKLIST.read_text()
        lowered = text.lower()
        for topic in (
            "temperature",
            "humidity",
            "illuminance",
            "sensor identity",
            "reference",
            "update interval",
            "stale",
            "calibration",
            "response time",
            "brightness",
            "hysteresis",
            "led",
            "comfort threshold",
            "warm",
            "disconnect",
            "recovery",
            "reboot",
            "home assistant",
        ):
            self.assertIn(topic, lowered, topic)
        # Prepared, not executed: unchecked boxes only, no results, no
        # machine-written attestation (standing rule).
        self.assertIn("[ ]", text)
        self.assertNotIn("[x]", lowered)
        self.assertIn("no results", lowered)


class RoadmapTests(unittest.TestCase):
    def test_roadmap_records_roomiq_framework(self) -> None:
        text = ROADMAP.read_text()
        self.assertIn("ROOMIQ-FRAMEWORK-001", text)
        section = text[text.index("ROOMIQ-FRAMEWORK-001") :][:9000]
        lowered = section.lower()
        self.assertIn("software foundation", lowered)
        self.assertIn("pending", lowered)
        self.assertIn("SOT", section)
        self.assertIn("ROOMIQ-FRAMEWORK-BENCH-001", section)
        # The unresolved sensor-identity reconciliation stays tracked.
        self.assertIn("LTR-303", section)


if __name__ == "__main__":
    unittest.main(verbosity=2)

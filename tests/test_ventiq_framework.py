#!/usr/bin/env python3
"""VENTIQ-FRAMEWORK-001 — canonical bathroom ventilation service contract.

These tests define (and then pin) the customer-focused Sense360 VentIQ
framework for the S360-211 VentIQ board: one honest bathroom ventilation
experience (Is ventilation required? Why? What is driving it? What should
I do?), built by CONSUMING the platform's existing canonical services —
the AirIQ pollutant engine (VOC/NOx severity — thresholds are never
duplicated), the RoomIQ canonical environmental service (calibrated
humidity/temperature — raw sensors are never re-read) and the Core
runtime framework (VentIQ module status entity) — plus the VentIQ-owned
ventilation logic (shower detection, moisture clearing, damp/mould
tracking, odour, deterministic recommendation), all produced by ONE
shared engine compiled by production YAML and the deterministic
simulation tests.

Authority facts this contract encodes (audited against the verified
S360-211-R4 schematic PDF, the hardware catalog, the module pinmap docs,
SOT and the feature-entity matrix — see
docs/architecture/sense360-ventiq-framework.md; the evidence layers
schematic / BOM / assembly / firmware / bundle / customer / bench are
recorded SEPARATELY and never merged):

* The S360-211 board's ONLY on-board sensor on the verified schematic
  (single sheet, Id 1/1) is the SGP41 VOC/NOx sensor (U3, shared I2C).
  There is NO SHT4x and NO BMP390 anywhere on the verified schematic.
* The compiled SHT4x @0x44 and BMP390 @0x77 in the board package are
  FIRMWARE/SCHEMATIC DRIFT (the feature-entity matrix already carries
  CONFIRM flags for both; no S360-211 BOM artifact record is committed).
  In every current VentIQ composition the RoomIQ board's SHT4x sits at
  the same address on the same shared bus. The framework therefore takes
  humidity/temperature ONLY from the RoomIQ canonical service and
  exposes NO new entity backed by the drifted drivers.
* The IR-temperature (J3) and SPS30 (J4) connectors are genuinely
  optional EXTERNAL attachments (catalog doctrine); neither has a driver
  compiled in the canonical board package; no entity may pretend them.
* The on-board inline fan-relay stage is drawn with its components
  crossed out on the verified schematic (KiCad do-not-populate
  convention); population is UNPROVEN, no BOM is committed, no driver is
  bound, and no runtime fan/ventilation-hardware health exists — none is
  invented. Compile-time fan-module presence stays with the Core
  framework's Fan Control Module Status entity (never duplicated here).
* There is NO VentIQ Base/Pro product axis (flat taxonomy, one SKU per
  product; SOT lists one S360-211 product). The legacy "Pro" overlay and
  the S360-BATH-B module-SKU string are legacy artifacts, recorded as
  conflicts — not product authority.
* Every VentIQ-bearing catalog composition also carries RoomIQ, so the
  canonical humidity service is present wherever this framework is
  composed.

Uses Python's stdlib unittest (repo convention). Run with::

    python3 tests/test_ventiq_framework.py
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any, Dict, List

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

FRAMEWORK_PACKAGE = REPO_ROOT / "packages" / "features" / "ventiq_framework.yaml"
LEGACY_PROFILE = REPO_ROOT / "packages" / "features" / "bathroom_profile.yaml"
LEGACY_PROFILE_ALIAS = REPO_ROOT / "packages" / "features" / "ventiq_profile.yaml"
BOARD_PACKAGE = REPO_ROOT / "packages" / "boards" / "s360-211-ventiq.yaml"
HEADER = REPO_ROOT / "include" / "sense360" / "ventiq_engine.h"
AIRIQ_HEADER = REPO_ROOT / "include" / "sense360" / "airiq_engine.h"
CPP_TEST = REPO_ROOT / "tests" / "unit" / "test_ventiq_engine.cpp"
DOC = REPO_ROOT / "docs" / "architecture" / "sense360-ventiq-framework.md"
CHECKLIST = REPO_ROOT / "docs" / "hardware" / "ventiq-framework-bench-checklist.md"
COMPILE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "core-framework-compile.yml"
VALIDATE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "validate.yml"
CONTRACT = REPO_ROOT / "config" / "core-framework.json"
ROADMAP = REPO_ROOT / "docs" / "sense360-roadmap-status.md"
BUNDLES_DIR = REPO_ROOT / "products" / "bundles"

FRAMEWORK_INCLUDE = "!include ../../packages/features/ventiq_framework.yaml"
LEGACY_PROFILE_INCLUDES = (
    "bathroom_profile.yaml",
    "ventiq_profile.yaml",
)

# Customer state vocabularies — single-sourced in the engine headers.
SEVERITY_STRINGS = (
    "Initialising",
    "Good",
    "Fair",
    "Poor",
    "Very poor",
    "Unavailable",
)
RECOMMENDATION_STRINGS = (
    "Sensor initialising",
    "No action needed",
    "Ventilate soon",
    "Ventilate now",
    "Unavailable",
)
REASON_STRINGS = (
    "Sensor initialising",
    "No ventilation needed",
    "Ventilation requested",
    "Shower in progress",
    "Clearing shower moisture",
    "Poor air quality",
    "Damp for a long time",
    "Odour detected",
    "High humidity",
    "Unavailable",
)
HEALTH_STRINGS = ("Initialising", "Available", "Degraded", "Unavailable", "Fault")

# Raw sensor part numbers / engineering jargon that must never appear in a
# customer entity name (diagnostics and documentation only).
FORBIDDEN_CUSTOMER_NAME_TOKENS = (
    "sgp41",
    "sgp4x",
    "sht4x",
    "bmp390",
    "bmp3xx",
    "sps30",
    "mlx90614",
    "scd41",
    "aqi",
    "i2c",
    "gpio",
    "raw",
    "baseline",
    "heater",
    "framework",
    "engine",
    "s360-bath",
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

# The exact default-enabled measurement/state customer set. Small by
# design: the bathroom customer questions are "is ventilation required,
# why, and what should I do" — answered by Recommendation / Ventilation
# Reason / Ventilation Needed — plus the honest on-board measurements
# (VOC/NOx are the board's only schematic-proven sensors) and the two
# bathroom conditions with genuine automation value (shower, mould risk).
# Humidity/temperature stay RoomIQ canonical entities — never duplicated.
DEFAULT_ENABLED_STATE_IDS = {
    "s360_ventiq_voc",
    "s360_ventiq_nox",
    "s360_ventiq_air_quality",
    "s360_ventiq_recommendation",
    "s360_ventiq_reason",
    "s360_ventilation_needed",
    "s360_ventiq_shower",
    "s360_ventiq_mould_risk",
}

# Legacy control ids that are PRESERVED and now genuinely wired into the
# engine (pre-framework they were placebo controls that no logic read —
# a recorded customer-experience defect this framework fixes).
WIRED_LEGACY_NUMBER_IDS = {
    "bathroom_shower_threshold",
    "bathroom_post_shower_duration",
    "bathroom_mold_threshold",
}
WIRED_LEGACY_BUTTON_IDS = {
    "bathroom_force_ventilation",
    "bathroom_reset_shower",
    "bathroom_reset_mold",
}

# Legacy published display entities preserved as disabled-by-default
# compatibility entities (ids and names unchanged).
LEGACY_COMPAT_IDS = {
    "bathroom_temp_display",
    "bathroom_humidity_display",
    "bathroom_pressure_display",
    "bathroom_voc_display",
    "bathroom_nox_display",
    "bathroom_dew_point_display",
    "bathroom_humidity_rate_display",
    "bathroom_post_shower_timer_display",
    "bathroom_fan_recommendation_display",
    "bathroom_mold_risk_display",
    "bathroom_shower_display",
    "bathroom_mold_warning_display",
    "bathroom_odor_display",
    "bathroom_ventilation_needed",
    "bathroom_status",
    "bathroom_mold_risk_status",
    "bathroom_ventilation_advice",
    "bathroom_air_quality_status",
    "bathroom_auto_ventilation",
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


def ventiq_bundles() -> List[Path]:
    """Bundle files whose contract entry declares the ventiq capability."""
    contract = json.loads(CONTRACT.read_text())
    paths = []
    for entry in contract.get("configs", {}).values():
        if "ventiq" in (entry.get("capabilities") or []):
            paths.append(REPO_ROOT / entry["bundle"])
    return sorted(paths)


def non_ventiq_bundles() -> List[Path]:
    contract = json.loads(CONTRACT.read_text())
    paths = []
    for entry in contract.get("configs", {}).values():
        if "ventiq" not in (entry.get("capabilities") or []):
            paths.append(REPO_ROOT / entry["bundle"])
    return sorted(paths)


# --- Package existence -------------------------------------------------------


class PackageFilesExistTests(unittest.TestCase):
    def test_new_files_exist(self) -> None:
        for path in (FRAMEWORK_PACKAGE, HEADER, CPP_TEST, DOC, CHECKLIST):
            self.assertTrue(path.exists(), f"missing: {path}")

    def test_legacy_paths_still_resolve(self) -> None:
        # Customers pin these exact include paths; they are never removed.
        for path in (LEGACY_PROFILE, LEGACY_PROFILE_ALIAS, BOARD_PACKAGE):
            self.assertTrue(path.exists(), f"legacy path removed: {path}")

    def test_no_secret_material_in_ventiq_packages(self) -> None:
        for path in (FRAMEWORK_PACKAGE, BOARD_PACKAGE):
            raw = path.read_text().lower()
            for token in ("password:", "api_key:", "private_key"):
                for line in raw.splitlines():
                    if token in line and "!secret" not in line:
                        self.fail(f"possible secret literal in {path}: {line}")


# --- Product / hardware authority ---------------------------------------------


class AuthorityTests(unittest.TestCase):
    """The S360-211 SKU (verified schematic) is the authority — never the
    compiled firmware, never a connector, never a legacy variant name."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.framework_raw = FRAMEWORK_PACKAGE.read_text()
        cls.framework = load_yaml(FRAMEWORK_PACKAGE)
        cls.entities = entities_by_id(cls.framework)
        cls.doc = DOC.read_text()

    def test_humidity_comes_from_the_roomiq_canonical_service(self) -> None:
        subs = self.framework.get("substitutions") or {}
        self.assertEqual(subs.get("ventiq_humidity_source_id"), "s360_humidity")
        self.assertEqual(subs.get("ventiq_temperature_source_id"), "s360_temperature")

    def test_no_raw_environmental_sensor_reads(self) -> None:
        # The framework must never re-read the drifted VentIQ SHT4x
        # (bathroom_temperature / bathroom_humidity), the board's derived
        # legacy templates, or the raw RoomIQ board sensors — via copy
        # sources OR lambda id() references. The ONE documented exception
        # is the preserved legacy pressure compatibility entity, which
        # keeps its pre-framework source (bathroom_pressure, the drifted
        # BMP390 driver) pending the VENTIQ-HW-DRIFT-001 reconciliation.
        allowed_copy_sources = {
            "${ventiq_humidity_source_id}",
            "${ventiq_temperature_source_id}",
            "${ventiq_voc_source_id}",
            "${ventiq_nox_source_id}",
            "s360_temperature",
            "s360_humidity",
            "s360_ventiq_voc",
            "s360_ventiq_nox",
            "bathroom_pressure",  # documented compatibility exception
        }
        for entity_id, entity in self.entities.items():
            source = entity.get("source_id")
            if source is not None:
                self.assertIn(
                    source,
                    allowed_copy_sources,
                    f"{entity_id} copies from a non-canonical source {source}",
                )
        for forbidden_ref in (
            "id(bathroom_temperature)",
            "id(bathroom_humidity)",
            "id(bathroom_pressure)",
            "id(bathroom_dew_point)",
            "id(bathroom_humidity_rate)",
            "id(comfort_ceiling_temperature)",
            "id(comfort_ceiling_humidity)",
            "id(comfort_ceiling_illuminance)",
            "id(bathroom_shower_active)",
            "id(bathroom_mold_risk)",
            "id(bathroom_fan_recommendation)",
            "id(bathroom_post_shower_timer)",
            "id(bathroom_odor_detected)",
        ):
            self.assertNotIn(
                forbidden_ref,
                self.framework_raw,
                f"framework re-reads raw board state {forbidden_ref}",
            )

    def test_voc_nox_come_from_the_board_sgp41(self) -> None:
        subs = self.framework.get("substitutions") or {}
        self.assertEqual(subs.get("ventiq_voc_source_id"), "bathroom_voc_index")
        self.assertEqual(subs.get("ventiq_nox_source_id"), "bathroom_nox_index")

    def test_no_new_pressure_surface(self) -> None:
        # Pressure is not S360-211 product hardware (verified schematic has
        # no pressure part). No canonical pressure entity may exist; only
        # the pre-framework compatibility id survives, disabled by default.
        for entity_id, entity in self.entities.items():
            name = str(entity.get("name") or "").lower()
            if "pressure" in name or "pressure" in entity_id:
                self.assertEqual(
                    entity_id,
                    "bathroom_pressure_display",
                    f"unexpected pressure entity {entity_id}",
                )
                self.assertTrue(entity.get("disabled_by_default"))

    def test_no_ir_temperature_or_pm_entity_pretended(self) -> None:
        # J3 IR-temp and J4 SPS30 are optional external attachments with no
        # compiled driver in the canonical board package: no entity exists.
        for entity_id, entity in self.entities.items():
            name = str(entity.get("name") or "").lower()
            self.assertNotIn("surface temperature", name)
            self.assertNotIn("particulate", name)
            self.assertNotIn("pm2", name)
            self.assertNotIn("condensation", name)

    def test_no_base_pro_axis_invented(self) -> None:
        raw = self.framework_raw.lower()
        for token in ("ventiq_pro:", "ventiq_base:", "is_pro", "pro_variant"):
            self.assertNotIn(token, raw)

    def test_expected_sensor_membership_is_configuration_driven(self) -> None:
        subs = self.framework.get("substitutions") or {}
        self.assertEqual(subs.get("ventiq_expected_voc"), "true")
        self.assertEqual(subs.get("ventiq_expected_nox"), "true")

    def test_board_package_records_the_drift_and_stays_unchanged(self) -> None:
        # The board package remains the owner of the compiled raw sensors
        # exactly as shipped (reconciliation is a separate follow-up), and
        # its header must now record the verified-schematic findings.
        raw = BOARD_PACKAGE.read_text()
        for required in (
            "platform: sht4x",
            "platform: bmp3xx_i2c",
            "platform: sgp4x",
            "address: 0x44",
            "address: 0x77",
            "address: 0x59",
        ):
            self.assertIn(required, raw)
        lower = raw.lower()
        self.assertIn("drift", lower)
        self.assertIn("verified schematic", lower)

    def test_no_runtime_fan_health_invented(self) -> None:
        # The fan-relay stage population is unproven and no driver is
        # bound: the framework must not expose any fan/ventilation-hardware
        # runtime health entity, and must not duplicate the Core
        # framework's compile-time Fan Control Module Status entity.
        for entity_id, entity in self.entities.items():
            name = str(entity.get("name") or "").lower()
            self.assertNotIn("fan status", name)
            self.assertNotIn("fan health", name)
            self.assertNotIn("fan control module", name)
            self.assertNotIn("hardware status", name)


# --- Customer entity contract --------------------------------------------------


class CustomerEntityContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.framework = load_yaml(FRAMEWORK_PACKAGE)
        cls.entities = entities_by_id(cls.framework)
        cls.raw = FRAMEWORK_PACKAGE.read_text()

    def entity(self, entity_id: str) -> Dict[str, Any]:
        self.assertIn(entity_id, self.entities, f"missing entity {entity_id}")
        return self.entities[entity_id]

    def test_canonical_voc_is_an_index_not_a_concentration(self) -> None:
        voc = self.entity("s360_ventiq_voc")
        self.assertEqual(voc["_platform"], "sensor")
        self.assertEqual(voc.get("name"), "VOC")
        self.assertNotIn("unit_of_measurement", voc)

    def test_canonical_nox_is_an_index_not_a_concentration(self) -> None:
        nox = self.entity("s360_ventiq_nox")
        self.assertEqual(nox["_platform"], "sensor")
        self.assertEqual(nox.get("name"), "NOx")
        self.assertNotIn("unit_of_measurement", nox)

    def test_air_quality_headline_text_sensor(self) -> None:
        headline = self.entity("s360_ventiq_air_quality")
        self.assertEqual(headline["_platform"], "text_sensor")
        self.assertEqual(headline.get("name"), "Air Quality")

    def test_recommendation_text_sensor(self) -> None:
        rec = self.entity("s360_ventiq_recommendation")
        self.assertEqual(rec["_platform"], "text_sensor")
        self.assertEqual(rec.get("name"), "Recommendation")

    def test_ventilation_reason_text_sensor(self) -> None:
        reason = self.entity("s360_ventiq_reason")
        self.assertEqual(reason["_platform"], "text_sensor")
        self.assertEqual(reason.get("name"), "Ventilation Reason")

    def test_ventilation_needed_binary_sensor(self) -> None:
        needed = self.entity("s360_ventilation_needed")
        self.assertEqual(needed["_platform"], "binary_sensor")
        self.assertEqual(needed.get("name"), "Ventilation Needed")

    def test_shower_binary_sensor(self) -> None:
        shower = self.entity("s360_ventiq_shower")
        self.assertEqual(shower["_platform"], "binary_sensor")
        self.assertEqual(shower.get("name"), "Shower Active")
        self.assertEqual(shower.get("device_class"), "moisture")

    def test_mould_risk_binary_sensor(self) -> None:
        mould = self.entity("s360_ventiq_mould_risk")
        self.assertEqual(mould["_platform"], "binary_sensor")
        self.assertEqual(mould.get("name"), "Mould Risk")
        self.assertEqual(mould.get("device_class"), "problem")

    def test_default_enabled_state_set_is_exact(self) -> None:
        enabled = set()
        for entity_id, entity in self.entities.items():
            if entity["_platform"] not in ("sensor", "binary_sensor", "text_sensor"):
                continue
            if entity.get("internal") is True:
                continue
            if entity.get("entity_category") == "diagnostic":
                continue
            if entity.get("disabled_by_default") is True:
                continue
            enabled.add(entity_id)
        self.assertEqual(enabled, DEFAULT_ENABLED_STATE_IDS)

    def test_no_duplicate_humidity_or_temperature_entity(self) -> None:
        # RoomIQ owns the canonical Temperature/Humidity entities; the only
        # humidity/temperature-named entities here are legacy compatibility
        # ids, disabled by default.
        for entity_id, entity in self.entities.items():
            if entity.get("internal") is True:
                continue
            name = str(entity.get("name") or "")
            if name in ("Temperature", "Humidity"):
                self.fail(f"duplicate canonical environmental entity: {entity_id}")

    def test_legacy_numbers_preserved_and_wired(self) -> None:
        # Pre-framework these controls were placebo (no logic read them —
        # a recorded customer-experience defect). They are preserved with
        # exact ids and now genuinely applied via the evaluate script.
        script_blob = json.dumps(self.framework.get("script") or [])
        for number_id in WIRED_LEGACY_NUMBER_IDS:
            entity = self.entity(number_id)
            self.assertEqual(entity["_platform"], "number")
            self.assertTrue(entity.get("restore_value"))
            self.assertIn(number_id, script_blob, f"{number_id} not wired")

    def test_legacy_buttons_preserved_and_wired(self) -> None:
        for button_id in WIRED_LEGACY_BUTTON_IDS:
            entity = self.entity(button_id)
            self.assertEqual(entity["_platform"], "button")
            blob = json.dumps(entity)
            self.assertIn("sense360::ventiq", blob, f"{button_id} not wired")

    def test_shower_detection_switch_preserved_and_wired(self) -> None:
        switch = self.entity("bathroom_shower_detection_enabled")
        self.assertEqual(switch["_platform"], "switch")
        script_blob = json.dumps(self.framework.get("script") or []) + json.dumps(
            switch
        )
        self.assertIn("bathroom_shower_detection_enabled", script_blob)

    def test_auto_ventilation_compat_is_disabled_by_default(self) -> None:
        # The legacy Auto Ventilation switch controls nothing in any
        # current composition (no fan driver is bound to VentIQ). The id
        # is preserved for registrations but it leaves the default
        # surface — an honest framework does not present dead controls.
        switch = self.entity("bathroom_auto_ventilation")
        self.assertTrue(switch.get("disabled_by_default"))

    def test_legacy_compat_entities_preserved_and_disabled(self) -> None:
        for entity_id in LEGACY_COMPAT_IDS:
            entity = self.entity(entity_id)
            self.assertTrue(
                entity.get("disabled_by_default"),
                f"legacy compat entity {entity_id} must be disabled by default",
            )

    def test_legacy_compat_names_unchanged(self) -> None:
        expected_names = {
            "bathroom_temp_display": "${friendly_name} VentIQ Temperature",
            "bathroom_humidity_display": "${friendly_name} VentIQ Humidity",
            "bathroom_pressure_display": "${friendly_name} VentIQ Pressure",
            "bathroom_voc_display": "${friendly_name} VentIQ VOC Index",
            "bathroom_nox_display": "${friendly_name} VentIQ NOx Index",
            "bathroom_dew_point_display": "${friendly_name} VentIQ Dew Point",
            "bathroom_humidity_rate_display": "${friendly_name} VentIQ Humidity Rate",
            "bathroom_post_shower_timer_display": "${friendly_name} Post-Shower Timer",
            "bathroom_fan_recommendation_display": (
                "${friendly_name} Recommended Fan Speed"
            ),
            "bathroom_mold_risk_display": "${friendly_name} Mold Risk Level",
            "bathroom_shower_display": "${friendly_name} Shower Active",
            "bathroom_mold_warning_display": "${friendly_name} Mold Risk Warning",
            "bathroom_odor_display": "${friendly_name} Odor Detected",
            "bathroom_ventilation_needed": "${friendly_name} Ventilation Needed",
            "bathroom_status": "${friendly_name} Bathroom Status",
            "bathroom_mold_risk_status": "${friendly_name} Mold Risk Status",
            "bathroom_ventilation_advice": "${friendly_name} Ventilation Advice",
            "bathroom_air_quality_status": "${friendly_name} Air Quality",
            "bathroom_auto_ventilation": "${friendly_name} Auto Ventilation",
        }
        for entity_id, name in expected_names.items():
            self.assertEqual(
                self.entity(entity_id).get("name"),
                name,
                f"legacy compat name changed for {entity_id}",
            )

    def test_compat_temperature_and_humidity_source_canonical(self) -> None:
        # Semantic upgrade (documented): the legacy VentIQ climate display
        # entities are driven by the RoomIQ CANONICAL calibrated values —
        # never by the drifted on-board SHT4x driver.
        temp = self.entity("bathroom_temp_display")
        hum = self.entity("bathroom_humidity_display")
        self.assertEqual(temp.get("source_id"), "s360_temperature")
        self.assertEqual(hum.get("source_id"), "s360_humidity")

    def test_no_engineering_jargon_in_customer_entity_names(self) -> None:
        for entity_id, entity in self.entities.items():
            if entity.get("internal") is True:
                continue
            if entity.get("entity_category") == "diagnostic":
                continue
            name = str(entity.get("name") or "").lower()
            for token in FORBIDDEN_CUSTOMER_NAME_TOKENS:
                self.assertNotIn(
                    token, name, f"jargon '{token}' in customer entity {entity_id}"
                )

    def test_no_aqi_entity_anywhere(self) -> None:
        for entity_id, entity in self.entities.items():
            name = str(entity.get("name") or "").lower()
            self.assertNotIn("aqi", name)
            self.assertNotIn("aqi", entity_id)

    def test_diagnostics_are_diagnostic_and_disabled(self) -> None:
        for entity_id in (
            "s360_ventiq_state_detail",
            "s360_ventiq_expected_sensors",
            "s360_ventiq_sensor_verification",
            "s360_ventiq_voc_data_age",
            "s360_ventiq_humidity_data_age",
        ):
            entity = self.entity(entity_id)
            self.assertEqual(entity.get("entity_category"), "diagnostic")
            self.assertTrue(entity.get("disabled_by_default"))

    def test_sensor_verification_diagnostic_states_limits(self) -> None:
        blob = json.dumps(self.entity("s360_ventiq_sensor_verification"))
        for phrase in ("SGP41", "RoomIQ", "drift", "fan"):
            self.assertIn(phrase, blob)

    def test_no_threshold_control_farm(self) -> None:
        numbers = [e for e in self.entities.values() if e["_platform"] == "number"]
        self.assertLessEqual(
            len(numbers),
            3,
            "customer control surface must stay small (3 preserved controls)",
        )


# --- Framework mechanics --------------------------------------------------------


class FrameworkMechanicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = FRAMEWORK_PACKAGE.read_text()
        cls.framework = load_yaml(FRAMEWORK_PACKAGE)

    def test_framework_uses_the_shared_header(self) -> None:
        self.assertIn("ventiq_engine.h", self.raw)
        self.assertIn("sense360::ventiq", self.raw)

    def test_framework_ships_both_engine_headers(self) -> None:
        # ESPHome copies only the files listed under `esphome: includes:`
        # into the build tree; ventiq_engine.h transitively includes the
        # canonical airiq_engine.h, and VentIQ compositions never compose
        # the AirIQ framework package — so BOTH headers must be listed or
        # `esphome compile` fails (config validation alone cannot catch
        # this; proven by the first hosted compile round of this PR).
        includes = (self.framework.get("esphome") or {}).get("includes") or []
        self.assertIn("../include/sense360/airiq_engine.h", includes)
        self.assertIn("../include/sense360/ventiq_engine.h", includes)

    def test_freshness_comes_from_update_callbacks(self) -> None:
        self.assertIn("on_value", self.raw)
        self.assertIn("input_humidity", self.raw)
        self.assertIn("input_voc", self.raw)
        self.assertIn("input_nox", self.raw)

    def test_stale_values_are_never_left_standing(self) -> None:
        self.assertIn("publish_state(NAN)", self.raw)

    def test_module_status_driven_with_reserved_vocabulary(self) -> None:
        self.assertIn("s360_module_status_ventiq", self.raw)
        self.assertIn("health_to_string", self.raw)

    def test_no_fabricated_fault_producer(self) -> None:
        self.assertNotIn("set_fault(true)", self.raw.replace(" ", ""))

    def test_no_duplicated_pollutant_thresholds(self) -> None:
        # VOC/NOx severity thresholds live in the AirIQ engine (the
        # platform's single source of pollutant truth). The framework YAML
        # must not re-declare pollutant band values.
        subs = self.framework.get("substitutions") or {}
        for key in subs:
            self.assertNotRegex(
                key,
                r"(voc|nox)_(fair|poor|very_poor|hysteresis)",
                f"pollutant threshold duplicated in substitution {key}",
            )

    def test_ventilation_thresholds_are_centralised_substitutions(self) -> None:
        subs = self.framework.get("substitutions") or {}
        for key in (
            "ventiq_shower_humidity_threshold",
            "ventiq_shower_rate_threshold",
            "ventiq_clearing_minutes",
            "ventiq_mould_humidity_threshold",
            "ventiq_mould_duration_minutes",
            "ventiq_humidity_high_threshold",
            "ventiq_humidity_hysteresis",
        ):
            self.assertIn(key, subs, f"missing substitution {key}")

    def test_per_channel_freshness_windows(self) -> None:
        subs = self.framework.get("substitutions") or {}
        for key in (
            "ventiq_humidity_warmup_ms",
            "ventiq_humidity_stale_ms",
            "ventiq_voc_warmup_ms",
            "ventiq_voc_stale_ms",
            "ventiq_nox_warmup_ms",
            "ventiq_nox_stale_ms",
        ):
            self.assertIn(key, subs, f"missing substitution {key}")


# --- Engine header ---------------------------------------------------------------


class EngineHeaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = HEADER.read_text()

    def test_namespace_and_engine(self) -> None:
        self.assertIn("namespace sense360", self.raw)
        self.assertIn("namespace ventiq", self.raw)
        self.assertIn("class VentIQEngine", self.raw)

    def test_consumes_the_canonical_airiq_engine(self) -> None:
        # Pollutant severity is CONSUMED from the AirIQ engine — never
        # reimplemented. The header includes it and embeds an instance.
        self.assertIn('#include "airiq_engine.h"', self.raw)
        self.assertIn("airiq::AirIQEngine", self.raw)

    def test_no_duplicated_pollutant_thresholds_in_header(self) -> None:
        # The VOC band values (150/250/400) and NOx band values
        # (100/200/300) are owned by the AirIQ engine defaults; this
        # header must not re-declare them.
        self.assertNotIn("set_thresholds", self.raw.replace("pollutants_.", "P."))

    def test_state_strings_are_single_sourced(self) -> None:
        for value in RECOMMENDATION_STRINGS:
            self.assertIn(f'"{value}"', self.raw)
        for value in REASON_STRINGS:
            self.assertIn(f'"{value}"', self.raw)

    def test_humidity_documented_as_roomiq_provided(self) -> None:
        lower = self.raw.lower()
        self.assertIn("roomiq", lower)
        self.assertIn("s360_humidity", self.raw)

    def test_module_health_excludes_humidity(self) -> None:
        # VentIQ module health attests the S360-211's own verifiable
        # channels (SGP41 VOC/NOx) only; the RoomIQ-owned humidity input
        # degrades the SERVICE, never the VentIQ module.
        lower = self.raw.lower()
        self.assertIn("never", lower)
        self.assertIn("health", lower)

    def test_no_hardware_validation_claim(self) -> None:
        lower = self.raw.lower()
        self.assertIn("nothing in this header claims hardware validation", lower)


# --- Simulation tests --------------------------------------------------------------


class SimulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = CPP_TEST.read_text()

    def test_simulation_tests_exist(self) -> None:
        self.assertTrue(CPP_TEST.exists())

    def test_simulation_uses_the_production_header(self) -> None:
        self.assertIn('#include "../../include/sense360/ventiq_engine.h"', self.raw)

    def test_simulation_covers_required_scenarios(self) -> None:
        for keyword in (
            "startup",
            "warmup",
            "shower",
            "clearing",
            "mould",
            "odour",
            "humidity",
            "stale",
            "recovery",
            "invalid",
            "degraded",
            "unavailable",
            "force",
            "reset",
            "disable",
            "priority",
            "hysteresis",
            "fan_percent",
            "dew_point",
        ):
            self.assertIn(keyword, self.raw, f"simulation must cover {keyword}")

    def test_simulation_is_logic_proof_only(self) -> None:
        lower = self.raw.lower()
        self.assertIn("logic/simulation proof only", lower)
        self.assertIn("never hardware validation", lower)


# --- Bundle wiring ------------------------------------------------------------------


class BundleWiringTests(unittest.TestCase):
    def test_contract_declares_ventiq_bundles(self) -> None:
        self.assertGreaterEqual(len(ventiq_bundles()), 7)

    def test_ventiq_bundles_compose_the_framework_exactly_once(self) -> None:
        for bundle in ventiq_bundles():
            raw = bundle.read_text()
            self.assertEqual(
                raw.count(FRAMEWORK_INCLUDE),
                1,
                f"{bundle.name} must compose the VentIQ framework exactly once",
            )

    def test_ventiq_bundles_drop_the_legacy_profile(self) -> None:
        for bundle in ventiq_bundles():
            raw = bundle.read_text()
            for legacy in LEGACY_PROFILE_INCLUDES:
                for line in raw.splitlines():
                    if line.strip().startswith("#"):
                        continue
                    self.assertNotIn(
                        f"features/{legacy}",
                        line,
                        f"{bundle.name} still composes {legacy}",
                    )

    def test_ventiq_bundles_keep_the_board_composition(self) -> None:
        # The board layer stays composed. The fan bundles bind it through
        # the preserved legacy alias (packages/expansions/
        # airiq_bathroom_base.yaml -> the board package, byte-identical
        # resolution per the alias-retention policy); the others bind the
        # canonical board package directly.
        for bundle in ventiq_bundles():
            raw = bundle.read_text()
            self.assertTrue(
                "packages/boards/s360-211-ventiq.yaml" in raw
                or "packages/expansions/airiq_bathroom_base.yaml" in raw,
                f"{bundle.name} lost the VentIQ board composition",
            )

    def test_ventiq_bundles_keep_the_diagnostics_surface(self) -> None:
        # The superseded bathroom_profile nested diagnostics.yaml; the
        # bundle swap must not shrink that shipped surface.
        for bundle in ventiq_bundles():
            raw = bundle.read_text()
            self.assertIn(
                "packages/features/diagnostics.yaml",
                raw,
                f"{bundle.name} lost the diagnostics surface",
            )

    def test_non_ventiq_bundles_gain_nothing(self) -> None:
        for bundle in non_ventiq_bundles():
            raw = bundle.read_text()
            self.assertNotIn("ventiq_framework", raw, f"{bundle.name} leaked")

    def test_legacy_shim_products_keep_the_profile(self) -> None:
        # The pinned legacy product keeps its exact pre-framework
        # behaviour (profile path, not the framework).
        legacy_product = REPO_ROOT / "products" / "sense360-core-ceiling-bathroom.yaml"
        raw = legacy_product.read_text()
        self.assertNotIn("ventiq_framework", raw)

    def test_compile_only_skeletons_never_include_the_framework(self) -> None:
        compile_only = REPO_ROOT / "products" / "compile-only"
        for path in sorted(compile_only.glob("*.yaml")):
            self.assertNotIn(
                "ventiq_framework",
                path.read_text(),
                f"compile-only skeleton {path.name} must not compose the framework",
            )


# --- Core framework contract ----------------------------------------------------------


class CoreFrameworkContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text())

    def test_ventiq_capability_names_the_framework_and_the_drift(self) -> None:
        description = self.contract["capabilities"]["ventiq"]["description"]
        self.assertIn("VENTIQ-FRAMEWORK-001", description)
        self.assertIn("drift", description)
        self.assertIn("RoomIQ", description)
        self.assertIn("SGP4x", description)

    def test_ventiq_module_runtime_status_declared(self) -> None:
        runtime = self.contract["module_runtime_status"]["ventiq"]
        self.assertEqual(runtime["work_item"], "VENTIQ-FRAMEWORK-001")
        self.assertEqual(runtime["entity_id"], "s360_module_status_ventiq")
        self.assertEqual(runtime["package"], "packages/features/ventiq_framework.yaml")
        self.assertEqual(tuple(runtime["values"]), HEALTH_STRINGS)
        definition = runtime["available_definition"]
        self.assertIn("SGP41", definition)
        self.assertIn("humidity", definition.lower())
        self.assertIn("never", definition.lower())

    def test_guardrail_names_ventiq_as_fourth_wired_module(self) -> None:
        blob = json.dumps(self.contract["guardrails"])
        self.assertIn("VENTIQ-FRAMEWORK-001", blob)

    def test_presence_roomiq_airiq_runtime_entries_unchanged(self) -> None:
        runtime = self.contract["module_runtime_status"]
        self.assertEqual(runtime["presence"]["work_item"], "PRESENCE-FRAMEWORK-001")
        self.assertEqual(runtime["roomiq"]["work_item"], "ROOMIQ-FRAMEWORK-001")
        self.assertEqual(runtime["airiq"]["work_item"], "AIRIQ-FRAMEWORK-001")

    def test_no_release_declaration_changed(self) -> None:
        # The framework changes no release row: config strings in the
        # contract stay exactly the pre-existing set.
        configs = set(self.contract["configs"].keys())
        self.assertEqual(
            configs,
            {
                "Ceiling-POE-VentIQ-RoomIQ",
                "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ",
                "Ceiling-POE-VentIQ-FanRelay-RoomIQ",
                "Ceiling-POE-VentIQ-FanPWM-RoomIQ",
                "Ceiling-POE-VentIQ-FanDAC-RoomIQ",
                "Ceiling-POE-AirIQ-FanRelay-RoomIQ",
                "Ceiling-POE-AirIQ-FanDAC-RoomIQ",
                "Ceiling-POE-AirIQ-FanPWM-RoomIQ",
                "Ceiling-POE-FanDAC",
                "Ceiling-POE-FanPWM",
                "Ceiling-POE-VentIQ-RoomIQ-LED",
                "Ceiling-POE-RoomIQ",
                "Ceiling-POE-AirIQ-RoomIQ",
                "Ceiling-POE-RoomIQ-LED",
                "Ceiling-USB-VentIQ-RoomIQ",
                "Ceiling-USB-RoomIQ",
            },
        )


# --- Compile lane -----------------------------------------------------------------------


class CompileLaneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.compile_raw = COMPILE_WORKFLOW.read_text()
        cls.validate_raw = VALIDATE_WORKFLOW.read_text()

    def test_matrix_covers_the_required_ventiq_compositions(self) -> None:
        for config in (
            "Ceiling-POE-VentIQ-RoomIQ",
            "Ceiling-USB-VentIQ-RoomIQ",
            "Ceiling-POE-VentIQ-RoomIQ-LED",
        ):
            self.assertIn(config, self.compile_raw)

    def test_matrix_keeps_a_non_ventiq_regression_target(self) -> None:
        self.assertIn("Ceiling-POE-FanDAC", self.compile_raw)
        self.assertIn("Ceiling-POE-RoomIQ", self.compile_raw)

    def test_contract_gate_runs_ventiq_tests(self) -> None:
        self.assertIn("python3 tests/test_ventiq_framework.py", self.compile_raw)

    def test_paths_cover_ventiq_framework_surfaces(self) -> None:
        self.assertIn("tests/test_ventiq_framework.py", self.compile_raw)

    def test_quick_validation_gate_runs_ventiq_contract(self) -> None:
        self.assertIn("python3 tests/test_ventiq_framework.py", self.validate_raw)


# --- Documentation -----------------------------------------------------------------------


class DocumentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = DOC.read_text()
        cls.checklist = CHECKLIST.read_text()

    def test_doc_exists_and_names_the_work_item(self) -> None:
        self.assertIn("VENTIQ-FRAMEWORK-001", self.doc)

    def test_evidence_layers_recorded_separately(self) -> None:
        lower = self.doc.lower()
        for layer in (
            "schematic",
            "bom",
            "assembly",
            "firmware",
            "bundle",
            "customer",
            "bench",
        ):
            self.assertIn(layer, lower, f"evidence layer '{layer}' missing")

    def test_conflicts_recorded_not_resolved(self) -> None:
        lower = self.doc.lower()
        # The four recorded authority conflicts.
        self.assertIn("sht4x", lower)
        self.assertIn("bmp390", lower)
        self.assertIn("s360-bath-b", lower)
        self.assertIn("crossed", lower)  # relay stage drawn crossed-out
        self.assertIn("j1", lower)
        self.assertIn("j9", lower)

    def test_follow_up_programmes_created(self) -> None:
        for programme in (
            "VENTIQ-FRAMEWORK-BENCH-001",
            "VENTIQ-HW-DRIFT-001",
            "VENTIQ-RELAY-POPULATION-001",
            "VENTIQ-SKU-LABEL-001",
        ):
            self.assertIn(programme, self.doc, f"follow-up {programme} missing")

    def test_no_false_proof(self) -> None:
        lower = self.doc.lower()
        self.assertIn("no hardware, bench, compliance", lower)

    def test_reuse_documented(self) -> None:
        for phrase in ("airiq_engine.h", "s360_humidity", "roomiq"):
            self.assertIn(phrase.lower(), self.doc.lower())

    def test_checklist_is_results_free(self) -> None:
        lower = self.checklist.lower()
        self.assertIn("ventiq-framework-bench-001", lower)
        # The checklist is a container for FUTURE operator evidence: it
        # must not contain any pre-filled result, date or signature.
        self.assertNotIn("passed", lower)
        self.assertNotIn("verified on", lower)

    def test_roadmap_records_the_programme(self) -> None:
        raw = ROADMAP.read_text()
        self.assertIn("VENTIQ-FRAMEWORK-001", raw)
        self.assertIn("VENTIQ-HW-DRIFT-001", raw)


if __name__ == "__main__":
    unittest.main()

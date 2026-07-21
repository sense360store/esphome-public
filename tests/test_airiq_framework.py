#!/usr/bin/env python3
"""AIRIQ-FRAMEWORK-001 — canonical indoor-air-quality service contract.

These tests define (and then pin) the customer-focused Sense360 AirIQ
framework for the S360-210 AirIQ board: honest individual pollutant
measurements (CO2 ppm, VOC index, NOx index, PM2.5 µg/m³), ONE headline
Air Quality state, ONE customer Recommendation, per-sensor warm-up and
freshness, and the AirIQ module runtime status — all produced by ONE
shared engine that downstream consumers (VentIQ / Pure / Zones / Home
Assistant) reuse instead of duplicating pollutant threshold logic.

Authority facts this contract encodes (re-audited against the verified
S360-210-R4 schematic, the R4 BOM artifact record, the hardware catalog
and SOT — see docs/architecture/sense360-airiq-framework.md; the five
layers PCB-footprint / production-population / external-connector /
driver-compiled / customer-functionality are recorded SEPARATELY):

* There is NO authoritative "AirIQ Base" vs "AirIQ Pro" product axis: the
  taxonomy is flat (one SKU per product, S360-210). Expected-sensor
  membership is configuration-driven by substitutions, never by an
  invented Base/Pro flag.
* Compiled customer stack: SCD41 (CO2 ppm; PCB-mounted U3) + SGP41
  (VOC/NOx relative indices — NEVER concentrations; PCB-mounted U1).
* SPS30 (PM µg/m³) is a SUPPORTED EXTERNAL ATTACHMENT (J2): the driver is
  compiled, but no authoritative kit/SOT/product record declares the
  module as supplied (kit records enumerate board SKUs only; no SPS30
  SKU exists; SOT never names SPS30; WebFlash lists the SPS30 as
  "optional"; the roadmap doctrine reserves the catalog's "Connectors
  for ..." phrasing for genuinely optional attachments). Commercial
  inclusion is therefore UNPROVEN: SPS30 is expected=false by default,
  its absence never degrades AirIQ health, and PM entities ship disabled
  by default — a future SPS30-declared composition opts in explicitly
  (airiq_expected_pm + enabling the PM entities). Firmware inference
  never creates a commercial decision.
* MICS-4514 (U4) + STM8 (U5) are PCB-MOUNTED (schematic + BOM + catalog
  agree) but have NO firmware driver and an unverified readout interface
  (ENTITY-FILL-210-MICS-001): the engine carries diagnostic-only MiCS
  channels, no customer CO / NO2 concentration is ever claimed, and no
  production input exists yet.
* SFA40 (formaldehyde): PCB footprint U2 is PRESENT on the verified
  schematic (which shows no SFA40 connector) and the BOM lists it
  populated, while the hardware catalog / reference doc describe a
  connector-attached off-board module — production-assembly population
  is an UNRESOLVED conflict (HW-PINMAP-210-FOLLOWUP). No driver is
  compiled; no Formaldehyde entity may exist until BOTH fitment and a
  compiled supported driver are proven.
* SEN0321 (ZE27-O3 ozone): an EXTERNAL sensor/interface — the verified
  schematic's STM8 stage is titled for "SEN0321(ZE27-O3) and MICS-4514";
  no on-board ozone part, no driver, no entity. ZE07 has no record.
* Pressure is NOT S360-210 product hardware: no pressure part exists on
  the verified schematic, the BOM, or the hardware catalog. The compiled
  BMP390 @0x77 in the board package is FIRMWARE/CATALOG DRIFT: it stays
  excluded from customer entities, severity, health and product claims.
* The headline uses a transparent worst-pollutant model: one severe
  pollutant is never averaged away; stale data is never treated as good.

Uses Python's stdlib unittest (repo convention). Run with::

    python3 tests/test_airiq_framework.py
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any, Dict, List

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

FRAMEWORK_PACKAGE = REPO_ROOT / "packages" / "features" / "airiq_framework.yaml"
LEGACY_PROFILE = REPO_ROOT / "packages" / "features" / "airiq_basic_profile.yaml"
BOARD_PACKAGE = REPO_ROOT / "packages" / "boards" / "s360-210-airiq.yaml"
SPS30_OVERLAY = REPO_ROOT / "packages" / "boards" / "s360-210-airiq-sps30.yaml"
SFA40_COMPONENT = REPO_ROOT / "components" / "sfa40"
MICS_COMPONENT = REPO_ROOT / "components" / "mics_stm8"
HEADER = REPO_ROOT / "include" / "sense360" / "airiq_engine.h"
ROOMIQ_HEADER = REPO_ROOT / "include" / "sense360" / "roomiq_engine.h"
CPP_TEST = REPO_ROOT / "tests" / "unit" / "test_airiq_engine.cpp"
DOC = REPO_ROOT / "docs" / "architecture" / "sense360-airiq-framework.md"
CHECKLIST = REPO_ROOT / "docs" / "hardware" / "airiq-framework-bench-checklist.md"
COMPILE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "core-framework-compile.yml"
VALIDATE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "validate.yml"
CONTRACT = REPO_ROOT / "config" / "core-framework.json"
ROADMAP = REPO_ROOT / "docs" / "sense360-roadmap-status.md"
BUNDLES_DIR = REPO_ROOT / "products" / "bundles"

FRAMEWORK_INCLUDE = "!include ../../packages/features/airiq_framework.yaml"
LEGACY_PROFILE_INCLUDES = (
    "airiq_basic_profile.yaml",
    "airiq_mqtt_profile.yaml",
)
# Legacy display/threshold packages that must never be composed together
# with the framework (duplicate pollutant entities / duplicate thresholds).
LEGACY_THRESHOLD_PACKAGES = (
    "airiq_basic.yaml",
    "airiq_advanced.yaml",
    "airiq_profile.yaml",
    "airiq_extended_profile.yaml",
    "ceiling_led_ring_air_quality.yaml",
)

# Customer state vocabularies — single-sourced in the engine header.
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
    "Check pollution source",
    "Unavailable",
)
HEALTH_STRINGS = ("Initialising", "Available", "Degraded", "Unavailable", "Fault")

# Raw sensor part numbers / engineering jargon that must never appear in a
# customer entity name (diagnostics and documentation only). "aqi" is
# banned because no recognised AQI standard is implemented (no AQI claim).
FORBIDDEN_CUSTOMER_NAME_TOKENS = (
    "scd41",
    "scd4x",
    "sgp41",
    "sgp4x",
    "sps30",
    "bmp390",
    "bmp581",
    "mics",
    "stm8",
    "sfa40",
    "sfa30",
    "ze07",
    "ze27",
    "aqi",
    "adc",
    "resistance",
    "baseline",
    "heater",
    "raw",
    "i2c",
    "gpio",
    "framework",
    "calibration state",
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

# The exact default-enabled customer set: pollutant measurements from the
# PCB-mounted compiled sensors + one headline + one recommendation. PM is
# NOT default-enabled anywhere: the SPS30 is an external attachment whose
# commercial inclusion is unproven.
DEFAULT_ENABLED_IDS = {
    "s360_co2",
    "s360_voc",
    "s360_nox",
    "s360_hcho",
    "s360_air_quality",
    "s360_recommendation",
}

# Standard (non-diagnostic) sensors that stay disabled by default: every
# PM entity (SPS30 external-attachment inclusion unproven; a declared
# composition opts in) — PM2.5 first among them, then the secondary
# fractions.
DISABLED_STANDARD_SENSOR_IDS = {
    "s360_pm2_5",
    "s360_pm1",
    "s360_pm4",
    "s360_pm10",
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


def airiq_bundles() -> List[Path]:
    """Bundle files whose contract entry declares the airiq capability."""
    contract = json.loads(CONTRACT.read_text())
    paths = []
    for entry in contract.get("configs", {}).values():
        if "airiq" in (entry.get("capabilities") or []):
            paths.append(REPO_ROOT / entry["bundle"])
    return sorted(paths)


def non_airiq_bundles() -> List[Path]:
    contract = json.loads(CONTRACT.read_text())
    paths = []
    for entry in contract.get("configs", {}).values():
        if "airiq" not in (entry.get("capabilities") or []):
            paths.append(REPO_ROOT / entry["bundle"])
    return sorted(paths)


# --- Package existence -------------------------------------------------------


class PackageFilesExistTests(unittest.TestCase):
    def test_new_files_exist(self) -> None:
        for path in (FRAMEWORK_PACKAGE, HEADER, CPP_TEST, DOC, CHECKLIST):
            self.assertTrue(path.is_file(), f"missing AIRIQ-FRAMEWORK-001 file: {path}")

    def test_no_secret_material_in_airiq_packages(self) -> None:
        for path in (FRAMEWORK_PACKAGE, BOARD_PACKAGE):
            if not path.is_file():
                continue
            raw = path.read_text().lower()
            self.assertNotIn("!secret", raw, path.name)
            for needle in ("password:", "api_encryption", "token"):
                # The MQTT compatibility block passes through the (empty by
                # default) legacy substitutions only.
                if needle == "password:" and "airiq_mqtt_password" in raw:
                    continue
                self.assertNotIn(needle, raw, path.name)


# --- Authority and configuration ----------------------------------------------


class AuthorityTests(unittest.TestCase):
    """Expected-sensor membership is configuration-driven; no Base/Pro axis
    is invented; unfitted / unresolved sensors never leak into products."""

    def setUp(self) -> None:
        if not FRAMEWORK_PACKAGE.is_file():
            self.skipTest("framework package not implemented yet")
        self.doc = load_yaml(FRAMEWORK_PACKAGE)
        self.subs = self.doc.get("substitutions") or {}

    def test_expected_sensor_membership_is_configuration_driven(self) -> None:
        # Compiled stack defaults: CO2 / VOC / NOx / PM expected. The
        # formaldehyde and ozone slots exist for future authoritative
        # compositions but default OFF everywhere today (no driver, no
        # resolved fitment) — they must not leak into current products.
        # PCB-mounted compiled sensors are expected; EXTERNAL attachments
        # (SPS30 PM, SEN0321/ZE27-O3 ozone) and unfitted stages default
        # OFF — a composition that declares an attachment opts in.
        expectations = {
            "airiq_expected_co2": "true",
            "airiq_expected_voc": "true",
            "airiq_expected_nox": "true",
            "airiq_expected_pm": "false",
            "airiq_expected_hcho": "true",
            "airiq_expected_o3": "false",
        }
        for key, value in expectations.items():
            self.assertIn(key, self.subs, key)
            self.assertEqual(str(self.subs[key]).lower(), value, key)

    def test_no_base_pro_axis_invented(self) -> None:
        # The product taxonomy is flat (one SKU per product). The framework
        # must not invent an "AirIQ Base" / "AirIQ Pro" composition flag.
        raw = FRAMEWORK_PACKAGE.read_text().lower()
        self.assertNotIn("airiq base", raw)
        self.assertNotIn("airiq pro", raw)
        self.assertNotIn("base_pro", raw)

    def test_formaldehyde_exposed_but_no_ozone_entity(self) -> None:
        # AIRIQ-HW-RECONCILE-001: the fitted SFA40 (U2) gives a real,
        # factory-calibrated ppb formaldehyde reading, so a customer
        # Formaldehyde entity now exists. Ozone (no fitted part, no driver)
        # still must not be exposed anywhere.
        entities = entities_by_id(self.doc)
        self.assertIn("s360_hcho", entities)
        self.assertEqual(entities["s360_hcho"]["name"], "Formaldehyde")
        for entity_id, entry in entities.items():
            name = str(entry.get("name", "")).lower()
            self.assertNotIn("ozone", name, entity_id)

    def test_no_mics_pollutant_entity(self) -> None:
        # MiCS-4514 has no driver and no defensible calibration: no
        # customer CO / NO2 concentration entity may exist.
        entities = entities_by_id(self.doc)
        for entity_id, entry in entities.items():
            name = str(entry.get("name", "")).lower()
            self.assertNotIn("carbon monoxide", name, entity_id)
            self.assertNotIn("nitrogen dioxide", name, entity_id)
            self.assertNotIn("mics", name, entity_id)

    def test_sps30_external_attachment_never_assumed_included(self) -> None:
        # A connector and a compiled driver do not prove an external
        # module is physically supplied. No authoritative kit / SOT /
        # product record declares SPS30 inclusion, so the framework must
        # state the opt-in posture and every AirIQ bundle must list the
        # SPS30 as an external attachment separate from the S360-210
        # board SKU — and must not describe AirIQ as a "full ... stack".
        raw = FRAMEWORK_PACKAGE.read_text().lower()
        self.assertIn("opt-in", raw)
        self.assertIn("external attachment", raw)
        for bundle in airiq_bundles():
            text = bundle.read_text()
            self.assertIn("SPS30", text, bundle.name)
            self.assertIn("external", text.lower(), bundle.name)
            for phrase in (
                "full indoor air-quality stack",
                "full ceiling air-quality stack",
                "full air-quality stack",
            ):
                self.assertNotIn(phrase, text, f"{bundle.name}: {phrase}")

    def test_board_package_separates_pcb_from_external(self) -> None:
        # The board package must not present the SPS30 as part of the
        # S360-210 PCB: it is an external J2 attachment.
        raw = BOARD_PACKAGE.read_text()
        self.assertIn("J2", raw)
        self.assertIn("external", raw.lower())

    def test_board_package_probes_fitted_hardware_only(self) -> None:
        # AIRIQ-HW-RECONCILE-001: the board package probes the FITTED R4
        # hardware — SGP41 (0x59), SCD41 (0x62), SFA40 (0x5D) and the
        # MICS/STM8 bridge (0x60) — and NOT the drifted BMP390 or the
        # external SPS30.
        raw = BOARD_PACKAGE.read_text()
        for needle in (
            "platform: sgp4x",
            "platform: scd4x",
            "platform: sfa40",
            "mics_stm8:",
            "address: 0x59",
            "address: 0x62",
            "address: 0x5D",
            "address: 0x60",
        ):
            self.assertIn(needle, raw, needle)
        for absent in (
            "platform: sps30",
            "platform: bmp3xx_i2c",
            "address: 0x69",
            "address: 0x77",
        ):
            self.assertNotIn(absent, raw, absent)
        # The raw pollutant sub-sensors (SGP41/SCD41/SFA40) stay internal;
        # the framework re-exposes the canonical customer surface.
        doc = load_yaml(BOARD_PACKAGE)
        for entry in doc.get("sensor") or []:
            for sub in entry.values():
                if isinstance(sub, dict) and "id" in sub and "name" in sub:
                    self.assertTrue(
                        sub.get("internal"),
                        f"raw pollutant sensor {sub.get('id')} must stay internal",
                    )


# --- Customer entity contract ---------------------------------------------------


class CustomerEntityContractTests(unittest.TestCase):
    """The default-enabled customer surface is exactly the accepted set,
    with honest units (indices are never concentrations)."""

    def setUp(self) -> None:
        if not FRAMEWORK_PACKAGE.is_file():
            self.skipTest("framework package not implemented yet")
        self.doc = load_yaml(FRAMEWORK_PACKAGE)
        self.entities = entities_by_id(self.doc)

    def _entity(self, entity_id: str) -> Dict[str, Any]:
        self.assertIn(entity_id, self.entities, f"missing entity {entity_id}")
        return self.entities[entity_id]

    def test_canonical_co2(self) -> None:
        entity = self._entity("s360_co2")
        self.assertEqual(entity["name"], "CO2")
        self.assertEqual(entity.get("unit_of_measurement"), "ppm")
        self.assertEqual(entity.get("device_class"), "carbon_dioxide")
        self.assertEqual(entity.get("state_class"), "measurement")

    def test_canonical_voc_is_an_index_not_a_concentration(self) -> None:
        entity = self._entity("s360_voc")
        self.assertEqual(entity["name"], "VOC")
        # SGP41 VOC output is a relative index: it must NEVER carry a
        # concentration unit (ppm / ppb / µg/m³ / mg/m³).
        self.assertNotIn("unit_of_measurement", entity)
        self.assertNotIn("device_class", entity)
        self.assertEqual(entity.get("state_class"), "measurement")

    def test_canonical_nox_is_an_index_not_a_concentration(self) -> None:
        entity = self._entity("s360_nox")
        self.assertEqual(entity["name"], "NOx")
        self.assertNotIn("unit_of_measurement", entity)
        self.assertNotIn("device_class", entity)
        self.assertEqual(entity.get("state_class"), "measurement")

    def test_canonical_pm25(self) -> None:
        entity = self._entity("s360_pm2_5")
        self.assertEqual(entity["name"], "PM2.5")
        self.assertEqual(entity.get("unit_of_measurement"), "µg/m³")
        self.assertEqual(entity.get("device_class"), "pm25")
        self.assertEqual(entity.get("state_class"), "measurement")

    def test_air_quality_headline_text_sensor(self) -> None:
        entity = self._entity("s360_air_quality")
        self.assertEqual(entity["_platform"], "text_sensor")
        self.assertEqual(entity["name"], "Air Quality")
        self.assertNotIn("disabled_by_default", entity)

    def test_recommendation_text_sensor(self) -> None:
        entity = self._entity("s360_recommendation")
        self.assertEqual(entity["_platform"], "text_sensor")
        self.assertEqual(entity["name"], "Recommendation")
        self.assertNotIn("disabled_by_default", entity)

    def test_default_enabled_customer_set_is_exact(self) -> None:
        enabled = set()
        for entity_id, entry in self.entities.items():
            if entry.get("internal"):
                continue
            if entry.get("disabled_by_default"):
                continue
            if entry.get("entity_category") in ("diagnostic", "config"):
                continue
            enabled.add(entity_id)
        self.assertEqual(
            enabled,
            DEFAULT_ENABLED_IDS,
            "default-enabled customer set must be exactly the accepted set",
        )

    def test_extra_pm_fractions_disabled_by_default(self) -> None:
        for entity_id in DISABLED_STANDARD_SENSOR_IDS:
            entity = self._entity(entity_id)
            self.assertTrue(
                entity.get("disabled_by_default"),
                f"{entity_id} must be disabled by default",
            )

    def test_pm_fraction_units(self) -> None:
        for entity_id, device_class in (
            ("s360_pm1", "pm1"),
            ("s360_pm10", "pm10"),
        ):
            entity = self._entity(entity_id)
            self.assertEqual(entity.get("unit_of_measurement"), "µg/m³")
            self.assertEqual(entity.get("device_class"), device_class)
        pm4 = self._entity("s360_pm4")
        self.assertEqual(pm4.get("unit_of_measurement"), "µg/m³")

    def test_pm_entities_are_opt_in_for_declared_compositions(self) -> None:
        # PM2.5 exists (the driver is compiled and a customer with an
        # attached SPS30 can enable it), but it ships disabled by default
        # and the framework documents the explicit opt-in contract for a
        # future composition with a declared SPS30 attachment.
        entity = self._entity("s360_pm2_5")
        self.assertTrue(entity.get("disabled_by_default"))
        raw = FRAMEWORK_PACKAGE.read_text()
        self.assertIn("airiq_expected_pm", raw)
        lowered = raw.lower()
        self.assertIn("opt-in", lowered)
        self.assertIn("declared", lowered)

    def test_no_pressure_customer_surface_bmp390_removed(self) -> None:
        # Pressure is NOT S360-210 product hardware: absent from the
        # verified schematic, the R4 BOM and the hardware catalog. Under
        # AIRIQ-HW-RECONCILE-001 the drifted BMP390 @0x77 is REMOVED — the
        # framework exposes NO pressure entity and the board package no
        # longer probes it.
        self.assertNotIn("s360_pressure", self.entities)
        self.assertNotIn("s360_airiq_pressure_data_age", self.entities)
        for entity_id, entry in self.entities.items():
            name = str(entry.get("name", "")).lower()
            self.assertNotIn("pressure", name, entity_id)
        raw = FRAMEWORK_PACKAGE.read_text()
        self.assertNotIn("airiq_pressure_source_id", raw)
        self.assertNotIn("input_pressure", raw)
        # The removal is stated on-device (sensor verification) and the
        # board package no longer instantiates the BMP390 driver.
        self.assertIn("drift", raw.lower())
        board_raw = BOARD_PACKAGE.read_text()
        self.assertNotIn("platform: bmp3xx_i2c", board_raw)
        self.assertNotIn("address: 0x77", board_raw)

    def test_no_engineering_jargon_in_customer_entity_names(self) -> None:
        for entity_id, entry in self.entities.items():
            if entry.get("internal"):
                continue
            if entry.get("entity_category") == "diagnostic":
                continue
            name = str(entry.get("name", "")).lower()
            for token in FORBIDDEN_CUSTOMER_NAME_TOKENS:
                self.assertNotIn(
                    token, name, f"{entity_id} name contains jargon '{token}'"
                )

    def test_no_aqi_entity_anywhere(self) -> None:
        # No recognised AQI standard is implemented; no entity may claim
        # to be an AQI (diagnostics included).
        for entity_id, entry in self.entities.items():
            name = str(entry.get("name", "")).lower()
            self.assertNotIn("aqi", name, entity_id)
            self.assertNotIn("air quality index", name, entity_id)

    def test_diagnostics_are_diagnostic_and_disabled(self) -> None:
        for entity_id in (
            "s360_airiq_state_detail",
            "s360_airiq_recommendation_reason",
            "s360_airiq_expected_sensors",
            "s360_airiq_sensor_verification",
            "s360_airiq_co2_data_age",
            "s360_airiq_voc_data_age",
            "s360_airiq_pm_data_age",
        ):
            entity = self._entity(entity_id)
            self.assertEqual(entity.get("entity_category"), "diagnostic", entity_id)
            self.assertTrue(entity.get("disabled_by_default"), entity_id)

    def test_sensor_verification_diagnostic_states_limits(self) -> None:
        entity = self._entity("s360_airiq_sensor_verification")
        raw = FRAMEWORK_PACKAGE.read_text()
        # The on-device honesty companion must state the BMP390
        # firmware/catalog drift, the not-compiled PCB-mounted MiCS stage
        # and the fitment-unresolved SFA40 stage.
        self.assertIn("BMP390", raw)
        self.assertIn("MICS-4514", raw)
        self.assertIn("SFA40", raw)
        self.assertEqual(entity.get("entity_category"), "diagnostic")

    def test_no_dozens_of_threshold_controls(self) -> None:
        # Thresholds are provisional internal substitutions, deliberately
        # NOT one customer entity per threshold and NOT a single opaque
        # "sensitivity" control.
        numbers = [
            entry for entry in (self.doc.get("number") or []) if isinstance(entry, dict)
        ]
        self.assertEqual(
            numbers, [], "no customer threshold controls in the first slice"
        )
        for entity_id, entry in self.entities.items():
            name = str(entry.get("name", "")).lower()
            self.assertNotIn("sensitivity", name, entity_id)

    def test_legacy_compat_entity_preserved_and_disabled(self) -> None:
        # The one published pre-framework customer entity
        # (air_quality_state, "Air Quality State" — previously a hardcoded
        # "unknown" placeholder) keeps its id and name, becomes a
        # disabled-by-default compatibility entity driven by the canonical
        # headline (documented semantic upgrade).
        entity = self._entity("air_quality_state")
        self.assertEqual(entity["_platform"], "text_sensor")
        self.assertEqual(entity["name"], "${friendly_name} Air Quality State")
        self.assertTrue(entity.get("disabled_by_default"))

    def test_mqtt_compatibility_surface_preserved(self) -> None:
        # The superseded airiq_basic_profile carried an MQTT block wired to
        # substitutions; shipped AirIQ firmware compiled it in. The
        # framework preserves that capability surface verbatim.
        subs = self.doc.get("substitutions") or {}
        self.assertEqual(subs.get("airiq_mqtt_broker"), "")
        self.assertEqual(str(subs.get("airiq_mqtt_port")), "1883")
        mqtt = self.doc.get("mqtt") or {}
        self.assertEqual(mqtt.get("broker"), "${airiq_mqtt_broker}")
        self.assertEqual(mqtt.get("discovery"), False)
        self.assertEqual(mqtt.get("topic_prefix"), "${air_quality_topic}")


# --- Framework mechanics ----------------------------------------------------------


class FrameworkMechanicsTests(unittest.TestCase):
    def setUp(self) -> None:
        if not FRAMEWORK_PACKAGE.is_file():
            self.skipTest("framework package not implemented yet")
        self.raw = FRAMEWORK_PACKAGE.read_text()

    def test_framework_uses_the_shared_header(self) -> None:
        self.assertIn("../include/sense360/airiq_engine.h", self.raw)

    def test_freshness_comes_from_update_callbacks(self) -> None:
        # Real value-update callbacks are the freshness signal. The PCB
        # sensors (CO2/VOC/NOx/HCHO) are wired here; the external SPS30 PM
        # input lives in the opt-in overlay (see SPS30OverlayTests).
        self.assertIn("on_value", self.raw)
        self.assertIn("input_co2", self.raw)
        self.assertIn("input_voc", self.raw)
        self.assertIn("input_nox", self.raw)
        self.assertIn("input_hcho", self.raw)
        self.assertNotIn("input_pm2_5", self.raw)

    def test_stale_values_are_never_left_standing(self) -> None:
        self.assertIn("publish_state(NAN)", self.raw)

    def test_module_status_driven_with_reserved_vocabulary(self) -> None:
        self.assertIn("s360_module_status_airiq", self.raw)
        self.assertIn("health_to_string", self.raw)

    def test_no_fabricated_fault_producer(self) -> None:
        # Fault is an engine contract with no production producer today:
        # production YAML must never call set_fault.
        self.assertNotIn("set_fault", self.raw)

    def test_thresholds_are_centralised_substitutions(self) -> None:
        for key in (
            "airiq_co2_fair_ppm",
            "airiq_co2_poor_ppm",
            "airiq_co2_very_poor_ppm",
            "airiq_voc_fair_index",
            "airiq_voc_poor_index",
            "airiq_voc_very_poor_index",
            "airiq_nox_fair_index",
            "airiq_nox_poor_index",
            "airiq_nox_very_poor_index",
            "airiq_pm25_fair_ugm3",
            "airiq_pm25_poor_ugm3",
            "airiq_pm25_very_poor_ugm3",
        ):
            self.assertIn(key, self.raw, key)

    def test_per_sensor_freshness_windows(self) -> None:
        # One arbitrary warm-up period for all sensors is forbidden: each
        # sensor gets its own window.
        for key in (
            "airiq_co2_warmup_ms",
            "airiq_voc_warmup_ms",
            "airiq_nox_warmup_ms",
            "airiq_pm_warmup_ms",
            "airiq_co2_stale_ms",
            "airiq_voc_stale_ms",
            "airiq_nox_stale_ms",
            "airiq_pm_stale_ms",
        ):
            self.assertIn(key, self.raw, key)
        # Pressure has no production wiring (firmware/catalog drift): no
        # pressure freshness substitutions may exist.
        self.assertNotIn("airiq_pressure_warmup_ms", self.raw)
        self.assertNotIn("airiq_pressure_stale_ms", self.raw)

    def test_no_roomiq_raw_sensor_reads(self) -> None:
        # RoomIQ integration honesty: AirIQ never re-reads raw RoomIQ
        # sensors (the SGP41 compensation stays SCD41-sourced at the board
        # layer; canonical RoomIQ values would be consumed via their
        # canonical ids only).
        for raw_id in (
            "comfort_ceiling_temperature",
            "comfort_ceiling_humidity",
            "comfort_ceiling_illuminance",
        ):
            self.assertNotIn(raw_id, self.raw, raw_id)


# --- Engine header ------------------------------------------------------------------


class EngineHeaderTests(unittest.TestCase):
    def setUp(self) -> None:
        if not HEADER.is_file():
            self.skipTest("engine header not implemented yet")
        self.raw = HEADER.read_text()

    def test_namespace_and_engine(self) -> None:
        self.assertIn("namespace sense360", self.raw)
        self.assertIn("namespace airiq", self.raw)
        self.assertIn("class AirIQEngine", self.raw)

    def test_state_strings_are_single_sourced(self) -> None:
        for value in SEVERITY_STRINGS + RECOMMENDATION_STRINGS + HEALTH_STRINGS:
            self.assertIn(f'"{value}"', self.raw, value)

    def test_worst_pollutant_model(self) -> None:
        lowered = self.raw.lower()
        self.assertIn("worst", lowered)
        # A blended / averaged proprietary score is rejected by accepted
        # owner decision 4.
        self.assertNotIn("weighted average", lowered)

    def test_pressure_is_not_a_pollutant(self) -> None:
        self.assertNotIn("POLLUTANT_PRESSURE", self.raw)

    def test_mics_channels_are_diagnostic_only(self) -> None:
        # MiCS is included in the architecture (accepted owner decision 8)
        # as diagnostic-only channels: inputs exist, but no MiCS pollutant
        # slot exists until calibration evidence lands.
        self.assertIn("input_mics_reducing", self.raw)
        self.assertIn("input_mics_oxidising", self.raw)
        self.assertNotIn("POLLUTANT_CO,", self.raw)
        self.assertNotIn("POLLUTANT_NO2", self.raw)
        self.assertNotIn("POLLUTANT_MICS", self.raw)

    def test_no_hardware_validation_claim(self) -> None:
        self.assertIn("Nothing in this header claims hardware validation", self.raw)

    def test_index_outputs_documented_as_relative(self) -> None:
        lowered = self.raw.lower()
        self.assertIn("relative", lowered)
        self.assertIn("index", lowered)

    def test_engine_supports_configuration_driven_expectations(self) -> None:
        self.assertIn("set_expected", self.raw)


# --- Simulation --------------------------------------------------------------------


class SimulationTests(unittest.TestCase):
    def test_simulation_tests_exist(self) -> None:
        self.assertTrue(CPP_TEST.is_file(), f"missing {CPP_TEST}")

    def test_simulation_covers_required_scenarios(self) -> None:
        if not CPP_TEST.is_file():
            self.skipTest("cpp test not implemented yet")
        raw = CPP_TEST.read_text().lower()
        for needle in (
            "warm",
            "stale",
            "worst",
            "recover",
            "boundary",
            "expected",
            "hcho",
            "ozone",
            "mics",
            "pressure",
            "recommendation",
            "invalid",
            "partial",
        ):
            self.assertIn(needle, raw, needle)

    def test_simulation_is_logic_proof_only(self) -> None:
        if not CPP_TEST.is_file():
            self.skipTest("cpp test not implemented yet")
        raw = CPP_TEST.read_text()
        self.assertIn("LOGIC/SIMULATION proof only", raw)

    def test_simulation_uses_the_production_header(self) -> None:
        if not CPP_TEST.is_file():
            self.skipTest("cpp test not implemented yet")
        raw = CPP_TEST.read_text()
        self.assertIn('#include "../../include/sense360/airiq_engine.h"', raw)


# --- Bundle wiring -------------------------------------------------------------------


class BundleWiringTests(unittest.TestCase):
    def test_airiq_bundle_authority_is_the_contract(self) -> None:
        bundles = airiq_bundles()
        self.assertGreaterEqual(len(bundles), 4)
        for bundle in bundles:
            self.assertTrue(bundle.is_file(), bundle)

    def test_airiq_bundles_compose_the_framework_exactly_once(self) -> None:
        for bundle in airiq_bundles():
            raw = bundle.read_text()
            self.assertEqual(
                raw.count(FRAMEWORK_INCLUDE),
                1,
                f"{bundle.name} must compose the AirIQ framework exactly once",
            )

    def test_airiq_bundles_drop_the_legacy_profile(self) -> None:
        # Composing both would duplicate the air_quality_state id and the
        # MQTT block.
        for bundle in airiq_bundles():
            raw = bundle.read_text()
            for legacy in LEGACY_PROFILE_INCLUDES:
                self.assertNotIn(
                    f"features/{legacy}",
                    raw,
                    f"{bundle.name} must not also compose {legacy}",
                )

    def test_airiq_bundles_never_compose_legacy_threshold_packages(self) -> None:
        for bundle in airiq_bundles():
            raw = bundle.read_text()
            for legacy in LEGACY_THRESHOLD_PACKAGES:
                self.assertNotIn(f"features/{legacy}", raw, bundle.name)

    def test_non_airiq_bundles_gain_nothing(self) -> None:
        for bundle in non_airiq_bundles():
            if not bundle.is_file():
                continue
            raw = bundle.read_text()
            self.assertNotIn(
                "airiq_framework.yaml",
                raw,
                f"{bundle.name} must not gain the AirIQ framework",
            )

    def test_airiq_bundles_keep_the_board_composition(self) -> None:
        for bundle in airiq_bundles():
            raw = bundle.read_text()
            self.assertIn("packages/boards/s360-210-airiq.yaml", raw, bundle.name)

    def test_legacy_include_paths_still_resolve(self) -> None:
        # Legacy shim products (products/sense360-core-ceiling.yaml,
        # compile-only skeletons) pin the legacy profile paths; they must
        # keep resolving with pre-framework behaviour (MQTT + placeholder).
        self.assertTrue(LEGACY_PROFILE.is_file())
        raw = LEGACY_PROFILE.read_text()
        self.assertIn("air_quality_state", raw)
        alias = REPO_ROOT / "packages" / "features" / "airiq_mqtt_profile.yaml"
        self.assertTrue(alias.is_file())


# --- Core framework contract ----------------------------------------------------------


class CoreFrameworkContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = json.loads(CONTRACT.read_text())

    def test_airiq_capability_names_the_framework(self) -> None:
        description = self.contract["capabilities"]["airiq"]["description"]
        self.assertIn("AIRIQ-FRAMEWORK-001", description)
        self.assertIn("packages/features/airiq_framework.yaml", description)

    def test_airiq_module_runtime_status_declared(self) -> None:
        runtime = self.contract.get("module_runtime_status") or {}
        self.assertIn("airiq", runtime, "airiq must be a wired runtime module")
        entry = runtime["airiq"]
        self.assertEqual(entry["work_item"], "AIRIQ-FRAMEWORK-001")
        self.assertEqual(entry["entity_id"], "s360_module_status_airiq")
        self.assertEqual(entry["package"], "packages/features/airiq_framework.yaml")
        self.assertEqual(tuple(entry["values"]), HEALTH_STRINGS)
        definition = entry["available_definition"]
        # Available is data-service availability only — never accuracy,
        # calibration correctness or hardware health.
        self.assertIn("NOT", definition)
        for honest in ("accuracy", "hardware"):
            self.assertIn(honest, definition)
        notes = entry.get("notes", "")
        for needle in ("SPS30", "BMP390", "MICS-4514", "drift", "opt"):
            self.assertIn(needle, notes + definition, needle)

    def test_airiq_contract_separates_pcb_from_external_attachments(self) -> None:
        # Machine-readable separation: PCB-mounted sensors and external
        # attachments are distinct fields, and external-attachment
        # membership (SPS30, SEN0321/ZE27-O3) is opt-in per composition.
        runtime = self.contract.get("module_runtime_status") or {}
        entry = runtime.get("airiq") or {}
        pcb = entry.get("pcb_mounted_sensors") or []
        self.assertTrue(any("SCD41" in item for item in pcb))
        self.assertTrue(any("SGP41" in item for item in pcb))
        self.assertTrue(any("MICS-4514" in item for item in pcb))
        external = entry.get("external_attachments") or {}
        self.assertIn("SPS30", external)
        self.assertTrue(any("SEN0321" in key for key in external))
        sps30 = external["SPS30"]
        for needle in ("j2", "not declared", "expected=false", "opt"):
            self.assertIn(needle, sps30.lower(), needle)
        # No sensor may appear on both sides of the separation.
        for key in external:
            token = key.split()[0]
            self.assertFalse(
                any(token in item for item in pcb),
                f"{token} listed both PCB-mounted and external",
            )

    def test_presence_and_roomiq_runtime_entries_unchanged(self) -> None:
        runtime = self.contract.get("module_runtime_status") or {}
        self.assertEqual(
            runtime.get("presence", {}).get("work_item"), "PRESENCE-FRAMEWORK-001"
        )
        self.assertEqual(
            runtime.get("roomiq", {}).get("work_item"), "ROOMIQ-FRAMEWORK-001"
        )


# --- Compile lane -----------------------------------------------------------------------


class CompileLaneTests(unittest.TestCase):
    def setUp(self) -> None:
        self.raw = COMPILE_WORKFLOW.read_text()

    def test_matrix_covers_the_required_airiq_composition(self) -> None:
        self.assertIn("Ceiling-POE-AirIQ-RoomIQ", self.raw)
        self.assertIn("products/sense360-ceiling-poe-airiq-roomiq.yaml", self.raw)

    def test_matrix_keeps_release_one_and_led_regressions(self) -> None:
        self.assertIn("Ceiling-POE-VentIQ-RoomIQ", self.raw)
        self.assertIn("Ceiling-POE-RoomIQ-LED", self.raw)

    def test_matrix_keeps_a_non_airiq_regression_target(self) -> None:
        # A framework-bearing product WITHOUT the airiq capability proves
        # the AirIQ service never leaks outside AirIQ-bearing bundles.
        self.assertIn("Ceiling-POE-FanDAC", self.raw)

    def test_contract_gate_runs_airiq_tests(self) -> None:
        self.assertIn("python3 tests/test_airiq_framework.py", self.raw)

    def test_paths_cover_airiq_framework_surfaces(self) -> None:
        self.assertIn("tests/test_airiq_framework.py", self.raw)

    def test_lane_guarantees_unchanged(self) -> None:
        self.assertIn("permissions:", self.raw)
        self.assertIn("contents: read", self.raw)
        self.assertIn("uploads NO artifact", self.raw)

    def test_quick_validation_gate_runs_airiq_contract(self) -> None:
        raw = VALIDATE_WORKFLOW.read_text()
        self.assertIn("python3 tests/test_airiq_framework.py", raw)


# --- Documentation ------------------------------------------------------------------------


class DocumentationTests(unittest.TestCase):
    def setUp(self) -> None:
        if not DOC.is_file():
            self.skipTest("architecture doc not written yet")
        self.text = DOC.read_text()
        self.lowered = self.text.lower()
        self.normalised = " ".join(self.lowered.split())

    def test_doc_exists_and_names_the_work_item(self) -> None:
        self.assertIn("AIRIQ-FRAMEWORK-001", self.text)

    def test_sensor_authority_matrix_documented(self) -> None:
        # The complete authoritative sensor stack, including the sensors
        # that are NOT compiled — nothing silently dropped.
        for needle in (
            "SCD41",
            "SGP41",
            "MICS-4514",
            "STM8",
            "SPS30",
            "SFA40",
            "BMP390",
            "ZE07",
            "ZE27",
        ):
            self.assertIn(needle, self.text, needle)

    def test_no_base_pro_axis_and_flat_taxonomy_documented(self) -> None:
        self.assertIn("flat", self.lowered)
        self.assertIn("base", self.lowered)  # the finding must be discussed
        self.assertIn("pro", self.lowered)

    def test_sensor_identity_conflicts_reported(self) -> None:
        # BMP390 compiled at 0x77 = firmware/catalog drift (no pressure
        # part on the verified schematic / BOM / catalog); SFA40 footprint
        # vs population conflict; MiCS STM8 interface unverified.
        self.assertIn("0x77", self.text)
        self.assertIn("BOM", self.text)
        self.assertIn("drift", self.lowered)
        self.assertIn("ENTITY-FILL-210-MICS-001", self.text)
        self.assertIn("ENTITY-FILL-210-HCHO-001", self.text)
        self.assertIn("HW-PINMAP-210-FOLLOWUP", self.text)

    def test_five_fitment_layers_recorded_separately(self) -> None:
        # The audit layers must never be conflated: PCB footprint present,
        # component populated in the production assembly, external
        # connector-supported, firmware driver compiled, and customer
        # functionality are recorded separately per sensor.
        for needle in (
            "footprint",
            "populated",
            "connector",
            "compiled",
            "customer",
        ):
            self.assertIn(needle, self.lowered, needle)

    def test_external_interfaces_recorded(self) -> None:
        # SPS30 is external connector-attached (J2); the SEN0321 (ZE27-O3)
        # ozone input is an external sensor/interface into the STM8 stage
        # per the verified schematic.
        self.assertIn("J2", self.text)
        self.assertIn("SEN0321", self.text)

    def test_sps30_inclusion_audit_documented(self) -> None:
        # The SPS30 commercial-inclusion audit and its outcome (unproven
        # -> safe opt-in model) must be documented, including the exact
        # SOT/product follow-up needed to declare a fitted attachment.
        self.assertIn("opt-in", self.lowered)
        self.assertIn("unproven", self.lowered)
        self.assertIn("kit", self.lowered)
        self.assertIn("optional", self.lowered)

    def test_state_vocabularies_documented(self) -> None:
        for value in SEVERITY_STRINGS + RECOMMENDATION_STRINGS:
            self.assertIn(value, self.text, value)

    def test_thresholds_documented_as_provisional_heuristics(self) -> None:
        self.assertIn("provisional", self.lowered)
        self.assertIn("heuristic", self.lowered)
        # PM2.5 band attribution without a compliance claim.
        self.assertIn("EPA", self.text)

    def test_indices_documented_as_relative(self) -> None:
        self.assertIn("relative", self.lowered)

    def test_mics_promotion_evidence_documented(self) -> None:
        self.assertIn("promotion", self.lowered)
        self.assertIn("MICS-4514", self.text)

    def test_worst_pollutant_model_documented(self) -> None:
        self.assertIn("worst", self.lowered)
        self.assertIn("pressure", self.lowered)

    def test_roomiq_reuse_documented(self) -> None:
        self.assertIn("RoomIQ", self.text)
        self.assertIn("compensation", self.lowered)

    def test_downstream_reuse_documented(self) -> None:
        for needle in ("VentIQ", "Pure", "Home Assistant", "Zones"):
            self.assertIn(needle, self.text, needle)

    def test_no_forbidden_claims(self) -> None:
        scrubbed = (
            self.normalised.replace("never medical", "")
            .replace("not medical", "")
            .replace("no medical", "")
            .replace("never a medical", "")
        )
        self.assertNotIn("medical", scrubbed)
        for forbidden in (
            "hardware verified",
            "bench verified",
            "certified",
            "complies with",
            "regulatory compliance is",
            "health protection",
            "prevents mould",
            "prevents mold",
            "prevents disease",
        ):
            self.assertNotIn(forbidden, self.normalised, forbidden)

    def test_compatibility_documented(self) -> None:
        self.assertIn("air_quality_state", self.text)
        self.assertIn("mqtt", self.lowered)


# --- Bench checklist -------------------------------------------------------------------------


class BenchChecklistTests(unittest.TestCase):
    def test_checklist_prepared_without_results(self) -> None:
        self.assertTrue(CHECKLIST.is_file(), f"missing {CHECKLIST}")
        text = CHECKLIST.read_text()
        lowered = text.lower()
        for topic in (
            "co2",
            "sgp41 conditioning",
            "mics",
            "heater",
            "baseline",
            "stm8",
            "sps30",
            "formaldehyde",
            "ozone",
            "pressure",
            "disconnect",
            "recovery",
            "stale",
            "air quality",
            "recommendation",
            "worst",
            "home assistant",
            "thermal",
            "airflow",
            "reference",
        ):
            self.assertIn(topic, lowered, topic)
        # Prepared, not executed: unchecked boxes only, no results, no
        # machine-written attestation (standing rule).
        self.assertIn("[ ]", text)
        self.assertNotIn("[x]", lowered)
        self.assertIn("no results", lowered)


# --- Roadmap ------------------------------------------------------------------------------------


class RoadmapTests(unittest.TestCase):
    def test_roadmap_records_airiq_framework(self) -> None:
        text = ROADMAP.read_text()
        self.assertIn("AIRIQ-FRAMEWORK-001", text)
        start = text.index("## ")
        section_start = text.index("AIRIQ-FRAMEWORK-001")
        section = text[section_start:][:11000]
        lowered = section.lower()
        self.assertIn("software foundation", lowered)
        self.assertIn("pending", lowered)
        self.assertIn("SOT", section)
        self.assertIn("AIRIQ-FRAMEWORK-BENCH-001", section)
        # Unresolved reconciliations stay tracked, and the BMP390 pressure
        # driver is recorded as firmware/catalog drift, never product
        # hardware.
        self.assertIn("MICS-4514", section)
        self.assertIn("BMP390", section)
        self.assertIn("drift", lowered)
        self.assertIn("SEN0321", section)
        self.assertIn("HW-PINMAP-210-FOLLOWUP", section)
        # SPS30 posture: external attachment, inclusion unproven, opt-in.
        self.assertIn("SPS30", section)
        self.assertIn("opt-in", lowered)
        self.assertGreater(section_start, start)


# --- AIRIQ-HW-RECONCILE-001 hardware-reconciliation proofs ------------------


class HardwareReconcileProofTests(unittest.TestCase):
    """The explicit proofs for AIRIQ-HW-RECONCILE-001: the canonical board
    package matches the fitted S360-210-R4 hardware."""

    def setUp(self) -> None:
        self.board_raw = BOARD_PACKAGE.read_text()
        self.board = load_yaml(BOARD_PACKAGE)

    def _all_ids(self, doc: Dict[str, Any]) -> List[str]:
        ids: List[str] = []
        for platform in ENTITY_PLATFORM_KEYS + ("mics_stm8",):
            block = doc.get(platform)
            if isinstance(block, dict):
                if isinstance(block.get("id"), str):
                    ids.append(block["id"])
                continue
            for entry in block or []:
                if isinstance(entry, dict):
                    if isinstance(entry.get("id"), str):
                        ids.append(entry["id"])
                    for sub in entry.values():
                        if isinstance(sub, dict) and isinstance(sub.get("id"), str):
                            ids.append(sub["id"])
        return ids

    # 1 + 2: no BMP390 driver / ids / substitutions in the canonical base.
    def test_no_bmp3xx_and_no_bmp390_ids_or_subs(self) -> None:
        # The driver is not instantiated (a comment may still explain the
        # removal), and no BMP390/pressure id or substitution survives.
        self.assertNotIn("platform: bmp3xx_i2c", self.board_raw)
        self.assertNotIn("address: 0x77", self.board_raw)
        lowered = self.board_raw.lower()
        self.assertNotIn("bmp390_sensor", lowered)
        self.assertNotIn("airiq_bmp390", lowered)
        self.assertNotIn("airiq_pressure", lowered)
        subs = self.board.get("substitutions") or {}
        for key in subs:
            self.assertNotIn("bmp390", key.lower())
            self.assertNotIn("pressure", key.lower())

    # 3: no SPS30 instantiation in the canonical base.
    def test_canonical_base_does_not_instantiate_sps30(self) -> None:
        self.assertNotIn("platform: sps30", self.board_raw)
        self.assertNotIn("address: 0x69", self.board_raw)

    # 4: SPS30 remains available through an explicit opt-in package.
    def test_sps30_available_through_opt_in_overlay(self) -> None:
        self.assertTrue(SPS30_OVERLAY.is_file())
        overlay = SPS30_OVERLAY.read_text()
        self.assertIn("platform: sps30", overlay)
        self.assertIn("address: 0x69", overlay)
        self.assertIn('airiq_expected_pm: "true"', overlay)

    # 5: SGP41 + SCD41 present.
    def test_canonical_includes_sgp41_and_scd41(self) -> None:
        self.assertIn("platform: sgp4x", self.board_raw)
        self.assertIn("address: 0x59", self.board_raw)
        self.assertIn("platform: scd4x", self.board_raw)
        self.assertIn("address: 0x62", self.board_raw)

    # 6: SFA40 support.
    def test_canonical_includes_sfa40(self) -> None:
        self.assertIn("platform: sfa40", self.board_raw)
        self.assertIn("address: 0x5D", self.board_raw)
        self.assertIn("formaldehyde:", self.board_raw)

    # 7: MICS/STM8 bridge at 0x60.
    def test_canonical_includes_mics_stm8_bridge_at_0x60(self) -> None:
        self.assertIn("mics_stm8:", self.board_raw)
        self.assertIn("address: 0x60", self.board_raw)

    # 8: STM8 extended protocol identity/register handling present.
    def test_stm8_protocol_identity_and_registers_present(self) -> None:
        header = (MICS_COMPONENT / "mics_stm8.h").read_text()
        source = (MICS_COMPONENT / "mics_stm8.cpp").read_text()
        self.assertIn("'M'", header)
        self.assertIn("'4'", header)
        self.assertIn("MICS_STM8_PROTOCOL_VERSION", header)
        self.assertIn("0x24", header)  # firmware
        self.assertIn("0xFE", header)  # command register
        self.assertIn("MICS_STM8_REG_BLOCK_LEN = 24", header)
        for token in ("WARMING", "CALIBRATED", "HEATER_ON", "baseline", "fault_flags"):
            self.assertIn(token, source)

    # 9: a missing optional SPS30 never marks base AirIQ hardware failed.
    def test_missing_sps30_does_not_degrade_base(self) -> None:
        subs = load_yaml(FRAMEWORK_PACKAGE).get("substitutions") or {}
        self.assertEqual(str(subs.get("airiq_expected_pm")).lower(), "false")
        self.assertNotIn("input_pm2_5", FRAMEWORK_PACKAGE.read_text())

    # 11: legacy aliases resolve to the corrected implementation.
    def test_legacy_alias_resolves_to_corrected_board(self) -> None:
        alias = REPO_ROOT / "packages" / "expansions" / "airiq_ceiling.yaml"
        raw = alias.read_text()
        self.assertIn("boards/s360-210-airiq.yaml", raw)
        self.assertNotIn("platform: bmp3xx_i2c", raw)
        self.assertNotIn("platform: sps30", raw)

    # 12: no duplicate ids, no duplicate I2C bus declaration.
    def test_no_duplicate_ids_or_i2c_bus(self) -> None:
        ids = self._all_ids(self.board)
        self.assertEqual(len(ids), len(set(ids)), f"duplicate id in board: {ids}")
        self.assertNotIn("i2c:", self.board_raw)  # references the shared Core bus
        overlay = SPS30_OVERLAY.read_text()
        self.assertNotIn("i2c:", overlay)
        # existing PM ids are preserved via !extend, never redefined.
        self.assertIn("!extend s360_pm2_5", overlay)


class ExternalComponentStructureTests(unittest.TestCase):
    def test_sfa40_component_files_exist(self) -> None:
        for name in ("__init__.py", "sensor.py", "sfa40.h", "sfa40.cpp"):
            self.assertTrue((SFA40_COMPONENT / name).is_file(), name)

    def test_sfa40_uses_datasheet_commands(self) -> None:
        cpp = (SFA40_COMPONENT / "sfa40.cpp").read_text()
        self.assertIn("0x00AC", cpp)  # start_continuous_measurement
        self.assertIn("0xC0EB", cpp)  # read_measurement

    def test_mics_component_files_exist(self) -> None:
        for name in ("__init__.py", "mics_stm8.h", "mics_stm8.cpp"):
            self.assertTrue((MICS_COMPONENT / name).is_file(), name)

    def test_board_loads_local_external_components(self) -> None:
        raw = BOARD_PACKAGE.read_text()
        self.assertIn("external_components:", raw)
        self.assertIn("type: local", raw)
        self.assertIn("[sfa40, mics_stm8]", raw)


class SPS30OverlayTests(unittest.TestCase):
    def setUp(self) -> None:
        if not SPS30_OVERLAY.is_file():
            self.skipTest("SPS30 overlay not implemented yet")
        self.raw = SPS30_OVERLAY.read_text()
        self.doc = load_yaml(SPS30_OVERLAY)

    def test_overlay_feeds_engine_pm_channels(self) -> None:
        for needle in ("input_pm2_5", "input_pm1", "input_pm4", "input_pm10"):
            self.assertIn(needle, self.raw, needle)

    def test_overlay_reenables_pm_customer_entities(self) -> None:
        for pm in ("s360_pm2_5", "s360_pm1", "s360_pm4", "s360_pm10"):
            self.assertIn(f"!extend {pm}", self.raw)

    def test_overlay_opts_in_expected_pm(self) -> None:
        subs = self.doc.get("substitutions") or {}
        self.assertEqual(str(subs.get("airiq_expected_pm")).lower(), "true")


if __name__ == "__main__":
    unittest.main(verbosity=2)

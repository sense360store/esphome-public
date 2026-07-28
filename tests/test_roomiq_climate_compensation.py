#!/usr/bin/env python3
"""S360-200-R4-CLIMATE-COMPENSATION-001 — RoomIQ climate compensation contract.

The S360-200 R4 board reads hot and dry. This work item moves the validated
provisional correction out of hand-entered customer offsets and into ONE
built-in, named, versioned board profile consumed by every S360-200 R4
composition.

What these tests pin:

* the compensation model lives in exactly ONE pure, ESPHome-free header
  (``components/sense360/roomiq_climate_compensation.h``), consumed by the RoomIQ
  engine and by native tests — never duplicated in the engine, a package, a
  bundle, a product or customer YAML;
* the named profile ``S360_200_R4_CLIMATE_PROFILE_V1`` carries the SKU, the
  revision, the -5.80 °C temperature correction, the +4.52 %RH residual and —
  inseparably — its validated-provisional evidence level;
* the humidity model is vapour-pressure preserving (Magnus / psychrometric),
  never a fixed additive offset;
* SHT45 samples are paired coherently before humidity is treated as fresh;
* the raw SHT45 driver contract (platform / address / bus / ids / precision)
  is unchanged, and the heater is now EXPLICITLY off;
* the BMP581 die temperature stays diagnostic-only and is never an input;
* the customer entity contract (ids, canonical compensated values, calibration
  neutral at zero) holds, with a one-time persisted calibration-schema
  migration so a pre-compensation manual offset cannot double-correct;
* documentation supersedes the old "-7.7 °C / +17 %RH" manual bench
  instructions and states the evidence level honestly;
* presence implementation files are untouched by this work item.

Firmware / simulation proof only. No hardware, bench, multi-unit, compliance
or commercial claim is made or implied anywhere in this file.

Uses Python's stdlib unittest (repo convention). Run with::

    python3 tests/test_roomiq_climate_compensation.py
"""

from __future__ import annotations

import math
import re
import unittest
from pathlib import Path
from typing import Any, Dict

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

COMPENSATION_HEADER = (
    REPO_ROOT / "components" / "sense360" / "roomiq_climate_compensation.h"
)
ENGINE_HEADER = REPO_ROOT / "components" / "sense360" / "roomiq_engine.h"
FRAMEWORK_PACKAGE = REPO_ROOT / "packages" / "features" / "roomiq_framework.yaml"
CLIMATE_BOARD = REPO_ROOT / "packages" / "boards" / "s360-200-roomiq-climate.yaml"
ROOMIQ_BOARD = REPO_ROOT / "packages" / "boards" / "s360-200-roomiq.yaml"
COMPENSATION_CPP_TEST = (
    REPO_ROOT / "tests" / "unit" / "test_roomiq_climate_compensation.cpp"
)
ENGINE_CPP_TEST = REPO_ROOT / "tests" / "unit" / "test_roomiq_engine.cpp"
ARCHITECTURE_DOC = REPO_ROOT / "docs" / "architecture" / "sense360-roomiq-framework.md"
RUNTIME_DOC = REPO_ROOT / "docs" / "hardware" / "s360-200-r4-presence-runtime.md"

PRESENCE_FILES = (
    REPO_ROOT / "packages" / "boards" / "s360-200-roomiq-radar.yaml",
    REPO_ROOT / "packages" / "boards" / "s360-200-roomiq-pir.yaml",
    REPO_ROOT / "packages" / "boards" / "s360-200-roomiq-sen0609.yaml",
    REPO_ROOT / "packages" / "boards" / "s360-200-roomiq-uart.yaml",
    REPO_ROOT / "packages" / "features" / "presence_framework.yaml",
    REPO_ROOT / "components" / "sense360" / "presence_fusion.h",
)

PROFILE_ID = "S360_200_R4_CLIMATE_PROFILE_V1"
TEMPERATURE_CORRECTION_C = -5.80
HUMIDITY_RESIDUAL_PCT = 4.52

# Claim-shaped phrases that would overstate the evidence. The profile is
# validated on ONE board; nothing may read as multi-unit, production,
# certification or compliance proof. (Stating that such validation remains
# OUTSTANDING is required, and is deliberately not matched here.)
FORBIDDEN_VALIDATION_CLAIMS = (
    "production validated",
    "production-validated",
    "validated on several",
    "validated across",
    "validated in production",
    "multi-unit validated",
    "certified",
    "compliance proven",
    "factory calibrated to spec",
)

# Superseded manual bench corrections. They were a temporary hand-entered
# workaround for exactly the error the built-in profile now corrects, so no
# document may still instruct an operator to enter them.
SUPERSEDED_OFFSET_PATTERNS = (
    re.compile(r"Temperature Offset[^.\n]*?-\s*7\.7", re.IGNORECASE),
    re.compile(r"Humidity Offset[^.\n]*?\+\s*17", re.IGNORECASE),
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


def without_comments(raw: str) -> str:
    """Drop whole-line YAML comments.

    Explanatory prose is welcome (and is where the rationale belongs); what
    must never appear is a constant or a formula the firmware actually uses.
    """
    return "\n".join(
        line for line in raw.splitlines() if not line.lstrip().startswith("#")
    )


def entities_by_id(doc: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for platform in ("sensor", "binary_sensor", "text_sensor", "number", "select"):
        for entry in doc.get(platform) or []:
            if isinstance(entry, dict) and isinstance(entry.get("id"), str):
                out[entry["id"]] = dict(entry, _platform=platform)
    return out


# --- Reference implementation of the documented model ------------------------
# Written independently from the C++ so a silent formula change in the header
# is caught here too (the C++ vectors live in the native test).


def _svp(temperature_c: float) -> float:
    return 6.112 * math.exp((17.62 * temperature_c) / (243.12 + temperature_c))


def reference_model(
    raw_temperature_c: float,
    raw_humidity_pct: float,
    customer_temperature_offset_c: float = 0.0,
    customer_humidity_offset_pct: float = 0.0,
):
    final_temperature = (
        raw_temperature_c + TEMPERATURE_CORRECTION_C + customer_temperature_offset_c
    )
    actual_vapour_pressure = (raw_humidity_pct / 100.0) * _svp(raw_temperature_c)
    psychrometric = 100.0 * actual_vapour_pressure / _svp(final_temperature)
    final_humidity = (
        psychrometric + HUMIDITY_RESIDUAL_PCT + customer_humidity_offset_pct
    )
    return final_temperature, min(max(final_humidity, 0.0), 100.0)


# --- One authoritative implementation ---------------------------------------


class SingleImplementationTests(unittest.TestCase):
    def test_compensation_header_exists_and_is_esphome_free(self) -> None:
        self.assertTrue(
            COMPENSATION_HEADER.is_file(),
            "the compensation model must live in one focused helper header",
        )
        raw = COMPENSATION_HEADER.read_text()
        # No ESPHome / Arduino dependency: the model must be exercisable by
        # native tests and movable behind a `sense360_roomiq` external
        # component later without any behaviour change.
        for forbidden in ("esphome/", "esphome.h", "Arduino.h", "#include <Arduino"):
            self.assertNotIn(forbidden, raw, forbidden)
        self.assertIn("namespace sense360", raw)
        self.assertIn("namespace roomiq", raw)

    def test_engine_consumes_the_helper_and_does_not_restate_the_formula(
        self,
    ) -> None:
        raw = ENGINE_HEADER.read_text()
        self.assertIn('#include "roomiq_climate_compensation.h"', raw)
        self.assertIn("compensate_climate(", raw)
        self.assertIn("compensate_temperature_c(", raw)
        # The Magnus constants must appear ONLY in the helper.
        for constant in ("6.112", "17.62", "243.12"):
            self.assertNotIn(
                constant,
                raw,
                f"{constant} belongs to the compensation helper, not the engine",
            )
        # The profile constants must not be restated as engine literals.
        for constant in ("5.80f", "4.52f"):
            self.assertNotIn(constant, raw, constant)

    def test_no_product_package_or_bundle_duplicates_the_model(self) -> None:
        # The formula and its constants must never leak into YAML: products and
        # customer configs compose behaviour, they do not restate physics.
        searched = 0
        for directory in ("products", "packages", "examples"):
            for path in sorted((REPO_ROOT / directory).rglob("*.yaml")):
                if ".esphome" in path.parts:
                    continue  # local build scratch, never repository source
                searched += 1
                raw = without_comments(path.read_text())
                for token in ("17.62", "243.12", "6.112", "5.80", "4.52"):
                    self.assertNotIn(
                        token,
                        raw,
                        f"{path.relative_to(REPO_ROOT)} must not duplicate the "
                        f"climate compensation constant {token} — the profile "
                        "lives in components/sense360/roomiq_climate_compensation.h",
                    )
                for token in ("saturation_vapour_pressure", "vapour_pressure ="):
                    self.assertNotIn(token, raw, str(path))
        self.assertGreater(searched, 50, "YAML sweep found suspiciously few files")

    def test_native_tests_exercise_the_helper_directly(self) -> None:
        self.assertTrue(COMPENSATION_CPP_TEST.is_file())
        raw = COMPENSATION_CPP_TEST.read_text()
        self.assertIn("roomiq_climate_compensation.h", raw)
        # Deterministic, no-hardware claim.
        self.assertIn("never hardware validation", raw)


# --- The named, versioned board profile --------------------------------------


class ClimateProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = COMPENSATION_HEADER.read_text()

    def test_profile_is_named_and_versioned(self) -> None:
        self.assertIn(PROFILE_ID, self.raw)
        self.assertIn('"S360-200"', self.raw)
        self.assertIn('"R4"', self.raw)

    def test_profile_constants_and_signs(self) -> None:
        self.assertIn("-5.80f", self.raw)
        self.assertIn("4.52f", self.raw)
        # The temperature correction is negative (the board reads hot); the
        # humidity residual is positive.
        self.assertNotIn("+5.80f", self.raw)
        self.assertNotIn("-4.52f", self.raw)

    def test_profile_carries_its_evidence_level(self) -> None:
        self.assertIn("CLIMATE_EVIDENCE_VALIDATED_PROVISIONAL", self.raw)
        self.assertIn("validated-provisional", self.raw)
        lowered = self.raw.lower()
        # Honest scope: one tested board, multi-unit validation outstanding.
        self.assertIn("multi-unit", lowered)
        for forbidden in FORBIDDEN_VALIDATION_CLAIMS:
            self.assertNotIn(forbidden, lowered, forbidden)

    def test_engine_default_profile_is_the_s360_200_r4_profile(self) -> None:
        raw = ENGINE_HEADER.read_text()
        self.assertIn(f"climate_profile_ = &{PROFILE_ID}()", raw)


# --- The model itself (independent reference) --------------------------------


class ModelBehaviourTests(unittest.TestCase):
    def test_documented_reference_vectors(self) -> None:
        temperature, humidity = reference_model(30.0, 40.0)
        self.assertAlmostEqual(temperature, 24.2, places=4)
        self.assertAlmostEqual(humidity, 60.7351, places=3)

        temperature, humidity = reference_model(36.0, 24.8)
        self.assertAlmostEqual(temperature, 30.2, places=4)
        self.assertAlmostEqual(humidity, 38.8673, places=3)

    def test_humidity_is_not_a_fixed_additive_offset(self) -> None:
        # If humidity were "raw + constant" the delta would be identical at
        # every temperature. The psychrometric model makes it temperature
        # dependent — that is the whole point.
        delta_cool = reference_model(20.0, 45.0)[1] - 45.0
        delta_warm = reference_model(32.0, 45.0)[1] - 45.0
        self.assertGreater(abs(delta_warm - delta_cool), 1.0)

    def test_customer_temperature_calibration_moves_relative_humidity(self) -> None:
        neutral = reference_model(30.0, 40.0)[1]
        warmer = reference_model(30.0, 40.0, customer_temperature_offset_c=1.0)[1]
        cooler = reference_model(30.0, 40.0, customer_temperature_offset_c=-1.0)[1]
        self.assertLess(warmer, neutral)
        self.assertGreater(cooler, neutral)

    def test_customer_humidity_calibration_applies_once_at_the_end(self) -> None:
        base = reference_model(30.0, 40.0)[1]
        shifted = reference_model(30.0, 40.0, customer_humidity_offset_pct=5.0)[1]
        self.assertAlmostEqual(shifted - base, 5.0, places=4)

    def test_humidity_is_clamped_to_the_physical_range(self) -> None:
        self.assertEqual(reference_model(10.0, 99.0)[1], 100.0)
        self.assertEqual(
            reference_model(30.0, 1.0, customer_humidity_offset_pct=-10.0)[1], 0.0
        )


# --- Sample coherence --------------------------------------------------------


class SampleCoherenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.header = COMPENSATION_HEADER.read_text()
        cls.engine = ENGINE_HEADER.read_text()
        cls.package = FRAMEWORK_PACKAGE.read_text()

    def test_pairing_rule_has_one_authoritative_implementation(self) -> None:
        self.assertIn("class ClimateSamplePairer", self.header)
        self.assertIn("ClimateSamplePairer climate_pair_", self.engine)
        # The engine must not re-derive pairing with its own timestamps.
        self.assertNotIn("class ClimateSamplePairer", self.engine)

    def test_pair_skew_is_documented_and_configurable(self) -> None:
        self.assertIn("DEFAULT_CLIMATE_PAIR_SKEW_MS", self.header)
        self.assertIn("set_max_pair_skew_ms", self.header)
        self.assertIn("set_climate_pair_skew_ms", self.engine)
        # The production package passes a real value in.
        self.assertIn("roomiq_climate_pair_skew_ms", self.package)
        doc = load_yaml(FRAMEWORK_PACKAGE)
        skew = int(doc["substitutions"]["roomiq_climate_pair_skew_ms"])
        self.assertGreater(skew, 0)
        # Well below the 30 s SHT4x polling cycle, so a stale counterpart can
        # never pair with the next cycle.
        self.assertLess(skew, 30000)

    def test_rollover_safe_timestamp_arithmetic(self) -> None:
        self.assertIn("static uint32_t skew_ms(", self.header)
        self.assertIn("static uint32_t later_ms(", self.header)
        # The circular-distance form (min of both unsigned differences) is what
        # makes the comparison correct across the millisecond rollover.
        self.assertIn("forward < backward ? forward : backward", self.header)

    def test_unpaired_humidity_cannot_mark_humidity_fresh(self) -> None:
        # input_humidity only refreshes the channel when the pairer reports a
        # NEW coherent pair.
        self.assertIn(
            "if (!climate_pair_.input_humidity(now_ms, percent)) return;",
            self.engine,
        )

    def test_native_tests_cover_both_callback_orders_and_rollover(self) -> None:
        for cpp in (COMPENSATION_CPP_TEST, ENGINE_CPP_TEST):
            raw = cpp.read_text()
            self.assertIn("callback_order", raw, str(cpp))
            self.assertIn("rollover", raw, str(cpp))
            self.assertIn("skew", raw, str(cpp))


# --- Raw SHT45 driver contract ----------------------------------------------


class Sht45DriverContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = load_yaml(CLIMATE_BOARD)
        cls.raw = CLIMATE_BOARD.read_text()
        cls.entities = entities_by_id(cls.doc)

    def test_hardware_contract_unchanged(self) -> None:
        sht = self.entities["comfort_ceiling_sht4x"]
        self.assertEqual(sht.get("platform"), "sht4x")
        self.assertEqual(sht.get("address"), 0x44)
        self.assertEqual(sht.get("i2c_id"), "${comfort_ceiling_i2c_id}")
        self.assertEqual(sht.get("precision"), "High")
        # The raw source ids the framework consumes are a preserved contract.
        self.assertEqual(sht["temperature"]["id"], "comfort_ceiling_temperature")
        self.assertEqual(sht["humidity"]["id"], "comfort_ceiling_humidity")
        self.assertTrue(sht["temperature"].get("internal"))
        self.assertTrue(sht["humidity"].get("internal"))

    def test_heater_is_explicitly_disabled(self) -> None:
        sht = self.entities["comfort_ceiling_sht4x"]
        # The supported explicit-disabled configuration: with a 0.0 duty the
        # pinned sht4x driver never computes a heater interval and never
        # issues a heater command.
        self.assertIn("heater_max_duty", sht)
        self.assertEqual(float(sht["heater_max_duty"]), 0.0)
        # The misleading bare heater_power (which selected a command that was
        # never sent) is gone.
        self.assertNotIn("heater_power", sht)
        # And no periodic heater operation is introduced by this work item.
        self.assertNotIn("heater_time", sht)

    def test_raw_sub_sensors_carry_no_compensation(self) -> None:
        sht = self.entities["comfort_ceiling_sht4x"]
        for key in ("temperature", "humidity"):
            for entry in sht[key].get("filters") or []:
                if isinstance(entry, dict):
                    for banned in ("offset", "multiply", "calibrate_linear", "lambda"):
                        self.assertNotIn(banned, entry, f"{key}: {banned}")

    def test_bmp581_temperature_stays_diagnostic_and_unused(self) -> None:
        bmp = self.entities["comfort_ceiling_bmp581"]
        temperature = bmp["temperature"]
        self.assertEqual(temperature["id"], "comfort_ceiling_bmp_temperature")
        self.assertEqual(temperature.get("entity_category"), "diagnostic")
        self.assertTrue(temperature.get("disabled_by_default"))
        # Nothing consumes it: no framework source substitution points at it,
        # and no engine input exists for a second temperature source.
        framework = FRAMEWORK_PACKAGE.read_text()
        self.assertNotIn("comfort_ceiling_bmp_temperature", framework)
        # The engine exposes exactly three sensor inputs, none of which is a
        # second temperature source, so the die temperature has nowhere to go.
        engine = ENGINE_HEADER.read_text()
        inputs = sorted(set(re.findall(r"void (input_\w+)\(", engine)))
        self.assertEqual(
            inputs, ["input_humidity", "input_lux", "input_temperature"], inputs
        )
        self.assertNotIn(
            "comfort_ceiling_bmp_temperature", COMPENSATION_HEADER.read_text()
        )

    def test_pressure_policy_unchanged(self) -> None:
        pressure = self.entities["comfort_ceiling_bmp581"]["pressure"]
        self.assertEqual(pressure["id"], "comfort_ceiling_pressure")
        self.assertEqual(pressure.get("unit_of_measurement"), "hPa")
        multipliers = [
            entry["multiply"]
            for entry in (pressure.get("filters") or [])
            if isinstance(entry, dict) and "multiply" in entry
        ]
        self.assertEqual(multipliers, [0.01])


# --- Customer contract -------------------------------------------------------


class CustomerContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = load_yaml(FRAMEWORK_PACKAGE)
        cls.raw = FRAMEWORK_PACKAGE.read_text()
        cls.entities = entities_by_id(cls.doc)

    def test_canonical_entity_ids_preserved(self) -> None:
        for entity_id in (
            "s360_temperature",
            "s360_humidity",
            "s360_temperature_offset",
            "s360_humidity_offset",
        ):
            self.assertIn(entity_id, self.entities, entity_id)

    def test_canonical_values_are_compensated_not_raw(self) -> None:
        # The canonical sensors are published from the engine (which applies
        # the profile), never copied from the raw board sensors.
        for entity_id in ("s360_temperature", "s360_humidity"):
            entity = self.entities[entity_id]
            self.assertEqual(entity.get("platform"), "template", entity_id)
            self.assertNotIn("source_id", entity, entity_id)
        self.assertIn(
            "publish_changed(id(s360_temperature), engine.temperature())", self.raw
        )
        self.assertIn("publish_changed(id(s360_humidity), engine.humidity())", self.raw)

    def test_presentation_precision(self) -> None:
        self.assertEqual(int(self.entities["s360_temperature"]["accuracy_decimals"]), 1)
        self.assertEqual(int(self.entities["s360_humidity"]["accuracy_decimals"]), 1)

    def test_calibration_controls_are_neutral_at_zero_and_persisted(self) -> None:
        for entity_id in ("s360_temperature_offset", "s360_humidity_offset"):
            entity = self.entities[entity_id]
            self.assertEqual(float(entity["initial_value"]), 0.0, entity_id)
            self.assertTrue(entity.get("restore_value"), entity_id)
            self.assertEqual(entity.get("entity_category"), "config", entity_id)

    def test_calibration_ranges_are_documented_as_retained_not_expected(self) -> None:
        # The protected ±15 °C / ±30 %RH stable contract is deliberately NOT
        # narrowed. Because it is now much wider than a normal post-factory
        # correction, the package must say so where the controls are defined.
        self.assertEqual(
            float(self.entities["s360_temperature_offset"]["min_value"]), -15.0
        )
        self.assertEqual(
            float(self.entities["s360_temperature_offset"]["max_value"]), 15.0
        )
        self.assertEqual(
            float(self.entities["s360_humidity_offset"]["min_value"]), -30.0
        )
        self.assertEqual(
            float(self.entities["s360_humidity_offset"]["max_value"]), 30.0
        )
        lowered = self.raw.lower()
        self.assertIn("compatibility", lowered)
        self.assertIn("should be small", lowered)

    def test_stale_data_publishes_unknown_never_a_frozen_value(self) -> None:
        # One publisher, publishing NaN (unknown) whenever the engine reports
        # the channel is no longer fresh.
        self.assertIn("publish_changed", self.raw)
        self.assertIn("std::isnan(current) && std::isnan(value)", self.raw)


# --- Diagnostics -------------------------------------------------------------


class DiagnosticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = load_yaml(FRAMEWORK_PACKAGE)
        cls.raw = FRAMEWORK_PACKAGE.read_text()
        cls.entities = entities_by_id(cls.doc)

    def test_raw_diagnostics_remain_raw(self) -> None:
        for entity_id, source in (
            ("s360_roomiq_raw_temperature", "${roomiq_temperature_source_id}"),
            ("s360_roomiq_raw_humidity", "${roomiq_humidity_source_id}"),
        ):
            entity = self.entities[entity_id]
            self.assertEqual(entity.get("platform"), "copy", entity_id)
            self.assertEqual(entity.get("source_id"), source, entity_id)
            self.assertIsNone(entity.get("filters"), entity_id)

    def test_factory_compensated_diagnostics_exist_and_are_disabled(self) -> None:
        for entity_id in (
            "s360_roomiq_factory_temperature",
            "s360_roomiq_factory_humidity",
        ):
            entity = self.entities[entity_id]
            self.assertEqual(entity.get("entity_category"), "diagnostic", entity_id)
            self.assertTrue(entity.get("disabled_by_default"), entity_id)
        self.assertIn("engine.factory_temperature()", self.raw)
        self.assertIn("engine.factory_humidity()", self.raw)

    def test_profile_and_evidence_diagnostic_exists(self) -> None:
        entity = self.entities["s360_roomiq_climate_profile"]
        self.assertEqual(entity["_platform"], "text_sensor")
        self.assertEqual(entity.get("entity_category"), "diagnostic")
        self.assertTrue(entity.get("disabled_by_default"))
        # It reports the profile identity, its constants AND its evidence
        # posture — the constants may never be published without the posture.
        self.assertIn("profile.id", self.raw)
        self.assertIn("climate_evidence_to_string", self.raw)
        self.assertIn("multi-unit", self.raw)

    def test_calibration_diagnostic_separates_every_contribution(self) -> None:
        entity = self.entities["s360_roomiq_calibration_state"]
        self.assertEqual(entity.get("entity_category"), "diagnostic")
        self.assertTrue(entity.get("disabled_by_default"))
        # factory profile · customer temperature · customer humidity ·
        # illuminance, all distinguishable in one line.
        for token in (
            '"factory %s',
            "customer temperature",
            "customer humidity",
            "illuminance x",
        ):
            self.assertIn(token, self.raw, token)

    def test_no_new_default_enabled_customer_entities(self) -> None:
        # Diagnostics must not become customer noise, and no internal formula
        # stage may be exposed by default.
        for entity_id in (
            "s360_roomiq_factory_temperature",
            "s360_roomiq_factory_humidity",
            "s360_roomiq_climate_profile",
            "s360_roomiq_calibration_schema_state",
        ):
            self.assertTrue(
                self.entities[entity_id].get("disabled_by_default"), entity_id
            )
        # Intermediate stages (vapour pressure, psychrometric humidity) are
        # never entities at all.
        for token in ("vapour_pressure", "psychrometric"):
            for entry in self.entities.values():
                self.assertNotIn(token, str(entry.get("name", "")).lower(), token)


# --- Persisted calibration migration ----------------------------------------


class CalibrationMigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = load_yaml(FRAMEWORK_PACKAGE)
        cls.raw = FRAMEWORK_PACKAGE.read_text()
        cls.entities = entities_by_id(cls.doc)

    def test_explicit_persisted_schema_marker(self) -> None:
        globals_ = {
            entry["id"]: entry
            for entry in (self.doc.get("globals") or [])
            if isinstance(entry, dict) and "id" in entry
        }
        marker = globals_["s360_roomiq_calibration_schema"]
        self.assertEqual(marker.get("type"), "int")
        self.assertTrue(marker.get("restore_value"))
        # A device that has never stored the marker (old schema OR clean
        # install) reads the neutral 0 and is migrated once.
        self.assertEqual(int(marker.get("initial_value")), 0)
        version = int(self.doc["substitutions"]["roomiq_calibration_schema_version"])
        self.assertGreater(version, 0)

    def test_migration_does_not_infer_from_the_stored_numbers(self) -> None:
        # A legitimate -7.7 °C is indistinguishable from a legacy one, so the
        # trigger must be the explicit marker only. (Prose explaining WHY may
        # mention the old values; the executable configuration may not test
        # them.)
        self.assertIn("s360_roomiq_calibration_schema", self.raw)
        executable = without_comments(self.raw)
        for guess in ("-7.7", "< -5", "> 10", "abs(id(s360_temperature_offset)"):
            self.assertNotIn(guess, executable, guess)

    def test_migration_resets_both_customer_controls_once(self) -> None:
        boot = [
            entry
            for entry in (self.doc.get("esphome") or {}).get("on_boot") or []
            if isinstance(entry, dict)
        ]
        migration = [entry for entry in boot if entry.get("priority") == 200]
        self.assertEqual(len(migration), 1, "exactly one migration boot hook")
        rendered = str(migration[0])
        self.assertIn("s360_temperature_offset", rendered)
        self.assertIn("s360_humidity_offset", rendered)
        # Reset to neutral, and stamp the marker so it runs exactly once.
        self.assertIn("number.set", self.raw)
        self.assertIn(
            "id(s360_roomiq_calibration_schema) =\n"
            "                      ${roomiq_calibration_schema_version};",
            self.raw,
        )

    def test_migration_runs_after_the_numbers_have_restored(self) -> None:
        # ESPHome number components set up at HARDWARE priority (800); the
        # migration hook must run later or it would be overwritten by the
        # restored values.
        priorities = [
            entry.get("priority")
            for entry in (self.doc.get("esphome") or {}).get("on_boot") or []
            if isinstance(entry, dict)
        ]
        self.assertIn(200, priorities)
        self.assertTrue(all(p < 800 for p in priorities if p is not None))

    def test_migration_is_visible_to_support(self) -> None:
        self.assertIn("logger.log", self.raw)
        entity = self.entities["s360_roomiq_calibration_schema_state"]
        self.assertEqual(entity["_platform"], "text_sensor")
        self.assertEqual(entity.get("entity_category"), "diagnostic")
        self.assertTrue(entity.get("disabled_by_default"))

    def test_no_factory_reset_is_required(self) -> None:
        # Nothing global is wiped: only the two customer climate calibration
        # controls are reset.
        for destructive in (
            "global_preferences->reset",
            "factory_reset",
            "button.press: factory",
        ):
            self.assertNotIn(destructive, self.raw, destructive)
        self.assertNotIn("s360_illuminance_scale\n                  value: 1", self.raw)


# --- Presence is untouched ---------------------------------------------------


class PresenceUnchangedTests(unittest.TestCase):
    def test_presence_files_carry_no_climate_compensation(self) -> None:
        for path in PRESENCE_FILES:
            self.assertTrue(path.is_file(), str(path))
            raw = path.read_text()
            for token in (
                PROFILE_ID,
                "roomiq_climate_compensation",
                "compensate_climate",
                "5.80",
                "4.52",
            ):
                self.assertNotIn(
                    token,
                    raw,
                    f"{path.relative_to(REPO_ROOT)} is presence scope and must "
                    "not change for this climate work item",
                )

    def test_roomiq_board_wrapper_still_composes_presence(self) -> None:
        doc = load_yaml(ROOMIQ_BOARD)
        packages = doc.get("packages") or {}
        self.assertEqual(
            packages.get("board_roomiq_radar"), "s360-200-roomiq-radar.yaml"
        )
        self.assertEqual(packages.get("board_roomiq_uart"), "s360-200-roomiq-uart.yaml")
        self.assertEqual(
            packages.get("board_roomiq_comfort"), "s360-200-roomiq-climate.yaml"
        )


# --- Documentation -----------------------------------------------------------


class DocumentationTests(unittest.TestCase):
    def test_superseded_manual_offsets_are_gone_from_operator_instructions(
        self,
    ) -> None:
        for doc in (ARCHITECTURE_DOC, RUNTIME_DOC):
            raw = doc.read_text()
            for pattern in SUPERSEDED_OFFSET_PATTERNS:
                # Historical narrative is allowed, but only where the text also
                # marks it superseded on the same line.
                for line in raw.splitlines():
                    if pattern.search(line):
                        self.assertTrue(
                            "supersede" in line.lower()
                            or "no longer" in line.lower()
                            or "historic" in line.lower(),
                            f"{doc.name}: '{line.strip()}' still reads as a live "
                            "instruction to enter the superseded manual offset",
                        )

    def test_architecture_doc_documents_the_current_model(self) -> None:
        raw = ARCHITECTURE_DOC.read_text()
        for token in ("5.80", "4.52", PROFILE_ID, "vapour pressure"):
            self.assertIn(token, raw, token)
        lowered = raw.lower()
        self.assertIn("neutral", lowered)

    def test_documentation_states_the_evidence_level_honestly(self) -> None:
        raw = ARCHITECTURE_DOC.read_text()
        lowered = raw.lower()
        self.assertIn("validated provisional", lowered)
        self.assertIn("multi-unit", lowered)
        for forbidden in FORBIDDEN_VALIDATION_CLAIMS:
            self.assertNotIn(forbidden, lowered, forbidden)

    def test_explanation_is_not_duplicated_across_permanent_context(self) -> None:
        # One authoritative home: the architecture doc. CLAUDE.md and the
        # standing invariants must not restate the model.
        for path in (
            REPO_ROOT / "CLAUDE.md",
            REPO_ROOT / "docs" / "standing-invariants.md",
        ):
            raw = path.read_text()
            for token in ("17.62", "243.12", "6.112", "4.52"):
                self.assertNotIn(
                    token,
                    raw,
                    f"{path.name} must not restate the compensation model — "
                    "the authoritative home is "
                    "docs/architecture/sense360-roomiq-framework.md",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)

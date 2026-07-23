#!/usr/bin/env python3
"""S360-200-R4-BMP581-001 contract lock.

Pins the fitted Bosch BMP581 barometric-pressure driver on the S360-200-R4
RoomIQ climate board against the verified schematic + BOM + runtime evidence:

  * schematic (docs/hardware/schematics/S360-200-R4.pdf, "Pressure Sensor
    BMP581"): U4 is a BMP581 in I2C mode on the SHARED I2C bus (I2C_SCL /
    I2C_SDA — the same nets as U1/U2), address strapped by JP1;
  * BOM (docs/hardware/artifacts/S360-200-R4.md, U4): MFR# BMP581 (Bosch) —
    NOT a BMP390/BMP3xx/BMP280;
  * address: JP1 default VDD strap -> 0x47, matching the runtime I2C scan.

The contract proven here:

  1. the BMP581 is configured on the correct ESPHome platform (bmp581_i2c);
  2. it uses the shared core_i2c bus and the verified address 0x47;
  3. a customer-facing atmospheric-pressure entity exists;
  4. the BMP581 die temperature is diagnostic / disabled-by-default only —
     SHT45 (U2) remains the canonical RoomIQ temperature;
  5. the reconciled canonical SHT45 temperature / humidity inputs are NOT
     altered by this slice, and the RoomIQ engine still binds them;
  6. the RoomIQ + Presence remote wrapper still composes the (now
     BMP581-bearing) climate half.

Live `esphome config` validation of a representative RoomIQ product (and a
representative `esphome compile`) is performed out-of-band during development
rather than in this committed suite: running the CLI in-tree fetches external
git components and writes a build cache into the repo, which pollutes the
"no stray YAML in bundles" and secret-posture guards. The structural
assertions below are hermetic (pure YAML parsing, no CLI, no network) and
fully pin the S360-200-R4-BMP581-001 contract.

Stdlib unittest only (repo convention); runnable directly or under pytest.
"""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

CLIMATE = REPO_ROOT / "packages" / "boards" / "s360-200-roomiq-climate.yaml"
ROOMIQ_BOARD = REPO_ROOT / "packages" / "boards" / "s360-200-roomiq.yaml"
ROOMIQ_FRAMEWORK = REPO_ROOT / "packages" / "features" / "roomiq_framework.yaml"
ROOMIQ_PRESENCE_WRAPPER = (
    REPO_ROOT / "packages" / "remote" / "ceiling-roomiq-presence.yaml"
)
ENTITY_MATRIX = REPO_ROOT / "config" / "feature-entity-matrix.json"


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


def _load(path: Path) -> dict:
    doc = yaml.safe_load(path.read_text())
    return doc if isinstance(doc, dict) else {}


def _sensors_by_id(doc: dict) -> dict:
    out = {}
    for entry in doc.get("sensor") or []:
        if isinstance(entry, dict) and entry.get("id"):
            out[entry["id"]] = entry
    return out


class Bmp581DriverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = CLIMATE.read_text()
        cls.doc = _load(CLIMATE)
        cls.sensors = _sensors_by_id(cls.doc)

    # 1. The BMP581 is configured on the correct ESPHome platform.
    def test_bmp581_configured(self) -> None:
        bmp = self.sensors.get("comfort_ceiling_bmp581")
        self.assertIsNotNone(bmp, "BMP581 sensor id missing")
        self.assertEqual(bmp.get("platform"), "bmp581_i2c")
        self.assertIn("platform: bmp581_i2c", self.raw)

    # 1b. It is the BMP581 driver specifically — no BMP280/BME280/BMP3xx
    # substitution slipped in.
    def test_no_substitute_pressure_driver(self) -> None:
        for wrong in (
            "platform: bmp280",
            "platform: bmp280_i2c",
            "platform: bme280",
            "platform: bme280_i2c",
            "platform: bmp3xx",
            "platform: bmp3xx_i2c",
            "platform: bme680",
        ):
            self.assertNotIn(wrong, self.raw, wrong)

    # 2. Correct bus and verified address.
    def test_bus_and_address(self) -> None:
        bmp = self.sensors["comfort_ceiling_bmp581"]
        self.assertEqual(bmp.get("i2c_id"), "${comfort_ceiling_i2c_id}")
        subs = self.doc.get("substitutions") or {}
        self.assertEqual(subs.get("comfort_ceiling_i2c_id"), "core_i2c")
        # YAML parses 0x47 as the int 71; assert on the numeric value + literal.
        self.assertEqual(int(bmp.get("address")), 0x47)
        self.assertIn("address: 0x47", self.raw)

    # 3. A customer-facing atmospheric-pressure entity exists.
    def test_customer_facing_pressure_entity(self) -> None:
        bmp = self.sensors["comfort_ceiling_bmp581"]
        press = bmp.get("pressure") or {}
        self.assertEqual(press.get("id"), "comfort_ceiling_pressure")
        # Customer-facing => not internal, not disabled by default, and named.
        self.assertNotEqual(press.get("internal"), True)
        self.assertNotEqual(press.get("disabled_by_default"), True)
        self.assertIn("name", press)
        self.assertEqual(press.get("device_class"), "atmospheric_pressure")
        self.assertEqual(press.get("unit_of_measurement"), "hPa")

    # 4. The BMP581 die temperature is diagnostic / disabled only — it must
    #    never present itself as the canonical temperature.
    def test_bmp_temperature_is_diagnostic_only(self) -> None:
        bmp = self.sensors["comfort_ceiling_bmp581"]
        temp = bmp.get("temperature") or {}
        # A distinct id from the canonical SHT45 temperature.
        self.assertEqual(temp.get("id"), "comfort_ceiling_bmp_temperature")
        self.assertNotEqual(temp.get("id"), "comfort_ceiling_temperature")
        self.assertEqual(temp.get("entity_category"), "diagnostic")
        self.assertTrue(temp.get("disabled_by_default"))


class Sht45CanonicalPreservedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = _load(CLIMATE)
        cls.sensors = _sensors_by_id(cls.doc)

    # 5. SHT45 remains the canonical RoomIQ temperature source, unchanged.
    def test_sht45_temp_humidity_unchanged(self) -> None:
        sht = self.sensors.get("comfort_ceiling_sht4x")
        self.assertIsNotNone(sht, "SHT45 driver missing")
        self.assertEqual(sht.get("platform"), "sht4x")
        self.assertEqual(int(sht.get("address")), 0x44)
        self.assertEqual((sht.get("temperature") or {}).get("id"),
                         "comfort_ceiling_temperature")
        self.assertEqual((sht.get("humidity") or {}).get("id"),
                         "comfort_ceiling_humidity")

    # 5b. The RoomIQ engine still binds the SHT45 temperature id (NOT the BMP581
    #     die temperature) as the canonical temperature source.
    def test_framework_temperature_source_is_sht45(self) -> None:
        subs = (_load(ROOMIQ_FRAMEWORK).get("substitutions") or {})
        self.assertEqual(subs.get("roomiq_temperature_source_id"),
                         "comfort_ceiling_temperature")
        # The BMP581 die-temperature id must not have become a framework input.
        for key, val in subs.items():
            if key.endswith("_source_id"):
                self.assertNotEqual(val, "comfort_ceiling_bmp_temperature", key)

    # 5c. Pressure is a standalone entity — it is NOT wired into RoomIQ
    #     framework availability in this slice (no *_source_id points at it,
    #     and the engine YAML does not reference the pressure id).
    def test_pressure_not_a_framework_availability_input(self) -> None:
        fw_raw = ROOMIQ_FRAMEWORK.read_text()
        self.assertNotIn("comfort_ceiling_pressure", fw_raw)
        subs = (_load(ROOMIQ_FRAMEWORK).get("substitutions") or {})
        for key, val in subs.items():
            self.assertNotEqual(val, "comfort_ceiling_pressure", key)


class RemoteWrapperStillComposesTests(unittest.TestCase):
    # 6. The RoomIQ + Presence remote wrapper still composes the RoomIQ board,
    #    which composes the (now BMP581-bearing) climate half.
    def test_wrapper_composition_intact(self) -> None:
        raw = ROOMIQ_PRESENCE_WRAPPER.read_text()
        self.assertIn("../boards/s360-200-roomiq.yaml", raw)
        self.assertIn("../features/roomiq_framework.yaml", raw)
        self.assertIn("../features/presence_framework.yaml", raw)
        board_raw = ROOMIQ_BOARD.read_text()
        self.assertIn("s360-200-roomiq-climate.yaml", board_raw)
        # The climate half the wrapper transitively composes carries the BMP581.
        self.assertIn("platform: bmp581_i2c", CLIMATE.read_text())


if __name__ == "__main__":
    unittest.main()

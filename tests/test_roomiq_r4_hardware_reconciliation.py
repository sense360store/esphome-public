#!/usr/bin/env python3
"""S360-200-R4-HARDWARE-RECONCILIATION-001 contract lock.

Pins the corrected S360-200-R4 RoomIQ climate hardware definition against the
verified schematic + BOM (docs/hardware/s360-200-r4-roomiq.md,
docs/hardware/artifacts/S360-200-R4.md):

  * ambient light  : LTR-303ALS-01 (U1) via ESPHome's built-in ltr_als_ps
                     platform, ALS-only, I2C 0x29 on the shared core_i2c bus;
  * temp/humidity  : SHT45 (U2, SHT45-AD1B-R3) via sht4x, I2C 0x44 on core_i2c;

and the SFA40 opt-out mechanism for custom no-SFA40 assemblies, without
regressing the RoomIQ / Presence framework contracts or the default
(SFA40-fitted) behaviour of shipping AirIQ products.

Stdlib unittest only (repo convention); runnable directly or under pytest.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

CLIMATE = REPO_ROOT / "packages" / "boards" / "s360-200-roomiq-climate.yaml"
ROOMIQ_BOARD = REPO_ROOT / "packages" / "boards" / "s360-200-roomiq.yaml"
ROOMIQ_FRAMEWORK = REPO_ROOT / "packages" / "features" / "roomiq_framework.yaml"
AIRIQ_BOARD = REPO_ROOT / "packages" / "boards" / "s360-210-airiq.yaml"
AIRIQ_NOSFA40 = REPO_ROOT / "packages" / "boards" / "s360-210-airiq-no-sfa40.yaml"
ROOMIQ_PRESENCE_WRAPPER = (
    REPO_ROOT / "packages" / "remote" / "ceiling-roomiq-presence.yaml"
)
LED_FRAMEWORK = REPO_ROOT / "packages" / "features" / "led_framework.yaml"
CORE_FRAMEWORK_JSON = REPO_ROOT / "config" / "core-framework.json"
HW_DOC = REPO_ROOT / "docs" / "hardware" / "s360-200-r4-roomiq.md"


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


class ClimateDriverReconciledTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = CLIMATE.read_text()
        cls.doc = _load(CLIMATE)
        cls.sensors = _sensors_by_id(cls.doc)

    # 1. No veml7700 remains in the canonical S360-200-R4 climate package.
    def test_no_veml7700(self) -> None:
        self.assertNotIn("platform: veml7700", self.raw)
        self.assertNotIn("comfort_ceiling_veml7700", self.raw)
        self.assertNotIn("address: 0x10", self.raw)

    # 2. The correct package uses ltr_als_ps.
    def test_uses_ltr_als_ps(self) -> None:
        self.assertIn("platform: ltr_als_ps", self.raw)
        ltr = self.sensors.get("comfort_ceiling_ltr303")
        self.assertIsNotNone(ltr, "ltr_als_ps sensor id missing")
        self.assertEqual(ltr.get("platform"), "ltr_als_ps")

    # 3. The light sensor is configured as ALS-only.
    def test_als_only(self) -> None:
        ltr = self.sensors["comfort_ceiling_ltr303"]
        self.assertEqual(ltr.get("type"), "ALS")

    # 4. No proximity entities are exposed.
    def test_no_proximity(self) -> None:
        ltr = self.sensors["comfort_ceiling_ltr303"]
        for key in ("proximity", "proximity_counts", "ps_cooldown",
                    "ps_high_threshold", "ps_low_threshold"):
            self.assertNotIn(key, ltr, key)
        self.assertNotIn("type: ALS_PS", self.raw)
        self.assertNotIn("type: PS", self.raw)

    # 5. The schematic-proven address and bus are used.
    def test_schematic_address_and_bus(self) -> None:
        ltr = self.sensors["comfort_ceiling_ltr303"]
        # YAML parses 0x29 as the int 41; assert on the numeric value.
        self.assertEqual(int(ltr.get("address")), 0x29)
        self.assertIn("address: 0x29", self.raw)
        self.assertEqual(ltr.get("i2c_id"), "${comfort_ceiling_i2c_id}")
        subs = self.doc.get("substitutions") or {}
        self.assertEqual(subs.get("comfort_ceiling_i2c_id"), "core_i2c")

    # 6. The existing RoomIQ raw illuminance ID is preserved.
    def test_illuminance_id_preserved(self) -> None:
        ltr = self.sensors["comfort_ceiling_ltr303"]
        self.assertEqual(
            (ltr.get("ambient_light") or {}).get("id"),
            "comfort_ceiling_illuminance",
        )
        self.assertTrue((ltr.get("ambient_light") or {}).get("internal"))

    # 7. The SHT45 uses the correct ESPHome platform, bus and address.
    def test_sht45_platform_bus_address(self) -> None:
        sht = self.sensors.get("comfort_ceiling_sht4x")
        self.assertIsNotNone(sht)
        self.assertEqual(sht.get("platform"), "sht4x")
        # YAML parses 0x44 as the int 68; assert on the numeric value.
        self.assertEqual(int(sht.get("address")), 0x44)
        self.assertIn("address: 0x44", self.raw)
        self.assertEqual(sht.get("i2c_id"), "${comfort_ceiling_i2c_id}")

    # 8. Existing RoomIQ raw temperature and humidity IDs are preserved.
    def test_temp_humidity_ids_preserved(self) -> None:
        sht = self.sensors["comfort_ceiling_sht4x"]
        self.assertEqual((sht.get("temperature") or {}).get("id"),
                         "comfort_ceiling_temperature")
        self.assertEqual((sht.get("humidity") or {}).get("id"),
                         "comfort_ceiling_humidity")

    # 13a. Board comments / logs name the corrected physical assembly.
    def test_comments_name_corrected_parts(self) -> None:
        self.assertIn("LTR-303ALS-01", self.raw)
        self.assertIn("SHT45", self.raw)
        # No false runtime-success claim: the runtime caveat is documented.
        lowered = self.raw.lower()
        self.assertIn("pending bench", lowered)


class FrameworkContractPreservedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fw = _load(ROOMIQ_FRAMEWORK)
        cls.fw_raw = ROOMIQ_FRAMEWORK.read_text()

    # 6/8. The framework still binds the preserved raw source ids.
    def test_framework_source_ids_unchanged(self) -> None:
        subs = self.fw.get("substitutions") or {}
        self.assertEqual(subs.get("roomiq_illuminance_source_id"),
                         "comfort_ceiling_illuminance")
        self.assertEqual(subs.get("roomiq_temperature_source_id"),
                         "comfort_ceiling_temperature")
        self.assertEqual(subs.get("roomiq_humidity_source_id"),
                         "comfort_ceiling_humidity")

    # 13b. The framework identity note reflects the reconciliation (not a
    # stale VEML7700 conflict) and makes no runtime-success claim.
    def test_identity_note_reconciled(self) -> None:
        self.assertIn("ltr_als_ps", self.fw_raw)
        self.assertIn("0x29", self.fw_raw)
        self.assertIn("pending bench", self.fw_raw.lower())


class RemoteWrapperComposesReconciledClimateTests(unittest.TestCase):
    # 9. The RoomIQ + Presence remote wrapper composes the reconciled climate
    # half (full esphome-config validation lives in
    # tests/test_remote_package_consumer.py; this pins the composition shape).
    def test_wrapper_composes_roomiq_board_and_frameworks(self) -> None:
        raw = ROOMIQ_PRESENCE_WRAPPER.read_text()
        self.assertIn("../boards/s360-200-roomiq.yaml", raw)
        self.assertIn("../features/roomiq_framework.yaml", raw)
        self.assertIn("../features/presence_framework.yaml", raw)
        # The board composes the reconciled climate half.
        board_raw = ROOMIQ_BOARD.read_text()
        self.assertIn("s360-200-roomiq-climate.yaml", board_raw)
        self.assertIn("LTR-303ALS-01", board_raw)


class LedAutomationContractTests(unittest.TestCase):
    # 10. LED automatic behaviour still consumes RoomIQ darkness (over the
    # preserved illuminance id) and fused Presence occupancy — the reconciled
    # driver keeps feeding the same canonical darkness service.
    def test_led_darkness_source_preserved(self) -> None:
        led_raw = LED_FRAMEWORK.read_text()
        # LED consumes the RoomIQ canonical darkness service (roomiq_engine.h)
        # and the fused Presence occupancy; the reconciliation changes neither.
        self.assertIn("roomiq_engine.h", led_raw)
        # The RoomIQ engine darkness is computed from the calibrated illuminance
        # path over the preserved raw id.
        fw = _load(ROOMIQ_FRAMEWORK)
        self.assertEqual((fw.get("substitutions") or {}).get(
            "roomiq_illuminance_source_id"), "comfort_ceiling_illuminance")


class Sfa40OptOutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.airiq_raw = AIRIQ_BOARD.read_text()
        cls.overlay_raw = AIRIQ_NOSFA40.read_text()
        cls.overlay = _load(AIRIQ_NOSFA40)

    # 11. Existing SFA40-bearing products remain unchanged: the canonical AirIQ
    # board still declares the fitted SFA40 @ 0x5D by default.
    def test_canonical_airiq_still_has_sfa40(self) -> None:
        self.assertIn("platform: sfa40", self.airiq_raw)
        self.assertIn("0x5D", self.airiq_raw)
        self.assertIn("sfa40_sensor", self.airiq_raw)

    # 12. The opt-out overlay removes the SFA40 driver + the framework HCHO
    # engine-input and marks HCHO not-expected, without touching the default.
    def test_overlay_removes_sfa40_and_expected(self) -> None:
        self.assertIn("!remove sfa40_sensor", self.overlay_raw)
        self.assertIn("!remove s360_airiq_hcho_sample", self.overlay_raw)
        subs = self.overlay.get("substitutions") or {}
        self.assertEqual(subs.get("airiq_expected_hcho"), "false")
        # The overlay must NOT itself declare an sfa40 driver (a comment may
        # mention the string, so check the parsed sensor entries instead) or
        # touch release / catalog state.
        for entry in self.overlay.get("sensor") or []:
            self.assertNotEqual(
                (entry or {}).get("platform"), "sfa40",
                "opt-out overlay must not declare an sfa40 driver",
            )
        for forbidden in ("webflash_build_matrix", "artifact_name",
                          "product-catalog"):
            self.assertNotIn(forbidden, self.overlay_raw)


class CatalogAndDocReconciledTests(unittest.TestCase):
    # 13c. Catalog / core-framework declarations name the corrected assembly.
    def test_core_framework_json_reconciled(self) -> None:
        raw = CORE_FRAMEWORK_JSON.read_text()
        self.assertIn("LTR-303ALS-01", raw)
        self.assertIn("ltr_als_ps", raw)
        data = json.loads(raw)  # still valid JSON
        self.assertIsInstance(data, dict)

    # 13d. The authoritative hardware doc already documents LTR-303ALS-01 (U1)
    # and SHT45 (U2) — the firmware now matches it.
    def test_hw_doc_parts(self) -> None:
        raw = HW_DOC.read_text()
        self.assertIn("LTR-303ALS-01", raw)
        self.assertIn("SHT45", raw)


if __name__ == "__main__":
    unittest.main()

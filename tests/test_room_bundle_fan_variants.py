"""Contract tests for the planning-only room-bundle fan-control variants.

These tests validate config/room-bundle-fan-variants.json. They are intentionally
strict about the planning-only, non-release nature of the proposal:

  * every variant is lifecycle "planning" and webflash_exposed False
  * only Bathroom and Kitchen bundles have fan variants
  * no TRIAC fan-control method appears anywhere
  * fan-control methods are limited to relay / dac_0_10v / pwm
  * variant SKUs are derived from their base bundle SKU

The tests do not import any firmware/build modules and do not imply a release.
"""
import json
import os
import unittest


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(REPO_ROOT, "config", "room-bundle-fan-variants.json")

ALLOWED_FAN_CONTROL = {"relay", "dac_0_10v", "pwm"}
ALLOWED_ROOMS = {"Bathroom", "Kitchen"}
EXPECTED_VARIANTS = {
    "S360-KIT-BATH-P-REL",
    "S360-KIT-BATH-P-DAC",
    "S360-KIT-BATH-P-PWM",
    "S360-KIT-KITCHEN-P-DAC",
    "S360-KIT-KITCHEN-P-REL",
}


class RoomBundleFanVariantsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CONFIG_PATH, encoding="utf-8") as handle:
            cls.data = json.load(handle)

    def test_schema_version_and_status(self):
        self.assertEqual(self.data["schema_version"], "1.0.0")
        self.assertEqual(self.data["status"], "planning")
        self.assertEqual(self.data["doc_id"], "ROOM-BUNDLE-FAN-VARIANTS-001")

    def test_all_variants_planning_and_not_webflash(self):
        for variant in self.data["variants"]:
            self.assertEqual(variant["lifecycle"], "planning")
            self.assertFalse(variant["webflash_exposed"])

    def test_expected_variant_skus(self):
        skus = {v["variant_sku"] for v in self.data["variants"]}
        self.assertEqual(skus, EXPECTED_VARIANTS)

    def test_only_bathroom_and_kitchen(self):
        rooms = {v["room"] for v in self.data["variants"]}
        self.assertEqual(rooms, ALLOWED_ROOMS)

    def test_fan_control_methods_allowed(self):
        for variant in self.data["variants"]:
            self.assertIn(variant["fan_control"], ALLOWED_FAN_CONTROL)

    def test_no_triac_anywhere(self):
        blob = json.dumps(self.data).lower()
        self.assertNotIn("triac", blob)

    def test_variant_sku_derived_from_base(self):
        for variant in self.data["variants"]:
            self.assertTrue(
                variant["variant_sku"].startswith(variant["base_bundle_sku"] + "-")
            )

    def test_base_bundles_are_poe(self):
        for variant in self.data["variants"]:
            self.assertTrue(variant["base_bundle_sku"].endswith("-P"))

    def test_fan_control_methods_section(self):
        methods = set(self.data["fan_control_methods"].keys())
        self.assertEqual(methods, ALLOWED_FAN_CONTROL)

    def test_non_goals_present(self):
        self.assertTrue(any("TRIAC" in g for g in self.data["non_goals"]))
        self.assertTrue(any("WebFlash" in g for g in self.data["non_goals"]))

    def test_planning_notes_present(self):
        notes = self.data["planning_notes"]
        self.assertIn("option_chosen", notes)
        self.assertIn("interchangeability", notes)
        self.assertIn("webflash", notes)
        self.assertIn("kitchen_framing", notes)

    def test_kitchen_not_cooker_hood(self):
        for variant in self.data["variants"]:
            if variant["room"] == "Kitchen":
                self.assertIn("cooker-hood", variant["notes"])

    def test_no_corridor_living_bedroom(self):
        rooms = {v["room"] for v in self.data["variants"]}
        self.assertNotIn("Corridor", rooms)
        self.assertNotIn("Living", rooms)
        self.assertNotIn("Bedroom", rooms)

    def test_dac_uses_0_10v_label(self):
        self.assertIn("0-10V", self.data["fan_control_methods"]["dac_0_10v"])

    def test_variant_count(self):
        self.assertEqual(len(self.data["variants"]), 5)

    def test_bathroom_has_three_variants(self):
        bath = [v for v in self.data["variants"] if v["room"] == "Bathroom"]
        self.assertEqual(len(bath), 3)

    def test_kitchen_has_two_variants(self):
        kitchen = [v for v in self.data["variants"] if v["room"] == "Kitchen"]
        self.assertEqual(len(kitchen), 2)

    def test_no_artifact_name_field(self):
        for variant in self.data["variants"]:
            self.assertNotIn("artifact_name", variant)

    def test_description_mentions_planning_only(self):
        self.assertIn("Planning-only", self.data["description"])

    def test_all_variants_have_notes(self):
        for variant in self.data["variants"]:
            self.assertTrue(variant["notes"].strip())

    def test_all_variants_have_required_keys(self):
        required = {
            "variant_sku",
            "base_bundle_sku",
            "room",
            "fan_control",
            "lifecycle",
            "webflash_exposed",
            "notes",
        }
        for variant in self.data["variants"]:
            self.assertTrue(required.issubset(variant.keys()))

    def test_base_bundle_skus_known(self):
        known = {"S360-KIT-BATH-P", "S360-KIT-KITCHEN-P"}
        for variant in self.data["variants"]:
            self.assertIn(variant["base_bundle_sku"], known)

    def test_relay_description_mentions_on_off(self):
        desc = self.data["fan_control_methods"]["relay"].lower()
        self.assertTrue("on/off" in desc or "on-off" in desc)

    def test_pwm_description_mentions_duty(self):
        self.assertIn("duty", self.data["fan_control_methods"]["pwm"].lower())

    def test_planning_notes_option_a(self):
        self.assertIn("Option A", self.data["planning_notes"]["option_chosen"])

    def test_kitchen_framing_mvhr(self):
        framing = self.data["planning_notes"]["kitchen_framing"].lower()
        self.assertIn("mvhr", framing)

    def test_interchangeability_note(self):
        note = self.data["planning_notes"]["interchangeability"].lower()
        self.assertIn("not runtime-interchangeable", note)

    def test_sku_vs_config_note(self):
        note = self.data["planning_notes"]["sku_vs_config"].lower()
        self.assertIn("config", note)

    def test_no_webflash_build_matrix_key(self):
        self.assertNotIn("webflash_build_matrix", self.data)

    def test_top_level_keys(self):
        expected = {
            "schema_version",
            "doc_id",
            "status",
            "description",
            "non_goals",
            "fan_control_methods",
            "variants",
            "planning_notes",
        }
        self.assertEqual(set(self.data.keys()), expected)

    def test_relay_variants_exist(self):
        relay = [v for v in self.data["variants"] if v["fan_control"] == "relay"]
        self.assertEqual(len(relay), 2)

    def test_dac_variants_exist(self):
        dac = [v for v in self.data["variants"] if v["fan_control"] == "dac_0_10v"]
        self.assertEqual(len(dac), 2)

    def test_pwm_variants_exist(self):
        pwm = [v for v in self.data["variants"] if v["fan_control"] == "pwm"]
        self.assertEqual(len(pwm), 1)

    def test_config_file_exists(self):
        self.assertTrue(os.path.exists(CONFIG_PATH))

    def test_json_is_object(self):
        self.assertIsInstance(self.data, dict)

    def test_variants_is_list(self):
        self.assertIsInstance(self.data["variants"], list)

    def test_all_skus_unique(self):
        skus = [v["variant_sku"] for v in self.data["variants"]]
        self.assertEqual(len(skus), len(set(skus)))

    def test_all_variants_have_lifecycle(self):
        self.assertEqual({v["lifecycle"] for v in self.data["variants"]}, {"planning"})

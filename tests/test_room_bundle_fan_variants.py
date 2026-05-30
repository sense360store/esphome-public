import json
import os
import unittest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VARIANTS = os.path.join(BASE, "config", "room-bundle-fan-variants.json")
BUNDLES = os.path.join(BASE, "config", "room-bundle-skus.json")
WEBFLASH = os.path.join(BASE, "config", "webflash-builds.json")

EXPECTED_VARIANT_SKUS = {
    "S360-KIT-BATH-P-REL",
    "S360-KIT-BATH-P-DAC",
    "S360-KIT-BATH-P-PWM",
    "S360-KIT-KITCHEN-P-DAC",
    "S360-KIT-KITCHEN-P-REL",
}

ALLOWED_FAN_DRIVERS = {"S360-310", "S360-311", "S360-312"}
ALLOWED_LIFECYCLES = {"planning", "manual-candidate"}


def load(path):
    with open(path) as f:
        return json.load(f)


class TestRoomBundleFanVariants(unittest.TestCase):
    def setUp(self):
        self.data = load(VARIANTS)
        self.variants = self.data["fan_variant_candidates"]
        self.bundles = load(BUNDLES)

    def _bundle_skus(self):
        out = set()
        for b in self.bundles.get("room_bundles", []):
            out.add(b["sku"])
        return out

    def test_all_variants_reference_existing_base(self):
        bundle_skus = self._bundle_skus()
        for v in self.variants:
            self.assertIn(v["base_bundle"], bundle_skus)

    def test_only_bathroom_kitchen_bases(self):
        for v in self.variants:
            self.assertTrue(
                "BATH" in v["base_bundle"] or "KITCHEN" in v["base_bundle"]
            )

    def test_only_allowed_fan_drivers(self):
        for v in self.variants:
            self.assertIn(v["fan_driver_board"], ALLOWED_FAN_DRIVERS)

    def test_no_triac_driver(self):
        for v in self.variants:
            self.assertNotEqual(v["fan_driver_board"], "S360-320")

    def test_lifecycle_planning_only(self):
        for v in self.variants:
            self.assertIn(v["lifecycle"], ALLOWED_LIFECYCLES)

    def test_no_webflash_exposure(self):
        wf = load(WEBFLASH)
        exposed = set()
        for b in wf.get("builds", []):
            exposed.add(b.get("sku"))
        for v in self.variants:
            if v.get("webflash_exposed"):
                self.assertIn(v["variant_sku"], exposed)

    def test_exactly_expected_variant_skus(self):
        skus = {v["variant_sku"] for v in self.variants}
        self.assertEqual(skus, EXPECTED_VARIANT_SKUS)

    def test_all_have_control_type(self):
        for v in self.variants:
            self.assertIn(v["control_type"], {"relay", "0-10V", "pwm"})

    def test_webflash_exposed_is_bool(self):
        for v in self.variants:
            self.assertIsInstance(v["webflash_exposed"], bool)


if __name__ == "__main__":
    unittest.main()

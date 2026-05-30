#!/usr/bin/env python3
"""Tests for the planning-only room-bundle fan-control variant proposal.

Covers ``config/room-bundle-fan-variants.json`` (ROOM-BUNDLE-FAN-VARIANTS-001),
the planning-only proposal that splits ONLY the Bathroom and Kitchen PoE room
bundles into optional fan-control variants. These variants are bundle-SKU
planning metadata; they must reference an existing base bundle, must use only
the customer-facing fan drivers (S360-310 / S360-311 / S360-312), must never
recommend the TRIAC driver (S360-320), must never claim WebFlash exposure, and
must never carry a stable/release lifecycle.

Uses Python's stdlib unittest (matching this repo's no-pytest convention for
its Python validators). Run with::

    python3 tests/test_room_bundle_fan_variants.py

or::

    python3 -m unittest tests.test_room_bundle_fan_variants -v
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FAN_VARIANTS_PATH = REPO_ROOT / "config" / "room-bundle-fan-variants.json"
BUNDLE_SKUS_PATH = REPO_ROOT / "config" / "room-bundle-skus.json"
WEBFLASH_BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"

# Fan driver boards that may appear as a customer-facing variant driver.
ALLOWED_FAN_DRIVER_SKUS = frozenset({"S360-310", "S360-311", "S360-312"})
# TRIAC driver must never be recommended for a customer-facing fan bundle.
FORBIDDEN_FAN_DRIVER_SKU = "S360-320"
# Only these lifecycle values are permitted for planning-stage variants.
ALLOWED_LIFECYCLES = frozenset({"planning", "manual-candidate"})
# Only the Bathroom and Kitchen base bundles may have fan variants.
ALLOWED_BASE_BUNDLE_SKUS = frozenset({"S360-KIT-BATH-P", "S360-KIT-KITCHEN-P"})
# Base bundles that must never appear as a fan-variant base.
FORBIDDEN_BASE_BUNDLE_SKUS = frozenset(
    {"S360-KIT-CORRIDOR-P", "S360-KIT-LIVING-P", "S360-KIT-BEDROOM-P"}
)
EXPECTED_VARIANT_SKUS = frozenset(
    {
        "S360-KIT-BATH-P-REL",
        "S360-KIT-BATH-P-DAC",
        "S360-KIT-BATH-P-PWM",
        "S360-KIT-KITCHEN-P-DAC",
        "S360-KIT-KITCHEN-P-REL",
    }
)


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class RoomBundleFanVariantsTests(unittest.TestCase):
    """Planning-only contract for the fan-control variant candidates."""

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(FAN_VARIANTS_PATH)
        cls.variants = cls.doc["fan_variant_candidates"]
        cls.base_bundle_skus = {
            b["bundle_sku"] for b in _load(BUNDLE_SKUS_PATH)["bundles"]
        }
        # WebFlash builds are keyed by firmware config_string; collect them so a
        # variant SKU cannot be silently treated as already WebFlash-exposed.
        cls.webflash_config_strings = {
            entry["config_string"]
            for entry in _load(WEBFLASH_BUILDS_PATH).get("builds", []) or []
            if entry.get("config_string")
        }

    def test_has_fan_variant_candidates(self):
        self.assertIn("fan_variant_candidates", self.doc)
        self.assertIsInstance(self.variants, list)
        self.assertGreaterEqual(len(self.variants), 1)

    def test_every_base_bundle_exists_in_room_bundle_skus(self):
        for v in self.variants:
            self.assertIn(
                v["base_bundle"],
                self.base_bundle_skus,
                f"variant {v['sku']!r} references base bundle "
                f"{v['base_bundle']!r} which does not exist in "
                "config/room-bundle-skus.json",
            )

    def test_only_bathroom_and_kitchen_base_bundles(self):
        for v in self.variants:
            self.assertIn(
                v["base_bundle"],
                ALLOWED_BASE_BUNDLE_SKUS,
                f"variant {v['sku']!r} uses base bundle {v['base_bundle']!r}; "
                "only Bathroom / Kitchen may have fan variants",
            )
            self.assertNotIn(
                v["base_bundle"],
                FORBIDDEN_BASE_BUNDLE_SKUS,
                f"variant {v['sku']!r} uses a forbidden base bundle "
                f"{v['base_bundle']!r} (Corridor / Living / Bedroom)",
            )

    def test_no_corridor_living_or_bedroom_fan_variant(self):
        used_bases = {v["base_bundle"] for v in self.variants}
        offending = used_bases & FORBIDDEN_BASE_BUNDLE_SKUS
        self.assertFalse(
            offending,
            "Corridor / Living / Bedroom base bundles must not have fan "
            f"variants; found {sorted(offending)}",
        )

    def test_fan_drivers_are_allowed_only(self):
        for v in self.variants:
            self.assertIn(
                v["fan_driver"],
                ALLOWED_FAN_DRIVER_SKUS,
                f"variant {v['sku']!r} references fan driver "
                f"{v['fan_driver']!r}; only S360-310 / S360-311 / S360-312 "
                "are allowed",
            )

    def test_triac_never_appears(self):
        for v in self.variants:
            self.assertNotEqual(
                v["fan_driver"],
                FORBIDDEN_FAN_DRIVER_SKU,
                f"variant {v['sku']!r} must not use the TRIAC driver "
                f"{FORBIDDEN_FAN_DRIVER_SKU}",
            )
            for value in v.values():
                self.assertNotEqual(
                    value,
                    FORBIDDEN_FAN_DRIVER_SKU,
                    f"variant {v['sku']!r} must not reference the TRIAC "
                    f"driver {FORBIDDEN_FAN_DRIVER_SKU} anywhere",
                )
        # The TRIAC SKU must also not be in the file's allowed driver list.
        self.assertNotIn(
            FORBIDDEN_FAN_DRIVER_SKU,
            self.doc.get("allowed_fan_driver_skus", []),
        )

    def test_lifecycle_is_planning_only(self):
        for v in self.variants:
            self.assertIn(
                v.get("lifecycle"),
                ALLOWED_LIFECYCLES,
                f"variant {v['sku']!r} lifecycle {v.get('lifecycle')!r} must "
                "be planning / manual-candidate only (never a stable/release "
                "lifecycle)",
            )

    def test_no_variant_claims_webflash_exposure(self):
        for v in self.variants:
            exposed = v.get("webflash_exposed", False)
            if not exposed:
                self.assertIs(
                    exposed,
                    False,
                    f"variant {v['sku']!r} webflash_exposed must be false",
                )
                continue
            # A variant may only claim exposure if its SKU is already a
            # committed WebFlash build config_string; none of these are.
            self.assertIn(
                v["sku"],
                self.webflash_config_strings,
                f"variant {v['sku']!r} claims webflash_exposed=true but is "
                "not present in config/webflash-builds.json",
            )

    def test_exactly_the_five_expected_variants(self):
        skus = {v["sku"] for v in self.variants}
        self.assertEqual(
            skus,
            set(EXPECTED_VARIANT_SKUS),
            "fan variant SKU set drifted from the five expected variants",
        )
        self.assertEqual(len(self.variants), len(EXPECTED_VARIANT_SKUS))


def test_main():
    unittest.main()


if __name__ == "__main__":
    unittest.main(verbosity=2)

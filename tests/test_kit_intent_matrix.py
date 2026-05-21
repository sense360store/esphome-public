#!/usr/bin/env python3
"""Tests for the productized kit / bundle intent matrix (KIT-MATRIX-001).

Covers the planning matrix at ``config/kit-intent-matrix.json`` which
maps customer-facing kit / bundle intent groups onto module SKUs and the
firmware config strings tracked in
``config/firmware-combination-matrix.json``. The kit-intent matrix is
planning data only; these tests pin the productization invariants and
the guardrails that no kit intent implies unsafe WebFlash exposure or
stable promotion.

Uses Python's stdlib unittest (matching this repo's no-pytest convention
for Python validators). Run with::

    python3 tests/test_kit_intent_matrix.py

or::

    python3 -m unittest tests.test_kit_intent_matrix -v
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
KIT_MATRIX_PATH = REPO_ROOT / "config" / "kit-intent-matrix.json"
FW_MATRIX_PATH = REPO_ROOT / "config" / "firmware-combination-matrix.json"
WEBFLASH_BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"

RELEASE_ONE_CONFIG_STRING = "Ceiling-POE-VentIQ-RoomIQ"
LED_PREVIEW_CONFIG_STRING = "Ceiling-POE-VentIQ-RoomIQ-LED"

ALLOWED_TIERS = frozenset(
    {"ready-kit", "preview-kit", "future-expansion", "advanced-manual"}
)
ALLOWED_LIFECYCLE_STATUSES = frozenset(
    {"production", "preview", "hardware-pending", "blocked"}
)
ALLOWED_USE_CASES = frozenset({"bathroom", "kitchen-or-duct-fan"})

REQUIRED_KIT_FIELDS = {
    "kit_id",
    "customer_name",
    "use_case",
    "tier",
    "lifecycle_status",
    "default_config_string",
    "included_module_skus",
    "recommended_modules",
    "optional_modules",
    "advanced_modules",
    "excluded_or_not_recommended_modules",
    "firmware_matrix_lane",
    "webflash_exposure_allowed_now",
    "stable_ready_now",
    "blockers",
    "notes",
}


def _load(path: Path):
    return json.loads(path.read_text())


class KitIntentMatrixShapeTests(unittest.TestCase):
    """Shape / schema invariants of the on-disk kit-intent matrix."""

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(KIT_MATRIX_PATH)
        cls.kits = cls.doc["kits"]
        cls.by_id = {kit["kit_id"]: kit for kit in cls.kits}

    def test_schema_version_is_one(self):
        self.assertEqual(self.doc["schema_version"], 1)

    def test_sources_point_to_canonical_files(self):
        sources = self.doc.get("sources", {})
        self.assertEqual(
            sources.get("firmware_matrix"),
            "config/firmware-combination-matrix.json",
        )
        self.assertEqual(sources.get("webflash_builds"), "config/webflash-builds.json")
        self.assertEqual(
            sources.get("hardware_catalog"), "config/hardware-catalog.json"
        )

    def test_every_kit_has_required_fields(self):
        for kit in self.kits:
            missing = REQUIRED_KIT_FIELDS - set(kit.keys())
            self.assertFalse(
                missing,
                f"kit {kit.get('kit_id')!r} missing fields {missing}",
            )

    def test_kit_ids_are_unique(self):
        ids = [kit["kit_id"] for kit in self.kits]
        self.assertEqual(len(ids), len(set(ids)), f"duplicate kit_id in {ids}")

    def test_every_tier_is_allowed(self):
        for kit in self.kits:
            self.assertIn(
                kit["tier"],
                ALLOWED_TIERS,
                f"kit {kit['kit_id']!r} has disallowed tier {kit['tier']!r}",
            )

    def test_every_lifecycle_status_is_allowed(self):
        for kit in self.kits:
            self.assertIn(
                kit["lifecycle_status"],
                ALLOWED_LIFECYCLE_STATUSES,
                f"kit {kit['kit_id']!r} has disallowed lifecycle_status "
                f"{kit['lifecycle_status']!r}",
            )

    def test_every_use_case_is_allowed(self):
        for kit in self.kits:
            self.assertIn(
                kit["use_case"],
                ALLOWED_USE_CASES,
                f"kit {kit['kit_id']!r} has disallowed use_case "
                f"{kit['use_case']!r}",
            )

    def test_module_list_fields_are_lists_of_strings(self):
        list_fields = (
            "included_module_skus",
            "recommended_modules",
            "optional_modules",
            "advanced_modules",
            "excluded_or_not_recommended_modules",
            "blockers",
        )
        for kit in self.kits:
            for field in list_fields:
                value = kit[field]
                self.assertIsInstance(
                    value,
                    list,
                    f"kit {kit['kit_id']!r} field {field!r} must be a list",
                )
                for entry in value:
                    self.assertIsInstance(
                        entry,
                        str,
                        f"kit {kit['kit_id']!r} field {field!r} must be a "
                        f"list of strings; got {entry!r}",
                    )


class KitIntentFirmwareLinkTests(unittest.TestCase):
    """Pin the kit-intent <-> firmware-matrix and webflash-builds links."""

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(KIT_MATRIX_PATH)
        cls.kits = cls.doc["kits"]
        cls.by_id = {kit["kit_id"]: kit for kit in cls.kits}
        fw_matrix = _load(FW_MATRIX_PATH)
        cls.fw_config_strings = {
            row["config_string"] for row in fw_matrix["combinations"]
        }
        builds = _load(WEBFLASH_BUILDS_PATH)
        cls.webflash_config_strings = {
            entry["config_string"]
            for entry in builds.get("builds", []) or []
            if entry.get("config_string")
        }

    def test_default_config_strings_exist_in_firmware_matrix(self):
        for kit in self.kits:
            cs = kit.get("default_config_string")
            if cs is None:
                continue
            self.assertIn(
                cs,
                self.fw_config_strings,
                f"kit {kit['kit_id']!r} default_config_string {cs!r} is not "
                "present in config/firmware-combination-matrix.json",
            )

    def test_webflash_exposure_implies_committed_build(self):
        for kit in self.kits:
            if not kit.get("webflash_exposure_allowed_now"):
                continue
            cs = kit.get("default_config_string")
            self.assertIsNotNone(
                cs,
                f"kit {kit['kit_id']!r} has webflash_exposure_allowed_now=true "
                "but no default_config_string",
            )
            self.assertIn(
                cs,
                self.webflash_config_strings,
                f"kit {kit['kit_id']!r} has webflash_exposure_allowed_now=true "
                f"but its default_config_string {cs!r} is not in "
                "config/webflash-builds.json",
            )

    def test_stable_ready_implies_webflash_exposure(self):
        for kit in self.kits:
            if kit.get("stable_ready_now"):
                self.assertTrue(
                    kit.get("webflash_exposure_allowed_now"),
                    f"kit {kit['kit_id']!r} is stable_ready_now=true but "
                    "webflash_exposure_allowed_now=false; that is "
                    "self-contradictory",
                )


class KitIntentRowAssertionsTests(unittest.TestCase):
    """Assert the per-row invariants the productization plan promises."""

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(KIT_MATRIX_PATH)
        cls.kits = cls.doc["kits"]
        cls.by_id = {kit["kit_id"]: kit for kit in cls.kits}

    def test_bath_poe_maps_to_release_one_stable(self):
        kit = self.by_id["S360-KIT-BATH-POE"]
        self.assertEqual(kit["default_config_string"], RELEASE_ONE_CONFIG_STRING)
        self.assertEqual(kit["use_case"], "bathroom")
        self.assertEqual(kit["tier"], "ready-kit")
        self.assertEqual(kit["lifecycle_status"], "production")
        self.assertTrue(kit["webflash_exposure_allowed_now"])
        self.assertTrue(kit["stable_ready_now"])
        for sku in ("S360-100", "S360-200", "S360-211", "S360-410"):
            self.assertIn(
                sku,
                kit["included_module_skus"],
                f"S360-KIT-BATH-POE must include module SKU {sku!r}",
            )

    def test_bath_poe_led_maps_to_led_preview_and_is_not_stable(self):
        kit = self.by_id["S360-KIT-BATH-POE-LED"]
        self.assertEqual(kit["default_config_string"], LED_PREVIEW_CONFIG_STRING)
        self.assertEqual(kit["use_case"], "bathroom")
        self.assertEqual(kit["tier"], "preview-kit")
        self.assertEqual(kit["lifecycle_status"], "preview")
        self.assertTrue(kit["webflash_exposure_allowed_now"])
        self.assertFalse(
            kit["stable_ready_now"],
            "S360-KIT-BATH-POE-LED must not be stable_ready_now until the "
            "LED stable gauntlet (S360-300-BENCH-001 + WF-HW-TEST-001 "
            "operator proof) closes",
        )
        for sku in ("S360-100", "S360-200", "S360-211", "S360-300", "S360-410"):
            self.assertIn(
                sku,
                kit["included_module_skus"],
                f"S360-KIT-BATH-POE-LED must include module SKU {sku!r}",
            )

    def test_led_preview_kit_carries_required_blockers(self):
        kit = self.by_id["S360-KIT-BATH-POE-LED"]
        blockers = set(kit["blockers"])
        self.assertIn(
            "S360-300-BENCH-001",
            blockers,
            "LED preview kit must carry the S360-300-BENCH-001 bench-evidence "
            "blocker",
        )
        operator_proof_blockers = {"WF-HW-TEST-001", "WF-HW-TEST-003"}
        self.assertTrue(
            operator_proof_blockers.issubset(blockers),
            "LED preview kit must carry the WebFlash operator-proof blockers "
            f"{sorted(operator_proof_blockers)} (found {sorted(blockers)})",
        )

    def test_fantriac_kit_is_not_stable_and_carries_hw005_and_compliance001(self):
        kit = self.by_id["S360-KIT-BATH-TRIAC"]
        self.assertFalse(
            kit["stable_ready_now"],
            "TRIAC kit must not be stable_ready_now",
        )
        self.assertFalse(
            kit["webflash_exposure_allowed_now"],
            "TRIAC kit must not be webflash_exposure_allowed_now",
        )
        blockers = set(kit["blockers"])
        self.assertIn(
            "HW-005",
            blockers,
            "TRIAC kit must carry HW-005 (FanTRIAC hardware blocker)",
        )
        self.assertIn(
            "COMPLIANCE-001",
            blockers,
            "TRIAC kit must carry COMPLIANCE-001 (mains-voltage compliance " "blocker)",
        )

    def test_pwm_kit_is_advanced_duct_fan_not_default_bathroom(self):
        kit = self.by_id["S360-KIT-DUCT-PWM"]
        self.assertEqual(
            kit["use_case"],
            "kitchen-or-duct-fan",
            "PWM kit must be classified under kitchen-or-duct-fan use case, "
            "not default bathroom",
        )
        self.assertIn(
            kit["tier"],
            {"future-expansion", "advanced-manual"},
            "PWM kit must be future-expansion / advanced-manual, not "
            "ready-kit / preview-kit",
        )
        self.assertFalse(
            kit["stable_ready_now"],
            "PWM kit must not be stable_ready_now",
        )
        self.assertFalse(
            kit["webflash_exposure_allowed_now"],
            "PWM kit must not be webflash_exposure_allowed_now",
        )

    def test_fandac_kit_is_advanced_duct_fan_not_default_bathroom(self):
        kit = self.by_id["S360-KIT-DUCT-0-10V"]
        self.assertEqual(
            kit["use_case"],
            "kitchen-or-duct-fan",
            "FanDAC (0-10V) kit must be classified under kitchen-or-duct-fan "
            "use case, not default bathroom",
        )
        self.assertIn(
            kit["tier"],
            {"future-expansion", "advanced-manual"},
            "FanDAC kit must be future-expansion / advanced-manual, not "
            "ready-kit / preview-kit",
        )
        self.assertFalse(
            kit["stable_ready_now"],
            "FanDAC kit must not be stable_ready_now",
        )
        self.assertFalse(
            kit["webflash_exposure_allowed_now"],
            "FanDAC kit must not be webflash_exposure_allowed_now",
        )


class KitIntentGuardrailTests(unittest.TestCase):
    """Hard guardrails: kit intent must not imply unsafe exposure."""

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(KIT_MATRIX_PATH)
        cls.kits = cls.doc["kits"]
        builds = _load(WEBFLASH_BUILDS_PATH)
        cls.webflash_config_strings = {
            entry["config_string"]
            for entry in builds.get("builds", []) or []
            if entry.get("config_string")
        }

    def test_no_kit_exposes_a_config_string_absent_from_webflash_builds(self):
        for kit in self.kits:
            if not kit.get("webflash_exposure_allowed_now"):
                continue
            cs = kit.get("default_config_string")
            self.assertIn(
                cs,
                self.webflash_config_strings,
                f"kit {kit['kit_id']!r} claims webflash_exposure_allowed_now "
                f"but its default_config_string {cs!r} is not committed in "
                "config/webflash-builds.json",
            )

    def test_pwr_related_kits_are_not_webflash_exposed(self):
        for kit in self.kits:
            mentions_pwr = any(
                "S360-400" in sku
                for sku in (
                    kit["included_module_skus"]
                    + kit["recommended_modules"]
                    + kit["optional_modules"]
                    + kit["advanced_modules"]
                )
            ) or (
                kit.get("default_config_string") is not None
                and "PWR" in kit["default_config_string"].split("-")
            )
            if not mentions_pwr:
                continue
            self.assertFalse(
                kit.get("webflash_exposure_allowed_now"),
                f"kit {kit['kit_id']!r} references PWR / S360-400 but is "
                "webflash_exposure_allowed_now; PWR remains compliance-blocked",
            )
            self.assertFalse(
                kit.get("stable_ready_now"),
                f"kit {kit['kit_id']!r} references PWR / S360-400 but is "
                "stable_ready_now; PWR remains compliance-blocked",
            )

    def test_no_kit_promotes_blocked_fan_to_stable(self):
        blocked_fan_skus = {"S360-310", "S360-311", "S360-312", "S360-320"}
        for kit in self.kits:
            uses_blocked_fan = bool(
                blocked_fan_skus.intersection(
                    set(kit["included_module_skus"])
                    | set(kit["recommended_modules"])
                    | set(kit["advanced_modules"])
                )
            )
            if not uses_blocked_fan:
                continue
            self.assertFalse(
                kit.get("stable_ready_now"),
                f"kit {kit['kit_id']!r} references a blocked fan SKU but is "
                "stable_ready_now",
            )
            self.assertFalse(
                kit.get("webflash_exposure_allowed_now"),
                f"kit {kit['kit_id']!r} references a blocked fan SKU but is "
                "webflash_exposure_allowed_now",
            )

    def test_only_ready_kit_tier_is_stable_ready(self):
        for kit in self.kits:
            if kit.get("stable_ready_now"):
                self.assertEqual(
                    kit["tier"],
                    "ready-kit",
                    f"kit {kit['kit_id']!r} is stable_ready_now but its tier "
                    f"is {kit['tier']!r}; only ready-kit should be stable",
                )
                self.assertEqual(
                    kit["lifecycle_status"],
                    "production",
                    f"kit {kit['kit_id']!r} is stable_ready_now but its "
                    f"lifecycle_status is {kit['lifecycle_status']!r}; only "
                    "production should be stable",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)

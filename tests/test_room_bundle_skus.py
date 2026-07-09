#!/usr/bin/env python3
"""Tests for the Sense360 PoE room bundle SKU matrix (BUNDLE-SKU-MATRIX-001).

Covers the canonical bundle SKU matrix at
``config/room-bundle-skus.json`` and pins the productization invariants:
bundle SKUs are unique; included board SKUs are valid known board SKUs;
every bundle has at least Core (S360-100) and PoE PSU (S360-410); LED
bundles are not marked stable while LED remains preview; no fan bundle
SKUs are introduced by this PR; bundle SKU names do not become release
artifact names automatically; the likely firmware config target, when
not null, exists in the firmware combination matrix.

Uses Python's stdlib unittest (no-pytest convention for this repo).
Run with::

    python3 tests/test_room_bundle_skus.py

or::

    python3 -m unittest tests.test_room_bundle_skus -v
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BUNDLE_PATH = REPO_ROOT / "config" / "room-bundle-skus.json"
HARDWARE_CATALOG_PATH = REPO_ROOT / "config" / "hardware-catalog.json"
FW_MATRIX_PATH = REPO_ROOT / "config" / "firmware-combination-matrix.json"
WEBFLASH_BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"

REQUIRED_BUNDLE_FIELDS = {
    "bundle_sku",
    "bundle_name",
    "room",
    "included_board_skus",
    "likely_firmware_config_target",
    "current_release_status",
    "missing_gates",
    "notes",
}

LED_BOARD_SKU = "S360-300"
CORE_BOARD_SKU = "S360-100"
POE_PSU_BOARD_SKU = "S360-410"
FAN_BOARD_SKUS = frozenset({"S360-310", "S360-311", "S360-312", "S360-320"})

STABLE_STATUSES = frozenset({"stable-release", "stable-candidate"})

BUNDLE_SKU_PATTERN = re.compile(r"^S360-KIT-[A-Z0-9-]+-P$")


def _load(path: Path):
    return json.loads(path.read_text())


class RoomBundleShapeTests(unittest.TestCase):
    """Shape / schema invariants of the on-disk bundle matrix."""

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(BUNDLE_PATH)
        cls.bundles = cls.doc["bundles"]
        cls.by_sku = {bundle["bundle_sku"]: bundle for bundle in cls.bundles}
        cls.allowed_statuses = frozenset(cls.doc["allowed_release_status"])

    def test_schema_version_is_one(self):
        self.assertEqual(self.doc["schema_version"], 1)

    def test_sources_point_to_canonical_files(self):
        sources = self.doc.get("sources", {})
        self.assertEqual(sources.get("hardware_catalog"), "config/hardware-catalog.json")
        self.assertEqual(
            sources.get("firmware_matrix"), "config/firmware-combination-matrix.json"
        )
        self.assertEqual(sources.get("webflash_builds"), "config/webflash-builds.json")
        self.assertEqual(sources.get("product_catalog"), "config/product-catalog.json")
        self.assertEqual(
            sources.get("kit_intent_matrix"), "config/kit-intent-matrix.json"
        )

    def test_every_bundle_has_required_fields(self):
        for bundle in self.bundles:
            missing = REQUIRED_BUNDLE_FIELDS - set(bundle.keys())
            self.assertFalse(
                missing,
                f"bundle {bundle.get('bundle_sku')!r} missing fields {missing}",
            )

    def test_bundle_sku_pattern(self):
        for bundle in self.bundles:
            sku = bundle["bundle_sku"]
            self.assertRegex(
                sku,
                BUNDLE_SKU_PATTERN,
                f"bundle_sku {sku!r} does not match {BUNDLE_SKU_PATTERN.pattern!r}; "
                "PoE room bundles use the S360-KIT-{ROOM}-P pattern",
            )

    def test_release_status_is_allowed(self):
        for bundle in self.bundles:
            status = bundle["current_release_status"]
            self.assertIn(
                status,
                self.allowed_statuses,
                f"bundle {bundle['bundle_sku']!r} has disallowed "
                f"current_release_status {status!r}",
            )

    def test_list_fields_are_lists_of_strings(self):
        list_fields = ("included_board_skus", "missing_gates")
        for bundle in self.bundles:
            for field in list_fields:
                value = bundle[field]
                self.assertIsInstance(
                    value,
                    list,
                    f"bundle {bundle['bundle_sku']!r} field {field!r} must be a list",
                )
                for entry in value:
                    self.assertIsInstance(
                        entry,
                        str,
                        f"bundle {bundle['bundle_sku']!r} field {field!r} must be a "
                        f"list of strings; got {entry!r}",
                    )


class RoomBundleHardwareLinkTests(unittest.TestCase):
    """Pin the bundle -> hardware catalog link."""

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(BUNDLE_PATH)
        cls.bundles = cls.doc["bundles"]
        cls.hw = _load(HARDWARE_CATALOG_PATH)
        cls.known_board_skus = {item["sku"] for item in cls.hw["items"]}

    def test_bundle_skus_are_unique(self):
        skus = [bundle["bundle_sku"] for bundle in self.bundles]
        self.assertEqual(
            len(skus),
            len(set(skus)),
            f"duplicate bundle_sku in {skus}",
        )

    def test_included_board_skus_are_known(self):
        for bundle in self.bundles:
            for board_sku in bundle["included_board_skus"]:
                self.assertIn(
                    board_sku,
                    self.known_board_skus,
                    f"bundle {bundle['bundle_sku']!r} references board SKU "
                    f"{board_sku!r} not in config/hardware-catalog.json",
                )

    def test_every_bundle_includes_core_and_poe_psu(self):
        for bundle in self.bundles:
            boards = set(bundle["included_board_skus"])
            self.assertIn(
                CORE_BOARD_SKU,
                boards,
                f"bundle {bundle['bundle_sku']!r} must include the Core board "
                f"({CORE_BOARD_SKU})",
            )
            self.assertIn(
                POE_PSU_BOARD_SKU,
                boards,
                f"bundle {bundle['bundle_sku']!r} must include the PoE PSU board "
                f"({POE_PSU_BOARD_SKU}); PoE room bundles by definition ship with "
                "S360-410",
            )

    def test_bundle_sku_is_not_a_board_sku(self):
        for bundle in self.bundles:
            sku = bundle["bundle_sku"]
            self.assertNotIn(
                sku,
                self.known_board_skus,
                f"bundle_sku {sku!r} must not collide with a known board SKU",
            )


class RoomBundleFirmwareLinkTests(unittest.TestCase):
    """Pin the bundle -> firmware combination matrix link."""

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(BUNDLE_PATH)
        cls.bundles = cls.doc["bundles"]
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
        cls.webflash_artifact_names = {
            entry.get("artifact_name")
            for entry in builds.get("builds", []) or []
            if entry.get("artifact_name")
        }

    def test_likely_firmware_config_targets_exist_in_firmware_matrix(self):
        for bundle in self.bundles:
            cs = bundle.get("likely_firmware_config_target")
            if cs is None:
                continue
            self.assertIn(
                cs,
                self.fw_config_strings,
                f"bundle {bundle['bundle_sku']!r} likely_firmware_config_target "
                f"{cs!r} is not present in config/firmware-combination-matrix.json",
            )

    def test_stable_release_status_implies_committed_webflash_build(self):
        for bundle in self.bundles:
            if bundle["current_release_status"] != "stable-release":
                continue
            cs = bundle.get("likely_firmware_config_target")
            self.assertIsNotNone(
                cs,
                f"bundle {bundle['bundle_sku']!r} is stable-release but has no "
                "likely_firmware_config_target",
            )
            self.assertIn(
                cs,
                self.webflash_config_strings,
                f"bundle {bundle['bundle_sku']!r} is stable-release but its "
                f"likely_firmware_config_target {cs!r} is not committed in "
                "config/webflash-builds.json",
            )

    def test_bundle_sku_is_not_a_firmware_artifact_name(self):
        for bundle in self.bundles:
            self.assertNotIn(
                bundle["bundle_sku"],
                self.webflash_artifact_names,
                f"bundle_sku {bundle['bundle_sku']!r} must not collide with a "
                "WebFlash release artifact_name; bundle SKU names do not become "
                "release artifact names automatically",
            )

    def test_bundle_sku_is_not_a_firmware_config_string(self):
        for bundle in self.bundles:
            self.assertNotIn(
                bundle["bundle_sku"],
                self.fw_config_strings,
                f"bundle_sku {bundle['bundle_sku']!r} must not collide with a "
                "firmware config string",
            )


class RoomBundleGuardrailTests(unittest.TestCase):
    """Hard guardrails: bundle SKUs must not imply unsafe promotion."""

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(BUNDLE_PATH)
        cls.bundles = cls.doc["bundles"]
        cls.by_sku = {bundle["bundle_sku"]: bundle for bundle in cls.bundles}

    def test_led_bundles_are_not_marked_stable(self):
        for bundle in self.bundles:
            boards = set(bundle["included_board_skus"])
            cs = bundle.get("likely_firmware_config_target") or ""
            mentions_led = LED_BOARD_SKU in boards or "LED" in cs.split("-")
            if not mentions_led:
                continue
            self.assertNotIn(
                bundle["current_release_status"],
                STABLE_STATUSES,
                f"bundle {bundle['bundle_sku']!r} includes LED ({LED_BOARD_SKU}) "
                f"and/or LED token; must not be marked "
                f"{bundle['current_release_status']!r} while LED remains preview "
                "(LED-STABLE-PROMOTION-001 / RELEASE-007 not closed)",
            )

    def test_no_fan_board_in_any_bundle(self):
        for bundle in self.bundles:
            boards = set(bundle["included_board_skus"])
            offending = boards & FAN_BOARD_SKUS
            self.assertFalse(
                offending,
                f"bundle {bundle['bundle_sku']!r} includes fan SKUs {sorted(offending)}; "
                "fan bundles are not introduced by BUNDLE-SKU-MATRIX-001 and "
                "remain owned by their per-family follow-up PR chains",
            )

    def test_no_fan_token_in_any_firmware_target(self):
        forbidden_tokens = {"FanRelay", "FanPWM", "FanDAC", "FanTRIAC"}
        for bundle in self.bundles:
            cs = bundle.get("likely_firmware_config_target") or ""
            tokens = set(cs.split("-"))
            offending = tokens & forbidden_tokens
            self.assertFalse(
                offending,
                f"bundle {bundle['bundle_sku']!r} likely_firmware_config_target "
                f"{cs!r} carries fan tokens {sorted(offending)}; fan bundles are "
                "not introduced by this PR",
            )

    def test_no_pwr_in_any_bundle(self):
        for bundle in self.bundles:
            boards = set(bundle["included_board_skus"])
            self.assertNotIn(
                "S360-400",
                boards,
                f"bundle {bundle['bundle_sku']!r} references PWR / S360-400; "
                "PWR is compliance-blocked and not in scope for PoE room bundles",
            )
            cs = bundle.get("likely_firmware_config_target") or ""
            self.assertNotIn(
                "PWR",
                cs.split("-"),
                f"bundle {bundle['bundle_sku']!r} likely_firmware_config_target "
                f"{cs!r} carries the PWR token; PoE room bundles are PoE-only",
            )

    def test_bath_bundle_maps_to_release_one_stable(self):
        bundle = self.by_sku["S360-KIT-BATH-P"]
        self.assertEqual(
            bundle["likely_firmware_config_target"],
            "Ceiling-POE-VentIQ-RoomIQ",
        )
        self.assertEqual(bundle["current_release_status"], "stable-release")
        for sku in ("S360-100", "S360-200", "S360-211", "S360-410"):
            self.assertIn(
                sku,
                bundle["included_board_skus"],
                f"S360-KIT-BATH-P must include board SKU {sku!r}",
            )

    def test_kitchen_bundle_maps_to_airiq_candidate(self):
        bundle = self.by_sku["S360-KIT-KITCHEN-P"]
        self.assertEqual(
            bundle["likely_firmware_config_target"],
            "Ceiling-POE-AirIQ-RoomIQ",
        )
        # Promoted stable-candidate -> stable-release under owner declaration
        # HW-RELEASE-001 (docs/hw-release-001.md); G8 gates cleared by owner
        # declaration, kit/customer visibility unchanged.
        self.assertEqual(bundle["current_release_status"], "stable-release")
        self.assertEqual(bundle["missing_gates"], [])
        for sku in ("S360-100", "S360-200", "S360-210", "S360-410"):
            self.assertIn(
                sku,
                bundle["included_board_skus"],
                f"S360-KIT-KITCHEN-P must include board SKU {sku!r}",
            )

    def test_bedroom_bundle_maps_to_roomiq_candidate(self):
        bundle = self.by_sku["S360-KIT-BEDROOM-P"]
        self.assertEqual(
            bundle["likely_firmware_config_target"],
            "Ceiling-POE-RoomIQ",
        )
        self.assertEqual(bundle["current_release_status"], "stable-candidate")
        self.assertEqual(
            set(bundle["included_board_skus"]),
            {"S360-100", "S360-200", "S360-410"},
            "S360-KIT-BEDROOM-P is the smallest RoomIQ-only PoE bundle and must "
            "contain exactly Core + RoomIQ + PoE PSU",
        )

    def test_living_and_corridor_share_board_set(self):
        living = self.by_sku["S360-KIT-LIVING-P"]
        corridor = self.by_sku["S360-KIT-CORRIDOR-P"]
        self.assertEqual(
            set(living["included_board_skus"]),
            set(corridor["included_board_skus"]),
            "S360-KIT-LIVING-P and S360-KIT-CORRIDOR-P currently share the same "
            "included board set; a future room-specific firmware would "
            "differentiate them",
        )

    def test_living_and_corridor_bundles_are_preview_candidate_with_led(self):
        for sku in ("S360-KIT-LIVING-P", "S360-KIT-CORRIDOR-P"):
            bundle = self.by_sku[sku]
            self.assertIn(
                LED_BOARD_SKU,
                bundle["included_board_skus"],
                f"{sku} must include the LED board ({LED_BOARD_SKU})",
            )
            self.assertEqual(
                bundle["current_release_status"],
                "preview-candidate",
                f"{sku} must be preview-candidate while LED remains preview",
            )

    def test_expected_bundle_skus_present(self):
        expected = {
            "S360-KIT-BATH-P",
            "S360-KIT-KITCHEN-P",
            "S360-KIT-LIVING-P",
            "S360-KIT-BEDROOM-P",
            "S360-KIT-CORRIDOR-P",
        }
        actual = {bundle["bundle_sku"] for bundle in self.bundles}
        self.assertEqual(
            expected,
            actual,
            f"BUNDLE-SKU-MATRIX-001 defines exactly the bundle set {sorted(expected)}; "
            f"found {sorted(actual)}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

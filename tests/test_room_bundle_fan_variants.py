#!/usr/bin/env python3
"""Tests for the Bathroom & Kitchen fan-control PREVIEW bundle variants.

Covers ``config/room-bundle-fan-variants.json`` (ROOM-BUNDLE-FAN-VARIANTS-002),
which promotes the Bathroom and Kitchen PoE room-bundle fan-control variants
from planning-only (ROOM-BUNDLE-FAN-VARIANTS-001) to an explicit PREVIEW bundle
plan: WebFlash easy mode becomes a bundle picker in which a fan-control variant
MAY appear as an Advanced-install-only, acknowledgement-gated PREVIEW bundle
(with warnings), while the stable / full release of every fan-control variant
stays gated behind hardware / bench-evidence / compliance gates.

This is source-of-truth metadata only: it publishes no firmware, adds no
``config/webflash-builds.json`` row, and never touches the WebFlash repo. The
contract this file locks in (task ROOM-BUNDLE-FAN-VARIANTS-002 §7):

* all fan variants reference a valid base bundle;
* only Bathroom / Kitchen may have fan variants;
* TRIAC is never stable / recommended / default (Bathroom-only, advanced-only,
  build-blocked, never normal "easy" exposure; Kitchen has no TRIAC variant);
* preview does NOT require hardware proof;
* stable STILL requires hardware / evidence / compliance;
* missing full-bundle configs are explicitly marked missing, never silently
  exposed, and a fan-only config is never substituted for a room-bundle SKU.

Uses Python's stdlib unittest (matching this repo's no-pytest convention). Run::

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
PREVIEW_TARGETS_PATH = REPO_ROOT / "config" / "preview-release-targets.json"

# Fan-driver boards that may appear as a variant driver. TRIAC (S360-320) is
# now ALLOWED, but only for the Bathroom, only as an advanced / manual-warning
# variant, and only as the (currently build-blocked) advanced-preview tier.
ALLOWED_FAN_DRIVER_SKUS = frozenset({"S360-310", "S360-311", "S360-312", "S360-320"})
ADVANCED_ONLY_FAN_DRIVER_SKUS = frozenset({"S360-320"})
# Only the Bathroom and Kitchen base bundles may have fan variants.
ALLOWED_BASE_BUNDLE_SKUS = frozenset({"S360-KIT-BATH-P", "S360-KIT-KITCHEN-P"})
# Base bundles that must never appear as a fan-variant base.
FORBIDDEN_BASE_BUNDLE_SKUS = frozenset(
    {"S360-KIT-CORRIDOR-P", "S360-KIT-LIVING-P", "S360-KIT-BEDROOM-P"}
)
# The seven explicit variants: four Bathroom + three Kitchen.
EXPECTED_VARIANT_SKUS = frozenset(
    {
        "S360-KIT-BATH-P-REL",
        "S360-KIT-BATH-P-TRIAC",
        "S360-KIT-BATH-P-PWM",
        "S360-KIT-BATH-P-DAC",
        "S360-KIT-KITCHEN-P-REL",
        "S360-KIT-KITCHEN-P-DAC",
        "S360-KIT-KITCHEN-P-PWM",
    }
)
ALLOWED_FIRMWARE_CONFIG_STATUS = frozenset(
    {
        "buildable-preview-published",
        "defined-build-blocked",
        "preview-planned-missing-config",
    }
)
ALLOWED_PREVIEW_STATUS = frozenset(
    {"preview", "advanced-preview-build-blocked", "preview-planned-missing-config"}
)
# Bare fan-only config strings that must NEVER be mapped to a room-bundle SKU
# (they omit the bundle's room-sensing modules).
FAN_ONLY_CONFIGS = frozenset(
    {
        "Ceiling-POE-FanRelay",
        "Ceiling-POE-FanPWM",
        "Ceiling-POE-FanDAC",
        "Ceiling-POE-FanTRIAC",
    }
)
CONTROL_TYPE_TO_FAN_TOKEN = {
    "relay": "FanRelay",
    "pwm": "FanPWM",
    "0-10V": "FanDAC",
    "triac": "FanTRIAC",
}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class RoomBundleFanVariantsTests(unittest.TestCase):
    """Preview-bundle contract for the fan-control variant candidates."""

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(FAN_VARIANTS_PATH)
        cls.variants = cls.doc["fan_variant_candidates"]
        cls.base_bundle_skus = {
            b["bundle_sku"] for b in _load(BUNDLE_SKUS_PATH)["bundles"]
        }
        # WebFlash builds are keyed by firmware config_string. A variant must
        # never be silently treated as already a committed WebFlash build.
        cls.webflash_config_strings = {
            entry["config_string"]
            for entry in _load(WEBFLASH_BUILDS_PATH).get("builds", []) or []
            if entry.get("config_string")
        }
        preview = _load(PREVIEW_TARGETS_PATH)
        cls.preview_config_strings = {
            t["config_string"] for t in preview.get("targets", [])
        }
        cls.preview_import_eligible = {
            t["config_string"]
            for t in preview.get("targets", [])
            if (t.get("webflash_import_eligibility") or {}).get("eligible") is True
        }

    # -- identity / promotion metadata -----------------------------------

    def test_is_the_002_promotion(self):
        self.assertEqual(self.doc.get("id"), "ROOM-BUNDLE-FAN-VARIANTS-002")
        self.assertEqual(self.doc.get("supersedes"), "ROOM-BUNDLE-FAN-VARIANTS-001")

    def test_has_fan_variant_candidates(self):
        self.assertIsInstance(self.variants, list)
        self.assertEqual(len(self.variants), len(EXPECTED_VARIANT_SKUS))

    def test_exactly_the_seven_expected_variants(self):
        skus = {v["sku"] for v in self.variants}
        self.assertEqual(skus, set(EXPECTED_VARIANT_SKUS))

    def test_bundle_skus_are_unique(self):
        skus = [v["sku"] for v in self.variants]
        self.assertEqual(len(skus), len(set(skus)))

    # -- task §7: all fan variants reference valid base bundles -----------

    def test_every_base_bundle_exists_in_room_bundle_skus(self):
        for v in self.variants:
            self.assertIn(
                v["base_bundle"],
                self.base_bundle_skus,
                f"variant {v['sku']!r} references base bundle "
                f"{v['base_bundle']!r} which does not exist in "
                "config/room-bundle-skus.json",
            )

    # -- task §7: only Bathroom / Kitchen may have fan variants -----------

    def test_only_bathroom_and_kitchen_base_bundles(self):
        for v in self.variants:
            self.assertIn(
                v["base_bundle"],
                ALLOWED_BASE_BUNDLE_SKUS,
                f"variant {v['sku']!r} uses base bundle {v['base_bundle']!r}; "
                "only Bathroom / Kitchen may have fan variants",
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
                f"variant {v['sku']!r} references fan driver {v['fan_driver']!r}",
            )

    # -- task §7: TRIAC is not stable / recommended / default -------------

    def test_triac_only_for_bathroom_and_advanced_only(self):
        triac = [v for v in self.variants if v["fan_driver"] == "S360-320"]
        # There is exactly one TRIAC variant and it is the Bathroom one.
        self.assertEqual(
            {v["sku"] for v in triac},
            {"S360-KIT-BATH-P-TRIAC"},
            "TRIAC must appear only as the single Bathroom advanced variant",
        )
        for v in triac:
            self.assertEqual(v["room"], "bathroom")
            self.assertEqual(v["control_type"], "triac")
            self.assertTrue(
                v["webflash_advanced_mode_only"],
                "Bathroom TRIAC must be advanced-mode-only (never normal easy)",
            )
            self.assertFalse(
                v["webflash_easy_mode_eligible"],
                "Bathroom TRIAC must not be a normal easy-mode option",
            )
            self.assertEqual(v["preview_status"], "advanced-preview-build-blocked")
            self.assertEqual(v["firmware_config_status"], "defined-build-blocked")

    def test_no_kitchen_triac_variant(self):
        for v in self.variants:
            if v["base_bundle"] == "S360-KIT-KITCHEN-P":
                self.assertNotEqual(
                    v["fan_driver"],
                    "S360-320",
                    f"Kitchen variant {v['sku']!r} must not be TRIAC",
                )
                self.assertNotEqual(v["control_type"], "triac")

    def test_no_variant_is_stable_recommended_or_default(self):
        for v in self.variants:
            self.assertEqual(
                v["stable_status"],
                "blocked",
                f"variant {v['sku']!r} stable_status must be 'blocked'",
            )
            self.assertFalse(v["recommended"], f"{v['sku']} must not be recommended")
            self.assertFalse(
                v["customer_default"], f"{v['sku']} must not be a customer default"
            )

    def test_advanced_only_drivers_are_never_easy_mode(self):
        for v in self.variants:
            if v["fan_driver"] in ADVANCED_ONLY_FAN_DRIVER_SKUS:
                self.assertFalse(v["webflash_easy_mode_eligible"])
                self.assertTrue(v["webflash_advanced_mode_only"])

    # -- task §7: preview does NOT require hardware proof -----------------

    def test_preview_does_not_require_hardware_proof(self):
        self.assertFalse(
            self.doc["policy"]["preview_requires_hardware_proof"],
            "policy must state preview does not require hardware proof",
        )
        for v in self.variants:
            # No variant may claim bench evidence or compliance for its preview.
            self.assertFalse(
                v["bench_evidence_claimed"], f"{v['sku']} claims bench evidence"
            )
            self.assertFalse(
                v["compliance_claimed"], f"{v['sku']} claims compliance"
            )
        # The one published preview (Bathroom Relay) is preview-eligible despite
        # carrying only stable-only (hardware/evidence) blockers.
        relay = next(v for v in self.variants if v["sku"] == "S360-KIT-BATH-P-REL")
        self.assertEqual(relay["firmware_config_status"], "buildable-preview-published")
        self.assertEqual(relay["preview_status"], "preview")
        self.assertTrue(relay["webflash_easy_mode_eligible"])
        self.assertTrue(
            relay["stable_blockers"],
            "even a preview-eligible variant must keep its stable blockers",
        )

    # -- task §7: stable STILL requires hardware / evidence / compliance --

    def test_stable_still_requires_hardware_evidence_compliance(self):
        self.assertTrue(
            self.doc["policy"]["stable_full_release_remains_hardware_gated"]
        )
        self.assertTrue(
            self.doc["policy"]["stable_requires_hardware_evidence_and_compliance"]
        )
        for v in self.variants:
            self.assertEqual(v["stable_status"], "blocked")
            self.assertTrue(
                v["stable_blockers"],
                f"variant {v['sku']!r} must record at least one stable blocker",
            )

    # -- task §7: missing configs explicit, never silently exposed --------

    def test_firmware_config_status_is_valid(self):
        for v in self.variants:
            self.assertIn(v["firmware_config_status"], ALLOWED_FIRMWARE_CONFIG_STATUS)
            self.assertIn(v["preview_status"], ALLOWED_PREVIEW_STATUS)

    def test_missing_configs_are_marked_not_exposed(self):
        missing = [
            v
            for v in self.variants
            if v["firmware_config_status"] == "preview-planned-missing-config"
        ]
        # Five of the seven variants are missing-config today.
        self.assertEqual(len(missing), 5)
        for v in missing:
            self.assertFalse(
                v["firmware_config_exists"],
                f"{v['sku']}: missing-config but firmware_config_exists true",
            )
            self.assertFalse(
                v["webflash_easy_mode_eligible"],
                f"{v['sku']}: missing-config must not be easy-mode eligible",
            )
            self.assertFalse(
                v["webflash_exposed"],
                f"{v['sku']}: missing-config must not be exposed",
            )
            self.assertEqual(v["preview_status"], "preview-planned-missing-config")
            # The intended config must genuinely be absent from the release sources.
            cfg = v["intended_firmware_config_string"]
            self.assertNotIn(
                cfg,
                self.webflash_config_strings,
                f"{v['sku']}: marked missing but {cfg!r} is a WebFlash build",
            )
            self.assertNotIn(
                cfg,
                self.preview_config_strings,
                f"{v['sku']}: marked missing but {cfg!r} is a preview target",
            )

    def test_no_fan_only_config_mapped_to_a_room_bundle(self):
        for v in self.variants:
            cfg = v["intended_firmware_config_string"]
            self.assertNotIn(
                cfg,
                FAN_ONLY_CONFIGS,
                f"{v['sku']}: maps to bare fan-only config {cfg!r}",
            )
            # Composition must include the base bundle's room-module tokens AND
            # the control type's fan token (proves it is a real bundle config).
            required = self.doc["base_bundle_room_module_tokens"][v["base_bundle"]]
            fan_token = CONTROL_TYPE_TO_FAN_TOKEN[v["control_type"]]
            for token in list(required) + [fan_token]:
                self.assertIn(
                    token,
                    cfg,
                    f"{v['sku']}: intended config {cfg!r} missing {token!r}",
                )
            self.assertFalse(
                v["composition_check"]["fan_only_config_substituted"],
                f"{v['sku']}: composition_check admits a fan-only substitution",
            )

    def test_only_published_preview_is_easy_mode_eligible(self):
        for v in self.variants:
            if v["webflash_easy_mode_eligible"]:
                self.assertEqual(
                    v["firmware_config_status"],
                    "buildable-preview-published",
                    f"{v['sku']}: easy-mode eligible without a published build",
                )
                cfg = v["intended_firmware_config_string"]
                self.assertIn(
                    cfg,
                    self.preview_import_eligible,
                    f"{v['sku']}: easy-mode eligible but {cfg!r} is not a "
                    "WebFlash-import-eligible preview target",
                )
        # Exactly one variant (Bathroom Relay) is easy-mode eligible today.
        eligible = [v["sku"] for v in self.variants if v["webflash_easy_mode_eligible"]]
        self.assertEqual(eligible, ["S360-KIT-BATH-P-REL"])

    # -- no committed WebFlash exposure / no firmware release -------------

    def test_no_variant_is_a_committed_webflash_build(self):
        # webflash_exposed means "a committed config/webflash-builds.json row".
        # No fan row is added by this PR, so it is false for every variant.
        for v in self.variants:
            self.assertFalse(
                v["webflash_exposed"], f"{v['sku']}: webflash_exposed must be False"
            )
            self.assertNotIn(
                v["intended_firmware_config_string"],
                self.webflash_config_strings,
                f"{v['sku']}: intended config must not be a committed WebFlash build",
            )

    def test_no_variant_is_buyable(self):
        for v in self.variants:
            self.assertFalse(v["buyable"], f"{v['sku']} must not be buyable")
            self.assertEqual(
                v["commercial_availability"],
                "waitlist-only",
                f"{v['sku']} must be waitlist-only (hidden / not buyable)",
            )

    def test_scope_publishes_no_firmware_and_no_webflash_repo_change(self):
        scope = self.doc["scope"]
        for flag in (
            "publishes_firmware",
            "touches_webflash_repo",
            "adds_webflash_builds_entries",
            "marks_any_variant_stable",
            "marks_any_variant_recommended_or_default",
            "exposes_any_variant_buyable",
            "exposes_kitchen_triac",
            "maps_fan_only_config_to_room_bundle",
            "claims_hardware_proof",
            "claims_compliance",
            "claims_triac_safety_or_compliance_proof",
        ):
            self.assertIs(scope[flag], False, f"scope.{flag} must be False")

    # -- warning copy ----------------------------------------------------

    def test_every_variant_carries_resolvable_warning_copy(self):
        warning_copy = self.doc["warning_copy"]
        for v in self.variants:
            key = v["warning_copy_key"]
            self.assertIn(key, warning_copy, f"{v['sku']}: unknown warning key {key!r}")
            self.assertEqual(
                v["warning_copy"],
                warning_copy[key],
                f"{v['sku']}: inline warning_copy diverges from the keyed copy",
            )
        # The advanced (TRIAC) warning must carry the mains-voltage risk language.
        triac = next(v for v in self.variants if v["control_type"] == "triac")
        self.assertEqual(triac["warning_copy_key"], "advanced-preview")
        self.assertIn("MAINS-VOLTAGE", triac["warning_copy"])

    def test_control_types_not_interchangeable_flag(self):
        self.assertTrue(
            self.doc["policy"]["control_types_not_interchangeable_at_runtime"]
        )


def test_main():
    unittest.main()


if __name__ == "__main__":
    unittest.main(verbosity=2)

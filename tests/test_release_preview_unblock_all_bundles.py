#!/usr/bin/env python3
"""Tests for RELEASE-PREVIEW-UNBLOCK-ALL-BUNDLES-001.

This guards the policy decision that **hardware / bench / compliance /
commercial-availability blockers gate STABLE / full release only** and therefore
**never block a PREVIEW artifact** for a buildable firmware target — including
the fan-control and TRIAC paths.

These are policy / eligibility guards. They assert nothing about firmware
behaviour, publish no artifact, and read only committed config files:

  * ``config/release-channel-policy.json``      (RELEASE-PREVIEW-ALL-PRODUCTS-001)
  * ``config/preview-release-targets.json``     (RELEASE-PREVIEW-TARGETS-ALL-PRODUCTS-001)
  * ``config/manual-firmware-artifacts.json``   (fan manual-preview lane)
  * ``config/webflash-builds.json``             (sole release-eligibility ledger)
  * ``config/product-catalog.json``             (lifecycle layer)
  * ``config/shop-commercial-source-of-truth.json`` (commercial posture)

Invariants asserted (matching the task contract):

  - every buildable product has preview eligibility (``preview_allowed``);
  - missing hardware proof does **not** block preview;
  - missing hardware proof **still** blocks stable;
  - TRIAC remains advanced / manual-warning only;
  - fan-control builds remain manual / preview only;
  - no preview build is stable / recommended / default;
  - Simple install (stable Bathroom PoE) remains unchanged;
  - candidate bundles remain hidden / not buyable;
  - no stable / full release unblock happens.
"""

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
POLICY_PATH = REPO_ROOT / "config" / "release-channel-policy.json"
TARGETS_PATH = REPO_ROOT / "config" / "preview-release-targets.json"
MANUAL_PATH = REPO_ROOT / "config" / "manual-firmware-artifacts.json"
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"
SHOP_PATH = REPO_ROOT / "config" / "shop-commercial-source-of-truth.json"

DECISION_ID = "RELEASE-PREVIEW-UNBLOCK-ALL-BUNDLES-001"
SIMPLE_INSTALL_CONFIG = "Ceiling-POE-VentIQ-RoomIQ"
SIMPLE_INSTALL_ARTIFACT = "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin"
FAN_DRIVER_TOKENS = ("FanRelay", "FanPWM", "FanDAC", "FanTRIAC")
EXPLICIT_WARNING_FAMILIES = {"FanRelay", "FanPWM", "FanDAC", "FanTRIAC", "LED"}


def _load(path: Path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


class DecisionRecordedTests(unittest.TestCase):
    """The unblock decision is recorded in both machine-readable config files."""

    @classmethod
    def setUpClass(cls):
        cls.policy = _load(POLICY_PATH)
        cls.targets = _load(TARGETS_PATH)

    def test_policy_records_the_decision(self):
        decision = self.policy["unblock_all_bundles_decision"]
        self.assertEqual(decision["id"], DECISION_ID)
        self.assertEqual(decision["rule"], "lack_of_hardware_proof_blocks_stable_only")
        # Stable-only blocker classes include hardware / bench / compliance /
        # commercial; the only preview blocker class is buildability.
        self.assertEqual(
            set(decision["stable_only_blocker_classes"]),
            {"hardware-proof", "bench-evidence", "compliance", "commercial-availability"},
        )
        self.assertEqual(set(decision["preview_blocker_classes"]), {"buildability"})

    def test_targets_manifest_echoes_the_decision(self):
        decision = self.targets["unblock_all_bundles_decision"]
        self.assertEqual(decision["id"], DECISION_ID)

    def test_decision_guarantees_are_all_protective(self):
        g = self.policy["unblock_all_bundles_decision"]["guarantees"]
        for flag in (
            "nothing_becomes_stable",
            "nothing_becomes_recommended_or_default",
            "nothing_becomes_buyable",
            "simple_install_remains_stable_bathroom_poe_only",
            "advanced_manual_preview_is_only_exposure_for_risky_or_unverified_builds",
            "triac_stays_advanced_manual_warning_only",
            "fan_drivers_stay_manual_preview_only",
            "candidate_bundles_stay_hidden_not_buyable",
            "stable_full_release_gates_unchanged",
            "publishes_no_firmware",
            "touches_no_webflash_repo",
            "touches_no_firmware_sources_or_manifest",
        ):
            self.assertTrue(g[flag], f"guarantee {flag} must be true")

    def test_new_guardrail_flags_present(self):
        g = self.policy["guardrails"]
        for flag in (
            "hardware_proof_blocker_is_stable_only",
            "bench_evidence_blocker_is_stable_only",
            "compliance_blocker_is_stable_only",
            "commercial_availability_blocker_is_stable_only",
            "only_buildability_blocker_can_block_preview",
            "every_buildable_target_is_preview_eligible",
            "simple_install_remains_stable_bathroom_poe_only",
            "advanced_manual_preview_is_only_risky_build_exposure_path",
            "candidate_bundles_stay_hidden_and_not_buyable",
            "no_stable_or_full_release_unblock",
        ):
            self.assertTrue(g[flag], f"guardrail {flag} must be true")


class EveryBuildableProductIsPreviewEligibleTests(unittest.TestCase):
    """Every recorded target carries explicit preview eligibility."""

    @classmethod
    def setUpClass(cls):
        cls.policy = _load(POLICY_PATH)
        cls.targets = _load(TARGETS_PATH)

    def test_every_policy_matrix_row_is_preview_allowed(self):
        for row in self.policy["preview_release_matrix"]:
            self.assertTrue(
                row["preview_allowed"],
                f"{row['config_string']} must be preview_allowed",
            )

    def test_every_concrete_target_is_preview_allowed(self):
        for target in self.targets["targets"]:
            self.assertTrue(
                target["preview_allowed"],
                f"{target['target_id']} must be preview_allowed",
            )

    def test_every_preview_target_requires_a_warning(self):
        for target in self.targets["targets"]:
            self.assertTrue(target["preview_warning_required"])


class MissingHardwareProofDoesNotBlockPreviewTests(unittest.TestCase):
    """Hardware-only blockers gate stable only; preview stays open."""

    @classmethod
    def setUpClass(cls):
        cls.policy = _load(POLICY_PATH)
        cls.targets = _load(TARGETS_PATH)

    def test_preview_tier_needs_no_hardware_proof(self):
        tiers = self.policy["channel_tiers"]
        self.assertFalse(tiers["preview"]["hardware_proof_required"])
        self.assertFalse(tiers["advanced-preview"]["hardware_proof_required"])

    def test_split_guardrails_declared(self):
        g = self.policy["guardrails"]
        self.assertTrue(g["lack_of_hardware_proof_blocks_stable_only"])
        self.assertTrue(g["lack_of_hardware_proof_does_not_block_preview"])

    def test_a_recorded_stable_blocker_never_revokes_preview_allowed(self):
        # Every non-stable matrix row carries a stable_blocker AND stays
        # preview_allowed — the blocker gates stable, not preview.
        for row in self.policy["preview_release_matrix"]:
            if row["intended_channel"] == "stable":
                continue
            self.assertTrue(row["stable_blocker"])
            self.assertTrue(row["preview_allowed"])

    def test_non_buildability_blockers_marked_stable_only(self):
        # Every non-stable, non-TRIAC target records its stable_blocker as
        # stable-only (does not gate preview). TRIAC is the sole exception
        # because HW-005 is a genuine buildability blocker.
        for target in self.targets["targets"]:
            if target["channel_tier"] == "stable":
                continue
            if target.get("is_triac"):
                continue
            self.assertTrue(
                target["blocker_is_stable_only"],
                f"{target['target_id']}: stable_blocker must be stable-only",
            )
            self.assertIsNone(
                target["build_blocker"],
                f"{target['target_id']}: non-TRIAC preview must have no build blocker",
            )

    def test_no_target_publication_status_blocks_preview(self):
        for target in self.targets["targets"]:
            self.assertNotIn("blocked-from-preview", str(target["publication_status"]))
        # Lanes are the three releasable lanes, never a "blocked" lane.
        lanes = {t["delivery_lane"] for t in self.targets["targets"]}
        self.assertEqual(
            lanes, {"webflash", "manual-preview", "advanced-manual-preview"}
        )


class MissingHardwareProofStillBlocksStableTests(unittest.TestCase):
    """Stable promotion is unchanged — evidence still required."""

    @classmethod
    def setUpClass(cls):
        cls.policy = _load(POLICY_PATH)

    def test_stable_tier_still_evidence_gated(self):
        stable = self.policy["channel_tiers"]["stable"]
        self.assertTrue(stable["hardware_proof_required"])
        self.assertTrue(stable["evidence_gated"])
        self.assertTrue(stable["requires_schematic_status_verified"])
        self.assertTrue(stable["requires_lifecycle_production"])

    def test_every_non_stable_row_keeps_a_stable_blocker(self):
        for row in self.policy["preview_release_matrix"]:
            if row["intended_channel"] == "stable":
                continue
            self.assertTrue(
                row["stable_blocker"],
                f"{row['config_string']} must keep its stable blocker",
            )


class TriacAdvancedManualWarningOnlyTests(unittest.TestCase):
    """TRIAC may be advanced-preview only — never stable / recommended / default."""

    @classmethod
    def setUpClass(cls):
        cls.policy = _load(POLICY_PATH)
        cls.targets = _load(TARGETS_PATH)
        cls.triac_targets = [
            t for t in cls.targets["targets"] if t.get("is_triac")
        ]

    def test_exactly_one_triac_target(self):
        self.assertEqual(len(self.triac_targets), 1)

    def test_triac_is_advanced_preview_with_mains_warning(self):
        triac = self.triac_targets[0]
        self.assertEqual(triac["channel_tier"], "advanced-preview")
        self.assertEqual(triac["delivery_lane"], "advanced-manual-preview")
        self.assertEqual(triac["warning_copy_key"], "advanced-preview")
        self.assertIn("MAINS", triac["release_note_warning"].upper())

    def test_triac_preview_allowed_but_cut_gated_by_buildability(self):
        triac = self.triac_targets[0]
        self.assertTrue(triac["preview_allowed"])
        self.assertTrue(triac["preview_warning_required"])
        # Hardware PROOF does not block TRIAC preview; only buildability does.
        self.assertFalse(triac["hardware_proof_blocks_preview"])
        self.assertTrue(triac["preview_cut_gated_by_buildability"])
        self.assertTrue(triac["build_blocker"])
        self.assertIn("HW-005", triac["build_blocker"])

    def test_triac_never_stable_recommended_default_required(self):
        triac = self.triac_targets[0]
        self.assertNotEqual(triac["channel_tier"], "stable")
        for flag in (
            "recommended",
            "customer_default",
            "required_config",
            "customer_kit_default",
        ):
            self.assertFalse(triac[flag], f"TRIAC {flag} must be false")
        self.assertFalse(triac["webflash_import_eligibility"]["eligible"])

    def test_triac_makes_no_safety_or_compliance_claim(self):
        triac = self.triac_targets[0]
        self.assertFalse(triac["bench_evidence_claimed"])
        self.assertFalse(triac["schematic_status_verified_claim"])
        # Stable blocker keeps the compliance / mains-voltage review.
        self.assertIn("COMPLIANCE-001", triac["stable_blocker"])


class FanDriversManualPreviewOnlyTests(unittest.TestCase):
    """FanRelay / FanPWM / FanDAC stay manual / preview only."""

    @classmethod
    def setUpClass(cls):
        cls.targets = _load(TARGETS_PATH)
        cls.builds = _load(BUILDS_PATH)
        cls.catalog = _load(CATALOG_PATH)
        cls.manual = _load(MANUAL_PATH)
        cls.fan_targets = [
            t
            for t in cls.targets["targets"]
            if t.get("is_fan") and not t.get("is_triac")
        ]

    def test_three_fan_families(self):
        families = {t["family"] for t in self.fan_targets}
        self.assertEqual(families, {"FanRelay", "FanPWM", "FanDAC"})

    def test_fans_use_manual_preview_lane_and_are_not_webflash_importable(self):
        for t in self.fan_targets:
            self.assertEqual(t["delivery_lane"], "manual-preview")
            self.assertFalse(t["webflash_import_eligibility"]["eligible"])
            self.assertTrue(t["preview_allowed"])

    def test_fans_absent_from_webflash_ledger(self):
        ledger = {b["config_string"] for b in self.builds["builds"]}
        for t in self.fan_targets:
            self.assertNotIn(t["config_string"], ledger)

    def test_fan_catalog_entries_stay_off_the_build_matrix(self):
        catalog = {
            p.get("config_string"): p
            for p in self.catalog["products"]
            if p.get("config_string")
        }
        for t in self.fan_targets:
            entry = catalog.get(t["config_string"])
            if entry is not None:
                self.assertFalse(
                    entry.get("webflash_build_matrix", False),
                    f"{t['config_string']} must stay off the WebFlash build matrix",
                )

    def test_fan_manual_lane_candidates_preserve_stable_blocker_and_caveat(self):
        for candidate in self.manual["candidates"]:
            self.assertEqual(candidate["preview_channel"], "preview")
            self.assertEqual(candidate["delivery_lane"], "manual-preview")
            self.assertFalse(candidate["webflash_importable"])
            self.assertTrue(candidate["stable_blocker"])
            self.assertTrue(candidate["caveat"])


class ExplicitWarningsPreservedTests(unittest.TestCase):
    """Explicit warnings are preserved for every unverified family."""

    @classmethod
    def setUpClass(cls):
        cls.policy = _load(POLICY_PATH)
        cls.targets = _load(TARGETS_PATH)

    def test_decision_lists_the_explicit_warning_families(self):
        listed = set(
            self.policy["unblock_all_bundles_decision"]["explicit_warning_families"]
        )
        self.assertEqual(listed, EXPLICIT_WARNING_FAMILIES)

    def test_each_unverified_family_target_requires_warning_copy(self):
        by_family = {t["family"]: t for t in self.targets["targets"]}
        for family in EXPLICIT_WARNING_FAMILIES:
            self.assertIn(family, by_family, f"{family} target must exist")
            target = by_family[family]
            self.assertTrue(target["warning_copy_required"])
            self.assertTrue(target["release_note_warning"])
            self.assertTrue(target["stable_blocker"])


class NoPreviewBuildIsStableOrDefaultTests(unittest.TestCase):
    """No preview target is stable / recommended / default / required."""

    @classmethod
    def setUpClass(cls):
        cls.targets = _load(TARGETS_PATH)

    def test_preview_targets_never_recommended_default_or_required(self):
        for t in self.targets["targets"]:
            if t["channel_tier"] == "stable":
                continue
            for flag in (
                "recommended",
                "customer_default",
                "required_config",
                "customer_kit_default",
            ):
                self.assertFalse(t[flag], f"{t['target_id']} {flag} must be false")

    def test_exactly_one_stable_target(self):
        stable = [t for t in self.targets["targets"] if t["channel_tier"] == "stable"]
        self.assertEqual(len(stable), 1)
        self.assertEqual(stable[0]["config_string"], SIMPLE_INSTALL_CONFIG)


class SimpleInstallUnchangedTests(unittest.TestCase):
    """Simple install remains the stable Bathroom PoE build only."""

    @classmethod
    def setUpClass(cls):
        cls.targets = _load(TARGETS_PATH)
        cls.builds = _load(BUILDS_PATH)
        cls.shop = _load(SHOP_PATH)

    def test_single_stable_build_is_bathroom_poe(self):
        stable_builds = [
            b for b in self.builds["builds"] if b["channel"] == "stable"
        ]
        self.assertEqual(len(stable_builds), 1)
        self.assertEqual(stable_builds[0]["config_string"], SIMPLE_INSTALL_CONFIG)
        self.assertEqual(stable_builds[0]["artifact_name"], SIMPLE_INSTALL_ARTIFACT)

    def test_shop_launch_product_is_the_stable_bathroom_build(self):
        launch = self.shop["launch_product"]
        self.assertEqual(launch["firmware_config"], SIMPLE_INSTALL_CONFIG)
        self.assertEqual(launch["artifact_name"], SIMPLE_INSTALL_ARTIFACT)

    def test_stable_baseline_target_unchanged_flags(self):
        stable = next(
            t for t in self.targets["targets"] if t["channel_tier"] == "stable"
        )
        self.assertTrue(stable["recommended"])
        self.assertTrue(stable["customer_default"])
        self.assertTrue(stable["required_config"])
        self.assertFalse(stable["warning_copy_required"])


class CandidateBundlesHiddenNotBuyableTests(unittest.TestCase):
    """Candidate room bundles stay hidden and not buyable."""

    @classmethod
    def setUpClass(cls):
        cls.shop = _load(SHOP_PATH)

    def test_candidate_bundles_not_buyable(self):
        vis = self.shop["candidate_bundle_visibility"]
        self.assertEqual(vis["default"], "hidden-from-shop-navigation")
        self.assertFalse(vis["buy_button_allowed"])
        self.assertFalse(self.shop["guardrails"]["candidate_bundles_buyable"])

    def test_candidate_bundle_list_is_the_four_room_bundles(self):
        vis = self.shop["candidate_bundle_visibility"]
        self.assertEqual(
            set(vis["candidate_bundles"]),
            {
                "S360-KIT-KITCHEN-P",
                "S360-KIT-LIVING-P",
                "S360-KIT-BEDROOM-P",
                "S360-KIT-CORRIDOR-P",
            },
        )

    def test_shop_source_of_truth_untouched_guardrails(self):
        g = self.shop["guardrails"]
        self.assertEqual(g["canonical_room_bundle_sku"], "S360-KIT-BATH-P")
        self.assertFalse(g["publishes_firmware"])
        self.assertFalse(g["touches_webflash_repo"])


class NoStableOrFullReleaseUnblockTests(unittest.TestCase):
    """No stable / full release unblock happens."""

    @classmethod
    def setUpClass(cls):
        cls.policy = _load(POLICY_PATH)
        cls.targets = _load(TARGETS_PATH)

    def test_policy_scope_stays_metadata_only(self):
        scope = self.policy["scope"]
        self.assertFalse(scope["publishes_artifacts"])
        self.assertFalse(scope["touches_webflash_repo"])
        self.assertFalse(scope["marks_any_product_stable"])
        self.assertFalse(scope["claims_bench_evidence"])
        self.assertFalse(scope["claims_compliance"])

    def test_targets_scope_stays_metadata_only(self):
        scope = self.targets["scope"]
        self.assertFalse(scope["publishes_artifacts"])
        self.assertFalse(scope["touches_webflash_repo"])
        self.assertFalse(scope["adds_webflash_builds_entries"])
        self.assertFalse(scope["flips_product_catalog_status"])
        self.assertFalse(scope["marks_any_product_stable"])

    def test_no_target_was_promoted_to_stable(self):
        stable = [t for t in self.targets["targets"] if t["channel_tier"] == "stable"]
        self.assertEqual([t["config_string"] for t in stable], [SIMPLE_INSTALL_CONFIG])


if __name__ == "__main__":
    unittest.main(verbosity=2)

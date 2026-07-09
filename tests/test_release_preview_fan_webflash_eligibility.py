#!/usr/bin/env python3
"""Regression guard for RELEASE-PREVIEW-FAN-WEBFLASH-ELIGIBILITY-001.

FanRelay / FanPWM / FanDAC are now preview / manual-preview WebFlash-import
ELIGIBLE (Advanced-install-only, acknowledgement-gated) so downstream WebFlash no
longer treats the catalog ``webflash_build_matrix: false`` or the prior
``WEBFLASH-RELAY-001 BLOCKED`` framing as a preview-import blocker.

The eligibility flip is import-eligibility ONLY. It is deliberately NOT:
  * a stable / full / production release (those blockers remain),
  * a recommended / default / customer-kit selection,
  * a buyable / public-shop product.

HW-RELEASE-001 (docs/hw-release-001.md, owner decision of record, 2026-07-09)
then retired the bench-proof documentation requirement as a release gate and
added declaration-driven ``config/webflash-builds.json`` release-eligibility
metadata rows for the fan candidates (release_state
``metadata-ready-unpublished``; no binary / Release / tag / manifest cut),
flipping their catalog entries to status preview / ``webflash_build_matrix:
true``. The former "no fan build row" guardrail was revised by the owner into
CHANNEL teeth, guarded below: FanPWM / FanDAC rows sit on the preview channel,
FanRelay rows on the experimental channel ONLY (mains-adjacent, COMPLIANCE-001
lane posture), and fan configs are NEVER on the stable channel or in
release_one_required_configs.

FanTRIAC stays excluded from import eligibility (eligible=false,
advanced-manual-preview) and is handled by its own separate TRIAC-specific
track. The stable Bathroom PoE build (Ceiling-POE-VentIQ-RoomIQ) is unchanged.

These are metadata-only guards. They assert nothing about firmware behaviour and
claim no hardware / bench / compliance / commercial-availability proof.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any, Dict

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGETS_PATH = REPO_ROOT / "config" / "preview-release-targets.json"
LEDGER_PATH = REPO_ROOT / "config" / "preview-fan-triac-build-rows.json"
MANUAL_PATH = REPO_ROOT / "config" / "manual-firmware-artifacts.json"
CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"

FAN_CONFIGS = (
    "Ceiling-POE-VentIQ-FanRelay-RoomIQ",
    "Ceiling-POE-FanPWM",
    "Ceiling-POE-FanDAC",
)
TRIAC_CONFIG = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"
STABLE_CONFIG = "Ceiling-POE-VentIQ-RoomIQ"
# HW-RELEASE-001 channel teeth: the only catalog / builds channel each fan
# candidate may occupy. FanRelay is mains-adjacent → experimental only;
# FanPWM / FanDAC → preview. NEVER "stable" for any fan config.
FAN_BUILD_CHANNEL = {
    "Ceiling-POE-VentIQ-FanRelay-RoomIQ": "experimental",
    "Ceiling-POE-FanPWM": "preview",
    "Ceiling-POE-FanDAC": "preview",
}
HW_RELEASE_DOC = "docs/hw-release-001.md"
HW_RELEASE_HARDWARE_STATUS = "owner-declared-bench-working-hw-release-001"
FAN_FAMILY_TOKENS = ("FanRelay", "FanPWM", "FanDAC", "FanTRIAC")


def _load(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _targets_by_cs() -> Dict[str, Dict[str, Any]]:
    return {
        t["config_string"]: t
        for t in _load(TARGETS_PATH)["targets"]
        if t.get("config_string")
    }


def _catalog_by_cs() -> Dict[str, Dict[str, Any]]:
    return {
        e["config_string"]: e
        for e in _load(CATALOG_PATH)["products"]
        if e.get("config_string")
    }


class FanPreviewImportEligibleTests(unittest.TestCase):
    """The three fan drivers are preview / manual-preview WebFlash-import eligible."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.by_cs = _targets_by_cs()

    def test_three_fan_targets_present(self) -> None:
        for cs in FAN_CONFIGS:
            self.assertIn(cs, self.by_cs, f"missing preview target for {cs!r}")

    def test_fans_are_webflash_import_eligible(self) -> None:
        for cs in FAN_CONFIGS:
            with self.subTest(config_string=cs):
                elig = self.by_cs[cs]["webflash_import_eligibility"]
                self.assertIs(
                    elig["eligible"],
                    True,
                    f"{cs!r}: preview / manual-preview WebFlash import must be "
                    "eligible (RELEASE-PREVIEW-FAN-WEBFLASH-ELIGIBILITY-001)",
                )
                self.assertEqual(
                    elig["exposure_class"],
                    "acknowledgement-gated",
                    f"{cs!r}: fan preview import is Advanced-install-only / "
                    "acknowledgement-gated",
                )

    def test_fans_stay_on_manual_preview_lane(self) -> None:
        for cs in FAN_CONFIGS:
            with self.subTest(config_string=cs):
                self.assertEqual(
                    self.by_cs[cs]["delivery_lane"],
                    "manual-preview",
                    f"{cs!r}: import-eligible but still delivered on the "
                    "manual-preview lane (no committed webflash build row)",
                )

    def test_fans_publication_status_is_preview_import_eligible(self) -> None:
        for cs in FAN_CONFIGS:
            with self.subTest(config_string=cs):
                self.assertEqual(
                    self.by_cs[cs]["publication_status"],
                    "preview-import-eligible",
                )

    def test_eligibility_reason_records_the_decision(self) -> None:
        for cs in FAN_CONFIGS:
            with self.subTest(config_string=cs):
                reason = self.by_cs[cs]["webflash_import_eligibility"]["reason"].lower()
                self.assertIn("eligible", reason)
                self.assertIn("manual-preview", reason)


class FanNotStableNotRecommendedNotBuyableTests(unittest.TestCase):
    """Eligibility is NOT stable / recommended / default / buyable."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.by_cs = _targets_by_cs()
        cls.ledger = {r["config_string"]: r for r in _load(LEDGER_PATH)["rows"]}

    def test_fans_are_not_stable(self) -> None:
        for cs in FAN_CONFIGS:
            with self.subTest(config_string=cs):
                t = self.by_cs[cs]
                self.assertEqual(t["channel_tier"], "preview")
                self.assertNotEqual(t["channel_tier"], "stable")
                self.assertNotEqual(t["build_channel"], "stable")

    def test_fans_are_not_recommended_default_or_required(self) -> None:
        for cs in FAN_CONFIGS:
            with self.subTest(config_string=cs):
                t = self.by_cs[cs]
                self.assertFalse(t["recommended"])
                self.assertFalse(t["customer_default"])
                self.assertFalse(t["required_config"])
                self.assertFalse(t["customer_kit_default"])

    def test_fans_are_not_buyable_or_shop_visible(self) -> None:
        # The fan-ledger commercial posture is the buyability source of truth.
        for cs in FAN_CONFIGS:
            with self.subTest(config_string=cs):
                posture = self.ledger[cs]["commercial_posture"]
                self.assertEqual(posture["visibility"], "hidden")
                self.assertFalse(posture["buyable"])
                self.assertFalse(posture["recommended"])
                self.assertFalse(posture["customer_default"])
                self.assertFalse(posture["stable"])
                self.assertFalse(posture["release_one_required_config"])


class StableBlockersRemainTests(unittest.TestCase):
    """Stable / full-release blockers are preserved on every fan target."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.by_cs = _targets_by_cs()

    def test_each_fan_records_a_stable_blocker(self) -> None:
        for cs in FAN_CONFIGS:
            with self.subTest(config_string=cs):
                t = self.by_cs[cs]
                self.assertTrue(
                    t.get("stable_blocker"),
                    f"{cs!r}: stable / full release must stay blocked",
                )
                # The blocker gates stable only, never the preview import.
                self.assertIs(t["blocker_is_stable_only"], True)
                self.assertIsNone(t.get("build_blocker"))

    def test_catalog_status_preview_on_build_matrix_never_stable(self) -> None:
        # HW-RELEASE-001 inverted the old "hardware-pending / off-matrix" pin:
        # the fan candidates' catalog entries are now status preview with
        # webflash_build_matrix true under the owner declaration. The
        # permanent teeth: the channel matches the lane and is NEVER "stable",
        # and hardware readiness is owner-declared, not proven.
        catalog = _catalog_by_cs()
        for cs, channel in FAN_BUILD_CHANNEL.items():
            with self.subTest(config_string=cs):
                entry = catalog[cs]
                self.assertEqual(entry["status"], "preview")
                self.assertIs(entry["webflash_build_matrix"], True)
                self.assertEqual(entry["channel"], channel)
                self.assertNotEqual(
                    entry["channel"],
                    "stable",
                    f"{cs!r}: fan candidates' catalog channel is never stable",
                )
                self.assertEqual(entry["hardware_status"], HW_RELEASE_HARDWARE_STATUS)
                self.assertEqual(
                    entry["artifact_name"],
                    f"Sense360-{cs}-v1.0.0-{channel}.bin",
                )
                self.assertTrue(
                    (REPO_ROOT / entry["webflash_wrapper"]).is_file(),
                    f"{cs!r}: catalog webflash_wrapper must exist on disk",
                )


class CommittedWebflashRowChannelTeethTests(unittest.TestCase):
    """HW-RELEASE-001 revised the fan-token guardrail into channel teeth: fan
    rows exist in config/webflash-builds.json but are NEVER stable."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.builds = {b["config_string"]: b for b in _load(BUILDS_PATH)["builds"]}
        cls.ledger = {r["config_string"]: r for r in _load(LEDGER_PATH)["rows"]}
        cls.manual = {c["id"]: c for c in _load(MANUAL_PATH)["candidates"]}

    def test_fan_candidate_rows_match_lane_channel(self) -> None:
        # Inverts the pre-HW-RELEASE-001 "fans absent from the ledger" pin:
        # each candidate now has a declaration-driven release-eligibility
        # METADATA row (metadata-ready-unpublished; no binary / Release / tag
        # cut) on its lane channel, never stable, hidden / not buyable.
        for cs, channel in FAN_BUILD_CHANNEL.items():
            with self.subTest(config_string=cs):
                self.assertIn(cs, self.builds)
                row = self.builds[cs]
                self.assertEqual(row["channel"], channel)
                self.assertNotEqual(row["channel"], "stable")
                self.assertEqual(row["release_state"], "metadata-ready-unpublished")
                self.assertEqual(row["owner_declaration"], HW_RELEASE_DOC)
                posture = row["commercial_posture"]
                self.assertFalse(posture["stable"])
                self.assertFalse(posture["buyable"])
                self.assertFalse(posture["recommended"])
                self.assertFalse(posture["customer_default"])
                self.assertFalse(posture["release_one_required_config"])

    def test_fan_token_rows_never_stable_channel(self) -> None:
        # The former raw fan-token scan ("no FanRelay/FanPWM/FanDAC token in
        # the ledger") is inverted into the owner's channel teeth
        # (HW-RELEASE-001): every ledger row carrying a fan-family token is on
        # the experimental channel (FanRelay, FanTRIAC) or the preview channel
        # (FanPWM, FanDAC) and NEVER on the stable channel.
        seen_tokens = set()
        for cs, row in self.builds.items():
            tokens = set(cs.split("-")) & set(FAN_FAMILY_TOKENS)
            if not tokens:
                continue
            seen_tokens |= tokens
            with self.subTest(config_string=cs):
                self.assertNotEqual(
                    row["channel"],
                    "stable",
                    f"{cs}: fan configs are NEVER on the stable channel",
                )
                if tokens & {"FanRelay", "FanTRIAC"}:
                    self.assertEqual(row["channel"], "experimental")
                else:
                    self.assertEqual(row["channel"], "preview")
                self.assertNotIn("-stable.bin", row["artifact_name"])
        # The teeth actually bit something (all four fan families present).
        self.assertEqual(seen_tokens, set(FAN_FAMILY_TOKENS))

    def test_fan_ledger_rows_stay_not_webflash_importable(self) -> None:
        # webflash_importable (committed build-matrix import) is a DIFFERENT
        # concept from import-eligibility and stays false.
        for cs in FAN_CONFIGS:
            with self.subTest(config_string=cs):
                row = self.ledger[cs]
                self.assertIs(row["webflash_importable"], False)
                self.assertIsNone(row["webflash_exposure_class"])

    def test_manual_lane_candidates_stay_non_release(self) -> None:
        top = _load(MANUAL_PATH)
        self.assertIs(top["release"], False)
        self.assertIs(top["webflash"], False)
        self.assertIsNone(top["release_channel"])
        for cand in top["candidates"]:
            with self.subTest(candidate=cand["id"]):
                self.assertIs(cand["webflash_importable"], False)


class TotalsReflectFanEligibilityTests(unittest.TestCase):
    """The preview-release-targets totals reflect the flip; TRIAC stays gated."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.totals = _load(TARGETS_PATH)["totals"]

    def test_eligible_now_and_gated_followup_counts(self) -> None:
        # 13 eligible: the 5 webflash-lane targets + the 3 standalone fan
        # drivers + the 5 HW-RELEASE-001 room-bundle fan targets the
        # reconciled manifest now enumerates. FanTRIAC stays the single gated
        # follow-up (never import-eligible from this manifest).
        self.assertEqual(self.totals["webflash_import_eligible_now"], 13)
        self.assertEqual(self.totals["webflash_import_gated_followup"], 1)

    def test_eligible_now_matches_actual_eligible_targets(self) -> None:
        targets = _load(TARGETS_PATH)["targets"]
        eligible = sum(
            1
            for t in targets
            if t.get("webflash_import_eligibility", {}).get("eligible") is True
        )
        self.assertEqual(eligible, self.totals["webflash_import_eligible_now"])


class TriacStaysExcludedTests(unittest.TestCase):
    """FanTRIAC remains excluded / separate; this PR does not touch it."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.by_cs = _targets_by_cs()
        cls.ledger = {r["config_string"]: r for r in _load(LEDGER_PATH)["rows"]}

    def test_triac_is_not_webflash_import_eligible(self) -> None:
        t = self.by_cs[TRIAC_CONFIG]
        self.assertIs(t["webflash_import_eligibility"]["eligible"], False)
        self.assertEqual(
            t["webflash_import_eligibility"]["exposure_class"],
            "acknowledgement-gated-advanced",
        )

    def test_triac_is_advanced_manual_preview_and_build_blocked(self) -> None:
        # TRIAC-UNBLOCK-BUILD-001 cleared the HW-005 build_blocker (buildable
        # now); TRIAC stays on the advanced-manual-preview lane, not
        # WebFlash-importable, with the stable_blocker citing the
        # COMPLIANCE-001-RESOLUTION-001 experimental-lane preconditions
        # (COMPLIANCE-001 closed by posture; behaviour unchanged).
        t = self.by_cs[TRIAC_CONFIG]
        self.assertEqual(t["delivery_lane"], "advanced-manual-preview")
        self.assertIsNone(t.get("build_blocker"))
        self.assertIn("COMPLIANCE-001", str(t.get("stable_blocker")))
        self.assertFalse(t["webflash_import_eligibility"]["eligible"])

    def test_triac_committed_on_experimental_channel_only(self) -> None:
        # FanTRIAC is committed in config/webflash-builds.json only on the
        # experimental self-build mains channel (TRIAC-COMMISSIONING-001); its
        # preview-eligibility target stays advanced-manual-preview and
        # NOT WebFlash-import eligible (asserted above).
        builds = {b["config_string"]: b for b in _load(BUILDS_PATH)["builds"]}
        self.assertIn(TRIAC_CONFIG, builds)
        self.assertEqual(builds[TRIAC_CONFIG]["channel"], "experimental")


class StableBathroomPoeUnchangedTests(unittest.TestCase):
    """The stable Bathroom PoE baseline is unchanged by this PR."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.by_cs = _targets_by_cs()
        cls.catalog = _catalog_by_cs()

    def test_stable_baseline_is_still_default_and_required(self) -> None:
        t = self.by_cs[STABLE_CONFIG]
        self.assertEqual(t["channel_tier"], "stable")
        self.assertIs(t["recommended"], True)
        self.assertIs(t["customer_default"], True)
        self.assertIs(t["required_config"], True)

    def test_stable_baseline_catalog_is_production(self) -> None:
        self.assertEqual(self.catalog[STABLE_CONFIG]["status"], "production")


class DownstreamMetadataNoLongerBlocksTests(unittest.TestCase):
    """Downstream-facing export/readiness metadata no longer blocks fan preview import."""

    def test_no_fan_eligibility_records_a_blocker(self) -> None:
        by_cs = _targets_by_cs()
        for cs in FAN_CONFIGS:
            with self.subTest(config_string=cs):
                elig = by_cs[cs]["webflash_import_eligibility"]
                # Eligible, and the reason explicitly disclaims the old block.
                self.assertTrue(elig["eligible"])
                reason = elig["reason"].lower()
                self.assertNotIn("stays gated", reason)
                self.assertNotIn("not a preview block", reason)

    def test_targets_manifest_decision_block_present(self) -> None:
        manifest = _load(TARGETS_PATH)
        decision = manifest.get("fan_webflash_eligibility_decision", {})
        self.assertEqual(
            decision.get("id"), "RELEASE-PREVIEW-FAN-WEBFLASH-ELIGIBILITY-001"
        )
        guarantees = decision.get("guarantees", {})
        self.assertIs(guarantees.get("no_fan_row_added_to_webflash_builds"), True)
        self.assertIs(guarantees.get("catalog_webflash_build_matrix_stays_false"), True)
        self.assertIs(guarantees.get("stable_full_release_blockers_remain"), True)
        self.assertIs(guarantees.get("triac_stays_excluded_and_separate"), True)


if __name__ == "__main__":
    unittest.main(verbosity=2)

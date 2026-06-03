#!/usr/bin/env python3
"""Regression guard for RELEASE-PREVIEW-FAN-WEBFLASH-ELIGIBILITY-001.

FanRelay / FanPWM / FanDAC are now preview / manual-preview WebFlash-import
ELIGIBLE (Advanced-install-only, acknowledgement-gated) so downstream WebFlash no
longer treats the catalog ``webflash_build_matrix: false`` or the prior
``WEBFLASH-RELAY-001 BLOCKED`` framing as a preview-import blocker.

The eligibility flip is import-eligibility ONLY. It is deliberately NOT:
  * a stable / full / production release (those blockers remain),
  * a recommended / default / customer-kit selection,
  * a buyable / public-shop product,
  * a committed ``config/webflash-builds.json`` build row (the fan-token
    guardrail and ``webflash_build_matrix: false`` stand; the one-click import is
    the separately queued downstream WF-IMPORT-RELAY-001 / -PWM-001 / -DAC-001).

FanTRIAC stays excluded (eligible=false, advanced-manual-preview, HW-005 build
blocker) and is handled by its own separate TRIAC-specific PR. The stable
Bathroom PoE build (Ceiling-POE-VentIQ-RoomIQ) is unchanged.

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
        cls.ledger = {
            r["config_string"]: r for r in _load(LEDGER_PATH)["rows"]
        }

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

    def test_catalog_status_and_build_matrix_unchanged(self) -> None:
        catalog = _catalog_by_cs()
        for cs in FAN_CONFIGS:
            with self.subTest(config_string=cs):
                entry = catalog[cs]
                self.assertEqual(
                    entry["status"],
                    "hardware-pending",
                    f"{cs!r}: lifecycle status stays hardware-pending "
                    "(preview import eligibility is not a lifecycle promotion)",
                )
                self.assertIs(
                    entry["webflash_build_matrix"],
                    False,
                    f"{cs!r}: webflash_build_matrix stays false — eligibility is "
                    "not a committed build row",
                )


class NoCommittedWebflashRowTests(unittest.TestCase):
    """No fan row enters config/webflash-builds.json; the import is queued only."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.builds = {b["config_string"] for b in _load(BUILDS_PATH)["builds"]}
        cls.ledger = {r["config_string"]: r for r in _load(LEDGER_PATH)["rows"]}
        cls.manual = {c["id"]: c for c in _load(MANUAL_PATH)["candidates"]}

    def test_fans_absent_from_committed_webflash_builds(self) -> None:
        for cs in FAN_CONFIGS:
            with self.subTest(config_string=cs):
                self.assertNotIn(cs, self.builds)

    def test_no_fan_token_in_webflash_builds(self) -> None:
        raw = BUILDS_PATH.read_text(encoding="utf-8")
        for token in ("FanRelay", "FanPWM", "FanDAC", "FanTRIAC"):
            with self.subTest(token=token):
                self.assertNotIn(token, raw)

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
        self.assertEqual(self.totals["webflash_import_eligible_now"], 8)
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
        t = self.by_cs[TRIAC_CONFIG]
        self.assertEqual(t["delivery_lane"], "advanced-manual-preview")
        self.assertIn("HW-005", str(t.get("build_blocker")))

    def test_triac_absent_from_webflash_builds(self) -> None:
        builds = {b["config_string"] for b in _load(BUILDS_PATH)["builds"]}
        self.assertNotIn(TRIAC_CONFIG, builds)


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

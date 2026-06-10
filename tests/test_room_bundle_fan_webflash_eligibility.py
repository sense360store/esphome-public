#!/usr/bin/env python3
"""Regression guard for ROOM-BUNDLE-FAN-WEBFLASH-ELIGIBILITY-001.

The five published full-composition Bathroom / Kitchen fan-control PREVIEW
bundle artifacts from ROOM-BUNDLE-FAN-PUBLISH-RESULTS-001 (#719) are now
preview WebFlash-import ELIGIBLE (Advanced-install-only, acknowledgement-gated):

    Ceiling-POE-VentIQ-FanPWM-RoomIQ
    Ceiling-POE-VentIQ-FanDAC-RoomIQ
    Ceiling-POE-AirIQ-FanRelay-RoomIQ
    Ceiling-POE-AirIQ-FanDAC-RoomIQ
    Ceiling-POE-AirIQ-FanPWM-RoomIQ

This is the room-bundle sibling of RELEASE-PREVIEW-FAN-WEBFLASH-ELIGIBILITY-001
(#711, which marked the single-driver FanRelay / FanPWM / FanDAC standalone
previews eligible). Like that decision, the flip is import-eligibility ONLY. It
is deliberately NOT:

  * a stable / full / production release (those blockers remain),
  * a recommended / default / customer-kit selection,
  * a buyable / shop-visible product,
  * a committed config/webflash-builds.json build row (the fan-token guardrail
    and catalog webflash_build_matrix=false stand; the one-click import is the
    separately queued downstream WF-IMPORT-FAN-BUNDLES-001),
  * a Simple / easy-mode exposure (webflash_easy_mode_eligible stays false until
    the downstream WebFlash import + warning gates land).

FanTRIAC stays excluded (not import eligible, no artifact; HW-005 buildability
resolved by TRIAC-PINMAP-CORRECT-001 but advanced-manual-preview publish gated
by PACKAGE-TRIAC-001 + the COMPLIANCE-001 gate element — per
COMPLIANCE-001-RESOLUTION-001 that element now resolves to the
experimental-lane preconditions, with the gated_by tokens and the enforced
behaviour unchanged — never by an acknowledgement gate).
The two FanDAC artifacts keep the GP8403 IC1 0x58 / IC2 0x5A address policy
(0x59 forbidden) and the pending FANDAC-I2C-ADDR-001 bench verification — no
FanDAC hardware proof is claimed. The stable Bathroom PoE build
(Ceiling-POE-VentIQ-RoomIQ) and Simple install are unchanged.

Metadata-only guards: they assert nothing about firmware behaviour and claim no
hardware / bench / compliance / safety / commercial-availability proof. Run::

    python3 tests/test_room_bundle_fan_webflash_eligibility.py
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from typing import Any, Dict

REPO_ROOT = Path(__file__).resolve().parent.parent
VARIANTS_PATH = REPO_ROOT / "config" / "room-bundle-fan-variants.json"
CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
SHOP_PATH = REPO_ROOT / "config" / "shop-commercial-source-of-truth.json"

DECISION_ID = "ROOM-BUNDLE-FAN-WEBFLASH-ELIGIBILITY-001"
RELEASE_TAG = "v1.0.0-preview"
DOWNSTREAM_IMPORT = "WF-IMPORT-FAN-BUNDLES-001"

# The five published full-composition room-bundle fan configs, with the durable
# release-asset SHA256 + size recorded by ROOM-BUNDLE-FAN-PUBLISH-RESULTS-001.
EXPECTED: Dict[str, Dict[str, Any]] = {
    "Ceiling-POE-VentIQ-FanPWM-RoomIQ": {
        "asset": "Sense360-Ceiling-POE-VentIQ-FanPWM-RoomIQ-v1.0.0-preview.bin",
        "sha256": "6d988708558881d653ffbc7429ef8779a574878ac0ee26d745bf645be85befba",
        "size": 1010192,
    },
    "Ceiling-POE-VentIQ-FanDAC-RoomIQ": {
        "asset": "Sense360-Ceiling-POE-VentIQ-FanDAC-RoomIQ-v1.0.0-preview.bin",
        "sha256": "a08c82f735aa058614afda71dbec2d220d23a0a4fbb4cb46088adb82a41d8ef8",
        "size": 990112,
    },
    "Ceiling-POE-AirIQ-FanRelay-RoomIQ": {
        "asset": "Sense360-Ceiling-POE-AirIQ-FanRelay-RoomIQ-v1.0.0-preview.bin",
        "sha256": "97e54930f26074e38326fbeaff7a222c828df38a33be509327e77a0b0f24a83f",
        "size": 1090656,
    },
    "Ceiling-POE-AirIQ-FanDAC-RoomIQ": {
        "asset": "Sense360-Ceiling-POE-AirIQ-FanDAC-RoomIQ-v1.0.0-preview.bin",
        "sha256": "903a37dc2faf3e1f87016c435e6076752b8c776e7a862f8986d5b5a4b19a994b",
        "size": 1090400,
    },
    "Ceiling-POE-AirIQ-FanPWM-RoomIQ": {
        "asset": "Sense360-Ceiling-POE-AirIQ-FanPWM-RoomIQ-v1.0.0-preview.bin",
        "sha256": "0ca10a2f3e867ae5693e36149276b0176294b2391fa9ef02ba7059d9c853a1cc",
        "size": 1113872,
    },
}
FIVE = tuple(EXPECTED)
FANDAC_CONFIGS = (
    "Ceiling-POE-VentIQ-FanDAC-RoomIQ",
    "Ceiling-POE-AirIQ-FanDAC-RoomIQ",
)
TRIAC_CONFIG = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"
STABLE_CONFIG = "Ceiling-POE-VentIQ-RoomIQ"
LAUNCH_SKU = "S360-KIT-BATH-P"
FAN_FAMILY_TOKENS = ("FanRelay", "FanPWM", "FanDAC", "FanTRIAC")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _load(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _variants_by_config() -> Dict[str, Dict[str, Any]]:
    return {
        v["intended_firmware_config_string"]: v
        for v in _load(VARIANTS_PATH)["fan_variant_candidates"]
    }


def _catalog_by_config() -> Dict[str, Dict[str, Any]]:
    return {
        e["config_string"]: e
        for e in _load(CATALOG_PATH)["products"]
        if e.get("config_string")
    }


class FiveAreWebflashImportEligibleTests(unittest.TestCase):
    """All five published room-bundle fan previews are WebFlash-import eligible."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.variants = _variants_by_config()
        cls.catalog = _catalog_by_config()

    def test_each_variant_is_import_eligible(self) -> None:
        for cs in FIVE:
            with self.subTest(config_string=cs):
                elig = self.variants[cs].get("webflash_import_eligibility")
                self.assertIsInstance(elig, dict, f"{cs}: missing eligibility block")
                self.assertIs(elig["eligible"], True)
                self.assertEqual(elig["exposure_class"], "acknowledgement-gated")
                self.assertEqual(elig["channel"], "preview")
                self.assertEqual(elig["delivery_lane"], "manual-preview")
                self.assertEqual(elig["authorised_by"], DECISION_ID)
                self.assertEqual(elig["proof_scope"], "firmware-build-release-only")
                self.assertEqual(
                    elig["downstream_import_followup"], DOWNSTREAM_IMPORT
                )

    def test_eligibility_records_release_asset_sha256_and_size(self) -> None:
        for cs, want in EXPECTED.items():
            with self.subTest(config_string=cs):
                elig = self.variants[cs]["webflash_import_eligibility"]
                self.assertEqual(elig["source_release_tag"], RELEASE_TAG)
                self.assertEqual(elig["release_asset_name"], want["asset"])
                self.assertEqual(elig["expected_sha256"], want["sha256"])
                self.assertEqual(elig["expected_size_bytes"], want["size"])
                self.assertRegex(elig["expected_sha256"], SHA256_RE)
                self.assertTrue(want["asset"].endswith("-preview.bin"))

    def test_eligibility_cross_locks_publish_evidence(self) -> None:
        # The eligibility SHA256 / size / asset must equal the recorded publish
        # proof so the two can never silently disagree.
        for cs in FIVE:
            with self.subTest(config_string=cs):
                elig = self.variants[cs]["webflash_import_eligibility"]
                ev = self.variants[cs]["firmware_config_evidence"]["publish_evidence"]
                self.assertEqual(elig["expected_sha256"], ev["asset_sha256"])
                self.assertEqual(elig["expected_size_bytes"], ev["asset_size_bytes"])
                self.assertEqual(
                    elig["release_asset_name"], ev["published_artifact_name"]
                )
                self.assertEqual(elig["source_release_tag"], ev["release_tag"])

    def test_eligibility_cross_locks_publish_results(self) -> None:
        results = {
            a["config_string"]: a
            for a in _load(VARIANTS_PATH)["publish_results"]["published_artifacts"]
        }
        for cs, want in EXPECTED.items():
            with self.subTest(config_string=cs):
                self.assertEqual(results[cs]["asset_sha256"], want["sha256"])
                self.assertEqual(results[cs]["asset_size_bytes"], want["size"])
                self.assertEqual(results[cs]["artifact_name"], want["asset"])

    def test_catalog_entries_carry_import_eligibility(self) -> None:
        # The product catalog is the downstream contract surface that WebFlash
        # reads (is_explicit_preview_import_eligible). It must agree.
        for cs, want in EXPECTED.items():
            with self.subTest(config_string=cs):
                block = self.catalog[cs].get("webflash_import_eligibility")
                self.assertIsInstance(block, dict, f"{cs}: catalog block missing")
                self.assertIs(block["eligible"], True)
                self.assertEqual(block["exposure_class"], "acknowledgement-gated")
                self.assertEqual(block["upstream_decision"], DECISION_ID)
                self.assertEqual(block["expected_sha256"], want["sha256"])
                self.assertEqual(block["release_asset_name"], want["asset"])

    def test_totals_and_decision_block(self) -> None:
        doc = _load(VARIANTS_PATH)
        self.assertEqual(doc["totals"]["webflash_import_eligible_now"], 5)
        eligible = [
            v["intended_firmware_config_string"]
            for v in doc["fan_variant_candidates"]
            if (v.get("webflash_import_eligibility") or {}).get("eligible") is True
        ]
        self.assertEqual(sorted(eligible), sorted(FIVE))
        self.assertEqual(doc["marked_webflash_import_eligible_by"], DECISION_ID)
        decision = doc["webflash_import_eligibility_decision"]
        self.assertEqual(decision["id"], DECISION_ID)
        self.assertEqual(sorted(decision["targets"]), sorted(FIVE))
        g = decision["guarantees"]
        for flag in (
            "nothing_becomes_stable",
            "nothing_becomes_recommended_or_default",
            "nothing_becomes_buyable",
            "no_fan_row_added_to_webflash_builds",
            "catalog_status_stays_hardware_pending",
            "catalog_webflash_build_matrix_stays_false",
            "stable_full_release_blockers_remain",
            "simple_easy_mode_requires_downstream_webflash_import",
            "fandac_bench_verification_stays_pending",
            "triac_stays_excluded_and_separate",
            "publishes_no_firmware",
            "touches_no_webflash_repo",
        ):
            with self.subTest(flag=flag):
                self.assertIs(g[flag], True)


class FivePreviewOnlyPostureTests(unittest.TestCase):
    """Eligibility does not weaken the preview-only posture."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.variants = _variants_by_config()
        cls.catalog = _catalog_by_config()

    def test_five_stay_compile_validated_preview(self) -> None:
        for cs in FIVE:
            v = self.variants[cs]
            with self.subTest(config_string=cs):
                self.assertEqual(
                    v["firmware_config_status"],
                    "buildable-preview-compile-validated",
                )
                self.assertEqual(v["preview_status"], "preview-compile-validated")
                self.assertFalse(v["webflash_exposed"])
                # Import-eligible, but easy/simple-mode stays gated until the
                # downstream WebFlash import lands.
                self.assertFalse(v["webflash_easy_mode_eligible"])
                self.assertIs(
                    v["webflash_import_eligibility"][
                        "simple_easy_mode_requires_downstream_webflash_import_and_warning_gates"
                    ],
                    True,
                )

    def test_five_not_stable_recommended_default_or_buyable(self) -> None:
        for cs in FIVE:
            v = self.variants[cs]
            with self.subTest(config_string=cs):
                self.assertEqual(v["stable_status"], "blocked")
                self.assertTrue(v["stable_blockers"])
                self.assertFalse(v["recommended"])
                self.assertFalse(v["customer_default"])
                self.assertFalse(v["buyable"])
                self.assertEqual(v["commercial_availability"], "waitlist-only")
                self.assertFalse(v["bench_evidence_claimed"])
                self.assertFalse(v["compliance_claimed"])
                self.assertIs(
                    v["webflash_import_eligibility"][
                        "stable_full_release_blockers_remain"
                    ],
                    True,
                )

    def test_catalog_status_and_build_matrix_unchanged(self) -> None:
        for cs in FIVE:
            entry = self.catalog[cs]
            with self.subTest(config_string=cs):
                self.assertEqual(entry["status"], "hardware-pending")
                self.assertIs(entry["webflash_build_matrix"], False)

    def test_no_committed_webflash_build_row(self) -> None:
        builds = {b["config_string"] for b in _load(BUILDS_PATH)["builds"]}
        for cs in FIVE:
            with self.subTest(config_string=cs):
                self.assertNotIn(cs, builds)
                self.assertIs(
                    self.variants[cs]["webflash_import_eligibility"][
                        "webflash_build_row_added"
                    ],
                    False,
                )


class FanDacPendingTests(unittest.TestCase):
    """The two FanDAC previews keep the 0x5A policy and pending bench gate."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.variants = _variants_by_config()

    def test_fandac_eligibility_records_address_policy_and_pending(self) -> None:
        for cs in FANDAC_CONFIGS:
            req = self.variants[cs]["webflash_import_eligibility"][
                "fandac_address_requirement"
            ]
            with self.subTest(config_string=cs):
                self.assertEqual(req["gp8403_ic1"], "0x58")
                self.assertEqual(req["gp8403_ic2"], "0x5A")
                self.assertEqual(req["forbidden_gp8403_address"], "0x59")
                self.assertEqual(req["sgp41"], "0x59")
                self.assertEqual(
                    req["bench_verification_followup"], "FANDAC-I2C-ADDR-001"
                )
                self.assertEqual(req["bench_verification_status"], "pending")

    def test_non_fandac_eligibility_has_no_address_requirement(self) -> None:
        for cs in FIVE:
            if cs in FANDAC_CONFIGS:
                continue
            with self.subTest(config_string=cs):
                self.assertNotIn(
                    "fandac_address_requirement",
                    self.variants[cs]["webflash_import_eligibility"],
                )

    def test_document_policy_bench_status_still_pending(self) -> None:
        doc = _load(VARIANTS_PATH)
        self.assertEqual(
            doc["fan_dac_i2c_address_policy"]["bench_verification_status"], "pending"
        )
        self.assertEqual(
            doc["webflash_import_eligibility_decision"][
                "fandac_bench_verification_status"
            ],
            "pending",
        )


class TriacStaysExcludedTests(unittest.TestCase):
    """FanTRIAC stays excluded / build-blocked and is NOT import eligible."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.variants = _variants_by_config()
        cls.catalog = _catalog_by_config()

    def test_triac_is_not_import_eligible(self) -> None:
        triac = self.variants[TRIAC_CONFIG]
        # No eligible:true block (absent or explicitly not-eligible both pass).
        self.assertIsNot(
            (triac.get("webflash_import_eligibility") or {}).get("eligible"),
            True,
        )
        self.assertNotIn(TRIAC_CONFIG, EXPECTED)

    def test_triac_stays_publish_blocked(self) -> None:
        triac = self.variants[TRIAC_CONFIG]
        self.assertEqual(triac["firmware_config_status"], "defined-build-blocked")
        ev = triac["firmware_config_evidence"]
        # HW-005 buildability is RESOLVED (TRIAC-PINMAP-CORRECT-001): buildable
        # now, no build_blocker. The history field still names HW-005.
        self.assertTrue(ev["buildable_now"])
        self.assertIsNone(ev["build_blocker"])
        self.assertIn("HW-005", ev["build_blocker_history"])
        self.assertNotIn("publish_evidence", ev)
        # The remaining blocker is the advanced-manual-preview PUBLISH gate
        # (PACKAGE-TRIAC-001 + the COMPLIANCE-001 gate element, which per
        # COMPLIANCE-001-RESOLUTION-001 resolves to the experimental-lane
        # preconditions; tokens unchanged until the commissioning PR), never
        # an acknowledgement gate.
        gate = triac["advanced_preview_publish_gate"]
        self.assertEqual(gate["id"], "TRIAC-PUBLISH-ADVANCED-PREVIEW-001")
        self.assertEqual(
            set(gate["gated_by"]), {"PACKAGE-TRIAC-001", "COMPLIANCE-001"}
        )
        self.assertFalse(gate["is_acknowledgement_gate"])
        self.assertFalse(gate["artifact_cut"])
        self.assertFalse(gate["preview_or_advanced_preview_row_added"])

    def test_triac_absent_from_catalog_eligibility(self) -> None:
        entry = self.catalog.get(TRIAC_CONFIG)
        if entry is not None:
            self.assertIsNot(
                (entry.get("webflash_import_eligibility") or {}).get("eligible"),
                True,
            )


class WebflashRepoUntouchedTests(unittest.TestCase):
    """No committed WebFlash build row / .bin / manifest; fan-token guardrail."""

    def test_five_and_triac_absent_from_webflash_builds(self) -> None:
        builds = {b["config_string"] for b in _load(BUILDS_PATH)["builds"]}
        for cs in FIVE + (TRIAC_CONFIG,):
            with self.subTest(config_string=cs):
                self.assertNotIn(cs, builds)

    def test_no_fan_token_in_webflash_builds(self) -> None:
        raw = BUILDS_PATH.read_text(encoding="utf-8")
        for token in FAN_FAMILY_TOKENS:
            with self.subTest(token=token):
                self.assertNotIn(token, raw)

    def test_no_manifest_sources_or_bin_committed(self) -> None:
        self.assertFalse((REPO_ROOT / "manifest.json").exists())
        self.assertFalse((REPO_ROOT / "firmware" / "sources.json").exists())
        bins = [p for p in REPO_ROOT.rglob("*.bin") if ".git" not in p.parts]
        self.assertEqual(bins, [], f"no .bin may be committed; found {bins}")


class StableBathroomPoeUnchangedTests(unittest.TestCase):
    """The stable Bathroom PoE baseline is unchanged by this PR."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = _catalog_by_config()

    def test_stable_baseline_catalog_is_production(self) -> None:
        self.assertEqual(self.catalog[STABLE_CONFIG]["status"], "production")
        self.assertNotIn(
            "webflash_import_eligibility",
            self.catalog[STABLE_CONFIG],
            "the stable production baseline must not gain a preview-import block",
        )

    def test_stable_baseline_is_the_launch_product(self) -> None:
        shop = _load(SHOP_PATH)["launch_product"]
        self.assertEqual(shop["shop_sku"], LAUNCH_SKU)
        self.assertEqual(shop["firmware_config"], STABLE_CONFIG)

    def test_stable_baseline_is_a_committed_webflash_build(self) -> None:
        builds = {
            b["config_string"]: b for b in _load(BUILDS_PATH)["builds"]
        }
        self.assertIn(STABLE_CONFIG, builds)


if __name__ == "__main__":
    unittest.main(verbosity=2)

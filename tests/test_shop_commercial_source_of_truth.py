#!/usr/bin/env python3
"""Tests for the shop commercial source of truth (SHOP-COMMERCIAL-SOURCE-OF-TRUTH-001).

Covers the repo-level commercial launch source of truth at
``config/shop-commercial-source-of-truth.json`` (and its doc
``docs/shop-commercial-source-of-truth.md``) and pins the commercial naming /
shop-posture / claims invariants for the first shop launch:

  * the canonical launch SKU is ``S360-KIT-BATH-P`` and exists as a bundle in
    ``config/room-bundle-skus.json``;
  * the launch firmware config is ``Ceiling-POE-VentIQ-RoomIQ`` and the launch
    artifact equals the stable WebFlash build artifact in
    ``config/webflash-builds.json`` (and the production entry in
    ``config/product-catalog.json``);
  * the customer WebFlash URL is ``https://flash.sense360.com`` and the GitHub
    Pages URL is the technical fallback only;
  * candidate bundles are hidden from shop navigation and not buyable;
  * individual boards are not a public-sale launch product;
  * the forbidden-claims list includes mold prevention/detection, condensation
    prevention/elimination, safety certification, and base-kit fan-control
    claims;
  * TRIAC never appears as customer-facing / recommended / default.

These are commercial-policy / docs-config guards. They assert nothing about
firmware behaviour and they do not weaken any existing test: the canonical
room-bundle SKU, the hardware schematic statuses, the WebFlash build matrix,
and the product-catalog lifecycle are all read-only here.

Uses Python's stdlib unittest (no-pytest convention for this repo).
Run with::

    python3 tests/test_shop_commercial_source_of_truth.py

or::

    python3 -m unittest tests.test_shop_commercial_source_of_truth -v
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOT_PATH = REPO_ROOT / "config" / "shop-commercial-source-of-truth.json"
SOT_DOC_PATH = REPO_ROOT / "docs" / "shop-commercial-source-of-truth.md"
BUNDLE_PATH = REPO_ROOT / "config" / "room-bundle-skus.json"
WEBFLASH_BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
PRODUCT_CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"
HARDWARE_CATALOG_PATH = REPO_ROOT / "config" / "hardware-catalog.json"

LAUNCH_SKU = "S360-KIT-BATH-P"
LAUNCH_FIRMWARE_CONFIG = "Ceiling-POE-VentIQ-RoomIQ"
LAUNCH_BOARDS = ["S360-100", "S360-200", "S360-211", "S360-410"]
CUSTOMER_WEBFLASH_URL = "https://flash.sense360.com"
GITHUB_PAGES_URL = "https://sense360store.github.io/WebFlash/"
RESERVED_PORTAL_URL = "https://mysense360.com"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _launch_artifact() -> str:
    """The live stable artifact for the launch config, from the build ledger.

    Derived (not pinned) so release version bumps do not rot this test: the
    invariant is that the shop source of truth mirrors the stable WebFlash
    build for ``Ceiling-POE-VentIQ-RoomIQ``, whatever version that is today.
    """
    for entry in _load(WEBFLASH_BUILDS_PATH).get("builds", []) or []:
        if (
            entry.get("config_string") == LAUNCH_FIRMWARE_CONFIG
            and entry.get("channel") == "stable"
        ):
            return entry["artifact_name"]
    raise AssertionError(
        f"no stable build for {LAUNCH_FIRMWARE_CONFIG!r} in webflash-builds.json"
    )


LAUNCH_ARTIFACT = _launch_artifact()


class ShopSotShapeTests(unittest.TestCase):
    """Shape / schema invariants of the on-disk commercial source of truth."""

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(SOT_PATH)

    def test_file_exists(self):
        self.assertTrue(SOT_PATH.is_file(), f"missing: {SOT_PATH}")

    def test_schema_version_is_one(self):
        self.assertEqual(self.doc["schema_version"], 1)

    def test_canonical_id_present(self):
        self.assertEqual(
            self.doc["canonical_id"], "SHOP-COMMERCIAL-SOURCE-OF-TRUTH-001"
        )

    def test_top_level_sections_present(self):
        for key in (
            "launch_product",
            "aliases",
            "webflash",
            "candidate_bundle_visibility",
            "claims",
            "fan_control_copy",
            "guardrails",
        ):
            self.assertIn(key, self.doc, f"missing top-level section {key!r}")

    def test_sources_point_to_canonical_files(self):
        sources = self.doc.get("sources", {})
        self.assertEqual(
            sources.get("room_bundle_skus"), "config/room-bundle-skus.json"
        )
        self.assertEqual(sources.get("product_catalog"), "config/product-catalog.json")
        self.assertEqual(
            sources.get("hardware_catalog"), "config/hardware-catalog.json"
        )
        self.assertEqual(sources.get("webflash_builds"), "config/webflash-builds.json")

    def test_doc_pointer_resolves(self):
        self.assertEqual(self.doc.get("doc"), "docs/shop-commercial-source-of-truth.md")
        self.assertTrue(
            (REPO_ROOT / self.doc["doc"]).is_file(),
            "doc pointer must resolve to a real file",
        )


class LaunchProductTests(unittest.TestCase):
    """The single launch shop product invariants."""

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(SOT_PATH)
        cls.launch = cls.doc["launch_product"]

    def test_canonical_launch_sku_is_bath_p(self):
        self.assertEqual(
            self.launch["shop_sku"],
            LAUNCH_SKU,
            "canonical launch SKU must be S360-KIT-BATH-P",
        )

    def test_shop_title_is_bathroom_poe_bundle(self):
        self.assertEqual(self.launch["shop_title"], "Sense360 Bathroom Bundle — PoE")

    def test_launch_firmware_config_matches(self):
        self.assertEqual(self.launch["firmware_config"], LAUNCH_FIRMWARE_CONFIG)

    def test_launch_artifact_matches(self):
        self.assertEqual(self.launch["artifact_name"], LAUNCH_ARTIFACT)

    def test_launch_boards_match(self):
        self.assertEqual(
            sorted(self.launch["boards"]),
            sorted(LAUNCH_BOARDS),
            "launch bundle must ship Core + RoomIQ + VentIQ + PoE PSU",
        )

    def test_shop_posture_is_complete_room_bundle(self):
        self.assertEqual(self.launch["shop_posture"], "sellable-complete-room-bundle")

    def test_individual_boards_public_sale_is_false(self):
        self.assertIs(self.launch["individual_boards_public_sale"], False)

    def test_readiness_wording_allows_only_honest_phrasing(self):
        allowed = self.launch["readiness_wording"]["allowed"]
        self.assertIn("stable firmware available", allowed)
        self.assertIn("WebFlash install supported", allowed)
        self.assertIn("complete room kit", allowed)

    def test_readiness_wording_forbids_overclaims(self):
        not_allowed = " | ".join(
            self.launch["readiness_wording"]["not_allowed"]
        ).lower()
        for needle in (
            "hardware certified",
            "compliance certified",
            "verified poe hardware",
            "safety certified",
        ):
            self.assertIn(
                needle,
                not_allowed,
                f"readiness wording must forbid {needle!r}",
            )


class LaunchProductCrossReferenceTests(unittest.TestCase):
    """The launch product must agree with the canonical config files."""

    @classmethod
    def setUpClass(cls):
        cls.launch = _load(SOT_PATH)["launch_product"]
        cls.bundles = _load(BUNDLE_PATH)["bundles"]
        cls.by_sku = {b["bundle_sku"]: b for b in cls.bundles}
        cls.builds = _load(WEBFLASH_BUILDS_PATH)["builds"]
        cls.products = _load(PRODUCT_CATALOG_PATH)["products"]

    def test_launch_sku_exists_in_room_bundle_matrix(self):
        self.assertIn(
            LAUNCH_SKU,
            self.by_sku,
            "launch SKU must exist in config/room-bundle-skus.json",
        )

    def test_launch_sku_is_the_only_stable_release_bundle(self):
        stable = [
            b["bundle_sku"]
            for b in self.bundles
            if b["current_release_status"] == "stable-release"
        ]
        self.assertEqual(
            stable,
            [LAUNCH_SKU],
            "only the launch SKU may be stable-release in the bundle matrix",
        )

    def test_launch_bundle_firmware_and_boards_agree(self):
        bundle = self.by_sku[LAUNCH_SKU]
        self.assertEqual(
            bundle["likely_firmware_config_target"], LAUNCH_FIRMWARE_CONFIG
        )
        self.assertEqual(bundle["current_release_status"], "stable-release")
        self.assertEqual(
            sorted(bundle["included_board_skus"]),
            sorted(self.launch["boards"]),
            "launch boards must match the room-bundle matrix",
        )

    def test_launch_artifact_matches_stable_webflash_build(self):
        # STABLE-PROMOTION-RECONCILE-001: the ledger now carries three stable
        # rows (Release-One plus the promoted Bedroom v1.0.5 and Kitchen
        # v1.0.6 bundles). The LAUNCH product must still map to the
        # Release-One stable build, and remains the only stable row whose
        # commercial posture is release_one_required_config.
        stable = {
            b["config_string"]: b for b in self.builds if b.get("channel") == "stable"
        }
        self.assertIn(LAUNCH_FIRMWARE_CONFIG, stable)
        self.assertEqual(
            stable[LAUNCH_FIRMWARE_CONFIG]["artifact_name"],
            self.launch["artifact_name"],
            "launch artifact must equal the stable WebFlash build artifact",
        )
        for cs, b in stable.items():
            if cs == LAUNCH_FIRMWARE_CONFIG:
                continue
            posture = b.get("commercial_posture") or {}
            self.assertFalse(
                posture.get("release_one_required_config"),
                f"{cs}: a promoted stable row must never claim "
                "release_one_required_config",
            )
            self.assertFalse(
                posture.get("customer_default"),
                f"{cs}: a promoted stable row must never claim customer_default",
            )

    def test_launch_config_is_production_in_product_catalog(self):
        production = [
            p for p in self.products if p.get("config_string") == LAUNCH_FIRMWARE_CONFIG
        ]
        self.assertEqual(
            len(production), 1, "launch config must have one product-catalog row"
        )
        self.assertEqual(production[0]["status"], "production")
        self.assertEqual(production[0]["artifact_name"], LAUNCH_ARTIFACT)


class WebflashUrlTests(unittest.TestCase):
    """Customer flashing URL vs technical fallback vs reserved portal."""

    @classmethod
    def setUpClass(cls):
        cls.webflash = _load(SOT_PATH)["webflash"]

    def test_customer_url_is_flash_sense360_com(self):
        self.assertEqual(
            self.webflash["customer_url"],
            CUSTOMER_WEBFLASH_URL,
            "customer WebFlash URL must be https://flash.sense360.com",
        )

    def test_github_pages_is_fallback_only(self):
        self.assertEqual(
            self.webflash["technical_fallback_url"],
            GITHUB_PAGES_URL,
            "GitHub Pages URL must be the technical fallback / deployment origin",
        )
        # GitHub Pages must NOT be promoted to the customer-facing URL.
        self.assertNotEqual(
            self.webflash["customer_url"],
            GITHUB_PAGES_URL,
            "GitHub Pages must not be the customer-facing flashing URL",
        )

    def test_mysense360_reserved_for_portal_not_flashing(self):
        self.assertEqual(self.webflash["reserved_portal_url"], RESERVED_PORTAL_URL)
        self.assertNotEqual(
            self.webflash["customer_url"],
            RESERVED_PORTAL_URL,
            "mysense360.com is reserved for a future portal, not the flashing URL",
        )


class CandidateBundleVisibilityTests(unittest.TestCase):
    """Candidate bundles are hidden and not buyable."""

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(SOT_PATH)
        cls.visibility = cls.doc["candidate_bundle_visibility"]
        cls.bundles = _load(BUNDLE_PATH)["bundles"]

    def test_default_is_hidden_from_shop_navigation(self):
        self.assertEqual(self.visibility["default"], "hidden-from-shop-navigation")

    def test_buy_button_not_allowed(self):
        self.assertIs(
            self.visibility["buy_button_allowed"],
            False,
            "candidate bundles must not be marked sellable / buyable",
        )

    def test_candidate_bundles_are_every_non_launch_bundle(self):
        all_skus = {b["bundle_sku"] for b in self.bundles}
        expected = sorted(all_skus - {LAUNCH_SKU})
        self.assertEqual(
            sorted(self.visibility["candidate_bundles"]),
            expected,
            "candidate-bundle list must be every room bundle except the launch SKU",
        )

    def test_no_candidate_bundle_is_stable_release(self):
        by_sku = {b["bundle_sku"]: b for b in self.bundles}
        for sku in self.visibility["candidate_bundles"]:
            self.assertNotEqual(
                by_sku[sku]["current_release_status"],
                "stable-release",
                f"candidate bundle {sku!r} must not be stable-release / sellable",
            )

    def test_waitlist_labels_are_explicit(self):
        labels = " | ".join(self.visibility["required_labels_if_shown"]).lower()
        self.assertIn("coming soon", labels)
        self.assertIn("not available to buy", labels)


class ClaimsTests(unittest.TestCase):
    """Approved vs forbidden ecommerce claims."""

    @classmethod
    def setUpClass(cls):
        cls.claims = _load(SOT_PATH)["claims"]
        cls.allowed = cls.claims["allowed"]
        cls.not_allowed = cls.claims["not_allowed"]
        cls.allowed_low = [c.lower() for c in cls.allowed]
        cls.not_allowed_low = [c.lower() for c in cls.not_allowed]

    def test_allowed_claims_present(self):
        for needle in (
            "monitors bathroom environment",
            "designed for home assistant / esphome users",
            "supports browser-based firmware installation with webflash",
            "poe-powered room sensing kit",
        ):
            self.assertTrue(
                any(needle == c for c in self.allowed_low),
                f"approved claim missing: {needle!r}",
            )

    def test_forbidden_claims_include_mold(self):
        self.assertIn("prevents mold", self.not_allowed_low)
        self.assertIn("detects mold", self.not_allowed_low)

    def test_forbidden_claims_include_condensation(self):
        self.assertIn("eliminates condensation", self.not_allowed_low)
        self.assertIn("prevents condensation", self.not_allowed_low)

    def test_forbidden_claims_include_safety_certification(self):
        self.assertIn("safety certified", self.not_allowed_low)

    def test_forbidden_claims_include_base_kit_fan_control(self):
        self.assertIn("controls extractor fans", self.not_allowed_low)
        self.assertIn("mains fan control", self.not_allowed_low)
        self.assertIn("triac fan control", self.not_allowed_low)

    def test_mold_and_condensation_never_appear_in_allowed_claims(self):
        joined = " ".join(self.allowed_low)
        for forbidden in ("mold", "condensation", "certified", "medical"):
            self.assertNotIn(
                forbidden,
                joined,
                f"forbidden term {forbidden!r} must not appear in approved claims",
            )

    def test_no_claim_overlap_between_allowed_and_not_allowed(self):
        overlap = set(self.allowed_low) & set(self.not_allowed_low)
        self.assertEqual(
            overlap, set(), f"claim listed as both allowed and not: {overlap}"
        )


class FanAndTriacGuardrailTests(unittest.TestCase):
    """Fan-control copy and TRIAC posture guardrails."""

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(SOT_PATH)
        cls.fan = cls.doc["fan_control_copy"]
        cls.guardrails = cls.doc["guardrails"]

    def test_base_kit_has_no_fan_control(self):
        self.assertIs(self.fan["base_kit_includes_fan_control"], False)

    def test_triac_not_customer_facing_recommended_or_default(self):
        self.assertIs(self.fan["triac_customer_facing"], False)
        self.assertIs(self.fan["triac_recommended_or_default"], False)
        self.assertEqual(self.fan["triac_blocker"], "HW-005")

    def test_triac_token_absent_from_allowed_claims(self):
        allowed = " ".join(c.lower() for c in self.doc["claims"]["allowed"])
        self.assertNotIn("triac", allowed)

    def test_fan_framing_is_only_future_preview_installer_manual(self):
        self.assertEqual(
            sorted(self.fan["allowed_framing"]),
            sorted(["future", "preview", "installer", "manual-candidate"]),
        )


class HardGuardrailTests(unittest.TestCase):
    """Hard guardrails that must never silently flip."""

    @classmethod
    def setUpClass(cls):
        cls.guardrails = _load(SOT_PATH)["guardrails"]
        cls.hw_items = _load(HARDWARE_CATALOG_PATH)["items"]

    def test_canonical_sku_unchanged(self):
        self.assertEqual(self.guardrails["canonical_room_bundle_sku"], LAUNCH_SKU)
        self.assertIs(self.guardrails["canonical_room_bundle_sku_unchanged"], True)

    def test_s360_410_not_claimed_verified(self):
        self.assertIs(self.guardrails["s360_410_schematic_verified"], False)
        # Consistency with the hardware catalog: S360-410 really is unverified.
        s410 = next(i for i in self.hw_items if i.get("sku") == "S360-410")
        self.assertEqual(s410["schematic_status"], "cataloged_unverified")

    def test_no_hardware_compliance_certification(self):
        self.assertIs(self.guardrails["hardware_compliance_certified"], False)

    def test_candidate_bundles_not_buyable_and_no_board_primary_sale(self):
        self.assertIs(self.guardrails["candidate_bundles_buyable"], False)
        self.assertIs(
            self.guardrails["individual_boards_primary_launch_product"], False
        )

    def test_no_firmware_publish_or_webflash_touch(self):
        self.assertIs(self.guardrails["publishes_firmware"], False)
        self.assertIs(self.guardrails["touches_webflash_repo"], False)


class ShopSotDocTests(unittest.TestCase):
    """The companion doc exists and stays aligned with the config."""

    @classmethod
    def setUpClass(cls):
        cls.text = SOT_DOC_PATH.read_text(encoding="utf-8")

    def test_doc_exists(self):
        self.assertTrue(SOT_DOC_PATH.is_file(), f"missing: {SOT_DOC_PATH}")

    def test_doc_names_canonical_id(self):
        self.assertIn("SHOP-COMMERCIAL-SOURCE-OF-TRUTH-001", self.text)

    def test_doc_names_launch_sku_and_url(self):
        self.assertIn(LAUNCH_SKU, self.text)
        self.assertIn(CUSTOMER_WEBFLASH_URL, self.text)

    def test_doc_points_at_machine_readable_config(self):
        self.assertIn("config/shop-commercial-source-of-truth.json", self.text)

    def test_doc_is_policy_only(self):
        low = self.text.lower()
        self.assertIn("does not", low)
        # Must not claim S360-410 verification.
        self.assertIn("cataloged_unverified", low)


if __name__ == "__main__":
    unittest.main(verbosity=2)

#!/usr/bin/env python3
"""Tests for the release-channel policy (RELEASE-PREVIEW-ALL-PRODUCTS-001).

These guard the explicit channel-tier policy that opens *preview* eligibility
to every buildable Sense360 firmware target while keeping *stable* promotion
evidence-gated.

The policy under test is config/release-channel-policy.json (the canonical
narrative doc docs/release-channel-policy.md was archived under
DOCS-DISPOSITION-001; see docs/archive-index.md). These are
policy/eligibility guards: they assert nothing about firmware behaviour and
publish no artifacts.

Invariants asserted (matching the task contract):
  - preview is allowed without hardware proof
  - stable still requires evidence / hardware proof
  - TRIAC cannot be stable / recommended / customer default
  - TRIAC preview requires the advanced (mains-risk) warning
  - fan previews are not stable
  - preview targets require release-note warning text
  - the WebFlash build matrix may include preview targets without stable promotion
  - no fake hardware evidence is claimed
"""

import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
POLICY_PATH = REPO_ROOT / "config" / "release-channel-policy.json"
ARCHIVE_INDEX = REPO_ROOT / "docs" / "archive-index.md"
WEBFLASH_COMPAT = REPO_ROOT / "config" / "webflash-compatibility.json"


def _load(path: Path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


class PolicyStructureTests(unittest.TestCase):
    """The policy file exists and has the expected shape."""

    @classmethod
    def setUpClass(cls):
        cls.policy = _load(POLICY_PATH)

    def test_policy_file_exists_and_is_identified(self):
        self.assertEqual(self.policy["policy_id"], "RELEASE-PREVIEW-ALL-PRODUCTS-001")
        self.assertEqual(self.policy["schema_version"], 1)

    def test_canonical_doc_recorded_in_archive_index(self):
        # The canonical narrative doc was archived under
        # DOCS-DISPOSITION-001; the policy JSON's canonical_doc path must
        # keep being recorded in docs/archive-index.md, from whose SHA the
        # content stays recoverable.
        self.assertIn(
            self.policy.get("canonical_doc", "docs/release-channel-policy.md"),
            ARCHIVE_INDEX.read_text(encoding="utf-8"),
            "the archived canonical policy doc must be recorded in "
            "docs/archive-index.md",
        )

    def test_three_channel_tiers_defined(self):
        self.assertEqual(
            set(self.policy["channel_tiers"]),
            {"stable", "preview", "advanced-preview"},
        )

    def test_each_tier_has_required_fields(self):
        required = {
            "hardware_proof_required",
            "evidence_gated",
            "recommended",
            "customer_default_allowed",
            "may_be_required_config",
            "webflash_exposure_class",
            "build_channel",
            "warning_required",
            "may_claim_bench_evidence",
            "requires_schematic_status_verified",
            "requires_lifecycle_production",
        }
        for name, tier in self.policy["channel_tiers"].items():
            self.assertTrue(
                required.issubset(tier),
                f"tier {name} missing fields: {required - set(tier)}",
            )

    def test_matrix_rows_have_required_columns(self):
        required = {
            "product",
            "config_string",
            "yaml_path",
            "intended_channel",
            "expected_artifact_name",
            "webflash_exposure_class",
            "warning_copy_required",
            "stable_blocker",
        }
        for row in self.policy["preview_release_matrix"]:
            self.assertTrue(
                required.issubset(row),
                f"{row.get('config_string')} missing columns: {required - set(row)}",
            )

    def test_matrix_intended_channels_are_known(self):
        known = set(self.policy["channel_tiers"])
        for row in self.policy["preview_release_matrix"]:
            self.assertIn(row["intended_channel"], known)

    def test_referenced_yaml_paths_exist(self):
        for row in self.policy["preview_release_matrix"]:
            yaml_path = REPO_ROOT / row["yaml_path"]
            self.assertTrue(
                yaml_path.is_file(),
                f"{row['config_string']} -> missing YAML {row['yaml_path']}",
            )

    def test_artifact_names_follow_pattern_with_valid_build_channel(self):
        # Artifact suffix must be a build channel that WebFlash actually allows.
        compat = _load(WEBFLASH_COMPAT)
        allowed = set(compat["allowed_channels"])
        mapping = self.policy["build_channel_mapping"]
        pattern = re.compile(r"^Sense360-(.+)-v(\d+\.\d+\.\d+)-([a-z]+)\.bin$")
        for row in self.policy["preview_release_matrix"]:
            match = pattern.match(row["expected_artifact_name"])
            self.assertIsNotNone(
                match, f"bad artifact name: {row['expected_artifact_name']}"
            )
            config, _version, suffix = match.groups()
            self.assertEqual(config, row["config_string"])
            self.assertIn(suffix, allowed)
            self.assertEqual(suffix, mapping[row["intended_channel"]])


class PreviewWithoutHardwareProofTests(unittest.TestCase):
    """Preview is allowed without hardware proof; stable still requires it."""

    @classmethod
    def setUpClass(cls):
        cls.policy = _load(POLICY_PATH)
        cls.tiers = cls.policy["channel_tiers"]

    def test_preview_allowed_without_hardware_proof(self):
        self.assertFalse(self.tiers["preview"]["hardware_proof_required"])
        self.assertFalse(self.tiers["preview"]["evidence_gated"])
        self.assertFalse(self.tiers["advanced-preview"]["hardware_proof_required"])

    def test_stable_still_requires_evidence(self):
        self.assertTrue(self.tiers["stable"]["hardware_proof_required"])
        self.assertTrue(self.tiers["stable"]["evidence_gated"])
        self.assertTrue(self.tiers["stable"]["requires_schematic_status_verified"])
        self.assertTrue(self.tiers["stable"]["requires_lifecycle_production"])

    def test_guardrail_flags_declare_the_split(self):
        g = self.policy["guardrails"]
        self.assertTrue(g["lack_of_hardware_proof_blocks_stable_only"])
        self.assertTrue(g["lack_of_hardware_proof_does_not_block_preview"])

    def test_preview_rows_do_not_require_a_resolved_stable_blocker(self):
        # Every non-stable row may still carry a stable_blocker, but its presence
        # must NOT prevent the row from being preview-eligible.
        for row in self.policy["preview_release_matrix"]:
            if row["intended_channel"] == "stable":
                continue
            # Preview-eligible rows are recorded regardless of an open blocker.
            self.assertIn(
                row["publication_status"],
                {
                    "published-preview",
                    "eligible-unpublished",
                    "eligible-needs-product-yaml",
                },
            )


class TriacTests(unittest.TestCase):
    """TRIAC may be advanced-preview only — never stable/recommended/default."""

    @classmethod
    def setUpClass(cls):
        cls.policy = _load(POLICY_PATH)
        cls.triac_rows = [
            r for r in cls.policy["preview_release_matrix"] if r.get("is_triac")
        ]

    def test_triac_row_exists(self):
        self.assertTrue(self.triac_rows, "expected at least one TRIAC matrix row")

    def test_triac_ceiling_is_advanced_preview(self):
        self.assertEqual(
            self.policy["module_channel_ceiling"]["FanTRIAC"], "advanced-preview"
        )

    def test_triac_cannot_be_stable(self):
        for row in self.triac_rows:
            self.assertNotEqual(row["intended_channel"], "stable")
            self.assertEqual(row["intended_channel"], "advanced-preview")

    def test_triac_is_not_recommended_or_default(self):
        adv = self.policy["channel_tiers"]["advanced-preview"]
        self.assertFalse(adv["recommended"])
        self.assertFalse(adv["customer_default_allowed"])
        self.assertFalse(adv["may_be_required_config"])
        g = self.policy["guardrails"]
        self.assertTrue(g["triac_must_not_be_stable"])
        self.assertTrue(g["triac_must_not_be_recommended"])
        self.assertTrue(g["triac_must_not_be_customer_default"])

    def test_triac_preview_requires_advanced_warning(self):
        for row in self.triac_rows:
            self.assertTrue(row["warning_copy_required"])
            self.assertEqual(
                row["webflash_exposure_class"], "acknowledgement-gated-advanced"
            )
        adv_copy = self.policy["warning_copy"]["advanced-preview"]
        self.assertIn("MAINS", adv_copy.upper())
        self.assertTrue(self.policy["guardrails"]["triac_preview_requires_advanced_warning"])


class FanPreviewTests(unittest.TestCase):
    """Fan previews are buildable previews but never stable."""

    @classmethod
    def setUpClass(cls):
        cls.policy = _load(POLICY_PATH)
        cls.fan_rows = [
            r for r in cls.policy["preview_release_matrix"] if r.get("is_fan")
        ]

    def test_fan_families_present(self):
        families = {r["family"] for r in self.fan_rows}
        self.assertTrue({"FanRelay", "FanPWM", "FanDAC", "FanTRIAC"}.issubset(families))

    def test_fan_previews_are_not_stable(self):
        for row in self.fan_rows:
            self.assertNotEqual(
                row["intended_channel"],
                "stable",
                f"{row['config_string']} must not be stable",
            )
        self.assertTrue(self.policy["guardrails"]["fan_previews_must_not_be_stable"])

    def test_fan_previews_carry_a_stable_blocker(self):
        for row in self.fan_rows:
            self.assertTrue(
                row["stable_blocker"],
                f"{row['config_string']} must record a stable blocker",
            )


class WarningTextTests(unittest.TestCase):
    """Preview targets require release-note warning text."""

    @classmethod
    def setUpClass(cls):
        cls.policy = _load(POLICY_PATH)

    def test_warning_copy_defined_for_preview_tiers(self):
        copy = self.policy["warning_copy"]
        self.assertIn("preview", copy)
        self.assertIn("advanced-preview", copy)
        for key in ("preview", "advanced-preview"):
            self.assertGreater(len(copy[key].strip()), 40)

    def test_non_stable_tiers_require_warnings(self):
        for name, tier in self.policy["channel_tiers"].items():
            if name == "stable":
                self.assertFalse(tier["warning_required"])
            else:
                self.assertTrue(tier["warning_required"])
                self.assertIsNotNone(tier["warning_copy_key"])

    def test_preview_matrix_rows_require_warning_copy(self):
        for row in self.policy["preview_release_matrix"]:
            if row["intended_channel"] == "stable":
                continue
            self.assertTrue(
                row["warning_copy_required"],
                f"{row['config_string']} preview row must require warning copy",
            )

    def test_warning_copy_keys_resolve(self):
        for name, tier in self.policy["channel_tiers"].items():
            key = tier["warning_copy_key"]
            if key is None:
                continue
            self.assertIn(key, self.policy["warning_copy"])


class WebflashMatrixTests(unittest.TestCase):
    """WebFlash build matrix may include preview targets without stable promotion."""

    @classmethod
    def setUpClass(cls):
        cls.policy = _load(POLICY_PATH)

    def test_policy_permits_preview_in_webflash_without_stable(self):
        self.assertTrue(
            self.policy["guardrails"][
                "webflash_build_matrix_may_include_preview_without_stable_promotion"
            ]
        )

    def test_preview_exposure_is_acknowledgement_gated(self):
        self.assertEqual(
            self.policy["channel_tiers"]["preview"]["webflash_exposure_class"],
            "acknowledgement-gated",
        )
        self.assertEqual(
            self.policy["channel_tiers"]["advanced-preview"]["webflash_exposure_class"],
            "acknowledgement-gated-advanced",
        )

    def test_existing_preview_build_matches_live_webflash_builds(self):
        # The already-published LED preview must agree with config/webflash-builds.json,
        # proving the matrix already carries a preview target without stable promotion.
        builds = _load(REPO_ROOT / "config" / "webflash-builds.json")["builds"]
        led_builds = {
            b["config_string"]: b
            for b in builds
            if b["config_string"] == "Ceiling-POE-VentIQ-RoomIQ-LED"
        }
        self.assertIn("Ceiling-POE-VentIQ-RoomIQ-LED", led_builds)
        self.assertEqual(led_builds["Ceiling-POE-VentIQ-RoomIQ-LED"]["channel"], "preview")


class NoFakeEvidenceTests(unittest.TestCase):
    """No fake hardware evidence / compliance is claimed anywhere in the policy."""

    @classmethod
    def setUpClass(cls):
        cls.policy = _load(POLICY_PATH)

    def test_scope_disclaims_evidence_and_publication(self):
        scope = self.policy["scope"]
        self.assertFalse(scope["publishes_artifacts"])
        self.assertFalse(scope["touches_webflash_repo"])
        self.assertFalse(scope["claims_bench_evidence"])
        self.assertFalse(scope["claims_compliance"])
        self.assertFalse(scope["marks_any_schematic_verified"])
        self.assertFalse(scope["marks_any_product_stable"])

    def test_no_matrix_row_claims_bench_evidence_or_verified_schematic(self):
        for row in self.policy["preview_release_matrix"]:
            self.assertFalse(
                row["bench_evidence_claimed"],
                f"{row['config_string']} must not claim bench evidence",
            )
            self.assertFalse(
                row["schematic_status_verified_claim"],
                f"{row['config_string']} must not claim a verified schematic",
            )

    def test_preview_tiers_cannot_claim_bench_evidence(self):
        for name in ("preview", "advanced-preview"):
            self.assertFalse(self.policy["channel_tiers"][name]["may_claim_bench_evidence"])

    def test_no_preview_row_is_marked_production_or_required(self):
        for row in self.policy["preview_release_matrix"]:
            if row["intended_channel"] == "stable":
                continue
            self.assertFalse(
                row["required_config"],
                f"{row['config_string']} preview row must not be a REQUIRED_CONFIG",
            )

    def test_only_already_stable_row_is_required_config(self):
        for row in self.policy["preview_release_matrix"]:
            if row.get("required_config"):
                self.assertEqual(row["intended_channel"], "stable")


if __name__ == "__main__":
    unittest.main(verbosity=2)

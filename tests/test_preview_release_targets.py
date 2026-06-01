#!/usr/bin/env python3
"""Tests for the concrete preview release-target manifest.

RELEASE-PREVIEW-TARGETS-ALL-PRODUCTS-001.

These guard ``config/preview-release-targets.json`` — the concrete,
CI-consumable preview / advanced-preview release-target manifest for every
buildable Sense360 firmware target. The manifest makes the eligibility policy
in ``config/release-channel-policy.json`` (RELEASE-PREVIEW-ALL-PRODUCTS-001)
actionable while staying metadata only: it publishes no firmware, adds no
``config/webflash-builds.json`` row, flips no ``config/product-catalog.json``
status, promotes nothing to stable, claims no bench / compliance / hardware /
build evidence, and does not touch the WebFlash repo.

Invariants asserted (matching the task contract):

  * every buildable product has a concrete target with a config string, YAML
    path, channel, expected artifact name, release-note warning text, WebFlash
    import eligibility, and a stable blocker;
  * preview is allowed without hardware proof and is never stable / recommended
    / a default / a REQUIRED_CONFIG / a customer-kit default;
  * TRIAC is advanced-preview only, with the mains-risk warning, not
    WebFlash-importable, and recorded as a build blocker;
  * fan-driver previews are manual-candidate-only (never WebFlash-importable);
  * no target claims bench evidence, a verified schematic, hardware proof, or
    build proof, and no target is promoted to stable;
  * the manifest agrees with the policy matrix, the manual lane, and the live
    WebFlash build ledger.

Uses Python's stdlib unittest (matching the no-pytest convention the other
validators in this repo use). Run with::

    python3 tests/test_preview_release_targets.py
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from typing import Any, Dict

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from product_name_mapper import generate_webflash_filename  # noqa: E402
from validate_preview_release_targets import validate  # noqa: E402

MANIFEST_PATH = REPO_ROOT / "config" / "preview-release-targets.json"
POLICY_PATH = REPO_ROOT / "config" / "release-channel-policy.json"
COMPAT_PATH = REPO_ROOT / "config" / "webflash-compatibility.json"
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"
MANUAL_PATH = REPO_ROOT / "config" / "manual-firmware-artifacts.json"

LED_PREVIEW_CONFIG = "Ceiling-POE-VentIQ-RoomIQ-LED"
RELEASE_ONE_CONFIG = "Ceiling-POE-VentIQ-RoomIQ"
FANTRIAC_CONFIG = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"
FAN_DRIVER_TOKENS = ("FanRelay", "FanPWM", "FanDAC", "FanTRIAC")


def _load(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


class ManifestStructureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = _load(MANIFEST_PATH)
        cls.targets = cls.manifest["targets"]

    def test_manifest_validates_clean(self) -> None:
        errors = validate(
            self.manifest,
            _load(POLICY_PATH),
            _load(COMPAT_PATH),
            _load(BUILDS_PATH),
            _load(CATALOG_PATH),
            _load(MANUAL_PATH),
        )
        self.assertEqual(errors, [], "\n".join(errors))

    def test_identity_and_schema(self) -> None:
        self.assertEqual(self.manifest["schema_version"], 1)
        self.assertEqual(
            self.manifest["id"], "RELEASE-PREVIEW-TARGETS-ALL-PRODUCTS-001"
        )
        self.assertTrue(
            (REPO_ROOT / self.manifest["canonical_doc"]).is_file(),
            "canonical doc must exist",
        )

    def test_scope_is_metadata_only(self) -> None:
        scope = self.manifest["scope"]
        for flag in (
            "publishes_artifacts",
            "touches_webflash_repo",
            "adds_webflash_builds_entries",
            "flips_product_catalog_status",
            "marks_any_product_stable",
            "claims_bench_evidence",
            "claims_compliance",
            "claims_hardware_proof",
            "claims_build_proof",
        ):
            self.assertIs(scope[flag], False, f"scope.{flag} must be false")

    def test_targets_unique_and_counted(self) -> None:
        ids = [t["target_id"] for t in self.targets]
        self.assertEqual(len(ids), len(set(ids)), "target_id values must be unique")
        cfgs = [t["config_string"] for t in self.targets]
        self.assertEqual(
            len(cfgs), len(set(cfgs)), "config_string values must be unique"
        )
        self.assertEqual(self.manifest["totals"]["targets"], len(self.targets))

    def test_every_target_has_the_eight_required_attributes(self) -> None:
        # Task item 2: config string, YAML path, channel, expected artifact
        # name, release-note warning text, WebFlash import eligibility, stable
        # blocker. (Stable baseline excepted from warning / blocker.)
        for t in self.targets:
            with self.subTest(target=t["target_id"]):
                self.assertTrue(t["config_string"])
                self.assertTrue((REPO_ROOT / t["yaml_path"]).is_file())
                self.assertIn(
                    t["channel_tier"], ("stable", "preview", "advanced-preview")
                )
                self.assertTrue(t["expected_artifact_name"].endswith(".bin"))
                self.assertIn("eligible", t["webflash_import_eligibility"])
                if t["channel_tier"] != "stable":
                    self.assertTrue(t["release_note_warning"])
                    self.assertTrue(t["stable_blocker"])


class ChannelAndArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = _load(MANIFEST_PATH)
        cls.targets = cls.manifest["targets"]
        cls.compat = _load(COMPAT_PATH)

    def test_build_channel_is_allowed_by_webflash(self) -> None:
        allowed = set(self.compat["allowed_channels"])
        for t in self.targets:
            with self.subTest(target=t["target_id"]):
                self.assertIn(t["build_channel"], allowed)

    def test_advanced_preview_builds_on_preview_channel(self) -> None:
        mapping = self.manifest["build_channel_mapping"]
        self.assertEqual(mapping["advanced-preview"], "preview")
        for t in self.targets:
            with self.subTest(target=t["target_id"]):
                self.assertEqual(t["build_channel"], mapping[t["channel_tier"]])

    def test_artifact_name_matches_config_and_channel(self) -> None:
        for t in self.targets:
            with self.subTest(target=t["target_id"]):
                expected = (
                    f"Sense360-{t['config_string']}-v{t['version']}"
                    f"-{t['build_channel']}.bin"
                )
                self.assertEqual(t["expected_artifact_name"], expected)


class PreviewGuardrailTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = _load(MANIFEST_PATH)
        cls.preview = [
            t for t in cls.manifest["targets"] if t["channel_tier"] != "stable"
        ]

    def test_there_are_preview_targets(self) -> None:
        self.assertGreaterEqual(len(self.preview), 1)

    def test_preview_never_stable_recommended_or_default(self) -> None:
        for t in self.preview:
            with self.subTest(target=t["target_id"]):
                self.assertNotEqual(t["channel_tier"], "stable")
                self.assertFalse(t["recommended"])
                self.assertFalse(t["customer_default"])
                self.assertFalse(t["required_config"])
                self.assertFalse(t["customer_kit_default"])

    def test_preview_requires_warning_text(self) -> None:
        policy_warning = _load(POLICY_PATH)["warning_copy"]
        for t in self.preview:
            with self.subTest(target=t["target_id"]):
                self.assertTrue(t["warning_copy_required"])
                self.assertIn(t["warning_copy_key"], policy_warning)
                self.assertEqual(
                    t["release_note_warning"],
                    policy_warning[t["warning_copy_key"]],
                )

    def test_preview_never_claims_evidence_or_proof(self) -> None:
        for t in self.preview:
            with self.subTest(target=t["target_id"]):
                self.assertFalse(t["bench_evidence_claimed"])
                self.assertFalse(t["schematic_status_verified_claim"])


class TriacTargetTests(unittest.TestCase):
    """Task item 3: TRIAC advanced-preview, mains warning, not default/stable."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = _load(MANIFEST_PATH)
        cls.triac = [t for t in cls.manifest["targets"] if t.get("is_triac")]

    def test_exactly_one_triac_target(self) -> None:
        self.assertEqual(len(self.triac), 1)
        self.assertEqual(self.triac[0]["config_string"], FANTRIAC_CONFIG)

    def test_triac_is_advanced_preview_with_mains_warning(self) -> None:
        t = self.triac[0]
        self.assertEqual(t["channel_tier"], "advanced-preview")
        self.assertEqual(t["warning_copy_key"], "advanced-preview")
        self.assertIn("MAINS", t["release_note_warning"].upper())
        self.assertEqual(
            t["webflash_import_eligibility"]["exposure_class"],
            "acknowledgement-gated-advanced",
        )

    def test_triac_is_not_recommended_default_required_or_kit_default(self) -> None:
        t = self.triac[0]
        self.assertFalse(t["recommended"])
        self.assertFalse(t["customer_default"])
        self.assertFalse(t["required_config"])
        self.assertFalse(t["customer_kit_default"])

    def test_triac_is_not_webflash_importable_and_is_blocked(self) -> None:
        t = self.triac[0]
        self.assertFalse(t["webflash_import_eligibility"]["eligible"])
        self.assertEqual(t["delivery_lane"], "blocked")
        self.assertTrue(t["build_blocker"])
        self.assertNotEqual(t["channel_tier"], "stable")

    def test_triac_absent_from_webflash_builds(self) -> None:
        builds = {b["config_string"] for b in _load(BUILDS_PATH)["builds"]}
        self.assertNotIn(FANTRIAC_CONFIG, builds)


class FanTargetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = _load(MANIFEST_PATH)
        cls.fans = [
            t
            for t in cls.manifest["targets"]
            if t.get("is_fan") and not t.get("is_triac")
        ]
        cls.manual_yamls = {c["product_yaml"] for c in _load(MANUAL_PATH)["candidates"]}
        cls.catalog_by_cs = {
            p.get("config_string"): p
            for p in _load(CATALOG_PATH)["products"]
            if p.get("config_string")
        }

    def test_three_fan_families_present(self) -> None:
        families = {t["family"] for t in self.fans}
        self.assertEqual(families, {"FanRelay", "FanPWM", "FanDAC"})

    def test_fans_are_manual_candidate_only(self) -> None:
        for t in self.fans:
            with self.subTest(target=t["target_id"]):
                self.assertEqual(t["delivery_lane"], "manual-candidate")
                self.assertFalse(t["webflash_import_eligibility"]["eligible"])
                self.assertIn(t["yaml_path"], self.manual_yamls)
                self.assertNotEqual(t["channel_tier"], "stable")

    def test_fan_catalog_entries_stay_off_the_build_matrix(self) -> None:
        for t in self.fans:
            with self.subTest(target=t["target_id"]):
                entry = self.catalog_by_cs.get(t["config_string"])
                self.assertIsNotNone(entry)
                self.assertIs(entry["webflash_build_matrix"], False)

    def test_fans_are_not_in_webflash_builds(self) -> None:
        builds = {b["config_string"] for b in _load(BUILDS_PATH)["builds"]}
        for t in self.fans:
            with self.subTest(target=t["target_id"]):
                self.assertNotIn(t["config_string"], builds)


class WebflashCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = _load(MANIFEST_PATH)
        cls.by_cs = {t["config_string"]: t for t in cls.manifest["targets"]}
        cls.builds = {b["config_string"]: b for b in _load(BUILDS_PATH)["builds"]}

    def test_every_committed_build_is_represented(self) -> None:
        for cs, build in self.builds.items():
            with self.subTest(config_string=cs):
                self.assertIn(cs, self.by_cs)
                target = self.by_cs[cs]
                self.assertEqual(target["build_channel"], build["channel"])
                self.assertEqual(
                    target["expected_artifact_name"], build["artifact_name"]
                )

    def test_led_preview_is_published_and_agrees_with_ledger(self) -> None:
        t = self.by_cs[LED_PREVIEW_CONFIG]
        self.assertEqual(t["publication_status"], "published-preview")
        self.assertEqual(t["channel_tier"], "preview")
        self.assertIn(LED_PREVIEW_CONFIG, self.builds)

    def test_unpublished_webflash_targets_are_absent_from_ledger(self) -> None:
        for t in self.manifest["targets"]:
            if t["delivery_lane"] != "webflash":
                continue
            if t["publication_status"] in ("published-stable", "published-preview"):
                continue
            with self.subTest(target=t["target_id"]):
                self.assertNotIn(t["config_string"], self.builds)
                self.assertTrue(
                    t["build_blocker"],
                    "an unpublished webflash target must record a build blocker",
                )

    def test_published_targets_match_product_name_mapper(self) -> None:
        # The mapper is the authority the release workflow uses; published
        # artifact names must round-trip through it.
        for t in self.manifest["targets"]:
            if t["publication_status"] not in (
                "published-stable",
                "published-preview",
            ):
                continue
            with self.subTest(target=t["target_id"]):
                stem = Path(t["yaml_path"]).stem
                produced = generate_webflash_filename(
                    stem, t["version"], t["build_channel"]
                )
                self.assertEqual(produced, t["expected_artifact_name"])


class PolicyCorrespondenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = _load(MANIFEST_PATH)
        cls.policy = _load(POLICY_PATH)
        cls.by_cs = {t["config_string"]: t for t in cls.manifest["targets"]}

    def test_warning_copy_matches_policy(self) -> None:
        self.assertEqual(self.manifest["warning_copy"], self.policy["warning_copy"])

    def test_build_channel_mapping_matches_policy(self) -> None:
        self.assertEqual(
            self.manifest["build_channel_mapping"],
            self.policy["build_channel_mapping"],
        )

    def test_every_non_stable_policy_row_has_a_target(self) -> None:
        for row in self.policy["preview_release_matrix"]:
            if row["intended_channel"] == "stable":
                continue
            with self.subTest(config_string=row["config_string"]):
                target = self.by_cs.get(row["config_string"])
                self.assertIsNotNone(
                    target,
                    f"policy preview row {row['config_string']} has no target",
                )
                self.assertEqual(target["channel_tier"], row["intended_channel"])
                self.assertEqual(
                    target["expected_artifact_name"],
                    row["expected_artifact_name"],
                )


class NoStablePromotionTests(unittest.TestCase):
    """The manifest must never promote anything to stable or claim proof."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = _load(MANIFEST_PATH)

    def test_only_the_release_one_baseline_is_stable(self) -> None:
        stable = [t for t in self.manifest["targets"] if t["channel_tier"] == "stable"]
        self.assertEqual(len(stable), 1)
        self.assertEqual(stable[0]["config_string"], RELEASE_ONE_CONFIG)
        # The stable baseline is the only required-config / kit-default target.
        self.assertTrue(stable[0]["required_config"])

    def test_required_config_implies_stable(self) -> None:
        for t in self.manifest["targets"]:
            if t["required_config"]:
                with self.subTest(target=t["target_id"]):
                    self.assertEqual(t["channel_tier"], "stable")

    def test_no_target_claims_bench_or_schematic_evidence(self) -> None:
        for t in self.manifest["targets"]:
            with self.subTest(target=t["target_id"]):
                self.assertFalse(t["bench_evidence_claimed"])
                self.assertFalse(t["schematic_status_verified_claim"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

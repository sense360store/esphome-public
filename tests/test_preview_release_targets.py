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
  * TRIAC is advanced-preview only, with the mains-risk warning, delivered on the
    ``advanced-manual-preview`` lane (no longer ``blocked``), not (yet)
    WebFlash-importable, and recorded with an HW-005 build blocker;
  * fan-driver previews are PREVIEW release targets on the ``manual-preview``
    lane (releasable preview artifact; WebFlash import gated as a follow-up);
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

    def test_triac_is_not_webflash_importable_and_is_advanced_manual_preview(
        self,
    ) -> None:
        t = self.triac[0]
        self.assertFalse(t["webflash_import_eligibility"]["eligible"])
        # Delivered on the advanced-manual-preview lane. TRIAC-UNBLOCK-BUILD-001
        # cleared the HW-005 buildability blocker (build_blocker now null); the
        # target is buildable and the stable_blocker cites PACKAGE-TRIAC-001 +
        # the COMPLIANCE-001-RESOLUTION-001 experimental-lane preconditions
        # (COMPLIANCE-001 closed by posture; the assertion below checks the
        # COMPLIANCE-001 citation substring, which the resolution id carries).
        # Publish is the separate TRIAC-PUBLISH-ADVANCED-PREVIEW-001 follow-up,
        # owned by the commissioning PR.
        self.assertEqual(t["delivery_lane"], "advanced-manual-preview")
        self.assertNotEqual(t["delivery_lane"], "blocked")
        self.assertIsNone(t["build_blocker"])
        self.assertIn("COMPLIANCE-001", t["stable_blocker"])
        self.assertNotEqual(t["channel_tier"], "stable")

    def test_triac_committed_on_experimental_channel_only(self) -> None:
        # TRIAC-COMMISSIONING-001 added FanTRIAC to config/webflash-builds.json
        # on the experimental self-build mains channel only. Its preview-release
        # eligibility target stays advanced-manual-preview (not WebFlash-import
        # eligible); the committed build is the separate experimental lane.
        builds = {b["config_string"]: b for b in _load(BUILDS_PATH)["builds"]}
        self.assertIn(FANTRIAC_CONFIG, builds)
        self.assertEqual(builds[FANTRIAC_CONFIG]["channel"], "experimental")


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

    def test_fans_are_manual_preview_lane(self) -> None:
        # Fan drivers are real PREVIEW release targets delivered on the
        # manual-preview lane. The preview / manual-preview WebFlash import is now
        # ELIGIBLE (RELEASE-PREVIEW-FAN-WEBFLASH-ELIGIBILITY-001) as an
        # Advanced-install-only, acknowledgement-gated preview import; the lane
        # stays manual-preview and no committed webflash-builds.json row is added.
        for t in self.fans:
            with self.subTest(target=t["target_id"]):
                self.assertEqual(t["delivery_lane"], "manual-preview")
                self.assertNotEqual(t["delivery_lane"], "manual-candidate")
                self.assertTrue(t["webflash_import_eligibility"]["eligible"])
                self.assertEqual(
                    t["webflash_import_eligibility"]["exposure_class"],
                    "acknowledgement-gated",
                )
                self.assertIn(t["yaml_path"], self.manual_yamls)
                self.assertNotEqual(t["channel_tier"], "stable")

    def test_fans_are_preview_release_targets_not_passive_candidates(self) -> None:
        # The whole point of RELEASE-PREVIEW-WEBFLASH-ALL-BUILDABLE-001: fan
        # previews are releasable preview targets, not "manual-lane-only".
        for t in self.fans:
            with self.subTest(target=t["target_id"]):
                self.assertEqual(t["channel_tier"], "preview")
                self.assertTrue(t["is_preview_target"])
                self.assertEqual(t["publication_status"], "preview-import-eligible")

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
                if build.get("channel") == "experimental":
                    # FanTRIAC experimental self-build commissioning
                    # (TRIAC-COMMISSIONING-001): the committed build is on the
                    # experimental lane, intentionally a SEPARATE lane from this
                    # advanced-manual-preview eligibility target, so its channel /
                    # artifact differ from the target. It is still represented
                    # (its config has a target) and committed only on experimental.
                    self.assertTrue(target.get("is_triac"))
                    continue
                self.assertEqual(target["build_channel"], build["channel"])
                self.assertEqual(
                    target["expected_artifact_name"], build["artifact_name"]
                )

    def test_led_preview_is_published_and_agrees_with_ledger(self) -> None:
        t = self.by_cs[LED_PREVIEW_CONFIG]
        self.assertEqual(t["publication_status"], "published-preview")
        self.assertEqual(t["channel_tier"], "preview")
        self.assertIn(LED_PREVIEW_CONFIG, self.builds)

    # Ledger-present statuses: the WebFlash release-eligibility row exists in
    # config/webflash-builds.json. "published-*" means an actual published /
    # exposed artifact; "webflash-preview-metadata-ready"
    # (RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001) means the reviewed preview build
    # row exists but no binary / GitHub Release is published yet.
    LEDGER_PRESENT_STATUSES = (
        "published-stable",
        "published-preview",
        "webflash-preview-metadata-ready",
    )

    def test_unpublished_webflash_targets_are_absent_from_ledger(self) -> None:
        for t in self.manifest["targets"]:
            if t["delivery_lane"] != "webflash":
                continue
            if t["publication_status"] in self.LEDGER_PRESENT_STATUSES:
                # Ledger-present targets are covered by
                # test_ledger_present_webflash_targets_agree_with_ledger.
                continue
            with self.subTest(target=t["target_id"]):
                self.assertNotIn(t["config_string"], self.builds)
                self.assertTrue(
                    t["build_blocker"],
                    "an unpublished webflash target must record a build blocker",
                )

    def test_ledger_present_webflash_targets_agree_with_ledger(self) -> None:
        # Every webflash target whose publication_status says its build row
        # exists must actually be in config/webflash-builds.json and agree on
        # channel + artifact name.
        for t in self.manifest["targets"]:
            if t["delivery_lane"] != "webflash":
                continue
            if t["publication_status"] not in self.LEDGER_PRESENT_STATUSES:
                continue
            with self.subTest(target=t["target_id"]):
                self.assertIn(t["config_string"], self.builds)
                build = self.builds[t["config_string"]]
                self.assertEqual(build["channel"], t["build_channel"])
                self.assertEqual(build["artifact_name"], t["expected_artifact_name"])

    def test_metadata_ready_targets_are_the_remaining_room_bundle_previews(self) -> None:
        # RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001 recorded three room-bundle
        # previews as webflash-preview-metadata-ready. STABLE-PROMOTION-
        # RECONCILE-001: two of them have since been promoted and published
        # stable (Ceiling-POE-RoomIQ v1.0.5 on 2026-06-08, Ceiling-POE-AirIQ-
        # RoomIQ v1.0.6 on 2026-06-09, both owner-waiver promotions), so only
        # the Living/Corridor LED bundle still sits metadata-ready on the
        # preview channel (no binary published for it yet).
        metadata_ready = {
            t["config_string"]
            for t in self.manifest["targets"]
            if t["publication_status"] == "webflash-preview-metadata-ready"
        }
        self.assertEqual(
            metadata_ready,
            {
                "Ceiling-POE-RoomIQ-LED",
            },
        )
        by_cs = {t["config_string"]: t for t in self.manifest["targets"]}
        for cs in metadata_ready:
            with self.subTest(config_string=cs):
                t = by_cs[cs]
                self.assertEqual(t["channel_tier"], "preview")
                self.assertEqual(t["delivery_lane"], "webflash")
                self.assertIsNone(t["build_blocker"])
                self.assertIn(cs, self.builds)
                self.assertFalse(t["recommended"])
                self.assertFalse(t["customer_default"])
                self.assertFalse(t["required_config"])
                self.assertFalse(t["customer_kit_default"])
                # Stable stays gated; no evidence is claimed.
                self.assertTrue(t["stable_blocker"])
                self.assertFalse(t["bench_evidence_claimed"])
                self.assertFalse(t["schematic_status_verified_claim"])

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

    def test_stable_targets_mirror_the_ledger_and_baseline_stays_unique(self) -> None:
        # STABLE-PROMOTION-RECONCILE-001: the stable tier now carries the
        # Release-One baseline plus the two owner-waiver promotions (Bedroom
        # v1.0.5, Kitchen v1.0.6). The stable targets must mirror the stable
        # rows of config/webflash-builds.json, and the Release-One baseline
        # must remain the ONLY required-config / customer-default target.
        stable = [t for t in self.manifest["targets"] if t["channel_tier"] == "stable"]
        ledger_stable = {
            b["config_string"]
            for b in _load(BUILDS_PATH)["builds"]
            if b.get("channel") == "stable"
        }
        self.assertEqual({t["config_string"] for t in stable}, ledger_stable)
        required = [t for t in stable if t["required_config"]]
        self.assertEqual(len(required), 1)
        self.assertEqual(required[0]["config_string"], RELEASE_ONE_CONFIG)

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


class AllBuildableReleasableTests(unittest.TestCase):
    """RELEASE-PREVIEW-WEBFLASH-ALL-BUILDABLE-001: every buildable product is a
    preview / advanced-preview release target, and nothing is 'blocked from
    preview' merely for lacking stable evidence."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = _load(MANIFEST_PATH)
        cls.targets = cls.manifest["targets"]

    def test_delivery_lanes_are_the_three_releasable_lanes(self) -> None:
        allowed = {"webflash", "manual-preview", "advanced-manual-preview"}
        for t in self.targets:
            with self.subTest(target=t["target_id"]):
                self.assertIn(t["delivery_lane"], allowed)

    def test_no_target_uses_a_blocked_delivery_lane(self) -> None:
        # "blocked" as a delivery lane is gone: stable can be blocked, preview
        # is not.
        lanes = {t["delivery_lane"] for t in self.targets}
        self.assertNotIn("blocked", lanes)
        self.assertNotIn("manual-candidate", lanes)

    def test_every_preview_target_has_a_releasable_lane(self) -> None:
        for t in self.targets:
            if t["channel_tier"] == "stable":
                continue
            with self.subTest(target=t["target_id"]):
                self.assertIn(
                    t["delivery_lane"],
                    {"webflash", "manual-preview", "advanced-manual-preview"},
                )

    def test_no_publication_status_blocks_preview(self) -> None:
        # No target may be recorded as "blocked-unpublished" / "manual-lane-only"
        # any more: those framed buildable previews as not-releasable.
        for t in self.targets:
            with self.subTest(target=t["target_id"]):
                self.assertNotEqual(t["publication_status"], "blocked-unpublished")
                self.assertNotEqual(t["publication_status"], "manual-lane-only")


if __name__ == "__main__":
    unittest.main(verbosity=2)

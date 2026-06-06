#!/usr/bin/env python3
"""Regression guard for the room-bundle fan-control preview PUBLISH PLAN.

ROOM-BUNDLE-FAN-PUBLISH-PLAN-001.

This plan PR verifies — without publishing anything — that the five
full-composition Bathroom / Kitchen fan-control room-bundle configs that now
carry hosted full ESPHome compile proof (run ``26913592989``) are ready to be
published as preview artifacts, decides the publish lane (a small additive
extension to the existing manual-preview fan publish workflow, queued as
``ROOM-BUNDLE-FAN-PUBLISH-WORKFLOW-001`` then ``ROOM-BUNDLE-FAN-PUBLISH-RUN-001``),
and records the per-target publish metadata. This guard locks the invariants the
plan asserts (matching the task's test list) so they cannot silently regress:

  * the publish scope is exactly the **five** compile-validated room-bundle fan
    configs (``Ceiling-POE-VentIQ-FanPWM-RoomIQ``,
    ``Ceiling-POE-VentIQ-FanDAC-RoomIQ``, ``Ceiling-POE-AirIQ-FanRelay-RoomIQ``,
    ``Ceiling-POE-AirIQ-FanDAC-RoomIQ``, ``Ceiling-POE-AirIQ-FanPWM-RoomIQ``);
  * all five cite firmware-build compile evidence run ``26913592989``;
  * the two FanDAC artifacts record the GP8403 IC2 ``0x5A`` requirement
    (IC1 ``0x58``, ``0x59`` forbidden with VentIQ/AirIQ) and ``FANDAC-I2C-ADDR-001``
    pending hardware verification — no bench proof claimed;
  * TRIAC (``Ceiling-POE-VentIQ-FanTRIAC-RoomIQ``) is excluded (``HW-005``,
    build-blocked, no compile proof, no ``.bin`` named);
  * no stable / recommended / default / buyable status is claimed;
  * no hardware / bench / compliance / safety / commercial proof is claimed;
  * WebFlash import is only AFTER artifact publication (separately gated, no
    ``config/webflash-builds.json`` row, WebFlash repo untouched);
  * artifact names follow the ``Sense360-{config}-v{version}-{channel}.bin``
    contract and the doc names no ``.bin`` outside the publish set + the stable
    Simple-install cross-reference;
  * the publish-lane decision is real — the existing manual-preview fan publish
    validator stays hard-scoped to the three single-driver configs (this PR does
    not extend it), and the plan queues the additive workflow rather than hacking
    fans into ``config/webflash-builds.json``; and
  * the hard guardrails hold — no ``manifest.json`` / ``firmware/sources.json`` /
    ``.bin`` produced, the five are not silently added to any publish ledger.

Uses Python's stdlib unittest (matching the no-pytest convention the other
validators in this repo use). Run with::

    python3 tests/test_room_bundle_fan_publish_plan.py
"""

from __future__ import annotations

import importlib.util
import json
import re
import unittest
from pathlib import Path
from typing import Any, Dict

REPO_ROOT = Path(__file__).resolve().parent.parent
VARIANTS_PATH = REPO_ROOT / "config" / "room-bundle-fan-variants.json"
COMPILE_TARGETS_PATH = REPO_ROOT / "config" / "compile-only-targets.json"
CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
LEDGER_PATH = REPO_ROOT / "config" / "preview-fan-triac-build-rows.json"
MANUAL_PATH = REPO_ROOT / "config" / "manual-firmware-artifacts.json"
SHOP_PATH = REPO_ROOT / "config" / "shop-commercial-source-of-truth.json"
PLAN_DOC = REPO_ROOT / "docs" / "room-bundle-fan-publish-plan.md"
MANUAL_PUBLISH_VALIDATOR_PATH = (
    REPO_ROOT / "scripts" / "validate_manual_preview_fan_publish.py"
)

PLAN_ID = "ROOM-BUNDLE-FAN-PUBLISH-PLAN-001"
WORKFLOW_FOLLOWUP_ID = "ROOM-BUNDLE-FAN-PUBLISH-WORKFLOW-001"
RUN_FOLLOWUP_ID = "ROOM-BUNDLE-FAN-PUBLISH-RUN-001"
COMPILE_RUN_ID = 26913592989
# The OTHER fan lane's compile run (the three single-driver fans). The plan's
# gap analysis must distinguish it from ours.
SINGLE_DRIVER_COMPILE_RUN_ID = 26821900127
VERSION = "1.0.0"
LAUNCH_SKU = "S360-KIT-BATH-P"

SIMPLE_INSTALL_CONFIG = "Ceiling-POE-VentIQ-RoomIQ"
SIMPLE_INSTALL_ARTIFACT = "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin"

# The five compile-validated full-composition room-bundle fan configs.
ROOM_BUNDLE_CONFIGS = (
    "Ceiling-POE-VentIQ-FanPWM-RoomIQ",
    "Ceiling-POE-VentIQ-FanDAC-RoomIQ",
    "Ceiling-POE-AirIQ-FanRelay-RoomIQ",
    "Ceiling-POE-AirIQ-FanDAC-RoomIQ",
    "Ceiling-POE-AirIQ-FanPWM-RoomIQ",
)
# The two FanDAC configs that carry the 0x5A requirement.
FANDAC_CONFIGS = (
    "Ceiling-POE-VentIQ-FanDAC-RoomIQ",
    "Ceiling-POE-AirIQ-FanDAC-RoomIQ",
)
# TRIAC is out of scope (HW-005).
TRIAC_CONFIG = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"
# The three single-driver manual-preview fan configs the EXISTING workflow owns.
SINGLE_DRIVER_FAN_CONFIGS = (
    "Ceiling-POE-VentIQ-FanRelay-RoomIQ",
    "Ceiling-POE-FanPWM",
    "Ceiling-POE-FanDAC",
)


def _artifact(config_string: str) -> str:
    return f"Sense360-{config_string}-v{VERSION}-preview.bin"


# Every Sense360-*.bin the plan doc may name: the five room-bundle preview
# artifacts (the publish set) plus the stable Bathroom Simple-install reference.
ALLOWED_BIN_ARTIFACTS = {_artifact(cs) for cs in ROOM_BUNDLE_CONFIGS} | {
    SIMPLE_INSTALL_ARTIFACT
}
FORBIDDEN_BIN_TOKENS = ("FanTRIAC", "TRIAC")
FAN_FAMILY_TOKENS = ("FanRelay", "FanPWM", "FanDAC", "FanTRIAC")
BIN_TOKEN_RE = re.compile(r"Sense360-[A-Za-z0-9.\-]+\.bin")

POSTURE_FLAGS_MUST_BE_FALSE = (
    "recommended",
    "customer_default",
    "buyable",
    "bench_evidence_claimed",
    "compliance_claimed",
)


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _variants_by_config() -> Dict[str, Dict[str, Any]]:
    data = _load_json(VARIANTS_PATH)
    return {
        v["intended_firmware_config_string"]: v
        for v in data["fan_variant_candidates"]
    }


def _compile_targets_by_config() -> Dict[str, Dict[str, Any]]:
    data = _load_json(COMPILE_TARGETS_PATH)
    return {t["config_string"]: t for t in data["targets"] if t.get("config_string")}


def _catalog_by_config() -> Dict[str, Dict[str, Any]]:
    data = _load_json(CATALOG_PATH)
    return {p["config_string"]: p for p in data["products"] if p.get("config_string")}


def _webflash_config_strings() -> set[str]:
    return {b["config_string"] for b in _load_json(BUILDS_PATH)["builds"]}


def _normalise(text: str) -> str:
    """Lowercase; drop blockquote markers / backticks / table pipes / emphasis;
    collapse whitespace so wrapped prose still matches regardless of styling."""
    lines = [re.sub(r"^\s*>\s?", "", ln) for ln in text.splitlines()]
    joined = " ".join(lines).replace("`", "").replace("|", " ").replace("*", "")
    return re.sub(r"\s+", " ", joined).lower()


class PublishScopeTests(unittest.TestCase):
    """Task: publish plan includes exactly the five compiled configs."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.variants = _variants_by_config()
        cls.targets = _compile_targets_by_config()
        cls.text = PLAN_DOC.read_text(encoding="utf-8")

    def test_source_validated_set_is_exactly_the_five(self) -> None:
        validated = _load_json(VARIANTS_PATH)["compile_results"][
            "validated_config_strings"
        ]
        self.assertEqual(sorted(validated), sorted(ROOM_BUNDLE_CONFIGS))

    def test_each_config_is_compile_validated_full(self) -> None:
        for cs in ROOM_BUNDLE_CONFIGS:
            with self.subTest(config_string=cs):
                target = self.targets[cs]
                self.assertEqual(
                    target["compile_validation_status"], "validated-full-compile"
                )
                variant = self.variants[cs]
                self.assertEqual(
                    variant["firmware_config_status"],
                    "buildable-preview-compile-validated",
                )

    def test_plan_doc_names_all_five_configs_and_artifacts(self) -> None:
        for cs in ROOM_BUNDLE_CONFIGS:
            with self.subTest(config_string=cs):
                self.assertIn(cs, self.text)
                self.assertIn(_artifact(cs), self.text)

    def test_plan_doc_records_product_and_bundle_yaml_per_config(self) -> None:
        for cs in ROOM_BUNDLE_CONFIGS:
            with self.subTest(config_string=cs):
                ev = self.variants[cs]["firmware_config_evidence"]
                self.assertIn(ev["product_yaml"], self.text)
                self.assertIn(ev["bundle_yaml"], self.text)
                # The shim product YAML actually exists on disk.
                self.assertTrue((REPO_ROOT / ev["product_yaml"]).is_file())
                self.assertTrue((REPO_ROOT / ev["bundle_yaml"]).is_file())


class CompileEvidenceTests(unittest.TestCase):
    """Task: all five cite run 26913592989."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.variants = _variants_by_config()
        cls.targets = _compile_targets_by_config()
        cls.text = PLAN_DOC.read_text(encoding="utf-8")

    def test_source_data_cites_run_26913592989(self) -> None:
        for cs in ROOM_BUNDLE_CONFIGS:
            with self.subTest(config_string=cs):
                ce_target = self.targets[cs]["compile_evidence"]
                self.assertEqual(ce_target["run_id"], COMPILE_RUN_ID)
                self.assertEqual(ce_target["result"], "success")
                self.assertEqual(ce_target["proof_scope"], "firmware-build-only")
                self.assertIn("hardware", ce_target["not_proof_of"])
                self.assertIn("compliance", ce_target["not_proof_of"])
                ce_variant = self.variants[cs]["firmware_config_evidence"][
                    "compile_evidence"
                ]
                self.assertEqual(ce_variant["run_id"], COMPILE_RUN_ID)

    def test_plan_doc_cites_the_compile_run(self) -> None:
        self.assertIn(str(COMPILE_RUN_ID), self.text)
        # Every config sits under a heading that the doc ties to the run; the
        # whole doc is keyed off run 26913592989, so a single mention suffices,
        # but assert it is referenced at least in the common-fields and proof
        # sections (>= 2 occurrences) to lock it in.
        self.assertGreaterEqual(self.text.count(str(COMPILE_RUN_ID)), 2)


class FanDacRequirementTests(unittest.TestCase):
    """Task: FanDAC artifacts include 0x5A requirement and pending hardware
    verification (and claim no bench proof)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.variants = _variants_by_config()
        cls.text = PLAN_DOC.read_text(encoding="utf-8")
        cls.norm = _normalise(cls.text)

    def test_source_fandac_address_requirement(self) -> None:
        for cs in FANDAC_CONFIGS:
            with self.subTest(config_string=cs):
                req = self.variants[cs]["fan_dac_address_requirement"]
                self.assertEqual(req["gp8403_ic1"], "0x58")
                self.assertEqual(req["gp8403_ic2"], "0x5A")
                self.assertEqual(req["forbidden_gp8403_address"], "0x59")
                self.assertEqual(req["sgp41"], "0x59")
                self.assertEqual(
                    req["bench_verification_followup"], "FANDAC-I2C-ADDR-001"
                )

    def test_plan_doc_records_fandac_addresses_and_pending(self) -> None:
        # The doc must record IC1 0x58, IC2 0x5A, 0x59 forbidden, and the pending
        # bench-verification follow-up.
        self.assertIn("0x58", self.norm)
        self.assertIn("0x5a", self.norm)
        self.assertIn("0x59", self.norm)
        self.assertIn("forbidden", self.norm)
        self.assertIn("fandac-i2c-addr-001", self.norm)
        self.assertIn("pending", self.norm)
        # Both FanDAC config strings appear in the doc.
        for cs in FANDAC_CONFIGS:
            self.assertIn(cs, self.text)

    def test_plan_doc_claims_no_fandac_bench_proof(self) -> None:
        # The override is compile-time only; no bench / hardware proof claimed.
        self.assertIn("not bench verified", self.norm)
        self.assertIn("no fandac bench proof is claimed", self.norm)


class TriacExcludedTests(unittest.TestCase):
    """Task: no TRIAC."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.variants = _variants_by_config()
        cls.text = PLAN_DOC.read_text(encoding="utf-8")
        cls.norm = _normalise(cls.text)

    def test_triac_not_in_publish_set(self) -> None:
        self.assertNotIn(TRIAC_CONFIG, ROOM_BUNDLE_CONFIGS)

    def test_source_triac_is_publish_blocked_not_build_blocked(self) -> None:
        triac = self.variants[TRIAC_CONFIG]
        self.assertEqual(triac["firmware_config_status"], "defined-build-blocked")
        ev = triac["firmware_config_evidence"]
        # HW-005 buildability is RESOLVED (TRIAC-PINMAP-CORRECT-001); the
        # remaining blocker is the advanced-manual-preview PUBLISH gate
        # (PACKAGE-TRIAC-001 + COMPLIANCE-001), recorded out of the publish set.
        self.assertTrue(ev["buildable_now"])
        self.assertIsNone(ev["build_blocker"])
        self.assertIn("HW-005", ev["build_blocker_history"])
        gate = triac["advanced_preview_publish_gate"]
        self.assertEqual(
            set(gate["gated_by"]), {"PACKAGE-TRIAC-001", "COMPLIANCE-001"}
        )

    def test_plan_doc_marks_triac_out_of_scope_under_hw005(self) -> None:
        self.assertIn(TRIAC_CONFIG, self.text)
        self.assertIn("hw-005", self.norm)
        self.assertIn("out of scope", self.norm)

    def test_plan_doc_names_no_triac_bin_artifact(self) -> None:
        for token in BIN_TOKEN_RE.findall(self.text):
            for forbidden in FORBIDDEN_BIN_TOKENS:
                with self.subTest(artifact=token, token=forbidden):
                    self.assertNotIn(forbidden.lower(), token.lower())


class NoStableRecommendedDefaultBuyableTests(unittest.TestCase):
    """Task: no stable/recommended/default/buyable wording (no positive claim)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.variants = _variants_by_config()
        cls.norm = _normalise(PLAN_DOC.read_text(encoding="utf-8"))

    def test_source_posture_flags_are_false(self) -> None:
        for cs in ROOM_BUNDLE_CONFIGS:
            variant = self.variants[cs]
            with self.subTest(config_string=cs):
                for flag in POSTURE_FLAGS_MUST_BE_FALSE:
                    self.assertFalse(variant[flag], f"{cs}: {flag} must be false")
                self.assertEqual(variant["stable_status"], "blocked")

    def test_plan_doc_disclaims_each_status(self) -> None:
        for phrase in (
            "not stable",
            "not recommended",
            "not a customer default",
            "not buyable",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.norm)

    def test_plan_doc_makes_no_positive_status_claim(self) -> None:
        # No phrasing that would promote any of the five to a positive status.
        # Only unambiguous positive claims are listed here; the negative stable
        # posture ("nothing is promoted to stable", "not yet stable") is covered
        # by test_plan_doc_disclaims_each_status + test_source_posture_flags_are_false,
        # so stable-promotion phrases (which appear naturally in disclaimers) are
        # deliberately excluded from this contiguous-substring guard.
        for bad in (
            "is buyable",
            "are buyable",
            "now buyable",
            "becomes buyable",
            "is recommended",
            "are recommended",
            "now recommended",
            "becomes recommended",
            "is a customer default",
            "are customer defaults",
        ):
            with self.subTest(phrase=bad):
                self.assertNotIn(bad, self.norm)


class NoHardwareComplianceProofTests(unittest.TestCase):
    """Task: no hardware/compliance proof claims."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.norm = _normalise(PLAN_DOC.read_text(encoding="utf-8"))

    def test_plan_doc_states_compile_proof_only(self) -> None:
        self.assertIn("firmware-build", self.norm)
        self.assertIn("compile proof", self.norm)

    def test_plan_doc_disclaims_hardware_and_compliance(self) -> None:
        self.assertIn("no hardware", self.norm)
        self.assertIn("compliance", self.norm)
        self.assertIn("no bench evidence", self.norm)


class WebflashImportAfterPublicationTests(unittest.TestCase):
    """Task: WebFlash import is only after artifact publication."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.norm = _normalise(PLAN_DOC.read_text(encoding="utf-8"))
        cls.catalog = _catalog_by_config()

    def test_plan_doc_orders_import_after_publication(self) -> None:
        self.assertIn("after artifact publication", self.norm)
        self.assertIn("post-publication", self.norm)
        self.assertIn("separately gated", self.norm)

    def test_no_fan_token_in_webflash_builds(self) -> None:
        cs_set = _webflash_config_strings()
        for cs in ROOM_BUNDLE_CONFIGS + (TRIAC_CONFIG,):
            with self.subTest(config_string=cs):
                self.assertNotIn(cs, cs_set)
        for entry_cs in cs_set:
            for token in FAN_FAMILY_TOKENS:
                with self.subTest(config_string=entry_cs, token=token):
                    self.assertNotIn(token.lower(), entry_cs.lower())

    def test_catalog_keeps_webflash_build_matrix_false(self) -> None:
        for cs in ROOM_BUNDLE_CONFIGS:
            with self.subTest(config_string=cs):
                product = self.catalog[cs]
                self.assertEqual(product["status"], "hardware-pending")
                self.assertFalse(product.get("webflash_build_matrix", False))
                self.assertIsNone(product.get("artifact_name"))


class ArtifactNameContractTests(unittest.TestCase):
    """Task: artifact names follow the contract; the doc names only the
    publish set + the stable Simple-install cross-reference."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = PLAN_DOC.read_text(encoding="utf-8")

    def test_each_artifact_name_follows_contract(self) -> None:
        for cs in ROOM_BUNDLE_CONFIGS:
            with self.subTest(config_string=cs):
                expected = _artifact(cs)
                self.assertTrue(expected.endswith("-preview.bin"))
                self.assertNotIn("-stable.bin", expected)
                self.assertIn(expected, self.text)

    def test_doc_bin_tokens_are_exactly_the_publish_set(self) -> None:
        tokens = set(BIN_TOKEN_RE.findall(self.text))
        self.assertTrue(
            tokens.issubset(ALLOWED_BIN_ARTIFACTS),
            f"plan names unexpected .bin artifact(s): "
            f"{sorted(tokens - ALLOWED_BIN_ARTIFACTS)}",
        )
        for cs in ROOM_BUNDLE_CONFIGS:
            self.assertIn(_artifact(cs), tokens)


class PublishLaneDecisionTests(unittest.TestCase):
    """Task item 6: the publish-lane decision is documented and the existing
    manual-preview fan publish lane is NOT extended by this PR."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = PLAN_DOC.read_text(encoding="utf-8")
        cls.norm = _normalise(cls.text)

    def test_plan_doc_is_self_identified(self) -> None:
        self.assertTrue(PLAN_DOC.is_file())
        self.assertIn(PLAN_ID, self.text)

    def test_plan_doc_documents_the_gap(self) -> None:
        # Names the existing workflow + validator and the canonical source.
        self.assertIn("manual-preview-fan-publish.yml", self.text)
        self.assertIn("validate_manual_preview_fan_publish.py", self.text)
        self.assertIn("room-bundle-fan-variants.json", self.text)
        # Distinguishes the two compile runs (ours vs the single-driver lane's).
        self.assertIn(str(COMPILE_RUN_ID), self.text)
        self.assertIn(str(SINGLE_DRIVER_COMPILE_RUN_ID), self.text)
        # Explicitly refuses the hack.
        self.assertIn("does not add", self.norm)
        self.assertIn("webflash-builds.json", self.text)

    def test_plan_doc_queues_workflow_and_run_followups(self) -> None:
        self.assertIn(WORKFLOW_FOLLOWUP_ID, self.text)
        self.assertIn(RUN_FOLLOWUP_ID, self.text)

    def test_plan_doc_keeps_launch_sku_and_simple_install_unchanged(self) -> None:
        self.assertIn(LAUNCH_SKU, self.text)
        self.assertIn(SIMPLE_INSTALL_ARTIFACT, self.text)
        shop = _load_json(SHOP_PATH)["launch_product"]
        self.assertEqual(shop["shop_sku"], LAUNCH_SKU)
        self.assertEqual(shop["firmware_config"], SIMPLE_INSTALL_CONFIG)

    def test_existing_manual_preview_lane_unchanged(self) -> None:
        # The existing manual-preview fan publish validator stays hard-scoped to
        # the three single-driver configs; this PR does not extend it (no scope
        # drift). Importing it and replaying its selection proves the lane is
        # untouched and the five room-bundle configs are NOT selectable there.
        validator = _load_module(
            "validate_manual_preview_fan_publish_for_room_bundle_plan",
            MANUAL_PUBLISH_VALIDATOR_PATH,
        )
        self.assertEqual(
            tuple(validator.FAN_CONFIGS), SINGLE_DRIVER_FAN_CONFIGS
        )
        rows, errors = validator._select_rows(
            _load_json(LEDGER_PATH),
            _load_json(MANUAL_PATH),
            _load_json(BUILDS_PATH),
            version=VERSION,
            release_target="all-manual-preview-fans",
        )
        self.assertEqual(errors, [], "\n".join(errors))
        selected = sorted(r["config_string"] for r in rows)
        self.assertEqual(selected, sorted(SINGLE_DRIVER_FAN_CONFIGS))
        for cs in ROOM_BUNDLE_CONFIGS:
            self.assertNotIn(cs, selected)


class NotSilentlyAddedToPublishLedgersTests(unittest.TestCase):
    """The plan must not silently extend any publish ledger with the five."""

    def test_five_not_in_single_driver_ledger(self) -> None:
        ledger_cs = {r["config_string"] for r in _load_json(LEDGER_PATH)["rows"]}
        for cs in ROOM_BUNDLE_CONFIGS:
            with self.subTest(config_string=cs):
                self.assertNotIn(cs, ledger_cs)

    def test_five_not_in_manual_lane(self) -> None:
        manual = _load_json(MANUAL_PATH)
        manual_cs = {c.get("config_string") for c in manual["candidates"]}
        manual_ids = {c.get("id") for c in manual["candidates"]}
        for cs in ROOM_BUNDLE_CONFIGS:
            with self.subTest(config_string=cs):
                self.assertNotIn(cs, manual_cs)
        # The manual lane keeps exactly the three single-driver candidates.
        self.assertEqual(manual_ids, {"fanrelay", "fanpwm", "fandac"})


class GuardrailTests(unittest.TestCase):
    """Hard guardrails: planning only — no publish side effects."""

    def test_no_manifest_or_sources_committed(self) -> None:
        self.assertFalse((REPO_ROOT / "manifest.json").exists())
        self.assertFalse((REPO_ROOT / "firmware" / "sources.json").exists())

    def test_no_bin_committed_anywhere_in_repo(self) -> None:
        bins = [p for p in REPO_ROOT.rglob("*.bin") if ".git" not in p.parts]
        self.assertEqual(bins, [], f"no .bin may be committed; found {bins}")


if __name__ == "__main__":
    unittest.main(verbosity=2)

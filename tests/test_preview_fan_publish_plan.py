#!/usr/bin/env python3
"""Regression guard for the manual-preview FAN artifact PUBLISH PLAN.

RELEASE-PREVIEW-FAN-PUBLISH-PLAN-001.

This plan PR verifies — without publishing anything — that the three buildable
manual-preview fan-control targets are ready to be published, documents the
workflow/publish-path GAP (the existing release workflow publishes only
``config/webflash-builds.json`` rows, which the fan-token guardrail keeps fans
out of; the manual lane is explicitly non-release / expiring), and queues the
workflow work (``RELEASE-PREVIEW-FAN-PUBLISH-WORKFLOW-001``) and the eventual run
(``RELEASE-PREVIEW-FAN-PUBLISH-RUN-001``). This guard locks the invariants the
plan asserts (matching task item 6) so they cannot silently regress:

  * the publish scope is exactly the three buildable ``manual-preview`` fan rows
    (``Ceiling-POE-VentIQ-FanRelay-RoomIQ``, ``Ceiling-POE-FanPWM``,
    ``Ceiling-POE-FanDAC``);
  * TRIAC (``Ceiling-POE-VentIQ-FanTRIAC-RoomIQ``) is excluded due to ``HW-005``
    (build-blocked, no compile proof, not named as a publishable ``.bin``);
  * all three have a validated preview release-note draft;
  * all three cite firmware-build compile evidence (run ``26821900127``);
  * all three remain ``manual-preview`` only (preview channel, not
    WebFlash-importable);
  * no WebFlash build row is added (the ledger adds zero, and no fan token is in
    ``config/webflash-builds.json``);
  * no stable / recommended / default / buyable flag is set;
  * artifact names match the ``Sense360-{config}-v{version}-{channel}.bin``
    naming contract;
  * the workflow GAP is real (fan configs are not selectable / not in the release
    matrix) and the plan documents it + queues the workflow PR instead of hacking
    fans into ``config/webflash-builds.json``; and
  * the hard guardrails hold — no ``manifest.json`` / ``firmware/sources.json`` /
    ``.bin`` produced, launch SKU unchanged, and no fan / TRIAC ``.bin`` other
    than the allowed publish set is named.

Uses Python's stdlib unittest (matching the no-pytest convention the other
validators in this repo use). Run with::

    python3 tests/test_preview_fan_publish_plan.py
"""

from __future__ import annotations

import importlib.util
import json
import re
import unittest
from pathlib import Path
from typing import Any, Dict, List

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER_PATH = REPO_ROOT / "config" / "preview-fan-triac-build-rows.json"
TARGETS_PATH = REPO_ROOT / "config" / "preview-release-targets.json"
POLICY_PATH = REPO_ROOT / "config" / "release-channel-policy.json"
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
MANUAL_PATH = REPO_ROOT / "config" / "manual-firmware-artifacts.json"
SHOP_PATH = REPO_ROOT / "config" / "shop-commercial-source-of-truth.json"
PLAN_DOC = REPO_ROOT / "docs" / "release-preview-fan-publish-plan.md"
DRAFT_DIR = REPO_ROOT / "docs" / "release-notes" / "manual-preview"
NOTES_VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate-webflash-release-notes.py"
LEDGER_VALIDATOR_PATH = (
    REPO_ROOT / "scripts" / "validate_preview_fan_triac_build_rows.py"
)
LIST_TARGETS_PATH = REPO_ROOT / "scripts" / "list_release_targets.py"
BUILD_RELEASE_WORKFLOW = (
    REPO_ROOT / ".github" / "workflows" / "firmware-build-release.yml"
)
MANUAL_WORKFLOW = (
    REPO_ROOT / ".github" / "workflows" / "manual-firmware-artifacts.yml"
)

PLAN_ID = "RELEASE-PREVIEW-FAN-PUBLISH-PLAN-001"
WORKFLOW_FOLLOWUP_ID = "RELEASE-PREVIEW-FAN-PUBLISH-WORKFLOW-001"
RUN_FOLLOWUP_ID = "RELEASE-PREVIEW-FAN-PUBLISH-RUN-001"
COMPILE_RUN_ID = 26821900127
VERSION = "1.0.0"
LAUNCH_SKU = "S360-KIT-BATH-P"
ALL_TARGETS_SENTINEL = "all-release-eligible"

SIMPLE_INSTALL_CONFIG = "Ceiling-POE-VentIQ-RoomIQ"
SIMPLE_INSTALL_ARTIFACT = "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin"

# The three buildable manual-preview fan targets this plan publishes.
FAN_CONFIGS = (
    "Ceiling-POE-VentIQ-FanRelay-RoomIQ",
    "Ceiling-POE-FanPWM",
    "Ceiling-POE-FanDAC",
)
# TRIAC is the fourth ledger row but is out of scope (HW-005).
TRIAC_CONFIG = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"

# Every Sense360-*.bin the plan doc may name: the three fan preview artifacts
# (the publish set) plus the stable Bathroom Simple-install cross-reference.
ALLOWED_BIN_ARTIFACTS = {
    "Sense360-Ceiling-POE-VentIQ-FanRelay-RoomIQ-v1.0.0-preview.bin",
    "Sense360-Ceiling-POE-FanPWM-v1.0.0-preview.bin",
    "Sense360-Ceiling-POE-FanDAC-v1.0.0-preview.bin",
    SIMPLE_INSTALL_ARTIFACT,
}
# No .bin named in the plan may carry a TRIAC token.
FORBIDDEN_BIN_TOKENS = ("FanTRIAC", "TRIAC")
# Fan tokens that must never appear in the release picker / matrix.
FAN_FAMILY_TOKENS = ("FanRelay", "FanPWM", "FanDAC")

BIN_TOKEN_RE = re.compile(r"Sense360-[A-Za-z0-9.\-]+\.bin")

POSTURE_MUST_BE_FALSE = (
    "buyable",
    "recommended",
    "customer_default",
    "stable",
    "release_one_required_config",
)


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


_NOTES = _load_module("vw_release_notes_for_fan_plan", NOTES_VALIDATOR_PATH)
_LEDGER_VALIDATOR = _load_module(
    "validate_fan_triac_rows_for_fan_plan", LEDGER_VALIDATOR_PATH
)
_LIST_TARGETS = _load_module("list_release_targets_for_fan_plan", LIST_TARGETS_PATH)


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rows_by_cs() -> Dict[str, Dict[str, Any]]:
    return {r["config_string"]: r for r in _load_json(LEDGER_PATH)["rows"]}


def _targets_by_id() -> Dict[str, Dict[str, Any]]:
    return {t["target_id"]: t for t in _load_json(TARGETS_PATH)["targets"]}


def _manual_by_id() -> Dict[str, Dict[str, Any]]:
    return {c["id"]: c for c in _load_json(MANUAL_PATH)["candidates"]}


def _builds() -> List[Dict[str, Any]]:
    return _load_json(BUILDS_PATH)["builds"]


def _normalise(text: str) -> str:
    """Lowercase; drop blockquote markers / backticks / table pipes / emphasis;
    collapse whitespace so wrapped prose still matches regardless of styling."""
    lines = [re.sub(r"^\s*>\s?", "", ln) for ln in text.splitlines()]
    joined = " ".join(lines).replace("`", "").replace("|", " ").replace("*", "")
    return re.sub(r"\s+", " ", joined).lower()


def _matrix(version: str, channel: str, release_target: str, event: str) -> List[str]:
    """Replay the generate-matrix filter from firmware-build-release.yml against
    config/webflash-builds.json (version + channel, optional dispatch scope)."""
    rt = release_target
    if event != "workflow_dispatch":
        rt = ""
    if rt in ("", ALL_TARGETS_SENTINEL):
        rt = ""
    rows: List[str] = []
    for entry in _builds():
        if entry.get("version") != version:
            continue
        if entry.get("channel") != channel:
            continue
        if rt and entry.get("config_string") != rt:
            continue
        rows.append(entry["config_string"])
    return rows


def _triggers(data: dict) -> dict:
    # PyYAML parses the bare key ``on:`` as boolean True (YAML 1.1 truthy key).
    raw = data.get("on")
    if raw is None:
        raw = data.get(True)
    return raw if isinstance(raw, dict) else {}


def _dispatch_inputs(workflow_path: Path) -> Dict[str, Any]:
    data = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
    wd = _triggers(data).get("workflow_dispatch") or {}
    return wd.get("inputs") or {}


class PublishScopeTests(unittest.TestCase):
    """Task item 6: scope is exactly the three buildable fan targets."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = _rows_by_cs()

    def test_three_buildable_manual_preview_fan_rows(self) -> None:
        manual_preview = sorted(
            cs
            for cs, row in self.rows.items()
            if row["delivery_lane"] == "manual-preview"
        )
        self.assertEqual(manual_preview, sorted(FAN_CONFIGS))

    def test_each_fan_row_is_buildable_preview(self) -> None:
        for cs in FAN_CONFIGS:
            with self.subTest(config_string=cs):
                row = self.rows[cs]
                self.assertTrue(row["buildable_now"])
                self.assertIsNone(row["build_blocker"])
                self.assertEqual(row["channel_tier"], "preview")
                self.assertEqual(row["build_channel"], "preview")
                self.assertEqual(row["version"], VERSION)


class TriacExcludedTests(unittest.TestCase):
    """Task item 6: TRIAC excluded from the manual-preview publish lane.

    TRIAC-UNBLOCK-BUILD-001 resolved the HW-005 BUILDABILITY blocker, so TRIAC
    is buildable (compile-only); it still stays off the manual-preview publish
    lane (advanced-manual-preview; published separately).
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.triac = _rows_by_cs()[TRIAC_CONFIG]

    def test_triac_is_buildable_and_on_advanced_manual_preview_lane(self) -> None:
        self.assertTrue(self.triac["buildable_now"])
        self.assertIsNone(self.triac["build_blocker"])
        self.assertIsInstance(self.triac["compile_evidence"], dict)
        self.assertIn("COMPLIANCE-001", self.triac["stable_blocker"])
        self.assertEqual(self.triac["delivery_lane"], "advanced-manual-preview")

    def test_triac_is_not_a_manual_preview_publish_target(self) -> None:
        # The publish set is only the manual-preview lane; TRIAC is not on it.
        self.assertNotIn(TRIAC_CONFIG, FAN_CONFIGS)
        self.assertNotEqual(self.triac["delivery_lane"], "manual-preview")


class ReleaseNoteDraftTests(unittest.TestCase):
    """Task item 6: all three have a validated preview release-note draft."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = _rows_by_cs()

    def test_each_fan_draft_exists_and_validates_on_preview(self) -> None:
        for cs in FAN_CONFIGS:
            with self.subTest(config_string=cs):
                draft = DRAFT_DIR / f"{cs.lower()}.md"
                self.assertTrue(draft.is_file(), f"missing draft: {draft}")
                errors = _NOTES.validate_body(
                    draft.read_text(encoding="utf-8"), channel="preview"
                )
                self.assertEqual(errors, [], f"{cs}: {errors}")

    def test_ledger_row_points_at_the_existing_draft(self) -> None:
        for cs in FAN_CONFIGS:
            with self.subTest(config_string=cs):
                draft_rel = self.rows[cs]["release_note_draft"]
                self.assertEqual(
                    draft_rel, f"docs/release-notes/manual-preview/{cs.lower()}.md"
                )
                self.assertTrue((REPO_ROOT / draft_rel).is_file())


class CompileEvidenceTests(unittest.TestCase):
    """Task item 6: all three cite firmware-build compile evidence."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = _rows_by_cs()

    def test_each_fan_row_cites_run_26821900127(self) -> None:
        for cs in FAN_CONFIGS:
            with self.subTest(config_string=cs):
                ev = self.rows[cs]["compile_evidence"]
                self.assertIsInstance(ev, dict)
                self.assertEqual(ev["run_id"], COMPILE_RUN_ID)
                self.assertEqual(ev["proof_class"], "firmware-build-only")
                self.assertEqual(ev["result"], "success")
                self.assertIn("hardware", ev["not_proof_of"])
                self.assertIn("compliance", ev["not_proof_of"])


class ManualPreviewOnlyTests(unittest.TestCase):
    """Task item 6: all three remain manual-preview only."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = _rows_by_cs()
        cls.targets = _targets_by_id()

    def test_rows_are_manual_preview_and_not_webflash_importable(self) -> None:
        for cs in FAN_CONFIGS:
            with self.subTest(config_string=cs):
                row = self.rows[cs]
                self.assertEqual(row["delivery_lane"], "manual-preview")
                self.assertFalse(row["webflash_importable"])
                self.assertIsNone(row["webflash_exposure_class"])
                self.assertEqual(row["warning_copy_key"], "preview")

    def test_preview_target_is_webflash_import_eligible(self) -> None:
        # RELEASE-PREVIEW-FAN-WEBFLASH-ELIGIBILITY-001: the preview-release target
        # is now preview / manual-preview WebFlash-import eligible. The ledger row's
        # own webflash_importable stays false (no committed build row); that is
        # asserted in test_rows_are_manual_preview_and_not_webflash_importable.
        for cs in FAN_CONFIGS:
            with self.subTest(config_string=cs):
                tid = self.rows[cs]["preview_release_target_id"]
                target = self.targets[tid]
                self.assertEqual(target["delivery_lane"], "manual-preview")
                self.assertTrue(
                    target["webflash_import_eligibility"]["eligible"]
                )


class NoWebflashBuildRowsTests(unittest.TestCase):
    """Task item 6: no WebFlash build rows added."""

    def test_ledger_adds_zero_webflash_build_rows(self) -> None:
        self.assertEqual(
            _load_json(LEDGER_PATH)["totals"]["webflash_builds_rows_added"], 0
        )

    def test_no_fan_token_in_webflash_builds(self) -> None:
        ledger_cs = {b["config_string"] for b in _builds()}
        for cs in FAN_CONFIGS + (TRIAC_CONFIG,):
            with self.subTest(config_string=cs):
                self.assertNotIn(cs, ledger_cs)
        for entry in _builds():
            for token in FAN_FAMILY_TOKENS + ("FanTRIAC",):
                with self.subTest(config_string=entry["config_string"], token=token):
                    self.assertNotIn(token.lower(), entry["config_string"].lower())


class NoStableRecommendedDefaultBuyableTests(unittest.TestCase):
    """Task item 6: no stable / recommended / default / buyable flags."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = _rows_by_cs()
        cls.targets = _targets_by_id()

    def test_commercial_posture_locked(self) -> None:
        for cs in FAN_CONFIGS:
            with self.subTest(config_string=cs):
                p = self.rows[cs]["commercial_posture"]
                self.assertEqual(p["visibility"], "hidden")
                for flag in POSTURE_MUST_BE_FALSE:
                    self.assertFalse(p[flag], f"{cs}: posture.{flag} must be false")

    def test_preview_target_is_never_recommended_default_required(self) -> None:
        for cs in FAN_CONFIGS:
            with self.subTest(config_string=cs):
                target = self.targets[self.rows[cs]["preview_release_target_id"]]
                for flag in (
                    "recommended",
                    "customer_default",
                    "required_config",
                    "customer_kit_default",
                ):
                    self.assertFalse(target[flag], f"{cs}: target.{flag} must be false")

    def test_no_fan_row_is_stable_channel(self) -> None:
        for cs in FAN_CONFIGS:
            with self.subTest(config_string=cs):
                self.assertNotEqual(self.rows[cs]["channel_tier"], "stable")
                self.assertNotEqual(self.rows[cs]["build_channel"], "stable")


class ArtifactNameContractTests(unittest.TestCase):
    """Task item 6: artifact names match the naming contract."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = _rows_by_cs()

    def test_each_artifact_name_follows_contract(self) -> None:
        for cs in FAN_CONFIGS:
            with self.subTest(config_string=cs):
                expected = f"Sense360-{cs}-v{VERSION}-preview.bin"
                self.assertEqual(
                    self.rows[cs]["expected_preview_artifact_name"], expected
                )
                self.assertTrue(expected.endswith("-preview.bin"))
                self.assertNotIn("-stable.bin", expected)
                self.assertIn(expected, ALLOWED_BIN_ARTIFACTS)


class WorkflowGapTests(unittest.TestCase):
    """Task item 5/6: the workflow gap is real and the plan documents it."""

    def test_fan_configs_not_selectable_release_targets(self) -> None:
        for cs in FAN_CONFIGS:
            with self.subTest(config_string=cs):
                # validate_target returns an error string (not None) for fans.
                self.assertIsNotNone(
                    _LIST_TARGETS.validate_target(cs, BUILDS_PATH),
                    f"{cs} must NOT be a selectable release target",
                )

    def test_release_matrix_never_yields_a_fan_artifact(self) -> None:
        for event, rt in (
            ("release", ""),
            ("workflow_dispatch", ALL_TARGETS_SENTINEL),
        ):
            got = _matrix(VERSION, "preview", rt, event)
            for cs in FAN_CONFIGS:
                with self.subTest(event=event, config_string=cs):
                    self.assertNotIn(cs, got)

    def test_build_release_picker_carries_no_fan_token(self) -> None:
        inputs = _dispatch_inputs(BUILD_RELEASE_WORKFLOW)
        options = list((inputs.get("release_target") or {}).get("options") or [])
        for opt in options:
            for token in FAN_FAMILY_TOKENS:
                with self.subTest(option=opt, token=token):
                    self.assertNotIn(token.lower(), opt.lower())

    def test_manual_lane_is_non_release(self) -> None:
        manual = _load_json(MANUAL_PATH)
        self.assertFalse(manual["release"])
        self.assertFalse(manual["webflash"])
        self.assertIsNone(manual["release_channel"])
        # Its naming pattern is non-release; it cannot emit a -preview.bin.
        self.assertIn("nonrelease", manual["naming"]["pattern"])


class PublishPlanDocTests(unittest.TestCase):
    """Task items 3 / 5 / 7: the doc records the per-target fields, documents the
    gap, queues the follow-ups, and honours the publish-set guardrails."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = PLAN_DOC.read_text(encoding="utf-8")
        cls.norm = _normalise(cls.text)
        cls.rows = _rows_by_cs()
        cls.manual = _manual_by_id()

    def test_plan_doc_exists_and_is_self_identified(self) -> None:
        self.assertTrue(PLAN_DOC.is_file())
        self.assertIn(PLAN_ID, self.text)

    def test_plan_doc_records_every_required_field_per_target(self) -> None:
        for cs in FAN_CONFIGS:
            row = self.rows[cs]
            with self.subTest(config_string=cs):
                # config string
                self.assertIn(cs, self.text)
                # artifact name
                self.assertIn(row["expected_preview_artifact_name"], self.text)
                # YAML / product path
                self.assertIn(row["product_yaml"], self.text)
                # manual artifact row (candidate id)
                self.assertIn(row["manual_lane_candidate_id"], self.text)
                # release-note draft path
                self.assertIn(f"release-notes/manual-preview/{cs.lower()}.md", self.text)
                # compile evidence run
                self.assertIn(str(COMPILE_RUN_ID), self.text)
                # stable blocker text (backtick-insensitive; SKU codes may be
                # wrapped in inline code in the doc)
                blocker_fragment = row["stable_blocker"].split(".")[0].strip()
                self.assertIn(blocker_fragment, self.text.replace("`", ""))

    def test_plan_doc_records_lane_channel_and_posture(self) -> None:
        for key in (
            "manual-preview",
            "preview",
            "hidden",
            "not buyable",
            "not stable",
            "not recommended",
            "not a customer default",
        ):
            with self.subTest(phrase=key):
                self.assertIn(key, self.norm)

    def test_plan_doc_states_warning_copy_and_no_proof(self) -> None:
        self.assertIn("firmware-build proof only", self.norm)
        self.assertIn("no hardware", self.norm)
        self.assertIn("compliance", self.norm)
        # The preview warning-copy text is reflected in the plan.
        self.assertIn("buildable and installable for testers only", self.norm)

    def test_plan_doc_documents_the_workflow_gap(self) -> None:
        # Names both workflows and the sole-source-of-truth file.
        self.assertIn("firmware-build-release.yml", self.text)
        self.assertIn("manual-firmware-artifacts.yml", self.text)
        self.assertIn("webflash-builds.json", self.text)
        # Explains the manual lane is non-release / expiring.
        self.assertIn("expiring", self.norm)
        # Explicitly refuses the hack.
        self.assertIn("does not add fan rows", self.norm)

    def test_plan_doc_queues_workflow_and_run_followups(self) -> None:
        self.assertIn(WORKFLOW_FOLLOWUP_ID, self.text)
        self.assertIn(RUN_FOLLOWUP_ID, self.text)

    def test_plan_doc_marks_triac_out_of_scope_under_hw005(self) -> None:
        self.assertIn(TRIAC_CONFIG, self.text)
        self.assertIn("hw-005", self.norm)
        self.assertIn("out of scope", self.norm)

    def test_plan_doc_keeps_launch_sku_and_simple_install_unchanged(self) -> None:
        self.assertIn(LAUNCH_SKU, self.text)
        self.assertIn(SIMPLE_INSTALL_ARTIFACT, self.text)
        shop = _load_json(SHOP_PATH)["launch_product"]
        self.assertEqual(shop["shop_sku"], LAUNCH_SKU)
        self.assertEqual(shop["firmware_config"], SIMPLE_INSTALL_CONFIG)

    def test_plan_doc_bin_tokens_are_exactly_the_publish_set(self) -> None:
        tokens = set(BIN_TOKEN_RE.findall(self.text))
        self.assertTrue(
            tokens.issubset(ALLOWED_BIN_ARTIFACTS),
            f"plan names unexpected .bin artifact(s): "
            f"{sorted(tokens - ALLOWED_BIN_ARTIFACTS)}",
        )
        for cs in FAN_CONFIGS:
            self.assertIn(self.rows[cs]["expected_preview_artifact_name"], tokens)

    def test_plan_doc_names_no_triac_bin_artifact(self) -> None:
        for token in BIN_TOKEN_RE.findall(self.text):
            for forbidden in FORBIDDEN_BIN_TOKENS:
                with self.subTest(artifact=token, token=forbidden):
                    self.assertNotIn(forbidden.lower(), token.lower())


class GuardrailTests(unittest.TestCase):
    """Hard guardrails: planning only — no publish side effects."""

    def test_no_manifest_or_sources_committed(self) -> None:
        self.assertFalse((REPO_ROOT / "manifest.json").exists())
        self.assertFalse((REPO_ROOT / "firmware" / "sources.json").exists())

    def test_no_bin_committed_anywhere_in_repo(self) -> None:
        bins = [p for p in REPO_ROOT.rglob("*.bin") if ".git" not in p.parts]
        self.assertEqual(bins, [], f"no .bin may be committed; found {bins}")

    def test_ledger_still_validates_clean(self) -> None:
        # Belt-and-braces: the plan does not perturb the build-row ledger.
        errors = _LEDGER_VALIDATOR.validate(
            _load_json(LEDGER_PATH),
            _load_json(TARGETS_PATH),
            _load_json(POLICY_PATH),
            _load_json(BUILDS_PATH),
            _load_json(MANUAL_PATH),
        )
        self.assertEqual(errors, [], "\n".join(errors))


if __name__ == "__main__":
    unittest.main(verbosity=2)

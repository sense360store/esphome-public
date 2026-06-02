#!/usr/bin/env python3
"""Regression guard for the preview WebFlash artifact PUBLISH PLAN.

RELEASE-PREVIEW-PUBLISH-PLAN-001.

This plan PR verifies — without publishing anything — that the three
metadata-ready preview WebFlash build rows are ready to be published by the
firmware release workflow, and queues the actual run as
``RELEASE-PREVIEW-PUBLISH-RUN-001``. This guard locks the invariants the plan
asserts so they cannot silently regress:

  * the publish scope is exactly the three ``release_state:
    metadata-ready-unpublished`` preview rows
    (``Ceiling-POE-AirIQ-RoomIQ``, ``Ceiling-POE-RoomIQ``,
    ``Ceiling-POE-RoomIQ-LED``), all on the ``preview`` channel;
  * every preview publish row has a validated release-note draft
    (task item 6);
  * every preview publish row carries firmware-build compile evidence from
    hosted run ``26821900127`` (task item 6);
  * every preview publish row is selectable in the release / release-notes
    workflow pickers and via ``scripts/list_release_targets.py --validate``
    (task item 6);
  * each preview artifact name matches the build-row contract and round-trips
    through ``scripts/product_name_mapper.py`` (task item 6);
  * no forbidden target (stable Bathroom unless explicitly selected, TRIAC,
    or any fan manual-preview target) is in the preview publish scope, verified
    by replaying the release workflow's matrix-generation filter (task item 6);
  * the plan doc records, for each artifact, the config string, build row,
    wrapper path, release-note draft path, compile run, hidden / candidate /
    not-buyable posture, ``preview`` channel, not-stable / not-recommended /
    not-default posture, no hardware/compliance proof, the workflow selector,
    and the output filename (task items 3 / 4);
  * the plan queues ``RELEASE-PREVIEW-PUBLISH-RUN-001`` and states WebFlash
    import comes after upstream artifacts exist (task item 7); and
  * the hard guardrails hold — no ``manifest.json`` / ``firmware/sources.json``
    / ``.bin`` produced, launch SKU unchanged, and no fan / TRIAC ``.bin``
    appears in the publish set.

Uses Python's stdlib unittest (matching the no-pytest convention the other
validators in this repo use). Run with::

    python3 tests/test_preview_publish_plan.py
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path
from typing import Any, Dict, List

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"
SHOP_PATH = REPO_ROOT / "config" / "shop-commercial-source-of-truth.json"
PLAN_DOC = REPO_ROOT / "docs" / "release-preview-publish-plan.md"
DRAFT_DIR = REPO_ROOT / "docs" / "release-notes" / "preview"
VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate-webflash-release-notes.py"
MAPPER_PATH = REPO_ROOT / "scripts" / "product_name_mapper.py"
LIST_TARGETS_PATH = REPO_ROOT / "scripts" / "list_release_targets.py"
BUILD_RELEASE_WORKFLOW = (
    REPO_ROOT / ".github" / "workflows" / "firmware-build-release.yml"
)
RELEASE_NOTES_WORKFLOW = (
    REPO_ROOT / ".github" / "workflows" / "release-notes-draft.yml"
)

COMPILE_RUN_ID = 26821900127
PLAN_ID = "RELEASE-PREVIEW-PUBLISH-PLAN-001"
RUN_ID = "RELEASE-PREVIEW-PUBLISH-RUN-001"
LAUNCH_SKU = "S360-KIT-BATH-P"
VERSION = "1.0.0"
ALL_TARGETS_SENTINEL = "all-release-eligible"

# The three metadata-ready preview rows this plan publishes, by config string.
PUBLISH_CONFIGS = (
    "Ceiling-POE-AirIQ-RoomIQ",
    "Ceiling-POE-RoomIQ",
    "Ceiling-POE-RoomIQ-LED",
)

# The stable Bathroom baseline + already-published VentIQ LED preview are
# explicitly out of the publish set (the stable build is only built when
# `channel: stable` is selected; the VentIQ LED preview is already published).
STABLE_CONFIG = "Ceiling-POE-VentIQ-RoomIQ"
PUBLISHED_LED_PREVIEW_CONFIG = "Ceiling-POE-VentIQ-RoomIQ-LED"

# Forbidden tokens that must never appear as a preview publish artifact.
FORBIDDEN_ARTIFACT_TOKENS = ("FanTRIAC", "FanRelay", "FanPWM", "FanDAC", "TRIAC")
# Off-matrix configs that must be rejected by the release-target picker.
FORBIDDEN_TARGETS = (
    "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ",
    "Ceiling-POE-VentIQ-FanRelay-RoomIQ",
    "Ceiling-POE-FanPWM",
    "Ceiling-POE-FanDAC",
)

# Allow-list of every Sense360-*.bin token the plan doc may name: the three
# preview artifacts (the publish set) plus the stable Bathroom + published
# VentIQ LED preview cross-references (named by config string today, allowed by
# name if a future edit adds them).
ALLOWED_BIN_ARTIFACTS = {
    "Sense360-Ceiling-POE-AirIQ-RoomIQ-v1.0.0-preview.bin",
    "Sense360-Ceiling-POE-RoomIQ-v1.0.0-preview.bin",
    "Sense360-Ceiling-POE-RoomIQ-LED-v1.0.0-preview.bin",
    "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin",
    "Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin",
}

BIN_TOKEN_RE = re.compile(r"Sense360-[A-Za-z0-9.\-]+\.bin")


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


_VALIDATOR = _load_module("vw_release_notes_for_plan", VALIDATOR_PATH)
_MAPPER = _load_module("product_name_mapper_for_plan", MAPPER_PATH)
_LIST_TARGETS = _load_module("list_release_targets_for_plan", LIST_TARGETS_PATH)


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _builds() -> List[Dict[str, Any]]:
    return _load_json(BUILDS_PATH)["builds"]


def _by_cs() -> Dict[str, Dict[str, Any]]:
    return {b["config_string"]: b for b in _builds()}


def _metadata_ready_rows() -> List[Dict[str, Any]]:
    return [
        b
        for b in _builds()
        if b.get("release_state") == "metadata-ready-unpublished"
    ]


def _normalise(text: str) -> str:
    """Lowercase, drop blockquote markers / backticks / table pipes / markdown
    emphasis markers, collapse whitespace runs to single spaces so wrapped prose
    still matches regardless of bold / italic styling."""
    lines = [re.sub(r"^\s*>\s?", "", ln) for ln in text.splitlines()]
    joined = " ".join(lines).replace("`", "").replace("|", " ").replace("*", "")
    return re.sub(r"\s+", " ", joined).lower()


def _wrapper_stem(product_yaml: str) -> str:
    return Path(product_yaml).stem


def _matrix(version: str, channel: str, release_target: str, event: str) -> List[str]:
    """Replay the generate-matrix filter from firmware-build-release.yml.

    Mirrors the embedded Python in the workflow: filter
    config/webflash-builds.json by version + channel, and (only on a
    workflow_dispatch) optionally scope to a single release_target. The
    `all-release-eligible` sentinel and a non-dispatch event clear the scope.
    """
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
    """The publish scope is exactly the three metadata-ready preview rows."""

    def test_metadata_ready_rows_are_the_three_publish_configs(self) -> None:
        got = sorted(b["config_string"] for b in _metadata_ready_rows())
        self.assertEqual(got, sorted(PUBLISH_CONFIGS))

    def test_publish_rows_are_preview_channel_at_expected_version(self) -> None:
        by_cs = _by_cs()
        for cs in PUBLISH_CONFIGS:
            with self.subTest(config_string=cs):
                row = by_cs[cs]
                self.assertEqual(row["channel"], "preview")
                self.assertEqual(row["version"], VERSION)
                self.assertEqual(
                    row.get("release_state"), "metadata-ready-unpublished"
                )

    def test_stable_baseline_is_not_in_publish_scope(self) -> None:
        # The stable Bathroom build is channel=stable, never metadata-ready.
        row = _by_cs()[STABLE_CONFIG]
        self.assertEqual(row["channel"], "stable")
        self.assertNotEqual(row.get("release_state"), "metadata-ready-unpublished")


class ArtifactNameContractTests(unittest.TestCase):
    """Preview artifact names match the build-row contract + the mapper."""

    def test_artifact_names_follow_preview_contract(self) -> None:
        by_cs = _by_cs()
        for cs in PUBLISH_CONFIGS:
            with self.subTest(config_string=cs):
                expected = f"Sense360-{cs}-v{VERSION}-preview.bin"
                self.assertEqual(by_cs[cs]["artifact_name"], expected)
                self.assertTrue(expected.endswith("-preview.bin"))
                self.assertNotIn("-stable.bin", expected)

    def test_artifact_names_round_trip_through_mapper(self) -> None:
        by_cs = _by_cs()
        for cs in PUBLISH_CONFIGS:
            with self.subTest(config_string=cs):
                stem = _wrapper_stem(by_cs[cs]["product_yaml"])
                produced = _MAPPER.generate_webflash_filename(
                    stem, VERSION, "preview"
                )
                self.assertEqual(produced, by_cs[cs]["artifact_name"])

    def test_no_forbidden_token_in_publish_artifact_names(self) -> None:
        by_cs = _by_cs()
        for cs in PUBLISH_CONFIGS:
            name = by_cs[cs]["artifact_name"]
            for token in FORBIDDEN_ARTIFACT_TOKENS:
                with self.subTest(config_string=cs, token=token):
                    self.assertNotIn(token.lower(), name.lower())


class CompileEvidenceTests(unittest.TestCase):
    """Task item 6: every preview publish row carries compile evidence."""

    def test_each_row_cites_firmware_build_compile_evidence(self) -> None:
        by_cs = _by_cs()
        for cs in PUBLISH_CONFIGS:
            with self.subTest(config_string=cs):
                ev = by_cs[cs].get("compile_evidence")
                self.assertIsInstance(ev, dict)
                self.assertEqual(ev.get("run_id"), COMPILE_RUN_ID)
                self.assertEqual(ev.get("proof_class"), "firmware-build-only")
                self.assertEqual(ev.get("result"), "success")
                # The evidence must explicitly disclaim hardware/compliance.
                self.assertIn("hardware", ev.get("not_proof_of", []))
                self.assertIn("compliance", ev.get("not_proof_of", []))


class CommercialPostureTests(unittest.TestCase):
    """Task item 4: hidden / candidate / not buyable / not stable posture."""

    def test_rows_are_hidden_candidate_not_buyable_not_stable(self) -> None:
        by_cs = _by_cs()
        for cs in PUBLISH_CONFIGS:
            with self.subTest(config_string=cs):
                posture = by_cs[cs].get("commercial_posture", {})
                self.assertEqual(posture.get("visibility"), "hidden")
                self.assertEqual(posture.get("lifecycle"), "candidate")
                self.assertFalse(posture.get("buyable"))
                self.assertFalse(posture.get("recommended"))
                self.assertFalse(posture.get("customer_default"))
                self.assertFalse(posture.get("stable"))
                self.assertFalse(posture.get("release_one_required_config"))


class ReleaseNoteDraftCoverageTests(unittest.TestCase):
    """Task item 6: every preview publish row has a validated release-note draft."""

    def test_each_row_has_a_draft_that_validates_on_preview(self) -> None:
        for cs in PUBLISH_CONFIGS:
            with self.subTest(config_string=cs):
                draft = DRAFT_DIR / f"{cs.lower()}.md"
                self.assertTrue(draft.is_file(), f"missing draft for {cs}: {draft}")
                errors = _VALIDATOR.validate_body(
                    draft.read_text(encoding="utf-8"), channel="preview"
                )
                self.assertEqual(errors, [], f"{cs}: {errors}")


class WorkflowPickerTests(unittest.TestCase):
    """Task item 6: each publish config is selectable in both workflow pickers."""

    def test_build_release_release_target_contains_each_publish_config(self) -> None:
        inputs = _dispatch_inputs(BUILD_RELEASE_WORKFLOW)
        rt = inputs.get("release_target") or {}
        self.assertEqual(rt.get("type"), "choice")
        options = list(rt.get("options") or [])
        self.assertIn(ALL_TARGETS_SENTINEL, options)
        for cs in PUBLISH_CONFIGS:
            with self.subTest(config_string=cs):
                self.assertIn(cs, options)

    def test_release_notes_config_string_contains_each_publish_config(self) -> None:
        inputs = _dispatch_inputs(RELEASE_NOTES_WORKFLOW)
        cs_input = inputs.get("config_string") or {}
        self.assertEqual(cs_input.get("type"), "choice")
        options = list(cs_input.get("options") or [])
        for cs in PUBLISH_CONFIGS:
            with self.subTest(config_string=cs):
                self.assertIn(cs, options)

    def test_pickers_carry_no_fan_token(self) -> None:
        for wf in (BUILD_RELEASE_WORKFLOW, RELEASE_NOTES_WORKFLOW):
            inputs = _dispatch_inputs(wf)
            options: List[str] = []
            for key in ("release_target", "config_string"):
                options += list((inputs.get(key) or {}).get("options") or [])
            for opt in options:
                for token in ("FanRelay", "FanPWM", "FanDAC"):
                    with self.subTest(workflow=wf.name, option=opt, token=token):
                        self.assertNotIn(token.lower(), opt.lower())

    def test_list_release_targets_validates_each_publish_config(self) -> None:
        for cs in PUBLISH_CONFIGS:
            with self.subTest(config_string=cs):
                self.assertIsNone(
                    _LIST_TARGETS.validate_target(cs, BUILDS_PATH)
                )

    def test_list_release_targets_rejects_forbidden_targets(self) -> None:
        for bad in FORBIDDEN_TARGETS:
            with self.subTest(target=bad):
                self.assertIsNotNone(
                    _LIST_TARGETS.validate_target(bad, BUILDS_PATH),
                    f"{bad} must not be a selectable release target",
                )


class WorkflowMatrixScopeTests(unittest.TestCase):
    """Task item 6: replay the release workflow matrix filter for scope."""

    def test_scoped_dispatch_selects_exactly_one_publish_config(self) -> None:
        for cs in PUBLISH_CONFIGS:
            with self.subTest(config_string=cs):
                got = _matrix(VERSION, "preview", cs, "workflow_dispatch")
                self.assertEqual(got, [cs])

    def test_preview_run_never_includes_stable_bathroom(self) -> None:
        # An unscoped preview run (release event or all-release-eligible) must
        # not include the stable Bathroom build.
        for event, rt in (("release", ""), ("workflow_dispatch", ALL_TARGETS_SENTINEL)):
            with self.subTest(event=event):
                got = _matrix(VERSION, "preview", rt, event)
                self.assertNotIn(STABLE_CONFIG, got)
                for cs in PUBLISH_CONFIGS:
                    self.assertIn(cs, got)

    def test_stable_run_includes_only_the_stable_bathroom_build(self) -> None:
        got = _matrix(VERSION, "stable", "", "release")
        self.assertEqual(got, [STABLE_CONFIG])

    def test_no_fan_or_triac_token_in_any_build_row(self) -> None:
        for entry in _builds():
            cs = entry["config_string"]
            for token in FORBIDDEN_ARTIFACT_TOKENS:
                with self.subTest(config_string=cs, token=token):
                    self.assertNotIn(token.lower(), cs.lower())


class PublishPlanDocTests(unittest.TestCase):
    """Task items 3 / 4 / 7: the plan doc records the required per-artifact
    fields, queues the run, and honours the publish-set guardrails."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = PLAN_DOC.read_text(encoding="utf-8")
        cls.norm = _normalise(cls.text)
        cls.by_cs = _by_cs()

    def test_plan_doc_exists_and_is_self_identified(self) -> None:
        self.assertTrue(PLAN_DOC.is_file())
        self.assertIn(PLAN_ID, self.text)

    def test_plan_doc_records_every_required_field_per_artifact(self) -> None:
        for cs in PUBLISH_CONFIGS:
            row = self.by_cs[cs]
            artifact = row["artifact_name"]
            wrapper = row["product_yaml"]
            draft_rel = f"release-notes/preview/{cs.lower()}.md"
            with self.subTest(config_string=cs):
                # config string, build row config, expected output filename
                self.assertIn(cs, self.text)
                self.assertIn(artifact, self.text)
                # product YAML / wrapper path
                self.assertIn(wrapper, self.text)
                # release-note draft path
                self.assertIn(draft_rel, self.text)
                # compile evidence run
                self.assertIn(str(COMPILE_RUN_ID), self.text)
                # channel preview + not stable/recommended/default + posture
                norm = self.norm
                self.assertIn("preview", norm)
                self.assertIn("hidden", norm)
                self.assertIn("candidate", norm)
                self.assertIn("not buyable", norm)
                self.assertIn("not stable", norm)
                self.assertIn("not recommended", norm)
                self.assertIn("not a customer default", norm)

    def test_plan_doc_states_no_hardware_or_compliance_proof(self) -> None:
        self.assertIn("firmware-build proof only", self.norm)
        self.assertIn("no hardware / bench / compliance", self.norm)

    def test_plan_doc_records_workflow_selector_per_artifact(self) -> None:
        for cs in PUBLISH_CONFIGS:
            with self.subTest(config_string=cs):
                # The release_target selector value is the config string itself.
                self.assertIn(f"release_target: {cs}", self.text)

    def test_plan_doc_queues_the_run_and_defers_webflash_import(self) -> None:
        self.assertIn(RUN_ID, self.text)
        self.assertIn("webflash import comes after", self.norm)

    def test_plan_doc_keeps_launch_sku_unchanged(self) -> None:
        self.assertIn(LAUNCH_SKU, self.text)
        shop = _load_json(SHOP_PATH)["launch_product"]
        self.assertEqual(shop["shop_sku"], LAUNCH_SKU)

    def test_plan_doc_marks_triac_and_fans_out_of_scope(self) -> None:
        self.assertIn("triac", self.norm)
        self.assertIn("manual-preview", self.norm)
        self.assertIn("hw-005", self.norm)

    def test_plan_doc_bin_tokens_are_exactly_the_publish_set(self) -> None:
        tokens = set(BIN_TOKEN_RE.findall(self.text))
        # Every .bin named in the plan is on the allow-list ...
        self.assertTrue(
            tokens.issubset(ALLOWED_BIN_ARTIFACTS),
            f"plan names unexpected .bin artifact(s): "
            f"{sorted(tokens - ALLOWED_BIN_ARTIFACTS)}",
        )
        # ... and all three preview artifacts are present.
        for cs in PUBLISH_CONFIGS:
            self.assertIn(self.by_cs[cs]["artifact_name"], tokens)

    def test_plan_doc_names_no_fan_or_triac_bin_artifact(self) -> None:
        for token in BIN_TOKEN_RE.findall(self.text):
            for forbidden in FORBIDDEN_ARTIFACT_TOKENS:
                with self.subTest(artifact=token, token=forbidden):
                    self.assertNotIn(forbidden.lower(), token.lower())


class GuardrailTests(unittest.TestCase):
    """Hard guardrails: planning only — no publish side effects."""

    def test_no_manifest_or_sources_committed(self) -> None:
        self.assertFalse((REPO_ROOT / "manifest.json").exists())
        self.assertFalse((REPO_ROOT / "firmware" / "sources.json").exists())

    def test_no_bin_committed_anywhere_in_repo(self) -> None:
        bins = [
            p
            for p in REPO_ROOT.rglob("*.bin")
            if ".git" not in p.parts
        ]
        self.assertEqual(bins, [], f"no .bin may be committed; found {bins}")

    def test_catalog_publish_rows_stay_preview_not_production(self) -> None:
        catalog = {
            p["config_string"]: p
            for p in _load_json(CATALOG_PATH)["products"]
            if isinstance(p, dict) and "config_string" in p
        }
        for cs in PUBLISH_CONFIGS:
            with self.subTest(config_string=cs):
                entry = catalog[cs]
                self.assertEqual(entry["status"], "preview")
                self.assertEqual(entry["channel"], "preview")
                self.assertNotEqual(entry["status"], "production")


if __name__ == "__main__":
    unittest.main(verbosity=2)

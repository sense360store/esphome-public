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
    and
  * the hard guardrails hold — no ``manifest.json`` / ``firmware/sources.json``
    / ``.bin`` produced, and no fan / TRIAC token appears in the publish set.

The plan record doc (``docs/release-preview-publish-plan.md``) was archived
under DOCS-DISPOSITION-001 (see ``docs/archive-index.md``); the tests that
pinned that doc's prose were retired with it. The live-ledger / workflow
guards above remain.

Uses Python's stdlib unittest (matching the no-pytest convention the other
validators in this repo use). Run with::

    python3 tests/test_preview_publish_plan.py
"""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path
from typing import Any, Dict, List

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"
DRAFT_DIR = REPO_ROOT / "docs" / "release-notes" / "preview"
VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate-webflash-release-notes.py"
MAPPER_PATH = REPO_ROOT / "scripts" / "product_name_mapper.py"
LIST_TARGETS_PATH = REPO_ROOT / "scripts" / "list_release_targets.py"
RELEASE_NOTES_WORKFLOW = (
    REPO_ROOT / ".github" / "workflows" / "release-notes-draft.yml"
)

COMPILE_RUN_ID = 26821900127
VERSION = "1.0.0"

# The three metadata-ready preview rows this plan published, by config string.
# HISTORICAL: the plan was executed (run 26847702410, release v1.0.0-preview).
# STABLE-PROMOTION-RECONCILE-001 has since promoted two of the three to the
# stable channel (Ceiling-POE-RoomIQ v1.0.5 on 2026-06-08,
# Ceiling-POE-AirIQ-RoomIQ v1.0.6 on 2026-06-09, owner-waiver promotions), so
# live-ledger assertions below distinguish the promoted rows from the one
# still on the preview channel.
# CI-PIPELINE-CLARITY-001 P4a DE-LISTED Ceiling-POE-RoomIQ-LED (never built or
# served): its build row was removed from config/webflash-builds.json, so it is
# no longer a publish config. The two room bundles that remain in the ledger
# were both promoted to stable.
PUBLISH_CONFIGS = (
    "Ceiling-POE-AirIQ-RoomIQ",
    "Ceiling-POE-RoomIQ",
)
PROMOTED_CONFIGS = (
    "Ceiling-POE-AirIQ-RoomIQ",
    "Ceiling-POE-RoomIQ",
)
# HW-RELEASE-001 (docs/hw-release-001.md, owner declaration) re-listed the
# LED room bundle and added the six FanPWM / FanDAC preview rows, all
# metadata-ready on the PREVIEW channel. The FanTRIAC experimental self-build
# mains build (TRIAC-COMMISSIONING-001) plus the two owner-declared FanRelay
# room bundles are metadata-ready on the EXPERIMENTAL channel, tracked
# separately.
STILL_PREVIEW_CONFIGS: tuple[str, ...] = (
    "Ceiling-POE-RoomIQ-LED",
    "Ceiling-POE-FanPWM",
    "Ceiling-POE-AirIQ-FanPWM-RoomIQ",
    "Ceiling-POE-VentIQ-FanPWM-RoomIQ",
    "Ceiling-POE-FanDAC",
    "Ceiling-POE-AirIQ-FanDAC-RoomIQ",
    "Ceiling-POE-VentIQ-FanDAC-RoomIQ",
)
EXPERIMENTAL_METADATA_READY_CONFIGS = (
    "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ",
    "Ceiling-POE-AirIQ-FanRelay-RoomIQ",
    "Ceiling-POE-VentIQ-FanRelay-RoomIQ",
)

# The stable Bathroom baseline + already-published VentIQ LED preview are
# explicitly out of the publish set (the stable build is only built when
# `channel: stable` is selected; the VentIQ LED preview is already published).
STABLE_CONFIG = "Ceiling-POE-VentIQ-RoomIQ"
PUBLISHED_LED_PREVIEW_CONFIG = "Ceiling-POE-VentIQ-RoomIQ-LED"

# Tokens that must never appear in the HISTORICAL v1.0.0-preview publish
# set's artifact names (PUBLISH_CONFIGS above) — that publish predates
# HW-RELEASE-001 and carried no fan/TRIAC artifact.
FORBIDDEN_ARTIFACT_TOKENS = ("FanTRIAC", "FanRelay", "FanPWM", "FanDAC", "TRIAC")
# Off-matrix configs that must be rejected by the release-target picker.
# (FanTRIAC was admitted by TRIAC-COMMISSIONING-001 on the experimental
# channel; HW-RELEASE-001 then admitted the FanPWM / FanDAC configs on
# preview and the FanRelay room bundles on experimental, so those are now
# accepted. What stays rejected is anything without a build row.)
FORBIDDEN_TARGETS = (
    "Ceiling-USB-FanPWM",
    "Ceiling-POE-FanRelay",
    "Not-A-Real-Config",
)


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


def _wrapper_stem(product_yaml: str) -> str:
    return Path(product_yaml).stem


def _matrix(version: str, channel: str) -> List[str]:
    """Replay the generate-matrix filter from firmware-build-release.yml.

    Mirrors the embedded Python in the workflow: filter
    config/webflash-builds.json by the version + channel derived from the
    release tag. The workflow is release-event only (it has no
    workflow_dispatch / scoped release_target lane), so version + channel
    is the entire filter.
    """
    rows: List[str] = []
    for entry in _builds():
        if entry.get("version") != version:
            continue
        if entry.get("channel") != channel:
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
    """The publish scope was the three metadata-ready preview rows; after the
    promotions only the LED room bundle is still metadata-ready."""

    def test_metadata_ready_rows_are_the_unpromoted_publish_configs(self) -> None:
        # The unpromoted preview LED room bundle plus the FanTRIAC experimental
        # self-build mains build (TRIAC-COMMISSIONING-001, experimental channel).
        got = sorted(b["config_string"] for b in _metadata_ready_rows())
        self.assertEqual(
            got,
            sorted(STILL_PREVIEW_CONFIGS + EXPERIMENTAL_METADATA_READY_CONFIGS),
        )

    def test_publish_rows_match_their_promotion_state(self) -> None:
        by_cs = _by_cs()
        for cs in STILL_PREVIEW_CONFIGS:
            with self.subTest(config_string=cs):
                row = by_cs[cs]
                self.assertEqual(row["channel"], "preview")
                self.assertEqual(row["version"], VERSION)
                self.assertEqual(
                    row.get("release_state"), "metadata-ready-unpublished"
                )
        for cs in PROMOTED_CONFIGS:
            with self.subTest(config_string=cs):
                row = by_cs[cs]
                self.assertEqual(row["channel"], "stable")
                self.assertNotIn("release_state", row)
                self.assertTrue(row["artifact_name"].endswith("-stable.bin"))

    def test_stable_baseline_is_not_in_publish_scope(self) -> None:
        # The stable Bathroom build is channel=stable, never metadata-ready.
        row = _by_cs()[STABLE_CONFIG]
        self.assertEqual(row["channel"], "stable")
        self.assertNotEqual(row.get("release_state"), "metadata-ready-unpublished")


class ArtifactNameContractTests(unittest.TestCase):
    """Artifact names match the build-row contract + the mapper (the preview
    contract for the unpromoted row; the stable contract for the promoted)."""

    def test_artifact_names_follow_channel_contract(self) -> None:
        by_cs = _by_cs()
        for cs in STILL_PREVIEW_CONFIGS:
            with self.subTest(config_string=cs):
                expected = f"Sense360-{cs}-v{VERSION}-preview.bin"
                self.assertEqual(by_cs[cs]["artifact_name"], expected)
        for cs in PROMOTED_CONFIGS:
            with self.subTest(config_string=cs):
                row = by_cs[cs]
                expected = f"Sense360-{cs}-v{row['version']}-stable.bin"
                self.assertEqual(row["artifact_name"], expected)

    def test_artifact_names_round_trip_through_mapper(self) -> None:
        by_cs = _by_cs()
        for cs in PUBLISH_CONFIGS:
            with self.subTest(config_string=cs):
                row = by_cs[cs]
                stem = _wrapper_stem(row["product_yaml"])
                produced = _MAPPER.generate_webflash_filename(
                    stem, row["version"], row["channel"]
                )
                self.assertEqual(produced, row["artifact_name"])

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

    def test_rows_are_hidden_candidate_not_buyable(self) -> None:
        # posture.stable mirrors the channel after the promotions: true for
        # the two promoted rows, false for the unpromoted LED room bundle.
        # Everything else (hidden / candidate / not buyable / not recommended /
        # not default / not required-config) is unchanged by promotion.
        by_cs = _by_cs()
        for cs in PUBLISH_CONFIGS:
            with self.subTest(config_string=cs):
                posture = by_cs[cs].get("commercial_posture", {})
                self.assertEqual(posture.get("visibility"), "hidden")
                self.assertEqual(posture.get("lifecycle"), "candidate")
                self.assertFalse(posture.get("buyable"))
                self.assertFalse(posture.get("recommended"))
                self.assertFalse(posture.get("customer_default"))
                self.assertEqual(posture.get("stable"), cs in PROMOTED_CONFIGS)
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
    """Task item 6: each publish config is selectable in the release-notes
    picker and accepted by the release-target validator.

    firmware-build-release.yml no longer has a workflow_dispatch
    release_target picker (it fires only on the published release event),
    so the operator picker that remains is release-notes-draft.yml's
    config_string input.
    """

    def test_release_notes_config_string_contains_each_publish_config(self) -> None:
        inputs = _dispatch_inputs(RELEASE_NOTES_WORKFLOW)
        cs_input = inputs.get("config_string") or {}
        self.assertEqual(cs_input.get("type"), "choice")
        options = list(cs_input.get("options") or [])
        for cs in PUBLISH_CONFIGS:
            with self.subTest(config_string=cs):
                self.assertIn(cs, options)

    def test_release_notes_picker_fan_options_never_stable(self) -> None:
        # HW-RELEASE-001: fan targets are pickable, but every fan option must
        # map to a non-stable build row (FanRelay: experimental; FanPWM /
        # FanDAC: preview). Fan configs are NEVER stable.
        inputs = _dispatch_inputs(RELEASE_NOTES_WORKFLOW)
        options = list((inputs.get("config_string") or {}).get("options") or [])
        by_cs = _by_cs()
        for opt in options:
            if not any(
                token.lower() in opt.lower()
                for token in ("FanRelay", "FanPWM", "FanDAC")
            ):
                continue
            with self.subTest(option=opt):
                self.assertIn(opt, by_cs)
                channel = by_cs[opt]["channel"]
                self.assertNotEqual(channel, "stable")
                if "fanrelay" in opt.lower():
                    self.assertEqual(channel, "experimental")
                else:
                    self.assertEqual(channel, "preview")

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

    def test_preview_run_never_includes_stable_bathroom(self) -> None:
        # A preview release run must not include the stable Bathroom build,
        # and (post-promotion) no longer includes the two promoted rows.
        got = _matrix(VERSION, "preview")
        self.assertNotIn(STABLE_CONFIG, got)
        for cs in STILL_PREVIEW_CONFIGS:
            self.assertIn(cs, got)
        for cs in PROMOTED_CONFIGS:
            self.assertNotIn(cs, got)

    def test_each_stable_version_builds_exactly_one_row(self) -> None:
        # Stable rows carry distinct versions (the bump/promote flow moves one
        # config at a time), so a stable release run at a given version builds
        # exactly that config — never a second stable row by accident.
        for entry in _builds():
            if entry.get("channel") != "stable":
                continue
            with self.subTest(config_string=entry["config_string"]):
                got = _matrix(entry["version"], "stable")
                self.assertEqual(got, [entry["config_string"]])

    def test_fan_and_triac_build_rows_never_stable(self) -> None:
        # HW-RELEASE-001 revised the fan-token guardrail to channel teeth:
        # FanTRIAC / FanRelay rows only on 'experimental', FanPWM / FanDAC
        # rows only on 'preview'. Fan / TRIAC rows are NEVER stable.
        for entry in _builds():
            cs = entry["config_string"]
            tokens = cs.split("-")
            if "FanTRIAC" in tokens or "FanRelay" in tokens:
                with self.subTest(config_string=cs):
                    self.assertEqual(entry.get("channel"), "experimental")
                continue
            if "FanPWM" in tokens or "FanDAC" in tokens:
                with self.subTest(config_string=cs):
                    self.assertEqual(entry.get("channel"), "preview")
                continue
            for token in FORBIDDEN_ARTIFACT_TOKENS:
                with self.subTest(config_string=cs, token=token):
                    self.assertNotIn(token.lower(), cs.lower())


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

    def test_catalog_publish_rows_match_promotion_state(self) -> None:
        # The plan itself promoted nothing. STABLE-PROMOTION-RECONCILE-001:
        # Kitchen and Bedroom were later promoted to production/stable by
        # their own owner-waiver promotion PRs; the unpromoted LED room
        # bundle stays preview.
        catalog = {
            p["config_string"]: p
            for p in _load_json(CATALOG_PATH)["products"]
            if isinstance(p, dict) and "config_string" in p
        }
        for cs in STILL_PREVIEW_CONFIGS:
            with self.subTest(config_string=cs):
                entry = catalog[cs]
                self.assertEqual(entry["status"], "preview")
                self.assertEqual(entry["channel"], "preview")
        for cs in PROMOTED_CONFIGS:
            with self.subTest(config_string=cs):
                entry = catalog[cs]
                self.assertEqual(entry["status"], "production")
                self.assertEqual(entry["channel"], "stable")


if __name__ == "__main__":
    unittest.main(verbosity=2)

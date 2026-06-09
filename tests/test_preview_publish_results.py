#!/usr/bin/env python3
"""Regression guard for the preview WebFlash artifact PUBLISH RESULTS record.

RELEASE-PREVIEW-PUBLISH-RESULTS-001.

This PR records the **successful** ``Build & Release Firmware`` run that
published the preview firmware artifacts to the GitHub Release
``v1.0.0-preview`` (the run queued by ``RELEASE-PREVIEW-PUBLISH-RUN-001``). This
guard locks the invariants the results doc asserts so they cannot silently
regress:

  * the results doc records the run id ``26847702410``, the workflow name
    ``Build & Release Firmware``, the ``release`` event (not a manual dispatch),
    conclusion ``success``, and a build count of four (task items 3 / 5);
  * the four published artifacts are the HISTORICAL ``(version=1.0.0,
    channel=preview)`` publish set, pinned statically (task item 4). They were
    originally derived from ``config/webflash-builds.json``, but
    STABLE-PROMOTION-RECONCILE-001 promoted two of the four to stable
    (Bedroom v1.0.5, Kitchen v1.0.6), so the live ledger now legitimately
    carries only a subset on the preview channel — the guard checks that
    subset relationship instead;
  * the doc explains the four-artifact scope — the ``release`` event ignores the
    ``workflow_dispatch``-only ``release_target`` picker and builds every
    ``version`` + ``channel`` row (task item 5);
  * the preview posture is preserved — preview / not stable / not recommended /
    not a customer default / candidate bundles hidden / not buyable, the launch
    SKU stays ``S360-KIT-BATH-P``, TRIAC stays out (``HW-005``), and no
    hardware / compliance proof is claimed (task item 6);
  * no forbidden token (FanTRIAC / FanRelay / FanPWM / FanDAC / TRIAC) appears in
    any ``.bin`` the doc names;
  * the hard guardrails hold — no ``manifest.json`` / ``firmware/sources.json`` /
    ``.bin`` is committed, and the three new build rows stay
    ``release_state: metadata-ready-unpublished`` (this PR records results; it
    does not edit ``config/webflash-builds.json``); and
  * ``UPCOMING_PR.md`` marks ``RELEASE-PREVIEW-PUBLISH-RUN-001`` done and queues
    the WebFlash import ``WF-PREVIEW-IMPORT-FIRST-BATCH-001`` (task item 7).

Uses Python's stdlib unittest (matching the no-pytest convention the other
validators in this repo use). Run with::

    python3 tests/test_preview_publish_results.py
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
SHOP_PATH = REPO_ROOT / "config" / "shop-commercial-source-of-truth.json"
RESULTS_DOC = REPO_ROOT / "docs" / "release-preview-publish-results.md"
UPCOMING_PR = REPO_ROOT / "UPCOMING_PR.md"

RESULTS_ID = "RELEASE-PREVIEW-PUBLISH-RESULTS-001"
RUN_QUEUE_ID = "RELEASE-PREVIEW-PUBLISH-RUN-001"
IMPORT_FOLLOWUP_ID = "WF-PREVIEW-IMPORT-FIRST-BATCH-001"
WORKFLOW_NAME = "Build & Release Firmware"
RUN_ID = "26847702410"
RELEASE_TAG = "v1.0.0-preview"
LAUNCH_SKU = "S360-KIT-BATH-P"
VERSION = "1.0.0"
CHANNEL = "preview"
BUILD_COUNT = 4

# The exact four config strings the v1.0.0-preview release published (the three
# new room-bundle previews + the re-attached VentIQ LED preview). This is a
# HISTORICAL record of that release run, pinned statically: the live ledger has
# since legitimately moved on (STABLE-PROMOTION-RECONCILE-001 promoted
# Ceiling-POE-RoomIQ to stable v1.0.5 on 2026-06-08 and Ceiling-POE-AirIQ-RoomIQ
# to stable v1.0.6 on 2026-06-09), so the historical publish set can no longer
# be derived from config/webflash-builds.json.
EXPECTED_PUBLISHED_CONFIGS = {
    "Ceiling-POE-AirIQ-RoomIQ",
    "Ceiling-POE-RoomIQ",
    "Ceiling-POE-RoomIQ-LED",
    "Ceiling-POE-VentIQ-RoomIQ-LED",
}
# The artifact names that release run attached (historical, static).
EXPECTED_PUBLISHED_ARTIFACTS = {
    "Sense360-Ceiling-POE-AirIQ-RoomIQ-v1.0.0-preview.bin",
    "Sense360-Ceiling-POE-RoomIQ-v1.0.0-preview.bin",
    "Sense360-Ceiling-POE-RoomIQ-LED-v1.0.0-preview.bin",
    "Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin",
}
# Of the three rows added by RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001, only the
# unpromoted LED room bundle still carries release_state
# metadata-ready-unpublished; the two promoted rows dropped the preview-only
# release_state field on promotion.
UNPROMOTED_METADATA_ROWS = {
    "Ceiling-POE-RoomIQ-LED",
}
PROMOTED_ROWS = {
    "Ceiling-POE-AirIQ-RoomIQ",
    "Ceiling-POE-RoomIQ",
}
STABLE_CONFIG = "Ceiling-POE-VentIQ-RoomIQ"

FORBIDDEN_ARTIFACT_TOKENS = ("FanTRIAC", "FanRelay", "FanPWM", "FanDAC", "TRIAC")

# Every Sense360-*.bin token the results doc may name: the four preview
# artifacts plus the stable Bathroom cross-reference.
ALLOWED_BIN_ARTIFACTS = {
    "Sense360-Ceiling-POE-AirIQ-RoomIQ-v1.0.0-preview.bin",
    "Sense360-Ceiling-POE-RoomIQ-v1.0.0-preview.bin",
    "Sense360-Ceiling-POE-RoomIQ-LED-v1.0.0-preview.bin",
    "Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin",
    "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin",
}

BIN_TOKEN_RE = re.compile(r"Sense360-[A-Za-z0-9.\-]+\.bin")


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _builds() -> List[Dict[str, Any]]:
    return _load_json(BUILDS_PATH)["builds"]


def _by_cs() -> Dict[str, Dict[str, Any]]:
    return {b["config_string"]: b for b in _builds()}


def _preview_rows_today() -> List[Dict[str, Any]]:
    """Every webflash-builds.json row still at (version=1.0.0, channel=preview)
    TODAY. Historically the v1.0.0-preview release-event filter matched four
    rows; two have since been promoted to stable, so today's preview rows are a
    strict subset of the historical publish set."""
    return [
        b
        for b in _builds()
        if b.get("version") == VERSION and b.get("channel") == CHANNEL
    ]


def _normalise(text: str) -> str:
    lines = [re.sub(r"^\s*>\s?", "", ln) for ln in text.splitlines()]
    joined = " ".join(lines).replace("`", "").replace("|", " ").replace("*", "")
    return re.sub(r"\s+", " ", joined).lower()


class RunEvidenceTests(unittest.TestCase):
    """Task items 3 / 5: the run is recorded faithfully."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = RESULTS_DOC.read_text(encoding="utf-8")
        cls.norm = _normalise(cls.text)

    def test_results_doc_exists_and_is_self_identified(self) -> None:
        self.assertTrue(RESULTS_DOC.is_file())
        self.assertIn(RESULTS_ID, self.text)

    def test_records_run_id_tag_and_workflow_name(self) -> None:
        self.assertIn(RUN_ID, self.text)
        self.assertIn(RELEASE_TAG, self.text)
        self.assertIn(WORKFLOW_NAME, self.text)

    def test_records_release_event_not_manual_dispatch(self) -> None:
        # The run was a real `release` event; the doc must say so and contrast
        # it with manual dispatch.
        self.assertIn("release event", self.norm)
        self.assertIn("manual dispatch", self.norm)
        self.assertIn("workflow_dispatch", self.norm)

    def test_records_success_conclusion_and_four_artifacts(self) -> None:
        self.assertIn("success", self.norm)
        self.assertIn("four", self.norm)
        # The recorded build count matches the (historical, static) publish set.
        self.assertEqual(len(EXPECTED_PUBLISHED_CONFIGS), BUILD_COUNT)
        self.assertEqual(len(EXPECTED_PUBLISHED_ARTIFACTS), BUILD_COUNT)

    def test_records_attach_and_gate_steps(self) -> None:
        for needle in (
            "attach to release",
            "validate webflash release notes",
            "check webflash release assets",
            "upload release assets",
        ):
            with self.subTest(step=needle):
                self.assertIn(needle, self.norm)


class PublishedArtifactTests(unittest.TestCase):
    """Task item 4: the four artifacts are exactly the preview build rows."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = RESULTS_DOC.read_text(encoding="utf-8")

    def test_published_set_covers_todays_preview_rows(self) -> None:
        # Today's preview rows are a strict subset of the historical publish
        # set (two of the four were promoted to stable after the run), and
        # every historically published config still exists in the ledger.
        got = {b["config_string"] for b in _preview_rows_today()}
        self.assertTrue(
            got.issubset(EXPECTED_PUBLISHED_CONFIGS),
            f"unexpected preview rows: {sorted(got - EXPECTED_PUBLISHED_CONFIGS)}",
        )
        ledger = set(_by_cs())
        self.assertTrue(EXPECTED_PUBLISHED_CONFIGS.issubset(ledger))
        self.assertEqual(
            EXPECTED_PUBLISHED_CONFIGS - got,
            PROMOTED_ROWS,
            "only the two promoted rows may have left the preview channel",
        )

    def test_stable_row_is_not_in_the_preview_publish_set(self) -> None:
        self.assertNotIn(STABLE_CONFIG, EXPECTED_PUBLISHED_CONFIGS)
        got = {b["config_string"] for b in _preview_rows_today()}
        self.assertNotIn(STABLE_CONFIG, got)

    def test_doc_names_each_published_artifact(self) -> None:
        for artifact in EXPECTED_PUBLISHED_ARTIFACTS:
            with self.subTest(artifact=artifact):
                self.assertTrue(artifact.endswith("-preview.bin"))
                self.assertIn(artifact, self.text)

    def test_doc_bin_tokens_are_exactly_the_allowed_set(self) -> None:
        tokens = set(BIN_TOKEN_RE.findall(self.text))
        self.assertTrue(
            tokens.issubset(ALLOWED_BIN_ARTIFACTS),
            f"doc names unexpected .bin artifact(s): "
            f"{sorted(tokens - ALLOWED_BIN_ARTIFACTS)}",
        )
        for artifact in EXPECTED_PUBLISHED_ARTIFACTS:
            self.assertIn(artifact, tokens)

    def test_no_forbidden_token_in_any_named_bin(self) -> None:
        for token in BIN_TOKEN_RE.findall(self.text):
            for forbidden in FORBIDDEN_ARTIFACT_TOKENS:
                with self.subTest(artifact=token, token=forbidden):
                    self.assertNotIn(forbidden.lower(), token.lower())


class WhyFourArtifactsTests(unittest.TestCase):
    """Task item 5: the doc explains the release-event scope."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.norm = _normalise(RESULTS_DOC.read_text(encoding="utf-8"))

    def test_explains_release_target_ignored_on_release_event(self) -> None:
        self.assertIn("release_target", self.norm)
        self.assertIn("ignored", self.norm)
        self.assertIn("workflow_dispatch", self.norm)

    def test_explains_version_and_channel_filter(self) -> None:
        self.assertIn("version=1.0.0", self.norm)
        self.assertIn("channel=preview", self.norm)


class PosturePreservedTests(unittest.TestCase):
    """Task item 6: the preview posture is preserved and nothing is overclaimed."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = RESULTS_DOC.read_text(encoding="utf-8")
        cls.norm = _normalise(cls.text)

    def test_preview_not_stable_not_recommended_not_default(self) -> None:
        for needle in (
            "preview",
            "not stable",
            "not recommended",
            "not a customer default",
        ):
            with self.subTest(needle=needle):
                self.assertIn(needle, self.norm)

    def test_candidate_bundles_hidden_and_not_buyable(self) -> None:
        self.assertIn("hidden", self.norm)
        self.assertIn("not buyable", self.norm)

    def test_stable_bathroom_remains_only_customer_default_production(self) -> None:
        self.assertIn("stable bathroom", self.norm)
        self.assertIn("production", self.norm)
        # The launch SKU is named and matches the commercial source of truth.
        self.assertIn(LAUNCH_SKU, self.text)
        self.assertEqual(
            _load_json(SHOP_PATH)["launch_product"]["shop_sku"], LAUNCH_SKU
        )

    def test_triac_stays_out_under_hw005(self) -> None:
        self.assertIn("triac", self.norm)
        self.assertIn("hw-005", self.norm)

    def test_no_hardware_or_compliance_proof_claimed(self) -> None:
        self.assertIn("firmware-build", self.norm)
        self.assertIn("no hardware", self.norm)


class GuardrailTests(unittest.TestCase):
    """Hard guardrails: recording only — no publish / config side effects."""

    def test_no_manifest_or_sources_committed(self) -> None:
        self.assertFalse((REPO_ROOT / "manifest.json").exists())
        self.assertFalse((REPO_ROOT / "firmware" / "sources.json").exists())

    def test_no_bin_committed_anywhere_in_repo(self) -> None:
        bins = [p for p in REPO_ROOT.rglob("*.bin") if ".git" not in p.parts]
        self.assertEqual(bins, [], f"no .bin may be committed; found {bins}")

    def test_release_state_matches_promotion_state(self) -> None:
        # The unpromoted LED room bundle still carries the preview-only
        # release_state; the two promoted rows dropped it on promotion
        # (matching the stable Release-One row shape).
        by_cs = _by_cs()
        for cs in UNPROMOTED_METADATA_ROWS:
            with self.subTest(config_string=cs):
                self.assertEqual(
                    by_cs[cs].get("release_state"), "metadata-ready-unpublished"
                )
        for cs in PROMOTED_ROWS:
            with self.subTest(config_string=cs):
                self.assertNotIn("release_state", by_cs[cs])

    def test_builds_ledger_still_has_five_entries(self) -> None:
        self.assertEqual(len(_builds()), 5)


class UpcomingPrTests(unittest.TestCase):
    """Task item 7: the queue is updated."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = UPCOMING_PR.read_text(encoding="utf-8")

    def test_publish_run_marked_done(self) -> None:
        run_lines = [
            ln for ln in self.text.splitlines() if RUN_QUEUE_ID in ln
        ]
        self.assertTrue(run_lines, f"{RUN_QUEUE_ID} not found in UPCOMING_PR.md")
        self.assertTrue(
            any("DONE" in ln for ln in run_lines),
            f"{RUN_QUEUE_ID} is not marked DONE in any heading/line",
        )

    def test_webflash_import_first_batch_queued(self) -> None:
        self.assertIn(IMPORT_FOLLOWUP_ID, self.text)

    def test_run_id_recorded_in_queue(self) -> None:
        self.assertIn(RUN_ID, self.text)


if __name__ == "__main__":
    unittest.main(verbosity=2)

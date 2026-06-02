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
  * the four published artifacts are EXACTLY the ``(version=1.0.0,
    channel=preview)`` rows in ``config/webflash-builds.json`` (derived, not
    hardcoded), each a ``-preview.bin`` (task item 4);
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
# new room-bundle previews + the re-attached VentIQ LED preview). The test also
# derives this set from config/webflash-builds.json so the doc cannot drift.
EXPECTED_PUBLISHED_CONFIGS = {
    "Ceiling-POE-AirIQ-RoomIQ",
    "Ceiling-POE-RoomIQ",
    "Ceiling-POE-RoomIQ-LED",
    "Ceiling-POE-VentIQ-RoomIQ-LED",
}
# The three rows added by RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001 that must stay
# metadata-ready-unpublished (this PR records results; it edits no build row).
NEW_METADATA_ROWS = {
    "Ceiling-POE-AirIQ-RoomIQ",
    "Ceiling-POE-RoomIQ",
    "Ceiling-POE-RoomIQ-LED",
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


def _published_rows() -> List[Dict[str, Any]]:
    """Replay the release-event matrix filter: every webflash-builds.json row at
    (version=1.0.0, channel=preview). release_target is ignored on a release
    event, so the scope is purely the version + channel match."""
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
        # The recorded build count matches the derived matrix size.
        self.assertEqual(len(_published_rows()), BUILD_COUNT)

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

    def test_published_set_is_the_four_preview_rows(self) -> None:
        got = {b["config_string"] for b in _published_rows()}
        self.assertEqual(got, EXPECTED_PUBLISHED_CONFIGS)

    def test_stable_row_is_not_in_the_preview_publish_set(self) -> None:
        got = {b["config_string"] for b in _published_rows()}
        self.assertNotIn(STABLE_CONFIG, got)

    def test_doc_names_each_published_artifact(self) -> None:
        by_cs = _by_cs()
        for cs in EXPECTED_PUBLISHED_CONFIGS:
            with self.subTest(config_string=cs):
                artifact = by_cs[cs]["artifact_name"]
                self.assertTrue(artifact.endswith("-preview.bin"))
                self.assertIn(artifact, self.text)

    def test_doc_bin_tokens_are_exactly_the_allowed_set(self) -> None:
        tokens = set(BIN_TOKEN_RE.findall(self.text))
        self.assertTrue(
            tokens.issubset(ALLOWED_BIN_ARTIFACTS),
            f"doc names unexpected .bin artifact(s): "
            f"{sorted(tokens - ALLOWED_BIN_ARTIFACTS)}",
        )
        by_cs = _by_cs()
        for cs in EXPECTED_PUBLISHED_CONFIGS:
            self.assertIn(by_cs[cs]["artifact_name"], tokens)

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

    def test_new_build_rows_stay_metadata_ready_unpublished(self) -> None:
        by_cs = _by_cs()
        for cs in NEW_METADATA_ROWS:
            with self.subTest(config_string=cs):
                self.assertEqual(
                    by_cs[cs].get("release_state"), "metadata-ready-unpublished"
                )

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

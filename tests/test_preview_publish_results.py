#!/usr/bin/env python3
"""Regression guard for the preview WebFlash artifact PUBLISH RESULTS record.

RELEASE-PREVIEW-PUBLISH-RESULTS-001.

This PR records the **successful** ``Build & Release Firmware`` run that
published the preview firmware artifacts to the GitHub Release
``v1.0.0-preview`` (the run queued by ``RELEASE-PREVIEW-PUBLISH-RUN-001``). This
guard locks the invariants the results doc asserts so they cannot silently
regress:

  * the four published artifacts are the HISTORICAL ``(version=1.0.0,
    channel=preview)`` publish set, pinned statically (task item 4). They were
    originally derived from ``config/webflash-builds.json``, but
    STABLE-PROMOTION-RECONCILE-001 promoted two of the four to stable
    (Bedroom v1.0.5, Kitchen v1.0.6), so the live ledger now legitimately
    carries only a subset on the preview channel — the guard checks that
    subset relationship instead;
  * the hard guardrails hold — no ``manifest.json`` / ``firmware/sources.json`` /
    ``.bin`` is committed, and the unpromoted build row stays
    ``release_state: metadata-ready-unpublished``.

The results record doc (``docs/release-preview-publish-results.md``) was
archived under DOCS-DISPOSITION-001 (see ``docs/archive-index.md``); the tests
that pinned that doc's prose were retired with it. ``UPCOMING_PR.md`` was
retired at DOCS-DISPOSITION-001 Step 7, and the queue-bookkeeping guards
(``RELEASE-PREVIEW-PUBLISH-RUN-001`` marked DONE, run ``26847702410``
recorded, ``WF-PREVIEW-IMPORT-FIRST-BATCH-001`` queued) were retired with it —
the queue text remains recoverable from the SHA indexed in
``docs/archive-index.md``. The live-ledger guards above remain.

Uses Python's stdlib unittest (matching the no-pytest convention the other
validators in this repo use). Run with::

    python3 tests/test_preview_publish_results.py
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"

VERSION = "1.0.0"
CHANNEL = "preview"

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
# Rows that left the historical (version=1.0.0, channel=preview) set by being
# re-released on the preview channel at a newer version (not promoted):
# REBUILD-CLEAN-CREDENTIALS-001 re-cut the VentIQ LED preview as v1.0.1
# (prerelease v1.0.1-led-preview, 2026-07-06).
REROLLED_PREVIEW_ROWS = {
    "Ceiling-POE-VentIQ-RoomIQ-LED",
}
STABLE_CONFIG = "Ceiling-POE-VentIQ-RoomIQ"


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


class PublishedArtifactTests(unittest.TestCase):
    """Task item 4: the historical publish set still reconciles with the
    live ledger (today's preview rows are a strict subset of it)."""

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
            PROMOTED_ROWS | REROLLED_PREVIEW_ROWS,
            "only the two promoted rows (stable) and the re-released VentIQ "
            "LED preview (v1.0.1) may have left the historical v1.0.0 "
            "preview set",
        )

    def test_stable_row_is_not_in_the_preview_publish_set(self) -> None:
        self.assertNotIn(STABLE_CONFIG, EXPECTED_PUBLISHED_CONFIGS)
        got = {b["config_string"] for b in _preview_rows_today()}
        self.assertNotIn(STABLE_CONFIG, got)


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

    def test_builds_ledger_has_six_entries(self) -> None:
        # Five customer (stable / preview) builds plus the experimental
        # self-build mains FanTRIAC build added by TRIAC-COMMISSIONING-001.
        self.assertEqual(len(_builds()), 6)


if __name__ == "__main__":
    unittest.main(verbosity=2)

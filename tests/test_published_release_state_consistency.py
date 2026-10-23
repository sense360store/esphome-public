#!/usr/bin/env python3
"""Contract: a build row's ``release_state`` agrees with observed published releases.

SENSE360-REVIEW-RELEASE-001.

``config/webflash-builds.json`` uses exactly one ``release_state`` value,
``metadata-ready-unpublished``, and published rows carry no ``release_state``
at all (the shape of the published VentIQ LED preview row and the stable
rows; ``scripts/promote_to_stable.py`` lists it as a preview-only field). A
row that still claims ``metadata-ready-unpublished`` for a version whose
GitHub Release has been published is a stale declaration.

CI runs offline, so the published releases are pinned here as OBSERVED
EXISTING EVIDENCE with provenance (read from the GitHub REST API and the
WebFlash tree; they are not outcomes of any agent's work). This guard proves
declaration consistency only. It is not proof of hardware behaviour, bench
evidence, compliance, customer validation or commercial availability, and it
claims nothing about served binaries beyond the recorded WebFlash files.

Run with::

    python3 tests/test_published_release_state_consistency.py
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any, Dict

REPO_ROOT = Path(__file__).resolve().parent.parent
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
ROADMAP_PATH = REPO_ROOT / "docs" / "sense360-roadmap-status.md"

METADATA_READY = "metadata-ready-unpublished"
ALLOWED_RELEASE_STATES = frozenset({METADATA_READY})

# Observed published releases for declared rows, keyed by config string.
# Provenance per entry: GitHub REST API (repos/sense360store/esphome-public/
# releases/tags/<tag>) and, where recorded, the WebFlash main import record.
OBSERVED_PUBLISHED_RELEASES: Dict[str, Dict[str, Any]] = {
    "Ceiling-POE-AirIQ-RoomIQ": {
        "version": "1.0.10",
        "channel": "preview",
        "release_tag": "v1.0.10-preview",
        "release_url": (
            "https://github.com/sense360store/esphome-public/releases/tag/"
            "v1.0.10-preview"
        ),
        "prerelease": True,
        "published_at": "2026-08-21T10:23:18Z",
        "target_commit": "adb03fdc03f938cb54f62d08b7947a6d82f1a402",
        "asset_name": "Sense360-Ceiling-POE-AirIQ-RoomIQ-v1.0.10-preview.bin",
        "asset_sha256": (
            "c06389ba52e6c255b965287d52031729b726698b5da340851f3e5b86eceef698"
        ),
        "webflash_sidecar": (
            "firmware/configurations/"
            "Sense360-Ceiling-POE-AirIQ-RoomIQ-v1.0.10-preview.meta.json"
        ),
        "webflash_import_commit": "55cc0eccc5bc6c4f51031f1b62b24a6fc2b54183",
        "webflash_imported_at": "2026-08-21T12:20:14+00:00",
    },
}


def _by_cs() -> Dict[str, Dict[str, Any]]:
    builds = json.loads(BUILDS_PATH.read_text(encoding="utf-8"))["builds"]
    return {b["config_string"]: b for b in builds}


class ReleaseStateVocabularyTests(unittest.TestCase):
    def test_release_state_uses_only_existing_value(self) -> None:
        for cs, row in _by_cs().items():
            if "release_state" in row:
                with self.subTest(config_string=cs):
                    self.assertIn(row["release_state"], ALLOWED_RELEASE_STATES)


class PublishedReleaseConsistencyTests(unittest.TestCase):
    def test_published_version_is_not_declared_unpublished(self) -> None:
        by_cs = _by_cs()
        for cs, rel in OBSERVED_PUBLISHED_RELEASES.items():
            with self.subTest(config_string=cs):
                row = by_cs[cs]
                if row["version"] != rel["version"]:
                    # The declaration moved past the observed release; the
                    # observation says nothing about the new version.
                    continue
                self.assertEqual(row["channel"], rel["channel"])
                self.assertEqual(row["artifact_name"], rel["asset_name"])
                self.assertNotEqual(
                    row.get("release_state"),
                    METADATA_READY,
                    f"{cs} v{rel['version']} is published as "
                    f"{rel['release_tag']} ({rel['release_url']}); the row "
                    "must not claim metadata-ready-unpublished",
                )

    def test_published_row_notes_do_not_claim_unpublished_state(self) -> None:
        # The notes must not contradict the row: once the field is dropped
        # for a published version, no prose may still claim it.
        by_cs = _by_cs()
        for cs, rel in OBSERVED_PUBLISHED_RELEASES.items():
            with self.subTest(config_string=cs):
                row = by_cs[cs]
                if row["version"] != rel["version"]:
                    continue
                notes = row.get("notes", "")
                for claim in (
                    f"release_state stays {METADATA_READY}",
                    f"release_state remains {METADATA_READY}",
                    f"release_state is {METADATA_READY}",
                ):
                    self.assertNotIn(claim, notes)

    def test_published_row_keeps_non_stable_posture(self) -> None:
        # Publication on the preview channel changes no channel, posture or
        # stable gate.
        by_cs = _by_cs()
        for cs, rel in OBSERVED_PUBLISHED_RELEASES.items():
            with self.subTest(config_string=cs):
                row = by_cs[cs]
                self.assertTrue(rel["prerelease"])
                self.assertEqual(row["channel"], "preview")
                self.assertTrue(row["stable_blocker"])
                posture = row["commercial_posture"]
                self.assertFalse(posture["stable"])
                self.assertFalse(posture["buyable"])
                self.assertFalse(posture["recommended"])
                self.assertFalse(posture["customer_default"])
                self.assertEqual(posture["visibility"], "hidden")


class RoadmapStatusDocTests(unittest.TestCase):
    def test_roadmap_cites_observed_release_and_webflash_record(self) -> None:
        text = ROADMAP_PATH.read_text(encoding="utf-8")
        for cs, rel in OBSERVED_PUBLISHED_RELEASES.items():
            with self.subTest(config_string=cs):
                self.assertIn(rel["release_url"], text)
                self.assertIn(rel["target_commit"], text)
                self.assertIn(rel["webflash_sidecar"], text)
                self.assertIn(rel["webflash_import_commit"], text)
                self.assertNotIn(
                    f"declared at **{rel['version']}** on the preview channel "
                    "awaiting",
                    text,
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)

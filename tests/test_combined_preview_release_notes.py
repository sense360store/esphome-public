#!/usr/bin/env python3
"""Regression guard for RELEASE-PREVIEW-COMBINED-RELEASE-NOTES-001."""

from __future__ import annotations

import importlib.util
import json
import re
import unittest
from pathlib import Path
from typing import Any, Dict


REPO_ROOT = Path(__file__).resolve().parent.parent
NOTES_PATH = REPO_ROOT / "docs" / "release-notes" / "preview" / "v1.0.0-preview.md"
VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate-webflash-release-notes.py"
WEBFLASH_BUILDS = REPO_ROOT / "config" / "webflash-builds.json"
FAN_LEDGER = REPO_ROOT / "config" / "preview-fan-triac-build-rows.json"
UPCOMING_PR = REPO_ROOT / "UPCOMING_PR.md"

RELEASE_ID = "RELEASE-PREVIEW-COMBINED-RELEASE-NOTES-001"
SHARED_TAG_ID = "RELEASE-PREVIEW-FAN-SHARED-TAG-001"
RELEASE_TAG = "v1.0.0-preview"
VERSION = "1.0.0"
CHANNEL = "preview"

# The (version=1.0.0, channel=preview) rows still in config/webflash-builds.json
# TODAY. The v1.0.0-preview release originally also carried Ceiling-POE-RoomIQ
# and Ceiling-POE-AirIQ-RoomIQ, but those were since promoted to stable
# (v1.0.5 on 2026-06-08 and v1.0.6 on 2026-06-09, owner-waiver promotions), so
# they are no longer preview-channel rows in the live ledger. The historical
# notes doc still names them; the live-derivation check below covers only the
# rows that remain on the preview channel.
EXPECTED_ROOM_PREVIEW_CONFIGS = {
    "Ceiling-POE-RoomIQ-LED",
    "Ceiling-POE-VentIQ-RoomIQ-LED",
}

EXPECTED_FAN_MANUAL_PREVIEW_CONFIGS = {
    "Ceiling-POE-VentIQ-FanRelay-RoomIQ",
    "Ceiling-POE-FanPWM",
    "Ceiling-POE-FanDAC",
}

TRIAC_CONFIG = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"
REQUIRED_H2_SECTIONS = {
    "Changelog",
    "Known Issues",
    "Features",
    "Hardware Requirements",
}

REQUIRED_WARNING_PHRASES = (
    "preview/manual-preview firmware only",
    "not stable",
    "not recommended",
    "not default",
    "not simple install",
    "not buyable as public shop product",
    "no hardware proof",
    "no bench proof",
    "no compliance proof",
    "no commercial-availability proof",
    "fan-control builds require installer/developer judgement",
    "triac excluded",
)

FORBIDDEN_AFFIRMATIVE_PHRASES = (
    "is stable",
    "now stable",
    "marked stable",
    "promoted to stable",
    "is recommended",
    "recommended for customers",
    "is the default",
    "is default",
    "customer-ready",
    "production-ready",
)


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_webflash_release_notes", VALIDATOR_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


_VALIDATOR = _load_validator()


def _normalise(text: str) -> str:
    lines = [re.sub(r"^\s*>\s?", "", ln) for ln in text.splitlines()]
    joined = " ".join(lines).replace("`", "").replace("|", " ").replace("*", "")
    return re.sub(r"\s+", " ", joined).lower()


def _room_preview_configs_from_webflash_builds() -> set[str]:
    return {
        row["config_string"]
        for row in _load_json(WEBFLASH_BUILDS)["builds"]
        if row.get("version") == VERSION and row.get("channel") == CHANNEL
    }


def _fan_manual_preview_configs_from_ledger() -> set[str]:
    return {
        row["config_string"]
        for row in _load_json(FAN_LEDGER)["rows"]
        if row.get("delivery_lane") == "manual-preview"
        and row.get("version") == VERSION
        and row.get("build_channel") == CHANNEL
        and row.get("buildable_now") is True
    }


class CombinedReleaseNotesStructuralTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = NOTES_PATH.read_text(encoding="utf-8")
        cls.norm = _normalise(cls.text)

    def test_combined_notes_file_exists_and_names_canonical_id(self) -> None:
        self.assertTrue(NOTES_PATH.is_file())
        self.assertIn(RELEASE_ID, self.text)
        self.assertIn(RELEASE_TAG, self.text)

    def test_passes_webflash_release_notes_validator_on_preview_channel(self) -> None:
        errors = _VALIDATOR.validate_body(self.text, channel=CHANNEL)
        self.assertEqual(errors, [], errors)

    def test_has_all_required_h2_sections(self) -> None:
        sections = _VALIDATOR._parse_sections(self.text)
        self.assertTrue(
            REQUIRED_H2_SECTIONS.issubset(sections.keys()),
            f"missing sections: {REQUIRED_H2_SECTIONS - set(sections.keys())}",
        )

    def test_required_h2_sections_are_non_empty(self) -> None:
        sections = _VALIDATOR._parse_sections(self.text)
        for section in REQUIRED_H2_SECTIONS:
            with self.subTest(section=section):
                self.assertGreater(len(sections.get(section, [])), 0)


class CombinedArtifactCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = NOTES_PATH.read_text(encoding="utf-8")
        cls.norm = _normalise(cls.text)

    def test_room_preview_configs_match_webflash_preview_rows(self) -> None:
        self.assertEqual(
            _room_preview_configs_from_webflash_builds(),
            EXPECTED_ROOM_PREVIEW_CONFIGS,
        )
        for config in EXPECTED_ROOM_PREVIEW_CONFIGS:
            with self.subTest(config=config):
                self.assertIn(config, self.text)

    def test_fan_manual_preview_configs_match_manual_preview_ledger(self) -> None:
        self.assertEqual(
            _fan_manual_preview_configs_from_ledger(),
            EXPECTED_FAN_MANUAL_PREVIEW_CONFIGS,
        )
        for config in EXPECTED_FAN_MANUAL_PREVIEW_CONFIGS:
            with self.subTest(config=config):
                self.assertIn(config, self.text)

    def test_triac_is_explicitly_excluded_and_no_triac_bin_is_named(self) -> None:
        self.assertIn(TRIAC_CONFIG, self.text)
        self.assertIn("triac excluded", self.norm)
        self.assertIn("hw-005", self.norm)
        self.assertNotRegex(
            self.text,
            r"Sense360-Ceiling-POE-VentIQ-FanTRIAC-RoomIQ-v1\.0\.0-preview\.bin",
        )


class CombinedWarningCopyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = NOTES_PATH.read_text(encoding="utf-8")
        cls.norm = _normalise(cls.text)

    def test_required_warning_phrases_are_present(self) -> None:
        for phrase in REQUIRED_WARNING_PHRASES:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.norm)

    def test_no_affirmative_stable_recommended_default_customer_ready_language(self) -> None:
        for phrase in FORBIDDEN_AFFIRMATIVE_PHRASES:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, self.norm)

    def test_fan_artifacts_do_not_imply_webflash_import(self) -> None:
        self.assertIn("does not imply webflash import for fan artifacts", self.norm)
        self.assertIn("they are not webflash imports", self.norm)
        self.assertIn("no fan row is added to config/webflash-builds.json", self.norm)
        ledger_rows = {
            row["config_string"]: row for row in _load_json(FAN_LEDGER)["rows"]
        }
        for config in EXPECTED_FAN_MANUAL_PREVIEW_CONFIGS:
            with self.subTest(config=config):
                self.assertIs(ledger_rows[config]["webflash_importable"], False)

    def test_notes_do_not_imply_simple_install_exposure(self) -> None:
        self.assertIn("not simple install", self.norm)
        self.assertIn("no simple-install exposure is created", self.norm)


class UpcomingPrQueueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = UPCOMING_PR.read_text(encoding="utf-8")
        cls.norm = _normalise(cls.text)

    def test_pr_708_shared_tag_is_marked_done(self) -> None:
        self.assertIn("#708", self.text)
        self.assertIn(SHARED_TAG_ID, self.text)
        shared_tag_lines = [
            line
            for line in self.text.splitlines()
            if SHARED_TAG_ID in line or "#708" in line
        ]
        self.assertTrue(
            any("DONE" in line for line in shared_tag_lines),
            f"{SHARED_TAG_ID} / #708 is not marked DONE",
        )

    def test_combined_release_notes_item_is_this_pr(self) -> None:
        self.assertIn(RELEASE_ID, self.text)
        self.assertIn("v1.0.0-preview.md", self.text)
        self.assertIn("DONE (this PR)", self.text)

    def test_webflash_fan_import_decisions_are_queued_separately(self) -> None:
        for followup in ("WEBFLASH-RELAY-001", "WEBFLASH-PWM-001", "WEBFLASH-DAC-001"):
            with self.subTest(followup=followup):
                heading = re.compile(rf"^#### {followup}\b.*queued", re.MULTILINE)
                self.assertRegex(self.text, heading)
        self.assertIn("queued separately", self.norm)

    def test_triac_preview_work_stays_separate(self) -> None:
        self.assertIn("fantriac preview work", self.norm)
        self.assertIn("hw-005", self.norm)
        self.assertIn("must remain its own", self.norm)


if __name__ == "__main__":
    unittest.main(verbosity=2)

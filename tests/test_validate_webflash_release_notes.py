#!/usr/bin/env python3
"""Unit tests for scripts/validate-webflash-release-notes.py.

Uses Python's stdlib unittest (matching this repo's no-pytest convention for
Python validators).

Run with:
    python3 tests/test_validate_webflash_release_notes.py
"""

import importlib.util
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "validate-webflash-release-notes.py"

_spec = importlib.util.spec_from_file_location(
    "validate_webflash_release_notes", SCRIPT_PATH
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
sys.modules["validate_webflash_release_notes"] = _mod
validate_body = _mod.validate_body


VALID_RELEASE_ONE = """## Changelog

- Initial production stable release for Ceiling-POE-VentIQ-RoomIQ with PoE power, VentIQ bathroom air-quality sensing, and RoomIQ room sensing. FanTRIAC is excluded from production Release-One while HW-005 is open.

## Known Issues

- None.

## Features

- PoE-powered Sense360 Core configuration
- VentIQ bathroom air-quality sensing
- RoomIQ room sensing

## Hardware Requirements

- Sense360 Core R4 or newer
- Sense360 PoE PSU
- Sense360 VentIQ module
- Sense360 RoomIQ module
"""


class WebflashReleaseNotesTests(unittest.TestCase):
    # ------------------------------------------------------------------
    # 1. Valid Release-One body passes.
    # ------------------------------------------------------------------
    def test_valid_release_one_passes(self):
        errors = validate_body(VALID_RELEASE_ONE, channel="stable")
        self.assertEqual(errors, [], errors)

    # ------------------------------------------------------------------
    # 2. Missing ## Changelog fails.
    # ------------------------------------------------------------------
    def test_missing_changelog_fails(self):
        body = VALID_RELEASE_ONE.replace("## Changelog\n", "## Notes\n")
        errors = validate_body(body, channel="stable")
        self.assertTrue(
            any("Changelog" in e for e in errors),
            f"expected Changelog error; got {errors}",
        )

    # ------------------------------------------------------------------
    # 3. Missing ## Known Issues fails.
    # ------------------------------------------------------------------
    def test_missing_known_issues_fails(self):
        body = VALID_RELEASE_ONE.replace("## Known Issues\n", "## Open Items\n")
        errors = validate_body(body, channel="stable")
        self.assertTrue(
            any("Known Issues" in e for e in errors),
            f"expected Known Issues error; got {errors}",
        )

    # ------------------------------------------------------------------
    # 4. Missing ## Features fails.
    # ------------------------------------------------------------------
    def test_missing_features_fails(self):
        body = VALID_RELEASE_ONE.replace("## Features\n", "## What\n")
        errors = validate_body(body, channel="stable")
        self.assertTrue(
            any("Features" in e for e in errors),
            f"expected Features error; got {errors}",
        )

    # ------------------------------------------------------------------
    # 5. Missing ## Hardware Requirements fails.
    # ------------------------------------------------------------------
    def test_missing_hardware_requirements_fails(self):
        body = VALID_RELEASE_ONE.replace("## Hardware Requirements\n", "## Hardware\n")
        errors = validate_body(body, channel="stable")
        self.assertTrue(
            any("Hardware Requirements" in e for e in errors),
            f"expected Hardware Requirements error; got {errors}",
        )

    # ------------------------------------------------------------------
    # 6. Empty Changelog fails.
    # ------------------------------------------------------------------
    def test_empty_changelog_fails(self):
        body = """## Changelog

## Known Issues

- None.

## Features

- A feature

## Hardware Requirements

- A requirement
"""
        errors = validate_body(body, channel="stable")
        self.assertTrue(
            any("Changelog" in e and "bullet" in e for e in errors),
            f"expected empty-Changelog error; got {errors}",
        )

    # ------------------------------------------------------------------
    # 7. Filler changelog fails on stable.
    # ------------------------------------------------------------------
    def test_filler_changelog_fails_on_stable(self):
        original_bullet = (
            "- Initial production stable release for "
            "Ceiling-POE-VentIQ-RoomIQ with PoE power, VentIQ "
            "bathroom air-quality sensing, and RoomIQ room sensing. "
            "FanTRIAC is excluded from production Release-One while "
            "HW-005 is open."
        )
        for filler in (
            "TBD",
            "Initial release",
            "N/A",
            "Placeholder",
            "No changes",
            "See release notes",
        ):
            with self.subTest(filler=filler):
                body = VALID_RELEASE_ONE.replace(original_bullet, f"- {filler}")
                errors = validate_body(body, channel="stable")
                self.assertTrue(
                    any("filler" in e.lower() for e in errors),
                    f"expected filler error for '{filler}'; got {errors}",
                )

    # ------------------------------------------------------------------
    # 8. Known Issues with `- None.` passes (covered by valid body).
    # ------------------------------------------------------------------
    def test_known_issues_with_none_passes(self):
        errors = validate_body(VALID_RELEASE_ONE, channel="stable")
        self.assertEqual(errors, [], errors)

    # ------------------------------------------------------------------
    # 9. Alternate bullet formats pass (`*`, `+`).
    # ------------------------------------------------------------------
    def test_alternate_bullet_styles_pass(self):
        body = VALID_RELEASE_ONE.replace(
            "- PoE-powered Sense360 Core configuration",
            "* PoE-powered Sense360 Core configuration",
        ).replace(
            "- Sense360 Core R4 or newer",
            "+ Sense360 Core R4 or newer",
        )
        errors = validate_body(body, channel="stable")
        self.assertEqual(errors, [], errors)

    # ------------------------------------------------------------------
    # 10. CRLF line endings pass.
    # ------------------------------------------------------------------
    def test_crlf_line_endings_pass(self):
        body = VALID_RELEASE_ONE.replace("\n", "\r\n")
        errors = validate_body(body, channel="stable")
        self.assertEqual(errors, [], errors)


if __name__ == "__main__":
    unittest.main(verbosity=2)

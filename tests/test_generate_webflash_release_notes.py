#!/usr/bin/env python3
"""Unit tests for scripts/generate_webflash_release_notes.py (RELEASE-001).

Uses Python's stdlib ``unittest`` (matching the no-pytest convention the
rest of the validators in this repo use). Run with:

    python3 tests/test_generate_webflash_release_notes.py

The tests lock in:

  * Release-One generation produces a body with all four required
    Markdown ``##`` sections and passes the existing release-notes
    validator.
  * Output includes the config string, the artifact name, and every
    hardware SKU from the product catalog.
  * FanTRIAC and Sense360 LED appear only in ``## Known Issues`` as
    exclusions, never in ``## Features``.
  * The generator refuses ``blocked`` (FanTRIAC) and
    ``legacy-compatible`` catalog entries.
  * The generator refuses preview-status entries on the stable channel.
  * The generator accepts a user-supplied changelog and the resulting
    body still passes the validator.
  * ``--output`` writes a file containing the same body that stdout
    would have produced.
  * ``--validate`` shells out to the existing release-notes validator
    and returns 0 for Release-One.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "generate_webflash_release_notes.py"
VALIDATOR_SCRIPT = REPO_ROOT / "scripts" / "validate-webflash-release-notes.py"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


gen = _load_module("generate_webflash_release_notes", SCRIPT_PATH)
val = _load_module("validate_webflash_release_notes", VALIDATOR_SCRIPT)


RELEASE_ONE_CONFIG_STRING = "Ceiling-POE-VentIQ-RoomIQ"
RELEASE_ONE_VERSION = "1.0.0"
RELEASE_ONE_CHANNEL = "stable"
RELEASE_ONE_ARTIFACT = (
    "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin"
)
RELEASE_ONE_SKUS = ("S360-100", "S360-211", "S360-200", "S360-410")
FANTRIAC_BLOCKED_CONFIG = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"
LEGACY_CONFIG_ID = "sense360-poe"


def _generate_release_one(**overrides: Any) -> str:
    kwargs: Dict[str, Any] = dict(
        config_string=RELEASE_ONE_CONFIG_STRING,
        version=RELEASE_ONE_VERSION,
        channel=RELEASE_ONE_CHANNEL,
    )
    kwargs.update(overrides)
    return gen.generate(**kwargs)


def _section_bullets(body: str, section: str) -> List[str]:
    return val._parse_sections(body).get(section, [])


# ----------------------------------------------------------------------
# Release-One generation
# ----------------------------------------------------------------------


class ReleaseOneGenerationTests(unittest.TestCase):
    def test_generates_all_four_required_sections(self) -> None:
        body = _generate_release_one()
        sections = val._parse_sections(body)
        for required in (
            "Changelog",
            "Known Issues",
            "Features",
            "Hardware Requirements",
        ):
            self.assertIn(
                required,
                sections,
                f"missing required section {required}; body was:\n{body}",
            )

    def test_generated_output_passes_validator(self) -> None:
        body = _generate_release_one()
        errors = val.validate_body(body, channel=RELEASE_ONE_CHANNEL)
        self.assertEqual(
            errors, [], f"validator errors: {errors}\nbody:\n{body}"
        )

    def test_output_contains_config_string(self) -> None:
        body = _generate_release_one()
        self.assertIn(RELEASE_ONE_CONFIG_STRING, body)

    def test_output_contains_artifact_name(self) -> None:
        body = _generate_release_one()
        self.assertIn(RELEASE_ONE_ARTIFACT, body)

    def test_output_contains_hardware_skus(self) -> None:
        body = _generate_release_one()
        for sku in RELEASE_ONE_SKUS:
            self.assertIn(
                sku, body, f"missing SKU {sku} in body:\n{body}"
            )


# ----------------------------------------------------------------------
# FanTRIAC and LED must be exclusions, never features
# ----------------------------------------------------------------------


class FanTRIACAndLEDExclusionTests(unittest.TestCase):
    def test_fantriac_is_known_issue_not_feature(self) -> None:
        body = _generate_release_one()
        known_issues = _section_bullets(body, "Known Issues")
        features = _section_bullets(body, "Features")
        self.assertTrue(
            any("FanTRIAC" in b for b in known_issues),
            f"FanTRIAC missing from Known Issues: {known_issues}",
        )
        self.assertFalse(
            any("FanTRIAC" in b for b in features),
            f"FanTRIAC must not appear in Features: {features}",
        )

    def test_led_is_known_issue_not_feature(self) -> None:
        body = _generate_release_one()
        known_issues = _section_bullets(body, "Known Issues")
        features = _section_bullets(body, "Features")
        self.assertTrue(
            any("LED" in b for b in known_issues),
            f"LED missing from Known Issues: {known_issues}",
        )
        self.assertFalse(
            any("LED" in b for b in features),
            f"LED must not appear in Features: {features}",
        )

    def test_fantriac_known_issue_references_hw_005(self) -> None:
        body = _generate_release_one()
        known_issues = _section_bullets(body, "Known Issues")
        fantriac_bullet = next(
            (b for b in known_issues if "FanTRIAC" in b), None
        )
        self.assertIsNotNone(fantriac_bullet)
        self.assertIn("HW-005", fantriac_bullet or "")


# ----------------------------------------------------------------------
# Refusal paths
# ----------------------------------------------------------------------


class RefusalTests(unittest.TestCase):
    def test_refuses_blocked_fantriac_config(self) -> None:
        with self.assertRaises(gen.GeneratorError) as ctx:
            _generate_release_one(
                config_string=FANTRIAC_BLOCKED_CONFIG, channel="stable"
            )
        self.assertIn("blocked", str(ctx.exception).lower())

    def test_refuses_legacy_compatible_product(self) -> None:
        with self.assertRaises(gen.GeneratorError) as ctx:
            _generate_release_one(
                config_string=LEGACY_CONFIG_ID, channel="stable"
            )
        self.assertIn("legacy", str(ctx.exception).lower())

    def test_refuses_unknown_config_string(self) -> None:
        with self.assertRaises(gen.GeneratorError):
            _generate_release_one(config_string="Not-A-Real-Config")


# ----------------------------------------------------------------------
# Stable channel requires production status (synthetic catalog)
# ----------------------------------------------------------------------


class StableRequiresProductionTests(unittest.TestCase):
    """Synthetic catalog so the rule is locked in even without a live
    preview entry in the real catalog."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.catalog_path = Path(tmp.name) / "catalog.json"
        self.builds_path = Path(tmp.name) / "builds.json"
        self.hardware_path = Path(tmp.name) / "hardware.json"

        self.catalog_path.write_text(
            json.dumps(
                {
                    "products": [
                        {
                            "config_string": "Ceiling-USB-AirIQ",
                            "status": "preview",
                            "version": "0.9.0",
                            "channel": "preview",
                            "product_yaml": "products/x.yaml",
                            "webflash_wrapper": "products/webflash/x.yaml",
                            "artifact_name": (
                                "Sense360-Ceiling-USB-AirIQ-"
                                "v0.9.0-preview.bin"
                            ),
                            "webflash_build_matrix": True,
                            "modules": {"mount": "Ceiling"},
                            "blocked_modules": [],
                            "hardware": {"core": "S360-100"},
                            "hardware_status": "verified",
                        }
                    ]
                }
            )
        )
        self.builds_path.write_text(
            json.dumps(
                {
                    "builds": [
                        {
                            "config_string": "Ceiling-USB-AirIQ",
                            "version": "0.9.0",
                            "channel": "preview",
                            "features": ["Preview AirIQ feature"],
                            "hardware_requirements": ["Sense360 Core"],
                            "artifact_name": (
                                "Sense360-Ceiling-USB-AirIQ-"
                                "v0.9.0-preview.bin"
                            ),
                        }
                    ]
                }
            )
        )
        self.hardware_path.write_text(
            json.dumps(
                {
                    "items": [
                        {
                            "sku": "S360-100",
                            "friendly_name": "Sense360 Core",
                        }
                    ]
                }
            )
        )

    def test_stable_channel_refuses_preview_entry(self) -> None:
        with self.assertRaises(gen.GeneratorError) as ctx:
            gen.generate(
                config_string="Ceiling-USB-AirIQ",
                version="0.9.0",
                channel="stable",
                catalog_path=self.catalog_path,
                builds_path=self.builds_path,
                hardware_path=self.hardware_path,
            )
        self.assertIn("stable", str(ctx.exception).lower())

    def test_preview_channel_accepts_preview_entry(self) -> None:
        body = gen.generate(
            config_string="Ceiling-USB-AirIQ",
            version="0.9.0",
            channel="preview",
            catalog_path=self.catalog_path,
            builds_path=self.builds_path,
            hardware_path=self.hardware_path,
        )
        errors = val.validate_body(body, channel="preview")
        self.assertEqual(errors, [], errors)


# ----------------------------------------------------------------------
# Custom changelog input
# ----------------------------------------------------------------------


class CustomChangelogTests(unittest.TestCase):
    def test_custom_changelog_text_appears_in_output(self) -> None:
        body = _generate_release_one(
            changelog="Real change one\nReal change two"
        )
        bullets = _section_bullets(body, "Changelog")
        self.assertIn("Real change one", bullets)
        self.assertIn("Real change two", bullets)

    def test_custom_changelog_passes_validator(self) -> None:
        body = _generate_release_one(
            changelog="Concrete user-visible change for v1.0.0."
        )
        errors = val.validate_body(body, channel=RELEASE_ONE_CHANNEL)
        self.assertEqual(errors, [], errors)

    def test_custom_changelog_strips_bullet_prefix(self) -> None:
        body = _generate_release_one(
            changelog="- bullet one\n* bullet two\n+ bullet three"
        )
        bullets = _section_bullets(body, "Changelog")
        self.assertIn("bullet one", bullets)
        self.assertIn("bullet two", bullets)
        self.assertIn("bullet three", bullets)

    def test_changelog_file_is_read(self) -> None:
        with tempfile.NamedTemporaryFile(
            "w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write("- Bullet from file one\n- Bullet from file two\n")
            f_path = Path(f.name)
        try:
            body = _generate_release_one(changelog_file=f_path)
            bullets = _section_bullets(body, "Changelog")
            self.assertIn("Bullet from file one", bullets)
            self.assertIn("Bullet from file two", bullets)
        finally:
            try:
                f_path.unlink()
            except OSError:
                pass

    def test_require_changelog_without_input_errors(self) -> None:
        with self.assertRaises(gen.GeneratorError):
            _generate_release_one(require_changelog=True)

    def test_changelog_and_changelog_file_are_mutually_exclusive(self) -> None:
        with self.assertRaises(gen.GeneratorError):
            _generate_release_one(
                changelog="x", changelog_file=Path("/tmp/no")
            )


# ----------------------------------------------------------------------
# --output writes a file
# ----------------------------------------------------------------------


class OutputFileTests(unittest.TestCase):
    def test_output_flag_writes_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "notes.md"
            rc = gen.main(
                [
                    "--config-string", RELEASE_ONE_CONFIG_STRING,
                    "--version", RELEASE_ONE_VERSION,
                    "--channel", RELEASE_ONE_CHANNEL,
                    "--output", str(out),
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(
                out.is_file(), f"{out} should have been written"
            )
            content = out.read_text(encoding="utf-8")
            self.assertIn("## Changelog", content)
            self.assertIn("## Known Issues", content)
            self.assertIn("## Features", content)
            self.assertIn("## Hardware Requirements", content)
            self.assertIn(RELEASE_ONE_CONFIG_STRING, content)


# ----------------------------------------------------------------------
# --validate shells out to the existing validator
# ----------------------------------------------------------------------


class ValidateFlagTests(unittest.TestCase):
    def test_validate_flag_passes_on_release_one(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "notes.md"
            rc = gen.main(
                [
                    "--config-string", RELEASE_ONE_CONFIG_STRING,
                    "--version", RELEASE_ONE_VERSION,
                    "--channel", RELEASE_ONE_CHANNEL,
                    "--output", str(out),
                    "--validate",
                ]
            )
            self.assertEqual(
                rc, 0, "expected --validate to return 0 on Release-One"
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)

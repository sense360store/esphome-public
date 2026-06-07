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

Version-bearing fixtures (version, channel, artifact_name) are read from
``config/product-catalog.json`` rather than hardcoded, so this test tracks
the catalog and never goes stale when "Release 1: Bump Version" bumps a
config's version and version-bearing artifact_name. The behavioural
assertions are unchanged.
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
CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


gen = _load_module("generate_webflash_release_notes", SCRIPT_PATH)
val = _load_module("validate_webflash_release_notes", VALIDATOR_SCRIPT)


def _catalog_entry(config_string: str) -> Dict[str, Any]:
    """Return the ``config/product-catalog.json`` entry for ``config_string``.

    The version-bearing fixtures below (version, channel, artifact_name) are
    read from this entry rather than hardcoded, so the test follows the
    catalog and never goes stale when "Release 1: Bump Version" bumps a
    config's version + version-bearing artifact_name. The config_string,
    expected hardware SKUs, and every behavioural assertion stay explicit.
    """
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    for entry in catalog.get("products", []) or []:
        if isinstance(entry, dict) and entry.get("config_string") == config_string:
            return entry
    raise AssertionError(
        f"{config_string!r} not found in {CATALOG_PATH}; this test fixture "
        "requires the config to exist in the product catalog"
    )


RELEASE_ONE_CONFIG_STRING = "Ceiling-POE-VentIQ-RoomIQ"
_RELEASE_ONE_ENTRY = _catalog_entry(RELEASE_ONE_CONFIG_STRING)
RELEASE_ONE_VERSION = _RELEASE_ONE_ENTRY["version"]
RELEASE_ONE_CHANNEL = _RELEASE_ONE_ENTRY["channel"]
RELEASE_ONE_ARTIFACT = _RELEASE_ONE_ENTRY["artifact_name"]
RELEASE_ONE_SKUS = ("S360-100", "S360-211", "S360-200", "S360-410")
FANTRIAC_BLOCKED_CONFIG = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"
LEGACY_CONFIG_ID = "sense360-poe"

LED_PREVIEW_CONFIG_STRING = "Ceiling-POE-VentIQ-RoomIQ-LED"
_LED_PREVIEW_ENTRY = _catalog_entry(LED_PREVIEW_CONFIG_STRING)
LED_PREVIEW_VERSION = _LED_PREVIEW_ENTRY["version"]
LED_PREVIEW_CHANNEL = _LED_PREVIEW_ENTRY["channel"]
LED_PREVIEW_ARTIFACT = _LED_PREVIEW_ENTRY["artifact_name"]
LED_PREVIEW_SKUS = (
    "S360-100",
    "S360-211",
    "S360-200",
    "S360-410",
    "S360-300",
)


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
        self.assertEqual(errors, [], f"validator errors: {errors}\nbody:\n{body}")

    def test_output_contains_config_string(self) -> None:
        body = _generate_release_one()
        self.assertIn(RELEASE_ONE_CONFIG_STRING, body)

    def test_output_contains_artifact_name(self) -> None:
        body = _generate_release_one()
        self.assertIn(RELEASE_ONE_ARTIFACT, body)

    def test_output_contains_hardware_skus(self) -> None:
        body = _generate_release_one()
        for sku in RELEASE_ONE_SKUS:
            self.assertIn(sku, body, f"missing SKU {sku} in body:\n{body}")


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

    def test_fantriac_known_issue_references_compliance_001(self) -> None:
        # TRIAC-UNBLOCK-BUILD-001 cleared the HW-005 buildability blocker; the
        # FanTRIAC Known-Issues bullet now cites the remaining stable gate
        # (COMPLIANCE-001 mains-voltage review).
        body = _generate_release_one()
        known_issues = _section_bullets(body, "Known Issues")
        fantriac_bullet = next((b for b in known_issues if "FanTRIAC" in b), None)
        self.assertIsNotNone(fantriac_bullet)
        self.assertIn("COMPLIANCE-001", fantriac_bullet or "")


# ----------------------------------------------------------------------
# LED preview generation (PRODUCT-009): LED moves from Known Issues to
# Features for the LED-bearing sibling, FanTRIAC remains a Known Issue.
# ----------------------------------------------------------------------


def _generate_led_preview(**overrides):
    kwargs = dict(
        config_string=LED_PREVIEW_CONFIG_STRING,
        version=LED_PREVIEW_VERSION,
        channel=LED_PREVIEW_CHANNEL,
    )
    kwargs.update(overrides)
    return gen.generate(**kwargs)


class LedPreviewGenerationTests(unittest.TestCase):
    def test_generates_all_four_required_sections(self) -> None:
        body = _generate_led_preview()
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
        body = _generate_led_preview()
        errors = val.validate_body(body, channel=LED_PREVIEW_CHANNEL)
        self.assertEqual(errors, [], f"validator errors: {errors}\nbody:\n{body}")

    def test_output_contains_config_string(self) -> None:
        body = _generate_led_preview()
        self.assertIn(LED_PREVIEW_CONFIG_STRING, body)

    def test_output_contains_artifact_name(self) -> None:
        body = _generate_led_preview()
        self.assertIn(LED_PREVIEW_ARTIFACT, body)

    def test_output_contains_all_hardware_skus_including_led(self) -> None:
        body = _generate_led_preview()
        for sku in LED_PREVIEW_SKUS:
            self.assertIn(sku, body, f"missing SKU {sku} in body:\n{body}")

    def test_led_is_feature_not_known_issue_for_led_preview(self) -> None:
        body = _generate_led_preview()
        features = _section_bullets(body, "Features")
        known_issues = _section_bullets(body, "Known Issues")
        self.assertTrue(
            any("LED" in b for b in features),
            f"LED missing from Features for LED preview: {features}",
        )
        self.assertFalse(
            any("LED" in b for b in known_issues),
            f"LED must not appear in Known Issues for LED preview: " f"{known_issues}",
        )

    def test_led_appears_in_hardware_requirements_for_led_preview(self) -> None:
        body = _generate_led_preview()
        hardware = _section_bullets(body, "Hardware Requirements")
        self.assertTrue(
            any("LED" in b or "S360-300" in b for b in hardware),
            "Sense360 LED hardware must appear in Hardware Requirements "
            f"for the LED preview: {hardware}",
        )

    def test_fantriac_remains_known_issue_for_led_preview(self) -> None:
        body = _generate_led_preview()
        known_issues = _section_bullets(body, "Known Issues")
        features = _section_bullets(body, "Features")
        self.assertTrue(
            any("FanTRIAC" in b for b in known_issues),
            f"FanTRIAC missing from Known Issues for LED preview: " f"{known_issues}",
        )
        self.assertTrue(
            any("COMPLIANCE-001" in b for b in known_issues),
            f"FanTRIAC Known-Issues bullet must reference COMPLIANCE-001 "
            f"(HW-005 buildability resolved by TRIAC-UNBLOCK-BUILD-001): "
            f"{known_issues}",
        )
        self.assertFalse(
            any("FanTRIAC" in b for b in features),
            f"FanTRIAC must not appear in Features for LED preview: " f"{features}",
        )

    def test_stable_channel_refused_for_led_preview(self) -> None:
        with self.assertRaises(gen.GeneratorError) as ctx:
            _generate_led_preview(channel="stable")
        self.assertIn("stable", str(ctx.exception).lower())


# ----------------------------------------------------------------------
# Refusal paths
# ----------------------------------------------------------------------


class RefusalTests(unittest.TestCase):
    def test_refuses_blocked_fantriac_config(self) -> None:
        # FanTRIAC is status: blocked (TRIAC-REBLOCK-PINMAP-001 +
        # TRIAC-PINMAP-CORRECT-001 keep it blocked); the generator refuses
        # blocked entries (not WebFlash-shippable), so generation fails citing
        # the status.
        with self.assertRaises(gen.GeneratorError) as ctx:
            _generate_release_one(
                config_string=FANTRIAC_BLOCKED_CONFIG, channel="stable"
            )
        self.assertIn("blocked", str(ctx.exception).lower())

    def test_refuses_legacy_compatible_product(self) -> None:
        with self.assertRaises(gen.GeneratorError) as ctx:
            _generate_release_one(config_string=LEGACY_CONFIG_ID, channel="stable")
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
                                "Sense360-Ceiling-USB-AirIQ-" "v0.9.0-preview.bin"
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
                                "Sense360-Ceiling-USB-AirIQ-" "v0.9.0-preview.bin"
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
        body = _generate_release_one(changelog="Real change one\nReal change two")
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
            _generate_release_one(changelog="x", changelog_file=Path("/tmp/no"))


# ----------------------------------------------------------------------
# Semicolon / newline bullet splitting (single-line workflow_dispatch UI)
# ----------------------------------------------------------------------


class ChangelogBulletSplitTests(unittest.TestCase):
    """The GitHub workflow_dispatch ``changelog`` input is type:string,
    rendered single-line, so pasted newlines collapse into spaces. The
    generator must therefore split on a ';' separator as well as newlines
    so a single-line operator input still yields multiple bullets."""

    def test_semicolon_separated_single_line_yields_multiple_bullets(self) -> None:
        body = _generate_release_one(changelog="A; B; C")
        bullets = _section_bullets(body, "Changelog")
        self.assertEqual(bullets, ["A", "B", "C"])

    def test_newline_separated_yields_same_bullets(self) -> None:
        body = _generate_release_one(changelog="A\nB\nC")
        bullets = _section_bullets(body, "Changelog")
        self.assertEqual(bullets, ["A", "B", "C"])

    def test_semicolon_separated_strips_leading_markers(self) -> None:
        body = _generate_release_one(changelog="- A; * B; + C")
        bullets = _section_bullets(body, "Changelog")
        self.assertEqual(bullets, ["A", "B", "C"])

    def test_mixed_semicolon_and_newline_separators(self) -> None:
        body = _generate_release_one(changelog="- A; B\nC; - D")
        bullets = _section_bullets(body, "Changelog")
        self.assertEqual(bullets, ["A", "B", "C", "D"])

    def test_leading_trailing_and_blank_segments_dropped(self) -> None:
        body = _generate_release_one(changelog="; A ;; B ; ")
        bullets = _section_bullets(body, "Changelog")
        self.assertEqual(bullets, ["A", "B"])

    def test_realistic_single_line_operator_input(self) -> None:
        body = _generate_release_one(
            changelog="First stable release; No functional changes since 1.0.0"
        )
        bullets = _section_bullets(body, "Changelog")
        self.assertEqual(
            bullets,
            ["First stable release", "No functional changes since 1.0.0"],
        )

    def test_changelog_file_semicolon_split_still_applies(self) -> None:
        # The semicolon split is additive for the file path too; a newline
        # file with no semicolons keeps its existing per-line behaviour.
        with tempfile.NamedTemporaryFile(
            "w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write("- Bullet one\n- Bullet two\n")
            f_path = Path(f.name)
        try:
            body = _generate_release_one(changelog_file=f_path)
            bullets = _section_bullets(body, "Changelog")
            self.assertEqual(bullets, ["Bullet one", "Bullet two"])
        finally:
            try:
                f_path.unlink()
            except OSError:
                pass


# ----------------------------------------------------------------------
# --output writes a file
# ----------------------------------------------------------------------


class OutputFileTests(unittest.TestCase):
    def test_output_flag_writes_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "notes.md"
            rc = gen.main(
                [
                    "--config-string",
                    RELEASE_ONE_CONFIG_STRING,
                    "--version",
                    RELEASE_ONE_VERSION,
                    "--channel",
                    RELEASE_ONE_CHANNEL,
                    "--output",
                    str(out),
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(out.is_file(), f"{out} should have been written")
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
                    "--config-string",
                    RELEASE_ONE_CONFIG_STRING,
                    "--version",
                    RELEASE_ONE_VERSION,
                    "--channel",
                    RELEASE_ONE_CHANNEL,
                    "--output",
                    str(out),
                    "--validate",
                ]
            )
            self.assertEqual(rc, 0, "expected --validate to return 0 on Release-One")


if __name__ == "__main__":
    unittest.main(verbosity=2)

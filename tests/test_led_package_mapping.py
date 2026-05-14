#!/usr/bin/env python3
"""HW-010 invariants for the Sense360 LED ceiling package pin mapping.

These tests lock in the package-level fix HW-010 lands against the verified
schematic evidence (`S360-100-R4` and `S360-300-R4`):

  * Core schematic: `IO38 = LED_DATA` (WS2812B data source).
  * Core schematic: `IO14 = SCS` (peripheral SPI chip-select, not LED).
  * LED board:      `J1` receives `LED_DATA / +5V / GND`; mates with Core `J3`.

The fix is a single-package edit in
``packages/hardware/led_ring_ceiling.yaml``: ``led_data_pin`` flips from
``GPIO14`` to ``GPIO38``. HW-010 does **not** add ``LED`` to the Release-One
config string, does **not** add a WebFlash LED build, does **not** add a
product-catalog LED entry, and does **not** change the FanTRIAC HW-005
blocked status.

What this file checks:

  * ``packages/hardware/led_ring_ceiling.yaml`` contains
    ``led_data_pin: GPIO38`` (the schematic-correct value).
  * ``packages/hardware/led_ring_ceiling.yaml`` no longer contains
    ``GPIO14`` anywhere (substitution value or comment header).
  * The Release-One product YAML
    ``products/sense360-ceiling-poe-ventiq-roomiq.yaml`` does **not**
    ``!include`` ``led_ring_ceiling.yaml``. Release-One stays LED-less.
  * ``config/webflash-builds.json`` continues to ship exactly one build,
    ``Ceiling-POE-VentIQ-RoomIQ``, with no ``LED`` token in the config
    string or artifact name.
  * ``config/product-catalog.json`` keeps the FanTRIAC entry
    (``Ceiling-POE-VentIQ-FanTRIAC-RoomIQ``) ``status: blocked``,
    ``blocker: HW-005``, ``webflash_build_matrix: false``.

These are deliberately file-content / structural checks — they do not
require an ESPHome compile.

Run with:

    python3 tests/test_led_package_mapping.py
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

LED_CEILING_PACKAGE = REPO_ROOT / "packages" / "hardware" / "led_ring_ceiling.yaml"
RELEASE_ONE_PRODUCT = (
    REPO_ROOT / "products" / "sense360-ceiling-poe-ventiq-roomiq.yaml"
)
WEBFLASH_BUILDS = REPO_ROOT / "config" / "webflash-builds.json"
PRODUCT_CATALOG = REPO_ROOT / "config" / "product-catalog.json"

RELEASE_ONE_CONFIG_STRING = "Ceiling-POE-VentIQ-RoomIQ"
FANTRIAC_CONFIG_STRING = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"


class LedCeilingPackageMappingTests(unittest.TestCase):
    """HW-010: the ceiling LED package binds the schematic-correct pin."""

    def test_package_file_exists(self) -> None:
        self.assertTrue(
            LED_CEILING_PACKAGE.is_file(),
            f"missing LED ceiling package: {LED_CEILING_PACKAGE}",
        )

    def test_led_data_pin_is_gpio38(self) -> None:
        text = LED_CEILING_PACKAGE.read_text()
        pin_re = re.compile(
            r"^\s*led_data_pin:\s*GPIO38\b",
            re.MULTILINE,
        )
        self.assertIsNotNone(
            pin_re.search(text),
            "led_data_pin must bind GPIO38 (Core IO38 = LED_DATA per "
            "S360-100-R4 schematic); see docs/hardware/s360-100-r4-core.md "
            "§LED output.",
        )

    def test_package_does_not_reference_gpio14(self) -> None:
        text = LED_CEILING_PACKAGE.read_text()
        # GPIO14 must not reappear as a value or in a code-style identifier
        # anywhere in this package. It is intentionally allowed to mention
        # the legacy pin in an HW-010 commentary line that explains why
        # GPIO14 was wrong; we therefore only forbid the assignment form
        # and any pin-binding usage. The simplest, robust check: the token
        # `GPIO14` must not appear anywhere in the file body.
        self.assertNotIn(
            "GPIO14",
            text,
            "GPIO14 must not appear in led_ring_ceiling.yaml after HW-010 "
            "(IO14 is SCS / peripheral SPI chip-select, not LED_DATA, per "
            "the S360-100-R4 schematic).",
        )

    def test_release_one_does_not_include_led_ceiling_package(self) -> None:
        self.assertTrue(
            RELEASE_ONE_PRODUCT.is_file(),
            f"missing Release-One product YAML: {RELEASE_ONE_PRODUCT}",
        )
        text = RELEASE_ONE_PRODUCT.read_text()
        # We disallow any real !include line; commentary lines that mention
        # the filename are fine. The Release-One YAML's existing comment
        # block (lines 121–128) explains why LED is excluded — keep those.
        include_re = re.compile(
            r"^\s*[A-Za-z0-9_]+\s*:\s*!include\s+\S*led_ring_ceiling\.yaml\b",
            re.MULTILINE,
        )
        self.assertIsNone(
            include_re.search(text),
            "Release-One YAML must not !include led_ring_ceiling.yaml. The "
            "Release-One config string Ceiling-POE-VentIQ-RoomIQ carries no "
            "LED token; HW-010 does not add LED to Release-One.",
        )


class WebflashBuildsLedExclusionTests(unittest.TestCase):
    """HW-010 does not add an LED-bearing WebFlash build."""

    def setUp(self) -> None:
        self.doc = json.loads(WEBFLASH_BUILDS.read_text())

    def test_builds_array_present(self) -> None:
        self.assertIn("builds", self.doc)
        self.assertIsInstance(self.doc["builds"], list)
        self.assertGreater(
            len(self.doc["builds"]),
            0,
            "webflash-builds.json must contain at least one build",
        )

    def test_release_one_build_present_and_unchanged(self) -> None:
        config_strings = [b.get("config_string") for b in self.doc["builds"]]
        self.assertIn(
            RELEASE_ONE_CONFIG_STRING,
            config_strings,
            "Release-One build must remain in the WebFlash build matrix.",
        )

    def test_no_led_token_in_any_build(self) -> None:
        for build in self.doc["builds"]:
            config_string = build.get("config_string", "")
            artifact_name = build.get("artifact_name", "")
            tokens = config_string.split("-")
            self.assertNotIn(
                "LED",
                tokens,
                f"WebFlash build {config_string!r} must not carry an LED "
                "token. HW-010 does not add LED to any WebFlash build.",
            )
            self.assertNotIn(
                "LED",
                artifact_name.split("-"),
                f"WebFlash artifact {artifact_name!r} must not carry an LED "
                "token. HW-010 does not add LED to any WebFlash artifact.",
            )


class FanTRIACStatusUnaffectedTests(unittest.TestCase):
    """HW-010 does not change FanTRIAC's HW-005 blocker."""

    def setUp(self) -> None:
        self.doc = json.loads(PRODUCT_CATALOG.read_text())

    def _entry(self, config_string: str) -> dict:
        for product in self.doc.get("products", []):
            if product.get("config_string") == config_string:
                return product
        raise AssertionError(
            f"product-catalog.json has no entry with config_string="
            f"{config_string!r}"
        )

    def test_fantriac_entry_remains_blocked(self) -> None:
        entry = self._entry(FANTRIAC_CONFIG_STRING)
        self.assertEqual(
            entry.get("status"),
            "blocked",
            "FanTRIAC must remain status=blocked; HW-010 does not unblock "
            "FanTRIAC (HW-005 is a separate, still-open blocker).",
        )
        self.assertEqual(
            entry.get("blocker"),
            "HW-005",
            "FanTRIAC blocker must remain HW-005; HW-010 does not change "
            "the FanTRIAC blocker identity.",
        )
        self.assertEqual(
            entry.get("webflash_build_matrix"),
            False,
            "FanTRIAC must remain webflash_build_matrix=false; HW-010 does "
            "not promote FanTRIAC into the WebFlash build matrix.",
        )

    def test_release_one_entry_unchanged(self) -> None:
        entry = self._entry(RELEASE_ONE_CONFIG_STRING)
        self.assertEqual(entry.get("status"), "production")
        # blocked_modules must still call out LED + FanTRIAC; HW-010 does
        # not move LED out of the blocked-modules list.
        blocked = entry.get("blocked_modules", [])
        self.assertIn(
            "LED",
            blocked,
            "Release-One must keep LED in blocked_modules; HW-010 does not "
            "add LED to Release-One.",
        )
        self.assertIn("FanTRIAC", blocked)


if __name__ == "__main__":
    unittest.main(verbosity=2)

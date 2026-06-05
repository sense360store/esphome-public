#!/usr/bin/env python3
"""HW-010 invariants for the Sense360 LED ceiling package pin mapping
plus PRODUCT-009 scoping of LED exclusion to stable Release-One.

These tests lock in the package-level fix HW-010 lands against the verified
schematic evidence (`S360-100-R4` and `S360-300-R4`):

  * Core schematic: `IO38 = LED_DATA` (WS2812B data source).
  * Core schematic: `IO14 = SCS` (peripheral SPI chip-select, not LED).
  * LED board:      `J1` receives `LED_DATA / +5V / GND`; mates with Core `J3`.

The fix is a single-package edit in
``packages/hardware/led_ring_ceiling.yaml``: ``led_data_pin`` flips from
``GPIO14`` to ``GPIO38``. HW-010 does **not** add ``LED`` to the Release-One
config string and does **not** change the FanTRIAC HW-005 blocked status.

After PRODUCT-009 the WebFlash build matrix is allowed to carry a
**non-stable** LED-bearing preview build alongside the Release-One stable
build. The LED-exclusion guarantee is therefore scoped to the
**stable** channel (Release-One) only: stable builds must remain
LED-less, but a preview build may carry the ``LED`` token if it points
at the LED wrapper.

What this file checks:

  * ``packages/hardware/led_ring_ceiling.yaml`` contains
    ``led_data_pin: GPIO38`` (the schematic-correct value).
  * ``packages/hardware/led_ring_ceiling.yaml`` no longer contains
    ``GPIO14`` anywhere (substitution value or comment header).
  * The Release-One product YAML
    ``products/sense360-ceiling-poe-ventiq-roomiq.yaml`` does **not**
    ``!include`` ``led_ring_ceiling.yaml``. Release-One stays LED-less.
  * ``config/webflash-builds.json`` still contains the Release-One
    stable build ``Ceiling-POE-VentIQ-RoomIQ`` with no ``LED`` token in
    its config string or artifact name.
  * Every **stable** build in ``config/webflash-builds.json`` is
    LED-less (no ``LED`` token in config_string or artifact_name).
  * Any LED-bearing build in ``config/webflash-builds.json`` is
    **non-stable** (channel != ``stable``) and points at the LED
    WebFlash wrapper ``products/webflash/ceiling-poe-ventiq-roomiq-led.yaml``.
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

# PACKAGE-RENAME-001 (docs/arch-board-bundle-plan.md §5.5): the authoritative,
# self-contained ceiling LED definition moved from
# `packages/hardware/led_ring_ceiling.yaml` (now a thin alias) into the
# SKU-aligned board package below. The content-asserting checks travel with
# the content, so they now target the board package.
LED_CEILING_PACKAGE = REPO_ROOT / "packages" / "boards" / "s360-300-led.yaml"
RELEASE_ONE_PRODUCT = REPO_ROOT / "products" / "sense360-ceiling-poe-ventiq-roomiq.yaml"
WEBFLASH_BUILDS = REPO_ROOT / "config" / "webflash-builds.json"
PRODUCT_CATALOG = REPO_ROOT / "config" / "product-catalog.json"

RELEASE_ONE_CONFIG_STRING = "Ceiling-POE-VentIQ-RoomIQ"
FANTRIAC_CONFIG_STRING = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"
LED_PREVIEW_CONFIG_STRING = "Ceiling-POE-VentIQ-RoomIQ-LED"
LED_PREVIEW_WRAPPER = "products/webflash/ceiling-poe-ventiq-roomiq-led.yaml"


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
    """LED exclusion is scoped to the stable Release-One build only.

    HW-010 did not add any LED-bearing WebFlash build. PRODUCT-009 added a
    **non-stable** LED-bearing preview build alongside the Release-One
    stable build. The LED-exclusion guarantee is therefore scoped to
    stable channels (Release-One). Stable builds must remain LED-less;
    LED-bearing builds must be non-stable and must point at the LED
    WebFlash wrapper.
    """

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

    def test_release_one_build_is_stable_and_led_less(self) -> None:
        matches = [
            b
            for b in self.doc["builds"]
            if b.get("config_string") == RELEASE_ONE_CONFIG_STRING
        ]
        self.assertEqual(
            len(matches),
            1,
            "expected exactly one Release-One build entry",
        )
        entry = matches[0]
        self.assertEqual(
            entry.get("channel"),
            "stable",
            "Release-One build must remain on the 'stable' channel.",
        )
        tokens = entry.get("config_string", "").split("-")
        self.assertNotIn(
            "LED",
            tokens,
            "Release-One config string must not carry an LED token.",
        )
        self.assertNotIn(
            "LED",
            entry.get("artifact_name", "").split("-"),
            "Release-One artifact name must not carry an LED token.",
        )

    def test_stable_channel_builds_have_no_led_token(self) -> None:
        for build in self.doc["builds"]:
            if build.get("channel") != "stable":
                continue
            config_string = build.get("config_string", "")
            artifact_name = build.get("artifact_name", "")
            with self.subTest(config_string=config_string):
                tokens = config_string.split("-")
                self.assertNotIn(
                    "LED",
                    tokens,
                    f"Stable WebFlash build {config_string!r} must not "
                    "carry an LED token. LED is reserved for non-stable "
                    "(preview / beta) channels until a stable build / "
                    "release proof has been recorded.",
                )
                self.assertNotIn(
                    "LED",
                    artifact_name.split("-"),
                    f"Stable WebFlash artifact {artifact_name!r} must not "
                    "carry an LED token.",
                )

    def test_led_preview_build_is_non_stable(self) -> None:
        for build in self.doc["builds"]:
            config_string = build.get("config_string", "")
            if "LED" not in config_string.split("-"):
                continue
            with self.subTest(config_string=config_string):
                channel = build.get("channel")
                self.assertNotEqual(
                    channel,
                    "stable",
                    f"LED-bearing build {config_string!r} is on the "
                    f"'stable' channel; LED-bearing builds must be on a "
                    "non-stable channel (e.g. 'preview' or 'beta') until "
                    "a stable build / release proof has been recorded.",
                )

    def test_led_preview_build_uses_led_wrapper(self) -> None:
        # Each LED-bearing build must point at its OWN products/webflash LED
        # wrapper (basename == lowercased config string). RELEASE-PREVIEW-
        # WEBFLASH-BUILD-ROWS-001 added Ceiling-POE-RoomIQ-LED alongside the
        # published Ceiling-POE-VentIQ-RoomIQ-LED, so there is no longer a
        # single shared LED wrapper.
        for build in self.doc["builds"]:
            config_string = build.get("config_string", "")
            if "LED" not in config_string.split("-"):
                continue
            with self.subTest(config_string=config_string):
                product_yaml = build.get("product_yaml", "")
                expected = f"products/webflash/{config_string.lower()}.yaml"
                self.assertEqual(
                    product_yaml,
                    expected,
                    f"LED-bearing build {config_string!r} must point at its "
                    f"LED WebFlash wrapper {expected!r}.",
                )
                self.assertTrue(
                    (REPO_ROOT / product_yaml).is_file(),
                    f"LED wrapper {product_yaml!r} must exist on disk.",
                )


class FanTRIACStatusUnaffectedTests(unittest.TestCase):
    """HW-010 does not change FanTRIAC's exposure posture.

    TRIAC-UNBLOCK-BUILD-001 (a separate PR) moved FanTRIAC from status: blocked
    / HW-005 to status: compile-only (HW-005 BUILDABILITY resolved by the
    SX1509-free Core respin). HW-010 (LED) does not touch FanTRIAC; the
    preserved invariant is that FanTRIAC stays off the WebFlash build matrix and
    stable stays gated by COMPLIANCE-001.
    """

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
            "FanTRIAC is status=blocked (TRIAC-PINMAP-CORRECT-001 corrected "
            "the pins but the product stays blocked); HW-010 (LED) does not "
            "change the FanTRIAC posture.",
        )
        self.assertIn(
            "COMPLIANCE-001",
            entry.get("blocker", ""),
            "FanTRIAC must stay gated by COMPLIANCE-001; HW-010 does "
            "not clear the mains-voltage compliance gate.",
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

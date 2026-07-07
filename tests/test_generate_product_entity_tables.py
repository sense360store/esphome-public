#!/usr/bin/env python3
"""Tests for the product entity-table generator (PRODUCT-GUIDES-001 G1).

Covers ``scripts/generate_product_entity_tables.py`` — the mechanical
derivation of customer-facing Home Assistant entity tables from the served
products' YAML composition — and the freshness of the committed tables
under ``site/generated/``.

Uses Python's stdlib unittest (matching this repo's no-pytest convention
for Python validators). Run with::

    python3 tests/test_generate_product_entity_tables.py

or::

    python3 -m unittest tests.test_generate_product_entity_tables -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import generate_product_entity_tables as gpet  # noqa: E402

EXPECTED_SERVED_CONFIGS = (
    "Ceiling-POE-RoomIQ",
    "Ceiling-POE-AirIQ-RoomIQ",
    "Ceiling-POE-VentIQ-RoomIQ",
    "Ceiling-POE-VentIQ-RoomIQ-LED",
)


class TestServedConfigScope(unittest.TestCase):
    """The generator covers exactly the PRODUCT-GUIDES-001 served set."""

    def test_served_config_strings(self):
        self.assertEqual(tuple(gpet.SERVED_CONFIG_STRINGS), EXPECTED_SERVED_CONFIGS)

    def test_every_served_config_has_a_build_row_and_yaml(self):
        rows = gpet.load_build_rows()
        for config_string in gpet.SERVED_CONFIG_STRINGS:
            with self.subTest(config=config_string):
                self.assertIn(config_string, rows)
                product_yaml = REPO_ROOT / rows[config_string]["product_yaml"]
                self.assertTrue(
                    product_yaml.is_file(),
                    f"{product_yaml} missing for {config_string}",
                )


class TestNameRendering(unittest.TestCase):
    def test_friendly_name_prefix_is_stripped(self):
        self.assertEqual(
            gpet._render_name("${friendly_name} Temperature", {}),
            "Temperature",
        )

    def test_other_substitutions_resolve_from_context(self):
        self.assertEqual(
            gpet._render_name("${friendly_name} ${zone} Level", {"zone": "PM"}),
            "PM Level",
        )

    def test_unknown_substitutions_are_left_verbatim(self):
        self.assertEqual(gpet._render_name("${mystery} Level", {}), "${mystery} Level")


class TestDerivedTables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = {
            path.name: content for path, content in gpet.expected_outputs().items()
        }

    def test_one_table_per_served_config(self):
        self.assertEqual(
            sorted(self.outputs),
            sorted(f"{c.lower()}-entities.md" for c in EXPECTED_SERVED_CONFIGS),
        )

    def test_generation_is_deterministic(self):
        second = {
            path.name: content for path, content in gpet.expected_outputs().items()
        }
        self.assertEqual(self.outputs, second)

    def test_tables_carry_the_generated_banner(self):
        for name, content in self.outputs.items():
            with self.subTest(file=name):
                self.assertIn("AUTO-GENERATED — DO NOT EDIT", content)
                self.assertIn("scripts/generate_product_entity_tables.py", content)

    def test_exposed_entities_are_listed(self):
        ventiq = self.outputs["ceiling-poe-ventiq-roomiq-entities.md"]
        self.assertIn("| RoomIQ Temperature | Sensor | °C |", ventiq)
        self.assertIn("| Shower Active | Binary sensor |", ventiq)
        self.assertIn("| Relay | Switch |", ventiq)
        self.assertIn("| WebFlash Config | Text sensor |", ventiq)

    def test_internal_entities_are_excluded(self):
        # The raw board measurements are internal: true — never HA-exposed.
        ventiq = self.outputs["ceiling-poe-ventiq-roomiq-entities.md"]
        self.assertNotIn("| Illuminance |", ventiq)
        airiq = self.outputs["ceiling-poe-airiq-roomiq-entities.md"]
        self.assertNotIn("| CO2 |", airiq)
        self.assertNotIn("| PM2.5 |", airiq)

    def test_led_variant_adds_the_led_entities(self):
        led = self.outputs["ceiling-poe-ventiq-roomiq-led-entities.md"]
        base = self.outputs["ceiling-poe-ventiq-roomiq-entities.md"]
        self.assertIn("| LED Ring | Light |", led)
        self.assertIn("| Night Mode | Switch |", led)
        self.assertNotIn("| LED Ring | Light |", base)

    def test_default_units_applied_for_known_platforms(self):
        roomiq = self.outputs["ceiling-poe-roomiq-entities.md"]
        self.assertIn("| WiFi Signal | Sensor | dBm |", roomiq)
        self.assertIn("| Internal Temperature | Sensor | °C |", roomiq)


class TestFreshnessGate(unittest.TestCase):
    def test_committed_tables_are_fresh(self):
        # The committed site/generated/*.md must byte-match regeneration —
        # the same gate CI and the local gate run via --check.
        self.assertEqual(gpet.check_outputs(), 0)


if __name__ == "__main__":
    unittest.main()

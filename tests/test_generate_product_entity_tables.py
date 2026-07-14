#!/usr/bin/env python3
"""Tests for the product entity-table generator (PRODUCT-GUIDES-001 G1+G2).

Covers ``scripts/generate_product_entity_tables.py`` — the mechanical
derivation of customer-facing Home Assistant entity tables from the served
products' YAML composition, plus (G2) the four-product comparison matrix —
and the freshness of the committed tables under ``site/generated/``.

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

    def test_one_table_per_served_config_plus_compare_matrix(self):
        expected = {f"{c.lower()}-entities.md" for c in EXPECTED_SERVED_CONFIGS}
        expected.add(gpet.COMPARE_OUTPUT_NAME)
        self.assertEqual(sorted(self.outputs), sorted(expected))

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
        # (ROOMIQ-FRAMEWORK-001: "Illuminance" is now the CALIBRATED
        # canonical customer entity, so the internal-leak canaries are the
        # driver-internal VEML7700 channels instead.)
        ventiq = self.outputs["ceiling-poe-ventiq-roomiq-entities.md"]
        self.assertNotIn("| ALS Counts |", ventiq)
        self.assertNotIn("| Full Spectrum |", ventiq)
        self.assertNotIn("| ALS Interrupt |", ventiq)
        # (AIRIQ-FRAMEWORK-001: "CO2" / "PM2.5" are now the canonical
        # customer entities, so the internal-leak canaries are the
        # driver-internal SCD41/BMP390/SPS30 channels instead.)
        airiq = self.outputs["ceiling-poe-airiq-roomiq-entities.md"]
        self.assertNotIn("| SCD41 Temperature |", airiq)
        self.assertNotIn("| BMP390 Temperature |", airiq)
        self.assertNotIn("| Typical Particle Size |", airiq)
        self.assertNotIn("| PMC 0.5 |", airiq)

    def test_led_variant_adds_the_led_entities(self):
        led = self.outputs["ceiling-poe-ventiq-roomiq-led-entities.md"]
        base = self.outputs["ceiling-poe-ventiq-roomiq-entities.md"]
        self.assertIn("| Room Light | Light |", led)
        self.assertIn("| Night Mode | Switch |", led)
        self.assertNotIn("| Room Light | Light |", base)

    def test_default_units_applied_for_known_platforms(self):
        roomiq = self.outputs["ceiling-poe-roomiq-entities.md"]
        self.assertIn("| WiFi Signal | Sensor | dBm |", roomiq)
        self.assertIn("| Internal Temperature | Sensor | °C |", roomiq)


class TestCompareMatrix(unittest.TestCase):
    """The G2 comparison matrix: derived from the catalog, the build
    matrix, and the same entity sets the tables come from."""

    @classmethod
    def setUpClass(cls):
        outputs = gpet.expected_outputs()
        cls.matrix = outputs[gpet.OUTPUT_DIR / gpet.COMPARE_OUTPUT_NAME]
        cls.rows = {
            line.split(" | ")[0].lstrip("| "): line
            for line in cls.matrix.splitlines()
            if line.startswith("|")
        }

    def test_matrix_is_in_expected_outputs(self):
        self.assertIn("AUTO-GENERATED — DO NOT EDIT", self.matrix)

    def test_every_served_config_is_a_column(self):
        for config_string in EXPECTED_SERVED_CONFIGS:
            with self.subTest(config=config_string):
                self.assertIn(f"`{config_string}`", self.matrix)
                # Column headers link to the guide page for the product, as
                # an absolute deployed-site URL: the committed snippet is
                # link-checked standalone from site/generated/, where a
                # page-relative link would be a dead path (see SITE_BASE_URL
                # in the generator).
                self.assertIn(
                    f"({gpet.SITE_BASE_URL}products/{config_string.lower()}/)",
                    self.matrix,
                )

    def test_channel_row_matches_the_build_matrix(self):
        build_rows = gpet.load_build_rows()
        channel_row = self.rows["**Channel / version**"]
        for config_string in EXPECTED_SERVED_CONFIGS:
            build = build_rows[config_string]
            with self.subTest(config=config_string):
                self.assertIn(f"s360-badge--{build['channel']}", channel_row)
                self.assertIn(f"v{build['version']}", channel_row)

    def test_module_rows_come_from_the_catalog(self):
        self.assertIn("VentIQ (S360-211)", self.rows["**Air-quality module**"])
        self.assertIn("AirIQ (S360-210)", self.rows["**Air-quality module**"])
        self.assertEqual(
            self.rows["**Room-sensing module**"].count("RoomIQ (S360-200)"), 4
        )
        led_cells = self.rows["**LED module**"].split(" | ")[1:]
        self.assertEqual(
            [c.strip(" |") for c in led_cells],
            ["—", "—", "—", "LED (S360-300)"],
        )

    def _cells(self, label):
        return [c.strip(" |") for c in self.rows[label].split(" | ")[1:]]

    def test_capability_cells_track_the_derived_entities(self):
        # Column order is SERVED_CONFIG_STRINGS: RoomIQ, AirIQ+RoomIQ,
        # VentIQ+RoomIQ, VentIQ+RoomIQ+LED.
        self.assertEqual(
            self._cells("Presence detection (radar)"), ["✓", "✓", "✓", "✓"]
        )
        self.assertEqual(self._cells("Shower detection"), ["—", "—", "✓", "✓"])
        self.assertEqual(self._cells("LED ring light"), ["—", "—", "—", "✓"])

    def test_airiq_placeholder_never_counts_as_air_quality(self):
        # The legacy AirIQ profile's "Air Quality State" text sensor was a
        # placeholder that always read "unknown" and never counted here.
        # AIRIQ-FRAMEWORK-001 gives the AirIQ product a REAL "Air Quality"
        # headline (worst-pollutant model), so the AirIQ column is now a
        # genuine ✓ — driven by the canonical entity, not the placeholder
        # (which survives only as a disabled-by-default compatibility
        # entity named "Air Quality State").
        self.assertEqual(self._cells("Air-quality summary"), ["—", "✓", "✓", "✓"])
        self.assertEqual(self._cells("CO2"), ["—", "✓", "—", "—"])
        # PM row: the label carries the external-SPS30 caveat because the
        # module's commercial inclusion is not declared — the ✓ states
        # firmware support only (entity ships disabled by default).
        self.assertEqual(
            self._cells("Particulate matter (PM2.5, needs external SPS30 module)"),
            ["—", "✓", "—", "—"],
        )
        self.assertEqual(self._cells("VOC index"), ["—", "✓", "✓", "✓"])

    def test_entity_count_row_matches_the_tables(self):
        outputs = {
            path.name: content for path, content in gpet.expected_outputs().items()
        }
        counts = self._cells("**Home Assistant entities**")
        for config_string, count in zip(EXPECTED_SERVED_CONFIGS, counts):
            table = outputs[f"{config_string.lower()}-entities.md"]
            with self.subTest(config=config_string):
                self.assertIn(f"exposes **{count} entities**", table)


class TestFreshnessGate(unittest.TestCase):
    def test_committed_tables_are_fresh(self):
        # The committed site/generated/*.md must byte-match regeneration —
        # the same gate CI and the local gate run via --check.
        self.assertEqual(gpet.check_outputs(), 0)


if __name__ == "__main__":
    unittest.main()

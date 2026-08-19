#!/usr/bin/env python3
"""Customer entity surface contract (SENSE360-REVIEW-RELEASE-001, Gate B).

Pins what a customer sees by default in Home Assistant for each served
configuration, per docs/architecture/sense360-customer-entity-surface.md.

The contract is about PRESENTATION only. Every entity that existed before
still exists; these tests assert which Home Assistant panel it lands in:

- customer default — enabled, no effective entity_category;
- advanced       — effective entity_category diagnostic or config;
- opt-in         — disabled_by_default.

"Effective" category is the YAML entity_category, or the default the
ESPHome platform applies when YAML declares none (carried by the
generator in PLATFORM_DEFAULT_ENTITY_CATEGORY). Reading YAML alone
misreports ten device-health entities as customer-facing.

Two exclusions are evidence gates, not hardware claims. Formaldehyde is
excluded while SFA40 production population is an open bench item (SOT
OD-SOT-008); radar-derived entities are excluded while radar attachment
inclusion is unresolved (SOT OD-SOT-004). Neither exclusion asserts that
any part is present or absent, and neither resolves an owner decision.

Uses Python's stdlib unittest (repo convention). Run with::

    python3 tests/test_customer_entity_surface.py
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import generate_product_entity_tables as gen  # noqa: E402

REVIEW_CONFIG = "Ceiling-POE-AirIQ-RoomIQ"

# The customer-default surface of the review composition, verbatim from
# the architecture record. Exact-set equality: an addition is as much a
# regression as a removal.
REVIEW_CUSTOMER_DEFAULT = {
    # presence
    "Occupancy",
    # room climate
    "Temperature",
    "Humidity",
    "Pressure",
    # light
    "Illuminance",
    "Brightness",
    # derived room state
    "Comfort",
    "Environment State",
    # air quality
    "CO2",
    "VOC",
    "NOx",
    "Air Quality",
    "Recommendation",
}

# Device-health and device-management entities: available, never leading.
NEVER_CUSTOMER_DEFAULT = {
    "ESPHome Version",
    "IP Address",
    "MAC Address",
    "SSID",
    "WiFi Signal",
    "Uptime",
    "Internal Temperature",
    "Status",
    "Supply Voltage",
    "Power Source",
    "PoE Power Connected",
    "Restart",
    "Safe Mode",
    "Factory Reset",
    "Relay",
}

# Evidence-gated capability. Excluded from the customer default surface of
# EVERY served configuration while the owner decision behind it is open.
EVIDENCE_GATED = {
    "Formaldehyde": "OD-SOT-008 (SFA40 production population unresolved)",
    # Presence Status reads "Sensor degraded" rather than "Clear" on a unit
    # whose radar connector is unpopulated, because the canonical package
    # expects radar and PD-02 puts HEALTH_DEGRADED above STATUS_CLEAR.
    # Proven in tests/unit/test_presence_fusion.cpp.
    "Presence Status": "OD-SOT-004 (radar attachment inclusion unresolved)",
}
RADAR_PREFIX = "Radar "  # OD-SOT-004 (radar attachment inclusion unresolved)


def surface(config_string):
    """Deduplicated entity list for a config, with effective category."""
    collector = gen.collect_for_config(config_string)
    seen = set()
    entities = []
    for entity in collector.entities:
        key = (entity["type"], entity["name"])
        if key in seen:
            continue
        seen.add(key)
        entities.append(entity)
    return entities


def customer_default(entities):
    return {
        e["name"]
        for e in entities
        if not e["disabled_by_default"] and not e["effective_entity_category"]
    }


class TestEffectiveCategoryIsModelled(unittest.TestCase):
    """The generator must know the ESPHome platform defaults, or every
    check below silently measures the wrong thing."""

    def test_platform_defaults_are_declared(self):
        defaults = gen.PLATFORM_DEFAULT_ENTITY_CATEGORY
        for platform in ("status", "wifi_signal", "wifi_info", "version",
                         "uptime", "internal_temperature"):
            self.assertEqual(defaults.get(platform), "diagnostic", platform)
        for platform in ("restart", "safe_mode", "factory_reset"):
            self.assertEqual(defaults.get(platform), "config", platform)

    def test_effective_category_is_recorded_per_entity(self):
        for entity in surface(REVIEW_CONFIG):
            self.assertIn("effective_entity_category", entity)

    def test_yaml_category_wins_over_platform_default(self):
        for entity in surface(REVIEW_CONFIG):
            if entity["entity_category"]:
                self.assertEqual(
                    entity["effective_entity_category"],
                    entity["entity_category"],
                    entity["name"],
                )


class TestReviewCompositionSurface(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entities = surface(REVIEW_CONFIG)

    def test_customer_default_surface_is_exact(self):
        self.assertEqual(customer_default(self.entities), REVIEW_CUSTOMER_DEFAULT)

    def test_every_desired_customer_outcome_is_present(self):
        """The reviewer must be able to read the product proposition off
        the default panel: presence, climate, light, air quality."""
        names = customer_default(self.entities)
        for required in ("Occupancy", "Temperature", "Humidity",
                         "Illuminance", "CO2", "Air Quality"):
            self.assertIn(required, names)

    def test_no_device_health_or_management_entity_leads(self):
        leaked = customer_default(self.entities) & NEVER_CUSTOMER_DEFAULT
        self.assertEqual(leaked, set(), f"engineering entities leaked: {leaked}")


class TestEvidenceGatedCapability(unittest.TestCase):
    """Applies to every served configuration, not just the review one."""

    def test_formaldehyde_is_never_customer_default(self):
        for config_string in gen.SERVED_CONFIG_STRINGS:
            names = customer_default(surface(config_string))
            for name, reason in EVIDENCE_GATED.items():
                self.assertNotIn(name, names, f"{config_string}: {name} — {reason}")

    def test_formaldehyde_is_diagnostic_and_opt_in_where_it_exists(self):
        found = False
        for config_string in gen.SERVED_CONFIG_STRINGS:
            for entity in surface(config_string):
                if entity["name"] != "Formaldehyde":
                    continue
                found = True
                self.assertEqual(
                    entity["effective_entity_category"], "diagnostic",
                    config_string,
                )
                self.assertTrue(entity["disabled_by_default"], config_string)
        self.assertTrue(found, "Formaldehyde must still exist — capability is preserved")

    def test_no_radar_entity_is_customer_default(self):
        for config_string in gen.SERVED_CONFIG_STRINGS:
            for name in customer_default(surface(config_string)):
                self.assertFalse(
                    name.startswith(RADAR_PREFIX),
                    f"{config_string}: radar entity {name!r} is customer-default "
                    f"while OD-SOT-004 is unresolved",
                )

    def test_every_radar_entity_is_diagnostic_and_opt_in(self):
        found = False
        for config_string in gen.SERVED_CONFIG_STRINGS:
            for entity in surface(config_string):
                if not entity["name"].startswith(RADAR_PREFIX):
                    continue
                found = True
                self.assertEqual(
                    entity["effective_entity_category"], "diagnostic",
                    f"{config_string}: {entity['name']}",
                )
                self.assertTrue(
                    entity["disabled_by_default"],
                    f"{config_string}: {entity['name']}",
                )
        self.assertTrue(found, "radar entities must still exist")

    def test_occupancy_carries_the_presence_story_alone(self):
        """Occupancy asserts from ANY valid sensor and stays correct with
        radar absent, so it remains the customer-facing presence signal.
        Presence Status does not: with radar expected but unpopulated it
        reports "Sensor degraded" rather than "Clear" whenever the room is
        empty, so it is gated with the other OD-SOT-004 entities."""
        names = customer_default(surface(REVIEW_CONFIG))
        self.assertIn("Occupancy", names)
        self.assertNotIn("Presence Status", names)

    def test_evidence_gated_entities_are_diagnostic_and_opt_in(self):
        """Every gated entity keeps its capability: still present, merely
        filed under Diagnostic and switched off until enabled."""
        for config_string in gen.SERVED_CONFIG_STRINGS:
            by_name = {e["name"]: e for e in surface(config_string)}
            for name in EVIDENCE_GATED:
                entity = by_name.get(name)
                if entity is None:
                    continue
                self.assertEqual(
                    entity["effective_entity_category"], "diagnostic",
                    f"{config_string}: {name}",
                )
                self.assertTrue(
                    entity["disabled_by_default"], f"{config_string}: {name}"
                )


class TestCoreRelay(unittest.TestCase):
    def test_relay_is_advanced_in_every_served_config(self):
        found = False
        for config_string in gen.SERVED_CONFIG_STRINGS:
            for entity in surface(config_string):
                if entity["name"] != "Relay":
                    continue
                found = True
                self.assertEqual(
                    entity["effective_entity_category"], "config", config_string
                )
                self.assertTrue(entity["disabled_by_default"], config_string)
        self.assertTrue(found, "the Core relay capability must be preserved")


class TestNothingWasDeleted(unittest.TestCase):
    """Recategorisation must not shrink the entity set. These totals are
    the pre-change counts; they may only change by a deliberate edit."""

    EXPECTED_TOTALS = {
        "Ceiling-POE-RoomIQ": 98,
        "Ceiling-POE-AirIQ-RoomIQ": 140,
        "Ceiling-POE-VentIQ-RoomIQ": 136,
        "Ceiling-POE-VentIQ-RoomIQ-LED": 148,
    }

    def test_entity_totals_are_unchanged(self):
        for config_string, expected in self.EXPECTED_TOTALS.items():
            self.assertEqual(len(surface(config_string)), expected, config_string)


if __name__ == "__main__":
    unittest.main(verbosity=2)

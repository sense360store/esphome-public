#!/usr/bin/env python3
"""CORE-BENCH-RUNTIME-EVIDENCE-001 — Core runtime-evidence record guards.

Pins the scoped evidence document
``docs/hardware/CORE-BENCH-RUNTIME-EVIDENCE-001.md``: it must record the
sanitised physical runtime-initialisation facts (PSRAM, I2C, UARTs, GPIO46,
GPIO3), state the PASS / PARTIAL-OPEN split, explicitly disclaim unproven
physical behaviour, contain no network identifiers or credentials, make no
release / safety / compliance / commercial claim, and leave
``config/hardware-catalog.json`` state untouched.

Uses Python's stdlib unittest (repo convention). Run with::

    python3 tests/test_core_bench_runtime_evidence.py
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOC_PATH = REPO_ROOT / "docs" / "hardware" / "CORE-BENCH-RUNTIME-EVIDENCE-001.md"
HARDWARE_CATALOG = REPO_ROOT / "config" / "hardware-catalog.json"


class CoreBenchRuntimeEvidenceTests(unittest.TestCase):
    """All assertions inspect the scoped evidence document only."""

    @classmethod
    def setUpClass(cls) -> None:
        assert DOC_PATH.is_file(), f"missing {DOC_PATH}"
        cls.text = DOC_PATH.read_text(encoding="utf-8")
        # Whitespace-normalised view so assertions survive markdown line wraps.
        cls.flat = re.sub(r"\s+", " ", cls.text)

    def test_record_exists_and_identifies_programme(self) -> None:
        self.assertIn("CORE-BENCH-RUNTIME-EVIDENCE-001", self.text)
        self.assertIn("runtime initialisation evidence", self.text)

    def test_pass_result_recorded(self) -> None:
        self.assertIn("PASS — Core package physical runtime initialisation", self.text)

    def test_overall_hardware_state_partial_open(self) -> None:
        self.assertIn("PARTIAL / OPEN", self.text)
        self.assertIn("not yet proven", self.text)

    def test_psram_evidence_recorded(self) -> None:
        self.assertIn("8192 KB", self.text)

    def test_i2c_runtime_pins_and_recovery(self) -> None:
        self.assertIn("GPIO48", self.text)
        self.assertIn("GPIO45", self.text)
        self.assertIn("400000", self.text)
        self.assertIn("bus recovery successful", self.text.lower())

    def test_both_uart_runtime_configurations(self) -> None:
        # Hi-Link UART
        self.assertIn("GPIO2", self.text)
        self.assertIn("GPIO1", self.text)
        self.assertIn("256000", self.text)
        # SEN0609 UART
        self.assertIn("GPIO5", self.text)
        self.assertIn("GPIO4", self.text)
        self.assertIn("115200", self.text)

    def test_gpio46_runtime_component_initialisation_only(self) -> None:
        self.assertIn("GPIO46", self.text)
        self.assertIn("runtime component initialisation only", self.flat)

    def test_gpio3_relay_configuration_and_default_off_only(self) -> None:
        self.assertIn("GPIO3", self.text)
        self.assertIn("RESTORE_DEFAULT_OFF", self.text)
        self.assertIn("configuration acceptance only", self.text)

    def test_physical_relay_actuation_not_proven(self) -> None:
        self.assertIn("physical relay actuation is not proven", self.flat)

    def test_connector_continuity_not_proven(self) -> None:
        self.assertIn("connector continuity is not proven", self.text)

    def test_poe_not_proven(self) -> None:
        self.assertIn("PoE is not proven", self.text)

    def test_no_network_identifiers_or_credentials(self) -> None:
        # No IPv4 addresses (e.g. the bench device IP).
        self.assertIsNone(
            re.search(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", self.text),
            "evidence record must not contain an IP address",
        )
        # No MAC-address-like tokens.
        self.assertIsNone(
            re.search(r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b", self.text),
            "evidence record must not contain a MAC/BSSID",
        )
        # No secret-bearing key:value declarations. The words "password" /
        # "encryption" may appear only in configured-state or redaction
        # statements, never followed by a literal value.
        for banned in ("ssid:", "bssid:", "password:", "psk:", "key:"):
            self.assertNotIn(banned, self.text.lower())
        self.assertIn("network identifiers redacted", self.text)
        self.assertIn("no repository-stored credentials", self.flat)

    def test_no_release_safety_compliance_commercial_claim(self) -> None:
        lower = self.text.lower()
        for phrase in (
            "fully verified",
            "hardware verified",
            "pinout proven",
            "production proven",
            "release ready",
            "commercially available",
        ):
            self.assertNotIn(phrase, lower, f"forbidden claim: {phrase!r}")
        self.assertIn(
            "no release, electrical-safety, EMC, compliance, customer, "
            "reliability, or commercial claim",
            self.flat,
        )

    def test_source_package_paths_and_capture_metadata(self) -> None:
        self.assertIn("packages/hardware/sense360_core_ceiling.yaml", self.text)
        self.assertIn("packages/boards/s360-100-core.yaml", self.text)
        self.assertIn("2026.7.0", self.text)
        self.assertIn("2026-07-19", self.text)
        self.assertIn("owner-supplied", self.text)

    def test_hardware_catalog_state_unchanged(self) -> None:
        catalog = json.loads(HARDWARE_CATALOG.read_text(encoding="utf-8"))
        core = [i for i in catalog["items"] if i.get("sku") == "S360-100"]
        self.assertEqual(len(core), 1)
        self.assertEqual(core[0]["rev"], "R4")
        self.assertEqual(core[0]["schematic_status"], "verified")

    def test_remaining_bench_checks_listed(self) -> None:
        for check in (
            "multimeter continuity",
            "cold power cycle",
            "LED identity and polarity",
            "known expansion module",
            "radar hardware",
            "Connector voltage and continuity",
            "PoE test",
            "Soak and reboot monitoring",
        ):
            self.assertIn(check, self.text, f"missing bench check: {check!r}")


class LedFunctionalEvidenceTests(unittest.TestCase):
    """Guards for the attached S360-300 LED functional-evidence section."""

    @classmethod
    def setUpClass(cls) -> None:
        assert DOC_PATH.is_file(), f"missing {DOC_PATH}"
        cls.text = DOC_PATH.read_text(encoding="utf-8")
        cls.flat = re.sub(r"\s+", " ", cls.text)
        marker = "## Attached S360-300 LED functional evidence"
        assert marker in cls.text, "missing LED functional evidence section"
        cls.led = cls.text.split(marker, 1)[1]
        cls.led_flat = re.sub(r"\s+", " ", cls.led)

    def test_identifies_led_board_package(self) -> None:
        self.assertIn("packages/boards/s360-300-led.yaml", self.led)

    def test_records_gpio38_data_pin(self) -> None:
        self.assertIn("GPIO38", self.led)

    def test_records_twelve_leds(self) -> None:
        self.assertIn("12 LEDs", self.led)

    def test_records_grb_as_configured_firmware_order(self) -> None:
        self.assertIn("GRB", self.led)
        self.assertIn("GRB is the configured firmware order", self.led_flat)

    def test_records_room_light_entity(self) -> None:
        self.assertIn("Room Light", self.led)

    def test_records_logged_on_off_command_cycles(self) -> None:
        self.assertIn("two successful logged ON/OFF command cycles", self.led_flat)

    def test_records_owner_observed_physical_operation(self) -> None:
        self.assertIn("owner-supplied observation", self.led)
        self.assertIn("physical LED ring illuminated", self.led_flat)
        self.assertIn('the owner reports the LED as "fully working"', self.led_flat)
        self.assertIn("owner reports RGB colour control worked", self.led_flat)

    def test_led_functional_evidence_pass(self) -> None:
        self.assertIn(
            "PASS — canonical S360-300 LED package physical functional "
            "operation observed",
            self.led_flat,
        )

    def test_full_brightness_not_a_thermal_or_safety_claim(self) -> None:
        self.assertIn(
            "It is not a thermal or electrical-safety conclusion", self.led_flat
        )
        # Safety wording may appear only inside the explicit not-proven
        # disclaimers, never as an affirmative claim.
        self.assertIn(
            "that 100% brightness is thermally or electrically safe",
            self.led_flat,
        )
        self.assertIn("does not establish a maximum safe brightness", self.led_flat)
        lower = self.led_flat.lower()
        for phrase in ("proven safe", "confirmed safe", "is safe to run"):
            self.assertNotIn(phrase, lower, f"forbidden safety claim: {phrase!r}")

    def test_open_items_stay_open(self) -> None:
        for item in (
            "LED supply-rail identity",
            "electrical current draw",
            "thermal performance",
            "soak reliability",
            "EMC, safety, or compliance",
            "complete Core hardware verification",
        ):
            self.assertIn(item, self.led_flat, f"missing open item: {item!r}")
        self.assertIn("PARTIAL / OPEN", self.text)

    def test_no_network_identifiers_in_led_section(self) -> None:
        self.assertIsNone(
            re.search(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", self.led),
            "LED evidence must not contain an IP address",
        )
        self.assertIsNone(
            re.search(r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b", self.led),
            "LED evidence must not contain a MAC/BSSID",
        )
        for banned in ("ssid:", "bssid:", "password:", "psk:", "key:"):
            self.assertNotIn(banned, self.led.lower())


if __name__ == "__main__":
    unittest.main()

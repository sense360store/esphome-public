#!/usr/bin/env python3
"""Pin-pinning regression tests for CORE-ABSTRACT-BUS-001C.

These tests lock in the schematic-backed CORE-ABSTRACT-BUS-001C rebind plan
recorded in
``docs/hardware/core-abstract-bus-001c-rebind-plan.md`` and the parent
audit doc
``docs/hardware/core-abstract-bus-reconciliation.md``. They are the
scaffold owed by precondition #5 of the 001C planning record (the
``tests/test_core_abstract_bus.py`` scaffold lands **with** the first
implementation slice).

Schematic ground truth references (S360-100-R4, the Core schematic):

* ``IO15 = PIR``        — RoomIQ J10 PIR motion input
* ``IO47 = ALS_INT``    — RoomIQ J10 ambient-light-sensor interrupt
* ``IO17 = expander_int`` — SX1509 GPIO/PWM expander interrupt
* ``IO1 = Hi-Link_RX``  — RoomIQ J10 Hi-Link LD2450 UART RX (ESP rx_pin)
* ``IO2 = Hi-Link_TX``  — RoomIQ J10 Hi-Link LD2450 UART TX (ESP tx_pin)
* ``IO4 = SEN0609_RX``  — RoomIQ J10 SEN0609 UART RX (ESP rx_pin)
* ``IO5 = SEN0609_TX``  — RoomIQ J10 SEN0609 UART TX (ESP tx_pin)
* ``IO6 = out(gpio6)``  — RoomIQ J10 SEN0609 auxiliary output
* ``IO38 = LED_DATA``   — S360-300 WS2812B LED ring data
* ``IO46 = GP_Fan_Status_Led`` — Core-side fan status indicator
* ``IO7 = AirQ_Status_Led``    — AirIQ module status indicator (AirIQ-only)
* ``IO8 = AirQ_Led``           — AirIQ module indicator (AirIQ-only)

Hi-Link baud is 256000 and SEN0609 baud is 115200 per operator decision #7.

This PR does NOT move ``relay_pin`` to ``GPIO3`` — that move belongs to the
next slice, CORE-ABSTRACT-BUS-001A. The test below pins each Core
abstract package's current ``relay_pin`` value so any accidental relay
re-bind in this PR fails loudly.

Run with::

    python3 tests/test_core_abstract_bus.py
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent

# Core abstract packages whose 001C substitutions / blocks this PR
# rebinds. Each must drop the generic ``status_led_pin`` and
# ``expansion_gpio1..4`` substitutions and adopt the schematic-named
# replacements.
AFFECTED_CORE_PACKAGES = [
    REPO_ROOT / "packages" / "hardware" / "sense360_core.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_ceiling.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_mapping.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_poe.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_wall.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_voice_ceiling.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_voice_wall.yaml",
]

# Per-package substitutions affected by 001C.
COMFORT_CEILING_PACKAGE = REPO_ROOT / "packages" / "expansions" / "comfort_ceiling.yaml"
SX1509_PACKAGE = REPO_ROOT / "packages" / "expansions" / "gpio_expander_sx1509.yaml"
SENSE360_CORE_CEILING = REPO_ROOT / "packages" / "hardware" / "sense360_core_ceiling.yaml"
SENSE360_CORE_MAPPING = REPO_ROOT / "packages" / "hardware" / "sense360_core_mapping.yaml"
LED_RING_CEILING_PACKAGE = REPO_ROOT / "packages" / "hardware" / "led_ring_ceiling.yaml"
AIRIQ_CEILING_S3_PACKAGE = REPO_ROOT / "packages" / "expansions" / "airiq_ceiling_s3.yaml"
SENSE360_CORE_CEILING_S3 = REPO_ROOT / "packages" / "hardware" / "sense360_core_ceiling_s3.yaml"

PACKAGES_DIR = REPO_ROOT / "packages"


def _substitution_value(text: str, name: str) -> Optional[str]:
    """Return the right-hand value of a ``name: VALUE`` substitution line.

    Strips ``#`` comments and surrounding quotes. Skips lines that are
    themselves commented out (start with ``#``). Returns ``None`` if the
    substitution is not present.
    """
    pattern = re.compile(
        rf"^\s*{re.escape(name)}:\s*(?P<value>\S+)",
        re.MULTILINE,
    )
    for match in pattern.finditer(text):
        # Verify the line is not commented out.
        line_start = text.rfind("\n", 0, match.start()) + 1
        prefix = text[line_start : match.start()]
        if prefix.lstrip().startswith("#"):
            continue
        raw = match.group("value")
        # Strip trailing comment if any.
        if "#" in raw:
            raw = raw.split("#", 1)[0].rstrip()
        return raw.strip("\"'")
    return None


def _find_uart_block(text: str, bus_id: str) -> Optional[dict]:
    """Return parsed tx/rx/baud values for the named UART bus, or None.

    The search is intentionally regex-driven so the test does not depend
    on a full ESPHome YAML parser. The Core abstract packages declare
    each UART bus with literal pin / baud values immediately following
    the ``- id: ...`` line.
    """
    pattern = re.compile(
        rf"-\s*id:\s*{re.escape(bus_id)}\s*\n"
        r"(?P<body>(?:\s*[a-z_]+:\s*\S+\s*\n)+)",
        re.MULTILINE,
    )
    match = pattern.search(text)
    if not match:
        return None
    body = match.group("body")
    fields: dict = {}
    for key in ("tx_pin", "rx_pin", "baud_rate"):
        m = re.search(rf"^\s*{key}:\s*(\S+)", body, re.MULTILINE)
        if m:
            value = m.group(1).split("#", 1)[0].rstrip()
            fields[key] = value.strip("\"'")
    return fields


class PirSensorPinTests(unittest.TestCase):
    """PIR rebind: GPIO47 (ALS_INT, conflict) → GPIO15 (schematic PIR)."""

    def test_pir_sensor_pin_is_gpio15_in_sense360_core_ceiling(self) -> None:
        value = _substitution_value(
            SENSE360_CORE_CEILING.read_text(), "pir_sensor_pin"
        )
        self.assertEqual(
            value,
            "GPIO15",
            "pir_sensor_pin must be GPIO15 (schematic IO15 = PIR per "
            "S360-100-R4) in sense360_core_ceiling.yaml. Was previously "
            "GPIO47 (= ALS_INT, schematic-conflicting).",
        )


class ComfortCeilingAlsIntTests(unittest.TestCase):
    """ALS_INT rebind: GPIO3 (Relay net) → GPIO47 (schematic ALS_INT)."""

    def test_comfort_ceiling_als_int_pin_is_gpio47(self) -> None:
        value = _substitution_value(
            COMFORT_CEILING_PACKAGE.read_text(), "comfort_ceiling_als_int_pin"
        )
        self.assertEqual(
            value,
            "GPIO47",
            "comfort_ceiling_als_int_pin must be GPIO47 (schematic "
            "IO47 = ALS_INT per S360-100-R4) in "
            "packages/expansions/comfort_ceiling.yaml. Was previously "
            "GPIO3 (= Relay net), which is freed by this 001C slice for "
            "the relay slice (CORE-ABSTRACT-BUS-001A).",
        )

    def test_comfort_ceiling_als_int_pin_does_not_reference_gpio3(self) -> None:
        # The substitution line itself must be GPIO47 only. Mention of
        # GPIO3 in commentary explaining the rebind is fine; an active
        # substitution binding to GPIO3 is not.
        text = COMFORT_CEILING_PACKAGE.read_text()
        for line in text.splitlines():
            stripped = line.lstrip()
            if stripped.startswith("#"):
                continue
            if re.match(r"comfort_ceiling_als_int_pin:\s*GPIO3\b", stripped):
                self.fail(
                    "comfort_ceiling_als_int_pin must not bind GPIO3 "
                    "after CORE-ABSTRACT-BUS-001C."
                )


class RoomIQSen0609OutputPinTests(unittest.TestCase):
    """SEN0609 auxiliary line: introduced as roomiq_sen0609_output_pin: GPIO6."""

    def test_roomiq_sen0609_output_pin_is_gpio6_when_defined(self) -> None:
        defined_somewhere = False
        for pkg in AFFECTED_CORE_PACKAGES:
            value = _substitution_value(pkg.read_text(), "roomiq_sen0609_output_pin")
            if value is None:
                continue
            defined_somewhere = True
            with self.subTest(package=pkg.name):
                self.assertEqual(
                    value,
                    "GPIO6",
                    f"roomiq_sen0609_output_pin must be GPIO6 (schematic "
                    f"IO6 = out(gpio6) per S360-100-R4) in {pkg.name}.",
                )
        self.assertTrue(
            defined_somewhere,
            "roomiq_sen0609_output_pin must be introduced in at least one "
            "Core abstract package (schematic IO6 = out(gpio6) per "
            "S360-100-R4).",
        )


class ExpanderIntPinTests(unittest.TestCase):
    """Expander interrupt rebind: GPIO3 (Relay net) → GPIO17 (schematic expander_int)."""

    def test_expander_int_pin_is_gpio17_where_defined(self) -> None:
        value = _substitution_value(
            SENSE360_CORE_MAPPING.read_text(), "expander_int_pin"
        )
        self.assertEqual(
            value,
            "GPIO17",
            "expander_int_pin must be GPIO17 (schematic IO17 = "
            "expander_int per S360-100-R4) in "
            "packages/hardware/sense360_core_mapping.yaml. Was "
            "previously GPIO3 (= Relay net).",
        )


class SX1509InterruptPinTests(unittest.TestCase):
    """SX1509 interrupt: GPIO3 → GPIO17 (same schematic expander_int net)."""

    def test_sx1509_interrupt_pin_is_gpio17(self) -> None:
        value = _substitution_value(
            SX1509_PACKAGE.read_text(), "sx1509_interrupt_pin"
        )
        self.assertEqual(
            value,
            "GPIO17",
            "sx1509_interrupt_pin must be GPIO17 (schematic IO17 = "
            "expander_int per S360-100-R4) in "
            "packages/expansions/gpio_expander_sx1509.yaml. Was "
            "previously GPIO3 (= Relay net).",
        )


class RoomIQHiLinkUartTests(unittest.TestCase):
    """roomiq_hi_link_uart: tx_pin GPIO2, rx_pin GPIO1, baud 256000."""

    def test_hi_link_uart_defined_with_correct_pinning(self) -> None:
        defined_somewhere = False
        for pkg in AFFECTED_CORE_PACKAGES:
            fields = _find_uart_block(pkg.read_text(), "roomiq_hi_link_uart")
            if fields is None:
                continue
            defined_somewhere = True
            with self.subTest(package=pkg.name):
                self.assertEqual(
                    fields.get("tx_pin"),
                    "GPIO2",
                    f"roomiq_hi_link_uart.tx_pin must be GPIO2 (schematic "
                    f"IO2 = Hi-Link_TX, ESP transmits to radar) in {pkg.name}",
                )
                self.assertEqual(
                    fields.get("rx_pin"),
                    "GPIO1",
                    f"roomiq_hi_link_uart.rx_pin must be GPIO1 (schematic "
                    f"IO1 = Hi-Link_RX, ESP receives from radar) in {pkg.name}",
                )
                self.assertEqual(
                    fields.get("baud_rate"),
                    "256000",
                    f"roomiq_hi_link_uart.baud_rate must be 256000 (Hi-Link "
                    f"LD2450 default per operator decision #7) in {pkg.name}",
                )
        self.assertTrue(
            defined_somewhere,
            "roomiq_hi_link_uart must be defined in at least one Core "
            "abstract package after CORE-ABSTRACT-BUS-001C.",
        )


class RoomIQSen0609UartTests(unittest.TestCase):
    """roomiq_sen0609_uart: tx_pin GPIO5, rx_pin GPIO4, baud 115200."""

    def test_sen0609_uart_defined_with_correct_pinning(self) -> None:
        defined_somewhere = False
        for pkg in AFFECTED_CORE_PACKAGES:
            fields = _find_uart_block(pkg.read_text(), "roomiq_sen0609_uart")
            if fields is None:
                continue
            defined_somewhere = True
            with self.subTest(package=pkg.name):
                self.assertEqual(
                    fields.get("tx_pin"),
                    "GPIO5",
                    f"roomiq_sen0609_uart.tx_pin must be GPIO5 (schematic "
                    f"IO5 = SEN0609_TX, ESP transmits to radar) in {pkg.name}",
                )
                self.assertEqual(
                    fields.get("rx_pin"),
                    "GPIO4",
                    f"roomiq_sen0609_uart.rx_pin must be GPIO4 (schematic "
                    f"IO4 = SEN0609_RX, ESP receives from radar) in {pkg.name}",
                )
                self.assertEqual(
                    fields.get("baud_rate"),
                    "115200",
                    f"roomiq_sen0609_uart.baud_rate must be 115200 (SEN0609 "
                    f"default per operator decision #7) in {pkg.name}",
                )
        self.assertTrue(
            defined_somewhere,
            "roomiq_sen0609_uart must be defined in at least one Core "
            "abstract package after CORE-ABSTRACT-BUS-001C.",
        )


class StatusLedPinRetiredTests(unittest.TestCase):
    """Generic Core ``status_led_pin`` substitution retired from affected packages."""

    def test_status_led_pin_substitution_absent(self) -> None:
        for pkg in AFFECTED_CORE_PACKAGES:
            text = pkg.read_text()
            value = _substitution_value(text, "status_led_pin")
            with self.subTest(package=pkg.name):
                self.assertIsNone(
                    value,
                    f"generic `status_led_pin` substitution must be retired "
                    f"from {pkg.name} per CORE-ABSTRACT-BUS-001C (operator "
                    f"decisions #9 / #12). The schematic-correct LED ring "
                    f"data line is on GPIO38 and owned by the LED ring "
                    f"package; Core-side indicator now uses "
                    f"`fan_status_led_pin: GPIO46`.",
                )


class LedRingCeilingPinTests(unittest.TestCase):
    """S360-300 LED ring data remains GPIO38 in led_ring_ceiling.yaml."""

    def test_led_data_pin_is_gpio38(self) -> None:
        value = _substitution_value(
            LED_RING_CEILING_PACKAGE.read_text(), "led_data_pin"
        )
        self.assertEqual(
            value,
            "GPIO38",
            "led_data_pin must remain GPIO38 (S360-300 LED ring data; "
            "schematic IO38 = LED_DATA per S360-100-R4) in "
            "packages/hardware/led_ring_ceiling.yaml. CORE-ABSTRACT-BUS-001C "
            "explicitly does NOT change the LED ring data line.",
        )


class FanStatusLedPinTests(unittest.TestCase):
    """fan_status_led_pin: GPIO46 where introduced/retained."""

    def test_fan_status_led_pin_is_gpio46_where_defined(self) -> None:
        defined_somewhere = False
        for pkg in AFFECTED_CORE_PACKAGES:
            value = _substitution_value(pkg.read_text(), "fan_status_led_pin")
            if value is None:
                continue
            defined_somewhere = True
            with self.subTest(package=pkg.name):
                self.assertEqual(
                    value,
                    "GPIO46",
                    f"fan_status_led_pin must be GPIO46 (schematic "
                    f"IO46 = GP_Fan_Status_Led per S360-100-R4) where "
                    f"defined; got {value} in {pkg.name}.",
                )
        self.assertTrue(
            defined_somewhere,
            "fan_status_led_pin must be introduced in at least one Core "
            "abstract package per CORE-ABSTRACT-BUS-001C operator "
            "decision #10.",
        )


class AirIQLedClassificationTests(unittest.TestCase):
    """AirIQ LED lines (GPIO7, GPIO8) stay AirIQ-only."""

    def test_airiq_status_led_pin_is_gpio7_where_defined(self) -> None:
        for path in [AIRIQ_CEILING_S3_PACKAGE, SENSE360_CORE_CEILING_S3]:
            if not path.is_file():
                continue
            value = _substitution_value(path.read_text(), "airiq_status_led_pin")
            if value is None:
                continue
            with self.subTest(package=path.name):
                self.assertEqual(
                    value,
                    "GPIO7",
                    f"airiq_status_led_pin must be GPIO7 (schematic "
                    f"IO7 = AirQ_Status_Led, AirIQ J9 indicator) in "
                    f"{path.name}.",
                )

    def test_airiq_led_pin_is_gpio8_if_defined(self) -> None:
        # airiq_led_pin is currently only present as a commented hint in
        # sense360_core_ceiling_s3.yaml. If any package activates it,
        # the value must be GPIO8 (schematic IO8 = AirQ_Led).
        for path in [AIRIQ_CEILING_S3_PACKAGE, SENSE360_CORE_CEILING_S3]:
            if not path.is_file():
                continue
            value = _substitution_value(path.read_text(), "airiq_led_pin")
            if value is None:
                continue
            with self.subTest(package=path.name):
                self.assertEqual(
                    value,
                    "GPIO8",
                    f"airiq_led_pin must be GPIO8 (schematic IO8 = "
                    f"AirQ_Led, AirIQ J9 indicator) in {path.name}.",
                )


class VentIQNoCoreDrivenLedTests(unittest.TestCase):
    """VentIQ has no Core-driven LED / status line (operator decision #12)."""

    def test_no_ventiq_core_led_substitution(self) -> None:
        for yaml_path in PACKAGES_DIR.rglob("*.yaml"):
            text = yaml_path.read_text()
            # Skip commented lines; look only for active substitutions.
            for line in text.splitlines():
                stripped = line.lstrip()
                if stripped.startswith("#"):
                    continue
                m = re.match(
                    r"(?P<name>ventiq[_a-z0-9]*(?:status_)?led_pin):\s*GPIO\d+",
                    stripped,
                )
                if m:
                    self.fail(
                        f"VentIQ Core-driven LED substitution "
                        f"{m.group('name')!r} found in {yaml_path}. VentIQ "
                        f"has no dedicated Core-driven LED line per "
                        f"CORE-ABSTRACT-BUS-001C operator decision #12."
                    )


class ExpansionGpioRetiredTests(unittest.TestCase):
    """Generic `expansion_gpio1..4` substitutions retired from affected Core packages."""

    def test_expansion_gpio_substitutions_absent(self) -> None:
        for pkg in AFFECTED_CORE_PACKAGES:
            text = pkg.read_text()
            with self.subTest(package=pkg.name):
                for n in (1, 2, 3, 4):
                    value = _substitution_value(text, f"expansion_gpio{n}")
                    self.assertIsNone(
                        value,
                        f"expansion_gpio{n} substitution must be retired "
                        f"in {pkg.name} per CORE-ABSTRACT-BUS-001C "
                        f"operator decision #13 (function-specific "
                        f"substitutions replace the generic "
                        f"expansion_gpio* abstraction).",
                    )


class NoSubstitutionCollisionTests(unittest.TestCase):
    """No collision between relay_pin, comfort_ceiling_als_int_pin, expander_int_pin, sx1509_interrupt_pin.

    Each of these substitutions resolves to a single pin per file. The
    rebind must ensure the three previously-colliding substitutions
    (ALS_INT, expander_int, SX1509 INT, all on GPIO3) no longer share a
    pin with relay_pin (which is the schematic-correct Relay net on
    GPIO3 once CORE-ABSTRACT-BUS-001A lands; in this PR it stays at its
    current pre-001A values).
    """

    def test_relay_pin_does_not_collide_with_001c_rebound_pins(self) -> None:
        comfort = _substitution_value(
            COMFORT_CEILING_PACKAGE.read_text(), "comfort_ceiling_als_int_pin"
        )
        expander_mapping = _substitution_value(
            SENSE360_CORE_MAPPING.read_text(), "expander_int_pin"
        )
        sx1509 = _substitution_value(
            SX1509_PACKAGE.read_text(), "sx1509_interrupt_pin"
        )

        for pkg in AFFECTED_CORE_PACKAGES:
            relay = _substitution_value(pkg.read_text(), "relay_pin")
            if relay is None:
                continue
            with self.subTest(package=pkg.name, sub="comfort_ceiling_als_int_pin"):
                self.assertNotEqual(
                    relay,
                    comfort,
                    f"relay_pin in {pkg.name} ({relay}) must not collide "
                    f"with comfort_ceiling_als_int_pin ({comfort}). 001C "
                    f"moved ALS_INT off GPIO3 specifically to free GPIO3 "
                    f"for the relay slice.",
                )
            with self.subTest(package=pkg.name, sub="expander_int_pin"):
                self.assertNotEqual(
                    relay,
                    expander_mapping,
                    f"relay_pin in {pkg.name} ({relay}) must not collide "
                    f"with expander_int_pin ({expander_mapping}).",
                )
            with self.subTest(package=pkg.name, sub="sx1509_interrupt_pin"):
                self.assertNotEqual(
                    relay,
                    sx1509,
                    f"relay_pin in {pkg.name} ({relay}) must not collide "
                    f"with sx1509_interrupt_pin ({sx1509}).",
                )

    def test_001c_rebound_pins_do_not_collide_with_each_other(self) -> None:
        comfort = _substitution_value(
            COMFORT_CEILING_PACKAGE.read_text(), "comfort_ceiling_als_int_pin"
        )
        expander_mapping = _substitution_value(
            SENSE360_CORE_MAPPING.read_text(), "expander_int_pin"
        )
        sx1509 = _substitution_value(
            SX1509_PACKAGE.read_text(), "sx1509_interrupt_pin"
        )
        # comfort_ceiling_als_int_pin (GPIO47) and expander_int_pin /
        # sx1509_interrupt_pin (both GPIO17) must be distinct nets.
        # expander_int_pin and sx1509_interrupt_pin SHARE the same net
        # by design (both name the schematic IO17 = expander_int line);
        # that aliasing is intentional and is not a collision.
        self.assertNotEqual(
            comfort,
            expander_mapping,
            "comfort_ceiling_als_int_pin and expander_int_pin must bind "
            "different physical nets (ALS_INT vs expander_int).",
        )
        self.assertNotEqual(
            comfort,
            sx1509,
            "comfort_ceiling_als_int_pin and sx1509_interrupt_pin must "
            "bind different physical nets (ALS_INT vs expander_int).",
        )


class RelayPinUnchangedTests(unittest.TestCase):
    """relay_pin is NOT moved to GPIO3 in this PR.

    Each Core abstract package keeps its pre-001A value. The relay
    move to ``GPIO3`` belongs to CORE-ABSTRACT-BUS-001A and lands in a
    later atomic slice; this PR only frees ``GPIO3`` by moving the
    schematic-conflicting bindings (ALS_INT, expander_int, SX1509 INT)
    away from ``GPIO3``.
    """

    EXPECTED_RELAY_PINS = {
        "sense360_core.yaml": "GPIO10",
        "sense360_core_ceiling.yaml": "GPIO4",
        "sense360_core_mapping.yaml": "GPIO10",
        "sense360_core_poe.yaml": "GPIO10",
        "sense360_core_wall.yaml": "GPIO4",
        "sense360_core_voice_ceiling.yaml": "GPIO4",
        "sense360_core_voice_wall.yaml": "GPIO4",
    }

    def test_relay_pin_holds_current_value_in_each_core_package(self) -> None:
        for pkg in AFFECTED_CORE_PACKAGES:
            relay = _substitution_value(pkg.read_text(), "relay_pin")
            expected = self.EXPECTED_RELAY_PINS.get(pkg.name)
            with self.subTest(package=pkg.name):
                self.assertEqual(
                    relay,
                    expected,
                    f"relay_pin in {pkg.name} must remain {expected} "
                    f"until CORE-ABSTRACT-BUS-001A lands. This 001C PR "
                    f"frees GPIO3 but does not consume it.",
                )

    def test_relay_pin_is_not_gpio3_in_any_affected_core_package(self) -> None:
        for pkg in AFFECTED_CORE_PACKAGES:
            relay = _substitution_value(pkg.read_text(), "relay_pin")
            if relay is None:
                continue
            with self.subTest(package=pkg.name):
                self.assertNotEqual(
                    relay,
                    "GPIO3",
                    f"relay_pin in {pkg.name} must not be GPIO3 in this "
                    f"PR. The GPIO3 rebind belongs to "
                    f"CORE-ABSTRACT-BUS-001A.",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)

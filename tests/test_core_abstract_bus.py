#!/usr/bin/env python3
"""Pin-pinning regression tests for CORE-ABSTRACT-BUS-001A / 001B / 001C.

These tests lock in the schematic-backed CORE-ABSTRACT-BUS-001C rebind plan
recorded in
``docs/hardware/core-abstract-bus-001c-rebind-plan.md`` and the parent
audit doc
``docs/hardware/core-abstract-bus-reconciliation.md``. They are the
scaffold owed by precondition #5 of the 001C planning record (the
``tests/test_core_abstract_bus.py`` scaffold lands **with** the first
implementation slice).

CORE-ABSTRACT-BUS-001A extends this scaffold with the schematic-backed
``relay_pin: GPIO3`` rebind. The 001A rebind landed once 001C (PR #557)
freed ``GPIO3`` by moving ALS_INT off ``GPIO3`` to ``GPIO47`` and the
SX1509 / expander interrupt off ``GPIO3`` to ``GPIO17``.

CORE-ABSTRACT-BUS-001B further extends this scaffold with the
schematic-backed I²C consolidation: every in-scope Core abstract package
exposes a single shared bus ``core_i2c`` on ``GPIO48`` (SDA) /
``GPIO45`` (SCL) at ``400kHz`` (schematic ``IO48`` / ``IO45`` per
``S360-100-R4``, pulled up by ``R22``/``R21`` 10 kΩ). The six legacy
bus ids (``halo_i2c`` / ``expansion_i2c`` / ``i2c0`` / ``i2c1`` /
``i2c_primary`` / ``i2c_expander``) are removed from every in-scope
Core abstract package. Every downstream ``*_i2c_id`` consumer default
is rebound to ``core_i2c``. The hard-coded ``i2c_id: halo_i2c`` literal
in ``packages/features/ceiling_halo_leds.yaml`` is rebound to
``i2c_id: core_i2c``. The implementation is a **hard rename only** —
no compatibility aliases are introduced.

Schematic ground truth references (S360-100-R4, the Core schematic):

* ``IO3 = Relay``       — J4 Relay module gate (drives S360-310 K1 coil)
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

The Core abstract packages affected by CORE-ABSTRACT-BUS-001A are listed
in ``RELAY_REBIND_PACKAGES`` below. Voice-variant Core packages
(``sense360_core_voice_ceiling.yaml`` / ``sense360_core_voice_wall.yaml``)
are deliberately out of scope for the 001A rebind; their ``relay_pin``
substitutions remain at their pre-001A values until a later slice
addresses them.

Run with::

    python3 tests/test_core_abstract_bus.py
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent

# Core abstract packages whose 001C substitutions / blocks were rebound
# by CORE-ABSTRACT-BUS-001C (#557). Each must drop the generic
# ``status_led_pin`` and ``expansion_gpio1..4`` substitutions and adopt
# the schematic-named replacements.
AFFECTED_CORE_PACKAGES = [
    REPO_ROOT / "packages" / "hardware" / "sense360_core.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_ceiling.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_mapping.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_poe.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_wall.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_voice_ceiling.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_voice_wall.yaml",
]

# Core abstract packages whose ``relay_pin`` substitution is rebound to
# the schematic-correct ``GPIO3`` by CORE-ABSTRACT-BUS-001A. Voice-
# variant Core packages are deliberately not in this list; the 001A
# scope is restricted to the five non-voice Core packages enumerated
# below. Each must drop the pre-001A ``GPIO4`` / ``GPIO10`` value and
# adopt ``GPIO3`` (schematic Relay net per S360-100-R4 IO3).
RELAY_REBIND_PACKAGES = [
    REPO_ROOT / "packages" / "hardware" / "sense360_core.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_ceiling.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_mapping.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_poe.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_wall.yaml",
]

# Per-package substitutions affected by 001C.
COMFORT_CEILING_PACKAGE = REPO_ROOT / "packages" / "expansions" / "comfort_ceiling.yaml"
SX1509_PACKAGE = REPO_ROOT / "packages" / "expansions" / "gpio_expander_sx1509.yaml"
# CORE-ABSTRACT-BUS-SX1509-001: neutral FanPWM SX1509 binding layer.
FAN_PWM_SX1509_PACKAGE = REPO_ROOT / "packages" / "expansions" / "fan_pwm_sx1509.yaml"
FAN_RELAY_PACKAGE = REPO_ROOT / "packages" / "expansions" / "fan_relay.yaml"
FAN_DAC_PACKAGE = REPO_ROOT / "packages" / "expansions" / "fan_dac.yaml"
FAN_GP8403_PACKAGE_PATH = REPO_ROOT / "packages" / "expansions" / "fan_gp8403.yaml"
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
    rebind ensures the three previously-colliding substitutions
    (ALS_INT, expander_int, SX1509 INT, all on GPIO3 before 001C) no
    longer share a pin with relay_pin (which is now the schematic-
    correct Relay net on GPIO3 after CORE-ABSTRACT-BUS-001A).
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
                    f"for the relay slice; 001A then rebound relay_pin "
                    f"to GPIO3.",
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


class RelayPinRebindTests(unittest.TestCase):
    """CORE-ABSTRACT-BUS-001A: relay_pin rebound to GPIO3 (schematic Relay net).

    Each Core abstract package listed in ``RELAY_REBIND_PACKAGES`` has
    ``relay_pin`` set to ``GPIO3`` (schematic IO3 = Relay per
    S360-100-R4). The GPIO3 collision was resolved by CORE-ABSTRACT-
    BUS-001C (#557) which moved ALS_INT off GPIO3 to GPIO47 and the
    expander interrupt off GPIO3 to GPIO17.

    Voice-variant Core packages (``sense360_core_voice_ceiling.yaml``
    and ``sense360_core_voice_wall.yaml``) are out-of-scope for the
    001A rebind; their ``relay_pin`` substitutions are not asserted by
    this class.
    """

    def test_relay_pin_is_gpio3_in_every_affected_core_package(self) -> None:
        for pkg in RELAY_REBIND_PACKAGES:
            relay = _substitution_value(pkg.read_text(), "relay_pin")
            with self.subTest(package=pkg.name):
                self.assertEqual(
                    relay,
                    "GPIO3",
                    f"relay_pin in {pkg.name} must be GPIO3 (schematic "
                    f"IO3 = Relay per S360-100-R4) after "
                    f"CORE-ABSTRACT-BUS-001A; got {relay!r}.",
                )

    def test_relay_pin_is_not_gpio4_or_gpio10_in_any_affected_core_package(
        self,
    ) -> None:
        for pkg in RELAY_REBIND_PACKAGES:
            relay = _substitution_value(pkg.read_text(), "relay_pin")
            with self.subTest(package=pkg.name):
                self.assertNotIn(
                    relay,
                    ("GPIO4", "GPIO10"),
                    f"relay_pin in {pkg.name} must not be the pre-001A "
                    f"value GPIO4 or GPIO10. CORE-ABSTRACT-BUS-001A "
                    f"rebinds relay_pin to the schematic-correct GPIO3 "
                    f"(IO4 is SEN0609_RX; IO10 is not the Relay net per "
                    f"S360-100-R4).",
                )


class MainRelaySwitchBindingTests(unittest.TestCase):
    """``main_relay`` in sense360_core_ceiling.yaml resolves to ${relay_pin}.

    Asserts the ``switch.platform: gpio`` block declaring ``id:
    main_relay`` in sense360_core_ceiling.yaml has ``pin:
    ${relay_pin}`` so the generated-config diff for Release-One
    moves ``main_relay`` from ``GPIO4`` to ``GPIO3`` cleanly with the
    relay_pin substitution.
    """

    def test_main_relay_pin_is_relay_pin_substitution(self) -> None:
        text = SENSE360_CORE_CEILING.read_text()
        # Look for the ``id: main_relay`` line followed by a ``pin:``
        # line referencing the ``${relay_pin}`` substitution.
        pattern = re.compile(
            r"id:\s*main_relay\s*\n"
            r"(?P<between>(?:\s*[a-z_]+:\s*[^\n]+\n)*?)"
            r"\s*pin:\s*(?P<pin>\S+)",
            re.MULTILINE,
        )
        match = pattern.search(text)
        self.assertIsNotNone(
            match,
            "Expected a switch.platform: gpio block with id: main_relay "
            "followed by a pin: declaration in "
            "sense360_core_ceiling.yaml.",
        )
        pin_value = match.group("pin").strip("\"'")
        self.assertEqual(
            pin_value,
            "${relay_pin}",
            "main_relay in sense360_core_ceiling.yaml must bind "
            "pin: ${relay_pin} so the schematic-correct Relay net "
            "(GPIO3 per CORE-ABSTRACT-BUS-001A) is consumed by "
            "downstream products through substitution.",
        )


# ============================================================================
# CORE-ABSTRACT-BUS-001B — Shared Core I²C bus consolidation tests
# ============================================================================

# Core abstract packages whose I²C bus is consolidated to the single shared
# ``core_i2c`` bus by CORE-ABSTRACT-BUS-001B. Each must define exactly one
# top-level ``i2c:`` bus with ``id: core_i2c``, ``sda: GPIO48``,
# ``scl: GPIO45``, ``frequency: 400kHz`` (schematic IO48/IO45 per
# S360-100-R4, pulled up by R22/R21 10 kΩ).
SHARED_I2C_BUS_PACKAGES = [
    REPO_ROOT / "packages" / "hardware" / "sense360_core.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_ceiling.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_mapping.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_poe.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_wall.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_voice_ceiling.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_voice_wall.yaml",
]

# Expansion-package consumers whose ``*_i2c_id`` substitution default is
# rebound to ``core_i2c`` by CORE-ABSTRACT-BUS-001B. Each tuple records the
# package path and the substitution name. The two S3-variant consumers
# (``airiq_ceiling_s3.yaml``, ``comfort_ceiling_s3.yaml``) are deliberately
# out of scope. (The Mini helper was removed by PRODUCT-DEP-MINI-001.)
SHARED_I2C_CONSUMER_DEFAULTS = [
    (REPO_ROOT / "packages" / "expansions" / "airiq.yaml", "airiq_i2c_id"),
    (REPO_ROOT / "packages" / "expansions" / "airiq_wall.yaml", "airiq_i2c_id"),
    (REPO_ROOT / "packages" / "expansions" / "airiq_ceiling.yaml", "airiq_i2c_id"),
    (REPO_ROOT / "packages" / "expansions" / "airiq_bathroom_base.yaml", "bathroom_i2c_id"),
    (REPO_ROOT / "packages" / "expansions" / "airiq_bathroom_pro.yaml", "bathroom_i2c_id"),
    (REPO_ROOT / "packages" / "expansions" / "comfort.yaml", "comfort_i2c_id"),
    (REPO_ROOT / "packages" / "expansions" / "comfort_wall.yaml", "comfort_i2c_id"),
    (REPO_ROOT / "packages" / "expansions" / "comfort_ceiling.yaml", "comfort_ceiling_i2c_id"),
    (REPO_ROOT / "packages" / "expansions" / "fan_gp8403.yaml", "fan_dac_i2c_id"),
    (REPO_ROOT / "packages" / "expansions" / "gpio_expander_sx1509.yaml", "sx1509_i2c_id"),
]

CEILING_HALO_LEDS_PACKAGE = REPO_ROOT / "packages" / "features" / "ceiling_halo_leds.yaml"
FAN_GP8403_PACKAGE = REPO_ROOT / "packages" / "expansions" / "fan_gp8403.yaml"
GP8403_FANDAC_ALIAS_PACKAGE = REPO_ROOT / "packages" / "expansions" / "fan_dac.yaml"
GENERATE_TEST_CONFIGS_SCRIPT = REPO_ROOT / "tests" / "generate_test_configs.py"

# Legacy bus ids retired from every in-scope Core abstract package by
# CORE-ABSTRACT-BUS-001B. Each must not appear as an active ``- id:``
# binding in any package in ``SHARED_I2C_BUS_PACKAGES``.
LEGACY_BUS_IDS = (
    "halo_i2c",
    "expansion_i2c",
    "i2c0",
    "i2c1",
    "i2c_primary",
    "i2c_expander",
)

CORE_I2C_SDA_PIN = "GPIO48"
CORE_I2C_SCL_PIN = "GPIO45"
CORE_I2C_FREQUENCY = "400kHz"


def _find_i2c_bus_block(text: str, bus_id: str) -> Optional[dict]:
    """Return the parsed sda/scl/frequency for the named I²C bus, or None.

    Mirrors ``_find_uart_block`` but matches an ``i2c:`` bus block. Returns
    a dict with the literal sda / scl / frequency values found on the
    immediately-following indented lines.
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
    for key in ("sda", "scl", "frequency"):
        m = re.search(rf"^\s*{key}:\s*(\S+)", body, re.MULTILINE)
        if m:
            value = m.group(1).split("#", 1)[0].rstrip()
            fields[key] = value.strip("\"'")
    return fields


def _active_top_level_bus_ids(text: str) -> list:
    """Return the list of active ``- id: <bus>`` declarations.

    Only returns ids that follow a top-level ``i2c:`` block (the ``i2c:``
    section header). Lines inside commented-out blocks are skipped.
    """
    ids: list = []
    in_i2c_block = False
    base_indent: Optional[int] = None
    for raw_line in text.splitlines():
        # Detect the start of a top-level ``i2c:`` block.
        if re.match(r"^i2c:\s*$", raw_line):
            in_i2c_block = True
            base_indent = None
            continue
        if not in_i2c_block:
            continue
        # Skip blank lines and comment-only lines.
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # A new top-level section ends the i2c block.
        if not raw_line.startswith((" ", "\t", "-")) and not raw_line.startswith("  "):
            indent_match = re.match(r"^(\s*)(\S)", raw_line)
            if indent_match and len(indent_match.group(1)) == 0:
                in_i2c_block = False
                continue
        m = re.match(r"\s*-\s*id:\s*(\S+)", raw_line)
        if m:
            value = m.group(1).split("#", 1)[0].strip().strip("\"'")
            ids.append(value)
    return ids


class SharedI2CBusTests(unittest.TestCase):
    """CORE-ABSTRACT-BUS-001B: single shared ``core_i2c`` bus consolidation.

    Asserts the schematic-correct hard rename across every in-scope Core
    abstract package, every in-scope expansion-package consumer default,
    and the hard-coded literal in
    ``packages/features/ceiling_halo_leds.yaml``. The two S3-variant
    Core / expansion packages are deliberately out-of-scope and are
    checked here only to confirm they retain their pre-001B bus ids.
    (The Mini family was removed by PRODUCT-DEP-MINI-001.)
    """

    def test_every_in_scope_core_package_defines_core_i2c(self) -> None:
        for pkg in SHARED_I2C_BUS_PACKAGES:
            fields = _find_i2c_bus_block(pkg.read_text(), "core_i2c")
            with self.subTest(package=pkg.name):
                self.assertIsNotNone(
                    fields,
                    f"{pkg.name} must define an i2c bus with `id: core_i2c` "
                    f"per CORE-ABSTRACT-BUS-001B.",
                )
                self.assertEqual(
                    fields.get("sda"),
                    CORE_I2C_SDA_PIN,
                    f"{pkg.name} core_i2c.sda must be {CORE_I2C_SDA_PIN} "
                    f"(schematic IO48 = I2C_SDA per S360-100-R4); "
                    f"got {fields.get('sda')!r}.",
                )
                self.assertEqual(
                    fields.get("scl"),
                    CORE_I2C_SCL_PIN,
                    f"{pkg.name} core_i2c.scl must be {CORE_I2C_SCL_PIN} "
                    f"(schematic IO45 = I2C_SCL per S360-100-R4); "
                    f"got {fields.get('scl')!r}.",
                )
                self.assertEqual(
                    fields.get("frequency"),
                    CORE_I2C_FREQUENCY,
                    f"{pkg.name} core_i2c.frequency must be "
                    f"{CORE_I2C_FREQUENCY}; got {fields.get('frequency')!r}.",
                )

    def test_legacy_bus_ids_absent_in_every_in_scope_core_package(self) -> None:
        for pkg in SHARED_I2C_BUS_PACKAGES:
            active_ids = _active_top_level_bus_ids(pkg.read_text())
            with self.subTest(package=pkg.name):
                for legacy in LEGACY_BUS_IDS:
                    self.assertNotIn(
                        legacy,
                        active_ids,
                        f"Legacy bus id `{legacy}` must not survive in "
                        f"{pkg.name} after CORE-ABSTRACT-BUS-001B (hard "
                        f"rename only). Active top-level i2c ids found: "
                        f"{active_ids!r}.",
                    )

    def test_every_in_scope_core_package_defines_exactly_one_i2c_bus(self) -> None:
        for pkg in SHARED_I2C_BUS_PACKAGES:
            active_ids = _active_top_level_bus_ids(pkg.read_text())
            with self.subTest(package=pkg.name):
                self.assertEqual(
                    active_ids,
                    ["core_i2c"],
                    f"{pkg.name} must define exactly one i2c bus "
                    f"(`core_i2c`) per CORE-ABSTRACT-BUS-001B operator "
                    f"decision #4 (legacy bus ids removed; no parallel "
                    f"definitions). Active top-level i2c ids found: "
                    f"{active_ids!r}.",
                )

    def test_every_in_scope_consumer_default_resolves_to_core_i2c(self) -> None:
        for pkg, sub_name in SHARED_I2C_CONSUMER_DEFAULTS:
            value = _substitution_value(pkg.read_text(), sub_name)
            with self.subTest(package=pkg.name, substitution=sub_name):
                self.assertEqual(
                    value,
                    "core_i2c",
                    f"{pkg.name} substitution `{sub_name}` default must "
                    f"be `core_i2c` per CORE-ABSTRACT-BUS-001B; "
                    f"got {value!r}.",
                )

    def test_ceiling_halo_leds_literal_rebound_to_core_i2c(self) -> None:
        text = CEILING_HALO_LEDS_PACKAGE.read_text()
        # Active (non-comment) i2c_id: literal must be core_i2c.
        active_value: Optional[str] = None
        for line in text.splitlines():
            stripped = line.lstrip()
            if stripped.startswith("#"):
                continue
            m = re.match(r"i2c_id:\s*(\S+)", stripped)
            if m:
                active_value = m.group(1).split("#", 1)[0].strip().strip("\"'")
                break
        self.assertEqual(
            active_value,
            "core_i2c",
            f"`packages/features/ceiling_halo_leds.yaml` hard-coded "
            f"`i2c_id:` literal must be `core_i2c` per "
            f"CORE-ABSTRACT-BUS-001B; got {active_value!r}.",
        )
        # The literal `halo_i2c` must not appear on any active line.
        for line in text.splitlines():
            stripped = line.lstrip()
            if stripped.startswith("#"):
                continue
            self.assertNotIn(
                "halo_i2c",
                line,
                f"`halo_i2c` must not appear on any active line in "
                f"ceiling_halo_leds.yaml after CORE-ABSTRACT-BUS-001B; "
                f"found on line: {line!r}.",
            )

    def test_fan_gp8403_binds_core_i2c_via_substitution(self) -> None:
        text = FAN_GP8403_PACKAGE.read_text()
        default = _substitution_value(text, "fan_dac_i2c_id")
        self.assertEqual(
            default,
            "core_i2c",
            "fan_gp8403.yaml fan_dac_i2c_id default must be core_i2c "
            "per CORE-ABSTRACT-BUS-001B.",
        )
        # The gp8403: block must consume the substitution (not a literal).
        self.assertRegex(
            text,
            r"gp8403:\s*\n[^\n]*\n[^\n]*i2c_id:\s*\$\{fan_dac_i2c_id\}",
            "fan_gp8403.yaml `gp8403:` block must bind "
            "`i2c_id: ${fan_dac_i2c_id}` so the rename flows through.",
        )

    def test_fan_dac_alias_includes_fan_gp8403_implementation(self) -> None:
        text = GP8403_FANDAC_ALIAS_PACKAGE.read_text()
        self.assertIn(
            "!include fan_gp8403.yaml",
            text,
            "packages/expansions/fan_dac.yaml must remain a thin "
            "`!include` of fan_gp8403.yaml so the canonical FanDAC alias "
            "inherits the core_i2c rebind without adding parallel "
            "substitutions.",
        )

    def test_sx1509_binds_core_i2c_via_substitution(self) -> None:
        text = SX1509_PACKAGE.read_text()
        default = _substitution_value(text, "sx1509_i2c_id")
        self.assertEqual(
            default,
            "core_i2c",
            "gpio_expander_sx1509.yaml sx1509_i2c_id default must be "
            "core_i2c per CORE-ABSTRACT-BUS-001B.",
        )
        # The sx1509: block must consume the substitution.
        self.assertRegex(
            text,
            r"sx1509:\s*\n[^\n]*\n[^\n]*i2c_id:\s*\$\{sx1509_i2c_id\}",
            "gpio_expander_sx1509.yaml `sx1509:` block must bind "
            "`i2c_id: ${sx1509_i2c_id}` so the rename flows through.",
        )

    def test_generate_test_configs_does_not_set_expansion_i2c_override(self) -> None:
        text = GENERATE_TEST_CONFIGS_SCRIPT.read_text()
        # The pre-001B helper hard-coded `fan_dac_i2c_id: expansion_i2c`
        # as a per-product override for the ceiling lineage. The default
        # in fan_gp8403.yaml now resolves to core_i2c directly, so the
        # override must be removed.
        self.assertNotIn(
            "fan_dac_i2c_id: expansion_i2c",
            text,
            "tests/generate_test_configs.py must not emit the pre-001B "
            "`fan_dac_i2c_id: expansion_i2c` override; the fan_gp8403.yaml "
            "default already resolves to core_i2c after "
            "CORE-ABSTRACT-BUS-001B.",
        )

    def test_out_of_scope_ceiling_s3_keeps_i2c_primary(self) -> None:
        # The S3 ceiling Core variant has a different board lineage and
        # keeps `i2c_primary` on GPIO17/GPIO18. A future 001B sweep must
        # not silently fold it into the Core namespace.
        text = SENSE360_CORE_CEILING_S3.read_text()
        fields = _find_i2c_bus_block(text, "i2c_primary")
        self.assertIsNotNone(
            fields,
            "sense360_core_ceiling_s3.yaml must retain its `i2c_primary` "
            "bus definition (out-of-scope for CORE-ABSTRACT-BUS-001B per "
            "operator decision #10).",
        )

    # PRODUCT-DEP-MINI-001 removed the Mini product range and its Mini-only
    # packages (sense360_core_mini.yaml, mini_onboard_sensors.yaml). The
    # former ``test_out_of_scope_mini_keeps_i2c0`` guard is dropped because
    # the file it asserted on no longer exists.

    def test_no_legacy_bus_id_in_any_active_consumer_line(self) -> None:
        # Sweep every package YAML under `packages/` for active
        # ``i2c_id: <legacy>`` lines. The two out-of-scope S3 expansion
        # packages (airiq_ceiling_s3.yaml, comfort_ceiling_s3.yaml) are
        # allowed to keep ``i2c_primary``. (The Mini-family helpers were
        # removed by PRODUCT-DEP-MINI-001 and are no longer on disk.) Every
        # other active reference to a legacy id is a regression.
        out_of_scope_paths = {
            REPO_ROOT / "packages" / "expansions" / "airiq_ceiling_s3.yaml",
            REPO_ROOT / "packages" / "expansions" / "comfort_ceiling_s3.yaml",
            REPO_ROOT / "packages" / "hardware" / "sense360_core_ceiling_s3.yaml",
        }
        for yaml_path in PACKAGES_DIR.rglob("*.yaml"):
            if yaml_path in out_of_scope_paths:
                continue
            text = yaml_path.read_text()
            for line_no, raw_line in enumerate(text.splitlines(), start=1):
                stripped = raw_line.lstrip()
                if stripped.startswith("#"):
                    continue
                m = re.search(
                    r"\bi2c_id:\s*(\S+)|^\s*-?\s*id:\s*(\S+)",
                    raw_line,
                )
                if not m:
                    continue
                value = (m.group(1) or m.group(2) or "").split("#", 1)[0].strip()
                value = value.strip("\"'")
                with self.subTest(file=str(yaml_path.relative_to(REPO_ROOT)), line=line_no):
                    self.assertNotIn(
                        value,
                        LEGACY_BUS_IDS,
                        f"Active reference to legacy bus id `{value}` "
                        f"found at {yaml_path.relative_to(REPO_ROOT)}:{line_no} "
                        f"after CORE-ABSTRACT-BUS-001B. Either rebind to "
                        f"core_i2c or add to the explicit out-of-scope list "
                        f"in this test.",
                    )

    def test_no_legacy_pin_substitutions_in_in_scope_core_packages(self) -> None:
        # The pre-001B Core packages exposed ``i2c0_sda_pin`` /
        # ``i2c0_scl_pin`` / ``i2c0_frequency`` / ``i2c1_*`` /
        # ``halo_i2c_*`` / ``expansion_i2c_*`` pin substitutions. The
        # recommended retirement path (CORE-ABSTRACT-BUS-001B operator
        # decisions / risk note #4) inlines GPIO48 / GPIO45 / 400kHz into
        # each Core package and retires the substitutions.
        retired_subs = (
            "i2c0_sda_pin",
            "i2c0_scl_pin",
            "i2c0_frequency",
            "i2c1_sda_pin",
            "i2c1_scl_pin",
            "i2c1_frequency",
            "halo_i2c_sda_pin",
            "halo_i2c_scl_pin",
            "expansion_i2c_sda_pin",
            "expansion_i2c_scl_pin",
        )
        for pkg in SHARED_I2C_BUS_PACKAGES:
            text = pkg.read_text()
            for sub_name in retired_subs:
                value = _substitution_value(text, sub_name)
                with self.subTest(package=pkg.name, substitution=sub_name):
                    self.assertIsNone(
                        value,
                        f"Legacy pin substitution `{sub_name}` must be "
                        f"retired from {pkg.name} per "
                        f"CORE-ABSTRACT-BUS-001B (the consolidated bus "
                        f"inlines GPIO48 / GPIO45 / 400kHz).",
                    )


# ============================================================================
# CORE-ABSTRACT-BUS-SX1509-001 — neutral FanPWM SX1509 binding layer tests
# ============================================================================
#
# These tests pin the neutral, product-agnostic SX1509 binding layer added by
# CORE-ABSTRACT-BUS-SX1509-001 in
# ``packages/expansions/fan_pwm_sx1509.yaml``. The binding satisfies the
# explicit "next prerequisite" recorded by PWM-BLOCKER-REMOVAL-001 (PR #586)
# operator decision D2:
#
#   * TachPMW1..4 (per-fan PWM drive) -> SX1509 channels 0..3
#   * Pul_Cou1..4 (per-fan tach feedback) -> SX1509 channels 4..7
#   * TachIO (shared tach passthrough) -> ESP32 IO16 (direct, NOT the expander)
#
# The layer is BINDING-ONLY: it adds no FanPWM product, no WebFlash surface,
# and no product-facing entities, and it does not resurrect the retired
# ``expansion_gpio1..4`` substitutions.

# SX1509 PWM-drive output ids (TachPMW1..4 -> channels 0..3) and their channel
# substitutions, in channel order.
FAN_PWM_DRIVE_BINDINGS = [
    ("fan_pwm_drive_1", "fan_pwm_drive_1_channel", "0"),
    ("fan_pwm_drive_2", "fan_pwm_drive_2_channel", "1"),
    ("fan_pwm_drive_3", "fan_pwm_drive_3_channel", "2"),
    ("fan_pwm_drive_4", "fan_pwm_drive_4_channel", "3"),
]

# SX1509 tach binary-sensor ids (Pul_Cou1..4 -> channels 4..7) and their
# channel substitutions, in channel order.
FAN_PWM_TACH_BINDINGS = [
    ("fan_pwm_tach_1", "fan_pwm_tach_1_channel", "4"),
    ("fan_pwm_tach_2", "fan_pwm_tach_2_channel", "5"),
    ("fan_pwm_tach_3", "fan_pwm_tach_3_channel", "6"),
    ("fan_pwm_tach_4", "fan_pwm_tach_4_channel", "7"),
]


class FanPwmSx1509BindingExistsTests(unittest.TestCase):
    """The neutral FanPWM SX1509 binding package exists."""

    def test_binding_package_present(self) -> None:
        self.assertTrue(
            FAN_PWM_SX1509_PACKAGE.is_file(),
            "packages/expansions/fan_pwm_sx1509.yaml must exist — it is the "
            "CORE-ABSTRACT-BUS-SX1509-001 neutral binding prerequisite for "
            "PACKAGE-PWM-001-IMPLEMENT-001.",
        )


class FanPwmSx1509BoundThroughCoreI2cTests(unittest.TestCase):
    """SX1509 is bound through the shared ``core_i2c`` bus."""

    def test_sx1509_i2c_id_defaults_to_core_i2c(self) -> None:
        value = _substitution_value(
            FAN_PWM_SX1509_PACKAGE.read_text(), "sx1509_i2c_id"
        )
        self.assertEqual(
            value,
            "core_i2c",
            "fan_pwm_sx1509.yaml sx1509_i2c_id default must be core_i2c "
            "(CORE-ABSTRACT-BUS-001B shared bus).",
        )

    def test_sx1509_block_binds_i2c_id_substitution(self) -> None:
        text = FAN_PWM_SX1509_PACKAGE.read_text()
        self.assertRegex(
            text,
            r"sx1509:\s*\n[^\n]*\n[^\n]*i2c_id:\s*\$\{sx1509_i2c_id\}",
            "fan_pwm_sx1509.yaml `sx1509:` block must bind "
            "`i2c_id: ${sx1509_i2c_id}` so the SX1509 hub rides core_i2c.",
        )

    def test_sx1509_interrupt_pin_is_gpio17(self) -> None:
        value = _substitution_value(
            FAN_PWM_SX1509_PACKAGE.read_text(), "sx1509_interrupt_pin"
        )
        self.assertEqual(
            value,
            "GPIO17",
            "fan_pwm_sx1509.yaml sx1509_interrupt_pin must be GPIO17 "
            "(schematic IO17 = expander_int per S360-100-R4).",
        )


class FanPwmSx1509EightChannelTests(unittest.TestCase):
    """The eight FanPWM-related expander channels are represented neutrally."""

    def test_drive_channel_substitutions_map_0_to_3(self) -> None:
        text = FAN_PWM_SX1509_PACKAGE.read_text()
        for _id, sub, expected in FAN_PWM_DRIVE_BINDINGS:
            with self.subTest(channel_sub=sub):
                self.assertEqual(
                    _substitution_value(text, sub),
                    expected,
                    f"{sub} must map to SX1509 channel {expected} "
                    f"(TachPMW -> channels 0..3 per operator decision D2).",
                )

    def test_tach_channel_substitutions_map_4_to_7(self) -> None:
        text = FAN_PWM_SX1509_PACKAGE.read_text()
        for _id, sub, expected in FAN_PWM_TACH_BINDINGS:
            with self.subTest(channel_sub=sub):
                self.assertEqual(
                    _substitution_value(text, sub),
                    expected,
                    f"{sub} must map to SX1509 channel {expected} "
                    f"(Pul_Cou -> channels 4..7 per operator decision D2).",
                )

    def test_four_sx1509_pwm_drive_outputs_declared(self) -> None:
        text = FAN_PWM_SX1509_PACKAGE.read_text()
        for out_id, sub, _expected in FAN_PWM_DRIVE_BINDINGS:
            with self.subTest(output=out_id):
                # Each drive output is an `output: platform: sx1509` entry that
                # references the channel substitution (not a raw GPIO).
                pattern = re.compile(
                    r"platform:\s*sx1509\s*\n"
                    r"(?:\s*[a-z0-9_]+:\s*\S+\s*\n)*?"
                    rf"\s*id:\s*{re.escape(out_id)}\s*\n"
                    r"(?:\s*[a-z0-9_]+:\s*\S+\s*\n)*?"
                    rf"\s*pin:\s*\$\{{{re.escape(sub)}\}}",
                    re.MULTILINE,
                )
                self.assertRegex(
                    text,
                    pattern,
                    f"{out_id} must be declared as `output: platform: sx1509` "
                    f"with `pin: ${{{sub}}}` (SX1509 on-chip PWM, not ledc).",
                )

    def test_four_sx1509_tach_binary_sensors_declared(self) -> None:
        text = FAN_PWM_SX1509_PACKAGE.read_text()
        for bs_id, sub, _expected in FAN_PWM_TACH_BINDINGS:
            with self.subTest(binary_sensor=bs_id):
                # Each tach input is a gpio binary_sensor whose pin routes
                # through the SX1509 expander at the channel substitution.
                pattern = re.compile(
                    rf"id:\s*{re.escape(bs_id)}\s*\n"
                    r"(?:\s*[a-z_]+:\s*\S+\s*\n)*?"
                    r"\s*pin:\s*\n"
                    r"\s*sx1509:\s*sx1509_expander\s*\n"
                    rf"\s*number:\s*\$\{{{re.escape(sub)}\}}",
                    re.MULTILINE,
                )
                self.assertRegex(
                    text,
                    pattern,
                    f"{bs_id} must be a gpio binary_sensor whose pin routes "
                    f"through `sx1509: sx1509_expander` at "
                    f"`number: ${{{sub}}}`.",
                )


class FanPwmTachIoDirectOnGpio16Tests(unittest.TestCase):
    """TachIO remains direct on ESP32 IO16 (NOT the expander)."""

    def test_tach_io_pin_is_gpio16(self) -> None:
        value = _substitution_value(
            FAN_PWM_SX1509_PACKAGE.read_text(), "tach_io_pin"
        )
        self.assertEqual(
            value,
            "GPIO16",
            "fan_pwm_sx1509.yaml tach_io_pin must be GPIO16 (schematic "
            "IO16 = TachIO, direct on the ESP32 per S360-100-R4 — TachIO is "
            "the only fan line NOT routed through the SX1509 expander).",
        )


class FanPwmNoDirectEsp32FanChannelTests(unittest.TestCase):
    """No direct ESP32 mapping is used for TachPMW1..4 / Pul_Cou1..4."""

    def test_drive_and_tach_channels_are_not_raw_gpio(self) -> None:
        text = FAN_PWM_SX1509_PACKAGE.read_text()
        # The eight FanPWM channels are SX1509 channel numbers, never raw
        # GPIO pins. Only TachIO (tach_io_pin) and the expander interrupt
        # (sx1509_interrupt_pin) are GPIO substitutions in this file.
        for _id, sub, _expected in FAN_PWM_DRIVE_BINDINGS + FAN_PWM_TACH_BINDINGS:
            value = _substitution_value(text, sub)
            with self.subTest(channel_sub=sub):
                self.assertIsNotNone(value, f"{sub} must be defined.")
                self.assertFalse(
                    value.upper().startswith("GPIO"),
                    f"{sub} must be an SX1509 channel number, not a raw ESP32 "
                    f"GPIO (operator decision D2: TachPMW1..4 / Pul_Cou1..4 are "
                    f"expander-routed, not direct ESP32).",
                )

    def test_no_ledc_pwm_drive_in_binding(self) -> None:
        text = FAN_PWM_SX1509_PACKAGE.read_text()
        for line in text.splitlines():
            stripped = line.lstrip()
            if stripped.startswith("#"):
                continue
            self.assertNotRegex(
                stripped,
                r"platform:\s*ledc",
                "fan_pwm_sx1509.yaml must not drive the four PWM channels via "
                "`ledc` (direct ESP32 PWM); the schematic routes TachPMW1..4 "
                "through the SX1509 expander.",
            )


class FanPwmSx1509NeutralityTests(unittest.TestCase):
    """The binding layer adds no FanPWM product / WebFlash / product surface."""

    def test_no_product_facing_entity_names(self) -> None:
        text = FAN_PWM_SX1509_PACKAGE.read_text()
        for line_no, line in enumerate(text.splitlines(), start=1):
            stripped = line.lstrip()
            if stripped.startswith("#"):
                continue
            with self.subTest(line=line_no):
                self.assertNotRegex(
                    stripped,
                    r"^name:\s",
                    "fan_pwm_sx1509.yaml is binding-only and must not declare "
                    "product-facing `name:` entities (no fan/light/sensor "
                    "names; downstream FanPWM owns user-facing entities).",
                )

    def test_no_esphome_block_or_webflash_surface(self) -> None:
        text = FAN_PWM_SX1509_PACKAGE.read_text()
        active = "\n".join(
            line for line in text.splitlines()
            if not line.lstrip().startswith("#")
        )
        for forbidden in ("esphome:", "artifact_name", "webflash", "fan:", "light:"):
            with self.subTest(token=forbidden):
                self.assertNotIn(
                    forbidden,
                    active,
                    f"fan_pwm_sx1509.yaml must not contain `{forbidden}` — it "
                    f"is a neutral binding layer, not a product / WebFlash / "
                    f"fan-controller surface.",
                )

    def test_no_expansion_gpio_substitutions_resurrected(self) -> None:
        text = FAN_PWM_SX1509_PACKAGE.read_text()
        for n in (1, 2, 3, 4):
            with self.subTest(n=n):
                self.assertIsNone(
                    _substitution_value(text, f"expansion_gpio{n}"),
                    f"fan_pwm_sx1509.yaml must not resurrect the retired "
                    f"`expansion_gpio{n}` substitution (CORE-ABSTRACT-BUS-001C "
                    f"retired the generic expansion_gpio* abstraction).",
                )


class FanRelayAndFanDacUnchangedTests(unittest.TestCase):
    """FanRelay / FanDAC remain unaffected by the SX1509 FanPWM binding."""

    def test_fan_relay_does_not_route_through_sx1509(self) -> None:
        text = FAN_RELAY_PACKAGE.read_text()
        self.assertNotIn(
            "sx1509",
            text,
            "fan_relay.yaml must remain a relay-only driver (the FanPWM "
            "SX1509 binding must not leak into FanRelay).",
        )

    def test_fan_dac_remains_thin_gp8403_include(self) -> None:
        text = FAN_DAC_PACKAGE.read_text()
        self.assertIn(
            "!include fan_gp8403.yaml",
            text,
            "fan_dac.yaml must remain a thin !include of fan_gp8403.yaml "
            "(unchanged by CORE-ABSTRACT-BUS-SX1509-001).",
        )

    def test_fan_gp8403_uses_dac_not_sx1509(self) -> None:
        text = FAN_GP8403_PACKAGE_PATH.read_text()
        self.assertIn(
            "gp8403:",
            text,
            "fan_gp8403.yaml must remain a GP8403 DAC driver.",
        )
        self.assertNotIn(
            "sx1509",
            text,
            "fan_gp8403.yaml (FanDAC) must not route through the SX1509 "
            "expander.",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

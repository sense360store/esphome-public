#!/usr/bin/env python3
"""PACKAGE-PWM-001-IMPLEMENT-001 invariants for the canonical FanPWM package.

These tests pin the PWM-drive-only FanPWM package implemented in
``packages/expansions/fan_pwm.yaml``. The package is the reconciliation of the
legacy single-channel ``fan_pwm.yaml`` against the four-channel SX1509 routing
recorded by the prior FanPWM chain:

* PR #586 (``PWM-BLOCKER-REMOVAL-001``) — operator decisions D1 (FanPWM is
  four-channel) / D2 (SX1509 routing: ``TachPMW1..4`` -> channels 0..3,
  ``Pul_Cou1..4`` -> channels 4..7, ``TachIO`` direct on ESP32 IO16).
* PR #587 (``CORE-ABSTRACT-BUS-SX1509-001``) — added the neutral binding-only
  layer ``packages/expansions/fan_pwm_sx1509.yaml`` that this package composes.
* PR #588 (``PACKAGE-PWM-TACH-STRATEGY-001``) — scoped the first package
  PWM-drive-only (four PWM outputs; no per-fan RPM; optional diagnostic binary
  tach only; ``TachIO`` / ``GPIO16`` reserved/pending).
* PR #589 (``PWM-SX1509-TACH-PROOF-001``) — compile/config proof that SX1509
  PWM-drive output IS supported and that an SX1509 pin cannot back an ESPHome
  ``pulse_counter`` RPM input (``[sx1509] is an invalid option for [pin]``).

What this file checks (PWM-drive-only contract):

  * ``packages/expansions/fan_pwm.yaml`` exists and parses as YAML.
  * It COMPOSES / reuses ``fan_pwm_sx1509.yaml`` via a ``packages:`` include
    (it does not duplicate the SX1509 channel definitions).
  * Four INDEPENDENT PWM-drive fan controllers are exposed, each bound to one
    of the neutral SX1509 PWM-drive outputs ``fan_pwm_drive_1..4`` in order.
  * No ``pulse_counter`` appears anywhere in the package (active lines).
  * No RPM sensor is exposed and no entity is named / unit'd as RPM.
  * ``TachIO`` / ``GPIO16`` is reserved/pending — not bound as an active
    sensor by this package.
  * Diagnostic tach binary states (the binding's ``fan_pwm_tach_1..4``) are
    not named or treated as RPM.
  * No direct ESP32 GPIO mapping (no ``ledc`` / raw ``GPIO``) is reintroduced
    for the four PWM/tach expander channels.
  * No FanPWM product YAML, WebFlash wrapper, release artifact, or
    ``config/webflash-builds.json`` row is added by this package slice.
  * FanRelay and FanDAC remain unchanged.

These are deliberately file-content / structural checks — they do not require
an ESPHome compile.

Run with::

    python3 tests/test_fan_pwm_package.py

or::

    python3 -m unittest tests.test_fan_pwm_package -v
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from typing import Optional

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent

FAN_PWM_PACKAGE = REPO_ROOT / "packages" / "expansions" / "fan_pwm.yaml"
FAN_PWM_SX1509_PACKAGE = REPO_ROOT / "packages" / "expansions" / "fan_pwm_sx1509.yaml"
FAN_RELAY_PACKAGE = REPO_ROOT / "packages" / "expansions" / "fan_relay.yaml"
FAN_DAC_PACKAGE = REPO_ROOT / "packages" / "expansions" / "fan_dac.yaml"
FAN_GP8403_PACKAGE = REPO_ROOT / "packages" / "expansions" / "fan_gp8403.yaml"

# The four neutral SX1509 PWM-drive output IDs (from fan_pwm_sx1509.yaml), in
# channel order, and the fan controller that must drive each one.
EXPECTED_DRIVE_OUTPUTS = [
    "fan_pwm_drive_1",
    "fan_pwm_drive_2",
    "fan_pwm_drive_3",
    "fan_pwm_drive_4",
]


# Register the same minimal set of ESPHome custom tags used by
# ``tests/validate_configs.py`` so ``yaml.safe_load`` can parse the package
# without a real ESPHome runtime. ``!include`` resolves to the scalar filename.
def _esphome_constructor(loader, node):  # type: ignore[no-untyped-def]
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None


for _tag in ("!secret", "!include", "!extend", "!lambda", "!remove"):
    yaml.add_constructor(_tag, _esphome_constructor, Loader=yaml.SafeLoader)


def _active_lines(text: str) -> list[str]:
    """Return only non-comment, non-blank lines from ``text``."""
    out: list[str] = []
    for line in text.splitlines():
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            continue
        out.append(line)
    return out


def _load(path: Path) -> dict:
    data = yaml.safe_load(path.read_text())
    assert isinstance(data, dict), f"{path.name} must parse as a YAML mapping."
    return data


class FanPwmPackageStructureTests(unittest.TestCase):
    """``packages/expansions/fan_pwm.yaml`` exists and parses as YAML."""

    def test_package_exists(self) -> None:
        self.assertTrue(
            FAN_PWM_PACKAGE.is_file(),
            f"Expected the canonical FanPWM package at {FAN_PWM_PACKAGE} — "
            "PACKAGE-PWM-001-IMPLEMENT-001 reconciles the existing "
            "fan_pwm.yaml in place.",
        )

    def test_package_parses_as_yaml_mapping(self) -> None:
        data = _load(FAN_PWM_PACKAGE)
        for key in ("packages", "fan"):
            self.assertIn(
                key,
                data,
                f"fan_pwm.yaml must declare a top-level `{key}:` block "
                "(composes the SX1509 binding + exposes the PWM fans).",
            )


class FanPwmComposesSx1509BindingTests(unittest.TestCase):
    """The package reuses ``fan_pwm_sx1509.yaml`` instead of duplicating it."""

    def test_includes_fan_pwm_sx1509(self) -> None:
        text = FAN_PWM_PACKAGE.read_text()
        self.assertIn(
            "!include fan_pwm_sx1509.yaml",
            text,
            "fan_pwm.yaml must compose the neutral binding via "
            "`!include fan_pwm_sx1509.yaml` (CORE-ABSTRACT-BUS-SX1509-001) "
            "rather than re-declaring the SX1509 channel map.",
        )

    def test_include_is_inside_a_packages_block(self) -> None:
        data = _load(FAN_PWM_PACKAGE)
        packages = data.get("packages")
        self.assertIsInstance(
            packages,
            dict,
            "fan_pwm.yaml `packages:` block must be a mapping of "
            "include names to !include targets.",
        )
        rendered = " ".join(str(v) for v in packages.values())
        self.assertIn(
            "fan_pwm_sx1509.yaml",
            rendered,
            "the `packages:` block must include fan_pwm_sx1509.yaml.",
        )

    def test_does_not_redeclare_sx1509_channels(self) -> None:
        # The SX1509 hub / channel outputs live in the binding only. The
        # canonical package must not re-declare an `sx1509:` hub or
        # `platform: sx1509` outputs (that would double-define the channels).
        text = FAN_PWM_PACKAGE.read_text()
        for line in _active_lines(text):
            stripped = line.lstrip()
            self.assertNotRegex(
                stripped,
                r"^sx1509:",
                "fan_pwm.yaml must not re-declare the `sx1509:` hub — it is "
                "owned by the composed fan_pwm_sx1509.yaml binding.",
            )
            self.assertNotRegex(
                stripped,
                r"platform:\s*sx1509",
                "fan_pwm.yaml must not re-declare `platform: sx1509` outputs "
                "— the four PWM-drive channels are owned by the binding.",
            )


class FanPwmFourIndependentDriveChannelsTests(unittest.TestCase):
    """Four independent PWM-drive fan controllers, one per SX1509 output."""

    def _fan_entries(self) -> list[dict]:
        data = _load(FAN_PWM_PACKAGE)
        fans = data.get("fan", [])
        self.assertIsInstance(
            fans, list, "fan_pwm.yaml `fan:` block must be a list."
        )
        return [f for f in fans if isinstance(f, dict)]

    def test_exactly_four_fan_controllers(self) -> None:
        fans = self._fan_entries()
        self.assertEqual(
            len(fans),
            4,
            "fan_pwm.yaml must expose exactly four independent fan "
            f"controllers (PWM-drive-only scope); found {len(fans)}.",
        )

    def test_each_fan_is_a_speed_platform(self) -> None:
        for fan in self._fan_entries():
            self.assertEqual(
                fan.get("platform"),
                "speed",
                f"fan {fan.get('id')!r} must be a `speed` fan platform "
                "driven by an SX1509 PWM output.",
            )

    def test_fans_drive_the_four_neutral_sx1509_outputs_in_order(self) -> None:
        outputs = [fan.get("output") for fan in self._fan_entries()]
        self.assertEqual(
            outputs,
            EXPECTED_DRIVE_OUTPUTS,
            "the four fan controllers must drive the neutral SX1509 "
            "PWM-drive outputs fan_pwm_drive_1..4 (channels 0..3) in order; "
            f"got {outputs!r}.",
        )

    def test_fan_controller_ids_are_distinct(self) -> None:
        ids = [fan.get("id") for fan in self._fan_entries()]
        self.assertEqual(
            len(set(ids)),
            4,
            f"the four fan controllers must have distinct ids; got {ids!r}.",
        )

    def test_binding_actually_defines_the_four_drive_outputs(self) -> None:
        # Cross-check: the composed binding really declares the four outputs
        # the fans reference, so composition resolves at compile time.
        binding_text = FAN_PWM_SX1509_PACKAGE.read_text()
        for out_id in EXPECTED_DRIVE_OUTPUTS:
            self.assertRegex(
                binding_text,
                rf"id:\s*{re.escape(out_id)}\b",
                f"fan_pwm_sx1509.yaml must declare the PWM-drive output "
                f"{out_id!r} that fan_pwm.yaml drives.",
            )


class FanPwmNoRpmNoPulseCounterTests(unittest.TestCase):
    """No RPM is exposed and no `pulse_counter` is used."""

    def test_no_pulse_counter_anywhere_active(self) -> None:
        for line in _active_lines(FAN_PWM_PACKAGE.read_text()):
            self.assertNotIn(
                "pulse_counter",
                line,
                "fan_pwm.yaml must not use `pulse_counter` on any active "
                "line — an SX1509 pin cannot back an ESPHome pulse_counter "
                "(PWM-SX1509-TACH-PROOF-001) and no native pulse_counter is "
                f"in scope for the PWM-drive-only package. Line: {line!r}",
            )

    def test_no_rpm_named_or_unit_entities(self) -> None:
        # No entity may be named "... RPM" or carry unit_of_measurement: RPM.
        for line in _active_lines(FAN_PWM_PACKAGE.read_text()):
            low = line.lower()
            if "name:" in low:
                self.assertNotIn(
                    "rpm",
                    low,
                    f"fan_pwm.yaml must expose no RPM-named entity (PWM-drive-"
                    f"only; no RPM claim). Line: {line!r}",
                )
            if "unit_of_measurement:" in low:
                self.assertNotIn(
                    "rpm",
                    low,
                    "fan_pwm.yaml must expose no entity with "
                    f"unit_of_measurement RPM. Line: {line!r}",
                )

    def test_no_sensor_block_exposing_rpm(self) -> None:
        # The PWM-drive-only package adds no `sensor:` RPM entities at all.
        data = _load(FAN_PWM_PACKAGE)
        sensors = data.get("sensor") or []
        if not isinstance(sensors, list):
            return
        for sensor in sensors:
            if not isinstance(sensor, dict):
                continue
            self.assertNotEqual(
                sensor.get("platform"),
                "pulse_counter",
                f"fan_pwm.yaml sensor {sensor.get('id')!r} must not be a "
                "pulse_counter (no per-fan RPM).",
            )
            self.assertNotEqual(
                str(sensor.get("unit_of_measurement", "")).upper(),
                "RPM",
                f"fan_pwm.yaml sensor {sensor.get('id')!r} must not report "
                "RPM.",
            )


class FanPwmTachIoReservedTests(unittest.TestCase):
    """``TachIO`` / ``GPIO16`` is reserved/pending — not an active sensor."""

    def test_tach_io_pin_not_consumed_as_a_sensor(self) -> None:
        # The binding exposes `tach_io_pin: GPIO16` as a substitution only.
        # This package must not consume it (e.g. as a pulse_counter / sensor
        # pin); it stays reserved/pending.
        for line in _active_lines(FAN_PWM_PACKAGE.read_text()):
            self.assertNotIn(
                "${tach_io_pin}",
                line,
                "fan_pwm.yaml must not consume `${tach_io_pin}` — TachIO / "
                f"GPIO16 stays reserved/pending in this package. Line: {line!r}",
            )

    def test_no_gpio16_active_binding(self) -> None:
        for line in _active_lines(FAN_PWM_PACKAGE.read_text()):
            self.assertNotRegex(
                line,
                r"\bGPIO16\b",
                "fan_pwm.yaml must not bind GPIO16 (TachIO) on an active "
                f"line — it is reserved/pending. Line: {line!r}",
            )


class FanPwmDiagnosticTachNotRpmTests(unittest.TestCase):
    """The composed diagnostic tach binary states are not RPM."""

    def test_binding_tach_inputs_are_binary_not_rpm(self) -> None:
        # The diagnostic tach states come from the binding's
        # `fan_pwm_tach_1..4` gpio binary_sensors. Confirm they are binary
        # (gpio) and not exposed as RPM sensors anywhere.
        binding_text = FAN_PWM_SX1509_PACKAGE.read_text()
        for n in (1, 2, 3, 4):
            self.assertRegex(
                binding_text,
                rf"id:\s*fan_pwm_tach_{n}\b",
                f"fan_pwm_sx1509.yaml must declare the diagnostic tach "
                f"binary input fan_pwm_tach_{n}.",
            )
        # The composed package must not relabel any tach state as RPM.
        for line in _active_lines(FAN_PWM_PACKAGE.read_text()):
            low = line.lower()
            if "tach" in low and "name:" in low:
                self.assertNotIn(
                    "rpm",
                    low,
                    "a diagnostic tach entity must never be named as RPM. "
                    f"Line: {line!r}",
                )


class FanPwmNoDirectEsp32MappingTests(unittest.TestCase):
    """No direct ESP32 GPIO mapping for the four PWM/tach expander channels."""

    def test_no_ledc_pwm_drive(self) -> None:
        for line in _active_lines(FAN_PWM_PACKAGE.read_text()):
            self.assertNotRegex(
                line.lstrip(),
                r"platform:\s*ledc",
                "fan_pwm.yaml must not drive the PWM channels via `ledc` "
                "(direct ESP32 PWM); TachPMW1..4 are SX1509-expander-routed "
                "(operator decision D2).",
            )

    def test_no_raw_gpio_for_expander_channels(self) -> None:
        # The only GPIO substitutions in the composed config are tach_io_pin
        # (GPIO16, reserved) and sx1509_interrupt_pin (GPIO17), both owned by
        # the binding. The canonical package itself must name no GPIO on an
        # active line (no direct ESP32 mapping for TachPMW/Pul_Cou).
        for line in _active_lines(FAN_PWM_PACKAGE.read_text()):
            self.assertNotRegex(
                line,
                r"\bGPIO\d+\b",
                "fan_pwm.yaml must not name any GPIO on an active line — the "
                "four PWM/tach expander channels are SX1509-routed and TachIO "
                f"stays abstract via the binding. Line: {line!r}",
            )


class FanPwmNoProductOrWebFlashSurfaceTests(unittest.TestCase):
    """PACKAGE-PWM-001-IMPLEMENT-001 adds no product / WebFlash / release surface."""

    def test_package_is_not_a_product(self) -> None:
        # A package layer artifact: no esphome: block, no artifact_name, no
        # webflash surface.
        data = _load(FAN_PWM_PACKAGE)
        for forbidden in ("esphome", "artifact_name"):
            self.assertNotIn(
                forbidden,
                data,
                f"fan_pwm.yaml must not declare a top-level `{forbidden}` — "
                "it is a package, not a product / WebFlash surface.",
            )
        active = "\n".join(_active_lines(FAN_PWM_PACKAGE.read_text())).lower()
        self.assertNotIn(
            "webflash",
            active,
            "fan_pwm.yaml must not reference a WebFlash surface on an active "
            "line.",
        )

    def test_no_fan_pwm_product_yaml_added(self) -> None:
        products_dir = REPO_ROOT / "products"
        if not products_dir.is_dir():
            self.skipTest("products/ directory not present in repo")
        offenders = []
        for path in products_dir.glob("**/*.yaml"):
            name = path.name.lower()
            if "fanpwm" in name or "fan-pwm" in name or "fan_pwm" in name:
                offenders.append(path.relative_to(REPO_ROOT).as_posix())
        # The legacy standalone fan board product (sense360-fan-pwm.yaml)
        # predates this slice and is allowed; PACKAGE-PWM-001-IMPLEMENT-001
        # adds NO new FanPWM product YAML.
        allowed = {"products/sense360-fan-pwm.yaml"}
        unexpected = sorted(set(offenders) - allowed)
        self.assertEqual(
            unexpected,
            [],
            "PACKAGE-PWM-001-IMPLEMENT-001 is a package slice and must add no "
            f"new FanPWM product YAML; unexpected: {unexpected!r}.",
        )

    def test_no_fan_pwm_token_in_webflash_builds(self) -> None:
        builds = REPO_ROOT / "config" / "webflash-builds.json"
        if not builds.is_file():
            self.skipTest("config/webflash-builds.json not present in repo")
        text = builds.read_text()
        self.assertNotIn(
            "FanPWM",
            text,
            "config/webflash-builds.json must not contain a FanPWM token — "
            "PACKAGE-PWM-001-IMPLEMENT-001 does not advance WEBFLASH-PWM-001 "
            "or RELEASE-PWM-001.",
        )


class FanRelayAndFanDacUnchangedTests(unittest.TestCase):
    """FanRelay / FanDAC remain unaffected by the FanPWM implementation."""

    def test_fan_relay_does_not_route_through_sx1509(self) -> None:
        self.assertNotIn(
            "sx1509",
            FAN_RELAY_PACKAGE.read_text(),
            "fan_relay.yaml must remain a relay-only driver (the FanPWM "
            "SX1509 implementation must not leak into FanRelay).",
        )

    def test_fan_dac_remains_thin_gp8403_include(self) -> None:
        self.assertIn(
            "!include fan_gp8403.yaml",
            FAN_DAC_PACKAGE.read_text(),
            "fan_dac.yaml must remain a thin !include of fan_gp8403.yaml.",
        )

    def test_fan_gp8403_uses_dac_not_sx1509(self) -> None:
        text = FAN_GP8403_PACKAGE.read_text()
        self.assertIn("gp8403:", text, "fan_gp8403.yaml must remain a DAC driver.")
        self.assertNotIn(
            "sx1509",
            text,
            "fan_gp8403.yaml (FanDAC) must not route through the SX1509 "
            "expander.",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

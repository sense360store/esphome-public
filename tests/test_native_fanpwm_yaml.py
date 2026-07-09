#!/usr/bin/env python3
"""S360-311-NATIVE-FANPWM-YAML-001 — native ESP32-S3 GPIO FanPWM candidate.

This module pins the invariants for the NATIVE ESP32-S3 GPIO FanPWM
candidate added by S360-311-NATIVE-FANPWM-YAML-001:

  * ``packages/expansions/fan_pwm_native.yaml`` — native FanPWM package
    (four native ``output: platform: ledc`` PWM-drive outputs + three
    native ``sensor: platform: pulse_counter`` tach inputs).
  * ``products/compile-only/ceiling-poe-fanpwm-native.yaml`` — native
    compile-only skeleton composing the native package on the Core
    ceiling + PoE PSU + base/health base.
  * ``config/compile-only-targets.json`` target
    ``ceiling-poe-fanpwm-native-compile-only``.

These are the **stricter native-path** guards required by the work item.
They sit alongside (they do NOT replace) the historical SX1509 /
pulse_counter compile/config proof
(``tests/test_sx1509_tach_pulse_counter_proof.py`` +
``tests/esphome/sx1509_pulse_counter_proof.yaml``), which stays in place
as evidence for the architectural rule.

Pinned invariants:

  1. The native candidate does NOT use ``sx1509:`` for PWM output or for
     any tach / pulse_counter input. No ``pulse_counter`` pin routes
     through an ``sx1509:`` mapping.
  2. PWM outputs use the native ESP32-S3 GPIO map (``TachPMW1..4`` ->
     ``GPIO10`` / ``GPIO11`` / ``GPIO12`` / ``GPIO39``) via ``ledc``.
  3. Tach inputs use the native ESP32-S3 GPIO map (``Pul_Cou1`` /
     ``Pul_Cou2`` / ``Pul_Cou4`` -> ``GPIO17`` / ``GPIO18`` / ``GPIO9``)
     via ``pulse_counter``. ``Pul_Cou3`` (``GPIO46``) is disabled / TBD
     (collides with the Core ``fan_status_led_pin``); ``TachIO``
     (``GPIO16``) is reserved / pending — neither is actively bound.
  4. The candidate makes no RPM claim (no ``rpm`` name / unit anywhere)
     and the compile-only target keeps ``rpm_supported`` false. The
     target is ``validated-full-compile`` (S360-311-NATIVE-FANPWM-COMPILE-001
     ran a full ``esphome compile`` against the native composition and it
     PASSED, rc=0); a green compile is compile coverage only and is NOT
     RPM / tach bench validation.
  5. FanPWM stays absent from ``config/webflash-builds.json``; the native
     compile-only target declares no ``artifact_name`` / no
     ``webflash_build_matrix``.
  6. The legacy SX1509 FanPWM YAMLs and the historical SX1509 proof
     remain in place (superseded / manual-only, not release-selectable).

Run with::

    python3 tests/test_native_fanpwm_yaml.py

or::

    python3 -m unittest tests.test_native_fanpwm_yaml -v
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from typing import Any, Dict, List

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent

NATIVE_PACKAGE = REPO_ROOT / "packages" / "expansions" / "fan_pwm_native.yaml"
NATIVE_SKELETON = (
    REPO_ROOT / "products" / "compile-only" / "ceiling-poe-fanpwm-native.yaml"
)
NATIVE_SKELETON_REL = "products/compile-only/ceiling-poe-fanpwm-native.yaml"
NATIVE_TARGET_ID = "ceiling-poe-fanpwm-native-compile-only"
CONFIG_STRING = "Ceiling-POE-FanPWM"

COMPILE_ONLY_TARGETS = REPO_ROOT / "config" / "compile-only-targets.json"
WEBFLASH_BUILDS = REPO_ROOT / "config" / "webflash-builds.json"

# Legacy / superseded SX1509 FanPWM YAMLs that must be preserved.
LEGACY_PACKAGE = REPO_ROOT / "packages" / "expansions" / "fan_pwm.yaml"
LEGACY_SX1509_BINDING = REPO_ROOT / "packages" / "expansions" / "fan_pwm_sx1509.yaml"
LEGACY_SKELETON = (
    REPO_ROOT / "products" / "compile-only" / "ceiling-poe-fanpwm.yaml"
)
SX1509_PROOF_FIXTURE = (
    REPO_ROOT / "tests" / "esphome" / "sx1509_pulse_counter_proof.yaml"
)
SX1509_PROOF_TEST = REPO_ROOT / "tests" / "test_sx1509_tach_pulse_counter_proof.py"

# Schematic-printed native ESP32-S3 GPIO map (S360-100-NATIVE-FAN-GPIO-MAP-001).
EXPECTED_PWM_PINS = {
    "fan_pwm_native_pwm_1_pin": "GPIO10",  # TachPMW1
    "fan_pwm_native_pwm_2_pin": "GPIO11",  # TachPMW2
    "fan_pwm_native_pwm_3_pin": "GPIO12",  # TachPMW3
    "fan_pwm_native_pwm_4_pin": "GPIO39",  # TachPMW4
}
EXPECTED_TACH_PINS = {
    "fan_pwm_native_tach_1_pin": "GPIO17",  # Pul_Cou1
    "fan_pwm_native_tach_2_pin": "GPIO18",  # Pul_Cou2
    "fan_pwm_native_tach_4_pin": "GPIO9",   # Pul_Cou4
}


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
yaml.add_multi_constructor("!include_dir_", _esphome_constructor, Loader=yaml.SafeLoader)


def _load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text())


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _active_lines(text: str) -> List[str]:
    out: List[str] = []
    for line in text.splitlines():
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            continue
        out.append(line)
    return out


_PULSE_COUNTER_SX1509_PIN = re.compile(
    r"platform:\s*pulse_counter\b(?:.*\n)*?\s*pin:\s*\n\s*sx1509:\s*\w+",
    re.MULTILINE,
)


class NativePackageExistsTests(unittest.TestCase):
    def test_native_package_exists(self) -> None:
        self.assertTrue(
            NATIVE_PACKAGE.is_file(),
            "S360-311-NATIVE-FANPWM-YAML-001 must add the native FanPWM "
            f"package at {NATIVE_PACKAGE}",
        )

    def test_native_package_parses(self) -> None:
        data = _load_yaml(NATIVE_PACKAGE)
        self.assertIsInstance(data, dict)
        for key in ("substitutions", "output", "fan", "sensor"):
            self.assertIn(key, data, f"native package must declare `{key}:`")

    def test_native_skeleton_exists(self) -> None:
        self.assertTrue(
            NATIVE_SKELETON.is_file(),
            "S360-311-NATIVE-FANPWM-YAML-001 must add the native FanPWM "
            f"compile-only skeleton at {NATIVE_SKELETON}",
        )


class NativeNoSx1509Tests(unittest.TestCase):
    """Rule (1): native candidate uses no SX1509 for PWM or tach."""

    def test_native_package_has_no_sx1509_on_active_line(self) -> None:
        for line in _active_lines(NATIVE_PACKAGE.read_text()):
            self.assertNotIn(
                "sx1509",
                line.lower(),
                "native FanPWM package must not reference sx1509 on any "
                f"active line (native ESP32 GPIO only). Line: {line!r}",
            )

    def test_native_skeleton_has_no_sx1509_on_active_line(self) -> None:
        for line in _active_lines(NATIVE_SKELETON.read_text()):
            self.assertNotIn(
                "sx1509",
                line.lower(),
                "native FanPWM skeleton must not reference sx1509 on any "
                f"active line. Line: {line!r}",
            )

    def test_native_skeleton_does_not_include_sx1509_binding(self) -> None:
        text = NATIVE_SKELETON.read_text()
        self.assertNotIn(
            "packages/expansions/fan_pwm_sx1509.yaml",
            text,
            "native FanPWM skeleton must not compose the legacy SX1509 "
            "binding layer",
        )
        self.assertIn(
            "packages/expansions/fan_pwm_native.yaml",
            text,
            "native FanPWM skeleton must compose the native FanPWM package",
        )

    def test_no_pulse_counter_routes_through_sx1509(self) -> None:
        for path in (NATIVE_PACKAGE, NATIVE_SKELETON):
            with self.subTest(file=path.name):
                self.assertIsNone(
                    _PULSE_COUNTER_SX1509_PIN.search(path.read_text()),
                    "no pulse_counter pin may route through an sx1509: "
                    "mapping in the native FanPWM candidate "
                    f"({path.name})",
                )


class NativePwmOutputTests(unittest.TestCase):
    """Rule (2): native ledc PWM outputs on the schematic-printed pins."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.data = _load_yaml(NATIVE_PACKAGE)
        cls.subs = cls.data.get("substitutions", {}) or {}
        cls.outputs = cls.data.get("output", []) or []

    def test_four_ledc_outputs(self) -> None:
        platforms = [o.get("platform") for o in self.outputs if isinstance(o, dict)]
        self.assertEqual(
            platforms,
            ["ledc", "ledc", "ledc", "ledc"],
            "native FanPWM package must declare four native ledc PWM-drive "
            f"outputs; got platforms {platforms!r}",
        )

    def test_no_sx1509_output_platform(self) -> None:
        for o in self.outputs:
            if isinstance(o, dict):
                self.assertNotEqual(
                    o.get("platform"),
                    "sx1509",
                    "native FanPWM package must not declare an sx1509 output",
                )

    def test_pwm_pins_match_native_map(self) -> None:
        for sub, expected in EXPECTED_PWM_PINS.items():
            with self.subTest(substitution=sub):
                self.assertEqual(
                    self.subs.get(sub),
                    expected,
                    f"{sub} must map to the schematic-printed native "
                    f"ESP32-S3 GPIO {expected}",
                )

    def test_four_speed_fan_controllers(self) -> None:
        fans = self.data.get("fan", []) or []
        platforms = [f.get("platform") for f in fans if isinstance(f, dict)]
        self.assertEqual(platforms, ["speed"] * 4)


class NativeTachInputTests(unittest.TestCase):
    """Rule (3): native pulse_counter tach inputs; IO46/IO16 not bound."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.data = _load_yaml(NATIVE_PACKAGE)
        cls.subs = cls.data.get("substitutions", {}) or {}
        cls.sensors = cls.data.get("sensor", []) or []
        cls.text = NATIVE_PACKAGE.read_text()

    def test_three_native_pulse_counters(self) -> None:
        platforms = [s.get("platform") for s in self.sensors if isinstance(s, dict)]
        self.assertEqual(
            platforms,
            ["pulse_counter", "pulse_counter", "pulse_counter"],
            "native FanPWM package must declare three native pulse_counter "
            f"tach inputs (Pul_Cou1/2/4); got {platforms!r}",
        )

    def test_tach_pins_match_native_map(self) -> None:
        for sub, expected in EXPECTED_TACH_PINS.items():
            with self.subTest(substitution=sub):
                self.assertEqual(
                    self.subs.get(sub),
                    expected,
                    f"{sub} must map to the schematic-printed native "
                    f"ESP32-S3 GPIO {expected}",
                )

    def test_pulse_counter_pins_are_native_substitutions(self) -> None:
        # Every pulse_counter pin must reference a native pin substitution,
        # never an sx1509 mapping.
        for s in self.sensors:
            if not isinstance(s, dict) or s.get("platform") != "pulse_counter":
                continue
            pin = s.get("pin")
            with self.subTest(id=s.get("id")):
                self.assertIsInstance(
                    pin,
                    str,
                    "pulse_counter pin must be a native scalar GPIO "
                    "substitution, not an expander mapping",
                )
                self.assertTrue(
                    pin.startswith("${fan_pwm_native_tach_"),
                    f"pulse_counter pin {pin!r} must be a native tach "
                    "substitution",
                )

    def test_pul_cou3_io46_not_actively_bound(self) -> None:
        # IO46 collides with the Core fan_status_led_pin; Pul_Cou3 stays TBD.
        for line in _active_lines(self.text):
            self.assertNotRegex(
                line,
                r"\bGPIO46\b",
                "Pul_Cou3 (IO46) must stay disabled / TBD — it collides "
                f"with the Core fan_status_led_pin. Line: {line!r}",
            )

    def test_tach_io_gpio16_not_actively_bound(self) -> None:
        # TachIO (IO16) shared passthrough is reserved/pending. It may appear
        # as a reserved substitution definition, but must not be consumed by
        # an output/sensor/pin binding.
        for line in _active_lines(self.text):
            self.assertNotIn(
                "${fan_pwm_native_tach_io_pin}",
                line,
                "TachIO (GPIO16) must stay reserved / pending — it must not "
                f"be consumed by an active binding. Line: {line!r}",
            )


class NativeNoRpmClaimTests(unittest.TestCase):
    """Rule (4): no RPM claim in the native candidate YAMLs."""

    def test_no_rpm_named_or_unit_entities(self) -> None:
        for path in (NATIVE_PACKAGE, NATIVE_SKELETON):
            for line in _active_lines(path.read_text()):
                low = line.lower()
                if "name:" in low or "unit_of_measurement:" in low:
                    with self.subTest(file=path.name, line=line):
                        self.assertNotIn(
                            "rpm",
                            low,
                            "native FanPWM candidate must expose no "
                            f"RPM-named / RPM-unit entity. Line: {line!r}",
                        )


class NativeCompileOnlyTargetTests(unittest.TestCase):
    """Rules (4)/(5): the compile-only target is honest and non-release."""

    @classmethod
    def setUpClass(cls) -> None:
        doc = _load_json(COMPILE_ONLY_TARGETS)
        cls.by_id = {t.get("id"): t for t in doc.get("targets", []) if t.get("id")}
        cls.target = cls.by_id.get(NATIVE_TARGET_ID)

    def test_target_registered(self) -> None:
        self.assertIsNotNone(
            self.target,
            f"native compile-only target {NATIVE_TARGET_ID!r} must be "
            "registered in config/compile-only-targets.json",
        )

    def test_target_points_at_native_skeleton(self) -> None:
        self.assertEqual(
            self.target.get("product_yaml"), NATIVE_SKELETON_REL
        )

    def test_target_config_string(self) -> None:
        self.assertEqual(self.target.get("config_string"), CONFIG_STRING)

    def test_target_shipment_status_compile_only(self) -> None:
        self.assertEqual(self.target.get("shipment_status"), "compile-only")

    def test_target_disallows_webflash_exposure(self) -> None:
        self.assertFalse(self.target.get("webflash_exposure_allowed_now"))

    def test_target_not_blocked(self) -> None:
        self.assertFalse(self.target.get("blocked"))

    def test_target_rpm_supported_false(self) -> None:
        self.assertFalse(
            self.target.get("rpm_supported", False),
            "native FanPWM target must keep rpm_supported false until "
            "measured bench evidence exists",
        )

    def test_target_compile_status_is_validated_full_compile(self) -> None:
        # S360-311-NATIVE-FANPWM-COMPILE-001: a full `esphome compile` run
        # was performed against the native composition and it PASSED (rc=0;
        # ESPHome 2026.4.5, esp32-s3-devkitc-1 / espidf ESP-IDF v5.5.4;
        # commit 643bbd3; RAM 13.2% / Flash 51.7%, real firmware.bin), so
        # the native target now records validated-full-compile, superseding
        # the prior pending-ci marker. The legacy SX1509 full-compile run
        # does not transfer; this is the native composition's own proof.
        self.assertEqual(
            self.target.get("compile_validation_status"),
            "validated-full-compile",
            "native FanPWM target must record compile_validation_status: "
            "validated-full-compile — S360-311-NATIVE-FANPWM-COMPILE-001 ran "
            "a full esphome compile against the native composition and it "
            "passed (rc=0), superseding the prior pending-ci marker",
        )

    def test_target_does_not_declare_webflash_build_matrix(self) -> None:
        self.assertNotIn("webflash_build_matrix", self.target)

    def test_target_does_not_declare_artifact_name(self) -> None:
        self.assertNotIn("artifact_name", self.target)


class FanPwmStaysOutOfWebFlashTests(unittest.TestCase):
    """Rule (5), amended by HW-RELEASE-001 (docs/hw-release-001.md,
    owner decision of record, 2026-07-09): FanPWM metadata build rows now
    exist by owner declaration, so the guard is a channel pin instead of
    an absence pin — every FanPWM-bearing row stays on the preview
    channel and is never stable.
    """

    def test_fanpwm_builds_rows_are_preview_never_stable(self) -> None:
        data = json.loads(WEBFLASH_BUILDS.read_text())
        rows = [
            row
            for row in (data.get("builds", []) or [])
            if "FanPWM" in (row.get("config_string") or "").split("-")
        ]
        self.assertTrue(
            rows,
            "expected FanPWM metadata build rows in "
            "config/webflash-builds.json (declared by HW-RELEASE-001)",
        )
        for row in rows:
            cfg = row.get("config_string")
            self.assertNotEqual(
                row.get("channel"),
                "stable",
                f"{cfg!r}: FanPWM build rows are NEVER channel stable",
            )
            self.assertEqual(
                row.get("channel"),
                "preview",
                f"{cfg!r}: FanPWM build rows are preview-channel only "
                "(HW-RELEASE-001); the native candidate itself remains "
                "non-release / compile-only",
            )
            self.assertNotIn(
                "-stable",
                row.get("artifact_name") or "",
                f"{cfg!r}: FanPWM artifact_name must never claim stable",
            )


class LegacySx1509PreservedTests(unittest.TestCase):
    """Rule (6): legacy SX1509 YAMLs and the historical proof stay in place."""

    def test_legacy_yamls_preserved(self) -> None:
        for path in (LEGACY_PACKAGE, LEGACY_SX1509_BINDING, LEGACY_SKELETON):
            self.assertTrue(
                path.is_file(),
                f"legacy / superseded SX1509 FanPWM YAML {path.name} must "
                "be preserved (manual-only / historical), not deleted",
            )

    def test_legacy_yamls_carry_superseded_banner(self) -> None:
        for path in (LEGACY_PACKAGE, LEGACY_SX1509_BINDING, LEGACY_SKELETON):
            with self.subTest(file=path.name):
                self.assertIn(
                    "LEGACY / SUPERSEDED SX1509 FAN PATH",
                    path.read_text(),
                    f"{path.name} must keep its legacy / superseded banner",
                )

    def test_historical_sx1509_proof_preserved(self) -> None:
        self.assertTrue(SX1509_PROOF_FIXTURE.is_file())
        self.assertTrue(SX1509_PROOF_TEST.is_file())


if __name__ == "__main__":
    unittest.main(verbosity=2)

#!/usr/bin/env python3
"""PWM-SX1509-TACH-PROOF-001 — prove SX1509 tach `pulse_counter` support.

This module turns the previously *inferred* "SX1509 expander pins cannot
back an ESPHome ``pulse_counter``" claim into an actual ESPHome
config/compile proof, and guards the documentation against wording
regressions.

Three things are pinned here:

1. **The proof fixture exists and is shaped correctly.**
   ``tests/esphome/sx1509_pulse_counter_proof.yaml`` mirrors the real
   ``packages/expansions/fan_pwm_sx1509.yaml`` binding (SX1509 hub on
   ``core_i2c``, channel 4 = ``Pul_Cou1``) but attempts the unproven
   path: channel 4 as a ``sensor: platform: pulse_counter`` pin.

2. **The proof runs (when ESPHome is installed).** If the ``esphome``
   CLI is on ``PATH``, ``esphome config`` is run against the fixture and
   MUST fail with the captured error
   ``[sx1509] is an invalid option for [pin]``. Two control configs
   confirm the rejection is specific to ``pulse_counter`` + SX1509:
   the same SX1509 pin validates as a ``binary_sensor: gpio``, and
   ``pulse_counter`` validates on a native ESP32 GPIO. If ESPHome is not
   available the live checks are skipped (never faked).

3. **The docs do not regress the wording.** The S360-311 / FanPWM docs
   and the SX1509 binding package must (a) never claim "SX1509 does not
   support PWM" (it does), (b) never attribute the tach limitation to
   "online docs" without a citation, (c) keep PWM-drive **output**
   support distinct from the ``pulse_counter`` / RPM limitation, and
   (d) attribute the limitation to the compile/config proof rather than
   inference.

Run with::

    python3 tests/test_sx1509_tach_pulse_counter_proof.py
"""

from __future__ import annotations

import re
import shutil
import subprocess
import unittest
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parent.parent

PROOF_FIXTURE = REPO_ROOT / "tests" / "esphome" / "sx1509_pulse_counter_proof.yaml"
FAN_PWM_SX1509_PACKAGE = REPO_ROOT / "packages" / "expansions" / "fan_pwm_sx1509.yaml"
PWM_DOC = REPO_ROOT / "docs" / "hardware" / "s360-311-r4-pwm.md"
PACKAGE_MATRIX = REPO_ROOT / "docs" / "hardware" / "package-readiness-matrix.md"
PRODUCT_MATRIX = REPO_ROOT / "docs" / "product-readiness-matrix.md"

# The exact ESPHome `esphome config` rejection captured by the proof
# (ESPHome 2026.5.1). This string is the evidence.
CAPTURED_ERROR = "[sx1509] is an invalid option for [pin]"
PROOF_MARKER = "PWM-SX1509-TACH-PROOF-001"

# Docs/packages that carry the proof finding and must stay consistent.
PROOF_BEARING_FILES = [
    FAN_PWM_SX1509_PACKAGE,
    PWM_DOC,
    PACKAGE_MATRIX,
    PRODUCT_MATRIX,
]

# Phrasings that would wrongly claim the SX1509 cannot do PWM. SX1509
# PWM-drive output IS supported and is the basis of FanPWM drive, so none
# of these may appear in the proof-bearing files.
FORBIDDEN_NO_PWM_PATTERNS = [
    r"does not support pwm",
    r"doesn'?t support pwm",
    r"do not support pwm",
    r"don'?t support pwm",
    r"cannot support pwm",
    r"can'?t support pwm",
    r"no pwm support",
    r"lacks pwm",
    r"unsupported pwm",
    r"pwm (?:drive |output )?is not supported",
    r"pwm (?:drive |output )?are not supported",
    r"sx1509[^.\n]{0,60}\bno pwm\b",
]


def _esphome_cli() -> str | None:
    return shutil.which("esphome")


class ProofFixtureShapeTests(unittest.TestCase):
    """The proof fixture exists and targets the right claim."""

    def test_fixture_exists(self) -> None:
        self.assertTrue(
            PROOF_FIXTURE.is_file(),
            "tests/esphome/sx1509_pulse_counter_proof.yaml must exist — it is "
            "the PWM-SX1509-TACH-PROOF-001 minimal proof target.",
        )

    def test_fixture_binds_sx1509_hub_on_core_i2c(self) -> None:
        text = PROOF_FIXTURE.read_text()
        self.assertRegex(
            text,
            r"sx1509:\s*\n\s*-\s*id:\s*sx1509_expander",
            "Proof fixture must declare the SX1509 hub `sx1509_expander`.",
        )
        self.assertRegex(
            text,
            r"i2c_id:\s*core_i2c",
            "Proof fixture must bind the SX1509 hub to the shared `core_i2c` "
            "bus (mirrors fan_pwm_sx1509.yaml).",
        )

    def test_fixture_attempts_pulse_counter_on_sx1509_channel_4(self) -> None:
        text = PROOF_FIXTURE.read_text()
        # A pulse_counter sensor whose pin routes through the SX1509 hub on
        # channel 4 (Pul_Cou1) — the exact claim under test.
        pattern = re.compile(
            r"platform:\s*pulse_counter\b"
            r"(?:.*\n)*?"
            r"\s*pin:\s*\n"
            r"\s*sx1509:\s*sx1509_expander\s*\n"
            r"\s*number:\s*4\b",
            re.MULTILINE,
        )
        self.assertRegex(
            text,
            pattern,
            "Proof fixture must attempt `pulse_counter` on SX1509 channel 4 "
            "(Pul_Cou1) — that is the unproven path being tested.",
        )

    def test_fixture_records_captured_error(self) -> None:
        self.assertIn(
            CAPTURED_ERROR,
            PROOF_FIXTURE.read_text(),
            "Proof fixture header must record the captured `esphome config` "
            f"rejection {CAPTURED_ERROR!r}.",
        )


class LiveEsphomeConfigProofTests(unittest.TestCase):
    """When ESPHome is installed, the proof actually runs.

    These tests are skipped (never faked) if the `esphome` CLI is not on
    PATH, per repo convention (see scripts/validate_compile_targets.py).
    """

    def _run_config(self, yaml_text: str) -> subprocess.CompletedProcess:
        import tempfile

        esphome = _esphome_cli()
        assert esphome is not None  # guarded by skip in callers
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Path(tmp) / "cfg.yaml"
            cfg.write_text(yaml_text)
            return subprocess.run(
                [esphome, "config", str(cfg)],
                cwd=tmp,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

    def test_pulse_counter_on_sx1509_is_rejected(self) -> None:
        if _esphome_cli() is None:
            self.skipTest("esphome CLI not on PATH; proof runs in CI/manual")
        esphome = _esphome_cli()
        proc = subprocess.run(
            [esphome, "config", str(PROOF_FIXTURE)],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        self.assertNotEqual(
            proc.returncode,
            0,
            "esphome config MUST reject pulse_counter on an SX1509 pin; "
            f"got rc=0. Output:\n{proc.stdout}",
        )
        self.assertIn(
            CAPTURED_ERROR,
            proc.stdout,
            "esphome config rejection must be the captured pin-schema error "
            f"{CAPTURED_ERROR!r}. Output:\n{proc.stdout}",
        )

    def test_control_sx1509_pin_validates_as_binary_sensor(self) -> None:
        if _esphome_cli() is None:
            self.skipTest("esphome CLI not on PATH; proof runs in CI/manual")
        yaml_text = (
            "esphome:\n  name: ctrl-a\n"
            "esp32:\n  board: esp32-s3-devkitc-1\n  framework:\n    type: esp-idf\n"
            "i2c:\n  - id: core_i2c\n    sda: GPIO48\n    scl: GPIO45\n"
            "    frequency: 400kHz\n"
            "sx1509:\n  - id: sx1509_expander\n    i2c_id: core_i2c\n"
            "    address: 0x3E\n"
            "binary_sensor:\n  - platform: gpio\n    id: fan_pwm_tach_1\n"
            "    internal: true\n    pin:\n      sx1509: sx1509_expander\n"
            "      number: 4\n      mode:\n        input: true\n"
            "        pullup: true\n      inverted: true\n"
        )
        proc = self._run_config(yaml_text)
        self.assertEqual(
            proc.returncode,
            0,
            "Control A: the SAME SX1509 pin must validate as a gpio "
            f"binary_sensor (proves the rejection is pulse_counter-specific). "
            f"Output:\n{proc.stdout}",
        )

    def test_control_pulse_counter_validates_on_native_gpio(self) -> None:
        if _esphome_cli() is None:
            self.skipTest("esphome CLI not on PATH; proof runs in CI/manual")
        yaml_text = (
            "esphome:\n  name: ctrl-b\n"
            "esp32:\n  board: esp32-s3-devkitc-1\n  framework:\n    type: esp-idf\n"
            "sensor:\n  - platform: pulse_counter\n    id: tach_io_rpm\n"
            "    name: TachIO RPM\n    pin:\n      number: GPIO16\n"
            "      mode:\n        input: true\n        pullup: true\n"
        )
        proc = self._run_config(yaml_text)
        self.assertEqual(
            proc.returncode,
            0,
            "Control B: pulse_counter must validate on a native ESP32 GPIO "
            f"(proves pulse_counter itself works). Output:\n{proc.stdout}",
        )


class WordingRegressionTests(unittest.TestCase):
    """Guard the docs/package wording against the over-strong / inferred form."""

    def test_no_claim_that_sx1509_lacks_pwm(self) -> None:
        for path in PROOF_BEARING_FILES:
            text = path.read_text().lower()
            for pat in FORBIDDEN_NO_PWM_PATTERNS:
                with self.subTest(file=path.name, pattern=pat):
                    self.assertIsNone(
                        re.search(pat, text),
                        f"{path.name} must not claim the SX1509 lacks PWM "
                        f"(pattern {pat!r}). SX1509 PWM-drive output IS "
                        f"supported and is the basis of FanPWM drive.",
                    )

    def test_no_uncited_online_tach_claim(self) -> None:
        # An "online docs say tach unsupported" style attribution is only
        # allowed if the same line carries an http(s) citation.
        for path in PROOF_BEARING_FILES:
            for line_no, line in enumerate(path.read_text().splitlines(), start=1):
                low = line.lower()
                if "online" not in low:
                    continue
                mentions_tach = any(
                    t in low for t in ("tach", "pulse_counter", "rpm")
                )
                mentions_unsupported = any(
                    u in low for u in ("unsupported", "not supported", "unproven")
                )
                if mentions_tach and mentions_unsupported:
                    with self.subTest(file=path.name, line=line_no):
                        self.assertIn(
                            "http",
                            low,
                            f"{path.name}:{line_no} attributes the tach "
                            f"limitation to 'online' without a citation. "
                            f"Either cite a URL or attribute it to the "
                            f"compile/config proof.",
                        )

    def test_pwm_output_support_distinguished_from_pulse_counter(self) -> None:
        for path in PROOF_BEARING_FILES:
            text = path.read_text()
            low = text.lower()
            with self.subTest(file=path.name):
                self.assertIn(
                    "pulse_counter",
                    low,
                    f"{path.name} must reference `pulse_counter` so the RPM "
                    f"limitation is named explicitly.",
                )
                # PWM output support must be affirmed on a single line near
                # the word PWM, so a reader cannot conflate "no pulse_counter
                # RPM" with "no PWM".
                self.assertRegex(
                    low,
                    r"pwm[^\n]{0,120}is supported",
                    f"{path.name} must affirm that SX1509 PWM(-drive) output "
                    f"IS supported, kept distinct from the pulse_counter/RPM "
                    f"limitation.",
                )

    def test_limitation_is_attributed_to_the_compile_proof(self) -> None:
        for path in PROOF_BEARING_FILES:
            text = path.read_text()
            with self.subTest(file=path.name):
                self.assertIn(
                    PROOF_MARKER,
                    text,
                    f"{path.name} must reference {PROOF_MARKER} so the tach "
                    f"finding is traceable to the compile/config proof.",
                )
                self.assertIn(
                    CAPTURED_ERROR,
                    text,
                    f"{path.name} must quote the captured `esphome config` "
                    f"rejection {CAPTURED_ERROR!r} as the evidence (not "
                    f"inference, not 'online docs').",
                )
                self.assertRegex(
                    text.lower(),
                    r"compile-proven|config-proven|esphome config",
                    f"{path.name} must describe the finding as proven by "
                    f"ESPHome validation, not merely inferred.",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)

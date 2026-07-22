#!/usr/bin/env python3
"""LED-FRAMEWORK-002 — resolved-config proof across the optional-input matrix.

Proves that the FULL LED framework composes and fully resolves under `esphome
config` across every supported composition, with RoomIQ and Presence optional:

    1. LED only                 (Core + LED)
    2. Core + AirIQ + LED       (the AirIQ-only device that motivated this work)
    3. LED + RoomIQ             (no Presence)
    4. LED + Presence           (no RoomIQ)
    5. LED + RoomIQ + Presence  (the historical full composition — regression)

For each it asserts the config is valid, no `id()` fails to resolve (the exact
Presence-less defect this programme fixes), and the compile-time capability
flags reach the engine as the expected `set_capabilities(<roomiq>, <presence>)`
bool literals — so the degraded behaviour is proven, not assumed.

How this avoids a false pass
----------------------------
Each composition is validated in an isolated temp directory whose only real
files are the device YAML and generated placeholder secrets; the repository's
`packages/`, `include/` and `components/` trees are symlinked in so the
frameworks' repository-local `esphome: includes:` (../include/sense360/*.h)
resolve exactly as they do for a real one-deep product build. Nothing is
copied or re-implemented.

The `esphome config` assertions need the `esphome` CLI and are skipped when it
is absent (e.g. the offline quick-validation gate). The structural coverage
assertion always runs.

Uses Python's stdlib unittest (repo convention). Run with::

    python3 tests/test_led_composition.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# A valid 32-byte base64 API key + strong placeholder secrets (the fallback-AP
# guard rejects the historical literals, so these are freshly random-looking).
PLACEHOLDER_SECRETS = (
    'wifi_ssid: "s360-test-ssid"\n'
    'wifi_password: "s360-test-password"\n'
    'api_encryption_key: "AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8="\n'
    'ota_password: "s360-test-ota-pw-8chars"\n'
    'fallback_ap_password: "s360-test-fallback-Kt9wQ2"\n'
    'web_username: "admin"\n'
    'web_password: "s360-test-web-pw-8chars"\n'
    'mqtt_broker: "192.0.2.10"\n'
    'mqtt_port: "1883"\n'
    'mqtt_username: "u"\n'
    'mqtt_password: "p"\n'
    'airiq_mqtt_broker: "192.0.2.10"\n'
    'airiq_mqtt_port: "1883"\n'
    'airiq_mqtt_username: "u"\n'
    'airiq_mqtt_password: "p"\n'
)

_COMMON_SUBS = """\
  device_name: s360-led-comp
  friendly_name: "S360 LED Comp"
  device_version: "0.0.0-led-composition-test"
  timezone: "UTC"
  log_level: INFO
  wifi_fast_connect: "false"
  fallback_ssid: "S360 LED Comp"
  s360_hardware_model: "S360-100"
  s360_hardware_revision: "R4"
"""

_BASE_PACKAGES = """\
  external_components: !include ../packages/base/external_components.yaml
  base_wifi: !include ../packages/base/wifi.yaml
  base_logging: !include ../packages/base/logging.yaml
  base_api: !include ../packages/base/api_encrypted.yaml
  base_ota: !include ../packages/base/ota.yaml
  base_time: !include ../packages/base/time.yaml
  core_board: !include ../packages/boards/s360-100-core-ceiling.yaml
  led_board: !include ../packages/boards/s360-300-led.yaml
  led_framework: !include ../packages/features/led_framework.yaml
  framework: !include ../packages/base/device_framework.yaml
"""

# Each composition: (name, expected set_capabilities literal, extra subs, extra
# package includes). The base always composes Core + LED board + LED framework.
COMPOSITIONS = {
    "led_only": (
        "set_capabilities(false, false)",
        '  s360_config_string: "Ceiling-Core-LED"\n'
        '  s360_capabilities: "core,led"\n'
        '  s360_capabilities_human: "Core, LED"\n'
        '  s360_module_led: "Included"\n'
        '  led_has_roomiq: "false"\n'
        '  led_has_presence: "false"\n',
        "",
    ),
    "core_airiq_led": (
        "set_capabilities(false, false)",
        '  s360_config_string: "Ceiling-Core-LED-AirIQ"\n'
        '  s360_capabilities: "core,airiq,led"\n'
        '  s360_capabilities_human: "Core, AirIQ, LED"\n'
        '  s360_module_airiq: "Included"\n'
        '  s360_module_led: "Included"\n'
        '  led_has_roomiq: "false"\n'
        '  led_has_presence: "false"\n',
        "  airiq_board: !include ../packages/boards/s360-210-airiq.yaml\n"
        "  airiq_framework: !include ../packages/features/airiq_framework.yaml\n",
    ),
    "led_roomiq": (
        "set_capabilities(true, false)",
        '  s360_config_string: "Ceiling-Core-RoomIQ-LED"\n'
        '  s360_capabilities: "core,roomiq,led"\n'
        '  s360_capabilities_human: "Core, RoomIQ, LED"\n'
        '  s360_module_roomiq: "Included"\n'
        '  s360_module_led: "Included"\n'
        '  led_has_roomiq: "true"\n'
        '  led_has_presence: "false"\n',
        "  roomiq_climate_board: !include ../packages/boards/s360-200-roomiq-climate.yaml\n"
        "  roomiq_framework: !include ../packages/features/roomiq_framework.yaml\n",
    ),
    "led_presence": (
        "set_capabilities(false, true)",
        '  s360_config_string: "Ceiling-Core-Presence-LED"\n'
        '  s360_capabilities: "core,presence,led"\n'
        '  s360_capabilities_human: "Core, Presence, LED"\n'
        '  s360_module_presence: "Included"\n'
        '  s360_module_led: "Included"\n'
        '  led_has_roomiq: "false"\n'
        '  led_has_presence: "true"\n',
        "  led_presence_bridge: !include ../packages/features/led_presence_bridge.yaml\n"
        "  roomiq_radar_board: !include ../packages/boards/s360-200-roomiq-radar.yaml\n"
        "  roomiq_pir_board: !include ../packages/boards/s360-200-roomiq-pir.yaml\n"
        "  roomiq_sen0609_board: !include ../packages/boards/s360-200-roomiq-sen0609.yaml\n"
        "  presence_framework: !include ../packages/features/presence_framework.yaml\n",
    ),
    "led_roomiq_presence": (
        "set_capabilities(true, true)",
        '  s360_config_string: "Ceiling-Core-RoomIQ-Presence-LED"\n'
        '  s360_capabilities: "core,roomiq,presence,led"\n'
        '  s360_capabilities_human: "Core, RoomIQ, Presence, LED"\n'
        '  s360_module_roomiq: "Included"\n'
        '  s360_module_presence: "Included"\n'
        '  s360_module_led: "Included"\n'
        '  led_has_roomiq: "true"\n'
        '  led_has_presence: "true"\n',
        "  led_presence_bridge: !include ../packages/features/led_presence_bridge.yaml\n"
        "  roomiq_board: !include ../packages/boards/s360-200-roomiq.yaml\n"
        "  roomiq_framework: !include ../packages/features/roomiq_framework.yaml\n"
        "  roomiq_pir_board: !include ../packages/boards/s360-200-roomiq-pir.yaml\n"
        "  roomiq_sen0609_board: !include ../packages/boards/s360-200-roomiq-sen0609.yaml\n"
        "  presence_framework: !include ../packages/features/presence_framework.yaml\n",
    ),
}


def _device_yaml(name: str) -> str:
    expected, extra_subs, extra_pkgs = COMPOSITIONS[name]
    return (
        "substitutions:\n"
        + _COMMON_SUBS
        + extra_subs
        + "\npackages:\n"
        + _BASE_PACKAGES
        + extra_pkgs
    )


def _esphome_cli() -> str | None:
    return shutil.which("esphome")


class _IsolatedComposition:
    """A temp product dir: only device.yaml + secrets are real; the repo
    packages/include/components trees are symlinked so framework includes
    resolve exactly as for a one-deep product build."""

    def __init__(self, name: str) -> None:
        self.work = Path(tempfile.mkdtemp(prefix="s360-led-comp-"))
        for tree in ("packages", "include", "components"):
            os.symlink(REPO_ROOT / tree, self.work / tree)
        products = self.work / "products"
        products.mkdir()
        (products / "secrets.yaml").write_text(PLACEHOLDER_SECRETS)
        self.device = products / f"{name}.yaml"
        self.device.write_text(_device_yaml(name))

    def run_config(self) -> subprocess.CompletedProcess:
        env = {**os.environ, "ESPHOME_DATA_DIR": str(self.work / "esphome-data")}
        return subprocess.run(
            [_esphome_cli(), "config", str(self.device)],
            cwd=self.work / "products",
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

    def cleanup(self) -> None:
        shutil.rmtree(self.work, ignore_errors=True)


class CompositionMatrixStructureTests(unittest.TestCase):
    """Always-run: the matrix covers every supported composition."""

    def test_matrix_covers_all_five_compositions(self) -> None:
        self.assertEqual(
            set(COMPOSITIONS),
            {
                "led_only",
                "core_airiq_led",
                "led_roomiq",
                "led_presence",
                "led_roomiq_presence",
            },
        )

    def test_expected_capabilities_track_the_flags(self) -> None:
        # The expected engine literal must match the declared flags for each
        # composition (guards against a copy-paste drift in the fixtures).
        for name, (expected, subs, _pkgs) in COMPOSITIONS.items():
            has_roomiq = 'led_has_roomiq: "true"' in subs
            has_presence = 'led_has_presence: "true"' in subs
            want = (
                f"set_capabilities({'true' if has_roomiq else 'false'}, "
                f"{'true' if has_presence else 'false'})"
            )
            self.assertEqual(expected, want, name)


@unittest.skipIf(_esphome_cli() is None, "esphome CLI not installed")
class ResolvedConfigTests(unittest.TestCase):
    """`esphome config` fully resolves every composition (no missing id)."""

    def _check(self, name: str) -> None:
        comp = _IsolatedComposition(name)
        try:
            proc = comp.run_config()
            out = proc.stdout
            # The exact Presence-less defect must be gone.
            self.assertNotIn("Couldn't find ID", out, out[-3000:])
            self.assertNotIn("Could not find file", out, out[-3000:])
            self.assertEqual(proc.returncode, 0, out[-3000:])
            self.assertIn("Configuration is valid", out)
            # The compile-time flags reached the engine as bool literals — the
            # degraded/automatic behaviour is proven, not assumed.
            expected = COMPOSITIONS[name][0]
            self.assertIn(expected, out, f"{name}: expected {expected}")
            # The full Night Mode Behaviour option list is always present.
            self.assertIn("When dark and occupied", out)
            # The honest fallback diagnostic is composed.
            self.assertIn("s360_led_night_behaviour_status", out)
        finally:
            comp.cleanup()

    def test_led_only(self) -> None:
        self._check("led_only")

    def test_core_airiq_led(self) -> None:
        self._check("core_airiq_led")

    def test_led_roomiq(self) -> None:
        self._check("led_roomiq")

    def test_led_presence(self) -> None:
        self._check("led_presence")

    def test_led_roomiq_presence(self) -> None:
        self._check("led_roomiq_presence")


if __name__ == "__main__":
    unittest.main(verbosity=2)

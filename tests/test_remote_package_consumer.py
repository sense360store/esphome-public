#!/usr/bin/env python3
"""REMOTE-PACKAGE-HEADER-RESOLUTION-001 — external-consumer regression.

Proves that a clean Home Assistant-style ESPHome device configuration can
consume the canonical Sense360 AirIQ board and framework through git packages
and resolve the shared C++ engine header (``include/sense360/airiq_engine.h``)
*without* any ``/config/include`` setup, manual header download, or local copy.

The defect
----------
The framework packages compile their engine via ``esphome: includes:`` with a
path relative to the ``products/`` config directory
(``../include/sense360/<engine>.h``). ESPHome resolves that path against the
*consumer's* config directory, so a git-package consumer looks for
``<config>/../include/sense360/...`` — a file the package never delivers — and
validation fails with "Could not find file". The fix delivers the shared
headers through the ``sense360`` external component
(``include/sense360/__init__.py``) and removes the local include via the
remote-consumer wrapper packages under ``packages/remote/``.

How this test avoids a false pass
---------------------------------
The consumer is built in an isolated temporary directory that contains ONLY
the device YAML and generated placeholder secrets — never the repository's
``include/`` tree. Everything Sense360 is fetched through ESPHome's supported
git-package mechanism from a throwaway local git repository built from the
current working tree, so the header can only be found if the packaging fix
delivers it. The test explicitly asserts the consumer directory has no
``include/`` directory of its own.

Modes
-----
* Structural assertions (always run): the external component, the delivery
  package, and the AirIQ wrapper are shaped correctly and the frameworks still
  carry their repository-local include (repo-local builds unchanged).
* ``esphome config`` validation (needs the ``esphome`` CLI; skipped otherwise):
  the exact defect — a config-validation-time "Could not find file" — is gone
  and the full Core + LED + AirIQ remote composition validates, including
  ``mqtt: null`` removal.
* Source-resolution / compile (needs the CLI **and** ``RUN_REMOTE_COMPILE=1``):
  ESPHome copies ``airiq_engine.h`` into the build's
  ``src/esphome/components/sense360/`` byte-identically to the canonical
  source. This runs a real ``esphome compile``; the delivered-header artifact
  is produced during C++ source generation, so the assertion holds whether or
  not the (network-dependent) toolchain download that follows succeeds.
* Live GitHub smoke (needs the CLI and ``RUN_REMOTE_LIVE=1``): the same
  composition fetched from the real repository. Documented, opt-in, offline CI
  never depends on it.

Uses Python's stdlib unittest (repo convention). Run with::

    python3 tests/test_remote_package_consumer.py
    RUN_REMOTE_COMPILE=1 python3 tests/test_remote_package_consumer.py
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

COMPONENT_INIT = REPO_ROOT / "include" / "sense360" / "__init__.py"
CANONICAL_HEADER = REPO_ROOT / "include" / "sense360" / "airiq_engine.h"
SHARED_ENGINES_PKG = REPO_ROOT / "packages" / "remote" / "sense360-shared-engines.yaml"
AIRIQ_WRAPPER = REPO_ROOT / "packages" / "remote" / "ceiling-airiq.yaml"

# Every shared header the sense360 component must deliver (one physical copy of
# each lives in include/sense360/ — the same files the native C++ unit tests
# compile).
EXPECTED_SHARED_HEADERS = {
    "airiq_engine.h",
    "ventiq_engine.h",
    "roomiq_engine.h",
    "presence_fusion.h",
    "led_controller.h",
    "led_logic.h",
    "thresholds.h",
    "calibration.h",
    "time_utils.h",
}

# A valid 32-byte base64 API encryption key + placeholder secrets. Generated
# here so no real secret is ever committed and the consumer dir is fully
# self-contained.
PLACEHOLDER_SECRETS = (
    'wifi_ssid: "sense360-test-ssid"\n'
    'wifi_password: "sense360-test-pw"\n'
    'api_encryption_key: "AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8="\n'
    'ota_password: "sense360-test-ota"\n'
)

# The external consumer: Core + LED board + AirIQ (board + framework) pulled
# entirely through git packages, with the AirIQ wrapper declared FIRST to prove
# the fix is independent of consumer package order. __REMOTE__ is replaced with
# the file:// URL of the throwaway local git repository.
CONSUMER_CORE_LED_AIRIQ = """\
substitutions:
  device_name: sense360-core-bench
  friendly_name: Sense360 Core Bench
  timezone: "Europe/London"
  device_version: "0.0.0-remote-consumer-test"
  sense360_remote_url: file://__REMOTE__
  sense360_remote_ref: main
  s360_config_string: "Ceiling-Core-LED-AirIQ-Bench"
  s360_hardware_model: "S360-100"
  s360_hardware_revision: "R4"
  s360_capabilities: "core,airiq,led"
  s360_capabilities_human: "Core, AirIQ, LED"
  s360_module_led: "Included"

packages:
  airiq:
    url: file://__REMOTE__
    ref: main
    files: [packages/remote/ceiling-airiq.yaml]
    refresh: 0s
  core:
    url: file://__REMOTE__
    ref: main
    files: [packages/hardware/sense360_core_ceiling.yaml]
    refresh: 0s
  core_framework:
    url: file://__REMOTE__
    ref: main
    files: [packages/base/device_framework.yaml]
    refresh: 0s
  led:
    url: file://__REMOTE__
    ref: main
    files: [packages/boards/s360-300-led.yaml]
    refresh: 0s

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_encryption_key

ota:
  - platform: esphome
    password: !secret ota_password

logger:
  level: DEBUG

mqtt: null
"""


# LED-FRAMEWORK-002 external consumer: Core + AirIQ + LED board + the LED
# behaviour framework, ALL pulled through git packages, with NO RoomIQ and NO
# Presence. Proves the full LED framework composes remotely on an AirIQ-only
# device and that the shared led_controller.h / roomiq_engine.h headers resolve
# via the sense360 component (no /config/include, no type:local). The LED
# framework wrapper carries led_has_roomiq/led_has_presence "false" defaults.
CONSUMER_CORE_AIRIQ_LED_FRAMEWORK = """\
substitutions:
  device_name: sense360-core-airiq-led
  friendly_name: Sense360 Core AirIQ LED
  timezone: "Europe/London"
  device_version: "0.0.0-remote-consumer-test"
  sense360_remote_url: file://__REMOTE__
  sense360_remote_ref: main
  s360_config_string: "Ceiling-Core-LED-AirIQ-Bench"
  s360_hardware_model: "S360-100"
  s360_hardware_revision: "R4"
  s360_capabilities: "core,airiq,led"
  s360_capabilities_human: "Core, AirIQ, LED"
  s360_module_airiq: "Included"
  s360_module_led: "Included"
  led_has_roomiq: "false"
  led_has_presence: "false"

packages:
  airiq:
    url: file://__REMOTE__
    ref: main
    files: [packages/remote/ceiling-airiq.yaml]
    refresh: 0s
  core:
    url: file://__REMOTE__
    ref: main
    files: [packages/hardware/sense360_core_ceiling.yaml]
    refresh: 0s
  core_framework:
    url: file://__REMOTE__
    ref: main
    files: [packages/base/device_framework.yaml]
    refresh: 0s
  led_board:
    url: file://__REMOTE__
    ref: main
    files: [packages/boards/s360-300-led.yaml]
    refresh: 0s
  led_framework:
    url: file://__REMOTE__
    ref: main
    files: [packages/remote/led-framework.yaml]
    refresh: 0s

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_encryption_key

ota:
  - platform: esphome
    password: !secret ota_password

logger:
  level: DEBUG

mqtt: null
"""


def _esphome_cli() -> str | None:
    return shutil.which("esphome")


def _build_local_remote(dest: Path) -> None:
    """Snapshot the working tree (tracked + untracked-not-ignored) into a fresh
    git repository so the consumer fetches exactly today's repository state."""
    tracked = subprocess.check_output(
        ["git", "ls-files"], cwd=REPO_ROOT, text=True
    ).splitlines()
    untracked = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=REPO_ROOT,
        text=True,
    ).splitlines()
    for rel in tracked + untracked:
        src = REPO_ROOT / rel
        if not src.is_file():
            continue
        dst = dest / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "test",
        "GIT_AUTHOR_EMAIL": "test@sense360.test",
        "GIT_COMMITTER_NAME": "test",
        "GIT_COMMITTER_EMAIL": "test@sense360.test",
    }
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=dest, check=True, env=env)
    subprocess.run(["git", "add", "-A"], cwd=dest, check=True, env=env)
    subprocess.run(
        ["git", "commit", "-q", "-m", "fixture"], cwd=dest, check=True, env=env
    )


class _RemoteFixture:
    """A throwaway git remote + isolated consumer directory."""

    def __init__(self, consumer_yaml: str, *, live: bool = False) -> None:
        self.work = Path(tempfile.mkdtemp(prefix="s360-remote-"))
        self.consumer = self.work / "consumer"
        self.consumer.mkdir()
        (self.consumer / "secrets.yaml").write_text(PLACEHOLDER_SECRETS)
        if live:
            body = consumer_yaml.replace(
                "file://__REMOTE__", "https://github.com/sense360store/esphome-public"
            )
        else:
            remote = self.work / "remote"
            remote.mkdir()
            _build_local_remote(remote)
            body = consumer_yaml.replace("__REMOTE__", str(remote))
        (self.consumer / "device.yaml").write_text(body)
        self.cache = self.work / "esphome-data"

    def run(self, command: str) -> subprocess.CompletedProcess:
        env = {**os.environ, "ESPHOME_DATA_DIR": str(self.cache)}
        return subprocess.run(
            [_esphome_cli(), command, str(self.consumer / "device.yaml")],
            cwd=self.consumer,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

    def cleanup(self) -> None:
        shutil.rmtree(self.work, ignore_errors=True)


# --- ESPHome-tag-tolerant YAML loading (repo convention) --------------------


def _esphome_tag(loader, node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None


# Register the ESPHome custom tags on the shared SafeLoader with the repo's
# convention (`!remove` collapses to None). The `!remove` markers themselves are
# asserted from the raw text, so this stays robust even when another test module
# registers the same tags in a different import order.
for _tag in ("!secret", "!include", "!extend", "!lambda", "!remove"):
    yaml.add_constructor(_tag, _esphome_tag, Loader=yaml.SafeLoader)
yaml.add_multi_constructor("!include_dir_", _esphome_tag, Loader=yaml.SafeLoader)


def _load(path: Path) -> dict:
    doc = yaml.safe_load(path.read_text())
    return doc if isinstance(doc, dict) else {}


# --- structural assertions (always run) -------------------------------------


class ExternalComponentStructureTests(unittest.TestCase):
    def test_component_init_exists(self) -> None:
        self.assertTrue(
            COMPONENT_INIT.is_file(),
            "sense360 external component (include/sense360/__init__.py) missing",
        )

    def test_component_delivers_every_shared_header(self) -> None:
        raw = COMPONENT_INIT.read_text()
        for header in EXPECTED_SHARED_HEADERS:
            self.assertIn(
                header, raw, f"{header} must be delivered by the sense360 component"
            )
            self.assertTrue(
                (REPO_ROOT / "include" / "sense360" / header).is_file(),
                f"canonical {header} must exist exactly once in include/sense360/",
            )

    def test_component_defines_config_only_schema(self) -> None:
        raw = COMPONENT_INIT.read_text()
        self.assertIn("CONFIG_SCHEMA", raw)
        self.assertIn("to_code", raw)
        # It must #include from its own installed component path so the headers
        # resolve in the build regardless of consumer layout.
        self.assertIn("esphome/components/sense360/", raw)


class DeliveryPackageStructureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.shared = _load(SHARED_ENGINES_PKG)
        self.wrapper = _load(AIRIQ_WRAPPER)

    def test_shared_engines_package_shape(self) -> None:
        ext = self.shared.get("external_components")
        self.assertTrue(ext, "shared-engines package must declare external_components")
        components = ext[0]["components"]
        self.assertIn("sense360", components)
        self.assertEqual(ext[0]["source"]["path"], "include")
        # Loads the delivery component and removes the local include.
        self.assertIn("sense360", self.shared)
        self.assertIn(
            "includes: !remove",
            SHARED_ENGINES_PKG.read_text(),
            "shared-engines must remove the framework's local esphome.includes",
        )

    def test_airiq_wrapper_shape(self) -> None:
        ext = self.wrapper.get("external_components")
        self.assertTrue(ext, "AirIQ wrapper must declare external_components")
        self.assertIn("sense360", ext[0]["components"])
        self.assertIn("sense360", self.wrapper)
        raw = AIRIQ_WRAPPER.read_text()
        # Removes the framework's local include and its legacy MQTT block.
        self.assertIn("includes: !remove", raw)
        self.assertIn("mqtt: !remove", raw)
        # It composes the board + framework relative to itself in the repo.
        self.assertIn("../boards/s360-210-airiq.yaml", raw)
        self.assertIn("../features/airiq_framework.yaml", raw)

    def test_wrapper_changes_no_commercial_or_release_declaration(self) -> None:
        # The packaging fix must not touch product / release / channel config.
        for path in (SHARED_ENGINES_PKG, AIRIQ_WRAPPER, COMPONENT_INIT):
            raw = path.read_text()
            for forbidden in (
                "webflash-builds",
                "product-catalog",
                "release-channel-policy",
                "artifact_name",
                "webflash_build_matrix",
            ):
                self.assertNotIn(
                    forbidden, raw, f"{path.name} must not touch {forbidden}"
                )


class RepoLocalBuildsUnchangedTests(unittest.TestCase):
    """The repository-local include delivery must be preserved so repo-local
    bundle builds are byte-for-byte unchanged (and release builds stay
    reproducible from the checked-out tree, not a moving git ref)."""

    def test_frameworks_keep_local_include(self) -> None:
        for framework in (
            "airiq_framework.yaml",
            "roomiq_framework.yaml",
            "ventiq_framework.yaml",
            "led_framework.yaml",
            "presence_framework.yaml",
        ):
            raw = (REPO_ROOT / "packages" / "features" / framework).read_text()
            self.assertIn(
                "../include/sense360/",
                raw,
                f"{framework} must keep its repository-local esphome.includes",
            )


# --- esphome config validation (skipped without the CLI) --------------------


@unittest.skipIf(_esphome_cli() is None, "esphome CLI not installed")
class RemoteConfigValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = _RemoteFixture(CONSUMER_CORE_LED_AIRIQ)

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_config_validates_and_include_error_is_gone(self) -> None:
        proc = self.fixture.run("config")
        out = proc.stdout
        # The exact defect this programme fixes must be gone.
        self.assertNotIn(
            "include/sense360/airiq_engine.h",
            out,
            "the repository-local header path must not appear as an unresolved include",
        )
        self.assertNotIn("Could not find file", out, out[-2000:])
        self.assertEqual(proc.returncode, 0, out[-3000:])
        self.assertIn("Configuration is valid", out)

    def test_consumer_dir_has_no_local_include_tree(self) -> None:
        # Proves the header is NOT satisfied by a local /config/include copy.
        self.fixture.run("config")
        self.assertFalse(
            (self.fixture.consumer / "include").exists(),
            "consumer must not need a local include/ directory",
        )

    def test_mqtt_null_removes_mqtt(self) -> None:
        # The consumer sets `mqtt: null`; the validated config must contain no
        # top-level mqtt component (the AirIQ framework's legacy compatibility
        # mqtt block is dropped by the wrapper, per requirement 8). Match the
        # dumped top-level `mqtt:` key, not the `airiq_mqtt_*` substitution
        # names (which legitimately remain and merely carry the string
        # "broker").
        proc = self.fixture.run("config")
        self.assertEqual(proc.returncode, 0, proc.stdout[-2000:])
        self.assertIsNone(
            re.search(r"(?m)^mqtt:", proc.stdout),
            "a top-level mqtt component must not survive `mqtt: null`",
        )


@unittest.skipIf(_esphome_cli() is None, "esphome CLI not installed")
class LedFrameworkRemoteConfigTests(unittest.TestCase):
    """LED-FRAMEWORK-002: the FULL LED framework composes remotely on an
    AirIQ-only device (no RoomIQ, no Presence), with the shared headers
    resolved via the sense360 component (no /config/include, no type:local)."""

    def setUp(self) -> None:
        self.fixture = _RemoteFixture(CONSUMER_CORE_AIRIQ_LED_FRAMEWORK)

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_config_validates_with_headers_resolved(self) -> None:
        proc = self.fixture.run("config")
        out = proc.stdout
        # No repository-local header path may appear as an unresolved include.
        for header in ("led_controller.h", "roomiq_engine.h"):
            self.assertNotIn(
                f"include/sense360/{header}'",
                out,
                f"{header} must not appear as an unresolved local include",
            )
        self.assertNotIn("Could not find file", out, out[-2000:])
        # The Presence-less defect (a missing occupancy id) must be gone.
        self.assertNotIn("Couldn't find ID", out, out[-2000:])
        self.assertEqual(proc.returncode, 0, out[-3000:])
        self.assertIn("Configuration is valid", out)
        # The optional-input flags reached the engine as bool literals: this
        # AirIQ-only device honestly declares no RoomIQ and no Presence.
        self.assertIn("set_capabilities(false, false)", out)

    def test_consumer_dir_has_no_local_include_tree(self) -> None:
        self.fixture.run("config")
        self.assertFalse(
            (self.fixture.consumer / "include").exists(),
            "consumer must not need a local include/ directory",
        )


# --- source resolution / compile (opt-in: runs a real esphome compile) ------


@unittest.skipUnless(
    _esphome_cli() is not None and os.environ.get("RUN_REMOTE_COMPILE") == "1",
    "set RUN_REMOTE_COMPILE=1 (and install esphome) to run the compile source-resolution check",
)
class RemoteSourceResolutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = _RemoteFixture(CONSUMER_CORE_LED_AIRIQ)

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_delivered_header_matches_canonical(self) -> None:
        # esphome compile generates C++ source (copying the sense360 component
        # into the build) before it downloads the toolchain, so the delivered
        # header artifact exists regardless of network access to the toolchain.
        self.fixture.run("compile")
        delivered = None
        for cand in self.fixture.cache.rglob(
            "src/esphome/components/sense360/airiq_engine.h"
        ):
            delivered = cand
            break
        self.assertIsNotNone(
            delivered,
            "airiq_engine.h was not delivered into the build via the package mechanism",
        )
        self.assertEqual(
            delivered.read_bytes(),
            CANONICAL_HEADER.read_bytes(),
            "delivered header must be byte-identical to the canonical single source",
        )
        # And it must be #included by the generated build.
        esphome_h = list(self.fixture.cache.rglob("src/esphome.h"))
        self.assertTrue(esphome_h)
        self.assertIn(
            "esphome/components/sense360/airiq_engine.h",
            esphome_h[0].read_text(),
        )


@unittest.skipUnless(
    _esphome_cli() is not None and os.environ.get("RUN_REMOTE_LIVE") == "1",
    "set RUN_REMOTE_LIVE=1 (and install esphome) to run the live GitHub smoke test",
)
class RemoteLiveSmokeTests(unittest.TestCase):
    def test_live_github_config_validates(self) -> None:
        fixture = _RemoteFixture(CONSUMER_CORE_LED_AIRIQ, live=True)
        try:
            proc = fixture.run("config")
            self.assertEqual(proc.returncode, 0, proc.stdout[-3000:])
            self.assertIn("Configuration is valid", proc.stdout)
        finally:
            fixture.cleanup()


if __name__ == "__main__":
    unittest.main(verbosity=2)

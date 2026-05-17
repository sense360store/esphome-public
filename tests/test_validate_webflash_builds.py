#!/usr/bin/env python3
"""
Unit tests for tests/validate_webflash_builds.py.

Uses Python's stdlib unittest (matching this repo's no-pytest convention for
Python validators). Each test stages a temporary repo_root containing a
copy of the canonical compatibility snapshot, a synthetic webflash-builds.json,
and stub product YAML files, then asserts on the validator's behavior.

Run with:
    python3 tests/test_validate_webflash_builds.py
"""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tests"))

from validate_webflash_builds import (  # noqa: E402
    GENERIC_FAN_MESSAGE,
    WebflashBuildsValidator,
)

CANONICAL_COMPAT_PATH = REPO_ROOT / "config" / "webflash-compatibility.json"

RELEASE_ONE_ENTRY = {
    "config_string": "Ceiling-POE-VentIQ-RoomIQ",
    "product_yaml": "products/webflash/ceiling-poe-ventiq-roomiq.yaml",
    "artifact_name": "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin",
    "channel": "stable",
    "version": "1.0.0",
    "chip_family": "ESP32",
}


class _StagedRepo:
    """Stages a temporary repo_root with snapshot + builds + stub product YAMLs."""

    def __init__(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmpdir.name)
        (self.root / "config").mkdir()
        shutil.copy(
            CANONICAL_COMPAT_PATH, self.root / "config" / "webflash-compatibility.json"
        )

    def write_builds(self, builds):
        """Write a webflash-builds.json with the given entries."""
        path = self.root / "config" / "webflash-builds.json"
        path.write_text(json.dumps({"schema_version": 1, "builds": builds}))

    def add_stub_yaml(self, rel_path):
        """Create an empty placeholder YAML at rel_path so existence checks pass."""
        full = self.root / rel_path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text("# stub for tests\n")

    def cleanup(self):
        self.tmpdir.cleanup()


def _entry(**overrides):
    e = dict(RELEASE_ONE_ENTRY)
    e.update(overrides)
    return e


class WebflashBuildsValidatorTests(unittest.TestCase):
    def setUp(self):
        self.staged = _StagedRepo()

    def tearDown(self):
        self.staged.cleanup()

    def _run(self, builds, stub_yamls=None):
        """Stage builds + stub YAMLs (defaulting to the release-one wrapper) and run validation."""
        self.staged.write_builds(builds)
        for rel in stub_yamls or [RELEASE_ONE_ENTRY["product_yaml"]]:
            self.staged.add_stub_yaml(rel)
        validator = WebflashBuildsValidator(self.staged.root)
        total, failed = validator.validate_all()
        return validator, total, failed

    # ------------------------------------------------------------------
    # 1. Valid release-one config passes.
    # ------------------------------------------------------------------
    def test_release_one_passes(self):
        validator, total, failed = self._run([_entry()])
        self.assertEqual(total, 1)
        self.assertEqual(failed, 0)
        self.assertEqual(validator.errors, [])

    # ------------------------------------------------------------------
    # 2. Generic Fan fails with the spec-mandated message.
    # ------------------------------------------------------------------
    def test_generic_fan_fails(self):
        bad_cs = "Ceiling-POE-VentIQ-Fan-RoomIQ"
        entry = _entry(
            config_string=bad_cs,
            artifact_name=f"Sense360-{bad_cs}-v1.0.0-stable.bin",
        )
        validator, _, failed = self._run([entry, _entry()])
        self.assertGreaterEqual(failed, 1)
        self.assertTrue(
            any(GENERIC_FAN_MESSAGE in e for e in validator.errors),
            f"expected generic-Fan message; got {validator.errors}",
        )

    # ------------------------------------------------------------------
    # 3. AirIQ + VentIQ together fails.
    # ------------------------------------------------------------------
    def test_airiq_plus_ventiq_fails(self):
        bad_cs = "Ceiling-USB-AirIQ-VentIQ-RoomIQ"
        entry = _entry(
            config_string=bad_cs,
            artifact_name=f"Sense360-{bad_cs}-v1.0.0-stable.bin",
        )
        validator, _, failed = self._run([entry, _entry()])
        self.assertGreaterEqual(failed, 1)
        self.assertTrue(
            any("mutually exclusive" in e for e in validator.errors),
            f"expected mutual-exclusion message; got {validator.errors}",
        )

    # ------------------------------------------------------------------
    # 4. RoomIQ + VentIQ passes.
    # ------------------------------------------------------------------
    def test_roomiq_with_ventiq_passes(self):
        cs = "Ceiling-POE-VentIQ-RoomIQ"
        entry = _entry(
            config_string=cs,
            artifact_name=f"Sense360-{cs}-v1.0.0-stable.bin",
        )
        validator, _, failed = self._run([entry, _entry()])
        # Release-One still in matrix => validation must pass overall.
        self.assertEqual(failed, 0, f"unexpected errors: {validator.errors}")

    # ------------------------------------------------------------------
    # 5. RoomIQ + AirIQ passes.
    # ------------------------------------------------------------------
    def test_roomiq_with_airiq_passes(self):
        cs = "Ceiling-USB-AirIQ-FanRelay-RoomIQ"
        entry = _entry(
            config_string=cs,
            artifact_name=f"Sense360-{cs}-v1.0.0-stable.bin",
        )
        validator, _, failed = self._run([entry, _entry()])
        self.assertEqual(failed, 0, f"unexpected errors: {validator.errors}")

    # ------------------------------------------------------------------
    # 6. artifact_name mismatch fails with the spec-mandated message.
    # ------------------------------------------------------------------
    def test_artifact_name_mismatch_fails(self):
        entry = _entry(
            artifact_name="Sense360-Ceiling-POE-VentIQ-RoomIQ-v9.9.9-stable.bin"
        )
        validator, _, failed = self._run([entry])
        self.assertEqual(failed, 1)
        self.assertTrue(
            any(
                "artifact_name mismatch: expected "
                "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin" in e
                for e in validator.errors
            ),
            f"expected mismatch message; got {validator.errors}",
        )

    # ------------------------------------------------------------------
    # 7. Missing product YAML fails.
    # ------------------------------------------------------------------
    def test_missing_product_yaml_fails(self):
        entry = _entry()
        # Don't stage any stub YAML.
        self.staged.write_builds([entry])
        validator = WebflashBuildsValidator(self.staged.root)
        _, failed = validator.validate_all()
        self.assertEqual(failed, 1)
        self.assertTrue(
            any("product_yaml not found" in e for e in validator.errors),
            f"expected product_yaml error; got {validator.errors}",
        )

    # ------------------------------------------------------------------
    # 8. Legacy Bathroom token fails.
    # ------------------------------------------------------------------
    def test_legacy_bathroom_fails(self):
        bad_cs = "Ceiling-POE-Bathroom-FanTRIAC-RoomIQ"
        entry = _entry(
            config_string=bad_cs,
            artifact_name=f"Sense360-{bad_cs}-v1.0.0-stable.bin",
        )
        validator, _, failed = self._run([entry, _entry()])
        self.assertGreaterEqual(failed, 1)
        self.assertTrue(
            any("'Bathroom'" in e for e in validator.errors),
            f"expected Bathroom forbidden-token error; got {validator.errors}",
        )

    # ------------------------------------------------------------------
    # 9. Legacy Presence token fails.
    # ------------------------------------------------------------------
    def test_legacy_presence_fails(self):
        bad_cs = "Ceiling-POE-VentIQ-FanTRIAC-Presence"
        entry = _entry(
            config_string=bad_cs,
            artifact_name=f"Sense360-{bad_cs}-v1.0.0-stable.bin",
        )
        validator, _, failed = self._run([entry, _entry()])
        self.assertGreaterEqual(failed, 1)
        self.assertTrue(
            any("'Presence'" in e for e in validator.errors),
            f"expected Presence forbidden-token error; got {validator.errors}",
        )

    # ------------------------------------------------------------------
    # 10. Required Release-One config missing fails.
    # ------------------------------------------------------------------
    def test_release_one_missing_fails(self):
        cs = "Ceiling-USB-AirIQ"
        other = _entry(
            config_string=cs,
            artifact_name=f"Sense360-{cs}-v0.1.0-preview.bin",
            channel="preview",
            version="0.1.0",
        )
        validator, _, _ = self._run([other])
        self.assertTrue(
            any("Release-One config" in e for e in validator.errors),
            f"expected Release-One missing error; got {validator.errors}",
        )

    # ------------------------------------------------------------------
    # 11. Channel outside allowed_channels fails.
    # ------------------------------------------------------------------
    def test_channel_outside_allowed_fails(self):
        entry = _entry(
            channel="nightly",
            artifact_name="Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-nightly.bin",
        )
        validator, _, failed = self._run([entry])
        self.assertGreaterEqual(failed, 1)
        self.assertTrue(
            any("'nightly'" in e and "allowed_channels" in e for e in validator.errors),
            f"expected channel error; got {validator.errors}",
        )

    # ------------------------------------------------------------------
    # 12. Missing required field fails.
    # ------------------------------------------------------------------
    def test_missing_required_field_fails(self):
        entry = _entry()
        del entry["chip_family"]
        validator, _, failed = self._run([entry])
        self.assertEqual(failed, 1)
        self.assertTrue(
            any("missing required field 'chip_family'" in e for e in validator.errors),
            f"expected missing-field error; got {validator.errors}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

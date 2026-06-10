#!/usr/bin/env python3
"""SEC-ESP-BUILD-GATES-001 regression guard for the release posture patch.

Locks in the behaviour of ``scripts/apply_release_secret_posture.py``
(SECURITY-AUDIT-2026-06 finding H1):

  * applied to a copy of the LIVE ``packages/base/`` tree, the patch strips
    the api-encryption / ota-password / web-auth / fallback-AP-password
    config so released firmware carries no shared credential material —
    drift in the committed files is caught here on every PR instead of at
    release time;
  * the setup path survives: the patched wifi package still joins the
    intentionally-public setup network and still serves the captive portal;
  * the patched files remain parseable YAML;
  * the transform is one-shot and fails closed on an unexpected file shape
    (a reshaped base package must fail the release loudly, never silently
    bake a shared secret).

Run with::

    python3 tests/test_apply_release_secret_posture.py
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "apply_release_secret_posture.py"

BASE_FILES = (
    "packages/base/api_encrypted.yaml",
    "packages/base/ota.yaml",
    "packages/base/logging.yaml",
    "packages/base/wifi.yaml",
)


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "apply_release_secret_posture", SCRIPT_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


class _EsphomeTagLoader(yaml.SafeLoader):
    """SafeLoader that tolerates ESPHome's custom tags (syntax-only parse)."""


_EsphomeTagLoader.add_multi_constructor("!", lambda loader, suffix, node: None)


def _copy_live_base(tmp: Path) -> Path:
    """Copy the live packages/base tree into tmp; return the new root."""
    root = tmp / "repo"
    (root / "packages").mkdir(parents=True)
    shutil.copytree(REPO_ROOT / "packages" / "base", root / "packages" / "base")
    return root


class ApplyPostureOnLiveTreeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _load_module()
        self.root = _copy_live_base(Path(tempfile.mkdtemp()))

    def _run_main(self, root: Path) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = self.mod.main(["--root", str(root)])
        return code, out.getvalue(), err.getvalue()

    def test_patch_applies_cleanly_to_the_live_committed_shapes(self) -> None:
        # If this fails after editing a packages/base file, update
        # scripts/apply_release_secret_posture.py in the same PR — otherwise
        # the release lane fails closed on the shape mismatch.
        code, out, err = self._run_main(self.root)
        self.assertEqual(code, 0, err)
        self.assertIn("release credential posture applied", out)

    def test_patched_tree_carries_no_shared_secret_references(self) -> None:
        self.assertEqual(self._run_main(self.root)[0], 0)
        for rel in BASE_FILES:
            text = (self.root / rel).read_text(encoding="utf-8")
            with self.subTest(file=rel):
                for key in (
                    "api_encryption_key",
                    "ota_password",
                    "web_username",
                    "web_password",
                    "fallback_ap_password",
                ):
                    self.assertNotIn(f"!secret {key}", text)

    def test_functional_config_survives_only_secrets_posture_changes(self) -> None:
        self.assertEqual(self._run_main(self.root)[0], 0)

        api = (self.root / "packages/base/api_encrypted.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn("api:", api)
        self.assertIn("reboot_timeout: 15min", api)
        self.assertNotIn("encryption:", api)

        ota = (self.root / "packages/base/ota.yaml").read_text(encoding="utf-8")
        self.assertIn("- platform: esphome", ota)
        ota_config_lines = [
            line for line in ota.splitlines() if not line.lstrip().startswith("#")
        ]
        self.assertNotIn("password", "\n".join(ota_config_lines))

        logging_text = (self.root / "packages/base/logging.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn("web_server:", logging_text)
        self.assertIn("port: 80", logging_text)
        self.assertIn("logger:", logging_text)
        self.assertNotIn("auth:", logging_text)

        wifi = (self.root / "packages/base/wifi.yaml").read_text(encoding="utf-8")
        # Setup path survives: setup-network join + open fallback AP +
        # captive portal.
        self.assertIn("!secret wifi_ssid", wifi)
        self.assertIn("!secret wifi_password", wifi)
        self.assertIn('ssid: "${fallback_ssid}"', wifi)
        self.assertIn("captive_portal:", wifi)
        self.assertNotIn("!secret fallback_ap_password", wifi)

    def test_patched_files_remain_parseable_yaml(self) -> None:
        self.assertEqual(self._run_main(self.root)[0], 0)
        for rel in BASE_FILES:
            with self.subTest(file=rel):
                text = (self.root / rel).read_text(encoding="utf-8")
                data = yaml.load(text, Loader=_EsphomeTagLoader)
                self.assertIsInstance(data, dict)

    def test_second_run_fails_one_shot_semantics(self) -> None:
        self.assertEqual(self._run_main(self.root)[0], 0)
        code, _, err = self._run_main(self.root)
        self.assertEqual(code, 1)
        self.assertIn("already applied", err)

    def test_unexpected_file_shape_fails_closed(self) -> None:
        # Simulate a refactor that moves the OTA password out of the shape
        # the patch expects: the patch must fail, not silently continue.
        ota = self.root / "packages/base/ota.yaml"
        ota.write_text(
            "ota:\n  - platform: esphome\n    password: !secret renamed_key\n",
            encoding="utf-8",
        )
        code, _, err = self._run_main(self.root)
        self.assertEqual(code, 1)
        self.assertIn("failing closed", err)
        self.assertIn("ota.yaml", err)

    def test_missing_base_file_fails_closed(self) -> None:
        (self.root / "packages/base/api_encrypted.yaml").unlink()
        code, _, err = self._run_main(self.root)
        self.assertEqual(code, 1)
        self.assertIn("does not exist", err)


if __name__ == "__main__":
    unittest.main(verbosity=2)

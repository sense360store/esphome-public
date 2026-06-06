#!/usr/bin/env python3
"""SEC-ESP-BUILD-GATES-001 regression guard for the api_encryption_key gate.

Locks in ``scripts/check_api_encryption_key.py`` (security.md finding #4):

  * the all-"a" placeholder (and any single-repeated-char base64 key, and an
    empty/missing key) is a placeholder;
  * only ``stable`` (or an explicit ``--release``) is a production build;
  * a production build with a placeholder key is rejected (exit 1), a
    production build with no key is a usage error (exit 2), and a production
    build with a real key passes (exit 0);
  * preview / beta / compile-only builds keep using the placeholder (exit 0).

Run with::

    python3 tests/test_check_api_encryption_key.py
"""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_api_encryption_key.py"
REAL_KEY = "Yt+3xH0k2m9QF7sP1bZ8cV6nL4wR0aD5gJ2kE7uM3o="


def _load_module():
    spec = importlib.util.spec_from_file_location("check_api_encryption_key", SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


class ClassifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _load_module()

    def test_placeholder_detection(self) -> None:
        self.assertTrue(self.mod.is_placeholder_key(self.mod.EXAMPLE_KEY))
        self.assertTrue(self.mod.is_placeholder_key("a" * 43 + "="))
        self.assertTrue(self.mod.is_placeholder_key("b" * 43 + "="))
        self.assertTrue(self.mod.is_placeholder_key(""))
        self.assertTrue(self.mod.is_placeholder_key(None))

    def test_real_key_is_not_placeholder(self) -> None:
        self.assertFalse(self.mod.is_placeholder_key(REAL_KEY))

    def test_production_channels(self) -> None:
        self.assertTrue(self.mod.is_production("stable", False))
        self.assertTrue(self.mod.is_production("preview", True))  # --release forces it
        self.assertFalse(self.mod.is_production("preview", False))
        self.assertFalse(self.mod.is_production("beta", False))
        self.assertFalse(self.mod.is_production("", False))
        self.assertFalse(self.mod.is_production(None, False))


class GateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _load_module()

    def _secrets(self, key: str | None) -> Path:
        tmp = Path(tempfile.mkdtemp()) / "secrets.yaml"
        body = "wifi_ssid: x\n"
        if key is not None:
            body += f'api_encryption_key: "{key}"\n'
        tmp.write_text(body, encoding="utf-8")
        return tmp

    def test_preview_with_placeholder_is_allowed(self) -> None:
        secrets = self._secrets(self.mod.EXAMPLE_KEY)
        self.assertEqual(self.mod.main(["--secrets", str(secrets), "--channel", "preview"]), 0)

    def test_stable_with_placeholder_is_rejected(self) -> None:
        secrets = self._secrets(self.mod.EXAMPLE_KEY)
        self.assertEqual(self.mod.main(["--secrets", str(secrets), "--channel", "stable"]), 1)

    def test_stable_with_real_key_passes(self) -> None:
        secrets = self._secrets(REAL_KEY)
        self.assertEqual(self.mod.main(["--secrets", str(secrets), "--channel", "stable"]), 0)

    def test_stable_with_missing_key_is_usage_error(self) -> None:
        secrets = self._secrets(None)
        self.assertEqual(self.mod.main(["--secrets", str(secrets), "--channel", "stable"]), 2)

    def test_value_arg_with_release_flag(self) -> None:
        self.assertEqual(self.mod.main(["--value", REAL_KEY, "--release"]), 0)
        self.assertEqual(self.mod.main(["--value", self.mod.EXAMPLE_KEY, "--release"]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)

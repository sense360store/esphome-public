#!/usr/bin/env python3
"""SEC-ESP-FALLBACK-AP-001 regression guard for the fallback-AP password check.

Locks in the behaviour of ``scripts/check_fallback_ap_password.py`` (security.md
finding #1):

  * the two historical hardcoded literals (``Sense360Fallback`` /
    ``sense360poe``) are rejected, both in a provisioned ``secrets.yaml`` and as
    a committed ``fallback_ap_password:`` assignment under ``packages/`` /
    ``products/``;
  * the disposable CI/build credentials (``fallback123`` / ``sense360fallback``)
    are NOT rejected, so the compile / preview / release lanes stay green;
  * the live repository tree is clean (the literals were removed by
    SEC-ESP-FALLBACK-AP-001).

Run with::

    python3 tests/test_check_fallback_ap_password.py
"""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_fallback_ap_password.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("check_fallback_ap_password", SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


class IsBannedTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _load_module()

    def test_banned_literals_rejected(self) -> None:
        self.assertTrue(self.mod.is_banned("Sense360Fallback"))
        self.assertTrue(self.mod.is_banned("sense360poe"))

    def test_ci_build_literals_allowed(self) -> None:
        # These disposable test credentials must stay allowed so the compile /
        # preview / release lanes are not broken by the guard.
        self.assertFalse(self.mod.is_banned("fallback123"))
        self.assertFalse(self.mod.is_banned("sense360fallback"))

    def test_match_is_exact_and_case_sensitive(self) -> None:
        self.assertFalse(self.mod.is_banned("sense360fallback"))  # lower != mixed
        self.assertFalse(self.mod.is_banned("SENSE360POE"))
        self.assertFalse(self.mod.is_banned("REPLACE_WITH_SECURE_FALLBACK_PASSWORD"))


class SecretsCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _load_module()

    def _write_secrets(self, value: str) -> Path:
        tmp = Path(tempfile.mkdtemp()) / "secrets.yaml"
        tmp.write_text(
            "wifi_ssid: x\n"
            "wifi_password: y\n"
            f'fallback_ap_password: "{value}"\n',
            encoding="utf-8",
        )
        return tmp

    def test_banned_secret_value_flagged(self) -> None:
        for banned in ("Sense360Fallback", "sense360poe"):
            problems = self.mod.check_secrets(self._write_secrets(banned))
            self.assertTrue(problems, f"{banned!r} should be flagged")

    def test_allowed_secret_value_clean(self) -> None:
        for allowed in ("fallback123", "sense360fallback", "a-strong-unique-pw"):
            problems = self.mod.check_secrets(self._write_secrets(allowed))
            self.assertEqual(problems, [], f"{allowed!r} should be clean")

    def test_missing_secrets_file_is_not_an_error(self) -> None:
        self.assertEqual(self.mod.check_secrets(Path("/nonexistent/secrets.yaml")), [])


class CommittedTreeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _load_module()

    def test_live_repo_tree_is_clean(self) -> None:
        # After SEC-ESP-FALLBACK-AP-001 no committed packages/ or products/ YAML
        # may assign a banned fallback_ap_password literal.
        problems = self.mod.scan_committed(REPO_ROOT)
        self.assertEqual(problems, [], "\n".join(problems))

    def test_planted_literal_is_detected(self) -> None:
        root = Path(tempfile.mkdtemp())
        (root / "packages").mkdir()
        (root / "packages" / "wifi.yaml").write_text(
            'substitutions:\n  fallback_ap_password: "Sense360Fallback"\n',
            encoding="utf-8",
        )
        problems = self.mod.scan_committed(root)
        self.assertEqual(len(problems), 1, problems)

    def test_main_exit_codes(self) -> None:
        # Clean live tree (committed-config scan only) exits 0.
        self.assertEqual(self.mod.main([]), 0)
        # A banned provisioned secrets.yaml exits non-zero.
        tmp = Path(tempfile.mkdtemp()) / "secrets.yaml"
        tmp.write_text('fallback_ap_password: "sense360poe"\n', encoding="utf-8")
        self.assertEqual(self.mod.main(["--secrets", str(tmp)]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)

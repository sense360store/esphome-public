#!/usr/bin/env python3
"""SEC-ESP-BUILD-GATES-001 regression guard for the default-credential gate.

Locks in the behaviour of ``scripts/check_firmware_default_credentials.py``
(SECURITY-AUDIT-2026-06 findings H1 and the forward half of H2):

  * a firmware binary containing ANY denylisted default / placeholder /
    burned credential byte-string fails the gate, and the failure names the
    artifact and the credential class;
  * the placeholder API encryption key is caught BOTH as the base64 literal
    and as its decoded 32-byte key material (the form ESPHome stores);
  * a clean binary passes;
  * the two intentionally-public setup-network credentials are excluded —
    and ONLY those two; the api/ota/web/fallback classes are never excluded;
  * the gate fails closed when there is nothing to scan.

Run with::

    python3 tests/test_check_firmware_default_credentials.py
"""

from __future__ import annotations

import base64
import contextlib
import importlib.util
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_firmware_default_credentials.py"

# Filler that cannot accidentally contain an ASCII credential needle: a fake
# ESP32 image magic byte followed by a strictly ascending byte ramp, repeated.
CLEAN_FILLER = (b"\xe9" + bytes(range(255))) * 64


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "check_firmware_default_credentials", SCRIPT_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _make_bin(directory: Path, name: str, embedded: bytes = b"") -> Path:
    """Write a synthetic firmware binary with `embedded` spliced mid-payload."""
    path = directory / name
    half = len(CLEAN_FILLER) // 2
    path.write_bytes(CLEAN_FILLER[:half] + embedded + CLEAN_FILLER[half:])
    return path


class DenylistContractTests(unittest.TestCase):
    """The shape of the denylist itself is part of the security contract."""

    def setUp(self) -> None:
        self.mod = _load_module()

    def test_four_device_control_classes_are_always_present(self) -> None:
        classes = {entry[0] for entry in self.mod.DENYLIST}
        for required in (
            "api_encryption_key",
            "ota_password",
            "web_password",
            "fallback_ap_password",
        ):
            self.assertIn(required, classes)
        # The pin the module itself exports must agree.
        self.assertEqual(
            set(self.mod.NEVER_EXCLUDED_CLASSES),
            {
                "api_encryption_key",
                "ota_password",
                "web_password",
                "fallback_ap_password",
            },
        )

    def test_api_key_denied_as_literal_and_decoded_material(self) -> None:
        needles = {n for c, _, n in self.mod.DENYLIST if c == "api_encryption_key"}
        literal = b"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa="
        self.assertIn(literal, needles)
        decoded = base64.b64decode(literal)
        self.assertEqual(len(decoded), 32)
        self.assertIn(decoded, needles)

    def test_burned_h2_history_literals_are_denied(self) -> None:
        # Audit H2 forward half: the pre-remediation fallback-AP literals are
        # permanently burned and must never ship in a future release binary.
        needles = {n for c, _, n in self.mod.DENYLIST if c == "fallback_ap_password"}
        self.assertIn(b"Sense360Fallback", needles)
        self.assertIn(b"sense360poe", needles)

    def test_setup_network_credentials_are_excluded_and_only_those(self) -> None:
        # The intentionally-public setup-only WiFi pair is documented and
        # excluded. Nothing else from the shipped credential set may be.
        self.assertEqual(
            set(self.mod.INTENTIONALLY_PUBLIC_SETUP_CREDENTIALS),
            {b"Sense360_Setup", b"sense360setup"},
        )
        denylisted = {n for _, _, n in self.mod.DENYLIST}
        for excluded in self.mod.INTENTIONALLY_PUBLIC_SETUP_CREDENTIALS:
            self.assertNotIn(excluded, denylisted)

    def test_bare_admin_username_is_not_a_needle(self) -> None:
        # "admin" alone is a generic token that false-positives on legitimate
        # binary content; the web class is enforced via its passwords.
        self.assertNotIn(b"admin", {n for _, _, n in self.mod.DENYLIST})


class ScanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _load_module()
        self.tmp = Path(tempfile.mkdtemp())

    def _run_main(self, argv: list[str]) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = self.mod.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_every_denylisted_needle_fails_a_dirty_binary(self) -> None:
        for cred_class, label, needle in self.mod.DENYLIST:
            with self.subTest(cred_class=cred_class, label=label):
                path = _make_bin(self.tmp, f"dirty-{abs(hash(needle))}.bin", needle)
                code, _, err = self._run_main([str(path)])
                self.assertEqual(code, 1, f"{cred_class} ({label}) must fail the gate")
                self.assertIn(path.name, err)
                self.assertIn(f"[{cred_class}]", err)
                path.unlink()

    def test_clean_binary_passes(self) -> None:
        path = _make_bin(self.tmp, "clean.bin")
        code, out, err = self._run_main([str(path)])
        self.assertEqual(code, 0, err)
        self.assertIn("no default/placeholder credential material", out)

    def test_setup_network_credentials_do_not_fail_a_binary(self) -> None:
        # Released firmware legitimately contains the intentionally-public
        # setup-network SSID/password; the gate must not flag them.
        path = _make_bin(self.tmp, "setup.bin", b"Sense360_Setup\x00sense360setup")
        code, _, err = self._run_main([str(path)])
        self.assertEqual(code, 0, err)

    def test_failure_names_the_dirty_artifact_among_clean_ones(self) -> None:
        _make_bin(self.tmp, "a-clean.bin")
        _make_bin(self.tmp, "b-dirty.bin", b"sense360-ota-default")
        _make_bin(self.tmp, "c-clean.bin")
        code, _, err = self._run_main(["--dir", str(self.tmp)])
        self.assertEqual(code, 1)
        self.assertIn("b-dirty.bin", err)
        self.assertIn("[ota_password]", err)
        self.assertNotIn("a-clean.bin", err)
        self.assertNotIn("c-clean.bin", err)

    def test_decoded_api_key_material_fails_without_the_literal(self) -> None:
        decoded = base64.b64decode(b"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa=")
        path = _make_bin(self.tmp, "keyed.bin", decoded)
        code, _, err = self._run_main([str(path)])
        self.assertEqual(code, 1)
        self.assertIn("[api_encryption_key]", err)

    def test_empty_artifact_set_fails_closed(self) -> None:
        empty = self.tmp / "empty-dir"
        empty.mkdir()
        code, _, err = self._run_main(["--dir", str(empty)])
        self.assertEqual(code, 2)
        self.assertIn("fails closed", err)

    def test_missing_artifact_fails(self) -> None:
        code, _, err = self._run_main([str(self.tmp / "nope.bin")])
        self.assertEqual(code, 2)
        self.assertIn("does not exist", err)

    def test_dir_and_positional_arguments_combine(self) -> None:
        sub = self.tmp / "all-firmware"
        sub.mkdir()
        _make_bin(sub, "x.bin")
        extra = _make_bin(self.tmp, "extra.bin")
        code, out, _ = self._run_main(["--dir", str(sub), str(extra)])
        self.assertEqual(code, 0)
        self.assertIn("2 firmware binaries", out)


class CommandLineIntegrationTests(unittest.TestCase):
    """Run the gate exactly as the release workflow invokes it."""

    def test_subprocess_exit_codes(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        dirty = _make_bin(tmp, "dirty.bin", b"fallback123")
        clean = _make_bin(tmp, "clean.bin")

        failing = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(dirty)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(failing.returncode, 1, failing.stderr)
        self.assertIn("[fallback_ap_password]", failing.stderr)

        passing = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(clean)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(passing.returncode, 0, passing.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)

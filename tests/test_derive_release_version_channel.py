#!/usr/bin/env python3
"""RELEASE-004 unit tests for scripts/derive_release_version_channel.py.

Locks in the agreed normalization mapping between a GitHub release tag
(plus the release's ``prerelease`` flag) and the
``(version, channel)`` pair the Build & Release Firmware workflow uses
to filter ``config/webflash-builds.json``.

Run with:

    python3 tests/test_derive_release_version_channel.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "derive_release_version_channel.py"

sys.path.insert(0, str(REPO_ROOT / "scripts"))

from derive_release_version_channel import (  # noqa: E402
    DeriveError,
    derive,
)


class DeriveFunctionTests(unittest.TestCase):
    def test_stable_plain_tag(self) -> None:
        self.assertEqual(derive("v1.0.0", False), ("1.0.0", "stable"))

    def test_stable_tag_without_v_prefix(self) -> None:
        self.assertEqual(derive("1.0.0", False), ("1.0.0", "stable"))

    def test_preview_led_preview_suffix(self) -> None:
        self.assertEqual(derive("v1.0.0-led-preview", True), ("1.0.0", "preview"))

    def test_preview_generic_preview_suffix(self) -> None:
        self.assertEqual(derive("v1.0.0-preview", True), ("1.0.0", "preview"))

    def test_prerelease_plain_tag_is_preview(self) -> None:
        # A prerelease tagged with a plain semver string (no suffix) is
        # still a preview release per the prerelease flag. This preserves
        # the workflow's pre-RELEASE-004 behavior for that shape.
        self.assertEqual(derive("v1.0.0", True), ("1.0.0", "preview"))

    def test_stable_suffixed_tag_rejected(self) -> None:
        with self.assertRaises(DeriveError) as ctx:
            derive("v1.0.0-led-preview", False)
        self.assertIn("plain semantic tag", str(ctx.exception))

    def test_stable_generic_suffixed_tag_rejected(self) -> None:
        with self.assertRaises(DeriveError) as ctx:
            derive("v1.0.0-preview", False)
        self.assertIn("plain semantic tag", str(ctx.exception))

    def test_prerelease_unknown_suffix_rejected(self) -> None:
        with self.assertRaises(DeriveError) as ctx:
            derive("v1.0.0-foo", True)
        msg = str(ctx.exception)
        self.assertIn("unrecognized suffix", msg)
        self.assertIn("-led-preview", msg)
        self.assertIn("-preview", msg)

    def test_prerelease_typo_suffix_rejected(self) -> None:
        with self.assertRaises(DeriveError) as ctx:
            derive("v1.0.0-prevue", True)
        self.assertIn("unrecognized suffix", str(ctx.exception))

    def test_prerelease_nested_dash_in_version_rejected(self) -> None:
        with self.assertRaises(DeriveError) as ctx:
            derive("v1.0.0-rc1-led-preview", True)
        self.assertIn("nested '-'", str(ctx.exception))

    def test_empty_tag_rejected(self) -> None:
        with self.assertRaises(DeriveError):
            derive("", False)

    def test_v_only_tag_rejected(self) -> None:
        with self.assertRaises(DeriveError):
            derive("v", False)

    def test_preview_suffix_alone_rejected(self) -> None:
        with self.assertRaises(DeriveError) as ctx:
            derive("v-led-preview", True)
        self.assertIn("no version part", str(ctx.exception))


class DeriveCLITests(unittest.TestCase):
    """Smoke test the CLI surface used by the workflow."""

    def _run(self, tag: str, prerelease: str) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env["GITHUB_REF_NAME"] = tag
        env["PRERELEASE"] = prerelease
        env.pop("GITHUB_OUTPUT", None)
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH)],
            env=env,
            capture_output=True,
            text=True,
        )

    def test_cli_stable_tag(self) -> None:
        result = self._run("v1.0.0", "false")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("version=1.0.0", result.stdout)
        self.assertIn("channel=stable", result.stdout)

    def test_cli_led_preview_tag(self) -> None:
        result = self._run("v1.0.0-led-preview", "true")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("version=1.0.0", result.stdout)
        self.assertIn("channel=preview", result.stdout)

    def test_cli_preview_tag(self) -> None:
        result = self._run("v1.0.0-preview", "true")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("version=1.0.0", result.stdout)
        self.assertIn("channel=preview", result.stdout)

    def test_cli_rejects_stable_suffix(self) -> None:
        result = self._run("v1.0.0-led-preview", "false")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("plain semantic tag", result.stderr)

    def test_cli_rejects_unknown_prerelease_suffix(self) -> None:
        result = self._run("v1.0.0-foo", "true")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unrecognized suffix", result.stderr)

    def test_cli_writes_github_output(self) -> None:
        with tempfile.NamedTemporaryFile(
            "w+", suffix=".out", delete=False, encoding="utf-8"
        ) as tmp:
            output_path = Path(tmp.name)
        try:
            env = os.environ.copy()
            env["GITHUB_REF_NAME"] = "v1.0.0-led-preview"
            env["PRERELEASE"] = "true"
            env["GITHUB_OUTPUT"] = str(output_path)
            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH)],
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            written = output_path.read_text(encoding="utf-8")
            self.assertIn("version=1.0.0", written)
            self.assertIn("channel=preview", written)
        finally:
            try:
                output_path.unlink()
            except OSError:
                pass


if __name__ == "__main__":
    unittest.main(verbosity=2)

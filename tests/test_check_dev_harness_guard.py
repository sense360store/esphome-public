#!/usr/bin/env python3
"""Unit tests for scripts/check_dev_harness_guard.py (DEV-HARNESS-001).

Uses Python's stdlib unittest (matching this repo's no-pytest convention for
Python validators). Fully offline: the guard only reads local files.

Run with:
    python3 tests/test_check_dev_harness_guard.py
"""

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_dev_harness_guard.py"

_spec = importlib.util.spec_from_file_location("check_dev_harness_guard", SCRIPT_PATH)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
sys.modules["check_dev_harness_guard"] = _mod


class TestOverlayCheck(unittest.TestCase):
    """The overlay may contain only comments and blank lines."""

    def _write_overlay(self, tmpdir: str, content: str) -> Path:
        path = Path(tmpdir) / "dev-overlay.yaml"
        path.write_text(content, encoding="utf-8")
        return path

    def test_comments_and_blanks_pass(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            overlay = self._write_overlay(
                tmpdir, "# header comment\n\n  # indented comment\n\n"
            )
            self.assertEqual(_mod.overlay_problems(overlay), [])

    def test_functional_content_fails_with_promote_message(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            overlay = self._write_overlay(
                tmpdir,
                "# scratch experiment\n"
                "sensor:\n"
                "  - platform: template\n"
                "    name: Bench Test\n",
            )
            problems = _mod.overlay_problems(overlay)
            self.assertTrue(problems)
            self.assertIn(
                "promote overlay content into a package layer before merge",
                problems[0],
            )

    def test_inline_comment_after_content_still_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            overlay = self._write_overlay(tmpdir, "switch: []  # sneaky\n")
            self.assertTrue(_mod.overlay_problems(overlay))

    def test_missing_overlay_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            missing = Path(tmpdir) / "dev-overlay.yaml"
            problems = _mod.overlay_problems(missing)
            self.assertTrue(problems)
            self.assertIn("missing", problems[0])

    def test_committed_overlay_is_empty(self):
        """The live committed dev/dev-overlay.yaml must pass the guard."""
        self.assertEqual(_mod.overlay_problems(_mod.OVERLAY_PATH), [])


class TestConfigDevReferences(unittest.TestCase):
    """No config/*.json build declaration may reference a dev/ path."""

    def test_clean_config_dir_passes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "webflash-builds.json"
            path.write_text(
                json.dumps(
                    {
                        "builds": [
                            {
                                "product_yaml": (
                                    "products/webflash/ceiling-poe-roomiq.yaml"
                                ),
                                "channel": "stable",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(_mod.config_dev_references(Path(tmpdir)), [])

    def test_dev_reference_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "webflash-builds.json"
            path.write_text(
                json.dumps({"builds": [{"product_yaml": "dev/device-template.yaml"}]}),
                encoding="utf-8",
            )
            problems = _mod.config_dev_references(Path(tmpdir))
            self.assertTrue(problems)
            self.assertIn("dev/device-template.yaml", problems[0])

    def test_nested_dev_reference_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "targets.json"
            path.write_text(
                json.dumps({"targets": [{"files": ["repo/dev/foo.yaml"]}]}),
                encoding="utf-8",
            )
            self.assertTrue(_mod.config_dev_references(Path(tmpdir)))

    def test_unparseable_json_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "broken.json"
            path.write_text("{not json", encoding="utf-8")
            self.assertTrue(_mod.config_dev_references(Path(tmpdir)))

    def test_live_config_dir_has_no_dev_references(self):
        """The live committed config/*.json set must pass the guard."""
        self.assertEqual(_mod.config_dev_references(_mod.CONFIG_DIR), [])


class TestMainExitCodes(unittest.TestCase):
    def _run_main(self, argv):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = _mod.main(argv)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_live_repo_passes(self):
        code, stdout, _ = self._run_main([])
        self.assertEqual(code, 0)
        self.assertIn("guard passed", stdout)

    def test_populated_overlay_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            overlay = Path(tmpdir) / "dev-overlay.yaml"
            overlay.write_text("binary_sensor: []\n", encoding="utf-8")
            code, _, stderr = self._run_main(["--overlay", str(overlay)])
            self.assertEqual(code, 1)
            self.assertIn(
                "promote overlay content into a package layer before merge",
                stderr,
            )


if __name__ == "__main__":
    unittest.main()

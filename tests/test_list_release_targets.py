#!/usr/bin/env python3
"""Unit tests for scripts/list_release_targets.py (RELEASE-PRODUCT-SELECTION-001).

Uses Python's stdlib ``unittest`` (matching the no-pytest convention the
rest of the validators in this repo use). Run with::

    python3 tests/test_list_release_targets.py

The tests lock in the RELEASE-PRODUCT-SELECTION-001 contract:

  * the selectable release-target list is derived from
    ``config/webflash-builds.json`` (the same single source of truth the
    release workflow's build matrix uses);
  * the canonical list contains the two release-eligible builds the
    workflow currently ships (stable RoomIQ + preview LED) — adding a
    new release-eligible build to ``config/webflash-builds.json``
    automatically makes it selectable;
  * FanRelay / FanPWM / FanDAC are **not** selectable (they are
    manual-candidate-only and the helper refuses to enumerate a fan
    token in the release matrix);
  * ``validate_target`` accepts any release-eligible ``config_string``
    and the ``all-release-eligible`` sentinel, and rejects everything
    else;
  * the helper is read-only — calling ``main`` never writes
    ``firmware/sources.json`` / ``manifest.json``.
"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "list_release_targets.py"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


lrt = _load_module("list_release_targets", SCRIPT_PATH)

STABLE_CONFIG = "Ceiling-POE-VentIQ-RoomIQ"
LED_CONFIG = "Ceiling-POE-VentIQ-RoomIQ-LED"
FAN_TOKENS = ("FanRelay", "FanPWM", "FanDAC")


class CanonicalTargetListTests(unittest.TestCase):
    def test_targets_come_from_webflash_builds_json(self) -> None:
        targets = lrt.list_targets()
        config_strings = {t["config_string"] for t in targets}
        builds_doc = json.loads(
            (REPO_ROOT / "config" / "webflash-builds.json").read_text(
                encoding="utf-8"
            )
        )
        expected = {
            e["config_string"]
            for e in builds_doc["builds"]
            if isinstance(e, dict)
        }
        self.assertEqual(config_strings, expected)

    def test_includes_stable_roomiq_and_preview_led(self) -> None:
        config_strings = set(lrt.selectable_config_strings())
        self.assertIn(STABLE_CONFIG, config_strings)
        self.assertIn(LED_CONFIG, config_strings)

    def test_target_records_channel_and_version(self) -> None:
        by_cfg = {t["config_string"]: t for t in lrt.list_targets()}
        self.assertEqual(by_cfg[STABLE_CONFIG]["channel"], "stable")
        self.assertEqual(by_cfg[STABLE_CONFIG]["version"], "1.0.0")
        self.assertEqual(by_cfg[LED_CONFIG]["channel"], "preview")
        self.assertEqual(by_cfg[LED_CONFIG]["version"], "1.0.0")

    def test_target_records_artifact_name(self) -> None:
        by_cfg = {t["config_string"]: t for t in lrt.list_targets()}
        self.assertEqual(
            by_cfg[STABLE_CONFIG]["artifact_name"],
            "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin",
        )
        self.assertEqual(
            by_cfg[LED_CONFIG]["artifact_name"],
            "Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin",
        )


class FanExclusionTests(unittest.TestCase):
    def test_fans_are_not_selectable(self) -> None:
        config_strings = lrt.selectable_config_strings()
        for token in FAN_TOKENS:
            self.assertFalse(
                any(token.lower() in c.lower() for c in config_strings),
                f"{token} must not appear as a selectable release target",
            )

    def test_validate_rejects_fan_family_token(self) -> None:
        for token in FAN_TOKENS:
            err = lrt.validate_target(f"Ceiling-POE-VentIQ-{token}-RoomIQ")
            self.assertIsNotNone(err)
            self.assertIn("not a selectable release target", err)

    def test_guardrail_refuses_fan_token_in_builds_json(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            builds = Path(d) / "builds.json"
            builds.write_text(
                json.dumps(
                    {
                        "builds": [
                            {
                                "config_string": "Ceiling-POE-VentIQ-FanRelay-RoomIQ",
                                "channel": "stable",
                                "version": "1.0.0",
                                "artifact_name": "x.bin",
                                "product_yaml": "products/webflash/x.yaml",
                            }
                        ]
                    }
                )
            )
            with self.assertRaises(lrt.ListReleaseTargetsError) as ctx:
                lrt.list_targets(builds)
            self.assertIn("FanRelay", str(ctx.exception))


class ValidateTargetTests(unittest.TestCase):
    def test_accepts_release_eligible_config_string(self) -> None:
        self.assertIsNone(lrt.validate_target(STABLE_CONFIG))
        self.assertIsNone(lrt.validate_target(LED_CONFIG))

    def test_accepts_all_release_eligible_sentinel(self) -> None:
        self.assertIsNone(lrt.validate_target("all-release-eligible"))
        # The sentinel constant must stay in sync with the workflow input.
        self.assertEqual(lrt.ALL_TARGETS_SENTINEL, "all-release-eligible")

    def test_rejects_unknown_target(self) -> None:
        err = lrt.validate_target("Not-A-Real-Config")
        self.assertIsNotNone(err)
        self.assertIn("not a selectable release target", err)
        # The error message must enumerate the valid options so the
        # operator can correct a typo without grepping config files.
        self.assertIn(STABLE_CONFIG, err)
        self.assertIn(LED_CONFIG, err)
        self.assertIn("all-release-eligible", err)

    def test_rejects_empty_identifier(self) -> None:
        err = lrt.validate_target("")
        self.assertIsNotNone(err)
        self.assertIn("empty", err.lower())


class MainCliTests(unittest.TestCase):
    def test_main_validate_exits_zero_on_valid(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = lrt.main(["--validate", STABLE_CONFIG])
        self.assertEqual(rc, 0)
        self.assertIn("selectable release target", buf.getvalue())

    def test_main_validate_exits_two_on_invalid(self) -> None:
        rc = lrt.main(["--validate", "Not-Real"])
        self.assertEqual(rc, 2)

    def test_main_json_emits_valid_json(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = lrt.main(["--json"])
        self.assertEqual(rc, 0)
        data = json.loads(buf.getvalue())
        self.assertIsInstance(data, list)
        self.assertTrue(all("config_string" in e for e in data))

    def test_main_config_strings_one_per_line(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = lrt.main(["--config-strings"])
        self.assertEqual(rc, 0)
        lines = [ln for ln in buf.getvalue().splitlines() if ln.strip()]
        self.assertIn(STABLE_CONFIG, lines)
        self.assertIn(LED_CONFIG, lines)

    def test_main_writes_no_release_side_effect_files(self) -> None:
        sources = REPO_ROOT / "firmware" / "sources.json"
        manifest = REPO_ROOT / "manifest.json"
        sources_before = sources.exists()
        manifest_before = manifest.exists()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = lrt.main([])
        self.assertEqual(rc, 0)
        self.assertEqual(sources.exists(), sources_before)
        self.assertEqual(manifest.exists(), manifest_before)


if __name__ == "__main__":
    unittest.main(verbosity=2)

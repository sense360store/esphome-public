#!/usr/bin/env python3
"""Unit tests for scripts/check-catalog-release-artifacts.py.

Uses Python's stdlib unittest (matching this repo's no-pytest convention for
Python validators). These tests are fully offline: the GitHub query path is
exercised only through the parsed-data helpers, never the live gh CLI.

Run with:
    python3 tests/test_check_catalog_release_artifacts.py
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
SCRIPT_PATH = REPO_ROOT / "scripts" / "check-catalog-release-artifacts.py"

_spec = importlib.util.spec_from_file_location(
    "check_catalog_release_artifacts", SCRIPT_PATH
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
sys.modules["check_catalog_release_artifacts"] = _mod


# A small catalog with the four interesting shapes:
#   - a production build-matrix entry (must be verified)
#   - a preview build-matrix entry (must be verified)
#   - a blocked entry with no artifact_name (exempt)
#   - a legacy-compatible entry with no artifact_name (exempt)
SAMPLE_CATALOG = {
    "products": [
        {
            "config_string": "Ceiling-POE-VentIQ-RoomIQ",
            "status": "production",
            "version": "1.0.4",
            "channel": "stable",
            "artifact_name": "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.4-stable.bin",
            "webflash_build_matrix": True,
        },
        {
            "config_string": "Ceiling-POE-VentIQ-RoomIQ-LED",
            "status": "preview",
            "version": "1.0.0",
            "channel": "preview",
            "artifact_name": "Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin",
            "webflash_build_matrix": True,
        },
        {
            "config_string": "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ",
            "status": "blocked",
            "webflash_build_matrix": False,
        },
        {
            "legacy_config_id": "sense360-core-c-pwr-mains",
            "status": "legacy-compatible",
            "webflash_build_matrix": False,
        },
    ]
}

# gh-api-shaped released payload that backs both build-matrix artifacts.
RELEASES_OK = [
    {
        "tag_name": "v1.0.4",
        "draft": False,
        "prerelease": False,
        "assets": [
            {
                "name": "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.4-stable.bin",
                "size": 988448,
            },
            {"name": "checksums-sha256.txt", "size": 208},
        ],
    },
    {
        "tag_name": "v1.0.0-led-preview",
        "draft": False,
        "prerelease": True,
        "assets": [
            {
                "name": "Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin",
                "size": 1135904,
            }
        ],
    },
]


def _write(tmpdir: str, name: str, payload) -> str:
    path = Path(tmpdir) / name
    if isinstance(payload, str):
        path.write_text(payload)
    else:
        path.write_text(json.dumps(payload))
    return str(path)


class SelectBuildConfigsTests(unittest.TestCase):
    def test_selects_only_build_matrix_entries_with_artifact(self):
        configs = _mod.select_build_configs(SAMPLE_CATALOG)
        labels = sorted(c.label for c in configs)
        self.assertEqual(
            labels,
            ["Ceiling-POE-VentIQ-RoomIQ", "Ceiling-POE-VentIQ-RoomIQ-LED"],
        )

    def test_no_artifact_name_is_exempt_even_if_build_matrix_true(self):
        catalog = {
            "products": [
                # build_matrix true but no artifact_name -> not selected here
                {"config_string": "Weird", "webflash_build_matrix": True},
                # has artifact_name but build_matrix false -> not selected
                {
                    "config_string": "Other",
                    "webflash_build_matrix": False,
                    "artifact_name": "x.bin",
                },
                # mains board: CERN-OHL-P, no artifact_name -> exempt
                {
                    "legacy_config_id": "mains-psu-240v",
                    "status": "legacy-compatible",
                    "webflash_build_matrix": False,
                },
            ]
        }
        self.assertEqual(_mod.select_build_configs(catalog), [])

    def test_empty_string_artifact_name_not_selected(self):
        catalog = {
            "products": [
                {
                    "config_string": "Blank",
                    "webflash_build_matrix": True,
                    "artifact_name": "   ",
                }
            ]
        }
        self.assertEqual(_mod.select_build_configs(catalog), [])


class CollectReleasedAssetsTests(unittest.TestCase):
    def test_collects_names_and_sizes(self):
        assets = _mod.collect_released_assets(RELEASES_OK)
        self.assertIn("Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.4-stable.bin", assets)
        self.assertEqual(
            assets["Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.4-stable.bin"], 988448
        )

    def test_draft_releases_excluded(self):
        releases = [
            {
                "tag_name": "v9.9.9",
                "draft": True,
                "assets": [{"name": "phantom-draft.bin", "size": 999999}],
            }
        ]
        self.assertEqual(_mod.collect_released_assets(releases), {})

    def test_prerelease_included(self):
        releases = [
            {
                "tag_name": "v1.0.0-preview",
                "draft": False,
                "prerelease": True,
                "assets": [{"name": "preview.bin", "size": 500000}],
            }
        ]
        self.assertEqual(
            _mod.collect_released_assets(releases), {"preview.bin": 500000}
        )

    def test_duplicate_asset_keeps_largest_size(self):
        releases = [
            {"draft": False, "assets": [{"name": "dup.bin", "size": 10}]},
            {"draft": False, "assets": [{"name": "dup.bin", "size": 20}]},
        ]
        self.assertEqual(_mod.collect_released_assets(releases), {"dup.bin": 20})


class ParseReleasedAssetsTextTests(unittest.TestCase):
    def test_parses_releases_json_array(self):
        assets = _mod.parse_released_assets_text(json.dumps(RELEASES_OK))
        self.assertIn("Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.4-stable.bin", assets)

    def test_parses_single_release_object(self):
        assets = _mod.parse_released_assets_text(json.dumps(RELEASES_OK[0]))
        self.assertIn("Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.4-stable.bin", assets)

    def test_parses_json_array_of_names(self):
        assets = _mod.parse_released_assets_text(json.dumps(["a.bin", "b.bin"]))
        self.assertEqual(assets, {"a.bin": None, "b.bin": None})

    def test_parses_newline_list(self):
        assets = _mod.parse_released_assets_text("a.bin\n b.bin \n\n")
        self.assertEqual(assets, {"a.bin": None, "b.bin": None})


class EvaluateTests(unittest.TestCase):
    def test_all_present_passes(self):
        configs = _mod.select_build_configs(SAMPLE_CATALOG)
        released = _mod.collect_released_assets(RELEASES_OK)
        errors, checked = _mod.evaluate(configs, released, _mod.DEFAULT_MIN_SIZE_BYTES)
        self.assertEqual(errors, [])
        self.assertEqual(len(checked), 2)

    def test_phantom_version_fails_with_clear_message(self):
        configs = _mod.select_build_configs(SAMPLE_CATALOG)
        # Drop the LED artifact from the released set -> phantom.
        released = {
            "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.4-stable.bin": 988448,
        }
        errors, checked = _mod.evaluate(configs, released, _mod.DEFAULT_MIN_SIZE_BYTES)
        self.assertEqual(len(errors), 1)
        self.assertIn("no released artifact", errors[0])
        self.assertIn(
            "Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin", errors[0]
        )
        self.assertEqual(len(checked), 1)

    def test_size_floor_enforced_when_known(self):
        configs = _mod.select_build_configs(SAMPLE_CATALOG)
        released = {
            "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.4-stable.bin": 5,  # too small
            "Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin": 1135904,
        }
        errors, _checked = _mod.evaluate(configs, released, _mod.DEFAULT_MIN_SIZE_BYTES)
        self.assertTrue(any("too small" in e for e in errors), errors)

    def test_size_floor_skipped_when_unknown(self):
        configs = _mod.select_build_configs(SAMPLE_CATALOG)
        # newline-list shape -> sizes are None -> membership only
        released = {
            "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.4-stable.bin": None,
            "Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin": None,
        }
        errors, checked = _mod.evaluate(configs, released, _mod.DEFAULT_MIN_SIZE_BYTES)
        self.assertEqual(errors, [])
        self.assertEqual(len(checked), 2)


class MainTests(unittest.TestCase):
    """End-to-end main() via temp files (offline --released-assets path)."""

    def _run(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = _mod.main(argv)
        return rc, out.getvalue(), err.getvalue()

    def test_main_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            catalog = _write(tmp, "catalog.json", SAMPLE_CATALOG)
            assets = _write(tmp, "releases.json", RELEASES_OK)
            rc, out, _err = self._run(
                ["--catalog", catalog, "--released-assets", assets]
            )
            self.assertEqual(rc, 0, out)
            self.assertIn("OK:", out)

    def test_main_phantom_fails_exit_1(self):
        phantom_catalog = json.loads(json.dumps(SAMPLE_CATALOG))
        # Bump the LED entry to a version with no released artifact.
        phantom_catalog["products"][1]["version"] = "1.0.3"
        phantom_catalog["products"][1][
            "artifact_name"
        ] = "Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.3-preview.bin"
        with tempfile.TemporaryDirectory() as tmp:
            catalog = _write(tmp, "catalog.json", phantom_catalog)
            assets = _write(tmp, "releases.json", RELEASES_OK)
            rc, _out, err = self._run(
                ["--catalog", catalog, "--released-assets", assets]
            )
            self.assertEqual(rc, 1)
            self.assertIn("no released build", err)
            self.assertIn("v1.0.3-preview.bin", err)

    def test_main_missing_catalog_exit_2(self):
        rc, _out, err = self._run(
            ["--catalog", "/nonexistent/catalog.json", "--released-assets", "-"]
        )
        self.assertEqual(rc, 2)
        self.assertIn("not found", err)

    def test_main_zero_configs_fails_closed(self):
        empty = {"products": [{"config_string": "x", "webflash_build_matrix": False}]}
        with tempfile.TemporaryDirectory() as tmp:
            catalog = _write(tmp, "catalog.json", empty)
            assets = _write(tmp, "releases.json", RELEASES_OK)
            rc, _out, err = self._run(
                ["--catalog", catalog, "--released-assets", assets]
            )
            self.assertEqual(rc, 1)
            self.assertIn("no catalog configs", err)

    def test_main_zero_configs_allow_flag_passes(self):
        empty = {"products": [{"config_string": "x", "webflash_build_matrix": False}]}
        with tempfile.TemporaryDirectory() as tmp:
            catalog = _write(tmp, "catalog.json", empty)
            assets = _write(tmp, "releases.json", RELEASES_OK)
            rc, out, _err = self._run(
                [
                    "--catalog",
                    catalog,
                    "--released-assets",
                    assets,
                    "--allow-no-build-configs",
                ]
            )
            self.assertEqual(rc, 0, out)


if __name__ == "__main__":
    unittest.main()

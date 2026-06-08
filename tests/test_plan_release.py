#!/usr/bin/env python3
"""RELEASE-CREATE-001 unit tests for scripts/plan_release.py.

Offline and stdlib-only (matching the no-pytest convention the rest of
the validators in this repo use). Run with::

    python3 tests/test_plan_release.py

The pure tag/channel logic and the catalog-lookup rules are tested
against synthetic catalogs so they stay deterministic across version
bumps. A small set of version-agnostic integration tests then exercises
the real config/product-catalog.json (asserting the tag *shape* and the
prerelease flag, never a hardcoded version) so the script is proven
against live data without breaking every time Release 1 bumps a version.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "plan_release.py"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


pr = _load_module("plan_release", SCRIPT_PATH)


def _catalog(*entries: dict) -> dict:
    return {"products": list(entries)}


# Synthetic catalog rows. The version numbers here are fixtures, chosen so
# the "version does not match catalog" case has a stable, known message.
STABLE_CFG = "Ceiling-POE-VentIQ-RoomIQ"
PREVIEW_CFG = "Ceiling-POE-RoomIQ-LED"
STABLE_ROW = {
    "config_string": STABLE_CFG,
    "status": "production",
    "channel": "stable",
    "version": "1.0.1",
}
PREVIEW_ROW = {
    "config_string": PREVIEW_CFG,
    "status": "preview",
    "channel": "preview",
    "version": "1.0.0",
}


class PureTagLogicTests(unittest.TestCase):
    def test_is_prerelease_stable_is_false(self) -> None:
        self.assertFalse(pr.is_prerelease("stable"))

    def test_is_prerelease_non_stable_is_true(self) -> None:
        self.assertTrue(pr.is_prerelease("preview"))
        self.assertTrue(pr.is_prerelease("beta"))

    def test_compute_tag_stable_is_plain(self) -> None:
        self.assertEqual(pr.compute_tag("1.0.1", "stable"), "v1.0.1")

    def test_compute_tag_preview_defaults_to_channel_suffix(self) -> None:
        self.assertEqual(pr.compute_tag("1.0.0", "preview"), "v1.0.0-preview")

    def test_compute_tag_non_stable_honours_explicit_suffix(self) -> None:
        self.assertEqual(
            pr.compute_tag("1.0.0", "preview", "led-preview"),
            "v1.0.0-led-preview",
        )

    def test_compute_tag_stable_rejects_suffix(self) -> None:
        with self.assertRaises(pr.PlanReleaseError) as ctx:
            pr.compute_tag("1.0.0", "stable", "preview")
        self.assertIn("non-stable", str(ctx.exception))


class PlanReleaseRulesTests(unittest.TestCase):
    def test_stable_config_plain_tag_not_prerelease(self) -> None:
        plan = pr.plan_release(
            config_string=STABLE_CFG,
            version="1.0.1",
            catalog=_catalog(STABLE_ROW),
        )
        self.assertEqual(plan["tag"], "v1.0.1")
        self.assertEqual(plan["channel"], "stable")
        self.assertFalse(plan["prerelease"])

    def test_preview_config_preview_tag_is_prerelease(self) -> None:
        plan = pr.plan_release(
            config_string=PREVIEW_CFG,
            version="1.0.0",
            catalog=_catalog(PREVIEW_ROW),
        )
        self.assertEqual(plan["tag"], "v1.0.0-preview")
        self.assertEqual(plan["channel"], "preview")
        self.assertTrue(plan["prerelease"])

    def test_explicit_tag_suffix_honoured_for_non_stable(self) -> None:
        plan = pr.plan_release(
            config_string=PREVIEW_CFG,
            version="1.0.0",
            catalog=_catalog(PREVIEW_ROW),
            tag_suffix="led-preview",
        )
        self.assertEqual(plan["tag"], "v1.0.0-led-preview")
        self.assertEqual(plan["channel"], "preview")
        self.assertTrue(plan["prerelease"])

    def test_tag_suffix_on_stable_is_rejected(self) -> None:
        with self.assertRaises(pr.PlanReleaseError) as ctx:
            pr.plan_release(
                config_string=STABLE_CFG,
                version="1.0.1",
                catalog=_catalog(STABLE_ROW),
                tag_suffix="preview",
            )
        self.assertIn("non-stable", str(ctx.exception))

    def test_leading_v_version_is_accepted_and_equals_bare_catalog(self) -> None:
        # A leading 'v' (any case) and surrounding whitespace are tolerated:
        # 1.0.1, v1.0.1, and V1.0.1 all normalize to the bare 1.0.1 that
        # equals the catalog's bare version and produce the same plan.
        for raw in ("1.0.1", "v1.0.1", "V1.0.1", "  v1.0.1  "):
            with self.subTest(version=raw):
                plan = pr.plan_release(
                    config_string=STABLE_CFG,
                    version=raw,
                    catalog=_catalog(STABLE_ROW),
                )
                self.assertEqual(plan["version"], "1.0.1")
                self.assertEqual(plan["tag"], "v1.0.1")
                self.assertEqual(plan["channel"], "stable")
                self.assertFalse(plan["prerelease"])

    def test_normalize_version_helper(self) -> None:
        self.assertEqual(pr.normalize_version("1.0.5"), "1.0.5")
        self.assertEqual(pr.normalize_version("v1.0.5"), "1.0.5")
        self.assertEqual(pr.normalize_version("V1.0.5"), "1.0.5")
        self.assertEqual(pr.normalize_version("  v1.0.5  "), "1.0.5")

    def test_prerelease_suffix_is_still_rejected_even_with_leading_v(self) -> None:
        # The leading 'v' is stripped but the pre-release suffix is NOT, so
        # both forms still fail the bare-semver check (fail closed).
        for raw in ("1.0.5-preview", "v1.0.5-preview", "vv1.0.5", "1.0.5+build"):
            with self.subTest(version=raw):
                with self.assertRaises(pr.PlanReleaseError) as ctx:
                    pr.plan_release(
                        config_string=STABLE_CFG,
                        version=raw,
                        catalog=_catalog(STABLE_ROW),
                    )
                self.assertIn("semver", str(ctx.exception))

    def test_non_semver_version_is_rejected(self) -> None:
        with self.assertRaises(pr.PlanReleaseError) as ctx:
            pr.plan_release(
                config_string=STABLE_CFG,
                version="1.0",
                catalog=_catalog(STABLE_ROW),
            )
        self.assertIn("semver", str(ctx.exception))

    def test_version_not_matching_catalog_gives_bump_first_message(self) -> None:
        with self.assertRaises(pr.PlanReleaseError) as ctx:
            pr.plan_release(
                config_string=STABLE_CFG,
                version="1.0.0",
                catalog=_catalog(STABLE_ROW),
            )
        msg = str(ctx.exception)
        self.assertIn(
            "Catalog declares 1.0.1 for Ceiling-POE-VentIQ-RoomIQ, not 1.0.0",
            msg,
        )
        self.assertIn("Run Release 1: Bump Version and MERGE its PR first.", msg)

    def test_unknown_config_is_rejected(self) -> None:
        with self.assertRaises(pr.PlanReleaseError) as ctx:
            pr.plan_release(
                config_string="Not-A-Real-Config",
                version="1.0.1",
                catalog=_catalog(STABLE_ROW),
            )
        self.assertIn("not found", str(ctx.exception))


class CliTests(unittest.TestCase):
    """Smoke test the CLI surface the workflow drives."""

    def _write_catalog(self, dir_: str, data: dict) -> Path:
        path = Path(dir_) / "catalog.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def _run(self, catalog: Path, *args: str, github_output: str = None):
        env = os.environ.copy()
        if github_output is None:
            env.pop("GITHUB_OUTPUT", None)
        else:
            env["GITHUB_OUTPUT"] = github_output
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--catalog", str(catalog), *args],
            capture_output=True,
            text=True,
            env=env,
        )

    def test_cli_stable_prints_plain_tag(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            cat = self._write_catalog(d, _catalog(STABLE_ROW))
            res = self._run(cat, "--config", STABLE_CFG, "--version", "1.0.1")
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertIn("tag=v1.0.1", res.stdout)
            self.assertIn("channel=stable", res.stdout)
            self.assertIn("prerelease=false", res.stdout)

    def test_cli_preview_writes_github_output(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            cat = self._write_catalog(d, _catalog(PREVIEW_ROW))
            out_path = Path(d) / "out.txt"
            res = self._run(
                cat,
                "--config",
                PREVIEW_CFG,
                "--version",
                "1.0.0",
                github_output=str(out_path),
            )
            self.assertEqual(res.returncode, 0, res.stderr)
            written = out_path.read_text(encoding="utf-8")
            self.assertIn("tag=v1.0.0-preview", written)
            self.assertIn("channel=preview", written)
            self.assertIn("prerelease=true", written)

    def test_cli_leading_v_accepted_and_emits_normalized_version(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            cat = self._write_catalog(d, _catalog(STABLE_ROW))
            out_path = Path(d) / "out.txt"
            res = self._run(
                cat,
                "--config",
                STABLE_CFG,
                "--version",
                "V1.0.1",
                github_output=str(out_path),
            )
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertIn("tag=v1.0.1", res.stdout)
            # The normalized (bare) version is exposed for downstream steps.
            self.assertIn("version=1.0.1", res.stdout)
            self.assertIn("version=1.0.1", out_path.read_text(encoding="utf-8"))

    def test_cli_prerelease_suffix_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            cat = self._write_catalog(d, _catalog(STABLE_ROW))
            res = self._run(cat, "--config", STABLE_CFG, "--version", "v1.0.1-preview")
            self.assertNotEqual(res.returncode, 0)
            self.assertIn("semver", res.stderr)

    def test_cli_version_mismatch_exits_nonzero_with_bump_message(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            cat = self._write_catalog(d, _catalog(STABLE_ROW))
            res = self._run(cat, "--config", STABLE_CFG, "--version", "9.9.9")
            self.assertNotEqual(res.returncode, 0)
            self.assertIn(
                "Run Release 1: Bump Version and MERGE its PR first.",
                res.stderr,
            )


class RealCatalogIntegrationTests(unittest.TestCase):
    """Version-agnostic checks against the live product catalog.

    These read the catalog's *current* declared version rather than
    asserting a literal, so a Release 1 version bump never breaks them.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = pr.load_catalog(pr.DEFAULT_CATALOG_PATH)

    def test_real_stable_config_resolves_to_plain_tag(self) -> None:
        entry = pr.find_entry(self.catalog, "Ceiling-POE-VentIQ-RoomIQ")
        self.assertIsNotNone(entry, "stable Release-One config missing")
        self.assertEqual(entry["channel"], "stable")
        version = entry["version"]
        plan = pr.plan_release(
            config_string="Ceiling-POE-VentIQ-RoomIQ",
            version=version,
            catalog=self.catalog,
        )
        self.assertEqual(plan["tag"], f"v{version}")
        self.assertEqual(plan["channel"], "stable")
        self.assertFalse(plan["prerelease"])

    def test_real_preview_config_resolves_to_prerelease(self) -> None:
        entry = pr.find_entry(self.catalog, "Ceiling-POE-RoomIQ-LED")
        self.assertIsNotNone(entry, "preview LED config missing")
        self.assertEqual(entry["channel"], "preview")
        version = entry["version"]
        plan = pr.plan_release(
            config_string="Ceiling-POE-RoomIQ-LED",
            version=version,
            catalog=self.catalog,
        )
        self.assertEqual(plan["tag"], f"v{version}-preview")
        self.assertEqual(plan["channel"], "preview")
        self.assertTrue(plan["prerelease"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

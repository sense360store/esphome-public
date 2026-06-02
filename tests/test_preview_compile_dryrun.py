#!/usr/bin/env python3
"""Regression guard for the preview compile dry-run lane.

RELEASE-PREVIEW-COMPILE-DRYRUN-001.

Locks the invariants of the hosted preview / manual-preview compile dry-run:

  * ``scripts/list_preview_compile_targets.py`` scopes the compile dry-run to
    exactly the seven preview / manual-preview targets and NOTHING else (the
    stable baseline is never in scope; the TRIAC target is excluded by the
    ``HW-005`` buildability blocker and reported separately);
  * the emitted GitHub Actions matrix is well-formed and every in-scope
    ``product_yaml`` exists and agrees with ``config/preview-release-targets.json``;
  * ``.github/workflows/preview-compile-dryrun.yml`` is a safe dry-run lane:
    ``workflow_dispatch`` only, read-only token, no release/tag action, and it
    uploads only compile LOGS (never a ``.bin`` / firmware artifact).

Run with::

    python3 tests/test_preview_compile_dryrun.py
"""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "list_preview_compile_targets.py"
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "preview-compile-dryrun.yml"
MANIFEST_PATH = REPO_ROOT / "config" / "preview-release-targets.json"

# The exact in-scope set required by RELEASE-PREVIEW-COMPILE-DRYRUN-001.
EXPECTED_IN_SCOPE = [
    "Ceiling-POE-VentIQ-RoomIQ-LED",
    "Ceiling-POE-AirIQ-RoomIQ",
    "Ceiling-POE-RoomIQ",
    "Ceiling-POE-RoomIQ-LED",
    "Ceiling-POE-VentIQ-FanRelay-RoomIQ",
    "Ceiling-POE-FanPWM",
    "Ceiling-POE-FanDAC",
]
EXCLUDED_TRIAC = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"
STABLE_BASELINE = "Ceiling-POE-VentIQ-RoomIQ"


def _load_script():
    spec = importlib.util.spec_from_file_location(
        "list_preview_compile_targets", SCRIPT_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def _workflow_triggers(data: dict) -> dict:
    raw = data.get("on")
    if raw is None:
        raw = data.get(True)  # PyYAML parses bare `on:` as boolean True
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, list):
        return {k: None for k in raw}
    if isinstance(raw, str):
        return {raw: None}
    return {}


class PreviewCompileScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _load_script()
        cls.targets = cls.mod.scope_targets()
        cls.excluded = cls.mod.excluded_targets()

    def test_scope_is_exactly_the_seven_preview_targets(self) -> None:
        self.assertEqual(
            [t["config_string"] for t in self.targets], EXPECTED_IN_SCOPE
        )

    def test_stable_baseline_never_in_scope(self) -> None:
        self.assertNotIn(
            STABLE_BASELINE, [t["config_string"] for t in self.targets]
        )

    def test_triac_excluded_and_reported_with_hw005(self) -> None:
        in_scope = [t["config_string"] for t in self.targets]
        self.assertNotIn(EXCLUDED_TRIAC, in_scope)
        excluded_cs = [t["config_string"] for t in self.excluded]
        self.assertEqual(excluded_cs, [EXCLUDED_TRIAC])
        self.assertIn("HW-005", self.excluded[0]["build_blocker"])

    def test_in_scope_product_yamls_exist_and_match_manifest(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        yaml_by_cs = {
            t["config_string"]: t["yaml_path"] for t in manifest["targets"]
        }
        for target in self.targets:
            cs = target["config_string"]
            self.assertEqual(target["product_yaml"], yaml_by_cs[cs])
            self.assertTrue(
                (REPO_ROOT / target["product_yaml"]).is_file(),
                f"{cs}: product_yaml missing: {target['product_yaml']}",
            )

    def test_matrix_is_well_formed(self) -> None:
        matrix = self.mod.build_matrix(self.targets)
        self.assertIn("include", matrix)
        self.assertEqual(len(matrix["include"]), len(EXPECTED_IN_SCOPE))
        for entry in matrix["include"]:
            for key in ("id", "config_string", "product_yaml"):
                self.assertTrue(entry.get(key), f"matrix entry missing {key}")
        # The matrix must be JSON-serializable (consumed via fromJson in CI).
        self.assertIsInstance(json.dumps(matrix), str)

    def test_prior_compile_status_is_cited_not_invented(self) -> None:
        # The three webflash previews must still be pending-ci (no proof flipped
        # by this dry-run lane); the fans cite their prior validated-full-compile.
        status = {t["config_string"]: t["prior_compile_validation_status"]
                  for t in self.targets}
        for cs in ("Ceiling-POE-AirIQ-RoomIQ", "Ceiling-POE-RoomIQ",
                   "Ceiling-POE-RoomIQ-LED"):
            self.assertEqual(status[cs], "pending-ci")


class PreviewCompileWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.assertTrueExists = WORKFLOW_PATH.is_file()
        cls.data = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))

    def test_workflow_exists(self) -> None:
        self.assertTrue(self.assertTrueExists, f"missing {WORKFLOW_PATH}")

    def test_workflow_dispatch_only(self) -> None:
        triggers = _workflow_triggers(self.data)
        self.assertEqual(set(triggers), {"workflow_dispatch"})
        for forbidden in ("push", "pull_request", "pull_request_target", "release"):
            self.assertNotIn(forbidden, triggers)

    def test_compile_mode_default_is_metadata(self) -> None:
        inputs = _workflow_triggers(self.data)["workflow_dispatch"]["inputs"]
        self.assertEqual(inputs["compile_mode"]["default"], "metadata")
        self.assertEqual(
            sorted(inputs["compile_mode"]["options"]), ["full", "metadata"]
        )

    def test_token_is_read_only(self) -> None:
        self.assertEqual(self.data.get("permissions"), {"contents": "read"})
        for job_id, job in (self.data.get("jobs") or {}).items():
            perms = job.get("permissions")
            if perms is not None:
                self.assertNotIn(
                    "write", json.dumps(perms), f"job {job_id} requests write"
                )

    def test_compile_job_is_gated_on_full_mode(self) -> None:
        compile_job = self.data["jobs"]["compile-dryrun"]
        cond = compile_job.get("if", "")
        self.assertIn("compile_mode", cond)
        self.assertIn("full", cond)
        # fail-fast disabled so every target's pass/fail is recorded.
        self.assertFalse(compile_job["strategy"]["fail-fast"])

    def _iter_steps(self):
        for job in (self.data.get("jobs") or {}).values():
            for step in job.get("steps", []) or []:
                yield step

    def test_uploads_only_logs_never_firmware(self) -> None:
        uploaded_paths = []
        for step in self._iter_steps():
            uses = str(step.get("uses", ""))
            if "upload-artifact" in uses:
                path = str((step.get("with") or {}).get("path", ""))
                uploaded_paths.append(path)
        self.assertTrue(uploaded_paths, "expected at least one upload-artifact step")
        for path in uploaded_paths:
            self.assertNotIn(".bin", path, f"dry-run must not upload firmware: {path}")
            self.assertNotIn("firmware", path.lower())
            self.assertIn("log", path.lower(), f"upload must be a log: {path}")

    def test_no_release_or_tag_action(self) -> None:
        for step in self._iter_steps():
            uses = str(step.get("uses", ""))
            self.assertNotIn(
                "action-gh-release", uses, "dry-run must not create a Release"
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)

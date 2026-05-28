#!/usr/bin/env python3
"""RELEASE-WORKFLOW-DRYRUN-MODE-001 regression guard.

Locks in the explicit, safe-by-default dry-run mode added to the room
firmware release workflow (``.github/workflows/firmware-build-release.yml``)
so it cannot silently regress into a publishing path. The invariants:

  * a ``workflow_dispatch`` boolean input ``dry_run`` exists and its default
    is **safe / non-publishing** (``true``);
  * a dedicated ``release-dry-run`` job exists, gated to manual dispatch with
    ``dry_run`` enabled, that runs the release-note planner;
  * the dry-run job is **read-only** (no ``contents: write`` / no write scope)
    and contains **no** publish step (no ``softprops/action-gh-release``) and
    no ``firmware/sources.json`` / ``manifest.json`` write — it cannot publish;
  * the publish job (``release``) stays gated to ``github.event_name ==
    'release'`` and is **not** reachable from ``workflow_dispatch`` /
    ``dry_run`` — i.e. publishing remains gated to a real release event;
  * ``softprops/action-gh-release`` (the only asset-upload action) appears
    **only** inside the ``release`` job;
  * the dry-run mode plans **only** the release-eligible builds in
    ``config/webflash-builds.json`` (stable RoomIQ + preview LED) and
    **excludes** FanRelay / FanPWM / FanDAC.

Run with:

    python3 tests/test_release_dry_run_mode.py
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = (
    REPO_ROOT / ".github" / "workflows" / "firmware-build-release.yml"
)
PLANNER_PATH = REPO_ROOT / "scripts" / "plan_room_release_notes.py"

PUBLISH_ACTION = "softprops/action-gh-release"
DRY_RUN_JOB = "release-dry-run"
PUBLISH_JOB = "release"

STABLE_CONFIG = "Ceiling-POE-VentIQ-RoomIQ"
LED_CONFIG = "Ceiling-POE-VentIQ-RoomIQ-LED"
FAN_TOKENS = ("FanRelay", "FanPWM", "FanDAC")


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _triggers(data: dict) -> dict:
    """Return the workflow's ``on:`` mapping.

    PyYAML parses the bare key ``on:`` as boolean ``True`` (YAML 1.1 truthy
    key), so the trigger block can land under ``"on"`` or ``True``.
    """
    raw = data.get("on")
    if raw is None:
        raw = data.get(True)
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, list):
        return {key: None for key in raw}
    if isinstance(raw, str):
        return {raw: None}
    return {}


def _job_uses(job: dict) -> list[str]:
    refs: list[str] = []
    for step in job.get("steps", []) or []:
        if isinstance(step, dict) and isinstance(step.get("uses"), str):
            refs.append(step["uses"])
    return refs


def _job_run_text(job: dict) -> str:
    chunks: list[str] = []
    for step in job.get("steps", []) or []:
        if isinstance(step, dict) and isinstance(step.get("run"), str):
            chunks.append(step["run"])
    return "\n".join(chunks)


class WorkflowDryRunModeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = WORKFLOW_PATH.read_text(encoding="utf-8")
        cls.data = yaml.safe_load(cls.raw)
        cls.jobs = cls.data.get("jobs") or {}

    # -- input -------------------------------------------------------------

    def test_dry_run_input_exists(self) -> None:
        wd = _triggers(self.data).get("workflow_dispatch") or {}
        inputs = wd.get("inputs") or {}
        self.assertIn(
            "dry_run",
            inputs,
            "workflow_dispatch must declare a 'dry_run' input "
            "(RELEASE-WORKFLOW-DRYRUN-MODE-001)",
        )

    def test_dry_run_default_is_safe_non_publishing(self) -> None:
        wd = _triggers(self.data).get("workflow_dispatch") or {}
        dry_run = (wd.get("inputs") or {}).get("dry_run") or {}
        # Safe default = dry-run ON. YAML 'default: true' parses to Python True.
        self.assertIs(
            dry_run.get("default"),
            True,
            "dry_run default must be the safe, non-publishing value (true)",
        )
        self.assertEqual(
            dry_run.get("type"),
            "boolean",
            "dry_run should be a boolean input",
        )

    # -- dry-run job -------------------------------------------------------

    def test_dry_run_job_exists_and_is_gated(self) -> None:
        self.assertIn(
            DRY_RUN_JOB, self.jobs, f"missing '{DRY_RUN_JOB}' job"
        )
        gate = str(self.jobs[DRY_RUN_JOB].get("if", ""))
        self.assertIn("workflow_dispatch", gate)
        self.assertIn("dry_run", gate)

    def test_dry_run_job_runs_the_planner(self) -> None:
        run_text = _job_run_text(self.jobs[DRY_RUN_JOB])
        self.assertIn(
            "scripts/plan_room_release_notes.py",
            run_text,
            "dry-run job must exercise the release-note planner",
        )

    def test_dry_run_job_is_read_only(self) -> None:
        perms = self.jobs[DRY_RUN_JOB].get("permissions")
        self.assertIsInstance(
            perms, dict, "dry-run job must declare an explicit permissions block"
        )
        for scope, value in perms.items():
            self.assertNotEqual(
                str(value),
                "write",
                f"dry-run job must not grant '{scope}: write' (least privilege)",
            )
        self.assertEqual(str(perms.get("contents")), "read")

    def test_dry_run_job_has_no_publish_step(self) -> None:
        uses = _job_uses(self.jobs[DRY_RUN_JOB])
        for ref in uses:
            self.assertNotIn(
                PUBLISH_ACTION,
                ref,
                "dry-run job must not call the release-publish action",
            )

    def test_dry_run_job_writes_no_release_side_effect_files(self) -> None:
        run_text = _job_run_text(self.jobs[DRY_RUN_JOB])
        # The job may *assert the absence of* these files, so only reject
        # tokens that indicate writing/creating them.
        for forbidden in (
            "> firmware/sources.json",
            "> manifest.json",
            ">> firmware/sources.json",
            ">> manifest.json",
        ):
            self.assertNotIn(
                forbidden,
                run_text,
                f"dry-run job must not write {forbidden!r}",
            )

    # -- publish job remains gated ----------------------------------------

    def test_publish_job_gated_to_release_event(self) -> None:
        self.assertIn(PUBLISH_JOB, self.jobs)
        gate = str(self.jobs[PUBLISH_JOB].get("if", ""))
        self.assertIn(
            "github.event_name == 'release'",
            gate,
            "publish job must remain gated to a real release event",
        )

    def test_publish_job_not_reachable_from_dispatch_or_dry_run(self) -> None:
        gate = str(self.jobs[PUBLISH_JOB].get("if", ""))
        self.assertNotIn(
            "workflow_dispatch",
            gate,
            "publish job must not be reachable from workflow_dispatch",
        )
        self.assertNotIn(
            "dry_run",
            gate,
            "the dry_run input must not be able to enable publishing",
        )

    def test_publish_action_only_in_release_job(self) -> None:
        offenders: list[str] = []
        for job_id, job in self.jobs.items():
            if not isinstance(job, dict):
                continue
            for ref in _job_uses(job):
                if PUBLISH_ACTION in ref and job_id != PUBLISH_JOB:
                    offenders.append(f"{job_id}: {ref}")
        self.assertEqual(
            offenders,
            [],
            f"{PUBLISH_ACTION} must appear only in the '{PUBLISH_JOB}' job; "
            f"found in: {offenders}",
        )


class DryRunScopeTests(unittest.TestCase):
    """The dry-run mode plans only release-eligible builds, excludes fans."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = _load_module("plan_room_release_notes", PLANNER_PATH)

    def test_plans_only_the_two_release_eligible_builds(self) -> None:
        builds = self.plan.build_plan(commit="deadbeef")["builds"]
        configs = {b["config_string"] for b in builds}
        self.assertEqual(configs, {STABLE_CONFIG, LED_CONFIG})

    def test_fans_excluded_from_release_plan(self) -> None:
        builds = self.plan.build_plan(commit="deadbeef")["builds"]
        configs = {b["config_string"] for b in builds}
        for token in FAN_TOKENS:
            self.assertFalse(
                any(token.lower() in c.lower() for c in configs),
                f"{token} must not be a release-eligible (dry-run) build",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)

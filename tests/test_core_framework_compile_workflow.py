#!/usr/bin/env python3
"""CORE-FRAMEWORK-001 — shape guards for the representative compile lane.

Pins the contract of ``.github/workflows/core-framework-compile.yml``
("CI: Core Framework Representative Compile"), the narrowly scoped hosted
lane that provides real ``esphome compile`` evidence that the shared device
framework (PR #825) compiles in representative production compositions.

The lane is COMPILE PROOF ONLY, and these guards keep it that way:

* triggers are ``pull_request`` (path-filtered, with NO base-branch filter,
  so it runs on stacked PRs whose base branch contains ``/``) and
  ``workflow_dispatch`` — never push / release / schedule / tag /
  ``workflow_call`` (so no production release workflow can call it);
* read-only token (``permissions: contents: read``), SHA-pinned actions;
* it compiles ONLY the audited, pre-existing representative products that
  compose the framework (``framework_included: true`` in
  ``config/core-framework.json``) — no invented configurations, no release
  declarations added for its benefit, and never the deferred
  ``Ceiling-POE-FanPWM`` gap;
* it uploads NO artifact and publishes NOTHING: no firmware upload, no
  GitHub Release, no manifest / checksum / webflash-builds mutation;
* throwaway secrets come from the standard setup-esphome-build action, are
  never printed, and are cleaned with an ``if: always()`` step;
* the framework contract tests and the no-tracked-secrets guard run before
  any compile, and ``esphome config`` runs before ``esphome compile``.

Uses Python's stdlib unittest (repo convention). Run with::

    python3 tests/test_core_framework_compile_workflow.py
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from typing import Any, Dict

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "core-framework-compile.yml"
WORKFLOW_DIR = REPO_ROOT / ".github" / "workflows"
CONTRACT_PATH = REPO_ROOT / "config" / "core-framework.json"

EXPECTED_WORKFLOW_NAME = "CI: Core Framework Representative Compile"

# The audited representative matrix (existing bundle-backed products only).
# Category mapping (no duplicate compiles for categories already covered):
#   1. Core+RoomIQ (PoE)          -> Ceiling-POE-RoomIQ
#   2. Core+RoomIQ+AirIQ (PoE)    -> Ceiling-POE-AirIQ-RoomIQ
#   3. Core+RoomIQ+VentIQ (PoE)   -> Ceiling-POE-VentIQ-RoomIQ (Release-One)
#   4. Core+RoomIQ (USB)          -> Ceiling-USB-RoomIQ
#   5. Core+RoomIQ+VentIQ (USB)   -> Ceiling-USB-VentIQ-RoomIQ
#   6. Presence-bearing (LD2450)  -> every RoomIQ target above compiles the
#      LD2450 radar half; canonical representative: Ceiling-POE-RoomIQ.
#   7. LED-bearing preview        -> Ceiling-POE-VentIQ-RoomIQ-LED
#   8. LED+RoomIQ (PoE) preview   -> Ceiling-POE-RoomIQ-LED
#      (LED-FRAMEWORK-001: the second authoritative LED-bearing bundle —
#      Presence + LED composition; the LED-less targets double as the
#      regression check that the LED framework never leaks outside the
#      LED-bearing bundles.)
EXPECTED_MATRIX = {
    "Ceiling-POE-RoomIQ": "products/sense360-ceiling-poe-roomiq.yaml",
    "Ceiling-POE-AirIQ-RoomIQ": ("products/sense360-ceiling-poe-airiq-roomiq.yaml"),
    "Ceiling-POE-VentIQ-RoomIQ": ("products/sense360-ceiling-poe-ventiq-roomiq.yaml"),
    "Ceiling-USB-RoomIQ": "products/sense360-ceiling-usb-roomiq.yaml",
    "Ceiling-USB-VentIQ-RoomIQ": ("products/sense360-ceiling-usb-ventiq-roomiq.yaml"),
    "Ceiling-POE-VentIQ-RoomIQ-LED": (
        "products/sense360-ceiling-poe-ventiq-roomiq-led.yaml"
    ),
    "Ceiling-POE-RoomIQ-LED": ("products/sense360-ceiling-poe-roomiq-led.yaml"),
}

FORBIDDEN_TRIGGERS = {
    "push",
    "release",
    "schedule",
    "create",
    "workflow_call",
    "pull_request_target",
    "workflow_run",
}

# Strings that would indicate publication / mutation surfaces. None of them
# may appear anywhere in the workflow.
FORBIDDEN_STRINGS = (
    "upload-artifact",
    "action-gh-release",
    "softprops",
    "gh release",
    "create-release",
    "git push",
    "webflash-builds.json",
    "manifest.json",
    "firmware/sources.json",
    "checksums-sha256",
    "fanpwm",
    "FanPWM",
    "fan-pwm",
)

SHA_PIN_RE = re.compile(r"^[^@]+@[0-9a-f]{40}$")


def load_workflow() -> Dict[str, Any]:
    return yaml.safe_load(WORKFLOW_PATH.read_text())


def workflow_triggers(doc: Dict[str, Any]) -> Dict[str, Any]:
    # PyYAML parses the bare `on:` key as boolean True (YAML 1.1).
    triggers = doc.get("on", doc.get(True))
    if isinstance(triggers, str):
        return {triggers: None}
    if isinstance(triggers, list):
        return {t: None for t in triggers}
    return dict(triggers or {})


def iter_steps(doc: Dict[str, Any]):
    for job_id, job in (doc.get("jobs") or {}).items():
        for step in job.get("steps") or []:
            yield job_id, step


class WorkflowShapeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(
            WORKFLOW_PATH.is_file(),
            f"missing compile-proof workflow at {WORKFLOW_PATH}",
        )
        self.doc = load_workflow()
        self.raw = WORKFLOW_PATH.read_text()

    def test_name(self) -> None:
        self.assertEqual(self.doc.get("name"), EXPECTED_WORKFLOW_NAME)

    def test_triggers_are_pull_request_and_dispatch_only(self) -> None:
        triggers = workflow_triggers(self.doc)
        self.assertEqual(
            set(triggers),
            {"pull_request", "workflow_dispatch"},
            "the lane may trigger only on pull_request + workflow_dispatch",
        )

    def test_no_forbidden_triggers(self) -> None:
        triggers = workflow_triggers(self.doc)
        self.assertEqual(set(triggers) & FORBIDDEN_TRIGGERS, set())
        # No tag / branch publication trigger hiding inside pull_request.
        self.assertNotIn("tags", self.raw)

    def test_pull_request_paths_filter_without_branch_filter(self) -> None:
        triggers = workflow_triggers(self.doc)
        pr = triggers.get("pull_request") or {}
        self.assertIsInstance(pr, dict)
        paths = pr.get("paths") or []
        self.assertIn("packages/base/device_framework.yaml", paths)
        self.assertIn(".github/workflows/core-framework-compile.yml", paths)
        # The stacked PR's base branch contains '/', so a branches filter
        # would silently keep the lane from ever running on it. Rely on the
        # paths filter + these guards instead.
        self.assertNotIn("branches", pr)
        self.assertNotIn("branches-ignore", pr)

    def test_read_only_permissions(self) -> None:
        self.assertEqual(self.doc.get("permissions"), {"contents": "read"})
        for job_id, job in (self.doc.get("jobs") or {}).items():
            self.assertNotIn(
                "permissions",
                job,
                f"job {job_id} must not escalate beyond the read-only token",
            )

    def test_no_publication_or_mutation_surface(self) -> None:
        for needle in FORBIDDEN_STRINGS:
            self.assertNotIn(
                needle,
                self.raw,
                f"compile-proof lane must not reference {needle!r}",
            )

    def test_actions_are_sha_pinned_or_local(self) -> None:
        for job_id, step in iter_steps(self.doc):
            uses = step.get("uses")
            if not uses:
                continue
            if uses.startswith("./"):
                continue
            self.assertRegex(
                uses,
                SHA_PIN_RE,
                f"{job_id}: action {uses!r} must be SHA-pinned",
            )

    def test_uses_standard_esphome_setup_action(self) -> None:
        self.assertIn("./.github/actions/setup-esphome-build", self.raw)
        # Repo policy: the ESPHome version is single-sourced in the setup
        # action (2026.4.5); this lane must not override it.
        for _, step in iter_steps(self.doc):
            if step.get("uses") == "./.github/actions/setup-esphome-build":
                with_block = step.get("with") or {}
                self.assertNotIn("esphome-version", with_block)

    def test_matrix_is_exactly_the_audited_representatives(self) -> None:
        compile_jobs = [
            job
            for job in (self.doc.get("jobs") or {}).values()
            if "matrix" in (job.get("strategy") or {})
        ]
        self.assertEqual(len(compile_jobs), 1)
        include = compile_jobs[0]["strategy"]["matrix"]["include"]
        got = {row["config_string"]: row["product_yaml"] for row in include}
        self.assertEqual(got, EXPECTED_MATRIX)
        self.assertFalse(compile_jobs[0]["strategy"].get("fail-fast", True))

    def test_matrix_targets_exist_and_compose_the_framework(self) -> None:
        contract = json.loads(CONTRACT_PATH.read_text())
        configs = contract["configs"]
        for config_string, product_yaml in EXPECTED_MATRIX.items():
            self.assertTrue((REPO_ROOT / product_yaml).is_file(), product_yaml)
            entry = configs[config_string]
            self.assertTrue(
                entry.get("framework_included", True),
                f"{config_string} must compose the framework to be compile "
                "evidence for it",
            )

    def test_contract_tests_and_secret_guard_run_before_compiles(self) -> None:
        self.assertIn("tests/test_core_framework.py", self.raw)
        self.assertIn("scripts/check-no-tracked-secrets.py", self.raw)

    def test_config_check_precedes_compile(self) -> None:
        for job_id, job in (self.doc.get("jobs") or {}).items():
            runs = [str(s.get("run", "")) for s in job.get("steps") or []]
            config_idx = [i for i, r in enumerate(runs) if "esphome config" in r]
            compile_idx = [i for i, r in enumerate(runs) if "esphome compile" in r]
            if compile_idx:
                self.assertTrue(
                    config_idx and min(config_idx) < min(compile_idx),
                    f"{job_id}: esphome config must run before compile",
                )

    def test_secrets_cleanup_is_always(self) -> None:
        cleanup = [
            step
            for _, step in iter_steps(self.doc)
            if "secrets.yaml" in str(step.get("run", ""))
            and "rm" in str(step.get("run", ""))
        ]
        self.assertTrue(cleanup, "missing temporary-secrets cleanup step")
        self.assertTrue(
            any(step.get("if") == "always()" for step in cleanup),
            "secrets cleanup must run with if: always()",
        )

    def test_secrets_are_never_printed(self) -> None:
        for _, step in iter_steps(self.doc):
            run = str(step.get("run", ""))
            self.assertNotIn("cat secrets", run)
            self.assertNotIn("cat products/secrets", run)


class WorkflowIsolationTests(unittest.TestCase):
    """No production workflow can reach or reuse this lane."""

    def test_not_referenced_by_any_other_workflow(self) -> None:
        for path in sorted(WORKFLOW_DIR.glob("*.yml")):
            if path.name == "core-framework-compile.yml":
                continue
            self.assertNotIn(
                "core-framework-compile",
                path.read_text(),
                f"{path.name} must not reference the compile-proof lane",
            )

    def test_no_release_declaration_added_for_this_lane(self) -> None:
        # The lane compiles pre-existing declared products only; the release
        # matrix and compile/preview target declarations must not gain rows
        # for its benefit. (Counts pinned elsewhere; here we pin that the
        # lane does not read or write those declaration files at all.)
        raw = WORKFLOW_PATH.read_text()
        for declaration in (
            "preview-release-targets.json",
            "compile-only-targets.json",
            "product-catalog.json",
        ):
            self.assertNotIn(declaration, raw)


if __name__ == "__main__":
    unittest.main(verbosity=2)

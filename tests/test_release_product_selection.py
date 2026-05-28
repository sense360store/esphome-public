#!/usr/bin/env python3
"""RELEASE-PRODUCT-SELECTION-001 contract tests.

Locks in the operator-facing release-target selection added to the
release-notes draft workflow and the firmware build/release workflow so
they cannot silently regress (e.g. by quietly defaulting back to a
single hardcoded product, by accepting an off-catalog free-text value,
or by letting a FanRelay / FanPWM / FanDAC token become selectable for
release).

The invariants:

  * ``release-notes-draft.yml`` exposes ``config_string`` as a
    ``type: choice`` input whose options exactly match the
    release-eligible ``config_string`` values in
    ``config/webflash-builds.json`` — no free-text default that
    silently scopes to one product.
  * ``firmware-build-release.yml`` exposes ``release_target`` as a
    ``type: choice`` input with options =
    ``['all-release-eligible', ...release-eligible config_strings]``,
    defaulting to ``all-release-eligible``.
  * Neither input lists a FanRelay / FanPWM / FanDAC token (those are
    manual-candidate-only).
  * The ``release-dry-run`` job passes the selected ``release_target``
    to ``scripts/plan_room_release_notes.py`` via ``--config-string``.
  * The ``release-dry-run`` job calls
    ``scripts/list_release_targets.py --validate`` so the picker and
    ``config/webflash-builds.json`` can't drift apart silently.
  * Publishing semantics are unchanged — the publish job (``release``)
    stays gated on a real release event and does **not** reference the
    new ``release_target`` input.

Run with::

    python3 tests/test_release_product_selection.py
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
RELEASE_NOTES_WORKFLOW = (
    REPO_ROOT / ".github" / "workflows" / "release-notes-draft.yml"
)
BUILD_RELEASE_WORKFLOW = (
    REPO_ROOT / ".github" / "workflows" / "firmware-build-release.yml"
)
BUILDS_JSON = REPO_ROOT / "config" / "webflash-builds.json"
LIST_TARGETS_SCRIPT = REPO_ROOT / "scripts" / "list_release_targets.py"

FAN_TOKENS = ("FanRelay", "FanPWM", "FanDAC")
ALL_TARGETS_SENTINEL = "all-release-eligible"
PUBLISH_JOB = "release"
DRY_RUN_JOB = "release-dry-run"
MATRIX_JOB = "generate-matrix"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _triggers(data: dict) -> dict:
    # PyYAML parses bare key ``on:`` as boolean True (YAML 1.1 truthy key).
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


def _release_eligible_config_strings() -> list[str]:
    doc = json.loads(BUILDS_JSON.read_text(encoding="utf-8"))
    return [
        e["config_string"]
        for e in doc.get("builds", [])
        if isinstance(e, dict) and isinstance(e.get("config_string"), str)
    ]


def _job_run_text(job: dict) -> str:
    chunks: list[str] = []
    for step in job.get("steps", []) or []:
        if isinstance(step, dict) and isinstance(step.get("run"), str):
            chunks.append(step["run"])
    return "\n".join(chunks)


class ReleaseNotesDraftPickerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = yaml.safe_load(RELEASE_NOTES_WORKFLOW.read_text(encoding="utf-8"))
        wd = _triggers(cls.data).get("workflow_dispatch") or {}
        cls.inputs = wd.get("inputs") or {}

    def test_config_string_is_type_choice(self) -> None:
        cs = self.inputs.get("config_string") or {}
        self.assertEqual(
            cs.get("type"),
            "choice",
            "release-notes-draft.yml config_string must be a `type: choice` "
            "picker (RELEASE-PRODUCT-SELECTION-001) so the operator picks "
            "from the canonical release-eligible list rather than typing a "
            "free-text product name",
        )

    def test_config_string_options_match_release_matrix(self) -> None:
        cs = self.inputs.get("config_string") or {}
        options = list(cs.get("options") or [])
        expected = _release_eligible_config_strings()
        self.assertEqual(
            set(options),
            set(expected),
            f"release-notes-draft.yml config_string options {options!r} "
            f"must equal config/webflash-builds.json config_strings "
            f"{expected!r} (add the new release-eligible target to BOTH "
            "the workflow picker and the release matrix)",
        )

    def test_config_string_options_exclude_fan_tokens(self) -> None:
        options = list((self.inputs.get("config_string") or {}).get("options") or [])
        for token in FAN_TOKENS:
            self.assertFalse(
                any(token.lower() in str(opt).lower() for opt in options),
                f"release-notes-draft.yml config_string options must not "
                f"include {token} (manual-candidate-only)",
            )

    def test_config_string_does_not_silently_default_to_one_product(self) -> None:
        # The picker has no `default:` — operator must select. This prevents
        # a silent default-scoped run that only documents stable RoomIQ.
        cs = self.inputs.get("config_string") or {}
        self.assertNotIn(
            "default",
            cs,
            "release-notes-draft.yml config_string must NOT declare a "
            "`default:`; forcing operator selection prevents the workflow "
            "from silently scoping every dispatch to a single product "
            "(RELEASE-PRODUCT-SELECTION-001)",
        )


class FirmwareBuildReleasePickerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = yaml.safe_load(BUILD_RELEASE_WORKFLOW.read_text(encoding="utf-8"))
        wd = _triggers(cls.data).get("workflow_dispatch") or {}
        cls.inputs = wd.get("inputs") or {}
        cls.jobs = cls.data.get("jobs") or {}

    def test_release_target_input_exists_as_choice(self) -> None:
        rt = self.inputs.get("release_target") or {}
        self.assertEqual(
            rt.get("type"),
            "choice",
            "firmware-build-release.yml must declare `release_target` as a "
            "`type: choice` picker (RELEASE-PRODUCT-SELECTION-001)",
        )

    def test_release_target_default_is_all_release_eligible(self) -> None:
        rt = self.inputs.get("release_target") or {}
        self.assertEqual(
            rt.get("default"),
            ALL_TARGETS_SENTINEL,
            "release_target must default to 'all-release-eligible' so a "
            "default dispatch covers every release-eligible build",
        )

    def test_release_target_options_include_all_and_each_target(self) -> None:
        rt = self.inputs.get("release_target") or {}
        options = list(rt.get("options") or [])
        expected = [ALL_TARGETS_SENTINEL] + _release_eligible_config_strings()
        self.assertEqual(
            set(options),
            set(expected),
            f"release_target options {options!r} must equal "
            f"['all-release-eligible'] + config/webflash-builds.json "
            f"config_strings {expected!r}",
        )

    def test_release_target_options_exclude_fan_tokens(self) -> None:
        options = list((self.inputs.get("release_target") or {}).get("options") or [])
        for token in FAN_TOKENS:
            self.assertFalse(
                any(token.lower() in str(opt).lower() for opt in options),
                f"release_target options must not include {token} "
                "(manual-candidate-only; never release-eligible)",
            )

    def test_dry_run_job_validates_release_target(self) -> None:
        job = self.jobs.get(DRY_RUN_JOB) or {}
        run_text = _job_run_text(job)
        self.assertIn(
            "scripts/list_release_targets.py",
            run_text,
            "release-dry-run job must call list_release_targets.py --validate "
            "to fail-closed if release_target and config/webflash-builds.json "
            "ever drift apart",
        )
        self.assertIn("--validate", run_text)

    def test_dry_run_job_passes_release_target_to_planner(self) -> None:
        job = self.jobs.get(DRY_RUN_JOB) or {}
        run_text = _job_run_text(job)
        self.assertIn(
            "--config-string",
            run_text,
            "release-dry-run job must pass --config-string to "
            "plan_room_release_notes.py so the operator's release_target "
            "scopes the dry-run plan",
        )
        # The env var the dry-run job uses must carry the selection.
        # Either the literal env-var reference or the input expression is fine.
        for step in job.get("steps", []) or []:
            if not isinstance(step, dict):
                continue
            env = step.get("env") or {}
            if env.get("RELEASE_TARGET") is not None:
                self.assertIn(
                    "inputs.release_target",
                    str(env["RELEASE_TARGET"]),
                    "release-dry-run job's RELEASE_TARGET env var must "
                    "reference inputs.release_target",
                )

    def test_publish_job_does_not_reference_release_target(self) -> None:
        publish = self.jobs.get(PUBLISH_JOB) or {}
        gate = str(publish.get("if", ""))
        self.assertNotIn(
            "release_target",
            gate,
            "publish job gate must not reference release_target; publishing "
            "stays gated to a real release event",
        )

    def test_matrix_job_filters_on_release_target_in_dispatch(self) -> None:
        # The generate-matrix job (which only runs on release / non-dry-run
        # dispatch) must honor release_target so a manual dispatch with a
        # specific target builds only that target.
        job = self.jobs.get(MATRIX_JOB) or {}
        run_text = _job_run_text(job)
        self.assertIn(
            "RELEASE_TARGET",
            run_text,
            "generate-matrix must honor the release_target input on "
            "workflow_dispatch (RELEASE-PRODUCT-SELECTION-001)",
        )


class PlannerSelectionTests(unittest.TestCase):
    """RELEASE-PRODUCT-SELECTION-001 planner-level scoping contract."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = _load_module(
            "plan_room_release_notes",
            REPO_ROOT / "scripts" / "plan_room_release_notes.py",
        )

    def test_planner_scope_defaults_to_all(self) -> None:
        builds = self.plan.build_plan(commit="deadbeef")["builds"]
        configs = {b["config_string"] for b in builds}
        self.assertEqual(
            configs,
            set(_release_eligible_config_strings()),
            "default plan must cover every release-eligible build",
        )

    def test_planner_scope_filters_to_single_config(self) -> None:
        target = "Ceiling-POE-VentIQ-RoomIQ"
        builds = self.plan.build_plan(
            commit="deadbeef", config_string=target
        )["builds"]
        configs = {b["config_string"] for b in builds}
        self.assertEqual(configs, {target})

    def test_planner_scope_filters_to_led_preview(self) -> None:
        target = "Ceiling-POE-VentIQ-RoomIQ-LED"
        builds = self.plan.build_plan(
            commit="deadbeef", config_string=target
        )["builds"]
        configs = {b["config_string"] for b in builds}
        self.assertEqual(configs, {target})

    def test_planner_all_release_eligible_sentinel_is_equivalent(self) -> None:
        a = self.plan.build_plan(commit="deadbeef")["builds"]
        b = self.plan.build_plan(
            commit="deadbeef", config_string="all-release-eligible"
        )["builds"]
        self.assertEqual(
            {x["config_string"] for x in a},
            {x["config_string"] for x in b},
        )

    def test_planner_rejects_unknown_config_string(self) -> None:
        with self.assertRaises(self.plan.PlanError) as ctx:
            self.plan.build_plan(
                commit="deadbeef", config_string="Not-A-Real"
            )
        msg = str(ctx.exception)
        self.assertIn("not a release-eligible", msg)
        # Error must enumerate the legitimate alternatives.
        for cfg in _release_eligible_config_strings():
            self.assertIn(cfg, msg)

    def test_planner_rejects_fan_family_token(self) -> None:
        for token in FAN_TOKENS:
            with self.assertRaises(self.plan.PlanError):
                self.plan.build_plan(
                    commit="deadbeef",
                    config_string=f"Ceiling-POE-VentIQ-{token}-RoomIQ",
                )


class GeneratorProductAwareLedTests(unittest.TestCase):
    """RELEASE-PRODUCT-SELECTION-001: the stale 'Release-One firmware' wording
    in the LED Known-Issues bullet is replaced by product-aware text."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.gen = _load_module(
            "generate_webflash_release_notes",
            REPO_ROOT / "scripts" / "generate_webflash_release_notes.py",
        )

    def test_led_known_issue_does_not_mention_release_one(self) -> None:
        body = self.gen.generate(
            config_string="Ceiling-POE-VentIQ-RoomIQ",
            version="1.0.0",
            channel="stable",
        )
        # The LED exclusion bullet appears under ## Known Issues. The full
        # body should no longer carry the stale 'Release-One firmware' phrasing.
        self.assertNotIn(
            "Release-One firmware",
            body,
            "generator must not emit hardcoded 'Release-One firmware' text "
            "in the LED Known-Issues bullet (RELEASE-PRODUCT-SELECTION-001)",
        )

    def test_led_known_issue_names_selected_config(self) -> None:
        body = self.gen.generate(
            config_string="Ceiling-POE-VentIQ-RoomIQ",
            version="1.0.0",
            channel="stable",
        )
        # The LED bullet should make it clear *this selected config* does
        # not include LED, rather than implying LED was forgotten or that
        # there is only one fixed product in the universe.
        self.assertIn("Ceiling-POE-VentIQ-RoomIQ", body)
        self.assertIn("does not include LED", body)

    def test_changelog_placeholder_is_product_aware(self) -> None:
        body = self.gen.generate(
            config_string="Ceiling-POE-VentIQ-RoomIQ-LED",
            version="1.0.0",
            channel="preview",
        )
        # The placeholder must name the selected config + version so a
        # multi-product draft can't be mistaken for the wrong product.
        self.assertIn("Ceiling-POE-VentIQ-RoomIQ-LED", body)
        self.assertIn("v1.0.0", body)
        # It must be unmistakable as a placeholder requiring operator action.
        lowered = body.lower()
        self.assertIn("todo", lowered)
        self.assertIn("operator", lowered)

    def test_led_preview_body_mentions_led_and_preview(self) -> None:
        body = self.gen.generate(
            config_string="Ceiling-POE-VentIQ-RoomIQ-LED",
            version="1.0.0",
            channel="preview",
        )
        # For the LED preview, ## Features should call out the LED ring and
        # the preview channel framing.
        self.assertIn("LED", body)
        self.assertIn("preview", body.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)

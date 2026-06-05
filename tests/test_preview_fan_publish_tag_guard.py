#!/usr/bin/env python3
"""Regression guard for the manual-preview fan release-tag confirm-gate.

RELEASE-PREVIEW-FAN-PUBLISH-TAG-GUARD-001.

This complements RELEASE-PREVIEW-FAN-SHARED-TAG-001 (which adopted the shared
``v1.0.0-preview`` preview release as the single vehicle for every preview
artifact). It does NOT reintroduce a dedicated fan tag. Instead it hardens the
publish workflow so the shared release stays the frictionless default and any
OTHER release tag must be explicitly confirmed — catching an accidental dispatch
to the wrong tag (a typo, the stable release, or a stray new release) before any
build runs. This guard locks the invariants:

  * ``_validate_release_tag`` accepts the shared ``v1.0.0-preview`` with no
    confirmation, and rejects any other tag unless ``confirm_override`` is set;
  * the workflow keeps the shared tag as the default (it does NOT default to the
    retired dedicated tag) and fails fast via a "Guard release tag" step;
  * the shared-tag model is respected — the retired dedicated tag is treated as a
    plain non-shared tag (allowed only with confirmation), not as a special /
    reserved vehicle;
  * the WebFlash build matrix still carries no fan / TRIAC row; and
  * TRIAC remains excluded (``HW-005``).

Run with::

    python3 tests/test_preview_fan_publish_tag_guard.py
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import re
import unittest
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "validate_manual_preview_fan_publish.py"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "manual-preview-fan-publish.yml"
WEBFLASH_BUILDS = REPO_ROOT / "config" / "webflash-builds.json"
PLAN_DOC = REPO_ROOT / "docs" / "release-preview-fan-publish-plan.md"
WORKFLOW_DOC = REPO_ROOT / "docs" / "release-preview-fan-publish-workflow.md"
UPCOMING_PR = REPO_ROOT / "UPCOMING_PR.md"

TAG_GUARD_ID = "RELEASE-PREVIEW-FAN-PUBLISH-TAG-GUARD-001"
SHARED_TAG = "v1.0.0-preview"
RETIRED_DEDICATED_TAG = "v1.0.0-manual-preview-fans"
STABLE_TAG = "v1.0.0"

FAN_CONFIGS = (
    "Ceiling-POE-VentIQ-FanRelay-RoomIQ",
    "Ceiling-POE-FanPWM",
    "Ceiling-POE-FanDAC",
)
TRIAC_CONFIG = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"

BIN_TOKEN_RE = re.compile(r"Sense360-[A-Za-z0-9.\-]+\.bin")


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


_SCRIPT = _load_module("validate_manual_preview_fan_publish_tag_guard", SCRIPT_PATH)


def _run_main(argv: List[str]) -> int:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        return _SCRIPT.main(argv)


def _docs() -> tuple:
    return (
        _SCRIPT._load_json(_SCRIPT.LEDGER_PATH),
        _SCRIPT._load_json(_SCRIPT.MANUAL_PATH),
        _SCRIPT._load_json(_SCRIPT.WEBFLASH_BUILDS_PATH),
    )


def _webflash_config_strings() -> set[str]:
    builds = json.loads(WEBFLASH_BUILDS.read_text(encoding="utf-8"))["builds"]
    return {b["config_string"] for b in builds}


class TagGuardConstantsTests(unittest.TestCase):
    def test_shared_tag_is_the_default(self) -> None:
        self.assertEqual(_SCRIPT.EXPECTED_RELEASE_TAG, SHARED_TAG)
        self.assertEqual(_SCRIPT.SHARED_PREVIEW_RELEASE_TAG, SHARED_TAG)

    def test_canonical_id_present(self) -> None:
        self.assertEqual(_SCRIPT.TAG_GUARD_ID, TAG_GUARD_ID)


class ValidateReleaseTagTests(unittest.TestCase):
    """Shared tag is frictionless; any other tag needs confirmation."""

    def test_shared_tag_accepted_without_confirmation(self) -> None:
        self.assertEqual(_SCRIPT._validate_release_tag(SHARED_TAG), [])

    def test_shared_tag_accepted_with_confirmation_too(self) -> None:
        self.assertEqual(
            _SCRIPT._validate_release_tag(SHARED_TAG, confirm_override=True), []
        )

    def test_non_shared_tag_requires_confirmation(self) -> None:
        errors = _SCRIPT._validate_release_tag(RETIRED_DEDICATED_TAG)
        self.assertTrue(errors)
        joined = " ".join(errors).lower()
        self.assertIn("shared preview release", joined)
        self.assertIn("confirm_tag_override", joined)
        self.assertEqual(
            _SCRIPT._validate_release_tag(
                RETIRED_DEDICATED_TAG, confirm_override=True
            ),
            [],
        )

    def test_stable_tag_typo_requires_confirmation(self) -> None:
        # An accidental stable-release tag is caught unless deliberately confirmed.
        self.assertTrue(_SCRIPT._validate_release_tag(STABLE_TAG))
        self.assertEqual(
            _SCRIPT._validate_release_tag(STABLE_TAG, confirm_override=True), []
        )

    def test_empty_tag_is_rejected(self) -> None:
        self.assertTrue(_SCRIPT._validate_release_tag(""))

    def test_is_truthy(self) -> None:
        for value in ("true", "True", "1", "yes", "on"):
            self.assertTrue(_SCRIPT._is_truthy(value))
        for value in ("false", "False", "0", "no", "", "off", None):
            self.assertFalse(_SCRIPT._is_truthy(value))


class SharedTagModelRespectedTests(unittest.TestCase):
    """The retired dedicated tag is NOT resurrected as a special vehicle."""

    def test_dedicated_tag_is_just_a_non_shared_tag(self) -> None:
        # It is neither the default nor a reserved/blocked tag — it is allowed
        # with confirmation like any other non-shared tag.
        self.assertNotEqual(_SCRIPT.EXPECTED_RELEASE_TAG, RETIRED_DEDICATED_TAG)
        self.assertEqual(
            _SCRIPT._validate_release_tag(
                RETIRED_DEDICATED_TAG, confirm_override=True
            ),
            [],
        )

    def test_shared_tag_never_needs_an_override(self) -> None:
        self.assertEqual(_SCRIPT._validate_release_tag(SHARED_TAG), [])


class MainCliTagGuardTests(unittest.TestCase):
    def test_validate_release_tag_accepts_shared(self) -> None:
        self.assertEqual(
            _run_main(["--validate-release-tag", "--release-tag", SHARED_TAG]), 0
        )

    def test_validate_release_tag_rejects_non_shared_without_confirm(self) -> None:
        self.assertEqual(
            _run_main(
                ["--validate-release-tag", "--release-tag", RETIRED_DEDICATED_TAG]
            ),
            1,
        )

    def test_validate_release_tag_accepts_non_shared_with_confirm(self) -> None:
        self.assertEqual(
            _run_main(
                [
                    "--validate-release-tag",
                    "--release-tag",
                    RETIRED_DEDICATED_TAG,
                    "--confirm-tag-override",
                    "true",
                ]
            ),
            0,
        )

    def test_metadata_only_default_tag_passes(self) -> None:
        self.assertEqual(_run_main(["--metadata-only"]), 0)

    def test_metadata_only_rejects_unconfirmed_non_shared_tag(self) -> None:
        # Defense in depth: the bad tag fails even the metadata mode.
        self.assertEqual(
            _run_main(["--metadata-only", "--release-tag", "v2.0.0-preview"]), 1
        )

    def test_release_body_rejects_unconfirmed_non_shared_tag(self) -> None:
        self.assertEqual(
            _run_main(["--release-body", "--release-tag", STABLE_TAG]), 1
        )


class WorkflowShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_default_release_tag_is_shared(self) -> None:
        self.assertRegex(
            self.text,
            rf'release_tag:\n(?:[^\n]*\n)*?\s+default: "{re.escape(SHARED_TAG)}"',
        )

    def test_default_is_not_the_retired_dedicated_tag(self) -> None:
        self.assertNotIn(f'default: "{RETIRED_DEDICATED_TAG}"', self.text)

    def test_confirm_tag_override_input_present(self) -> None:
        self.assertRegex(
            self.text,
            r"confirm_tag_override:\n(?:[^\n]*\n)*?\s+default: false\n"
            r"\s+type: boolean",
        )

    def test_guard_release_tag_step_present(self) -> None:
        self.assertIn("Guard release tag", self.text)
        self.assertIn("--validate-release-tag", self.text)

    def test_guard_step_passes_tag_and_override_inputs(self) -> None:
        self.assertIn('--release-tag "${{ inputs.release_tag }}"', self.text)
        self.assertIn(
            '--confirm-tag-override "${{ inputs.confirm_tag_override }}"', self.text
        )

    def test_workflow_names_the_tag_guard_id(self) -> None:
        self.assertIn(TAG_GUARD_ID, self.text)


class WebFlashSourceOfTruthTests(unittest.TestCase):
    def test_fan_and_triac_configs_never_in_webflash_builds(self) -> None:
        config_strings = _webflash_config_strings()
        for cs in FAN_CONFIGS + (TRIAC_CONFIG,):
            with self.subTest(config_string=cs):
                self.assertNotIn(cs, config_strings)

    def test_no_fan_token_in_webflash_builds(self) -> None:
        config_strings = _webflash_config_strings()
        for cs in config_strings:
            for token in ("FanRelay", "FanPWM", "FanDAC", "FanTRIAC"):
                with self.subTest(config_string=cs, token=token):
                    self.assertNotIn(token.lower(), cs.lower())


class TriacExcludedTests(unittest.TestCase):
    def test_triac_selection_fails_closed(self) -> None:
        # TRIAC is buildable after TRIAC-UNBLOCK-BUILD-001, but it stays on the
        # advanced-manual-preview lane and must NOT be published by this
        # manual-preview fan publish workflow (publish is the separate
        # TRIAC-PUBLISH-ADVANCED-PREVIEW-001 follow-up).
        rows, errors = _SCRIPT._select_rows(
            *_docs(), version="1.0.0", release_target=TRIAC_CONFIG
        )
        self.assertEqual(rows, [])
        self.assertTrue(any("advanced-manual-preview" in e for e in errors))

    def test_default_matrix_contains_no_triac(self) -> None:
        rows, errors = _SCRIPT._select_rows(*_docs(), version="1.0.0")
        self.assertEqual(errors, [])
        for row in rows:
            self.assertNotIn("TRIAC", row["config_string"])

    def test_release_body_excludes_triac_bin_and_notes_advanced_lane(self) -> None:
        rows, errors = _SCRIPT._select_rows(*_docs(), version="1.0.0")
        self.assertEqual(errors, [])
        body = _SCRIPT._release_body(rows, version="1.0.0", release_tag=SHARED_TAG)
        for token in BIN_TOKEN_RE.findall(body):
            self.assertNotIn("triac", token.lower())
        self.assertIn("advanced-manual-preview", body)
        self.assertIn("COMPLIANCE-001", body)


class DocsAndQueueTests(unittest.TestCase):
    def test_workflow_doc_records_the_confirm_gate(self) -> None:
        text = WORKFLOW_DOC.read_text(encoding="utf-8")
        self.assertIn(TAG_GUARD_ID, text)
        self.assertIn("confirm", text.lower())

    def test_plan_doc_records_the_tag_guard(self) -> None:
        self.assertIn(TAG_GUARD_ID, PLAN_DOC.read_text(encoding="utf-8"))

    def test_upcoming_pr_marks_tag_guard_done(self) -> None:
        text = UPCOMING_PR.read_text(encoding="utf-8")
        guard_lines = [ln for ln in text.splitlines() if TAG_GUARD_ID in ln]
        self.assertTrue(guard_lines, f"{TAG_GUARD_ID} not found in UPCOMING_PR.md")
        self.assertTrue(
            any("DONE" in ln for ln in guard_lines),
            f"{TAG_GUARD_ID} is not marked DONE in any heading/line",
        )


class HardGuardrailTests(unittest.TestCase):
    def test_no_manifest_or_sources_committed(self) -> None:
        self.assertFalse((REPO_ROOT / "manifest.json").exists())
        self.assertFalse((REPO_ROOT / "firmware" / "sources.json").exists())

    def test_no_bin_committed_anywhere_in_repo(self) -> None:
        bins = [p for p in REPO_ROOT.rglob("*.bin") if ".git" not in p.parts]
        self.assertEqual(bins, [], f"no .bin may be committed; found {bins}")

    def test_no_fan_or_triac_row_in_webflash_builds(self) -> None:
        config_strings = _webflash_config_strings()
        for cs in FAN_CONFIGS + (TRIAC_CONFIG,):
            self.assertNotIn(cs, config_strings)


if __name__ == "__main__":
    unittest.main(verbosity=2)

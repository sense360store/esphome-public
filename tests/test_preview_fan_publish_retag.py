#!/usr/bin/env python3
"""Regression guard for the manual-preview fan release-tag isolation.

RELEASE-PREVIEW-FAN-PUBLISH-RETAG-001.

``RELEASE-PREVIEW-FAN-PUBLISH-RUN-001`` (run ``26878032103``) was dispatched with
``release_tag=v1.0.0-preview`` — the WebFlash room preview release tag — which
overwrote that release's name / body / checksums and co-mingled the three fan
``.bin`` with the four room-bundle preview ``.bin``. This PR isolates the fan
release tag so the deviation cannot recur, and records the formal decision for the
already-completed run. This guard locks the invariants:

  * the validator rejects ``v1.0.0-preview`` (and every reserved WebFlash
    room/preview tag) unconditionally, accepts the dedicated default
    ``v1.0.0-manual-preview-fans``, and requires ``confirm_tag_override`` (plus the
    ``manual-preview-fans`` marker) for any other tag (task items 3 / 5);
  * the publish workflow defaults to ``v1.0.0-manual-preview-fans`` and fails fast
    via a dedicated "Guard release tag" step (task items 3 / 5);
  * fan artifacts are NOT expected to co-mingle with the room preview artifacts —
    the expected output set is exactly the three fan ``-preview.bin`` and a
    room-preview ``.bin`` is rejected as unexpected (task item 5);
  * the WebFlash room preview release stays the source of truth for the room
    preview import — the four room preview configs live in
    ``config/webflash-builds.json`` and the fan / TRIAC configs never do (task
    item 5);
  * TRIAC remains excluded (``HW-005``) (task item 5);
  * the docs (results §4.1 / plan §3.4-§6 / workflow doc) and ``UPCOMING_PR.md``
    record the decision (task items 4 / 5); and
  * the hard guardrails hold — no ``.bin`` / ``manifest.json`` /
    ``firmware/sources.json`` is committed, and no fan / TRIAC row enters
    ``config/webflash-builds.json``.

Uses Python's stdlib unittest (matching the no-pytest convention of the other
validators in this repo). Run with::

    python3 tests/test_preview_fan_publish_retag.py
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import re
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "validate_manual_preview_fan_publish.py"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "manual-preview-fan-publish.yml"
WEBFLASH_BUILDS = REPO_ROOT / "config" / "webflash-builds.json"
RESULTS_DOC = REPO_ROOT / "docs" / "release-preview-fan-publish-results.md"
PLAN_DOC = REPO_ROOT / "docs" / "release-preview-fan-publish-plan.md"
WORKFLOW_DOC = REPO_ROOT / "docs" / "release-preview-fan-publish-workflow.md"
UPCOMING_PR = REPO_ROOT / "UPCOMING_PR.md"

RETAG_ID = "RELEASE-PREVIEW-FAN-PUBLISH-RETAG-001"
DEDICATED_TAG = "v1.0.0-manual-preview-fans"
WEBFLASH_PREVIEW_TAG = "v1.0.0-preview"
WEBFLASH_LED_PREVIEW_TAG = "v1.0.0-led-preview"

FAN_CONFIGS = (
    "Ceiling-POE-VentIQ-FanRelay-RoomIQ",
    "Ceiling-POE-FanPWM",
    "Ceiling-POE-FanDAC",
)
TRIAC_CONFIG = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"

# The four room-bundle preview configs that co-mingle on v1.0.0-preview — and the
# stable Bathroom build — are the WebFlash room preview / release import surface.
ROOM_PREVIEW_CONFIGS = (
    "Ceiling-POE-AirIQ-RoomIQ",
    "Ceiling-POE-RoomIQ",
    "Ceiling-POE-RoomIQ-LED",
    "Ceiling-POE-VentIQ-RoomIQ-LED",
)
STABLE_CONFIG = "Ceiling-POE-VentIQ-RoomIQ"

ROOM_PREVIEW_ARTIFACTS = {
    f"Sense360-{cs}-v1.0.0-preview.bin" for cs in ROOM_PREVIEW_CONFIGS
}
FAN_ARTIFACTS = {f"Sense360-{cs}-v1.0.0-preview.bin" for cs in FAN_CONFIGS}


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


_SCRIPT = _load_module("validate_manual_preview_fan_publish_retag", SCRIPT_PATH)


def _run_main(argv: List[str]) -> int:
    """Invoke the validator's main() swallowing its stdout/stderr."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        return _SCRIPT.main(argv)


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _webflash_config_strings() -> set[str]:
    return {b["config_string"] for b in _load_json(WEBFLASH_BUILDS)["builds"]}


def _webflash_builds_by_cs() -> Dict[str, Dict[str, Any]]:
    return {b["config_string"]: b for b in _load_json(WEBFLASH_BUILDS)["builds"]}


def _docs() -> tuple:
    return (
        _SCRIPT._load_json(_SCRIPT.LEDGER_PATH),
        _SCRIPT._load_json(_SCRIPT.MANUAL_PATH),
        _SCRIPT._load_json(_SCRIPT.WEBFLASH_BUILDS_PATH),
    )


BIN_TOKEN_RE = re.compile(r"Sense360-[A-Za-z0-9.\-]+\.bin")


class TagPolicyConstantsTests(unittest.TestCase):
    """The validator pins the dedicated tag and the reserved WebFlash tags."""

    def test_dedicated_default_tag(self) -> None:
        self.assertEqual(_SCRIPT.EXPECTED_RELEASE_TAG, DEDICATED_TAG)

    def test_reserved_set_includes_webflash_preview_tags(self) -> None:
        self.assertIn(WEBFLASH_PREVIEW_TAG, _SCRIPT.RESERVED_WEBFLASH_RELEASE_TAGS)
        self.assertIn(
            WEBFLASH_LED_PREVIEW_TAG, _SCRIPT.RESERVED_WEBFLASH_RELEASE_TAGS
        )

    def test_dedicated_tag_is_not_reserved(self) -> None:
        self.assertNotIn(DEDICATED_TAG, _SCRIPT.RESERVED_WEBFLASH_RELEASE_TAGS)

    def test_marker_present_in_dedicated_tag(self) -> None:
        self.assertIn(_SCRIPT.MANUAL_PREVIEW_FANS_MARKER, DEDICATED_TAG)


class ValidateReleaseTagTests(unittest.TestCase):
    """Unit behaviour of ``_validate_release_tag`` (task items 3 / 5)."""

    def test_dedicated_default_is_accepted(self) -> None:
        self.assertEqual(_SCRIPT._validate_release_tag(DEDICATED_TAG), [])

    def test_webflash_preview_tag_is_rejected(self) -> None:
        errors = _SCRIPT._validate_release_tag(WEBFLASH_PREVIEW_TAG)
        self.assertTrue(errors)
        joined = " ".join(errors).lower()
        self.assertIn("reserved", joined)
        self.assertIn("webflash", joined)

    def test_webflash_preview_tag_rejected_even_with_override(self) -> None:
        # Reserved tags are rejected unconditionally — the override cannot bypass.
        errors = _SCRIPT._validate_release_tag(
            WEBFLASH_PREVIEW_TAG, confirm_override=True
        )
        self.assertTrue(errors)

    def test_led_preview_tag_is_rejected(self) -> None:
        self.assertTrue(_SCRIPT._validate_release_tag(WEBFLASH_LED_PREVIEW_TAG))

    def test_non_default_tag_requires_confirmation(self) -> None:
        future = "v1.1.0-manual-preview-fans"
        self.assertTrue(_SCRIPT._validate_release_tag(future))
        self.assertEqual(
            _SCRIPT._validate_release_tag(future, confirm_override=True), []
        )

    def test_override_must_stay_on_dedicated_vehicle(self) -> None:
        # A confirmed override without the marker is still rejected.
        errors = _SCRIPT._validate_release_tag("v1.0.0-stable", confirm_override=True)
        self.assertTrue(errors)
        self.assertIn(
            _SCRIPT.MANUAL_PREVIEW_FANS_MARKER, " ".join(errors)
        )

    def test_empty_tag_is_rejected(self) -> None:
        self.assertTrue(_SCRIPT._validate_release_tag(""))

    def test_is_truthy(self) -> None:
        for value in ("true", "True", "1", "yes", "on"):
            self.assertTrue(_SCRIPT._is_truthy(value))
        for value in ("false", "False", "0", "no", "", "off", None):
            self.assertFalse(_SCRIPT._is_truthy(value))


class MainCliTagGuardTests(unittest.TestCase):
    """``main()`` enforces the tag guard in every mode (task items 3 / 5)."""

    def test_validate_release_tag_accepts_dedicated(self) -> None:
        self.assertEqual(
            _run_main(["--validate-release-tag", "--release-tag", DEDICATED_TAG]), 0
        )

    def test_validate_release_tag_rejects_webflash_preview(self) -> None:
        self.assertEqual(
            _run_main(
                ["--validate-release-tag", "--release-tag", WEBFLASH_PREVIEW_TAG]
            ),
            1,
        )

    def test_validate_release_tag_rejects_webflash_preview_with_override(self) -> None:
        self.assertEqual(
            _run_main(
                [
                    "--validate-release-tag",
                    "--release-tag",
                    WEBFLASH_PREVIEW_TAG,
                    "--confirm-tag-override",
                    "true",
                ]
            ),
            1,
        )

    def test_metadata_only_default_tag_passes(self) -> None:
        self.assertEqual(_run_main(["--metadata-only"]), 0)

    def test_metadata_only_rejects_webflash_preview_tag(self) -> None:
        # Defense in depth: the bad tag fails even the metadata mode.
        self.assertEqual(
            _run_main(["--metadata-only", "--release-tag", WEBFLASH_PREVIEW_TAG]), 1
        )

    def test_release_body_rejects_webflash_preview_tag(self) -> None:
        self.assertEqual(
            _run_main(["--release-body", "--release-tag", WEBFLASH_PREVIEW_TAG]), 1
        )


class WorkflowTagGuardShapeTests(unittest.TestCase):
    """The workflow defaults to the dedicated tag and guards it (task item 3/5)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_default_release_tag_is_dedicated(self) -> None:
        self.assertRegex(
            self.text,
            rf'release_tag:\n(?:[^\n]*\n)*?\s+default: "{re.escape(DEDICATED_TAG)}"',
        )

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

    def test_workflow_names_the_retag_canonical_id(self) -> None:
        self.assertIn(RETAG_ID, self.text)


class NoCoMingleTests(unittest.TestCase):
    """Fan artifacts are NOT expected to co-mingle with room preview (item 5)."""

    def test_expected_output_is_only_the_three_fan_bins(self) -> None:
        rows, errors = _SCRIPT._select_rows(*_docs(), version="1.0.0")
        self.assertEqual(errors, [])
        expected = {row["expected_preview_artifact_name"] for row in rows}
        self.assertEqual(expected, FAN_ARTIFACTS)
        # The fan publish set and the room preview set are disjoint.
        self.assertEqual(expected & ROOM_PREVIEW_ARTIFACTS, set())

    def test_room_preview_bin_is_rejected_as_unexpected(self) -> None:
        rows, errors = _SCRIPT._select_rows(*_docs(), version="1.0.0")
        self.assertEqual(errors, [])
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            for artifact in FAN_ARTIFACTS:
                (tmp_path / artifact).write_bytes(b"x" * 102400)
            # A clean fan-only output set validates.
            self.assertEqual(_SCRIPT._validate_output_dir(rows, tmp_path), [])
            # Adding a room preview .bin makes it co-mingle → rejected as extra.
            room_bin = "Sense360-Ceiling-POE-RoomIQ-v1.0.0-preview.bin"
            (tmp_path / room_bin).write_bytes(b"x" * 102400)
            out_errors = _SCRIPT._validate_output_dir(rows, tmp_path)
            self.assertTrue(out_errors)
            self.assertTrue(any(room_bin in e for e in out_errors))

    def test_fan_tag_is_disjoint_from_webflash_room_preview_tag(self) -> None:
        self.assertNotEqual(_SCRIPT.EXPECTED_RELEASE_TAG, WEBFLASH_PREVIEW_TAG)
        self.assertNotIn(
            _SCRIPT.EXPECTED_RELEASE_TAG, _SCRIPT.RESERVED_WEBFLASH_RELEASE_TAGS
        )


class WebFlashRoomPreviewSourceOfTruthTests(unittest.TestCase):
    """The WebFlash room preview release stays the room import source (item 5)."""

    def test_room_preview_configs_are_webflash_builds_rows(self) -> None:
        builds = _webflash_builds_by_cs()
        for cs in ROOM_PREVIEW_CONFIGS:
            with self.subTest(config_string=cs):
                self.assertIn(cs, builds)
                self.assertEqual(builds[cs]["channel"], "preview")

    def test_stable_room_config_is_a_webflash_builds_row(self) -> None:
        builds = _webflash_builds_by_cs()
        self.assertIn(STABLE_CONFIG, builds)
        self.assertEqual(builds[STABLE_CONFIG]["channel"], "stable")

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
    """TRIAC remains excluded under HW-005 (task item 5)."""

    def test_triac_selection_fails_closed(self) -> None:
        rows, errors = _SCRIPT._select_rows(
            *_docs(), version="1.0.0", release_target=TRIAC_CONFIG
        )
        self.assertEqual(rows, [])
        self.assertTrue(any("HW-005" in e for e in errors))

    def test_default_matrix_contains_no_triac(self) -> None:
        rows, errors = _SCRIPT._select_rows(*_docs(), version="1.0.0")
        self.assertEqual(errors, [])
        for row in rows:
            self.assertNotIn("TRIAC", row["config_string"])

    def test_release_body_excludes_triac_artifact_but_notes_hw005(self) -> None:
        rows, errors = _SCRIPT._select_rows(*_docs(), version="1.0.0")
        self.assertEqual(errors, [])
        body = _SCRIPT._release_body(rows, version="1.0.0", release_tag=DEDICATED_TAG)
        for token in BIN_TOKEN_RE.findall(body):
            self.assertNotIn("triac", token.lower())
        self.assertIn("HW-005", body)


class DocsRecordRetagDecisionTests(unittest.TestCase):
    """The docs record the retag decision (task items 4 / 5)."""

    def test_results_doc_records_correction(self) -> None:
        text = RESULTS_DOC.read_text(encoding="utf-8")
        self.assertIn(RETAG_ID, text)
        self.assertIn(DEDICATED_TAG, text)
        # The original deviation record is preserved alongside the correction.
        self.assertIn(WEBFLASH_PREVIEW_TAG, text)
        self.assertIn("intact", text.lower())
        # No room-preview .bin filename is introduced (results-doc bin-token
        # allow-set stays the three fan previews + the stable cross-reference;
        # room previews are referenced by config string only).
        stable_artifact = "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin"
        allowed = FAN_ARTIFACTS | {stable_artifact}
        tokens = set(BIN_TOKEN_RE.findall(text))
        self.assertTrue(
            tokens.issubset(allowed),
            f"results doc names unexpected .bin: {sorted(tokens - allowed)}",
        )
        self.assertEqual(tokens & ROOM_PREVIEW_ARTIFACTS, set())

    def test_plan_doc_records_tag_isolation(self) -> None:
        text = PLAN_DOC.read_text(encoding="utf-8")
        self.assertIn(RETAG_ID, text)
        self.assertIn("Guard release tag", text)

    def test_workflow_doc_records_tag_isolation(self) -> None:
        text = WORKFLOW_DOC.read_text(encoding="utf-8")
        self.assertIn(RETAG_ID, text)
        self.assertIn("Guard release tag", text)


class UpcomingPrTests(unittest.TestCase):
    """The queue marks the retag work done (task item 4)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = UPCOMING_PR.read_text(encoding="utf-8")

    def test_retag_id_present(self) -> None:
        self.assertIn(RETAG_ID, self.text)

    def test_retag_marked_done(self) -> None:
        retag_lines = [ln for ln in self.text.splitlines() if RETAG_ID in ln]
        self.assertTrue(retag_lines, f"{RETAG_ID} not found in UPCOMING_PR.md")
        self.assertTrue(
            any("DONE" in ln for ln in retag_lines),
            f"{RETAG_ID} is not marked DONE in any heading/line",
        )


class HardGuardrailTests(unittest.TestCase):
    """Hard guardrails: workflow + docs + tests only — no publish side effects."""

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

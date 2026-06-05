#!/usr/bin/env python3
"""Regression guard for RELEASE-PREVIEW-FAN-PUBLISH-WORKFLOW-001."""

from __future__ import annotations

import importlib.util
import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "manual-preview-fan-publish.yml"
SCRIPT_PATH = REPO_ROOT / "scripts" / "validate_manual_preview_fan_publish.py"
WEBFLASH_BUILDS = REPO_ROOT / "config" / "webflash-builds.json"

WORKFLOW_ID = "RELEASE-PREVIEW-FAN-PUBLISH-WORKFLOW-001"
RUN_ID = "RELEASE-PREVIEW-FAN-PUBLISH-RUN-001"
# RELEASE-PREVIEW-FAN-SHARED-TAG-001: the manual-preview fan publish workflow
# defaults to the shared v1.0.0-preview preview release (the single preview
# release for all preview artifacts). There is no dedicated fan tag.
DEFAULT_TAG = "v1.0.0-preview"
RETIRED_DEDICATED_TAG = "v1.0.0-manual-preview-fans"
VERSION = "1.0.0"

FAN_CONFIGS = (
    "Ceiling-POE-VentIQ-FanRelay-RoomIQ",
    "Ceiling-POE-FanPWM",
    "Ceiling-POE-FanDAC",
)
TRIAC_CONFIG = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"

EXPECTED_ARTIFACTS = {
    f"Sense360-{config}-v{VERSION}-preview.bin" for config in FAN_CONFIGS
}


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


_SCRIPT = _load_module("validate_manual_preview_fan_publish", SCRIPT_PATH)


def _workflow_text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def _release_target_options(text: str) -> list[str]:
    match = re.search(
        r"release_target:\n(?:[^\n]*\n)*?\s+options:\n(?P<options>(?:\s+- .+\n)+)",
        text,
    )
    if not match:
        return []
    return [line.split("-", 1)[1].strip() for line in match.group("options").splitlines()]


class WorkflowShapeTests(unittest.TestCase):
    def test_workflow_exists_and_names_the_canonical_slice(self) -> None:
        self.assertTrue(WORKFLOW.is_file())
        text = _workflow_text()
        self.assertIn(WORKFLOW_ID, text)

    def test_workflow_is_dispatch_only(self) -> None:
        text = _workflow_text()
        self.assertRegex(text, r"(?m)^on:\n  workflow_dispatch:")
        self.assertNotRegex(text, r"(?m)^  release:")
        self.assertNotRegex(text, r"(?m)^  push:")
        self.assertNotRegex(text, r"(?m)^  pull_request:")

    def test_dry_run_is_safe_default(self) -> None:
        text = _workflow_text()
        self.assertRegex(
            text,
            r"dry_run:\n(?:[^\n]*\n)*?\s+default: true\n\s+type: boolean",
        )

    def test_release_target_picker_is_manual_fans_only(self) -> None:
        options = _release_target_options(_workflow_text())
        self.assertEqual(
            options,
            ["all-manual-preview-fans", *FAN_CONFIGS],
        )
        self.assertNotIn(TRIAC_CONFIG, options)

    def test_default_release_tag_is_shared_preview_release(self) -> None:
        text = _workflow_text()
        self.assertRegex(
            text,
            rf"release_tag:\n(?:[^\n]*\n)*?\s+default: \"{re.escape(DEFAULT_TAG)}\"",
        )

    def test_default_release_tag_is_not_a_dedicated_fan_tag(self) -> None:
        # The retired dedicated vehicle must not be the workflow default.
        text = _workflow_text()
        self.assertNotIn(f'default: "{RETIRED_DEDICATED_TAG}"', text)

    def test_confirm_tag_override_input_present(self) -> None:
        # RELEASE-PREVIEW-FAN-PUBLISH-TAG-GUARD-001: a non-shared tag needs
        # explicit confirmation.
        text = _workflow_text()
        self.assertRegex(
            text,
            r"confirm_tag_override:\n(?:[^\n]*\n)*?\s+default: false\n"
            r"\s+type: boolean",
        )

    def test_guard_release_tag_step_confirm_gates_non_shared_tag(self) -> None:
        # RELEASE-PREVIEW-FAN-PUBLISH-TAG-GUARD-001: a dedicated guard step fails
        # fast (before any build) on an unconfirmed non-shared tag.
        text = _workflow_text()
        self.assertIn("Guard release tag", text)
        self.assertIn("--validate-release-tag", text)
        self.assertIn(
            '--confirm-tag-override "${{ inputs.confirm_tag_override }}"', text
        )

    def test_permissions_are_read_only_except_publish_job(self) -> None:
        text = _workflow_text()
        self.assertRegex(text, r"(?m)^permissions:\n  contents: read$")
        self.assertRegex(
            text,
            r"dry-run:\n(?:.|\n)*?permissions:\n      contents: read",
        )
        self.assertRegex(
            text,
            r"publish:\n(?:.|\n)*?permissions:\n      contents: write",
        )

    def test_publish_job_is_gated_behind_non_dry_run_dispatch(self) -> None:
        text = _workflow_text()
        self.assertRegex(text, r"build:\n(?:.|\n)*?if: github\.event_name == 'workflow_dispatch' && !inputs\.dry_run")
        self.assertRegex(text, r"publish:\n(?:.|\n)*?if: github\.event_name == 'workflow_dispatch' && !inputs\.dry_run")
        self.assertRegex(text, r"dry-run:\n(?:.|\n)*?if: github\.event_name == 'workflow_dispatch' && inputs\.dry_run")

    def test_publish_job_attaches_to_shared_release_via_gh_release(self) -> None:
        text = _workflow_text()
        self.assertIn("softprops/action-gh-release", text)
        self.assertIn("tag_name: ${{ inputs.release_tag }}", text)
        self.assertIn("all-firmware/*.bin", text)
        self.assertIn("all-firmware/checksums-sha256.txt", text)


class HelperScriptTests(unittest.TestCase):
    def _docs(self):
        return (
            _SCRIPT._load_json(_SCRIPT.LEDGER_PATH),
            _SCRIPT._load_json(_SCRIPT.MANUAL_PATH),
            _SCRIPT._load_json(_SCRIPT.WEBFLASH_BUILDS_PATH),
        )

    def test_metadata_selects_exactly_three_manual_preview_fans(self) -> None:
        rows, errors = _SCRIPT._select_rows(*self._docs(), version=VERSION)
        self.assertEqual(errors, [])
        self.assertEqual([row["config_string"] for row in rows], list(FAN_CONFIGS))

    def test_single_target_selection(self) -> None:
        for config in FAN_CONFIGS:
            with self.subTest(config_string=config):
                rows, errors = _SCRIPT._select_rows(
                    *self._docs(),
                    version=VERSION,
                    release_target=config,
                )
                self.assertEqual(errors, [])
                self.assertEqual([row["config_string"] for row in rows], [config])

    def test_triac_selection_fails_closed(self) -> None:
        # TRIAC stays excluded from the manual-preview fan publish lane after
        # TRIAC-UNBLOCK-BUILD-001: it is buildable but delivered on the
        # advanced-manual-preview lane (published separately).
        rows, errors = _SCRIPT._select_rows(
            *self._docs(),
            version=VERSION,
            release_target=TRIAC_CONFIG,
        )
        self.assertEqual(rows, [])
        self.assertTrue(any("advanced-manual-preview" in error for error in errors))

    def test_matrix_artifact_names_match_contract(self) -> None:
        rows, errors = _SCRIPT._select_rows(*self._docs(), version=VERSION)
        self.assertEqual(errors, [])
        matrix = _SCRIPT._matrix(rows)
        self.assertEqual(
            {item["artifact_name"] for item in matrix["include"]},
            EXPECTED_ARTIFACTS,
        )
        for item in matrix["include"]:
            self.assertTrue(item["product_yaml"].startswith("products/sense360-"))
            self.assertNotIn("products/webflash/", item["product_yaml"])

    def test_release_body_validates_against_preview_contract(self) -> None:
        rows, errors = _SCRIPT._select_rows(*self._docs(), version=VERSION)
        self.assertEqual(errors, [])
        body = _SCRIPT._release_body(rows, version=VERSION, release_tag=DEFAULT_TAG)
        notes_module = _load_module(
            "validate_webflash_notes_for_manual_preview_fans",
            REPO_ROOT / "scripts" / "validate-webflash-release-notes.py",
        )
        self.assertEqual(notes_module.validate_body(body, channel="preview"), [])
        for artifact in EXPECTED_ARTIFACTS:
            self.assertIn(artifact, body)
        self.assertIn(TRIAC_CONFIG, body)
        self.assertIn("advanced-manual-preview", body)

    def test_selected_rows_are_never_stable_recommended_default_buyable(self) -> None:
        rows, errors = _SCRIPT._select_rows(*self._docs(), version=VERSION)
        self.assertEqual(errors, [])
        for row in rows:
            posture = row["commercial_posture"]
            with self.subTest(config_string=row["config_string"]):
                self.assertEqual(posture["visibility"], "hidden")
                for flag in (
                    "stable",
                    "recommended",
                    "customer_default",
                    "buyable",
                    "release_one_required_config",
                ):
                    self.assertFalse(
                        posture[flag], f"{row['config_string']}: posture.{flag} must be false"
                    )

    def test_shared_release_body_does_not_imply_webflash_import(self) -> None:
        # A fan artifact living in the shared v1.0.0-preview release must never
        # imply WebFlash import; eligibility stays controlled by import policy.
        rows, errors = _SCRIPT._select_rows(*self._docs(), version=VERSION)
        self.assertEqual(errors, [])
        body = _SCRIPT._release_body(
            rows, version=VERSION, release_tag=DEFAULT_TAG
        ).lower()
        self.assertIn("shared", body)
        self.assertIn("webflash import eligibility is controlled", body)
        self.assertIn("does not make them webflash one-click imports", body)

    def test_shared_release_body_records_room_and_fan_previews(self) -> None:
        # The shared preview release may legitimately contain both room-bundle
        # and fan preview artifacts.
        rows, errors = _SCRIPT._select_rows(*self._docs(), version=VERSION)
        self.assertEqual(errors, [])
        body = _SCRIPT._release_body(
            rows, version=VERSION, release_tag=DEFAULT_TAG
        ).lower()
        self.assertIn(DEFAULT_TAG, body)
        self.assertIn("room-bundle preview", body)

    def test_output_validation_accepts_only_expected_artifacts(self) -> None:
        rows, errors = _SCRIPT._select_rows(*self._docs(), version=VERSION)
        self.assertEqual(errors, [])
        tmp = REPO_ROOT / "tests" / ".tmp-manual-preview-output"
        tmp.mkdir(exist_ok=True)
        try:
            for artifact in EXPECTED_ARTIFACTS:
                (tmp / artifact).write_bytes(b"placeholder")
            self.assertEqual(_SCRIPT._validate_output_dir(rows, tmp), [])
            (tmp / "Sense360-Ceiling-POE-VentIQ-FanTRIAC-RoomIQ-v1.0.0-preview.bin").write_bytes(
                b"placeholder"
            )
            errors = _SCRIPT._validate_output_dir(rows, tmp)
            self.assertTrue(any("TRIAC" in error for error in errors))
        finally:
            for path in tmp.glob("*"):
                path.unlink()
            tmp.rmdir()


class GuardrailTests(unittest.TestCase):
    def test_fans_still_absent_from_webflash_builds(self) -> None:
        builds = json.loads(WEBFLASH_BUILDS.read_text(encoding="utf-8"))["builds"]
        config_strings = {entry["config_string"] for entry in builds}
        for config in FAN_CONFIGS + (TRIAC_CONFIG,):
            self.assertNotIn(config, config_strings)

    def test_no_repo_manifest_sources_or_bin_committed(self) -> None:
        self.assertFalse((REPO_ROOT / "manifest.json").exists())
        self.assertFalse((REPO_ROOT / "firmware" / "sources.json").exists())
        bins = [path for path in REPO_ROOT.rglob("*.bin") if ".git" not in path.parts]
        self.assertEqual(bins, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)

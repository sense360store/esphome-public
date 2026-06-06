#!/usr/bin/env python3
"""Regression guard for ROOM-BUNDLE-FAN-PUBLISH-WORKFLOW-001.

Locks the additive room-bundle fan-control preview publish workflow + validator
(``.github/workflows/room-bundle-fan-publish.yml`` +
``scripts/validate_room_bundle_fan_publish.py``) against the task contract:

  * the workflow exists, names the canonical slice, and is ``workflow_dispatch``
    only with ``dry_run`` defaulting to ``true``;
  * publishing requires an explicit ``dry_run: false`` (build + publish jobs are
    gated behind ``!inputs.dry_run``; the dry-run job behind ``inputs.dry_run``);
  * the scoped target list is EXACTLY the five compile-validated room-bundle fan
    configs (plus the ``all-room-bundle-fan-previews`` group); TRIAC is excluded;
  * the matrix is generated from ``config/room-bundle-fan-variants.json`` +
    ``config/compile-only-targets.json`` (NOT ``config/webflash-builds.json``),
    each artifact follows the ``Sense360-…-v1.0.0-preview.bin`` contract, and each
    cites compile run ``26913592989``;
  * the FanDAC IC2 ``0x5A`` address policy is enforced (IC1 ``0x58``, ``0x59``
    forbidden, ``FANDAC-I2C-ADDR-001`` pending) and non-FanDAC configs carry no
    such requirement;
  * nothing is stable / recommended / default / buyable and no stable artifact is
    published; the run attaches to the existing shared ``v1.0.0-preview`` release
    and creates no new release / tag;
  * the existing single-driver manual-preview fan publish lane is unchanged; and
  * the hard guardrails hold (no ``.bin`` / ``manifest.json`` /
    ``firmware/sources.json`` committed; no fan row in the WebFlash build ledger).

Run with::

    python3 tests/test_room_bundle_fan_publish_workflow.py
"""

from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import re
import unittest
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "room-bundle-fan-publish.yml"
SCRIPT_PATH = REPO_ROOT / "scripts" / "validate_room_bundle_fan_publish.py"
MANUAL_SCRIPT_PATH = REPO_ROOT / "scripts" / "validate_manual_preview_fan_publish.py"
VARIANTS_PATH = REPO_ROOT / "config" / "room-bundle-fan-variants.json"
COMPILE_TARGETS_PATH = REPO_ROOT / "config" / "compile-only-targets.json"
WEBFLASH_BUILDS = REPO_ROOT / "config" / "webflash-builds.json"
WORKFLOW_DOC = REPO_ROOT / "docs" / "room-bundle-fan-publish-workflow.md"
PLAN_DOC = REPO_ROOT / "docs" / "room-bundle-fan-publish-plan.md"
UPCOMING_PR = REPO_ROOT / "UPCOMING_PR.md"

WORKFLOW_ID = "ROOM-BUNDLE-FAN-PUBLISH-WORKFLOW-001"
RUN_ID = "ROOM-BUNDLE-FAN-PUBLISH-RUN-001"
TAG_GUARD_ID = "RELEASE-PREVIEW-FAN-PUBLISH-TAG-GUARD-001"
DEFAULT_TAG = "v1.0.0-preview"
STABLE_TAG = "v1.0.0"
RETIRED_DEDICATED_TAG = "v1.0.0-manual-preview-fans"
VERSION = "1.0.0"
COMPILE_RUN_ID = 26913592989
SINGLE_DRIVER_COMPILE_RUN_ID = 26821900127

ALL_TARGETS = "all-room-bundle-fan-previews"
ROOM_BUNDLE_FAN_CONFIGS = (
    "Ceiling-POE-VentIQ-FanPWM-RoomIQ",
    "Ceiling-POE-VentIQ-FanDAC-RoomIQ",
    "Ceiling-POE-AirIQ-FanRelay-RoomIQ",
    "Ceiling-POE-AirIQ-FanDAC-RoomIQ",
    "Ceiling-POE-AirIQ-FanPWM-RoomIQ",
)
FANDAC_CONFIGS = (
    "Ceiling-POE-VentIQ-FanDAC-RoomIQ",
    "Ceiling-POE-AirIQ-FanDAC-RoomIQ",
)
TRIAC_CONFIG = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"
SINGLE_DRIVER_FAN_CONFIGS = (
    "Ceiling-POE-VentIQ-FanRelay-RoomIQ",
    "Ceiling-POE-FanPWM",
    "Ceiling-POE-FanDAC",
)
FAN_TOKENS = ("FanRelay", "FanPWM", "FanDAC", "FanTRIAC")

EXPECTED_ARTIFACTS = {
    f"Sense360-{config}-v{VERSION}-preview.bin" for config in ROOM_BUNDLE_FAN_CONFIGS
}


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


_SCRIPT = _load_module("validate_room_bundle_fan_publish", SCRIPT_PATH)


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


def _docs() -> tuple:
    return (
        _SCRIPT._load_json(_SCRIPT.VARIANTS_PATH),
        _SCRIPT._load_json(_SCRIPT.COMPILE_TARGETS_PATH),
        _SCRIPT._load_json(_SCRIPT.WEBFLASH_BUILDS_PATH),
    )


def _run_main(argv: List[str]) -> int:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        return _SCRIPT.main(argv)


def _webflash_config_strings() -> set[str]:
    builds = json.loads(WEBFLASH_BUILDS.read_text(encoding="utf-8"))["builds"]
    return {b["config_string"] for b in builds}


class WorkflowShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = _workflow_text()

    def test_workflow_exists_and_names_the_canonical_slice(self) -> None:
        self.assertTrue(WORKFLOW.is_file())
        self.assertIn(WORKFLOW_ID, self.text)

    def test_workflow_is_dispatch_only(self) -> None:
        self.assertRegex(self.text, r"(?m)^on:\n  workflow_dispatch:")
        self.assertNotRegex(self.text, r"(?m)^  release:")
        self.assertNotRegex(self.text, r"(?m)^  push:")
        self.assertNotRegex(self.text, r"(?m)^  pull_request:")

    def test_dry_run_is_safe_default(self) -> None:
        self.assertRegex(
            self.text,
            r"dry_run:\n(?:[^\n]*\n)*?\s+default: true\n\s+type: boolean",
        )

    def test_release_target_picker_is_room_bundle_fans_only(self) -> None:
        options = _release_target_options(self.text)
        self.assertEqual(options, [ALL_TARGETS, *ROOM_BUNDLE_FAN_CONFIGS])
        self.assertNotIn(TRIAC_CONFIG, options)

    def test_default_release_tag_is_shared_preview_release(self) -> None:
        self.assertRegex(
            self.text,
            rf'release_tag:\n(?:[^\n]*\n)*?\s+default: "{re.escape(DEFAULT_TAG)}"',
        )

    def test_default_release_tag_is_not_a_dedicated_fan_tag(self) -> None:
        self.assertNotIn(f'default: "{RETIRED_DEDICATED_TAG}"', self.text)

    def test_confirm_tag_override_input_present(self) -> None:
        self.assertRegex(
            self.text,
            r"confirm_tag_override:\n(?:[^\n]*\n)*?\s+default: false\n"
            r"\s+type: boolean",
        )

    def test_guard_release_tag_step_confirm_gates_non_shared_tag(self) -> None:
        self.assertIn("Guard release tag", self.text)
        self.assertIn("--validate-release-tag", self.text)
        self.assertIn(
            '--confirm-tag-override "${{ inputs.confirm_tag_override }}"', self.text
        )

    def test_workflow_uses_the_room_bundle_validator(self) -> None:
        self.assertIn("scripts/validate_room_bundle_fan_publish.py", self.text)

    def test_permissions_are_read_only_except_publish_job(self) -> None:
        self.assertRegex(self.text, r"(?m)^permissions:\n  contents: read$")
        self.assertRegex(
            self.text, r"dry-run:\n(?:.|\n)*?permissions:\n      contents: read"
        )
        self.assertRegex(
            self.text, r"publish:\n(?:.|\n)*?permissions:\n      contents: write"
        )

    def test_publish_requires_explicit_non_dry_run_dispatch(self) -> None:
        self.assertRegex(
            self.text,
            r"(?m)^  build:\n(?:.|\n)*?if: github\.event_name == 'workflow_dispatch' && !inputs\.dry_run",
        )
        self.assertRegex(
            self.text,
            r"(?m)^  publish:\n(?:.|\n)*?if: github\.event_name == 'workflow_dispatch' && !inputs\.dry_run",
        )
        self.assertRegex(
            self.text,
            r"(?m)^  dry-run:\n(?:.|\n)*?if: github\.event_name == 'workflow_dispatch' && inputs\.dry_run",
        )

    def test_publish_job_attaches_to_shared_release_via_gh_release(self) -> None:
        self.assertIn("softprops/action-gh-release", self.text)
        self.assertIn("tag_name: ${{ inputs.release_tag }}", self.text)
        self.assertIn("all-firmware/*.bin", self.text)
        self.assertIn("all-firmware/checksums-sha256.txt", self.text)
        self.assertIn("all-firmware/manifest.json", self.text)

    def test_workflow_creates_no_new_release_or_tag(self) -> None:
        # Attaches to the existing shared tag only; never creates a tag / release.
        self.assertNotIn("gh release create", self.text)
        self.assertNotIn("git tag", self.text)
        self.assertIn("does NOT create a new release / tag", self.text)

    def test_workflow_publishes_no_stable_artifact(self) -> None:
        self.assertNotIn("-stable.bin", self.text)
        self.assertIn("prerelease: true", self.text)
        self.assertIn('"channel": "preview"', self.text)

    def test_workflow_declares_preview_channel_manual_preview_lane(self) -> None:
        # Build channel is preview; publish delivery lane is manual-preview.
        self.assertIn('"channel": "preview"', self.text)
        self.assertIn('"delivery_lane": "manual-preview"', self.text)

    def test_workflow_cites_the_room_bundle_compile_run(self) -> None:
        self.assertIn(str(COMPILE_RUN_ID), self.text)


class HelperScriptScopeTests(unittest.TestCase):
    def test_scope_constant_is_exactly_five(self) -> None:
        self.assertEqual(_SCRIPT.ROOM_BUNDLE_FAN_CONFIGS, ROOM_BUNDLE_FAN_CONFIGS)
        self.assertEqual(_SCRIPT.EXPECTED_COMPILE_RUN_ID, COMPILE_RUN_ID)

    def test_metadata_selects_exactly_five_room_bundle_fans(self) -> None:
        rows, errors = _SCRIPT._select_rows(*_docs(), version=VERSION)
        self.assertEqual(errors, [])
        self.assertEqual(
            [row["config_string"] for row in rows], list(ROOM_BUNDLE_FAN_CONFIGS)
        )

    def test_single_target_selection(self) -> None:
        for config in ROOM_BUNDLE_FAN_CONFIGS:
            with self.subTest(config_string=config):
                rows, errors = _SCRIPT._select_rows(
                    *_docs(), version=VERSION, release_target=config
                )
                self.assertEqual(errors, [])
                self.assertEqual([row["config_string"] for row in rows], [config])

    def test_triac_selection_fails_closed(self) -> None:
        # TRIAC must still fail closed: HW-005 buildability is resolved, but the
        # advanced-manual-preview publish stays gated by PACKAGE-TRIAC-001 +
        # COMPLIANCE-001 and is not published by this workflow.
        rows, errors = _SCRIPT._select_rows(
            *_docs(), version=VERSION, release_target=TRIAC_CONFIG
        )
        self.assertEqual(rows, [])
        self.assertTrue(
            any(
                "PACKAGE-TRIAC-001" in error and "COMPLIANCE-001" in error
                for error in errors
            )
        )

    def test_unknown_target_fails_closed(self) -> None:
        rows, errors = _SCRIPT._select_rows(
            *_docs(), version=VERSION, release_target="Ceiling-POE-Nope"
        )
        self.assertEqual(rows, [])
        self.assertTrue(errors)

    def test_matrix_artifact_names_match_contract(self) -> None:
        rows, errors = _SCRIPT._select_rows(*_docs(), version=VERSION)
        self.assertEqual(errors, [])
        matrix = _SCRIPT._matrix(rows)
        self.assertEqual(
            {item["artifact_name"] for item in matrix["include"]}, EXPECTED_ARTIFACTS
        )
        for item in matrix["include"]:
            self.assertTrue(item["product_yaml"].startswith("products/sense360-"))
            self.assertNotIn("products/webflash/", item["product_yaml"])
            self.assertTrue(item["artifact_name"].endswith("-preview.bin"))

    def test_expected_preview_artifacts_constant_matches_task(self) -> None:
        self.assertEqual(set(_SCRIPT.EXPECTED_PREVIEW_ARTIFACTS), EXPECTED_ARTIFACTS)


class CompileEvidenceTests(unittest.TestCase):
    def test_every_selected_row_cites_the_room_bundle_run(self) -> None:
        variants = _SCRIPT._variants_by_config(_SCRIPT._load_json(VARIANTS_PATH))
        for cs in ROOM_BUNDLE_FAN_CONFIGS:
            with self.subTest(config_string=cs):
                ev = variants[cs]["firmware_config_evidence"]["compile_evidence"]
                self.assertEqual(ev["run_id"], COMPILE_RUN_ID)
                self.assertNotEqual(ev["run_id"], SINGLE_DRIVER_COMPILE_RUN_ID)
                self.assertEqual(ev["proof_scope"], "firmware-build-only")

    def test_release_body_validates_against_preview_contract(self) -> None:
        rows, errors = _SCRIPT._select_rows(*_docs(), version=VERSION)
        self.assertEqual(errors, [])
        body = _SCRIPT._release_body(rows, version=VERSION, release_tag=DEFAULT_TAG)
        notes_module = _load_module(
            "validate_webflash_notes_for_room_bundle_fans",
            REPO_ROOT / "scripts" / "validate-webflash-release-notes.py",
        )
        self.assertEqual(notes_module.validate_body(body, channel="preview"), [])
        for artifact in EXPECTED_ARTIFACTS:
            self.assertIn(artifact, body)
        self.assertIn(str(COMPILE_RUN_ID), body)
        self.assertIn(TRIAC_CONFIG, body)
        self.assertIn("HW-005", body)
        # The TRIAC exclusion reason is now the advanced-manual-preview publish
        # gate, not a buildability blocker.
        self.assertIn("PACKAGE-TRIAC-001", body)
        self.assertIn("COMPLIANCE-001", body)

    def test_release_body_does_not_imply_webflash_import(self) -> None:
        rows, errors = _SCRIPT._select_rows(*_docs(), version=VERSION)
        self.assertEqual(errors, [])
        body = _SCRIPT._release_body(
            rows, version=VERSION, release_tag=DEFAULT_TAG
        ).lower()
        self.assertIn("shared", body)
        self.assertIn("webflash import eligibility is controlled", body)
        self.assertIn("does not make them webflash one-click imports", body)


class FanDacAddressPolicyTests(unittest.TestCase):
    def test_source_fandac_requirements_are_correct(self) -> None:
        variants = _SCRIPT._variants_by_config(_SCRIPT._load_json(VARIANTS_PATH))
        for cs in FANDAC_CONFIGS:
            with self.subTest(config_string=cs):
                req = variants[cs]["firmware_config_evidence"][
                    "fan_dac_address_requirement"
                ]
                self.assertEqual(req["gp8403_ic1"], "0x58")
                self.assertEqual(req["gp8403_ic2"], "0x5A")
                self.assertEqual(req["forbidden_gp8403_address"], "0x59")
                self.assertEqual(
                    req["bench_verification_followup"], "FANDAC-I2C-ADDR-001"
                )
                self.assertEqual(req["bench_verification_status"], "pending")

    def test_release_body_records_fandac_policy_and_pending(self) -> None:
        rows, errors = _SCRIPT._select_rows(*_docs(), version=VERSION)
        self.assertEqual(errors, [])
        body = _SCRIPT._release_body(rows, version=VERSION, release_tag=DEFAULT_TAG)
        self.assertIn("0x5A", body)
        self.assertIn("0x58", body)
        self.assertIn("0x59", body)
        self.assertIn("FANDAC-I2C-ADDR-001", body)
        self.assertIn("pending", body.lower())

    def test_validator_rejects_wrong_fandac_ic2_address(self) -> None:
        variants = copy.deepcopy(_SCRIPT._load_json(VARIANTS_PATH))
        for variant in variants["fan_variant_candidates"]:
            if variant["intended_firmware_config_string"] in FANDAC_CONFIGS:
                variant["firmware_config_evidence"]["fan_dac_address_requirement"][
                    "gp8403_ic2"
                ] = "0x59"  # forbidden collision
        rows, errors = _SCRIPT._select_rows(
            variants,
            _SCRIPT._load_json(COMPILE_TARGETS_PATH),
            _SCRIPT._load_json(WEBFLASH_BUILDS),
            version=VERSION,
        )
        self.assertTrue(any("IC2" in e for e in errors), errors)

    def test_validator_requires_pending_bench_status(self) -> None:
        variants = copy.deepcopy(_SCRIPT._load_json(VARIANTS_PATH))
        for variant in variants["fan_variant_candidates"]:
            if variant["intended_firmware_config_string"] in FANDAC_CONFIGS:
                variant["firmware_config_evidence"]["fan_dac_address_requirement"][
                    "bench_verification_status"
                ] = "verified"  # would falsely claim hardware verification
        _rows, errors = _SCRIPT._select_rows(
            variants,
            _SCRIPT._load_json(COMPILE_TARGETS_PATH),
            _SCRIPT._load_json(WEBFLASH_BUILDS),
            version=VERSION,
        )
        self.assertTrue(any("pending" in e for e in errors), errors)

    def test_non_fandac_configs_carry_no_fandac_requirement(self) -> None:
        variants = _SCRIPT._variants_by_config(_SCRIPT._load_json(VARIANTS_PATH))
        non_fandac = set(ROOM_BUNDLE_FAN_CONFIGS) - set(FANDAC_CONFIGS)
        for cs in non_fandac:
            with self.subTest(config_string=cs):
                ev = variants[cs]["firmware_config_evidence"]
                self.assertNotIn("fan_dac_address_requirement", ev)


class NoStableRecommendedDefaultBuyableTests(unittest.TestCase):
    def test_selected_rows_have_false_posture_flags(self) -> None:
        variants = _SCRIPT._variants_by_config(_SCRIPT._load_json(VARIANTS_PATH))
        for cs in ROOM_BUNDLE_FAN_CONFIGS:
            with self.subTest(config_string=cs):
                v = variants[cs]
                self.assertFalse(v["recommended"])
                self.assertFalse(v["customer_default"])
                self.assertFalse(v["buyable"])
                self.assertFalse(v["bench_evidence_claimed"])
                self.assertFalse(v["compliance_claimed"])
                self.assertEqual(v["stable_status"], "blocked")
                self.assertEqual(v["commercial_availability"], "waitlist-only")

    def test_validator_rejects_a_buyable_claim(self) -> None:
        variants = copy.deepcopy(_SCRIPT._load_json(VARIANTS_PATH))
        for variant in variants["fan_variant_candidates"]:
            if variant["intended_firmware_config_string"] == ROOM_BUNDLE_FAN_CONFIGS[0]:
                variant["buyable"] = True
        _rows, errors = _SCRIPT._select_rows(
            variants,
            _SCRIPT._load_json(COMPILE_TARGETS_PATH),
            _SCRIPT._load_json(WEBFLASH_BUILDS),
            version=VERSION,
        )
        self.assertTrue(any("buyable" in e for e in errors), errors)


class OutputValidationTests(unittest.TestCase):
    def test_output_validation_accepts_only_expected_artifacts(self) -> None:
        rows, errors = _SCRIPT._select_rows(*_docs(), version=VERSION)
        self.assertEqual(errors, [])
        tmp = REPO_ROOT / "tests" / ".tmp-room-bundle-fan-output"
        tmp.mkdir(exist_ok=True)
        try:
            for artifact in EXPECTED_ARTIFACTS:
                (tmp / artifact).write_bytes(b"placeholder")
            self.assertEqual(_SCRIPT._validate_output_dir(rows, tmp), [])

            # A TRIAC artifact must be rejected.
            (tmp / f"Sense360-{TRIAC_CONFIG}-v{VERSION}-preview.bin").write_bytes(
                b"placeholder"
            )
            errs = _SCRIPT._validate_output_dir(rows, tmp)
            self.assertTrue(any("TRIAC" in e for e in errs))
            (tmp / f"Sense360-{TRIAC_CONFIG}-v{VERSION}-preview.bin").unlink()

            # A stable artifact must be rejected.
            (tmp / "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin").write_bytes(
                b"placeholder"
            )
            errs = _SCRIPT._validate_output_dir(rows, tmp)
            self.assertTrue(any("stable" in e for e in errs))
        finally:
            for path in tmp.glob("*"):
                path.unlink()
            tmp.rmdir()


class TagGuardTests(unittest.TestCase):
    def test_shared_tag_accepted_without_confirmation(self) -> None:
        self.assertEqual(_SCRIPT._validate_release_tag(DEFAULT_TAG), [])

    def test_non_shared_tag_requires_confirmation(self) -> None:
        self.assertTrue(_SCRIPT._validate_release_tag(STABLE_TAG))
        self.assertEqual(
            _SCRIPT._validate_release_tag(STABLE_TAG, confirm_override=True), []
        )

    def test_cli_validate_release_tag(self) -> None:
        self.assertEqual(
            _run_main(["--validate-release-tag", "--release-tag", DEFAULT_TAG]), 0
        )
        self.assertEqual(
            _run_main(["--validate-release-tag", "--release-tag", STABLE_TAG]), 1
        )
        self.assertEqual(
            _run_main(
                [
                    "--validate-release-tag",
                    "--release-tag",
                    STABLE_TAG,
                    "--confirm-tag-override",
                    "true",
                ]
            ),
            0,
        )

    def test_metadata_only_rejects_unconfirmed_non_shared_tag(self) -> None:
        self.assertEqual(
            _run_main(["--metadata-only", "--release-tag", "v2.0.0-preview"]), 1
        )


class ExistingLaneUnchangedTests(unittest.TestCase):
    """The single-driver manual-preview fan publish lane stays untouched."""

    def test_single_driver_validator_still_scopes_to_three(self) -> None:
        manual = _load_module(
            "validate_manual_preview_fan_publish_for_room_bundle_workflow",
            MANUAL_SCRIPT_PATH,
        )
        self.assertEqual(tuple(manual.FAN_CONFIGS), SINGLE_DRIVER_FAN_CONFIGS)
        rows, errors = manual._select_rows(
            manual._load_json(manual.LEDGER_PATH),
            manual._load_json(manual.MANUAL_PATH),
            manual._load_json(manual.WEBFLASH_BUILDS_PATH),
            version=VERSION,
            release_target="all-manual-preview-fans",
        )
        self.assertEqual(errors, [])
        selected = sorted(r["config_string"] for r in rows)
        self.assertEqual(selected, sorted(SINGLE_DRIVER_FAN_CONFIGS))
        for cs in ROOM_BUNDLE_FAN_CONFIGS:
            self.assertNotIn(cs, selected)

    def test_single_driver_workflow_still_present(self) -> None:
        manual_wf = REPO_ROOT / ".github" / "workflows" / "manual-preview-fan-publish.yml"
        self.assertTrue(manual_wf.is_file())
        wf_text = manual_wf.read_text(encoding="utf-8")
        self.assertIn("RELEASE-PREVIEW-FAN-PUBLISH-WORKFLOW-001", wf_text)
        self.assertIn("validate_manual_preview_fan_publish.py", wf_text)
        # The single-driver lane keeps citing its OWN compile run (26821900127),
        # distinct from this room-bundle lane's run (26913592989).
        manual = _load_module(
            "validate_manual_preview_fan_publish_run_id_check", MANUAL_SCRIPT_PATH
        )
        rows, errors = manual._select_rows(
            manual._load_json(manual.LEDGER_PATH),
            manual._load_json(manual.MANUAL_PATH),
            manual._load_json(manual.WEBFLASH_BUILDS_PATH),
            version=VERSION,
        )
        self.assertEqual(errors, [])
        body = manual._release_body(rows, version=VERSION, release_tag=DEFAULT_TAG)
        self.assertIn(str(SINGLE_DRIVER_COMPILE_RUN_ID), body)
        self.assertNotIn(str(COMPILE_RUN_ID), body)


class WebFlashLedgerGuardrailTests(unittest.TestCase):
    def test_five_and_triac_absent_from_webflash_builds(self) -> None:
        config_strings = _webflash_config_strings()
        for cs in ROOM_BUNDLE_FAN_CONFIGS + (TRIAC_CONFIG,):
            with self.subTest(config_string=cs):
                self.assertNotIn(cs, config_strings)

    def test_no_fan_token_in_webflash_builds(self) -> None:
        for cs in _webflash_config_strings():
            for token in FAN_TOKENS:
                with self.subTest(config_string=cs, token=token):
                    self.assertNotIn(token.lower(), cs.lower())


class HardGuardrailTests(unittest.TestCase):
    def test_no_repo_manifest_or_sources_committed(self) -> None:
        self.assertFalse((REPO_ROOT / "manifest.json").exists())
        self.assertFalse((REPO_ROOT / "firmware" / "sources.json").exists())

    def test_no_bin_committed_anywhere_in_repo(self) -> None:
        bins = [p for p in REPO_ROOT.rglob("*.bin") if ".git" not in p.parts]
        self.assertEqual(bins, [], f"no .bin may be committed; found {bins}")


class DocsAndQueueTests(unittest.TestCase):
    def test_workflow_doc_exists_and_names_canonical_id(self) -> None:
        self.assertTrue(WORKFLOW_DOC.is_file())
        text = WORKFLOW_DOC.read_text(encoding="utf-8")
        self.assertIn(WORKFLOW_ID, text)
        self.assertIn(str(COMPILE_RUN_ID), text)
        self.assertIn("FANDAC-I2C-ADDR-001", text)

    def test_plan_doc_references_the_landed_workflow(self) -> None:
        text = PLAN_DOC.read_text(encoding="utf-8")
        self.assertIn(WORKFLOW_ID, text)
        self.assertIn("room-bundle-fan-publish.yml", text)
        self.assertIn("validate_room_bundle_fan_publish.py", text)

    def test_upcoming_pr_marks_workflow_done(self) -> None:
        text = UPCOMING_PR.read_text(encoding="utf-8")
        done_lines = [
            ln for ln in text.splitlines() if WORKFLOW_ID in ln and "DONE" in ln
        ]
        self.assertTrue(
            done_lines, f"{WORKFLOW_ID} is not marked DONE in any UPCOMING_PR.md line"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

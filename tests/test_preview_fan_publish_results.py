#!/usr/bin/env python3
"""Regression guard for the manual-preview fan firmware PUBLISH RESULTS record.

RELEASE-PREVIEW-FAN-PUBLISH-RESULTS-001.

This PR records the **successful** ``Manual-Preview Fan Firmware Publish`` run
(``RELEASE-PREVIEW-FAN-PUBLISH-RUN-001``) that published the three buildable
manual-preview fan artifacts (FanRelay / FanPWM / FanDAC). This guard locks the
invariants the results doc and the ledger ``publish_evidence`` assert so they
cannot silently regress:

  * the results doc records run id ``26878032103``, the workflow name
    ``Manual-Preview Fan Firmware Publish``, the ``workflow_dispatch`` (manual
    dispatch) event, the commit ``0963afb``, and conclusion ``success`` (task
    items 3 / 5);
  * exactly the three buildable ``delivery_lane: manual-preview`` rows are the
    published targets, each a ``-preview.bin`` (task item 3); the only
    ``Sense360-*.bin`` tokens the doc may name are those three plus the stable
    Bathroom cross-reference; no FanTRIAC / TRIAC ``.bin`` is named;
  * the three fan rows of ``config/preview-fan-triac-build-rows.json`` carry a
    ``publish_evidence`` block recording run ``26878032103`` / conclusion
    ``success`` / ``webflash_importable: false``, while TRIAC carries **no**
    ``publish_evidence`` and stays build-blocked (task item 6);
  * the ledger still validates clean (the extra ``publish_evidence`` does not
    break ``scripts/validate_preview_fan_triac_build_rows.py``);
  * the preview posture is preserved — preview / not stable / not recommended /
    not a customer default / fan products hidden / not buyable, Simple install +
    the launch SKU ``S360-KIT-BATH-P`` unchanged, TRIAC excluded (``HW-005``),
    and no hardware / compliance proof claimed (task item 5);
  * the shared preview release is adopted — ``v1.0.0-preview`` is the single
    preview release for both the room-bundle previews and the fan manual-preview
    artifacts, framed as the intended shared release (not a deviation), with the
    dedicated ``v1.0.0-manual-preview-fans`` tag concept retired
    (``RELEASE-PREVIEW-FAN-SHARED-TAG-001``);
  * shared-release presence never implies WebFlash import — WebFlash import
    eligibility stays separately gated and the three fan rows stay
    ``webflash_importable: false``;
  * the hard guardrails hold — no ``manifest.json`` / ``firmware/sources.json`` /
    ``.bin`` is committed, and no fan / TRIAC row enters
    ``config/webflash-builds.json``; and
  * ``UPCOMING_PR.md`` marks ``RELEASE-PREVIEW-FAN-PUBLISH-RUN-001`` done and
    records the run id (task item 7).

Uses Python's stdlib unittest (matching the no-pytest convention the other
validators in this repo use). Run with::

    python3 tests/test_preview_fan_publish_results.py
"""

from __future__ import annotations

import importlib.util
import json
import re
import unittest
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER_PATH = REPO_ROOT / "config" / "preview-fan-triac-build-rows.json"
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
SHOP_PATH = REPO_ROOT / "config" / "shop-commercial-source-of-truth.json"
TARGETS_PATH = REPO_ROOT / "config" / "preview-release-targets.json"
POLICY_PATH = REPO_ROOT / "config" / "release-channel-policy.json"
MANUAL_PATH = REPO_ROOT / "config" / "manual-firmware-artifacts.json"
RESULTS_DOC = REPO_ROOT / "docs" / "release-preview-fan-publish-results.md"
UPCOMING_PR = REPO_ROOT / "UPCOMING_PR.md"
VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate_preview_fan_triac_build_rows.py"

RESULTS_ID = "RELEASE-PREVIEW-FAN-PUBLISH-RESULTS-001"
RUN_QUEUE_ID = "RELEASE-PREVIEW-FAN-PUBLISH-RUN-001"
WORKFLOW_NAME = "Manual-Preview Fan Firmware Publish"
RUN_ID = "26878032103"
COMMIT_SHA = "0963afb"
RELEASE_TAG_USED = "v1.0.0-preview"
# RELEASE-PREVIEW-FAN-SHARED-TAG-001: v1.0.0-preview is the single shared preview
# release for every preview artifact (room-bundle + LED + fan). The dedicated
# v1.0.0-manual-preview-fans tag concept is retired; tests must NOT expect it.
RETIRED_DEDICATED_TAG = "v1.0.0-manual-preview-fans"
LAUNCH_SKU = "S360-KIT-BATH-P"
VERSION = "1.0.0"

FAN_CONFIGS = (
    "Ceiling-POE-VentIQ-FanRelay-RoomIQ",
    "Ceiling-POE-FanPWM",
    "Ceiling-POE-FanDAC",
)
TRIAC_CONFIG = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"

STABLE_CONFIG = "Ceiling-POE-VentIQ-RoomIQ"
STABLE_ARTIFACT = "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin"

# The three durable fan preview artifacts this run published.
FAN_ARTIFACTS = {f"Sense360-{cs}-v{VERSION}-preview.bin" for cs in FAN_CONFIGS}
# Every Sense360-*.bin token the results doc may name: the three fan previews
# plus the stable Bathroom cross-reference. (The four co-mingled room-bundle
# previews are referenced by config string, not by .bin filename.)
ALLOWED_BIN_ARTIFACTS = set(FAN_ARTIFACTS) | {STABLE_ARTIFACT}

# Only TRIAC is forbidden as a named .bin (the three fan tokens are expected).
FORBIDDEN_BIN_TOKENS = ("FanTRIAC", "TRIAC")

# The three workflow (CI) artifact names the publish job consumed.
WORKFLOW_ARTIFACTS = (
    "manual-preview-firmware-fanrelay",
    "manual-preview-firmware-fanpwm",
    "manual-preview-firmware-fandac",
)

BIN_TOKEN_RE = re.compile(r"Sense360-[A-Za-z0-9.\-]+\.bin")


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _normalise(text: str) -> str:
    lines = [re.sub(r"^\s*>\s?", "", ln) for ln in text.splitlines()]
    joined = " ".join(lines).replace("`", "").replace("|", " ").replace("*", "")
    return re.sub(r"\s+", " ", joined).lower()


def _rows_by_cs() -> Dict[str, Dict[str, Any]]:
    return {r["config_string"]: r for r in _load_json(LEDGER_PATH)["rows"]}


def _builds() -> List[Dict[str, Any]]:
    return _load_json(BUILDS_PATH)["builds"]


class RunEvidenceTests(unittest.TestCase):
    """Task items 3 / 5: the run is recorded faithfully."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = RESULTS_DOC.read_text(encoding="utf-8")
        cls.norm = _normalise(cls.text)

    def test_results_doc_exists_and_is_self_identified(self) -> None:
        self.assertTrue(RESULTS_DOC.is_file())
        self.assertIn(RESULTS_ID, self.text)

    def test_records_run_id_and_workflow_name(self) -> None:
        self.assertIn(RUN_ID, self.text)
        self.assertIn(WORKFLOW_NAME, self.text)

    def test_records_workflow_dispatch_not_release_event(self) -> None:
        self.assertIn("workflow_dispatch", self.norm)
        self.assertIn("manual dispatch", self.norm)

    def test_records_commit_and_success_conclusion(self) -> None:
        self.assertIn(COMMIT_SHA, self.text)
        self.assertIn("success", self.norm)

    def test_records_three_fan_builds_and_attach_steps(self) -> None:
        self.assertIn("three", self.norm)
        for needle in (
            "validate manual-preview output set",
            "generate checksums and build-info manifest",
            "generate and validate release notes",
            "upload manual-preview release assets",
        ):
            with self.subTest(step=needle):
                self.assertIn(needle, self.norm)

    def test_records_workflow_artifact_names(self) -> None:
        for name in WORKFLOW_ARTIFACTS:
            with self.subTest(artifact=name):
                self.assertIn(name, self.text)


class PublishedArtifactTests(unittest.TestCase):
    """Task item 3: the three artifacts are exactly the manual-preview fan rows."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = RESULTS_DOC.read_text(encoding="utf-8")

    def test_doc_names_each_fan_artifact(self) -> None:
        for artifact in FAN_ARTIFACTS:
            with self.subTest(artifact=artifact):
                self.assertTrue(artifact.endswith("-preview.bin"))
                self.assertIn(artifact, self.text)

    def test_doc_bin_tokens_are_exactly_the_allowed_set(self) -> None:
        tokens = set(BIN_TOKEN_RE.findall(self.text))
        self.assertTrue(
            tokens.issubset(ALLOWED_BIN_ARTIFACTS),
            f"doc names unexpected .bin artifact(s): "
            f"{sorted(tokens - ALLOWED_BIN_ARTIFACTS)}",
        )
        self.assertTrue(FAN_ARTIFACTS.issubset(tokens))

    def test_no_triac_bin_is_named(self) -> None:
        for token in BIN_TOKEN_RE.findall(self.text):
            for forbidden in FORBIDDEN_BIN_TOKENS:
                with self.subTest(artifact=token, token=forbidden):
                    self.assertNotIn(forbidden.lower(), token.lower())


class LedgerPublishEvidenceTests(unittest.TestCase):
    """Task item 6: the three fan rows record publish evidence; TRIAC does not."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = _rows_by_cs()
        cls.doc = RESULTS_DOC.read_text(encoding="utf-8")

    def test_each_fan_row_has_success_publish_evidence(self) -> None:
        for cs in FAN_CONFIGS:
            row = self.rows[cs]
            with self.subTest(config_string=cs):
                ev = row.get("publish_evidence")
                self.assertIsInstance(ev, dict, f"{cs}: missing publish_evidence")
                self.assertEqual(ev["run_id"], int(RUN_ID))
                self.assertEqual(ev["conclusion"], "success")
                self.assertEqual(ev["event"], "workflow_dispatch")
                self.assertFalse(ev["dry_run"])
                self.assertIs(ev["webflash_importable"], False)
                self.assertEqual(ev["proof_class"], "firmware-build-release-only")
                self.assertEqual(ev["release_tag"], RELEASE_TAG_USED)
                self.assertTrue(
                    ev["published_artifact_name"].endswith("-preview.bin")
                )

    def test_publish_evidence_claims_no_hardware_or_stable(self) -> None:
        for cs in FAN_CONFIGS:
            ev = self.rows[cs]["publish_evidence"]
            with self.subTest(config_string=cs):
                for claim in (
                    "hardware",
                    "bench-evidence",
                    "compliance",
                    "stable-promotion",
                    "customer-availability",
                ):
                    self.assertIn(claim, ev["not_proof_of"])

    def test_publish_evidence_cross_locks_doc(self) -> None:
        # Each row's published artifact name + asset SHA256 appears in the doc.
        for cs in FAN_CONFIGS:
            ev = self.rows[cs]["publish_evidence"]
            with self.subTest(config_string=cs):
                self.assertIn(ev["published_artifact_name"], self.doc)
                self.assertIn(ev["asset_sha256"], self.doc)

    def test_triac_carries_no_publish_evidence_and_stays_blocked(self) -> None:
        triac = self.rows[TRIAC_CONFIG]
        self.assertNotIn("publish_evidence", triac)
        self.assertFalse(triac["buildable_now"])
        self.assertIn("HW-005", triac["build_blocker"])
        self.assertIsNone(triac["compile_evidence"])

    def test_ledger_still_validates_clean(self) -> None:
        validator = _load_module(VALIDATOR_PATH, "validate_preview_fan_triac_build_rows")
        errors = validator.validate(
            _load_json(LEDGER_PATH),
            _load_json(TARGETS_PATH),
            _load_json(POLICY_PATH),
            _load_json(BUILDS_PATH),
            _load_json(MANUAL_PATH),
        )
        self.assertEqual(errors, [], "\n".join(errors))


class SharedTagAdoptedTests(unittest.TestCase):
    """RELEASE-PREVIEW-FAN-SHARED-TAG-001: v1.0.0-preview is the intended shared
    preview release for room + fan preview artifacts — not a deviation, and no
    dedicated fan tag is expected."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = RESULTS_DOC.read_text(encoding="utf-8")
        cls.norm = _normalise(cls.text)

    def test_shared_preview_tag_is_the_named_release(self) -> None:
        self.assertIn(RELEASE_TAG_USED, self.norm)
        self.assertIn("shared", self.norm)

    def test_shared_tag_not_framed_as_a_deviation(self) -> None:
        # The shared tag is the intended single preview release, not an error /
        # override / deviation.
        for forbidden in ("deviation", "deviates", "operator override"):
            with self.subTest(phrase=forbidden):
                self.assertNotIn(forbidden, self.norm)

    def test_dedicated_fan_tag_is_retired(self) -> None:
        # The dedicated vehicle is named only as retired historical context.
        self.assertIn("retired", self.norm)

    def test_shared_release_holds_room_and_fan_previews(self) -> None:
        # The shared release intentionally co-hosts the four room-bundle previews
        # and the three fan previews.
        self.assertIn("shared", self.norm)
        self.assertIn("room", self.norm)
        self.assertIn("fan", self.norm)
        # The pre-existing room-bundle previews stay attached with SHA256 intact.
        self.assertIn("intact", self.norm)


class SharedReleaseDoesNotImplyWebflashImportTests(unittest.TestCase):
    """Presence in the shared preview release must never imply WebFlash import."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.norm = _normalise(RESULTS_DOC.read_text(encoding="utf-8"))
        cls.rows = _rows_by_cs()

    def test_doc_states_webflash_import_is_controlled_separately(self) -> None:
        self.assertIn("webflash import", self.norm)
        self.assertIn("controlled separately", self.norm)

    def test_fan_rows_stay_not_webflash_importable_on_shared_release(self) -> None:
        for cs in FAN_CONFIGS:
            with self.subTest(config_string=cs):
                ev = self.rows[cs]["publish_evidence"]
                self.assertIs(ev["webflash_importable"], False)
                self.assertEqual(ev["release_tag"], RELEASE_TAG_USED)


class PosturePreservedTests(unittest.TestCase):
    """Task item 5: the preview posture is preserved and nothing is overclaimed."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = RESULTS_DOC.read_text(encoding="utf-8")
        cls.norm = _normalise(cls.text)
        cls.rows = _rows_by_cs()

    def test_preview_not_stable_not_recommended_not_default(self) -> None:
        for needle in (
            "preview",
            "not stable",
            "not recommended",
            "not a customer default",
        ):
            with self.subTest(needle=needle):
                self.assertIn(needle, self.norm)

    def test_fan_products_hidden_and_not_buyable(self) -> None:
        self.assertIn("hidden", self.norm)
        self.assertIn("not buyable", self.norm)

    def test_simple_install_and_launch_sku_unchanged(self) -> None:
        self.assertIn("simple install", self.norm)
        self.assertIn(LAUNCH_SKU, self.text)
        self.assertEqual(
            _load_json(SHOP_PATH)["launch_product"]["shop_sku"], LAUNCH_SKU
        )

    def test_triac_excluded_under_hw005(self) -> None:
        self.assertIn("triac", self.norm)
        self.assertIn("hw-005", self.norm)

    def test_no_hardware_or_compliance_proof_claimed(self) -> None:
        self.assertIn("firmware-build", self.norm)
        self.assertIn("no hardware", self.norm)

    def test_fan_rows_commercial_posture_locked(self) -> None:
        for cs in FAN_CONFIGS:
            p = self.rows[cs]["commercial_posture"]
            with self.subTest(config_string=cs):
                self.assertEqual(p["visibility"], "hidden")
                self.assertFalse(p["buyable"])
                self.assertFalse(p["recommended"])
                self.assertFalse(p["customer_default"])
                self.assertFalse(p["stable"])
                self.assertFalse(p["release_one_required_config"])


class GuardrailTests(unittest.TestCase):
    """Hard guardrails: recording only — no publish / config side effects."""

    def test_no_manifest_or_sources_committed(self) -> None:
        self.assertFalse((REPO_ROOT / "manifest.json").exists())
        self.assertFalse((REPO_ROOT / "firmware" / "sources.json").exists())

    def test_no_bin_committed_anywhere_in_repo(self) -> None:
        bins = [p for p in REPO_ROOT.rglob("*.bin") if ".git" not in p.parts]
        self.assertEqual(bins, [], f"no .bin may be committed; found {bins}")

    def test_no_fan_or_triac_in_webflash_builds(self) -> None:
        config_strings = {b["config_string"] for b in _builds()}
        for cs in FAN_CONFIGS + (TRIAC_CONFIG,):
            with self.subTest(config_string=cs):
                self.assertNotIn(cs, config_strings)

    def test_ledger_still_has_four_rows_no_webflash_row_added(self) -> None:
        ledger = _load_json(LEDGER_PATH)
        self.assertEqual(len(ledger["rows"]), 4)
        self.assertEqual(ledger["totals"]["webflash_builds_rows_added"], 0)

    def test_stable_config_is_not_a_fan_row(self) -> None:
        self.assertNotIn(STABLE_CONFIG, set(FAN_CONFIGS))


class UpcomingPrTests(unittest.TestCase):
    """Task item 7: the queue is updated."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = UPCOMING_PR.read_text(encoding="utf-8")

    def test_publish_run_marked_done(self) -> None:
        run_lines = [ln for ln in self.text.splitlines() if RUN_QUEUE_ID in ln]
        self.assertTrue(run_lines, f"{RUN_QUEUE_ID} not found in UPCOMING_PR.md")
        self.assertTrue(
            any("DONE" in ln for ln in run_lines),
            f"{RUN_QUEUE_ID} is not marked DONE in any heading/line",
        )

    def test_run_id_recorded_in_queue(self) -> None:
        self.assertIn(RUN_ID, self.text)

    def test_results_id_recorded_in_queue(self) -> None:
        self.assertIn(RESULTS_ID, self.text)


if __name__ == "__main__":
    unittest.main(verbosity=2)

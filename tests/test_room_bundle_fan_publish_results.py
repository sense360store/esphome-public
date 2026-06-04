#!/usr/bin/env python3
"""Regression guard for the room-bundle fan firmware PUBLISH RESULTS record.

ROOM-BUNDLE-FAN-PUBLISH-RESULTS-001.

This PR records the **successful** ``Room-Bundle Fan Firmware Publish`` run
(``ROOM-BUNDLE-FAN-PUBLISH-RUN-001``) that published the five full-composition
Bathroom / Kitchen fan-control room-bundle **preview** artifacts
(Bathroom PWM / DAC, Kitchen Relay / DAC / PWM). This guard locks the invariants
the results doc and the per-variant ``publish_evidence`` assert so they cannot
silently regress (matching the task's test list):

  * the results doc records run id ``26947595936``, the workflow name
    ``Room-Bundle Fan Firmware Publish``, the ``workflow_dispatch`` (manual
    dispatch) event, the commit ``ad1d957``, and conclusion ``success``;
  * exactly the five compile-validated room-bundle fan configs are the published
    targets, each a ``-preview.bin``; the only ``Sense360-*.bin`` tokens the doc
    may name are those five plus the stable Bathroom cross-reference, and no
    FanTRIAC / TRIAC ``.bin`` is named;
  * each of the five variants in ``config/room-bundle-fan-variants.json`` carries
    a ``publish_evidence`` block recording run ``26947595936`` / conclusion
    ``success`` / ``webflash_importable: false``, while TRIAC carries **no**
    ``publish_evidence`` and stays build-blocked (``HW-005``);
  * all five remain **preview only** — ``firmware_config_status``
    ``buildable-preview-compile-validated`` / ``preview_status``
    ``preview-compile-validated`` / ``webflash_exposed: false`` — and none is
    stable / recommended / customer-default / buyable;
  * the two FanDAC artifacts record the IC2 ``0x5A`` build override and the
    pending ``FANDAC-I2C-ADDR-001`` bench verification (no hardware proof);
  * the variants source still validates clean
    (``scripts/validate_room_bundle_fan_publish.py`` selects the five with no
    errors — the extra ``publish_evidence`` does not break it);
  * WebFlash import remains **not done** (no fan row in
    ``config/webflash-builds.json``; fan-token guardrail intact);
  * the hard guardrails hold — no ``manifest.json`` / ``firmware/sources.json`` /
    ``.bin`` is committed; and
  * ``UPCOMING_PR.md`` marks ``ROOM-BUNDLE-FAN-PUBLISH-RUN-001`` done and records
    the run id + the results id.

Uses Python's stdlib unittest (matching the no-pytest convention the other
validators in this repo use). Run with::

    python3 tests/test_room_bundle_fan_publish_results.py
"""

from __future__ import annotations

import importlib.util
import json
import re
import unittest
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
VARIANTS_PATH = REPO_ROOT / "config" / "room-bundle-fan-variants.json"
COMPILE_TARGETS_PATH = REPO_ROOT / "config" / "compile-only-targets.json"
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
SHOP_PATH = REPO_ROOT / "config" / "shop-commercial-source-of-truth.json"
RESULTS_DOC = REPO_ROOT / "docs" / "room-bundle-fan-publish-results.md"
UPCOMING_PR = REPO_ROOT / "UPCOMING_PR.md"
VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate_room_bundle_fan_publish.py"

RESULTS_ID = "ROOM-BUNDLE-FAN-PUBLISH-RESULTS-001"
RUN_QUEUE_ID = "ROOM-BUNDLE-FAN-PUBLISH-RUN-001"
WORKFLOW_NAME = "Room-Bundle Fan Firmware Publish"
RUN_ID = 26947595936
COMMIT_SHA = "ad1d957"
RELEASE_TAG_USED = "v1.0.0-preview"
RELEASE_ID = 333373906
LAUNCH_SKU = "S360-KIT-BATH-P"
VERSION = "1.0.0"

# The five compile-validated full-composition room-bundle fan configs.
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

STABLE_CONFIG = "Ceiling-POE-VentIQ-RoomIQ"
STABLE_ARTIFACT = "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin"

# The five durable room-bundle fan preview artifacts this run published.
FAN_ARTIFACTS = {
    f"Sense360-{cs}-v{VERSION}-preview.bin" for cs in ROOM_BUNDLE_FAN_CONFIGS
}
# Every Sense360-*.bin token the results doc may name: the five room-bundle fan
# previews plus the stable Bathroom cross-reference. (The co-mingled room / LED /
# single-driver fan previews are referenced by config string, not by .bin name.)
ALLOWED_BIN_ARTIFACTS = set(FAN_ARTIFACTS) | {STABLE_ARTIFACT}
# Only TRIAC is forbidden as a named .bin (the four fan tokens are expected).
FORBIDDEN_BIN_TOKENS = ("FanTRIAC", "TRIAC")
FAN_FAMILY_TOKENS = ("FanRelay", "FanPWM", "FanDAC", "FanTRIAC")

# The five workflow (CI) artifact names the publish job consumed.
WORKFLOW_ARTIFACTS = (
    "room-bundle-fan-firmware-ceiling-poe-ventiq-fanpwm-roomiq-compile-only",
    "room-bundle-fan-firmware-ceiling-poe-ventiq-fandac-roomiq-compile-only",
    "room-bundle-fan-firmware-ceiling-poe-airiq-fanrelay-roomiq-compile-only",
    "room-bundle-fan-firmware-ceiling-poe-airiq-fandac-roomiq-compile-only",
    "room-bundle-fan-firmware-ceiling-poe-airiq-fanpwm-roomiq-compile-only",
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


def _variants_by_config() -> Dict[str, Dict[str, Any]]:
    data = _load_json(VARIANTS_PATH)
    return {
        v["intended_firmware_config_string"]: v
        for v in data["fan_variant_candidates"]
    }


def _builds() -> List[Dict[str, Any]]:
    return _load_json(BUILDS_PATH)["builds"]


class RunEvidenceTests(unittest.TestCase):
    """The run is recorded faithfully."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = RESULTS_DOC.read_text(encoding="utf-8")
        cls.norm = _normalise(cls.text)

    def test_results_doc_exists_and_is_self_identified(self) -> None:
        self.assertTrue(RESULTS_DOC.is_file())
        self.assertIn(RESULTS_ID, self.text)

    def test_records_run_id_and_workflow_name(self) -> None:
        self.assertIn(str(RUN_ID), self.text)
        self.assertIn(WORKFLOW_NAME, self.text)

    def test_records_workflow_dispatch_not_release_event(self) -> None:
        self.assertIn("workflow_dispatch", self.norm)
        self.assertIn("manual dispatch", self.norm)

    def test_records_commit_branch_and_success_conclusion(self) -> None:
        self.assertIn(COMMIT_SHA, self.text)
        self.assertIn("main", self.norm)
        self.assertIn("success", self.norm)

    def test_records_five_builds_and_attach_steps(self) -> None:
        self.assertIn("five", self.norm)
        for needle in (
            "validate room-bundle fan output set",
            "generate checksums and build-info manifest",
            "generate and validate release notes",
            "upload room-bundle fan release assets",
        ):
            with self.subTest(step=needle):
                self.assertIn(needle, self.norm)

    def test_records_dry_run_job_skipped(self) -> None:
        # dry_run=false ⇒ the dry-run job was skipped (a real publish dispatch).
        self.assertIn("skipped", self.norm)
        self.assertIn("dry_run=false", self.norm.replace(" ", ""))

    def test_records_each_build_job(self) -> None:
        for cs in ROOM_BUNDLE_FAN_CONFIGS:
            with self.subTest(config_string=cs):
                self.assertIn(f"Build room-bundle fan: {cs}", self.text)

    def test_records_workflow_artifact_names(self) -> None:
        for name in WORKFLOW_ARTIFACTS:
            with self.subTest(artifact=name):
                self.assertIn(name, self.text)


class PublishedArtifactTests(unittest.TestCase):
    """The five artifacts are exactly the room-bundle fan configs."""

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


class VariantPublishEvidenceTests(unittest.TestCase):
    """Each of the five variants records run 26947595936 publish evidence;
    TRIAC does not."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.variants = _variants_by_config()
        cls.doc = RESULTS_DOC.read_text(encoding="utf-8")

    def test_each_fan_variant_has_success_publish_evidence(self) -> None:
        for cs in ROOM_BUNDLE_FAN_CONFIGS:
            with self.subTest(config_string=cs):
                ev = self.variants[cs]["firmware_config_evidence"].get(
                    "publish_evidence"
                )
                self.assertIsInstance(ev, dict, f"{cs}: missing publish_evidence")
                self.assertEqual(ev["run_id"], RUN_ID)
                self.assertEqual(ev["conclusion"], "success")
                self.assertEqual(ev["event"], "workflow_dispatch")
                self.assertFalse(ev["dry_run"])
                self.assertEqual(ev["ref"], "main")
                self.assertIs(ev["webflash_importable"], False)
                self.assertEqual(ev["proof_class"], "firmware-build-release-only")
                self.assertEqual(ev["release_tag"], RELEASE_TAG_USED)
                self.assertTrue(
                    ev["published_artifact_name"].endswith("-preview.bin")
                )

    def test_publish_evidence_posture_flags_false(self) -> None:
        for cs in ROOM_BUNDLE_FAN_CONFIGS:
            ev = self.variants[cs]["firmware_config_evidence"]["publish_evidence"]
            with self.subTest(config_string=cs):
                for flag in ("stable", "recommended", "customer_default", "buyable"):
                    self.assertFalse(ev[flag], f"{cs}: {flag} must be false")

    def test_publish_evidence_claims_no_hardware_or_stable(self) -> None:
        for cs in ROOM_BUNDLE_FAN_CONFIGS:
            ev = self.variants[cs]["firmware_config_evidence"]["publish_evidence"]
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
        # Each variant's published artifact name + asset SHA256 appears in the doc.
        for cs in ROOM_BUNDLE_FAN_CONFIGS:
            ev = self.variants[cs]["firmware_config_evidence"]["publish_evidence"]
            with self.subTest(config_string=cs):
                self.assertIn(ev["published_artifact_name"], self.doc)
                self.assertIn(ev["asset_sha256"], self.doc)
                self.assertIn(ev["workflow_artifact_name"], self.doc)

    def test_triac_carries_no_publish_evidence_and_stays_blocked(self) -> None:
        triac = self.variants[TRIAC_CONFIG]
        self.assertNotIn(
            "publish_evidence", triac["firmware_config_evidence"]
        )
        self.assertEqual(
            triac["firmware_config_status"], "defined-build-blocked"
        )
        self.assertFalse(triac["firmware_config_evidence"]["buildable_now"])
        self.assertIn(
            "HW-005", triac["firmware_config_evidence"]["build_blocker"]
        )


class PreviewOnlyPostureTests(unittest.TestCase):
    """All five remain preview only — never stable / recommended / default /
    buyable, never WebFlash-exposed."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.variants = _variants_by_config()

    def test_five_stay_compile_validated_preview(self) -> None:
        for cs in ROOM_BUNDLE_FAN_CONFIGS:
            v = self.variants[cs]
            with self.subTest(config_string=cs):
                self.assertEqual(
                    v["firmware_config_status"],
                    "buildable-preview-compile-validated",
                )
                self.assertEqual(v["preview_status"], "preview-compile-validated")
                self.assertFalse(v["webflash_exposed"])
                self.assertFalse(v["webflash_easy_mode_eligible"])

    def test_five_are_not_stable_recommended_default_buyable(self) -> None:
        for cs in ROOM_BUNDLE_FAN_CONFIGS:
            v = self.variants[cs]
            with self.subTest(config_string=cs):
                self.assertEqual(v["stable_status"], "blocked")
                self.assertFalse(v["recommended"])
                self.assertFalse(v["customer_default"])
                self.assertFalse(v["buyable"])
                self.assertEqual(v["commercial_availability"], "waitlist-only")
                self.assertFalse(v["bench_evidence_claimed"])
                self.assertFalse(v["compliance_claimed"])

    def test_publish_results_record_is_consistent(self) -> None:
        pr = _load_json(VARIANTS_PATH)["publish_results"]
        self.assertEqual(pr["id"], RESULTS_ID)
        self.assertEqual(pr["records_run_followup_id"], RUN_QUEUE_ID)
        self.assertEqual(pr["run_id"], RUN_ID)
        self.assertEqual(pr["workflow"], WORKFLOW_NAME)
        self.assertEqual(pr["ref"], "main")
        self.assertEqual(pr["event"], "workflow_dispatch")
        self.assertFalse(pr["dry_run"])
        self.assertEqual(pr["conclusion"], "success")
        self.assertEqual(pr["result"], "success")
        self.assertEqual(pr["build_count"], 5)
        self.assertEqual(pr["artifact_count"], 5)
        self.assertEqual(pr["dry_run_job"], "skipped")
        for field in (
            "attach_to_release_result",
            "validate_output_set_result",
            "checksums_generated_result",
            "build_info_manifest_generated_result",
            "release_notes_generated_validated_result",
            "release_asset_upload_result",
        ):
            with self.subTest(field=field):
                self.assertEqual(pr[field], "success")
        self.assertEqual(pr["release_tag"], RELEASE_TAG_USED)
        self.assertEqual(pr["release_id"], RELEASE_ID)
        self.assertFalse(pr["stable_or_full_release_promotion"])
        self.assertEqual(pr["proof_scope"], "firmware-build-release-only")
        self.assertEqual(
            sorted(pr["published_config_strings"]),
            sorted(ROOM_BUNDLE_FAN_CONFIGS),
        )
        self.assertEqual(len(pr["published_artifacts"]), 5)


class FanDacPendingTests(unittest.TestCase):
    """The two FanDAC artifacts record the 0x5A build override and pending bench
    verification — no FanDAC hardware proof claimed."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.variants = _variants_by_config()
        cls.norm = _normalise(RESULTS_DOC.read_text(encoding="utf-8"))

    def test_fandac_publish_evidence_records_pending_bench(self) -> None:
        for cs in FANDAC_CONFIGS:
            ev = self.variants[cs]["firmware_config_evidence"]["publish_evidence"]
            with self.subTest(config_string=cs):
                self.assertEqual(
                    ev["fandac_bench_verification_followup"], "FANDAC-I2C-ADDR-001"
                )
                self.assertEqual(ev["fandac_bench_verification_status"], "pending")
                self.assertIn("0x5A", ev["fandac_address_note"])
                self.assertIn("NOT bench verified", ev["fandac_address_note"])

    def test_doc_states_fandac_addresses_and_pending(self) -> None:
        for needle in ("0x58", "0x5a", "0x59", "forbidden", "fandac-i2c-addr-001",
                       "not bench verified", "pending"):
            with self.subTest(needle=needle):
                self.assertIn(needle, self.norm)

    def test_doc_policy_level_fandac_pending(self) -> None:
        policy = _load_json(VARIANTS_PATH)["fan_dac_i2c_address_policy"]
        self.assertEqual(policy["bench_verification_status"], "pending")


class TriacExcludedTests(unittest.TestCase):
    """TRIAC remains excluded / build-blocked (HW-005)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.norm = _normalise(RESULTS_DOC.read_text(encoding="utf-8"))

    def test_triac_out_of_publish_set(self) -> None:
        self.assertNotIn(TRIAC_CONFIG, ROOM_BUNDLE_FAN_CONFIGS)

    def test_doc_marks_triac_excluded_under_hw005(self) -> None:
        self.assertIn("triac", self.norm)
        self.assertIn("hw-005", self.norm)
        self.assertIn("excluded", self.norm)


class SharedReleaseTests(unittest.TestCase):
    """v1.0.0-preview is the intended shared preview release; pre-existing
    previews stay attached with SHA256 intact; presence ≠ WebFlash import."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.norm = _normalise(RESULTS_DOC.read_text(encoding="utf-8"))

    def test_shared_preview_tag_is_named(self) -> None:
        self.assertIn(RELEASE_TAG_USED, self.norm)
        self.assertIn("shared", self.norm)

    def test_dedicated_room_bundle_fan_tag_is_retired(self) -> None:
        self.assertIn("retired", self.norm)

    def test_shared_release_cohosts_room_and_fan_previews_intact(self) -> None:
        self.assertIn("room", self.norm)
        self.assertIn("fan", self.norm)
        self.assertIn("intact", self.norm)

    def test_not_framed_as_a_deviation(self) -> None:
        for forbidden in ("deviation", "deviates", "operator override"):
            with self.subTest(phrase=forbidden):
                self.assertNotIn(forbidden, self.norm)

    def test_doc_states_webflash_import_controlled_separately(self) -> None:
        self.assertIn("webflash import", self.norm)
        self.assertIn("controlled separately", self.norm)


class PosturePreservedTests(unittest.TestCase):
    """The preview posture is preserved and nothing is overclaimed."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = RESULTS_DOC.read_text(encoding="utf-8")
        cls.norm = _normalise(cls.text)

    def test_preview_not_stable_not_recommended_not_default_not_buyable(self) -> None:
        for needle in (
            "preview",
            "not stable",
            "not recommended",
            "not a customer default",
            "not buyable",
        ):
            with self.subTest(needle=needle):
                self.assertIn(needle, self.norm)

    def test_fan_variants_hidden_and_not_buyable(self) -> None:
        self.assertIn("hidden", self.norm)
        self.assertIn("not buyable", self.norm)

    def test_simple_install_and_launch_sku_unchanged(self) -> None:
        self.assertIn("simple install", self.norm)
        self.assertIn(LAUNCH_SKU, self.text)
        shop = _load_json(SHOP_PATH)["launch_product"]
        self.assertEqual(shop["shop_sku"], LAUNCH_SKU)
        self.assertEqual(shop["firmware_config"], STABLE_CONFIG)

    def test_no_hardware_or_compliance_proof_claimed(self) -> None:
        self.assertIn("firmware-build", self.norm)
        self.assertIn("no hardware", self.norm)

    def test_no_positive_status_claim(self) -> None:
        for bad in (
            "is buyable",
            "are buyable",
            "now buyable",
            "becomes buyable",
            "is recommended",
            "are recommended",
            "now recommended",
            "is a customer default",
            "now stable",
            "becomes stable",
            "promoted to stable",
        ):
            with self.subTest(phrase=bad):
                self.assertNotIn(bad, self.norm)


class SourceStillValidatesTests(unittest.TestCase):
    """The extra publish_evidence does not break the publish validator."""

    def test_validator_selects_the_five_with_no_errors(self) -> None:
        script = _load_module(VALIDATOR_PATH, "validate_room_bundle_fan_publish")
        rows, errors = script._select_rows(
            _load_json(VARIANTS_PATH),
            _load_json(COMPILE_TARGETS_PATH),
            _load_json(BUILDS_PATH),
            version=VERSION,
        )
        self.assertEqual(errors, [], "\n".join(errors))
        self.assertEqual(
            [row["config_string"] for row in rows], list(ROOM_BUNDLE_FAN_CONFIGS)
        )


class WebflashImportNotDoneTests(unittest.TestCase):
    """WebFlash import remains not yet done; the fan-token guardrail is intact."""

    def test_five_and_triac_absent_from_webflash_builds(self) -> None:
        config_strings = {b["config_string"] for b in _builds()}
        for cs in ROOM_BUNDLE_FAN_CONFIGS + (TRIAC_CONFIG,):
            with self.subTest(config_string=cs):
                self.assertNotIn(cs, config_strings)

    def test_no_fan_token_in_webflash_builds(self) -> None:
        for cs in {b["config_string"] for b in _builds()}:
            for token in FAN_FAMILY_TOKENS:
                with self.subTest(config_string=cs, token=token):
                    self.assertNotIn(token.lower(), cs.lower())


class HardGuardrailTests(unittest.TestCase):
    """Hard guardrails: recording only — no publish / config side effects."""

    def test_no_manifest_or_sources_committed(self) -> None:
        self.assertFalse((REPO_ROOT / "manifest.json").exists())
        self.assertFalse((REPO_ROOT / "firmware" / "sources.json").exists())

    def test_no_bin_committed_anywhere_in_repo(self) -> None:
        bins = [p for p in REPO_ROOT.rglob("*.bin") if ".git" not in p.parts]
        self.assertEqual(bins, [], f"no .bin may be committed; found {bins}")


class UpcomingPrTests(unittest.TestCase):
    """The queue is updated."""

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

    def test_run_id_and_results_id_recorded(self) -> None:
        self.assertIn(str(RUN_ID), self.text)
        self.assertIn(RESULTS_ID, self.text)


if __name__ == "__main__":
    unittest.main(verbosity=2)

#!/usr/bin/env python3
"""Tests for RELEASE-PREVIEW-FAN-TRIAC-BUILD-ROWS-001.

Locks the invariants of the fan-control / TRIAC PREVIEW build-row ledger
(``config/preview-fan-triac-build-rows.json``), its validator
(``scripts/validate_preview_fan_triac_build_rows.py``), and the four
release-note drafts under ``docs/release-notes/manual-preview/``.

These are policy / metadata / release-note guards. They assert nothing about
firmware behaviour, publish no artifact, and read only committed files. The
invariants match the task contract (item 9):

  * all four targets (FanRelay / FanPWM / FanDAC / FanTRIAC) are preview-eligible;
  * the stable blockers remain recorded;
  * TRIAC is advanced / manual-warning only (advanced-manual-preview lane,
    advanced-preview warning, acknowledgement-gated-advanced, build-blocked by
    HW-005, no compile proof claimed);
  * no target becomes stable / recommended / default;
  * no target enters Simple install (none is in config/webflash-builds.json and
    none is the stable Bathroom config; the launch SKU is unchanged);
  * candidate bundles remain hidden / not buyable;
  * every release-note draft validates against the WebFlash release-body
    contract on the preview channel and carries the required warning copy;
  * every build row / manual-artifact row points to an existing YAML path;
  * no full-release gate is weakened (no WebFlash build row added; scope is
    metadata-only).

Run with::

    python3 tests/test_preview_fan_triac_build_rows.py
"""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER_PATH = REPO_ROOT / "config" / "preview-fan-triac-build-rows.json"
TARGETS_PATH = REPO_ROOT / "config" / "preview-release-targets.json"
POLICY_PATH = REPO_ROOT / "config" / "release-channel-policy.json"
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
MANUAL_PATH = REPO_ROOT / "config" / "manual-firmware-artifacts.json"
SHOP_PATH = REPO_ROOT / "config" / "shop-commercial-source-of-truth.json"
DRAFT_DIR = REPO_ROOT / "docs" / "release-notes" / "manual-preview"
VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate_preview_fan_triac_build_rows.py"
NOTES_VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate-webflash-release-notes.py"

LEDGER_ID = "RELEASE-PREVIEW-FAN-TRIAC-BUILD-ROWS-001"
COMPILE_RUN_ID = 26821900127

FAN_CONFIGS = (
    "Ceiling-POE-VentIQ-FanRelay-RoomIQ",
    "Ceiling-POE-FanPWM",
    "Ceiling-POE-FanDAC",
)
TRIAC_CONFIG = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"
ALL_CONFIGS = FAN_CONFIGS + (TRIAC_CONFIG,)

SIMPLE_INSTALL_CONFIG = "Ceiling-POE-VentIQ-RoomIQ"
SIMPLE_INSTALL_ARTIFACT = "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin"
LAUNCH_SKU = "S360-KIT-BATH-P"

# Warning phrases every draft must state (case-insensitive, whitespace-normalised).
COMMON_PHRASES = (
    "not stable",
    "not recommended",
    "not a customer default",
    "not hardware verified",
    "not compliance certified",
    "not buyable as a public shop product",
    "stable bathroom poe release",
    SIMPLE_INSTALL_ARTIFACT.lower(),
    LAUNCH_SKU.lower(),
    "dry-run draft",
    "not attached to any github release",
)
FAN_PHRASES = (
    "preview firmware",
    "firmware-build proof only",
    str(COMPILE_RUN_ID),
    "no hardware, bench, compliance, or commercial-availability proof",
)
TRIAC_PHRASES = (
    "advanced preview",
    "mains",
    "competent person",
    "manual install",
    "compliance-001",
    "fire, electric shock, or death",
)
FORBIDDEN_AFFIRMATIVE = (
    "is stable",
    "now stable",
    "promoted to stable",
    "is recommended",
    "is the default",
    "production-ready",
    "customer-ready",
)


def _load(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


_VALIDATOR = _load_module(VALIDATOR_PATH, "validate_preview_fan_triac_build_rows")
_NOTES = _load_module(NOTES_VALIDATOR_PATH, "validate_webflash_release_notes_fan_triac")


def _normalise(text: str) -> str:
    import re

    lines = [re.sub(r"^\s*>\s?", "", ln) for ln in text.splitlines()]
    joined = " ".join(lines).replace("`", "")
    return re.sub(r"\s+", " ", joined).lower()


def _draft_path(config_string: str) -> Path:
    return DRAFT_DIR / f"{config_string.lower()}.md"


def _rows_by_cs() -> Dict[str, Dict[str, Any]]:
    return {r["config_string"]: r for r in _load(LEDGER_PATH)["rows"]}


class ValidatorTests(unittest.TestCase):
    """The ledger validates clean and fails closed on drift."""

    def test_ledger_validates_clean(self) -> None:
        errors = _VALIDATOR.validate(
            _load(LEDGER_PATH),
            _load(TARGETS_PATH),
            _load(POLICY_PATH),
            _load(BUILDS_PATH),
            _load(MANUAL_PATH),
        )
        self.assertEqual(errors, [], "\n".join(errors))

    def test_ledger_id_and_scope(self) -> None:
        ledger = _load(LEDGER_PATH)
        self.assertEqual(ledger["id"], LEDGER_ID)
        for flag, val in ledger["scope"].items():
            self.assertFalse(val, f"scope.{flag} must be false")

    def test_validator_rejects_a_webflash_builds_collision(self) -> None:
        # If a fan/TRIAC config ever appears in the WebFlash ledger, validation fails.
        builds = _load(BUILDS_PATH)
        builds["builds"].append({"config_string": TRIAC_CONFIG, "channel": "preview"})
        errors = _VALIDATOR.validate(
            _load(LEDGER_PATH), _load(TARGETS_PATH), _load(POLICY_PATH), builds,
            _load(MANUAL_PATH),
        )
        self.assertNotEqual(errors, [])

    def test_validator_rejects_malformed_triac_compile_proof(self) -> None:
        # After TRIAC-UNBLOCK-BUILD-001 the TRIAC row carries compile evidence,
        # but the validator still rejects a MALFORMED / non-success evidence
        # object (e.g. a bare run_id with no successful result).
        ledger = _load(LEDGER_PATH)
        for row in ledger["rows"]:
            if row["config_string"] == TRIAC_CONFIG:
                row["compile_evidence"] = {"run_id": COMPILE_RUN_ID}
        errors = _VALIDATOR.validate(
            ledger, _load(TARGETS_PATH), _load(POLICY_PATH), _load(BUILDS_PATH),
            _load(MANUAL_PATH),
        )
        self.assertNotEqual(errors, [])

    def test_validator_rejects_triac_build_blocker_reintroduction(self) -> None:
        # The HW-005 build_blocker must stay cleared; reintroducing it fails.
        ledger = _load(LEDGER_PATH)
        for row in ledger["rows"]:
            if row["config_string"] == TRIAC_CONFIG:
                row["build_blocker"] = "HW-005 (reintroduced)"
        errors = _VALIDATOR.validate(
            ledger, _load(TARGETS_PATH), _load(POLICY_PATH), _load(BUILDS_PATH),
            _load(MANUAL_PATH),
        )
        self.assertNotEqual(errors, [])


class PreviewEligibilityTests(unittest.TestCase):
    """Item 9: all four targets are preview-eligible."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = _rows_by_cs()

    def test_all_four_configs_present(self) -> None:
        self.assertEqual(set(self.rows), set(ALL_CONFIGS))

    def test_every_row_is_preview_channel(self) -> None:
        for cs, row in self.rows.items():
            with self.subTest(config_string=cs):
                self.assertEqual(row["build_channel"], "preview")
                self.assertIn(row["channel_tier"], ("preview", "advanced-preview"))
                self.assertTrue(row["expected_preview_artifact_name"].endswith("-preview.bin"))

    def test_every_row_requires_warning_copy(self) -> None:
        policy_warn = _load(POLICY_PATH)["warning_copy"]
        for cs, row in self.rows.items():
            with self.subTest(config_string=cs):
                self.assertIn(row["warning_copy_key"], policy_warn)
                self.assertEqual(row["release_note_warning"], policy_warn[row["warning_copy_key"]])


class StableBlockersRemainTests(unittest.TestCase):
    """Item 9: stable blockers remain (and match the canonical manifest)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = _rows_by_cs()
        cls.targets = {t["target_id"]: t for t in _load(TARGETS_PATH)["targets"]}

    def test_every_row_keeps_a_stable_blocker(self) -> None:
        for cs, row in self.rows.items():
            with self.subTest(config_string=cs):
                self.assertTrue(row["stable_blocker"])

    def test_stable_blocker_matches_preview_release_targets(self) -> None:
        for cs, row in self.rows.items():
            with self.subTest(config_string=cs):
                target = self.targets[row["preview_release_target_id"]]
                self.assertEqual(row["stable_blocker"], target["stable_blocker"])


class TriacAdvancedManualOnlyTests(unittest.TestCase):
    """Item 9: TRIAC is advanced / manual-warning only; buildable (compile-only)
    after TRIAC-UNBLOCK-BUILD-001 cleared the HW-005 BUILDABILITY blocker."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.triac = _rows_by_cs()[TRIAC_CONFIG]

    def test_triac_lane_channel_and_exposure(self) -> None:
        self.assertEqual(self.triac["delivery_lane"], "advanced-manual-preview")
        self.assertEqual(self.triac["channel_tier"], "advanced-preview")
        self.assertEqual(self.triac["warning_copy_key"], "advanced-preview")
        self.assertEqual(
            self.triac["webflash_exposure_class"], "acknowledgement-gated-advanced"
        )
        self.assertFalse(self.triac["webflash_importable"])

    def test_triac_is_buildable_with_compile_proof(self) -> None:
        # TRIAC-UNBLOCK-BUILD-001: HW-005 BUILDABILITY resolved (SX1509-free
        # Core respin; TRI_GPIO1/2 -> IO13/IO14). build_blocker cleared,
        # buildable, with firmware-build compile evidence. Still NOT a
        # manual-firmware-artifacts candidate (advanced-manual-preview lane).
        self.assertTrue(self.triac["buildable_now"])
        self.assertIsNone(self.triac["build_blocker"])
        self.assertIsInstance(self.triac["compile_evidence"], dict)
        self.assertEqual(self.triac["compile_evidence"]["result"], "success")
        self.assertIsNone(self.triac["manual_lane_candidate_id"])

    def test_triac_stable_blocker_keeps_compliance_001(self) -> None:
        # Buildability resolved, but stable stays gated by COMPLIANCE-001.
        self.assertIn("COMPLIANCE-001", self.triac["stable_blocker"])

    def test_triac_warning_copy_is_mains_risk(self) -> None:
        self.assertIn("MAINS", self.triac["release_note_warning"].upper())


class NoStableRecommendedDefaultTests(unittest.TestCase):
    """Item 9: no target becomes stable / recommended / default."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = _rows_by_cs()

    def test_commercial_posture_locked(self) -> None:
        for cs, row in self.rows.items():
            with self.subTest(config_string=cs):
                p = row["commercial_posture"]
                self.assertEqual(p["visibility"], "hidden")
                self.assertFalse(p["buyable"])
                self.assertFalse(p["recommended"])
                self.assertFalse(p["customer_default"])
                self.assertFalse(p["stable"])
                self.assertFalse(p["release_one_required_config"])

    def test_no_row_is_stable_channel(self) -> None:
        for cs, row in self.rows.items():
            with self.subTest(config_string=cs):
                self.assertNotEqual(row["channel_tier"], "stable")
                self.assertNotEqual(row["build_channel"], "stable")


class SimpleInstallUnchangedTests(unittest.TestCase):
    """Item 9: no target enters Simple install; launch SKU unchanged."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = _rows_by_cs()
        cls.builds = _load(BUILDS_PATH)
        cls.shop = _load(SHOP_PATH)

    def test_no_fan_or_triac_in_webflash_builds(self) -> None:
        ledger_cs = {b["config_string"] for b in self.builds["builds"]}
        for cs in ALL_CONFIGS:
            with self.subTest(config_string=cs):
                self.assertNotIn(cs, ledger_cs)

    def test_no_row_is_the_simple_install_config(self) -> None:
        for cs in self.rows:
            self.assertNotEqual(cs, SIMPLE_INSTALL_CONFIG)

    def test_single_stable_webflash_build_is_bathroom(self) -> None:
        stable = [b for b in self.builds["builds"] if b["channel"] == "stable"]
        self.assertEqual(len(stable), 1)
        self.assertEqual(stable[0]["config_string"], SIMPLE_INSTALL_CONFIG)
        self.assertEqual(stable[0]["artifact_name"], SIMPLE_INSTALL_ARTIFACT)

    def test_launch_sku_unchanged(self) -> None:
        launch = self.shop["launch_product"]
        self.assertEqual(launch["shop_sku"], LAUNCH_SKU)
        self.assertEqual(launch["firmware_config"], SIMPLE_INSTALL_CONFIG)
        self.assertEqual(launch["artifact_name"], SIMPLE_INSTALL_ARTIFACT)


class CandidateBundlesHiddenNotBuyableTests(unittest.TestCase):
    """Item 9: candidate bundles remain hidden / not buyable."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = _rows_by_cs()
        cls.shop = _load(SHOP_PATH)

    def test_fan_triac_rows_consume_no_room_bundle(self) -> None:
        for cs, row in self.rows.items():
            with self.subTest(config_string=cs):
                self.assertEqual(row["consuming_bundles"], [])

    def test_shop_guardrails_unchanged(self) -> None:
        g = self.shop["guardrails"]
        self.assertFalse(g["candidate_bundles_buyable"])
        self.assertEqual(g["canonical_room_bundle_sku"], LAUNCH_SKU)
        self.assertFalse(self.shop["candidate_bundle_visibility"]["buy_button_allowed"])


class ReleaseNoteDraftsTests(unittest.TestCase):
    """Item 9: release-note drafts validate and carry the required warning copy."""

    def test_each_draft_exists_and_validates_on_preview(self) -> None:
        for cs in ALL_CONFIGS:
            with self.subTest(config_string=cs):
                path = _draft_path(cs)
                self.assertTrue(path.is_file(), f"missing draft: {path}")
                errors = _NOTES.validate_body(
                    path.read_text(encoding="utf-8"), channel="preview"
                )
                self.assertEqual(errors, [], f"{cs}: {errors}")

    def test_each_draft_has_the_four_required_h2_sections(self) -> None:
        required = {"Changelog", "Known Issues", "Features", "Hardware Requirements"}
        for cs in ALL_CONFIGS:
            with self.subTest(config_string=cs):
                body = _draft_path(cs).read_text(encoding="utf-8")
                sections = _NOTES._parse_sections(body)
                self.assertTrue(required.issubset(sections.keys()))

    def test_common_warning_phrases_present(self) -> None:
        for cs in ALL_CONFIGS:
            norm = _normalise(_draft_path(cs).read_text(encoding="utf-8"))
            for phrase in COMMON_PHRASES:
                with self.subTest(config_string=cs, phrase=phrase):
                    self.assertIn(phrase, norm, f"{cs}: missing {phrase!r}")

    def test_fan_drafts_cite_firmware_build_proof(self) -> None:
        for cs in FAN_CONFIGS:
            norm = _normalise(_draft_path(cs).read_text(encoding="utf-8"))
            for phrase in FAN_PHRASES:
                with self.subTest(config_string=cs, phrase=phrase):
                    self.assertIn(phrase, norm, f"{cs}: missing {phrase!r}")

    def test_triac_draft_states_mains_risk_and_compile_only(self) -> None:
        norm = _normalise(_draft_path(TRIAC_CONFIG).read_text(encoding="utf-8"))
        for phrase in TRIAC_PHRASES:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, norm, f"TRIAC: missing {phrase!r}")
        # TRIAC-UNBLOCK-BUILD-001 used a LOCAL full compile, not the shared
        # hosted fan dry-run run; the TRIAC draft must NOT cite that fan run id.
        self.assertNotIn(str(COMPILE_RUN_ID), norm)
        # Firmware-build compile proof only — no hardware / bench / compliance.
        self.assertIn("compile proof only", norm)
        self.assertIn("not compliance certified", norm)

    def test_no_affirmative_stable_recommended_default_claim(self) -> None:
        for cs in ALL_CONFIGS:
            norm = _normalise(_draft_path(cs).read_text(encoding="utf-8"))
            for bad in FORBIDDEN_AFFIRMATIVE:
                with self.subTest(config_string=cs, phrase=bad):
                    self.assertNotIn(bad, norm, f"{cs}: must not claim {bad!r}")

    def test_draft_self_artifact_is_preview_and_one_stable_crossref(self) -> None:
        rows = _rows_by_cs()
        for cs in ALL_CONFIGS:
            with self.subTest(config_string=cs):
                norm = _normalise(_draft_path(cs).read_text(encoding="utf-8"))
                own = rows[cs]["expected_preview_artifact_name"].lower()
                self.assertTrue(own.endswith("-preview.bin"))
                self.assertIn(own, norm)
                self.assertEqual(
                    norm.count("-stable.bin"),
                    1,
                    f"{cs}: the only -stable.bin must be the Bathroom cross-reference",
                )


class BuildRowsPointToExistingYamlTests(unittest.TestCase):
    """Item 9: build rows / manual-artifact rows point to existing YAML paths."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = _rows_by_cs()
        cls.manual = {c["id"]: c for c in _load(MANUAL_PATH)["candidates"]}

    def test_row_product_yaml_exists(self) -> None:
        for cs, row in self.rows.items():
            with self.subTest(config_string=cs):
                self.assertTrue((REPO_ROOT / row["product_yaml"]).is_file())

    def test_row_release_note_draft_exists(self) -> None:
        for cs, row in self.rows.items():
            with self.subTest(config_string=cs):
                self.assertTrue((REPO_ROOT / row["release_note_draft"]).is_file())

    def test_manual_candidate_rows_point_to_existing_yaml(self) -> None:
        for cid, cand in self.manual.items():
            with self.subTest(candidate=cid):
                self.assertTrue((REPO_ROOT / cand["product_yaml"]).is_file())

    def test_fan_rows_reference_real_manual_candidates(self) -> None:
        for cs in FAN_CONFIGS:
            row = self.rows[cs]
            cand_id = row["manual_lane_candidate_id"]
            with self.subTest(config_string=cs):
                self.assertIn(cand_id, self.manual)
                self.assertEqual(self.manual[cand_id]["product_yaml"], row["product_yaml"])


class NoFullReleaseGateWeakenedTests(unittest.TestCase):
    """Item 9 / hard guardrails: no full-release gate is weakened."""

    def test_no_publish_side_effect_files(self) -> None:
        self.assertFalse((REPO_ROOT / "manifest.json").exists())
        self.assertFalse((REPO_ROOT / "firmware" / "sources.json").exists())

    def test_no_bin_under_draft_dir(self) -> None:
        bins = list(DRAFT_DIR.rglob("*.bin")) if DRAFT_DIR.is_dir() else []
        self.assertEqual(bins, [])

    def test_draft_dir_holds_only_the_four_drafts_and_readme(self) -> None:
        present = sorted(p.name for p in DRAFT_DIR.glob("*.md"))
        expected = sorted(["README.md"] + [f"{cs.lower()}.md" for cs in ALL_CONFIGS])
        self.assertEqual(present, expected)

    def test_ledger_adds_no_webflash_builds_row(self) -> None:
        self.assertEqual(_load(LEDGER_PATH)["totals"]["webflash_builds_rows_added"], 0)

    def test_stable_tier_still_evidence_gated(self) -> None:
        stable = _load(POLICY_PATH)["channel_tiers"]["stable"]
        self.assertTrue(stable["hardware_proof_required"])
        self.assertTrue(stable["evidence_gated"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

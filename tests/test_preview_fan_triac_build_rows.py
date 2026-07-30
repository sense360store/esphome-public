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


DRAFT_INDEX = DRAFT_DIR / "README.md"


def _draft_body(config_string: str) -> str:
    """The config's draft body inside the channel index page.

    REPO-CONSOLIDATION-001 (owner decision of 2026-07-30) collapsed the
    per-config draft files of the advanced/experimental lanes into one
    index page per channel; each former draft body is preserved verbatim
    between ``<!-- draft:<Config-String>:start/end -->`` markers, and
    these guards assert against that slice.
    """
    text = DRAFT_INDEX.read_text(encoding="utf-8")
    start = f"<!-- draft:{config_string}:start -->"
    end = f"<!-- draft:{config_string}:end -->"
    if start not in text or end not in text:
        raise AssertionError(
            f"channel index {DRAFT_INDEX} is missing the marked draft "
            f"section for {config_string}"
        )
    return text.split(start, 1)[1].split(end, 1)[0]


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
            _load(LEDGER_PATH),
            _load(TARGETS_PATH),
            _load(POLICY_PATH),
            builds,
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
            ledger,
            _load(TARGETS_PATH),
            _load(POLICY_PATH),
            _load(BUILDS_PATH),
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
            ledger,
            _load(TARGETS_PATH),
            _load(POLICY_PATH),
            _load(BUILDS_PATH),
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

    def test_every_row_channel_follows_the_build_ledger(self) -> None:
        # ESP-007 (owner decision of 2026-07-28,
        # SENSE360-CANONICALISATION-001): a row whose config has a
        # config/webflash-builds.json row takes that row's channel — the
        # FanRelay / FanTRIAC rows are experimental — and 'preview' stays the
        # default for rows with no build row. The expected artifact suffix
        # follows the same channel, so this ledger can never declare a second
        # artifact name for a config the build ledger already names.
        builds = {
            b["config_string"]: b
            for b in _load(REPO_ROOT / "config" / "webflash-builds.json")["builds"]
        }
        for cs, row in self.rows.items():
            with self.subTest(config_string=cs):
                build_row = builds.get(cs)
                expected_channel = (
                    build_row["channel"] if build_row is not None else "preview"
                )
                self.assertEqual(row["build_channel"], expected_channel)
                self.assertIn(row["channel_tier"], ("preview", "advanced-preview"))
                self.assertTrue(
                    row["expected_preview_artifact_name"].endswith(
                        f"-{expected_channel}.bin"
                    )
                )

    def test_every_row_requires_warning_copy(self) -> None:
        policy_warn = _load(POLICY_PATH)["warning_copy"]
        for cs, row in self.rows.items():
            with self.subTest(config_string=cs):
                self.assertIn(row["warning_copy_key"], policy_warn)
                self.assertEqual(
                    row["release_note_warning"], policy_warn[row["warning_copy_key"]]
                )


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
        # Core respin; TRI_GPIO1/2 -> IO14/IO13, corrected by
        # TRIAC-PINMAP-CORRECT-001). build_blocker cleared,
        # buildable, with firmware-build compile evidence. Still NOT a
        # manual-firmware-artifacts candidate (advanced-manual-preview lane).
        self.assertTrue(self.triac["buildable_now"])
        self.assertIsNone(self.triac["build_blocker"])
        self.assertIsInstance(self.triac["compile_evidence"], dict)
        self.assertEqual(self.triac["compile_evidence"]["result"], "success")
        self.assertIsNone(self.triac["manual_lane_candidate_id"])

    def test_triac_stable_blocker_keeps_compliance_001(self) -> None:
        # Buildability resolved; the stable_blocker must keep citing the
        # COMPLIANCE-001 gate element. Per COMPLIANCE-001-RESOLUTION-001 the
        # citation now points at the experimental-lane preconditions
        # (COMPLIANCE-001 closed by posture) — the resolution id carries the
        # COMPLIANCE-001 substring, and the enforced behaviour is unchanged.
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

    def test_fans_in_webflash_builds_on_their_lanes_never_stable(self) -> None:
        # HW-RELEASE-001 (docs/hw-release-001.md): the fan drivers are
        # admitted to the WebFlash build matrix on their non-stable lanes
        # only — FanPWM / FanDAC on 'preview', FanRelay on 'experimental'
        # (mains-adjacent lane per COMPLIANCE-001). FanTRIAC stays admitted
        # only on the experimental self-build mains channel
        # (TRIAC-COMMISSIONING-001). No fan/TRIAC row is ever stable.
        ledger_cs = {b["config_string"]: b for b in self.builds["builds"]}
        for cs in FAN_CONFIGS:
            with self.subTest(config_string=cs):
                self.assertIn(cs, ledger_cs)
                channel = ledger_cs[cs]["channel"]
                self.assertNotEqual(channel, "stable")
                if "FanRelay" in cs:
                    self.assertEqual(channel, "experimental")
                else:
                    self.assertEqual(channel, "preview")
        self.assertIn(TRIAC_CONFIG, ledger_cs)
        self.assertEqual(ledger_cs[TRIAC_CONFIG]["channel"], "experimental")

    def test_no_row_is_the_simple_install_config(self) -> None:
        for cs in self.rows:
            self.assertNotEqual(cs, SIMPLE_INSTALL_CONFIG)

    def test_simple_install_stable_build_is_bathroom(self) -> None:
        # STABLE-PROMOTION-RECONCILE-001: the ledger now carries three stable
        # rows (Release-One + the promoted Bedroom/Kitchen bundles), but
        # Simple install still resolves to the stable Bathroom build only and
        # no fan/TRIAC row is ever stable.
        stable = {
            b["config_string"]: b
            for b in self.builds["builds"]
            if b["channel"] == "stable"
        }
        self.assertIn(SIMPLE_INSTALL_CONFIG, stable)
        for cs in stable:
            for token in (*FAN_CONFIGS, TRIAC_CONFIG):
                self.assertNotEqual(cs, token)
        self.assertEqual(
            stable[SIMPLE_INSTALL_CONFIG]["artifact_name"],
            self.shop["launch_product"]["artifact_name"],
            "the shop launch artifact must mirror the stable Bathroom build",
        )

    def test_launch_sku_unchanged(self) -> None:
        launch = self.shop["launch_product"]
        self.assertEqual(launch["shop_sku"], LAUNCH_SKU)
        self.assertEqual(launch["firmware_config"], SIMPLE_INSTALL_CONFIG)
        self.assertTrue(launch["artifact_name"].endswith("-stable.bin"))


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
        self.assertTrue(DRAFT_INDEX.is_file(), f"missing index: {DRAFT_INDEX}")
        for cs in ALL_CONFIGS:
            with self.subTest(config_string=cs):
                errors = _NOTES.validate_body(_draft_body(cs), channel="preview")
                self.assertEqual(errors, [], f"{cs}: {errors}")

    def test_each_draft_has_the_four_required_h2_sections(self) -> None:
        required = {"Changelog", "Known Issues", "Features", "Hardware Requirements"}
        for cs in ALL_CONFIGS:
            with self.subTest(config_string=cs):
                body = _draft_body(cs)
                sections = _NOTES._parse_sections(body)
                self.assertTrue(required.issubset(sections.keys()))

    def test_common_warning_phrases_present(self) -> None:
        for cs in ALL_CONFIGS:
            norm = _normalise(_draft_body(cs))
            for phrase in COMMON_PHRASES:
                with self.subTest(config_string=cs, phrase=phrase):
                    self.assertIn(phrase, norm, f"{cs}: missing {phrase!r}")

    def test_fan_drafts_cite_firmware_build_proof(self) -> None:
        for cs in FAN_CONFIGS:
            norm = _normalise(_draft_body(cs))
            for phrase in FAN_PHRASES:
                with self.subTest(config_string=cs, phrase=phrase):
                    self.assertIn(phrase, norm, f"{cs}: missing {phrase!r}")

    def test_triac_draft_states_mains_risk_and_compile_only(self) -> None:
        norm = _normalise(_draft_body(TRIAC_CONFIG))
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
            norm = _normalise(_draft_body(cs))
            for bad in FORBIDDEN_AFFIRMATIVE:
                with self.subTest(config_string=cs, phrase=bad):
                    self.assertNotIn(bad, norm, f"{cs}: must not claim {bad!r}")

    def test_draft_self_artifact_is_preview_and_one_stable_crossref(self) -> None:
        for cs in ALL_CONFIGS:
            with self.subTest(config_string=cs):
                norm = _normalise(_draft_body(cs))
                # The committed drafts are the HISTORICAL v1.0.0-preview
                # drafting records. The FanRelay / FanTRIAC rows' forward
                # declarations moved to the experimental channel (owner
                # decision of 2026-07-28, SENSE360-CANONICALISATION-001), but
                # the drafts themselves are unchanged history, so the
                # assertion pins the drafted name rather than the row's
                # current forward-looking field.
                own = f"sense360-{cs}-v1.0.0-preview.bin".lower()
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
                self.assertEqual(
                    self.manual[cand_id]["product_yaml"], row["product_yaml"]
                )


class NoFullReleaseGateWeakenedTests(unittest.TestCase):
    """Item 9 / hard guardrails: no full-release gate is weakened."""

    def test_no_publish_side_effect_files(self) -> None:
        self.assertFalse((REPO_ROOT / "manifest.json").exists())
        self.assertFalse((REPO_ROOT / "firmware" / "sources.json").exists())

    def test_no_bin_under_draft_dir(self) -> None:
        bins = list(DRAFT_DIR.rglob("*.bin")) if DRAFT_DIR.is_dir() else []
        self.assertEqual(bins, [])

    def test_draft_dir_holds_only_the_channel_index(self) -> None:
        # REPO-CONSOLIDATION-001: one index page per advanced/experimental
        # channel; every former per-config draft lives inside it, marked.
        present = sorted(p.name for p in DRAFT_DIR.glob("*.md"))
        self.assertEqual(present, ["README.md"])
        text = DRAFT_INDEX.read_text(encoding="utf-8")
        for cs in ALL_CONFIGS:
            self.assertIn(f"<!-- draft:{cs}:start -->", text)

    def test_ledger_adds_no_webflash_builds_row(self) -> None:
        self.assertEqual(_load(LEDGER_PATH)["totals"]["webflash_builds_rows_added"], 0)

    def test_stable_tier_still_evidence_gated(self) -> None:
        stable = _load(POLICY_PATH)["channel_tiers"]["stable"]
        self.assertTrue(stable["hardware_proof_required"])
        self.assertTrue(stable["evidence_gated"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

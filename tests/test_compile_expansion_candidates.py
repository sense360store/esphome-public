#!/usr/bin/env python3
"""Tests for the compile-only expansion candidate ledger (FW-COMPILE-EXPAND-001).

Covers the candidate list at ``config/compile-only-candidates.json``
(formerly also documented at ``docs/compile-only-expansion-candidates.md``,
archived under DOCS-DISPOSITION-001; see ``docs/archive-index.md``).
The candidate ledger is a planning document only; these tests pin the
structural invariants and the guardrails that no candidate implies a
compile-only target add, WebFlash exposure, stable promotion, hardware
proof, or release readiness.

Uses Python's stdlib unittest (matching this repo's no-pytest
convention for Python validators). Run with::

    python3 tests/test_compile_expansion_candidates.py

or::

    python3 -m unittest tests.test_compile_expansion_candidates -v
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

CANDIDATES_PATH = REPO_ROOT / "config" / "compile-only-candidates.json"
COMPILE_ONLY_TARGETS_PATH = REPO_ROOT / "config" / "compile-only-targets.json"
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
MATRIX_PATH = REPO_ROOT / "config" / "firmware-combination-matrix.json"
ARCHIVE_INDEX = REPO_ROOT / "docs" / "archive-index.md"

# The currently release-eligible WebFlash builds. A candidate row whose
# ``would_be_webflash_exposed_now=false`` flag is true is allowed to
# share a config_string with one of these only because they are
# already-shipping (and this candidate ledger never adds them).
# RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001 added the three room-bundle preview
# build rows (Ceiling-POE-AirIQ-RoomIQ, Ceiling-POE-RoomIQ,
# Ceiling-POE-RoomIQ-LED) alongside the stable RoomIQ and the VentIQ LED preview.
CURRENTLY_SHIPPING_CONFIG_STRINGS = frozenset(
    {
        "Ceiling-POE-VentIQ-RoomIQ",
        "Ceiling-POE-VentIQ-RoomIQ-LED",
        "Ceiling-POE-AirIQ-RoomIQ",
        "Ceiling-POE-RoomIQ",
        "Ceiling-POE-RoomIQ-LED",
    }
)

ALLOWED_CANDIDATE_STATUSES = frozenset(
    {
        "ready-for-product-yaml",
        "needs-product-yaml",
        "blocked-package",
        "blocked-core-bus",
        "blocked-hardware",
        "blocked-compliance",
        "defer",
    }
)

ALLOWED_LANES = frozenset(
    {
        "poe-non-fan",
        "poe-non-fan-led",
        "usb-non-fan",
        "usb-non-fan-led",
        "pwr",
        "fanrelay",
        "fanpwm",
        "fandac",
        "fantriac",
    }
)

NON_BLOCKED_LANES = frozenset(
    {
        "poe-non-fan",
        "poe-non-fan-led",
        "usb-non-fan",
        "usb-non-fan-led",
    }
)

BLOCKED_LANES = frozenset(
    {
        "pwr",
        "fanrelay",
        "fanpwm",
        "fandac",
        "fantriac",
    }
)

# Fields each candidate must declare. would_be_webflash_exposed_now is
# part of the schema so a future row that accidentally claims WebFlash
# exposure surfaces here, not in webflash-builds.json.
REQUIRED_CANDIDATE_FIELDS = {
    "config_string",
    "rank",
    "lane",
    "use_case",
    "proposed_product_yaml",
    "candidate_status",
    "reason",
    "blockers",
    "would_be_webflash_exposed_now",
    "compile_only_safe",
}

# Fields that must NOT appear on a candidate row. These are owned by
# real shipment manifests, not by this planning ledger.
FORBIDDEN_CANDIDATE_FIELDS = {
    "artifact_name",
    "webflash_build_matrix",
    "webflash_wrapper",
    "release_ready",
    "stable_ready",
    "preview_ready",
    "hardware_proof",
    "hardware_validated",
    "release_007_unblocked",
}

# Tokens used by the WebFlash config-string grammar.
PWR_TOKEN = "PWR"
FANTRIAC_TOKEN = "FanTRIAC"
FANRELAY_TOKEN = "FanRelay"
FANPWM_TOKEN = "FanPWM"
FANDAC_TOKEN = "FanDAC"

# Blocker name substrings asserted on the fan / PWR deferral rows.
CORE_BUS_BLOCKER_SUBSTRINGS = (
    "CORE-ABSTRACT-BUS-001A",
    "CORE-ABSTRACT-BUS-001B",
    "CORE-ABSTRACT-BUS-001C",
)
PACKAGE_RELAY_BLOCKER_SUBSTRING = "PACKAGE-RELAY-001"
PACKAGE_PWM_BLOCKER_SUBSTRING = "PACKAGE-PWM-001"
PACKAGE_DAC_BLOCKER_SUBSTRING = "PACKAGE-DAC-001"
COMPLIANCE_BLOCKER_SUBSTRING = "COMPLIANCE-001"
HW_005_BLOCKER_SUBSTRING = "HW-005"


def _load(path: Path):
    return json.loads(path.read_text())


def _tokens(config_string: str) -> set:
    if not config_string:
        return set()
    return set(config_string.split("-"))


class CandidatesShapeTests(unittest.TestCase):
    """Shape / schema invariants of the candidate ledger."""

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(CANDIDATES_PATH)
        cls.candidates = cls.doc["candidates"]

    def test_schema_version_is_one(self):
        self.assertEqual(self.doc["schema_version"], 1)

    def test_sources_point_to_canonical_files(self):
        sources = self.doc.get("sources", {})
        self.assertEqual(
            sources.get("compile_only_targets"),
            "config/compile-only-targets.json",
        )
        self.assertEqual(
            sources.get("webflash_builds"),
            "config/webflash-builds.json",
        )
        self.assertEqual(
            sources.get("firmware_combination_matrix"),
            "config/firmware-combination-matrix.json",
        )
        self.assertEqual(
            sources.get("firmware_build_gap_report"),
            "docs/firmware-build-gap-report.md",
        )

    def test_candidate_list_is_non_empty(self):
        self.assertGreater(len(self.candidates), 0)

    def test_every_candidate_has_required_fields(self):
        for cand in self.candidates:
            missing = REQUIRED_CANDIDATE_FIELDS - set(cand.keys())
            self.assertFalse(
                missing,
                f"candidate {cand.get('config_string')!r} missing fields {missing}",
            )

    def test_no_candidate_declares_forbidden_shipment_fields(self):
        for cand in self.candidates:
            present_forbidden = FORBIDDEN_CANDIDATE_FIELDS & set(cand.keys())
            self.assertFalse(
                present_forbidden,
                f"candidate {cand.get('config_string')!r} declares forbidden "
                f"shipment fields {sorted(present_forbidden)} — those fields "
                "are owned by config/webflash-builds.json / "
                "config/product-catalog.json, not by this planning ledger",
            )

    def test_candidate_statuses_are_allowed(self):
        for cand in self.candidates:
            self.assertIn(
                cand["candidate_status"],
                ALLOWED_CANDIDATE_STATUSES,
                f"{cand['config_string']!r}: bad candidate_status",
            )

    def test_candidate_lanes_are_allowed(self):
        for cand in self.candidates:
            self.assertIn(
                cand["lane"],
                ALLOWED_LANES,
                f"{cand['config_string']!r}: bad lane",
            )

    def test_allowed_status_field_is_consistent(self):
        declared = set(self.doc.get("allowed_candidate_statuses") or [])
        self.assertEqual(declared, ALLOWED_CANDIDATE_STATUSES)

    def test_allowed_lanes_field_is_consistent(self):
        declared = set(self.doc.get("allowed_lanes") or [])
        self.assertEqual(declared, ALLOWED_LANES)

    def test_non_blocked_lanes_field_is_consistent(self):
        declared = set(self.doc.get("non_blocked_lanes") or [])
        self.assertEqual(declared, NON_BLOCKED_LANES)

    def test_blocked_lanes_field_is_consistent(self):
        declared = set(self.doc.get("blocked_lanes") or [])
        self.assertEqual(declared, BLOCKED_LANES)

    def test_totals_match_candidates_length(self):
        totals = self.doc.get("totals") or {}
        self.assertEqual(totals.get("candidates"), len(self.candidates))

    def test_totals_by_lane_match_actual_counts(self):
        totals = self.doc.get("totals") or {}
        by_lane = totals.get("by_lane") or {}
        actual = {}
        for cand in self.candidates:
            actual[cand["lane"]] = actual.get(cand["lane"], 0) + 1
        self.assertEqual(by_lane, actual)

    def test_config_strings_are_unique(self):
        configs = [c["config_string"] for c in self.candidates]
        self.assertEqual(
            len(configs),
            len(set(configs)),
            "duplicate config_string in candidate list",
        )

    def test_ranks_are_unique_positive_integers(self):
        ranks = [c["rank"] for c in self.candidates]
        for r in ranks:
            self.assertIsInstance(r, int, f"rank must be int, got {type(r)}")
            self.assertGreater(r, 0, f"rank must be > 0, got {r}")
        self.assertEqual(len(ranks), len(set(ranks)), "duplicate rank value")

    def test_blockers_is_a_list_of_strings(self):
        for cand in self.candidates:
            blockers = cand["blockers"]
            self.assertIsInstance(
                blockers,
                list,
                f"{cand['config_string']!r}: blockers must be a list",
            )
            for b in blockers:
                self.assertIsInstance(
                    b,
                    str,
                    f"{cand['config_string']!r}: blocker entries must be str",
                )

    def test_compile_only_safe_is_bool(self):
        for cand in self.candidates:
            self.assertIsInstance(
                cand["compile_only_safe"],
                bool,
                f"{cand['config_string']!r}: compile_only_safe must be bool",
            )

    def test_would_be_webflash_exposed_now_is_always_false(self):
        for cand in self.candidates:
            self.assertFalse(
                cand["would_be_webflash_exposed_now"],
                f"{cand['config_string']!r}: would_be_webflash_exposed_now "
                "must be false for every candidate — this ledger does not "
                "add WebFlash exposure",
            )

    def test_proposed_product_yaml_is_under_products_or_compile_only(self):
        for cand in self.candidates:
            yaml_path = cand["proposed_product_yaml"]
            self.assertIsInstance(yaml_path, str)
            self.assertTrue(
                yaml_path.startswith("products/"),
                f"{cand['config_string']!r}: proposed_product_yaml must be "
                f"under products/, got {yaml_path!r}",
            )
            self.assertFalse(
                yaml_path.startswith("products/webflash/"),
                f"{cand['config_string']!r}: proposed_product_yaml must NOT "
                "be under products/webflash/ — that directory is the "
                "WebFlash wrapper namespace, not the compile-only namespace",
            )


class CandidatesCrossRefTests(unittest.TestCase):
    """Cross-references against the source matrix and the build matrix."""

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(CANDIDATES_PATH)
        cls.candidates = cls.doc["candidates"]
        cls.builds = _load(BUILDS_PATH)
        cls.matrix = _load(MATRIX_PATH)
        cls.committed_configs = {
            entry["config_string"]
            for entry in (cls.builds.get("builds", []) or [])
            if entry.get("config_string")
        }
        cls.matrix_configs = {
            row["config_string"]
            for row in (cls.matrix.get("combinations", []) or [])
            if row.get("config_string")
        }

    def test_every_candidate_config_string_exists_in_firmware_matrix(self):
        for cand in self.candidates:
            self.assertIn(
                cand["config_string"],
                self.matrix_configs,
                f"candidate {cand['config_string']!r}: config_string not "
                "present in config/firmware-combination-matrix.json",
            )

    def test_no_candidate_appears_in_webflash_builds_unless_already_shipping(self):
        for cand in self.candidates:
            cs = cand["config_string"]
            if cand["would_be_webflash_exposed_now"]:
                continue
            if cs in self.committed_configs:
                self.assertIn(
                    cs,
                    CURRENTLY_SHIPPING_CONFIG_STRINGS,
                    f"candidate {cs!r}: would_be_webflash_exposed_now is "
                    "false but the config_string is committed in "
                    "config/webflash-builds.json AND is not one of the two "
                    "currently shipping builds — this ledger must not "
                    "shadow an existing WebFlash build",
                )

    def test_currently_shipping_field_matches_actual_builds(self):
        declared = set(self.doc.get("currently_shipping_config_strings") or [])
        self.assertEqual(
            declared,
            CURRENTLY_SHIPPING_CONFIG_STRINGS,
            "currently_shipping_config_strings drifted from the test's "
            "frozen list of the two shipping builds",
        )
        self.assertTrue(
            declared.issubset(self.committed_configs),
            "currently_shipping_config_strings must be a subset of the "
            "configs actually committed to config/webflash-builds.json",
        )

    def test_currently_compile_only_field_matches_compile_only_targets(self):
        declared = set(self.doc.get("currently_compile_only_config_strings") or [])
        targets = _load(COMPILE_ONLY_TARGETS_PATH).get("targets", [])
        actual = {t["config_string"] for t in targets if t.get("config_string")}
        self.assertEqual(
            declared,
            actual,
            "currently_compile_only_config_strings drifted from "
            "config/compile-only-targets.json — update the ledger and the "
            "doc together",
        )


class CandidatesGuardrailTests(unittest.TestCase):
    """Guardrails: no candidate implies WebFlash / stable / release readiness."""

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(CANDIDATES_PATH)
        cls.candidates = cls.doc["candidates"]

    def test_no_pwr_candidate_is_compile_only_safe(self):
        for cand in self.candidates:
            if PWR_TOKEN not in _tokens(cand["config_string"]):
                continue
            self.assertFalse(
                cand["compile_only_safe"],
                f"candidate {cand['config_string']!r}: PWR-bearing "
                "candidate must NOT claim compile_only_safe=true; the "
                "COMPLIANCE-001-RESOLUTION-001 experimental-lane "
                "preconditions for S360-400 are not met (COMPLIANCE-001 "
                "closed by posture; deferral behaviour unchanged)",
            )

    def test_every_pwr_candidate_carries_compliance_blocker(self):
        for cand in self.candidates:
            if PWR_TOKEN not in _tokens(cand["config_string"]):
                continue
            joined = " ".join(cand["blockers"])
            self.assertIn(
                COMPLIANCE_BLOCKER_SUBSTRING,
                joined,
                f"candidate {cand['config_string']!r}: PWR-bearing "
                f"candidate must list a COMPLIANCE-001 blocker; got "
                f"{cand['blockers']!r}",
            )

    def test_no_fantriac_candidate_is_compile_only_safe(self):
        for cand in self.candidates:
            if FANTRIAC_TOKEN not in _tokens(cand["config_string"]):
                continue
            self.assertFalse(
                cand["compile_only_safe"],
                f"candidate {cand['config_string']!r}: FanTRIAC-bearing "
                "candidate must NOT claim compile_only_safe=true; the "
                "PACKAGE-TRIAC-001 attestation and the "
                "COMPLIANCE-001-RESOLUTION-001 experimental-lane move "
                "(commissioning PR) have not landed",
            )

    def test_every_fantriac_candidate_carries_hw005_and_compliance_blockers(self):
        for cand in self.candidates:
            if FANTRIAC_TOKEN not in _tokens(cand["config_string"]):
                continue
            joined = " ".join(cand["blockers"])
            self.assertIn(
                HW_005_BLOCKER_SUBSTRING,
                joined,
                f"candidate {cand['config_string']!r}: FanTRIAC-bearing "
                f"candidate must list an HW-005 blocker; got "
                f"{cand['blockers']!r}",
            )
            self.assertIn(
                COMPLIANCE_BLOCKER_SUBSTRING,
                joined,
                f"candidate {cand['config_string']!r}: FanTRIAC-bearing "
                f"candidate must list a COMPLIANCE-001 blocker; got "
                f"{cand['blockers']!r}",
            )

    def test_every_fanrelay_candidate_carries_required_blockers(self):
        """FanRelay candidates must list both a package and a core-bus blocker."""
        for cand in self.candidates:
            if FANRELAY_TOKEN not in _tokens(cand["config_string"]):
                continue
            joined = " ".join(cand["blockers"])
            self.assertIn(
                PACKAGE_RELAY_BLOCKER_SUBSTRING,
                joined,
                f"candidate {cand['config_string']!r}: FanRelay candidate "
                f"must list a PACKAGE-RELAY-001 blocker; got "
                f"{cand['blockers']!r}",
            )
            self.assertTrue(
                any(sub in joined for sub in CORE_BUS_BLOCKER_SUBSTRINGS),
                f"candidate {cand['config_string']!r}: FanRelay candidate "
                f"must list at least one CORE-ABSTRACT-BUS-001A / 001B / "
                f"001C blocker; got {cand['blockers']!r}",
            )
            self.assertFalse(
                cand["compile_only_safe"],
                f"candidate {cand['config_string']!r}: FanRelay candidate "
                "must NOT claim compile_only_safe=true",
            )

    def test_every_fanpwm_candidate_carries_required_blockers(self):
        """FanPWM candidates must list a package and a core-bus blocker."""
        for cand in self.candidates:
            if FANPWM_TOKEN not in _tokens(cand["config_string"]):
                continue
            joined = " ".join(cand["blockers"])
            self.assertIn(
                PACKAGE_PWM_BLOCKER_SUBSTRING,
                joined,
                f"candidate {cand['config_string']!r}: FanPWM candidate "
                f"must list a PACKAGE-PWM-001 blocker; got "
                f"{cand['blockers']!r}",
            )
            self.assertTrue(
                any(sub in joined for sub in CORE_BUS_BLOCKER_SUBSTRINGS),
                f"candidate {cand['config_string']!r}: FanPWM candidate "
                f"must list at least one CORE-ABSTRACT-BUS-001A / 001B / "
                f"001C blocker; got {cand['blockers']!r}",
            )
            self.assertFalse(
                cand["compile_only_safe"],
                f"candidate {cand['config_string']!r}: FanPWM candidate "
                "must NOT claim compile_only_safe=true",
            )

    def test_every_fandac_candidate_carries_required_blockers(self):
        """FanDAC candidates must list a package and a core-bus blocker."""
        for cand in self.candidates:
            if FANDAC_TOKEN not in _tokens(cand["config_string"]):
                continue
            joined = " ".join(cand["blockers"])
            self.assertIn(
                PACKAGE_DAC_BLOCKER_SUBSTRING,
                joined,
                f"candidate {cand['config_string']!r}: FanDAC candidate "
                f"must list a PACKAGE-DAC-001 blocker; got "
                f"{cand['blockers']!r}",
            )
            self.assertTrue(
                any(sub in joined for sub in CORE_BUS_BLOCKER_SUBSTRINGS),
                f"candidate {cand['config_string']!r}: FanDAC candidate "
                f"must list at least one CORE-ABSTRACT-BUS-001A / 001B / "
                f"001C blocker; got {cand['blockers']!r}",
            )
            self.assertFalse(
                cand["compile_only_safe"],
                f"candidate {cand['config_string']!r}: FanDAC candidate "
                "must NOT claim compile_only_safe=true",
            )

    def test_no_candidate_claims_release_readiness_or_hardware_proof(self):
        """No candidate may carry release-ready / hardware-proof markers.

        This guards against a future candidate row accidentally
        claiming readiness that lives in the per-slice evidence trail.
        """
        for cand in self.candidates:
            for forbidden_key in FORBIDDEN_CANDIDATE_FIELDS:
                self.assertNotIn(
                    forbidden_key,
                    cand,
                    f"candidate {cand['config_string']!r}: must not "
                    f"declare {forbidden_key!r}; release / hardware "
                    "readiness is not owned by this planning ledger",
                )
            blockers_text = " ".join(cand.get("blockers", []))
            reason = cand.get("reason", "")
            notes = cand.get("notes", "") or ""
            for forbidden_phrase in (
                "release-ready",
                "release ready",
                "hardware-proof exists",
                "hardware proof exists",
                "RELEASE-007 unblocked",
                "RELEASE-007 closed",
            ):
                self.assertNotIn(
                    forbidden_phrase.lower(),
                    reason.lower(),
                    f"candidate {cand['config_string']!r}: reason text "
                    f"must not claim {forbidden_phrase!r}",
                )
                self.assertNotIn(
                    forbidden_phrase.lower(),
                    notes.lower(),
                    f"candidate {cand['config_string']!r}: notes text "
                    f"must not claim {forbidden_phrase!r}",
                )
                self.assertNotIn(
                    forbidden_phrase.lower(),
                    blockers_text.lower(),
                    f"candidate {cand['config_string']!r}: blockers text "
                    f"must not claim {forbidden_phrase!r}",
                )

    def test_blocked_lane_candidates_are_not_compile_only_safe(self):
        for cand in self.candidates:
            if cand["lane"] not in BLOCKED_LANES:
                continue
            self.assertFalse(
                cand["compile_only_safe"],
                f"candidate {cand['config_string']!r}: blocked-lane "
                f"candidate (lane={cand['lane']!r}) must NOT claim "
                "compile_only_safe=true",
            )


class CandidatesRankingTests(unittest.TestCase):
    """POE / USB non-fan candidates must be ranked ahead of blocked lanes."""

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(CANDIDATES_PATH)
        cls.candidates = cls.doc["candidates"]

    def test_non_blocked_lanes_ranked_strictly_ahead_of_blocked_lanes(self):
        non_blocked_ranks = [
            c["rank"] for c in self.candidates if c["lane"] in NON_BLOCKED_LANES
        ]
        blocked_ranks = [
            c["rank"] for c in self.candidates if c["lane"] in BLOCKED_LANES
        ]
        self.assertGreater(
            len(non_blocked_ranks),
            0,
            "expected at least one non-blocked candidate "
            "(POE / USB non-fan or LED preview)",
        )
        self.assertGreater(
            len(blocked_ranks),
            0,
            "expected at least one blocked-lane candidate " "(PWR / fan deferral)",
        )
        self.assertLess(
            max(non_blocked_ranks),
            min(blocked_ranks),
            "non-blocked lanes (POE / USB non-fan +/- LED) must rank "
            "strictly ahead of blocked lanes (PWR / FanRelay / FanPWM / "
            f"FanDAC / FanTRIAC): max non-blocked rank "
            f"{max(non_blocked_ranks)} must be < min blocked rank "
            f"{min(blocked_ranks)}",
        )

    def test_poe_non_fan_lane_present_and_ranked_first(self):
        poe_non_fan_ranks = [
            c["rank"] for c in self.candidates if c["lane"] == "poe-non-fan"
        ]
        self.assertGreater(
            len(poe_non_fan_ranks),
            0,
            "expected at least one poe-non-fan candidate "
            "(already-compile-only ranking anchor)",
        )
        all_ranks = [c["rank"] for c in self.candidates]
        self.assertEqual(
            min(poe_non_fan_ranks),
            min(all_ranks),
            "poe-non-fan lane must include the lowest (highest-priority) "
            "rank in the ledger",
        )


class CandidatesDocArchivedTests(unittest.TestCase):
    """The companion doc was archived under DOCS-DISPOSITION-001.

    ``docs/compile-only-expansion-candidates.md`` was deleted with an
    index row (content recoverable from the indexed SHA); its doc-pinning
    tests went with it. The ledger guardrails above remain the live
    contract.
    """

    def test_doc_recorded_in_archive_index(self):
        self.assertIn(
            "docs/compile-only-expansion-candidates.md",
            ARCHIVE_INDEX.read_text(encoding="utf-8"),
            "the archived candidates doc must be recorded in " "docs/archive-index.md",
        )


if __name__ == "__main__":
    unittest.main()

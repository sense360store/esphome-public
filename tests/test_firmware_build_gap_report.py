#!/usr/bin/env python3
"""Tests for the firmware build-gap report (FW-MATRIX-002).

Covers the report generator at ``scripts/report_firmware_build_gaps.py``
and the on-disk report at ``docs/firmware-build-gap-report.md``. The
report is planning / reporting only; these tests pin lane-assignment
invariants and the guardrails that no lane implies unsafe WebFlash
exposure or stable promotion.

Uses Python's stdlib unittest (matching this repo's no-pytest
convention). Run with::

    python3 tests/test_firmware_build_gap_report.py

or::

    python3 -m unittest tests.test_firmware_build_gap_report -v
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import report_firmware_build_gaps as rfbg  # noqa: E402

MATRIX_PATH = REPO_ROOT / "config" / "firmware-combination-matrix.json"
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
REPORT_PATH = REPO_ROOT / "docs" / "firmware-build-gap-report.md"

RELEASE_ONE_CONFIG_STRING = "Ceiling-POE-VentIQ-RoomIQ"
LED_PREVIEW_CONFIG_STRING = "Ceiling-POE-VentIQ-RoomIQ-LED"
FANTRIAC_BLOCKED_CONFIG_STRING = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"

EXPECTED_LANE_IDS = [
    "current-webflash",
    "fantriac-blocked-hardware-compliance",
    "fanrelay-blocked-package-or-core-bus",
    "fanpwm-blocked-package-or-core-bus",
    "fandac-blocked-package-or-core-bus",
    "pwr-blocked-compliance",
    "led-preview-and-stable-candidates",
    "poe-non-fan-candidates",
    "usb-non-fan-candidates",
    "missing-product-yaml",
]

# RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001 added three room-bundle preview build
# rows, moving them from the candidate lanes into current-webflash:
#   current-webflash 2 -> 5 (the two pre-existing builds + the three previews);
#   poe-non-fan-candidates 5 -> 3 (Ceiling-POE-RoomIQ, Ceiling-POE-AirIQ-RoomIQ
#     are now shipping); led-preview-and-stable-candidates 11 -> 10
#     (Ceiling-POE-RoomIQ-LED is now shipping). Total stays 168.
EXPECTED_LANE_COUNTS = {
    # TRIAC-COMMISSIONING-001 moved the full-composition FanTRIAC config into
    # current-webflash (experimental channel), so current-webflash gains one
    # row (5 -> 6) and the blocked FanTRIAC family lane loses it (36 -> 35).
    "current-webflash": 6,
    "fantriac-blocked-hardware-compliance": 35,
    "fanrelay-blocked-package-or-core-bus": 36,
    "fanpwm-blocked-package-or-core-bus": 36,
    "fandac-blocked-package-or-core-bus": 24,
    "pwr-blocked-compliance": 12,
    "led-preview-and-stable-candidates": 10,
    "poe-non-fan-candidates": 3,
    "usb-non-fan-candidates": 6,
    "missing-product-yaml": 0,
}


def _load(path: Path):
    return json.loads(path.read_text())


class BuildGapReportTests(unittest.TestCase):
    """Tests over the freshly-regenerated report and lane entries."""

    @classmethod
    def setUpClass(cls):
        cls.matrix = _load(MATRIX_PATH)
        cls.builds = _load(BUILDS_PATH)
        cls.lane_entries, cls.rendered = rfbg.generate(cls.matrix, cls.builds)
        cls.by_lane = {entry["id"]: entry for entry in cls.lane_entries}
        cls.committed_configs = {
            entry["config_string"]
            for entry in (cls.builds.get("builds", []) or [])
            if entry.get("config_string")
        }

    # ------------------------------------------------------------------
    # Lane shape / structure
    # ------------------------------------------------------------------

    def test_lane_ids_are_the_expected_set(self):
        self.assertEqual(
            [entry["id"] for entry in self.lane_entries],
            EXPECTED_LANE_IDS,
        )

    def test_every_lane_entry_has_required_fields(self):
        required = {
            "id",
            "title",
            "count",
            "representatives",
            "blocker_summary",
            "recommended_next_pr",
            "compile_only_safe_now",
            "webflash_exposure_allowed_now",
            "stable_ready_now",
            "notes",
            "config_strings",
        }
        for entry in self.lane_entries:
            missing = required - set(entry.keys())
            self.assertFalse(
                missing,
                f"lane {entry.get('id')!r} missing fields {missing}",
            )

    def test_lane_counts_match_expected(self):
        for lane_id, expected in EXPECTED_LANE_COUNTS.items():
            self.assertEqual(
                self.by_lane[lane_id]["count"],
                expected,
                f"lane {lane_id!r}: expected {expected} rows, got "
                f"{self.by_lane[lane_id]['count']}",
            )

    # ------------------------------------------------------------------
    # Coverage: 168 rows, exactly one lane each
    # ------------------------------------------------------------------

    def test_all_168_rows_accounted_for_by_exactly_one_lane(self):
        matrix_total = self.matrix["totals"]["combinations"]
        self.assertEqual(matrix_total, 168)
        lane_total = sum(entry["count"] for entry in self.lane_entries)
        self.assertEqual(lane_total, matrix_total)

    def test_every_matrix_row_has_exactly_one_lane(self):
        seen_per_row: dict[str, list[str]] = {}
        for entry in self.lane_entries:
            for cs in entry["config_strings"]:
                seen_per_row.setdefault(cs, []).append(entry["id"])
        matrix_configs = {row["config_string"] for row in self.matrix["combinations"]}
        # every matrix row appears in exactly one lane
        for cs in matrix_configs:
            assigned = seen_per_row.get(cs, [])
            self.assertEqual(
                len(assigned),
                1,
                f"{cs!r} assigned to lanes {assigned!r}; expected exactly 1",
            )
        # and the lanes do not invent rows that aren't in the matrix
        for cs in seen_per_row:
            self.assertIn(cs, matrix_configs, f"lane row {cs!r} is not in the matrix")

    # ------------------------------------------------------------------
    # current-webflash lane contents
    # ------------------------------------------------------------------

    def test_current_webflash_lane_includes_release_one(self):
        lane = self.by_lane["current-webflash"]
        self.assertIn(RELEASE_ONE_CONFIG_STRING, lane["config_strings"])

    def test_current_webflash_lane_includes_led_preview(self):
        lane = self.by_lane["current-webflash"]
        self.assertIn(LED_PREVIEW_CONFIG_STRING, lane["config_strings"])

    def test_current_webflash_lane_count_matches_committed_builds(self):
        lane = self.by_lane["current-webflash"]
        self.assertEqual(lane["count"], len(self.committed_configs))

    def test_rendered_report_mentions_release_one(self):
        self.assertIn(RELEASE_ONE_CONFIG_STRING, self.rendered)

    def test_rendered_report_mentions_led_preview(self):
        self.assertIn(LED_PREVIEW_CONFIG_STRING, self.rendered)

    # ------------------------------------------------------------------
    # FanTRIAC lane: blocked, references HW-005
    # ------------------------------------------------------------------

    def test_fantriac_lane_is_blocked(self):
        lane = self.by_lane["fantriac-blocked-hardware-compliance"]
        self.assertFalse(
            lane["webflash_exposure_allowed_now"],
            "FanTRIAC lane must not be marked webflash-exposable",
        )
        self.assertFalse(
            lane["compile_only_safe_now"],
            "FanTRIAC lane must not be marked compile-only-safe",
        )
        self.assertFalse(
            lane["stable_ready_now"],
            "FanTRIAC lane must not be marked stable-ready",
        )

    def test_fantriac_lane_references_hw_005(self):
        lane = self.by_lane["fantriac-blocked-hardware-compliance"]
        self.assertIn(
            "HW-005",
            lane["blocker_summary"],
            "FanTRIAC lane blocker summary must reference HW-005",
        )

    def test_fantriac_full_composition_commissioned_out_of_blocked_lane(self):
        # TRIAC-COMMISSIONING-001 moved the full-composition FanTRIAC config out
        # of the blocked family lane into current-webflash (experimental
        # channel). The remaining FanTRIAC family combinations stay blocked.
        blocked_lane = self.by_lane["fantriac-blocked-hardware-compliance"]
        self.assertNotIn(
            FANTRIAC_BLOCKED_CONFIG_STRING, blocked_lane["config_strings"]
        )
        webflash_lane = self.by_lane["current-webflash"]
        self.assertIn(
            FANTRIAC_BLOCKED_CONFIG_STRING, webflash_lane["config_strings"]
        )

    # ------------------------------------------------------------------
    # PWR lane: not WebFlash-exposable
    # ------------------------------------------------------------------

    def test_pwr_lane_is_not_webflash_exposable(self):
        lane = self.by_lane["pwr-blocked-compliance"]
        self.assertFalse(
            lane["webflash_exposure_allowed_now"],
            "PWR lane must not be marked webflash-exposable",
        )

    def test_pwr_lane_references_compliance_001(self):
        lane = self.by_lane["pwr-blocked-compliance"]
        self.assertIn(
            "COMPLIANCE-001",
            lane["blocker_summary"],
            "PWR lane blocker summary must reference COMPLIANCE-001",
        )

    def test_pwr_lane_contains_only_pwr_rows(self):
        lane = self.by_lane["pwr-blocked-compliance"]
        for cs in lane["config_strings"]:
            self.assertTrue(
                cs.startswith("Ceiling-PWR"),
                f"{cs!r} in pwr lane but does not start with Ceiling-PWR",
            )

    # ------------------------------------------------------------------
    # LED stable lane: not stable-ready without bench + operator proof
    # ------------------------------------------------------------------

    def test_led_lane_is_not_stable_ready(self):
        lane = self.by_lane["led-preview-and-stable-candidates"]
        self.assertFalse(
            lane["stable_ready_now"],
            "LED candidate lane must not be marked stable-ready",
        )

    def test_led_lane_blocker_references_s360_300_bench(self):
        lane = self.by_lane["led-preview-and-stable-candidates"]
        self.assertIn(
            "S360-300-BENCH-001",
            lane["blocker_summary"],
            "LED candidate lane must reference S360-300-BENCH-001",
        )

    def test_led_lane_blocker_references_operator_proof(self):
        lane = self.by_lane["led-preview-and-stable-candidates"]
        self.assertIn(
            "WF-HW-TEST-001",
            lane["blocker_summary"],
            "LED candidate lane must reference WebFlash operator-proof "
            "container WF-HW-TEST-001",
        )

    def test_led_lane_rows_all_carry_led(self):
        lane = self.by_lane["led-preview-and-stable-candidates"]
        for cs in lane["config_strings"]:
            self.assertIn(
                "LED",
                cs.split("-"),
                f"{cs!r} in led lane but does not carry LED token",
            )

    def test_led_lane_excludes_committed_led_preview(self):
        lane = self.by_lane["led-preview-and-stable-candidates"]
        self.assertNotIn(
            LED_PREVIEW_CONFIG_STRING,
            lane["config_strings"],
            "LED preview build must live in current-webflash, not the "
            "led-preview-and-stable-candidates lane",
        )

    # ------------------------------------------------------------------
    # Global guardrail: WebFlash exposure only for committed rows
    # ------------------------------------------------------------------

    def test_no_lane_implies_unsafe_webflash_exposure(self):
        for entry in self.lane_entries:
            if not entry["webflash_exposure_allowed_now"]:
                continue
            for cs in entry["config_strings"]:
                self.assertIn(
                    cs,
                    self.committed_configs,
                    f"lane {entry['id']!r} claims WebFlash exposure is "
                    f"allowed but {cs!r} is not in config/webflash-builds.json",
                )

    def test_no_lane_is_stable_ready(self):
        """No lane should be marked stable-ready in this report.

        The two committed builds are stable (Release-One) and preview
        (LED). Stable-ready is a per-row gate per
        docs/preview-to-stable-promotion-gates.md; the report never
        asserts it across an entire lane. This guards against future
        accidental flips.
        """
        for entry in self.lane_entries:
            self.assertFalse(
                entry["stable_ready_now"],
                f"lane {entry['id']!r} must not be marked stable-ready",
            )

    def test_fan_lanes_are_all_blocked(self):
        for lane_id in (
            "fantriac-blocked-hardware-compliance",
            "fanrelay-blocked-package-or-core-bus",
            "fanpwm-blocked-package-or-core-bus",
            "fandac-blocked-package-or-core-bus",
        ):
            lane = self.by_lane[lane_id]
            self.assertFalse(
                lane["webflash_exposure_allowed_now"],
                f"{lane_id} must not be marked webflash-exposable",
            )
            self.assertFalse(
                lane["compile_only_safe_now"],
                f"{lane_id} must not be marked compile-only-safe",
            )
            self.assertFalse(
                lane["stable_ready_now"],
                f"{lane_id} must not be marked stable-ready",
            )

    # ------------------------------------------------------------------
    # Sentinel lane
    # ------------------------------------------------------------------

    def test_missing_product_yaml_lane_is_empty_today(self):
        lane = self.by_lane["missing-product-yaml"]
        self.assertEqual(
            lane["count"],
            0,
            "missing-product-yaml sentinel lane should be empty under "
            "the current matrix; a non-empty value indicates matrix "
            "drift or stale lane policies.",
        )


class BuildGapReportOnDiskTests(unittest.TestCase):
    """Pin the committed docs/firmware-build-gap-report.md to the generator."""

    def test_committed_report_matches_regeneration(self):
        matrix = _load(MATRIX_PATH)
        builds = _load(BUILDS_PATH)
        _, regenerated = rfbg.generate(matrix, builds)
        on_disk = REPORT_PATH.read_text()
        self.assertEqual(
            on_disk,
            regenerated,
            "docs/firmware-build-gap-report.md is stale; run "
            "`python3 scripts/report_firmware_build_gaps.py`.",
        )


class BuildGapReportCLITests(unittest.TestCase):
    """The report-generator CLI surface."""

    def test_check_mode_passes_when_committed(self):
        rc = rfbg.main(["--check"])
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)

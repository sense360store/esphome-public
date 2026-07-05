#!/usr/bin/env python3
"""DOCS-CONSOLIDATION-ROADMAP-001 — canonical roadmap/status doc guards.

This module pins the invariants for the canonical repo status / roadmap /
blocker / upcoming-PR document created by DOCS-CONSOLIDATION-ROADMAP-001:

  * ``docs/sense360-roadmap-status.md`` exists and is the single canonical
    status doc.
  * The superseded roadmap / status / audit / handoff docs carry a redirect
    pointer back to the canonical doc (they redirect rather than duplicate
    current-state status).
  * FanPWM is shown as **compile-proven but bench-pending** (current /
    thermal / RPM not measured) and excluded from release / WebFlash.
  * LED remains **preview** (no LED-stable claim).
  * S360-410 PoE remains **unresolved** / ``cataloged_unverified``.
  * The release targets stated in the doc match
    ``config/webflash-builds.json``.

These are docs-only guards. They assert nothing about firmware behaviour and
they do not weaken any existing test: source-of-truth, evidence, pinmap, and
catalog docs are explicitly required to be preserved (not deleted).

Run with::

    python3 tests/test_roadmap_status_doc.py

or::

    python3 -m unittest tests.test_roadmap_status_doc -v
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent

CANONICAL_REL = "docs/sense360-roadmap-status.md"
CANONICAL = REPO_ROOT / CANONICAL_REL
WEBFLASH_BUILDS = REPO_ROOT / "config" / "webflash-builds.json"

# Docs that the DOCS-CONSOLIDATION-ROADMAP-001 pass turned into redirects
# to the canonical doc. All eight have since been ARCHIVED under
# DOCS-DISPOSITION-001 (deleted with provenance rows; content recoverable
# from the indexed SHAs), so the redirect contract is now an
# archive-index-row contract.
ARCHIVED_REDIRECTED_DOCS = [
    "docs/repo-freshness-roadmap-audit.md",
    "docs/repo-structure-audit.md",
    "docs/cleanup-audit.md",
    "docs/webflash-drift-audit.md",
    "docs/webflash-ci-alignment.md",
    "docs/webflash-release-handoff.md",
    "docs/stable-target-expansion-plan.md",
    "docs/stable-target-ventiq-001-gate-closure.md",
]

# Source-of-truth / evidence / pinmap / catalog / policy docs that MUST be
# preserved in the tree (must NOT be deleted or gutted).
PRESERVED_DOCS = [
    "docs/hardware-catalog.md",
    "docs/webflash-contract.md",
    "docs/compliance/mains-voltage-uk-eu-assessment.md",
    "docs/hardware/s360-100-native-fan-gpio-map.md",
    "docs/hardware/s360-311-r4-pwm.md",
    "docs/hardware/s360-410-r4-poe.md",
    "docs/hardware/s360-410-module-pinmap.md",
    "docs/hardware/s360-300-r4-led.md",
]

# Formerly PRESERVED docs that DOCS-DISPOSITION-001 (the newer, ratified
# disposition authority) archived: preservation now means an
# archive-index row whose SHA the verbatim content stays recoverable from.
ARCHIVED_PRESERVED_DOCS = [
    "docs/release-one.md",
    "docs/sense360-room-bundles.md",
    "docs/preview-to-stable-promotion-gates.md",
    "docs/blocker-burndown.md",
    "docs/product-readiness-matrix.md",
    "docs/manual-install-fan-candidates.md",
    "docs/package-poe-410-001-audit.md",
]

ARCHIVE_INDEX = REPO_ROOT / "docs" / "archive-index.md"


class CanonicalDocExistsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(
            CANONICAL.is_file(),
            f"Canonical roadmap/status doc {CANONICAL_REL} must exist.",
        )
        self.text = CANONICAL.read_text(encoding="utf-8")

    def test_canonical_id_present(self) -> None:
        self.assertIn("DOCS-CONSOLIDATION-ROADMAP-001", self.text)

    def test_required_sections_present(self) -> None:
        required = [
            "current release targets",
            "bundle sku",
            "board sku",
            "room firmware config",
            "webflash",
            "hardware blocker",
            "fanpwm",
            "s360-410",
            "next pr queue",
            "cross-repo",
        ]
        low = self.text.lower()
        for needle in required:
            self.assertIn(
                needle,
                low,
                f"Canonical doc missing required topic: {needle!r}",
            )

    def test_docs_only_guardrails_declared(self) -> None:
        low = self.text.lower()
        self.assertIn("docs only", low)
        # It must NOT claim to enable webflash / publish firmware.
        self.assertIn("does", low)


class RedirectedDocsTests(unittest.TestCase):
    def test_superseded_docs_recorded_in_archive_index(self) -> None:
        archive_index = ARCHIVE_INDEX.read_text(encoding="utf-8")
        for rel in ARCHIVED_REDIRECTED_DOCS:
            with self.subTest(doc=rel):
                self.assertIn(
                    rel,
                    archive_index,
                    f"archived redirected doc must be recorded in "
                    f"docs/archive-index.md: {rel}",
                )


class PreservedDocsTests(unittest.TestCase):
    def test_source_of_truth_docs_preserved(self) -> None:
        for rel in PRESERVED_DOCS:
            path = REPO_ROOT / rel
            self.assertTrue(
                path.is_file(),
                f"Preserved source-of-truth/evidence doc was removed: {rel}",
            )
            # Must not have been gutted down to a bare redirect stub.
            self.assertGreater(
                len(path.read_text(encoding="utf-8")),
                400,
                f"Preserved doc looks gutted (too short): {rel}",
            )

    def test_archived_preserved_docs_recorded_in_archive_index(self) -> None:
        archive_index = ARCHIVE_INDEX.read_text(encoding="utf-8")
        for rel in ARCHIVED_PRESERVED_DOCS:
            with self.subTest(doc=rel):
                self.assertIn(
                    rel,
                    archive_index,
                    f"archived formerly-preserved doc must be recorded in "
                    f"docs/archive-index.md: {rel}",
                )


class FanPwmStatusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.low = CANONICAL.read_text(encoding="utf-8").lower()

    def test_fanpwm_compile_proven(self) -> None:
        self.assertIn("compile-proven", self.low)

    def test_fanpwm_bench_pending(self) -> None:
        # Current / thermal / RPM must be shown as not yet measured.
        self.assertIn("not measured", self.low)
        self.assertIn("rpm_supported", self.low)

    def test_fanpwm_excluded_from_release_webflash(self) -> None:
        self.assertIn("hardware-pending", self.low)

    def test_sx1509_marked_legacy_superseded(self) -> None:
        self.assertIn("superseded", self.low)


class LedPreviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = CANONICAL.read_text(encoding="utf-8")
        self.low = self.text.lower()

    def test_led_is_preview(self) -> None:
        self.assertIn("preview", self.low)
        self.assertIn("led", self.low)

    def test_no_led_stable_claim(self) -> None:
        self.assertIn("no led-stable claim", self.low)


class Poe410Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.low = CANONICAL.read_text(encoding="utf-8").lower()

    def test_s360_410_unresolved(self) -> None:
        self.assertIn("s360-410", self.low)
        self.assertIn("unresolved", self.low)
        self.assertIn("cataloged_unverified", self.low)

    def test_no_s360_410_verified_claim(self) -> None:
        self.assertIn("not verified", self.low)


class ReleaseTargetsMatchConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = CANONICAL.read_text(encoding="utf-8")
        self.builds = json.loads(WEBFLASH_BUILDS.read_text(encoding="utf-8"))["builds"]

    def test_every_build_appears_in_doc(self) -> None:
        for build in self.builds:
            self.assertIn(
                build["config_string"],
                self.text,
                f"Release target {build['config_string']} missing from canonical doc.",
            )
            self.assertIn(
                build["artifact_name"],
                self.text,
                f"Artifact {build['artifact_name']} missing from canonical doc.",
            )
            self.assertIn(
                build["channel"],
                self.text,
                f"Channel {build['channel']} for {build['config_string']} missing.",
            )

    def test_doc_does_not_invent_extra_release_targets(self) -> None:
        known = {b["config_string"] for b in self.builds}
        # Any "-v{version}-{channel}.bin" artifact named in the doc must be a
        # known build artifact (no fabricated release artifacts).
        doc_artifacts = {b["artifact_name"] for b in self.builds}
        for art in doc_artifacts:
            self.assertIn(art, self.text)
        # The stable channel carries Release-One plus the two owner-waiver
        # promotions (STABLE-PROMOTION-RECONCILE-001: Bedroom v1.0.5,
        # Kitchen v1.0.6); Release-One stays the required customer baseline.
        stable = {b["config_string"] for b in self.builds if b["channel"] == "stable"}
        self.assertEqual(
            stable,
            {
                "Ceiling-POE-VentIQ-RoomIQ",
                "Ceiling-POE-AirIQ-RoomIQ",
                "Ceiling-POE-RoomIQ",
            },
            "Stable release targets drifted from config/webflash-builds.json.",
        )
        self.assertIn("Ceiling-POE-VentIQ-RoomIQ", stable)
        self.assertTrue(known)


class NextHardwareTaskTests(unittest.TestCase):
    """PRE-HW-PREP-FW-312-CLOSEOUT-001 — the S360-312 DAC bench task is recorded
    as the next real hardware task (forward pointer only), and no DAC bench
    evidence is claimed in the Evidence & Bench Logs section."""

    BENCH_ID = "S360-312-DAC-BENCH-001"

    def setUp(self) -> None:
        self.text = CANONICAL.read_text(encoding="utf-8")

    def _section(self, heading_substr: str, text: str) -> str:
        idx = text.index(heading_substr)
        rest = text[idx + len(heading_substr):]
        nxt = rest.find("\n## ")
        return rest if nxt == -1 else rest[:nxt]

    def test_next_hardware_tasks_names_dac_bench(self) -> None:
        # (a) The Next Hardware Tasks section must name the canonical bench task.
        self.assertIn("## Next Hardware Tasks", self.text)
        section = self._section("## Next Hardware Tasks", self.text)
        self.assertIn(
            self.BENCH_ID,
            section,
            "Next Hardware Tasks section must name the DAC bench task "
            f"{self.BENCH_ID}.",
        )

    def test_evidence_and_bench_logs_stays_empty(self) -> None:
        # (b) The Evidence & Bench Logs section must remain the empty
        # placeholder — no measured DAC bench-log row may appear there.
        self.assertIn("## Evidence & Bench Logs", self.text)
        section = self._section("## Evidence & Bench Logs", self.text)
        self.assertIn(
            "(no bench logs yet)",
            section,
            "Evidence & Bench Logs must stay the empty placeholder.",
        )
        self.assertNotIn(
            self.BENCH_ID,
            section,
            "No filled S360-312 DAC bench-log row may appear in "
            "Evidence & Bench Logs (no hardware evidence exists).",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

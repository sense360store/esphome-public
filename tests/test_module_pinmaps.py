#!/usr/bin/env python3
"""MODULE-PINMAPS-GDRIVE-001.

Guards for the per-module module-side pinmap docs under
``docs/hardware/sXXX-module-pinmap.md``.

Each module pinmap doc records the **module-side** view of the
Sense360 Core-to-module connector pin map (canonical Core-side
master in ``docs/hardware/s360-100-core-connector-pin-map.md``,
S360-100-CONNECTOR-PINMAP-001) and reconciles every pin back to
the matching Core connector row.

This test file pins:

1. Every known Sense360 module SKU has a module pinmap doc.
2. Every module pinmap doc declares its MODULE-PINMAPS-GDRIVE-001
   identifier and references the canonical Core-side pin map.
3. Every module pinmap doc references its companion audit doc.
4. No module pinmap doc maps a tach / pulse-counter signal through
   an SX1509 (or other) I/O expander.
5. No `TBD` row is treated as `verified` — the four allowed
   Status vocabulary terms (`verified` / `schematic-backed` /
   `TBD` / `needs silkscreen confirmation`) are pinned.
6. No module pinmap doc contains release / WebFlash readiness
   phrasing.
7. The per-board do-not-change guardrails (`S360-310` / `S360-311`
   / `S360-312` / `S360-400` / `S360-410` stay
   `cataloged_unverified` — `S360-320` is now `schematic-backed` under
   TRIAC-UNBLOCK-BUILD-001; FanPWM stays out of
   `config/webflash-builds.json`; FanPWM products keep
   `rpm_supported: false` and `webflash_build_matrix: false`).
8. Cross-doc linking from the canonical Core-side pin map, the
   Core reference doc, the room-bundles doc, the blocker-burndown
   doc, the product-readiness-matrix doc, and ``UPCOMING_PR.md``.

Run with::

    python3 tests/test_module_pinmaps.py
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent

HARDWARE_DIR = REPO_ROOT / "docs" / "hardware"
CORE_PINMAP_DOC = HARDWARE_DIR / "s360-100-core-connector-pin-map.md"
CORE_REF_DOC = HARDWARE_DIR / "s360-100-r4-core.md"
ROOM_BUNDLES_DOC = REPO_ROOT / "docs" / "sense360-room-bundles.md"
BLOCKER_BURNDOWN_DOC = REPO_ROOT / "docs" / "blocker-burndown.md"
PRODUCT_READINESS_DOC = REPO_ROOT / "docs" / "product-readiness-matrix.md"
UPCOMING_PR_DOC = REPO_ROOT / "UPCOMING_PR.md"

HARDWARE_CATALOG_JSON = REPO_ROOT / "config" / "hardware-catalog.json"
PRODUCT_CATALOG_JSON = REPO_ROOT / "config" / "product-catalog.json"
WEBFLASH_BUILDS_JSON = REPO_ROOT / "config" / "webflash-builds.json"

# (SKU, friendly_name, pinmap doc filename, companion audit doc filename)
MODULE_PINMAP_DOCS: List[tuple] = [
    ("S360-200", "Sense360 RoomIQ", "s360-200-module-pinmap.md", "s360-200-r4-roomiq.md"),
    ("S360-210", "Sense360 AirIQ", "s360-210-module-pinmap.md", "s360-210-r4-airiq.md"),
    ("S360-211", "Sense360 VentIQ", "s360-211-module-pinmap.md", "s360-211-r4-ventiq.md"),
    ("S360-300", "Sense360 LED", "s360-300-module-pinmap.md", "s360-300-r4-led.md"),
    ("S360-310", "Sense360 Relay", "s360-310-module-pinmap.md", "s360-310-r4-relay.md"),
    ("S360-311", "Sense360 PWM", "s360-311-module-pinmap.md", "s360-311-r4-pwm.md"),
    ("S360-312", "Sense360 DAC", "s360-312-module-pinmap.md", "s360-312-r4-dac.md"),
    ("S360-320", "Sense360 TRIAC", "s360-320-module-pinmap.md", "s360-320-r4-triac.md"),
    ("S360-400", "Sense360 240v PSU", "s360-400-module-pinmap.md", "s360-400-r4-power.md"),
    ("S360-410", "Sense360 PoE PSU", "s360-410-module-pinmap.md", "s360-410-r4-poe.md"),
]

# The four allowed Status values, per the canonical pin map's
# Status-language rules.
ALLOWED_STATUS_VALUES = {
    "verified",
    "schematic-backed",
    "TBD",
    "needs silkscreen confirmation",
}

# Tach / pulse-counter net names that must NOT be mapped through
# an expander on any module pinmap doc row.
TACH_NET_NAMES = [
    "TachIO",
    "Pul_Cou1",
    "Pul_Cou2",
    "Pul_Cou3",
    "Pul_Cou4",
]

# Forbidden expander tokens. If any of these co-occurs with a tach /
# pulse-counter net on the same line (and the line is not flagged
# as 'removed' / 'superseded' / 'forbidden' / 'historical' /
# 'legacy' / 'must not' / 'no row' / 'no tach' / 'rejected'), the
# architectural rule has been violated.
FORBIDDEN_EXPANDER_TOKENS_NEAR_TACH = ["sx1509", "SX1509"]

# Forbidden release / WebFlash readiness phrases. None of these may
# appear in a module pinmap doc.
FORBIDDEN_RELEASE_PHRASES = [
    "release ready",
    "release-ready",
    "release-eligible",
    "stable-release",
    "webflash-ready",
    "rpm_supported: true",
    "rpm_supported = true",
]

# Per-board do-not-change guardrails. SKUs that must stay
# `cataloged_unverified` after MODULE-PINMAPS-GDRIVE-001.
# S360-320 moved to `schematic-backed` under TRIAC-UNBLOCK-BUILD-001
# (HW-005 BUILDABILITY resolved; NOT verified), so it is no longer in this list.
SKUS_STAYING_CATALOGED_UNVERIFIED = [
    "S360-310",
    "S360-311",
    "S360-312",
    "S360-400",
    "S360-410",
]


def _module_pinmap_path(filename: str) -> Path:
    return HARDWARE_DIR / filename


class DocExistsTests(unittest.TestCase):
    def test_every_known_sku_has_a_module_pinmap_doc(self) -> None:
        for sku, friendly, filename, _ in MODULE_PINMAP_DOCS:
            path = _module_pinmap_path(filename)
            with self.subTest(sku=sku):
                self.assertTrue(
                    path.is_file(),
                    f"Module-side pinmap doc for {sku} ({friendly}) must "
                    f"exist at {path.relative_to(REPO_ROOT)}.",
                )

    def test_every_pinmap_doc_declares_module_pinmaps_identifier(self) -> None:
        for sku, _, filename, _ in MODULE_PINMAP_DOCS:
            path = _module_pinmap_path(filename)
            with self.subTest(sku=sku):
                text = path.read_text()
                self.assertIn(
                    "MODULE-PINMAPS-GDRIVE-001",
                    text,
                    f"{filename} must self-identify as "
                    f"MODULE-PINMAPS-GDRIVE-001.",
                )

    def test_every_pinmap_doc_names_its_sku_and_friendly_name(self) -> None:
        for sku, friendly, filename, _ in MODULE_PINMAP_DOCS:
            path = _module_pinmap_path(filename)
            text = path.read_text()
            with self.subTest(sku=sku):
                self.assertIn(
                    sku,
                    text,
                    f"{filename} must name SKU {sku}.",
                )
                self.assertIn(
                    friendly,
                    text,
                    f"{filename} must name {sku} as {friendly!r}.",
                )


class CrossLinkingTests(unittest.TestCase):
    def test_every_pinmap_doc_references_core_pin_map(self) -> None:
        needle = "s360-100-core-connector-pin-map.md"
        for sku, _, filename, _ in MODULE_PINMAP_DOCS:
            path = _module_pinmap_path(filename)
            with self.subTest(sku=sku):
                self.assertIn(
                    needle,
                    path.read_text(),
                    f"{filename} must reference the canonical Core-side "
                    f"pin map ({needle}).",
                )

    def test_every_pinmap_doc_references_companion_audit_doc(self) -> None:
        for sku, _, filename, companion in MODULE_PINMAP_DOCS:
            path = _module_pinmap_path(filename)
            with self.subTest(sku=sku):
                self.assertIn(
                    companion,
                    path.read_text(),
                    f"{filename} must reference its companion audit doc "
                    f"({companion}).",
                )

    def test_core_pin_map_references_every_module_pinmap_doc(self) -> None:
        text = CORE_PINMAP_DOC.read_text()
        for sku, _, filename, _ in MODULE_PINMAP_DOCS:
            with self.subTest(sku=sku):
                self.assertIn(
                    filename,
                    text,
                    f"{CORE_PINMAP_DOC.name} must cross-reference "
                    f"{filename}.",
                )

    def test_core_reference_doc_references_every_module_pinmap_doc(self) -> None:
        text = CORE_REF_DOC.read_text()
        for sku, _, filename, _ in MODULE_PINMAP_DOCS:
            with self.subTest(sku=sku):
                self.assertIn(
                    filename,
                    text,
                    f"{CORE_REF_DOC.name} must cross-reference "
                    f"{filename}.",
                )

    def test_room_bundles_doc_references_every_module_pinmap_doc(self) -> None:
        text = ROOM_BUNDLES_DOC.read_text()
        for sku, _, filename, _ in MODULE_PINMAP_DOCS:
            with self.subTest(sku=sku):
                self.assertIn(
                    filename,
                    text,
                    f"{ROOM_BUNDLES_DOC.name} must cross-reference "
                    f"{filename}.",
                )

    def test_module_pinmaps_identifier_in_blocker_burndown(self) -> None:
        self.assertIn(
            "MODULE-PINMAPS-GDRIVE-001",
            BLOCKER_BURNDOWN_DOC.read_text(),
            f"{BLOCKER_BURNDOWN_DOC.name} must record "
            f"MODULE-PINMAPS-GDRIVE-001.",
        )

    def test_module_pinmaps_identifier_in_product_readiness_matrix(self) -> None:
        self.assertIn(
            "MODULE-PINMAPS-GDRIVE-001",
            PRODUCT_READINESS_DOC.read_text(),
            f"{PRODUCT_READINESS_DOC.name} must record "
            f"MODULE-PINMAPS-GDRIVE-001.",
        )

    def test_module_pinmaps_identifier_in_upcoming_pr(self) -> None:
        self.assertIn(
            "MODULE-PINMAPS-GDRIVE-001",
            UPCOMING_PR_DOC.read_text(),
            f"{UPCOMING_PR_DOC.name} must record "
            f"MODULE-PINMAPS-GDRIVE-001.",
        )


class StatusVocabularyTests(unittest.TestCase):
    def test_only_allowed_status_values_appear_in_pin_table_rows(self) -> None:
        """Every per-connector pin-table row in a module pinmap doc
        must end with one of the four allowed Status values
        (verified / schematic-backed / TBD / needs silkscreen
        confirmation)."""
        for sku, _, filename, _ in MODULE_PINMAP_DOCS:
            path = _module_pinmap_path(filename)
            text = path.read_text()
            suspect_rows: List[str] = []
            for line in text.splitlines():
                if not line.startswith("|") or "---" in line:
                    continue
                cells = [c.strip() for c in line.strip("|").split("|")]
                if len(cells) < 6:
                    continue
                # Skip schema-description rows / matrix header rows /
                # the AC-line connector tables that use fewer status
                # columns.
                first = cells[0]
                if first in {
                    "Column",
                    "Connector ref",
                    "Pin",
                    "Pin number",
                    "Domain identifier",
                    "Pin range",
                    "Field",
                    "Artifact class",
                    "Drive item",
                    "Element",
                    "Sensor / connector",
                    "Net",
                    "Sensor / component",
                    "Rail",
                    "I²C target on VentIQ",
                    "`JP1` strap",
                    "Fan output",
                    "Pin number",
                }:
                    continue
                if not (first.isdigit() or first in {
                    "VBUS", "D+", "D-", "CC1", "CC2", "SBU1 / SBU2",
                    "SHIELD",
                }):
                    continue
                last = cells[-1].lower()
                tail_match = None
                for status in ALLOWED_STATUS_VALUES:
                    s = status.lower()
                    if last == s or last.endswith(s):
                        tail_match = status
                        break
                if tail_match is None:
                    suspect_rows.append(f"{filename}: {line}")
            with self.subTest(sku=sku):
                self.assertEqual(
                    suspect_rows,
                    [],
                    "Every per-connector pin-table row in a module "
                    "pinmap doc must end with one of the four allowed "
                    "Status values. Suspect rows:\n"
                    + "\n".join(suspect_rows),
                )

    def test_no_tbd_row_is_treated_as_verified(self) -> None:
        """A row carrying `TBD` in its Status cell must NOT also
        carry `verified` — the four status values are mutually
        exclusive per the Status-language rules."""
        for sku, _, filename, _ in MODULE_PINMAP_DOCS:
            path = _module_pinmap_path(filename)
            text = path.read_text()
            violations: List[str] = []
            for line in text.splitlines():
                if not line.startswith("|") or "---" in line:
                    continue
                cells = [c.strip() for c in line.strip("|").split("|")]
                if len(cells) < 6:
                    continue
                last = cells[-1]
                # Row must not contain both TBD and a bare `verified`
                # value in the same row's Status tail position. We
                # only flag rows whose Status cell literally equals
                # `verified` AND contains `TBD` elsewhere in the row.
                if last.lower() == "verified" and "TBD" in line:
                    # Allow the standalone connector matrix narrative
                    # rows; flag only per-pin rows (first cell numeric
                    # or USB-C pin label).
                    first = cells[0]
                    if first.isdigit() or first in {
                        "VBUS", "D+", "D-", "CC1", "CC2", "SBU1 / SBU2",
                        "SHIELD",
                    }:
                        violations.append(f"{filename}: {line}")
            with self.subTest(sku=sku):
                self.assertEqual(
                    violations,
                    [],
                    "A `TBD` row must not be treated as `verified`. "
                    "Violations:\n" + "\n".join(violations),
                )


class NativeGpioRuleTests(unittest.TestCase):
    def test_no_tach_signal_is_mapped_through_an_expander(self) -> None:
        """No row in any module pinmap doc may map a tach /
        pulse-counter signal (`TachIO` / `Pul_Cou1..4`) through an
        SX1509 (or other) I/O expander. Lines that explicitly call
        out the SX1509 path as removed / superseded / forbidden /
        historical / legacy / rejected / no tach / etc. are allowed
        for narrative purposes."""
        safe_tokens = (
            "removed",
            "superseded",
            "forbidden",
            "historical",
            "legacy",
            "must not",
            "no row",
            "no tach",
            "rejected",
            "no `tachio`",
            "expressly reject",
            "explicitly reject",
            "no sx1509",
        )
        for sku, _, filename, _ in MODULE_PINMAP_DOCS:
            path = _module_pinmap_path(filename)
            text = path.read_text()
            violations: List[str] = []
            for line in text.splitlines():
                if not line.startswith("|") or "---" in line:
                    continue
                mentions_tach = any(net in line for net in TACH_NET_NAMES)
                mentions_expander = any(
                    token in line
                    for token in FORBIDDEN_EXPANDER_TOKENS_NEAR_TACH
                )
                if mentions_tach and mentions_expander:
                    lower = line.lower()
                    if any(safe in lower for safe in safe_tokens):
                        continue
                    violations.append(f"{filename}: {line}")
            with self.subTest(sku=sku):
                self.assertEqual(
                    violations,
                    [],
                    "A module pinmap doc must not map any tach / "
                    "pulse-counter signal through an SX1509 expander "
                    "row. Violations:\n" + "\n".join(violations),
                )


class ReleaseReadinessGuardrailTests(unittest.TestCase):
    def test_no_pinmap_doc_claims_release_readiness(self) -> None:
        for sku, _, filename, _ in MODULE_PINMAP_DOCS:
            path = _module_pinmap_path(filename)
            text = path.read_text().lower()
            violations = [
                phrase
                for phrase in FORBIDDEN_RELEASE_PHRASES
                if phrase.lower() in text
            ]
            with self.subTest(sku=sku):
                self.assertEqual(
                    violations,
                    [],
                    f"{filename} must not contain release / WebFlash "
                    f"readiness phrases: {violations}",
                )

    def test_no_pinmap_doc_advances_fan_triac_blocker(self) -> None:
        for sku, _, filename, _ in MODULE_PINMAP_DOCS:
            path = _module_pinmap_path(filename)
            lower = path.read_text().lower()
            for forbidden in (
                "hw-005 resolved",
                "hw-005 closed",
                "fan triac unblocked",
                "fan triac resolved",
                "fantriac resolved",
                "fantriac unblocked",
            ):
                with self.subTest(sku=sku, phrase=forbidden):
                    self.assertNotIn(
                        forbidden,
                        lower,
                        f"{filename} must not advance FanTRIAC HW-005 "
                        f"(phrase: {forbidden!r}).",
                    )

    def test_no_pinmap_doc_advances_poe_410_blocker(self) -> None:
        for sku, _, filename, _ in MODULE_PINMAP_DOCS:
            path = _module_pinmap_path(filename)
            lower = path.read_text().lower()
            for forbidden in (
                "package-poe-410-001 resolved",
                "package-poe-410-001 closed",
                "s360-410 verified",
                "poe psu verified",
            ):
                with self.subTest(sku=sku, phrase=forbidden):
                    self.assertNotIn(
                        forbidden,
                        lower,
                        f"{filename} must not advance "
                        f"PACKAGE-POE-410-001 (phrase: {forbidden!r}).",
                    )


class CatalogGuardrailTests(unittest.TestCase):
    def _load_json(self, path: Path) -> dict:
        with path.open() as fh:
            return json.load(fh)

    def test_skus_stay_cataloged_unverified(self) -> None:
        data = self._load_json(HARDWARE_CATALOG_JSON)
        items = {e.get("sku"): e for e in data.get("items", [])}
        for sku in SKUS_STAYING_CATALOGED_UNVERIFIED:
            with self.subTest(sku=sku):
                entry = items.get(sku)
                self.assertIsNotNone(
                    entry,
                    f"{sku} row must exist in hardware catalog.",
                )
                self.assertEqual(
                    entry.get("schematic_status"),
                    "cataloged_unverified",
                    f"{sku} schematic_status must stay "
                    f"`cataloged_unverified` across "
                    f"MODULE-PINMAPS-GDRIVE-001.",
                )

    def test_no_fanpwm_in_webflash_builds(self) -> None:
        data = self._load_json(WEBFLASH_BUILDS_JSON)
        builds = data.get("builds", []) if isinstance(data, dict) else []
        for row in builds:
            cfg = row.get("config_string", "")
            with self.subTest(config_string=cfg):
                self.assertNotIn(
                    "FanPWM",
                    cfg,
                    "FanPWM must not appear in any WebFlash build "
                    "across MODULE-PINMAPS-GDRIVE-001.",
                )

    def test_fanpwm_products_keep_no_rpm_claim(self) -> None:
        data = self._load_json(PRODUCT_CATALOG_JSON)
        for entry in data.get("products", []):
            cfg = entry.get("config_string") or entry.get("name") or ""
            if "FanPWM" not in str(cfg):
                continue
            with self.subTest(config=cfg):
                self.assertNotEqual(
                    entry.get("rpm_supported"),
                    True,
                    f"{cfg}: rpm_supported must not be True across "
                    f"MODULE-PINMAPS-GDRIVE-001.",
                )
                self.assertFalse(
                    bool(entry.get("webflash_build_matrix")),
                    f"{cfg}: webflash_build_matrix must stay false.",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)

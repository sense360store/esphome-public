#!/usr/bin/env python3
"""Unit tests for config/hardware-catalog.json (HW-008).

These tests lock in the machine-readable hardware-catalog evidence fields
refreshed by HW-008 against the schematic PDFs committed under HW-007. They
intentionally do **not** assert anything about WebFlash build matrix entries,
product-catalog lifecycle statuses, Release-One config strings, FanTRIAC
HW-005 status, Sense360 LED Release-One exclusion, or mains-voltage
compliance — those concerns live in separate sources of truth and have their
own tests.

What this file checks:

  * config/hardware-catalog.json parses as JSON.
  * Every hardware entry has non-empty 'sku', 'friendly_name', and
    'schematic_status' fields.
  * Every 'schematic_status' value is one of the approved enum
    ('verified', 'cataloged_unverified').
  * Every entry with 'schematic_status: verified' has a non-empty
    'schematic_file' string.
  * Every 'schematic_file' path resolves to a real file under the repo root.
  * S360-100, S360-200, S360-210, S360-211, and S360-300 are 'verified'
    (HW-007 committed schematic evidence; HW-008 flips the JSON status).
  * S360-320 (Sense360 TRIAC) remains not 'verified' — HW-005 is still
    blocked and the S360-320 schematic is not committed.
  * S360-400 (Sense360 240v PSU) remains not 'verified' — the mains-voltage
    compliance review tracked in COMPLIANCE-001 still applies and the
    S360-400 schematic is not committed.
  * Entries that are not 'verified' may legitimately omit 'schematic_file';
    HW-008 does not require every catalog entry to point at a PDF.

Run with:

    python3 tests/test_hardware_catalog.py
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = REPO_ROOT / "config" / "hardware-catalog.json"

APPROVED_SCHEMATIC_STATUSES = frozenset({"verified", "cataloged_unverified"})

EXPECTED_VERIFIED_SKUS = frozenset(
    {"S360-100", "S360-200", "S360-210", "S360-211", "S360-300"}
)

EXPECTED_STILL_UNVERIFIED_SKUS = frozenset({"S360-320", "S360-400", "S360-410"})


def _load_catalog() -> Dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text())


def _items() -> List[Dict[str, Any]]:
    return [i for i in _load_catalog().get("items", []) if isinstance(i, dict)]


def _entry_by_sku(sku: str) -> Dict[str, Any]:
    for entry in _items():
        if entry.get("sku") == sku:
            return entry
    raise AssertionError(f"no hardware-catalog entry with sku={sku!r}")


class CatalogParseTests(unittest.TestCase):
    def test_catalog_file_exists(self) -> None:
        self.assertTrue(
            CATALOG_PATH.is_file(),
            f"hardware catalog missing: {CATALOG_PATH}",
        )

    def test_catalog_parses_as_json(self) -> None:
        try:
            doc = _load_catalog()
        except json.JSONDecodeError as exc:
            self.fail(f"config/hardware-catalog.json is not valid JSON: {exc}")
        self.assertIsInstance(doc, dict)
        self.assertIn("items", doc)
        self.assertIsInstance(doc["items"], list)
        self.assertGreater(len(doc["items"]), 0)


class CatalogEntryShapeTests(unittest.TestCase):
    def test_every_entry_has_required_string_fields(self) -> None:
        for entry in _items():
            sku = entry.get("sku", "<missing>")
            for field in ("sku", "friendly_name", "schematic_status"):
                with self.subTest(sku=sku, field=field):
                    value = entry.get(field)
                    self.assertIsInstance(
                        value,
                        str,
                        f"entry {sku!r} field {field!r} must be a string",
                    )
                    self.assertNotEqual(
                        value,
                        "",
                        f"entry {sku!r} field {field!r} must be non-empty",
                    )

    def test_every_schematic_status_is_in_approved_enum(self) -> None:
        for entry in _items():
            sku = entry.get("sku", "<missing>")
            status = entry.get("schematic_status")
            with self.subTest(sku=sku):
                self.assertIn(
                    status,
                    APPROVED_SCHEMATIC_STATUSES,
                    f"entry {sku!r} has schematic_status {status!r} not in "
                    f"{sorted(APPROVED_SCHEMATIC_STATUSES)}",
                )


class VerifiedEntryEvidenceTests(unittest.TestCase):
    def test_every_verified_entry_has_schematic_file(self) -> None:
        for entry in _items():
            if entry.get("schematic_status") != "verified":
                continue
            sku = entry.get("sku", "<missing>")
            with self.subTest(sku=sku):
                schematic_file = entry.get("schematic_file")
                self.assertIsInstance(
                    schematic_file,
                    str,
                    f"verified entry {sku!r} missing schematic_file",
                )
                self.assertNotEqual(
                    schematic_file,
                    "",
                    f"verified entry {sku!r} has empty schematic_file",
                )

    def test_every_schematic_file_exists_on_disk(self) -> None:
        for entry in _items():
            schematic_file = entry.get("schematic_file")
            if not isinstance(schematic_file, str) or schematic_file == "":
                continue
            sku = entry.get("sku", "<missing>")
            with self.subTest(sku=sku, schematic_file=schematic_file):
                path = REPO_ROOT / schematic_file
                self.assertTrue(
                    path.is_file(),
                    f"entry {sku!r} schematic_file does not exist: {path}",
                )

    def test_unverified_entries_may_omit_schematic_file(self) -> None:
        unverified = [
            e for e in _items() if e.get("schematic_status") == "cataloged_unverified"
        ]
        self.assertGreater(
            len(unverified),
            0,
            "expected at least one cataloged_unverified entry to remain",
        )
        # No assertion that schematic_file is absent — the test merely
        # documents that this is allowed and that this file deliberately
        # does not require it.


class HW008VerifiedSKUsTests(unittest.TestCase):
    """SKUs whose schematic_status must be 'verified' after HW-008."""

    def test_s360_100_core_is_verified(self) -> None:
        entry = _entry_by_sku("S360-100")
        self.assertEqual(entry.get("schematic_status"), "verified")
        self.assertEqual(
            entry.get("schematic_file"),
            "docs/hardware/schematics/S360-100-R4.pdf",
        )

    def test_s360_200_roomiq_is_verified(self) -> None:
        entry = _entry_by_sku("S360-200")
        self.assertEqual(entry.get("schematic_status"), "verified")
        self.assertEqual(
            entry.get("schematic_file"),
            "docs/hardware/schematics/S360-200-R4.pdf",
        )

    def test_s360_210_airiq_is_verified(self) -> None:
        entry = _entry_by_sku("S360-210")
        self.assertEqual(entry.get("schematic_status"), "verified")
        self.assertEqual(
            entry.get("schematic_file"),
            "docs/hardware/schematics/S360-210-R4.pdf",
        )

    def test_s360_211_ventiq_is_verified(self) -> None:
        entry = _entry_by_sku("S360-211")
        self.assertEqual(entry.get("schematic_status"), "verified")
        self.assertEqual(
            entry.get("schematic_file"),
            "docs/hardware/schematics/S360-211-R4.pdf",
        )

    def test_s360_300_led_is_verified(self) -> None:
        entry = _entry_by_sku("S360-300")
        self.assertEqual(entry.get("schematic_status"), "verified")
        self.assertEqual(
            entry.get("schematic_file"),
            "docs/hardware/schematics/S360-300-R4.pdf",
        )

    def test_all_expected_verified_skus_are_verified(self) -> None:
        verified = {
            e["sku"] for e in _items() if e.get("schematic_status") == "verified"
        }
        self.assertEqual(EXPECTED_VERIFIED_SKUS, verified & EXPECTED_VERIFIED_SKUS)


class HW008StillUnverifiedSKUsTests(unittest.TestCase):
    """SKUs whose schematic_status must NOT be 'verified' after HW-008.

    HW-008 does not by itself unblock FanTRIAC (HW-005) or clear the
    mains-voltage compliance gate for S360-400 (COMPLIANCE-001). These tests
    pin those statuses so HW-008 cannot quietly upgrade them.
    """

    def test_s360_320_triac_is_not_verified(self) -> None:
        entry = _entry_by_sku("S360-320")
        self.assertNotEqual(
            entry.get("schematic_status"),
            "verified",
            "S360-320 must remain cataloged_unverified; HW-005 blocks "
            "FanTRIAC and the S360-320 schematic is not committed.",
        )
        self.assertNotIn(
            "schematic_file",
            entry,
            "S360-320 must not carry a schematic_file value while it is "
            "not verified.",
        )

    def test_s360_400_psu_is_not_verified(self) -> None:
        entry = _entry_by_sku("S360-400")
        self.assertNotEqual(
            entry.get("schematic_status"),
            "verified",
            "S360-400 must remain cataloged_unverified; the mains-voltage "
            "compliance review (COMPLIANCE-001) still applies and the "
            "S360-400 schematic is not committed.",
        )
        self.assertNotIn(
            "schematic_file",
            entry,
            "S360-400 must not carry a schematic_file value while it is "
            "not verified.",
        )

    def test_s360_410_poe_psu_is_not_verified(self) -> None:
        """PACKAGE-POE-410-001 / 2026-05-28 evidence audit.

        Locks in the option-4 outcome of
        docs/package-poe-410-001-audit.md: the S360-410 schematic PDF is
        committed (HW-ASSETS-410) and the BOM is on file
        (HW-BOM-ASSETS-002), but silkscreen pin-1, PoE link-up,
        isolation / Hi-pot / leakage, J2-harness identity
        (HW-002 OQ#6 / S360-100-BENCH-001), and PCB-level evidence are
        still missing. The schematic_status: verified JSON-only PR is
        owed to a separate later PR after those evidence rows close.
        """
        entry = _entry_by_sku("S360-410")
        self.assertNotEqual(
            entry.get("schematic_status"),
            "verified",
            "S360-410 must remain cataloged_unverified; PACKAGE-POE-410-001 "
            "audit (docs/package-poe-410-001-audit.md) records that "
            "silkscreen / bench / isolation / J2-harness evidence is not "
            "yet on file. Promoting to 'verified' requires the separate "
            "S360-410-SCHEMATIC-STATUS-VERIFIED JSON-only PR after E2 + "
            "E8-E12 close.",
        )
        self.assertNotIn(
            "schematic_file",
            entry,
            "S360-410 must not carry a schematic_file value while it is "
            "not verified.",
        )

    def test_expected_still_unverified_skus_remain_unverified(self) -> None:
        for sku in EXPECTED_STILL_UNVERIFIED_SKUS:
            with self.subTest(sku=sku):
                entry = _entry_by_sku(sku)
                self.assertEqual(
                    entry.get("schematic_status"),
                    "cataloged_unverified",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)

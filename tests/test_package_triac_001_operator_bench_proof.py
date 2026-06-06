#!/usr/bin/env python3
"""PACKAGE-TRIAC-001 invariants for the FanTRIAC operator bench proof doc.

PACKAGE-TRIAC-001 authors the operator bench *proof container* for the
blocked ``Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`` product:
``docs/package-triac-001-operator-bench-proof.md``. It is an
operator-evidence record (template + procedure) that stays ``PENDING``
until a real bench run fills it in. Creating the container is docs-only:
it must not clear the blocker, publish firmware, or claim any bench /
compliance / hardware proof.

These tests pin the structural invariants so a future regression cannot:

  * fabricate a recorded operator PASS while the catalog still blocks the
    product (the proof's ``PENDING`` state is coupled to the catalog
    blocker staying ``blocked``);
  * drift the schematic-verified pin mapping the bench depends on
    (gate ``GPIO14`` = ``TRI_GPIO1`` -> U1 MOC3023M; zero-cross
    ``GPIO13`` = ``TRI_GPIO2`` -> OK1 EL814);
  * silently promote the FanTRIAC product off its ``status: blocked``
    posture or flip ``webflash_build_matrix`` while PACKAGE-TRIAC-001 and
    COMPLIANCE-001 are still the recorded gates.

When the operator bench is actually run and PASSes, the human-reviewed
PR that clears the PACKAGE-TRIAC-001 half of the blocker updates the
catalog, the doc, and this test together (COMPLIANCE-001 still gates the
publish).

Run with::

    python3 tests/test_package_triac_001_operator_bench_proof.py

or::

    python3 -m unittest tests.test_package_triac_001_operator_bench_proof -v
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any, Iterator

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs" / "package-triac-001-operator-bench-proof.md"
CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"
VARIANTS_PATH = REPO_ROOT / "config" / "room-bundle-fan-variants.json"

FANTRIAC_CONFIG = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"


def _walk(obj: Any) -> Iterator[Any]:
    """Yield every node in a nested JSON structure (dicts, lists, scalars)."""
    yield obj
    if isinstance(obj, dict):
        for value in obj.values():
            yield from _walk(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from _walk(item)


class TestPackageTriac001OperatorBenchProofDoc(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = DOC_PATH.read_text(encoding="utf-8")
        cls.lines = cls.text.splitlines()
        cls.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        cls.variants = json.loads(VARIANTS_PATH.read_text(encoding="utf-8"))
        cls.fantriac = cls._find_fantriac_product(cls.catalog)

    @staticmethod
    def _find_fantriac_product(catalog: dict) -> dict:
        for product in catalog.get("products", []):
            if product.get("config_string") == FANTRIAC_CONFIG:
                return product
        raise AssertionError(
            f"{FANTRIAC_CONFIG} missing from config/product-catalog.json"
        )

    # --- the proof container itself ------------------------------------

    def test_doc_exists_with_blocker_id_title(self) -> None:
        self.assertTrue(DOC_PATH.is_file(), f"missing {DOC_PATH}")
        first_line = self.lines[0]
        self.assertTrue(first_line.startswith("# "), "doc must open with an H1")
        self.assertIn("PACKAGE-TRIAC-001", first_line)
        self.assertIn("Operator Bench Proof", first_line)

    def test_status_is_pending(self) -> None:
        self.assertIn("**Status:** PENDING", self.text)
        self.assertIn("operator bench not yet run", self.text)
        # No row may be flipped to a recorded verdict while PENDING.
        self.assertIn("stays `PENDING` until filled from a real run", self.text)

    def test_docs_only_scope_declared(self) -> None:
        self.assertIn("Operator-evidence record. Docs only.", self.text)
        self.assertIn(
            "asserts **no** firmware, manifest, release, or WebFlash change",
            self.text,
        )

    def test_no_compliance_claim_and_compliance_remains_gate(self) -> None:
        # The bench proves timing/waveform/thermal, never electrical safety.
        self.assertIn("makes **no** isolation, creepage, clearance, EMI", self.text)
        self.assertIn("Those stay with `COMPLIANCE-001`.", self.text)
        self.assertIn("`COMPLIANCE-001` as the sole remaining gate", self.text)

    def test_schematic_verified_pin_mapping(self) -> None:
        for needle in (
            "gate `GPIO14`",
            "zero-cross `GPIO13`",
            "`TRI_GPIO1`",
            "`TRI_GPIO2`",
            "MOC3023M",
            "EL814",
        ):
            self.assertIn(needle, self.text, f"pin-mapping detail missing: {needle}")

    def test_bench_firmware_uses_production_pins(self) -> None:
        self.assertIn("gate_pin: GPIO14", self.text)
        self.assertIn("number: GPIO13", self.text)
        self.assertIn("platform: ac_dimmer", self.text)
        # Leading-edge phase cut for a latching TRIAC.
        self.assertIn("method: leading", self.text)

    def test_attestation_template_is_unfilled(self) -> None:
        # Placeholder operator/date and the unresolved PASS / FAIL verdict
        # guard against a fabricated, "completed" attestation being committed.
        self.assertIn("| Operator | ____ |", self.text)
        self.assertIn("| Date | ____ |", self.text)
        self.assertIn("| Overall result | PASS / FAIL |", self.text)

    # --- coupling to the live source-of-truth config -------------------

    def test_catalog_fantriac_stays_blocked(self) -> None:
        self.assertEqual(self.fantriac.get("status"), "blocked")
        self.assertIs(self.fantriac.get("webflash_build_matrix"), False)
        blocker = self.fantriac.get("blocker", "")
        self.assertIn("PACKAGE-TRIAC-001", blocker)
        self.assertIn("COMPLIANCE-001", blocker)

    def test_variants_still_record_operator_bench_gate(self) -> None:
        gates = []
        for node in _walk(self.variants):
            if not isinstance(node, dict):
                continue
            if node.get("requires_operator_bench") == "PACKAGE-TRIAC-001":
                gates.append(node)
        self.assertTrue(
            gates,
            "config/room-bundle-fan-variants.json must still record "
            "requires_operator_bench == PACKAGE-TRIAC-001",
        )

    def test_pending_proof_is_coupled_to_blocked_catalog(self) -> None:
        # While the catalog blocks FanTRIAC, the proof must stay a PENDING
        # template (no recorded overall PASS). A real bench PASS is a
        # separate human-reviewed PR that clears the blocker and updates
        # the doc and this test together.
        catalog_blocked = self.fantriac.get("status") == "blocked"
        doc_pending = (
            "**Status:** PENDING" in self.text
            and "| Overall result | PASS / FAIL |" in self.text
        )
        self.assertTrue(catalog_blocked, "FanTRIAC must currently stay blocked")
        self.assertTrue(
            doc_pending,
            "proof must stay PENDING while the catalog blocker is unresolved",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

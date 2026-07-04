#!/usr/bin/env python3
"""PACKAGE-TRIAC-001 invariants for the FanTRIAC operator bench proof doc.

PACKAGE-TRIAC-001 authored the operator bench *proof container* for the
blocked ``Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`` product:
``docs/package-triac-001-operator-bench-proof.md``. The container started
``PENDING`` (#728), ``PACKAGE-TRIAC-001-PARAMS`` (#738) recorded the
partial bench (Steps A, B, C, E PASS on the real Manrose fan motor) and
folded the bench-confirmed parameters into
``packages/expansions/fan_triac.yaml``, and ``PACKAGE-TRIAC-001-CLOSE``
recorded the operator-reported Step F results (cold boots / warm reboots /
stability soak — PASS; evidence class: operator observation, no log
capture): Steps A–F all PASS. ``PACKAGE-TRIAC-001-RECONFIRM-001`` then
recorded the operator's closure of the full-composition re-confirm via
closure path (a) — his explicit statement, 2026-06-10, that the Step F
image was the full composition. The re-confirm exists to check that the
sensor stack's I2C traffic, the LD2450 UART, and WiFi activity do not
perturb the dimmer timing; production parameters alone cannot prove
that, which is why the row waited for the explicit statement instead of
being inferred. ``PACKAGE-TRIAC-001-ATTEST-CLOSE`` then recorded the
operator-reported bench-fact corrections — every bench run (including
the Step F boot/reboot cycles previously dated 2026-06-09) ran on
2026-06-08, and local logs WERE captured on the bench laptop but are
not attached to the record (nothing implies they were reviewed or
attached) — and staged the final close-out: the status flips to
OPERATOR ATTESTATION RECORDED BELOW, next steps point solely at the
commissioning PR (``TRIAC-COMMISSIONING-001``), and a designed-to-fail
guard below holds the close-out branch red until the operator himself
fills the Operator and Signature cells (the cells are staged EMPTY; no
attestation content is ever machine-written).

DOCS-DISPOSITION-001 (Step 3, archive batch B) archived the attested
proof container ``docs/package-triac-001-operator-bench-proof.md``:
deleted from the tree with a provenance row in ``docs/archive-index.md``,
its full content (operator attestation included) recoverable verbatim
from the indexed SHA. Nothing in the record was rewritten and no
attestation content was authored, edited, or summarised. The doc-pinning
tests were retired with the doc; what remains here are the live
source-of-truth config guards, so a regression cannot:

  * silently drop the catalog's citation of the attested proof container
    or the governing resolution record;
  * promote FanTRIAC off its experimental self-build mains lane posture
    (never stable / recommended / default / buyable / kit-exposed) or
    weaken the ``requires_operator_bench`` gate recorded in
    ``config/room-bundle-fan-variants.json``.

FanTRIAC posture changes remain human-review-only.

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
# The proof container docs/package-triac-001-operator-bench-proof.md was
# archived under DOCS-DISPOSITION-001; its path stays the catalog's cited
# bench_proof value and must stay recorded in the archive index.
DOC_REL = "docs/package-triac-001-operator-bench-proof.md"
ARCHIVE_INDEX = REPO_ROOT / "docs" / "archive-index.md"
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

    # --- the archived proof container -----------------------------------

    def test_proof_container_recorded_in_archive_index(self) -> None:
        # ARCHIVE means delete plus index, never rewrite: the container's
        # content (operator attestation included) stays recoverable
        # verbatim from the SHA recorded in docs/archive-index.md, and the
        # catalog keeps citing the container by its original path.
        self.assertIn(
            DOC_REL,
            ARCHIVE_INDEX.read_text(encoding="utf-8"),
            "the archived PACKAGE-TRIAC-001 proof container must be "
            "recorded in docs/archive-index.md",
        )

    # --- coupling to the live source-of-truth config -------------------

    def test_catalog_fantriac_commissioned_to_experimental_lane(self) -> None:
        # TRIAC-COMMISSIONING-001 (this commissioning PR) cleared the
        # PACKAGE-TRIAC-001 half of the blocker and moved FanTRIAC into the
        # experimental self-build mains lane: the catalog flips to status
        # preview on the experimental channel with a webflash-builds row, while
        # the bench-proof doc keeps its historical close-out statements (this PR
        # does not edit the doc). The catalog cites the attested proof and the
        # governing resolution record, and every permanent tooth survives.
        self.assertEqual(self.fantriac.get("status"), "preview")
        self.assertEqual(self.fantriac.get("channel"), "experimental")
        self.assertIs(self.fantriac.get("webflash_build_matrix"), True)
        self.assertEqual(
            self.fantriac.get("bench_proof"),
            "docs/package-triac-001-operator-bench-proof.md",
        )
        self.assertEqual(
            self.fantriac.get("governing_decision"),
            "docs/decisions/COMPLIANCE-001-RESOLUTION-001.md",
        )
        reason = self.fantriac.get("reason", "")
        self.assertIn("PACKAGE-TRIAC-001", reason)
        self.assertIn("COMPLIANCE-001", reason)
        posture = self.fantriac.get("experimental_lane_posture", {})
        self.assertIs(posture.get("never_stable"), True)
        self.assertIs(posture.get("never_buyable"), True)
        self.assertIs(posture.get("never_in_kit_or_kit_picker"), True)
        self.assertIs(
            posture.get("self_build_board_never_placed_on_market_by_sense360"), True
        )

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

    def test_close_out_decoupling_survives_in_catalog(self) -> None:
        # Closing the bench protocol was NOT clearing the blocker — only the
        # commissioning PR (TRIAC-COMMISSIONING-001) did that, moving the
        # catalog to status preview (experimental lane). The archived
        # bench-proof doc retains its historical close-out statements
        # verbatim at the indexed SHA; the live decoupling evidence is the
        # catalog's lane state, pinned here.
        self.assertEqual(
            self.fantriac.get("status"),
            "preview",
            "the commissioning PR moved FanTRIAC into the experimental lane",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

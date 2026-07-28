#!/usr/bin/env python3
"""AirIQ / VentIQ mutual-exclusion guard (SENSE360-CANONICALISATION-001 PR 11).

The charter requires the AirIQ (S360-210) / VentIQ (S360-211) mutual
exclusion to be machine-enforced: the two air-quality boards are separate
physical products and no composition may carry both. Before PR 11 the rule
lived in documentation and the WebFlash wizard matrix only; this module
pins it against the generated firmware-configuration contract (the PR 06
include-graph walker's output) and the bundle sources themselves.

Run with::

    python3 tests/test_airiq_ventiq_exclusion.py
"""

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTRACT = REPO_ROOT / "config" / "config-string-contract.json"

AIRIQ_SKU = "S360-210"
VENTIQ_SKU = "S360-211"


class AirIQVentIQExclusionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.configurations = json.loads(CONTRACT.read_text(encoding="utf-8"))[
            "configurations"
        ]

    def test_no_composition_carries_both_boards(self) -> None:
        offenders = []
        for row in self.configurations:
            boards = set(row.get("board_composition") or [])
            if AIRIQ_SKU in boards and VENTIQ_SKU in boards:
                offenders.append(row.get("config_string"))
        self.assertEqual(
            offenders,
            [],
            "AirIQ (S360-210) and VentIQ (S360-211) are mutually exclusive "
            "per composition; these configs carry both: " + ", ".join(offenders),
        )

    def test_guard_is_not_vacuous(self) -> None:
        # Both boards must actually appear somewhere, or the exclusion
        # check proves nothing.
        seen = set()
        for row in self.configurations:
            seen.update(row.get("board_composition") or [])
        self.assertIn(AIRIQ_SKU, seen)
        self.assertIn(VENTIQ_SKU, seen)

    def test_no_bundle_includes_both_board_packages(self) -> None:
        # Belt-and-braces over the raw bundle sources (the contract is
        # generated; this half catches an offender even before the
        # freshness gate forces regeneration).
        offenders = []
        for path in sorted((REPO_ROOT / "products").rglob("*.yaml")):
            if any(part.startswith(".") for part in path.parts):
                continue
            text = path.read_text(encoding="utf-8")
            active = "\n".join(
                line for line in text.splitlines()
                if not line.strip().startswith("#")
            )
            has_airiq = "boards/s360-210-airiq" in active
            has_ventiq = "boards/s360-211-ventiq" in active
            if has_airiq and has_ventiq:
                offenders.append(str(path.relative_to(REPO_ROOT)))
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()

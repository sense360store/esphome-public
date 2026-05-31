#!/usr/bin/env python3
"""Tests for the per-board feature & entity matrix (FEATURE-ENTITY-MATRIX-001).

Covers the planning / audit matrix at ``config/feature-entity-matrix.json``
which records, per board / module, the required Home Assistant sensor
entities (design-derived from the BOM / schematic) and the required HA
features (product intent), and audits each row as present / partial /
missing against the YAML that exists today. The matrix is planning and
audit data only; these tests pin its structural invariants and the
guardrails that no row implies a YAML change, that product intent is
never fabricated, and that every gap names a queued fill slice.

Uses Python's stdlib unittest (matching this repo's no-pytest convention
for Python validators). Run with::

    python3 tests/test_feature_entity_matrix.py

or::

    python3 -m unittest tests.test_feature_entity_matrix -v
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MATRIX_PATH = REPO_ROOT / "config" / "feature-entity-matrix.json"
HARDWARE_CATALOG_PATH = REPO_ROOT / "config" / "hardware-catalog.json"

ALLOWED_STATUS = frozenset({"present", "partial", "missing"})
ALLOWED_KIND = frozenset({"sensor-entity", "ha-feature"})
ALLOWED_DERIVATION = frozenset({"design-derived", "product-intent"})
ALLOWED_CONFIRM = frozenset(
    {"none", "needs-operator-confirm", "needs-schematic-reconcile"}
)

REQUIRED_GUARDRAILS = {
    "matrix_is_planning_and_audit_only",
    "matrix_does_not_change_any_board_or_feature_yaml",
    "matrix_does_not_change_any_product_or_webflash_yaml",
    "matrix_does_not_add_webflash_builds_or_artifacts",
    "matrix_does_not_promote_any_module_to_stable",
    "entity_and_feature_fills_happen_only_in_named_queued_slices",
    "intended_feature_set_is_never_fabricated",
    "unknown_product_intent_is_recorded_as_needs_operator_confirm",
}

REQUIRED_ROW_FIELDS = {
    "row",
    "kind",
    "derivation",
    "required",
    "status",
    "present_as",
    "defined_in",
    "confirm",
    "queued_fill_slice",
    "notes",
}


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class FeatureEntityMatrixStructureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.matrix = _load(MATRIX_PATH)
        cls.boards = cls.matrix["boards"]

    def test_top_level_metadata(self) -> None:
        self.assertEqual(self.matrix["schema_version"], 1)
        self.assertEqual(self.matrix["work_item"], "FEATURE-ENTITY-MATRIX-001")
        self.assertIn("PRE-HARDWARE-PREP-PLAN-001", self.matrix["parent_plan"])
        self.assertIn("Workstream C", self.matrix["parent_plan"])

    def test_guardrail_flags_present_and_true(self) -> None:
        guardrails = self.matrix["guardrails"]
        self.assertEqual(set(guardrails), REQUIRED_GUARDRAILS)
        for name, value in guardrails.items():
            self.assertIs(value, True, f"guardrail {name} must be true")

    def test_legends_cover_enums(self) -> None:
        self.assertEqual(set(self.matrix["row_status_legend"]), ALLOWED_STATUS)
        self.assertEqual(set(self.matrix["derivation_legend"]), ALLOWED_DERIVATION)
        self.assertEqual(set(self.matrix["confirm_flags"]), ALLOWED_CONFIRM)

    def test_boards_have_required_shape(self) -> None:
        seen_skus = set()
        for board in self.boards:
            sku = board["sku"]
            self.assertNotIn(sku, seen_skus, f"duplicate board sku {sku}")
            seen_skus.add(sku)
            for field in ("friendly_name", "schematic_status", "rows"):
                self.assertIn(field, board, f"{sku} missing {field}")
            self.assertIn("canonical_board_package", board)
            self.assertIsInstance(board["composed_of"], list)
            self.assertTrue(board["rows"], f"{sku} has no rows")

    def test_rows_constrained(self) -> None:
        for board in self.boards:
            sku = board["sku"]
            for row in board["rows"]:
                missing = REQUIRED_ROW_FIELDS - set(row)
                self.assertFalse(missing, f"{sku} row missing fields {missing}")
                self.assertIn(row["status"], ALLOWED_STATUS)
                self.assertIn(row["kind"], ALLOWED_KIND)
                self.assertIn(row["derivation"], ALLOWED_DERIVATION)
                self.assertIn(row["confirm"], ALLOWED_CONFIRM)


class FeatureEntityMatrixCoverageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.matrix = _load(MATRIX_PATH)
        cls.boards = cls.matrix["boards"]
        cls.catalog = _load(HARDWARE_CATALOG_PATH)

    def test_every_catalog_sku_is_covered(self) -> None:
        catalog_skus = {item["sku"] for item in self.catalog["items"]}
        matrix_skus = {board["sku"] for board in self.boards}
        uncovered = catalog_skus - matrix_skus
        self.assertFalse(
            uncovered, f"hardware-catalog SKUs absent from matrix: {sorted(uncovered)}"
        )

    def test_led_nightlight_worked_example_present(self) -> None:
        """C3: the LED night-light is recorded as a needs-operator-confirm gap."""
        led = next(b for b in self.boards if b["sku"] == "S360-300")
        nightlight = [
            row
            for row in led["rows"]
            if "night-light" in row["row"].lower()
        ]
        self.assertEqual(
            len(nightlight), 1, "S360-300 must record exactly one night-light row"
        )
        row = nightlight[0]
        self.assertEqual(row["status"], "missing")
        self.assertEqual(row["derivation"], "product-intent")
        self.assertEqual(row["confirm"], "needs-operator-confirm")
        self.assertIsNotNone(row["queued_fill_slice"])
        # The existing Night Mode switch / brightness number stay recorded as present.
        present_rows = {r["row"] for r in led["rows"] if r["status"] == "present"}
        self.assertTrue(
            any("Night mode" in r for r in present_rows),
            "existing Night Mode switch must stay recorded as present",
        )


class FeatureEntityMatrixGuardrailTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.matrix = _load(MATRIX_PATH)
        cls.rows = [
            (board["sku"], row)
            for board in cls.matrix["boards"]
            for row in board["rows"]
        ]

    def test_non_present_rows_queue_a_fill_slice(self) -> None:
        """C4: every gap must name the slice that will later fill it."""
        for sku, row in self.rows:
            if row["status"] != "present":
                self.assertIsNotNone(
                    row["queued_fill_slice"],
                    f"{sku} row '{row['row']}' is {row['status']} but queues no fill slice",
                )

    def test_present_rows_do_not_queue_fills(self) -> None:
        for sku, row in self.rows:
            if row["status"] == "present":
                self.assertIsNone(
                    row["queued_fill_slice"],
                    f"{sku} present row '{row['row']}' should not queue a fill slice",
                )

    def test_product_intent_gaps_need_operator_confirm(self) -> None:
        """C2: unknown product intent is never fabricated."""
        for sku, row in self.rows:
            if row["derivation"] == "product-intent" and row["status"] != "present":
                self.assertEqual(
                    row["confirm"],
                    "needs-operator-confirm",
                    f"{sku} product-intent gap '{row['row']}' must be needs-operator-confirm",
                )

    def test_present_rows_name_where_defined(self) -> None:
        for sku, row in self.rows:
            if row["status"] == "present":
                self.assertTrue(
                    row["defined_in"],
                    f"{sku} present row '{row['row']}' must say where it is defined",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)

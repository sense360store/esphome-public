#!/usr/bin/env python3
"""Unit tests for scripts/validate_product_catalog_consistency.py (PRODUCT-003).

These tests exercise the read-only consistency validator added in PRODUCT-003.
They lock in:

  * The current repo state passes ``validate_all()`` with zero errors.
  * The Release-One production entry passes every production-specific check
    (build-matrix presence, mapper agreement, wrapper basename, hardware SKU
    resolution).
  * The FanTRIAC blocked entry passes every blocked-specific check and is
    absent from the WebFlash build matrix.
  * Every ``legacy-compatible`` entry stays non-WebFlash-shippable
    (no ``artifact_name``, no ``webflash_wrapper``,
    ``webflash_build_matrix=false``, absent from the build matrix).
  * The artifact mapper agrees with every production catalog entry's
    declared ``artifact_name``.
  * Every production entry's ``webflash_wrapper`` basename equals
    lowercased ``config_string``.
  * The checklist mode resolves Release-One and returns all-passing items.

This file uses Python's stdlib ``unittest`` to match the no-pytest
convention the other validators in this repo use. Run with:

    python3 tests/test_product_catalog_consistency.py
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from product_name_mapper import generate_webflash_filename  # noqa: E402
from validate_product_catalog_consistency import (  # noqa: E402
    ProductCatalogConsistencyValidator,
    WEBFLASH_ELIGIBLE_STATUSES,
)

CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"

RELEASE_ONE_CONFIG_STRING = "Ceiling-POE-VentIQ-RoomIQ"
FANTRIAC_CONFIG_STRING = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"


def _load_catalog() -> Dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text())


def _load_builds() -> Dict[str, Any]:
    return json.loads(BUILDS_PATH.read_text())


def _products() -> List[Dict[str, Any]]:
    return [
        p
        for p in _load_catalog().get("products", [])
        if isinstance(p, dict)
    ]


def _build_config_strings() -> set:
    return {
        b.get("config_string")
        for b in _load_builds().get("builds", [])
        if isinstance(b, dict) and b.get("config_string")
    }


def _entry_by_config_string(cs: str) -> Dict[str, Any]:
    for p in _products():
        if p.get("config_string") == cs:
            return p
    raise AssertionError(f"no catalog entry with config_string={cs!r}")


class FullValidationTests(unittest.TestCase):
    """The current repo state must pass validate_all() with no errors."""

    def test_validate_all_passes_with_no_errors(self) -> None:
        v = ProductCatalogConsistencyValidator()
        self.assertTrue(v.load(), "validator failed to load required files")
        total, _failed = v.validate_all()
        self.assertGreater(total, 0)
        self.assertEqual(
            v.errors,
            [],
            "validate_all() reported errors:\n  - "
            + "\n  - ".join(v.errors),
        )


class ReleaseOneProductionTests(unittest.TestCase):
    """Targeted checks on the Release-One production entry."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.entry = _entry_by_config_string(RELEASE_ONE_CONFIG_STRING)
        cls.builds = _build_config_strings()

    def test_status_is_production(self) -> None:
        self.assertEqual(self.entry["status"], "production")

    def test_required_string_fields_present_and_non_empty(self) -> None:
        for field in (
            "config_string",
            "product_yaml",
            "webflash_wrapper",
            "artifact_name",
            "version",
            "channel",
            "hardware_status",
        ):
            with self.subTest(field=field):
                self.assertIn(field, self.entry)
                self.assertIsInstance(self.entry[field], str)
                self.assertNotEqual(self.entry[field], "")

    def test_required_map_fields_are_non_empty_maps(self) -> None:
        for field in ("hardware", "modules"):
            with self.subTest(field=field):
                value = self.entry.get(field)
                self.assertIsInstance(value, dict)
                self.assertGreater(len(value), 0)

    def test_webflash_build_matrix_is_true(self) -> None:
        self.assertIs(self.entry["webflash_build_matrix"], True)

    def test_appears_in_webflash_builds(self) -> None:
        self.assertIn(self.entry["config_string"], self.builds)

    def test_artifact_name_matches_mapper(self) -> None:
        product_key = Path(self.entry["product_yaml"]).stem
        produced = generate_webflash_filename(
            product_key,
            self.entry["version"],
            self.entry["channel"],
        )
        self.assertEqual(produced, self.entry["artifact_name"])

    def test_webflash_wrapper_exists(self) -> None:
        wrapper = REPO_ROOT / self.entry["webflash_wrapper"]
        self.assertTrue(wrapper.is_file(), f"missing: {wrapper}")

    def test_wrapper_basename_matches_config_string_lowercased(self) -> None:
        stem = Path(self.entry["webflash_wrapper"]).stem
        self.assertEqual(stem, self.entry["config_string"].lower())

    def test_hardware_skus_resolve_to_hardware_catalog(self) -> None:
        v = ProductCatalogConsistencyValidator()
        self.assertTrue(v.load())
        known = v._hardware_skus()  # noqa: SLF001
        self.assertGreater(len(known), 0)
        for slot, sku in self.entry["hardware"].items():
            with self.subTest(slot=slot, sku=sku):
                self.assertIn(sku, known)


class FanTriacBlockedTests(unittest.TestCase):
    """Targeted checks on the FanTRIAC blocked entry."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.entry = _entry_by_config_string(FANTRIAC_CONFIG_STRING)
        cls.builds = _build_config_strings()

    def test_status_is_blocked(self) -> None:
        self.assertEqual(self.entry["status"], "blocked")

    def test_required_blocked_fields_present(self) -> None:
        for field in ("blocker", "reason"):
            with self.subTest(field=field):
                self.assertIn(field, self.entry)
                self.assertIsInstance(self.entry[field], str)
                self.assertNotEqual(self.entry[field], "")

    def test_webflash_build_matrix_is_false(self) -> None:
        self.assertIs(self.entry["webflash_build_matrix"], False)

    def test_no_artifact_name(self) -> None:
        self.assertNotIn("artifact_name", self.entry)

    def test_not_in_webflash_builds(self) -> None:
        self.assertNotIn(self.entry["config_string"], self.builds)


class LegacyCompatibleSweepTests(unittest.TestCase):
    """Every legacy-compatible entry must remain non-WebFlash-shippable."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.entries = [
            p for p in _products() if p.get("status") == "legacy-compatible"
        ]
        cls.builds = _build_config_strings()

    def test_at_least_one_legacy_compatible_entry(self) -> None:
        self.assertGreater(len(self.entries), 0)

    def test_no_legacy_entry_has_artifact_name(self) -> None:
        for entry in self.entries:
            with self.subTest(entry=entry.get("legacy_config_id")):
                self.assertNotIn("artifact_name", entry)

    def test_no_legacy_entry_has_webflash_wrapper(self) -> None:
        for entry in self.entries:
            with self.subTest(entry=entry.get("legacy_config_id")):
                self.assertNotIn("webflash_wrapper", entry)

    def test_every_legacy_entry_webflash_build_matrix_is_false(self) -> None:
        for entry in self.entries:
            with self.subTest(entry=entry.get("legacy_config_id")):
                self.assertIs(entry.get("webflash_build_matrix"), False)

    def test_no_legacy_entry_appears_in_webflash_builds(self) -> None:
        for entry in self.entries:
            cs = entry.get("config_string")
            with self.subTest(entry=entry.get("legacy_config_id")):
                if isinstance(cs, str) and cs:
                    self.assertNotIn(cs, self.builds)


class ArtifactMapperAgreementTests(unittest.TestCase):
    """Mapper output must match every production entry's artifact_name."""

    def test_every_production_entry_matches_mapper(self) -> None:
        production = [
            p for p in _products() if p.get("status") == "production"
        ]
        self.assertGreater(len(production), 0)
        for entry in production:
            with self.subTest(config_string=entry.get("config_string")):
                product_key = Path(entry["product_yaml"]).stem
                produced = generate_webflash_filename(
                    product_key,
                    entry["version"],
                    entry["channel"],
                )
                self.assertEqual(produced, entry["artifact_name"])


class WrapperBasenameAgreementTests(unittest.TestCase):
    """Every WebFlash-eligible entry's wrapper basename equals lc(config_string)."""

    def test_every_eligible_wrapper_basename_matches_config_string(self) -> None:
        eligible = [
            p
            for p in _products()
            if p.get("status") in WEBFLASH_ELIGIBLE_STATUSES
            and isinstance(p.get("webflash_wrapper"), str)
            and isinstance(p.get("config_string"), str)
        ]
        self.assertGreater(len(eligible), 0)
        for entry in eligible:
            with self.subTest(config_string=entry["config_string"]):
                stem = Path(entry["webflash_wrapper"]).stem
                self.assertEqual(stem, entry["config_string"].lower())


class ChecklistModeTests(unittest.TestCase):
    """Checklist mode resolves real entries and surfaces unresolved ones."""

    def test_release_one_checklist_is_all_passing(self) -> None:
        v = ProductCatalogConsistencyValidator()
        self.assertTrue(v.load())
        items = v.checklist(identifier=RELEASE_ONE_CONFIG_STRING)
        self.assertGreater(len(items), 0)
        for ok, desc in items:
            with self.subTest(desc=desc):
                self.assertTrue(ok, f"checklist item failed: {desc}")

    def test_fantriac_checklist_is_all_passing(self) -> None:
        v = ProductCatalogConsistencyValidator()
        self.assertTrue(v.load())
        items = v.checklist(identifier=FANTRIAC_CONFIG_STRING)
        self.assertGreater(len(items), 0)
        for ok, desc in items:
            with self.subTest(desc=desc):
                self.assertTrue(ok, f"checklist item failed: {desc}")

    def test_unknown_identifier_returns_all_unchecked(self) -> None:
        v = ProductCatalogConsistencyValidator()
        self.assertTrue(v.load())
        items = v.checklist(identifier="No-Such-Config-At-All")
        self.assertGreater(len(items), 0)
        for ok, desc in items:
            with self.subTest(desc=desc):
                self.assertFalse(ok, f"unknown identifier should be unchecked: {desc}")

    def test_product_yaml_lookup_resolves_legacy_entry(self) -> None:
        v = ProductCatalogConsistencyValidator()
        self.assertTrue(v.load())
        items = v.checklist(product_yaml="products/sense360-core-c-poe.yaml")
        self.assertGreater(len(items), 0)
        for ok, desc in items:
            with self.subTest(desc=desc):
                self.assertTrue(ok, f"checklist item failed: {desc}")


if __name__ == "__main__":
    unittest.main(verbosity=2)

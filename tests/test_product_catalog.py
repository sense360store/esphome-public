#!/usr/bin/env python3
"""Validate config/product-catalog.json.

The product catalog is the lifecycle layer on top of the WebFlash build
matrix. It records, for each Sense360 product configuration, the lifecycle
status (production / preview / blocked / etc.), the product YAML, the
WebFlash wrapper, the artifact name (for production entries), the hardware
SKUs, and any blocked modules.

config/webflash-builds.json remains the authoritative WebFlash build
matrix; this catalog adds the lifecycle layer and is one-way cross-checked
against the build matrix here:

  - every catalog entry with status blocked must NOT appear in the
    WebFlash build matrix;
  - every entry in the WebFlash build matrix must appear in the catalog
    with a WebFlash-eligible status (production or preview).

This test uses Python's stdlib unittest (matching the no-pytest convention
the other validators in this repo use). Run with:

    python3 tests/test_product_catalog.py

or:

    python3 -m unittest tests.test_product_catalog -v
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
COMPAT_PATH = REPO_ROOT / "config" / "webflash-compatibility.json"
PRODUCTS_DIR = REPO_ROOT / "products"
WEBFLASH_WRAPPER_DIR = PRODUCTS_DIR / "webflash"
EXCLUDED_TOP_LEVEL_YAMLS = {"secrets.yaml"}

# Substrings that mark a ``legacy-compatible`` entry's ``notes`` field as
# explicitly non-WebFlash / non-Release-One / manual. Matched case-insensitively
# (PRODUCT-STALE-001 wording guard).
LEGACY_NOTES_REQUIRED_MARKERS = (
    "not release-one",
    "not webflash",
    "manual/custom",
    "manual users",
)

EXPECTED_LIFECYCLE_STATUSES = [
    "production",
    "preview",
    "compile-only",
    "hardware-pending",
    "blocked",
    "legacy-compatible",
    "deprecated",
    "removed",
]

WEBFLASH_ELIGIBLE_STATUSES = {"production", "preview"}

PRODUCTION_REQUIRED_FIELDS = (
    "config_string",
    "product_yaml",
    "webflash_wrapper",
    "artifact_name",
    "version",
    "channel",
    "hardware_status",
)

BLOCKED_REQUIRED_FIELDS = (
    "blocker",
    "reason",
)

ARTIFACT_PATTERN = "Sense360-{config_string}-v{version}-{channel}.bin"

RELEASE_ONE_CONFIG_STRING = "Ceiling-POE-VentIQ-RoomIQ"
FANTRIAC_CONFIG_STRING = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"


def _load_catalog() -> Dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text())


def _load_builds() -> Dict[str, Any]:
    return json.loads(BUILDS_PATH.read_text())


def _load_compat() -> Dict[str, Any]:
    return json.loads(COMPAT_PATH.read_text())


def _products(catalog: Dict[str, Any]) -> List[Dict[str, Any]]:
    return catalog.get("products", [])


def _top_level_product_yamls() -> List[str]:
    """Return repo-relative paths for every top-level product YAML.

    Excludes ``products/secrets.yaml`` and anything under
    ``products/webflash/``. The catalog must enumerate every path returned
    here.
    """
    paths: List[str] = []
    for child in sorted(PRODUCTS_DIR.iterdir()):
        if not child.is_file():
            continue
        if child.suffix != ".yaml":
            continue
        if child.name in EXCLUDED_TOP_LEVEL_YAMLS:
            continue
        paths.append(child.relative_to(REPO_ROOT).as_posix())
    return paths


def _webflash_wrapper_yamls() -> List[str]:
    """Return repo-relative paths for every WebFlash wrapper YAML."""
    if not WEBFLASH_WRAPPER_DIR.is_dir():
        return []
    paths: List[str] = []
    for child in sorted(WEBFLASH_WRAPPER_DIR.iterdir()):
        if not child.is_file():
            continue
        if child.suffix != ".yaml":
            continue
        paths.append(child.relative_to(REPO_ROOT).as_posix())
    return paths


class ProductCatalogTests(unittest.TestCase):
    """Schema, status, path, and cross-reference checks for the catalog."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = _load_catalog()
        cls.builds_doc = _load_builds()
        cls.compat = _load_compat()
        cls.products = _products(cls.catalog)
        cls.builds = cls.builds_doc.get("builds", [])
        cls.forbidden_tokens = frozenset(cls.compat.get("forbidden_tokens", []) or [])

    # ----- Top-level shape -------------------------------------------------

    def test_catalog_file_exists(self) -> None:
        self.assertTrue(
            CATALOG_PATH.is_file(),
            f"expected catalog at {CATALOG_PATH}",
        )

    def test_catalog_parses_as_json(self) -> None:
        self.assertIsInstance(self.catalog, dict)

    def test_schema_version_is_one(self) -> None:
        self.assertEqual(self.catalog.get("schema_version"), 1)

    def test_lifecycle_statuses_match_expected_enum(self) -> None:
        statuses = self.catalog.get("lifecycle_statuses")
        self.assertIsInstance(statuses, list)
        self.assertEqual(statuses, EXPECTED_LIFECYCLE_STATUSES)

    def test_products_is_non_empty_list(self) -> None:
        self.assertIsInstance(self.products, list)
        self.assertGreater(len(self.products), 0)

    # ----- Per-entry required fields and types ----------------------------

    def test_every_entry_has_status(self) -> None:
        for idx, entry in enumerate(self.products):
            with self.subTest(idx=idx, entry=entry):
                self.assertIn("status", entry)
                self.assertIn(entry["status"], EXPECTED_LIFECYCLE_STATUSES)

    def test_every_entry_has_product_yaml_path(self) -> None:
        for idx, entry in enumerate(self.products):
            with self.subTest(idx=idx, entry=entry):
                self.assertIn("product_yaml", entry)
                self.assertIsInstance(entry["product_yaml"], str)
                self.assertNotEqual(entry["product_yaml"], "")

    def test_every_entry_has_webflash_build_matrix_boolean(self) -> None:
        for idx, entry in enumerate(self.products):
            with self.subTest(idx=idx, entry=entry):
                self.assertIn("webflash_build_matrix", entry)
                self.assertIsInstance(entry["webflash_build_matrix"], bool)

    # ----- Path existence -------------------------------------------------

    def test_every_product_yaml_exists(self) -> None:
        for idx, entry in enumerate(self.products):
            with self.subTest(idx=idx, entry=entry):
                rel = entry["product_yaml"]
                self.assertTrue(
                    (REPO_ROOT / rel).is_file(),
                    f"product_yaml not found: {rel}",
                )

    def test_every_webflash_wrapper_when_present_exists(self) -> None:
        for idx, entry in enumerate(self.products):
            if "webflash_wrapper" not in entry:
                continue
            with self.subTest(idx=idx, entry=entry):
                rel = entry["webflash_wrapper"]
                self.assertIsInstance(rel, str)
                self.assertNotEqual(rel, "")
                self.assertTrue(
                    (REPO_ROOT / rel).is_file(),
                    f"webflash_wrapper not found: {rel}",
                )

    # ----- Catalog ↔ products/ enumeration --------------------------------

    def test_every_top_level_product_yaml_is_in_catalog(self) -> None:
        cataloged = {entry["product_yaml"] for entry in self.products}
        for rel in _top_level_product_yamls():
            with self.subTest(product_yaml=rel):
                self.assertIn(
                    rel,
                    cataloged,
                    f"product YAML {rel!r} has no entry in "
                    "config/product-catalog.json (PRODUCT-002 requires every "
                    "top-level product YAML to be enumerated; add a "
                    "legacy-compatible entry if it is not WebFlash-shippable)",
                )

    def test_no_product_yaml_points_at_webflash_wrapper(self) -> None:
        for idx, entry in enumerate(self.products):
            with self.subTest(idx=idx, entry=entry):
                rel = entry.get("product_yaml", "")
                self.assertFalse(
                    rel.startswith("products/webflash/"),
                    f"product_yaml {rel!r} points at a WebFlash wrapper; "
                    "wrappers may only appear in webflash_wrapper",
                )

    def test_webflash_wrappers_only_appear_in_webflash_wrapper_field(
        self,
    ) -> None:
        product_yaml_paths = {entry.get("product_yaml") for entry in self.products}
        for wrapper in _webflash_wrapper_yamls():
            with self.subTest(wrapper=wrapper):
                self.assertNotIn(
                    wrapper,
                    product_yaml_paths,
                    f"WebFlash wrapper {wrapper!r} is referenced as a "
                    "catalog product_yaml; wrappers may only appear in "
                    "webflash_wrapper",
                )

    # ----- Uniqueness -----------------------------------------------------

    def test_every_config_string_is_unique(self) -> None:
        config_strings = [
            entry["config_string"]
            for entry in self.products
            if "config_string" in entry
        ]
        self.assertEqual(
            len(config_strings),
            len(set(config_strings)),
            f"duplicate config_string values in catalog: {config_strings}",
        )

    def test_every_product_yaml_is_unique(self) -> None:
        paths = [entry["product_yaml"] for entry in self.products]
        self.assertEqual(
            len(paths),
            len(set(paths)),
            f"duplicate product_yaml values in catalog: {paths}",
        )

    def test_legacy_config_id_values_are_unique(self) -> None:
        ids = [
            entry["legacy_config_id"]
            for entry in self.products
            if "legacy_config_id" in entry
        ]
        self.assertEqual(
            len(ids),
            len(set(ids)),
            f"duplicate legacy_config_id values in catalog: {ids}",
        )

    def test_legacy_config_id_does_not_collide_with_config_string(
        self,
    ) -> None:
        config_strings = {
            entry["config_string"]
            for entry in self.products
            if "config_string" in entry
        }
        for idx, entry in enumerate(self.products):
            if "legacy_config_id" not in entry:
                continue
            with self.subTest(idx=idx, entry=entry):
                self.assertNotIn(
                    entry["legacy_config_id"],
                    config_strings,
                    "legacy_config_id "
                    f"{entry['legacy_config_id']!r} collides with a "
                    "WebFlash config_string; the two namespaces must stay "
                    "disjoint",
                )

    # ----- Production-entry contract --------------------------------------

    def test_production_entries_have_required_fields(self) -> None:
        for idx, entry in enumerate(self.products):
            if entry.get("status") != "production":
                continue
            with self.subTest(idx=idx, entry=entry):
                for field in PRODUCTION_REQUIRED_FIELDS:
                    self.assertIn(
                        field,
                        entry,
                        f"production entry missing required field '{field}'",
                    )
                    self.assertNotEqual(
                        entry[field],
                        "",
                        f"production entry field '{field}' is empty",
                    )
                self.assertTrue(
                    entry["webflash_build_matrix"],
                    "production entry must have webflash_build_matrix=true",
                )

    def test_production_entries_artifact_name_matches_pattern(self) -> None:
        for idx, entry in enumerate(self.products):
            if entry.get("status") != "production":
                continue
            with self.subTest(idx=idx, entry=entry):
                expected = ARTIFACT_PATTERN.format(
                    config_string=entry["config_string"],
                    version=entry["version"],
                    channel=entry["channel"],
                )
                self.assertEqual(
                    entry["artifact_name"],
                    expected,
                    f"artifact_name {entry['artifact_name']!r} "
                    f"does not match pattern {expected!r}",
                )

    # ----- Blocked-entry contract -----------------------------------------

    def test_blocked_entries_have_required_fields(self) -> None:
        for idx, entry in enumerate(self.products):
            if entry.get("status") != "blocked":
                continue
            with self.subTest(idx=idx, entry=entry):
                for field in BLOCKED_REQUIRED_FIELDS:
                    self.assertIn(
                        field,
                        entry,
                        f"blocked entry missing required field '{field}'",
                    )
                    self.assertNotEqual(
                        entry[field],
                        "",
                        f"blocked entry field '{field}' is empty",
                    )
                self.assertFalse(
                    entry["webflash_build_matrix"],
                    "blocked entry must have webflash_build_matrix=false",
                )

    # ----- Non-production cannot claim the build matrix -------------------

    def test_only_production_or_preview_have_webflash_build_matrix_true(
        self,
    ) -> None:
        for idx, entry in enumerate(self.products):
            with self.subTest(idx=idx, entry=entry):
                if entry["webflash_build_matrix"]:
                    self.assertIn(
                        entry["status"],
                        WEBFLASH_ELIGIBLE_STATUSES,
                        "only production or preview entries may set "
                        "webflash_build_matrix=true",
                    )

    def test_non_eligible_statuses_have_webflash_build_matrix_false(
        self,
    ) -> None:
        for idx, entry in enumerate(self.products):
            if entry.get("status") in WEBFLASH_ELIGIBLE_STATUSES:
                continue
            with self.subTest(idx=idx, entry=entry):
                self.assertFalse(
                    entry["webflash_build_matrix"],
                    f"entry with status {entry.get('status')!r} must have "
                    "webflash_build_matrix=false",
                )

    def test_legacy_compatible_entries_have_no_artifact_name(self) -> None:
        for idx, entry in enumerate(self.products):
            if entry.get("status") != "legacy-compatible":
                continue
            with self.subTest(idx=idx, entry=entry):
                self.assertNotIn(
                    "artifact_name",
                    entry,
                    "legacy-compatible entries must not have artifact_name; "
                    "they are not WebFlash-shippable",
                )

    def test_legacy_compatible_entries_have_no_config_string(self) -> None:
        # PRODUCT-STALE-001: the WebFlash config_string namespace is reserved
        # for WebFlash-shippable entries; legacy-compatible entries must use
        # legacy_config_id instead. Catalog description spells this out.
        for idx, entry in enumerate(self.products):
            if entry.get("status") != "legacy-compatible":
                continue
            with self.subTest(idx=idx, entry=entry):
                self.assertNotIn(
                    "config_string",
                    entry,
                    "legacy-compatible entries must not have config_string; "
                    "use legacy_config_id (the WebFlash config_string "
                    "namespace is reserved for WebFlash-shippable entries)",
                )

    def test_legacy_compatible_entry_notes_call_out_non_webflash(self) -> None:
        # PRODUCT-STALE-001: every legacy-compatible note must explicitly
        # signal that the entry is non-WebFlash / non-Release-One / manual so
        # the disclaimer cannot be silently edited away.
        for idx, entry in enumerate(self.products):
            if entry.get("status") != "legacy-compatible":
                continue
            with self.subTest(idx=idx, entry=entry):
                notes = entry.get("notes", "")
                self.assertIsInstance(
                    notes,
                    str,
                    "legacy-compatible entry must have a notes string",
                )
                self.assertNotEqual(
                    notes,
                    "",
                    "legacy-compatible entry notes must not be empty",
                )
                lowered = notes.lower()
                self.assertTrue(
                    any(marker in lowered for marker in LEGACY_NOTES_REQUIRED_MARKERS),
                    "legacy-compatible entry notes must call out "
                    "non-WebFlash / non-Release-One / manual status; "
                    f"got {notes!r} (expected one of "
                    f"{list(LEGACY_NOTES_REQUIRED_MARKERS)})",
                )

    def test_no_webflash_eligible_entry_uses_forbidden_token(self) -> None:
        # PRODUCT-STALE-001: catalog-layer mirror of the build-matrix-level
        # forbidden-token guard in tests/validate_webflash_builds.py. Catches
        # a stale alias (Bathroom / Comfort / Presence / Fan / FanAnalog)
        # leaking into a production or preview entry even before the
        # webflash_build_matrix flag is flipped.
        if not self.forbidden_tokens:
            self.skipTest("no forbidden_tokens declared in webflash-compatibility.json")
        for idx, entry in enumerate(self.products):
            if entry.get("status") not in WEBFLASH_ELIGIBLE_STATUSES:
                continue
            cs = entry.get("config_string")
            if not isinstance(cs, str) or not cs:
                continue
            for token in cs.split("-"):
                with self.subTest(idx=idx, config_string=cs, token=token):
                    self.assertNotIn(
                        token,
                        self.forbidden_tokens,
                        f"production/preview catalog entry {cs!r} contains "
                        f"forbidden token {token!r}; see "
                        "config/webflash-compatibility.json forbidden_tokens "
                        "and docs/webflash-contract.md",
                    )

    def test_blocked_entries_have_no_artifact_name(self) -> None:
        for idx, entry in enumerate(self.products):
            if entry.get("status") != "blocked":
                continue
            with self.subTest(idx=idx, entry=entry):
                self.assertNotIn(
                    "artifact_name",
                    entry,
                    "blocked entries must not have artifact_name",
                )

    # ----- Release-One specific assertions --------------------------------

    def test_release_one_entry_exists_and_is_production(self) -> None:
        matches = [
            e
            for e in self.products
            if e.get("config_string") == RELEASE_ONE_CONFIG_STRING
        ]
        self.assertEqual(
            len(matches),
            1,
            f"expected exactly one catalog entry for "
            f"{RELEASE_ONE_CONFIG_STRING!r}, found {len(matches)}",
        )
        self.assertEqual(matches[0]["status"], "production")

    def test_fantriac_entry_when_present_is_not_production(self) -> None:
        matches = [
            e for e in self.products if e.get("config_string") == FANTRIAC_CONFIG_STRING
        ]
        if not matches:
            self.skipTest(f"{FANTRIAC_CONFIG_STRING} not in catalog; nothing to check")
        for entry in matches:
            self.assertNotEqual(
                entry["status"],
                "production",
                f"{FANTRIAC_CONFIG_STRING} must not be production while "
                "HW-005 is open",
            )

    # ----- Cross-reference with WebFlash build matrix ---------------------

    def test_no_blocked_entry_in_webflash_build_matrix(self) -> None:
        build_strings = {
            b.get("config_string") for b in self.builds if isinstance(b, dict)
        }
        for idx, entry in enumerate(self.products):
            if entry.get("status") != "blocked":
                continue
            with self.subTest(idx=idx, entry=entry):
                cs = entry.get("config_string")
                self.assertNotIn(
                    cs,
                    build_strings,
                    f"blocked catalog entry {cs!r} must not appear in "
                    "config/webflash-builds.json",
                )

    def test_every_webflash_build_appears_in_catalog_with_eligible_status(
        self,
    ) -> None:
        catalog_by_cs = {
            e.get("config_string"): e for e in self.products if "config_string" in e
        }
        for idx, build in enumerate(self.builds):
            cs = build.get("config_string") if isinstance(build, dict) else None
            with self.subTest(idx=idx, build=build):
                self.assertIsNotNone(
                    cs,
                    "webflash-builds entry has no config_string",
                )
                self.assertIn(
                    cs,
                    catalog_by_cs,
                    f"webflash-builds entry {cs!r} is not present in "
                    "config/product-catalog.json",
                )
                entry = catalog_by_cs[cs]
                self.assertIn(
                    entry["status"],
                    WEBFLASH_ELIGIBLE_STATUSES,
                    f"webflash-builds entry {cs!r} maps to catalog status "
                    f"{entry['status']!r}, which is not WebFlash-eligible",
                )
                self.assertTrue(
                    entry["webflash_build_matrix"],
                    f"webflash-builds entry {cs!r} maps to a catalog entry "
                    "whose webflash_build_matrix is false",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)

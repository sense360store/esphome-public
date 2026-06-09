#!/usr/bin/env python3
"""Unit tests for scripts/promote_to_stable.py (esphome-public side).

Exercises the pure planning core (compute_plan) and the version normalizer in
isolation against in-memory catalog / build-matrix documents, so the field
edits and the refusal guards are pinned without touching the real
config/*.json files. The artifact name is checked against the SAME mapper the
release job and scripts/validate_product_catalog_consistency.py use.

Stdlib unittest, matching the no-pytest convention of the other validators::

    python3 tests/test_promote_to_stable.py
    python3 -m unittest tests.test_promote_to_stable -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import promote_to_stable as promote  # noqa: E402
from product_name_mapper import generate_webflash_filename  # noqa: E402


def make_catalog(entry_overrides=None):
    entry = {
        "config_string": "Ceiling-POE-AirIQ-RoomIQ",
        "status": "preview",
        "channel": "preview",
        "version": "1.0.0",
        "artifact_name": "Sense360-Ceiling-POE-AirIQ-RoomIQ-v1.0.0-preview.bin",
        "product_yaml": "products/webflash/ceiling-poe-airiq-roomiq.yaml",
        "webflash_wrapper": "products/webflash/ceiling-poe-airiq-roomiq.yaml",
        "webflash_build_matrix": True,
        "hardware_status": "cataloged",
        "hardware": {"core": "S360-100"},
        "modules": {"airiq": True},
        "stable_blocker": "some blocker prose",
    }
    if entry_overrides is not None:
        entry.update(entry_overrides)
    return {"products": [entry]}


def make_builds():
    return {
        "builds": [
            {
                "config_string": "Ceiling-POE-AirIQ-RoomIQ",
                "product_yaml": "products/webflash/ceiling-poe-airiq-roomiq.yaml",
                "artifact_name": "Sense360-Ceiling-POE-AirIQ-RoomIQ-v1.0.0-preview.bin",
                "channel": "preview",
                "channel_tier": "preview",
                "version": "1.0.0",
            }
        ]
    }


class NormalizeVersionTests(unittest.TestCase):
    def test_accepts_clean_and_strips_v(self):
        self.assertEqual(promote.normalize_version("1.0.5"), "1.0.5")
        self.assertEqual(promote.normalize_version("v1.2.3"), "1.2.3")
        self.assertEqual(promote.normalize_version(" 2.0 "), "2.0")

    def test_refuses_ambiguous(self):
        for bad in ("1.0.0-rc1", "1.0.x", "latest", "", "v", "1.0.0+build"):
            with self.assertRaises(promote.PromotionError):
                promote.normalize_version(bad)


class ComputePlanTests(unittest.TestCase):
    def test_field_changes_and_mapper_agreement(self):
        catalog = make_catalog()
        builds = make_builds()
        plan = promote.compute_plan(catalog, builds, "Ceiling-POE-AirIQ-RoomIQ", "1.1.0")

        expected_artifact = generate_webflash_filename(
            "ceiling-poe-airiq-roomiq", "1.1.0", "stable"
        )
        self.assertEqual(plan.artifact_name, expected_artifact)

        catalog_map = {c.field: c for c in plan.catalog_changes}
        self.assertEqual(catalog_map["status"].new, "production")
        self.assertEqual(catalog_map["channel"].new, "stable")
        self.assertEqual(catalog_map["version"].new, "1.1.0")
        self.assertEqual(catalog_map["artifact_name"].new, expected_artifact)
        # The sample catalog entry has no channel_tier, so it is not touched.
        self.assertNotIn("channel_tier", catalog_map)

        builds_map = {c.field: c for c in plan.builds_changes}
        self.assertEqual(builds_map["channel"].new, "stable")
        self.assertEqual(builds_map["version"].new, "1.1.0")
        self.assertEqual(builds_map["artifact_name"].new, expected_artifact)
        # The build row DOES carry channel_tier, so it mirrors to stable.
        self.assertEqual(builds_map["channel_tier"].new, "stable")
        # status is a catalog-only field; the build row is not given a status.
        self.assertNotIn("status", builds_map)

    def test_review_fields_listed_not_touched(self):
        plan = promote.compute_plan(
            make_catalog(), make_builds(), "Ceiling-POE-AirIQ-RoomIQ", "1.1.0"
        )
        self.assertIn("stable_blocker", plan.review_fields)
        # review fields are advisory only; never part of the applied changes.
        self.assertNotIn(
            "stable_blocker", {c.field for c in plan.catalog_changes}
        )

    def test_idempotent_when_already_production_at_same_version(self):
        catalog = make_catalog(
            {
                "status": "production",
                "channel": "stable",
                "version": "1.0.5",
                "artifact_name": generate_webflash_filename(
                    "ceiling-poe-airiq-roomiq", "1.0.5", "stable"
                ),
            }
        )
        builds = make_builds()
        builds["builds"][0].update(
            {
                "channel": "stable",
                "channel_tier": "stable",
                "version": "1.0.5",
                "artifact_name": generate_webflash_filename(
                    "ceiling-poe-airiq-roomiq", "1.0.5", "stable"
                ),
            }
        )
        plan = promote.compute_plan(catalog, builds, "Ceiling-POE-AirIQ-RoomIQ", "1.0.5")
        self.assertFalse(plan.has_changes)

    def test_refuses_unknown_config(self):
        with self.assertRaises(promote.PromotionError):
            promote.compute_plan(make_catalog(), make_builds(), "Ceiling-POE-Nope", "1.0.0")

    def test_refuses_blocked_status(self):
        catalog = make_catalog({"status": "blocked"})
        with self.assertRaises(promote.PromotionError):
            promote.compute_plan(catalog, make_builds(), "Ceiling-POE-AirIQ-RoomIQ", "1.0.0")

    def test_refuses_when_missing_from_build_matrix(self):
        builds = {"builds": []}
        with self.assertRaises(promote.PromotionError):
            promote.compute_plan(make_catalog(), builds, "Ceiling-POE-AirIQ-RoomIQ", "1.0.0")

    def test_refuses_when_no_product_yaml(self):
        catalog = make_catalog({"product_yaml": ""})
        with self.assertRaises(promote.PromotionError):
            promote.compute_plan(catalog, make_builds(), "Ceiling-POE-AirIQ-RoomIQ", "1.0.0")

    def test_warns_when_not_production_ready(self):
        # Drop a production-required field; compute_plan still plans but warns.
        catalog = make_catalog({"webflash_wrapper": ""})
        plan = promote.compute_plan(
            catalog, make_builds(), "Ceiling-POE-AirIQ-RoomIQ", "1.1.0"
        )
        self.assertTrue(any("webflash_wrapper" in w for w in plan.warnings))


if __name__ == "__main__":
    unittest.main()

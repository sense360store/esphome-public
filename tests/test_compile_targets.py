#!/usr/bin/env python3
"""Tests for the compile-only firmware validation lane (FW-COMPILE-MATRIX-001).

Covers the compile-only target list at
``config/compile-only-targets.json`` and the validator script at
``scripts/validate_compile_targets.py``. The compile-only lane is a CI
validation lane only; these tests pin the structural invariants and the
guardrails that no compile-only target implies new WebFlash exposure,
stable promotion, hardware proof, or webflash_build_matrix flips.

Uses Python's stdlib unittest (matching this repo's no-pytest
convention for Python validators). Run with::

    python3 tests/test_compile_targets.py

or::

    python3 -m unittest tests.test_compile_targets -v
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import validate_compile_targets as vct  # noqa: E402

TARGETS_PATH = REPO_ROOT / "config" / "compile-only-targets.json"
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
MATRIX_PATH = REPO_ROOT / "config" / "firmware-combination-matrix.json"
CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"

RELEASE_ONE_CONFIG_STRING = "Ceiling-POE-VentIQ-RoomIQ"
LED_PREVIEW_CONFIG_STRING = "Ceiling-POE-VentIQ-RoomIQ-LED"

# FW-COMPILE-POE-NONFAN-001: POE non-fan compile-only candidates added in
# this PR. Each maps to a product YAML under products/compile-only/.
POE_NONFAN_COMPILE_ONLY_CONFIG_STRINGS = frozenset(
    {
        "Ceiling-POE",
        "Ceiling-POE-RoomIQ",
        "Ceiling-POE-VentIQ",
        "Ceiling-POE-AirIQ",
        "Ceiling-POE-AirIQ-RoomIQ",
    }
)

POE_NONFAN_COMPILE_ONLY_PRODUCT_YAMLS = frozenset(
    {
        "products/compile-only/ceiling-poe.yaml",
        "products/compile-only/ceiling-poe-roomiq.yaml",
        "products/compile-only/ceiling-poe-ventiq.yaml",
        "products/compile-only/ceiling-poe-airiq.yaml",
        "products/compile-only/ceiling-poe-airiq-roomiq.yaml",
    }
)

# Fan / PWR tokens that this PR must not introduce as compile-only targets.
FORBIDDEN_FAN_TOKENS_FOR_THIS_PR = frozenset(
    {"FanRelay", "FanPWM", "FanDAC", "FanTRIAC"}
)
FORBIDDEN_POWER_TOKENS_FOR_THIS_PR = frozenset({"PWR"})

ALLOWED_SHIPMENT_STATUSES = frozenset(
    {"webflash-current", "preview-current", "compile-only"}
)

REQUIRED_TARGET_FIELDS = {
    "id",
    "product_yaml",
    "reason",
    "shipment_status",
    "hardware_required_for_validation",
    "webflash_exposure_allowed_now",
}


def _load(path: Path):
    return json.loads(path.read_text())


class CompileTargetsShapeTests(unittest.TestCase):
    """Shape / schema invariants of the compile-only target list."""

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(TARGETS_PATH)
        cls.targets = cls.doc["targets"]
        cls.by_id = {t["id"]: t for t in cls.targets}

    def test_schema_version_is_one(self):
        self.assertEqual(self.doc["schema_version"], 1)

    def test_sources_point_to_canonical_files(self):
        sources = self.doc.get("sources", {})
        self.assertEqual(sources.get("webflash_builds"), "config/webflash-builds.json")
        self.assertEqual(
            sources.get("firmware_combination_matrix"),
            "config/firmware-combination-matrix.json",
        )
        self.assertEqual(sources.get("product_catalog"), "config/product-catalog.json")

    def test_target_list_is_non_empty(self):
        self.assertGreater(len(self.targets), 0)

    def test_every_target_has_required_fields(self):
        for target in self.targets:
            missing = REQUIRED_TARGET_FIELDS - set(target.keys())
            self.assertFalse(
                missing,
                f"target {target.get('id')!r} missing fields {missing}",
            )

    def test_target_ids_are_unique(self):
        ids = [t["id"] for t in self.targets]
        self.assertEqual(len(ids), len(set(ids)))

    def test_totals_match_targets_length(self):
        totals = self.doc.get("totals") or {}
        self.assertEqual(totals.get("targets"), len(self.targets))

    def test_shipment_statuses_are_allowed(self):
        for target in self.targets:
            self.assertIn(
                target["shipment_status"],
                ALLOWED_SHIPMENT_STATUSES,
                f"{target['id']}: bad shipment_status",
            )

    def test_allowed_shipment_statuses_field_is_consistent(self):
        declared = set(self.doc.get("allowed_shipment_statuses") or [])
        self.assertEqual(declared, ALLOWED_SHIPMENT_STATUSES)


class CompileTargetsExistenceTests(unittest.TestCase):
    """Every target's product_yaml exists on disk."""

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(TARGETS_PATH)
        cls.targets = cls.doc["targets"]

    def test_every_product_yaml_exists(self):
        for target in self.targets:
            product_yaml = target["product_yaml"]
            path = REPO_ROOT / product_yaml
            self.assertTrue(
                path.is_file(),
                f"target {target['id']!r}: product_yaml not found at {product_yaml}",
            )


class CompileTargetsCrossRefTests(unittest.TestCase):
    """Cross-references between compile-only targets and the source catalogs."""

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(TARGETS_PATH)
        cls.targets = cls.doc["targets"]
        cls.builds = _load(BUILDS_PATH)
        cls.matrix = _load(MATRIX_PATH)
        cls.committed_configs = {
            entry["config_string"]
            for entry in (cls.builds.get("builds", []) or [])
            if entry.get("config_string")
        }
        cls.matrix_configs = {
            row["config_string"]
            for row in (cls.matrix.get("combinations", []) or [])
            if row.get("config_string")
        }

    def test_every_target_with_config_string_is_in_firmware_matrix(self):
        for target in self.targets:
            cs = target.get("config_string")
            if not cs:
                continue
            self.assertIn(
                cs,
                self.matrix_configs,
                f"target {target['id']!r}: config_string {cs!r} not present in "
                "config/firmware-combination-matrix.json",
            )

    def test_every_webflash_current_target_is_in_webflash_builds(self):
        for target in self.targets:
            if target.get("shipment_status") != "webflash-current":
                continue
            cs = target.get("config_string")
            self.assertIsNotNone(
                cs,
                f"target {target['id']!r}: shipment_status webflash-current "
                "requires a config_string",
            )
            self.assertIn(
                cs,
                self.committed_configs,
                f"target {target['id']!r}: shipment_status webflash-current "
                f"but config_string {cs!r} is not in "
                "config/webflash-builds.json",
            )

    def test_every_preview_current_target_is_in_webflash_builds(self):
        for target in self.targets:
            if target.get("shipment_status") != "preview-current":
                continue
            cs = target.get("config_string")
            self.assertIsNotNone(
                cs,
                f"target {target['id']!r}: shipment_status preview-current "
                "requires a config_string",
            )
            self.assertIn(
                cs,
                self.committed_configs,
                f"target {target['id']!r}: shipment_status preview-current "
                f"but config_string {cs!r} is not in "
                "config/webflash-builds.json",
            )

    def test_target_channels_match_committed_builds(self):
        builds_index = {
            entry["config_string"]: entry
            for entry in (self.builds.get("builds", []) or [])
            if entry.get("config_string")
        }
        for target in self.targets:
            expected_channel = target.get("expected_channel")
            cs = target.get("config_string")
            if not expected_channel or not cs:
                continue
            entry = builds_index.get(cs)
            if entry is None:
                continue
            self.assertEqual(
                entry.get("channel"),
                expected_channel,
                f"target {target['id']!r}: expected_channel "
                f"{expected_channel!r} does not match channel "
                f"{entry.get('channel')!r} in config/webflash-builds.json",
            )


class CompileTargetsGuardrailTests(unittest.TestCase):
    """Guardrails: compile-only targets must not imply WebFlash exposure or promotion."""

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(TARGETS_PATH)
        cls.targets = cls.doc["targets"]

    def test_no_target_declares_webflash_build_matrix(self):
        """compile-only targets must NOT redefine webflash_build_matrix."""
        for target in self.targets:
            self.assertNotIn(
                "webflash_build_matrix",
                target,
                f"target {target['id']!r}: must not declare "
                "webflash_build_matrix; that flag is owned by "
                "config/product-catalog.json",
            )

    def test_no_target_declares_artifact_name(self):
        """compile-only targets must NOT declare a release artifact name."""
        for target in self.targets:
            self.assertNotIn(
                "artifact_name",
                target,
                f"target {target['id']!r}: must not declare artifact_name; "
                "that field is owned by config/webflash-builds.json",
            )

    def test_compile_only_targets_do_not_claim_webflash_exposure(self):
        for target in self.targets:
            if target.get("shipment_status") == "compile-only":
                self.assertFalse(
                    target.get("webflash_exposure_allowed_now"),
                    f"target {target['id']!r}: shipment_status compile-only "
                    "must not claim webflash_exposure_allowed_now=true",
                )

    def test_webflash_current_targets_claim_webflash_exposure(self):
        for target in self.targets:
            if target.get("shipment_status") == "webflash-current":
                self.assertTrue(
                    target.get("webflash_exposure_allowed_now"),
                    f"target {target['id']!r}: shipment_status webflash-current "
                    "requires webflash_exposure_allowed_now=true",
                )

    def test_preview_current_targets_claim_webflash_exposure(self):
        for target in self.targets:
            if target.get("shipment_status") == "preview-current":
                self.assertTrue(
                    target.get("webflash_exposure_allowed_now"),
                    f"target {target['id']!r}: shipment_status preview-current "
                    "requires webflash_exposure_allowed_now=true",
                )

    def test_no_blocked_fantriac_or_pwr_target_is_unmarked(self):
        """FanTRIAC / PWR targets must be explicitly marked blocked / non-shippable."""
        for target in self.targets:
            cs = target.get("config_string") or ""
            tokens = cs.split("-") if cs else []
            has_blocked = ("FanTRIAC" in tokens) or ("PWR" in tokens)
            if not has_blocked:
                continue
            self.assertTrue(
                target.get("blocked"),
                f"target {target['id']!r}: carries FanTRIAC / PWR token "
                "but is not explicitly marked blocked=true",
            )
            self.assertFalse(
                target.get("webflash_exposure_allowed_now"),
                f"target {target['id']!r}: FanTRIAC / PWR target must not "
                "claim webflash_exposure_allowed_now=true",
            )
            self.assertNotIn(
                target.get("shipment_status"),
                {"webflash-current", "preview-current"},
                f"target {target['id']!r}: FanTRIAC / PWR target must not "
                "claim webflash-current / preview-current shipment_status",
            )


class CurrentWebflashCoverageTests(unittest.TestCase):
    """The current WebFlash builds are included as compile-only targets."""

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(TARGETS_PATH)
        cls.targets = cls.doc["targets"]
        cls.config_strings = {
            t.get("config_string") for t in cls.targets if t.get("config_string")
        }

    def test_release_one_is_a_compile_only_target(self):
        self.assertIn(RELEASE_ONE_CONFIG_STRING, self.config_strings)

    def test_led_preview_is_a_compile_only_target(self):
        self.assertIn(LED_PREVIEW_CONFIG_STRING, self.config_strings)


class PoeNonFanCompileOnlyCoverageTests(unittest.TestCase):
    """FW-COMPILE-POE-NONFAN-001: POE non-fan compile-only candidates.

    These tests pin the invariants for the POE non-fan compile-only
    candidates added by FW-COMPILE-POE-NONFAN-001: each candidate's
    product YAML exists on disk under ``products/compile-only/``,
    each candidate's ``config_string`` is present in
    ``config/firmware-combination-matrix.json``, each candidate is
    absent from ``config/webflash-builds.json``, each candidate
    declares ``shipment_status: compile-only`` /
    ``webflash_exposure_allowed_now: false`` /
    ``hardware_required_for_validation: true``, no candidate declares
    ``webflash_build_matrix`` or ``artifact_name``, and no candidate
    carries a forbidden fan / PWR token.
    """

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(TARGETS_PATH)
        cls.targets = cls.doc["targets"]
        cls.by_config = {
            t["config_string"]: t for t in cls.targets if t.get("config_string")
        }
        cls.builds = _load(BUILDS_PATH)
        cls.matrix = _load(MATRIX_PATH)
        cls.committed_configs = {
            entry["config_string"]
            for entry in (cls.builds.get("builds", []) or [])
            if entry.get("config_string")
        }
        cls.matrix_configs = {
            row["config_string"]
            for row in (cls.matrix.get("combinations", []) or [])
            if row.get("config_string")
        }

    def test_every_poe_nonfan_config_string_is_a_compile_only_target(self):
        for cs in POE_NONFAN_COMPILE_ONLY_CONFIG_STRINGS:
            self.assertIn(
                cs,
                self.by_config,
                f"POE non-fan config_string {cs!r} is not present in "
                "config/compile-only-targets.json",
            )

    def test_every_poe_nonfan_product_yaml_exists_on_disk(self):
        for rel in POE_NONFAN_COMPILE_ONLY_PRODUCT_YAMLS:
            self.assertTrue(
                (REPO_ROOT / rel).is_file(),
                f"POE non-fan compile-only product YAML not found: {rel}",
            )

    def test_every_poe_nonfan_config_string_is_in_firmware_matrix(self):
        for cs in POE_NONFAN_COMPILE_ONLY_CONFIG_STRINGS:
            self.assertIn(
                cs,
                self.matrix_configs,
                f"POE non-fan config_string {cs!r} is not present in "
                "config/firmware-combination-matrix.json",
            )

    def test_no_poe_nonfan_config_string_is_in_webflash_builds(self):
        for cs in POE_NONFAN_COMPILE_ONLY_CONFIG_STRINGS:
            self.assertNotIn(
                cs,
                self.committed_configs,
                f"POE non-fan compile-only target {cs!r} must NOT be "
                "present in config/webflash-builds.json (compile-only "
                "targets are not WebFlash exposed)",
            )

    def test_every_poe_nonfan_target_has_compile_only_shipment_status(self):
        for cs in POE_NONFAN_COMPILE_ONLY_CONFIG_STRINGS:
            target = self.by_config.get(cs)
            self.assertIsNotNone(target, f"missing compile-only target for {cs!r}")
            self.assertEqual(
                target["shipment_status"],
                "compile-only",
                f"target {target['id']!r}: shipment_status must be "
                "'compile-only' for POE non-fan compile-confidence targets",
            )

    def test_every_poe_nonfan_target_disallows_webflash_exposure(self):
        for cs in POE_NONFAN_COMPILE_ONLY_CONFIG_STRINGS:
            target = self.by_config.get(cs)
            self.assertIsNotNone(target, f"missing compile-only target for {cs!r}")
            self.assertFalse(
                target.get("webflash_exposure_allowed_now"),
                f"target {target['id']!r}: webflash_exposure_allowed_now "
                "must be false for POE non-fan compile-confidence targets",
            )

    def test_every_poe_nonfan_target_requires_hardware_for_validation(self):
        for cs in POE_NONFAN_COMPILE_ONLY_CONFIG_STRINGS:
            target = self.by_config.get(cs)
            self.assertIsNotNone(target, f"missing compile-only target for {cs!r}")
            self.assertTrue(
                target.get("hardware_required_for_validation"),
                f"target {target['id']!r}: "
                "hardware_required_for_validation must be true — "
                "compile-only is pre-hardware confidence, not "
                "hardware-validated readiness",
            )

    def test_no_poe_nonfan_target_declares_webflash_build_matrix(self):
        for cs in POE_NONFAN_COMPILE_ONLY_CONFIG_STRINGS:
            target = self.by_config.get(cs)
            self.assertIsNotNone(target, f"missing compile-only target for {cs!r}")
            self.assertNotIn(
                "webflash_build_matrix",
                target,
                f"target {target['id']!r}: must not declare "
                "webflash_build_matrix; that flag is owned by "
                "config/product-catalog.json",
            )

    def test_no_poe_nonfan_target_declares_artifact_name(self):
        for cs in POE_NONFAN_COMPILE_ONLY_CONFIG_STRINGS:
            target = self.by_config.get(cs)
            self.assertIsNotNone(target, f"missing compile-only target for {cs!r}")
            self.assertNotIn(
                "artifact_name",
                target,
                f"target {target['id']!r}: must not declare artifact_name; "
                "that field is owned by config/webflash-builds.json",
            )

    def test_no_poe_nonfan_target_declares_webflash_wrapper(self):
        for cs in POE_NONFAN_COMPILE_ONLY_CONFIG_STRINGS:
            target = self.by_config.get(cs)
            self.assertIsNotNone(target, f"missing compile-only target for {cs!r}")
            self.assertNotIn(
                "webflash_wrapper",
                target,
                f"target {target['id']!r}: must not declare webflash_wrapper; "
                "compile-only targets do not add WebFlash wrappers",
            )

    def test_no_poe_nonfan_product_yaml_lives_in_webflash_directory(self):
        for rel in POE_NONFAN_COMPILE_ONLY_PRODUCT_YAMLS:
            self.assertFalse(
                rel.startswith("products/webflash/"),
                f"POE non-fan compile-only product YAML {rel!r} must NOT "
                "live under products/webflash/; that directory is the "
                "WebFlash wrapper namespace",
            )

    def test_this_pr_introduces_no_fan_compile_only_target(self):
        """FW-COMPILE-POE-NONFAN-001 must not add any Fan* compile-only target."""
        for target in self.targets:
            cs = target.get("config_string") or ""
            tokens = set(cs.split("-")) if cs else set()
            forbidden_fan_tokens = tokens & FORBIDDEN_FAN_TOKENS_FOR_THIS_PR
            self.assertFalse(
                forbidden_fan_tokens,
                f"target {target['id']!r}: carries forbidden fan token "
                f"{sorted(forbidden_fan_tokens)} — this PR must not add "
                "any FanRelay / FanPWM / FanDAC / FanTRIAC compile-only "
                "target",
            )

    def test_this_pr_introduces_no_pwr_compile_only_target(self):
        """FW-COMPILE-POE-NONFAN-001 must not add any PWR compile-only target."""
        for target in self.targets:
            cs = target.get("config_string") or ""
            tokens = set(cs.split("-")) if cs else set()
            forbidden_power_tokens = tokens & FORBIDDEN_POWER_TOKENS_FOR_THIS_PR
            self.assertFalse(
                forbidden_power_tokens,
                f"target {target['id']!r}: carries forbidden power token "
                f"{sorted(forbidden_power_tokens)} — this PR must not add "
                "any PWR / S360-400 compile-only target",
            )

    def test_totals_match_expected_target_count(self):
        """Totals must match the sum of the two committed WebFlash targets
        plus the five FW-COMPILE-POE-NONFAN-001 candidates."""
        totals = self.doc.get("totals") or {}
        self.assertEqual(totals.get("targets"), len(self.targets))
        expected_min_targets = 2 + len(POE_NONFAN_COMPILE_ONLY_CONFIG_STRINGS)
        self.assertGreaterEqual(
            len(self.targets),
            expected_min_targets,
            "expected at least the two committed WebFlash targets plus "
            "the five POE non-fan compile-only candidates",
        )


class ValidatorScriptTests(unittest.TestCase):
    """The validator script behaves correctly via its module API."""

    def test_metadata_only_validation_passes_on_committed_targets(self):
        rc = vct.main(["--metadata-only"])
        self.assertEqual(rc, 0)

    def test_default_mode_is_metadata_only_and_passes(self):
        rc = vct.main([])
        self.assertEqual(rc, 0)

    def test_validate_metadata_rejects_unknown_shipment_status(self):
        doc = _load(TARGETS_PATH)
        doc["targets"] = [
            {
                "id": "bogus",
                "product_yaml": "products/webflash/ceiling-poe-ventiq-roomiq.yaml",
                "reason": "test",
                "shipment_status": "not-a-real-status",
                "hardware_required_for_validation": False,
                "webflash_exposure_allowed_now": False,
            }
        ]
        builds = _load(BUILDS_PATH)
        matrix = _load(MATRIX_PATH)
        failed, errors = vct.validate_metadata(doc, builds, matrix)
        self.assertGreaterEqual(failed, 1)
        self.assertTrue(
            any("shipment_status" in e for e in errors),
            f"expected shipment_status error in {errors!r}",
        )

    def test_validate_metadata_rejects_missing_product_yaml(self):
        doc = _load(TARGETS_PATH)
        doc["targets"] = [
            {
                "id": "missing-yaml",
                "product_yaml": "products/does-not-exist.yaml",
                "reason": "test",
                "shipment_status": "compile-only",
                "hardware_required_for_validation": False,
                "webflash_exposure_allowed_now": False,
            }
        ]
        builds = _load(BUILDS_PATH)
        matrix = _load(MATRIX_PATH)
        failed, errors = vct.validate_metadata(doc, builds, matrix)
        self.assertGreaterEqual(failed, 1)
        self.assertTrue(
            any("product_yaml not found" in e for e in errors),
            f"expected product_yaml not found error in {errors!r}",
        )

    def test_validate_metadata_rejects_unknown_config_string(self):
        doc = _load(TARGETS_PATH)
        doc["targets"] = [
            {
                "id": "unknown-cs",
                "product_yaml": "products/webflash/ceiling-poe-ventiq-roomiq.yaml",
                "config_string": "Ceiling-POE-VentIQ-RoomIQ-Bogus",
                "reason": "test",
                "shipment_status": "compile-only",
                "hardware_required_for_validation": False,
                "webflash_exposure_allowed_now": False,
            }
        ]
        builds = _load(BUILDS_PATH)
        matrix = _load(MATRIX_PATH)
        failed, errors = vct.validate_metadata(doc, builds, matrix)
        self.assertGreaterEqual(failed, 1)
        self.assertTrue(
            any("not present in" in e for e in errors),
            f"expected matrix lookup error in {errors!r}",
        )

    def test_validate_metadata_rejects_webflash_current_not_in_builds(self):
        doc = _load(TARGETS_PATH)
        doc["targets"] = [
            {
                "id": "fake-webflash-current",
                "product_yaml": "products/webflash/ceiling-poe-ventiq-roomiq.yaml",
                "config_string": "Ceiling-POE",
                "reason": "test",
                "shipment_status": "webflash-current",
                "hardware_required_for_validation": False,
                "webflash_exposure_allowed_now": True,
            }
        ]
        builds = _load(BUILDS_PATH)
        matrix = _load(MATRIX_PATH)
        failed, errors = vct.validate_metadata(doc, builds, matrix)
        self.assertGreaterEqual(failed, 1)
        self.assertTrue(
            any("webflash-builds.json" in e for e in errors),
            f"expected webflash-builds.json lookup error in {errors!r}",
        )

    def test_validate_metadata_rejects_unmarked_fantriac_target(self):
        doc = _load(TARGETS_PATH)
        doc["targets"] = [
            {
                "id": "fantriac-leak",
                "product_yaml": "products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml",
                "config_string": "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ",
                "reason": "test",
                "shipment_status": "compile-only",
                "hardware_required_for_validation": False,
                "webflash_exposure_allowed_now": False,
            }
        ]
        builds = _load(BUILDS_PATH)
        matrix = _load(MATRIX_PATH)
        failed, errors = vct.validate_metadata(doc, builds, matrix)
        self.assertGreaterEqual(failed, 1)
        self.assertTrue(
            any("FanTRIAC" in e or "blocked" in e for e in errors),
            f"expected FanTRIAC blocked-marker error in {errors!r}",
        )

    def test_validate_metadata_rejects_webflash_build_matrix_field(self):
        doc = _load(TARGETS_PATH)
        doc["targets"] = [
            {
                "id": "leaky-flag",
                "product_yaml": "products/webflash/ceiling-poe-ventiq-roomiq.yaml",
                "config_string": "Ceiling-POE-VentIQ-RoomIQ",
                "reason": "test",
                "shipment_status": "webflash-current",
                "hardware_required_for_validation": False,
                "webflash_exposure_allowed_now": True,
                "webflash_build_matrix": True,
            }
        ]
        builds = _load(BUILDS_PATH)
        matrix = _load(MATRIX_PATH)
        failed, errors = vct.validate_metadata(doc, builds, matrix)
        self.assertGreaterEqual(failed, 1)
        self.assertTrue(
            any("webflash_build_matrix" in e for e in errors),
            f"expected webflash_build_matrix rejection in {errors!r}",
        )

    def test_validate_metadata_rejects_duplicate_target_id(self):
        doc = _load(TARGETS_PATH)
        doc["targets"] = [
            {
                "id": "dup",
                "product_yaml": "products/webflash/ceiling-poe-ventiq-roomiq.yaml",
                "reason": "test",
                "shipment_status": "compile-only",
                "hardware_required_for_validation": False,
                "webflash_exposure_allowed_now": False,
            },
            {
                "id": "dup",
                "product_yaml": "products/webflash/ceiling-poe-ventiq-roomiq-led.yaml",
                "reason": "test",
                "shipment_status": "compile-only",
                "hardware_required_for_validation": False,
                "webflash_exposure_allowed_now": False,
            },
        ]
        builds = _load(BUILDS_PATH)
        matrix = _load(MATRIX_PATH)
        failed, errors = vct.validate_metadata(doc, builds, matrix)
        self.assertGreaterEqual(failed, 1)
        self.assertTrue(
            any("duplicate id" in e for e in errors),
            f"expected duplicate id error in {errors!r}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

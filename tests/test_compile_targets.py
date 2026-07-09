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

import contextlib
import io
import json
import shutil
import stat
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

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

# RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001: these POE non-fan config strings
# keep their compile-only SKELETON target (validated above) but ALSO now carry
# a reviewed PREVIEW build row in config/webflash-builds.json (addressed via a
# products/webflash wrapper, a distinct file from the skeleton). So they are
# legitimately present in the build ledger; only the pure compile-only
# skeletons (Ceiling-POE, Ceiling-POE-VentIQ, Ceiling-POE-AirIQ) must stay out.
POE_NONFAN_NOW_PREVIEW_BUILDS = frozenset(
    {
        "Ceiling-POE-RoomIQ",
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

# Fan / PWR tokens that the FW-COMPILE-POE-NONFAN-001 lane
# (products/compile-only/) must never introduce. Compile-only targets
# that carry a fan-driver token (e.g. FW-COMPILE-RELAY-001) live outside
# products/compile-only/ and reuse the canonical product YAML under
# products/ so the catalog enumeration / product-readiness gates apply.
FORBIDDEN_FAN_TOKENS_FOR_THIS_PR = frozenset(
    {"FanRelay", "FanPWM", "FanDAC", "FanTRIAC"}
)
FORBIDDEN_POWER_TOKENS_FOR_THIS_PR = frozenset({"PWR"})

# HW-RELEASE-001 (docs/hw-release-001.md, owner decision of record,
# 2026-07-09): the bench-proof documentation gate is retired and hardware
# readiness is owner-declared, so the fan-token configs now carry committed
# metadata build rows in config/webflash-builds.json plus wrappers under
# products/webflash/. The fan guardrails below are therefore CHANNEL /
# POSTURE guards, no longer absence guards: fan-token rows are allowed, but
# only on a non-stable channel — FanPWM / FanDAC rows are channel "preview",
# FanRelay / FanTRIAC rows are channel "experimental". Nothing fan-flavored
# is EVER channel "stable", recommended, buyable, a customer default, or in
# release_one_required_configs.
FAN_TOKEN_ALLOWED_CHANNEL = {
    "FanPWM": "preview",
    "FanDAC": "preview",
    "FanRelay": "experimental",
    "FanTRIAC": "experimental",
}


def _fan_build_rows(builds, token):
    """Committed build rows whose config_string carries the fan token."""
    return [
        row
        for row in (builds.get("builds", []) or [])
        if token in (row.get("config_string") or "").split("-")
    ]


# FW-COMPILE-RELAY-001: FanRelay compile-only target added in this PR.
# The product YAML was landed by PRODUCT-RELAY-001 / PR #564 and lives at
# the top level of products/ (not under products/webflash/ and not under
# products/compile-only/). The target is advanced / manual-warning-only,
# hardware-pending, and explicitly NOT WebFlash exposed.
FANRELAY_COMPILE_ONLY_TARGET_ID = "ceiling-poe-ventiq-fanrelay-roomiq-compile-only"
FANRELAY_COMPILE_ONLY_CONFIG_STRING = "Ceiling-POE-VentIQ-FanRelay-RoomIQ"
FANRELAY_COMPILE_ONLY_PRODUCT_YAML = (
    "products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml"
)

# FW-COMPILE-DAC-001: FanDAC compile-only validation target. The FanDAC
# compile-only skeleton lives UNDER products/compile-only/ (the only
# place that avoids the top-level product-catalog enumeration gate) and
# is the one explicitly-registered fan exception to the otherwise-non-fan
# products/compile-only/ lane. This compile-only target stays unchanged
# by PRODUCT-DAC-001 and is independent of the product YAML below.
#
# PRODUCT-DAC-001 has since landed the canonical FanDAC product YAML at
# the top level of products/ as the product-YAML-only / no-WebFlash-
# exposure slice (see tests/test_dac_product_readiness.py for the full
# non-WebFlash invariants). The top-level product YAML and the
# compile-only skeleton both reference config string Ceiling-POE-FanDAC
# but are separate files: the compile-only skeleton is the CI validation
# target; the product YAML is the consumer-facing deliverable.
FANDAC_COMPILE_ONLY_TARGET_ID = "ceiling-poe-fandac-compile-only"
FANDAC_COMPILE_ONLY_CONFIG_STRING = "Ceiling-POE-FanDAC"
FANDAC_COMPILE_ONLY_PRODUCT_YAML = "products/compile-only/ceiling-poe-fandac.yaml"
FANDAC_PRODUCT_YAML = "products/sense360-ceiling-poe-fandac.yaml"

# FW-COMPILE-PWM-001: FanPWM compile-only validation target. Like the
# FanDAC compile-only skeleton, the FanPWM skeleton lives UNDER
# products/compile-only/ (the only place that avoids the top-level
# product-catalog enumeration gate). It is the second explicitly-
# registered fan exception to the otherwise-non-fan products/compile-only/
# lane.
#
# PRODUCT-PWM-001 has since landed the canonical FanPWM product YAML at
# the top level of products/ as the product-YAML-only / no-WebFlash-
# exposure slice (see tests/test_pwm_product_readiness.py for the full
# non-WebFlash invariants). The top-level product YAML and the
# compile-only skeleton both reference config string Ceiling-POE-FanPWM
# but are separate files: the compile-only skeleton is the CI validation
# target; the product YAML is the consumer-facing deliverable. The
# PWM-drive-only package (PACKAGE-PWM-001-IMPLEMENT-001 / PR #590) exposes
# four SX1509 PWM-drive fan controllers and NO RPM / NO pulse_counter;
# this target makes no RPM claim.
FANPWM_COMPILE_ONLY_TARGET_ID = "ceiling-poe-fanpwm-compile-only"
FANPWM_COMPILE_ONLY_CONFIG_STRING = "Ceiling-POE-FanPWM"
FANPWM_COMPILE_ONLY_PRODUCT_YAML = "products/compile-only/ceiling-poe-fanpwm.yaml"
FANPWM_PRODUCT_YAML = "products/sense360-ceiling-poe-fanpwm.yaml"

# S360-311-NATIVE-FANPWM-YAML-001: the native ESP32-S3 GPIO FanPWM compile-only
# skeleton is the third explicitly-registered fan target allowed under
# products/compile-only/. It is the native-GPIO successor to the legacy SX1509
# skeleton (preserved unchanged): native ledc PWM-drive outputs + native
# pulse_counter tach inputs, NO SX1509 for PWM or tach. It is recorded
# compile_validation_status: pending-ci (no native compile run performed) and
# rpm_supported: false. Its full invariants are pinned by
# tests/test_native_fanpwm_yaml.py.
FANPWM_NATIVE_COMPILE_ONLY_TARGET_ID = "ceiling-poe-fanpwm-native-compile-only"
FANPWM_NATIVE_COMPILE_ONLY_PRODUCT_YAML = (
    "products/compile-only/ceiling-poe-fanpwm-native.yaml"
)

# TOPLEVEL-FAN-COMPILE-TARGETS-001: register the actual top-level FanPWM /
# FanDAC product YAMLs (landed by PRODUCT-PWM-001 / PRODUCT-DAC-001) as
# first-class compile-only targets, ALONGSIDE — not replacing — the
# products/compile-only/ skeletons. This closes the top-level product-YAML
# full-compile evidence gap that the skeleton-only registration left open
# and mirrors the FanRelay precedent, where the registered compile-only
# target IS the top-level product YAML. These targets were first registered
# metadata-only (compile_validation_status: pending-ci); FW-FULL-COMPILE-
# TOPLEVEL-FANS-001 then ran the full --compile lane against all 12 targets
# (every target rc=0) and recorded the result, so both top-level targets now
# carry compile_validation_status: validated-full-compile (local run; no CI
# run id claimed).
FANDAC_PRODUCT_COMPILE_ONLY_TARGET_ID = "ceiling-poe-fandac-product-compile-only"
FANPWM_PRODUCT_COMPILE_ONLY_TARGET_ID = "ceiling-poe-fanpwm-product-compile-only"

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
            if target.get("webflash_grammar_excluded") is True:
                # Intentionally absent from the WebFlash one-click grammar
                # (e.g. AirIQ+FanDAC under the fandac_conflicts_with_airiq
                # mutex, which the one-click surface cannot satisfy because it
                # cannot set the required FanDAC IC2 DIP switch to 0x5A). Such a
                # target is still compile-validated but must document why.
                self.assertTrue(
                    target.get("webflash_grammar_excluded_reason"),
                    f"target {target['id']!r}: webflash_grammar_excluded=true "
                    "requires a non-empty webflash_grammar_excluded_reason",
                )
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

    def test_no_poe_nonfan_compile_only_skeleton_is_in_webflash_builds(self):
        # The pure compile-only skeleton config strings stay out of the
        # WebFlash build matrix. The two that RELEASE-PREVIEW-WEBFLASH-BUILD-
        # ROWS-001 promoted to a preview build row (via a products/webflash
        # wrapper) are excluded here; they keep their skeleton target but are
        # legitimately release-eligible as preview builds.
        for cs in (
            POE_NONFAN_COMPILE_ONLY_CONFIG_STRINGS - POE_NONFAN_NOW_PREVIEW_BUILDS
        ):
            self.assertNotIn(
                cs,
                self.committed_configs,
                f"POE non-fan compile-only skeleton {cs!r} must NOT be "
                "present in config/webflash-builds.json (pure compile-only "
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

    def test_poe_nonfan_lane_introduces_no_fan_compile_only_target(self):
        """FW-COMPILE-POE-NONFAN-001 lane must not carry any Fan* token.

        Scoped to targets whose ``product_yaml`` lives under
        ``products/compile-only/`` (the directory FW-COMPILE-POE-NONFAN-001
        owns). Compile-only targets for fan-driver products live outside
        that directory (e.g. FW-COMPILE-RELAY-001 reuses the canonical
        ``products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml``).
        """
        for target in self.targets:
            product_yaml = target.get("product_yaml") or ""
            if not product_yaml.startswith("products/compile-only/"):
                continue
            # FW-COMPILE-DAC-001: the FanDAC compile-only target is the one
            # explicitly-registered fan target allowed under
            # products/compile-only/ — PRODUCT-DAC-001 is not landed, so a
            # top-level products/ YAML + catalog row is forbidden, leaving
            # products/compile-only/ as the only valid home. Its full
            # invariants are pinned by FanDACCompileOnlyCoverageTests.
            if target.get("id") == FANDAC_COMPILE_ONLY_TARGET_ID:
                continue
            # FW-COMPILE-PWM-001: the FanPWM compile-only target is the
            # second explicitly-registered fan target allowed under
            # products/compile-only/ — PRODUCT-PWM-001 is not landed, so a
            # top-level products/ YAML + catalog row is forbidden, leaving
            # products/compile-only/ as the only valid home. Its full
            # invariants are pinned by FanPWMCompileOnlyCoverageTests.
            if target.get("id") == FANPWM_COMPILE_ONLY_TARGET_ID:
                continue
            # S360-311-NATIVE-FANPWM-YAML-001: the native ESP32-S3 GPIO FanPWM
            # compile-only skeleton is the third explicitly-registered fan
            # target allowed under products/compile-only/ — the native-GPIO
            # successor to the legacy SX1509 skeleton. Its full invariants are
            # pinned by tests/test_native_fanpwm_yaml.py.
            if target.get("id") == FANPWM_NATIVE_COMPILE_ONLY_TARGET_ID:
                continue
            cs = target.get("config_string") or ""
            tokens = set(cs.split("-")) if cs else set()
            forbidden_fan_tokens = tokens & FORBIDDEN_FAN_TOKENS_FOR_THIS_PR
            self.assertFalse(
                forbidden_fan_tokens,
                f"target {target['id']!r}: carries forbidden fan token "
                f"{sorted(forbidden_fan_tokens)} — the "
                "FW-COMPILE-POE-NONFAN-001 lane (products/compile-only/) "
                "must not add any FanRelay / FanPWM / FanDAC / FanTRIAC "
                "compile-only target (except the explicitly-registered "
                "FW-COMPILE-DAC-001 FanDAC and FW-COMPILE-PWM-001 FanPWM "
                "validation targets)",
            )

    def test_poe_nonfan_lane_introduces_no_pwr_compile_only_target(self):
        """FW-COMPILE-POE-NONFAN-001 lane must not carry any PWR token.

        Scoped to targets whose ``product_yaml`` lives under
        ``products/compile-only/`` (the directory FW-COMPILE-POE-NONFAN-001
        owns). PWR / S360-400 compile-only targets remain blocked by
        COMPLIANCE-001 and are not in scope for any compile-only lane
        until a separate FW-COMPILE-PWR-001 slice is approved.
        """
        for target in self.targets:
            product_yaml = target.get("product_yaml") or ""
            if not product_yaml.startswith("products/compile-only/"):
                continue
            cs = target.get("config_string") or ""
            tokens = set(cs.split("-")) if cs else set()
            forbidden_power_tokens = tokens & FORBIDDEN_POWER_TOKENS_FOR_THIS_PR
            self.assertFalse(
                forbidden_power_tokens,
                f"target {target['id']!r}: carries forbidden power token "
                f"{sorted(forbidden_power_tokens)} — the "
                "FW-COMPILE-POE-NONFAN-001 lane (products/compile-only/) "
                "must not add any PWR / S360-400 compile-only target",
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


class FanRelayCompileOnlyCoverageTests(unittest.TestCase):
    """FW-COMPILE-RELAY-001: FanRelay compile-only validation target.

    Pins the invariants for the single FanRelay compile-only target
    added by FW-COMPILE-RELAY-001 on top of the PRODUCT-RELAY-001 /
    PR #564 product YAML. The target validates that the canonical
    FanRelay product YAML at
    ``products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`` still
    composes / substitutes / includes / generates code cleanly under
    the current ESPHome version. Compile success here is **not**
    WebFlash exposure, **not** a release artifact, **not** WebFlash
    import readiness, **not** a ``RELEASE-RELAY-001`` unblock, **not**
    compliance approval, **not** hardware proof, and **not** stable /
    preview promotion. WebFlash exposure remains blocked behind the
    separate ``WEBFLASH-RELAY-001`` slice.
    """

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(TARGETS_PATH)
        cls.targets = cls.doc["targets"]
        cls.by_id = {t["id"]: t for t in cls.targets if t.get("id")}
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
        cls.target = cls.by_id.get(FANRELAY_COMPILE_ONLY_TARGET_ID)

    def test_fanrelay_compile_only_target_exists(self):
        self.assertIsNotNone(
            self.target,
            f"FW-COMPILE-RELAY-001 must add the FanRelay compile-only "
            f"target with id {FANRELAY_COMPILE_ONLY_TARGET_ID!r} to "
            "config/compile-only-targets.json",
        )

    def test_fanrelay_compile_only_target_points_at_product_yaml(self):
        self.assertIsNotNone(self.target)
        self.assertEqual(
            self.target.get("product_yaml"),
            FANRELAY_COMPILE_ONLY_PRODUCT_YAML,
            f"FanRelay compile-only target must point at "
            f"{FANRELAY_COMPILE_ONLY_PRODUCT_YAML!r} — the PRODUCT-RELAY-001 "
            "/ PR #564 canonical FanRelay product YAML",
        )

    def test_fanrelay_compile_only_product_yaml_exists_on_disk(self):
        path = REPO_ROOT / FANRELAY_COMPILE_ONLY_PRODUCT_YAML
        self.assertTrue(
            path.is_file(),
            f"FanRelay compile-only product YAML not found at {path}",
        )

    def test_fanrelay_compile_only_config_string_is_correct(self):
        self.assertIsNotNone(self.target)
        self.assertEqual(
            self.target.get("config_string"),
            FANRELAY_COMPILE_ONLY_CONFIG_STRING,
        )

    def test_fanrelay_compile_only_config_string_is_in_firmware_matrix(self):
        self.assertIn(
            FANRELAY_COMPILE_ONLY_CONFIG_STRING,
            self.matrix_configs,
            f"FanRelay compile-only config_string "
            f"{FANRELAY_COMPILE_ONLY_CONFIG_STRING!r} must be present in "
            "config/firmware-combination-matrix.json",
        )

    def test_fanrelay_compile_only_shipment_status_is_compile_only(self):
        self.assertIsNotNone(self.target)
        self.assertEqual(
            self.target.get("shipment_status"),
            "compile-only",
            "FanRelay compile-only target must declare "
            "shipment_status: compile-only — FW-COMPILE-RELAY-001 does "
            "not advance the WebFlash exposure or release surface",
        )

    def test_fanrelay_compile_only_disallows_webflash_exposure(self):
        self.assertIsNotNone(self.target)
        self.assertFalse(
            self.target.get("webflash_exposure_allowed_now"),
            "FanRelay compile-only target must declare "
            "webflash_exposure_allowed_now: false — WebFlash Relay "
            "exposure remains blocked behind the separate "
            "WEBFLASH-RELAY-001 slice",
        )

    def test_fanrelay_compile_only_requires_hardware_for_validation(self):
        self.assertIsNotNone(self.target)
        self.assertTrue(
            self.target.get("hardware_required_for_validation"),
            "FanRelay compile-only target must declare "
            "hardware_required_for_validation: true — compile-only is "
            "pre-hardware confidence, not hardware-validated readiness",
        )

    def test_fanrelay_compile_only_is_marked_advanced_manual_warning_only(self):
        self.assertIsNotNone(self.target)
        self.assertTrue(
            self.target.get("advanced_manual_warning_only"),
            "FanRelay compile-only target must declare "
            "advanced_manual_warning_only: true — the FanRelay product "
            "is advanced / manual-warning-only per "
            "PRODUCT-RELAY-001-READINESS-REFRESH / PR #563 and "
            "PRODUCT-RELAY-001 / PR #564",
        )

    def test_fanrelay_compile_only_is_marked_hardware_pending(self):
        self.assertIsNotNone(self.target)
        self.assertTrue(
            self.target.get("hardware_pending"),
            "FanRelay compile-only target must declare "
            "hardware_pending: true — the FanRelay catalog row is "
            "status: hardware-pending per PRODUCT-RELAY-001 / PR #564",
        )

    def test_fanrelay_compile_only_does_not_declare_webflash_build_matrix(self):
        self.assertIsNotNone(self.target)
        self.assertNotIn(
            "webflash_build_matrix",
            self.target,
            "FanRelay compile-only target must not declare "
            "webflash_build_matrix; that flag is owned by "
            "config/product-catalog.json",
        )

    def test_fanrelay_compile_only_does_not_declare_artifact_name(self):
        self.assertIsNotNone(self.target)
        self.assertNotIn(
            "artifact_name",
            self.target,
            "FanRelay compile-only target must not declare "
            "artifact_name; no release artifact is built by "
            "FW-COMPILE-RELAY-001",
        )

    def test_fanrelay_compile_only_does_not_declare_webflash_wrapper(self):
        self.assertIsNotNone(self.target)
        self.assertNotIn(
            "webflash_wrapper",
            self.target,
            "FanRelay compile-only target must not declare "
            "webflash_wrapper; no WebFlash wrapper under "
            "products/webflash/ is added by FW-COMPILE-RELAY-001",
        )

    def test_fanrelay_compile_only_does_not_declare_expected_channel(self):
        self.assertIsNotNone(self.target)
        self.assertNotIn(
            "expected_channel",
            self.target,
            "FanRelay compile-only target must not declare "
            "expected_channel; compile-only targets do not pin a "
            "WebFlash channel",
        )

    def test_fanrelay_compile_only_target_is_not_blocked(self):
        self.assertIsNotNone(self.target)
        self.assertFalse(
            self.target.get("blocked"),
            "FanRelay compile-only target must declare blocked: false "
            "— the FanRelay product is product-YAML-landed and "
            "compile-only-eligible (it is not FanTRIAC / HW-005 / "
            "PWR / COMPLIANCE-001 blocked)",
        )

    def test_fanrelay_builds_rows_are_never_stable_channel(self):
        """HW-RELEASE-001 channel guard (was: FanRelay absent from builds).

        HW-RELEASE-001 (docs/hw-release-001.md, 2026-07-09) declared
        FanRelay metadata build rows in config/webflash-builds.json, so
        this guard pins CHANNEL POSTURE instead of absence: every
        FanRelay-bearing row must be channel "experimental" — never
        "stable".
        """
        rows = _fan_build_rows(self.builds, "FanRelay")
        self.assertTrue(
            rows,
            "expected at least one FanRelay metadata build row in "
            "config/webflash-builds.json (declared by HW-RELEASE-001)",
        )
        for row in rows:
            cfg = row.get("config_string")
            self.assertNotEqual(
                row.get("channel"),
                "stable",
                f"{cfg!r}: fan-token build rows are NEVER channel stable",
            )
            self.assertEqual(
                row.get("channel"),
                FAN_TOKEN_ALLOWED_CHANNEL["FanRelay"],
                f"{cfg!r}: FanRelay build rows are experimental-channel "
                "only (mains-adjacent, COMPLIANCE-001 lane posture; "
                "HW-RELEASE-001)",
            )

    def test_fanrelay_rows_declare_experimental_artifacts_only(self):
        """HW-RELEASE-001 artifact guard (was: no FanRelay token in builds).

        FanRelay-bearing rows may exist, but every declared artifact_name
        must carry the -experimental channel suffix — a -stable FanRelay
        artifact name is a regression of the never-stable posture.
        """
        rows = _fan_build_rows(self.builds, "FanRelay")
        self.assertTrue(rows, "expected FanRelay rows (HW-RELEASE-001)")
        for row in rows:
            cfg = row.get("config_string")
            artifact = row.get("artifact_name") or ""
            self.assertTrue(
                artifact.endswith("-experimental.bin"),
                f"{cfg!r}: FanRelay artifact_name {artifact!r} must end "
                "with -experimental.bin (never -stable.bin) per "
                "HW-RELEASE-001",
            )
            self.assertNotIn(
                "-stable",
                artifact,
                f"{cfg!r}: FanRelay artifact_name must never claim the "
                "stable channel",
            )

    def test_fanrelay_compile_only_target_is_not_in_release_one_required_configs(
        self,
    ):
        compat_path = REPO_ROOT / "config" / "webflash-compatibility.json"
        compat = _load(compat_path)
        required = compat.get("release_one_required_configs", []) or []
        self.assertNotIn(
            FANRELAY_COMPILE_ONLY_CONFIG_STRING,
            required,
            f"release_one_required_configs in "
            f"config/webflash-compatibility.json must not contain "
            f"{FANRELAY_COMPILE_ONLY_CONFIG_STRING!r} — "
            "FW-COMPILE-RELAY-001 does not promote FanRelay into "
            "Release-One required configs",
        )

    def test_fanrelay_product_yaml_does_not_live_in_webflash_directory(self):
        self.assertFalse(
            FANRELAY_COMPILE_ONLY_PRODUCT_YAML.startswith("products/webflash/"),
            f"FanRelay compile-only product YAML "
            f"{FANRELAY_COMPILE_ONLY_PRODUCT_YAML!r} must NOT live under "
            "products/webflash/ — that directory is the WebFlash "
            "wrapper namespace, and FW-COMPILE-RELAY-001 does not add a "
            "WebFlash wrapper",
        )

    def test_fanrelay_webflash_wrappers_are_backed_by_experimental_rows(self):
        """HW-RELEASE-001 wrapper guard (was: no FanRelay wrapper exists).

        HW-RELEASE-001 landed FanRelay wrappers under products/webflash/.
        Every FanRelay-named wrapper must be addressed by a committed
        config/webflash-builds.json row on the experimental channel — an
        undeclared wrapper, or one addressed by a stable row, is a
        regression.
        """
        webflash_dir = REPO_ROOT / "products" / "webflash"
        if not webflash_dir.is_dir():
            return
        rows_by_yaml = {
            row.get("product_yaml"): row
            for row in (self.builds.get("builds", []) or [])
        }
        for path in webflash_dir.glob("*.yaml"):
            name = path.name.lower()
            if "fanrelay" in name or "fan-relay" in name or "fan_relay" in name:
                rel = path.relative_to(REPO_ROOT).as_posix()
                row = rows_by_yaml.get(rel)
                self.assertIsNotNone(
                    row,
                    f"FanRelay wrapper {rel!r} must be declared as a "
                    "product_yaml in config/webflash-builds.json "
                    "(HW-RELEASE-001) — undeclared fan wrappers are "
                    "forbidden",
                )
                self.assertEqual(
                    row.get("channel"),
                    "experimental",
                    f"FanRelay wrapper {rel!r} must be addressed by an "
                    "experimental-channel row only — never stable",
                )

    def test_release_one_target_unchanged(self):
        """The Release-One compile-only target must remain unchanged."""
        target = self.by_config.get(RELEASE_ONE_CONFIG_STRING)
        self.assertIsNotNone(
            target,
            "Release-One compile-only target must remain present",
        )
        self.assertEqual(target.get("shipment_status"), "webflash-current")
        self.assertEqual(target.get("expected_channel"), "stable")
        self.assertTrue(target.get("webflash_exposure_allowed_now"))
        self.assertEqual(
            target.get("product_yaml"),
            "products/webflash/ceiling-poe-ventiq-roomiq.yaml",
        )

    def test_led_preview_target_unchanged(self):
        """The LED preview compile-only target must remain unchanged."""
        target = self.by_config.get(LED_PREVIEW_CONFIG_STRING)
        self.assertIsNotNone(
            target,
            "LED preview compile-only target must remain present",
        )
        self.assertEqual(target.get("shipment_status"), "preview-current")
        self.assertEqual(target.get("expected_channel"), "preview")
        self.assertTrue(target.get("webflash_exposure_allowed_now"))
        self.assertEqual(
            target.get("product_yaml"),
            "products/webflash/ceiling-poe-ventiq-roomiq-led.yaml",
        )

    def test_totals_match_expected_target_count_after_fanrelay(self):
        """Totals must match the targets array length after the FanRelay add."""
        totals = self.doc.get("totals") or {}
        self.assertEqual(totals.get("targets"), len(self.targets))
        expected_min_targets = 2 + len(POE_NONFAN_COMPILE_ONLY_CONFIG_STRINGS) + 1
        self.assertGreaterEqual(
            len(self.targets),
            expected_min_targets,
            "expected at least the two committed WebFlash targets, the "
            "five POE non-fan compile-only candidates, and the FanRelay "
            "compile-only target",
        )


class FanDACCompileOnlyCoverageTests(unittest.TestCase):
    """FW-COMPILE-DAC-001: FanDAC compile-only validation target.

    Pins the invariants for the single FanDAC compile-only target added
    by FW-COMPILE-DAC-001 after PACKAGE-DAC-001 / PR #573 implemented the
    FanDAC package and PR #574 recorded the gp8403 voltage-enum concern.
    The skeleton lives under ``products/compile-only/`` (PRODUCT-DAC-001
    is gated on this validation, so no top-level product YAML / catalog
    row may be added). Compile success here is **not** WebFlash exposure,
    **not** a release artifact, **not** a PRODUCT-DAC-001 /
    WEBFLASH-DAC-001 / RELEASE-DAC-001 unblock, **not** S360-312
    schematic / BOM verification, and **not** stable / preview promotion.
    Compile success is **not** claimed until CI runs the ``--compile``
    lane (ESPHome is not assumed available locally).
    """

    PACKAGE_FAN_GP8403 = REPO_ROOT / "packages" / "expansions" / "fan_gp8403.yaml"

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(TARGETS_PATH)
        cls.targets = cls.doc["targets"]
        cls.by_id = {t["id"]: t for t in cls.targets if t.get("id")}
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
        cls.target = cls.by_id.get(FANDAC_COMPILE_ONLY_TARGET_ID)

    def test_fandac_compile_only_target_exists(self):
        self.assertIsNotNone(
            self.target,
            f"FW-COMPILE-DAC-001 must add the FanDAC compile-only target "
            f"with id {FANDAC_COMPILE_ONLY_TARGET_ID!r} to "
            "config/compile-only-targets.json",
        )

    def test_fandac_compile_only_points_at_compile_only_skeleton(self):
        self.assertIsNotNone(self.target)
        self.assertEqual(
            self.target.get("product_yaml"),
            FANDAC_COMPILE_ONLY_PRODUCT_YAML,
        )

    def test_fandac_compile_only_skeleton_exists_on_disk(self):
        path = REPO_ROOT / FANDAC_COMPILE_ONLY_PRODUCT_YAML
        self.assertTrue(
            path.is_file(),
            f"FanDAC compile-only skeleton not found at {path}",
        )

    def test_fandac_skeleton_includes_the_fandac_package(self):
        """Target must include the fan_dac / fan_gp8403 package."""
        path = REPO_ROOT / FANDAC_COMPILE_ONLY_PRODUCT_YAML
        text = path.read_text()
        self.assertTrue(
            ("fan_dac.yaml" in text) or ("fan_gp8403.yaml" in text),
            "FanDAC compile-only skeleton must !include the FanDAC package "
            "(packages/expansions/fan_dac.yaml or fan_gp8403.yaml)",
        )
        self.assertIn(
            "!include",
            text,
            "FanDAC compile-only skeleton must compose packages via !include",
        )

    def test_fandac_config_string_is_correct(self):
        self.assertIsNotNone(self.target)
        self.assertEqual(
            self.target.get("config_string"),
            FANDAC_COMPILE_ONLY_CONFIG_STRING,
        )

    def test_fandac_config_string_is_in_firmware_matrix(self):
        self.assertIn(
            FANDAC_COMPILE_ONLY_CONFIG_STRING,
            self.matrix_configs,
            f"FanDAC compile-only config_string "
            f"{FANDAC_COMPILE_ONLY_CONFIG_STRING!r} must be present in "
            "config/firmware-combination-matrix.json",
        )

    def test_fandac_shipment_status_is_compile_only(self):
        self.assertIsNotNone(self.target)
        self.assertEqual(
            self.target.get("shipment_status"),
            "compile-only",
            "FanDAC target must be compile-only — it is NOT a WebFlash "
            "build (no webflash-current / preview-current)",
        )

    def test_fandac_disallows_webflash_exposure(self):
        self.assertIsNotNone(self.target)
        self.assertFalse(
            self.target.get("webflash_exposure_allowed_now"),
            "FanDAC compile-only target must declare "
            "webflash_exposure_allowed_now: false",
        )

    def test_fandac_requires_hardware_for_validation(self):
        self.assertIsNotNone(self.target)
        self.assertTrue(
            self.target.get("hardware_required_for_validation"),
            "FanDAC compile-only target must declare "
            "hardware_required_for_validation: true — compile-only is "
            "pre-hardware confidence, not hardware-validated readiness",
        )

    def test_fandac_target_is_not_blocked(self):
        self.assertIsNotNone(self.target)
        self.assertFalse(
            self.target.get("blocked"),
            "FanDAC compile-only target must declare blocked: false — "
            "FanDAC is not FanTRIAC / PWR / COMPLIANCE-001 blocked",
        )

    def test_fandac_does_not_declare_webflash_build_matrix(self):
        self.assertIsNotNone(self.target)
        self.assertNotIn(
            "webflash_build_matrix",
            self.target,
            "FanDAC compile-only target must not declare "
            "webflash_build_matrix; that flag is owned by "
            "config/product-catalog.json",
        )

    def test_fandac_does_not_declare_artifact_name(self):
        self.assertIsNotNone(self.target)
        self.assertNotIn(
            "artifact_name",
            self.target,
            "FanDAC compile-only target must not declare artifact_name; "
            "no release artifact is built by FW-COMPILE-DAC-001",
        )

    def test_fandac_does_not_declare_webflash_wrapper(self):
        self.assertIsNotNone(self.target)
        self.assertNotIn(
            "webflash_wrapper",
            self.target,
            "FanDAC compile-only target must not declare webflash_wrapper",
        )

    def test_fandac_builds_rows_are_never_stable_channel(self):
        """HW-RELEASE-001 channel guard (was: FanDAC absent from builds).

        HW-RELEASE-001 (docs/hw-release-001.md, 2026-07-09) declared
        FanDAC metadata build rows in config/webflash-builds.json, so this
        guard pins CHANNEL POSTURE instead of absence: every FanDAC-bearing
        row must be channel "preview" — never "stable".
        """
        rows = _fan_build_rows(self.builds, "FanDAC")
        self.assertTrue(
            rows,
            "expected at least one FanDAC metadata build row in "
            "config/webflash-builds.json (declared by HW-RELEASE-001)",
        )
        for row in rows:
            cfg = row.get("config_string")
            self.assertNotEqual(
                row.get("channel"),
                "stable",
                f"{cfg!r}: fan-token build rows are NEVER channel stable",
            )
            self.assertEqual(
                row.get("channel"),
                FAN_TOKEN_ALLOWED_CHANNEL["FanDAC"],
                f"{cfg!r}: FanDAC build rows are preview-channel only "
                "(HW-RELEASE-001)",
            )

    def test_fandac_rows_declare_preview_artifacts_only(self):
        """HW-RELEASE-001 artifact guard (was: no FanDAC token in builds).

        FanDAC-bearing rows may exist, but every declared artifact_name
        must carry the -preview channel suffix — a -stable FanDAC artifact
        name is a regression of the never-stable posture.
        """
        rows = _fan_build_rows(self.builds, "FanDAC")
        self.assertTrue(rows, "expected FanDAC rows (HW-RELEASE-001)")
        for row in rows:
            cfg = row.get("config_string")
            artifact = row.get("artifact_name") or ""
            self.assertTrue(
                artifact.endswith("-preview.bin"),
                f"{cfg!r}: FanDAC artifact_name {artifact!r} must end "
                "with -preview.bin (never -stable.bin) per HW-RELEASE-001",
            )
            self.assertNotIn(
                "-stable",
                artifact,
                f"{cfg!r}: FanDAC artifact_name must never claim the " "stable channel",
            )

    def test_fandac_target_is_not_in_release_one_required_configs(self):
        compat_path = REPO_ROOT / "config" / "webflash-compatibility.json"
        compat = _load(compat_path)
        required = compat.get("release_one_required_configs", []) or []
        self.assertNotIn(
            FANDAC_COMPILE_ONLY_CONFIG_STRING,
            required,
            "release_one_required_configs must not contain "
            f"{FANDAC_COMPILE_ONLY_CONFIG_STRING!r} — FW-COMPILE-DAC-001 "
            "does not promote FanDAC into Release-One required configs",
        )

    def test_fandac_skeleton_not_under_webflash_directory(self):
        self.assertFalse(
            FANDAC_COMPILE_ONLY_PRODUCT_YAML.startswith("products/webflash/"),
            "FanDAC compile-only skeleton must NOT live under "
            "products/webflash/ (the WebFlash wrapper namespace)",
        )

    def test_fandac_webflash_wrappers_are_backed_by_preview_rows(self):
        """HW-RELEASE-001 wrapper guard (was: no FanDAC wrapper exists).

        HW-RELEASE-001 landed FanDAC wrappers under products/webflash/.
        Every FanDAC-named wrapper must be addressed by a committed
        config/webflash-builds.json row on the preview channel — an
        undeclared wrapper, or one addressed by a stable row, is a
        regression.
        """
        webflash_dir = REPO_ROOT / "products" / "webflash"
        if not webflash_dir.is_dir():
            return
        rows_by_yaml = {
            row.get("product_yaml"): row
            for row in (self.builds.get("builds", []) or [])
        }
        for path in webflash_dir.glob("*.yaml"):
            name = path.name.lower()
            if "fandac" in name or "fan-dac" in name or "fan_dac" in name:
                rel = path.relative_to(REPO_ROOT).as_posix()
                row = rows_by_yaml.get(rel)
                self.assertIsNotNone(
                    row,
                    f"FanDAC wrapper {rel!r} must be declared as a "
                    "product_yaml in config/webflash-builds.json "
                    "(HW-RELEASE-001) — undeclared fan wrappers are "
                    "forbidden",
                )
                self.assertEqual(
                    row.get("channel"),
                    "preview",
                    f"FanDAC wrapper {rel!r} must be addressed by a "
                    "preview-channel row only — never stable",
                )

    def test_compile_only_skeleton_stays_separate_from_product_yaml(self):
        """The compile-only skeleton is not the top-level product YAML.

        FW-COMPILE-DAC-001 deliberately keeps the FanDAC compile-only
        skeleton UNDER products/compile-only/. PRODUCT-DAC-001 later
        landed the canonical product YAML at the top level of products/;
        the two must remain distinct files (the compile-only target must
        never silently repoint at the top-level product YAML).
        """
        self.assertTrue(
            FANDAC_COMPILE_ONLY_PRODUCT_YAML.startswith("products/compile-only/"),
            "FanDAC compile-only skeleton must stay under " "products/compile-only/",
        )
        self.assertNotEqual(
            FANDAC_COMPILE_ONLY_PRODUCT_YAML,
            FANDAC_PRODUCT_YAML,
            "The compile-only skeleton and the PRODUCT-DAC-001 product "
            "YAML must be distinct files",
        )
        self.assertIsNotNone(self.target)
        self.assertEqual(
            self.target.get("product_yaml"),
            FANDAC_COMPILE_ONLY_PRODUCT_YAML,
            "FanDAC compile-only target must keep pointing at the "
            "products/compile-only/ skeleton, not the top-level product "
            "YAML",
        )

    def test_product_dac_001_yaml_landed_at_top_level(self):
        """PRODUCT-DAC-001 landed the canonical FanDAC product YAML.

        The product-YAML-only / no-WebFlash-exposure slice adds the
        single canonical FanDAC product YAML at the top level of
        products/. The detailed non-WebFlash invariants
        (no webflash_build_matrix flip, no artifact_name, no wrapper, no
        config/webflash-builds.json row, full-compile + J3-silk +
        Cloudlift-harness caveats) are owned by
        tests/test_dac_product_readiness.py.
        """
        path = REPO_ROOT / FANDAC_PRODUCT_YAML
        self.assertTrue(
            path.is_file(),
            f"PRODUCT-DAC-001 must add the FanDAC product YAML at "
            f"{FANDAC_PRODUCT_YAML}",
        )

    def test_fandac_catalog_entries_keep_preview_posture(self):
        """FanDAC catalog posture guard (was: no wrapper under webflash/).

        HW-RELEASE-001 flipped the FanDAC catalog entries to status
        "preview" with a declared webflash_wrapper, so the guard is now a
        POSTURE pin: every FanDAC catalog entry must be status "preview"
        (never "production"), never recommended / buyable / a customer
        default, and any declared webflash_wrapper must exist on disk
        under products/webflash/.
        """
        catalog = _load(CATALOG_PATH)
        entries = [
            entry
            for entry in (catalog.get("products", []) or [])
            if "FanDAC" in (entry.get("config_string") or "").split("-")
        ]
        self.assertTrue(entries, "expected FanDAC catalog entries")
        for entry in entries:
            cfg = entry.get("config_string")
            self.assertNotEqual(
                entry.get("status"),
                "production",
                f"{cfg!r}: FanDAC catalog entries are never production",
            )
            self.assertEqual(
                entry.get("status"),
                "preview",
                f"{cfg!r}: HW-RELEASE-001 pins FanDAC catalog status " "to preview",
            )
            self.assertNotEqual(
                entry.get("channel"),
                "stable",
                f"{cfg!r}: FanDAC catalog channel is never stable",
            )
            self.assertFalse(
                entry.get("recommended", False),
                f"{cfg!r}: FanDAC is never recommended",
            )
            self.assertFalse(
                entry.get("buyable", False),
                f"{cfg!r}: FanDAC is never buyable",
            )
            self.assertFalse(
                entry.get("customer_default", False),
                f"{cfg!r}: FanDAC is never a customer default",
            )
            wrapper = entry.get("webflash_wrapper")
            if wrapper:
                self.assertTrue(
                    wrapper.startswith("products/webflash/"),
                    f"{cfg!r}: webflash_wrapper {wrapper!r} must live "
                    "under products/webflash/",
                )
                self.assertTrue(
                    (REPO_ROOT / wrapper).is_file(),
                    f"{cfg!r}: declared webflash_wrapper {wrapper!r} "
                    "must exist on disk",
                )

    def test_fandac_voltage_enum_concern_is_fixed(self):
        """The gp8403 voltage-enum concern must be resolved, not just tracked.

        ESPHome's gp8403 `voltage:` accepts only the bare enum tokens
        10V / 5V (https://esphome.io/components/output/gp8403); the prior
        invalid 0-10V / 0-5V strings are rejected by ESPHome config
        validation. The package substitutions must now feed a valid enum.
        """
        text = self.PACKAGE_FAN_GP8403.read_text()
        for active_assignment in (
            'fan_dac_1_output_range: "0-10V"',
            'fan_dac_2_output_range: "0-10V"',
            'fan_dac_1_output_range: "0-5V"',
            'fan_dac_2_output_range: "0-5V"',
        ):
            self.assertNotIn(
                active_assignment,
                text,
                "packages/expansions/fan_gp8403.yaml must not assign the "
                "invalid ESPHome gp8403 voltage enum string via "
                f"{active_assignment!r}; use 10V / 5V instead",
            )
        self.assertIn(
            'fan_dac_1_output_range: "10V"',
            text,
            "fan_dac_1_output_range must default to the valid ESPHome "
            "voltage enum 10V (customer-facing 0-10V)",
        )
        self.assertIn(
            'fan_dac_2_output_range: "10V"',
            text,
            "fan_dac_2_output_range must default to the valid ESPHome "
            "voltage enum 10V (customer-facing 0-10V)",
        )

    def test_fandac_compile_validated_by_full_compile_run(self):
        """The target must record the full compile passed (run 26364679370)."""
        self.assertIsNotNone(self.target)
        self.assertEqual(
            self.target.get("compile_validation_status"),
            "validated-full-compile",
            "FanDAC compile-only target must record "
            "compile_validation_status: validated-full-compile — the manual "
            "workflow_dispatch compile_mode=full run 26364679370 ran "
            "scripts/validate_compile_targets.py --compile against this YAML "
            "and passed (9 targets, conclusion success)",
        )

    def test_release_one_and_led_targets_unchanged(self):
        by_config = {
            t["config_string"]: t for t in self.targets if t.get("config_string")
        }
        r1 = by_config.get(RELEASE_ONE_CONFIG_STRING)
        self.assertIsNotNone(r1)
        self.assertEqual(r1.get("shipment_status"), "webflash-current")
        led = by_config.get(LED_PREVIEW_CONFIG_STRING)
        self.assertIsNotNone(led)
        self.assertEqual(led.get("shipment_status"), "preview-current")


class FanPWMCompileOnlyCoverageTests(unittest.TestCase):
    """FW-COMPILE-PWM-001: FanPWM compile-only validation target.

    Pins the invariants for the single FanPWM compile-only target added
    by FW-COMPILE-PWM-001 after PACKAGE-PWM-001-IMPLEMENT-001 / PR #590
    reconciled the FanPWM package to the PWM-drive-only scope (four
    independent SX1509 PWM-drive fan controllers; no RPM; no
    ``pulse_counter``; ``TachIO`` / ``GPIO16`` reserved) and
    CORE-ABSTRACT-BUS-001B landed the ``core_i2c`` bus the SX1509
    expander binds. The skeleton lives under ``products/compile-only/``
    (PRODUCT-PWM-001 is not landed, so no top-level product YAML /
    catalog row may be added). Compile success here is **not** WebFlash
    exposure, **not** a release artifact, **not** a PRODUCT-PWM-001 /
    WEBFLASH-PWM-001 / RELEASE-PWM-001 unblock, **not** S360-311
    schematic / BOM / bench verification, **not** RPM support, and
    **not** stable / preview promotion. Compile success is **not**
    claimed until CI runs the ``--compile`` lane (ESPHome is not assumed
    available locally).
    """

    PACKAGE_FAN_PWM = REPO_ROOT / "packages" / "expansions" / "fan_pwm.yaml"

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(TARGETS_PATH)
        cls.targets = cls.doc["targets"]
        cls.by_id = {t["id"]: t for t in cls.targets if t.get("id")}
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
        cls.target = cls.by_id.get(FANPWM_COMPILE_ONLY_TARGET_ID)

    @staticmethod
    def _active_lines(text):
        out = []
        for line in text.splitlines():
            stripped = line.lstrip()
            if not stripped or stripped.startswith("#"):
                continue
            out.append(line)
        return out

    def test_fanpwm_compile_only_target_exists(self):
        self.assertIsNotNone(
            self.target,
            f"FW-COMPILE-PWM-001 must add the FanPWM compile-only target "
            f"with id {FANPWM_COMPILE_ONLY_TARGET_ID!r} to "
            "config/compile-only-targets.json",
        )

    def test_fanpwm_compile_only_points_at_compile_only_skeleton(self):
        self.assertIsNotNone(self.target)
        self.assertEqual(
            self.target.get("product_yaml"),
            FANPWM_COMPILE_ONLY_PRODUCT_YAML,
        )

    def test_fanpwm_compile_only_skeleton_exists_on_disk(self):
        path = REPO_ROOT / FANPWM_COMPILE_ONLY_PRODUCT_YAML
        self.assertTrue(
            path.is_file(),
            f"FanPWM compile-only skeleton not found at {path}",
        )

    def test_fanpwm_skeleton_includes_the_fanpwm_package(self):
        """Target must include packages/expansions/fan_pwm.yaml."""
        path = REPO_ROOT / FANPWM_COMPILE_ONLY_PRODUCT_YAML
        text = path.read_text()
        self.assertIn(
            "fan_pwm.yaml",
            text,
            "FanPWM compile-only skeleton must !include the FanPWM package "
            "(packages/expansions/fan_pwm.yaml)",
        )
        self.assertIn(
            "!include",
            text,
            "FanPWM compile-only skeleton must compose packages via !include",
        )

    def test_fanpwm_config_string_is_correct(self):
        self.assertIsNotNone(self.target)
        self.assertEqual(
            self.target.get("config_string"),
            FANPWM_COMPILE_ONLY_CONFIG_STRING,
        )

    def test_fanpwm_config_string_is_in_firmware_matrix(self):
        self.assertIn(
            FANPWM_COMPILE_ONLY_CONFIG_STRING,
            self.matrix_configs,
            f"FanPWM compile-only config_string "
            f"{FANPWM_COMPILE_ONLY_CONFIG_STRING!r} must be present in "
            "config/firmware-combination-matrix.json",
        )

    def test_fanpwm_shipment_status_is_compile_only(self):
        self.assertIsNotNone(self.target)
        self.assertEqual(
            self.target.get("shipment_status"),
            "compile-only",
            "FanPWM target must be compile-only — it is NOT a WebFlash "
            "build (no webflash-current / preview-current)",
        )

    def test_fanpwm_disallows_webflash_exposure(self):
        self.assertIsNotNone(self.target)
        self.assertFalse(
            self.target.get("webflash_exposure_allowed_now"),
            "FanPWM compile-only target must declare "
            "webflash_exposure_allowed_now: false",
        )

    def test_fanpwm_requires_hardware_for_validation(self):
        self.assertIsNotNone(self.target)
        self.assertTrue(
            self.target.get("hardware_required_for_validation"),
            "FanPWM compile-only target must declare "
            "hardware_required_for_validation: true — compile-only is "
            "pre-hardware confidence, not hardware-validated readiness",
        )

    def test_fanpwm_target_is_not_blocked(self):
        self.assertIsNotNone(self.target)
        self.assertFalse(
            self.target.get("blocked"),
            "FanPWM compile-only target must declare blocked: false — "
            "FanPWM is a SELV low-voltage board, not FanTRIAC / PWR / "
            "COMPLIANCE-001 blocked",
        )

    def test_fanpwm_does_not_declare_webflash_build_matrix(self):
        self.assertIsNotNone(self.target)
        self.assertNotIn(
            "webflash_build_matrix",
            self.target,
            "FanPWM compile-only target must not declare "
            "webflash_build_matrix; that flag is owned by "
            "config/product-catalog.json",
        )

    def test_fanpwm_does_not_declare_artifact_name(self):
        self.assertIsNotNone(self.target)
        self.assertNotIn(
            "artifact_name",
            self.target,
            "FanPWM compile-only target must not declare artifact_name; "
            "no release artifact is built by FW-COMPILE-PWM-001",
        )

    def test_fanpwm_does_not_declare_webflash_wrapper(self):
        self.assertIsNotNone(self.target)
        self.assertNotIn(
            "webflash_wrapper",
            self.target,
            "FanPWM compile-only target must not declare webflash_wrapper",
        )

    def test_fanpwm_builds_rows_are_never_stable_channel(self):
        """HW-RELEASE-001 channel guard (was: FanPWM absent from builds).

        HW-RELEASE-001 (docs/hw-release-001.md, 2026-07-09) declared
        FanPWM metadata build rows in config/webflash-builds.json, so this
        guard pins CHANNEL POSTURE instead of absence: every FanPWM-bearing
        row must be channel "preview" — never "stable".
        """
        rows = _fan_build_rows(self.builds, "FanPWM")
        self.assertTrue(
            rows,
            "expected at least one FanPWM metadata build row in "
            "config/webflash-builds.json (declared by HW-RELEASE-001)",
        )
        for row in rows:
            cfg = row.get("config_string")
            self.assertNotEqual(
                row.get("channel"),
                "stable",
                f"{cfg!r}: fan-token build rows are NEVER channel stable",
            )
            self.assertEqual(
                row.get("channel"),
                FAN_TOKEN_ALLOWED_CHANNEL["FanPWM"],
                f"{cfg!r}: FanPWM build rows are preview-channel only "
                "(HW-RELEASE-001)",
            )

    def test_fanpwm_rows_declare_preview_artifacts_only(self):
        """HW-RELEASE-001 artifact guard (was: no FanPWM token in builds).

        FanPWM-bearing rows may exist, but every declared artifact_name
        must carry the -preview channel suffix — a -stable FanPWM artifact
        name is a regression of the never-stable posture.
        """
        rows = _fan_build_rows(self.builds, "FanPWM")
        self.assertTrue(rows, "expected FanPWM rows (HW-RELEASE-001)")
        for row in rows:
            cfg = row.get("config_string")
            artifact = row.get("artifact_name") or ""
            self.assertTrue(
                artifact.endswith("-preview.bin"),
                f"{cfg!r}: FanPWM artifact_name {artifact!r} must end "
                "with -preview.bin (never -stable.bin) per HW-RELEASE-001",
            )
            self.assertNotIn(
                "-stable",
                artifact,
                f"{cfg!r}: FanPWM artifact_name must never claim the " "stable channel",
            )

    def test_fanpwm_target_is_not_in_release_one_required_configs(self):
        compat_path = REPO_ROOT / "config" / "webflash-compatibility.json"
        compat = _load(compat_path)
        required = compat.get("release_one_required_configs", []) or []
        self.assertNotIn(
            FANPWM_COMPILE_ONLY_CONFIG_STRING,
            required,
            "release_one_required_configs must not contain "
            f"{FANPWM_COMPILE_ONLY_CONFIG_STRING!r} — FW-COMPILE-PWM-001 "
            "does not promote FanPWM into Release-One required configs",
        )

    def test_fanpwm_skeleton_not_under_webflash_directory(self):
        self.assertFalse(
            FANPWM_COMPILE_ONLY_PRODUCT_YAML.startswith("products/webflash/"),
            "FanPWM compile-only skeleton must NOT live under "
            "products/webflash/ (the WebFlash wrapper namespace)",
        )

    def test_fanpwm_webflash_wrappers_are_backed_by_preview_rows(self):
        """HW-RELEASE-001 wrapper guard (was: no FanPWM wrapper exists).

        HW-RELEASE-001 landed FanPWM wrappers under products/webflash/.
        Every FanPWM-named wrapper must be addressed by a committed
        config/webflash-builds.json row on the preview channel — an
        undeclared wrapper, or one addressed by a stable row, is a
        regression.
        """
        webflash_dir = REPO_ROOT / "products" / "webflash"
        if not webflash_dir.is_dir():
            return
        rows_by_yaml = {
            row.get("product_yaml"): row
            for row in (self.builds.get("builds", []) or [])
        }
        for path in webflash_dir.glob("*.yaml"):
            name = path.name.lower()
            if "fanpwm" in name or "fan-pwm" in name or "fan_pwm" in name:
                rel = path.relative_to(REPO_ROOT).as_posix()
                row = rows_by_yaml.get(rel)
                self.assertIsNotNone(
                    row,
                    f"FanPWM wrapper {rel!r} must be declared as a "
                    "product_yaml in config/webflash-builds.json "
                    "(HW-RELEASE-001) — undeclared fan wrappers are "
                    "forbidden",
                )
                self.assertEqual(
                    row.get("channel"),
                    "preview",
                    f"FanPWM wrapper {rel!r} must be addressed by a "
                    "preview-channel row only — never stable",
                )

    def test_fanpwm_skeleton_stays_under_compile_only(self):
        """The compile-only skeleton is not the top-level product YAML.

        FW-COMPILE-PWM-001 deliberately keeps the FanPWM compile-only
        skeleton UNDER products/compile-only/. PRODUCT-PWM-001 later
        landed the canonical product YAML at the top level of products/;
        the two must remain distinct files (the compile-only target must
        never silently repoint at the top-level product YAML).
        """
        self.assertTrue(
            FANPWM_COMPILE_ONLY_PRODUCT_YAML.startswith("products/compile-only/"),
            "FanPWM compile-only skeleton must stay under " "products/compile-only/",
        )
        self.assertNotEqual(
            FANPWM_COMPILE_ONLY_PRODUCT_YAML,
            FANPWM_PRODUCT_YAML,
            "The compile-only skeleton and the PRODUCT-PWM-001 product "
            "YAML must be distinct files",
        )
        self.assertIsNotNone(self.target)
        self.assertEqual(
            self.target.get("product_yaml"),
            FANPWM_COMPILE_ONLY_PRODUCT_YAML,
            "FanPWM compile-only target must keep pointing at the "
            "products/compile-only/ skeleton, not the top-level product "
            "YAML",
        )

    def test_product_pwm_001_yaml_landed_at_top_level(self):
        """PRODUCT-PWM-001 landed the canonical FanPWM product YAML.

        The product-YAML-only / no-WebFlash-exposure slice adds the single
        canonical FanPWM product YAML at the top level of products/. The
        detailed non-WebFlash invariants (no webflash_build_matrix flip,
        no artifact_name, no wrapper, no config/webflash-builds.json row,
        full-compile + bench caveats, no RPM) are owned by
        tests/test_pwm_product_readiness.py. The legacy standalone
        fan-board product (products/sense360-fan-pwm.yaml) predates this
        slice; the only other FanPWM-named YAML outside
        products/compile-only/ must be the PRODUCT-PWM-001 product YAML.
        """
        path = REPO_ROOT / FANPWM_PRODUCT_YAML
        self.assertTrue(
            path.is_file(),
            f"PRODUCT-PWM-001 must add the FanPWM product YAML at "
            f"{FANPWM_PRODUCT_YAML}",
        )
        products_dir = REPO_ROOT / "products"
        if not products_dir.is_dir():
            self.skipTest("products/ directory not present")
        compile_only_dir = products_dir / "compile-only"
        # The FanPWM composition now lives in the bundle that the product shim
        # pulls in; the bundle is an additional allowed FanPWM-named YAML.
        allowed = {
            "products/sense360-fan-pwm.yaml",
            FANPWM_PRODUCT_YAML,
            "products/bundles/ceiling-poe-fanpwm.yaml",
            # ROOM-BUNDLE-FAN-CONFIGS-001 room-bundle FanPWM previews
            # (shim + bundle, Bathroom + Kitchen); compile-pending, not
            # WebFlash-exposed.
            "products/sense360-ceiling-poe-ventiq-fanpwm-roomiq.yaml",
            "products/bundles/ceiling-poe-ventiq-fanpwm-roomiq.yaml",
            "products/sense360-ceiling-poe-airiq-fanpwm-roomiq.yaml",
            "products/bundles/ceiling-poe-airiq-fanpwm-roomiq.yaml",
            # HW-RELEASE-001 (docs/hw-release-001.md, 2026-07-09): the owner
            # decision declared preview-channel FanPWM build rows, so the
            # matching WebFlash wrappers now legitimately exist under
            # products/webflash/. Their never-stable channel posture is
            # pinned by test_fanpwm_webflash_wrappers_are_backed_by_
            # preview_rows / test_fanpwm_builds_rows_are_never_stable_channel.
            "products/webflash/ceiling-poe-fanpwm.yaml",
            "products/webflash/ceiling-poe-ventiq-fanpwm-roomiq.yaml",
            "products/webflash/ceiling-poe-airiq-fanpwm-roomiq.yaml",
        }
        offenders = []
        for path in products_dir.rglob("*.yaml"):
            if compile_only_dir in path.parents:
                continue
            name = path.name.lower()
            if "fanpwm" in name or "fan-pwm" in name or "fan_pwm" in name:
                rel = path.relative_to(REPO_ROOT).as_posix()
                if rel not in allowed:
                    offenders.append(rel)
        self.assertEqual(
            sorted(offenders),
            [],
            "Only the legacy fan-board YAML and the PRODUCT-PWM-001 product "
            f"YAML may carry a FanPWM name; unexpected: {sorted(offenders)!r}",
        )

    def test_fanpwm_catalog_entries_keep_preview_posture(self):
        """FanPWM catalog posture guard (was: no wrapper under webflash/).

        HW-RELEASE-001 flipped the FanPWM catalog entries to status
        "preview" with a declared webflash_wrapper, so the guard is now a
        POSTURE pin: every FanPWM catalog entry must be status "preview"
        (never "production"), never recommended / buyable / a customer
        default, and any declared webflash_wrapper must exist on disk
        under products/webflash/.
        """
        catalog = _load(CATALOG_PATH)
        entries = [
            entry
            for entry in (catalog.get("products", []) or [])
            if "FanPWM" in (entry.get("config_string") or "").split("-")
        ]
        self.assertTrue(entries, "expected FanPWM catalog entries")
        for entry in entries:
            cfg = entry.get("config_string")
            self.assertNotEqual(
                entry.get("status"),
                "production",
                f"{cfg!r}: FanPWM catalog entries are never production",
            )
            self.assertEqual(
                entry.get("status"),
                "preview",
                f"{cfg!r}: HW-RELEASE-001 pins FanPWM catalog status " "to preview",
            )
            self.assertNotEqual(
                entry.get("channel"),
                "stable",
                f"{cfg!r}: FanPWM catalog channel is never stable",
            )
            self.assertFalse(
                entry.get("recommended", False),
                f"{cfg!r}: FanPWM is never recommended",
            )
            self.assertFalse(
                entry.get("buyable", False),
                f"{cfg!r}: FanPWM is never buyable",
            )
            self.assertFalse(
                entry.get("customer_default", False),
                f"{cfg!r}: FanPWM is never a customer default",
            )
            wrapper = entry.get("webflash_wrapper")
            if wrapper:
                self.assertTrue(
                    wrapper.startswith("products/webflash/"),
                    f"{cfg!r}: webflash_wrapper {wrapper!r} must live "
                    "under products/webflash/",
                )
                self.assertTrue(
                    (REPO_ROOT / wrapper).is_file(),
                    f"{cfg!r}: declared webflash_wrapper {wrapper!r} "
                    "must exist on disk",
                )

    def test_fanpwm_target_makes_no_rpm_claim(self):
        self.assertIsNotNone(self.target)
        self.assertFalse(
            self.target.get("rpm_supported", False),
            "FanPWM compile-only target must not claim RPM support — the "
            "PWM-drive-only package exposes no per-fan or aggregate RPM",
        )

    def test_fanpwm_skeleton_exposes_no_rpm_or_pulse_counter(self):
        """The skeleton must wire no pulse_counter and no RPM entity."""
        text = (REPO_ROOT / FANPWM_COMPILE_ONLY_PRODUCT_YAML).read_text()
        for line in self._active_lines(text):
            self.assertNotIn(
                "pulse_counter",
                line,
                "FanPWM compile-only skeleton must not use pulse_counter on "
                f"any active line. Line: {line!r}",
            )
            low = line.lower()
            if "name:" in low or "unit_of_measurement:" in low:
                self.assertNotIn(
                    "rpm",
                    low,
                    "FanPWM compile-only skeleton must expose no RPM-named / "
                    f"RPM-unit entity (PWM-drive-only). Line: {line!r}",
                )

    def test_fanpwm_skeleton_does_not_bind_tachio_gpio16(self):
        """TachIO / GPIO16 stays reserved/pending — not an active binding."""
        text = (REPO_ROOT / FANPWM_COMPILE_ONLY_PRODUCT_YAML).read_text()
        for line in self._active_lines(text):
            self.assertNotIn(
                "${tach_io_pin}",
                line,
                "FanPWM compile-only skeleton must not consume "
                f"${{tach_io_pin}} — TachIO / GPIO16 stays reserved. Line: {line!r}",
            )
            self.assertNotRegex(
                line,
                r"\bGPIO16\b",
                "FanPWM compile-only skeleton must not bind GPIO16 (TachIO) "
                f"on an active line. Line: {line!r}",
            )

    def test_underlying_fanpwm_package_has_no_pulse_counter(self):
        """Cross-check: the composed package itself wires no pulse_counter."""
        text = self.PACKAGE_FAN_PWM.read_text()
        for line in self._active_lines(text):
            self.assertNotIn(
                "pulse_counter",
                line,
                "packages/expansions/fan_pwm.yaml must not use pulse_counter "
                f"on any active line. Line: {line!r}",
            )

    def test_fanpwm_compile_validated_by_full_compile_run(self):
        """The target must record the full compile passed (run 26414398902)."""
        self.assertIsNotNone(self.target)
        self.assertEqual(
            self.target.get("compile_validation_status"),
            "validated-full-compile",
            "FanPWM compile-only target must record "
            "compile_validation_status: validated-full-compile — the "
            "Compile-only Firmware Validation run 26414398902 "
            "(compile_mode=full, 10 targets, conclusion success) ran "
            "scripts/validate_compile_targets.py --compile against this YAML "
            "and passed, superseding the prior pending-ci marker",
        )

    def test_release_one_and_led_targets_unchanged(self):
        by_config = {
            t["config_string"]: t for t in self.targets if t.get("config_string")
        }
        r1 = by_config.get(RELEASE_ONE_CONFIG_STRING)
        self.assertIsNotNone(r1)
        self.assertEqual(r1.get("shipment_status"), "webflash-current")
        led = by_config.get(LED_PREVIEW_CONFIG_STRING)
        self.assertIsNotNone(led)
        self.assertEqual(led.get("shipment_status"), "preview-current")

    def test_relay_and_dac_targets_unchanged(self):
        self.assertIn(FANRELAY_COMPILE_ONLY_TARGET_ID, self.by_id)
        self.assertEqual(
            self.by_id[FANRELAY_COMPILE_ONLY_TARGET_ID].get("shipment_status"),
            "compile-only",
        )
        self.assertIn(FANDAC_COMPILE_ONLY_TARGET_ID, self.by_id)
        self.assertEqual(
            self.by_id[FANDAC_COMPILE_ONLY_TARGET_ID].get("compile_validation_status"),
            "validated-full-compile",
            "FW-COMPILE-PWM-001 must not change the FanDAC target's "
            "validated-full-compile status",
        )


class TopLevelFanProductCompileTargetTests(unittest.TestCase):
    """TOPLEVEL-FAN-COMPILE-TARGETS-001: the actual top-level FanPWM /
    FanDAC product YAMLs are registered as compile-only targets.

    PR #614 recorded a real full ESPHome compile (10/10 registered targets
    passed), but FanPWM / FanDAC were only registered via their
    ``products/compile-only/`` skeletons, leaving the top-level product
    YAMLs (``products/sense360-ceiling-poe-fanpwm.yaml`` /
    ``products/sense360-ceiling-poe-fandac.yaml``) without their own
    compile-only coverage. This slice registers those top-level product
    YAMLs as first-class compile-only targets — mirroring the FanRelay
    precedent, where the registered compile-only target IS the top-level
    product YAML — WITHOUT retiring the skeletons.

    Guardrails pinned here: the new targets are compile-only /
    no-WebFlash-exposure / no-artifact / no-build-matrix-flip; the existing
    skeleton targets remain present and unchanged (``validated-full-compile``).

    FW-FULL-COMPILE-TOPLEVEL-FANS-001 has since RUN the full
    ``scripts/validate_compile_targets.py --compile`` lane against all 12
    registered targets — every target ``rc=0``, including these two top-level
    product YAMLs — and recorded the result, so both top-level targets now
    carry ``compile_validation_status: validated-full-compile`` (superseding
    the prior ``pending-ci`` marker). The run was local; no CI run id is
    claimed and none is fabricated.
    """

    # (target_id, product_yaml, config_string, skeleton_id, skeleton_yaml)
    PARAMS = (
        (
            FANDAC_PRODUCT_COMPILE_ONLY_TARGET_ID,
            FANDAC_PRODUCT_YAML,
            FANDAC_COMPILE_ONLY_CONFIG_STRING,
            FANDAC_COMPILE_ONLY_TARGET_ID,
            FANDAC_COMPILE_ONLY_PRODUCT_YAML,
        ),
        (
            FANPWM_PRODUCT_COMPILE_ONLY_TARGET_ID,
            FANPWM_PRODUCT_YAML,
            FANPWM_COMPILE_ONLY_CONFIG_STRING,
            FANPWM_COMPILE_ONLY_TARGET_ID,
            FANPWM_COMPILE_ONLY_PRODUCT_YAML,
        ),
    )

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(TARGETS_PATH)
        cls.targets = cls.doc["targets"]
        cls.by_id = {t["id"]: t for t in cls.targets if t.get("id")}
        cls.builds = _load(BUILDS_PATH)
        cls.matrix = _load(MATRIX_PATH)
        cls.catalog = _load(CATALOG_PATH)
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
        cls.catalog_by_config = {
            entry["config_string"]: entry
            for entry in (cls.catalog.get("products", []) or [])
            if entry.get("config_string")
        }

    def test_top_level_fan_product_targets_exist(self):
        """FanPWM and FanDAC top-level product YAMLs are registered."""
        for tid, *_ in self.PARAMS:
            self.assertIn(
                tid,
                self.by_id,
                f"TOPLEVEL-FAN-COMPILE-TARGETS-001 must register a "
                f"compile-only target with id {tid!r}",
            )

    def test_top_level_targets_point_at_top_level_product_yaml(self):
        for tid, product_yaml, *_ in self.PARAMS:
            target = self.by_id.get(tid)
            self.assertIsNotNone(target)
            self.assertEqual(
                target.get("product_yaml"),
                product_yaml,
                f"target {tid!r} must register the top-level product YAML "
                f"{product_yaml!r}",
            )
            self.assertFalse(
                product_yaml.startswith("products/compile-only/"),
                f"target {tid!r}: the whole point is to register the "
                "TOP-LEVEL product YAML, not a products/compile-only/ "
                "skeleton",
            )
            self.assertFalse(
                product_yaml.startswith("products/webflash/"),
                f"target {tid!r}: must not register a products/webflash/ " "wrapper",
            )

    def test_top_level_product_yaml_exists_on_disk(self):
        for tid, product_yaml, *_ in self.PARAMS:
            self.assertTrue(
                (REPO_ROOT / product_yaml).is_file(),
                f"target {tid!r}: product_yaml {product_yaml!r} not found " "on disk",
            )

    def test_top_level_targets_config_string_in_firmware_matrix(self):
        for tid, _, config_string, *_ in self.PARAMS:
            self.assertIn(
                config_string,
                self.matrix_configs,
                f"target {tid!r}: config_string {config_string!r} must be "
                "present in config/firmware-combination-matrix.json",
            )

    def test_top_level_targets_are_compile_only(self):
        for tid, *_ in self.PARAMS:
            target = self.by_id.get(tid)
            self.assertIsNotNone(target)
            self.assertEqual(
                target.get("shipment_status"),
                "compile-only",
                f"target {tid!r}: shipment_status must be compile-only",
            )

    def test_top_level_targets_disallow_webflash_exposure(self):
        for tid, *_ in self.PARAMS:
            target = self.by_id.get(tid)
            self.assertIsNotNone(target)
            self.assertFalse(
                target.get("webflash_exposure_allowed_now"),
                f"target {tid!r}: webflash_exposure_allowed_now must be " "false",
            )

    def test_top_level_targets_require_hardware_for_validation(self):
        for tid, *_ in self.PARAMS:
            target = self.by_id.get(tid)
            self.assertIsNotNone(target)
            self.assertTrue(
                target.get("hardware_required_for_validation"),
                f"target {tid!r}: hardware_required_for_validation must be "
                "true — compile-only is pre-hardware confidence",
            )

    def test_top_level_targets_not_blocked(self):
        for tid, *_ in self.PARAMS:
            target = self.by_id.get(tid)
            self.assertIsNotNone(target)
            self.assertFalse(
                target.get("blocked"),
                f"target {tid!r}: FanPWM / FanDAC are SELV / non-compliance "
                "lanes, not blocked=true targets",
            )

    def test_top_level_targets_declare_no_webflash_build_matrix(self):
        """No webflash_build_matrix flip on the new target rows."""
        for tid, *_ in self.PARAMS:
            target = self.by_id.get(tid)
            self.assertIsNotNone(target)
            self.assertNotIn(
                "webflash_build_matrix",
                target,
                f"target {tid!r}: must not declare webflash_build_matrix; "
                "that flag is owned by config/product-catalog.json and is "
                "not flipped here",
            )

    def test_top_level_targets_declare_no_artifact_name(self):
        for tid, *_ in self.PARAMS:
            target = self.by_id.get(tid)
            self.assertIsNotNone(target)
            self.assertNotIn(
                "artifact_name",
                target,
                f"target {tid!r}: must not declare artifact_name; no "
                "release artifact is added",
            )

    def test_top_level_targets_declare_no_webflash_wrapper(self):
        for tid, *_ in self.PARAMS:
            target = self.by_id.get(tid)
            self.assertIsNotNone(target)
            self.assertNotIn(
                "webflash_wrapper",
                target,
                f"target {tid!r}: must not declare webflash_wrapper",
            )

    def test_top_level_targets_are_validated_full_compile(self):
        """FW-FULL-COMPILE-TOPLEVEL-FANS-001: the two registered top-level
        FanDAC / FanPWM product targets are now validated-full-compile.

        TOPLEVEL-FAN-COMPILE-TARGETS-001 registered these targets with
        compile_validation_status: pending-ci because no full ESPHome
        --compile run had yet been recorded against the registered top-level
        product YAMLs. FW-FULL-COMPILE-TOPLEVEL-FANS-001 then RAN the full
        lane (scripts/validate_compile_targets.py --compile) against all 12
        registered targets — every target rc=0, including these two
        top-level product YAMLs — and recorded the result, so both now carry
        compile_validation_status: validated-full-compile. This is a recorded
        compile result, not a fabricated one; the run was local (no CI run id
        is claimed).
        """
        for tid, *_ in self.PARAMS:
            target = self.by_id.get(tid)
            self.assertIsNotNone(target)
            self.assertEqual(
                target.get("compile_validation_status"),
                "validated-full-compile",
                f"target {tid!r}: must record compile_validation_status: "
                "validated-full-compile — FW-FULL-COMPILE-TOPLEVEL-FANS-001 "
                "ran the full esphome --compile lane against this registered "
                "top-level product YAML and it passed (rc=0)",
            )
            self.assertNotEqual(
                target.get("compile_validation_status"),
                "pending-ci",
                f"target {tid!r}: the prior pending-ci marker is superseded "
                "by the recorded full-compile result",
            )

    def test_top_level_config_strings_build_rows_are_preview_only(self):
        """HW-RELEASE-001 channel guard (was: not in webflash-builds).

        HW-RELEASE-001 (docs/hw-release-001.md, 2026-07-09) declared
        metadata build rows for the top-level FanPWM / FanDAC config
        strings, so this guard pins CHANNEL POSTURE instead of absence:
        each config string's rows must be channel "preview" — never
        "stable".
        """
        rows_by_config = {}
        for row in self.builds.get("builds", []) or []:
            rows_by_config.setdefault(row.get("config_string"), []).append(row)
        for tid, _, config_string, *_ in self.PARAMS:
            rows = rows_by_config.get(config_string) or []
            self.assertTrue(
                rows,
                f"target {tid!r}: expected a HW-RELEASE-001 metadata build "
                f"row for {config_string!r} in config/webflash-builds.json",
            )
            for row in rows:
                self.assertNotEqual(
                    row.get("channel"),
                    "stable",
                    f"target {tid!r}: {config_string!r} build rows are "
                    "NEVER channel stable",
                )
                self.assertEqual(
                    row.get("channel"),
                    "preview",
                    f"target {tid!r}: {config_string!r} build rows are "
                    "preview-channel only (HW-RELEASE-001)",
                )

    def test_no_fan_token_row_is_stable_in_webflash_builds(self):
        """HW-RELEASE-001 posture guard (was: no fan token in builds).

        Fan-token rows now exist by owner declaration, but every
        FanPWM / FanDAC-bearing row must stay on the preview channel and
        never claim a stable artifact name.
        """
        for token in ("FanPWM", "FanDAC"):
            rows = _fan_build_rows(self.builds, token)
            self.assertTrue(
                rows,
                f"expected {token!r} metadata build rows (HW-RELEASE-001)",
            )
            for row in rows:
                cfg = row.get("config_string")
                self.assertEqual(
                    row.get("channel"),
                    FAN_TOKEN_ALLOWED_CHANNEL[token],
                    f"{cfg!r}: {token} rows are preview-channel only — "
                    "never stable (HW-RELEASE-001)",
                )
                self.assertNotIn(
                    "-stable",
                    row.get("artifact_name") or "",
                    f"{cfg!r}: {token} artifact_name must never claim "
                    "the stable channel",
                )

    def test_top_level_targets_not_in_release_one_required_configs(self):
        compat_path = REPO_ROOT / "config" / "webflash-compatibility.json"
        compat = _load(compat_path)
        required = compat.get("release_one_required_configs", []) or []
        for tid, _, config_string, *_ in self.PARAMS:
            self.assertNotIn(
                config_string,
                required,
                f"target {tid!r}: {config_string!r} must not be promoted "
                "into release_one_required_configs",
            )

    def test_fanpwm_top_level_target_makes_no_rpm_claim(self):
        target = self.by_id.get(FANPWM_PRODUCT_COMPILE_ONLY_TARGET_ID)
        self.assertIsNotNone(target)
        self.assertFalse(
            target.get("rpm_supported", False),
            "FanPWM top-level product compile-only target must keep "
            "rpm_supported false — the PWM-drive-only package exposes no "
            "RPM",
        )

    def test_skeleton_targets_remain_present_and_unchanged(self):
        """Existing skeleton targets are preserved, not retired."""
        for _, _, _, skeleton_id, skeleton_yaml in self.PARAMS:
            skeleton = self.by_id.get(skeleton_id)
            self.assertIsNotNone(
                skeleton,
                f"skeleton target {skeleton_id!r} must remain present — "
                "TOPLEVEL-FAN-COMPILE-TARGETS-001 adds top-level targets "
                "alongside the skeletons, it does not retire them",
            )
            self.assertEqual(
                skeleton.get("product_yaml"),
                skeleton_yaml,
                f"skeleton target {skeleton_id!r} must keep pointing at "
                f"{skeleton_yaml!r}",
            )
            self.assertEqual(
                skeleton.get("shipment_status"),
                "compile-only",
                f"skeleton target {skeleton_id!r} stays compile-only",
            )
            self.assertEqual(
                skeleton.get("compile_validation_status"),
                "validated-full-compile",
                f"skeleton target {skeleton_id!r} must stay "
                "validated-full-compile — its recorded full compile is not "
                "regressed by this slice",
            )

    def test_skeleton_and_top_level_targets_are_distinct_files(self):
        """The top-level target and the skeleton are separate YAML files."""
        for tid, product_yaml, _, skeleton_id, skeleton_yaml in self.PARAMS:
            self.assertNotEqual(
                product_yaml,
                skeleton_yaml,
                f"target {tid!r} and skeleton {skeleton_id!r} must register "
                "distinct files (top-level product YAML vs skeleton)",
            )
            self.assertNotEqual(tid, skeleton_id)

    def test_catalog_entries_keep_preview_never_stable_posture(self):
        """HW-RELEASE-001 catalog posture guard (was: no build-matrix flip).

        HW-RELEASE-001 (docs/hw-release-001.md, 2026-07-09) flipped
        webflash_build_matrix to true and declared artifact_name /
        webflash_wrapper for the fan catalog entries by owner decision.
        The remaining teeth: status "preview" (never "production"),
        channel "preview" (never "stable"), artifact names carry the
        -preview suffix, and the entries are never recommended / buyable /
        customer-default.
        """
        for _, _, config_string, *_ in self.PARAMS:
            entry = self.catalog_by_config.get(config_string)
            self.assertIsNotNone(
                entry,
                f"catalog entry for {config_string!r} must exist "
                "(landed by PRODUCT-PWM-001 / PRODUCT-DAC-001)",
            )
            self.assertEqual(
                entry.get("status"),
                "preview",
                f"catalog entry for {config_string!r}: status must be "
                "preview (never production) per HW-RELEASE-001",
            )
            self.assertNotEqual(
                entry.get("channel"),
                "stable",
                f"catalog entry for {config_string!r}: channel is never "
                "stable — nothing fan-flavored is ever stable",
            )
            artifact = entry.get("artifact_name") or ""
            self.assertTrue(
                artifact.endswith("-preview.bin"),
                f"catalog entry for {config_string!r}: artifact_name "
                f"{artifact!r} must carry the -preview channel suffix",
            )
            self.assertFalse(
                entry.get("recommended", False),
                f"catalog entry for {config_string!r}: never recommended",
            )
            self.assertFalse(
                entry.get("buyable", False),
                f"catalog entry for {config_string!r}: never buyable",
            )
            self.assertFalse(
                entry.get("customer_default", False),
                f"catalog entry for {config_string!r}: never a customer " "default",
            )

    def test_totals_updated_for_two_new_top_level_targets(self):
        totals = self.doc.get("totals") or {}
        self.assertEqual(totals.get("targets"), len(self.targets))
        # 2 WebFlash + 5 POE non-fan + 1 FanRelay + 2 fan skeletons
        # (FanDAC, FanPWM) + 2 new top-level fan product targets.
        self.assertGreaterEqual(
            len(self.targets),
            12,
            "expected at least the prior 10 registered targets plus the two "
            "new top-level FanPWM / FanDAC product compile-only targets",
        )


class RoomBundleFanCompileResultsTests(unittest.TestCase):
    """ROOM-BUNDLE-FAN-COMPILE-RESULTS-001: record the hosted full ESPHome
    compile result for the five full-composition room-bundle fan-control
    preview configs added by ROOM-BUNDLE-FAN-CONFIGS-001 (#713).

    The five compile-only targets move from ``compile_validation_status:
    pending-ci`` to ``validated-full-compile``, each carrying a
    ``compile_evidence`` block that cites the hosted Compile-only Firmware
    Validation run ``26913592989`` (compile_mode=full, ref main, conclusion
    success). This is firmware-build proof ONLY: it is not WebFlash exposure,
    not a release artifact, not hardware / bench / compliance / safety proof,
    and not stable / preview / kit / buyable promotion. TRIAC stays
    build-blocked and the FanDAC IC2 DIP-switch mapping stays bench-pending
    under FANDAC-I2C-ADDR-001.
    """

    RUN_ID = 26913592989
    WORKFLOW = "Compile-only Firmware Validation"
    TARGET_IDS = (
        "ceiling-poe-ventiq-fanpwm-roomiq-compile-only",
        "ceiling-poe-ventiq-fandac-roomiq-compile-only",
        "ceiling-poe-airiq-fanrelay-roomiq-compile-only",
        "ceiling-poe-airiq-fandac-roomiq-compile-only",
        "ceiling-poe-airiq-fanpwm-roomiq-compile-only",
    )
    CONFIG_STRINGS = {
        "ceiling-poe-ventiq-fanpwm-roomiq-compile-only": "Ceiling-POE-VentIQ-FanPWM-RoomIQ",
        "ceiling-poe-ventiq-fandac-roomiq-compile-only": "Ceiling-POE-VentIQ-FanDAC-RoomIQ",
        "ceiling-poe-airiq-fanrelay-roomiq-compile-only": "Ceiling-POE-AirIQ-FanRelay-RoomIQ",
        "ceiling-poe-airiq-fandac-roomiq-compile-only": "Ceiling-POE-AirIQ-FanDAC-RoomIQ",
        "ceiling-poe-airiq-fanpwm-roomiq-compile-only": "Ceiling-POE-AirIQ-FanPWM-RoomIQ",
    }
    DAC_TARGET_IDS = (
        "ceiling-poe-ventiq-fandac-roomiq-compile-only",
        "ceiling-poe-airiq-fandac-roomiq-compile-only",
    )

    @classmethod
    def setUpClass(cls):
        cls.doc = _load(TARGETS_PATH)
        cls.by_id = {t["id"]: t for t in cls.doc["targets"] if t.get("id")}
        cls.builds = _load(BUILDS_PATH)
        cls.committed_configs = {
            entry["config_string"]
            for entry in (cls.builds.get("builds", []) or [])
            if entry.get("config_string")
        }

    def _target(self, tid):
        target = self.by_id.get(tid)
        self.assertIsNotNone(target, f"missing compile-only target {tid!r}")
        return target

    def test_all_five_targets_present_with_expected_config_string(self):
        for tid in self.TARGET_IDS:
            target = self._target(tid)
            self.assertEqual(target.get("config_string"), self.CONFIG_STRINGS[tid])

    def test_all_five_targets_are_validated_full_compile(self):
        for tid in self.TARGET_IDS:
            target = self._target(tid)
            self.assertEqual(
                target.get("compile_validation_status"),
                "validated-full-compile",
                f"{tid}: must record validated-full-compile (ROOM-BUNDLE-FAN-"
                "COMPILE-RESULTS-001 recorded the hosted compile)",
            )

    def test_each_target_cites_run_26913592989_evidence(self):
        for tid in self.TARGET_IDS:
            ce = self._target(tid).get("compile_evidence")
            self.assertIsInstance(ce, dict, f"{tid}: missing compile_evidence")
            self.assertEqual(ce.get("run_id"), self.RUN_ID)
            self.assertEqual(
                ce.get("run_url"),
                f"https://github.com/sense360store/esphome-public/actions/runs/{self.RUN_ID}",
            )
            self.assertEqual(ce.get("workflow"), self.WORKFLOW)
            self.assertEqual(ce.get("ref"), "main")
            self.assertEqual(ce.get("result"), "success")
            self.assertEqual(ce.get("metadata_validation_result"), "success")
            self.assertEqual(ce.get("full_esphome_compile_result"), "success")
            self.assertEqual(ce.get("evidence_type"), "hosted-full-compile")
            self.assertEqual(ce.get("proof_scope"), "firmware-build-only")
            self.assertEqual(ce.get("esphome_version"), "2026.4.5")

    def test_compile_proof_is_not_more_than_a_compile(self):
        for tid in self.TARGET_IDS:
            ce = self._target(tid)["compile_evidence"]
            self.assertFalse(ce.get("artifacts_produced", True))
            for forbidden in (
                "hardware",
                "bench-evidence",
                "compliance",
                "stable-promotion",
                "webflash-exposure",
                "release-artifact",
            ):
                self.assertIn(forbidden, ce.get("not_proof_of", []))

    def test_targets_stay_compile_only_and_unexposed(self):
        # HW-RELEASE-001 (docs/hw-release-001.md, 2026-07-09): the five
        # fan-bundle config strings now carry committed metadata build rows,
        # but the compile-only TARGETS themselves stay compile-only and
        # release-artifact-field-free; the build rows are pinned to a
        # non-stable channel in
        # test_fan_bundle_build_rows_are_never_stable_channel below.
        for tid in self.TARGET_IDS:
            target = self._target(tid)
            self.assertEqual(target.get("shipment_status"), "compile-only")
            self.assertFalse(target.get("webflash_exposure_allowed_now"))
            self.assertFalse(target.get("blocked"))
            self.assertNotIn("webflash_build_matrix", target)
            self.assertNotIn("artifact_name", target)

    def test_fan_bundle_build_rows_are_never_stable_channel(self):
        """HW-RELEASE-001 channel guard (was: configs absent from builds).

        The five fan-bundle config strings now have committed metadata
        build rows by owner declaration; each row must stay on its
        non-stable channel — FanPWM / FanDAC bundles on "preview",
        FanRelay bundles on "experimental" — and never "stable".
        """
        rows_by_config = {}
        for row in self.builds.get("builds", []) or []:
            rows_by_config.setdefault(row.get("config_string"), []).append(row)
        for cfg in self.CONFIG_STRINGS.values():
            rows = rows_by_config.get(cfg) or []
            self.assertTrue(
                rows,
                f"{cfg!r}: expected a HW-RELEASE-001 metadata build row "
                "in config/webflash-builds.json",
            )
            tokens = set(cfg.split("-"))
            fan_tokens = tokens & set(FAN_TOKEN_ALLOWED_CHANNEL)
            self.assertTrue(fan_tokens, f"{cfg!r}: expected a fan token")
            for row in rows:
                self.assertNotEqual(
                    row.get("channel"),
                    "stable",
                    f"{cfg!r}: fan-token build rows are NEVER channel " "stable",
                )
                for token in fan_tokens:
                    self.assertEqual(
                        row.get("channel"),
                        FAN_TOKEN_ALLOWED_CHANNEL[token],
                        f"{cfg!r}: {token} rows must be channel "
                        f"{FAN_TOKEN_ALLOWED_CHANNEL[token]!r} "
                        "(HW-RELEASE-001)",
                    )
                self.assertNotIn(
                    "-stable",
                    row.get("artifact_name") or "",
                    f"{cfg!r}: artifact_name must never claim the stable " "channel",
                )

    def test_triac_room_bundle_config_is_never_compile_validated(self):
        # TRIAC-UNBLOCK-BUILD-001 compile-validated exactly ONE FanTRIAC config
        # (Ceiling-POE-VentIQ-FanTRIAC-RoomIQ, status compile-only, still
        # blocked from WebFlash exposure). No OTHER FanTRIAC-bearing config
        # (e.g. a room-bundle fan-control expansion) may be compile-validated.
        unblocked_triac = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"
        for target in self.doc["targets"]:
            cs = target.get("config_string") or ""
            if "FanTRIAC" in cs.split("-") and cs != unblocked_triac:
                self.assertNotEqual(
                    target.get("compile_validation_status"),
                    "validated-full-compile",
                    f"{target.get('id')!r}: only the TRIAC-UNBLOCK-BUILD-001 "
                    "FanTRIAC config may be compile-validated",
                )

    def test_usb_targets_remain_pending_ci(self):
        # ROOM-BUNDLE-FAN-COMPILE-RESULTS-001 only records the five fan-bundle
        # configs; the unrelated USB compile-only targets stay pending-ci.
        for tid in (
            "ceiling-usb-ventiq-roomiq-product-compile-only",
            "ceiling-usb-roomiq-product-compile-only",
        ):
            target = self.by_id.get(tid)
            if target is None:
                continue
            self.assertEqual(
                target.get("compile_validation_status"),
                "pending-ci",
                f"{tid}: must stay pending-ci (out of scope for "
                "ROOM-BUNDLE-FAN-COMPILE-RESULTS-001)",
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


class CompileRunnerLoggingTimeoutSummaryTests(unittest.TestCase):
    """COMPILE-VALIDATOR-PROGRESS-LOGGING-001.

    Pin the per-target progress logging, the per-target timeout, and the
    final summary added to the ``--compile`` lane of
    ``scripts/validate_compile_targets.py``. These drive the validator
    via its module API with an injected ``compile_runner`` so no real
    ESPHome / PlatformIO compile is needed; a couple of tests also drive
    the real ``subprocess`` timeout path through
    ``_make_esphome_compile_runner``.
    """

    # Real product YAMLs on disk (distinct basenames so the injected
    # runner can key behaviour off ``Path.name``) so run_compile's
    # is_file() guard passes without invoking ESPHome.
    PASS_YAML = "products/compile-only/ceiling-poe.yaml"
    FAIL_YAML = "products/compile-only/ceiling-poe-roomiq.yaml"
    TIMEOUT_YAML = "products/compile-only/ceiling-poe-ventiq.yaml"
    SECOND_PASS_YAML = "products/compile-only/ceiling-poe-airiq.yaml"

    def _doc(self, targets):
        return {"schema_version": 1, "targets": targets}

    def _pass_target(self):
        return {
            "id": "pass-target",
            "product_yaml": self.PASS_YAML,
            "config_string": "Ceiling-POE",
            "shipment_status": "compile-only",
        }

    def _fail_target(self):
        return {
            "id": "fail-target",
            "product_yaml": self.FAIL_YAML,
            "config_string": "Ceiling-POE-RoomIQ",
            "shipment_status": "compile-only",
        }

    def _timeout_target(self):
        return {
            "id": "timeout-target",
            "product_yaml": self.TIMEOUT_YAML,
            "config_string": "Ceiling-POE-VentIQ",
            "shipment_status": "compile-only",
        }

    @staticmethod
    def _runner_for(behaviours):
        """Return a compile_runner keyed by YAML basename.

        ``behaviours`` maps a product-YAML basename to the
        ``(returncode, output, timed_out)`` triple the runner returns;
        anything not listed compiles cleanly (rc 0).
        """

        def _runner(path, timeout_seconds):
            result = behaviours.get(Path(path).name)
            if result is not None:
                return result
            return (0, "INFO Successfully compiled program.\n", False)

        return _runner

    @contextlib.contextmanager
    def _patched_cli(self, runner):
        """Make main()'s --compile path use ``runner`` (no real ESPHome)."""
        with mock.patch.object(
            vct, "find_esphome_cli", return_value="esphome"
        ), mock.patch.object(vct, "_make_esphome_compile_runner", return_value=runner):
            yield

    @staticmethod
    def _write_fake_esphome(directory, body):
        path = Path(directory) / "esphome"
        path.write_text("#!/bin/sh\n" + body)
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        return path

    # -- logging -----------------------------------------------------------

    def test_logging_includes_index_config_string_and_yaml_path(self):
        targets = [
            self._pass_target(),
            self._fail_target(),
            self._timeout_target(),
        ]
        runner = self._runner_for(
            {
                "ceiling-poe-roomiq.yaml": (
                    1,
                    "compile broke\nerror tail line\n",
                    False,
                ),
                "ceiling-poe-ventiq.yaml": (None, "partial output\n", True),
            }
        )
        stream = io.StringIO()
        vct.run_compile(
            self._doc(targets),
            timeout_seconds=1200,
            compile_runner=runner,
            stream=stream,
        )
        out = stream.getvalue()

        # Total count announced before the loop.
        self.assertIn("Compiling 3 target(s)", out)

        # Before-each block: index/total + id + config string + yaml path
        # + channel/status, for every target.
        self.assertIn("[1/3] ▶ START pass-target", out)
        self.assertIn("[2/3] ▶ START fail-target", out)
        self.assertIn("[3/3] ▶ START timeout-target", out)
        for config_string in (
            "Ceiling-POE",
            "Ceiling-POE-RoomIQ",
            "Ceiling-POE-VentIQ",
        ):
            self.assertIn(config_string, out)
        for yaml_path in (self.PASS_YAML, self.FAIL_YAML, self.TIMEOUT_YAML):
            self.assertIn(yaml_path, out)
        self.assertIn("channel/status", out)

        # After-each result lines name the outcome per target.
        self.assertIn("PASS pass-target", out)
        self.assertIn("FAIL fail-target", out)
        self.assertIn("TIMEOUT timeout-target", out)

    def test_logging_reports_duration_after_each_target(self):
        stream = io.StringIO()
        vct.run_compile(
            self._doc([self._pass_target()]),
            compile_runner=self._runner_for({}),
            stream=stream,
        )
        out = stream.getvalue()
        # Each result line carries a duration in seconds, e.g. "(0.0s)".
        self.assertRegex(out, r"PASS pass-target \(\d+\.\d+s\)")

    # -- timeout -----------------------------------------------------------

    def test_timeout_outcome_has_clear_message(self):
        runner = self._runner_for(
            {"ceiling-poe.yaml": (None, "hung mid-compile\n", True)}
        )
        stream = io.StringIO()
        results = vct.run_compile(
            self._doc([self._pass_target()]),
            timeout_seconds=600,
            compile_runner=runner,
            stream=stream,
        )
        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertEqual(result.outcome, vct.OUTCOME_TIMEOUT)
        self.assertIsNone(result.returncode)
        # The message must be unambiguous about what happened.
        self.assertIn("timeout", result.message.lower())
        self.assertIn("terminated", result.message.lower())
        # The live log line for this (timed-out) target names the outcome.
        self.assertIn("TIMEOUT pass-target", stream.getvalue())

    def test_run_compile_continues_after_failure_and_timeout(self):
        # Order: pass, timeout, fail, pass — the trailing pass proves the
        # loop did not stop at the timeout or the failure.
        targets = [
            self._pass_target(),
            self._timeout_target(),
            self._fail_target(),
            {
                "id": "second-pass-target",
                "product_yaml": self.SECOND_PASS_YAML,
                "config_string": "Ceiling-POE-AirIQ",
                "shipment_status": "compile-only",
            },
        ]
        runner = self._runner_for(
            {
                "ceiling-poe-ventiq.yaml": (None, "", True),
                "ceiling-poe-roomiq.yaml": (2, "boom\n", False),
            }
        )
        results = vct.run_compile(
            self._doc(targets),
            compile_runner=runner,
            stream=io.StringIO(),
        )
        self.assertEqual(
            [r.outcome for r in results],
            [
                vct.OUTCOME_PASS,
                vct.OUTCOME_TIMEOUT,
                vct.OUTCOME_FAIL,
                vct.OUTCOME_PASS,
            ],
        )

    def test_real_subprocess_compile_is_killed_at_timeout(self):
        directory = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, directory, ignore_errors=True)
        fake = self._write_fake_esphome(
            directory, "echo starting\nsleep 5\necho done\n"
        )
        runner = vct._make_esphome_compile_runner(str(fake))
        start = time.monotonic()
        returncode, output, timed_out = runner(Path(self.PASS_YAML), 0.5)
        elapsed = time.monotonic() - start
        self.assertTrue(timed_out)
        self.assertIsNone(returncode)
        self.assertLess(
            elapsed,
            4.0,
            "the compile should be terminated at the 0.5s timeout, "
            "not allowed to run to its 5s completion",
        )

    def test_real_subprocess_runner_returns_rc_and_output(self):
        directory = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, directory, ignore_errors=True)
        fake = self._write_fake_esphome(
            directory, "echo 'INFO Successfully compiled program.'\nexit 0\n"
        )
        runner = vct._make_esphome_compile_runner(str(fake))
        returncode, output, timed_out = runner(Path(self.PASS_YAML), 30)
        self.assertEqual(returncode, 0)
        self.assertFalse(timed_out)
        self.assertIn("Successfully compiled", output)

    def test_run_compile_raises_when_esphome_missing(self):
        with mock.patch.object(vct, "find_esphome_cli", return_value=None):
            with self.assertRaises(vct.TargetValidationError):
                vct.run_compile(self._doc([self._pass_target()]), stream=io.StringIO())

    # -- failures are never hidden ----------------------------------------

    def test_missing_product_yaml_field_is_failure_not_skip(self):
        target = {
            "id": "no-yaml",
            "config_string": "Ceiling-POE",
            "shipment_status": "compile-only",
        }
        results = vct.run_compile(
            self._doc([target]),
            compile_runner=self._runner_for({}),
            stream=io.StringIO(),
        )
        self.assertEqual(results[0].outcome, vct.OUTCOME_FAIL)
        self.assertNotEqual(results[0].outcome, vct.OUTCOME_SKIP)
        self.assertIn("missing product_yaml", results[0].message)

    def test_nonexistent_product_yaml_is_failure(self):
        target = {
            "id": "ghost-yaml",
            "product_yaml": "products/does-not-exist.yaml",
            "config_string": "Ceiling-POE",
            "shipment_status": "compile-only",
        }
        results = vct.run_compile(
            self._doc([target]),
            compile_runner=self._runner_for({}),
            stream=io.StringIO(),
        )
        self.assertEqual(results[0].outcome, vct.OUTCOME_FAIL)
        self.assertIn("not found", results[0].message)

    # -- summary -----------------------------------------------------------

    def test_summarize_results_has_all_outcome_buckets(self):
        buckets = vct.summarize_results([])
        for outcome in vct.OUTCOME_ORDER:
            self.assertIn(outcome, buckets)
            self.assertEqual(buckets[outcome], [])

    def test_render_summary_includes_counts_timed_out_and_skipped(self):
        results = [
            vct.CompileTargetResult(
                target_id="p",
                config_string="Ceiling-POE",
                product_yaml="products/compile-only/ceiling-poe.yaml",
                channel="-",
                shipment_status="compile-only",
                outcome=vct.OUTCOME_PASS,
                returncode=0,
                duration_seconds=12.0,
            ),
            vct.CompileTargetResult(
                target_id="f",
                config_string="Ceiling-POE-RoomIQ",
                product_yaml="products/compile-only/ceiling-poe-roomiq.yaml",
                channel="-",
                shipment_status="compile-only",
                outcome=vct.OUTCOME_FAIL,
                returncode=1,
                duration_seconds=8.0,
                message="esphome compile exited with rc=1",
            ),
            vct.CompileTargetResult(
                target_id="t",
                config_string="Ceiling-POE-VentIQ",
                product_yaml="products/compile-only/ceiling-poe-ventiq.yaml",
                channel="-",
                shipment_status="compile-only",
                outcome=vct.OUTCOME_TIMEOUT,
                returncode=None,
                duration_seconds=1200.0,
                message="exceeded the per-target timeout and was terminated",
            ),
            vct.CompileTargetResult(
                target_id="s",
                config_string="Ceiling-POE-AirIQ",
                product_yaml="products/compile-only/ceiling-poe-airiq.yaml",
                channel="-",
                shipment_status="compile-only",
                outcome=vct.OUTCOME_SKIP,
                returncode=None,
                duration_seconds=0.0,
                message="not attempted",
            ),
        ]
        summary = vct.render_summary(results, total_duration_seconds=42.5)

        self.assertIn("Total targets : 4", summary)
        self.assertIn("Passed        : 1", summary)
        self.assertIn("Failed        : 1", summary)
        self.assertIn("Timed out     : 1", summary)
        self.assertIn("Skipped       : 1", summary)
        self.assertIn("Total duration: 42.5s", summary)

        # The timed-out target must be itemised by id + config string.
        self.assertIn("Timed-out targets:", summary)
        self.assertIn("t (Ceiling-POE-VentIQ)", summary)
        # As must the failed and skipped targets.
        self.assertIn("Failed targets:", summary)
        self.assertIn("f (Ceiling-POE-RoomIQ)", summary)
        self.assertIn("Skipped targets:", summary)
        self.assertIn("s (Ceiling-POE-AirIQ)", summary)

    # -- exit codes via main() --------------------------------------------

    def test_main_compile_all_pass_returns_zero(self):
        buf = io.StringIO()
        with self._patched_cli(self._runner_for({})), contextlib.redirect_stdout(buf):
            rc = vct.main(["--compile", "--timeout-minutes", "20"])
        out = buf.getvalue()
        self.assertEqual(rc, 0, out)
        self.assertIn("Compile-only validation summary", out)
        self.assertIn("compile target(s) passed", out)

    def test_main_compile_with_failure_returns_one(self):
        runner = self._runner_for(
            {"ceiling-poe-ventiq-roomiq.yaml": (1, "compile failed\n", False)}
        )
        buf = io.StringIO()
        with self._patched_cli(runner), contextlib.redirect_stdout(buf):
            rc = vct.main(["--compile"])
        out = buf.getvalue()
        self.assertEqual(rc, 1, out)
        self.assertIn("did not pass", out)

    def test_main_compile_with_timeout_returns_one_and_names_it(self):
        runner = self._runner_for(
            {"ceiling-poe-ventiq-roomiq.yaml": (None, "stuck\n", True)}
        )
        buf = io.StringIO()
        with self._patched_cli(runner), contextlib.redirect_stdout(buf):
            rc = vct.main(["--compile"])
        out = buf.getvalue()
        self.assertEqual(rc, 1, out)
        self.assertIn("timed out", out)
        self.assertIn("Timed-out targets:", out)

    # -- metadata-only path unaffected + flag plumbing --------------------

    def test_metadata_only_modes_still_pass(self):
        self.assertEqual(vct.main(["--metadata-only"]), 0)
        self.assertEqual(vct.main([]), 0)

    def test_timeout_minutes_flag_is_accepted_with_metadata(self):
        self.assertEqual(vct.main(["--metadata-only", "--timeout-minutes", "5"]), 0)

    def test_timeout_minutes_flag_rejects_non_positive(self):
        with self.assertRaises(SystemExit):
            vct.main(["--compile", "--timeout-minutes", "0"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

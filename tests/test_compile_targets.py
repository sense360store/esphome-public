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

# Fan / PWR tokens that the FW-COMPILE-POE-NONFAN-001 lane
# (products/compile-only/) must never introduce. Compile-only targets
# that carry a fan-driver token (e.g. FW-COMPILE-RELAY-001) live outside
# products/compile-only/ and reuse the canonical product YAML under
# products/ so the catalog enumeration / product-readiness gates apply.
FORBIDDEN_FAN_TOKENS_FOR_THIS_PR = frozenset(
    {"FanRelay", "FanPWM", "FanDAC", "FanTRIAC"}
)
FORBIDDEN_POWER_TOKENS_FOR_THIS_PR = frozenset({"PWR"})

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
# lane. PRODUCT-PWM-001 is not landed, so no top-level products/ YAML and
# no catalog row is added; the compile-only skeleton is the sole CI
# validation target. The PWM-drive-only package (PACKAGE-PWM-001-
# IMPLEMENT-001 / PR #590) exposes four SX1509 PWM-drive fan controllers
# and NO RPM / NO pulse_counter; this target makes no RPM claim.
FANPWM_COMPILE_ONLY_TARGET_ID = "ceiling-poe-fanpwm-compile-only"
FANPWM_COMPILE_ONLY_CONFIG_STRING = "Ceiling-POE-FanPWM"
FANPWM_COMPILE_ONLY_PRODUCT_YAML = "products/compile-only/ceiling-poe-fanpwm.yaml"

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
            t["config_string"]: t
            for t in cls.targets
            if t.get("config_string")
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

    def test_fanrelay_compile_only_target_is_not_in_webflash_builds(self):
        self.assertNotIn(
            FANRELAY_COMPILE_ONLY_CONFIG_STRING,
            self.committed_configs,
            f"FanRelay compile-only target {FANRELAY_COMPILE_ONLY_CONFIG_STRING!r} "
            "must NOT be present in config/webflash-builds.json — "
            "compile-only targets do not add WebFlash builds",
        )

    def test_no_fanrelay_token_in_webflash_builds(self):
        text = BUILDS_PATH.read_text()
        self.assertNotIn(
            "FanRelay",
            text,
            "config/webflash-builds.json must not contain the FanRelay "
            "token — FW-COMPILE-RELAY-001 does not add a FanRelay "
            "WebFlash build entry. A FanRelay-bearing build entry is "
            "owned by RELEASE-RELAY-001 (not landed).",
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

    def test_no_fanrelay_webflash_wrapper_file_exists(self):
        webflash_dir = REPO_ROOT / "products" / "webflash"
        if not webflash_dir.is_dir():
            return
        offenders = []
        for path in webflash_dir.glob("*.yaml"):
            name = path.name.lower()
            if "fanrelay" in name or "fan-relay" in name or "fan_relay" in name:
                offenders.append(path.relative_to(REPO_ROOT).as_posix())
        self.assertEqual(
            offenders,
            [],
            f"FW-COMPILE-RELAY-001 must NOT add any FanRelay WebFlash "
            f"wrapper under products/webflash/ — that work belongs to "
            f"WEBFLASH-RELAY-001 (not landed). Offending paths: "
            f"{offenders!r}",
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
        expected_min_targets = (
            2 + len(POE_NONFAN_COMPILE_ONLY_CONFIG_STRINGS) + 1
        )
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

    def test_fandac_target_is_not_in_webflash_builds(self):
        self.assertNotIn(
            FANDAC_COMPILE_ONLY_CONFIG_STRING,
            self.committed_configs,
            f"FanDAC compile-only target {FANDAC_COMPILE_ONLY_CONFIG_STRING!r} "
            "must NOT be present in config/webflash-builds.json",
        )

    def test_no_fandac_token_in_webflash_builds(self):
        text = BUILDS_PATH.read_text()
        self.assertNotIn(
            "FanDAC",
            text,
            "config/webflash-builds.json must not contain the FanDAC token "
            "— FW-COMPILE-DAC-001 adds no FanDAC WebFlash build entry",
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

    def test_no_fandac_webflash_wrapper_file_exists(self):
        webflash_dir = REPO_ROOT / "products" / "webflash"
        if not webflash_dir.is_dir():
            return
        offenders = []
        for path in webflash_dir.glob("*.yaml"):
            name = path.name.lower()
            if "fandac" in name or "fan-dac" in name or "fan_dac" in name:
                offenders.append(path.relative_to(REPO_ROOT).as_posix())
        self.assertEqual(
            offenders,
            [],
            f"FW-COMPILE-DAC-001 must NOT add any FanDAC WebFlash wrapper "
            f"under products/webflash/. Offending paths: {offenders!r}",
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
            "FanDAC compile-only skeleton must stay under "
            "products/compile-only/",
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

    def test_no_fandac_product_yaml_under_webflash_wrapper_dir(self):
        """No FanDAC YAML may live under products/webflash/.

        PRODUCT-DAC-001 is product-YAML-only / no-WebFlash-exposure: the
        WebFlash wrapper namespace (products/webflash/) must carry no
        FanDAC YAML. That work belongs to WEBFLASH-DAC-001 (not landed).
        """
        webflash_dir = REPO_ROOT / "products" / "webflash"
        if not webflash_dir.is_dir():
            return
        offenders = []
        for path in webflash_dir.glob("*.yaml"):
            name = path.name.lower()
            if "fandac" in name or "fan-dac" in name or "fan_dac" in name:
                offenders.append(path.relative_to(REPO_ROOT).as_posix())
        self.assertEqual(
            offenders,
            [],
            "PRODUCT-DAC-001 must NOT add a FanDAC WebFlash wrapper under "
            f"products/webflash/. Offending paths: {offenders!r}",
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

    def test_fanpwm_target_is_not_in_webflash_builds(self):
        self.assertNotIn(
            FANPWM_COMPILE_ONLY_CONFIG_STRING,
            self.committed_configs,
            f"FanPWM compile-only target {FANPWM_COMPILE_ONLY_CONFIG_STRING!r} "
            "must NOT be present in config/webflash-builds.json",
        )

    def test_no_fanpwm_token_in_webflash_builds(self):
        text = BUILDS_PATH.read_text()
        self.assertNotIn(
            "FanPWM",
            text,
            "config/webflash-builds.json must not contain the FanPWM token "
            "— FW-COMPILE-PWM-001 adds no FanPWM WebFlash build entry",
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

    def test_no_fanpwm_webflash_wrapper_file_exists(self):
        webflash_dir = REPO_ROOT / "products" / "webflash"
        if not webflash_dir.is_dir():
            return
        offenders = []
        for path in webflash_dir.glob("*.yaml"):
            name = path.name.lower()
            if "fanpwm" in name or "fan-pwm" in name or "fan_pwm" in name:
                offenders.append(path.relative_to(REPO_ROOT).as_posix())
        self.assertEqual(
            offenders,
            [],
            f"FW-COMPILE-PWM-001 must NOT add any FanPWM WebFlash wrapper "
            f"under products/webflash/. Offending paths: {offenders!r}",
        )

    def test_fanpwm_skeleton_stays_under_compile_only(self):
        self.assertTrue(
            FANPWM_COMPILE_ONLY_PRODUCT_YAML.startswith("products/compile-only/"),
            "FanPWM compile-only skeleton must stay under "
            "products/compile-only/",
        )

    def test_no_top_level_fanpwm_product_yaml_added(self):
        """PRODUCT-PWM-001 is not landed: no top-level FanPWM product YAML.

        FW-COMPILE-PWM-001 adds only the compile-only skeleton under
        products/compile-only/. The legacy standalone fan-board product
        (products/sense360-fan-pwm.yaml) predates this slice and is
        allowed; no other FanPWM-named YAML may appear outside
        products/compile-only/.
        """
        products_dir = REPO_ROOT / "products"
        if not products_dir.is_dir():
            self.skipTest("products/ directory not present")
        compile_only_dir = products_dir / "compile-only"
        allowed = {"products/sense360-fan-pwm.yaml"}
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
            "FW-COMPILE-PWM-001 must add no top-level FanPWM product YAML "
            f"(PRODUCT-PWM-001 not landed); unexpected: {sorted(offenders)!r}",
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
            self.by_id[FANDAC_COMPILE_ONLY_TARGET_ID].get(
                "compile_validation_status"
            ),
            "validated-full-compile",
            "FW-COMPILE-PWM-001 must not change the FanDAC target's "
            "validated-full-compile status",
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

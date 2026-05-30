#!/usr/bin/env python3
"""PRODUCT-DAC-001 invariants for the FanDAC product YAML.

PRODUCT-DAC-001 adds a single canonical FanDAC product YAML
(``products/sense360-ceiling-poe-fandac.yaml``) as the
**product-YAML-only / no-WebFlash-exposure** slice that follows
PACKAGE-DAC-001 (PR #573, package layer) and the FW-COMPILE-DAC-001 /
FW-COMPILE-DAC-RESULT-001 compile-only **metadata** lane (PR #575 /
PR #576). The product composes Core ceiling + PoE PSU + base/health with
the canonical FanDAC package alias
``packages/expansions/fan_dac.yaml`` (a pure ``!include`` wrapper of
``packages/expansions/fan_gp8403.yaml``: two GP8403 DACs / four neutral
analog outputs). The customer outcome is 0-10V fan control (for example
Cloudlift S12 fan control).

The product intentionally has:

  * no WebFlash wrapper under ``products/webflash/``;
  * no ``webflash_build_matrix: true`` flip in
    ``config/product-catalog.json``;
  * no ``artifact_name`` declared;
  * no entry in ``config/webflash-builds.json``;
  * no entry in ``release_one_required_configs``;
  * no release artifact / tag / checksum / build-info manifest;
  * an explicit full-compile-validated caveat (run 26364679370 /
    validated-full-compile; CONFIG-FRESHNESS-001), a J3 silkscreen
    transposition caveat, and a Cloudlift S12 harness / product-bench
    caveat in the product YAML header.

These tests pin the structural invariants so a future regression cannot
silently promote the FanDAC product onto a WebFlash-shippable surface or
strip the required caveats without an explicit WEBFLASH-DAC-001 /
RELEASE-DAC-001 slice.

Run with::

    python3 tests/test_dac_product_readiness.py

or::

    python3 -m unittest tests.test_dac_product_readiness -v
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from typing import Any, Dict, List

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent

DAC_PRODUCT_YAML = REPO_ROOT / "products" / "sense360-ceiling-poe-fandac.yaml"
DAC_PRODUCT_REL = "products/sense360-ceiling-poe-fandac.yaml"
# The product YAML is now a thin compat shim; its full composition/substitution
# content lives in the bundle. Content reads must target the bundle.
DAC_BUNDLE = REPO_ROOT / "products" / "bundles" / "ceiling-poe-fandac.yaml"
DAC_CONFIG_STRING = "Ceiling-POE-FanDAC"

# Existing siblings that PRODUCT-DAC-001 must not disturb.
RELEASE_ONE_PRODUCT_REL = "products/sense360-ceiling-poe-ventiq-roomiq.yaml"
RELEASE_ONE_CONFIG_STRING = "Ceiling-POE-VentIQ-RoomIQ"
LED_PREVIEW_PRODUCT_REL = "products/sense360-ceiling-poe-ventiq-roomiq-led.yaml"
LED_PREVIEW_CONFIG_STRING = "Ceiling-POE-VentIQ-RoomIQ-LED"
RELAY_PRODUCT_REL = "products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml"
RELAY_CONFIG_STRING = "Ceiling-POE-VentIQ-FanRelay-RoomIQ"
FANTRIAC_BLOCKED_CONFIG_STRING = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"

PRODUCT_CATALOG = REPO_ROOT / "config" / "product-catalog.json"
WEBFLASH_BUILDS = REPO_ROOT / "config" / "webflash-builds.json"
WEBFLASH_COMPATIBILITY = REPO_ROOT / "config" / "webflash-compatibility.json"
WEBFLASH_WRAPPER_DIR = REPO_ROOT / "products" / "webflash"

# The FW-COMPILE-DAC-001 compile-only skeleton must remain unchanged.
COMPILE_ONLY_TARGETS = REPO_ROOT / "config" / "compile-only-targets.json"
FANDAC_COMPILE_ONLY_TARGET_ID = "ceiling-poe-fandac-compile-only"
FANDAC_COMPILE_ONLY_PRODUCT_YAML = "products/compile-only/ceiling-poe-fandac.yaml"


# Register the same minimal set of ESPHome custom tags used by
# ``tests/validate_configs.py`` so ``yaml.safe_load`` can parse the
# product YAML without a real ESPHome runtime.
def _esphome_constructor(loader, node):  # type: ignore[no-untyped-def]
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None


for _tag in ("!secret", "!include", "!extend", "!lambda", "!remove"):
    yaml.add_constructor(_tag, _esphome_constructor, Loader=yaml.SafeLoader)
yaml.add_multi_constructor(
    "!include_dir_", _esphome_constructor, Loader=yaml.SafeLoader
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text())


def _active_lines(text: str) -> List[str]:
    """Return only non-comment, non-blank lines from ``text``."""
    out: List[str] = []
    for line in text.splitlines():
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            continue
        out.append(line)
    return out


def _catalog_entry_for(rel_path: str) -> Dict[str, Any]:
    catalog = _load_json(PRODUCT_CATALOG)
    for entry in catalog.get("products", []):
        if entry.get("product_yaml") == rel_path:
            return entry
    raise AssertionError(
        f"no catalog entry for product_yaml={rel_path!r} in "
        f"config/product-catalog.json (PRODUCT-DAC-001 requires a "
        f"non-WebFlash row)"
    )


class DacProductYamlExistsTests(unittest.TestCase):
    """The PRODUCT-DAC-001 product YAML exists at the canonical path."""

    def test_product_yaml_file_exists(self) -> None:
        self.assertTrue(
            DAC_PRODUCT_YAML.is_file(),
            f"PRODUCT-DAC-001 must add the FanDAC product YAML at "
            f"{DAC_PRODUCT_YAML} (config string {DAC_CONFIG_STRING})",
        )

    def test_product_yaml_parses_as_yaml(self) -> None:
        data = _load_yaml(DAC_BUNDLE)
        self.assertIsInstance(
            data,
            dict,
            "FanDAC product YAML must parse as a YAML mapping",
        )
        for key in ("substitutions", "packages"):
            self.assertIn(
                key,
                data,
                f"FanDAC product YAML must declare a top-level `{key}:` block",
            )

    def test_product_yaml_is_enumerated_in_catalog(self) -> None:
        entry = _catalog_entry_for(DAC_PRODUCT_REL)
        self.assertEqual(entry.get("config_string"), DAC_CONFIG_STRING)


class DacProductPackageCompositionTests(unittest.TestCase):
    """The product composes the FanDAC package + the Core / PoE base stack."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.data = _load_yaml(DAC_BUNDLE)
        cls.packages = cls.data.get("packages", {}) or {}
        cls.text = DAC_BUNDLE.read_text()

    def test_packages_block_is_a_mapping(self) -> None:
        self.assertIsInstance(
            self.packages,
            dict,
            "FanDAC product YAML `packages:` block must be a mapping",
        )

    def test_includes_fan_dac_package_alias(self) -> None:
        self.assertIn(
            "packages/expansions/fan_dac.yaml",
            self.text,
            "FanDAC product YAML must !include "
            "packages/expansions/fan_dac.yaml so the DAC outputs are "
            "composed through the canonical FanDAC package alias.",
        )

    def test_includes_core_ceiling_package(self) -> None:
        self.assertIn(
            "packages/hardware/sense360_core_ceiling.yaml",
            self.text,
            "FanDAC product YAML must !include the Core ceiling abstract "
            "package so the GP8403 DACs bind to the shared core_i2c bus.",
        )

    def test_includes_poe_power_package(self) -> None:
        self.assertIn(
            "packages/hardware/power_poe.yaml",
            self.text,
            "FanDAC product YAML must !include the PoE power package.",
        )

    def test_includes_device_health_package(self) -> None:
        self.assertIn(
            "packages/features/device_health.yaml",
            self.text,
            "FanDAC product YAML must !include the device health package.",
        )

    def test_does_not_include_airiq_packages(self) -> None:
        # FanDAC is mutually exclusive with AirIQ
        # (fandac_conflicts_with_airiq). The product must carry no AirIQ
        # module include.
        for forbidden in (
            "packages/expansions/airiq.yaml",
            "packages/expansions/airiq_ceiling.yaml",
            "packages/expansions/airiq_bathroom_base.yaml",
            "packages/expansions/airiq_bathroom_pro.yaml",
            "packages/expansions/airiq_wall.yaml",
        ):
            self.assertNotIn(
                forbidden,
                self.text,
                f"FanDAC product YAML must NOT !include {forbidden}; "
                "FanDAC is mutually exclusive with AirIQ "
                "(fandac_conflicts_with_airiq).",
            )

    def test_does_not_include_other_fan_driver_packages(self) -> None:
        # Fan driver variants are firmware-distinct; this product ships
        # FanDAC only.
        for forbidden in (
            "packages/expansions/fan_relay.yaml",
            "packages/expansions/fan_triac.yaml",
            "packages/expansions/fan_pwm.yaml",
            "packages/expansions/fan_12v_pwm.yaml",
        ):
            self.assertNotIn(
                forbidden,
                self.text,
                f"FanDAC product YAML must NOT !include {forbidden}; "
                "fan-driver variants are firmware-distinct and this "
                "product ships FanDAC only.",
            )


class DacProductDoesNotLeakChipJargonTests(unittest.TestCase):
    """Customer-facing template names stay outcome-first / neutral.

    The package keeps neutral output IDs; the product layer must not leak
    board-module jargon (the GP8403 chip name, VOUTn, IC1 / IC2) into the
    template entity ``name:`` fields surfaced to Home Assistant.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.data = _load_yaml(DAC_BUNDLE)

    def test_template_entity_names_are_neutral(self) -> None:
        sensors = self.data.get("text_sensor", []) or []
        for sensor in sensors:
            if not isinstance(sensor, dict):
                continue
            name = sensor.get("name", "")
            if not isinstance(name, str):
                continue
            lowered = name.lower()
            for jargon in ("gp8403", "vout", "ic1", "ic2"):
                self.assertNotIn(
                    jargon,
                    lowered,
                    f"FanDAC product template entity name {name!r} must "
                    f"not leak board-module jargon {jargon!r}; "
                    "customer-facing labels stay outcome-first.",
                )


class DacProductWebFlashExposureGuardsTests(unittest.TestCase):
    """The FanDAC product is NOT WebFlash-exposed.

    PRODUCT-DAC-001 explicitly does not add a WebFlash wrapper, a catalog
    ``webflash_build_matrix: true`` flip, an ``artifact_name``, a
    ``config/webflash-builds.json`` entry, or a release artifact.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.entry = _catalog_entry_for(DAC_PRODUCT_REL)
        cls.builds_doc = _load_json(WEBFLASH_BUILDS)
        cls.compat = _load_json(WEBFLASH_COMPATIBILITY)

    def test_catalog_entry_webflash_build_matrix_is_false(self) -> None:
        self.assertEqual(
            self.entry.get("webflash_build_matrix"),
            False,
            "FanDAC product catalog entry must set "
            "webflash_build_matrix: false — PRODUCT-DAC-001 does not "
            "advance WEBFLASH-DAC-001 or RELEASE-DAC-001.",
        )

    def test_catalog_entry_has_no_artifact_name(self) -> None:
        self.assertNotIn(
            "artifact_name",
            self.entry,
            "FanDAC product catalog entry must NOT declare artifact_name "
            "— no release artifact is built by PRODUCT-DAC-001.",
        )

    def test_catalog_entry_has_no_webflash_wrapper(self) -> None:
        self.assertNotIn(
            "webflash_wrapper",
            self.entry,
            "FanDAC product catalog entry must NOT declare "
            "webflash_wrapper — PRODUCT-DAC-001 does not add a WebFlash "
            "wrapper under products/webflash/.",
        )

    def test_catalog_entry_status_is_not_release_eligible(self) -> None:
        # production / preview entries are WebFlash-eligible; the FanDAC
        # entry must stay outside that set so the product remains
        # WebFlash-blocked.
        self.assertNotIn(
            self.entry.get("status"),
            {"production", "preview"},
            f"FanDAC product catalog entry must not be production or "
            f"preview — those statuses authorise WebFlash exposure. "
            f"Got status={self.entry.get('status')!r}.",
        )

    def test_no_fandac_webflash_wrapper_file(self) -> None:
        if not WEBFLASH_WRAPPER_DIR.is_dir():
            return
        offenders = []
        for path in WEBFLASH_WRAPPER_DIR.glob("*.yaml"):
            name = path.name.lower()
            if "fandac" in name or "fan-dac" in name or "fan_dac" in name:
                offenders.append(path.relative_to(REPO_ROOT).as_posix())
        self.assertEqual(
            offenders,
            [],
            f"PRODUCT-DAC-001 must NOT add any FanDAC WebFlash wrapper "
            f"under products/webflash/ — that work belongs to "
            f"WEBFLASH-DAC-001 (not landed). Offending paths: {offenders!r}",
        )

    def test_dac_config_string_not_in_webflash_builds(self) -> None:
        for entry in self.builds_doc.get("builds", []) or []:
            self.assertNotEqual(
                entry.get("config_string"),
                DAC_CONFIG_STRING,
                f"config/webflash-builds.json must not contain "
                f"{DAC_CONFIG_STRING!r} — PRODUCT-DAC-001 does not add a "
                f"build-matrix entry. RELEASE-DAC-001 owns the FanDAC "
                f"build entry.",
            )

    def test_fandac_token_not_in_webflash_builds_json(self) -> None:
        text = WEBFLASH_BUILDS.read_text()
        self.assertNotIn(
            "FanDAC",
            text,
            "config/webflash-builds.json must not contain the FanDAC "
            "token at all — PRODUCT-DAC-001 does not advance "
            "WEBFLASH-DAC-001 or RELEASE-DAC-001.",
        )

    def test_dac_config_string_not_in_release_one_required_configs(
        self,
    ) -> None:
        required = self.compat.get("release_one_required_configs", []) or []
        self.assertNotIn(
            DAC_CONFIG_STRING,
            required,
            f"release_one_required_configs in "
            f"config/webflash-compatibility.json must not contain "
            f"{DAC_CONFIG_STRING!r} — PRODUCT-DAC-001 does not promote "
            f"FanDAC into Release-One required configs.",
        )

    def test_product_yaml_does_not_declare_webflash_build_matrix_true(
        self,
    ) -> None:
        text = DAC_BUNDLE.read_text()
        for line in _active_lines(text):
            self.assertNotIn(
                "webflash_build_matrix",
                line,
                f"FanDAC product YAML must not declare a "
                f"`webflash_build_matrix` field — that field belongs to "
                f"the catalog entry only and must remain false. "
                f"Offending line: {line!r}",
            )

    def test_product_yaml_does_not_declare_artifact_name(self) -> None:
        text = DAC_BUNDLE.read_text()
        for line in _active_lines(text):
            self.assertNotIn(
                "artifact_name",
                line,
                f"FanDAC product YAML must not declare an `artifact_name` "
                f"field — no release artifact is built by PRODUCT-DAC-001. "
                f"Offending line: {line!r}",
            )


class DacProductCaveatWordingTests(unittest.TestCase):
    """The FanDAC product YAML carries the PRODUCT-DAC-001 caveats.

    PRODUCT-DAC-001 requires explicit full-compile-validated (run
    26364679370; CONFIG-FRESHNESS-001), J3 silkscreen transposition,
    Cloudlift S12 harness / product-bench, and no-WebFlash / no-release /
    no-compliance caveat wording in the product YAML itself. These tests
    pin that wording so a later refactor cannot silently strip it.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = DAC_BUNDLE.read_text()
        # Normalize so phrase checks survive comment-line wrapping: strip
        # leading comment markers, collapse all whitespace to single
        # spaces, and lower-case.
        stripped = re.sub(r"(?m)^\s*#", " ", cls.text)
        cls.normalized = re.sub(r"\s+", " ", stripped).lower()

    def _assert_phrase(self, phrase: str, hint: str) -> None:
        needle = re.sub(r"\s+", " ", phrase).lower()
        self.assertIn(
            needle,
            self.normalized,
            f"FanDAC product YAML must contain wording matching {phrase!r} "
            f"({hint}). PRODUCT-DAC-001 requires the product YAML to carry "
            f"explicit no-WebFlash / full-compile-validated / J3-silk / "
            f"Cloudlift-harness caveat text.",
        )

    def test_carries_outcome_first_0_10v_wording(self) -> None:
        self._assert_phrase(
            "0-10v fan control",
            "outcome-first 0-10V fan control naming",
        )

    def test_carries_cloudlift_s12_fan_control_wording(self) -> None:
        self._assert_phrase(
            "cloudlift s12 fan control",
            "outcome-first Cloudlift S12 fan control naming",
        )

    def test_carries_full_compile_validated_caveat(self) -> None:
        # CONFIG-FRESHNESS-001: the full ESPHome compile is now recorded
        # green (run 26364679370, compile_mode=full); the caveat must say
        # validated-full-compile, not the superseded owed / pending-ci
        # narrative.
        self._assert_phrase(
            "full esphome compile",
            "full ESPHome compile caveat",
        )
        self._assert_phrase(
            "compile_mode=full",
            "manual workflow_dispatch compile_mode=full run that validated it",
        )
        self._assert_phrase(
            "validated-full-compile",
            "compile_validation_status: validated-full-compile now stands",
        )
        self._assert_phrase(
            "26364679370",
            "the full-compile run id that validated the FanDAC target",
        )
        self.assertNotIn(
            "pending-ci",
            self.normalized,
            "FanDAC product YAML must no longer carry the superseded "
            "pending-ci / full-compile-owed narrative (CONFIG-FRESHNESS-001).",
        )

    def test_carries_j3_silk_transposition_caveat(self) -> None:
        self._assert_phrase("j3", "J3 connector reference")
        self._assert_phrase(
            "transposition",
            "J3 out0/out1 silkscreen transposition caveat",
        )

    def test_carries_cloudlift_harness_bench_caveat(self) -> None:
        self._assert_phrase("harness", "harness conductor mapping caveat")
        self._assert_phrase(
            "bench",
            "harness / product-bench confirmation caveat",
        )

    def test_states_not_webflash_exposed(self) -> None:
        self._assert_phrase(
            "not webflash",
            "explicit not-WebFlash-exposed statement",
        )

    def test_states_not_default_or_recommended(self) -> None:
        self._assert_phrase(
            "not a default",
            "explicit not-default / not-recommended statement",
        )

    def test_states_not_release_artifact(self) -> None:
        self._assert_phrase(
            "not a release artifact",
            "explicit not-release-artifact statement",
        )

    def test_states_not_compliance_certified(self) -> None:
        self._assert_phrase(
            "not compliance-certified",
            "explicit not-compliance-certified statement",
        )

    def test_states_fandac_airiq_mutex(self) -> None:
        self._assert_phrase("airiq", "FanDAC <-> AirIQ mutex reference")
        self._assert_phrase(
            "mutually exclusive",
            "FanDAC mutually exclusive with AirIQ",
        )

    def test_does_not_claim_simultaneous_dual_range(self) -> None:
        # The product must NOT claim simultaneous per-output 0-5V + 0-10V
        # on one GP8403; it must state the per-chip range limitation.
        self._assert_phrase(
            "cannot drive one output at 0-5v and the other at 0-10v",
            "per-chip single-range limitation (no simultaneous "
            "per-output 0-5V + 0-10V on one GP8403)",
        )


class DacProductCompileOnlyTargetUnchangedTests(unittest.TestCase):
    """FW-COMPILE-DAC-001 compile-only skeleton / target stays unchanged.

    PRODUCT-DAC-001 adds a top-level product YAML but must not repoint or
    alter the existing compile-only target, which keeps pointing at the
    products/compile-only/ skeleton.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = _load_json(COMPILE_ONLY_TARGETS)
        cls.by_id = {
            t.get("id"): t for t in cls.doc.get("targets", []) if t.get("id")
        }
        cls.target = cls.by_id.get(FANDAC_COMPILE_ONLY_TARGET_ID)

    def test_compile_only_target_exists(self) -> None:
        self.assertIsNotNone(
            self.target,
            f"FanDAC compile-only target {FANDAC_COMPILE_ONLY_TARGET_ID!r} "
            "must remain present",
        )

    def test_compile_only_target_points_at_skeleton(self) -> None:
        self.assertIsNotNone(self.target)
        self.assertEqual(
            self.target.get("product_yaml"),
            FANDAC_COMPILE_ONLY_PRODUCT_YAML,
            "FanDAC compile-only target must keep pointing at the "
            "products/compile-only/ skeleton, not the top-level product "
            "YAML added by PRODUCT-DAC-001.",
        )

    def test_compile_only_target_shipment_status_unchanged(self) -> None:
        self.assertIsNotNone(self.target)
        self.assertEqual(self.target.get("shipment_status"), "compile-only")

    def test_compile_only_target_compile_validation_full_compile(self) -> None:
        self.assertIsNotNone(self.target)
        self.assertEqual(
            self.target.get("compile_validation_status"),
            "validated-full-compile",
            "FanDAC compile-only target must record "
            "compile_validation_status: validated-full-compile — the manual "
            "workflow_dispatch compile_mode=full run 26364679370 compiled the "
            "FanDAC target green (COMPILE-STATUS-FLAGS-001).",
        )


class ReleaseOneRelayAndLedUnchangedTests(unittest.TestCase):
    """Release-One, LED preview, FanRelay, and FanTRIAC entries are unchanged.

    PRODUCT-DAC-001 must not touch the Release-One canonical YAML, the LED
    preview canonical YAML, the FanRelay sibling, or their catalog
    entries.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = _load_json(PRODUCT_CATALOG)

    def _find(self, cs: str) -> Dict[str, Any]:
        for entry in self.catalog.get("products", []):
            if entry.get("config_string") == cs:
                return entry
        raise AssertionError(f"no catalog entry for {cs!r}")

    def test_release_one_product_yaml_exists(self) -> None:
        path = REPO_ROOT / RELEASE_ONE_PRODUCT_REL
        self.assertTrue(path.is_file(), f"missing {RELEASE_ONE_PRODUCT_REL}")

    def test_led_preview_product_yaml_exists(self) -> None:
        path = REPO_ROOT / LED_PREVIEW_PRODUCT_REL
        self.assertTrue(path.is_file(), f"missing {LED_PREVIEW_PRODUCT_REL}")

    def test_relay_product_yaml_exists(self) -> None:
        path = REPO_ROOT / RELAY_PRODUCT_REL
        self.assertTrue(path.is_file(), f"missing {RELAY_PRODUCT_REL}")

    def test_release_one_catalog_entry_is_unchanged_production(self) -> None:
        entry = self._find(RELEASE_ONE_CONFIG_STRING)
        self.assertEqual(entry["status"], "production")
        self.assertEqual(entry["channel"], "stable")
        self.assertEqual(entry["version"], "1.0.0")
        self.assertEqual(
            entry["artifact_name"],
            "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin",
        )
        self.assertTrue(entry["webflash_build_matrix"])
        self.assertEqual(entry["product_yaml"], RELEASE_ONE_PRODUCT_REL)

    def test_led_preview_catalog_entry_is_unchanged_preview(self) -> None:
        entry = self._find(LED_PREVIEW_CONFIG_STRING)
        self.assertEqual(entry["status"], "preview")
        self.assertEqual(entry["channel"], "preview")
        self.assertTrue(entry["webflash_build_matrix"])
        self.assertEqual(entry["product_yaml"], LED_PREVIEW_PRODUCT_REL)

    def test_relay_catalog_entry_remains_hardware_pending(self) -> None:
        entry = self._find(RELAY_CONFIG_STRING)
        self.assertEqual(entry["status"], "hardware-pending")
        self.assertFalse(entry["webflash_build_matrix"])
        self.assertNotIn("artifact_name", entry)
        self.assertEqual(entry["product_yaml"], RELAY_PRODUCT_REL)

    def test_fantriac_catalog_entry_remains_blocked(self) -> None:
        entry = self._find(FANTRIAC_BLOCKED_CONFIG_STRING)
        self.assertEqual(entry["status"], "blocked")
        self.assertFalse(entry["webflash_build_matrix"])

    def test_release_one_required_configs_unchanged(self) -> None:
        compat = _load_json(WEBFLASH_COMPATIBILITY)
        self.assertEqual(
            compat.get("release_one_required_configs"),
            [RELEASE_ONE_CONFIG_STRING],
            "release_one_required_configs must remain "
            "[Ceiling-POE-VentIQ-RoomIQ]; PRODUCT-DAC-001 does not add "
            "FanDAC to the Release-One required configs.",
        )


# MANUAL-FIRMWARE-CANDIDATE-001: the registered TOP-LEVEL FanDAC product
# compile-only target (distinct from the products/compile-only/ skeleton).
FANDAC_PRODUCT_COMPILE_ONLY_TARGET_ID = "ceiling-poe-fandac-product-compile-only"


class FanDacManualFirmwareCandidateTests(unittest.TestCase):
    """MANUAL-FIRMWARE-CANDIDATE-001: FanDAC is a manual / no-WebFlash
    firmware candidate — present, structurally validated, full-compile
    validated — but no more than that.

    Pins: the top-level product compile-only target is
    ``validated-full-compile``; the catalog notes record the candidate
    status and disclaim release / WebFlash / hardware-stable / compliance /
    Cloudlift readiness; ``webflash_build_matrix`` stays false; no
    ``artifact_name`` / ``webflash_wrapper`` / WebFlash wrapper file / build
    entry is added.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.targets = _load_json(COMPILE_ONLY_TARGETS).get("targets", [])
        cls.by_id = {t["id"]: t for t in cls.targets if t.get("id")}
        cls.entry = _catalog_entry_for(DAC_PRODUCT_REL)

    def _target(self) -> Dict[str, Any]:
        target = self.by_id.get(FANDAC_PRODUCT_COMPILE_ONLY_TARGET_ID)
        self.assertIsNotNone(
            target,
            "top-level FanDAC product compile-only target "
            f"{FANDAC_PRODUCT_COMPILE_ONLY_TARGET_ID!r} must be registered",
        )
        return target

    def test_top_level_target_points_at_product_yaml(self) -> None:
        self.assertEqual(self._target().get("product_yaml"), DAC_PRODUCT_REL)

    def test_top_level_target_is_validated_full_compile(self) -> None:
        self.assertEqual(
            self._target().get("compile_validation_status"),
            "validated-full-compile",
            "FanDAC top-level product compile-only target must be "
            "validated-full-compile — the full-compile evidence that makes "
            "FanDAC a manual / no-WebFlash firmware candidate",
        )

    def test_catalog_notes_record_manual_candidate_status(self) -> None:
        notes = self.entry.get("notes", "").lower()
        self.assertIn("manual / no-webflash firmware candidate", notes)
        self.assertIn("manual-firmware-candidate-001", notes)
        self.assertIn("full-compile validated", notes)

    def test_catalog_notes_disclaim_readiness(self) -> None:
        notes = self.entry.get("notes", "").lower()
        for marker in (
            "not a release artifact",
            "not webflash exposure",
            "not hardware-stable",
            "not compliance",
            "not cloudlift-ready",
        ):
            self.assertIn(
                marker, notes, f"FanDAC notes must disclaim {marker!r}"
            )

    def test_catalog_status_stays_hardware_pending(self) -> None:
        self.assertEqual(self.entry.get("status"), "hardware-pending")

    def test_catalog_webflash_build_matrix_stays_false(self) -> None:
        self.assertEqual(self.entry.get("webflash_build_matrix"), False)

    def test_catalog_has_no_artifact_name(self) -> None:
        self.assertNotIn("artifact_name", self.entry)

    def test_catalog_has_no_webflash_wrapper(self) -> None:
        self.assertNotIn("webflash_wrapper", self.entry)

    def test_no_webflash_wrapper_file(self) -> None:
        offenders = (
            [
                p.name
                for p in WEBFLASH_WRAPPER_DIR.glob("*.yaml")
                if "fandac" in p.name.lower()
            ]
            if WEBFLASH_WRAPPER_DIR.is_dir()
            else []
        )
        self.assertEqual(offenders, [])

    def test_config_string_not_in_webflash_builds(self) -> None:
        builds = _load_json(WEBFLASH_BUILDS)
        configs = {
            b.get("config_string") for b in builds.get("builds", []) or []
        }
        self.assertNotIn(DAC_CONFIG_STRING, configs)

    def test_config_string_not_in_release_one_required(self) -> None:
        compat = _load_json(WEBFLASH_COMPATIBILITY)
        self.assertNotIn(
            DAC_CONFIG_STRING,
            compat.get("release_one_required_configs", []) or [],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

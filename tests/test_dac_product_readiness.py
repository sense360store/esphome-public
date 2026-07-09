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

HW-RELEASE-001 (docs/hw-release-001.md, owner decision of record,
2026-07-09) retired the bench-proof documentation requirement as a
release gate; hardware readiness is declared by the owner directly.
Under that decision the FanDAC product is now a release-eligible
PREVIEW-channel config:

  * a thin packages-only WebFlash wrapper under ``products/webflash/``
    re-exporting the canonical product YAML;
  * ``status: preview`` + ``webflash_build_matrix: true`` +
    ``artifact_name`` + ``webflash_wrapper`` in
    ``config/product-catalog.json`` (hardware_status
    ``owner-declared-bench-working-hw-release-001``);
  * a ``config/webflash-builds.json`` row on the PREVIEW channel
    (release_state metadata-ready-unpublished — metadata only, no
    binary / Release / tag / manifest is cut).

Unchanged truths these tests keep pinning:

  * fan configs are NEVER on the stable channel — FanDAC rows are
    ``preview``, never ``stable``; RELEASE-DAC-001 remains the STABLE
    blocker and FANDAC-I2C-ADDR-001 stays PENDING;
  * still NO entry in ``release_one_required_configs``; the builds-row
    ``commercial_posture`` keeps buyable / recommended /
    customer_default / stable false;
  * the J3 silkscreen transposition, Cloudlift S12 harness /
    product-bench, and full-compile-validated (run 26364679370 /
    CONFIG-FRESHNESS-001) caveats stay in the product YAML;
  * promotion is firmware-build proof only under owner declaration —
    no hardware / bench / compliance / safety /
    commercial-availability claim.

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
# HW-RELEASE-001: the release-gate WebFlash wrapper now exists.
DAC_WRAPPER_REL = "products/webflash/ceiling-poe-fandac.yaml"
# HW-RELEASE-001 owner declaration marker recorded in the catalog.
OWNER_DECLARED_HW_STATUS = "owner-declared-bench-working-hw-release-001"
# The two air-quality + FanDAC room-bundle configs that require the IC2
# 0x5A address override (0x59 is forbidden when VentIQ / AirIQ shares the
# core_i2c bus; FANDAC-I2C-ADDR-001 stays PENDING).
DAC_AIR_QUALITY_CONFIG_STRINGS = (
    "Ceiling-POE-AirIQ-FanDAC-RoomIQ",
    "Ceiling-POE-VentIQ-FanDAC-RoomIQ",
)

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


def _builds_row_for(config_string: str) -> Dict[str, Any]:
    doc = _load_json(WEBFLASH_BUILDS)
    for row in doc.get("builds", []) or []:
        if row.get("config_string") == config_string:
            return row
    raise AssertionError(
        f"no config/webflash-builds.json row for {config_string!r} — "
        f"HW-RELEASE-001 declares this config release-eligible"
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


class DacProductWebFlashReleaseSurfaceTests(unittest.TestCase):
    """HW-RELEASE-001: FanDAC IS release-eligible — on the PREVIEW channel.

    Rewritten from the former ``DacProductWebFlashExposureGuardsTests``
    (which pinned the pre-HW-RELEASE-001 "no WebFlash exposure" posture).
    HW-RELEASE-001 (docs/hw-release-001.md, 2026-07-09) retired the
    bench-proof documentation requirement as a release gate; the owner
    declares hardware readiness directly. The inverted invariants: the
    catalog entry is status preview with webflash_build_matrix true, an
    artifact_name, and an existing thin webflash wrapper; the builds row
    exists on the PREVIEW channel. The preserved invariants: fan configs
    are NEVER stable, RELEASE-DAC-001 remains the STABLE blocker,
    FANDAC-I2C-ADDR-001 stays PENDING (0x59 forbidden next to VentIQ /
    AirIQ), the commercial posture stays non-customer, promotion is
    firmware-build proof only, and FanDAC stays out of
    release_one_required_configs.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.entry = _catalog_entry_for(DAC_PRODUCT_REL)
        cls.builds_doc = _load_json(WEBFLASH_BUILDS)
        cls.compat = _load_json(WEBFLASH_COMPATIBILITY)
        cls.row = _builds_row_for(DAC_CONFIG_STRING)

    def test_catalog_entry_webflash_build_matrix_is_true(self) -> None:
        self.assertEqual(
            self.entry.get("webflash_build_matrix"),
            True,
            "FanDAC product catalog entry must set "
            "webflash_build_matrix: true — HW-RELEASE-001 promoted the "
            "config into the declaration-driven release matrix.",
        )

    def test_catalog_entry_status_is_preview(self) -> None:
        self.assertEqual(
            self.entry.get("status"),
            "preview",
            "FanDAC product catalog entry must be status: preview (a "
            "release-eligible status) per owner decision HW-RELEASE-001.",
        )

    def test_catalog_entry_channel_is_preview_never_stable(self) -> None:
        self.assertEqual(
            self.entry.get("channel"),
            "preview",
            "FanDAC catalog channel must be exactly 'preview' — fan "
            "configs are NEVER on the stable channel (HW-RELEASE-001 "
            "channel-teeth revision of the fan-token guardrail).",
        )

    def test_catalog_entry_artifact_name_matches_contract(self) -> None:
        version = self.entry.get("version")
        channel = self.entry.get("channel")
        self.assertEqual(version, "1.0.0")
        self.assertEqual(
            self.entry.get("artifact_name"),
            f"Sense360-{DAC_CONFIG_STRING}-v{version}-{channel}.bin",
            "FanDAC artifact_name must follow the "
            "Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin contract.",
        )

    def test_catalog_entry_hardware_status_is_owner_declared(self) -> None:
        self.assertEqual(
            self.entry.get("hardware_status"),
            OWNER_DECLARED_HW_STATUS,
            "FanDAC hardware_status must record the HW-RELEASE-001 owner "
            "declaration (owner-declared, not measured/bench-proven).",
        )

    def test_catalog_entry_declares_existing_webflash_wrapper(self) -> None:
        self.assertEqual(
            self.entry.get("webflash_wrapper"),
            DAC_WRAPPER_REL,
            "FanDAC catalog entry must declare the products/webflash "
            "wrapper HW-RELEASE-001 added.",
        )
        self.assertTrue(
            (REPO_ROOT / DAC_WRAPPER_REL).is_file(),
            f"declared webflash_wrapper {DAC_WRAPPER_REL!r} must exist",
        )

    def test_webflash_wrapper_is_thin_packages_only_reexport(self) -> None:
        wrapper = REPO_ROOT / DAC_WRAPPER_REL
        data = _load_yaml(wrapper)
        self.assertEqual(
            set(data.keys()),
            {"packages"},
            "the FanDAC WebFlash wrapper must be a thin packages-only "
            "re-export (no substitutions / esphome / component blocks).",
        )
        includes = list((data.get("packages") or {}).values())
        self.assertEqual(
            includes,
            ["../sense360-ceiling-poe-fandac.yaml"],
            "the wrapper must !include exactly the canonical "
            "products/sense360-ceiling-poe-fandac.yaml (as ../sense360-*).",
        )

    def test_dac_builds_row_is_preview_channel(self) -> None:
        self.assertEqual(
            self.row.get("channel"),
            "preview",
            "the FanDAC config/webflash-builds.json row must be on the "
            "preview channel — never stable (HW-RELEASE-001).",
        )
        self.assertEqual(self.row.get("product_yaml"), DAC_WRAPPER_REL)
        self.assertEqual(
            self.row.get("artifact_name"),
            self.entry.get("artifact_name"),
            "builds-row artifact_name must match the catalog entry",
        )

    def test_all_fandac_rows_preview_never_stable(self) -> None:
        rows = [
            row
            for row in self.builds_doc.get("builds", []) or []
            if "FanDAC" in row.get("config_string", "")
        ]
        self.assertTrue(rows, "expected FanDAC rows post HW-RELEASE-001")
        for row in rows:
            with self.subTest(config_string=row.get("config_string")):
                self.assertEqual(
                    row.get("channel"),
                    "preview",
                    "every FanDAC builds row must be on the preview "
                    "channel exactly — fan configs are NEVER stable.",
                )

    def test_fandac_rows_keep_release_dac_and_i2c_addr_blockers(self) -> None:
        # RELEASE-DAC-001 remains the STABLE blocker and FANDAC-I2C-ADDR-001
        # stays PENDING; HW-RELEASE-001 promoted preview only, not stable.
        for row in self.builds_doc.get("builds", []) or []:
            if "FanDAC" not in row.get("config_string", ""):
                continue
            with self.subTest(config_string=row.get("config_string")):
                blocker = row.get("stable_blocker", "")
                self.assertIn("RELEASE-DAC-001", blocker)
                self.assertIn("FANDAC-I2C-ADDR-001", blocker)

    def test_air_quality_fandac_rows_carry_0x5a_override(self) -> None:
        # 0x59 is forbidden when VentIQ / AirIQ shares the core_i2c bus:
        # the air-quality FanDAC rows must document the IC2 0x5A relocation
        # away from the 0x59 package default (FANDAC-I2C-ADDR-001 pending).
        for cs in DAC_AIR_QUALITY_CONFIG_STRINGS:
            with self.subTest(config_string=cs):
                notes = _builds_row_for(cs).get("notes", "")
                self.assertIn("0x5A", notes)
                self.assertIn("0x59", notes)

    def test_dac_builds_row_commercial_posture_stays_non_customer(
        self,
    ) -> None:
        posture = self.row.get("commercial_posture") or {}
        for key in ("buyable", "recommended", "customer_default", "stable"):
            self.assertIs(
                posture.get(key),
                False,
                f"FanDAC builds-row commercial_posture.{key} must stay "
                f"false — HW-RELEASE-001 changes no customer visibility.",
            )

    def test_dac_builds_row_claims_firmware_build_proof_only(self) -> None:
        notes = self.row.get("notes", "").lower()
        self.assertIn(
            "firmware-build proof only",
            notes,
            "the FanDAC builds row must state promotion is firmware-build "
            "proof only (no false proof claims under HW-RELEASE-001).",
        )
        self.assertIn(
            "no hardware / bench / compliance",
            notes,
            "the FanDAC builds row must disclaim hardware / bench / "
            "compliance proof.",
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


class ReleaseOneRelayAndLedPostureTests(unittest.TestCase):
    """Release-One, LED preview, FanRelay, and FanTRIAC posture.

    Release-One and the LED preview stay untouched. The FanRelay sibling
    is pinned at its HW-RELEASE-001 posture (release-eligible preview
    status; experimental channel only; never stable), and FanTRIAC keeps
    its experimental-only lane.
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
        # Version-agnostic: release bumps move version + artifact_name in
        # lock-step, so assert the invariant shape instead of pinning v1.0.0.
        entry = self._find(RELEASE_ONE_CONFIG_STRING)
        self.assertEqual(entry["status"], "production")
        self.assertEqual(entry["channel"], "stable")
        self.assertEqual(
            entry["artifact_name"],
            f"Sense360-{RELEASE_ONE_CONFIG_STRING}-v{entry['version']}-stable.bin",
        )
        self.assertTrue(entry["webflash_build_matrix"])
        self.assertEqual(entry["product_yaml"], RELEASE_ONE_PRODUCT_REL)

    def test_led_preview_catalog_entry_is_unchanged_preview(self) -> None:
        entry = self._find(LED_PREVIEW_CONFIG_STRING)
        self.assertEqual(entry["status"], "preview")
        self.assertEqual(entry["channel"], "preview")
        self.assertTrue(entry["webflash_build_matrix"])
        self.assertEqual(entry["product_yaml"], LED_PREVIEW_PRODUCT_REL)

    def test_relay_catalog_entry_is_experimental_preview(self) -> None:
        # HW-RELEASE-001 promoted the FanRelay sibling by owner declaration:
        # status preview, release-eligible, but on the EXPERIMENTAL channel
        # only (mains-adjacent lane per COMPLIANCE-001; never stable).
        entry = self._find(RELAY_CONFIG_STRING)
        self.assertEqual(entry["status"], "preview")
        self.assertEqual(entry["channel"], "experimental")
        self.assertTrue(entry["webflash_build_matrix"])
        self.assertEqual(
            entry["artifact_name"],
            f"Sense360-{RELAY_CONFIG_STRING}-v{entry['version']}"
            "-experimental.bin",
        )
        self.assertEqual(entry["product_yaml"], RELAY_PRODUCT_REL)
        self.assertEqual(entry["hardware_status"], OWNER_DECLARED_HW_STATUS)

    def test_fantriac_catalog_entry_is_experimental_self_build(self) -> None:
        # TRIAC-COMMISSIONING-001 moved FanTRIAC into the experimental
        # self-build mains lane (status preview, channel experimental). This PR
        # (FanDAC readiness) does not change FanTRIAC; the preserved invariant
        # is that FanTRIAC is never a normal customer build — it stays on the
        # experimental channel and never stable.
        entry = self._find(FANTRIAC_BLOCKED_CONFIG_STRING)
        self.assertEqual(entry["status"], "preview")
        self.assertEqual(entry.get("channel"), "experimental")
        self.assertIs(
            entry.get("experimental_lane_posture", {}).get("never_stable"), True
        )

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
    """MANUAL-FIRMWARE-CANDIDATE-001 evidence + HW-RELEASE-001 promotion.

    The full-compile evidence trail stands: the top-level product
    compile-only target is ``validated-full-compile``, and the catalog
    notes keep the candidate record and its no-false-proof disclaimers.
    The former "no more than a manual candidate" pins (status
    hardware-pending, no wrapper, no artifact, no build row) were
    inverted by owner decision HW-RELEASE-001: the entry is now a
    release-eligible preview-channel config, still firmware-build proof
    only and never stable.
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

    def test_catalog_status_is_preview_per_hw_release_001(self) -> None:
        # Inverted from "stays hardware-pending" by HW-RELEASE-001.
        self.assertEqual(self.entry.get("status"), "preview")

    def test_catalog_webflash_build_matrix_is_true(self) -> None:
        # Inverted from "stays false" by HW-RELEASE-001.
        self.assertEqual(self.entry.get("webflash_build_matrix"), True)

    def test_catalog_declares_contract_artifact_name(self) -> None:
        # Inverted from "no artifact_name" by HW-RELEASE-001.
        self.assertEqual(
            self.entry.get("artifact_name"),
            f"Sense360-{DAC_CONFIG_STRING}-v{self.entry.get('version')}"
            f"-{self.entry.get('channel')}.bin",
        )

    def test_catalog_declares_webflash_wrapper(self) -> None:
        # Inverted from "no webflash_wrapper" by HW-RELEASE-001.
        self.assertEqual(self.entry.get("webflash_wrapper"), DAC_WRAPPER_REL)

    def test_webflash_wrapper_file_exists_and_is_thin(self) -> None:
        # Inverted from "no wrapper file" by HW-RELEASE-001: the wrapper
        # exists and is a thin packages-only re-export of the canonical
        # product YAML.
        wrapper = REPO_ROOT / DAC_WRAPPER_REL
        self.assertTrue(wrapper.is_file())
        data = _load_yaml(wrapper)
        self.assertEqual(set(data.keys()), {"packages"})
        self.assertIn(
            "../sense360-ceiling-poe-fandac.yaml",
            list((data.get("packages") or {}).values()),
        )

    def test_config_string_in_webflash_builds_preview_never_stable(
        self,
    ) -> None:
        # Inverted from "not in webflash-builds" by HW-RELEASE-001; the
        # preserved half is channel teeth: preview only, never stable.
        row = _builds_row_for(DAC_CONFIG_STRING)
        self.assertEqual(row.get("channel"), "preview")
        self.assertNotEqual(row.get("channel"), "stable")

    def test_config_string_not_in_release_one_required(self) -> None:
        compat = _load_json(WEBFLASH_COMPATIBILITY)
        self.assertNotIn(
            DAC_CONFIG_STRING,
            compat.get("release_one_required_configs", []) or [],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

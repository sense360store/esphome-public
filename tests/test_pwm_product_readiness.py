#!/usr/bin/env python3
"""PRODUCT-PWM-001 invariants for the FanPWM product YAML.

PRODUCT-PWM-001 adds a single canonical FanPWM product YAML
(``products/sense360-ceiling-poe-fanpwm.yaml``) as the
**product-YAML-only / no-WebFlash-exposure** slice that follows
PACKAGE-PWM-001-IMPLEMENT-001 (PR #590, package layer),
FW-COMPILE-PWM-001 (PR #591, compile-only target) and
FW-COMPILE-PWM-RESULT-001 (PR #592, full-compile result). The product
composes Core ceiling + PoE PSU + base/health with the canonical
PWM-drive-only FanPWM package ``packages/expansions/fan_pwm.yaml`` (four
independent SX1509 PWM-drive fan-speed controllers; composes the neutral
binding ``packages/expansions/fan_pwm_sx1509.yaml``). The customer
outcome is four-channel 12V PWM fan-speed control on the S360-311 board.

HW-RELEASE-001 (docs/hw-release-001.md, owner decision of record,
2026-07-09) retired the bench-proof documentation requirement as a
release gate; hardware readiness is declared by the owner directly.
Under that decision the FanPWM product is now a release-eligible
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

  * fan configs are NEVER on the stable channel — FanPWM / FanDAC rows
    are ``preview``, FanRelay rows are ``experimental``, none ever
    ``stable``; RELEASE-PWM-001 remains the STABLE blocker;
  * still NO entry in ``release_one_required_configs``; the builds-row
    ``commercial_posture`` keeps buyable / recommended /
    customer_default / stable false;
  * NO RPM support (``rpm_supported`` false; native tach inputs stay
    internal diagnostic only) and ``TachIO`` / ``GPIO16`` stays
    reserved / pending;
  * promotion is firmware-build proof only under owner declaration —
    no hardware / bench / compliance / safety /
    commercial-availability claim.

Run with::

    python3 tests/test_pwm_product_readiness.py

or::

    python3 -m unittest tests.test_pwm_product_readiness -v
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from typing import Any, Dict, List

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent

PWM_PRODUCT_YAML = REPO_ROOT / "products" / "sense360-ceiling-poe-fanpwm.yaml"
PWM_PRODUCT_REL = "products/sense360-ceiling-poe-fanpwm.yaml"
PWM_CONFIG_STRING = "Ceiling-POE-FanPWM"
# HW-RELEASE-001: the release-gate WebFlash wrapper now exists.
PWM_WRAPPER_REL = "products/webflash/ceiling-poe-fanpwm.yaml"
# HW-RELEASE-001 owner declaration marker recorded in the catalog.
OWNER_DECLARED_HW_STATUS = "owner-declared-bench-working-hw-release-001"
# Fan channel policy (HW-RELEASE-001 revision of the former fan-token
# guardrail): fan configs are NEVER stable; FanPWM / FanDAC ship preview,
# FanRelay / FanTRIAC ship experimental only.
FAN_TOKEN_EXPECTED_CHANNEL = {
    "FanPWM": "preview",
    "FanDAC": "preview",
    "FanRelay": "experimental",
    "FanTRIAC": "experimental",
}
# The product YAML is now a thin compat shim; its full composition/substitution
# content lives in the bundle. Content reads must target the bundle.
PWM_BUNDLE = REPO_ROOT / "products" / "bundles" / "ceiling-poe-fanpwm.yaml"

# Existing siblings that PRODUCT-PWM-001 must not disturb.
RELEASE_ONE_PRODUCT_REL = "products/sense360-ceiling-poe-ventiq-roomiq.yaml"
RELEASE_ONE_CONFIG_STRING = "Ceiling-POE-VentIQ-RoomIQ"
LED_PREVIEW_PRODUCT_REL = "products/sense360-ceiling-poe-ventiq-roomiq-led.yaml"
LED_PREVIEW_CONFIG_STRING = "Ceiling-POE-VentIQ-RoomIQ-LED"
RELAY_PRODUCT_REL = "products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml"
RELAY_CONFIG_STRING = "Ceiling-POE-VentIQ-FanRelay-RoomIQ"
DAC_PRODUCT_REL = "products/sense360-ceiling-poe-fandac.yaml"
DAC_CONFIG_STRING = "Ceiling-POE-FanDAC"
FANTRIAC_BLOCKED_CONFIG_STRING = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"

PRODUCT_CATALOG = REPO_ROOT / "config" / "product-catalog.json"
WEBFLASH_BUILDS = REPO_ROOT / "config" / "webflash-builds.json"
WEBFLASH_COMPATIBILITY = REPO_ROOT / "config" / "webflash-compatibility.json"
WEBFLASH_WRAPPER_DIR = REPO_ROOT / "products" / "webflash"

# The FW-COMPILE-PWM-001 legacy SX1509 compile-only skeleton must remain
# unchanged (historical / superseded compile proof; SX1509-RECONCILE-001 does
# not touch it).
COMPILE_ONLY_TARGETS = REPO_ROOT / "config" / "compile-only-targets.json"
FANPWM_COMPILE_ONLY_TARGET_ID = "ceiling-poe-fanpwm-compile-only"
FANPWM_COMPILE_ONLY_PRODUCT_YAML = "products/compile-only/ceiling-poe-fanpwm.yaml"

# SX1509-RECONCILE-001: the bundle is now migrated off the deprecated SX1509
# path to the NATIVE ESP32-S3 GPIO FanPWM package
# (packages/expansions/fan_pwm_native.yaml). The bundle composes the IDENTICAL
# package set as the native compile-only skeleton, whose full `esphome compile`
# is recorded green by S360-311-NATIVE-FANPWM-COMPILE-001 (commit 643bbd3).
FANPWM_NATIVE_COMPILE_ONLY_TARGET_ID = "ceiling-poe-fanpwm-native-compile-only"
FANPWM_NATIVE_COMPILE_ONLY_PRODUCT_YAML = (
    "products/compile-only/ceiling-poe-fanpwm-native.yaml"
)
FANPWM_NATIVE_PACKAGE_REL = "packages/expansions/fan_pwm_native.yaml"

# Legacy SX1509 full-compile evidence (run 26414398902) — still recorded for
# the preserved legacy skeleton/target, but it does NOT transfer to the native
# composition this bundle now composes.
FANPWM_FULL_COMPILE_RUN_ID = "26414398902"
# Native full-compile evidence the migrated bundle/product lane references.
FANPWM_NATIVE_COMPILE_EVIDENCE = "S360-311-NATIVE-FANPWM-COMPILE-001"
FANPWM_NATIVE_COMPILE_COMMIT = "643bbd3"


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
        f"config/product-catalog.json (PRODUCT-PWM-001 requires a "
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


def _fan_rows() -> List[Dict[str, Any]]:
    """All builds rows whose config_string carries a fan-driver token."""
    doc = _load_json(WEBFLASH_BUILDS)
    return [
        row
        for row in doc.get("builds", []) or []
        if any(
            token in row.get("config_string", "")
            for token in FAN_TOKEN_EXPECTED_CHANNEL
        )
    ]


def _package_include_map(yaml_path: Path) -> Dict[str, str]:
    """Return ``{package_key: repo-relative !include target}`` for a YAML.

    The minimal ESPHome constructors registered above turn an ``!include
    <path>`` scalar into the raw (directory-relative) path string, so every
    ``packages:`` value is that include target. Resolve it against the YAML's
    own directory and re-root on ``REPO_ROOT`` so a top-level product YAML
    (``../packages/...``) and a ``products/compile-only/`` skeleton
    (``../../packages/...``) become directly comparable.
    """
    data = _load_yaml(yaml_path)
    packages = data.get("packages", {}) or {}
    out: Dict[str, str] = {}
    base = yaml_path.parent
    for key, value in packages.items():
        resolved = (base / str(value)).resolve()
        out[key] = resolved.relative_to(REPO_ROOT).as_posix()
    return out


class PwmProductYamlExistsTests(unittest.TestCase):
    """The PRODUCT-PWM-001 product YAML exists at the canonical path."""

    def test_product_yaml_file_exists(self) -> None:
        self.assertTrue(
            PWM_PRODUCT_YAML.is_file(),
            f"PRODUCT-PWM-001 must add the FanPWM product YAML at "
            f"{PWM_PRODUCT_YAML} (config string {PWM_CONFIG_STRING})",
        )

    def test_product_yaml_parses_as_yaml(self) -> None:
        data = _load_yaml(PWM_BUNDLE)
        self.assertIsInstance(
            data,
            dict,
            "FanPWM product YAML must parse as a YAML mapping",
        )
        for key in ("substitutions", "packages"):
            self.assertIn(
                key,
                data,
                f"FanPWM product YAML must declare a top-level `{key}:` block",
            )

    def test_product_yaml_is_enumerated_in_catalog(self) -> None:
        entry = _catalog_entry_for(PWM_PRODUCT_REL)
        self.assertEqual(entry.get("config_string"), PWM_CONFIG_STRING)

    def test_product_yaml_not_under_webflash_dir(self) -> None:
        self.assertFalse(
            PWM_PRODUCT_REL.startswith("products/webflash/"),
            "FanPWM product YAML must NOT live under products/webflash/ "
            "(the WebFlash wrapper namespace)",
        )

    def test_product_yaml_not_under_compile_only_dir(self) -> None:
        self.assertFalse(
            PWM_PRODUCT_REL.startswith("products/compile-only/"),
            "FanPWM product YAML must be a top-level products/ YAML, not a "
            "compile-only skeleton",
        )


class PwmProductPackageCompositionTests(unittest.TestCase):
    """The product composes the FanPWM package + the Core / PoE base stack."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.data = _load_yaml(PWM_BUNDLE)
        cls.packages = cls.data.get("packages", {}) or {}
        cls.text = PWM_BUNDLE.read_text()

    def test_packages_block_is_a_mapping(self) -> None:
        self.assertIsInstance(
            self.packages,
            dict,
            "FanPWM product YAML `packages:` block must be a mapping",
        )

    def test_includes_fan_pwm_package(self) -> None:
        # SX1509-RECONCILE-001: the bundle now composes the NATIVE ESP32-S3
        # GPIO FanPWM package instead of the deprecated SX1509 chain.
        self.assertIn(
            FANPWM_NATIVE_PACKAGE_REL,
            self.text,
            "FanPWM bundle must !include packages/expansions/fan_pwm_native.yaml "
            "so the PWM-drive outputs are composed through the native ESP32-S3 "
            "GPIO FanPWM package (SX1509-RECONCILE-001 migrated it off the "
            "deprecated SX1509 fan_pwm.yaml -> fan_pwm_sx1509.yaml chain).",
        )

    def test_does_not_compose_legacy_sx1509_fan_pwm_package(self) -> None:
        # The migrated bundle must NOT compose the legacy SX1509 driver on an
        # active (non-comment) line; the legacy packages are preserved only as
        # historical / superseded compile proof, not composed here.
        for line in _active_lines(self.text):
            self.assertNotIn(
                "packages/expansions/fan_pwm.yaml",
                line,
                "FanPWM bundle must not compose the legacy SX1509 "
                f"packages/expansions/fan_pwm.yaml on an active line: {line!r}",
            )

    def test_includes_core_ceiling_package(self) -> None:
        self.assertIn(
            "packages/hardware/sense360_core_ceiling.yaml",
            self.text,
            "FanPWM product YAML must !include the Core ceiling abstract "
            "package so the SX1509 expander binds to the shared core_i2c bus.",
        )

    def test_includes_poe_power_package(self) -> None:
        self.assertIn(
            "packages/hardware/power_poe.yaml",
            self.text,
            "FanPWM product YAML must !include the PoE power package.",
        )

    def test_includes_device_health_package(self) -> None:
        self.assertIn(
            "packages/features/device_health.yaml",
            self.text,
            "FanPWM product YAML must !include the device health package.",
        )

    def test_does_not_include_other_fan_driver_packages(self) -> None:
        # Fan driver variants are firmware-distinct; this product ships
        # FanPWM only.
        for forbidden in (
            "packages/expansions/fan_relay.yaml",
            "packages/expansions/fan_triac.yaml",
            "packages/expansions/fan_dac.yaml",
            "packages/expansions/fan_gp8403.yaml",
            "packages/expansions/sense360_fan_pwm.yaml",
        ):
            self.assertNotIn(
                forbidden,
                self.text,
                f"FanPWM product YAML must NOT !include {forbidden}; "
                "fan-driver variants are firmware-distinct and this "
                "product ships the PWM-drive-only FanPWM package only.",
            )

    def test_config_string_text_sensor_is_present(self) -> None:
        sensors = self.data.get("text_sensor", []) or []
        lambdas = " ".join(
            str(s.get("lambda", "")) for s in sensors if isinstance(s, dict)
        )
        self.assertIn(
            PWM_CONFIG_STRING,
            lambdas,
            f"FanPWM product YAML must surface the {PWM_CONFIG_STRING!r} "
            "config string via a template text_sensor (catalog convention).",
        )


class PwmProductNoRpmNoPulseCounterTests(unittest.TestCase):
    """The product makes no RPM claim and wires no ``pulse_counter``."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = PWM_BUNDLE.read_text()

    def test_no_pulse_counter_on_active_line(self) -> None:
        for line in _active_lines(self.text):
            self.assertNotIn(
                "pulse_counter",
                line,
                "FanPWM product YAML must not use pulse_counter on any "
                f"active line (no per-fan RPM). Line: {line!r}",
            )

    def test_no_rpm_named_or_unit_entities(self) -> None:
        for line in _active_lines(self.text):
            low = line.lower()
            if "name:" in low or "unit_of_measurement:" in low:
                self.assertNotIn(
                    "rpm",
                    low,
                    "FanPWM product YAML must expose no RPM-named / RPM-unit "
                    f"entity (PWM-drive-only). Line: {line!r}",
                )

    def test_no_tachio_gpio16_active_binding(self) -> None:
        for line in _active_lines(self.text):
            self.assertNotIn(
                "${tach_io_pin}",
                line,
                "FanPWM product YAML must not consume ${tach_io_pin} — "
                f"TachIO / GPIO16 stays reserved/pending. Line: {line!r}",
            )
            self.assertNotRegex(
                line,
                r"\bGPIO16\b",
                "FanPWM product YAML must not bind GPIO16 (TachIO) on an "
                f"active line — it is reserved/pending. Line: {line!r}",
            )

    def test_underlying_native_package_tach_is_internal_no_rpm(self) -> None:
        # SX1509-RECONCILE-001: the native FanPWM package DOES wire native
        # pulse_counter tach inputs (a native interrupt-capable ESP32 GPIO can
        # back one, unlike an SX1509 expander pin). They must stay INTERNAL
        # diagnostic inputs with no RPM name / unit — no surfaced RPM.
        pkg = REPO_ROOT / "packages" / "expansions" / "fan_pwm_native.yaml"
        data = _load_yaml(pkg)
        sensors = [s for s in (data.get("sensor") or []) if isinstance(s, dict)]
        pulse_counters = [
            s for s in sensors if s.get("platform") == "pulse_counter"
        ]
        self.assertTrue(
            pulse_counters,
            "fan_pwm_native.yaml is expected to declare native pulse_counter "
            "tach inputs (internal diagnostic only).",
        )
        for s in pulse_counters:
            self.assertTrue(
                s.get("internal") is True,
                f"native pulse_counter {s.get('id')!r} must be internal: true "
                "(diagnostic only, never surfaced).",
            )
            self.assertNotIn("name", s, "native tach must carry no entity name")
            self.assertNotIn(
                "unit_of_measurement",
                s,
                "native tach must carry no unit (no RPM claim)",
            )


class PwmProductWebFlashReleaseSurfaceTests(unittest.TestCase):
    """HW-RELEASE-001: FanPWM IS release-eligible — on the PREVIEW channel.

    Rewritten from the former ``PwmProductWebFlashExposureGuardsTests``
    (which pinned the pre-HW-RELEASE-001 "no WebFlash exposure" posture).
    HW-RELEASE-001 (docs/hw-release-001.md, 2026-07-09) retired the
    bench-proof documentation requirement as a release gate; the owner
    declares hardware readiness directly. The inverted invariants: the
    catalog entry is status preview with webflash_build_matrix true, an
    artifact_name, and an existing thin webflash wrapper; the builds row
    exists on the PREVIEW channel. The preserved invariants: fan configs
    are NEVER stable, RELEASE-PWM-001 remains the STABLE blocker, the
    commercial posture stays non-customer, promotion is firmware-build
    proof only, and FanPWM stays out of release_one_required_configs.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.entry = _catalog_entry_for(PWM_PRODUCT_REL)
        cls.builds_doc = _load_json(WEBFLASH_BUILDS)
        cls.compat = _load_json(WEBFLASH_COMPATIBILITY)
        cls.row = _builds_row_for(PWM_CONFIG_STRING)

    def test_catalog_entry_webflash_build_matrix_is_true(self) -> None:
        self.assertEqual(
            self.entry.get("webflash_build_matrix"),
            True,
            "FanPWM product catalog entry must set "
            "webflash_build_matrix: true — HW-RELEASE-001 promoted the "
            "config into the declaration-driven release matrix.",
        )

    def test_catalog_entry_status_is_preview(self) -> None:
        self.assertEqual(
            self.entry.get("status"),
            "preview",
            "FanPWM product catalog entry must be status: preview (a "
            "release-eligible status) per owner decision HW-RELEASE-001.",
        )

    def test_catalog_entry_channel_is_preview_never_stable(self) -> None:
        self.assertEqual(
            self.entry.get("channel"),
            "preview",
            "FanPWM catalog channel must be exactly 'preview' — fan "
            "configs are NEVER on the stable channel (HW-RELEASE-001 "
            "channel-teeth revision of the fan-token guardrail).",
        )

    def test_catalog_entry_artifact_name_matches_contract(self) -> None:
        version = self.entry.get("version")
        channel = self.entry.get("channel")
        self.assertEqual(version, "1.0.0")
        self.assertEqual(
            self.entry.get("artifact_name"),
            f"Sense360-{PWM_CONFIG_STRING}-v{version}-{channel}.bin",
            "FanPWM artifact_name must follow the "
            "Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin contract.",
        )

    def test_catalog_entry_hardware_status_is_owner_declared(self) -> None:
        self.assertEqual(
            self.entry.get("hardware_status"),
            OWNER_DECLARED_HW_STATUS,
            "FanPWM hardware_status must record the HW-RELEASE-001 owner "
            "declaration (owner-declared, not measured/bench-proven).",
        )

    def test_catalog_entry_declares_existing_webflash_wrapper(self) -> None:
        self.assertEqual(
            self.entry.get("webflash_wrapper"),
            PWM_WRAPPER_REL,
            "FanPWM catalog entry must declare the products/webflash "
            "wrapper HW-RELEASE-001 added.",
        )
        self.assertTrue(
            (REPO_ROOT / PWM_WRAPPER_REL).is_file(),
            f"declared webflash_wrapper {PWM_WRAPPER_REL!r} must exist",
        )

    def test_webflash_wrapper_is_thin_packages_only_reexport(self) -> None:
        wrapper = REPO_ROOT / PWM_WRAPPER_REL
        data = _load_yaml(wrapper)
        self.assertEqual(
            set(data.keys()),
            {"packages"},
            "the FanPWM WebFlash wrapper must be a thin packages-only "
            "re-export (no substitutions / esphome / component blocks).",
        )
        includes = list((data.get("packages") or {}).values())
        self.assertEqual(
            includes,
            ["../sense360-ceiling-poe-fanpwm.yaml"],
            "the wrapper must !include exactly the canonical "
            "products/sense360-ceiling-poe-fanpwm.yaml (as ../sense360-*).",
        )

    def test_pwm_builds_row_is_preview_channel(self) -> None:
        self.assertEqual(
            self.row.get("channel"),
            "preview",
            "the FanPWM config/webflash-builds.json row must be on the "
            "preview channel — never stable (HW-RELEASE-001).",
        )
        self.assertEqual(self.row.get("product_yaml"), PWM_WRAPPER_REL)
        self.assertEqual(
            self.row.get("artifact_name"),
            self.entry.get("artifact_name"),
            "builds-row artifact_name must match the catalog entry",
        )

    def test_pwm_builds_row_stable_blocker_cites_release_pwm_001(self) -> None:
        self.assertIn(
            "RELEASE-PWM-001",
            self.row.get("stable_blocker", ""),
            "RELEASE-PWM-001 remains the STABLE blocker for FanPWM — "
            "HW-RELEASE-001 promoted preview only, not stable.",
        )

    def test_pwm_builds_row_commercial_posture_stays_non_customer(self) -> None:
        posture = self.row.get("commercial_posture") or {}
        for key in ("buyable", "recommended", "customer_default", "stable"):
            self.assertIs(
                posture.get(key),
                False,
                f"FanPWM builds-row commercial_posture.{key} must stay "
                f"false — HW-RELEASE-001 changes no customer visibility.",
            )

    def test_pwm_builds_row_claims_firmware_build_proof_only(self) -> None:
        notes = self.row.get("notes", "").lower()
        self.assertIn(
            "firmware-build proof only",
            notes,
            "the FanPWM builds row must state promotion is firmware-build "
            "proof only (no false proof claims under HW-RELEASE-001).",
        )
        self.assertIn(
            "no hardware / bench / compliance",
            notes,
            "the FanPWM builds row must disclaim hardware / bench / "
            "compliance proof.",
        )

    def test_no_fan_config_row_is_ever_stable(self) -> None:
        rows = _fan_rows()
        self.assertTrue(rows, "expected fan-config rows post HW-RELEASE-001")
        for row in rows:
            cs = row.get("config_string", "")
            with self.subTest(config_string=cs):
                self.assertNotEqual(
                    row.get("channel"),
                    "stable",
                    f"fan config {cs!r} must NEVER be on the stable "
                    f"channel (HW-RELEASE-001 channel-teeth guardrail).",
                )
                for token, channel in FAN_TOKEN_EXPECTED_CHANNEL.items():
                    if token in cs:
                        self.assertEqual(
                            row.get("channel"),
                            channel,
                            f"{token} config {cs!r} must be on the "
                            f"{channel!r} channel exactly.",
                        )

    def test_pwm_config_string_not_in_release_one_required_configs(
        self,
    ) -> None:
        required = self.compat.get("release_one_required_configs", []) or []
        self.assertNotIn(
            PWM_CONFIG_STRING,
            required,
            f"release_one_required_configs in "
            f"config/webflash-compatibility.json must not contain "
            f"{PWM_CONFIG_STRING!r} — PRODUCT-PWM-001 does not promote "
            f"FanPWM into Release-One required configs.",
        )

    def test_product_yaml_does_not_declare_webflash_build_matrix(
        self,
    ) -> None:
        for line in _active_lines(PWM_BUNDLE.read_text()):
            self.assertNotIn(
                "webflash_build_matrix",
                line,
                f"FanPWM product YAML must not declare a "
                f"`webflash_build_matrix` field — that field belongs to "
                f"the catalog entry only and must remain false. "
                f"Offending line: {line!r}",
            )

    def test_product_yaml_does_not_declare_artifact_name(self) -> None:
        for line in _active_lines(PWM_BUNDLE.read_text()):
            self.assertNotIn(
                "artifact_name",
                line,
                f"FanPWM product YAML must not declare an `artifact_name` "
                f"field — no release artifact is built by PRODUCT-PWM-001. "
                f"Offending line: {line!r}",
            )


class PwmProductCaveatWordingTests(unittest.TestCase):
    """The FanPWM product YAML carries the PRODUCT-PWM-001 caveats.

    PRODUCT-PWM-001 requires explicit full-compile-validated (run
    26414398902), no-RPM, PWM-polarity, current / thermal-envelope,
    TachIO-reserved, and no-WebFlash / no-release / no-compliance /
    not-hardware-stable caveat wording in the product YAML itself. These
    tests pin that wording so a later refactor cannot silently strip it.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = PWM_BUNDLE.read_text()
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
            f"FanPWM product YAML must contain wording matching {phrase!r} "
            f"({hint}). PRODUCT-PWM-001 requires the product YAML to carry "
            f"explicit no-WebFlash / full-compile-validated / no-RPM / "
            f"bench caveat text.",
        )

    def test_carries_native_gpio_wording(self) -> None:
        # SX1509-RECONCILE-001: the migrated bundle drives the fans on native
        # ESP32-S3 GPIO via ledc, not the SX1509 expander.
        self._assert_phrase(
            "native esp32-s3",
            "native ESP32-S3 GPIO fan path naming",
        )
        self._assert_phrase(
            "ledc",
            "native ledc PWM-drive output naming",
        )

    def test_carries_full_compile_validated_caveat(self) -> None:
        # The bundle now composes the native composition, whose full
        # `esphome compile` is recorded green by the native compile evidence
        # (the legacy SX1509 run does not transfer).
        self._assert_phrase(
            "esphome compile",
            "full ESPHome compile caveat",
        )
        self._assert_phrase(
            "validated-full-compile",
            "compile_validation_status: validated-full-compile now stands",
        )
        self._assert_phrase(
            FANPWM_NATIVE_COMPILE_EVIDENCE.lower(),
            "the native full-compile evidence id that validated the "
            "native FanPWM composition",
        )
        self._assert_phrase(
            FANPWM_NATIVE_COMPILE_COMMIT,
            "the commit the native full compile ran against",
        )

    def test_states_no_rpm_support(self) -> None:
        self._assert_phrase("rpm", "RPM reference")
        # The product must explicitly say RPM is not supported / no RPM.
        self.assertTrue(
            ("not rpm support" in self.normalized)
            or ("no per-fan and no aggregate rpm" in self.normalized)
            or ("makes no rpm claim" in self.normalized)
            or ("rpm is not supported" in self.normalized),
            "FanPWM product YAML must explicitly state that RPM is not "
            "supported / no RPM claim is made.",
        )

    def test_states_native_tach_internal_no_rpm(self) -> None:
        # SX1509-RECONCILE-001: the native path wires native pulse_counter
        # tach inputs, but only as INTERNAL diagnostic inputs with no RPM.
        self._assert_phrase(
            "pulse_counter",
            "native pulse_counter tach reference",
        )
        self._assert_phrase(
            "internal diagnostic",
            "native tach is internal diagnostic only (no RPM)",
        )

    def test_states_tachio_gpio16_reserved(self) -> None:
        self._assert_phrase("tachio", "TachIO reference")
        self._assert_phrase("gpio16", "GPIO16 reference")
        self._assert_phrase("reserved", "TachIO / GPIO16 reserved/pending")

    def test_carries_pwm_polarity_pending_caveat(self) -> None:
        self._assert_phrase("pwm polarity", "PWM polarity bench caveat")

    def test_carries_current_and_thermal_envelope_caveat(self) -> None:
        self._assert_phrase("current", "per-fan / aggregate current caveat")
        self._assert_phrase("thermal envelope", "thermal envelope caveat")

    def test_states_schematic_status_cataloged_unverified(self) -> None:
        self._assert_phrase(
            "cataloged_unverified",
            "S360-311 schematic_status stays cataloged_unverified",
        )

    def test_states_product_bench_not_complete(self) -> None:
        self._assert_phrase("bench", "product-bench caveat")

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

    def test_states_not_hardware_stable_ready(self) -> None:
        self._assert_phrase(
            "not hardware-stable-ready",
            "explicit not-hardware-stable-ready statement",
        )

    def test_does_not_claim_sx1509_lacks_pwm_output(self) -> None:
        # Guardrail: never say SX1509 lacks PWM output support. SX1509 PWM
        # drive IS supported and is the basis of the package.
        for bad in (
            "sx1509 does not support pwm",
            "sx1509 lacks pwm",
            "sx1509 cannot drive pwm",
            "no sx1509 pwm output",
        ):
            self.assertNotIn(
                bad,
                self.normalized,
                "FanPWM product YAML must not claim SX1509 lacks PWM output "
                f"support (it IS supported). Offending phrase: {bad!r}.",
            )


class PwmProductCompileOnlyTargetUnchangedTests(unittest.TestCase):
    """FW-COMPILE-PWM-001 compile-only skeleton / target stays unchanged.

    PRODUCT-PWM-001 adds a top-level product YAML but must not repoint or
    alter the existing compile-only target, which keeps pointing at the
    products/compile-only/ skeleton and stays validated-full-compile.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = _load_json(COMPILE_ONLY_TARGETS)
        cls.by_id = {
            t.get("id"): t for t in cls.doc.get("targets", []) if t.get("id")
        }
        cls.target = cls.by_id.get(FANPWM_COMPILE_ONLY_TARGET_ID)

    def test_compile_only_target_exists(self) -> None:
        self.assertIsNotNone(
            self.target,
            f"FanPWM compile-only target {FANPWM_COMPILE_ONLY_TARGET_ID!r} "
            "must remain present",
        )

    def test_compile_only_target_points_at_skeleton(self) -> None:
        self.assertIsNotNone(self.target)
        self.assertEqual(
            self.target.get("product_yaml"),
            FANPWM_COMPILE_ONLY_PRODUCT_YAML,
            "FanPWM compile-only target must keep pointing at the "
            "products/compile-only/ skeleton, not the top-level product "
            "YAML added by PRODUCT-PWM-001.",
        )

    def test_compile_only_target_shipment_status_unchanged(self) -> None:
        self.assertIsNotNone(self.target)
        self.assertEqual(self.target.get("shipment_status"), "compile-only")

    def test_compile_only_target_disallows_webflash_exposure(self) -> None:
        self.assertIsNotNone(self.target)
        self.assertFalse(self.target.get("webflash_exposure_allowed_now"))

    def test_compile_only_target_makes_no_rpm_claim(self) -> None:
        self.assertIsNotNone(self.target)
        self.assertFalse(
            self.target.get("rpm_supported", False),
            "FanPWM compile-only target must keep rpm_supported false.",
        )

    def test_compile_only_target_validated_full_compile(self) -> None:
        self.assertIsNotNone(self.target)
        self.assertEqual(
            self.target.get("compile_validation_status"),
            "validated-full-compile",
            "FanPWM compile-only target must remain "
            "compile_validation_status: validated-full-compile — the "
            f"full compile passed in run {FANPWM_FULL_COMPILE_RUN_ID} "
            "(FW-COMPILE-PWM-RESULT-001 / PR #592); PRODUCT-PWM-001 must "
            "not regress it.",
        )


class PwmProductMatchesValidatedCompileOnlyCompositionTests(unittest.TestCase):
    """SX1509-RECONCILE-001: the migrated bundle composes the SAME validated
    package set as the NATIVE full-compile-validated compile-only skeleton.

    ``products/compile-only/ceiling-poe-fanpwm-native.yaml`` is the native
    skeleton whose FULL ``esphome compile`` passed under
    S360-311-NATIVE-FANPWM-COMPILE-001 (commit 643bbd3, rc=0). The bundle now
    composes the native FanPWM package; these tests pin that the bundle and
    the native skeleton compose the identical Core ceiling + PoE PSU +
    base/health + native FanPWM package set (same package keys, same
    repo-relative ``!include`` targets), so the recorded native full compile
    transfers to the bundle's composition. The two differ only in
    substitutions / identification ``text_sensor`` wording, never in which
    packages are composed. The legacy SX1509 skeleton + run 26414398902 are
    preserved separately as historical / superseded proof and are NOT what the
    migrated bundle mirrors.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.compile_only_yaml = REPO_ROOT / FANPWM_NATIVE_COMPILE_ONLY_PRODUCT_YAML
        cls.product_map = _package_include_map(PWM_BUNDLE)
        cls.compile_map = _package_include_map(cls.compile_only_yaml)

    def test_compile_only_skeleton_file_exists(self) -> None:
        self.assertTrue(
            self.compile_only_yaml.is_file(),
            f"the native full-compile-validated compile-only skeleton "
            f"{FANPWM_NATIVE_COMPILE_ONLY_PRODUCT_YAML} must exist for the "
            "migrated bundle to inherit its validated composition",
        )

    def test_product_and_compile_only_compose_identical_package_set(
        self,
    ) -> None:
        self.assertEqual(
            self.product_map,
            self.compile_map,
            "FanPWM bundle must compose the IDENTICAL package set "
            "(same package keys, same repo-relative !include targets) as the "
            "native full-compile-validated compile-only skeleton "
            f"{FANPWM_NATIVE_COMPILE_ONLY_PRODUCT_YAML} "
            f"({FANPWM_NATIVE_COMPILE_EVIDENCE}); otherwise the recorded "
            "native full compile does not transfer to the bundle composition.",
        )

    def test_both_compose_canonical_fan_pwm_package(self) -> None:
        for label, mapping in (
            ("bundle", self.product_map),
            ("native compile-only", self.compile_map),
        ):
            self.assertIn(
                FANPWM_NATIVE_PACKAGE_REL,
                set(mapping.values()),
                f"the {label} FanPWM YAML must compose the native ESP32-S3 "
                f"GPIO package {FANPWM_NATIVE_PACKAGE_REL}",
            )

    def test_both_yamls_surface_same_config_string(self) -> None:
        # The product's text_sensor composition (incl. the config-string
        # template) now lives in the bundle the product shim pulls in.
        for path in (PWM_BUNDLE, self.compile_only_yaml):
            data = _load_yaml(path)
            sensors = data.get("text_sensor", []) or []
            lambdas = " ".join(
                str(s.get("lambda", "")) for s in sensors if isinstance(s, dict)
            )
            self.assertIn(
                PWM_CONFIG_STRING,
                lambdas,
                f"{path.name} must surface the {PWM_CONFIG_STRING!r} config "
                "string so the product and its validated compile-only "
                "skeleton agree on the config identity.",
            )

    def test_validated_composition_is_recorded_full_compile(self) -> None:
        doc = _load_json(COMPILE_ONLY_TARGETS)
        target = next(
            (
                t
                for t in doc.get("targets", [])
                if t.get("id") == FANPWM_NATIVE_COMPILE_ONLY_TARGET_ID
            ),
            None,
        )
        self.assertIsNotNone(target)
        self.assertEqual(
            target.get("compile_validation_status"),
            "validated-full-compile",
            "the native composition the migrated bundle mirrors must remain "
            f"validated-full-compile ({FANPWM_NATIVE_COMPILE_EVIDENCE}); "
            "SX1509-RECONCILE-001 relies on that recorded native full compile.",
        )
        self.assertFalse(
            target.get("rpm_supported", False),
            "the validated native composition must keep rpm_supported false.",
        )


class ReleaseOneRelayDacAndLedPostureTests(unittest.TestCase):
    """Release-One, LED preview, FanRelay, FanDAC, and FanTRIAC posture.

    Release-One and the LED preview stay untouched. The FanRelay / FanDAC
    siblings are pinned at their HW-RELEASE-001 posture (release-eligible
    preview status; experimental / preview channels; never stable), and
    FanTRIAC keeps its experimental-only lane.
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

    def test_relay_product_yaml_exists(self) -> None:
        path = REPO_ROOT / RELAY_PRODUCT_REL
        self.assertTrue(path.is_file(), f"missing {RELAY_PRODUCT_REL}")

    def test_dac_product_yaml_exists(self) -> None:
        path = REPO_ROOT / DAC_PRODUCT_REL
        self.assertTrue(path.is_file(), f"missing {DAC_PRODUCT_REL}")

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

    def test_dac_catalog_entry_is_preview_channel(self) -> None:
        # HW-RELEASE-001 promoted the FanDAC sibling by owner declaration:
        # status preview on the PREVIEW channel (never stable;
        # RELEASE-DAC-001 / FANDAC-I2C-ADDR-001 stay the stable blockers).
        entry = self._find(DAC_CONFIG_STRING)
        self.assertEqual(entry["status"], "preview")
        self.assertEqual(entry["channel"], "preview")
        self.assertTrue(entry["webflash_build_matrix"])
        self.assertEqual(
            entry["artifact_name"],
            f"Sense360-{DAC_CONFIG_STRING}-v{entry['version']}-preview.bin",
        )
        self.assertEqual(entry["product_yaml"], DAC_PRODUCT_REL)
        self.assertEqual(entry["hardware_status"], OWNER_DECLARED_HW_STATUS)

    def test_fantriac_catalog_entry_is_experimental_self_build(self) -> None:
        # TRIAC-COMMISSIONING-001 moved FanTRIAC into the experimental
        # self-build mains lane (status preview, channel experimental). This PR
        # (FanPWM readiness) does not change FanTRIAC; the preserved invariant
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
            "[Ceiling-POE-VentIQ-RoomIQ]; PRODUCT-PWM-001 does not add "
            "FanPWM to the Release-One required configs.",
        )


# MANUAL-FIRMWARE-CANDIDATE-001: the registered TOP-LEVEL FanPWM product
# compile-only target (distinct from the products/compile-only/ skeleton).
FANPWM_PRODUCT_COMPILE_ONLY_TARGET_ID = "ceiling-poe-fanpwm-product-compile-only"


class FanPwmManualFirmwareCandidateTests(unittest.TestCase):
    """MANUAL-FIRMWARE-CANDIDATE-001 evidence + HW-RELEASE-001 promotion.

    The full-compile evidence trail stands: the top-level product
    compile-only target is ``validated-full-compile`` with
    ``rpm_supported`` false, and the catalog notes keep the candidate
    record and its no-false-proof disclaimers. The former "no more than
    a manual candidate" pins (status hardware-pending, no wrapper, no
    artifact, no build row) were inverted by owner decision HW-RELEASE-001:
    the entry is now a release-eligible preview-channel config, still
    firmware-build proof only and never stable.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.targets = _load_json(COMPILE_ONLY_TARGETS).get("targets", [])
        cls.by_id = {t["id"]: t for t in cls.targets if t.get("id")}
        cls.entry = _catalog_entry_for(PWM_PRODUCT_REL)

    def _target(self) -> Dict[str, Any]:
        target = self.by_id.get(FANPWM_PRODUCT_COMPILE_ONLY_TARGET_ID)
        self.assertIsNotNone(
            target,
            "top-level FanPWM product compile-only target "
            f"{FANPWM_PRODUCT_COMPILE_ONLY_TARGET_ID!r} must be registered",
        )
        return target

    def test_top_level_target_points_at_product_yaml(self) -> None:
        self.assertEqual(self._target().get("product_yaml"), PWM_PRODUCT_REL)

    def test_top_level_target_is_validated_full_compile(self) -> None:
        self.assertEqual(
            self._target().get("compile_validation_status"),
            "validated-full-compile",
            "FanPWM top-level product compile-only target must be "
            "validated-full-compile — the full-compile evidence that makes "
            "FanPWM a manual / no-WebFlash firmware candidate",
        )

    def test_top_level_target_makes_no_rpm_claim(self) -> None:
        self.assertFalse(
            self._target().get("rpm_supported", False),
            "FanPWM top-level target must keep rpm_supported false",
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
            "not rpm support",
        ):
            self.assertIn(
                marker, notes, f"FanPWM notes must disclaim {marker!r}"
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
            f"Sense360-{PWM_CONFIG_STRING}-v{self.entry.get('version')}"
            f"-{self.entry.get('channel')}.bin",
        )

    def test_catalog_declares_webflash_wrapper(self) -> None:
        # Inverted from "no webflash_wrapper" by HW-RELEASE-001.
        self.assertEqual(self.entry.get("webflash_wrapper"), PWM_WRAPPER_REL)

    def test_webflash_wrapper_file_exists_and_is_thin(self) -> None:
        # Inverted from "no wrapper file" by HW-RELEASE-001: the wrapper
        # exists and is a thin packages-only re-export of the canonical
        # product YAML.
        wrapper = REPO_ROOT / PWM_WRAPPER_REL
        self.assertTrue(wrapper.is_file())
        data = _load_yaml(wrapper)
        self.assertEqual(set(data.keys()), {"packages"})
        self.assertIn(
            "../sense360-ceiling-poe-fanpwm.yaml",
            list((data.get("packages") or {}).values()),
        )

    def test_config_string_in_webflash_builds_preview_never_stable(
        self,
    ) -> None:
        # Inverted from "not in webflash-builds" by HW-RELEASE-001; the
        # preserved half is channel teeth: preview only, never stable.
        row = _builds_row_for(PWM_CONFIG_STRING)
        self.assertEqual(row.get("channel"), "preview")
        self.assertNotEqual(row.get("channel"), "stable")

    def test_config_string_not_in_release_one_required(self) -> None:
        compat = _load_json(WEBFLASH_COMPATIBILITY)
        self.assertNotIn(
            PWM_CONFIG_STRING,
            compat.get("release_one_required_configs", []) or [],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

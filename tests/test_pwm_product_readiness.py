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

The product intentionally has:

  * no WebFlash wrapper under ``products/webflash/``;
  * no ``webflash_build_matrix: true`` flip in
    ``config/product-catalog.json``;
  * no ``artifact_name`` declared;
  * no entry in ``config/webflash-builds.json``;
  * no entry in ``release_one_required_configs``;
  * no release artifact / tag / checksum / build-info manifest;
  * NO RPM support and NO ``pulse_counter`` (an SX1509 expander pin is
    compile-proven unable to back an ESPHome ``pulse_counter``);
  * ``TachIO`` / ``GPIO16`` reserved / pending;
  * an explicit full-compile-validated caveat (run 26414398902 /
    validated-full-compile), PWM-polarity, current / thermal-envelope,
    no-RPM, and no-WebFlash / no-release / no-compliance /
    not-hardware-stable caveat wording in the product YAML header.

These tests pin the structural invariants so a future regression cannot
silently promote the FanPWM product onto a WebFlash-shippable surface,
add an RPM claim, or strip the required caveats without an explicit
WEBFLASH-PWM-001 / RELEASE-PWM-001 slice.

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

# The FW-COMPILE-PWM-001 compile-only skeleton must remain unchanged.
COMPILE_ONLY_TARGETS = REPO_ROOT / "config" / "compile-only-targets.json"
FANPWM_COMPILE_ONLY_TARGET_ID = "ceiling-poe-fanpwm-compile-only"
FANPWM_COMPILE_ONLY_PRODUCT_YAML = "products/compile-only/ceiling-poe-fanpwm.yaml"

# Full-compile evidence the FanPWM lane references.
FANPWM_FULL_COMPILE_RUN_ID = "26414398902"


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
        self.assertIn(
            "packages/expansions/fan_pwm.yaml",
            self.text,
            "FanPWM product YAML must !include "
            "packages/expansions/fan_pwm.yaml so the PWM-drive outputs are "
            "composed through the canonical PWM-drive-only FanPWM package.",
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

    def test_underlying_package_has_no_pulse_counter(self) -> None:
        pkg = REPO_ROOT / "packages" / "expansions" / "fan_pwm.yaml"
        for line in _active_lines(pkg.read_text()):
            self.assertNotIn(
                "pulse_counter",
                line,
                "packages/expansions/fan_pwm.yaml must not use pulse_counter "
                f"on any active line. Line: {line!r}",
            )


class PwmProductWebFlashExposureGuardsTests(unittest.TestCase):
    """The FanPWM product is NOT WebFlash-exposed.

    PRODUCT-PWM-001 explicitly does not add a WebFlash wrapper, a catalog
    ``webflash_build_matrix: true`` flip, an ``artifact_name``, a
    ``config/webflash-builds.json`` entry, or a release artifact.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.entry = _catalog_entry_for(PWM_PRODUCT_REL)
        cls.builds_doc = _load_json(WEBFLASH_BUILDS)
        cls.compat = _load_json(WEBFLASH_COMPATIBILITY)

    def test_catalog_entry_webflash_build_matrix_is_false(self) -> None:
        self.assertEqual(
            self.entry.get("webflash_build_matrix"),
            False,
            "FanPWM product catalog entry must set "
            "webflash_build_matrix: false — PRODUCT-PWM-001 does not "
            "advance WEBFLASH-PWM-001 or RELEASE-PWM-001.",
        )

    def test_catalog_entry_has_no_artifact_name(self) -> None:
        self.assertNotIn(
            "artifact_name",
            self.entry,
            "FanPWM product catalog entry must NOT declare artifact_name "
            "— no release artifact is built by PRODUCT-PWM-001.",
        )

    def test_catalog_entry_has_no_webflash_wrapper(self) -> None:
        self.assertNotIn(
            "webflash_wrapper",
            self.entry,
            "FanPWM product catalog entry must NOT declare "
            "webflash_wrapper — PRODUCT-PWM-001 does not add a WebFlash "
            "wrapper under products/webflash/.",
        )

    def test_catalog_entry_status_is_not_release_eligible(self) -> None:
        self.assertNotIn(
            self.entry.get("status"),
            {"production", "preview"},
            f"FanPWM product catalog entry must not be production or "
            f"preview — those statuses authorise WebFlash exposure. "
            f"Got status={self.entry.get('status')!r}.",
        )

    def test_catalog_entry_status_is_hardware_pending(self) -> None:
        self.assertEqual(
            self.entry.get("status"),
            "hardware-pending",
            "FanPWM product catalog entry must be status: hardware-pending "
            "(bench gates open; matches the FanDAC / FanRelay precedent).",
        )

    def test_no_fanpwm_webflash_wrapper_file(self) -> None:
        if not WEBFLASH_WRAPPER_DIR.is_dir():
            return
        offenders = []
        for path in WEBFLASH_WRAPPER_DIR.glob("*.yaml"):
            name = path.name.lower()
            if "fanpwm" in name or "fan-pwm" in name or "fan_pwm" in name:
                offenders.append(path.relative_to(REPO_ROOT).as_posix())
        self.assertEqual(
            offenders,
            [],
            f"PRODUCT-PWM-001 must NOT add any FanPWM WebFlash wrapper "
            f"under products/webflash/ — that work belongs to "
            f"WEBFLASH-PWM-001 (not landed). Offending paths: {offenders!r}",
        )

    def test_pwm_config_string_not_in_webflash_builds(self) -> None:
        for entry in self.builds_doc.get("builds", []) or []:
            self.assertNotEqual(
                entry.get("config_string"),
                PWM_CONFIG_STRING,
                f"config/webflash-builds.json must not contain "
                f"{PWM_CONFIG_STRING!r} — PRODUCT-PWM-001 does not add a "
                f"build-matrix entry. RELEASE-PWM-001 owns the FanPWM "
                f"build entry.",
            )

    def test_fanpwm_token_not_in_webflash_builds_json(self) -> None:
        text = WEBFLASH_BUILDS.read_text()
        self.assertNotIn(
            "FanPWM",
            text,
            "config/webflash-builds.json must not contain the FanPWM "
            "token at all — PRODUCT-PWM-001 does not advance "
            "WEBFLASH-PWM-001 or RELEASE-PWM-001.",
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

    def test_carries_pwm_drive_only_wording(self) -> None:
        self._assert_phrase(
            "pwm-drive-only",
            "PWM-drive-only scope naming",
        )

    def test_carries_full_compile_validated_caveat(self) -> None:
        self._assert_phrase(
            "full esphome compile",
            "full ESPHome compile caveat",
        )
        self._assert_phrase(
            "compile_mode=full",
            "the compile_mode=full run that validated it",
        )
        self._assert_phrase(
            "validated-full-compile",
            "compile_validation_status: validated-full-compile now stands",
        )
        self._assert_phrase(
            FANPWM_FULL_COMPILE_RUN_ID,
            "the full-compile run id that validated the FanPWM target",
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

    def test_states_no_pulse_counter(self) -> None:
        self._assert_phrase(
            "pulse_counter",
            "no-pulse_counter caveat (SX1509 pin cannot back one)",
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
    """FW-COMPILE-PWM-PRODUCT-001: the product YAML composes the SAME
    validated package set as the full-compile-validated compile-only target.

    ``products/compile-only/ceiling-poe-fanpwm.yaml`` is the skeleton whose
    FULL ESPHome compile passed in run 26414398902 (``compile_mode=full``;
    FW-COMPILE-PWM-RESULT-001 / PR #592). PRODUCT-PWM-001 then added the
    normal product YAML. These tests pin that the two YAMLs compose the
    identical Core ceiling + PoE PSU + base/health + FanPWM package set (same
    package keys, same repo-relative ``!include`` targets), so the recorded
    full compile transfers to the product YAML's composition. The two differ
    only in substitutions / identification ``text_sensor`` wording, never in
    which packages are composed.

    Live ``esphome config products/sense360-ceiling-poe-fanpwm.yaml`` is NOT
    asserted here (ESPHome is not assumed present); the structural parity to
    the already-validated compile-only skeleton is what these tests pin. See
    docs/product-readiness-matrix.md §FanPWM / S360-311
    FW-COMPILE-PWM-PRODUCT-001 addendum for the conservative status and the
    exact manual / CI command that still owns the live product-config run.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.compile_only_yaml = REPO_ROOT / FANPWM_COMPILE_ONLY_PRODUCT_YAML
        cls.product_map = _package_include_map(PWM_BUNDLE)
        cls.compile_map = _package_include_map(cls.compile_only_yaml)

    def test_compile_only_skeleton_file_exists(self) -> None:
        self.assertTrue(
            self.compile_only_yaml.is_file(),
            f"the full-compile-validated compile-only skeleton "
            f"{FANPWM_COMPILE_ONLY_PRODUCT_YAML} must exist for the product "
            "YAML to inherit its validated composition",
        )

    def test_product_and_compile_only_compose_identical_package_set(
        self,
    ) -> None:
        self.assertEqual(
            self.product_map,
            self.compile_map,
            "FanPWM product YAML must compose the IDENTICAL package set "
            "(same package keys, same repo-relative !include targets) as the "
            "full-compile-validated compile-only skeleton "
            f"{FANPWM_COMPILE_ONLY_PRODUCT_YAML} (run "
            f"{FANPWM_FULL_COMPILE_RUN_ID}); otherwise the recorded full "
            "compile does not transfer to the product composition.",
        )

    def test_both_compose_canonical_fan_pwm_package(self) -> None:
        for label, mapping in (
            ("product", self.product_map),
            ("compile-only", self.compile_map),
        ):
            self.assertIn(
                "packages/expansions/fan_pwm.yaml",
                set(mapping.values()),
                f"the {label} FanPWM YAML must compose the canonical "
                "PWM-drive-only package packages/expansions/fan_pwm.yaml",
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
                if t.get("id") == FANPWM_COMPILE_ONLY_TARGET_ID
            ),
            None,
        )
        self.assertIsNotNone(target)
        self.assertEqual(
            target.get("compile_validation_status"),
            "validated-full-compile",
            "the composition the product YAML mirrors must remain "
            f"validated-full-compile (run {FANPWM_FULL_COMPILE_RUN_ID}); "
            "FW-COMPILE-PWM-PRODUCT-001 relies on that recorded full compile.",
        )
        self.assertFalse(
            target.get("rpm_supported", False),
            "the validated composition must keep rpm_supported false.",
        )


class ReleaseOneRelayDacAndLedUnchangedTests(unittest.TestCase):
    """Release-One, LED preview, FanRelay, FanDAC, and FanTRIAC unchanged.

    PRODUCT-PWM-001 must not touch the Release-One canonical YAML, the LED
    preview canonical YAML, the FanRelay / FanDAC siblings, or their
    catalog entries.
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

    def test_dac_catalog_entry_remains_hardware_pending(self) -> None:
        entry = self._find(DAC_CONFIG_STRING)
        self.assertEqual(entry["status"], "hardware-pending")
        self.assertFalse(entry["webflash_build_matrix"])
        self.assertNotIn("artifact_name", entry)
        self.assertEqual(entry["product_yaml"], DAC_PRODUCT_REL)

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
            "[Ceiling-POE-VentIQ-RoomIQ]; PRODUCT-PWM-001 does not add "
            "FanPWM to the Release-One required configs.",
        )


# MANUAL-FIRMWARE-CANDIDATE-001: the registered TOP-LEVEL FanPWM product
# compile-only target (distinct from the products/compile-only/ skeleton).
FANPWM_PRODUCT_COMPILE_ONLY_TARGET_ID = "ceiling-poe-fanpwm-product-compile-only"


class FanPwmManualFirmwareCandidateTests(unittest.TestCase):
    """MANUAL-FIRMWARE-CANDIDATE-001: FanPWM is a manual / no-WebFlash
    firmware candidate — present, structurally validated, full-compile
    validated — but no more than that.

    Pins: the top-level product compile-only target is
    ``validated-full-compile``; the catalog notes record the candidate
    status and disclaim release / WebFlash / hardware-stable / compliance /
    RPM readiness; ``webflash_build_matrix`` stays false; no
    ``artifact_name`` / ``webflash_wrapper`` / WebFlash wrapper file / build
    entry is added.
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
                if "fanpwm" in p.name.lower()
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
        self.assertNotIn(PWM_CONFIG_STRING, configs)

    def test_config_string_not_in_release_one_required(self) -> None:
        compat = _load_json(WEBFLASH_COMPATIBILITY)
        self.assertNotIn(
            PWM_CONFIG_STRING,
            compat.get("release_one_required_configs", []) or [],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

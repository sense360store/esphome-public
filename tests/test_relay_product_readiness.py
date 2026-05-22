#!/usr/bin/env python3
"""PRODUCT-RELAY-001 invariants for the FanRelay product YAML.

PRODUCT-RELAY-001 adds a single canonical FanRelay product YAML
(``products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml``) as an
**advanced / manual-warning-only** sibling of Release-One. The product
intentionally has:

  * no WebFlash wrapper under ``products/webflash/``;
  * no ``webflash_build_matrix: true`` flip in
    ``config/product-catalog.json``;
  * no ``artifact_name`` declared;
  * no entry in ``config/webflash-builds.json``;
  * no entry in ``release_one_required_configs``;
  * no release artifact / tag / checksum / build-info manifest;
  * explicit advanced / manual-warning + installation / safety +
    competent-person caveat wording in the product YAML header.

These tests pin the structural invariants so a future regression cannot
silently promote the FanRelay product onto a WebFlash-shippable surface
without an explicit WEBFLASH-RELAY-001 / RELEASE-RELAY-001 slice.

Run with::

    python3 tests/test_relay_product_readiness.py

or::

    python3 -m unittest tests.test_relay_product_readiness -v
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from typing import Any, Dict, Iterable, List

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent

RELAY_PRODUCT_YAML = (
    REPO_ROOT
    / "products"
    / "sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml"
)
RELAY_PRODUCT_REL = "products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml"
RELAY_CONFIG_STRING = "Ceiling-POE-VentIQ-FanRelay-RoomIQ"

RELEASE_ONE_PRODUCT_REL = "products/sense360-ceiling-poe-ventiq-roomiq.yaml"
RELEASE_ONE_CONFIG_STRING = "Ceiling-POE-VentIQ-RoomIQ"
LED_PREVIEW_PRODUCT_REL = "products/sense360-ceiling-poe-ventiq-roomiq-led.yaml"
LED_PREVIEW_CONFIG_STRING = "Ceiling-POE-VentIQ-RoomIQ-LED"
FANTRIAC_BLOCKED_CONFIG_STRING = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"

PRODUCT_CATALOG = REPO_ROOT / "config" / "product-catalog.json"
WEBFLASH_BUILDS = REPO_ROOT / "config" / "webflash-builds.json"
WEBFLASH_COMPATIBILITY = REPO_ROOT / "config" / "webflash-compatibility.json"
WEBFLASH_WRAPPER_DIR = REPO_ROOT / "products" / "webflash"


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
        f"config/product-catalog.json (PRODUCT-RELAY-001 requires a "
        f"non-WebFlash row)"
    )


class RelayProductYamlExistsTests(unittest.TestCase):
    """The PRODUCT-RELAY-001 product YAML exists at the canonical path."""

    def test_product_yaml_file_exists(self) -> None:
        self.assertTrue(
            RELAY_PRODUCT_YAML.is_file(),
            f"PRODUCT-RELAY-001 must add the FanRelay product YAML at "
            f"{RELAY_PRODUCT_YAML} (canonical config-string order: "
            f"{RELAY_CONFIG_STRING})",
        )

    def test_product_yaml_parses_as_yaml(self) -> None:
        data = _load_yaml(RELAY_PRODUCT_YAML)
        self.assertIsInstance(
            data,
            dict,
            "FanRelay product YAML must parse as a YAML mapping",
        )
        for key in ("substitutions", "packages"):
            self.assertIn(
                key,
                data,
                f"FanRelay product YAML must declare a top-level "
                f"`{key}:` block",
            )

    def test_product_yaml_is_enumerated_in_catalog(self) -> None:
        entry = _catalog_entry_for(RELAY_PRODUCT_REL)
        self.assertEqual(entry.get("config_string"), RELAY_CONFIG_STRING)


class RelayProductPackageCompositionTests(unittest.TestCase):
    """The product composes the FanRelay package + the Release-One base stack."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.data = _load_yaml(RELAY_PRODUCT_YAML)
        cls.packages = cls.data.get("packages", {}) or {}

    def test_packages_block_is_a_mapping(self) -> None:
        self.assertIsInstance(
            self.packages,
            dict,
            "FanRelay product YAML `packages:` block must be a mapping",
        )

    def test_includes_fan_relay_package(self) -> None:
        text = RELAY_PRODUCT_YAML.read_text()
        self.assertIn(
            "packages/expansions/fan_relay.yaml",
            text,
            "FanRelay product YAML must !include "
            "packages/expansions/fan_relay.yaml so the relay output is "
            "composed through the FanRelay package abstraction.",
        )

    def test_includes_core_ceiling_package(self) -> None:
        text = RELAY_PRODUCT_YAML.read_text()
        self.assertIn(
            "packages/hardware/sense360_core_ceiling.yaml",
            text,
            "FanRelay product YAML must !include the Core ceiling "
            "abstract package so `${relay_pin}` resolves to the "
            "schematic-correct GPIO3 bound by CORE-ABSTRACT-BUS-001A.",
        )

    def test_includes_poe_power_package(self) -> None:
        text = RELAY_PRODUCT_YAML.read_text()
        self.assertIn(
            "packages/hardware/power_poe.yaml",
            text,
            "FanRelay product YAML must !include the PoE power package "
            "to match the Release-One PoE base stack.",
        )

    def test_includes_ventiq_module(self) -> None:
        text = RELAY_PRODUCT_YAML.read_text()
        self.assertIn(
            "packages/expansions/airiq_bathroom_base.yaml",
            text,
            "FanRelay product YAML must !include the VentIQ "
            "(airiq_bathroom_base) module to match the Release-One base "
            "stack.",
        )

    def test_includes_roomiq_packages(self) -> None:
        text = RELAY_PRODUCT_YAML.read_text()
        for required in (
            "packages/expansions/comfort_ceiling.yaml",
            "packages/expansions/presence_ceiling.yaml",
        ):
            self.assertIn(
                required,
                text,
                f"FanRelay product YAML must !include {required} to "
                f"match the Release-One RoomIQ (comfort + presence) "
                f"base stack.",
            )

    def test_does_not_include_led_ring_package(self) -> None:
        text = RELAY_PRODUCT_YAML.read_text()
        self.assertNotIn(
            "packages/hardware/led_ring_ceiling.yaml",
            text,
            "FanRelay product YAML must NOT !include the LED ceiling "
            "package; LED is owned by the separate "
            "products/sense360-ceiling-poe-ventiq-roomiq-led.yaml "
            "sibling and PRODUCT-RELAY-001 does not bundle LED.",
        )

    def test_does_not_include_fan_triac_package(self) -> None:
        text = RELAY_PRODUCT_YAML.read_text()
        self.assertNotIn(
            "packages/expansions/fan_triac.yaml",
            text,
            "FanRelay product YAML must NOT !include the FanTRIAC "
            "package; FanTRIAC stays blocked under HW-005 and is owned "
            "by the separate "
            "products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml "
            "blocked reference.",
        )


class RelayProductGpio3Tests(unittest.TestCase):
    """The FanRelay product MUST NOT hard-code ``GPIO3`` (or any GPIO).

    The Relay net is exposed through the substitution layer:
    ``packages/hardware/sense360_core_ceiling.yaml`` binds
    ``relay_pin: GPIO3`` (schematic-correct Relay net per S360-100-R4
    IO3 after CORE-ABSTRACT-BUS-001A / PR #558);
    ``packages/expansions/fan_relay.yaml`` declares
    ``fan_relay_pin: ${relay_pin}``; the product YAML inherits both
    through ``!include`` without naming GPIO3 directly.
    """

    def test_product_yaml_does_not_hardcode_gpio3(self) -> None:
        text = RELAY_PRODUCT_YAML.read_text()
        for line in _active_lines(text):
            self.assertNotIn(
                "GPIO3",
                line,
                f"FanRelay product YAML must NOT hard-code GPIO3 on an "
                f"active (non-comment) line. The Relay net flows through "
                f"the ${{relay_pin}} → ${{fan_relay_pin}} substitution "
                f"chain (Core abstract package binds GPIO3 post-"
                f"CORE-ABSTRACT-BUS-001A / PR #558). Offending line: "
                f"{line!r}",
            )

    def test_product_yaml_does_not_hardcode_any_gpio(self) -> None:
        text = RELAY_PRODUCT_YAML.read_text()
        pattern = re.compile(r"\bGPIO\d+\b")
        for line in _active_lines(text):
            match = pattern.search(line)
            self.assertIsNone(
                match,
                f"FanRelay product YAML must not name any GPIO on an "
                f"active (non-comment) line; pin bindings flow through "
                f"package substitutions. Offending line: {line!r}",
            )


class RelayProductWebFlashExposureGuardsTests(unittest.TestCase):
    """The FanRelay product is NOT WebFlash-exposed.

    PRODUCT-RELAY-001 explicitly does not add a WebFlash wrapper, a
    catalog ``webflash_build_matrix: true`` flip, an ``artifact_name``,
    a ``config/webflash-builds.json`` entry, or a release artifact.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.entry = _catalog_entry_for(RELAY_PRODUCT_REL)
        cls.builds_doc = _load_json(WEBFLASH_BUILDS)
        cls.compat = _load_json(WEBFLASH_COMPATIBILITY)

    def test_catalog_entry_webflash_build_matrix_is_false(self) -> None:
        self.assertEqual(
            self.entry.get("webflash_build_matrix"),
            False,
            "FanRelay product catalog entry must set "
            "webflash_build_matrix: false — PRODUCT-RELAY-001 does not "
            "advance WEBFLASH-RELAY-001 or RELEASE-RELAY-001.",
        )

    def test_catalog_entry_has_no_artifact_name(self) -> None:
        self.assertNotIn(
            "artifact_name",
            self.entry,
            "FanRelay product catalog entry must NOT declare "
            "artifact_name — no release artifact is built by "
            "PRODUCT-RELAY-001.",
        )

    def test_catalog_entry_has_no_webflash_wrapper(self) -> None:
        self.assertNotIn(
            "webflash_wrapper",
            self.entry,
            "FanRelay product catalog entry must NOT declare "
            "webflash_wrapper — PRODUCT-RELAY-001 does not add a "
            "WebFlash wrapper under products/webflash/.",
        )

    def test_no_fan_relay_webflash_wrapper_file(self) -> None:
        if not WEBFLASH_WRAPPER_DIR.is_dir():
            return
        offenders = []
        for path in WEBFLASH_WRAPPER_DIR.glob("*.yaml"):
            name = path.name.lower()
            if "fanrelay" in name or "fan-relay" in name or "fan_relay" in name:
                offenders.append(path.relative_to(REPO_ROOT).as_posix())
        self.assertEqual(
            offenders,
            [],
            f"PRODUCT-RELAY-001 must NOT add any FanRelay WebFlash "
            f"wrapper under products/webflash/ — that work belongs to "
            f"WEBFLASH-RELAY-001 (not landed). Offending paths: "
            f"{offenders!r}",
        )

    def test_relay_config_string_not_in_webflash_builds(self) -> None:
        for entry in self.builds_doc.get("builds", []) or []:
            self.assertNotEqual(
                entry.get("config_string"),
                RELAY_CONFIG_STRING,
                f"config/webflash-builds.json must not contain "
                f"{RELAY_CONFIG_STRING!r} — PRODUCT-RELAY-001 does not "
                f"add a build-matrix entry. RELEASE-RELAY-001 owns the "
                f"FanRelay build entry.",
            )

    def test_fan_relay_token_not_in_webflash_builds_json(self) -> None:
        text = WEBFLASH_BUILDS.read_text()
        self.assertNotIn(
            "FanRelay",
            text,
            "config/webflash-builds.json must not contain the FanRelay "
            "token at all — PRODUCT-RELAY-001 does not advance "
            "WEBFLASH-RELAY-001 or RELEASE-RELAY-001.",
        )

    def test_relay_config_string_not_in_release_one_required_configs(
        self,
    ) -> None:
        required = self.compat.get("release_one_required_configs", []) or []
        self.assertNotIn(
            RELAY_CONFIG_STRING,
            required,
            f"release_one_required_configs in "
            f"config/webflash-compatibility.json must not contain "
            f"{RELAY_CONFIG_STRING!r} — PRODUCT-RELAY-001 does not "
            f"promote FanRelay into Release-One required configs.",
        )

    def test_product_yaml_does_not_declare_webflash_build_matrix_true(
        self,
    ) -> None:
        text = RELAY_PRODUCT_YAML.read_text()
        for line in _active_lines(text):
            self.assertNotIn(
                "webflash_build_matrix",
                line,
                f"FanRelay product YAML must not declare a "
                f"`webflash_build_matrix` field — that field belongs to "
                f"the catalog entry only and must remain false. "
                f"Offending line: {line!r}",
            )

    def test_product_yaml_does_not_declare_artifact_name(self) -> None:
        text = RELAY_PRODUCT_YAML.read_text()
        for line in _active_lines(text):
            self.assertNotIn(
                "artifact_name",
                line,
                f"FanRelay product YAML must not declare an "
                f"`artifact_name` field — no release artifact is built "
                f"by PRODUCT-RELAY-001. Offending line: {line!r}",
            )

    def test_catalog_entry_status_is_not_release_eligible(self) -> None:
        # Production / preview entries are WebFlash-eligible (flipped on
        # in tests/test_product_catalog.py WEBFLASH_ELIGIBLE_STATUSES);
        # the FanRelay entry must stay outside that set so the product
        # remains WebFlash-blocked.
        self.assertNotIn(
            self.entry.get("status"),
            {"production", "preview"},
            f"FanRelay product catalog entry must not be production or "
            f"preview — those statuses authorise WebFlash exposure. "
            f"Got status={self.entry.get('status')!r}.",
        )


class RelayProductAdvancedManualWarningWordingTests(unittest.TestCase):
    """The FanRelay product YAML carries advanced / manual-warning wording.

    The PRODUCT-RELAY-001 readiness refresh
    (``docs/product-readiness-matrix.md`` §FanRelay / S360-310)
    requires explicit advanced / manual-warning + installation / safety
    + competent-person caveat wording in the product YAML itself. These
    tests pin that wording so a later refactor cannot silently strip it.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = RELAY_PRODUCT_YAML.read_text()
        cls.lowered = cls.text.lower()

    def _assert_phrase(self, phrase: str, hint: str) -> None:
        self.assertIn(
            phrase.lower(),
            self.lowered,
            f"FanRelay product YAML must contain wording matching "
            f"{phrase!r} ({hint}). The PRODUCT-RELAY-001 readiness "
            f"refresh requires the product YAML to carry explicit "
            f"advanced / manual-warning + installation / safety + "
            f"competent-person caveat text.",
        )

    def test_carries_advanced_manual_warning_wording(self) -> None:
        self._assert_phrase(
            "advanced / manual-warning",
            "advanced / manual-warning posture",
        )

    def test_carries_competent_person_caveat(self) -> None:
        self._assert_phrase(
            "competent person",
            "competent-person caveat per applicable jurisdiction",
        )

    def test_carries_mains_switching_wording(self) -> None:
        # Confirm the YAML names the mains-switching path (so the
        # installation hazard is visible to a reader, not just implied).
        self._assert_phrase(
            "mains",
            "mains switching path",
        )

    def test_carries_bathroom_fan_control_wording(self) -> None:
        self._assert_phrase(
            "fan-control",
            "bathroom fan-control intended use",
        )

    def test_states_not_webflash_exposed(self) -> None:
        self._assert_phrase(
            "not webflash",
            "explicit not-WebFlash-exposed statement",
        )

    def test_states_not_default_kit(self) -> None:
        self._assert_phrase(
            "not a default kit",
            "explicit not-default-kit statement",
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


class RelayKitIntentRemainsBlockedTests(unittest.TestCase):
    """``S360-KIT-BATH-RELAY`` stays future-expansion / hardware-pending.

    PRODUCT-RELAY-001 must not promote the Relay bathroom kit. The
    default sellable bathroom kit stays ``S360-KIT-BATH-POE`` mapped to
    Release-One.
    """

    @classmethod
    def setUpClass(cls) -> None:
        path = REPO_ROOT / "config" / "kit-intent-matrix.json"
        cls.doc = _load_json(path)
        cls.by_id = {kit["kit_id"]: kit for kit in cls.doc.get("kits", [])}

    def test_relay_kit_is_future_expansion(self) -> None:
        kit = self.by_id.get("S360-KIT-BATH-RELAY")
        self.assertIsNotNone(kit, "S360-KIT-BATH-RELAY must exist")
        self.assertEqual(kit["tier"], "future-expansion")

    def test_relay_kit_lifecycle_is_hardware_pending(self) -> None:
        kit = self.by_id["S360-KIT-BATH-RELAY"]
        self.assertEqual(kit["lifecycle_status"], "hardware-pending")

    def test_relay_kit_is_not_webflash_exposed(self) -> None:
        kit = self.by_id["S360-KIT-BATH-RELAY"]
        self.assertFalse(
            kit["webflash_exposure_allowed_now"],
            "S360-KIT-BATH-RELAY must not be webflash_exposure_allowed_now",
        )

    def test_relay_kit_is_not_stable_ready(self) -> None:
        kit = self.by_id["S360-KIT-BATH-RELAY"]
        self.assertFalse(
            kit["stable_ready_now"],
            "S360-KIT-BATH-RELAY must not be stable_ready_now",
        )

    def test_default_sellable_bathroom_kit_is_release_one(self) -> None:
        kit = self.by_id.get("S360-KIT-BATH-POE")
        self.assertIsNotNone(kit, "S360-KIT-BATH-POE must exist")
        self.assertEqual(kit["default_config_string"], RELEASE_ONE_CONFIG_STRING)
        self.assertEqual(kit["tier"], "ready-kit")
        self.assertEqual(kit["lifecycle_status"], "production")


class ReleaseOneAndLedPreviewUnchangedTests(unittest.TestCase):
    """Release-One and the LED preview product YAMLs / catalog entries are unchanged.

    PRODUCT-RELAY-001 must not touch the Release-One canonical YAML, the
    LED preview canonical YAML, or their catalog entries.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = _load_json(PRODUCT_CATALOG)

    def test_release_one_product_yaml_exists(self) -> None:
        path = REPO_ROOT / RELEASE_ONE_PRODUCT_REL
        self.assertTrue(path.is_file(), f"missing {RELEASE_ONE_PRODUCT_REL}")

    def test_led_preview_product_yaml_exists(self) -> None:
        path = REPO_ROOT / LED_PREVIEW_PRODUCT_REL
        self.assertTrue(path.is_file(), f"missing {LED_PREVIEW_PRODUCT_REL}")

    def _find(self, cs: str) -> Dict[str, Any]:
        for entry in self.catalog.get("products", []):
            if entry.get("config_string") == cs:
                return entry
        raise AssertionError(f"no catalog entry for {cs!r}")

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
        self.assertEqual(entry["version"], "1.0.0")
        self.assertEqual(
            entry["artifact_name"],
            "Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin",
        )
        self.assertTrue(entry["webflash_build_matrix"])
        self.assertEqual(entry["product_yaml"], LED_PREVIEW_PRODUCT_REL)

    def test_fantriac_catalog_entry_remains_blocked(self) -> None:
        entry = self._find(FANTRIAC_BLOCKED_CONFIG_STRING)
        self.assertEqual(entry["status"], "blocked")
        self.assertEqual(entry["blocker"], "HW-005")
        self.assertFalse(entry["webflash_build_matrix"])

    def test_release_one_required_configs_unchanged(self) -> None:
        compat = _load_json(WEBFLASH_COMPATIBILITY)
        self.assertEqual(
            compat.get("release_one_required_configs"),
            [RELEASE_ONE_CONFIG_STRING],
            "release_one_required_configs must remain "
            "[Ceiling-POE-VentIQ-RoomIQ]; PRODUCT-RELAY-001 does not "
            "add FanRelay to the Release-One required configs.",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

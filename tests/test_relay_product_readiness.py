#!/usr/bin/env python3
"""PRODUCT-RELAY-001 invariants for the FanRelay product YAML.

PRODUCT-RELAY-001 added a single canonical FanRelay product YAML
(``products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml``) as an
**advanced / manual-warning-only** sibling of Release-One.

HW-RELEASE-001 (docs/hw-release-001.md, owner decision of record,
2026-07-09) retired the bench-proof documentation requirement as a
release gate; hardware readiness is declared by the owner directly.
Under that decision the FanRelay product is now a release-eligible
config on the EXPERIMENTAL channel only (mains-adjacent contact
switching, COMPLIANCE-001 lane posture):

  * a thin packages-only WebFlash wrapper under ``products/webflash/``
    re-exporting the canonical product YAML;
  * ``status: preview`` + ``webflash_build_matrix: true`` +
    ``artifact_name`` + ``webflash_wrapper`` in
    ``config/product-catalog.json`` (hardware_status
    ``owner-declared-bench-working-hw-release-001``);
  * a ``config/webflash-builds.json`` row on the EXPERIMENTAL channel
    (release_state metadata-ready-unpublished — metadata only, no
    binary / Release / tag / manifest is cut).

Unchanged truths these tests keep pinning:

  * fan configs are NEVER on the stable channel — FanRelay rows are
    ``experimental`` exactly, never ``stable``; RELEASE-RELAY-001
    remains the STABLE blocker;
  * still NO entry in ``release_one_required_configs``; the builds-row
    ``commercial_posture`` keeps buyable / recommended /
    customer_default / stable false;
  * the advanced / manual-warning + installation / safety +
    competent-person caveat wording stays in the product YAML;
  * promotion is firmware-build proof only under owner declaration —
    no hardware / bench / compliance / safety /
    commercial-availability claim.

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
from typing import Any, Dict, List

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent

RELAY_PRODUCT_YAML = (
    REPO_ROOT
    / "products"
    / "sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml"
)
RELAY_PRODUCT_REL = "products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml"
# The product YAML is now a thin compat shim; its full composition/substitution
# content lives in the bundle. Content reads must target the bundle.
RELAY_BUNDLE = (
    REPO_ROOT / "products" / "bundles"
    / "ceiling-poe-ventiq-fanrelay-roomiq.yaml"
)
RELAY_CONFIG_STRING = "Ceiling-POE-VentIQ-FanRelay-RoomIQ"
# HW-RELEASE-001: the release-gate WebFlash wrapper now exists.
RELAY_WRAPPER_REL = "products/webflash/ceiling-poe-ventiq-fanrelay-roomiq.yaml"
# HW-RELEASE-001 owner declaration marker recorded in the catalog.
OWNER_DECLARED_HW_STATUS = "owner-declared-bench-working-hw-release-001"

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


def _builds_row_for(config_string: str) -> Dict[str, Any]:
    catalog = _load_json(WEBFLASH_BUILDS)
    for row in catalog.get("builds", []) or []:
        if row.get("config_string") == config_string:
            return row
    raise AssertionError(
        f"no config/webflash-builds.json row for {config_string!r} — "
        f"HW-RELEASE-001 declares this config release-eligible"
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
        data = _load_yaml(RELAY_BUNDLE)
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
        cls.data = _load_yaml(RELAY_BUNDLE)
        cls.packages = cls.data.get("packages", {}) or {}

    def test_packages_block_is_a_mapping(self) -> None:
        self.assertIsInstance(
            self.packages,
            dict,
            "FanRelay product YAML `packages:` block must be a mapping",
        )

    def test_includes_fan_relay_package(self) -> None:
        text = RELAY_BUNDLE.read_text()
        self.assertIn(
            "packages/expansions/fan_relay.yaml",
            text,
            "FanRelay product YAML must !include "
            "packages/expansions/fan_relay.yaml so the relay output is "
            "composed through the FanRelay package abstraction.",
        )

    def test_includes_core_ceiling_package(self) -> None:
        text = RELAY_BUNDLE.read_text()
        self.assertIn(
            "packages/hardware/sense360_core_ceiling.yaml",
            text,
            "FanRelay product YAML must !include the Core ceiling "
            "abstract package so `${relay_pin}` resolves to the "
            "schematic-correct GPIO3 bound by CORE-ABSTRACT-BUS-001A.",
        )

    def test_includes_poe_power_package(self) -> None:
        text = RELAY_BUNDLE.read_text()
        self.assertIn(
            "packages/hardware/power_poe.yaml",
            text,
            "FanRelay product YAML must !include the PoE power package "
            "to match the Release-One PoE base stack.",
        )

    def test_includes_ventiq_module(self) -> None:
        text = RELAY_BUNDLE.read_text()
        self.assertIn(
            "packages/expansions/airiq_bathroom_base.yaml",
            text,
            "FanRelay product YAML must !include the VentIQ "
            "(airiq_bathroom_base) module to match the Release-One base "
            "stack.",
        )

    def test_includes_roomiq_packages(self) -> None:
        text = RELAY_BUNDLE.read_text()
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
        text = RELAY_BUNDLE.read_text()
        self.assertNotIn(
            "packages/hardware/led_ring_ceiling.yaml",
            text,
            "FanRelay product YAML must NOT !include the LED ceiling "
            "package; LED is owned by the separate "
            "products/sense360-ceiling-poe-ventiq-roomiq-led.yaml "
            "sibling and PRODUCT-RELAY-001 does not bundle LED.",
        )

    def test_does_not_include_fan_triac_package(self) -> None:
        text = RELAY_BUNDLE.read_text()
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
        text = RELAY_BUNDLE.read_text()
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
        text = RELAY_BUNDLE.read_text()
        pattern = re.compile(r"\bGPIO\d+\b")
        for line in _active_lines(text):
            match = pattern.search(line)
            self.assertIsNone(
                match,
                f"FanRelay product YAML must not name any GPIO on an "
                f"active (non-comment) line; pin bindings flow through "
                f"package substitutions. Offending line: {line!r}",
            )


class RelayProductWebFlashReleaseSurfaceTests(unittest.TestCase):
    """HW-RELEASE-001: FanRelay IS release-eligible — EXPERIMENTAL only.

    Rewritten from the former ``RelayProductWebFlashExposureGuardsTests``
    (which pinned the pre-HW-RELEASE-001 "no WebFlash exposure" posture).
    HW-RELEASE-001 (docs/hw-release-001.md, 2026-07-09) retired the
    bench-proof documentation requirement as a release gate; the owner
    declares hardware readiness directly. The inverted invariants: the
    catalog entry is status preview with webflash_build_matrix true, an
    artifact_name, and an existing thin webflash wrapper; the builds row
    exists — on the EXPERIMENTAL channel exactly (mains-adjacent contact
    switching per the COMPLIANCE-001 lane posture). The preserved
    invariants: FanRelay is NEVER stable, RELEASE-RELAY-001 remains the
    STABLE blocker, the commercial posture stays non-customer, promotion
    is firmware-build proof only, and FanRelay stays out of
    release_one_required_configs.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.entry = _catalog_entry_for(RELAY_PRODUCT_REL)
        cls.builds_doc = _load_json(WEBFLASH_BUILDS)
        cls.compat = _load_json(WEBFLASH_COMPATIBILITY)
        cls.row = _builds_row_for(RELAY_CONFIG_STRING)

    def test_catalog_entry_webflash_build_matrix_is_true(self) -> None:
        self.assertEqual(
            self.entry.get("webflash_build_matrix"),
            True,
            "FanRelay product catalog entry must set "
            "webflash_build_matrix: true — HW-RELEASE-001 promoted the "
            "config into the declaration-driven release matrix.",
        )

    def test_catalog_entry_status_is_preview(self) -> None:
        self.assertEqual(
            self.entry.get("status"),
            "preview",
            "FanRelay product catalog entry must be status: preview (a "
            "release-eligible status) per owner decision HW-RELEASE-001.",
        )

    def test_catalog_entry_channel_is_experimental_exactly(self) -> None:
        self.assertEqual(
            self.entry.get("channel"),
            "experimental",
            "FanRelay catalog channel must be exactly 'experimental' — "
            "mains-adjacent contact switching takes the COMPLIANCE-001 "
            "lane posture; fan configs are NEVER on the stable channel.",
        )

    def test_catalog_entry_artifact_name_matches_contract(self) -> None:
        version = self.entry.get("version")
        self.assertEqual(version, "1.0.0")
        self.assertEqual(
            self.entry.get("artifact_name"),
            f"Sense360-{RELAY_CONFIG_STRING}-v{version}-experimental.bin",
            "FanRelay artifact_name must follow the "
            "Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin contract "
            "on the experimental channel.",
        )

    def test_catalog_entry_hardware_status_is_owner_declared(self) -> None:
        self.assertEqual(
            self.entry.get("hardware_status"),
            OWNER_DECLARED_HW_STATUS,
            "FanRelay hardware_status must record the HW-RELEASE-001 "
            "owner declaration (owner-declared, not measured/bench-proven).",
        )

    def test_catalog_entry_declares_existing_webflash_wrapper(self) -> None:
        self.assertEqual(
            self.entry.get("webflash_wrapper"),
            RELAY_WRAPPER_REL,
            "FanRelay catalog entry must declare the products/webflash "
            "wrapper HW-RELEASE-001 added.",
        )
        self.assertTrue(
            (REPO_ROOT / RELAY_WRAPPER_REL).is_file(),
            f"declared webflash_wrapper {RELAY_WRAPPER_REL!r} must exist",
        )

    def test_webflash_wrapper_is_thin_packages_only_reexport(self) -> None:
        wrapper = REPO_ROOT / RELAY_WRAPPER_REL
        data = _load_yaml(wrapper)
        self.assertEqual(
            set(data.keys()),
            {"packages"},
            "the FanRelay WebFlash wrapper must be a thin packages-only "
            "re-export (no substitutions / esphome / component blocks).",
        )
        includes = list((data.get("packages") or {}).values())
        self.assertEqual(
            includes,
            ["../sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml"],
            "the wrapper must !include exactly the canonical "
            "products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml "
            "(as ../sense360-*).",
        )

    def test_relay_builds_row_is_experimental_channel(self) -> None:
        self.assertEqual(
            self.row.get("channel"),
            "experimental",
            "the FanRelay config/webflash-builds.json row must be on the "
            "experimental channel exactly — never stable (HW-RELEASE-001 "
            "/ COMPLIANCE-001 lane posture).",
        )
        self.assertEqual(self.row.get("product_yaml"), RELAY_WRAPPER_REL)
        self.assertEqual(
            self.row.get("artifact_name"),
            self.entry.get("artifact_name"),
            "builds-row artifact_name must match the catalog entry",
        )

    def test_all_fanrelay_rows_experimental_never_stable(self) -> None:
        rows = [
            row
            for row in self.builds_doc.get("builds", []) or []
            if "FanRelay" in row.get("config_string", "")
        ]
        self.assertTrue(rows, "expected FanRelay rows post HW-RELEASE-001")
        for row in rows:
            with self.subTest(config_string=row.get("config_string")):
                self.assertEqual(
                    row.get("channel"),
                    "experimental",
                    "every FanRelay builds row must be on the "
                    "experimental channel exactly — fan configs are "
                    "NEVER stable.",
                )

    def test_relay_builds_row_stable_blocker_cites_release_relay_001(
        self,
    ) -> None:
        self.assertIn(
            "RELEASE-RELAY-001",
            self.row.get("stable_blocker", ""),
            "RELEASE-RELAY-001 remains the STABLE blocker for FanRelay — "
            "HW-RELEASE-001 promoted the experimental lane only, not "
            "stable.",
        )

    def test_relay_builds_row_commercial_posture_stays_non_customer(
        self,
    ) -> None:
        posture = self.row.get("commercial_posture") or {}
        for key in ("buyable", "recommended", "customer_default", "stable"):
            self.assertIs(
                posture.get(key),
                False,
                f"FanRelay builds-row commercial_posture.{key} must stay "
                f"false — HW-RELEASE-001 changes no customer visibility.",
            )

    def test_relay_builds_row_claims_firmware_build_proof_only(self) -> None:
        notes = self.row.get("notes", "").lower()
        self.assertIn(
            "firmware-build proof only",
            notes,
            "the FanRelay builds row must state promotion is "
            "firmware-build proof only (no false proof claims under "
            "HW-RELEASE-001).",
        )
        self.assertIn(
            "no hardware / bench / compliance",
            notes,
            "the FanRelay builds row must disclaim hardware / bench / "
            "compliance proof.",
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
        text = RELAY_BUNDLE.read_text()
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
        text = RELAY_BUNDLE.read_text()
        for line in _active_lines(text):
            self.assertNotIn(
                "artifact_name",
                line,
                f"FanRelay product YAML must not declare an "
                f"`artifact_name` field — no release artifact is built "
                f"by PRODUCT-RELAY-001. Offending line: {line!r}",
            )

    def test_catalog_entry_status_is_never_production(self) -> None:
        # HW-RELEASE-001 authorises preview-status / experimental-channel
        # release eligibility only. FanRelay must never reach production
        # status (the stable customer surface) while RELEASE-RELAY-001
        # (mains-safety / installation / competent-person evidence) is
        # open.
        self.assertNotEqual(
            self.entry.get("status"),
            "production",
            f"FanRelay product catalog entry must never be production — "
            f"RELEASE-RELAY-001 remains the stable blocker. "
            f"Got status={self.entry.get('status')!r}.",
        )


class RelayProductAdvancedManualWarningWordingTests(unittest.TestCase):
    """The FanRelay product YAML carries advanced / manual-warning wording.

    The PRODUCT-RELAY-001 readiness refresh
    (``docs/product-readiness-matrix.md`` §FanRelay / S360-310; archived
    under DOCS-DISPOSITION-001, see ``docs/archive-index.md``)
    requires explicit advanced / manual-warning + installation / safety
    + competent-person caveat wording in the product YAML itself. These
    tests pin that wording so a later refactor cannot silently strip it.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = RELAY_BUNDLE.read_text()
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
        # The version moves with release bumps (v1.0.1-led-preview,
        # 2026-07-06), so assert the invariant shape instead of pinning it.
        entry = self._find(LED_PREVIEW_CONFIG_STRING)
        self.assertEqual(entry["status"], "preview")
        self.assertEqual(entry["channel"], "preview")
        self.assertTrue(entry["version"])
        self.assertEqual(
            entry["artifact_name"],
            f"Sense360-{LED_PREVIEW_CONFIG_STRING}-v{entry['version']}-preview.bin",
        )
        self.assertTrue(entry["webflash_build_matrix"])
        self.assertEqual(entry["product_yaml"], LED_PREVIEW_PRODUCT_REL)

    def test_fantriac_catalog_entry_is_experimental_self_build(self) -> None:
        # TRIAC-COMMISSIONING-001 moved FanTRIAC into the experimental
        # self-build mains lane (status preview, channel experimental). This PR
        # (FanRelay readiness) does not change FanTRIAC; the preserved invariant
        # is that FanTRIAC is never a normal customer build — it stays on the
        # experimental channel, never stable, with the COMPLIANCE-001 stable
        # gate citation intact.
        entry = self._find(FANTRIAC_BLOCKED_CONFIG_STRING)
        self.assertEqual(entry["status"], "preview")
        self.assertEqual(entry.get("channel"), "experimental")
        self.assertIn(
            "COMPLIANCE-001",
            entry.get("stable_blocker", "") + " " + entry.get("reason", ""),
        )
        self.assertIs(
            entry.get("experimental_lane_posture", {}).get("never_stable"), True
        )

    def test_release_one_required_configs_unchanged(self) -> None:
        compat = _load_json(WEBFLASH_COMPATIBILITY)
        self.assertEqual(
            compat.get("release_one_required_configs"),
            [RELEASE_ONE_CONFIG_STRING],
            "release_one_required_configs must remain "
            "[Ceiling-POE-VentIQ-RoomIQ]; PRODUCT-RELAY-001 does not "
            "add FanRelay to the Release-One required configs.",
        )


class RelayProductCompileOnlyTargetTests(unittest.TestCase):
    """FW-COMPILE-RELAY-001 enrols the FanRelay product into compile-only.

    The PRODUCT-RELAY-001 / PR #564 product YAML lives at
    ``products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`` and
    carries the advanced / manual-warning-only posture. FW-COMPILE-RELAY-001
    adds a single compile-only validation target pointing at that same
    YAML so YAML / package / ESPHome compile drift surfaces in CI. The
    compile-only target itself carries **no** release-surface fields
    (no ``webflash_build_matrix`` / ``artifact_name`` /
    ``webflash_wrapper`` / ``expected_channel``): the release surface
    HW-RELEASE-001 added lives in the catalog + build matrix and is
    addressed via the products/webflash wrapper, never this lane.
    """

    COMPILE_ONLY_TARGETS_PATH = (
        REPO_ROOT / "config" / "compile-only-targets.json"
    )
    EXPECTED_TARGET_ID = "ceiling-poe-ventiq-fanrelay-roomiq-compile-only"

    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = _load_json(cls.COMPILE_ONLY_TARGETS_PATH)
        cls.targets = cls.doc.get("targets") or []
        cls.by_id = {t.get("id"): t for t in cls.targets if t.get("id")}
        cls.target = cls.by_id.get(cls.EXPECTED_TARGET_ID)

    def test_relay_compile_only_target_exists(self) -> None:
        self.assertIsNotNone(
            self.target,
            f"FW-COMPILE-RELAY-001 must add a compile-only target with "
            f"id {self.EXPECTED_TARGET_ID!r} to "
            "config/compile-only-targets.json",
        )

    def test_relay_compile_only_target_points_at_product_yaml(self) -> None:
        self.assertIsNotNone(self.target)
        self.assertEqual(
            self.target.get("product_yaml"),
            RELAY_PRODUCT_REL,
            f"FanRelay compile-only target must point at "
            f"{RELAY_PRODUCT_REL!r}",
        )

    def test_relay_compile_only_target_config_string(self) -> None:
        self.assertIsNotNone(self.target)
        self.assertEqual(
            self.target.get("config_string"),
            RELAY_CONFIG_STRING,
        )

    def test_relay_compile_only_target_shipment_status(self) -> None:
        self.assertIsNotNone(self.target)
        self.assertEqual(
            self.target.get("shipment_status"),
            "compile-only",
            "FanRelay compile-only target must declare "
            "shipment_status: compile-only — FW-COMPILE-RELAY-001 does "
            "not advance WebFlash exposure or release",
        )

    def test_relay_compile_only_target_is_advanced_manual_warning_only(
        self,
    ) -> None:
        self.assertIsNotNone(self.target)
        self.assertTrue(
            self.target.get("advanced_manual_warning_only"),
            "FanRelay compile-only target must declare "
            "advanced_manual_warning_only: true",
        )

    def test_relay_compile_only_target_is_hardware_pending(self) -> None:
        self.assertIsNotNone(self.target)
        self.assertTrue(
            self.target.get("hardware_pending"),
            "FanRelay compile-only target must declare "
            "hardware_pending: true (PRODUCT-RELAY-001 catalog row is "
            "status: hardware-pending)",
        )

    def test_relay_compile_only_target_requires_hardware(self) -> None:
        self.assertIsNotNone(self.target)
        self.assertTrue(
            self.target.get("hardware_required_for_validation"),
            "FanRelay compile-only target must declare "
            "hardware_required_for_validation: true",
        )

    def test_relay_compile_only_target_disallows_webflash_exposure(
        self,
    ) -> None:
        self.assertIsNotNone(self.target)
        self.assertFalse(
            self.target.get("webflash_exposure_allowed_now"),
            "FanRelay compile-only target must declare "
            "webflash_exposure_allowed_now: false",
        )

    def test_relay_compile_only_target_not_blocked(self) -> None:
        self.assertIsNotNone(self.target)
        self.assertFalse(
            self.target.get("blocked"),
            "FanRelay compile-only target must declare blocked: false "
            "— the FanRelay product is product-YAML-landed and "
            "compile-only-eligible",
        )

    def test_relay_compile_only_target_has_no_webflash_build_matrix(
        self,
    ) -> None:
        self.assertIsNotNone(self.target)
        self.assertNotIn(
            "webflash_build_matrix",
            self.target,
            "FanRelay compile-only target must NOT declare "
            "webflash_build_matrix — that field is owned by "
            "config/product-catalog.json and stays false",
        )

    def test_relay_compile_only_target_has_no_artifact_name(self) -> None:
        self.assertIsNotNone(self.target)
        self.assertNotIn(
            "artifact_name",
            self.target,
            "FanRelay compile-only target must NOT declare artifact_name "
            "— no release artifact is built by FW-COMPILE-RELAY-001",
        )

    def test_relay_compile_only_target_has_no_webflash_wrapper(self) -> None:
        self.assertIsNotNone(self.target)
        self.assertNotIn(
            "webflash_wrapper",
            self.target,
            "FanRelay compile-only target must NOT declare "
            "webflash_wrapper — no WebFlash wrapper is added by "
            "FW-COMPILE-RELAY-001",
        )

    def test_relay_compile_only_target_has_no_expected_channel(self) -> None:
        self.assertIsNotNone(self.target)
        self.assertNotIn(
            "expected_channel",
            self.target,
            "FanRelay compile-only target must NOT declare "
            "expected_channel — compile-only targets do not pin a "
            "WebFlash channel",
        )

    def test_relay_builds_row_addresses_wrapper_not_compile_only(
        self,
    ) -> None:
        # Rewritten for HW-RELEASE-001: the FanRelay build-matrix row now
        # exists, but it must address the products/webflash wrapper (the
        # release-gate namespace), never this compile-only lane, and it
        # stays on the experimental channel only.
        row = _builds_row_for(RELAY_CONFIG_STRING)
        self.assertEqual(row.get("product_yaml"), RELAY_WRAPPER_REL)
        self.assertNotIn("compile-only", row.get("product_yaml", ""))
        self.assertEqual(row.get("channel"), "experimental")

    def test_relay_compile_only_config_string_not_in_required_configs(
        self,
    ) -> None:
        compat = _load_json(WEBFLASH_COMPATIBILITY)
        required = compat.get("release_one_required_configs", []) or []
        self.assertNotIn(
            RELAY_CONFIG_STRING,
            required,
            f"release_one_required_configs must not contain "
            f"{RELAY_CONFIG_STRING!r} — FW-COMPILE-RELAY-001 does not "
            "promote FanRelay into Release-One required configs",
        )

    def test_release_one_compile_only_target_unchanged(self) -> None:
        """Release-One compile-only target stays webflash-current / stable."""
        rel_one = None
        for t in self.targets:
            if t.get("config_string") == RELEASE_ONE_CONFIG_STRING:
                rel_one = t
                break
        self.assertIsNotNone(
            rel_one,
            "Release-One compile-only target must remain present",
        )
        self.assertEqual(rel_one.get("shipment_status"), "webflash-current")
        self.assertEqual(rel_one.get("expected_channel"), "stable")
        self.assertTrue(rel_one.get("webflash_exposure_allowed_now"))

    def test_led_preview_compile_only_target_unchanged(self) -> None:
        """LED preview compile-only target stays preview-current / preview."""
        led = None
        for t in self.targets:
            if t.get("config_string") == LED_PREVIEW_CONFIG_STRING:
                led = t
                break
        self.assertIsNotNone(
            led,
            "LED preview compile-only target must remain present",
        )
        self.assertEqual(led.get("shipment_status"), "preview-current")
        self.assertEqual(led.get("expected_channel"), "preview")
        self.assertTrue(led.get("webflash_exposure_allowed_now"))


class RelayProductCustomerUsageExampleTests(unittest.TestCase):
    """The ``Customer usage`` example must reference this product's real path.

    The product YAML header carries a copy-paste remote-package
    ``packages: { sense360_firmware: { files: [...] } }`` example. A
    consumer pins to this exact ``files:`` path, so it must reference the
    FanRelay product's own canonical path
    (``products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml``) and that
    file must exist. A stale / transposed example path (the config-string
    order is ``VentIQ-FanRelay-RoomIQ`` but the filename is the same order,
    not ``VentIQ-RoomIQ-FanRelay``) would hand the customer a 404 remote
    include on the no-WebFlash manual-install path. This guard pins the
    example to the real file.
    """

    # Match the indented ``- products/....yaml`` reference inside the
    # commented customer-usage ``files:`` example.
    _FILES_REF = re.compile(r"-\s+(products/[A-Za-z0-9._-]+\.yaml)")

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = RELAY_BUNDLE.read_text()

    def _customer_usage_file_refs(self) -> List[str]:
        refs: List[str] = []
        for line in self.text.splitlines():
            stripped = line.lstrip()
            if not stripped.startswith("#"):
                continue
            match = self._FILES_REF.search(stripped)
            if match:
                refs.append(match.group(1))
        return refs

    def test_customer_usage_example_references_real_product_path(self) -> None:
        refs = self._customer_usage_file_refs()
        self.assertIn(
            RELAY_PRODUCT_REL,
            refs,
            f"The customer-usage remote-package example in "
            f"{RELAY_PRODUCT_REL} must reference the product's own real "
            f"path {RELAY_PRODUCT_REL!r}; found refs={refs!r}",
        )

    def test_customer_usage_example_references_only_existing_files(
        self,
    ) -> None:
        for ref in self._customer_usage_file_refs():
            with self.subTest(ref=ref):
                self.assertTrue(
                    (REPO_ROOT / ref).is_file(),
                    f"customer-usage example in {RELAY_PRODUCT_REL} "
                    f"references {ref!r}, which does not exist — a "
                    f"consumer pinning that path gets a broken remote "
                    f"include on the no-WebFlash manual-install path",
                )


class RelayManualFirmwareCandidateTests(unittest.TestCase):
    """MANUAL-FIRMWARE-CANDIDATE-001 evidence + HW-RELEASE-001 promotion.

    The full-compile evidence trail stands: the FanRelay compile-only
    target (which registers the top-level product YAML directly) records
    ``compile_validation_status: validated-full-compile`` from the
    committed FW-FULL-COMPILE-TOPLEVEL-FANS-001 / PR #616 run, and the
    catalog notes keep the candidate record and its no-false-proof
    disclaimers. The former "no more than a manual candidate" pins
    (status hardware-pending, no wrapper, no artifact, no build row)
    were inverted by owner decision HW-RELEASE-001: the entry is now a
    release-eligible experimental-channel config, still firmware-build
    proof only and never stable.
    """

    COMPILE_ONLY_TARGETS_PATH = (
        REPO_ROOT / "config" / "compile-only-targets.json"
    )
    TARGET_ID = "ceiling-poe-ventiq-fanrelay-roomiq-compile-only"

    @classmethod
    def setUpClass(cls) -> None:
        targets = (
            _load_json(cls.COMPILE_ONLY_TARGETS_PATH).get("targets") or []
        )
        cls.by_id = {t.get("id"): t for t in targets if t.get("id")}
        cls.entry = _catalog_entry_for(RELAY_PRODUCT_REL)

    def _target(self) -> Dict[str, Any]:
        target = self.by_id.get(self.TARGET_ID)
        self.assertIsNotNone(
            target,
            f"FanRelay compile-only target {self.TARGET_ID!r} must exist",
        )
        return target

    def test_target_points_at_top_level_product_yaml(self) -> None:
        self.assertEqual(self._target().get("product_yaml"), RELAY_PRODUCT_REL)

    def test_target_is_validated_full_compile(self) -> None:
        self.assertEqual(
            self._target().get("compile_validation_status"),
            "validated-full-compile",
            "FanRelay top-level compile-only target must record "
            "compile_validation_status: validated-full-compile — the "
            "full-compile evidence (committed FW-FULL-COMPILE-TOPLEVEL-FANS-001 "
            "/ PR #616 run, target #8, rc=0) that makes FanRelay a manual / "
            "no-WebFlash firmware candidate",
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
            "not kit-default",
        ):
            self.assertIn(
                marker, notes, f"FanRelay notes must disclaim {marker!r}"
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
            f"Sense360-{RELAY_CONFIG_STRING}-v{self.entry.get('version')}"
            f"-{self.entry.get('channel')}.bin",
        )

    def test_catalog_declares_webflash_wrapper(self) -> None:
        # Inverted from "no webflash_wrapper" by HW-RELEASE-001.
        self.assertEqual(
            self.entry.get("webflash_wrapper"), RELAY_WRAPPER_REL
        )

    def test_webflash_wrapper_file_exists_and_is_thin(self) -> None:
        # Inverted from "no wrapper file" by HW-RELEASE-001: the wrapper
        # exists and is a thin packages-only re-export of the canonical
        # product YAML.
        wrapper = REPO_ROOT / RELAY_WRAPPER_REL
        self.assertTrue(wrapper.is_file())
        data = _load_yaml(wrapper)
        self.assertEqual(set(data.keys()), {"packages"})
        self.assertIn(
            "../sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml",
            list((data.get("packages") or {}).values()),
        )

    def test_config_string_in_webflash_builds_experimental_never_stable(
        self,
    ) -> None:
        # Inverted from "not in webflash-builds" by HW-RELEASE-001; the
        # preserved half is channel teeth: experimental only, never stable.
        row = _builds_row_for(RELAY_CONFIG_STRING)
        self.assertEqual(row.get("channel"), "experimental")
        self.assertNotEqual(row.get("channel"), "stable")

    def test_config_string_not_in_release_one_required(self) -> None:
        compat = _load_json(WEBFLASH_COMPATIBILITY)
        self.assertNotIn(
            RELAY_CONFIG_STRING,
            compat.get("release_one_required_configs", []) or [],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

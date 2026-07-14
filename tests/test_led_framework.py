#!/usr/bin/env python3
"""LED-FRAMEWORK-001 — customer LED experience contract.

These tests define (and then pin) the customer-focused Sense360 LED framework
for the S360-300 LED board (12-LED WS2812B halo ring on the Core LED_DATA
line, GPIO38 per HW-010): one customer Room Light, a predictable Night Mode,
discreet status indication, an Identify action and safe restore behaviour —
arbitrated by a single priority model.

Contract highlights enforced here:

* Customer entities are exactly: Room Light, Night Mode, Night Mode
  Behaviour, Status Indicator, Identify Device, Darkness Threshold — stable
  IDs, product-facing names, enabled by default. There is deliberately NO
  per-channel entity, NO colour-temperature control (the WS2812B ring has no
  white/CCT channel), NO customer "Maximum Brightness" control (the software
  ceiling is a documented substitution), and NO novelty/strobe effects.
* The behaviour logic is a single header-only implementation
  (``include/sense360/led_controller.h``) shared by production YAML and the
  deterministic simulation tests (``tests/unit/test_led_controller.cpp``) —
  no second implementation that can drift.
* State ownership: customer/manual intent always wins; automation reverses
  only its own activations; transient overlays (identify/status) restore the
  previous state; restart restores the stable customer state and never a
  transient layer.
* Honesty: the WS2812B data line is one-way — the framework can never verify
  emitted light, so the LED module status keeps the compile-time vocabulary
  ("Included") and NO runtime health is fabricated. Brightness/colour/night
  values are provisional software definitions pending bench validation.
* Firmware-build / simulation proof only — no hardware, bench, compliance or
  commercial claim anywhere. No release declaration changes.

Uses Python's stdlib unittest (repo convention). Run with::

    python3 tests/test_led_framework.py
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any, Dict, List

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

BOARD_PACKAGE = REPO_ROOT / "packages" / "boards" / "s360-300-led.yaml"
FRAMEWORK_PACKAGE = REPO_ROOT / "packages" / "features" / "led_framework.yaml"
HEADER = REPO_ROOT / "include" / "sense360" / "led_controller.h"
CPP_TEST = REPO_ROOT / "tests" / "unit" / "test_led_controller.cpp"
DOC = REPO_ROOT / "docs" / "architecture" / "sense360-led-framework.md"
CHECKLIST = REPO_ROOT / "docs" / "hardware" / "led-framework-bench-checklist.md"
COMPILE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "core-framework-compile.yml"
VALIDATE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "validate.yml"
CONTRACT = REPO_ROOT / "config" / "core-framework.json"
MATRIX = REPO_ROOT / "config" / "feature-entity-matrix.json"
ROADMAP = REPO_ROOT / "docs" / "sense360-roadmap-status.md"
BUNDLES_DIR = REPO_ROOT / "products" / "bundles"

FRAMEWORK_INCLUDE = "!include ../../packages/features/led_framework.yaml"
BOARD_INCLUDE = "!include ../../packages/boards/s360-300-led.yaml"

# Approved customer effects (LED-10). "None" is provided natively by the
# light component; no strobe / rainbow / novelty effect ships by default.
APPROVED_EFFECT_NAMES = {"Gentle Pulse", "Night Glow"}
FORBIDDEN_EFFECT_NAMES = {
    "Alert",
    "Rainbow",
    "Random",
    "Scan",
    "Color Wipe",
    "Strobe",
}
FORBIDDEN_EFFECT_PLATFORMS = {"strobe", "addressable_rainbow", "addressable_scan"}

NIGHT_BEHAVIOUR_OPTIONS = ["Manual", "When dark", "When dark and occupied"]
STATUS_INDICATOR_OPTIONS = ["Off", "Essential", "Detailed"]

LAYER_STRINGS = ("Fault", "Identify", "Night Mode", "Room Light", "Status")
DARKNESS_STRINGS = ("Unknown", "Dark", "Not dark")

ENTITY_PLATFORM_KEYS = (
    "sensor",
    "binary_sensor",
    "text_sensor",
    "switch",
    "number",
    "button",
    "select",
    "light",
)


# --- ESPHome-tag-tolerant YAML loading --------------------------------------


def _esphome_tag(loader, node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None


for _tag in ("!secret", "!include", "!extend", "!lambda", "!remove"):
    yaml.add_constructor(_tag, _esphome_tag, Loader=yaml.SafeLoader)
yaml.add_multi_constructor("!include_dir_", _esphome_tag, Loader=yaml.SafeLoader)


def load_yaml(path: Path) -> Dict[str, Any]:
    doc = yaml.safe_load(path.read_text())
    return doc if isinstance(doc, dict) else {}


def entities_by_id(doc: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Flatten all top-level entity entries keyed by id."""
    out: Dict[str, Dict[str, Any]] = {}
    for platform in ENTITY_PLATFORM_KEYS:
        for entry in doc.get(platform) or []:
            if isinstance(entry, dict) and isinstance(entry.get("id"), str):
                out[entry["id"]] = dict(entry, _platform=platform)
    return out


def led_bundles() -> List[Path]:
    """Bundle files whose contract entry declares the led capability."""
    contract = json.loads(CONTRACT.read_text())
    paths = []
    for entry in contract.get("configs", {}).values():
        if "led" in (entry.get("capabilities") or []):
            paths.append(REPO_ROOT / entry["bundle"])
    return sorted(paths)


# --- Package existence -------------------------------------------------------


class PackageFilesExistTests(unittest.TestCase):
    def test_new_files_exist(self) -> None:
        for path in (
            FRAMEWORK_PACKAGE,
            HEADER,
            CPP_TEST,
            DOC,
            CHECKLIST,
        ):
            self.assertTrue(path.is_file(), f"missing LED-FRAMEWORK-001 file: {path}")

    def test_no_secret_material_in_led_packages(self) -> None:
        for path in (BOARD_PACKAGE, FRAMEWORK_PACKAGE):
            raw = path.read_text().lower()
            self.assertNotIn("!secret", raw, path.name)
            for needle in ("password", "api_encryption", "token"):
                self.assertNotIn(needle, raw, path.name)


# --- Room Light (board package: hardware adapter + customer light) -----------


class RoomLightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = load_yaml(BOARD_PACKAGE)
        cls.raw = BOARD_PACKAGE.read_text()
        cls.entities = entities_by_id(cls.doc)

    def _light(self) -> Dict[str, Any]:
        self.assertIn("led_ring", self.entities, "missing led_ring light")
        return self.entities["led_ring"]

    def test_room_light_entity(self) -> None:
        light = self._light()
        self.assertEqual(light["_platform"], "light")
        self.assertEqual(light.get("platform"), "esp32_rmt_led_strip")
        self.assertEqual(light.get("name"), "Room Light")
        self.assertFalse(light.get("disabled_by_default", False))
        self.assertNotEqual(light.get("internal"), True)

    def test_hardware_authority_unchanged(self) -> None:
        # HW-010: Core IO38 = LED_DATA; 12-LED WS2812B GRB ring. The
        # framework changes behaviour, never the verified hardware binding.
        subs = self.doc.get("substitutions") or {}
        self.assertEqual(subs.get("led_data_pin"), "GPIO38")
        self.assertEqual(str(subs.get("led_count")), "12")
        self.assertEqual(subs.get("led_chipset"), "WS2812")
        self.assertEqual(subs.get("led_rgb_order"), "GRB")
        self.assertNotIn("GPIO14", self.raw)

    def test_no_colour_temperature_claim(self) -> None:
        # The WS2812B ring has no white/CCT channel: colour-temperature
        # controls would be an unsupported hardware claim.
        self.assertNotIn("color_temperature", self.raw)
        self.assertNotIn("cold_white", self.raw)
        self.assertNotIn("warm_white", self.raw)

    def test_restore_is_framework_owned(self) -> None:
        # The framework's restore contract owns boot state (its persisted
        # customer-state globals are re-applied on boot); the light itself
        # must not race that with its own flash restore, so an interrupted
        # transient overlay can never flash back at boot.
        light = self._light()
        self.assertEqual(light.get("restore_mode"), "ALWAYS_OFF")

    def test_effects_are_exactly_the_approved_set(self) -> None:
        light = self._light()
        names = set()
        platforms = set()
        for effect in light.get("effects") or []:
            if not isinstance(effect, dict):
                continue
            for platform, config in effect.items():
                platforms.add(platform)
                if isinstance(config, dict) and "name" in config:
                    names.add(str(config["name"]))
        self.assertEqual(names, APPROVED_EFFECT_NAMES)
        self.assertFalse(names & FORBIDDEN_EFFECT_NAMES)
        self.assertFalse(platforms & FORBIDDEN_EFFECT_PLATFORMS)

    def test_effects_respect_max_brightness(self) -> None:
        # Every effect obeys the provisional software brightness ceiling.
        light = self._light()
        for effect in light.get("effects") or []:
            for platform, config in (effect or {}).items():
                if not isinstance(config, dict):
                    continue
                if str(config.get("name")) == "Gentle Pulse":
                    self.assertEqual(
                        str(config.get("max_brightness")),
                        "${led_max_brightness_pct}%",
                    )

    def test_max_brightness_is_provisional_substitution_not_entity(self) -> None:
        subs = self.doc.get("substitutions") or {}
        # No verified electrical/thermal ceiling exists (no recorded current
        # limit anywhere in the repo), so the existing 100% software limit is
        # preserved as an explicit, documented, provisional substitution.
        self.assertEqual(str(subs.get("led_max_brightness_pct")), "100")
        lowered = self.raw.lower()
        self.assertIn("provisional", lowered)
        self.assertIn("physical validation pending", lowered)
        self.assertIn("no electrical", lowered)

    def test_legacy_board_controls_removed(self) -> None:
        # The framework replaces the pre-framework board-level Night Mode
        # switch and LED Brightness number (duplicate, conflicting controls
        # were never shipped stable — LED is preview-gated).
        self.assertNotIn("switch:", self.doc)
        self.assertNotIn("number:", self.doc)
        self.assertNotIn("led_ring_night_mode", self.raw)
        self.assertNotIn("led_brightness_control", self.raw)

    def test_no_raw_channel_entities(self) -> None:
        # One Room Light; never one entity per physical channel.
        lights = [e for e in self.entities.values() if e["_platform"] == "light"]
        self.assertEqual(len(lights), 1)

    def test_sku_text_sensor_stays_diagnostic(self) -> None:
        raws = [
            entry
            for entry in self.doc.get("text_sensor") or []
            if isinstance(entry, dict)
        ]
        self.assertTrue(raws, "SKU text sensor missing")
        for entry in raws:
            self.assertEqual(entry.get("entity_category"), "diagnostic")


# --- Customer behaviour layer (framework package) -----------------------------


class CustomerEntityContractTests(unittest.TestCase):
    """The default-enabled customer surface is exactly the accepted set."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = load_yaml(FRAMEWORK_PACKAGE)
        cls.raw = FRAMEWORK_PACKAGE.read_text()
        cls.entities = entities_by_id(cls.doc)

    def _entity(self, entity_id: str) -> Dict[str, Any]:
        self.assertIn(entity_id, self.entities, f"missing entity id {entity_id}")
        return self.entities[entity_id]

    def test_night_mode_switch(self) -> None:
        entity = self._entity("s360_led_night_mode")
        self.assertEqual(entity["_platform"], "switch")
        self.assertEqual(entity.get("name"), "Night Mode")
        self.assertFalse(entity.get("disabled_by_default", False))
        # State is engine-truth (lambda-polled), so automation- and
        # customer-initiated changes stay in sync without publish races.
        self.assertIn("lambda", entity)

    def test_night_mode_behaviour_select(self) -> None:
        entity = self._entity("s360_led_night_behaviour")
        self.assertEqual(entity["_platform"], "select")
        self.assertEqual(entity.get("name"), "Night Mode Behaviour")
        self.assertEqual(entity.get("options"), NIGHT_BEHAVIOUR_OPTIONS)
        self.assertEqual(entity.get("initial_option"), "Manual")
        self.assertTrue(entity.get("restore_value"))
        self.assertFalse(entity.get("disabled_by_default", False))

    def test_no_scheduled_option_without_reliable_local_time(self) -> None:
        # Only SNTP (internet) and Home Assistant time sources exist —
        # neither is a reliable local-first scheduler, so "Scheduled" is
        # deferred (documented) rather than shipped dishonestly.
        entity = self._entity("s360_led_night_behaviour")
        for option in entity.get("options") or []:
            self.assertNotIn("sched", str(option).lower())

    def test_status_indicator_select(self) -> None:
        entity = self._entity("s360_led_status_indicator")
        self.assertEqual(entity["_platform"], "select")
        self.assertEqual(entity.get("name"), "Status Indicator")
        self.assertEqual(entity.get("options"), STATUS_INDICATOR_OPTIONS)
        self.assertEqual(entity.get("initial_option"), "Essential")
        self.assertTrue(entity.get("restore_value"))
        self.assertFalse(entity.get("disabled_by_default", False))

    def test_identify_button(self) -> None:
        entity = self._entity("s360_led_identify")
        self.assertEqual(entity["_platform"], "button")
        self.assertEqual(entity.get("name"), "Identify Device")
        self.assertFalse(entity.get("disabled_by_default", False))

    def test_darkness_threshold_number(self) -> None:
        entity = self._entity("s360_led_darkness_threshold")
        self.assertEqual(entity["_platform"], "number")
        self.assertEqual(entity.get("name"), "Darkness Threshold")
        self.assertEqual(float(entity.get("min_value")), 1.0)
        self.assertEqual(float(entity.get("max_value")), 200.0)
        self.assertEqual(float(entity.get("initial_value")), 20.0)
        self.assertEqual(entity.get("unit_of_measurement"), "lx")
        self.assertTrue(entity.get("restore_value"))
        self.assertEqual(entity.get("entity_category"), "config")
        self.assertFalse(entity.get("disabled_by_default", False))

    def test_no_customer_maximum_brightness_entity(self) -> None:
        # LED-09: no verified hardware ceiling exists, so a customer-facing
        # Maximum Brightness control would imply a safety contract we cannot
        # honour. The cap stays a documented substitution.
        for entity in self.entities.values():
            name = str(entity.get("name", "")).lower()
            self.assertNotIn("maximum brightness", name)
            self.assertNotIn("max brightness", name)

    def test_no_technical_customer_controls(self) -> None:
        for entity in self.entities.values():
            name = str(entity.get("name", "")).lower()
            for forbidden in ("channel", "pwm", "frequency", "gpio", "driver"):
                self.assertNotIn(forbidden, name, name)

    def test_diagnostics_are_diagnostic_and_disabled(self) -> None:
        for entity_id, expected_name in (
            ("s360_led_active_layer", "LED Active Layer"),
            ("s360_led_last_status_event", "LED Last Status Event"),
            ("s360_led_darkness_state", "LED Darkness State"),
            ("s360_led_output_verification", "LED Output Verification"),
        ):
            entity = self._entity(entity_id)
            self.assertEqual(entity.get("name"), expected_name, entity_id)
            self.assertEqual(entity.get("entity_category"), "diagnostic", entity_id)
            self.assertTrue(entity.get("disabled_by_default"), entity_id)

    def test_output_verification_states_one_way_limit(self) -> None:
        # Honesty companion: the WS2812B data line is one-way, so the
        # firmware can never verify the emitted light. The diagnostic states
        # this on-device so "Included" is never read as hardware health.
        entity = self._entity("s360_led_output_verification")
        value = str(entity.get("lambda", ""))
        self.assertIn("one-way", value)
        self.assertIn("cannot", value)

    def test_framework_uses_the_shared_header(self) -> None:
        self.assertIn("include/sense360/led_controller.h", self.raw)

    def test_framework_consumes_fused_occupancy_not_raw_sensors(self) -> None:
        # LED-04: the merged unified Occupancy contract is the input — never
        # raw PIR / radar / SEN0609 states.
        self.assertIn("s360_occupancy", self.raw)
        for forbidden in ("s360_pir_motion", "s360_sen0609_presence", "ld2450_"):
            self.assertNotIn(forbidden, self.raw)

    def test_darkness_comes_from_the_canonical_roomiq_service(self) -> None:
        # ROOMIQ-FRAMEWORK-001: the darkness decision (threshold,
        # hysteresis, lux staleness) is the canonical RoomIQ engine's
        # service. LED passes its customer threshold into that service and
        # consumes the decision — it never re-implements lux threshold
        # logic and never reads the raw board lux sensor.
        self.assertIn("sense360::roomiq", self.raw)
        self.assertIn("set_darkness_threshold", self.raw)
        self.assertIn("input_darkness", self.raw)
        self.assertNotIn("input_lux", self.raw)
        self.assertNotIn("comfort_ceiling_illuminance", self.raw)

    def test_no_duplicate_darkness_engine_in_led_controller(self) -> None:
        # Regression guard: exactly one lux-threshold implementation exists
        # (include/sense360/roomiq_engine.h). The LED controller consumes
        # the injected decision only.
        header_raw = HEADER.read_text() if HEADER.is_file() else ""
        self.assertNotIn("input_lux", header_raw)
        self.assertIn("input_darkness", header_raw)

    def test_restore_contract_uses_persisted_customer_state(self) -> None:
        # LED-11: the framework persists the stable customer state and
        # re-applies it on boot; transient overlays are never persisted.
        doc_globals = {
            entry.get("id"): entry
            for entry in self.doc.get("globals") or []
            if isinstance(entry, dict)
        }
        for needed in (
            "s360_led_saved_on",
            "s360_led_saved_brightness",
            "s360_led_night_on",
            "s360_led_night_auto",
        ):
            self.assertIn(needed, doc_globals, needed)
            self.assertTrue(
                doc_globals[needed].get("restore_value"),
                f"{needed} must persist across restart",
            )
        self.assertIn("on_boot", self.raw)
        self.assertIn("restore(", self.raw)

    def test_status_events_come_from_real_signals(self) -> None:
        # LED-06: no claimed status without a real signal — API connection
        # events are the supported connectivity signal.
        self.assertIn("on_client_connected", self.raw)
        self.assertIn("on_client_disconnected", self.raw)

    def test_no_fabricated_fault_producer(self) -> None:
        # The fault layer is an engine contract; no composed component
        # exposes a supported LED fault signal today, so nothing may call
        # set_fault(true) in production YAML.
        self.assertNotIn("set_fault(true)", self.raw)


# --- Engine header / simulation layer -----------------------------------------


class ControllerHeaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = HEADER.read_text() if HEADER.is_file() else ""

    def test_header_exists(self) -> None:
        self.assertTrue(HEADER.is_file(), f"missing {HEADER}")

    def test_namespace_and_engine(self) -> None:
        self.assertIn("namespace sense360", self.raw)
        self.assertIn("class LedController", self.raw)

    def test_layer_strings_are_single_sourced(self) -> None:
        for value in LAYER_STRINGS:
            self.assertIn(f'"{value}"', self.raw, value)

    def test_darkness_strings_are_single_sourced(self) -> None:
        for value in DARKNESS_STRINGS:
            self.assertIn(f'"{value}"', self.raw, value)

    def test_no_hardware_validation_claim(self) -> None:
        lowered = self.raw.lower()
        self.assertIn("provisional", lowered)
        self.assertNotIn("hardware verified", lowered)
        self.assertNotIn("bench verified", lowered)

    def test_simulation_tests_exist(self) -> None:
        self.assertTrue(CPP_TEST.is_file(), f"missing {CPP_TEST}")
        cpp = CPP_TEST.read_text()
        self.assertIn("led_controller.h", cpp)


# --- Bundle wiring --------------------------------------------------------------


class BundleWiringTests(unittest.TestCase):
    def test_led_bundles_are_exactly_the_authoritative_set(self) -> None:
        # Bundle authority: only the two catalog-declared LED-bearing
        # configs compose the LED board; the framework never spreads to a
        # bundle merely because the Core could support it.
        bundles = {p.name for p in led_bundles()}
        self.assertEqual(
            bundles,
            {
                "ceiling-poe-ventiq-roomiq-led.yaml",
                "ceiling-poe-roomiq-led.yaml",
            },
        )

    def test_every_led_bundle_composes_the_framework(self) -> None:
        for bundle in led_bundles():
            raw = bundle.read_text()
            self.assertIn(BOARD_INCLUDE, raw, bundle.name)
            self.assertIn(FRAMEWORK_INCLUDE, raw, bundle.name)

    def test_non_led_bundles_do_not_compose_led_packages(self) -> None:
        led = {p.resolve() for p in led_bundles()}
        for bundle in sorted(BUNDLES_DIR.glob("*.yaml")):
            if bundle.resolve() in led:
                continue
            raw = bundle.read_text()
            self.assertNotIn("led_framework.yaml", raw, bundle.name)
            self.assertNotIn("s360-300-led", raw, bundle.name)

    def test_led_bundles_have_the_framework_inputs(self) -> None:
        # The framework consumes the fused Occupancy entity and the
        # canonical RoomIQ darkness service; every LED bundle must compose
        # all three sources (Presence, the RoomIQ board and the RoomIQ
        # environmental framework).
        for bundle in led_bundles():
            raw = bundle.read_text()
            self.assertIn("presence_framework.yaml", raw, bundle.name)
            self.assertIn("s360-200-roomiq.yaml", raw, bundle.name)
            self.assertIn("roomiq_framework.yaml", raw, bundle.name)

    def test_legacy_alias_paths_still_resolve(self) -> None:
        # Customers pin legacy paths; they must keep existing.
        for rel in (
            "packages/hardware/led_ring_ceiling.yaml",
            "packages/hardware/led_ring_mic_ceiling.yaml",
        ):
            self.assertTrue((REPO_ROOT / rel).is_file(), rel)


# --- Core framework contract ------------------------------------------------------


class CoreFrameworkContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text())

    def test_led_capability_names_the_framework(self) -> None:
        description = self.contract["capabilities"]["led"]["description"]
        self.assertIn("WS2812", description)
        self.assertIn("LED-FRAMEWORK-001", description)

    def test_led_module_status_stays_compile_time(self) -> None:
        # Honesty rule: the WS2812B data line is one-way — no real runtime
        # health signal exists, so the LED module must NOT claim the
        # reserved runtime vocabulary. "Included" stays compile-time truth.
        runtime = self.contract.get("module_runtime_status") or {}
        self.assertNotIn(
            "led",
            runtime,
            "LED has no supported runtime health signal; do not fabricate "
            "module runtime status",
        )


# --- Feature-entity matrix -----------------------------------------------------


class FeatureEntityMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        matrix = json.loads(MATRIX.read_text())
        cls.board = next(b for b in matrix["boards"] if b["sku"] == "S360-300")

    def test_night_mode_row_points_at_the_framework(self) -> None:
        rows = [r for r in self.board["rows"] if "Night mode" in r["row"]]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["status"], "present")
        self.assertIn("s360_led_night_mode", str(row["present_as"]))
        self.assertIn("led_framework.yaml", str(row["defined_in"]))

    def test_night_light_gap_stays_operator_gated(self) -> None:
        # The separate dedicated night-light *light* entity remains an
        # unconfirmed product intent: this framework implements Night Mode
        # as a profile on the Room Light and must NOT silently fill the
        # operator-gated gap.
        rows = [r for r in self.board["rows"] if "night-light" in r["row"].lower()]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "missing")
        self.assertEqual(rows[0]["confirm"], "needs-operator-confirm")

    def test_room_light_row_reflects_new_surface(self) -> None:
        rows = [
            r
            for r in self.board["rows"]
            if "light" in r["row"].lower() and r["status"] == "present"
        ]
        self.assertTrue(rows)
        joined = " ".join(str(r["present_as"]) for r in rows)
        self.assertIn("Room Light", joined)
        self.assertNotIn("Rainbow", " ".join(r["row"] for r in self.board["rows"]))


# --- Compile lane / CI wiring ------------------------------------------------------


class CompileLaneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = COMPILE_WORKFLOW.read_text()
        cls.doc = yaml.safe_load(cls.raw)

    def _matrix_configs(self) -> Dict[str, str]:
        jobs = self.doc.get("jobs") or {}
        for job in jobs.values():
            include = ((job.get("strategy") or {}).get("matrix") or {}).get("include")
            if include:
                return {row["config_string"]: row["product_yaml"] for row in include}
        return {}

    def test_matrix_covers_the_required_led_compositions(self) -> None:
        configs = self._matrix_configs()
        # The current LED preview product (VentIQ + RoomIQ + Presence + LED).
        self.assertIn("Ceiling-POE-VentIQ-RoomIQ-LED", configs)
        # The authoritative PoE LED-bearing RoomIQ bundle (Presence + LED).
        self.assertEqual(
            configs.get("Ceiling-POE-RoomIQ-LED"),
            "products/sense360-ceiling-poe-roomiq-led.yaml",
        )
        # A non-LED bundle stays in the matrix as the regression check that
        # the LED package is not accidentally included (Release-One).
        self.assertIn("Ceiling-POE-VentIQ-RoomIQ", configs)

    def test_paths_cover_led_framework_surfaces(self) -> None:
        triggers = self.doc.get("on", self.doc.get(True)) or {}
        paths = (triggers.get("pull_request") or {}).get("paths") or []
        for needed in (
            "packages/boards/**",
            "packages/features/**",
            "include/sense360/**",
            "tests/unit/**",
            "tests/test_led_framework.py",
        ):
            self.assertIn(needed, paths)

    def test_contract_gate_runs_led_tests(self) -> None:
        self.assertIn("tests/test_led_framework.py", self.raw)
        # The deterministic C++ simulation suite runs in the cheap gate job.
        self.assertIn("make -C tests test", self.raw)

    def test_lane_guarantees_unchanged(self) -> None:
        triggers = self.doc.get("on", self.doc.get(True)) or {}
        self.assertEqual(set(triggers), {"pull_request", "workflow_dispatch"})
        self.assertEqual(self.doc.get("permissions"), {"contents": "read"})
        self.assertNotIn("upload-artifact", self.raw)

    def test_quick_validation_gate_runs_led_contract(self) -> None:
        self.assertIn("tests/test_led_framework.py", VALIDATE_WORKFLOW.read_text())


# --- Documentation ------------------------------------------------------------------


class DocumentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = DOC.read_text() if DOC.is_file() else ""
        cls.lowered = cls.text.lower()
        cls.normalised = " ".join(cls.lowered.split())

    def test_doc_exists_and_names_the_work_item(self) -> None:
        self.assertTrue(DOC.is_file(), f"missing {DOC}")
        self.assertIn("LED-FRAMEWORK-001", self.text)

    def test_customer_contract_documented(self) -> None:
        for name in (
            "Room Light",
            "Night Mode",
            "Night Mode Behaviour",
            "Status Indicator",
            "Identify Device",
            "Darkness Threshold",
        ):
            self.assertIn(name, self.text, name)
        for option in NIGHT_BEHAVIOUR_OPTIONS + STATUS_INDICATOR_OPTIONS:
            self.assertIn(option, self.text, option)

    def test_priority_and_ownership_documented(self) -> None:
        self.assertIn("priority", self.lowered)
        self.assertIn("ownership", self.lowered)
        for layer in LAYER_STRINGS:
            self.assertIn(layer, self.text, layer)

    def test_restore_contract_documented(self) -> None:
        self.assertIn("restore", self.lowered)
        self.assertIn("safe mode", self.lowered)

    def test_brightness_limits_documented_honestly(self) -> None:
        # No verified electrical/thermal ceiling exists: the doc must state
        # the software cap is provisional and never claim 100% is safe.
        self.assertIn("provisional", self.normalised)
        self.assertIn("physical validation pending", self.normalised)
        for forbidden in (
            "physically safe",
            "electrically safe",
            "flicker-free",
            "hardware verified",
            "bench verified",
        ):
            self.assertNotIn(forbidden, self.normalised)

    def test_one_way_output_limitation_documented(self) -> None:
        self.assertIn("one-way", self.lowered)
        self.assertIn("included", self.lowered)

    def test_scheduled_deferral_documented(self) -> None:
        self.assertIn("scheduled", self.lowered)
        self.assertIn("deferred", self.lowered)

    def test_bundle_membership_documented(self) -> None:
        self.assertIn("Ceiling-POE-VentIQ-RoomIQ-LED", self.text)
        self.assertIn("Ceiling-POE-RoomIQ-LED", self.text)

    def test_lux_sensor_conflict_reported(self) -> None:
        # The hardware catalog documents LTR-303ALS for RoomIQ while the
        # compiled firmware uses VEML7700 — the doc must surface this
        # unresolved documentation-vs-firmware mismatch, not hide it.
        self.assertIn("VEML7700", self.text)
        self.assertIn("LTR-303", self.text)


class BenchChecklistTests(unittest.TestCase):
    def test_checklist_prepared_without_results(self) -> None:
        self.assertTrue(CHECKLIST.is_file(), f"missing {CHECKLIST}")
        text = CHECKLIST.read_text()
        lowered = text.lower()
        for topic in (
            "colour",
            "channel order",
            "minimum visible brightness",
            "maximum safe brightness",
            "thermal",
            "power draw",
            "night mode",
            "diffuser",
            "flicker",
            "restart",
            "identify",
            "status indication",
            "presence",
            "lux",
            "hysteresis",
            "latency",
            "recovery",
            "rail",
        ):
            self.assertIn(topic, lowered, topic)
        # Prepared, not executed: unchecked boxes only, no results, no
        # machine-written attestation (standing rule).
        self.assertIn("[ ]", text)
        self.assertNotIn("[x]", lowered)
        self.assertIn("no results", lowered)


class RoadmapTests(unittest.TestCase):
    def test_roadmap_records_led_framework(self) -> None:
        text = ROADMAP.read_text()
        self.assertIn("LED-FRAMEWORK-001", text)
        section = text[text.index("LED-FRAMEWORK-001") :][:8000]
        lowered = section.lower()
        self.assertIn("software foundation", lowered)
        self.assertIn("pending", lowered)
        self.assertIn("SOT", section)
        self.assertIn("LED-FRAMEWORK-BENCH-001", section)


if __name__ == "__main__":
    unittest.main(verbosity=2)

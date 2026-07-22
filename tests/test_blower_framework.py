#!/usr/bin/env python3
"""BLOWER-FRAMEWORK-001 — customer blower experience contract.

These tests define (and then pin) the customer-focused Sense360 blower framework
for the Core's dedicated on-board FAN net (schematic ``IO21`` → Q4 SI2302S → J13,
a two-wire binary 5 V blower output): one customer Blower control, a Blower Mode
(Manual / Auto) that optionally follows the canonical AirIQ ventilation demand,
and a Blower Auto Trigger — all honest about the fact that J13 has NO speed /
tach / current / airflow / rotation feedback.

Contract highlights enforced here:

* The behaviour logic is a single header-only implementation
  (``include/sense360/blower_controller.h``) shared by production YAML and the
  deterministic simulation tests (``tests/unit/test_blower_controller.cpp`` and
  ``tests/unit/test_blower_airiq_coexist.cpp``) — no second implementation that
  can drift. It is delivered to remote consumers via the ``sense360`` external
  component (registered in ``include/sense360/__init__.py``).
* AirIQ is an OPTIONAL input read through the shared engine singleton
  ``sense360::airiq::global_engine().recommendation()`` — never a hard ``id()``
  to an AirIQ entity, and pollutant thresholds are never duplicated. The
  compile-time flag ``blower_has_airiq`` (default ``"false"``) gates the Auto
  behaviour, which is honestly downgraded to Manual when AirIQ is absent.
* Fail-safe: a missing / initialising / unavailable AirIQ demand is UNKNOWN and
  NEVER starts the blower.
* Honesty: the FAN net is a one-way binary drive; the framework commands only
  on/off and claims no speed / airflow / current / rotation. It NEVER touches
  the Core ``GPIO46`` status LED (not rotation feedback) or the separate
  ``GPIO3`` relay.
* Gate posture: the blower is a fan output, so the "Fans are never stable"
  standing gate applies — the framework ships COMPILE-ONLY: no
  ``config/webflash-builds.json`` row, no artifact, never stable / preview /
  customer-default / buyable / kit-exposed.
* Firmware-build / simulation proof only — no hardware, bench, airflow,
  compliance or commercial claim anywhere. No release declaration changes.

Uses Python's stdlib unittest (repo convention). Run with::

    python3 tests/test_blower_framework.py

or::

    python3 -m unittest tests.test_blower_framework -v
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from typing import Any, Dict, List

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

FRAMEWORK_PACKAGE = REPO_ROOT / "packages" / "features" / "blower_framework.yaml"
REMOTE_WRAPPER = REPO_ROOT / "packages" / "remote" / "blower-framework.yaml"
FIXTURE = REPO_ROOT / "products" / "sense360-core-ceiling-airiq-blower.yaml"
HEADER = REPO_ROOT / "include" / "sense360" / "blower_controller.h"
AIRIQ_HEADER = REPO_ROOT / "include" / "sense360" / "airiq_engine.h"
CPP_TEST = REPO_ROOT / "tests" / "unit" / "test_blower_controller.cpp"
CPP_COEXIST = REPO_ROOT / "tests" / "unit" / "test_blower_airiq_coexist.cpp"
DOC = REPO_ROOT / "docs" / "architecture" / "sense360-blower-framework.md"
CHECKLIST = REPO_ROOT / "docs" / "hardware" / "blower-framework-bench-checklist.md"
INIT_PY = REPO_ROOT / "include" / "sense360" / "__init__.py"

PRODUCT_CATALOG = REPO_ROOT / "config" / "product-catalog.json"
COMPILE_ONLY_TARGETS = REPO_ROOT / "config" / "compile-only-targets.json"
WEBFLASH_BUILDS = REPO_ROOT / "config" / "webflash-builds.json"

CONFIG_STRING = "Ceiling-Core-AirIQ-Blower"
FAN_PIN = "GPIO21"


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


def strip_cpp_comments(src: str) -> str:
    """Remove // and /* */ comments so honesty disclaimers in comments do not
    trip code-level bans."""
    src = re.sub(r"/\*.*?\*/", " ", src, flags=re.DOTALL)
    src = re.sub(r"//[^\n]*", " ", src)
    return src


def entries(doc: Dict[str, Any], platform: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for entry in doc.get(platform) or []:
        if isinstance(entry, dict):
            out.append(entry)
    return out


class EngineHeaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = HEADER.read_text() if HEADER.is_file() else ""

    def test_header_exists(self) -> None:
        self.assertTrue(HEADER.is_file(), "blower_controller.h must exist")

    def test_header_is_self_contained_stdlib_only(self) -> None:
        # Every shared engine header is self-contained (standard library only)
        # so it compiles natively and as an ESPHome external component. The
        # cross-namespace demand read is proven by the coexistence test, not by
        # cross-including airiq_engine.h here.
        self.assertNotIn('#include "', self.raw)
        self.assertIn("#pragma once", self.raw)

    def test_defines_customer_vocabulary_and_api(self) -> None:
        for token in (
            "namespace blower",
            "MODE_OFF",
            "MODE_AUTO",
            "MODE_ON",
            "DEMAND_UNKNOWN",
            "DEMAND_ELEVATED",
            "DEMAND_HIGH",
            "TRIGGER_NOW",
            "TRIGGER_SOON",
            "STATE_AUTO_PURGE",
            "demand_from_airiq_recommendation",
            "set_has_airiq",
            "set_min_on_ms",
            "set_min_off_ms",
            "set_purge_ms",
            "purging",
            "output_on",
            "global_controller",
        ):
            self.assertIn(token, self.raw, f"header must define {token}")

    def test_default_mode_is_auto(self) -> None:
        # Auto is the default/first-boot mode (owner decision).
        self.assertIn("Mode mode_ = MODE_AUTO", self.raw)

    def test_fail_safe_unknown_demand_never_starts_blower(self) -> None:
        # A start requires an actionable demand (HIGH, or ELEVATED under the
        # SOON trigger); UNKNOWN is never actionable, so a stopped blower never
        # starts on unknown/stale data, and the honest off-state names it.
        self.assertIn("demand_ == DEMAND_HIGH", self.raw)
        self.assertIn("STATE_AUTO_OFF_UNKNOWN", self.raw)

    def test_no_speed_or_rotation_surface(self) -> None:
        # Honesty: the engine commands binary on/off only. Its CODE (comments
        # stripped — they legitimately disclaim these words) must not model a
        # speed, RPM, airflow or rotation value.
        code = strip_cpp_comments(self.raw).lower()
        for banned in ("rpm", "airflow", "tach", "rotation", "speed"):
            self.assertNotIn(banned, code, f"engine code must not reference {banned!r}")

    def test_registered_in_shared_headers(self) -> None:
        init = INIT_PY.read_text()
        self.assertIn(
            '"blower_controller.h"',
            init,
            "blower_controller.h must be registered in include/sense360/__init__.py "
            "SHARED_HEADERS so remote consumers receive it",
        )


class CppSimulationTests(unittest.TestCase):
    def test_cpp_tests_exist_and_use_the_header(self) -> None:
        self.assertTrue(CPP_TEST.is_file(), "native blower controller test must exist")
        self.assertIn("blower_controller.h", CPP_TEST.read_text())

    def test_coexist_test_pins_airiq_demand_contract(self) -> None:
        self.assertTrue(CPP_COEXIST.is_file(), "blower/airiq coexist test must exist")
        raw = CPP_COEXIST.read_text()
        self.assertIn("airiq_engine.h", raw)
        self.assertIn("blower_controller.h", raw)
        # The coexist test pins the integer contract the demand mapping relies on.
        self.assertIn("RECOMMENDATION_VENTILATE_NOW", raw)


class FrameworkPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = FRAMEWORK_PACKAGE.read_text()
        cls.doc = load_yaml(FRAMEWORK_PACKAGE)

    def test_fan_pin_is_the_verified_fan_net(self) -> None:
        subs = self.doc.get("substitutions") or {}
        self.assertEqual(
            subs.get("blower_fan_pin"),
            FAN_PIN,
            "the blower must drive the verified FAN net on GPIO21",
        )

    def test_has_airiq_defaults_false(self) -> None:
        subs = self.doc.get("substitutions") or {}
        self.assertEqual(
            str(subs.get("blower_has_airiq")).lower(),
            "false",
            "blower_has_airiq must default false so the framework degrades cleanly",
        )

    def test_timing_substitutions_present(self) -> None:
        subs = self.doc.get("substitutions") or {}
        for sub in ("blower_min_on_ms", "blower_min_off_ms", "blower_purge_ms"):
            self.assertIn(sub, subs, f"framework must expose {sub}")

    def test_compiles_both_engine_headers(self) -> None:
        includes = (self.doc.get("esphome") or {}).get("includes") or []
        joined = " ".join(str(i) for i in includes)
        self.assertIn("blower_controller.h", joined)
        self.assertIn(
            "airiq_engine.h",
            joined,
            "the AirIQ engine header must be compiled so the demand read resolves "
            "with or without the AirIQ framework composed",
        )

    def test_reads_airiq_demand_via_engine_singleton_not_hard_id(self) -> None:
        # The framework consults the shared AirIQ engine singleton, never a hard
        # id() to an AirIQ entity (which a device without AirIQ would not define).
        self.assertIn("sense360::airiq::global_engine().recommendation()", self.raw)
        self.assertIn("demand_from_airiq_recommendation", self.raw)

    def test_blower_output_and_readonly_state(self) -> None:
        outputs = entries(self.doc, "output")
        blower_out = [o for o in outputs if o.get("id") == "blower_output"]
        self.assertEqual(len(blower_out), 1, "exactly one blower_output")
        self.assertEqual(blower_out[0].get("pin"), "${blower_fan_pin}")

        # Option A: no controllable fan/switch toggle that could contradict the
        # selected mode — the mode is the authoritative control.
        self.assertEqual(entries(self.doc, "fan"), [], "no controllable fan entity")
        self.assertEqual(entries(self.doc, "switch"), [], "no controllable switch entity")

        # The "Blower" is a read-only commanded-state binary_sensor (a lambda
        # representation), never a customer toggle.
        bsensors = {b.get("id"): b for b in entries(self.doc, "binary_sensor")}
        self.assertIn("blower_state", bsensors)
        blower = bsensors["blower_state"]
        self.assertEqual(blower.get("name"), "Blower")
        self.assertIn("lambda", blower, "Blower state is a read-only lambda sensor")
        self.assertNotIn("on_press", blower)

    def test_customer_config_entities(self) -> None:
        selects = {s.get("id"): s for s in entries(self.doc, "select")}
        # Owner decision: explicit Off / Auto / On, default Auto.
        self.assertIn("s360_blower_mode", selects)
        self.assertEqual(
            selects["s360_blower_mode"].get("options"), ["Off", "Auto", "On"]
        )
        self.assertEqual(
            selects["s360_blower_mode"].get("initial_option"),
            "Auto",
            "the blower must default to Auto (operate automatically out of the box)",
        )
        self.assertTrue(
            selects["s360_blower_mode"].get("restore_value"),
            "the selected mode must persist across restart",
        )
        self.assertIn("s360_blower_auto_trigger", selects)
        self.assertEqual(
            selects["s360_blower_auto_trigger"].get("options"),
            ["Ventilate now", "Ventilate soon"],
        )

    def test_diagnostics_present_and_disabled_by_default(self) -> None:
        texts = {t.get("id"): t for t in entries(self.doc, "text_sensor")}
        for tid in (
            "s360_blower_status",
            "s360_blower_demand",
            "s360_blower_output_verification",
        ):
            self.assertIn(tid, texts, f"diagnostic {tid} must exist")
            self.assertEqual(texts[tid].get("entity_category"), "diagnostic")
            self.assertTrue(texts[tid].get("disabled_by_default"))

    def test_output_verification_states_the_one_way_limit(self) -> None:
        verify = [
            t
            for t in entries(self.doc, "text_sensor")
            if t.get("id") == "s360_blower_output_verification"
        ][0]
        lam = str(verify.get("lambda", "")).lower()
        # (the string is split across C++ literals, so check the words, not a phrase)
        self.assertIn("one-way", lam)
        self.assertIn("verified", lam)

    def test_never_touches_gpio46_or_gpio3_or_relay(self) -> None:
        # The Core status LED (GPIO46) is NEVER rotation feedback and the generic
        # GPIO3 relay is a SEPARATE control. The honesty comment / diagnostic text
        # legitimately NAME them to disclaim them, so we assert the framework never
        # CONFIGURES those pins and never defines / drives the relay entity.
        self.assertNotIn("pin: GPIO3", self.raw)
        self.assertNotIn("pin: GPIO46", self.raw)
        self.assertNotIn("number: GPIO3", self.raw)
        self.assertNotIn("number: GPIO46", self.raw)
        self.assertNotIn("id: main_relay", self.raw)
        # The only pin the framework configures is the FAN-net substitution.
        pins = [o.get("pin") for o in entries(self.doc, "output")]
        self.assertEqual(pins, ["${blower_fan_pin}"])

    def test_no_tach_pulse_counter_or_rpm(self) -> None:
        # Config-form bans (these constructs never appear in the honesty prose).
        self.assertNotIn("pulse_counter", self.raw)
        self.assertNotIn("platform: speed", self.raw)
        self.assertNotIn("rpm", self.raw.lower())


class RemoteWrapperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = REMOTE_WRAPPER.read_text()
        cls.doc = load_yaml(REMOTE_WRAPPER)

    def test_delivers_engine_via_external_component(self) -> None:
        ext = self.doc.get("external_components") or []
        self.assertTrue(ext, "remote wrapper must declare the sense360 external component")
        source = ext[0].get("source") or {}
        # git delivery, NOT type: local (which would break remote consumers).
        self.assertEqual(source.get("type"), "git")
        self.assertIn("sense360", ext[0].get("components") or [])
        # No repository-local include path survives for a remote consumer.
        self.assertIn("includes: !remove", self.raw)

    def test_includes_the_framework_and_defaults_airiq_false(self) -> None:
        pkgs = self.doc.get("packages") or {}
        joined = " ".join(str(v) for v in pkgs.values())
        self.assertIn("../features/blower_framework.yaml", joined)
        subs = self.doc.get("substitutions") or {}
        self.assertEqual(str(subs.get("blower_has_airiq")).lower(), "false")


class FixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = FIXTURE.read_text()
        cls.doc = load_yaml(FIXTURE)

    def test_composes_core_airiq_and_blower(self) -> None:
        pkgs = self.doc.get("packages") or {}
        joined = " ".join(str(v) for v in pkgs.values())
        self.assertIn("s360-100-core-ceiling.yaml", joined)
        self.assertIn("s360-210-airiq.yaml", joined)
        self.assertIn("airiq_framework.yaml", joined)
        self.assertIn("blower_framework.yaml", joined)

    def test_declares_airiq_capability_true(self) -> None:
        subs = self.doc.get("substitutions") or {}
        self.assertEqual(str(subs.get("blower_has_airiq")).lower(), "true")
        self.assertEqual(subs.get("s360_config_string"), CONFIG_STRING)


class CatalogGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads(PRODUCT_CATALOG.read_text())
        cls.targets = json.loads(COMPILE_ONLY_TARGETS.read_text())
        cls.webflash_raw = WEBFLASH_BUILDS.read_text()

    def _catalog_entry(self) -> Dict[str, Any]:
        for entry in self.catalog.get("products", []):
            if entry.get("config_string") == CONFIG_STRING:
                return entry
        self.fail(f"{CONFIG_STRING} missing from product-catalog.json")

    def test_catalog_entry_is_compile_only_and_not_webflash(self) -> None:
        entry = self._catalog_entry()
        self.assertEqual(entry.get("status"), "compile-only")
        self.assertFalse(entry.get("webflash_build_matrix"))
        self.assertEqual(entry.get("target_channel"), "manual-custom")
        self.assertNotIn("artifact_name", entry)
        self.assertNotIn("webflash_wrapper", entry)
        self.assertEqual(
            entry.get("product_yaml"),
            "products/sense360-core-ceiling-airiq-blower.yaml",
        )

    def test_compile_only_target_registered(self) -> None:
        ids = {t.get("id") for t in self.targets.get("targets", [])}
        self.assertIn("ceiling-core-airiq-blower-compile-only", ids)
        target = next(
            t
            for t in self.targets["targets"]
            if t.get("id") == "ceiling-core-airiq-blower-compile-only"
        )
        self.assertEqual(target.get("shipment_status"), "compile-only")
        self.assertFalse(target.get("webflash_exposure_allowed_now"))
        self.assertFalse(target.get("blocked"))

    def test_blower_is_never_a_webflash_build(self) -> None:
        # "Fans are never stable" — the blower has no WebFlash build row and no
        # artifact anywhere. Neither the config string nor a Blower token appears
        # in the release matrix.
        self.assertNotIn(CONFIG_STRING, self.webflash_raw)
        self.assertNotIn("Blower", self.webflash_raw)


if __name__ == "__main__":
    unittest.main(verbosity=2)

#!/usr/bin/env python3
"""S360-100-NATIVE-FAN-GPIO-MAP-001 — native ESP32-S3 GPIO map for the
S360-100 / S360-311 fan signal path.

This module pins the architectural correction recorded in
``docs/hardware/s360-100-native-fan-gpio-map.md``:

1. **The canonical fan GPIO map doc exists and lists every required
   native ESP32-S3 GPIO** for the four FanPWM control nets
   (``TachPMW1..4``) and the four tach / pulse-counter nets
   (``Pul_Cou1..4``) plus the shared ``TachIO`` passthrough.

2. **The current FanPWM YAMLs are explicitly labelled legacy /
   superseded** against that map. The FanPWM package
   (``packages/expansions/fan_pwm.yaml``), its SX1509 binding layer
   (``packages/expansions/fan_pwm_sx1509.yaml``), the product YAML
   (``products/sense360-ceiling-poe-fanpwm.yaml``) and the
   compile-only skeleton
   (``products/compile-only/ceiling-poe-fanpwm.yaml``) all carry that
   classification in their YAML header comments so the SX1509 fan
   path cannot be silently presented as the current FanPWM control /
   tach implementation.

3. **No current FanPWM release / WebFlash path uses SX1509 for PWM
   or tach.** The ``FanPWM`` token must not appear in
   ``config/webflash-builds.json``; the FanPWM catalog row must keep
   ``webflash_build_matrix: false``, no ``artifact_name``, and a
   non-release-eligible status. The historical SX1509 / pulse_counter
   compile/config proof fixture and test stay in place as evidence
   for the rule (not as the current hardware path).

4. **The canonical map records the same native ESP32-S3 GPIOs as the
   S360-100 Core architecture doc** so a future drift cannot
   silently rewrite either record in isolation.

Run with::

    python3 tests/test_native_fan_gpio_map.py

or::

    python3 -m unittest tests.test_native_fan_gpio_map -v
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parent.parent

FAN_GPIO_MAP_DOC = REPO_ROOT / "docs" / "hardware" / "s360-100-native-fan-gpio-map.md"
CORE_ARCHITECTURE_DOC = REPO_ROOT / "docs" / "hardware" / "s360-100-core-architecture.md"

FAN_PWM_PACKAGE = REPO_ROOT / "packages" / "expansions" / "fan_pwm.yaml"
FAN_PWM_SX1509_BINDING = REPO_ROOT / "packages" / "expansions" / "fan_pwm_sx1509.yaml"
FAN_PWM_PRODUCT = REPO_ROOT / "products" / "sense360-ceiling-poe-fanpwm.yaml"
FAN_PWM_COMPILE_ONLY = REPO_ROOT / "products" / "compile-only" / "ceiling-poe-fanpwm.yaml"

PRODUCT_CATALOG_JSON = REPO_ROOT / "config" / "product-catalog.json"
HARDWARE_CATALOG_JSON = REPO_ROOT / "config" / "hardware-catalog.json"
WEBFLASH_BUILDS_JSON = REPO_ROOT / "config" / "webflash-builds.json"

# Pre-existing SX1509 / pulse_counter compile-proof fixture and test —
# this PR must not delete or weaken them. They are evidence for the
# rule, not the current fan-path binding.
SX1509_PROOF_FIXTURE = REPO_ROOT / "tests" / "esphome" / "sx1509_pulse_counter_proof.yaml"
SX1509_PROOF_TEST = REPO_ROOT / "tests" / "test_sx1509_tach_pulse_counter_proof.py"

# Schematic-printed native ESP32-S3 GPIO terminations on the refreshed
# canonical S360-100-R4 sheet. Every value below is the value recorded
# in docs/hardware/s360-100-core-architecture.md § Pin allocation
# table — this test asserts that the new fan-GPIO-map doc records the
# same native pin for each net.
EXPECTED_FAN_GPIO_MAP: Dict[str, str] = {
    "TachIO": "IO16",
    "Pul_Cou1": "IO17",
    "Pul_Cou2": "IO18",
    "Pul_Cou3": "IO46",
    "Pul_Cou4": "IO9",
    "TachPMW1": "IO10",
    "TachPMW2": "IO11",
    "TachPMW3": "IO12",
    "TachPMW4": "IO39",
}

FANPWM_CONFIG_STRING = "Ceiling-POE-FanPWM"
FANPWM_PRODUCT_REL = "products/sense360-ceiling-poe-fanpwm.yaml"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _fanpwm_catalog_entry() -> Dict[str, Any]:
    catalog = _load_json(PRODUCT_CATALOG_JSON)
    for entry in catalog.get("products", []):
        if entry.get("config_string") == FANPWM_CONFIG_STRING:
            return entry
    raise AssertionError(
        f"missing {FANPWM_CONFIG_STRING!r} entry in "
        f"config/product-catalog.json"
    )


class FanGpioMapDocExistsTests(unittest.TestCase):
    """Rule (1) preamble: the canonical fan GPIO map doc exists and
    declares S360-100-NATIVE-FAN-GPIO-MAP-001 as its identifier."""

    def test_doc_file_exists(self) -> None:
        self.assertTrue(
            FAN_GPIO_MAP_DOC.is_file(),
            "docs/hardware/s360-100-native-fan-gpio-map.md must exist "
            "as the canonical S360-100 / S360-311 native fan GPIO map "
            "(S360-100-NATIVE-FAN-GPIO-MAP-001).",
        )

    def test_doc_declares_identifier(self) -> None:
        text = FAN_GPIO_MAP_DOC.read_text()
        self.assertIn(
            "S360-100-NATIVE-FAN-GPIO-MAP-001",
            text,
            "fan GPIO map doc must declare the "
            "S360-100-NATIVE-FAN-GPIO-MAP-001 identifier.",
        )

    def test_doc_says_documentation_only(self) -> None:
        text = FAN_GPIO_MAP_DOC.read_text().lower()
        self.assertIn(
            "documentation only",
            text,
            "fan GPIO map doc must explicitly say it is documentation "
            "only (no firmware / release / WebFlash flip).",
        )


class FanGpioMapNativePinsTests(unittest.TestCase):
    """Rule (1): the fan GPIO map doc records every required native
    ESP32-S3 GPIO and the rule cannot be silently degraded.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = FAN_GPIO_MAP_DOC.read_text()

    def test_doc_records_every_expected_native_pin(self) -> None:
        for net, pin in EXPECTED_FAN_GPIO_MAP.items():
            with self.subTest(net=net, pin=pin):
                # The doc must mention both the net name and its
                # schematic-printed native ESP32-S3 GPIO.
                self.assertIn(
                    net,
                    self.text,
                    f"fan GPIO map doc must record the {net!r} fan net.",
                )
                self.assertRegex(
                    self.text,
                    rf"\b{re.escape(pin)}\b",
                    f"fan GPIO map doc must record the {net!r} "
                    f"schematic-printed native ESP32-S3 GPIO {pin!r}.",
                )

    def test_doc_requires_native_esp32_pin_family(self) -> None:
        text = self.text.lower()
        self.assertIn(
            "native esp32",
            text,
            "fan GPIO map doc must positively require the native "
            "ESP32-S3 pin family for fan PWM control and tach / "
            "pulse-counter inputs.",
        )

    def test_doc_lists_pwm_capable_and_interrupt_capable_constraints(self) -> None:
        text = self.text.lower()
        self.assertIn(
            "pwm-capable",
            text,
            "fan GPIO map doc must record the PWM-capable native ESP32 "
            "pin-family constraint for TachPMW1..4.",
        )
        self.assertIn(
            "interrupt-capable",
            text,
            "fan GPIO map doc must record the interrupt-capable native "
            "ESP32 pin-family constraint for tach / pulse counter.",
        )

    def test_doc_mentions_connector_pair(self) -> None:
        # Connector labels must be present: Sense360 Core J6 (13-pin)
        # and S360-311 module J3 (13-pin). The doc must record the
        # connector mapping (Required work item #1).
        for label in ("J6", "J3", "13-pin"):
            with self.subTest(label=label):
                self.assertIn(
                    label,
                    self.text,
                    f"fan GPIO map doc must record the {label!r} "
                    f"connector identity for the Core <-> S360-311 "
                    f"13-pin harness.",
                )

    def test_doc_does_not_invent_other_native_pins(self) -> None:
        # Guardrail: in the canonical per-net map (single net name per
        # row, followed by exactly one PWM-capable / interrupt-capable
        # native pin), the doc must record the schematic-printed value
        # and only that value. We scope the check to rows where the
        # exact net name appears with a `|` table separator and at most
        # one `IO\d+` token close to it, so summary rows that list
        # multiple Pul_Cou or TachPMW pins together (e.g. "Pul_Cou1..4")
        # are not matched by this guard.
        per_row = re.compile(
            r"\|\s*[^|\n]*`(Pul_Cou\d|TachPMW\d|TachIO)`[^|\n]*\|[^|\n]*\|\s*`(IO\d+)`",
        )
        matches = per_row.findall(self.text)
        self.assertGreaterEqual(
            len(matches),
            len(EXPECTED_FAN_GPIO_MAP),
            "fan GPIO map doc canonical per-net table must record at "
            "least one row per net (TachIO + Pul_Cou1..4 + TachPMW1..4).",
        )
        for net, pin in matches:
            with self.subTest(net=net, pin=pin):
                self.assertEqual(
                    pin,
                    EXPECTED_FAN_GPIO_MAP[net],
                    f"canonical per-net row records {net!r} against "
                    f"{pin!r}, which disagrees with the "
                    f"schematic-printed {EXPECTED_FAN_GPIO_MAP[net]!r} "
                    f"value. No GPIO numbers may be invented.",
                )

    def test_doc_marks_bench_verified_no(self) -> None:
        # The map records schematic-printed values, not bench-verified
        # ones. The "Bench-verified?" column must consistently say No.
        # We assert that the doc clearly states the values are NOT
        # bench-verified.
        text_low = self.text.lower()
        self.assertIn(
            "not bench-verified",
            text_low,
            "fan GPIO map doc must explicitly state the recorded "
            "native ESP32-S3 GPIO terminations are not bench-verified.",
        )


class FanGpioMapAgreesWithCoreArchitectureTests(unittest.TestCase):
    """Rule (4): the new doc and the Core architecture doc agree on
    every native ESP32-S3 GPIO termination for the fan path.
    """

    def test_core_architecture_doc_records_same_pins(self) -> None:
        core_text = CORE_ARCHITECTURE_DOC.read_text()
        for net, pin in EXPECTED_FAN_GPIO_MAP.items():
            with self.subTest(net=net, pin=pin):
                # Both docs must mention the same net + native pin
                # together; we do this with a contained-pair pattern
                # so a drift in one record without the other surfaces.
                pattern = rf"{re.escape(net)}[^\n]{{0,200}}\b{re.escape(pin)}\b"
                self.assertRegex(
                    core_text,
                    pattern,
                    f"Core architecture doc must record {net!r} -> "
                    f"{pin!r} (matches the fan GPIO map doc).",
                )


class FanPwmYamlLegacySupersededLabellingTests(unittest.TestCase):
    """Rule (2): the FanPWM YAMLs carry the legacy / superseded SX1509
    fan-path labelling so the SX1509 path cannot be silently presented
    as the current FanPWM implementation.
    """

    LEGACY_BANNERS = (
        "LEGACY / SUPERSEDED SX1509 FAN PATH",
        "S360-100-NATIVE-FAN-GPIO-MAP-001",
    )

    def _assert_carries_banners(self, path: Path) -> None:
        text = path.read_text()
        for banner in self.LEGACY_BANNERS:
            with self.subTest(file=path.name, banner=banner):
                self.assertIn(
                    banner,
                    text,
                    f"{path.name} must carry the {banner!r} header "
                    f"banner so the SX1509-routed FanPWM control / tach "
                    f"path is classified legacy / superseded against "
                    f"the canonical native ESP32-S3 GPIO map.",
                )

    def test_fan_pwm_package_carries_legacy_banner(self) -> None:
        self._assert_carries_banners(FAN_PWM_PACKAGE)

    def test_fan_pwm_sx1509_binding_carries_legacy_banner(self) -> None:
        self._assert_carries_banners(FAN_PWM_SX1509_BINDING)

    def test_fan_pwm_product_carries_legacy_banner(self) -> None:
        self._assert_carries_banners(FAN_PWM_PRODUCT)

    def test_fan_pwm_compile_only_carries_legacy_banner(self) -> None:
        self._assert_carries_banners(FAN_PWM_COMPILE_ONLY)


class FanPwmStaysOutOfReleaseAndWebFlashTests(unittest.TestCase):
    """Rule (3): no current FanPWM release / WebFlash path uses
    SX1509 for PWM or tach. The catalog / build-matrix rows confirm
    the FanPWM lane stays release-blocked and WebFlash-blocked.
    """

    def test_webflash_builds_does_not_contain_fanpwm_token(self) -> None:
        text = WEBFLASH_BUILDS_JSON.read_text()
        self.assertNotIn(
            "FanPWM",
            text,
            "config/webflash-builds.json must not contain the FanPWM "
            "token — the current FanPWM hardware path is not WebFlash-"
            "exposed and the legacy SX1509 composition must not be "
            "presented as a current WebFlash-shippable build.",
        )

    def test_fanpwm_catalog_entry_keeps_webflash_build_matrix_false(self) -> None:
        entry = _fanpwm_catalog_entry()
        self.assertEqual(
            entry.get("webflash_build_matrix"),
            False,
            f"FanPWM catalog entry must keep "
            f"webflash_build_matrix: false (legacy SX1509 composition "
            f"is not release-eligible). Got "
            f"{entry.get('webflash_build_matrix')!r}.",
        )

    def test_fanpwm_catalog_entry_has_no_artifact_name(self) -> None:
        entry = _fanpwm_catalog_entry()
        self.assertNotIn(
            "artifact_name",
            entry,
            "FanPWM catalog entry must not declare artifact_name — no "
            "release artifact is built against the legacy SX1509 "
            "composition.",
        )

    def test_fanpwm_catalog_entry_has_no_webflash_wrapper(self) -> None:
        entry = _fanpwm_catalog_entry()
        self.assertNotIn(
            "webflash_wrapper",
            entry,
            "FanPWM catalog entry must not declare a webflash_wrapper "
            "— the legacy SX1509 composition is not WebFlash-exposed.",
        )

    def test_fanpwm_catalog_entry_status_is_not_release_eligible(self) -> None:
        entry = _fanpwm_catalog_entry()
        self.assertNotIn(
            entry.get("status"),
            {"production", "preview"},
            f"FanPWM catalog entry must not be production or preview "
            f"— those statuses authorise WebFlash exposure. Got "
            f"status={entry.get('status')!r}.",
        )

    def test_fanpwm_catalog_entry_keeps_rpm_supported_false(self) -> None:
        entry = _fanpwm_catalog_entry()
        # rpm_supported is either explicitly False or absent; the rule
        # is "must not assert True".
        self.assertNotEqual(
            entry.get("rpm_supported"),
            True,
            "FanPWM catalog entry must not claim rpm_supported: true "
            "— no measured RPM evidence exists, and the legacy SX1509 "
            "tach path is compile-proven unable to back an ESPHome "
            "pulse_counter.",
        )

    def test_no_active_product_yaml_binds_pulse_counter_on_sx1509(self) -> None:
        # Smoke check: neither the FanPWM product YAML nor the
        # compile-only skeleton declares a pulse_counter on an
        # SX1509-routed pin. The architectural rule has its own
        # comprehensive guard in
        # tests/test_native_tach_pulse_pin_strategy.py; this test
        # narrows it to the FanPWM lane.
        for path in (FAN_PWM_PRODUCT, FAN_PWM_COMPILE_ONLY):
            with self.subTest(file=path.name):
                text = path.read_text()
                # Drop comment-only lines so banner wording doesn't
                # trigger a false positive (the banner mentions
                # "pulse_counter" in prose).
                active = []
                for line in text.splitlines():
                    stripped = line.lstrip()
                    if not stripped or stripped.startswith("#"):
                        continue
                    active.append(line)
                joined = "\n".join(active)
                self.assertNotIn(
                    "pulse_counter",
                    joined,
                    f"{path.name} must not declare pulse_counter on any "
                    f"active (non-comment) line — the legacy SX1509 "
                    f"fan path is not RPM-capable, and the native ESP32 "
                    f"re-bind is a separate firmware PR.",
                )


class HistoricalSx1509ProofIsPreservedTests(unittest.TestCase):
    """Rule (3) corollary: the historical SX1509 + pulse_counter
    compile/config proof is kept in place as evidence for the
    architectural rule. This PR must not delete or weaken it.
    """

    def test_proof_fixture_exists(self) -> None:
        self.assertTrue(
            SX1509_PROOF_FIXTURE.is_file(),
            "tests/esphome/sx1509_pulse_counter_proof.yaml must remain "
            "in place as the SX1509 + pulse_counter compile/config "
            "proof fixture — it is evidence for the architectural rule, "
            "not the current FanPWM hardware path.",
        )

    def test_proof_test_module_exists(self) -> None:
        self.assertTrue(
            SX1509_PROOF_TEST.is_file(),
            "tests/test_sx1509_tach_pulse_counter_proof.py must remain "
            "in place — it is the authoritative compile/config proof "
            "guard for the SX1509 / pulse_counter rejection.",
        )


class FanGpioMapDocGuardrailsTests(unittest.TestCase):
    """Rule (3): the canonical fan GPIO map doc carries explicit
    do-not-change guardrails so it cannot silently authorise a
    release / WebFlash flip on its own.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.text_lower = FAN_GPIO_MAP_DOC.read_text().lower()

    def test_doc_says_no_webflash_flip(self) -> None:
        # Either "webflash" + "blocked" or an explicit
        # "no webflash_build_matrix flip" / "stay blocked" wording.
        self.assertRegex(
            self.text_lower,
            r"webflash[^\n]{0,400}(?:blocked|do not|must not|stay)",
            "fan GPIO map doc must explicitly forbid a WebFlash "
            "exposure flip / build-matrix flip / artifact addition.",
        )

    def test_doc_says_no_firmware_publish(self) -> None:
        # "publish firmware" must appear as a forbidden / negated
        # action somewhere in the doc. We collapse whitespace so the
        # phrase survives the "It does not:\n\n- publish firmware,"
        # bulleted form.
        collapsed = re.sub(r"\s+", " ", self.text_lower)
        self.assertRegex(
            collapsed,
            r"(?:does not|do not|must not|not)[^|]{0,200}publish firmware",
            "fan GPIO map doc must explicitly state it does not "
            "publish firmware.",
        )

    def test_doc_says_no_release_artifact(self) -> None:
        collapsed = re.sub(r"\s+", " ", self.text_lower)
        self.assertRegex(
            collapsed,
            r"(?:does not|do not|must not|not)[^|]{0,200}release artifact",
            "fan GPIO map doc must explicitly state it does not "
            "create a release artifact.",
        )

    def test_doc_says_s360_311_stays_cataloged_unverified(self) -> None:
        self.assertIn(
            "cataloged_unverified",
            self.text_lower,
            "fan GPIO map doc must explicitly state S360-311 stays "
            "schematic_status: cataloged_unverified.",
        )

    def test_doc_says_no_invented_gpio_numbers(self) -> None:
        # The guardrail "no GPIO numbers are invented here" pin.
        self.assertRegex(
            self.text_lower,
            r"(?:are not invented|not invented|no gpio numbers are invented|do not invent|are schematic-printed)",
            "fan GPIO map doc must explicitly state no GPIO numbers "
            "are invented (Required work item: 'Do not invent GPIO "
            "numbers.').",
        )

    def test_doc_says_sx1509_not_removed_globally(self) -> None:
        # The doc must not silently authorise a global SX1509 deletion.
        # We assert that it mentions SX1509 retention for historical /
        # superseded context or non-fan signals.
        self.assertRegex(
            self.text_lower,
            r"sx1509[^\n]{0,400}(?:historical|superseded|non-fan)",
            "fan GPIO map doc must explicitly state SX1509 references "
            "may remain for historical / superseded context or for "
            "non-fan signals (the SX1509 must not be removed globally).",
        )


class S360_311_HardwareCatalogUnchangedTests(unittest.TestCase):
    """S360-311 hardware catalog row is not promoted by this PR."""

    def test_s360_311_stays_not_verified(self) -> None:
        data = _load_json(HARDWARE_CATALOG_JSON)
        entries = data.get("items", [])
        s311 = next((e for e in entries if e.get("sku") == "S360-311"), None)
        self.assertIsNotNone(
            s311, "S360-311 row must exist in hardware catalog."
        )
        self.assertNotEqual(
            s311.get("schematic_status"),
            "verified",
            "S360-311 must not be `verified` — bench / current / "
            "thermal evidence and firmware re-bind against the native "
            "ESP32-S3 GPIO map are required first "
            "(S360-100-NATIVE-FAN-GPIO-MAP-001 is documentation-only).",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

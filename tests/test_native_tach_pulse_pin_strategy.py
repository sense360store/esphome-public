#!/usr/bin/env python3
"""S360-100-NATIVE-TACH-PULSE-001 — native ESP32 GPIO is required for
tach / pulse-counter inputs.

This module pins the architectural rule recorded in
``docs/hardware/s360-100-native-tach-pulse-strategy.md``:

1. **No package / product YAML maps a `pulse_counter` (or other tach /
   pulse-counter) pin through an `sx1509:` expander key.** The pre-existing
   ``tests/test_sx1509_tach_pulse_counter_proof.py`` proves at the
   ``esphome config`` layer that the ESPHome schema rejects an SX1509 pin
   under ``sensor.pulse_counter.pin``; this guard enforces the same rule at
   the repo level so a YAML drift cannot land that needs the live compile
   to catch.

2. **Any docs / catalog text that mentions S360-311 tach / RPM / pulse
   counter requires native ESP32 GPIO.** Forbidden positive claims like
   "SX1509 pulse counter", "SX1509 fan tach", "SX1509-backed tach", or
   "SX1509-backed RPM" do not appear as architecture claims.

3. **SX1509 PWM-drive output and SX1509 tach / pulse-counter are explicitly
   separated.** The architecture-rule strategy doc and the SX1509
   binding-only package both affirm PWM-drive output is supported while
   forbidding tach / `pulse_counter` on the expander.

4. **S360-311 does not claim RPM / tach readiness anywhere in the machine-
   readable config until measured native-GPIO tach evidence exists.**
   ``config/product-catalog.json``, ``config/hardware-catalog.json``, and
   ``config/webflash-builds.json`` must not assert RPM / tach support for
   ``S360-311`` while the architectural rule's pending pin-allocation table
   is unresolved.

Run with::

    python3 tests/test_native_tach_pulse_pin_strategy.py
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from typing import Iterable, List

REPO_ROOT = Path(__file__).resolve().parent.parent

STRATEGY_DOC = REPO_ROOT / "docs" / "hardware" / "s360-100-native-tach-pulse-strategy.md"
SX1509_BINDING = REPO_ROOT / "packages" / "expansions" / "fan_pwm_sx1509.yaml"
FAN_PWM_PACKAGE = REPO_ROOT / "packages" / "expansions" / "fan_pwm.yaml"

PACKAGES_DIR = REPO_ROOT / "packages"
PRODUCTS_DIR = REPO_ROOT / "products"

HARDWARE_CATALOG_JSON = REPO_ROOT / "config" / "hardware-catalog.json"
PRODUCT_CATALOG_JSON = REPO_ROOT / "config" / "product-catalog.json"
WEBFLASH_BUILDS_JSON = REPO_ROOT / "config" / "webflash-builds.json"

# The PROOF fixture itself is deliberately a violation (it exists to prove
# the SX1509 + pulse_counter rejection). Exclude it from the structural
# scan; the dedicated PWM-SX1509-TACH-PROOF-001 test guards its shape.
PROOF_FIXTURE = REPO_ROOT / "tests" / "esphome" / "sx1509_pulse_counter_proof.yaml"


def _iter_yaml(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*.yaml")):
        if path == PROOF_FIXTURE:
            continue
        yield path


def _strip_yaml_comments(text: str) -> str:
    """Drop full-line YAML comments and inline `# ...` tails so the
    `pulse_counter` + `sx1509:` structural scan only sees actual mapping
    nodes, not prose in header docblocks.
    """
    out_lines: List[str] = []
    for line in text.splitlines():
        # Drop pure comment lines.
        if line.lstrip().startswith("#"):
            out_lines.append("")
            continue
        # Strip inline comment tails. YAML doesn't allow `#` inside a
        # bare scalar (it does inside quoted strings), so this naive
        # split is adequate for our structural pattern check.
        if "#" in line:
            head, _, _ = line.partition("#")
            out_lines.append(head.rstrip())
        else:
            out_lines.append(line)
    return "\n".join(out_lines)


# Match a `pulse_counter` block whose `pin:` value is an `sx1509:` mapping.
# Tolerates arbitrary keys between `platform: pulse_counter` and the `pin:`.
_PULSE_COUNTER_SX1509_PIN = re.compile(
    r"platform:\s*pulse_counter\b"
    r"(?:.*\n)*?"
    r"\s*pin:\s*\n"
    r"\s*sx1509:\s*\w+",
    re.MULTILINE,
)


class NoPulseCounterOnSx1509InPackagesOrProductsTests(unittest.TestCase):
    """Rule (1): no `pulse_counter` pin routes through `sx1509:`."""

    def test_packages_have_no_sx1509_pulse_counter_pin(self) -> None:
        for path in _iter_yaml(PACKAGES_DIR):
            with self.subTest(file=path.relative_to(REPO_ROOT).as_posix()):
                text = _strip_yaml_comments(path.read_text())
                self.assertIsNone(
                    _PULSE_COUNTER_SX1509_PIN.search(text),
                    "`pulse_counter` must not bind an `sx1509:` pin "
                    "(S360-100-NATIVE-TACH-PULSE-001). The SX1509 pin "
                    "schema is compile-proven invalid under "
                    "`sensor.pulse_counter.pin` "
                    "(PWM-SX1509-TACH-PROOF-001); tach / pulse-counter "
                    "inputs must terminate on native ESP32 GPIO.",
                )

    def test_products_have_no_sx1509_pulse_counter_pin(self) -> None:
        for path in _iter_yaml(PRODUCTS_DIR):
            with self.subTest(file=path.relative_to(REPO_ROOT).as_posix()):
                text = _strip_yaml_comments(path.read_text())
                self.assertIsNone(
                    _PULSE_COUNTER_SX1509_PIN.search(text),
                    "`pulse_counter` must not bind an `sx1509:` pin "
                    "(S360-100-NATIVE-TACH-PULSE-001).",
                )


class StrategyDocShapeTests(unittest.TestCase):
    """Rule (3): the strategy doc separates PWM-drive output from
    tach / pulse-counter support, and pins the native-GPIO requirement.
    """

    def test_strategy_doc_exists(self) -> None:
        self.assertTrue(
            STRATEGY_DOC.is_file(),
            "docs/hardware/s360-100-native-tach-pulse-strategy.md must "
            "exist — it is the canonical S360-100 native ESP32 tach / "
            "pulse-counter pin strategy.",
        )

    def test_strategy_doc_names_native_gpio_rule(self) -> None:
        text = STRATEGY_DOC.read_text().lower()
        self.assertIn("native esp32", text)
        self.assertIn("pulse_counter", text)
        self.assertIn("sx1509", text)
        # Affirmative native-GPIO requirement.
        self.assertRegex(
            text,
            r"tach\s*/\s*pulse-counter inputs\s+must\s+(?:land on|terminate on|use)\s+(?:a\s+)?native esp32",
            "Strategy doc must positively require native ESP32 GPIO for "
            "tach / pulse-counter inputs.",
        )

    def test_strategy_doc_forbids_sx1509_for_tach(self) -> None:
        text = STRATEGY_DOC.read_text().lower()
        # Either "must not" or "forbidden" wording, anywhere near "sx1509"
        # and "tach"/"pulse_counter"/"pulse counter".
        self.assertRegex(
            text,
            r"sx1509[^\n]{0,200}\b(?:must not|forbidden|cannot|not be used)\b",
            "Strategy doc must forbid SX1509 for tach / pulse-counter.",
        )

    def test_strategy_doc_separates_pwm_drive_from_tach(self) -> None:
        text = STRATEGY_DOC.read_text().lower()
        # PWM-drive output is positively supported on a single line near
        # the word "pwm" — the same shape the proof test expects.
        self.assertRegex(
            text,
            r"pwm[^\n]{0,200}is supported",
            "Strategy doc must affirm SX1509 PWM-drive output IS supported "
            "(separate from tach / pulse-counter support).",
        )

    def test_strategy_doc_cites_proof(self) -> None:
        text = STRATEGY_DOC.read_text()
        self.assertIn(
            "PWM-SX1509-TACH-PROOF-001",
            text,
            "Strategy doc must cite the PWM-SX1509-TACH-PROOF-001 "
            "compile/config proof as the evidence for the rule.",
        )
        self.assertIn(
            "[sx1509] is an invalid option for [pin]",
            text,
            "Strategy doc must quote the captured `esphome config` "
            "rejection so the rule is traceable to evidence, not "
            "inference.",
        )


class NoExpanderTachClaimsInDocsTests(unittest.TestCase):
    """Rule (2): docs and product-catalog notes must not assert that the
    SX1509 (or any other expander-class device) backs fan tach / RPM /
    pulse counting as a positive capability claim.
    """

    # Phrasings that would represent an incorrect "expander does tach"
    # claim. The check is case-insensitive and tolerant of common
    # punctuation between the words.
    FORBIDDEN_POSITIVE_CLAIMS = [
        r"sx1509[^.\n]{0,40}\bfan tach\b",
        r"sx1509[^.\n]{0,40}\btach (?:input|sensor|rpm|support)\b",
        r"sx1509[^.\n]{0,40}\bpulse[ _-]?counter (?:support|input|backed)\b",
        r"sx1509[^.\n]{0,40}\b(?:backs|supports) (?:tach|pulse[ _-]?counter|rpm)\b",
        r"\bexpander[^.\n]{0,40}\bfan tach\b",
        r"\bexpander[^.\n]{0,40}\b(?:backs|supports) (?:tach|pulse[ _-]?counter|rpm)\b",
        r"\bexpander[ -]based tach\b",
    ]

    # The strategy doc itself is intentionally excluded: it MUST quote
    # the forbidden forms in order to define the rule and label them as
    # forbidden. Every other doc is scanned for the positive (claim)
    # form of the same phrasing.
    # docs/product-readiness-matrix.md, docs/blocker-burndown.md, and
    # docs/hardware/package-readiness-matrix.md were archived under
    # DOCS-DISPOSITION-001 (see docs/archive-index.md) and dropped out of
    # this scan; the rule still holds for the kept board docs.
    DOC_TARGETS = [
        REPO_ROOT / "docs" / "hardware" / "s360-100-r4-core.md",
        REPO_ROOT / "docs" / "hardware" / "s360-311-r4-fanpwm.md",
    ]

    def test_no_forbidden_expander_tach_claims(self) -> None:
        for path in self.DOC_TARGETS:
            text = path.read_text().lower()
            for pat in self.FORBIDDEN_POSITIVE_CLAIMS:
                with self.subTest(
                    file=path.relative_to(REPO_ROOT).as_posix(), pattern=pat
                ):
                    self.assertIsNone(
                        re.search(pat, text),
                        f"{path.name} must not assert "
                        f"expander-based tach / pulse-counter / RPM "
                        f"(pattern {pat!r}). Tach / pulse-counter "
                        f"inputs must terminate on native ESP32 GPIO "
                        f"(S360-100-NATIVE-TACH-PULSE-001).",
                    )

    def test_product_catalog_notes_have_no_forbidden_expander_tach_claims(self) -> None:
        text = PRODUCT_CATALOG_JSON.read_text().lower()
        for pat in self.FORBIDDEN_POSITIVE_CLAIMS:
            with self.subTest(pattern=pat):
                self.assertIsNone(
                    re.search(pat, text),
                    f"config/product-catalog.json must not assert "
                    f"expander-based tach / pulse-counter / RPM "
                    f"(pattern {pat!r}).",
                )


class S360_311_DoesNotClaimTachReadinessTests(unittest.TestCase):
    """Rule (4): S360-311 must not claim RPM / tach readiness in config."""

    def _load_json(self, path: Path) -> dict:
        with path.open() as fh:
            return json.load(fh)

    def test_hardware_catalog_s360_311_is_not_verified(self) -> None:
        data = self._load_json(HARDWARE_CATALOG_JSON)
        entries = data.get("items", [])
        s311 = next((e for e in entries if e.get("sku") == "S360-311"), None)
        self.assertIsNotNone(s311, "S360-311 row must exist in hardware catalog.")
        self.assertNotEqual(
            s311.get("schematic_status"),
            "verified",
            "S360-311 must not be `verified` until measured native-GPIO "
            "tach evidence and the bench / current / thermal gates exist "
            "(S360-100-NATIVE-TACH-PULSE-001 + PWM-BLOCKER-RECLASSIFY-001).",
        )

    def test_product_catalog_fanpwm_product_does_not_claim_rpm(self) -> None:
        data = self._load_json(PRODUCT_CATALOG_JSON)
        for entry in data.get("products", []):
            config = entry.get("config_string") or entry.get("name")
            if not config or "FanPWM" not in str(config):
                continue
            with self.subTest(config=config):
                # No positive RPM-support flag.
                self.assertNotEqual(
                    entry.get("rpm_supported"),
                    True,
                    f"{config}: rpm_supported must not be True until "
                    f"native-GPIO per-fan tach evidence exists.",
                )
                # No webflash exposure.
                self.assertFalse(
                    bool(entry.get("webflash_build_matrix")),
                    f"{config}: webflash_build_matrix must stay false "
                    f"(WebFlash exposure is blocked).",
                )
                self.assertIn(
                    entry.get("status"),
                    {"hardware-pending", "design-pending", "blocked",
                     "compile-only", "manual-candidate-only"},
                    f"{config}: status must stay non-stable; got "
                    f"{entry.get('status')!r}.",
                )

    def test_webflash_builds_has_no_fanpwm_entry(self) -> None:
        data = self._load_json(WEBFLASH_BUILDS_JSON)
        builds: List[dict] = data.get("builds", []) if isinstance(data, dict) else []
        for row in builds:
            cfg = row.get("config_string", "")
            with self.subTest(config_string=cfg):
                self.assertNotIn(
                    "FanPWM",
                    cfg,
                    f"FanPWM must not appear in any WebFlash build "
                    f"(`{cfg}`) until measured native-GPIO tach evidence + "
                    f"WebFlash live-classification land.",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)

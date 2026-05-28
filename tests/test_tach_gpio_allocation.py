#!/usr/bin/env python3
"""S360-100-TACH-GPIO-ALLOCATION-001 — pin the native ESP32-S3 GPIO
allocation recorded for the FanPWM tach / pulse-counter inputs.

The canonical S360-100-R4 schematic (committed under
``S360-100-NATIVE-TACH-PULSE-001`` R4 refresh) terminates each per-fan
tach / pulse-counter / PWM-drive net directly at a native ESP32-S3
module pin. This module checks that the **same** per-fan native GPIO
mapping is recorded on every hardware-reference / audit / architecture
doc that records it, and that the architectural rule pinned by
``tests/test_native_tach_pulse_pin_strategy.py`` (no
``pulse_counter`` ↔ ``sx1509:`` binding; no FanPWM in
``config/webflash-builds.json``) still holds.

Run with::

    python3 tests/test_tach_gpio_allocation.py
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent

CORE_HW_DOC = REPO_ROOT / "docs" / "hardware" / "s360-100-r4-core.md"
PWM_HW_DOC = REPO_ROOT / "docs" / "hardware" / "s360-311-r4-pwm.md"
STRATEGY_DOC = REPO_ROOT / "docs" / "hardware" / "s360-100-native-tach-pulse-strategy.md"
ARCHITECTURE_DOC = REPO_ROOT / "docs" / "hardware" / "s360-100-core-architecture.md"
BLOCKER_DOC = REPO_ROOT / "docs" / "blocker-burndown.md"
READINESS_DOC = REPO_ROOT / "docs" / "product-readiness-matrix.md"

PACKAGES_DIR = REPO_ROOT / "packages"
PRODUCTS_DIR = REPO_ROOT / "products"

PRODUCT_CATALOG_JSON = REPO_ROOT / "config" / "product-catalog.json"
HARDWARE_CATALOG_JSON = REPO_ROOT / "config" / "hardware-catalog.json"
WEBFLASH_BUILDS_JSON = REPO_ROOT / "config" / "webflash-builds.json"

# The proof fixture is deliberately a violation; exclude.
PROOF_FIXTURE = REPO_ROOT / "tests" / "esphome" / "sx1509_pulse_counter_proof.yaml"

# Canonical S360-100-TACH-GPIO-ALLOCATION-001 mapping, taken from the
# committed canonical S360-100-R4.pdf sheet (SHA256
# 4c9e8b06d129fbb55f61e143b648e03762d06cb4dc67fe3120c268cd3a4bdf16).
TACH_PULSE_COUNTER_ALLOCATION: Dict[str, str] = {
    "TachIO": "IO16",
    "Pul_Cou1": "IO17",
    "Pul_Cou2": "IO18",
    "Pul_Cou3": "IO46",
    "Pul_Cou4": "IO9",
}

PWM_DRIVE_ALLOCATION: Dict[str, str] = {
    "TachPMW1": "IO10",
    "TachPMW2": "IO11",
    "TachPMW3": "IO12",
    "TachPMW4": "IO39",
}

ALL_ALLOCATION: Dict[str, str] = {**TACH_PULSE_COUNTER_ALLOCATION, **PWM_DRIVE_ALLOCATION}

# ESP32-S3 octal-SPI PSRAM reservation per
# docs/hardware/s360-100-r4-core.md §ESP32-S3 pin and net mapping.
PSRAM_RESERVED_GPIOS = {"IO35", "IO36", "IO37"}


def _iter_yaml(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*.yaml")):
        if path == PROOF_FIXTURE:
            continue
        yield path


_PULSE_COUNTER_SX1509_PIN = re.compile(
    r"platform:\s*pulse_counter\b"
    r"(?:.*\n)*?"
    r"\s*pin:\s*\n"
    r"\s*sx1509:\s*\w+",
    re.MULTILINE,
)


def _strip_yaml_comments(text: str) -> str:
    out: List[str] = []
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            out.append("")
            continue
        if "#" in line:
            head, _, _ = line.partition("#")
            out.append(head.rstrip())
        else:
            out.append(line)
    return "\n".join(out)


def _doc_pairs_present(text: str, pairs: Iterable[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """Return the pairs (net, gpio) where the doc does NOT mention both
    `net` and `gpio` together on at least one line."""
    missing: List[Tuple[str, str]] = []
    lines = text.splitlines()
    for net, gpio in pairs:
        hit = False
        for line in lines:
            if net in line and gpio in line:
                hit = True
                break
        if not hit:
            missing.append((net, gpio))
    return missing


class TachGpioAllocationOnCoreHardwareDocTests(unittest.TestCase):
    """The Core hardware reference doc must record the per-net native
    GPIO allocation in the S360-100-TACH-GPIO-ALLOCATION-001 section."""

    def setUp(self) -> None:
        self.text = CORE_HW_DOC.read_text()

    def test_section_heading_exists(self) -> None:
        self.assertIn(
            "S360-100-TACH-GPIO-ALLOCATION-001",
            self.text,
            f"{CORE_HW_DOC.name} must record the "
            "S360-100-TACH-GPIO-ALLOCATION-001 section.",
        )

    def test_every_tach_net_records_its_native_gpio(self) -> None:
        missing = _doc_pairs_present(self.text, TACH_PULSE_COUNTER_ALLOCATION.items())
        self.assertEqual(
            missing,
            [],
            f"{CORE_HW_DOC.name} must record the native ESP32-S3 GPIO "
            f"for every tach / pulse-counter net (missing pairs: {missing}).",
        )

    def test_every_pwm_drive_net_records_its_native_gpio(self) -> None:
        missing = _doc_pairs_present(self.text, PWM_DRIVE_ALLOCATION.items())
        self.assertEqual(
            missing,
            [],
            f"{CORE_HW_DOC.name} must record the native ESP32-S3 GPIO "
            f"for every PWM-drive net (missing pairs: {missing}).",
        )

    def test_no_psram_reserved_gpio_used_for_tach_or_pwm(self) -> None:
        for net, gpio in ALL_ALLOCATION.items():
            with self.subTest(net=net, gpio=gpio):
                self.assertNotIn(
                    gpio,
                    PSRAM_RESERVED_GPIOS,
                    f"{net} must not use a PSRAM-reserved GPIO "
                    f"({PSRAM_RESERVED_GPIOS}); got {gpio}.",
                )


class TachGpioAllocationOnPwmModuleDocTests(unittest.TestCase):
    """The FanPWM module audit doc must mirror the Core-side allocation."""

    def setUp(self) -> None:
        self.text = PWM_HW_DOC.read_text()

    def test_section_heading_exists(self) -> None:
        self.assertIn(
            "S360-100-TACH-GPIO-ALLOCATION-001",
            self.text,
            f"{PWM_HW_DOC.name} must record the "
            "S360-100-TACH-GPIO-ALLOCATION-001 Core-side allocation section.",
        )

    def test_every_net_records_its_native_gpio(self) -> None:
        missing = _doc_pairs_present(self.text, ALL_ALLOCATION.items())
        self.assertEqual(
            missing,
            [],
            f"{PWM_HW_DOC.name} must mirror the per-net native ESP32-S3 "
            f"GPIO allocation (missing pairs: {missing}).",
        )


class TachGpioAllocationCrossReferencedTests(unittest.TestCase):
    """Strategy doc, architecture doc, blocker burndown, and readiness
    matrix must all cite S360-100-TACH-GPIO-ALLOCATION-001."""

    def test_strategy_doc_cites_the_allocation(self) -> None:
        text = STRATEGY_DOC.read_text()
        self.assertIn(
            "S360-100-TACH-GPIO-ALLOCATION-001",
            text,
            f"{STRATEGY_DOC.name} must cite S360-100-TACH-GPIO-ALLOCATION-001 "
            "as the record of the schematic-proven native-GPIO allocation.",
        )

    def test_architecture_doc_records_every_pair(self) -> None:
        text = ARCHITECTURE_DOC.read_text()
        missing = _doc_pairs_present(text, ALL_ALLOCATION.items())
        self.assertEqual(
            missing,
            [],
            f"{ARCHITECTURE_DOC.name} (the Core architecture index) must "
            f"keep the per-net native GPIO pin-allocation table "
            f"(missing pairs: {missing}).",
        )

    def test_blocker_doc_records_native_gpio_allocation_status(self) -> None:
        text = BLOCKER_DOC.read_text()
        self.assertIn(
            "S360-100-TACH-GPIO-ALLOCATION-001",
            text,
            f"{BLOCKER_DOC.name} (PWM-12 row) must cite "
            "S360-100-TACH-GPIO-ALLOCATION-001.",
        )
        self.assertIn(
            "native GPIO allocation documented",
            text,
            f"{BLOCKER_DOC.name} PWM-12 row status text must reflect "
            "that the native GPIO allocation is documented.",
        )

    def test_readiness_doc_cites_the_allocation(self) -> None:
        text = READINESS_DOC.read_text()
        self.assertIn(
            "S360-100-TACH-GPIO-ALLOCATION-001",
            text,
            f"{READINESS_DOC.name} must carry a dated FanPWM / S360-311 "
            "subsection for S360-100-TACH-GPIO-ALLOCATION-001.",
        )


class NoExpanderTachStillEnforcedTests(unittest.TestCase):
    """The architectural rule from S360-100-NATIVE-TACH-PULSE-001 must
    keep holding after the GPIO allocation is recorded."""

    def test_no_pulse_counter_uses_sx1509_pin_in_packages(self) -> None:
        for path in _iter_yaml(PACKAGES_DIR):
            with self.subTest(file=path.relative_to(REPO_ROOT).as_posix()):
                text = _strip_yaml_comments(path.read_text())
                self.assertIsNone(
                    _PULSE_COUNTER_SX1509_PIN.search(text),
                    "Allocating native GPIOs must not weaken the "
                    "S360-100-NATIVE-TACH-PULSE-001 rule: no "
                    "`pulse_counter` may bind an `sx1509:` pin.",
                )

    def test_no_pulse_counter_uses_sx1509_pin_in_products(self) -> None:
        for path in _iter_yaml(PRODUCTS_DIR):
            with self.subTest(file=path.relative_to(REPO_ROOT).as_posix()):
                text = _strip_yaml_comments(path.read_text())
                self.assertIsNone(
                    _PULSE_COUNTER_SX1509_PIN.search(text),
                    "Allocating native GPIOs must not weaken the "
                    "S360-100-NATIVE-TACH-PULSE-001 rule.",
                )


class TachGpioAllocationDoesNotFlipProductStatusTests(unittest.TestCase):
    """Recording the GPIO allocation must not flip FanPWM status or
    open WebFlash exposure for S360-311."""

    def _load_json(self, path: Path) -> dict:
        with path.open() as fh:
            return json.load(fh)

    def test_hardware_catalog_s360_311_not_verified(self) -> None:
        data = self._load_json(HARDWARE_CATALOG_JSON)
        s311 = next(
            (e for e in data.get("items", []) if e.get("sku") == "S360-311"),
            None,
        )
        self.assertIsNotNone(s311, "S360-311 row must exist.")
        self.assertNotEqual(
            s311.get("schematic_status"),
            "verified",
            "S360-311 must not be promoted to `verified` by the "
            "GPIO allocation PR.",
        )

    def test_product_catalog_fanpwm_not_promoted(self) -> None:
        data = self._load_json(PRODUCT_CATALOG_JSON)
        for entry in data.get("products", []):
            config = entry.get("config_string") or entry.get("name")
            if not config or "FanPWM" not in str(config):
                continue
            with self.subTest(config=config):
                self.assertNotEqual(
                    entry.get("rpm_supported"),
                    True,
                    f"{config}: rpm_supported must stay false.",
                )
                self.assertFalse(
                    bool(entry.get("webflash_build_matrix")),
                    f"{config}: webflash_build_matrix must stay false.",
                )
                self.assertIsNone(
                    entry.get("artifact_name"),
                    f"{config}: artifact_name must remain unset.",
                )

    def test_webflash_builds_has_no_fanpwm_entry(self) -> None:
        data = self._load_json(WEBFLASH_BUILDS_JSON)
        builds = data.get("builds", []) if isinstance(data, dict) else []
        for row in builds:
            cfg = row.get("config_string", "")
            with self.subTest(config_string=cfg):
                self.assertNotIn(
                    "FanPWM",
                    cfg,
                    f"FanPWM must not appear in any WebFlash build "
                    f"(`{cfg}`) after S360-100-TACH-GPIO-ALLOCATION-001.",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)

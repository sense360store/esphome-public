#!/usr/bin/env python3
"""PRODUCT-010 stdlib unittest suite for scripts/scaffold_product.py.

Covers the conservative-scaffold rules:

  * Valid compile-only scaffold report for a fresh, non-duplicate config
    exits 0 and the Markdown report contains the expected sections.
  * Invalid module tokens exit non-zero.
  * Duplicate catalog entry exits non-zero.
  * Unknown hardware SKU exits non-zero.
  * Production status is rejected with an explanatory message that
    points at the promotion gates.
  * Preview with --channel stable is rejected.
  * Preview --webflash-build-matrix without --webflash-wrapper is
    rejected.
  * FanTRIAC config forces blocked + HW-005.
  * The report always carries the validation-commands section.
  * The report always carries the do-not-change guardrails section.
  * Future tokens (LED, FanRelay, FanPWM, FanDAC, AirIQ) parse cleanly
    when used legally.

Run with:

    python3 tests/test_scaffold_product.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "scaffold_product.py"


# ----------------------------------------------------------------------
# Synthetic fixtures
# ----------------------------------------------------------------------


def _minimal_compat() -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "source": "WebFlash",
        "canonical_mounting": ["Ceiling"],
        "canonical_power": ["USB", "POE", "PWR"],
        "canonical_modules": [
            "AirIQ",
            "VentIQ",
            "RoomIQ",
            "FanRelay",
            "FanPWM",
            "FanDAC",
            "FanTRIAC",
            "LED",
        ],
        "forbidden_tokens": [
            "Bathroom",
            "Comfort",
            "Presence",
            "Fan",
            "FanAnalog",
        ],
        "rules": {
            "airiq_and_ventiq_mutually_exclusive": True,
            "roomiq_can_pair_with_airiq": True,
            "roomiq_can_pair_with_ventiq": True,
            "fan_variants_are_firmware_distinct": True,
            "generic_fan_token_forbidden": True,
            "fandac_conflicts_with_airiq": True,
        },
        "release_one_required_configs": ["Ceiling-POE-VentIQ-RoomIQ"],
        "artifact_pattern": "Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin",
        "allowed_channels": ["stable", "beta", "preview", "dev", "rescue"],
        "production_channel": "stable",
        "rescue_config_string": "Rescue",
    }


def _minimal_hardware_catalog() -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "items": [
            {"sku": "S360-100", "friendly_name": "Sense360 Core"},
            {"sku": "S360-200", "friendly_name": "Sense360 RoomIQ"},
            {"sku": "S360-210", "friendly_name": "Sense360 AirIQ"},
            {"sku": "S360-211", "friendly_name": "Sense360 VentIQ"},
            {"sku": "S360-300", "friendly_name": "Sense360 LED"},
            {"sku": "S360-310", "friendly_name": "Sense360 Relay"},
            {"sku": "S360-410", "friendly_name": "Sense360 PoE PSU"},
        ],
    }


def _minimal_catalog_with_release_one() -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "lifecycle_statuses": [
            "production",
            "preview",
            "compile-only",
            "hardware-pending",
            "blocked",
            "legacy-compatible",
            "deprecated",
            "removed",
        ],
        "products": [
            {
                "config_string": "Ceiling-POE-VentIQ-RoomIQ",
                "status": "production",
                "version": "1.0.0",
                "channel": "stable",
                "product_yaml": "products/sense360-ceiling-poe-ventiq-roomiq.yaml",
                "webflash_wrapper": "products/webflash/ceiling-poe-ventiq-roomiq.yaml",
                "artifact_name": "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin",
                "webflash_build_matrix": True,
            }
        ],
    }


def _minimal_builds_with_release_one() -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "builds": [
            {
                "config_string": "Ceiling-POE-VentIQ-RoomIQ",
                "product_yaml": "products/webflash/ceiling-poe-ventiq-roomiq.yaml",
                "artifact_name": "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin",
                "channel": "stable",
                "version": "1.0.0",
                "chip_family": "ESP32-S3",
                "hardware_requirements": [],
                "features": [],
            }
        ],
    }


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


class ScaffoldFixture:
    """Writes a minimal set of synthetic JSON fixtures to a temp dir."""

    def __init__(
        self,
        catalog: Dict[str, Any],
        builds: Dict[str, Any],
        compat: Dict[str, Any],
        hardware: Dict[str, Any],
    ) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        self.catalog_path = root / "catalog.json"
        self.builds_path = root / "builds.json"
        self.compat_path = root / "compat.json"
        self.hardware_path = root / "hardware.json"
        self.catalog_path.write_text(json.dumps(catalog))
        self.builds_path.write_text(json.dumps(builds))
        self.compat_path.write_text(json.dumps(compat))
        self.hardware_path.write_text(json.dumps(hardware))

    def cleanup(self) -> None:
        self._tmp.cleanup()

    def run(self, args: List[str]) -> Tuple[int, str, str]:
        full = [
            sys.executable,
            str(SCRIPT_PATH),
            "--catalog",
            str(self.catalog_path),
            "--builds",
            str(self.builds_path),
            "--compat",
            str(self.compat_path),
            "--hardware-catalog",
            str(self.hardware_path),
            *args,
        ]
        result = subprocess.run(
            full,
            capture_output=True,
            text=True,
        )
        return result.returncode, result.stdout, result.stderr


def _default_fixture() -> ScaffoldFixture:
    return ScaffoldFixture(
        catalog=_minimal_catalog_with_release_one(),
        builds=_minimal_builds_with_release_one(),
        compat=_minimal_compat(),
        hardware=_minimal_hardware_catalog(),
    )


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------


class CompileOnlyHappyPathTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = _default_fixture()
        self.addCleanup(self.fx.cleanup)

    def test_valid_compile_only_exits_zero(self) -> None:
        code, out, err = self.fx.run(
            [
                "--config-string",
                "Ceiling-POE-VentIQ-RoomIQ-LED",
                "--status",
                "compile-only",
                "--product-yaml",
                "products/sense360-ceiling-poe-ventiq-roomiq-led.yaml",
                "--hardware-status",
                "verified-led-candidate",
                "--hardware",
                "core=S360-100",
                "--hardware",
                "ventiq=S360-211",
                "--hardware",
                "roomiq=S360-200",
                "--hardware",
                "poe=S360-410",
                "--hardware",
                "led=S360-300",
            ]
        )
        self.assertEqual(code, 0, f"stdout=\n{out}\nstderr=\n{err}")
        self.assertIn("# Product Scaffold Report", out)
        self.assertIn("## Input", out)
        self.assertIn("## Parsed config string", out)
        self.assertIn("## Compatibility grammar check", out)
        self.assertIn("## Existing repo state", out)
        self.assertIn("## Hardware SKU check", out)
        self.assertIn("## Proposed product-catalog entry", out)
        self.assertIn("## Optional WebFlash build-matrix entry", out)
        self.assertIn("## Required files", out)
        self.assertIn("## Validation commands", out)
        self.assertIn("## Human review checklist", out)
        self.assertIn("## Do-not-change guardrails", out)
        self.assertIn("## Next PR sequence", out)
        self.assertIn("scaffold report passed every validation", out)

    def test_report_contains_validation_commands(self) -> None:
        code, out, _ = self.fx.run(
            [
                "--config-string",
                "Ceiling-POE-AirIQ",
                "--status",
                "compile-only",
                "--product-yaml",
                "products/sense360-ceiling-poe-airiq.yaml",
                "--hardware-status",
                "pending-bringup",
            ]
        )
        self.assertEqual(code, 0)
        for cmd in (
            "python3 tests/test_scaffold_product.py",
            "python3 tests/test_product_catalog.py",
            "python3 tests/test_product_catalog_consistency.py",
            "python3 tests/validate_webflash_builds.py",
            "python3 tests/test_webflash_compatibility.py",
            "python3 tests/test_webflash_artifact_naming.py",
            "python3 tests/test_validate_webflash_release_notes.py",
            "python3 tests/test_generate_webflash_release_notes.py",
            "python3 tests/test_product_substitutions.py",
            "python3 tests/test_release_one_entity_names.py",
            "python3 tests/validate_configs.py",
        ):
            self.assertIn(cmd, out, f"validation command {cmd!r} missing")

    def test_report_contains_do_not_change_guardrails(self) -> None:
        code, out, _ = self.fx.run(
            [
                "--config-string",
                "Ceiling-POE-AirIQ",
                "--status",
                "compile-only",
                "--product-yaml",
                "products/sense360-ceiling-poe-airiq.yaml",
                "--hardware-status",
                "pending-bringup",
            ]
        )
        self.assertEqual(code, 0)
        self.assertIn("Release-One config string", out)
        self.assertIn("FanTRIAC stays blocked under HW-005", out)
        self.assertIn("Sense360 LED stays excluded from Release-One", out)
        self.assertIn(
            "No firmware build, no GitHub Release, no WebFlash import",
            out,
        )


class GrammarTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = _default_fixture()
        self.addCleanup(self.fx.cleanup)

    def test_invalid_module_token_exits_nonzero(self) -> None:
        code, out, _ = self.fx.run(
            [
                "--config-string",
                "Ceiling-POE-Bogus",
                "--status",
                "compile-only",
                "--product-yaml",
                "products/sense360-ceiling-poe-bogus.yaml",
                "--hardware-status",
                "pending-bringup",
            ]
        )
        self.assertNotEqual(code, 0)
        self.assertIn("Unknown module token", out)

    def test_invalid_mounting_token_exits_nonzero(self) -> None:
        code, out, _ = self.fx.run(
            [
                "--config-string",
                "Wall-POE-VentIQ",
                "--status",
                "compile-only",
                "--product-yaml",
                "products/sense360-wall-poe-ventiq.yaml",
                "--hardware-status",
                "pending-bringup",
            ]
        )
        self.assertNotEqual(code, 0)
        self.assertIn("Invalid mounting token", out)

    def test_airiq_and_ventiq_mutex_violation_exits_nonzero(self) -> None:
        code, out, _ = self.fx.run(
            [
                "--config-string",
                "Ceiling-POE-AirIQ-VentIQ",
                "--status",
                "compile-only",
                "--product-yaml",
                "products/sense360-ceiling-poe-airiq-ventiq.yaml",
                "--hardware-status",
                "pending-bringup",
            ]
        )
        self.assertNotEqual(code, 0)
        self.assertIn("mutually exclusive", out)

    def test_future_tokens_parse_cleanly(self) -> None:
        code, out, _ = self.fx.run(
            [
                "--config-string",
                "Ceiling-POE-AirIQ-FanRelay-LED",
                "--status",
                "compile-only",
                "--product-yaml",
                "products/sense360-ceiling-poe-airiq-fanrelay-led.yaml",
                "--hardware-status",
                "pending-bringup",
                "--hardware",
                "core=S360-100",
                "--hardware",
                "airiq=S360-210",
                "--hardware",
                "fanrelay=S360-310",
                "--hardware",
                "led=S360-300",
                "--hardware",
                "poe=S360-410",
            ]
        )
        self.assertEqual(code, 0, msg=out)


class DuplicateDetectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = _default_fixture()
        self.addCleanup(self.fx.cleanup)

    def test_duplicate_catalog_entry_exits_nonzero(self) -> None:
        code, out, _ = self.fx.run(
            [
                "--config-string",
                "Ceiling-POE-VentIQ-RoomIQ",
                "--status",
                "compile-only",
                "--product-yaml",
                "products/sense360-ceiling-poe-ventiq-roomiq.yaml",
                "--hardware-status",
                "pending-bringup",
            ]
        )
        self.assertNotEqual(code, 0)
        self.assertIn("duplicate catalog entry", out)


class HardwareSkuTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = _default_fixture()
        self.addCleanup(self.fx.cleanup)

    def test_unknown_hardware_sku_exits_nonzero(self) -> None:
        code, out, _ = self.fx.run(
            [
                "--config-string",
                "Ceiling-POE-VentIQ",
                "--status",
                "compile-only",
                "--product-yaml",
                "products/sense360-ceiling-poe-ventiq.yaml",
                "--hardware-status",
                "pending-bringup",
                "--hardware",
                "core=S360-999",
            ]
        )
        self.assertNotEqual(code, 0)
        self.assertIn("S360-999", out)
        self.assertIn("config/hardware-catalog.json", out)


class StatusRejectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = _default_fixture()
        self.addCleanup(self.fx.cleanup)

    def test_production_status_is_rejected(self) -> None:
        code, out, _ = self.fx.run(
            [
                "--config-string",
                "Ceiling-POE-AirIQ",
                "--status",
                "production",
                "--product-yaml",
                "products/sense360-ceiling-poe-airiq.yaml",
                "--hardware-status",
                "verified-candidate",
            ]
        )
        self.assertNotEqual(code, 0)
        self.assertIn("not scaffoldable", out)
        self.assertIn("preview-to-stable-promotion-gates.md", out)

    def test_legacy_compatible_status_is_rejected(self) -> None:
        code, out, _ = self.fx.run(
            [
                "--config-string",
                "Ceiling-POE-AirIQ",
                "--status",
                "legacy-compatible",
                "--product-yaml",
                "products/sense360-ceiling-poe-airiq.yaml",
                "--hardware-status",
                "verified-candidate",
            ]
        )
        self.assertNotEqual(code, 0)
        self.assertIn("legacy-compatible", out)


class PreviewRulesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = _default_fixture()
        self.addCleanup(self.fx.cleanup)

    def test_preview_with_stable_channel_is_rejected(self) -> None:
        code, out, _ = self.fx.run(
            [
                "--config-string",
                "Ceiling-POE-AirIQ",
                "--status",
                "preview",
                "--product-yaml",
                "products/sense360-ceiling-poe-airiq.yaml",
                "--hardware-status",
                "verified-candidate",
                "--version",
                "1.0.0",
                "--channel",
                "stable",
            ]
        )
        self.assertNotEqual(code, 0)
        self.assertIn("must not use --channel stable", out)

    def test_preview_build_matrix_without_wrapper_exits_nonzero(self) -> None:
        code, out, _ = self.fx.run(
            [
                "--config-string",
                "Ceiling-POE-AirIQ",
                "--status",
                "preview",
                "--product-yaml",
                "products/sense360-ceiling-poe-airiq.yaml",
                "--hardware-status",
                "verified-candidate",
                "--version",
                "1.0.0",
                "--channel",
                "preview",
                "--webflash-build-matrix",
            ]
        )
        self.assertNotEqual(code, 0)
        self.assertIn("--webflash-wrapper", out)

    def test_preview_must_not_claim_release_one_required_config(self) -> None:
        catalog = _minimal_catalog_with_release_one()
        catalog["products"] = []
        builds = _minimal_builds_with_release_one()
        builds["builds"] = []
        fx = ScaffoldFixture(
            catalog=catalog,
            builds=builds,
            compat=_minimal_compat(),
            hardware=_minimal_hardware_catalog(),
        )
        self.addCleanup(fx.cleanup)
        code, out, _ = fx.run(
            [
                "--config-string",
                "Ceiling-POE-VentIQ-RoomIQ",
                "--status",
                "preview",
                "--product-yaml",
                "products/sense360-ceiling-poe-ventiq-roomiq.yaml",
                "--hardware-status",
                "verified-candidate",
                "--version",
                "0.9.0",
                "--channel",
                "preview",
            ]
        )
        self.assertNotEqual(code, 0)
        self.assertIn("Release-One required config", out)

    def test_preview_happy_path_without_build_matrix(self) -> None:
        code, out, _ = self.fx.run(
            [
                "--config-string",
                "Ceiling-POE-AirIQ",
                "--status",
                "preview",
                "--product-yaml",
                "products/sense360-ceiling-poe-airiq.yaml",
                "--hardware-status",
                "verified-candidate",
                "--version",
                "0.1.0",
                "--channel",
                "preview",
            ]
        )
        self.assertEqual(code, 0, msg=out)
        self.assertIn("Recommendation: `webflash_build_matrix: false`", out)


class FanTriacPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = _default_fixture()
        self.addCleanup(self.fx.cleanup)

    def test_fantriac_compile_only_is_rejected(self) -> None:
        code, out, _ = self.fx.run(
            [
                "--config-string",
                "Ceiling-POE-VentIQ-FanTRIAC",
                "--status",
                "compile-only",
                "--product-yaml",
                "products/sense360-ceiling-poe-ventiq-fantriac.yaml",
                "--hardware-status",
                "pending-bringup",
            ]
        )
        self.assertNotEqual(code, 0)
        self.assertIn("FanTRIAC", out)
        self.assertIn("HW-005", out)

    def test_fantriac_blocked_with_hw005_is_accepted(self) -> None:
        code, out, _ = self.fx.run(
            [
                "--config-string",
                "Ceiling-POE-FanTRIAC",
                "--status",
                "blocked",
                "--product-yaml",
                "products/sense360-ceiling-poe-fantriac.yaml",
                "--blocker",
                "HW-005",
                "--reason",
                "S360-320 schematic uncommitted.",
            ]
        )
        self.assertEqual(code, 0, msg=out)
        self.assertIn("scaffold report passed every validation", out)

    def test_fantriac_blocked_with_wrong_blocker_is_rejected(self) -> None:
        code, out, _ = self.fx.run(
            [
                "--config-string",
                "Ceiling-POE-FanTRIAC",
                "--status",
                "blocked",
                "--product-yaml",
                "products/sense360-ceiling-poe-fantriac.yaml",
                "--blocker",
                "HW-999",
                "--reason",
                "Wrong blocker.",
            ]
        )
        self.assertNotEqual(code, 0)
        self.assertIn("HW-005", out)


class BuildMatrixGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = _default_fixture()
        self.addCleanup(self.fx.cleanup)

    def test_compile_only_cannot_request_build_matrix(self) -> None:
        code, out, _ = self.fx.run(
            [
                "--config-string",
                "Ceiling-POE-AirIQ",
                "--status",
                "compile-only",
                "--product-yaml",
                "products/sense360-ceiling-poe-airiq.yaml",
                "--hardware-status",
                "pending-bringup",
                "--webflash-build-matrix",
            ]
        )
        self.assertNotEqual(code, 0)
        self.assertIn("compile-only", out)
        self.assertIn("--webflash-build-matrix", out)


class HardwarePendingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = _default_fixture()
        self.addCleanup(self.fx.cleanup)

    def test_hardware_pending_requires_missing_evidence(self) -> None:
        code, out, _ = self.fx.run(
            [
                "--config-string",
                "Ceiling-POE-AirIQ",
                "--status",
                "hardware-pending",
                "--product-yaml",
                "products/sense360-ceiling-poe-airiq.yaml",
                "--hardware-status",
                "pending-evidence",
            ]
        )
        self.assertNotEqual(code, 0)
        self.assertIn("missing-hardware-evidence", out)

    def test_hardware_pending_happy_path(self) -> None:
        code, out, _ = self.fx.run(
            [
                "--config-string",
                "Ceiling-POE-AirIQ",
                "--status",
                "hardware-pending",
                "--product-yaml",
                "products/sense360-ceiling-poe-airiq.yaml",
                "--hardware-status",
                "pending-evidence",
                "--missing-hardware-evidence",
                "S360-210 bench verification pending",
            ]
        )
        self.assertEqual(code, 0, msg=out)


class ProductYamlPathTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = _default_fixture()
        self.addCleanup(self.fx.cleanup)

    def test_product_yaml_under_webflash_wrappers_is_rejected(self) -> None:
        code, out, _ = self.fx.run(
            [
                "--config-string",
                "Ceiling-POE-AirIQ",
                "--status",
                "compile-only",
                "--product-yaml",
                "products/webflash/ceiling-poe-airiq.yaml",
                "--hardware-status",
                "pending-bringup",
            ]
        )
        self.assertNotEqual(code, 0)
        self.assertIn("products/webflash/", out)


class ReadOnlyTests(unittest.TestCase):
    """Confirm the script never mutates any input file."""

    def test_running_does_not_mutate_fixtures(self) -> None:
        fx = _default_fixture()
        self.addCleanup(fx.cleanup)
        before_catalog = fx.catalog_path.read_text()
        before_builds = fx.builds_path.read_text()
        before_compat = fx.compat_path.read_text()
        before_hardware = fx.hardware_path.read_text()
        fx.run(
            [
                "--config-string",
                "Ceiling-POE-VentIQ-RoomIQ-LED",
                "--status",
                "compile-only",
                "--product-yaml",
                "products/sense360-ceiling-poe-ventiq-roomiq-led.yaml",
                "--hardware-status",
                "verified-led-candidate",
            ]
        )
        self.assertEqual(before_catalog, fx.catalog_path.read_text())
        self.assertEqual(before_builds, fx.builds_path.read_text())
        self.assertEqual(before_compat, fx.compat_path.read_text())
        self.assertEqual(before_hardware, fx.hardware_path.read_text())


if __name__ == "__main__":
    unittest.main(verbosity=2)

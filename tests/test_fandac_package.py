#!/usr/bin/env python3
"""Tests for the FanDAC dual-GP8403 package implementation
(PACKAGE-DAC-001-IMPLEMENT-001).

These checks pin the package-layer reconciliation of
``packages/expansions/fan_gp8403.yaml`` against the schematic + BOM +
GP8403 datasheet + layout evidence consolidated in
``docs/hardware/s360-312-r4-fandac.md`` and the operator design
decisions recorded there:

  * two GP8403 DAC chips (IC1 / IC2) on the shared ``core_i2c`` bus,
  * four neutral package-layer outputs (two per chip),
  * per-chip I2C address substitutions,
  * per-chip output-range substitutions, both defaulting to 0-10V,
  * range is firmware/register-driven (no hardware jumper),
  * a single GP8403 cannot mix 0-5V / 0-10V across its two outputs,
  * the package stays package-layer only — no product fan names,
    no WebFlash / release wiring, no DAC product YAML.

These are deliberately file-content / structural checks — they do
not require an ESPHome compile (the package consumes the abstract
``${fan_dac_i2c_id}`` bus from a parent Core package).

Run with::

    python3 tests/test_fandac_package.py

or::

    python3 -m unittest tests.test_fandac_package -v
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
PACKAGES_EXPANSIONS = REPO_ROOT / "packages" / "expansions"

FAN_GP8403 = PACKAGES_EXPANSIONS / "fan_gp8403.yaml"
FAN_DAC_ALIAS = PACKAGES_EXPANSIONS / "fan_dac.yaml"
PRODUCTS_DIR = REPO_ROOT / "products"


def _read(path: Path) -> str:
    return path.read_text()


def _substitution_value(text: str, key: str) -> str | None:
    """Return the value of a top-level ``key: value`` substitution.

    Mirrors the lightweight scalar lookup used by
    ``tests/test_core_abstract_bus.py``; tolerates optional quoting and
    inline comments.
    """

    m = re.search(
        rf"^\s*{re.escape(key)}\s*:\s*(.+?)\s*(?:#.*)?$",
        text,
        re.MULTILINE,
    )
    if not m:
        return None
    return m.group(1).strip().strip('"').strip("'")


def _active_lines(text: str) -> list[str]:
    """Non-comment, non-blank lines (comment = first non-space char is #)."""

    out = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        out.append(raw)
    return out


class FanDACAliasContractTests(unittest.TestCase):
    """fan_dac.yaml must remain a pure alias of fan_gp8403.yaml."""

    def test_alias_includes_fan_gp8403(self) -> None:
        text = _read(FAN_DAC_ALIAS)
        includes = re.findall(
            r"^\s*[A-Za-z0-9_\-]+\s*:\s*!include\s+(\S+)\s*$",
            text,
            re.MULTILINE,
        )
        self.assertEqual(
            includes,
            ["fan_gp8403.yaml"],
            "fan_dac.yaml must alias fan_gp8403.yaml via exactly one "
            f"`!include fan_gp8403.yaml`; found {includes!r}.",
        )


class FanDACBusBindingTests(unittest.TestCase):
    """Shared core_i2c bus binding (CORE-ABSTRACT-BUS-001B)."""

    def test_fan_dac_i2c_id_default_is_core_i2c(self) -> None:
        self.assertEqual(
            _substitution_value(_read(FAN_GP8403), "fan_dac_i2c_id"),
            "core_i2c",
            "fan_gp8403.yaml fan_dac_i2c_id default must be core_i2c.",
        )

    def test_both_chips_consume_the_bus_substitution(self) -> None:
        text = _read(FAN_GP8403)
        binds = re.findall(r"i2c_id:\s*\$\{fan_dac_i2c_id\}", text)
        self.assertEqual(
            len(binds),
            2,
            "Both GP8403 chips must bind `i2c_id: ${fan_dac_i2c_id}` so the "
            f"shared-bus rebind flows through; found {len(binds)}.",
        )

    def test_no_legacy_i2c_ids_remain(self) -> None:
        text = _read(FAN_GP8403)
        for legacy in ("i2c0", "expansion_i2c", "shared_i2c", "halo_i2c"):
            self.assertNotIn(
                legacy,
                text,
                f"legacy i2c id {legacy!r} must not appear in "
                "fan_gp8403.yaml after CORE-ABSTRACT-BUS-001B.",
            )
        # The stale GPIO39 / GPIO40 header pin claims (pre-001B) must be gone.
        for legacy_pin in ("GPIO39", "GPIO40"):
            self.assertNotIn(
                legacy_pin,
                text,
                f"stale pin reference {legacy_pin!r} must not remain in "
                "fan_gp8403.yaml; the Core I2C bus is GPIO48 / GPIO45.",
            )


class FanDACTwoChipTests(unittest.TestCase):
    """Two GP8403 chips (IC1 / IC2) must be declared."""

    def test_two_gp8403_chips_declared(self) -> None:
        text = _read(FAN_GP8403)
        for chip_id in ("fan_dac_1", "fan_dac_2"):
            self.assertRegex(
                text,
                rf"-\s*id:\s*{chip_id}\b",
                f"fan_gp8403.yaml must declare a GP8403 chip `id: {chip_id}`.",
            )

    def test_gp8403_block_is_a_list_of_two(self) -> None:
        text = _read(FAN_GP8403)
        chip_ids = re.findall(r"^\s*-\s*id:\s*(fan_dac_\d)\b", text, re.MULTILINE)
        self.assertEqual(
            chip_ids,
            ["fan_dac_1", "fan_dac_2"],
            "fan_gp8403.yaml must expose exactly two GP8403 chips "
            f"(fan_dac_1, fan_dac_2); found {chip_ids!r}.",
        )


class FanDACAddressSubstitutionTests(unittest.TestCase):
    """Per-chip I2C address substitutions for IC1 and IC2."""

    def test_two_address_substitutions_exist(self) -> None:
        text = _read(FAN_GP8403)
        self.assertEqual(
            _substitution_value(text, "fan_dac_1_i2c_address"),
            "0x58",
            "fan_dac_1_i2c_address (IC1) must default to 0x58.",
        )
        self.assertEqual(
            _substitution_value(text, "fan_dac_2_i2c_address"),
            "0x59",
            "fan_dac_2_i2c_address (IC2) must default to 0x59.",
        )

    def test_chips_consume_address_substitutions(self) -> None:
        text = _read(FAN_GP8403)
        self.assertIn("address: ${fan_dac_1_i2c_address}", text)
        self.assertIn("address: ${fan_dac_2_i2c_address}", text)


class FanDACRangeSubstitutionTests(unittest.TestCase):
    """Per-chip output-range substitutions, both defaulting to 0-10V."""

    def test_two_range_substitutions_default_to_0_10v(self) -> None:
        text = _read(FAN_GP8403)
        self.assertEqual(
            _substitution_value(text, "fan_dac_1_output_range"),
            "0-10V",
            "fan_dac_1_output_range (IC1) must default to 0-10V.",
        )
        self.assertEqual(
            _substitution_value(text, "fan_dac_2_output_range"),
            "0-10V",
            "fan_dac_2_output_range (IC2) must default to 0-10V.",
        )

    def test_chips_consume_range_substitutions(self) -> None:
        text = _read(FAN_GP8403)
        self.assertIn("voltage: ${fan_dac_1_output_range}", text)
        self.assertIn("voltage: ${fan_dac_2_output_range}", text)

    def test_range_is_per_chip_not_per_output(self) -> None:
        """Range policy is per DAC chip — there must be no per-output
        range substitution (operator decision D2)."""

        text = _read(FAN_GP8403)
        per_output_range = re.findall(
            r"fan_dac_\d_vout\d_(?:output_)?range", text
        )
        self.assertEqual(
            per_output_range,
            [],
            "Output range is per DAC chip, not per output; no per-output "
            f"range substitution may exist. Found {per_output_range!r}.",
        )


class FanDACOutputTests(unittest.TestCase):
    """Four neutral package-layer outputs (two per chip)."""

    EXPECTED_OUTPUT_IDS = (
        "fan_dac_1_vout0",
        "fan_dac_1_vout1",
        "fan_dac_2_vout0",
        "fan_dac_2_vout1",
    )

    def test_four_output_ids_exist(self) -> None:
        text = _read(FAN_GP8403)
        for out_id in self.EXPECTED_OUTPUT_IDS:
            self.assertRegex(
                text,
                rf"id:\s*{out_id}\b",
                f"fan_gp8403.yaml must expose output `id: {out_id}`.",
            )

    def test_outputs_map_to_the_right_chip_and_channel(self) -> None:
        text = _read(FAN_GP8403)
        # vout0 -> channel 0, vout1 -> channel 1, on the matching chip.
        for chip in ("1", "2"):
            for ch in ("0", "1"):
                block = re.search(
                    rf"id:\s*fan_dac_{chip}_vout{ch}\b.*?channel:\s*(\d)",
                    text,
                    re.DOTALL,
                )
                self.assertIsNotNone(
                    block,
                    f"output fan_dac_{chip}_vout{ch} must declare a channel.",
                )
                self.assertEqual(
                    block.group(1),
                    ch,
                    f"fan_dac_{chip}_vout{ch} must map to channel {ch}.",
                )
                self.assertRegex(
                    text,
                    rf"id:\s*fan_dac_{chip}_vout{ch}\b[\s\S]*?gp8403_id:\s*fan_dac_{chip}\b",
                    f"fan_dac_{chip}_vout{ch} must bind gp8403_id "
                    f"fan_dac_{chip}.",
                )


class FanDACRangeMechanismTests(unittest.TestCase):
    """Range mechanism wording: firmware/register-driven, not jumper."""

    def test_no_stale_jumper_selectable_wording(self) -> None:
        lowered = _read(FAN_GP8403).lower()
        for stale in ("jumper selectable", "jumper-selectable", "selectable on hardware"):
            self.assertNotIn(
                stale,
                lowered,
                f"stale {stale!r} wording must not remain in fan_gp8403.yaml; "
                "GP8403 range is firmware/register-driven (register 0x01).",
            )

    def test_records_firmware_register_driven_range(self) -> None:
        lowered = _read(FAN_GP8403).lower()
        self.assertIn(
            "register",
            lowered,
            "fan_gp8403.yaml must record that range is register-driven.",
        )
        self.assertIn(
            "firmware",
            lowered,
            "fan_gp8403.yaml must record that range is firmware-driven.",
        )

    def test_does_not_claim_per_output_mixed_ranges_on_one_chip(self) -> None:
        """Hard guardrail D6: a single GP8403 cannot drive one output at
        0-5V and the other at 0-10V (one V5V reference / one range
        register per chip)."""

        lowered = _read(FAN_GP8403).lower()
        self.assertIn(
            "cannot mix",
            lowered,
            "fan_gp8403.yaml must explicitly record that a single GP8403 "
            "cannot mix 0-5V and 0-10V across its two outputs.",
        )


class FanDACPackageLayerOnlyTests(unittest.TestCase):
    """The package stays package-layer only — no product wiring."""

    def test_no_product_fan_names_hardcoded(self) -> None:
        active = "\n".join(_active_lines(_read(FAN_GP8403)))
        self.assertNotIn(
            "${friendly_name}",
            active,
            "fan_gp8403.yaml must not hard-code product-layer fan names "
            "via ${friendly_name}; user-facing fan entities belong to the "
            "product layer (PRODUCT-DAC-001).",
        )
        self.assertNotRegex(
            active,
            r"^\s*name\s*:",
            "fan_gp8403.yaml must not declare a user-facing `name:` "
            "(product-layer concern).",
        )

    def test_no_product_layer_entity_blocks(self) -> None:
        active = _active_lines(_read(FAN_GP8403))
        forbidden_top_level = ("fan:", "climate:", "switch:", "select:", "number:")
        for line in active:
            for key in forbidden_top_level:
                self.assertFalse(
                    line.startswith(key),
                    f"fan_gp8403.yaml is package-layer only and must not "
                    f"declare a top-level {key!r} block.",
                )

    def test_no_webflash_or_release_tokens(self) -> None:
        lowered = _read(FAN_GP8403).lower()
        for token in ("artifact_name", "webflash_build_matrix", "webflash", "config_string"):
            self.assertNotIn(
                token,
                lowered,
                f"package-layer fan_gp8403.yaml must not carry WebFlash / "
                f"release token {token!r}.",
            )

    def test_no_product_actively_includes_the_dac_package(self) -> None:
        """Guardrail: this slice adds no DAC product YAML, so no file under
        products/ may actively !include the FanDAC package (comment-only
        references are allowed)."""

        if not PRODUCTS_DIR.is_dir():
            self.skipTest("no products/ directory")
        offenders: list[str] = []
        for path in PRODUCTS_DIR.rglob("*.yaml"):
            for raw in path.read_text().splitlines():
                stripped = raw.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                if "!include" in stripped and (
                    "fan_gp8403.yaml" in stripped or "fan_dac.yaml" in stripped
                ):
                    offenders.append(f"{path.name}: {stripped}")
        self.assertEqual(
            offenders,
            [],
            "No product YAML may actively !include the FanDAC package in "
            f"this package-layer-only slice; found: {offenders!r}.",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

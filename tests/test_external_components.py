#!/usr/bin/env python3
"""External-component foundation guards (SENSE360-CANONICALISATION-001 PR 08).

Pins the external-component architecture introduced by PR 08:

  * ``config/external-components.json`` is the manifest of everything under
    ``components/`` — both directions (no undeclared component directory, no
    dangling manifest row), every row with origin / role / provenance /
    disposition_owner.
  * The no-fork rule travels with the manifest: the ``sense360`` foundation
    component contains no raw hardware I/O driver code (no I2C / UART / SPI
    device classes) — product behaviour never enters through a forked or
    smuggled sensor driver.
  * The ``BOARD_SKUS`` literal carried by ``components/sense360/__init__.py``
    (a consumer build cannot read repository config) stays pinned equal to
    the canonical ``config/hardware-catalog.json`` SKU set.
  * ``SHARED_HEADERS`` matches the ``.h`` files physically present in the
    component, both directions, so the delivered set cannot drift from the
    tested set.
  * The former ``include/sense360/`` delivery-only path stays deleted.

Run with::

    python3 tests/test_external_components.py
"""

import ast
import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = REPO_ROOT / "config" / "external-components.json"
COMPONENTS_DIR = REPO_ROOT / "components"
SENSE360_DIR = COMPONENTS_DIR / "sense360"
SENSE360_INIT = SENSE360_DIR / "__init__.py"
HARDWARE_CATALOG = REPO_ROOT / "config" / "hardware-catalog.json"

REQUIRED_ROW_KEYS = {"role", "origin", "provenance", "disposition_owner"}

# Raw hardware-I/O markers that must never appear in the foundation
# component: it is logic-and-schema only.
HARDWARE_IO_MARKERS = (
    "i2c::I2CDevice",
    "uart::UARTDevice",
    "spi::SPIDevice",
    "esphome/components/i2c",
    "esphome/components/uart",
    "esphome/components/spi",
)


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _init_literal(name: str) -> tuple:
    """Extract a top-level tuple literal from components/sense360/__init__.py.

    Parsed with ``ast`` so the test never imports the module (which would
    require an ESPHome runtime).
    """
    tree = ast.parse(SENSE360_INIT.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return tuple(ast.literal_eval(node.value))
    raise AssertionError(f"{name} literal not found in {SENSE360_INIT}")


class ManifestCompletenessTests(unittest.TestCase):
    def test_every_component_directory_is_declared(self) -> None:
        declared = set(_manifest()["components"])
        on_disk = {p.name for p in COMPONENTS_DIR.iterdir() if p.is_dir()}
        self.assertEqual(
            on_disk,
            declared,
            "components/ directories and config/external-components.json rows "
            "must match exactly (no undeclared component, no dangling row).",
        )

    def test_every_row_carries_provenance(self) -> None:
        for name, row in _manifest()["components"].items():
            with self.subTest(component=name):
                self.assertTrue(
                    REQUIRED_ROW_KEYS.issubset(row),
                    f"{name} row must carry {sorted(REQUIRED_ROW_KEYS)}",
                )

    def test_no_fork_rule_recorded(self) -> None:
        rules = _manifest()["rules"]
        self.assertIn("never_fork_upstream_for_product_behaviour", rules)
        self.assertIn("foundation_declares_no_hardware_io", rules)
        self.assertIn("delivery_path_is_components_only", rules)


class FoundationBoundaryTests(unittest.TestCase):
    """The sense360 component is logic-and-schema only."""

    def test_no_hardware_io_in_foundation(self) -> None:
        for path in sorted(SENSE360_DIR.glob("*")):
            if path.suffix not in (".h", ".cpp", ".py"):
                continue
            text = path.read_text(encoding="utf-8")
            for marker in HARDWARE_IO_MARKERS:
                self.assertNotIn(
                    marker,
                    text,
                    f"{path.name} must not contain raw hardware I/O "
                    f"({marker}); raw sensor communication uses built-in "
                    "ESPHome drivers or a declared vendored driver, never "
                    "the foundation component.",
                )

    def test_shared_headers_match_disk_both_directions(self) -> None:
        declared = set(_init_literal("SHARED_HEADERS"))
        on_disk = {p.name for p in SENSE360_DIR.glob("*.h")}
        self.assertEqual(
            on_disk,
            declared,
            "SHARED_HEADERS in components/sense360/__init__.py must list "
            "exactly the .h files present in the component.",
        )

    def test_board_skus_pinned_to_hardware_catalog(self) -> None:
        catalog = json.loads(HARDWARE_CATALOG.read_text(encoding="utf-8"))
        catalog_skus = {item["sku"] for item in catalog["items"]}
        self.assertEqual(
            set(_init_literal("BOARD_SKUS")),
            catalog_skus,
            "BOARD_SKUS in components/sense360/__init__.py drifted from "
            "config/hardware-catalog.json (the catalog decides; the "
            "component literal follows).",
        )

    def test_foundation_declares_no_platform_modules(self) -> None:
        # Domain platforms (sensor.py, switch.py, ...) belong to the PR 09..12
        # domain components, never the foundation.
        platform_files = [
            p.name
            for p in SENSE360_DIR.glob("*.py")
            if p.name != "__init__.py"
        ]
        self.assertEqual(
            platform_files,
            [],
            "components/sense360/ must stay logic-and-schema only; platform "
            f"modules found: {platform_files}",
        )


class CiOverrideCompletenessTests(unittest.TestCase):
    """The CI-only external_components override must deliver every component.

    The build lanes rewrite packages/base/external_components.yaml at runtime
    to a local checked-out source (setup-esphome-build action, plus the
    duplicate heredoc in manual-firmware-artifacts.yml). A component missing
    from those static lists compiles locally but fails every hosted lane —
    exactly how the PR 09 sense360_roomiq introduction first failed CI. Pin
    both lists to the manifest so a new component can never silently miss
    the override.
    """

    OVERRIDE_FILES = (
        REPO_ROOT / ".github" / "actions" / "setup-esphome-build" / "action.yml",
        REPO_ROOT / ".github" / "workflows" / "manual-firmware-artifacts.yml",
    )

    def test_every_row_declares_its_delivery(self) -> None:
        for name, row in _manifest()["components"].items():
            with self.subTest(component=name):
                self.assertIn(
                    row.get("delivery"),
                    ("base", "inline-board"),
                    f"{name} must declare delivery: base | inline-board "
                    "(see the delivery_axis rule).",
                )

    def test_base_delivered_components_fill_every_ci_override(self) -> None:
        manifest = _manifest()["components"]
        base_set = {n for n, row in manifest.items() if row.get("delivery") == "base"}
        pattern = re.compile(r"components:\s*\[([^\]]+)\]")
        for path in self.OVERRIDE_FILES:
            text = path.read_text(encoding="utf-8")
            matches = [
                m
                for m in pattern.finditer(text)
                if "type: local" in text[max(0, m.start() - 400) : m.start()]
            ]
            self.assertTrue(
                matches,
                f"{path.name}: expected a local external_components override "
                "with a components list",
            )
            for m in matches:
                listed = {item.strip() for item in m.group(1).split(",")}
                self.assertEqual(
                    listed,
                    base_set,
                    f"{path.name}: the CI override components list must "
                    "equal the delivery:'base' set in "
                    "config/external-components.json (a missing base "
                    "component fails every hosted compile lane; an "
                    "inline-board component here would resolve from two "
                    "sources).",
                )

    def test_base_yaml_declares_exactly_the_base_set(self) -> None:
        base_yaml = (
            REPO_ROOT / "packages" / "base" / "external_components.yaml"
        ).read_text(encoding="utf-8")
        manifest = _manifest()["components"]
        for name, row in manifest.items():
            with self.subTest(component=name):
                declared = re.search(
                    rf"components:\s*\[[^\]]*\b{re.escape(name)}\b[^\]]*\]",
                    base_yaml,
                )
                if row.get("delivery") == "base":
                    self.assertIsNotNone(
                        declared,
                        f"{name} is delivery:'base' but missing from "
                        "packages/base/external_components.yaml",
                    )
                else:
                    self.assertIsNone(
                        declared,
                        f"{name} is delivery:'inline-board' and must not "
                        "also appear in packages/base/external_components.yaml",
                    )


class LegacyDeliveryPathTests(unittest.TestCase):
    def test_include_tree_stays_deleted(self) -> None:
        legacy = REPO_ROOT / "include"
        self.assertFalse(
            legacy.exists(),
            "include/ was replaced by components/sense360/ in "
            "SENSE360-CANONICALISATION-001 PR 08 and must not return.",
        )

    def test_no_yaml_references_the_legacy_include_path(self) -> None:
        offenders = []
        pattern = re.compile(r"(?<![\w/])include/sense360/")
        for scan in ("products", "packages"):
            for path in (REPO_ROOT / scan).rglob("*.yaml"):
                for i, line in enumerate(
                    path.read_text(encoding="utf-8").splitlines(), 1
                ):
                    stripped = line.strip()
                    if stripped.startswith("#"):
                        continue
                    if pattern.search(stripped):
                        offenders.append(
                            f"{path.relative_to(REPO_ROOT)}:{i}: {stripped}"
                        )
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()

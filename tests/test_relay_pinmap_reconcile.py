#!/usr/bin/env python3
"""S360-310-RELAY-PINMAP-RECONCILE-001 — cross-layer relay GPIO drift guard.

The S360-310 Relay drive net historically disagreed across layers:

* Core schematic / canonical Core-side connector pin map: ``Relay`` on
  ``IO3`` at ``J4`` pin 2 (``S360-100-R4``).
* ceiling Core abstract package: ``relay_pin: GPIO4`` (pre-001A).
* generic Core abstract package: ``relay_pin: GPIO10`` (pre-001A).

That disagreement was resolved at the substitution layer by
``CORE-ABSTRACT-BUS-001C`` (freed ``GPIO3``) + ``CORE-ABSTRACT-BUS-001A``
(rebound ``relay_pin`` to ``GPIO3``) and reconciled at the package layer
by ``PACKAGE-RELAY-001``. The canonical relay GPIO for ``S360-100-R4``
is ``IO3`` (== ``GPIO3``), proven by the only schematic-backed source in
the repo (the Core schematic / connector pin map).

Per-layer regression tests already exist
(``tests/test_core_abstract_bus.py`` ``RelayPinRebindTests`` pins the
package value; ``tests/test_fan_relay_package.py`` pins the FanRelay
abstraction; ``tests/test_module_pinmaps.py`` pins the module pinmap
doc). What none of them assert is the **cross-layer agreement**: that
the GPIO number bound in the Core abstract packages is the *same number*
the schematic-backed docs record for the ``Relay`` net. This file closes
that gap so the doc layer and the firmware layer cannot silently drift
apart in either direction — if a future edit moves the doc to ``IO5``
but leaves the package at ``GPIO3`` (or vice versa), this test fails.

It also re-pins the hard guardrails for the reconcile slice: the
reconciliation is documentation + tests only and must not enable
WebFlash / release, must not add an ``artifact_name``, must not publish
firmware, and must not promote ``S360-310`` beyond
``cataloged_unverified``.

Run with::

    python3 tests/test_relay_pinmap_reconcile.py

or::

    python3 -m unittest tests.test_relay_pinmap_reconcile -v
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent

HARDWARE_DIR = REPO_ROOT / "docs" / "hardware"
CORE_CONNECTOR_PINMAP_DOC = HARDWARE_DIR / "s360-100-core-connector-pin-map.md"
CORE_REFERENCE_DOC = HARDWARE_DIR / "s360-100-r4-core.md"
MODULE_PINMAP_DOC = HARDWARE_DIR / "s360-310-module-pinmap.md"
# The S360-310-RELAY-PINMAP-RECONCILE-001 record doc was archived under
# DOCS-DISPOSITION-001 (see docs/archive-index.md); the doc-pinning tests
# went with it. The cross-layer drift guards below remain live.

# Four non-voice Core abstract packages rebound by CORE-ABSTRACT-BUS-001A
# to the schematic-correct ``relay_pin: GPIO3``.
NON_VOICE_CORE_PACKAGES = [
    REPO_ROOT / "packages" / "hardware" / "sense360_core.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_ceiling.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_mapping.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_poe.yaml",
]

FAN_RELAY_PACKAGE = REPO_ROOT / "packages" / "expansions" / "fan_relay.yaml"
CORE_CEILING_PACKAGE = (
    REPO_ROOT / "packages" / "hardware" / "sense360_core_ceiling.yaml"
)

HARDWARE_CATALOG_JSON = REPO_ROOT / "config" / "hardware-catalog.json"
WEBFLASH_BUILDS_JSON = REPO_ROOT / "config" / "webflash-builds.json"
PRODUCT_CATALOG_JSON = REPO_ROOT / "config" / "product-catalog.json"

RELAY_PRODUCT_REL = (
    "products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml"
)

# The canonical relay net per the Core schematic. ``IO3`` on the
# schematic == ``GPIO3`` in ESPHome substitution syntax. Both spellings
# name the same physical ESP32-S3 pin (pin number 3).
CANONICAL_RELAY_PIN_NUMBER = 3


def _substitution_value(text: str, name: str) -> Optional[str]:
    """Return the right-hand value of a ``name: VALUE`` substitution line.

    Mirrors the helper in ``tests/test_core_abstract_bus.py``: skips
    commented-out lines and strips trailing inline comments.
    """
    pattern = re.compile(
        rf"^\s*{re.escape(name)}:\s*(?P<value>\S+)",
        re.MULTILINE,
    )
    for match in pattern.finditer(text):
        line_start = text.rfind("\n", 0, match.start()) + 1
        prefix = text[line_start : match.start()]
        if prefix.lstrip().startswith("#"):
            continue
        raw = match.group("value")
        if "#" in raw:
            raw = raw.split("#", 1)[0].rstrip()
        return raw.strip("\"'")
    return None


def _pin_number(token: Optional[str]) -> Optional[int]:
    """Extract the trailing integer from a ``GPIOn`` / ``IOn`` token."""
    if not token:
        return None
    match = re.search(r"(?:GPIO|IO)(\d+)", token)
    return int(match.group(1)) if match else None


def _relay_io_from_connector_pinmap() -> Optional[int]:
    """Parse the ``Relay`` ESP32 GPIO number from the J4 table.

    Locates the ``### J4 — Relay module connector`` section of the
    canonical Core-side connector pin map and reads the ESP32 GPIO cell
    of the row whose net cell is ``Relay``. Returns the integer pin
    number (e.g. ``3`` for ``IO3``), or ``None`` if the row is not found.
    """
    text = CORE_CONNECTOR_PINMAP_DOC.read_text()
    # Restrict to the J4 section so a ``Relay`` mention elsewhere in the
    # doc cannot be misread as the J4 drive net.
    section = re.split(r"^###\s+J4\b.*$", text, maxsplit=1, flags=re.MULTILINE)
    if len(section) < 2:
        return None
    body = section[1]
    # Stop at the next ``###`` heading.
    body = re.split(r"^###\s", body, maxsplit=1, flags=re.MULTILINE)[0]
    for line in body.splitlines():
        if not line.startswith("|") or "---" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        net = cells[1].strip("`")
        if net == "Relay":
            return _pin_number(cells[2])
    return None


class CanonicalRelayPinAcrossLayersTests(unittest.TestCase):
    """The relay GPIO number agrees across the doc layer and the firmware layer."""

    def test_connector_pinmap_records_relay_on_canonical_pin(self) -> None:
        io = _relay_io_from_connector_pinmap()
        self.assertEqual(
            io,
            CANONICAL_RELAY_PIN_NUMBER,
            f"The canonical Core-side connector pin map "
            f"({CORE_CONNECTOR_PINMAP_DOC.name}) J4 section must record "
            f"the `Relay` net on IO{CANONICAL_RELAY_PIN_NUMBER} "
            f"(schematic-backed per S360-100-R4); parsed {io!r}.",
        )

    def test_core_reference_doc_records_io3_relay(self) -> None:
        text = CORE_REFERENCE_DOC.read_text()
        # The pin-assignment table row ``| IO3 | Relay | ...`` must be
        # present (schematic-backed Relay source pin on the Core side).
        self.assertRegex(
            text,
            r"\bIO3\b[^\n|]*\|\s*Relay\b",
            f"{CORE_REFERENCE_DOC.name} must record the schematic-backed "
            f"`IO3 -> Relay` Core source-pin assignment.",
        )

    def test_module_pinmap_doc_records_relay_on_io3(self) -> None:
        text = MODULE_PINMAP_DOC.read_text()
        self.assertIn(
            "IO3",
            text,
            f"{MODULE_PINMAP_DOC.name} must record the `Relay` net on "
            f"the Core schematic IO3 (J4 / J2 pin 2).",
        )

    def test_every_non_voice_core_package_binds_canonical_relay_pin(self) -> None:
        for pkg in NON_VOICE_CORE_PACKAGES:
            with self.subTest(package=pkg.name):
                self.assertTrue(
                    pkg.is_file(),
                    f"Expected Core abstract package at {pkg}.",
                )
                value = _substitution_value(pkg.read_text(), "relay_pin")
                self.assertEqual(
                    _pin_number(value),
                    CANONICAL_RELAY_PIN_NUMBER,
                    f"relay_pin in {pkg.name} must bind the canonical "
                    f"relay pin GPIO{CANONICAL_RELAY_PIN_NUMBER} "
                    f"(schematic IO{CANONICAL_RELAY_PIN_NUMBER} = Relay); "
                    f"got {value!r}.",
                )

    def test_doc_layer_and_firmware_layer_agree(self) -> None:
        """The number the docs record == the number the packages bind.

        This is the heart of the reconcile guard: the schematic-backed
        doc value (IO3) and the firmware substitution value (GPIO3) are
        the *same pin number*. If either side is edited independently,
        the two numbers diverge and this assertion fails.
        """
        doc_pin = _relay_io_from_connector_pinmap()
        package_pins = {
            pkg.name: _pin_number(
                _substitution_value(pkg.read_text(), "relay_pin")
            )
            for pkg in NON_VOICE_CORE_PACKAGES
        }
        for name, pin in package_pins.items():
            with self.subTest(package=name):
                self.assertEqual(
                    pin,
                    doc_pin,
                    f"relay_pin number in {name} ({pin!r}) must equal the "
                    f"schematic-backed Relay IO number recorded in "
                    f"{CORE_CONNECTOR_PINMAP_DOC.name} ({doc_pin!r}). The "
                    f"doc layer and the firmware layer must not drift "
                    f"apart — reconcile both under "
                    f"S360-310-RELAY-PINMAP-RECONCILE-001.",
                )


class FanRelayPackageStaysAbstractTests(unittest.TestCase):
    """The relay GPIO stays owned by the Core ``${relay_pin}`` abstraction.

    After FW-COMPILE-RELAY-FULL-FIX-001 the FanRelay package proxies the
    Core ``main_relay`` through a ``template`` switch and no longer
    declares its own ``fan_relay_pin`` / ``gpio`` binding. The single
    GPIO owner is the Core ``main_relay`` ``switch.gpio`` on
    ``pin: ${relay_pin}``. This keeps the resolved relay pin abstract so
    the only place the literal ``GPIO3`` lives is the Core abstract
    package substitution — which the cross-layer guard above pins to the
    schematic IO number.
    """

    def test_core_main_relay_binds_relay_pin_substitution(self) -> None:
        text = CORE_CEILING_PACKAGE.read_text()
        pattern = re.compile(
            r"id:\s*main_relay\s*\n"
            r"(?:\s*[a-z_]+:\s*[^\n]+\n)*?"
            r"\s*pin:\s*(?P<pin>\S+)",
            re.MULTILINE,
        )
        match = pattern.search(text)
        self.assertIsNotNone(
            match,
            "sense360_core_ceiling.yaml must declare a `main_relay` "
            "switch.gpio with a `pin:` line.",
        )
        assert match is not None
        self.assertEqual(
            match.group("pin").strip("\"'"),
            "${relay_pin}",
            "the Core `main_relay` must bind `pin: ${relay_pin}` so the "
            "resolved relay GPIO stays abstract (no literal that could "
            "drift from the schematic).",
        )

    def test_fan_relay_names_no_gpio_on_active_line(self) -> None:
        pattern = re.compile(r"\bGPIO\d+\b")
        for line in FAN_RELAY_PACKAGE.read_text().splitlines():
            stripped = line.lstrip()
            if not stripped or stripped.startswith("#"):
                continue
            self.assertIsNone(
                pattern.search(line),
                f"fan_relay.yaml must not name any GPIO on an active line; "
                f"the relay output is owned by the Core `main_relay` on "
                f"${{relay_pin}}. Offending line: {line!r}",
            )


class ReconcileGuardrailTests(unittest.TestCase):
    """Hard guardrails: no WebFlash / release / artifact_name / promotion."""

    def test_s360_310_stays_cataloged_unverified(self) -> None:
        data = json.loads(HARDWARE_CATALOG_JSON.read_text())
        items = {e.get("sku"): e for e in data.get("items", [])}
        entry = items.get("S360-310")
        self.assertIsNotNone(entry, "S360-310 must exist in hardware catalog.")
        assert entry is not None
        self.assertEqual(
            entry.get("schematic_status"),
            "cataloged_unverified",
            "S360-310 schematic_status must stay `cataloged_unverified` "
            "across S360-310-RELAY-PINMAP-RECONCILE-001.",
        )

    def test_no_fan_relay_token_in_webflash_builds(self) -> None:
        text = WEBFLASH_BUILDS_JSON.read_text()
        self.assertNotIn(
            "FanRelay",
            text,
            "config/webflash-builds.json must not contain the FanRelay "
            "token — the reconcile slice does not advance WebFlash / "
            "release.",
        )

    def test_relay_product_has_no_artifact_name_and_no_webflash(self) -> None:
        data = json.loads(PRODUCT_CATALOG_JSON.read_text())
        entry = None
        for product in data.get("products", []):
            if product.get("product_yaml") == RELAY_PRODUCT_REL:
                entry = product
                break
        self.assertIsNotNone(
            entry,
            f"FanRelay product entry ({RELAY_PRODUCT_REL}) must exist in "
            f"the product catalog.",
        )
        assert entry is not None
        self.assertNotIn(
            "artifact_name",
            entry,
            "FanRelay product catalog entry must not declare "
            "artifact_name — the reconcile slice does not build a release "
            "artifact.",
        )
        self.assertEqual(
            entry.get("webflash_build_matrix"),
            False,
            "FanRelay product catalog entry must keep "
            "webflash_build_matrix: false.",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

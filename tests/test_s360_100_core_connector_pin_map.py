#!/usr/bin/env python3
"""S360-100-CONNECTOR-PINMAP-001.

Guards for ``docs/hardware/s360-100-core-connector-pin-map.md`` — the
canonical S360-100 Core-to-module connector pin map.

The doc records, for every per-module connector on the Sense360 Core
(``S360-100``):

1. A canonical connector matrix listing every Core connector with its
   connector ref, attached Sense360 module SKU + friendly name, pin
   count, pin-1 orientation, intended function, and notes / caveats.

2. Per-connector pin tables with the columns Pin number / Core net /
   ESP32 GPIO / Module-side signal / Signal type / Voltage / Status,
   where Status is one of ``verified`` / ``schematic-backed`` /
   ``TBD`` / ``needs silkscreen confirmation``.

3. The architectural-rule restatement that tach / pulse-counter
   signals (``TachIO`` / ``Pul_Cou1..4``) must terminate on native
   ESP32-S3 GPIO; no row may map them through an expander.

4. The do-not-change guardrails: no Release-One / LED-preview
   promotion, no FanRelay / FanPWM / FanDAC release promotion, no
   FanTRIAC HW-005 closure, no PoE-410 closure, no measured RPM
   claim, no WebFlash build / artifact_name flip on the affected
   modules.

5. Cross-doc linking: the new doc is referenced from the Core
   reference doc, the PWM module audit, the room-bundles doc, and
   ``UPCOMING_PR.md``.

Run with::

    python3 tests/test_s360_100_core_connector_pin_map.py
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent

PINMAP_DOC = REPO_ROOT / "docs" / "hardware" / "s360-100-core-connector-pin-map.md"
CORE_REF_DOC = REPO_ROOT / "docs" / "hardware" / "s360-100-r4-core.md"
ARCHITECTURE_DOC = REPO_ROOT / "docs" / "hardware" / "s360-100-core-architecture.md"
PWM_AUDIT_DOC = REPO_ROOT / "docs" / "hardware" / "s360-311-r4-pwm.md"
ROOM_BUNDLES_DOC = REPO_ROOT / "docs" / "sense360-room-bundles.md"
UPCOMING_PR_DOC = REPO_ROOT / "UPCOMING_PR.md"

HARDWARE_CATALOG_JSON = REPO_ROOT / "config" / "hardware-catalog.json"
PRODUCT_CATALOG_JSON = REPO_ROOT / "config" / "product-catalog.json"
WEBFLASH_BUILDS_JSON = REPO_ROOT / "config" / "webflash-builds.json"

# Every Sense360 module SKU that must appear in the connector matrix,
# with its friendly name.
EXPECTED_MODULE_SKUS: Dict[str, str] = {
    "S360-200": "Sense360 RoomIQ",
    "S360-210": "Sense360 AirIQ",
    "S360-211": "Sense360 VentIQ",
    "S360-300": "Sense360 LED",
    "S360-310": "Sense360 Relay",
    "S360-311": "Sense360 PWM",
    "S360-312": "Sense360 DAC",
    "S360-320": "Sense360 TRIAC",
    "S360-410": "Sense360 PoE PSU",
}

# Every Core-side connector reference the matrix must list.
EXPECTED_CONNECTOR_REFS = [
    "J1",
    "J2",
    "J3",
    "J4",
    "J6",
    "J7",
    "J9",
    "J10",
    "J13",
    "J15",
]

# Tach / pulse-counter and per-fan PWM-drive nets that the pin map
# must record as native ESP32-S3 GPIO terminations (architectural rule).
# These match s360-100-core-architecture.md and s360-100-native-fan-gpio-map.md.
EXPECTED_NATIVE_GPIO_TERMINATIONS: Dict[str, str] = {
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

# The four allowed Status values, per the doc's Status-language rules.
ALLOWED_STATUS_VALUES = {
    "verified",
    "schematic-backed",
    "TBD",
    "needs silkscreen confirmation",
}

# Forbidden expander-pin patterns next to a tach signal. If any of these
# regexes co-occurs with a tach / pulse-counter signal, the
# architectural rule has been violated.
FORBIDDEN_EXPANDER_TOKENS_NEAR_TACH = [
    "sx1509",
    "SX1509",
]
TACH_NET_NAMES = list(EXPECTED_NATIVE_GPIO_TERMINATIONS.keys())


class DocExistsTests(unittest.TestCase):
    def test_pinmap_doc_exists(self) -> None:
        self.assertTrue(
            PINMAP_DOC.is_file(),
            f"Canonical Core-to-module connector pin map doc must exist "
            f"at {PINMAP_DOC.relative_to(REPO_ROOT)}.",
        )

    def test_pinmap_doc_declares_its_identifier(self) -> None:
        text = PINMAP_DOC.read_text()
        self.assertIn(
            "S360-100-CONNECTOR-PINMAP-001",
            text,
            "Pin map doc must self-identify as S360-100-CONNECTOR-PINMAP-001.",
        )


class ConnectorMatrixTests(unittest.TestCase):
    def test_matrix_lists_every_expected_module_sku_with_friendly_name(self) -> None:
        text = PINMAP_DOC.read_text()
        for sku, friendly in EXPECTED_MODULE_SKUS.items():
            with self.subTest(sku=sku):
                self.assertIn(
                    sku,
                    text,
                    f"Pin map matrix must list module SKU {sku}.",
                )
                self.assertIn(
                    friendly,
                    text,
                    f"Pin map matrix must name {sku} as {friendly!r}.",
                )

    def test_matrix_lists_every_expected_connector_ref(self) -> None:
        text = PINMAP_DOC.read_text()
        for ref in EXPECTED_CONNECTOR_REFS:
            with self.subTest(connector=ref):
                # Each connector ref must appear as a Markdown-table cell
                # somewhere in the doc (e.g. ``| `J6` |`` or ``§ J6 —``).
                pattern = rf"(`{re.escape(ref)}`|\b{re.escape(ref)}\b)"
                self.assertRegex(
                    text,
                    pattern,
                    f"Pin map must list connector ref {ref}.",
                )

    def test_matrix_includes_required_columns(self) -> None:
        text = PINMAP_DOC.read_text()
        for column in (
            "Connector ref",
            "Connected module",
            "Module SKU",
            "Connector type",
            "Pin count",
            "Pin-1 orientation",
            "Intended function",
        ):
            with self.subTest(column=column):
                self.assertIn(
                    column,
                    text,
                    f"Connector matrix must include the '{column}' column.",
                )

    def test_connector_refs_are_unique_in_matrix(self) -> None:
        # Extract the connector matrix block (between '## Connector matrix'
        # heading and the next '## ' heading). Then check each ref appears
        # at most once as a leading-row marker.
        text = PINMAP_DOC.read_text()
        m = re.search(
            r"## Connector matrix\s*\n(.*?)\n## ",
            text,
            re.DOTALL,
        )
        self.assertIsNotNone(m, "Connector matrix section must be present.")
        block = m.group(1)
        for ref in EXPECTED_CONNECTOR_REFS:
            with self.subTest(connector=ref):
                pattern = rf"^\|\s*`{re.escape(ref)}`\s*\|"
                row_starts = re.findall(pattern, block, re.MULTILINE)
                self.assertEqual(
                    len(row_starts),
                    1,
                    f"Connector ref {ref} must appear exactly once as a "
                    f"matrix-row leading cell (found {len(row_starts)}).",
                )


class PerConnectorPinTableTests(unittest.TestCase):
    def test_required_columns_present(self) -> None:
        text = PINMAP_DOC.read_text()
        for column in (
            "Pin number",
            "Core net / signal",
            "ESP32 GPIO",
            "Module-side signal",
            "Signal type",
            "Voltage",
            "Status",
        ):
            with self.subTest(column=column):
                self.assertIn(
                    column,
                    text,
                    f"Per-connector pin tables must include a '{column}' "
                    f"column header in the schema description.",
                )

    def test_status_vocabulary_is_documented(self) -> None:
        text = PINMAP_DOC.read_text()
        for status in ALLOWED_STATUS_VALUES:
            with self.subTest(status=status):
                self.assertIn(
                    status,
                    text,
                    f"Pin map doc must document the {status!r} status value.",
                )

    def test_only_allowed_status_values_appear_in_pin_rows(self) -> None:
        """The last cell of each per-connector pin-table row must be one
        of the four allowed Status values, or a value that contains one
        as a clear prefix (e.g. ``needs silkscreen confirmation``)."""
        text = PINMAP_DOC.read_text()
        # Find lines that look like pin-table rows ending with one of
        # the allowed status values. We scan all pipe-table rows and
        # then filter to ones that look like a per-pin row (start with
        # a pin number or net token, contain at least 6 columns).
        suspect_rows: List[str] = []
        for line in text.splitlines():
            if not line.startswith("|") or "---" in line:
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 6:
                continue
            # Skip the schema-description table (Pin number / Core net /
            # ESP32 GPIO / Module-side signal / Signal type / Voltage /
            # Status) and the connector matrix (Connector ref / Connected
            # module / Module SKU / Connector type / Pin count /
            # Pin-1 orientation / Intended function / Notes).
            if cells[0] in {
                "Column",
                "Connector ref",
                "Pin",
                "Pin number",
                "Domain identifier",
                "Pin range",
                "Field",
            }:
                continue
            last = cells[-1].lower()
            # Try to match a row with one of the four allowed status values
            # at the end. If we recognize the row as a pin-table row by
            # status-value tail, validate it.
            tail_match = None
            for status in ALLOWED_STATUS_VALUES:
                s = status.lower()
                if last == s or last.endswith(s):
                    tail_match = status
                    break
            # Filter rows that look like pin rows: the first cell is a
            # pin number (1..N) or a USB-C pin label (VBUS / D+ / D- /
            # CC1 / CC2 / SBU1 / SBU2 / SHIELD).
            first = cells[0]
            looks_like_pin_row = (
                first.isdigit()
                or first in {"VBUS", "D+", "D-", "CC1", "CC2", "SBU1 / SBU2", "SHIELD"}
            )
            if not looks_like_pin_row:
                continue
            if tail_match is None:
                suspect_rows.append(line)
        self.assertEqual(
            suspect_rows,
            [],
            "Every per-connector pin-table row must end with one of the "
            "four allowed Status values (verified / schematic-backed / "
            "TBD / needs silkscreen confirmation). Suspect rows: "
            + "\n".join(suspect_rows),
        )


class NativeGpioRuleTests(unittest.TestCase):
    def test_pinmap_records_schematic_printed_gpio_for_each_tach_net(self) -> None:
        text = PINMAP_DOC.read_text()
        for net, gpio in EXPECTED_NATIVE_GPIO_TERMINATIONS.items():
            with self.subTest(net=net):
                pattern = (
                    rf"`{re.escape(net)}`[^\n]{{0,400}}`{re.escape(gpio)}`"
                )
                self.assertRegex(
                    text,
                    pattern,
                    f"Pin map must record {net} → {gpio} (native ESP32-S3 "
                    f"GPIO termination per the canonical R4 schematic).",
                )

    def test_no_tach_signal_is_mapped_through_an_expander(self) -> None:
        text = PINMAP_DOC.read_text()
        # Scan only the per-connector pin tables / matrix rows; not the
        # narrative which legitimately discusses the SX1509 historical
        # path.
        violations: List[str] = []
        for line in text.splitlines():
            if not line.startswith("|") or "---" in line:
                continue
            # If this line names a tach signal and also names an SX1509
            # token, it would be a violation. We deliberately exclude
            # rows that flag the SX1509 path as removed / superseded /
            # forbidden — those carry words like 'removed', 'superseded',
            # 'forbidden', 'no row', 'no tach', 'historical', 'legacy',
            # 'must NOT', 'must not'.
            mentions_tach = any(net in line for net in TACH_NET_NAMES)
            mentions_expander = any(
                token in line for token in FORBIDDEN_EXPANDER_TOKENS_NEAR_TACH
            )
            if mentions_tach and mentions_expander:
                lower = line.lower()
                if any(
                    safe in lower
                    for safe in (
                        "removed",
                        "superseded",
                        "forbidden",
                        "historical",
                        "legacy",
                        "must not",
                        "must NOT",
                        "no row",
                        "no tach",
                    )
                ):
                    continue
                violations.append(line)
        self.assertEqual(
            violations,
            [],
            "Pin map must not map any tach / pulse-counter signal "
            "through the SX1509 expander. Violations:\n"
            + "\n".join(violations),
        )


class DoNotChangeGuardrailsTests(unittest.TestCase):
    def _load_json(self, path: Path) -> dict:
        with path.open() as fh:
            return json.load(fh)

    def test_s360_311_stays_cataloged_unverified(self) -> None:
        data = self._load_json(HARDWARE_CATALOG_JSON)
        s311 = next(
            (e for e in data.get("items", []) if e.get("sku") == "S360-311"),
            None,
        )
        self.assertIsNotNone(s311, "S360-311 row must exist in hardware catalog.")
        self.assertEqual(
            s311.get("schematic_status"),
            "cataloged_unverified",
            "S360-311 schematic_status must stay `cataloged_unverified` "
            "across S360-100-CONNECTOR-PINMAP-001.",
        )

    def test_s360_310_stays_cataloged_unverified(self) -> None:
        data = self._load_json(HARDWARE_CATALOG_JSON)
        s310 = next(
            (e for e in data.get("items", []) if e.get("sku") == "S360-310"),
            None,
        )
        self.assertIsNotNone(s310, "S360-310 row must exist in hardware catalog.")
        self.assertEqual(
            s310.get("schematic_status"),
            "cataloged_unverified",
            "S360-310 schematic_status must stay `cataloged_unverified` "
            "across S360-100-CONNECTOR-PINMAP-001.",
        )

    def test_s360_312_stays_cataloged_unverified(self) -> None:
        data = self._load_json(HARDWARE_CATALOG_JSON)
        s312 = next(
            (e for e in data.get("items", []) if e.get("sku") == "S360-312"),
            None,
        )
        self.assertIsNotNone(s312, "S360-312 row must exist in hardware catalog.")
        self.assertEqual(
            s312.get("schematic_status"),
            "cataloged_unverified",
            "S360-312 schematic_status must stay `cataloged_unverified` "
            "across S360-100-CONNECTOR-PINMAP-001.",
        )

    def test_s360_320_stays_cataloged_unverified(self) -> None:
        data = self._load_json(HARDWARE_CATALOG_JSON)
        s320 = next(
            (e for e in data.get("items", []) if e.get("sku") == "S360-320"),
            None,
        )
        self.assertIsNotNone(s320, "S360-320 row must exist in hardware catalog.")
        self.assertEqual(
            s320.get("schematic_status"),
            "cataloged_unverified",
            "S360-320 schematic_status must stay `cataloged_unverified` "
            "across S360-100-CONNECTOR-PINMAP-001.",
        )

    def test_s360_410_stays_cataloged_unverified(self) -> None:
        data = self._load_json(HARDWARE_CATALOG_JSON)
        s410 = next(
            (e for e in data.get("items", []) if e.get("sku") == "S360-410"),
            None,
        )
        self.assertIsNotNone(s410, "S360-410 row must exist in hardware catalog.")
        self.assertEqual(
            s410.get("schematic_status"),
            "cataloged_unverified",
            "S360-410 schematic_status must stay `cataloged_unverified` "
            "across S360-100-CONNECTOR-PINMAP-001 — PoE PSU blocker "
            "chain is separate.",
        )

    def test_no_fanpwm_in_webflash_builds(self) -> None:
        data = self._load_json(WEBFLASH_BUILDS_JSON)
        builds = data.get("builds", []) if isinstance(data, dict) else []
        for row in builds:
            cfg = row.get("config_string", "")
            with self.subTest(config_string=cfg):
                self.assertNotIn(
                    "FanPWM",
                    cfg,
                    "FanPWM must not appear in any WebFlash build across "
                    "S360-100-CONNECTOR-PINMAP-001.",
                )

    def test_fanpwm_products_keep_no_rpm_claim(self) -> None:
        data = self._load_json(PRODUCT_CATALOG_JSON)
        for entry in data.get("products", []):
            cfg = entry.get("config_string") or entry.get("name") or ""
            if "FanPWM" not in str(cfg):
                continue
            with self.subTest(config=cfg):
                self.assertNotEqual(
                    entry.get("rpm_supported"),
                    True,
                    f"{cfg}: rpm_supported must not be True across "
                    f"S360-100-CONNECTOR-PINMAP-001.",
                )
                self.assertFalse(
                    bool(entry.get("webflash_build_matrix")),
                    f"{cfg}: webflash_build_matrix must stay false.",
                )

    def test_doc_does_not_claim_release_readiness(self) -> None:
        text = PINMAP_DOC.read_text()
        # The pin map doc is documentation-only; it must not make
        # release-readiness claims for the affected modules. These
        # phrases were checked specifically because they are the typical
        # ways such claims would be smuggled in.
        forbidden_phrases = [
            "stable-release",
            "release-eligible",
            "release ready",
            "release-ready",
            "webflash-ready",
            "rpm_supported: true",
            "rpm_supported = true",
        ]
        lower = text.lower()
        violations = [p for p in forbidden_phrases if p.lower() in lower]
        self.assertEqual(
            violations,
            [],
            "Pin map doc must not contain release-readiness claims: "
            f"{violations}",
        )

    def test_doc_does_not_advance_fan_triac_blocker(self) -> None:
        text = PINMAP_DOC.read_text().lower()
        # The doc must keep FanTRIAC HW-005 blocked; it may say
        # 'blocked' / 'unchanged' / 'not advanced' but must not flip
        # it to resolved / closed / unblocked.
        for forbidden in (
            "hw-005 resolved",
            "hw-005 closed",
            "fan triac unblocked",
            "fan triac resolved",
            "fantriac resolved",
            "fantriac unblocked",
        ):
            with self.subTest(phrase=forbidden):
                self.assertNotIn(
                    forbidden,
                    text,
                    f"Pin map must not advance FanTRIAC HW-005 (phrase: "
                    f"{forbidden!r}).",
                )

    def test_doc_does_not_advance_poe_410_blocker(self) -> None:
        text = PINMAP_DOC.read_text().lower()
        for forbidden in (
            "package-poe-410-001 resolved",
            "package-poe-410-001 closed",
            "s360-410 verified",
            "poe psu verified",
        ):
            with self.subTest(phrase=forbidden):
                self.assertNotIn(
                    forbidden,
                    text,
                    f"Pin map must not advance PACKAGE-POE-410-001 "
                    f"(phrase: {forbidden!r}).",
                )


class CrossDocLinkingTests(unittest.TestCase):
    LINK_NEEDLE = "s360-100-core-connector-pin-map.md"

    DOCS_THAT_MUST_LINK_TO_PINMAP_DOC = [
        CORE_REF_DOC,
        PWM_AUDIT_DOC,
        ROOM_BUNDLES_DOC,
        UPCOMING_PR_DOC,
    ]

    def test_pinmap_doc_is_cross_linked(self) -> None:
        for path in self.DOCS_THAT_MUST_LINK_TO_PINMAP_DOC:
            with self.subTest(file=path.relative_to(REPO_ROOT).as_posix()):
                self.assertIn(
                    self.LINK_NEEDLE,
                    path.read_text(),
                    f"{path.name} must link to "
                    f"docs/hardware/s360-100-core-connector-pin-map.md.",
                )

    def test_pinmap_doc_references_canonical_sources(self) -> None:
        text = PINMAP_DOC.read_text()
        for needle in (
            "s360-100-r4-core.md",
            "s360-100-core-architecture.md",
            "s360-100-native-fan-gpio-map.md",
            "s360-100-native-tach-pulse-strategy.md",
        ):
            with self.subTest(reference=needle):
                self.assertIn(
                    needle,
                    text,
                    f"Pin map must cross-reference {needle}.",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)

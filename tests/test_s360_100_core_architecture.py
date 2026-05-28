#!/usr/bin/env python3
"""S360-100-NATIVE-TACH-PULSE-001 — R4 refresh.

Guards for ``docs/hardware/s360-100-core-architecture.md`` — the
canonical S360-100 Core architecture index. The doc records:

1. The Sense360 Core (``S360-100``) is the central Core / backplane
   controller; every Sense360 module attaches via a dedicated Core
   connector; every room bundle derives from
   **``S360-100`` Core + room modules + ``S360-410`` PoE PSU**.

2. The current canonical S360-100 Core schematic evidence is
   ``docs/hardware/schematics/S360-100-R4.pdf`` (SHA256
   ``4c9e8b06d129fbb55f61e143b648e03762d06cb4dc67fe3120c268cd3a4bdf16``,
   837,443 bytes, KiCad E.D.A. 10.0.3, single sheet ``1/1``). The PDF
   file must exist on disk and match those bytes.

3. The connector / module matrix lists each Core connector together
   with its attached Sense360 module SKU and the signal family it
   carries (S360-200 RoomIQ, S360-210 AirIQ, S360-211 VentIQ,
   S360-300 LED, S360-310 Relay, S360-311 PWM, S360-312 DAC,
   S360-320 TRIAC, S360-410 PoE PSU).

4. The schematic-printed pin-allocation table records, for every
   ``TachIO`` / ``Pul_Cou1..4`` / ``TachPMW1..4`` net, the native
   ESP32-S3 GPIO termination printed on the new R4 sheet. None of
   those rows may be allowed to silently claim **bench-verified**;
   the table must continue to mark every row "**Not** — not
   bench-verified" so the architectural rule (native-GPIO termination
   is a schematic-side property only; firmware-binding and bench
   evidence are separate gates) is not eroded.

5. The do-not-change guardrails forbid promoting S360-311 /
   S360-410 / FanTRIAC / Release-One / LED-preview / firmware /
   release artifacts / WebFlash build matrix / `rpm_supported`
   posture as a side-effect of this docs PR.

Run with::

    python3 tests/test_s360_100_core_architecture.py
"""

from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path
from typing import Dict, Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent

ARCHITECTURE_DOC = REPO_ROOT / "docs" / "hardware" / "s360-100-core-architecture.md"
STRATEGY_DOC = REPO_ROOT / "docs" / "hardware" / "s360-100-native-tach-pulse-strategy.md"
CORE_REF_DOC = REPO_ROOT / "docs" / "hardware" / "s360-100-r4-core.md"
ARTIFACT_INDEX_DOC = REPO_ROOT / "docs" / "hardware" / "artifacts" / "S360-100-R4.md"
ROOM_BUNDLES_DOC = REPO_ROOT / "docs" / "sense360-room-bundles.md"
BLOCKER_BURNDOWN_DOC = REPO_ROOT / "docs" / "blocker-burndown.md"

SCHEMATIC_PDF = REPO_ROOT / "docs" / "hardware" / "schematics" / "S360-100-R4.pdf"
HARDWARE_CATALOG_JSON = REPO_ROOT / "config" / "hardware-catalog.json"
PRODUCT_CATALOG_JSON = REPO_ROOT / "config" / "product-catalog.json"
WEBFLASH_BUILDS_JSON = REPO_ROOT / "config" / "webflash-builds.json"

EXPECTED_PDF_SHA256 = "4c9e8b06d129fbb55f61e143b648e03762d06cb4dc67fe3120c268cd3a4bdf16"
EXPECTED_PDF_BYTES = 837443

# Sense360 module SKUs and the friendly name the architecture doc must
# advertise alongside each one in the connector / module matrix. The
# matrix lists module SKUs (S360-200..S360-320) plus the off-board PoE
# PSU inlet (S360-410).
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

# Tach / pulse-counter and per-fan PWM-drive nets that the architecture
# doc must record as schematic-printed native ESP32-S3 GPIO terminations.
# The exact pin numbers come from the new R4 schematic.
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


class CanonicalSchematicEvidenceTests(unittest.TestCase):
    """Rule (2): the refreshed canonical S360-100 Core schematic PDF is
    committed on disk and matches the recorded SHA256 + byte length.
    """

    def test_schematic_pdf_exists(self) -> None:
        self.assertTrue(
            SCHEMATIC_PDF.is_file(),
            f"Canonical S360-100 Core schematic PDF must exist at "
            f"{SCHEMATIC_PDF.relative_to(REPO_ROOT)}.",
        )

    def test_schematic_pdf_matches_recorded_sha256_and_size(self) -> None:
        data = SCHEMATIC_PDF.read_bytes()
        actual_sha = hashlib.sha256(data).hexdigest()
        self.assertEqual(
            len(data),
            EXPECTED_PDF_BYTES,
            f"PDF byte length mismatch: expected {EXPECTED_PDF_BYTES}, "
            f"got {len(data)}.",
        )
        self.assertEqual(
            actual_sha,
            EXPECTED_PDF_SHA256,
            f"PDF SHA256 mismatch: expected {EXPECTED_PDF_SHA256}, got "
            f"{actual_sha}. Refresh the architecture doc, artifact "
            f"index, and this test's EXPECTED_PDF_SHA256 / "
            f"EXPECTED_PDF_BYTES constants together — never silently.",
        )

    def test_architecture_doc_records_pdf_sha256_and_size(self) -> None:
        self.assertTrue(ARCHITECTURE_DOC.is_file())
        text = ARCHITECTURE_DOC.read_text()
        self.assertIn(
            EXPECTED_PDF_SHA256,
            text,
            "Architecture doc must record the canonical PDF SHA256.",
        )
        self.assertIn(
            "837,443 bytes",
            text,
            "Architecture doc must record the canonical PDF byte length.",
        )

    def test_hardware_catalog_s360_100_points_at_committed_pdf(self) -> None:
        with HARDWARE_CATALOG_JSON.open() as fh:
            data = json.load(fh)
        s100 = next(
            (e for e in data.get("items", []) if e.get("sku") == "S360-100"),
            None,
        )
        self.assertIsNotNone(s100, "S360-100 row must exist in hardware catalog.")
        self.assertEqual(
            s100.get("schematic_file"),
            "docs/hardware/schematics/S360-100-R4.pdf",
            "S360-100 schematic_file must continue to point at the "
            "refreshed canonical PDF path.",
        )
        # The catalog status must NOT be silently relaxed by the refresh.
        self.assertEqual(
            s100.get("schematic_status"),
            "verified",
            "S360-100 schematic_status must remain `verified` across the "
            "R4 refresh (no status flip).",
        )


class CoreHubFramingTests(unittest.TestCase):
    """Rule (1): the architecture doc establishes the Sense360 Core
    (``S360-100``) as the central hub of the room / module stack.
    """

    def test_architecture_doc_exists(self) -> None:
        self.assertTrue(
            ARCHITECTURE_DOC.is_file(),
            "docs/hardware/s360-100-core-architecture.md must exist.",
        )

    def test_architecture_doc_calls_core_central(self) -> None:
        text = ARCHITECTURE_DOC.read_text().lower()
        self.assertRegex(
            text,
            r"\bcentral\s+core\b",
            "Architecture doc must explicitly call the Sense360 Core "
            "(S360-100) the central Core / backplane controller.",
        )
        self.assertIn(
            "esp32-s3-wroom-1-n16r8",
            text,
            "Architecture doc must name the MCU "
            "(ESP32-S3-WROOM-1-N16R8).",
        )

    def test_architecture_doc_states_bundle_recipe(self) -> None:
        # Bundle = Core + room modules + PoE PSU. The recipe appears as
        # a 3-item bullet list around the "A room bundle" sentence, so
        # the search spans multiple lines (use DOTALL).
        text = ARCHITECTURE_DOC.read_text()
        self.assertIsNotNone(
            re.search(
                r"S360-100\s+Core.{0,800}room\s+modules.{0,800}S360-410",
                text,
                re.DOTALL,
            ),
            "Architecture doc must state every room bundle derives "
            "from S360-100 Core + room modules + S360-410 PoE PSU.",
        )


class ConnectorModuleMatrixTests(unittest.TestCase):
    """Rule (3): the connector / module matrix lists every Sense360
    module SKU together with its friendly name.
    """

    def test_matrix_lists_every_expected_module_sku(self) -> None:
        text = ARCHITECTURE_DOC.read_text()
        for sku, friendly in EXPECTED_MODULE_SKUS.items():
            with self.subTest(sku=sku):
                self.assertIn(
                    sku,
                    text,
                    f"Connector / module matrix must list {sku}.",
                )
                self.assertIn(
                    friendly,
                    text,
                    f"Connector / module matrix must name {sku} as "
                    f"{friendly!r}.",
                )

    def test_matrix_records_native_mcu_requirement_column(self) -> None:
        text = ARCHITECTURE_DOC.read_text()
        # The matrix must contain a "Native MCU requirement" column so the
        # native-GPIO architectural rule is recorded per connector.
        self.assertIn(
            "Native MCU requirement",
            text,
            "Connector / module matrix must include a "
            "'Native MCU requirement' column.",
        )


class NativeGpioPinAllocationTableTests(unittest.TestCase):
    """Rule (4): the schematic-printed pin-allocation table records,
    for every TachIO / Pul_Cou1..4 / TachPMW1..4 net, the native
    ESP32-S3 GPIO termination — and never claims bench-verified.
    """

    def test_table_records_schematic_printed_gpio_for_each_net(self) -> None:
        text = ARCHITECTURE_DOC.read_text()
        for net, gpio in EXPECTED_NATIVE_GPIO_TERMINATIONS.items():
            with self.subTest(net=net):
                # Net name and GPIO id must co-occur within ~200 chars
                # (in the same table row).
                pattern = (
                    rf"`{re.escape(net)}`[^\n]{{0,400}}`{re.escape(gpio)}`"
                )
                self.assertRegex(
                    text,
                    pattern,
                    f"Pin-allocation table must record {net} → {gpio} "
                    f"(native ESP32-S3 GPIO termination per new R4 "
                    f"schematic).",
                )

    def test_table_does_not_claim_bench_verified(self) -> None:
        text = ARCHITECTURE_DOC.read_text()
        # The "Bench-verified?" column must contain "No" rows; no row may
        # silently flip to "Yes" without dedicated bench evidence.
        bench_yes_rows = re.findall(
            r"\|\s*Pul_Cou\d[^|]*\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|\s*\*\*Yes\*\*",
            text,
        )
        self.assertEqual(
            bench_yes_rows,
            [],
            "Pin-allocation table must not claim any Pul_Cou row as "
            "bench-verified (S360-311-CURRENT-THERMAL-001 owns bench "
            "evidence).",
        )
        # Strategy doc must also not be allowed to silently flip the
        # pending-table firmware-binding column to "Bound".
        strat = STRATEGY_DOC.read_text()
        bind_yes = re.findall(
            r"\|\s*`Pul_Cou\d`[^|]*\|[^|]*\|[^|]*\|[^|]*\|\s*Bound\b",
            strat,
        )
        self.assertEqual(
            bind_yes,
            [],
            "Strategy doc pending pin-allocation table must not claim "
            "Pul_Cou* as Bound in firmware (no firmware-binding edit "
            "by this PR).",
        )


class DoNotChangeGuardrailsTests(unittest.TestCase):
    """Rule (5): the R4 refresh PR must not silently promote anything."""

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
            "across the R4 refresh — no measured native-GPIO tach "
            "evidence exists.",
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
            "across the R4 refresh — PoE PSU blocker chain is separate.",
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
                    "the R4 refresh (S360-100-NATIVE-TACH-PULSE-001).",
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
                    f"{cfg}: rpm_supported must not be True across the "
                    f"R4 refresh — no measured tach evidence.",
                )
                self.assertFalse(
                    bool(entry.get("webflash_build_matrix")),
                    f"{cfg}: webflash_build_matrix must stay false.",
                )


class CrossDocLinkingTests(unittest.TestCase):
    """Cross-doc linking: the architecture doc must be referenced from
    the strategy doc, the Core hardware-reference doc, the artifact
    index, the room-bundles doc, and the blocker-burndown row that
    cites the architectural rule.
    """

    LINK_NEEDLE = "s360-100-core-architecture.md"

    DOCS_THAT_MUST_LINK_TO_ARCHITECTURE_DOC = [
        STRATEGY_DOC,
        CORE_REF_DOC,
        ARTIFACT_INDEX_DOC,
        ROOM_BUNDLES_DOC,
        BLOCKER_BURNDOWN_DOC,
    ]

    def test_architecture_doc_is_cross_linked(self) -> None:
        for path in self.DOCS_THAT_MUST_LINK_TO_ARCHITECTURE_DOC:
            with self.subTest(file=path.relative_to(REPO_ROOT).as_posix()):
                self.assertIn(
                    self.LINK_NEEDLE,
                    path.read_text(),
                    f"{path.name} must link to "
                    f"docs/hardware/s360-100-core-architecture.md.",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)

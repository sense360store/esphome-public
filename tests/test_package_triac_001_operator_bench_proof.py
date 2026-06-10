#!/usr/bin/env python3
"""PACKAGE-TRIAC-001 invariants for the FanTRIAC operator bench proof doc.

PACKAGE-TRIAC-001 authored the operator bench *proof container* for the
blocked ``Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`` product:
``docs/package-triac-001-operator-bench-proof.md``. The container started
``PENDING`` (#728), ``PACKAGE-TRIAC-001-PARAMS`` (#738) recorded the
partial bench (Steps A, B, C, E PASS on the real Manrose fan motor) and
folded the bench-confirmed parameters into
``packages/expansions/fan_triac.yaml``, and ``PACKAGE-TRIAC-001-CLOSE``
recorded the operator-reported Step F results (cold boots / warm reboots /
stability soak — PASS; evidence class: operator observation, no log
capture): Steps A–F all PASS. ``PACKAGE-TRIAC-001-RECONFIRM-001`` then
recorded the operator's closure of the full-composition re-confirm via
closure path (a) — his explicit statement, 2026-06-10, that the Step F
image was the full composition. The re-confirm exists to check that the
sensor stack's I2C traffic, the LD2450 UART, and WiFi activity do not
perturb the dimmer timing; production parameters alone cannot prove
that, which is why the row waited for the explicit statement instead of
being inferred. ``PACKAGE-TRIAC-001-ATTEST-CLOSE`` then recorded the
operator-reported bench-fact corrections — every bench run (including
the Step F boot/reboot cycles previously dated 2026-06-09) ran on
2026-06-08, and local logs WERE captured on the bench laptop but are
not attached to the record (nothing implies they were reviewed or
attached) — and staged the final close-out: the status flips to
OPERATOR ATTESTATION RECORDED BELOW, next steps point solely at the
commissioning PR (``TRIAC-COMMISSIONING-001``), and a designed-to-fail
guard below holds the close-out branch red until the operator himself
fills the Operator and Signature cells (the cells are staged EMPTY; no
attestation content is ever machine-written).

These tests pin the close-out invariants so a regression cannot:

  * fabricate a *cleared blocker* out of the lettered-steps close — the
    catalog keeps ``status: blocked`` and the doc must keep saying the
    close-out does not clear ``PACKAGE-TRIAC-001``;
  * drop the publish-posture statement — BLOCKED / reference-only, never
    stable / recommended / default / buyable / WebFlash-exposed, pending
    the commissioning PR and the COMPLIANCE-001-RESOLUTION-001
    experimental-lane preconditions;
  * launder the Step F evidence class — every Step F row is operator
    observation with local logs captured on the bench but not attached
    to this record, and must say so (the superseded no-log-capture
    wording must not come back, and nothing may imply the logs were
    reviewed or attached);
  * launder the full-composition re-confirm closure — the row records
    PASS via closure path (a), the operator's explicit, dated statement
    (never an inference from production parameters), and the rejected
    covered-by-Step-F wording must never come back;
  * drift the schematic-verified pin mapping the bench depended on
    (gate ``GPIO14`` = ``TRI_GPIO1`` -> U1 MOC3023M; zero-cross
    ``GPIO13`` = ``TRI_GPIO2`` -> OK1 EL814);
  * silently promote the FanTRIAC product off its ``status: blocked``
    posture or flip ``webflash_build_matrix`` while PACKAGE-TRIAC-001 and
    the COMPLIANCE-001-RESOLUTION-001 experimental-lane preconditions are
    still the recorded gates (COMPLIANCE-001 itself is CLOSED by market
    posture per docs/decisions/COMPLIANCE-001-RESOLUTION-001.md; the
    cited reason changed, the enforced behaviour did not).

After the operator attests, the human-reviewed commissioning PR that
clears the PACKAGE-TRIAC-001 half of the blocker updates the catalog,
the doc, and this test together
(the COMPLIANCE-001-RESOLUTION-001 experimental-lane entry still gates
the publish).

Run with::

    python3 tests/test_package_triac_001_operator_bench_proof.py

or::

    python3 -m unittest tests.test_package_triac_001_operator_bench_proof -v
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any, Iterator

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs" / "package-triac-001-operator-bench-proof.md"
CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"
VARIANTS_PATH = REPO_ROOT / "config" / "room-bundle-fan-variants.json"

FANTRIAC_CONFIG = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"

STEP_F_EVIDENCE_CLASS = (
    "operator observation; local logs captured, not attached to this record"
)
# The wording PACKAGE-TRIAC-001-ATTEST-CLOSE superseded (operator-reported
# correction: local logs WERE captured on the bench laptop, not attached).
STEP_F_EVIDENCE_CLASS_SUPERSEDED = "operator observation, no log capture"


def _walk(obj: Any) -> Iterator[Any]:
    """Yield every node in a nested JSON structure (dicts, lists, scalars)."""
    yield obj
    if isinstance(obj, dict):
        for value in obj.values():
            yield from _walk(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from _walk(item)


class TestPackageTriac001OperatorBenchProofDoc(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = DOC_PATH.read_text(encoding="utf-8")
        cls.lines = cls.text.splitlines()
        cls.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        cls.variants = json.loads(VARIANTS_PATH.read_text(encoding="utf-8"))
        cls.fantriac = cls._find_fantriac_product(cls.catalog)

    @staticmethod
    def _find_fantriac_product(catalog: dict) -> dict:
        for product in catalog.get("products", []):
            if product.get("config_string") == FANTRIAC_CONFIG:
                return product
        raise AssertionError(
            f"{FANTRIAC_CONFIG} missing from config/product-catalog.json"
        )

    # --- the proof container itself ------------------------------------

    def test_doc_exists_with_blocker_id_title(self) -> None:
        self.assertTrue(DOC_PATH.is_file(), f"missing {DOC_PATH}")
        first_line = self.lines[0]
        self.assertTrue(first_line.startswith("# "), "doc must open with an H1")
        self.assertIn("PACKAGE-TRIAC-001", first_line)
        self.assertIn("Operator Bench Proof", first_line)

    def test_status_steps_and_reconfirm_complete_attestation_recorded(self) -> None:
        self.assertIn(
            "**Status:** STEPS A–F AND FULL-COMPOSITION RE-CONFIRM COMPLETE "
            "— OPERATOR ATTESTATION RECORDED BELOW",
            self.text,
        )
        self.assertIn("Steps A through F all recorded PASS", self.text)
        # Operator-reported dating correction (ATTEST-CLOSE): every bench
        # run was 2026-06-08; only the re-confirm statement and the signing
        # are dated 2026-06-10. The superseded 2026-06-09 run dating must
        # not come back anywhere in the record.
        self.assertIn("bench runs of 2026-06-08", self.text)
        self.assertNotIn("2026-06-09", self.text)
        # The close-out must say, in the status line itself, that it does
        # not clear the blocker.
        self.assertIn(
            "does **not** clear `PACKAGE-TRIAC-001`",
            self.text,
        )
        # The stale pre-close and pre-attestation claims must be gone.
        self.assertNotIn("operator bench not yet run", self.text)
        self.assertNotIn("PENDING OPERATOR ATTESTATION ONLY", self.text)

    def test_docs_only_scope_declared(self) -> None:
        self.assertIn("Operator-evidence record. Docs only.", self.text)
        self.assertIn(
            "asserts **no** firmware, manifest, release, or WebFlash change",
            self.text,
        )

    def test_no_compliance_claim_and_compliance_remains_gate(self) -> None:
        # The bench proves timing/waveform/thermal, never electrical safety.
        # COMPLIANCE-001 is CLOSED by posture (COMPLIANCE-001-RESOLUTION-001);
        # the doc must cite the resolution record and keep the safety topics
        # out of the bench's scope, with the experimental-lane entry as the
        # remaining publish gate. Behaviour is unchanged: still not published,
        # not buyable, not kit-exposed.
        self.assertIn("makes **no** isolation, creepage, clearance, EMI", self.text)
        self.assertIn("COMPLIANCE-001 was closed by posture", self.text)
        self.assertIn(
            "`COMPLIANCE-001-RESOLUTION-001` experimental-lane entry as the "
            "sole remaining gate",
            self.text,
        )
        self.assertIn("never a safety or compliance claim", self.text)

    def test_schematic_verified_pin_mapping(self) -> None:
        for needle in (
            "gate `GPIO14`",
            "zero-cross `GPIO13`",
            "`TRI_GPIO1`",
            "`TRI_GPIO2`",
            "MOC3023M",
            "EL814",
        ):
            self.assertIn(needle, self.text, f"pin-mapping detail missing: {needle}")

    def test_bench_firmware_uses_production_pins(self) -> None:
        self.assertIn("gate_pin: GPIO14", self.text)
        self.assertIn("number: GPIO13", self.text)
        self.assertIn("platform: ac_dimmer", self.text)
        # Leading-edge phase cut for a latching TRIAC.
        self.assertIn("method: leading", self.text)

    # --- the Step F close-out record ------------------------------------

    def test_step_f_rows_carry_operator_evidence_class(self) -> None:
        # Every Step F capture row is operator-reported, with local logs
        # captured on the bench laptop but not attached to this record, and
        # the table must say so on each row.
        step_f = self.text.split("### Step F", 1)[1].split(
            "### Full-composition re-confirm", 1
        )[0]
        capture_rows = [
            line
            for line in step_f.splitlines()
            if line.startswith("| ")
            and not line.startswith("| Capture")
            and "---" not in line
        ]
        self.assertEqual(
            len(capture_rows),
            4,
            "Step F records the four operator-reported result groups "
            "(cold boots, warm reboots, stability soak, supplementary speed "
            f"check); found {len(capture_rows)} rows",
        )
        for row in capture_rows:
            self.assertIn(
                STEP_F_EVIDENCE_CLASS,
                row,
                f"Step F row missing its evidence class: {row}",
            )
        # The superseded no-log-capture wording must not come back anywhere.
        self.assertNotIn(STEP_F_EVIDENCE_CLASS_SUPERSEDED, self.text)
        self.assertIn("**Step F result: PASS (Manrose fan motor)", self.text)

    def test_close_out_marks_all_steps_pass(self) -> None:
        self.assertIn(
            "## Close-out — Steps A–F and full-composition re-confirm "
            "complete, operator attestation recorded below",
            self.text,
        )
        for needle in (
            "| A — zero-cross detection | PASS |",
            "| B — gate firing | PASS |",
            "| C — load waveform (mains side, real fan) | PASS |",
            "| D — locked parameters | PASS",
            "| E — thermal soak | PASS |",
            "| F — stability and boot | PASS (operator observation; "
            "local logs captured, not attached to this record) |",
        ):
            self.assertIn(needle, self.text, f"close-out step row missing: {needle}")
        # Hardware and locked parameters travel with the close-out.
        self.assertIn("S360-100-R4 Core + S360-320-R4 TRIAC", self.text)
        self.assertIn("Manrose fan motor (real inductive load)", self.text)
        self.assertIn("`restore_mode: RESTORE_DEFAULT_OFF`", self.text)
        self.assertIn("`init_with_half_cycle: true`", self.text)
        self.assertIn("`min_power: 15%`", self.text)

    def test_close_out_keeps_publish_posture_blocked(self) -> None:
        self.assertIn(
            "Closure of `PACKAGE-TRIAC-001` does not change the publish posture.",
            self.text,
        )
        self.assertIn(
            "remains BLOCKED / reference-only: never stable, "
            "never recommended, never default, never buyable, never "
            "WebFlash-exposed",
            self.text,
        )
        # The gate framing is the resolution record, not an open
        # COMPLIANCE-001 assessment.
        self.assertIn(
            "pending the commissioning PR and the "
            "`COMPLIANCE-001-RESOLUTION-001` experimental-lane preconditions",
            self.text,
        )

    def test_full_composition_reconfirm_not_marked_by_inference(self) -> None:
        # The re-confirm exists to check that the full product firmware
        # (sensor-stack I2C traffic, LD2450 UART, WiFi activity) does not
        # perturb the dimmer timing. Production parameters cannot prove
        # that; only the image identity can. The row closed via closure
        # path (a) — the operator's explicit, dated statement that the
        # Step F image was the full composition
        # (PACKAGE-TRIAC-001-RECONFIRM-001, 2026-06-10) — a deliberate,
        # human-reviewed doc + test edit, never an inference. Pin the
        # recorded closure: the path, the quoted statement, the date, and
        # the absence of both the stale open state and the rejected
        # PASS-by-inference wording.
        self.assertIn("### Full-composition re-confirm", self.text)
        reconfirm = self.text.split("### Full-composition re-confirm", 1)[1].split(
            "## Close-out", 1
        )[0]
        self.assertIn("PASS — closed via closure path (a) on 2026-06-10", reconfirm)
        self.assertIn(
            '"the Step F image was the full '
            'Ceiling-POE-VentIQ-FanTRIAC-RoomIQ composition."',
            reconfirm,
        )
        self.assertIn(
            "production parameters are not the full composition", reconfirm
        )
        self.assertIn("explicit operator statement", reconfirm)
        self.assertIn("re-flash of the full composition", reconfirm)
        # The close-out summary row must mirror the recorded closure.
        self.assertIn(
            "| Full-composition re-confirm | PASS — closed via closure path (a)",
            self.text,
        )
        # The stale open state must not linger anywhere in the record.
        self.assertNotIn("NOT RECORDED", self.text)
        # The rejected PASS-by-inference wording must never come back.
        self.assertNotIn("covered by the Step F", self.text)

    def test_operator_attestation_block_present(self) -> None:
        # The close-out PR inserts the attestation block empty; the operator
        # completes it himself before merge. Pin the structure (heading +
        # the six fields), not the emptiness, so the operator's fill does
        # not break the suite.
        self.assertIn("## Operator attestation", self.text)
        self.assertIn("To be completed by the operator himself before merge", self.text)
        attestation = self.text.split("## Operator attestation", 1)[1]
        for field in (
            "| Operator |",
            "| Date |",
            "| Units under test |",
            "| Safety setup |",
            "| Statement |",
            "| Signature |",
        ):
            self.assertIn(
                field,
                attestation,
                f"operator attestation field missing: {field}",
            )

    def test_attestation_operator_and_signature_cells_filled(self) -> None:
        # Final close-out merge guard (PACKAGE-TRIAC-001-ATTEST-CLOSE): the
        # close-out branch must NOT merge green while the attestation table
        # is unfilled. This is DESIGNED TO FAIL on the staging commits —
        # the entry cells are deliberately empty there — and clears only
        # when the operator commits his own fill. It asserts presence only,
        # never wording: no attestation content is machine-written or
        # machine-checked beyond non-emptiness.
        attestation = self.text.split("## Operator attestation", 1)[1]
        entries = {}
        for line in attestation.splitlines():
            stripped = line.strip()
            if not stripped.startswith("|"):
                continue
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if len(cells) >= 2 and cells[0] in ("Operator", "Signature"):
                entries[cells[0]] = cells[1]
        self.assertTrue(
            entries.get("Operator") and entries.get("Signature"),
            "operator attestation is unsigned: the Operator and Signature "
            "entry cells must be filled by the operator himself on this "
            "branch before merge (this guard is designed to fail until "
            "that fill lands; found "
            f"Operator={entries.get('Operator')!r}, "
            f"Signature={entries.get('Signature')!r})",
        )

    # --- coupling to the live source-of-truth config -------------------

    def test_catalog_fantriac_commissioned_to_experimental_lane(self) -> None:
        # TRIAC-COMMISSIONING-001 (this commissioning PR) cleared the
        # PACKAGE-TRIAC-001 half of the blocker and moved FanTRIAC into the
        # experimental self-build mains lane: the catalog flips to status
        # preview on the experimental channel with a webflash-builds row, while
        # the bench-proof doc keeps its historical close-out statements (this PR
        # does not edit the doc). The catalog cites the attested proof and the
        # governing resolution record, and every permanent tooth survives.
        self.assertEqual(self.fantriac.get("status"), "preview")
        self.assertEqual(self.fantriac.get("channel"), "experimental")
        self.assertIs(self.fantriac.get("webflash_build_matrix"), True)
        self.assertEqual(
            self.fantriac.get("bench_proof"),
            "docs/package-triac-001-operator-bench-proof.md",
        )
        self.assertEqual(
            self.fantriac.get("governing_decision"),
            "docs/decisions/COMPLIANCE-001-RESOLUTION-001.md",
        )
        reason = self.fantriac.get("reason", "")
        self.assertIn("PACKAGE-TRIAC-001", reason)
        self.assertIn("COMPLIANCE-001", reason)
        posture = self.fantriac.get("experimental_lane_posture", {})
        self.assertIs(posture.get("never_stable"), True)
        self.assertIs(posture.get("never_buyable"), True)
        self.assertIs(posture.get("never_in_kit_or_kit_picker"), True)
        self.assertIs(
            posture.get("self_build_board_never_placed_on_market_by_sense360"), True
        )

    def test_variants_still_record_operator_bench_gate(self) -> None:
        gates = []
        for node in _walk(self.variants):
            if not isinstance(node, dict):
                continue
            if node.get("requires_operator_bench") == "PACKAGE-TRIAC-001":
                gates.append(node)
        self.assertTrue(
            gates,
            "config/room-bundle-fan-variants.json must still record "
            "requires_operator_bench == PACKAGE-TRIAC-001",
        )

    def test_bench_proof_doc_retains_historical_close_out_decoupling(self) -> None:
        # Closing the bench protocol was NOT clearing the blocker — only the
        # commissioning PR (TRIAC-COMMISSIONING-001) did that, and it has now
        # landed, so the catalog has moved to status preview (experimental
        # lane). This commissioning PR does NOT edit the bench-proof doc, so the
        # doc RETAINS its historical close-out statements verbatim: the close-out
        # itself does not clear PACKAGE-TRIAC-001, and COMPLIANCE-001 is closed
        # by market posture. The bench proof (evidence) and the catalog (lane
        # move) stay decoupled.
        self.assertEqual(
            self.fantriac.get("status"),
            "preview",
            "the commissioning PR moved FanTRIAC into the experimental lane",
        )
        self.assertIn(
            "does **not** clear `PACKAGE-TRIAC-001`",
            self.text,
            "the bench-proof doc must retain its historical statement that the "
            "close-out (not the bench proof itself) does not clear the blocker",
        )
        self.assertIn(
            "`COMPLIANCE-001` is CLOSED, resolved by market posture",
            self.text,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

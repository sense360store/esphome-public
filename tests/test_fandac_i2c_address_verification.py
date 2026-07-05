#!/usr/bin/env python3
"""FANDAC-I2C-ADDR-001 — FanDAC I²C address verification doc guards.

These are docs / metadata-only guards. They assert nothing about firmware
behaviour and they claim no hardware / bench / compliance proof. They pin the
invariants for the dedicated FanDAC I²C address hardware verification checklist
added by ``FANDAC-I2C-ADDR-001`` for the room-bundle FanDAC preview configs
introduced by ``ROOM-BUNDLE-FAN-CONFIGS-001`` (#713):

  * ``docs/hardware/fandac-i2c-address-verification.md`` exists.
  * It states the required addresses (GP8403 IC1 ``0x58``, IC2 ``0x5A``), the
    forbidden ``0x59``, and that the air-quality SGP41 sits at ``0x59``.
  * It states the verification is pending / not yet proof — i.e. "required but
    not bench-verified".
  * It carries a bench checklist and an evidence template.
  * The room-bundle / FanDAC / first-release / handoff docs link to it.
  * No stable / compliance / safety / hardware-verified proof is claimed.

Run with::

    python3 tests/test_fandac_i2c_address_verification.py

or::

    python3 -m unittest tests.test_fandac_i2c_address_verification -v
"""

from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent

VERIFICATION_REL = "docs/hardware/fandac-i2c-address-verification.md"
VERIFICATION_DOC = REPO_ROOT / VERIFICATION_REL

# Docs that must point at the verification gate.
# docs/sense360-room-bundles.md, docs/first-release-gates.md, and
# docs/pre-hardware-room-bundle-release-handoff.md were archived under
# DOCS-DISPOSITION-001 (see docs/archive-index.md), so they dropped out
# of this list; the FANDAC-I2C-ADDR-001 gate itself stays PENDING and
# unchanged.
LINKING_DOCS = [
    "docs/hardware/s360-312-r4-fandac.md",
    "UPCOMING_PR.md",
]


class FandacI2cAddressVerificationDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = VERIFICATION_DOC.read_text(encoding="utf-8")
        cls.lower = cls.text.lower()

    def test_doc_exists(self):
        self.assertTrue(
            VERIFICATION_DOC.is_file(),
            f"{VERIFICATION_REL} must exist",
        )

    def test_mentions_followup_id(self):
        self.assertIn("FANDAC-I2C-ADDR-001", self.text)

    def test_required_and_forbidden_addresses(self):
        # Required GP8403 addresses.
        self.assertIn("0x58", self.text, "must state GP8403 IC1 address 0x58")
        self.assertIn("0x5A", self.text, "must state GP8403 IC2 address 0x5A")
        # The forbidden / colliding address.
        self.assertIn("0x59", self.text, "must reference the forbidden 0x59")
        self.assertIn(
            "forbidden",
            self.lower,
            "must mark 0x59 as forbidden when VentIQ/AirIQ is present",
        )

    def test_mentions_sgp41(self):
        self.assertIn("SGP41", self.text, "must mention the air-quality SGP41")

    def test_mentions_gp8403(self):
        self.assertIn("GP8403", self.text)

    def test_mentions_air_quality_modules(self):
        self.assertIn("VentIQ", self.text)
        self.assertIn("AirIQ", self.text)

    def test_verification_is_pending_not_proof(self):
        self.assertIn(
            "required but not bench-verified",
            self.lower,
            "must state the mapping is required but not bench-verified",
        )
        self.assertIn("pending", self.lower, "must state the gate is pending")

    def test_has_bench_checklist(self):
        self.assertIn("checklist", self.lower)
        # Three distinct I²C scan scenarios.
        self.assertIn("fandac only", self.lower)
        self.assertIn("ventiq + fandac", self.lower)
        self.assertIn("airiq + fandac", self.lower)
        # Pass/fail + tester/date recording.
        self.assertIn("pass", self.lower)
        self.assertIn("fail", self.lower)
        self.assertIn("tester", self.lower)

    def test_has_evidence_template(self):
        self.assertIn("evidence template", self.lower)
        self.assertIn("board revision", self.lower)
        self.assertIn("switch position", self.lower)
        self.assertIn("sign-off", self.lower)

    def test_no_stable_compliance_safety_proof_claimed(self):
        # The doc must explicitly disclaim proof, not assert it.
        self.assertIn("no hardware", self.lower)
        self.assertIn("compliance", self.lower)
        # Guard against an accidental *positive* proof claim. (The guardrail
        # sentence "do not mark fandac hardware verified" is a disclaimer, so we
        # only flag affirmative phrasings here.)
        for bad in (
            "compliance proof is claimed",
            "safety proof is claimed",
            "is hardware verified",
            "is now stable",
            "marked stable",
        ):
            self.assertNotIn(
                bad,
                self.lower,
                f"verification doc must not claim proof: found {bad!r}",
            )

    def test_linking_docs_reference_verification_gate(self):
        needle = "fandac-i2c-address-verification.md"
        for rel in LINKING_DOCS:
            path = REPO_ROOT / rel
            self.assertTrue(path.is_file(), f"{rel} must exist")
            self.assertIn(
                needle,
                path.read_text(encoding="utf-8"),
                f"{rel} must link to the FANDAC-I2C-ADDR-001 verification doc",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)

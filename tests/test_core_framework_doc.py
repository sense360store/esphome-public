#!/usr/bin/env python3
"""CORE-FRAMEWORK-001 — framework documentation and roadmap guards.

Pins the documentation contract for the shared Sense360 firmware / entity
framework:

* ``docs/architecture/sense360-core-framework.md`` exists and documents the
  entity naming rules, diagnostic verbosity policy, capability model,
  compile-time vs runtime distinction, module-status contract, overall
  health aggregation, availability rules, extension rules, and the
  backwards-compatibility policy.
* Every stable capability identifier and status value from
  ``config/core-framework.json`` is documented.
* The doc claims firmware-composition proof only — never hardware / bench
  proof (standing invariant: no false proof).
* The canonical roadmap doc records CORE-FRAMEWORK-001 without touching SOT
  programme state.

Uses Python's stdlib unittest (repo convention). Run with::

    python3 tests/test_core_framework_doc.py
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOC_PATH = REPO_ROOT / "docs" / "architecture" / "sense360-core-framework.md"
CONTRACT_PATH = REPO_ROOT / "config" / "core-framework.json"
ROADMAP_PATH = REPO_ROOT / "docs" / "sense360-roadmap-status.md"

REQUIRED_TOPIC_HEADINGS = (
    "Purpose",
    "Entity naming",
    "Diagnostic",
    "Capability model",
    "Compile-time",
    "Module status",
    "Overall device health",
    "Availability",
    "Extension rules",
    "Backwards compatibility",
    "Test",
)


class FrameworkDocTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(DOC_PATH.is_file(), f"missing {DOC_PATH}")
        self.text = DOC_PATH.read_text()
        self.assertTrue(CONTRACT_PATH.is_file(), f"missing {CONTRACT_PATH}")
        self.contract = json.loads(CONTRACT_PATH.read_text())

    def test_work_item_recorded(self) -> None:
        self.assertIn("CORE-FRAMEWORK-001", self.text)

    def test_required_topics_present(self) -> None:
        for topic in REQUIRED_TOPIC_HEADINGS:
            self.assertIn(
                topic,
                self.text,
                f"framework doc must cover topic {topic!r}",
            )

    def test_every_capability_id_documented(self) -> None:
        for cap_id in self.contract.get("capabilities", {}):
            self.assertIn(f"`{cap_id}`", self.text, cap_id)

    def test_status_and_health_values_documented(self) -> None:
        status = self.contract.get("module_status", {})
        health = self.contract.get("device_health", {})
        values = (
            list(status.get("values", {}))
            + list(status.get("reserved_values", {}))
            + list(health.get("values", {}))
            + list(health.get("reserved_values", {}))
        )
        self.assertTrue(values)
        for value in values:
            self.assertIn(value, self.text, value)

    def test_compile_time_vs_runtime_distinction(self) -> None:
        lowered = self.text.lower()
        self.assertIn("compile-time", lowered)
        self.assertIn("runtime", lowered)
        self.assertIn("not", lowered)

    def test_no_hardware_proof_claim(self) -> None:
        lowered = self.text.lower()
        self.assertIn("no hardware", lowered)
        for forbidden in (
            "hardware verified",
            "bench verified",
            "hardware-proven",
            "bench-proven",
        ):
            self.assertNotIn(forbidden, lowered)

    def test_disabled_by_default_policy_documented(self) -> None:
        self.assertIn("disabled by default", self.text.lower())


class RoadmapEntryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = ROADMAP_PATH.read_text()

    def test_core_framework_recorded(self) -> None:
        self.assertIn("CORE-FRAMEWORK-001", self.text)

    def test_no_sot_state_change_declared(self) -> None:
        # The roadmap entry must state that SOT programme state is unchanged.
        self.assertIn("CORE-FRAMEWORK-001", self.text)
        section = self.text[self.text.index("CORE-FRAMEWORK-001") :]
        self.assertIn("SOT", section[:4000])

    def test_no_hardware_requirement_declared(self) -> None:
        self.assertIn("CORE-FRAMEWORK-001", self.text)
        section = self.text[self.text.index("CORE-FRAMEWORK-001") :]
        self.assertIn("hardware", section[:4000].lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)

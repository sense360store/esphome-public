#!/usr/bin/env python3
"""AGENT-BOUNDED-AUTONOMY-001 adoption regression guards.

This repository adopts the bounded agent autonomy contract owned by
``sense360store/SOT`` (``CLAUDE-OPERATING-MODEL.md``, section
*AGENT-BOUNDED-AUTONOMY-001: bounded autonomy*) through a scoped adoption
section in ``CLAUDE.md``. These tests pin that adoption so it cannot
silently regress:

  * the adoption section exists, names the programme ID, and links to the
    authoritative SOT operating model on ``main``;
  * the exact SOT adoption-provenance commit is recorded;
  * local rules may tighten but never loosen the SOT contract, the
    stricter safety rule wins, and an unresolvable authority conflict is
    ``BLOCKED_AUTHORITY_CONFLICT``;
  * exactly the five canonical SOT terminal states are referenced (no
    sixth local state), and the conjunctive ALL-FOUR escalation threshold
    is preserved;
  * routine inspection, testing, CI remediation, and draft-PR work stay
    autonomous, while merge, release publication, and release-capable
    workflow dispatch stay owner-reserved;
  * the firmware-specific tightening (declaration-driven releases,
    Release-One baseline, Kitchen/Bedroom posture, fans never stable,
    FanTRIAC restrictions, no machine-authored attestations, evidence-
    level separation) is present in the adoption section itself.

Every content assertion runs against the scoped adoption section extracted
from ``CLAUDE.md`` — not the whole file — so a test cannot pass merely
because similar wording exists elsewhere in the document.

Run with::

    python3 tests/test_agent_bounded_autonomy_adoption.py

or::

    python3 -m unittest tests.test_agent_bounded_autonomy_adoption -v
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"

PROGRAMME_ID = "AGENT-BOUNDED-AUTONOMY-001"

ADOPTION_HEADING = "### Bounded agent autonomy (AGENT-BOUNDED-AUTONOMY-001)"

SOT_OPERATING_MODEL_MAIN_URL = (
    "https://github.com/sense360store/SOT/blob/main/CLAUDE-OPERATING-MODEL.md"
)

# The exact SOT main commit verified during adoption: it contains the
# bounded-autonomy contract, programme_status: implemented, and the
# esphome-public "not yet adopted" rollout record (PR #10 merge commit).
SOT_PROVENANCE_COMMIT = "387cabf44a79dfe03d6c7959ec4e3d012c295647"

# The five canonical SOT terminal states — referenced, never redefined,
# and never extended with a sixth local state.
CANONICAL_TERMINAL_STATES = frozenset(
    {
        "READY_FOR_OWNER_REVIEW",
        "BLOCKED_OWNER_DECISION",
        "BLOCKED_EXTERNAL_ACCESS",
        "BLOCKED_AUTHORITY_CONFLICT",
        "UNSAFE_TO_PROCEED",
    }
)

# ALL-CAPS underscore-joined tokens; in the adoption section these can
# only be terminal-state names (programme and gate IDs use hyphens).
_STATE_TOKEN_RE = re.compile(r"\b[A-Z]+(?:_[A-Z]+)+\b")

# Next markdown heading of level 1-3 ends the adoption section.
_NEXT_HEADING_RE = re.compile(r"^#{1,3} ", re.MULTILINE)


def _read_claude_md() -> str:
    return CLAUDE_MD.read_text(encoding="utf-8")


def _adoption_section(text: str) -> str:
    """Return only the scoped adoption section from CLAUDE.md."""
    start = text.index(ADOPTION_HEADING)
    body = text[start + len(ADOPTION_HEADING) :]
    match = _NEXT_HEADING_RE.search(body)
    return body[: match.start()] if match else body


class AdoptionSectionScopeTests(unittest.TestCase):
    """The adoption section exists exactly once and is extractable."""

    def setUp(self) -> None:
        self.assertTrue(CLAUDE_MD.is_file(), f"missing {CLAUDE_MD}")
        self.text = _read_claude_md()

    def test_adoption_heading_present_exactly_once(self) -> None:
        self.assertEqual(
            self.text.count(ADOPTION_HEADING),
            1,
            "CLAUDE.md must contain exactly one bounded-autonomy adoption "
            f"section headed '{ADOPTION_HEADING}'.",
        )

    def test_adoption_section_is_nonempty(self) -> None:
        section = _adoption_section(self.text)
        self.assertGreater(
            len(section.strip()),
            0,
            "The adoption section must have body text, not just a heading.",
        )

    def test_adoption_section_inside_cross_repo_operating_model(self) -> None:
        cross_repo = self.text.index("## Cross-repository operating model")
        adoption = self.text.index(ADOPTION_HEADING)
        next_h2 = self.text.index("\n## ", cross_repo)
        self.assertTrue(
            cross_repo < adoption < next_h2,
            "The adoption subsection must live inside the "
            "'Cross-repository operating model' section.",
        )


class AdoptionContractTests(unittest.TestCase):
    """Assertions scoped to the adoption section only."""

    def setUp(self) -> None:
        self.section = _adoption_section(_read_claude_md())

    # -- adoption, canonical link, provenance --------------------------------

    def test_adopts_programme_id(self) -> None:
        self.assertIn(PROGRAMME_ID, self.section)
        self.assertIn(
            "adopts",
            self.section,
            "The section must state that this repository adopts the "
            "bounded-autonomy contract.",
        )

    def test_links_to_authoritative_sot_operating_model_on_main(self) -> None:
        self.assertIn(
            SOT_OPERATING_MODEL_MAIN_URL,
            self.section,
            "The canonical contract link must point at SOT main, not a " "pinned ref.",
        )

    def test_records_exact_sot_provenance_commit(self) -> None:
        self.assertIn(
            SOT_PROVENANCE_COMMIT,
            self.section,
            "The exact SOT main commit verified during adoption must be "
            "recorded as provenance.",
        )
        self.assertIn(
            "programme_status: implemented",
            self.section,
            "The provenance record must name the verified programme status.",
        )

    def test_contract_is_not_duplicated_locally(self) -> None:
        self.assertIn("not duplicated here", self.section)
        self.assertIn(
            "canonical SOT invocation block",
            self.section,
            "Future tasks must use the canonical SOT invocation block "
            "rather than restating the contract.",
        )

    # -- tighten-never-loosen, authority conflict ----------------------------

    def test_tighten_but_never_loosen(self) -> None:
        self.assertIn("tighten but never loosen", self.section)
        self.assertIn("stricter safety rule wins", self.section)

    def test_unresolvable_authority_conflict_is_blocked(self) -> None:
        self.assertIn("BLOCKED_AUTHORITY_CONFLICT", self.section)
        self.assertRegex(
            self.section,
            r"authority conflict[\s\S]{0,120}cannot resolve",
            "The section must state that an unresolvable authority "
            "conflict ends the run as BLOCKED_AUTHORITY_CONFLICT.",
        )

    def test_continues_autonomously_until_terminal_state(self) -> None:
        self.assertIn("continue\nautonomously", self.section.replace("**", ""))
        self.assertIn(
            "exactly\none of the five named SOT terminal states",
            self.section.replace("**", ""),
        )

    # -- terminal states and escalation threshold ----------------------------

    def test_references_exactly_the_five_canonical_terminal_states(
        self,
    ) -> None:
        found = frozenset(_STATE_TOKEN_RE.findall(self.section))
        self.assertEqual(
            found,
            CANONICAL_TERMINAL_STATES,
            "The adoption section must reference exactly the five "
            "canonical SOT terminal states — no missing state and no "
            f"invented sixth state. Found: {sorted(found)}",
        )
        self.assertIn(
            "no sixth local state",
            self.section,
            "The section must state explicitly that no sixth local "
            "terminal state exists.",
        )

    def test_preserves_conjunctive_all_four_escalation_threshold(self) -> None:
        flat = self.section.replace("**", "")
        self.assertIn("conjunctive", flat)
        self.assertRegex(
            flat,
            r"only\s+when\s+all four\s+SOT threshold conditions hold\s+"
            r"simultaneously",
            "The ALL-FOUR conjunctive escalation threshold must be "
            "preserved verbatim in meaning: interrupt only when all four "
            "conditions hold simultaneously.",
        )

    # -- autonomous permissions ----------------------------------------------

    def test_permits_routine_autonomous_engineering(self) -> None:
        flat = " ".join(self.section.split())
        for phrase in (
            "inspect source, configuration declarations, history, PRs, " "and CI",
            "run static validation, unit and contract tests",
            "remediate every branch-caused test or CI failure",
            "create and maintain one draft PR",
            "prepare a separate SOT reconciliation recommendation",
        ):
            self.assertIn(
                phrase,
                flat,
                f"Autonomous permission missing from adoption section: " f"{phrase!r}",
            )

    # -- owner-reserved actions (firmware tightening) ------------------------

    def test_prohibits_merge_and_release_publication(self) -> None:
        flat = " ".join(self.section.split())
        self.assertIn("merge any PR (including the agent's own draft PR)", flat)
        self.assertIn("create or publish a tag or GitHub Release", flat)

    def test_prohibits_release_capable_workflow_dispatch(self) -> None:
        flat = " ".join(self.section.split())
        self.assertIn(
            "dispatch any workflow that can publish, release, attach, or "
            "deploy firmware",
            flat,
        )
        self.assertIn("Release 3: Build & Release", flat)
        self.assertIn("firmware-build-release.yml", flat)
        self.assertIn("create-release.yml", flat)

    def test_preserves_declaration_driven_release_model(self) -> None:
        flat = " ".join(self.section.split())
        self.assertIn("declaration-driven", flat)
        self.assertIn("webflash-builds.json", flat)
        self.assertIn("(ESP-007)", flat)

    def test_preserves_release_one_customer_baseline(self) -> None:
        flat = " ".join(self.section.split())
        self.assertIn(
            "Release-One (`Ceiling-POE-VentIQ-RoomIQ`) remains the "
            "production stable customer baseline",
            flat,
        )

    def test_keeps_kitchen_and_bedroom_not_default_not_buyable(self) -> None:
        flat = " ".join(self.section.split())
        self.assertIn(
            "make Kitchen or Bedroom customer-default, buyable, or "
            "commercially available",
            flat,
        )

    def test_keeps_every_fan_configuration_off_stable(self) -> None:
        self.assertIn("make any fan configuration stable", self.section)

    def test_preserves_fantriac_restrictions(self) -> None:
        flat = " ".join(self.section.split())
        self.assertIn(
            "expose FanTRIAC as stable, recommended, default, buyable, or " "one-click",
            flat,
        )

    def test_prohibits_machine_authored_attestations(self) -> None:
        flat = " ".join(self.section.split())
        self.assertIn(
            "author or amend operator attestations, dates, signatures, or "
            "physical bench claims",
            flat,
        )

    def test_separates_compile_evidence_from_hardware_and_commerce(
        self,
    ) -> None:
        flat = " ".join(self.section.split())
        self.assertIn(
            "treat source inspection, simulation, or compilation as "
            "physical hardware, customer, compliance, safety, or "
            "commercial proof",
            flat,
        )
        self.assertIn(
            "infer hardware population, sensor identity, pin correctness",
            flat,
        )

    def test_prohibits_changing_sot_programme_status_here(self) -> None:
        self.assertIn("change SOT programme status in this repository", self.section)

    # -- observation and workflow distinction --------------------------------

    def test_allows_read_only_observation_of_existing_evidence(self) -> None:
        flat = " ".join(self.section.split())
        self.assertIn(
            "verify existing releases, tags, artifacts, served binaries, "
            "owner-authored decisions, and bench records",
            flat,
        )
        self.assertIn("Observation never authorises mutation", flat)
        self.assertIn("never raises the evidence level", flat)
        self.assertIn("provenance", flat)

    def test_workflow_distinction_is_explicit(self) -> None:
        flat = " ".join(self.section.split())
        self.assertIn("routine PR CI and validation inspection is autonomous", flat)
        self.assertIn("branch-caused CI remediation is autonomous", flat)
        self.assertIn(
            "only when the task explicitly authorises it and the workflow "
            "has no release or deployment side effect",
            flat,
        )
        self.assertIn(
            "any publishing or release-capable workflow remains " "owner-reserved",
            flat,
        )

    # -- adoption scope: governance text only --------------------------------

    def test_declares_governance_only_scope(self) -> None:
        flat = " ".join(self.section.split())
        self.assertIn(
            "changes no firmware, product YAML, configuration declaration, "
            "release workflow, version, manifest, binary, hardware record, "
            "product status, or commercial state",
            flat,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

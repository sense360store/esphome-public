#!/usr/bin/env python3
"""RELEASE-002 smoke test for .github/workflows/release-notes-draft.yml.

Locks in the manual release-notes draft workflow's surface area:

  * the workflow file exists at the expected path
  * it is manual-only (declares ``workflow_dispatch``)
  * it shells out to ``scripts/generate_webflash_release_notes.py``
  * it shells out to ``scripts/validate-webflash-release-notes.py``
  * it uploads the generated ``release-notes.md`` via
    ``actions/upload-artifact``

The check is intentionally a substring smoke test rather than a full YAML
schema parse. Workflow-shape assertions in this repo are limited to what
the RELEASE-002 task description spells out as the required smoke check;
deeper structural assertions would couple this test to YAML-formatting
choices that are not part of the contract.

Run with:

    python3 tests/test_release_notes_draft_workflow.py
"""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "release-notes-draft.yml"


def _strip_comment_lines(text: str) -> str:
    """Return ``text`` with comment-only lines removed.

    Lines whose first non-whitespace character is ``#`` are dropped. This
    covers both YAML comments and shell comments inside ``run:`` blocks,
    so substring assertions below match real workflow behavior rather
    than narrative comments that document what the workflow deliberately
    does or does not do.
    """
    return "\n".join(line for line in text.splitlines() if line.lstrip()[:1] != "#")


class ReleaseNotesDraftWorkflowSmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(
            WORKFLOW_PATH.is_file(),
            f"missing workflow file: {WORKFLOW_PATH}",
        )
        self.text = WORKFLOW_PATH.read_text(encoding="utf-8")
        self.executable_text = _strip_comment_lines(self.text)

    def test_is_manual_dispatch_only(self) -> None:
        self.assertIn(
            "workflow_dispatch:",
            self.executable_text,
            "release-notes-draft workflow must declare workflow_dispatch",
        )
        # Guard against the workflow gaining a release/push/pull_request
        # trigger by accident, which would silently turn this preflight
        # helper into part of release-publish behavior.
        forbidden_triggers = (
            "release:",
            "push:",
            "pull_request:",
            "schedule:",
        )
        for trigger in forbidden_triggers:
            self.assertNotIn(
                trigger,
                self.executable_text,
                f"release-notes-draft workflow must not declare {trigger!r}; "
                "it is preflight-only and must stay manual_dispatch only",
            )

    def test_references_generator_script(self) -> None:
        self.assertIn(
            "generate_webflash_release_notes.py",
            self.executable_text,
            "workflow must invoke scripts/generate_webflash_release_notes.py",
        )

    def test_references_validator_script(self) -> None:
        self.assertIn(
            "validate-webflash-release-notes.py",
            self.executable_text,
            "workflow must invoke scripts/validate-webflash-release-notes.py",
        )

    def test_uploads_artifact(self) -> None:
        self.assertIn(
            "upload-artifact",
            self.executable_text,
            "workflow must upload the generated release-notes.md via "
            "actions/upload-artifact",
        )
        self.assertIn(
            "release-notes.md",
            self.executable_text,
            "workflow must reference release-notes.md as its draft output",
        )

    def test_does_not_force_require_changelog(self) -> None:
        # The task explicitly forbids defaulting to --require-changelog so
        # the operator can produce a TODO-placeholder draft as a starting
        # point. Lock that in. Checked against the comment-stripped text so
        # narrative comments that name the flag (to explain why it is NOT
        # passed) do not trip the assertion.
        self.assertNotIn(
            "--require-changelog",
            self.executable_text,
            "release-notes-draft workflow must not pass --require-changelog "
            "by default; the TODO placeholder is the intended starting point",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

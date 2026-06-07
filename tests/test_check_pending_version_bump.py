#!/usr/bin/env python3
"""Unit tests for scripts/check_pending_version_bump.py (Draft Notes preflight).

Uses Python's stdlib ``unittest`` (matching the no-pytest convention the rest
of the validators in this repo use). Every test here exercises the **pure**
``decide()`` function offline: no network, no ``gh``, no filesystem. The
GitHub I/O wrapper is intentionally not exercised here; the decision logic is
fully covered by the cases below.

Run with::

    python3 tests/test_check_pending_version_bump.py

The preflight is a **version-declaration gate only**: the pass/fail decision
depends solely on whether the catalog declares the requested version. Channel
and status are deferred to the generator. The tests lock in:

  * version match -> ok, no message (regardless of channel);
  * version match but channel differs -> ok (deferred to the generator), the
    Codex P2 case where a preview entry is left on the default stable channel;
  * version mismatch with a matching candidate bump PR (one that introduces the
    requested version, regardless of its channel) -> not ok, and the message
    names that PR's number and url and tells the operator to merge it;
  * version mismatch with no candidates -> not ok, and the message directs the
    operator to run "Release 1: Bump Version";
  * version mismatch with only a non-matching candidate -> still not ok, and the
    message mentions the candidate's (different) version;
  * the decision never depends on the candidate list (it is derivable from the
    local catalog alone).
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_pending_version_bump.py"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


preflight = _load_module("check_pending_version_bump", SCRIPT_PATH)
decide = preflight.decide

CONFIG = "Ceiling-POE-VentIQ-RoomIQ"


class DecideExactMatchTests(unittest.TestCase):
    def test_exact_match_is_ok_with_no_message(self) -> None:
        ok, message = decide(
            config=CONFIG,
            requested_version="1.0.1",
            requested_channel="stable",
            catalog_version="1.0.1",
            catalog_channel="stable",
            candidate_bumps=[],
        )
        self.assertTrue(ok)
        self.assertIsNone(message)

    def test_exact_match_ignores_candidates(self) -> None:
        # The decision is derivable from the local catalog alone: even a pile of
        # candidate PRs cannot turn a matching catalog into a failure.
        ok, message = decide(
            config=CONFIG,
            requested_version="1.0.1",
            requested_channel="stable",
            catalog_version="1.0.1",
            catalog_channel="stable",
            candidate_bumps=[
                {
                    "pr_number": 42,
                    "pr_url": "https://github.com/o/r/pull/42",
                    "proposed_version": "2.0.0",
                    "proposed_channel": "stable",
                }
            ],
        )
        self.assertTrue(ok)
        self.assertIsNone(message)

    def test_channel_mismatch_with_matching_version_is_ok(self) -> None:
        # Version-declaration gate only: when the catalog already declares the
        # requested version, a channel-only mismatch is deferred to the
        # generator (which owns channel/status). decide() passes rather than
        # printing a misleading "run Release 1: Bump Version" message for a bump
        # that does not exist. This is the Codex P2 case (preview entry left on
        # the default stable channel).
        ok, message = decide(
            config=CONFIG,
            requested_version="1.0.0",
            requested_channel="stable",
            catalog_version="1.0.0",
            catalog_channel="preview",
            candidate_bumps=[],
        )
        self.assertTrue(ok)
        self.assertIsNone(message)

    def test_channel_mismatch_is_ok_even_with_candidates(self) -> None:
        # Version matches, so ok regardless of channel or any candidate PRs.
        ok, message = decide(
            config=CONFIG,
            requested_version="1.0.0",
            requested_channel="stable",
            catalog_version="1.0.0",
            catalog_channel="preview",
            candidate_bumps=[
                {
                    "pr_number": 99,
                    "pr_url": "https://github.com/o/r/pull/99",
                    "proposed_version": "2.0.0",
                    "proposed_channel": "stable",
                }
            ],
        )
        self.assertTrue(ok)
        self.assertIsNone(message)


class DecideMatchingCandidateTests(unittest.TestCase):
    def test_matching_candidate_points_at_the_pr(self) -> None:
        ok, message = decide(
            config=CONFIG,
            requested_version="1.0.2",
            requested_channel="stable",
            catalog_version="1.0.1",
            catalog_channel="stable",
            candidate_bumps=[
                {
                    "pr_number": 123,
                    "pr_url": "https://github.com/sense360store/esphome-public/pull/123",
                    "proposed_version": "1.0.2",
                    "proposed_channel": "stable",
                }
            ],
        )
        self.assertFalse(ok)
        assert message is not None
        # Names the catalog version, the requested version+channel, the PR
        # number and url, and tells the operator to merge it.
        self.assertIn("1.0.1", message)
        self.assertIn("1.0.2", message)
        self.assertIn("stable", message)
        self.assertIn("#123", message)
        self.assertIn(
            "https://github.com/sense360store/esphome-public/pull/123", message
        )
        self.assertIn("Merge that PR", message)
        self.assertIn("Release 2: Draft Notes", message)
        # It must NOT mis-route the operator to Release 1 when the bump already
        # exists as an open PR.
        self.assertNotIn("Run Release 1", message)

    def test_candidate_matches_on_version_regardless_of_channel(self) -> None:
        # Channel is not part of the gate: a candidate that introduces the
        # requested version is the matching bump even if its proposed channel
        # differs from the requested channel (a version bump never changes
        # channel). The operator is pointed at that PR, not routed to Release 1.
        ok, message = decide(
            config=CONFIG,
            requested_version="1.0.2",
            requested_channel="stable",
            catalog_version="1.0.1",
            catalog_channel="stable",
            candidate_bumps=[
                {
                    "pr_number": 7,
                    "pr_url": "https://github.com/o/r/pull/7",
                    "proposed_version": "1.0.2",
                    "proposed_channel": "preview",
                }
            ],
        )
        self.assertFalse(ok)
        assert message is not None
        self.assertIn("#7", message)
        self.assertIn("Merge that PR", message)
        self.assertNotIn("Run Release 1", message)

    def test_first_matching_candidate_is_used(self) -> None:
        ok, message = decide(
            config=CONFIG,
            requested_version="2.0.0",
            requested_channel="stable",
            catalog_version="1.0.1",
            catalog_channel="stable",
            candidate_bumps=[
                {
                    "pr_number": 11,
                    "pr_url": "https://github.com/o/r/pull/11",
                    "proposed_version": "2.0.0",
                    "proposed_channel": "stable",
                },
                {
                    "pr_number": 12,
                    "pr_url": "https://github.com/o/r/pull/12",
                    "proposed_version": "2.0.0",
                    "proposed_channel": "stable",
                },
            ],
        )
        self.assertFalse(ok)
        assert message is not None
        self.assertIn("#11", message)


class DecideNoCandidateTests(unittest.TestCase):
    def test_no_candidates_directs_to_release_1(self) -> None:
        ok, message = decide(
            config=CONFIG,
            requested_version="2.0.0",
            requested_channel="stable",
            catalog_version="1.0.1",
            catalog_channel="stable",
            candidate_bumps=[],
        )
        self.assertFalse(ok)
        assert message is not None
        self.assertIn("Catalog declares 1.0.1", message)
        self.assertIn("not the requested 2.0.0", message)
        self.assertIn("Run Release 1: Bump Version", message)
        self.assertIn(CONFIG, message)
        # No PRs were supplied, so no "Open PRs changing the catalog" suffix.
        self.assertNotIn("Open PRs changing the catalog", message)

    def test_none_candidate_list_is_treated_as_empty(self) -> None:
        ok, message = decide(
            config=CONFIG,
            requested_version="2.0.0",
            requested_channel="stable",
            catalog_version="1.0.1",
            catalog_channel="stable",
            candidate_bumps=None,
        )
        self.assertFalse(ok)
        assert message is not None
        self.assertIn("Run Release 1: Bump Version", message)


class DecideNonMatchingCandidateTests(unittest.TestCase):
    def test_only_a_non_matching_candidate_is_still_not_ok_and_is_mentioned(self) -> None:
        ok, message = decide(
            config=CONFIG,
            requested_version="2.0.0",
            requested_channel="stable",
            catalog_version="1.0.1",
            catalog_channel="stable",
            candidate_bumps=[
                {
                    "pr_number": 55,
                    "pr_url": "https://github.com/o/r/pull/55",
                    "proposed_version": "3.0.0",
                    "proposed_channel": "stable",
                }
            ],
        )
        self.assertFalse(ok)
        assert message is not None
        # Routes to Release 1 because no PR matches the requested version...
        self.assertIn("Run Release 1: Bump Version", message)
        # ...but still surfaces the divergent candidate so the operator can spot
        # a wrong-version dispatch.
        self.assertIn("Open PRs changing the catalog", message)
        self.assertIn("#55 proposes 3.0.0", message)

    def test_multiple_non_matching_candidates_are_all_listed(self) -> None:
        ok, message = decide(
            config=CONFIG,
            requested_version="2.0.0",
            requested_channel="stable",
            catalog_version="1.0.1",
            catalog_channel="stable",
            candidate_bumps=[
                {
                    "pr_number": 8,
                    "pr_url": "https://github.com/o/r/pull/8",
                    "proposed_version": "1.0.2",
                    "proposed_channel": "stable",
                },
                {
                    "pr_number": 9,
                    "pr_url": "https://github.com/o/r/pull/9",
                    "proposed_version": "1.5.0",
                    "proposed_channel": "stable",
                },
            ],
        )
        self.assertFalse(ok)
        assert message is not None
        self.assertIn("#8 proposes 1.0.2", message)
        self.assertIn("#9 proposes 1.5.0", message)


if __name__ == "__main__":
    unittest.main(verbosity=2)

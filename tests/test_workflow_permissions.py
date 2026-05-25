#!/usr/bin/env python3
"""SECURITY-AUDIT-FIX-001 regression guard for GitHub Actions workflows.

Locks in the workflow-hardening invariants introduced by
``SECURITY-AUDIT-FIX-001`` (the concrete follow-up found by
``REPO-FRESHNESS-ROADMAP-AUDIT-001`` / PR #582) so they cannot silently
regress:

  * every workflow under ``.github/workflows/`` declares an explicit
    top-level ``permissions:`` block (no inheriting the repo-default,
    potentially read-write, token scope);
  * no workflow uses the ``pull_request_target`` trigger (which would run
    with a read-write token in the context of the base repo on untrusted
    PR head code);
  * no workflow uses ``permissions: write-all`` at any scope;
  * no ``write`` permission scope is granted (top-level or job-level)
    unless it is explicitly allowlisted here with a documented reason;
  * every third-party / first-party action ``uses:`` reference is either
    pinned to an immutable commit SHA **or** listed in the documented
    mutable-major-tag allowlist below (the inventory pending
    ``SECURITY-ACTION-PINNING-001``).

Pinning policy note (do not over-claim): this repo currently pins actions
to **mutable major tags** (e.g. ``actions/checkout@v4``), not immutable
commit SHAs. Converting to SHA pins is tracked as the follow-up
``SECURITY-ACTION-PINNING-001``. This test therefore does not assert that
pins are immutable; it asserts that any action in use is *either*
SHA-pinned *or* an already-inventoried major tag, so that adding a new,
undocumented, unpinned action fails until it is consciously reviewed.

Run with:

    python3 tests/test_workflow_permissions.py
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_DIR = REPO_ROOT / ".github" / "workflows"

# ---------------------------------------------------------------------------
# Allowlist: write permission scopes that are legitimately required.
# Keyed by (workflow filename, scope location, scope name) -> reason.
# "scope location" is either "<top-level>" or the job id.
# ---------------------------------------------------------------------------
WRITE_PERMISSION_ALLOWLIST: dict[tuple[str, str, str], str] = {
    (
        "firmware-build-release.yml",
        "release",
        "contents",
    ): (
        "The release job attaches firmware binaries + checksums + manifest "
        "to the GitHub Release via softprops/action-gh-release, which "
        "requires contents: write. Scoped to this job only."
    ),
}

# ---------------------------------------------------------------------------
# Allowlist: action references pinned to mutable major tags. Each entry is
# the documented current inventory pending SECURITY-ACTION-PINNING-001
# (SHA-pinning). Adding a new action requires either a SHA pin or a
# conscious addition here with a reason.
# ---------------------------------------------------------------------------
MUTABLE_ACTION_TAG_ALLOWLIST: dict[str, str] = {
    "actions/checkout@v4": "first-party GitHub action; major-tag pin (SECURITY-ACTION-PINNING-001)",
    "actions/setup-python@v5": "first-party GitHub action; major-tag pin (SECURITY-ACTION-PINNING-001)",
    "actions/cache@v4": "first-party GitHub action; major-tag pin (SECURITY-ACTION-PINNING-001)",
    "actions/upload-artifact@v4": "first-party GitHub action; major-tag pin (SECURITY-ACTION-PINNING-001)",
    "actions/download-artifact@v4": "first-party GitHub action; major-tag pin (SECURITY-ACTION-PINNING-001)",
    "softprops/action-gh-release@v2": "third-party action; major-tag pin — highest-value SHA-pin target (SECURITY-ACTION-PINNING-001)",
}

_SHA_PIN_RE = re.compile(r"@[0-9a-f]{40}$")
_USES_RE = re.compile(r"^\s*-?\s*uses:\s*(?P<ref>\S+)", re.MULTILINE)


def _workflow_paths() -> list[Path]:
    paths = sorted(WORKFLOW_DIR.glob("*.yml")) + sorted(WORKFLOW_DIR.glob("*.yaml"))
    return paths


def _strip_comment_lines(text: str) -> str:
    """Drop comment-only lines so narrative comments don't trip raw-text checks."""
    return "\n".join(
        line for line in text.splitlines() if line.lstrip()[:1] != "#"
    )


def _triggers(data: dict) -> dict:
    """Return the workflow's ``on:`` mapping.

    PyYAML parses the bare key ``on:`` as the boolean ``True`` (YAML 1.1
    truthy key), so the trigger block can land under either ``"on"`` or
    ``True`` depending on how it was written. Handle both.
    """
    raw = data.get("on")
    if raw is None:
        raw = data.get(True)
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, list):
        return {key: None for key in raw}
    if isinstance(raw, str):
        return {raw: None}
    return {}


def _iter_permission_scopes(perms):
    """Yield (scope_name, value) pairs from a permissions value.

    Handles the mapping form (``{contents: write}``) and the string form
    (``write-all`` / ``read-all``).
    """
    if isinstance(perms, dict):
        for name, value in perms.items():
            yield str(name), str(value)
    elif isinstance(perms, str):
        yield "<all>", perms


class WorkflowPermissionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(
            WORKFLOW_DIR.is_dir(),
            f"missing workflows directory: {WORKFLOW_DIR}",
        )
        self.paths = _workflow_paths()
        self.assertTrue(self.paths, "no workflow files found to validate")
        self.parsed = {
            path.name: yaml.safe_load(path.read_text(encoding="utf-8"))
            for path in self.paths
        }
        self.raw = {
            path.name: path.read_text(encoding="utf-8") for path in self.paths
        }

    def test_every_workflow_has_explicit_top_level_permissions(self) -> None:
        for name, data in self.parsed.items():
            self.assertIsInstance(
                data, dict, f"{name}: workflow did not parse to a mapping"
            )
            self.assertIn(
                "permissions",
                data,
                f"{name}: missing explicit top-level 'permissions:' block. "
                "Add least-privilege 'permissions:\\n  contents: read' "
                "(SECURITY-AUDIT-FIX-001) so the workflow does not inherit "
                "the repo-default (potentially read-write) token scope.",
            )

    def test_no_pull_request_target_trigger(self) -> None:
        for name, data in self.parsed.items():
            triggers = _triggers(data)
            self.assertNotIn(
                "pull_request_target",
                triggers,
                f"{name}: uses the 'pull_request_target' trigger, which runs "
                "with a read-write token in the base-repo context against "
                "untrusted PR head code. This is forbidden by "
                "SECURITY-AUDIT-FIX-001.",
            )
            # Belt-and-braces raw-text check (comment lines stripped) in case
            # the trigger lands under the YAML boolean 'True' key in an odd
            # formatting that _triggers misses.
            self.assertNotIn(
                "pull_request_target",
                _strip_comment_lines(self.raw[name]),
                f"{name}: references 'pull_request_target' in workflow body.",
            )

    def test_no_write_all_permissions(self) -> None:
        for name, data in self.parsed.items():
            # Top-level
            for _, value in _iter_permission_scopes(data.get("permissions")):
                self.assertNotEqual(
                    value,
                    "write-all",
                    f"{name}: top-level 'permissions: write-all' is forbidden "
                    "by SECURITY-AUDIT-FIX-001.",
                )
            # Job-level
            for job_id, job in (data.get("jobs") or {}).items():
                if not isinstance(job, dict):
                    continue
                for _, value in _iter_permission_scopes(job.get("permissions")):
                    self.assertNotEqual(
                        value,
                        "write-all",
                        f"{name}: job '{job_id}' uses 'permissions: write-all', "
                        "which is forbidden by SECURITY-AUDIT-FIX-001.",
                    )

    def test_no_unallowlisted_write_permissions(self) -> None:
        offenders: list[str] = []
        for name, data in self.parsed.items():
            locations = [("<top-level>", data.get("permissions"))]
            for job_id, job in (data.get("jobs") or {}).items():
                if isinstance(job, dict):
                    locations.append((job_id, job.get("permissions")))

            for location, perms in locations:
                for scope, value in _iter_permission_scopes(perms):
                    if value != "write":
                        continue
                    key = (name, location, scope)
                    if key not in WRITE_PERMISSION_ALLOWLIST:
                        offenders.append(
                            f"{name}: {location}: '{scope}: write' is not "
                            "allowlisted. Either remove the write scope or add "
                            "it to WRITE_PERMISSION_ALLOWLIST with a reason."
                        )
        self.assertEqual(offenders, [], "\n".join(offenders))

    def test_action_pins_are_sha_or_documented(self) -> None:
        offenders: list[str] = []
        for name, raw in self.raw.items():
            for match in _USES_RE.finditer(raw):
                ref = match.group("ref").strip().strip("'\"")
                # Local composite actions reference a path, not a versioned ref.
                if ref.startswith("./") or ref.startswith("../"):
                    continue
                if _SHA_PIN_RE.search(ref):
                    continue
                if ref in MUTABLE_ACTION_TAG_ALLOWLIST:
                    continue
                offenders.append(
                    f"{name}: action '{ref}' is neither SHA-pinned nor in "
                    "MUTABLE_ACTION_TAG_ALLOWLIST. Pin it to an immutable "
                    "commit SHA, or add it to the allowlist with a reason "
                    "(tracked by SECURITY-ACTION-PINNING-001)."
                )
        self.assertEqual(offenders, [], "\n".join(offenders))

    def test_allowlisted_actions_are_all_in_use(self) -> None:
        # Keep the documented inventory honest: every allowlisted major-tag
        # entry must still be referenced by some workflow, so the inventory
        # does not rot as actions are removed.
        all_refs: set[str] = set()
        for raw in self.raw.values():
            for match in _USES_RE.finditer(raw):
                all_refs.add(match.group("ref").strip().strip("'\""))
        unused = sorted(set(MUTABLE_ACTION_TAG_ALLOWLIST) - all_refs)
        self.assertEqual(
            unused,
            [],
            "MUTABLE_ACTION_TAG_ALLOWLIST has entries no longer used by any "
            f"workflow (remove them): {unused}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

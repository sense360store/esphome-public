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
  * every action ``uses:`` reference is pinned to an immutable 40-hex
    commit SHA (local ``./`` composite actions and any explicitly
    documented exception in ``MUTABLE_TAG_PIN_EXCEPTIONS`` are exempt).

Pinning policy note: ``SECURITY-ACTION-PINNING-001`` converted all six
referenced actions from mutable major tags (e.g. ``actions/checkout@v4``)
to immutable commit SHAs, preserving the resolved upstream version in a
trailing comment for maintainability. This test now asserts immutability:
any action that is not SHA-pinned, not a local composite action, and not a
documented exception fails, so a new mutable-tag reference cannot slip in.

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
# Allowlist: action references that are deliberately NOT pinned to an
# immutable commit SHA, each with a documented reason. SECURITY-ACTION-
# PINNING-001 converted all six referenced actions to commit SHAs, so this
# is empty. Any future action that genuinely cannot be SHA-pinned must be
# added here with a reason; otherwise it must be SHA-pinned.
# ---------------------------------------------------------------------------
MUTABLE_TAG_PIN_EXCEPTIONS: dict[str, str] = {}

# ---------------------------------------------------------------------------
# Inventory: the SHA-pinned actions and the upstream version each SHA
# resolves to (mirrors docs/workflow-security-hardening.md §2). Kept honest
# by test_pinned_action_inventory_is_in_use so the inventory does not rot.
# ---------------------------------------------------------------------------
SHA_PINNED_ACTION_INVENTORY: dict[str, str] = {
    "actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5": "v4.3.1",
    "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065": "v5.6.0",
    "actions/cache@0057852bfaa89a56745cba8c7296529d2fc39830": "v4.3.0",
    "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02": "v4.6.2",
    "actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093": "v4.3.0",
    "softprops/action-gh-release@3bb12739c298aeb8a4eeaf626c5b8d85266b0e65": "v2.6.2",
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

    def _all_uses_refs(self) -> set[str]:
        refs: set[str] = set()
        for raw in self.raw.values():
            for match in _USES_RE.finditer(raw):
                refs.add(match.group("ref").strip().strip("'\""))
        return refs

    def test_action_pins_are_immutable_sha(self) -> None:
        offenders: list[str] = []
        for name, raw in self.raw.items():
            for match in _USES_RE.finditer(raw):
                ref = match.group("ref").strip().strip("'\"")
                # Local composite actions reference a path, not a versioned ref.
                if ref.startswith("./") or ref.startswith("../"):
                    continue
                if _SHA_PIN_RE.search(ref):
                    continue
                if ref in MUTABLE_TAG_PIN_EXCEPTIONS:
                    continue
                offenders.append(
                    f"{name}: action '{ref}' is not pinned to an immutable "
                    "40-hex commit SHA. Pin it to a commit SHA (keep the "
                    "upstream version in a trailing comment), or add it to "
                    "MUTABLE_TAG_PIN_EXCEPTIONS with a reason "
                    "(SECURITY-ACTION-PINNING-001)."
                )
        self.assertEqual(offenders, [], "\n".join(offenders))

    def test_pin_exceptions_are_all_in_use(self) -> None:
        # Keep the exception list honest: every documented not-SHA-pinned
        # exception must still be referenced by a workflow.
        unused = sorted(set(MUTABLE_TAG_PIN_EXCEPTIONS) - self._all_uses_refs())
        self.assertEqual(
            unused,
            [],
            "MUTABLE_TAG_PIN_EXCEPTIONS has entries no longer used by any "
            f"workflow (remove them): {unused}",
        )

    def test_pinned_action_inventory_is_in_use(self) -> None:
        # Keep the documented SHA-pin inventory honest: every inventoried
        # SHA pin must still be referenced by a workflow, so the inventory
        # (and docs/workflow-security-hardening.md §2) does not rot.
        unused = sorted(set(SHA_PINNED_ACTION_INVENTORY) - self._all_uses_refs())
        self.assertEqual(
            unused,
            [],
            "SHA_PINNED_ACTION_INVENTORY has entries no longer used by any "
            f"workflow (update the inventory + docs): {unused}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

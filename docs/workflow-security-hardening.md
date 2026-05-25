# GitHub Actions Workflow Security Hardening

**Owner id:** `SECURITY-AUDIT-FIX-001`
**Date:** 2026-05-25
**Scope repo:** `sense360store/esphome-public`
**Source:** concrete hardening follow-up found by `REPO-FRESHNESS-ROADMAP-AUDIT-001` / PR #582.

This document records the security posture of the workflows under
`.github/workflows/`: the least-privilege token model now applied, the
action-pin inventory, the pinning policy decision, and the regression
guard that locks these invariants in. It is **not** a clean bill of
health — see [Explicitly not claimed](#explicitly-not-claimed).

---

## 1. Token permissions model (applied)

All five workflows now declare an **explicit top-level
`permissions:`** block. The repo-default (potentially read-write)
inherited token scope is no longer relied on anywhere.

| Workflow | Trigger(s) | Top-level `permissions:` | Job-level override | Why |
|---|---|---|---|---|
| `validate.yml` | push / PR | `contents: read` | — | read-only validation scripts only |
| `compile-only.yml` | push / PR / dispatch | `contents: read` | — | metadata + (manual) compile validation; no writes |
| `ci-validate-configs.yml` | dispatch | `contents: read` | — | manual broad/legacy `esphome config` + lint sweep; no writes |
| `release-notes-draft.yml` | dispatch | `contents: read` | — | drafts notes + uploads a CI artifact only |
| `firmware-build-release.yml` | release / dispatch | `contents: read` | `release` job: `contents: write` | only the `release` job attaches assets to the GitHub Release |

**Least-privilege detail for `firmware-build-release.yml`:** the
top-level scope was narrowed from `contents: write` to `contents: read`.
Write access is granted **only** on the `release` job, which uploads
firmware binaries + checksums + manifest via
`softprops/action-gh-release` (this genuinely needs `contents: write`).
The `generate-matrix`, `build`, and `summary` jobs only read the repo and
exchange CI artifacts through the artifact service (which does not use the
`contents` scope), so they run read-only.

Other trigger-safety facts confirmed (and regression-guarded):

- **No `pull_request_target` trigger** in any workflow (would run with a
  read-write token in the base-repo context against untrusted PR head
  code).
- **No `permissions: write-all`** at any scope.
- The release flow uses the built-in `GITHUB_TOKEN` (`secrets.GITHUB_TOKEN`),
  not a long-lived PAT.

---

## 2. Action-pin inventory

As of 2026-05-25 the workflows reference six actions, **all pinned to
mutable major tags** (not immutable commit SHAs):

| Action | Pin | First/third party | Notes |
|---|---|---|---|
| `actions/checkout` | `@v4` | first-party | repo checkout |
| `actions/setup-python` | `@v5` | first-party | Python toolchain |
| `actions/cache` | `@v4` | first-party | PlatformIO / pip cache |
| `actions/upload-artifact` | `@v4` | first-party | CI artifact upload |
| `actions/download-artifact` | `@v4` | first-party | CI artifact download |
| `softprops/action-gh-release` | `@v2` | **third-party** | release asset upload — **highest-value SHA-pin target** |

This inventory is mirrored in `MUTABLE_ACTION_TAG_ALLOWLIST` inside
`tests/test_workflow_permissions.py`, which keeps it from rotting (every
allowlisted entry must still be referenced by a workflow).

---

## 3. Pinning policy decision

**Current policy: documented mutable major-tag pins.** Converting all six
actions to immutable commit SHAs — and standing up the
Renovate/Dependabot follow-through needed to keep those SHAs current — is
broader than the permissions-hardening scope of `SECURITY-AUDIT-FIX-001`.
It is carried forward as the follow-up **`SECURITY-ACTION-PINNING-001`**
(start with the third-party `softprops/action-gh-release@v2`).

To prevent silent regression in the meantime,
`tests/test_workflow_permissions.py` requires every action `uses:`
reference to be **either** SHA-pinned **or** present in the documented
major-tag allowlist. A new, undocumented, unpinned action fails the test
until it is consciously reviewed.

> This repo does **not** currently claim immutable (SHA) action pinning.

---

## 4. Regression guard

`tests/test_workflow_permissions.py` (runs under
`python3 -m unittest discover -s tests`) asserts:

1. every workflow declares an explicit top-level `permissions:` block;
2. no workflow uses the `pull_request_target` trigger;
3. no workflow uses `permissions: write-all` (top-level or job-level);
4. no `write` scope is granted (top-level or job-level) unless explicitly
   allowlisted with a reason (`WRITE_PERMISSION_ALLOWLIST` — currently only
   the `firmware-build-release.yml` `release` job's `contents: write`);
5. every action `uses:` reference is SHA-pinned or in the documented
   major-tag allowlist (`MUTABLE_ACTION_TAG_ALLOWLIST`).

---

## 5. Explicitly not claimed

- **No security clean bill of health.** No Dependabot, code-scanning, or
  secret-scanning **alert** feed was available, so no "no vulnerabilities"
  claim is made.
- **No immutable action pinning** — major-tag pins remain; SHA conversion
  is the open follow-up `SECURITY-ACTION-PINNING-001`.
- No release-readiness, WebFlash-import-readiness, or compliance-approval
  claim is made or affected by this work.
- No validation workflow was weakened: token scopes were **tightened**,
  never widened, and no validation step was removed or relaxed.

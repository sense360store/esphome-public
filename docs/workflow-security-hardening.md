# GitHub Actions Workflow Security Hardening

**Owner id:** `SECURITY-AUDIT-FIX-001`
**Date:** 2026-05-25
**Updated:** 2026-05-27 by `SECURITY-ACTION-PINNING-001` (action SHA-pinning).
**Scope repo:** `sense360store/esphome-public`
**Source:** concrete hardening follow-up found by `REPO-FRESHNESS-ROADMAP-AUDIT-001` / PR #582.

This document records the security posture of the workflows under
`.github/workflows/`: the least-privilege token model applied by
`SECURITY-AUDIT-FIX-001`, the action-pin inventory (now converted to
immutable commit SHAs by `SECURITY-ACTION-PINNING-001`), the pinning
policy decision, and the regression guard that locks these invariants in.
It is **not** a clean bill of health — see
[Explicitly not claimed](#explicitly-not-claimed).

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
| `firmware-build-release.yml` | release / dispatch | `contents: read` | `release` job: `contents: write` + `id-token: write` | only the `release` job attaches assets to the GitHub Release and keyless-signs the checksums |

**Least-privilege detail for `firmware-build-release.yml`:** the
top-level scope was narrowed from `contents: write` to `contents: read`.
Write access is granted **only** on the `release` job, which uploads
firmware binaries + checksums + manifest via
`softprops/action-gh-release` (this genuinely needs `contents: write`).
The `generate-matrix`, `build`, and `summary` jobs only read the repo and
exchange CI artifacts through the artifact service (which does not use the
`contents` scope), so they run read-only.

`SEC-ESP-CHECKSUM-SIGNING-001` (security.md finding #3) additionally grants
the `release` job `id-token: write` so keyless Sigstore cosign can mint a
short-lived signing certificate from the workflow's OIDC identity and sign
`checksums-sha256.txt`. This is scoped to the `release` job only; the
top-level token stays `contents: read`.

Other trigger-safety facts confirmed (and regression-guarded):

- **No `pull_request_target` trigger** in any workflow (would run with a
  read-write token in the base-repo context against untrusted PR head
  code).
- **No `permissions: write-all`** at any scope.
- The release flow uses the built-in `GITHUB_TOKEN` (`secrets.GITHUB_TOKEN`),
  not a long-lived PAT.

---

## 2. Action-pin inventory (SHA-pinned by `SECURITY-ACTION-PINNING-001`)

The workflows reference seven actions, **all pinned to immutable 40-hex
commit SHAs** (the resolved upstream version is preserved in a trailing
`# vX.Y.Z` comment for maintainability). The original six SHAs (taken from
`git ls-remote --tags` on 2026-05-27) plus `sigstore/cosign-installer`
(added by `SEC-ESP-CHECKSUM-SIGNING-001`) are inventoried below.

| Action | Workflow file(s) | Previous ref | Pinned SHA | Resolves to | First/third party | Next maintenance action |
|---|---|---|---|---|---|---|
| `actions/checkout` | `validate.yml`, `compile-only.yml`, `ci-validate-configs.yml`, `release-notes-draft.yml`, `firmware-build-release.yml` | `@v4` | `34e114876b0b11c390a56381ad16ebd13914f8d5` | `v4.3.1` | first-party | bump SHA + comment when adopting a newer `v4.x`/`v5.x` |
| `actions/setup-python` | `validate.yml`, `compile-only.yml`, `ci-validate-configs.yml`, `release-notes-draft.yml`, `firmware-build-release.yml` | `@v5` | `a26af69be951a213d495a4c3e4e4022e16d87065` | `v5.6.0` | first-party | bump SHA + comment when adopting a newer `v5.x` |
| `actions/cache` | `compile-only.yml`, `ci-validate-configs.yml`, `firmware-build-release.yml` | `@v4` | `0057852bfaa89a56745cba8c7296529d2fc39830` | `v4.3.0` | first-party | bump SHA + comment when adopting a newer `v4.x` |
| `actions/upload-artifact` | `release-notes-draft.yml`, `firmware-build-release.yml` | `@v4` | `ea165f8d65b6e75b540449e92b4886f43607fa02` | `v4.6.2` | first-party | bump SHA + comment when adopting a newer `v4.x` |
| `actions/download-artifact` | `firmware-build-release.yml` | `@v4` | `d3f86a106a0bac45b974a628896c90dbdf5c8093` | `v4.3.0` | first-party | bump SHA + comment when adopting a newer `v4.x` |
| `softprops/action-gh-release` | `firmware-build-release.yml` | `@v2` | `3bb12739c298aeb8a4eeaf626c5b8d85266b0e65` | `v2.6.2` | **third-party** | bump SHA + comment when adopting a newer `v2.x`; highest-value pin target |
| `sigstore/cosign-installer` | `firmware-build-release.yml` | n/a (added by `SEC-ESP-CHECKSUM-SIGNING-001`) | `dc72c7d5c4d10cd6bcb8cf6e3fd625a9e5e537da` | `v3.7.0` | **third-party** | bump SHA + comment when adopting a newer `v3.x`/`v4.x` |

There are **no exceptions** — every referenced action is SHA-pinned, so
the documented-exception allowlist is empty. This inventory is mirrored in
`SHA_PINNED_ACTION_INVENTORY` inside `tests/test_workflow_permissions.py`,
which keeps it from rotting (every inventoried SHA pin must still be
referenced by a workflow).

---

## 3. Pinning policy decision

**Current policy: immutable commit-SHA pins for every action.**
`SECURITY-ACTION-PINNING-001` converted all six actions (first- and
third-party) from mutable major tags to commit SHAs, keeping the upstream
version visible in a trailing comment. This closes the SHA-pinning
follow-up carried forward from `SECURITY-AUDIT-FIX-001`.

`tests/test_workflow_permissions.py` now requires every action `uses:`
reference to be SHA-pinned (a local `./` composite action or an explicitly
documented `MUTABLE_TAG_PIN_EXCEPTIONS` entry are the only exemptions). A
new mutable-tag reference fails the test until it is SHA-pinned or
consciously excepted with a reason.

> **Maintenance note.** SHA pins are immutable, so they do **not** receive
> upstream patch/security updates automatically. Refreshing them is a
> deliberate maintenance action: re-resolve the intended version with
> `git ls-remote --tags <repo>`, update the SHA **and** the trailing
> `# vX.Y.Z` comment, and update both this table and
> `SHA_PINNED_ACTION_INVENTORY`. Automating this (Renovate/Dependabot
> SHA-pin updates) remains an optional future enhancement, not a claim
> made here.

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
5. every action `uses:` reference is pinned to an immutable 40-hex commit
   SHA, except local `./` composite actions and documented
   `MUTABLE_TAG_PIN_EXCEPTIONS` entries (currently none);
6. the documented exception list and the `SHA_PINNED_ACTION_INVENTORY`
   stay honest (no entry that is no longer referenced by a workflow).

---

## 5. Explicitly not claimed

- **No security clean bill of health.** No Dependabot, code-scanning, or
  secret-scanning **alert** feed was available, so no "no vulnerabilities"
  claim is made.
- **No automatic update guarantee.** SHA pins are immutable and do not
  self-update; keeping them current is a manual maintenance action (§3).
  No Renovate/Dependabot SHA-bump automation is claimed.
- No release-readiness, WebFlash-import-readiness, or compliance-approval
  claim is made or affected by this work.
- No validation workflow was weakened: token scopes remain **tightened**,
  no validation step was removed or relaxed, and pinning changed only the
  action ref (SHA instead of tag) — never the workflow's triggers,
  permissions, jobs, scripts, environments, secrets, or build logic.

# Docs disposition manifest: esphome-public and webflash

Generated 2026-07-04 from live clones (esphome-public @ HEAD, webflash @
`7f00997`).

Status: **approved** (ratified 2026-07-04). Every former `DECIDE` row is
resolved by the owner decisions of record below, and the ratified amendments
have been applied to the affected rows. This file is the **sole disposition
authority** and the **single canonical text** for the `DOCS-DISPOSITION-001`
programme — it supersedes the copy of this manifest on WebFlash main (added
there by WebFlash PR #569), whose guard-test execution notes are folded into
the execution constraints below. Each disposition step is executed in its own
follow-up PR (queued as `DOCS-DISPOSITION-001` in
[`UPCOMING_PR.md`](../UPCOMING_PR.md)) and recorded in the
[Execution log](#execution-log). No file was moved, merged, slimmed, or
removed by the ratification PR itself.

Actions:

- **KEEP** — production doc, stays.
- **KEEP-SLIM** — keep but strip embedded audit trail to archive.
- **KEEP-SANITISE** — keep, but strip internal process and commercial
  detail; retain repo conventions and gates.
- **MERGE** — duplicate pair, consolidate.
- **ARCHIVE** — delete from the tree plus an index row in
  `docs/archive-index.md` (`| original path | last main SHA containing the
  file | disposition | date |`), plus a three-line stub at the old path where
  a cross-repo link requires one. Never rewrite then delete. The private
  records repo is populated later from the indexed SHAs (owner decision 6).
- **MOVE-PRIVATE** — delete from the public tree with an index row; content
  remains recoverable from the indexed SHA for the private records repo.
- **REMOVE** — working state, transfer to issues then delete.
- **DECIDE** — needed an owner call; all `DECIDE` rows are now resolved (see
  the owner decisions of record below and the per-repo `DECIDED` sections).

## Owner decisions of record (ratified 2026-07-04)

1. `docs/sense360-roadmap-status.md` → **KEEP** (remains the internal status
   page).
2. `CLAUDE.md` → **KEEP-SANITISE** (strip internal process and commercial
   detail; retain repo conventions and gates). Executed at Step 7.
3. `docs/shop-commercial-source-of-truth.md` → **MOVE-PRIVATE** (delete from
   the public tree; retire `tests/test_shop_commercial_source_of_truth.py`
   in the same PR; content remains recoverable from the indexed SHA).
   Executed at Step 6.
4. `include/README.md` → **KEEP**.
5. WebFlash side, recorded here for the cross-repo picture:
   `docs/sense360-webflash-status.md` → **KEEP**; `CLAUDE.md` →
   **KEEP-SANITISE**. Executed in the WebFlash repo, Phase 2.
6. Archive destination: private records repo populated later from the SHAs
   in `docs/archive-index.md`. The in-tree result of ARCHIVE is deletion
   plus index entry plus stub where a cross-repo link requires one.

Ratified amendments: `docs/firmware-combination-matrix.md` and
`docs/firmware-build-gap-report.md` → **KEEP** (CI-generated with freshness
gates; generators stay). `docs/webflash-contract.md` → **KEEP** (inter-repo
interface contract).

## Execution constraints (read before acting on any row)

The action labels classify *content*; they do not prove a file is safe to
move. Verified against the tree at generation time:

1. **Code-referenced docs.** Many `ARCHIVE` / `MERGE` / `KEEP-SLIM` rows are
   referenced by `scripts/*.py`, `tests/*.py`, or `.github/workflows/*.yml`
   (found via path grep). Notable examples:
   `docs/firmware-build-gap-report.md` and
   `docs/firmware-combination-matrix.md` are **generated files with CI
   freshness gates** (`scripts/generate_firmware_matrix.py --check`,
   `scripts/report_firmware_build_gaps.py --check`) — now `KEEP` by ratified
   amendment, generators stay;
   `docs/shop-commercial-source-of-truth.md` (a `MOVE-PRIVATE` row, owner
   decision 3) is pinned by
   `tests/test_shop_commercial_source_of_truth.py`, which is retired in the
   same PR (Step 6);
   `docs/package-triac-001-operator-bench-proof.md` is pinned by
   `tests/test_package_triac_001_operator_bench_proof.py`; the `MERGE` pair
   members `docs/hardware/s360-311-r4-pwm.md` and
   `docs/hardware/s360-312-r4-fandac.md` are referenced from tests, as are
   the `KEEP-SLIM` targets `docs/hardware/s360-100-r4-core.md` and
   `docs/hardware/s360-410-r4-poe.md`. Any disposition PR must re-run
   `grep -rE "docs/<name>\.md" scripts/ tests/ .github/` for each file it
   touches and update generators, tests, and workflow references in the same
   PR — CI (`validate.yml`) gates on them.
2. **`UPCOMING_PR.md` is load-bearing.** It is declared the source-of-truth
   queue by `CLAUDE.md`, and the standing-invariant gates link to its
   anchors. Its `REMOVE` disposition executes only at Step 7, together with
   the `CLAUDE.md` KEEP-SANITISE rewrite (owner decision 2) and a migration
   of the live queue + standing invariants to their new home (the queue
   snapshot in the Step 7 PR description + a durable
   `docs/standing-invariants.md` carrying the invariant content verbatim).
3. **Standing rules still apply.** No disposition may weaken the standing
   gates: FanTRIAC posture changes stay human-review-only, operator
   attestation blocks are never machine-written (relevant when slimming or
   archiving bench-proof docs), and archiving a governance record must
   preserve its content verbatim (move, don't rewrite). The governance
   directories `docs/security/`, `docs/compliance/`, `docs/decisions/`, and
   `docs/release-notes/` are KEEP in full — not moved or rewritten under
   this programme.
4. **webflash rows are recorded here for the cross-repo picture only.** They
   are executed in the `sense360store/WebFlash` repo, not from this one
   (Phase 2).

### WebFlash guard-test execution notes

Folded verbatim-in-substance from the copy of this manifest on WebFlash main
(WebFlash PR #569), which this file supersedes as the single canonical text:

- Several ARCHIVE rows on the webflash side are currently referenced as live
  contracts by `CLAUDE.md` and the guard tests (for example
  `docs/firmware-import.md`, `docs/product-import-readiness.md`,
  `docs/webflash-import-readiness-matrix.md`, `docs/conventions-history.md`,
  `docs/wizard-ux-roadmap.md`, `docs/led-preview-webflash-proof.md`).
  Executing those rows requires updating every inbound reference
  (`CLAUDE.md`, README, tests such as
  `__tests__/product-import-readiness.test.js`) in the same change, or the
  disposition must be downgraded to KEEP until the reference is retired.
- `UPCOMING_PR.md` removal (webflash side) likewise requires retiring the
  standing convention in `CLAUDE.md` that every queue-changing PR must
  update it, and transferring live queue items to GitHub issues or a project
  board first.
- Dispositions are per-repo: esphome-public rows are executed in
  `sense360store/esphome-public`, webflash rows in `sense360store/WebFlash`.

## esphome-public

### DECIDED (4 files, 64 KB — resolved by the owner decisions of record, 2026-07-04)

| File | KB | Disposition |
|---|---:|---|
| `docs/sense360-roadmap-status.md` | 34 | **KEEP** — remains the single internal status page (owner decision 1). |
| `CLAUDE.md` | 14 | **KEEP-SANITISE** — strip internal process and commercial detail; retain repo conventions and gates; point standing rules at `docs/standing-invariants.md`. Executed at Step 7 (owner decision 2). |
| `docs/shop-commercial-source-of-truth.md` | 11 | **MOVE-PRIVATE** — delete from the public tree; retire `tests/test_shop_commercial_source_of_truth.py` in the same PR; content remains recoverable from the indexed SHA. Executed at Step 6 (owner decision 3). |
| `include/README.md` | 5 | **KEEP** (owner decision 4). |

### REMOVE (1 file, 38 KB)

| File | KB | Rationale |
|---|---:|---|
| `UPCOMING_PR.md` | 38 | 38KB working queue at root. Snapshot the live queue into the Step 7 PR description, then delete with an index row. Git history retains it. Executed at Step 7; see execution constraint 2 above. |

### MERGE (4 files, 503 KB)

| File | KB | Rationale |
|---|---:|---|
| `docs/hardware/s360-311-r4-pwm.md` | 225 | Duplicate pair with s360-311-r4-fanpwm.md (naming drift). Merge into one clean S360-311 reference per official naming, archive the audit trail. |
| `docs/hardware/s360-312-r4-fandac.md` | 155 | See s360-312-r4-dac.md. |
| `docs/hardware/s360-312-r4-dac.md` | 87 | Duplicate pair with s360-312-r4-fandac.md. Same treatment. |
| `docs/hardware/s360-311-r4-fanpwm.md` | 35 | See s360-311-r4-pwm.md. |

### KEEP-SLIM (5 files, 742 KB)

| File | KB | Rationale |
|---|---:|---|
| `docs/hardware/s360-310-r4-relay.md` | 205 | Board reference with embedded audit trail. Keep a clean reference, move the trail to archive. |
| `docs/hardware/s360-410-r4-poe.md` | 192 | Board reference with embedded audit trail. Keep a clean reference, move the trail to archive. |
| `docs/hardware/s360-400-r4-power.md` | 171 | Board reference with embedded audit trail. Keep a clean reference, move the trail to archive. |
| `docs/hardware/s360-320-r4-triac.md` | 110 | Board reference with embedded audit trail. Keep a clean reference, move the trail to archive. |
| `docs/hardware/s360-100-r4-core.md` | 65 | Board reference with embedded audit trail. Keep a clean reference, move the trail to archive. |

### ARCHIVE (68 files, 4090 KB)

Rationale for every row: process artifact (audit / proof / dryrun / matrix /
plan / handoff). Delete plus index row in `docs/archive-index.md`, plus a
stub where a cross-repo link requires one; the private records repo is
populated later from the indexed SHAs (owner decision 6). Rows marked
**[code-ref]** were referenced from `scripts/`, `tests/`, or
`.github/workflows/` at generation time (see execution constraint 1) and are
executed in archive batch B (Step 3); unmarked rows are batch A (Step 2).
The two former **[generated]** rows (`docs/firmware-build-gap-report.md`,
`docs/firmware-combination-matrix.md`) and `docs/webflash-contract.md` moved
to KEEP by ratified amendment and no longer appear below.

| File | KB | Notes |
|---|---:|---|
| `docs/cleanup-audit.md` | 808 | [code-ref] |
| `docs/product-readiness-matrix.md` | 266 | [code-ref] |
| `docs/release-artifact-readiness-matrix.md` | 250 | [code-ref] |
| `docs/webflash-exposure-readiness-matrix.md` | 226 | [code-ref] |
| `docs/hardware/core-abstract-bus-reconciliation.md` | 167 | [code-ref] |
| `docs/hardware/package-readiness-matrix.md` | 159 | [code-ref] |
| `docs/blocker-burndown.md` | 134 | [code-ref] |
| `docs/package-naming-audit.md` | 122 | [code-ref] |
| `docs/hardware/board-readiness-matrix.md` | 107 | |
| `docs/hardware/firmware-package-mapping-audit.md` | 87 | |
| `docs/compile-only-firmware-validation.md` | 87 | [code-ref] |
| `docs/hardware/remaining-board-documentation-audit.md` | 68 | |
| `docs/product-availability-taxonomy.md` | 68 | |
| `docs/hardware/hardware-artifact-policy.md` | 65 | |
| `docs/arch-board-bundle-plan.md` | 59 | [code-ref] |
| `docs/release-one-hardware-audit.md` | 56 | [code-ref] |
| `docs/hardware/core-abstract-bus-001c-rebind-plan.md` | 53 | [code-ref] |
| `docs/package-poe-410-001-audit.md` | 50 | [code-ref] |
| `docs/product-led-preview-decision.md` | 50 | |
| `docs/preview-to-stable-promotion-gates.md` | 49 | [code-ref] |
| `docs/first-release-dryrun-checklist.md` | 46 | |
| `docs/package-poe-410-evidence-result.md` | 44 | |
| `docs/webflash-drift-audit.md` | 43 | [code-ref] |
| `docs/pre-hardware-prep-plan.md` | 42 | |
| `docs/product-deprecation-removal-policy.md` | 40 | |
| `docs/repo-freshness-roadmap-audit.md` | 40 | [code-ref] |
| `docs/webflash-compatibility-taxonomy-audit.md` | 40 | [code-ref] |
| `docs/sense360-room-bundles.md` | 39 | [code-ref] |
| `docs/product-onboarding.md` | 39 | [code-ref] |
| `docs/all-yaml-release-matrix.md` | 38 | [code-ref] |
| `docs/room-firmware-release-matrix.md` | 37 | |
| `docs/stable-target-expansion-plan.md` | 34 | [code-ref] |
| `docs/first-release-gates.md` | 32 | [code-ref] |
| `docs/modular-combinations.md` | 31 | |
| `docs/stable-target-ventiq-001-gate-closure.md` | 31 | [code-ref] |
| `docs/v1-r4-product-gap.md` | 30 | |
| `docs/room-firmware-release-notes.md` | 29 | |
| `docs/release-matrix-webflash-alignment.md` | 28 | |
| `docs/release-preview-build-dryrun.md` | 28 | |
| `docs/kit-intent-matrix.md` | 28 | |
| `docs/release-preview-build-dryrun-002.md` | 23 | |
| `docs/pre-hardware-room-bundle-release-handoff.md` | 22 | [code-ref] |
| `docs/compile-only-expansion-candidates.md` | 22 | [code-ref] |
| `docs/webflash-release-proof.md` | 21 | [code-ref] |
| `docs/webflash-release-handoff.md` | 21 | [code-ref] |
| `docs/release-channel-policy.md` | 21 | [code-ref] |
| `docs/board-combinations.md` | 19 | |
| `docs/release-preview-publish-plan.md` | 19 | |
| `docs/package-triac-001-operator-bench-proof.md` | 19 | [code-ref] |
| `docs/manual-install-fan-candidates.md` | 18 | [code-ref] |
| `docs/manual-user-walkthrough.md` | 18 | |
| `docs/product-config-audit-2026-06.md` | 18 | |
| `docs/release-preview-publish-results.md` | 17 | |
| `docs/repo-structure-audit.md` | 17 | [code-ref] |
| `docs/workflow-audit-2026-06.md` | 16 | |
| `docs/webflash-ci-alignment.md` | 16 | [code-ref] |
| `docs/first-release-publish-readiness.md` | 15 | |
| `docs/release-preview-compile-dryrun.md` | 15 | |
| `docs/release-one.md` | 14 | [code-ref] |
| `docs/product-release-matrix.md` | 13 | |
| `docs/preview-release-targets.md` | 13 | |
| `docs/release-preview-fan-triac-build-rows.md` | 11 | |
| `docs/release-preview-webflash-release-notes-dryrun.md` | 10 | |
| `docs/release-preview-webflash-build-rows.md` | 10 | |
| `docs/release-preview-webflash-wrappers.md` | 10 | |
| `docs/hardware/s360-310-relay-pinmap-reconcile.md` | 8 | |
| `docs/room-bundle-fan-compile-results.md` | 5 | |
| `docs/docs-consolidation-verify-001.md` | 5 | |

### KEEP (69 files, 1074 KB)

| File | KB | Rationale |
|---|---:|---|
| `docs/hardware/artifacts/S360-410-R4.md` | 76 | Production user or developer doc. |
| `docs/compliance/mains-voltage-uk-eu-assessment.md` | 61 | Governance record (security/compliance/decision/release note/gate). Stays, structure already correct. |
| `docs/hardware/artifacts/S360-400-R4.md` | 54 | Production user or developer doc. |
| `docs/hardware/s360-100-core-connector-pin-map.md` | 47 | Production user or developer doc. |
| `docs/hardware/artifacts/S360-310-R4.md` | 38 | Production user or developer doc. |
| `docs/hardware/artifacts/S360-320-R4.md` | 34 | Production user or developer doc. |
| `docs/hardware/artifacts/S360-100-R4.md` | 30 | Production user or developer doc. |
| `docs/hardware/artifacts/S360-312-R4.md` | 28 | Production user or developer doc. |
| `docs/hardware/artifacts/S360-311-R4.md` | 27 | Production user or developer doc. |
| `docs/product-matrix.md` | 26 | Production user or developer doc. |
| `docs/ci-pipeline.md` | 26 | Production user or developer doc. |
| `docs/hardware/s360-100-core-architecture.md` | 23 | Production user or developer doc. |
| `docs/security/SECURITY-AUDIT-2026-06.md` | 22 | Governance record. Stays, structure already correct. |
| `docs/hardware/s360-300-r4-led.md` | 21 | Board reference, reasonable size. |
| `docs/hardware/s360-200-r4-roomiq.md` | 21 | Board reference, reasonable size. |
| `README.md` | 21 | Front door. Polish pass for production tone. |
| `docs/hardware/artifacts/S360-200-R4.md` | 20 | Production user or developer doc. |
| `docs/hardware/artifacts/S360-210-R4.md` | 20 | Production user or developer doc. |
| `docs/webflash-contract.md` | 21 | Inter-repo interface contract (ratified amendment; was ARCHIVE [code-ref]). |
| `docs/firmware-build-gap-report.md` | 20 | CI-generated with freshness gate (`scripts/report_firmware_build_gaps.py --check`); generator stays (ratified amendment; was ARCHIVE [generated]). |
| `CHANGELOG.md` | 19 | Standard. |
| `docs/hardware/s360-100-native-tach-pulse-strategy.md` | 18 | Production user or developer doc. |
| `docs/configuration.md` | 17 | Production user or developer doc. |
| `docs/hardware/s360-100-native-fan-gpio-map.md` | 17 | Production user or developer doc. |
| `docs/security/rebuild-clean-credentials-001.md` | 15 | Governance record. Stays, structure already correct. |
| `docs/firmware-combination-matrix.md` | 15 | CI-generated with freshness gate (`scripts/generate_firmware_matrix.py --check`); generator stays (ratified amendment; was ARCHIVE [generated]). |
| `docs/hardware/s360-210-r4-airiq.md` | 15 | Board reference, reasonable size. |
| `docs/hardware/s360-311-module-pinmap.md` | 14 | Production user or developer doc. |
| `docs/repo-structure.md` | 14 | Production user or developer doc. |
| `docs/hardware/s360-211-r4-ventiq.md` | 13 | Board reference, reasonable size. |
| `packages/SENSE360_MODULES.md` | 12 | Production user or developer doc. |
| `docs/decisions/COMPLIANCE-001-RESOLUTION-001.md` | 12 | Governance record. Stays, structure already correct. |
| `docs/product-scaffold-generator.md` | 11 | Production user or developer doc. |
| `docs/system-architecture.md` | 11 | Production user or developer doc. |
| `docs/feature-entity-matrix.md` | 11 | Production user or developer doc. |
| `docs/installation.md` | 11 | Production user or developer doc. |
| `packages/README.md` | 10 | Production user or developer doc. |
| `docs/hardware/s360-410-module-pinmap.md` | 10 | Production user or developer doc. |
| `tests/README.md` | 10 | Production user or developer doc. |
| `docs/hardware/s360-211-module-pinmap.md` | 10 | Production user or developer doc. |
| `docs/hardware/s360-200-module-pinmap.md` | 10 | Production user or developer doc. |
| `docs/hardware/s360-320-module-pinmap.md` | 9 | Production user or developer doc. |
| `security.md` | 9 | Rename to SECURITY.md for GitHub recognition. |
| `docs/hardware/s360-400-module-pinmap.md` | 9 | Production user or developer doc. |
| `docs/hardware/s360-310-module-pinmap.md` | 9 | Production user or developer doc. |
| `docs/workflow-security-hardening.md` | 9 | Production user or developer doc. |
| `docs/hardware/s360-312-module-pinmap.md` | 9 | Production user or developer doc. |
| `docs/hardware-catalog.md` | 8 | Production user or developer doc. |
| `docs/hardware/fandac-i2c-address-verification.md` | 8 | Production user or developer doc. |
| `docs/development.md` | 8 | Production user or developer doc. |
| `docs/security/release-firmware-credential-posture.md` | 8 | Governance record. Stays, structure already correct. |
| `docs/hardware/s360-210-module-pinmap.md` | 7 | Production user or developer doc. |
| `docs/hardware/s360-300-module-pinmap.md` | 7 | Production user or developer doc. |
| `docs/DEV_WORKFLOW.md` | 6 | Production user or developer doc. |
| `docs/security/checksums-verification.md` | 6 | Governance record. Stays, structure already correct. |
| `docs/release-notes/manual-preview/ceiling-poe-ventiq-fantriac-roomiq.md` | 6 | Governance record. Stays, structure already correct. |
| `tests/INTEGRATION_GUIDE.md` | 6 | Production user or developer doc. |
| `docs/release-notes/experimental/ceiling-poe-ventiq-fantriac-roomiq.md` | 5 | Governance record. Stays, structure already correct. |
| `docs/release-notes/preview/v1.0.0-preview.md` | 4 | Governance record. Stays, structure already correct. |
| `docs/release-notes/manual-preview/ceiling-poe-ventiq-fanrelay-roomiq.md` | 4 | Governance record. Stays, structure already correct. |
| `docs/release-notes/manual-preview/ceiling-poe-fanpwm.md` | 4 | Governance record. Stays, structure already correct. |
| `docs/release-notes/manual-preview/ceiling-poe-fandac.md` | 4 | Governance record. Stays, structure already correct. |
| `docs/release-notes/preview/ceiling-poe-roomiq-led.md` | 4 | Governance record. Stays, structure already correct. |
| `docs/release-notes/preview/README.md` | 3 | Governance record. Stays, structure already correct. |
| `docs/release-notes/manual-preview/README.md` | 3 | Governance record. Stays, structure already correct. |
| `docs/release-notes/preview/ceiling-poe-airiq-roomiq.md` | 3 | Governance record. Stays, structure already correct. |
| `docs/release-notes/preview/ceiling-poe-roomiq.md` | 3 | Governance record. Stays, structure already correct. |
| `docs/release-notes/experimental/README.md` | 2 | Governance record. Stays, structure already correct. |
| `dev/README.md` | 1 | Production user or developer doc. |

## webflash

Recorded here for the cross-repo picture; executed in
`sense360store/WebFlash` (see execution constraint 4).

### DECIDED (2 files, 82 KB — resolved by the owner decisions of record, 2026-07-04)

| File | KB | Disposition |
|---|---:|---|
| `docs/sense360-webflash-status.md` | 57 | **KEEP** — remains the internal status page, WebFlash side (owner decision 5). Executed in the WebFlash repo, Phase 2. |
| `CLAUDE.md` | 25 | **KEEP-SANITISE** — same treatment as the esphome-public `CLAUDE.md` (owner decision 5). Executed in the WebFlash repo, Phase 2. |

### REMOVE (2 files, 138 KB)

| File | KB | Rationale |
|---|---:|---|
| `UPCOMING_PR.md` | 138 | 140KB working queue. Transfer to issues/project, delete from tree. |
| `docs/pr-comment.md` | 0 | 488 byte leftover scratch file. |

### ARCHIVE (33 files, 762 KB)

Rationale for every row (except where noted): process artifact (audit /
proof / dryrun / matrix / plan / handoff). Move to `docs/archive/` with an
index entry, or a private records repo.

| File | KB | Notes |
|---|---:|---|
| `docs/wizard-ux-roadmap.md` | 89 | |
| `docs/webflash-import-readiness-matrix.md` | 72 | |
| `docs/webflash-cleanup-audit.md` | 70 | |
| `docs/conventions-history.md` | 63 | |
| `docs/webflash-required-configs-cleanup.md` | 45 | |
| `docs/github-pages-surface-audit.md` | 43 | |
| `docs/dual-channel-coexistence-design.md` | 29 | |
| `docs/firmware-import.md` | 27 | |
| `docs/led-preview-webflash-proof.md` | 27 | |
| `docs/led-preview-import-plan.md` | 26 | |
| `docs/product-import-readiness.md` | 21 | |
| `FIRMWARE-DISTRIBUTION-REVIEW.md` | 21 | One-off review record. |
| `docs/webflash-2-migration.md` | 18 | |
| `docs/webflash-2-migration-prompts.md` | 18 | |
| `docs/fan-bundle-preview-import-proof.md` | 15 | |
| `docs/preview-import-automation-proof.md` | 15 | |
| `docs/ux-roadmap.md` | 14 | |
| `docs/webflash-2-beta-default-s360-410-evidence.md` | 13 | |
| `docs/workflow-audit.md` | 12 | |
| `docs/fanpwm-preview-import-proof.md` | 12 | |
| `docs/webflash-bundle-sku-matrix.md` | 12 | |
| `docs/fanrelay-preview-import-proof.md` | 12 | |
| `docs/live-smoke-easy-bundle-picker-current.md` | 11 | |
| `docs/live-smoke-preview-import.md` | 10 | |
| `docs/wf-ux-017-freshness-diagnosis.md` | 10 | |
| `docs/wf-import-pwm-001-closure.md` | 10 | |
| `docs/preview-import-first-batch-proof.md` | 10 | |
| `docs/webflash-2-migration-delivery.md` | 9 | |
| `docs/live-smoke-easy-bundle-picker-fan-expansion.md` | 8 | |
| `docs/live-smoke-easy-bundle-picker.md` | 7 | |
| `docs/wf-manifest-freshness-race-diagnosis.md` | 6 | |
| `docs/expected-surface-fixture.md` | 4 | |
| `docs/docs-consolidation-verify-001.md` | 3 | |

### KEEP (17 files, 312 KB)

| File | KB | Rationale |
|---|---:|---|
| `README.md` | 56 | Front door, 57KB is too long. Split user quickstart vs everything else. |
| `DEVELOPER.md` | 38 | Contributor doc. |
| `CHANGELOG.md` | 33 | Standard. |
| `firmware-signing/README.md` | 26 | Signing/verification doc, user facing trust surface. |
| `docs/release-gates/WEBFLASH-FIRST-RELEASE-DRYRUN-HANDOFF-001.md` | 24 | Governance record. Stays, structure already correct. |
| `docs/security/SECURITY-AUDIT-2026-06.md` | 18 | Governance record. Stays, structure already correct. |
| `docs/release-gates/WF-LIVE-SMOKE-2-0-DEFAULT-001.md` | 17 | Governance record. Stays, structure already correct. |
| `docs/security/CTF-AUDIT-2026-07-03.md` | 14 | Governance record. Stays, structure already correct. |
| `docs/release-gates/WEBFLASH-FIRST-RELEASE-GATES-SYNC-001.md` | 14 | Governance record. Stays, structure already correct. |
| `docs/release-gates/WEBFLASH-LIVE-MANIFEST-FRESHNESS-SMOKE-001.md` | 13 | Governance record. Stays, structure already correct. |
| `docs/deploy-notes.md` | 12 | Production user or developer doc. |
| `docs/architecture.md` | 12 | Production user or developer doc. |
| `security.md` | 11 | Rename to SECURITY.md. |
| `docs/release-gates/PRE-HW-PREP-FIRST-RELEASE-GATES-001.md` | 10 | Governance record. Stays, structure already correct. |
| `docs/adr/0001-webflash-2-view-over-engine.md` | 6 | Governance record. Stays, structure already correct. |
| `TROUBLESHOOTING.md` | 5 | User doc. |
| `FEATURES.md` | 2 | Small, already redirects to canonical status. |

## Execution log

One step per session, one PR per step, lowest-numbered non-EXECUTED step
first. A step is marked EXECUTED (with its PR number) inside the same PR
that performs it.

| Step | Scope | PR | Date | Status |
|---|---|---|---|---|
| 1 | Ratify the manifest (owner decisions + amendments applied; WebFlash guard-test notes folded in; this log added) | #786 | 2026-07-04 | EXECUTED |
| 2 | Archive batch A (ARCHIVE rows without [code-ref]) | #787 | 2026-07-04 | EXECUTED |
| 3 | Archive batch B (ARCHIVE rows with [code-ref], reference updates in-PR) | — | 2026-07-04 | EXECUTED |
| 4 | Merge the duplicate pairs (S360-311, S360-312) | — | — | PENDING |
| 5 | Slim the five KEEP-SLIM board docs | — | — | PENDING |
| 6 | Execute MOVE-PRIVATE (`docs/shop-commercial-source-of-truth.md`) | — | — | PENDING |
| 7 | `CLAUDE.md` sanitise + `UPCOMING_PR.md` retirement (+ `docs/standing-invariants.md`) | — | — | PENDING |
| 8 | Link sweep + Phase 2 handoff section | — | — | PENDING |

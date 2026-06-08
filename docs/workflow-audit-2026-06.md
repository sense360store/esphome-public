# GitHub Actions workflow audit — 2026-06 (WORKFLOW-AUDIT-2026-06)

Review-first audit of every workflow in `.github/workflows/` for obsolescence,
redundancy, and staleness. Each verdict is backed by the workflow file **and**
its real Actions run history (pulled from the GitHub Actions API on 2026-06-08,
not inferred from the file alone).

This document **supersedes the workflow verdicts** in
[`cleanup-audit.md`](cleanup-audit.md) (CLEANUP-001), which was written when the
repo had only four workflows and is now out of date — it does not mention the
six workflows added since (`bump-version.yml`, `create-release.yml`,
`preview-fan-publish.yml`, `manual-firmware-artifacts.yml`,
`preview-compile-dryrun.yml`, and the renamed gate set), and it still lists
legacy `sense360-core-v-*` / voice / wall and `sense360-mini-*` product YAMLs
that have since been deleted from the tree. See the `CLEANUP-007` note appended
to that file.

## Method

- Read every workflow file in `.github/workflows/`.
- For each, pulled the Actions **run history** via the API
  (`actions/workflows/<file>/runs`): total run count, the most recent run's
  date, trigger event, and conclusion.
- Grepped the whole repo (`workflows/`, `scripts/`, `tests/`, `docs/`) for
  references before proposing any removal.
- For the failing workflow, read the failed-job logs of the last run to find
  the exact failure, not a guess.

## Per-workflow verdicts (with evidence)

| # | File | `name:` | Triggers | Total runs | Last run (UTC) | Last result | Verdict |
|---|------|---------|----------|-----------:|----------------|-------------|---------|
| 1 | `bump-version.yml` | Release 1: Bump Version | `workflow_dispatch` | 5 | 2026-06-07 21:40 | success | **Keep** — core release path |
| 2 | `create-release.yml` | Release: Create GitHub Release | `workflow_dispatch` | 7 | 2026-06-07 21:45 | success | **Keep** — core release path (added 2026-06-07) |
| 3 | `firmware-build-release.yml` | Release 3: Build & Release (auto on publish) | `release: [published]` | 29 | 2026-06-07 21:45 (`v1.0.4`) | success | **Keep** — core release path |
| 4 | `release-notes-draft.yml` | Release 2: Draft Notes | `workflow_dispatch` | 5 | 2026-06-07 11:24 | success | **Keep, but redundant in the release path** — fix stale order comments (PR for it) |
| 5 | `validate.yml` | CI: Quick Validation | `push` + `pull_request` | 1383 | 2026-06-07 22:20 | success | **Keep** — the per-PR gate |
| 6 | `compile-only.yml` | CI: Compile-Only | `push` + `pull_request` (+ `workflow_dispatch` full) | 428 | 2026-06-07 22:20 | success | **Keep** — active |
| 7 | `preview-compile-dryrun.yml` | CI: Preview Compile Dry-Run | `workflow_dispatch` | 1 | 2026-06-02 13:10 | success | **Keep** — distinct (hosted preview compile proof) |
| 8 | `manual-firmware-artifacts.yml` | Tools: Manual Firmware Artifacts | `workflow_dispatch` | 2 | 2026-05-27 18:20 | success | **Keep** — distinct (non-release artifact handoff) |
| 9 | `ci-validate-configs.yml` | CI: Validate Configs | `workflow_dispatch` | 238 | 2026-05-23 12:24 | **failure** | **Fix + scope** (separate PR); keep the workflow |
| 10 | ~~`preview-fan-publish.yml`~~ **(removed 2026-06-08)** | Publish: Fan Firmware (preview) | `workflow_dispatch` | **0** | **never ran** | — | **Removed 2026-06-08** — 0 runs / never executed; superseded by Create Release + Release 3 (which published the live `v1.0.0-preview` fan builds on the release event). Resolved from the "needs Neil" review item below. |

### Roles and overlaps

- **The release path is Release 1 → Create Release → Release 3** (`bump-version`
  → `create-release` → `firmware-build-release`). `create-release.yml` (added
  2026-06-07) generates and validates the WebFlash release notes inline and
  creates the tagged Release that fires Release 3. `firmware-build-release.yml`
  was narrowed to `on: release: [published]` only (PR #749, the redundant
  `workflow_dispatch` lane removed). These three are out of scope for changes
  beyond stale comments and are healthy and current.
- **`validate.yml`** is the only `push`/`pull_request` gate (the "Quick
  Validation" set: YAML syntax + the WebFlash build / catalog / release-notes
  unit tests). 1383 runs, green. The single most-used workflow.
- **`compile-only.yml`** runs metadata-only validation on every push/PR and a
  full `esphome compile` of `config/compile-only-targets.json` only on
  `workflow_dispatch compile_mode=full`. Green, active.
- **`ci-validate-configs.yml`** is a manual broad `esphome config` sweep. It
  overlaps partly with `compile-only` (curated compile) and `validate` (syntax),
  but at a different depth and scope. It gates nothing and is currently broken
  (see below).

## Hypotheses — confirmed / refuted

### `release-notes-draft.yml` (Release 2) is SUPERSEDED in the release path — CONFIRMED; but it is NOT dead → kept

**What the evidence shows.** `create-release.yml`'s own header states: *"Release
2: Draft Notes is now optional (a preview-only check): this workflow generates
and validates the same notes inline."* It does — it runs the same two scripts
Draft Notes runs (`generate_webflash_release_notes.py` then
`validate-webflash-release-notes.py`) and then creates the Release. Run history
confirms the real path: after Create Release landed (2026-06-07 11:43), releases
`v1.0.2` (16:24) and `v1.0.4` (21:45) were cut via Create Release → Release 3,
and **Draft Notes was not run for either** (its last run, 11:24, predates Create
Release). So Release 2 is genuinely out of the release path.

**Why it is kept, not removed.** "Confirmed dead" was not provable:

- Draft Notes is reachable, ran **green on 2026-06-07**, and uniquely uploads a
  downloadable `release-notes.md` artifact (Create Release only prints the body
  to the step summary). That is a real, if optional, standalone use.
- Its author **deliberately reframed** it as "optional (a preview-only check)"
  one day before this audit, rather than deleting it.
- It is wired into the repo: its contract test
  `tests/test_release_notes_draft_workflow.py` is a step in the Quick Validation
  PR gate (`validate.yml`), and `tests/test_release_product_selection.py` /
  `tests/test_check_pending_version_bump.py` assert its picker and preflight
  message. Removal would have multi-file tentacles into the gate.

**Action taken.** Keep the workflow and its test; correct the now-wrong
`Release 1 → Release 2 → Release 3` order comments in `bump-version.yml` (header,
arrow chain, and the PR body it opens), clarify `release-notes-draft.yml`'s
header as optional/preview-only, and align `docs/ci-pipeline.md` §6 with §7.
(Done in the "release order comments" PR.)

### `preview-fan-publish.yml` may be redundant with Create Release + Release 3 — RESOLVED 2026-06-08: REMOVED

**What the evidence shows.**

- **It has 0 runs. It has never executed.** (`actions/.../runs` → `total_count: 0`.)
- It was created 2026-06-06. The currently-live `v1.0.0-preview` fan builds were
  published **earlier**, on **2026-06-02**, by `firmware-build-release.yml`
  (Release 3) on the `v1.0.0-preview` release event (run titled *"Sense360
  room-bundle fan preview firmware 1.0.0"*, success). So this workflow was **not**
  the publish path for the live fan builds — it postdates them and never ran.
- It is **not unreferenced**: four contract tests
  (`tests/test_preview_fan_publish_{plan,results,tag_guard,workflow}.py`), two
  validator scripts (`validate_manual_preview_fan_publish.py`,
  `validate_room_bundle_fan_publish.py`), and several docs depend on it. It is a
  recent, intentional merge of two prior fan-publish workflows, and its
  `room-bundle` set targets five full-composition fan configs that are not yet
  published — i.e. it looks like a forward-looking publish tool awaiting first use.

**Conclusion (original audit).** Likely superseded by the generic Create Release
+ Release 3 flow, but **cannot be proven dead and unreferenced**, so it was **not
removed** at audit time. *Review item — confirm with Neil.*

**Resolution — 2026-06-08 (removed).** Neil confirmed the retirement. The
workflow was removed in the `ci/remove-preview-fan-publish` PR together with its
**dedicated-only** machinery: the two matrix/validator scripts
(`validate_manual_preview_fan_publish.py`, `validate_room_bundle_fan_publish.py`,
invoked by nothing but this workflow), the four `test_preview_fan_publish_*` and
three `test_room_bundle_fan_publish_*` contract tests (run by nothing but this
workflow's docs/scripts; not in the Quick Validation gate), and the six
`release-preview-fan-publish-*.md` / `room-bundle-fan-publish-*.md` lifecycle
docs. The `preview-fan-publish.yml` write-permission allowlist entry in
`tests/test_workflow_permissions.py` was dropped. The live `v1.0.0-preview` fan
preview product is **untouched**: the published `.bin` assets stay on the shared
release, and the shared/parked-track surfaces stay in place —
`config/preview-fan-triac-build-rows.json` (the build-row ledger, with its kept
validator `validate_preview_fan_triac_build_rows.py` + test
`test_preview_fan_triac_build_rows.py` and doc
`release-preview-fan-triac-build-rows.md`), `config/room-bundle-fan-variants.json`,
`config/preview-release-targets.json`, `config/webflash-builds.json`, and the
kept `preview-compile-dryrun.yml` lane (which still validates its target set).

### `manual-firmware-artifacts.yml` and `preview-compile-dryrun.yml` are distinct — CONFIRMED → keep

- **`preview-compile-dryrun.yml`** runs a hosted `esphome compile` **dry-run**
  over the preview / manual-preview target set
  (`config/preview-release-targets.json`) to replace the `pending-ci`
  `compile_validation_status` with real compile proof before any preview is
  published — uploading only an ephemeral compile **log**. Distinct target set
  and distinct purpose from `compile-only` (its own curated list) and from
  `validate` (syntax only). 1 run, green. **Keep.**
- **`manual-firmware-artifacts.yml`** compiles the FanRelay / FanPWM / FanDAC
  manual / no-WebFlash candidates and uploads **expiring** Actions artifacts for
  point-to-point operator handoff (requires an explicit
  `artifact_mode=manual-candidate`; never creates a Release). Neither
  `compile-only` nor `validate` produces downloadable `.bin` artifacts. 2 runs,
  green. **Keep.**

## `ci-validate-configs.yml` — diagnosis and fix

**Status:** `workflow_dispatch`-only (gates nothing); 238 runs; **every recent
run failed**; last run 2026-05-23, failure.

**Root causes (from the failed-job logs of run `26332573178`):**

1. **Missing secrets in product subdirectories.** Jobs failed with `esphome
   config` exit 2 and `Error reading file products/compile-only/secrets.yaml:
   [Errno 2] No such file or directory`. After the secret-guard refactor, the
   setup action provisions `secrets.yaml` only at the repo root and `products/`,
   so configs discovered under `products/compile-only/` and `products/bundles/`
   cannot resolve `!secret`.
2. **The external_components git clone.** The only active remote dependency is
   `packages/base/external_components.yaml` →
   `source: { type: git, url: https://github.com/sense360store/esphome-public }`
   (every `products/*.yaml` `type: git` reference is commented out). This lane
   rewrote `ref: main` → `ref: <branch>` and let `esphome config` clone it; that
   clone fails non-interactively when the rewritten ref is not fetchable on
   GitHub (`could not read Username`, git exit 128), surfacing as `esphome
   config` exit 2 across the matrix.

**Fix (separate PR):** both ESPHome lanes use the shared action's
`patch-external-components: true` (local `components/` tree, the pattern
`preview-compile-dryrun.yml` already uses) — eliminating the remote clone and
removing the fragile `sed` rewrites — and `extra-secrets-dirs` provisions the
product subdirectories.

**Scope (same PR):** the **default `quick`** matrix is now the maintained
Ceiling-POE shipping set (the five `config_string` product YAMLs in
`config/webflash-builds.json`); the broad legacy/manual product sweep (48
configs, legacy boards included, webflash wrappers excluded) and the full
generated module-combination walk are the opt-in **`full`** deep check. (The
legacy `sense360-core-v-*` voice/wall boards that the older audit flagged have
already been deleted from the tree; the remaining non-shipping configs — USB
variants, bundles, FanTRIAC, core-only boards — are exercised in `full` only.)

## Items left untouched because they could not be proven dead

| Item | Last run | Why left |
|------|----------|----------|
| `preview-fan-publish.yml` | **never (0 runs)** | ~~Needs Neil's decision.~~ **Resolved 2026-06-08 — removed** (Neil confirmed). Superseded by Create Release + Release 3. Removed with its dedicated-only validators/tests/docs in the `ci/remove-preview-fan-publish` PR; see the resolution note above. |
| `release-notes-draft.yml` | 2026-06-07 | Superseded in the release path but reachable, recently green, uniquely uploads an artifact, and deliberately kept as "optional preview-only" by Create Release; wired into the Quick Validation gate. Kept; only comments fixed. |
| Core release path (`bump-version` / `create-release` / `firmware-build-release`) | 2026-06-07 | Healthy and current; out of scope except stale comments (only `bump-version.yml`'s order comments were stale and are fixed). |

## Pre-existing issues observed (out of scope)

Two tests fail on `origin/main`, independent of any change here, both from the
same unpropagated version bump (the catalog moved to `Ceiling-POE-VentIQ-RoomIQ`
`v1.0.4` / `Ceiling-POE-VentIQ-RoomIQ-LED` `v1.0.3`, but some docs/tests still
pin `1.0.0`):

- `tests/test_release_product_selection.py` —
  `generate_webflash_release_notes.GeneratorError: --version '1.0.0' does not
  match catalog 'version' '1.0.3'` for `Ceiling-POE-VentIQ-RoomIQ-LED`.
- `tests/test_roadmap_status_doc.py` — asserts
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.4-stable.bin` appears in
  `docs/sense360-roadmap-status.md`, which still lists the older version.

**Neither is part of the Quick Validation gate (`validate.yml`), so the gate is
green.** Both are version drift, not a workflow-obsolescence matter; flagged for
a separate fix.

## Pull requests from this audit

- **Fix + scope `ci-validate-configs.yml`** (workflow fix + matching
  `docs/ci-pipeline.md` update).
- **Correct stale `R1 → R2 → R3` order comments** (`bump-version.yml`,
  `release-notes-draft.yml`, `docs/ci-pipeline.md` §6). Release 2 kept.
- **This findings report** + the `CLEANUP-007` correction note appended to
  `cleanup-audit.md`.
- **Remove `preview-fan-publish.yml`** (`ci/remove-preview-fan-publish`,
  2026-06-08) — retire the never-run, superseded fan-publish workflow and its
  dedicated-only validators, contract tests, and lifecycle docs; update this
  audit, `cleanup-audit.md`, `UPCOMING_PR.md`, and the workflow-permissions
  allowlist. Shared config (`preview-release-targets.json`,
  `room-bundle-fan-variants.json`, `webflash-builds.json`,
  `preview-fan-triac-build-rows.json`) and the live `v1.0.0-preview` fan preview
  product are untouched.

Acceptance per PR: `actionlint` on the changed workflows (with shellcheck) and
the full Quick Validation test set green.

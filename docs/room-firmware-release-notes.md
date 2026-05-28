# Room Firmware Release Notes (RELEASE-NOTES-PIPELINE-001)

## Purpose and scope

This document **defines the release-notes / changelog requirements** for the
currently release-eligible room firmware builds. It prepares the release
pipeline for real firmware publishing **without publishing any artifact**.

It answers one question — *"for the room firmware that release CI can build
today, what must a release-notes entry contain, and what must it never
claim?"* — and pairs the answer with a **dry-run generator**
([`scripts/plan_room_release_notes.py`](../scripts/plan_room_release_notes.py))
that emits a release-notes plan for those builds.

### Currently release-eligible builds

Release-eligibility is driven **exclusively** by
[`config/webflash-builds.json`](../config/webflash-builds.json) — the same
single source of truth the release workflow
([`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml))
filters by `version` + `channel` to generate its build matrix. Today that is:

| Config string | Channel | Artifact name |
|---|---|---|
| `Ceiling-POE-VentIQ-RoomIQ` | `stable` | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` |
| `Ceiling-POE-VentIQ-RoomIQ-LED` | `preview` | `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` |

`FanRelay` / `FanPWM` / `FanDAC` are **manual-candidate-only** (see
[`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json)
and [`docs/manual-install-fan-candidates.md`](manual-install-fan-candidates.md))
and are **not** promoted by this work. `FanTRIAC` is blocked (HW-005).

### This document defines, it does not publish

RELEASE-NOTES-PIPELINE-001 — this PR — does **not**:

- publish, build, or attach any firmware artifact, and creates no GitHub Release;
- commit any `.bin`, checksum, or build-info file;
- edit `products/**` or `products/webflash/**`;
- flip any `webflash_build_matrix` value or add an `artifact_name` to any fan product;
- add a release artifact or WebFlash exposure for any fan candidate;
- write [`firmware/sources.json`](../firmware/sources.json) or `manifest.json`;
- claim WebFlash / import / release / hardware-stable / compliance readiness
  for `FanRelay` / `FanPWM` / `FanDAC`, nor promote them out of
  manual-candidate-only.

Every classification below is **read** from the committed catalogs and
workflows cited inline; nothing is asserted beyond what they already record.

---

## Source-of-truth files

| Layer | File |
|-------|------|
| Release matrix (sole release-eligibility source) | [`config/webflash-builds.json`](../config/webflash-builds.json) |
| Release build/publish workflow | [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml) |
| Product lifecycle / hardware status | [`config/product-catalog.json`](../config/product-catalog.json) |
| Non-release fan candidates (excluded) | [`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json) |
| Per-config release-notes draft body | [`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py) |
| Release-body contract validator | [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py) |
| **Dry-run pipeline plan (this PR)** | [`scripts/plan_room_release_notes.py`](../scripts/plan_room_release_notes.py) |
| Shared external-component pin | [`packages/base/external_components.yaml`](../packages/base/external_components.yaml) |

---

## Required release-notes fields

Each release-eligible build's release-notes entry must record the following.
These are the fields the dry-run generator emits per build:

| Field | Source / rule |
|---|---|
| **Version / tag** | `version` from the build matrix; tag is `v{version}`. |
| **Channel** | `stable` or `preview`, from the build matrix. |
| **Config string** | The WebFlash config string (the build-matrix key). |
| **YAML path** | Canonical `products/sense360-*.yaml` + its `products/webflash/*` wrapper. |
| **Artifact name** | `artifact_name` from the build matrix (e.g. `Sense360-…-v1.0.0-stable.bin`). |
| **Commit SHA** | The commit the notes pin to (release CI passes `${{ github.sha }}`). |
| **ESPHome version** | `ESPHOME_VERSION` from the release workflow (currently `2026.4.5`). |
| **Source YAML GitHub URL** | `…/blob/<tag-or-commit>/<canonical yaml>`, pinned to the release tag **or** the commit — never `main`. |
| **Package / external-component pin status** | The git `ref` in `packages/base/external_components.yaml`. For a reproducible tagged release this must be pinned to the release tag, not `main`. |
| **Validation summary** | Result of `scripts/validate-webflash-release-notes.py` against the draft body for that channel. |
| **Known limitations** | Derived from the catalog only (`status`, `hardware_status`, `blocked_modules`, preview caveats). No invented claims. |
| **Explicit exclusions** | The fan-candidate / no-WebFlash / no-compliance statements below. |

### Release-body section contract

The draft body itself (produced by `generate_webflash_release_notes.py`)
must contain the four H2 sections enforced by the validator:

```
## Changelog
## Known Issues
## Features
## Hardware Requirements
```

---

## Per-channel requirements

### Stable — `Ceiling-POE-VentIQ-RoomIQ`

- `## Changelog` must be **human-authored**; filler (`TODO`, `TBD`, `initial
  release`, …) is rejected by the validator on the `stable` channel.
- `## Known Issues` records the by-design exclusions carried in the catalog's
  `blocked_modules`: **FanTRIAC** (blocked, HW-005) and **LED** (the config
  string has no LED token).
- Source YAML and the shared `external_components.yaml` should be pinned to
  `v1.0.0` at release time.
- Hardware status is reported verbatim from the catalog
  (`verified-for-release-one`); no claim beyond that recorded state.

### Preview — `Ceiling-POE-VentIQ-RoomIQ-LED`

- Lives on the `preview` channel; the generator **refuses** to emit
  stable-channel notes for it (promote to production first).
- A `TODO` changelog placeholder is acceptable for a preview draft, but human
  review is still expected before publishing.
- `## Features` includes the Sense360 LED ring (preview); `## Known Issues`
  still carries FanTRIAC (HW-005).
- Preview-stage S360-300 bench Open Questions (harness rail, LED count,
  harness identity — see `docs/hardware/s360-300-r4-led.md`) remain open and
  must resolve before any stable promotion. Hardware status is reported
  verbatim (`verified-led-candidate`).

---

## Explicit exclusions — fan candidates are not release artifacts

For `FanRelay` / `FanPWM` / `FanDAC`, the release-notes pipeline asserts:

- they are **not release artifacts** — they have no entry in
  `config/webflash-builds.json`, so release CI never builds or attaches them;
- they have **no WebFlash exposure** — no `products/webflash/*` wrapper and
  `webflash_build_matrix: false` in the catalog;
- the pipeline makes **no hardware-stable / compliance / release-ready claim**
  for them beyond their existing `hardware-pending` catalog state.

The dry-run generator both enforces this (it errors if a fan family token or
fan candidate `product_yaml` appears in the release matrix) and documents it
(it lists each excluded candidate with the statements above).

---

## Generating a dry-run plan

The dry-run generator is **read-only**: it creates no GitHub Release, builds
no firmware, and never writes `firmware/sources.json` or `manifest.json`.

```bash
# Print the plan for every release-eligible build to stdout:
python3 scripts/plan_room_release_notes.py

# Plan only one release target (RELEASE-PRODUCT-SELECTION-001):
python3 scripts/plan_room_release_notes.py \
    --config-string Ceiling-POE-VentIQ-RoomIQ

# Write the plan to a file and pin to a specific commit:
python3 scripts/plan_room_release_notes.py \
    --commit "$GITHUB_SHA" \
    --output release-notes-plan.md
```

To produce / validate a single build's draft body (the existing RELEASE-001 /
RELEASE-002 helpers, unchanged by this PR):

```bash
python3 scripts/generate_webflash_release_notes.py \
    --config-string Ceiling-POE-VentIQ-RoomIQ \
    --version 1.0.0 --channel stable --validate
```

To list every selectable release target (RELEASE-PRODUCT-SELECTION-001):

```bash
python3 scripts/list_release_targets.py
python3 scripts/list_release_targets.py --json
python3 scripts/list_release_targets.py --validate Ceiling-POE-VentIQ-RoomIQ
```

Tests: [`tests/test_plan_room_release_notes.py`](../tests/test_plan_room_release_notes.py)
(run with `python3 tests/test_plan_room_release_notes.py`) and
[`tests/test_list_release_targets.py`](../tests/test_list_release_targets.py)
(run with `python3 tests/test_list_release_targets.py`).

---

## RELEASE-CI-DRYRUN-001 — recorded dry-run of the release pipeline (2026-05-27)

RELEASE-CI-DRYRUN-001 **ran and recorded** a release-candidate dry-run for the
currently release-eligible room firmware builds. It is a **docs-only record**:
it publishes **no** GitHub Release, builds / attaches **no** firmware artifact,
writes **no** [`firmware/sources.json`](../firmware/sources.json) or
`manifest.json`, commits **no** `.bin` / checksum, edits **no**
`products/webflash/**`, and adds **no** fan `artifact_name` or
`webflash_build_matrix` flip.

### What was run

All commands were run read-only against the repo HEAD
(`cb15cffd6018645c3004bdbaf0f84edb3a8a6eba` at execution time; release CI pins
notes to `${{ github.sha }}` and the planner otherwise resolves the current
`git HEAD`):

| Command | Result |
|---|---|
| `python3 scripts/plan_room_release_notes.py` | OK — emitted a 2-build plan (no file written) |
| `python3 tests/test_plan_room_release_notes.py` | OK — 20 tests passed |
| `python3 tests/validate_configs.py` | OK — 208 files checked, 0 failed |
| `python3 scripts/validate_compile_targets.py --metadata-only` | OK — 12 compile-only targets, metadata valid |
| `python3 tests/validate_webflash_builds.py` | OK — 2 build entries checked, 0 failed |
| `python3 -m unittest discover -s tests -p "test_*.py"` | OK — 871 tests, 3 skipped |

### What the dry-run confirmed

- **Stable RoomIQ is included** — `Ceiling-POE-VentIQ-RoomIQ` (`stable`,
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`); release-notes draft
  validates `PASSED (structural, channel=stable)`.
- **Preview LED is included** — `Ceiling-POE-VentIQ-RoomIQ-LED` (`preview`,
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`); draft validates
  `PASSED (structural, channel=preview)`.
- **FanRelay / FanPWM / FanDAC are excluded** — none appear in
  `config/webflash-builds.json`; the planner's fan guardrail passed and they are
  listed under "Explicitly excluded — not release artifacts".
- **FanTRIAC is excluded / blocked** — no release build; carried in the stable
  config's catalog `blocked_modules` (HW-005) and reported as an excluded
  Known Issue in both draft bodies.
- **Required release-notes fields are present** for each build — version/tag
  placeholder, channel, config string, canonical + WebFlash-wrapper YAML path,
  artifact name, commit SHA, ESPHome version (`2026.4.5`), tag/commit-pinned
  source YAML URL, `external_components` pin status, validation summary, and
  catalog-derived known limitations.
- **No release side effects** — no GitHub Release; no
  `firmware/sources.json` / `manifest.json` update; no `.bin` / checksum
  committed (`git ls-files '*.bin'` is empty; there is no `firmware/`
  directory).

### Release workflow dry-run mode (implemented by RELEASE-WORKFLOW-DRYRUN-MODE-001)

At the time RELEASE-CI-DRYRUN-001 ran,
[`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)
had **no explicit dry-run mode**: its `workflow_dispatch` trigger compiled the
matrix and uploaded ephemeral CI artifacts via `actions/upload-artifact`, while
the `release` job — which generates `checksums-*.txt`, builds `manifest.json`,
runs the release-notes / asset-naming guards, and attaches assets via
`softprops/action-gh-release` — was gated `if: github.event_name == 'release'`.
A `workflow_dispatch` run therefore never published, but it also **built
binaries** and never exercised the release-notes / asset guards; it was a
build-only path, not a release-candidate dry-run.

`RELEASE-WORKFLOW-DRYRUN-MODE-001` adds that dry-run mode. The change is
deliberately **non-publishing by construction** — it does **not** relax the
publish job's gate. Instead:

1. **New `workflow_dispatch` input `dry_run`** (boolean, **default `true`** —
   safe / non-publishing).
2. **New read-only `release-dry-run` job**, gated
   `if: github.event_name == 'workflow_dispatch' && inputs.dry_run`, with
   `permissions: contents: read` (least privilege). It runs
   `scripts/plan_room_release_notes.py` (which enumerates the release-eligible
   builds, runs each draft body through
   `scripts/validate-webflash-release-notes.py`, and enforces the
   fan-exclusion guardrail), then the planner contract tests
   (`tests/test_plan_room_release_notes.py`,
   `tests/test_release_dry_run_mode.py`), and finally asserts no release
   side-effect file (`firmware/sources.json`, `manifest.json`, or a root
   `*.bin`) was produced. It contains **no** `softprops/action-gh-release`
   step, uploads **no** release asset, and writes nothing to the repo.
3. **Publishing stays gated to a real release event.** The `release` job's
   gate is unchanged (`if: github.event_name == 'release'`); it does not
   reference `workflow_dispatch` or `dry_run`, so the dry-run input **cannot**
   trigger a publish. `softprops/action-gh-release` appears only inside the
   `release` job. These invariants are locked in by
   [`tests/test_release_dry_run_mode.py`](../tests/test_release_dry_run_mode.py)
   and [`tests/test_workflow_permissions.py`](../tests/test_workflow_permissions.py).

`scripts/plan_room_release_notes.py` remains the supported **offline**
release-candidate dry-run; the new job runs that same planner **in CI** on
manual dispatch.

### Dry-run lane isolation (implemented by RELEASE-WORKFLOW-DRYRUN-GATE-FIX-001)

The first manual dispatch of the dry-run mode shipped above (workflow run
`26558131655`, commit `f6fe43366fbf3e70013e8189fbe8f49848fc7a82`) revealed
that `dry_run=true` was not fully isolating the dry-run lane. Two issues
surfaced:

1. **`generate-matrix` (Generate Build Matrix) was not gated.** Without an
   `if:` gate, it ran on every `workflow_dispatch` regardless of the
   `dry_run` input value, and the dispatch's default `version=0.0.0-dev` /
   `channel=preview` matched no entry in
   [`config/webflash-builds.json`](../config/webflash-builds.json) (which
   only carries `1.0.0/stable` and `1.0.0/preview`), so the
   `Generate product build matrix` step failed. The `build` and `summary`
   jobs would have inherited the same exposure if `generate-matrix` had
   succeeded.
2. **The `release-dry-run` job did not install PyYAML.** The planner contract
   test [`tests/test_release_dry_run_mode.py`](../tests/test_release_dry_run_mode.py)
   parses the workflow YAML (`import yaml`) to enforce the dry-run gating
   invariants. `actions/setup-python@v5.6.0` provides a clean interpreter,
   so the test failed with `ModuleNotFoundError: No module named 'yaml'` —
   masking the real invariants the test exists to enforce.

`RELEASE-WORKFLOW-DRYRUN-GATE-FIX-001` closes both gaps:

- `generate-matrix`, `build`, and `summary` are now gated to
  `if: github.event_name == 'release' || (github.event_name == 'workflow_dispatch'
  && !inputs.dry_run)`. A dispatch with `dry_run=true` therefore skips the
  matrix / build / summary jobs entirely and only exercises the
  `release-dry-run` job; a dispatch with `dry_run=false` still runs the
  build path (no Release is attached because the `release` job's gate is
  unchanged); a real `release` event runs the build matrix and the `release`
  job as before.
- The `release-dry-run` job installs `pyyaml` before running the planner
  contract tests, so `tests/test_release_dry_run_mode.py` now imports
  successfully in GitHub Actions.

**Publishing remains gated to a real release event** — the `release` job
still gates on `if: github.event_name == 'release'` only, the dry-run
input cannot reach `softprops/action-gh-release` (which still appears only
inside the `release` job), the dry-run job grants no `contents: write`, and
the FanRelay / FanPWM / FanDAC manual-candidate-only exclusion is unchanged.
The new gate invariants are locked in by `DryRunGatingTests` in
[`tests/test_release_dry_run_mode.py`](../tests/test_release_dry_run_mode.py).

---

## RELEASE-WORKFLOW-DRYRUN-RESULT-001 — recorded successful release dry-run (2026-05-28)

RELEASE-WORKFLOW-DRYRUN-RESULT-001 **ran and recorded** the first
**successful** manual dispatch of the `dry_run=true` lane added by
`RELEASE-WORKFLOW-DRYRUN-MODE-001` and isolated end-to-end by
`RELEASE-WORKFLOW-DRYRUN-GATE-FIX-001`. It is a **docs-only record**: it
publishes **no** GitHub Release, builds / attaches **no** firmware artifact,
writes **no** [`firmware/sources.json`](../firmware/sources.json) or
`manifest.json`, commits **no** `.bin` / checksum, edits **no**
`products/webflash/**`, and adds **no** fan `artifact_name` or
`webflash_build_matrix` flip.

### What was run

| Aspect | Value |
|---|---|
| Workflow run ID | [`26558999495`](https://github.com/sense360store/esphome-public/actions/runs/26558999495/job/78237206588) |
| Workflow | `Build & Release Firmware` ([`firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)) |
| Trigger | `workflow_dispatch` with `dry_run=true` |
| Branch | `main` |
| Predecessor merged | `RELEASE-WORKFLOW-DRYRUN-GATE-FIX-001` (PR #626, commit `776fb86`) merged as `2b4d214` |

### Job results

| Job | Result | Why |
|---|---|---|
| `Release Dry-Run (no publish)` | **success** | All four steps passed (see below) |
| `Generate Build Matrix` | **skipped** | Gated `release \|\| (workflow_dispatch && !inputs.dry_run)`; `dry_run=true` ⇒ skip |
| Per-product build jobs | **skipped** | Same gate (depend on `generate-matrix`) |
| `Build Summary` | **skipped** | Same gate |
| `Attach to Release` | **skipped** | Still gated `if: github.event_name == 'release'`; a dispatch can never reach it |

### Steps passed in `Release Dry-Run (no publish)`

| Step | Result |
|---|---|
| `Install dry-run test dependencies` | passed — installed `pyyaml` so the planner contract tests can `import yaml` (the gap closed by `RELEASE-WORKFLOW-DRYRUN-GATE-FIX-001`) |
| `Plan room release notes (dry-run, no publish)` | passed — `scripts/plan_room_release_notes.py --commit "${{ github.sha }}"` planned the two release-eligible builds, ran the release-notes validator against each draft body, and enforced the fan-exclusion guardrail; **wrote no file** |
| `Verify dry-run guardrails (planner contract tests)` | passed — `tests/test_plan_room_release_notes.py` + `tests/test_release_dry_run_mode.py` (the latter parses the workflow YAML to lock in the dry-run gate invariants) |
| `Assert no release side effects were produced` | passed — no `firmware/sources.json`, no `manifest.json`, and no root-level `*.bin` were produced |

### What the dispatch confirmed

- **The dry-run plans / validates the room release notes without publishing** —
  the `release-dry-run` job ran `scripts/plan_room_release_notes.py` for the
  two release-eligible builds and validated each draft body, with **no**
  `softprops/action-gh-release` step in the dry-run lane.
- **Build and release jobs are skipped under `dry_run=true`** — the
  `generate-matrix`, per-product `build`, `summary`, and `release`
  (`Attach to Release`) jobs were all skipped by their `if:` gates,
  proving the dry-run lane is isolated end-to-end as designed by
  `RELEASE-WORKFLOW-DRYRUN-GATE-FIX-001`.
- **It does not create a GitHub Release** — no Release was created,
  retitled, restamped, or modified; `softprops/action-gh-release` was
  not invoked anywhere in this run.
- **It does not build or attach release artifacts** — no `.bin`, no
  `checksums-sha256.txt`, no `checksums-md5.txt`, and no
  `manifest.json` were uploaded as Release assets.
- **It does not update [`firmware/sources.json`](../firmware/sources.json)
  or `manifest.json`** — the `Assert no release side effects were produced`
  step explicitly verifies this in CI; neither file is present in the repo.
- **It does not include FanRelay / FanPWM / FanDAC in the release lane** —
  the planner's fan-exclusion guardrail passed; FanRelay / FanPWM / FanDAC
  remain manual-candidate-only (`config/manual-firmware-artifacts.json`)
  and are listed under "Explicitly excluded — not release artifacts" in the
  plan. FanTRIAC remains blocked (HW-005).

### Local validation re-run (against the same commit)

| Command | Result |
|---|---|
| `python3 scripts/plan_room_release_notes.py` | OK — emitted a 2-build plan (no file written) |
| `python3 tests/test_plan_room_release_notes.py` | OK — 20 tests passed |
| `python3 tests/test_release_dry_run_mode.py` | OK — 17 tests passed (includes `DryRunGatingTests`) |
| `python3 tests/validate_configs.py` | OK — 208 files checked, 0 failed |
| `python3 scripts/validate_compile_targets.py --metadata-only` | OK — 12 compile-only targets, metadata valid |
| `python3 tests/validate_webflash_builds.py` | OK — 2 build entries checked, 0 failed |
| `python3 tests/test_workflow_permissions.py` | OK — 7 tests passed |
| `python3 -m unittest discover -s tests -p "test_*.py"` | OK — 888 tests, 3 skipped |

### Provenance

The workflow run ID, job URL, job/step pass-fail status, and skipped-job
list are the operator-supplied handoff (this session has no live Actions
API for this run); recorded as handed off, **not** fabricated. Local
validation against the same source-of-truth commit was re-run by this
session and is reported verbatim above.

---

## RELEASE-PRODUCT-SELECTION-001 — selectable release targets (2026-05-28)

RELEASE-PRODUCT-SELECTION-001 makes the release-notes / dry-run / release
workflows **operator-selectable** by the agreed room / product config rather
than silently scoping every dispatch to a single hardcoded target. It is a
behavior + ergonomics change for the workflow inputs and the planner /
generator; it publishes nothing.

### What the operator sees

| Workflow | Input | Type | Default | Options |
|---|---|---|---|---|
| [`release-notes-draft.yml`](../.github/workflows/release-notes-draft.yml) | `config_string` | `choice` | (none — must select) | `Ceiling-POE-VentIQ-RoomIQ`, `Ceiling-POE-VentIQ-RoomIQ-LED` |
| [`firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml) | `release_target` | `choice` | `all-release-eligible` | `all-release-eligible`, `Ceiling-POE-VentIQ-RoomIQ`, `Ceiling-POE-VentIQ-RoomIQ-LED` |

The picker options are **mirrored from**
[`config/webflash-builds.json`](../config/webflash-builds.json) — the same
single source of truth the release workflow's build matrix uses. Adding a
new release-eligible build to that file requires adding a matching option to
both pickers; the contract test
[`tests/test_release_product_selection.py`](../tests/test_release_product_selection.py)
fails fast if the picker and the release matrix drift apart.

FanRelay / FanPWM / FanDAC are **never** selectable as a release target —
they are manual-candidate-only
([`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json),
[`docs/manual-install-fan-candidates.md`](manual-install-fan-candidates.md))
and
[`scripts/list_release_targets.py`](../scripts/list_release_targets.py)
refuses to enumerate a fan token in the release matrix. FanTRIAC stays
blocked (HW-005).

### Where the selection flows

| Layer | Selection consumed by |
|---|---|
| Release-notes draft (`release-notes-draft.yml`) | Passes `config_string` straight to `scripts/generate_webflash_release_notes.py`, which already errors on an off-catalog config. |
| Dry-run lane (`firmware-build-release.yml` → `release-dry-run` job) | Validates the selection via `scripts/list_release_targets.py --validate`, then scopes [`scripts/plan_room_release_notes.py`](../scripts/plan_room_release_notes.py) with `--config-string`. `all-release-eligible` plans every release-eligible build (same behavior as before this PR). |
| Non-dry-run workflow_dispatch (`firmware-build-release.yml` → `generate-matrix`) | Filters the build matrix to the selected `config_string` when not `all-release-eligible`. A real `release` event ignores this input and continues to derive the matrix from the tag's `version` + `channel` only. |
| Real release event | **Unchanged.** Tag → `(version, channel)` mapping stays in [`scripts/derive_release_version_channel.py`](../scripts/derive_release_version_channel.py): plain `vX.Y.Z` is stable; `vX.Y.Z-led-preview` / `vX.Y.Z-preview` is preview. The matrix filter on `(version, channel)` then selects every matching row in `config/webflash-builds.json`. The `release_target` input does not (and cannot) reach the publish job. |

### Tag → product mapping (publish path)

For a real `release` event, product selection is implicit in the tag:

| Tag | `prerelease` | `(version, channel)` | Selects (from `config/webflash-builds.json`) |
|---|---|---|---|
| `v1.0.0` | `false` | `(1.0.0, stable)` | `Ceiling-POE-VentIQ-RoomIQ` |
| `v1.0.0-led-preview` | `true` | `(1.0.0, preview)` | `Ceiling-POE-VentIQ-RoomIQ-LED` |
| `v1.0.0-preview` | `true` | `(1.0.0, preview)` | `Ceiling-POE-VentIQ-RoomIQ-LED` |

A future LED stable release reuses the same `vX.Y.Z` shape on the stable
channel once the LED-bearing config is promoted; the matrix filter does
the product selection from `config/webflash-builds.json`, not from the
tag name.

### Generator wording is now product-aware

Two stale wording bugs surfaced once selection became operator-driven and
this PR fixes them in [`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py):

- The **LED Known-Issues bullet** previously read "Sense360 LED is not
  included in this Release-One firmware because the config string has no
  LED token." That implied there is only one fixed product. It is now
  product-aware: *"Sense360 LED is not included in this firmware: the
  selected configuration `<config_string>` does not include LED. The
  LED-bearing sibling lives on the preview channel."* For the LED preview
  it is still suppressed (LED moves to `## Features`).
- The **`## Changelog` TODO placeholder** previously read "TODO: Summarize
  user-visible changes for v1.0.0 …" — easy to mistake for finished notes.
  It is now operator-actionable and product-aware: *"TODO (operator
  changelog required): replace this bullet with the user-visible changes
  shipped in `<config_string>` `v<version>` (`<channel>`). One bullet per
  change. This placeholder must be replaced before the release notes are
  attached to a GitHub Release."* The structural validator still passes;
  the wording is unmistakably a publish blocker.

### What this PR does **not** do

- Publish any GitHub Release.
- Build, attach, commit, or upload any `.bin`, checksum, or build-info file.
- Write [`firmware/sources.json`](../firmware/sources.json) or `manifest.json`.
- Edit any `products/*` or `products/webflash/*` YAML.
- Add any FanRelay / FanPWM / FanDAC entry to
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  flip any fan `webflash_build_matrix`, or add any fan `artifact_name`.
- Promote FanRelay / FanPWM / FanDAC out of manual-candidate-only.
- Change the publish job's gate
  (`if: github.event_name == 'release'` is unchanged) or grant the
  dry-run lane any `contents: write`. `softprops/action-gh-release`
  still appears only inside the `release` job and the publish gate does
  not reference `release_target`.

### Tests added / updated

- [`tests/test_list_release_targets.py`](../tests/test_list_release_targets.py)
  — release-target enumeration / validation contract (16 tests).
- [`tests/test_release_product_selection.py`](../tests/test_release_product_selection.py)
  — workflow picker / planner-scope / generator-wording contract (22 tests).
- [`tests/test_plan_room_release_notes.py`](../tests/test_plan_room_release_notes.py)
  — unchanged; still passes with the new `--config-string` filter wired
  through `build_plan`.
- [`tests/test_release_dry_run_mode.py`](../tests/test_release_dry_run_mode.py)
  — unchanged; still passes with the new validate + planner-scope steps in
  the `release-dry-run` job.

---

## Cross-references

- Room firmware release inventory: [`docs/room-firmware-release-matrix.md`](room-firmware-release-matrix.md)
- Release-layer gate: [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
- Shipping configuration: [`docs/release-one.md`](release-one.md)
- Manual (non-release) fan install path: [`docs/manual-install-fan-candidates.md`](manual-install-fan-candidates.md)
- Manual artifact policy: `config/manual-firmware-artifacts.json` (MANUAL-FIRMWARE-ARTIFACT-POLICY-001)
- WebFlash release-body contract: [`docs/webflash-contract.md`](webflash-contract.md)
- Selectable release targets: [`scripts/list_release_targets.py`](../scripts/list_release_targets.py) (RELEASE-PRODUCT-SELECTION-001)

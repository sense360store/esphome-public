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

Tests: [`tests/test_plan_room_release_notes.py`](../tests/test_plan_room_release_notes.py)
(run with `python3 tests/test_plan_room_release_notes.py`).

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

---

## Cross-references

- Room firmware release inventory: [`docs/room-firmware-release-matrix.md`](room-firmware-release-matrix.md)
- Release-layer gate: [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
- Shipping configuration: [`docs/release-one.md`](release-one.md)
- Manual (non-release) fan install path: [`docs/manual-install-fan-candidates.md`](manual-install-fan-candidates.md)
- Manual artifact policy: `config/manual-firmware-artifacts.json` (MANUAL-FIRMWARE-ARTIFACT-POLICY-001)
- WebFlash release-body contract: [`docs/webflash-contract.md`](webflash-contract.md)

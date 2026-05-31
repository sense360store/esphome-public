# First-Release Publish-Readiness Assessment (FIRST-RELEASE-PUBLISH-READINESS-001)

**Canonical id:** `FIRST-RELEASE-PUBLISH-READINESS-001`
**Type:** Assessment / docs only. This document **publishes nothing, builds no
`.bin`, creates no GitHub Release, pushes no tag, promotes nothing, and verifies
no hardware.** It does **not** edit `manifest.json` / `firmware/sources.json`,
change [`config/webflash-builds.json`](../config/webflash-builds.json) or any
other `config/*.json`, add an `artifact_name`, flip `webflash_build_matrix`,
enable a new WebFlash target, touch the `sense360store/WebFlash` repo, mark
`S360-410` verified, mark LED stable, or mark any fan variant release-ready.

## Purpose

Assess whether the current first-release stable path is ready for a **real
publish**, now that the hosted GitHub Actions dry-run has passed
(`FIRST-RELEASE-WORKFLOW-DRYRUN-CI-RESULT-001`). The assessment walks the
publish-readiness checklist (human-reviewed changelog, real changelog text,
artifact naming, external-component pinning, hosted dry-run, WebFlash exposure,
checksums, WebFlash import handoff, rollback/abort criteria) and records a single
evidence-backed outcome.

### The one first-release-eligible stable path

Per [`docs/first-release-gates.md`](first-release-gates.md)
(`PRE-HW-PREP-FIRST-RELEASE-GATES-001`):

| Field | Value |
|---|---|
| **Bundle SKU** | `S360-KIT-BATH-P` (Bathroom) |
| **Config string** | `Ceiling-POE-VentIQ-RoomIQ` |
| **Channel** | `stable` |
| **Version** | `1.0.0` |
| **Expected artifact** | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` |
| **Chip family** | `ESP32-S3` |

---

## Outcome — **ALREADY PUBLISHED / NO ACTION REQUIRED**

> **The current first-release stable path is already published and live.** The
> GitHub Release **`v1.0.0`** for `sense360store/esphome-public` was published on
> **2026-05-12** (not a draft, not a prerelease) with the exact expected stable
> artifact, a **real human-authored changelog** (not a TODO/filler placeholder),
> checksums, and a build-info `manifest.json`; and it is already
> **imported/live in WebFlash** (`firmware/sources.json` + production
> `manifest.json` + per-artifact sidecar). There is **no pending publish action**
> for `v1.0.0`.
>
> Because the publish has already happened, **`FIRST-RELEASE-PUBLISH-001` is NOT
> opened** — see [§5](#5-decision-no-first-release-publish-001-is-opened). A new
> publish would only be warranted for a **new version** (e.g. `1.0.1` / `1.1.0`),
> which is out of scope for this assessment and is not requested.

This determination is grounded in the **live GitHub + WebFlash state**, not only
the working-branch docs. Several recent working docs describe the publish as
"still pending human review / future" (they were written around the *dry-run
rehearsal*); that framing is **stale** relative to the live release — see
[§4 Documentation reconciliation](#4-documentation-reconciliation-doc-drift).

---

## 1. Evidence — the live `v1.0.0` stable release

Queried live from `sense360store/esphome-public` Releases (GitHub API) during
this assessment:

| Field | Value |
|---|---|
| Release | **Sense360 Release-One Firmware v1.0.0** (id `321438349`) |
| Tag | **`v1.0.0`** → commit `0d0219bee8ada7fe9d891e3dc4a04662dcd76e28` (target `main`) |
| Published | **2026-05-12T21:22:44Z** |
| Draft / Prerelease | **`false` / `false`** (a real stable publish) |
| Release URL | <https://github.com/sense360store/esphome-public/releases/tag/v1.0.0> |
| Build run (real `release` event) | <https://github.com/sense360store/esphome-public/actions/runs/25763009641> (recorded in [`docs/webflash-release-proof.md`](webflash-release-proof.md), ESP-006/ESP-007) |

### 1.1 Attached assets (uploaded by `github-actions[bot]`, 2026-05-12T21:25:41Z)

| Asset | Size | SHA-256 (asset digest) |
|---|---|---|
| `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` | `1,087,488` B (≈ 1.04 MB) | `9169f2ce486d14d3c0e0b1d6e9adf558480db6ec301f8eac1622fda4d7ceffcc` |
| `checksums-sha256.txt` | `208` B | `c0602ecb0d5755aa3eaf81b7106d31ae568429b9e67c088f15d6c391a5a7aa11` |
| `checksums-md5.txt` | `138` B | — |
| `manifest.json` (build-info) | `382` B | `8ac33f38298b0568933a83d79d6f03faf9180c8e6c0431f4098b929311188e57` |

The artifact name is **byte-for-byte** the expected
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` and the size (≈1.04 MB) is
plausible for ESPHome firmware (well over the 100 KB floor the release/build
steps enforce).

### 1.2 Release body changelog — real, human-authored (NOT a placeholder)

The published `## Changelog` is genuine user-visible text, not the generator's
TODO placeholder and not `stable`-rejected filler:

- *"Production Release-One firmware for `Ceiling-POE-VentIQ-RoomIQ`."*
- *"Builds the no-TRIAC Release-One configuration while Sense360 TRIAC remains
  blocked pending hardware verification."*
- *"Excludes Sense360 LED because the WebFlash config string does not include
  `LED`."*

All four required H2 sections are present and non-empty (`## Changelog`,
`## Known Issues`, `## Features`, `## Hardware Requirements`), matching the
WebFlash release-body contract that
[`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py)
enforces at publish time.

### 1.3 LED preview release (separate, preview channel)

A separate **`v1.0.0-led-preview`** release (id `323244354`, commit
`4493e0c9…`) was published **2026-05-15T12:43:43Z** as a **prerelease**
(`prerelease: true`) carrying `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-…-preview`.
This is the expected, gated preview sibling (§7); it is **not** a stable publish
and changes nothing about the LED-preview gate.

### 1.4 WebFlash already has `v1.0.0` imported/live

Confirmed in `sense360store/WebFlash` (read-only):

- `firmware/sources.json` pins `release_tag: v1.0.0`, the release URL,
  `version: 1.0.0`, `channel: stable`, `config_string: Ceiling-POE-VentIQ-RoomIQ`,
  `asset_name: Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, the four
  required release-body sections, and `block_tokens: [FanTRIAC, LED]`.
- `manifest.json` + `firmware-0.json` carry the `Ceiling-POE-VentIQ-RoomIQ`
  config string.
- A per-artifact sidecar exists:
  `firmware/configurations/Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.meta.json`.

The artifact identity is consistent across **four** sources: the live GitHub
release asset, [`config/webflash-builds.json`](../config/webflash-builds.json),
[`config/product-catalog.json`](../config/product-catalog.json)
(`status: production`, `version: 1.0.0`, `channel: stable`,
`blocked_modules: [FanTRIAC, LED]`), and WebFlash `firmware/sources.json`.

---

## 2. Publish-readiness checklist (evaluated against the live release)

Every required gate, assessed against the **already-published** `v1.0.0`:

| # | Gate | Status | Evidence |
|---|---|---|---|
| 1 | Release notes human-reviewed (not TODO/filler) | ✅ **Met** | Live release body has real, human-authored bullets (§1.2); not the generator TODO placeholder, not `stable`-rejected filler. |
| 2 | Changelog is real user-visible text | ✅ **Met** | The three `## Changelog` bullets describe the actual Release-One firmware (§1.2). |
| 3 | Artifact naming matches expected pattern | ✅ **Met** | Asset is exactly `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` (§1.1), matching the contract pattern `Sense360-{config}-v{version}-{channel}.bin`. |
| 4 | External components / remote packages tag-pinned if required | ✅ **Met (effectively)** | The `release` build patches `packages/base/external_components.yaml` to **local checked-out source** (`type: local, path: ../components`), so the published `.bin` is built from the repo tree at the release commit — effectively pinned to the tag. The committed file keeps git `ref: main` **for remote-package consumers**; pinning that to a tag is an optional reproducibility nicety, not a publish blocker (see [§3](#3-residual-soft-items-not-blockers)). |
| 5 | Hosted dry-run passed | ✅ **Met** | `FIRST-RELEASE-WORKFLOW-DRYRUN-CI-RESULT-001` — hosted `Release Dry-Run (no publish)` passed ([run 26723839261](https://github.com/sense360store/esphome-public/actions/runs/26723839261/job/78755574773)). The real publish itself ran earlier on a `release` event ([run 25763009641](https://github.com/sense360store/esphome-public/actions/runs/25763009641)). |
| 6 | No unintended WebFlash exposure | ✅ **Met** | `config/webflash-builds.json` exposes exactly two builds — one `stable` (`Ceiling-POE-VentIQ-RoomIQ`) and one `preview` (`…-LED`); no fan driver, no other room bundle. Validated by `tests/validate_webflash_builds.py`. |
| 7 | Checksums expected at publish time | ✅ **Met** | `checksums-sha256.txt` + `checksums-md5.txt` are attached to the live release (§1.1); the build-info `manifest.json` is also attached. These are publish-time products and they exist. |
| 8 | WebFlash import handoff understood | ✅ **Met** | Handoff documented in [`docs/webflash-release-handoff.md`](webflash-release-handoff.md); WebFlash has imported `v1.0.0` (sources.json + manifest + sidecar, §1.4). |
| 9 | Rollback / no-publish abort criteria documented | ✅ **Met** | [`docs/first-release-dryrun-checklist.md`](first-release-dryrun-checklist.md) §8 + [`docs/webflash-release-handoff.md`](webflash-release-handoff.md) document the recovery path: delete the GitHub Release **and** its tag, re-run the WebFlash sync (WebFlash will not import an absent release). |

**All nine gates are satisfied by the live release.** Nothing in this checklist
is outstanding for `v1.0.0`.

---

## 3. Residual "soft" items (not blockers)

These do **not** block — `v1.0.0` is already published — and are recorded only
for a **future** version bump:

- **`external_components` git `ref: main`.** The committed
  `packages/base/external_components.yaml` uses `ref: main` for remote-package
  consumers. The published artifact is unaffected (the build patches it to local
  source, checklist #4). For a future tagged release, pinning this `ref` to the
  release tag would give remote-package consumers a reproducible pin. Optional.
- **`firmware/sources.json` does not live in `esphome-public`.** It is **owned by
  WebFlash** (`sense360store/WebFlash/firmware/sources.json`) and already records
  `v1.0.0` (§1.4). The `esphome-public` dry-run doc treats a repo-local
  `firmware/sources.json` as a "future" file; in practice the source-of-record is
  WebFlash-side and is present. No action.

---

## 4. Documentation reconciliation (doc drift)

There is a genuine, surface-level **contradiction** between the live state and a
cluster of recent working-branch docs, which a human should be aware of:

- **Live state (ground truth):** `v1.0.0` stable has been **published since
  2026-05-12** and is **live in WebFlash** (§1). [`docs/webflash-release-proof.md`](webflash-release-proof.md)
  already records this (ESP-006/ESP-007 "proven", release URL + run
  `25763009641`).
- **Stale framing:** [`docs/first-release-dryrun-checklist.md`](first-release-dryrun-checklist.md)
  (§6, §10, §11.8.4), [`docs/first-release-gates.md`](first-release-gates.md)
  (Headline dry-run callout), [`docs/sense360-roadmap-status.md`](sense360-roadmap-status.md)
  (§5.1/§5.2), and the `UPCOMING_PR.md` dry-run entries describe publishing as
  *"still a separate human decision / future"* and say *"no release / tag /
  `firmware/sources.json` exists."*

**Reconciliation:** those docs describe the **dry-run rehearsal** of the path and
were written as if the publish had not yet happened. The rehearsal is valid as a
rehearsal, but the path it rehearses **already shipped**. This is documentation
drift, not a defect in the release. This assessment does **not** rewrite those
docs (the task is readiness-assessment only and forbids touching gate state); the
drift is flagged here so a maintainer can decide whether to refresh the dry-run /
gates / roadmap wording to "published" in a follow-up docs PR.

---

## 5. Decision: no `FIRST-RELEASE-PUBLISH-001` is opened

The task says to create `FIRST-RELEASE-PUBLISH-001` **only if** the path is *ready
to publish*. It is **already published**, which is a terminal state, not a
"ready" state. Opening a publish item now would imply a publish still needs to
run against `v1.0.0` — that would risk a **double-publish / re-tag of an existing
live release**, which the hard guardrails explicitly forbid (no GitHub Release,
no tag, no `.bin`). Therefore:

- **`FIRST-RELEASE-PUBLISH-001` is intentionally NOT created.**
- The only legitimate future "publish" is a **new version** (`1.0.1` / `1.1.0`)
  with its own changelog and tag — out of scope here and not requested.

---

## 6. Validation

This PR adds this assessment doc plus an `UPCOMING_PR.md` entry; it changes no
config or code. The existing suite is unchanged and green:

- `python3 tests/validate_configs.py` — 213 files, 0 failed ✅
- `python3 tests/test_roadmap_status_doc.py` — 17 tests OK ✅
- `python3 tests/test_product_catalog.py` — 41 tests OK ✅
- `python3 tests/validate_webflash_builds.py` — 2 builds, 0 failed ✅
- `python3 -m unittest discover -s tests -p "test_*.py"` — 1177 tests OK (3 skipped) ✅

---

## 7. Guardrails (explicitly NOT changed)

This PR does **not**:

- publish firmware, create a GitHub Release, or push a tag;
- create or commit any `.bin` artifact or checksum file;
- change `firmware/sources.json` (WebFlash-owned) or `manifest.json`;
- change [`config/webflash-builds.json`](../config/webflash-builds.json) or any
  `config/*.json`;
- add an `artifact_name` or flip any `webflash_build_matrix` value;
- enable a new WebFlash target or touch the `sense360store/WebFlash` repo;
- promote any other bundle (`S360-KIT-KITCHEN-P` / `-LIVING-P` / `-BEDROOM-P` /
  `-CORRIDOR-P` stay candidates; no `current_release_status` change);
- mark `S360-410` verified (stays `cataloged_unverified`; PoE caveat preserved);
- mark LED (`S360-300`) stable (LED firmware stays `preview`);
- mark any fan variant (`S360-310` / `-311` / `-312` / `-320`) release-ready;
- claim, run, or fabricate any bench / hardware evidence.

No `config/*.json`, `packages/**`, or `products/**` file is edited.

---

## 8. Cross-references

- First-release / expansion gates:
  [`docs/first-release-gates.md`](first-release-gates.md) —
  `PRE-HW-PREP-FIRST-RELEASE-GATES-001`.
- Operator dry-run checklist (incl. publish-readiness checklist):
  [`docs/first-release-dryrun-checklist.md`](first-release-dryrun-checklist.md) —
  `FIRST-RELEASE-DRYRUN-CHECKLIST-001` (hosted pass: §11.8,
  `FIRST-RELEASE-WORKFLOW-DRYRUN-CI-RESULT-001`).
- Roadmap / status / blocker view:
  [`docs/sense360-roadmap-status.md`](sense360-roadmap-status.md) —
  `DOCS-CONSOLIDATION-ROADMAP-001`.
- Repo-side release proof (records the live `v1.0.0`):
  [`docs/webflash-release-proof.md`](webflash-release-proof.md) — ESP-006/ESP-007.
- Operational WebFlash handoff + rollback:
  [`docs/webflash-release-handoff.md`](webflash-release-handoff.md).
- Shippable builds / contract:
  [`config/webflash-builds.json`](../config/webflash-builds.json) ·
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json).
- Build & release workflow (publish gating + dry-run mode):
  [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml).

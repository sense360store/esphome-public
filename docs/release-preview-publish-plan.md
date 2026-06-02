# Preview WebFlash artifact publish plan — pre-run record

**Canonical id:** `RELEASE-PREVIEW-PUBLISH-PLAN-001`
**Date:** 2026-06-02
**Type:** Plans the actual publication of the three **metadata-ready** preview
WebFlash build rows before the firmware release workflow is run. This PR
**verifies inputs, artifact names, release-note drafts, compile evidence,
commercial posture, and workflow scope** and **queues** the actual run as
`RELEASE-PREVIEW-PUBLISH-RUN-001`. It is **planning only**: it **publishes no
firmware**, runs **no** release workflow, creates **no** GitHub Release / tag /
checksum, commits **no** `.bin`, writes **no** `manifest.json` /
`firmware/sources.json`, touches **no** WebFlash repo, marks **nothing** stable,
makes **no** preview build recommended / default, exposes **no** candidate
bundle as buyable, adds **no** TRIAC row, adds **no** fan manual-preview row,
changes the launch SKU away from **`S360-KIT-BATH-P`** **not at all**, and
claims **no** hardware / bench / compliance / commercial-availability proof.

**Predecessors:**

- `#695` `RELEASE-PREVIEW-COMPILE-RESULTS-001` recorded hosted compile run
  [`26821900127`](https://github.com/sense360store/esphome-public/actions/runs/26821900127)
  as GREEN firmware-build proof for the preview matrix.
- `#696` `RELEASE-PREVIEW-WEBFLASH-WRAPPERS-001` added the three
  `products/webflash` wrappers.
- `#697` `SHOP-COMMERCIAL-SOURCE-OF-TRUTH-001` locked the launch SKU
  `S360-KIT-BATH-P` and the candidate-bundle hidden / not-buyable posture.
- `#698` `RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001` added the three reviewed
  **preview** rows to
  [`config/webflash-builds.json`](../config/webflash-builds.json)
  ([`docs/release-preview-webflash-build-rows.md`](release-preview-webflash-build-rows.md)).
- `#699` `RELEASE-PREVIEW-RELEASE-NOTES-DRYRUN-001` generated and validated the
  three preview release-note drafts under
  [`docs/release-notes/preview/`](release-notes/preview/)
  ([`docs/release-preview-webflash-release-notes-dryrun.md`](release-preview-webflash-release-notes-dryrun.md)).

---

## TL;DR

* **Scope is exactly three preview artifacts** — `Ceiling-POE-AirIQ-RoomIQ`,
  `Ceiling-POE-RoomIQ`, and `Ceiling-POE-RoomIQ-LED` — the three
  `release_state: metadata-ready-unpublished` rows in
  [`config/webflash-builds.json`](../config/webflash-builds.json). Each is
  preview-channel, build-row-backed, release-note-drafted, and
  compile-validated by run `26821900127`.
* **Everything the run needs already exists and is verified here:** the build
  rows, the `products/webflash` wrappers, the validated release-note drafts, the
  compile evidence, the hidden / candidate / not-buyable commercial posture, and
  the workflow pickers that can scope to exactly one of the three.
* **The run is *not* in this PR.** It is queued as
  `RELEASE-PREVIEW-PUBLISH-RUN-001`. This PR produces **no** firmware binary,
  GitHub Release, tag, `manifest.json`, or `firmware/sources.json`, and touches
  **no** WebFlash repo.
* **Out of scope and verified absent from the publish set:** the stable Bathroom
  PoE build (`Ceiling-POE-VentIQ-RoomIQ` — production / simple-install, only
  published when `channel: stable` is explicitly selected), TRIAC
  (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`, `HW-005`), and the fan manual-preview
  targets (`FanRelay` / `FanPWM` / `FanDAC`, which live on the manual lane, never
  in `config/webflash-builds.json`).
* **WebFlash import comes *after* upstream artifacts exist** — the
  WebFlash-side one-click import is a strictly later, separately gated follow-up
  that only begins once these preview artifacts are published upstream.

---

## 1. The three preview artifacts

Each row is published exactly as declared in
[`config/webflash-builds.json`](../config/webflash-builds.json) (the **sole**
release-eligibility source of truth). Nothing below is hand-set: the publish
plan reads from the build rows, the catalog, the preview-target manifest, the
release-note drafts, and the workflow pickers.

### 1.1 `Sense360-Ceiling-POE-AirIQ-RoomIQ-v1.0.0-preview.bin`

| Field | Value |
|---|---|
| Config string | `Ceiling-POE-AirIQ-RoomIQ` |
| WebFlash build row | [`config/webflash-builds.json`](../config/webflash-builds.json) → `builds[]` `Ceiling-POE-AirIQ-RoomIQ` (`channel: preview`, `version: 1.0.0`, `release_state: metadata-ready-unpublished`) |
| Product YAML / wrapper | `products/webflash/ceiling-poe-airiq-roomiq.yaml` (canonical `products/sense360-ceiling-poe-airiq-roomiq.yaml`) |
| Release-note draft | [`docs/release-notes/preview/ceiling-poe-airiq-roomiq.md`](release-notes/preview/ceiling-poe-airiq-roomiq.md) (validated `--channel preview`) |
| Compile evidence | run `26821900127` (`Preview Compile Dry-Run`, `workflow_dispatch` / `compile_mode=full`, 2026-06-02, ESPHome 2026.4.5; job `Compile Dry-Run: Ceiling-POE-AirIQ-RoomIQ`, result `success`, `proof_class: firmware-build-only`) |
| Commercial posture | **hidden / candidate / not buyable** (consuming bundle `S360-KIT-KITCHEN-P`); not recommended; not customer default; not stable |
| Channel | `preview` |
| Stable / recommended / default | **not stable, not recommended, not a customer default** |
| Hardware / compliance proof | **none claimed** — firmware-build proof only; stable stays blocked by S360-410 PoE-PSU schematic verification (`PRODUCT-POE-410-001` / `PACKAGE-POE-410-001`) + AirIQ sensor-stack bench evidence |
| Expected workflow selector | `release_target: Ceiling-POE-AirIQ-RoomIQ` · `channel: preview` · `version: 1.0.0` (release-notes-draft picker: `config_string: Ceiling-POE-AirIQ-RoomIQ`; build matrix `product` stem: `ceiling-poe-airiq-roomiq`) |
| Expected output file name | `Sense360-Ceiling-POE-AirIQ-RoomIQ-v1.0.0-preview.bin` |

### 1.2 `Sense360-Ceiling-POE-RoomIQ-v1.0.0-preview.bin`

| Field | Value |
|---|---|
| Config string | `Ceiling-POE-RoomIQ` |
| WebFlash build row | [`config/webflash-builds.json`](../config/webflash-builds.json) → `builds[]` `Ceiling-POE-RoomIQ` (`channel: preview`, `version: 1.0.0`, `release_state: metadata-ready-unpublished`) |
| Product YAML / wrapper | `products/webflash/ceiling-poe-roomiq.yaml` (canonical `products/sense360-ceiling-poe-roomiq.yaml`) |
| Release-note draft | [`docs/release-notes/preview/ceiling-poe-roomiq.md`](release-notes/preview/ceiling-poe-roomiq.md) (validated `--channel preview`) |
| Compile evidence | run `26821900127` (`Preview Compile Dry-Run`, `compile_mode=full`, 2026-06-02, ESPHome 2026.4.5; job `Compile Dry-Run: Ceiling-POE-RoomIQ`, result `success`, `proof_class: firmware-build-only`) |
| Commercial posture | **hidden / candidate / not buyable** (consuming bundle `S360-KIT-BEDROOM-P`); not recommended; not customer default; not stable |
| Channel | `preview` |
| Stable / recommended / default | **not stable, not recommended, not a customer default** |
| Hardware / compliance proof | **none claimed** — firmware-build proof only; stable stays blocked by S360-410 PoE-PSU schematic verification (`PRODUCT-POE-410-001` / `PACKAGE-POE-410-001`) |
| Expected workflow selector | `release_target: Ceiling-POE-RoomIQ` · `channel: preview` · `version: 1.0.0` (release-notes-draft picker: `config_string: Ceiling-POE-RoomIQ`; build matrix `product` stem: `ceiling-poe-roomiq`) |
| Expected output file name | `Sense360-Ceiling-POE-RoomIQ-v1.0.0-preview.bin` |

### 1.3 `Sense360-Ceiling-POE-RoomIQ-LED-v1.0.0-preview.bin`

| Field | Value |
|---|---|
| Config string | `Ceiling-POE-RoomIQ-LED` |
| WebFlash build row | [`config/webflash-builds.json`](../config/webflash-builds.json) → `builds[]` `Ceiling-POE-RoomIQ-LED` (`channel: preview`, `version: 1.0.0`, `release_state: metadata-ready-unpublished`) |
| Product YAML / wrapper | `products/webflash/ceiling-poe-roomiq-led.yaml` (canonical `products/sense360-ceiling-poe-roomiq-led.yaml`) |
| Release-note draft | [`docs/release-notes/preview/ceiling-poe-roomiq-led.md`](release-notes/preview/ceiling-poe-roomiq-led.md) (validated `--channel preview`) |
| Compile evidence | run `26821900127` (`Preview Compile Dry-Run`, `compile_mode=full`, 2026-06-02, ESPHome 2026.4.5; job `Compile Dry-Run: Ceiling-POE-RoomIQ-LED`, result `success`, `proof_class: firmware-build-only`) |
| Commercial posture | **hidden / candidate / not buyable** (consuming bundles `S360-KIT-LIVING-P`, `S360-KIT-CORRIDOR-P`); not recommended; not customer default; not stable |
| Channel | `preview` |
| Stable / recommended / default | **not stable, not recommended, not a customer default**; LED stays preview and never auto-promotes |
| Hardware / compliance proof | **none claimed** — firmware-build proof only; stable stays blocked by S360-410 PoE-PSU schematic verification (`PRODUCT-POE-410-001` / `PACKAGE-POE-410-001`) + the LED preview-to-stable gauntlet |
| Expected workflow selector | `release_target: Ceiling-POE-RoomIQ-LED` · `channel: preview` · `version: 1.0.0` (release-notes-draft picker: `config_string: Ceiling-POE-RoomIQ-LED`; build matrix `product` stem: `ceiling-poe-roomiq-led`) |
| Expected output file name | `Sense360-Ceiling-POE-RoomIQ-LED-v1.0.0-preview.bin` |

> `Ceiling-POE-RoomIQ-LED` is the **RoomIQ + LED** sibling shared by the
> Living-room and Corridor bundles. It is **distinct** from the
> already-published VentIQ LED preview `Ceiling-POE-VentIQ-RoomIQ-LED`
> (tag `v1.0.0-led-preview`), which this plan does **not** re-publish or change.

Artifact names follow the contract pattern
`Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin` and round-trip through
[`scripts/product_name_mapper.py`](../scripts/product_name_mapper.py); the
build-time `Assert renamed binary matches WebFlash build matrix` step
([`tests/check_webflash_build_output.py`](../tests/check_webflash_build_output.py))
fails the build if a produced filename disagrees with the declared
`artifact_name`.

---

## 2. Workflow scope verification

The release / build workflow
([`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml))
generates its build matrix **exclusively** from
`config/webflash-builds.json`, filtered by `version` + `channel` (and, on a
`workflow_dispatch`, optionally scoped to a single `release_target`). The
release-eligible target picker is mirrored in both the build/release workflow
(`release_target`) and the release-notes-draft workflow
([`.github/workflows/release-notes-draft.yml`](../.github/workflows/release-notes-draft.yml),
`config_string`), and locked in lock-step with the build matrix by
[`tests/test_release_product_selection.py`](../tests/test_release_product_selection.py).

The scope claims below were verified by replaying the matrix-generation filter
against the live `config/webflash-builds.json`:

| Claim | Result |
|---|---|
| The workflow can select **exactly** each of the three preview configs | ✅ `release_target=Ceiling-POE-AirIQ-RoomIQ` → matrix `[Ceiling-POE-AirIQ-RoomIQ]`; `Ceiling-POE-RoomIQ` → `[Ceiling-POE-RoomIQ]`; `Ceiling-POE-RoomIQ-LED` → `[Ceiling-POE-RoomIQ-LED]`. Each also validates via `scripts/list_release_targets.py --validate`. |
| The workflow does **not** include the stable Bathroom build unless explicitly selected | ✅ `Ceiling-POE-VentIQ-RoomIQ` is `channel: stable`; a `channel: preview` run never includes it. It is only built when `channel: stable` (or `release_target=Ceiling-POE-VentIQ-RoomIQ` on a stable run) is explicitly chosen. |
| The workflow does **not** include TRIAC | ✅ `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` is **not** in `config/webflash-builds.json` and **not** in either picker (`HW-005`). |
| The workflow does **not** include fan manual-preview targets | ✅ `FanRelay` / `FanPWM` / `FanDAC` are manual-lane only (`config/manual-firmware-artifacts.json`), excluded from `config/webflash-builds.json` and both pickers, and rejected by `scripts/list_release_targets.py --validate` (exit 2). |
| The workflow does **not** update the WebFlash repo | ✅ It attaches assets to a GitHub Release in this repo only; no job writes to `sense360store/WebFlash`, `manifest.json`, or `firmware/sources.json`. |

### 2.1 Scoping note for the run (decision for `RELEASE-PREVIEW-PUBLISH-RUN-001`)

Two facts shape *how* the run is dispatched, and the run PR must choose
deliberately:

1. **Single-config scoping exists only on `workflow_dispatch`.** The
   `release_target` picker is a `workflow_dispatch` input and is ignored on a
   real `release` event (see the matrix step's `EVENT_NAME` guard). A
   `workflow_dispatch` with `dry_run=false` builds the scoped target and
   uploads it as a **CI artifact** (7-day retention) — it does **not** create a
   GitHub Release (the `release` job is gated on
   `github.event_name == 'release'`).
2. **Publication (Release assets) is `version` + `channel` scoped.** On a real
   `release` event, the tag normalises to `(version, channel)` via
   [`scripts/derive_release_version_channel.py`](../scripts/derive_release_version_channel.py)
   and the matrix builds **every** `config/webflash-builds.json` row at that
   `version` + `channel`. A `v1.0.0-preview` prerelease therefore resolves to
   `version=1.0.0, channel=preview`, whose matrix is **all four** preview rows —
   the three planned here **plus** the already-published VentIQ LED preview
   `Ceiling-POE-VentIQ-RoomIQ-LED`.

So the run PR must pick its publish vehicle with eyes open — e.g. accept that a
single `v1.0.0-preview` prerelease re-attaches the (byte-identical) VentIQ LED
preview alongside the three new artifacts, or scope publication another way.
**This plan does not decide that** (planning only); it records the constraint so
the run is scoped correctly. What is *fixed* is the per-artifact selector and
output filename in §1, the channel (`preview`), the version (`1.0.0`), and the
fact that the stable Bathroom build, TRIAC, and the fan manual-preview targets
stay **out** of the preview publish set.

---

## 3. What is proven (and what is not)

* **Proven (firmware-build only):** the canonical product YAML for each of the
  three targets compiled GREEN on hosted CI in Preview Compile Dry-Run run
  [`26821900127`](https://github.com/sense360store/esphome-public/actions/runs/26821900127)
  (2026-06-02, ESPHome 2026.4.5), each release-note draft validates structurally
  against the WebFlash release-body contract (`--channel preview`), and the
  release / release-notes pickers can scope to exactly these three configs.
* **Not proven / not claimed:** hardware operation, bench verification, a
  verified schematic, electrical / mains-safety / EMC compliance, commercial
  availability, or any stable-promotion readiness. Stable stays gated by
  `PRODUCT-POE-410-001` (S360-410 PoE-PSU schematic verification), plus AirIQ
  sensor-stack bench evidence for the Kitchen firmware and the LED
  preview-to-stable gauntlet for the RoomIQ-LED firmware. A validated plan is
  **not** a published artifact.

---

## 4. Queued follow-up — `RELEASE-PREVIEW-PUBLISH-RUN-001`

The actual manual workflow run is the **next** queue item, not this PR. When it
runs, it will (per the selectors in §1 and the scoping note in §2.1):

1. Publish the three preview artifacts named in §1, on `channel: preview`,
   `version: 1.0.0`, each backed by its build row + wrapper + validated
   release-note draft + compile evidence.
2. Keep the stable Bathroom PoE build, TRIAC, and the fan manual-preview
   targets **out** of the preview publish set.
3. Keep the consuming candidate bundles (`S360-KIT-KITCHEN-P`,
   `S360-KIT-BEDROOM-P`, `S360-KIT-LIVING-P`, `S360-KIT-CORRIDOR-P`)
   **hidden / not buyable** and the launch SKU **`S360-KIT-BATH-P`** unchanged.

**WebFlash import comes after upstream artifacts exist.** The WebFlash-side
one-click import (a `config/webflash-builds.json` row + `products/webflash`
wrapper on the WebFlash repo, behind its acknowledgement gate) is a strictly
later, separately gated follow-up
(`WEBFLASH-PREVIEW-IMPORT-HANDOFF-001`) that only begins once
`RELEASE-PREVIEW-PUBLISH-RUN-001` has actually published these preview
artifacts. No WebFlash change happens before then.

---

## 5. Guardrails — what this PR did and did NOT do

It did **not**: publish firmware; run the release workflow; create a GitHub
Release / tag / checksum; commit any `.bin`; write `manifest.json` or
`firmware/sources.json`; touch the WebFlash repo; flip anything to
`production` / `stable`; mark any candidate bundle buyable; make any preview row
recommended / default; change the launch SKU away from `S360-KIT-BATH-P`; add a
TRIAC row (FanTRIAC stays `advanced-manual-preview`, blocked by `HW-005`); add a
fan manual-preview row (FanRelay / FanPWM / FanDAC stay on the `manual-preview`
lane, off the WebFlash build matrix); or claim hardware / bench / compliance /
commercial-availability proof. It edits only this plan doc, the new test, and
`UPCOMING_PR.md`.

---

## 6. Validation

All commands run from the repo root and pass:

| Command | Result |
|---|---|
| `python3 tests/validate_configs.py` | `✅ All configuration files are valid!` |
| `python3 scripts/validate_compile_targets.py --metadata-only` | `✅ Metadata validation passed.` |
| `python3 scripts/validate_preview_release_targets.py --metadata-only` | `✅ … validation passed.` (9 targets) |
| `python3 tests/test_product_catalog.py` | `OK` |
| `python3 tests/validate_webflash_builds.py` | `✅ All WebFlash build entries are valid!` (5 builds) |
| `python3 tests/test_shop_commercial_source_of_truth.py` | `OK` |
| `python3 tests/test_preview_release_notes_drafts.py` | `OK` |
| `python3 tests/test_preview_publish_plan.py` | `OK` (this PR's guard) |
| `for f in docs/release-notes/preview/ceiling-poe-*.md; do python3 scripts/validate-webflash-release-notes.py --channel preview "$f"; done` | `validation passed (channel=preview)` (each of the 3 drafts) |
| `python3 -m unittest discover -s tests -p "test_*.py"` | `OK` |

---

## Cross-references

- Preview WebFlash build rows: [`docs/release-preview-webflash-build-rows.md`](release-preview-webflash-build-rows.md)
- Preview release-note drafts (dry-run): [`docs/release-preview-webflash-release-notes-dryrun.md`](release-preview-webflash-release-notes-dryrun.md) · [`docs/release-notes/preview/`](release-notes/preview/)
- Preview WebFlash wrappers: [`docs/release-preview-webflash-wrappers.md`](release-preview-webflash-wrappers.md)
- Compile dry-run record: [`docs/release-preview-compile-dryrun.md`](release-preview-compile-dryrun.md)
- Release-eligibility source of truth: [`config/webflash-builds.json`](../config/webflash-builds.json)
- Preview target manifest: [`config/preview-release-targets.json`](../config/preview-release-targets.json)
- Release / build workflow: [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)
- Release-notes draft workflow: [`.github/workflows/release-notes-draft.yml`](../.github/workflows/release-notes-draft.yml)
- Release-target picker helper: [`scripts/list_release_targets.py`](../scripts/list_release_targets.py)
- Artifact-name mapper: [`scripts/product_name_mapper.py`](../scripts/product_name_mapper.py)
- Release-body validator: [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py)
- Commercial source of truth: [`docs/shop-commercial-source-of-truth.md`](shop-commercial-source-of-truth.md)
- Release matrix / WebFlash alignment: [`docs/release-matrix-webflash-alignment.md`](release-matrix-webflash-alignment.md)
- Canonical roadmap / status: [`docs/sense360-roadmap-status.md`](sense360-roadmap-status.md)

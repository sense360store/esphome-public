# Preview WebFlash artifact publish — recorded successful run

**Canonical id:** `RELEASE-PREVIEW-PUBLISH-RESULTS-001`
**Date:** 2026-06-02
**Type:** Records the **successful** `Build & Release Firmware` workflow run that
published the preview firmware artifacts to the GitHub Release `v1.0.0-preview`,
including the **four** preview `.bin` artifacts built and attached. This is
**documentation / config-evidence only** — it records an already-completed run.
It **does not** re-run the release workflow, create another release, build or
commit any `.bin`, write `manifest.json` / `firmware/sources.json`, touch the
WebFlash repo, promote anything to stable, make any preview build recommended /
default, expose any candidate bundle as buyable, add a TRIAC row, add a fan
manual-preview row, change the launch SKU away from **`S360-KIT-BATH-P`**, or
claim any hardware / bench / compliance / commercial-availability proof.

**Predecessors:**

- `#695` `RELEASE-PREVIEW-COMPILE-RESULTS-001` recorded the hosted compile run
  [`26821900127`](https://github.com/sense360store/esphome-public/actions/runs/26821900127)
  as GREEN firmware-build proof for the preview matrix.
- `#698` `RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001` added the three reviewed
  **preview** rows to
  [`config/webflash-builds.json`](../config/webflash-builds.json).
- `#699` `RELEASE-PREVIEW-RELEASE-NOTES-DRYRUN-001` generated + validated the
  three preview release-note drafts under
  [`docs/release-notes/preview/`](release-notes/preview/).
- `#700` `RELEASE-PREVIEW-PUBLISH-PLAN-001` verified the publish inputs / scope
  and queued the run as `RELEASE-PREVIEW-PUBLISH-RUN-001`
  ([`docs/release-preview-publish-plan.md`](release-preview-publish-plan.md)).
- `RELEASE-PREVIEW-PUBLISH-RUN-001` is the run this document records as **done /
  success**.

---

## TL;DR

* **The preview publish run is DONE and GREEN.** The `Build & Release Firmware`
  workflow ran on the **`release` event** (not a manual dispatch) for the
  published prerelease `v1.0.0-preview` —
  [run `26847702410`](https://github.com/sense360store/esphome-public/actions/runs/26847702410)
  (2026-06-02) — and finished with **conclusion `success`**.
* **Four preview artifacts were built and attached.** Because a `release` event
  ignores the `workflow_dispatch`-only `release_target` picker and builds **every**
  `config/webflash-builds.json` row matching the tag's `(version=1.0.0,
  channel=preview)`, the matrix resolved to **all four** preview rows — the three
  new room-bundle previews **plus** the already-published VentIQ LED preview
  sibling (re-built and re-attached on this tag).
* **Every gate passed before upload.** `Attach to Release` ran release-notes
  validation and the WebFlash release-asset check, then uploaded the assets — all
  `success`. The release carries the four `.bin` files plus
  `checksums-sha256.txt`, `checksums-md5.txt`, and a build-info `manifest.json`.
* **Posture is unchanged.** All four artifacts are **preview** — not stable, not
  recommended, not a customer default; the consuming candidate bundles stay
  **hidden / not buyable**; the **stable Bathroom PoE release**
  (`S360-KIT-BATH-P` / `Ceiling-POE-VentIQ-RoomIQ`) remains the only
  customer-default **production** release. **No** hardware / bench / compliance /
  commercial-availability proof is claimed — this is **firmware-build / release
  proof only**.
* **Records, does not republish.** This PR edits only this doc, its guard test,
  and `UPCOMING_PR.md`. No firmware is built, no `.bin` is committed, no
  `config/webflash-builds.json` / `manifest.json` / `firmware/sources.json` is
  written, and the WebFlash repo is untouched.

---

## 1. The publish run (evidence)

| Field | Value |
|---|---|
| Workflow name | **`Build & Release Firmware`** ([`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)) |
| Run id | **`26847702410`** (run #43, attempt 1) |
| Run URL | <https://github.com/sense360store/esphome-public/actions/runs/26847702410> |
| Event | **`release`** (`release.published`) — **not** `workflow_dispatch` / manual dispatch |
| Display title | `Sense360 Preview Firmware v1.0.0` |
| Triggered by | `sense360store` |
| Tag / head branch | `v1.0.0-preview` |
| Commit (`head_sha`) | `2228bbb785a8d5b214d92cae08d1c760ba36ec47` (merge of #700, `RELEASE-PREVIEW-PUBLISH-PLAN-001`) |
| Derived `(version, channel)` | `version=1.0.0`, `channel=preview` (from `prerelease: true` + tag normalisation via [`scripts/derive_release_version_channel.py`](../scripts/derive_release_version_channel.py)) |
| Started → finished | 2026-06-02 20:59:35Z → 21:04:40Z (≈5m) |
| Build count (`product_count`) | **4** preview artifacts |
| Conclusion | **`success`** |

---

## 2. The GitHub Release

| Field | Value |
|---|---|
| Release tag | **`v1.0.0-preview`** |
| Release name | `Sense360 Preview Firmware v1.0.0` |
| Release URL | <https://github.com/sense360store/esphome-public/releases/tag/v1.0.0-preview> |
| Prerelease | **`true`** (drives `channel=preview`); `draft: false` |
| Target | `main` |
| Published | 2026-06-02 20:59:32Z |
| Release-body validation | **passed** (four required H2 sections present + non-empty: `## Changelog`, `## Known Issues`, `## Features`, `## Hardware Requirements`) |

The release body states the preview posture in plain words (preview firmware for
testers only; not stable; not recommended; not a customer default; not hardware
verified; not a public shop product), cites firmware-build compile run
`26821900127`, and points normal customers at the stable Bathroom PoE release
(`S360-KIT-BATH-P` / `Ceiling-POE-VentIQ-RoomIQ`).

---

## 3. The four published preview artifacts

Every artifact is `channel: preview`, `version: 1.0.0`, and is backed by its
`config/webflash-builds.json` build row. Sizes and SHA256 values below are the
**recorded** GitHub Release asset values (the asset digest, matching the uploaded
`checksums-sha256.txt`); each is well above the 100 KB floor enforced by
[`scripts/check-webflash-release-assets.py`](../scripts/check-webflash-release-assets.py).

| # | Config string | Artifact (preview `.bin`) | Size (bytes) | SHA256 |
|---|---|---|---|---|
| 1 | `Ceiling-POE-AirIQ-RoomIQ` | `Sense360-Ceiling-POE-AirIQ-RoomIQ-v1.0.0-preview.bin` | 1,089,296 | `16565de6cd8b62c51d4fa8041eb5ffdb29fd2b8daddceecd73a6b0df5d722bc7` |
| 2 | `Ceiling-POE-RoomIQ` | `Sense360-Ceiling-POE-RoomIQ-v1.0.0-preview.bin` | 956,976 | `2c7d691c70a557d8df4ef2ba58a6dc43195b952b6c209c89d5522a392f47b937` |
| 3 | `Ceiling-POE-RoomIQ-LED` | `Sense360-Ceiling-POE-RoomIQ-LED-v1.0.0-preview.bin` | 1,006,848 | `d4f18824466e95ba091dfd80e8159d544613e4c28f70f03ba81e9c8a676c9cb0` |
| 4 | `Ceiling-POE-VentIQ-RoomIQ-LED` | `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` | 1,027,744 | `9e513b47b7b7b76024e426bb8a5562785ed1667229211a523645d2f8e33cdae2` |

Supporting assets attached to the same release (uploaded by `Attach to Release`):

| Asset | Size (bytes) | Notes |
|---|---|---|
| `checksums-sha256.txt` | 563 | SHA256 of each `.bin` |
| `checksums-md5.txt` | 396 | MD5 of each `.bin` (compatibility) |
| `manifest.json` | 874 | **build-info** manifest (per-file SHA256 / size, build date, git SHA, ESPHome version, `product_count: 4`) — **not** the WebFlash production-signed manifest |

> **Artifact #4 is a fresh rebuild, distinct from the `v1.0.0-led-preview`
> release.** `Ceiling-POE-VentIQ-RoomIQ-LED` was previously published on its own
> dedicated tag [`v1.0.0-led-preview`](https://github.com/sense360store/esphome-public/releases/tag/v1.0.0-led-preview)
> (run `25918422743`, asset 1,135,904 bytes, SHA256
> `93310d2cbc27355e399f36a232336b6b9075dacfc178d603c7a92aa1089182d3`). Because it
> matches `(version=1.0.0, channel=preview)`, it was **re-built and re-attached**
> on `v1.0.0-preview` as an independent build artifact (different size + SHA256,
> as expected for a separate compile); the dedicated `v1.0.0-led-preview` release
> and its recorded proof in [`docs/webflash-release-proof.md`](webflash-release-proof.md)
> are **unchanged**.

---

## 4. Why there are four artifacts (release-event scope)

The number of artifacts is a direct, expected consequence of how the release
workflow generates its matrix on a **`release` event** — exactly the constraint
the publish plan recorded in advance (`RELEASE-PREVIEW-PUBLISH-PLAN-001` §2.1):

1. **The `release_target` picker is `workflow_dispatch`-only and is ignored on a
   `release` event.** In the matrix step of
   [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml),
   `release_target` is forced empty when `event_name != "workflow_dispatch"`, so
   single-config scoping is **not available** on a real release. (Single-config
   scoping only ever produced a 7-day CI artifact on a `workflow_dispatch`; it
   never creates a Release.)
2. **Publication is `(version, channel)` scoped.** The tag `v1.0.0-preview`
   normalises to `version=1.0.0`, `channel=preview`, and the matrix builds
   **every** `config/webflash-builds.json` row at that `version` + `channel`.
3. **There are exactly four such rows.** Filtering
   [`config/webflash-builds.json`](../config/webflash-builds.json) by
   `version=1.0.0` **and** `channel=preview` yields the four preview builds —
   `Ceiling-POE-AirIQ-RoomIQ`, `Ceiling-POE-RoomIQ`, `Ceiling-POE-RoomIQ-LED`,
   and the already-published `Ceiling-POE-VentIQ-RoomIQ-LED`. The fifth row,
   `Ceiling-POE-VentIQ-RoomIQ`, is `channel: stable` and is therefore **not** in
   a preview matrix.

So all preview WebFlash build rows for `v1.0.0` were published. The
`Ceiling-POE-VentIQ-RoomIQ` **stable** Bathroom build, **TRIAC**
(`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`, `HW-005`), and the fan **manual-preview**
targets (`FanRelay` / `FanPWM` / `FanDAC`, manual-lane only) stayed **out** of the
publish set — none is a `(version=1.0.0, channel=preview)` row in
`config/webflash-builds.json`.

---

## 5. Gate + step results (the `Attach to Release` job)

The release-attaching job runs only on `github.event_name == 'release'` and is the
sole job granted `contents: write`. Every step finished `success`; the terminal
upload step is gated behind both pre-upload checks, so the presence of all four
`.bin` files plus the checksums and manifest as **uploaded release assets** is
direct evidence both gates and the upload passed.

| Step | Result |
|---|---|
| `Attach to Release` (job) | ✅ **success** |
| Generate checksums (`checksums-sha256.txt`, `checksums-md5.txt`) | ✅ success |
| Create firmware manifest (`manifest.json`, build-info) | ✅ success |
| **Validate WebFlash release notes** (`scripts/validate-webflash-release-notes.py … --channel preview`) | ✅ **success** |
| **Check WebFlash release assets** (`scripts/check-webflash-release-assets.py --version 1.0.0 --channel preview`) | ✅ **success** (4 matched build rows, each `.bin` ≥ 100 KB) |
| **Upload release assets** (`softprops/action-gh-release`, `fail_on_unmatched_files: true`) | ✅ **success** (4 `.bin` + 2 checksum files + `manifest.json`) |

---

## 6. Posture preserved

| Posture claim | State after this run |
|---|---|
| Channel | all four artifacts are **preview** (never stable) |
| Recommended / default | **not recommended, not a customer default** |
| Candidate bundles (`S360-KIT-KITCHEN-P`, `S360-KIT-BEDROOM-P`, `S360-KIT-LIVING-P`, `S360-KIT-CORRIDOR-P`) | **hidden / not buyable** — unchanged |
| Customer-default production release | the **stable Bathroom PoE** kit (`S360-KIT-BATH-P` / `Ceiling-POE-VentIQ-RoomIQ` / `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`) remains the **only** one |
| Launch SKU | **`S360-KIT-BATH-P`** — unchanged |
| TRIAC (`S360-320`) | **not added** — stays blocked by `HW-005`, off the WebFlash matrix and both pickers |
| Fan manual-preview (`FanRelay` / `FanPWM` / `FanDAC`) | **not added** — manual-lane only |
| LED | stays **preview**; never auto-promoted to stable |
| Hardware / bench / compliance / commercial-availability | **none claimed** |

---

## 7. What is proven (and what is not)

* **Proven (firmware-build / release proof only):** the four preview targets
  compiled, were renamed to the WebFlash-compatible artifact names, passed the
  release-notes and release-asset gates, and were attached to a real GitHub
  prerelease — i.e. **importable upstream preview artifacts now exist**.
* **Not proven / not claimed:** hardware operation, bench verification, a verified
  schematic, electrical / mains-safety / EMC compliance, commercial availability,
  or any stable-promotion readiness. Stable stays gated by `PRODUCT-POE-410-001`
  (S360-410 PoE-PSU schematic verification), plus AirIQ sensor-stack bench
  evidence for the Kitchen firmware and the LED preview-to-stable gauntlet for the
  RoomIQ-LED firmware. A published **preview** artifact is **not** a stable
  release and **not** a hardware/compliance claim.

---

## 8. Validation

All commands run from the repo root and pass (this PR records results into a new
doc; it adds no config row, no product YAML, and no WebFlash build, so the
existing counts are unchanged):

| Command | Result |
|---|---|
| `python3 tests/validate_configs.py` | `✅ All configuration files are valid!` |
| `python3 scripts/validate_compile_targets.py --metadata-only` | `✅ Metadata validation passed.` |
| `python3 scripts/validate_preview_release_targets.py --metadata-only` | `✅ … validation passed.` (9 targets) |
| `python3 tests/test_product_catalog.py` | `OK` |
| `python3 tests/validate_webflash_builds.py` | `✅ All WebFlash build entries are valid!` (5 builds) |
| `python3 tests/test_shop_commercial_source_of_truth.py` | `OK` |
| `python3 tests/test_preview_release_notes_drafts.py` | `OK` |
| `python3 tests/test_preview_publish_plan.py` | `OK` (unchanged — rows stay `metadata-ready-unpublished`) |
| `python3 tests/test_preview_publish_results.py` | `OK` (this PR's guard) |
| `python3 -m unittest discover -s tests -p "test_*.py"` | `OK` |

---

## 9. Follow-up — WebFlash import (queued)

**WebFlash import comes after upstream artifacts exist — and they now do.** With
the four preview artifacts published on `v1.0.0-preview`, the WebFlash-side
one-click import is now actionable and is queued as
**`WF-PREVIEW-IMPORT-FIRST-BATCH-001`** in `UPCOMING_PR.md`: import the first
batch of preview artifacts (config-string row + `products/webflash` wrapper on the
WebFlash repo, behind the existing acknowledgement gate), consuming each release
asset's `browser_download_url` + tag + recorded SHA256. That work lives in the
[`sense360store/WebFlash`](https://github.com/sense360store/WebFlash) repo, **not**
here, and changes nothing in this repo.

---

## Guardrails — what this PR did and did NOT do

This PR **records** a successful, already-completed release run. It did **not**,
and must not be read as having done, any of:

* re-run the release workflow or create another release / tag / checksum;
* build or commit any `.bin` (none is in this diff);
* write `manifest.json` or `firmware/sources.json`, or add/modify any
  `config/webflash-builds.json` row (ledger stays 5; the three new rows stay
  `release_state: metadata-ready-unpublished`);
* touch the WebFlash repo;
* flip anything to `production` / `stable`; mark any preview build recommended /
  default; expose any candidate bundle as buyable; change the launch SKU away from
  `S360-KIT-BATH-P`;
* add a TRIAC row (FanTRIAC stays `advanced-manual-preview`, blocked by `HW-005`);
  add a fan manual-preview row (`FanRelay` / `FanPWM` / `FanDAC` stay on the
  manual lane);
* claim hardware, bench, compliance, safety, or commercial-availability proof.

The files changed by the PR carrying this record are this document, the guard test
[`tests/test_preview_publish_results.py`](../tests/test_preview_publish_results.py),
and `UPCOMING_PR.md`.

---

## Cross-references

- Publish plan (pre-run record): [`docs/release-preview-publish-plan.md`](release-preview-publish-plan.md)
- Preview WebFlash build rows: [`docs/release-preview-webflash-build-rows.md`](release-preview-webflash-build-rows.md)
- Preview release-note drafts (dry-run): [`docs/release-preview-webflash-release-notes-dryrun.md`](release-preview-webflash-release-notes-dryrun.md) · [`docs/release-notes/preview/`](release-notes/preview/)
- Compile dry-run record: [`docs/release-preview-compile-dryrun.md`](release-preview-compile-dryrun.md)
- Published stable + LED preview release proof: [`docs/webflash-release-proof.md`](webflash-release-proof.md)
- Release-eligibility source of truth: [`config/webflash-builds.json`](../config/webflash-builds.json)
- Release / build workflow: [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)
- Release-asset / release-body gates: [`scripts/check-webflash-release-assets.py`](../scripts/check-webflash-release-assets.py) · [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py)
- Commercial source of truth: [`docs/shop-commercial-source-of-truth.md`](shop-commercial-source-of-truth.md)
- Canonical roadmap / status: [`docs/sense360-roadmap-status.md`](sense360-roadmap-status.md)

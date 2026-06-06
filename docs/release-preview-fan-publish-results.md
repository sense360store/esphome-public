# Manual-preview fan firmware publish — recorded successful run

> **Workflow since merged:** this run was executed by the standalone
> `Manual-Preview Fan Firmware Publish` workflow, which has since been merged into
> [`preview-fan-publish.yml`](../.github/workflows/preview-fan-publish.yml)
> (`fan_set: single-driver`). This historical run record is unchanged.

**Canonical id:** `RELEASE-PREVIEW-FAN-PUBLISH-RESULTS-001`
**Date:** 2026-06-03
**Type:** Records the **successful** `Manual-Preview Fan Firmware Publish`
workflow run that published the three buildable manual-preview fan-control
firmware artifacts (FanRelay / FanPWM / FanDAC) — the run queued as
`RELEASE-PREVIEW-FAN-PUBLISH-RUN-001`. This is **documentation / config-evidence
only** — it records an already-completed run. It **does not** re-run the
workflow, create another release, build or commit any `.bin`, write
`manifest.json` / `firmware/sources.json`, touch the WebFlash repo, add any
`config/webflash-builds.json` row, promote anything to stable, make any fan build
recommended / default, expose any fan product as buyable, include TRIAC, change
the launch SKU **`S360-KIT-BATH-P`**, change Simple install, or claim any
hardware / bench / compliance / commercial-availability proof.

**Predecessors:**

- `#703` `RELEASE-PREVIEW-FAN-TRIAC-BUILD-ROWS-001` added the non-WebFlash
  build-row ledger
  [`config/preview-fan-triac-build-rows.json`](../config/preview-fan-triac-build-rows.json)
  and the validated preview release-note drafts under
  [`docs/release-notes/manual-preview/`](release-notes/manual-preview/).
- `#704` `RELEASE-PREVIEW-FAN-PUBLISH-PLAN-001` verified the publish inputs /
  scope, found the workflow/publish-path **gap**, and queued the workflow + run
  ([`docs/release-preview-fan-publish-plan.md`](release-preview-fan-publish-plan.md)).
- `#705` `RELEASE-PREVIEW-FAN-PUBLISH-WORKFLOW-001` added the dispatch-only,
  dry-run-default publication workflow
  [`.github/workflows/manual-preview-fan-publish.yml`](../.github/workflows/manual-preview-fan-publish.yml)
  and its validator
  [`scripts/validate_manual_preview_fan_publish.py`](../scripts/validate_manual_preview_fan_publish.py).
- `#695` `RELEASE-PREVIEW-COMPILE-RESULTS-001` recorded the hosted compile run
  [`26821900127`](https://github.com/sense360store/esphome-public/actions/runs/26821900127)
  as GREEN firmware-build proof for the three fan drivers.
- `RELEASE-PREVIEW-FAN-PUBLISH-RUN-001` is the run this document records as **done
  / success**.

---

## TL;DR

* **The manual-preview fan publish run is DONE and GREEN.** The
  `Manual-Preview Fan Firmware Publish` workflow ran on a **`workflow_dispatch`
  (manual dispatch)** with `dry_run=false` —
  [run `26878032103`](https://github.com/sense360store/esphome-public/actions/runs/26878032103)
  (2026-06-03) — and finished with **conclusion `success`**.
* **The three buildable fan artifacts were built and attached.** The matrix
  resolved to exactly the three `delivery_lane: manual-preview` rows
  (`Ceiling-POE-VentIQ-FanRelay-RoomIQ`, `Ceiling-POE-FanPWM`,
  `Ceiling-POE-FanDAC`); each compiled `success`, and the publish job attached the
  three durable `-v1.0.0-preview.bin` files plus `checksums-sha256.txt`,
  `checksums-md5.txt`, and a build-info `manifest.json`.
* **TRIAC was excluded.** `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` is **build-blocked
  by `HW-005`**; no TRIAC build job ran and no TRIAC artifact exists.
* **Shared preview release — `v1.0.0-preview` is the single preview release for
  every preview artifact.** The three fan `.bin` were attached to the shared
  `v1.0.0-preview` GitHub Release (see §4), which also carries the four
  room-bundle preview `.bin`. Under `RELEASE-PREVIEW-FAN-SHARED-TAG-001` this is
  the **intended** model — there is no separate fan release tag; room-bundle, LED,
  and FanRelay/FanPWM/FanDAC manual-preview artifacts all live under one shared
  preview release. `softprops/action-gh-release` upserted the release, so its name
  + body + checksum/manifest helper files were **refreshed** (a release-metadata
  refresh, **not a release error**). The four room-bundle preview `.bin` remain
  attached with their **SHA256 values intact**, so the WebFlash preview import is
  unaffected, and the shared release now intentionally co-hosts the room-bundle
  and fan preview artifacts.
* **Posture is unchanged.** All three fan artifacts are **preview** — not stable,
  not recommended, not a customer default; the fan products stay **hidden / not
  buyable**; the **stable Bathroom PoE release** (`S360-KIT-BATH-P` /
  `Ceiling-POE-VentIQ-RoomIQ`) remains the only customer-default production
  release and Simple install is unchanged. **No** hardware / bench / compliance /
  commercial-availability proof is claimed — this is **firmware-build / release
  proof only**.
* **Records, does not republish.** This PR edits only this doc, its guard test,
  the three fan rows' `publish_evidence` in
  [`config/preview-fan-triac-build-rows.json`](../config/preview-fan-triac-build-rows.json),
  and `UPCOMING_PR.md`. No firmware is built, no `.bin` is committed, no
  `config/webflash-builds.json` / `manifest.json` / `firmware/sources.json` is
  written, and the WebFlash repo is untouched.

---

## 1. The publish run (evidence)

| Field | Value |
|---|---|
| Workflow name | **`Manual-Preview Fan Firmware Publish`** ([`.github/workflows/manual-preview-fan-publish.yml`](../.github/workflows/manual-preview-fan-publish.yml)) |
| Run id | **`26878032103`** (run #1, attempt 1) |
| Run URL | <https://github.com/sense360store/esphome-public/actions/runs/26878032103> |
| Event | **`workflow_dispatch`** (manual dispatch) — **not** a `release` event |
| Input — `dry_run` | **`false`** (the `dry-run` job was **skipped**, confirming a real publish dispatch) |
| Input — `release_target` | `all-manual-preview-fans` (matrix resolved to the three fan rows) |
| Input — `version` | `1.0.0` |
| Input — `release_tag` | **`v1.0.0-preview`** (the shared preview release for all preview artifacts; the workflow default is now `v1.0.0-preview` — see §4) |
| Triggered by | `sense360store` |
| Head branch | `main` |
| Commit (`head_sha`) | `0963afb9c9582f5021019d1635421e41c9dd10f6` (`0963afb`, merge of #705, `RELEASE-PREVIEW-FAN-PUBLISH-WORKFLOW-001`) |
| Started → finished | 2026-06-03 10:09:33Z → 10:13:59Z (≈4.5m) |
| Build count | **3** manual-preview fan artifacts |
| Conclusion | **`success`** |

### 1.1 Job results

Six jobs were scheduled; the `dry-run` job was correctly **skipped** because
`dry_run=false`. Every other job finished `success`.

| Job | Result |
|---|---|
| `Manual-preview fan matrix` (validate metadata + generate matrix) | ✅ **success** |
| `Build manual-preview fan: Ceiling-POE-VentIQ-FanRelay-RoomIQ` | ✅ **success** |
| `Build manual-preview fan: Ceiling-POE-FanPWM` | ✅ **success** |
| `Build manual-preview fan: Ceiling-POE-FanDAC` | ✅ **success** |
| `Manual-preview fan publish dry-run` | ⏭️ **skipped** (`dry_run=false`) |
| `Attach manual-preview fan release assets` | ✅ **success** |

No TRIAC build job exists in the run — `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` is
build-blocked by `HW-005` and is absent from the fan-only matrix.

---

## 2. The three published manual-preview fan artifacts

Every artifact is `channel: preview`, `version: 1.0.0`, `delivery_lane:
manual-preview`, and is backed by its
[`config/preview-fan-triac-build-rows.json`](../config/preview-fan-triac-build-rows.json)
build row. Sizes and SHA256 values below are the **recorded GitHub Release asset
values** (matching the uploaded `checksums-sha256.txt`).

| # | Config string | Artifact (preview `.bin`) | Size (bytes) | SHA256 |
|---|---|---|---|---|
| 1 | `Ceiling-POE-VentIQ-FanRelay-RoomIQ` | `Sense360-Ceiling-POE-VentIQ-FanRelay-RoomIQ-v1.0.0-preview.bin` | 989,840 | `f9600a6b7891b520eff28314a001ff3b0d566224d3ab7d82de2e15242d026ca4` |
| 2 | `Ceiling-POE-FanPWM` | `Sense360-Ceiling-POE-FanPWM-v1.0.0-preview.bin` | 950,720 | `4ef9f35346b38be05d270d07b6baa46eae139e7a440af95e80f97c3b91c59926` |
| 3 | `Ceiling-POE-FanDAC` | `Sense360-Ceiling-POE-FanDAC-v1.0.0-preview.bin` | 930,400 | `151894c1408c5ae9d45f56382e392a82539a87d2882f443fa9bc78cdb6a39b9f` |

### 2.1 Workflow (CI) artifacts

The build jobs also uploaded the three intermediate workflow artifacts (7-day
retention, `expires_at: 2026-06-10`) the publish job consumed:

| Workflow artifact name | Artifact id | Compressed size (bytes) |
|---|---|---|
| `manual-preview-firmware-fanrelay` | `7381745752` | 686,653 |
| `manual-preview-firmware-fanpwm` | `7381738007` | 661,192 |
| `manual-preview-firmware-fandac` | `7381742682` | 648,311 |

These are expiring CI artifacts (the `${{ matrix.candidate_id }}` upload), not the
durable release assets; the durable `-preview.bin` files in §2 are the published
deliverables.

---

## 3. Gate + step results (the `Attach manual-preview fan release assets` job)

The publish job is the only job granted `contents: write` and runs only on a
non-dry-run `workflow_dispatch`. Every step finished `success`.

| Step | Result |
|---|---|
| `Download manual-preview firmware artifacts` (`manual-preview-firmware-*`) | ✅ success |
| **`Validate manual-preview output set`** (output validation; exact non-TRIAC `.bin` set) | ✅ **success** |
| `Generate checksums and build-info manifest` (`checksums-sha256.txt`, `checksums-md5.txt`, `manifest.json`) | ✅ success |
| **`Generate and validate release notes`** (`scripts/validate-webflash-release-notes.py … --channel preview`) | ✅ **success** |
| **`Upload manual-preview release assets`** (`softprops/action-gh-release`, `fail_on_unmatched_files: true`) | ✅ **success** |
| `Publish summary` | ✅ success |

The build-info `manifest.json` attached by this run records `channel: preview`,
`delivery_lane: manual-preview`, `target_count: 3`, `webflash_importable: false`,
the git SHA `0963afb…`, ESPHome `2026.4.5`, and the per-file SHA256 / size for the
three fan `.bin` — it is **not** the WebFlash production-signed manifest.

---

## 4. Release vehicle — the shared `v1.0.0-preview` preview release

Under `RELEASE-PREVIEW-FAN-SHARED-TAG-001`, `v1.0.0-preview` is the **single,
shared preview release** for every preview firmware artifact — the room-bundle
previews, the LED preview, and the FanRelay / FanPWM / FanDAC manual-preview
artifacts. There is **no** dedicated fan release tag. The run attached the three
fan `.bin` to that shared release via `softprops/action-gh-release`, which
upserts (creates-or-updates) the release. Recorded:

| Field | Value |
|---|---|
| Release tag used | **`v1.0.0-preview`** (the shared preview release for all preview artifacts) |
| Release id | `333373906` |
| Release name (now) | `Sense360 manual-preview fan firmware 1.0.0` (refreshed from `Sense360 Preview Firmware v1.0.0`) |
| Release body (now) | the manual-preview fan release notes (refreshed) |
| Prerelease / draft | `true` / `false` |
| `target_commitish` (now) | `0963afb9c9582f5021019d1635421e41c9dd10f6` |
| Release URL | <https://github.com/sense360store/esphome-public/releases/tag/v1.0.0-preview> |

**Effect of the upsert (a release-metadata refresh, not a release error):**

* The three fan `.bin` (created `2026-06-03T10:13:54Z`) were **added** as new
  assets; `checksums-sha256.txt` / `checksums-md5.txt` / `manifest.json` were
  **refreshed** by the upsert. Regenerating these — and the release name / body —
  so they describe the room **and** fan preview artifacts together is the queued
  `RELEASE-PREVIEW-COMBINED-RELEASE-NOTES-001` follow-up (see §8); it is a
  metadata refresh, not a correction of an error.
* The **four** pre-existing WebFlash room-bundle preview assets (created
  `2026-06-02T21:04:35Z`) **remain attached** with their **SHA256 values intact**
  — `Ceiling-POE-AirIQ-RoomIQ` (`16565de6…`), `Ceiling-POE-RoomIQ` (`2c7d691c…`),
  `Ceiling-POE-RoomIQ-LED` (`d4f18824…`), and `Ceiling-POE-VentIQ-RoomIQ-LED`
  (`9e513b47…`). These match the SHA256 values WebFlash pinned in
  `WF-PREVIEW-IMPORT-FIRST-BATCH-001`, so the preview artifacts WebFlash already
  imported are **unaffected** by this run.
* The shared release therefore now **intentionally co-hosts** seven `.bin` — four
  room-bundle preview + three fan preview — exactly as the shared-tag model
  intends.

This is a **release-metadata refresh only** — no artifact was deleted, no SHA256
changed, and no WebFlash import broke. Presence of a fan artifact in the shared
release does **not** make it WebFlash-importable: WebFlash import eligibility is
controlled separately by WebFlash import policy (the fan-token guardrail keeps fan
rows out of `config/webflash-builds.json`), so a fan preview in the shared release
is never implied to be a WebFlash one-click import, a Simple-install build, or
stable / recommended / default / buyable.

---

## 5. Posture preserved

| Posture claim | State after this run |
|---|---|
| Channel | all three fan artifacts are **preview** (never stable) |
| Recommended / default | **not recommended, not a customer default** |
| Fan products (`FanRelay` S360-310 / `FanPWM` S360-311 / `FanDAC` S360-312) | **hidden / not buyable** — unchanged |
| Customer-default production release | the **stable Bathroom PoE** kit (`S360-KIT-BATH-P` / `Ceiling-POE-VentIQ-RoomIQ` / `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`) remains the **only** one |
| Simple install | **unchanged** — stable Bathroom PoE build only |
| Launch SKU | **`S360-KIT-BATH-P`** — unchanged |
| TRIAC (`S360-320`) | **excluded** — build-blocked by `HW-005`; no build job, no artifact, off the fan matrix |
| WebFlash import | **not done** — no fan row added to `config/webflash-builds.json`; the fan-token guardrail is intact (`WEBFLASH-RELAY-001` / `WEBFLASH-PWM-001` / `WEBFLASH-DAC-001` remain later, separately gated follow-ups) |
| Hardware / bench / compliance / commercial-availability | **none claimed** |

---

## 6. What is proven (and what is not)

* **Proven (firmware-build / release proof only):** the three buildable
  manual-preview fan product YAMLs
  (`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`,
  `products/sense360-ceiling-poe-fanpwm.yaml`,
  `products/sense360-ceiling-poe-fandac.yaml`) compiled on hosted CI, were renamed
  to their contract artifact names, passed the manual-preview output + release-note
  gates, and were attached to a real GitHub prerelease — i.e. durable
  `-v1.0.0-preview.bin` fan artifacts now exist.
* **Not proven / not claimed:** any FanTRIAC compile (build-blocked by `HW-005`),
  hardware operation, bench verification, a verified schematic, electrical /
  mains-safety / EMC compliance, commercial availability, or any stable-promotion
  readiness. Stable stays gated per target — mains-safety / installation-approval
  + competent-person sign-off + GPIO3 strap-pin characterisation (FanRelay);
  measured current / thermal (FanPWM); Cloudlift S12 / J3 harness + S360-312
  schematic (FanDAC). A published **preview** artifact is **not** a stable release
  and **not** a hardware / compliance claim.

---

## 7. Validation

All commands run from the repo root and pass (this PR records results and adds
`publish_evidence` to the three fan rows only; it adds no `config/webflash-builds.json`
row, no product YAML, and no firmware, so the existing counts are unchanged):

| Command | Result |
|---|---|
| `python3 tests/validate_configs.py` | `✅ All configuration files are valid!` |
| `python3 scripts/validate_compile_targets.py --metadata-only` | `✅ Metadata validation passed.` |
| `python3 scripts/validate_preview_release_targets.py --metadata-only` | `✅ … validation passed.` |
| `python3 scripts/validate_preview_fan_triac_build_rows.py --metadata-only` | `✅ … ledger validation passed.` (4 rows) |
| `python3 scripts/validate_manual_preview_fan_publish.py --metadata-only` | `Manual-preview fan publish metadata validated (3 target(s)…)` |
| `python3 tests/test_product_catalog.py` | `OK` |
| `python3 tests/validate_webflash_builds.py` | `✅ … valid!` (no fan / TRIAC row added) |
| `python3 tests/test_preview_fan_publish_results.py` | `OK` (this PR's guard) |
| `python3 -m unittest discover -s tests -p "test_*.py"` | `OK` |

---

## 8. Follow-up

* **WebFlash import — intentionally out of scope.** WebFlash one-click import of
  the fan preview artifacts is **not** wanted today and is **not** performed here.
  It remains the separately gated `WEBFLASH-RELAY-001` / `WEBFLASH-PWM-001` /
  `WEBFLASH-DAC-001` follow-ups (WebFlash repo, behind a fan preview warning UX),
  contingent on a deliberate WebFlash policy decision. No fan row is added to
  `config/webflash-builds.json`; the fan-token guardrail stays intact.
* **Shared preview release — accepted.** `RELEASE-PREVIEW-FAN-SHARED-TAG-001`
  formally adopts `v1.0.0-preview` as the single shared preview release for all
  preview artifacts (room-bundle + LED + fan). The dedicated
  `v1.0.0-manual-preview-fans` tag concept is retired; no re-cut onto a separate
  fan tag is wanted, and none is performed.
* **Combined release body / manifest (queued).** The shared release's name / body
  / checksums currently describe only the fan content. Regenerating a combined
  preview release body + manifest that covers both the room-bundle previews and
  the fan previews is queued as `RELEASE-PREVIEW-COMBINED-RELEASE-NOTES-001` in
  `UPCOMING_PR.md`; it is a release-metadata refresh, not actioned here.
* **FanTRIAC `HW-005`** — unchanged buildability defect; FanTRIAC stays
  `advanced-manual-preview`, build-blocked, excluded from every publish surface.

---

## Guardrails — what this PR did and did NOT do

This PR **records** a successful, already-completed publish run. It did **not**,
and must not be read as having done, any of:

* re-run the publish workflow or create another release / tag / checksum;
* build or commit any `.bin` (none is in this diff);
* write `manifest.json` or `firmware/sources.json`, or add/modify any
  `config/webflash-builds.json` row (the fan-token guardrail stays intact);
* touch the WebFlash repo;
* flip anything to `stable`; mark any fan build recommended / default; expose any
  fan product as buyable; change the launch SKU away from `S360-KIT-BATH-P`;
  change Simple install;
* include TRIAC (FanTRIAC stays `advanced-manual-preview`, blocked by `HW-005`);
* claim hardware, bench, compliance, safety, or commercial-availability proof.

The files changed by the PR carrying this record are this document, the guard test
[`tests/test_preview_fan_publish_results.py`](../tests/test_preview_fan_publish_results.py),
the three fan rows' `publish_evidence` in
[`config/preview-fan-triac-build-rows.json`](../config/preview-fan-triac-build-rows.json)
(TRIAC untouched — stays build-blocked with no compile / publish evidence), and
`UPCOMING_PR.md`.

---

## Cross-references

- Publish plan (pre-run record): [`docs/release-preview-fan-publish-plan.md`](release-preview-fan-publish-plan.md)
- Publish workflow: [`.github/workflows/manual-preview-fan-publish.yml`](../.github/workflows/manual-preview-fan-publish.yml) · validator [`scripts/validate_manual_preview_fan_publish.py`](../scripts/validate_manual_preview_fan_publish.py)
- Fan / TRIAC build-row ledger: [`config/preview-fan-triac-build-rows.json`](../config/preview-fan-triac-build-rows.json) · readiness record [`docs/release-preview-fan-triac-build-rows.md`](release-preview-fan-triac-build-rows.md)
- Manual-preview release-note drafts: [`docs/release-notes/manual-preview/`](release-notes/manual-preview/)
- Manual fan lane: [`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json)
- Compile dry-run record: [`docs/release-preview-compile-dryrun.md`](release-preview-compile-dryrun.md)
- Predecessor WebFlash publish results: [`docs/release-preview-publish-results.md`](release-preview-publish-results.md)
- WebFlash release-eligibility source of truth: [`config/webflash-builds.json`](../config/webflash-builds.json)
- Commercial source of truth: [`docs/shop-commercial-source-of-truth.md`](shop-commercial-source-of-truth.md)

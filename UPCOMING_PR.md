# Upcoming PR

This file is the source-of-truth queue for the next planned change set in the
esphome-public repository. The **Next queue (actionable)** section lists the only
true open work; the **Completed / merged** section keeps a one-line history of
recently landed PRs. Full historical PR write-ups are retained below.

## Preview-release queue state (source of truth)

Where the preview-release program actually stands today:

* **Channel-tier policy — DONE** (`RELEASE-PREVIEW-ALL-PRODUCTS-001`, #686).
  [`config/release-channel-policy.json`](config/release-channel-policy.json) opens
  **preview** eligibility to every buildable product; lack of hardware proof
  blocks **stable only**.
* **Preview target manifest — DONE**
  (`RELEASE-PREVIEW-TARGETS-ALL-PRODUCTS-001`, #687).
  [`config/preview-release-targets.json`](config/preview-release-targets.json)
  enumerates every buildable product as a concrete preview / advanced-preview
  release target (config string, YAML path, channel, artifact name, warning copy,
  WebFlash import eligibility, stable blocker, build blocker).
* **All-buildable releasable metadata — DONE**
  (`RELEASE-PREVIEW-WEBFLASH-ALL-BUILDABLE-001`, #688). Fan targets are
  `manual-preview`, FanTRIAC is `advanced-manual-preview`; **no** buildable target
  is "blocked from preview" for lacking stable evidence.
* **Hardware blockers are stable-only for preview — DONE**
  (`RELEASE-PREVIEW-UNBLOCK-ALL-BUNDLES-001`, this PR). Formalises the decision
  into machine-checkable per-target flags. Every row of
  [`config/release-channel-policy.json`](config/release-channel-policy.json)
  `preview_release_matrix` and every target of
  [`config/preview-release-targets.json`](config/preview-release-targets.json)
  now carries explicit `preview_allowed` / `preview_warning_required` /
  `blocker_is_stable_only` flags, plus a top-level `unblock_all_bundles_decision`
  block classifying every hardware / bench / compliance / commercial blocker as
  **stable-only** and `buildability` as the only preview blocker. `preview_allowed`
  is `true` for **every buildable product** (fan-control + TRIAC included). **TRIAC**
  stays `advanced-manual-preview` only (`blocker_is_stable_only: false`,
  `hardware_proof_blocks_preview: false`, `preview_cut_gated_by_buildability: true`
  under `HW-005`; mains-risk warning + `COMPLIANCE-001` kept; never stable /
  recommended / default / safe / certified). Fan drivers stay `manual-preview`
  only. **Simple install stays stable Bathroom PoE only**; candidate bundles stay
  **hidden / not buyable**; **no stable / full release unblock**. Adds
  [`tests/test_release_preview_unblock_all_bundles.py`](tests/test_release_preview_unblock_all_bundles.py).
  Docs/config + test only: publishes no firmware, adds no
  `config/webflash-builds.json` row, flips no catalog status, does not touch the
  WebFlash repo, and does not update `firmware/sources.json` / `manifest.json`.
* **Build/release dry-run — DONE (metadata; compile pending)**
  (`RELEASE-PREVIEW-BUILD-DRYRUN-001`). Recorded a per-target dry-run for all 9
  targets in
  [`docs/release-preview-build-dryrun.md`](docs/release-preview-build-dryrun.md):
  metadata / config validation is clean (6/6 commands, 1245 tests, 0 failures),
  but the **ESPHome compile dry-run could not run (CLI unavailable)** so **no
  build proof is claimed**. 3 manual-preview fan targets + the published LED
  preview are metadata-clean; 3 targets are `blocked-by-missing-yaml` and FanTRIAC
  is `blocked-by-build` (HW-005). Published nothing, built no `.bin`, added no
  `config/webflash-builds.json` row.
* **Build/release dry-run RE-RUN — DONE (metadata; compile still pending)**
  (`RELEASE-PREVIEW-BUILD-DRYRUN-002`, this PR). Re-ran the dry-run after #691 +
  #692 in
  [`docs/release-preview-build-dryrun-002.md`](docs/release-preview-build-dryrun-002.md):
  metadata clean again (6/6 commands, now **217 files / 18 compile-only / 9
  preview / 1245 tests, 0 failures**); ESPHome still unavailable so **no compile
  proof is claimed**. **The 3 `blocked-by-missing-yaml` targets are resolved →
  `blocked-by-missing-yaml` 3 → 0.** `Ceiling-POE-AirIQ-RoomIQ`,
  `Ceiling-POE-RoomIQ`, `Ceiling-POE-RoomIQ-LED` reclassify to **`blocked-by-build`**
  (buildable composition resolves, but `compile_validation_status: pending-ci` and
  no `products/webflash` wrapper yet). Counts now: 1 `stable-only-existing`, 1
  `ready-for-preview-build`, 3 `ready-for-manual-preview-build`, **4
  `blocked-by-build`** (FanTRIAC HW-005 + the 3 reclassified), 0
  `blocked-by-missing-yaml`, 0 `blocked-by-policy`. Removed nothing
  (`components/` + `products/` intact), promoted nothing, added no
  `config/webflash-builds.json` row.
* **Hosted compile dry-run — DONE (GREEN)** (`RELEASE-PREVIEW-COMPILE-DRYRUN-001`
  added the lane, #694; `RELEASE-PREVIEW-COMPILE-RESULTS-001`, this PR, records the
  run). The scoped `workflow_dispatch`-only lane
  [`.github/workflows/preview-compile-dryrun.yml`](.github/workflows/preview-compile-dryrun.yml)
  (name `Preview Compile Dry-Run`) was dispatched on the default branch with
  `compile_mode=full` —
  [run `26821900127`](https://github.com/sense360store/esphome-public/actions/runs/26821900127)
  (2026-06-02, ESPHome 2026.4.5) — and **all 9 jobs (scope + 7 compile +
  summary) finished `success`**. **All seven** preview / manual-preview targets
  compiled **PASS**; **TRIAC is excluded** (`HW-005`, reported not compiled).
  Metadata recorded: the three webflash previews flip `compile_validation_status`
  **`pending-ci` → `validated-full-compile`** (citing the run in a
  `compile_evidence` block); the three fans keep `validated-full-compile` with the
  run as hosted corroboration. **Logs only** — no `.bin`, no Release/tag, no
  `config/webflash-builds.json` row, no `firmware/sources.json` / `manifest.json`,
  no stable / TRIAC change. Firmware-build proof only (not hardware / bench /
  compliance). See
  [`docs/release-preview-compile-dryrun.md`](docs/release-preview-compile-dryrun.md).
* **Preview build rows + release-note drafts — DONE (metadata / dry-run).** The
  three reviewed `config/webflash-builds.json` **preview** rows were cut
  (`RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001`, #698; ledger 2 → 5), and their
  **release-note drafts** were generated + validated against the WebFlash
  release-body contract (`RELEASE-PREVIEW-RELEASE-NOTES-DRYRUN-001`, #699) under
  [`docs/release-notes/preview/`](docs/release-notes/preview/). Metadata /
  dry-run only: rows stay `metadata-ready-unpublished`, drafts are attached to no
  Release, nothing is promoted to stable, and the consuming candidate bundles stay
  hidden / not buyable. Firmware-build proof only (run `26821900127`).
* **Publish plan — DONE (#700).** `RELEASE-PREVIEW-PUBLISH-PLAN-001` planned the
  actual publication of the three metadata-ready preview artifacts
  ([`docs/release-preview-publish-plan.md`](docs/release-preview-publish-plan.md)):
  per-artifact config string / build row / wrapper / draft / compile evidence /
  commercial posture / channel / workflow selector / output filename, plus a
  verified workflow scope (the picker selects exactly the three; stable Bathroom,
  TRIAC, and the fan manual-preview targets stay out; WebFlash repo untouched).
  Planning only — publishes nothing, runs no workflow, adds no `.bin` / Release /
  tag / `manifest.json` / `firmware/sources.json`. Guard:
  [`tests/test_preview_publish_plan.py`](tests/test_preview_publish_plan.py).
* **Publish run — DONE (`RELEASE-PREVIEW-PUBLISH-RESULTS-001`, this PR).**
  `RELEASE-PREVIEW-PUBLISH-RUN-001` ran: the `Build & Release Firmware` workflow
  published prerelease `v1.0.0-preview` on the **`release` event** —
  [run `26847702410`](https://github.com/sense360store/esphome-public/actions/runs/26847702410),
  conclusion **`success`** — building and attaching **four** preview artifacts
  (the release event ignores the `workflow_dispatch`-only `release_target` picker
  and builds every `version=1.0.0` + `channel=preview` row). Release-notes
  validation, the WebFlash release-asset check, and upload all passed. Recorded in
  [`docs/release-preview-publish-results.md`](docs/release-preview-publish-results.md);
  guard [`tests/test_preview_publish_results.py`](tests/test_preview_publish_results.py).
* **Actual preview artifacts — PUBLISHED.** The four preview `.bin` artifacts
  (`Ceiling-POE-AirIQ-RoomIQ`, `Ceiling-POE-RoomIQ`, `Ceiling-POE-RoomIQ-LED`,
  `Ceiling-POE-VentIQ-RoomIQ-LED`) are attached to `v1.0.0-preview` with checksums
  and a build-info `manifest.json`. They are **preview** — not stable, not
  recommended, not a customer default; candidate bundles stay hidden / not
  buyable; the stable Bathroom PoE release stays the only customer-default
  production release; no hardware / compliance proof is claimed. The three new
  rows stay `release_state: metadata-ready-unpublished` in
  [`config/webflash-builds.json`](config/webflash-builds.json) (this record edits
  no build row).
* **WebFlash import — NOW ACTIONABLE.** Importable upstream preview artifacts now
  exist, so the WebFlash-side one-click import is unblocked and queued as
  `WF-PREVIEW-IMPORT-FIRST-BATCH-001` (a WebFlash-repo follow-up, behind the
  existing acknowledgement gate). No WebFlash change is in this repo.
* **Fan-control / TRIAC preview build rows + release-note drafts — DONE (this PR,
  `RELEASE-PREVIEW-FAN-TRIAC-BUILD-ROWS-001`).** Adds the non-WebFlash build-row
  ledger
  [`config/preview-fan-triac-build-rows.json`](config/preview-fan-triac-build-rows.json)
  (the manual / advanced-manual analog of `config/webflash-builds.json`) plus
  validated preview release-note drafts under
  [`docs/release-notes/manual-preview/`](docs/release-notes/manual-preview/) for
  the four fan / TRIAC targets. FanRelay / FanPWM / FanDAC are `manual-preview`
  rows citing **firmware-build proof only** (run `26821900127`); FanTRIAC is
  `advanced-manual-preview`, **build-blocked by `HW-005`** with **no compile proof
  claimed** and the mandatory mains-risk warning. Adds **no**
  `config/webflash-builds.json` row, flips no catalog status, promotes nothing to
  stable / recommended / default / buyable, leaves **Simple install + launch SKU
  `S360-KIT-BATH-P` unchanged**, and makes **no** TRIAC safety / compliance claim.
  Guards
  [`scripts/validate_preview_fan_triac_build_rows.py`](scripts/validate_preview_fan_triac_build_rows.py)
  + [`tests/test_preview_fan_triac_build_rows.py`](tests/test_preview_fan_triac_build_rows.py);
  full record
  [`docs/release-preview-fan-triac-build-rows.md`](docs/release-preview-fan-triac-build-rows.md).
* **Manual-preview fan publish plan — DONE (this PR,
  `RELEASE-PREVIEW-FAN-PUBLISH-PLAN-001`).** Plans the actual publication of the
  three **buildable** manual-preview fan artifacts (`Ceiling-POE-VentIQ-FanRelay-RoomIQ`,
  `Ceiling-POE-FanPWM`, `Ceiling-POE-FanDAC`) — per-target config string / lane
  (`manual-preview`) / channel (`preview`) / artifact name / product YAML / manual
  artifact row / release-note draft / compile evidence (run `26821900127`) /
  warning copy / stable blocker / hidden-not-buyable posture / no-hardware-proof
  disclaimer — in
  [`docs/release-preview-fan-publish-plan.md`](docs/release-preview-fan-publish-plan.md).
  **TRIAC is out of scope** (`HW-005`, build-blocked, no compile proof). The
  workflow/publish-path check found a **gap**: the release workflow
  [`firmware-build-release.yml`](.github/workflows/firmware-build-release.yml)
  publishes **only** `config/webflash-builds.json` rows (fan-token guardrail keeps
  fans out) and the manual lane
  [`manual-firmware-artifacts.yml`](.github/workflows/manual-firmware-artifacts.yml)
  is non-release / expiring, so **neither** can durably publish these artifacts.
  The plan therefore **queues** `RELEASE-PREVIEW-FAN-PUBLISH-WORKFLOW-001` (add the
  manual-preview publish path) then `RELEASE-PREVIEW-FAN-PUBLISH-RUN-001` (execute
  it) — **without** adding any fan row to `config/webflash-builds.json`. Planning
  only: publishes nothing, runs no workflow, no `.bin` / Release / tag /
  `manifest.json` / `firmware/sources.json`, no WebFlash repo change, launch SKU
  `S360-KIT-BATH-P` + Simple install unchanged, no hardware / bench / compliance
  proof. Guard
  [`tests/test_preview_fan_publish_plan.py`](tests/test_preview_fan_publish_plan.py).
* **Manual-preview fan publish workflow — DONE (this PR,
  `RELEASE-PREVIEW-FAN-PUBLISH-WORKFLOW-001`).** Adds the dispatch-only,
  dry-run-default workflow
  [`.github/workflows/manual-preview-fan-publish.yml`](.github/workflows/manual-preview-fan-publish.yml)
  plus
  [`scripts/validate_manual_preview_fan_publish.py`](scripts/validate_manual_preview_fan_publish.py)
  so the three buildable manual-preview fan targets can be durably published
  from
  [`config/preview-fan-triac-build-rows.json`](config/preview-fan-triac-build-rows.json)
  / [`config/manual-firmware-artifacts.json`](config/manual-firmware-artifacts.json)
  without adding any fan row to
  [`config/webflash-builds.json`](config/webflash-builds.json). `dry_run: true`
  validates only; `dry_run: false` compiles the selected fan target(s), renames
  outputs to the ledger's `expected_preview_artifact_name`, validates the exact
  non-TRIAC output set, and attaches the `.bin` files plus checksums and a
  build-info `manifest.json` to the dedicated
  `v1.0.0-manual-preview-fans` prerelease. **TRIAC stays excluded** (`HW-005`).
  No workflow is run by this PR; no `.bin` / Release / tag is created; no
  repo-root `manifest.json` / `firmware/sources.json`, WebFlash repo,
  Simple-install, stable, recommended, default, buyable, hardware, bench, or
  compliance state changes. Guard:
  [`tests/test_preview_fan_publish_workflow.py`](tests/test_preview_fan_publish_workflow.py).

So **policy, target manifest, releasable metadata, the metadata build/release
dry-run + re-run, and now the hosted compile dry-run are done**. The three former
`blocked-by-missing-yaml` preview targets gained **concrete product YAMLs**
(`RELEASE-PREVIEW-BUILD-FIXES-001`, #691); the hosted compile dry-run (run
`26821900127`, `RELEASE-PREVIEW-COMPILE-RESULTS-001`, #695) then **compiled
them GREEN** and flipped their `compile_validation_status` to
`validated-full-compile`, so their **only** residual WebFlash prerequisite was the
`products/webflash` wrapper — now **authored** by
`RELEASE-PREVIEW-WEBFLASH-WRAPPERS-001` (#696). The reviewed
`config/webflash-builds.json` **preview build rows** for the three wrapped
previews then landed (`RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001`, #698), their
**release-note drafts** were generated + validated
(`RELEASE-PREVIEW-RELEASE-NOTES-DRYRUN-001`, #699) — release-note dry-run only,
nothing published — and the **publish plan** for the three metadata-ready preview
artifacts was verified (`RELEASE-PREVIEW-PUBLISH-PLAN-001`, #700) and the **actual
publish then ran GREEN** (`RELEASE-PREVIEW-PUBLISH-RUN-001`, recorded by
`RELEASE-PREVIEW-PUBLISH-RESULTS-001`, this PR; run `26847702410`, four preview
artifacts on `v1.0.0-preview`). The remaining open work: the **WebFlash import**
of the now-published preview artifacts (`WF-PREVIEW-IMPORT-FIRST-BATCH-001`, a
WebFlash-repo follow-up), the **manual-preview fan publish run**
(`RELEASE-PREVIEW-FAN-PUBLISH-RUN-001`, now queued behind the new workflow), plus
resolving FanTRIAC `HW-005` — captured as the next queue items below.

---

## Next queue (actionable)

> **`SHOP-COMMERCIAL-SOURCE-OF-TRUTH-001` is DONE (this PR; commercial / docs +
> config only).** Records the first-shop-launch **commercial naming and shop
> posture decision** so product naming, ecommerce copy, WebFlash links,
> candidate-bundle visibility, and claims are consistent before customer-facing
> pages publish. Canonical shop SKU **`S360-KIT-BATH-P`** (title *Sense360
> Bathroom Bundle — PoE*); `S360-KIT-BATH-POE` is a legacy alias and
> `S360-KIT-CEILING-VENTIQ-ROOMIQ-POE` is rejected (too close to firmware
> naming). Launch sells the **complete Bathroom PoE bundle only** (no individual
> boards); candidate bundles stay **hidden / not buyable**; customer WebFlash URL
> is **`https://flash.sense360.com`** (GitHub Pages = fallback, `mysense360.com`
> reserved for a future portal). Approved vs forbidden claims are pinned (no
> mold / condensation / safety-certified / base-kit fan-control / TRIAC claims).
> Adds [`config/shop-commercial-source-of-truth.json`](config/shop-commercial-source-of-truth.json),
> [`docs/shop-commercial-source-of-truth.md`](docs/shop-commercial-source-of-truth.md),
> and [`tests/test_shop_commercial_source_of_truth.py`](tests/test_shop_commercial_source_of_truth.py).
> See the write-up below. Publishes nothing, builds no `.bin`, adds no
> `config/webflash-builds.json` row, flips no `schematic_status` / lifecycle, and
> does not touch the WebFlash repo.

> `RELEASE-PREVIEW-BUILD-DRYRUN-001` is **DONE** — see
> [`docs/release-preview-build-dryrun.md`](docs/release-preview-build-dryrun.md)
> and the detailed write-up below. It recorded the metadata dry-run for all 9
> targets (compile pending an ESPHome-capable environment) and seeded the two
> follow-ups below.

> **Precursor cleared — `REPO-STRUCTURE-AUDIT-001` is DONE (#692; audit only).**
> Before the preview build-fix work adds files under `products/bundles/`, this
> audited the top-level `components/` and `products/` directories. **Result:
> `products/` active / KEEP** (release/build backbone; `products/bundles/**`
> active because preview targets resolve there — the next PR's expected home);
> **`components/` active / KEEP** (ESPHome external components `ld2412`/`ld2450`/
> `ld24xx`; build dependency + public remote-package surface — **not** legacy, no
> `REMOVE-LEGACY-COMPONENTS-001` follow-up). Nothing removed. Full reference map:
> [`docs/repo-structure.md`](docs/repo-structure.md) and the write-up below.

> **`RELEASE-PREVIEW-BUILD-DRYRUN-002` is DONE (this PR; metadata re-run).** Re-ran
> the dry-run after #691 + #692 — see
> [`docs/release-preview-build-dryrun-002.md`](docs/release-preview-build-dryrun-002.md)
> and the write-up below. **Confirmed the missing-YAML blocker is cleared on all
> three targets** (`yaml_path`s resolve; 217 files parse) → **`blocked-by-missing-yaml`
> 3 → 0**, with `Ceiling-POE-AirIQ-RoomIQ` / `Ceiling-POE-RoomIQ` /
> `Ceiling-POE-RoomIQ-LED` reclassified **`blocked-by-build`** (the recorded new
> blocker: `compile_validation_status: pending-ci` + no `products/webflash`
> wrapper). ESPHome still unavailable → **no compile proof claimed**. The two
> concrete follow-ups it seeds (a real compile dry-run, then the wrappers) are
> below.

### RELEASE-PREVIEW-BUILD-FIXES-001 — fix the build blockers the dry-run found — missing-YAML items DONE (this PR)

**Status:** the three `blocked-by-missing-yaml` items are **DONE in this PR**;
FanTRIAC `HW-005` and the real `esphome compile` dry-run remain open (see below).

`RELEASE-PREVIEW-BUILD-DRYRUN-001` found build blockers on 4 targets. This PR
converts the three **`blocked-by-missing-yaml`** targets into concrete preview
product YAMLs composed from existing packages only:

* `Ceiling-POE-AirIQ-RoomIQ` — new `products/bundles/ceiling-poe-airiq-roomiq.yaml`
  (Core + PoE + AirIQ + RoomIQ) + `products/sense360-ceiling-poe-airiq-roomiq.yaml`
  shim + catalog entry (`status: blocked` on `PRODUCT-POE-410-001`).
* `Ceiling-POE-RoomIQ` — bundle/shim/catalog already existed; the preview
  manifest `yaml_path` is repointed from the compile-only skeleton to the
  product YAML.
* `Ceiling-POE-RoomIQ-LED` — new `products/bundles/ceiling-poe-roomiq-led.yaml`
  (Core + PoE + RoomIQ + LED) + `products/sense360-ceiling-poe-roomiq-led.yaml`
  shim + catalog entry (`status: blocked`, `target_channel: preview-candidate`).
  **LED stays preview.**

Each new product YAML is registered as a product-level compile-only target
(`compile_validation_status: pending-ci`); the firmware combination matrix +
gap report are regenerated (the two rows move `missing-product-yaml` →
`blocked-hardware`). Channel/status stay honest: preview-only, not stable, not
recommended, not production, not hardware-verified, no bench evidence claimed.
Promotes nothing, flips no existing status, publishes no artifact, adds no
`config/webflash-builds.json` row, no `products/webflash` wrapper, no `.bin`.

**Still open (NOT in this PR):** a **real `esphome compile` dry-run** for the
three new YAMLs and the manual-preview fan targets (the authoring environment
had no ESPHome CLI, so no build proof exists yet — none was faked); the
`products/webflash` wrappers; and FanTRIAC `HW-005` buildability
(`blocked-by-build`, TRIAC policy unchanged). Subsumes the planning-only intent
of the former `RELEASE-PREVIEW-BUILD-BLOCKERS-001`.

### RELEASE-PREVIEW-COMPILE-DRYRUN-001 / RELEASE-PREVIEW-COMPILE-RESULTS-001 — hosted preview compile dry-run — DONE (GREEN)

**Status:** **DONE.** `RELEASE-PREVIEW-COMPILE-DRYRUN-001` (#694) added the scoped
lane; `RELEASE-PREVIEW-COMPILE-RESULTS-001` (this PR) **records the green hosted
run**. The lane was dispatched on the default branch with `compile_mode=full` —
[run `26821900127`](https://github.com/sense360store/esphome-public/actions/runs/26821900127)
(2026-06-02, ESPHome 2026.4.5) — and **all 9 jobs (scope + 7 compile + summary)
finished `success`**.

The lane —
[`.github/workflows/preview-compile-dryrun.yml`](.github/workflows/preview-compile-dryrun.yml)
(name `Preview Compile Dry-Run`, `workflow_dispatch`, `compile_mode=full`) driven
by [`scripts/list_preview_compile_targets.py`](scripts/list_preview_compile_targets.py)
— compiled **only** the seven preview / manual-preview targets
(`Ceiling-POE-VentIQ-RoomIQ-LED`, `Ceiling-POE-AirIQ-RoomIQ`, `Ceiling-POE-RoomIQ`,
`Ceiling-POE-RoomIQ-LED`, `Ceiling-POE-VentIQ-FanRelay-RoomIQ`,
`Ceiling-POE-FanPWM`, `Ceiling-POE-FanDAC`) — **all seven PASS** — and **excluded**
`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` (`HW-005`, reported not compiled). It uploaded
only the compile log; published nothing; created no Release / tag; wrote no
`firmware/sources.json` / `manifest.json`; added no `config/webflash-builds.json`
row. Per-target pass/fail + evidence recorded in
[`docs/release-preview-compile-dryrun.md`](docs/release-preview-compile-dryrun.md).
The sanctioned metadata flip is recorded: the three webflash previews
`compile_validation_status: pending-ci` → `validated-full-compile` (citing the run
in a `compile_evidence` block in
[`config/compile-only-targets.json`](config/compile-only-targets.json)); the three
fans keep `validated-full-compile` with the run as hosted corroboration. Firmware-build
proof only — not hardware / bench / compliance; no stable / TRIAC change.

### RELEASE-PREVIEW-WEBFLASH-WRAPPERS-001 — author the three `products/webflash` wrappers — DONE (this PR)

**Status: DONE in this PR.** The compile gate was **satisfied** by run
`26821900127` (above): `Ceiling-POE-AirIQ-RoomIQ`, `Ceiling-POE-RoomIQ`, and
`Ceiling-POE-RoomIQ-LED` are `validated-full-compile`, so the **only** residual
WebFlash prerequisite was the wrapper YAML. This PR adds the three thin
preview-only wrappers
[`products/webflash/ceiling-poe-airiq-roomiq.yaml`](products/webflash/ceiling-poe-airiq-roomiq.yaml),
[`…/ceiling-poe-roomiq.yaml`](products/webflash/ceiling-poe-roomiq.yaml), and
[`…/ceiling-poe-roomiq-led.yaml`](products/webflash/ceiling-poe-roomiq-led.yaml)
(each re-includes its canonical `products/sense360-*.yaml` shim; no version /
channel / artifact_name), records each in the per-target `webflash_wrapper` field
of [`config/preview-release-targets.json`](config/preview-release-targets.json),
and reclassifies the residual `build_blocker` from "no wrapper" to "needs a
reviewed `config/webflash-builds.json` build row". Readiness write-up:
[`docs/release-preview-webflash-wrappers.md`](docs/release-preview-webflash-wrappers.md);
regression guard [`tests/test_preview_webflash_wrappers.py`](tests/test_preview_webflash_wrappers.py).
**Still** no `config/webflash-builds.json` row, no catalog status flip, no `.bin`,
no Release / tag, no WebFlash-repo change — WebFlash import/publish stays gated
for a later reviewed build-row PR. TRIAC stays out (`HW-005`); no fan wrapper added.

### RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001 — add the three reviewed preview build rows — DONE (this PR)

**Status: DONE in this PR.** The wrapper prerequisite from
`RELEASE-PREVIEW-WEBFLASH-WRAPPERS-001` (above) is satisfied, so this PR cuts the
three reviewed **preview** rows in
[`config/webflash-builds.json`](config/webflash-builds.json) — taking the ledger
from **2 → 5** builds (one stable, four preview). Each new row uses its
`products/webflash` wrapper as `product_yaml`, is on the **preview** channel
(`Sense360-Ceiling-POE-AirIQ-RoomIQ-v1.0.0-preview.bin`,
`Sense360-Ceiling-POE-RoomIQ-v1.0.0-preview.bin`,
`Sense360-Ceiling-POE-RoomIQ-LED-v1.0.0-preview.bin`), carries the preview
release-note warning, a `commercial_posture` (hidden / candidate / not buyable /
not recommended / not default / not stable), and a `compile_evidence` block
citing hosted run `26821900127` (`firmware-build-only`). The matching
[`config/product-catalog.json`](config/product-catalog.json) rows flip
`blocked` → `preview` (`webflash_build_matrix: true`, wrapper + `artifact_name`;
required by the build-matrix ↔ catalog cross-check), and the three targets in
[`config/preview-release-targets.json`](config/preview-release-targets.json) move
from `eligible-unpublished` to **`webflash-preview-metadata-ready`** with their
build blocker resolved. Derived artifacts regenerated
(`config/firmware-combination-matrix.json`, `docs/firmware-build-gap-report.md`),
workflow pickers + `scripts/product_name_mapper.py` updated, and the affected
tests refreshed. Readiness write-up:
[`docs/release-preview-webflash-build-rows.md`](docs/release-preview-webflash-build-rows.md).
**No** `.bin`, Release, tag, `manifest.json`, or `firmware/sources.json`; **no**
stable promotion; **no** TRIAC / fan row; launch SKU stays `S360-KIT-BATH-P`;
candidate bundles stay hidden / not buyable; WebFlash one-click customer import
remains a separate, gated follow-up.

### RELEASE-PREVIEW-RELEASE-NOTES-DRYRUN-001 — generate preview release-note drafts — DONE (#699)

**Status: DONE (#699).** With the three reviewed preview build rows in place
(`RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001`, #698), #699 generated and
validated **release-note drafts** for them, completing the release-note coverage
matrix so **every** preview WebFlash build row is covered. It adds the three
drafts under
[`docs/release-notes/preview/`](docs/release-notes/preview/)
(`ceiling-poe-airiq-roomiq.md`, `ceiling-poe-roomiq.md`,
`ceiling-poe-roomiq-led.md`) — each carrying the four required H2 sections
(`## Changelog`, `## Known Issues`, `## Features`, `## Hardware Requirements`)
plus a prominent PREVIEW warning banner — and a regression guard
[`tests/test_preview_release_notes_drafts.py`](tests/test_preview_release_notes_drafts.py)
(27 tests). Each draft **validates** against the WebFlash release-body contract
([`scripts/validate-webflash-release-notes.py`](scripts/validate-webflash-release-notes.py),
`channel=preview`) and states the posture in plain words: PREVIEW firmware, NOT
stable, NOT recommended, NOT a customer default, NOT hardware verified, NOT
buyable as a public shop product; **firmware-build proof only** citing hosted
compile run `26821900127`; **no** hardware / bench / compliance /
commercial-availability proof; and points normal customers at the **stable
Bathroom PoE release** (`S360-KIT-BATH-P` / `Ceiling-POE-VentIQ-RoomIQ`). The
published stable Bathroom release and the published VentIQ LED preview are **not**
re-drafted (covered by [`docs/webflash-release-proof.md`](docs/webflash-release-proof.md)).
Readiness write-up:
[`docs/release-preview-webflash-release-notes-dryrun.md`](docs/release-preview-webflash-release-notes-dryrun.md).
**Release-note dry-run only** — no `.bin`, GitHub Release, tag, `manifest.json`,
or `firmware/sources.json`; no stable promotion; no TRIAC / fan draft; launch SKU
stays `S360-KIT-BATH-P`; candidate bundles stay hidden / not buyable; WebFlash
repo untouched.

### RELEASE-PREVIEW-PUBLISH-PLAN-001 — plan preview artifact publication for the metadata-ready WebFlash builds — DONE (this PR)

**Status: DONE in this PR.** With the three reviewed preview build rows
(`RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001`, #698), their validated release-note
drafts (`RELEASE-PREVIEW-RELEASE-NOTES-DRYRUN-001`, #699), and green firmware-build
compile proof (run `26821900127`, #695) all in place, this PR writes the **publish
plan** for the three **metadata-ready** preview WebFlash artifacts —
`Sense360-Ceiling-POE-AirIQ-RoomIQ-v1.0.0-preview.bin`,
`Sense360-Ceiling-POE-RoomIQ-v1.0.0-preview.bin`, and
`Sense360-Ceiling-POE-RoomIQ-LED-v1.0.0-preview.bin` —
[`docs/release-preview-publish-plan.md`](docs/release-preview-publish-plan.md).
For each artifact it records the config string, WebFlash build row, product YAML /
wrapper, release-note draft, compile evidence (run `26821900127`,
firmware-build-only), commercial posture (hidden / candidate / not buyable / not
recommended / not default / not stable), channel (`preview`), the
no-hardware/compliance-proof disclaimer, the expected workflow selector
(`release_target` = the config string, `channel: preview`, `version: 1.0.0`), and
the expected output filename. It **verifies workflow scope** by replaying the
release workflow's matrix filter: the picker can select **exactly** each of the
three; the stable Bathroom build (`Ceiling-POE-VentIQ-RoomIQ`) is never included
unless `channel: stable` is explicitly selected; TRIAC and the fan manual-preview
targets (`FanRelay` / `FanPWM` / `FanDAC`) are not in the matrix or the picker; and
the workflow never touches the WebFlash repo. Guard:
[`tests/test_preview_publish_plan.py`](tests/test_preview_publish_plan.py) (30
tests). **Planning only** — publishes no firmware, runs no release workflow,
creates no GitHub Release / tag / checksum, commits no `.bin`, writes no
`manifest.json` / `firmware/sources.json`, touches no WebFlash repo, marks nothing
stable, makes no preview build recommended / default, exposes no candidate bundle
as buyable, adds no TRIAC row, adds no fan manual-preview row, keeps the launch SKU
`S360-KIT-BATH-P`, and claims no hardware / bench / compliance / commercial proof.

### RELEASE-PREVIEW-PUBLISH-RUN-001 — run the actual preview artifact publication — DONE (recorded by `RELEASE-PREVIEW-PUBLISH-RESULTS-001`, this PR)

**Status: DONE / success.** The verified publish plan
(`RELEASE-PREVIEW-PUBLISH-PLAN-001`, #700) was executed by publishing the
prerelease `v1.0.0-preview`, which triggered the `Build & Release Firmware`
workflow on the **`release` event** —
[run `26847702410`](https://github.com/sense360store/esphome-public/actions/runs/26847702410),
conclusion **`success`**, 2026-06-02. Per the plan's §2.1 scoping note, a real
`release` event ignores the `workflow_dispatch`-only `release_target` picker and
builds **every** `config/webflash-builds.json` row at the tag's
`(version=1.0.0, channel=preview)` — so **four** preview artifacts were built and
attached: `Sense360-Ceiling-POE-AirIQ-RoomIQ-v1.0.0-preview.bin`,
`Sense360-Ceiling-POE-RoomIQ-v1.0.0-preview.bin`,
`Sense360-Ceiling-POE-RoomIQ-LED-v1.0.0-preview.bin`, and the re-attached
`Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` (plus
`checksums-sha256.txt`, `checksums-md5.txt`, and a build-info `manifest.json`).
Release-notes validation, the WebFlash release-asset check, and upload all passed.
The stable Bathroom build, TRIAC (`HW-005`), and the fan manual-preview targets
stayed **out**; candidate bundles stay hidden / not buyable; the launch SKU
`S360-KIT-BATH-P` is unchanged; no hardware / compliance proof is claimed.
Recorded in
[`docs/release-preview-publish-results.md`](docs/release-preview-publish-results.md)
with guard [`tests/test_preview_publish_results.py`](tests/test_preview_publish_results.py).

### WF-PREVIEW-IMPORT-FIRST-BATCH-001 — import the first batch of published preview artifacts into WebFlash (QUEUED — actionable; WebFlash repo)

**Now actionable — upstream artifacts exist.** With the four preview artifacts
published on `v1.0.0-preview` (`RELEASE-PREVIEW-PUBLISH-RUN-001`, recorded by
`RELEASE-PREVIEW-PUBLISH-RESULTS-001`), the WebFlash-side one-click import is
unblocked. This item (formerly tracked as `WEBFLASH-PREVIEW-IMPORT-HANDOFF-001`)
imports the first batch into the
[`sense360store/WebFlash`](https://github.com/sense360store/WebFlash) repo: add the
`config/webflash-builds.json` row(s) + `products/webflash` wrapper there, behind
the existing acknowledgement gate, consuming each release asset's
`browser_download_url`, tag, and recorded SHA256. **WebFlash-repo follow-up only**
— no change in this repo, no stable promotion, candidate bundles stay hidden / not
buyable, and no hardware / compliance proof is implied by import.

### RELEASE-PREVIEW-FAN-PUBLISH-PLAN-001 — plan manual-preview fan firmware publication — DONE (this PR)

**Status: DONE in this PR.** With the fan / TRIAC build-row ledger + validated
release-note drafts in place (`RELEASE-PREVIEW-FAN-TRIAC-BUILD-ROWS-001`, #703)
and green firmware-build compile proof (run `26821900127`, #695), this PR writes
the **publish plan** for the three **buildable manual-preview fan artifacts** —
`Sense360-Ceiling-POE-VentIQ-FanRelay-RoomIQ-v1.0.0-preview.bin`,
`Sense360-Ceiling-POE-FanPWM-v1.0.0-preview.bin`, and
`Sense360-Ceiling-POE-FanDAC-v1.0.0-preview.bin` —
[`docs/release-preview-fan-publish-plan.md`](docs/release-preview-fan-publish-plan.md).
For each it records the config string, lane (`manual-preview`), channel
(`preview`), artifact name, product YAML, manual-lane candidate, release-note
draft, compile evidence (run `26821900127`, firmware-build-only), warning copy,
stable blocker, commercial posture (hidden / candidate / not buyable / not
recommended / not default / not stable), and the no-hardware/compliance-proof
disclaimer. **TRIAC (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`) is out of scope**
(`HW-005`, build-blocked, no compile proof, no `.bin`). The plan **verifies the
publish path** and documents a **gap**: the release workflow publishes only
`config/webflash-builds.json` rows (the fan-token guardrail keeps fans out) and
the manual lane is non-release / expiring, so neither can durably publish these
artifacts. It therefore **queues** the workflow follow-up below **without**
hacking fans into `config/webflash-builds.json`. Guard
[`tests/test_preview_fan_publish_plan.py`](tests/test_preview_fan_publish_plan.py)
(32 tests). **Planning only** — publishes no firmware, runs no workflow, creates
no GitHub Release / tag / checksum, commits no `.bin`, writes no `manifest.json`
/ `firmware/sources.json`, touches no WebFlash repo, marks nothing stable /
recommended / default / buyable, adds no `config/webflash-builds.json` row, keeps
Simple install + the launch SKU `S360-KIT-BATH-P` unchanged, and claims no
hardware / bench / compliance proof.

### RELEASE-PREVIEW-FAN-PUBLISH-WORKFLOW-001 — add the manual-preview fan publication workflow path — DONE (this PR)

**Status: DONE in this PR.** Adds the manual-preview publication path identified
by `RELEASE-PREVIEW-FAN-PUBLISH-PLAN-001`:
[`.github/workflows/manual-preview-fan-publish.yml`](.github/workflows/manual-preview-fan-publish.yml)
plus
[`scripts/validate_manual_preview_fan_publish.py`](scripts/validate_manual_preview_fan_publish.py).
The workflow is `workflow_dispatch` only, defaults to `dry_run: true`, and reads
the manual-preview rows from
[`config/preview-fan-triac-build-rows.json`](config/preview-fan-triac-build-rows.json)
/ [`config/manual-firmware-artifacts.json`](config/manual-firmware-artifacts.json)
(**not** `config/webflash-builds.json`). A deliberate `dry_run: false` dispatch
builds `Ceiling-POE-VentIQ-FanRelay-RoomIQ`, `Ceiling-POE-FanPWM`, and/or
`Ceiling-POE-FanDAC`, renames outputs to the ledger's
`expected_preview_artifact_name`, validates the exact non-TRIAC artifact set, and
attaches the durable `-v1.0.0-preview.bin` artifacts to the dedicated
`v1.0.0-manual-preview-fans` prerelease, separate from the WebFlash
`v1.0.0-preview` release. TRIAC stays excluded (`HW-005`); no fan row is added to
`config/webflash-builds.json`; no stable promotion. Guard:
[`tests/test_preview_fan_publish_workflow.py`](tests/test_preview_fan_publish_workflow.py).
This PR runs no workflow and publishes nothing.

### RELEASE-PREVIEW-FAN-PUBLISH-RUN-001 — execute the manual-preview fan publish workflow (QUEUED — actionable)

**Now actionable after `RELEASE-PREVIEW-FAN-PUBLISH-WORKFLOW-001` lands.** Dispatch
`Manual-Preview Fan Firmware Publish` with `version=1.0.0`,
`release_tag=v1.0.0-manual-preview-fans`,
`release_target=all-manual-preview-fans`, and `dry_run=false`; then record the
run URL, release URL, attached artifact names, checksums, build-info manifest,
and unchanged guardrails. Expected artifacts:
`Sense360-Ceiling-POE-VentIQ-FanRelay-RoomIQ-v1.0.0-preview.bin`,
`Sense360-Ceiling-POE-FanPWM-v1.0.0-preview.bin`, and
`Sense360-Ceiling-POE-FanDAC-v1.0.0-preview.bin`. TRIAC remains excluded
(`HW-005`); WebFlash one-click import (`WEBFLASH-RELAY-001` /
`WEBFLASH-PWM-001` / `WEBFLASH-DAC-001`) remains a strictly later, separately
gated follow-up.

> Also queued (future, not started): **`FIRST-MAINTENANCE-RELEASE-PLAN-001`** —
> plan a future maintenance release (new version); see its entry below.

---

## Completed / merged

Recently landed; kept as one-line history (full write-ups preserved below).

* **#688 — `RELEASE-PREVIEW-WEBFLASH-ALL-BUILDABLE-001`**: made every buildable
  preview target releasable — fan targets → `manual-preview`, FanTRIAC →
  `advanced-manual-preview`; removed the "blocked-from-preview" framing. Config +
  docs only; no artifact, no WebFlash row.
* **#687 — `RELEASE-PREVIEW-TARGETS-ALL-PRODUCTS-001`**: added
  `config/preview-release-targets.json`, the concrete preview / advanced-preview
  target manifest for all buildable products. Config + docs only; published
  nothing.
* **#686 — `RELEASE-PREVIEW-ALL-PRODUCTS-001`**: added the channel-tier policy
  (`config/release-channel-policy.json`) opening preview eligibility to every
  buildable product while keeping stable evidence-gated. Policy + docs only.
* **#685 — `FIRST-RELEASE-DOCS-DRIFT-RECONCILE-001`**: reconciled the
  first-release / dry-run / roadmap / gate docs with the already-published, live
  `v1.0.0` stable release. Docs only.

Earlier completed / queued entries (including `FIRST-MAINTENANCE-RELEASE-PLAN-001`
and PR #684) are retained below as historical detail.

---

## RELEASE-PREVIEW-PUBLISH-RESULTS-001 — record preview release publication — DONE (this PR)

**Status:** **DONE.** Documentation / config-evidence only. Records the
**successful** `Build & Release Firmware` run that published the preview firmware
artifacts to the GitHub Release `v1.0.0-preview` (the run queued as
`RELEASE-PREVIEW-PUBLISH-RUN-001`). It re-runs no workflow, creates no release,
builds/commits no `.bin`, writes no `manifest.json` / `firmware/sources.json`,
touches no WebFlash repo, promotes nothing to stable, makes no preview build
recommended / default, exposes no candidate bundle as buyable, adds no TRIAC / fan
manual-preview row, keeps the launch SKU `S360-KIT-BATH-P`, and claims no
hardware / bench / compliance / commercial-availability proof.

### The run

* **Workflow:** `Build & Release Firmware`
  ([`.github/workflows/firmware-build-release.yml`](.github/workflows/firmware-build-release.yml)).
* **Run:** [`26847702410`](https://github.com/sense360store/esphome-public/actions/runs/26847702410)
  (run #43, attempt 1), **event `release`** (not `workflow_dispatch`), commit
  `2228bbb` (merge of #700), 2026-06-02 20:59:35Z → 21:04:40Z, **conclusion
  `success`**.
* **Release:** prerelease [`v1.0.0-preview`](https://github.com/sense360store/esphome-public/releases/tag/v1.0.0-preview)
  (`Sense360 Preview Firmware v1.0.0`, `prerelease: true` → `channel=preview`,
  normalised to `version=1.0.0`), published 2026-06-02 20:59:32Z.

### Four artifacts (and why four)

A real `release` event ignores the `workflow_dispatch`-only `release_target`
picker and builds **every** `config/webflash-builds.json` row matching the tag's
`(version=1.0.0, channel=preview)` — which is **four** rows. So all four preview
artifacts were built and attached:

| Config string | Artifact | Size (bytes) | SHA256 |
|---|---|---|---|
| `Ceiling-POE-AirIQ-RoomIQ` | `Sense360-Ceiling-POE-AirIQ-RoomIQ-v1.0.0-preview.bin` | 1,089,296 | `16565de6…22bc7` |
| `Ceiling-POE-RoomIQ` | `Sense360-Ceiling-POE-RoomIQ-v1.0.0-preview.bin` | 956,976 | `2c7d691c…7b937` |
| `Ceiling-POE-RoomIQ-LED` | `Sense360-Ceiling-POE-RoomIQ-LED-v1.0.0-preview.bin` | 1,006,848 | `d4f18824…c9cb0` |
| `Ceiling-POE-VentIQ-RoomIQ-LED` | `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` | 1,027,744 | `9e513b47…cdae2` |

Plus `checksums-sha256.txt`, `checksums-md5.txt`, and a build-info `manifest.json`.
The fourth artifact (`Ceiling-POE-VentIQ-RoomIQ-LED`) is a **fresh rebuild**,
distinct from the dedicated `v1.0.0-led-preview` release asset (which is
unchanged). The stable Bathroom build (`Ceiling-POE-VentIQ-RoomIQ`, `channel:
stable`), TRIAC (`HW-005`), and the fan manual-preview targets stayed out — none
is a `(version=1.0.0, channel=preview)` row.

### Gates

`Attach to Release` ran release-notes validation
([`scripts/validate-webflash-release-notes.py`](scripts/validate-webflash-release-notes.py))
and the WebFlash release-asset check
([`scripts/check-webflash-release-assets.py`](scripts/check-webflash-release-assets.py),
4 matched rows, each `.bin` ≥ 100 KB), then uploaded the assets — all `success`.

### What changed

* Added [`docs/release-preview-publish-results.md`](docs/release-preview-publish-results.md)
  — the result record (run evidence, the four artifacts with sizes + SHA256, the
  four-artifact scope explanation, gate results, posture preservation,
  validation, and guardrails).
* Added [`tests/test_preview_publish_results.py`](tests/test_preview_publish_results.py)
  — the regression guard (run id / tag / workflow / event / conclusion / count;
  the four published configs derived from `config/webflash-builds.json`; preview
  posture; no forbidden token; no `.bin` / `manifest.json` / `firmware/sources.json`
  committed; rows stay `metadata-ready-unpublished`; `UPCOMING_PR.md` marks the run
  DONE and queues the import).
* Updated `UPCOMING_PR.md` — marked `RELEASE-PREVIEW-PUBLISH-RUN-001` DONE and
  queued `WF-PREVIEW-IMPORT-FIRST-BATCH-001`.

### Validation

* `python3 tests/validate_configs.py` — PASS (unchanged).
* `python3 scripts/validate_compile_targets.py --metadata-only` — PASS.
* `python3 scripts/validate_preview_release_targets.py --metadata-only` — PASS.
* `python3 tests/test_product_catalog.py` — PASS.
* `python3 tests/validate_webflash_builds.py` — PASS (5 builds, unchanged).
* `python3 tests/test_shop_commercial_source_of_truth.py` — PASS.
* `python3 tests/test_preview_release_notes_drafts.py` — PASS.
* `python3 tests/test_preview_publish_plan.py` — PASS (rows stay
  `metadata-ready-unpublished`).
* `python3 tests/test_preview_publish_results.py` — PASS (new guard).
* `python3 -m unittest discover -s tests -p "test_*.py"` — full suite PASS.

### Guardrails (explicitly NOT done)

Did **not** re-run the release workflow, create another release / tag / checksum,
build or commit any `.bin`, write `manifest.json` / `firmware/sources.json`, add or
modify any `config/webflash-builds.json` row (ledger stays 5; the three new rows
stay `release_state: metadata-ready-unpublished`), touch the WebFlash repo, flip
anything to `production` / `stable`, make any preview build recommended / default,
expose any candidate bundle as buyable, change the launch SKU away from
`S360-KIT-BATH-P`, add a TRIAC row (`HW-005`), add a fan manual-preview row, or
claim hardware / bench / compliance / commercial-availability proof.

---

## SHOP-COMMERCIAL-SOURCE-OF-TRUTH-001 — define launch SKU, shop posture, and approved claims — DONE (this PR)

**Status:** **DONE.** Commercial / docs + config only. Records the commercial
naming and shop-posture decision for the **first shop launch** so product
naming, ecommerce copy, WebFlash links, candidate-bundle visibility, and claims
are consistent before any customer-facing page is published. It promotes
nothing, publishes no firmware, builds no `.bin`, adds no
`config/webflash-builds.json` row, flips no `schematic_status` or product-catalog
lifecycle, and does not touch the WebFlash repo.

### Decisions encoded

* **Canonical shop SKU** — `S360-KIT-BATH-P`, shop title **Sense360 Bathroom
  Bundle — PoE**. `S360-KIT-BATH-POE` (the kit-intent `kit_id` in
  [`config/kit-intent-matrix.json`](config/kit-intent-matrix.json)) is recorded
  as a **legacy alias** of `S360-KIT-BATH-P`. `S360-KIT-CEILING-VENTIQ-ROOMIQ-POE`
  (a WebFlash `kits.json` kit id) is **rejected** as a customer-facing SKU
  because it mirrors the firmware config string too closely. The canonical
  room-bundle SKU is **not renamed**.
* **Launch sale posture** — the first shop product is the **complete Bathroom
  PoE room bundle only** (`sellable-complete-room-bundle`). Individual boards
  are **not** sold publicly at launch (`individual_boards_public_sale: false`);
  they may be documented as internal / service / developer / future-add-on
  parts only.
* **Bathroom PoE readiness wording** — allowed: stable firmware available,
  Release-One firmware target, WebFlash install supported, complete room kit.
  Not allowed: hardware/compliance/safety certified, verified PoE hardware,
  bench-proven for every installation, mold prevention/detection, condensation
  guarantees (S360-410 stays `cataloged_unverified`).
* **Candidate bundle visibility** — `S360-KIT-KITCHEN-P`, `S360-KIT-LIVING-P`,
  `S360-KIT-BEDROOM-P`, `S360-KIT-CORRIDOR-P` are **hidden from shop navigation**
  by default and **not buyable** (no buy button). Optional waitlist / coming-soon
  pages allowed only if explicitly labelled (coming soon / not available to buy /
  firmware preview / hardware gates not closed) and may not imply availability,
  delivery date, or production readiness.
* **Customer WebFlash URL** — `https://flash.sense360.com`. GitHub Pages
  (`https://sense360store.github.io/WebFlash/`) is the technical fallback /
  deployment origin only; `https://mysense360.com` is reserved for a future
  customer portal, not the flashing URL.
* **Approved claims** — the allowed / not-allowed ecommerce claim lists are
  pinned. Forbidden: mold prevention/detection, condensation prevention/
  elimination, certified air-quality / medical-grade / safety-certified, base-kit
  extractor-fan / mains-fan / TRIAC fan control, guaranteed ventilation
  compliance, and any certified life-safety / building-code / medical /
  compliance claim.
* **Fan-control copy** — fan control may be framed only as future / preview /
  installer / manual-candidate; never as part of the base Bathroom PoE kit.
  TRIAC is not added as recommended / default / stable / customer-facing
  (blocked by `HW-005`).

### What changed

* Added [`config/shop-commercial-source-of-truth.json`](config/shop-commercial-source-of-truth.json)
  — the machine-readable commercial source of truth (launch product, aliases,
  rejected SKUs, WebFlash URLs, candidate-bundle visibility, allowed / forbidden
  claims, fan-control copy, hard guardrails) cross-linked to the existing
  sources of truth.
* Added [`docs/shop-commercial-source-of-truth.md`](docs/shop-commercial-source-of-truth.md)
  — the human-readable commercial launch source-of-truth doc.
* Added [`tests/test_shop_commercial_source_of_truth.py`](tests/test_shop_commercial_source_of_truth.py)
  — contract tests cross-referencing `config/room-bundle-skus.json`,
  `config/webflash-builds.json`, `config/product-catalog.json`, and
  `config/hardware-catalog.json`.
* Updated [`docs/sense360-room-bundles.md`](docs/sense360-room-bundles.md) to
  point at the commercial source of truth.
* Updated [`docs/sense360-roadmap-status.md`](docs/sense360-roadmap-status.md)
  §2 so non-launch bundles are explicitly **not publicly buyable**, plus a new
  sources-of-truth row.

### Validation

* `python3 tests/test_shop_commercial_source_of_truth.py` — **PASS** (new).
* `python3 tests/validate_configs.py` — PASS (unchanged).
* `python3 tests/test_product_catalog.py` — PASS (unchanged).
* `python3 tests/validate_webflash_builds.py` — PASS (unchanged).
* `python3 scripts/validate_preview_release_targets.py --metadata-only` — PASS
  (unchanged).
* `python3 tests/test_room_bundle_skus.py` / `tests/test_roadmap_status_doc.py`
  — PASS (unchanged by the doc edits).
* `python3 -m unittest discover -s tests -p "test_*.py"` — full suite PASS.

### Guardrails (explicitly NOT done)

Did **not** rename the canonical room-bundle SKU `S360-KIT-BATH-P`; did **not**
claim the `S360-410` schematic is verified or any hardware / compliance
certification; did **not** claim mold prevention/detection or condensation
prevention/elimination; did **not** claim fan control for the base Bathroom PoE
kit; did **not** expose candidate bundles as buyable; did **not** sell
individual boards as primary launch products; did **not** add TRIAC to any
customer-facing recommendation; did **not** publish firmware, build a `.bin`,
add a `config/webflash-builds.json` row, edit `manifest.json` /
`firmware/sources.json`, change stable/preview channel policy, change hardware
schematic status, or touch the WebFlash repo.

---

## RELEASE-PREVIEW-COMPILE-RESULTS-001 — record green hosted preview compile (this PR)

**Status:** **DONE.** Records the **successful** hosted `Preview Compile Dry-Run`
([run `26821900127`](https://github.com/sense360store/esphome-public/actions/runs/26821900127),
`workflow_dispatch` / `compile_mode=full`, 2026-06-02, ESPHome 2026.4.5) that the
lane added by `RELEASE-PREVIEW-COMPILE-DRYRUN-001` (#694) became dispatchable for
once it merged to the default branch. **All 9 jobs (scope + 7 compile + summary)
finished `success`.**

### What was recorded

* **Per-target ledger (all seven PASS):** `Ceiling-POE-VentIQ-RoomIQ-LED`,
  `Ceiling-POE-AirIQ-RoomIQ`, `Ceiling-POE-RoomIQ`, `Ceiling-POE-RoomIQ-LED`,
  `Ceiling-POE-VentIQ-FanRelay-RoomIQ`, `Ceiling-POE-FanPWM`, `Ceiling-POE-FanDAC`.
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` is **excluded** (`HW-005`, reported by the
  Scope job, not compiled). Full evidence (run/job ids, durations) in
  [`docs/release-preview-compile-dryrun.md`](docs/release-preview-compile-dryrun.md).
* **Metadata flip (`config/compile-only-targets.json`):** the three webflash
  previews `ceiling-poe-airiq-roomiq-product-compile-only`,
  `ceiling-poe-roomiq-product-compile-only`, and
  `ceiling-poe-roomiq-led-product-compile-only` move
  `compile_validation_status: pending-ci` → **`validated-full-compile`**, each
  with a structured `compile_evidence` block citing run `26821900127`. The three
  fan product targets keep `validated-full-compile` and record the same run as
  **hosted corroboration**. The two USB targets stay `pending-ci` (not in scope);
  the published LED preview has no product-level row (cited `none`).
* **Reclassification (`config/preview-release-targets.json`):** the three webflash
  previews' `build_blocker` now records **only `no products/webflash wrapper`**
  as the residual prerequisite (compile recorded green); the fan
  `preview_artifact_release` prose cites the hosted run.
* **Regression test:** `tests/test_preview_compile_dryrun.py` updated — the cited
  compile status for the six targets carrying a compile-only row is now
  `validated-full-compile` (still cited from the manifest, never invented).

### Guardrails (unchanged posture)

Firmware-build proof only. **No** firmware published, **no** GitHub Release / tag
/ checksum, **no** `.bin` committed, **no** `firmware/sources.json` /
`manifest.json`, **no** `config/webflash-builds.json` row, **no** WebFlash-repo
change, **nothing** marked stable, **TRIAC not touched / not unblocked / not added
to any release surface**, and **no** hardware / bench / compliance claim.

### Validation

* `python3 tests/validate_configs.py` — 217 files, 0 failed (exit 0).
* `python3 scripts/validate_compile_targets.py --metadata-only` — 18 targets,
  passed (exit 0).
* `python3 scripts/validate_preview_release_targets.py --metadata-only` — 9
  targets, passed (exit 0).
* `python3 tests/test_product_catalog.py` — OK (exit 0).
* `python3 tests/validate_webflash_builds.py` — 2 builds, 0 failed (exit 0).
* `python3 -m unittest discover -s tests -p "test_*.py"` — OK (exit 0).

### Next

`RELEASE-PREVIEW-WEBFLASH-WRAPPERS-001` (author the three `products/webflash`
wrappers) — the compile gate is satisfied, the wrapper is the sole residual
prerequisite. Publish / import work stays gated until the wrappers + metadata are
reviewed.

---

## RELEASE-PREVIEW-COMPILE-DRYRUN-001 — add hosted preview compile dry-run — PATH ADDED (#694; compile not yet run at that time)

**Status:** the **hosted compile dry-run path is DONE in this PR** (scoped lane +
scoping helper + regression test + honest record). The **actual hosted compile
was not run** here and **no compile proof is claimed**: the local environment has
no ESPHome CLI, and a brand-new `workflow_dispatch` workflow is not dispatchable
until it lands on the default branch. Full record:
[`docs/release-preview-compile-dryrun.md`](docs/release-preview-compile-dryrun.md).

### What changed

* New [`.github/workflows/preview-compile-dryrun.yml`](.github/workflows/preview-compile-dryrun.yml)
  (name `Preview Compile Dry-Run`): `workflow_dispatch`-only, `permissions:
  contents: read`, SHA-pinned actions. A `compile_mode` input selects `metadata`
  (default; scope validation only, no ESPHome) or `full` (the real hosted
  `esphome compile` dry-run over a matrix of the seven preview targets). It
  uploads **only** the per-target compile **log** (never a `.bin`), creates no
  Release / tag, and writes no `firmware/sources.json` / `manifest.json` /
  `config/webflash-builds.json`. Build hygiene mirrors the proven
  `manual-firmware-artifacts.yml` (throwaway secrets + local-`components/`
  `external_components` patch).
* New [`scripts/list_preview_compile_targets.py`](scripts/list_preview_compile_targets.py):
  read-only helper that derives the compile scope from
  `config/preview-release-targets.json` (`--matrix` / `--json` /
  `--config-strings` / `--report-excluded`). Scope = every `preview` /
  `advanced-preview` target **except** TRIAC → exactly the seven targets;
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` is excluded (`HW-005`) and reported, never
  compiled. The stable baseline is never in scope.
* New [`tests/test_preview_compile_dryrun.py`](tests/test_preview_compile_dryrun.py)
  (13 tests): locks the seven-target scope, the TRIAC exclusion + `HW-005` report,
  the well-formed CI matrix, and the workflow guardrails (dispatch-only, read-only
  token, logs-not-firmware, no Release action, `compile_mode=full` gating).
* New [`docs/release-preview-compile-dryrun.md`](docs/release-preview-compile-dryrun.md):
  the canonical record — chosen hosted path, honest "compile not yet run" status
  with both reasons, the exact workflow name + dispatch command, the per-target
  pass/fail/**pending** ledger, and the "firmware-build proof only, not hardware
  proof" statement.
* This `UPCOMING_PR.md`: queue-state precursor bullet, the actionable-queue entry
  (retitled PATH ADDED), the `RELEASE-PREVIEW-WEBFLASH-WRAPPERS-001` gate note,
  and this write-up.

### Per-target outcome

All seven in-scope targets are **`pending` (compile not yet run)**; the three
webflash previews stay `compile_validation_status: pending-ci`, the three fans
cite a prior `validated-full-compile` (not re-proven), and the LED preview is the
already-published preview. TRIAC is **excluded** (`HW-005`). No row is `pass` or
`fail` because no hosted compile ran. **`RELEASE-PREVIEW-WEBFLASH-WRAPPERS-001`
stays queued**, gated on a real green from the new lane; **no per-target fix PRs
are queued** (no failure was observed).

### Validation

* `python3 tests/validate_configs.py` — 217 files, 0 failed (exit 0).
* `python3 scripts/validate_compile_targets.py --metadata-only` — 18 targets,
  passed (exit 0).
* `python3 scripts/validate_preview_release_targets.py --metadata-only` — 9
  targets, passed (exit 0).
* `python3 tests/test_product_catalog.py` — 41 tests OK (exit 0).
* `python3 tests/validate_webflash_builds.py` — 2 builds, 0 failed (exit 0).
* `python3 -m unittest discover -s tests -p "test_*.py"` — 1258 tests OK
  (3 skipped) (exit 0); the `+13` are `tests/test_preview_compile_dryrun.py`.
* `esphome` compile — **not run; no local CLI; no build proof claimed or faked.**

### Guardrails (explicitly NOT done)

No hosted compile run / compile proof claimed; no firmware published; no GitHub
Release / tag / checksum; no `.bin` committed or uploaded; no WebFlash repo
change; no `firmware/sources.json` / `manifest.json`; no
`config/webflash-builds.json` row (stays 2); no `compile_validation_status` flip
(the three webflash previews stay `pending-ci`); no `config/product-catalog.json`
status / `webflash_build_matrix` flip; nothing marked stable; TRIAC not unblocked
(`HW-005` unresolved → excluded); no hardware / compliance proof.

---

## REPO-STRUCTURE-AUDIT-001 — audit components and products directories — DONE (this PR; audit only)

**Status:** **DONE in this PR** as an **audit / classification only** (deletes,
renames, and restructures nothing; removes no `products/` path, no
`products/bundles/**` path, no `components/`; changes no release policy;
publishes no firmware; touches no WebFlash repo; claims no compile/build proof).
Audits whether the top-level `components/` and `products/` directories are
active, legacy, or removable before the preview build-fix PR adds files under
`products/bundles/`.

### Outcome — both directories ACTIVE / KEEP; nothing removable

* **`products/` — active / KEEP.** It is the release/build/test/config backbone:
  18 top-level `sense360-*.yaml` customer-pinned compat shims, 11
  `products/bundles/` canonical compositions, 8 `products/compile-only/`
  validation skeletons, 3 `products/webflash/` release wrappers, and the
  `products/secrets.yaml` compile/test symlink. No obsolete subfolders; no
  removal. The expected policy holds: `products/` stays because it contains
  active product/bundle YAMLs.
* **`products/bundles/**` — active / KEEP.** Preview targets resolve here.
  `config/preview-release-targets.json` names
  `products/bundles/ceiling-poe-airiq-roomiq.yaml`,
  `…/ceiling-poe-roomiq.yaml`, and `…/ceiling-poe-roomiq-led.yaml` in its
  blocker notes, and **all 11** bundles are `!include`d by their top-level shim
  (`webflash/ → sense360-*.yaml → bundles/` 3-layer `BUNDLE-LAYER-001` chain).
  This is the next functional PR's expected home — explicitly **not** removed.
* **`components/` — active / KEEP (not legacy).** The ESPHome external
  components `ld2412` / `ld2450` / `ld24xx` (62 files) are a hard build
  dependency **and** the public remote-package surface:
  `packages/base/external_components.yaml` declares
  `components: [ld2412, ld2450, ld24xx]` via a `git` source (external consumers
  pinned to a tag fetch from this repo); **three** workflows wire it locally —
  `firmware-build-release.yml` and `manual-firmware-artifacts.yml` rewrite to
  `path: ../components`, and `ci-validate-configs.yml` rewrites the git `ref` to
  the build branch; `tests/generate_test_configs.py` inlines `path: ../../components`;
  and 7 package files instantiate `ld2412:` / `ld2450:` platforms
  (`boards/s360-200-roomiq-radar*`, `expansions/presence_ld24{12,50}`,
  `features/presence_advanced_ld2412`, `hardware/presence_ld24{12,50}`).
  A reference search proves it is **not** unused, so it is **not** removed and
  **no `REMOVE-LEGACY-COMPONENTS-001` follow-up is opened.**

No file under `components/` or `products/` classified as historical-only or
dead; on top of explicit references, every `products/**/*.yaml` is also consumed
by enumeration (`ci-validate-configs.yml` `find products/` and
`tests/test_all_yaml_release_matrix.py` `rglob`).

### What changed

* New [`docs/repo-structure.md`](docs/repo-structure.md) —
  `REPO-STRUCTURE-AUDIT-001`: the canonical structural reference + full reference
  map (the 3-layer include chain, per-subfolder classification, the `components/`
  active-dependency proof table, the bundle→shim map, audit method, and
  guardrails). Cross-links the canonical status doc
  [`docs/sense360-roadmap-status.md`](docs/sense360-roadmap-status.md) and the
  historical [`docs/repo-structure-audit.md`](docs/repo-structure-audit.md)
  (ESP-009 / ESP-010), which this refreshes for the current subfolder layout.
* This `UPCOMING_PR.md`: recorded the result (products active/keep; components
  active/keep, no removal follow-up) in the queue-state precursor note and this
  write-up.

No config, package, product YAML, component, workflow, or WebFlash file was
modified (docs + queue only).

### Validation

* `python3 tests/validate_configs.py` — 217 files, 0 failed (exit 0).
* `python3 scripts/validate_compile_targets.py --metadata-only` — 18 targets,
  metadata passed (exit 0).
* `python3 scripts/validate_preview_release_targets.py --metadata-only` — 9
  targets, passed (exit 0).
* `python3 tests/test_product_catalog.py` — 41 tests OK (exit 0).
* `python3 tests/validate_webflash_builds.py` — 2 builds, 0 failed (exit 0).
* `python3 -m unittest discover -s tests -p "test_*.py"` — 1245 tests OK
  (3 skipped) (exit 0).
* `esphome` compile — **not run; audit is docs-only; no build proof claimed.**

### Guardrails (explicitly NOT done)

No `products/` path removed; no `products/bundles/**` path removed; no
`components/` removal; no release policy change; no firmware published; no GitHub
Release / tag / checksum; no WebFlash repo change; no `config/webflash-builds.json`
row; nothing promoted to stable; no `config/product-catalog.json` status flip; no
compile / build / hardware / compliance proof claimed or faked.

---

## RELEASE-PREVIEW-BUILD-DRYRUN-001 — dry-run preview release targets — DONE (this PR; metadata dry-run, compile pending)

**Status:** **DONE in this PR** as a **metadata dry-run** (publishes nothing,
builds no `.bin`, creates no GitHub Release / tag / checksum, adds no
`config/webflash-builds.json` row, touches no WebFlash repo, writes no
`firmware/sources.json` / `manifest.json`, promotes nothing to stable, marks no
TRIAC recommended/default/stable, claims no hardware / compliance / build proof).
Recorded a per-target build/release dry-run for the current preview /
manual-preview / advanced-manual-preview matrix.

### Outcome — metadata dry-run CLEAN; compile NOT attempted (ESPHome CLI unavailable)

* **Metadata / config validation: PASS.** All six required commands exit `0`
  (see the **Validation** list below); the full suite is 1245 tests, 0 failures.
* **ESPHome compile dry-run: NOT ATTEMPTED — `esphome` CLI unavailable.** No
  `esphome` binary and no `esphome` Python module exist in this environment, so
  **no build proof is claimed or faked.** Prior `compile_validation_status`
  values are cited from `config/compile-only-targets.json` as previously-recorded
  CI status only, not re-proven here.
* **Per-target classification** (all 9 targets in
  `config/preview-release-targets.json`):
  * `stable-only-existing` (1): `Ceiling-POE-VentIQ-RoomIQ` (live `v1.0.0`).
  * `ready-for-preview-build` (1): `Ceiling-POE-VentIQ-RoomIQ-LED` (already
    published preview).
  * `ready-for-manual-preview-build` (3): `Ceiling-POE-VentIQ-FanRelay-RoomIQ`,
    `Ceiling-POE-FanPWM`, `Ceiling-POE-FanDAC` — metadata-clean, no build blocker,
    manual-preview lane; **a real compile dry-run is still owed**.
  * `blocked-by-missing-yaml` (3): `Ceiling-POE-AirIQ-RoomIQ` (no catalog entry +
    no wrapper), `Ceiling-POE-RoomIQ` (no wrapper), `Ceiling-POE-RoomIQ-LED` (no
    dedicated product/wrapper YAML, no catalog entry).
  * `blocked-by-build` (1): `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` — HW-005
    buildability (S360-320 schematic; GPIO5/GPIO6 collision; `ac_dimmer` across
    SX1509).
  * `blocked-by-policy` (0): none — no buildable target is blocked from preview
    by policy.

### What changed

* New [`docs/release-preview-build-dryrun.md`](docs/release-preview-build-dryrun.md)
  — `RELEASE-PREVIEW-BUILD-DRYRUN-001`: the full per-target ledger (config string,
  lane, YAML/product path, expected artifact name, metadata-validation result,
  compile attempt/result, exact blocker, required warning copy, stable blocker),
  the exact validation results, the outcome classification, and the referenced
  (not invoked) dry-run workflow lanes.
* This `UPCOMING_PR.md`: marked the dry-run **DONE** in the queue-state section;
  queued `RELEASE-PREVIEW-BUILD-FIXES-001` (build blockers found) and
  `RELEASE-PREVIEW-PUBLISH-PLAN-001` (enough targets metadata-clean; gated on a
  real compile dry-run); the latter two supersede the former planning-only
  `RELEASE-PREVIEW-BUILD-BLOCKERS-001` queue item.

No config, package, product YAML, workflow, or WebFlash file was modified
(docs + queue only).

### Validation

* `python3 tests/validate_configs.py` — 213 files, 0 failed (exit 0).
* `python3 scripts/validate_compile_targets.py --metadata-only` — 16 targets,
  metadata passed (exit 0).
* `python3 scripts/validate_preview_release_targets.py --metadata-only` — 9
  targets, passed (exit 0).
* `python3 tests/test_product_catalog.py` — 41 tests OK (exit 0).
* `python3 tests/validate_webflash_builds.py` — 2 builds, 0 failed (exit 0).
* `python3 -m unittest discover -s tests -p "test_*.py"` — 1245 tests OK
  (3 skipped) (exit 0).
* `esphome` compile — **not run; CLI unavailable; no build proof claimed.**

### Guardrails (explicitly NOT done)

No firmware published; no GitHub Release / tag / checksum; no committed `.bin`; no
WebFlash repo change; no `firmware/sources.json` / `manifest.json`; no
`config/webflash-builds.json` row; no `config/product-catalog.json` status or
`webflash_build_matrix` flip; nothing marked stable; TRIAC not marked
recommended/default/stable; no hardware / compliance / compile proof claimed or
faked.

---

## RELEASE-PREVIEW-BUILD-DRYRUN-002 — re-run preview dry-run after YAML fixes — DONE (this PR; metadata re-run, compile still pending)

**Status:** **DONE in this PR** as a **metadata re-run** (publishes nothing,
builds no `.bin`, creates no GitHub Release / tag / checksum, adds no
`config/webflash-builds.json` row, touches no WebFlash repo, writes no
`firmware/sources.json` / `manifest.json`, promotes nothing to stable, removes
neither `components/` nor `products/`, marks no TRIAC recommended/default/stable,
claims no hardware / compliance / build proof). Re-ran the preview /
manual-preview / advanced-manual-preview dry-run **after**
`RELEASE-PREVIEW-BUILD-FIXES-001` (#691) and `REPO-STRUCTURE-AUDIT-001` (#692) to
confirm whether the previously missing-YAML blockers are resolved and to record
the remaining blockers.

### Outcome — missing-YAML cleared (3 → 0); compile still NOT attempted (ESPHome CLI unavailable)

* **Metadata / config validation: PASS.** All six required commands exit `0`; the
  suite is now **217 files / 18 compile-only / 9 preview / 1245 tests, 0 failures**
  (the `+4` files and `+2` compile-only targets vs DRYRUN-001 are the #691 product
  YAMLs and their product-level compile-only registrations).
* **ESPHome compile dry-run: NOT ATTEMPTED — `esphome` CLI unavailable.** No
  `esphome` binary and no `esphome` module exist here, so **no fresh compile pass
  was run and none is claimed or faked.** `compile_validation_status` values are
  cited from `config/compile-only-targets.json`, not re-proven.
* **The three previously missing YAML target paths now exist and resolve.** Each
  manifest `yaml_path` points to a real `products/sense360-*.yaml` shim that
  `!include`s a `products/bundles/*.yaml` composed only from existing packages;
  `validate_configs.py` parses all of them (217/0), and
  `validate_preview_release_targets.py` (which asserts each `yaml_path`
  `is_file()`) passes 9/9.
* **Per-target re-classification** (all 9 targets):
  * `stable-only-existing` (1): `Ceiling-POE-VentIQ-RoomIQ` — unchanged.
  * `ready-for-preview-build` (1): `Ceiling-POE-VentIQ-RoomIQ-LED` — unchanged.
  * `ready-for-manual-preview-build` (3): `Ceiling-POE-VentIQ-FanRelay-RoomIQ`,
    `Ceiling-POE-FanPWM`, `Ceiling-POE-FanDAC` — unchanged; **a real compile
    dry-run is still owed**.
  * `blocked-by-missing-yaml` (**0**, was 3): all three resolved. ✅
  * `blocked-by-build` (**4**, was 1): `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`
    (HW-005 buildability **defect**, unchanged) **+** `Ceiling-POE-AirIQ-RoomIQ`,
    `Ceiling-POE-RoomIQ`, `Ceiling-POE-RoomIQ-LED` (buildable composition resolves
    but **compile-unproven `pending-ci` + `products/webflash` wrapper owed**).
  * `blocked-by-policy` (0): none.
* **Exact new blocker recorded for the three reclassified targets:** no recorded
  ESPHome compile (`compile_validation_status: pending-ci`; none produced this
  run) **and** no `products/webflash/<sku>.yaml` wrapper, so no
  `config/webflash-builds.json` preview row can be cut yet.
* **No stable / product status promoted:** catalog entries stay `status: blocked`
  / `webflash_build_matrix: false` / `blocker: PRODUCT-POE-410-001`;
  `config/webflash-builds.json` still has exactly the 2 published rows.
  `components/` (`ld2412`/`ld2450`/`ld24xx`) and `products/{bundles,compile-only,webflash}/`
  + the 18 shims are intact.

### What changed

* New [`docs/release-preview-build-dryrun-002.md`](docs/release-preview-build-dryrun-002.md)
  — `RELEASE-PREVIEW-BUILD-DRYRUN-002`: the verification of the #691 fixes
  (path-resolution + compile-only + catalog + no-promotion + directories-intact
  checks), the exact validation results, the DRYRUN-001 → -002 reclassification
  table with the recorded new blocker per target, the rationale for
  `blocked-by-build` (incl. an honest caveat on the residual wrapper YAML), the
  outcome classification, and the seeded follow-ups. DRYRUN-001's doc is retained
  unchanged as the first-run record.
* This `UPCOMING_PR.md`: recorded the re-run **DONE** in the queue-state section
  and this write-up; seeded `RELEASE-PREVIEW-COMPILE-DRYRUN-001` (the real compile
  dry-run) and `RELEASE-PREVIEW-WEBFLASH-WRAPPERS-001` (the three wrappers).

No config, package, product YAML, component, workflow, or WebFlash file was
modified (docs + queue only).

### Validation

* `python3 tests/validate_configs.py` — 217 files, 0 failed (exit 0).
* `python3 scripts/validate_compile_targets.py --metadata-only` — 18 targets,
  metadata passed (exit 0).
* `python3 scripts/validate_preview_release_targets.py --metadata-only` — 9
  targets, passed (exit 0).
* `python3 tests/test_product_catalog.py` — 41 tests OK (exit 0).
* `python3 tests/validate_webflash_builds.py` — 2 builds, 0 failed (exit 0).
* `python3 -m unittest discover -s tests -p "test_*.py"` — 1245 tests OK
  (3 skipped) (exit 0).
* `esphome` compile — **not run; CLI unavailable (`which esphome` not found,
  `import esphome` → ModuleNotFoundError); no build proof claimed.**

### Guardrails (explicitly NOT done)

No firmware published; no GitHub Release / tag / checksum; no committed `.bin`; no
WebFlash repo change; no `firmware/sources.json` / `manifest.json`; no
`config/webflash-builds.json` row; no `config/product-catalog.json` status or
`webflash_build_matrix` flip; nothing marked stable; TRIAC not marked
recommended/default/stable; `components/` not removed; `products/` not removed; no
hardware / compliance / compile proof claimed or faked.

---

## FIRST-MAINTENANCE-RELEASE-PLAN-001 — plan a future maintenance release (new version) — FUTURE / NOT STARTED

**Status:** future / not started — placeholder only. The stable first release
`v1.0.0` is published and live; there is **no pending publish action** for it.
The only legitimate future publish is a **new version** (e.g. `1.0.1` for a
maintenance/patch release or `1.1.0` for a feature release), which would have its
own real changelog, tag, build, checksums, and WebFlash handoff. This entry
exists so the next *meaningful* release task is named; it is **not** scoped or
approved here and creates nothing. It supersedes any notion of a
`FIRST-RELEASE-PUBLISH-001` (which is **not** opened — `v1.0.0` is already
published).

### When this would run

* A real, user-visible change worth shipping has merged to `main`.
* A new semantic version is chosen (`1.0.1` / `1.1.0`); `v1.0.0` is never
  re-published or re-tagged.
* The §10 publish-readiness gates in
  [`docs/first-release-dryrun-checklist.md`](docs/first-release-dryrun-checklist.md)
  are re-cleared for the new version (real changelog, artifact/checksum review,
  release-note review, WebFlash handoff, post-publish verification).

---

## FIRST-RELEASE-PUBLISH-READINESS-001 — assess first stable release publish readiness — DONE (PR #684)

**Status:** **DONE** (PR #684) — assessment / documentation only (publishes nothing, builds no
`.bin`, creates no GitHub Release, pushes no tag, promotes nothing, verifies no
hardware; no `artifact_name` added, no `webflash_build_matrix` flip, no
`firmware/sources.json` / `manifest.json` change, no `config/*.json` /
`packages/**` / `products/**` edit, no WebFlash repo change). Records the
publish-readiness assessment for the only eligible first-release stable path.

### Outcome — **ALREADY PUBLISHED / NO ACTION REQUIRED**

The current first-release stable path (`S360-KIT-BATH-P` /
`Ceiling-POE-VentIQ-RoomIQ` / `stable` / `1.0.0`) is **already published and
live**. GitHub Release **`v1.0.0`** was published on **2026-05-12** (not draft,
not prerelease) with the exact expected artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` (≈1.04 MB, sha256
`9169f2ce…ceffcc`), a **real human-authored changelog** (not a TODO/filler
placeholder), `checksums-sha256.txt` + `checksums-md5.txt`, and a build-info
`manifest.json`; and it is already **imported/live in WebFlash**
(`firmware/sources.json` pins `release_tag: v1.0.0`, plus `manifest.json` and a
per-artifact sidecar). All nine publish-readiness gates are satisfied by the live
release.

### Decision — `FIRST-RELEASE-PUBLISH-001` is NOT opened

The publish has already happened, which is terminal — not "ready to publish."
Opening a publish item would risk a **double-publish / re-tag of an existing live
release**, which the hard guardrails forbid. The only legitimate future publish
is a **new version** (`1.0.1` / `1.1.0`), out of scope here.

### Note — documentation drift (flagged, not fixed here)

The recent dry-run / gates / roadmap docs describe publishing as "still pending /
future" and say "no release/tag exists." That framing is **stale**: it describes
the dry-run *rehearsal* of a path that already shipped on 2026-05-12 (see
[`docs/webflash-release-proof.md`](docs/webflash-release-proof.md), ESP-006/ESP-007).
This assessment flags the drift for a possible follow-up docs refresh but does
**not** rewrite those gate docs (assessment-only; no gate state changed).

### What changed

* New [`docs/first-release-publish-readiness.md`](docs/first-release-publish-readiness.md)
  — `FIRST-RELEASE-PUBLISH-READINESS-001`: the live-release evidence
  (release/tag/commit/assets/changelog + WebFlash import), the nine-gate
  publish-readiness checklist (all met), the doc-drift reconciliation, and the
  decision not to open `FIRST-RELEASE-PUBLISH-001`.
* This `UPCOMING_PR.md` entry.

### Validation

* `python3 tests/validate_configs.py` — 213 files, 0 failed.
* `python3 tests/test_roadmap_status_doc.py` — 17 tests OK.
* `python3 tests/test_product_catalog.py` — 41 tests OK.
* `python3 tests/validate_webflash_builds.py` — 2 builds, 0 failed.
* `python3 -m unittest discover -s tests -p "test_*.py"` — 1177 tests OK (3 skipped).

### Guardrails (explicitly NOT changed)

* **No publish** — no GitHub Release, no tag, no release asset; publishing stays
  gated to a real `release: published` event.
* **No artifacts** — no `.bin`, no checksum file, no build-info `manifest.json`.
* **No source-of-record change** — no `firmware/sources.json` (WebFlash-owned),
  no `manifest.json`.
* **No WebFlash exposure change** — no `config/webflash-builds.json` row, no
  `artifact_name` added, no `webflash_build_matrix` flip, no new WebFlash target;
  the `sense360store/WebFlash` repo is untouched.
* **No promotion** — no other bundle promoted; `S360-410` stays
  `cataloged_unverified`; LED stays `preview`; no fan variant marked
  release-ready.

## FIRST-RELEASE-WORKFLOW-DRYRUN-CI-RESULT-001 — record hosted first-release dry-run pass

**Status:** documentation/record only (publishes nothing, builds no committed
`.bin`, promotes nothing, verifies no hardware; no GitHub Release, no tag, no
`artifact_name` added, no `webflash_build_matrix` flip, no
`firmware/sources.json` / `manifest.json` change, no `config/*.json` /
`packages/**` / `products/**` edit, no WebFlash repo change). Records the
**hosted GitHub Actions dry-run result** (passed) for the only eligible
first-release stable path and upgrades the first-release dry-run from
`partial` → `passed`.

### Summary

`FIRST-RELEASE-WORKFLOW-DRYRUN-001` (PR #681) ran the non-publishing dry-run
lanes locally and classified the outcome `dry-run partial` because this sandbox
cannot dispatch GitHub Actions; `FIRST-RELEASE-WORKFLOW-DRYRUN-CI-RUN-001`
(PR #682) recorded that dispatch blocker. An operator with GitHub Actions access
has since dispatched the hosted dry-run and it **passed**. This PR records that
result and reclassifies the dry-run as **passed**.

### Recorded hosted run (passed)

* **Workflow / job:** `Build & Release Firmware` → `Release Dry-Run (no publish)`
  (the read-only `release-dry-run` job; `workflow_dispatch` + `dry_run=true`).
* **Run URL:** https://github.com/sense360store/esphome-public/actions/runs/26723839261/job/78755574773
* **Run ID / Job ID:** `26723839261` / `78755574773`
* **Commit SHA:** `b2cc9fd5054f62c18b63230c2b380bc749abf2f0`
* **Path:** `S360-KIT-BATH-P` / `Ceiling-POE-VentIQ-RoomIQ` / `stable` / `1.0.0`.
* **Expected artifact:** `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`.
* **Result:** **`passed`** — all dry-run guardrail steps passed.
* **Artifacts:** **none** — expected for a no-publish dry-run; no release, tag,
  asset, committed `.bin`, `firmware/sources.json`, or `manifest.json`.

### Reclassification

* **First-release workflow dry-run:** **`passed`** (was `partial`).
* **Hosted CI dry-run:** **`passed`** (was blocked / not-captured).
* **Publish readiness:** **still pending** human review and a real
  changelog/publish decision (a passing dry-run does not authorise a publish).

### Publish-readiness gaps still open (explicit)

* Real `## Changelog` bullets still required before a `stable` publish (filler is
  rejected at publish time).
* External-component `ref`/tag pinning still required if release policy requires
  it (`packages/base/external_components.yaml` uses git `ref: main`).
* Checksums (`checksums-sha256.txt` / `checksums-md5.txt`) and the build-info
  `manifest.json` are **publish-time only** — none produced by the dry-run.
* WebFlash import / handoff happens **only after** a real release artifact
  exists; no WebFlash change is triggered here.

### What changed

* [`docs/first-release-dryrun-checklist.md`](docs/first-release-dryrun-checklist.md)
  — new **§11.8** recording the hosted dry-run pass; §11.4 outcome upgraded to
  `dry-run passed`, §11.5 gap #1 marked resolved, and the §11.1 / §11.7.5 / §14
  pointers updated.
* [`docs/first-release-gates.md`](docs/first-release-gates.md) — Headline
  dry-run callout updated to `dry-run passed` (hosted run captured); **gate
  tables unchanged**.
* [`docs/sense360-roadmap-status.md`](docs/sense360-roadmap-status.md) — §5.1
  outcome upgraded to `passed`; new **§5.2** recording the hosted run; status /
  blocker sections, Next Hardware Tasks, and Evidence & Bench Logs unchanged.
* This `UPCOMING_PR.md` entry.

### Guardrails (explicitly NOT changed)

* **No publish** — no GitHub Release, no tag, no release asset; publishing stays
  gated to a real `release: published` event.
* **No artifacts** — no `.bin` created/committed, no checksum file, no build-info
  `manifest.json` (the hosted dry-run produced none — expected).
* **No source-of-record change** — no `firmware/sources.json` (still absent), no
  `manifest.json`.
* **No WebFlash exposure** — no `config/webflash-builds.json` row, no
  `artifact_name` added, no `webflash_build_matrix` flip, no new WebFlash target;
  the `sense360store/webflash` repo is untouched.
* **No bundle promoted** — `S360-KIT-KITCHEN-P` / `-LIVING-P` / `-BEDROOM-P` /
  `-CORRIDOR-P` stay candidates; no `current_release_status` change.
* **S360-410 not marked verified** — `schematic_status` stays
  `cataloged_unverified`; the Release-One PoE caveat preserved.
* **LED not marked stable** — `S360-300` firmware stays `preview`; no LED-stable
  claim.
* **Fan variants not release-ready** — no fan driver
  (`S360-310`/`311`/`312`/`320`) is promoted.
* **No bench evidence claimed** — no hardware measurement run or fabricated.
* No `config/*.json` / `packages/**` / `products/**` change; docs only.

### Validation

* `python3 tests/validate_configs.py`
* `python3 tests/test_roadmap_status_doc.py`
* `python3 tests/test_product_catalog.py`
* `python3 tests/validate_webflash_builds.py`
* `python3 -m unittest discover -s tests -p "test_*.py"`

## FIRST-RELEASE-WORKFLOW-DRYRUN-001 — dry-run first stable release workflow

**Status:** documentation/record only (publishes nothing, builds no committed
`.bin`, promotes nothing, verifies no hardware; no GitHub Release, no tag, no
`artifact_name` added, no `webflash_build_matrix` flip, no
`firmware/sources.json` / `manifest.json` change, no `config/*.json` /
`packages/**` / `products/**` edit, no WebFlash repo change). Records an
**actual execution** of the existing non-publishing dry-run lanes for the only
eligible first-release path.

### Summary

`FIRST-RELEASE-DRYRUN-CHECKLIST-001` (PR #680) documented *how* to rehearse the
first stable release; this PR *runs* that rehearsal and records the result. The
dry-run targeted the only first-release-eligible stable path: bundle
`S360-KIT-BATH-P`, config `Ceiling-POE-VentIQ-RoomIQ`, channel `stable`, version
`1.0.0`, expected artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, pinned to commit
`6f4b7f748302d8cb600e2dd368076df548ed5f81`.

Because the hosted `Build & Release Firmware` / `Draft WebFlash Release Notes`
workflows are `workflow_dispatch`-driven and this environment has no GitHub
Actions dispatch capability, the dry-run was executed by running the **same
non-publishing scripts and contract tests the `release-dry-run` job and the
RELEASE-002 draft workflow run**, locally, pinned to that commit.

### Dry-run result (recorded, nothing published)

* **Stage 1–2 (release notes + validation):** `list_release_targets.py
  --validate Ceiling-POE-VentIQ-RoomIQ` → OK; generator (TODO placeholder)
  validates on `stable` (placeholder survives as a human-review signal);
  generator with realistic bullets `--validate` → pass; pure filler
  (`Initial release`) is correctly **rejected** on `stable` (gate works).
* **Stage 3 (build workflow dry-run, run locally):** target validation OK,
  `plan_room_release_notes.py --config-string Ceiling-POE-VentIQ-RoomIQ` → exit
  0 with `Validation summary: PASSED (structural, channel=stable)`,
  `tests/test_plan_room_release_notes.py` (20) + `tests/test_release_dry_run_mode.py`
  (17) → **37 tests OK**, and no `firmware/sources.json` / `manifest.json` /
  root `*.bin` produced.
* **Stage 4 (artifact naming):** `product_name_mapper.py
  ceiling-poe-ventiq-roomiq 1.0.0 stable` == `config/webflash-builds.json`
  `artifact_name` == `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`.
* **Checksums:** publish-time only — **none** produced (expected). **Artifact
  published:** **none**; working tree clean after the run.
* **Outcome classification: `dry-run partial`** *(later upgraded to `dry-run
  passed` once the hosted run was captured — see
  `FIRST-RELEASE-WORKFLOW-DRYRUN-CI-RESULT-001` above).* All local lanes pass;
  the one unmet item at the time was the hosted **workflow run URL / run ID**
  (this environment cannot dispatch GitHub Actions).

### No-safe-dry-run-mode follow-up: NOT opened (and why)

The task says to open `FIRST-RELEASE-WORKFLOW-DRYRUN-MODE-001` **only if** the
workflow has no safe dry-run mode. It already has one
(`RELEASE-WORKFLOW-DRYRUN-MODE-001`: the read-only `release-dry-run` job gated on
`workflow_dispatch && inputs.dry_run`, with publishing gated separately on the
`release` event). Opening that follow-up would fabricate a non-existent gap, so
it is **not** created. The genuine residual step — an operator dispatching the
dry-run on hosted CI and recording the run URL/ID — is tracked instead as
**`FIRST-RELEASE-WORKFLOW-DRYRUN-CI-RUN-001`** (queued below).

### What changed

* [`docs/first-release-dryrun-checklist.md`](docs/first-release-dryrun-checklist.md)
  — new **§11 Dry-run execution record** (`FIRST-RELEASE-WORKFLOW-DRYRUN-001`):
  run metadata, per-stage results, recorded artifact/checksum expectations,
  outcome `dry-run partial`, publish-readiness gaps, and reproduction commands;
  trailing sections renumbered (Guardrails §12, Validation §13,
  Cross-references §14).
* [`docs/first-release-gates.md`](docs/first-release-gates.md) — added a dry-run
  executed note under the Operator dry-run callout; **gate tables unchanged**.
* [`docs/sense360-roadmap-status.md`](docs/sense360-roadmap-status.md) — added
  **§5.1** recording the dry-run result; status/blocker sections, Next Hardware
  Tasks, and Evidence & Bench Logs unchanged.
* This `UPCOMING_PR.md` entry (plus the queued follow-up below).

### Follow-up queued

* **`FIRST-RELEASE-WORKFLOW-DRYRUN-CI-RUN-001`** ✅ **done** — the hosted dry-run
  was dispatched and **passed**
  ([run 26723839261](https://github.com/sense360store/esphome-public/actions/runs/26723839261/job/78755574773),
  commit `b2cc9fd5054f62c18b63230c2b380bc749abf2f0`); the result is recorded by
  `FIRST-RELEASE-WORKFLOW-DRYRUN-CI-RESULT-001` (entry above) and the dry-run is
  now `passed`. No code change was needed; the safe dry-run mode already exists.

### Guardrails (explicitly NOT changed)

* **No publish** — no GitHub Release, no tag, no release asset; publishing stays
  gated to a real `release: published` event.
* **No artifacts** — no `.bin` created/committed, no checksum file, no build-info
  `manifest.json`.
* **No source-of-record change** — no `firmware/sources.json` (still absent), no
  `manifest.json`.
* **No WebFlash exposure** — no `config/webflash-builds.json` row, no
  `artifact_name` added, no `webflash_build_matrix` flip, no new WebFlash target;
  the `sense360store/webflash` repo is untouched.
* **No bundle promoted** — `S360-KIT-KITCHEN-P` / `-LIVING-P` / `-BEDROOM-P` /
  `-CORRIDOR-P` stay candidates; no `current_release_status` change.
* **S360-410 not marked verified** — `schematic_status` stays
  `cataloged_unverified`; the Release-One PoE caveat preserved.
* **LED not marked stable** — `S360-300` firmware stays `preview`; no LED-stable
  claim.
* **Fan variants not release-ready** — no fan driver
  (`S360-310`/`311`/`312`/`320`) is promoted.
* **No bench evidence claimed** — no hardware measurement run or fabricated.
* No `config/*.json` / `packages/**` / `products/**` change; docs only.

### Validation

* `python3 tests/validate_configs.py`
* `python3 tests/test_roadmap_status_doc.py`
* `python3 tests/test_product_catalog.py`
* `python3 tests/validate_webflash_builds.py`
* `python3 -m unittest discover -s tests -p "test_*.py"`

## FIRST-RELEASE-DRYRUN-CHECKLIST-001 — document first stable release dry-run

**Status:** documentation/planning only (publishes nothing, builds no `.bin`,
promotes nothing, verifies no hardware; no GitHub Release, no `artifact_name`, no
`webflash_build_matrix` flip, no `firmware/sources.json` / `manifest.json`
change, no `config/*.json` / `packages/**` / `products/**` edit, no WebFlash repo
change). Adds one concrete operator checklist for **dry-running** the current
first-release path without publishing new firmware or changing WebFlash
exposure.

### Summary

`PRE-HW-PREP-FIRST-RELEASE-GATES-001` confirmed the only first-release-eligible
stable path: bundle `S360-KIT-BATH-P`, config `Ceiling-POE-VentIQ-RoomIQ`,
channel `stable`, and the WebFlash first-release gate sync has run/merged. This
PR adds the **operator dry-run checklist** that rehearses that path end to end —
release-note generation, release-note validation, the build workflow's
safe-by-default dry-run mode, artifact naming, checksum expectations, the future
`firmware/sources.json` record, the later WebFlash mirror, and rollback/no-publish
safety checks — plus an explicit publish-readiness checklist (human review,
artifact/checksum review, GitHub release-note review, WebFlash handoff, and
post-publish verification).

Every command and workflow it names already exists:
`scripts/generate_webflash_release_notes.py`,
`scripts/validate-webflash-release-notes.py`, `scripts/list_release_targets.py`,
the `Draft WebFlash Release Notes` workflow (RELEASE-002), and the
`Build & Release Firmware` workflow's `dry_run` mode
(`RELEASE-WORKFLOW-DRYRUN-MODE-001`). The checklist threads them; it changes none
of them.

### What changed

* New [`docs/first-release-dryrun-checklist.md`](docs/first-release-dryrun-checklist.md)
  — `FIRST-RELEASE-DRYRUN-CHECKLIST-001`: the one eligible path
  (`S360-KIT-BATH-P` / `Ceiling-POE-VentIQ-RoomIQ` / `stable` /
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v<x.y.z>-stable.bin`), the release-note
  generation command + RELEASE-002 workflow, changelog expectations, the build
  workflow + its dry-run mode, where expiring CI artifacts appear, checksum
  expectations, what goes into `firmware/sources.json` later, what WebFlash must
  mirror later, rollback/no-publish safety checks, the operator **dry-run
  checklist**, and the **publish-readiness checklist**.
* [`docs/first-release-gates.md`](docs/first-release-gates.md) — added a
  sources-of-truth row, a See-also note, and a §13 cross-reference pointing at
  the new dry-run checklist; gate tables unchanged.
* [`docs/sense360-roadmap-status.md`](docs/sense360-roadmap-status.md) — added a
  sources-of-truth row pointing at the dry-run checklist; status/blocker sections
  unchanged.
* This `UPCOMING_PR.md` entry.

### Guardrails (explicitly NOT changed)

* **No publish** — no GitHub Release, no tag, no release asset; the dry-run lanes
  are non-publishing and publishing stays gated to a real `release: published`
  event.
* **No artifacts** — no `.bin` created/committed, no checksum file, no build-info
  added.
* **No source-of-record change** — no `firmware/sources.json` (still absent) and
  no `manifest.json` change.
* **No WebFlash exposure** — no `config/webflash-builds.json` row, no
  `artifact_name`, no `webflash_build_matrix` flip, no new WebFlash target, and
  the `sense360store/webflash` repo is untouched.
* **No bundle promoted** — `S360-KIT-KITCHEN-P` / `-LIVING-P` / `-BEDROOM-P` /
  `-CORRIDOR-P` stay candidates; no `current_release_status` change.
* **S360-410 not marked verified** — `schematic_status` stays
  `cataloged_unverified`; the Release-One PoE caveat preserved.
* **LED not marked stable** — `S360-300` firmware stays `preview`; no LED-stable
  claim.
* **Fan variants not release-ready** — no fan driver
  (`S360-310`/`311`/`312`/`320`) is promoted.
* **No bench evidence claimed** — no hardware measurement run or fabricated.
* No `config/*.json` / `packages/**` / `products/**` change; docs only.

### Validation

* `python3 tests/validate_configs.py`
* `python3 tests/test_roadmap_status_doc.py`
* `python3 tests/test_product_catalog.py`
* `python3 tests/validate_webflash_builds.py`
* `python3 -m unittest discover -s tests -p "test_*.py"`

---

## PRE-HW-PREP-FIRST-RELEASE-GATES-001 — consolidate first-release and expansion gates

**Status:** documentation-only consolidation (promotes nothing, enables nothing,
verifies nothing; no `schematic_status` flipped, no lifecycle change, no
WebFlash exposure, no `artifact_name` set, no `webflash_build_matrix` flip, no
release, no artifact, no `firmware/sources.json` / `manifest.json` change, no
`config/*.json` / `packages/**` / `products/**` edit). Creates one canonical
first-release gate checklist showing what can ship now, what is blocked, and the
exact evidence required for each blocked path.

### Summary

Threads the existing first-release / expansion gate facts from the sources of
truth ([`config/webflash-builds.json`](config/webflash-builds.json),
[`config/room-bundle-skus.json`](config/room-bundle-skus.json),
[`config/room-bundle-fan-variants.json`](config/room-bundle-fan-variants.json),
[`config/hardware-catalog.json`](config/hardware-catalog.json),
[`config/firmware-combination-matrix.json`](config/firmware-combination-matrix.json),
the room-bundle handoff matrix, the roadmap/status doc, the pre-hardware prep
plan, and the board readiness / promotion-gate docs) into a single canonical
checklist.

**Result:** `S360-KIT-BATH-P` (Bathroom, `Ceiling-POE-VentIQ-RoomIQ`, stable)
**can ship today** as the current first-release path. Kitchen / Bedroom / Living
/ Corridor are **not** first-release eligible yet. Fan variants are
**planning-only**. Hardware bench tasks are **future-only** until physical
hardware/equipment exists.

### What changed

* New [`docs/first-release-gates.md`](docs/first-release-gates.md) —
  `PRE-HW-PREP-FIRST-RELEASE-GATES-001`: current-shippable-release, blocked
  bundle-expansion, hardware-blocker, firmware-blocker, WebFlash-blocker,
  release-note/artifact-blocker, exact-evidence-required, and next-PR-owner
  tables; covers `S360-KIT-BATH-P` / `-KITCHEN-P` / `-LIVING-P` / `-BEDROOM-P` /
  `-CORRIDOR-P`, the Bathroom/Kitchen fan variants, `S360-410` PoE PSU,
  `S360-300` LED, `S360-310` Relay, `S360-311` PWM, `S360-312` DAC, and
  `S360-320` TRIAC.
* [`docs/sense360-roadmap-status.md`](docs/sense360-roadmap-status.md) — added a
  sources-of-truth row pointing at the new consolidated gates doc.
* [`docs/pre-hardware-room-bundle-release-handoff.md`](docs/pre-hardware-room-bundle-release-handoff.md)
  — added a See-also banner pointing at the consolidated gates doc; matrix
  unchanged.
* [`docs/pre-hardware-prep-plan.md`](docs/pre-hardware-prep-plan.md) — added a
  See-also link to the gates doc (and removed two stray trailing markup lines).
* This `UPCOMING_PR.md` entry.

### Guardrails (explicitly NOT changed)

* **No bundle promoted** — no `current_release_status` change; nothing moved to
  `preview` / `stable` / `production`.
* **No WebFlash enabled** — no `config/webflash-builds.json` row, no
  `artifact_name`, no `webflash_build_matrix` flip; the WebFlash repo
  (`sense360store/webflash`) is untouched.
* **No artifacts / firmware** — no `.bin` / checksum / build-info, no
  `firmware/sources.json` / `manifest.json` change, no release / tag.
* **S360-410 not marked verified** — `schematic_status` stays
  `cataloged_unverified`; the Release-One PoE caveat preserved verbatim.
* **LED not marked stable** — `S360-300` firmware stays `preview`; no LED-stable
  claim.
* **Fan variants not release-ready** — `room-bundle-fan-variants.json` stays
  `planning` / `webflash_exposed: false`; no fan bundle SKU added.
* **No bench evidence claimed** — every bench task is a future-only forward
  pointer; no measurement is run or fabricated.
* No `config/*.json` / `packages/**` / `products/**` change; docs only.

### Validation

* `python3 tests/validate_configs.py`
* `python3 tests/test_roadmap_status_doc.py`
* `python3 tests/test_product_catalog.py`
* `python3 tests/test_room_bundle_skus.py`
* `python3 tests/test_room_bundle_fan_variants.py`
* `python3 tests/validate_webflash_builds.py`
* `python3 -m unittest discover -s tests -p "test_*.py"`

---

## PRE-HW-PREP-ROOM-BUNDLES-001 — prepare room bundles for first-release evidence handoff

**Status:** documentation-only audit (promotes nothing, enables nothing,
verifies nothing; no `schematic_status` flipped, no lifecycle change, no
WebFlash exposure, no `artifact_name` set, no release, no artifact, no
config/`packages`/`products` edit). Audits the five canonical PoE room
bundles against current board readiness and emits a pre-hardware
release-handoff matrix.

### Summary

Cross-walked the five room bundles (Bathroom, Kitchen, Living, Bedroom,
Corridor) in [`config/room-bundle-skus.json`](config/room-bundle-skus.json)
against [`config/firmware-combination-matrix.json`](config/firmware-combination-matrix.json),
[`config/webflash-builds.json`](config/webflash-builds.json),
[`docs/hardware/board-readiness-matrix.md`](docs/hardware/board-readiness-matrix.md),
and the room firmware release matrix / release-notes docs, and threaded
the result into a single matrix with, per bundle: bundle SKU, included
boards, firmware config target, release channel/status, WebFlash status,
blocking hardware evidence, release-note status, bench task pointer, and
first-release eligibility.

**Result: 1 of 5 bundles (`S360-KIT-BATH-P`) is first-release eligible
today** — it is already the Release-One stable build. The other four are
candidates owned by named follow-up PRs, none approved here.

### What changed

* [`docs/pre-hardware-room-bundle-release-handoff.md`](docs/pre-hardware-room-bundle-release-handoff.md)
  — new `PRE-HW-PREP-ROOM-BUNDLES-001` doc: the pre-hardware
  release-handoff matrix, column legend, audit findings, bench/evidence
  forward pointers, guardrails, validation, and cross-references.
* This `UPCOMING_PR.md` entry.

### Audit findings (recorded, not resolved)

1. Only `Ceiling-POE-VentIQ-RoomIQ` (Bathroom) is WebFlash-exposed; the
   four other bundles' config targets have no `webflash-builds` row.
2. Bedroom's config target `Ceiling-POE-RoomIQ` is `blocked-hardware`
   (top-level product YAML exists, blocked on `PRODUCT-POE-410-001`) in
   the firmware-combination-matrix, a nuance over the `stable-candidate`
   label in `room-bundle-skus.json`. Flagged, not reconciled.
3. The S360-410 PoE schematic-verification chain is the shared blocker
   under every non-Bathroom bundle; caveat preserved, not cleared.
4. Fan-control variants stay planning-only, not release-ready.

### Guardrails (explicitly NOT changed)

* **No bundle promoted** — no `current_release_status` change; nothing
  moved to `preview` / `stable` / `production`.
* **No WebFlash enabled** — no `config/webflash-builds.json` row, no
  `artifact_name`, no `webflash_build_matrix` flip; WebFlash repo
  untouched.
* **No artifacts** — no `.bin` / checksum / build-info, no
  `firmware/sources.json` / `manifest.json`, no release / tag.
* **S360-410 not marked verified** — `schematic_status` stays
  `cataloged_unverified`; Release-One PoE caveat preserved verbatim.
* **LED not marked stable** — `S360-300` stays `preview`.
* **Fan variants not release-ready** — `room-bundle-fan-variants.json`
  stays `planning` / `webflash_exposed: false`; no fan bundle SKU added.
* No `config/*.json` / `packages/**` / `products/**` change; docs only.

### Validation

* `python3 tests/test_room_bundle_skus.py`
* `python3 tests/test_room_bundle_fan_variants.py`
* `python3 tests/validate_configs.py`
* `python3 tests/validate_webflash_builds.py`
* `python3 tests/test_product_catalog.py`
* `python3 -m unittest discover -s tests -p "test_*.py"`

---

## PRE-HW-PREP-FW-312-CLOSEOUT-001 — close out S360-312 DAC pre-hardware prep gaps

**Status:** documentation / CI closeout (promotes nothing, verifies nothing,
resolves no owed hardware item; no `schematic_status` flipped, no lifecycle
change, no WebFlash exposure, no `artifact_name` set, no release, no compile
or measurement fabricated). Closes the remaining narrative / forward-pointer
pre-hardware gaps for the S360-312 DAC (FanDAC) board.

### Summary

Audited the merged S360-312 design-complete work (PR #674) and **confirmed all
six deliverables D1–D6 are complete**:

* D1 pinmap — [`docs/hardware/s360-312-r4-dac.md`](docs/hardware/s360-312-r4-dac.md)
  + [`docs/hardware/s360-312-module-pinmap.md`](docs/hardware/s360-312-module-pinmap.md).
* D2 firmware — [`packages/expansions/fan_gp8403.yaml`](packages/expansions/fan_gp8403.yaml)
  (+ alias [`packages/expansions/fan_dac.yaml`](packages/expansions/fan_dac.yaml)).
* D3 bundle — [`products/bundles/ceiling-poe-fandac.yaml`](products/bundles/ceiling-poe-fandac.yaml)
  (config string `Ceiling-POE-FanDAC`).
* D4 compile-only — `config/compile-only-targets.json` (`validated-full-compile`,
  run `26364679370`).
* D5 release-note template + D6 bench/evidence matrix —
  [`docs/hardware/s360-312-r4-fandac.md`](docs/hardware/s360-312-r4-fandac.md).

This closeout records **`S360-312-DAC-BENCH-001`** as the next **real hardware**
task — to be run **only when physical hardware exists**. It is a forward pointer
only: nothing is promoted, no bench evidence is claimed, and no gate is flipped.

### What changed

* [`docs/sense360-roadmap-status.md`](docs/sense360-roadmap-status.md) — new
  **Next Hardware Tasks (Blocked on Physical Hardware)** section recording the
  `S360-312-DAC-BENCH-001` task (board, blocking, evidence owed), and an empty
  **Evidence & Bench Logs** `(no bench logs yet)` placeholder. The WebFlash /
  release sections are unchanged (FanDAC stays Disabled / unexposed).
* [`docs/pre-hardware-prep-plan.md`](docs/pre-hardware-prep-plan.md) — §6
  S360-312 bench row names the queued task `S360-312-DAC-BENCH-001` (blocked on
  hardware); §7 ordered slice sequence gains a row for the bench task.
* [`docs/hardware/s360-312-r4-fandac.md`](docs/hardware/s360-312-r4-fandac.md) —
  D6 bench/evidence matrix names the bench session id `S360-312-DAC-BENCH-001`
  (to be run only when physical hardware exists; all rows stay unfilled / owed).
* [`tests/test_roadmap_status_doc.py`](tests/test_roadmap_status_doc.py) — a new
  guard asserting the Next Hardware Tasks section names `S360-312-DAC-BENCH-001`
  and the Evidence & Bench Logs section stays an empty placeholder.
* This `UPCOMING_PR.md` entry.

### Owed (recorded, not resolved)

The seven S360-312 hardware-evidence items stay **OWED** to
`S360-312-DAC-BENCH-001` (no physical board exists yet); none is resolved here:

1. Measured voltage output (per channel).
2. GP8403 detection / I²C address.
3. Output range / calibration.
4. Fan / controller response.
5. Current draw under load.
6. Thermal under sustained load.
7. Harness / silkscreen confirmation.

### Guardrails (explicitly NOT changed)

* **No S360-312 bench evidence claimed** — no GP8403 detection, no voltage,
  current, thermal, or calibration measurement is fabricated; every D6 row stays
  unfilled / owed.
* **No WebFlash enabled** — no `config/webflash-builds.json` row, the `FanDAC`
  token stays absent, the WebFlash repo (`sense360store/webflash`) is untouched.
* **No `artifact_name` added**, **no `webflash_build_matrix` flip**, **no
  firmware published** — no release / tag / `.bin`, no `manifest.json` /
  [`firmware/sources.json`](firmware/sources.json) change.
* No `config/*.json` changed (`config/product-catalog.json`,
  `config/compile-only-targets.json`, `config/manual-firmware-artifacts.json`
  untouched); no `schematic_status` / lifecycle flip; nothing marked
  hardware-stable or verified; `S360-312` stays `cataloged_unverified`.
* No `packages/**` / `products/**` change; this PR is docs + tests only.

### Validation

* `python3 tests/validate_configs.py`
* `python3 scripts/validate_compile_targets.py --metadata-only`
* `python3 tests/test_product_catalog.py`
* `python3 tests/test_module_pinmaps.py`
* `python3 tests/test_compile_expansion_candidates.py`
* `python3 tests/test_roadmap_status_doc.py`
* `python3 -m unittest discover -s tests -p "test_*.py"`

---

## S360-311-CURRENT-THERMAL-001 — record FanPWM current and thermal evidence

**Status:** documentation-only bench-evidence record (promotes nothing, verifies
nothing, resolves no owed hardware item). Records the `S360-311-CURRENT-THERMAL-001`
bench pass (2026-05-29 first pass + **2026-05-31 re-run**) on the **native**
ESP32-S3 GPIO FanPWM composition (`S360-100-R4` Core + `S360-311-R4` PWM board),
following `PRE-HW-PREP-FW-311-001`.

### Summary

The operator (`@wifispray`) re-ran the queued current / thermal / tach bench pass.
The result is recorded **honestly**: **functional PWM re-confirmed PASS**
(operator-notes-only — no photo / video / scope / multimeter log / thermal image),
but **current, thermal, and tach/RPM were all NOT measured**. Per the project
no-fabrication rule, **no current / thermal / RPM value is inferred, estimated, or
back-filled** from the fan label, the MT3608 datasheet, or the supply capability.
`PWM-6` / `PWM-13` (current / thermal) and `PWM-12` (per-fan RPM) **stay owed**;
`rpm_supported` stays **false**. The board is **not** claimed hardware-stable.

### Recorded result (per the required evidence list)

* **PWM channel 1–4** — individually speed-controlled, **PASS** (operator-notes).
* **All-four simultaneous** — **PASS**.
* **High / medium / low command** — tracked commanded duty, **PASS**.
* **Restart retention** — last commanded speed retained across a restart, **PASS**.
* **Fan model / load** — **not re-specified** this pass; the established rig on
  file (Arctic P14 Plus, one per channel) is carried for provenance only, not
  re-attested as a 2026-05-31 measurement.
* **Supply used** — **not re-specified**; rig on file is the on-board MT3608 12 V
  boost (~2 A available capability, **not** a measured ceiling).
* **Per-channel current** — **NOT measured.**
* **Aggregate current** — **NOT measured** (no measured MT3608 ceiling / sag / inrush).
* **Thermal duration / result** — **NOT measured** (no sustained thermal run; no
  method / ambient / hottest-location / measured °C).
* **Tach / RPM** — **explicitly NOT measured**; `rpm_supported` stays false.
* **`Pul_Cou3` / `IO46`** — stays **disabled / TBD** (collides with the Core
  `fan_status_led_pin` `GPIO46`); `TachIO` / `IO16` stays reserved / pending.
* **`J3` silkscreen order / `J6`↔`J3` harness / `"NINE 4pin FANs"` label / `J3`
  11/12 UART routing** — **remain OWED;** none proven on this run.

### What changed

* [`docs/hardware/s360-311-r4-pwm.md`](docs/hardware/s360-311-r4-pwm.md) — new
  top-of-file `S360-311-CURRENT-THERMAL-001` re-run callout (2026-05-31); the
  existing `§S360-311-CURRENT-THERMAL-001` section header dated for both passes
  and a **2026-05-31 re-run** subsection added (functional re-confirmed;
  current / thermal / tach again not measured; every owed item restated).
* [`docs/hardware/s360-311-r4-fanpwm.md`](docs/hardware/s360-311-r4-fanpwm.md) —
  new **D6 bench-session result so far** subsection recording the two-pass outcome
  against the D6 matrix (T3 functional PASS; T4/T5/T6/T7/T8 + T1/T2/T9/T10/T11
  owed); the `Measured` / `Pass?` columns stay empty by design.
* [`docs/hardware/board-readiness-matrix.md`](docs/hardware/board-readiness-matrix.md)
  — new **Bench evidence (`S360-311-CURRENT-THERMAL-001`)** bullet under the
  `S360-311` subsection; `schematic_status` / lifecycle classifications unchanged.
* This `UPCOMING_PR.md` entry.

### Guardrails (explicitly NOT changed)

* **No WebFlash enabled** — no wrapper, no `config/webflash-builds.json` row, no
  WebFlash repo (`sense360store/webflash`) edit; the `FanPWM` token stays absent.
* **No `artifact_name` added**, **no `webflash_build_matrix` flip**, **no firmware
  published** — no release / tag / `.bin`, no `manifest.json` /
  [`firmware/sources.json`](firmware/sources.json) change.
* **No hardware-stable claim** — current / thermal / RPM stay unvalidated; the
  evidence does not support it, so it is not claimed.
* No `config/*.json` changed — `S360-311` stays `cataloged_unverified`, no
  `schematic_status` flip, no lifecycle change; nothing marked `verified`.
* No `packages/**` / `products/**` behaviour change; no compile re-run or compile
  result fabricated; no measurement / photo / video / log fabricated — the intake
  was blank and is recorded as such. Release-One (`Ceiling-POE-VentIQ-RoomIQ` /
  stable) and the LED preview are untouched.

### Validation

* `python3 tests/validate_configs.py`
* `python3 scripts/validate_compile_targets.py --metadata-only`
* `python3 tests/test_native_fanpwm_yaml.py`
* `python3 tests/test_pwm_product_readiness.py`
* `python3 tests/test_product_catalog.py`
* `python3 -m unittest discover -s tests -p "test_*.py"`

---

## PRE-HW-PREP-FW-311-001 — bring the S360-311 PWM firmware to design-complete

**Status:** design-complete annotation + firmware finalisation (promotes
nothing, verifies nothing, resolves no owed hardware item; no `schematic_status`
flipped, no lifecycle change, no WebFlash exposure, no `artifact_name` set, no
release, no compile result fabricated). Executes slice #3
(`PRE-HW-PREP-FW-311-001`) of
[`docs/pre-hardware-prep-plan.md`](docs/pre-hardware-prep-plan.md).

### Summary

Records the `Sense360 PWM` board (`S360-311-R4`, FanPWM) as **design-complete**
— a prose / documentation annotation that is explicitly **not** `verified`
(per [`docs/pre-hardware-prep-plan.md` §1.2 / §1.4](docs/pre-hardware-prep-plan.md)).
Builds on the completed `SX1509-RECONCILE-001` + `PACKAGE-PWM-001`: finalises
[`packages/expansions/fan_pwm_native.yaml`](packages/expansions/fan_pwm_native.yaml)
as the design-complete **four-channel** native PWM+tach driver (four `ledc`
PWM-drive outputs `TachPMW1..4` -> `IO10`/`IO11`/`IO12`/`IO39` feeding four
`fan: speed` controllers; three native `pulse_counter` tach inputs
`Pul_Cou1`/`2`/`4` -> `IO17`/`IO18`/`IO9` as the per-fan-RPM mechanism, internal
diagnostic / no RPM claim), and reconciles the stale single-channel
`fan_pwm_pin: GPIO4` / `fan_tach_pin: GPIO5` placeholder in
[`packages/hardware/sense360_core_mapping.yaml`](packages/hardware/sense360_core_mapping.yaml)
to the four-channel native map (marked legacy/superseded). The FanPWM bundle
(D3) and the native compile-only targets (D4, `validated-full-compile` by
`S360-311-NATIVE-FANPWM-COMPILE-001`, local run 2026-05-28, commit `643bbd3`,
rc=0) were already landed by `SX1509-RECONCILE-001`. This slice adds the missing
design-complete pieces (D5 + D6) and the prose annotation, all from the
committed schematic.

### What changed

* [`packages/expansions/fan_pwm_native.yaml`](packages/expansions/fan_pwm_native.yaml)
  — header finalised from "NATIVE-GPIO CANDIDATE / NOT compile-proven /
  pending-ci" to "FINALISED / DESIGN-COMPLETE / compile-proven
  (validated-full-compile)", with the four-channel framing and the
  `Pul_Cou3`/`IO46` + `TachIO`/`IO16` owed notes made explicit. The
  `substitutions:` / `output:` / `fan:` / `sensor:` body is byte-identical (no
  pin / entity-name change; the recorded compile still holds).
* [`packages/hardware/sense360_core_mapping.yaml`](packages/hardware/sense360_core_mapping.yaml)
  — the stale single-channel `fan_pwm_pin: GPIO4` / `fan_tach_pin: GPIO5`
  placeholder marked **legacy / superseded** against the four-channel native
  map (header pin-map note, substitution banner, the `fan_pwm_output` /
  `fan_tach_sensor` blocks, and the SX1509 I²C address-table comment). The
  `GPIO4`/`GPIO5` values are retained as the legacy source-of-truth alias
  (consumed by `fan_control_advanced_profile.yaml`); the production
  `roomiq_sen0609_uart` radar binding (GPIO5/GPIO4) is untouched.
* [`docs/hardware/s360-311-r4-fanpwm.md`](docs/hardware/s360-311-r4-fanpwm.md)
  — new **Design-complete status** section (the four-condition §1.1 checklist
  with the compile-run reference), new **D5** release-note template +
  artifact-naming scheme (template only — no artifact, no release), new **D6**
  pre-written bench / evidence test matrix (silkscreen `J3` order, `J6`↔`J3`
  harness, native PWM drive on `IO10/11/12/39`, per-fan + aggregate current,
  thermal envelope, per-fan RPM via native `pulse_counter`, `Pul_Cou3`/`IO46`
  collision, `"NINE 4pin FANs"` label, `J3` 11/12 UART routing, `TachIO` role).
* [`docs/hardware/board-readiness-matrix.md`](docs/hardware/board-readiness-matrix.md)
  — added a `design_status: design-complete` prose bullet to the `S360-311`
  subsection; `Hardware evidence`, `schematic_status`, and `Package YAML`
  classifications unchanged.
* [`docs/pre-hardware-prep-plan.md`](docs/pre-hardware-prep-plan.md) — §3.1
  Executed note + §7 ordered-slice-sequence row 3 marked **DONE**.
* This `UPCOMING_PR.md` entry.

### Owed (recorded, not resolved)

The hardware-only items stay **OWED** to `HW-PINMAP-311` and are captured in the
D6 matrix, not resolved here: the `"NINE 4pin FANs"` label vs four-connector
question, the `J3` pins 11/12 UART-routing question, the `J3` 1-to-13
silkscreen order, the `J6`↔`J3` 13-pin harness, the `Pul_Cou3`/`IO46`
fourth-tach collision with the Core `fan_status_led_pin`, the `TachIO`/`IO16`
shared-net role, PWM polarity (`PWM-6`), per-fan + aggregate fan current, the
thermal envelope, and per-fan RPM via native `pulse_counter` (`PWM-13`).
`PWM-6` / `PWM-13` stay owed; `S360-311-CURRENT-THERMAL` is the queued bench
session that fills the D6 checklist.

### Guardrails (explicitly NOT changed)

* No `packages/boards/` board package for `S360-311` (that promotion is gated
  on HW-PINMAP-311 evidence per the plan); the driver package and bundle are
  finalised only.
* The native driver's `substitutions:` / `output:` / `fan:` / `sensor:` body is
  byte-identical (only comments/header changed); the bundle
  [`products/bundles/ceiling-poe-fanpwm.yaml`](products/bundles/ceiling-poe-fanpwm.yaml)
  is untouched (config string `Ceiling-POE-FanPWM` and entity names
  `${friendly_name} Fan 1..4` byte-identical, no `artifact_name`).
* Production `GPIO4`/`GPIO5` radar-UART binding in
  [`packages/boards/s360-100-core.yaml`](packages/boards/s360-100-core.yaml) is
  unchanged; the legacy SX1509 packages (`fan_pwm.yaml` / `fan_pwm_sx1509.yaml`)
  and the historical SX1509 proof are not revived.
* No `config/*.json` changed — `S360-311` stays `cataloged_unverified`, no
  `schematic_file`, no lifecycle / `webflash_build_matrix` / `artifact_name`
  change. `design-complete` is a doc annotation, never a JSON field.
* No `schematic_status` flip; nothing marked `verified` or
  design-complete-as-verified; no PWM current / thermal / RPM bench evidence
  claimed; `PWM-6` / `PWM-13` not closed; `rpm_supported` stays false; no
  compile result fabricated (ESPHome unavailable here; the recorded compile is
  the already-committed local run `643bbd3`).
* No WebFlash exposure, no `artifact_name`, no `webflash_build_matrix` flip, no
  `config/webflash-builds.json` row, no release / tag / artifact; the `FanPWM`
  token stays absent from `config/webflash-builds.json`.
* The production product and `tests/test_release_one_entity_names.py` are
  untouched; no edit to `manifest.json` / [`firmware/sources.json`](firmware/sources.json);
  the WebFlash repo (`sense360store/webflash`) is untouched.

### Validation

* `python3 tests/validate_configs.py`
* `python3 scripts/validate_compile_targets.py --metadata-only`
* `python3 tests/test_native_fanpwm_yaml.py`
* `python3 tests/test_pwm_product_readiness.py`
* `python3 tests/test_product_catalog.py`
* `python3 tests/test_release_one_entity_names.py`
* `python3 tests/test_product_substitutions.py`
* `python3 -m unittest discover -s tests -p "test_*.py"`

---

## PRE-HW-PREP-FW-312-001 — bring the S360-312 DAC firmware to design-complete

**Status:** design-complete annotation (docs-only; promotes nothing, verifies
nothing, resolves no owed hardware item; no `schematic_status` flipped, no
lifecycle change, no WebFlash exposure, no `artifact_name` set, no release, no
compile result fabricated). Executes slice #2
(`PRE-HW-PREP-FW-312-001`) of
[`docs/pre-hardware-prep-plan.md`](docs/pre-hardware-prep-plan.md).

### Summary

Records the `Sense360 DAC` board (`S360-312-R4`, FanDAC) as **design-complete**
— a prose / documentation annotation that is explicitly **not** `verified`
(per [`docs/pre-hardware-prep-plan.md` §1.2 / §1.4](docs/pre-hardware-prep-plan.md)).
The dual-GP8403 driver (D2), the FanDAC bundle (D3), and the compile-only
targets (D4) were already landed by the earlier FanDAC slices
(`PACKAGE-DAC-001` / `PRODUCT-DAC-001` / `FW-COMPILE-DAC-001`; the
[`packages/expansions/fan_gp8403.yaml`](packages/expansions/fan_gp8403.yaml)
driver already exposes both DACs `IC1`/`IC2` on the shared `core_i2c` bus as
four neutral outputs, with the stale `GPIO39`/`GPIO40` header comment already
corrected to the Core `IO48`/`IO45` bus), and D1 by `HW-PINMAP-312` /
`HW-PINMAP-312-FOLLOWUP`. This slice adds the missing design-complete pieces
(D5 + D6) and the design-complete prose annotation, all from the committed
schematic; it edits no YAML and no `config/*.json`.

### What changed

* [`docs/hardware/s360-312-r4-fandac.md`](docs/hardware/s360-312-r4-fandac.md)
  — new **Design-complete status** section (the four-condition §1.1 checklist
  with the compile-run link), new **D5** release-note template + artifact-naming
  scheme (template only — no artifact, no release), new **D6** pre-written
  bench / evidence test matrix (the fill-in checklist covering the verify-pending
  D1 items plus per-channel output linearity/range, Cloudlift drive, and the
  voltage-mode jumper), and a reconciliation-log row.
* [`docs/hardware/board-readiness-matrix.md`](docs/hardware/board-readiness-matrix.md)
  — added a `design_status: design-complete` prose row to the `S360-312`
  subsection with a link to the compile run; `Readiness`, `schematic_status`,
  and `Package status` are unchanged.
* [`docs/pre-hardware-prep-plan.md`](docs/pre-hardware-prep-plan.md) — §3.2
  Executed note + §7 ordered-slice-sequence row 2 marked **DONE**.
* This `UPCOMING_PR.md` entry.

### Owed (recorded, not resolved)

The hardware-only items stay **OWED** to `HW-PINMAP-312-FOLLOWUP` and are
captured in the D6 matrix, not resolved here: the Core-`J7`-`+5V`-vs-module-
`J1`-`+3.3V` rail question, the `SW1`/`SW2` DIP-switch → I²C-address mapping,
the `J2`/`J3` Cloudlift output silkscreen pin order (incl. the `J3` out0/out1
transposition), and the `5V`/`10V` voltage-mode jumper identification.

### Guardrails (explicitly NOT changed)

* No `packages/boards/` board package for `S360-312` (that promotion is gated
  on HW-PINMAP-312 evidence); the driver package and bundle are finalised only.
* No YAML edited — [`packages/expansions/fan_gp8403.yaml`](packages/expansions/fan_gp8403.yaml),
  [`packages/expansions/fan_dac.yaml`](packages/expansions/fan_dac.yaml), and
  [`products/bundles/ceiling-poe-fandac.yaml`](products/bundles/ceiling-poe-fandac.yaml)
  are byte-identical (config string `Ceiling-POE-FanDAC` and the artifact-name
  scheme unchanged).
* No `config/*.json` changed — `S360-312` stays `cataloged_unverified`, no
  `schematic_file`, no lifecycle / `webflash_build_matrix` / `artifact_name`
  change. `design-complete` is a doc annotation, never a JSON field.
* No `schematic_status` flip; nothing marked `verified` or
  design-complete-as-verified; no DAC bench / hardware evidence claimed; no
  compile result fabricated (ESPHome unavailable here; the recorded compile is
  the already-committed run `26364679370`).
* No WebFlash exposure, no `artifact_name`, no `webflash_build_matrix` flip, no
  `config/webflash-builds.json` row, no release / tag / artifact.
* FanDAC ↔ AirIQ mutex and the fan-driver `max-one-of` rule unchanged; the
  production product and `tests/test_release_one_entity_names.py` untouched.
* No edit to `manifest.json` / [`firmware/sources.json`](firmware/sources.json);
  the WebFlash repo (`sense360store/webflash`) is untouched.

### Validation

* `python3 tests/validate_configs.py`
* `python3 scripts/validate_compile_targets.py`
* `python3 tests/test_release_one_entity_names.py`
* `python3 -m unittest discover -s tests -p "test_*.py"` (1175 tests, 3 skipped)

---

## SX1509-RECONCILE-001 — migrate fan PWM path off SX1509 to native GPIO

**Status:** design-complete fan-path migration (NOT verified, NOT released; no
board promoted, no `schematic_status` flipped, no WebFlash exposure, no
`artifact_name`, no compile result fabricated). Executes slice #1
(`PRE-HW-PREP-SX1509-RECONCILE-001`) of
[`docs/pre-hardware-prep-plan.md`](docs/pre-hardware-prep-plan.md).

### Summary

Reconciles the deprecated SX1509 I/O expander out of the fan PWM path per the
operator confirmation that the SX1509 is no longer used and the schematic-printed
native fan GPIO map ([`docs/hardware/s360-100-native-fan-gpio-map.md`](docs/hardware/s360-100-native-fan-gpio-map.md):
`TachPMW1..4` -> IO10/IO11/IO12/IO39, `Pul_Cou1/2/4` -> IO17/IO18/IO9, `TachIO`
= IO16). The FanPWM bundle is migrated to compose the native
`packages/expansions/fan_pwm_native.yaml` driver instead of the deprecated
`fan_pwm.yaml` -> `fan_pwm_sx1509.yaml` chain; the per-fan entity names
(`${friendly_name} Fan 1..4`) and the `Ceiling-POE-FanPWM` config string are
kept **byte-identical**, and no `artifact_name` is added. The native
composition is full-compile validated by structural parity to the native
compile-only skeleton (`S360-311-NATIVE-FANPWM-COMPILE-001`, commit `643bbd3`,
rc=0); the legacy SX1509 full-compile run `26414398902` is preserved as the
historical proof for the SX1509 skeleton only and does not transfer.

### What changed

* [`products/bundles/ceiling-poe-fanpwm.yaml`](products/bundles/ceiling-poe-fanpwm.yaml)
  — composes `packages/expansions/fan_pwm_native.yaml` (key
  `fan_pwm_native_module`) instead of the SX1509 `fan_pwm.yaml`; header /
  binding comments rewritten to the native path. Substitutions, config string,
  and entity names byte-identical.
* [`packages/boards/s360-100-core.yaml`](packages/boards/s360-100-core.yaml) —
  removed the stale `SX1509 expander` entry from the Core I²C-device comment
  (the SX1509 is no longer a current Core I²C device on the fan path).
* [`config/product-catalog.json`](config/product-catalog.json) /
  [`config/compile-only-targets.json`](config/compile-only-targets.json) — the
  current FanPWM product / product-compile-only rows retargeted to the native
  composition + native compile evidence; the legacy SX1509 compile-only
  skeleton row + run `26414398902` preserved unchanged as historical proof.
* [`packages/expansions/gpio_expander_sx1509.yaml`](packages/expansions/gpio_expander_sx1509.yaml)
  and [`packages/expansions/fan_12v_pwm.yaml`](packages/expansions/fan_12v_pwm.yaml)
  — added LEGACY / SUPERSEDED banners recording the **kept-with-reason**
  retirement disposition (no live binder, but read by tests and forbidden from
  global removal by `S360-100-NATIVE-FAN-GPIO-MAP-001`).
* [`tests/test_pwm_product_readiness.py`](tests/test_pwm_product_readiness.py)
  and [`tests/test_native_fan_gpio_map.py`](tests/test_native_fan_gpio_map.py)
  — updated to assert the migrated native composition (the bundle composes the
  native package, mirrors the native validated-full-compile skeleton, and no
  longer carries the legacy SX1509 banner).
* [`docs/pre-hardware-prep-plan.md`](docs/pre-hardware-prep-plan.md) — slice #1
  marked **DONE** (§5.3 executed-note + §7 table).
* This `UPCOMING_PR.md` entry.

### Retirement disposition (PRODUCT-DEP-001)

No SX1509 package is deleted. `fan_pwm.yaml` / `fan_pwm_sx1509.yaml` stay bound
by the preserved legacy compile-only skeleton (historical SX1509 compile proof,
required by `tests/test_native_fanpwm_yaml.py`); `gpio_expander_sx1509.yaml` and
`fan_12v_pwm.yaml` have no live `!include` binder but are read directly by
`tests/test_core_abstract_bus.py` / `tests/test_dac_product_readiness.py` and
may not be removed globally per `S360-100-NATIVE-FAN-GPIO-MAP-001`. All four are
therefore **kept-with-reason** with legacy/superseded banners; a hard delete is
left to a future cleanup PR once the doc/test references are also retired.

### Guardrails (explicitly NOT changed)

* Release-One (`Ceiling-POE-VentIQ-RoomIQ`) byte-identical — it uses no SX1509
  and no fan package; `tests/test_release_one_entity_names.py` passes untouched.
* No fan board verified / promoted; all stay `hardware-pending` / unverified
  (design-complete only). `S360-311` `schematic_status` stays
  `cataloged_unverified`.
* No WebFlash exposure, no `artifact_name`, no `webflash_build_matrix` flip, no
  `config/webflash-builds.json` row; FanPWM token stays absent.
* No PWM current/thermal evidence claimed; `PWM-6` / `PWM-13` stay owed;
  `rpm_supported` stays false.
* FanTRIAC stays `blocked` / `HW-005`; its SX1509 blocker-explanation comments
  are factual and left intact.
* No edit to `manifest.json` / `firmware/sources.json` (absent here); the
  WebFlash repo is untouched; no compile result fabricated.

### Validation

* `python3 tests/validate_configs.py`
* `python3 scripts/validate_compile_targets.py --metadata-only`
* `python3 tests/test_native_fanpwm_yaml.py`
* `python3 tests/test_pwm_product_readiness.py`
* `python3 tests/test_release_one_entity_names.py`
* `python3 tests/test_product_substitutions.py`
* `python3 -m unittest discover -s tests -p "test_*.py"` (1175 tests, 3 skipped)

---

## HW-SENSOR-SFA40-CORRECTION-001 — correct AirIQ HCHO sensor from SFA30 to SFA40

**Status:** metadata / docs-only (corrects a recorded part identity; promotes
nothing, verifies nothing, no gate closed, no `schematic_status` or lifecycle
flipped, no entity added)

### Summary

Corrects the formaldehyde / HCHO sensor identity on the `S360-210` AirIQ from
**SFA30** to **SFA40** — the newer Sensirion HCHO module the operator confirms
is the fitted / intended part — across the catalog, the feature/entity matrix
(JSON + MD), and the AirIQ board / readiness docs. The HCHO entity still does
**not** exist and stays gated; the SFA40 connector interface/address (bus, I²C
address, ESPHome driver) remains **verify-pending** in the AirIQ pin-map and is
not asserted here. This part-identity fix re-points the queued
`ENTITY-FILL-210-HCHO-001` fill slice at the correct sensor.

### What changed

* [`config/hardware-catalog.json`](config/hardware-catalog.json) — `S360-210`
  description connector list now reads `SFA40 HCHO`.
* [`config/feature-entity-matrix.json`](config/feature-entity-matrix.json) —
  AirIQ board note and the HCHO row label now read `SFA40`; the HCHO row note
  records that SFA40 is the newer module superseding the SFA30, that its
  connector interface/address is verify-pending, and that
  `ENTITY-FILL-210-HCHO-001` now targets the SFA40 and still depends on
  interface confirmation.
* [`docs/feature-entity-matrix.md`](docs/feature-entity-matrix.md) — AirIQ
  headline-gaps row now reads `SFA40 HCHO` with the newer-module /
  verify-pending note.
* [`docs/hardware-catalog.md`](docs/hardware-catalog.md) — `S360-210` row
  connector list now reads `SFA40 HCHO`.
* [`docs/hardware/board-readiness-matrix.md`](docs/hardware/board-readiness-matrix.md)
  — `S360-210` Role bullet now reads `SFA40 HCHO connector`.
* This `UPCOMING_PR.md` update.

### Guardrails (explicitly NOT changed)

* No HCHO (or any) sensor entity added; no package / board / product / bundle /
  expansion YAML edited. The HCHO entity stays absent and gated.
* SFA40 bus, I²C address, and ESPHome driver are **not** asserted — marked
  verify-pending.
* No `schematic_status` flip; no lifecycle / status promotion on `S360-210` or
  any board.
* No other board's sensor labels changed.
* No edit to [`config/webflash-builds.json`](config/webflash-builds.json),
  `manifest.json`, or [`firmware/sources.json`](firmware/sources.json).
* The WebFlash repo (`sense360store/webflash`) is untouched.

### Validation

* `python3 tests/validate_configs.py`
* `python3 tests/test_product_catalog.py`
* `python3 tests/test_roadmap_status_doc.py`
* `python3 -m unittest discover -s tests -p "test_*.py"`

---

## PRE-HARDWARE-PREP-PLAN-001 — plan the design-derived readiness program

**Status:** docs-only / planning (promotes nothing, verifies nothing, resolves
nothing; no gate closed; no `schematic_status` flipped)

### Summary

Authors [`docs/pre-hardware-prep-plan.md`](docs/pre-hardware-prep-plan.md), the
design-derived readiness program that brings the six driver / PSU boards
(`S360-310` / `S360-311` / `S360-312` / `S360-320` / `S360-400` / `S360-410`)
to a **design-complete** state from the schematic PDFs the repo already holds,
**ahead of hardware**, so the eventual bench session is pure test-and-record.
The plan defines a `design-complete` status concept that is explicitly distinct
from `verified` (firmware authored + compile-validated from design artifacts,
recorded as a doc/metadata annotation — never a `config/*.json` field — and
which **never flips `schematic_status` on its own**), enumerates the six
per-board deliverables, flags every gerber/BOM-dependent item as
**ARTIFACT-BLOCKED**, captures the operator-stated **SX1509 deprecation** as
its own early reconcile slice, fixes the per-board hardware-verification
handoff, and emits the ordered slice sequence.

### What changed

* New [`docs/pre-hardware-prep-plan.md`](docs/pre-hardware-prep-plan.md) —
  the program: `design-complete` policy + non-flip rule, per-board D1–D6
  deliverable tables, ARTIFACT-BLOCKED flags (clearance/creepage for the
  PoE `S360-410` and mains `S360-310`/`S360-320`/`S360-400` boards), the
  SX1509 reference inventory + native-GPIO resolution targets, the
  `design-complete → verified` bench handoff per board, and the ordered
  slice sequence.
* This `UPCOMING_PR.md` entry.

### Ordered slice sequence (queued; this PR authors none of them)

1. `PRE-HW-PREP-SX1509-RECONCILE-001` — re-bind the fan path to native
   ESP32-S3 GPIO; mark residual SX1509 fan refs legacy/superseded
   (coordinates with `CORE-ABSTRACT-BUS-001` + the native fan GPIO map).
2. `PRE-HW-PREP-FW-312-001` — `S360-312` DAC (native I²C, no SX1509 dep).
3. `PRE-HW-PREP-FW-311-001` — `S360-311` PWM (native re-bind; `PACKAGE-PWM-001`).
4. `PRE-HW-PREP-FW-310-001` — `S360-310` Relay (SELV logic side).
5. `PRE-HW-PREP-TESTMATRIX-SELV-001` — finalise the SELV bench matrices.
6. `PRE-HW-PREP-GERBER-REVIEW-001` *(ARTIFACT-BLOCKED)* — clearance/creepage
   reviews; **gated on gerbers + BOM being committed**.
7. `PRE-HW-PREP-TRIAC-320-001` *(HW-005 / COMPLIANCE-001)*.
8. `PRE-HW-PREP-MAINS-400-001` *(COMPLIANCE-001)*.
9. `PRE-HW-PREP-POE-410-001` *(isolation / Hi-pot; `PACKAGE-POE-410-001`)*.

### Guardrails (explicitly NOT changed)

* No YAML, package, board, bundle, expansion, or product file edited.
* No `config/*.json` changed — `S360-310/311/312/320/400/410` stay
  `cataloged_unverified`, no `schematic_file`, no config string, artifact
  name, or lifecycle touched.
* No `schematic_status` flip; nothing marked `verified` or
  design-complete-as-verified; nothing promoted.
* No WebFlash exposure / release; no edit to
  [`firmware/sources.json`](firmware/sources.json) or `manifest.json`.
* The SX1509 reconciliation is **planned only**, not performed; no GPIO
  numbers invented beyond schematic-printed values.
* No gerbers / BOM / measurement fabricated; the WebFlash repo is untouched.

### Validation

* `python3 tests/validate_configs.py`
* `python3 tests/test_roadmap_status_doc.py`
* `python3 -m unittest discover -s tests -p "test_*.py"`

---

## HW-PINMAP-311-FOLLOWUP — standalone schematic-backed reference doc for S360-311 PWM

**Status:** docs-only (records, resolves nothing; no gate closed; board package still gated)

### Summary

Authors the standalone schematic-backed hardware reference doc for the
Sense360 PWM board (`S360-311-R4`) at
[`docs/hardware/s360-311-r4-fanpwm.md`](docs/hardware/s360-311-r4-fanpwm.md),
sourced **only** from the already-committed module-side schematic PDF
[`docs/hardware/schematics/S360-311-R4.pdf`](docs/hardware/schematics/S360-311-R4.pdf)
(HW-ASSETS-003; SHA256 `c910b3364be1d58fc44d12b5a189dade47efddf6cae158a86577ec7501e48006`).
It transcribes the connector and pin map exactly as the schematic shows
(`J3` 13-pin "From Core"; the four fan outputs `J1` / `J2` / `J4` / `J5`;
the Nextion `J6`; mounting holes `H1..H4`; the MT3608 boost) and records
every open reconciliation question as **STILL OWED**. Per
[`docs/cleanup-audit.md`](docs/cleanup-audit.md) the reconciliation itself
needs silkscreen, harness, and bench evidence plus the systemic Core
abstract-bus resolution, none of which this PR performs.

### What changed

* New `docs/hardware/s360-311-r4-fanpwm.md` — the standalone reference doc.
* `docs/hardware/s360-311-r4-pwm.md` — added a See-also cross-link to the
  new reference doc (no other section rewritten; status row unchanged).
* `docs/hardware/board-readiness-matrix.md` — replaced the "still no
  standalone reference doc" note in the `S360-311` subsection with a link
  to the new doc, and added a See-also entry. `S360-311` classification
  (`partially-documented`, `not-needed-for-release-one`,
  `package-yaml-pending`) is unchanged.
* This `UPCOMING_PR.md` update.

### Open reconciliation questions recorded as STILL OWED (resolved: none)

1. SX1509-expander-vs-direct-ESP32-GPIO mapping disagreement → owned by
   `CORE-ABSTRACT-BUS-001` /
   [`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3](docs/release-one-hardware-audit.md).
2. UART on `J3` pins 11 / 12 (module-side labels not in the Core `J6`
   capture).
3. `"NINE 4pin FANs"` section title vs four visible outputs
   (`J1` / `J2` / `J4` / `J5`).
4. Single-channel-vs-four-channel canonical abstraction for the `FanPWM`
   token (`PACKAGE-PWM-001`).

Each records the evidence (silkscreen, harness, bench waveforms) that
would close it. The reconciliation and the S360-311 board-package
promotion **remain gated** on that owed evidence.

### Guardrails (explicitly NOT changed)

* No edit to `config/hardware-catalog.json` (`S360-311` stays
  `cataloged_unverified`, no `schematic_file`),
  `config/product-catalog.json`, `config/webflash-builds.json`, or
  `config/webflash-compatibility.json`.
* No `schematic_status` flip; no `verified` / `pin-map-confirmed` mark.
* No package YAML edited (`fan_pwm.yaml`, `sense360_fan_pwm.yaml`,
  `gpio_expander_sx1509.yaml`, `sense360_core*.yaml` all unchanged).
* No product YAML, WebFlash wrapper, build entry, release, tag, or import
  added; no firmware regenerated.
* Release-One, the LED preview path, and FanTRIAC (`blocked` / `HW-005`)
  are unchanged; `S360-320` / `S360-400` compliance is unchanged.
* The schematic PDF and the curated artifact index
  (`docs/hardware/artifacts/S360-311-R4.md`) are not edited.
* The WebFlash repo (`sense360store/webflash`) is untouched.

### Validation

* `python3 tests/validate_configs.py`
* `python3 tests/test_roadmap_status_doc.py`
* `python3 -m unittest discover -s tests -p "test_*.py"`

---

## PRODUCT-DEP-CORE-001 — retire non-template legacy core-c/v/w configs

**Status:** retired (14 legacy `sense360-core-*` configs moved to `removed`; 5 kept as live authoring templates)

### Summary

Executes the `core-c` / `core-v` / `core-w` disposition recommended in
[`docs/v1-r4-product-gap.md`](docs/v1-r4-product-gap.md) (§"`core-c` / `core-v`
/ `core-w` disposition"), the deprecation-series sibling of
`PRODUCT-DEP-MINI-001`. Of the 19 legacy `sense360-core-*` `legacy-compatible`
entries, the **14** with no R4-v1 reuse are retired through the
`PRODUCT-DEP-001` `legacy-compatible -> removed` (intentional-retirement)
transition — the same path the Mini range used; no `deprecated` step is needed
because these were never WebFlash-shippable and never appeared in
`config/webflash-builds.json`. The **5** ceiling Core bases / sensor stacks that
the gap doc flags as authoring templates for not-yet-authored `V1-R4-CREATE-*`
configs stay `legacy-compatible`; their retirement is **deferred** to land with
the CREATE config they template.

### KEEP / RETIRE split (from the gap-doc template-source table)

**KEEP-as-template (5, stay `legacy-compatible`, annotated; retirement deferred):**

* `sense360-core-c-poe` — ceiling + PoE base → templates V1-R4-CREATE-002 / 003.
* `sense360-core-c-usb` — ceiling + USB base → templates V1-R4-CREATE-005 / 006.
* `sense360-core-ceiling` — full AirIQ stack → templates V1-R4-CREATE-002 / 005.
* `sense360-core-ceiling-bathroom` — VentIQ-intent stack → templates V1-R4-CREATE-006
  (V1-R4-CREATE-004 already authored).
* `sense360-core-ceiling-presence` — presence(+LED) stack → templates
  V1-R4-CREATE-003 / 006 (V1-R4-CREATE-001 / 004 already authored).

**RETIRE (14, moved to `removed` tombstones; product YAMLs deleted):**

* mains: `sense360-core-c-pwr`.
* wall (5): `sense360-core-w-poe`, `-w-pwr`, `-w-usb`, `sense360-core-wall`,
  `sense360-core-wall-presence`.
* voice (8): `sense360-core-v-c-poe`, `-v-c-pwr`, `-v-c-usb`, `-v-w-poe`,
  `-v-w-pwr`, `-v-w-usb`, `sense360-core-voice-ceiling`,
  `sense360-core-voice-wall`.

The two standalone legacy entries (`sense360-fan-pwm`, `sense360-poe`) are
**outside** `PRODUCT-DEP-CORE-001` scope and stay `legacy-compatible`.

### What changed

* `config/product-catalog.json`: the 14 RETIRE rows flip
  `legacy-compatible -> removed` with `removed_since: 2026-05-30`,
  `removal_reason` ("Superseded by R4 product line; not an R4 config and not a
  live authoring template." + the `legacy-compatible -> removed` transition
  note), a per-family `no_replacement_reason`, and tombstone `notes`; each drops
  `product_yaml` (tombstone contract, exactly as the Mini entries). The 5 KEEP
  rows keep `status: legacy-compatible` and gain a template-retention annotation
  in `notes`.
* `products/`: the 14 RETIRE `sense360-core-*.yaml` files are removed.

### Guardrails (explicitly NOT changed)

* No KEEP-as-template config retired; their lifecycle is unchanged.
* No shared package under `packages/` deleted — the legacy core configs
  referenced core/board/expansion packages that R4 still uses; only the legacy
  product YAMLs and their catalog rows are retired.
* No touch to the 6 R4 configs, the 2 USB configs, or the 10 Mini tombstones.
* No edits to `config/webflash-builds.json`, `manifest.json`, or
  `firmware/sources.json`; no board `schematic_status` change; nothing promoted.
* `v1.0.0` is untouched — it keeps the legacy files for tag-pinned field units.
* No new tests and no test assertions weakened: the `packages/`-level package
  tests (`test_core_abstract_bus.py`) and the auto-discovering
  `test_product_substitutions.py` / `generate_test_configs.py` reference shared
  packages (which survive) and discover product YAMLs dynamically, so the suite
  passes with the RETIRE set gone with no test edits.

### Deferred work

The KEEP-as-template set's retirement is **deferred**: each of the 5 retained
configs is retired in the PR that authors its last templated `V1-R4-CREATE-*`
config (CREATE-002 / 003 / 005 / 006), through the same
`legacy-compatible -> removed` transition used here.

### Validation

* `python3 tests/validate_configs.py`
* `python3 tests/test_product_catalog.py`
* `python3 tests/test_product_substitutions.py`
* `python3 tests/test_core_abstract_bus.py`
* `python3 tests/test_all_yaml_release_matrix.py`
* `python3 -m unittest discover -s tests -p "test_*.py"`

---

## V1-R4-CREATE-004 — author USB sensor variants (Ceiling-USB-VentIQ-RoomIQ, Ceiling-USB-RoomIQ)

**Status:** authored (manual / custom channel; compile-validation pending-ci; no WebFlash promotion)

### Summary

This change authors the two unblocked R4 USB sensor configs from
[`docs/v1-r4-product-gap.md`](docs/v1-r4-product-gap.md) (V1-R4-CREATE-004),
each as a config-string-named bundle + thin compat shim + catalog row composed
from the `packages/boards/` layer:

* `Ceiling-USB-VentIQ-RoomIQ` — Core(ceiling) + USB-C power + S360-211 VentIQ +
  S360-200 RoomIQ (the USB power-axis variant of the WebFlash-shipping
  `Ceiling-POE-VentIQ-RoomIQ`, PoE PSU board swapped for the USB-C power package).
* `Ceiling-USB-RoomIQ` — Core(ceiling) + USB-C power + S360-200 RoomIQ (the USB
  power-axis variant of the authored `Ceiling-POE-RoomIQ`).

These are **manual / custom** firmwares available for manual ESPHome / GitHub
use, **NOT** WebFlash-exposed. USB variants carry **no PoE PSU board** (no
S360-410); all three boards (S360-100, S360-211, S360-200) are
`schematic_status: verified` and there is **no evidence blocker**.

### What changed

* New bundles `products/bundles/ceiling-usb-ventiq-roomiq.yaml` and
  `products/bundles/ceiling-usb-roomiq.yaml` (full configs composed from the
  board packages + `packages/hardware/power_usb.yaml` + base tier + the same
  behaviour profiles the PoE sensor bundle uses).
* New compat shims `products/sense360-ceiling-usb-ventiq-roomiq.yaml` and
  `products/sense360-ceiling-usb-roomiq.yaml` (each does nothing but `!include`
  its bundle, per §3.2).
* `config/product-catalog.json`: two rows, `status: compile-only`,
  `target_channel: manual-custom`, `webflash_build_matrix: false`, no
  `artifact_name`, no `webflash_wrapper`, no kit preset.
* `config/compile-only-targets.json`: two top-level targets
  (`ceiling-usb-ventiq-roomiq-product-compile-only`,
  `ceiling-usb-roomiq-product-compile-only`), `compile_validation_status:
  pending-ci`.
* `config/compile-only-candidates.json`,
  `config/firmware-combination-matrix.json` (regenerated;
  `compile-only-candidate`), `docs/firmware-build-gap-report.md` (regenerated),
  `docs/product-readiness-matrix.md`, `docs/all-yaml-release-matrix.md`, and
  `docs/v1-r4-product-gap.md` (CREATE-004 marked authored) updated to match.

### Guardrails (explicitly NOT changed)

* No edits to `config/webflash-builds.json`, `firmware/sources.json`, or
  `manifest.json`.
* No `artifact_name`; no `webflash_build_matrix` flip; no kit preset; no
  WebFlash wrapper / exposure.
* No PoE PSU (no S360-410) in these USB variants.
* No board `schematic_status` change; LED not marked stable; S360-410 not marked
  verified; nothing preview-promoted or claimed as a kit.
* No compile result fabricated (ESPHome unavailable in the authoring
  environment; a CI `--compile` run is owed).

### Queue status (maintenance rule)

`V1-R4-CREATE-004` delivers the unblocked non-LED USB pair. The remaining
`V1-R4-CREATE-*` slices stay **queued behind their gates**:

* **V1-R4-CREATE-002** — `Ceiling-POE-AirIQ-RoomIQ` (S360-410 + AirIQ-stack
  evidence-gated).
* **V1-R4-CREATE-003** — `Ceiling-POE-RoomIQ-LED` (LED preview gauntlet;
  S360-410-gated).
* **V1-R4-CREATE-005** — `Ceiling-USB-AirIQ-RoomIQ` (AirIQ-stack evidence-gated).
* **V1-R4-CREATE-006** — `Ceiling-USB-VentIQ-RoomIQ-LED`,
  `Ceiling-USB-RoomIQ-LED` (LED preview-gated).

### Validation

* `python3 tests/validate_configs.py`
* `python3 scripts/validate_compile_targets.py --metadata-only`
* `python3 tests/test_product_catalog.py`
* `python3 tests/test_all_yaml_release_matrix.py`
* `python3 tests/test_product_substitutions.py`
* `python3 tests/test_release_one_entity_names.py`
* `python3 tests/validate_webflash_builds.py`
* `python3 -m unittest discover -s tests -p "test_*.py"`

### Retained cross-references (maintenance)

The module-side pinmap ledger `MODULE-PINMAPS-GDRIVE-001` and the canonical Core
connector pin map [`docs/hardware/s360-100-core-connector-pin-map.md`](docs/hardware/s360-100-core-connector-pin-map.md)
are unchanged by this slice and remain the source of truth for the S360-100
ceiling Core bus that the USB variants bind.

---

## ROOM-BUNDLE-FAN-VARIANTS-001 — Planning-only fan-control variants (Bathroom & Kitchen)

**Status:** planning-only (no firmware release, no WebFlash promotion)

### Summary

This change adds a planning-only proposal for optional fan-control variants of the
Bathroom and Kitchen PoE room bundles. The base room bundles remain the primary
product line. The fan variants are Bathroom/Kitchen-only add-ons and are captured
in a separate config file (Option A) so the stable room-bundle matrix stays clean.

### What changed

* New `config/room-bundle-fan-variants.json` describing five planning variants:
  * `S360-KIT-BATH-P-REL` (relay)
  * `S360-KIT-BATH-P-DAC` (0-10V DAC)
  * `S360-KIT-BATH-P-PWM` (PWM)
  * `S360-KIT-KITCHEN-P-DAC` (0-10V DAC)
  * `S360-KIT-KITCHEN-P-REL` (relay)
* New docs section in `docs/sense360-room-bundles.md` with the variant table and prose.
* New contract test `tests/test_room_bundle_fan_variants.py`.
* This `UPCOMING_PR.md` update.

### Guardrails (explicitly NOT changed)

* No edits to `webflash-builds.json`, `sources.json`, or `manifest.json`.
* No `artifact_name` fields anywhere.
* No `webflash_build_matrix` flip.
* No LED/fan-driver stable promotion.
* No TRIAC variant.
* No Corridor/Living/Bedroom fan variant.
* No existing bundle SKU or lifecycle changed.

### Validation

* `python3 -m unittest discover -s tests -p "test_*.py"` (1163 tests, 3 skipped).
* `validate_configs.py`.
* Per-test scripts for the new contract test.

### Variants

| Variant SKU | Base bundle | Room | Fan control |
| --- | --- | --- | --- |
| S360-KIT-BATH-P-REL | S360-KIT-BATH-P | Bathroom | relay |
| S360-KIT-BATH-P-DAC | S360-KIT-BATH-P | Bathroom | dac_0_10v |
| S360-KIT-BATH-P-PWM | S360-KIT-BATH-P | Bathroom | pwm |
| S360-KIT-KITCHEN-P-DAC | S360-KIT-KITCHEN-P | Kitchen | dac_0_10v |
| S360-KIT-KITCHEN-P-REL | S360-KIT-KITCHEN-P | Kitchen | relay |

### Notes

* relay vs DAC(0-10V) vs PWM are not runtime-interchangeable; each is a separate SKU.
* Bundle SKUs are kept separate from firmware config strings.
* Kitchen fan control is framed as extract/MVHR/EC boost, not a cooker-hood replacement.
* No variant is exposed to WebFlash.

### Next steps

* A future implementation PR would define firmware configs, build artifacts, and
  validation before any WebFlash promotion.

---

_Previous entries below this line are historical and unchanged._

## (historical placeholder)

Earlier planning notes are intentionally omitted from this excerpt.

(end)

## Historical: ROOM-BUNDLE-MATRIX baseline

The room-bundle matrix (Corridor, Living, Bedroom, Bathroom, Kitchen) across PoE and
USB power options remains the stable, released baseline. This planning entry does not
modify that matrix; it only proposes additive Bathroom/Kitchen fan variants for a
future PR.

* Corridor: S360-KIT-CORR-P / S360-KIT-CORR-U
* Living: S360-KIT-LIV-P / S360-KIT-LIV-U
* Bedroom: S360-KIT-BED-P / S360-KIT-BED-U
* Bathroom: S360-KIT-BATH-P / S360-KIT-BATH-U
* Kitchen: S360-KIT-KITCHEN-P / S360-KIT-KITCHEN-U

* Base bundles remain the main product line; fan variants are add-ons.
* No bundle SKU or lifecycle is changed by this planning entry.

(end of file)

<!-- planning-only; no firmware release implied -->

<!-- ROOM-BUNDLE-FAN-VARIANTS-001 -->

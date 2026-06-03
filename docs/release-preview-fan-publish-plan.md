# Manual-preview fan firmware publish plan — pre-run record

**Canonical id:** `RELEASE-PREVIEW-FAN-PUBLISH-PLAN-001`
**Date:** 2026-06-03
**Type:** Plans the actual publication of the **three buildable manual-preview
fan-control** firmware targets **before** any release workflow is run or any
artifact is published. This PR **verifies inputs, artifact names, release-note
drafts, compile evidence, commercial posture, and the workflow/publish path**,
finds that the existing release workflow **cannot** publish manual-preview fan
targets, and **queues** the workflow work (`RELEASE-PREVIEW-FAN-PUBLISH-WORKFLOW-001`)
and the eventual run (`RELEASE-PREVIEW-FAN-PUBLISH-RUN-001`). It is **planning
only**: it **publishes no firmware**, runs **no** workflow, creates **no** GitHub
Release / tag / checksum, commits **no** `.bin`, writes **no** `manifest.json` /
`firmware/sources.json`, touches **no** WebFlash repo, adds **no**
`config/webflash-builds.json` row, marks **nothing** stable / recommended /
default / buyable, changes Simple install / the launch SKU **`S360-KIT-BATH-P`**
**not at all**, and claims **no** hardware / bench / compliance proof.

> **Superseded release vehicle — shared preview tag
> (`RELEASE-PREVIEW-FAN-SHARED-TAG-001`).** This plan originally anticipated a
> *dedicated* `v1.0.0-manual-preview-fans` release vehicle kept separate from the
> WebFlash `v1.0.0-preview` release (§3.3 / §3.4). That dedicated-tag concept has
> since been **retired**: `v1.0.0-preview` is now the single **shared** preview
> release for **all** preview firmware artifacts — room-bundle, LED, and the
> FanRelay / FanPWM / FanDAC manual-preview artifacts. The workflow / publish-path
> gap analysis below still stands; only the release-vehicle expectation changed,
> and §3.3 / §3.4 are updated to the shared tag. WebFlash import eligibility stays
> controlled separately by WebFlash import policy and is never implied by presence
> in the shared release.

**Predecessors:**

- `#702` `RELEASE-PREVIEW-UNBLOCK-ALL-BUNDLES-001` made hardware / bench /
  compliance / commercial blockers **stable-only** for preview, so every
  buildable target (the three fan drivers included) is preview-eligible; only a
  genuine buildability blocker (`HW-005` for TRIAC) can stop a preview cut
  ([`docs/release-channel-policy.md`](release-channel-policy.md)).
- `#703` `RELEASE-PREVIEW-FAN-TRIAC-BUILD-ROWS-001` added the non-WebFlash
  build-row ledger [`config/preview-fan-triac-build-rows.json`](../config/preview-fan-triac-build-rows.json)
  and the validated preview release-note drafts under
  [`docs/release-notes/manual-preview/`](release-notes/manual-preview/)
  ([`docs/release-preview-fan-triac-build-rows.md`](release-preview-fan-triac-build-rows.md)).
- `#695` `RELEASE-PREVIEW-COMPILE-RESULTS-001` recorded hosted compile run
  [`26821900127`](https://github.com/sense360store/esphome-public/actions/runs/26821900127)
  as GREEN **firmware-build proof only** for the three fan drivers
  ([`docs/release-preview-compile-dryrun.md`](release-preview-compile-dryrun.md)).

---

## TL;DR

* **Scope is exactly three manual-preview fan artifacts** —
  `Ceiling-POE-VentIQ-FanRelay-RoomIQ`, `Ceiling-POE-FanPWM`, and
  `Ceiling-POE-FanDAC` — the three **buildable** `delivery_lane: manual-preview`
  rows in [`config/preview-fan-triac-build-rows.json`](../config/preview-fan-triac-build-rows.json).
  Each is preview-channel, build-row-backed, release-note-drafted, and
  firmware-build-compile-validated by run `26821900127`.
* **TRIAC is out of scope.** `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` is
  **build-blocked by `HW-005`** — not buildable end-to-end, so no compile /
  firmware artifact exists and **none is planned here**. It is the fourth row of
  the ledger but the `advanced-manual-preview` lane and stays excluded from this
  publish plan.
* **There is a workflow/publish-path GAP (this is the important finding).** The
  existing release workflow
  [`firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)
  generates its matrix **exclusively** from `config/webflash-builds.json`,
  filtered by `version` + `channel`. The fan-token guardrail keeps fan tokens
  **out** of `config/webflash-builds.json`, so **the release workflow cannot
  publish the fan preview artifacts**. The manual lane
  [`manual-firmware-artifacts.yml`](../.github/workflows/manual-firmware-artifacts.yml)
  *compiles* the three fans but is **explicitly non-release** (it names artifacts
  `<stem>-manual-<sha>-nonrelease`, uploads only **expiring** 7-day CI artifacts,
  creates no Release, and produces no durable `-vX.Y.Z-preview.bin`). **Neither
  existing workflow can durably publish these artifacts.**
* **The fix is a queued workflow PR, not a hack.** This plan **does not** add
  fan rows to `config/webflash-builds.json` (policy forbids it) and **does not**
  run anything. It queues `RELEASE-PREVIEW-FAN-PUBLISH-WORKFLOW-001` to add a
  manual-preview publication path, then `RELEASE-PREVIEW-FAN-PUBLISH-RUN-001` to
  execute it.
* **Nothing becomes stable / recommended / default / buyable.** Simple install
  stays the stable Bathroom PoE build (`Ceiling-POE-VentIQ-RoomIQ`,
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, `S360-KIT-BATH-P`).
  WebFlash one-click import remains a strictly later, separately gated follow-up
  (`WEBFLASH-RELAY-001` / `WEBFLASH-PWM-001` / `WEBFLASH-DAC-001`).

---

## 1. The three manual-preview fan targets

Each target is published exactly as declared in
[`config/preview-fan-triac-build-rows.json`](../config/preview-fan-triac-build-rows.json)
(the manual / advanced-manual analog of `config/webflash-builds.json`) and its
manual-lane candidate in
[`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json).
Nothing below is hand-set: the publish plan reads from the build-row ledger, the
preview-target manifest, the manual-lane candidate set, the release-note drafts,
and the recorded compile evidence.

### 1.1 `Sense360-Ceiling-POE-VentIQ-FanRelay-RoomIQ-v1.0.0-preview.bin`

| Field | Value |
|---|---|
| Config string | `Ceiling-POE-VentIQ-FanRelay-RoomIQ` |
| Family / SKU | FanRelay / `S360-310` |
| Delivery lane | **`manual-preview`** |
| Channel | `preview` (build channel `preview`) |
| Build row | [`config/preview-fan-triac-build-rows.json`](../config/preview-fan-triac-build-rows.json) → `rows[]` `Ceiling-POE-VentIQ-FanRelay-RoomIQ` |
| Product YAML | `products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml` |
| Manual artifact row | [`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json) → candidate `fanrelay` |
| Release-note draft | [`docs/release-notes/manual-preview/ceiling-poe-ventiq-fanrelay-roomiq.md`](release-notes/manual-preview/ceiling-poe-ventiq-fanrelay-roomiq.md) (validated `--channel preview`) |
| Compile evidence | run `26821900127` (`Preview Compile Dry-Run`, `workflow_dispatch` / `compile_mode=full`, 2026-06-02, ESPHome 2026.4.5; job `Compile Dry-Run: Ceiling-POE-VentIQ-FanRelay-RoomIQ`, job run `79078546242`, result `success`, `proof_class: firmware-build-only`) |
| Warning copy | `preview` — *"PREVIEW FIRMWARE — buildable and installable for testers only. This build is NOT hardware verified, NOT stable, NOT recommended, and NOT a customer default. No bench evidence and no compliance is claimed. Flash at your own risk and expect to recover with the rescue/stable firmware."* (plus the relay/mains competent-person caveat in the draft) |
| Stable blocker | Mains-safety / installation-approval / creepage / clearance evidence + competent-person sign-off + GPIO3 strap-pin boot characterisation. |
| Commercial posture | **hidden / candidate / not buyable**; not recommended; not customer default; not stable; not a required config |
| Hardware / compliance proof | **none claimed** — firmware-build proof only |
| Expected output file name | `Sense360-Ceiling-POE-VentIQ-FanRelay-RoomIQ-v1.0.0-preview.bin` |

### 1.2 `Sense360-Ceiling-POE-FanPWM-v1.0.0-preview.bin`

| Field | Value |
|---|---|
| Config string | `Ceiling-POE-FanPWM` |
| Family / SKU | FanPWM / `S360-311` |
| Delivery lane | **`manual-preview`** |
| Channel | `preview` (build channel `preview`) |
| Build row | [`config/preview-fan-triac-build-rows.json`](../config/preview-fan-triac-build-rows.json) → `rows[]` `Ceiling-POE-FanPWM` |
| Product YAML | `products/sense360-ceiling-poe-fanpwm.yaml` |
| Manual artifact row | [`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json) → candidate `fanpwm` |
| Release-note draft | [`docs/release-notes/manual-preview/ceiling-poe-fanpwm.md`](release-notes/manual-preview/ceiling-poe-fanpwm.md) (validated `--channel preview`) |
| Compile evidence | run `26821900127` (`Preview Compile Dry-Run`, `compile_mode=full`, 2026-06-02, ESPHome 2026.4.5; job `Compile Dry-Run: Ceiling-POE-FanPWM`, job run `79078546303`, result `success`, `proof_class: firmware-build-only`) |
| Warning copy | `preview` — *"PREVIEW FIRMWARE — buildable and installable for testers only. This build is NOT hardware verified, NOT stable, NOT recommended, and NOT a customer default. No bench evidence and no compliance is claimed. Flash at your own risk and expect to recover with the rescue/stable firmware."* |
| Stable blocker | Measured current / thermal evidence (`S360-311-CURRENT-THERMAL-001`). RPM / TachIO is not claimed (`rpm_supported: false`). |
| Commercial posture | **hidden / candidate / not buyable**; not recommended; not customer default; not stable; not a required config |
| Hardware / compliance proof | **none claimed** — firmware-build proof only |
| Expected output file name | `Sense360-Ceiling-POE-FanPWM-v1.0.0-preview.bin` |

### 1.3 `Sense360-Ceiling-POE-FanDAC-v1.0.0-preview.bin`

| Field | Value |
|---|---|
| Config string | `Ceiling-POE-FanDAC` |
| Family / SKU | FanDAC / `S360-312` |
| Delivery lane | **`manual-preview`** |
| Channel | `preview` (build channel `preview`) |
| Build row | [`config/preview-fan-triac-build-rows.json`](../config/preview-fan-triac-build-rows.json) → `rows[]` `Ceiling-POE-FanDAC` |
| Product YAML | `products/sense360-ceiling-poe-fandac.yaml` |
| Manual artifact row | [`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json) → candidate `fandac` |
| Release-note draft | [`docs/release-notes/manual-preview/ceiling-poe-fandac.md`](release-notes/manual-preview/ceiling-poe-fandac.md) (validated `--channel preview`) |
| Compile evidence | run `26821900127` (`Preview Compile Dry-Run`, `compile_mode=full`, 2026-06-02, ESPHome 2026.4.5; job `Compile Dry-Run: Ceiling-POE-FanDAC`, job run `79078546268`, result `success`, `proof_class: firmware-build-only`) |
| Warning copy | `preview` — *"PREVIEW FIRMWARE — buildable and installable for testers only. This build is NOT hardware verified, NOT stable, NOT recommended, and NOT a customer default. No bench evidence and no compliance is claimed. Flash at your own risk and expect to recover with the rescue/stable firmware."* |
| Stable blocker | Cloudlift S12 / J3 harness + product-bench evidence; S360-312 schematic / BOM. |
| Commercial posture | **hidden / candidate / not buyable**; not recommended; not customer default; not stable; not a required config |
| Hardware / compliance proof | **none claimed** — firmware-build proof only |
| Expected output file name | `Sense360-Ceiling-POE-FanDAC-v1.0.0-preview.bin` |

Artifact names follow the contract pattern
`Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin`, identical to the
`expected_preview_artifact_name` recorded for each row in the ledger.

---

## 2. Expected artifacts

The publish run (once the workflow path exists — see §3) must produce **exactly**
these three durable preview binaries and **no others** from this plan:

1. `Sense360-Ceiling-POE-VentIQ-FanRelay-RoomIQ-v1.0.0-preview.bin`
2. `Sense360-Ceiling-POE-FanPWM-v1.0.0-preview.bin`
3. `Sense360-Ceiling-POE-FanDAC-v1.0.0-preview.bin`

No `Sense360-…-FanTRIAC-…-preview.bin` is in scope (TRIAC is build-blocked by
`HW-005`; see §4). The stable Simple-install artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` is **unchanged** and is
**not** re-published by this plan.

---

## 3. Workflow / publish-path verification — and the GAP

This is the heart of the plan. The task asks: *can the existing firmware release
workflow publish these manual-preview fan targets?* The answer, verified against
the live config and workflows, is **no** — and this section documents exactly why
and what the fix is.

### 3.1 The release workflow publishes only `config/webflash-builds.json` rows

[`firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)
generates its build matrix **exclusively** from `config/webflash-builds.json`
(the `Generate product build matrix` step reads `config/webflash-builds.json` and
filters by `version` + `channel`; on a real `release` event the
`workflow_dispatch`-only `release_target` picker is ignored). The fan-token
guardrail in [`scripts/list_release_targets.py`](../scripts/list_release_targets.py)
(`FAN_FAMILY_TOKENS = ("FanRelay", "FanPWM", "FanDAC")`) — mirrored in
[`scripts/plan_room_release_notes.py`](../scripts/plan_room_release_notes.py) —
**refuses** any fan token in the release matrix, and the catalog keeps
`webflash_build_matrix: false` for the fan products. So:

| Claim | Result |
|---|---|
| The three fan configs are in `config/webflash-builds.json` | ❌ **No.** The ledger holds `Ceiling-POE-VentIQ-RoomIQ` (stable) + four preview WebFlash rows; **no fan / TRIAC row**. |
| The release workflow can scope to a fan target | ❌ **No.** `release_target` picker options carry **no** fan token; `scripts/list_release_targets.py --validate Ceiling-POE-FanPWM` exits non-zero ("not a selectable release target"). |
| Replaying the matrix filter at `(version=1.0.0, channel=preview)` yields a fan artifact | ❌ **No.** It yields only the four WebFlash preview rows; **no fan config**. |
| Therefore the release workflow can publish a fan `-preview.bin` | ❌ **No — this is the gap.** |

### 3.2 The manual lane compiles fans but is explicitly non-release

[`manual-firmware-artifacts.yml`](../.github/workflows/manual-firmware-artifacts.yml)
(`MANUAL-FIRMWARE-CI-ARTIFACTS-001`) *does* compile FanRelay / FanPWM / FanDAC
from [`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json),
but it is the **non-release, expiring CI job** by construction:

| Property | Value | Consequence |
|---|---|---|
| `release` / `webflash` / `release_channel` | `false` / `false` / `null` | Never creates a GitHub Release; never a release channel. |
| Artifact name pattern | `{product_stem}-manual-{short_sha}-nonrelease` | **Not** a durable `Sense360-…-v1.0.0-preview.bin`. |
| Upload | `actions/upload-artifact` with `retention-days: 7` | **Expiring** CI artifact only — not a durable release asset. |
| Side effects | none (no `firmware/sources.json` / `manifest.json` / committed `.bin`) | Point-to-point operator handoff only. |

So the manual lane **cannot** produce the durable, release-named preview `.bin`
the publish plan needs either.

### 3.3 Conclusion + queued workflow PR

**There is no existing workflow that can durably publish the three manual-preview
fan artifacts** under their release names. Per the task's explicit instruction
("If existing workflow only publishes `config/webflash-builds.json` rows, document
that gap and queue a workflow PR to support manual-preview artifacts. Do not hack
fan targets into `config/webflash-builds.json` unless policy explicitly changes."):

* **This plan does NOT add fan rows to `config/webflash-builds.json`.** That file
  stays the sole WebFlash release-eligibility source of truth; the fan-token
  guardrail stays intact.
* **A workflow PR is queued: `RELEASE-PREVIEW-FAN-PUBLISH-WORKFLOW-001`.** It must
  add a **manual-preview publication path** that reads the manual-preview rows
  from `config/preview-fan-triac-build-rows.json` /
  `config/manual-firmware-artifacts.json` (NOT `config/webflash-builds.json`),
  builds the three fan product YAMLs, renames each output to its
  `expected_preview_artifact_name`, and attaches the three durable
  `-v1.0.0-preview.bin` artifacts to the **shared `v1.0.0-preview` preview
  release** — the single preview release for all preview artifacts
  (`RELEASE-PREVIEW-FAN-SHARED-TAG-001`). WebFlash import eligibility stays
  controlled separately by WebFlash import policy, so a fan artifact in the shared
  release is never implied to be WebFlash-importable. TRIAC must stay excluded
  (`HW-005`).
* **Then `RELEASE-PREVIEW-FAN-PUBLISH-RUN-001`** executes that workflow.

### 3.4 Tag / channel / version expectations for the future workflow

When `RELEASE-PREVIEW-FAN-PUBLISH-WORKFLOW-001` + `RELEASE-PREVIEW-FAN-PUBLISH-RUN-001`
land, the publish must use:

| Expectation | Value |
|---|---|
| Version | `1.0.0` |
| Channel / build channel | `preview` / `preview` |
| Delivery lane | `manual-preview` (FanRelay / FanPWM / FanDAC) |
| Artifact names | the three `expected_preview_artifact_name` values in §1 / §2 |
| Source of truth for the matrix | `config/preview-fan-triac-build-rows.json` (+ `config/manual-firmware-artifacts.json`), **not** `config/webflash-builds.json` |
| Release vehicle | the shared `v1.0.0-preview` preview release (`RELEASE-PREVIEW-FAN-SHARED-TAG-001`); **must not** reuse the WebFlash build matrix or imply WebFlash import — import eligibility stays controlled separately by WebFlash import policy |
| Excluded | `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` (`HW-005`); the stable Bathroom build; every WebFlash one-click import |

---

## 4. What is proven (and what is not)

* **Proven (firmware-build only):** the canonical product YAML for each of the
  three fan targets compiled GREEN on hosted CI in Preview Compile Dry-Run run
  [`26821900127`](https://github.com/sense360store/esphome-public/actions/runs/26821900127)
  (2026-06-02, ESPHome 2026.4.5); each release-note draft validates structurally
  against the WebFlash release-body contract (`--channel preview`); and each row's
  artifact name follows the `Sense360-{config}-v{version}-{channel}.bin` contract.
* **Not proven / not claimed:** any FanTRIAC compile (build-blocked by `HW-005`),
  hardware operation, bench verification, a verified schematic, electrical /
  mains-safety / EMC compliance, commercial availability, or any stable-promotion
  readiness. Stable stays gated per target — mains-safety / installation-approval
  + competent-person sign-off + GPIO3 strap-pin characterisation (FanRelay);
  measured current / thermal (FanPWM); Cloudlift S12 / J3 harness + S360-312
  schematic (FanDAC). A validated plan is **not** a published artifact.

---

## 5. Out of scope (explicit)

| Item | Status / reason |
|---|---|
| `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` | **Excluded** — build-blocked by `HW-005` (S360-320 schematic uncommitted; GPIO5/GPIO6 collide with RoomIQ J10 nets; `ac_dimmer` cannot run across the SX1509 expander). No compile / firmware artifact exists; none is planned. Stays `advanced-manual-preview`. |
| Any stable / full release | **Excluded** — nothing here is promoted to stable; the stable channel stays evidence-gated. |
| Any WebFlash import | **Excluded** — fan WebFlash one-click import is a strictly later, separately gated follow-up (`WEBFLASH-RELAY-001` / `WEBFLASH-PWM-001` / `WEBFLASH-DAC-001`); no fan row is added to `config/webflash-builds.json`. |
| Any Simple-install exposure | **Excluded** — Simple install stays the stable Bathroom PoE build only (`Ceiling-POE-VentIQ-RoomIQ`, `S360-KIT-BATH-P`). |

---

## 6. Queued follow-ups

1. **`RELEASE-PREVIEW-FAN-PUBLISH-WORKFLOW-001`** — add the manual-preview
   publication workflow path described in §3.3 / §3.4 (reads the manual-preview
   ledger, not `config/webflash-builds.json`; excludes TRIAC).
2. **`RELEASE-PREVIEW-FAN-PUBLISH-RUN-001`** — run the manual-preview publication
   for the three fan artifacts named in §1 / §2, on `version=1.0.0`,
   `channel=preview`, keeping the stable Bathroom build, TRIAC, and every WebFlash
   import out.
3. **`WEBFLASH-RELAY-001` / `WEBFLASH-PWM-001` / `WEBFLASH-DAC-001`** (even later)
   — the WebFlash-side one-click import, only once the fan warning UX supports fan
   preview exposure. Not started; not implied by this plan.
4. **FanTRIAC `HW-005`** — unchanged buildability defect; FanTRIAC stays
   `advanced-manual-preview`, build-blocked, excluded from every publish surface.

---

## 7. Guardrails — what this PR did and did NOT do

It did **not**: publish firmware; create a GitHub Release / tag / checksum;
commit any `.bin`; write `manifest.json` or `firmware/sources.json`; touch the
WebFlash repo (including its `manifest.json` / `firmware/sources.json`); add a
`config/webflash-builds.json` row for any fan / TRIAC config; add a fan target to
Simple install; include TRIAC in the publish scope; mark any target stable /
recommended / default / buyable; change Simple install or the launch SKU
`S360-KIT-BATH-P`; or claim hardware / bench / compliance proof. It edits only
this plan doc, the new test
[`tests/test_preview_fan_publish_plan.py`](../tests/test_preview_fan_publish_plan.py),
a cross-reference in
[`docs/release-preview-fan-triac-build-rows.md`](release-preview-fan-triac-build-rows.md),
and `UPCOMING_PR.md`.

---

## 8. Validation

All commands run from the repo root and pass:

| Command | Result |
|---|---|
| `python3 tests/validate_configs.py` | `✅ All configuration files are valid!` |
| `python3 scripts/validate_compile_targets.py --metadata-only` | `✅ Metadata validation passed.` |
| `python3 scripts/validate_preview_release_targets.py --metadata-only` | `✅ … validation passed.` (9 targets) |
| `python3 scripts/validate_preview_fan_triac_build_rows.py --metadata-only` | `✅ … ledger validation passed.` (4 rows) |
| `python3 tests/test_product_catalog.py` | `OK` |
| `python3 tests/validate_webflash_builds.py` | `✅ … valid!` (no fan / TRIAC row added) |
| `python3 tests/test_preview_fan_publish_plan.py` | `OK` (this PR's guard) |
| `python3 scripts/validate-webflash-release-notes.py --channel preview docs/release-notes/manual-preview/ceiling-poe-ventiq-fanrelay-roomiq.md` | `passed` |
| `python3 scripts/validate-webflash-release-notes.py --channel preview docs/release-notes/manual-preview/ceiling-poe-fanpwm.md` | `passed` |
| `python3 scripts/validate-webflash-release-notes.py --channel preview docs/release-notes/manual-preview/ceiling-poe-fandac.md` | `passed` |
| `python3 -m unittest discover -s tests -p "test_*.py"` | `OK` |

---

## Cross-references

- Fan / TRIAC build-row ledger: [`config/preview-fan-triac-build-rows.json`](../config/preview-fan-triac-build-rows.json) · readiness record [`docs/release-preview-fan-triac-build-rows.md`](release-preview-fan-triac-build-rows.md)
- Manual-preview release-note drafts: [`docs/release-notes/manual-preview/`](release-notes/manual-preview/)
- Manual fan lane: [`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json) · [`docs/manual-install-fan-candidates.md`](manual-install-fan-candidates.md)
- Preview target manifest: [`config/preview-release-targets.json`](../config/preview-release-targets.json) · [`docs/preview-release-targets.md`](preview-release-targets.md)
- Release-channel policy: [`config/release-channel-policy.json`](../config/release-channel-policy.json) · [`docs/release-channel-policy.md`](release-channel-policy.md)
- Compile dry-run record: [`docs/release-preview-compile-dryrun.md`](release-preview-compile-dryrun.md)
- Release / build workflow: [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)
- Manual (non-release) firmware lane: [`.github/workflows/manual-firmware-artifacts.yml`](../.github/workflows/manual-firmware-artifacts.yml)
- Release-target picker helper: [`scripts/list_release_targets.py`](../scripts/list_release_targets.py)
- Release-body validator: [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py)
- WebFlash release-eligibility source of truth: [`config/webflash-builds.json`](../config/webflash-builds.json)
- Commercial source of truth: [`docs/shop-commercial-source-of-truth.md`](shop-commercial-source-of-truth.md)
- Predecessor WebFlash publish plan: [`docs/release-preview-publish-plan.md`](release-preview-publish-plan.md)

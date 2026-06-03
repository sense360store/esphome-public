# Release Matrix / WebFlash Alignment (WEBFLASH-RELEASE-MATRIX-ALIGNMENT-001)

**Canonical id:** `WEBFLASH-RELEASE-MATRIX-ALIGNMENT-001`
**Date:** 2026-05-29
**Type:** Docs only. This document does **not** change firmware behaviour,
publish firmware, build or attach any artifact, edit `manifest.json` /
`firmware/sources.json`, enable WebFlash for any fan driver, mark LED stable,
mark S360-410 verified, or move any readiness gate.

## Purpose

This is the **single reconciled view** that aligns, in one place, what the
repository can build, what it can release, what is preview-only, what is
manual-only, and what remains blocked — across the release matrix, WebFlash
exposure, firmware availability, room-bundle SKUs, release-note generation,
and the artifact pipeline.

It does **not** introduce a new source of truth. Every cell below is **read**
from a committed config, workflow, or test-backed reference doc. Where this
doc and a source-of-truth file ever disagree, **the source-of-truth file
wins** and this doc is the one to fix.

### Sources of truth (read-only inputs)

| Layer | Source of truth |
|---|---|
| Release-eligibility (sole source) | [`config/webflash-builds.json`](../config/webflash-builds.json) → [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py) |
| Release build/publish workflow | [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml) |
| Product lifecycle / hardware status | [`config/product-catalog.json`](../config/product-catalog.json) → [`tests/test_product_catalog.py`](../tests/test_product_catalog.py) |
| Compile-only validation lane | [`config/compile-only-targets.json`](../config/compile-only-targets.json) + [`.github/workflows/compile-only.yml`](../.github/workflows/compile-only.yml) |
| Manual (non-release) artifact lane | [`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json) + [`.github/workflows/manual-firmware-artifacts.yml`](../.github/workflows/manual-firmware-artifacts.yml) |
| Room-bundle SKUs | [`config/room-bundle-skus.json`](../config/room-bundle-skus.json) · [`docs/sense360-room-bundles.md`](sense360-room-bundles.md) |
| Firmware combination matrix | [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json) |
| All-YAML release classification | [`docs/all-yaml-release-matrix.md`](all-yaml-release-matrix.md) · [`scripts/classify_all_yaml_release_matrix.py`](../scripts/classify_all_yaml_release_matrix.py) |
| Release-note generation | [`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py) · [`scripts/plan_room_release_notes.py`](../scripts/plan_room_release_notes.py) · [`.github/workflows/release-notes-draft.yml`](../.github/workflows/release-notes-draft.yml) |
| Canonical roadmap / status | [`docs/sense360-roadmap-status.md`](sense360-roadmap-status.md) (DOCS-CONSOLIDATION-ROADMAP-001) |

**Key pipeline fact (unchanged):** the release workflow's build matrix is
generated **exclusively** from `config/webflash-builds.json`, filtered by
`version` + `channel` (job `generate-matrix` in
`firmware-build-release.yml`). A config that is not in
`config/webflash-builds.json` is **not** built or attached when a GitHub
Release is published, regardless of whether its YAML exists. "Release-capable"
in this document means exactly that: present in `config/webflash-builds.json`.

---

## 1. Canonical release matrix

One row per relevant firmware config string. Columns are exactly the
task-brief contract: bundle SKU · config string · YAML path · release channel
· compile status · artifact status · release-note status · WebFlash status ·
blocker status · notes. Empty release-channel / artifact cells (`—`) mean the
config is intentionally **not** release-eligible today.

| Bundle SKU | Config string | YAML path | Release channel | Compile status | Artifact status | Release-note status | WebFlash status | Blocker status | Notes |
|---|---|---|---|---|---|---|---|---|---|
| `S360-KIT-BATH-P` | `Ceiling-POE-VentIQ-RoomIQ` | `products/sense360-ceiling-poe-ventiq-roomiq.yaml` | **stable** | release-ci + compile-only-ci | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` | generated (stable) | **exposed (stable)** | none | Release-One stable build; the only `release_one_required_configs` entry. |
| — (LED variant) | `Ceiling-POE-VentIQ-RoomIQ-LED` | `products/sense360-ceiling-poe-ventiq-roomiq-led.yaml` | **preview** | release-ci + compile-only-ci | `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` | generated (preview) | **exposed (preview, manifest-only)** | LED preview→stable gauntlet (for stable promotion only) | Preview channel only. No LED-stable claim. |
| `S360-KIT-KITCHEN-P` | `Ceiling-POE-AirIQ-RoomIQ` | `products/sense360-ceiling-poe-airiq-roomiq.yaml` (wrapper `products/webflash/ceiling-poe-airiq-roomiq.yaml`) | **preview** | compile-only-ci (`validated-full-compile`, run `26821900127`) | `Sense360-Ceiling-POE-AirIQ-RoomIQ-v1.0.0-preview.bin` | generated (preview) | **build row (preview); metadata-ready / unpublished, not customer-exposed** | S360-410 + AirIQ-stack evidence (stable only) | Preview build row added by `RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001`; catalog `preview`. No binary / Release / `manifest.json`; bundle hidden / not buyable. |
| `S360-KIT-BEDROOM-P` | `Ceiling-POE-RoomIQ` | `products/sense360-ceiling-poe-roomiq.yaml` (wrapper `products/webflash/ceiling-poe-roomiq.yaml`) | **preview** | compile-only-ci (`validated-full-compile`, run `26821900127`) | `Sense360-Ceiling-POE-RoomIQ-v1.0.0-preview.bin` | generated (preview) | **build row (preview); metadata-ready / unpublished, not customer-exposed** | S360-410 (stable only) | Preview build row added by `RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001`; catalog `preview`. No binary / Release / `manifest.json`; bundle hidden / not buyable. |
| `S360-KIT-LIVING-P` / `S360-KIT-CORRIDOR-P` | `Ceiling-POE-RoomIQ-LED` | `products/sense360-ceiling-poe-roomiq-led.yaml` (wrapper `products/webflash/ceiling-poe-roomiq-led.yaml`) | **preview** | compile-only-ci (`validated-full-compile`, run `26821900127`) | `Sense360-Ceiling-POE-RoomIQ-LED-v1.0.0-preview.bin` | generated (preview) | **build row (preview); metadata-ready / unpublished, not customer-exposed** | S360-410 + LED preview→stable gauntlet (stable only) | Preview build row added by `RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001`; LED stays preview. Distinct from the VentIQ LED preview. No binary / Release / `manifest.json`; bundles hidden / not buyable. |
| — | `Ceiling-POE-VentIQ-FanRelay-RoomIQ` | `products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml` | — | manual-nonrelease-ci + compile-only-ci (`validated-full-compile`) | manual (`{stem}-manual-{sha}-nonrelease`, expiring) | not generated | not exposed | mains-safety / competent-person sign-off; GPIO3 strap-pin boot characterisation | Manual-only candidate. `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` blocked. |
| — | `Ceiling-POE-FanPWM` | `products/sense360-ceiling-poe-fanpwm.yaml` | — | manual-nonrelease-ci + compile-only-ci (`validated-full-compile`, **native + skeleton**) | manual (expiring) | not generated | not exposed | measured current / thermal (`S360-311-CURRENT-THERMAL-001`); `rpm_supported: false` | Native ESP32-S3 GPIO path compile-proven + functional bench PASS; current / thermal **not measured**, RPM **not measured**. Legacy SX1509 path superseded. `WEBFLASH-PWM-001` / `RELEASE-PWM-001` blocked. |
| — | `Ceiling-POE-FanDAC` | `products/sense360-ceiling-poe-fandac.yaml` | — | manual-nonrelease-ci + compile-only-ci (`validated-full-compile`) | manual (expiring) | not generated | not exposed | Cloudlift S12 / J3 harness + product-bench; S360-312 schematic / BOM | Manual-only candidate; enforces FanDAC↔AirIQ mutex. `WEBFLASH-DAC-001` / `RELEASE-DAC-001` blocked. |
| — | `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` | `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml` | — | no-ci-build | — | not generated | not exposed (reference-only wrapper) | **HW-005** (S360-320 schematic; GPIO5/6 collision; `ac_dimmer` cannot run across SX1509) + PACKAGE-TRIAC-001 + COMPLIANCE-001 | Hard `blocked`. No CI build of any kind. |

**Stable release target is exactly one config** — `Ceiling-POE-VentIQ-RoomIQ`
— matching `config/webflash-builds.json` and locked by
`tests/test_roadmap_status_doc.py::ReleaseTargetsMatchConfigTests`.

---

## 2. Room bundle verification

From [`config/room-bundle-skus.json`](../config/room-bundle-skus.json)
(validated by `tests/test_room_bundle_skus.py`). Bundle SKUs are sellable
room kits — **not** board SKUs, firmware artifact names, or release artifact
ids.

| Bundle SKU | Room | Boards | Likely firmware target | Release status | Remaining gates |
|---|---|---|---|---|---|
| `S360-KIT-BATH-P` | bathroom | S360-100/200/211/410 | `Ceiling-POE-VentIQ-RoomIQ` | **stable-release** | none (ships under preserved S360-410 schematic-pending caveat) |
| `S360-KIT-KITCHEN-P` | kitchen | S360-100/200/210/410 | `Ceiling-POE-AirIQ-RoomIQ` | stable-candidate | G1–G7 productization + AirIQ-stack hardware evidence + S360-410 verified |
| `S360-KIT-LIVING-P` | living-room | S360-100/200/300/410 | `Ceiling-POE-RoomIQ-LED` | preview-candidate | G1–G7 + S360-410 verified + LED preview→stable gauntlet |
| `S360-KIT-BEDROOM-P` | bedroom | S360-100/200/410 | `Ceiling-POE-RoomIQ` | stable-candidate | G1–G7 + S360-410 verified |
| `S360-KIT-CORRIDOR-P` | corridor | S360-100/200/300/410 | `Ceiling-POE-RoomIQ-LED` | preview-candidate | G1–G7 + S360-410 verified + LED preview→stable gauntlet (shares board set with LIVING-P) |

Only `S360-KIT-BATH-P` maps to a shipped stable build. Every other bundle is
a candidate gated behind its own promotion gates. **No bundle is promoted by
this PR.**

---

## 3. Target classification

Every firmware config string falls into exactly one class.

| Class | Definition | Targets |
|---|---|---|
| **Stable** | `webflash-builds.json` row, `channel: stable`; release workflow builds + attaches on a `release` event. | `Ceiling-POE-VentIQ-RoomIQ` |
| **Preview** | `webflash-builds.json` row, `channel: preview`; built + attached only when a preview tag is published. | `Ceiling-POE-VentIQ-RoomIQ-LED` |
| **Manual-only** | Top-level YAML in the `workflow_dispatch`-only manual / non-release artifact lane; no `artifact_name`, no wrapper, no builds row, no release. | `Ceiling-POE-VentIQ-FanRelay-RoomIQ`, `Ceiling-POE-FanPWM`, `Ceiling-POE-FanDAC` |
| **Compile-only** | CI-validation skeleton under `products/compile-only/`; compiles to prove the combination is valid; never released, never WebFlash-exposed. | `Ceiling-POE`, `Ceiling-POE-RoomIQ`, `Ceiling-POE-VentIQ`, `Ceiling-POE-AirIQ`, `Ceiling-POE-AirIQ-RoomIQ` (plus fan skeletons that are companions to manual-only targets) |
| **Blocked** | Catalog `status: blocked`; no CI build of any kind until upstream evidence clears. | `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` (HW-005) |

The full per-YAML enumeration (48 YAMLs incl. legacy / wrapper / helper) lives
in [`docs/all-yaml-release-matrix.md`](all-yaml-release-matrix.md) and is
reproduced by `scripts/classify_all_yaml_release_matrix.py`.

> **Class is a *WebFlash* classification, not a preview-release verdict.** The
> "Manual-only" (`FanRelay` / `FanPWM` / `FanDAC`) and "Blocked" (`FanTRIAC`)
> classes describe **WebFlash / `webflash-builds.json` eligibility**. Under
> `RELEASE-PREVIEW-WEBFLASH-ALL-BUILDABLE-001` those same targets are still
> **preview / advanced-preview release targets** delivered on the
> `manual-preview` / `advanced-manual-preview` lanes (see the channel-tier policy
> section below). "Manual-only" / "Blocked" here means "not WebFlash-importable
> yet", not "not preview-releasable".

---

## 4. Release-note coverage matrix

For every release-capable target (i.e. present in
`config/webflash-builds.json`), the release-note pipeline is verified end to
end. Non-release targets are intentionally **refused** by the pipeline — that
refusal is the correct behaviour, not a gap.

| Config string | Release-note template/generator | Workflow supports target | Artifact naming documented | Changelog expectation | Result |
|---|---|---|---|---|---|
| `Ceiling-POE-VentIQ-RoomIQ` (stable) | `scripts/generate_webflash_release_notes.py` + `scripts/plan_room_release_notes.py` | `release-notes-draft.yml` (`config_string` choice mirrors `webflash-builds.json`) | `Sense360-{CONFIG}-v{VERSION}-{CHANNEL}.bin` per `scripts/validate-webflash-release-notes.py` | `## Changelog` section requires human review before any real release | ✅ generated, validates structurally (channel=stable) |
| `Ceiling-POE-VentIQ-RoomIQ-LED` (preview) | same generator/planner | same workflow | same naming convention | `## Changelog` + preview-channel caveat | ✅ published preview; release proof in `docs/webflash-release-proof.md` |
| `Ceiling-POE-AirIQ-RoomIQ` (preview) | dry-run draft `docs/release-notes/preview/ceiling-poe-airiq-roomiq.md` | `release-notes-draft.yml` (`config_string` choice mirrors `webflash-builds.json`) | `Sense360-Ceiling-POE-AirIQ-RoomIQ-v1.0.0-preview.bin` | `## Changelog` + PREVIEW warning banner | ✅ draft validates structurally (channel=preview) — `RELEASE-PREVIEW-RELEASE-NOTES-DRYRUN-001`, metadata-ready / unpublished |
| `Ceiling-POE-RoomIQ` (preview) | dry-run draft `docs/release-notes/preview/ceiling-poe-roomiq.md` | same workflow | `Sense360-Ceiling-POE-RoomIQ-v1.0.0-preview.bin` | `## Changelog` + PREVIEW warning banner | ✅ draft validates structurally (channel=preview) — `RELEASE-PREVIEW-RELEASE-NOTES-DRYRUN-001`, metadata-ready / unpublished |
| `Ceiling-POE-RoomIQ-LED` (preview) | dry-run draft `docs/release-notes/preview/ceiling-poe-roomiq-led.md` | same workflow | `Sense360-Ceiling-POE-RoomIQ-LED-v1.0.0-preview.bin` | `## Changelog` + PREVIEW warning banner | ✅ draft validates structurally (channel=preview) — `RELEASE-PREVIEW-RELEASE-NOTES-DRYRUN-001`, metadata-ready / unpublished |
| Fan / blocked / compile-only configs | — | **refused** (not in `webflash-builds.json`) | n/a (no `artifact_name`) | n/a | ✅ correctly refused — `list_release_targets.py --validate`, the planner, and the classifier all reject fan tokens / non-matrix configs |

Every preview build row now has **release-note coverage**: the published VentIQ
LED preview by its recorded release proof
([`docs/webflash-release-proof.md`](webflash-release-proof.md)), and the three
metadata-ready room-bundle previews by validated **dry-run drafts**
([`docs/release-notes/preview/`](release-notes/preview/),
`RELEASE-PREVIEW-RELEASE-NOTES-DRYRUN-001`). The drafts are **not** attached to
any GitHub Release; they validate against the release-body contract and are
locked by
[`tests/test_preview_release_notes_drafts.py`](../tests/test_preview_release_notes_drafts.py).
Each draft states the PREVIEW posture (not stable / not recommended / not a
customer default / not hardware verified / not buyable), cites firmware-build
proof only (run `26821900127`), and points normal customers to the stable
Bathroom PoE release. Verified locally via `python3 scripts/list_release_targets.py`,
`for f in docs/release-notes/preview/ceiling-poe-*.md; do python3 scripts/validate-webflash-release-notes.py "$f" --channel preview; done`,
and `python3 tests/test_preview_release_notes_drafts.py`.

The **non-WebFlash** fan-control / TRIAC preview targets (refused by the WebFlash
release-note pipeline above, correctly, because they are not in
`config/webflash-builds.json`) get their own preview release-note coverage under
`RELEASE-PREVIEW-FAN-TRIAC-BUILD-ROWS-001`: validated dry-run drafts under
[`docs/release-notes/manual-preview/`](release-notes/manual-preview/) and a
build-row ledger at
[`config/preview-fan-triac-build-rows.json`](../config/preview-fan-triac-build-rows.json)
(the manual / advanced-manual analog of `config/webflash-builds.json`).
FanRelay / FanPWM / FanDAC are `manual-preview` (firmware-build proof only, run
`26821900127`); FanTRIAC is `advanced-manual-preview`, **build-blocked by
`HW-005`** with **no compile proof claimed** and the mandatory mains-risk
warning. No `config/webflash-builds.json` row is added. Locked by
[`tests/test_preview_fan_triac_build_rows.py`](../tests/test_preview_fan_triac_build_rows.py);
full record in
[`docs/release-preview-fan-triac-build-rows.md`](release-preview-fan-triac-build-rows.md).

---

## 5. WebFlash exposure verification

| Config string | WebFlash state | Rationale |
|---|---|---|
| `Ceiling-POE-VentIQ-RoomIQ` | **exposed** | Stable Release-One build; in `webflash-builds.json` + WebFlash `manifest.json` + `REQUIRED_CONFIGS`. |
| `Ceiling-POE-VentIQ-RoomIQ-LED` | **exposed (preview, manifest-only)** | Preview channel; manifest-only exposure (WebFlash WF-LED-003 Option A). Not in `REQUIRED_CONFIGS`. |
| `Ceiling-POE-FanPWM` | **intentionally hidden** | Manual-only; FanPWM WebFlash not enabled (guardrail). Future candidate behind `WEBFLASH-PWM-001`. |
| `Ceiling-POE-FanDAC` | **intentionally hidden** | Manual-only; FanDAC WebFlash not enabled (guardrail). Future candidate behind `WEBFLASH-DAC-001`. |
| `Ceiling-POE-VentIQ-FanRelay-RoomIQ` | **intentionally hidden** | Manual-only; FanRelay WebFlash not enabled (guardrail). Future candidate behind `WEBFLASH-RELAY-001`. |
| `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` | **blocked** | Reference-only wrapper exists but is not in the builds matrix; HW-005 gates everything downstream. |
| `Ceiling-POE-AirIQ-RoomIQ` / `Ceiling-POE-RoomIQ` / `Ceiling-POE-RoomIQ-LED` | **preview build row; not customer-exposed** | `RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001` added a preview row to `config/webflash-builds.json` (metadata-ready / unpublished). NOT in WebFlash `manifest.json`, NOT in `REQUIRED_CONFIGS`; no binary / GitHub Release; candidate bundles hidden / not buyable. Customer exposure stays owned by the `STABLE-TARGET-*` lanes after S360-410 (and, for LED, the gauntlet). |

WebFlash exposure matches actual readiness: the build matrix
(`config/webflash-builds.json`) now holds **five** rows — the stable
Release-One build, the published VentIQ LED preview, and the three
metadata-ready room-bundle previews added by
`RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001` — but only the first two are
**customer-exposed** via the WebFlash `manifest.json`; the three new preview
rows are release-eligibility metadata only (no binary, no Release, no
`manifest.json`, bundles hidden / not buyable). No fan driver is exposed. The
WebFlash-side canonical view is
`docs/sense360-webflash-status.md` in `sense360store/WebFlash`.

---

## 6. YAML availability

| Config string / family | GitHub / manual ESPHome use | Remote-package use | Release-capable | Tag-pinning recommendation |
|---|---|---|---|---|
| `Ceiling-POE-VentIQ-RoomIQ` | yes (canonical YAML) | yes (release-pinned wrapper) | **yes** (stable) | Pin `ref: v1.0.0` for reproducible installs; `external_components` pin documented in generated release notes |
| `Ceiling-POE-VentIQ-RoomIQ-LED` | yes | yes | **yes** (preview) | Pin to the preview tag (e.g. `v1.0.0-led-preview`); treat as preview, not for production |
| Fan manual candidates (Relay / PWM / DAC) | yes (manual / custom only) | yes (manual include) | no | Pin to a reviewed commit; manual install only — see [`docs/manual-install-fan-candidates.md`](manual-install-fan-candidates.md) |
| `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` | reference-only | no | no | n/a (blocked) |
| Compile-only skeletons | CI only (not advertised installable) | no | no | n/a |
| Legacy Core / Core-Voice / Mini YAMLs | yes (manual / custom) | yes | no | Pin to a reviewed commit; not advertised through the release / WebFlash pipelines |

Manual / remote-package availability is **not** the same as release-capability:
only the two `webflash-builds.json` configs are release-capable.

---

## 7. Next-release roadmap

| Horizon | Items | Gate(s) |
|---|---|---|
| **Immediate** | Keep `Ceiling-POE-VentIQ-RoomIQ` stable + `Ceiling-POE-VentIQ-RoomIQ-LED` preview as the only release-capable builds. Docs alignment (this PR). | none — already shipping |
| **Near-term** | LED preview→stable promotion lane (`PRODUCT-LED-STABLE-001`-style); fan-driver measured-evidence lane (`S360-311-CURRENT-THERMAL-001`, `S360-312-BENCH-RESULT-001`, `S360-310-SAFETY-BENCH-RESULT-001`); `STABLE-TARGET-ROOMIQ-001` (bedroom) / `STABLE-TARGET-AIRIQ-ROOMIQ-001` (kitchen) productization. | LED gauntlet; per-board bench evidence; **S360-410 verification (`PRODUCT-POE-410-001`)** |
| **Blocked** | `RELEASE-POE-410-001` + every S360-410-bearing stable bundle; fan-driver release lanes (`RELEASE-{PWM,DAC,RELAY}-001`); `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` (HW-005); cross-repo `WEBFLASH-{PWM,DAC,RELAY}-LIVE-CHECK-001`. | S360-410 evidence (bench / isolation / connector / J2-harness / PCB-source still missing); mains compliance; WebFlash repo access |

No queue item is started, reordered, or unblocked by this doc.

---

## 8. Guardrails honoured

This PR did **not**: publish firmware; generate artifacts; modify
`manifest.json` or `firmware/sources.json` (either repo); enable FanPWM /
FanDAC / FanRelay WebFlash; mark LED stable; mark S360-410 verified; or
fabricate any release readiness. It edits documentation only and adds no
config, YAML, workflow, or build entry.

## Validation

- `python3 tests/validate_configs.py`
- `python3 scripts/validate_compile_targets.py --metadata-only`
- `python3 tests/test_product_catalog.py`
- `python3 tests/test_all_yaml_release_matrix.py`
- `python3 tests/validate_webflash_builds.py`
- `python3 tests/test_roadmap_status_doc.py`
- `python3 -m unittest discover -s tests -p "test_*.py"`

## Cross-references

- Canonical roadmap / status: [`docs/sense360-roadmap-status.md`](sense360-roadmap-status.md)
- All-YAML release classification: [`docs/all-yaml-release-matrix.md`](all-yaml-release-matrix.md)
- Room bundle SKUs: [`docs/sense360-room-bundles.md`](sense360-room-bundles.md)
- Product-layer gate: [`docs/product-readiness-matrix.md`](product-readiness-matrix.md)
- WebFlash-layer gate: [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md)
- Release-layer gate: [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
- Manual install path: [`docs/manual-install-fan-candidates.md`](manual-install-fan-candidates.md)
- S360-410 evidence: [`docs/package-poe-410-evidence-result.md`](package-poe-410-evidence-result.md)
- Detailed PR queue: [`UPCOMING_PR.md`](../UPCOMING_PR.md)

---

## Channel-tier policy (RELEASE-PREVIEW-ALL-PRODUCTS-001)

The explicit stable / preview / advanced-preview channel-tier policy — and the
rule that **lack of hardware proof blocks stable only, not preview** — now
lives in [`docs/release-channel-policy.md`](release-channel-policy.md), backed
by [`config/release-channel-policy.json`](../config/release-channel-policy.json)
and [`tests/test_release_channel_policy.py`](../tests/test_release_channel_policy.py).
That doc carries the preview-release eligibility matrix for every buildable
target (Kitchen/AirIQ, Bedroom/RoomIQ, Living/Corridor LED, LED, FanRelay,
FanPWM, FanDAC, and FanTRIAC as advanced-preview only). It records eligibility
and warning copy only; it adds no `config/webflash-builds.json` rows and
publishes no artifacts.

### Concrete preview release targets + delivery lanes (RELEASE-PREVIEW-WEBFLASH-ALL-BUILDABLE-001)

The concrete, CI-consumable target manifest is
[`config/preview-release-targets.json`](../config/preview-release-targets.json)
(canonical doc [`docs/preview-release-targets.md`](preview-release-targets.md)).
`RELEASE-PREVIEW-WEBFLASH-ALL-BUILDABLE-001` aligns those concrete targets with
the policy: **every buildable product is a preview / advanced-preview release
target**, with three delivery lanes —

- **`webflash`** — the SELV PoE targets (the two live builds plus the
  Kitchen/AirIQ, Bedroom/RoomIQ, Living/Corridor LED candidates). Only these can
  ever enter `config/webflash-builds.json`, which remains the **sole WebFlash
  release-eligibility source of truth**.
- **`manual-preview`** — FanRelay / FanPWM / FanDAC. Their tester-facing preview
  artifact is produced by the manual lane
  ([`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json));
  they are real preview release targets, no longer "manual-only / not
  releasable". WebFlash one-click import stays gated by the fan-token guardrail
  (`scripts/list_release_targets.py`) until the WebFlash warning UX supports fan
  preview exposure — a separate follow-up (`WEBFLASH-{RELAY,PWM,DAC}-001`).
- **`advanced-manual-preview`** — FanTRIAC. No longer "blocked from preview":
  preview is allowed in principle and only the `HW-005` *buildability* blocker
  prevents a cut. WebFlash import is the `WF-IMPORT-TRIAC-001` follow-up.

**This does not move any WebFlash cell above:** no fan / TRIAC token enters
`config/webflash-builds.json`, the catalog `webflash_build_matrix` stays `false`
for every fan driver, and WebFlash exposure is unchanged. The manual-preview /
advanced-manual-preview lanes are **non-WebFlash** preview delivery lanes; the
"not exposed" WebFlash cells in §1 / §5 remain correct.

### Preview WebFlash wrappers authored (RELEASE-PREVIEW-WEBFLASH-WRAPPERS-001)

The three compile-validated `webflash`-lane preview candidates —
`Ceiling-POE-AirIQ-RoomIQ`, `Ceiling-POE-RoomIQ`, and `Ceiling-POE-RoomIQ-LED` —
now have thin `products/webflash/*.yaml` wrappers, each re-including its
canonical `products/sense360-*.yaml` shim (preview-only; no `version`,
`channel`, or `artifact_name`). See
[`docs/release-preview-webflash-wrappers.md`](release-preview-webflash-wrappers.md);
each wrapper is recorded in the per-target `webflash_wrapper` field of
[`config/preview-release-targets.json`](../config/preview-release-targets.json).

**This still moves no WebFlash cell in §1 / §5.** No `config/webflash-builds.json`
row is added (it stays the two live builds), no `config/product-catalog.json`
status is flipped, and WebFlash exposure is unchanged. The wrapper is a
build-prep artifact only; cutting an actual `config/webflash-builds.json` row —
with recorded firmware-build proof — remains a separate, later, reviewed PR, and
those three targets stay **not exposed** in the WebFlash matrix until then. No
TRIAC wrapper and no fan manual-preview wrapper were added.

### Preview WebFlash build rows cut (RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001)

The reviewed `config/webflash-builds.json` **preview** build rows for the three
wrapped candidates — `Ceiling-POE-AirIQ-RoomIQ`, `Ceiling-POE-RoomIQ`, and
`Ceiling-POE-RoomIQ-LED` — have now been cut (each addressed via its
`products/webflash` wrapper, on the preview channel, citing hosted-compile run
`26821900127`), and their `config/product-catalog.json` rows were flipped
`blocked` → `preview` (with `webflash_build_matrix: true`). The §1 / §5 cells
above are updated accordingly: those three configs are now **preview build
rows** in the matrix. This is **release-eligibility metadata only** — no
firmware binary, GitHub Release, tag, `manifest.json`, or
`firmware/sources.json` is published; the three rows are **not customer-exposed**
via the WebFlash `manifest.json`; nothing is promoted to stable; the launch SKU
stays `S360-KIT-BATH-P`; and the consuming candidate bundles stay hidden / not
buyable. See
[`docs/release-preview-webflash-build-rows.md`](release-preview-webflash-build-rows.md).
No TRIAC row and no fan manual-preview row were added.

### Preview release-note drafts generated (RELEASE-PREVIEW-RELEASE-NOTES-DRYRUN-001)

Validated **release-note drafts** for the three metadata-ready preview build
rows now live under
[`docs/release-notes/preview/`](release-notes/preview/) (one per config string),
completing the §4 release-note coverage matrix above so **every** preview build
row has coverage. This is **release-note dry-run only**: each draft passes the
WebFlash release-body contract
([`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py),
`channel=preview`) and is locked by
[`tests/test_preview_release_notes_drafts.py`](../tests/test_preview_release_notes_drafts.py),
but **no** draft is attached to a GitHub Release and **no** firmware binary,
Release, tag, `manifest.json`, or `firmware/sources.json` is produced. The
drafts mark the builds PREVIEW (not stable / not recommended / not a customer
default / not hardware verified / not buyable as a public shop product), cite
firmware-build proof only (run `26821900127`), claim no hardware / bench /
compliance / commercial-availability proof, and point normal customers to the
stable Bathroom PoE release. The published stable Bathroom release and the
published VentIQ LED preview are **not** re-drafted. See
[`docs/release-preview-webflash-release-notes-dryrun.md`](release-preview-webflash-release-notes-dryrun.md).

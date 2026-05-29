# All-YAML Release Matrix (STABLE-RELEASE-MATRIX-ALL-YAML-001)

## Purpose and scope

This document is the canonical, **all-YAML** release classification.
It enumerates every YAML under [`products/`](../products/) (top-level
canonical YAMLs, [`products/webflash/`](../products/webflash/)
wrappers, and [`products/compile-only/`](../products/compile-only/)
skeletons) and records, for each, exactly one release class out of
six:

  * `stable-release`
  * `preview-release`
  * `manual-candidate-only`
  * `compile-only`
  * `blocked`
  * `not-a-product-entrypoint`

It exists because the prior release inventory in
[`docs/room-firmware-release-matrix.md`](room-firmware-release-matrix.md)
([`RELEASE-PIPELINE-ROOM-MATRIX-001`](room-firmware-release-matrix.md#room-firmware-release-matrix-release-pipeline-room-matrix-001))
was deliberately scoped to the room-firmware family that the release
workflow had already been wired for —
`Ceiling-POE-VentIQ-RoomIQ` (stable) and
`Ceiling-POE-VentIQ-RoomIQ-LED` (preview). That scope answered
*"which RoomIQ variants exist"*, but it did not answer *"for every
YAML in the repo, which release path applies"*. This document fills
that gap: it is the broader release-posture map across the AirIQ /
VentIQ / RoomIQ / LED / Relay / PWM / DAC / TRIAC families plus the
Core / Core-Voice / Mini legacy YAMLs and the WebFlash wrappers.

It cross-cuts the existing layered gates:

- [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md) (PACKAGE-GAP-001)
- [`docs/product-readiness-matrix.md`](product-readiness-matrix.md) (PRODUCT-GAP-001)
- [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md) (WEBFLASH-GAP-001)
- [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md) (RELEASE-GAP-001)
- [`docs/room-firmware-release-matrix.md`](room-firmware-release-matrix.md) (RELEASE-PIPELINE-ROOM-MATRIX-001)
- [`docs/room-firmware-release-notes.md`](room-firmware-release-notes.md) (RELEASE-NOTES-PIPELINE-001)

### This document is documentation only

STABLE-RELEASE-MATRIX-ALL-YAML-001 — this PR — does **not**:

- publish, build, or attach any firmware artifact, and creates no GitHub Release;
- commit any `.bin`, checksum, or build-info file;
- edit any YAML under [`products/`](../products/) or
  [`products/webflash/`](../products/webflash/) or
  [`products/compile-only/`](../products/compile-only/);
- promote LED from `preview` to `stable`;
- promote FanRelay / FanPWM / FanDAC out of manual-candidate-only;
- add an `artifact_name` to any fan product;
- flip any `webflash_build_matrix` value;
- add or remove an entry in
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  [`config/product-catalog.json`](../config/product-catalog.json),
  [`config/compile-only-targets.json`](../config/compile-only-targets.json),
  or [`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json);
- write [`firmware/sources.json`](../firmware/sources.json) or `manifest.json`;
- claim WebFlash / import / release / hardware-stable / compliance readiness
  for FanRelay / FanPWM / FanDAC / FanTRIAC.

Every classification below is **read** from the committed catalogs and
workflows cited inline by the read-only classifier
[`scripts/classify_all_yaml_release_matrix.py`](../scripts/classify_all_yaml_release_matrix.py);
nothing is asserted beyond what they already record.

---

## Source-of-truth files

| Layer | File |
|-------|------|
| Release matrix (sole release-eligibility source) | [`config/webflash-builds.json`](../config/webflash-builds.json) |
| Release build/publish workflow | [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml) |
| Product lifecycle / hardware status | [`config/product-catalog.json`](../config/product-catalog.json) |
| Compile-only validation lane | [`config/compile-only-targets.json`](../config/compile-only-targets.json) + [`.github/workflows/compile-only.yml`](../.github/workflows/compile-only.yml) |
| Manual (non-release) artifact lane | [`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json) + [`.github/workflows/manual-firmware-artifacts.yml`](../.github/workflows/manual-firmware-artifacts.yml) |
| Selectable release targets (UX) | [`scripts/list_release_targets.py`](../scripts/list_release_targets.py) |
| Release-notes draft helper | [`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py) + [`.github/workflows/release-notes-draft.yml`](../.github/workflows/release-notes-draft.yml) |
| Release-notes dry-run planner | [`scripts/plan_room_release_notes.py`](../scripts/plan_room_release_notes.py) |
| **All-YAML classifier (this PR)** | [`scripts/classify_all_yaml_release_matrix.py`](../scripts/classify_all_yaml_release_matrix.py) |

**Key pipeline fact:** the release workflow's build matrix is generated
**exclusively** from `config/webflash-builds.json`, filtered by `version`
+ `channel` (see `firmware-build-release.yml` job `generate-matrix`). A
config that is not in `webflash-builds.json` is **not** built or attached
when a GitHub Release is published, regardless of whether its YAML exists.
Release-selectable in this document means exactly that: present in
`config/webflash-builds.json`.

---

## Release-class definitions

| Class | Definition | Decided by |
|---|---|---|
| `stable-release` | Production-channel build that the release workflow will compile and attach to a `release` event. | `config/webflash-builds.json` row with `channel: stable` |
| `preview-release` | Preview-channel build that the release workflow will compile and attach when explicitly selected as preview. | `config/webflash-builds.json` row with `channel: preview` |
| `manual-candidate-only` | Top-level product YAML that **only** participates in the workflow_dispatch-only manual / non-release artifact lane; no `artifact_name`, no `webflash_build_matrix`, no release. | `config/manual-firmware-artifacts.json` candidate |
| `compile-only` | CI-validation skeleton under `products/compile-only/`; compiles in CI to prove the combination is valid; never released and never WebFlash-exposed. | location under `products/compile-only/` and entry in `config/compile-only-targets.json` |
| `blocked` | Top-level product YAML with a catalog `status: blocked` or a `hardware-pending` posture that has no manual lane participation; held until upstream evidence clears. | `config/product-catalog.json` `status: blocked` or `hardware-pending` (with no manual-lane row) |
| `not-a-product-entrypoint` | Either a WebFlash wrapper under `products/webflash/` (which re-includes a canonical product YAML), a `legacy-compatible` pre-WebFlash YAML retained for manual / custom users, or a repo helper such as `products/secrets.yaml`. | location under `products/webflash/`, catalog `status: legacy-compatible`, or no catalog row at all |

A YAML belongs to **exactly one** class. The classifier
[`scripts/classify_all_yaml_release_matrix.py`](../scripts/classify_all_yaml_release_matrix.py)
applies the decision rules above in a deterministic order and the
contract is locked in by
[`tests/test_all_yaml_release_matrix.py`](../tests/test_all_yaml_release_matrix.py).

---

## Stable-promotion criteria

For a candidate YAML to be promoted to `stable-release`, all of the
following must be true at the time of promotion. None of these are
asserted to be true by this PR for any YAML that is not already
`stable-release` today.

1. **Canonical product YAML exists** under
   [`products/`](../products/) with the expected
   `sense360-<config>.yaml` naming.
2. **Catalog row exists** in
   [`config/product-catalog.json`](../config/product-catalog.json) with
   `status: production` (or — for promotion from `preview` — a status
   change approved by a separate slice), the matching
   `config_string`, `version`, `channel: stable`, and `artifact_name`.
3. **Top-level full compile validated** through the compile-only lane
   (`config/compile-only-targets.json` carries
   `compile_validation_status: validated-full-compile` for a target
   that includes the canonical product YAML, **not** just a
   skeleton).
4. **WebFlash wrapper exists** under
   [`products/webflash/`](../products/webflash/) and the catalog row
   sets `webflash_wrapper` to it, **if** WebFlash release is required
   for the product. (Remote-package / manual-install-only products
   are not selectable for release through this lane today.)
5. **`artifact_name` exists** on the catalog row **and** on the
   matching [`config/webflash-builds.json`](../config/webflash-builds.json)
   row, with the standard
   `Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin` shape that
   [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py)
   accepts.
6. **Release notes can be generated** without overrides:
   [`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py)
   does not refuse the target and
   [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py)
   passes structurally.
7. **No blocking hardware / compliance caveat** in
   [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md),
   [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md),
   [`docs/product-readiness-matrix.md`](product-readiness-matrix.md),
   or [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md).
8. **Not currently `manual-candidate-only`** — promotion out of the
   manual lane requires an explicit per-family slice
   (`WEBFLASH-RELAY-001` / `RELEASE-RELAY-001`, the FanPWM /
   FanDAC analogues) that clears the hardware and compliance gates
   first.
9. **Not currently `preview-only`** — promotion from `preview` to
   `stable` requires the
   [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
   gauntlet (preview-stage bench Open Questions resolved, no
   regression in the release artifact, etc.).

---

## Current intended channel posture

The classifications below match the source-of-truth catalogs as of
this PR. They are deliberately **not** more ambitious than what the
committed evidence supports.

- **RoomIQ (non-LED) agreed release configs** —
  `Ceiling-POE-VentIQ-RoomIQ` is currently the **only** `stable`
  config. The other RoomIQ-bearing canonical YAML
  (`Ceiling-POE-VentIQ-RoomIQ-LED`) is on `preview` because its
  preview-stage S360-300 hardware Open Questions (LED harness rail,
  LED count, harness identity) must clear before any stable
  promotion (see
  [`docs/product-led-preview-decision.md`](product-led-preview-decision.md)).
- **LED remains `preview`** unless a separate LED stable-promotion
  PR approves it. This PR does **not** approve that promotion.
- **FanRelay / FanPWM / FanDAC** remain `manual-candidate-only`.
  They are tracked exclusively by
  [`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json)
  for the workflow_dispatch-only
  [`.github/workflows/manual-firmware-artifacts.yml`](../.github/workflows/manual-firmware-artifacts.yml)
  lane. None has an `artifact_name`, a `webflash_wrapper`, or a row in
  `config/webflash-builds.json`. None is reachable from
  `firmware-build-release.yml`.
- **FanTRIAC** remains `blocked` under
  [HW-005](release-one-hardware-audit.md#fantriac-mapping-resolution)
  + PACKAGE-TRIAC-001 + COMPLIANCE-001 + WebFlash manual-warning UX
  gates. It has no CI build of any kind today.
- **Compile-only skeletons** under
  [`products/compile-only/`](../products/compile-only/) are CI
  validation files, not release products. They are not promoted by
  this PR and are not advertised as installable.
- **Helper / package YAMLs** — `products/secrets.yaml` (the
  secrets-example installer companion) and the WebFlash wrappers
  under [`products/webflash/`](../products/webflash/) (which
  re-include the canonical product YAML) — are not release products.

---

## All-YAML release classification table

The table below is the full enumeration as classified by
[`scripts/classify_all_yaml_release_matrix.py`](../scripts/classify_all_yaml_release_matrix.py)
at the source-of-truth files. Re-run the classifier locally to
regenerate the table; this document is the human-readable view of
that output.

### Release-eligible (`stable-release` / `preview-release`)

| Product / config string | YAML path | Boards | Catalog status | Compile status | WebFlash wrapper | `artifact_name` | Channel | Selectable for | Blockers / notes |
|---|---|---|---|---|---|---|---|---|---|
| **Ceiling-POE-VentIQ-RoomIQ** | `products/sense360-ceiling-poe-ventiq-roomiq.yaml` | S360-100 + S360-211 + S360-200 + S360-410 | `production` | release-ci + compile-only-ci | `products/webflash/ceiling-poe-ventiq-roomiq.yaml` | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` | `stable` | release-notes / dry-run / release dispatch as `stable` | None — Release-One ships this. FanTRIAC / LED excluded by design. |
| **Ceiling-POE-VentIQ-RoomIQ-LED** | `products/sense360-ceiling-poe-ventiq-roomiq-led.yaml` | S360-100 + S360-211 + S360-200 + S360-410 + S360-300 | `preview` | release-ci + compile-only-ci | `products/webflash/ceiling-poe-ventiq-roomiq-led.yaml` | `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` | `preview` | release-notes / dry-run / release dispatch as `preview` **only** | Preview-stage S360-300 bench Open Questions before any stable promotion (LED harness rail, LED count, harness identity); FanTRIAC stays blocked. |

### `manual-candidate-only`

| Product / config string | YAML path | Boards | Catalog status | Compile status | WebFlash wrapper | `artifact_name` | Channel | Selectable for | Blockers / notes |
|---|---|---|---|---|---|---|---|---|---|
| **Ceiling-POE-VentIQ-FanRelay-RoomIQ** | `products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml` | S360-100 + S360-211 + S360-200 + S360-310 + S360-410 | `hardware-pending` | manual-nonrelease-ci + compile-only-ci (`validated-full-compile`) | none | none | none | manual-firmware-artifacts (workflow_dispatch only); **not release-selectable** | GPIO3 strap-pin boot characterisation (production-wide / multi-unit); mains-safety / installation-approval / creepage / clearance / thermal / EMI / EMC evidence; competent-person sign-off. WEBFLASH-RELAY-001 / RELEASE-RELAY-001 / WF-IMPORT-RELAY-001 blocked. |
| **Ceiling-POE-FanPWM** | `products/sense360-ceiling-poe-fanpwm.yaml` | S360-100 + S360-311 + S360-410 | `hardware-pending` | manual-nonrelease-ci + compile-only-ci (top-level + skeleton, both `validated-full-compile`) | none | none | none | manual-firmware-artifacts (workflow_dispatch only); **not release-selectable** | PWM polarity bench; per-fan / aggregate current + thermal envelope; product bench incomplete; **no RPM / TachIO** (`rpm_supported: false`); S360-311 schematic `cataloged_unverified`. WEBFLASH-PWM-001 / RELEASE-PWM-001 / WF-IMPORT-PWM-001 blocked. |
| **Ceiling-POE-FanDAC** | `products/sense360-ceiling-poe-fandac.yaml` | S360-100 + S360-312 + S360-410 | `hardware-pending` | manual-nonrelease-ci + compile-only-ci (top-level + skeleton, both `validated-full-compile`) | none | none | none | manual-firmware-artifacts (workflow_dispatch only); **not release-selectable** | Not Cloudlift-ready; J3 / Cloudlift S12 harness + product-bench evidence; S360-312 schematic / BOM verification; enforces FanDAC↔AirIQ mutex. WEBFLASH-DAC-001 / RELEASE-DAC-001 / WF-IMPORT-DAC-001 blocked. |

### `compile-only`

| YAML path | Compile-only target id | Compile status | Blockers / notes |
|---|---|---|---|
| `products/compile-only/ceiling-poe.yaml` | `ceiling-poe-compile-only` | compile-only | CI validation subset only; `hardware_required_for_validation: true`. |
| `products/compile-only/ceiling-poe-roomiq.yaml` | `ceiling-poe-roomiq-compile-only` | compile-only | CI validation subset only; `hardware_required_for_validation: true`. |
| `products/compile-only/ceiling-poe-ventiq.yaml` | `ceiling-poe-ventiq-compile-only` | compile-only | CI validation subset only; `hardware_required_for_validation: true`. |
| `products/compile-only/ceiling-poe-airiq.yaml` | `ceiling-poe-airiq-compile-only` | compile-only | CI validation subset only; AirIQ↔VentIQ mutex; `hardware_required_for_validation: true`. |
| `products/compile-only/ceiling-poe-airiq-roomiq.yaml` | `ceiling-poe-airiq-roomiq-compile-only` | compile-only | CI validation subset only; AirIQ↔VentIQ mutex; `hardware_required_for_validation: true`. |
| `products/compile-only/ceiling-poe-fanpwm.yaml` | `ceiling-poe-fanpwm-compile-only` | `validated-full-compile` | Skeleton companion to the top-level FanPWM manual candidate; not a release product. |
| `products/compile-only/ceiling-poe-fandac.yaml` | `ceiling-poe-fandac-compile-only` | `validated-full-compile` | Skeleton companion to the top-level FanDAC manual candidate; not a release product. |

### `blocked`

| Product / config string | YAML path | Boards | Catalog status | Compile status | WebFlash wrapper | `artifact_name` | Channel | Selectable for | Blockers / notes |
|---|---|---|---|---|---|---|---|---|---|
| **Ceiling-POE-VentIQ-FanTRIAC-RoomIQ** | `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml` | S360-100 + S360-211 + S360-200 + S360-320 + S360-410 | `blocked` (`HW-005`) | no-ci-build | `products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml` (reference-only) | none | none | **none** | HW-005 (S360-320 schematic uncommitted; GPIO5/GPIO6 collide with RoomIQ J10; `ac_dimmer` cannot run across SX1509) + HW-PINMAP-320-FOLLOWUP + PACKAGE-TRIAC-001 + COMPLIANCE-001 + WebFlash manual-warning UX gates. |

### `not-a-product-entrypoint`

This class collects everything that is **not** a standalone release
entry point. It splits into three groups: WebFlash wrappers, legacy
pre-WebFlash YAMLs retained for manual / custom users, and helper
YAMLs. None is release-selectable.

**WebFlash wrappers** under [`products/webflash/`](../products/webflash/)
— each re-includes its canonical product YAML; the canonical YAML
(not the wrapper) carries the release classification:

| Wrapper YAML | Canonical YAML it wraps | Wrapper's classification |
|---|---|---|
| `products/webflash/ceiling-poe-ventiq-roomiq.yaml` | `products/sense360-ceiling-poe-ventiq-roomiq.yaml` (stable) | `not-a-product-entrypoint` |
| `products/webflash/ceiling-poe-ventiq-roomiq-led.yaml` | `products/sense360-ceiling-poe-ventiq-roomiq-led.yaml` (preview) | `not-a-product-entrypoint` |
| `products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml` | `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml` (blocked) | `not-a-product-entrypoint` (reference-only; not in builds matrix) |

**Helper YAMLs**:

| YAML path | Notes |
|---|---|
| `products/secrets.yaml` | Secrets-example install companion; gitignored secrets, never released. |

**Legacy-compatible YAMLs** (`status: legacy-compatible` per the
catalog) — pre-WebFlash Core / Core-Voice / Mini / PoE / fan-pwm
products retained for manual / custom users. **None** is a
Release-One WebFlash firmware target. Each is installable manually
via remote-package include but is **not** advertised through the
release / WebFlash / release-notes pipelines:

| YAML path | Family | Notes |
|---|---|---|
| `products/sense360-poe.yaml` | PoE controller | Pre-WebFlash. |
| `products/sense360-fan-pwm.yaml` | Legacy four-channel PWM accessory | Pre-WebFlash. Not the new FanPWM (`Ceiling-POE-FanPWM`). |
| `products/sense360-core-c-poe.yaml`, `…-c-pwr.yaml`, `…-c-usb.yaml` | Core ceiling-mount (3 power options) | Pre-WebFlash. |
| `products/sense360-core-w-poe.yaml`, `…-w-pwr.yaml`, `…-w-usb.yaml` | Core wall-mount (3 power options) | Pre-WebFlash. |
| `products/sense360-core-v-c-poe.yaml`, `…-v-c-pwr.yaml`, `…-v-c-usb.yaml` | Core-Voice ceiling-mount (3 power options) | Pre-WebFlash. LED+MIC ring required. |
| `products/sense360-core-v-w-poe.yaml`, `…-v-w-pwr.yaml`, `…-v-w-usb.yaml` | Core-Voice wall-mount (3 power options) | Pre-WebFlash. LED+MIC ring required. |
| `products/sense360-core-ceiling.yaml`, `…-wall.yaml` | Core complete configs | Pre-WebFlash. AirIQ + Comfort + Presence + LED. |
| `products/sense360-core-voice-ceiling.yaml`, `…-voice-wall.yaml` | Core-Voice complete configs | Pre-WebFlash. LED+MIC ring required. |
| `products/sense360-core-ceiling-bathroom.yaml` | Bathroom ceiling | Pre-WebFlash. Legacy Bathroom module (the WebFlash taxonomy spells it VentIQ). |
| `products/sense360-core-ceiling-presence.yaml`, `…-wall-presence.yaml` | Presence-only | Pre-WebFlash. |
| `products/sense360-mini-airiq.yaml`, `…-basic.yaml`, `…-advanced.yaml`, `…-ld2412.yaml` | Mini AirIQ family | Pre-WebFlash. |
| `products/sense360-mini-presence.yaml`, `…-basic.yaml`, `…-advanced.yaml`, `…-ld2412.yaml`, `…-advanced-ld2412.yaml` | Mini Presence family | Pre-WebFlash. |
| `products/sense360-mini-full-ld2412.yaml` | Mini full | Pre-WebFlash. |

---

## Candidate stable additions

The user-facing question *"should other room combos be promoted into
[`config/webflash-builds.json`](../config/webflash-builds.json)?"* is
answered explicitly here. None is approved by this PR; each row
records the exact blocker(s) that must clear in a separately approved
slice before promotion.

| Candidate (config string) | Status today | What is **already** evidenced | What is **missing** for stable | Owning follow-up |
|---|---|---|---|---|
| `Ceiling-POE-VentIQ-RoomIQ-LED` | **already `preview`** | Catalog row (`preview`), WebFlash wrapper, build-matrix row, `artifact_name`, release notes (preview) | Preview-stage S360-300 hardware Open Questions (LED harness rail, LED count, harness identity); regression-free preview soak | Separate LED stable-promotion PR (`PRODUCT-LED-STABLE-001`-style); see [`docs/product-led-preview-decision.md`](product-led-preview-decision.md) and [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md). **Not approved by this PR.** |
| `Ceiling-POE-VentIQ-FanRelay-RoomIQ` | `manual-candidate-only` | Catalog row (`hardware-pending`); top-level full compile (`validated-full-compile`); manual-lane artifact path | WebFlash wrapper; `artifact_name`; `webflash_build_matrix: true`; `config/webflash-builds.json` row; mains-safety / installation / competent-person sign-off; production-wide GPIO3 strap-pin boot characterisation; compliance / EMI / EMC evidence | `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001` (all blocked). **Not approved by this PR.** |
| `Ceiling-POE-FanPWM` | `manual-candidate-only` | Catalog row (`hardware-pending`); top-level full compile (`validated-full-compile`); manual-lane artifact path | WebFlash wrapper; `artifact_name`; `webflash_build_matrix: true`; `config/webflash-builds.json` row; PWM polarity bench; per-fan / aggregate current and thermal envelope; product bench; RPM / TachIO out of scope (`rpm_supported: false`); S360-311 schematic verification | `WEBFLASH-PWM-001` / `RELEASE-PWM-001` / `WF-IMPORT-PWM-001` (all blocked). **Not approved by this PR.** |
| `Ceiling-POE-FanDAC` | `manual-candidate-only` | Catalog row (`hardware-pending`); top-level full compile (`validated-full-compile`); manual-lane artifact path | WebFlash wrapper; `artifact_name`; `webflash_build_matrix: true`; `config/webflash-builds.json` row; Cloudlift S12 harness / product-bench evidence; S360-312 schematic / BOM verification; FanDAC↔AirIQ mutex still enforced | `WEBFLASH-DAC-001` / `RELEASE-DAC-001` / `WF-IMPORT-DAC-001` (all blocked). **Not approved by this PR.** |
| `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` | `blocked` | Reference-only WebFlash wrapper; catalog row (`blocked`, `HW-005`) | Everything else — HW-005 S360-320 schematic; pin-map resolution; PACKAGE-TRIAC-001; COMPLIANCE-001; WebFlash manual-warning UX | Long chain; remains `blocked` until HW-005 clears. **Not approved by this PR.** |
| Other room combos (`Ceiling-POE-VentIQ` alone, `Ceiling-POE-RoomIQ` alone, `Ceiling-POE-AirIQ`, `Ceiling-POE-AirIQ-RoomIQ`, `Ceiling-POE`) | compile-only | Compile-only skeleton; CI validation row | Top-level product YAML; catalog row; WebFlash wrapper; `artifact_name`; `webflash_build_matrix: true`; `config/webflash-builds.json` row; product / WebFlash / release readiness | Out of scope — no Release-One kit ships these as standalone configs today. **Not a candidate addition.** |
| Legacy Core / Core-Voice / Mini configs (`products/sense360-core-*.yaml`, `products/sense360-mini-*.yaml`, `products/sense360-poe.yaml`, `products/sense360-fan-pwm.yaml`) | `not-a-product-entrypoint` (legacy-compatible) | Pre-WebFlash YAMLs retained for manual / custom users | Re-onboarding through PRODUCT-GAP-001 / WEBFLASH-GAP-001 / RELEASE-GAP-001; no claim that any of these would map cleanly to a WebFlash `config_string` without further work | Not in any current follow-up. **Not a candidate addition.** |

> **Actionable expansion plan:** the
> [`docs/stable-target-expansion-plan.md`](stable-target-expansion-plan.md)
> (STABLE-TARGET-EXPANSION-PLAN-001) document derives the per-candidate
> stable-promotion gate checklist (G1–G10), the recommended follow-up
> PR sequence (`STABLE-TARGET-VENTIQ-001`, `STABLE-TARGET-CORE-001`,
> `STABLE-TARGET-ROOMIQ-001`, `STABLE-TARGET-AIRIQ-001`,
> `STABLE-TARGET-AIRIQ-ROOMIQ-001`, `LED-STABLE-PROMOTION-001`) and the
> per-PR scope template directly from the rows above. The plan does
> **not** promote anything; it records the missing evidence per
> candidate. Cross-referenced from the all-YAML matrix to keep the
> "what's next" path obvious.

---

## Release-selection design (post-this-PR)

This PR codifies the rules the existing release pipeline already
follows and adds the cross-cutting documentation + a classifier and
test that lock the broader posture in. No workflow file is changed
by this PR.

- **Release-note generation** —
  [`scripts/plan_room_release_notes.py`](../scripts/plan_room_release_notes.py)
  and
  [`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py)
  select **only** from `config/webflash-builds.json`. The classifier
  test
  ([`tests/test_all_yaml_release_matrix.py`](../tests/test_all_yaml_release_matrix.py))
  asserts the release-selectable set equals the
  `config/webflash-builds.json` entries, so a future regression that
  accidentally hardcodes the stable RoomIQ is caught.
- **Release dry-run** —
  [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)
  exposes `release_target` as a `type: choice` input whose options
  are mirrored from `config/webflash-builds.json` plus the
  `all-release-eligible` sentinel; the default is
  `all-release-eligible`. Selecting `all-release-eligible` covers
  both the stable RoomIQ and the preview LED.
- **LED preview is preview-only** — the LED row's channel is
  `preview`, so a dispatch that filters on `channel=stable` does
  **not** include LED. LED is only attached to a `release` event
  when an LED-channel tag (e.g. `v1.0.0-led-preview`) is published;
  the tag → product mapping is unchanged from
  `RELEASE-PRODUCT-SELECTION-001` and lives in
  [`scripts/derive_release_version_channel.py`](../scripts/derive_release_version_channel.py).
- **Fan candidates must not appear in release selection** — the
  picker, the planner, the release-target enumerator
  ([`scripts/list_release_targets.py`](../scripts/list_release_targets.py)),
  and the new classifier all refuse `FanRelay` / `FanPWM` /
  `FanDAC` tokens in `config/webflash-builds.json` (a hard
  guardrail). The test suite locks that in.
- **Invalid / manual / blocked targets must fail clearly** —
  `list_release_targets.py --validate` rejects any identifier that
  is not in `config/webflash-builds.json` or the sentinel; the
  planner rejects any `config_string` not in the release matrix;
  the classifier raises `ClassifyError` if a fan token leaks into
  the release matrix.

---

## Validation

This document is reproduced and locked in by:

- `python3 scripts/classify_all_yaml_release_matrix.py` — emits the
  table above as the source-of-truth-derived view.
- `python3 scripts/classify_all_yaml_release_matrix.py --summary` —
  per-class counts.
- `python3 scripts/classify_all_yaml_release_matrix.py --json` —
  machine-readable form, consumed by the contract tests.
- `python3 scripts/plan_room_release_notes.py` — release-notes
  dry-run planner (unchanged by this PR; cross-checked).
- `python3 tests/test_all_yaml_release_matrix.py` — contract tests
  for this matrix.
- `python3 tests/test_plan_room_release_notes.py` — planner
  contract tests (unchanged by this PR).
- `python3 tests/test_release_dry_run_mode.py` — dry-run mode
  contract tests (unchanged by this PR).
- `python3 tests/test_release_product_selection.py` — picker /
  selection contract tests (unchanged by this PR).
- `python3 tests/validate_configs.py` — full YAML structural
  validator.
- `python3 scripts/validate_compile_targets.py --metadata-only` —
  compile-target metadata.
- `python3 tests/validate_webflash_builds.py` — WebFlash build
  matrix validator.
- `python3 tests/test_product_catalog.py` — catalog cross-check.
- `python3 tests/test_workflow_permissions.py` — workflow
  permissions guardrails.
- `python3 -m unittest discover -s tests -p "test_*.py"` — full
  test suite.

---

## Cross-references

- Shipping configuration: [`docs/release-one.md`](release-one.md)
- Room firmware release inventory: [`docs/room-firmware-release-matrix.md`](room-firmware-release-matrix.md)
- Room firmware release notes: [`docs/room-firmware-release-notes.md`](room-firmware-release-notes.md)
- Release-layer gate: [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
- WebFlash-layer gate: [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md)
- Product-layer gate: [`docs/product-readiness-matrix.md`](product-readiness-matrix.md)
- Preview-to-stable gauntlet: [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
- LED preview decision: [`docs/product-led-preview-decision.md`](product-led-preview-decision.md)
- **Stable target expansion plan: [`docs/stable-target-expansion-plan.md`](stable-target-expansion-plan.md) (STABLE-TARGET-EXPANSION-PLAN-001)**
- **Stable target VentIQ gate-closure record: [`docs/stable-target-ventiq-001-gate-closure.md`](stable-target-ventiq-001-gate-closure.md) (STABLE-TARGET-VENTIQ-001)** — per-gate G1–G10 audit for `Ceiling-POE-VentIQ`; documents the deferral and resume conditions; promotes nothing; the 48-YAML classification stays verbatim.
- **PACKAGE-POE-410-001 audit: [`docs/package-poe-410-001-audit.md`](package-poe-410-001-audit.md) (PACKAGE-POE-410-001)** — per-evidence-class audit of `S360-410` Sense360 PoE PSU; records the option-4 outcome (evidence insufficient for verification; precise evidence-request record produced) and the upstream G8 blocker for the five A-row stable expansion candidates (`Ceiling-POE`, `Ceiling-POE-RoomIQ`, `Ceiling-POE-VentIQ`, `Ceiling-POE-AirIQ`, `Ceiling-POE-AirIQ-RoomIQ`). `S360-410` stays `cataloged_unverified`; `packages/hardware/power_poe.yaml` stays byte-identical; the Release-One PoE caveat is preserved verbatim; the 48-YAML classification stays verbatim.
- **Sense360 PoE room bundle SKU matrix: [`docs/sense360-room-bundles.md`](sense360-room-bundles.md) (BUNDLE-SKU-MATRIX-001) — sellable room bundle SKUs (`S360-KIT-BATH-P`, `S360-KIT-KITCHEN-P`, `S360-KIT-LIVING-P`, `S360-KIT-BEDROOM-P`, `S360-KIT-CORRIDOR-P`) mapped onto the release classes this document defines. Bundle SKU is not a firmware config string; promotion of any bundle's likely firmware config target is owned by the named `STABLE-TARGET-*-001` follow-up PR.**
- Kit intent matrix (productized planning): [`docs/kit-intent-matrix.md`](kit-intent-matrix.md) (KIT-MATRIX-001)
- Manual install path: [`docs/manual-install-fan-candidates.md`](manual-install-fan-candidates.md)
- Compile-only lane: [`docs/compile-only-firmware-validation.md`](compile-only-firmware-validation.md)
- Availability vocabulary: [`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md)
- **Reconciled release-matrix / WebFlash / firmware-availability view: [`docs/release-matrix-webflash-alignment.md`](release-matrix-webflash-alignment.md) (WEBFLASH-RELEASE-MATRIX-ALIGNMENT-001)** — one-table canonical release matrix (bundle SKU · config · YAML · channel · compile · artifact · release-note · WebFlash · blocker · notes), bundle verification, target classification, release-note coverage, WebFlash exposure, YAML availability, and the next-release roadmap. Reads from the same source-of-truth files; promotes nothing.

# WebFlash Exposure Readiness Matrix (WEBFLASH-GAP-001)

> **Reconciled view:** the cross-layer release / WebFlash / firmware
> availability reconciliation lives in
> [`docs/release-matrix-webflash-alignment.md`](release-matrix-webflash-alignment.md)
> (WEBFLASH-RELEASE-MATRIX-ALIGNMENT-001). This matrix remains the canonical
> WebFlash-layer gate.

## Purpose and scope

This document is the canonical, **WebFlash-layer** readiness gate for
the candidate product families whose wrappers, catalog entries, and
build-matrix rows are not yet — and in most cases must not yet be —
present in this repo. It sits one layer downstream of the
[`docs/product-readiness-matrix.md`](product-readiness-matrix.md)
PRODUCT-GAP-001 gate. Where that matrix decides whether a product
YAML may be **added**, this matrix decides whether — and how —
a product YAML, once it exists, may be **exposed** through WebFlash:
through a wrapper under [`products/webflash/`](../products/webflash/),
a catalog entry in
[`config/product-catalog.json`](../config/product-catalog.json) with
`webflash_wrapper` / `webflash_build_matrix: true`, a build-matrix
row in [`config/webflash-builds.json`](../config/webflash-builds.json),
a signed release artifact, and an eventual import into the WebFlash
repo's `manifest.json` / `firmware-N.json`.

WEBFLASH-GAP-001 exists because the upstream gates have already made
the WebFlash-layer answer clear and yet potentially confusing. Per
[`product-readiness-matrix.md`](product-readiness-matrix.md), no
candidate product family in the PRODUCT-GAP-001 scope
(FanRelay / FanPWM / FanDAC / FanTRIAC / PWR-240V / PoE-410) carries
`ready-for-product-yaml` today. Per
[`hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md),
none of the six in-scope packages carries
`ready-for-package-change`. Per
[`hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md),
five of the six candidate boards carry `missing` or `partial`
hardware evidence and the sixth (`S360-320` TRIAC) is `blocked` under
HW-005 + COMPLIANCE-001. The downstream conclusion is mechanical: no
new WebFlash wrapper, no new catalog entry, and no new build-matrix
row may be added in this PR. This document records that conclusion,
classifies each candidate family against the WebFlash-exposure axis,
and names the per-family follow-up PRs that would eventually take a
family from "no WebFlash surface" to either preview, advanced /
manual-warning, or — only after the full
[`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
gauntlet — stable / production.

This document is **documentation only**. It does **not**:

- add, remove, or modify any WebFlash wrapper under
  [`products/webflash/`](../products/webflash/) — the production
  Release-One wrapper
  [`products/webflash/ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml),
  the LED preview wrapper
  [`products/webflash/ceiling-poe-ventiq-roomiq-led.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq-led.yaml),
  and the blocked FanTRIAC reference wrapper
  [`products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml)
  all stay verbatim,
- add, remove, or modify any product YAML under
  [`products/`](../products/), including the production
  [`sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml),
  the LED preview
  [`sense360-ceiling-poe-ventiq-roomiq-led.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq-led.yaml),
  the blocked FanTRIAC reference
  [`sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml),
  and any of the 31 `legacy-compatible` Core / Core-Voice / Mini /
  FanPWM / PoE entries,
- add, remove, or modify any package YAML under
  [`packages/`](../packages/) — the six in-scope packages tracked by
  [`package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
  ([`fan_relay.yaml`](../packages/expansions/fan_relay.yaml),
  [`fan_pwm.yaml`](../packages/expansions/fan_pwm.yaml),
  [`fan_gp8403.yaml`](../packages/expansions/fan_gp8403.yaml),
  [`fan_triac.yaml`](../packages/expansions/fan_triac.yaml),
  [`power_240v.yaml`](../packages/hardware/power_240v.yaml),
  [`power_poe.yaml`](../packages/hardware/power_poe.yaml)) plus the
  Core abstract packages
  ([`sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml),
  [`sense360_core.yaml`](../packages/hardware/sense360_core.yaml))
  stay verbatim,
- add, remove, or modify any entry or field in
  [`config/hardware-catalog.json`](../config/hardware-catalog.json),
  [`config/product-catalog.json`](../config/product-catalog.json),
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  or
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json) —
  no new product entry, no `lifecycle_statuses` value, no
  `canonical_modules` token, no `forbidden_tokens` change, no
  `release_one_required_configs` membership, no new build-matrix
  entry, no `webflash_build_matrix` flip,
- add, remove, or modify any script under
  [`scripts/`](../scripts/), any test under
  [`tests/`](../tests/), any workflow under `.github/workflows/`, any
  component under `components/`, any include under `include/`, or any
  firmware artifact under `firmware/` (including
  `firmware/sources.json` and `manifest.json`),
- generate, regenerate, sign, import, deploy, or otherwise produce
  firmware; create or modify any GitHub Release; or change any
  WebFlash-side `REQUIRED_CONFIGS`, `scripts/data/kits.json`,
  `firmware/sources.json`, or `manifest.json` entry,
- promote any candidate product family to `preview` /
  `advanced/manual-warning-only` / `production-candidate`, flip any
  catalog `status`, add any entry to or remove any entry from
  Release-One `release_one_required_configs`, add any kit, move any
  `legacy-compatible` entry off `legacy-compatible`, or unblock the
  FanTRIAC reference entry,
- change the Release-One configuration `Ceiling-POE-VentIQ-RoomIQ`
  (`status: production`, `channel: stable`, version `1.0.0`,
  artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`,
  tag `v1.0.0`),
- change the LED preview entry `Ceiling-POE-VentIQ-RoomIQ-LED`
  (stays `status: preview`, `channel: preview`, version `1.0.0`,
  artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`),
- change the FanTRIAC reference
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` (`status: blocked`,
  `blocker: HW-005`, `webflash_build_matrix: false`),
- change the mains-voltage compliance status of `S360-320` or
  `S360-400` (owned by COMPLIANCE-001;
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)).

If this matrix and any source-of-truth document drift, **the
source-of-truth document wins** and this matrix must be updated. The
sources of truth are listed in [See also](#see-also).

### Namespace note

The identifier `WEBFLASH-GAP-001` is owned by **this readiness
matrix**. It is the WebFlash-layer counterpart of the existing
`HW-GAP-001` / `PACKAGE-GAP-001` / `PRODUCT-GAP-001` gates: a
documentation-only readiness / classification / policy doc, not an
implementation slice. The actual implementation work — adding
WebFlash wrappers, catalog entries, build-matrix rows, release
artifacts, and WebFlash-side imports — is split per family into
separate per-family slice PRs:

- **`WEBFLASH-RELAY-001`** — FanRelay (S360-310) wrapper / catalog /
  build-matrix slice. Gated on `PRODUCT-RELAY-001`.
- **`WEBFLASH-PWM-001`** — FanPWM (S360-311) wrapper / catalog /
  build-matrix slice. Gated on `PRODUCT-PWM-001`.
- **`WEBFLASH-DAC-001`** — FanDAC (S360-312) wrapper / catalog /
  build-matrix slice. Gated on `PRODUCT-DAC-001`.
- **`WF-TRIAC-001`** — FanTRIAC (S360-320) advanced /
  manual-warning-only wrapper / catalog / build-matrix slice with the
  manual-warning UX gate enforced. Gated on `PRODUCT-TRIAC-001`
  (landed: notes-only catalog policy decided) + `PRODUCT-TRIAC-002`
  (product YAML / catalog-entry rework) + `COMPLIANCE-001` advanced
  / manual-warning sign-off + WebFlash-side manual-warning UX. Never
  standard, never recommended, never kit / default, never
  `release_one_required_configs`.
- **`WEBFLASH-POWER-400-001`** — PWR-240V (S360-400) wrapper /
  catalog / build-matrix slice. Gated on `PRODUCT-POWER-400-001` and
  `COMPLIANCE-001` `S360-400` slice closure.
- **`WEBFLASH-POE-410-001`** — PoE-410 (S360-410) wrapper / catalog /
  build-matrix slice, **only if** `PRODUCT-POE-410-001` decides a
  separate WebFlash-shippable product entry is warranted. Often this
  slice closes by extending the Release-One caveat record without
  adding a new product / wrapper at all.
- **`RELEASE-GAP-001`** — Build / sign / release the firmware
  artifacts for whatever WebFlash entries the per-family slices have
  added. Uses the existing
  [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)
  flow and the existing artifact-naming validators.
- **`WF-IMPORT-GAP-001`** — Import the signed artifacts into the
  WebFlash repo's `manifest.json` / `firmware-N.json` per
  [`docs/webflash-release-handoff.md`](webflash-release-handoff.md).
  Owned by the WebFlash repo, not this repo.

Historical references that name `WEBFLASH-GAP-001` as the PR that
"adds wrappers / catalog / build-matrix entries for selected new
products" should be read as referring to this readiness / gating
matrix unless a later per-family slice (`WEBFLASH-RELAY-001`,
`WEBFLASH-PWM-001`, `WEBFLASH-DAC-001`, `WF-TRIAC-001`,
`WEBFLASH-POWER-400-001`, `WEBFLASH-POE-410-001`) is explicitly
named. The existing follow-up tables in
[`product-readiness-matrix.md` row #9 of the Follow-up PR sequence](product-readiness-matrix.md#follow-up-pr-sequence)
and
[`hardware/board-readiness-matrix.md` row #9 of the Follow-up PR sequence](hardware/board-readiness-matrix.md#follow-up-pr-sequence)
remain valid by reference; they are not rewritten by this PR.

## Core rule

> **WebFlash exposure requires every upstream gate — hardware
> evidence, pin / package mapping, package YAML readiness, product
> YAML existence, catalog status decision, wrapper presence,
> build-matrix approval, release artifact, and WebFlash-side import —
> to be satisfied for the intended exposure class. Product YAML
> existence alone does not imply WebFlash exposure. Each gate is a
> separate, named follow-up PR. No gate is skipped, collapsed, or
> implied by another.**

This is the load-bearing premise of WEBFLASH-GAP-001. It is the
WebFlash-layer form of the
[`package-readiness-matrix.md` Core rule](hardware/package-readiness-matrix.md#core-rule)
("package YAML changes are allowed only when the target board has
verified pin-map evidence") and of the
[`product-readiness-matrix.md` Core rule](product-readiness-matrix.md#core-rule)
("package readiness, product readiness, and WebFlash exposure are
three separate gates; product YAML existence does not itself
authorise WebFlash exposure").

The full chain a WebFlash-shippable product must climb, in order:

1. **Hardware evidence and pin / package mapping** adequate for the
   intended exposure class. Verified per
   [`hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
   and the per-board `HW-PINMAP-*` audit docs.
2. **Package YAML readiness.** The product's required package(s) are
   `ready-for-package-change` per
   [`hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md),
   and the Core abstract-bus rebind (CORE-ABSTRACT-BUS-001) has
   landed where the product consumes the Ceiling Core abstract
   package.
3. **Product YAML existence and approval.** A canonical product YAML
   exists under [`products/`](../products/) and has cleared
   [`product-onboarding.md`](product-onboarding.md). Per
   [`product-readiness-matrix.md`](product-readiness-matrix.md) row
   classification.
4. **Product catalog status chosen intentionally.** The catalog
   `status` in
   [`config/product-catalog.json`](../config/product-catalog.json)
   is one of `production` / `preview` / `compile-only` /
   `hardware-pending` / `blocked` / `legacy-compatible`, chosen with
   reference to
   [`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md).
5. **WebFlash wrapper exists.** A thin wrapper YAML lives under
   [`products/webflash/`](../products/webflash/) and conforms to the
   WebFlash compatibility grammar in
   [`config/webflash-compatibility.json`](../config/webflash-compatibility.json).
6. **Build-matrix entry approved.** The product appears as a
   `webflash_build_matrix: true` row in the catalog with a matching
   row in
   [`config/webflash-builds.json`](../config/webflash-builds.json),
   validated by
   [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py)
   and
   [`tests/test_webflash_compatibility.py`](../tests/test_webflash_compatibility.py).
7. **Release artifact exists.** A signed firmware artifact with the
   canonical
   `Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin` name has been
   built and released via
   [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml),
   validated by
   [`tests/test_webflash_artifact_naming.py`](../tests/test_webflash_artifact_naming.py)
   and the release-notes validators.
8. **Import-readiness passes in WebFlash.** The artifact is importable
   into the WebFlash repo's `manifest.json` / `firmware-N.json` per
   [`webflash-release-handoff.md`](webflash-release-handoff.md).
9. **Exposure class is respected.** The product's surfacing in the
   WebFlash flasher honours its declared class — `none`,
   `docs-only / manual YAML only`, `preview-candidate`,
   `advanced/manual-warning-only`, `production-candidate`, or
   `legacy-only` (see [Exposure classes](#exposure-classes) below).
   REQUIRED_CONFIGS / kit / recommended membership is a strictly
   additional gate (see [REQUIRED_CONFIGS policy](#required_configs-policy)
   and [Kit / recommended path policy](#kit--recommended-path-policy)).

Two corollaries follow:

- **Skipping a gate is not allowed.** A future PR that, for example,
  adds a build-matrix entry without first landing a wrapper, or
  flips `webflash_build_matrix: true` without a release artifact,
  must be rejected on first read.
- **Reaching a gate is not the same as reaching the next.** A
  product YAML that has cleared
  [`product-onboarding.md`](product-onboarding.md) has cleared step 3
  only; the wrapper / catalog / build / release / import / exposure
  decisions remain separately gated by this matrix and the per-family
  slice PRs above.

## Status value vocabulary (policy-only)

The candidate exposure table below uses a small set of cell values.
**All are policy-only labels** — they are not JSON enums, not promoted
to any schema, and not added to any validator by this PR. They sit
alongside the existing
[`config/product-catalog.json`](../config/product-catalog.json)
`lifecycle_statuses`
(`production` / `preview` / `compile-only` / `hardware-pending` /
`blocked` / `legacy-compatible` / `deprecated` / `removed`), the
[`product-availability-taxonomy.md`](product-availability-taxonomy.md)
13-rung ladder, the
[`package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
package labels, and the
[`product-readiness-matrix.md`](product-readiness-matrix.md) product
labels that this matrix consumes for the upstream-gate columns.

| Cell value | Meaning |
|---|---|
| `not-webflash-ready` | The candidate family is **not** eligible for any new WebFlash surface today. The cause is identified by one or more of the more specific labels below. Carried by every candidate row in this matrix as the primary "Allowed WebFlash action now" verdict. |
| `missing-product-yaml` | No canonical product YAML exists under [`products/`](../products/) for the family, and `product-readiness-matrix.md` has not marked the family `ready-for-product-yaml`. The follow-up is the per-family `PRODUCT-*-001` slice. Until that slice lands, no WebFlash wrapper / catalog entry / build-matrix entry may be added. |
| `missing-package-readiness` | At least one required package for the family is **not** `ready-for-package-change` per [`hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md). The follow-up is the per-family `PACKAGE-*-001` slice. Until that slice lands, no `PRODUCT-*-001` slice may add a product YAML, so no WebFlash surface may be added. |
| `missing-hardware-evidence` | At least one required board carries `schematic-evidence-pending` or `hardware-evidence-pending` per [`hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md) and the per-board `HW-PINMAP-*` audit doc. The follow-up is the per-board `HW-ASSETS-*` supplier-delivery + `HW-PINMAP-*-FOLLOWUP` reconciliation. Until that lands, package readiness cannot advance. |
| `preview-candidate` | If and when the per-family product slice lands, the eventual WebFlash exposure class is `preview-candidate`: canonical YAML + wrapper + catalog entry + build-matrix entry on a non-`stable` channel (typically `preview`), with the WebFlash-side import optional / staged. The first stable promotion would later require the full 17-row [`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md) gauntlet. |
| `advanced/manual-warning-only` | If and when the per-family product slice lands, the eventual WebFlash exposure class is `advanced/manual-warning-only`: reachable only behind an explicit advanced-flow / manual-warning UX, never on the standard landing list, never in `release_one_required_configs`, never kit / recommended / default. Today this applies only to FanTRIAC; the long-term posture is documented in [`hardware/s360-320-r4-triac.md` Advanced / manual-warning product posture](hardware/s360-320-r4-triac.md#advanced--manual-warning-product-posture) and is now policy-recorded by `PRODUCT-TRIAC-001` as a notes-only catalog edit (JSON `status: blocked` / `blocker: HW-005` / `webflash_build_matrix: false` unchanged; no new lifecycle enum). A live WebFlash surface still requires HW-005 + COMPLIANCE-001 + `HW-PINMAP-320-FOLLOWUP` + `PACKAGE-TRIAC-001` + `PRODUCT-TRIAC-002` + `WF-TRIAC-001` to clear. |
| `standard-exposure-candidate` | If and when the per-family product slice lands, the eventual WebFlash exposure class will be standard (i.e. `preview-candidate` → `production-candidate` subject to the promotion gauntlet), without an advanced / manual-warning UX qualifier. The standard / advanced distinction is decided per family on first per-family product-slice PR, not by this matrix. |
| `production-candidate` | If and when the per-family product slice lands **and** the full 17-row [`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md) gauntlet clears, the eventual WebFlash exposure class is `production-candidate`: canonical YAML + wrapper + catalog entry + build-matrix entry on `stable`, signed release artifact, WebFlash-side import live. Today carried only by `Ceiling-POE-VentIQ-RoomIQ`; no candidate family in this matrix is `production-candidate` today. |
| `not-required-configs` | Even after a family has reached `preview-candidate` (or beyond), it is **not** added to `release_one_required_configs` by default. Any addition is a separately gated, explicit PR per [REQUIRED_CONFIGS policy](#required_configs-policy). |
| `not-recommended` | Even after a family has reached `preview-candidate` (or beyond), it is **not** added to recommended-product surfaces by default. See [Kit / recommended path policy](#kit--recommended-path-policy). |
| `not-kit-default` | Even after a family has reached `preview-candidate` (or beyond), it is **not** added to kit / default-bundle surfaces (`scripts/data/kits.json` etc. in the WebFlash repo) by default. See [Kit / recommended path policy](#kit--recommended-path-policy). |
| `docs-only` | The family's WebFlash exposure is intentionally bounded to manual YAML use only; the user installs by `esphome run` rather than via the WebFlash flasher. Carried today by the 31 `legacy-compatible` entries. No new `docs-only` entry is added by this PR. |
| `legacy-only` | The family already has a `legacy-compatible` product YAML under [`products/`](../products/) but no WebFlash wrapper / catalog `webflash_wrapper` / `webflash_build_matrix: true`. PRODUCT-GAP-001 does not move any `legacy-compatible` entry off legacy, and WEBFLASH-GAP-001 does not add a non-legacy WebFlash surface for any legacy family. Carried today by the legacy four-channel [`products/sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml) and the legacy [`products/sense360-poe.yaml`](../products/sense360-poe.yaml). |
| `blocked-from-standard-exposure` | The family must never be added to Release-One, `release_one_required_configs`, recommended / kit / default surfaces, or compliance-certified surfaces, regardless of any future product YAML existence. Carried by FanTRIAC. Applied as an additive qualifier alongside `advanced/manual-warning-only`. |
| `unknown` | Cannot be classified from currently committed evidence. Not used in this matrix today; every candidate family below is placeable under the labels above. |

A row may carry one primary "Allowed WebFlash action now" label
(typically `not-webflash-ready`) plus a future-exposure-class label
(`preview-candidate` / `advanced/manual-warning-only` /
`standard-exposure-candidate`) plus any number of additive
qualifier labels (`not-required-configs` / `not-recommended` /
`not-kit-default` / `blocked-from-standard-exposure`) and one or
more cause labels (`missing-product-yaml` /
`missing-package-readiness` / `missing-hardware-evidence`).

## Exposure classes

WebFlash exposure is a discrete classification with six values. Every
product / candidate family lands at exactly one class at any given
moment. Movement up the ladder requires the upstream gates plus a
named per-family slice PR (see [Follow-up PR sequence](#follow-up-pr-sequence)).

| Class | Means | Used today by |
|---|---|---|
| `none` | No product YAML; no wrapper; no catalog entry; no build-matrix entry; not reachable through WebFlash in any form. | Every candidate family in this matrix (FanRelay / FanPWM / FanDAC / FanTRIAC product-side exposure / PWR-240V / PoE-410). Also the default state for any new product family that has not begun the product-onboarding flow. |
| `docs-only` / `manual YAML only` | A canonical YAML exists under [`products/`](../products/) but the catalog entry is `legacy-compatible` (no `config_string`, no `webflash_wrapper`, no `artifact_name`, `webflash_build_matrix: false`). The user installs by manual `esphome run`. | The 31 `legacy-compatible` Core / Core-Voice / Mini / `sense360-fan-pwm.yaml` / `sense360-poe.yaml` entries in [`config/product-catalog.json`](../config/product-catalog.json). |
| `preview-candidate` | Canonical YAML + WebFlash wrapper + catalog entry + build-matrix entry on a non-`stable` channel (typically `preview`); WebFlash-side import optional / staged. | `Ceiling-POE-VentIQ-RoomIQ-LED` only. Each additional `preview-candidate` requires a separate per-family slice PR. |
| `advanced/manual-warning-only` | Reachable through WebFlash only behind an explicit advanced-flow / manual-warning UX, never on the standard landing list, never in `release_one_required_configs`, never kit / recommended / default. The wrapper / catalog / build-matrix slice must carry the manual-warning UX gate and (for mains-voltage products) `COMPLIANCE-001` sign-off. | The intended long-term posture for FanTRIAC. Today the catalog `status` for `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` is `blocked` under HW-005 and `webflash_build_matrix: false`; no live WebFlash surface exists. Posture is `WF-TRIAC-001` responsibility, not realised here. |
| `production-candidate` | Canonical YAML + WebFlash wrapper + catalog entry + build-matrix entry on `stable`; signed release artifact; WebFlash-side import live. | `Ceiling-POE-VentIQ-RoomIQ` only (Release-One). Any new `production-candidate` entry must clear the full 17-row [`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md) gauntlet. |
| `legacy-only` | The canonical YAML exists but is `legacy-compatible`; the family is not in the WebFlash build matrix and is not promoted by PRODUCT-GAP-001 or by any per-family `WEBFLASH-*-001` slice. | The legacy four-channel [`products/sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml) and [`products/sense360-poe.yaml`](../products/sense360-poe.yaml), plus the 29 `core-*` / `mini-*` legacy entries (which more precisely sit at `docs-only`; "legacy-only" is the additive qualifier that prevents non-legacy siblings being added). |

The rule:

> **`advanced/manual-warning-only` is an explicit WebFlash *exposure*
> class, not a certification claim and not a compliance verdict. A
> family classified `advanced/manual-warning-only` is buildable and
> installable through WebFlash only behind a manual-warning UX gate;
> any compliance / safety / regulatory certification (UK / EU
> mains-voltage in particular) is a separate `COMPLIANCE-001` gate
> that runs in addition.**

## Current WebFlash surface

The current WebFlash surface — taken verbatim from
[`config/product-catalog.json`](../config/product-catalog.json) and
[`config/webflash-builds.json`](../config/webflash-builds.json) and
unchanged by this PR — is as follows.

| Config string | Catalog `status` | `channel` | `webflash_wrapper` | `webflash_build_matrix` | Artifact | Exposure class |
|---|---|---|---|---|---|---|
| `Ceiling-POE-VentIQ-RoomIQ` | `production` | `stable` | [`products/webflash/ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml) | `true` | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` | `production-candidate` (Release-One). |
| `Ceiling-POE-VentIQ-RoomIQ-LED` | `preview` | `preview` | [`products/webflash/ceiling-poe-ventiq-roomiq-led.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq-led.yaml) | `true` | `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` | `preview-candidate` (PRODUCT-009; LED preview). |
| `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` | `blocked` (`blocker: HW-005`) | — | [`products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml) | `false` | — | Blocked reference. Posture intent: `advanced/manual-warning-only` once HW-005 + COMPLIANCE-001 + `WF-TRIAC-001` clear. |
| 31 `legacy-compatible` entries (Core / Core-Voice / Mini / `sense360-fan-pwm.yaml` / `sense360-poe.yaml`) | `legacy-compatible` | — | — | `false` | — | `docs-only` / `legacy-only`. |

`release_one_required_configs` in
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
is the single entry `["Ceiling-POE-VentIQ-RoomIQ"]`. No
candidate family in this matrix is added to it. The LED preview is
**not** in `release_one_required_configs` and remains explicitly
outside; FanTRIAC is **never** added.

> **Cross-repo drift note — `WEBFLASH-DRIFT-001` (2026-05-26).** The standing
> cross-repo drift audit is [`docs/webflash-drift-audit.md`](webflash-drift-audit.md).
> It found **no confirmed product/import drift** between this matrix's surface and
> the (prior-recorded, PR #565) WebFlash side: the 2 shippable builds, their
> artifact names, the default-kit posture, and the outcome-first naming all
> `MATCH`; Relay/DAC/PWM/TRIAC are `INTENTIONALLY-BLOCKED` (absent on both sides);
> and the WebFlash `manifest.json`'s 3rd build is the WebFlash-owned **Rescue**
> recovery image (esphome-public ships 2 product builds, by design — not drift).
> Axes needing a live-WebFlash re-run (`artifact_pattern` source, grammar-validator
> parity, full channel list, PWM/DAC `module-availability.js`) are recorded as
> `NEEDS-OPERATOR-INPUT` there.

## Candidate exposure table

The table below is the matrix's primary deliverable. Each row is a
candidate **product family** (not a candidate product YAML; this
matrix does not enumerate per-config-string variants because no
candidate family today carries a product YAML to enumerate against).
Every cell is a policy label as defined in
[Status value vocabulary](#status-value-vocabulary-policy-only) and
[Exposure classes](#exposure-classes) above.

| Candidate family | Required product YAML | Required package status | Current product readiness | Current WebFlash wrapper | Current build-matrix status | Allowed WebFlash action now | Future exposure class | REQUIRED_CONFIGS eligibility | Kit / recommended eligibility | Follow-up owner |
|---|---|---|---|---|---|---|---|---|---|---|
| **FanRelay / S360-310** | exists at [`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml) (PRODUCT-RELAY-001 / PR #564 landed; advanced / manual-warning-only sibling of Release-One; carries explicit installation / safety / competent-person caveat wording); product-layer disposition stays `advanced/manual-warning-only` + product-YAML-landed (no WebFlash) per [`product-readiness-matrix.md`](product-readiness-matrix.md#fanrelay--s360-310) | **`package-implemented` + `reconciled-at-package-layer`** (S360-310 module-side schematic committed under HW-ASSETS-310; HW-PINMAP-310-FOLLOWUP consumed the schematic; `CORE-ABSTRACT-BUS-001C` / PR #557 freed `GPIO3`; `CORE-ABSTRACT-BUS-001A` / PR #558 rebound `relay_pin: GPIO3`; `S360-310-BENCH-EVIDENCE-001` / PR #561 populated the ten enumerated hardware-evidence rows from operator-attested + BOM-backed + public-reference-backed sources, with no photo / video / oscilloscope / continuity-meter artifacts attached; `PACKAGE-RELAY-001` / PR #562 added [`tests/test_fan_relay_package.py`](../tests/test_fan_relay_package.py) pinning the FanRelay package abstraction without a YAML edit) | **`product-yaml-landed`** + `product-layer-blockers-narrowed` per [`product-readiness-matrix.md`](product-readiness-matrix.md#fanrelay--s360-310); product-layer blockers narrowed but residual: production-wide / multi-unit `GPIO3` strap-pin boot characterisation; board-level mains-safety / installation-approval evidence; independent competent-person sign-off | none | none | `not-webflash-ready` — **WebFlash Relay exposure remains blocked even though `PRODUCT-RELAY-001` / PR #564 has now landed the product YAML.** Per the [`product-readiness-matrix.md` §FanRelay / S360-310](product-readiness-matrix.md#fanrelay--s360-310) PRODUCT-RELAY-001 audit-log entry, the product YAML carries explicit advanced / manual-warning wording but explicitly does not add a WebFlash wrapper / catalog flip / build-matrix row / release artifact. WebFlash exposure is owned by a separate `WEBFLASH-RELAY-001` slice gated on (1) explicit `WEBFLASH-RELAY-001` implementation approval; (2) advanced / manual-warning UI copy; (3) competent-person / installation warning flow; (4) product not default / not recommended; (5) release artifact must exist before WebFlash import; (6) no stable / preview promotion until explicit approval; (7) production-wide / installation / safety caveats remain separate from any WebFlash surface. | `advanced/manual-warning-only` (long-term posture; not the default `preview-candidate` standard-exposure ladder rung — the readiness refresh explicitly rejects `preview-candidate` for FanRelay because a mains-switching driver without installation / safety wording or a competent-person caveat is not appropriate for standard preview surfacing). User-facing naming, if and when WebFlash exposure ever lands, is **outcome-first** (e.g. "Switched fan control" or "Relay fan control"), not loose board / module naming such as "S360-310 board" or "Sense360 Relay board" — this matches the WebFlash repo's already-shipped outcome-first convention ("Fan relay control" in Step 4 module cards; "Sense360 Bathroom Kit — Relay Fan Control" in the Stage 1 bundle preset `S360-KIT-BATH-RELAY`). | **`not-required-configs` — never by default.** Any future addition to `release_one_required_configs` would be a separate, explicit PR with installation-safety + competent-person sign-off and is **not** authorised by this matrix. | **`not-recommended` + `not-kit-default` — never by default.** Mains-switching products without installation / safety wording and a competent-person caveat are categorically excluded from kit / default / recommended surfaces until a separate UX + compliance / installation-method sign-off lands. | `HW-ASSETS-310` *(landed)* → `HW-PINMAP-310-FOLLOWUP` *(landed)* → `CORE-ABSTRACT-BUS-001C` *(landed PR #557)* → `CORE-ABSTRACT-BUS-001A` *(landed PR #558)* → `PACKAGE-RELAY-001-READINESS-REFRESH` *(landed PR #559)* → `S360-310-BENCH-001` *(landed PR #560)* → `S360-310-BENCH-EVIDENCE-001` *(landed PR #561)* → `PACKAGE-RELAY-001` *(landed PR #562 — test + readiness reconciliation at the package layer only)* → `PRODUCT-RELAY-001-READINESS-REFRESH` *(landed PR #563)* → `PRODUCT-RELAY-001` *(landed PR #564 — product YAML only; no WebFlash wrapper / catalog flip / build-matrix entry / release artifact)* → **`WEBFLASH-RELAY-001-READINESS-REFRESH`** *(this PR; docs-only readiness re-evaluation after PRODUCT-RELAY-001)* → `WEBFLASH-RELAY-001` (advanced / manual-warning WebFlash wrapper / catalog / build-matrix; only after additional production-wide hardware characterisation + installation / competent-person sign-off + WebFlash-side manual-warning UX parity) → `RELEASE-RELAY-001` → `WF-IMPORT-RELAY-001` (cross-repo). |
| **FanPWM / S360-311** | product-YAML-only (`products/sense360-ceiling-poe-fanpwm.yaml`, config string `Ceiling-POE-FanPWM`, PRODUCT-PWM-001 / this PR; `webflash_build_matrix: false`, no wrapper, no `artifact_name`, no release artifact; PWM-drive-only, **no RPM**); the legacy four-channel [`products/sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml) stays `legacy-compatible` only | `package-layer-implemented` (PACKAGE-PWM-001-IMPLEMENT-001 / PR #590 — PWM-drive-only; four SX1509 PWM-drive controllers; `packages/expansions/fan_pwm.yaml` composes `fan_pwm_sx1509.yaml`; no `pulse_counter`, no RPM, `TachIO`/`GPIO16` reserved) + `compile-only-target-landed` + `compile-pass-validated-full-compile` (FW-COMPILE-PWM-001 / PR #591 added the `Ceiling-POE-FanPWM` compile-only target; CI `--compile` passed in run `26414398902`, FW-COMPILE-PWM-RESULT-001 / PR #592) | `product-yaml-landed` + `compile-pass-validated-full-compile` + `no-rpm` per [`product-readiness-matrix.md`](product-readiness-matrix.md#fanpwm--s360-311) | none | none | `not-webflash-ready` — **WebFlash PWM exposure remains blocked even though `PRODUCT-PWM-001` has now landed the product YAML.** The product YAML adds no WebFlash wrapper / catalog flip / build-matrix row / release artifact; WebFlash exposure is owned by a separate `WEBFLASH-PWM-001` slice. | `preview-candidate` (standard exposure once `WEBFLASH-PWM-001` + the S360-311 bench gates land) | `not-required-configs` | `not-recommended` + `not-kit-default` (legacy four-channel YAML retention / migration / removal decided by `PRODUCT-PWM-001`) | `HW-PINMAP-311-FOLLOWUP` → `PACKAGE-PWM-001-IMPLEMENT-001` *(PR #590)* → `FW-COMPILE-PWM-001` *(PR #591)* → `FW-COMPILE-PWM-RESULT-001` *(PR #592)* → **`PRODUCT-PWM-001`** *(this PR; product-YAML-only)* → `WEBFLASH-PWM-001` → `RELEASE-PWM-001` → `WF-IMPORT-GAP-001`. |
| **FanDAC / S360-312** | product-YAML-only (`products/sense360-ceiling-poe-fandac.yaml`, config string `Ceiling-POE-FanDAC`, PRODUCT-DAC-001 / this PR; `webflash_build_matrix: false`, no wrapper, no `artifact_name`); respects the `FanDAC ↔ AirIQ` mutex (`config/webflash-compatibility.json` `rules.fandac_conflicts_with_airiq: true`) | `package-layer-implemented` (PACKAGE-DAC-001 / PR #573 — two GP8403 chips, four neutral outputs, per-chip address + range substitutions; `packages/expansions/fan_gp8403.yaml` `package-layer-implemented`) + `voltage-enum-fixed` + `compile-only-target-landed` + `compile-pass-validated-full-compile` (FW-COMPILE-DAC-001 / PR #575 fixed the `gp8403:` `voltage:` substitutions `0-10V` → ESPHome's `10V` enum and added the `Ceiling-POE-FanDAC` compile-only target; CI `--compile` pass passed in run `26364679370`, flag flipped by COMPILE-STATUS-FLAGS-001) | `missing-product-yaml` + `compile-pass-validated-full-compile` + `invalid-combination` with any AirIQ-bearing variant per [`product-readiness-matrix.md`](product-readiness-matrix.md#fandac--s360-312) | none | none | `not-webflash-ready` | `preview-candidate` (standard exposure; AirIQ-bearing FanDAC variants forbidden by mutex) | `not-required-configs` | `not-recommended` + `not-kit-default` (FanDAC ↔ AirIQ mutex narrows the eligible config-string space; kit / recommended decision belongs to `PRODUCT-DAC-001`) | `PACKAGE-DAC-001` *(PR #573)* → `FW-COMPILE-DAC-001` *(this PR)* → `PRODUCT-DAC-001` → `WEBFLASH-DAC-001` → `RELEASE-DAC-001` → `WF-IMPORT-DAC-001`. |
| **FanTRIAC / S360-320** | exists as the **blocked** reference [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml); catalog status `blocked`, blocker `HW-005`, `webflash_build_matrix: false`; `PRODUCT-TRIAC-001` has performed a **notes-only** catalog edit recording the advanced / manual-warning candidate posture without changing any structural field. No new product YAML is added by `WEBFLASH-GAP-001`. | `missing` (S360-320 schematic committed; `ac_dimmer` timing across SX1509 expander rejected; `fan_triac.yaml` `needs-package-reconciliation` + `timing/compliance-pending` + `blocked-from-standard-exposure`) | `timing/compliance-pending` + `advanced/manual-warning-only` (policy-recorded by `PRODUCT-TRIAC-001` notes-only) + `blocked-from-standard-exposure` per [`product-readiness-matrix.md`](product-readiness-matrix.md#fantriac--s360-320); HW-005 unblock + COMPLIANCE-001 sign-off required before any product / WebFlash motion | exists for the blocked reference; `webflash_build_matrix: false` | not in the build matrix | `not-webflash-ready` (blocked reference wrapper retained as evidence; no live build / WebFlash surface) | `advanced/manual-warning-only` (long-term posture; policy-recorded by `PRODUCT-TRIAC-001` notes-only; reach to a live WebFlash surface still requires `WF-TRIAC-001` after `PACKAGE-TRIAC-001` + `PRODUCT-TRIAC-002` + `COMPLIANCE-001` advanced / manual-warning sign-off + WebFlash-side manual-warning UX) | **`not-required-configs` — never by default.** Any future addition to `release_one_required_configs` would be a separate explicit, scoped PR with COMPLIANCE-001 sign-off and is **not** authorised by this matrix. | **`not-recommended` + `not-kit-default` — never by default.** Mains-voltage advanced / manual-warning products are categorically excluded from kit / default / recommended / Release-One surfaces, irrespective of any future product YAML existence. | `PRODUCT-TRIAC-001` (landed: notes-only catalog reclassification) → `HW-005` resolution → `HW-PINMAP-320-FOLLOWUP` → `PACKAGE-TRIAC-001` → `PRODUCT-TRIAC-002` → `COMPLIANCE-001` advanced / manual-warning sign-off → `WF-TRIAC-001` (advanced / manual-warning WebFlash slice) → `RELEASE-TRIAC-001` → `WF-IMPORT-TRIAC-001`. See [`hardware/s360-320-r4-triac.md` Follow-up PR sequence](hardware/s360-320-r4-triac.md#follow-up-pr-sequence). |
| **PWR-240V / S360-400** | none (the four `legacy-compatible` `*-pwr` Core variants are `*-pwr` mains-power Core configurations only; no WebFlash-shippable PWR-240V product entry exists) | `missing` (S360-400 module-side schematic committed under HW-ASSETS-400 / PR #514 at [`hardware/schematics/S360-400-R4.pdf`](hardware/schematics/S360-400-R4.pdf) with curated artifact index at [`hardware/artifacts/S360-400-R4.md`](hardware/artifacts/S360-400-R4.md); HW-PINMAP-400-FOLLOWUP consumed both and promoted [`s360-400-r4-power.md`](hardware/s360-400-r4-power.md) to `partial — schematic evidence available; package reconciliation, BOM, silkscreen, creepage/clearance, and COMPLIANCE-001 pending`; `packages/hardware/power_240v.yaml` stays `schematic-evidence-pending` + `timing/compliance-pending` under COMPLIANCE-001 — three-way `HLK-5M05` / `HLK-PM01 or similar` / `HLK-10M05` part-identity disagreement + silkscreen + BOM + creepage/clearance + compliance still owed) | `schematic-evidence-pending` + `timing/compliance-pending` per [`product-readiness-matrix.md`](product-readiness-matrix.md#pwr-240v--s360-400); COMPLIANCE-001 `S360-400` slice closure required before any product / WebFlash motion | none | none | `not-webflash-ready` | `preview-candidate` (standard exposure once schematic-backed pin-map + compliance gates clear; advanced / manual-warning posture **not** the default for PWR-240V, but the per-family `PRODUCT-POWER-400-001` slice decides) | `not-required-configs` | `not-recommended` + `not-kit-default` (mains-voltage compliance posture is gating-priority over exposure decision; kit / recommended decision belongs to `PRODUCT-POWER-400-001`) | `HW-ASSETS-400` *(landed at PR #514)* → `HW-PINMAP-400-FOLLOWUP` *(this PR; docs-only)* → BOM + silkscreen + creepage / clearance + bench / thermal / EMI evidence → `PACKAGE-POWER-400-001` → `COMPLIANCE-001` S360-400 slice closure → `PRODUCT-POWER-400-001` → `WEBFLASH-POWER-400-001` → `RELEASE-GAP-001` → `WF-IMPORT-GAP-001`. |
| **PoE-410 / S360-410** | none directly; the verified S360-410 PoE PSU is consumed only by Release-One (`Ceiling-POE-VentIQ-RoomIQ`) and the LED preview (`Ceiling-POE-VentIQ-RoomIQ-LED`) under their existing schematic-pending caveat | S360-410 schematic committed under HW-ASSETS-410 / PR #516 at [`docs/hardware/schematics/S360-410-R4.pdf`](hardware/schematics/S360-410-R4.pdf) (975,137 bytes; SHA256 `4a8b7a3b2a89006a9332eaa486743f687aaedc4b6bb807c6b25670f742ac2414`) with curated artifact index at [`docs/hardware/artifacts/S360-410-R4.md`](hardware/artifacts/S360-410-R4.md); HW-PINMAP-410-FOLLOWUP has consumed both and promoted [`docs/hardware/s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md) to `partial`; `packages/hardware/power_poe.yaml` stays `reference-only` + `schematic-evidence-pending` + `do-not-change-release-one` | `schematic-evidence-pending` per [`product-readiness-matrix.md`](product-readiness-matrix.md#poe-410--s360-410); per the matrix, "often this slice will close by promoting Release-One's preserved schematic-pending caveat alone, without adding a new product entry" | none new; existing Release-One wrapper unchanged | none new; existing Release-One row unchanged | `not-webflash-ready` for any **new** PoE-410 product entry. Existing Release-One PoE consumption is **not** affected; Release-One wrapper / catalog / build / artifact stays verbatim | `preview-candidate` (only if a new product entry is added; the default close is no-new-entry / caveat-closure-only) | `not-required-configs` (Release-One's existing membership is not touched) | `not-recommended` + `not-kit-default` (no new product entry implies no new kit / recommended membership) | `HW-ASSETS-410` (PR #516) → `HW-PINMAP-410-FOLLOWUP` (this PR) → BOM cross-check → `S360-100-BENCH-001` update / `HW-002 OQ#6` closure → `S360-410` `schematic_status: verified` JSON PR → `PACKAGE-POE-410-001` → `PRODUCT-POE-410-001` (if warranted) → `WEBFLASH-POE-410-001` (if a new product entry is added) → `RELEASE-GAP-001` → `WF-IMPORT-GAP-001`. |

No row in this table carries `standard-exposure-candidate` or
`production-candidate` as a *current* class today; every row is
`not-webflash-ready` at the present moment. The future-exposure
column records the **eventual** class each family would reach if and
only if the named upstream gates close.

## Relay / S360-310 WebFlash posture

**Current state.** `S360-310 Sense360 Relay`,
`schematic_status: cataloged_unverified`, no `schematic_file`.
**Module-side schematic PDF committed under HW-ASSETS-310** at
[`docs/hardware/schematics/S360-310-R4.pdf`](hardware/schematics/S360-310-R4.pdf)
and curated artifact index committed at
[`docs/hardware/artifacts/S360-310-R4.md`](hardware/artifacts/S360-310-R4.md).
**HW-PINMAP-310-FOLLOWUP** consumed the schematic and promoted
[`s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md) from
`pending — schematic/design evidence required` to
`partial — schematic evidence available; package reconciliation
pending`; the audit records the schematic-backed module-`J2` ↔
Core-`J4` logical net match (`+5V` ↔ `+5V`, `Relay` ↔ `Relay`,
`GND` ↔ `GND`) and the module-side relay coil-drive topology
(`Q1` MMBT3904 NPN low-side; `R1` 1 kΩ; `R2` 10 kΩ; `D1` flyback;
coil rail `+5V`; no opto; no indicator LED; no snubber).
**`CORE-ABSTRACT-BUS-001C` / PR #557 freed `GPIO3`**;
**`CORE-ABSTRACT-BUS-001A` / PR #558 rebound `relay_pin: GPIO3`**
across the five non-voice Core abstract packages.
**`S360-310-BENCH-001` / PR #560 added the bench-evidence
checklist**; **`S360-310-BENCH-EVIDENCE-001` / PR #561 populated
the ten enumerated hardware-evidence rows** from operator-attested
+ BOM-backed + public-reference-backed sources (no photo / video /
oscilloscope / continuity-meter artifacts attached).
**`PACKAGE-RELAY-001` / PR #562 implemented / reconciled the
FanRelay package at the package layer only**: the package
[`packages/expansions/fan_relay.yaml`](../packages/expansions/fan_relay.yaml)
was already structurally correct (`fan_relay_pin: ${relay_pin}`
line 27 inherits the parent Core abstract package binding, which
post-001A resolves to the schematic-correct `GPIO3`) and the
reconciliation is the addition of
[`tests/test_fan_relay_package.py`](../tests/test_fan_relay_package.py)
pinning the FanRelay package abstraction against future regression.
[`hardware/package-readiness-matrix.md` §fan_relay.yaml](hardware/package-readiness-matrix.md#fan_relayyaml--s360-310)
records the row as `package-implemented` +
`reconciled-at-package-layer`. **`PRODUCT-RELAY-001` has now
landed** as a product-YAML-only / no-WebFlash-exposure slice: the
canonical FanRelay product YAML
[`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml)
is committed alongside a non-WebFlash row in
[`config/product-catalog.json`](../config/product-catalog.json)
(`status: hardware-pending`, `webflash_build_matrix: false`, no
`artifact_name`, no `webflash_wrapper`). **No FanRelay WebFlash
wrapper, no FanRelay build-matrix entry, no FanRelay release
artifact, and no FanRelay WebFlash import exists** — those
remain blocked behind `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` /
`WF-IMPORT-RELAY-001`.

**Allowed WebFlash action now.** `not-webflash-ready`. No wrapper,
no `webflash_build_matrix: true` catalog flip, no build-matrix
entry, no release artifact, no WebFlash import. WEBFLASH-GAP-001
adds **none** of these for the Relay family. **WebFlash Relay
exposure remains blocked even though `PRODUCT-RELAY-001` / PR #564
has now landed the product YAML** — per the
[`product-readiness-matrix.md` §FanRelay / S360-310](product-readiness-matrix.md#fanrelay--s360-310)
PRODUCT-RELAY-001 audit-log entry, the product YAML carries
explicit advanced / manual-warning wording + installation / safety
caveat + competent-person caveat but **explicitly does not** add a
WebFlash wrapper / catalog `webflash_build_matrix: true` flip /
build-matrix row / release artifact. WebFlash exposure (if and
when ever appropriate) is owned by a separate `WEBFLASH-RELAY-001`
slice gated on the seven WebFlash gates enumerated below. The
recommended next PR in the Relay chain is one of
`WEBFLASH-RELAY-001` implementation plan / scaffold only (if
allowed by the project lead), `RELEASE-RELAY-001` (blocked until
artifact path exists), or `FW-COMPILE-RELAY-001` (if compile-only
validation should happen first); none of those is opened by this
readiness refresh.

**Remaining WebFlash gates (the seven gates a future
`WEBFLASH-RELAY-001` must clear).** Per the WEBFLASH-GAP-001
[Core rule](#core-rule) and the
`WEBFLASH-RELAY-001-READINESS-REFRESH` review:

1. **Explicit `WEBFLASH-RELAY-001` implementation approval.** A
   product-lead-approved per-family slice PR is required before any
   FanRelay WebFlash wrapper / catalog flip / build-matrix row is
   opened; `PRODUCT-RELAY-001` landing the product YAML does
   **not** imply WebFlash-implementation approval.
2. **Advanced / manual-warning UI copy.** The wrapper / catalog
   surfacing must carry the advanced / manual-warning UI copy on
   the WebFlash side (analogous to but distinct from the FanTRIAC
   `advanced-manual-warning` runtime UX already shipped under
   WebFlash-side `WF-TRIAC-001`) — not standard preview-list copy.
3. **Competent-person / installation warning flow.** A
   competent-person warning flow comparable in load-bearing weight
   to the FanTRIAC mains-load warning must be reachable from the
   FanRelay flash path before install; the warning belongs in the
   WebFlash runtime, not in the product YAML alone.
4. **Product not default / not recommended.** The FanRelay catalog
   row must remain off the default WebFlash landing list, off
   `release_one_required_configs`, off the kit / recommended /
   "most popular" surfaces, and off any Stage 1 installable bundle
   preset — the existing WebFlash `S360-KIT-BATH-RELAY` preset
   stays `planned` / non-installable until and unless this gate is
   explicitly relaxed.
5. **Release artifact must exist before WebFlash import.** No
   WebFlash-side import (`WF-IMPORT-RELAY-001`) may proceed before
   `RELEASE-RELAY-001` builds + signs + attaches a Relay artifact
   under the canonical
   `Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin` naming with
   SHA256 / MD5 / build-info `manifest.json` and a release-proof
   row in [`webflash-release-proof.md`](webflash-release-proof.md).
6. **No stable / preview promotion until explicit approval.** Even
   if a wrapper / catalog / build-matrix entry eventually lands,
   the channel must remain non-`stable` (and most likely on a
   dedicated advanced / manual-warning channel, **not** `preview`)
   until a separately scoped explicit PR with installation-safety
   + competent-person sign-off clears the 17-row
   [`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
   gauntlet.
7. **Production-wide / installation / safety caveats remain
   separate.** The production-wide / multi-unit `GPIO3` strap-pin
   boot characterisation, board-level mains-safety / installation
   approval / creepage / clearance / thermal / EMI evidence, and
   independent competent-person sign-off are **not** discharged by
   any WebFlash slice; they remain owed to subsequent
   evidence-bearing PRs in parallel with any WebFlash-side work.

**Possible exposure classes the eventual `WEBFLASH-RELAY-001` could
take** (decided by that slice, **not** by this readiness refresh):

- **Blocked entirely.** The default fallback if any of the seven
  gates above stays open. Mirrors the current FanTRIAC blocked
  reference catalog entry (`status: blocked`,
  `webflash_build_matrix: false`).
- **Advanced / manual-warning import only.** A wrapper + catalog
  entry + build-matrix row + signed release artifact behind a
  manual-warning UX gate on a non-`stable` channel, never on the
  standard landing list, never in `release_one_required_configs`,
  never kit / recommended / default. This is the long-term
  posture-of-record for FanRelay if all seven gates eventually
  clear.
- **Hidden / manual mode only.** A wrapper + catalog entry that is
  reachable only via a hidden manual-mode toggle in the WebFlash
  wizard (no landing-list exposure, no kit / preset exposure, no
  auto-selection); less restrictive than `blocked entirely` but
  more restrictive than `advanced / manual-warning import only`.
- **Compile-only / no-runtime exposure.** A
  [`config/compile-only-targets.json`](../config/compile-only-targets.json)
  entry that exercises the FanRelay package + product YAML through
  the upstream compile-only matrix without producing a signed
  release artifact, without adding a wrapper, without adding a
  catalog `webflash_build_matrix: true` row, and without any
  WebFlash runtime exposure. Owned by a future
  `FW-COMPILE-RELAY-001` slice, **not** by `WEBFLASH-RELAY-001`.

`WEBFLASH-RELAY-001-READINESS-REFRESH` (this PR) does **not**
choose among these classes — that decision belongs to the
implementation-slice PR.

**Future exposure class (intent).** **`advanced/manual-warning-only`,
not `preview-candidate`.** The readiness refresh in
[`product-readiness-matrix.md`](product-readiness-matrix.md#fanrelay--s360-310)
explicitly rejects the standard `preview-candidate` exposure-ladder
rung for FanRelay: a mains-switching driver without installation /
safety wording or a competent-person caveat is not appropriate for
standard preview surfacing. The eventual reach to a live
`advanced/manual-warning-only` WebFlash surface requires, in order:
`HW-ASSETS-310` *(landed; module-side schematic PDF + curated
artifact index committed)* → `HW-PINMAP-310-FOLLOWUP` *(landed;
schematic-backed reconciliation recorded in
[`s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md))* →
`CORE-ABSTRACT-BUS-001C` *(landed PR #557 — freed `GPIO3`)* →
`CORE-ABSTRACT-BUS-001A` *(landed PR #558 — `relay_pin → GPIO3`)*
→ `PACKAGE-RELAY-001-READINESS-REFRESH` *(landed PR #559)*
→ `S360-310-BENCH-001` *(landed PR #560 — checklist)*
→ `S360-310-BENCH-EVIDENCE-001` *(landed PR #561 — operator /
BOM / public-reference evidence)*
→ `PACKAGE-RELAY-001` *(landed PR #562 — test + readiness
reconciliation at the package layer only)*
→ **`PRODUCT-RELAY-001-READINESS-REFRESH`** *(this PR; docs-only)*
→ `PRODUCT-RELAY-001` (product YAML only; advanced /
manual-warning wording + installation / safety caveat +
competent-person caveat; no WebFlash wrapper / catalog flip /
build-matrix entry / release artifact; optional compile-only
target under [`config/compile-only-targets.json`](../config/compile-only-targets.json))
→ production-wide / multi-unit / oscilloscope-traced general
ESP32-S3 `GPIO3` strap-pin boot-behaviour characterisation +
installation / safety / competent-person sign-off + WebFlash-side
manual-warning UX parity decision
→ `WEBFLASH-RELAY-001` (advanced / manual-warning WebFlash wrapper
under [`products/webflash/`](../products/webflash/) + catalog
entry in [`config/product-catalog.json`](../config/product-catalog.json)
+ build-matrix row in [`config/webflash-builds.json`](../config/webflash-builds.json)
on a non-`stable` channel, behind a manual-warning UX gate)
→ `RELEASE-RELAY-001` (signed `.bin` on the advanced /
manual-warning channel; release notes; checksums; release-proof
row)
→ `WF-IMPORT-RELAY-001` (WebFlash-side import; cross-repo).

**REQUIRED_CONFIGS posture.** **`not-required-configs` — never by
default**, irrespective of any future product YAML, catalog
status, wrapper, build-matrix entry, release artifact, or
WebFlash import. Any future addition to
`release_one_required_configs` would be a separately scoped PR
with installation-safety + competent-person sign-off and is
**not** authorised by this matrix.

**Kit / recommended posture.** **`not-recommended` +
`not-kit-default` — never by default**. Mains-switching products
without installation / safety wording and a competent-person
caveat are categorically excluded from kit / default /
recommended surfaces until a separate UX + compliance /
installation-method sign-off lands. The
[`docs/kit-intent-matrix.md` §S360-KIT-BATH-RELAY](kit-intent-matrix.md#s360-kit-bath-relay--sense360-bathroom-kit--relay-fan-control)
row stays `future-expansion` / `hardware-pending` and
`webflash_exposure_allowed_now: false` /
`stable_ready_now: false`; the default sellable kit remains the
POE non-fan bundle `S360-KIT-BATH-POE` mapped to Release-One
`Ceiling-POE-VentIQ-RoomIQ`.

**User-facing naming policy.** When and if WebFlash exposure ever
lands, the user-facing name for the FanRelay surface is
**outcome-first** — e.g. `"Relay fan control"` or
`"Switched fan control"` — **not** loose board / module naming
like `"Sense360 Relay"` (which is the canonical product /
inventory name) or `"S360-310"` (which is the canonical SKU).
This matches the WebFlash repo's outcome-first Step 4 module-label
convention recorded in `WF-UX-007` (Step 4 jargon and module-label
cleanup; outcome-first primary titles with technical Friendly Name +
SKU layered into a secondary meta line).

**Cross-references.**
[`hardware/s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md),
[`hardware/board-readiness-matrix.md` §S360-310](hardware/board-readiness-matrix.md#s360-310-sense360-relay),
[`hardware/package-readiness-matrix.md` §fan_relay.yaml](hardware/package-readiness-matrix.md#fan_relayyaml--s360-310),
[`product-readiness-matrix.md` §FanRelay / S360-310](product-readiness-matrix.md#fanrelay--s360-310),
[`release-artifact-readiness-matrix.md` §Relay / S360-310 release posture](release-artifact-readiness-matrix.md#relay--s360-310-release-posture),
[`kit-intent-matrix.md` §S360-KIT-BATH-RELAY](kit-intent-matrix.md#s360-kit-bath-relay--sense360-bathroom-kit--relay-fan-control).

**2026-05-22 — `PRODUCT-RELAY-001-READINESS-REFRESH` (this PR;
docs-only).** Re-evaluated the FanRelay WebFlash-exposure
disposition after `PACKAGE-RELAY-001` / PR #562 implemented the
package at the package layer. Re-verified against the live files:
no FanRelay WebFlash wrapper under
[`products/webflash/`](../products/webflash/) (only Release-One
[`ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml),
LED preview
[`ceiling-poe-ventiq-roomiq-led.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq-led.yaml),
and the blocked FanTRIAC reference
[`ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml));
no FanRelay catalog row in
[`config/product-catalog.json`](../config/product-catalog.json);
no FanRelay build in
[`config/webflash-builds.json`](../config/webflash-builds.json);
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
reserves `FanRelay` in `canonical_modules` (line 11) subject to
the fan-driver `max-one-of` rule; `release_one_required_configs`
stays `["Ceiling-POE-VentIQ-RoomIQ"]`. **WebFlash Relay exposure
remains blocked.** The product-layer disposition recorded in
[`product-readiness-matrix.md` §FanRelay / S360-310](product-readiness-matrix.md#fanrelay--s360-310)
is `advanced/manual-warning-only` + product-YAML-allowed (no
WebFlash) + compile-only-allowed; the eventual WebFlash exposure
class is `advanced/manual-warning-only` (not the default
`preview-candidate` standard-exposure ladder rung), and a live
WebFlash surface still requires `PRODUCT-RELAY-001` implementation
+ production-wide hardware characterisation + installation /
competent-person sign-off + WebFlash-side manual-warning UX
parity + a separate `WEBFLASH-RELAY-001` slice. **No package /
product / WebFlash / build / release / compliance / JSON-catalog /
test / script / workflow / component / include / firmware /
manifest edit**; **no `webflash_build_matrix` flip**; **no
`artifact_name` / `webflash_wrapper` / `config_string` /
`release_one_required_configs` / `lifecycle_statuses` /
`canonical_modules` / `canonical_power` / `forbidden_tokens` /
`REQUIRED_CONFIGS` / kit JSON change**; **no `schematic_status` /
`schematic_file` promotion** (`S360-310` stays
`cataloged_unverified`); **no COMPLIANCE-001 movement**; Release-One
stays `Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`; LED
preview stays `Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`;
FanTRIAC stays `blocked` / `HW-005`. **No WebFlash import-readiness
claim. No WebFlash exposure claim. No `REQUIRED_CONFIGS`
membership claim. No kit / recommended membership claim. No
stable-channel claim.** The recommended next active-queue item is
`PRODUCT-RELAY-001` implementation as a product-YAML-only /
no-WebFlash-exposure slice (see
[`product-readiness-matrix.md` §FanRelay / S360-310](product-readiness-matrix.md#fanrelay--s360-310)),
**not** `WEBFLASH-RELAY-001`.

**2026-05-22 — `PRODUCT-RELAY-001` (PR #564; implementation
slice).** `PRODUCT-RELAY-001` landed as a product-YAML-only /
no-WebFlash-exposure slice. The canonical FanRelay product YAML
[`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml)
exists; a non-WebFlash row was added to
[`config/product-catalog.json`](../config/product-catalog.json)
for it (`config_string: Ceiling-POE-VentIQ-FanRelay-RoomIQ`,
`status: hardware-pending`, `webflash_build_matrix: false`, no
`artifact_name`, no `webflash_wrapper`). **WebFlash Relay exposure
remains blocked**: no FanRelay WebFlash wrapper under
[`products/webflash/`](../products/webflash/), no FanRelay row in
[`config/webflash-builds.json`](../config/webflash-builds.json),
no FanRelay token in `release_one_required_configs`, no FanRelay
release artifact / tag / checksum / build-info manifest, no
WebFlash-side import. The row class above is refreshed from
`product-layer-disposition: advanced/manual-warning-only +
product-YAML-allowed (no WebFlash) + compile-only-allowed` to
`product-yaml-landed + product-layer-blockers-narrowed` (the
product YAML carries the advanced / manual-warning + installation
/ safety + competent-person caveat wording explicitly; the
production-wide / multi-unit hardware characterisation,
board-level mains-safety / installation-approval evidence, and
independent competent-person sign-off remain owed to subsequent
slices). The structural pins are recorded in
[`tests/test_relay_product_readiness.py`](../tests/test_relay_product_readiness.py)
(42 stdlib-unittest cases, all green). **No
[`products/webflash/`](../products/webflash/) edit; no
[`config/webflash-builds.json`](../config/webflash-builds.json)
edit; no
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
edit; no `webflash_build_matrix` flip; no `artifact_name`; no
`webflash_wrapper`; no `release_one_required_configs` change; no
COMPLIANCE-001 movement; no `schematic_status` /
`schematic_file` promotion (`S360-310` stays
`cataloged_unverified`); no kit JSON change** — the WebFlash
side of the FanRelay chain is byte-identical to the
`PRODUCT-RELAY-001-READINESS-REFRESH` snapshot above on
[`config/`](../config/) `[webflash-builds.json,
webflash-compatibility.json, hardware-catalog.json,
kit-intent-matrix.json]`. Release-One stays
`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`; LED preview
stays `Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`; FanTRIAC stays
`blocked` / `HW-005`. The recommended next active-queue item is
`WEBFLASH-RELAY-001-READINESS-REFRESH` (docs-only readiness
re-evaluation after PRODUCT-RELAY-001 lands), **not** immediate
`WEBFLASH-RELAY-001` exposure work.

**2026-05-22 — `WEBFLASH-RELAY-001-READINESS-REFRESH` (this PR;
docs-only).** Re-evaluated the FanRelay WebFlash exposure
readiness after `PRODUCT-RELAY-001` / PR #564 landed the FanRelay
product YAML
[`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml)
without WebFlash exposure (catalog row
`Ceiling-POE-VentIQ-FanRelay-RoomIQ` with `status:
hardware-pending`, `webflash_build_matrix: false`, no
`artifact_name`, no `webflash_wrapper`). Re-verified against the
live files:

- **No FanRelay WebFlash wrapper** under
  [`products/webflash/`](../products/webflash/) — only the
  Release-One
  [`ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml),
  the LED preview
  [`ceiling-poe-ventiq-roomiq-led.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq-led.yaml),
  and the blocked FanTRIAC reference
  [`ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml)
  are present.
- **No FanRelay row in
  [`config/webflash-builds.json`](../config/webflash-builds.json)**
  — only the two existing Release-One stable +
  `Ceiling-POE-VentIQ-RoomIQ-LED` preview builds remain.
- [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  reserves `FanRelay` in `canonical_modules` (line 11) subject to
  the fan-driver `max-one-of` rule, with **no
  `webflash_build_matrix: true` consumer** — reservation is
  grammar-only and does **not** imply WebFlash exposure.
- `release_one_required_configs` stays
  `["Ceiling-POE-VentIQ-RoomIQ"]`; no FanRelay member is added.
- The
  [`config/product-catalog.json`](../config/product-catalog.json)
  FanRelay row landed by `PRODUCT-RELAY-001` / PR #564
  (`config_string: Ceiling-POE-VentIQ-FanRelay-RoomIQ`, `status:
  hardware-pending`, `webflash_build_matrix: false`, no
  `artifact_name`, no `webflash_wrapper`) is byte-identical to the
  PRODUCT-RELAY-001 snapshot above and is **not** flipped.
- The kit-intent surface
  [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json)
  `S360-KIT-BATH-RELAY` row stays `future-expansion` /
  `hardware-pending` / `webflash_exposure_allowed_now: false` /
  `stable_ready_now: false`; the default sellable bathroom kit
  remains `S360-KIT-BATH-POE` mapped to Release-One.

**WebFlash Relay exposure remains blocked.** The seven remaining
WebFlash gates (explicit `WEBFLASH-RELAY-001` implementation
approval; advanced / manual-warning UI copy; competent-person /
installation warning flow; product not default / not recommended;
release artifact must exist before WebFlash import; no stable /
preview promotion until explicit approval; production-wide /
installation / safety caveats remain separate) are enumerated
above under [Allowed WebFlash action now](#allowed-webflash-action-now-1).
A future `WEBFLASH-RELAY-001` slice could land as any one of four
exposure shapes — **blocked entirely**, **advanced / manual-warning
import only**, **hidden / manual mode only**, or **compile-only /
no-runtime exposure** — and this readiness refresh records the
shapes without choosing among them.

**WebFlash repo posture (read-only review).** Re-read against the
`sense360store/WebFlash` repo: `firmware/sources.json` has **no
FanRelay source declaration**; `manifest.json` carries **no
FanRelay build**; the three live builds remain Release-One
(`Ceiling-POE-VentIQ-RoomIQ` v1.0.0 stable), LED preview
(`Ceiling-POE-VentIQ-RoomIQ-LED` v1.0.0 preview), and Rescue;
`REQUIRED_CONFIGS` stays `["Ceiling-POE-VentIQ-RoomIQ",
"Rescue"]`; `scripts/data/kits.json` stays Release-One-only;
`scripts/utils/module-availability.js` keeps Sense360 Relay
(S360-310) classified as `design-pending`; Stage 1
[`scripts/data/kit-presets.js`](https://github.com/sense360store/WebFlash/blob/main/scripts/data/kit-presets.js)
keeps the `S360-KIT-BATH-RELAY` preset as `status: planned`
(non-installable, `notAvailableReason: "Awaiting upstream
RELEASE-RELAY-001 firmware import (WF-IMPORT-RELAY-001)."`); and
the WebFlash UPCOMING_PR queue item 4 keeps `WF-IMPORT-RELAY-001`
**blocked** behind upstream `RELEASE-RELAY-001`. **The WebFlash
repo's outcome-first user-facing naming** — "Fan relay control"
in Step 4 module cards under WF-UX-007 and "Sense360 Bathroom Kit
— Relay Fan Control" in Stage 1 bundle presets under
WF-KIT-PRESETS-001 — **is already aligned** with this matrix's
user-facing-naming policy; no naming refresh is owed on either
side.

**No package / product / WebFlash / build / release / compliance /
JSON-catalog / test / script / workflow / component / include /
firmware / manifest edit; no `webflash_build_matrix` flip; no
`artifact_name` / `webflash_wrapper` / `config_string` /
`release_one_required_configs` / `lifecycle_statuses` /
`canonical_modules` / `canonical_power` / `forbidden_tokens` /
`REQUIRED_CONFIGS` / kit JSON change; no `schematic_status` /
`schematic_file` promotion** (`S360-310` stays
`cataloged_unverified`); **no COMPLIANCE-001 movement**;
Release-One stays `Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` /
`stable`; LED preview stays `Ceiling-POE-VentIQ-RoomIQ-LED` /
`preview`; FanTRIAC stays `blocked` / `HW-005`. **No WebFlash
import-readiness claim. No WebFlash exposure claim. No
`RELEASE-RELAY-001` unblock claim. No `REQUIRED_CONFIGS`
membership claim. No kit / recommended / default membership claim.
No compliance / board-level mains-safety certification claim. No
hardware stable / release-readiness claim. No WebFlash repo edit.**
The recommended next active-queue item is one of
`WEBFLASH-RELAY-001` implementation plan / scaffold only (if
allowed by the project lead), `RELEASE-RELAY-001` (blocked until
artifact path exists), or `FW-COMPILE-RELAY-001` (if compile-only
validation should happen first); **not** immediate
`WEBFLASH-RELAY-001` wrapper / catalog / build-matrix work.

**2026-05-22 — `FW-COMPILE-RELAY-001` (this PR; compile-only target
add) — note on WebFlash surface.** Added a single FanRelay
compile-only validation target to
[`config/compile-only-targets.json`](../config/compile-only-targets.json)
pointing at the PRODUCT-RELAY-001 / PR #564 canonical FanRelay
product YAML
[`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml).
The target carries `shipment_status: compile-only`,
`webflash_exposure_allowed_now: false`,
`hardware_required_for_validation: true`,
`advanced_manual_warning_only: true`, `hardware_pending: true`, and
`blocked: false`. **WebFlash Relay exposure remains blocked.** The
seven WebFlash gates enumerated above under
[Allowed WebFlash action now](#allowed-webflash-action-now-1) are
**not** advanced by this compile-only target; the four possible
exposure shapes a future `WEBFLASH-RELAY-001` slice could take
(blocked entirely; advanced / manual-warning import only; hidden /
manual mode only; or compile-only / no-runtime exposure) are
unchanged. Re-verified against the live files:

- **No FanRelay WebFlash wrapper** under
  [`products/webflash/`](../products/webflash/) — only the
  Release-One, LED preview, and blocked FanTRIAC reference wrappers
  remain.
- **No FanRelay row in
  [`config/webflash-builds.json`](../config/webflash-builds.json)**
  — only Release-One stable + LED preview.
- The FanRelay token does not appear anywhere in
  [`config/webflash-builds.json`](../config/webflash-builds.json);
  `release_one_required_configs` in
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  stays `["Ceiling-POE-VentIQ-RoomIQ"]`.
- The [`config/product-catalog.json`](../config/product-catalog.json)
  FanRelay row landed by PRODUCT-RELAY-001 / PR #564 (`status:
  hardware-pending`, `webflash_build_matrix: false`, no
  `artifact_name`, no `webflash_wrapper`) is byte-identical.
- The [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json)
  `S360-KIT-BATH-RELAY` row stays `future-expansion` /
  `hardware-pending` / `webflash_exposure_allowed_now: false` /
  `stable_ready_now: false`; the default sellable bathroom kit
  remains `S360-KIT-BATH-POE` mapped to Release-One.

**No `packages/**` edit; no `products/**` or `products/webflash/**`
edit** (the FanRelay product YAML at
[`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml)
is consumed verbatim as landed by PR #564; no edits made); **no
[`config/webflash-builds.json`](../config/webflash-builds.json)
edit**; **no
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
edit**; **no
[`config/hardware-catalog.json`](../config/hardware-catalog.json)
edit**; **no
[`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json)
edit**; **no
[`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json)
edit**; **no
[`config/product-catalog.json`](../config/product-catalog.json)
edit**; **no `scripts/**`, `.github/workflows/**`,
`components/**`, `include/**`, `firmware/**`, `manifest.json`,
`firmware/sources.json` edit**; **no WebFlash repo
(`sense360store/WebFlash`) edit**; **no `webflash_build_matrix`
flip; no `artifact_name`; no `webflash_wrapper`; no `config_string`
change; no `release_one_required_configs` change; no
`lifecycle_statuses` change; no `canonical_modules` /
`canonical_power` / `forbidden_tokens` change; no
`REQUIRED_CONFIGS` / kit JSON change; no `schematic_status` /
`schematic_file` promotion** (`S360-310` stays
`cataloged_unverified`); **no COMPLIANCE-001 movement**;
Release-One stays `Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` /
`stable`; LED preview stays `Ceiling-POE-VentIQ-RoomIQ-LED` /
`preview`; FanTRIAC stays `blocked` / `HW-005`. **No WebFlash
import-readiness claim. No WebFlash exposure claim. No
`RELEASE-RELAY-001` unblock claim. No `WEBFLASH-RELAY-001`
unblock claim. No `WF-IMPORT-RELAY-001` unblock claim. No
`REQUIRED_CONFIGS` membership claim. No kit / recommended /
default membership claim. No compliance / board-level mains-safety
certification claim. No installation-approval / qualified-electrician
sign-off claim. No production-wide / multi-unit hardware
characterisation claim. No hardware stable / release-readiness
claim.** Edits are scoped to
[`config/compile-only-targets.json`](../config/compile-only-targets.json)
(one new row, totals 7 → 8), the matching ledger
[`config/compile-only-candidates.json`](../config/compile-only-candidates.json)
(`currently_compile_only_config_strings` extended by one),
[`tests/test_compile_targets.py`](../tests/test_compile_targets.py)
(new `FanRelayCompileOnlyCoverageTests` class; the POE non-fan lane's
fan / PWR-token guardrails scoped to `products/compile-only/`),
[`tests/test_relay_product_readiness.py`](../tests/test_relay_product_readiness.py)
(new `RelayProductCompileOnlyTargetTests` class), this matrix,
[`docs/compile-only-firmware-validation.md`](compile-only-firmware-validation.md)
(new audit-log entry),
[`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
(new audit-log note), and `UPCOMING_PR.md`. The recommended next
Relay-chain PR is one of `WEBFLASH-RELAY-001` implementation plan /
scaffold only (if allowed by the project lead), `RELEASE-RELAY-001`
(still blocked until artifact path exists), or, if any future ESPHome
upgrade breaks compile, a targeted compile fix for the FanRelay
target only; **not** immediate `WEBFLASH-RELAY-001` wrapper / catalog
/ build-matrix work.

**2026-05-22 — `FW-COMPILE-RELAY-RESULT-001` (this PR; docs-only
record of successful CI result).** The
`Compile-only Firmware Validation` workflow ran against the
expanded eight-target compile-only lane (the FanRelay
compile-only target added by `FW-COMPILE-RELAY-001` / PR #566 plus
the seven prior compile-only targets) and **passed** —
GitHub Actions Run ID `26298089904`, status `completed`,
conclusion `success`, PR/head validation for PR #566; the
companion Quick Validation run ID `26298090061` also succeeded.
**FanRelay compile-only validation now has a green CI result.**
**WebFlash Relay exposure remains blocked.** The seven WebFlash
gates enumerated above under
[Allowed WebFlash action now](#allowed-webflash-action-now-1) are
**not** advanced by a green compile-only CI result; the four
possible exposure shapes a future `WEBFLASH-RELAY-001` slice
could take (blocked entirely; advanced / manual-warning import
only; hidden / manual mode only; or compile-only / no-runtime
exposure) are unchanged. Re-verified against the live files:

- **No FanRelay WebFlash wrapper** under
  [`products/webflash/`](../products/webflash/) — only the
  Release-One, LED preview, and blocked FanTRIAC reference
  wrappers remain.
- **No FanRelay row in
  [`config/webflash-builds.json`](../config/webflash-builds.json)**
  — only Release-One stable + LED preview.
- `release_one_required_configs` in
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  stays `["Ceiling-POE-VentIQ-RoomIQ"]`.
- The [`config/product-catalog.json`](../config/product-catalog.json)
  FanRelay row landed by PRODUCT-RELAY-001 / PR #564 (`status:
  hardware-pending`, `webflash_build_matrix: false`, no
  `artifact_name`, no `webflash_wrapper`) is byte-identical.
- The [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json)
  `S360-KIT-BATH-RELAY` row stays `future-expansion` /
  `hardware-pending` / `webflash_exposure_allowed_now: false` /
  `stable_ready_now: false`; the default sellable bathroom kit
  remains `S360-KIT-BATH-POE` mapped to Release-One.

**No `packages/**` edit; no `products/**` or `products/webflash/**`
edit; no
[`config/compile-only-targets.json`](../config/compile-only-targets.json)
edit (totals stay at 8 targets after PR #566); no
[`config/webflash-builds.json`](../config/webflash-builds.json)
edit; no
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
edit; no
[`config/hardware-catalog.json`](../config/hardware-catalog.json)
edit; no
[`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json)
edit; no
[`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json)
edit; no
[`config/product-catalog.json`](../config/product-catalog.json)
edit; no `scripts/**`, `.github/workflows/**`, `components/**`,
`include/**`, `firmware/**`, `manifest.json`,
`firmware/sources.json`, `tests/**` edit; no WebFlash repo
(`sense360store/WebFlash`) edit; no `webflash_build_matrix` flip;
no `artifact_name`; no `webflash_wrapper`; no `config_string`
change; no `release_one_required_configs` change; no
`lifecycle_statuses` change; no `canonical_modules` /
`canonical_power` / `forbidden_tokens` change; no
`REQUIRED_CONFIGS` / kit JSON change; no `schematic_status` /
`schematic_file` promotion** (`S360-310` stays
`cataloged_unverified`); **no COMPLIANCE-001 movement**;
Release-One stays `Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` /
`stable`; LED preview stays `Ceiling-POE-VentIQ-RoomIQ-LED` /
`preview`; FanTRIAC stays `blocked` / `HW-005`. **No WebFlash
import-readiness claim. No WebFlash exposure claim. No
`RELEASE-RELAY-001` unblock claim. No `WEBFLASH-RELAY-001`
unblock claim. No `WF-IMPORT-RELAY-001` unblock claim. No
`REQUIRED_CONFIGS` membership claim. No kit / recommended /
default membership claim. No compliance / board-level
mains-safety certification claim. No installation-approval /
qualified-electrician sign-off claim. No production-wide /
multi-unit hardware characterisation claim. No hardware stable /
release-readiness claim.** Compile success on GitHub Actions is
**necessary-but-insufficient** input to the broader
preview-to-stable promotion process; it does **not** discharge
any of the seven WebFlash gates owned by `WEBFLASH-RELAY-001`,
and does **not** discharge any release-readiness gate owned by
`RELEASE-RELAY-001`. The recommended next Relay-chain PR is one
of `WEBFLASH-RELAY-001-SCAFFOLD-001` (if WebFlash Relay planning
continues) or `CORE-ABSTRACT-BUS-001B` (if PWM / DAC blocker
removal is prioritised instead); **not** immediate
`WEBFLASH-RELAY-001` wrapper / catalog / build-matrix work.

**2026-05-24 — `FW-COMPILE-RELAY-FULL-RESULT-001` (this PR; docs-only
record of successful full-compile result).** The manual
`workflow_dispatch` `compile_mode=full` run of the
`Compile-only Firmware Validation` lane owed by
`FW-COMPILE-RELAY-FULL-FIX-001` / PR #578 ran against post-#578 `main`
and **passed** — GitHub Actions Run ID `26364679370`, event
`workflow_dispatch`, mode `compile_mode=full`, status `completed`,
conclusion `success`, **9** compile-only targets; the
`Compile-only Targets — Full ESPHome Compile` job (`77606324332`)
completed `success`. **The previously failed full-compile run
`26334334727` is superseded.** **The FanRelay target now full-compiles
green, but WebFlash Relay exposure remains blocked.** The seven WebFlash
gates enumerated above under
[Allowed WebFlash action now](#allowed-webflash-action-now-1) are **not**
advanced by a green full-compile CI result; the four possible exposure
shapes a future `WEBFLASH-RELAY-001` slice could take are unchanged.
Re-verified against the live files: no FanRelay WebFlash wrapper under
[`products/webflash/`](../products/webflash/); no FanRelay row in
[`config/webflash-builds.json`](../config/webflash-builds.json);
`release_one_required_configs` in
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
stays `["Ceiling-POE-VentIQ-RoomIQ"]`; the
[`config/product-catalog.json`](../config/product-catalog.json) FanRelay
row stays `status: hardware-pending` / `webflash_build_matrix: false` /
no `artifact_name` / no `webflash_wrapper`. **No `packages/**`,
`products/**`, `products/webflash/**`, `config/**`, `scripts/**`,
`.github/workflows/**`, `components/**`, `include/**`, `tests/**`,
`firmware/**`, `manifest.json`, `firmware/sources.json` edit; no
`webflash_build_matrix` flip; no `artifact_name`; no `webflash_wrapper`;
no `release_one_required_configs` change; no `schematic_status` /
`schematic_file` promotion** (`S360-310` stays `cataloged_unverified`);
**no COMPLIANCE-001 movement.** Release-One stays
`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`; LED preview stays
`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`; FanTRIAC stays `blocked` /
`HW-005`. **No WebFlash import-readiness claim. No WebFlash exposure
claim. No `RELEASE-RELAY-001` / `WEBFLASH-RELAY-001` /
`WF-IMPORT-RELAY-001` unblock claim. No compliance / board-level
mains-safety / installation-approval / qualified-electrician sign-off /
production-wide / multi-unit hardware characterisation / hardware-stable
claim.** A green full-compile CI result is **necessary-but-insufficient**
input to the broader preview-to-stable promotion process; it does **not**
discharge any of the seven WebFlash gates owned by `WEBFLASH-RELAY-001`.

**2026-05-26 — `WEBFLASH-RELAY-001-READINESS` (this PR; docs-only
re-evaluation, no exposure flip).** Re-evaluated FanRelay / S360-310
WebFlash-exposure readiness using the latest package / product /
full-compile and `WEBFLASH-DRIFT-001` / PR #595 drift-audit evidence,
**without exposing FanRelay to WebFlash**. Re-verified against the live
esphome-public files this session:

- **Product YAML exists** —
  [`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml)
  (PRODUCT-RELAY-001 / PR #564), confirmed on disk.
- **Package layer implemented** —
  [`packages/expansions/fan_relay.yaml`](../packages/expansions/fan_relay.yaml)
  (PACKAGE-RELAY-001 / PR #562): `fan_relay_switch` `template` switch
  proxies the Core `main_relay`, single `${relay_pin}` → `GPIO3` owner;
  no second `switch.gpio`.
- **Full-compile evidence recorded** — the FanRelay compile-only target
  full-compiled green in run `26364679370` (`workflow_dispatch` /
  `compile_mode=full`, 9 targets, conclusion `success`; the lane runs
  `esphome compile` against every
  [`config/compile-only-targets.json`](../config/compile-only-targets.json)
  target and fails on the first failure, so `success` proves all nine
  including FanRelay; FW-COMPILE-RELAY-FULL-RESULT-001 / PR #579). This is
  **prior-recorded in-repo evidence**; the GitHub Actions run could not be
  re-read with the tooling scoped to this session.
- **No WebFlash wrapper** under
  [`products/webflash/`](../products/webflash/) — only Release-One, LED
  preview, and the blocked FanTRIAC reference.
- **No [`config/webflash-builds.json`](../config/webflash-builds.json)
  row** — only the 2 existing builds; the `FanRelay` token appears 0
  times.
- **No `artifact_name`, no `webflash_wrapper`,
  `webflash_build_matrix: false`** on the catalog row.
- **No release artifact** — no `.bin`, tag, checksum, or build-info
  manifest.
- **No import readiness** — WebFlash-owned; prior-recorded (2026-05-22,
  PR #565) has no FanRelay source / build, and `WF-IMPORT-RELAY-001` is
  blocked behind `RELEASE-RELAY-001`. A **live re-read of
  `sense360store/WebFlash` was denied this session** (the GitHub scope is
  `sense360store/esphome-public` + `sense360store/esphome` only), so the
  WebFlash side stays prior-recorded, not re-verified — `NEEDS-TOOLING`.

**Compile-flag gap (`WEBFLASH-DRIFT-001` row #21) — resolved as a docs
clarification, no config edit.** The narrative correctly records the
FanRelay full compile as green (run `26364679370`); the
[`config/compile-only-targets.json`](../config/compile-only-targets.json)
FanRelay target deliberately carries **no** `compile_validation_status`
field — `COMPILE-STATUS-FLAGS-001` (2026-05-24) explicitly left it
unchanged ("FanRelay carries no `compile_validation_status` field and is
left unchanged") while flipping only FanDAC. No doc stale-says the
FanRelay compile is unvalidated, and no test asserts the flag's presence
or absence, so **no `config/` edit is required or made** by this
docs-only PR. Adding the explicit flag (to match FanDAC / FanPWM
`validated-full-compile`) is an **optional, non-blocking**
config-completeness follow-up (`FW-COMPILE-RELAY-RESULT-001`), not a
WebFlash gate.

**Relay WebFlash readiness table (re-evaluated 2026-05-26).** Status
legend: `CLOSED` (gate satisfied); `BLOCKING` (open gate that blocks
WebFlash exposure); `NEEDS-TOOLING` (cannot be re-verified without live
WebFlash / CI access); `NEEDS-OPERATOR-INPUT` (requires operator
evidence / sign-off); `OUT-OF-SCOPE` (not advanced by any WebFlash slice
and/or never by default).

| Gate | Status | Evidence | Next action |
|---|---|---|---|
| Product YAML exists | `CLOSED` | `products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml` (PRODUCT-RELAY-001 / PR #564); verified on disk this session | none — landed |
| Package layer implemented | `CLOSED` | `packages/expansions/fan_relay.yaml` (PACKAGE-RELAY-001 / PR #562); `fan_relay_switch` proxies Core `main_relay`; single `GPIO3` owner; pinned by `tests/test_fan_relay_package.py` | none — landed |
| Full-compile evidence recorded | `CLOSED` | run `26364679370` (`compile_mode=full`, 9 targets, `success`); fails-on-first → FanRelay green (FW-COMPILE-RELAY-FULL-RESULT-001 / PR #579); prior-recorded in-repo | optional `FW-COMPILE-RELAY-RESULT-001` config-flag add (non-blocking) |
| FanRelay `compile_validation_status` config flag | `OUT-OF-SCOPE` | field intentionally absent (COMPILE-STATUS-FLAGS-001 left FanRelay unchanged); no stale "unvalidated" doc; no test pins it | optional config-only `FW-COMPILE-RELAY-RESULT-001`; this docs-only PR does not touch `config/` |
| Hardware evidence — package/product config posture | `CLOSED` | HW-ASSETS-310 schematic PDF + HW-PINMAP-310-FOLLOWUP; S360-310-BENCH-EVIDENCE-001 / PR #561 (10 rows; operator + BOM + public-reference) | none for config posture |
| Hardware evidence — production-wide / mains-safety | `NEEDS-OPERATOR-INPUT` | no oscilloscope / photo / continuity artifacts; `S360-310 schematic_status: cataloged_unverified`; production-wide / multi-unit `GPIO3` strap-pin boot characterisation owed | operator-supplied bench + multi-unit evidence |
| WebFlash wrapper | `BLOCKING` | none under `products/webflash/` (only RoomIQ / LED / blocked FanTRIAC) | `WEBFLASH-RELAY-001` (gated) |
| `config/webflash-builds.json` row | `BLOCKING` | absent — 2 builds only; 0 FanRelay tokens | `WEBFLASH-RELAY-001` |
| `artifact_name` | `BLOCKING` | catalog row has none; `webflash_build_matrix: false` | `WEBFLASH-RELAY-001` |
| Firmware release artifact | `BLOCKING` | no `.bin` / tag / checksum / build-info manifest | `RELEASE-RELAY-001` (behind wrapper / build-matrix) |
| Import-source path (WebFlash `firmware/sources.json` / `manifest.json`) | `BLOCKING` | WebFlash-owned; prior-recorded no FanRelay source / build; `WF-IMPORT-RELAY-001` blocked behind `RELEASE-RELAY-001` | `WF-IMPORT-RELAY-001` (cross-repo) |
| WebFlash live repo re-verification | `NEEDS-TOOLING` | `sense360store/WebFlash` read access denied this session; WebFlash facts are prior-recorded 2026-05-22 (PR #565) | `WEBFLASH-RELAY-LIVE-CHECK-001` once access restored |
| Compliance / mains-safety approval | `BLOCKING` | only public-reference contact rating; no board-level mains-safety / creepage / clearance / thermal / EMI / EMC certification; `COMPLIANCE-001` not signed off | `COMPLIANCE-001` (separate; not a WebFlash slice) |
| Advanced / manual-warning WebFlash UX parity | `BLOCKING` | Relay-side manual-warning runtime UX not confirmed (analogous `WF-TRIAC-001` UX exists for TRIAC only) | `WEBFLASH-RELAY-001` + WebFlash-side UX |
| Competent-person / installation sign-off | `NEEDS-OPERATOR-INPUT` | product YAML carries caveat wording only; no independent sign-off | operator-supplied competent-person sign-off |
| REQUIRED_CONFIGS / kit / recommended membership | `OUT-OF-SCOPE` | `release_one_required_configs = ["Ceiling-POE-VentIQ-RoomIQ"]`; `S360-KIT-BATH-RELAY` stays `future-expansion` / `hardware-pending` | never by default; separate explicit PR |

**Verdict — WebFlash Relay exposure stays blocked; recommended next
Relay PR is `WEBFLASH-RELAY-LIVE-CHECK-001`.** The package / product /
full-compile / config-posture-hardware gates are `CLOSED`, but the
non-WebFlash gates are **not** all clean — compliance / mains-safety
sign-off, production-wide `GPIO3` strap-pin characterisation, and a
competent-person sign-off remain owed — and the WebFlash side cannot be
re-verified live this session (`NEEDS-TOOLING`). This is therefore
**not** the "only WebFlash-wrapper / artifact / import missing" case that
would justify a `WEBFLASH-RELAY-002-WRAPPER-PLAN` slice. The recommended
next step is **`WEBFLASH-RELAY-LIVE-CHECK-001`** — a re-run of the live
WebFlash readiness / drift check (`firmware/sources.json`,
`manifest.json`, `scripts/utils/module-availability.js`,
`scripts/data/kit-presets.js`, import grammar) once read access to
`sense360store/WebFlash` is restored — which closes the `NEEDS-TOOLING`
axes before any `WEBFLASH-RELAY-001` wrapper / catalog / build-matrix
work is even considered. The compile-flag gap (#21) is a docs
clarification only and is recorded resolved above; the optional
`FW-COMPILE-RELAY-RESULT-001` config-flag PR is non-blocking.

**Guardrails honoured.** **No `packages/**`, `products/**`,
`products/webflash/**`, `config/**` (including
`config/webflash-builds.json`, `config/product-catalog.json`,
`config/compile-only-targets.json`), `scripts/**`,
`.github/workflows/**`, `components/**`, `include/**`, `tests/**`,
`firmware/**`, `manifest.json`, `firmware/sources.json`,
release-artifact / checksum / build-info, or `sense360store/WebFlash`
edit.** No WebFlash wrapper added; no `webflash_build_matrix` flip; no
`artifact_name`; no `webflash_wrapper`; no `config_string` /
`release_one_required_configs` / `lifecycle_statuses` /
`canonical_modules` change; no `schematic_status` / `schematic_file`
promotion (`S360-310` stays `cataloged_unverified`); no `COMPLIANCE-001`
movement. Release-One stays `Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` /
`stable`; LED preview stays `Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`;
FanTRIAC stays `blocked` / `HW-005`. **No WebFlash import-readiness
claim, no WebFlash exposure claim, no release-readiness claim, no
compliance / mains-safety approval claim, no hardware-stable readiness
claim, and no fabricated WebFlash evidence.**

**2026-05-27 — `RELAY-BLOCKER-RECLASSIFY-001` (this PR; docs-only) — note on
WebFlash surface.** The remaining FanRelay gaps are **reclassified by release
scope**, and the reclassification **keeps the WebFlash surface fully
blocked.** It explicitly names **WebFlash live access / `S360-310`
module-availability** (`RLY-8`, `WF-1`/`WF-2`) and the **WebFlash wrapper /
build / artifact / import** chain as a **WebFlash-exposure blocker only**
(they do **not** gate the FanRelay package / product / `config` layer, which
is already complete with the product YAML landed and full-compile-green in run
`26364679370`), and it keeps the **manual / advanced-warning UX** (`RLY-5`,
WebFlash UX blocker only), the **production-wide `GPIO3` strap-pin
characterisation** (`RLY-3`, production / hardware-stable / WebFlash / release
blocker only), the **competent-person sign-off** (`RLY-4`, safety /
compliance / release blocker only), and the **mains / compliance approval**
(`RLY-6`, release / compliance blocker only) as WebFlash gates. So the
FanRelay WebFlash surface stays **`not-webflash-ready`**: the wrapper,
`config/webflash-builds.json` row, `artifact_name`, release artifact, and
import-source gates stay `BLOCKING`; the live `sense360store/WebFlash`
re-verification and the still-owed `S360-310` module-availability
classification stay `NEEDS-TOOLING`; the competent-person sign-off,
production-wide `GPIO3` characterisation, and mains-safety approval stay
`BLOCKING` / `NEEDS-OPERATOR-INPUT`. Kit / default / recommended membership
stays out of scope unless separately approved. The `RLY-6` mains-switching
safety posture stays correct. The recommended next step is
**`WEBFLASH-RELAY-LIVE-CHECK-001`** (behind WebFlash access), and **no
`WEBFLASH-RELAY-001` wrapper is recommended** until the production-wide
`GPIO3` + competent-person + mains-compliance evidence *and* the WebFlash
live classification are done; **`S360-310-SAFETY-BENCH-RESULT-001`**
(requested via `S360-310-SAFETY-EVIDENCE-REQUEST-001`) is the later
safety-evidence PR. Canonical table in
[`hardware/s360-310-r4-relay.md` §RELAY-BLOCKER-RECLASSIFY-001](hardware/s360-310-r4-relay.md#relay-blocker-reclassify-001--fanrelay-remaining-blockers-reclassified-by-release-scope-2026-05-27).
No `packages/**`, `products/**`, `products/webflash/**`, `config/**`,
`scripts/**`, `.github/workflows/**`, `components/**`, `include/**`,
`tests/**`, `firmware/**`, `manifest.json`, `firmware/sources.json`,
release-artifact / checksum / build-info, or `sense360store/WebFlash`
edit; no `webflash_build_matrix` flip; no `artifact_name`; no
`schematic_status` promotion (`S360-310` stays `cataloged_unverified`); no
WebFlash exposure / import / release / compliance / hardware-stable claim;
no fabricated evidence.

**2026-05-27 — `WEBFLASH-LIVE-CHECK-001` (this PR; docs-only live re-check,
no exposure flip).** Re-attempted the live read of `sense360store/WebFlash`
this session via three read-only GitHub methods (repo root,
`scripts/utils/module-availability.js`, and a branch listing) — **all three
returned access denied** (session scope is `sense360store/esphome-public` +
`sense360store/esphome` only). The FanRelay WebFlash axes therefore stay
unchanged: the `WebFlash live repo re-verification` gate stays `NEEDS-TOOLING`,
the `S360-310` `module-availability.js` classification stays **prior-recorded
`design-pending`** (2026-05-22, PR #565) — not re-confirmed this session — and
`WF-IMPORT-RELAY-001` stays blocked behind `RELEASE-RELAY-001`. The
esphome-public side was re-verified fresh this session and is unchanged
(catalog `Ceiling-POE-VentIQ-FanRelay-RoomIQ` stays `hardware-pending` /
`webflash_build_matrix: false` / no `artifact_name`; no Relay wrapper under
[`products/webflash/`](../products/webflash/)). Full record in
[`webflash-drift-audit.md` §4.4](webflash-drift-audit.md#44-follow-up-resolution-log-updated-2026-05-27-by-webflash-live-check-001).
The recommended next Relay live step stays `WEBFLASH-RELAY-LIVE-CHECK-001`
(or this consolidated re-run) once read access is restored. No
`packages/**`, `products/**`, `products/webflash/**`, `config/**`,
`scripts/**`, `.github/workflows/**`, `components/**`, `include/**`,
`tests/**`, `firmware/**`, `manifest.json`, `firmware/sources.json`,
release-artifact / checksum / build-info, or `sense360store/WebFlash` edit;
no `webflash_build_matrix` flip; no `artifact_name`; no `schematic_status`
promotion; no WebFlash exposure / import / release / compliance /
hardware-stable claim; no fabricated evidence.

## PWM / S360-311 WebFlash posture

**Current state.** `S360-311 Sense360 PWM`,
`schematic_status: cataloged_unverified` (the module-side schematic
PDF is committed at
[`docs/hardware/schematics/S360-311-R4.pdf`](hardware/schematics/S360-311-R4.pdf)
under HW-ASSETS-003 but the JSON status has not been promoted; the
catalog `schematic_status` flip is owed to a separate JSON PR).
[`s360-311-r4-pwm.md`](hardware/s360-311-r4-pwm.md) status
`partial — schematic evidence available; package reconciliation
pending`. `packages/expansions/fan_pwm.yaml` and the legacy
four-channel `packages/expansions/sense360_fan_pwm.yaml` both carry
`needs-package-reconciliation` (SX1509-channel vs direct-ESP32-GPIO
disagreement; the verified Core schematic routes `TachPMW1..4` /
`Pul_Cou1..4` through the SX1509 expander, while the Core abstract
packages bind `fan_pwm_pin: ${expansion_gpio1}` /
`fan_tach_pin: ${expansion_gpio2}` to direct ESP32 GPIOs).
No non-legacy product YAML consumes S360-311; the legacy
[`products/sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml)
is `legacy-compatible` only and is not WebFlash-shippable. No
WebFlash wrapper / catalog entry / build-matrix entry / release
artifact / WebFlash import exists for FanPWM.

**Allowed WebFlash action now.** `not-webflash-ready`. No wrapper, no
catalog entry, no new build-matrix entry, no release artifact, no
WebFlash import. The existing legacy four-channel YAML stays
`legacy-compatible` and stays out of the WebFlash build matrix.

**Native ESP32-S3 GPIO FanPWM candidate — `S360-311-NATIVE-FANPWM-YAML-001`
(this PR).** A native-GPIO FanPWM candidate now exists alongside the legacy
SX1509 path:
[`packages/expansions/fan_pwm_native.yaml`](../packages/expansions/fan_pwm_native.yaml)
binds FanPWM control to native ESP32-S3 GPIO (`TachPMW1..4` ->
`IO10`/`IO11`/`IO12`/`IO39`, `ledc`) and tach / pulse-counter to native
ESP32-S3 GPIO (`Pul_Cou1`/`Pul_Cou2`/`Pul_Cou4` -> `IO17`/`IO18`/`IO9`,
internal-diagnostic `pulse_counter`), with **no SX1509** for PWM or tach;
`Pul_Cou3`/`IO46` is disabled/TBD (collides with the Core
`fan_status_led_pin` `GPIO46`) and `TachIO`/`IO16` is reserved/pending. It is
exercised by the compile-only skeleton
[`products/compile-only/ceiling-poe-fanpwm-native.yaml`](../products/compile-only/ceiling-poe-fanpwm-native.yaml)
(target `ceiling-poe-fanpwm-native-compile-only`,
`compile_validation_status: validated-full-compile` — a full `esphome
compile` run against the native composition PASSED under
S360-311-NATIVE-FANPWM-COMPILE-001, LOCAL run 2026-05-28, ESPHome 2026.4.5,
`esp32-s3-devkitc-1` / espidf / ESP-IDF v5.5.4, commit `643bbd3`, rc=0, Flash
51.7% / 948679 bytes; LOCAL run, no GitHub Actions run id, none fabricated).
**This changes no WebFlash posture:** a green compile is compile coverage only
and is NOT WebFlash exposure / readiness; the `FanPWM` token does not appear in
`config/webflash-builds.json`; no wrapper, no `webflash_build_matrix` flip,
no `artifact_name`, no release artifact; `rpm_supported: false`. FanPWM stays
`not-webflash-ready`.

**Native FanPWM bench evidence — `S360-311-NATIVE-FANPWM-BENCH-001`
(this PR; 2026-05-29).** The operator (`@wifispray`) flashed the **native**
ESP32-S3 GPIO FanPWM firmware (compile-proven at commit `643bbd3` under
S360-311-NATIVE-FANPWM-COMPILE-001) onto `S360-100-R4` + `S360-311-R4` and
re-ran the **functional** bench. **Functional PWM PASSED**
(operator-notes-only): all four channels individual + simultaneous +
low/med/high + restart-retention on the native composition (its own
functional bench — the 2026-05-26 legacy SX1509 bench does not transfer).
**This changes no WebFlash posture:** an operator functional bench is not
WebFlash exposure / readiness; the `FanPWM` token does not appear in
`config/webflash-builds.json`; no wrapper, no `webflash_build_matrix` flip,
no `artifact_name`, no release artifact. **Current / thermal were NOT
measured** and **tach / RPM were NOT measured** (`rpm_supported: false`;
`Pul_Cou3`/`IO46` disabled/TBD; `TachIO`/`IO16` reserved/pending). FanPWM
stays `not-webflash-ready`; `WEBFLASH-PWM-LIVE-CHECK-001` stays behind
`sense360store/WebFlash` access and the still-owed
`S360-311-CURRENT-THERMAL-001` measured envelope.

**Measured current / thermal run — `S360-311-CURRENT-THERMAL-001` (this PR;
2026-05-29) — NO values recorded.** The measured current / thermal bench
run owed by `PWM-6` / `PWM-13` was recorded, but the measurement intake
arrived **blank** — no per-channel / aggregate current, no MT3608 measured
voltage / sag / output-current ceiling, no inrush, and no thermal method /
ambient / hottest-location / measured °C / EMI observation; nothing was
inferred or estimated. **This changes no WebFlash posture:** the `FanPWM`
token still does not appear in `config/webflash-builds.json`; no wrapper,
no `webflash_build_matrix` flip, no `artifact_name`, no release artifact;
FanPWM stays `not-webflash-ready`. The measured envelope stays owed to a
re-run of `S360-311-CURRENT-THERMAL-001`. A measured PASS, when it lands,
closes `PWM-6` / `PWM-13` **only** and does **not** by itself enable
WebFlash — `PWM-15` (`WEBFLASH-PWM-LIVE-CHECK-001`) stays a separate gate
behind `sense360store/WebFlash` access.

**Future exposure class (intent).** `preview-candidate` as a standard
exposure, only after: `HW-PINMAP-311-FOLLOWUP` (standalone
schematic-backed reference doc; Core `J6` 1-to-13 pin-order verify
flag; UART-on-`J3`-pins-11/12 routing resolution; single-channel
vs four-channel canonical-abstraction decision) → `PACKAGE-PWM-001`
(FanPWM package YAML reconciliation; `CORE-ABSTRACT-BUS-001` rebind;
fate of legacy four-channel `sense360_fan_pwm.yaml`) →
`PRODUCT-PWM-001` (canonical product YAML; decide retain / migrate /
remove on the legacy four-channel YAML) → `WEBFLASH-PWM-001`
(wrapper + catalog + build-matrix on non-`stable` channel) →
`RELEASE-GAP-001` → `WF-IMPORT-GAP-001`.

**REQUIRED_CONFIGS posture.** `not-required-configs` by default.

**Kit / recommended posture.** `not-recommended` + `not-kit-default`.
The four-channel legacy retention / migration / removal decision is
owned by `PRODUCT-PWM-001`, not by this matrix.

**2026-05-26 — `PRODUCT-PWM-001` (product-YAML-only / no-WebFlash-exposure).**
The PWM-drive-only FanPWM package is implemented at the package layer
(PACKAGE-PWM-001-IMPLEMENT-001 / PR #590) and the **full ESPHome compile
is validated** (FW-COMPILE-PWM-001 / PR #591 + FW-COMPILE-PWM-RESULT-001 /
PR #592; `Compile-only Firmware Validation` run `26414398902`,
`compile_mode=full`, conclusion `success`,
`compile_validation_status: validated-full-compile`, `rpm_supported: false`).
`PRODUCT-PWM-001` now lands the canonical product YAML
[`products/sense360-ceiling-poe-fanpwm.yaml`](../products/sense360-ceiling-poe-fanpwm.yaml)
(config string `Ceiling-POE-FanPWM`) and the matching non-WebFlash catalog
row (`status: hardware-pending`, `webflash_build_matrix: false`, no
`artifact_name`, no `webflash_wrapper`). **WebFlash exposure stays blocked:**
no wrapper under `products/webflash/`, no `config/webflash-builds.json` row,
no build-matrix flip, no release artifact, no WebFlash import. WebFlash
exposure is owned by the separate `WEBFLASH-PWM-001` slice. **RPM is not
supported** (no `pulse_counter`, no per-fan / aggregate RPM; `TachIO` /
`GPIO16` reserved/pending). The bench gates (PWM polarity; per-fan /
aggregate current + thermal envelope; product bench) stay open and
`S360-311 schematic_status` stays `cataloged_unverified`; this is **not
hardware-stable readiness and not product-release approval**. The
`not-webflash-ready` posture above is unchanged. Pinned by
[`tests/test_pwm_product_readiness.py`](../tests/test_pwm_product_readiness.py).

**Cross-references.**
[`hardware/s360-311-r4-pwm.md`](hardware/s360-311-r4-pwm.md),
[`hardware/board-readiness-matrix.md` §S360-311](hardware/board-readiness-matrix.md#s360-311-sense360-pwm),
[`hardware/package-readiness-matrix.md` §fan_pwm.yaml](hardware/package-readiness-matrix.md#fan_pwmyaml--s360-311),
[`product-readiness-matrix.md` §FanPWM / S360-311](product-readiness-matrix.md#fanpwm--s360-311).

**2026-05-26 — `WEBFLASH-PWM-001-READINESS` (this PR; docs-only
re-evaluation, no exposure flip).** Re-evaluated FanPWM / S360-311
WebFlash-exposure readiness using the latest package / product /
full-compile / product-validation and `WEBFLASH-DRIFT-001` / PR #595
drift-audit evidence, **without exposing FanPWM to WebFlash**.
Re-verified against the live esphome-public files this session:

- **Product YAML exists** —
  [`products/sense360-ceiling-poe-fanpwm.yaml`](../products/sense360-ceiling-poe-fanpwm.yaml)
  (PRODUCT-PWM-001 / PR #593), config string `Ceiling-POE-FanPWM`,
  confirmed on disk; the matching
  [`config/product-catalog.json`](../config/product-catalog.json) row
  is `status: hardware-pending`, `webflash_build_matrix: false`, no
  `artifact_name`, no `webflash_wrapper`.
- **Package layer implemented (PWM-drive-only)** —
  [`packages/expansions/fan_pwm.yaml`](../packages/expansions/fan_pwm.yaml)
  composes the neutral binding
  [`packages/expansions/fan_pwm_sx1509.yaml`](../packages/expansions/fan_pwm_sx1509.yaml)
  (PACKAGE-PWM-001-IMPLEMENT-001 / PR #590): SX1509 hub on `core_i2c`,
  four PWM-drive outputs (`fan_pwm_drive_1..4` on channels 0..3), four
  user-facing speed controllers (`fan_pwm_1..4`). **No `pulse_counter`,
  no per-fan / aggregate RPM**; the four `Pul_Cou1..4` lines stay as
  INTERNAL diagnostic binary GPIO states. Pinned by
  [`tests/test_fan_pwm_package.py`](../tests/test_fan_pwm_package.py).
- **Full-compile evidence recorded** — the FanPWM compile-only target
  full-compiled green in run `26414398902` (`Compile-only Firmware
  Validation`, `compile_mode=full`, 10 targets, conclusion `success`;
  the `Run compile-only validator (full compile)` step ran
  `scripts/validate_compile_targets.py --compile` against
  [`products/compile-only/ceiling-poe-fanpwm.yaml`](../products/compile-only/ceiling-poe-fanpwm.yaml)
  and passed; FW-COMPILE-PWM-RESULT-001 / PR #592). This is
  **prior-recorded in-repo evidence**; the GitHub Actions run could not
  be re-read with the tooling scoped to this session.
- **`compile_validation_status: validated-full-compile` and
  `rpm_supported: false`** — both present on the FanPWM compile-only
  target in
  [`config/compile-only-targets.json`](../config/compile-only-targets.json).
  **Unlike FanRelay** (drift row #21, intentionally flag-less),
  FanPWM's compile-status flag is already set, so there is **no**
  narrative-vs-config compile-flag gap to resolve for PWM.
- **Product YAML composition validation** — the parity check
  `PwmProductMatchesValidatedCompileOnlyCompositionTests`
  (FW-COMPILE-PWM-PRODUCT-001 / PR #594) in
  [`tests/test_pwm_product_readiness.py`](../tests/test_pwm_product_readiness.py)
  pins that the product YAML composes the **identical** package set
  (same keys, same repo-relative `!include` targets) as the
  full-compile-validated compile-only skeleton, so the recorded full
  compile transfers to the product composition. **Live `esphome
  config` against the normal product YAML was NOT re-run this session**
  (ESPHome is not present in this environment), so live product-config
  validation of `products/sense360-ceiling-poe-fanpwm.yaml` remains
  pending — owed to a local `esphome config` run or the
  `Compile-only Firmware Validation` action (which already full-compiles
  the byte-equivalent composition).
- **No WebFlash wrapper** under
  [`products/webflash/`](../products/webflash/) — only Release-One, LED
  preview, and the blocked FanTRIAC reference.
- **No [`config/webflash-builds.json`](../config/webflash-builds.json)
  row** — only the 2 existing builds; the `FanPWM` token appears 0
  times.
- **No `artifact_name`, no `webflash_wrapper`,
  `webflash_build_matrix: false`** on the `Ceiling-POE-FanPWM` catalog
  row.
- **No release artifact** — no `.bin`, tag, checksum, or build-info
  manifest.
- **No import readiness** — WebFlash-owned; `WF-IMPORT-PWM-001` is
  blocked behind `RELEASE-PWM-001`. A **live re-read of
  `sense360store/WebFlash` was denied this session** (the GitHub scope
  is `sense360store/esphome-public` + `sense360store/esphome` only), so
  the WebFlash side stays prior-recorded, not re-verified —
  `NEEDS-TOOLING`. In particular `WEBFLASH-DRIFT-001` row #16 (WebFlash
  `scripts/utils/module-availability.js` carries **no** `S360-311`
  classification in any recorded snapshot) cannot be closed this PR;
  recording that classification stays owed to a live check.
- **RPM is not supported** — an SX1509 expander pin is compile-proven
  unable to back an ESPHome `pulse_counter`
  (PWM-SX1509-TACH-PROOF-001 / PR #589: `esphome config` rejects it
  with `[sx1509] is an invalid option for [pin]`); per-fan RPM is
  deferred to `COMPONENT-SX1509-TACH-001` or a bench-confirmed TachIO
  follow-up. `TachIO` / `GPIO16` stays reserved/pending.

**PWM WebFlash readiness table (re-evaluated 2026-05-26).** Status
legend: `CLOSED` (gate satisfied); `BLOCKING` (open gate that blocks
WebFlash exposure); `NEEDS-TOOLING` (cannot be re-verified without live
WebFlash / CI / ESPHome access); `NEEDS-OPERATOR-INPUT` (requires
operator evidence / sign-off); `OUT-OF-SCOPE` (not advanced by any
WebFlash slice and/or never by default).

| Gate | Status | Evidence | Next action |
|---|---|---|---|
| Product YAML exists | `CLOSED` | `products/sense360-ceiling-poe-fanpwm.yaml` (`Ceiling-POE-FanPWM`, PRODUCT-PWM-001 / PR #593); verified on disk this session | none — landed |
| Package layer implemented (PWM-drive-only) | `CLOSED` | `packages/expansions/fan_pwm.yaml` → `fan_pwm_sx1509.yaml` (PACKAGE-PWM-001-IMPLEMENT-001 / PR #590); four SX1509 PWM-drive controllers; pinned by `tests/test_fan_pwm_package.py` | none — landed |
| Full-compile evidence recorded | `CLOSED` | run `26414398902` (`compile_mode=full`, 10 targets, `success`); FW-COMPILE-PWM-RESULT-001 / PR #592; prior-recorded in-repo | none — recorded |
| `compile_validation_status` config flag | `CLOSED` | `validated-full-compile` on the FanPWM compile-only target; no narrative-vs-config gap (unlike FanRelay drift row #21) | none — flag set |
| `rpm_supported` config flag | `CLOSED` | `rpm_supported: false` on the FanPWM compile-only target; package wires no `pulse_counter` and no per-fan / aggregate RPM | none — flag set |
| Product YAML composition validation | `CLOSED` | `PwmProductMatchesValidatedCompileOnlyCompositionTests` (FW-COMPILE-PWM-PRODUCT-001 / PR #594) pins identical package set vs the full-compile-validated skeleton; full compile transfers | none — parity pinned |
| Live `esphome config` of the product YAML | `NEEDS-TOOLING` | ESPHome not present this session; byte-equivalent composition full-compiled via the compile-only skeleton (run `26414398902`) | local `esphome config products/sense360-ceiling-poe-fanpwm.yaml`, or rely on the full-compile action |
| Hardware evidence — package/product config posture | `CLOSED` | module-side schematic PDF `S360-311-R4.pdf` (HW-ASSETS-003); SX1509 routing per operator decision D2 (PWM-BLOCKER-REMOVAL-001 / PR #586); package reconciled at the package layer | none for config posture |
| Hardware evidence — PWM polarity bench | `NEEDS-OPERATOR-INPUT` | SX1509 PWM-drive output polarity vs the fan's PWM input (and any inversion / pull-up on the `TachPMW*` gate path) not bench-confirmed | operator / bench waveform confirmation (`S360-311-BENCH-001`) |
| Hardware evidence — per-fan / aggregate current + thermal envelope | `NEEDS-OPERATOR-INPUT` | per-fan current budget, MT3608 boost output-current ceiling, multi-fan aggregate load, and locked-rotor / inrush envelope not specified / not bench-characterised | operator-supplied bench / thermal evidence (`S360-311-BENCH-001`) |
| Hardware evidence — product bench | `NEEDS-OPERATOR-INPUT` | S360-311 / FanPWM product bench not complete; product YAML exists for manual / compile-your-own use only | operator-supplied product-bench sign-off (`S360-311-BENCH-001`) |
| WebFlash wrapper | `BLOCKING` | none under `products/webflash/` (only Release-One / LED / blocked FanTRIAC) | `WEBFLASH-PWM-001` (gated) |
| `config/webflash-builds.json` row | `BLOCKING` | absent — 2 builds only; 0 FanPWM tokens | `WEBFLASH-PWM-001` |
| `artifact_name` | `BLOCKING` | catalog row has none; `webflash_build_matrix: false` | `WEBFLASH-PWM-001` |
| Firmware release artifact | `BLOCKING` | no `.bin` / tag / checksum / build-info manifest | `RELEASE-PWM-001` (behind wrapper / build-matrix) |
| Import-source path (WebFlash `firmware/sources.json` / `manifest.json`) | `BLOCKING` | WebFlash-owned; no FanPWM source / build prior-recorded; `WF-IMPORT-PWM-001` blocked behind `RELEASE-PWM-001` | `WF-IMPORT-PWM-001` (cross-repo) |
| WebFlash live repo re-verification | `NEEDS-TOOLING` | `sense360store/WebFlash` read access denied this session; WebFlash facts stay prior-recorded | `WEBFLASH-PWM-LIVE-CHECK-001` once access restored |
| WebFlash `module-availability.js` `S360-311` classification (drift row #16) | `NEEDS-TOOLING` | `S360-311` not recorded in any WebFlash module-availability snapshot; cannot be read / recorded without live access | `WEBFLASH-PWM-LIVE-CHECK-001` (record the classification) |
| No-RPM / product UX expectations | `BLOCKING` | no WebFlash-side UX confirmed; any future UX must surface speed-only control and must **not** present per-fan / aggregate RPM entities | `WEBFLASH-PWM-001` + WebFlash-side UX |
| `TachIO` / `GPIO16` reserved/pending | `NEEDS-OPERATOR-INPUT` | binding binds no TachIO sensor; per-fan RPM via SX1509 `pulse_counter` is compile-proven unsupported (PWM-SX1509-TACH-PROOF-001 / PR #589) | `COMPONENT-SX1509-TACH-001` or a bench-confirmed TachIO follow-up |
| Compliance / safety approval | `NEEDS-OPERATOR-INPUT` | SELV low-voltage board (5 V → 12 V boost via MT3608; no mains path → `COMPLIANCE-001` mains gate does **not** apply); board-level thermal / EMI / EMC not certified | board-level thermal / EMI evidence via `S360-311-BENCH-001` (not a WebFlash slice) |
| REQUIRED_CONFIGS / kit / recommended membership | `OUT-OF-SCOPE` | `release_one_required_configs = ["Ceiling-POE-VentIQ-RoomIQ"]`; legacy four-channel `sense360-fan-pwm.yaml` retention / migration / removal owned by `PRODUCT-PWM-001` | never by default; separate explicit PR |

**Verdict — WebFlash PWM exposure stays blocked; recommended next PWM
PR is `WEBFLASH-PWM-LIVE-CHECK-001`, with `S360-311-BENCH-001` as the
substantive evidence gate.** The package / product / full-compile /
`compile_validation_status` / `rpm_supported` / composition-parity /
config-posture-hardware gates are `CLOSED` (this is **stronger** than
the FanRelay state — PWM's compile-status flag is already set, so there
is no compile-flag gap), but the non-WebFlash gates are **not** all
clean: the **PWM polarity**, **per-fan / aggregate current + thermal
envelope**, and **product bench** caveats remain `NEEDS-OPERATOR-INPUT`;
`TachIO` / `GPIO16` stays reserved/pending; the no-RPM UX expectation is
`BLOCKING` on the WebFlash side; and the WebFlash side cannot be
re-verified live this session (`NEEDS-TOOLING`, including the still-owed
`S360-311` module-availability classification, `WEBFLASH-DRIFT-001`
row #16). This is therefore **not** the "only WebFlash-wrapper /
artifact / import missing" case that would justify a
`WEBFLASH-PWM-002-WRAPPER-PLAN` slice, and **not** `WEBFLASH-PWM-001`.
The recommended next esphome-public step is
**`WEBFLASH-PWM-LIVE-CHECK-001`** — a re-run of the live WebFlash
readiness / drift check (`firmware/sources.json`, `manifest.json`,
`scripts/utils/module-availability.js`, `scripts/data/kit-presets.js`,
import grammar; record the `S360-311` classification) once read access
to `sense360store/WebFlash` is restored — while the substantive
exposure blocker is the bench evidence, owned by **`S360-311-BENCH-001`**
(PWM polarity + per-fan / aggregate current + thermal envelope + product
bench). Both must clear before any `WEBFLASH-PWM-001` wrapper / catalog /
build-matrix work is even considered.

**Guardrails honoured.** **No `packages/**`, `products/**`,
`products/webflash/**`, `config/**` (including
`config/webflash-builds.json`, `config/product-catalog.json`,
`config/compile-only-targets.json`, `config/firmware-combination-matrix.json`),
`scripts/**`, `.github/workflows/**`, `components/**`, `include/**`,
`tests/**`, `firmware/**`, `manifest.json`, `firmware/sources.json`,
release-artifact / checksum / build-info, or `sense360store/WebFlash`
edit.** No WebFlash wrapper added; no `webflash_build_matrix` flip; no
`artifact_name`; no `webflash_wrapper`; no `config_string` /
`release_one_required_configs` / `canonical_modules` change; no
`schematic_status` / `schematic_file` promotion (`S360-311` stays
`cataloged_unverified`); no RPM added or claimed. Release-One stays
`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`; LED preview stays
`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`; FanTRIAC stays `blocked` /
`HW-005`. **No WebFlash import-readiness claim, no WebFlash exposure
claim, no release-readiness claim, no RPM-support claim, no compliance /
safety approval claim, no hardware-stable readiness claim, and no
fabricated WebFlash evidence.**

**2026-05-26 — `S360-311-BENCH-RESULT-001` (this PR; docs-only) — note on
WebFlash surface.** The operator (`@wifispray`) ran the requested FanPWM
bench; the result is recorded (operator-notes-only attestation) in
[`hardware/s360-311-r4-pwm.md` §S360-311-BENCH-RESULT-001](hardware/s360-311-r4-pwm.md#s360-311-bench-result-001--fanpwm-operator-bench-result-2026-05-26)
and [`blocker-burndown.md` §5B](blocker-burndown.md#5b-s360-311-bench-result-001--fanpwm-operator-bench-result-2026-05-26).
**The WebFlash surface is unchanged and stays `not-webflash-ready`.** Two
of the hardware-evidence rows in the readiness table above move from
`NEEDS-OPERATOR-INPUT` to satisfied at the **product-bench** level — the
**PWM polarity** row (operator observed increasing duty → increasing fan
speed; non-inverting, no inversion required) and the **product bench** row
(all four channels individually speed-controlled, all four simultaneous
for 1+ hour, restart retained the last commanded speed on `S360-311-R4`).
The **per-fan / aggregate current + thermal envelope** row stays
`NEEDS-OPERATOR-INPUT` (current **not measured**; only a qualitative 1+
hour no-heat observation, **no** measured °C). **None of this advances
the WebFlash side:** the WebFlash wrapper, `config/webflash-builds.json`
row, `artifact_name`, release artifact, and import-source gates stay
`BLOCKING`; the live `sense360store/WebFlash` re-verification and the
still-owed `S360-311` module-availability classification stay
`NEEDS-TOOLING`; `TachIO` / `GPIO16` stays reserved and RPM stays
unsupported (no `pulse_counter`). Operator notes are enough for the
product bench but **not** for WebFlash exposure. The recommended next PWM
PR for the **measured** envelope is **`S360-311-CURRENT-THERMAL-001`**;
**`WEBFLASH-PWM-LIVE-CHECK-001`** stays blocked behind WebFlash access,
and **no `WEBFLASH-PWM-001` wrapper is recommended** until measured
current / thermal *and* the WebFlash live classification are done. No
`packages/**`, `products/**`, `products/webflash/**`, `config/**`,
`scripts/**`, `.github/workflows/**`, `components/**`, `include/**`,
`tests/**`, `firmware/**`, `manifest.json`, `firmware/sources.json`,
release-artifact / checksum / build-info, or `sense360store/WebFlash`
edit; no `webflash_build_matrix` flip; no `artifact_name`; no
`schematic_status` promotion (`S360-311` stays `cataloged_unverified`); no
WebFlash exposure / import / release / RPM / compliance / hardware-stable
claim; no fabricated evidence.

**2026-05-27 — `PWM-BLOCKER-RECLASSIFY-001` (this PR; docs-only) — note on
WebFlash surface.** The remaining FanPWM gaps are **reclassified by release
scope**, and the reclassification **keeps the WebFlash surface fully
blocked.** It explicitly names **WebFlash live access / `S360-311`
module-availability** and the **WebFlash wrapper / build / artifact /
import** chain as a **WebFlash-exposure blocker only** (they do **not**
gate the FanPWM package / product / `config` layer, which is already
complete), and it keeps the **measured per-channel + aggregate current and
measured thermal temperature** as a **WebFlash / release / hardware-stable
blocker**. So the FanPWM WebFlash surface stays **`not-webflash-ready`**:
the wrapper, `config/webflash-builds.json` row, `artifact_name`, release
artifact, and import-source gates stay `BLOCKING`; the live
`sense360store/WebFlash` re-verification and the still-owed `S360-311`
module-availability classification stay `NEEDS-TOOLING`; `TachIO` /
`GPIO16` stays reserved (RPM / diagnostics blocker only) and RPM stays
unsupported (out of scope for the PWM-drive-only product). Operator notes
remain enough for the product bench but **not** for WebFlash exposure. The
recommended measured-envelope PR is **`S360-311-CURRENT-THERMAL-001`**;
**`WEBFLASH-PWM-LIVE-CHECK-001`** stays blocked behind WebFlash access, and
**no `WEBFLASH-PWM-001` wrapper is recommended** until measured current /
thermal *and* the WebFlash live classification are done. Canonical table in
[`hardware/s360-311-r4-pwm.md` §PWM-BLOCKER-RECLASSIFY-001](hardware/s360-311-r4-pwm.md#pwm-blocker-reclassify-001--fanpwm-remaining-blockers-reclassified-by-release-scope-2026-05-27).
No `packages/**`, `products/**`, `products/webflash/**`, `config/**`,
`scripts/**`, `.github/workflows/**`, `components/**`, `include/**`,
`tests/**`, `firmware/**`, `manifest.json`, `firmware/sources.json`,
release-artifact / checksum / build-info, or `sense360store/WebFlash`
edit; no `webflash_build_matrix` flip; no `artifact_name`; no
`schematic_status` promotion (`S360-311` stays `cataloged_unverified`); no
WebFlash exposure / import / release / RPM / compliance / hardware-stable
claim; no fabricated evidence.

**2026-05-27 — `WEBFLASH-LIVE-CHECK-001` (this PR; docs-only live re-check,
no exposure flip).** Re-attempted the live read of `sense360store/WebFlash`
this session via three read-only GitHub methods (repo root,
`scripts/utils/module-availability.js`, and a branch listing) — **all three
returned access denied** (session scope is `sense360store/esphome-public` +
`sense360store/esphome` only). The FanPWM WebFlash axes therefore stay
unchanged: the `WebFlash live repo re-verification` gate stays `NEEDS-TOOLING`
and the `S360-311` `module-availability.js` classification stays **not recorded
in any snapshot** (`WEBFLASH-DRIFT-001` row #16) — it cannot be captured here
without fabricating evidence. The esphome-public side was re-verified fresh
this session and is unchanged (catalog `Ceiling-POE-FanPWM` stays
`hardware-pending` / `webflash_build_matrix: false` / no `artifact_name`; no
FanPWM wrapper under [`products/webflash/`](../products/webflash/); no RPM
added or claimed). Full record in
[`webflash-drift-audit.md` §4.4](webflash-drift-audit.md#44-follow-up-resolution-log-updated-2026-05-27-by-webflash-live-check-001).
The recommended next PWM live step stays `WEBFLASH-PWM-LIVE-CHECK-001` (or this
consolidated re-run) once read access is restored, with `S360-311-BENCH-001`
as the substantive evidence gate. No `packages/**`, `products/**`,
`products/webflash/**`, `config/**`, `scripts/**`, `.github/workflows/**`,
`components/**`, `include/**`, `tests/**`, `firmware/**`, `manifest.json`,
`firmware/sources.json`, release-artifact / checksum / build-info, or
`sense360store/WebFlash` edit; no `webflash_build_matrix` flip; no
`artifact_name`; no `schematic_status` promotion; no WebFlash exposure /
import / release / RPM / compliance / hardware-stable claim; no fabricated
evidence.

## DAC / S360-312 WebFlash posture

**Current state.** `S360-312 Sense360 DAC`,
`schematic_status: cataloged_unverified` (module-side schematic PDF
committed at
[`docs/hardware/schematics/S360-312-R4.pdf`](hardware/schematics/S360-312-R4.pdf)
under HW-ASSETS-003).
[`s360-312-r4-dac.md`](hardware/s360-312-r4-dac.md) status
`partial — schematic evidence available; package reconciliation
pending`. `packages/expansions/fan_gp8403.yaml` carries
`needs-package-reconciliation` (Core `J7` pin-1 `+5V` vs Module `J1`
pin-1 `+3.3V` voltage-rail discrepancy; DIP-switch I²C address-selection
scheme; UART0-vs-Nextion arbitration; stale header-comment block on
lines 13–18). The `FanDAC ↔ AirIQ` mutex
(`config/webflash-compatibility.json` `rules.fandac_conflicts_with_airiq: true`)
constrains any future product YAML. No FanDAC product YAML
exists. No WebFlash wrapper / catalog entry / build-matrix entry /
release artifact / WebFlash import exists.

**2026-05-23 — `PRODUCT-DAC-001-READINESS-REFRESH` (after PACKAGE-DAC-001 / PR #573).**
The FanDAC package is now **implemented at the package layer** by
`PACKAGE-DAC-001-IMPLEMENT-001` / PR #573 (two GP8403 chips, four
neutral outputs, per-chip address + range substitutions; see
[`product-readiness-matrix.md` §FanDAC / S360-312](product-readiness-matrix.md#fandac--s360-312)).
**This does not advance WebFlash exposure.** WebFlash exposure for
FanDAC remains **blocked**: no WebFlash wrapper under
[`products/webflash/`](../products/webflash/), no
[`config/product-catalog.json`](../config/product-catalog.json) catalog
entry, no `webflash_build_matrix: true` flip, no
[`config/webflash-builds.json`](../config/webflash-builds.json)
build-matrix row, no `artifact_name`, no release artifact, no WebFlash
import. The package-layer landing is upstream of `PRODUCT-DAC-001`,
which **`FW-COMPILE-DAC-001`** *(this PR)* now partially unblocks: it
fixed the `gp8403:` `voltage:` substitutions from the invalid `0-10V`
string to ESPHome's valid `10V` enum (customer-facing 0-10V) and added
the `Ceiling-POE-FanDAC` compile-only target under
[`products/compile-only/`](../products/compile-only/). The actual
`esphome config` / `--compile` pass is owed to CI
(`compile_validation_status: pending-ci`); `PRODUCT-DAC-001` stays
gated on that CI pass plus `S360-312 schematic_status: verified`.
WebFlash exposure stays `WEBFLASH-DAC-001`, gated on `PRODUCT-DAC-001`
landing. The `FanDAC ↔ AirIQ` mutex is not relaxed.

**2026-05-23 — `FW-COMPILE-DAC-RESULT-001` (this PR; docs-only record
of CI result).** The `Compile-only Firmware Validation` workflow ran
against the expanded nine-target compile-only lane after
`FW-COMPILE-DAC-001` / PR #575 added the `Ceiling-POE-FanDAC`
compile-only target, and the **metadata-validation lane passed** —
GitHub Actions Run ID `26332462496`, status `completed`, conclusion
`success`, target count 9; companion Quick Validation Run ID
`26332462516` also succeeded. **FanDAC compile-only (metadata)
validation now has a green CI result; WebFlash exposure
(`WEBFLASH-DAC-001`) remains blocked.** Precise scope: the
`Compile-only Targets — Full ESPHome Compile` job was **`skipped`** (it
runs only on a manual `workflow_dispatch` with `compile_mode=full` per
[`.github/workflows/compile-only.yml`](../.github/workflows/compile-only.yml)
line 103), so **no `esphome config` / `esphome compile` ran against the
FanDAC skeleton in CI** — the green result proves the metadata /
structural lane (target shape, cross-references, count 9, guardrails,
the `voltage: 10V` enum pinned by `tests/test_fandac_package.py` against
the documented ESPHome schema), not a full ESPHome compile. The CI
`--compile` pass remains owed (`compile_validation_status: pending-ci`).
A green compile-only CI result does **not** advance any WebFlash gate.
Re-verified against the live files: **no FanDAC WebFlash wrapper** under
[`products/webflash/`](../products/webflash/); **no FanDAC row in
[`config/webflash-builds.json`](../config/webflash-builds.json)** (the
`FanDAC` token is absent there); `release_one_required_configs` stays
`["Ceiling-POE-VentIQ-RoomIQ"]`; no `webflash_build_matrix: true` flip;
no `artifact_name`; no `webflash_wrapper`; the
[`config/product-catalog.json`](../config/product-catalog.json) has no
FanDAC entry; the `FanDAC ↔ AirIQ` mutex is not relaxed; `S360-312`
stays `cataloged_unverified`. **No `packages/**`, `products/**`,
`products/webflash/**`, `config/**`, `scripts/**`,
`.github/workflows/**`, `components/**`, `include/**`, `tests/**`,
`firmware/**`, `manifest.json`, `firmware/sources.json`,
release-artifact, checksum, build-info, or WebFlash-repo edit; no
`compile-only-targets.json` / `compile-only-candidates.json` edit
(totals stay 9 after PR #575).** **No WebFlash exposure / import
readiness claim; no `WEBFLASH-DAC-001` / `RELEASE-DAC-001` /
`WF-IMPORT-DAC-001` unblock claim; no DAC product readiness claim; no
release-artifact claim; no harness / fan bench validation claim; no
compliance claim; no simultaneous per-output 0-5V + 0-10V on a single
GP8403 claim.** The next chain step is `PRODUCT-DAC-001`, which stays
gated on the still-owed full `--compile` pass + `S360-312
schematic_status: verified`; `WEBFLASH-DAC-001` stays blocked behind it.

**2026-05-23 — `PRODUCT-DAC-001` (this PR; product-YAML-only / no-WebFlash-exposure).**
The canonical FanDAC product YAML
[`products/sense360-ceiling-poe-fandac.yaml`](../products/sense360-ceiling-poe-fandac.yaml)
(config string `Ceiling-POE-FanDAC`) and its
[`config/product-catalog.json`](../config/product-catalog.json)
`hardware-pending` row landed at the **product layer only**. **This does
NOT advance WebFlash exposure.** Re-verified against the live files:
**no FanDAC WebFlash wrapper** under
[`products/webflash/`](../products/webflash/); **no FanDAC row in
[`config/webflash-builds.json`](../config/webflash-builds.json)** (the
`FanDAC` token is absent there); the catalog row keeps
`webflash_build_matrix: false`, declares no `artifact_name` and no
`webflash_wrapper`; `release_one_required_configs` stays
`["Ceiling-POE-VentIQ-RoomIQ"]`; the `FanDAC ↔ AirIQ` mutex is not
relaxed; `S360-312` stays `cataloged_unverified`. The product YAML
carries explicit caveats that the full ESPHome `--compile` pass is still
**owed** (`compile_validation_status: pending-ci`; only the compile-only
metadata lane is green per FW-COMPILE-DAC-RESULT-001 / PR #576), plus the
`J3` silk transposition and Cloudlift S12 harness / product-bench
residuals. **`WEBFLASH-DAC-001` remains BLOCKED** (and `RELEASE-DAC-001` /
`WF-IMPORT-DAC-001` behind it). No WebFlash / import / release /
compliance / hardware-stable readiness claim is made. The next chain step
is `FW-COMPILE-DAC-FULL-001` (record the owed full compile) or
`WEBFLASH-DAC-001-READINESS-REFRESH` (re-evaluate the WebFlash gate)
before `WEBFLASH-DAC-001` itself.

**2026-05-24 — `FW-COMPILE-DAC-FULL-RESULT-001` (this PR; docs-only
record of successful full-compile result).** The manual
`workflow_dispatch` `compile_mode=full` run `26364679370` — the same run
`FW-COMPILE-RELAY-FULL-RESULT-001` / PR #579 recorded — ran against
post-#578 `main` (merge commit `4906a22`) and **passed**, and it **also
validates the FanDAC compile-only target**: event `workflow_dispatch`,
mode `compile_mode=full`, status `completed`, conclusion `success`,
**9** compile-only targets; the `Compile-only Targets — Full ESPHome
Compile` job (`77606324332`) completed `success`. The full-compile lane
runs `esphome compile` against every
[`config/compile-only-targets.json`](../config/compile-only-targets.json)
target and fails on the first failure, so `success` proves all nine —
including `ceiling-poe-fandac-compile-only` →
[`products/compile-only/ceiling-poe-fandac.yaml`](../products/compile-only/ceiling-poe-fandac.yaml)
(`Ceiling-POE-FanDAC`) — compiled. **This supersedes the full-compile
concern left owed by FW-COMPILE-DAC-RESULT-001 / PR #576** and
compile-validates the GP8403 `voltage: 10V` enum fix in ESPHome itself.
**FanDAC now full-compiles green, but WebFlash DAC exposure remains
blocked.** A green full-compile CI result does **not** advance any
WebFlash gate. Re-verified against the live files: no FanDAC WebFlash
wrapper under [`products/webflash/`](../products/webflash/); no FanDAC
row in [`config/webflash-builds.json`](../config/webflash-builds.json)
(the `FanDAC` token is absent there); the
[`config/product-catalog.json`](../config/product-catalog.json) FanDAC
row (PRODUCT-DAC-001 / PR #577) stays `status: hardware-pending` /
`webflash_build_matrix: false` / no `artifact_name` / no
`webflash_wrapper`; `release_one_required_configs` stays
`["Ceiling-POE-VentIQ-RoomIQ"]`; the `FanDAC ↔ AirIQ` mutex is not
relaxed; `S360-312` stays `cataloged_unverified`. **No `packages/**`,
`products/**`, `products/webflash/**`, `config/**`, `scripts/**`,
`.github/workflows/**`, `components/**`, `include/**`, `tests/**`,
`firmware/**`, `manifest.json`, `firmware/sources.json` edit; no
`webflash_build_matrix` flip; no `artifact_name`; no `webflash_wrapper`;
no `release_one_required_configs` change; no `schematic_status` /
`schematic_file` promotion; no COMPLIANCE-001 movement.** **No WebFlash
exposure / import-readiness claim; no `WEBFLASH-DAC-001` /
`RELEASE-DAC-001` / `WF-IMPORT-DAC-001` unblock claim; no compliance or
safety-certification claim; no simultaneous per-output 0-5V + 0-10V on a
single GP8403 claim.** `WEBFLASH-DAC-001` stays blocked behind
`PRODUCT-DAC-001`'s remaining WebFlash gates.

**2026-05-24 — `COMPILE-STATUS-FLAGS-001` (config/status reconciliation).**
Flips the FanDAC compile-only target's
`compile_validation_status` in
[`config/compile-only-targets.json`](../config/compile-only-targets.json)
from `pending-ci` to `validated-full-compile` (the state already proven by
run `26364679370`) and updates the two tests that pinned `pending-ci`.
**This is a compile-status reconciliation only and does NOT advance any
WebFlash gate.** `S360-312` stays `cataloged_unverified`; no FanDAC
WebFlash wrapper, no [`config/webflash-builds.json`](../config/webflash-builds.json)
row, no `webflash_build_matrix` flip, no `artifact_name`, no release
artifact; `release_one_required_configs` unchanged; the `FanDAC ↔ AirIQ`
mutex is not relaxed; `config/product-catalog.json` and the product YAML
are untouched. **`WEBFLASH-DAC-001`, `RELEASE-DAC-001`, and
`WF-IMPORT-DAC-001` stay BLOCKED**; no WebFlash exposure / import readiness
is claimed.

**Allowed WebFlash action now.** `not-webflash-ready`. No wrapper,
no build-matrix entry, no release artifact, no WebFlash import. A
product-layer catalog row (`webflash_build_matrix: false`) now exists for
`Ceiling-POE-FanDAC` (PRODUCT-DAC-001) but does NOT authorise any
WebFlash surface. The `FanDAC ↔ AirIQ` mutex is not relaxed.

**Future exposure class (intent).** `preview-candidate` as a standard
exposure, only after: `PACKAGE-DAC-001` (FanDAC package YAML
implementation — **landed PR #573**) → `FW-COMPILE-DAC-001`
(compile-only validation of the `voltage:` binding; confirm `0-10V`
validates or record the `0-10V` → `10V` fix) → `PRODUCT-DAC-001`
(canonical product YAML; outcome-first user-facing names; carry the
`J2` / `J3` harness-trace + `J3` silkscreen-transposition caveats;
Nextion / `J7` out of scope unless the product drives a display;
enforce `FanDAC ↔ AirIQ` mutex; no AirIQ-bearing FanDAC product) →
`WEBFLASH-DAC-001` (wrapper + catalog + build-matrix on non-`stable`
channel) → `RELEASE-DAC-001` → `WF-IMPORT-DAC-001`.

**REQUIRED_CONFIGS posture.** `not-required-configs` by default. The
`FanDAC ↔ AirIQ` mutex narrows the eligible config-string space; any
future REQUIRED_CONFIGS membership is a separate explicit PR.

**Kit / recommended posture.** `not-recommended` + `not-kit-default`.
The hardware-catalog `description` ("0 to 10V analog fan driver, for
example Cloudlift S12") understates the dual-DAC capacity recorded
in the schematic (two `GP8403-TC50-EW` ICs driving two 3-pin
outputs); broadening the catalog `description` is a separate later
PR and is **not** in scope for this matrix.

**Cross-references.**
[`hardware/s360-312-r4-dac.md`](hardware/s360-312-r4-dac.md),
[`hardware/board-readiness-matrix.md` §S360-312](hardware/board-readiness-matrix.md#s360-312-sense360-dac),
[`hardware/package-readiness-matrix.md` §fan_gp8403.yaml](hardware/package-readiness-matrix.md#fan_gp8403yaml--s360-312),
[`product-readiness-matrix.md` §FanDAC / S360-312](product-readiness-matrix.md#fandac--s360-312).

**2026-05-26 — `WEBFLASH-DAC-001-READINESS` (this PR; docs-only
re-evaluation, no exposure flip).** Re-evaluated FanDAC / S360-312
WebFlash-exposure readiness using the latest package / product /
full-compile and `WEBFLASH-DRIFT-001` / PR #595 drift-audit evidence,
**without exposing FanDAC to WebFlash**. Re-verified against the live
esphome-public files this session:

- **Product YAML exists** —
  [`products/sense360-ceiling-poe-fandac.yaml`](../products/sense360-ceiling-poe-fandac.yaml)
  (PRODUCT-DAC-001 / PR #577), config string `Ceiling-POE-FanDAC`,
  confirmed on disk.
- **Package layer implemented** —
  [`packages/expansions/fan_dac.yaml`](../packages/expansions/fan_dac.yaml)
  (canonical alias, PACKAGE-NAMING-ALIASES-FANDAC-001) → the
  [`packages/expansions/fan_gp8403.yaml`](../packages/expansions/fan_gp8403.yaml)
  implementation (PACKAGE-DAC-001 / PR #573): two GP8403 dual-channel
  I²C DACs (`fan_dac_1` / IC1 at `0x58`, `fan_dac_2` / IC2 at `0x59`)
  on the shared `${fan_dac_i2c_id}` (`core_i2c`) bus, four neutral
  outputs (`fan_dac_1_vout0` … `fan_dac_2_vout1`), per-chip address +
  range substitutions.
- **Full-compile evidence recorded** — the FanDAC compile-only target
  full-compiled green in run `26364679370` (`workflow_dispatch` /
  `compile_mode=full`, 9 targets, conclusion `success`; the
  `Compile-only Targets — Full ESPHome Compile` job `77606324332`
  completed `success`; the lane runs `esphome compile` against every
  [`config/compile-only-targets.json`](../config/compile-only-targets.json)
  target and fails on the first failure, so `success` proves all nine
  including `ceiling-poe-fandac-compile-only`; FW-COMPILE-DAC-FULL-RESULT-001
  / PR #580). This is **prior-recorded in-repo evidence**; the GitHub
  Actions run could not be re-read with the tooling scoped to this
  session.
- **`compile_validation_status: validated-full-compile` and
  `voltage_enum_fixed: true`** — both present on the FanDAC
  compile-only target in
  [`config/compile-only-targets.json`](../config/compile-only-targets.json)
  (flipped from `pending-ci` by COMPILE-STATUS-FLAGS-001 / PR #581;
  the `gp8403:` `voltage:` `0-10V` → ESPHome's `10V` enum fix by
  FW-COMPILE-DAC-001 / PR #575). **Unlike FanRelay** (drift row #21,
  intentionally flag-less), FanDAC's compile-status flag is already
  set, so there is **no** narrative-vs-config compile-flag gap to
  resolve for DAC.
- **No WebFlash wrapper** under
  [`products/webflash/`](../products/webflash/) — only Release-One, LED
  preview, and the blocked FanTRIAC reference.
- **No [`config/webflash-builds.json`](../config/webflash-builds.json)
  row** — only the 2 existing builds; the `FanDAC` token appears 0
  times.
- **No `artifact_name`, no `webflash_wrapper`,
  `webflash_build_matrix: false`** on the
  [`config/product-catalog.json`](../config/product-catalog.json)
  `Ceiling-POE-FanDAC` row (`status: hardware-pending`).
- **No release artifact** — no `.bin`, tag, checksum, or build-info
  manifest.
- **No import readiness** — WebFlash-owned; `WF-IMPORT-DAC-001` is
  blocked behind `RELEASE-DAC-001`. A **live re-read of
  `sense360store/WebFlash` was denied this session** (the GitHub scope
  is `sense360store/esphome-public` + `sense360store/esphome` only), so
  the WebFlash side stays prior-recorded, not re-verified —
  `NEEDS-TOOLING`. In particular `WEBFLASH-DRIFT-001` row #17
  (WebFlash `scripts/utils/module-availability.js` carries **no**
  `S360-312` classification in any recorded snapshot) cannot be closed
  this PR; recording that classification stays owed to a live check.
- **`FanDAC ↔ AirIQ` mutex honoured** — `config/webflash-compatibility.json`
  `rules.fandac_conflicts_with_airiq: true`; no `AirIQ`-bearing FanDAC
  combination exists in
  [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json)
  (24 FanDAC config strings, 0 with an `AirIQ` token); any
  `Ceiling-POE-AirIQ-FanDAC-*` is `invalid-combination`.

**DAC WebFlash readiness table (re-evaluated 2026-05-26).** Status
legend: `CLOSED` (gate satisfied); `BLOCKING` (open gate that blocks
WebFlash exposure); `NEEDS-TOOLING` (cannot be re-verified without live
WebFlash / CI access); `NEEDS-OPERATOR-INPUT` (requires operator
evidence / sign-off); `OUT-OF-SCOPE` (not advanced by any WebFlash slice
and/or never by default).

| Gate | Status | Evidence | Next action |
|---|---|---|---|
| Product YAML exists | `CLOSED` | `products/sense360-ceiling-poe-fandac.yaml` (`Ceiling-POE-FanDAC`, PRODUCT-DAC-001 / PR #577); verified on disk this session | none — landed |
| Package layer implemented | `CLOSED` | `packages/expansions/fan_dac.yaml` → `fan_gp8403.yaml` (PACKAGE-DAC-001 / PR #573); two GP8403 chips, four neutral outputs; pinned by `tests/test_fandac_package.py` | none — landed |
| Full-compile evidence recorded | `CLOSED` | run `26364679370` (`compile_mode=full`, 9 targets, `success`); fails-on-first → FanDAC green (FW-COMPILE-DAC-FULL-RESULT-001 / PR #580); prior-recorded in-repo | none — recorded |
| `compile_validation_status` config flag | `CLOSED` | `validated-full-compile` on the FanDAC compile-only target (COMPILE-STATUS-FLAGS-001 / PR #581); no narrative-vs-config gap (unlike FanRelay drift row #21) | none — flag set |
| `voltage:` enum fixed | `CLOSED` | `voltage_enum_fixed: true`; package substitutions `10V` (customer-facing 0-10V), FW-COMPILE-DAC-001 / PR #575; compile-validated by run `26364679370` | none — fixed |
| Hardware evidence — package/product config posture | `CLOSED` | HW-ASSETS-003 schematic PDF `S360-312-R4.pdf`; board-audit rows 3/6/8 (DIP-switch↔address, output-range policy, `J2`/`J3` pin-1 identity) closed by PR #572 | none for config posture |
| Hardware evidence — `J3` `out0`/`out1` silkscreen transposition | `NEEDS-OPERATOR-INPUT` | pin-1 pad (IC2 VOUT0) silk-labelled `out1`, pin-3 pad (IC2 VOUT1) silk-labelled `out0`; carried as a product caveat, not bench-confirmed | operator / bench confirmation before printed `J3` labels are relied upon |
| Hardware evidence — Cloudlift S12 harness / product bench | `NEEDS-OPERATOR-INPUT` | no fan / harness artifact captured; conductor-by-conductor `J2`/`J3` → Cloudlift S12 fan-input trace unresolved | operator-supplied bench / harness evidence (`S360-312-BENCH-*`) |
| WebFlash wrapper | `BLOCKING` | none under `products/webflash/` (only Release-One / LED / blocked FanTRIAC) | `WEBFLASH-DAC-001` (gated) |
| `config/webflash-builds.json` row | `BLOCKING` | absent — 2 builds only; 0 FanDAC tokens | `WEBFLASH-DAC-001` |
| `artifact_name` | `BLOCKING` | catalog row has none; `webflash_build_matrix: false` | `WEBFLASH-DAC-001` |
| Firmware release artifact | `BLOCKING` | no `.bin` / tag / checksum / build-info manifest | `RELEASE-DAC-001` (behind wrapper / build-matrix) |
| Import-source path (WebFlash `firmware/sources.json` / `manifest.json`) | `BLOCKING` | WebFlash-owned; no FanDAC source / build prior-recorded; `WF-IMPORT-DAC-001` blocked behind `RELEASE-DAC-001` | `WF-IMPORT-DAC-001` (cross-repo) |
| WebFlash live repo re-verification | `NEEDS-TOOLING` | `sense360store/WebFlash` read access denied this session; WebFlash facts stay prior-recorded | `WEBFLASH-DAC-LIVE-CHECK-001` once access restored |
| WebFlash `module-availability.js` `S360-312` classification (drift row #17) | `NEEDS-TOOLING` | `S360-312` not recorded in any WebFlash module-availability snapshot; cannot be read / recorded without live access | `WEBFLASH-DAC-LIVE-CHECK-001` (record the classification) |
| Voltage-mode / product UX expectations | `BLOCKING` | no WebFlash-side 0-10V/0-5V voltage-mode UX confirmed; per-chip (not per-output) range limitation must surface in any future UX | `WEBFLASH-DAC-001` + WebFlash-side UX |
| Compliance / safety approval | `BLOCKING` | SELV 0-10V control signalling only; no board-level creepage / clearance / thermal / EMI / EMC certification; `COMPLIANCE-001` not signed off | `COMPLIANCE-001` (separate; not a WebFlash slice) |
| `FanDAC ↔ AirIQ` mutex | `CLOSED` | `fandac_conflicts_with_airiq: true`; 0 AirIQ-bearing FanDAC combos in `firmware-combination-matrix.json` | none — enforced; not relaxed |
| REQUIRED_CONFIGS / kit / recommended membership | `OUT-OF-SCOPE` | `release_one_required_configs = ["Ceiling-POE-VentIQ-RoomIQ"]`; duct-fan kit `S360-KIT-DUCT-0-10V` stays `future-expansion` / `hardware-pending` | never by default; separate explicit PR |

**Verdict — WebFlash DAC exposure stays blocked; recommended next DAC
PR is `WEBFLASH-DAC-LIVE-CHECK-001`.** The package / product /
full-compile / `compile_validation_status` / `voltage`-enum /
config-posture-hardware / `FanDAC ↔ AirIQ` mutex gates are `CLOSED`
(this is **stronger** than the FanRelay state — DAC's compile-status
flag is already set, so there is no compile-flag gap), but the
non-WebFlash gates are **not** all clean: the `J3` silkscreen
transposition and the Cloudlift S12 harness / product-bench caveats
remain `NEEDS-OPERATOR-INPUT`, compliance / safety sign-off remains
`BLOCKING`, and the WebFlash side cannot be re-verified live this
session (`NEEDS-TOOLING`, including the still-owed `S360-312`
module-availability classification, `WEBFLASH-DRIFT-001` row #17). This
is therefore **not** the "only WebFlash-wrapper / artifact / import
missing" case that would justify a `WEBFLASH-DAC-002-WRAPPER-PLAN`
slice. The recommended next step is **`WEBFLASH-DAC-LIVE-CHECK-001`** —
a re-run of the live WebFlash readiness / drift check
(`firmware/sources.json`, `manifest.json`,
`scripts/utils/module-availability.js`, `scripts/data/kit-presets.js`,
import grammar; record the `S360-312` classification) once read access
to `sense360store/WebFlash` is restored — which closes the
`NEEDS-TOOLING` axes (and lets the hardware-bench caveats be discharged
by `S360-312-BENCH-*` / operator evidence) before any `WEBFLASH-DAC-001`
wrapper / catalog / build-matrix work is even considered.

**Guardrails honoured.** **No `packages/**`, `products/**`,
`products/webflash/**`, `config/**` (including
`config/webflash-builds.json`, `config/product-catalog.json`,
`config/compile-only-targets.json`, `config/firmware-combination-matrix.json`),
`scripts/**`, `.github/workflows/**`, `components/**`, `include/**`,
`tests/**`, `firmware/**`, `manifest.json`, `firmware/sources.json`,
release-artifact / checksum / build-info, or `sense360store/WebFlash`
edit.** No WebFlash wrapper added; no `webflash_build_matrix` flip; no
`artifact_name`; no `webflash_wrapper`; no `config_string` /
`release_one_required_configs` / `canonical_modules` change; no
`schematic_status` / `schematic_file` promotion (`S360-312` stays
`cataloged_unverified`); no `COMPLIANCE-001` movement; the
`FanDAC ↔ AirIQ` mutex is not relaxed. Release-One stays
`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`; LED preview stays
`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`; FanTRIAC stays `blocked` /
`HW-005`. **No WebFlash import-readiness claim, no WebFlash exposure
claim, no release-readiness claim, no compliance / safety approval
claim, no hardware-stable readiness claim, and no fabricated WebFlash
evidence.**

**2026-05-27 — `DAC-BLOCKER-RECLASSIFY-001` (this PR; docs-only) — note on
WebFlash surface.** The remaining FanDAC gaps are **reclassified by release
scope**, and the reclassification **keeps the WebFlash surface fully
blocked.** It explicitly names **WebFlash live access / `S360-312`
module-availability** (drift #17) and the **WebFlash wrapper / build /
artifact / import** chain as a **WebFlash-exposure blocker only** (they do
**not** gate the FanDAC package / product / `config` layer, which is already
complete with `validated-full-compile` + `voltage_enum_fixed: true`), and it
keeps the **`J3` `out0`/`out1` silkscreen transposition** (product /
installation-documentation and WebFlash / release blocker only), the
**Cloudlift S12 harness + product bench** (Cloudlift product-claim /
WebFlash / release blocker only), and the **voltage-mode UX** (WebFlash /
product UX blocker only) as WebFlash gates. So the FanDAC WebFlash surface
stays **`not-webflash-ready`**: the wrapper, `config/webflash-builds.json`
row, `artifact_name`, release artifact, and import-source gates stay
`BLOCKING`; the live `sense360store/WebFlash` re-verification and the
still-owed `S360-312` module-availability classification stay
`NEEDS-TOOLING`; the `J3` silk transposition and Cloudlift S12 harness /
product-bench caveats stay `NEEDS-OPERATOR-INPUT`. The `DAC-7`
no-simultaneous-per-output-0–5 V / 0–10 V constraint stays correct. The
recommended bench PR is **`S360-312-BENCH-RESULT-001`** (requested via
`S360-312-BENCH-EVIDENCE-REQUEST-001`); **`WEBFLASH-DAC-LIVE-CHECK-001`**
stays blocked behind WebFlash access, and **no `WEBFLASH-DAC-001` wrapper is
recommended** until the Cloudlift S12 bench evidence *and* the WebFlash live
classification are done. Canonical table in
[`hardware/s360-312-r4-fandac.md` §DAC-BLOCKER-RECLASSIFY-001](hardware/s360-312-r4-fandac.md#dac-blocker-reclassify-001--fandac-remaining-blockers-reclassified-by-release-scope-2026-05-27).
No `packages/**`, `products/**`, `products/webflash/**`, `config/**`,
`scripts/**`, `.github/workflows/**`, `components/**`, `include/**`,
`tests/**`, `firmware/**`, `manifest.json`, `firmware/sources.json`,
release-artifact / checksum / build-info, or `sense360store/WebFlash`
edit; no `webflash_build_matrix` flip; no `artifact_name`; no
`schematic_status` promotion (`S360-312` stays `cataloged_unverified`); no
WebFlash exposure / import / release / compliance / hardware-stable /
Cloudlift-ready claim; no fabricated evidence.

**2026-05-27 — `WEBFLASH-LIVE-CHECK-001` (this PR; docs-only live re-check,
no exposure flip).** Re-attempted the live read of `sense360store/WebFlash`
this session via three read-only GitHub methods (repo root,
`scripts/utils/module-availability.js`, and a branch listing) — **all three
returned access denied** (session scope is `sense360store/esphome-public` +
`sense360store/esphome` only). The FanDAC WebFlash axes therefore stay
unchanged: the `WebFlash live repo re-verification` gate stays `NEEDS-TOOLING`
and the `S360-312` `module-availability.js` classification stays **not recorded
in any snapshot** (`WEBFLASH-DRIFT-001` row #17) — it cannot be captured here
without fabricating evidence. The esphome-public side was re-verified fresh
this session and is unchanged (catalog `Ceiling-POE-FanDAC` stays
`hardware-pending` / `webflash_build_matrix: false` / no `artifact_name`; no
FanDAC wrapper under [`products/webflash/`](../products/webflash/); the
`fandac_conflicts_with_airiq: true` mutex is unchanged). Full record in
[`webflash-drift-audit.md` §4.4](webflash-drift-audit.md#44-follow-up-resolution-log-updated-2026-05-27-by-webflash-live-check-001).
The recommended next DAC live step stays `WEBFLASH-DAC-LIVE-CHECK-001` (or this
consolidated re-run) once read access is restored, with the Cloudlift S12
bench as the substantive evidence gate. No `packages/**`, `products/**`,
`products/webflash/**`, `config/**`, `scripts/**`, `.github/workflows/**`,
`components/**`, `include/**`, `tests/**`, `firmware/**`, `manifest.json`,
`firmware/sources.json`, release-artifact / checksum / build-info, or
`sense360store/WebFlash` edit; no `webflash_build_matrix` flip; no
`artifact_name`; no `schematic_status` promotion; no WebFlash exposure /
import / release / compliance / hardware-stable / Cloudlift-ready claim; no
fabricated evidence.

## TRIAC / S360-320 WebFlash posture

**Current state.** `S360-320 Sense360 TRIAC`,
`schematic_status: cataloged_unverified` (module-side schematic PDF
committed at
[`docs/hardware/schematics/S360-320-R4.pdf`](hardware/schematics/S360-320-R4.pdf)
under HW-ASSETS-003).
[`s360-320-r4-triac.md`](hardware/s360-320-r4-triac.md) status
`partial — schematic evidence available; package reconciliation,
timing validation, and compliance/certification pending`.
`packages/expansions/fan_triac.yaml` carries
`needs-package-reconciliation` + `timing/compliance-pending` +
`blocked-from-standard-exposure`. ESPHome `ac_dimmer` requires direct
interrupt-capable ESP32 GPIOs; the Core currently routes
`TRI_GPIO1` / `TRI_GPIO2` via the SX1509 expander, which the timing
analysis rejects. HW-005 remains unresolved. COMPLIANCE-001
(mains-voltage UK / EU) is in force. The catalog entry
`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` is `status: blocked`,
`blocker: HW-005`, `webflash_build_matrix: false`, with `notes`
edited by `PRODUCT-TRIAC-001` to record the advanced /
manual-warning candidate posture (notes-only; structural fields
unchanged; no new lifecycle enum). The WebFlash wrapper
[`products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml)
is retained as a blocked reference but is not in the build matrix
and has no release artifact / WebFlash import.

**Allowed WebFlash action now.** `not-webflash-ready`. The blocked
reference wrapper stays exactly as it is. No promotion of the
catalog entry off `blocked`. No flip of `webflash_build_matrix` to
`true`. No build-matrix entry. No release artifact. No WebFlash
import. **No promotion of FanTRIAC to `production` / `preview` /
`compile-only` / `hardware-pending` / `legacy-compatible` at any
layer.**

**WebFlash runtime UX `WF-TRIAC-001` landed; in-repo wrapper /
catalog / build slice still blocked.** The `WF-TRIAC-001`
runtime slice has **landed in the
[`sense360store/WebFlash`](https://github.com/sense360store/WebFlash)
repo** as a runtime advanced / manual-warning UX gate: FanTRIAC
is visible / selectable in the WebFlash custom path with
explicit acknowledgement and install blocking. **The runtime UX
gate is the only `WF-TRIAC-001` work that has landed.** The
in-repo `WF-TRIAC-001` wrapper / catalog / build-matrix slice —
a WebFlash wrapper under
[`products/webflash/`](../products/webflash/), a catalog edit on
[`config/product-catalog.json`](../config/product-catalog.json)
flipping `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` off `blocked` and
flipping `webflash_build_matrix` to `true`, and a build-matrix
row in
[`config/webflash-builds.json`](../config/webflash-builds.json)
— **remains blocked** until `PRODUCT-TRIAC-002` (currently
deferred) and `PACKAGE-TRIAC-001` (currently deferred) clear,
which themselves require `HW-005`, `HW-PINMAP-320-FOLLOWUP`,
bench / waveform / real-load evidence, and `COMPLIANCE-001`
advanced / manual-warning sign-off. No wrapper, no catalog
flip, no build-matrix entry, no `webflash_build_matrix: true`
flip, no firmware import. See
[`docs/cleanup-audit.md` §TRIAC-QUEUE-001 update](cleanup-audit.md#triac-queue-001-update-remaining-fantriac-chain-normalized-after-package-deferral).

**Future exposure class (policy-recorded by `PRODUCT-TRIAC-001`).**
`advanced/manual-warning-only` **only**. Reachable through WebFlash
exclusively behind an explicit advanced-flow / manual-warning UX
gate. **Never** on the standard WebFlash flasher landing list.
**Never** in `release_one_required_configs`. **Never** kit /
default / recommended. **Never** Release-One. **Not**
compliance-certified — the advanced / manual-warning posture is an
exposure class, not a certification claim; the COMPLIANCE-001
mains-voltage UK / EU sign-off runs in addition.

The reach to a live `advanced/manual-warning-only` WebFlash surface
requires, in order: `PRODUCT-TRIAC-001` (**landed**: notes-only
catalog policy reclassification on `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`
recording the advanced / manual-warning candidate posture; JSON
`status: blocked` / `blocker: HW-005` / `webflash_build_matrix: false`
unchanged; no new lifecycle enum) → `HW-005` unblock (S360-320
schematic-side electrical / firmware-side timing reconciliation; per
[`docs/release-one-hardware-audit.md` §FanTRIAC mapping resolution](release-one-hardware-audit.md#fantriac-mapping-resolution)) →
`HW-PINMAP-320-FOLLOWUP` (standalone schematic-backed reference doc;
J3 ↔ J15 reconciliation; `TRI_GPIO*` / `ESP_GPIO*` naming;
`ac_dimmer` ISR timing budget recomputation) → `PACKAGE-TRIAC-001`
(FanTRIAC package YAML reconciliation; timing-correctness verdict) →
`PRODUCT-TRIAC-002` (FanTRIAC product YAML / catalog-entry rework;
decide canonical FanTRIAC config-string shape; preserve all
mains-voltage warnings) → `COMPLIANCE-001` advanced /
manual-warning sign-off (UK / EU mains-voltage compliance evidence;
qualified-electrician acknowledgement; document approval) →
`WF-TRIAC-001` (advanced / manual-warning WebFlash wrapper / catalog
/ build-matrix entry, behind the manual-warning UX gate; separate
from the standard `WEBFLASH-*-001` flow because of the advanced /
manual-warning posture) → `RELEASE-TRIAC-001` (signed artifact) →
`WF-IMPORT-TRIAC-001` (WebFlash-side import behind manual-warning
UX).

**REQUIRED_CONFIGS posture.** `not-required-configs` — **never by
default**, irrespective of any future product YAML existence,
catalog status, or WebFlash surface. Any future addition to
`release_one_required_configs` would be a separately scoped PR with
explicit COMPLIANCE-001 sign-off and is **not** authorised by this
matrix.

**Kit / recommended posture.** `not-recommended` + `not-kit-default`
— **never by default**. Mains-voltage advanced / manual-warning
products are categorically excluded from kit / default / recommended
surfaces, irrespective of any future product YAML existence,
catalog status, or WebFlash surface.

**Cross-references.**
[`hardware/s360-320-r4-triac.md`](hardware/s360-320-r4-triac.md),
[`hardware/s360-320-r4-triac.md` Advanced / manual-warning product posture](hardware/s360-320-r4-triac.md#advanced--manual-warning-product-posture),
[`hardware/board-readiness-matrix.md` §S360-320](hardware/board-readiness-matrix.md#s360-320-sense360-triac),
[`hardware/package-readiness-matrix.md` §fan_triac.yaml](hardware/package-readiness-matrix.md#fan_triacyaml--s360-320),
[`product-readiness-matrix.md` §FanTRIAC / S360-320](product-readiness-matrix.md#fantriac--s360-320),
[`release-one-hardware-audit.md` §FanTRIAC mapping resolution](release-one-hardware-audit.md#fantriac-mapping-resolution),
[`compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md).

## Power / S360-400 WebFlash posture

**Current state.** `S360-400 Sense360 240v PSU`,
`schematic_status: cataloged_unverified`, no `schematic_file`.
**Module-side schematic PDF committed under HW-ASSETS-400 (PR #514)**
at
[`docs/hardware/schematics/S360-400-R4.pdf`](hardware/schematics/S360-400-R4.pdf)
with curated artifact index at
[`docs/hardware/artifacts/S360-400-R4.md`](hardware/artifacts/S360-400-R4.md).
**HW-PINMAP-400-FOLLOWUP consumed both** and promoted
[`s360-400-r4-power.md`](hardware/s360-400-r4-power.md) from
`pending — schematic/design evidence required` to
`partial — schematic evidence available; package reconciliation,
BOM, silkscreen, creepage/clearance, and COMPLIANCE-001 pending`;
the standalone schematic-backed reference-doc rewrite (in the
per-board `s360-XXX-r4-<role>.md` reference pattern) is still
owed to a later evidence-bearing PR.
`packages/hardware/power_240v.yaml` carries
`schematic-evidence-pending` + `timing/compliance-pending`
(class unchanged by HW-PINMAP-400-FOLLOWUP). The three-way AC/DC
part-identity disagreement (catalog `HLK-5M05` vs package header
`HLK-PM01 or similar` vs schematic `HLK-10M05`) is recorded but
**unresolved** by this PR — BOM-bound, owed to
`PACKAGE-POWER-400-001`. COMPLIANCE-001 (mains-voltage UK / EU) is
in force (last re-check PR #506). The four `legacy-compatible`
`*-pwr` Core variants
([`sense360-core-c-pwr.yaml`](../products/sense360-core-c-pwr.yaml),
[`sense360-core-v-c-pwr.yaml`](../products/sense360-core-v-c-pwr.yaml),
[`sense360-core-v-w-pwr.yaml`](../products/sense360-core-v-w-pwr.yaml),
[`sense360-core-w-pwr.yaml`](../products/sense360-core-w-pwr.yaml))
exist as manual / pre-WebFlash YAMLs only and are not
WebFlash-shippable. No WebFlash wrapper / catalog entry /
build-matrix entry / release artifact / WebFlash import exists for
any PWR-240V product.

**Allowed WebFlash action now.** `not-webflash-ready`. No wrapper,
no catalog entry, no build-matrix entry, no release artifact, no
WebFlash import. The four `legacy-compatible` `*-pwr` Core entries
stay `legacy-compatible` and stay out of the WebFlash build matrix.

**Future exposure class (intent).** `preview-candidate` as a standard
exposure (the advanced / manual-warning posture is **not** the
default for PWR-240V; the per-family `PRODUCT-POWER-400-001` slice
decides whether mains-voltage PWR-240V products are standard
preview-candidate, advanced / manual-warning-only, or both
depending on intended UX). Reach requires: `HW-ASSETS-400`
*(landed at PR #514; module-side schematic PDF + curated artifact
index committed)* → `HW-PINMAP-400-FOLLOWUP` *(this PR;
docs-only schematic-backed reconciliation; audit promoted to
`partial`)* → BOM cross-check + silkscreen + creepage / clearance
+ bench / load / thermal / EMI evidence (separate evidence-bearing
slices) → `S360-400` `schematic_status: verified` JSON PR →
`PACKAGE-POWER-400-001` (PWR-240V package YAML reconciliation) →
`COMPLIANCE-001` S360-400 slice closure (mains-voltage UK / EU
sign-off) → `PRODUCT-POWER-400-001` (canonical product YAML;
preserve the four `legacy-compatible` `*-pwr` Core variants) →
`WEBFLASH-POWER-400-001` (wrapper + catalog + build-matrix; UX
class — standard preview-candidate vs advanced / manual-warning —
decided per the product slice's compliance verdict) →
`RELEASE-GAP-001` → `WF-IMPORT-GAP-001`.

**REQUIRED_CONFIGS posture.** `not-required-configs` by default.

**Kit / recommended posture.** `not-recommended` + `not-kit-default`.
Mains-voltage compliance posture is gating-priority over exposure
decisions; kit / recommended membership decision belongs to
`PRODUCT-POWER-400-001`.

**Cross-references.**
[`hardware/s360-400-r4-power.md`](hardware/s360-400-r4-power.md),
[`hardware/board-readiness-matrix.md` §S360-400](hardware/board-readiness-matrix.md#s360-400-sense360-240v-psu),
[`hardware/package-readiness-matrix.md` §power_240v.yaml](hardware/package-readiness-matrix.md#power_240vyaml--s360-400),
[`product-readiness-matrix.md` §PWR-240V / S360-400](product-readiness-matrix.md#pwr-240v--s360-400),
[`compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md).

**2026-05-19 — `PRODUCT-POWER-400-001` investigation pass
(Path A docs-only deferral; class unchanged).**
The upstream `PACKAGE-POWER-400-001` investigation pass merged as
**PR #520** on 2026-05-19 (docs-only Path A deferral) and the
downstream `PRODUCT-POWER-400-001` investigation pass ran on
2026-05-19 (this PR — docs-only Path A deferral). Re-verified
against the live files: no S360-400-explicit / `PWR`-bearing
WebFlash-shippable product YAML exists under
[`../products/`](../products/) or
[`../products/webflash/`](../products/webflash/); no S360-400
product entry in
[`../config/product-catalog.json`](../config/product-catalog.json)
(four `legacy-compatible` `*-pwr` Core variants unchanged); no
`PWR` build in
[`../config/webflash-builds.json`](../config/webflash-builds.json);
[`../config/webflash-compatibility.json`](../config/webflash-compatibility.json)
`PWR` stays reserved in `canonical_power` with no
`webflash_build_matrix: true` consumer. `WEBFLASH-POWER-400-001`
stays **blocked** behind `PRODUCT-POWER-400-001` and
`COMPLIANCE-001` `S360-400` slice closure; `PRODUCT-POWER-400-001`
itself stays blocked behind `PACKAGE-POWER-400-001`
implementation (PR #520 was docs-only investigation only), BOM
cross-check, `S360-400` `schematic_status: verified` JSON PR,
`COMPLIANCE-001` `S360-400` slice, package / catalog
reconciliation, and product-onboarding approval. No package,
product, WebFlash, build, release, compliance, JSON catalog,
test, script, workflow, component, include, firmware, or
manifest edits; no `schematic_status` / `schematic_file`
promotion; no `webflash_build_matrix` flip; no `REQUIRED_CONFIGS`
/ kit change. Release-One stays `Ceiling-POE-VentIQ-RoomIQ` /
`stable` / `v1.0.0`; LED preview stays
`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`; FanTRIAC stays
`blocked` / `HW-005`. Investigation outcome cross-recorded at
[`cleanup-audit.md` §`PRODUCT-POWER-400-001 update (2026-05-19 — docs-only investigation pass)`](cleanup-audit.md#product-power-400-001-update-2026-05-19--docs-only-investigation-pass)
and [`product-readiness-matrix.md` §PWR-240V / S360-400](product-readiness-matrix.md#pwr-240v--s360-400).

**2026-05-19 — `WEBFLASH-POWER-400-001` investigation pass
(Path A docs-only deferral; class unchanged).**
The downstream `WEBFLASH-POWER-400-001` investigation pass merged
as **PR #522** on 2026-05-19 (docs-only Path A deferral). The
upstream `PRODUCT-POWER-400-001` investigation pass merged
earlier the same day as **PR #521** (docs-only Path A deferral)
and is recorded above. Re-verified against the live files: no
S360-400 WebFlash wrapper exists under
[`../products/webflash/`](../products/webflash/) (three PoE
wrappers only —
[`ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml),
[`ceiling-poe-ventiq-roomiq-led.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq-led.yaml),
[`ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml));
[`../config/webflash-builds.json`](../config/webflash-builds.json)
has no PWR build (only `Ceiling-POE-VentIQ-RoomIQ` stable +
`Ceiling-POE-VentIQ-RoomIQ-LED` preview);
[`../config/webflash-compatibility.json`](../config/webflash-compatibility.json)
reserves `PWR` in `canonical_power: ["USB", "POE", "PWR"]` with
no `webflash_build_matrix: true` consumer;
`release_one_required_configs` stays
`["Ceiling-POE-VentIQ-RoomIQ"]`;
[`../config/product-catalog.json`](../config/product-catalog.json)
has no S360-400-specific product (four `legacy-compatible`
`*-pwr` Core variants unchanged: `sense360-core-c-pwr`,
`sense360-core-w-pwr`, `sense360-core-v-c-pwr`,
`sense360-core-v-w-pwr` — each `status: legacy-compatible` /
`webflash_build_matrix: false` / no `config_string` / no
`webflash_wrapper` / no `artifact_name`);
[`../config/hardware-catalog.json`](../config/hardware-catalog.json)
`S360-400` row stays `schematic_status: cataloged_unverified`
with no `schematic_file`;
[`../tests/test_hardware_catalog.py:53`](../tests/test_hardware_catalog.py)
`EXPECTED_STILL_UNVERIFIED_SKUS = frozenset({"S360-320",
"S360-400"})` actively enforces this state. UX class (standard
preview-candidate vs advanced / manual-warning) stays undecided
— owed to the per-family `PRODUCT-POWER-400-001` compliance
verdict; `PRODUCT-POWER-400-001` is deferred (PR #521) and the
compliance verdict has not been rendered, so
`WEBFLASH-POWER-400-001` cannot set the UX class either.
`RELEASE-POWER-400-001` stays **blocked** behind
`WEBFLASH-POWER-400-001` and `COMPLIANCE-001` `S360-400` slice
closure; `WEBFLASH-POWER-400-001` itself stays blocked on
`PRODUCT-POWER-400-001` implementation (PR #521 was docs-only
investigation only), `PACKAGE-POWER-400-001` implementation
(PR #520 was docs-only investigation only), BOM cross-check,
the `S360-400` `schematic_status: verified` JSON PR, the
`COMPLIANCE-001` `S360-400` slice, and the UX-class decision.
No package, product, WebFlash, build, release, compliance, JSON
catalog, test, script, workflow, component, include, firmware,
or manifest edits; no `schematic_status` / `schematic_file`
promotion; no `webflash_build_matrix` flip; no
`REQUIRED_CONFIGS` / kit change. Release-One stays
`Ceiling-POE-VentIQ-RoomIQ` / `stable` / `v1.0.0`; LED preview
stays `Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`; FanTRIAC
stays `blocked` / `HW-005`. Investigation outcome
cross-recorded at
The upstream `PRODUCT-POWER-400-001` investigation pass merged
as **PR #521** on 2026-05-19 (docs-only Path A deferral) and the
downstream `WEBFLASH-POWER-400-001` investigation pass ran on
2026-05-19 (this PR — docs-only Path A deferral). Re-verified
against the live files: no S360-400-explicit / `PWR`-bearing
WebFlash wrapper exists under
[`../products/webflash/`](../products/webflash/) (the directory
contains only three POE wrappers
[`ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml),
[`ceiling-poe-ventiq-roomiq-led.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq-led.yaml),
and
[`ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml));
[`../config/webflash-builds.json`](../config/webflash-builds.json)
has no `PWR` build (only Release-One
`Ceiling-POE-VentIQ-RoomIQ` `stable` and
`Ceiling-POE-VentIQ-RoomIQ-LED` `preview`);
[`../config/product-catalog.json`](../config/product-catalog.json)
has no S360-400-specific product (the four `legacy-compatible`
`*-pwr` Core variants stay `legacy-compatible` /
`webflash_build_matrix: false` / no `config_string` / no
`webflash_wrapper` / no `artifact_name`, and are **not**
WebFlash exposure evidence);
[`../config/webflash-compatibility.json`](../config/webflash-compatibility.json)
reserves `PWR` in `canonical_power: ["USB", "POE", "PWR"]` but
no `webflash_build_matrix: true` row consumes it — reservation
is grammar-only and does **not** imply WebFlash exposure;
[`../config/hardware-catalog.json`](../config/hardware-catalog.json)
`S360-400` row stays `schematic_status: cataloged_unverified`
with no `schematic_file`. `WEBFLASH-POWER-400-001` stays
**blocked** behind `PRODUCT-POWER-400-001` implementation (PR
#521 was docs-only investigation only), `PACKAGE-POWER-400-001`
implementation (PR #520 docs-only), BOM cross-check, the
`S360-400` `schematic_status: verified` JSON PR, the
`COMPLIANCE-001` `S360-400` slice, package / catalog
reconciliation, product-onboarding approval, and release /
build / artifact readiness; `RELEASE-POWER-400-001` /
`WF-IMPORT-POWER-400-001` stay blocked behind it. Path B
(documentation-only cleanup) is unhelpful because this section
and the matching sections of
[`release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
and [`product-readiness-matrix.md`](product-readiness-matrix.md)
already correctly classify the slice as `not-webflash-ready` /
`not-release-ready` / `no product YAML` / `no wrapper` /
`no build-matrix row`. Path C (implementation) is unsafe
because every gate is open: adding a wrapper while no
S360-400 product YAML exists would have nothing to wrap;
flipping `webflash_build_matrix: true` while the catalog has
no S360-400-specific entry would have nothing to flip; adding
a build-matrix row would emit a mains-voltage artifact while
`packages/hardware/power_240v.yaml` is
`schematic-evidence-pending` + `needs-package-reconciliation`
+ `timing/compliance-pending` and `COMPLIANCE-001` `S360-400`
is open. No package, product, WebFlash, build, release,
compliance, JSON catalog, test, script, workflow, component,
include, firmware, or manifest edits; no `schematic_status` /
`schematic_file` promotion; no `webflash_build_matrix` flip;
no `artifact_name` added; no `REQUIRED_CONFIGS` / kit change.
Release-One stays `Ceiling-POE-VentIQ-RoomIQ` / `stable` /
`v1.0.0`; LED preview stays
`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`; FanTRIAC stays
`blocked` / `HW-005`. Investigation outcome cross-recorded at
[`cleanup-audit.md` §`WEBFLASH-POWER-400-001 update (2026-05-19 — docs-only investigation pass)`](cleanup-audit.md#webflash-power-400-001-update-2026-05-19--docs-only-investigation-pass)
and
[`release-artifact-readiness-matrix.md` §Power / S360-400 release posture](release-artifact-readiness-matrix.md#power--s360-400-release-posture).

**2026-05-20 — `PACKAGE-POWER-400-001` package-header cleanup
(Path B / limited implementation).** Following the
`HW-BOM-ASSETS-002` / PR #535 BOM-confirmation of
`PS1 = HLK-5M05` (HI-LINK), the comment-only header cleanup of
[`packages/hardware/power_240v.yaml`](../packages/hardware/power_240v.yaml)
that PR #515 and PR #520 deferred has now landed under Path B:
the disproved `HLK-PM01 or similar` claim is removed, the
BOM-confirmed part identity (`PS1 = HLK-5M05 (HI-LINK)`) and
BOM-confirmed populated protection / connector components
(`F1 A250-1200`, `RV1 10D391K`, `C1 470nF`, `J1` WAGO 2601-3103,
`J2` JST SH `SM02B-SRSS-TB(LF)(SN)`) are now named in the header,
input / output / isolation / protection ratings are reclassified
as vendor-datasheet typicals (not BOM-confirmed and not
compliance evidence), the misleading `1A recommended` AC-input
fusing line is removed, and the header restates that
mains-voltage UK / EU compliance is tracked by COMPLIANCE-001
and remains OPEN. Runtime YAML behavior is unchanged
(substitutions / globals / sensors / binary_sensor / logger
blocks preserved byte-for-byte). `WEBFLASH-POWER-400-001`
posture is unchanged — the WebFlash slice **stays blocked**
(`not-webflash-ready`) on `PRODUCT-POWER-400-001` implementation,
on COMPLIANCE-001 `S360-400` slice closure, and on the UX-class
decision (standard preview-candidate vs advanced /
manual-warning); the residual coordinated `PACKAGE-POWER-400-001`
work (the `S360-400` `schematic_status: verified` JSON-only PR,
additionally gated on the schematic-side correction of the
committed PDF's `PS1 = HLK-10M05` value-field string) is still
owed. No WebFlash wrapper added; no `webflash_build_matrix: true`
flip; no `artifact_name`; no `webflash_wrapper`; no
`config_string`; no `release_one_required_configs` /
`lifecycle_statuses` / `canonical_modules` / `canonical_power` /
`forbidden_tokens` / kit / `REQUIRED_CONFIGS` change.
Release-One stays `Ceiling-POE-VentIQ-RoomIQ` / `stable` /
`v1.0.0`; LED preview stays
`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`; FanTRIAC stays
`blocked` / `HW-005`. Outcome cross-recorded at
[`docs/hardware/s360-400-r4-power.md` §2026-05-20 — PACKAGE-POWER-400-001 package-header cleanup](hardware/s360-400-r4-power.md#2026-05-20--package-power-400-001-package-header-cleanup-bom-confirmed-part-identity-in-header-ratings-softened-downstream-slices-still-blocked),
[`docs/hardware/package-readiness-matrix.md` `power_240v.yaml` / S360-400](hardware/package-readiness-matrix.md#power_240vyaml--s360-400),
[`docs/cleanup-audit.md` §`PACKAGE-POWER-400-001 update (2026-05-20 — Path B package-header cleanup)`](cleanup-audit.md#package-power-400-001-update-2026-05-20--path-b-package-header-cleanup),
and
[`release-artifact-readiness-matrix.md` §Power / S360-400 release posture](release-artifact-readiness-matrix.md#power--s360-400-release-posture).

## PoE / S360-410 WebFlash posture

**Current state.** `S360-410 Sense360 PoE PSU`,
`schematic_status: cataloged_unverified` (unchanged by HW-ASSETS-410
or HW-PINMAP-410-FOLLOWUP), no `schematic_file`. Module-side
schematic now **committed under HW-ASSETS-410 / PR #516** at
[`docs/hardware/schematics/S360-410-R4.pdf`](hardware/schematics/S360-410-R4.pdf)
with curated artifact index at
[`docs/hardware/artifacts/S360-410-R4.md`](hardware/artifacts/S360-410-R4.md);
[`s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md) audit doc
**promoted by HW-PINMAP-410-FOLLOWUP** to `partial — schematic
evidence available; package reconciliation, PoE PD controller /
magnetics / buck / isolated DC/DC / harness identity evidence
pending`. Standalone schematic-backed reference-doc rewrite still
owed.
`packages/hardware/power_poe.yaml` stays `reference-only` +
`schematic-evidence-pending` (schematic consumed; package-header
reconciliation still owed to `PACKAGE-POE-410-001` after BOM
lands) + `do-not-change-release-one`. The Release-One product
`Ceiling-POE-VentIQ-RoomIQ` and the LED preview
`Ceiling-POE-VentIQ-RoomIQ-LED` both consume S360-410 logically
under the existing schematic-pending caveat preserved in
[`release-one-hardware-audit.md` Findings → PoE PSU](release-one-hardware-audit.md#findings).
No **new** PoE-410 product YAML exists; no new WebFlash wrapper /
catalog entry / build-matrix entry / release artifact / WebFlash
import is created for PoE-410 specifically by this matrix.

**2026-06 evidence narrowing (HW-S360-410-EVIDENCE-2026-06).** WebFlash
posture unchanged — `not-webflash-ready` for any new PoE-410 entry; no new
wrapper / catalog / build-matrix / artifact. Narrowed: the `J3` connector
pin-1 polarity (E9, render basis), the J2-harness spec (E10), and the
gerber set (E13) are now **on file**, and the PoE bench (E11) is **partial**
(link-up + 5 V confirmed; load / cold-start inrush / thermal / EMI-EMC not
measured). On the E9 + E10 basis the Release-One PoE `"schematic
verification pending"` caveat (E15) is **closed** (flagship documentation
closure; no `verified` claim; `S360-410` stays `cataloged_unverified`, no
`schematic_file`). The E11 bench remainder and E12 isolation stay missing,
so no new PoE-410 WebFlash exposure is unblocked.

**2026-06-08 owner waiver (HW-S360-410-WAIVER-2026-06).** The owner decided to
release S360-410 **without** completing the remaining E11 bench (load regulation
/ cold-start inrush / thermal rise / EMI-EMC) and E12 isolation (Hi-pot /
insulation resistance / leakage / earth continuity) evidence, and **accepted the
risk**. Those measurements were **NOT measured, NOT tested, and NOT passed** —
this is a **risk-acceptance waiver, not verification**: `S360-410` stays
`cataloged_unverified` (no `schematic_status` flip, no `schematic_file`; the
catalog records the waiver in a new `release_disposition` field only) and **no
`verified` claim is made**. The waiver lifts the S360-410 hardware-verification
**block**, so the dependent PoE room bundles (`S360-KIT-BEDROOM-P`,
`S360-KIT-KITCHEN-P`, `S360-KIT-LIVING-P`, `S360-KIT-CORRIDOR-P`) **no longer
block on the S360-410 hardware-verification basis**. It lifts the hardware block
**only** and changes **no** WebFlash surface: it adds no new PoE-410 WebFlash
wrapper / catalog / build-matrix entry, flips no `config/webflash-builds.json`
channel, and leaves the existing Release-One stable and LED preview WebFlash
surfaces byte-identical. Any WebFlash exposure / productization remains a
separate, explicit step. Full record:
[`docs/package-poe-410-evidence-result.md` §0.1](package-poe-410-evidence-result.md).

**Allowed WebFlash action now.** `not-webflash-ready` for any
**new** PoE-410 product entry. The existing Release-One and LED
preview WebFlash surface that consumes S360-410 is **not**
affected: Release-One wrapper / catalog `status: production` /
`channel: stable` / `webflash_build_matrix: true` / artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` /
tag `v1.0.0` stay verbatim. LED preview wrapper / catalog
`status: preview` / `channel: preview` /
`webflash_build_matrix: true` / artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` stay
verbatim.

**Future exposure class (intent).** `preview-candidate` as a
standard exposure **only if** a new PoE-410 product entry is
warranted. Per
[`product-readiness-matrix.md` §PoE-410 / S360-410](product-readiness-matrix.md#poe-410--s360-410),
the per-family `PRODUCT-POE-410-001` slice "often will close by
promoting Release-One's preserved schematic-pending caveat alone,
without adding a new product entry." If `PRODUCT-POE-410-001`
decides no new product entry is added, then `WEBFLASH-POE-410-001`
is not required, and the family closes at the existing Release-One
caveat without a new exposure class. The reach to a new
`preview-candidate` exposure, if `PRODUCT-POE-410-001` decides one
is warranted, requires: `HW-ASSETS-410` (supplier delivery of
module-side schematic PDF + curated artifact index — landed as PR
#516) → `HW-PINMAP-410-FOLLOWUP` (schematic-backed partial audit —
this PR; standalone schematic-backed reference-doc rewrite still
owed) → BOM cross-check → `HW-002 OQ#6` J2 harness identity
closure / `S360-100-BENCH-001` update → `S360-410`
`schematic_status: verified` JSON PR → `PACKAGE-POE-410-001`
(PoE-410 package YAML reconciliation) → `PRODUCT-POE-410-001`
(canonical product YAML, **if warranted**) → `WEBFLASH-POE-410-001`
(wrapper + catalog + build-matrix, **if a new product entry is
added**) → `RELEASE-GAP-001` → `WF-IMPORT-GAP-001`.

**REQUIRED_CONFIGS posture.** Release-One's existing
`release_one_required_configs: ["Ceiling-POE-VentIQ-RoomIQ"]`
membership is not touched. Any new PoE-410 product entry is
`not-required-configs` by default.

**Kit / recommended posture.** Release-One's existing kit /
recommended membership is not touched. Any new PoE-410 product
entry is `not-recommended` + `not-kit-default` by default; the
membership decision belongs to `PRODUCT-POE-410-001`.

**Cross-references.**
[`hardware/s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md),
[`hardware/board-readiness-matrix.md` §S360-410](hardware/board-readiness-matrix.md#s360-410-sense360-poe-psu),
[`hardware/package-readiness-matrix.md` §power_poe.yaml](hardware/package-readiness-matrix.md#power_poeyaml--s360-410),
[`product-readiness-matrix.md` §PoE-410 / S360-410](product-readiness-matrix.md#poe-410--s360-410),
[`release-one-hardware-audit.md` §Findings → PoE PSU](release-one-hardware-audit.md#findings).

**2026-05-29 — `PACKAGE-POE-410-EVIDENCE-RESULT-001` evidence
reconciliation (no WebFlash change).** The S360-410 evidence was
reconciled into a single evidence-result record at
[`docs/package-poe-410-evidence-result.md`](package-poe-410-evidence-result.md).
**No WebFlash surface change:** no PoE-410-subject WebFlash wrapper /
build / catalog row is added, no `webflash_build_matrix` value is
flipped, and the existing Release-One (`Ceiling-POE-VentIQ-RoomIQ`)
and LED-preview (`Ceiling-POE-VentIQ-RoomIQ-LED`) wrappers — both of
which consume `S360-410` logically under Release-One identity — stay
byte-identical. The reconciliation confirms the bench, isolation /
safety, connector-silkscreen, J2-harness, and PCB-source evidence
classes are **still missing**, so `S360-410` stays
`cataloged_unverified` and any new PoE-410 product entry stays
`not-webflash-ready`. The PoE room bundles remain gated per
[`docs/package-poe-410-evidence-result.md` §3](package-poe-410-evidence-result.md#3-stable-bundle-impact-assessment).

**2026-05-20 — `PRODUCT-POE-410-001` investigation pass
(Path A docs-only deferral).** Re-verified against the live
files: no S360-410-explicit / `POE`-410-subject
WebFlash-shippable product YAML exists under
[`products/`](../products/) or
[`products/webflash/`](../products/webflash/) (the three
existing PoE wrappers
[`ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml),
[`ceiling-poe-ventiq-roomiq-led.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq-led.yaml),
and
[`ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml)
are Release-One / LED-preview / FanTRIAC-blocked wrappers,
**not** S360-410-subject WebFlash exposure). The three
shipping PoE entries in
[`config/product-catalog.json`](../config/product-catalog.json)
each carry `hardware.poe: "S360-410"` as a catalog-level
mapping field only — Release-One identity, not
S360-410-subject WebFlash exposure;
[`config/webflash-builds.json`](../config/webflash-builds.json)
has only the Release-One `stable` build and the LED
`preview` build (no new PoE-410-explicit build);
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
reserves `POE` in `canonical_power` consumed by both
committed builds (POE reservation does **not** imply
S360-410-subject WebFlash exposure);
`release_one_required_configs` stays
`["Ceiling-POE-VentIQ-RoomIQ"]`;
[`config/hardware-catalog.json`](../config/hardware-catalog.json)
`S360-410` row stays byte-identical
(`schematic_status: cataloged_unverified`, no
`schematic_file`);
[`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml)
stays byte-identical to PR #517 / PR #526 state. The
2026-05-20 `PRODUCT-POE-410-001` investigation pass is
**confirmed deferred** — the eight preconditions recorded
under
[`product-readiness-matrix.md` §PoE-410 / S360-410](product-readiness-matrix.md#poe-410--s360-410)
(`PACKAGE-POE-410-001` implementation slice; BOM cross-check;
`S360-410` `schematic_status: verified` JSON PR; HW-002 OQ#6
/ `S360-100-BENCH-001` J2-harness closure; package-header
reconciliation; Release-One PoE caveat closure;
product-onboarding approval; no-new-entry vs new-entry
product-catalog readiness decision) all remain open.
`WEBFLASH-POE-410-001` therefore stays blocked behind
`PRODUCT-POE-410-001` implementation (which itself stays
blocked behind `PACKAGE-POE-410-001` implementation and the
Release-One PoE caveat-closure PR); `RELEASE-POE-410-001` /
`WF-IMPORT-POE-410-001` (cross-repo) stay blocked behind
`WEBFLASH-POE-410-001`. The existing Release-One and LED
preview WebFlash surface that consumes S360-410 is **not**
affected: Release-One wrapper / catalog `status: production`
/ `channel: stable` / `webflash_build_matrix: true` /
artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` /
tag `v1.0.0` stay verbatim; LED preview wrapper / catalog
`status: preview` / `channel: preview` /
`webflash_build_matrix: true` / artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`
stay verbatim. The Release-One PoE "schematic verification
pending" caveat in
[`release-one-hardware-audit.md` Findings → PoE PSU](release-one-hardware-audit.md#findings)
is **preserved verbatim** by this re-check. Path B
(documentation / catalog-classification-note-only cleanup)
was rejected because this section already correctly
classifies the slice as `not-webflash-ready` for any new
PoE-410 product entry, with the existing Release-One
exposure unaffected; Path C (implementation) was unsafe
because every upstream gate is open and adding a wrapper
without a canonical S360-410 / `POE`-410-subject product
YAML to wrap would break the
[Core rule](#core-rule). The next
`WEBFLASH-POE-410-001` PR (if and only if
`PRODUCT-POE-410-001` adds a new PoE-410-explicit product
entry) must land **the WebFlash wrapper + the catalog
`webflash_build_matrix: true` flip + the build-matrix row
+ the UX-class decision as a single atomic slice**, not as
a documentation cleanup alone, and only after
`PRODUCT-POE-410-001` implementation and the Release-One
PoE caveat-closure PR both land. Per the
[Follow-up PR sequence](#follow-up-pr-sequence) row, "often
this slice is not required because `PRODUCT-POE-410-001`
closes by extending the Release-One caveat without adding a
new product." See
[`docs/cleanup-audit.md` §`PRODUCT-POE-410-001 update (2026-05-20 — docs-only investigation pass)`](cleanup-audit.md#product-poe-410-001-update-2026-05-20--docs-only-investigation-pass).

**2026-05-20 — `WEBFLASH-POE-410-001` investigation pass
(Path A docs-only deferral).** Re-verified against the live
WebFlash exposure surface: **no S360-410 WebFlash wrapper
exists** under [`products/webflash/`](../products/webflash/) —
only three PoE wrappers
[`ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml),
[`ceiling-poe-ventiq-roomiq-led.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq-led.yaml),
and
[`ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml),
all of which are Release-One / LED-preview / FanTRIAC-blocked
wrappers under Release-One identity (not S360-410-subject
WebFlash exposure);
[`config/webflash-builds.json`](../config/webflash-builds.json)
has **no S360-410-explicit build** (only Release-One
`Ceiling-POE-VentIQ-RoomIQ` `stable` and
`Ceiling-POE-VentIQ-RoomIQ-LED` `preview`, both consuming
S360-410 logically under the preserved schematic-pending
caveat);
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
reserves `POE` in `canonical_power` consumed by both
committed builds (POE reservation does **not** imply
S360-410-subject WebFlash exposure);
`release_one_required_configs` stays
`["Ceiling-POE-VentIQ-RoomIQ"]`;
[`config/product-catalog.json`](../config/product-catalog.json)
has **no S360-410-explicit product** (the three shipping PoE
entries each carry `hardware.poe: "S360-410"` as a
catalog-level mapping field only — Release-One identity,
not S360-410-subject WebFlash readiness evidence; the six
`legacy-compatible` `*-poe` Core variants stay
`legacy-compatible` / `webflash_build_matrix: false` / no
`config_string` / no `webflash_wrapper` / no
`artifact_name`);
[`config/hardware-catalog.json`](../config/hardware-catalog.json)
`S360-410` row stays byte-identical
(`schematic_status: cataloged_unverified`, no
`schematic_file`);
[`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml)
stays byte-identical to PR #517 / PR #526 / PR #528 state.
The 2026-05-20 `WEBFLASH-POE-410-001` investigation pass is
**confirmed deferred** — eight blocker preconditions remain
open: (1) `PRODUCT-POE-410-001` implementation slice (only
docs-only investigation merged as PR #528); (2)
`PACKAGE-POE-410-001` implementation slice (only docs-only
investigation merged as PR #526; a wrapper cannot wrap a
package that stays `reference-only` +
`schematic-evidence-pending` + `do-not-change-release-one`);
(3) BOM cross-check missing; (4) `S360-410`
`schematic_status: verified` JSON PR not landed; (5) HW-002
Open Question #6 / `S360-100-BENCH-001` J2-harness identity
closure missing; (6) Release-One PoE "schematic verification
pending" caveat closure missing — the caveat in
[`release-one-hardware-audit.md` Findings → PoE PSU](release-one-hardware-audit.md#findings)
is **preserved verbatim** by this re-check; (7)
product-onboarding approval per
[`docs/product-onboarding.md`](product-onboarding.md)
missing — `POE` is already reserved in `canonical_power`
and is consumed by both committed builds under the
preserved Release-One caveat, so no new
`webflash_build_matrix: true` row is required to make the
WebFlash compatibility grammar pass, but a wrapper still
cannot land without the upstream product YAML; (8) release
/ build readiness gates open — per the
[Core rule](#core-rule), a WebFlash wrapper requires
product readiness + package readiness + the upstream
product YAML to exist; none of those is satisfied today.
A ninth observation is carried forward but does **not**
resolve the slice today: per
[`product-readiness-matrix.md` §PoE-410 / S360-410](product-readiness-matrix.md#poe-410--s360-410)
and the
[Follow-up PR sequence](#follow-up-pr-sequence) row for
`WEBFLASH-POE-410-001`, "often this slice is not required
because `PRODUCT-POE-410-001` closes by extending the
Release-One caveat without adding a new product"; if
`PRODUCT-POE-410-001` ultimately closes via the default
no-new-entry / caveat-closure-only path,
`WEBFLASH-POE-410-001` becomes a no-op and the family
closes at the existing Release-One caveat without a new
WebFlash wrapper / catalog entry / build-matrix row. The
queue stays blocked / deferred until `PRODUCT-POE-410-001`
implementation or no-op closure is explicitly decided
later. `RELEASE-POE-410-001` / `WF-IMPORT-POE-410-001`
(cross-repo) stay blocked behind `WEBFLASH-POE-410-001`.
The existing Release-One and LED preview WebFlash surface
that consumes S360-410 is **not** affected: Release-One
wrapper / catalog `status: production` / `channel: stable`
/ `webflash_build_matrix: true` / artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` /
tag `v1.0.0` stay verbatim; LED preview wrapper / catalog
`status: preview` / `channel: preview` /
`webflash_build_matrix: true` / artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`
stay verbatim. The Release-One PoE "schematic verification
pending" caveat in
[`release-one-hardware-audit.md` Findings → PoE PSU](release-one-hardware-audit.md#findings)
is **preserved verbatim** by this re-check. Path B
(documentation / catalog-classification-note-only cleanup)
was rejected because this section already correctly
classifies the slice as `not-webflash-ready` for any new
PoE-410 product entry, with the existing Release-One
exposure unaffected, and the Follow-up PR sequence row
already names the product + caveat-closure +
product-onboarding gates (same rule PR #522 applied to the
parallel `WEBFLASH-POWER-400-001` slice); Path C
(implementation) was unsafe because adding a WebFlash
wrapper without a canonical S360-410 / `POE`-410-subject
product YAML to wrap would break the
[Core rule](#core-rule), and adding a build-matrix row or
flipping `webflash_build_matrix: true` on a
Release-One-identity entry while the Release-One PoE
caveat is preserved would implicitly requalify Release-One
— explicitly forbidden by PR #526 / PR #528 and by every
prior PoE-410 follow-up document. The next
`WEBFLASH-POE-410-001` PR (if and only if
`PRODUCT-POE-410-001` adds a new PoE-410-explicit product
entry) must land **the WebFlash wrapper + the catalog
`webflash_build_matrix: true` flip + the build-matrix row
+ the UX-class decision as a single atomic slice**, not as
a documentation cleanup alone, and only after
`PRODUCT-POE-410-001` implementation and the Release-One
PoE caveat-closure PR both land. See
[`docs/cleanup-audit.md` §`WEBFLASH-POE-410-001 update (2026-05-20 — docs-only investigation pass)`](cleanup-audit.md#webflash-poe-410-001-update-2026-05-20--docs-only-investigation-pass).

**2026-05-20 — `RELEASE-POE-410-001` investigation pass
(Path A docs-only deferral) — note on WebFlash exposure
surface.** The downstream `RELEASE-POE-410-001` Path A
investigation pass merged the same day as this PR
re-verified the WebFlash exposure surface that
`RELEASE-POE-410-001` consumes (the
[`config/webflash-builds.json`](../config/webflash-builds.json)
matrix and the
[`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)
workflow that processes it) and confirmed it is byte-identical
to the PR #530 state: only the two existing
Release-One / LED preview builds remain, both consuming
S360-410 logically under the preserved Release-One caveat,
not as S360-410-subject WebFlash exposure. No PoE-410-explicit
WebFlash wrapper / catalog `webflash_build_matrix: true` flip
/ build-matrix row was added by `RELEASE-POE-410-001`; this
WebFlash-exposure layer is **not** advanced by that release-layer
investigation pass. The eight `WEBFLASH-POE-410-001` blocker
preconditions recorded above stay open; the ninth carried-forward
observation (`WEBFLASH-POE-410-001` may not be required if
`PRODUCT-POE-410-001` closes by no-new-entry / caveat-closure
only) is restated by `RELEASE-POE-410-001` for the release
layer (`RELEASE-POE-410-001` is similarly not required if the
upstream family closes by no-new-entry / caveat-closure only).
Re repo-committed BOM evidence: BOM files have been supplied
out-of-band / uploaded, and for `S360-410` the uploaded BOM
appears to support the schematic-shown discrete PoE topology,
but **repo-committed BOM evidence has not landed in this
repository yet** — BOM ingest is the responsibility of a
separate `HW-BOM-ASSETS-001` follow-up, not of
`RELEASE-POE-410-001`. See
[`docs/release-artifact-readiness-matrix.md` §PoE / S360-410 release posture](release-artifact-readiness-matrix.md#poe--s360-410-release-posture)
and
[`docs/cleanup-audit.md` §`RELEASE-POE-410-001 update (2026-05-20 — docs-only investigation pass)`](cleanup-audit.md#release-poe-410-001-update-2026-05-20--docs-only-investigation-pass).

## Release-One and LED preview safety

The Release-One production product and the LED preview product are
the two existing WebFlash-shippable surfaces in this repo. Both are
explicitly preserved by this PR.

**Release-One — do not change.**

- Config string: `Ceiling-POE-VentIQ-RoomIQ`.
- Catalog entry: `status: production`, `channel: stable`,
  `version: 1.0.0`,
  `artifact_name: Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`,
  `webflash_wrapper: products/webflash/ceiling-poe-ventiq-roomiq.yaml`,
  `webflash_build_matrix: true`,
  `blocked_modules: ["FanTRIAC", "LED"]`,
  `hardware_status: verified-for-release-one`.
- Product YAML:
  [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml).
- WebFlash wrapper:
  [`products/webflash/ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml).
- Build-matrix row:
  [`config/webflash-builds.json`](../config/webflash-builds.json)
  Release-One entry.
- `release_one_required_configs`:
  `["Ceiling-POE-VentIQ-RoomIQ"]`.
- GitHub Release tag: `v1.0.0`.

WEBFLASH-GAP-001 does **not**:

- alter the Release-One product YAML, wrapper, catalog entry, build
  matrix row, or release artifact,
- alter the Release-One wrapper / catalog / build / release / import
  surface in any way,
- add any missing-module product (FanRelay / FanPWM / FanDAC /
  FanTRIAC / PWR-240V / PoE-410 new entry) to the Release-One config
  string,
- add any new `release_one_required_configs` member,
- change the `blocked_modules: ["FanTRIAC", "LED"]` list on the
  Release-One catalog entry.

**LED preview — do not change.**

- Config string: `Ceiling-POE-VentIQ-RoomIQ-LED`.
- Catalog entry: `status: preview`, `channel: preview`,
  `version: 1.0.0`,
  `artifact_name: Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`,
  `webflash_wrapper: products/webflash/ceiling-poe-ventiq-roomiq-led.yaml`,
  `webflash_build_matrix: true`,
  `blocked_modules: ["FanTRIAC"]`,
  `hardware_status: verified-led-candidate`.
- Product YAML:
  [`products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq-led.yaml).
- WebFlash wrapper:
  [`products/webflash/ceiling-poe-ventiq-roomiq-led.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq-led.yaml).

WEBFLASH-GAP-001 does **not**:

- promote the LED preview to `production` / `stable`,
- add LED to `release_one_required_configs`,
- add an LED-specific kit,
- change the LED preview wrapper / catalog / build / release /
  import surface in any way,
- add missing-module products (FanRelay / FanPWM / FanDAC /
  FanTRIAC) to the LED preview config string,
- close the bench-verification Open Questions in
  [`hardware/s360-300-r4-led.md`](hardware/s360-300-r4-led.md)
  (harness rail, LED count, harness identity, observed LED ring
  behaviour) — these remain carried as preview-stage caveats.

LED's eventual promotion to `production` / `stable` is owned by
[`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
17-row gauntlet plus the
[`product-led-preview-decision.md`](product-led-preview-decision.md)
record, and is explicitly **not** in scope for this matrix.

## REQUIRED_CONFIGS policy

`release_one_required_configs` in
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
is the WebFlash-side baseline site-health list. It is **not** the
list of every valid firmware build, **not** the list of every
WebFlash-shippable product, and **not** the list of every recommended
product. It is the small set of configurations that WebFlash treats
as required for a fleet to count as healthy under the Release-One
contract.

The policy:

- **New preview candidates are not REQUIRED_CONFIGS.** Adding a
  `preview-candidate` to the WebFlash build matrix does not add it to
  `release_one_required_configs`. The two decisions are separately
  gated. Today this is enforced for `Ceiling-POE-VentIQ-RoomIQ-LED`
  (preview, in build matrix, **not** in `release_one_required_configs`).
- **Advanced / manual-warning products are not REQUIRED_CONFIGS — ever
  by default.** A family classified `advanced/manual-warning-only` is
  reachable only behind the manual-warning UX gate, never on the
  standard landing list, and never added to
  `release_one_required_configs` by default. This applies categorically
  to FanTRIAC. Any future REQUIRED_CONFIGS addition would be a
  separate, explicit PR with COMPLIANCE-001 sign-off and is **not**
  authorised by this matrix.
- **FanTRIAC is never REQUIRED_CONFIGS by default.** Restated for
  clarity: irrespective of any future product YAML existence, catalog
  status flip, wrapper addition, build-matrix entry, release artifact,
  or WebFlash import, FanTRIAC is not added to
  `release_one_required_configs` by this matrix or by `WF-TRIAC-001`.
  Any such addition is a separate, explicit, scoped PR.
- **LED's stable promotion is a separate decision.** Whether LED is
  ever added to `release_one_required_configs` is owned by
  [`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
  and the
  [`product-led-preview-decision.md`](product-led-preview-decision.md)
  record. WEBFLASH-GAP-001 does not move LED into
  `release_one_required_configs` and does not authorise such a move.
- **Any future REQUIRED_CONFIGS addition requires a separate explicit
  PR.** The PR must name the configuration, demonstrate stable-channel
  release-artifact existence + WebFlash-side import + 17-row gauntlet
  closure, and gate its membership on the explicit site-health
  argument. The PR is not implied by any preview-candidate addition,
  any advanced / manual-warning addition, or any wrapper / catalog /
  build-matrix slice.

## Kit / recommended path policy

Kit / recommended path exposure is **separate** from WebFlash
installability. A product can be installable through WebFlash without
being kit / recommended; a product can be kit / recommended without
being in `release_one_required_configs`. The two surfaces are
independent.

The policy:

- **Kit / recommended exposure is separate from WebFlash
  installability.** A `preview-candidate` is reachable through WebFlash
  but is not added to kit / default / recommended surfaces by default.
- **A product can be installable but not recommended.** The standard
  WebFlash landing list is not the same as the recommended bundle.
  Recommended bundles are an additional product / UX decision.
- **Advanced / manual-warning products must not be kit / default /
  recommended.** A family classified `advanced/manual-warning-only`
  is excluded from kit, default, and recommended surfaces
  categorically. This applies to FanTRIAC.
- **FanTRIAC must not be kit / default / recommended.** Restated for
  clarity: irrespective of any future product YAML existence, catalog
  status flip, wrapper addition, build-matrix entry, release artifact,
  or WebFlash import, FanTRIAC is not added to kit / default /
  recommended surfaces (`scripts/data/kits.json` etc. in the WebFlash
  repo) by this matrix or by `WF-TRIAC-001`. Any such addition is a
  separate, explicit, scoped PR.
- **Relay / PWM / DAC need separate product / UX decisions before kit /
  recommended exposure.** Reaching `preview-candidate` does not
  authorise kit / recommended membership. The per-family slice PRs
  `PRODUCT-RELAY-001` / `PRODUCT-PWM-001` / `PRODUCT-DAC-001` decide
  kit / recommended exposure as a separate UX question, **after** the
  product YAML lands.
- **Release-One's existing kit / recommended membership is not
  touched** by this matrix.
- **LED's kit / recommended decision is separate** and remains owned by
  [`product-led-preview-decision.md`](product-led-preview-decision.md);
  this matrix does not move LED into a kit / default / recommended
  bundle.

## Wrapper / catalog / build gates

The wrapper / catalog / build-matrix triad is the chunk of the
9-gate chain that lives inside this repo and is implemented by the
per-family `WEBFLASH-*-001` slices. Each is a separate, named gate;
no slice may skip any of the three.

| Sub-gate | What it adds | Where | Validated by |
|---|---|---|---|
| Wrapper | A thin product wrapper YAML that consumes the canonical product YAML under [`products/`](../products/) and includes the WebFlash-specific substitutions (`webflash_config_string` etc.). | [`products/webflash/<family>-<config>.yaml`](../products/webflash/) | [`tests/test_product_substitutions.py`](../tests/test_product_substitutions.py) (substitution shape), [`tests/validate_configs.py`](../tests/validate_configs.py) (ESPHome YAML validity), the existing [`tests/test_release_one_entity_names.py`](../tests/test_release_one_entity_names.py) where appropriate. |
| Catalog entry | A row in [`config/product-catalog.json`](../config/product-catalog.json) with `config_string`, `status` (one of the existing `lifecycle_statuses`), `version`, `channel`, `product_yaml`, `webflash_wrapper`, `artifact_name`, `webflash_build_matrix`, `modules` map, `blocked_modules` list where appropriate, `hardware` SKU map, and `hardware_status` label. | [`config/product-catalog.json`](../config/product-catalog.json) | [`tests/test_product_catalog.py`](../tests/test_product_catalog.py), [`tests/test_product_catalog_consistency.py`](../tests/test_product_catalog_consistency.py), [`scripts/validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py). |
| Build-matrix entry | A row in [`config/webflash-builds.json`](../config/webflash-builds.json) with `config_string`, `product_yaml`, `artifact_name`, `channel`, `version`, `chip_family`, `hardware_requirements`, `features`. | [`config/webflash-builds.json`](../config/webflash-builds.json) | [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py), [`tests/test_webflash_compatibility.py`](../tests/test_webflash_compatibility.py), [`tests/test_webflash_artifact_naming.py`](../tests/test_webflash_artifact_naming.py). |

Compatibility-grammar conformance — `canonical_mounting` /
`canonical_power` / `canonical_modules` / `forbidden_tokens` / mutex
rules / fan-driver `max-one-of` / `fandac_conflicts_with_airiq` —
remains an additional gate, validated by
[`tests/test_webflash_compatibility.py`](../tests/test_webflash_compatibility.py)
against
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json).
No new `canonical_modules` token, no new `forbidden_tokens` entry,
and no relaxation of any mutex / `max-one-of` rule is added by this
matrix or by any per-family slice without an explicit grammar
amendment PR.

## Release and import gates

The release-artifact gate and the WebFlash-side import gate live
beyond the wrapper / catalog / build-matrix triad. Each is a separate
PR and a separate validation pass.

| Gate | What it produces | Where | Validated by |
|---|---|---|---|
| Release artifact (`RELEASE-GAP-001`) | A signed firmware artifact `Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin` released via [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml), with release notes generated by [`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py). | GitHub Release on `sense360store/esphome-public`. | [`tests/test_webflash_artifact_naming.py`](../tests/test_webflash_artifact_naming.py), [`tests/test_validate_webflash_release_notes.py`](../tests/test_validate_webflash_release_notes.py), [`tests/test_generate_webflash_release_notes.py`](../tests/test_generate_webflash_release_notes.py), [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py), [`scripts/check-webflash-release-assets.py`](../scripts/check-webflash-release-assets.py). |
| WebFlash-side import (`WF-IMPORT-GAP-001`) | An entry in the WebFlash repo's `manifest.json` / `firmware-N.json` per [`webflash-release-handoff.md`](webflash-release-handoff.md), the existing release-proof record per [`webflash-release-proof.md`](webflash-release-proof.md), and the `firmware/sources.json` mapping. | Owned by the WebFlash repo (`sense360store/webflash`), not this repo. | WebFlash-side validators; the release-handoff record is the proof. |
| Stable promotion (per-product, in `RELEASE-GAP-001`) | A `channel: stable` artifact only after the full 17-row gauntlet in [`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md) clears. | GitHub Release. | The 17-row gauntlet; the existing artifact-naming / release-notes validators. |

Neither `RELEASE-GAP-001` nor `WF-IMPORT-GAP-001` is performed by
this matrix. No firmware is built, signed, released, or imported by
WEBFLASH-GAP-001.

## Follow-up PR sequence

Each entry below is a separate PR with its own scope, review, and
gate evidence. WEBFLASH-GAP-001 does not commit to a calendar and
does not order these beyond the dependencies recorded in
[`hardware/board-readiness-matrix.md` Follow-up PR sequence](hardware/board-readiness-matrix.md#follow-up-pr-sequence),
[`hardware/package-readiness-matrix.md` Follow-up PR sequence](hardware/package-readiness-matrix.md#follow-up-pr-sequence),
[`product-readiness-matrix.md` Follow-up PR sequence](product-readiness-matrix.md#follow-up-pr-sequence),
and the per-board audit docs.

| PR | Purpose | Gated on |
|---|---|---|
| **`WEBFLASH-RELAY-001`** (alias: `WEBFLASH-GAP-001` FanRelay slice) | Add the FanRelay WebFlash wrapper under [`products/webflash/`](../products/webflash/) behind an explicit advanced / manual-warning UX gate, catalog entry in [`config/product-catalog.json`](../config/product-catalog.json) with `webflash_wrapper` + `webflash_build_matrix: true` on a non-`stable` channel, and build-matrix row in [`config/webflash-builds.json`](../config/webflash-builds.json). Honours the **`advanced/manual-warning-only`** exposure class (not the default `preview-candidate` standard-exposure ladder rung — `PRODUCT-RELAY-001-READINESS-REFRESH` explicitly rejects standard preview surfacing for a mains-switching driver without installation / safety wording or a competent-person caveat); never `release_one_required_configs`, never kit / recommended. User-facing naming is **outcome-first** (e.g. "Relay fan control" or "Switched fan control"), not loose board / module naming. | `PRODUCT-RELAY-001` landed + production-wide / multi-unit / oscilloscope-traced general ESP32-S3 `GPIO3` strap-pin boot-behaviour characterisation against multiple populated `S360-310-R4` + `S360-100-R4` units + installation / safety / competent-person sign-off + WebFlash-side manual-warning UX parity. |
| **`WEBFLASH-PWM-001`** (alias: `WEBFLASH-GAP-001` FanPWM slice) | Same as above for FanPWM. Decide retention / migration / removal of the legacy four-channel [`products/sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml) in coordination with `PRODUCT-PWM-001` (typically: retain `legacy-compatible`; do not migrate to a non-legacy sibling). | `PRODUCT-PWM-001` landed. |
| **`WEBFLASH-DAC-001`** (alias: `WEBFLASH-GAP-001` FanDAC slice) | Same as above for FanDAC. Enforce the `FanDAC ↔ AirIQ` mutex; no AirIQ-bearing FanDAC product / wrapper / catalog entry / build-matrix row is added. | `PRODUCT-DAC-001` landed. |
| **`WF-TRIAC-001`** | Advanced / manual-warning WebFlash wrapper / catalog / build-matrix entry for FanTRIAC, behind an explicit manual-warning UX gate. **Separate** from the standard `WEBFLASH-*-001` flow because of the advanced / manual-warning posture. Not standard, not recommended, not kit / default, not `release_one_required_configs`. | `PRODUCT-TRIAC-001` landed (wording-only catalog policy decided) + `PRODUCT-TRIAC-002` landed (product YAML / catalog-entry rework) + `COMPLIANCE-001` advanced / manual-warning sign-off + WebFlash-side manual-warning UX implemented. |
| **`WEBFLASH-POWER-400-001`** (alias: `WEBFLASH-GAP-001` PWR-240V slice) | Same as above for PWR-240V. UX class (standard preview-candidate vs advanced / manual-warning) decided per the `PRODUCT-POWER-400-001` compliance verdict. | `PRODUCT-POWER-400-001` landed + `COMPLIANCE-001` S360-400 slice closed. |
| **`WEBFLASH-POE-410-001`** (alias: `WEBFLASH-GAP-001` PoE-410 slice) | **If and only if** `PRODUCT-POE-410-001` adds a new PoE-410-explicit product YAML, add the corresponding wrapper + catalog entry + build-matrix row. Often this slice is not required because `PRODUCT-POE-410-001` closes by extending the Release-One caveat without adding a new product. | `PRODUCT-POE-410-001` landed + new product entry added (else: not required). |
| **`RELEASE-GAP-001`** | Build, sign, and release firmware artifacts for the WebFlash entries added by the per-family slices above. Uses the existing [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml) flow. Stable promotion gated additionally by [`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md). | The relevant per-family slice landed; the 17-row gauntlet applied for any stable promotion. |
| **`WF-IMPORT-GAP-001`** | Import the signed artifacts into the WebFlash repo's `manifest.json` / `firmware-N.json` per [`webflash-release-handoff.md`](webflash-release-handoff.md). Owned by the WebFlash repo, not this repo. | `RELEASE-GAP-001` landed for the entries to be imported. |
| **`RELEASE-TRIAC-001`** | Build, sign, and release the FanTRIAC artifact behind the advanced / manual-warning UX. Separate from `RELEASE-GAP-001` because of the advanced / manual-warning posture. Not stable. | `WF-TRIAC-001` landed. |
| **`WF-IMPORT-TRIAC-001`** | Import the FanTRIAC artifact into the WebFlash repo behind the advanced / manual-warning UX. Separate from `WF-IMPORT-GAP-001` because of the advanced / manual-warning posture. | `RELEASE-TRIAC-001` landed. |

None of these PRs is approved or scoped by WEBFLASH-GAP-001 itself.
They are recorded so the matrix has a clear next-action chain.

## BLOCKER-BURNDOWN-001 consolidation (2026-05-26)

The consolidated cross-lane blocker view now lives in
[`docs/blocker-burndown.md`](blocker-burndown.md) (BLOCKER-BURNDOWN-001).
For the WebFlash axes specifically, that pass re-confirms — without any
exposure change — that:

- **Live `sense360store/WebFlash` access is unavailable this session**
  (GitHub scope is `esphome-public` + `esphome` only), so every
  WebFlash-side gate stays prior-recorded (`NEEDS WEBFLASH ACCESS`),
  including the still-owed `S360-311` / `S360-312`
  `module-availability.js` classifications (`WEBFLASH-DRIFT-001`
  rows #16/#17) and the `S360-310` `design-pending` re-record.
- The Relay / DAC / PWM WebFlash wrappers stay **`BLOCKING`**; the
  substantive non-WebFlash gates are bench / operator / safety, not
  repo gates.
- The recommended next WebFlash steps stay the per-family
  **`WEBFLASH-{RELAY,DAC,PWM}-LIVE-CHECK-001`** (or a `WEBFLASH-DRIFT-001`
  re-run) once read access is restored — **not** any wrapper-plan slice.

No `webflash_build_matrix` flip, no `artifact_name`, no wrapper, and no
exposure / import / release / compliance claim is made by the
consolidation.

## Do-not-change guardrails

WEBFLASH-GAP-001 — this matrix — performs **none** of the following.
Anyone reading this matrix looking for justification to change one
of them must use a separate, scoped PR with its own gate evidence.

- No edits to any WebFlash wrapper under
  [`products/webflash/`](../products/webflash/) — the production
  [`ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml),
  the LED preview
  [`ceiling-poe-ventiq-roomiq-led.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq-led.yaml),
  and the blocked reference
  [`ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml)
  all stay verbatim. **No new wrapper is added.**
- No edits to any product YAML under
  [`products/`](../products/) — including all three current
  catalog-tracked entries
  ([`sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml),
  [`sense360-ceiling-poe-ventiq-roomiq-led.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq-led.yaml),
  [`sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml))
  and all 31 `legacy-compatible` entries. **No new product YAML is
  added.**
- No edits to any package YAML under
  [`packages/`](../packages/). All packages — the six fan-driver /
  power packages
  ([`fan_relay.yaml`](../packages/expansions/fan_relay.yaml),
  [`fan_pwm.yaml`](../packages/expansions/fan_pwm.yaml),
  [`fan_gp8403.yaml`](../packages/expansions/fan_gp8403.yaml),
  [`fan_triac.yaml`](../packages/expansions/fan_triac.yaml),
  [`power_240v.yaml`](../packages/hardware/power_240v.yaml),
  [`power_poe.yaml`](../packages/hardware/power_poe.yaml)), the Core
  abstract packages
  ([`sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml),
  [`sense360_core.yaml`](../packages/hardware/sense360_core.yaml)),
  the legacy four-channel
  [`sense360_fan_pwm.yaml`](../packages/expansions/sense360_fan_pwm.yaml),
  and the SX1509 expander
  [`gpio_expander_sx1509.yaml`](../packages/expansions/gpio_expander_sx1509.yaml)
  — stay verbatim.
- No edits to
  [`config/hardware-catalog.json`](../config/hardware-catalog.json),
  [`config/product-catalog.json`](../config/product-catalog.json),
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  or
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json).
  No new product entry, no new `lifecycle_statuses` value, no new
  `canonical_modules` token, no new `forbidden_tokens` entry, no new
  `release_one_required_configs` membership, no new build-matrix
  entry, no `webflash_build_matrix` flip, no compatibility rule
  relaxation, no mutex change.
- No edits to any script under
  [`scripts/`](../scripts/), any test under
  [`tests/`](../tests/), any workflow under
  [`.github/workflows/`](../.github/workflows/), any component under
  [`components/`](../components/), any include under
  [`include/`](../include/), or any firmware artifact under
  `firmware/` (including `firmware/sources.json` and `manifest.json`).
- No firmware regenerated, no firmware signed, no GitHub Release
  created or modified, no WebFlash import performed, no WebFlash-side
  `manifest.json` / `firmware-N.json` / `scripts/data/kits.json`
  edit attempted.
- No change to the Release-One configuration `Ceiling-POE-VentIQ-RoomIQ`
  (`status: production`, `channel: stable`, version `1.0.0`,
  artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`,
  tag `v1.0.0`,
  `release_one_required_configs: ["Ceiling-POE-VentIQ-RoomIQ"]`).
- No change to the LED preview `Ceiling-POE-VentIQ-RoomIQ-LED` (stays
  `status: preview`, `channel: preview`, version `1.0.0`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`,
  `blocked_modules: ["FanTRIAC"]`).
- No change to the FanTRIAC reference
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` (stays `status: blocked`,
  `blocker: HW-005`, `webflash_build_matrix: false`).
- No change to the mains-voltage compliance status of `S360-320` or
  `S360-400` (owned by COMPLIANCE-001;
  [`compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)).
- No addition of any candidate family (FanRelay / FanPWM / FanDAC /
  FanTRIAC product-side / PWR-240V / PoE-410 new entry) to
  `release_one_required_configs`, to kit / default surfaces, to
  recommended surfaces, or to Release-One.
- No promotion of `Ceiling-POE-VentIQ-RoomIQ-LED` to `production` /
  `stable` and no addition of LED to `release_one_required_configs`.
- No resolution of the Core J10 vs RoomIQ J6 pin-order open question
  (owned by HW-009 + the per-board audit follow-ups).
- No resolution of the systemic Core abstract-bus mismatch
  (`CORE-ABSTRACT-BUS-001`; owned by
  [`release-one-hardware-audit.md`](release-one-hardware-audit.md)
  Required follow-ups #2 / #3).
- No removal or deprecation of any `legacy-compatible` entry; the
  31 `legacy-compatible` entries stay `legacy-compatible`. Removal is
  owned by
  [`product-deprecation-removal-policy.md`](product-deprecation-removal-policy.md)
  and `PRODUCT-DEP-001`.

## Validation

WEBFLASH-GAP-001 is documentation-only and runs only the docs-safe
validators. Every validator must continue to pass without any
configuration / product / package / wrapper / build / release edit.

### Test commands

```text
python3 tests/test_hardware_catalog.py
python3 tests/test_product_catalog.py
python3 tests/test_product_catalog_consistency.py
python3 tests/validate_webflash_builds.py
python3 tests/test_webflash_compatibility.py
python3 tests/test_webflash_artifact_naming.py
python3 tests/test_validate_webflash_release_notes.py
python3 tests/test_generate_webflash_release_notes.py
python3 tests/test_product_substitutions.py
python3 tests/test_release_one_entity_names.py
python3 tests/validate_configs.py
python3 tests/test_led_package_mapping.py
```

### Diff expectations

```text
git diff products products/webflash packages config scripts tests \
        .github/workflows components include firmware
```

Expected: **empty**. WEBFLASH-GAP-001 changes none of these paths.

The full PR diff is limited to:

- `docs/webflash-exposure-readiness-matrix.md` (new file)
- `docs/product-readiness-matrix.md` (one See-also entry added)
- `docs/cleanup-audit.md` (one classification row added)

### Sanity-grep expectations

```text
grep -RIn "WEBFLASH-GAP-001|webflash-exposure-readiness|not-webflash-ready|missing-product-yaml|advanced/manual-warning|not-required-configs|not-recommended|not-kit-default|FanRelay|FanPWM|FanDAC|FanTRIAC|S360-310|S360-311|S360-312|S360-320|S360-400|S360-410" \
     docs config products products/webflash packages tests
```

Expected:

- `WEBFLASH-GAP-001` appears in `docs/webflash-exposure-readiness-matrix.md`,
  `docs/product-readiness-matrix.md`, `docs/cleanup-audit.md`, plus
  the existing references in
  `docs/hardware/board-readiness-matrix.md`,
  `docs/hardware/package-readiness-matrix.md`, and the per-board
  audit docs.
- `webflash-exposure-readiness` appears in
  `docs/webflash-exposure-readiness-matrix.md` and in cross-link
  destinations in
  `docs/product-readiness-matrix.md` and `docs/cleanup-audit.md`.
- The new policy labels (`not-webflash-ready`, `missing-product-yaml`,
  `missing-package-readiness`, `missing-hardware-evidence`,
  `not-required-configs`, `not-recommended`, `not-kit-default`) appear
  only in `docs/webflash-exposure-readiness-matrix.md` (plus the
  pre-existing additive qualifier usage of `not-required-configs` /
  `not-recommended` / `not-kit` in `docs/product-readiness-matrix.md`).
- `advanced/manual-warning` continues to appear in the existing docs
  (`docs/product-readiness-matrix.md`,
  `docs/hardware/s360-320-r4-triac.md`, etc.) plus the new matrix.
- `FanRelay` / `FanPWM` / `FanDAC` / `FanTRIAC` and `S360-310` /
  `S360-311` / `S360-312` / `S360-320` / `S360-400` / `S360-410`
  continue to appear in the existing docs / configs / packages and
  in the new matrix.
- No new occurrences of any of the above tokens appear under
  `products`, `products/webflash`, `packages`, `config`, `scripts`,
  `tests`, or `.github/workflows`.

## See also

- [`docs/webflash-drift-audit.md`](webflash-drift-audit.md) —
  `WEBFLASH-DRIFT-001` cross-repo drift audit (esphome-public vs WebFlash
  product / import). Source of the prior-recorded WebFlash-side facts and the
  `MATCH` / `INTENTIONALLY-BLOCKED` / `NEEDS-OPERATOR-INPUT` drift classification
  cited in the cross-repo drift note above. Documentation only.
- [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
  — RELEASE-GAP-001 release-layer readiness gate. Downstream from
  this matrix: classifies per-family release artifact eligibility
  (build / sign / attach / checksums / release-notes /
  release-proof / operator-proof / import) for the same FanRelay /
  FanPWM / FanDAC / FanTRIAC / PWR-240V / PoE-410 candidate
  families, and names the per-family release slices
  (`RELEASE-RELAY-001`, `RELEASE-PWM-001`, `RELEASE-DAC-001`,
  `RELEASE-TRIAC-001`, `RELEASE-POWER-400-001`,
  `RELEASE-POE-410-001`). Preserves Release-One, the LED preview,
  and the FanTRIAC blocked reference; treats `RELEASE-007` LED
  stable as reference-only and out-of-scope. Documentation only.
- [`docs/product-readiness-matrix.md`](product-readiness-matrix.md)
  — PRODUCT-GAP-001 product-level readiness gate. Source of truth
  for the "Current product readiness" column on every candidate row
  in this matrix. Documentation only.
- [`docs/stable-target-expansion-plan.md`](stable-target-expansion-plan.md)
  — STABLE-TARGET-EXPANSION-PLAN-001 actionable stable-target
  expansion plan. Per-candidate G1–G10 gate checklist and the
  recommended `STABLE-TARGET-*-001` PR sequence. Documentation only;
  promotes nothing.
- [`docs/stable-target-ventiq-001-gate-closure.md`](stable-target-ventiq-001-gate-closure.md)
  — STABLE-TARGET-VENTIQ-001 gate-closure record. Per-gate G1–G10
  audit for `Ceiling-POE-VentIQ`; records option-3 deferral; no
  WebFlash wrapper added under [`products/webflash/`](../products/webflash/);
  no `webflash_build_matrix` flip; no `artifact_name`; no
  `config/webflash-builds.json` row.
- [`docs/package-poe-410-001-audit.md`](package-poe-410-001-audit.md)
  — PACKAGE-POE-410-001 per-evidence-class audit for `S360-410`
  Sense360 PoE PSU. Upstream G8 / WebFlash-exposure blocker for
  any sibling PoE-410-explicit WebFlash wrapper under
  [`products/webflash/`](../products/webflash/) and for the five
  A-row stable expansion candidates. Records the option-4 outcome
  (evidence insufficient for verification; precise
  evidence-request record produced). Documentation + test-constant
  pin only; `S360-410` stays `cataloged_unverified`;
  `packages/hardware/power_poe.yaml` stays byte-identical; no
  WebFlash wrapper, no `webflash_build_matrix` flip, no
  `artifact_name`, no `config/webflash-builds.json` row added.
- [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
  — PACKAGE-GAP-001 package-level readiness gate. Source of truth
  for the "Required package status" column on every candidate row
  in this matrix. Documentation only.
- [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
  — HW-GAP-001 board-level readiness matrix. Records the per-board
  hardware-evidence axis this matrix consumes; row #9 of its
  Follow-up PR sequence is `WEBFLASH-GAP-001`.
- [`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md)
  — PRODUCT-AVAIL-001 cross-cutting product availability taxonomy.
  Maps this matrix's exposure-class labels onto the cross-cutting
  13-rung ladder without changing any JSON enum.
- [`docs/product-onboarding.md`](product-onboarding.md) —
  PRODUCT-004 ordered safe sequence for adding any new product /
  config. Every future per-family `PRODUCT-*-001` slice must clear
  the onboarding gates before adding a product YAML, which in turn
  gates the matching `WEBFLASH-*-001` slice in this matrix.
- [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
  — RELEASE-006 canonical 17-row preview-to-stable promotion gate.
  Applies to any future preview-candidate that would target a stable
  channel; not bypassed by WEBFLASH-GAP-001. Also defines the
  REQUIRED_CONFIGS policy and the Kit policy referenced here.
- [`docs/product-led-preview-decision.md`](product-led-preview-decision.md)
  — PRODUCT-009 LED preview decision record. Owns any future
  stable promotion of `Ceiling-POE-VentIQ-RoomIQ-LED`; not bypassed
  by WEBFLASH-GAP-001.
- [`docs/product-deprecation-removal-policy.md`](product-deprecation-removal-policy.md)
  — PRODUCT-DEP-001 deprecation / removal policy. Owns any future
  retirement of `legacy-compatible` entries; WEBFLASH-GAP-001 does
  not deprecate or remove any entry.
- [`docs/release-one.md`](release-one.md) — Release-One overview.
  Source of truth for the Release-One configuration that
  WEBFLASH-GAP-001 leaves unchanged.
- [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)
  — Release-One firmware-vs-schematic audit; source of truth for
  the HW-005 FanTRIAC blocker, the systemic Core abstract-bus rebind
  (CORE-ABSTRACT-BUS-001), and the `S360-410` PoE PSU
  schematic-pending caveat.
- [`docs/webflash-contract.md`](webflash-contract.md) — canonical
  WebFlash artifact / grammar / token contract; the fan-driver
  `max-one-of` rule and the `FanDAC ↔ AirIQ` mutex bound this
  matrix's exposure policy.
- [`docs/webflash-release-handoff.md`](webflash-release-handoff.md)
  — WebFlash-side import handoff record format. Owned by the
  WebFlash repo for `WF-IMPORT-GAP-001` / `WF-IMPORT-TRIAC-001`.
- [`docs/webflash-release-proof.md`](webflash-release-proof.md)
  — Release-One release-proof record. Reference shape for any
  future per-family release proof record produced by
  `RELEASE-GAP-001` / `RELEASE-TRIAC-001`.
- [`docs/webflash-compatibility-taxonomy-audit.md`](webflash-compatibility-taxonomy-audit.md)
  — Audit of the WebFlash compatibility taxonomy; bounds any future
  grammar / token changes that the per-family slices may need to
  request (which are out of scope for this matrix).
- [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
  — COMPLIANCE-001 mains-voltage UK / EU compliance tracker;
  additional gate for any product / WebFlash work consuming
  `S360-320` (FanTRIAC) or `S360-400` (240v PSU). PoE is SELV and
  is not in scope.
- [`docs/hardware/s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md),
  [`docs/hardware/s360-311-r4-pwm.md`](hardware/s360-311-r4-pwm.md),
  [`docs/hardware/s360-312-r4-dac.md`](hardware/s360-312-r4-dac.md),
  [`docs/hardware/s360-320-r4-triac.md`](hardware/s360-320-r4-triac.md),
  [`docs/hardware/s360-400-r4-power.md`](hardware/s360-400-r4-power.md),
  [`docs/hardware/s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md)
  — per-board pin / package mapping audit docs; sources of truth
  for the per-family WebFlash posture sections.
- [`docs/cleanup-audit.md`](cleanup-audit.md) — classification of
  stale / current / blocked-reference / legacy-compatible repo
  content; carries the WEBFLASH-GAP-001 registration row.
- [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  — machine-readable hardware catalog. `schematic_status` stays
  `cataloged_unverified` for `S360-310`, `S360-311`, `S360-312`,
  `S360-320`, `S360-400`, `S360-410`. WEBFLASH-GAP-001 changes none
  of these values.
- [`config/product-catalog.json`](../config/product-catalog.json)
  — machine-readable product catalog. Release-One is
  `status: production`; LED preview is `status: preview`;
  FanTRIAC variant is `status: blocked`, `blocker: HW-005`; the
  31 `legacy-compatible` entries stay `legacy-compatible`.
- [`config/webflash-builds.json`](../config/webflash-builds.json)
  — WebFlash build matrix; contains the two existing builds
  (`Ceiling-POE-VentIQ-RoomIQ` stable;
  `Ceiling-POE-VentIQ-RoomIQ-LED` preview) only.
- [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  — WebFlash compatibility grammar; source of truth for the
  `canonical_modules` / `forbidden_tokens` / mutex / `max-one-of` /
  `fandac_conflicts_with_airiq` rules this matrix's exposure policy
  consumes.

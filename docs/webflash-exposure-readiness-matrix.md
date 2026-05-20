# WebFlash Exposure Readiness Matrix (WEBFLASH-GAP-001)

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
| **FanRelay / S360-310** | none (no `sense360-*-fanrelay-*.yaml`) | `missing` (S360-310 module-side schematic committed under HW-ASSETS-310; HW-PINMAP-310-FOLLOWUP has consumed the schematic and recorded schematic-backed module-`J2` ↔ Core-`J4` logical net match in [`s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md); `packages/expansions/fan_relay.yaml` stays `schematic-evidence-pending` + `needs-package-reconciliation` — silkscreen / harness / `K1` BOM evidence + Core abstract-bus rebind still owed) | `missing-product-yaml` + `missing-package-readiness` + `missing-hardware-evidence` per [`product-readiness-matrix.md`](product-readiness-matrix.md#fanrelay--s360-310) | none | none | `not-webflash-ready` | `preview-candidate` (standard exposure; reach reserved for after package + product slices) | `not-required-configs` (no by default after preview) | `not-recommended` + `not-kit-default` until separate product / UX decision lands | `HW-ASSETS-310` *(landed)* → `HW-PINMAP-310-FOLLOWUP` *(landed)* → silkscreen / harness / `K1` BOM evidence + `CORE-ABSTRACT-BUS-001` → `PACKAGE-RELAY-001` → `PRODUCT-RELAY-001` → `WEBFLASH-RELAY-001` → `RELEASE-GAP-001` → `WF-IMPORT-GAP-001`. |
| **FanPWM / S360-311** | none (no `sense360-*-fanpwm-*.yaml`; legacy [`products/sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml) is `legacy-compatible` only and is not a WebFlash-shippable product entry) | `missing` (S360-311 schematic committed; SX1509-vs-direct-GPIO mapping disagreement unresolved; `packages/expansions/fan_pwm.yaml` `needs-package-reconciliation`) | `missing-product-yaml` + `needs-package-reconciliation` per [`product-readiness-matrix.md`](product-readiness-matrix.md#fanpwm--s360-311) | none | none | `not-webflash-ready` | `preview-candidate` (standard exposure once Core abstract-bus rebind + package slice land) | `not-required-configs` | `not-recommended` + `not-kit-default` (legacy four-channel YAML retention / migration / removal decided by `PRODUCT-PWM-001`) | `HW-PINMAP-311-FOLLOWUP` → `PACKAGE-PWM-001` (+ `CORE-ABSTRACT-BUS-001`) → `PRODUCT-PWM-001` → `WEBFLASH-PWM-001` → `RELEASE-GAP-001` → `WF-IMPORT-GAP-001`. |
| **FanDAC / S360-312** | none (no `sense360-*-fandac-*.yaml`); any future FanDAC product must respect the `FanDAC ↔ AirIQ` mutex (`config/webflash-compatibility.json` `rules.fandac_conflicts_with_airiq: true`) | `missing` (S360-312 schematic committed; voltage-rail discrepancy + DIP-switch I²C address + UART-vs-Nextion arbitration + stale header-comment block all unresolved; `packages/expansions/fan_gp8403.yaml` `needs-package-reconciliation`) | `missing-product-yaml` + `needs-package-reconciliation` + `invalid-combination` with any AirIQ-bearing variant per [`product-readiness-matrix.md`](product-readiness-matrix.md#fandac--s360-312) | none | none | `not-webflash-ready` | `preview-candidate` (standard exposure; AirIQ-bearing FanDAC variants forbidden by mutex) | `not-required-configs` | `not-recommended` + `not-kit-default` (FanDAC ↔ AirIQ mutex narrows the eligible config-string space; kit / recommended decision belongs to `PRODUCT-DAC-001`) | `HW-PINMAP-312-FOLLOWUP` → `PACKAGE-DAC-001` → `PRODUCT-DAC-001` → `WEBFLASH-DAC-001` → `RELEASE-GAP-001` → `WF-IMPORT-GAP-001`. |
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
**HW-PINMAP-310-FOLLOWUP** has consumed the schematic and promoted
[`s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md) from
`pending — schematic/design evidence required` to
`partial — schematic evidence available; package reconciliation
pending`; the audit records the schematic-backed module-`J2` ↔
Core-`J4` logical net match (`+5V` ↔ `+5V`, `Relay` ↔ `Relay`,
`GND` ↔ `GND`) and the module-side relay coil-drive topology
(`Q1` MMBT3904 NPN low-side; `R1` 1 kΩ; `R2` 10 kΩ; `D1` flyback;
coil rail `+5V`; no opto; no indicator LED; no snubber). A
standalone per-board schematic-backed reference doc rewrite is
still owed.
[`packages/expansions/fan_relay.yaml`](../packages/expansions/fan_relay.yaml)
carries `schematic-evidence-pending` + `needs-package-reconciliation`
(Core abstract-bus binds disagree on `relay_pin`: `IO3` per Core
schematic, `GPIO4` per
[`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml),
`GPIO10` per
[`packages/hardware/sense360_core.yaml`](../packages/hardware/sense360_core.yaml);
silkscreen / harness / `K1` BOM evidence still owed). No product
YAML consumes S360-310. No WebFlash wrapper / catalog entry /
build-matrix entry / release artifact / WebFlash import exists.

**Allowed WebFlash action now.** `not-webflash-ready`. No wrapper, no
catalog entry, no build-matrix entry, no release artifact, no
WebFlash import. WEBFLASH-GAP-001 adds **none** of these for the
Relay family.

**Future exposure class (intent).** `preview-candidate` as a standard
exposure, only after the full upstream chain has closed:
`HW-ASSETS-310` *(landed; module-side schematic PDF + curated
artifact index committed)* → `HW-PINMAP-310-FOLLOWUP` *(landed;
schematic-backed reconciliation recorded in
[`s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md))* →
silkscreen / harness / `K1` BOM evidence + `CORE-ABSTRACT-BUS-001`
→ `PACKAGE-RELAY-001` (FanRelay package YAML reconciliation,
including the `relay_pin` resolution) → `PRODUCT-RELAY-001`
(canonical product YAML under [`products/`](../products/), config
string per the WebFlash grammar) → `WEBFLASH-RELAY-001` (wrapper +
catalog entry + build-matrix entry on a non-`stable` channel) →
`RELEASE-GAP-001` (signed artifact) → `WF-IMPORT-GAP-001`
(WebFlash-side import).

**REQUIRED_CONFIGS posture.** `not-required-configs` by default.
After preview-candidate exposure, FanRelay is not added to
`release_one_required_configs`. Any such addition would be a
separate, explicit PR per [REQUIRED_CONFIGS policy](#required_configs-policy).

**Kit / recommended posture.** `not-recommended` + `not-kit-default`
until `PRODUCT-RELAY-001` makes an explicit decision. Relay's
inclusion in kit / default / recommended bundles is not implied by
`preview-candidate` exposure.

**Cross-references.**
[`hardware/s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md),
[`hardware/board-readiness-matrix.md` §S360-310](hardware/board-readiness-matrix.md#s360-310-sense360-relay),
[`hardware/package-readiness-matrix.md` §fan_relay.yaml](hardware/package-readiness-matrix.md#fan_relayyaml--s360-310),
[`product-readiness-matrix.md` §FanRelay / S360-310](product-readiness-matrix.md#fanrelay--s360-310).

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

**Cross-references.**
[`hardware/s360-311-r4-pwm.md`](hardware/s360-311-r4-pwm.md),
[`hardware/board-readiness-matrix.md` §S360-311](hardware/board-readiness-matrix.md#s360-311-sense360-pwm),
[`hardware/package-readiness-matrix.md` §fan_pwm.yaml](hardware/package-readiness-matrix.md#fan_pwmyaml--s360-311),
[`product-readiness-matrix.md` §FanPWM / S360-311](product-readiness-matrix.md#fanpwm--s360-311).

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

**Allowed WebFlash action now.** `not-webflash-ready`. No wrapper,
no catalog entry, no build-matrix entry, no release artifact, no
WebFlash import. The `FanDAC ↔ AirIQ` mutex is not relaxed.

**Future exposure class (intent).** `preview-candidate` as a standard
exposure, only after: `HW-PINMAP-312-FOLLOWUP` (standalone
schematic-backed reference doc; voltage-rail / DIP-switch / UART /
Cloudlift / voltage-mode-jumper resolution) → `PACKAGE-DAC-001`
(FanDAC package YAML reconciliation; stale header-comment cleanup;
DIP-switch address scheme) → `PRODUCT-DAC-001` (canonical product
YAML; enforce `FanDAC ↔ AirIQ` mutex; no AirIQ-bearing FanDAC
product) → `WEBFLASH-DAC-001` (wrapper + catalog + build-matrix on
non-`stable` channel) → `RELEASE-GAP-001` → `WF-IMPORT-GAP-001`.

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
| **`WEBFLASH-RELAY-001`** (alias: `WEBFLASH-GAP-001` FanRelay slice) | Add the FanRelay WebFlash wrapper under [`products/webflash/`](../products/webflash/), catalog entry in [`config/product-catalog.json`](../config/product-catalog.json) with `webflash_wrapper` + `webflash_build_matrix: true` on a non-`stable` channel, and build-matrix row in [`config/webflash-builds.json`](../config/webflash-builds.json). Honours the standard exposure class; not `release_one_required_configs`, not kit / recommended. | `PRODUCT-RELAY-001` landed. |
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

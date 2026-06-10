# Kit Intent Matrix (KIT-MATRIX-001)

## Purpose and scope

This document explains the **productized kit / bundle intent matrix** at
[`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json) and
the tests at [`tests/test_kit_intent_matrix.py`](../tests/test_kit_intent_matrix.py).

The matrix maps the generated 168-row firmware combination matrix at
[`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json)
into **customer-facing productized kit / bundle intent groups** so the
purchase flow, the WebFlash wizard, and downstream product /
WebFlash / release sequencing can pull from a ranked kit-intent view
rather than the raw combination matrix.

This document and the artefacts it describes do **not**:

- add product YAMLs,
- add WebFlash wrappers,
- add `webflash_build_matrix: true` to any product,
- add `artifact_name` to any product,
- build firmware,
- create release artifacts,
- promote LED to stable,
- promote any blocked fan module,
- promote `PWR` / `S360-400`,
- promote `POE` / `S360-410`,
- promote fan modules,
- claim hardware proof exists,
- claim `RELEASE-007` is unblocked,
- claim WebFlash import is ready,
- change [`config/webflash-builds.json`](../config/webflash-builds.json),
  [`config/product-catalog.json`](../config/product-catalog.json),
  [`config/hardware-catalog.json`](../config/hardware-catalog.json),
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
  or [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json),
- change [`docs/firmware-build-gap-report.md`](firmware-build-gap-report.md),
- change `products/**`, `products/webflash/**`, `packages/**`,
  `firmware/**`, `manifest.json`, `firmware/sources.json`,
  `.github/workflows/**`, release artifacts, checksums, or
  build-info manifests,
- change `REQUIRED_CONFIGS`.

## What a "kit intent" is

A **kit intent** is a planned customer purchase unit — an outcome bundle
that maps a marketing-friendly use case (for example "bathroom") onto
the underlying Sense360 module SKUs (Core, RoomIQ, VentIQ, LED ring,
PoE PSU, etc.) and, where one exists, onto the firmware config string
that those modules together produce.

Three identifier spaces are kept deliberately separate:

| Identifier space             | Example                          | Audience       | Source of truth                                                                                  |
|------------------------------|----------------------------------|----------------|--------------------------------------------------------------------------------------------------|
| **Kit SKU**                  | `S360-KIT-BATH-POE`              | Customer       | [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json) (this file)                  |
| **Module SKU**               | `S360-100`, `S360-200`, `S360-211`, `S360-300`, `S360-410` | Inventory / support | [`config/hardware-catalog.json`](../config/hardware-catalog.json)                                |
| **Firmware config string**   | `Ceiling-POE-VentIQ-RoomIQ`      | Build / WebFlash / release | [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json) and [`config/webflash-builds.json`](../config/webflash-builds.json) |

A productized kit existing **does not** imply WebFlash exposure; a
kit may be planned, preview, or blocked without being installable.
Actual installability is still controlled by
[`config/webflash-builds.json`](../config/webflash-builds.json) and the
WebFlash repo's manifest.

## Per-row schema

Each row in the `kits` array carries the following fields:

| Field                                  | Meaning                                                                                                                                |
|----------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| `kit_id`                               | Customer-facing kit SKU. Unique. Example: `S360-KIT-BATH-POE`.                                                                          |
| `customer_name`                        | Human-readable kit name surfaced to customers.                                                                                          |
| `use_case`                             | Marketing-friendly bucket. One of `bathroom`, `kitchen-or-duct-fan`.                                                                    |
| `tier`                                 | One of `ready-kit`, `preview-kit`, `future-expansion`, `advanced-manual`.                                                               |
| `lifecycle_status`                     | One of `production`, `preview`, `hardware-pending`, `blocked`.                                                                          |
| `default_config_string`                | The firmware config string this kit's default firmware build targets, or `null` if no such build exists today.                          |
| `included_module_skus`                 | Module SKUs **shipped** in the kit. Empty when the kit is future / blocked and no shippable inventory exists.                            |
| `recommended_modules`                  | Module SKUs strongly recommended for this use case.                                                                                     |
| `optional_modules`                     | Module SKUs that may be added in custom flows (for example LED in custom bathroom flows).                                                |
| `advanced_modules`                     | Module SKUs that require an explicit advanced / manual choice (for example FanTRIAC).                                                    |
| `excluded_or_not_recommended_modules`  | Module SKUs explicitly outside this kit's intent.                                                                                       |
| `firmware_matrix_lane`                 | The lane id from [`docs/firmware-build-gap-report.md`](firmware-build-gap-report.md) that this kit's firmware sits in, when applicable. |
| `webflash_exposure_allowed_now`        | `true` only if the kit's `default_config_string` is currently committed to [`config/webflash-builds.json`](../config/webflash-builds.json). |
| `stable_ready_now`                     | `true` only if the kit's `default_config_string` is on the stable channel today.                                                         |
| `blockers`                             | List of blocker tokens (for example `S360-300-BENCH-001`, `HW-005`, `COMPLIANCE-001`) that must close before the kit can advance.        |
| `notes`                                | Human-readable narrative.                                                                                                               |

## Rules

The matrix enforces the following productization rules:

- **Bathroom defaults to `VentIQ`, not `AirIQ`.** The Sense360 Bathroom
  Kits pair RoomIQ + VentIQ (S360-211), not AirIQ (S360-210). AirIQ stays
  out of bathroom kit intents.
- **RoomIQ is recommended for bathroom kits** but may become optional in
  custom pick-and-choose flows.
- **LED (S360-300) is optional and preview-gated** until stable promotion
  closes the LED gauntlet (`S360-300-BENCH-001` + `WF-HW-TEST-001` /
  `WF-HW-TEST-003` + `RELEASE-007`). LED stays out of the default stable
  bathroom kit.
- **Relay and TRIAC are bathroom-relevant fan-control concepts.** A relay
  kit (S360-310, low-voltage on/off) and a TRIAC kit (S360-320,
  mains-voltage dimming) are planned bathroom expansions.
- **PWM and 0–10V are advanced duct-fan / kitchen-style concepts**, not
  default bathroom options. They live under `use_case:
  kitchen-or-duct-fan`. PWM uses S360-311; 0–10V uses S360-312 (FanDAC).
- **`PWR` / `S360-400` remains blocked from kits.** No kit currently
  ships with the 240V mains PSU; under `COMPLIANCE-001-RESOLUTION-001`
  (COMPLIANCE-001 closed by market posture) S360-400 is never placed on
  the market, so at most a kit may be designated expansion-ready for the
  self-build board under that record's two binding conditions.
- **TRIAC remains advanced / manual or blocked.** HW-005 +
  HW-PINMAP-320-FOLLOWUP are resolved; PACKAGE-TRIAC-001 (signed
  attestation) + the COMPLIANCE-001-RESOLUTION-001 experimental-lane
  preconditions remain, and an experimental build is never in the kit
  picker by that record's constraints.
- **Kit intent is not product YAML.** A row in this file is not a
  request to add a YAML under `products/**`.
- **Kit intent is not WebFlash exposure.** A row in this file does not
  add a build to [`config/webflash-builds.json`](../config/webflash-builds.json)
  or flip `webflash_build_matrix: true` on any product.
- **Kit intent is not a release artifact.** A row in this file does
  not create firmware binaries, checksums, build-info manifests, or
  GitHub Releases.
- **Custom / pick-and-choose UI must combine kit intent with the
  firmware matrix and WebFlash manifest availability.** If a custom
  module selection does not resolve to a `config_string` that is
  currently in [`config/webflash-builds.json`](../config/webflash-builds.json),
  the UI must not offer a WebFlash install for it, regardless of which
  kit intent the customer started from.

## Wizard usage

Stage 1 of the WebFlash wizard should show **productized bundles as
presets** keyed off `kit_id`. Customers pick a kit; the kit decides the
default module set and (when available) the default firmware config
string.

Later wizard stages may allow **custom pick-and-choose** of module
SKUs. In those stages the wizard must:

1. Reduce the customer's module selection to a token set conformant
   with the grammar in
   [`config/webflash-compatibility.json`](../config/webflash-compatibility.json).
2. Look up the resulting config string in
   [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json).
3. Only offer an actual WebFlash install if the config string is also
   committed in [`config/webflash-builds.json`](../config/webflash-builds.json).
4. Otherwise mark the selection as planned / preview / blocked per the
   matrix row and surface the corresponding `blockers` from this file
   and from [`docs/firmware-build-gap-report.md`](firmware-build-gap-report.md).

A bundle may be planned, preview, or blocked without being installable.
The matrix and the WebFlash manifest still control actual
installability.

## Kits

### S360-KIT-BATH-POE — Sense360 Bathroom Kit — PoE

- **Tier.** `ready-kit`
- **Lifecycle status.** `production`
- **Default firmware config string.** `Ceiling-POE-VentIQ-RoomIQ`
- **Included module SKUs.** S360-100 (Core), S360-200 (RoomIQ),
  S360-211 (VentIQ), S360-410 (PoE PSU)
- **Firmware matrix lane.** `current-webflash` (see
  [`docs/firmware-build-gap-report.md`](firmware-build-gap-report.md))
- **WebFlash exposure allowed now?** yes
- **Stable-ready now?** yes

Default stable bathroom bundle. The firmware config string
`Ceiling-POE-VentIQ-RoomIQ` is the Release-One stable WebFlash build
committed to [`config/webflash-builds.json`](../config/webflash-builds.json).
LED (S360-300) is deliberately routed through the preview kit
`S360-KIT-BATH-POE-LED` until LED stable gates close.

### S360-KIT-BATH-POE-LED — Sense360 Bathroom Kit — PoE + Status Ring Preview

- **Tier.** `preview-kit`
- **Lifecycle status.** `preview`
- **Default firmware config string.** `Ceiling-POE-VentIQ-RoomIQ-LED`
- **Included module SKUs.** S360-100 (Core), S360-200 (RoomIQ),
  S360-211 (VentIQ), S360-300 (LED ring), S360-410 (PoE PSU)
- **Firmware matrix lane.** `current-webflash`
- **WebFlash exposure allowed now?** yes
- **Stable-ready now?** no
- **Blockers.** `S360-300-BENCH-001`, `WF-HW-TEST-001`,
  `WF-HW-TEST-003`, `RELEASE-007`

Preview / early-access bundle. The firmware config string
`Ceiling-POE-VentIQ-RoomIQ-LED` is committed to
[`config/webflash-builds.json`](../config/webflash-builds.json) on the
`preview` channel only. Stable promotion requires the full 17-row
preview-to-stable gauntlet in
[`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md).

### S360-KIT-BATH-RELAY — Sense360 Bathroom Kit — Relay Fan Control

- **Tier.** `future-expansion`
- **Lifecycle status.** `hardware-pending`
- **Default firmware config string.** (none committed)
- **Recommended fan module.** FanRelay / S360-310
- **Firmware matrix lane.** `fanrelay-blocked-package-or-core-bus`
- **WebFlash exposure allowed now?** no
- **Stable-ready now?** no
- **Blockers.** `CORE-ABSTRACT-BUS-001C`, `CORE-ABSTRACT-BUS-001A`,
  `PACKAGE-RELAY-001`, `PRODUCT-RELAY-001`, `WEBFLASH-RELAY-001`,
  `RELEASE-RELAY-001`

Future expansion bundle pairing the stable bathroom kit with the
FanRelay driver (S360-310) for on/off bathroom-fan control.
Implementation chain runs CORE-ABSTRACT-BUS-001C →
CORE-ABSTRACT-BUS-001A → PACKAGE-RELAY-001 → PRODUCT-RELAY-001 →
WEBFLASH-RELAY-001 → RELEASE-RELAY-001 per the FanRelay lane in
[`docs/firmware-build-gap-report.md`](firmware-build-gap-report.md).

**2026-05-22 — `PRODUCT-RELAY-001-READINESS-REFRESH` status update
(docs-only).** `CORE-ABSTRACT-BUS-001C` (PR #557),
`CORE-ABSTRACT-BUS-001A` (PR #558), and `PACKAGE-RELAY-001`
(PR #562 — implemented at the package layer only) have **landed**;
`PRODUCT-RELAY-001`, `WEBFLASH-RELAY-001`, and `RELEASE-RELAY-001`
remain **open**. The blocker token list above mirrors
[`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json)
verbatim; a config-edit PR refreshing the list to drop the landed
blockers is owed separately (this readiness-refresh PR is
documentation-only and does not edit any
[`config/`](../config/) file). Per the
[`docs/product-readiness-matrix.md` §FanRelay / S360-310](product-readiness-matrix.md#fanrelay--s360-310)
recommended posture, the FanRelay product-layer disposition is
`advanced/manual-warning-only` + product-YAML-allowed (no
WebFlash) + compile-only-allowed; **the Relay Bathroom Kit
remains `future-expansion` / `hardware-pending` and
`webflash_exposure_allowed_now: false` /
`stable_ready_now: false`**, irrespective of any future
`PRODUCT-RELAY-001` implementation. The default sellable kit
remains `S360-KIT-BATH-POE` mapped to Release-One
`Ceiling-POE-VentIQ-RoomIQ` on the `stable` channel; Relay
remains a fan-control option that becomes installable only when
the full chain — `PRODUCT-RELAY-001` + `WEBFLASH-RELAY-001` (with
its production-wide / installation / competent-person sign-off
gates) + `RELEASE-RELAY-001` + WebFlash-side
`WF-IMPORT-RELAY-001` — has cleared.

**2026-05-22 — `PRODUCT-RELAY-001` status update (PR #564;
implementation slice).** `PRODUCT-RELAY-001` **landed** as a
product-YAML-only / no-WebFlash-exposure slice. The canonical
FanRelay product YAML
[`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml)
is committed alongside a non-WebFlash catalog row in
[`config/product-catalog.json`](../config/product-catalog.json)
(config string `Ceiling-POE-VentIQ-FanRelay-RoomIQ`, `status:
hardware-pending`, `webflash_build_matrix: false`, no
`artifact_name`, no `webflash_wrapper`, no entry in
[`config/webflash-builds.json`](../config/webflash-builds.json),
not in `release_one_required_configs`). The product YAML carries
explicit advanced / manual-warning + installation / safety +
competent-person caveat wording per the readiness-refresh
recommended posture; the structural pins are recorded in
[`tests/test_relay_product_readiness.py`](../tests/test_relay_product_readiness.py).
**The Relay Bathroom Kit still remains `future-expansion` /
`hardware-pending` and `webflash_exposure_allowed_now: false` /
`stable_ready_now: false`** — `PRODUCT-RELAY-001` lands the
product YAML only and explicitly does **not** add a WebFlash
wrapper, build-matrix row, release artifact, or kit promotion.
`WEBFLASH-RELAY-001`, `RELEASE-RELAY-001`, and
`WF-IMPORT-RELAY-001` remain **blocked** behind production-wide
hardware characterisation + installation / safety wording +
competent-person sign-off + WebFlash-side manual-warning UX
parity. The default sellable bathroom kit remains
`S360-KIT-BATH-POE` mapped to Release-One on `stable`. Relay
becomes installable only via the full chain
`WEBFLASH-RELAY-001` → `RELEASE-RELAY-001` →
`WF-IMPORT-RELAY-001`.

**2026-05-22 — `WEBFLASH-RELAY-001-READINESS-REFRESH` status
update (this PR; docs-only).** Re-evaluated the Relay Bathroom
Kit posture after `PRODUCT-RELAY-001` / PR #564 landed the
FanRelay product YAML without WebFlash exposure. Re-verified
against the live files: the
[`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json)
`S360-KIT-BATH-RELAY` row stays byte-identical
(`tier: future-expansion`, `lifecycle_status: hardware-pending`,
`default_config_string: null`, `webflash_exposure_allowed_now:
false`, `stable_ready_now: false`); the
[`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json)
lane `fanrelay-blocked-package-or-core-bus` count stays at 36
(reclassification from `missing-product-yaml` to
`blocked-hardware` was performed by PRODUCT-RELAY-001 / PR #564,
not by this readiness refresh); no kit / preset / bundle
configuration is added on either side of the cross-repo boundary.
**The Relay Bathroom Kit now has a product YAML upstream** (the
PRODUCT-RELAY-001 catalog row above) but **still has no WebFlash
exposure and is still not default** — neither
`webflash_exposure_allowed_now` nor `stable_ready_now` flips,
neither `S360-KIT-BATH-RELAY` nor any `Ceiling-POE-VentIQ-FanRelay-*`
config-string enters the WebFlash build matrix, and the kit
remains `future-expansion` / `hardware-pending`. **The default
sellable kit remains `S360-KIT-BATH-POE`** mapped to Release-One
`Ceiling-POE-VentIQ-RoomIQ` on the `stable` channel; the LED
preview kit remains `S360-KIT-BATH-POE-LED` on the `preview`
channel; FanTRIAC stays `blocked` / `HW-005`. The cross-repo
WebFlash Stage 1 bundle preset
[`scripts/data/kit-presets.js`](https://github.com/sense360store/WebFlash/blob/main/scripts/data/kit-presets.js)
`S360-KIT-BATH-RELAY` entry stays `status: planned` / `badge:
Planned` / `firmwareConfigString: null` /
`notAvailableReason: "Awaiting upstream RELEASE-RELAY-001
firmware import (WF-IMPORT-RELAY-001)."` — the WebFlash repo's
kit-preset surface and the in-Step-4 outcome-first label
"Fan relay control" remain aligned with this kit-intent matrix
and the WebFlash-side `WF-IMPORT-RELAY-001` queue item stays
blocked behind upstream `RELEASE-RELAY-001`. **No
[`config/`](../config/) edit (the live blocker token list in
[`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json)
still mirrors the pre-refresh state; the config-edit PR
refreshing it to drop the landed `CORE-ABSTRACT-BUS-001C` /
`CORE-ABSTRACT-BUS-001A` / `PACKAGE-RELAY-001` / `PRODUCT-RELAY-001`
blockers is still owed separately); no `packages/**`, `products/**`,
`products/webflash/**`, `scripts/**`, `.github/workflows/**`,
`components/**`, `include/**`, `firmware/**`, `manifest.json`,
`firmware/sources.json`, `tests/**`, WebFlash repo edit; no
`webflash_build_matrix` flip; no `artifact_name`; no
`webflash_wrapper`; no `release_one_required_configs` change; no
COMPLIANCE-001 movement; no `schematic_status` / `schematic_file`
promotion** (`S360-310` stays `cataloged_unverified`). **No claim
of FanRelay WebFlash-readiness, release-readiness,
compliance-clearance, kit-default-readiness, recommended-bundle
readiness, board-level mains-safety certification,
installation-approval, qualified-electrician sign-off, or
production-wide / multi-unit hardware characterisation.** The
recommended next Relay-chain PR is one of `WEBFLASH-RELAY-001`
implementation plan / scaffold only (if allowed by the project
lead), `RELEASE-RELAY-001` (blocked until artifact path exists),
or `FW-COMPILE-RELAY-001` (if compile-only validation should
happen first); none of those promotes the Relay Bathroom Kit on
either side of the cross-repo boundary.

### S360-KIT-BATH-TRIAC — Sense360 Bathroom Kit — TRIAC Fan Control

- **Tier.** `advanced-manual`
- **Lifecycle status.** `blocked`
- **Default firmware config string.** (none committed)
- **Recommended fan module.** FanTRIAC / S360-320
- **Firmware matrix lane.** `fantriac-blocked-hardware-compliance`
- **WebFlash exposure allowed now?** no
- **Stable-ready now?** no
- **Blockers.** `HW-005`, `HW-PINMAP-320-FOLLOWUP`,
  `PACKAGE-TRIAC-001`, `COMPLIANCE-001`

Advanced / manual bathroom bundle using the FanTRIAC driver
(S360-320) for mains-voltage fan dimming. Of the four blocker tokens
kept for history: **HW-005** and **HW-PINMAP-320-FOLLOWUP** are
resolved (TRIAC-PINMAP-CORRECT-001); **PACKAGE-TRIAC-001** remains
open until the signed operator attestation is committed; and
**COMPLIANCE-001** is CLOSED by market posture per
`COMPLIANCE-001-RESOLUTION-001` (S360-320 is never placed on the
market), so its element now denotes that record's experimental-lane
preconditions. FanTRIAC stays advanced / manual or blocked, and per
the resolution an experimental build is never in the kit picker.

### S360-KIT-DUCT-PWM — Sense360 Duct Fan Kit — PWM Fan Control

- **Tier.** `future-expansion`
- **Lifecycle status.** `hardware-pending`
- **Default firmware config string.** (none committed)
- **Recommended fan module.** FanPWM / S360-311
- **Firmware matrix lane.** `fanpwm-blocked-package-or-core-bus`
- **WebFlash exposure allowed now?** no
- **Stable-ready now?** no
- **Blockers.** `CORE-ABSTRACT-BUS-001B`, `PACKAGE-PWM-001`,
  `PRODUCT-PWM-001`, `WEBFLASH-PWM-001`, `RELEASE-PWM-001`

Future kitchen / duct-fan bundle using the 12V PWM fan driver
(S360-311). PWM is **not** a default bathroom option — this is an
advanced duct-fan / kitchen-style concept. Implementation chain runs
CORE-ABSTRACT-BUS-001B → PACKAGE-PWM-001 → PRODUCT-PWM-001 →
WEBFLASH-PWM-001 → RELEASE-PWM-001 per the FanPWM lane in
[`docs/firmware-build-gap-report.md`](firmware-build-gap-report.md).

### S360-KIT-DUCT-0-10V — Sense360 Duct Fan Kit — 0–10V Fan Control

- **Tier.** `future-expansion`
- **Lifecycle status.** `hardware-pending`
- **Default firmware config string.** (none committed)
- **Recommended fan module.** FanDAC / S360-312
- **Firmware matrix lane.** `fandac-blocked-package-or-core-bus`
- **WebFlash exposure allowed now?** no
- **Stable-ready now?** no
- **Blockers.** `CORE-ABSTRACT-BUS-001B`, `PACKAGE-DAC-001`,
  `PRODUCT-DAC-001`, `WEBFLASH-DAC-001`, `RELEASE-DAC-001`

Future kitchen / duct-fan bundle using the 0–10V (GP8403 I²C DAC)
fan driver (S360-312). 0–10V is **not** a default bathroom option —
this is an advanced duct-fan / kitchen-style concept. The grammar in
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
forbids FanDAC + AirIQ, so FanDAC-bearing combinations live entirely in
the duct-fan space. Implementation chain runs CORE-ABSTRACT-BUS-001B →
PACKAGE-DAC-001 → PRODUCT-DAC-001 → WEBFLASH-DAC-001 →
RELEASE-DAC-001 per the FanDAC lane in
[`docs/firmware-build-gap-report.md`](firmware-build-gap-report.md).

> **Status note (2026-05-23 — `PRODUCT-DAC-001-READINESS-REFRESH`).**
> The two earliest chain links have now landed at their own layer:
> `CORE-ABSTRACT-BUS-001B` (the `core_i2c` shared-bus rename) merged as
> **PR #569**, and `PACKAGE-DAC-001` (the FanDAC dual-GP8403 package —
> two chips, four neutral outputs, per-chip address + range
> substitutions) merged as **PR #573**. The `blockers` list above is
> the canonical [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json)
> array and is unchanged by this docs refresh. **The kit stays
> `future-expansion` / `hardware-pending` and gated** — a package-layer
> landing is not product, WebFlash, or release readiness. Before
> `PRODUCT-DAC-001` can add a FanDAC product YAML, the recommended next
> link is **`FW-COMPILE-DAC-001`** (compile-only validation): the
> package binds the `gp8403:` `voltage:` field to the neutral `0-10V`
> value rather than ESPHome's bare `10V` / `5V` enum, and with no FanDAC
> compile-only target this is **unvalidated**. So the live chain is
> CORE-ABSTRACT-BUS-001B *(PR #569)* → PACKAGE-DAC-001 *(PR #573)* →
> **FW-COMPILE-DAC-001** → PRODUCT-DAC-001 → WEBFLASH-DAC-001 →
> RELEASE-DAC-001. No `webflash_build_matrix`, `artifact_name`, kit
> config string, or readiness flag is changed here.

> **Status note (2026-05-23 — `PRODUCT-DAC-001`).** Two further chain
> links have since landed: `FW-COMPILE-DAC-001` (compile-only target +
> `gp8403:` `voltage:` `0-10V` → ESPHome `10V` enum fix) merged as
> **PR #575**, `FW-COMPILE-DAC-RESULT-001` recorded the compile-only
> **metadata** lane green as **PR #576**, and **`PRODUCT-DAC-001`** (this
> PR) added the canonical FanDAC product YAML
> [`products/sense360-ceiling-poe-fandac.yaml`](../products/sense360-ceiling-poe-fandac.yaml)
> (config string `Ceiling-POE-FanDAC`) as **product-YAML-only /
> no-WebFlash-exposure** with a `hardware-pending`
> [`config/product-catalog.json`](../config/product-catalog.json) row
> (`webflash_build_matrix: false`, no `artifact_name`, no wrapper). **The
> kit stays `future-expansion` / `hardware-pending` and gated** — a
> product-layer YAML is not WebFlash or release readiness, and the full
> ESPHome `--compile` pass is still **owed** (only the compile-only
> metadata lane is green). `WEBFLASH-DAC-001` and `RELEASE-DAC-001` stay
> blocked. The `blockers` array above is the canonical
> [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json)
> array and is unchanged by this docs refresh; no kit config string or
> readiness flag is changed. Recommended next link before
> `WEBFLASH-DAC-001`: `FW-COMPILE-DAC-FULL-001` (record the owed manual
> `workflow_dispatch` `compile_mode=full` compile) or
> `WEBFLASH-DAC-001-READINESS-REFRESH`.

## Hard guardrails

The kit intent matrix is a **planning artifact**. It does not change:

- [`config/webflash-builds.json`](../config/webflash-builds.json)
- [`config/product-catalog.json`](../config/product-catalog.json)
- [`config/hardware-catalog.json`](../config/hardware-catalog.json)
- [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
- [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json)
- [`docs/firmware-build-gap-report.md`](firmware-build-gap-report.md)
- `products/**`
- `products/webflash/**`
- `packages/**`
- `firmware/**`
- `manifest.json`
- `firmware/sources.json`
- `.github/workflows/**`
- release artifacts, checksums, or build-info manifests

It does not:

- add product YAMLs,
- add WebFlash wrappers,
- add `webflash_build_matrix: true`,
- add `artifact_name`,
- promote LED to stable,
- promote `PWR` / `S360-400`,
- promote `POE` / `S360-410`,
- promote any fan module,
- claim hardware proof exists,
- claim `RELEASE-007` is unblocked,
- claim WebFlash import is ready.

## See also

- [`docs/firmware-combination-matrix.md`](firmware-combination-matrix.md) — FW-MATRIX-001, the 168-row source matrix this file rolls up.
- [`docs/firmware-build-gap-report.md`](firmware-build-gap-report.md) — FW-MATRIX-002, the priority-lane lens that the `firmware_matrix_lane` field points back to.
- [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md) — the 17-row stable-promotion gauntlet that the LED preview kit must clear before its `stable_ready_now` flag can flip.
- [`docs/product-readiness-matrix.md`](product-readiness-matrix.md) — PRODUCT-GAP-001, product-layer readiness this kit-intent view consults.
- [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md) — WEBFLASH-GAP-001, WebFlash-exposure readiness.
- [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md) — RELEASE-GAP-001, release-artifact readiness.
- [`docs/webflash-contract.md`](webflash-contract.md) — canonical config-string grammar.

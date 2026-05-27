# Product YAML Readiness Matrix (PRODUCT-GAP-001)

## Purpose and scope

This document is the canonical, **product-level** readiness gate for
the missing-module product combinations that PRODUCT-GAP-001 covers —
the FanRelay / FanPWM / FanDAC / FanTRIAC / PWR-240V / PoE-410 product
families that have at least one verified package or evidenced
hardware path on file but are **not** today represented by a
WebFlash-shippable product YAML. It records, per candidate product
family, the current package-evidence state, the WebFlash compatibility
grammar verdict, the allowed action right now, and the named follow-up
PR that owns each family's product slice.

PRODUCT-GAP-001 exists because the original backlog row — *"add
product YAMLs for evidenced module combinations"* — must be gated
against actual package evidence. The
[`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
verdict is unambiguous: **no in-scope package is
`ready-for-package-change` today**. Every fan-driver and power package
that any new product YAML would consume carries at least one of
`schematic-evidence-pending`, `needs-package-reconciliation`,
`bench-evidence-pending`, `timing/compliance-pending`,
`reference-only`, `do-not-change-release-one`, or
`blocked-from-standard-exposure`. Therefore this document is the
explicit **implementation gate** for PRODUCT-GAP-001: it classifies
each candidate product family, names the follow-up PR that must
produce the missing evidence, and **forbids** any product YAML edit
or addition in this PR.

This document is **documentation only**. It does **not**:

- add, remove, or modify any product YAML under
  [`products/`](../products/), including the existing production
  Release-One product
  [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml),
  the LED preview
  [`products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq-led.yaml),
  the blocked FanTRIAC reference
  [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml),
  the legacy four-channel PWM accessory
  [`products/sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml),
  the legacy PoE network controller
  [`products/sense360-poe.yaml`](../products/sense360-poe.yaml),
  the `legacy-compatible` Core / Core-Voice / Mini family, or any
  other product YAML in the tree,
- add, remove, or modify any WebFlash wrapper under
  [`products/webflash/`](../products/webflash/), including the
  production wrapper
  [`products/webflash/ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml),
  the preview wrapper
  [`products/webflash/ceiling-poe-ventiq-roomiq-led.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq-led.yaml),
  and the blocked reference wrapper
  [`products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml),
- add, remove, or modify any package YAML under
  [`packages/`](../packages/) — including the six packages tracked
  by [`package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
  ([`fan_relay.yaml`](../packages/expansions/fan_relay.yaml),
  [`fan_pwm.yaml`](../packages/expansions/fan_pwm.yaml),
  [`fan_gp8403.yaml`](../packages/expansions/fan_gp8403.yaml),
  [`fan_triac.yaml`](../packages/expansions/fan_triac.yaml),
  [`power_240v.yaml`](../packages/hardware/power_240v.yaml),
  [`power_poe.yaml`](../packages/hardware/power_poe.yaml)) plus the
  legacy four-channel
  [`packages/expansions/sense360_fan_pwm.yaml`](../packages/expansions/sense360_fan_pwm.yaml),
  the Core abstract packages
  [`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml)
  and
  [`packages/hardware/sense360_core.yaml`](../packages/hardware/sense360_core.yaml),
  and every other package in the tree,
- add, remove, or modify any entry in
  [`config/hardware-catalog.json`](../config/hardware-catalog.json),
  [`config/product-catalog.json`](../config/product-catalog.json),
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  or
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json) —
  no new product entry, no `lifecycle_statuses` value, no
  `canonical_modules` token, no `release_one_required_configs` change,
  no build-matrix entry, no `webflash_build_matrix` flip,
- add, remove, or modify any script under
  [`scripts/`](../scripts/), any test under
  [`tests/`](../tests/), any workflow under `.github/workflows/`, any
  component under `components/`, any include under `include/`, or
  any firmware artifact under `firmware/`,
- generate, regenerate, sign, import, deploy, or otherwise produce
  firmware; create or modify any GitHub Release; or change any
  WebFlash-side `REQUIRED_CONFIGS`, `scripts/data/kits.json`,
  `firmware/sources.json`, or `manifest.json` entry,
- mark any candidate product family `ready-for-product-yaml`, flip
  any catalog `status`, promote any `preview` entry to `production`,
  add any entry to or remove any entry from Release-One
  REQUIRED_CONFIGS, add any kit, or move any `legacy-compatible`
  entry off `legacy-compatible`,
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

## Core rule

> **Product YAML changes are allowed only when (a) every package the
> product would consume is `ready-for-package-change` per
> [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md),
> (b) the combination is permitted by the WebFlash compatibility
> grammar in
> [`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
> and (c) the
> [`docs/product-onboarding.md`](product-onboarding.md) safe
> sequence is followed end-to-end. Package readiness, product
> readiness, and WebFlash exposure are three separate gates; product
> YAML existence does not itself authorise WebFlash exposure.**

This is the load-bearing premise of PRODUCT-GAP-001. It is the
product-level form of the
[`package-readiness-matrix.md` Core rule](hardware/package-readiness-matrix.md#core-rule)
("package YAML changes are allowed only when the target board has
verified pin-map evidence") and of the
[`product-availability-taxonomy.md` Core rule](product-availability-taxonomy.md#core-rule)
("hardware evidence does not equal firmware support, product
support, or WebFlash availability"). Any PR that argues "this
combination is plausible / requested / referenced in the wizard,
therefore this product YAML may be added" without supplying the named
PACKAGE-*-001 evidence is breaking the rule and must be rejected on
first read.

Two corollaries follow:

- A `ready-for-package-change` verdict on **one** required package
  is **not** product readiness. A new product YAML consumes a stack
  of packages; **every** package in the stack must be ready, the
  Core abstract-bus values consumed by the stack must be rebound
  (CORE-ABSTRACT-BUS-001), and the resulting product must validate
  against the WebFlash compatibility grammar before any new
  product YAML may be added.
- Adding a product YAML is **not** the same as exposing the product
  via WebFlash. WebFlash exposure requires, in order: a WebFlash
  wrapper under [`products/webflash/`](../products/webflash/), a
  catalog entry in
  [`config/product-catalog.json`](../config/product-catalog.json),
  a build-matrix entry in
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  a release artifact, and a WebFlash-side import. Each of those is
  a separate gate — see [WebFlash exposure gates](#webflash-exposure-gates)
  and the [Follow-up PR sequence](#follow-up-pr-sequence) below.

## Status value vocabulary (policy-only)

The product readiness table below uses a small set of cell values.
**All are policy-only labels** — they are not JSON enums, not
promoted to any schema, and not added to any validator by this PR.
They sit alongside the existing
[`config/product-catalog.json`](../config/product-catalog.json)
`lifecycle_statuses`
(`production` / `preview` / `compile-only` / `hardware-pending` /
`blocked` / `legacy-compatible` / `deprecated` / `removed`), the
[`product-availability-taxonomy.md`](product-availability-taxonomy.md)
13-rung ladder, and the
[`package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
labels which this matrix consumes for the "Package readiness"
column.

| Cell value | Meaning |
|---|---|
| `ready-for-product-yaml` | A canonical product YAML may be added now. Requires (a) every required package `ready-for-package-change` per [`package-readiness-matrix.md`](hardware/package-readiness-matrix.md); (b) the combination passes [`config/webflash-compatibility.json`](../config/webflash-compatibility.json) (mounting / power / module set / mutex rules / no `forbidden_tokens`); (c) CORE-ABSTRACT-BUS-001 rebind landed where the product consumes the Ceiling Core abstract package; (d) PRODUCT-AVAIL-001 ladder rung `product-yaml-ready` is achievable. **No candidate product in this matrix carries this label today.** |
| `needs-package-reconciliation` | The product's required package(s) are known to disagree with schematic-backed evidence at a specific, named point and carry `needs-package-reconciliation` in [`package-readiness-matrix.md`](hardware/package-readiness-matrix.md). The fix is the named PACKAGE-*-001 slice (FanRelay / FanPWM / FanDAC / FanTRIAC / PWR-240V / PoE-410); only **after** that slice lands may the matching PRODUCT-*-001 slice add a product YAML. **Not** approval to add a product YAML in this PR. |
| `schematic-evidence-pending` | The product cannot be reconciled at all because at least one required module-side `S360-*-R4` schematic is not committed (catalog `schematic_status: cataloged_unverified`, no `schematic_file` set). The HW-ASSETS-310 / HW-ASSETS-400 / HW-ASSETS-410 supplier-delivery follow-ups precede any product addition. |
| `hardware-evidence-pending` | The product cannot be added until bench / silkscreen / harness / waveform evidence is owed against at least one required board (e.g. PWM polarity, tach pull-up, DIP-switch I²C address, zero-cross waveform, dimmer real-load proof). Owned by the named HW-PINMAP-*-FOLLOWUP plus bench evidence (S360-100-BENCH-001 etc.). |
| `timing/compliance-pending` | The product cannot be added because timing-correctness or mains-voltage compliance evidence is owed. Applies to FanTRIAC (`ac_dimmer` ISR timing + COMPLIANCE-001) and to PWR-240V (COMPLIANCE-001). |
| `advanced/manual-warning-only` | The product family, when it eventually lands, is to be reachable only through an advanced / manual-warning surface — never via the standard WebFlash flow, REQUIRED_CONFIGS, recommended lists, kits, or default offerings. Today this applies only to FanTRIAC; the long-term posture is documented in [`docs/hardware/s360-320-r4-triac.md` Advanced / manual-warning product posture](hardware/s360-320-r4-triac.md#advanced--manual-warning-product-posture) and is **intent only** until HW-005 / COMPLIANCE-001 / HW-PINMAP-320-FOLLOWUP / PACKAGE-TRIAC-001 clear. |
| `blocked-from-standard-exposure` | The product family must not be added to Release-One, REQUIRED_CONFIGS, recommended / kit / default lists, or compliance-certified surfaces, regardless of any future product YAML existence. Carried alongside `advanced/manual-warning-only` where applicable; the JSON `status` for any existing blocked reference (FanTRIAC) stays unchanged. |
| `not-webflash-default` | Even after package readiness, the product family's first product YAML will **not** flip `webflash_build_matrix: true` by default and will **not** appear on the standard WebFlash flasher landing list. The wrapper / catalog / build-matrix promotion is a separately gated WEBFLASH-GAP-001 step. |
| `not-recommended` / `not-required-configs` / `not-kit` | Additive qualifiers that constrain a future product's WebFlash exposure class even after `ready-for-product-yaml`. Used today for FanTRIAC to make the long-term posture explicit. |
| `legacy-only` | The product YAML for this family already exists under [`products/`](../products/) as a `legacy-compatible` entry (today: the legacy four-channel [`products/sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml) and the legacy PoE-controller [`products/sense360-poe.yaml`](../products/sense360-poe.yaml)). The entry is consumed manually and is **not** in the WebFlash build matrix; PRODUCT-GAP-001 does not move it off `legacy-compatible` and does not add a non-legacy sibling for it. |
| `invalid-combination` | The combination is forbidden by the WebFlash compatibility grammar in [`config/webflash-compatibility.json`](../config/webflash-compatibility.json) (AirIQ ↔ VentIQ mutex, FanDAC ↔ AirIQ mutex, generic `Fan` token forbidden, fan variants firmware-distinct, `forbidden_tokens` `Bathroom` / `Comfort` / `Presence` / `Fan` / `FanAnalog`). No product YAML may add it regardless of any package readiness verdict. |
| `unknown` | Cannot be classified from currently committed evidence. Not used in this matrix today; every candidate family below is placeable under the labels above. |

A row may carry one primary label plus one or more additive qualifier
labels (e.g. `timing/compliance-pending` +
`needs-package-reconciliation` + `blocked-from-standard-exposure` +
`advanced/manual-warning-only` + `not-recommended` +
`not-required-configs` + `not-kit` + `not-webflash-default` for
FanTRIAC).

## Current product surface

The current product surface — taken verbatim from
[`config/product-catalog.json`](../config/product-catalog.json) — is:

- **1 `production` entry** —
  `Ceiling-POE-VentIQ-RoomIQ` (Release-One). Version `1.0.0`,
  channel `stable`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`,
  `webflash_build_matrix: true`, the only entry on
  `release_one_required_configs` in
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json).
  Canonical YAML
  [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml);
  wrapper
  [`products/webflash/ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml).
  Carries `blocked_modules: [FanTRIAC, LED]`.
- **1 `preview` entry** —
  `Ceiling-POE-VentIQ-RoomIQ-LED`. Version `1.0.0`, channel
  `preview`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`,
  `webflash_build_matrix: true`. Canonical YAML
  [`products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq-led.yaml);
  wrapper
  [`products/webflash/ceiling-poe-ventiq-roomiq-led.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq-led.yaml).
  Carries `blocked_modules: [FanTRIAC]`. Bench-verification Open
  Questions in [`docs/hardware/s360-300-r4-led.md`](hardware/s360-300-r4-led.md)
  remain carried as preview-stage caveats.
- **1 `blocked` reference entry** —
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`, `blocker: HW-005`,
  `webflash_build_matrix: false`. Canonical YAML
  [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml)
  retained with placeholder
  `fan_triac_gate_pin: GPIO5` / `fan_triac_zc_pin: GPIO6`
  (parse-only; both pins already claimed by RoomIQ J10); wrapper
  [`products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml)
  retained with BLOCKED banner. Not on the WebFlash build matrix.
- **31 `legacy-compatible` entries**, all
  `webflash_build_matrix: false` (no `config_string`, no
  `webflash_wrapper`, no `artifact_name`):
  - **Core family (4 variants)** — `sense360-core-c-poe.yaml`,
    `sense360-core-c-pwr.yaml`, `sense360-core-c-usb.yaml`,
    plus the combined `sense360-core-ceiling.yaml`,
    `sense360-core-ceiling-bathroom.yaml`,
    `sense360-core-ceiling-presence.yaml`.
  - **Core wall family** — `sense360-core-w-poe.yaml`,
    `sense360-core-w-pwr.yaml`, `sense360-core-w-usb.yaml`,
    plus `sense360-core-wall.yaml`,
    `sense360-core-wall-presence.yaml`.
  - **Core Voice family** — `sense360-core-v-c-poe.yaml`,
    `sense360-core-v-c-pwr.yaml`, `sense360-core-v-c-usb.yaml`,
    `sense360-core-v-w-poe.yaml`,
    `sense360-core-v-w-pwr.yaml`, `sense360-core-v-w-usb.yaml`,
    plus `sense360-core-voice-ceiling.yaml`,
    `sense360-core-voice-wall.yaml`.
  - **Mini family (9 variants)** —
    `sense360-mini-airiq.yaml`,
    `sense360-mini-airiq-basic.yaml`,
    `sense360-mini-airiq-advanced.yaml`,
    `sense360-mini-airiq-ld2412.yaml`,
    `sense360-mini-full-ld2412.yaml`,
    `sense360-mini-presence.yaml`,
    `sense360-mini-presence-basic.yaml`,
    `sense360-mini-presence-advanced.yaml`,
    `sense360-mini-presence-advanced-ld2412.yaml`,
    `sense360-mini-presence-basic.yaml`,
    `sense360-mini-presence-ld2412.yaml`.
  - **Standalone legacy** —
    [`products/sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml)
    (legacy single-purpose four-channel fan-PWM accessory; consumes
    [`packages/expansions/sense360_fan_pwm.yaml`](../packages/expansions/sense360_fan_pwm.yaml)),
    [`products/sense360-poe.yaml`](../products/sense360-poe.yaml)
    (legacy single-purpose PoE network controller).

Every legacy-compatible entry stays `legacy-compatible` for the
duration of PRODUCT-GAP-001 and remains out of the WebFlash build
matrix.

## Candidate product families

PRODUCT-GAP-001 considers six candidate product families derived
from the six in-scope boards in
[`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
and the six in-scope packages in
[`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md):

- **FanRelay** — products consuming
  [`packages/expansions/fan_relay.yaml`](../packages/expansions/fan_relay.yaml)
  (S360-310 Sense360 Relay). Candidate shape:
  `Ceiling-{POWER}-{AIR}-FanRelay-{ROOM}`.
- **FanPWM** — products consuming
  [`packages/expansions/fan_pwm.yaml`](../packages/expansions/fan_pwm.yaml)
  (S360-311 Sense360 PWM). Candidate shape:
  `Ceiling-{POWER}-{AIR}-FanPWM-{ROOM}`. The legacy four-channel
  product [`products/sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml)
  remains `legacy-compatible` and is **not** the FanPWM candidate.
- **FanDAC** — products consuming
  [`packages/expansions/fan_gp8403.yaml`](../packages/expansions/fan_gp8403.yaml)
  (S360-312 Sense360 DAC). Candidate shape:
  `Ceiling-{POWER}-FanDAC-{ROOM}` (FanDAC is mutually exclusive
  with AirIQ — see
  [Compatibility constraints](#compatibility-constraints)).
- **FanTRIAC** — products consuming
  [`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml)
  (S360-320 Sense360 TRIAC). The blocked reference entry
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` already exists as the
  canonical placeholder; PRODUCT-GAP-001 adds **no** sibling and
  does **not** flip its status.
- **PWR-240V** — products consuming
  [`packages/hardware/power_240v.yaml`](../packages/hardware/power_240v.yaml)
  (S360-400 Sense360 240v PSU) on the WebFlash-shippable surface.
  The four `legacy-compatible` `*-pwr` Core variants already
  consume this package manually; the candidate shape here would be
  `Ceiling-PWR-{AIR}-{ROOM}` on the WebFlash surface, which does
  **not** exist today.
- **PoE-410** — products consuming
  [`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml)
  (S360-410 Sense360 PoE PSU) as the explicit module-side board
  rather than the logical-only role Release-One already consumes
  under the preserved schematic-pending caveat. No PoE-410
  candidate product is added; the package remains `reference-only`
  + `do-not-change-release-one`.

No additional candidate family (e.g. `FanAnalog`, `Bathroom`,
`Comfort`, `Presence`, generic `Fan`) is considered, because
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
lists them under `forbidden_tokens` or does not promote them to
`canonical_modules`.

## Compatibility constraints

[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
defines the rules every candidate product must clear:

- **`canonical_modules`** —
  `["AirIQ", "VentIQ", "RoomIQ", "FanRelay", "FanPWM", "FanDAC",
  "FanTRIAC", "LED"]`. No new module token may be added by
  PRODUCT-GAP-001.
- **`canonical_mounting`** — `["Ceiling"]`. No wall- or
  hand-mount surface is in scope for the WebFlash build matrix.
- **`canonical_power`** — `["USB", "POE", "PWR"]`. `USB` and `PWR`
  are not exercised by any current `webflash_build_matrix: true`
  entry.
- **`forbidden_tokens`** —
  `["Bathroom", "Comfort", "Presence", "Fan", "FanAnalog"]`. Any
  candidate product YAML that introduces one of these in its
  config string is `invalid-combination`.
- **Rules**:
  - `airiq_and_ventiq_mutually_exclusive: true` — no product may
    carry both `AirIQ` and `VentIQ`.
  - `roomiq_can_pair_with_airiq: true` and
    `roomiq_can_pair_with_ventiq: true` — `RoomIQ` is independent
    of the air-quality token.
  - `fan_variants_are_firmware_distinct: true` — `FanRelay` /
    `FanPWM` / `FanDAC` / `FanTRIAC` each produce a different
    firmware binary; no combined "fan" surface exists.
  - `generic_fan_token_forbidden: true` — only the four specific
    tokens above are allowed; the bare `Fan` token is forbidden.
  - `fandac_conflicts_with_airiq: true` — any
    `Ceiling-{POWER}-AirIQ-FanDAC-*` proposal is
    `invalid-combination` regardless of any future S360-312 /
    S360-210 package readiness.
- **`release_one_required_configs`** —
  `["Ceiling-POE-VentIQ-RoomIQ"]`. PRODUCT-GAP-001 adds nothing
  here; REQUIRED_CONFIGS changes are owned by
  [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
  §`REQUIRED_CONFIGS policy` and require an explicit RELEASE-006
  promotion. FanTRIAC explicitly cannot enter REQUIRED_CONFIGS
  even after PACKAGE-TRIAC-001 lands — see
  [Per-family status →
  FanTRIAC / S360-320](#fantriac--s360-320).
- **`artifact_pattern`** —
  `Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin`. Verified by
  [`tests/test_webflash_artifact_naming.py`](../tests/test_webflash_artifact_naming.py).

Combinations marked `invalid-combination` upfront, before any
package readiness verdict:

- Any product carrying both `AirIQ` and `VentIQ` —
  `airiq_and_ventiq_mutually_exclusive`.
- Any product carrying both `AirIQ` and `FanDAC` —
  `fandac_conflicts_with_airiq`.
- Any product carrying more than one fan variant in the same
  config string — `fan_variants_are_firmware_distinct` (each fan
  driver is a separate firmware binary).
- Any product carrying a `forbidden_tokens` value (`Bathroom`,
  `Comfort`, `Presence`, `Fan`, `FanAnalog`).
- Any product using a `canonical_mounting` value other than
  `Ceiling` or a `canonical_power` value outside
  `{USB, POE, PWR}`.

## Product readiness table

**No candidate product family is `ready-for-product-yaml` today.**
Every row below carries at least one of `needs-package-reconciliation`,
`schematic-evidence-pending`, `hardware-evidence-pending`,
`timing/compliance-pending`, `reference-only`,
`blocked-from-standard-exposure`, or
`do-not-change-release-one`. The follow-up PR sequence in
[Follow-up PR sequence](#follow-up-pr-sequence) records the named
per-family slices that must each be a separate scoped PR with its
own gate evidence.

| Candidate product / family | Modules | Power path | Required packages | Compatibility status | Package readiness | Product YAML action now | WebFlash exposure class | Follow-up owner |
|---|---|---|---|---|---|---|---|---|
| `Ceiling-POE-VentIQ-FanRelay-RoomIQ` (FanRelay slice) | `VentIQ` + `FanRelay` + `RoomIQ` | POE (S360-410) | [`fan_relay.yaml`](../packages/expansions/fan_relay.yaml) + Core abstract + RoomIQ + VentIQ + [`power_poe.yaml`](../packages/hardware/power_poe.yaml) | grammar-clean (no mutex hit, no forbidden token) | [`fan_relay.yaml`](../packages/expansions/fan_relay.yaml): **`package-implemented` + `reconciled-at-package-layer`** (PACKAGE-RELAY-001 / PR #562; tests pin via [`tests/test_fan_relay_package.py`](../tests/test_fan_relay_package.py); package-evidence layer populated by `S360-310-BENCH-EVIDENCE-001` / PR #561 from operator-attested + BOM-backed + public-reference-backed sources, no photo / video / oscilloscope / continuity-meter artifacts); Core abstract: `relay_pin: GPIO3` post-`CORE-ABSTRACT-BUS-001A` / PR #558 (the `GPIO3` collision was resolved by `CORE-ABSTRACT-BUS-001C` / PR #557); voice-variant Core packages stay at pre-001A `relay_pin: GPIO4` (out of scope) | **`PRODUCT-RELAY-001` landed (this PR)** as product-YAML-only / no-WebFlash-exposure. Canonical FanRelay product YAML [`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml) committed; non-WebFlash catalog row added (`status: hardware-pending`, `webflash_build_matrix: false`, no `artifact_name`, no `webflash_wrapper`); product YAML carries explicit advanced / manual-warning + installation / safety + competent-person caveat wording; structural pins in [`tests/test_relay_product_readiness.py`](../tests/test_relay_product_readiness.py). Product-layer disposition remains `advanced/manual-warning-only` + WebFlash-blocked; `not-required-configs` + `not-recommended` + `not-kit-default`. | `none` (not in build matrix; not in REQUIRED_CONFIGS; not on landing list); long-term posture is `advanced/manual-warning-only` (never standard, never recommended, never kit / default), not `preview-candidate` | `HW-ASSETS-310` → `HW-PINMAP-310-FOLLOWUP` → `CORE-ABSTRACT-BUS-001C` / PR #557 → `CORE-ABSTRACT-BUS-001A` / PR #558 → `PACKAGE-RELAY-001-READINESS-REFRESH` / PR #559 → `S360-310-BENCH-001` / PR #560 → `S360-310-BENCH-EVIDENCE-001` / PR #561 → `PACKAGE-RELAY-001` / PR #562 → `PRODUCT-RELAY-001-READINESS-REFRESH` / PR #563 → **`PRODUCT-RELAY-001`** *(this PR — product YAML only; no WebFlash wrapper / catalog flip / build-matrix entry / release artifact)* → `WEBFLASH-RELAY-001-READINESS-REFRESH` (recommended next; readiness re-evaluation after PRODUCT-RELAY-001 lands) → `WEBFLASH-RELAY-001` → `RELEASE-RELAY-001` → `WF-IMPORT-RELAY-001` |
| `Ceiling-POE-VentIQ-FanPWM-RoomIQ` (FanPWM slice) | `VentIQ` + `FanPWM` + `RoomIQ` | POE (S360-410) | [`fan_pwm.yaml`](../packages/expansions/fan_pwm.yaml) + Core abstract + RoomIQ + VentIQ + [`power_poe.yaml`](../packages/hardware/power_poe.yaml) | grammar-clean | [`fan_pwm.yaml`](../packages/expansions/fan_pwm.yaml): **`package-layer-implemented` (PWM-drive-only)** (PACKAGE-PWM-001-IMPLEMENT-001 / PR #590; four SX1509 PWM-drive controllers, no RPM, no `pulse_counter`, `TachIO`/`GPIO16` reserved; tests pin via [`tests/test_fan_pwm_package.py`](../tests/test_fan_pwm_package.py)) + **`compile-only-target-landed` + `compile-pass-validated-full-compile`** (FW-COMPILE-PWM-001 / PR #591 added the `Ceiling-POE-FanPWM` compile-only target; CI `--compile` passed in run `26414398902`, FW-COMPILE-PWM-RESULT-001 / PR #592); Core abstract: `do-not-change-release-one` | **`PRODUCT-PWM-001` landed the no-RoomIQ / no-VentIQ `Ceiling-POE-FanPWM` product YAML** ([`products/sense360-ceiling-poe-fanpwm.yaml`](../products/sense360-ceiling-poe-fanpwm.yaml), product-YAML-only / no-WebFlash-exposure; full compile validated by run `26414398902`; no RPM) per [§FanPWM / S360-311](#fanpwm--s360-311). This RoomIQ/VentIQ-bearing variant is **not** separately built. The legacy four-channel [`products/sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml) stays `legacy-compatible` and is **not** the FanPWM candidate. | `none` (not in build matrix; not in REQUIRED_CONFIGS; not on landing list) | `HW-PINMAP-311-FOLLOWUP` → `PACKAGE-PWM-001-IMPLEMENT-001` *(PR #590)* → `FW-COMPILE-PWM-001` *(PR #591)* → `FW-COMPILE-PWM-RESULT-001` *(PR #592)* → **`PRODUCT-PWM-001`** *(this PR; product-YAML-only)* → `WEBFLASH-PWM-001` → `RELEASE-PWM-001` |
| `Ceiling-POE-FanDAC-RoomIQ` (FanDAC slice; AirIQ excluded by mutex) | `FanDAC` + `RoomIQ` (no `AirIQ`; `VentIQ` independent) | POE (S360-410) | [`fan_gp8403.yaml`](../packages/expansions/fan_gp8403.yaml) + Core abstract + RoomIQ (+ optional VentIQ) + [`power_poe.yaml`](../packages/hardware/power_poe.yaml) | grammar-clean **only if** `AirIQ` absent (`fandac_conflicts_with_airiq`); `Ceiling-POE-AirIQ-FanDAC-*` is `invalid-combination` | [`fan_gp8403.yaml`](../packages/expansions/fan_gp8403.yaml): **`package-layer-implemented`** (PACKAGE-DAC-001 / PR #573 — two GP8403 chips, four neutral outputs, per-chip address + range substitutions; tests pin via [`tests/test_fandac_package.py`](../tests/test_fandac_package.py)) + **`voltage-enum-fixed` + `compile-only-target-landed` + `compile-pass-validated-full-compile`** (FW-COMPILE-DAC-001 / PR #575 fixed the `gp8403:` `voltage:` substitutions `0-10V` → ESPHome's `10V` enum and added the `Ceiling-POE-FanDAC` compile-only target; the CI `--compile` pass passed in run `26364679370`, flag flipped by COMPILE-STATUS-FLAGS-001); Core abstract: `do-not-change-release-one` | **`PRODUCT-DAC-001` landed the no-RoomIQ `Ceiling-POE-FanDAC` product YAML** ([`products/sense360-ceiling-poe-fandac.yaml`](../products/sense360-ceiling-poe-fandac.yaml), product-YAML-only / no-WebFlash-exposure; full compile validated by run `26364679370`) per [§FanDAC / S360-312](#fandac--s360-312). This RoomIQ-bearing variant is **not** separately built; FW-COMPILE-DAC-001 added the `products/compile-only/` skeleton + the `packages/**` voltage fix. | `none` (not in build matrix; not in REQUIRED_CONFIGS) | `PACKAGE-DAC-001` *(PR #573)* → `FW-COMPILE-DAC-001` *(PR #575)* → `FW-COMPILE-DAC-RESULT-001` *(PR #576)* → **`PRODUCT-DAC-001`** *(this PR; product-YAML-only)* → `WEBFLASH-DAC-001` → `RELEASE-DAC-001` |
| `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` (FanTRIAC slice; **existing blocked reference**) | `VentIQ` + `FanTRIAC` + `RoomIQ` | POE (S360-410) | [`fan_triac.yaml`](../packages/expansions/fan_triac.yaml) + Core abstract + RoomIQ + VentIQ + [`power_poe.yaml`](../packages/hardware/power_poe.yaml) | grammar-clean (FanTRIAC is a canonical fan variant) | [`fan_triac.yaml`](../packages/expansions/fan_triac.yaml): `timing/compliance-pending` + `needs-package-reconciliation` + `blocked-from-standard-exposure`; Core abstract: `do-not-change-release-one` + `needs-package-reconciliation` | **No new product YAML; no status flip.** The existing blocked reference YAML stays `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`. PRODUCT-TRIAC-001 has performed a **notes-only** edit on this entry's `notes` field; the structural fields (`status` / `blocker` / `reason` / `webflash_build_matrix` / no-`artifact_name`) are unchanged. | `advanced/manual-warning-only` + `blocked-from-standard-exposure` + `not-recommended` + `not-required-configs` + `not-kit` + `not-webflash-default` (policy-recorded by PRODUCT-TRIAC-001 notes-only catalog edit; JSON `status: blocked` unchanged; no new lifecycle enum) | `HW-005` unblock + `HW-PINMAP-320-FOLLOWUP` + `COMPLIANCE-001` advanced/manual-warning sign-off → `PACKAGE-TRIAC-001` → `PRODUCT-TRIAC-002` → `WF-TRIAC-001` |
| `Ceiling-PWR-{AIR}-{ROOM}` (PWR-240V slice; not yet on WebFlash surface) | any single air-quality token (`AirIQ` xor `VentIQ`) + optional `RoomIQ` | PWR (S360-400) | [`power_240v.yaml`](../packages/hardware/power_240v.yaml) + Core abstract + air / room packages | grammar-clean if mutex respected; `PWR` is in `canonical_power` but no `webflash_build_matrix: true` entry exercises it today | [`power_240v.yaml`](../packages/hardware/power_240v.yaml): `schematic-evidence-pending` + `needs-package-reconciliation` + `timing/compliance-pending` (compliance-gated) | **No product YAML.** The four `legacy-compatible` `*-pwr` Core variants stay `legacy-compatible`. | `none` (not in build matrix; not in REQUIRED_CONFIGS; not on landing list); ultimately `production-candidate` only after `COMPLIANCE-001` `S360-400` slice clears | `HW-ASSETS-400` *(landed at PR #514)* → `HW-PINMAP-400-FOLLOWUP` *(this PR; docs-only)* → BOM + silkscreen + creepage / clearance + bench / thermal / EMI evidence → `COMPLIANCE-001` `S360-400` slice → `PACKAGE-POWER-400-001` → `PRODUCT-POWER-400-001` |
| `Ceiling-POE-{AIR}-{ROOM}` (PoE-410 slice; explicit board-level) | as today; PoE module the explicit subject | POE (S360-410) | [`power_poe.yaml`](../packages/hardware/power_poe.yaml) + Core abstract + air / room packages | grammar-clean; Release-One already exercises this shape | [`power_poe.yaml`](../packages/hardware/power_poe.yaml): `reference-only` + `schematic-evidence-pending` (schematic landed under HW-ASSETS-410 / PR #516 and was consumed by HW-PINMAP-410-FOLLOWUP; package-header reconciliation still owed to `PACKAGE-POE-410-001` after BOM lands) + `do-not-change-release-one` | **No new product YAML.** Release-One already consumes the package under the preserved [`release-one-hardware-audit.md` schematic-pending caveat](release-one-hardware-audit.md#findings); PRODUCT-GAP-001 does not requalify Release-One and does not promote the caveat away. | `none` for **new** PoE-410 candidate; Release-One stays `production` / `stable` on its existing entry | `HW-ASSETS-410` (PR #516) → `HW-PINMAP-410-FOLLOWUP` (this PR) → BOM cross-check → `HW-002 OQ#6` closure / `S360-100-BENCH-001` update → `S360-410` `schematic_status: verified` JSON PR → `PACKAGE-POE-410-001` → separate later Release-One caveat-closure PR + `PRODUCT-POE-410-001` if a new entry is warranted |

The Release-One package stack consumed by
[`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml)
and by
[`products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq-led.yaml)
is **explicitly out of scope** for this matrix's candidate columns —
PRODUCT-GAP-001 does not reclassify either entry and does not edit
either canonical YAML or either WebFlash wrapper.

## Per-family status

Each subsection below is intentionally short. The package-side
evidence, the connector / net-level disagreements, and the exact
file / line citations live in the per-board HW-PINMAP-* audits and
in [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md);
the subsections here record only the product-level verdict and the
named follow-up.

### FanRelay / S360-310

- **Status.** **`package-implemented-at-package-layer` (upstream;
  PACKAGE-RELAY-001 / PR #562) + `product-yaml-landed` (this PR;
  PRODUCT-RELAY-001) + `advanced/manual-warning-only` +
  `blocked-from-standard-exposure` + `not-required-configs` +
  `not-recommended` + `not-kit-default` + `not-webflash-default`**
  for the product-layer slice. The package-side disposition is
  recorded in
  [`hardware/package-readiness-matrix.md` `fan_relay.yaml` / S360-310](hardware/package-readiness-matrix.md#fan_relayyaml--s360-310)
  as `package-implemented` + `reconciled-at-package-layer`; the
  product-layer disposition is recorded here. **PRODUCT-RELAY-001
  has now landed as a product-YAML-only / no-WebFlash-exposure
  slice; WEBFLASH-RELAY-001, RELEASE-RELAY-001, and
  WF-IMPORT-RELAY-001 remain blocked.**
- **Why this posture, not `ready-for-product-yaml`.** The
  required package
  [`packages/expansions/fan_relay.yaml`](../packages/expansions/fan_relay.yaml)
  is now **implemented at the package layer** by PACKAGE-RELAY-001
  / PR #562: the package was already structurally correct
  (`fan_relay_pin: ${relay_pin}` line 27 inherits the parent Core
  abstract package binding, which post-`CORE-ABSTRACT-BUS-001A` /
  PR #558 resolves to the schematic-correct `GPIO3`), and the
  reconciliation is the addition of
  [`tests/test_fan_relay_package.py`](../tests/test_fan_relay_package.py)
  pinning the FanRelay package abstraction against future regression.
  Substitution-layer blockers were resolved by
  `CORE-ABSTRACT-BUS-001C` / PR #557 + `CORE-ABSTRACT-BUS-001A` /
  PR #558; hardware-evidence blockers (silkscreen / harness / `K1`
  BOM / contact-rating / load-contact behaviour) were populated by
  `S360-310-BENCH-EVIDENCE-001` / PR #561 (operator-attested +
  BOM-backed + public-reference-backed; no photo / video /
  oscilloscope / continuity-meter artifacts attached). However, per
  the same package-readiness row, "implemented / reconciled at the
  `PACKAGE-RELAY-001` package layer" explicitly **does not mean**
  product-ready, WebFlash-ready, release-ready, compliance-cleared,
  safe for arbitrary mains installation, or verified across
  production batches. The product layer has **separate** gates that
  PACKAGE-RELAY-001 does not discharge:
  1. **Product onboarding.** A FanRelay product YAML must clear the
     [`docs/product-onboarding.md`](product-onboarding.md) ordered
     safe sequence (canonical config-string shape per the WebFlash
     grammar; substitutions test; `validate_configs`; explicit
     product-onboarding approval). Not performed yet.
  2. **Installation / safety wording.** A FanRelay product
     designed to switch a mains load (the populated bench evidence
     in `S360-310-BENCH-EVIDENCE-001` records a UK mains Manrose
     `MT100S`-class extractor fan; the on-board `K1` Songle
     `SRD-05VDC-SL-C` carries a public-reference contact rating of
     `10 A @ 250 VAC; 10 A @ 30 VDC`) requires explicit
     user-facing installation / safety wording before any product
     YAML / WebFlash / release / kit exposure. No such wording has
     been authored, reviewed, or signed off.
  3. **Competent-person caveat.** Any product YAML / wrapper /
     catalog entry / kit narrative that ships FanRelay as a
     mains-switching driver must carry a competent-person caveat
     (UK Building Regulations Part P-equivalent; analogous to the
     FanTRIAC `advanced/manual-warning-only` posture but at a
     lower-severity tier because FanRelay is on/off contact-side
     rather than phase-dimming). No such caveat has been
     authored. The package-evidence-layer operator self-report
     "as per UK standards" in `S360-310-BENCH-EVIDENCE-001` is
     **not** an independent compliance sign-off and **not** a
     competent-person caveat.
  4. **Production-wide / multi-unit / oscilloscope-traced general
     `GPIO3` strap-pin boot-behaviour characterisation.** The
     `S360-310-BENCH-EVIDENCE-001` pair-scoped 10-cycle × 4-power-path
     boot observation is operator-framed as **pair-scoped sufficient
     for `PACKAGE-RELAY-001` implementation only**. Production-wide
     characterisation (multi-unit, oscilloscope-traced strap-state
     captures with operator / reviewer / serial / date) remains
     owed before any FanRelay product / WebFlash / release /
     stable promotion.
  5. **Board-level mains-safety / installation-approval / creepage
     / clearance / thermal / EMI evidence.** The contact-rating
     evidence in `S360-310-BENCH-EVIDENCE-001` is public-reference
     only and is explicitly **not** board-level compliance,
     installation approval, creepage / clearance, thermal, EMI, or
     mains-safety certification.
- **Recommended product posture (PRODUCT-RELAY-001).**
  **`advanced/manual-warning-only`** + **product YAML allowed
  without WebFlash exposure** + **compile-only validation
  allowed** + **WebFlash exposure blocked**. Concretely: when (and
  only when) the next-PR PRODUCT-RELAY-001 implementation slice
  lands, the recommended posture is that PRODUCT-RELAY-001 may
  add a single canonical FanRelay product YAML under
  [`products/`](../products/) carrying explicit
  advanced / manual-warning wording, the installation / safety
  caveat, and the competent-person caveat, **without** a
  [`products/webflash/`](../products/webflash/) wrapper, **without**
  a [`config/product-catalog.json`](../config/product-catalog.json)
  entry that flips `webflash_build_matrix: true`, **without** a
  [`config/webflash-builds.json`](../config/webflash-builds.json)
  build-matrix row, and **without** a release artifact /
  release-proof. A compile-only target under
  [`config/compile-only-targets.json`](../config/compile-only-targets.json)
  / [`config/compile-only-candidates.json`](../config/compile-only-candidates.json)
  is acceptable for end-to-end FanRelay-token compile validation
  but is **not** a WebFlash-shippable artifact and does **not**
  promote the family to `preview-candidate` or `production-candidate`
  exposure. The matrix-table cell `Future exposure class` for
  FanRelay is updated from the prior generic `preview-candidate`
  intent to `advanced/manual-warning-only`; the standard exposure
  ladder is **not** the default.
- **Product YAML action now.** None. **No FanRelay product YAML
  is added by PRODUCT-RELAY-001-READINESS-REFRESH** — this
  readiness refresh is documentation-only. No FanRelay candidate
  is added to [`products/`](../products/) or to any
  [`products/webflash/`](../products/webflash/) wrapper. The
  catalog
  [`config/product-catalog.json`](../config/product-catalog.json)
  gains no FanRelay entry. The build matrix
  [`config/webflash-builds.json`](../config/webflash-builds.json)
  gains no FanRelay row. No compile-only target is added.
- **Allowed without WebFlash exposure?** **Yes**, for the
  follow-up PRODUCT-RELAY-001 implementation slice — a canonical
  FanRelay product YAML may be added under
  [`products/`](../products/) without any
  [`products/webflash/`](../products/webflash/) wrapper, without
  any `webflash_build_matrix: true` catalog flip, without any
  [`config/webflash-builds.json`](../config/webflash-builds.json)
  entry, and without any release artifact. This is the
  product-YAML-only / no-WebFlash-exposure path.
- **Compile-only validation allowed?** **Yes**, on the same
  follow-up PRODUCT-RELAY-001 slice or a sibling slice, a
  compile-only target may be added under
  [`config/compile-only-targets.json`](../config/compile-only-targets.json)
  exercising the FanRelay token end-to-end. Compile-only is a
  validation pass, not a release class — see
  [`docs/compile-only-firmware-validation.md`](compile-only-firmware-validation.md)
  and the
  [`webflash-import-readiness-matrix`](https://github.com/sense360store/WebFlash/blob/main/docs/webflash-import-readiness-matrix.md)
  WebFlash-side rule "compile-only does not equal WebFlash import
  readiness".
- **WebFlash exposure class.** `none` — **blocked**. No
  WebFlash wrapper, no `webflash_build_matrix: true` flip, no
  [`config/webflash-builds.json`](../config/webflash-builds.json)
  row, no release artifact, no WebFlash import. WebFlash exposure
  for FanRelay is **categorically blocked** by this matrix until
  PRODUCT-RELAY-001 lands the product YAML, the installation /
  safety wording and competent-person caveat are accepted, and a
  separate WEBFLASH-RELAY-001 slice (gated additionally on
  production-wide hardware characterisation + installation /
  competent-person sign-off + WebFlash-side manual-warning UX
  parity) authors the wrapper / catalog flip / build-matrix row.
- **Why not `preview` and not just `blocked`.** `preview-candidate`
  is the standard exposure-ladder rung that implies WebFlash
  surfacing on a `preview` channel with optional WebFlash-side
  import; that surfacing is **not** appropriate for a
  mains-switching product without installation / safety wording or
  a competent-person caveat. `blocked` would imply that no product
  YAML may be added at all, which is more conservative than the
  package-implemented state warrants — the package layer is
  satisfied, and the package-evidence-layer captures support a
  product-YAML-only (no WebFlash) posture with explicit
  installation / safety wording. The posture chosen here —
  `advanced/manual-warning-only` + product-YAML-allowed +
  compile-only-allowed + WebFlash-blocked — is the least-risk
  posture consistent with both the package implementation and the
  open product-layer blockers above.
- **Follow-up owner.** `HW-ASSETS-310` *(landed)* →
  `HW-PINMAP-310-FOLLOWUP` *(landed; schematic-backed reconciliation
  recorded in [`s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md))*
  → `CORE-ABSTRACT-BUS-001C` *(landed PR #557 — freed `GPIO3`)*
  → `CORE-ABSTRACT-BUS-001A` *(landed PR #558 — `relay_pin → GPIO3`)*
  → `PACKAGE-RELAY-001-READINESS-REFRESH` *(landed PR #559)*
  → `S360-310-BENCH-001` *(landed PR #560 — checklist)*
  → `S360-310-BENCH-EVIDENCE-001` *(landed PR #561 — operator /
  BOM / public-reference evidence)* → `PACKAGE-RELAY-001` *(landed
  PR #562 — test + readiness reconciliation at the package layer
  only)* → **`PRODUCT-RELAY-001-READINESS-REFRESH`** *(this PR —
  docs-only product-layer readiness refresh; defines posture and
  product-layer blockers; **does not add a FanRelay product YAML**)*
  → `PRODUCT-RELAY-001` (this matrix's named FanRelay product
  slice). `PRODUCT-RELAY-001` must clear the
  [`docs/product-onboarding.md`](product-onboarding.md) ordered
  safe sequence, must author the advanced / manual-warning
  installation / safety wording + competent-person caveat as part
  of the product YAML, and must **not** add a WebFlash wrapper /
  catalog flip / build-matrix entry / release artifact. WebFlash
  exposure (if ever appropriate) is owned by a separate
  WEBFLASH-RELAY-001 slice gated on additional production-wide
  evidence + installation / competent-person sign-off.
- **Cross-references.**
  [`docs/hardware/s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md);
  [`docs/hardware/artifacts/S360-310-R4.md`](hardware/artifacts/S360-310-R4.md);
  [`board-readiness-matrix.md` `S360-310` notes](hardware/board-readiness-matrix.md#s360-310-sense360-relay);
  [`package-readiness-matrix.md` `fan_relay.yaml` / S360-310](hardware/package-readiness-matrix.md#fan_relayyaml--s360-310);
  [`docs/webflash-exposure-readiness-matrix.md` §Relay / S360-310 WebFlash posture](webflash-exposure-readiness-matrix.md#relay--s360-310-webflash-posture);
  [`docs/release-artifact-readiness-matrix.md` §Relay / S360-310 release posture](release-artifact-readiness-matrix.md#relay--s360-310-release-posture).

- **2026-05-22 — `PRODUCT-RELAY-001-READINESS-REFRESH` (this PR;
  docs-only).** Re-evaluated the FanRelay product-layer
  disposition after PACKAGE-RELAY-001 / PR #562 implemented the
  package at the package layer. Re-verified against the live
  files: no FanRelay product YAML exists under
  [`products/`](../products/); no FanRelay WebFlash wrapper exists
  under [`products/webflash/`](../products/webflash/);
  [`config/product-catalog.json`](../config/product-catalog.json)
  has no FanRelay row (the only shipping entries are Release-One
  `Ceiling-POE-VentIQ-RoomIQ` `status: production` /
  `channel: stable`, LED preview `Ceiling-POE-VentIQ-RoomIQ-LED`
  `status: preview` / `channel: preview`, and the blocked
  FanTRIAC reference `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`
  `status: blocked` / `blocker: HW-005`);
  [`config/webflash-builds.json`](../config/webflash-builds.json)
  has no FanRelay build (only Release-One stable and LED preview);
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  `canonical_modules` reserves `FanRelay` (line 11) subject to the
  fan-driver `max-one-of` rule; no compile-only target exercises
  FanRelay today (
  [`config/compile-only-targets.json`](../config/compile-only-targets.json)
  / [`config/compile-only-candidates.json`](../config/compile-only-candidates.json)
  byte-identical);
  [`packages/expansions/fan_relay.yaml`](../packages/expansions/fan_relay.yaml)
  is byte-identical to PR #562 state;
  [`tests/test_fan_relay_package.py`](../tests/test_fan_relay_package.py)
  byte-identical (12 stdlib-unittest cases, all green);
  [`tests/test_core_abstract_bus.py`](../tests/test_core_abstract_bus.py)
  byte-identical (20 stdlib-unittest cases, all green). The
  product-layer disposition is recorded above as
  `advanced/manual-warning-only` + product-YAML-allowed (no
  WebFlash) + compile-only-allowed + WebFlash-blocked. **No
  package / product / WebFlash / build / release / compliance /
  JSON-catalog / test / script / workflow / component / include /
  firmware / manifest edit**; **no `webflash_build_matrix` flip**;
  **no `artifact_name` / `webflash_wrapper` / `config_string` /
  `release_one_required_configs` / `lifecycle_statuses` /
  `canonical_modules` / `canonical_power` / `forbidden_tokens` /
  `REQUIRED_CONFIGS` / kit JSON change**; **no `schematic_status` /
  `schematic_file` promotion** (`S360-310` stays
  `cataloged_unverified`); **no COMPLIANCE-001 movement**;
  Release-One stays `Ceiling-POE-VentIQ-RoomIQ` / version `1.0.0`
  / channel `stable` / artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` / tag
  `v1.0.0`; LED preview stays `Ceiling-POE-VentIQ-RoomIQ-LED` /
  `status: preview` / `channel: preview` / version `1.0.0` /
  artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`;
  FanTRIAC stays `status: blocked` / `blocker: HW-005` /
  `webflash_build_matrix: false`. **No claim of FanRelay
  product-readiness, WebFlash-readiness, release-readiness,
  compliance-clearance, board-level mains-safety certification,
  installation-approval, qualified-electrician sign-off, or
  production-wide / multi-unit hardware characterisation.** The
  recommended next PR is **PRODUCT-RELAY-001 implementation** as
  a product-YAML-only / no-WebFlash-exposure slice (canonical
  FanRelay product YAML under [`products/`](../products/);
  explicit advanced / manual-warning wording; installation /
  safety caveat; competent-person caveat;
  [`docs/product-onboarding.md`](product-onboarding.md) safe
  sequence cleared; optional compile-only target under
  [`config/compile-only-targets.json`](../config/compile-only-targets.json)),
  **not** a WebFlash wrapper / catalog flip / build-matrix entry /
  release artifact. If the team prefers more guardrails first, the
  alternative next PR is a specific installation-safety /
  competent-person caveat scaffold PR for FanRelay-bearing
  products before any product YAML lands.

- **2026-05-22 — `PRODUCT-RELAY-001` (this PR; implementation
  slice).** Added the canonical FanRelay product YAML
  [`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml)
  as the **product-YAML-only / no-WebFlash-exposure** slice the
  readiness refresh above recommended. The YAML composes the same
  Release-One base stack (Core ceiling abstract +
  [`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml)
  + VentIQ + RoomIQ) and additionally
  `!include`s [`packages/expansions/fan_relay.yaml`](../packages/expansions/fan_relay.yaml),
  inheriting `${relay_pin}` from the Core abstract package binding
  (schematic-correct `GPIO3` post-`CORE-ABSTRACT-BUS-001A` /
  PR #558) without hard-coding any GPIO. The product YAML carries
  explicit **advanced / manual-warning** + **installation /
  safety** + **competent-person caveat** wording in the header
  block (mains switching / bathroom fan-control path; installation
  by competent person where required; not WebFlash exposed; not
  default kit; not release artifact; not compliance certification;
  advanced / manual-warning only). A single non-WebFlash row was
  added to
  [`config/product-catalog.json`](../config/product-catalog.json)
  for the new product YAML (required by
  [`tests/test_product_catalog.py`](../tests/test_product_catalog.py)
  enumeration): `config_string:
  Ceiling-POE-VentIQ-FanRelay-RoomIQ` /
  `status: hardware-pending` / `webflash_build_matrix: false` /
  no `artifact_name` / no `webflash_wrapper`. The catalog row is
  **not** in
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  **not** in `release_one_required_configs`, and **not** mapped to
  any WebFlash wrapper under
  [`products/webflash/`](../products/webflash/). The FanRelay row
  in [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json)
  for `Ceiling-POE-VentIQ-FanRelay-RoomIQ` reclassifies from
  `missing-product-yaml` (130 → 129) to `blocked-hardware`
  (36 → 37) automatically through
  [`scripts/generate_firmware_matrix.py`](../scripts/generate_firmware_matrix.py);
  the [`docs/firmware-build-gap-report.md`](firmware-build-gap-report.md)
  rendered report was regenerated by
  [`scripts/report_firmware_build_gaps.py`](../scripts/report_firmware_build_gaps.py)
  and the `fanrelay-blocked-package-or-core-bus` lane count stays
  at 36 (the lane matcher is `_row_has_fan(r, "FanRelay")`, so
  total lane membership is unchanged). The structural invariants
  for the product YAML, the catalog row, and the absence of
  WebFlash / build-matrix / wrapper / artifact / required-configs
  / release artifact are pinned by the new
  [`tests/test_relay_product_readiness.py`](../tests/test_relay_product_readiness.py)
  (42 stdlib-unittest cases, all green). The existing
  [`tests/test_fan_relay_package.py`](../tests/test_fan_relay_package.py)
  guardrail class `PackageRelayDoesNotTouchWebFlashOrProductTests`
  was tightened so it now allows the single PRODUCT-RELAY-001
  canonical FanRelay product YAML while continuing to forbid any
  additional FanRelay product YAML, any FanRelay WebFlash wrapper
  under [`products/webflash/`](../products/webflash/), and any
  FanRelay token in
  [`config/webflash-builds.json`](../config/webflash-builds.json).
  The PRODUCT-RELAY-001 implementation makes **no** edit to:
  any package YAML under [`packages/`](../packages/) (the FanRelay
  package is consumed as-is from PR #562); any WebFlash wrapper
  under [`products/webflash/`](../products/webflash/); the four
  protected `config/` files
  [`webflash-builds.json`](../config/webflash-builds.json),
  [`webflash-compatibility.json`](../config/webflash-compatibility.json),
  [`hardware-catalog.json`](../config/hardware-catalog.json),
  [`kit-intent-matrix.json`](../config/kit-intent-matrix.json);
  any workflow under [`.github/workflows/`](../.github/workflows/);
  any script under [`scripts/`](../scripts/) (only the generated
  outputs of `generate_firmware_matrix.py` and
  `report_firmware_build_gaps.py` are refreshed); any component
  under `components/`; any include under `include/`; any firmware
  artifact, manifest, sources, checksum, or build-info manifest.
  **No `webflash_build_matrix` flip; no `artifact_name`; no
  `webflash_wrapper`; no `release_one_required_configs` change;
  no `lifecycle_statuses` change; no `canonical_modules` /
  `canonical_power` / `forbidden_tokens` change; no
  `REQUIRED_CONFIGS` / kit JSON change; no `schematic_status` /
  `schematic_file` promotion (`S360-310` stays
  `cataloged_unverified`); no COMPLIANCE-001 movement.**
  Release-One stays `Ceiling-POE-VentIQ-RoomIQ` / version `1.0.0`
  / channel `stable` / artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` / tag
  `v1.0.0`; LED preview stays `Ceiling-POE-VentIQ-RoomIQ-LED` /
  `status: preview` / `channel: preview`; FanTRIAC stays
  `status: blocked` / `blocker: HW-005` /
  `webflash_build_matrix: false`. **No claim of FanRelay
  WebFlash-readiness, release-readiness, compliance-clearance,
  board-level mains-safety certification, installation-approval,
  qualified-electrician sign-off, or production-wide /
  multi-unit hardware characterisation.** The recommended next PR
  in the Relay chain is **WEBFLASH-RELAY-001 readiness refresh**
  (not immediate WebFlash exposure), unless the new product YAML
  fails compile-only validation in a later run; WebFlash exposure
  (if and when appropriate) remains gated additionally on
  production-wide hardware characterisation + installation /
  competent-person sign-off + WebFlash-side manual-warning UX
  parity per
  [`docs/webflash-exposure-readiness-matrix.md` §Relay / S360-310 WebFlash posture](webflash-exposure-readiness-matrix.md#relay--s360-310-webflash-posture).

- **2026-05-24 — `FW-COMPILE-RELAY-FULL-FIX-001` (this PR).** Fixed
  the FanRelay `GPIO3` double-bind found by the full compile lane
  (run `26334334727`). The Core abstract package's `main_relay`
  `switch.gpio` on `${relay_pin}` and the FanRelay package's own
  `switch.gpio` on `${fan_relay_pin}` (default `${relay_pin}`) both
  bound `GPIO3` when composed, which ESPHome rejects.
  [`packages/expansions/fan_relay.yaml`](../packages/expansions/fan_relay.yaml)
  now exposes `fan_relay_switch` as a `switch.template` that proxies
  the single Core `main_relay` GPIO owner (no second `gpio` binding,
  no GPIO named, `${relay_pin}` unchanged at `GPIO3`); invariants
  pinned by the updated
  [`tests/test_fan_relay_package.py`](../tests/test_fan_relay_package.py).
  **The FanRelay readiness status is unchanged** —
  `advanced/manual-warning-only` + product-YAML-landed +
  WebFlash-blocked. No `webflash_build_matrix` flip; no
  `artifact_name`; no `webflash_wrapper`; no
  [`config/webflash-builds.json`](../config/webflash-builds.json) row;
  no release artifact; no `release_one_required_configs` change; no
  `schematic_status` / `schematic_file` promotion; no COMPLIANCE-001
  movement; FanDAC untouched. **Full compile success is not claimed**
  — ESPHome was not run in the authoring environment; a manual
  `workflow_dispatch` `compile_mode=full` rerun of the
  `Compile-only Firmware Validation` lane remains required to confirm
  the FanRelay target now compiles green. This supersedes the
  FW-COMPILE-RELAY-RESULT-001 (2026-05-22) "successful full compile"
  claim, which run `26334334727` contradicted. **No claim of FanRelay
  WebFlash-readiness, release-readiness, compliance-clearance,
  board-level mains-safety certification, installation-approval,
  qualified-electrician sign-off, or production-wide / multi-unit
  hardware characterisation.**

- **2026-05-24 — `FW-COMPILE-RELAY-FULL-RESULT-001` (this PR).**
  Records the **successful manual full-compile run** that
  FW-COMPILE-RELAY-FULL-FIX-001 / PR #578 owed. A `workflow_dispatch`
  run of the `Compile-only Firmware Validation` lane with
  `compile_mode=full` ran against post-#578 `main` and **passed** —
  Run ID `26364679370`, event `workflow_dispatch`, mode
  `compile_mode=full`, status `completed`, conclusion `success`,
  **9** compile-only targets (job `Compile-only Targets — Metadata
  Validation` `77606314361` `success` → `Compile-only Targets — Full
  ESPHome Compile` `77606324332` `success`). **The previously failed
  full-compile run `26334334727` is superseded by this successful run
  `26364679370`** — the FanRelay target
  (`Ceiling-POE-VentIQ-FanRelay-RoomIQ`) now full-compiles green with
  the shape-C single-owner fix (`relay_pin` unchanged at `GPIO3`).
  **The FanRelay readiness status is unchanged** —
  `advanced/manual-warning-only` + product-YAML-landed +
  WebFlash-blocked. **The Relay product remains no-WebFlash /
  no-release.** No `webflash_build_matrix` flip; no `artifact_name`; no
  `webflash_wrapper`; no
  [`config/webflash-builds.json`](../config/webflash-builds.json) row;
  no release artifact / tag / checksum / build-info manifest; no
  `release_one_required_configs` change; no `schematic_status` /
  `schematic_file` promotion (`S360-310` stays `cataloged_unverified`);
  no COMPLIANCE-001 movement; FanDAC untouched. `WEBFLASH-RELAY-001`,
  `RELEASE-RELAY-001`, and `WF-IMPORT-RELAY-001` stay **blocked**.
  Compile success is necessary-but-insufficient input to the broader
  preview-to-stable promotion process. **No claim of FanRelay
  WebFlash-readiness, release-readiness, WebFlash import-readiness,
  compliance-clearance, board-level mains-safety certification,
  installation-approval, qualified-electrician sign-off, or
  production-wide / multi-unit hardware characterisation.**

- **2026-05-26 — `WEBFLASH-RELAY-001-READINESS` (this PR; docs-only).**
  Re-evaluated the FanRelay WebFlash-exposure readiness after the
  `WEBFLASH-DRIFT-001` / PR #595 audit, **without exposing FanRelay to
  WebFlash**. The product-layer disposition is **unchanged** —
  `advanced/manual-warning-only` + product-YAML-landed + WebFlash-blocked.
  The full re-evaluated Relay WebFlash readiness table (gate / status /
  evidence / next action) is recorded in
  [`webflash-exposure-readiness-matrix.md` §Relay / S360-310 WebFlash posture](webflash-exposure-readiness-matrix.md#relay--s360-310-webflash-posture):
  the package / product / full-compile / config-posture-hardware gates are
  `CLOSED`; WebFlash wrapper / `config/webflash-builds.json` row /
  `artifact_name` / release artifact / import-source are `BLOCKING`; live
  `sense360store/WebFlash` re-verification and the WebFlash-side
  module-availability / manifest axes are `NEEDS-TOOLING` (read access
  denied this session); compliance / mains-safety, production-wide `GPIO3`
  strap-pin characterisation, and competent-person sign-off remain owed
  (`BLOCKING` / `NEEDS-OPERATOR-INPUT`). The drift-audit row #21
  narrative-vs-config compile-flag gap is resolved as a docs clarification
  (the config target intentionally carries no `compile_validation_status`
  per `COMPILE-STATUS-FLAGS-001`; the optional `FW-COMPILE-RELAY-RESULT-001`
  config-flag add is non-blocking). **The recommended next Relay PR is
  `WEBFLASH-RELAY-LIVE-CHECK-001`, not `WEBFLASH-RELAY-002-WRAPPER-PLAN`
  and not `WEBFLASH-RELAY-001`.** No `config/`, `packages/`, `products/`,
  `products/webflash/`, test, workflow, firmware, or `sense360store/WebFlash`
  edit; no `webflash_build_matrix` flip; no `artifact_name`; no
  `schematic_status` / `schematic_file` promotion (`S360-310` stays
  `cataloged_unverified`); no COMPLIANCE-001 movement. **No claim of
  FanRelay WebFlash-readiness, release-readiness, WebFlash import-readiness,
  compliance-clearance, board-level mains-safety certification, or
  production-wide / multi-unit hardware characterisation.**
- **2026-05-27 — `RELAY-BLOCKER-RECLASSIFY-001` (this PR; docs-only) — scope
  of the remaining gaps clarified.** The remaining FanRelay production-wide
  `GPIO3` strap-pin (`RLY-3`) / competent-person sign-off (`RLY-4`) /
  manual-UX (`RLY-5`) / mains-compliance (`RLY-6`) / TRIAC-merge (`RLY-7`) /
  WebFlash (`RLY-8`) gaps are **reclassified by release scope**: they are
  **not** blockers for the **product layer** recorded here (product YAML,
  compile-only target, `config/` / product-catalog presence, and the
  no-WebFlash `hardware-pending` posture), nor for future clean repo / YAML /
  firmware cleanup PRs that do not expose WebFlash / release. They **stay**
  blockers only for WebFlash exposure, release artifacts, import readiness,
  hardware-stable promotion, the production safety / install claim, mains /
  compliance / safety claims, and kit / default / recommended membership.
  **Product-layer disposition is unchanged** — `advanced/manual-warning-only`
  + product-YAML-landed + WebFlash-blocked + full-compile-green (run
  `26364679370`) + `hardware-pending`; this PR adds **no** product YAML and
  changes no status. The production-wide `GPIO3` strap-pin characterisation is
  a production / hardware-stable / WebFlash / release blocker only (not a
  package / product-YAML blocker — the package binds `${relay_pin}` to the
  schematic-correct `GPIO3` and full-compiles green); competent-person
  sign-off is a safety / compliance / release blocker only; manual /
  advanced-warning UX is a WebFlash UX blocker only; mains / compliance
  approval is a release / compliance blocker only; kit / default /
  recommended membership stays out of scope unless separately approved. The
  `RLY-6` mains-switching safety posture stays correct. Canonical table in
  [`s360-310-r4-relay.md` §RELAY-BLOCKER-RECLASSIFY-001](hardware/s360-310-r4-relay.md#relay-blocker-reclassify-001--fanrelay-remaining-blockers-reclassified-by-release-scope-2026-05-27);
  cross-lane copy in
  [`blocker-burndown.md` §2C](blocker-burndown.md#2c-fanrelay--s360-310).
  **`S360-310-SAFETY-BENCH-RESULT-001`** stays the later safety-evidence PR
  and WebFlash stays separate and blocked (`WEBFLASH-RELAY-LIVE-CHECK-001`).
  No `config/` / `packages/` / `products/` / `products/webflash/` / test /
  workflow / firmware / `sense360store/WebFlash` edit; no
  `webflash_build_matrix` flip; no `artifact_name`; no WebFlash / import /
  release / compliance / hardware-stable claim; `S360-310` stays
  `cataloged_unverified`; no fabricated evidence.
- **2026-05-27 — `S360-310-SAFETY-EVIDENCE-REQUEST-001` (this PR;
  docs-only).** The product-layer disposition is **unchanged** —
  `advanced/manual-warning-only` + product-YAML-landed + WebFlash-blocked +
  full-compile-green (run `26364679370`) + `hardware-pending`. This PR adds
  **no** product YAML and changes no status; it turns the still-open FanRelay
  safety / access blockers (`RLY-3` production-wide / multi-unit /
  oscilloscope-traced `GPIO3` strap-pin characterisation; `RLY-4`
  competent-person sign-off; `RLY-5` manual / advanced-warning UX; `RLY-6`
  thermal / enclosure characterisation) into an operator- /
  qualified-person-answerable safety / `GPIO3` checklist + pass/fail evidence
  contract in
  [`s360-310-r4-relay.md` §S360-310-SAFETY-EVIDENCE-REQUEST-001](hardware/s360-310-r4-relay.md#s360-310-safety-evidence-request-001--fanrelay-safety--gpio3-evidence-checklist--contract-2026-05-27)
  and
  [`blocker-burndown.md` §5E](blocker-burndown.md#5e-s360-310-safety-evidence-request-001--fanrelay-detailed-safety--gpio3-checklist--evidence-contract-2026-05-27).
  A fresh Drive re-search found **no** new FanRelay safety / `GPIO3` /
  competent-person evidence — only design / CAD material (the legacy
  `RelayBoard-Module` set and a canonically-named `S360-310-R4` Drive set of
  KiCad / gerbers / CPL / STEP / BOM / schematic PDF / renders, plus the
  unchanged `Sense360_R4_Tracker`), recorded for provenance only and
  committing no Drive file (re-confirms `BLOCKER-BURNDOWN-001` / PR #599).
  The relay-boot evidence stays **pair-scoped operator-attested only** (10
  boot cycles × 4 power paths on one pair; no scope trace, no second unit);
  competent-person sign-off, relay-load voltage / current proof, and
  thermal / enclosure observation stay `NEEDS OPERATOR INPUT` / `NEEDS
  BENCH`. **Recommended next FanRelay PR: `S360-310-SAFETY-BENCH-RESULT-001`,
  gated until the operator / qualified person uploads / answers the
  checklist** — WebFlash wrapper / release / import PRs stay blocked
  (`WEBFLASH-RELAY-LIVE-CHECK-001` behind `sense360store/WebFlash` access).
  No `config/` / `packages/` / `products/` / `products/webflash/` / test /
  workflow / firmware / `sense360store/WebFlash` edit; no
  `webflash_build_matrix` flip; no `artifact_name`; no WebFlash / import /
  release / compliance / production-safety / hardware-stable / kit-default
  claim; `S360-310` stays `cataloged_unverified`; no fabricated evidence.

### FanPWM / S360-311

- **Status.** **`product-yaml-landed`** (PRODUCT-PWM-001 / 2026-05-26;
  product-YAML-only, PWM-drive-only, **no RPM**) + `package-implemented-at-package-layer`
  (PACKAGE-PWM-001-IMPLEMENT-001 / PR #590) + `compile-pass-validated-full-compile`
  (run `26414398902`) + `hardware-pending` + `not-webflash-ready` +
  `not-required-configs` + `not-recommended` + `not-kit-default`.
  > **Headline reconciliation — `WEBFLASH-DRIFT-001` (2026-05-26).** The original
  > `needs-package-reconciliation` + `hardware-evidence-pending` status and the
  > "Why no product YAML" / "Product YAML action now: None" prose immediately
  > below **predate PRODUCT-PWM-001** and are **superseded** by the dated
  > PRODUCT-PWM-001 addendum further down this section (FanRelay and FanDAC had
  > their headline statuses refreshed when their product YAMLs landed; this
  > FanPWM headline had not been). The current posture is the compound status on
  > this line: the canonical product YAML
  > [`products/sense360-ceiling-poe-fanpwm.yaml`](../products/sense360-ceiling-poe-fanpwm.yaml)
  > (`Ceiling-POE-FanPWM`) **exists** as a product-YAML-only, no-WebFlash-exposure
  > slice; the legacy four-channel YAML stays `legacy-compatible`. The historical
  > prose below is retained for the audit trail only.
- **Why no product YAML.** *(Historical — superseded; see the reconciliation
  note above.)* The required package
  [`packages/expansions/fan_pwm.yaml`](../packages/expansions/fan_pwm.yaml)
  is `needs-package-reconciliation` + `bench-evidence-pending`
  per
  [`package-readiness-matrix.md` `fan_pwm.yaml` / S360-311](hardware/package-readiness-matrix.md#fan_pwmyaml--s360-311):
  the single-channel package disagrees with the four-channel
  schematic on cardinality and on SX1509-vs-direct-ESP32 routing;
  PWM polarity, tach pull-up, pulses-per-revolution decisions are
  unowed; legacy four-channel
  [`packages/expansions/sense360_fan_pwm.yaml`](../packages/expansions/sense360_fan_pwm.yaml)
  is consumed only by the legacy product. A FanPWM product cannot
  be added until the package is reconciled.
- **Product YAML action now.** None. No new FanPWM canonical
  product is added. The existing legacy entry
  [`products/sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml)
  stays `legacy-compatible` and is **not** the FanPWM
  WebFlash-shippable candidate — PRODUCT-GAP-001 does not promote
  it.
- **WebFlash exposure class.** `none`. The legacy product stays
  `legacy-only`.
- **Follow-up owner.** `HW-PINMAP-311-FOLLOWUP` → `S360-311`
  `schematic_status` promotion (separate JSON PR) →
  `PACKAGE-PWM-001` (with `CORE-ABSTRACT-BUS-001` paired) →
  `PRODUCT-PWM-001` (this matrix's named FanPWM product slice;
  must additionally decide whether the legacy four-channel product
  is migrated, removed, or retained alongside).
- **Cross-references.**
  [`docs/hardware/s360-311-r4-pwm.md`](hardware/s360-311-r4-pwm.md);
  [`board-readiness-matrix.md` `S360-311` notes](hardware/board-readiness-matrix.md#s360-311-sense360-pwm);
  [`package-readiness-matrix.md` `fan_pwm.yaml` / S360-311](hardware/package-readiness-matrix.md#fan_pwmyaml--s360-311).
- **PWM-BLOCKER-REMOVAL-001 addendum (2026-05-25).** No product YAML is
  added and the product-layer status is unchanged. The audit in
  [`s360-311-r4-pwm.md` §PWM-BLOCKER-REMOVAL-001 readiness / blocker table](hardware/s360-311-r4-pwm.md#pwm-blocker-removal-001-readiness--blocker-table)
  closed the hardware-evidence, controlled-load, BOM-part-identity, and
  (no-mains) compliance rows and lifted the shared-I²C-bus blocker, but
  the product gate is unchanged: `PRODUCT-PWM-001` stays blocked behind
  `PACKAGE-PWM-001`, which is itself **NOT READY** pending the operator
  + bench decisions (single-vs-four-channel; SX1509-vs-direct-ESP32
  routing; `J3` / `J6` silkscreen pin order; PWM polarity / tach
  pull-up / pulses-per-revolution; per-fan current envelope). The
  legacy [`products/sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml)
  stays `legacy-compatible` and is **not** promoted.
- **CORE-ABSTRACT-BUS-SX1509-001 addendum (2026-05-25).** No product YAML
  is added and the product-layer status is unchanged. This PR landed the
  neutral, binding-only Core abstract-bus prerequisite
  [`packages/expansions/fan_pwm_sx1509.yaml`](../packages/expansions/fan_pwm_sx1509.yaml)
  (SX1509 hub on `core_i2c`; PWM-drive outputs `fan_pwm_drive_1..4` →
  channels 0..3; tach inputs `fan_pwm_tach_1..4` → channels 4..7;
  `tach_io_pin: GPIO16`) — the explicit next prerequisite named by
  operator decision D2. It does **not** unblock `PRODUCT-PWM-001`: the
  product surface stays blocked behind `PACKAGE-PWM-001`, which is still
  **NOT READY** (bench evidence owed, plus a **new** documented blocker —
  ESPHome's `pulse_counter` cannot bind an SX1509 expander pin, so per-fan
  RPM via `Pul_Cou1..4` needs the direct `tach_io_pin` / `IO16` line, a
  future custom component, or a bench-decided alternative). No WebFlash /
  release readiness is claimed; FanRelay and FanDAC are unchanged.
- **PACKAGE-PWM-TACH-STRATEGY-001 addendum (2026-05-25).** No product YAML
  is added and the product-layer status is unchanged. This PR records the
  operator tach/RPM decision (see
  [`s360-311-r4-pwm.md` §Tach / RPM strategy](hardware/s360-311-r4-pwm.md#tach--rpm-strategy-package-pwm-tach-strategy-001)):
  the first FanPWM package is scoped **PWM-drive-only** (four PWM outputs,
  **no** per-fan RPM sensors, optional diagnostic binary tach states only,
  `TachIO`/`GPIO16` reserved/pending), with per-fan RPM deferred to future
  work. This resolves the expander-tach RPM blocker by deferral but does
  **not** unblock `PRODUCT-PWM-001`: the product surface stays blocked
  behind `PACKAGE-PWM-001-IMPLEMENT-001` (PWM-only), which is itself not
  yet implementation-complete (bench PWM-polarity + current/thermal
  envelope and the four-channel reconciliation remain). Per-fan RPM is
  explicitly **out of scope** for the first FanPWM product. No PWM product
  / WebFlash / import / release / RPM-support readiness is claimed; the
  legacy [`products/sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml)
  stays `legacy-compatible` and is **not** promoted.
- **PWM-SX1509-TACH-PROOF-001 addendum (2026-05-25).** No product YAML is
  added and the product-layer status is unchanged. This PR replaces the
  previously-inferred tach blocker wording with an actual ESPHome
  compile/config proof. **SX1509 PWM-drive output IS supported**
  (`output: platform: sx1509`) and remains the basis of FanPWM drive;
  SX1509 GPIO/binary input is supported too. **Only the per-fan RPM path —
  an SX1509 expander pin used as an ESPHome `pulse_counter` — is
  compile-proven unsupported by ESPHome validation:** the minimal fixture
  [`tests/esphome/sx1509_pulse_counter_proof.yaml`](../tests/esphome/sx1509_pulse_counter_proof.yaml)
  is rejected by `esphome config` (ESPHome 2026.5.1, exit code 2) with
  `[sx1509] is an invalid option for [pin]`, while two control checks in
  [`tests/test_sx1509_tach_pulse_counter_proof.py`](../tests/test_sx1509_tach_pulse_counter_proof.py)
  confirm the rejection is `pulse_counter`+SX1509-specific (the same SX1509
  pin validates as a `binary_sensor: gpio`; `pulse_counter` validates on a
  native ESP32 GPIO). The proof **confirms** the PWM-drive-only-first
  strategy rather than revising it; the wording is now "compile-proven
  unsupported by ESPHome validation", not "unsupported online". No PWM
  product / WebFlash / import / release / RPM-support / compliance
  readiness is claimed.
- **PACKAGE-PWM-001-IMPLEMENT-001 addendum (2026-05-25).** **No product YAML
  is added and the product-layer status is unchanged** — this is a
  **package-layer** slice. The canonical FanPWM package
  [`fan_pwm.yaml`](../packages/expansions/fan_pwm.yaml) is implemented for the
  **PWM-drive-only** scope: it composes the neutral binding
  [`fan_pwm_sx1509.yaml`](../packages/expansions/fan_pwm_sx1509.yaml) and
  exposes **four independent** `fan: platform: speed` controllers
  (`fan_pwm_1..4`) on the SX1509 PWM-drive outputs `fan_pwm_drive_1..4`
  (channels 0..3), pinned by
  [`tests/test_fan_pwm_package.py`](../tests/test_fan_pwm_package.py).
  **SX1509 PWM-drive output is supported and is the mechanism used**
  (`output: platform: sx1509`). **RPM via an SX1509 tach `pulse_counter` is
  not implemented and not claimed** — it is compile-proven unsupported
  (`PWM-SX1509-TACH-PROOF-001`: `esphome config` rejects it with `[sx1509] is
  an invalid option for [pin]`); the package wires no `pulse_counter` and no
  RPM sensor, and the `Pul_Cou1..4` lines stay as the binding's internal
  diagnostic binary states (never RPM). **`TachIO` / `GPIO16` stays
  reserved/pending.** This does **not** unblock `PRODUCT-PWM-001`: the FanPWM
  product / WebFlash / import / release / compliance surface stays blocked
  behind the remaining gates — bench **PWM polarity**, per-fan / aggregate
  **current + thermal envelope**, **product YAML**, **compile-only target /
  result**, **WebFlash / release / import / compliance**, and the **optional
  future RPM strategy** (`COMPONENT-SX1509-TACH-001` or a bench-confirmed
  `TachIO` follow-up). No product / WebFlash / import / release / RPM-support /
  compliance / product-readiness claim is made; the legacy
  [`products/sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml) stays
  `legacy-compatible` and is **not** promoted; FanRelay and FanDAC are
  unchanged.
- **FW-COMPILE-PWM-001 addendum (2026-05-25).** **No product YAML is added and
  the product-layer status is unchanged** — this is a **compile-only
  validation** slice. FW-COMPILE-PWM-001 adds a single compile-only target
  `ceiling-poe-fanpwm-compile-only` →
  [`products/compile-only/ceiling-poe-fanpwm.yaml`](../products/compile-only/ceiling-poe-fanpwm.yaml)
  (config string `Ceiling-POE-FanPWM`) to
  [`config/compile-only-targets.json`](../config/compile-only-targets.json),
  composing Core ceiling + PoE PSU + base + health + the PWM-drive-only
  [`fan_pwm.yaml`](../packages/expansions/fan_pwm.yaml). It **validates the
  PWM-drive-only package scope** (SX1509 hub on `core_i2c`; four
  `output: platform: sx1509` PWM-drive outputs; four `fan: platform: speed`
  controllers) at ESPHome config / compile time. It **does not prove
  product / WebFlash / import / release readiness** — `PRODUCT-PWM-001` /
  `WEBFLASH-PWM-001` / `RELEASE-PWM-001` / `WF-IMPORT-PWM-001` stay blocked;
  no `config/webflash-builds.json` row, no `webflash_build_matrix` flip, no
  `artifact_name`, no release artifact; the skeleton lives under
  `products/compile-only/` so no `config/product-catalog.json` entry is added.
  It **does not claim RPM support** (`rpm_supported: false`; no
  `pulse_counter`; `TachIO` / `GPIO16` reserved) and **does not claim a full
  compile** — `compile_validation_status: pending-ci`, so a GitHub Actions /
  `workflow_dispatch` `--compile` run is required before any compile result is
  claimed (only the metadata lane is asserted). `S360-311` `schematic_status`
  stays `cataloged_unverified`; the bench gates and the optional future RPM
  strategy stay open. Pinned by
  [`tests/test_compile_targets.py`](../tests/test_compile_targets.py)
  `FanPWMCompileOnlyCoverageTests`; the `Ceiling-POE-FanPWM` lane stays `defer`
  in [`config/compile-only-candidates.json`](../config/compile-only-candidates.json).
  FanRelay and FanDAC are unchanged.
- **FW-COMPILE-PWM-RESULT-001 addendum (2026-05-25).** The full ESPHome
  compile of the PWM-drive-only FanPWM composition is now **recorded green**:
  the `Compile-only Firmware Validation` run `26414398902`
  (`compile_mode=full`, 10 compile-only targets, conclusion `success`) ran
  `scripts/validate_compile_targets.py --compile` against
  [`products/compile-only/ceiling-poe-fanpwm.yaml`](../products/compile-only/ceiling-poe-fanpwm.yaml)
  and passed, so the FanPWM compile-only target carries
  `compile_validation_status: validated-full-compile` with
  `rpm_supported: false`. This records the **compile-only result only**; it is
  **not** WebFlash exposure, **not** a release artifact, **not** RPM support,
  and **not** hardware-stable readiness.
- **PRODUCT-PWM-001 addendum (2026-05-26; this PR — product-YAML-only /
  no-WebFlash-exposure).** **`PRODUCT-PWM-001` has now LANDED the canonical
  FanPWM product YAML**
  [`products/sense360-ceiling-poe-fanpwm.yaml`](../products/sense360-ceiling-poe-fanpwm.yaml)
  (config string `Ceiling-POE-FanPWM`) as the product-YAML-only /
  no-WebFlash-exposure slice. It composes Core ceiling + PoE PSU + base/health
  with the PWM-drive-only [`fan_pwm.yaml`](../packages/expansions/fan_pwm.yaml)
  (four independent SX1509 PWM-drive fan-speed controllers). The matching
  catalog row (`config/product-catalog.json`, `Ceiling-POE-FanPWM`,
  `status: hardware-pending`, `webflash_build_matrix: false`, no
  `artifact_name`, no `webflash_wrapper`) is added; the package layer
  (PACKAGE-PWM-001-IMPLEMENT-001 / PR #590) and the **full compile** (run
  `26414398902`, `validated-full-compile`) are **complete for the
  PWM-drive-only scope**. **RPM is not supported** (no `pulse_counter`, no
  per-fan / aggregate RPM; `TachIO` / `GPIO16` reserved/pending). The product
  remains **blocked from WebFlash / release / import / compliance**:
  `WEBFLASH-PWM-001` / `RELEASE-PWM-001` / `WF-IMPORT-PWM-001` stay blocked; no
  `config/webflash-builds.json` row, no `webflash_build_matrix` flip, no
  `artifact_name`, no release artifact. The bench gates stay open — **PWM
  polarity**, per-fan / aggregate **current + thermal envelope**, **product
  bench not complete**; `S360-311` `schematic_status` stays
  `cataloged_unverified`. This is **not hardware-stable readiness and not
  product-release approval**. The FW-COMPILE-PWM-001 compile-only skeleton
  stays the separate CI validation target (unchanged). Pinned by
  [`tests/test_pwm_product_readiness.py`](../tests/test_pwm_product_readiness.py).
  FanRelay and FanDAC are unchanged.
- **FW-COMPILE-PWM-PRODUCT-001 addendum (2026-05-26; validation slice —
  docs / tests only).** This slice **validates** the PRODUCT-PWM-001 product
  YAML without changing WebFlash / release exposure. It adds a
  composition-parity check
  (`PwmProductMatchesValidatedCompileOnlyCompositionTests` in
  [`tests/test_pwm_product_readiness.py`](../tests/test_pwm_product_readiness.py))
  that pins that
  [`products/sense360-ceiling-poe-fanpwm.yaml`](../products/sense360-ceiling-poe-fanpwm.yaml)
  composes the **identical** package set (same package keys, same
  repo-relative `!include` targets — Core ceiling + PoE PSU + base/health +
  [`fan_pwm.yaml`](../packages/expansions/fan_pwm.yaml)) as the
  full-compile-validated compile-only skeleton
  [`products/compile-only/ceiling-poe-fanpwm.yaml`](../products/compile-only/ceiling-poe-fanpwm.yaml)
  (run `26414398902`, `compile_mode=full`, `validated-full-compile`). The two
  YAMLs differ only in substitutions / identification `text_sensor` wording,
  so the recorded full compile transfers to the product composition. The
  existing guards continue to pin **no WebFlash / release metadata** (no
  `webflash_build_matrix` flip, no `artifact_name`, no `webflash_wrapper`, no
  `config/webflash-builds.json` row) and **no RPM** (no `pulse_counter`, no
  `${tach_io_pin}` / `GPIO16` active binding). **Live `esphome config` was NOT
  run** — ESPHome is not present in this environment, so live product-config
  validation of `products/sense360-ceiling-poe-fanpwm.yaml` **remains
  pending**. The exact action that still owns it: run
  `esphome config products/sense360-ceiling-poe-fanpwm.yaml` locally with
  ESPHome installed, **or** rely on the `Compile-only Firmware Validation`
  action (`scripts/validate_compile_targets.py --compile`) which already
  full-compiles the byte-for-byte-equivalent composition via the compile-only
  skeleton. **Status stays conservative and unchanged:** `Ceiling-POE-FanPWM`
  remains `hardware-pending`, PWM-drive-only, **no RPM**; `WEBFLASH-PWM-001` /
  `RELEASE-PWM-001` / `WF-IMPORT-PWM-001` stay blocked; the S360-311 bench
  gates (PWM polarity; per-fan / aggregate current + thermal envelope; product
  bench) stay open; `S360-311` `schematic_status` stays
  `cataloged_unverified`. This is **not** WebFlash / import / release
  readiness, **not** compliance approval, and **not** hardware-stable
  readiness.
- **2026-05-26 — `WEBFLASH-PWM-001-READINESS` (this PR; docs-only).**
  Re-evaluated the FanPWM WebFlash-exposure readiness after the
  `WEBFLASH-DRIFT-001` / PR #595 audit, **without exposing FanPWM to
  WebFlash**. The product-layer disposition is **unchanged** —
  product-YAML-landed + WebFlash-blocked + `validated-full-compile` +
  `rpm_supported: false`. The full re-evaluated PWM WebFlash readiness
  table (gate / status / evidence / next action) is recorded in
  [`webflash-exposure-readiness-matrix.md` §PWM / S360-311 WebFlash posture](webflash-exposure-readiness-matrix.md#pwm--s360-311-webflash-posture):
  the package / product / full-compile / `compile_validation_status` /
  `rpm_supported` / product-YAML-composition-parity (FW-COMPILE-PWM-PRODUCT-001
  / PR #594) / config-posture-hardware gates are `CLOSED` (stronger than
  FanRelay — PWM's compile-status flag is already set, so there is no
  compile-flag gap); WebFlash wrapper / `config/webflash-builds.json`
  row / `artifact_name` / release artifact / import-source / no-RPM UX
  are `BLOCKING`; live `sense360store/WebFlash` re-verification, the
  still-owed `S360-311` module-availability classification
  (`WEBFLASH-DRIFT-001` row #16), and the live product-YAML `esphome
  config` are `NEEDS-TOOLING` (read / ESPHome access unavailable this
  session); the **PWM polarity**, **per-fan / aggregate current +
  thermal envelope**, **product bench**, `TachIO` / `GPIO16`
  reserved/pending, and board-level thermal / EMI caveats remain
  `NEEDS-OPERATOR-INPUT` (the board is SELV — no mains — so the
  `COMPLIANCE-001` mains gate does not apply to FanPWM). **The
  recommended next PWM PR is `WEBFLASH-PWM-LIVE-CHECK-001`, with
  `S360-311-BENCH-001` as the substantive evidence gate, not
  `WEBFLASH-PWM-002-WRAPPER-PLAN` and not `WEBFLASH-PWM-001`**
  (non-WebFlash gates are not all clean). No `config/`, `packages/`,
  `products/`, `products/webflash/`, test, workflow, firmware, or
  `sense360store/WebFlash` edit; no `webflash_build_matrix` flip; no
  `artifact_name`; no RPM added or claimed; no `schematic_status` /
  `schematic_file` promotion (`S360-311` stays `cataloged_unverified`).
  **No claim of FanPWM WebFlash-readiness, release-readiness, WebFlash
  import-readiness, RPM support, compliance-clearance, board-level safety
  certification, or hardware-stable readiness.**
- **2026-05-26 — `S360-311-BENCH-EVIDENCE-REQUEST-001` (this PR;
  docs-only).** The product-layer disposition is **unchanged** —
  product-YAML-landed + WebFlash-blocked + `validated-full-compile` +
  `rpm_supported: false` + `hardware-pending`. This PR adds **no**
  product YAML and changes no status; it turns the still-open FanPWM
  bench blockers (`PWM-3` / `PWM-6` / `PWM-10` / `PWM-11` / `PWM-13`)
  into an operator-answerable bench checklist + pass/fail evidence
  contract in
  [`s360-311-r4-pwm.md` §S360-311-BENCH-EVIDENCE-REQUEST-001](hardware/s360-311-r4-pwm.md#s360-311-bench-evidence-request-001--fanpwm-bench-evidence-checklist--contract-2026-05-26)
  and
  [`blocker-burndown.md` §5A](blocker-burndown.md#5a-s360-311-bench-evidence-request-001--fanpwm-detailed-bench-checklist--evidence-contract-2026-05-26).
  A fresh Drive re-search found **no** new FanPWM bench evidence — only
  design / CAD material (the `12vFan_PWM_PulseCounter` set, a
  canonically-named `S360-311-R4` Drive folder of KiCad / gerbers / CPL /
  STEP / BOM / schematic PDF / renders, and the unchanged
  `Sense360_R4_Tracker`), recorded for provenance only and committing no
  Drive file. The product bench (`PWM-11`), PWM polarity (`PWM-10`),
  per-fan / aggregate current + thermal (`PWM-6` / `PWM-13`) stay
  `NEEDS-OPERATOR-INPUT`/`NEEDS BENCH`; `TachIO` / `GPIO16` stays
  reserved (no RPM). **Recommended next PWM PR: `S360-311-BENCH-RESULT-001`,
  gated until the operator uploads / answers the checklist** —
  WebFlash wrapper / release / import PRs stay blocked. No `config/` /
  `packages/` / `products/` / `products/webflash/` / test / workflow /
  firmware / `sense360store/WebFlash` edit; no `webflash_build_matrix`
  flip; no `artifact_name`; no RPM / WebFlash / release / import /
  compliance / hardware-stable claim; `S360-311` stays
  `cataloged_unverified`.
- **2026-05-26 — `S360-311-BENCH-RESULT-001` (this PR; docs-only).** The
  operator (`@wifispray`) ran the requested FanPWM bench; this PR
  **records** the result (operator-notes-only attestation — no photo /
  video / log) in
  [`s360-311-r4-pwm.md` §S360-311-BENCH-RESULT-001](hardware/s360-311-r4-pwm.md#s360-311-bench-result-001--fanpwm-operator-bench-result-2026-05-26)
  and [`blocker-burndown.md` §5B](blocker-burndown.md#5b-s360-311-bench-result-001--fanpwm-operator-bench-result-2026-05-26).
  **Product-layer disposition is unchanged** — product-YAML-landed +
  WebFlash-blocked + `validated-full-compile` + `rpm_supported: false` +
  `hardware-pending`; this PR adds **no** product YAML and changes no
  status. The bench **closed** PWM polarity (`PWM-10` — increasing duty
  increased fan speed; non-inverting, no inversion required) and the
  **functional product bench** (`PWM-11` — all four channels individually
  speed-controlled, all four simultaneous for 1+ hour, restart retained
  the last commanded speed on `S360-311-R4`), and **partially advanced**
  `PWM-3` (board tested = `S360-311-R4`), `PWM-6` (fan/load = Arctic P14
  Plus; supply = 12 V MT3608 boost, ~2 A available; qualitative 1+ hour
  run) and `PWM-13` (qualitative 1+ hour no-heat observation). **Still
  open / unchanged:** measured per-channel + aggregate current and
  measured thermal temperature (`PWM-6` / `PWM-13`); `TachIO` / `GPIO16`
  reserved and RPM unsupported (no `pulse_counter`; `PWM-12`); WebFlash
  exposure (`NEEDS WEBFLASH ACCESS`), release, and import. The SX1509
  PWM-drive output is supported and is the basis of FanPWM drive, kept
  distinct from the compile-proven per-fan RPM limitation
  (`PWM-SX1509-TACH-PROOF-001`; `esphome config` rejects an SX1509-backed
  `pulse_counter` with `[sx1509] is an invalid option for [pin]`).
  **Recommended next PWM PR: `S360-311-CURRENT-THERMAL-001`** (measured
  current / thermal); WebFlash stays separate and blocked
  (`WEBFLASH-PWM-LIVE-CHECK-001` behind access) and no `WEBFLASH-PWM-001`
  wrapper is recommended until measured current/thermal *and* the WebFlash
  live classification are done. No `config/` / `packages/` / `products/` /
  `products/webflash/` / test / workflow / firmware / `sense360store/WebFlash`
  edit; no `webflash_build_matrix` flip; no `artifact_name`; no RPM /
  WebFlash / import / release / compliance / hardware-stable claim;
  `S360-311` stays `cataloged_unverified`; no fabricated photo / video /
  log / measurement evidence.
- **2026-05-27 — `PWM-BLOCKER-RECLASSIFY-001` (this PR; docs-only) — scope
  of the remaining gaps clarified.** The remaining FanPWM measured-current /
  thermal / `TachIO` / WebFlash gaps are **reclassified by release scope**:
  they are **not** blockers for the **product layer** recorded here
  (product YAML, compile-only target, `config/` / product-catalog presence,
  and the no-WebFlash `hardware-pending` posture), nor for future clean
  repo / YAML / firmware cleanup PRs that do not expose WebFlash / release.
  They **stay** blockers only for WebFlash exposure, release artifacts,
  import readiness, hardware-stable promotion, the production
  electrical-margin claim, RPM / `TachIO` claims, and compliance.
  **Product-layer disposition is unchanged** —
  `product-YAML-landed` + WebFlash-blocked + `validated-full-compile` +
  `rpm_supported: false` + `hardware-pending`; this PR adds **no** product
  YAML and changes no status. Measured current / thermal is a release /
  WebFlash / hardware-stable blocker only; `TachIO`/`GPIO16` is an
  RPM / diagnostics blocker only; RPM is out of scope for the PWM-drive-only
  product; WebFlash live access is a WebFlash-exposure blocker only.
  Canonical table in
  [`s360-311-r4-pwm.md` §PWM-BLOCKER-RECLASSIFY-001](hardware/s360-311-r4-pwm.md#pwm-blocker-reclassify-001--fanpwm-remaining-blockers-reclassified-by-release-scope-2026-05-27);
  cross-lane copy in
  [`blocker-burndown.md` §2A](blocker-burndown.md#2a-fanpwm--s360-311).
  **`S360-311-CURRENT-THERMAL-001`** stays the later measured-evidence PR
  and WebFlash stays separate and blocked (`WEBFLASH-PWM-LIVE-CHECK-001`).
  No `config/` / `packages/` / `products/` / `products/webflash/` / test /
  workflow / firmware / `sense360store/WebFlash` edit; no
  `webflash_build_matrix` flip; no `artifact_name`; no RPM / WebFlash /
  import / release / compliance / hardware-stable claim; `S360-311` stays
  `cataloged_unverified`; no fabricated evidence.
- **2026-05-27 — `S360-311-CURRENT-THERMAL-EVIDENCE-REQUEST-001` (this PR;
  docs-only) — measured current / thermal evidence checklist defined.**
  The product-layer disposition is **unchanged** — `product-YAML-landed` +
  WebFlash-blocked + `validated-full-compile` + `rpm_supported: false` +
  `hardware-pending`; this PR adds **no** product YAML and changes no
  status. It turns the still-open **measured current / thermal** rows
  (`PWM-6` / `PWM-13`) — which per `PWM-BLOCKER-RECLASSIFY-001` gate **only**
  WebFlash / release / hardware-stable / electrical-margin, **not** this
  product layer — into an operator-answerable checklist (board rev; fan
  model + label current rating; supply voltage + measured supply current;
  per-channel + aggregate current at full speed; inrush; MT3608 input /
  output / measured ceiling; thermal method incl. IR / camera /
  thermocouple / qualitative; duration; ambient; hottest location; measured
  max temp; all-four-at-full-duty; any voltage-drop / instability / reset;
  optional `TachIO`/`GPIO16` with **no RPM claim**; photos / videos / logs;
  operator / date / provenance) + pass/fail evidence contract in
  [`s360-311-r4-pwm.md` §S360-311-CURRENT-THERMAL-EVIDENCE-REQUEST-001](hardware/s360-311-r4-pwm.md#s360-311-current-thermal-evidence-request-001--fanpwm-current--thermal-evidence-checklist--contract-2026-05-27)
  and [`blocker-burndown.md` §5D](blocker-burndown.md#5d-s360-311-current-thermal-evidence-request-001--fanpwm-current--thermal-checklist--contract-2026-05-27).
  A fresh Drive re-search found **no** measured current / thermal artifact
  — only design / CAD material (recorded for provenance, nothing
  committed). The measured rows stay `NEEDS-OPERATOR-INPUT`;
  **`S360-311-CURRENT-THERMAL-001` stays gated until the operator supplies
  them** — WebFlash wrapper / release / import PRs stay blocked. No
  `config/` / `packages/` / `products/` / `products/webflash/` / test /
  workflow / firmware / `sense360store/WebFlash` edit; no
  `webflash_build_matrix` flip; no `artifact_name`; no measured-current /
  measured-thermal / RPM / WebFlash / release / import / compliance /
  hardware-stable claim; `S360-311` stays `cataloged_unverified`; no
  fabricated evidence.

### FanDAC / S360-312

- **Status.** **`package-implemented-at-package-layer` (upstream;
  PACKAGE-DAC-001 / PR #573) + `compile-only-target-landed` +
  `voltage-enum-fixed` (FW-COMPILE-DAC-001 / PR #575) +
  `compile-only-metadata-ci-green` (FW-COMPILE-DAC-RESULT-001 / PR #576;
  Run ID `26332462496`, conclusion `success`) + `compile-pass-validated-full-compile`
  (the manual `workflow_dispatch` `compile_mode=full` run `26364679370`
  compiled the FanDAC target green; flag flipped by
  COMPILE-STATUS-FLAGS-001) +
  `not-required-configs` +
  `not-recommended` + `not-kit-default` + `not-webflash-default`**
  + `invalid-combination` for any `AirIQ`-bearing variant. The
  package-side disposition is recorded in
  [`hardware/package-readiness-matrix.md` `fan_gp8403.yaml` / S360-312](hardware/package-readiness-matrix.md#fan_gp8403yaml--s360-312)
  as `package-layer-implemented`; the product-layer disposition is
  recorded here. **`PRODUCT-DAC-001` has now LANDED as
  product-YAML-only / no-WebFlash-exposure** (this PR; see
  "Product YAML action now" below). **`WEBFLASH-DAC-001`,
  `RELEASE-DAC-001`, and `WF-IMPORT-DAC-001` all remain blocked**; the
  full ESPHome `--compile` pass is now **validated** by run `26364679370`
  (see the `COMPILE-STATUS-FLAGS-001` bullet below).
- **Package layer (PR #573).** The required package
  [`packages/expansions/fan_gp8403.yaml`](../packages/expansions/fan_gp8403.yaml)
  is now **implemented at the package layer** by
  PACKAGE-DAC-001-IMPLEMENT-001 / PR #573 (see
  [`docs/hardware/s360-312-r4-fandac.md` §2026-05-23 — PACKAGE-DAC-001-IMPLEMENT-001](hardware/s360-312-r4-fandac.md#2026-05-23--package-dac-001-implement-001)):
  two GP8403 chips (`fan_dac_1` / IC1 at `0x58`, `fan_dac_2` / IC2 at
  `0x59`) on the shared `${fan_dac_i2c_id}` (`core_i2c`) bus; per-chip
  address substitutions; per-chip output-range substitutions (both
  default `0-10V`, independently overridable per chip via register
  `0x01`); four neutral outputs (`fan_dac_1_vout0` / `fan_dac_1_vout1`
  / `fan_dac_2_vout0` / `fan_dac_2_vout1`). The earlier evidence
  blockers (rows 3 / 6 / 8 — DIP-switch ↔ address truth table,
  output-range policy, `J2` / `J3` pin-1 identity) were closed by
  PR #572. As recorded in the package-readiness row, "implemented at
  the package layer" explicitly **does not mean** product-ready,
  WebFlash-ready, release-ready, compile-validated, or
  compliance-cleared.
- **Compile concern — RESOLVED by FW-COMPILE-DAC-001 (Option A).**
  PR #573 bound the GP8403 `voltage:` field to the **invalid** value
  `0-10V` (`fan_dac_1_output_range` / `fan_dac_2_output_range`),
  whereas the upstream ESPHome `gp8403:` component accepts only the
  bare chip-level enum **`10V` / `5V`**
  ([esphome.io/components/output/gp8403](https://esphome.io/components/output/gp8403);
  the pre-implementation
  [§GP8403 output range capability](hardware/s360-312-r4-fandac.md#gp8403-output-range-capability)
  notes already implied a `${fan_dac_voltage_mode}` default of `10V`).
  Because ESPHome's documented schema unambiguously rejects `0-10V`,
  FW-COMPILE-DAC-001 takes **Option A**: it **fixes** the package
  substitutions from `0-10V` to the valid ESPHome enum **`10V`**
  (customer-facing 0-10V). The user-facing `0-10V` / `0-5V` labels stay
  in the product / kit docs (e.g. `S360-KIT-DUCT-0-10V`), never in the
  `voltage:` substitution. A product that `!include`s the package now
  inherits a valid `voltage: 10V` binding. A single GP8403 still cannot
  drive one output at 0-5V and the other at 0-10V (one `V5V` reference /
  one range register per chip).
- **Compile-pass status — metadata CI green; full compile validated
  (run `26364679370`).** FW-COMPILE-DAC-001 adds the `ceiling-poe-fandac-compile-only`
  target
  ([`products/compile-only/ceiling-poe-fandac.yaml`](../products/compile-only/ceiling-poe-fandac.yaml),
  config string `Ceiling-POE-FanDAC`) and passes
  `scripts/validate_compile_targets.py --metadata-only`. **FW-COMPILE-DAC-RESULT-001**
  (2026-05-23) records the GitHub Actions result for PR #575: the
  `Compile-only Firmware Validation` workflow (Run ID `26332462496`,
  conclusion `success`, target count 9) passed its **metadata-validation
  lane**. The `Compile-only Targets — Full ESPHome Compile` job was
  **`skipped`** — it runs only on a manual `workflow_dispatch` with
  `compile_mode=full`
  ([`.github/workflows/compile-only.yml`](../.github/workflows/compile-only.yml)
  line 103) — so **no `esphome config` / `esphome compile` was executed
  against the FanDAC skeleton in CI**. The `voltage: 10V` fix is
  confirmed against ESPHome's **documented** `gp8403` schema and pinned
  by `tests/test_fandac_package.py`. The actual `esphome config` /
  `--compile` pass — owed at FW-COMPILE-DAC-RESULT-001 time — has since
  **passed** in the manual `workflow_dispatch` `compile_mode=full` run
  `26364679370` (FW-COMPILE-DAC-FULL-RESULT-001), so the
  `compile_validation_status` flag is now `validated-full-compile`
  (flipped by COMPILE-STATUS-FLAGS-001), superseding the prior
  `pending-ci` marker.
- **Recommended product posture / next PR.** The voltage-enum gate that
  blocked `PRODUCT-DAC-001` is resolved at the package layer (the
  `0-10V` → `10V` fix is in place), and the compile-only **metadata** CI
  lane is now green (FW-COMPILE-DAC-RESULT-001, Run ID `26332462496`,
  conclusion `success`). **`PRODUCT-DAC-001` can now be considered the
  next chain step, subject to its product-layer gates** — but it is
  **not** unblocked yet: the full ESPHome `--compile` pass was
  **`skipped`** on PR #575 (it runs only via `workflow_dispatch`
  `compile_mode=full`), so the compile gate remains **owed**.
  `PRODUCT-DAC-001` may proceed once the CI `--compile` pass is green
  **and** `S360-312` `schematic_status: verified` lands (separate JSON
  PR). When it does, `PRODUCT-DAC-001` may add a single canonical
  FanDAC product YAML under [`products/`](../products/)
  **without** a [`products/webflash/`](../products/webflash/) wrapper,
  **without** a `webflash_build_matrix: true` catalog flip, **without** a
  [`config/webflash-builds.json`](../config/webflash-builds.json)
  build-matrix row, and **without** a release artifact — the
  product-YAML-only / no-WebFlash-exposure path. It must enforce the
  `fandac_conflicts_with_airiq` mutex (no `AirIQ`-bearing FanDAC
  product); any `Ceiling-POE-AirIQ-FanDAC-*` candidate is
  `invalid-combination` regardless of compile or package readiness.
- **Product YAML action now — `PRODUCT-DAC-001` LANDED (this PR;
  product-YAML-only / no-WebFlash-exposure).** `PRODUCT-DAC-001` adds the
  single canonical FanDAC product YAML
  [`products/sense360-ceiling-poe-fandac.yaml`](../products/sense360-ceiling-poe-fandac.yaml)
  (config string `Ceiling-POE-FanDAC`) plus its
  [`config/product-catalog.json`](../config/product-catalog.json)
  `hardware-pending` row. The product composes Core ceiling + PoE PSU +
  base/health with the canonical FanDAC alias
  [`packages/expansions/fan_dac.yaml`](../packages/expansions/fan_dac.yaml)
  (→ `fan_gp8403.yaml`). It is **product-YAML-only / no-WebFlash-exposure**:
  **no** [`products/webflash/`](../products/webflash/) wrapper, **no**
  `webflash_build_matrix: true` flip (`false` in the catalog row), **no**
  `artifact_name`, **no**
  [`config/webflash-builds.json`](../config/webflash-builds.json) row (the
  `FanDAC` token is absent there), **no** release artifact. The product
  YAML's header still carries (as written at PRODUCT-DAC-001 time) a
  full-compile-owed caveat (the config-layer
  `compile_validation_status` flag has since been flipped to
  `validated-full-compile` by COMPILE-STATUS-FLAGS-001 after run
  `26364679370`; reconciling the product-YAML header text is a separate
  follow-up since `products/**` is out of this PR's scope),
  the `J3` `out0`/`out1` silkscreen transposition, the Cloudlift S12
  harness / product-bench residual, the FanDAC ↔ AirIQ mutex, and the
  per-chip (not per-output) output-range limitation. Invariants pinned by
  [`tests/test_dac_product_readiness.py`](../tests/test_dac_product_readiness.py).
  The earlier FW-COMPILE-DAC-001 compile-only skeleton under
  [`products/compile-only/`](../products/compile-only/) stays unchanged
  and separate. **`WEBFLASH-DAC-001`, `RELEASE-DAC-001`, and
  `WF-IMPORT-DAC-001` remain blocked.** No full-compile-success, WebFlash,
  release, compliance, or hardware-stable readiness is claimed.
- **Harness / board-level pin mapping.** The `J2` (IC1, Cloudlift S12
  FAN) / `J3` (IC2, Cloudlift S12 FAN2) board-level pin-1 identity and
  pin order (**pin 1 = `VOUT0`**, **pin 2 = `GND`**, **pin 3 =
  `VOUT1`**) are captured at the board level (PR #572, row 8). Two
  product / bench residuals must be **carried into product docs /
  caveats** by `PRODUCT-DAC-001`:
  - the **harness conductor-by-conductor trace** from `J2` / `J3` to
    the physical Cloudlift S12 fan input remains an unresolved
    product / bench item (no fan / harness artifact exists in Drive);
  - the **`J3` `out0` / `out1` silkscreen transposition** (the pin-1
    pad — `IC2` `VOUT0` — is silk-labelled `out1`, and the pin-3 pad —
    `IC2` `VOUT1` — is silk-labelled `out0`) must be honoured in any
    installation / harness documentation and warrants operator / bench
    confirmation before the printed `J3` labels are relied upon.
- **Output naming.** The package keeps **neutral output IDs**
  (`fan_dac_1_vout0` … `fan_dac_2_vout1`). The product layer may map
  these to user-facing, **outcome-first** names — for example
  "0–10V fan control" / "Cloudlift S12 fan control" — and must **not**
  leak board-module jargon (the GP8403 chip name, `VOUTn`, `IC1` / `IC2`,
  or the generic `Fan` token) into customer-facing labels. The neutral
  package IDs stay unchanged.
- **Nextion / UART scope.** The Nextion display on Module `J7` (and the
  UART0-vs-Nextion arbitration) is **out of scope for the first DAC
  product** unless that product explicitly drives a display. The
  package binds **no** `uart:` and **no** `display:` on this pair;
  resolution stays a deferred item (row 9) and does not block
  `PRODUCT-DAC-001` for a non-display FanDAC product.
- **WebFlash exposure class.** `none`. WebFlash exposure remains
  blocked (`WEBFLASH-DAC-001`); release artifact remains blocked
  (`RELEASE-DAC-001`). No WebFlash wrapper, build-matrix entry,
  `artifact_name`, or release / proof row is added by this refresh.
- **Follow-up owner / sequence.** `PACKAGE-DAC-001` *(landed PR #573)*
  → `FW-COMPILE-DAC-001` *(PR #575 — compile-only target landed +
  `voltage:` `0-10V` → `10V` fix)* → `FW-COMPILE-DAC-RESULT-001`
  *(PR #576 — compile-only metadata lane green, Run ID `26332462496`)*
  → **`PRODUCT-DAC-001`** *(this PR — canonical product YAML landed
  product-YAML-only / no-WebFlash-exposure; enforces the FanDAC ↔ AirIQ
  mutex, outcome-first naming, and carries the full-compile-owed /
  harness / `J3`-silk caveats)* → **next:**
  `FW-COMPILE-DAC-FULL-001` (record the still-owed manual
  `workflow_dispatch` `compile_mode=full` ESPHome compile before WebFlash
  planning) *or* `WEBFLASH-DAC-001-READINESS-REFRESH` (re-evaluate the
  WebFlash gate) → `WEBFLASH-DAC-001` → `RELEASE-DAC-001` →
  `WF-IMPORT-DAC-001` (WebFlash-owned). `S360-312` `schematic_status`
  promotion stays a separate JSON PR.
- **2026-05-24 — `FW-COMPILE-DAC-FULL-RESULT-001` (this PR).** Records
  that the **successful manual full-compile run `26364679370`** — the
  same `workflow_dispatch` `compile_mode=full` run
  `FW-COMPILE-RELAY-FULL-RESULT-001` / PR #579 recorded for FanRelay —
  **also validates the FanDAC compile-only target**. Run ID
  `26364679370`, event `workflow_dispatch`, mode `compile_mode=full`,
  status `completed`, conclusion `success`, **9** compile-only targets
  (job `Compile-only Targets — Metadata Validation` `77606314361`
  `success` → `Compile-only Targets — Full ESPHome Compile`
  `77606324332` `success`), against post-#578 `main` (merge commit
  `4906a22`). The full-compile lane runs `esphome compile` against
  **every** [`config/compile-only-targets.json`](../config/compile-only-targets.json)
  target and fails on the first failure, so the `success` conclusion
  proves all nine targets compiled — including the 9th,
  `ceiling-poe-fandac-compile-only` →
  [`products/compile-only/ceiling-poe-fandac.yaml`](../products/compile-only/ceiling-poe-fandac.yaml)
  (`Ceiling-POE-FanDAC`), present at the validated ref. **This
  supersedes the full-compile concern left owed by
  FW-COMPILE-DAC-RESULT-001 / PR #576** (which recorded only the green
  metadata lane — the full-compile job was `skipped` on PR #575's head),
  and the **GP8403 `voltage: 10V` enum fix is now compile-validated by
  ESPHome's own validator**, not only against the documented schema. The
  `compile_validation_status: pending-ci` marker in
  [`config/compile-only-targets.json`](../config/compile-only-targets.json)
  is satisfied by this run; flipping that literal config flag is a
  separate config-layer change outside this docs-only record (since
  done — see the `COMPILE-STATUS-FLAGS-001` bullet below). **`PRODUCT-DAC-001`
  has product YAML
  ([`products/sense360-ceiling-poe-fandac.yaml`](../products/sense360-ceiling-poe-fandac.yaml),
  PR #577) but remains no-WebFlash / no-release** — `webflash_build_matrix:
  false`, no `artifact_name`, no `webflash_wrapper`, no
  [`config/webflash-builds.json`](../config/webflash-builds.json) row.
  `WEBFLASH-DAC-001`, `RELEASE-DAC-001`, and `WF-IMPORT-DAC-001` stay
  **blocked**. No `webflash_build_matrix` flip; no `artifact_name`; no
  release artifact / tag / checksum / build-info manifest; no
  `release_one_required_configs` change; no `schematic_status` /
  `schematic_file` promotion (`S360-312` stays `cataloged_unverified`);
  no COMPLIANCE-001 movement; FanDAC / FanRelay code untouched. Compile
  success is a necessary-but-insufficient input to the broader
  preview-to-stable promotion process. **No claim of FanDAC
  WebFlash-readiness, release-readiness, WebFlash import-readiness,
  compliance / safety certification, hardware proof, or simultaneous
  per-output 0-5V + 0-10V on a single GP8403.**
- **2026-05-24 — `COMPILE-STATUS-FLAGS-001` (this PR).** Reconciles the
  stale config-layer flag that FW-COMPILE-DAC-FULL-RESULT-001 deferred:
  the FanDAC compile-only target's `compile_validation_status` in
  [`config/compile-only-targets.json`](../config/compile-only-targets.json)
  is flipped `pending-ci` → **`validated-full-compile`** (proven by run
  `26364679370`), and the two tests that pinned `pending-ci`
  ([`tests/test_compile_targets.py`](../tests/test_compile_targets.py),
  [`tests/test_dac_product_readiness.py`](../tests/test_dac_product_readiness.py))
  are updated. Narrow status reconciliation only: **no** readiness
  verdict moves — `PRODUCT-DAC-001` stays no-WebFlash / no-release;
  `WEBFLASH-DAC-001`, `RELEASE-DAC-001`, and `WF-IMPORT-DAC-001` stay
  **blocked**; `S360-312` `schematic_status` stays `cataloged_unverified`;
  no `webflash_build_matrix` flip, no `artifact_name`, no release
  artifact, no compliance / safety claim. The product YAML and
  `config/product-catalog.json` are unchanged (their full-compile-owed
  narrative is a separate follow-up). FanRelay carries no
  `compile_validation_status` field and is unchanged.
- **2026-05-26 — `WEBFLASH-DAC-001-READINESS` (this PR; docs-only).**
  Re-evaluated the FanDAC WebFlash-exposure readiness after the
  `WEBFLASH-DRIFT-001` / PR #595 audit, **without exposing FanDAC to
  WebFlash**. The product-layer disposition is **unchanged** —
  product-YAML-landed + WebFlash-blocked + `validated-full-compile`. The
  full re-evaluated DAC WebFlash readiness table (gate / status /
  evidence / next action) is recorded in
  [`webflash-exposure-readiness-matrix.md` §DAC / S360-312 WebFlash posture](webflash-exposure-readiness-matrix.md#dac--s360-312-webflash-posture):
  the package / product / full-compile / `compile_validation_status` /
  `voltage`-enum / config-posture-hardware / `FanDAC ↔ AirIQ` mutex gates
  are `CLOSED` (stronger than FanRelay — DAC's compile-status flag is
  already set, so there is no compile-flag gap); WebFlash wrapper /
  `config/webflash-builds.json` row / `artifact_name` / release artifact /
  import-source / voltage-mode UX / compliance are `BLOCKING`; live
  `sense360store/WebFlash` re-verification and the still-owed `S360-312`
  module-availability classification (`WEBFLASH-DRIFT-001` row #17) are
  `NEEDS-TOOLING` (read access denied this session); the `J3` silkscreen
  transposition and Cloudlift S12 harness / product-bench caveats remain
  `NEEDS-OPERATOR-INPUT`. **The recommended next DAC PR is
  `WEBFLASH-DAC-LIVE-CHECK-001`, not `WEBFLASH-DAC-002-WRAPPER-PLAN`
  and not `WEBFLASH-DAC-001`** (non-WebFlash gates are not all clean). No
  `config/`, `packages/`, `products/`, `products/webflash/`, test,
  workflow, firmware, or `sense360store/WebFlash` edit; no
  `webflash_build_matrix` flip; no `artifact_name`; no `schematic_status` /
  `schematic_file` promotion (`S360-312` stays `cataloged_unverified`); no
  COMPLIANCE-001 movement; the `FanDAC ↔ AirIQ` mutex is not relaxed.
  **No claim of FanDAC WebFlash-readiness, release-readiness, WebFlash
  import-readiness, compliance-clearance, board-level safety
  certification, or hardware-stable readiness.**
- **2026-05-27 — `DAC-BLOCKER-RECLASSIFY-001` (this PR; docs-only) — scope
  of the remaining gaps clarified.** The remaining FanDAC `J3`-silk /
  Cloudlift S12 harness + product-bench / voltage-UX / `schematic_status` /
  WebFlash gaps are **reclassified by release scope**: they are **not**
  blockers for the **product layer** recorded here (product YAML,
  compile-only target, `config/` / product-catalog presence, and the
  no-WebFlash `hardware-pending` posture), nor for future clean repo / YAML
  / firmware cleanup PRs that do not expose WebFlash / release. They
  **stay** blockers only for WebFlash exposure, release artifacts, import
  readiness, hardware-stable promotion, the production voltage-control /
  product claim, the Cloudlift S12 product claim, and compliance.
  **Product-layer disposition is unchanged** — product-YAML-landed +
  WebFlash-blocked + `validated-full-compile` + `voltage_enum_fixed: true` +
  `hardware-pending`; this PR adds **no** product YAML and changes no
  status. The `J3` `out0`/`out1` silkscreen transposition is a product /
  installation-documentation and WebFlash / release blocker only (not a
  package / product-YAML blocker); the Cloudlift S12 harness / product bench
  is a Cloudlift product-claim / WebFlash / release blocker only;
  voltage-mode UX is a WebFlash / product UX blocker only; the `DAC-7`
  no-simultaneous-per-output-0–5 V / 0–10 V constraint stays correct.
  Canonical table in
  [`s360-312-r4-fandac.md` §DAC-BLOCKER-RECLASSIFY-001](hardware/s360-312-r4-fandac.md#dac-blocker-reclassify-001--fandac-remaining-blockers-reclassified-by-release-scope-2026-05-27);
  cross-lane copy in
  [`blocker-burndown.md` §2B](blocker-burndown.md#2b-fandac--s360-312).
  **`S360-312-BENCH-RESULT-001`** stays the later bench-evidence PR and
  WebFlash stays separate and blocked (`WEBFLASH-DAC-LIVE-CHECK-001`). No
  `config/` / `packages/` / `products/` / `products/webflash/` / test /
  workflow / firmware / `sense360store/WebFlash` edit; no
  `webflash_build_matrix` flip; no `artifact_name`; no WebFlash / import /
  release / compliance / hardware-stable / Cloudlift-ready claim; `S360-312`
  stays `cataloged_unverified`; no fabricated evidence.
- **2026-05-27 — `S360-312-BENCH-EVIDENCE-REQUEST-001` (this PR;
  docs-only).** The product-layer disposition is **unchanged** —
  product-YAML-landed + WebFlash-blocked + `validated-full-compile` +
  `voltage_enum_fixed: true` + `hardware-pending`. This PR adds **no**
  product YAML and changes no status; it turns the still-open FanDAC bench
  blockers (`DAC-8b` / `DAC-8c` / `DAC-8d` / `DAC-12`) into an
  operator-answerable bench checklist + pass/fail evidence contract in
  [`s360-312-r4-fandac.md` §S360-312-BENCH-EVIDENCE-REQUEST-001](hardware/s360-312-r4-fandac.md#s360-312-bench-evidence-request-001--fandac-bench-evidence-checklist--contract-2026-05-27)
  and
  [`blocker-burndown.md` §5C](blocker-burndown.md#5c-s360-312-bench-evidence-request-001--fandac-detailed-bench-checklist--evidence-contract-2026-05-27).
  A fresh Drive re-search found **no** new FanDAC bench evidence — only
  design / CAD material (the `Fan_GP8403` KiCad / gerber / CPL snapshot set,
  the canonical `S360-312-R4.pdf` schematic already committed
  byte-identical, and the unchanged `Sense360_R4_Tracker`), recorded for
  provenance only and committing no Drive file. The `J3` silkscreen
  transposition (`DAC-8b`), Cloudlift S12 harness + product bench
  (`DAC-8c` / `DAC-8d`), and voltage-mode / output-linearity (`DAC-12`)
  stay `NEEDS-OPERATOR-INPUT` / `NEEDS BENCH`; the `DAC-7`
  no-simultaneous-per-output-0–5 V / 0–10 V constraint stays correct.
  **Recommended next DAC PR: `S360-312-BENCH-RESULT-001`, gated until the
  operator uploads / answers the checklist** — WebFlash wrapper / release /
  import PRs stay blocked. No `config/` / `packages/` / `products/` /
  `products/webflash/` / test / workflow / firmware / `sense360store/WebFlash`
  edit; no `webflash_build_matrix` flip; no `artifact_name`; no WebFlash /
  import / release / compliance / hardware-stable / Cloudlift-ready claim;
  `S360-312` stays `cataloged_unverified`.
- **Cross-references.**
  [`docs/hardware/s360-312-r4-fandac.md`](hardware/s360-312-r4-fandac.md);
  [`docs/hardware/s360-312-r4-dac.md`](hardware/s360-312-r4-dac.md);
  [`board-readiness-matrix.md` `S360-312` notes](hardware/board-readiness-matrix.md#s360-312-sense360-dac);
  [`package-readiness-matrix.md` `fan_gp8403.yaml` / S360-312](hardware/package-readiness-matrix.md#fan_gp8403yaml--s360-312).

### FanTRIAC / S360-320

- **Status.** `timing/compliance-pending` + `needs-package-reconciliation`
  + `blocked-from-standard-exposure` + `advanced/manual-warning-only`
  (policy-recorded by PRODUCT-TRIAC-001 as a notes-only catalog edit;
  see [`config/product-catalog.json`](../config/product-catalog.json)
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` `notes` field and
  [`docs/hardware/s360-320-r4-triac.md` Advanced / manual-warning product posture](hardware/s360-320-r4-triac.md#advanced--manual-warning-product-posture)) +
  `not-recommended` + `not-required-configs` + `not-kit`
  + `not-webflash-default`. The JSON lifecycle row stays
  `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`;
  no new lifecycle enum value was added.
- **Why no product YAML and no status flip.** The required
  package
  [`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml)
  is `timing/compliance-pending` + `needs-package-reconciliation`
  + `blocked-from-standard-exposure` per
  [`package-readiness-matrix.md` `fan_triac.yaml` / S360-320](hardware/package-readiness-matrix.md#fan_triacyaml--s360-320):
  `ac_dimmer` requires direct interrupt-capable ESP32 GPIOs and
  rejects SX1509-routed pins; the placeholder
  `fan_triac_gate_pin: GPIO5` / `fan_triac_zc_pin: GPIO6` in the
  blocked reference product collide with RoomIQ J10
  (`IO5 = SEN0609_TX`, `IO6 = out(gpio6)`); HW-005 is open;
  COMPLIANCE-001 is not cleared. The existing blocked reference
  entry `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` is retained verbatim
  (`status: blocked`, `blocker: HW-005`,
  `webflash_build_matrix: false`) as the canonical placeholder.
- **Product YAML action now.** None. **No new FanTRIAC product
  YAML is added; no sibling combination is proposed; no status
  flip.** The BLOCKED banner in the canonical YAML and the BLOCKED
  banner in the wrapper stay; the parse-only placeholder GPIOs
  stay.
- **WebFlash exposure class (long-term posture, intent only).**
  When and only when HW-005 unblocks, HW-PINMAP-320-FOLLOWUP
  closes, bench timing / waveform / real-load evidence arrives,
  COMPLIANCE-001 advanced / manual-warning sign-off lands, and
  `PACKAGE-TRIAC-001` reconciles
  [`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml),
  the resulting FanTRIAC product surface is `advanced/manual-warning-only`
  + `blocked-from-standard-exposure` + `not-recommended` +
  `not-required-configs` + `not-kit` + `not-webflash-default`.
  Explicitly: **FanTRIAC is not Release-One, not REQUIRED_CONFIGS,
  not recommended, not kit / default, not compliance-certified.**
  WebFlash exposure (if any) requires an explicit advanced-flow
  UX, a manual-warning acknowledgement gate, and a separate
  WF-TRIAC-001 wrapper / catalog / build-matrix slice with its own
  COMPLIANCE-001-derived guard. PRODUCT-GAP-001 does not authorise
  any of this; it records the policy.
- **Follow-up owner.** `PRODUCT-TRIAC-001` has **landed** as a
  wording-only / notes-only catalog reclassification on
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` in
  [`config/product-catalog.json`](../config/product-catalog.json);
  the structural fields (`status: blocked`, `blocker: HW-005`,
  `reason`, `webflash_build_matrix: false`, no `artifact_name`) are
  unchanged, and no new lifecycle enum value was added.
  `PRODUCT-TRIAC-002` (FanTRIAC product YAML / catalog-entry
  rework) has been **investigated and deferred**: every gate it
  depends on is still open. `PACKAGE-TRIAC-001` has not landed;
  [`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml)
  still carries the BLOCKED / UNVERIFIED banner with placeholder
  `fan_triac_gate_pin: GPIO5` / `fan_triac_zc_pin: GPIO6`; `HW-005`,
  `HW-PINMAP-320-FOLLOWUP`, and `COMPLIANCE-001` all remain open.
  No product YAML, no WebFlash wrapper, no catalog edit (notes or
  structural), no build-matrix entry, no release artifact, and no
  WebFlash import is added by the PRODUCT-TRIAC-002 investigation;
  the docs-only deferral note is recorded in
  [`docs/cleanup-audit.md` PRODUCT-TRIAC-002 update](cleanup-audit.md#product-triac-002-update-deferred--package-triac-001-not-landed).
  The remaining chain is: `HW-005` unblock (Option (a) direct-ESP32
  pair or Core respin) + `HW-PINMAP-320-FOLLOWUP` + bench
  timing / waveform / real-load evidence + `COMPLIANCE-001`
  advanced / manual-warning sign-off → `PACKAGE-TRIAC-001` →
  `PRODUCT-TRIAC-002` (FanTRIAC product YAML slice; **must not**
  add to Release-One, REQUIRED_CONFIGS, kit / default, recommended,
  or compliance-certified surfaces) → `WF-TRIAC-001` (WebFlash
  advanced-flow wrapper / catalog / build with the manual-warning
  UX gate) → `RELEASE-TRIAC-001` (advanced-channel build / release
  artifact) → `WF-IMPORT-TRIAC-001` (advanced / manual artifact
  import). `PRODUCT-TRIAC-002` cannot proceed from `WF-TRIAC-001`
  having landed in the WebFlash repo (runtime advanced /
  manual-warning UX gate) alone; it **remains deferred** and is
  gated by `PACKAGE-TRIAC-001` (currently deferred), `HW-005`,
  `HW-PINMAP-320-FOLLOWUP`, and `COMPLIANCE-001`. After
  `PACKAGE-TRIAC-001` deferral, `RELEASE-TRIAC-001` and
  `WF-IMPORT-TRIAC-001` are likewise **blocked**, and the in-repo
  `WF-TRIAC-001` wrapper / catalog / build slice remains
  outstanding; see
  [`docs/cleanup-audit.md` §TRIAC-QUEUE-001 update](cleanup-audit.md#triac-queue-001-update-remaining-fantriac-chain-normalized-after-package-deferral).
- **Cross-references.**
  [`docs/hardware/s360-320-r4-triac.md` Advanced / manual-warning product posture](hardware/s360-320-r4-triac.md#advanced--manual-warning-product-posture);
  [`board-readiness-matrix.md` `S360-320` notes](hardware/board-readiness-matrix.md#s360-320-sense360-triac);
  [`package-readiness-matrix.md` `fan_triac.yaml` / S360-320](hardware/package-readiness-matrix.md#fan_triacyaml--s360-320);
  [`release-one-hardware-audit.md` FanTRIAC mapping resolution](release-one-hardware-audit.md#fantriac-mapping-resolution);
  [`compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md).

### PWR-240V / S360-400

- **Status.** `schematic-evidence-pending` + `needs-package-reconciliation`
  + `timing/compliance-pending` (compliance-gated). Class unchanged
  by HW-PINMAP-400-FOLLOWUP, by the 2026-05-19
  `PACKAGE-POWER-400-001` investigation pass merged as **PR #520**,
  or by the 2026-05-19 `PRODUCT-POWER-400-001` investigation pass
  (this PR). The per-board audit doc
  [`docs/hardware/s360-400-r4-power.md`](hardware/s360-400-r4-power.md)
  is now `partial — schematic evidence available; package
  reconciliation, BOM, silkscreen, creepage/clearance, and
  COMPLIANCE-001 pending` after HW-PINMAP-400-FOLLOWUP consumed
  the HW-ASSETS-400 (PR #514) schematic; PR #520 re-confirmed all
  five `PACKAGE-POWER-400-001` preconditions remain open without
  editing the package, the catalog, or the JSON `schematic_status`.
- **Why no product YAML.** The required package
  [`packages/hardware/power_240v.yaml`](../packages/hardware/power_240v.yaml)
  is `schematic-evidence-pending` + `needs-package-reconciliation`
  + `timing/compliance-pending` per
  [`package-readiness-matrix.md` `power_240v.yaml` / S360-400](hardware/package-readiness-matrix.md#power_240vyaml--s360-400).
  The `S360-400-R4` module-side schematic is committed under
  HW-ASSETS-400 (PR #514) at
  [`docs/hardware/schematics/S360-400-R4.pdf`](hardware/schematics/S360-400-R4.pdf)
  with curated artifact index at
  [`docs/hardware/artifacts/S360-400-R4.md`](hardware/artifacts/S360-400-R4.md);
  HW-PINMAP-400-FOLLOWUP consumed both and confirms a three-way
  AC/DC part-identity disagreement: the package header says
  `HLK-PM01 or similar`, the catalog says `HLK-5M05`, and the
  schematic shows `PS1 = HLK-10M05`. BOM cross-check, silkscreen
  pin-1, and creepage / clearance evidence remain owed to
  evidence-bearing follow-up slices and to `PACKAGE-POWER-400-001`.
  Input / output / isolation / protection ratings are
  package-header text only; COMPLIANCE-001 mains-voltage UK / EU
  sign-off is a separate, additional gate before any PWR-bearing
  **product** promotion. The four `legacy-compatible` `*-pwr` Core
  variants in
  [`products/`](../products/)
  (`sense360-core-c-pwr.yaml`, `sense360-core-w-pwr.yaml`,
  `sense360-core-v-c-pwr.yaml`, `sense360-core-v-w-pwr.yaml`)
  remain manual-only and stay out of the WebFlash matrix.
- **Product YAML action now.** None.
- **WebFlash exposure class.** `none`. After `PACKAGE-POWER-400-001`
  the future PWR-240V product surface (if any) is
  `production-candidate` **only after** `COMPLIANCE-001`
  `S360-400` slice clears; until then `not-webflash-default`.
- **Follow-up owner.** `HW-ASSETS-400` *(landed at PR #514)* →
  `HW-PINMAP-400-FOLLOWUP` *(this PR; docs-only schematic-backed
  reconciliation; product row unchanged)* → BOM cross-check +
  silkscreen + creepage / clearance + bench / load / thermal /
  EMI evidence (separate slices) → `S360-400` `schematic_status`
  promotion (separate JSON PR) → `COMPLIANCE-001` `S360-400`
  slice (independent track) → `PACKAGE-POWER-400-001` →
  `PRODUCT-POWER-400-001` (this matrix's named PWR-240V product
  slice).
- **Cross-references.**
  [`docs/hardware/artifacts/S360-400-R4.md`](hardware/artifacts/S360-400-R4.md);
  [`docs/hardware/s360-400-r4-power.md`](hardware/s360-400-r4-power.md);
  [`docs/hardware/s360-400-r4-power.md` HW-PINMAP-400-FOLLOWUP audit log](hardware/s360-400-r4-power.md#hw-pinmap-400-followup-audit-log);
  [`board-readiness-matrix.md` `S360-400` notes](hardware/board-readiness-matrix.md#s360-400-sense360-240v-psu);
  [`package-readiness-matrix.md` `power_240v.yaml` / S360-400](hardware/package-readiness-matrix.md#power_240vyaml--s360-400);
  [`compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md).

- **2026-05-19 — `PRODUCT-POWER-400-001` investigation pass
  (Path A docs-only deferral).** Re-verified against the live
  files: no S360-400-explicit / `PWR`-bearing WebFlash-shippable
  product YAML exists under [`products/`](../products/) or
  [`products/webflash/`](../products/webflash/);
  [`config/product-catalog.json`](../config/product-catalog.json)
  has no S360-400-specific product (the only `pwr`-bearing rows
  are the four `legacy-compatible` Core variants
  [`sense360-core-c-pwr.yaml`](../products/sense360-core-c-pwr.yaml),
  [`sense360-core-w-pwr.yaml`](../products/sense360-core-w-pwr.yaml),
  [`sense360-core-v-c-pwr.yaml`](../products/sense360-core-v-c-pwr.yaml),
  and
  [`sense360-core-v-w-pwr.yaml`](../products/sense360-core-v-w-pwr.yaml);
  each is `status: legacy-compatible` /
  `webflash_build_matrix: false` / no `config_string` / no
  `webflash_wrapper` / no `artifact_name`; those four products
  consume the logical `power_240v.yaml` package without explicit
  `S360-400` binding and are **not** S360-400-specific
  product-readiness evidence);
  [`config/webflash-builds.json`](../config/webflash-builds.json)
  has no `PWR` build (only Release-One
  `Ceiling-POE-VentIQ-RoomIQ` `stable` and
  `Ceiling-POE-VentIQ-RoomIQ-LED` `preview`);
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  reserves `PWR` in `canonical_power: ["USB", "POE", "PWR"]` but
  no `webflash_build_matrix: true` row consumes it; and
  [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  `S360-400` row at lines 102–110 still records
  `schematic_status: cataloged_unverified` with no
  `schematic_file` (asserted by
  [`tests/test_hardware_catalog.py:53`](../tests/test_hardware_catalog.py)
  `EXPECTED_STILL_UNVERIFIED_SKUS = frozenset({"S360-320",
  "S360-400"})`). Six preconditions remain open: (1)
  `PACKAGE-POWER-400-001` implementation slice has not landed
  (only the docs-only investigation pass merged as PR #520; the
  package YAML header reconciliation, the catalog `description`
  reconciliation, the `S360-400` `schematic_status: verified`
  JSON promotion, and the BOM citation that PR #520 enumerated as
  the required atomic slice all remain owed); (2) BOM cross-check
  missing; (3) `S360-400` `schematic_status: verified` JSON PR
  not landed; (4) `COMPLIANCE-001` `S360-400` slice still open
  (last re-checked PR #506); (5) package / catalog reconciliation
  owed to `PACKAGE-POWER-400-001` (the three-way `HLK-5M05` /
  `HLK-PM01 or similar` / `HLK-10M05` AC/DC part-identity
  disagreement and the input / output / isolation / protection /
  fusing header text in
  [`packages/hardware/power_240v.yaml`](../packages/hardware/power_240v.yaml)
  remain unresolved and BOM-bound); (6) product-onboarding
  approval missing per the [Core rule](#core-rule) of this
  matrix. Path B (documentation / catalog-note-only cleanup) is
  not useful right now because this section and the matching
  sections of
  [`webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md)
  and
  [`release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
  already correctly classify the slice; Path C (implementation)
  is unsafe because adding a product YAML while
  [`power_240v.yaml`](../packages/hardware/power_240v.yaml)
  carries `schematic-evidence-pending` +
  `needs-package-reconciliation` +
  `timing/compliance-pending` would break the
  [Core rule](#core-rule). The next `PRODUCT-POWER-400-001` PR
  must land **the canonical S360-400 / `PWR`-bearing product
  YAML + the matching `config/product-catalog.json` entry + the
  legacy-compatible `*-pwr` Core variant relationship decision
  (retain / migrate / coexist) as a single atomic slice**, not as
  a documentation cleanup alone, and only after
  `PACKAGE-POWER-400-001` implementation, the `S360-400`
  `schematic_status: verified` JSON PR, the `COMPLIANCE-001`
  `S360-400` slice, and product-onboarding approval all land.
  Release-One stays `Ceiling-POE-VentIQ-RoomIQ` / version
  `1.0.0` / channel `stable`; LED preview stays
  `Ceiling-POE-VentIQ-RoomIQ-LED` / `status: preview` /
  `channel: preview`; FanTRIAC stays `status: blocked` /
  `blocker: HW-005` / `webflash_build_matrix: false`. No
  package, product, WebFlash, build, release, compliance, JSON
  catalog, test, script, workflow, component, include, firmware,
  or manifest edits; no `schematic_status` / `schematic_file`
  promotion; no COMPLIANCE-001 movement; no `REQUIRED_CONFIGS` /
  kit change. Investigation outcome cross-recorded at
  [`docs/cleanup-audit.md` §`PRODUCT-POWER-400-001 update (2026-05-19 — docs-only investigation pass)`](cleanup-audit.md#product-power-400-001-update-2026-05-19--docs-only-investigation-pass).

- **2026-05-20 — `PACKAGE-POWER-400-001` package-header cleanup
  (Path B / limited implementation).** Following the
  `HW-BOM-ASSETS-002` / PR #535 BOM-confirmation of
  `PS1 = HLK-5M05` (HI-LINK), the comment-only header cleanup of
  [`packages/hardware/power_240v.yaml`](../packages/hardware/power_240v.yaml)
  that PR #515 and PR #520 deferred has now landed under Path B:
  the disproved `HLK-PM01 or similar` claim is removed, the
  BOM-confirmed part identity (`PS1 = HLK-5M05 (HI-LINK)`) and
  BOM-confirmed populated protection / connector components
  (`F1 A250-1200`, `RV1 10D391K`, `C1 470nF`, `J1` WAGO
  2601-3103, `J2` JST SH `SM02B-SRSS-TB(LF)(SN)`) are now named
  in the header, input / output / isolation / protection ratings
  are reclassified as vendor-datasheet typicals (not BOM-confirmed
  and not compliance evidence), the misleading `1A recommended`
  AC-input fusing line is removed, and the header restates that
  mains-voltage UK / EU compliance is tracked by COMPLIANCE-001
  and remains OPEN. Runtime YAML behavior is unchanged
  (substitutions / globals / sensors / binary_sensor / logger
  blocks preserved byte-for-byte). `PRODUCT-POWER-400-001` row
  class is unchanged — the product YAML slice **stays blocked**
  on the residual coordinated `PACKAGE-POWER-400-001` work
  (the `S360-400` `schematic_status: verified` JSON-only PR is
  additionally gated on the schematic-side correction of the
  committed PDF's `PS1 = HLK-10M05` value-field string), on
  COMPLIANCE-001 `S360-400` slice closure, on the silkscreen /
  PCB / creepage / clearance / bench / thermal / EMI evidence,
  and on product-onboarding approval. The four
  `legacy-compatible` `*-pwr` Core variants
  (`sense360-core-c-pwr.yaml` / `sense360-core-w-pwr.yaml` /
  `sense360-core-v-c-pwr.yaml` / `sense360-core-v-w-pwr.yaml`)
  stay `legacy-compatible` and `webflash_build_matrix: false`;
  Release-One / LED preview / FanTRIAC identities unchanged. No
  product, WebFlash, build, release, compliance, JSON catalog,
  test, script, workflow, component, include, firmware, or
  manifest edits. Outcome cross-recorded at
  [`docs/hardware/s360-400-r4-power.md` §2026-05-20 — PACKAGE-POWER-400-001 package-header cleanup](hardware/s360-400-r4-power.md#2026-05-20--package-power-400-001-package-header-cleanup-bom-confirmed-part-identity-in-header-ratings-softened-downstream-slices-still-blocked),
  [`docs/hardware/package-readiness-matrix.md` `power_240v.yaml` / S360-400](hardware/package-readiness-matrix.md#power_240vyaml--s360-400),
  [`docs/hardware/firmware-package-mapping-audit.md` `power_240v.yaml` AC/DC part-identity disagreement (S360-400)](hardware/firmware-package-mapping-audit.md#power_240vyaml-acdc-part-identity-disagreement-s360-400),
  and
  [`docs/cleanup-audit.md` §`PACKAGE-POWER-400-001 update (2026-05-20 — Path B package-header cleanup)`](cleanup-audit.md#package-power-400-001-update-2026-05-20--path-b-package-header-cleanup).

### PoE-410 / S360-410

- **Status.** `reference-only` + `schematic-evidence-pending`
  (schematic landed under HW-ASSETS-410 / PR #516 and was consumed
  by HW-PINMAP-410-FOLLOWUP; package-header reconciliation still
  owed) + `do-not-change-release-one`.
- **Why no product YAML.** The required package
  [`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml)
  is `reference-only` (logical PoE-power package; emits diagnostic
  sensors only, binds no GPIOs) + `schematic-evidence-pending` +
  `do-not-change-release-one` per
  [`package-readiness-matrix.md` `power_poe.yaml` / S360-410](hardware/package-readiness-matrix.md#power_poeyaml--s360-410).
  Module-side schematic now committed under HW-ASSETS-410 / PR #516
  and consumed by HW-PINMAP-410-FOLLOWUP — the HW-PINMAP-410 audit
  doc at [`docs/hardware/s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md)
  is now `partial — schematic evidence available; package
  reconciliation, PoE PD controller / magnetics / buck / isolated
  DC/DC / harness identity evidence pending`. The
  package-header whole-module `Ag9712M / Silvertel Ag9700 / or
  similar` hint vs the schematic-shown discrete topology
  (`TPS2378DDAR / TX4138 / F0505S-2WR2 / RJP-003TC1(LPJ4112CNL)`)
  is recorded as **unresolved** — BOM evidence is required before
  `PACKAGE-POE-410-001` can resolve the part identity. Release-One
  [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml)
  consumes the package today under the documented
  "schematic verification pending" caveat in
  [`release-one-hardware-audit.md` Findings → PoE PSU](release-one-hardware-audit.md#findings).
  PRODUCT-GAP-001 **does not** add a sibling PoE-410 product YAML,
  **does not** requalify Release-One, and **does not** promote the
  caveat away. Adding a new product YAML that explicitly subjects
  the PoE PSU as a verified module is gated on
  `PACKAGE-POE-410-001` (BOM-bound) and the separate `S360-410`
  `schematic_status: verified` JSON-only PR.
- **Product YAML action now.** None. Release-One stays
  `Ceiling-POE-VentIQ-RoomIQ`, `status: production`,
  `channel: stable`, version `1.0.0`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`. LED
  preview stays `Ceiling-POE-VentIQ-RoomIQ-LED`,
  `status: preview`, `channel: preview`, version `1.0.0`,
  artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`.
- **WebFlash exposure class.** Release-One's existing
  `production-candidate` exposure is unchanged. No new PoE-410
  candidate is on the WebFlash surface.
- **Follow-up owner.** `HW-ASSETS-410` (merged as PR #516) →
  `HW-PINMAP-410-FOLLOWUP` (schematic-backed partial audit; this
  PR) → BOM cross-check → `HW-002 OQ#6` closure /
  `S360-100-BENCH-001` update → `S360-410`
  `schematic_status: verified` JSON-only PR → `PACKAGE-POE-410-001`
  → separate later Release-One caveat-closure PR +
  `PRODUCT-POE-410-001` (only if a new explicitly-PoE-subject
  product is warranted; otherwise the slice closes by promoting
  the caveat alone).
- **Cross-references.**
  [`docs/hardware/s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md);
  [`board-readiness-matrix.md` `S360-410` notes](hardware/board-readiness-matrix.md#s360-410-sense360-poe-psu);
  [`package-readiness-matrix.md` `power_poe.yaml` / S360-410](hardware/package-readiness-matrix.md#power_poeyaml--s360-410);
  [`release-one-hardware-audit.md` Findings → PoE PSU](release-one-hardware-audit.md#findings).

- **2026-05-20 — `PRODUCT-POE-410-001` investigation pass
  (Path A docs-only deferral).** Re-verified against the live
  files: no S360-410-explicit / `POE`-410-subject
  WebFlash-shippable product YAML exists under
  [`products/`](../products/) or
  [`products/webflash/`](../products/webflash/). The three
  shipping PoE entries in
  [`config/product-catalog.json`](../config/product-catalog.json)
  (`Ceiling-POE-VentIQ-RoomIQ` `status: production` /
  `channel: stable`, `Ceiling-POE-VentIQ-RoomIQ-LED`
  `status: preview` / `channel: preview`, and
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` `status: blocked` /
  `blocker: HW-005` / `webflash_build_matrix: false`) each
  carry `hardware.poe: "S360-410"` as a catalog-level
  mapping field only — they consume the **logical**
  [`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml)
  package under Release-One identity and the preserved
  schematic-pending caveat, **not** as S360-410-subject
  product-readiness evidence; the six `legacy-compatible`
  `*-poe` Core variants
  ([`sense360-core-c-poe.yaml`](../products/sense360-core-c-poe.yaml),
  [`sense360-core-w-poe.yaml`](../products/sense360-core-w-poe.yaml),
  [`sense360-core-v-c-poe.yaml`](../products/sense360-core-v-c-poe.yaml),
  [`sense360-core-v-w-poe.yaml`](../products/sense360-core-v-w-poe.yaml),
  [`sense360-poe.yaml`](../products/sense360-poe.yaml),
  [`sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml))
  stay `legacy-compatible` / `webflash_build_matrix: false`
  and are also **not** S360-410-subject product-readiness
  evidence;
  [`config/webflash-builds.json`](../config/webflash-builds.json)
  has only the Release-One `stable` build and the LED
  `preview` build (no new PoE-410-explicit build);
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  reserves `POE` in `canonical_power: ["USB", "POE", "PWR"]`
  consumed by both committed builds (POE reservation does
  **not** imply S360-410-subject product readiness);
  `release_one_required_configs` stays
  `["Ceiling-POE-VentIQ-RoomIQ"]`;
  [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  `S360-410` row at lines 112–121 still records
  `schematic_status: cataloged_unverified` with no
  `schematic_file` and `description: "PoE to 5V."`;
  [`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml)
  stays byte-identical to PR #517 / PR #526 state. Eight
  preconditions remain open: (1) `PACKAGE-POE-410-001`
  implementation slice has not landed (only the docs-only
  investigation pass merged as PR #526; the package-header
  reconciliation against the schematic-shown discrete
  topology, the catalog `description` reconciliation (if
  applicable), the BOM citation, and the `S360-410`
  `schematic_status: verified` JSON promotion all remain
  owed); (2) BOM cross-check missing; (3) `S360-410`
  `schematic_status: verified` JSON PR not landed; (4)
  HW-002 OQ#6 / `S360-100-BENCH-001` J2-harness identity
  closure missing; (5) package-header reconciliation owed to
  `PACKAGE-POE-410-001` (the `Ag9712M, Silvertel Ag9700, or
  similar` whole-module hint vs schematic-shown discrete
  topology stays unresolved and BOM-bound); (6) Release-One
  PoE "schematic verification pending" caveat closure
  missing (preserved verbatim, owed to a separate later PR);
  (7) product-onboarding approval missing per the
  [Core rule](#core-rule); (8) product / catalog readiness
  approval missing (no-new-entry vs new-entry decision
  belongs to this slice and has not been made; per the
  [Follow-up PR sequence](#follow-up-pr-sequence) row,
  `PRODUCT-POE-410-001` "often will close by promoting
  Release-One's preserved schematic-pending caveat alone,
  without adding a new product entry"). Path B
  (documentation / catalog-note-only cleanup) is not useful
  right now because this section and the matching sections
  of
  [`webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md)
  and
  [`release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
  already correctly classify the slice; Path C
  (implementation) is unsafe because adding a
  S360-410-subject product YAML while
  [`power_poe.yaml`](../packages/hardware/power_poe.yaml)
  stays `reference-only` + `schematic-evidence-pending` +
  `do-not-change-release-one` would break the
  [Core rule](#core-rule), and adding a sibling PoE-410
  product entry while the Release-One PoE caveat is
  preserved would implicitly requalify Release-One —
  explicitly forbidden by PR #526 and by every prior PoE-410
  follow-up document. The next `PRODUCT-POE-410-001` PR
  must land **the no-new-entry vs new-entry decision +
  (if a new entry is warranted) the canonical S360-410 /
  `POE`-410-subject product YAML + the matching
  `config/product-catalog.json` entry as a single atomic
  slice**, not as a documentation cleanup alone, and only
  after `PACKAGE-POE-410-001` implementation, the
  Release-One PoE caveat-closure PR, and product-onboarding
  approval all land. The Release-One product
  (`Ceiling-POE-VentIQ-RoomIQ` / version `1.0.0` / channel
  `stable` / artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`),
  the LED preview (`Ceiling-POE-VentIQ-RoomIQ-LED` /
  `status: preview` / `channel: preview` / version
  `1.0.0` / artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`),
  and the FanTRIAC blocked reference are all preserved.
  See
  [`docs/cleanup-audit.md` §`PRODUCT-POE-410-001 update (2026-05-20 — docs-only investigation pass)`](cleanup-audit.md#product-poe-410-001-update-2026-05-20--docs-only-investigation-pass).

## Release-One and LED preview safety

PRODUCT-GAP-001 **does not change Release-One product behaviour** and
**does not change the LED preview**. Both entries are **explicitly
out of scope** for this PR:

- **Release-One** — config string `Ceiling-POE-VentIQ-RoomIQ`,
  `status: production`, `channel: stable`, version `1.0.0`,
  artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`,
  tag `v1.0.0`. Canonical YAML
  [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml).
  Wrapper
  [`products/webflash/ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml).
  REQUIRED_CONFIGS membership in
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  preserved. `blocked_modules: [FanTRIAC, LED]` preserved.
- **LED preview** — config string
  `Ceiling-POE-VentIQ-RoomIQ-LED`, `status: preview`,
  `channel: preview`, version `1.0.0`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`.
  Canonical YAML
  [`products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq-led.yaml).
  Wrapper
  [`products/webflash/ceiling-poe-ventiq-roomiq-led.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq-led.yaml).
  `blocked_modules: [FanTRIAC]` preserved. Bench-verification
  Open Questions in
  [`docs/hardware/s360-300-r4-led.md`](hardware/s360-300-r4-led.md)
  remain carried as preview-stage caveats.

Explicit LED preview guardrails for PRODUCT-GAP-001:

- **No LED stable promotion.** The LED preview stays
  `status: preview`, `channel: preview`. Promotion to
  `production` / `stable` requires the full 17-row
  [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
  gate; PRODUCT-GAP-001 does not perform any RELEASE-006
  promotion.
- **No LED REQUIRED_CONFIGS.** `release_one_required_configs` in
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  stays `["Ceiling-POE-VentIQ-RoomIQ"]`. The LED preview is not
  added.
- **No LED kit.** No entry is added to
  `scripts/data/kits.json` (WebFlash-owned). PRODUCT-GAP-001 makes
  no kit / default / recommended-list change of any kind.

Explicit FanTRIAC guardrails for PRODUCT-GAP-001:

- **FanTRIAC entry stays blocked.**
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`, `status: blocked`,
  `blocker: HW-005`, `webflash_build_matrix: false`. The BLOCKED
  banner in
  [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml)
  and in
  [`products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml)
  stays. The parse-only placeholder GPIOs stay. HW-005 is **not**
  resolved by PRODUCT-GAP-001. COMPLIANCE-001 is **not** cleared.

## WebFlash exposure gates

WebFlash exposure is a **separate** gate from product YAML
existence. Even after a future PRODUCT-*-001 slice lands a
canonical product YAML, the WebFlash exposure class is decided by a
separate scoped PR with its own gates. PRODUCT-GAP-001 records the
class definitions; it does not move any candidate up the ladder.

| Exposure class | Means | Required to reach |
|---|---|---|
| `none` | No product YAML; no wrapper; no catalog entry; no build-matrix entry; not reachable through WebFlash in any form. | Default for every candidate row in this matrix today. |
| `docs-only` / `manual YAML only` | A canonical YAML may exist under [`products/`](../products/) but the product is `legacy-compatible` (no `config_string`, no `webflash_wrapper`, no `artifact_name`, `webflash_build_matrix: false`); the user installs by manual `esphome run`. | Used today by the 31 `legacy-compatible` entries. PRODUCT-GAP-001 adds none and moves none. |
| `preview-candidate` | Canonical YAML + WebFlash wrapper + catalog entry + build-matrix entry on a non-`stable` channel (typically `preview`); WebFlash-side import optional / staged. | Today used by `Ceiling-POE-VentIQ-RoomIQ-LED` only. Each future preview-candidate addition is a separate `WEBFLASH-GAP-001`-class slice; PRODUCT-GAP-001 adds none. |
| `advanced/manual-warning-only` | Reachable through WebFlash only behind an explicit advanced-flow / manual-warning UX, never on the standard landing list. The wrapper / catalog / build-matrix slice must carry the manual-warning UX gate and (for mains-voltage products) `COMPLIANCE-001` sign-off. | The intended long-term posture for FanTRIAC. Owned by `WF-TRIAC-001`. Today the JSON `status` is `blocked` and no WebFlash surface exists. |
| `production-candidate` | Canonical YAML + WebFlash wrapper + catalog entry + build-matrix entry on `stable`; signed release artifact; WebFlash-side import live. | Today used by Release-One (`Ceiling-POE-VentIQ-RoomIQ`) only. Any new entry must clear the full 17-row [`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md). |
| `legacy-only` | The canonical YAML exists but is `legacy-compatible`; not in the WebFlash matrix and not promoted by PRODUCT-GAP-001. | Today: [`products/sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml), [`products/sense360-poe.yaml`](../products/sense360-poe.yaml), and the 29 `core-*` / `mini-*` legacy entries. |

The rule:

> **Product YAML existence does not automatically mean WebFlash
> exposure. WebFlash wrapper, catalog entry, build-matrix entry,
> release artifact, and WebFlash-side import remain separate gates,
> owned by `WEBFLASH-GAP-001`, `RELEASE-GAP-001`, and
> `WF-IMPORT-GAP-001` respectively. Advanced / manual-warning
> products require an explicit advanced-flow UX and a
> manual-warning acknowledgement before any WebFlash exposure.**

## Follow-up PR sequence

Each entry below is a separate PR with its own scope, review, and
gate evidence. PRODUCT-GAP-001 does not commit to a calendar and
does not order these beyond the dependencies recorded in
[`docs/hardware/board-readiness-matrix.md` Follow-up PR sequence](hardware/board-readiness-matrix.md#follow-up-pr-sequence),
[`docs/hardware/package-readiness-matrix.md` Follow-up PR sequence](hardware/package-readiness-matrix.md#follow-up-pr-sequence),
and the per-board audit docs.

| PR | Purpose | Gated on |
|---|---|---|
| **`PRODUCT-RELAY-001`** (alias: `PRODUCT-GAP-001` FanRelay slice) | **Landed (this PR).** Added the first FanRelay canonical product YAML [`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml) with config string `Ceiling-POE-VentIQ-FanRelay-RoomIQ` per the WebFlash grammar; carries **advanced / manual-warning wording + installation / safety caveat + competent-person caveat** in the product YAML header (per [§FanRelay / S360-310](#fanrelay--s360-310) recommended posture refreshed by `PRODUCT-RELAY-001-READINESS-REFRESH`); passes [`tests/test_product_substitutions.py`](../tests/test_product_substitutions.py) and [`tests/validate_configs.py`](../tests/validate_configs.py); added a non-WebFlash catalog row in [`config/product-catalog.json`](../config/product-catalog.json) (`status: hardware-pending`, `webflash_build_matrix: false`, no `artifact_name`, no `webflash_wrapper`) required by the [`tests/test_product_catalog.py`](../tests/test_product_catalog.py) enumeration; added [`tests/test_relay_product_readiness.py`](../tests/test_relay_product_readiness.py) (42 cases) pinning the structural invariants; tightened [`tests/test_fan_relay_package.py`](../tests/test_fan_relay_package.py) `PackageRelayDoesNotTouchWebFlashOrProductTests` to allow the single PRODUCT-RELAY-001 canonical product YAML while continuing to forbid additional FanRelay product YAMLs / WebFlash wrappers / build-matrix entries. **No compile-only target added.** **Does not** add a WebFlash wrapper, catalog `webflash_build_matrix: true` flip, [`config/webflash-builds.json`](../config/webflash-builds.json) build-matrix row, release artifact, REQUIRED_CONFIGS membership, kit / recommended membership, or stable-channel promotion. WebFlash exposure (if and when appropriate) is owned by a separate `WEBFLASH-RELAY-001` slice with its own gates; the recommended next PR is `WEBFLASH-RELAY-001-READINESS-REFRESH`, not immediate WebFlash exposure. | `PACKAGE-RELAY-001` landed (i.e. `HW-ASSETS-310` + `HW-PINMAP-310-FOLLOWUP` + `CORE-ABSTRACT-BUS-001C` + `CORE-ABSTRACT-BUS-001A` + `S360-310-BENCH-001` + `S360-310-BENCH-EVIDENCE-001` + the package-layer test + readiness reconciliation — **all landed via PR #557 / PR #558 / PR #559 / PR #560 / PR #561 / PR #562**) + `PRODUCT-RELAY-001-READINESS-REFRESH` *(landed PR #563)*. **Note:** "implemented / reconciled at the `PACKAGE-RELAY-001` package layer" explicitly does **not** mean product-ready, WebFlash-ready, release-ready, compliance-cleared, safe for arbitrary mains installation, or verified across production batches; the product-layer blockers in [§FanRelay / S360-310](#fanrelay--s360-310) (production-wide / multi-unit `GPIO3` strap-pin boot characterisation; board-level mains-safety / installation-approval evidence; competent-person sign-off) remain owed to subsequent slices and to any later `WEBFLASH-RELAY-001` motion. |
| **`PRODUCT-PWM-001`** (alias: `PRODUCT-GAP-001` FanPWM slice) | Add the first FanPWM canonical product YAML under [`products/`](../products/) consuming the reconciled [`packages/expansions/fan_pwm.yaml`](../packages/expansions/fan_pwm.yaml); decide the fate of the legacy [`products/sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml) (retain / migrate / remove); follow the [`product-onboarding.md`](product-onboarding.md) safe sequence. **Does not** add a WebFlash wrapper, catalog entry, build-matrix entry, or release artifact. | `PACKAGE-PWM-001` landed (i.e. `HW-PINMAP-311-FOLLOWUP` + `S360-311` `schematic_status: verified` + bench / silkscreen evidence + `CORE-ABSTRACT-BUS-001`). |
| **`FW-COMPILE-DAC-001`** (FanDAC compile-only / config-validation slice) | **Landed (this PR).** Compile-only validation of the implemented FanDAC package (PR #573). Took **Option A**: fixed the `gp8403:` `voltage:` substitutions from the invalid `0-10V` string to the valid ESPHome enum `10V` (customer-facing 0-10V) — ESPHome's documented schema rejects `0-10V` — so the unvalidated-`voltage:`-enum risk is closed **before** any product YAML inherits it. Added the `ceiling-poe-fandac-compile-only` target (`products/compile-only/ceiling-poe-fandac.yaml`, config string `Ceiling-POE-FanDAC`) and extended `tests/test_fandac_package.py` / `tests/test_compile_targets.py`. The `--metadata-only` lane passed; the `esphome config` / `--compile` pass — `compile_validation_status: pending-ci` at this slice's landing — has since **passed** in run `26364679370` and the flag is now `validated-full-compile` (COMPILE-STATUS-FLAGS-001). Compile-only is a validation pass, not a release class: it adds **no** product YAML, WebFlash wrapper, catalog entry, `webflash_build_matrix: true` flip, build-matrix row, `artifact_name`, release artifact, or `preview-candidate` / `production-candidate` promotion. | `PACKAGE-DAC-001` landed *(PR #573)*. |
| **`PRODUCT-DAC-001`** (alias: `PRODUCT-GAP-001` FanDAC slice) | Add the first FanDAC canonical product YAML under [`products/`](../products/) consuming the implemented [`packages/expansions/fan_gp8403.yaml`](../packages/expansions/fan_gp8403.yaml); map the neutral package outputs to **outcome-first** user-facing names (e.g. "0–10V fan control" / "Cloudlift S12 fan control") while keeping the package's neutral output IDs; carry the `J2` / `J3` harness-trace and `J3` silkscreen-transposition caveats into the product / installation docs; treat Nextion / `J7` as out of scope unless the product drives a display; enforce the `fandac_conflicts_with_airiq` mutex (no `AirIQ`-bearing FanDAC product); follow the [`product-onboarding.md`](product-onboarding.md) safe sequence. **Does not** add a WebFlash wrapper, catalog entry, build-matrix entry, or release artifact. | `PACKAGE-DAC-001` landed *(PR #573)* + **`FW-COMPILE-DAC-001`** landed *(this PR — the `voltage:` `0-10V` → `10V` enum fix is applied at the package layer; the CI `--compile` pass is pending)* + `S360-312` `schematic_status: verified` (separate JSON PR). |
| **`PRODUCT-TRIAC-001`** (alias: `PRODUCT-GAP-001` FanTRIAC slice) | **Landed as wording-only / notes-only.** Reclassified the FanTRIAC reference product policy to `advanced/manual-warning-only` via a `notes`-only edit on `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` in [`config/product-catalog.json`](../config/product-catalog.json) plus reinforcement of the listed docs. The JSON `status` stays `blocked`, `blocker` stays `HW-005`, `reason` is unchanged, `webflash_build_matrix` stays `false`, no `artifact_name` is added, and the lifecycle enum is unchanged. **Does not** add FanTRIAC to Release-One, REQUIRED_CONFIGS, kit / default lists, recommended surfaces, or compliance-certified surfaces; preserves all mains-voltage / qualified-electrician warnings. **Does not** add a product YAML, WebFlash wrapper, build-matrix entry, release artifact, or WebFlash import. The product YAML / catalog-entry rework (`PRODUCT-TRIAC-002`) remains outstanding. | None — wording-only catalog reclassification was acceptable without `HW-005` / `COMPLIANCE-001` / `HW-PINMAP-320-FOLLOWUP` / `PACKAGE-TRIAC-001` closure. |
| **`PRODUCT-TRIAC-002`** (alias: `PRODUCT-GAP-001` FanTRIAC product-YAML slice) | **Investigated and deferred** — readiness gates are not satisfied. Decide whether to retain `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` as the canonical FanTRIAC shape or to add an alternative variant; perform the product YAML / catalog-entry rework (removes `GPIO5` / `GPIO6` placeholders); follows the [`product-onboarding.md`](product-onboarding.md) safe sequence. **Does not** add a WebFlash wrapper, build-matrix entry, release artifact, or WebFlash import. **Does not** add FanTRIAC to Release-One, REQUIRED_CONFIGS, kit / default lists, recommended surfaces, or compliance-certified surfaces; preserves all mains-voltage / qualified-electrician warnings. Until the gates clear, the only PRODUCT-TRIAC-002 work recorded in this repo is the docs-only deferral note in [`docs/cleanup-audit.md` PRODUCT-TRIAC-002 update](cleanup-audit.md#product-triac-002-update-deferred--package-triac-001-not-landed). | `PACKAGE-TRIAC-001` landed (i.e. `HW-005` unblock + `HW-PINMAP-320-FOLLOWUP` + bench timing / waveform / real-load evidence + `COMPLIANCE-001` advanced/manual-warning sign-off) + `PRODUCT-TRIAC-001` landed (wording-only catalog policy decided; **already landed**). |
| **`PRODUCT-POWER-400-001`** (alias: `PRODUCT-GAP-001` PWR-240V slice) | **Investigated 2026-05-19 — confirmed deferred (Path A docs-only); six preconditions still open** per [PWR-240V / S360-400](#pwr-240v--s360-400) §2026-05-19 — `PRODUCT-POWER-400-001` investigation pass and [`docs/cleanup-audit.md` §`PRODUCT-POWER-400-001 update`](cleanup-audit.md#product-power-400-001-update-2026-05-19--docs-only-investigation-pass). Add the first PWR-240V WebFlash-shippable canonical product YAML under [`products/`](../products/); decide the legacy-compatible `*-pwr` Core variant relationship (retain / migrate / coexist) for the four existing entries ([`sense360-core-c-pwr.yaml`](../products/sense360-core-c-pwr.yaml), [`sense360-core-w-pwr.yaml`](../products/sense360-core-w-pwr.yaml), [`sense360-core-v-c-pwr.yaml`](../products/sense360-core-v-c-pwr.yaml), [`sense360-core-v-w-pwr.yaml`](../products/sense360-core-v-w-pwr.yaml)); follow the [`product-onboarding.md`](product-onboarding.md) safe sequence; preserve the four `legacy-compatible` `*-pwr` Core variants byte-for-byte during the investigation phase. **Does not** add a WebFlash wrapper, catalog entry, build-matrix entry, or release artifact (those are additionally gated by `COMPLIANCE-001` `S360-400` slice closure). | `PACKAGE-POWER-400-001` implementation landed (only the docs-only investigation pass merged as PR #520; package YAML reconciliation, catalog `description` reconciliation, `S360-400` `schematic_status: verified` JSON PR, and BOM citation all still owed) + `COMPLIANCE-001` `S360-400` slice closed + product-onboarding approval per [`product-onboarding.md`](product-onboarding.md). |
| **`PRODUCT-POE-410-001`** (alias: `PRODUCT-GAP-001` PoE-410 slice) | **If warranted**, add a canonical product YAML that subjects the verified S360-410 PoE PSU explicitly (rather than the logical-only role Release-One consumes today). Often this slice will close by promoting Release-One's preserved schematic-pending caveat alone, without adding a new product entry. **Does not** add a WebFlash wrapper, catalog entry, build-matrix entry, or release artifact for any new entry. | `PACKAGE-POE-410-001` landed + `HW-002 OQ#6` closure / `S360-100-BENCH-001` update + Release-One caveat-closure PR scope decided. |
| **`WEBFLASH-GAP-001`** | Add WebFlash wrappers under [`products/webflash/`](../products/webflash/), catalog entries in [`config/product-catalog.json`](../config/product-catalog.json), and build-matrix entries in [`config/webflash-builds.json`](../config/webflash-builds.json) for selected new products that have already landed via a `PRODUCT-*-001` slice. Honours the [WebFlash exposure gates](#webflash-exposure-gates) above; advanced / manual-warning products require the manual-warning UX gate. | Each `PRODUCT-*-001` slice landed for the entries to be exposed; [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md) gates applied for any `stable` promotion. |
| **`RELEASE-GAP-001`** | Build, sign, and release firmware artifacts for the WebFlash entries added by `WEBFLASH-GAP-001`, using the existing [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml) flow. Verified by [`tests/test_webflash_artifact_naming.py`](../tests/test_webflash_artifact_naming.py) and [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py). | `WEBFLASH-GAP-001` landed for the entries to be released. |
| **`WF-IMPORT-GAP-001`** | Import the signed artifacts into the WebFlash repo's `manifest.json` / `firmware-N.json` per [`docs/webflash-release-handoff.md`](webflash-release-handoff.md). Owned by the WebFlash repo, not this repo. | `RELEASE-GAP-001` landed for the entries to be imported. |
| **`WF-TRIAC-001`** | WebFlash advanced-flow wrapper / catalog / build-matrix entry for FanTRIAC, behind an explicit manual-warning UX gate. Separate from the standard `WEBFLASH-GAP-001` flow because of the advanced / manual-warning posture. | `PRODUCT-TRIAC-002` landed + `COMPLIANCE-001` advanced / manual-warning sign-off + WebFlash-side manual-warning UX implemented. |

None of these PRs is approved or scoped by PRODUCT-GAP-001 itself.
They are recorded so the matrix has a clear next-action chain.

## BLOCKER-BURNDOWN-001 consolidation (2026-05-26)

The consolidated cross-lane blocker view now lives in
[`docs/blocker-burndown.md`](blocker-burndown.md) (BLOCKER-BURNDOWN-001).
For product-YAML readiness specifically it re-confirms — with no product
change — that the FanRelay (`PRODUCT-RELAY-001`), FanDAC
(`PRODUCT-DAC-001`), and FanPWM (`PRODUCT-PWM-001`) product YAMLs have
**landed** and full-compiled, so the remaining blockers are **bench /
operator / safety**, not product-layer:

- **FanPWM** — bench items open (PWM polarity; per-fan / aggregate
  current + MT3608 ceiling + inrush + thermal; product bench). RPM stays
  unsupported (no `pulse_counter`; per-fan RPM via an SX1509
  `pulse_counter` is compile-proven unsupported,
  `PWM-SX1509-TACH-PROOF-001`, captured `esphome config` rejection
  `[sx1509] is an invalid option for [pin]`). SX1509 PWM-drive output
  is supported and is the basis of FanPWM drive. → `S360-311-BENCH-EVIDENCE-REQUEST-001`.
- **FanDAC** — `J3` `out0`/`out1` silkscreen transposition confirmation,
  Cloudlift S12 harness trace, and Cloudlift S12 product bench open; the
  no-simultaneous-per-output-0–5 V/0–10 V constraint stays correct. →
  `S360-312-BENCH-EVIDENCE-REQUEST-001`.
- **FanRelay** — production-wide / multi-unit / oscilloscope-traced
  GPIO3 strap characterization + competent-person sign-off + mains
  compliance caveats remain owed. → `S360-310-SAFETY-EVIDENCE-REQUEST-001`.

No product YAML, catalog, `webflash_build_matrix`, `artifact_name`,
release, RPM, or readiness claim is made by the consolidation.

## BLOCKER-STATUS-FINALIZE-001 — clean repo / YAML / firmware path unblocked (2026-05-27)

`BLOCKER-STATUS-FINALIZE-001` finalizes the blocker-removal chain
(PR #599 → #600 → #601 → #602 → #603 → #604 → #605). It is **docs-only**
and flips no posture. For product-YAML readiness it re-confirms — with no
product change — that the FanPWM / FanDAC / FanRelay product YAMLs have
landed and full-compiled, so **clean, no-WebFlash repo / YAML / firmware
work is now unblocked** for all three lanes, while WebFlash / release /
import / hardware-stable / compliance lanes stay separately gated exactly
as the per-family `*-BLOCKER-RECLASSIFY-001` updates left them.

A clean repo / YAML / firmware PR may proceed only if it does **not**:
expose WebFlash, add a release artifact, flip `webflash_build_matrix`, add
`artifact_name`, claim hardware-stable, claim compliance / safety approval,
claim RPM / `TachIO` for PWM, claim Cloudlift-ready for DAC, or claim
production safety / install or kit / default readiness for Relay.

| Lane | Clean repo / YAML / firmware (no-WebFlash) | WebFlash / release / import | Hardware-stable / compliance | Remaining evidence (before WebFlash / release / hardware-stable) | Next clean PR |
|---|---|---|---|---|---|
| FanPWM / S360-311 | **UNBLOCKED** — package + product + compile-only complete; no-WebFlash cleanup may proceed (no WebFlash / release / `webflash_build_matrix` flip / `artifact_name` / hardware-stable / RPM / compliance claim) | **BLOCKED** — wrapper / build-matrix / artifact / import gated | **BLOCKED** — `cataloged_unverified`; compliance n/a (SELV) | Measured per-channel + aggregate current, MT3608 ceiling / inrush, measured thermal → `S360-311-CURRENT-THERMAL-001`; RPM / `TachIO` out of scope | `REPO-CLEANUP-NOWEBFLASH-001` |
| FanDAC / S360-312 | **UNBLOCKED** — same conditions; no Cloudlift-ready claim; `DAC-7` no-per-output-mix guardrail kept | **BLOCKED** — wrapper / build-matrix / artifact / import gated | **BLOCKED** — `cataloged_unverified`; compliance n/a (SELV) | `J3` `out0`/`out1` silkscreen confirm, Cloudlift S12 harness trace + product bench → `S360-312-BENCH-RESULT-001` | `REPO-CLEANUP-NOWEBFLASH-001` |
| FanRelay / S360-310 | **UNBLOCKED** — same conditions; no production safety / install or kit / default / recommended readiness claim | **BLOCKED** — wrapper / build-matrix / artifact / import gated | **BLOCKED** — `cataloged_unverified`; mains compliance gated (`RLY-6`, `CMP-1`) | Multi-unit scope-traced `GPIO3` strap characterization + competent-person sign-off → `S360-310-SAFETY-BENCH-RESULT-001` | `REPO-CLEANUP-NOWEBFLASH-001` |

`SECURITY-ACTION-PINNING-001` (`SEC-2`) is **CLOSED** (2026-05-27). The
recommended next clean implementation PR is **`REPO-CLEANUP-NOWEBFLASH-001`**
(clear stale docs / config references + no-WebFlash YAML / firmware cleanup
only). The cross-lane copy of this table is
[`blocker-burndown.md` §3A](blocker-burndown.md#3a-final-blocker-status--clean-repo--yaml--firmware-path-unblocked-blocker-status-finalize-001-2026-05-27).
This section adds **no** product YAML, catalog, `webflash_build_matrix`,
`artifact_name`, release, RPM, or readiness claim, and promotes no
`schematic_status`.

## FW-CONFIG-RUN-NOWEBFLASH-001 — recorded config-validation evidence for the no-WebFlash product YAML path (2026-05-27)

`FW-CONFIG-RUN-NOWEBFLASH-001` records the **actual** config-validation
status of the safe no-WebFlash product YAML path after
`SHIP-YAML-FIRMWARE-NOWEBFLASH-001` / PR #612 corrected the FanRelay
customer-usage remote-package `files:` example path. It is **docs-only**,
flips no posture, adds no product / catalog / `webflash_build_matrix` /
`artifact_name` / release / WebFlash change, and makes no WebFlash /
import / release / compliance / hardware-stable / kit-default readiness
claim. It records evidence only and fabricates none.

### What PR #612 actually changed (compile-relevant scope)

PR #612 edited exactly three files — the FanRelay product YAML
[`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml),
[`tests/test_relay_product_readiness.py`](../tests/test_relay_product_readiness.py),
and `UPCOMING_PR.md`. The product-YAML edit was a **single commented
line** (the customer-usage example `files:` path, corrected from the
non-existent transposed `...-ventiq-roomiq-fanrelay.yaml` to the real
`...-ventiq-fanrelay-roomiq.yaml`). Because it touches only a comment, it
**cannot change** the resolved `esphome config` / codegen output of the
FanRelay composition; the active `substitutions:` / `packages:` /
`text_sensor:` body is byte-identical to the previously-validated form.

### CI evidence on the PR #612 commit

The merged PR #612 head commit `1424f074d9940db7164c0a468f39c49f8c74658e`
(merged to `main` at merge commit `ed57523`, 2026-05-27) carries these
GitHub Actions check runs:

| Workflow run | Check / job | Conclusion | What it proves |
|---|---|---|---|
| `26504904676` (Quick Validation / `validate.yml`) | YAML Syntax Check | **success** | YAML structure across the product / package tree parses |
| `26504904607` (Compile-only Targets) | Compile-only Targets — Metadata Validation | **success** | `config/compile-only-targets.json` metadata (10 targets) is schema-valid |
| `26504904607` (Compile-only Targets) | Compile-only Targets — Full ESPHome Compile | **skipped** | — full ESPHome compile did **not** run on this PR |

The full-compile job is `workflow_dispatch` + `compile_mode=full` only
(resource-driven; intentional — see
[`repo-freshness-roadmap-audit.md` §6](repo-freshness-roadmap-audit.md#6-ci--validation-coverage-table)),
so it was **skipped** on the PR #612 push, as expected. No post-#612
manual `workflow_dispatch` full-compile run was found via the GitHub
tooling available this session.

### Local validation evidence (run 2026-05-27 on the merged tree)

ESPHome is **not** installed in this environment, so local
`esphome config` was **not** run; the commands below are the
ESPHome-independent validators. All green:

| Command | Result |
|---|---|
| `python3 tests/validate_configs.py` | ✅ 208 files checked, 0 failed (covers all three target product YAMLs) |
| `python3 scripts/validate_compile_targets.py --metadata-only` | ✅ 10 targets, metadata passed |
| `python3 tests/test_relay_product_readiness.py` | ✅ 61 tests OK (incl. the #612 `RelayProductCustomerUsageExampleTests` guard) |
| `python3 tests/test_pwm_product_readiness.py` | ✅ 62 tests OK |
| `python3 tests/test_dac_product_readiness.py` | ✅ 44 tests OK |
| `python3 tests/test_product_catalog.py` | ✅ 31 tests OK |
| `python3 tests/test_compile_targets.py` | ✅ 119 tests OK |
| `python3 tests/test_firmware_combination_matrix.py` | ✅ 24 tests OK |
| `python3 tests/test_firmware_build_gap_report.py` | ✅ 27 tests OK |
| `python3 tests/validate_webflash_builds.py` | ✅ 2 builds checked, 0 failed |
| `python3 tests/test_workflow_permissions.py` | ✅ 7 tests OK |
| `python3 -m unittest discover -s tests -p "test_*.py"` | ✅ 759 tests OK (3 skipped) |

`validate_configs.py` was confirmed to explicitly enumerate the three
target product YAMLs
(`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`,
`products/sense360-ceiling-poe-fanpwm.yaml`,
`products/sense360-ceiling-poe-fandac.yaml`).

### What this evidence proves

- The three target product YAMLs **parse and pass YAML-syntax +
  structural validation** (local `validate_configs.py` + CI YAML Syntax
  Check on the #612 commit).
- `config/compile-only-targets.json` **metadata is schema-valid** for all
  10 targets (local `--metadata-only` + CI Metadata Validation job).
- The full repo guard suite — including the #612 customer-usage-path
  regression guard — **passes** (759 tests, 3 skipped).

### What this evidence does NOT prove

- **NOT** a full `esphome config` / codegen / compile of the three
  **top-level** product YAMLs. `validate_configs.py` is YAML-syntax +
  structure only (it stubs `!include` rather than resolving the package
  graph), the CI Full ESPHome Compile job was **skipped** on #612, and
  ESPHome is unavailable locally.
- The recorded full-compile runs are **separate and pre-#612**, and they
  exercise the **compile-only skeletons**, not the top-level product
  YAMLs: run `26414398902` (`compile_mode=full`, 10 targets, success)
  covers `products/compile-only/ceiling-poe-fanpwm.yaml`, and run
  `26364679370` (`compile_mode=full`, 9 targets, success) covers
  `products/compile-only/ceiling-poe-fandac.yaml`. The top-level
  `sense360-ceiling-poe-fanpwm.yaml` / `sense360-ceiling-poe-fandac.yaml`
  compose additional base / API / OTA / time / health packages and
  product `text_sensor` identity on top of those skeletons, so a clean
  skeleton compile is **not** a top-level full-compile of these two
  products. The FanRelay top-level YAML is itself the registered
  compile-only target `ceiling-poe-ventiq-fanrelay-roomiq-compile-only`,
  but its `config/compile-only-targets.json` entry carries **no**
  `compile_validation_status` flag (unlike the FanDAC / FanPWM targets)
  and #612 did **not** run the full lane, so this file records no
  full-compile claim for it here.
- **NOT** WebFlash exposure, **NOT** a release artifact, **NOT** WebFlash
  import readiness, **NOT** hardware / bench / harness proof, **NOT**
  compliance / mains-safety approval, **NOT** RPM support for PWM, **NOT**
  Cloudlift-ready for DAC, and **NOT** production-safety / kit-default /
  recommended readiness for Relay. All per-family WebFlash / release /
  hardware-stable / compliance gates stay exactly as
  §BLOCKER-STATUS-FINALIZE-001 (2026-05-27) above left them.

### Next action to obtain top-level full-compile evidence

To record a real full `esphome config` / compile of the three
**top-level** product YAMLs, dispatch the full lane manually:
`.github/workflows/compile-only.yml` via `workflow_dispatch` with
`compile_mode=full` (runs `scripts/validate_compile_targets.py
--compile`). That directly compiles the FanRelay top-level target;
top-level FanPWM / FanDAC coverage additionally requires registering
their top-level YAMLs as compile-only targets (a separate scoped change,
**not** made here). Until that run is recorded, top-level full-compile
evidence for these products is **pending** and is **not** claimed.

> **Update (`FW-FULL-COMPILE-NOWEBFLASH-001`, 2026-05-27):** the full
> `esphome compile` lane has now been **run** and its result recorded in
> the section immediately below. The FanRelay top-level product YAML is
> itself the registered target `ceiling-poe-ventiq-fanrelay-roomiq-compile-only`,
> so its top-level full-compile gap is now **closed** (rc=0). The FanPWM /
> FanDAC registered targets are still the `products/compile-only/`
> **skeletons**, so the top-level `sense360-ceiling-poe-fanpwm.yaml` /
> `sense360-ceiling-poe-fandac.yaml` full-compile gap stays **pending**
> (registering those top-level YAMLs remains the separate scoped change
> above, **not** made here).

## FW-FULL-COMPILE-NOWEBFLASH-001 — recorded full ESPHome compile evidence for the compile-only lane (2026-05-27)

`FW-FULL-COMPILE-NOWEBFLASH-001` records the **actual** result of running
the full `esphome compile` lane —
[`scripts/validate_compile_targets.py --compile`](../scripts/validate_compile_targets.py),
the same command [`.github/workflows/compile-only.yml`](../.github/workflows/compile-only.yml)
runs in its `workflow_dispatch` + `compile_mode=full` job — against every
target in [`config/compile-only-targets.json`](../config/compile-only-targets.json).
It is **docs-only**, flips no posture, adds no product / catalog /
`webflash_build_matrix` / `artifact_name` / release / WebFlash change, and
makes no WebFlash / import / release / compliance / hardware-stable /
kit-default readiness claim. It records evidence only and fabricates none.

### How this run was produced (honest provenance)

This is a **local** full-compile run, **not** a GitHub Actions
`workflow_dispatch` run. The GitHub tooling available this session has
**no Actions dispatch / run API**, so the CI full lane could not be
triggered or observed from here and **no CI run ID exists for it** — one
is therefore **not** recorded and **not** fabricated. To produce real
evidence, the lane's own script was executed locally against the current
branch tree with the workflow's pinned ESPHome version:

| Field | Value |
|---|---|
| Command | `python3 scripts/validate_compile_targets.py --compile` (the full-lane command), plus a per-target `esphome compile <product_yaml>` capture |
| ESPHome version | `2026.4.5` (matches `compile-only.yml` `env.ESPHOME_VERSION`) |
| Toolchain | board `esp32-s3-devkitc-1`, framework `espidf` (ESP-IDF 5.5.4 via pioarduino `platform-espressif32` 55.03.38-1) |
| Trigger | local manual invocation (**not** GitHub Actions `workflow_dispatch`) |
| `compile_mode` equivalent | `full` (real `esphome compile`, not metadata-only) |
| CI workflow run ID | **none** — Actions dispatch/run API unavailable this session; not fabricated |
| Commit / branch | `449d8c442e92b0562c22af8cbfedc3c0f8f0a4d5` on `claude/full-compile-validation-record-byyBY` (= `origin/main` tip after PR #613) |
| Test secrets | provisioned exactly as the workflow's "Provision test secrets" step (gitignored; removed after the run) |
| Target count | **10** (all registered compile-only targets) |
| Conclusion | **success** — `✅ All 10 compile target(s) passed.`; every target `rc=0`, `Successfully compiled program` |
| Skipped targets | **none** |
| Failures | **none** |

### Per-target full-compile result

All 10 targets produced a real `firmware.bin`. Sizes are CI-only
confidence figures, **not** shippable artifacts (no `.bin` / checksum /
build-info / release proof is uploaded or committed):

| # | Target id | `product_yaml` | rc | RAM | Flash |
|---|---|---|---|---|---|
| 1 | `ceiling-poe-ventiq-roomiq-webflash` | `products/webflash/ceiling-poe-ventiq-roomiq.yaml` | 0 | 14.9% (48728 B) | 53.7% (985871 B) |
| 2 | `ceiling-poe-ventiq-roomiq-led-webflash` | `products/webflash/ceiling-poe-ventiq-roomiq-led.yaml` | 0 | 15.2% (49888 B) | 55.9% (1025139 B) |
| 3 | `ceiling-poe-compile-only` | `products/compile-only/ceiling-poe.yaml` | 0 | 12.8% (42048 B) | 50.5% (926763 B) |
| 4 | `ceiling-poe-roomiq-compile-only` | `products/compile-only/ceiling-poe-roomiq.yaml` | 0 | 13.8% (45376 B) | 52.1% (955535 B) |
| 5 | `ceiling-poe-ventiq-compile-only` | `products/compile-only/ceiling-poe-ventiq.yaml` | 0 | 13.8% (45352 B) | 52.5% (963071 B) |
| 6 | `ceiling-poe-airiq-compile-only` | `products/compile-only/ceiling-poe-airiq.yaml` | 0 | 14.5% (47400 B) | 57.8% (1060051 B) |
| 7 | `ceiling-poe-airiq-roomiq-compile-only` | `products/compile-only/ceiling-poe-airiq-roomiq.yaml` | 0 | 16.0% (52520 B) | 59.3% (1088227 B) |
| 8 | `ceiling-poe-ventiq-fanrelay-roomiq-compile-only` | `products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml` (**top-level FanRelay product YAML**) | 0 | 14.9% (48936 B) | 53.8% (987267 B) |
| 9 | `ceiling-poe-fandac-compile-only` | `products/compile-only/ceiling-poe-fandac.yaml` (**FanDAC skeleton**) | 0 | 12.9% (42256 B) | 50.6% (928139 B) |
| 10 | `ceiling-poe-fanpwm-compile-only` | `products/compile-only/ceiling-poe-fanpwm.yaml` (**FanPWM skeleton**) | 0 | 13.1% (43080 B) | 51.1% (938239 B) |

### FanRelay / FanPWM / FanDAC inclusion

All three fan compile-only targets **were included** and all compiled
clean (`rc=0`):

- **FanRelay** (#8): the registered target `product_yaml` **is** the
  top-level product YAML
  [`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml)
  — the exact file PR #612 corrected. Its top-level full-compile gap,
  recorded as **pending** by `FW-CONFIG-RUN-NOWEBFLASH-001` above, is now
  **closed**: the active config (unchanged by #612's comment-only edit)
  compiles end-to-end.
- **FanDAC** (#9) / **FanPWM** (#10): the registered targets are the
  `products/compile-only/` **skeletons**, **not** the top-level
  [`sense360-ceiling-poe-fandac.yaml`](../products/sense360-ceiling-poe-fandac.yaml)
  /
  [`sense360-ceiling-poe-fanpwm.yaml`](../products/sense360-ceiling-poe-fanpwm.yaml)
  product YAMLs, which compose additional base / API / OTA / time / health
  packages and product identity on top of the skeletons. A clean skeleton
  compile is **not** a top-level full-compile of those two products.

### Local (ESPHome-independent) validators re-run on the clean tree

After the compile, the `.esphome` build trees and provisioned
`secrets.yaml` copies were removed and the full validator suite re-run on
the clean tree — all green and unchanged from `FW-CONFIG-RUN-NOWEBFLASH-001`:

| Command | Result |
|---|---|
| `python3 tests/validate_configs.py` | ✅ 208 files checked, 0 failed |
| `python3 scripts/validate_compile_targets.py --metadata-only` | ✅ 10 targets, metadata passed |
| `python3 tests/test_relay_product_readiness.py` | ✅ 61 tests OK |
| `python3 tests/test_pwm_product_readiness.py` | ✅ 62 tests OK |
| `python3 tests/test_dac_product_readiness.py` | ✅ 44 tests OK |
| `python3 tests/test_product_catalog.py` | ✅ 31 tests OK |
| `python3 tests/test_compile_targets.py` | ✅ 119 tests OK |
| `python3 tests/test_firmware_combination_matrix.py` | ✅ 24 tests OK |
| `python3 tests/test_firmware_build_gap_report.py` | ✅ 27 tests OK |
| `python3 tests/validate_webflash_builds.py` | ✅ 2 builds checked, 0 failed |
| `python3 tests/test_workflow_permissions.py` | ✅ 7 tests OK |
| `python3 -m unittest discover -s tests -p "test_*.py"` | ✅ 759 tests OK (3 skipped) |

### What this evidence proves

- A real full `esphome compile` (ESP-IDF, `esp32-s3-devkitc-1`) of **all
  10 registered compile-only targets** **succeeds** under ESPHome
  `2026.4.5` — the YAML composes, substitutions resolve, `!include`s
  resolve, package/component configs match, codegen runs, and the
  firmware links to a `firmware.bin` for every target.
- The **FanRelay top-level product YAML** (the #612-fixed file) compiles
  clean, closing the top-level full-compile gap that was previously
  `pending` for FanRelay.
- The compile-only lane script and metadata stay schema-valid and the
  full guard suite (759 tests) passes on the clean tree.

### What this evidence does NOT prove

- It is **not** a GitHub Actions `workflow_dispatch` CI run and carries
  **no** CI run ID; the CI full lane in
  [`compile-only.yml`](../.github/workflows/compile-only.yml) remains the
  canonical CI path and can still be dispatched to produce a CI-side
  record.
- It is **not** a top-level full-compile of
  [`sense360-ceiling-poe-fanpwm.yaml`](../products/sense360-ceiling-poe-fanpwm.yaml)
  or
  [`sense360-ceiling-poe-fandac.yaml`](../products/sense360-ceiling-poe-fandac.yaml):
  only the `products/compile-only/` skeletons are registered targets.
  Registering those top-level YAMLs as compile-only targets is a separate
  scoped change, **not** made here.
- Compile success is **necessary but not sufficient** for readiness. It is
  **NOT** WebFlash exposure, **NOT** a release artifact, **NOT** WebFlash
  import readiness, **NOT** hardware / bench / harness proof, **NOT**
  compliance / mains-safety approval, **NOT** RPM support for PWM, **NOT**
  Cloudlift-ready for DAC, and **NOT** production-safety / kit-default /
  recommended readiness for Relay. No `firmware.bin`, checksum, build-info
  manifest, or release proof is uploaded or committed; no
  `webflash_build_matrix` flip, `artifact_name`, or release is added. All
  per-family WebFlash / release / hardware-stable / compliance gates stay
  exactly as §BLOCKER-STATUS-FINALIZE-001 (2026-05-27) above left them.

## Do-not-change guardrails

PRODUCT-GAP-001 — this matrix — performs **none** of the following.
Anyone reading this matrix looking for justification to change one
of them must use a separate, scoped PR with its own gate evidence.

- No edits to any product YAML under
  [`products/`](../products/) — neither to the existing
  production / preview / blocked entries
  ([`sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml),
  [`sense360-ceiling-poe-ventiq-roomiq-led.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq-led.yaml),
  [`sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml))
  nor to any of the 31 `legacy-compatible` entries
  (including
  [`sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml) and
  [`sense360-poe.yaml`](../products/sense360-poe.yaml)). **No new
  product YAML is added by this matrix.**
- No edits to any WebFlash wrapper under
  [`products/webflash/`](../products/webflash/) —
  [`ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml),
  [`ceiling-poe-ventiq-roomiq-led.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq-led.yaml),
  and the blocked
  [`ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml)
  all stay verbatim. **No new wrapper is added.**
- No edits to any package YAML under
  [`packages/`](../packages/). The six packages tracked by
  [`package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
  stay verbatim; the Core abstract packages stay verbatim; every
  feature / hardware / expansion package stays verbatim.
- No edits to
  [`config/hardware-catalog.json`](../config/hardware-catalog.json),
  [`config/product-catalog.json`](../config/product-catalog.json),
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  or
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json).
  No new product entry, no new `lifecycle_statuses` value, no new
  `canonical_modules` token, no new `release_one_required_configs`
  membership, no new build-matrix entry, no
  `webflash_build_matrix` flip, no new channel, no new artifact
  pattern.
- No edits to any workflow under `.github/workflows/`, any script
  under [`scripts/`](../scripts/), any test under
  [`tests/`](../tests/), any component under `components/`, or any
  include under `include/`.
- No firmware regenerated; no GitHub Release created or modified;
  no manifest signed; no WebFlash import; no kit added; no
  `REQUIRED_CONFIGS` / `scripts/data/kits.json` /
  `firmware/sources.json` / `manifest.json` entry added or
  removed — those are WebFlash-owned and are not touched by this
  repo.
- Release-One stays `Ceiling-POE-VentIQ-RoomIQ`, version `1.0.0`,
  channel `stable`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
  `v1.0.0`.
- LED preview entry `Ceiling-POE-VentIQ-RoomIQ-LED` stays
  `status: preview`, `channel: preview`, version `1.0.0`,
  artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`. No
  promotion to `production` / `stable`. No addition to
  `release_one_required_configs`. No kit added.
- FanTRIAC entry `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays
  `status: blocked`, `blocker: HW-005`,
  `webflash_build_matrix: false`. HW-005 is **not** resolved. The
  advanced / manual-warning long-term posture in
  [`docs/hardware/s360-320-r4-triac.md` Advanced / manual-warning product posture](hardware/s360-320-r4-triac.md#advanced--manual-warning-product-posture)
  is **intent only**; the JSON lifecycle row is unchanged.
- COMPLIANCE-001 mains-voltage UK / EU status for `S360-320`
  (FanTRIAC) and `S360-400` (240v PSU) is unchanged. PoE is SELV
  and is not in scope for COMPLIANCE-001.
- The Core J10 vs RoomIQ J6 pin-order discrepancy
  (`needs-silkscreen/bench-verification` per HW-009) is **not**
  resolved.
- The systemic Core abstract-bus mismatch in
  [`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml)
  (CORE-ABSTRACT-BUS-001, owned by
  [`release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups))
  is **not** resolved.
- The `S360-410` PoE PSU schematic-pending caveat in
  [`release-one-hardware-audit.md` Findings → PoE PSU](release-one-hardware-audit.md#findings)
  is **preserved**, not promoted away.
- No candidate product is marked `ready-for-product-yaml` by this
  PR. Every candidate family carries at least one of
  `needs-package-reconciliation`, `schematic-evidence-pending`,
  `hardware-evidence-pending`, `timing/compliance-pending`,
  `reference-only`, `blocked-from-standard-exposure`, or
  `do-not-change-release-one`.
- Every `legacy-compatible` entry stays `legacy-compatible` and
  remains out of the WebFlash build matrix.

## Validation

PRODUCT-GAP-001 is documentation only. The relevant invariants
are:

- the existing docs-safe validators continue to pass;
- the diff against code / yaml / json / workflow paths is empty;
- the sanity grep continues to find the expected
  PRODUCT-GAP-001 tokens.

### Test commands

The following are run in this PR; all expected to pass without
modification:

- `python3 tests/test_hardware_catalog.py`
- `python3 tests/test_product_catalog.py`
- `python3 tests/test_product_catalog_consistency.py`
- `python3 tests/validate_webflash_builds.py`
- `python3 tests/test_webflash_compatibility.py`
- `python3 tests/test_webflash_artifact_naming.py`
- `python3 tests/test_validate_webflash_release_notes.py`
- `python3 tests/test_generate_webflash_release_notes.py`
- `python3 tests/test_product_substitutions.py`
- `python3 tests/test_release_one_entity_names.py`
- `python3 tests/validate_configs.py`
- `python3 tests/test_led_package_mapping.py`

No new test is added by this PR. A future per-family slice
(`PRODUCT-RELAY-001` / `PRODUCT-PWM-001` / `PRODUCT-DAC-001` /
`PRODUCT-TRIAC-001` / `PRODUCT-POWER-400-001` /
`PRODUCT-POE-410-001`) may add a structural file-content guard
analogous to
[`tests/test_release_one_entity_names.py`](../tests/test_release_one_entity_names.py)
once it adds the corresponding product YAML.

### Diff expectations

`git diff products products/webflash packages config scripts
.github/workflows components include firmware tests` is expected
to be **empty** in this PR — no edits to any of those trees.

### Sanity-grep expectations

`grep -RIn "PRODUCT-GAP-001|ready-for-product-yaml|needs-package-reconciliation|advanced/manual-warning|not-required-configs|not-recommended|FanRelay|FanPWM|FanDAC|FanTRIAC|S360-310|S360-311|S360-312|S360-320|S360-400|S360-410" docs config products packages tests`
is expected to return matches from:

- this new doc
  [`docs/product-readiness-matrix.md`](product-readiness-matrix.md);
- the per-board audit docs
  [`hardware/s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md),
  [`hardware/s360-311-r4-pwm.md`](hardware/s360-311-r4-pwm.md),
  [`hardware/s360-312-r4-dac.md`](hardware/s360-312-r4-dac.md),
  [`hardware/s360-320-r4-triac.md`](hardware/s360-320-r4-triac.md),
  [`hardware/s360-400-r4-power.md`](hardware/s360-400-r4-power.md),
  [`hardware/s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md);
- the cross-cutting docs
  [`hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md),
  [`hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md),
  [`hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md),
  [`product-availability-taxonomy.md`](product-availability-taxonomy.md),
  [`product-onboarding.md`](product-onboarding.md),
  [`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md),
  [`product-deprecation-removal-policy.md`](product-deprecation-removal-policy.md),
  [`release-one-hardware-audit.md`](release-one-hardware-audit.md),
  [`cleanup-audit.md`](cleanup-audit.md);
- the product YAML files themselves (config strings and module
  identity strings); and
- the JSON catalogs in `config/`.

No match outside of those trees is expected.

## See also

- [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md)
  — WEBFLASH-GAP-001 WebFlash-layer exposure readiness gate.
  Downstream from this matrix: classifies per-family WebFlash
  exposure (wrapper / catalog / build-matrix / release / import) for
  the same FanRelay / FanPWM / FanDAC / FanTRIAC / PWR-240V /
  PoE-410 candidate families, and names the per-family follow-up
  PRs (`WEBFLASH-RELAY-001`, `WEBFLASH-PWM-001`, `WEBFLASH-DAC-001`,
  `WF-TRIAC-001`, `WEBFLASH-POWER-400-001`, `WEBFLASH-POE-410-001`).
  Documentation only.
- [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
  — RELEASE-GAP-001 release-layer readiness gate. Two layers
  downstream from this matrix: classifies per-family release
  artifact eligibility (build / sign / attach / checksums /
  release-notes / release-proof / operator-proof / import) for
  the same FanRelay / FanPWM / FanDAC / FanTRIAC / PWR-240V /
  PoE-410 candidate families, and names the per-family follow-up
  release slices (`RELEASE-RELAY-001`, `RELEASE-PWM-001`,
  `RELEASE-DAC-001`, `RELEASE-TRIAC-001`,
  `RELEASE-POWER-400-001`, `RELEASE-POE-410-001`). Records the
  policy-only `not-release-ready` / `missing-build-matrix` /
  `preview-artifact-candidate` /
  `advanced/manual-warning-artifact-only` / `stable-not-approved`
  / `operator-proof-required` / `release-proof-required` label
  vocabulary; preserves Release-One, the LED preview, and the
  FanTRIAC blocked reference; treats `RELEASE-007` LED stable as
  reference-only and out-of-scope (owned by
  `docs/preview-to-stable-promotion-gates.md`). Documentation
  only.
- [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
  — PACKAGE-GAP-001 package-level readiness gate. Source of truth
  for the "Package readiness" column on every candidate row in
  this matrix. Documentation only.
- [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
  — HW-GAP-001 board-level readiness matrix. Records PRODUCT-GAP-001
  as Follow-up PR sequence row #8 with the
  `PRODUCT-GAP-001` → `WEBFLASH-GAP-001` → `RELEASE-GAP-001` →
  `WF-IMPORT-GAP-001` successor chain.
- [`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
  — HW-009 / HW-010 firmware-package-vs-schematic audit. Source of
  truth for the `confirmed-ok` / `needs-package-change` /
  `needs-doc-fix` / `needs-silkscreen/bench-verification` /
  `blocked` / `unknown` vocabulary the package matrix consumes;
  this matrix consumes the package matrix's verdict in turn.
- [`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md)
  — PRODUCT-AVAIL-001 cross-cutting product availability taxonomy.
  Maps this matrix's `ready-for-product-yaml` /
  `needs-package-reconciliation` / `schematic-evidence-pending` /
  `hardware-evidence-pending` / `timing/compliance-pending` /
  `advanced/manual-warning-only` / `blocked-from-standard-exposure`
  / `not-webflash-default` / `legacy-only` / `invalid-combination`
  labels onto the cross-cutting `product-yaml-ready` /
  `build-matrix-ready` / `release-artifact-ready` /
  `webflash-imported` / `webflash-live-preview` /
  `webflash-live-stable` ladder rungs without changing JSON enums.
- [`docs/product-onboarding.md`](product-onboarding.md) —
  PRODUCT-004 ordered safe sequence for adding any new product /
  config. Every future PRODUCT-*-001 slice must clear the
  onboarding gates before adding a product YAML.
- [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
  — RELEASE-006 canonical 17-row preview-to-stable promotion gate.
  Applies to any future product YAML that would target a `stable`
  channel; not bypassed by PRODUCT-GAP-001. Also defines the
  `REQUIRED_CONFIGS policy` and the `Kit policy` referenced here.
- [`docs/product-deprecation-removal-policy.md`](product-deprecation-removal-policy.md)
  — PRODUCT-DEP-001 deprecation / removal policy. Owns any future
  retirement of `legacy-compatible` entries (e.g. the legacy
  four-channel [`sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml));
  PRODUCT-GAP-001 does not deprecate or remove any entry.
- [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)
  — Release-One firmware-vs-schematic audit; source of truth for
  the HW-005 FanTRIAC blocker
  ([§FanTRIAC mapping resolution](release-one-hardware-audit.md#fantriac-mapping-resolution)),
  the systemic Core abstract-bus rebind (Required follow-ups
  #2 / #3 = CORE-ABSTRACT-BUS-001), and the `S360-410` PoE PSU
  schematic-pending caveat (Findings → PoE PSU).
- [`docs/webflash-contract.md`](webflash-contract.md) — canonical
  WebFlash artifact / grammar / token contract; §6 retains legacy
  package filenames; the fan-driver `max-one-of` rule and the
  `FanDAC` ↔ `AirIQ` mutex bound this matrix's product policy.
- [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
  — COMPLIANCE-001 mains-voltage UK / EU compliance tracker;
  additional gate for any product / WebFlash work consuming
  `S360-320` (FanTRIAC) or `S360-400` (240v PSU). PoE is SELV and
  is not in scope.
- [`docs/cleanup-audit.md`](cleanup-audit.md) — classification of
  stale / current / blocked-reference / legacy-compatible repo
  content; carries the PRODUCT-GAP-001 registration row.
- [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  — machine-readable hardware catalog. `schematic_status` stays
  `cataloged_unverified` for `S360-310`, `S360-311`, `S360-312`,
  `S360-320`, `S360-400`, `S360-410`. PRODUCT-GAP-001 changes
  none of these values.
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
  — WebFlash compatibility taxonomy; source of truth for the
  `canonical_modules` / `canonical_mounting` / `canonical_power` /
  `forbidden_tokens` / mutex rules / `release_one_required_configs`
  values this matrix consumes.

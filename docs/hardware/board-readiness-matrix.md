# S360 Board Readiness Matrix (HW-GAP-001)

## Purpose and scope

This document is the canonical, **board-level** readiness matrix for
every SKU in
[`config/hardware-catalog.json`](../../config/hardware-catalog.json).
It records, for each S360 board / module, the current state of every
evidence dimension that gates productization: hardware catalog status,
schematic PDF, per-board artifact index, pin-map / standalone
reference doc, package YAML, product YAML, WebFlash wrapper, WebFlash
build matrix, release artifact, WebFlash import / manifest, and
bench / operator proof.

It exists because the repository carries the same information today
in several axis-specific docs —
[`docs/product-availability-taxonomy.md`](../product-availability-taxonomy.md)
(PRODUCT-AVAIL-001) for the cross-cutting availability ladder,
[`docs/hardware/remaining-board-documentation-audit.md`](remaining-board-documentation-audit.md)
(HW-004 / HW-006 / HW-008) for the pin-map / documentation axis,
[`docs/hardware/firmware-package-mapping-audit.md`](firmware-package-mapping-audit.md)
(HW-009 / HW-010) for the package-vs-schematic axis,
[`docs/hardware/hardware-artifact-policy.md`](hardware-artifact-policy.md)
(HW-ASSETS-001) for the per-board artifact-index axis,
[`docs/release-one-hardware-audit.md`](../release-one-hardware-audit.md)
for the Release-One firmware-vs-schematic axis,
[`docs/preview-to-stable-promotion-gates.md`](../preview-to-stable-promotion-gates.md)
(RELEASE-006) for the preview-to-stable gate axis, and the JSON
catalogs themselves — but no single doc threads them per board into
one place. HW-GAP-001 is that place.

This document is **documentation only**. It does not:

- add, remove, or modify any entry in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json),
  [`config/product-catalog.json`](../../config/product-catalog.json),
  [`config/webflash-builds.json`](../../config/webflash-builds.json),
  or [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json),
- add any new JSON field, lifecycle status, schematic status, or
  channel value to any of those catalogs,
- add, remove, or modify any product YAML under
  [`products/`](../../products/) or any WebFlash wrapper under
  [`products/webflash/`](../../products/webflash/),
- add, remove, or modify any package YAML under
  [`packages/`](../../packages/),
- modify any workflow under `.github/workflows/`, any script under
  [`scripts/`](../../scripts/), any test under
  [`tests/`](../../tests/), any component under `components/`, or any
  include under `include/`,
- generate, regenerate, sign, import, deploy, or otherwise produce
  firmware,
- change the Release-One configuration `Ceiling-POE-VentIQ-RoomIQ`
  (`status: production`, `channel: stable`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag `v1.0.0`),
- change the LED preview entry `Ceiling-POE-VentIQ-RoomIQ-LED`
  (stays `status: preview`, `channel: preview`),
- unblock FanTRIAC (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays
  `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`),
- change the mains-voltage compliance status of `S360-320` or
  `S360-400` (owned by COMPLIANCE-001;
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md)),
- resolve the Core J10 vs RoomIQ J6 pin-order discrepancy,
- resolve the systemic Core abstract-bus mismatch flagged in
  [`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3](../release-one-hardware-audit.md#required-follow-ups),
- add, remove, or modify any WebFlash-side `REQUIRED_CONFIGS`,
  `scripts/data/kits.json`, `firmware/sources.json`, or `manifest.json`
  entry (those are WebFlash-owned).

If this matrix and any source-of-truth document drift, **the
source-of-truth document wins** and this matrix must be updated. The
sources of truth are listed in [See also](#see-also).

## Core rule

> **Board readiness is not the same as product readiness or WebFlash
> readiness.**

> A board may be schematic-verified and still lack a curated artifact
> index, a pin-map reconciliation, a package YAML reconciled against
> its module-side schematic, a product YAML that consumes it, a
> build-matrix entry, a release artifact, a WebFlash import, or
> bench / operator proof. Each of those is a separate gate, owned by a
> separate downstream PR, and must be cleared independently.

This is the same load-bearing premise as
[`docs/product-availability-taxonomy.md` Core rule](../product-availability-taxonomy.md#core-rule):
hardware evidence does not equal firmware support, product support, or
WebFlash availability. HW-GAP-001 records that rule in its per-board
form. Any PR that argues "the schematic is verified, therefore this
board is ready to ship" without clearing the downstream gates
documented here is breaking the rule and must be rejected on first
read.

## Readiness columns

The matrix below uses the column set proposed in the HW-GAP-001 brief.
Each column maps to vocabulary already established in this
repository — HW-GAP-001 introduces **no** new JSON enums, schemas, or
status values. The column-to-source map is:

| Column | Vocabulary source |
|---|---|
| Board (SKU) | [`config/hardware-catalog.json`](../../config/hardware-catalog.json) `sku` |
| Friendly name / role | [`config/hardware-catalog.json`](../../config/hardware-catalog.json) `friendly_name` + `description` |
| Hardware catalog status | [`config/hardware-catalog.json`](../../config/hardware-catalog.json) `schematic_status` — `verified` or `cataloged_unverified` |
| Schematic PDF | committed under [`docs/hardware/schematics/`](schematics/) — `done` or `missing` |
| Artifact index | per-board doc under [`docs/hardware/artifacts/`](artifacts/) per HW-ASSETS-001 — `done` or `missing` |
| Pin-map status | HW-004 / HW-006 / HW-008 audit labels — `documented` / `partially-documented` / `cataloged-unverified` / `blocked` / `not-needed-for-release-one` |
| Package YAML status | HW-009 / HW-010 audit labels — `confirmed-ok` (with caveat) / `needs-package-change` / `needs-silkscreen/bench-verification` / `package-yaml-pending` / `blocked` |
| Product YAML usage | active product YAMLs that consume the board, or `legacy-only`, or `none` |
| WebFlash wrapper | wrapper under [`products/webflash/`](../../products/webflash/) — `done`, `none`, or `blocked` |
| Build matrix | [`config/webflash-builds.json`](../../config/webflash-builds.json) channel — `done` (stable / preview / etc.), `none`, or `blocked` |
| Release artifact | GitHub Release `.bin` matching `artifact_name` per [`docs/webflash-release-proof.md`](../webflash-release-proof.md) — `done`, `none`, or `blocked` |
| WebFlash manifest / import | WebFlash-side sidecar + signed firmware + deployed manifest — `webflash-imported`, `none`, or `blocked` |
| Bench / operator proof | RELEASE-006 row state per [`docs/preview-to-stable-promotion-gates.md`](../preview-to-stable-promotion-gates.md) — `done`, `partial`, `pending`, `not applicable` |
| Blockers / open questions | named blocker IDs (HW-005, COMPLIANCE-001, HW-002 OQ#…) plus pointers to per-board open-questions lists |
| Current classification | PRODUCT-AVAIL-001 snapshot vocabulary plus the policy-only labels below |

### Status value vocabulary (policy-only)

The columns above use a small set of cell values. **All are
policy-only labels** — they are not JSON enums, not promoted to any
schema, and not added to any validator by this PR. PRODUCT-AVAIL-002
may promote some of them to machine-readable fields; HW-GAP-001 does
not.

| Cell value | Meaning |
|---|---|
| `done` | Evidence for this dimension is committed in this repo (or, for WebFlash-side dimensions, recorded in WebFlash repo per [`docs/webflash-release-handoff.md`](../webflash-release-handoff.md)). |
| `partial` | Some evidence is committed; the audit row that covers this board flags a retained caveat or **verify** flag against the physical board. |
| `missing` | No evidence committed; not blocked, just not yet produced. |
| `not applicable` | The dimension does not apply to this board (e.g. off-board PSU has no on-board J-header pin map). |
| `blocked` | A named blocker (HW-005, COMPLIANCE-001) intentionally holds this dimension. |
| `compliance-gated` | An additional compliance gate (COMPLIANCE-001 mains-voltage UK / EU) must clear before this dimension can advance. |
| `preview-only` | This dimension is filled on a non-`stable` WebFlash channel; stable promotion is gated by additional RELEASE-006 rows. |
| `legacy-only` | This board is consumed only by `legacy-compatible` product YAMLs; those are intentionally not WebFlash-shippable. |
| `unknown` | Cannot be classified from currently committed evidence. Not used in this matrix today; every board cell was placeable under one of the labels above. |

## Summary matrix

The matrix is split into two tables for readability. Both cover the
same 11 SKUs in catalog order. The detailed per-board notes in
[Board-by-board notes](#board-by-board-notes) below cite the supporting
evidence (file paths and line numbers) for every cell.

### Hardware-evidence axis

| Board | Friendly name / role | Hardware catalog | Schematic PDF | Artifact index | Pin-map status | Package YAML status |
|---|---|---|---|---|---|---|
| `S360-100` | Sense360 Core (ESP32-S3 hub) | `verified` | `done` | `done` (HW-ASSETS-002) | `documented` (with open-questions list) | `confirmed-ok` against connector-level; systemic abstract-bus rebind owed by [`release-one-hardware-audit.md` Required follow-ups #2 / #3](../release-one-hardware-audit.md#required-follow-ups) |
| `S360-200` | Sense360 RoomIQ (room sensor) | `verified` | `done` | `missing` (HW-ASSETS-003 deferred) | `documented` | `confirmed-ok` (abstract `expansion_i2c` / `uart_bus`) |
| `S360-210` | Sense360 AirIQ (air-quality, ceiling) | `verified` | `done` | `missing` (HW-ASSETS-004 deferred) | `documented`, `not-needed-for-release-one` | `confirmed-ok` (legacy-naming caveat) |
| `S360-211` | Sense360 VentIQ (bathroom air-quality) | `verified` | `done` | `missing` (HW-ASSETS-005 deferred) | `documented` | `confirmed-ok` (legacy filename `airiq_bathroom_base.yaml` retained per [`webflash-contract.md`](../webflash-contract.md) §6) |
| `S360-300` | Sense360 LED (WS2812B ring) | `verified` | `done` | `missing` (HW-ASSETS-006 deferred) | `documented`, `not-needed-for-release-one` | `confirmed-ok` for `led_ring_ceiling.yaml` (HW-010); `led_ring_wall.yaml` and `sense360_core_ceiling_s3.yaml` remain unresolved |
| `S360-310` | Sense360 Relay (on/off relay for fans) | `cataloged_unverified` | `missing` | `missing` | `partially-documented`, `not-needed-for-release-one` (Core J4 captured) | `package-yaml-pending` ([`fan_relay.yaml`](../../packages/expansions/fan_relay.yaml) exists; not reconciled against module-side schematic) |
| `S360-311` | Sense360 PWM (12V PWM fan driver) | `cataloged_unverified` | `done` (HW-ASSETS-003; JSON `schematic_status` still `cataloged_unverified`, `schematic_file` not yet set) | `done` (HW-ASSETS-003); HW-PINMAP-311 audit doc landed at [`s360-311-r4-pwm.md`](s360-311-r4-pwm.md) with **status: `partial — schematic evidence available; package reconciliation pending`** | `partially-documented`, `not-needed-for-release-one` (Core J6 captured; pin-order **verify**; new module-side `J3` pin-11 / pin-12 `UART_RX` / `UART_TX` reconciliation recorded in [`s360-311-r4-pwm.md`](s360-311-r4-pwm.md) and owed to HW-PINMAP-311-FOLLOWUP) | `package-yaml-pending` ([`fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml) exists; `needs-package-reconciliation` per [`s360-311-r4-pwm.md`](s360-311-r4-pwm.md); not reconciled against module-side schematic) |
| `S360-312` | Sense360 DAC (0–10 V analog fan driver) | `cataloged_unverified` | `done` (HW-ASSETS-003; JSON `schematic_status` still `cataloged_unverified`, `schematic_file` not yet set) | `done` (HW-ASSETS-003); HW-PINMAP-312 audit doc landed at [`s360-312-r4-dac.md`](s360-312-r4-dac.md) with **status: `partial — schematic evidence available; package reconciliation pending`** | `partially-documented`, `not-needed-for-release-one` (Core J7 fully captured; new module-side `J1` pin-1 `+3.3V` vs Core J7 pin-1 `+5V` rail discrepancy recorded in [`s360-312-r4-dac.md`](s360-312-r4-dac.md) and owed to HW-PINMAP-312-FOLLOWUP) | `package-yaml-pending` ([`fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) exists; `needs-package-reconciliation` per [`s360-312-r4-dac.md`](s360-312-r4-dac.md); not reconciled against module-side schematic) |
| `S360-320` | Sense360 TRIAC (phase-cut mains dimmer) | `cataloged_unverified` | `done` (HW-ASSETS-003; **does not unblock HW-005 or clear COMPLIANCE-001**; JSON `schematic_status` still `cataloged_unverified`, `schematic_file` not yet set) | `done` (HW-ASSETS-003; **does not unblock HW-005 or clear COMPLIANCE-001**) | `blocked` (HW-005), `compliance-gated` (COMPLIANCE-001) | `blocked` ([`fan_triac.yaml`](../../packages/expansions/fan_triac.yaml) retained as blocked / reference; `GPIO5` / `GPIO6` placeholders collide with RoomIQ J10 nets) |
| `S360-312` | Sense360 DAC (0–10 V analog fan driver) | `cataloged_unverified` | `done` (HW-ASSETS-003; JSON `schematic_status` still `cataloged_unverified`, `schematic_file` not yet set) | `done` (HW-ASSETS-003) | `partially-documented`, `not-needed-for-release-one` (Core J7 fully captured; new module-side `J1` pin-1 `+3.3V` vs Core J7 pin-1 `+5V` rail discrepancy owed to `HW-PINMAP-312`) | `package-yaml-pending` ([`fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) exists; not reconciled against module-side schematic) |
| `S360-320` | Sense360 TRIAC (phase-cut mains dimmer) | `cataloged_unverified` | `done` (HW-ASSETS-003; **does not unblock HW-005 or clear COMPLIANCE-001**; JSON `schematic_status` still `cataloged_unverified`, `schematic_file` not yet set) | `done` (HW-ASSETS-003); HW-PINMAP-320 audit doc landed at [`s360-320-r4-triac.md`](s360-320-r4-triac.md) with **status: `partial — schematic evidence available; package reconciliation, timing validation, and compliance/certification pending`** (**does not unblock HW-005 or clear COMPLIANCE-001**) | `blocked` (HW-005), `compliance-gated` (COMPLIANCE-001) (advanced / manual-warning long-term posture intended per [`s360-320-r4-triac.md`](s360-320-r4-triac.md#advanced--manual-warning-product-posture); **not realised in this PR** — JSON lifecycle row unchanged) | `blocked` / `needs-package-reconciliation` ([`fan_triac.yaml`](../../packages/expansions/fan_triac.yaml) retained as blocked / reference with BLOCKED / UNVERIFIED banner; `GPIO5` / `GPIO6` placeholders collide with RoomIQ J10 nets; see [`s360-320-r4-triac.md` Package YAML status](s360-320-r4-triac.md#package-yaml-status)) |
| `S360-400` | Sense360 240v PSU (HLK-5M05 mains PSU) | `cataloged_unverified` | `missing`, `compliance-gated` | `missing` | `not applicable` (off-board) / `cataloged-unverified`, `compliance-gated`; HW-PINMAP-400 audit doc landed at [`s360-400-r4-power.md`](s360-400-r4-power.md) with **status: `pending — schematic/design evidence required`** | `package-yaml-pending` ([`power_240v.yaml`](../../packages/hardware/power_240v.yaml) is a logical-power package; no GPIO binding) |
| `S360-410` | Sense360 PoE PSU (802.3af PoE → 5 V) | `cataloged_unverified` | `missing` (Release-One caveat preserved) | `missing` | `partially-documented` (Core J2 captured; module-side schematic pending; HW-002 OQ#6 open); HW-PINMAP-410 audit doc landed at [`s360-410-r4-poe.md`](s360-410-r4-poe.md) with **status: `pending — schematic/design evidence required`** | `confirmed-ok` (logical-only [`power_poe.yaml`](../../packages/hardware/power_poe.yaml) emits diagnostic sensors; no GPIO binding) |

### Productization / WebFlash axis

| Board | Product YAML usage | WebFlash wrapper | Build matrix | Release artifact | WebFlash manifest / import | Bench / operator proof | Current classification | Blockers / open questions |
|---|---|---|---|---|---|---|---|---|
| `S360-100` | Release-One (`production`) + LED preview (`preview`) + 30+ `legacy-compatible` Core variants | `done` (`ceiling-poe-ventiq-roomiq.yaml`, `ceiling-poe-ventiq-roomiq-led.yaml`) plus blocked `ceiling-poe-ventiq-fantriac-roomiq.yaml` | `done` (`stable` + `preview`) | `done` (Release-One stable bin; LED preview bin) | `webflash-imported` (Release-One); `webflash-imported` for LED preview (WF-LED-001 / WF-LED-002 / WF-LED-003 / WF-DEPLOY-001 per [`webflash-release-proof.md`](../webflash-release-proof.md)) | `done` for Release-One firmware (REL-001); `partial` for LED preview firmware (operator flash proof outstanding); Core board bench / manufacturing review tracked as [**S360-100-BENCH-001**](s360-100-r4-core.md#s360-100-bench-001-status) `pending — bench/manufacturing evidence required` | `hardware-evidenced / productized / WebFlash-used` | J6 vs J10 pin-order (silkscreen verify); `IO10` net label; `IO39`–`IO42` ↔ TPx mapping; J2 PoE harness identity; `AirQ_Led` / `AirQ_Status_Led` reuse (HW-002 OQ#4); BOM / CPL / Gerber / STEP manufacturing-artifact review — all tracked under [S360-100-BENCH-001](s360-100-r4-core.md#s360-100-bench-001-status); systemic Core abstract-bus rebind (owned by [`release-one-hardware-audit.md` Required follow-ups #2 / #3](../release-one-hardware-audit.md#required-follow-ups)) |
| `S360-200` | Release-One (`production`) + LED preview (`preview`) + legacy-compatible | `done` (same wrappers as Core) | `done` (`stable` + `preview`) | `done` (same artifacts as Core) | `webflash-imported` (Release-One); `webflash-imported` for LED preview | `done` for Release-One; `partial` for LED preview | `hardware-evidenced / productized / WebFlash-used` | Core J10 vs RoomIQ J6 pin-order discrepancy (`needs-silkscreen/bench-verification`); `AirQ_Led` reuse |
| `S360-210` | `none` active; legacy-compatible AirIQ Core / Mini paths only | `none` | `none` | `none` | `none` (`firmware-missing` for any AirIQ-bearing config) | `not applicable` | `hardware-evidenced / firmware-missing` (mutex with VentIQ enforced by [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json) `rules.airiq_and_ventiq_mutually_exclusive: true`) | No active product YAML consumes AirIQ; `AirQ_Led` / `AirQ_Status_Led` reuse (HW-002 OQ#4); any AirIQ-bearing config requires its own catalog entry + build-matrix entry + onboarding-gate clearance |
| `S360-211` | Release-One (`production`) + LED preview (`preview`) + 6 legacy-compatible bathroom variants | `done` (same wrappers as Core) | `done` (`stable` + `preview`) | `done` (same artifacts as Core) | `webflash-imported` (Release-One); `webflash-imported` for LED preview | `done` for Release-One; `partial` for LED preview | `hardware-evidenced / productized / WebFlash-used` | `AirQ_Led` / `AirQ_Status_Led` reuse (HW-002 OQ#4); on-board fan-relay drive-signal source (future fan-driver audit); on-board relay mains-side compliance tracked under COMPLIANCE-001 |
| `S360-300` | LED preview (`preview`) only; legacy-compatible Core ceiling variants include the package | `done` (`ceiling-poe-ventiq-roomiq-led.yaml`); Release-One wrapper deliberately omits LED | `done` (`preview` only) | `done` (LED preview bin recorded in [`webflash-release-proof.md`](../webflash-release-proof.md) RELEASE-005) | `webflash-imported` (per WF-LED-001 / WF-LED-002 / WF-LED-003 / WF-DEPLOY-001) on `preview` | `pending` for stable promotion — RELEASE-006 rows 9–17 (operator flash proof WF-HW-TEST-001, hardware bench verification tracked as [**S360-300-BENCH-001**](s360-300-r4-led.md#s360-300-bench-001-status) `pending — bench hardware evidence required`, stable release notes, production catalog promotion, stable build artifact, stable WebFlash import, separate REQUIRED_CONFIGS / kit decisions, human approval) | `preview-only` — stays `preview` / `preview` | Bench-verification open questions in [`s360-300-r4-led.md` Open questions](s360-300-r4-led.md#open-questions--verification-needed) (harness rail, LED count, harness identity, observed behaviour) tracked under [S360-300-BENCH-001](s360-300-r4-led.md#s360-300-bench-001-status); RELEASE-006 stable gates rows 9–17; `led_ring_wall.yaml` (`GPIO48`) and legacy `sense360_core_ceiling_s3.yaml` (`GPIO14`) remain unresolved at the package level (neither has Core-side schematic backing) |
| `S360-310` | `none` active (the legacy `sense360-fan-pwm.yaml` is `legacy-compatible` and is for PWM, not relay) | `none` | `none` (`FanRelay` token reserved in [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json); no build consumes it) | `none` | `none` (`design-pending` for any `FanRelay`-bearing config) | `not applicable` | `missing-productization-evidence / no-WebFlash-build` (`design-pending` per PRODUCT-AVAIL-001) | Module-side schematic not committed; standalone reference doc not committed; package YAML exists but not reconciled against module-side schematic; subject to fan-driver `max-one-of` rule per [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json) |
| `S360-311` | `none` active; legacy `sense360-fan-pwm.yaml` is `legacy-compatible` | `none` | `none` | `none` | `none` (`design-pending`) | `not applicable` | `missing-productization-evidence / no-WebFlash-build` (`design-pending`) | Module-side schematic not committed; standalone reference doc not committed; Core J6 1-to-13 pin-order **verify** must resolve against silkscreen; package YAML not reconciled against module-side schematic; subject to fan-driver `max-one-of` rule |
| `S360-312` | `none` active | `none` | `none` | `none` | `none` (`design-pending`) | `not applicable` | `missing-productization-evidence / no-WebFlash-build` (`design-pending`) | HW-PINMAP-312 audit doc landed at [`s360-312-r4-dac.md`](s360-312-r4-dac.md) with **status: `partial — schematic evidence available; package reconciliation pending`**; records the Core J7 pin-1 `+5V` vs Module J1 pin-1 `+3.3V` voltage-rail discrepancy, the DIP-switch I²C address-selection scheme on `IC1` / `IC2`, the UART0-vs-Nextion routing question, and the stale header-comment connector / GPIO claims in [`fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) as unresolved; package YAML not reconciled against module-side schematic; subject to fan-driver `max-one-of` rule **and** the explicit FanDAC ↔ AirIQ conflict per [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json). Follow-ups: `HW-PINMAP-312-FOLLOWUP`, `PACKAGE-GAP-001` FanDAC slice — per [`s360-312-r4-dac.md` Follow-up PRs](s360-312-r4-dac.md#follow-up-pr-sequence). |
| `S360-320` | Blocked reference only (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`, `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`) | `blocked` ([`ceiling-poe-ventiq-fantriac-roomiq.yaml`](../../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml) retained as reference only) | `blocked` (not in [`config/webflash-builds.json`](../../config/webflash-builds.json)) | `blocked` | `blocked` | `not applicable` | `blocked` — **stays blocked** | **HW-005** ([`release-one-hardware-audit.md#fantriac-mapping-resolution`](../release-one-hardware-audit.md#fantriac-mapping-resolution)) + **COMPLIANCE-001** ([`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md)); module-side schematic not committed; `TRI_GPIO1` / `TRI_GPIO2` source pins not visible as direct ESP32 GPIOs on Core sheet (route via SX1509, which `ac_dimmer` driver cannot use); placeholder `fan_triac_gate_pin: GPIO5` / `fan_triac_zc_pin: GPIO6` already claimed by RoomIQ J10 |
| `S360-400` | `none` active; legacy `c-pwr` / `v-c-pwr` / `w-pwr` / `v-w-pwr` Core variants are `legacy-compatible` | `none` | `none` (no `PWR`-bearing build today; Release-One is `POE`) | `none` | `none` (`design-pending` for any `PWR`-bearing config) | `not applicable` | `cataloged_unverified / compliance-gated` (`design-pending` + `compliance-gated` per PRODUCT-AVAIL-001) | Module-side schematic not committed; no Core-side connector capture (off-board); **COMPLIANCE-001** mains-voltage UK / EU assessment must clear before any `PWR`-bearing config ships; not critical for Release-One (Release-One ships PoE) |
| `S360-410` | Release-One (`production`) + LED preview (`preview`) + 6 legacy-compatible `*-poe` variants | `done` (same wrappers as Core) | `done` (`stable` + `preview`) | `done` (same artifacts as Core) | `webflash-imported` (Release-One); `webflash-imported` for LED preview | `partial` (consumed by Release-One under the `partially-documented` evidence state; the "schematic verification pending" caveat is preserved in [`release-one-hardware-audit.md` Findings → PoE PSU](../release-one-hardware-audit.md#findings)) | `partially-documented / used-by-Release-One-with-caveat` | Module-side schematic not committed; Core J2 PoE harness identity (HW-002 OQ#6 in [`s360-100-r4-core.md`](s360-100-r4-core.md#open-questions--verification-needed)); the caveat is preserved, not promoted away |

## Board-by-board notes

Each subsection records the per-board evidence, the per-board
gaps, and pointers back to the source-of-truth docs. The matrix
cells above are the summary; these notes are the citations. They
are intentionally short — they link to existing per-board docs
rather than restate them.

### `S360-100` Sense360 Core

- **Role.** Main board (ESP32-S3-WROOM-1-N16R8). Every Release-One,
  preview, and legacy product passes through it.
- **Hardware evidence.** Catalog row at
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  lines 7–16; `schematic_status: verified` under HW-008. Schematic PDF
  at [`docs/hardware/schematics/S360-100-R4.pdf`](schematics/S360-100-R4.pdf)
  (HW-007). Standalone reference at
  [`docs/hardware/s360-100-r4-core.md`](s360-100-r4-core.md). Curated
  artifact index at
  [`docs/hardware/artifacts/S360-100-R4.md`](artifacts/S360-100-R4.md)
  (HW-ASSETS-002) — currently the **only** per-board artifact index in
  the repo.
- **Package YAML.** [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml)
  and the related `sense360_core_*.yaml` family. `confirmed-ok` against
  connector-level evidence today; the systemic abstract-bus mismatch
  (`halo_i2c` / `expansion_i2c` / `uart_bus` / `relay_pin` /
  `status_led_pin` / `pir_sensor_pin` / `expansion_gpio*` not pin-correct
  against the schematic) is enumerated in
  [`release-one-hardware-audit.md` Summary](../release-one-hardware-audit.md#summary)
  and owned by Required follow-ups #2 / #3. **Not unblocked by this
  matrix.**
- **Productization.** Core is consumed by `Ceiling-POE-VentIQ-RoomIQ`
  (Release-One stable) and `Ceiling-POE-VentIQ-RoomIQ-LED` (preview),
  plus the blocked `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` reference.
- **Open work.** Core open-questions list at
  [`s360-100-r4-core.md#open-questions--verification-needed`](s360-100-r4-core.md#open-questions--verification-needed)
  (J6 / J10 pin-order, `IO10` net label, `IO39`–`IO42` ↔ TP mapping, J2
  PoE harness identity, `AirQ_Led` / `AirQ_Status_Led` reuse, FanTRIAC
  GPIO mapping). The bench-side / manufacturing-side companion record
  is [**S360-100-BENCH-001**](s360-100-r4-core.md#s360-100-bench-001-status),
  currently `pending — bench/manufacturing evidence required` (no
  operator, no review date, no observed board / connector / silkscreen
  / harness / rail values, and no BOM / CPL / Gerber / STEP review
  findings supplied). HW-GAP-001 does not resolve any of these. The
  2026-05-18 S360-100-BENCH-001 evidence-pass re-check confirms no new
  bench-side or manufacturing-side evidence has been committed since
  the record was created; the status remains `pending —
  bench/manufacturing evidence required` and no per-question row has
  been promoted (see
  [`s360-100-r4-core.md` Audit log](s360-100-r4-core.md#audit-log)
  for the dated investigation entry).

### `S360-200` Sense360 RoomIQ

- **Role.** Room-sensing module (PIR, LD2450 radar, SEN0609 radar,
  LTR-303ALS, SHT4x, BMP581). Mandatory Release-One component.
- **Hardware evidence.** Catalog row at
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  lines 18–27; `schematic_status: verified` under HW-008. PDF at
  [`schematics/S360-200-R4.pdf`](schematics/S360-200-R4.pdf). Standalone
  reference at [`s360-200-r4-roomiq.md`](s360-200-r4-roomiq.md). Curated
  artifact index deferred (HW-ASSETS-003 conditional).
- **Package YAML.** [`packages/expansions/comfort_ceiling.yaml`](../../packages/expansions/comfort_ceiling.yaml)
  + [`packages/expansions/presence_ceiling.yaml`](../../packages/expansions/presence_ceiling.yaml).
  Both target the abstract `expansion_i2c` bus and `uart_bus`; HW-009
  row `confirmed-ok`.
- **Productization.** Same paths as Core (stable + preview LED).
- **Open work.** Core J10 vs RoomIQ J6 12-pin pin-order disagreement
  flagged in both per-board docs and in
  [`firmware-package-mapping-audit.md` Core J10 vs RoomIQ J6](firmware-package-mapping-audit.md#core-j10-vs-roomiq-j6-pin-order)
  as `needs-silkscreen/bench-verification`. Other RoomIQ `verify`
  flags are listed in
  [`s360-200-r4-roomiq.md`](s360-200-r4-roomiq.md). Not resolved here.

### `S360-210` Sense360 AirIQ

- **Role.** Air-quality module (SCD41 CO₂, SGP41 VOC, MICS-4514 + STM8
  I²C bridge, SPS30 PM connector, SFA30 HCHO connector). Mutually
  exclusive with VentIQ in WebFlash compatibility rules.
- **Hardware evidence.** Catalog row at
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  lines 29–38; `schematic_status: verified` under HW-008. PDF at
  [`schematics/S360-210-R4.pdf`](schematics/S360-210-R4.pdf). Standalone
  reference at [`s360-210-r4-airiq.md`](s360-210-r4-airiq.md). Curated
  artifact index deferred (HW-ASSETS-004 conditional).
- **Package YAML.** [`packages/expansions/airiq_ceiling.yaml`](../../packages/expansions/airiq_ceiling.yaml),
  [`packages/expansions/airiq.yaml`](../../packages/expansions/airiq.yaml),
  and the related `airiq_*` family. HW-009 `confirmed-ok` with the
  legacy-naming caveat (no GPIO binding to `AirQ_Led` /
  `AirQ_Status_Led`).
- **Productization.** No active product YAML consumes AirIQ today;
  Release-One ships VentIQ. AirIQ is referenced by `legacy-compatible`
  AirIQ Core and Mini products only.
- **Open work.** `AirQ_Led` / `AirQ_Status_Led` reuse on AirIQ vs
  VentIQ remains HW-002 Open Question #4. Any future AirIQ-bearing
  config must go through [`docs/product-onboarding.md`](../product-onboarding.md)
  with its own catalog entry, build-matrix entry, and onboarding-gate
  clearance.

### `S360-211` Sense360 VentIQ

- **Role.** Bathroom-focused air-quality module (SGP41, IR-temperature
  connector, SPS30 PM connector, on-board fan-relay drive circuitry).
  Mandatory Release-One component.
- **Hardware evidence.** Catalog row at
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  lines 40–49; `schematic_status: verified` under HW-008. PDF at
  [`schematics/S360-211-R4.pdf`](schematics/S360-211-R4.pdf). Standalone
  reference at [`s360-211-r4-ventiq.md`](s360-211-r4-ventiq.md). Curated
  artifact index deferred (HW-ASSETS-005 conditional).
- **Package YAML.** [`packages/expansions/airiq_bathroom_base.yaml`](../../packages/expansions/airiq_bathroom_base.yaml).
  **Filename retained on purpose** per
  [`webflash-contract.md`](../webflash-contract.md) §6 — renaming would
  break remote-package URLs. HW-009 `confirmed-ok`.
- **Productization.** Same Release-One + LED preview paths as Core.
- **Open work.** `AirQ_Led` / `AirQ_Status_Led` reuse on VentIQ (HW-002
  OQ#4); on-board fan-relay drive-signal source (future fan-driver
  audit); mains-side topology of the on-board relay tracked under
  COMPLIANCE-001
  ([`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md)).
  Not cleared here.

### `S360-300` Sense360 LED

- **Role.** WS2812B LED ring. Deliberately excluded from production
  Release-One (`Ceiling-POE-VentIQ-RoomIQ` carries no `LED` token);
  consumed by `Ceiling-POE-VentIQ-RoomIQ-LED` on the `preview` channel.
- **Hardware evidence.** Catalog row at
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  lines 51–60; `schematic_status: verified` under HW-008. PDF at
  [`schematics/S360-300-R4.pdf`](schematics/S360-300-R4.pdf). Standalone
  reference at [`s360-300-r4-led.md`](s360-300-r4-led.md). Curated
  artifact index deferred (HW-ASSETS-006 conditional).
- **Package YAML.** [`packages/hardware/led_ring_ceiling.yaml`](../../packages/hardware/led_ring_ceiling.yaml)
  binds `led_data_pin: GPIO38` after HW-010 (matches Core `IO38 =
  LED_DATA`); HW-009 row `confirmed-ok`. [`led_ring_wall.yaml`](../../packages/hardware/led_ring_wall.yaml)
  (`GPIO48`) and the legacy [`sense360_core_ceiling_s3.yaml`](../../packages/hardware/sense360_core_ceiling_s3.yaml)
  (`GPIO14`) remain unresolved — neither has a Core-side schematic
  proving the same `LED_DATA` path, and the S3 Core package has no
  product consumer in this repo; the wall LED package is consumed by
  `legacy-compatible` products only.
- **Productization.** `preview` only. Release-One build matrix does not
  include LED. Preview build artifact and import recorded in
  [`webflash-release-proof.md`](../webflash-release-proof.md)
  (RELEASE-003 / RELEASE-005) plus WF-LED-001 / WF-LED-002 / WF-LED-003
  / WF-DEPLOY-001 on the WebFlash side.
- **Open work / stable gate.** Stable promotion is gated by
  [`docs/preview-to-stable-promotion-gates.md`](../preview-to-stable-promotion-gates.md)
  rows 9–17 — operator flash proof (WF-HW-TEST-001), hardware bench
  verification (harness rail, LED count, harness identity, observed
  behaviour per
  [`s360-300-r4-led.md#open-questions--verification-needed`](s360-300-r4-led.md#open-questions--verification-needed),
  tracked under [**S360-300-BENCH-001**](s360-300-r4-led.md#s360-300-bench-001-status)
  which is currently `pending — bench hardware evidence required`),
  stable release notes, production catalog promotion, stable build
  artifact, stable WebFlash import, separate REQUIRED_CONFIGS / kit
  decisions, human approval. **Stays `preview` / `preview` until those
  rows close.**

### `S360-310` Sense360 Relay

- **Role.** On-off relay driver for fan / lamp loads.
- **Hardware evidence.** Catalog row at
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  lines 62–70; `schematic_status: cataloged_unverified`. **No
  module-side schematic** is committed. **No standalone reference
  doc** exists. **No artifact index.** Core-side J4 connector capture
  (3-pin `+5V` / `Relay` / `GND`; drive signal `Relay` from ESP32
  `IO3`) lives in
  [`s360-100-r4-core.md#j4--relay-module-connector-3-pin`](s360-100-r4-core.md#j4--relay-module-connector-3-pin).
  HW-004 / HW-008 classification: `partially-documented`,
  `not-needed-for-release-one`. The HW-PINMAP-310 audit doc
  landed at
  [`s360-310-r4-relay.md`](s360-310-r4-relay.md) records the
  current state as **`pending — schematic/design evidence
  required`** and inventories the evidence required to close it.
- **Package YAML.** [`packages/expansions/fan_relay.yaml`](../../packages/expansions/fan_relay.yaml).
  `package-yaml-pending` against the missing module-side schematic.
  The `IO3` (Core schematic) vs `GPIO4` ([`sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml))
  vs `GPIO10` ([`sense360_core.yaml`](../../packages/hardware/sense360_core.yaml))
  `relay_pin` disagreement is recorded in
  [`s360-310-r4-relay.md` Pin-map reconciliation status](s360-310-r4-relay.md#pin-map-reconciliation-status)
  and is **not** resolved by HW-PINMAP-310 — resolution belongs to
  the systemic Core abstract-bus rebind owned by
  [`release-one-hardware-audit.md` Required follow-ups #2 / #3](../release-one-hardware-audit.md#required-follow-ups).
- **Productization.** No active product consumes Relay. WebFlash
  taxonomy reserves the `FanRelay` token (
  [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json))
  subject to the fan-driver `max-one-of` rule, but no build uses it.
- **Required before promotion.** Module-side schematic + standalone
  reference doc (`HW-PINMAP-310-FOLLOWUP` per
  [`s360-310-r4-relay.md` Follow-up PRs](s360-310-r4-relay.md#follow-up-prs));
  pin-map reconciliation; package YAML reconciliation; product YAML +
  WebFlash wrapper + catalog entry + build-matrix entry through
  [`docs/product-onboarding.md`](../product-onboarding.md).

### `S360-311` Sense360 PWM

- **Role.** 12V PWM fan driver, up to 4 fans with tach feedback.
- **Hardware evidence.** Catalog row at
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  lines 72–81; `schematic_status: cataloged_unverified` (unchanged
  after HW-ASSETS-003 and HW-PINMAP-311). **Module-side schematic now
  committed under HW-ASSETS-003** at
  [`docs/hardware/schematics/S360-311-R4.pdf`](schematics/S360-311-R4.pdf);
  **artifact index now committed** at
  [`docs/hardware/artifacts/S360-311-R4.md`](artifacts/S360-311-R4.md);
  **HW-PINMAP-311 audit doc now committed** at
  [`s360-311-r4-pwm.md`](s360-311-r4-pwm.md) with **status:
  `partial — schematic evidence available; package reconciliation
  pending`**. The audit doc consumes the artifact index and the
  Core-side `J6` capture; it does **not** rewrite either source of
  truth and does **not** promote the JSON `schematic_status`. Still
  no standalone schematic-backed reference doc (the pin-level
  rewrite belongs to HW-PINMAP-311-FOLLOWUP per
  [`s360-311-r4-pwm.md` Follow-up PR sequence](s360-311-r4-pwm.md#follow-up-pr-sequence)).
  Core-side J6 13-pin connector capture
  (`+5V` / `GND` / `TachIO` / `TachPMW1..4` / `Pul_Cou1..4`) lives in
  [`s360-100-r4-core.md#j6--12-v-pwm-fan-connector-13-pin`](s360-100-r4-core.md#j6--12-v-pwm-fan-connector-13-pin)
  with the 1-to-13 pin order explicitly marked **verify** against the
  silkscreen. The module-side `J3` capture additionally labels
  pin 11 / 12 as `UART_RX` / `UART_TX` (routed on-board to a Nextion
  display connector); reconciliation against the Core J6 capture is
  recorded in
  [`s360-311-r4-pwm.md` UART pins on J3 pins 11–12](s360-311-r4-pwm.md#uart-pins-on-j3-pins-1112)
  and owed to HW-PINMAP-311-FOLLOWUP. `TachPMW*` / `Pul_Cou*` are
  driven by the SX1509 expander (see
  [`packages/expansions/gpio_expander_sx1509.yaml`](../../packages/expansions/gpio_expander_sx1509.yaml));
  `TachIO` is ESP32 `IO16` direct.
- **Package YAML.** [`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml).
  `package-yaml-pending` / `needs-package-reconciliation` per
  [`s360-311-r4-pwm.md` Package YAML status](s360-311-r4-pwm.md#package-yaml-status).
  The SX1509-channel vs direct-ESP32-GPIO mapping disagreement (Core
  abstract packages bind FanPWM to direct ESP32 expansion GPIOs
  while the verified Core schematic routes the per-fan signals
  through the SX1509 expander) is recorded in
  [`s360-311-r4-pwm.md` Parent Core packages that resolve `fan_pwm_pin` / `fan_tach_pin`](s360-311-r4-pwm.md#parent-core-packages-that-resolve-fan_pwm_pin--fan_tach_pin)
  and is **not** resolved by HW-PINMAP-311 — resolution belongs to
  the systemic Core abstract-bus rebind owned by
  [`release-one-hardware-audit.md` Required follow-ups #2 / #3](../release-one-hardware-audit.md#required-follow-ups).
- **Productization.** No active product. Legacy
  [`products/sense360-fan-pwm.yaml`](../../products/sense360-fan-pwm.yaml)
  is `legacy-compatible` (pre-WebFlash; standalone fan board; uses
  the legacy four-channel
  [`packages/expansions/sense360_fan_pwm.yaml`](../../packages/expansions/sense360_fan_pwm.yaml),
  not the single-channel `fan_pwm.yaml`).
- **Required before promotion.** Standalone reference doc
  (`HW-PINMAP-311-FOLLOWUP` per
  [`s360-311-r4-pwm.md` Follow-up PRs](s360-311-r4-pwm.md#follow-up-pr-sequence));
  resolve J6 1-to-13 pin-order **verify** flag against silkscreen;
  resolve the UART-on-`J3`-pins-11/12 routing question; package YAML
  reconciliation (`PACKAGE-GAP-001` FanPWM slice); product YAML +
  WebFlash wrapper + catalog entry + build-matrix entry through
  [`docs/product-onboarding.md`](../product-onboarding.md).

### `S360-312` Sense360 DAC

- **Role.** 0–10 V analog fan driver (GP8403), for example Cloudlift S12.
- **Hardware evidence.** Catalog row at
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  lines 82–90; `schematic_status: cataloged_unverified` (unchanged
  after HW-ASSETS-003). **Module-side schematic now committed under
  HW-ASSETS-003** at
  [`docs/hardware/schematics/S360-312-R4.pdf`](schematics/S360-312-R4.pdf);
  **artifact index now committed** at
  [`docs/hardware/artifacts/S360-312-R4.md`](artifacts/S360-312-R4.md).
  **HW-PINMAP-312 audit doc now committed** at
  [`s360-312-r4-dac.md`](s360-312-r4-dac.md) with **status: `partial —
  schematic evidence available; package reconciliation pending`**.
  Standalone schematic-backed reference doc rewrite remains pending
  HW-PINMAP-312-FOLLOWUP.
  Core-side J7 6-pin connector capture (`+5V` /
  `I2C_SDA` / `I2C_SCL` / `UART_RX` / `UART_TX` / `GND`; no `verify`
  flag) lives in
  [`s360-100-r4-core.md#j7--gp8403-fan-connector-6-pin`](s360-100-r4-core.md#j7--gp8403-fan-connector-6-pin).
  The new module-side `J1` capture labels pin 1 as `+3.3V` rather than
  `+5V` and shows **two** GP8403 DACs (`IC1` / `IC2`) on a shared I²C
  bus driving two Cloudlift-style 3-pin outputs; both the voltage-rail
  discrepancy and the dual-DAC capacity are flagged in the artifact
  index and in [`s360-312-r4-dac.md`](s360-312-r4-dac.md) and owed to
  HW-PINMAP-312-FOLLOWUP.
- **Package YAML.** [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml).
  `package-yaml-pending` against the missing module-side schematic.
- **Productization.** No active product. WebFlash taxonomy enforces
  the FanDAC ↔ AirIQ conflict
  ([`config/webflash-compatibility.json`](../../config/webflash-compatibility.json)
  `rules.fandac_conflicts_with_airiq: true`) **and** the fan-driver
  `max-one-of` rule.
- **Required before promotion.** HW-PINMAP-312-FOLLOWUP standalone
  schematic-backed reference doc + voltage-rail discrepancy
  resolution + DIP-switch I²C address scheme resolution + UART0 /
  Nextion path resolution + package YAML reconciliation (per
  [`s360-312-r4-dac.md` Required evidence before promotion](s360-312-r4-dac.md#required-evidence-before-promotion));
  product YAML + WebFlash wrapper + catalog entry + build-matrix entry
  through [`docs/product-onboarding.md`](../product-onboarding.md);
  observe the FanDAC ↔ AirIQ conflict and the fan-driver max-one-of
  rule.

### `S360-320` Sense360 TRIAC

- **Role.** Phase-cut TRIAC dimmer for mains fan / lamp loads. **Stays
  blocked under HW-005 + COMPLIANCE-001.** Intended long-term posture
  is **advanced / manual-warning** per
  [`s360-320-r4-triac.md` §Advanced / manual-warning product posture](s360-320-r4-triac.md#advanced--manual-warning-product-posture)
  — visible / selectable, buildable after package evidence, installable
  only through an advanced / manual-warning path, **not** Release-One,
  **not** REQUIRED_CONFIGS, **not** recommended, **not** kit / default,
  **not** compliance-certified. The advanced / manual-warning posture
  is now **policy-recorded** by `PRODUCT-TRIAC-001` as a notes-only
  catalog edit on `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` in
  [`config/product-catalog.json`](../../config/product-catalog.json);
  the JSON lifecycle row stays `status: blocked`, `blocker: HW-005`,
  `webflash_build_matrix: false`, no `artifact_name`, no new lifecycle
  enum value. This board-readiness matrix does not realise any
  buildable / installable FanTRIAC path; HW-005 and COMPLIANCE-001
  remain open.
- **Hardware evidence.** Catalog row at
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  lines 92–101; `schematic_status: cataloged_unverified` (unchanged
  after HW-ASSETS-003). **Module-side schematic now committed under
  HW-ASSETS-003** at
  [`docs/hardware/schematics/S360-320-R4.pdf`](schematics/S360-320-R4.pdf);
  **artifact index now committed** at
  [`docs/hardware/artifacts/S360-320-R4.md`](artifacts/S360-320-R4.md);
  **HW-PINMAP-320 audit doc now landed** at
  [`s360-320-r4-triac.md`](s360-320-r4-triac.md) with **status:
  `partial — schematic evidence available; package reconciliation,
  timing validation, and compliance/certification pending`**.
  **Committing the schematic, the artifact index, and this audit does
  not unblock HW-005 or clear COMPLIANCE-001.** Core-side J15 4-pin
  connector capture (`+3.3V` / `TRI_GPIO1` / `TRI_GPIO2` / `GND`)
  lives in
  [`s360-100-r4-core.md#j15--triac-fan-module-connector-4-pin`](s360-100-r4-core.md#j15--triac-fan-module-connector-4-pin).
  `TRI_GPIO1` / `TRI_GPIO2` source pins are **not visible as direct
  ESP32 GPIOs** on the Core sheet; they appear to route via the SX1509
  expander (U3), which the ESPHome `ac_dimmer` driver cannot use per
  the timing analysis in
  [`release-one-hardware-audit.md#timing-constraint-ac_dimmer-vs-sx1509-expander`](../release-one-hardware-audit.md#timing-constraint-ac_dimmer-vs-sx1509-expander).
  The module-side `J3` capture labels the same physical pins as
  `+3V3` / `ESP_GPIO1` / `ESP_GPIO2` / `GND` (naming reconciliation
  owed to `HW-PINMAP-320-FOLLOWUP`) and shows discrete `MOC3023M` +
  `BT136` + `EL814` (specifically `Q1 BT136S-600D,118`,
  `U1 MOC3023M`, `OK1 EL814`) with no on-board controller IC —
  eliminating Option (b) from the HW-005 missing-evidence checklist
  for this revision, while Option (a) (end-to-end direct ESP32 GPIOs
  through Core `J15`) remains required and unmet. **HW-004 / HW-008
  classification stays `blocked`, `not-needed-for-release-one`.**
- **Package YAML.** [`packages/expansions/fan_triac.yaml`](../../packages/expansions/fan_triac.yaml)
  is retained as a **blocked / reference** package; HW-009 row
  `blocked`. HW-PINMAP-320 records the package YAML status as
  `package-yaml-pending` / `needs-package-reconciliation` per
  [`s360-320-r4-triac.md` Package YAML status](s360-320-r4-triac.md#package-yaml-status).
  Placeholder `fan_triac_gate_pin: GPIO5` and `fan_triac_zc_pin: GPIO6`
  in the blocked-reference product YAML collide with RoomIQ J10 nets
  (`SEN0609_TX` / `out(gpio6)`). The BLOCKED / UNVERIFIED banner and
  the mains-voltage / qualified-electrician warnings in
  [`packages/expansions/fan_triac.yaml`](../../packages/expansions/fan_triac.yaml)
  remain.
- **Productization.** `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` exists at
  [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml)
  + [`products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`](../../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml)
  as `status: blocked`, `blocker: HW-005`,
  `webflash_build_matrix: false`. Never built; never imported.
  `PRODUCT-TRIAC-001` has performed the **wording-only / notes-only**
  catalog reclassification on this entry, recording the advanced /
  manual-warning candidate posture in `notes` while leaving the
  structural fields (`status` / `blocker` / `reason` /
  `webflash_build_matrix` / no `artifact_name`) unchanged and adding
  no new lifecycle enum value. The product-side rework
  (`PRODUCT-TRIAC-002`), the WebFlash slice (`WF-TRIAC-001`), the
  advanced-channel release (`RELEASE-TRIAC-001`), and the WebFlash
  import (`WF-IMPORT-TRIAC-001`) all remain outstanding per
  [`s360-320-r4-triac.md` Follow-up PR sequence](s360-320-r4-triac.md#follow-up-pr-sequence).
- **Required before unblock.** The HW-005 missing-evidence checklist
  at
  [`release-one-hardware-audit.md#missing-evidence-checklist`](../release-one-hardware-audit.md#missing-evidence-checklist)
  — direct, interrupt-capable ESP32 GPIOs for both `gate_pin` and
  `zero_cross_pin`, traced end-to-end through `S360-100-R4` +
  `S360-320`; or a replacement non-`ac_dimmer` driver targeting an
  on-board controller IC over I²C (the latter eliminated for this
  revision). **Additionally** the mains-voltage compliance gate at
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md)
  (COMPLIANCE-001) must clear independently. HW-005 and COMPLIANCE-001
  are **separate** blockers; neither subsumes the other. Full
  required-evidence list at
  [`s360-320-r4-triac.md` Required evidence before implementation](s360-320-r4-triac.md#required-evidence-before-implementation).

### `S360-400` Sense360 240v PSU

- **Role.** HLK-5M05 mains-to-5 V converter. Off-board. Release-One
  uses PoE PSU `S360-410` instead.
- **Hardware evidence.** Catalog row at
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  lines 102–110; `schematic_status: cataloged_unverified`. **No
  module-side schematic** committed. **No standalone reference doc.**
  **No artifact index.** **No Core-side connector capture** because the
  240 V PSU is off-board and Release-One does not use it. HW-004 /
  HW-008 classification: `cataloged-unverified`,
  `not-needed-for-release-one`. The HW-PINMAP-400 audit doc has
  landed at
  [`s360-400-r4-power.md`](s360-400-r4-power.md) and records the
  current state as **`pending — schematic/design evidence
  required`**; it inventories the evidence required to close it,
  including the COMPLIANCE-001 mains-voltage UK / EU sign-off.
- **Package YAML.** [`packages/hardware/power_240v.yaml`](../../packages/hardware/power_240v.yaml)
  is a logical-power package with no GPIO binding.
- **Productization.** No active product. Legacy `c-pwr` / `v-c-pwr` /
  `w-pwr` / `v-w-pwr` Core variants under
  [`products/`](../../products/) are `legacy-compatible`.
- **Required before promotion.** Module-side schematic + standalone
  reference doc (`HW-PINMAP-400-FOLLOWUP` per
  [`s360-400-r4-power.md` Follow-up PRs](s360-400-r4-power.md#follow-up-prs));
  **COMPLIANCE-001 mains-voltage
  UK / EU assessment** ([`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md))
  must clear before any `PWR`-bearing config ships. Not critical for
  Release-One.

### `S360-410` Sense360 PoE PSU

- **Role.** 802.3af PoE → 5 V. Off-board. **In Release-One under a
  documented schematic-pending caveat.**
- **Hardware evidence.** Catalog row at
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  lines 112–120; `schematic_status: cataloged_unverified`. **No
  module-side schematic** committed. **No standalone reference doc.**
  **No artifact index.** Core-side `J2` `PoE_ACDC` inlet capture
  (2-pin) lives in
  [`s360-100-r4-core.md#j2--poe_acdc-inlet-2-pin`](s360-100-r4-core.md#j2--poe_acdc-inlet-2-pin)
  and in the Core power-rails section. HW-004 / HW-008 classification:
  `partially-documented` (Core-side captured; module-side schematic
  pending). The HW-PINMAP-410 audit doc has landed at
  [`s360-410-r4-poe.md`](s360-410-r4-poe.md) and records the
  current state as **`pending — schematic/design evidence
  required`**; it inventories the evidence required to close it
  and **preserves** the Release-One "schematic verification
  pending" caveat.
- **Package YAML.** [`packages/hardware/power_poe.yaml`](../../packages/hardware/power_poe.yaml)
  is a logical PoE-power package emitting diagnostic sensors only; no
  GPIO binding. `package-yaml-ready` (logical, abstract).
- **Productization.** Consumed by Release-One (stable) and the LED
  preview. The "schematic verification pending" caveat is preserved
  verbatim in
  [`release-one-hardware-audit.md` Findings → PoE PSU](../release-one-hardware-audit.md#findings)
  and is **not promoted away** by this matrix or by the HW-PINMAP-410
  audit doc.
- **Required before module-side promotion.** Module-side schematic +
  standalone reference doc (`HW-PINMAP-410-FOLLOWUP` per
  [`s360-410-r4-poe.md` Follow-up PRs](s360-410-r4-poe.md#follow-up-prs));
  J2 PoE harness identity
  (HW-002 Open Question #6 at
  [`s360-100-r4-core.md#open-questions--verification-needed`](s360-100-r4-core.md#open-questions--verification-needed),
  tracked on
  [S360-100-BENCH-001](s360-100-r4-core.md#s360-100-bench-001-status)
  as `pending — bench/manufacturing evidence required`). None of these
  block Release-One use; they are open work for the PoE PSU module
  itself.

## Ready / evidenced boards

These five SKUs carry a `verified` `schematic_status` in
[`config/hardware-catalog.json`](../../config/hardware-catalog.json) and
have committed module-side schematic PDFs plus schematic-backed
standalone reference docs. They are **hardware-evidenced**:

- `S360-100` Sense360 Core — `hardware-evidenced / productized /
  WebFlash-used`; Release-One stable + LED preview.
- `S360-200` Sense360 RoomIQ — `hardware-evidenced / productized /
  WebFlash-used`; Release-One stable + LED preview.
- `S360-210` Sense360 AirIQ — `hardware-evidenced / firmware-missing`;
  no active product YAML consumes it; mutex with VentIQ.
- `S360-211` Sense360 VentIQ — `hardware-evidenced / productized /
  WebFlash-used`; Release-One stable + LED preview.
- `S360-300` Sense360 LED — `hardware-evidenced / preview-only`; LED
  preview build only; stable promotion blocked by RELEASE-006 rows
  9–17.

**Hardware-evidenced is not the same as WebFlash-ready.** `S360-210`
is hardware-evidenced but has no active product YAML; `S360-300` is
hardware-evidenced and has a `preview` build but is intentionally not
stable. See [Core rule](#core-rule).

## Missing / unfinished boards

These six SKUs are `cataloged_unverified` in
[`config/hardware-catalog.json`](../../config/hardware-catalog.json) and
**lack module-side schematic, standalone reference doc, and per-board
artifact index**. They are not productized to WebFlash today.

- `S360-310` Sense360 Relay — `design-pending`. Needs `HW-PINMAP-310`
  (schematic + reference doc), pin-map reconciliation, package YAML
  reconciliation, product YAML decision.
- `S360-311` Sense360 PWM — `design-pending`. Module-side schematic
  committed under HW-ASSETS-003; HW-PINMAP-311 audit doc landed at
  [`s360-311-r4-pwm.md`](s360-311-r4-pwm.md) (status:
  `partial — schematic evidence available; package reconciliation
  pending`). Still needs `HW-PINMAP-311-FOLLOWUP` (standalone
  reference doc + pin-map reconciliation; J6 pin-order **verify**
  must resolve against silkscreen; UART-on-`J3`-pins-11/12 routing
  resolution), `PACKAGE-GAP-001` FanPWM slice for package YAML
  reconciliation, product YAML decision.
- `S360-312` Sense360 DAC — `design-pending`. HW-PINMAP-312 audit doc
  landed at [`s360-312-r4-dac.md`](s360-312-r4-dac.md) with
  **status: `partial — schematic evidence available; package
  reconciliation pending`**. Needs HW-PINMAP-312-FOLLOWUP (standalone
  reference doc + Core J7 / Module J1 pin-1 voltage-rail
  discrepancy resolution + DIP-switch I²C address scheme + UART0 /
  Nextion path), `PACKAGE-GAP-001` FanDAC slice for package YAML
  reconciliation, product YAML decision; FanDAC ↔ AirIQ conflict and
  fan-driver max-one-of rule must be respected.
- `S360-400` Sense360 240v PSU — `design-pending` + `compliance-gated`.
  HW-PINMAP-400 audit doc landed at
  [`s360-400-r4-power.md`](s360-400-r4-power.md) with **status:
  `pending — schematic/design evidence required`**. Still needs
  `HW-ASSETS-400` (schematic ingest), `HW-PINMAP-400-FOLLOWUP`
  (standalone reference doc), and COMPLIANCE-001 sign-off;
  off-board PSU, no Core-side connector capture today.
- `S360-410` Sense360 PoE PSU — `partially-documented`, **used by
  Release-One with documented schematic-pending caveat**.
  HW-PINMAP-410 audit doc landed at
  [`s360-410-r4-poe.md`](s360-410-r4-poe.md) with **status:
  `pending — schematic/design evidence required`** (caveat
  preserved). Still needs `HW-ASSETS-410` (schematic ingest),
  `HW-PINMAP-410-FOLLOWUP` (standalone reference doc), and
  resolution of HW-002 Open Question #6 (J2 harness identity,
  tracked on
  [S360-100-BENCH-001](s360-100-r4-core.md#s360-100-bench-001-status)).
- `S360-320` Sense360 TRIAC — see [Blocked / compliance-gated boards](#blocked--compliance-gated-boards).

**None of the missing boards is unblocked or promoted by HW-GAP-001.**
This matrix records what is missing; it does not produce schematics,
pin maps, package reconciliations, product YAMLs, build entries,
release artifacts, or WebFlash imports.

## Blocked / compliance-gated boards

- **`S360-320` Sense360 TRIAC — `blocked` under HW-005 +
  `compliance-gated` under COMPLIANCE-001.** Stays blocked. HW-005
  (FanTRIAC mapping) is a prior, independent blocker; COMPLIANCE-001
  (mains-voltage UK / EU) is an additional gate on any product /
  WebFlash work. The product entry
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`,
  `blocker: HW-005`, `webflash_build_matrix: false`. The HW-005
  missing-evidence checklist lives at
  [`release-one-hardware-audit.md#missing-evidence-checklist`](../release-one-hardware-audit.md#missing-evidence-checklist).
  The compliance tracker lives at
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md).
- **`S360-400` Sense360 240v PSU — `compliance-gated` under
  COMPLIANCE-001.** Mains-voltage UK / EU sign-off is required before
  any `PWR`-bearing product YAML / WebFlash wrapper / build-matrix
  entry ships. Release-One uses PoE; the 240 V PSU is not on the
  critical path today.

HW-GAP-001 changes neither blocker. The COMPLIANCE-001 status of
either board is not modified.

## Relationship to product availability

HW-GAP-001 is the **board-level** matrix that feeds the
**cross-cutting availability ladder** in
[`docs/product-availability-taxonomy.md`](../product-availability-taxonomy.md)
(PRODUCT-AVAIL-001). The relationship is:

- PRODUCT-AVAIL-001 defines the 13-rung ladder from `hardware-listed`
  to `kit-exposed`, the per-axis state vocabulary
  (hardware-side / product-lifecycle / WebFlash-availability /
  exception), and the policy-only `design-pending` /
  `firmware-missing` labels. It carries a **current snapshot** for
  every SKU in its
  [Current board / product snapshot](../product-availability-taxonomy.md#current-board--product-snapshot)
  section.
- HW-GAP-001 expands that snapshot into the per-board readiness matrix
  above and adds the readiness-axis breakdown (artifact index, pin map,
  package YAML, product YAML, wrapper, build matrix, release artifact,
  WebFlash manifest, bench proof). Every cell uses vocabulary already
  defined by PRODUCT-AVAIL-001, HW-004 / HW-006 / HW-008, HW-009 /
  HW-010, HW-ASSETS-001, RELEASE-006, PRODUCT-DEP-001, or the JSON
  catalogs themselves.

If the matrix here and any source-of-truth axis-specific doc drift,
the **source-of-truth doc wins** and this matrix must be updated.
HW-GAP-001 introduces no labels not already used by one of those
sources, except the policy-only convenience labels enumerated in
[Status value vocabulary](#status-value-vocabulary-policy-only).

## Relationship to WebFlash availability

WebFlash should consume this matrix as the per-board reference when
implementing the wizard-gating and import-readiness behaviours
specified in
[`docs/product-availability-taxonomy.md` How WebFlash should consume this taxonomy](../product-availability-taxonomy.md#how-webflash-should-consume-this-taxonomy).
The downstream WebFlash-side PRs that should consume the matrix are:

- **WF-WIZARD-AVAIL-001** — gate `design-pending` and
  `firmware-missing` modules / configs in the wizard so customers
  cannot pick a combination that cannot be flashed today.
- **WF-WIZARD-AVAIL-002** — surface the named blocker for any
  `blocked` selection (HW-005 for FanTRIAC; COMPLIANCE-001 for
  mains-voltage boards) instead of letting the customer pick that
  combination.
- **WF-STALE-001** — clean up wizard / kit / manifest references to
  modules and configs that the matrix records as `design-pending` /
  `firmware-missing` / `blocked` / `deprecated` / `removed`.
- **WF-PRODUCT-005** — enforce import readiness so that the WebFlash
  ingest step refuses any catalog entry whose lifecycle status is
  `blocked` / `deprecated` / `removed`, and distinguishes `preview`
  from `production`.

**HW-GAP-001 does not edit WebFlash.** Those PRs live in the
[`sense360store/WebFlash`](https://github.com/sense360store/WebFlash)
repo and have their own scope, review, and import / release flow per
[`docs/webflash-release-handoff.md`](../webflash-release-handoff.md).

## Follow-up PR sequence

Each entry is a separate PR with its own scope, review, and gate
evidence. HW-GAP-001 does not commit to a calendar and does not
order these beyond the dependencies recorded in
[`docs/hardware/hardware-artifact-policy.md` Follow-up PR sequence](hardware-artifact-policy.md#follow-up-pr-sequence)
and
[`docs/product-availability-taxonomy.md` Follow-up PR sequence](../product-availability-taxonomy.md#follow-up-pr-sequence).

1. **`HW-PINMAP-310` — `S360-310` pin / package mapping audit.**
   Module-side schematic ingest, standalone reference doc, pin-map
   reconciliation, package YAML reconciliation. Per
   [`hardware-artifact-policy.md` Follow-up PR sequence](hardware-artifact-policy.md#follow-up-pr-sequence)
   item #3. The HW-PINMAP-310 audit doc has landed at
   [`s360-310-r4-relay.md`](s360-310-r4-relay.md) with
   **status: `pending — schematic/design evidence required`**;
   the schematic ingest, the standalone schematic-backed reference
   doc, the pin-map reconciliation, and the package YAML
   reconciliation each remain owed to evidence-bearing follow-up
   PRs (`HW-ASSETS-310`, `HW-PINMAP-310-FOLLOWUP`,
   `PACKAGE-GAP-001` FanRelay slice — see
   [`s360-310-r4-relay.md` Follow-up PRs](s360-310-r4-relay.md#follow-up-prs)).
2. **`HW-PINMAP-311` — `S360-311` pin / package mapping audit.** Same
   for Sense360 PWM. The HW-PINMAP-311 audit doc has landed at
   [`s360-311-r4-pwm.md`](s360-311-r4-pwm.md) with
   **status: `partial — schematic evidence available; package
   reconciliation pending`**; the standalone schematic-backed
   reference doc rewrite, the Core J6 1-to-13 pin-order **verify**
   flag against silkscreen, the UART-on-`J3`-pins-11/12 routing
   resolution, and the FanPWM package YAML reconciliation each
   remain owed to evidence-bearing follow-up PRs
   (`HW-PINMAP-311-FOLLOWUP`, `PACKAGE-GAP-001` FanPWM slice — see
   [`s360-311-r4-pwm.md` Follow-up PRs](s360-311-r4-pwm.md#follow-up-pr-sequence)).
3. **`HW-PINMAP-312` — `S360-312` pin / package mapping audit.** Same
   for Sense360 DAC. The HW-PINMAP-312 audit doc has landed at
   [`s360-312-r4-dac.md`](s360-312-r4-dac.md) with
   **status: `partial — schematic evidence available; package
   reconciliation pending`**; the standalone schematic-backed
   reference doc rewrite, the Core `J7` pin-1 `+5V` vs Module `J1`
   pin-1 `+3.3V` voltage-rail discrepancy resolution, the DIP-switch
   I²C address-selection scheme on `IC1` / `IC2`, the UART0-vs-Nextion
   path resolution, and the FanDAC package YAML reconciliation each
   remain owed to evidence-bearing follow-up PRs
   (`HW-PINMAP-312-FOLLOWUP`, `PACKAGE-GAP-001` FanDAC slice — see
   [`s360-312-r4-dac.md` Follow-up PRs](s360-312-r4-dac.md#follow-up-pr-sequence)).
4. **`HW-PINMAP-320` — `S360-320` FanTRIAC pin / package mapping
   audit.** **Landed** at
   [`s360-320-r4-triac.md`](s360-320-r4-triac.md) with
   **status: `partial — schematic evidence available; package
   reconciliation, timing validation, and compliance/certification
   pending`**; records the module-side `J3` ↔ Core-side `J15`
   reconciliation, the `TRI_GPIO*` / `ESP_GPIO*` naming divergence,
   the `ac_dimmer` timing constraint, the FanTRIAC package
   `needs-package-reconciliation` status, the intended advanced /
   manual-warning long-term product posture (not realised by this
   PR), and the full follow-up PR sequence. Does **not** unblock
   HW-005 by itself; HW-005 resolution and COMPLIANCE-001
   mains-voltage sign-off remain prerequisites for any product /
   WebFlash work on this board. Follow-ups:
   `HW-PINMAP-320-FOLLOWUP`, `PACKAGE-TRIAC-001`,
   `PRODUCT-TRIAC-001`, `PRODUCT-TRIAC-002`, `WF-TRIAC-001`,
   `RELEASE-TRIAC-001`, `WF-IMPORT-TRIAC-001`, `COMPLIANCE-001`,
   `HW-005`, `HW-CATALOG-320` — per
   [`s360-320-r4-triac.md` Follow-up PR sequence](s360-320-r4-triac.md#follow-up-pr-sequence).
5. **`HW-PINMAP-400` — `S360-400` power-board mapping audit.** The
   HW-PINMAP-400 audit doc has landed at
   [`s360-400-r4-power.md`](s360-400-r4-power.md) with
   **status: `pending — schematic/design evidence required`**;
   the schematic ingest, the standalone schematic-backed reference
   doc, the rail / harness / safety reconciliation, and the
   COMPLIANCE-001 mains-voltage UK / EU sign-off each remain owed
   to evidence-bearing follow-up PRs (`HW-ASSETS-400`,
   `HW-PINMAP-400-FOLLOWUP`, `COMPLIANCE-001` S360-400 slice — see
   [`s360-400-r4-power.md` Follow-up PRs](s360-400-r4-power.md#follow-up-prs)).
   Gated by COMPLIANCE-001 for any product / WebFlash work.
6. **`HW-PINMAP-410` — `S360-410` PoE PSU mapping audit.** The
   HW-PINMAP-410 audit doc has landed at
   [`s360-410-r4-poe.md`](s360-410-r4-poe.md) with
   **status: `pending — schematic/design evidence required`**;
   the schematic ingest, the standalone schematic-backed reference
   doc, the PoE / rail / connector / harness reconciliation, and
   the HW-002 OQ#6 (J2 harness identity) closure each remain
   owed to evidence-bearing follow-up PRs (`HW-ASSETS-410`,
   `HW-PINMAP-410-FOLLOWUP`, `S360-100-BENCH-001` update — see
   [`s360-410-r4-poe.md` Follow-up PRs](s360-410-r4-poe.md#follow-up-prs)).
   The "schematic verification pending" caveat preserved in
   [`release-one-hardware-audit.md` Findings → PoE PSU](../release-one-hardware-audit.md#findings)
   is **not** promoted away by the audit doc; the caveat closure
   is owed to a later Release-One caveat-closure PR after the
   evidence above lands.
7. **`PACKAGE-GAP-001` — Add / reconcile package YAMLs where evidence
   exists.** After the `HW-PINMAP-*` sequence; per-board scope; does
   not promote any product. The package-level readiness matrix has
   landed at [`package-readiness-matrix.md`](package-readiness-matrix.md)
   with **status: no package YAML is `ready-for-package-change`
   today**. All six in-scope packages
   ([`fan_relay.yaml`](../../packages/expansions/fan_relay.yaml),
   [`fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml),
   [`fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml),
   [`fan_triac.yaml`](../../packages/expansions/fan_triac.yaml),
   [`power_240v.yaml`](../../packages/hardware/power_240v.yaml),
   [`power_poe.yaml`](../../packages/hardware/power_poe.yaml)) carry
   `schematic-evidence-pending` / `needs-package-reconciliation` /
   `bench-evidence-pending` / `timing/compliance-pending` /
   `reference-only` / `blocked-from-standard-exposure` labels; the
   per-package follow-up PRs are split as `PACKAGE-RELAY-001`,
   `PACKAGE-PWM-001`, `PACKAGE-DAC-001`, `PACKAGE-TRIAC-001`,
   `PACKAGE-POWER-400-001`, `PACKAGE-POE-410-001`, with
   `CORE-ABSTRACT-BUS-001` paired where the Core abstract
   substitutions are consumed. See
   [`package-readiness-matrix.md` Follow-up PR sequence](package-readiness-matrix.md#follow-up-pr-sequence).
8. **`PRODUCT-GAP-001` — Add product YAMLs where packages and
   evidence exist.** After `PACKAGE-GAP-001`. Goes through
   [`docs/product-onboarding.md`](../product-onboarding.md) gates and,
   for any stable promotion, the
   [`docs/preview-to-stable-promotion-gates.md`](../preview-to-stable-promotion-gates.md)
   gates.
9. **`WEBFLASH-GAP-001` — Add wrappers / catalog / build-matrix
   entries for selected new products.** After `PRODUCT-GAP-001`.
10. **`RELEASE-GAP-001` — Build / release artifacts for selected new
    products.** After `WEBFLASH-GAP-001`. Uses the existing
    [`.github/workflows/firmware-build-release.yml`](../../.github/workflows/firmware-build-release.yml)
    flow.
11. **`WF-IMPORT-GAP-001` — Import selected new firmware builds into
    WebFlash.** After `RELEASE-GAP-001`. Owned by the WebFlash repo
    per [`docs/webflash-release-handoff.md`](../webflash-release-handoff.md).

None of these is approved or scoped by HW-GAP-001. They are recorded
so the matrix has a clear next-action chain.

## Do-not-change guardrails

HW-GAP-001 — this matrix — performs **none** of the following.
Anyone reading this matrix looking for justification to change one of
them must use a separate, scoped PR with its own gate evidence.

- No edits to
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json),
  [`config/product-catalog.json`](../../config/product-catalog.json),
  [`config/webflash-builds.json`](../../config/webflash-builds.json),
  or
  [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json).
- No new JSON fields added to any catalog; no new status / channel /
  lifecycle / schematic-status value added to any enum.
- No edits to any product YAML under [`products/`](../../products/) or
  any WebFlash wrapper under
  [`products/webflash/`](../../products/webflash/).
- No edits to any package YAML under
  [`packages/`](../../packages/).
- No edits to any workflow under `.github/workflows/`, any script
  under [`scripts/`](../../scripts/), any test under
  [`tests/`](../../tests/), any component under `components/`, or any
  include under `include/`.
- No firmware regenerated; no GitHub Release created or modified; no
  manifest signed; no WebFlash import; no kit added.
- Release-One stays `Ceiling-POE-VentIQ-RoomIQ`, version `1.0.0`,
  channel `stable`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag `v1.0.0`.
- The LED preview entry `Ceiling-POE-VentIQ-RoomIQ-LED` stays
  `status: preview`, `channel: preview`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`. No
  promotion to `production` / `stable`; no addition to
  `REQUIRED_CONFIGS`; no kit added.
- FanTRIAC stays `status: blocked`, `blocker: HW-005`,
  `webflash_build_matrix: false`. HW-005 is not resolved;
  COMPLIANCE-001 is not cleared.
- The mains-voltage compliance status for `S360-320` (FanTRIAC) and
  `S360-400` (240 V PSU) is owned by COMPLIANCE-001
  ([`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md))
  and is not changed.
- The Core J10 vs RoomIQ J6 pin-order discrepancy
  (`needs-silkscreen/bench-verification` per HW-009) is not resolved.
- The systemic Core abstract-bus mismatch in
  [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml)
  (`needs-package-change`, owned by
  [`release-one-hardware-audit.md` Required follow-ups #2 / #3](../release-one-hardware-audit.md#required-follow-ups))
  is not resolved.
- The `S360-410` PoE PSU schematic-pending caveat in
  [`release-one-hardware-audit.md` Findings → PoE PSU](../release-one-hardware-audit.md#findings)
  is **preserved**, not promoted away.
- The `S360-300` bench-verification Open Questions in
  [`s360-300-r4-led.md`](s360-300-r4-led.md#open-questions--verification-needed)
  (harness rail, LED count, harness identity, observed behaviour) are
  **preserved**; the bench-side tracking record
  [S360-300-BENCH-001](s360-300-r4-led.md#s360-300-bench-001-status)
  remains `pending — bench hardware evidence required` (no operator,
  no date, no observed values supplied).
- The `S360-100` Core schematic-side Open Questions in
  [`s360-100-r4-core.md`](s360-100-r4-core.md#open-questions--verification-needed)
  (J6 / J10 silkscreen pin order, `IO10` net label, `IO39`–`IO42` ↔ TP
  mapping, J2 PoE harness identity, `AirQ_Led` / `AirQ_Status_Led`
  reuse) are **preserved**; the bench-side / manufacturing-side
  tracking record
  [S360-100-BENCH-001](s360-100-r4-core.md#s360-100-bench-001-status)
  remains `pending — bench/manufacturing evidence required` (no
  operator, no review date, no observed board / connector / silkscreen
  / harness / rail values, and no BOM / CPL / Gerber / STEP review
  findings supplied).
- Every `legacy-compatible` entry stays `legacy-compatible` and
  remains out of the WebFlash build matrix.
- No entry is added to or removed from WebFlash-side
  `REQUIRED_CONFIGS`, `scripts/data/kits.json`, `firmware/sources.json`,
  or `manifest.json` — those are WebFlash-owned and are not touched by
  this repo.

## See also

- [`docs/product-availability-taxonomy.md`](../product-availability-taxonomy.md)
  — PRODUCT-AVAIL-001 canonical cross-cutting product availability
  taxonomy. Carries the 13-rung availability ladder, the per-axis
  state vocabulary, and the current per-SKU snapshot that this matrix
  expands into a fuller per-board readiness view.
- [`docs/hardware/hardware-artifact-policy.md`](hardware-artifact-policy.md)
  — HW-ASSETS-001 canonical hardware source / manufacturing artifact
  policy. Defines the per-board artifact-index schema
  (`pin_map_status` / `package_yaml_status` / `product_yaml_status` /
  `webflash_status`) whose field names this matrix reuses as
  policy-only column vocabulary.
- [`docs/hardware/artifacts/S360-100-R4.md`](artifacts/S360-100-R4.md)
  — HW-ASSETS-002 curated artifact index for Sense360 Core. The only
  per-board artifact index in the repo today; the template for
  HW-ASSETS-003 / 004 / 005 / 006.
- [`docs/hardware/remaining-board-documentation-audit.md`](remaining-board-documentation-audit.md)
  — HW-004 / HW-006 per-board documentation-state classification with
  HW-007 schematic-ingest and HW-008 JSON-refresh subsections. Source
  of truth for the `documented` / `partially-documented` /
  `cataloged-unverified` / `blocked` / `not-needed-for-release-one`
  audit vocabulary the matrix consumes.
- [`docs/hardware/firmware-package-mapping-audit.md`](firmware-package-mapping-audit.md)
  — HW-009 / HW-010 firmware-package-vs-schematic audit. Source of
  truth for the `confirmed-ok` / `needs-package-change` /
  `needs-doc-fix` / `needs-silkscreen/bench-verification` / `blocked`
  / `unknown` package-mapping vocabulary the matrix consumes.
- [`docs/hardware/package-readiness-matrix.md`](package-readiness-matrix.md)
  — PACKAGE-GAP-001 package-level readiness gate. Per-package status
  for the six in-scope expansion / power packages
  ([`fan_relay.yaml`](../../packages/expansions/fan_relay.yaml),
  [`fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml),
  [`fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml),
  [`fan_triac.yaml`](../../packages/expansions/fan_triac.yaml),
  [`power_240v.yaml`](../../packages/hardware/power_240v.yaml),
  [`power_poe.yaml`](../../packages/hardware/power_poe.yaml)) plus
  the Core abstract-bus packages, with the policy-only label
  vocabulary (`ready-for-package-change` /
  `needs-package-reconciliation` /
  `schematic-evidence-pending` / `bench-evidence-pending` /
  `timing/compliance-pending` / `reference-only` /
  `do-not-change-release-one` /
  `blocked-from-standard-exposure`), the per-slice
  implementation gates, and the per-package follow-up PR sequence
  (`PACKAGE-RELAY-001`, `PACKAGE-PWM-001`, `PACKAGE-DAC-001`,
  `PACKAGE-TRIAC-001`, `PACKAGE-POWER-400-001`,
  `PACKAGE-POE-410-001`, `CORE-ABSTRACT-BUS-001`). Documentation
  only.
- [`docs/release-one-hardware-audit.md`](../release-one-hardware-audit.md)
  — Release-One firmware-vs-schematic audit; the source of truth for
  the HW-005 FanTRIAC blocker, the systemic Core abstract-bus rebind
  follow-ups, and the `S360-410` PoE PSU schematic-pending caveat.
- [`docs/release-one.md`](../release-one.md) — Release-One
  configuration; the only `production` entry today.
- [`docs/preview-to-stable-promotion-gates.md`](../preview-to-stable-promotion-gates.md)
  — RELEASE-006 canonical 17-row preview-to-stable gate document. The
  source of truth for the `S360-300` LED stable-promotion gates.
- [`docs/product-deprecation-removal-policy.md`](../product-deprecation-removal-policy.md)
  — PRODUCT-DEP-001 canonical cross-cutting deprecation / removal
  policy. Defines `deprecated` and `removed`; this matrix records
  every legacy-compatible row's exclusion from any WebFlash-shippable
  state.
- [`docs/product-onboarding.md`](../product-onboarding.md) —
  PRODUCT-004 ordered safe onboarding sequence; every `PRODUCT-GAP-001`
  follow-up listed in [Follow-up PR sequence](#follow-up-pr-sequence)
  goes through these gates.
- [`docs/webflash-contract.md`](../webflash-contract.md) — canonical
  WebFlash artifact / grammar / token contract. §6 retains legacy
  package filenames (`airiq_bathroom_base.yaml` / `comfort_*.yaml` /
  `presence_*.yaml` / `led_ring_*.yaml`) on purpose.
- [`docs/webflash-release-handoff.md`](../webflash-release-handoff.md)
  — operational source-to-installer flow. Defines the seam between
  `release-artifact-ready` and `webflash-imported`.
- [`docs/webflash-release-proof.md`](../webflash-release-proof.md) —
  Release-One ESP-006 / ESP-007 proof plus RELEASE-003 / RELEASE-005
  LED preview proof.
- [`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md)
  — COMPLIANCE-001 mains-voltage UK / EU compliance-assessment
  tracker. Additional gate for any product / WebFlash work consuming
  `S360-320` (FanTRIAC) or `S360-400` (240v PSU).
- [`docs/cleanup-audit.md`](../cleanup-audit.md) — classification of
  stale / current / blocked-reference / legacy-compatible repo
  content; carries the HW-GAP-001 registration row.
- [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  — machine-readable hardware catalog. `schematic_status` is
  `verified` for the five `hardware-evidenced` SKUs and
  `cataloged_unverified` for the six others; HW-GAP-001 changes none
  of these values.
- [`config/product-catalog.json`](../../config/product-catalog.json) —
  machine-readable product catalog. The eight `lifecycle_statuses` are
  reused verbatim; HW-GAP-001 changes none of them.
- [`config/webflash-builds.json`](../../config/webflash-builds.json) —
  machine-readable WebFlash build matrix; the two active builds
  (`Ceiling-POE-VentIQ-RoomIQ` stable, `Ceiling-POE-VentIQ-RoomIQ-LED`
  preview) are unchanged.
- [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json)
  — machine-readable WebFlash taxonomy / token / mutex / forbidden
  rules. AirIQ ↔ VentIQ mutex, fan-driver `max-one-of`, FanDAC ↔ AirIQ
  conflict, and reserved tokens for future fan drivers are unchanged.
- [`docs/hardware-catalog.md`](../hardware-catalog.md) — canonical
  Sense360 board / module names, SKUs, revisions, legacy names. The
  naming source of truth this matrix quotes.
- Per-board hardware reference docs —
  [`s360-100-r4-core.md`](s360-100-r4-core.md),
  [`s360-200-r4-roomiq.md`](s360-200-r4-roomiq.md),
  [`s360-210-r4-airiq.md`](s360-210-r4-airiq.md),
  [`s360-211-r4-ventiq.md`](s360-211-r4-ventiq.md),
  [`s360-300-r4-led.md`](s360-300-r4-led.md). Each carries its own
  open-questions list and is the source of truth for pin-level
  questions about its board.
- [`s360-310-r4-relay.md`](s360-310-r4-relay.md) — HW-PINMAP-310
  pin/package mapping audit for `S360-310` Sense360 Relay,
  **status: `pending — schematic/design evidence required`**. Not
  a schematic-backed reference doc; an evidence-gap record that
  inventories what HW-ASSETS-310 / HW-PINMAP-310-FOLLOWUP must
  supply.
- [`s360-311-r4-pwm.md`](s360-311-r4-pwm.md) — HW-PINMAP-311
  pin/package mapping audit for `S360-311` Sense360 PWM,
  **status: `partial — schematic evidence available; package
  reconciliation pending`**. Consumes the HW-ASSETS-003 module-side
  schematic and artifact index; records the
  SX1509-channel vs direct-ESP32-GPIO mapping disagreement, the
  UART-on-`J3`-pins-11/12 routing question, and the
  `"NINE 4pin FANs"` documentation question as **unresolved by this
  PR**; defers package YAML reconciliation to a future
  `PACKAGE-GAP-001` FanPWM slice and the systemic Core abstract-bus
  rebind owned by
  [`release-one-hardware-audit.md` Required follow-ups #2 / #3](../release-one-hardware-audit.md#required-follow-ups).
- [`s360-400-r4-power.md`](s360-400-r4-power.md) — HW-PINMAP-400
  pin/package mapping audit for `S360-400` Sense360 240v PSU,
  **status: `pending — schematic/design evidence required`**. Not
  a schematic-backed reference doc; an evidence-gap record that
  inventories what HW-ASSETS-400 / HW-PINMAP-400-FOLLOWUP /
  COMPLIANCE-001 must supply. Records the `HLK-5M05` (catalog)
  vs `HLK-PM01 or similar` (package-header) AC-DC part-identity
  disagreement and the COMPLIANCE-001 mains-voltage UK / EU
  gate as **unresolved by this PR**.
- [`s360-410-r4-poe.md`](s360-410-r4-poe.md) — HW-PINMAP-410
  pin/package mapping audit for `S360-410` Sense360 PoE PSU,
  **status: `pending — schematic/design evidence required`**. Not
  a schematic-backed reference doc; an evidence-gap record that
  inventories what HW-ASSETS-410 / HW-PINMAP-410-FOLLOWUP /
  HW-002 OQ#6 closure must supply. **Preserves the Release-One
  "schematic verification pending" caveat** in
  [`release-one-hardware-audit.md` Findings → PoE PSU](../release-one-hardware-audit.md#findings)
  and **does not promote it away**.
- [`../product-readiness-matrix.md`](../product-readiness-matrix.md)
  — PRODUCT-GAP-001 product-level readiness gate. Per-candidate-
  product-family verdict (FanRelay / FanPWM / FanDAC / FanTRIAC /
  PWR-240V / PoE-410) that sits one rung above the per-package
  [`package-readiness-matrix.md`](package-readiness-matrix.md) and
  records the per-family follow-up PR sequence (`PRODUCT-RELAY-001`,
  `PRODUCT-PWM-001`, `PRODUCT-DAC-001`, `PRODUCT-TRIAC-001`,
  `PRODUCT-POWER-400-001`, `PRODUCT-POE-410-001`) plus the
  downstream WebFlash exposure chain (`WEBFLASH-GAP-001` /
  `RELEASE-GAP-001` / `WF-IMPORT-GAP-001`, `WF-TRIAC-001` for the
  FanTRIAC advanced-flow). The Follow-up PR sequence row #8 of
  this matrix already names PRODUCT-GAP-001 as its successor.
  Documentation only.

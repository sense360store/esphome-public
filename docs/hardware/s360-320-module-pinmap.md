# S360-320 Module-Side Pinmap (MODULE-PINMAPS-GDRIVE-001)

## Status

**Status: documentation-only schematic-backed module-side pinmap.
FanTRIAC `HW-005` stays blocked; COMPLIANCE-001 stays in force.**
Companion to the canonical Core-side
[`s360-100-core-connector-pin-map.md`](s360-100-core-connector-pin-map.md)
(S360-100-CONNECTOR-PINMAP-001). This document records the
**module-side** view of the Sense360 TRIAC (`S360-320`) board and
reconciles every pin back to the mating Core connector `J15`.

It is **documentation only**. It does **not**:

- publish firmware, create release artifacts, or promote any
  release target;
- promote `S360-320` `schematic_status` in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  beyond its current `cataloged_unverified` value;
- claim the FanTRIAC `HW-005` blocker is solved
  (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`,
  `blocker: HW-005`, `webflash_build_matrix: false`);
- resolve the `TRI_GPIO1` / `TRI_GPIO2` (Core sheet) ↔
  `ESP_GPIO1` / `ESP_GPIO2` (module sheet) net-name divergence;
- resolve the AC LINE `J1` 3-pin function (L / N / PE);
- clear the mains-voltage UK / EU compliance gate (COMPLIANCE-001
  per
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md));
- fabricate connector type, pin order, signal mapping, or ESP32
  GPIO allocation. Values not proven by the committed module-side
  schematic PDF or the canonical Core schematic carry **TBD** or
  **needs silkscreen confirmation**.

## Board identity

| Field | Value |
|---|---|
| Friendly name | Sense360 TRIAC |
| SKU | `S360-320` |
| Rev | R4 |
| Mating Core connector | `J15` (4-pin TRIAC module connector) on `S360-100-R4` |
| Module-side connector | `J3` (4-pin "From Core") on `S360-320-R4` |
| Module-side AC LINE input | `J1` (3-pin) — mains-rated; out of scope for this pinmap |
| Module-side LOAD output | `J2` (2-pin) — switched mains; out of scope for this pinmap |
| Companion audit doc | [`s360-320-r4-triac.md`](s360-320-r4-triac.md) |

## Google Drive source evidence

The canonical Google Drive hardware folder for this board is
`PCB 2026 Sense360_r4 / PCB Project Files / Sense360 (Celling) / S360-320-R4`,
organized under per-type subfolders (`sch_pdf` / `bom` / `cpl` /
`gerbers` / `stepfile` / `Images` / `assets`).

| Drive item | Type | Notes |
|---|---|---|
| `S360-320-R4 / sch_pdf / S360-320-R4.pdf` | Schematic PDF | Module-side schematic. Byte-identical copy committed in-repo at [`schematics/S360-320-R4.pdf`](schematics/S360-320-R4.pdf). |
| `S360-320-R4 / bom` | BOM artifacts | Retained-but-not-committed per [`hardware-artifact-policy.md`](hardware-artifact-policy.md). |
| `S360-320-R4 / cpl` | Pick-and-place | Retained-but-not-committed. |
| `S360-320-R4 / gerbers` | Gerbers | Retained-but-not-committed. |
| `S360-320-R4 / stepfile` | 3D STEP | Retained-but-not-committed. |
| `S360-320-R4 / Images` | Renders / photos | Retained-but-not-committed. |
| `S360-320-R4 / assets` | Misc. | Retained-but-not-committed. |

## Evidence status

| Artifact class | Evidence available | Status |
|---|---|---|
| Module-side schematic PDF | [`schematics/S360-320-R4.pdf`](schematics/S360-320-R4.pdf) (committed) | schematic-backed |
| KiCad source | Not committed in-repo | TBD |
| Gerber / drill files | Drive `gerbers` (retained-but-not-committed) | TBD |
| 3D render / STEP | Drive `stepfile` (retained-but-not-committed) | TBD |
| Board photographs | Drive `Images` (retained-but-not-committed) | TBD |
| BOM | Drive `bom` (retained-but-not-committed) | TBD |
| Silkscreen / bench evidence | None committed | TBD |
| Mains-compliance evidence (COMPLIANCE-001) | Not recorded | TBD |

## Mating Core connector

| Element | Value |
|---|---|
| Core connector ref | `J15` |
| Core connector type | TBD (4-pin header; type not annotated on the visible Core sheet) |
| Pin count | 4 |
| Pin-1 orientation | TBD — needs silkscreen confirmation |
| Module-side connector ref | `J3` (`S360-320-R4`) |

## Module-side pinmap (`J3` ↔ Core `J15`)

The Core-side master table for `J15` is in
[`s360-100-core-connector-pin-map.md` § J15 — TRIAC module connector (4-pin)](s360-100-core-connector-pin-map.md#j15--triac-module-connector-4-pin).
The module-side capture is taken from
[`s360-320-r4-triac.md` § Schematic summary](s360-320-r4-triac.md#schematic-summary).

| Pin number | Module-side signal | Core net | ESP32 GPIO | Module-side signal type | Voltage / domain | Status |
|---|---|---|---|---|---|---|
| 1 | TRIAC module +3.3 V opto / sensor supply (Core side; module side opto-isolates to `Mains-domain` on the LOAD side) | `+3.3V` | N/A | power | `+3.3V` | needs silkscreen confirmation |
| 2 | TRIAC gate trigger — module-side label `ESP_GPIO1` drives `MOC3023M` LED via `R3` 220 Ω | `TRI_GPIO1` | TBD — see [Open questions](#open-questions--verification-needed) #1 | digital output | `Logic 3.3V (ESP32-S3)` (Core side); module side opto-isolates to `Mains-domain` | TBD |
| 3 | TRIAC zero-cross sense — module-side label `ESP_GPIO2` is fed from the `EL814` zero-cross optocoupler output | `TRI_GPIO2` | TBD — see [Open questions](#open-questions--verification-needed) #1 | digital input (interrupt-capable) | `Logic 3.3V (ESP32-S3)` (Core side); module side opto-isolates to `Mains-domain` | TBD |
| 4 | TRIAC module ground reference (Core side) | `GND` | N/A | ground | `GND` | needs silkscreen confirmation |

> **No `TachIO` / `Pul_Cou*` row on this connector.** TRIAC does
> not source or sink any tach / pulse-counter signal.

## Mains-side (`J1` AC LINE / `J2` LOAD) note

The AC LINE input `J1` (3-pin) and the LOAD output `J2` (2-pin)
on the TRIAC module switch mains. This document records the
**presence** of those connectors only. It does **not**:

- record `J1` 3-pin function (L / N / PE / doubled-line) — that
  is `not recorded` per
  [`s360-320-r4-triac.md` § Reconciliation flag classification](s360-320-r4-triac.md#reconciliation-flag-classification)
  and is COMPLIANCE-001-adjacent;
- record `J2` LOAD per-pin function or contact rating;
- make any mains-voltage / electrical-safety / compliance claim
  (tracked under COMPLIANCE-001 in
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md));
- characterise the `Q1 BT136S-600D` TRIAC, the `MOC3023M`
  optotriac driver, the `EL814` zero-cross optocoupler, the
  snubber `R2 100 Ω`, or any creepage / clearance value.

## FanTRIAC `HW-005` posture (explicit preservation)

`HW-005` stays **blocked**. The Release-One product YAML
[`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml)
carries placeholder `fan_triac_gate_pin: GPIO5` /
`fan_triac_zc_pin: GPIO6`, which on the `S360-100-R4` schematic
are `SEN0609_TX` / `out(gpio6)` (RoomIQ `J10` connector nets), not
TRIAC drive. The prior R4 snapshot routed `TRI_GPIO1` /
`TRI_GPIO2` via the SX1509 (`U3`) I/O expander, which the
ESPHome `ac_dimmer` driver **rejects** because it requires
interrupt-capable native ESP32 GPIOs for both `gate_pin` and
`zero_cross_pin`. This pinmap records the ESP32-side source as
**TBD** until evidence resolves it; no firmware YAML edit is
performed here; the `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` entry
in
[`config/product-catalog.json`](../../config/product-catalog.json)
stays `status: blocked`, `blocker: HW-005`,
`webflash_build_matrix: false`, no `artifact_name`.

## Open questions / verification needed

1. **`J15` `TRI_GPIO1` / `TRI_GPIO2` ESP32-side source pins.**
   The canonical R4 sheet does not unambiguously print a direct
   ESP32 route to `TRI_GPIO1` / `TRI_GPIO2`; the historical
   SX1509-routed path is **rejected** as a source for these
   pins; FanTRIAC `HW-005` stays blocked. See
   [`s360-100-r4-core.md` Open Questions #1 / #2](s360-100-r4-core.md#open-questions--verification-needed).
2. **`TRI_GPIO*` (Core) ↔ `ESP_GPIO*` (module) net-name
   divergence.** No canonical-naming choice is recorded here.
3. **AC LINE `J1` 3-pin function (L / N / PE).** Owed to
   silkscreen / PCB-source evidence; COMPLIANCE-001-adjacent.
4. **Silkscreen pin-1 orientation on Core `J15` and module `J3`.**
5. **Mains compliance.** All mains-related evidence is tracked
   under COMPLIANCE-001 and is out of scope for this pinmap.

## Cross references

- [`s360-100-core-connector-pin-map.md`](s360-100-core-connector-pin-map.md) — canonical Core-to-module connector pin map (S360-100-CONNECTOR-PINMAP-001).
- [`s360-100-r4-core.md`](s360-100-r4-core.md) — Core per-pin / per-net reference.
- [`s360-320-r4-triac.md`](s360-320-r4-triac.md) — TRIAC board-side audit (HW-PINMAP-320 / HW-005).
- [`schematics/S360-320-R4.pdf`](schematics/S360-320-R4.pdf) — committed module-side schematic PDF.
- [`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md) — COMPLIANCE-001 mains-voltage compliance tracker.
- [`docs/blocker-burndown.md`](../blocker-burndown.md) — blocker / scope-classification table (HW-005).

## Do-not-change guardrails

This document does **not**:

- promote `S360-320` `schematic_status` beyond `cataloged_unverified`;
- claim the FanTRIAC `HW-005` blocker is solved;
- promote any FanTRIAC-bearing product;
- add or change WebFlash builds in
  [`config/webflash-builds.json`](../../config/webflash-builds.json);
- claim release / WebFlash readiness for any FanTRIAC-bearing
  product;
- make any mains-voltage safety / compliance claim;
- fabricate connector type, pin order, or signal assignment;
- map any tach / pulse-counter signal through an expander.

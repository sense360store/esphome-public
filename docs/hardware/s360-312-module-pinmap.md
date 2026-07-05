# S360-312 Module-Side Pinmap (MODULE-PINMAPS-GDRIVE-001)

## Status

**Status: documentation-only schematic-backed module-side pinmap.
`S360-312` stays `cataloged_unverified`; FanDAC stays out of
release; no release / WebFlash readiness is implied.** Companion
to the canonical Core-side
[`s360-100-core-connector-pin-map.md`](s360-100-core-connector-pin-map.md)
(S360-100-CONNECTOR-PINMAP-001). This document records the
**module-side** view of the Sense360 DAC (`S360-312`) board and
reconciles every pin back to the mating Core connector `J7`.

It is **documentation only**. It does **not**:

- publish firmware, create release artifacts, or promote any
  release target;
- promote `S360-312` `schematic_status` in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  beyond its current `cataloged_unverified` value;
- promote `FanDAC` to release;
- claim WebFlash / release readiness for any FanDAC-bearing
  product;
- resolve the Core `J7` pin 1 `+5V` vs module `J1` pin 1 `+3.3V`
  rail-identity disagreement recorded under HW-PINMAP-312;
- resolve the I²C address-selection scheme on the two GP8403
  DACs;
- fabricate connector type, pin order, signal mapping, or ESP32
  GPIO allocation. Values not proven by the committed module-side
  schematic PDF or the canonical Core schematic carry **TBD** or
  **needs silkscreen confirmation**.

## Board identity

| Field | Value |
|---|---|
| Friendly name | Sense360 DAC |
| SKU | `S360-312` |
| Rev | R4 |
| Mating Core connector | `J7` (6-pin DAC module connector) on `S360-100-R4` |
| Module-side connector | `J1` (6-pin "From Core") on `S360-312-R4` |
| Module-side fan-output connectors | `J2`, `J3` — 3-pin each (Cloudlift-style outputs) |
| Module-side display connector | `J6` (4-pin "NEXTION DISPLAY") |
| Companion audit doc | [`s360-312-r4-dac.md`](s360-312-r4-dac.md) |

## Google Drive source evidence

The canonical Google Drive hardware folder for this board is
`PCB 2026 Sense360_r4 / PCB Project Files / Sense360 (Celling) / S360-312-R4`,
organized under per-type subfolders (`sch_pdf` / `bom` / `cpl` /
`gerbers` / `step_file` / `images` / `Assets`).

| Drive item | Type | Notes |
|---|---|---|
| `S360-312-R4 / sch_pdf / S360-312-R4.pdf` | Schematic PDF | Module-side schematic. Byte-identical copy committed in-repo at [`schematics/S360-312-R4.pdf`](schematics/S360-312-R4.pdf). |
| `S360-312-R4 / bom` | BOM artifacts | Retained-but-not-committed per [`hardware-artifact-policy.md` (archived)](../archive-index.md). |
| `S360-312-R4 / cpl` | Pick-and-place | Retained-but-not-committed. |
| `S360-312-R4 / gerbers` | Gerbers | Retained-but-not-committed. |
| `S360-312-R4 / step_file` | 3D STEP | Retained-but-not-committed. |
| `S360-312-R4 / images` | Renders / photos | Retained-but-not-committed. |
| `S360-312-R4 / Assets` | Misc. | Retained-but-not-committed. |

## Evidence status

| Artifact class | Evidence available | Status |
|---|---|---|
| Module-side schematic PDF | [`schematics/S360-312-R4.pdf`](schematics/S360-312-R4.pdf) (committed) | schematic-backed |
| KiCad source | Not committed in-repo | TBD |
| Gerber / drill files | Drive `gerbers` (retained-but-not-committed) | TBD |
| 3D render / STEP | Drive `step_file` (retained-but-not-committed) | TBD |
| Board photographs | Drive `images` (retained-but-not-committed) | TBD |
| BOM | Drive `bom` (retained-but-not-committed) | TBD |
| Silkscreen / bench evidence | None committed | TBD |

## Mating Core connector

| Element | Value |
|---|---|
| Core connector ref | `J7` |
| Core connector type | TBD (6-pin header; type not annotated on the visible Core sheet) |
| Pin count | 6 |
| Pin-1 orientation | TBD — needs silkscreen confirmation |
| Module-side connector ref | `J1` (`S360-312-R4`) |
| Pin-1 rail identity | **Unresolved discrepancy** (Core `J7` pin 1 = `+5V`; module `J1` pin 1 = `+3.3V`) — see [Open questions](#open-questions--verification-needed) #1 |

## Module-side pinmap (`J1` ↔ Core `J7`)

The Core-side master table for `J7` is in
[`s360-100-core-connector-pin-map.md` § J7 — DAC module connector (6-pin)](s360-100-core-connector-pin-map.md#j7--dac-module-connector-6-pin).
The module-side capture is taken from
[`s360-312-r4-dac.md` § Module-side `J1` ↔ Core-side `J7`](s360-312-r4-dac.md#module-side-j1--core-side-j7-6-pin-harness).

| Pin number | Module-side signal | Core net | ESP32 GPIO | Module-side signal type | Voltage / domain | Status |
|---|---|---|---|---|---|---|
| 1 | DAC module power input — module-side label `+3.3V` (Core `J7` pin 1 capture is `+5V`); routed to MT3608 boost converter `IN` pin | `+5V` (Core side) | N/A | power | TBD — `+5V` (Core side) vs `+3.3V` (module side label) | TBD |
| 2 | Shared I²C bus data — GP8403 DAC control bus (`IC1` / `IC2`) | `I2C_SDA` | `IO48` | I²C (open-drain) | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 3 | Shared I²C bus clock — same devices | `I2C_SCL` | `IO45` | I²C (open-drain) | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 4 | Module-side Nextion display UART receive (routed on-board from `J1` pin 4 to module `J6` UART pair) | `UART_RX` | `RXD0` (ESP32-S3 module pin 36) | UART | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 5 | Module-side Nextion display UART transmit (routed on-board from `J1` pin 5 to module `J6` UART pair) | `UART_TX` | `TXD0` (ESP32-S3 module pin 37) | UART | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 6 | DAC module ground reference | `GND` | N/A | ground | `GND` | needs silkscreen confirmation |

> **No `TachIO` / `Pul_Cou*` row on this connector.** FanDAC
> does not source or sink any tach / pulse-counter signal on this
> connector; the per-fan tach paths reside on the
> S360-311 FanPWM connector (`J6`) only.

## Cloudlift-style fan output connectors (`J2` / `J3`)

The module-side carries two GP8403-TC50-EW DACs (`IC1` / `IC2`)
driving two Cloudlift-style 3-pin fan-output connectors `J2` and
`J3`. Per-pin order on these load-side connectors is module-side
content and is recorded in
[`s360-312-r4-dac.md` § Schematic summary](s360-312-r4-dac.md#schematic-summary);
this pinmap does **not** restate or invent the per-pin assignments
on `J2` / `J3`. The fan-output current / voltage envelope, fan
compatibility, and analog-DAC firmware path are out of scope.

## Open questions / verification needed

1. **Core `J7` pin 1 `+5V` vs module `J1` pin 1 `+3.3V` rail
   identity.** The Core-side `J7` capture in
   [`s360-100-r4-core.md` § J7](s360-100-r4-core.md#j7--gp8403-fan-connector-6-pin)
   records `+5V` on Core `J7` pin 1; the committed module-side
   `S360-312-R4.pdf` labels the same pin position `+3.3V` and
   routes it to the MT3608 boost converter `IN` pin. Either the
   Core capture is wrong, or the module schematic mislabels the
   rail, or the silkscreen disagrees with both. Resolution
   belongs to a future HW-PINMAP-312-FOLLOWUP + silkscreen
   verification.
2. **Silkscreen pin-1 orientation on Core `J7` and module `J1`.**
3. **GP8403 I²C address selection.** Two DACs on a shared I²C bus
   need different addresses; the address-strap mechanism on
   `IC1` / `IC2` is **verify**.
4. **Cloudlift-style `J2` / `J3` connector identity, current
   rating, fan compatibility.** Owed to BOM / silkscreen
   evidence.
5. **DAC fan-driver firmware reconciliation.** The FanDAC
   firmware package
   [`packages/expansions/fan_dac.yaml`](../../packages/expansions/fan_dac.yaml)
   is not reconciled against this pinmap by this PR.

## Cross references

- [`s360-100-core-connector-pin-map.md`](s360-100-core-connector-pin-map.md) — canonical Core-to-module connector pin map (S360-100-CONNECTOR-PINMAP-001).
- [`s360-100-r4-core.md`](s360-100-r4-core.md) — Core per-pin / per-net reference.
- [`s360-312-r4-dac.md`](s360-312-r4-dac.md) — DAC board-side audit (HW-PINMAP-312).
- [`s360-312-r4-fandac.md`](s360-312-r4-fandac.md) — FanDAC product reference.
- [`schematics/S360-312-R4.pdf`](schematics/S360-312-R4.pdf) — committed module-side schematic PDF.
- [`docs/blocker-burndown.md` (archived)](../archive-index.md) — blocker / scope-classification table.

## Do-not-change guardrails

This document does **not**:

- promote `S360-312` `schematic_status` beyond `cataloged_unverified`;
- promote `FanDAC` to release;
- add or change WebFlash builds in
  [`config/webflash-builds.json`](../../config/webflash-builds.json);
- claim release / WebFlash readiness for any FanDAC-bearing
  product;
- claim measured DAC accuracy, fan-output current envelope, or
  thermal behaviour;
- fabricate connector type, pin order, or signal assignment;
- map any tach / pulse-counter signal through an expander.

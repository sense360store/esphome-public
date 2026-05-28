# S360-200 Module-Side Pinmap (MODULE-PINMAPS-GDRIVE-001)

## Status

**Status: documentation-only schematic-backed module-side pinmap.**
Companion to the canonical Core-side
[`s360-100-core-connector-pin-map.md`](s360-100-core-connector-pin-map.md)
(S360-100-CONNECTOR-PINMAP-001). This document records the
**module-side** view of the Sense360 RoomIQ (`S360-200`) board and
reconciles every pin back to the mating Core connector `J10`.

It is **documentation only**. It does **not**:

- publish firmware, create release artifacts, change
  [`firmware/sources.json`](../../firmware/sources.json), change
  [`manifest.json`](../../manifest.json), or promote any release
  target;
- claim WebFlash / release readiness for `S360-200` beyond the
  current Release-One posture (`Ceiling-POE-VentIQ-RoomIQ` stable);
- promote `S360-200` `schematic_status` in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  beyond its current value;
- resolve the Core `J10` vs RoomIQ `J6` pin-order discrepancy
  recorded as
  [`firmware-package-mapping-audit.md` Core J10 vs RoomIQ J6](firmware-package-mapping-audit.md#core-j10-vs-roomiq-j6-pin-order)
  and
  [`s360-200-r4-roomiq.md` Open Questions](s360-200-r4-roomiq.md#open-questions--verification-needed)
  #1;
- fabricate connector type, pin order, signal mapping, or ESP32
  GPIO allocation. Values not proven by the committed module-side
  schematic PDF or the canonical Core schematic carry **TBD** or
  **needs silkscreen confirmation**.

## Board identity

| Field | Value |
|---|---|
| Friendly name | Sense360 RoomIQ |
| SKU | `S360-200` |
| Rev | R4 |
| Mating Core connector | `J10` (12-pin "Presence/Comfort Module Connector") on `S360-100-R4` |
| Module-side connector | `J6` (12-pin) on `S360-200-R4` |
| Companion audit doc | [`s360-200-r4-roomiq.md`](s360-200-r4-roomiq.md) |

## Google Drive source evidence

The canonical Google Drive hardware folder for this board is
`PCB 2026 Sense360_r4 / PCB Project Files / Sense360 (Celling) / S360-200-R4`.
The module-side schematic PDF, BOM, CPL, gerbers, STEP, board
images, and assets are organized under per-type subfolders
(`sch_pdf` / `bom` / `cpl` / `gerbers` / `step_file` / `images` /
`assets`).

| Drive item | Type | Notes |
|---|---|---|
| `S360-200-R4 / sch_pdf / S360-200-R4.pdf` | Schematic PDF | Module-side schematic. Byte-identical copy committed in-repo at [`schematics/S360-200-R4.pdf`](schematics/S360-200-R4.pdf). |
| `S360-200-R4 / bom` | BOM artifacts | Retained-but-not-committed per [`hardware-artifact-policy.md`](hardware-artifact-policy.md). |
| `S360-200-R4 / cpl` | Pick-and-place | Retained-but-not-committed. |
| `S360-200-R4 / gerbers` | Gerbers | Retained-but-not-committed. |
| `S360-200-R4 / step_file` | 3D STEP | Retained-but-not-committed. |
| `S360-200-R4 / images` | Renders / photos | Retained-but-not-committed. |
| `S360-200-R4 / assets` | Misc. | Retained-but-not-committed. |

## Evidence status

| Artifact class | Evidence available | Status |
|---|---|---|
| Module-side schematic PDF | [`schematics/S360-200-R4.pdf`](schematics/S360-200-R4.pdf) (committed in-repo; mirrored in Drive `sch_pdf`) | schematic-backed |
| KiCad source | Not committed in-repo (Drive evidence per HW-007) | TBD |
| Gerber / drill files | Drive `gerbers` (retained-but-not-committed) | TBD |
| 3D render / STEP | Drive `step_file` (retained-but-not-committed) | TBD |
| Board photographs | Drive `images` (retained-but-not-committed) | TBD |
| BOM | Drive `bom` (retained-but-not-committed) | TBD |
| Silkscreen / bench evidence | None committed | TBD |

## Mating Core connector

| Element | Value |
|---|---|
| Core connector ref | `J10` |
| Core connector type | TBD (12-pin header; type not annotated on the visible Core sheet) |
| Pin count | 12 |
| Pin-1 orientation | TBD — needs silkscreen confirmation |
| Module-side connector ref | `J6` (`S360-200-R4`) |
| Module-side pin order | Module-side schematic prints pin 1 = `+5V`, pin 7 = `+3.3V`, pin 12 = `GND` per [`s360-200-r4-roomiq.md` § Module connector](s360-200-r4-roomiq.md#module-connector) |
| Pin-order reconciliation | **Disagreement with Core `J10` capture** — see [Open questions](#open-questions--verification-needed) #1 |

## Module-side pinmap (`J6` ↔ Core `J10`)

The table below is the **module-side** view. The Core-side master
table for `J10` is in
[`s360-100-core-connector-pin-map.md` § J10 — RoomIQ module connector (12-pin)](s360-100-core-connector-pin-map.md#j10--roomiq-module-connector-12-pin).
The Core-side capture follows the Core schematic; the module-side
capture below follows the
[`S360-200-R4.pdf`](schematics/S360-200-R4.pdf) sheet.

| Pin number | Module-side signal | Core net | ESP32 GPIO | Module-side signal type | Voltage / domain | Status |
|---|---|---|---|---|---|---|
| 1 | RoomIQ `+5V` rail (feeds `J2` Hi-Link LD2450, `J3` DFRobot SEN0609 radar) | `+5V` (Core `J10` pin 2 per Core capture) | N/A | power | `+5V` | needs silkscreen confirmation |
| 2 | SEN0609 / C4001 radar UART (module-side label `SEN0609_RX`) | `SEN0609_RX` | `IO4` | UART | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 3 | SEN0609 / C4001 radar UART (module-side label `SEN0609_TX`) | `SEN0609_TX` | `IO5` | UART | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 4 | Auxiliary radar I/O (module-side label `out(gpio6)`) | `out(gpio6)` | `IO6` | digital output | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 5 | Hi-Link LD2450 radar UART (module-side label `Hi-Link_RX`) | `Hi-Link_RX` | `IO1` | UART | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 6 | Hi-Link LD2450 radar UART (module-side label `Hi-Link_TX`) | `Hi-Link_TX` | `IO2` | UART | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 7 | RoomIQ `+3.3V` rail (feeds `U1` LTR-303ALS-01, `U2` SHT4x, `U3` EKMC1601111, `U4` BMP581) | `+3.3V` (Core `J10` pin 1 per Core capture) | N/A | power | `+3.3V` | needs silkscreen confirmation |
| 8 | `PIR` (`U3` EKMC1601111 motion output) | `PIR` | `IO15` | digital input (polled) | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 9 | `ALS_INT` (`U1` LTR-303ALS-01 INT) | `ALS_INT` | `IO47` | digital input (interrupt-capable) | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 10 | Shared I²C data (`U1` / `U2` / `U4`) | `I2C_SDA` | `IO48` | I²C (open-drain) | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 11 | Shared I²C clock (`U1` / `U2` / `U4`) | `I2C_SCL` | `IO45` | I²C (open-drain) | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 12 | RoomIQ ground reference | `GND` | N/A | ground | `GND` | needs silkscreen confirmation |

> **No `TachIO` / `Pul_Cou*` row on this connector.** RoomIQ does
> not source or sink any tach / pulse-counter signal; the
> architectural rule recorded in
> [`s360-100-native-tach-pulse-strategy.md`](s360-100-native-tach-pulse-strategy.md)
> and restated in
> [`s360-100-core-connector-pin-map.md` § Native ESP32-S3 GPIO requirements](s360-100-core-connector-pin-map.md#native-esp32-s3-gpio-requirements-architectural-rule)
> is preserved by exclusion.

## Open questions / verification needed

1. **Core `J10` vs RoomIQ `J6` pin-order reconciliation.** The
   module-side schematic prints `+5V` at `J6` pin 1 and `+3.3V` at
   pin 7; the Core-side capture in
   [`s360-100-core-connector-pin-map.md` § J10](s360-100-core-connector-pin-map.md#j10--roomiq-module-connector-12-pin)
   prints `+3.3V` at pin 1 and `+5V` at pin 2. Both connectors are
   nominally a mating pair, so one of the two tables disagrees with
   the silkscreen. The reconciliation is owed to
   [`firmware-package-mapping-audit.md` Core J10 vs RoomIQ J6](firmware-package-mapping-audit.md#core-j10-vs-roomiq-j6-pin-order)
   and to
   [`s360-100-r4-core.md` § S360-100-BENCH-001 status](s360-100-r4-core.md#s360-100-bench-001-status);
   it is **not** resolved by this PR.
2. **1-to-12 silkscreen pin order on both sides.** Per
   [`s360-100-r4-core.md` Open Question #9](s360-100-r4-core.md#open-questions--verification-needed).
3. **Connector type / part number for `J6` and Core `J10`.** The
   [`s360-200-r4-roomiq.md` Audit log](s360-200-r4-roomiq.md#audit-log)
   records a `SM12B-SRSS-TB` JST SH 12-pin identity from a
   retained-but-not-committed BOM; the Core-side connector
   identity is unrecorded. Both sides need silkscreen / BOM
   confirmation.
4. **Radar UART direction (`RX` / `TX` naming).** Whether the
   `SEN0609_RX` / `SEN0609_TX` / `Hi-Link_RX` / `Hi-Link_TX`
   labels are from the Core's perspective or the radar module's
   perspective is **verify**.

## Cross references

- [`s360-100-core-connector-pin-map.md`](s360-100-core-connector-pin-map.md) — canonical Core-to-module connector pin map (S360-100-CONNECTOR-PINMAP-001).
- [`s360-100-r4-core.md`](s360-100-r4-core.md) — Core per-pin / per-net reference.
- [`s360-200-r4-roomiq.md`](s360-200-r4-roomiq.md) — RoomIQ board-side hardware reference (companion audit doc).
- [`schematics/S360-200-R4.pdf`](schematics/S360-200-R4.pdf) — committed module-side schematic PDF.
- [`docs/sense360-room-bundles.md`](../sense360-room-bundles.md) — PoE room bundle SKU matrix.
- [`docs/blocker-burndown.md`](../blocker-burndown.md) — blocker / scope-classification table.

## Do-not-change guardrails

This document does **not**:

- promote `S360-200` beyond its current state in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json);
- promote any RoomIQ-bearing product;
- add or change WebFlash builds in
  [`config/webflash-builds.json`](../../config/webflash-builds.json);
- claim measured RPM / tach / fan capability (RoomIQ does not host
  a fan-driver path);
- claim release / WebFlash readiness;
- fabricate connector type, pin order, or signal assignment;
- map any tach / pulse-counter signal through an expander.

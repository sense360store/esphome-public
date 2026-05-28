# S360-210 Module-Side Pinmap (MODULE-PINMAPS-GDRIVE-001)

## Status

**Status: documentation-only schematic-backed module-side pinmap.**
Companion to the canonical Core-side
[`s360-100-core-connector-pin-map.md`](s360-100-core-connector-pin-map.md)
(S360-100-CONNECTOR-PINMAP-001). This document records the
**module-side** view of the Sense360 AirIQ (`S360-210`) board and
reconciles every pin back to the mating Core connector `J9`.

It is **documentation only**. It does **not**:

- publish firmware, create release artifacts, or promote any
  release target;
- claim WebFlash / release readiness for `S360-210` beyond the
  current Release-One posture;
- promote `S360-210` `schematic_status` in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  beyond its current value;
- resolve the `AirQ_Led` / `AirQ_Status_Led` AirIQ-vs-VentIQ reuse
  question (HW-002 OQ#4);
- fabricate connector type, pin order, signal mapping, or ESP32
  GPIO allocation. Values not proven by the committed module-side
  schematic PDF or the canonical Core schematic carry **TBD** or
  **needs silkscreen confirmation**.

## Board identity

| Field | Value |
|---|---|
| Friendly name | Sense360 AirIQ |
| SKU | `S360-210` |
| Rev | R4 |
| Mating Core connector | `J9` (7-pin "AirIQ Module Connector") on `S360-100-R4` |
| Module-side connector | 7-pin "From Core" header on `S360-210-R4` (silkscreen ref TBD) |
| Companion audit doc | [`s360-210-r4-airiq.md`](s360-210-r4-airiq.md) |

## Google Drive source evidence

The canonical Google Drive hardware folder for this board is
`PCB 2026 Sense360_r4 / PCB Project Files / Sense360 (Celling) / S360-210-R4`,
organized under per-type subfolders (`sch_pdf` / `bom` / `cpl` /
`gerbers` / `step_file` / `images` / `Assets`).

| Drive item | Type | Notes |
|---|---|---|
| `S360-210-R4 / sch_pdf / S360-210-R4.pdf` | Schematic PDF | Module-side schematic. Byte-identical copy committed in-repo at [`schematics/S360-210-R4.pdf`](schematics/S360-210-R4.pdf). |
| `S360-210-R4 / images / S360-210-R4.png` (and `_3.png` / `_5.png` / `_6.png`) | Renders / photos | Retained-but-not-committed. |
| `S360-210-R4 / bom` | BOM artifacts | Retained-but-not-committed. |
| `S360-210-R4 / cpl` | Pick-and-place | Retained-but-not-committed. |
| `S360-210-R4 / gerbers` | Gerbers | Retained-but-not-committed. |
| `S360-210-R4 / step_file` | 3D STEP | Retained-but-not-committed. |
| `S360-210-R4 / Assets` | Misc. | Retained-but-not-committed. |

## Evidence status

| Artifact class | Evidence available | Status |
|---|---|---|
| Module-side schematic PDF | [`schematics/S360-210-R4.pdf`](schematics/S360-210-R4.pdf) (committed) | schematic-backed |
| KiCad source | Not committed in-repo | TBD |
| Gerber / drill files | Drive `gerbers` (retained-but-not-committed) | TBD |
| 3D render / STEP | Drive `step_file` (retained-but-not-committed) | TBD |
| Board photographs | Drive `images` (retained-but-not-committed) | partial |
| BOM | Drive `bom` (retained-but-not-committed) | TBD |
| Silkscreen / bench evidence | None committed | TBD |

## Mating Core connector

| Element | Value |
|---|---|
| Core connector ref | `J9` |
| Core connector type | TBD (7-pin header; type not annotated on the visible Core sheet) |
| Pin count | 7 |
| Pin-1 orientation | TBD — needs silkscreen confirmation |
| Mutually-exclusive sibling | `S360-211` Sense360 VentIQ — see [Open questions](#open-questions--verification-needed) #1 |

## Module-side pinmap (`J9` mate, 7-pin)

The Core-side master table for `J9` is in
[`s360-100-core-connector-pin-map.md` § J9 — AirIQ module connector (7-pin)](s360-100-core-connector-pin-map.md#j9--airiq-module-connector-7-pin).
The pin order below follows the Core `J9` capture verbatim
because the module-side silkscreen ref + 1-to-7 order is not
unambiguously printed on the committed module-side PDF (see
[`s360-210-r4-airiq.md` Open Questions](s360-210-r4-airiq.md#open-questions--verification-needed)
#1).

| Pin number | Module-side signal | Core net | ESP32 GPIO | Module-side signal type | Voltage / domain | Status |
|---|---|---|---|---|---|---|
| 1 | AirIQ `+5V` rail (powers SPS30 and other +5 V loads — PM, HCHO, MICS heater on the AirIQ board) | `+5V` | N/A | power | `+5V` | needs silkscreen confirmation |
| 2 | AirIQ `+3.3V` rail (powers SGP41, SCD41, sensor logic) | `+3.3V` | N/A | power | `+3.3V` | needs silkscreen confirmation |
| 3 | Shared I²C bus data (SCD41 / SGP41 / BMP390 / SFA40 stack on the AirIQ board) | `I2C_SDA` | `IO48` | I²C (open-drain) | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 4 | Shared I²C bus clock (same devices) | `I2C_SCL` | `IO45` | I²C (open-drain) | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 5 | AirIQ status-LED line (legacy `AirQ_Status_Led` net; consumed by AirIQ board indicator — `verify`) | `AirQ_Status_Led` | `IO7` | digital output | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 6 | AirIQ LED control line (legacy `AirQ_Led` net; consumed by AirIQ board indicator — `verify`) | `AirQ_Led` | `IO8` | digital output | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 7 | AirIQ ground reference | `GND` | N/A | ground | `GND` | needs silkscreen confirmation |

> **No `TachIO` / `Pul_Cou*` row on this connector.** AirIQ does
> not source or sink any tach / pulse-counter signal.

## Open questions / verification needed

1. **Connector mating exclusion with `S360-211` VentIQ.** AirIQ
   and VentIQ share the `J9` 7-pin slot (mutually exclusive). The
   architecture doc places VentIQ on the 5-pin `J1` connector;
   the VentIQ board-side audit records VentIQ plugging into the
   Core 7-pin `J9` "AirIQ Module Connector". See
   [`s360-100-core-connector-pin-map.md` Open Questions](s360-100-core-connector-pin-map.md#open-questions--verification-needed)
   #1.
2. **AirIQ side of the `J9` connector — 1-to-7 pin order.** The
   Core `J9` table is committed; the AirIQ-side mating pin order
   is **verify** against the AirIQ silkscreen.
3. **`AirQ_Led` / `AirQ_Status_Led` reuse on AirIQ.** Whether
   these nets drive AirIQ-side indicators and how VentIQ reuses
   the same physical lines is **verify** (HW-002 OQ#4).
4. **SPS30 connector interface (UART vs I²C).** The SPS30 supports
   both; which interface the connector is wired for is **verify**
   against the silkscreen.
5. **SFA40 connector interface and address.** **Verify** against
   the SFA40 module spec.

## Cross references

- [`s360-100-core-connector-pin-map.md`](s360-100-core-connector-pin-map.md) — canonical Core-to-module connector pin map (S360-100-CONNECTOR-PINMAP-001).
- [`s360-100-r4-core.md`](s360-100-r4-core.md) — Core per-pin / per-net reference.
- [`s360-210-r4-airiq.md`](s360-210-r4-airiq.md) — AirIQ board-side hardware reference (companion audit doc).
- [`s360-211-module-pinmap.md`](s360-211-module-pinmap.md) — VentIQ module-side pinmap (mutually-exclusive sibling on the same Core connector).
- [`schematics/S360-210-R4.pdf`](schematics/S360-210-R4.pdf) — committed module-side schematic PDF.
- [`docs/sense360-room-bundles.md`](../sense360-room-bundles.md) — PoE room bundle SKU matrix.

## Do-not-change guardrails

This document does **not**:

- promote `S360-210` beyond its current state in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json);
- promote any AirIQ-bearing product;
- add or change WebFlash builds in
  [`config/webflash-builds.json`](../../config/webflash-builds.json);
- claim release / WebFlash readiness;
- fabricate connector type, pin order, or signal assignment;
- map any tach / pulse-counter signal through an expander.

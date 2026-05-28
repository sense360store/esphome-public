# S360-300 Module-Side Pinmap (MODULE-PINMAPS-GDRIVE-001)

## Status

**Status: documentation-only schematic-backed module-side pinmap.
LED stays `preview`.** Companion to the canonical Core-side
[`s360-100-core-connector-pin-map.md`](s360-100-core-connector-pin-map.md)
(S360-100-CONNECTOR-PINMAP-001). This document records the
**module-side** view of the Sense360 LED (`S360-300`) board and
reconciles every pin back to the mating Core connector `J3`.

It is **documentation only**. It does **not**:

- publish firmware, create release artifacts, or promote any
  release target;
- promote Sense360 LED from `preview` to `stable`;
  `Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`,
  `channel: preview`;
- promote `S360-300` `schematic_status` in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  beyond its current value;
- resolve the Core `J3` pin 2 rail-identity (`+5V` vs `+3.3V`)
  Open Question recorded in
  [`s360-300-r4-led.md` Open Questions](s360-300-r4-led.md#open-questions--verification-needed)
  #1;
- fabricate connector type, pin order, signal mapping, or ESP32
  GPIO allocation. Values not proven by the committed module-side
  schematic PDF or the canonical Core schematic carry **TBD** or
  **needs silkscreen confirmation**.

## Board identity

| Field | Value |
|---|---|
| Friendly name | Sense360 LED |
| SKU | `S360-300` |
| Rev | R4 |
| Mating Core connector | `J3` (3-pin LED ring connector) on `S360-100-R4` |
| Module-side connector | `J1` (3-pin) on `S360-300-R4` |
| Companion audit doc | [`s360-300-r4-led.md`](s360-300-r4-led.md) |

## Google Drive source evidence

The canonical Google Drive hardware folder for this board is
`PCB 2026 Sense360_r4 / PCB Project Files / Sense360 (Celling) / S360-300-R4`,
organized under per-type subfolders (`sch_pdf` / `bom` / `cpl` /
`gerbers` / `step_file` / `images` / `assets`).

| Drive item | Type | Notes |
|---|---|---|
| `S360-300-R4 / sch_pdf / S360-300-R4.pdf` | Schematic PDF | Module-side schematic. Byte-identical copy committed in-repo at [`schematics/S360-300-R4.pdf`](schematics/S360-300-R4.pdf). |
| `S360-300-R4 / bom` | BOM artifacts | Retained-but-not-committed. |
| `S360-300-R4 / cpl` | Pick-and-place | Retained-but-not-committed. |
| `S360-300-R4 / gerbers` | Gerbers | Retained-but-not-committed. |
| `S360-300-R4 / step_file` | 3D STEP | Retained-but-not-committed. |
| `S360-300-R4 / images` | Renders / photos | Retained-but-not-committed. |
| `S360-300-R4 / assets` | Misc. | Retained-but-not-committed. |

## Evidence status

| Artifact class | Evidence available | Status |
|---|---|---|
| Module-side schematic PDF | [`schematics/S360-300-R4.pdf`](schematics/S360-300-R4.pdf) (committed) | schematic-backed |
| KiCad source | Not committed in-repo | TBD |
| Gerber / drill files | Drive `gerbers` (retained-but-not-committed) | TBD |
| 3D render / STEP | Drive `step_file` (retained-but-not-committed) | TBD |
| Board photographs | Drive `images` (retained-but-not-committed) | TBD |
| BOM | Drive `bom` (retained-but-not-committed) | TBD |
| Silkscreen / bench evidence | None committed (`S360-300-BENCH-001` per [`s360-300-r4-led.md`](s360-300-r4-led.md) — `pending — bench hardware evidence required`) | TBD |

## Mating Core connector

| Element | Value |
|---|---|
| Core connector ref | `J3` |
| Core connector type | TBD (3-pin header; type not annotated on the visible Core sheet) |
| Pin count | 3 |
| Pin-1 orientation | TBD — needs silkscreen confirmation |
| Module-side connector ref | `J1` (`S360-300-R4`) |

## Module-side pinmap (`J1` ↔ Core `J3`)

The Core-side master table for `J3` is in
[`s360-100-core-connector-pin-map.md` § J3 — LED ring connector (3-pin)](s360-100-core-connector-pin-map.md#j3--led-ring-connector-3-pin).
The module-side capture follows
[`s360-300-r4-led.md` § Connector `J1`](s360-300-r4-led.md#connector-j1--module-connector-3-pin).

| Pin number | Module-side signal | Core net | ESP32 GPIO | Module-side signal type | Voltage / domain | Status |
|---|---|---|---|---|---|---|
| 1 | LED ground reference | `GND` | N/A | ground | `GND` | needs silkscreen confirmation |
| 2 | LED power rail — module-side label `+5V` (Core `J3` pin 1 capture is `+3.3V`; rail-identity reconciliation owed) | `+3.3V` (Core side) | N/A | power | TBD — `+5V` (module side label) vs `+3.3V` (Core side capture) | TBD |
| 3 | WS2812B serial data input on the LED chain | `LED_DATA_3V3` | `IO38` (source `LED_DATA` → `U2A` `74LVC1G07SE-7` open-drain buffer → `R8` 330 Ω → Core `J3` pin 3) | digital output | `Logic 3.3V (ESP32-S3)` | schematic-backed |

> **Rail-identity Open Question.** The Core schematic prints
> `+3.3V` on Core `J3` pin 1; the module-side LED `J1` schematic
> labels the same pin position `+5V`. Whichever rail is actually
> on the physical harness, the LED ring is a WS2812B chain that
> can run from either supply. The reconciliation is owed under
> [`s360-300-r4-led.md` Open Question #1](s360-300-r4-led.md#open-questions--verification-needed)
> and `S360-300-BENCH-001`; it is **not** resolved by this PR.

> **No `TachIO` / `Pul_Cou*` row on this connector.** LED does
> not source or sink any tach / pulse-counter signal.

## Open questions / verification needed

1. **`J1` pin 2 rail identity (`+5V` vs `+3.3V`).** The Core `J3`
   table records the rail as `+3.3V`; the LED module-side `J1`
   schematic labels the same pin position `+5V`. Confirm against
   the silkscreen on both boards.
2. **`J1` exact 1-to-3 pin order on the LED board.** **Verify**
   against the LED board silkscreen.
3. **Harness between Core `J3` and LED `J1`.** Direct mate vs
   short cable — **verify**.
4. **WS2812B chain length and arrangement.** Out of scope for
   this pinmap; the LED-driver firmware path is documented under
   [`s360-300-r4-led.md`](s360-300-r4-led.md).

## Preview posture

`S360-300` (Sense360 LED) ships under the LED preview entry
`Ceiling-POE-VentIQ-RoomIQ-LED` (`status: preview`,
`channel: preview`). This pinmap is part of the LED preview
documentation surface and does **not** add WebFlash / release
readiness to the LED slot. LED stable promotion is owned by
`LED-STABLE-PROMOTION-001` per
[`docs/preview-to-stable-promotion-gates.md`](../preview-to-stable-promotion-gates.md).

## Cross references

- [`s360-100-core-connector-pin-map.md`](s360-100-core-connector-pin-map.md) — canonical Core-to-module connector pin map (S360-100-CONNECTOR-PINMAP-001).
- [`s360-100-r4-core.md`](s360-100-r4-core.md) — Core per-pin / per-net reference.
- [`s360-300-r4-led.md`](s360-300-r4-led.md) — LED board-side hardware reference (companion audit doc).
- [`schematics/S360-300-R4.pdf`](schematics/S360-300-R4.pdf) — committed module-side schematic PDF.
- [`docs/preview-to-stable-promotion-gates.md`](../preview-to-stable-promotion-gates.md) — LED preview-to-stable promotion gates.
- [`docs/sense360-room-bundles.md`](../sense360-room-bundles.md) — PoE room bundle SKU matrix.

## Do-not-change guardrails

This document does **not**:

- promote `S360-300` `schematic_status` beyond its current state in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json);
- promote Sense360 LED from `preview` to `stable`;
- add or change WebFlash builds in
  [`config/webflash-builds.json`](../../config/webflash-builds.json);
- claim release / WebFlash readiness beyond preview;
- fabricate connector type, pin order, or signal assignment;
- map any tach / pulse-counter signal through an expander.

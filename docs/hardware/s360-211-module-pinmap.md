# S360-211 Module-Side Pinmap (MODULE-PINMAPS-GDRIVE-001)

## Status

**Status: documentation-only schematic-backed module-side pinmap.**
Companion to the canonical Core-side
[`s360-100-core-connector-pin-map.md`](s360-100-core-connector-pin-map.md)
(S360-100-CONNECTOR-PINMAP-001). This document records the
**module-side** view of the Sense360 VentIQ (`S360-211`) board and
reconciles every pin back to the Core mating connector — currently
recorded with a **cross-doc disagreement** (Core architecture =
`J1` 5-pin; VentIQ audit = Core `J9` 7-pin "AirIQ Module
Connector"). Both candidate mappings are recorded below as
candidate tables.

It is **documentation only**. It does **not**:

- publish firmware, create release artifacts, or promote any
  release target;
- claim WebFlash / release readiness for `S360-211` beyond the
  current Release-One posture (`Ceiling-POE-VentIQ-RoomIQ` stable);
- promote `S360-211` `schematic_status` in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  beyond its current value;
- make any mains-voltage / compliance claim about the VentIQ
  on-board fan-relay drive circuit (tracked under COMPLIANCE-001);
- resolve the `J1` vs `J9` connector identity disagreement;
- fabricate connector type, pin order, signal mapping, or ESP32
  GPIO allocation. Values not proven by the committed module-side
  schematic PDF or the canonical Core schematic carry **TBD** or
  **needs silkscreen confirmation**.

## Board identity

| Field | Value |
|---|---|
| Friendly name | Sense360 VentIQ |
| SKU | `S360-211` |
| Rev | R4 |
| Mating Core connector (Core architecture doc) | `J1` (5-pin) on `S360-100-R4` |
| Mating Core connector (VentIQ audit doc) | `J9` (7-pin "AirIQ Module Connector") on `S360-100-R4` |
| Module-side connector | TBD silkscreen ref on `S360-211-R4` |
| Companion audit doc | [`s360-211-r4-ventiq.md`](s360-211-r4-ventiq.md) |

## Google Drive source evidence

The canonical Google Drive hardware folder for this board is
`PCB 2026 Sense360_r4 / PCB Project Files / Sense360 (Celling) / S360-211-R4`,
organized under per-type subfolders (`sch_pdf` / `bom` / `cpl` /
`gerbers` / `step_file` / `images` / `assets`).

| Drive item | Type | Notes |
|---|---|---|
| `S360-211-R4 / sch_pdf / S360-211-R4.pdf` | Schematic PDF | Module-side schematic. Byte-identical copy committed in-repo at [`schematics/S360-211-R4.pdf`](schematics/S360-211-R4.pdf). |
| `S360-211-R4 / bom` | BOM artifacts | Retained-but-not-committed. |
| `S360-211-R4 / cpl` | Pick-and-place | Retained-but-not-committed. |
| `S360-211-R4 / gerbers` | Gerbers | Retained-but-not-committed. |
| `S360-211-R4 / step_file` | 3D STEP | Retained-but-not-committed. |
| `S360-211-R4 / images` | Renders / photos | Retained-but-not-committed. |
| `S360-211-R4 / assets` | Misc. | Retained-but-not-committed. |

## Evidence status

| Artifact class | Evidence available | Status |
|---|---|---|
| Module-side schematic PDF | [`schematics/S360-211-R4.pdf`](schematics/S360-211-R4.pdf) (committed) | schematic-backed |
| KiCad source | Not committed in-repo | TBD |
| Gerber / drill files | Drive `gerbers` (retained-but-not-committed) | TBD |
| 3D render / STEP | Drive `step_file` (retained-but-not-committed) | TBD |
| Board photographs | Drive `images` (retained-but-not-committed) | TBD |
| BOM | Drive `bom` (retained-but-not-committed) | TBD |
| Silkscreen / bench evidence | None committed | TBD |

## Candidate module-side pinmap A — Core `J1` (5-pin, architecture doc)

The Core-side master table for `J1` is in
[`s360-100-core-connector-pin-map.md` § J1 — VentIQ module connector (5-pin)](s360-100-core-connector-pin-map.md#j1--ventiq-module-connector-5-pin).

| Pin number | Module-side signal | Core net | ESP32 GPIO | Module-side signal type | Voltage / domain | Status |
|---|---|---|---|---|---|---|
| 1 | VentIQ +5 V rail (SPS30 PM, fan-relay coil supply path — `verify`) | `+5V` | N/A | power | `+5V` | needs silkscreen confirmation |
| 2 | VentIQ +3.3 V rail (SGP41 / sensor logic) | `+3.3V` | N/A | power | `+3.3V` | needs silkscreen confirmation |
| 3 | Shared I²C bus clock — SGP41 / off-board IR temperature (if I²C) | `I2C_SCL` | `IO45` | I²C (open-drain) | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 4 | Shared I²C bus data — same devices | `I2C_SDA` | `IO48` | I²C (open-drain) | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 5 | VentIQ ground reference | `GND` | N/A | ground | `GND` | needs silkscreen confirmation |

## Candidate module-side pinmap B — Core `J9` (7-pin, VentIQ audit doc)

The Core-side master table for `J9` is in
[`s360-100-core-connector-pin-map.md` § J9 — AirIQ module connector (7-pin)](s360-100-core-connector-pin-map.md#j9--airiq-module-connector-7-pin).
This is the candidate recorded in
[`s360-211-r4-ventiq.md` § Module connector mating](s360-211-r4-ventiq.md#module-connector-mating).

| Pin number | Module-side signal | Core net | ESP32 GPIO | Module-side signal type | Voltage / domain | Status |
|---|---|---|---|---|---|---|
| 1 | VentIQ +5 V rail (SPS30 PM, fan-relay coil supply path — `verify`) | `+5V` | N/A | power | `+5V` | needs silkscreen confirmation |
| 2 | VentIQ +3.3 V rail (SGP41 / sensor logic) | `+3.3V` | N/A | power | `+3.3V` | needs silkscreen confirmation |
| 3 | Shared I²C bus data — SGP41 / off-board IR temperature (if I²C) | `I2C_SDA` | `IO48` | I²C (open-drain) | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 4 | Shared I²C bus clock — same devices | `I2C_SCL` | `IO45` | I²C (open-drain) | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 5 | Legacy `AirQ_Status_Led` net — VentIQ reuse is `verify` (HW-002 OQ#4) | `AirQ_Status_Led` | `IO7` | digital output | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 6 | Legacy `AirQ_Led` net — VentIQ reuse is `verify` (HW-002 OQ#4) | `AirQ_Led` | `IO8` | digital output | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 7 | VentIQ ground reference | `GND` | N/A | ground | `GND` | needs silkscreen confirmation |

> **Both candidates are preserved; neither is promoted to canonical
> by this PR.** Silkscreen / harness evidence is owed under
> [`s360-100-r4-core.md` § S360-100-BENCH-001 status](s360-100-r4-core.md#s360-100-bench-001-status).

## Mains / fan-relay drive (module side only)

VentIQ carries on-board relay-drive circuitry intended to switch a
bathroom extractor fan. This document records the **presence** of
that circuit only; it does **not**:

- record contact rating, snubber, isolation barrier, creepage or
  clearance values;
- make any mains-voltage / electrical-safety / compliance claim
  (tracked under COMPLIANCE-001 in
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md));
- determine which Core net / ESP32 GPIO drives the on-board
  relay coil (the Release-One config string
  `Ceiling-POE-VentIQ-RoomIQ` does not include a fan-driver
  token; the relay-drive source remains `verify`).

The mains-side LOAD terminal pin numbering, fusing, and earth-
bonding are **not** recorded here.

## Open questions / verification needed

1. **`J1` vs `J9` reconciliation for VentIQ.** The Core
   architecture doc places VentIQ on the 5-pin `J1` connector;
   the VentIQ board-side audit records VentIQ plugging into the
   Core 7-pin `J9` "AirIQ Module Connector". Bench / silkscreen
   evidence is required to determine which connector the
   Release-One VentIQ harness actually mates with on the physical
   Core board. See
   [`s360-100-core-connector-pin-map.md` Open Questions](s360-100-core-connector-pin-map.md#open-questions--verification-needed)
   #1.
2. **VentIQ-side connector silkscreen reference and 1-to-N pin
   order.** Both 5-pin and 7-pin candidates carry `needs
   silkscreen confirmation`.
3. **`AirQ_Led` / `AirQ_Status_Led` reuse on VentIQ.** Whether
   these nets drive a VentIQ-side indicator at all is **verify**
   (HW-002 OQ#4).
4. **Fan-relay drive-signal source.** Which Core net / ESP32
   GPIO drives the on-board relay coil is **verify**.
5. **SPS30 / IR temperature interface.** Per the
   [`s360-211-r4-ventiq.md` Open Questions](s360-211-r4-ventiq.md#open-questions--verification-needed).
6. **Mains-side topology and compliance.** All mains-related
   evidence is tracked under COMPLIANCE-001 and is out of scope
   for this pinmap.

## Cross references

- [`s360-100-core-connector-pin-map.md`](s360-100-core-connector-pin-map.md) — canonical Core-to-module connector pin map (S360-100-CONNECTOR-PINMAP-001).
- [`s360-100-r4-core.md`](s360-100-r4-core.md) — Core per-pin / per-net reference.
- [`s360-211-r4-ventiq.md`](s360-211-r4-ventiq.md) — VentIQ board-side hardware reference (companion audit doc).
- [`s360-210-module-pinmap.md`](s360-210-module-pinmap.md) — AirIQ module-side pinmap (mutually-exclusive sibling on the same Core `J9` connector under candidate B).
- [`schematics/S360-211-R4.pdf`](schematics/S360-211-R4.pdf) — committed module-side schematic PDF.
- [`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md) — COMPLIANCE-001 mains-voltage compliance tracker.
- [`docs/sense360-room-bundles.md`](../sense360-room-bundles.md) — PoE room bundle SKU matrix.

## Do-not-change guardrails

This document does **not**:

- promote `S360-211` beyond its current state in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json);
- promote any VentIQ-bearing product beyond Release-One;
- add or change WebFlash builds in
  [`config/webflash-builds.json`](../../config/webflash-builds.json);
- claim release / WebFlash readiness beyond the existing
  Release-One posture;
- make any mains-voltage safety / compliance claim;
- fabricate connector type, pin order, or signal assignment;
- map any tach / pulse-counter signal through an expander.

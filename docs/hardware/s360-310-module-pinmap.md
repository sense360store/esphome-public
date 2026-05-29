# S360-310 Module-Side Pinmap (MODULE-PINMAPS-GDRIVE-001)

## Status

**Status: documentation-only schematic-backed module-side pinmap.
`S360-310` stays `cataloged_unverified`; FanRelay stays out of
release.** Companion to the canonical Core-side
[`s360-100-core-connector-pin-map.md`](s360-100-core-connector-pin-map.md)
(S360-100-CONNECTOR-PINMAP-001). This document records the
**module-side** view of the Sense360 Relay (`S360-310`) board and
reconciles every pin back to the mating Core connector `J4`.

It is **documentation only**. It does **not**:

- publish firmware, create release artifacts, or promote any
  release target;
- promote `S360-310` `schematic_status` in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  beyond its current `cataloged_unverified` value;
- mark `S360-310` `verified`;
- promote `FanRelay` to release;
- claim WebFlash / release readiness for any FanRelay-bearing
  product;
- make any mains-voltage / electrical-safety / compliance claim
  about the on-board `K1` mechanical relay or `J1` "Inline Fan"
  load-side output (tracked under COMPLIANCE-001);
- resolve the systemic `IO3` (Core schematic `Relay` net) vs
  `GPIO4` (ceiling Core abstract `relay_pin`) vs `GPIO10` (generic
  Core abstract `relay_pin`) disagreement — that resolution is
  owned by `CORE-ABSTRACT-BUS-001`;
- fabricate connector type, pin order, signal mapping, or ESP32
  GPIO allocation. Values not proven by the committed module-side
  schematic PDF or the canonical Core schematic carry **TBD** or
  **needs silkscreen confirmation**.

## Historical `IO3` vs `GPIO4` mismatch (explicit note)

The Core schematic records `IO3 → Relay (J4 Relay module gate)`;
the historical Core abstract package
[`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml)
bound `relay_pin: GPIO4` against the same connector, which on
the canonical `S360-100-R4` schematic is `SEN0609_RX` (RoomIQ
radar UART). The generic Core abstract package
[`packages/hardware/sense360_core.yaml`](../../packages/hardware/sense360_core.yaml)
binds `relay_pin: GPIO10`. **All three values disagree.** This
pinmap records the Core-side `Relay` net as `IO3` per the
canonical schematic (the only schematic-backed source); the
firmware-side reconciliation is owed under
`CORE-ABSTRACT-BUS-001` per
[`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3](../release-one-hardware-audit.md#required-follow-ups)
and is **not** resolved by this PR.

## Board identity

| Field | Value |
|---|---|
| Friendly name | Sense360 Relay |
| SKU | `S360-310` |
| Rev | R4 |
| Mating Core connector | `J4` (3-pin Relay module connector) on `S360-100-R4` |
| Module-side connector | `J2` (3-pin "From Core") on `S360-310-R4` |
| Module-side load-side connector | `J1` (3-pin "Inline Fan") — mains-rated; out of scope for this pinmap |
| Companion audit doc | [`s360-310-r4-relay.md`](s360-310-r4-relay.md) |

## Google Drive source evidence

The canonical Google Drive hardware folder for this board is
`PCB 2026 Sense360_r4 / PCB Project Files / Sense360 (Celling) / S360-310-R4`,
organized under per-type subfolders (`sch_pdf` / `Bom` / `cpl` /
`Gerbers` / `stepfile` / `images` / `assets`).

| Drive item | Type | Notes |
|---|---|---|
| `S360-310-R4 / sch_pdf / S360-310-R4.pdf` | Schematic PDF | Module-side schematic. Byte-identical copy committed in-repo at [`schematics/S360-310-R4.pdf`](schematics/S360-310-R4.pdf). |
| `S360-310-R4 / Bom` | BOM artifacts | Retained-but-not-committed. |
| `S360-310-R4 / cpl` | Pick-and-place | Retained-but-not-committed. |
| `S360-310-R4 / Gerbers` | Gerbers | Retained-but-not-committed. |
| `S360-310-R4 / stepfile` | 3D STEP | Retained-but-not-committed. |
| `S360-310-R4 / images` | Renders / photos | Retained-but-not-committed. |
| `S360-310-R4 / assets` | Misc. | Retained-but-not-committed. |

## Evidence status

| Artifact class | Evidence available | Status |
|---|---|---|
| Module-side schematic PDF | [`schematics/S360-310-R4.pdf`](schematics/S360-310-R4.pdf) (committed) | schematic-backed |
| KiCad source | Not committed in-repo | TBD |
| Gerber / drill files | Drive `Gerbers` (retained-but-not-committed) | TBD |
| 3D render / STEP | Drive `stepfile` (retained-but-not-committed) | TBD |
| Board photographs | Drive `images` (retained-but-not-committed) | TBD |
| BOM | Drive `Bom` (retained-but-not-committed) | TBD |
| Silkscreen / bench evidence | `S360-310-BENCH-001` per [`s360-310-r4-relay.md`](s360-310-r4-relay.md) — ten enumerated rows `pending — bench evidence required` | TBD |

## Mating Core connector

| Element | Value |
|---|---|
| Core connector ref | `J4` |
| Core connector type | TBD (3-pin header; type not annotated on the visible Core sheet) |
| Pin count | 3 |
| Pin-1 orientation | TBD — needs silkscreen confirmation |
| Module-side connector ref | `J2` (`S360-310-R4`) |

## Module-side pinmap (`J2` ↔ Core `J4`)

The Core-side master table for `J4` is in
[`s360-100-core-connector-pin-map.md` § J4 — Relay module connector (3-pin)](s360-100-core-connector-pin-map.md#j4--relay-module-connector-3-pin).
The module-side capture is taken from
[`s360-310-r4-relay.md` § Module-side `J2` ↔ Core-side `J4`](s360-310-r4-relay.md#module-side-j2--core-side-j4-3-pin-harness).

| Pin number | Module-side signal | Core net | ESP32 GPIO | Module-side signal type | Voltage / domain | Status |
|---|---|---|---|---|---|---|
| 1 | Relay coil supply rail (feeds `K1` mechanical relay coil via `Q1` MMBT3904 NPN low-side driver path) | `+5V` | N/A | power | `+5V` | needs silkscreen confirmation |
| 2 | Relay drive (module-side input to `Q1` base via `R1` 1 kΩ; `R2` 10 kΩ base pull-down; flyback diode `D1` across the relay coil; load-side switching is on `J1` "Inline Fan") | `Relay` | `IO3` (Core schematic — see [Historical `IO3` vs `GPIO4` mismatch](#historical-io3-vs-gpio4-mismatch-explicit-note)) | digital output | `Logic 3.3V (ESP32-S3)` (drive line; mains switching is module-side / isolated) | schematic-backed |
| 3 | Relay module ground reference | `GND` | N/A | ground | `GND` | needs silkscreen confirmation |

> **No `TachIO` / `Pul_Cou*` row on this connector.** Relay does
> not source or sink any tach / pulse-counter signal.

## Mains / load-side note

The load-side `J1` "Inline Fan" connector on the relay module
switches mains. This document records the **presence** of the
load-side connector only. It does **not**:

- record contact rating, snubber, isolation barrier, creepage or
  clearance values;
- record `J1` NO / COM / NC mapping;
- make any mains-voltage / electrical-safety / compliance claim
  (tracked under COMPLIANCE-001 in
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md));
- prove `K1` part number, coil-voltage, or contact-current rating
  (the schematic symbol carries no value label per
  [`s360-310-r4-relay.md`](s360-310-r4-relay.md)).

## Open questions / verification needed

1. **`IO3` (Core schematic) vs `GPIO4` (ceiling Core abstract
   `relay_pin`) vs `GPIO10` (generic Core abstract `relay_pin`)
   disagreement.** Resolution owed under `CORE-ABSTRACT-BUS-001`.
2. **Silkscreen pin-1 orientation on Core `J4` and module `J2`.**
3. **`K1` part number, coil voltage, contact rating.** Owed to
   BOM / silkscreen evidence.
4. **`J1` "Inline Fan" load-side NO / COM / NC mapping.**
5. **Core-to-module harness identity** (cable, connector keying,
   conductor gauge).
6. **Mains compliance.** All mains-related evidence is tracked
   under COMPLIANCE-001 and is out of scope for this pinmap.

## Cross references

- [`s360-100-core-connector-pin-map.md`](s360-100-core-connector-pin-map.md) — canonical Core-to-module connector pin map (S360-100-CONNECTOR-PINMAP-001).
- [`s360-100-r4-core.md`](s360-100-r4-core.md) — Core per-pin / per-net reference (records `IO3 → Relay`).
- [`s360-310-r4-relay.md`](s360-310-r4-relay.md) — Relay board-side audit (HW-PINMAP-310 / HW-PINMAP-310-FOLLOWUP).
- [`s360-310-relay-pinmap-reconcile.md`](s360-310-relay-pinmap-reconcile.md) — Relay GPIO cross-layer reconcile record (S360-310-RELAY-PINMAP-RECONCILE-001).
- [`schematics/S360-310-R4.pdf`](schematics/S360-310-R4.pdf) — committed module-side schematic PDF.
- [`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md) — COMPLIANCE-001 mains-voltage compliance tracker.
- [`docs/blocker-burndown.md`](../blocker-burndown.md) — blocker / scope-classification table (PACKAGE-RELAY-001).

## Do-not-change guardrails

This document does **not**:

- promote `S360-310` `schematic_status` beyond `cataloged_unverified`;
- promote `FanRelay` to release;
- add or change WebFlash builds in
  [`config/webflash-builds.json`](../../config/webflash-builds.json);
- claim release / WebFlash readiness for any FanRelay-bearing
  product;
- make any mains-voltage safety / compliance claim;
- resolve `CORE-ABSTRACT-BUS-001`;
- fabricate connector type, pin order, or signal assignment;
- map any tach / pulse-counter signal through an expander.

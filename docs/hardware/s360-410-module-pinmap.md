# S360-410 Module-Side Pinmap (MODULE-PINMAPS-GDRIVE-001)

## Status

**Status: documentation-only schematic-backed module-side pinmap.
`PACKAGE-POE-410-001` blocker is unchanged; `S360-410` stays
`cataloged_unverified`; no release / WebFlash readiness is
implied.** Companion to the canonical Core-side
[`s360-100-core-connector-pin-map.md`](s360-100-core-connector-pin-map.md)
(S360-100-CONNECTOR-PINMAP-001). This document records the
**module-side** view of the Sense360 PoE PSU (`S360-410`) board
and reconciles every pin back to the mating Core connector `J2`.

It is **documentation only**. It does **not**:

- publish firmware, create release artifacts, or promote any
  release target;
- promote `S360-410` `schematic_status` in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  beyond its current `cataloged_unverified` value;
- promote `S360-410` to `verified`;
- claim the `PACKAGE-POE-410-001` blocker chain is solved (audit
  lane is unchanged);
- close HW-002 Open Question #6 J2-harness identity (tracked
  under
  [`s360-100-r4-core.md` § S360-100-BENCH-001 status](s360-100-r4-core.md#s360-100-bench-001-status));
- resolve the PoE-module part-identity disagreement between the
  package header
  [`packages/hardware/power_poe.yaml`](../../packages/hardware/power_poe.yaml)
  (`Ag9712M, Silvertel Ag9700, or similar` whole-module hint) and
  the schematic-shown discrete topology (`TPS2378DDAR(HSOIC-8)`
  PoE PD controller + `TX4138(ESOIC-8)` buck + `F0505S-2WR2(SIP-7)`
  isolated DC/DC + `RJP-003TC1(LPJ4112CNL)` magnetics module);
- fabricate connector type, pin order, signal mapping, or ESP32
  GPIO allocation. Values not proven by the committed module-side
  schematic PDF or the canonical Core schematic carry **TBD** or
  **needs silkscreen confirmation**.

## Board identity

| Field | Value |
|---|---|
| Friendly name | Sense360 PoE PSU |
| SKU | `S360-410` |
| Rev | R4 |
| Mating Core connector | `J2` (2-pin PoE_ACDC inlet) on `S360-100-R4` |
| Module-side LV output connector | `J3` (2-pin "Connection to Cores") on `S360-410-R4` |
| Module-side network input | `LAN_CON1` integrated 10/100 BASE-TX magnetics + RJ45 module |
| Companion audit doc | [`s360-410-r4-poe.md`](s360-410-r4-poe.md) |

## Google Drive source evidence

The canonical Google Drive hardware folder for this board is
`PCB 2026 Sense360_r4 / PCB Project Files / Sense360 (Celling) / S360-410-R4`,
organized under per-type subfolders (`sch_pdf` / `bom` / `cpl` /
`gerbers` / `step_file` / `images` / `Assets`).

| Drive item | Type | Notes |
|---|---|---|
| `S360-410-R4 / sch_pdf / S360-410-R4.pdf` | Schematic PDF | Module-side schematic. Byte-identical copy committed in-repo at [`schematics/S360-410-R4.pdf`](schematics/S360-410-R4.pdf) (975,137 bytes; SHA256 `4a8b7a3b2a89006a9332eaa486743f687aaedc4b6bb807c6b25670f742ac2414`). |
| `S360-410-R4 / bom` | BOM artifacts | Retained-but-not-committed per [`hardware-artifact-policy.md`](hardware-artifact-policy.md). |
| `S360-410-R4 / cpl` | Pick-and-place | Retained-but-not-committed. |
| `S360-410-R4 / gerbers` | Gerbers | Retained-but-not-committed. |
| `S360-410-R4 / step_file` | 3D STEP | Retained-but-not-committed. |
| `S360-410-R4 / images` | Renders / photos | Retained-but-not-committed. |
| `S360-410-R4 / Assets` | Misc. | Retained-but-not-committed. |

## Evidence status

| Artifact class | Evidence available | Status |
|---|---|---|
| Module-side schematic PDF | [`schematics/S360-410-R4.pdf`](schematics/S360-410-R4.pdf) (committed) | schematic-backed |
| KiCad source | Not committed in-repo | TBD |
| Gerber / drill files | Drive `gerbers` (retained-but-not-committed) | TBD |
| 3D render / STEP | Drive `step_file` (retained-but-not-committed) | TBD |
| Board photographs | Drive `images` (retained-but-not-committed) | TBD |
| BOM | Drive `bom` (retained-but-not-committed) — part-identity disagreement is open under `PACKAGE-POE-410-001` | TBD |
| Silkscreen / bench evidence | None committed | TBD |
| PoE link-up / load / EMI / isolation evidence | Not recorded | TBD |

## Mating Core connector

| Element | Value |
|---|---|
| Core connector ref | `J2` |
| Core connector type | TBD (2-pin power inlet header; type not annotated on the visible Core sheet) |
| Pin count | 2 |
| Pin-1 orientation | TBD — needs silkscreen confirmation |
| Module-side connector ref | `J3` (`S360-410-R4`) |
| Harness identity | HW-002 OQ#6; `pending — bench/manufacturing evidence required` per [`s360-100-r4-core.md` § S360-100-BENCH-001 status](s360-100-r4-core.md#s360-100-bench-001-status) |

## Module-side pinmap (`J3` ↔ Core `J2`)

The Core-side master table for `J2` is in
[`s360-100-core-connector-pin-map.md` § J2 — PoE PSU inlet (2-pin)](s360-100-core-connector-pin-map.md#j2--poe-psu-inlet-2-pin).
The module-side capture is taken from
[`s360-410-r4-poe.md` § `J3` Core-facing output](s360-410-r4-poe.md#j3-core-facing-output-2-pin).

| Pin number | Module-side signal | Core net | ESP32 GPIO | Module-side signal type | Voltage / domain | Status |
|---|---|---|---|---|---|---|
| 1 | `+5VP` — post-isolation +5 V DC output of the `F0505S-2WR2(SIP-7)` isolated DC/DC (`AM1D-0505S-NZ` annotated alternate); `C8 22u` bulk + `R9 1k` bleed; routed through Core `Q2` `Si2319CDS` p-MOSFET ideal-diode-OR with `VBUS` into the Core `+5V` rail | `PoE_ACDC` (Core side) | N/A | power inlet | `PoE_ACDC` (DC inlet; off-board) | needs silkscreen confirmation |
| 2 | `GND` (post-isolation; **not** the same node as the pre-isolation `Earth` / `Lan_earth` rail) | `GND` | N/A | ground | `GND` | needs silkscreen confirmation |

> **No `TachIO` / `Pul_Cou*` row on this connector.** The PoE PSU
> does not source or sink any tach / pulse-counter signal.

## Pre-isolation domain note (informational)

The `S360-410` module crosses an isolation boundary inside the
`F0505S-2WR2(SIP-7)` (or `AM1D-0505S-NZ` annotated alternate)
isolated DC/DC. The **pre-isolation** domain on the PoE side
carries the nets `Spare1` / `Spare2` / `Lan_earth` / `PoE_Power` /
`PoE_SW` / `Sw_Vin_Poe` / `Earth`. The **post-isolation** domain
exposes only `+5VP` and `GND` to the Core `J2` inlet. The
mounting holes `H1`–`H4` are each labelled `Earth` at the symbol
layer; PCB-level electrical bonding of `H1`–`H4` to `Lan_earth` /
RJ45 shield is **not recorded** and is owed to silkscreen / PCB
source evidence.

This pinmap **does not** restate per-component values from the
PoE-side topology (`TPS2378DDAR` PD controller; `R1 24.9k`
detection signature; `R2 1.27k` Class=0 classification; `D1
SMAJ58A` TVS; `C2 15uF` CBULK; `R5 0.03R` RTN current sense;
`TX4138` buck with `R3/R4 9.1k` ILIM; `L1 33uH`; `D2 ss510`;
`C6 470u`; `R7 10.5k` / `R8 56.2k` feedback) — those values are
already captured in
[`s360-410-r4-poe.md`](s360-410-r4-poe.md).

## `PACKAGE-POE-410-001` blocker preservation (explicit)

`PACKAGE-POE-410-001` audit lane stays **unchanged**. This pinmap
does not:

- BOM-confirm the discrete topology;
- close the `Ag9712M` / `Silvertel Ag9700` whole-module hint vs
  discrete-topology disagreement;
- demonstrate PoE link-up against an 802.3af or 802.3at PSE;
- demonstrate signature / classification behaviour in hardware;
- demonstrate load regulation / cold-start inrush / thermal rise
  / EMI / EMC behaviour;
- demonstrate insulation resistance / Hi-pot / earth-continuity /
  leakage for the assembled board;
- record COMPLIANCE-001-adjacent isolation-barrier evidence.

PoE is SELV; `S360-410` is **not** in the COMPLIANCE-001 mains-
voltage UK / EU scope. Mains-voltage COMPLIANCE-001 applies to
`S360-320` and `S360-400`, not `S360-410`.

## Open questions / verification needed

1. **HW-002 OQ#6 — J2-harness identity.** Physical Release-One
   harness between off-board `S360-410 J3` and Core `J2`. Pending
   bench / manufacturing evidence per
   [`s360-100-r4-core.md` § S360-100-BENCH-001 status](s360-100-r4-core.md#s360-100-bench-001-status).
2. **Silkscreen pin-1 orientation on Core `J2` and module `J3`.**
3. **`J3` connector identity, current rating, keying.** Owed to
   BOM / silkscreen evidence.
4. **`LAN_CON1` magnetics-module mating, BOM identity.** Owed to
   BOM / silkscreen evidence.
5. **PoE link-up against an 802.3af / 802.3at PSE.** Owed to
   bench evidence.
6. **`Ag9712M` / `Silvertel Ag9700` whole-module hint vs
   `TPS2378DDAR` + `TX4138` + `F0505S-2WR2` discrete topology.**
   Owed to `PACKAGE-POE-410-001`.

## Cross references

- [`s360-100-core-connector-pin-map.md`](s360-100-core-connector-pin-map.md) — canonical Core-to-module connector pin map (S360-100-CONNECTOR-PINMAP-001).
- [`s360-100-r4-core.md`](s360-100-r4-core.md) — Core per-pin / per-net reference (records `J2` as PoE_ACDC inlet).
- [`s360-410-r4-poe.md`](s360-410-r4-poe.md) — PoE PSU board-side audit (HW-PINMAP-410 / HW-PINMAP-410-FOLLOWUP).
- [`artifacts/S360-410-R4.md`](artifacts/S360-410-R4.md) — curated artifact index (HW-ASSETS-410).
- [`s360-400-module-pinmap.md`](s360-400-module-pinmap.md) — 240V PSU module-side pinmap (shared Core `J2` inlet semantics).
- [`schematics/S360-410-R4.pdf`](schematics/S360-410-R4.pdf) — committed module-side schematic PDF.
- [`docs/blocker-burndown.md`](../blocker-burndown.md) — blocker / scope-classification table (`PACKAGE-POE-410-001`).
- [`docs/package-poe-410-001-audit.md`](../package-poe-410-001-audit.md) — `PACKAGE-POE-410-001` audit.

## Do-not-change guardrails

This document does **not**:

- promote `S360-410` `schematic_status` beyond `cataloged_unverified`;
- promote `S360-410` to `verified`;
- claim the `PACKAGE-POE-410-001` blocker chain is solved;
- promote any PoE-PSU-bearing product beyond Release-One;
- add or change WebFlash builds in
  [`config/webflash-builds.json`](../../config/webflash-builds.json);
- claim release / WebFlash readiness beyond existing Release-One
  posture;
- claim PoE link-up, load regulation, isolation, EMI, or
  signature / classification behaviour;
- fabricate connector type, pin order, or signal assignment;
- map any tach / pulse-counter signal through an expander.

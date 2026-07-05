# S360-400 Module-Side Pinmap (MODULE-PINMAPS-GDRIVE-001)

## Status

**Status: documentation-only schematic-backed module-side pinmap.
`S360-400` stays `cataloged_unverified`; PWR-240V stays out of
release; COMPLIANCE-001 stays in force.** Companion to the
canonical Core-side
[`s360-100-core-connector-pin-map.md`](s360-100-core-connector-pin-map.md)
(S360-100-CONNECTOR-PINMAP-001). This document records the
**module-side** view of the Sense360 240v PSU (`S360-400`) board.

`S360-400` is an **off-board mains-AC → +5 V DC PSU module**. It
is not listed in the Core-to-module connector matrix in
[`s360-100-core-connector-pin-map.md` § Connector matrix](s360-100-core-connector-pin-map.md#connector-matrix)
because its low-voltage output feeds the Core via the same
`+5VP` / `GND` inlet that `S360-410` (PoE PSU) uses (Core `J2`
PoE_ACDC inlet, see
[`s360-100-core-connector-pin-map.md` § J2 — PoE PSU inlet (2-pin)](s360-100-core-connector-pin-map.md#j2--poe-psu-inlet-2-pin)).
Both PSU boards present the same off-board low-voltage 2-pin DC
output to the Core; whether the physical Release-One harness
between `S360-400` `J2` and Core `J2` is identical to the
`S360-410` `J3` ↔ Core `J2` harness is an open question (see
[Open questions](#open-questions--verification-needed)).

It is **documentation only**. It does **not**:

- publish firmware, create release artifacts, or promote any
  release target;
- promote `S360-400` `schematic_status` in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  beyond its current `cataloged_unverified` value;
- promote any `PWR`-bearing product;
- claim mains-voltage compliance for `S360-400` — `COMPLIANCE-001`
  per
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md)
  remains the mains-voltage UK / EU gate;
- resolve the three-way AC/DC part-identity disagreement
  (catalog `HLK-5M05`; package header `HLK-PM01 or similar`;
  schematic `PS1 = HLK-10M05`);
- fabricate connector type, pin order, signal mapping, or ESP32
  GPIO allocation. Values not proven by the committed module-side
  schematic PDF or the canonical Core schematic carry **TBD** or
  **needs silkscreen confirmation**.

## Board identity

| Field | Value |
|---|---|
| Friendly name | Sense360 240v PSU |
| SKU | `S360-400` |
| Rev | R4 |
| Mating Core connector | Core `J2` PoE_ACDC inlet (2-pin) — shared with `S360-410`; physical Release-One harness identity is `verify` |
| Module-side AC input | `J1` (3-pin) — mains-rated; LIVE / NEUTRAL / Earth_Protective |
| Module-side LV output | `J2` (2-pin) — `+5VP` / `GND` |
| Companion audit doc | [`s360-400-r4-power.md`](s360-400-r4-power.md) |

## Google Drive source evidence

The canonical Google Drive hardware folder for this board is
`PCB 2026 Sense360_r4 / PCB Project Files / Sense360 (Celling) / S360-400-R4`,
organized under per-type subfolders (`sch_pdf` / `bom` / `cpl` /
`gerbers` / `step_file` / `images` / `Assets`).

| Drive item | Type | Notes |
|---|---|---|
| `S360-400-R4 / sch_pdf / S360-400-R4.pdf` | Schematic PDF | Module-side schematic. Byte-identical copy committed in-repo at [`schematics/S360-400-R4.pdf`](schematics/S360-400-R4.pdf). |
| `S360-400-R4 / bom` | BOM artifacts | Retained-but-not-committed per [`hardware-artifact-policy.md` (archived)](../archive-index.md). |
| `S360-400-R4 / cpl` | Pick-and-place | Retained-but-not-committed. |
| `S360-400-R4 / gerbers` | Gerbers | Retained-but-not-committed. |
| `S360-400-R4 / step_file` | 3D STEP | Retained-but-not-committed. |
| `S360-400-R4 / images` | Renders / photos | Retained-but-not-committed. |
| `S360-400-R4 / Assets` | Misc. | Retained-but-not-committed. |

## Evidence status

| Artifact class | Evidence available | Status |
|---|---|---|
| Module-side schematic PDF | [`schematics/S360-400-R4.pdf`](schematics/S360-400-R4.pdf) (committed) | schematic-backed |
| KiCad source | Not committed in-repo | TBD |
| Gerber / drill files | Drive `gerbers` (retained-but-not-committed) | TBD |
| 3D render / STEP | Drive `step_file` (retained-but-not-committed) | TBD |
| Board photographs | Drive `images` (retained-but-not-committed) | TBD |
| BOM | Drive `bom` (retained-but-not-committed) | TBD |
| Silkscreen / bench evidence | None committed | TBD |
| Mains-compliance evidence (COMPLIANCE-001) | Not recorded | TBD |

## Module-side mains AC input connector — `J1` (3-pin)

`J1` is the mains-AC input. **No mains-voltage / safety claim is
made here.** Pin function is recorded per the committed
schematic; pin-1 silkscreen orientation, connector identity, and
current / voltage ratings are TBD.

| Pin number | Module-side signal | Module-side signal type | Voltage / domain | Status |
|---|---|---|---|---|
| 1 | `LIVE` (mains live conductor) | mains-AC input | `Mains-domain` | needs silkscreen confirmation |
| 2 | `NEUTRAL` (mains neutral conductor) | mains-AC input | `Mains-domain` | needs silkscreen confirmation |
| 3 | `Earth_Protective` (protective earth) | mains-AC input | `Mains-domain` (PE) | needs silkscreen confirmation |

> **Mains-voltage compliance.** All mains-rated electrical-safety
> evidence — fuse rating (`F1`), MOV clamp voltage (`RV1`), X-cap
> safety class (`C1`), creepage / clearance, isolation barrier,
> earth bonding, inrush limiter, conducted / radiated EMI / EMC —
> is tracked under COMPLIANCE-001 and is **out of scope** for
> this pinmap.

## Module-side low-voltage DC output connector — `J2` (2-pin)

`J2` is the LV output to the Core. It feeds the Core `J2`
PoE_ACDC inlet (or an equivalent harness; the Release-One
physical harness identity is `verify`).

| Pin number | Module-side signal | Core net (on Core `J2`) | ESP32 GPIO | Module-side signal type | Voltage / domain | Status |
|---|---|---|---|---|---|---|
| 1 | `+5VP` (post-PSU DC output; routed via Core `Q2` `Si2319CDS` p-MOSFET ideal-diode-OR into the Core `+5V` rail) | `PoE_ACDC` (Core side; the Core does not regulate this rail before `Q2`) | N/A | power inlet | `PoE_ACDC` (DC inlet; off-board) | TBD |
| 2 | `GND` (PSU / Core ground reference) | `GND` | N/A | ground | `GND` | TBD |

> **No `TachIO` / `Pul_Cou*` row on this connector.** The 240V
> PSU does not source or sink any tach / pulse-counter signal.

## AC/DC converter (informational)

The module schematic prints `PS1 = HLK-10M05` with pinout
`AC(L)` / `AC(N)` / `-VO` / `+VO`. The
[`config/hardware-catalog.json`](../../config/hardware-catalog.json)
row line 109 records `Mains to 5V using HLK-5M05.`; the package
header
[`packages/hardware/power_240v.yaml`](../../packages/hardware/power_240v.yaml)
line 7 records `HLK-PM01 or similar`. **Three-way disagreement
unresolved.** Resolution owed to `PACKAGE-POWER-400-001` BOM
evidence.

## Open questions / verification needed

1. **Three-way AC/DC part-identity disagreement.** Catalog
   `HLK-5M05` vs package header `HLK-PM01 or similar` vs
   schematic `PS1 = HLK-10M05`. Owed to `PACKAGE-POWER-400-001`.
2. **Physical Release-One harness identity between Module `J2`
   and Core `J2`.** Whether `S360-400 J2` mates with Core `J2`
   directly (same cable / pigtail as `S360-410 J3` ↔ Core `J2`)
   or via a different connector is `verify`.
3. **`J1` 3-pin mains-AC connector identity, current rating,
   keying.** Owed to BOM / silkscreen evidence.
4. **`J2` 2-pin low-voltage connector identity, current rating,
   keying.** Owed to BOM / silkscreen evidence.
5. **Per-component ratings.** `F1 A250-1200` hold / trip /
   voltage; `RV1 10D391K` clamp voltage / energy; `C1 470nF`
   X-cap safety class X1 / X2; output-filter cap voltage /
   dielectric / ESR. Owed to BOM.
6. **Mains compliance (COMPLIANCE-001).** Creepage / clearance,
   isolation, earth bonding, thermal, inrush, EMI / EMC.

## Cross references

- [`s360-100-core-connector-pin-map.md`](s360-100-core-connector-pin-map.md) — canonical Core-to-module connector pin map (S360-100-CONNECTOR-PINMAP-001).
- [`s360-100-r4-core.md`](s360-100-r4-core.md) — Core per-pin / per-net reference.
- [`s360-400-r4-power.md`](s360-400-r4-power.md) — 240v PSU board-side audit (HW-PINMAP-400 / HW-PINMAP-400-FOLLOWUP).
- [`s360-410-module-pinmap.md`](s360-410-module-pinmap.md) — PoE PSU module-side pinmap (shared Core `J2` inlet semantics).
- [`schematics/S360-400-R4.pdf`](schematics/S360-400-R4.pdf) — committed module-side schematic PDF.
- [`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md) — COMPLIANCE-001 mains-voltage compliance tracker.
- [`docs/blocker-burndown.md` (archived)](../archive-index.md) — blocker / scope-classification table (PACKAGE-POWER-400-001).

## Do-not-change guardrails

This document does **not**:

- promote `S360-400` `schematic_status` beyond `cataloged_unverified`;
- promote any `PWR`-bearing product;
- add or change WebFlash builds in
  [`config/webflash-builds.json`](../../config/webflash-builds.json);
- claim release / WebFlash readiness;
- make any mains-voltage safety / compliance claim;
- resolve `PACKAGE-POWER-400-001`;
- fabricate connector type, pin order, or signal assignment;
- map any tach / pulse-counter signal through an expander.

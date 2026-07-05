# S360-211-R4 — Sense360 VentIQ Hardware Reference

## Purpose

This document is the schematic-backed pin, connector, and net reference for the
**Sense360 VentIQ** bathroom-focused air-quality module, revision **R4**
(`S360-211-R4`). VentIQ is the air-quality slot in the production Release-One
config string `Ceiling-POE-VentIQ-RoomIQ`.

This document is hardware reference only. It does **not** by itself prove that
any ESPHome YAML in this repository is correct. The HW-007 PR commits the
module-side schematic PDF and this standalone reference doc.

The machine-readable `schematic_status` field for `S360-211` in
[`config/hardware-catalog.json`](../../config/hardware-catalog.json) is **not**
changed by this PR — the status promotion from `cataloged_unverified` is
deferred to HW-008. Similarly, the "schematic verification pending" caveat that
appears in
[`docs/release-one-hardware-audit.md` (archived)](../archive-index.md) and
[`docs/webflash-compatibility-taxonomy-audit.md` (archived)](../archive-index.md)
is **retained** until HW-008 flips the JSON field — those docs gain a pointer
to this new evidence but do not drop the caveat.

## Board identity

| Field         | Value                                                                    |
| ------------- | ------------------------------------------------------------------------ |
| Friendly name | Sense360 VentIQ                                                          |
| SKU           | S360-211                                                                 |
| Rev           | R4                                                                       |
| Old name      | Bathroom Pro                                                             |
| Role          | Bathroom-focused air-quality module (VOC, IR temperature, PM, fan relay) |

This row matches the entries in
[`docs/hardware-catalog.md`](../hardware-catalog.md) and
[`config/hardware-catalog.json`](../../config/hardware-catalog.json). Do not
use the legacy `Bathroom Pro` name in new user-facing material.

## Schematic source

| Field             | Value                                              |
| ----------------- | -------------------------------------------------- |
| Schematic file    | [`schematics/S360-211-R4.pdf`](schematics/S360-211-R4.pdf) |
| PDF committed     | Yes, under HW-007                                  |
| KiCad source      | Not committed                                      |

The schematic PDF is the authoritative reference for every section below.
Where a label in the PDF was ambiguous or hard to read, the affected row is
marked **verify**. No pin is inferred or invented.

## Main components (visible on this sheet)

- **SGP41** — Sensirion VOC / NOₓ sensor on the shared I²C bus. Visible on
  this sheet of the VentIQ board.
- **IR temperature sensor connector** — header for an off-board IR / contact
  temperature sensor (used for shower / surface temperature). The IR sensor
  itself lives off-board on a separate module.
- **SPS30 connector** — Sensirion particulate-matter (PM₁ / PM₂.₅ / PM₄ /
  PM₁₀) sensor connector. Sensor lives off-board on a Sensirion SPS30
  module.
- **Inline fan-control relay circuitry** — VentIQ carries on-board relay
  drive circuitry to switch a bathroom extractor fan inline with the air-
  quality readings. Mains-level switching topology, contact rating, and
  isolation are **verify** and explicitly subject to the mains-voltage
  safety / compliance review tracked in
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md)
  (COMPLIANCE-001) — HW-007 makes no compliance claim.
- **Module connector to Core** — the VentIQ board plugs into the Sense360
  Core's `J9` "AirIQ Module Connector" (7-pin header on `S360-100-R4` —
  see [`s360-100-r4-core.md` §J9](s360-100-r4-core.md#j9--airiq-module-connector-7-pin)).
  The connector name on the Core remains the legacy `AirIQ Module
  Connector` label per the WebFlash contract §6 footnote about retained
  legacy package filenames; AirIQ and VentIQ are mutually exclusive and
  share this physical connector slot.

## Module connector mating

On the Core (`S360-100-R4`), `J9` is the 7-pin "AirIQ Module Connector"
that VentIQ plugs into. The Core J9 table is the source of truth for the
Core-side pin order:

| Core J9 pin | Core J9 net          | Direction on VentIQ                                                |
| ----------- | -------------------- | ------------------------------------------------------------------ |
| 1           | `+5V`                | Powers SPS30 (PM) and any +5 V loads                               |
| 2           | `+3.3V`              | Powers SGP41 and logic                                             |
| 3           | `I2C_SDA`            | Shared I²C bus — SGP41, off-board IR temperature (if I²C)         |
| 4           | `I2C_SCL`            | Shared I²C bus                                                     |
| 5           | `AirQ_Status_Led`    | Legacy `AirQ`-prefixed net — VentIQ reuse is **verify**            |
| 6           | `AirQ_Led`           | Legacy `AirQ`-prefixed net — VentIQ reuse is **verify**            |
| 7           | `GND`                |                                                                    |

The Core J9 table is committed; the VentIQ-side mating pin order is
**verify** against the VentIQ silkscreen. Whether `AirQ_Led` and
`AirQ_Status_Led` are consumed by VentIQ at all (and which on-board
indicator they drive) is **verify** — this doc does not resolve HW-002
Open Question #4.

## On-board sensors and connectors

| Sensor / connector  | Interface              | Notes                                                                                                 |
| ------------------- | ---------------------- | ----------------------------------------------------------------------------------------------------- |
| SGP41               | I²C (shared bus)       | Sensirion VOC index + NOₓ index. On-board; visible on this sheet.                                    |
| IR temperature connector | I²C / digital — verify | Off-board IR / contact temperature sensor. Interface (I²C vs digital pulse) is **verify** against the sensor module spec. |
| SPS30 connector     | UART or I²C — verify   | Sensirion particulate-matter module connector. Sensor lives off-board. The SPS30 supports both UART and I²C; which interface is wired here is **verify**. |
| Fan-relay drive     | Relay (mains switching)| On-board relay circuitry to switch a bathroom extractor fan. Drive signal source on the Core / J9 side is **verify**; contact rating, isolation, and mains compliance are **verify** and tracked under COMPLIANCE-001. |

## I²C bus

The shared I²C bus reaches VentIQ via `J9` pins 3 (`I2C_SDA`) and 4
(`I2C_SCL`). The Core side of that bus carries the 10 kΩ pull-ups (`R21`,
`R22` on `S360-100-R4`); this VentIQ board does not appear to duplicate
them. Local resistor placement is **verify**.

| I²C target on VentIQ | Address (where labelled) | Notes                                          |
| -------------------- | ------------------------ | ---------------------------------------------- |
| SGP41                | Per Sensirion datasheet  | Address not separately strapped — **verify**. |
| IR temperature (off-board) | Per sensor datasheet — **verify** | Only if the IR sensor is I²C. |

## Mains / fan-relay note

VentIQ's on-board fan-relay circuitry switches a bathroom extractor fan.
The relay-contact side of that circuit is **mains-voltage** when used to
switch a mains-powered extractor.

- This doc records the **presence** of the relay drive only.
- It does **not** make any electrical-safety or compliance claim.
- The drive signal source (which Core net / which ESP32-S3 GPIO / which
  SX1509 channel) is **verify**.
- Contact rating, snubber, creepage / clearance, and mains compliance
  are tracked under COMPLIANCE-001 (see
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md))
  and are **out of scope** for HW-007.

The Release-One config string `Ceiling-POE-VentIQ-RoomIQ` does **not**
include a fan-driver token. The mains-switching relay shown on the VentIQ
schematic is documented here for completeness; its production status,
firmware-driver mapping, and compliance evidence are tracked separately.

## Open questions / verification needed

These items are explicitly out of scope for HW-007. They are inputs to
HW-008 and to any future VentIQ-related firmware audit.

1. **VentIQ side of the J9 connector — 1-to-7 pin order.** The Core J9
   table is committed; the VentIQ side has to match it. Confirm against
   the VentIQ silkscreen.
2. **`AirQ_Led` / `AirQ_Status_Led` reuse on VentIQ.** HW-002 Open
   Question #4 stays open. Whether these nets drive a VentIQ-side
   indicator, and whether AirIQ reuses the same physical lines for the
   same purpose, is not resolved by this PDF alone.
3. **Fan-relay drive-signal source.** Which Core net / ESP32 GPIO / SX1509
   channel actually drives the on-board relay coil is **verify**. The
   Release-One YAML does not bind a fan-driver to VentIQ; this question
   is for future fan-driver audits, not Release-One.
4. **SPS30 connector interface (UART vs I²C).** **Verify** against the
   silkscreen.
5. **IR temperature connector interface.** I²C target address (or, if
   digital, pulse / one-wire encoding) is **verify** against the
   selected IR module.
6. **Mains-side topology and ratings.** Relay contact rating, snubber,
   isolation barrier, creepage / clearance, fusing, and applicable mains
   standards are **verify** and tracked under COMPLIANCE-001 — not by
   HW-007.

## Firmware mapping notes

This document is hardware reference only.

The Release-One product YAML
[`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq.yaml)
consumes the VentIQ slot via the package
[`packages/expansions/airiq_bathroom_base.yaml`](../../packages/expansions/airiq_bathroom_base.yaml).
The package filename retains the legacy `airiq_bathroom_base` form
**on purpose** per the WebFlash contract §6 footnote about legacy package
filenames — do not rename it.

The package targets the abstract `expansion_i2c` bus and does not bind to
specific ESP32-S3 GPIOs. Reconciliation between this package and the
VentIQ schematic is **out of scope for HW-007** and is a HW-follow-up
item tracked in
[`docs/release-one-hardware-audit.md` (archived)](../archive-index.md).

## HW-007 scope and non-scope

What this doc does:

- Records that the `S360-211-R4` schematic PDF is now committed under
  [`schematics/S360-211-R4.pdf`](schematics/S360-211-R4.pdf).
- Captures the visible main-component evidence (SGP41, IR-temperature
  connector, SPS30 connector, inline fan-relay drive circuitry, J9
  mating).
- Improves the Release-One VentIQ evidence — the module-side schematic
  is now committed.

What this doc does **not** do:

- It does **not** change the Release-One config string. Release-One
  remains `Ceiling-POE-VentIQ-RoomIQ`.
- It does **not** change the Release-One artifact name. The artifact
  remains `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`.
- It does **not** flip `S360-211` in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  (`schematic_status` stays `cataloged_unverified`); the JSON status
  upgrade is deferred to HW-008.
- It does **not** remove the "schematic verification pending" caveat in
  [`docs/release-one-hardware-audit.md` (archived)](../archive-index.md)
  or
  [`docs/webflash-compatibility-taxonomy-audit.md` (archived)](../archive-index.md).
  That caveat is tied to the JSON status field and will be dropped by
  HW-008, not here.
- It does **not** rebind, audit, or rename `airiq_bathroom_base.yaml`.
- It does **not** unblock or promote any fan-driver slot.
- It does **not** make any mains-voltage safety or compliance claim.
  Mains compliance is tracked under COMPLIANCE-001.

## See also

- [Sense360 Hardware Catalog](../hardware-catalog.md) — canonical board /
  module names, SKUs, revisions, and legacy names. Do not reuse
  `Bathroom Pro` in new user-facing material.
- [`config/hardware-catalog.json`](../../config/hardware-catalog.json) —
  machine-readable mirror of the catalog. VentIQ's row remains
  `schematic_status: cataloged_unverified` after HW-007; HW-008 owns the
  status flip.
- [S360-100-R4 Core Hardware Reference](s360-100-r4-core.md) — the
  Sense360 Core board that VentIQ plugs into via `J9`.
- [S360-210-R4 AirIQ Hardware Reference](s360-210-r4-airiq.md) —
  sibling air-quality module on the same `J9` connector; mutually
  exclusive with VentIQ.
- [Remaining-board documentation audit (HW-004 / HW-006) (archived)](../archive-index.md)
  — classifies VentIQ's current documentation state.
- [Release-One Hardware Audit (archived)](../archive-index.md) — VentIQ
  schematic-pending caveat retained until HW-008 flips the JSON status.
- [Release-One Configuration (archived)](../archive-index.md) — current Release-One
  config string `Ceiling-POE-VentIQ-RoomIQ`.
- [Mains-voltage UK / EU compliance assessment (COMPLIANCE-001)](../compliance/mains-voltage-uk-eu-assessment.md)
  — separate compliance tracker for any mains-switching hardware; HW-007
  makes no compliance claim about the VentIQ fan-relay circuitry.

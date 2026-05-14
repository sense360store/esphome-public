# S360-200-R4 — Sense360 RoomIQ Hardware Reference

## Purpose

This document is the schematic-backed pin, connector, and net reference for the
**Sense360 RoomIQ** sensor board, revision **R4** (`S360-200-R4`). It exists so
that firmware audits — in particular the upcoming Release-One YAML audit — have
a single, citable source of truth for what the silicon and copper actually do
on the merged room sensor board.

This document is hardware reference only. It does **not** by itself prove that
any ESPHome YAML in this repository is correct. Firmware mappings must be
verified separately by comparing this document against the package and product
YAML (see [Firmware mapping notes](#firmware-mapping-notes)).

## Board identity

| Field         | Value                                                        |
| ------------- | ------------------------------------------------------------ |
| Friendly name | Sense360 RoomIQ                                              |
| SKU           | S360-200                                                     |
| Rev           | R4                                                           |
| Old name      | Presence + Comfort (two boards)                              |
| Role          | Merged room sensor board for comfort and presence sensing    |

This row matches the entries in
[`docs/hardware-catalog.md`](../hardware-catalog.md) and
[`config/hardware-catalog.json`](../../config/hardware-catalog.json), where
`S360-200-R4` is marked **schematic-backed / verified**.

## Schematic source

| Field          | Value                          |
| -------------- | ------------------------------ |
| Schematic file | [`schematics/S360-200-R4.pdf`](schematics/S360-200-R4.pdf) |
| PDF committed  | Yes, under HW-007              |
| KiCad source   | `S360-200-R4.kicad_sch`        |
| KiCad version  | 10.0.0                         |
| Sheet size     | A4                             |
| Sheet count    | 1 (single sheet)               |
| Sheet ID       | 1/1                            |

The schematic PDF is the authoritative reference for every table below. The
KiCad source file itself is **not** committed to this repository. Where a label
in the PDF was ambiguous or hard to read, the affected row is marked **verify**.

> **HW-007 — PDF committed.** The schematic PDF cited above is now committed
> to this repo at [`schematics/S360-200-R4.pdf`](schematics/S360-200-R4.pdf).
> No pin tables, Open Questions, or reconciliation flags in this doc are
> changed by HW-007 — the tables below were already written from this PDF.
> The `config/hardware-catalog.json` `schematic_status` value for `S360-200`
> remains as committed; any JSON status refresh is deferred to HW-008. The
> Core J10 vs RoomIQ J6 pin-order discrepancy remains an Open Question and
> is not resolved by HW-007.

## Main components

- **U1** — `LTR-303ALS-01` ambient light sensor (I²C, with `ALS_INT` interrupt
  output). Powered from +3.3 V.
- **U2** — `SHT4x` temperature / humidity sensor (I²C). Powered from +3.3 V.
- **U3** — `EKMC1601111` PIR motion sensor (digital `OUT` on pin 2). Powered
  from +3.3 V.
- **U4** — `BMP581` pressure sensor (I²C; supports SPI, not used here). Powered
  from +3.3 V via the `VDD` and `VDDIO` pins.
- **J2** — Hi-Link **LD2450** mmWave radar connector (8-pin, only +5 V,
  `Hi-Link_RX`, `Hi-Link_TX`, and `GND` are clearly used; the remaining pins
  are **verify**).
- **J3** — DFRobot **SEN0609** / **C4001** radar connector (5-pin: +5 V,
  `SEN0609_RX`, `SEN0609_TX`, `out(gpio6)`, `GND`). Pin order at the connector
  is **verify** against silkscreen.
- **J6** — 12-pin module connector to the Sense360 Core board's `J10`
  (Presence/Comfort module connector). Carries both power rails, both radar
  UARTs, the auxiliary `out(gpio6)` line, `PIR`, `ALS_INT`, the shared I²C bus,
  and `GND`.
- **JP1** — 3-pin jumper for BMP581 I²C address selection (`add` net to U4
  `SDO/SA0`, with R3 10 k pull-up to +3.3 V). See [I2C bus](#i2c-bus).

Decoupling / pull-up parts visible on the sheet (non-exhaustive):

- **C1 100 µ** and **C2 100 n** on the +5 V rail near `J6` / `J2` / `J3`.
- **C3 100 µ** and **C4 100 n** near the radar connectors.
- **C5 100 n** near `U2`.
- **C6 100 n** and **C7 1 µ** near `U1`.
- **C8 100 n** and **C9 100 n** near `U4`.
- **R1 10 k** and **R2 10 k** around `U1` (one of these pulls `ALS_INT` to
  +3.3 V; exact assignment of each is **verify**).
- **R3 10 k** pull-up to +3.3 V on the BMP581 `add` net at `JP1`.
- **R4 10 k** near `U3` on the PIR output side (pull direction is **verify**).

## Module connector

The board's main interface to the Sense360 Core is the 12-pin connector `J6`.
It mates with `J10` on the Core (`S360-100-R4`). All signals to and from this
board pass through `J6`.

| Connector pin | Net / signal | Purpose                                                 | Notes                                                 |
| ------------- | ------------ | ------------------------------------------------------- | ----------------------------------------------------- |
| 1             | +5V          | Radar power rail                                        | Feeds `J2` (LD2450) and `J3` (SEN0609)                |
| 2             | SEN0609_RX   | DFRobot SEN0609 / C4001 radar UART                      | RX/TX naming is from the Core perspective — verify    |
| 3             | SEN0609_TX   | DFRobot SEN0609 / C4001 radar UART                      | RX/TX naming is from the Core perspective — verify    |
| 4             | out(gpio6)   | Auxiliary radar I/O                                     | Routed to `J3` pin 4 — purpose **verify**             |
| 5             | Hi-Link_RX   | Hi-Link LD2450 radar UART                               | RX/TX naming is from the Core perspective — verify    |
| 6             | Hi-Link_TX   | Hi-Link LD2450 radar UART                               | RX/TX naming is from the Core perspective — verify    |
| 7             | +3.3V        | Sensor logic supply                                     | Feeds `U1`, `U2`, `U3`, `U4`                          |
| 8             | PIR          | EKMC1601111 motion output                               | From `U3` pin 2 (`OUT`)                               |
| 9             | ALS_INT      | LTR-303ALS-01 interrupt output                          | From `U1` pin 5 (`INT`)                               |
| 10            | I2C_SDA      | Shared I²C bus — data                                   | Used by `U1`, `U2`, `U4`                              |
| 11            | I2C_SCL      | Shared I²C bus — clock                                  | Used by `U1`, `U2`, `U4`                              |
| 12            | GND          | Ground                                                  |                                                       |

The pin-order assignment above is taken from the visible J6 schematic symbol on
the S360-200-R4 sheet (pin 1 at the top, pin 12 at the bottom, with the +5 V
rail entering at pin 1 and the +3.3 V rail entering at pin 7). This **does not
match** the J10 table currently in
[`s360-100-r4-core.md`](./s360-100-r4-core.md) (which lists +3.3 V at pin 1 and
+5 V at pin 2). Both connectors are nominally a mating pair, so one of the two
docs needs to be reconciled against the silkscreen on the physical board — see
[Open questions / verification needed](#open-questions--verification-needed).

## Sensor summary

| Sensor / component | Reference         | Interface / nets                            | Purpose                                  | Notes                                                  |
| ------------------ | ----------------- | ------------------------------------------- | ---------------------------------------- | ------------------------------------------------------ |
| PIR                | U3 EKMC1601111    | `PIR`                                       | Motion / occupancy                       | Powered from +3.3 V; `OUT` on pin 2                    |
| LD2450             | J2 (Hi-Link)      | `Hi-Link_RX` / `Hi-Link_TX`                 | mmWave presence / multi-target radar     | Powered from +5 V via the J2 connector                 |
| SEN0609 / C4001    | J3 (DFRobot)      | `SEN0609_RX` / `SEN0609_TX` / `out(gpio6)`  | DFRobot radar / presence sensing         | Powered from +5 V via the J3 connector                 |
| LTR-303ALS-01      | U1                | `I2C_SDA` / `I2C_SCL` / `ALS_INT`           | Light sensing                            | I²C; `INT` on pin 5 → `ALS_INT` net                    |
| SHT4x              | U2                | `I2C_SDA` / `I2C_SCL`                       | Temperature / humidity                   | I²C only, no interrupt routed                          |
| BMP581             | U4                | `I2C_SDA` / `I2C_SCL` / `INT/DNC` (pin 7)   | Pressure                                 | I²C address selected by `JP1` (see I2C bus); INT route **verify** |

Purposes for the radar modules at `J2` and `J3` are inferred from the part
identity printed on the schematic (`Radar; Hi-Link LD2450` and
`Radar; DFRobot SEN0609(C4001)`); the schematic does not annotate the
behaviour of those modules beyond the connector name.

## I2C bus

A single shared I²C bus runs through the board. It enters from the Core via
`J6` and connects to all three on-board I²C devices.

| Net        | Source / direction              | Devices on-board       | Routed to J6 pin |
| ---------- | ------------------------------- | ---------------------- | ---------------- |
| `I2C_SDA`  | From Core, bi-directional       | U1, U2, U4             | 10               |
| `I2C_SCL`  | From Core                       | U1, U2, U4             | 11               |
| `ALS_INT`  | Open-drain output from U1 pin 5 | (interrupt-only)       | 9                |

I²C pull-up resistors are on the Core side of the bus (R21 / R22 10 k on
S360-100-R4); the RoomIQ board does not duplicate them.

### BMP581 INT

The schematic labels U4 pin 7 as `INT/DNC` with the local label `int`. The net
does not appear to be carried out to `J6` on this sheet (`J6` only carries
`ALS_INT`, not a separate BMP581 interrupt). Whether the BMP581 INT is
deliberately left unconnected, locally tied off, or routed via a label that is
not legible in the PDF is **verify**.

### JP1 — BMP581 I²C address strap

`JP1` is a 3-pin jumper that selects the BMP581 I²C address by tying its
`SDO/SA0` pin (U4 pin 5, net `add`) to either +3.3 V or GND. R3 10 k provides a
pull-up to +3.3 V on the `add` net.

The schematic prints the following address table next to `JP1`:

| `JP1` strap   | BMP581 I²C address |
| ------------- | ------------------ |
| GND           | 0x46               |
| VDD (Default) | 0x47               |
| Open          | SPI                |
| Both          | Undef              |

The actual strap position used in production / Release-One hardware is
**verify** — see [Open questions / verification needed](#open-questions--verification-needed).

## Radar / UART signals

Five connector-level signals carry radar data and an auxiliary radar I/O
between the RoomIQ board and the Core:

| Net          | On-board destination            | J6 pin | Notes                                                    |
| ------------ | ------------------------------- | ------ | -------------------------------------------------------- |
| `Hi-Link_RX` | `J2` pin 5 (Hi-Link LD2450)     | 5      | UART line; `RX`/`TX` direction is **verify**             |
| `Hi-Link_TX` | `J2` pin 6 (Hi-Link LD2450)     | 6      | UART line; `RX`/`TX` direction is **verify**             |
| `SEN0609_RX` | `J3` pin (DFRobot SEN0609)      | 2      | UART line; `RX`/`TX` direction is **verify**             |
| `SEN0609_TX` | `J3` pin (DFRobot SEN0609)      | 3      | UART line; `RX`/`TX` direction is **verify**             |
| `out(gpio6)` | `J3` (DFRobot SEN0609)          | 4      | Auxiliary radar I/O; purpose at the SEN0609 side **verify** |

All five of these signals return to the **Sense360 Core** through the RoomIQ
connector `J6` and arrive at the Core's `J10`. From there they map to ESP32
GPIOs as documented in
[`s360-100-r4-core.md`](./s360-100-r4-core.md). This document does not restate
those ESP32 pin assignments — the Core doc remains the source of truth for the
MCU side.

The `RX`/`TX` net names are taken verbatim from the schematic. Whether they
represent the radar module's `RX`/`TX` or the Core's `RX`/`TX` is not annotated
on the sheet; this is captured as a verification item below.

## PIR signal

| Net   | Source         | J6 pin | Notes                                                 |
| ----- | -------------- | ------ | ----------------------------------------------------- |
| `PIR` | U3 pin 2 (OUT) | 8      | EKMC1601111 PIR motion output; pulled by R4 10 k (direction **verify**) |

The PIR output returns to the Core through `J6` pin 8, where it lands on the
`PIR` net documented in the Core reference.

## Light interrupt signal

| Net       | Source         | J6 pin | Notes                                                |
| --------- | -------------- | ------ | ---------------------------------------------------- |
| `ALS_INT` | U1 pin 5 (INT) | 9      | LTR-303ALS-01 ambient-light-sensor interrupt output  |

`ALS_INT` is pulled to +3.3 V by one of `R1 10 k` / `R2 10 k` near `U1`. The
exact assignment of those two resistors (which one pulls `ALS_INT`, and what
the other pulls) is **verify**.

## Power rails

| Rail    | J6 pin | On-board destinations                                              |
| ------- | ------ | ------------------------------------------------------------------ |
| `+5V`   | 1      | `J2` (Hi-Link LD2450), `J3` (DFRobot SEN0609 / C4001)              |
| `+3.3V` | 7      | `U1` (LTR-303ALS-01), `U2` (SHT4x), `U3` (EKMC1601111), `U4` (BMP581) |
| `GND`   | 12     | All on-board components and both radar connectors                   |

The RoomIQ board does **not** generate either rail locally. Both `+5V` and
`+3.3V` are supplied by the Sense360 Core board via `J6` and originate at the
Core's USB / PoE input and on-board buck converter respectively (see
[`s360-100-r4-core.md`](./s360-100-r4-core.md) for the regulator).

Per-rail consumer split:

- **+5 V**: LD2450 connector `J2`, SEN0609 connector `J3`. Decoupled by
  `C1 100 µ` + `C2 100 n` near the radar connectors and `J6`.
- **+3.3 V**: PIR `U3`, ALS `U1`, SHT4x `U2`, BMP581 `U4`. Each device has its
  own local 100 n decoupling cap (`C5`, `C6`, `C8`, `C9`), with an additional
  `C7 1 µ` near `U1`.

## Open questions / verification needed

These items are explicitly out of scope for HW-003 to resolve. They are inputs
to the later Release-One YAML audit PR.

1. **`J6` (RoomIQ) vs `J10` (Core) pin-order discrepancy.** The S360-200-R4
   schematic places `+5V` at `J6` pin 1 and `+3.3V` at `J6` pin 7, with the
   nine signal nets distributed at pins 2–6 and 8–11 and `GND` at pin 12. The
   existing
   [`s360-100-r4-core.md`](./s360-100-r4-core.md) `J10` table places `+3.3V`
   at pin 1 and `+5V` at pin 2 with the signal nets at pins 3–11 and `GND` at
   pin 12. These connectors are nominally a mating pair, so one of the two
   tables is wrong. Reconcile against both schematics and the silkscreen on
   the physical boards before any firmware or cable harness relies on the
   mating pin order. Do **not** edit the Core doc as part of this PR.
2. **BMP581 `INT` routing.** The label `int` is visible at U4 pin 7
   (`INT/DNC`) in the PDF, but the net does not visibly leave the board on
   `J6` (which only carries `ALS_INT`). Confirm whether BMP581 INT is
   deliberately unconnected, locally tied, or routed via a label not legible
   in the PDF.
3. **`out(gpio6)` purpose.** The schematic carries `out(gpio6)` from `J6` pin 4
   to `J3` pin 4 on the DFRobot SEN0609 connector. Confirm whether this is the
   SEN0609 / C4001 dedicated output line, a general-purpose radar I/O exposed
   by the module, or something else.
4. **Radar UART direction (`RX` / `TX` naming).** The nets `Hi-Link_RX`,
   `Hi-Link_TX`, `SEN0609_RX`, `SEN0609_TX` are labelled verbatim in the
   schematic but the sheet does not state whether the names are from the
   Core's perspective or the radar module's perspective. Confirm before any
   firmware UART configuration relies on the directionality.
5. **`JP1` BMP581 address strap** position used in production. The schematic
   shows the four possible states (`GND` → 0x46, `VDD` → 0x47 default, `Open`
   → SPI, `Both` → undefined) but does not commit to one. Confirm which
   position is actually fitted on the Release-One assembly so the firmware I²C
   address (`0x46` vs `0x47`) can be set correctly.
6. **LD2450 / SEN0609 population in Release-One.** Confirm whether both `J2`
   (Hi-Link LD2450) and `J3` (DFRobot SEN0609 / C4001) are populated on the
   Release-One RoomIQ build, or whether one of them is optional / DNP. This
   determines whether both `Hi-Link_*` and `SEN0609_*` UARTs need to be
   configured in firmware simultaneously.
7. **`J2` and `J3` exact pinout.** The 8-pin `J2` clearly carries +5 V,
   `Hi-Link_RX` (pin 5), `Hi-Link_TX` (pin 6), and `GND`; the unused pins are
   not labelled. The 5-pin `J3` carries +5 V, `SEN0609_RX`, `SEN0609_TX`,
   `out(gpio6)`, and `GND`, but the 1-to-5 pin order is not unambiguous in the
   PDF. Confirm both connectors against silkscreen before fabricating cables.
8. **`R1` / `R2` and `R4` exact roles.** The two 10 k resistors near `U1`
   (`R1`, `R2`) and the 10 k near `U3` (`R4`) are clearly biasing networks,
   but the exact assignment (which net each pulls, and the pull direction for
   `R4` on the PIR output) is not unambiguously legible in the PDF.
9. **Firmware package mapping** for `comfort_ceiling.yaml` and
   `presence_ceiling.yaml`. This document does not by itself prove which
   ESPHome package consumes which net on this board. The audit PR must
   reconcile the package YAML against this reference.

## Firmware mapping notes

This document is a hardware reference only. It does not by itself prove that
the ESPHome YAML is correct.

Firmware mappings must be verified in a later audit PR by comparing this
document against:

- [`packages/expansions/comfort_ceiling.yaml`](../../packages/expansions/comfort_ceiling.yaml)
- [`packages/expansions/presence_ceiling.yaml`](../../packages/expansions/presence_ceiling.yaml)
- [`packages/features/comfort_basic_profile.yaml`](../../packages/features/comfort_basic_profile.yaml)
- [`packages/features/presence_basic_profile.yaml`](../../packages/features/presence_basic_profile.yaml)
- [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml)

No claim is made here that any of those files are currently pin-correct for
`S360-200-R4`. HW-003 only documents what the schematic says.

## See also

- [Sense360 Hardware Catalog](../hardware-catalog.md) — canonical board /
  module names, SKUs, revisions, and legacy names.
- [`config/hardware-catalog.json`](../../config/hardware-catalog.json) —
  machine-readable mirror of the catalog (this board's `schematic_status` is
  `verified`, `schematic_file` is `S360-200-R4.pdf`).
- [S360-100-R4 Core Hardware Reference](./s360-100-r4-core.md) — the mating
  Sense360 Core board; `J10` on the Core mates with `J6` on this board.
- [Release-One Configuration](../release-one.md) — the
  Ceiling-POE-VentIQ-FanTRIAC-RoomIQ shipping configuration that consumes the
  RoomIQ board.
- [Repository README](../../README.md) — entry point and documentation index.

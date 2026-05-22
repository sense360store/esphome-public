# S360-312-R4 FanDAC — Standalone Hardware Reference (HW-PINMAP-312-FOLLOWUP)

## Status

**Status: partial — schematic and BOM evidence consolidated; package reconciliation still pending after CORE-ABSTRACT-BUS-001B.**

This document is the per-board hardware reference for the Sense360 DAC
(0–10 V analog) fan board, revision R4 (`S360-312-R4`), produced under
`HW-PINMAP-312-FOLLOWUP`. It follows the per-board reference pattern
of [`s360-200-r4-roomiq.md`](s360-200-r4-roomiq.md),
[`s360-211-r4-ventiq.md`](s360-211-r4-ventiq.md), and
[`s360-300-r4-led.md`](s360-300-r4-led.md), and it complements the
broader HW-PINMAP-312 reconciliation audit at
[`s360-312-r4-dac.md`](s360-312-r4-dac.md).

This doc consolidates two evidence sources:

1. The committed module-side schematic PDF at
   [`docs/hardware/schematics/S360-312-R4.pdf`](schematics/S360-312-R4.pdf)
   (HW-ASSETS-003; SHA256
   `2888f626bfa0139d2190f154f9b02ecf4cb06f2522a5b5802eaf96e16de39e28`;
   122,230 bytes).
2. The newly-supplied **Fan_GP8403 BOM spreadsheet** (`Fan_GP8403.xlsx`,
   19 BOM rows, SHA256
   `1886ecad5b9dd1a683b8c0ccebb770e5c02894854650b5a5553b19875f7e3a20`;
   12,744 bytes). The spreadsheet is **not** committed to the repo by
   this PR; its content is transcribed into the
   [§BOM cross-check](#bom-cross-check) section below per the
   [Hardware Artifact Policy](hardware-artifact-policy.md)
   retained-but-not-committed rule on raw BOM spreadsheets.

The doc records what the schematic + BOM together prove, what they
do **not** prove, and what specific evidence still gates the
`PACKAGE-DAC-001` (alias: `PACKAGE-GAP-001` FanDAC slice) work. It
is **documentation-only**.

## Purpose and scope

This doc does **not**:

- change any value in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json),
  [`config/product-catalog.json`](../../config/product-catalog.json),
  [`config/webflash-builds.json`](../../config/webflash-builds.json),
  [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json),
  [`config/firmware-combination-matrix.json`](../../config/firmware-combination-matrix.json),
  [`config/kit-intent-matrix.json`](../../config/kit-intent-matrix.json),
  or [`config/compile-only-targets.json`](../../config/compile-only-targets.json),
- change any package YAML under [`packages/`](../../packages/),
  including [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)
  or its FanDAC alias
  [`packages/expansions/fan_dac.yaml`](../../packages/expansions/fan_dac.yaml),
- change any product YAML under [`products/`](../../products/) or any
  WebFlash wrapper under [`products/webflash/`](../../products/webflash/),
- change any workflow under `.github/workflows/`, any script under
  [`scripts/`](../../scripts/), any test under [`tests/`](../../tests/),
  any component under `components/`, any header under `include/`,
  or any release artifact / `manifest.json` / `firmware/sources.json`
  / checksums / build-info file,
- mark `S360-312` `verified` — `schematic_status` stays
  `cataloged_unverified`,
- add or change `schematic_file` for `S360-312` in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json),
- mark the pin map confirmed, or mark
  [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)
  as `confirmed-ok` — its status stays `package-yaml-pending`,
- resolve the Core `J7` pin-1 `+5V` vs Module `J1` pin-1 `+3.3V`
  voltage-rail discrepancy — that resolution requires silkscreen /
  bench evidence on the Core side and belongs to
  `S360-100-BENCH-001` + an evidence-bearing HW-PINMAP-312
  follow-up,
- resolve the DIP-switch I²C address-selection mapping
  (`SW1` / `SW2`) on `IC1` / `IC2` to specific 7-bit addresses,
- resolve the `J2` / `J3` Cloudlift S12 output connector
  pin-1-on-silkscreen identity, the pin-1 location relative to
  the terminal-block lever, or the harness conductor mapping to
  the fan,
- decide whether the GP8403 5 V / 10 V output range is exposed
  per-channel, per-DAC, or globally — see
  [§GP8403 output range capability](#gp8403-output-range-capability),
- decide on the firmware/product-selectable behavior between
  GP8403 modes (this is recorded as a future package-design
  decision; see [§Output-channel exposure](#output-channel-exposure)
  and [§Blockers remaining for PACKAGE-DAC-001](#blockers-remaining-for-package-dac-001)),
- claim that simultaneous one-channel-0–5 V and one-channel-0–10 V
  per individual GP8403 is supported (the schematic supplies a
  single `V5V` reference pin per chip wired to `+12V`, not a
  per-channel reference rail),
- promote `S360-312` to `preview` / `stable` / `production`,
- add a `FanDAC` token to any current or future Release-One config
  string,
- add a `FanDAC`-bearing entry to
  [`config/webflash-builds.json`](../../config/webflash-builds.json),
  [`products/`](../../products/), or
  [`products/webflash/`](../../products/webflash/),
- regenerate firmware, create a release, attach a release artifact,
  flip `webflash_build_matrix`, add an `artifact_name`, add a
  compile-only target, change any WebFlash manifest / import,
- relax or change the explicit `FanDAC` ↔ `AirIQ` mutex in
  [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json)
  (`rules.fandac_conflicts_with_airiq: true`),
- relax or change the fan-driver `max-one-of` rule enforced by
  `FAN_DRIVER_TOKENS` in
  [`tests/validate_webflash_builds.py`](../../tests/validate_webflash_builds.py),
- change the Release-One configuration
  `Ceiling-POE-VentIQ-RoomIQ` (`status: production`,
  `channel: stable`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
  `v1.0.0`),
- change the LED preview entry `Ceiling-POE-VentIQ-RoomIQ-LED`
  (stays `status: preview`, `channel: preview`),
- unblock FanTRIAC (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays
  `status: blocked`, `blocker: HW-005`,
  `webflash_build_matrix: false`),
- close `S360-100-BENCH-001`, `HW-PINMAP-311-FOLLOWUP`,
  `HW-PINMAP-320-FOLLOWUP`, or `COMPLIANCE-001`,
- touch the WebFlash repository (`sense360store/WebFlash`) — that
  repo is read-only for the purposes of this PR.

If this reference and any source-of-truth document drift, **the
source-of-truth document wins** and this reference must be
updated. The authoritative artifact-side record for this board is
[`docs/hardware/artifacts/S360-312-R4.md`](artifacts/S360-312-R4.md);
the authoritative Core-side capture lives in
[`docs/hardware/s360-100-r4-core.md`](s360-100-r4-core.md); the
authoritative full pin-map reconciliation audit is
[`docs/hardware/s360-312-r4-dac.md`](s360-312-r4-dac.md).

## Board identity

Mirrored from
[`config/hardware-catalog.json`](../../config/hardware-catalog.json)
lines 82–91 without modification.

| Field | Value |
|---|---|
| `group` | `Inline` |
| `type` | `Driver` |
| `friendly_name` | `Sense360 DAC` |
| `sku` | `S360-312` |
| `rev` | `R4` |
| `old_name` | `Fan_GP8403` |
| `description` | `0 to 10V analog fan driver, for example Cloudlift S12.` |
| `schematic_status` | `cataloged_unverified` (unchanged by this PR) |
| `schematic_file` | _(not set; unchanged by this PR)_ |
| Curated artifact index | [`docs/hardware/artifacts/S360-312-R4.md`](artifacts/S360-312-R4.md) |
| Committed schematic PDF | [`docs/hardware/schematics/S360-312-R4.pdf`](schematics/S360-312-R4.pdf) |
| Per-board reconciliation audit | [`s360-312-r4-dac.md`](s360-312-r4-dac.md) (HW-PINMAP-312) |
| FanDAC package YAML | [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) (dual-channel; `package-yaml-pending`) |
| FanDAC canonical alias | [`packages/expansions/fan_dac.yaml`](../../packages/expansions/fan_dac.yaml) (pure-wrapper alias) |

## Effect of CORE-ABSTRACT-BUS-001B on this board

`CORE-ABSTRACT-BUS-001B-IMPLEMENT-001` landed via PR #569 on
2026-05-22. That slice consolidated the Core / expansion-package
shared I²C bus to a single canonical `core_i2c` bus id
(`GPIO48` SDA / `GPIO45` SCL / `400 kHz`) across the seven in-scope
Core abstract packages and the 10 in-scope expansion-package
`*_i2c_id` consumer defaults — including
[`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml).

The FanDAC-relevant effect is **scoped to the I²C-bus-id layer
only**:

- The `fan_dac_i2c_id` substitution default in
  [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)
  is now `core_i2c` (line 27), and `gp8403.i2c_id: ${fan_dac_i2c_id}`
  (line 43) resolves through the parent Core abstract package to the
  single shared bus on `GPIO48` / `GPIO45`. The header comment block
  (lines 13–18) was updated by PR #569 to reference
  `GPIO48` / `GPIO45`, retiring the previous stale `GPIO39` /
  `GPIO40` claims.
- The FanDAC alias [`packages/expansions/fan_dac.yaml`](../../packages/expansions/fan_dac.yaml)
  is a pure-wrapper alias for `fan_gp8403.yaml` and inherits the
  rebind via its `!include` directive — no separate alias-side edit
  was required by PR #569.

What `CORE-ABSTRACT-BUS-001B` **did not** resolve for FanDAC:

- It did not provide silkscreen / bench / harness evidence for the
  S360-312-R4 board itself.
- It did not measure or document the GP8403 DIP-switch
  (`SW1` / `SW2`) I²C address-selection mapping.
- It did not resolve the Core `J7` pin-1 `+5V` vs Module `J1`
  pin-1 `+3.3V` voltage-rail discrepancy (that is a Core-side
  silkscreen / bench question owned by `S360-100-BENCH-001`).
- It did not resolve the UART0-vs-Nextion arbitration question on
  Module `J1` pins 4 / 5 (`UART_RX` / `UART_TX` shared with
  ESP32 `TXD0` / `RXD0` UART0 / USB boot-log path).
- It did not resolve the `J2` / `J3` Cloudlift S12 output silkscreen
  pin-1 identity.
- It did not decide whether GP8403 output range is exposed
  per-channel, per-DAC, or globally for product-selectable
  behavior — see
  [§GP8403 output range capability](#gp8403-output-range-capability).

Consequently `PACKAGE-DAC-001` is **no longer blocked at the
shared-I²C-bus-naming layer**, but it stays blocked on the
FanDAC-specific evidence enumerated in
[§Blockers remaining for PACKAGE-DAC-001](#blockers-remaining-for-package-dac-001).

## Evidence table

| Evidence | Source | Status |
|---|---|---|
| Module-side schematic PDF | [`docs/hardware/schematics/S360-312-R4.pdf`](schematics/S360-312-R4.pdf) (HW-ASSETS-003; SHA256 `2888f626bfa0139d2190f154f9b02ecf4cb06f2522a5b5802eaf96e16de39e28`; 122,230 bytes) | **Committed.** Byte-identical to upload. Single sheet (`S360-312-R4.kicad_sch`, page 1 / 1). KiCad 10.0.3 export, A4. |
| Module-side BOM spreadsheet | `Fan_GP8403.xlsx` (uploaded; SHA256 `1886ecad5b9dd1a683b8c0ccebb770e5c02894854650b5a5553b19875f7e3a20`; 12,744 bytes; single sheet `Fan_GP8403`; 19 rows incl. header) | **Not committed (raw spreadsheet form).** Content transcribed into [§BOM cross-check](#bom-cross-check) below. Treated under the [Hardware Artifact Policy](hardware-artifact-policy.md) retained-but-not-committed rule for raw BOM spreadsheets. |
| Curated artifact index | [`docs/hardware/artifacts/S360-312-R4.md`](artifacts/S360-312-R4.md) | **Committed.** Schematic-content capture + retained-but-not-committed inventory. |
| HW-PINMAP-312 audit | [`s360-312-r4-dac.md`](s360-312-r4-dac.md) | **Committed.** Full reconciliation audit; this reference doc complements it. |
| Core-side `J7` capture | [`s360-100-r4-core.md` §J7](s360-100-r4-core.md#j7--gp8403-fan-connector-6-pin) | **Committed.** Net list `+5V`, `I2C_SDA`, `I2C_SCL`, `UART_RX`, `UART_TX`, `GND` (no `verify` flag on pin-1 rail value). |
| Core-side shared I²C bus | [`s360-100-r4-core.md` §I2C bus](s360-100-r4-core.md#i2c-bus) | **Committed.** `I2C_SDA` on ESP32 `GPIO48` with `R22 10 kΩ` pull-up; `I2C_SCL` on `GPIO45` with `R21 10 kΩ` pull-up. Single shared bus after `CORE-ABSTRACT-BUS-001B`. |
| Core-side UART0 path | [`s360-100-r4-core.md` §UART buses](s360-100-r4-core.md#uart-buses) line 349 | **Committed.** Records UART0 as the boot-log path on USB. |
| GP8403 public datasheet (general) | Public manufacturer documentation; **not committed**. | **Reference only.** GP8403 is a dual-channel 12-bit DAC controlled over I²C; output range supports 0–5 V and 0–10 V configuration. Range selection is via an I²C configuration register; per-channel vs per-DAC behaviour against this specific board is **not** asserted by this doc beyond the schematic-derived single-`V5V`-per-chip observation in [§GP8403 output range capability](#gp8403-output-range-capability). |
| Silkscreen / harness inspection | _(not provided)_ | **Pending.** Required for Core `J7` ↔ Module `J1` pin-1 identity, Module `J2` / `J3` pin-1 identity, and harness conductor mapping. |
| Bench / scope / I²C capture | _(not provided)_ | **Pending.** Required for GP8403 address measurement, vout0/vout1 analog behaviour at configured range, and Cloudlift S12 functional response. |
| KiCad schematic source / PCB source / project metadata | _(not provided)_ | **Pending.** Source-level pin / net verification gated on this upload. |
| CPL / Gerbers / drill / STEP / board images | _(not provided)_ | **Pending.** Fab / mechanical / visual verification gated on these. |

## Schematic summary

This section restates only what is directly visible in the
committed schematic PDF and inventoried in
[`docs/hardware/artifacts/S360-312-R4.md` §What the schematic appears to contain](artifacts/S360-312-R4.md#what-the-schematic-appears-to-contain).
It does **not** invent transistor topology, electrical timings,
chip-side address-bit ordering, or pull-up assumptions beyond what
is labelled on the sheet.

- **Voltage Boost section.** `MT3608` boost converter (`U1`,
  SOT-23-6 footprint per BOM), input inductor `L1 22 µH` (Bourns
  `SRN6045TA-220M`), Schottky `D1 SS34` (JSMSEMI), input cap
  `C1 22 µF / 0805 / 10 V`, output cap `C2 22 µF / 0805 / 10 V`,
  feedback divider `R1 2 kΩ` / `R2 38 kΩ`, output indicator
  `R9 500 Ω` + blue LED `D6` (OSRAM `LB Q39E-L2OO-35-1`). Input
  rail at the boost converter `IN` pin (pin 5 of MT3608) is
  labelled `+3.3V`; output rail is `+12V`. Feedback divider
  ratio `R2 / R1 = 38 kΩ / 2 kΩ ≈ 19:1` is consistent with an
  MT3608 boosting to ~12 V using an internal ~0.6 V feedback
  reference; no claim on rated output current is made — that
  requires bench evidence and inductor / Schottky thermal
  characterisation.
- **Two GP8403 DAC channels** on the shared I²C bus:
  - **"CLOUDLIFT S12 FAN"** — `IC1 GP8403-TC50-EW`
    (`GP8403-TC50-EW:SOP100P600X165-11N` footprint per BOM;
    Guestgood manufacturer per BOM). Pin / net assignments as
    labelled on the schematic:

    | IC1 pin | Pin name | Net |
    |---:|---|---|
    | 1 | `SCLK` | `I2C_SCL` |
    | 2 | `SDA` | `I2C_SDA` |
    | 3 | `A0` | `A0` (DIP `SW1` position 1; 4.7 kΩ pull-up to `+3.3V`) |
    | 4 | `A1` | `A1` (DIP `SW1` position 2; 4.7 kΩ pull-up to `+3.3V`) |
    | 5 | `VCC` | `+3.3V` (decoupled by `C5 1 µF` + `C3 100 nF`) |
    | 6 | `GND` | `GND` |
    | 7 | `VOUT1` | `vout1` → `C8 10 µF` + `D2` ESD diode → `J2` |
    | 8 | `VOUT0` | `vout0` → `C7 10 µF` + `D4` ESD diode → `J2` |
    | 9 | `A2` | `A2` (DIP `SW1` position 3; 4.7 kΩ pull-up to `+3.3V`) |
    | 10 | `V5V` | `+12V` (boost output) |
    | 11 | `EP` | `GND` (exposed pad to ground) |

  - **"CLOUDLIFT S12 FAN2"** — `IC2 GP8403-TC50-EW`, mirror of
    `IC1`. Pin / net assignments:

    | IC2 pin | Pin name | Net |
    |---:|---|---|
    | 1 | `SCLK` | `I2C_SCL` |
    | 2 | `SDA` | `I2C_SDA` |
    | 3 | `A0` | `2A0` (DIP `SW2` position 1; 4.7 kΩ pull-up to `+3.3V`) |
    | 4 | `A1` | `2A1` (DIP `SW2` position 2; 4.7 kΩ pull-up to `+3.3V`) |
    | 5 | `VCC` | `+3.3V` (decoupled by `C6 1 µF` + `C4 100 nF`) |
    | 6 | `GND` | `GND` |
    | 7 | `VOUT1` | `2vout1` → `C10 10 µF` + `D3` ESD diode → `J3` |
    | 8 | `VOUT0` | `2vout0` → `C9 10 µF` + `D5` ESD diode → `J3` |
    | 9 | `A2` | `2A2` (DIP `SW2` position 3; 4.7 kΩ pull-up to `+3.3V`) |
    | 10 | `V5V` | `+12V` (boost output) |
    | 11 | `EP` | `GND` (exposed pad to ground) |

- **DIP-switch address-selection hardware.** `SW1` and `SW2` are
  each a single 3-position SPST DIP switch (BOM symbol
  `SW_DIP_x03`, manufacturer part `219-3MSTR` from CTS Electronic
  Components). Each pole, when closed, ties the corresponding
  address pin to `GND`; when open, the 4.7 kΩ pull-up holds the
  pin at `+3.3V`. `SW1` drives `IC1` nets `A0` / `A1` / `A2`;
  `SW2` drives `IC2` nets `2A0` / `2A1` / `2A2`. The mapping
  between specific DIP positions and the resulting GP8403 7-bit
  I²C address bits is **not** annotated on the schematic and is
  not asserted by this doc — see
  [§GP8403 address-selection evidence](#gp8403-address-selection-evidence).
- **Cloudlift S12 fan output connectors.** `J2` and `J3` are each
  3-pin Phoenix-compatible terminal blocks (BOM symbol
  `Conn_01x03`, footprint
  `TerminalBlock_Phoenix_PT-1,5-3-3.5-H_1x03_P3.50mm_Horizontal`,
  manufacturer part `MX350-3.5-03P-GN01-Cu-Y-A` from MAX). The
  nets reaching each connector are `vout0`, `vout1`, and `GND`
  (for `J2` driven by `IC1`) and `2vout0`, `2vout1`, and `GND`
  (for `J3` driven by `IC2`). The schematic does **not** label
  the silkscreen pin-1 location or the lever-side orientation of
  the terminal block; see
  [§Output-channel exposure](#output-channel-exposure).
- **"From Core"** connector `J1` — 6-pin JST SH (BOM part
  `SM06B-SRSS-TB(LF)(SN)`, 1.00 mm pitch, horizontal). Net list
  as labelled in the PDF:

  | Module `J1` pin | Net |
  |---:|---|
  | 1 | `+3.3V` |
  | 2 | `I2C_SDA` |
  | 3 | `I2C_SCL` |
  | 4 | `UART_RX` |
  | 5 | `UART_TX` |
  | 6 | `GND` |

- **"NEXTION DISPLAY"** connector `J7` — 4-pin JST PH (BOM part
  `B4B-PH-K-S(LF)(SN)`, 2.00 mm pitch, vertical). Net list:

  | Module `J7` pin | Net |
  |---:|---|
  | 1 | `+5V` (labelled `Vin` on the sheet; source not visible on this single sheet) |
  | 2 | `ESP32_RXD` / `UART_RX` → screen TX |
  | 3 | `ESP32_TXD` / `UART_TX` → screen RX |
  | 4 | `GND` |

- **Decoupling.** `C3 100 nF` on `IC1 VCC`; `C4 100 nF` on `IC2 VCC`.
- **ESD / blocking diodes on outputs.** `D2`, `D3`, `D4`, `D5` are
  each `ESD9B3.3ST5G` ESD-protection diodes in SOD-923 (per BOM
  manufacturer `ElecSuper`). The schematic places one diode per
  vout net, with the cathode towards the output rail and the
  anode at `GND` — consistent with reverse-bias ESD protection
  that conducts only above the diode's breakdown voltage (well
  above the 3.3 V working voltage suffix in the part name); not a
  clamping element under normal 0–10 V operation.
- **Mounting holes.** `H1`, `H2`, `H3`, `H4`.

Everything beyond the list above — module dimensions, layer
stackup, copper pour reference, PCB silkscreen pin-1 markers,
fab notes, harness identity, exact MT3608 thermal headroom, GP8403
internal range register bit mapping, electrical / timing claims
beyond what is printed on the visible sheet — is **unknown** and
would require the retained-but-not-committed KiCad source / PCB /
CPL / Gerbers / drill / STEP / board images or bench evidence per
[`hardware-artifact-policy.md`](hardware-artifact-policy.md).

## Pin / connector reference

### Module-side `J1` ↔ Core-side `J7` (6-pin)

| Pin | Module `J1` net (schematic) | Core `J7` net (per [s360-100-r4-core.md §J7](s360-100-r4-core.md#j7--gp8403-fan-connector-6-pin)) | Reconciliation |
|---:|---|---|---|
| 1 | `+3.3V` | `+5V` | **Voltage-rail discrepancy.** Owned by `S360-100-BENCH-001` + HW-PINMAP-312-FOLLOWUP evidence pass. See [`s360-312-r4-dac.md` §Voltage-rail discrepancy](s360-312-r4-dac.md#voltage-rail-discrepancy). |
| 2 | `I2C_SDA` | `I2C_SDA` | Net-name agrees. Bus is the shared `core_i2c` after PR #569 (`GPIO48` SDA, 10 kΩ pull-up `R22` on Core; 4.7 kΩ pull-ups on this module routed through the GP8403 address-select tree). |
| 3 | `I2C_SCL` | `I2C_SCL` | Net-name agrees. `core_i2c` (`GPIO45` SCL, 10 kΩ pull-up `R21` on Core). |
| 4 | `UART_RX` | `UART_RX` | Net-name agrees. On Core, this routes to ESP32 `RXD0` (pin 36) — UART0, also the USB boot-log path. UART0-vs-Nextion arbitration question remains open; see [§UART0-vs-Nextion arbitration](#uart0-vs-nextion-arbitration). |
| 5 | `UART_TX` | `UART_TX` | Net-name agrees. On Core, this routes to ESP32 `TXD0` (pin 37). |
| 6 | `GND` | `GND` | Net-name agrees. |

Pin-1 silkscreen identity on the Core side and on the module side
is **not** asserted by this doc; the Core `J7` capture in
[`s360-100-r4-core.md`](s360-100-r4-core.md#j7--gp8403-fan-connector-6-pin)
does not currently flag the pin order as `verify` (unlike Core
`J6` for FanPWM, which is flagged), so the question is whether the
Core `J7` capture's pin-1-as-`+5V` is correct or whether silkscreen
inspection will reveal `+3.3V` matching the module side.

### Module-side `J2` (CLOUDLIFT S12 FAN, driven by IC1)

3-pin Phoenix terminal block (`Conn_01x03`,
`MX350-3.5-03P-GN01-Cu-Y-A` per BOM). Nets reaching the connector,
from the schematic:

| Net | Source on IC1 | Path |
|---|---|---|
| `vout0` | `IC1` pin 8 (`VOUT0`) | `IC1.VOUT0` → `C7 10 µF` (output cap) → `D4` ESD-protection → `J2` |
| `vout1` | `IC1` pin 7 (`VOUT1`) | `IC1.VOUT1` → `C8 10 µF` (output cap) → `D2` ESD-protection → `J2` |
| `GND` | board ground | `J2` ground pin |

The schematic visually shows three connector pins on `J2` but does
**not** label the silkscreen pin-1 position relative to the
terminal-block lever, nor does it mark which of the three pins is
the ground reference. Pin-1 identity, lever orientation, and the
harness mapping to the Cloudlift S12 fan input remain
silkscreen / bench questions.

### Module-side `J3` (CLOUDLIFT S12 FAN2, driven by IC2)

3-pin Phoenix terminal block (`Conn_01x03`, identical part to
`J2` per BOM). Nets reaching the connector:

| Net | Source on IC2 | Path |
|---|---|---|
| `2vout0` | `IC2` pin 8 (`VOUT0`) | `IC2.VOUT0` → `C9 10 µF` (output cap) → `D5` ESD-protection → `J3` |
| `2vout1` | `IC2` pin 7 (`VOUT1`) | `IC2.VOUT1` → `C10 10 µF` (output cap) → `D3` ESD-protection → `J3` |
| `GND` | board ground | `J3` ground pin |

Same silkscreen / lever / harness open questions as `J2`.

### Module-side `J7` (NEXTION DISPLAY)

4-pin JST PH (`B4B-PH-K-S(LF)(SN)`, 2.00 mm vertical). Nets:

| Module `J7` pin | Net | Notes |
|---:|---|---|
| 1 | `+5V` (`Vin`) | Schematic label suggests this is an input rail; the source of `+5V` is not visible on this single sheet and is **not** generated by the MT3608 boost (which produces `+12V`). No `+5V` rail is present on Module `J1` (which is `+3.3V` per pin-1 capture). Where the Nextion display's `+5V` comes from is **open**. |
| 2 | `ESP32_RXD` / `UART_RX` | On-board route from Module `J1` pin 4 to Module `J7` pin 2; goes to the Nextion screen's TX line. |
| 3 | `ESP32_TXD` / `UART_TX` | On-board route from Module `J1` pin 5 to Module `J7` pin 3; goes to the Nextion screen's RX line. |
| 4 | `GND` | Common ground. |

### UART0-vs-Nextion arbitration

Module `J1` pins 4 / 5 carry `UART_RX` / `UART_TX`. These nets
route on-board to Module `J7` (the Nextion 4-pin connector). On
the Core side, the same nets bind to ESP32 `TXD0` (pin 37) /
`RXD0` (pin 36) — UART0, which is also the **boot-log path on USB**
per [`s360-100-r4-core.md` §UART buses](s360-100-r4-core.md#uart-buses)
line 349.

[`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)
binds **no** `uart:` block and **no** Nextion `display:` component
on this pair. The package does not, today, claim that a Nextion
display is wired in any product configuration. No bench evidence
has been recorded for the boot-log / deep-sleep / USB-debug /
firmware-over-UART contention scenarios. Resolution belongs to
HW-PINMAP-312-FOLLOWUP plus the `PACKAGE-DAC-001` design decision
on whether the FanDAC package should bind any UART consumer.

## GP8403 address-selection evidence

The schematic shows hardware capable of selecting per-DAC I²C
addresses:

- **Per-DAC pull-ups.** Each address pin on each GP8403 has its
  own 4.7 kΩ pull-up to `+3.3V`:
  - `IC1`: `R3` (A0), `R5` (A1), `R7` (A2). Resistor values per
    BOM row `R3,R4,R5,R6,R7,R8 / 4.7k / R_0402` — UNI-ROYAL part
    `HP02WAF4701TCE`.
  - `IC2`: `R4` (2A0), `R6` (2A1), `R8` (2A2). Same resistor row.
- **Per-DAC DIP switches.** Each GP8403 has its own 3-position
  DIP switch:
  - `SW1` — 3-pole SPST DIP switch (`SW_DIP_x03` per BOM symbol;
    manufacturer part `219-3MSTR` from CTS). Closing a pole ties
    the corresponding `IC1` address pin to `GND`; opening leaves
    it pulled up to `+3.3V`.
  - `SW2` — identical part to `SW1`; same behaviour for `IC2`'s
    `2A0` / `2A1` / `2A2` nets.

| GP8403 | Pull-ups (4.7 kΩ to `+3.3V`) | DIP switch | Address pins |
|---|---|---|---|
| `IC1` (CLOUDLIFT S12 FAN) | `R3` (A0), `R5` (A1), `R7` (A2) | `SW1` (positions 1 / 2 / 3 → A0 / A1 / A2; positions 4 / 5 / 6 → `GND`) | `A0`, `A1`, `A2` (independent of `IC2`) |
| `IC2` (CLOUDLIFT S12 FAN2) | `R4` (2A0), `R6` (2A1), `R8` (2A2) | `SW2` (positions 1 / 2 / 3 → 2A0 / 2A1 / 2A2; positions 4 / 5 / 6 → `GND`) | `2A0`, `2A1`, `2A2` (independent of `IC1`) |

What this proves:

- The two GP8403s are intended to live on the **same shared I²C
  bus** (`core_i2c`) and to be addressed independently via their
  own DIP switches.
- The hardware can drive each DAC to a different 7-bit address
  within whatever address span the GP8403 part variant supports.

What this **does not** prove:

- The exact GP8403-side bit ordering of `A0` / `A1` / `A2` into
  the 7-bit I²C address. The GP8403 public datasheet specifies the
  base address and the address-select bit layout, but this doc
  does **not** assert a specific 7-bit value for any DIP-switch
  configuration. The
  [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)
  `${fan_dac_address}` default is currently `0x58` with alternate
  `0x59` — addressing one DAC only. The package does not, today,
  bind a second `gp8403:` device or a second `${fan_dac_address}`
  for `IC2`.
- Which DIP positions ship from the factory.
- Whether a user-reachable label / silkscreen near `SW1` / `SW2`
  documents the address mapping.

**Bench / silkscreen evidence still required:**

- An I²C bus capture (logic analyser) of an `S360-100-R4` +
  `S360-312-R4` pair under both DIP-switch settings (all-open,
  all-closed, and at least one mixed setting), recording the
  observed 7-bit addresses for each DAC.
- A silkscreen reading of `SW1` and `SW2` (which side is
  position 1, which side is ON vs OFF, any printed labels).
- A datasheet excerpt / reference confirming the GP8403 address
  span and bit ordering, recorded in the audit log.

## Output-channel exposure

Each GP8403 exposes both `VOUT0` (pin 8) and `VOUT1` (pin 7) to
its respective terminal block (`J2` for `IC1`; `J3` for `IC2`).
The board therefore physically wires **four** analog outputs to
two 3-pin connectors:

| Connector | DAC | Channel | GP8403 pin | Schematic net | Output cap | ESD diode | Reaches |
|---|---|---|---|---|---|---|---|
| `J2` | `IC1` | 0 | pin 8 (`VOUT0`) | `vout0` | `C7 10 µF` | `D4` | `J2` |
| `J2` | `IC1` | 1 | pin 7 (`VOUT1`) | `vout1` | `C8 10 µF` | `D2` | `J2` |
| `J3` | `IC2` | 0 | pin 8 (`VOUT0`) | `2vout0` | `C9 10 µF` | `D5` | `J3` |
| `J3` | `IC2` | 1 | pin 7 (`VOUT1`) | `2vout1` | `C10 10 µF` | `D3` | `J3` |

This matches the dual-channel structure already encoded in
[`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)
— but the package binds only **one** GP8403 (`gp8403.id: fan_dac`),
not two. Specifically:

- `gp8403.address: ${fan_dac_address}` (default `0x58`) addresses
  one DAC chip.
- The two `output: platform: gp8403` entries (channels 0 and 1)
  drive both channels of **that one** DAC.
- The package does **not**, today, expose `IC2` as a second
  `gp8403:` device with its own address.

So at the package layer, the active model is "one DAC, two
channels", whereas the schematic + BOM evidence is "two DACs, each
with two channels — four channels total across two terminal-block
connectors". Reconciliation belongs to `PACKAGE-DAC-001` and is
**not** decided by this PR.

Per the user-supplied design decisions for this audit:

- **Both GP8403 channels** of each DAC should be considered
  exposed at the connector level — the schematic confirms this.
- **Possible product use** is one channel per fan / control
  output, with two DACs allowing up to four independent fans on
  one board. The package YAML's two-channel-per-DAC abstraction
  matches one DAC at a time; extending the package to bind both
  DACs is a `PACKAGE-DAC-001` design decision.
- **No claim is made** that one GP8403 can simultaneously drive
  one channel at 0–5 V and one channel at 0–10 V — see
  [§GP8403 output range capability](#gp8403-output-range-capability).

## GP8403 output range capability

The GP8403 public datasheet states that the output range is
configurable between 0–5 V and 0–10 V. The ESPHome `gp8403:`
component models this with a chip-level `voltage:` field (5 V or
10 V), and the
[`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)
substitution `${fan_dac_voltage_mode}` (default `10V`, alternate
`5V`) is bound at the chip level (`gp8403.voltage:` line 45), not
per-channel.

What the **S360-312-R4 schematic shows:**

- Each GP8403 has a single `V5V` pin (pin 10) wired directly to
  `+12V` from the MT3608 boost output. There is no per-channel
  `V5V` rail and no per-channel switching topology that would
  scale the output range independently between `VOUT0` and
  `VOUT1` of the same chip.
- There is **no jumper, solder-bridge, or DIP-switch** visible
  on the schematic for the 5 V / 10 V range selection. Range
  selection appears to be entirely register-driven via I²C.
- This means the stale `fan_gp8403.yaml` header comment
  ("0-10V or 0-5V (jumper selectable on hardware)" — file line 6)
  is, with the current schematic evidence, **not corroborated by
  any visible hardware jumper**. The selection is firmware-driven.

What the **schematic does not show:**

- The internal GP8403 register layout for the range bit (per-chip
  vs per-channel) — that is datasheet-side knowledge.
- Whether the ESPHome `gp8403:` component supports any per-channel
  range override.

**Conservative conclusion (no overclaim):**

- Range is selectable per **chip** (per GP8403), not per channel,
  in the package YAML model used today. The schematic supplies a
  single `V5V` reference per chip.
- With two chips on this board, the board can host two
  independent range domains:
  - `IC1` configured 0–5 V → `J2` channels 0 and 1 both at 0–5 V.
  - `IC1` configured 0–10 V → `J2` channels 0 and 1 both at 0–10 V.
  - `IC2` configured 0–5 V → `J3` channels 0 and 1 both at 0–5 V.
  - `IC2` configured 0–10 V → `J3` channels 0 and 1 both at 0–10 V.
- "Simultaneous one-channel-0–5 V and one-channel-0–10 V" can only
  be achieved by using **one channel from each DAC** (e.g. `J2`
  channel 0 at 0–5 V via `IC1`, `J3` channel 0 at 0–10 V via
  `IC2`). It is **not** achievable on a single GP8403 chip with
  the wiring shown on this schematic.
- The firmware/product-selectable behaviour discussion (whether
  the FanDAC package should support per-DAC range selection,
  per-fan-output range selection, or a single global range) is a
  `PACKAGE-DAC-001` design decision and is **not** resolved by
  this PR.

## BOM cross-check

Every row below is transcribed from the supplied `Fan_GP8403.xlsx`
spreadsheet. Quantities, footprints, manufacturer part numbers
(`MFR#`), and manufacturer names are reproduced verbatim from the
spreadsheet rows. Where a value is **absent** from the spreadsheet
(no value at all), the cell below is marked `_(not provided in
spreadsheet)_` rather than fabricated.

| Reference | Qty | Value | Footprint | MFR# | Manufacturer | Schematic role |
|---|---:|---|---|---|---|---|
| `C1`, `C2` | 2 | `22u/0805/10V` | `Capacitor_SMD:C_0805_2012Metric` | `C2012X5R1A226KT000N` | TDK | Boost-converter input cap (`C1` on `+3.3V` side of `U1 MT3608 IN`) and output cap (`C2` on `+12V` rail). |
| `C3`, `C4` | 2 | `100n` | `Capacitor_SMD:C_0402_1005Metric` | `0402F104M500NT` | FH | GP8403 `VCC` decoupling — `C3` on `IC1`, `C4` on `IC2`. |
| `C5`, `C6` | 2 | `1u` | `Capacitor_SMD:C_0402_1005Metric` | `HGC0402R5105K500NTEJ` | Chinocera | GP8403 `VCC` bulk decoupling — `C5` on `IC1`, `C6` on `IC2`. |
| `C7`, `C8`, `C9`, `C10` | 4 | `10u` | `Capacitor_SMD:C_0402_1005Metric` | `CGA0402X5R106M100GT` | HRE | DAC analog output filter caps — `C7` / `C8` on `IC1.VOUT0` / `IC1.VOUT1`; `C9` / `C10` on `IC2.VOUT0` / `IC2.VOUT1`. |
| `D1` | 1 | `SS34` | `Diode_SMD:D_SMA` | `SS34` | JSMSEMI | Schottky rectifier in the MT3608 boost output path. |
| `D2`, `D3`, `D4`, `D5` | 4 | `ESD9B3.3ST5G` | `Diode_SMD:D_SOD-923` | `ESD9B3.3ST5G-ES` | ElecSuper | ESD-protection diodes on each `vout*` net to `GND`. |
| `D6` | 1 | `Blue` | `LED_SMD:LED_0603_1608Metric` | `LB Q39E-L2OO-35-1` | OSRAM Opto Semicon | Boost-rail indicator LED via `R9 500 Ω` from `+12V`. |
| `IC1`, `IC2` | 2 | `GP8403-TC50-EW` | `GP8403-TC50-EW:SOP100P600X165-11N` | `GP8403-TC50-EW` | Guestgood | The two dual-channel 12-bit I²C DACs that drive the analog fan outputs. **Confirms GP8403 variant `-TC50-EW`** in a 10-pin SOP with exposed pad (11N footprint). |
| `J1` | 1 | `Conn_01x06` | `Connector_JST:JST_SH_SM06B-SRSS-TB_1x06-1MP_P1.00mm_Horizontal` | `SM06B-SRSS-TB(LF)(SN)` | JST | "From Core" 6-pin connector. Horizontal mount, 1.00 mm pitch. |
| `J2`, `J3` | 2 | `Conn_01x03` | `TerminalBlock_Phoenix:TerminalBlock_Phoenix_PT-1,5-3-3.5-H_1x03_P3.50mm_Horizontal` | `MX350-3.5-03P-GN01-Cu-Y-A` | MAX | Cloudlift S12 fan output terminal blocks. 3-position, 3.50 mm pitch, horizontal mount. |
| `J7` | 1 | `JST` | `Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical` | `B4B-PH-K-S(LF)(SN)` | JST | Nextion display 4-pin connector. Vertical mount, 2.00 mm pitch. |
| `L1` | 1 | `22uH` | `Inductor_SMD:L_Bourns_SRN6045TA` | `SRN6045TA-220M` | BOURNS | MT3608 boost inductor. |
| `R1` | 1 | `2k` | `Resistor_SMD:R_0402_1005Metric` | `HPCR0402F2K00K9` | RESI | MT3608 feedback divider (lower leg). |
| `R2` | 1 | `38k` | `Resistor_SMD:R_0402_1005Metric` | `ERJ2RKF3832X` | PANASONIC | MT3608 feedback divider (upper leg). |
| `R3`, `R4`, `R5`, `R6`, `R7`, `R8` | 6 | `4.7k` | `Resistor_SMD:R_0402_1005Metric` | `HP02WAF4701TCE` | UNI-ROYAL | GP8403 address-pin pull-ups. `R3` / `R5` / `R7` for `IC1` `A0` / `A1` / `A2`; `R4` / `R6` / `R8` for `IC2` `2A0` / `2A1` / `2A2`. |
| `R9` | 1 | `500R` | `Resistor_SMD:R_0402_1005Metric` | `HP02WAF5100TCE` | UNI-ROYAL | Blue-LED `D6` current-limit resistor on the `+12V` indicator. |
| `SW1`, `SW2` | 2 | `SW_DIP_x03` | `Button_Switch_SMD:SW_DIP_SPSTx03_Slide_6.7x9.18mm_W6.73mm_P2.54mm_LowProfile_JPin` | `219-3MSTR` | CTS Electronic Components | 3-pole SPST DIP switches for GP8403 address selection. `SW1` drives `IC1`; `SW2` drives `IC2`. |
| `U1` | 1 | `MT3608` | `Package_TO_SOT_SMD:SOT-23-6` | `MT3608` | XI'AN Aerosemi Tech | Step-up boost converter generating the `+12V` rail from `+3.3V`. |

**BOM ↔ schematic cross-check status:**

- `IC1`, `IC2` GP8403 variant `GP8403-TC50-EW` is **confirmed** by
  the BOM `MFR#` column — matches the schematic component label.
- `U1 MT3608` boost converter is **confirmed**.
- `J1` 6-pin JST SH connector identity is **confirmed** as
  `SM06B-SRSS-TB`.
- `J2`, `J3` 3-pin Phoenix-compatible terminal blocks are
  **confirmed** as `MX350-3.5-03P-GN01-Cu-Y-A` (3-position,
  3.50 mm pitch).
- `J7` Nextion 4-pin connector is **confirmed** as
  `B4B-PH-K-S` JST PH 2.0 mm vertical.
- `SW1`, `SW2` are **confirmed** as 3-pole SPST DIP switches
  (`219-3MSTR` from CTS) — the schematic's "6-position" appearance
  is the BOM symbol's 6 contacts (3 poles × 2 contacts each),
  not 6 independent switches.
- The 6× `4.7 kΩ` resistors (`R3`–`R8`) for address-pin pull-ups
  are **confirmed**.
- The `SS34` Schottky and `22 µH` Bourns inductor for the boost
  converter are **confirmed**.
- The 4× `ESD9B3.3ST5G` ESD diodes for `vout*` protection are
  **confirmed**.
- The `+5V` rail at `J7` pin 1 has **no BOM-side source** — there
  is no 5 V regulator, no 5 V battery holder, no 5 V LDO in the
  19 BOM rows. The `+5V` net at `J7` is therefore an **expected
  external supply** rather than a board-generated rail. Whether
  the Core side supplies `+5V` through the Module `J1` connector
  is **the same** Core `J7` pin-1 `+5V` vs Module `J1` pin-1
  `+3.3V` voltage-rail question recorded in
  [`s360-312-r4-dac.md` §Voltage-rail discrepancy](s360-312-r4-dac.md#voltage-rail-discrepancy);
  see also [§Open evidence](#open-evidence-not-resolved-by-this-pr).

**Items the BOM does NOT contain:**

- A 0–5 V vs 0–10 V hardware range-select jumper or solder bridge.
  The BOM rows include no `JP*`, no shunt header, no
  solder-bridge symbol. This corroborates the schematic-side
  conclusion in [§GP8403 output range capability](#gp8403-output-range-capability):
  output range is firmware/register-selected, not
  hardware-selected.
- A 5 V regulator / LDO / DC-DC for the Nextion `+5V` rail.
  Confirms that `+5V` at `J7` is an external input.
- A DIP-switch label / silkscreen-only reference. The DIP switch
  positions remain un-mapped to specific 7-bit I²C addresses at
  the BOM level.
- Any address-resistor selection (no jumper-strap addressing).

## Open evidence (not resolved by this PR)

These items remain **pending** before `PACKAGE-DAC-001` can land.
They are not resolved by this PR or by `CORE-ABSTRACT-BUS-001B`.

1. **GP8403 DIP-switch position ↔ 7-bit I²C address mapping**
   for both `IC1` (`SW1` → `A0` / `A1` / `A2`) and `IC2`
   (`SW2` → `2A0` / `2A1` / `2A2`). Requires either a datasheet
   reference recorded in this audit or a logic-analyser bench
   capture against a populated board.
2. **Whether output range selection is global, per-DAC, or
   per-channel** (`PACKAGE-DAC-001` design decision). The
   schematic-side evidence (one `V5V` per chip, hardwired to
   `+12V`) restricts range selection to **per-DAC at best**;
   per-channel range is not a hardware capability of this board
   as drawn.
3. **Module `J1` pin-1 silkscreen** — confirm whether it is
   physically labelled `+3.3V` (matching the schematic) or `+5V`
   (matching the Core `J7` capture). Resolves the voltage-rail
   discrepancy together with the Core-side silkscreen.
4. **Module `J2` / `J3` silkscreen pin-1 location and lever
   orientation.** Resolves which physical terminal-block screw is
   `vout0`, which is `vout1`, and which is `GND`, and the
   harness wiring direction.
5. **UART0-vs-Nextion arbitration.** Whether a FanDAC build can
   share UART0 with USB boot-log output, or whether the Nextion
   path on `J7` is mutually exclusive with USB debugging. Today
   the package binds no `uart:` / `display:` component on the
   pair; the question is what to do when a future product wants
   to use the Nextion display on `J7`.
6. **Cloudlift S12 functional response** at the configured
   `${fan_dac_voltage_mode}`. Bench capture against an actual
   Cloudlift S12 fan.
7. **`+5V` source for the Nextion `J7` pin 1.** Whether `+5V`
   arrives via the same Core ↔ module harness (in which case
   the Core `J7` capture's pin-1 `+5V` is the explanation), via
   a separate cable, or via an external supply.
8. **GP8403 datasheet excerpt** confirming the 7-bit address
   span, the `A0` / `A1` / `A2` bit ordering, and the range-
   selection register layout. Recorded in this audit (path /
   citation) or in [`docs/hardware/artifacts/S360-312-R4.md`](artifacts/S360-312-R4.md).
9. **KiCad source / PCB source / project metadata / CPL /
   Gerbers / drill / STEP / board images** for source-level
   verification. None are present in the upload.
10. **`tests/test_fandac_alias_packages.py` regression coverage**
    is in place for the alias-wrapper invariants, but no
    pin-pinning test exists for the FanDAC-side bindings (the
    way `tests/test_core_abstract_bus.py` covers Core-side
    pin / bus identity). Adding such coverage belongs to
    `PACKAGE-DAC-001`.

## Blockers remaining for PACKAGE-DAC-001

After `CORE-ABSTRACT-BUS-001B` (PR #569), `PACKAGE-DAC-001`
(alias: `PACKAGE-GAP-001` FanDAC slice) **no longer blocks** on
the shared-I²C-bus rename — `fan_gp8403.yaml` now defaults
`fan_dac_i2c_id` to `core_i2c` and inherits the single shared bus
from the parent Core abstract packages.

`PACKAGE-DAC-001` **still blocks on:**

| # | Blocker | Owner | Evidence required |
|---:|---|---|---|
| 1 | GP8403 DIP-switch ↔ I²C-address mapping for `IC1` (`SW1`) and `IC2` (`SW2`). | `HW-PINMAP-312-FOLLOWUP` evidence pass. | GP8403 datasheet citation + bench logic-analyser capture against an `S360-100-R4` + `S360-312-R4` pair under at least three DIP-switch settings, recorded with operator / date. |
| 2 | Whether the package YAML should bind **both** GP8403s (one `gp8403:` per chip with distinct `${fan_dac_address}` and `${fan_dac_address_2}`) or stay at the current "one DAC, two channels" abstraction. | `PACKAGE-DAC-001` design decision. | Decision recorded in audit log + `fan_gp8403.yaml` reconciliation against the chosen abstraction. |
| 3 | Output-range selection mechanism — global vs per-DAC vs per-channel. | `PACKAGE-DAC-001` design decision. | This audit's [§GP8403 output range capability](#gp8403-output-range-capability) conclusion plus GP8403 datasheet excerpt confirming the chip-level range-register layout. |
| 4 | `J2` / `J3` Cloudlift S12 output connector silkscreen pin-1 identity and harness mapping. | `HW-PINMAP-312-FOLLOWUP` evidence pass. | Operator-attested silkscreen reading + harness conductor-by-conductor trace, recorded with date. |
| 5 | Whether both `VOUT0` and `VOUT1` of a single GP8403 are intended to be exposed simultaneously (the schematic shows both routed to the same 3-pin connector), and whether external installation guidance is needed. | `PACKAGE-DAC-001` + product/installation docs. | Product-design decision documented; package YAML reflects it. |
| 6 | BOM part-number confirmation against shipping units. | `HW-PINMAP-312-FOLLOWUP` evidence pass. | Already partially closed by this PR (BOM spreadsheet content recorded); remaining gap is matching the BOM rows against a populated board. |
| 7 | Firmware behavior decision for 0–5 V / 0–10 V selection — what does the product expose to the end-user (`select`? automatic per-fan-type?)? | `PRODUCT-DAC-001` design decision. | Decision recorded once `PACKAGE-DAC-001` is unblocked. |
| 8 | Module `J1` pin-1 `+3.3V` vs Core `J7` pin-1 `+5V` voltage-rail discrepancy. | `S360-100-BENCH-001` + `HW-PINMAP-312-FOLLOWUP`. | Operator-attested silkscreen reading on both ends + harness inspection. |
| 9 | UART0-vs-Nextion arbitration if a product wants to use the Nextion display. | `PACKAGE-DAC-001` + `PRODUCT-DAC-001`. | Bench characterisation + product-design decision. |
| 10 | Compile-only and package-level test coverage for `fan_gp8403.yaml` / `fan_dac.yaml` after evidence closure. | `FW-COMPILE-DAC-001` (future) once `PACKAGE-DAC-001` lands. | `python3 scripts/validate_compile_targets.py` + `esphome config` pass against a compile-only target carrying `FanDAC`. |

## What CORE-ABSTRACT-BUS-001B unblocked vs what remains blocked

| Item | Pre-PR-#569 status | Post-PR-#569 status | Changed by this PR? |
|---|---|---|---|
| `fan_gp8403.yaml` shared-I²C-bus binding | `${fan_dac_i2c_id}` default `i2c0`, with ceiling form-factor override needed to reach the schematic-correct bus. | `${fan_dac_i2c_id}` default `core_i2c` — single shared bus on `GPIO48` / `GPIO45` inherited from any Core abstract package. | No (already done by PR #569). |
| `PACKAGE-DAC-001` shared-I²C-bus-naming blocker | Blocked. | Unblocked at the bus-naming layer. | No (carry-over from PR #569). |
| `PACKAGE-DAC-001` FanDAC-specific evidence blockers | All 10 items in the table above blocked. | All 10 items still blocked. | No — this PR records evidence, it does not implement `PACKAGE-DAC-001`. |
| `S360-312` `schematic_status` in [`config/hardware-catalog.json`](../../config/hardware-catalog.json) | `cataloged_unverified`. | `cataloged_unverified`. | No (still gated on HW-PINMAP-312-FOLLOWUP closure). |
| `schematic_file` for `S360-312` | not set. | not set. | No. |
| `S360-312` Sense360 DAC row in [`docs/hardware/board-readiness-matrix.md`](board-readiness-matrix.md) | `partially-documented` + `package-yaml-pending`. | `partially-documented` + `package-yaml-pending`. | No. |
| `fan_gp8403.yaml` row in [`docs/hardware/package-readiness-matrix.md`](package-readiness-matrix.md) | `needs-package-reconciliation` + `bench-evidence-pending`. | `needs-package-reconciliation` + `bench-evidence-pending`. | Notes refreshed by this PR (still blocked). |
| Release-One config | `Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`. | `Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`. | No. |
| LED preview path | `Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`. | `Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`. | No. |
| FanTRIAC | `blocked` / `HW-005`. | `blocked` / `HW-005`. | No. |
| `FanDAC` ↔ `AirIQ` mutex | `rules.fandac_conflicts_with_airiq: true`. | `rules.fandac_conflicts_with_airiq: true`. | No. |
| Fan-driver `max-one-of` rule | Enforced via `FAN_DRIVER_TOKENS` in [`tests/validate_webflash_builds.py`](../../tests/validate_webflash_builds.py). | Same. | No. |
| FanDAC WebFlash exposure | Not WebFlash-ready ([`webflash-exposure-readiness-matrix.md`](../webflash-exposure-readiness-matrix.md) §FanDAC / S360-312). | Same. | No. |
| FanDAC release readiness | Not release-ready ([`release-artifact-readiness-matrix.md`](../release-artifact-readiness-matrix.md) §FanDAC / S360-312). | Same. | No. |
| WebFlash repository | Untouched. | Untouched. | No (out of scope for this PR). |

## See also

- [`docs/hardware/s360-312-r4-dac.md`](s360-312-r4-dac.md) — full
  HW-PINMAP-312 reconciliation audit; the source-of-truth for the
  open reconciliation flags.
- [`docs/hardware/artifacts/S360-312-R4.md`](artifacts/S360-312-R4.md)
  — HW-ASSETS-003 curated artifact index.
- [`docs/hardware/schematics/S360-312-R4.pdf`](schematics/S360-312-R4.pdf)
  — committed module-side schematic PDF.
- [`docs/hardware/s360-100-r4-core.md`](s360-100-r4-core.md) —
  Core schematic-backed reference; §J7 GP8403 fan connector (6-pin);
  §I²C bus (`GPIO48` / `GPIO45` with 10 kΩ pull-ups);
  §UART buses (UART0 also boot-log on USB); §S360-100-BENCH-001
  status.
- [`docs/hardware/hardware-artifact-policy.md`](hardware-artifact-policy.md)
  — per-board artifact-index schema and retained-but-not-committed
  policy.
- [`docs/hardware/board-readiness-matrix.md`](board-readiness-matrix.md)
  — per-board readiness across hardware-evidence and productization
  axes; `S360-312` row.
- [`docs/hardware/package-readiness-matrix.md`](package-readiness-matrix.md)
  — `fan_gp8403.yaml` row; updated by this PR.
- [`docs/hardware/firmware-package-mapping-audit.md`](firmware-package-mapping-audit.md)
  — HW-009 / HW-010 six-label package classification; updated by
  this PR for the FanDAC slice.
- [`docs/hardware/core-abstract-bus-reconciliation.md`](core-abstract-bus-reconciliation.md)
  — `CORE-ABSTRACT-BUS-001*` slice plan; records the
  `CORE-ABSTRACT-BUS-001B-IMPLEMENT-001` (PR #569) landing.
- [`docs/release-one-hardware-audit.md`](../release-one-hardware-audit.md)
  — Required follow-ups #2 / #3, owner of `CORE-ABSTRACT-BUS-001`.
- [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)
  — dual-channel FanDAC package (not edited by this PR).
- [`packages/expansions/fan_dac.yaml`](../../packages/expansions/fan_dac.yaml)
  — FanDAC pure-wrapper alias (not edited by this PR).
- [`tests/test_core_abstract_bus.py`](../../tests/test_core_abstract_bus.py)
  — pin-pinning / shared-I²C-bus regression scaffold (not edited
  by this PR).
- [`tests/test_fandac_alias_packages.py`](../../tests/test_fandac_alias_packages.py)
  — FanDAC alias-wrapper regression scaffold (not edited by this PR).
- [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  — `S360-312` row at lines 82–91 (not edited by this PR).
- [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json)
  — `FanDAC` reserved in `canonical_modules`; `FanDAC` ↔ `AirIQ`
  mutex (`rules.fandac_conflicts_with_airiq: true`).

## HW-PINMAP-312-FOLLOWUP audit log

This section is the dated investigation log for this standalone
reference doc. Each row records the docs / evidence change
recorded against the schematic + BOM. An audit-log entry **does
not** by itself promote the top-line status of
[`s360-312-r4-dac.md`](s360-312-r4-dac.md), close any
reconciliation row in
[`s360-312-r4-dac.md`](s360-312-r4-dac.md#known-unresolved-issues),
change [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)
from `package-yaml-pending`, change the JSON `schematic_status` of
`S360-312` from `cataloged_unverified`, set `schematic_file` for
`S360-312`, advance any of the named follow-up PRs
(`HW-PINMAP-312-FOLLOWUP`, `S360-312 schematic_status` promotion,
`PACKAGE-DAC-001`, `PRODUCT-DAC-001`, `WEBFLASH-DAC-001`,
`RELEASE-DAC-001`, `WF-IMPORT-DAC-001`), advance any other
`CORE-ABSTRACT-BUS-001*` slice, close `S360-100-BENCH-001`,
`HW-PINMAP-311-FOLLOWUP`, `HW-PINMAP-320-FOLLOWUP`, or
`COMPLIANCE-001`, change Release-One, change the LED preview path,
unblock FanTRIAC (HW-005), relax or change the `FanDAC` ↔ `AirIQ`
mutex, or relax or change the fan-driver `max-one-of` rule.

| Audit date | Scope | Files inspected | Outcome |
|---|---|---|---|
| 2026-05-22 | HW-PINMAP-312-FOLLOWUP — consolidate schematic + BOM evidence in a standalone per-board reference doc after `CORE-ABSTRACT-BUS-001B-IMPLEMENT-001` (PR #569). The user supplied the same module-side schematic PDF (byte-identical to the already-committed schematic; SHA256 `2888f626bfa0139d2190f154f9b02ecf4cb06f2522a5b5802eaf96e16de39e28`) plus a **new** BOM spreadsheet (`Fan_GP8403.xlsx`; SHA256 `1886ecad5b9dd1a683b8c0ccebb770e5c02894854650b5a5553b19875f7e3a20`; 12,744 bytes; 19 rows incl. header) that had not previously been recorded in the repo. Decisions recorded: (i) target board `S360-312-R4`; (ii) FanDAC output behavior to be firmware/product-selectable (deferred to `PACKAGE-DAC-001`); (iii) supported ranges are GP8403's 0–5 V and 0–10 V; (iv) both GP8403 channels per chip are intended to be exposed at the connector; (v) no claim of simultaneous one-channel-0–5 V + one-channel-0–10 V on a single GP8403, because the schematic shows one `V5V` reference per chip wired to `+12V`. Inspected the schematic content already captured in [`docs/hardware/artifacts/S360-312-R4.md`](artifacts/S360-312-R4.md), the HW-PINMAP-312 audit at [`s360-312-r4-dac.md`](s360-312-r4-dac.md), the Core-side capture at [`s360-100-r4-core.md`](s360-100-r4-core.md), the `CORE-ABSTRACT-BUS-001B` landing at [`core-abstract-bus-reconciliation.md`](core-abstract-bus-reconciliation.md), and the current FanDAC package YAML at [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml). | Schematic PDF byte-identical to upload (SHA256 `2888f626bfa0139d2190f154f9b02ecf4cb06f2522a5b5802eaf96e16de39e28`; 122,230 bytes); `Fan_GP8403.xlsx` BOM spreadsheet (SHA256 `1886ecad5b9dd1a683b8c0ccebb770e5c02894854650b5a5553b19875f7e3a20`; 12,744 bytes; 19 rows transcribed under [§BOM cross-check](#bom-cross-check)); [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) (dual-channel; `fan_dac_i2c_id: core_i2c` default line 27; `gp8403.i2c_id: ${fan_dac_i2c_id}` line 43; `gp8403.address: ${fan_dac_address}` default `0x58` line 28; `gp8403.voltage: ${fan_dac_voltage_mode}` default `10V` line 31; two `output.platform: gp8403` channels 0 and 1; two `fan.platform: speed` entities); [`packages/expansions/fan_dac.yaml`](../../packages/expansions/fan_dac.yaml) (pure-wrapper alias); [`s360-100-r4-core.md` §J7](s360-100-r4-core.md#j7--gp8403-fan-connector-6-pin), §[I2C bus](s360-100-r4-core.md#i2c-bus), §[UART buses](s360-100-r4-core.md#uart-buses); this document. | **New file landed.** Created `docs/hardware/s360-312-r4-fandac.md` as the standalone schematic-backed reference doc that the HW-PINMAP-312 audit at [`s360-312-r4-dac.md` open question (x)](s360-312-r4-dac.md#hw-pinmap-312-followup-audit-log) had explicitly anticipated. **No package / product / WebFlash / catalog / release / firmware / test / WebFlash-wrapper edit.** [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) byte-identical. [`packages/expansions/fan_dac.yaml`](../../packages/expansions/fan_dac.yaml) byte-identical. `S360-312` `schematic_status` stays `cataloged_unverified`. `schematic_file` for `S360-312` stays unset. The `fan_gp8403.yaml` row in [`docs/hardware/package-readiness-matrix.md`](package-readiness-matrix.md) stays `needs-package-reconciliation` + `bench-evidence-pending` (notes refreshed by this PR to point at this new reference doc). [`docs/hardware/firmware-package-mapping-audit.md`](firmware-package-mapping-audit.md) notes for the FanDAC slice are refreshed to point at this new reference doc. `PACKAGE-DAC-001` (alias: `PACKAGE-GAP-001` FanDAC slice) is **no longer blocked at the shared-I²C-bus-naming layer** (carry-over from PR #569) but **stays blocked** on the 10 items enumerated in [§Blockers remaining for PACKAGE-DAC-001](#blockers-remaining-for-package-dac-001). `PRODUCT-DAC-001`, `WEBFLASH-DAC-001`, `RELEASE-DAC-001`, and `WF-IMPORT-DAC-001` stay blocked behind `PACKAGE-DAC-001`. No FanDAC-bearing entry exists in [`config/product-catalog.json`](../../config/product-catalog.json), [`config/webflash-builds.json`](../../config/webflash-builds.json), [`products/`](../../products/), or [`products/webflash/`](../../products/webflash/). `FanDAC` stays reserved in [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json) `canonical_modules` subject to the fan-driver `max-one-of` rule and the explicit `FanDAC` ↔ `AirIQ` mutex (`rules.fandac_conflicts_with_airiq: true`). `S360-100-BENCH-001`, `HW-PINMAP-311-FOLLOWUP`, `HW-PINMAP-320-FOLLOWUP`, and `COMPLIANCE-001` are not closed by this PR. Release-One stays `Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`. LED preview stays `Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`. FanTRIAC stays `blocked` / `HW-005`. The WebFlash repository (`sense360store/WebFlash`) is untouched. |

The next audit-log entry against this doc should appear when
committed evidence is added to the repository that closes any of
the [§Blockers remaining for PACKAGE-DAC-001](#blockers-remaining-for-package-dac-001)
items — for example, a logic-analyser DIP-switch I²C address
capture, a silkscreen reading of `J1` / `J2` / `J3`, a Core-side
`J7` bench reading that resolves the `+5V` / `+3.3V` rail
discrepancy, a GP8403 datasheet excerpt added under
`docs/hardware/`, or KiCad source for source-level pin
verification.

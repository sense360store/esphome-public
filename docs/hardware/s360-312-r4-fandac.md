# S360-312-R4 FanDAC — Standalone Hardware Reference (HW-PINMAP-312-FOLLOWUP)

## Status

**Status: package-layer implemented — schematic / BOM / datasheet / layout evidence consolidated and the FanDAC package reconciled at the package layer by `PACKAGE-DAC-001-IMPLEMENT-001` (2026-05-23). Product / WebFlash / release readiness remains blocked.**

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
| FanDAC package YAML | [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) (two GP8403 chips / four outputs; package-layer reconciled by `PACKAGE-DAC-001-IMPLEMENT-001`, 2026-05-23) |
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

## FANDAC-I2C-ADDR-001 — room-bundle FanDAC + air-quality address requirement

`ROOM-BUNDLE-FAN-CONFIGS-001` builds full-composition room-bundle preview
configs that compose the FanDAC package **alongside an air-quality module**
(`Ceiling-POE-VentIQ-FanDAC-RoomIQ`, `Ceiling-POE-AirIQ-FanDAC-RoomIQ`). That
exposes a hard I²C-address collision on the shared `core_i2c` bus:

| Device | Default I²C address |
|---|---|
| GP8403 IC1 (FanDAC, `SW1`) | `0x58` |
| GP8403 IC2 (FanDAC, `SW2`) | `0x59` |
| SGP41 VOC/NOx (VentIQ **and** AirIQ) | `0x59` |

The FanDAC second DAC (IC2) and the air-quality SGP41 both default to `0x59`,
so they cannot coexist unmodified. The `fandac_conflicts_with_airiq` rule in
[`config/webflash-compatibility.json`](../../config/webflash-compatibility.json)
records this for AirIQ and keeps AirIQ+FanDAC out of the WebFlash one-click
grammar (the one-click surface cannot set a DIP switch).

**Resolution (firmware side, landed):** the room-bundle FanDAC bundles
override `fan_dac_2_i2c_address: "0x5A"` so IC2 moves off `0x59`. GP8403
supports the `0x58`–`0x5F` span via its `A0`/`A1`/`A2` address pins, selected
by the on-board DIP switch. The required map when an air-quality module is
present is:

- GP8403 IC1 (`SW1`): `0x58` (unchanged)
- GP8403 IC2 (`SW2`): `0x5A` (**required**; `0x59` is **forbidden** here)
- SGP41: `0x59` (fixed; owned by the air-quality module)

**FANDAC-I2C-ADDR-001 (hardware follow-up — PENDING):** physically verify, on
a populated `S360-100-R4` + `S360-312-R4` pair with a VentIQ/AirIQ module
present, that the IC2 DIP switch (`SW2`) position selected for these bundles
actually yields `0x5A` (and IC1/`SW1` yields `0x58`) on `core_i2c`, with the
SGP41 still answering at `0x59` and no bus contention. This requires a
GP8403 datasheet DIP-position → 7-bit-address citation **or** a logic-analyser
bench capture recorded with operator / date. Until it lands, the two room-bundle
FanDAC configs stay **advanced / manual preview, compile-pending** behind the
documented switch requirement — no hardware / bench / compliance proof is
claimed. (This is a superset of Open-evidence item 1 below, scoped to the
specific `0x5A` requirement the room-bundle DAC configs depend on.)

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
| 10 | Compile-only and package-level test coverage for `fan_gp8403.yaml` / `fan_dac.yaml` after evidence closure. | **`FW-COMPILE-DAC-001` (this PR)** — metadata layer landed; compile layer pending CI. | **Partially addressed.** `FW-COMPILE-DAC-001` adds the `ceiling-poe-fandac-compile-only` target (`products/compile-only/ceiling-poe-fandac.yaml`, config string `Ceiling-POE-FanDAC`) and resolves the gp8403 `voltage:` enum (`0-10V` → `10V`; see [§Output-range policy — row 6](#output-range-policy--row-6-closed) and the audit-log entry below). `python3 scripts/validate_compile_targets.py --metadata-only` passes; the `--compile` / `esphome config` pass is **owed to CI** and not claimed locally. |

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

## PACKAGE-DAC-001 readiness refresh

This section is the **PACKAGE-DAC-001-READINESS-REFRESH** re-evaluation
of the 10 FanDAC-specific blockers enumerated in
[§Blockers remaining for PACKAGE-DAC-001](#blockers-remaining-for-package-dac-001),
performed after `CORE-ABSTRACT-BUS-001B-IMPLEMENT-001` (PR #569) and
`HW-PINMAP-312-FOLLOWUP` (PR #570) both landed on 2026-05-22. The
goal is to separate **resolved evidence** from **remaining package
design decisions** and to record a clear next-action recommendation.

This refresh is **documentation only**. It does **not** edit
[`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)
or
[`packages/expansions/fan_dac.yaml`](../../packages/expansions/fan_dac.yaml),
does **not** implement `PACKAGE-DAC-001`, does **not** add a DAC
product YAML or a WebFlash wrapper, does **not** flip
`webflash_build_matrix`, does **not** add an `artifact_name`, does
**not** add a compile-only target, does **not** claim DAC product /
WebFlash / release readiness, and does **not** claim simultaneous
per-channel 0–5 V and 0–10 V on a single GP8403. It does **not**
touch the WebFlash repository.

### Readiness table

The 10 readiness rows below mirror the 10-row blocker table in
[§Blockers remaining for PACKAGE-DAC-001](#blockers-remaining-for-package-dac-001).
Each row records the **previous state**, the **current state after
PR #569 + PR #570**, the **evidence**, whether the row **still
blocks** `PACKAGE-DAC-001`, and **what unblocks it**.

| # | Blocker | Previous state | Current state | Evidence | Still blocks `PACKAGE-DAC-001`? | What unblocks it |
|---:|---|---|---|---|---|---|
| 1 | Shared I²C bus naming for `fan_gp8403.yaml` / `fan_dac.yaml`. | `${fan_dac_i2c_id}` default `i2c0`; ceiling form-factor override required to reach the schematic-correct bus. | **Resolved.** `${fan_dac_i2c_id}` default `core_i2c` (line 27 of [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)); resolves through any Core abstract package to the single shared bus on `GPIO48` SDA / `GPIO45` SCL / 400 kHz. | PR #569 (`CORE-ABSTRACT-BUS-001B-IMPLEMENT-001`); `SharedI2CBusTests` (13 cases) in [`tests/test_core_abstract_bus.py`](../../tests/test_core_abstract_bus.py). | **No.** | Already unblocked. |
| 2 | GP8403 BOM identity (`IC1` / `IC2` variant). | Schematic showed two `GP8403-TC50-EW`-labelled DACs; BOM not on file. | **Resolved.** `IC1` and `IC2` both `GP8403-TC50-EW` (Guestgood); SOP-100P600X165-11N footprint per BOM. | PR #570 — [§BOM cross-check](#bom-cross-check) `IC1`, `IC2` rows. | **No.** | Already unblocked. |
| 3 | DIP-switch I²C address-selection mapping for `IC1` (`SW1` → `A0` / `A1` / `A2`) and `IC2` (`SW2` → `2A0` / `2A1` / `2A2`). | DIP-switch hardware and pull-up topology not committed; no DIP-position-to-I²C-address truth table. | **Partially resolved.** Hardware is BOM-confirmed: `SW1` / `SW2` are 3-pole SPST DIP switches (`219-3MSTR` from CTS); the six `4.7 kΩ` pull-ups `R3` / `R5` / `R7` (`IC1`) and `R4` / `R6` / `R8` (`IC2`) on the `A0` / `A1` / `A2` / `2A0` / `2A1` / `2A2` nets are BOM-confirmed (`HP02WAF4701TCE` from UNI-ROYAL). The DIP-position → 7-bit I²C address truth table is still **not** committed — needs a GP8403 datasheet excerpt under `docs/hardware/` **or** a logic-analyser bench scan recorded with operator / date. | PR #570 — [§GP8403 address-selection evidence](#gp8403-address-selection-evidence) and [§BOM cross-check](#bom-cross-check) `SW1`/`SW2` and `R3`–`R8` rows. | **Yes.** Required before any package edit that binds a second `gp8403:` device or that widens the `${fan_dac_address}` allowed-values set beyond the current `0x58` / `0x59`. | GP8403 datasheet excerpt (path + citation recorded in [`docs/hardware/artifacts/S360-312-R4.md`](artifacts/S360-312-R4.md)) **or** an operator-attested logic-analyser bench capture against a populated `S360-100-R4` + `S360-312-R4` pair under at least three DIP-switch settings (all-open, all-closed, one mixed). |
| 4 | Number of DAC chips and channels (board-level capacity). | Schematic-derived inference of two GP8403 chips on a shared bus; no BOM confirmation. | **Evidence captured.** Two `GP8403-TC50-EW` chips (`IC1` / `IC2`), each with two outputs (`VOUT0` / `VOUT1`); **four** analog channels total wired to two 3-pin Phoenix-compatible terminal blocks (`J2` for `IC1`; `J3` for `IC2`). Active YAML binds **one** GP8403 only (`gp8403.id: fan_dac`, single `${fan_dac_address}` default `0x58` / alternate `0x59`); the second chip is not exposed by the package today. **Package design decision still owed** between (a) keep "one logical FanDAC, two channels"; (b) bind both GP8403s as separate devices each with its own `${fan_dac_address*}`; (c) expose four logical outputs / four `fan:` entities. | PR #570 — [§Output-channel exposure](#output-channel-exposure) table; [§BOM cross-check](#bom-cross-check) `IC1`, `IC2`, `J2`, `J3` rows. | **Yes** — at the package-abstraction layer (the design decision must be recorded before any YAML edit). The board-level capacity itself is **no longer in evidential dispute**. | A `PACKAGE-DAC-001` package-design decision recorded in the audit log; the decision is bounded by row 3 (cannot expose two GP8403s without their I²C addresses) and by row 8 (cannot map a `fan:` entity to a physical Cloudlift S12 fan without `J2` / `J3` silkscreen / harness evidence). |
| 5 | Output range selection mechanism (5 V vs 10 V). | Stale header comment in [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) line 6 ("0-10V or 0-5V (jumper selectable on hardware)") not corroborated by any committed evidence. | **Evidence captured.** Range selection is **firmware/register-driven only**: each chip's `V5V` reference pin (pin 10) is hardwired to `+12V` (MT3608 boost output); the 19-row BOM contains **no** range-select jumper, solder bridge, or shunt header. The stale "jumper selectable on hardware" comment in `fan_gp8403.yaml` is therefore disagreement-on-paper rather than a runtime bug (the active YAML body resolves `${fan_dac_voltage_mode}` to `gp8403.voltage:` at the chip level — line 45 — without referencing any jumper). | PR #570 — [§GP8403 output range capability](#gp8403-output-range-capability) and [§BOM cross-check](#bom-cross-check) §"Items the BOM does NOT contain" bullet. | **Yes** — but only at the comment-correction layer. Any `fan_gp8403.yaml` edit must update the stale "jumper selectable on hardware" comment to "firmware/register-driven only (per board evidence)". | A `PACKAGE-DAC-001-IMPLEMENT-001` package edit that corrects the comment; or a documentation-only PR. **Cannot** be flipped to "no longer blocks" until the comment is actually corrected in YAML. |
| 6 | Output range policy (per-product / per-firmware behaviour for 0–5 V vs 0–10 V). | Operator-requested firmware/product-selectable behaviour not recorded in any committed audit. | **Product / package decision needed.** Operator has requested firmware/product-selectable 0–5 V / 0–10 V; the package must not silently assume 0–10 V only. The active YAML's `${fan_dac_voltage_mode}` default `10V` / alternate `5V` is a single chip-level substitution today — to satisfy the operator request the package may need to expose two substitutions (`${fan_dac_voltage_mode}` for `IC1`, `${fan_dac_voltage_mode_2}` for `IC2`) once `IC2` is bound. | PR #570 — [§GP8403 output range capability](#gp8403-output-range-capability) "Conservative conclusion" bullets; PR #570 audit log decision (ii) at line 825. | **Yes** at the design-decision layer. Cannot be cleared by evidence alone; requires `PACKAGE-DAC-001` (package layer) and `PRODUCT-DAC-001` (product layer) decisions to align. | Decision recorded in the next `PACKAGE-DAC-001` slice (whether to expose range via `select:` / per-fan-type / chip-level substitution) **and** in `PRODUCT-DAC-001` (which firmware variants offer which range). |
| 7 | Per-channel range mixing on a single GP8403. | Conservative posture not previously committed in writing. | **Constrained.** Schematic + BOM together show one `V5V` reference pin per chip wired to `+12V` (MT3608 boost output); no per-channel switching topology exists. Simultaneous one-channel-0–5 V and one-channel-0–10 V on a **single** GP8403 is **not** a hardware capability of this board. Per-chip range mixing across `IC1` and `IC2` (one chip at 0–5 V, the other at 0–10 V) is achievable in principle, **subject to firmware / datasheet support for chip-level range selection** and **subject to row 3** (need addresses for both chips). The package must **not** claim per-channel range mixing on one GP8403. | PR #570 — [§GP8403 output range capability](#gp8403-output-range-capability) and audit log decision (v) at line 825. | **No (constraint).** This row supplies a hard guardrail rather than a blocker; the constraint is committed and must be honoured by any future `PACKAGE-DAC-001` slice. | Already encoded as a constraint. Any package edit that would claim simultaneous per-channel 0–5 V + 0–10 V on one GP8403 **must be rejected**. |
| 8 | `J2` / `J3` Cloudlift S12 output connector silkscreen pin-1 identity and harness mapping. | Schematic shows three nets per connector (`vout0` / `vout1` / `GND` for `J2`; `2vout0` / `2vout1` / `GND` for `J3`); silkscreen pin-1 position and lever orientation not committed. | **Still owed.** The 3-pin Phoenix-compatible terminal blocks (`MX350-3.5-03P-GN01-Cu-Y-A`) are BOM-confirmed, but the BOM does **not** encode silkscreen pin-1 location, and the schematic PDF does **not** mark it either. Operator-attested silkscreen reading and conductor-by-conductor harness trace are required to map a future `fan:` entity to a physical Cloudlift S12 output. **Do not fabricate** the mapping. | PR #570 — [§Module-side `J2` (CLOUDLIFT S12 FAN, driven by IC1)](#module-side-j2-cloudlift-s12-fan-driven-by-ic1) and [§Module-side `J3` (CLOUDLIFT S12 FAN2, driven by IC2)](#module-side-j3-cloudlift-s12-fan2-driven-by-ic2). | **Yes.** Required before any package edit that names which terminal-block pin is `vout0` vs `vout1` vs `GND`, and before any product-level Cloudlift harness documentation. | Operator-attested silkscreen reading of `J2` / `J3` pin-1 position + harness conductor-by-conductor trace, recorded with operator / date in the audit log of this doc. |
| 9 | Nextion / `J7` and UART0 interaction. | Open question whether a FanDAC build can share UART0 with the USB boot log when a Nextion display is wired on Module `J7`. | **Out of scope for `PACKAGE-DAC-001`.** [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) binds **no** `uart:` block and **no** Nextion `display:` component on the Module `J1` pins 4 / 5 pair, and no product today claims a FanDAC + Nextion combination. The interaction belongs to a future product-level slice (e.g. `PRODUCT-DAC-001-NEXTION` or similar) once a product actually exposes the Nextion display; `PACKAGE-DAC-001` itself is **not** blocked by this row. | PR #570 — [§UART0-vs-Nextion arbitration](#uart0-vs-nextion-arbitration). | **No** (deferred to future `PRODUCT-DAC-001` scope). | A future product-design decision; not required for `PACKAGE-DAC-001`. |
| 10 | Package YAML correctness — header comments, channel cardinality, range substitution shape, alias contract. | `fan_gp8403.yaml` header lines 13–18 partially refreshed by PR #569 to reference `GPIO48` / `GPIO45`; range comment at line 6 still says "(jumper selectable on hardware)"; the package still binds one GP8403 only; the `${fan_dac_voltage_mode}` substitution is chip-level only; [`packages/expansions/fan_dac.yaml`](../../packages/expansions/fan_dac.yaml) alias is byte-identical to the canonical pure-wrapper form. | **Needs implementation PR.** The `fan_gp8403.yaml` body changes that the rows above identify — (a) correct the stale "(jumper selectable on hardware)" comment, (b) record whether the package binds one or both GP8403s, (c) record the range-policy shape (chip-level vs per-chip substitution pair), (d) document the address-truth-table source — cannot land until rows 3, 6, and 8 close. The `fan_dac.yaml` alias should remain a canonical pure-wrapper of `fan_gp8403.yaml` unless a separate `PACKAGE-DAC-SPLIT-001` slice argues for a different split. | This doc; [`docs/hardware/package-readiness-matrix.md`](package-readiness-matrix.md) `fan_gp8403.yaml` row notes. | **Yes.** Implementation-pending. | `PACKAGE-DAC-001-IMPLEMENT-001` once rows 3, 6, and 8 close. |

### Verdict

**`PACKAGE-DAC-001` is not implementation-plannable yet.** The
shared-I²C-bus and BOM-identity blockers (rows 1 and 2) are
resolved; the output-range mechanism and per-channel-mixing
constraints (rows 5 and 7) are evidence-captured; row 9 is deferred
to future product scope. Rows 3, 6, 8, and 10 remain blocking:

- **Row 3 (DIP-switch address truth table)** — needed before any
  edit that exposes `IC2` as a second `gp8403:` device or widens the
  `${fan_dac_address}` allowed-values set.
- **Row 6 (output-range policy decision)** — needed before any
  edit that introduces a `${fan_dac_voltage_mode_2}` substitution or
  any `select:` / per-product range exposure.
- **Row 8 (`J2` / `J3` silkscreen + harness)** — needed before any
  edit that documents the physical terminal-block pin order or
  before any product-level Cloudlift wiring guidance.
- **Row 10 (package YAML correctness)** — implementation-pending;
  cannot land until rows 3, 6, and 8 close.

### Recommended next PR

**A DAC address / range / silkscreen evidence PR** —
provisionally named `HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001` (or a
similarly-scoped evidence-bearing slice). Scope:

- Add a GP8403 datasheet excerpt under `docs/hardware/` (path +
  citation) covering the 7-bit address base, the `A0` / `A1` / `A2`
  bit ordering, and the range-selection register layout — **or** a
  logic-analyser bench capture against a populated `S360-100-R4` +
  `S360-312-R4` pair under at least three DIP-switch settings,
  recorded with operator / date.
- Record an operator-attested silkscreen reading of `J2` / `J3`
  pin-1 location + harness conductor trace to the Cloudlift S12
  fan input.
- Record an operator / product decision on the output-range policy
  (chip-level only vs per-chip substitution pair vs per-product
  range exposure).
- **Do not** edit
  [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml),
  [`packages/expansions/fan_dac.yaml`](../../packages/expansions/fan_dac.yaml),
  any product / WebFlash wrapper, `config/**`, `firmware/**`,
  `manifest.json`, `firmware/sources.json`, `scripts/**`,
  `.github/workflows/**`, `components/**`, `include/**`, or
  `tests/**`. **Do not** flip `webflash_build_matrix`, add an
  `artifact_name`, add a compile-only target, claim DAC product /
  WebFlash / release readiness, or claim simultaneous per-channel
  0–5 V + 0–10 V on a single GP8403.

`PACKAGE-DAC-001-IMPLEMENT-001` becomes the **next-next** PR, gated
on the evidence PR landing.

### What this readiness refresh does **not** change

- [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)
  byte-identical (`${fan_dac_i2c_id}` default `core_i2c`,
  `${fan_dac_address}` default `0x58` / alternate `0x59`,
  `${fan_dac_voltage_mode}` default `10V` / alternate `5V`, two
  `output.platform: gp8403` channels, two `fan.platform: speed`
  entities, per-channel template sensors / voltage calculations,
  fan-control scripts, link-mode / auto-mode globals all preserved).
- [`packages/expansions/fan_dac.yaml`](../../packages/expansions/fan_dac.yaml)
  byte-identical (pure-wrapper `!include` of `fan_gp8403.yaml`).
- `S360-312` `schematic_status` stays `cataloged_unverified`;
  `schematic_file` stays unset in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json).
- No edit to any product YAML under
  [`products/`](../../products/) or any WebFlash wrapper under
  [`products/webflash/`](../../products/webflash/).
- No edit to
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json),
  [`config/product-catalog.json`](../../config/product-catalog.json),
  [`config/webflash-builds.json`](../../config/webflash-builds.json),
  [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json),
  [`config/firmware-combination-matrix.json`](../../config/firmware-combination-matrix.json),
  [`config/kit-intent-matrix.json`](../../config/kit-intent-matrix.json),
  [`config/compile-only-targets.json`](../../config/compile-only-targets.json),
  or [`config/compile-only-candidates.json`](../../config/compile-only-candidates.json).
- No edit to any test under [`tests/`](../../tests/), any script
  under [`scripts/`](../../scripts/), any workflow under
  `.github/workflows/`, any component under `components/`, any
  header under `include/`, or any release artifact / `manifest.json`
  / `firmware/sources.json` / checksums / build-info file.
- Release-One (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`),
  the LED preview (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`),
  FanTRIAC (`blocked` / `HW-005`), the `FanDAC` ↔ `AirIQ` mutex
  (`rules.fandac_conflicts_with_airiq: true`), and the fan-driver
  `max-one-of` rule are all unchanged.
- `S360-100-BENCH-001`, `HW-PINMAP-311-FOLLOWUP`,
  `HW-PINMAP-320-FOLLOWUP`, and `COMPLIANCE-001` are not closed by
  this PR.
- The WebFlash repository (`sense360store/WebFlash`) is untouched.

## 2026-05-22 — HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001

This section records the **HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001**
evidence pass. It re-examines the rows that the
[§PACKAGE-DAC-001 readiness refresh](#package-dac-001-readiness-refresh)
(PR #571) left **blocking** — **row 3** (DIP-switch ↔ I²C-address
truth table), **row 6** (output-range policy decision), **row 8**
(`J2` / `J3` silkscreen pin-1 identity + harness), and **row 10**
(package YAML correctness, gated on rows 3 / 6 / 8) — using two
evidence sources that were **not** available to PR #570 / PR #571:

1. The **GP8403 public datasheet** — the StanStrong-translated GP8403
   datasheet and the Guestgood `GP8403-TC50-EW` datasheet — for the
   I²C address bit ordering and the output-range register.
2. The **S360-312-R4 / `Fan_GP8403` Google Drive layout assets** — the
   KiCad PCB source, the fabrication gerbers, and the board render
   images — for the physical `J2` / `J3` / `SW1` / `SW2` silkscreen and
   the pad-to-net mapping.

It also records the **operator design decisions** supplied for this
pass.

This section is **documentation / evidence only**. It does **not**
edit
[`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)
or
[`packages/expansions/fan_dac.yaml`](../../packages/expansions/fan_dac.yaml),
does **not** implement `PACKAGE-DAC-001`, does **not** add a DAC
product YAML or a WebFlash wrapper, does **not** flip
`webflash_build_matrix`, does **not** add an `artifact_name`, does
**not** add a compile-only target, does **not** claim DAC product /
WebFlash / release readiness, and does **not** claim simultaneous
per-output 0–5 V and 0–10 V on a single GP8403. It does **not** touch
`config/**`, `firmware/**`, `manifest.json`, `firmware/sources.json`,
`scripts/**`, `.github/workflows/**`, `components/**`, `include/**`,
`tests/**`, any release artifact / checksum / build-info manifest, or
the WebFlash repository (`sense360store/WebFlash`).

### Operator design decisions (recorded)

| # | Decision | Recorded value |
|---|---|---|
| D1 | Package shape | **Two DAC chips** (`IC1`, `IC2`), **four** analog outputs (two per chip). |
| D2 | Range policy | **Per-DAC-chip** range setting (one range per GP8403), **not** per-output. |
| D3 | Default range | **Both** DAC chips default **0–10 V**. |
| D4 | Override policy | Product / firmware may override `IC1` and `IC2` range **independently**. |
| D5 | Address policy | Expose I²C-address substitutions for **both** `IC1` and `IC2`. |
| D6 | Hard guardrail | Do **not** claim simultaneous per-output 0–5 V / 0–10 V on a single GP8403 (carried from PR #570 [§GP8403 output range capability](#gp8403-output-range-capability)). |

### Evidence-source provenance

The Google Drive layout assets live under the `Fan_GP8403` board
folder (legacy name for `S360-312`). They are inspected here for
evidence; per
[`docs/hardware/hardware-artifact-policy.md`](hardware-artifact-policy.md)
the KiCad source, gerbers, CPL, drill, STEP, and board-image classes
remain **retained-but-not-committed**, so this PR records their
provenance and the observations drawn from them **without** committing
the binaries. The SHA256 values below are of the **bytes downloaded
during this evidence pass** (recorded for traceability, not asserted
as canonical fab checksums).

| Asset | Drive file id | Size (bytes) | Drive `modifiedTime` | Role | SHA256 (downloaded bytes) |
|---|---|---:|---|---|---|
| `Fan_GP8403.kicad_pcb` | `1mXZ52Z2nDFqbtfSnmEdf5dDV_I2sTIW8` | 620,059 | 2025-08-22 | Authoritative pad→net + silkscreen-text source | `db702f1164e228a14e2071c87144ef7aaa50a5b143cfbb539435c53129578245` |
| `Fan_GP8403.png` (top render) | `1EcZCF3h89Ov90ETeGU6p_MuXCcgjqt81` | 172,016 | 2025-08-22 | Top-side 3D render — connector / DIP layout | `37e09178c08e13e8daeae015a3c251f8ee9cf321238c6b2690ac8819030ca8d8` |
| `Fan_GP84032.png` (bottom render) | `1eqjCPY2F4wSfx2suGjPzZ9qosaEwTxNM` | 106,990 | 2025-08-22 | **Bottom silkscreen** — `J2` / `J3` / `J7` pad labels | `c811635f370ceeec09229203b30fb8f2fe899f900e7c868ef540facf8a1630f2` |
| `Fan_GP84033.png` (front render) | `1n_YRisJxBaynasJdS027GcseD-QGpHMB` | 143,802 | 2025-08-22 | Front 3D render — `SW1` / `SW2` ON-arrow, `J3` pin-1 ▲ | `3f857ff8389e450c5b8a9c07b6eabe4dee56402eddc719ce582805e6917ca083` |
| `Fan_GP8403-F_Silkscreen.gto` | `1iXiit8J9DWJe2fSeyBt6yCVcUCV7X0Pq` | 85,222 | 2025-08-22 | Front silkscreen gerber (corroborates silk layer; present, not separately transcribed — text renders as strokes) | _(not hashed this pass)_ |
| `Fan_GP8403.xlsx` (BOM) | `1Vg7JVJyk-ysDSRJBNpfgDQelbcaE7dPh` | 12,744 | 2025-08-14 | BOM (already transcribed under [§BOM cross-check](#bom-cross-check); SHA256 `1886ecad…` recorded by PR #570) | _(see PR #570)_ |
| `Fan_GP8403.pdf` (Drive schematic) | `193BM5sV-3lvxBoKp1BRCquzWUkvKsylM` | 445,302 | 2025-08-14 | Drive-side schematic export. Content matches the committed schematic (same `IC1` / `IC2` pinout and nets) but is a **different export** (not byte-identical to the committed [`S360-312-R4.pdf`](schematics/S360-312-R4.pdf), SHA256 `2888f626…`, 122,230 bytes). The committed PDF stays canonical. | _(not hashed this pass)_ |

### GP8403 datasheet evidence

Sourced from the StanStrong-translated GP8403 datasheet and the
Guestgood `GP8403-TC50-EW` datasheet (the BOM-confirmed variant — see
[§BOM cross-check](#bom-cross-check)).

**Pin map (confirms the schematic capture):** pin 1 `SCLK`, pin 2
`SDA`, pin 3 `A0`, pin 4 `A1`, pin 5 `VCC`, pin 6 `GND`, pin 7
`VOUT1`, pin 8 `VOUT0`, pin 9 `A2`, pin 10 `V5V` (internal LDO, ≥ 1 µF
external cap). This matches the [§Schematic summary](#schematic-summary)
and [§GP8403 address-selection evidence](#gp8403-address-selection-evidence)
capture exactly.

**I²C address (closes the row-3 bit ordering):**

- The datasheet states "One I²C interface supports 8 GP8403 parallel
  connections, selected through three-digit hardware addresses
  `A2`/`A1`/`A0`", and the pin table defines `A0` = "the 0th bit
  hardware address", `A1` = "1st bit hardware address", `A2` = "2nd bit
  hardware address". So the three address pins form the low 3 bits of
  the 7-bit address, weighted `A2`·4 + `A1`·2 + `A0`·1.
- The GP8403 7-bit address **base is `0x58`**, giving the span
  **`0x58`–`0x5F`** (public GP8403 references; the ESPHome `gp8403:`
  component default address is `0x58`; the DFRobot GP8403 library uses
  `0x58`). This is **consistent** with the package's existing
  `${fan_dac_address}` default `0x58` / alternate `0x59` in
  [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml).

**Output range (closes the row-6 mechanism + reinforces row-7):**

- Datasheet §3.3.6: the range is selected by writing **register
  `0x01`** — write `0x00` → chip output range **0–5 V**; write `0x11`
  → chip output range **0–10 V**.
- Register `0x01` is a **single chip-level register** ("the voltage at
  **the chip** output is selected") — it sets the range for **both**
  `VOUT0` and `VOUT1` of that GP8403 together. Datasheet §4 confirms
  range is "selected by **internal configuration of the chip**".
- Therefore range selection is **register / I²C-firmware-driven and
  per-chip**, not per-output and not hardware-jumper-driven. This
  corroborates PR #570's schematic-side finding (one `V5V` per chip
  hardwired to `+12 V`; no range jumper in the BOM) and the row-7
  constraint that **simultaneous one-output-0–5 V + one-output-0–10 V
  on a single GP8403 is not possible**.

### DIP-switch ↔ I²C-address truth table — row 3 (CLOSED)

The KiCad PCB source assigns the `SW1` / `SW2` poles to the GP8403
address pins, with the opposite side of each pole tied to `GND`:

| DIP | Pole / pad 1 → net | Pole / pad 2 → net | Pole / pad 3 → net | Opposite pads | Drives |
|---|---|---|---|---|---|
| `SW1` | pad 1 → `A0` | pad 2 → `A1` | pad 3 → `A2` | pads 4 / 5 / 6 → `GND` | `IC1` |
| `SW2` | pad 1 → `2A0` | pad 2 → `2A1` | pad 3 → `2A2` | pads 4 / 5 / 6 → `GND` | `IC2` |

Each address pin also carries a 4.7 kΩ pull-up to `+3.3 V` (`R3`/`R5`/`R7`
for `IC1`; `R4`/`R6`/`R8` for `IC2` — see [§BOM cross-check](#bom-cross-check)).
A pole therefore behaves as:

- **Closed (ON)** → the address pin is shorted to `GND` → logic **0**.
- **Open (OFF)** → the address pin floats high through the 4.7 kΩ
  pull-up → logic **1**.

The board render (`Fan_GP84033.png` / `Fan_GP8403.png`) shows each DIP
body carries an **ON-direction arrow** pointing toward the `GND`-side
pads, so pushing a slider toward the arrow (ON) closes that pole. With
base `0x58` and the bit weighting above, the DIP-position → 7-bit
address truth table is:

| `A2` (SW pole 3) | `A1` (SW pole 2) | `A0` (SW pole 1) | 7-bit address |
|---|---|---|---|
| ON (0) | ON (0) | ON (0) | `0x58` |
| ON (0) | ON (0) | OFF (1) | `0x59` |
| ON (0) | OFF (1) | ON (0) | `0x5A` |
| ON (0) | OFF (1) | OFF (1) | `0x5B` |
| OFF (1) | ON (0) | ON (0) | `0x5C` |
| OFF (1) | ON (0) | OFF (1) | `0x5D` |
| OFF (1) | OFF (1) | ON (0) | `0x5E` |
| OFF (1) | OFF (1) | OFF (1) | `0x5F` |

(Same table applies to `SW2` → `IC2` using `2A0`/`2A1`/`2A2`.) The
package's `${fan_dac_address}` default `0x58` corresponds to **all
three `SW1` poles ON (closed)**; the alternate `0x59` corresponds to
**pole 1 (`A0`) OFF, poles 2/3 ON**. For the two-chip package
(decision D5), `IC1` and `IC2` must take **distinct** addresses — e.g.
`IC1` = `0x58` (SW1 all ON) and `IC2` = `0x59` (SW2 pole 1 OFF).

**Status: row 3 truth table CLOSED** by datasheet (bit ordering +
`0x58` base) plus the PCB pole→pin mapping. **Residual (non-blocking):**
the *as-shipped* factory DIP positions are **not** evidenced — the
render shows the KiCad 3D-model default slider position, which does
**not** establish what setting ships on a populated unit. Confirming
the shipped default still wants a logic-analyser bench scan or an
operator attestation; the package does not depend on it because it
exposes explicit `${fan_dac_address}` / `${fan_dac_address_2}`
substitutions.

### Output-range policy — row 6 (CLOSED)

| Question | Resolution | Basis |
|---|---|---|
| Per-output, per-chip, or global range? | **Per-chip** (one range per GP8403 via register `0x01`). | Datasheet §3.3.6 / §4; one `V5V` per chip (PR #570). |
| Default range | **Both chips 0–10 V.** | Operator decision D3. |
| Override | `IC1` and `IC2` overridable **independently**. | Operator decision D4; two independent register-`0x01` writes (one per address). |
| Per-output 0–5 V / 0–10 V mix on one chip? | **Not claimed / not possible.** | Operator guardrail D6; datasheet register `0x01` is chip-level. |

Package shape implied by this policy (for the implementation PR, not
applied here): two `gp8403:` devices; each with its own chip-level
`voltage:` substitution — e.g. `${fan_dac_voltage_mode}` (`IC1`,
default `10V`) and a new `${fan_dac_voltage_mode_2}` (`IC2`, default
`10V`).

**Status: row 6 CLOSED** — policy decided (operator) and mechanism
evidenced (datasheet).

### `J2` / `J3` connector mapping — row 8 (board-level CLOSED; harness pending)

The KiCad PCB source gives the authoritative pad-to-net mapping, and
the bottom-silkscreen render (`Fan_GP84032.png`) gives the printed pad
labels. Pad 1 of each terminal block is the KiCad pin-1 marker pad
(rounded-rectangle / square pad; the front render also shows a
silkscreen ▲ at `J3` pin 1):

| Conn. | Pin 1 (▢ marker) | Pin 2 (middle) | Pin 3 | Driven by |
|---|---|---|---|---|
| `J2` | net `vout0` (`IC1` `VOUT0`, pin 8); silk **`out0`** | net `GND`; silk **`gnd`** | net `vout1` (`IC1` `VOUT1`, pin 7); silk **`out1`** | `IC1` |
| `J3` | net `2vout0` (`IC2` `VOUT0`, pin 8); silk **`out1`** | net `GND`; silk **`gnd`** | net `2vout1` (`IC2` `VOUT1`, pin 7); silk **`out0`** | `IC2` |

Findings:

- **Pin order is identical and `GND` is the middle pin** on both
  connectors: physical **pin 1 = the chip's `VOUT0`**, **pin 2 =
  `GND`**, **pin 3 = the chip's `VOUT1`**. (This corrects any
  assumption of a `GND` / `vout0` / `vout1` order — `GND` is centre,
  not first.)
- **`J2` silkscreen agrees with the `IC1` channel index** (`out0` =
  `VOUT0`, `out1` = `VOUT1`).
- **⚠ `J3` silkscreen `out0`/`out1` text is transposed** relative to
  the `IC2` channel nets: the pin-1 pad (net `2vout0` = `IC2` `VOUT0`)
  is silkscreened **`out1`**, and the pin-3 pad (net `2vout1` = `IC2`
  `VOUT1`) is silkscreened **`out0`**. So firmware that drives `IC2`
  channel 0 (`VOUT0`) emits on the `J3` pin **physically labelled
  `out1`**. This is visible in both the bottom-silk render and the
  PCB silkscreen-text layer. It must be honoured (or corrected at the
  board level) by any installation / harness documentation, and
  warrants an operator / bench confirmation before the printed `J3`
  `out0`/`out1` text is relied upon.

**Status: row 8 board-level CLOSED** — `J2` / `J3` pin-1 identity, pin
order (`VOUT0` / `GND` / `VOUT1`), and silkscreen labels are now
evidenced from the Drive layout assets, including the `J3` label
transposition. **Residual (product / bench, does not block the package
YAML):** the **harness conductor-by-conductor trace to the physical
Cloudlift S12 fan input** is **not** resolvable from the Drive assets
(no fan / harness artifact exists in Drive) — it remains a
`PRODUCT-DAC-001` / installation-doc item; and the `J3` silk
transposition wants an operator / bench confirmation. The package YAML
binds logical GP8403 channels (chip + channel index) and does not
require the physical harness trace.

### Remaining `PACKAGE-DAC-001` blockers after this pass

Row numbering mirrors the [§Readiness table](#readiness-table)
(PR #571).

| # | Blocker | State after this evidence pass | Still blocks `PACKAGE-DAC-001`? |
|---:|---|---|---|
| 1 | Shared-I²C-bus naming | Resolved (PR #569). | No. |
| 2 | GP8403 BOM identity | Resolved (PR #570). | No. |
| 3 | DIP-switch ↔ I²C-address truth table | **CLOSED** — datasheet bit ordering + `0x58` base + PCB pole→pin map; truth table above. As-shipped DIP default is a non-blocking bench item. | No. |
| 4 | DAC-chip / channel capacity | **CLOSED** — operator decision D1 (two chips, four outputs); PCB confirms `IC1`→`J2`, `IC2`→`J3`. | No. |
| 5 | Range-selection **mechanism** | **CLOSED** — register `0x01`, per-chip, register/firmware-driven (datasheet). Stale "(jumper selectable on hardware)" comment correction is an implementation-PR edit. | No (comment fix deferred to impl PR). |
| 6 | Range **policy** | **CLOSED** — operator decisions D2–D4 (per-chip; both default 0–10 V; independent override). | No. |
| 7 | Per-output range mixing on one GP8403 | **Constraint confirmed** — register `0x01` is chip-level; mixing on one chip is not possible (guardrail D6). | No (hard constraint). |
| 8 | `J2` / `J3` silkscreen pin-1 + harness | **Board-level CLOSED** (pin order + silk labels + `J3` transposition). Harness-to-fan trace is a product/bench item; does not block the package YAML. | No (for the package); product-level residual. |
| 9 | Nextion / `J7` + UART0 | Deferred to a future product slice. | No. |
| 10 | Package YAML correctness | **PLANNABLE** — rows 3 / 6 / 8 (board-level) closed; operator decisions fix the shape, range, and address policy. Implementation = `PACKAGE-DAC-001-IMPLEMENT-001`. | Implementation-pending (no longer evidence-blocked). |

### Verdict

**`PACKAGE-DAC-001` is now implementation-plannable.** The three
rows that PR #571 left blocking are resolved at the layer the package
YAML needs:

- **Row 3** — the DIP-switch → 7-bit-address truth table is
  established from the GP8403 datasheet (`A0`/`A1`/`A2` = bits 0/1/2,
  base `0x58`) and the PCB pole→pin mapping.
- **Row 6** — the output-range policy is decided (per-chip; both
  default 0–10 V; independent override) and the mechanism is evidenced
  (register `0x01`, per-chip).
- **Row 8** — `J2` / `J3` pin-1 identity, pin order (`VOUT0` / `GND` /
  `VOUT1`), and silkscreen labels are evidenced from the Drive layout
  assets (including the `J3` `out0`/`out1` transposition).

### Recommended next PR

**`PACKAGE-DAC-001-IMPLEMENT-001`** — the package implementation PR.
Scope (for that PR, **not** done here):

- Bind **two** `gp8403:` devices: `IC1` at `${fan_dac_address}`
  (default `0x58`) and `IC2` at a new `${fan_dac_address_2}` (default
  `0x59`), both on `${fan_dac_i2c_id}` (`core_i2c`).
- Expose **per-chip** range substitutions: `${fan_dac_voltage_mode}`
  (`IC1`, default `10V`) and `${fan_dac_voltage_mode_2}` (`IC2`,
  default `10V`), overridable independently.
- Expose the **four** outputs (two per chip).
- Correct the stale `fan_gp8403.yaml` line-6 comment from "(jumper
  selectable on hardware)" to "firmware/register-driven (register
  `0x01`, per chip)".
- **Do not** claim per-output 0–5 V / 0–10 V mixing on a single
  GP8403.

The following remain **product / bench** follow-ups and do **not**
block `PACKAGE-DAC-001-IMPLEMENT-001`:

- Harness conductor-by-conductor trace from `J2` / `J3` to the
  physical Cloudlift S12 fan input (needs the physical fan / harness;
  `PRODUCT-DAC-001` / installation docs).
- Operator / bench confirmation of the **`J3` `out0`/`out1`
  silkscreen transposition** flagged above.
- As-shipped factory DIP-switch positions (bench logic-analyser scan).
- Module `J1` pin-1 `+3.3 V` vs Core `J7` pin-1 `+5 V` voltage-rail
  discrepancy (`S360-100-BENCH-001`; pre-existing).

### What this evidence pass does **not** change

- [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)
  and
  [`packages/expansions/fan_dac.yaml`](../../packages/expansions/fan_dac.yaml)
  — byte-identical (no YAML edit; the two-chip / per-chip-range shape
  above is recorded as the *plan* for `PACKAGE-DAC-001-IMPLEMENT-001`,
  not applied).
- `S360-312` `schematic_status` stays `cataloged_unverified`;
  `schematic_file` stays unset in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json).
- No product YAML / WebFlash wrapper / `config/**` / `firmware/**` /
  `manifest.json` / `firmware/sources.json` / `scripts/**` /
  `.github/workflows/**` / `components/**` / `include/**` / `tests/**`
  / release artifact / checksum / build-info edit.
- No `webflash_build_matrix` flip, no `artifact_name`, no compile-only
  target, no DAC product readiness claim, no per-output-mix claim.
- The KiCad source / gerbers / board images stay
  **retained-but-not-committed** per the artifact policy; this PR
  records their provenance + observations only.
- Release-One (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`), the
  LED preview, FanTRIAC (`blocked` / `HW-005`), the `FanDAC` ↔ `AirIQ`
  mutex, and the fan-driver `max-one-of` rule are unchanged. The
  WebFlash repository is untouched.

## 2026-05-23 — PACKAGE-DAC-001-IMPLEMENT-001

This section records the **PACKAGE-DAC-001-IMPLEMENT-001** package
implementation, which lands the YAML reconciliation that the
[§2026-05-22 — HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001](#2026-05-22--hw-pinmap-312-followup-dac-evidence-001)
evidence pass marked **implementation-plannable** (rows 3 / 6 / 8
closed; verdict "`PACKAGE-DAC-001` is now implementation-plannable").
It applies the operator design decisions (D1–D6) at the **package
layer only**.

### What changed

[`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)
was reconciled from the legacy single-DAC / two-channel form to the
schematic-correct **two-DAC / four-output** form:

- **Two GP8403 chips** bound as a list: `fan_dac_1` (IC1) and
  `fan_dac_2` (IC2), both on the shared `${fan_dac_i2c_id}` bus
  (default `core_i2c`, `GPIO48` SDA / `GPIO45` SCL after PR #569).
- **Per-chip I²C address substitutions** (decision D5):
  `fan_dac_1_i2c_address` (default `0x58`, IC1) and
  `fan_dac_2_i2c_address` (default `0x59`, IC2) — distinct addresses
  within the GP8403 `0x58`–`0x5F` span (row-3 truth table).
- **Per-chip output-range substitutions** (decisions D2 / D3 / D4):
  `fan_dac_1_output_range` and `fan_dac_2_output_range`, **both
  default `0-10V`**, overridable independently per chip. Range is
  one setting per GP8403 (datasheet register `0x01`), not per output.
- **Four neutral package-layer outputs** (decision D1): `fan_dac_1_vout0`,
  `fan_dac_1_vout1`, `fan_dac_2_vout0`, `fan_dac_2_vout1`.
- The stale header comment "0-10V or 0-5V (jumper selectable on
  hardware)" was corrected to record that range is
  **firmware/register-driven** (register `0x01`, per chip), with each
  chip's `V5V` reference hardwired to `+12V` and **no** range jumper /
  solder-bridge on the board (row 5). The doc / header now states a
  single GP8403 **cannot** mix 0–5 V and 0–10 V across its two outputs
  (guardrail D6 / row 7).
- The product-layer `fan:` / `sensor:` / `globals:` / `script:` blocks
  that hard-coded `${friendly_name} Fan 1` / `Fan 2` names were
  **removed** from the package — user-facing fan entities, names, and
  control behaviour are a product-layer concern (`PRODUCT-DAC-001`).

[`packages/expansions/fan_dac.yaml`](../../packages/expansions/fan_dac.yaml)
remains the canonical pure-wrapper `!include` of `fan_gp8403.yaml`
(unchanged — it inherits the new shape).

Regression coverage was added in
[`tests/test_fandac_package.py`](../../tests/test_fandac_package.py)
(two chips, four outputs, two address substitutions, two range
substitutions defaulting to `0-10V`, `${fan_dac_i2c_id}` → `core_i2c`,
no legacy i²c ids, no stale "jumper selectable" wording, the
per-chip-not-per-output range guardrail, and the package-layer-only
guardrails). The existing
[`tests/test_fandac_alias_packages.py`](../../tests/test_fandac_alias_packages.py)
and the `fan_gp8403` case in
[`tests/test_core_abstract_bus.py`](../../tests/test_core_abstract_bus.py)
continue to pass.

### Scope boundary (what this PR does NOT do)

- **Package layer only.** `PACKAGE-DAC-001` is implemented at the
  package layer. **Product / WebFlash / release readiness remains
  blocked.**
- **No DAC product YAML** is added under [`products/`](../../products/).
- **No compile-only target** is added (no entry in
  [`config/compile-only-targets.json`](../../config/compile-only-targets.json)).
- **No WebFlash wrapper**, no `webflash_build_matrix` flip, no
  `artifact_name`, no `config/**` / `firmware/**` / `scripts/**` /
  `.github/workflows/**` / `components/**` / `include/**` /
  `manifest.json` / `firmware/sources.json` / release-artifact /
  checksum / build-info edit.
- **No `schematic_status` / `schematic_file` promotion** — `S360-312`
  stays `cataloged_unverified`.
- **No claim** of simultaneous per-output 0–5 V + 0–10 V on a single
  GP8403, and **no** DAC product / WebFlash / release / compliance
  readiness claim.
- The WebFlash repository (`sense360store/WebFlash`) is untouched.

### Remaining product-level follow-ups (not in this PR)

These move to **`PRODUCT-DAC-001`** (and a parallel bench / hardware
track) and do **not** block the package:

- User-facing fan entities / names / speed-control behaviour and the
  `J2` / `J3` → physical Cloudlift S12 fan harness conductor trace.
- Operator / bench confirmation of the **`J3` `out0` / `out1`
  silkscreen transposition** flagged in the evidence pass.
- As-shipped factory DIP-switch positions (bench logic-analyser scan).
- Module `J1` pin-1 `+3.3 V` vs Core `J7` pin-1 `+5 V` voltage-rail
  discrepancy (`S360-100-BENCH-001`).
- `S360-312` `schematic_status` promotion (separate JSON PR).

## Design-complete status (PRE-HW-PREP-FW-312-001)

`S360-312` is **design-complete** as of `PRE-HW-PREP-FW-312-001`
(2026-05-31), slice 2 of
[`docs/pre-hardware-prep-plan.md`](../pre-hardware-prep-plan.md).

**`design-complete` is a prose / documentation annotation only.** It is
deliberately **not** `verified`: it does **not** flip
`schematic_status` (which stays `cataloged_unverified`), does **not**
change `S360-312`'s lifecycle (`hardware-pending`), does **not** set
`schematic_file`, and does **not** enable any WebFlash exposure or
release surface (per
[`pre-hardware-prep-plan.md` §1.2 / §1.4](../pre-hardware-prep-plan.md#12-what-design-complete-is-explicitly-not)).
A `design-complete` board stays `cataloged_unverified` until its bench
session fills the D6 matrix below and a separate JSON-catalog PR makes
the `cataloged_unverified -> verified` flip.

Checklist against the four `design-complete` conditions
([`pre-hardware-prep-plan.md` §1.1](../pre-hardware-prep-plan.md#11-definition)):

| # | Condition | State | Evidence |
|---|---|---|---|
| 1 | Firmware driver finalised to the current design artifacts | met | [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) — dual `GP8403` (`IC1`/`IC2`) on the shared `core_i2c` bus, four neutral package-layer outputs, per-chip address + per-chip `voltage:` substitutions; reconciled against the committed schematic in this doc and in [`s360-312-r4-dac.md`](s360-312-r4-dac.md). The stale `GPIO39`/`GPIO40` header comment was already corrected to the Core `IO48`/`IO45` bus by `CORE-ABSTRACT-BUS-001B`. |
| 2 | Firmware compiles end-to-end in a compile-only CI target | met | Full ESPHome compile green in run [`26364679370`](https://github.com/sense360store/esphome-public/actions/runs/26364679370) (`workflow_dispatch` / `compile_mode=full`, 9 targets, conclusion `success`; FW-COMPILE-DAC-FULL-RESULT-001). Targets `ceiling-poe-fandac-compile-only` and `ceiling-poe-fandac-product-compile-only` in [`config/compile-only-targets.json`](../../config/compile-only-targets.json). |
| 3 | Every binding traceable to a schematic-printed value (no invented GPIOs / addresses) | met (schematic-only values carried as such) | I²C bus is the abstract `${fan_dac_i2c_id}` -> `core_i2c`, which the Core schematic terminates at ESP32 `IO48`/`IO45`. The `0x58`/`0x59` addresses are the GP8403 base/next defaults and are **carried as owed-to-bench** (the `SW1`/`SW2` DIP->address mapping is not printed on the sheet — D6 item T2/T3). The `10V` range is the firmware default (GP8403 register `0x01`); the schematic shows no range jumper (D6 item T6). |
| 4 | Release-note template + artifact-naming + pre-written bench test matrix exist | met | D5 template + artifact-naming scheme and the D6 bench / evidence test matrix below. |

Owed to the bench (carried, **not** resolved by reaching
`design-complete`): the Core-`J7`-`+5V`-vs-module-`J1`-`+3.3V` rail
question, the `SW1`/`SW2` DIP-switch -> I²C-address mapping, the
`J2`/`J3` Cloudlift output silkscreen pin order (including the `J3`
out0/out1 transposition), and the `5V`/`10V` voltage-mode hardware
identification. All are listed in the D6 matrix below and owned by
`HW-PINMAP-312-FOLLOWUP`; the operator-facing form is the existing
[§S360-312-BENCH-EVIDENCE-REQUEST-001 checklist](#s360-312-bench-evidence-request-001--fandac-bench-evidence-checklist--contract-2026-05-27).

## D5 — Release-note template and artifact-naming (template only)

This is a **pre-written template only**: `PRE-HW-PREP-FW-312-001`
publishes no artifact, tags no release, authors no release notes for a
real build, and sets no `artifact_name` field in any `config/*.json`.
`RELEASE-DAC-001` / `WEBFLASH-DAC-001` stay blocked. The template
follows the house convention in
[`docs/room-firmware-release-notes.md`](../room-firmware-release-notes.md).

Artifact-naming scheme (for the eventual build, once verified +
released — **not** produced here), mirroring the Release-One scheme
(`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`):

```
Sense360-Ceiling-POE-FanDAC-v<MAJOR.MINOR.PATCH>-<channel>.bin
```

config string `Ceiling-POE-FanDAC`, product
[`products/sense360-ceiling-poe-fandac.yaml`](../../products/sense360-ceiling-poe-fandac.yaml).

Release-note template:

```
### Ceiling-POE-FanDAC v<MAJOR.MINOR.PATCH> (<channel>)

Artifact: Sense360-Ceiling-POE-FanDAC-v<MAJOR.MINOR.PATCH>-<channel>.bin

Summary: 0-10V fan control (for example Cloudlift S12 fan control) on the
Sense360 Core ceiling + PoE stack, via two GP8403 I2C DACs / four
neutral analog outputs (S360-312 FanDAC).

Entity surface: four package-layer analog outputs (fan_dac_1_vout0 /
fan_dac_1_vout1 / fan_dac_2_vout0 / fan_dac_2_vout1) plus the standard
device-identity / health diagnostic entities. (No user-facing fan
entity is bound at the package layer; product / feature-layer UX is a
separate slice.)

Compatibility: FanDAC is mutually exclusive with AirIQ
(fandac_conflicts_with_airiq); fan-driver variants
(FanRelay/FanPWM/FanDAC/FanTRIAC) are firmware-distinct and
max-one-of. Ships FanDAC only.

Owed / pending before stable: the D6 bench / evidence test matrix must
be filled and S360-312 flipped cataloged_unverified -> verified; the
+5V/+3.3V rail, DIP->address mapping, J2/J3 silkscreen pin order, and
5V/10V voltage-mode jumper remain owed (see D6). No release artifact is
published until then.
```

## D6 — Bench / evidence test matrix (pre-written; to be filled at the bench)

This is the pre-written checklist the hardware session fills to move
`S360-312` from `design-complete` to `verified`. It covers the
verify-pending items from D1 (rail, DIP->address, Cloudlift pin order,
voltage-mode jumper) plus per-channel DAC output linearity / range,
Cloudlift drive, and the blocking-diode behaviour. The `Measured` /
`Pass?` columns are **empty by design** — they are filled at the
bench, not here. This is the structured-matrix companion to the
operator-facing
[§S360-312-BENCH-EVIDENCE-REQUEST-001 checklist](#s360-312-bench-evidence-request-001--fandac-bench-evidence-checklist--contract-2026-05-27)
and the
[§Open evidence (not resolved by this PR)](#open-evidence-not-resolved-by-this-pr)
table (same owed set, expressed as a fill-in matrix).

**Bench session id:** `S360-312-DAC-BENCH-001` — to be run only when physical
hardware exists; all rows below are unfilled / owed.

| # | Test | Method | Expected (from design) | Measured | Pass? | Owed item |
|---|---|---|---|---|---|---|
| T1 | Core `J7` pin-1 vs module `J1` pin-1 supply rail | Silkscreen read + DMM on the assembled Core+module stack | Resolve `+5V` (Core capture) vs `+3.3V` (module `J1` / MT3608 `IN`) to a single confirmed rail | | | rail |
| T2 | `IC1` I²C address vs `SW1` DIP positions | Logic-analyser I²C capture + DIP silkscreen legend | `IC1` responds at the configured `fan_dac_1_i2c_address` (default `0x58`); DIP->address map recorded | | | DIP->address |
| T3 | `IC2` I²C address vs `SW2` DIP positions | Logic-analyser I²C capture + DIP silkscreen legend | `IC2` responds at the configured `fan_dac_2_i2c_address` (default `0x59`), distinct from `IC1`; no collision with Core I²C devices | | | DIP->address |
| T4 | `J2` Cloudlift output pin order (`IC1`) | Silkscreen photo + DMM continuity to `IC1` `VOUT0`/`VOUT1`/`GND` | Pin order confirmed against the net (`GND`/`vout0`/`vout1`) | | | Cloudlift pin order |
| T5 | `J3` Cloudlift output pin order (`IC2`) incl. out0/out1 transposition | Silkscreen photo + DMM continuity to `IC2` `VOUT0`/`VOUT1`/`GND` | Confirm the actual net (pin1=`VOUT0`, pin2=`GND`, pin3=`VOUT1`) vs the printed `out0`/`out1` labels | | | Cloudlift pin order |
| T6 | `5V`/`10V` voltage-mode hardware | Bench confirm GP8403 register `0x01` range vs any board jumper / solder-bridge | Range is firmware-selected (register `0x01`); confirm no contradicting board hardware | | | voltage-mode jumper |
| T7 | Per-channel output linearity / range (all four outputs) | DMM sweep of each output across 0–100% command | Monotonic, linear 0->10 V (or 0->5 V in `5V` mode) per channel; full-scale within GP8403 spec | | | DAC linearity/range |
| T8 | Blocking-diode behaviour (`D2`/`D3`/`D4`/`D5`) per output | Scope each output under load | Diode drop / reverse-block behaviour characterised per output | | | blocking diodes |
| T9 | Cloudlift S12 drive (harness conductor mapping) | Bench continuity + drive test against the actual Cloudlift S12 fan | Commanded 0–10 V drives the fan as expected end-to-end | | | Cloudlift drive |
| T10 | Nextion `J7` `+5V` source | Trace / DMM from module `J7` pin 1 | `+5V` source on the module identified | | | Nextion rail |
| T11 | UART0 boot-log vs Nextion-display contention | Bench behaviour at boot / OTA / deep-sleep | Contention characterised (package binds no `uart:`/`display:` today) | | | UART arbitration |

Filling this matrix is owed to the hardware session; this slice
resolves none of it. The `S360-312` board stays
`schematic_status: cataloged_unverified`.

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
| 2026-05-31 | `PRE-HW-PREP-FW-312-001` — record `S360-312` **design-complete** (prose annotation; slice 2 of [`pre-hardware-prep-plan.md`](../pre-hardware-prep-plan.md)). Added the [§Design-complete status](#design-complete-status-pre-hw-prep-fw-312-001) checklist, the [§D5](#d5--release-note-template-and-artifact-naming-template-only) release-note template + artifact-naming scheme, and the [§D6](#d6--bench--evidence-test-matrix-pre-written-to-be-filled-at-the-bench) bench / evidence test matrix. | Already-committed dual-`GP8403` driver [`fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml), the `Ceiling-POE-FanDAC` bundle, and the committed full-compile run [`26364679370`](https://github.com/sense360store/esphome-public/actions/runs/26364679370). No new bench / hardware evidence. | Documentation-only; no YAML / config / test / workflow / firmware change. `design-complete` is prose, **not** `verified`: `S360-312` stays `cataloged_unverified`, lifecycle unchanged, no `schematic_file`, no WebFlash / release surface. Rail / DIP->address / Cloudlift pin-order / voltage-mode-jumper stay OWED. |
| 2026-05-22 | HW-PINMAP-312-FOLLOWUP — consolidate schematic + BOM evidence in a standalone per-board reference doc after `CORE-ABSTRACT-BUS-001B-IMPLEMENT-001` (PR #569). The user supplied the same module-side schematic PDF (byte-identical to the already-committed schematic; SHA256 `2888f626bfa0139d2190f154f9b02ecf4cb06f2522a5b5802eaf96e16de39e28`) plus a **new** BOM spreadsheet (`Fan_GP8403.xlsx`; SHA256 `1886ecad5b9dd1a683b8c0ccebb770e5c02894854650b5a5553b19875f7e3a20`; 12,744 bytes; 19 rows incl. header) that had not previously been recorded in the repo. Decisions recorded: (i) target board `S360-312-R4`; (ii) FanDAC output behavior to be firmware/product-selectable (deferred to `PACKAGE-DAC-001`); (iii) supported ranges are GP8403's 0–5 V and 0–10 V; (iv) both GP8403 channels per chip are intended to be exposed at the connector; (v) no claim of simultaneous one-channel-0–5 V + one-channel-0–10 V on a single GP8403, because the schematic shows one `V5V` reference per chip wired to `+12V`. Inspected the schematic content already captured in [`docs/hardware/artifacts/S360-312-R4.md`](artifacts/S360-312-R4.md), the HW-PINMAP-312 audit at [`s360-312-r4-dac.md`](s360-312-r4-dac.md), the Core-side capture at [`s360-100-r4-core.md`](s360-100-r4-core.md), the `CORE-ABSTRACT-BUS-001B` landing at [`core-abstract-bus-reconciliation.md`](core-abstract-bus-reconciliation.md), and the current FanDAC package YAML at [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml). | Schematic PDF byte-identical to upload (SHA256 `2888f626bfa0139d2190f154f9b02ecf4cb06f2522a5b5802eaf96e16de39e28`; 122,230 bytes); `Fan_GP8403.xlsx` BOM spreadsheet (SHA256 `1886ecad5b9dd1a683b8c0ccebb770e5c02894854650b5a5553b19875f7e3a20`; 12,744 bytes; 19 rows transcribed under [§BOM cross-check](#bom-cross-check)); [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) (dual-channel; `fan_dac_i2c_id: core_i2c` default line 27; `gp8403.i2c_id: ${fan_dac_i2c_id}` line 43; `gp8403.address: ${fan_dac_address}` default `0x58` line 28; `gp8403.voltage: ${fan_dac_voltage_mode}` default `10V` line 31; two `output.platform: gp8403` channels 0 and 1; two `fan.platform: speed` entities); [`packages/expansions/fan_dac.yaml`](../../packages/expansions/fan_dac.yaml) (pure-wrapper alias); [`s360-100-r4-core.md` §J7](s360-100-r4-core.md#j7--gp8403-fan-connector-6-pin), §[I2C bus](s360-100-r4-core.md#i2c-bus), §[UART buses](s360-100-r4-core.md#uart-buses); this document. | **New file landed.** Created `docs/hardware/s360-312-r4-fandac.md` as the standalone schematic-backed reference doc that the HW-PINMAP-312 audit at [`s360-312-r4-dac.md` open question (x)](s360-312-r4-dac.md#hw-pinmap-312-followup-audit-log) had explicitly anticipated. **No package / product / WebFlash / catalog / release / firmware / test / WebFlash-wrapper edit.** [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) byte-identical. [`packages/expansions/fan_dac.yaml`](../../packages/expansions/fan_dac.yaml) byte-identical. `S360-312` `schematic_status` stays `cataloged_unverified`. `schematic_file` for `S360-312` stays unset. The `fan_gp8403.yaml` row in [`docs/hardware/package-readiness-matrix.md`](package-readiness-matrix.md) stays `needs-package-reconciliation` + `bench-evidence-pending` (notes refreshed by this PR to point at this new reference doc). [`docs/hardware/firmware-package-mapping-audit.md`](firmware-package-mapping-audit.md) notes for the FanDAC slice are refreshed to point at this new reference doc. `PACKAGE-DAC-001` (alias: `PACKAGE-GAP-001` FanDAC slice) is **no longer blocked at the shared-I²C-bus-naming layer** (carry-over from PR #569) but **stays blocked** on the 10 items enumerated in [§Blockers remaining for PACKAGE-DAC-001](#blockers-remaining-for-package-dac-001). `PRODUCT-DAC-001`, `WEBFLASH-DAC-001`, `RELEASE-DAC-001`, and `WF-IMPORT-DAC-001` stay blocked behind `PACKAGE-DAC-001`. No FanDAC-bearing entry exists in [`config/product-catalog.json`](../../config/product-catalog.json), [`config/webflash-builds.json`](../../config/webflash-builds.json), [`products/`](../../products/), or [`products/webflash/`](../../products/webflash/). `FanDAC` stays reserved in [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json) `canonical_modules` subject to the fan-driver `max-one-of` rule and the explicit `FanDAC` ↔ `AirIQ` mutex (`rules.fandac_conflicts_with_airiq: true`). `S360-100-BENCH-001`, `HW-PINMAP-311-FOLLOWUP`, `HW-PINMAP-320-FOLLOWUP`, and `COMPLIANCE-001` are not closed by this PR. Release-One stays `Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`. LED preview stays `Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`. FanTRIAC stays `blocked` / `HW-005`. The WebFlash repository (`sense360store/WebFlash`) is untouched. |
| 2026-05-22 | `PACKAGE-DAC-001-READINESS-REFRESH` — re-evaluate the 10 FanDAC-specific blockers enumerated in [§Blockers remaining for PACKAGE-DAC-001](#blockers-remaining-for-package-dac-001) after `CORE-ABSTRACT-BUS-001B-IMPLEMENT-001` (PR #569) and `HW-PINMAP-312-FOLLOWUP` (PR #570) both landed. Separate resolved evidence from remaining package-design decisions; record a clear next-action recommendation. **Docs / readiness only.** Inspected the post-PR-#570 state of this doc (the 10-row blocker table, the schematic + BOM evidence sections, the [§GP8403 output range capability](#gp8403-output-range-capability) finding, the [§Output-channel exposure](#output-channel-exposure) finding), the post-PR-#569 active YAML state in [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) (`${fan_dac_i2c_id}: core_i2c` default line 27, header comment block lines 13–18 already refreshed to reference `GPIO48` / `GPIO45`, stale "(jumper selectable on hardware)" comment at line 6 still present), the FanDAC alias [`packages/expansions/fan_dac.yaml`](../../packages/expansions/fan_dac.yaml) (byte-identical pure-wrapper `!include` of `fan_gp8403.yaml`), the post-PR-#569 [`tests/test_core_abstract_bus.py`](../../tests/test_core_abstract_bus.py) `SharedI2CBusTests` (13 cases) covering the canonical `core_i2c` bus on `GPIO48` / `GPIO45`, the [`tests/test_fandac_alias_packages.py`](../../tests/test_fandac_alias_packages.py) FanDAC alias regression scaffold (12 cases), the `fan_gp8403.yaml` row in [`docs/hardware/package-readiness-matrix.md`](package-readiness-matrix.md), the `Ceiling-POE-FanDAC` deferral row in [`config/compile-only-candidates.json`](../../config/compile-only-candidates.json) (rank 25, `defer`, blockers include `PACKAGE-DAC-001-deferred`), and the `PACKAGE-DAC-001` queue entry in [`UPCOMING_PR.md`](../../UPCOMING_PR.md). | This doc; [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) (byte-identical); [`packages/expansions/fan_dac.yaml`](../../packages/expansions/fan_dac.yaml) (byte-identical); [`tests/test_core_abstract_bus.py`](../../tests/test_core_abstract_bus.py); [`tests/test_fandac_alias_packages.py`](../../tests/test_fandac_alias_packages.py); [`docs/hardware/package-readiness-matrix.md`](package-readiness-matrix.md); [`config/compile-only-candidates.json`](../../config/compile-only-candidates.json) (byte-identical); [`UPCOMING_PR.md`](../../UPCOMING_PR.md). | **Readiness refresh recorded.** Added [§PACKAGE-DAC-001 readiness refresh](#package-dac-001-readiness-refresh) section with a 10-row readiness table (blocker × previous state × current state × evidence × still blocks `PACKAGE-DAC-001`? × what unblocks it), an explicit verdict (`PACKAGE-DAC-001` is **not implementation-plannable yet**), and a recommended next PR (a DAC address / range / silkscreen evidence PR — provisionally named `HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001`). Verdict basis: rows 1, 2 are resolved (shared-I²C-bus naming via PR #569; GP8403 BOM identity via PR #570); rows 5 and 7 are evidence-captured (firmware/register-driven range selection; per-channel range mixing on a single GP8403 is **not** a hardware capability); row 9 is deferred out of `PACKAGE-DAC-001` scope (Nextion / UART0 belongs to a future product slice). Rows 3, 6, 8, and 10 still block: row 3 (DIP-switch ↔ I²C address truth table) needs a GP8403 datasheet excerpt or a bench logic-analyser scan; row 6 (output-range policy) needs a recorded product / package design decision; row 8 (`J2` / `J3` silkscreen + harness) needs operator-attested silkscreen + harness trace; row 10 (package YAML correctness) is implementation-pending and gated on rows 3, 6, and 8. The recommended next PR is therefore the **DAC address/range evidence PR**, **not** `PACKAGE-DAC-001-IMPLEMENT-001`. **No edit** to [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) or [`packages/expansions/fan_dac.yaml`](../../packages/expansions/fan_dac.yaml) (both byte-identical). **No edit** to any product YAML / WebFlash wrapper / `config/**` / `firmware/**` / `manifest.json` / `firmware/sources.json` / `scripts/**` / `.github/workflows/**` / `components/**` / `include/**` / `tests/**` / release artifact / checksum / build-info manifest. **No** `webflash_build_matrix` flip; **no** `artifact_name` added; **no** compile-only target added; **no** WebFlash wrapper added; **no** DAC product YAML; **no** firmware artifact built or attached; **no** release artifact / tag created. **No** `schematic_status` / `schematic_file` promotion (`S360-312` stays `cataloged_unverified`; no `schematic_file` set). **No** COMPLIANCE-001 movement. **No** claim that `PACKAGE-DAC-001`, `PRODUCT-DAC-001`, `WEBFLASH-DAC-001`, `RELEASE-DAC-001`, or `WF-IMPORT-DAC-001` are unblocked beyond what PR #569 / PR #570 already established. **No** claim of simultaneous one-channel-0–5 V + one-channel-0–10 V on a single GP8403. **No** edit to the WebFlash repository (`sense360store/WebFlash`) — it is **read-only** for this PR. Refreshed cross-links in [`docs/hardware/package-readiness-matrix.md`](package-readiness-matrix.md) `fan_gp8403.yaml` row + §`fan_gp8403.yaml / S360-312` detail block; refreshed `PACKAGE-DAC-001` queue entry in [`UPCOMING_PR.md`](../../UPCOMING_PR.md). Release-One (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`), LED preview (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`), FanTRIAC (`blocked` / `HW-005`), the `FanDAC` ↔ `AirIQ` mutex, and the fan-driver `max-one-of` rule are unchanged. `S360-100-BENCH-001`, `HW-PINMAP-311-FOLLOWUP`, `HW-PINMAP-320-FOLLOWUP`, and `COMPLIANCE-001` are not closed. |
| 2026-05-22 | `HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001` — close the still-blocking `PACKAGE-DAC-001` rows (3 / 6 / 8 / 10) using the GP8403 public datasheet and the `Fan_GP8403` (S360-312-R4) Google Drive layout assets, and record the operator design decisions. Inspected: the GP8403 datasheet (StanStrong translation + Guestgood `GP8403-TC50-EW`) for the `A0`/`A1`/`A2` address bit ordering (bits 0/1/2; base `0x58`; span `0x58`–`0x5F`) and the output-range register (`0x01`; `0x00`→0–5 V, `0x11`→0–10 V; chip-level); the Drive `Fan_GP8403.kicad_pcb` (id `1mXZ52Z2nDFqbtfSnmEdf5dDV_I2sTIW8`; SHA256 `db702f11…` of downloaded bytes) for `J2`/`J3`/`SW1`/`SW2` pad→net and silkscreen-text layers; the Drive board renders `Fan_GP8403.png` (top; id `1EcZCF3h89Ov90ETeGU6p_MuXCcgjqt81`), `Fan_GP84032.png` (bottom silkscreen; id `1eqjCPY2F4wSfx2suGjPzZ9qosaEwTxNM`), `Fan_GP84033.png` (front; id `1n_YRisJxBaynasJdS027GcseD-QGpHMB`); the front-silkscreen gerber `Fan_GP8403-F_Silkscreen.gto` (id `1iXiit8J9DWJe2fSeyBt6yCVcUCV7X0Pq`). | GP8403 datasheet (public); Drive `Fan_GP8403.kicad_pcb`, `Fan_GP8403.png`, `Fan_GP84032.png`, `Fan_GP84033.png`, `Fan_GP8403-F_Silkscreen.gto`; this doc; [`docs/hardware/package-readiness-matrix.md`](package-readiness-matrix.md); [`UPCOMING_PR.md`](../../UPCOMING_PR.md). KiCad/gerber/image binaries **not committed** (retained-but-not-committed per [`hardware-artifact-policy.md`](hardware-artifact-policy.md)). | **Evidence section added** ([§2026-05-22 — HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001](#2026-05-22--hw-pinmap-312-followup-dac-evidence-001)) with tables for the DIP-switch ↔ I²C-address truth table, the output-range policy, the `J2`/`J3` connector mapping, and a refreshed remaining-blocker table. Outcome: **row 3 CLOSED** (DIP→7-bit-address truth table from datasheet bit ordering + `0x58` base + PCB pole→pin map); **row 6 CLOSED** (per-chip range policy decided + register `0x01` mechanism evidenced); **row 4 / 5 / 7 resolved/constrained**; **row 8 board-level CLOSED** (`J2`/`J3` pin order `VOUT0`/`GND`/`VOUT1`, silk labels, and the **`J3` `out0`/`out1` silkscreen transposition** vs `IC2` channel nets); **row 10 PLANNABLE**. Verdict: **`PACKAGE-DAC-001` is now implementation-plannable**; recommended next PR is **`PACKAGE-DAC-001-IMPLEMENT-001`** (bind two GP8403s; per-chip address + range substitutions; four outputs; correct the stale jumper comment). Residual product/bench items (non-blocking for the package): harness conductor trace to the physical Cloudlift S12 fan; operator/bench confirmation of the `J3` silk transposition; as-shipped DIP default; the `J1`/`J7` `+3.3 V`/`+5 V` rail discrepancy. **No edit** to [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) or [`packages/expansions/fan_dac.yaml`](../../packages/expansions/fan_dac.yaml) (both byte-identical). **No** product YAML / WebFlash wrapper / `config/**` / `firmware/**` / `manifest.json` / `firmware/sources.json` / `scripts/**` / `.github/workflows/**` / `components/**` / `include/**` / `tests/**` / release-artifact / checksum / build-info edit. **No** `webflash_build_matrix` flip, **no** `artifact_name`, **no** compile-only target, **no** DAC product YAML, **no** WebFlash wrapper, **no** firmware/release artifact. **No** `schematic_status` / `schematic_file` promotion (`S360-312` stays `cataloged_unverified`). **No** claim of simultaneous per-output 0–5 V + 0–10 V on a single GP8403. **No** DAC product / WebFlash / release readiness claim. The WebFlash repository (`sense360store/WebFlash`) is untouched. |
| 2026-05-23 | `PACKAGE-DAC-001-IMPLEMENT-001` — implement the FanDAC package at the **package layer** after the rows-3/6/8 evidence closure, applying operator decisions D1–D6. Inspected this doc's [§2026-05-22 — HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001](#2026-05-22--hw-pinmap-312-followup-dac-evidence-001) verdict, [`docs/hardware/package-readiness-matrix.md`](package-readiness-matrix.md) `fan_gp8403.yaml` row / detail block, [`UPCOMING_PR.md`](../../UPCOMING_PR.md) queue entry 14, the legacy [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) (single-DAC / two-channel form with hard-coded `${friendly_name} Fan 1/2` entities + sensors + globals + scripts), the [`packages/expansions/fan_dac.yaml`](../../packages/expansions/fan_dac.yaml) alias, and the `fan_gp8403` regression cases in [`tests/test_core_abstract_bus.py`](../../tests/test_core_abstract_bus.py) / [`tests/test_fandac_alias_packages.py`](../../tests/test_fandac_alias_packages.py). | [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) (reconciled); [`packages/expansions/fan_dac.yaml`](../../packages/expansions/fan_dac.yaml) (unchanged pure-wrapper); [`tests/test_fandac_package.py`](../../tests/test_fandac_package.py) (new); this doc; [`docs/hardware/package-readiness-matrix.md`](package-readiness-matrix.md); [`docs/hardware/firmware-package-mapping-audit.md`](firmware-package-mapping-audit.md); [`UPCOMING_PR.md`](../../UPCOMING_PR.md). | **Package-layer implementation landed.** [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) now binds **two** GP8403 chips (`fan_dac_1`/IC1, `fan_dac_2`/IC2) on the shared `${fan_dac_i2c_id}` (`core_i2c`) bus; exposes per-chip address substitutions `fan_dac_1_i2c_address` (`0x58`) / `fan_dac_2_i2c_address` (`0x59`); exposes per-chip output-range substitutions `fan_dac_1_output_range` / `fan_dac_2_output_range` (both default `0-10V`, independently overridable); exposes **four** neutral outputs `fan_dac_1_vout0` / `fan_dac_1_vout1` / `fan_dac_2_vout0` / `fan_dac_2_vout1`; corrects the stale "(jumper selectable on hardware)" comment to firmware/register-driven (register `0x01`, per chip); and records that a single GP8403 **cannot** mix 0–5 V / 0–10 V across its two outputs. The product-layer `fan:` / `sensor:` / `globals:` / `script:` blocks (hard-coded `${friendly_name}` fan names) were removed — they move to `PRODUCT-DAC-001`. [`packages/expansions/fan_dac.yaml`](../../packages/expansions/fan_dac.yaml) stays the canonical pure-wrapper `!include`. New regression test [`tests/test_fandac_package.py`](../../tests/test_fandac_package.py) (20 cases) pins the shape; [`tests/test_core_abstract_bus.py`](../../tests/test_core_abstract_bus.py) and [`tests/test_fandac_alias_packages.py`](../../tests/test_fandac_alias_packages.py) still pass. **Package layer only — product / WebFlash / release readiness remains blocked.** **No** DAC product YAML; **no** compile-only target; **no** WebFlash wrapper; **no** `webflash_build_matrix` flip; **no** `artifact_name`; **no** `config/**` / `firmware/**` / `scripts/**` / `.github/workflows/**` / `components/**` / `include/**` / `manifest.json` / `firmware/sources.json` / release-artifact / checksum / build-info edit; **no** `schematic_status` / `schematic_file` promotion (`S360-312` stays `cataloged_unverified`); **no** claim of simultaneous per-output 0–5 V + 0–10 V on a single GP8403; **no** DAC product / WebFlash / release / compliance readiness claim. Remaining product-level decisions move to `PRODUCT-DAC-001`. Release-One, LED preview, FanTRIAC (`blocked` / `HW-005`), the `FanDAC` ↔ `AirIQ` mutex, and the fan-driver `max-one-of` rule are unchanged. The WebFlash repository (`sense360store/WebFlash`) is untouched. |

| 2026-05-23 | `FW-COMPILE-DAC-001` — add compile-only validation coverage for the FanDAC package after `PACKAGE-DAC-001-IMPLEMENT-001` (PR #573) and resolve the gp8403 `voltage:` enum concern recorded by `PRODUCT-DAC-001-READINESS-REFRESH` (PR #574). Inspected the post-PR-#573 [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) (per-chip `fan_dac_1_output_range` / `fan_dac_2_output_range` were set to the **invalid** ESPHome enum string `0-10V`), the ESPHome gp8403 component schema ([esphome.io/components/output/gp8403](https://esphome.io/components/output/gp8403) — `voltage:` accepts only `10V` / `5V`), this doc's [§Output-range policy — row 6](#output-range-policy--row-6-closed) (implied default `10V`), the compile-only lane at [`config/compile-only-targets.json`](../../config/compile-only-targets.json) / [`config/compile-only-candidates.json`](../../config/compile-only-candidates.json), the existing compile-only skeleton pattern under [`products/compile-only/`](../../products/compile-only/), and [`tests/test_compile_targets.py`](../../tests/test_compile_targets.py) / [`tests/test_fandac_package.py`](../../tests/test_fandac_package.py). | [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) (voltage enum fix `0-10V`→`10V` + comments); [`products/compile-only/ceiling-poe-fandac.yaml`](../../products/compile-only/ceiling-poe-fandac.yaml) (new compile-only skeleton); [`config/compile-only-targets.json`](../../config/compile-only-targets.json) (new target, totals 8→9); [`config/compile-only-candidates.json`](../../config/compile-only-candidates.json) (FanDAC row refresh + `currently_compile_only_config_strings`); [`tests/test_fandac_package.py`](../../tests/test_fandac_package.py); [`tests/test_compile_targets.py`](../../tests/test_compile_targets.py); this doc; [`docs/compile-only-firmware-validation.md`](../compile-only-firmware-validation.md); [`docs/product-readiness-matrix.md`](../product-readiness-matrix.md); [`UPCOMING_PR.md`](../../UPCOMING_PR.md). | **Compile-only validation target landed + voltage enum FIXED (Option A).** The gp8403 `voltage:` substitutions are corrected from the invalid `0-10V` string to the valid ESPHome enum `10V` (customer-facing 0-10V) — matching the default `10V` row 6 already implied; the user-facing 0-10V / 0-5V labels stay in product / kit docs. A single compile-only target `ceiling-poe-fandac-compile-only` (`products/compile-only/ceiling-poe-fandac.yaml`, config string `Ceiling-POE-FanDAC`, `shipment_status: compile-only`, `webflash_exposure_allowed_now: false`, `hardware_required_for_validation: true`, `blocked: false`, `compile_validation_status: pending-ci`, `voltage_enum_fixed: true`) is added; it lives under `products/compile-only/` (no catalog enumeration), composes Core ceiling + PoE PSU + base + health + the FanDAC alias `fan_dac.yaml`. Row 10 of [§Blockers remaining for PACKAGE-DAC-001](#blockers-remaining-for-package-dac-001) is **partially addressed** — `validate_compile_targets.py --metadata-only` passes; the `--compile` / `esphome config` pass is **owed to CI** and **not claimed** locally (ESPHome is not assumed present). **No DAC product YAML** at the top level of [`products/`](../../products/); **no** `config/product-catalog.json` entry; `PRODUCT-DAC-001` stays gated. **No** WebFlash wrapper; **no** `webflash_build_matrix` flip; **no** `artifact_name`; **no** entry in [`config/webflash-builds.json`](../../config/webflash-builds.json) (the `FanDAC` token is absent there); **no** release artifact / checksum / build-info / `manifest.json` / `firmware/sources.json` / `.github/workflows/**` / `components/**` / `include/**` edit. **No** `schematic_status` / `schematic_file` promotion (`S360-312` stays `cataloged_unverified`). **No** claim of simultaneous per-output 0–5 V + 0–10 V on a single GP8403. **No** DAC product / WebFlash / release / compliance readiness claim, and **no** compile-success claim until CI proves it. Release-One (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`), LED preview (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`), FanTRIAC (`blocked` / `HW-005`), the `FanDAC` ↔ `AirIQ` mutex, and the fan-driver `max-one-of` rule are unchanged. The WebFlash repository (`sense360store/WebFlash`) is untouched. |
| 2026-05-23 | `PRODUCT-DAC-001` — add the canonical FanDAC product YAML at the **product layer** after `FW-COMPILE-DAC-001` (PR #575) landed the compile-only target + voltage-enum fix and `FW-COMPILE-DAC-RESULT-001` (PR #576) recorded the compile-only **metadata** lane green (Run ID `26332462496`, target count 9). Product-YAML-only / no-WebFlash-exposure. Carries into product docs / caveats the **`J3` `out0`/`out1` silkscreen transposition** (pin-1 pad `IC2` `VOUT0` silk-labelled `out1`; pin-3 pad `IC2` `VOUT1` silk-labelled `out0`) and the **Cloudlift S12 harness / product-bench** residual recorded at [§`J2` / `J3` connector mapping — row 8](#j2--j3-connector-mapping--row-8-board-level-closed-harness-pending). | [`products/sense360-ceiling-poe-fandac.yaml`](../../products/sense360-ceiling-poe-fandac.yaml) (new product YAML; config string `Ceiling-POE-FanDAC`); [`config/product-catalog.json`](../../config/product-catalog.json) (new `hardware-pending` row, `webflash_build_matrix: false`); [`config/firmware-combination-matrix.json`](../../config/firmware-combination-matrix.json) + [`docs/firmware-build-gap-report.md`](../firmware-build-gap-report.md) (regenerated — `Ceiling-POE-FanDAC` reclassified `missing-product-yaml` → `blocked-hardware`); [`tests/test_dac_product_readiness.py`](../../tests/test_dac_product_readiness.py) (new); [`tests/test_compile_targets.py`](../../tests/test_compile_targets.py) + [`tests/test_fandac_package.py`](../../tests/test_fandac_package.py) (superseded guards updated); [`docs/product-readiness-matrix.md`](../product-readiness-matrix.md); [`docs/webflash-exposure-readiness-matrix.md`](../webflash-exposure-readiness-matrix.md); [`docs/release-artifact-readiness-matrix.md`](../release-artifact-readiness-matrix.md); [`UPCOMING_PR.md`](../../UPCOMING_PR.md). | **Product YAML landed (product-YAML-only / no-WebFlash-exposure).** The product composes Core ceiling + PoE PSU + base/health with the canonical FanDAC alias [`packages/expansions/fan_dac.yaml`](../../packages/expansions/fan_dac.yaml) (→ `fan_gp8403.yaml`). Outcome-first naming ("0-10V fan control" / "Cloudlift S12 fan control"); neutral package output IDs unchanged. **The full ESPHome `--compile` pass remains OWED** — only the compile-only metadata lane is green (PR #576); the product YAML and catalog row carry the `compile_validation_status: pending-ci` caveat. The compile-only skeleton [`products/compile-only/ceiling-poe-fandac.yaml`](../../products/compile-only/ceiling-poe-fandac.yaml) and its target are **unchanged** and remain separate. **No** WebFlash wrapper; **no** `webflash_build_matrix` flip (catalog row stays `false`); **no** `artifact_name`; **no** entry in [`config/webflash-builds.json`](../../config/webflash-builds.json) (the `FanDAC` token is absent there); **no** release artifact / checksum / build-info / `manifest.json` / `firmware/sources.json` / `.github/workflows/**` / `components/**` / `include/**` edit. **No** `schematic_status` / `schematic_file` promotion (`S360-312` stays `cataloged_unverified`). Enforces the `FanDAC` ↔ `AirIQ` mutex (no AirIQ token). Nextion / `J7` out of scope (the product binds no `uart:` / `display:`). **No** claim of simultaneous per-output 0–5 V + 0–10 V on a single GP8403. **`WEBFLASH-DAC-001`, `RELEASE-DAC-001`, and `WF-IMPORT-DAC-001` remain BLOCKED**; no WebFlash / release / compliance / hardware-stable readiness claim. Next: `FW-COMPILE-DAC-FULL-001` (record the owed manual `workflow_dispatch` `compile_mode=full` compile) or `WEBFLASH-DAC-001-READINESS-REFRESH`. Release-One, LED preview, FanTRIAC (`blocked` / `HW-005`), and the fan-driver `max-one-of` rule are unchanged. The WebFlash repository (`sense360store/WebFlash`) is untouched. |
| 2026-05-24 | `FW-COMPILE-DAC-FULL-RESULT-001` — record that the successful manual full-compile run owed since `FW-COMPILE-DAC-RESULT-001` (PR #576) has passed and that it **also validates the FanDAC compile-only target**. Inspected GitHub Actions run [`26364679370`](https://github.com/sense360store/esphome-public/actions/runs/26364679370) (the same run `FW-COMPILE-RELAY-FULL-RESULT-001` / PR #579 recorded), [`config/compile-only-targets.json`](../../config/compile-only-targets.json) at the validated ref (post-#578 `main`, merge commit `4906a22`), [`.github/workflows/compile-only.yml`](../../.github/workflows/compile-only.yml) (the `compile_mode=full` lane runs `scripts/validate_compile_targets.py --compile` against every target), and [`products/compile-only/ceiling-poe-fandac.yaml`](../../products/compile-only/ceiling-poe-fandac.yaml). | [`docs/compile-only-firmware-validation.md`](../compile-only-firmware-validation.md) (new `### 2026-05-24 — FW-COMPILE-DAC-FULL-RESULT-001` entry + forward-update note on the FW-COMPILE-DAC-RESULT-001 entry); [`docs/product-readiness-matrix.md`](../product-readiness-matrix.md) (§FanDAC / S360-312 audit bullet); [`docs/webflash-exposure-readiness-matrix.md`](../webflash-exposure-readiness-matrix.md) (§DAC / S360-312 WebFlash posture note); [`docs/release-artifact-readiness-matrix.md`](../release-artifact-readiness-matrix.md) (§DAC / S360-312 release posture note); this doc; [`UPCOMING_PR.md`](../../UPCOMING_PR.md). | **FanDAC full compile passed in run `26364679370`.** Run `26364679370`: workflow `Compile-only Firmware Validation`, event `workflow_dispatch`, mode `compile_mode=full`, status `completed`, conclusion `success`, **9** compile-only targets (job `Compile-only Targets — Metadata Validation` `77606314361` `success` → `Compile-only Targets — Full ESPHome Compile` `77606324332` `success`). The full-compile lane invokes `esphome compile` against every `config/compile-only-targets.json` target and fails on the first failure, so the `success` conclusion proves all nine compiled — including the 9th, `ceiling-poe-fandac-compile-only` → `products/compile-only/ceiling-poe-fandac.yaml` (`config_string: Ceiling-POE-FanDAC`), which was present in the manifest at `4906a22` with its YAML on disk. **The full-compile concern left owed by `FW-COMPILE-DAC-RESULT-001` (PR #576) is superseded** (PR #576 recorded only the green metadata lane — the full-compile job was `skipped` on PR #575's head). **The GP8403 `voltage: 10V` enum fix is now compile-validated** by ESPHome's own validator (not only the documented schema + string-equality tests). The `compile_validation_status: pending-ci` marker in `config/compile-only-targets.json` is satisfied by this run; flipping that literal config flag is a separate config-layer change outside this docs-only record. **`PRODUCT-DAC-001` has product YAML** ([`products/sense360-ceiling-poe-fandac.yaml`](../../products/sense360-ceiling-poe-fandac.yaml), PR #577) **but remains no-WebFlash / no-release** (`webflash_build_matrix: false`, no `artifact_name`, no `webflash_wrapper`, no `config/webflash-builds.json` row). **`WEBFLASH-DAC-001`, `RELEASE-DAC-001`, and `WF-IMPORT-DAC-001` remain blocked.** **No** `packages/**` / `products/**` / `products/webflash/**` / `config/**` / `scripts/**` / `.github/workflows/**` / `components/**` / `include/**` / `tests/**` / `firmware/**` / `manifest.json` / `firmware/sources.json` / release-artifact / checksum / build-info edit; **no** `webflash_build_matrix` flip; **no** `artifact_name`; **no** `webflash_wrapper`; **no** `release_one_required_configs` change; **no** `schematic_status` / `schematic_file` promotion (`S360-312` stays `cataloged_unverified`); **no** COMPLIANCE-001 movement; FanDAC / FanRelay code untouched. **No** claim of simultaneous per-output 0–5 V + 0–10 V on a single GP8403, and **no** WebFlash import / release / compliance / safety-certification / hardware-stable readiness claim. Compile success is necessary-but-insufficient for shipment readiness. The WebFlash repository (`sense360store/WebFlash`) is untouched. |
| 2026-05-24 | `COMPILE-STATUS-FLAGS-001` — reconcile the stale config-layer `compile_validation_status` flag that `FW-COMPILE-DAC-FULL-RESULT-001` (PR #580) deferred as "a separate config-layer change". Inspected [`config/compile-only-targets.json`](../../config/compile-only-targets.json) (the FanDAC target `ceiling-poe-fandac-compile-only` still carried `compile_validation_status: pending-ci`), the run `26364679370` evidence recorded by PR #579 / PR #580, and the two tests pinning the marker. | [`config/compile-only-targets.json`](../../config/compile-only-targets.json) (FanDAC target `compile_validation_status` `pending-ci` → `validated-full-compile`; `reason` / `notes` wording reconciled); [`tests/test_compile_targets.py`](../../tests/test_compile_targets.py) + [`tests/test_dac_product_readiness.py`](../../tests/test_dac_product_readiness.py) (the two `pending-ci` assertions updated to `validated-full-compile`); [`docs/compile-only-firmware-validation.md`](../compile-only-firmware-validation.md), [`docs/product-readiness-matrix.md`](../product-readiness-matrix.md), [`docs/webflash-exposure-readiness-matrix.md`](../webflash-exposure-readiness-matrix.md), [`docs/release-artifact-readiness-matrix.md`](../release-artifact-readiness-matrix.md), this doc, [`UPCOMING_PR.md`](../../UPCOMING_PR.md) (standing compile-status wording reconciled). | **`compile_validation_status: pending-ci` → `validated-full-compile`.** The FanDAC compile-only flag is reconciled to the state already proven green by run `26364679370` (`workflow_dispatch` / `compile_mode=full`, 9 targets, conclusion `success`). Narrow status reconciliation only. **No** real blocker moves: `PRODUCT-DAC-001` stays no-WebFlash / no-release; `WEBFLASH-DAC-001`, `RELEASE-DAC-001`, and `WF-IMPORT-DAC-001` stay **blocked**; `S360-312` `schematic_status` stays `cataloged_unverified`; **no** `webflash_build_matrix` flip; **no** `artifact_name`; **no** `webflash_wrapper`; **no** release artifact / tag / checksum / build-info; **no** `release_one_required_configs` change; **no** COMPLIANCE-001 movement. **No** `packages/**` / `products/**` / `products/webflash/**` / `.github/workflows/**` / `components/**` / `include/**` / `firmware/**` / `manifest.json` / `firmware/sources.json` edit; `config/product-catalog.json` and the product YAML are untouched (their full-compile-owed narrative is a separate follow-up). FanRelay carries no `compile_validation_status` field and is unchanged. **No** claim of simultaneous per-output 0–5 V + 0–10 V on a single GP8403, and **no** WebFlash import / release / compliance / safety-certification / hardware-stable readiness claim. The WebFlash repository (`sense360store/WebFlash`) is untouched. |

The next audit-log entry against this doc should appear when
committed evidence is added to the repository that closes any of
the [§Blockers remaining for PACKAGE-DAC-001](#blockers-remaining-for-package-dac-001)
items — for example, a logic-analyser DIP-switch I²C address
capture, a silkscreen reading of `J1` / `J2` / `J3`, a Core-side
`J7` bench reading that resolves the `+5V` / `+3.3V` rail
discrepancy, a GP8403 datasheet excerpt added under
`docs/hardware/`, or KiCad source for source-level pin
verification.

## BLOCKER-BURNDOWN-001 consolidation note (2026-05-26)

This board's blockers are consolidated into the cross-lane
[`docs/blocker-burndown.md`](../blocker-burndown.md) §2B (FanDAC /
S360-312). No new DAC evidence appeared this session: a Drive re-search
found only the already-recorded `Fan_GP8403` / `GP8403-Module` CAD / BOM
/ gerber set — **no** fan / harness artifact and **no** Cloudlift S12
product-bench artifact exist in Drive. The board-level rows stay
**CLOSED** (DIP-address truth table, range mechanism / policy, `J2`/`J3`
pin order + silk labels including the `J3` `out0`/`out1` transposition,
two-chip / four-output package). The residuals remain product / bench:
operator / bench confirmation of the `J3` silkscreen transposition, the
Cloudlift S12 harness conductor-by-conductor trace, and the Cloudlift
S12 product bench — see
[§Remaining `PACKAGE-DAC-001` blockers after this pass](#remaining-package-dac-001-blockers-after-this-pass).
The no-simultaneous-per-output-0–5 V/0–10 V constraint stays correct.
Recommended next FanDAC PR: **`S360-312-BENCH-EVIDENCE-REQUEST-001`**
(residuals converted into operator questions in
[`blocker-burndown.md` §5](../blocker-burndown.md#5-minimum-operator-checklist)).
This note makes no config / product / package / WebFlash / release /
compliance / `schematic_status` change and fabricates no evidence.

## DAC-BLOCKER-RECLASSIFY-001 — FanDAC remaining blockers reclassified by release scope (2026-05-27)

The FanDAC package / product / full-compile chain is **complete**
(`PACKAGE-DAC-001-IMPLEMENT-001` / PR #573, `FW-COMPILE-DAC-001` / PR #575,
`FW-COMPILE-DAC-RESULT-001` / PR #576, `PRODUCT-DAC-001` / PR #577,
`FW-COMPILE-DAC-FULL-RESULT-001` / PR #580, `COMPILE-STATUS-FLAGS-001`):
`compile_validation_status` is `validated-full-compile`, `voltage_enum_fixed`
is `true`, and the GP8403 `voltage: 10V` enum is compile-validated by
ESPHome's own validator in run
[`26364679370`](https://github.com/sense360store/esphome-public/actions/runs/26364679370)
(`workflow_dispatch` / `compile_mode=full`, 9 targets, conclusion
`success`). `WEBFLASH-DAC-001-READINESS` (PR #597) kept FanDAC **off**
WebFlash, and `BLOCKER-BURNDOWN-001` (PR #599) re-confirmed that **no new
DAC bench / harness / Cloudlift-S12 product-bench artifact exists in Drive**.
The remaining open items — the **`J3` `out0`/`out1` silkscreen
transposition** confirmation (`DAC-8b`), the **Cloudlift S12 harness**
conductor trace (`DAC-8c`), the **Cloudlift S12 product bench** (`DAC-8d`),
the **voltage-mode / product UX expectations** (`DAC-12`), the **WebFlash
live access / `S360-312` module-availability** classification (`DAC-15`),
the **`schematic_status` promotion** (`DAC-14`), and the **compliance /
safety approval** (unclaimed) — have, until now, been read as if they
blocked *everything*. This section **reclassifies** them by the surface
each one actually gates.

It is **documentation only** — a classification decision, not a new
evidence record. It records **no** bench measurement, flips **no** posture,
changes **no** package / product / config / WebFlash / firmware / release
behaviour, and relaxes **no** guardrail. It makes **no** WebFlash / import /
release / compliance / hardware-stable / Cloudlift-ready readiness claim and
asserts **no** harness / product-bench result. The **no simultaneous
per-output 0–5 V + 0–10 V on one GP8403** constraint (`DAC-7`) stays correct
and is **not** relaxed (register `0x01` is chip-level; one `V5V` reference
per chip wired to `+12V`).

### Decision

The remaining FanDAC `J3`-silk / harness / product-bench / voltage-UX /
WebFlash gaps are **no longer treated as blockers for repo / package /
product / config work**. They are reclassified as blockers **only** for
WebFlash exposure, release artifacts, import readiness, hardware-stable
promotion, the production voltage-control / product claim, the Cloudlift
S12 product claim, and compliance / safety claims. The non-claims stay
exactly intact.

**Not a blocker for** (these may proceed without new bench evidence):

- FanDAC **package implementation** ([`fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)
  / [`fan_dac.yaml`](../../packages/expansions/fan_dac.yaml) — two GP8403
  chips, four neutral outputs, per-chip address + range substitutions).
- FanDAC **product YAML** ([`products/sense360-ceiling-poe-fandac.yaml`](../../products/sense360-ceiling-poe-fandac.yaml)).
- FanDAC **compile-only target** (`ceiling-poe-fandac-compile-only`;
  `validated-full-compile`).
- **`config/` / product-catalog presence** of the FanDAC product row
  (`hardware-pending`, `webflash_build_matrix: false`).
- The **no-WebFlash product-readiness posture** (no wrapper, no
  `artifact_name`, no `config/webflash-builds.json` row).
- **Future clean repo / YAML / firmware cleanup PRs** that do **not**
  expose WebFlash / release artifacts and do **not** claim
  Cloudlift-ready / hardware-stable / compliance.

**Still a blocker for** (these stay gated until the bench / access
evidence lands):

- **WebFlash exposure** (wrapper, `config/webflash-builds.json` row,
  `webflash_build_matrix` flip, `S360-312` module-availability
  classification).
- **Release artifacts** (`artifact_name`, `.bin` / tag / SHA256 / MD5 /
  build-info `manifest.json` / release-proof row; `RELEASE-DAC-001`).
- **Import readiness** (`WF-IMPORT-DAC-001`).
- **Hardware-stable promotion** (`S360-312 schematic_status` stays
  `cataloged_unverified`; `schematic_file` unset).
- **Production voltage-control / product claim** (the `J3` silk
  orientation and the as-shipped voltage-mode UX).
- **Cloudlift S12 product claim** (harness trace + product bench).
- **Compliance / safety claims** (SELV board; no mains path, but no
  compliance sign-off is claimed).

### Scope classification table

| Blocker | Current evidence | Blocks package / product / config? | Blocks WebFlash / release? | Blocks hardware-stable? | Next evidence needed |
|---|---|---|---|---|---|
| **`J3` `out0`/`out1` silkscreen transposition** (`DAC-8b`) | Layout shows `J3` pin-1 net `2vout0` (`IC2` `VOUT0`) silk-labelled `out1`, pin-3 net `2vout1` silk-labelled `out0` — **transposed**; not operator/bench-confirmed | **No** | **Yes** — **product / installation-documentation and WebFlash / release blocker only** | Informs only | Operator / bench confirmation of the printed `J3` `out0`/`out1` text → `S360-312-BENCH-RESULT-001` |
| **Cloudlift S12 harness conductor trace** (`DAC-8c`) | No fan / harness artifact in Drive (re-confirmed PR #599) | **No** | **Yes** — **Cloudlift product-claim / WebFlash / release blocker only** | **No** | Bench / harness trace from `J2`/`J3` to the physical Cloudlift S12 fan input → `S360-312-BENCH-RESULT-001` |
| **Cloudlift S12 product bench** (`DAC-8d`) | Not captured | **No** | **Yes** — **Cloudlift product-claim / WebFlash / release blocker only** | **No** | Operator product-bench against a Cloudlift S12 load → `S360-312-BENCH-RESULT-001` |
| **Voltage-mode / product UX expectations** (`DAC-12`) | Per-chip range substitutions default `0-10V`, independently overridable; outcome-first naming planned; design decided, not exposed as product UX | **No** | **Yes** — **WebFlash / product UX blocker only** | **No** | Product-layer UX naming / exposure decision (`PRODUCT-DAC` follow-up); no per-output mix claim |
| **Production voltage-control / product claim** | Compile-validated drive; `J3` silk + voltage-UX not product-confirmed | **No** | **Yes** | Informs only | The `J3` silk + voltage-UX rows above |
| **WebFlash live access / `S360-312` module-availability** (`DAC-15`) | Read denied this session; `S360-312` not in any `module-availability.js` snapshot (drift #17) | **No** | **Yes** — **WebFlash exposure blocker only** | **No** | Restore `sense360store/WebFlash` read access → `WEBFLASH-DAC-LIVE-CHECK-001` |
| **WebFlash wrapper / build / artifact / import** (`DAC-15`, `RELEASE-DAC-001`, `WF-IMPORT-DAC-001`) | None | **No** | **Yes** | **No** | Wrapper + build-matrix + artifact, gated behind the bench evidence **and** the WebFlash live classification |
| **Release readiness** (`RELEASE-DAC-001`) | None; full-compile is necessary-but-insufficient | **No** | **Yes** | **No** | Release-proof chain after the WebFlash wrapper |
| **Hardware-stable promotion** (`schematic_status`, `DAC-14`) | `cataloged_unverified`; `schematic_file` unset | **No** | **No** | **Yes** | Operator decision + bench evidence via a separate JSON-only PR |
| **Per-output range mixing on one GP8403** (`DAC-7`) | Register `0x01` chip-level; one `V5V` per chip → `+12V`; **no** simultaneous per-output 0–5 V + 0–10 V claim | **No (constraint)** | Keep the no-mix guardrail | **No** | None — already encoded as a hard guardrail; must not be relaxed |
| **Compliance / safety approval** | SELV (5 V → 12 V boost); no mains path; no sign-off claimed | **No** | **No** | **No** | Release / compliance sign-off if a future surface requires it (`COMPLIANCE-001` mains gate does not apply) |

### Explicit scope markings (as required)

- **`J3` `out0`/`out1` silkscreen transposition** → **product /
  installation-documentation and WebFlash / release blocker only** (not a
  package / product-YAML blocker — the package binds neutral output IDs and
  does not depend on the printed silk).
- **Cloudlift S12 harness / product bench** → **Cloudlift product-claim /
  WebFlash / release blocker only** (not a package / product / config
  blocker).
- **Voltage-mode UX expectations** → **WebFlash / product UX blocker only**
  (the per-chip range design is decided; product-UX exposure is owed before
  WebFlash / a production voltage-control claim).
- **WebFlash live access** → **WebFlash exposure blocker only** (does not
  gate package / product / config, and does not gate hardware-stable).
- **Compliance / safety approval** → **release / compliance blocker only**
  (`COMPLIANCE-001` mains gate does not apply to this SELV board).

### Next implementation path

- **Clean repo / YAML / firmware PRs may proceed** provided they do **not**
  expose WebFlash / release artifacts and do **not** claim
  Cloudlift-ready / hardware-stable / compliance.
- **WebFlash wrapper / build / artifact / import PRs remain blocked**
  (`WEBFLASH-DAC-001` / `RELEASE-DAC-001` / `WF-IMPORT-DAC-001`), behind
  `WEBFLASH-DAC-LIVE-CHECK-001` (`sense360store/WebFlash` access) and the
  Cloudlift S12 bench / harness / `J3`-silk evidence.
- **`S360-312-BENCH-RESULT-001` remains a later evidence PR** (requested via
  `S360-312-BENCH-EVIDENCE-REQUEST-001`) that must land before any WebFlash
  exposure / release / hardware-stable promotion or Cloudlift-ready claim.

### Guardrails honoured / non-claims

This PR is **documentation-only**. It edits **no** `packages/**`,
`products/**`, `products/webflash/**`, `config/**`, `firmware/**`,
`manifest.json`, `firmware/sources.json`, release artifacts, checksums,
build-info manifests, any WebFlash repo file, `.github/workflows/**`,
`components/**`, or `include/**`. It changes **no** FanDAC package
behaviour, adds / edits **no** product YAML, adds **no** WebFlash wrapper,
flips **no** `webflash_build_matrix`, adds **no** `artifact_name` or
release artifact, and makes **no** WebFlash / import / release / compliance /
hardware-stable / Cloudlift-ready readiness claim. It promotes **no**
`schematic_status` (`S360-312` stays `cataloged_unverified`;
`schematic_file` unset), keeps the **no simultaneous per-output 0–5 V +
0–10 V on one GP8403** constraint correct, keeps the `FanDAC` ↔ `AirIQ`
mutex intact, and fabricates **no** evidence — it is a scope-classification
decision only. Release-One (`Ceiling-POE-VentIQ-RoomIQ` / `stable`), the
LED preview (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`), and FanTRIAC
(`blocked` / `HW-005`) are unchanged. The WebFlash repository
(`sense360store/WebFlash`) is untouched.

## S360-312-BENCH-EVIDENCE-REQUEST-001 — FanDAC bench evidence checklist & contract (2026-05-27)

This section turns the still-open FanDAC bench blockers
(`DAC-8b` / `DAC-8c` / `DAC-8d` / `DAC-12` in
[`blocker-burndown.md` §2B](../blocker-burndown.md#2b-fandac--s360-312))
into one **operator-answerable checklist** and an explicit **pass/fail
evidence contract**, so a later `S360-312-BENCH-RESULT-001` is small and
evidence-backed. It is **documentation only**: it requests evidence, it does
not record results, change behaviour, or relax any guardrail in
[§DAC-BLOCKER-RECLASSIFY-001](#dac-blocker-reclassify-001--fandac-remaining-blockers-reclassified-by-release-scope-2026-05-27).
The lane is **bench / operator / WebFlash-access gated, not repo gated** —
package, product, and full-compile are complete (`DAC-10` / `DAC-11`
CLOSED; `compile_validation_status: validated-full-compile`,
`voltage_enum_fixed: true`, run
[`26364679370`](https://github.com/sense360store/esphome-public/actions/runs/26364679370)).

### Drive re-search result (2026-05-27)

A fresh Drive search for new FanDAC bench evidence (`S360-312`,
`S360-312-R4`, `FanDAC`, `GP8403`, `Cloudlift`, `Cloudlift S12`, `0-10V`,
`VOUT`, `voltage reading`, `DAC bench`, `harness`, photos / videos /
spreadsheets / logs) found **no bench artifact**. The only FanDAC-bearing
material is **design / CAD only**:

- the `Fan_GP8403` design set (owner `neilmcrae@googlemail.com`):
  `Fan_GP8403.kicad_sch` plus the timestamped `Fan_GP8403-*.zip` gerber /
  CPL snapshot series (2025-08 → 2026-01), and the related `GP8403.zip` /
  `GP8403-Module` folder — the same BOM/CAD class cross-checked in
  [§BOM cross-check](#bom-cross-check);
- the canonical `S360-312-R4.pdf` schematic (owner
  `kanyugistash@gmail.com`, modified 2026-05-16) — already committed,
  byte-identical, as
  [`schematics/S360-312-R4.pdf`](schematics/S360-312-R4.pdf);
- the unchanged `Sense360_R4_Tracker` (2026-05-18).

None of these is a `J3` `out0`/`out1` silkscreen photo, a Cloudlift S12
harness conductor trace, a per-channel output-voltage reading, a
voltage-mode (0–10 V / 0–5 V) sweep, a noise / flicker / thermal
observation, or a product-bench sign-off. This is **board design /
manufacturing provenance**, recorded for provenance only; it closes **no**
bench blocker and **no Drive file is committed by this PR and no bench
evidence is fabricated.**

### Operator checklist (fill in and attach evidence)

Every row is answerable by the hardware owner at the bench. Leave a row
`UNANSWERED` rather than guessing. Each row names the blocker it feeds.

| # | Item | Answer (operator fills in) | Feeds |
|---|---|---|---|
| 1 | **Board revision tested** (silkscreen P/N + rev; note if blank per tracker `G01`) | | DAC-8b |
| 2 | **`J3` `out0`/`out1` silkscreen transposition** — confirm the printed text: layout shows `J3` pin-1 net `2vout0` (`IC2` `VOUT0`) silk-labelled `out1`, pin-3 net `2vout1` silk-labelled `out0`. Is the silk **transposed** as the layout suggests? (yes / no; read the actual printed text) | | DAC-8b |
| 3 | **Actual `J3` channel mapping observed** — drive `IC2` `VOUT0` and `VOUT1` one at a time and record which physical `J3` pin each appears on (pin-1 / pin-2 GND / pin-3) | | DAC-8b |
| 4a | **Voltage mode tested — 0–10 V?** (`${fan_dac_voltage_mode}` `10V`; did you test it?) | | DAC-12 |
| 4b | **Voltage mode tested — 0–5 V?** (`5V` alternate; tested or not — leave `NOT TESTED` if untested) | | DAC-12 |
| 5 | **Both DAC channels tested** (which of `J2` ch0/ch1 + `J3` ch0/ch1 were exercised) | | DAC-8d |
| 6 | **Both channels tested simultaneously** (were two/four outputs driven at once, or one at a time?) | | DAC-8d |
| 7 | **Controlled load / device tested** (Cloudlift S12, multimeter / DMM, fan simulator, scope probe, or other — name it) | | DAC-8d |
| 8 | **Harness used** (Cloudlift S12 harness, custom harness, bare probe / none — describe `J2`/`J3` → load wiring) | | DAC-8c |
| 9a | **Voltage readings — low / 0 % command** (V at the output) | | DAC-12 |
| 9b | **Voltage readings — medium / 25–50 % command** (V) | | DAC-12 |
| 9c | **Voltage readings — high / 75–100 % command** (V) | | DAC-12 |
| 10 | **Did increasing command increase output voltage?** (monotonic 0 → full; yes / no) | | DAC-12 |
| 11 | **Do the channel labels match expected UI / product behaviour?** (does the channel the UI calls "out0" / fan-1 drive the physically expected `J3` pin / fan, given the silk in item 2?) | | DAC-8b / DAC-12 |
| 12 | **Noise / flicker / instability** (output ripple, jitter, audible fan flicker, settling behaviour) | | DAC-8d |
| 13 | **Thermal observation** (GP8403 / MT3608 boost / board warmth under sustained 4-output drive — duration + qualitative or measured) | | DAC-8d |
| 14 | **Photos / videos / logs attached** (silk close-ups, DMM shots, scope captures, ESPHome log) | | all |
| 15 | **Operator / date / source / provenance** (who, when, board serial, Drive path of uploaded evidence) | | all |

### Pass/fail evidence contract

What evidence **closes** each open bench blocker, and what does **not**.

| Blocker | Closes when (PASS) | Does NOT close / FAIL |
|---|---|---|
| **`J3` silkscreen transposition (`DAC-8b`)** | A photo / direct reading of the printed `J3` `out0`/`out1` silk **plus** the observed channel-mapping (item 3) confirming which `J3` pin carries `IC2` `VOUT0` vs `VOUT1`, with the transposition answered yes/no (items 1–3, 11). | A layout-only inference with no read of the printed board; or "looks right" with no per-channel drive test. |
| **Cloudlift S12 harness trace (`DAC-8c`)** | A conductor-by-conductor trace from `J2`/`J3` pins to the physical Cloudlift S12 fan input, identifying the harness used (items 7–8). | Datasheet / assumed pinout with no traced harness; "should map straight through" without verification. |
| **Cloudlift S12 product bench (`DAC-8d`)** | Operator end-to-end sign-off driving both channels (and ideally simultaneously) into the controlled load, with noise/flicker + thermal observation and operator/date/serial + attached evidence (items 5–7, 12–15). | A compile-pass or package test treated as a product bench; a single-channel spot check called a full bench. |
| **Voltage-mode / output linearity (`DAC-12`)** | Output-voltage readings at low/medium/high (or 0/25/50/75/100 %) for the mode(s) tested, showing increasing command → increasing output, with the 0–10 V (and 0–5 V if tested) mode recorded (items 4a–4b, 9a–10). | Mode asserted but not measured; no recorded command→output direction; a per-output 0–5 V + 0–10 V mix claim on one GP8403 (forbidden by `DAC-7`). |

### Out of scope (stays blocked regardless of this checklist)

These are **not** unlocked by any answer above and must not be claimed:

- **Per-output range mixing on one GP8403** — register `0x01` is chip-level
  and each GP8403 has a single `V5V` reference wired to `+12V`; **no**
  simultaneous per-output 0–5 V + 0–10 V on one chip (`DAC-7`, hard
  guardrail). Two-range operation needs one channel from each of `IC1` /
  `IC2`.
- **WebFlash exposure** — no wrapper, no `config/webflash-builds.json` row,
  no `webflash_build_matrix` flip, no `artifact_name`; gated and
  additionally `NEEDS WEBFLASH ACCESS` (`DAC-15`; `S360-312` not in any
  `module-availability.js` snapshot — drift #17).
- **Release artifact** — no `.bin` / tag / checksum / build-info
  (`RELEASE-DAC-001` stays blocked).
- **Import readiness** — `WF-IMPORT-DAC-001` stays blocked behind
  `RELEASE-DAC-001` (WebFlash-owned).
- **Hardware-stable promotion** — `S360-312` `schematic_status` stays
  `cataloged_unverified` (`schematic_file` unset); promotion is a separate
  JSON-only PR (`DAC-14`), not this checklist, unless policy explicitly
  allows.
- **Cloudlift-ready / production voltage-control product claim** — informed
  by the rows above but a separate product-layer decision; not claimed here.
- **Compliance approval** — board is SELV (5 V → 12 V boost, no mains), so
  `COMPLIANCE-001` does not apply; the thermal item is characterisation,
  not certification.

### Next-PR recommendation

- **If the operator uploads / answers the checklist and attaches bench
  evidence** → **`S360-312-BENCH-RESULT-001`** records the results and
  closes the bench rows it actually proves.
- **While evidence is still missing** (the case today) →
  **`S360-312-BENCH-RESULT-001` remains gated** until the operator uploads
  or answers the checklist above; no FanDAC bench row can close in a
  docs-only pass.
- **WebFlash wrapper / build PRs stay blocked**
  (`WEBFLASH-DAC-001` / `RELEASE-DAC-001` / `WF-IMPORT-DAC-001`); the
  live-access re-check `WEBFLASH-DAC-LIVE-CHECK-001` stays queued behind
  `sense360store/WebFlash` access restoration.

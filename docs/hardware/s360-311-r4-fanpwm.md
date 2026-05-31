# S360-311-R4 FanPWM — Standalone Hardware Reference (HW-PINMAP-311-FOLLOWUP)

## Status

**Status: partial — schematic evidence available; package reconciliation pending. This reference resolves none of the open reconciliation questions, closes no gate, and does not unblock the S360-311 board package.**

This document is the per-board hardware reference for the Sense360 PWM
12 V fan-driver board, revision R4 (`S360-311-R4`), produced under
`HW-PINMAP-311-FOLLOWUP`. It follows the per-board reference pattern of
[`s360-200-r4-roomiq.md`](s360-200-r4-roomiq.md),
[`s360-211-r4-ventiq.md`](s360-211-r4-ventiq.md),
[`s360-300-r4-led.md`](s360-300-r4-led.md), and its FanDAC sibling
[`s360-312-r4-fandac.md`](s360-312-r4-fandac.md), and it complements the
broader HW-PINMAP-311 reconciliation audit at
[`s360-311-r4-pwm.md`](s360-311-r4-pwm.md).

This reference transcribes the connector and pin map **exactly as the
committed module-side schematic shows** and records every open
reconciliation question as **STILL OWED**. It is **documentation only**.
It resolves nothing: per
[`docs/cleanup-audit.md`](../cleanup-audit.md) the reconciliation itself
needs silkscreen, harness, and bench evidence plus the systemic Core
abstract-bus resolution, none of which this reference performs.

The sole evidence source for the pin map below is the committed
module-side schematic PDF
[`docs/hardware/schematics/S360-311-R4.pdf`](schematics/S360-311-R4.pdf)
(HW-ASSETS-003; SHA256
`c910b3364be1d58fc44d12b5a189dade47efddf6cae158a86577ec7501e48006`;
91,543 bytes; KiCad 10.0.3 export; single sheet `S360-311-R4.kicad_sch`,
A4, Id 1/1, Date / Title / Rev fields blank). Every connector / pin / net
claim in this document is sourced from a visible label or symbol on that
single schematic sheet, as already inventoried in
[`docs/hardware/artifacts/S360-311-R4.md` §What the schematic appears to contain](artifacts/S360-311-R4.md#what-the-schematic-appears-to-contain).

## Purpose and scope

This reference does **not**:

- change any value in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  (`S360-311` stays `schematic_status: cataloged_unverified`, no
  `schematic_file` set),
  [`config/product-catalog.json`](../../config/product-catalog.json),
  [`config/webflash-builds.json`](../../config/webflash-builds.json),
  or [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json),
- flip `S360-311` `schematic_status` or mark it `verified` /
  `pin-map-confirmed`,
- set `schematic_file` for `S360-311`,
- edit any package YAML —
  [`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml),
  [`packages/expansions/sense360_fan_pwm.yaml`](../../packages/expansions/sense360_fan_pwm.yaml),
  [`packages/expansions/gpio_expander_sx1509.yaml`](../../packages/expansions/gpio_expander_sx1509.yaml),
  [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml),
  and [`packages/hardware/sense360_core.yaml`](../../packages/hardware/sense360_core.yaml)
  all stay unchanged,
- mark [`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml)
  `confirmed-ok` — it stays `package-yaml-pending` /
  `needs-package-reconciliation`,
- resolve the SX1509-expander-vs-direct-ESP32-GPIO mapping disagreement,
  the UART-on-`J3`-pins-11/12 routing question, the `"NINE 4pin FANs"`
  section-title question, or the single-channel-vs-four-channel
  canonical-abstraction decision (see
  [§Open reconciliation questions (still owed)](#open-reconciliation-questions-still-owed)),
- promote the board to a package, add any product YAML under
  [`products/`](../../products/), a WebFlash wrapper under
  [`products/webflash/`](../../products/webflash/), a build-matrix
  entry, a release, a tag, or a WebFlash import,
- regenerate firmware, create a GitHub Release or tag, or change any
  WebFlash manifest / `firmware/sources.json` / `manifest.json`,
- change Release-One (`Ceiling-POE-VentIQ-RoomIQ`, version `1.0.0`,
  channel `stable`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag `v1.0.0`),
- change the LED preview path (`Ceiling-POE-VentIQ-RoomIQ-LED` stays
  `status: preview`, `channel: preview`),
- unblock FanTRIAC (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays
  `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`),
- change the mains-voltage compliance status of `S360-320` or `S360-400`
  (owned by COMPLIANCE-001),
- edit the schematic PDF
  [`docs/hardware/schematics/S360-311-R4.pdf`](schematics/S360-311-R4.pdf)
  (byte-identical to the HW-ASSETS-003 commit) or the curated artifact
  index [`docs/hardware/artifacts/S360-311-R4.md`](artifacts/S360-311-R4.md),
- touch the WebFlash repository (`sense360store/webflash`) — that repo is
  out of scope for this PR.

If this reference and any source-of-truth document drift, **the
source-of-truth document wins** and this reference must be updated. The
authoritative artifact-side record for this board is
[`docs/hardware/artifacts/S360-311-R4.md`](artifacts/S360-311-R4.md); the
authoritative Core-side capture lives in
[`docs/hardware/s360-100-r4-core.md`](s360-100-r4-core.md); the
authoritative full pin-map reconciliation audit (with the evidence-pass
audit log and bench records) is
[`docs/hardware/s360-311-r4-pwm.md`](s360-311-r4-pwm.md).

## Board identity

Mirrored from
[`config/hardware-catalog.json`](../../config/hardware-catalog.json)
lines 72–81 without modification.

| Field | Value |
|---|---|
| `group` | `Inline` |
| `type` | `Driver` |
| `friendly_name` | `Sense360 PWM` |
| `sku` | `S360-311` |
| `rev` | `R4` |
| `old_name` | `12vFan_PWM_PulseCounter` |
| `description` | `12V PWM fan driver, up to 4 fans with tach feedback.` |
| `schematic_status` | `cataloged_unverified` (unchanged by this PR) |
| `schematic_file` | _(not set; unchanged by this PR)_ |
| Curated artifact index | [`docs/hardware/artifacts/S360-311-R4.md`](artifacts/S360-311-R4.md) (HW-ASSETS-003) |
| Committed schematic PDF | [`docs/hardware/schematics/S360-311-R4.pdf`](schematics/S360-311-R4.pdf) (HW-ASSETS-003) |
| Per-board reconciliation audit | [`s360-311-r4-pwm.md`](s360-311-r4-pwm.md) (HW-PINMAP-311) |
| FanPWM package YAML | [`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml) (single-channel; `package-yaml-pending`) |

## Evidence table

| Evidence | Source | Status |
|---|---|---|
| Module-side schematic PDF | [`docs/hardware/schematics/S360-311-R4.pdf`](schematics/S360-311-R4.pdf) (HW-ASSETS-003; SHA256 `c910b3364be1d58fc44d12b5a189dade47efddf6cae158a86577ec7501e48006`; 91,543 bytes) | **Committed.** Byte-identical to upload. Single sheet (`S360-311-R4.kicad_sch`, Id 1/1), KiCad 10.0.3 export, A4. The only pin-map source for this reference. |
| Curated artifact index | [`docs/hardware/artifacts/S360-311-R4.md`](artifacts/S360-311-R4.md) | **Committed.** Schematic-content capture + retained-but-not-committed inventory. Not edited by this PR. |
| HW-PINMAP-311 audit | [`s360-311-r4-pwm.md`](s360-311-r4-pwm.md) | **Committed.** Full reconciliation audit; this reference complements it. |
| Core-side `J6` capture | [`s360-100-r4-core.md` §J6](s360-100-r4-core.md#j6--12-v-pwm-fan-connector-13-pin) | **Committed.** Net list `+5V`, `GND`, `TachIO`, `TachPMW1..4`, `Pul_Cou1..4` (11 nets); 1-to-13 pin order explicitly flagged **verify** against silkscreen. Does **not** list any UART pins. |
| Module-side BOM spreadsheet | _(not provided in this upload)_ | **Pending.** Unlike the FanDAC board, no `12vFan_PWM_PulseCounter` BOM has been committed alongside this reference; component part numbers below are only those printed on the schematic sheet. |
| Silkscreen / harness inspection | _(not provided)_ | **Pending.** Required for the Core `J6` ↔ module `J3` 1-to-13 pin order and the 13-pin harness conductor mapping. |
| Bench / scope / waveform capture | _(not provided here)_ | **Pending.** Required for per-fan PWM drive (`TachPMW*`), per-fan tach feedback (`Pul_Cou*`), the shared open-drain `TachIO`, PWM polarity, and pulses-per-revolution. (Operator functional-bench attestations are recorded in [`s360-311-r4-pwm.md`](s360-311-r4-pwm.md); they are not re-litigated or upgraded here.) |
| KiCad schematic source / PCB source / project metadata | _(not provided)_ | **Pending.** Source-level pin / net verification gated on this upload. |
| CPL / Gerbers / drill / STEP / board images | _(not provided)_ | **Pending.** Fab / mechanical / visual verification gated on these. |

## Schematic summary

This section restates only what is directly visible in the committed
schematic PDF
[`docs/hardware/schematics/S360-311-R4.pdf`](schematics/S360-311-R4.pdf).
It does **not** invent electrical characteristics, transistor topology,
timing guarantees, MOSFET ratings, PWM polarity, or pull-up assumptions
beyond what is labelled on the sheet.

- **Voltage Boost section.** `MT3608` boost converter (`U1`) with input
  inductor `L1 22 µH`, Schottky `D1 SS34`, feedback divider `R3 38 kΩ`
  (upper leg) / `R5 2 kΩ` (lower leg), input cap `C1 22 µF / 10 V`,
  output cap `C2 22 µF / 10 V`, output indicator `R4 330 Ω` + blue LED
  `D2`. `U1` pin labels on the sheet: pin 5 `IN`, pin 1 `SW`, pin 4 `EN`,
  pin 3 `FB`, pin 2 `GND`. Boosts the Core-supplied `+5V` rail up to
  `+12V` for the fan outputs. No claim on rated output current is made —
  that requires bench evidence and inductor / Schottky thermal
  characterisation.
- **Fan outputs section** (printed sheet title `"NINE 4pin FANs"`; see
  [§Open reconciliation questions (still owed)](#open-reconciliation-questions-still-owed)
  #3). **Four** 4-pin fan output connectors are present: `J1`, `J2`,
  `J4`, `J5`. Each fan connector carries `+12V`, `GND`, one `Pul_Cou*`
  net, and one `TachPMW*` net, and is paired with one low-side
  N-channel MOSFET (`Q_NMOS_GSD` — `Q1..Q4`) on the `TachPMW*` gate path,
  with a 1 kΩ gate resistor (`R1`, `R2`, `R6`, `R7`); drain wired to the
  shared `TachIO` net; source to `GND`.
- **"From Core"** module-side connector `J3` — 13-pin. Pin / net table
  exactly as labelled in the PDF:

  | Module `J3` pin | Net |
  |---:|---|
  | 1 | `+5V` |
  | 2 | `TachIO` |
  | 3 | `TachPMW1` |
  | 4 | `Pul_Cou1` |
  | 5 | `TachPMW2` |
  | 6 | `Pul_Cou2` |
  | 7 | `TachPMW3` |
  | 8 | `Pul_Cou3` |
  | 9 | `TachPMW4` |
  | 10 | `Pul_Cou4` |
  | 11 | `UART_RX` |
  | 12 | `UART_TX` |
  | 13 | `GND` |

- **"NEXTION DISPLAY"** module-side connector `J6` — 4-pin:

  | Module `J6` pin | Net | Schematic annotation |
  |---:|---|---|
  | 1 | `+5V` (`V IN`) | Display supply input |
  | 2 | `ESP32_TXD` / `UART_TX` | "To screen RX" |
  | 3 | `ESP32_RXD` / `UART_RX` | "To screen TX" |
  | 4 | `GND` | Common ground |

  The UART pair on module `J6` is the on-board route from module `J3`
  pins 11 / 12 (`UART_RX` / `UART_TX`).
- **Mounting holes** `H1`, `H2`, `H3`, `H4`.

Everything beyond the list above — module dimensions, layer stackup,
PCB silkscreen pin-1 markers, fab notes, harness identity, exact MT3608
thermal headroom, per-fan rated current, MOSFET part-number ratings (the
symbol is `Q_NMOS_GSD`, not a populated part number), PWM polarity, tach
pull-up source, or any electrical / timing claim — is **unknown** and
would require the retained-but-not-committed KiCad source / PCB / BOM /
CPL / Gerbers / drill / STEP / board images or bench evidence per
[`hardware-artifact-policy.md`](hardware-artifact-policy.md).

## Pin / connector reference

### Module-side `J3` ↔ Core-side `J6` (13-pin harness)

The two connectors mate via a 13-pin Core ↔ module harness. The
module-side `J3` capture is **schematic-confirmed** against the committed
S360-311-R4 PDF. The Core-side `J6` capture in
[`s360-100-r4-core.md` §J6](s360-100-r4-core.md#j6--12-v-pwm-fan-connector-13-pin)
records the net list but explicitly flags the 1-to-13 pin order as
**verify** against the silkscreen
([`s360-100-r4-core.md` Open Questions #9](s360-100-r4-core.md#open-questions--verification-needed)).

| Element | Core side (`J6`) | Module side (`J3`) | Reconciliation status |
|---|---|---|---|
| Connector identity | `J6` — 12 V PWM fan connector (13-pin) | `J3` — "From Core" (13-pin) — schematic-confirmed | Naming mismatch is expected (each board labels its own connectors); the 13-pin pin count matches. |
| Signal nets | `+5V`, `GND`, `TachIO`, `TachPMW1..4`, `Pul_Cou1..4` (11 nets) | `+5V`, `GND`, `TachIO`, `TachPMW1..4`, `Pul_Cou1..4`, **`UART_RX`**, **`UART_TX`** | **Module side carries two additional nets (`UART_RX` / `UART_TX`) the Core-side capture does not document.** Owed; see [§Open reconciliation questions (still owed)](#open-reconciliation-questions-still-owed) #2. |
| 1-to-13 pin order | **`verify`** against silkscreen | Schematic-only — order exactly as labelled in the PDF | Schematic-only on the module side; **requires silkscreen verification** to confirm conductor-by-conductor mapping. Owed to HW-PINMAP-311 reconciliation + bench evidence. |

### Module-side fan outputs `J1` / `J2` / `J4` / `J5` (4-pin each)

Four 4-pin fan output connectors. The schematic assigns the `TachPMW*` /
`Pul_Cou*` nets per connector as follows (note the schematic's non-sequential
connector-to-channel pairing):

| Connector | Pin 1 | Pin 2 | Pin 3 (`Pul_Cou*`, tach) | Pin 4 (`TachPMW*`, PWM gate) | Low-side N-FET (gate resistor) |
|---|---|---|---|---|---|
| `J1` | `+12V` | `GND` | `Pul_Cou1` | `TachPMW1` | `Q1` (`R1 1 kΩ`) |
| `J2` | `+12V` | `GND` | `Pul_Cou3` | `TachPMW3` | `Q2` (`R2 1 kΩ`) |
| `J4` | `+12V` | `GND` | `Pul_Cou2` | `TachPMW2` | `Q3` (`R6 1 kΩ`) |
| `J5` | `+12V` | `GND` | `Pul_Cou4` | `TachPMW4` | `Q4` (`R7 1 kΩ`) |

Each `Q_NMOS_GSD` MOSFET has its drain tied to the shared `TachIO` net and
its source to `GND`. This is recorded as **observed schematic topology**,
not as verified design intent. The schematic does **not** state:

- whether `TachPMW*` is the PWM drive signal or only an open-drain
  pull-down for a tach-share scheme (the net name is ambiguous on its
  own),
- whether the per-fan `Pul_Cou*` connector pin is direct tach feedback
  passed through to the Core or whether the module buffers / level-shifts
  it,
- the per-fan rated current, the MOSFET's actual ratings, PWM polarity
  (active-high vs active-low for the low-side gate), or any thermal
  characterisation.

Bench / harness / waveform evidence is **owed**.

### Module-side `J6` (NEXTION DISPLAY, 4-pin)

`+5V` (`V IN`), `ESP32_TXD` / `UART_TX` (to screen RX), `ESP32_RXD` /
`UART_RX` (to screen TX), `GND`. The UART pair routes on-board from
module `J3` pins 11 / 12. The source of the Nextion `+5V` rail and
whether the UART pair actually arrives over the 13-pin Core `J6` cable
are **open** — see
[§Open reconciliation questions (still owed)](#open-reconciliation-questions-still-owed)
#2.

### Core-side fan-path origin (for context, not changed here)

On the Core side, the FanPWM signal origins are captured in
[`s360-100-r4-core.md` §Fan / driver outputs](s360-100-r4-core.md#fan--driver-outputs)
and in the FanPWM package binding chain. The
SX1509-expander-vs-direct-ESP32-GPIO disagreement on those origins is
recorded as still owed in
[§Open reconciliation questions (still owed)](#open-reconciliation-questions-still-owed)
#1; this reference does not adjudicate it and does not edit
[`s360-100-r4-core.md`](s360-100-r4-core.md) or any package YAML.

## Open reconciliation questions (still owed)

Every question below remains **STILL OWED**. This reference resolves none
of them. The authoritative running record (with the dated evidence-pass
audit log) is
[`s360-311-r4-pwm.md`](s360-311-r4-pwm.md); the items below restate the
gates and name the specific evidence that would close each one.

### 1. SX1509-expander-vs-direct-ESP32-GPIO mapping disagreement — STILL OWED

The Core abstract packages bind FanPWM to direct ESP32 expansion GPIOs:
[`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml)
binds `fan_pwm_pin: ${expansion_gpio1}` (= `GPIO5`) /
`fan_tach_pin: ${expansion_gpio2}` (= `GPIO6`), and
[`packages/hardware/sense360_core.yaml`](../../packages/hardware/sense360_core.yaml)
binds `expansion_gpio1` / `expansion_gpio2` to `GPIO4` / `GPIO5`. The
SX1509 channel map in
[`packages/expansions/gpio_expander_sx1509.yaml`](../../packages/expansions/gpio_expander_sx1509.yaml)
reserves channels 0–3 for fan PWM and 4–7 for tach, while the shared
`TachIO` net is the direct ESP32 `IO16` passthrough. These three pictures
do not agree.

- **Owner.** The systemic Core abstract-bus rebind, `CORE-ABSTRACT-BUS-001`,
  aliased to
  [`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3](../release-one-hardware-audit.md#required-follow-ups).
  **Not** this reference, and **not** HW-PINMAP-311-FOLLOWUP.
- **Evidence that would close it.** Operator-attested silkscreen reading of
  the Core-side fan-signal origins, a documented Core abstract-bus rebind
  (or retirement decision) under `CORE-ABSTRACT-BUS-001`, and bench /
  scope confirmation that each `TachPMW*` / `Pul_Cou*` net is driven from
  the asserted GPIO / SX1509 channel. The canonical Core-side fan GPIO map
  candidate is tracked separately at
  [`s360-100-native-fan-gpio-map.md`](s360-100-native-fan-gpio-map.md);
  this reference does not assert it as resolved.

### 2. UART on `J3` pins 11 / 12 — STILL OWED

Module `J3` labels pins 11 / 12 as `UART_RX` / `UART_TX` and routes them
on-board to the Nextion display connector `J6`. The Core-side `J6`
capture in
[`s360-100-r4-core.md` §J6](s360-100-r4-core.md#j6--12-v-pwm-fan-connector-13-pin)
does **not** list any UART pins on the 13-pin connector (only the 11
power / signal nets). Two schematic-internally-consistent possibilities
remain, and this reference chooses **neither**:

1. the Core-side `J6` capture is incomplete and must be extended to record
   the UART pair on pins 11 / 12, or
2. the Nextion UART pair reaches the module via a **separate** harness, in
   which case module `J3` pins 11 / 12 are not populated on the 13-pin
   Core cable.

- **Owner.** HW-PINMAP-311 reconciliation evidence pass.
- **Evidence that would close it.** Operator-attested silkscreen reading
  of the Core-side `J6` pins 11 / 12, a conductor-by-conductor inspection
  of the physical 13-pin Core ↔ module harness, and identification of
  which ESP32 UART (if any) the pair binds to. Until then, the Nextion
  `+5V` source likewise stays open.

### 3. `"NINE 4pin FANs"` section title vs four visible outputs — STILL OWED

The schematic fan-section title reads `"NINE 4pin FANs"`, but only
**four** 4-pin fan output connectors are visible on the sheet (`J1`,
`J2`, `J4`, `J5`). The hardware-catalog description (`up to 4 fans`)
matches the four visible connectors; the `"NINE"` label is unexplained.
Whether the title is a stale label copied from another design, a marker /
project code, or an undelivered intent is **unresolved**. This is a
**documentation question only**, not a wiring change.

- **Owner.** HW-PINMAP-311 reconciliation evidence pass / design provenance.
- **Evidence that would close it.** A design-provenance note from the
  board author, the KiCad schematic source title block, or board images /
  silkscreen confirming exactly four populated fan connectors.

### 4. Single-channel-vs-four-channel canonical abstraction — STILL OWED

[`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml)
binds **one** channel (`output.platform: ledc`, `pin: ${fan_pwm_pin}`;
`sensor.platform: pulse_counter`, `pin.number: ${fan_tach_pin}`), while
the board exposes **four** fan outputs. The legacy four-channel package
[`packages/expansions/sense360_fan_pwm.yaml`](../../packages/expansions/sense360_fan_pwm.yaml)
binds four channels with direct ESP32 GPIO mappings
(`fan1..4_pwm_pin` / `fan1..4_tach_pin` / `tach_io_pin` /
`nextion_*_pin`) that **also** disagree with the schematic, and is
consumed only by the `legacy-compatible`
[`products/sense360-fan-pwm.yaml`](../../products/sense360-fan-pwm.yaml).
Which cardinality is canonical for the `FanPWM` token is **undecided**.

- **Owner.** `PACKAGE-PWM-001` (alias: `PACKAGE-GAP-001` FanPWM slice)
  package-design decision, paired with `CORE-ABSTRACT-BUS-001`.
- **Evidence that would close it.** A recorded package-design decision
  (one logical channel vs four), the resolved Core-side GPIO / SX1509
  routing from question #1, and bench confirmation that the chosen
  abstraction drives all intended fan outputs with valid tach feedback.

## What this reference does not assert

- It does **not** claim any silkscreen, harness, scope, multimeter, or
  manufacturing-artifact (KiCad source / PCB / BOM / CPL / Gerber / drill /
  STEP / board image) review has been performed for `S360-311-R4`. None of
  those artifacts are committed.
- It does **not** promote any row of
  [`s360-311-r4-pwm.md`](s360-311-r4-pwm.md) away from its current value,
  close any of its Known unresolved issues, or close the
  [`s360-100-r4-core.md` Open Questions #9](s360-100-r4-core.md#open-questions--verification-needed)
  `J6` 1-to-13 verify flag (owned by `S360-100-BENCH-001`).
- It does **not** advance `PACKAGE-PWM-001`, `PRODUCT-PWM-001`,
  `WEBFLASH-PWM-001`, `RELEASE-PWM-001`, `WF-IMPORT-PWM-001`, or
  `CORE-ABSTRACT-BUS-001`.
- The board package and the `S360-311` `schematic_status` promotion stay
  **gated** on the owed silkscreen / harness / bench evidence and the
  systemic Core abstract-bus resolution.

## Design-complete status (PRE-HW-PREP-FW-311-001)

`S360-311` is **design-complete** as of `PRE-HW-PREP-FW-311-001`
(2026-05-31), slice 3 of
[`docs/pre-hardware-prep-plan.md`](../pre-hardware-prep-plan.md).

**`design-complete` is a prose / documentation annotation only.** It is
deliberately **not** `verified`: it does **not** flip `schematic_status`
(which stays `cataloged_unverified`), does **not** change `S360-311`'s
lifecycle (`hardware-pending`), does **not** set `schematic_file`, and
does **not** enable any WebFlash exposure or release surface (per
[`pre-hardware-prep-plan.md` §1.2 / §1.4](../pre-hardware-prep-plan.md#12-what-design-complete-is-explicitly-not)).
A `design-complete` board stays `cataloged_unverified` until its bench
session fills the D6 matrix below and a separate JSON-catalog PR makes
the `cataloged_unverified -> verified` flip.

Two of the four open reconciliation questions above are no longer the
blockers they were when this reference first landed: question #1 (the
SX1509-vs-direct-GPIO disagreement) was resolved to the **native
ESP32-S3 GPIO** path by `SX1509-RECONCILE-001`
([`s360-100-native-fan-gpio-map.md`](s360-100-native-fan-gpio-map.md)),
and question #4 (single- vs four-channel) was decided **four-channel**
by `PACKAGE-PWM-001` ([`fan_pwm_native.yaml`](../../packages/expansions/fan_pwm_native.yaml)).
The remaining hardware questions — `"NINE 4pin FANs"` label (#3), the
`J3` pins 11/12 UART routing (#2), the `J3` 1-to-13 silkscreen order,
and the `J6`↔`J3` harness — stay **OWED** to `HW-PINMAP-311` and are
carried into the D6 matrix, not resolved here.

Checklist against the four `design-complete` conditions
([`pre-hardware-prep-plan.md` §1.1](../pre-hardware-prep-plan.md#11-definition)):

| # | Condition | State | Evidence |
|---|---|---|---|
| 1 | Firmware driver finalised to the current design artifacts | met | [`packages/expansions/fan_pwm_native.yaml`](../../packages/expansions/fan_pwm_native.yaml) — the finalised **four-channel** native driver: four `output: platform: ledc` PWM-drive outputs (`TachPMW1..4` -> `IO10`/`IO11`/`IO12`/`IO39`) feeding four `fan: platform: speed` controllers, plus three native `sensor: platform: pulse_counter` tach inputs (`Pul_Cou1`/`Pul_Cou2`/`Pul_Cou4` -> `IO17`/`IO18`/`IO9`, internal diagnostic, no RPM claim). Re-bound off the deprecated SX1509 path by `SX1509-RECONCILE-001`; cardinality decided four-channel by `PACKAGE-PWM-001`. This slice also reconciled the stale single-channel `fan_pwm_pin: GPIO4` / `fan_tach_pin: GPIO5` placeholder in [`packages/hardware/sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml) — marked **legacy / superseded** against the four-channel native map, with the production GPIO4/5 radar-UART binding in the Core board package left untouched. |
| 2 | Firmware compiles end-to-end in a compile-only CI target | met | Full `esphome compile` of the native composition recorded **green** by `S360-311-NATIVE-FANPWM-COMPILE-001` (local run 2026-05-28, ESPHome 2026.4.5, board `esp32-s3-devkitc-1` / framework `espidf`, commit `643bbd3`, rc=0, real `firmware.bin`). Targets `ceiling-poe-fanpwm-native-compile-only` and `ceiling-poe-fanpwm-product-compile-only` in [`config/compile-only-targets.json`](../../config/compile-only-targets.json) carry `compile_validation_status: validated-full-compile`. The legacy SX1509 full-compile run `26414398902` does **not** transfer to the native composition (it stays the historical proof for the superseded SX1509 skeleton). ESPHome is not available in this slice's authoring environment, so no new compile is run or fabricated here. |
| 3 | Every binding traceable to a schematic-printed value (no invented GPIOs / addresses) | met (schematic-only values carried as such) | Every native GPIO (`IO10`/`IO11`/`IO12`/`IO39` drive; `IO17`/`IO18`/`IO46`/`IO9` tach; `IO16` shared) is **schematic-printed** on `S360-100-R4` per [`s360-100-native-fan-gpio-map.md`](s360-100-native-fan-gpio-map.md); none is bench-verified (carried as such). The fourth tach `Pul_Cou3` -> `IO46` is **owed-not-invented**: `IO46` collides with the Core `fan_status_led_pin` (`GP_Fan_Status_Led`), so it stays disabled rather than inventing a conflicting binding (D6 item T8). `TachIO` -> `IO16` stays reserved (its shared-net role is ambiguous on the sheet — D6 item T11). |
| 4 | Release-note template + artifact-naming + pre-written bench test matrix exist | met | D5 template + artifact-naming scheme and the D6 bench / evidence test matrix below. |

Owed to the bench (carried, **not** resolved by reaching
`design-complete`): the `J3` 1-to-13 silkscreen order, the `J6`↔`J3`
13-pin harness conductor mapping, the `"NINE 4pin FANs"` label, the
`J3` pins 11/12 UART routing, the fourth-tach `Pul_Cou3`/`IO46`
collision, PWM polarity (`PWM-6`), per-fan + aggregate current, the
thermal envelope, and per-fan RPM via native `pulse_counter` (`PWM-13`).
All are listed in the D6 matrix below and owned by `HW-PINMAP-311`; the
operator-facing form is the existing
[§S360-311-BENCH-EVIDENCE-REQUEST-001 checklist](s360-311-r4-pwm.md#s360-311-bench-evidence-request-001--fanpwm-bench-evidence-checklist--contract-2026-05-26)
in the HW-PINMAP-311 audit.

## D5 — Release-note template and artifact-naming (template only)

This is a **pre-written template only**: `PRE-HW-PREP-FW-311-001`
publishes no artifact, tags no release, authors no release notes for a
real build, and sets no `artifact_name` field in any `config/*.json`.
`WEBFLASH-PWM-001` / `RELEASE-PWM-001` / `WF-IMPORT-PWM-001` stay
blocked. The template follows the house convention in
[`docs/room-firmware-release-notes.md`](../room-firmware-release-notes.md).

Artifact-naming scheme (for the eventual build, once verified +
released — **not** produced here), mirroring the Release-One scheme
(`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`):

```
Sense360-Ceiling-POE-FanPWM-v<MAJOR.MINOR.PATCH>-<channel>.bin
```

config string `Ceiling-POE-FanPWM`, product
[`products/sense360-ceiling-poe-fanpwm.yaml`](../../products/sense360-ceiling-poe-fanpwm.yaml).

Release-note template:

```
### Ceiling-POE-FanPWM v<MAJOR.MINOR.PATCH> (<channel>)

Artifact: Sense360-Ceiling-POE-FanPWM-v<MAJOR.MINOR.PATCH>-<channel>.bin

Summary: four-channel 12 V PWM fan-speed control on the Sense360 Core
ceiling + PoE stack, via four native ESP32-S3 ledc PWM-drive outputs
(S360-311 FanPWM, fans on J1/J2/J4/J5). 5 V in -> 12 V boost (MT3608);
SELV, no mains path.

Entity surface: four package-layer fan-speed controllers
(${friendly_name} Fan 1..4) plus the standard device-identity / health
diagnostic entities. Per-fan tach inputs are INTERNAL diagnostic
pulse-rate only — no RPM entity is surfaced and no RPM is claimed.

Compatibility: fan-driver variants (FanRelay/FanPWM/FanDAC/FanTRIAC)
are firmware-distinct and max-one-of. Ships FanPWM only.

Owed / pending before stable: the D6 bench / evidence test matrix must
be filled and S360-311 flipped cataloged_unverified -> verified; the
J3 silkscreen order, J6<->J3 harness, "NINE 4pin FANs" label, J3 11/12
UART routing, Pul_Cou3/IO46 fourth-tach collision, PWM polarity,
per-fan + aggregate current, thermal envelope, and per-fan RPM remain
owed (see D6). No release artifact is published until then.
```

## D6 — Bench / evidence test matrix (pre-written; to be filled at the bench)

This is the pre-written checklist the hardware session fills to move
`S360-311` from `design-complete` to `verified`. It covers the
verify-pending D1 items (silkscreen `J3` 1-to-13 order, `J6`↔`J3`
harness, `"NINE 4pin FANs"` label, `J3` 11/12 UART routing) plus the
native PWM drive, per-fan + aggregate current, thermal envelope, and
per-fan RPM via native `pulse_counter`. The `Measured` / `Pass?`
columns are **empty by design** — they are filled at the bench, not
here. This is the structured-matrix companion to the operator-facing
[§S360-311-BENCH-EVIDENCE-REQUEST-001 checklist](s360-311-r4-pwm.md#s360-311-bench-evidence-request-001--fanpwm-bench-evidence-checklist--contract-2026-05-26)
in the HW-PINMAP-311 audit (same owed set, expressed as a fill-in
matrix). It is the slice the queued `S360-311-CURRENT-THERMAL` bench
session fills; `PWM-6` (PWM polarity) and `PWM-13` (per-fan RPM) stay
**owed**.

| # | Test | Method | Expected (from design) | Measured | Pass? | Owed item |
|---|---|---|---|---|---|---|
| T1 | `J3` 1-to-13 silkscreen pin order | Silkscreen photo + DMM continuity on the assembled module | Pin order matches the schematic `J3` capture (`+5V`/`TachIO`/`TachPMW1`/`Pul_Cou1`/…/`UART_RX`/`UART_TX`/`GND`) | | | J3 silkscreen order |
| T2 | `J6`↔`J3` 13-pin harness conductor mapping | Conductor-by-conductor continuity on the physical Core `J6` ↔ module `J3` cable | Each Core `J6` net lands on the matching module `J3` pin | | | J6↔J3 harness |
| T3 | Native PWM drive on `IO10`/`IO11`/`IO12`/`IO39` (per fan) | Scope each `TachPMW*` gate node while commanding each `fan_pwm_native_1..4` 0–100 % | Each channel drives its fan; PWM polarity (active-high vs active-low low-side gate) confirmed against the fan | | | PWM polarity (PWM-6) |
| T4 | Per-fan fan current | DMM / current probe per fan output under load across the speed range | Per-fan current budget characterised within MOSFET / connector rating | | | per-fan current |
| T5 | Aggregate fan current + MT3608 boost ceiling | Sum all four channels at full load; measure the 12 V boost rail | Aggregate load within the MT3608 output-current ceiling; rail holds 12 V | | | aggregate current |
| T6 | Thermal envelope | Thermal camera / probe on `Q1..Q4`, MT3608, `L1`/`D1` at sustained full load | Steady-state temperatures within part ratings; locked-rotor / inrush envelope characterised | | | thermal envelope |
| T7 | Per-fan RPM via native `pulse_counter` (`Pul_Cou1`/`Pul_Cou2`/`Pul_Cou4`) | Compare each native pulse_counter rate against a reference tach / scope on `IO17`/`IO18`/`IO9` | Pulses-per-revolution established; per-fan RPM validated before any RPM entity is surfaced | | | per-fan RPM (PWM-13) |
| T8 | Fourth tach `Pul_Cou3` -> `IO46` vs Core `fan_status_led_pin` | Silkscreen + bench: resolve whether `IO46` carries `Pul_Cou3`, the fan-status LED, or both | A non-colliding binding for the fourth tach channel (or a confirmed shared use) | | | Pul_Cou3/IO46 collision |
| T9 | `"NINE 4pin FANs"` label vs four connectors | Design-provenance note / KiCad title block / board image | Four populated fan connectors (`J1`/`J2`/`J4`/`J5`) confirmed; the `"NINE"` label explained | | | NINE-fans label |
| T10 | `J3` pins 11/12 UART routing | Silkscreen read of Core `J6` 11/12 + harness trace + ESP32 UART identification | Confirm whether the Nextion `UART_RX`/`UART_TX` pair arrives over the 13-pin Core cable or a separate harness | | | J3 11/12 UART routing |
| T11 | Shared `TachIO` (`IO16`) role | Scope `TachIO` net (MOSFET drains) under per-fan drive | The shared-passthrough role of `TachIO` characterised; binding decision recorded | | | TachIO/IO16 role |

Filling this matrix is owed to the hardware session; this slice
resolves none of it. The `S360-311` board stays
`schematic_status: cataloged_unverified`.

## See also

- [`docs/hardware/s360-311-r4-pwm.md`](s360-311-r4-pwm.md) — HW-PINMAP-311
  full pin / package reconciliation audit (the authoritative running
  record this reference complements), including the HW-PINMAP-311-FOLLOWUP
  audit log and the operator bench records.
- [`docs/hardware/artifacts/S360-311-R4.md`](artifacts/S360-311-R4.md) —
  HW-ASSETS-003 curated artifact index; the schematic-side source of
  truth.
- [`docs/hardware/schematics/S360-311-R4.pdf`](schematics/S360-311-R4.pdf)
  — committed module-side schematic PDF (HW-ASSETS-003); the sole pin-map
  source for this reference.
- [`docs/hardware/s360-100-r4-core.md`](s360-100-r4-core.md) — Core
  schematic-backed reference; §J6 12 V PWM fan connector (13-pin);
  §Fan / driver outputs; §Open Questions #9 (`J6` 1-to-13 verify);
  §S360-100-BENCH-001 status.
- [`docs/hardware/s360-312-r4-fandac.md`](s360-312-r4-fandac.md) — the
  FanDAC sibling standalone reference (HW-PINMAP-312-FOLLOWUP); the pattern
  this doc follows.
- [`docs/release-one-hardware-audit.md`](../release-one-hardware-audit.md)
  — Required follow-ups #2 / #3, the owner (`CORE-ABSTRACT-BUS-001`) of the
  systemic Core abstract-bus rebind this reference defers question #1 to.
- [`docs/hardware/board-readiness-matrix.md`](board-readiness-matrix.md)
  — per-board readiness; the `S360-311` row (classification unchanged by
  this PR).
- [Hardware Artifact Policy (HW-ASSETS-001)](hardware-artifact-policy.md)
  — the retained-but-not-committed policy this reference respects.
- [`docs/cleanup-audit.md`](../cleanup-audit.md) — CLEANUP-001
  classification; carries the HW-PINMAP-311 / HW-PINMAP-311-FOLLOWUP
  registration rows and the explicit do-not list this PR honours.

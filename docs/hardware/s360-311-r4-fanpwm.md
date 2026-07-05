# S360-311-R4 FanPWM — Standalone Hardware Reference (HW-PINMAP-311-FOLLOWUP)

## Status

**Status: partial — schematic evidence available; package reconciliation pending. This reference resolves none of the open reconciliation questions, closes no gate, and does not unblock the S360-311 board package.**

> **S360-100-NATIVE-FAN-GPIO-MAP-001 — Core-side fan path is native ESP32-S3 GPIO (2026-05-28).**
> The canonical Core-side fan GPIO map is recorded in
> [`docs/hardware/s360-100-native-fan-gpio-map.md`](s360-100-native-fan-gpio-map.md):
> on the refreshed `S360-100-R4` schematic, `TachPMW1..4` (FanPWM
> control) and `Pul_Cou1..4` + `TachIO` (tach / pulse counter)
> terminate directly at native ESP32-S3 GPIO; the SX1509 (`U3`) I/O
> expander is removed from the S360-100 fan signal path. The
> Core-side SX1509-routed fan-path text below — including the package-
> vs-schematic disagreement recorded in the
> *Existing package abstraction* and *Reconciliation findings*
> sections of the merged audit's historical trail (departed under
> DOCS-DISPOSITION-001; recoverable via
> [`docs/archive-index.md`](../archive-index.md)) — is
> retained as historical / superseded context for that prior R4
> snapshot. The current FanPWM YAML
> ([`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml)
> and [`packages/expansions/fan_pwm_sx1509.yaml`](../../packages/expansions/fan_pwm_sx1509.yaml))
> remains wired against the legacy SX1509 routing and is now
> classified **legacy / superseded** by S360-100-NATIVE-FAN-GPIO-MAP-001.
> No firmware re-bind, no `esphome compile` against the native map,
> and no bench evidence is performed here.
> `Ceiling-POE-FanPWM` stays `status: hardware-pending`,
> `webflash_build_matrix: false`, no `artifact_name`,
> `rpm_supported: false`.

> **S360-311-NATIVE-FANPWM-YAML-001 — native ESP32-S3 GPIO FanPWM YAML
> candidate (2026-05-28).** A native-GPIO FanPWM candidate now exists
> alongside the legacy / superseded SX1509 path. The native package
> [`packages/expansions/fan_pwm_native.yaml`](../../packages/expansions/fan_pwm_native.yaml)
> binds the FanPWM control nets directly to native ESP32-S3 GPIO
> (`TachPMW1` → `IO10`, `TachPMW2` → `IO11`, `TachPMW3` → `IO12`,
> `TachPMW4` → `IO39`) using four `output: platform: ledc` outputs, and
> binds the per-fan tach / pulse-counter nets to native ESP32-S3 GPIO
> (`Pul_Cou1` → `IO17`, `Pul_Cou2` → `IO18`, `Pul_Cou4` → `IO9`) using
> three internal-diagnostic `sensor: platform: pulse_counter` inputs. It
> uses **no SX1509** for PWM output and **no SX1509** for any tach /
> `pulse_counter` input, per the canonical map in
> [`s360-100-native-fan-gpio-map.md`](s360-100-native-fan-gpio-map.md)
> (S360-100-NATIVE-FAN-GPIO-MAP-001). Two lines are intentionally left
> unbound rather than invented: `Pul_Cou3` (`IO46`) is **disabled / TBD**
> because `IO46` collides with the Core `fan_status_led_pin` (`GPIO46`)
> bound by
> [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml),
> and the shared `TachIO` net (`IO16`) stays **reserved / pending**
> (its shared-passthrough role is ambiguous per the per-fan-output drive
> topology section below). The candidate is exercised by the compile-only
> skeleton
> [`products/compile-only/ceiling-poe-fanpwm-native.yaml`](../../products/compile-only/ceiling-poe-fanpwm-native.yaml)
> (target `ceiling-poe-fanpwm-native-compile-only`). **Compile status is
> recorded honestly: `compile_validation_status: validated-full-compile`** —
> a full `esphome compile` run against the native composition PASSED
> (S360-311-NATIVE-FANPWM-COMPILE-001, LOCAL run 2026-05-28, ESPHome 2026.4.5,
> board `esp32-s3-devkitc-1` / framework espidf / ESP-IDF v5.5.4, commit
> `643bbd3`; rc=0, `INFO Successfully compiled program.`, RAM 13.2% / Flash
> 51.7% / 948679 bytes, real `firmware.bin`). This was a LOCAL run; no GitHub
> Actions run id exists and none is fabricated. The legacy SX1509 full-compile
> run `26414398902` does **not** transfer to the native composition — this is
> the native composition's own compile proof. A green compile is compile
> coverage only: it is **not** a release artifact, **not** WebFlash exposure,
> and **not** RPM / tach bench validation. RPM / tach support stays
> **unvalidated** (`rpm_supported: false`) until measured bench evidence
> exists. The native candidate adds **no** WebFlash wrapper, **no**
> `config/webflash-builds.json` row, **no** `artifact_name`, and **no**
> `webflash_build_matrix` flip; `Ceiling-POE-FanPWM` stays excluded from
> release / WebFlash and `S360-311` `schematic_status` stays
> `cataloged_unverified`. The legacy SX1509 YAMLs and the historical
> SX1509 / `pulse_counter` proof remain in place as superseded /
> manual-only context. Pinned by
> [`tests/test_native_fanpwm_yaml.py`](../../tests/test_native_fanpwm_yaml.py).

This document is the per-board hardware reference for the Sense360 PWM
12 V fan-driver board, revision R4 (`S360-311-R4`), produced under
`HW-PINMAP-311-FOLLOWUP`. It follows the per-board reference pattern of
[`s360-200-r4-roomiq.md`](s360-200-r4-roomiq.md),
[`s360-211-r4-ventiq.md`](s360-211-r4-ventiq.md),
[`s360-300-r4-led.md`](s360-300-r4-led.md), and its FanDAC sibling
[`s360-312-r4-fandac.md`](s360-312-r4-fandac.md), and it subsumes the
broader HW-PINMAP-311 reconciliation audit (the former standalone
`docs/hardware/s360-311-r4-pwm.md`, merged into this document under
DOCS-DISPOSITION-001 Step 4; the original audit record is indexed by
SHA in [`docs/archive-index.md`](../archive-index.md)).

This reference transcribes the connector and pin map **exactly as the
committed module-side schematic shows** and records every open
reconciliation question as **STILL OWED**. It is **documentation only**.
It resolves nothing: per
[`docs/cleanup-audit.md` (archived)](../archive-index.md) the reconciliation itself
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
[`docs/hardware/s360-100-r4-core.md`](s360-100-r4-core.md). This
document is also the authoritative HW-PINMAP-311 pin-map
reconciliation record and carries the operator bench records (the
former standalone audit `docs/hardware/s360-311-r4-pwm.md` was merged
into it; original indexed in
[`docs/archive-index.md`](../archive-index.md)).

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
| Per-board reconciliation audit | This document (HW-PINMAP-311; the former standalone `s360-311-r4-pwm.md` was merged here — original indexed in [`docs/archive-index.md`](../archive-index.md)) |
| FanPWM package YAML (canonical) | [`packages/expansions/fan_pwm_native.yaml`](../../packages/expansions/fan_pwm_native.yaml) (four-channel native ESP32-S3 GPIO; cardinality decided by `PACKAGE-PWM-001`, rebound off SX1509 by `SX1509-RECONCILE-001`) |
| FanPWM package YAML (legacy / superseded) | [`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml) and [`packages/expansions/fan_pwm_sx1509.yaml`](../../packages/expansions/fan_pwm_sx1509.yaml) — SX1509-routed path, classified legacy / superseded by `S360-100-NATIVE-FAN-GPIO-MAP-001` |

## Evidence table

| Evidence | Source | Status |
|---|---|---|
| Module-side schematic PDF | [`docs/hardware/schematics/S360-311-R4.pdf`](schematics/S360-311-R4.pdf) (HW-ASSETS-003; SHA256 `c910b3364be1d58fc44d12b5a189dade47efddf6cae158a86577ec7501e48006`; 91,543 bytes) | **Committed.** Byte-identical to upload. Single sheet (`S360-311-R4.kicad_sch`, Id 1/1), KiCad 10.0.3 export, A4. The only pin-map source for this reference. |
| Curated artifact index | [`docs/hardware/artifacts/S360-311-R4.md`](artifacts/S360-311-R4.md) | **Committed.** Schematic-content capture + retained-but-not-committed inventory. Not edited by this PR. |
| HW-PINMAP-311 audit | This document (the former standalone `s360-311-r4-pwm.md` was merged here; original indexed in [`docs/archive-index.md`](../archive-index.md)) | **Merged.** The full reconciliation audit record now lives in this reference doc. |
| Core-side `J6` capture | [`s360-100-r4-core.md` §J6](s360-100-r4-core.md#j6--12-v-pwm-fan-connector-13-pin) | **Committed.** Net list `+5V`, `GND`, `TachIO`, `TachPMW1..4`, `Pul_Cou1..4` (11 nets); 1-to-13 pin order explicitly flagged **verify** against silkscreen. Does **not** list any UART pins. |
| Module-side BOM spreadsheet | Drive `12vFan_PWM_PulseCounter.xlsx` (retained-but-not-committed) | **Part-identity layer closed.** BOM content transcribed in [§BOM part-identity cross-check](#bom-part-identity-cross-check-drive-12vfan_pwm_pulsecounterxlsx) below (PWM-BLOCKER-REMOVAL-001); the `.xlsx` itself stays retained-but-not-committed. Matching the BOM rows against a populated board stays owed to the bench. |
| Silkscreen / harness inspection | _(not provided)_ | **Pending.** Required for the Core `J6` ↔ module `J3` 1-to-13 pin order and the 13-pin harness conductor mapping. |
| Bench / scope / waveform capture | _(not provided here)_ | **Pending.** Required for per-fan PWM drive (`TachPMW*`), per-fan tach feedback (`Pul_Cou*`), the shared open-drain `TachIO`, PWM polarity, and pulses-per-revolution. (Operator functional-bench attestations are recorded below in this document — [§S360-311-BENCH-RESULT-001](#s360-311-bench-result-001--fanpwm-operator-bench-result-2026-05-26), [§S360-311-NATIVE-FANPWM-BENCH-001](#s360-311-native-fanpwm-bench-001--native-fanpwm-operator-bench-result-2026-05-29), [§S360-311-CURRENT-THERMAL-001](#s360-311-current-thermal-001--measured-current--thermal-bench-run-2026-05-29--2026-05-31-no-values-recorded); they are not re-litigated or upgraded here.) |
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
[`hardware-artifact-policy.md` (archived)](../archive-index.md).

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
of them. The authoritative running record is carried in this document
(the former standalone audit was merged here; its dated evidence-pass
audit log departed with the archived original — see
[`docs/archive-index.md`](../archive-index.md)); the items below restate the
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
  [`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3 (archived)](../archive-index.md).
  **Not** this reference, and **not** HW-PINMAP-311-FOLLOWUP.
- **Evidence that would close it.** Operator-attested silkscreen reading of
  the Core-side fan-signal origins, a documented Core abstract-bus rebind
  (or retirement decision) under `CORE-ABSTRACT-BUS-001`, and bench /
  scope confirmation that each `TachPMW*` / `Pul_Cou*` net is driven from
  the asserted GPIO / SX1509 channel. The canonical Core-side fan GPIO map
  candidate is tracked separately at
  [`s360-100-native-fan-gpio-map.md`](s360-100-native-fan-gpio-map.md);
  this reference does not assert it as resolved.

> **Resolution note (recorded later):** question #1 was resolved to the
> **native ESP32-S3 GPIO** path by `SX1509-RECONCILE-001` /
> `S360-100-NATIVE-FAN-GPIO-MAP-001` — see
> [§Design-complete status](#design-complete-status-pre-hw-prep-fw-311-001).
> The direct-GPIO `expansion_gpio*` bindings cited above were retired by
> `CORE-ABSTRACT-BUS-001C`; the text above is retained as the historical
> statement of the disagreement.

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

> **Resolution note (recorded later):** question #4 was decided
> **four-channel** by `PACKAGE-PWM-001`
> ([`fan_pwm_native.yaml`](../../packages/expansions/fan_pwm_native.yaml));
> see [§Design-complete status](#design-complete-status-pre-hw-prep-fw-311-001).

## What this reference does not assert

- It does **not** claim any silkscreen, harness, scope, multimeter, or
  manufacturing-artifact (KiCad source / PCB / BOM / CPL / Gerber / drill /
  STEP / board image) review has been performed for `S360-311-R4`. None of
  those artifacts are committed.
- It does **not** promote any row of the merged HW-PINMAP-311 audit
  record away from its current value,
  close any of its known unresolved issues, or close the
  [`s360-100-r4-core.md` Open Questions #9](s360-100-r4-core.md#open-questions--verification-needed)
  `J6` 1-to-13 verify flag (owned by `S360-100-BENCH-001`).
- It does **not** advance `WEBFLASH-PWM-001`, `RELEASE-PWM-001`,
  `WF-IMPORT-PWM-001`, or `CORE-ABSTRACT-BUS-001`. (`PACKAGE-PWM-001`
  and `PRODUCT-PWM-001` have since landed — see
  [§Design-complete status](#design-complete-status-pre-hw-prep-fw-311-001) —
  without changing this reference's own non-claims.)
- The board package and the `S360-311` `schematic_status` promotion stay
  **gated** on the owed silkscreen / harness / bench evidence and the
  systemic Core abstract-bus resolution.

## Design-complete status (PRE-HW-PREP-FW-311-001)

`S360-311` is **design-complete** as of `PRE-HW-PREP-FW-311-001`
(2026-05-31), slice 3 of
[`docs/pre-hardware-prep-plan.md` (archived)](../archive-index.md).

**`design-complete` is a prose / documentation annotation only.** It is
deliberately **not** `verified`: it does **not** flip `schematic_status`
(which stays `cataloged_unverified`), does **not** change `S360-311`'s
lifecycle (`hardware-pending`), does **not** set `schematic_file`, and
does **not** enable any WebFlash exposure or release surface (per
[`pre-hardware-prep-plan.md` §1.2 / §1.4 (archived)](../archive-index.md)).
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
([`pre-hardware-prep-plan.md` §1.1 (archived)](../archive-index.md)):

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
[§S360-311-BENCH-EVIDENCE-REQUEST-001 checklist](#s360-311-bench-evidence-request-001--fanpwm-bench-evidence-checklist--contract-2026-05-26)
below (carried from the merged HW-PINMAP-311 audit).

## D5 — Release-note template and artifact-naming (template only)

This is a **pre-written template only**: `PRE-HW-PREP-FW-311-001`
publishes no artifact, tags no release, authors no release notes for a
real build, and sets no `artifact_name` field in any `config/*.json`.
`WEBFLASH-PWM-001` / `RELEASE-PWM-001` / `WF-IMPORT-PWM-001` stay
blocked. The template follows the house convention in
[`docs/room-firmware-release-notes.md` (archived)](../archive-index.md).

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
[§S360-311-BENCH-EVIDENCE-REQUEST-001 checklist](#s360-311-bench-evidence-request-001--fanpwm-bench-evidence-checklist--contract-2026-05-26)
below (same owed set, expressed as a fill-in
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

### D6 bench-session result so far (`S360-311-CURRENT-THERMAL-001`)

The queued `S360-311-CURRENT-THERMAL` bench session has been **run twice**
(2026-05-29 and re-run 2026-05-31) by the operator (`@wifispray`). Both
passes **re-confirmed the functional PWM rows** (operator-notes-only:
channels `J1`/`J2`/`J4`/`J5` individually + all-four-simultaneous +
low/medium/high + restart-retention all PASS) but **captured no measured
current, thermal, or tach/RPM values**. Against the matrix above, that
leaves:

- **T3 (native PWM drive)** — functional drive **PASS** (operator-notes);
  PWM polarity via scope (`PWM-6`) **still owed** (not scoped).
- **T4 (per-fan current)** — **NOT measured; owed.**
- **T5 (aggregate current + MT3608 ceiling)** — **NOT measured; owed.**
- **T6 (thermal envelope)** — **NOT measured; owed.**
- **T7 (per-fan RPM via `pulse_counter`)** — **explicitly NOT measured;
  owed.** `rpm_supported` stays **false**.
- **T8 (`Pul_Cou3`/`IO46`)** — **unresolved; owed.** Stays disabled / TBD.
- **T1 / T2 / T9 / T10 / T11** (`J3` silkscreen order, `J6`↔`J3` harness,
  `"NINE 4pin FANs"` label, `J3` 11/12 UART routing, `TachIO`/`IO16`
  role) — **remain OWED;** none was proven on either run.

Per the project no-fabrication rule, no current / thermal / RPM value is
inferred or back-filled. The full dated record (including the 2026-05-31
re-run) is in
[§S360-311-CURRENT-THERMAL-001](#s360-311-current-thermal-001--measured-current--thermal-bench-run-2026-05-29--2026-05-31-no-values-recorded)
below.
The `Measured` / `Pass?` columns above stay empty by design until the
measured rows are actually captured.

## S360-100-TACH-GPIO-ALLOCATION-001 — Core-side native ESP32 GPIO allocation (2026-05-28)

This subsection mirrors, on the FanPWM module-audit side, the **final
native ESP32 GPIO allocation** for the per-fan tach / pulse-counter
inputs `Pul_Cou1..4` (and the shared `TachIO` passthrough and the
`TachPMW1..4` PWM-drive outputs) that the
[`docs/hardware/s360-100-r4-core.md` § S360-100-TACH-GPIO-ALLOCATION-001](s360-100-r4-core.md#s360-100-tach-gpio-allocation-001--native-esp32-gpio-allocation-for-fanpwm-tach-inputs)
section and the
[`docs/hardware/s360-100-core-architecture.md` § Pin allocation table](s360-100-core-architecture.md#pin-allocation-table--native-esp32-s3-gpio-termination)
record from the canonical
[`schematics/S360-100-R4.pdf`](schematics/S360-100-R4.pdf) sheet
(SHA256 `4c9e8b06d129fbb55f61e143b648e03762d06cb4dc67fe3120c268cd3a4bdf16`).
It is **documentation only** and reuses the same allocation evidence;
this section does **not** flip any `S360-311` status, **not** edit
[`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml),
**not** add `pulse_counter` bindings, and **not** claim measured RPM.

| Module-side `J3` pin | Net on the 13-pin Core ↔ module harness | Core-side `S360-100-R4` native ESP32-S3 GPIO | ESP32-S3 module pin | Notes |
|---:|---|---|---:|---|
| 1 | `+5V` | n/a | n/a | Power. |
| 2 | `TachIO` (shared 12 V PWM fan tach passthrough) | `IO16` | 9 | Native ESP32-S3 GPIO, interrupt-capable; today bound only as substitution `tach_io_pin: GPIO16`; no `pulse_counter` consumer. |
| 3 | `TachPMW1` (per-fan PWM-drive output, channel 1) | `IO10` | 18 | Native ESP32-S3 GPIO (PWM-capable); not bound as a native `ledc:` output today (`fan_pwm.yaml` still composes `fan_pwm_sx1509.yaml`'s SX1509 PWM-drive). |
| 4 | `Pul_Cou1` (per-fan tach, channel 1) | `IO17` | 10 | Native ESP32-S3 GPIO, interrupt-capable; **not** bound as `pulse_counter` in any package / product. |
| 5 | `TachPMW2` (per-fan PWM-drive output, channel 2) | `IO11` | 19 | Native ESP32-S3 GPIO (PWM-capable); not bound as a native `ledc:` output today. |
| 6 | `Pul_Cou2` (per-fan tach, channel 2) | `IO18` | 11 | Native ESP32-S3 GPIO, interrupt-capable; **not** bound as `pulse_counter`. |
| 7 | `TachPMW3` (per-fan PWM-drive output, channel 3) | `IO12` | 20 | Native ESP32-S3 GPIO (PWM-capable); not bound as a native `ledc:` output today. |
| 8 | `Pul_Cou3` (per-fan tach, channel 3) | `IO46` | 16 | Native ESP32-S3 GPIO, interrupt-capable; **not** bound as `pulse_counter`. |
| 9 | `TachPMW4` (per-fan PWM-drive output, channel 4) | `IO39` | 32 | Native ESP32-S3 GPIO (PWM-capable); not bound as a native `ledc:` output today. |
| 10 | `Pul_Cou4` (per-fan tach, channel 4) | `IO9` | 17 | Native ESP32-S3 GPIO, interrupt-capable; **not** bound as `pulse_counter`. |
| 11 | `UART_RX` | (open question — see [§Open reconciliation questions (still owed)](#open-reconciliation-questions-still-owed) #2) | — | Module-side schematic labels pin 11 `UART_RX`; Core-side `J6` capture does not currently list a UART pair on these pins. Unchanged by this section. |
| 12 | `UART_TX` | (open question — see [§Open reconciliation questions (still owed)](#open-reconciliation-questions-still-owed) #2) | — | As above for pin 12. |
| 13 | `GND` | n/a | n/a | Ground. |

### Verification scope (S360-100-TACH-GPIO-ALLOCATION-001 on the FanPWM side)

- **Schematic side — proven.** The Core-side native GPIO termination
  for each `TachIO` / `Pul_Cou1..4` / `TachPMW1..4` net is printed on
  the canonical
  [`schematics/S360-100-R4.pdf`](schematics/S360-100-R4.pdf) sheet
  (the new R4 export delivered under `S360-100-NATIVE-TACH-PULSE-001`
  R4 refresh). None of the native GPIOs above
  (`IO9` / `IO10` / `IO11` / `IO12` / `IO16` / `IO17` / `IO18` /
  `IO39` / `IO46`) is on the ESP32-S3 PSRAM / SPI-reserved set
  (`IO35` / `IO36` / `IO37`); the strapping / boot-conflict check for
  `IO46` and the connector-1-to-13 silkscreen verification stay open
  in the existing [§Open reconciliation questions (still owed)](#open-reconciliation-questions-still-owed)
  + [`s360-100-r4-core.md` Open Questions #9](s360-100-r4-core.md#open-questions--verification-needed)
  and are owed to bench evidence (S360-100-BENCH-001 +
  HW-PINMAP-311-FOLLOWUP).
- **Module side — schematic-confirmed but bench-unverified.** The
  module-side `J3` 1-to-13 pin order in the table above is taken from
  the committed `S360-311-R4` schematic
  ([§Schematic summary](#schematic-summary), Module-side `J3` table).
  Silkscreen reading and harness inspection still owe to bench
  evidence per the [§D6 — Bench / evidence test matrix](#d6--bench--evidence-test-matrix-pre-written-to-be-filled-at-the-bench).
- **Firmware side — not changed.** This section does not edit
  [`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml)
  / [`packages/expansions/fan_pwm_sx1509.yaml`](../../packages/expansions/fan_pwm_sx1509.yaml),
  does not bind `Pul_Cou1..4` as `sensor: platform: pulse_counter`,
  and does not move PWM-drive output off the SX1509 path. Any future
  rebind belongs to the **PACKAGE-GAP-001 FanPWM slice** /
  **HW-PINMAP-311-FOLLOWUP** PRs (the native rebind has since landed —
  see [§Design-complete status](#design-complete-status-pre-hw-prep-fw-311-001)).
- **RPM / bench-measured side — not claimed.** `rpm_supported: false`
  stays the posture on every FanPWM product;
  [`config/webflash-builds.json`](../../config/webflash-builds.json)
  carries no FanPWM-bearing entry; `S360-311` stays
  `cataloged_unverified`. Bench-measured RPM remains owned by
  `S360-311-CURRENT-THERMAL-001` / `COMPONENT-NATIVE-TACH-001`
  (future).

> **Superseded note (merge, 2026-07-05):** the "Firmware side — not
> changed" posture above is the historical statement from the original
> audit pass. The native four-channel rebind has since landed
> (`SX1509-RECONCILE-001` / `PACKAGE-PWM-001`,
> [`packages/expansions/fan_pwm_native.yaml`](../../packages/expansions/fan_pwm_native.yaml));
> the SX1509 packages are legacy / superseded per
> `S360-100-NATIVE-FAN-GPIO-MAP-001`. See
> [§Design-complete status](#design-complete-status-pre-hw-prep-fw-311-001).

## PWM-BLOCKER-REMOVAL-001 evidence record (2026-05-25)

Carried verbatim from the merged HW-PINMAP-311 audit: the
Drive-evidence provenance, the BOM part-identity cross-check, the
project-tracker corroboration, and the operator design decisions
D1–D3.

### Newly inspected Drive evidence (provenance recorded, not committed)

A Drive folder named **`12vFan_PWM_PulseCounter`** — the exact
`old_name` carried for `S360-311` in
[`config/hardware-catalog.json`](../../config/hardware-catalog.json) —
was inspected this pass (from the project hardware owner). It holds a
complete manufacturing artifact set that
the [HW-ASSETS-003 artifact index](artifacts/S360-311-R4.md#files-not-provided-in-this-upload)
previously recorded as `not provided in this upload`:

| Drive artifact | Format / size | Use in this audit |
|---|---|---|
| `bom/12vFan_PWM_PulseCounter.xlsx` | XLSX, 11,112 B | **BOM part-identity cross-check** (below). |
| `sch_pdf/12vFan_PWM_PulseCounter.pdf` | PDF, 357,151 B | Corroborating schematic export. Title block reads `12vFan_PWM_PulseCounter.kicad_sch`, **KiCad 9.0.2**, blank Rev — the *older project-name* export. The repo-committed [`schematics/S360-311-R4.pdf`](schematics/S360-311-R4.pdf) is the renamed `S360-311-R4.kicad_sch` **KiCad 10.0.3** export, also blank Rev. Net / connector / part content matches; neither PDF carries an explicit `R4` rev stamp. |
| `images/12vFan_PWM_PulseCounter*.png` | 3 × PNG | Board render. Silkscreen reads **`SENSE 360 FAN`** with `J3`, `J5`, `J6`, `pwm1..4`, `pul1..4`, `rx`, `tx`, `Q1..Q4`, `R2/R6/R7`, `gnd`, `5v tx rx gnd`. Confirms board identity and the per-channel labels; does **not** by itself confirm the `J3` / `J6` 1-to-13 pin-1 numbering. |
| `gerbers/`, `cpl/`, `step_file/`, `Assets/` | Folders | Recorded as existing in Drive; not inspected pin-by-pin; not committed. |

**Provenance caveat.** The Drive set carries the board's pre-rename
project name (`12vFan_PWM_PulseCounter`) and a blank Rev field. Its
component list matches the committed `S360-311-R4` schematic 1:1 (see
BOM cross-check), so it cross-checks **at the part-identity layer**,
but it is **not** an explicitly `R4`-stamped artifact set. An operator
confirmation that this Drive folder is the same revision as the
committed `S360-311-R4` schematic is the one remaining identity
nicety; the part-identity match is not contradicted by any evidence.

### BOM part-identity cross-check (Drive `12vFan_PWM_PulseCounter.xlsx`)

Every component the BOM lists matches the
[§Schematic summary](#schematic-summary) of the committed
`S360-311-R4` schematic. No part is contradicted; no part is missing.

| Ref(s) | Value | MFR # | Manufacturer | Schematic role |
|---|---|---|---|---|
| `U1` | MT3608 | MT3608 | XI'AN Aerosemi | `+5V → +12V` boost converter (SOT-23-6). |
| `L1` | 22 µH | SRN6045TA-220M | BOURNS | Boost inductor. |
| `D1` | SS34 | SS34 | GOODWORK | Boost Schottky rectifier (SMA). |
| `R3` / `R5` | 38k / 2k | FRC0402F3832TS / FRC0402F2001TS | FOJAN | Boost feedback divider (sets ≈12 V). |
| `R4` | 330R | FRC0402F3300TS | FOJAN | `D2` indicator-LED series resistor. |
| `D2` | Blue | TZ-P2-0402YGTIA1-0.45T | TUOZHAN | Power / boost indicator LED. |
| `C1` / `C2` | 22 µF / 10V | GRM158R61A226ME15D | muRata | Boost input / output bulk caps. |
| `Q1`–`Q4` | Q_NMOS_GSD | **ME15N10-G** | MATSUKI | **Per-channel low-side N-FET** (TO-252), one per fan output. |
| `R1` / `R2` / `R6` / `R7` | 1k | FRC0402F1001TS | FOJAN | Gate series resistors for `Q1`–`Q4`. |
| `J1` / `J2` / `J4` / `J5` / `J6` | Conn_01x4 | SM04B-SRSS-TB(LF)(SN) | JST (SH, 1.0 mm) | Four 4-pin fan outputs + the 4-pin Nextion (`J6`). |
| `J3` | Conn_01x13 | SM13B-SRSS-TB(LF)(SN) | JST (SH, 1.0 mm) | 13-pin "From Core" harness connector. |

This closes the **BOM cross-check** precondition recorded for
`PACKAGE-PWM-001` in
[`package-readiness-matrix.md` (archived)](../archive-index.md)
**at the part-identity layer** — the same standard `HW-BOM-ASSETS-002`
applied to `S360-400` / `S360-410`. It does **not** add the `.xlsx` to
git, and does **not** by itself promote `schematic_status`.

### Project-tracker corroboration (Drive `Sense360_R4_Tracker`, evidence-pass 2)

A second Drive artifact was inspected this pass that the prior pass did
**not** cite: the project tracker spreadsheet **`Sense360_R4_Tracker`**
(Google Sheet, from the hardware design source, in the R4 shared
drive). It is a task / status tracker, not
a manufacturing artifact, so it is recorded here for **provenance and
status corroboration only**; nothing is committed from it.

| Tracker reference | Status (per tracker) | Bearing on this audit |
|---|---|---|
| Boards tab — `S360-311` row | — | Restates the board identity **1:1** with [`config/hardware-catalog.json`](../../config/hardware-catalog.json): `Inline` / `Driver` / `Sense360 PWM` / `S360-311` / `R4` / old name `12vFan_PWM_PulseCounter` / `12V PWM fan driver, up to 4 fans with tach feedback.`. Independent confirmation of the catalog row. |
| Task `R07` — "Rename project to S360-311 R4 and upload to R4 drive" | **Done** | Confirms, at the project-management layer, that the `12vFan_PWM_PulseCounter` → `S360-311 R4` rename actually happened — the same rename the catalog `old_name` records. Corroborates that the Drive `12vFan_PWM_PulseCounter` set and the committed `S360-311-R4` schematic are the **same board lineage**. |
| Task `G01` — "Add the silkscreen markings on every R4 board: Sense360 logo, friendly name, P/N (SKU), REV, date code" | **Waiting** (High) — *"P/N, REV and date code are not currently on the boards. Waiting for the design owner to send the SVG logo (see N01)."* | **Explains the blank `Rev` field** in both schematic exports and the absence of a `R4` rev stamp in the board renders: the P/N / REV / date-code silkscreen is a **board-wide, not-yet-applied** task across the entire R4 fleet, blocked on task `N01` (design owner to supply the logo SVG), **not** a board-specific identity ambiguity for `S360-311`. |
| Task `N01` — "Send the Sense360 SVG logo to Stephen" | **To do** (High) | Upstream blocker for `G01`. Until it lands, **no** R4 board carries an on-silkscreen P/N / REV / date code. |
| Task `C02` — "Change the fan connector to XH2.54" (Core, `S360-100`) | **Done** (High) — *"All small fans we can find use XH2.54, not the current connector."* | Records that the **Core-side** fan connector was migrated to **XH2.54 (2.54 mm pitch)**, while the committed `S360-311` module BOM uses **JST-SH (1.0 mm pitch)** for both the fan outputs (`SM04B`) and the "From Core" `J3` (`SM13B`). Adds a concrete **connector-type / pitch reconciliation** item at the Core ↔ module harness — see below. |

**What this advances:**

- **Row 2 (schematic / BOM identity).** The single residual on row 2
  was the missing explicit `R4` rev stamp. The tracker now **explains
  it**: `R07` (Done) confirms the project-level rename to `S360-311 R4`,
  and `G01` (Waiting) + `N01` (To do) show the blank `REV` is a tracked,
  fleet-wide silkscreen task pending the design owner's SVG — not unresolved
  provenance. The rev-stamp item stays a **minor operator confirmation**
  (it will arrive via `G01`/`N01`), but it is no longer an unexplained
  gap. Row 2 stays **CLOSED (part-identity)**.

- **Row 3 (Core connector / bus / GPIO mapping).** The tracker adds a
  new, specific harness sub-item: **Core fan connector = XH2.54** (`C02`
  Done) vs **module connectors = JST-SH** (`J3` `SM13B`, fan outputs
  `SM04B`). Either the committed module schematic / BOM **predates** a
  matching module-side connector change, or the Core ↔ module harness
  **adapts** XH2.54 ↔ JST-SH. This is recorded as an open reconciliation
  point for `HW-PINMAP-311-FOLLOWUP`; it does **not** change row 3's
  **STILL BLOCKING** classification (it sharpens it).

- **Silkscreen-based pin-order verification.** `G01` (Waiting) confirms
  that **no R4 board currently carries a P/N / REV / date-code
  silkscreen**. The board renders in the Drive set show component
  reference designators (`J3` / `J5` / `J6`, `pwm1..4`, `pul1..4`,
  `Q1..Q4`) but cannot supply an operator-attributed `J3` / `J6`
  1-to-13 **pin-1 numbering** read; and the canonical board-identity
  silkscreen those renders would carry is itself pending `G01`/`N01`.
  This reinforces why the Core `J6` / module `J3` pin-order `verify`
  flags (row 3) stay open: the silkscreen evidence does not exist yet.

This subsection **does not** edit the catalog, any package / product /
config, or any binary; it records tracker provenance and refines the
basis of rows 2 and 3 only.

### Operator decisions (PWM-BLOCKER-REMOVAL-001, 2026-05-25)

The three design questions that evidence alone could not close were put
to the project operator during `PWM-BLOCKER-REMOVAL-001` and answered as
follows. These are recorded as **operator-attributed design decisions**
(provenance: operator response, 2026-05-25). They resolve the
*design-intent* questions; they do **not** supply bench / silkscreen /
waveform evidence and they do **not** authorize a package edit in this
PR — the operator explicitly directed that any SX1509 / Core
abstract-bus binding be recorded as the **next prerequisite**, not
fabricated here.

| # | Question | Operator decision |
|---|---|---|
| D1 | Single-channel vs four-channel canonical FanPWM abstraction | **Four-channel.** Canonical FanPWM exposes **4 independent fan PWM outputs + 4 tach inputs**, matching the board outputs `J1` / `J2` / `J4` / `J5` and the legacy `sense360_fan_pwm.yaml` shape. Product layers may use one channel, gang channels, or leave channels unused, but the **package abstraction represents all four hardware channels neutrally**. |
| D2 | SX1509-routed vs direct-ESP32 PWM / tach binding | **SX1509 expander.** Bind `TachPMW1..4` → **SX1509 channels 0..3** and `Pul_Cou1..4` → **SX1509 channels 4..7**; keep `TachIO` **direct on ESP32 `IO16`**. Do **not** preserve the older direct-ESP32 binding where it contradicts the schematic. If implementation needs a Core abstract-bus / SX1509 package follow-up, **record that as the next prerequisite** rather than fabricating direct-GPIO mappings. |
| D3 | Is the committed JST-SH schematic the current R4, given Core `C02` → XH2.54? | **Committed schematic is current R4.** JST-SH is correct for the module side (`SM04B` fan outputs, `SM13B` From-Core `J3`). The Core ↔ module harness **adapts XH2.54 ↔ JST-SH** where needed. No newer schematic / BOM is asserted; no new schematic is needed for this PR. |

**What this resolves (design-intent layer only):**

- **D1 + D2** define the reconciliation target for
  [`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml):
  a **four-channel** package bound to **SX1509 channels 0..3 (PWM) /
  4..7 (tach)** with `TachIO` direct on `IO16`. This removes the
  cardinality and routing-direction ambiguity that previously gated
  rows 4 and 7. It does **not** remove the implementation gate: the
  parent Core abstract packages bind direct ESP32 GPIOs and
  `expansion_gpio1..4` were retired by `CORE-ABSTRACT-BUS-001C`, so the
  SX1509 four-channel binding is owed to a **`CORE-ABSTRACT-BUS-001` /
  SX1509 package follow-up** that must land before (or with)
  `PACKAGE-PWM-001-IMPLEMENT-001`.
- **D3** resolves the connector-identity sub-item raised in
  [§Project-tracker corroboration](#project-tracker-corroboration-drive-sense360_r4_tracker-evidence-pass-2):
  the committed JST-SH module schematic is current; the XH2.54-vs-JST-SH
  difference is a **harness adaptation**, not a stale module schematic.
  The Core `J6` / module `J3` 1-to-13 **silkscreen pin order** remains
  `verify` (no R4 silkscreen exists yet per tracker `G01`).

**What this does NOT resolve (still owed to bench / follow-up):** PWM
polarity (active-high vs active-low for the low-side N-FET gate path);
tach pull-up source (discrete / SX1509 on-die / fan-side);
pulses-per-revolution validation of the `multiply: 0.5` factor; per-fan
and aggregate current + thermal envelope (MT3608 ceiling); the Core `J6`
/ module `J3` silkscreen 1-to-13 pin order; the UART-on-`J3`-pins-11/12
routing question; and the `CORE-ABSTRACT-BUS-001` / SX1509 four-channel
package binding itself.

## Tach / RPM strategy (PACKAGE-PWM-TACH-STRATEGY-001)

Carried verbatim from the merged HW-PINMAP-311 audit: the
compile-proven SX1509 / `pulse_counter` capability finding, the
operator scope decisions D-T1 / D-T2, and the open `GPIO16`
contention record.

### Finding being resolved (compile-proven — PWM-SX1509-TACH-PROOF-001)

`CORE-ABSTRACT-BUS-SX1509-001` first recorded this ESPHome capability
finding; **PWM-SX1509-TACH-PROOF-001 (2026-05-25) upgrades it from an
inferred claim to a compile/config proof** so the wording no longer
rests on "online docs" or on reasoning-from-`InternalGPIOPin` alone:

- **SX1509 PWM drive (channels 0..3, `TachPMW1..4`) IS supported** via
  the on-chip LED-driver PWM engine (`output: platform: sx1509`). This
  is **not** in question and stays the basis of FanPWM drive. SX1509
  GPIO / binary input (channels 4..7, polled `binary_sensor: platform:
  gpio`) is supported too.
- **An SX1509 expander pin used as an ESPHome `pulse_counter` input is
  compile-proven unsupported by ESPHome validation.** The minimal
  fixture
  [`tests/esphome/sx1509_pulse_counter_proof.yaml`](../../tests/esphome/sx1509_pulse_counter_proof.yaml)
  (SX1509 hub on `core_i2c`, channel 4 = `Pul_Cou1`, behind a
  `sensor: platform: pulse_counter`) is **rejected by `esphome config`**
  (ESPHome 2026.5.1, exit code 2) with the captured error:

  ```text
  Failed config

  sensor.pulse_counter: [source sx1509_pulse_counter_proof.yaml:…]
    pin:
      [sx1509] is an invalid option for [pin]. Please check the indentation.
  ```

  The `pulse_counter` pin schema accepts only an interrupt-capable
  native ESP32 `InternalGPIOPin`; the SX1509 expander pin schema is not
  a valid option for it.
- **Per-fan RPM via `Pul_Cou1..4` is therefore un-implementable** as a
  standard ESPHome `pulse_counter` RPM input — a compile-proven blocker
  for the originally-scoped four-PWM + four-per-fan-RPM
  `PACKAGE-PWM-001-IMPLEMENT-001`.

Two control checks in
[`tests/test_sx1509_tach_pulse_counter_proof.py`](../../tests/test_sx1509_tach_pulse_counter_proof.py)
confirm the rejection is specific to `pulse_counter` + SX1509, not a
generic config error: the **same** SX1509 pin validates as a
`binary_sensor: platform: gpio` (`esphome config` passes), and
`pulse_counter` validates on a **native** ESP32 GPIO (the `TachIO` /
`GPIO16` line) (`esphome config` passes). The decision below
(PWM-drive-only first) is unchanged by the proof — it confirms, rather
than revises, `PACKAGE-PWM-TACH-STRATEGY-001`.

Cross-checks consistent with the finding (not new evidence): the only
`pulse_counter` uses in the repo are on **native ESP32 GPIOs**
([`fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml) `${fan_tach_pin}`,
[`sense360_fan_pwm.yaml`](../../packages/expansions/sense360_fan_pwm.yaml)
`GPIO8`/`GPIO12`/`GPIO14`/`GPIO16`,
[`sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml)
`GPIO5`); both SX1509 packages
([`fan_pwm_sx1509.yaml`](../../packages/expansions/fan_pwm_sx1509.yaml),
[`gpio_expander_sx1509.yaml`](../../packages/expansions/gpio_expander_sx1509.yaml))
expose tach as `binary_sensor: platform: gpio`, never `pulse_counter`;
no custom tach/RPM component exists in [`components/`](../../components).

### Operator decision (PACKAGE-PWM-TACH-STRATEGY-001, 2026-05-25)

Recorded as **operator-attributed design decisions** (provenance:
operator response, 2026-05-25). They resolve the *scope* question; they
do **not** supply bench / waveform evidence and do **not** authorize a
package edit in this PR.

| # | Question | Operator decision |
|---|---|---|
| D-T1 | Is the first FanPWM package allowed to be PWM-drive-only, with no per-fan RPM initially? | **Yes — PWM-drive-only first.** `PACKAGE-PWM-001-IMPLEMENT-001` may proceed as a PWM-drive-only initial package: **four** independent SX1509 PWM outputs (channels 0..3); **no** per-fan RPM sensors; **optional diagnostic binary tach states only** (channels 4..7) if safe and useful; per-fan RPM remains **future work**. Do **not** claim RPM via SX1509 `pulse_counter`; do **not** build a custom component in this PR; keep the RPM limitation documented as a future `COMPONENT-SX1509-TACH-001` or bench-confirmed `TachIO` follow-up. |
| D-T2 | Should `TachIO` `GPIO16` be used as one aggregate/native RPM input if bench confirms it? | **Reserve only — no RPM claim now.** Document `GPIO16` / `TachIO` as reserved/pending: no aggregate RPM claim now, no per-fan RPM claim now, **no `TachIO` sensor in the initial package** unless separately proven safe. Future aggregate RPM via `TachIO` requires bench confirmation that `TachIO` carries a usable signal **and** resolution of any `GPIO16` conflict. |

### What stays blocked

- **Per-fan RPM** — blocked by the SX1509 hardware-`pulse_counter`
  limitation (above). Only a future `COMPONENT-SX1509-TACH-001` could
  change this; not pursued here.
- **Aggregate RPM via `TachIO`** — blocked pending (i) bench
  confirmation that the shared `TachIO` net carries a usable tach
  waveform, and (ii) resolution of the `GPIO16` conflict below.
- **FanPWM product / WebFlash / release surface** — unchanged; stays
  blocked behind `PACKAGE-PWM-001-IMPLEMENT-001` → `PRODUCT-PWM-001`.

### `GPIO16` conflict — open verification item

Recorded as an **open item**, not a resolved conflict. The direct
`TachIO` line is `GPIO16`, but `GPIO16` is also bound elsewhere in the
Core package stack: **W5500 Ethernet `RST` on the PoE core**
([`packages/hardware/sense360_core_poe.yaml`](../../packages/hardware/sense360_core_poe.yaml))
— material because the candidate FanPWM product family is
`Ceiling-POE-VentIQ-FanPWM-RoomIQ` (PoE power path) — and **Speaker I2S
`DIN` on the voice core**
([`sense360_core_voice.yaml`](../../packages/hardware/sense360_core_voice.yaml)).
Any future use of `TachIO` for aggregate RPM must first resolve this
`GPIO16` contention; the resolution belongs to the
`CORE-ABSTRACT-BUS-001` rebind + bench follow-up, **not** to this PR. No
conflict is asserted as resolved here.

## S360-311-BENCH-EVIDENCE-REQUEST-001 — FanPWM bench evidence checklist & contract (2026-05-26)

This section turns the still-open FanPWM bench blockers
(`PWM-3` / `PWM-6` / `PWM-10` / `PWM-11` / `PWM-13` in
[`blocker-burndown.md` §2A (archived)](../archive-index.md))
into one **operator-answerable checklist** and an explicit **pass/fail
evidence contract**. It is **documentation only**: it requests evidence,
it does not record results, change behaviour, or relax any guardrail in
[§Do-not-change guardrails](#do-not-change-guardrails). The lane is
**bench / operator / WebFlash-access gated, not repo gated** — package,
product, and full-compile are complete (`PWM-4` / `PWM-7` / `PWM-8` /
`PWM-9` CLOSED).

### Drive re-search result (2026-05-26)

A fresh Drive search for new FanPWM bench evidence (`S360-311`,
`S360-311-R4`, `FanPWM`, `PWM bench`, `polarity`, `current`, `thermal`,
`TachIO`, `GPIO16`, `fan test`, `product bench`, photos / videos /
spreadsheets / logs) found **no bench artifact**. The only FanPWM-bearing
material is **design / CAD only**:

- the already-recorded `12vFan_PWM_PulseCounter` set (schematic PDF,
  `.xlsx` BOM, gerbers, CPL, STEP, KiCad sources, 3 board renders);
- a canonically-named `S360-311-R4` Drive folder (from the PCB design
  owner) holding the same
  artifact classes under the board's catalog id — `S360-311-R4.kicad_sch`
  / `.kicad_pcb` / `.kicad_pro`, `S360-311-R4.step`,
  `S360-311-R4_GERBERS.zip`, `S360-311-R4_positions.csv` (CPL),
  `S360-311-R4.pdf` (schematic), `S360-311-R4_BOM.xlsx` (modified
  2026-02-08), and three renders `S360-311-R4.png` / `_2.png` / `_3.png`
  (modified 2026-05-14);
- the `Sense360_R4_Tracker` (2026-05-18, unchanged).

None of these is a PWM-polarity waveform, a per-fan / aggregate current
measurement, an MT3608 boost-ceiling note, an inrush / locked-rotor
capture, a thermal observation, or a product-bench sign-off. The
`S360-311-R4` folder is **board design / manufacturing provenance**, the
same artifact class as the committed
[`schematics/S360-311-R4.pdf`](schematics/S360-311-R4.pdf); it closes no
bench blocker and is recorded for provenance only — **no Drive file is
committed by this PR and no bench evidence is fabricated.**

### Operator checklist (fill in and attach evidence)

Every row is answerable by the hardware owner at the bench. Leave a row
`UNANSWERED` rather than guessing. Each row names the blocker it feeds.

| # | Item | Answer (operator fills in) | Feeds |
|---|---|---|---|
| 1 | **Board revision tested** (silkscreen P/N + rev; note if blank per tracker `G01`) | | PWM-3 |
| 2 | **Fan / load model tested** (make / model; 4-wire PWM fan; rated current) | | PWM-6 |
| 3 | **Supply voltage** (input rail into the board, e.g. 5 V PoE-derived) | | PWM-6 |
| 4 | **PSU / current limit** (bench PSU model; set current limit during test) | | PWM-6 |
| 5 | **Number of channels tested** (1–4 of `J1` / `J2` / `J4` / `J5`) | | PWM-6 |
| 6 | **PWM frequency used** (Hz at the SX1509 PWM-drive output) | | PWM-10 |
| 7 | **PWM duty range tested** (min%–max% commanded) | | PWM-10 |
| 8a | **PWM polarity — does increasing duty increase fan speed?** (yes / no) | | PWM-10 |
| 8b | **PWM polarity — is inversion required?** (yes / no; where: package vs gate path) | | PWM-10 |
| 9a | **Boot / default output — before ESPHome boots** (fan state: off / full / spinning?) | | PWM-10 / PWM-11 |
| 9b | **Boot / default output — after ESPHome boots** (commanded default duty / fan state) | | PWM-10 / PWM-11 |
| 9c | **Boot / default output — after restart** (glitch / transient on reboot?) | | PWM-10 / PWM-11 |
| 10 | **Per-channel current measured** (A per channel at full speed; method) | | PWM-6 |
| 11 | **Aggregate current with all four channels active** (total A at full speed) | | PWM-6 |
| 12 | **Inrush / startup behaviour** (peak A at spin-up; locked-rotor draw if observed) | | PWM-6 |
| 13a | **Thermal — duration** (how long the worst-case load ran) | | PWM-6 / PWM-13 |
| 13b | **Thermal — ambient temp** (°C) | | PWM-6 / PWM-13 |
| 13c | **Thermal — hottest component / location** (e.g. MT3608, `L1`, an `ME15N10-G` FET) | | PWM-6 / PWM-13 |
| 13d | **Thermal — measured temp or qualitative observation** (°C if measured, else note) | | PWM-6 / PWM-13 |
| 14 | **MT3608 / boost-converter observation** (output-current ceiling; sag / dropout under 4-fan load) | | PWM-6 |
| 15 | **Connector / pin-1 / silkscreen confirmation** (Core `J6` & module `J3` 1-to-13 order; fan-output `J1`/`J2`/`J4`/`J5` pin-1; UART on `J3` pins 11/12?) | | PWM-3 |
| 16 | **TachIO / GPIO16 observation (if any)** — *no RPM claim unless separately proven* (idle level, transitions; **not** an RPM figure) | | PWM-12 (deferred) |
| 17 | **Photos / videos / logs attached** (scope captures, multimeter shots, thermal photos, ESPHome log) | | all |
| 18 | **Operator / date / source / provenance** (who, when, board serial, Drive path of uploaded evidence) | | all |

### Pass/fail evidence contract

What evidence **closes** each open bench blocker, and what does **not**.

| Blocker | Closes when (PASS) | Does NOT close / FAIL |
|---|---|---|
| **PWM polarity (`PWM-10`)** | Scope or observed behaviour showing increasing commanded duty increases fan speed at the SX1509 PWM-drive output → fan PWM input, with the inversion-required answer recorded (items 6–8b). | A duty sweep with no recorded speed direction, or an un-scoped "it works" claim. |
| **Per-fan current (`PWM-6`)** | Measured per-channel current at full speed for the fan/load and supply under test, with method (items 2–5, 10). | Datasheet-only fan rating with no board-side measurement. |
| **Aggregate current (`PWM-6`)** | Measured total current with all four channels active at full speed, plus the inrush / locked-rotor peak (items 11–12, 14). | Single-channel figure multiplied by four; no inrush capture. |
| **Thermal (`PWM-6` / `PWM-13`)** | A worst-case-load thermal observation with duration, ambient, hottest location, and a measured or qualitative reading (items 13a–13d). Bench characterisation only — **not** a compliance / EMC approval. | No duration/ambient context, or a claim of certification. |
| **Product bench (`PWM-11`)** | Operator end-to-end FanPWM product-bench sign-off on the `S360-311-R4` board (boot/default behaviour items 9a–9c plus polarity/current/thermal above), with operator/date/serial and attached evidence (items 17–18). | A compile-pass or package test treated as a product-bench pass. |

### Out of scope (stays blocked regardless of this checklist)

These are **not** unlocked by any answer above and must not be claimed:

- **RPM support** — no `pulse_counter`; per-fan RPM via an SX1509 pin is
  compile-proven unsupported (`PWM-SX1509-TACH-PROOF-001`). `TachIO` /
  `GPIO16` stays reserved/pending; any RPM needs a separate approved tach
  strategy (`COMPONENT-SX1509-TACH-001`, future). A TachIO observation
  (item 16) is diagnostic only and is **not** an RPM claim.
- **WebFlash exposure** — no wrapper, no `config/webflash-builds.json`
  row, no `webflash_build_matrix` flip, no `artifact_name`; gated and
  additionally `NEEDS WEBFLASH ACCESS` (`PWM-15`).
- **Release artifact** — no `.bin` / tag / checksum / build-info
  (`RELEASE-PWM-001` stays blocked).
- **Import readiness** — `WF-IMPORT-PWM-001` stays blocked behind
  `RELEASE-PWM-001` (WebFlash-owned).
- **Hardware-stable promotion** — `S360-311` `schematic_status` stays
  `cataloged_unverified`; promotion is a separate JSON-only PR gated on
  the silkscreen / pin-map items, not on this checklist, unless policy
  explicitly allows.
- **Compliance approval** — board is SELV (5 V → 12 V boost, no mains), so
  `COMPLIANCE-001` does not apply; the thermal item is characterisation,
  not certification.

## S360-311-BENCH-RESULT-001 — FanPWM operator bench result (2026-05-26)

The operator (`@wifispray`) ran the FanPWM bench requested by
[`S360-311-BENCH-EVIDENCE-REQUEST-001`](#s360-311-bench-evidence-request-001--fanpwm-bench-evidence-checklist--contract-2026-05-26)
and reported a result. This section **records that operator evidence**
and closes / partially closes **only** the bench gates it actually
supports; every measurement and access gate the operator did **not**
cover stays open exactly as before. Evidence type is **operator notes
only** — no photo, video, scope capture, multimeter log, or thermal
image was uploaded — so it is recorded as an operator attestation
(provenance: operator `@wifispray`, 2026-05-26), the same evidence class
that closed the package-evidence rows in `S360-310-BENCH-EVIDENCE-001`.
It is **documentation only**: it changes no package / product / config /
WebFlash / firmware / release behaviour and relaxes no guardrail in
[§Do-not-change guardrails](#do-not-change-guardrails). RPM stays
unsupported (no `pulse_counter`; the SX1509 PWM-drive output is supported
and is the basis of FanPWM drive, kept distinct from the per-fan RPM
limitation that is compile-proven via `PWM-SX1509-TACH-PROOF-001`).

### Operator answers recorded (against the checklist)

| # | Item | Operator answer (recorded) | Feeds |
|---|---|---|---|
| 1 | Board revision tested | **S360-311-R4** | PWM-3 |
| 2 | Fan / load model tested | **Arctic P14 Plus** (12 V 4-wire PWM fan) | PWM-6 |
| 3 | Supply voltage | **12 V** from the on-board S360-311 **MT3608 boost** stage | PWM-6 |
| 4 | PSU / current limit | **up to ~2 A available** from the MT3608 boost output (capability, not a measured ceiling) | PWM-6 |
| 5 | Number of channels tested | **all 4** of `J1`/`J2`/`J4`/`J5`, each tested individually for speed / control | PWM-6 / PWM-11 |
| 6 | PWM frequency used | UNANSWERED (specific Hz not recorded) | PWM-10 |
| 7 | PWM duty range tested | **low / medium / high** (qualitative; specific min%–max% not recorded) | PWM-10 |
| 8a | Increasing duty increases fan speed? | **Yes** | PWM-10 |
| 8b | Inversion required? | **No** — increasing commanded duty increased fan speed directly (non-inverting) | PWM-10 |
| 9a–9c | Boot / default + **restart** behaviour | **Fans stayed on at the last commanded speed during restart** | PWM-10 / PWM-11 |
| 10 | Per-channel current measured | **NOT measured** | PWM-6 |
| 11 | Aggregate current (all 4 active) | **NOT measured** | PWM-6 |
| 12 | Inrush / startup | UNANSWERED (not captured) | PWM-6 |
| 13a | Thermal — duration | **1+ hour** with all four channels running | PWM-6 / PWM-13 |
| 13b–13c | Thermal — ambient / hottest location | UNANSWERED (not recorded) | PWM-6 / PWM-13 |
| 13d | Thermal — reading | **Qualitative: no heat issue noticed** (no measured °C / IR / thermocouple) | PWM-6 / PWM-13 |
| 14 | MT3608 / boost observation | No sag / dropout reported across the 1+ hour all-four run; measured output-current ceiling **NOT** characterised | PWM-6 |
| 15 | Connector / pin-1 / silkscreen confirmation | UNANSWERED (not addressed) | PWM-3 |
| 16 | TachIO / GPIO16 observation | **NOT measured** | PWM-12 (deferred) |
| 17 | Photos / videos / logs attached | **None** — operator notes only | all |
| 18 | Operator / date / provenance | Operator `@wifispray`, 2026-05-26; board S360-311-R4; "confirms working" | all |

All-board / all-channel scope: the operator tested **all four
fans/channels individually** for speed / control and ran **all four at
the same time** for **1+ hour** with no heat issue noticed, and confirmed
fans **retained the last commanded speed across a restart**. Operator
summary: **confirms working.**

### Gate dispositions (what this evidence does and does not close)

| Gate / blocker | Disposition | Why |
|---|---|---|
| **Board revision tested** (`PWM-3`) | **PARTIAL — recorded** | Board on the bench = `S360-311-R4` (items 1). The silkscreen pin-1 / `J6`/`J3` 1-to-13 order and the UART-on-`J3`-11/12 routing (the rest of `PWM-3`) were **not** addressed and stay `NEEDS BENCH`. |
| **Fan / load model tested** (`PWM-6`) | **PARTIAL — recorded** | Fan/load = **Arctic P14 Plus**, supply = **12 V MT3608 boost (~2 A available)** (items 2–4). The *measured* electrical characterisation (per-channel + aggregate current, MT3608 measured ceiling / sag, inrush) is **not** recorded and stays open. |
| **PWM polarity** (`PWM-10`) | **CLOSED — observed behaviour** | Increasing commanded duty increased fan speed across low/med/high; **no inversion required** (items 7–8b). The pass/fail contract accepts observed behaviour. Optional scope-trace of the gate waveform and exact Hz / min%–max% remain nice-to-have, **not** required to close the functional-polarity gate. |
| **Four-channel individual speed / control** (`PWM-11`) | **CLOSED — operator-attested** | All four channels (`J1`/`J2`/`J4`/`J5`) were each driven for speed / control individually (item 5). |
| **All-four simultaneous operation** (`PWM-11`) | **CLOSED — operator-attested** | All four fans ran at the same time (item 5 / 13a). |
| **Restart retained last commanded speed** (`PWM-11`) | **CLOSED — operator-attested** | Fans stayed on at the last commanded speed during restart (items 9a–9c). |
| **Product bench end-to-end** (`PWM-11`) | **CLOSED — functional, operator-notes-only** | The functional product bench (four-channel individual control + all-four simultaneous + restart retention + non-inverting polarity + qualitative 1+ hour run) is operator-attested PASS on `S360-311-R4`. The **measured** electrical / thermal characterisation is carried by `PWM-6` / `PWM-13` and stays open. |
| **Qualitative thermal observation, 1+ hour** (`PWM-13`) | **PARTIAL — recorded** | All four ran 1+ hour with no heat issue noticed (items 13a/13d). The **measured** thermal data (ambient, hottest-location °C via IR / thermocouple) and any EMI observation are **not** recorded and stay open. |
| **Per-channel current measurement** (`PWM-6`) | **OPEN** | Not measured (item 10). |
| **Aggregate current measurement** (`PWM-6`) | **OPEN** | Not measured (item 11). |
| **Measured thermal temperature / IR / thermocouple** (`PWM-13`) | **OPEN** | Only a qualitative "no heat issue" note; no measured °C (items 13b–13d). |
| **TachIO / GPIO16 observation** (`PWM-12`) | **OPEN / deferred** | Not measured (item 16); diagnostic only and **not** an RPM claim. |
| **RPM support** (`PWM-12`) | **OPEN — stays unsupported** | No `pulse_counter`; per-fan RPM via an SX1509 pin is compile-proven unsupported (`PWM-SX1509-TACH-PROOF-001`); `rpm_supported` stays `false`. |
| **WebFlash live access / `S360-311` module-availability** (`PWM-15`, `WF-1`/`WF-2`) | **OPEN — `NEEDS WEBFLASH ACCESS`** | Bench evidence does not grant WebFlash read access; classification stays owed to `WEBFLASH-PWM-LIVE-CHECK-001`. |
| **WebFlash wrapper / build / artifact / import** (`PWM-15`, `RELEASE-PWM-001`, `WF-IMPORT-PWM-001`) | **OPEN — gated** | No wrapper, no `config/webflash-builds.json` row, no `webflash_build_matrix` flip, no `artifact_name`, no `.bin` / import. |
| **Release readiness** (`RELEASE-PWM-001`) | **OPEN — gated** | Bench evidence discharges no release gate. |
| **Hardware-stable promotion** | **OUT OF SCOPE — not promoted** | `S360-311 schematic_status` stays `cataloged_unverified`; promotion is a separate JSON-only PR gated on the silkscreen / pin-map items, and this PR does **not** assert operator-notes-only bench evidence as sufficient for stable promotion. |
| **Compliance approval** (`PWM-14` / `CMP-2`) | **N/A — unchanged** | Board is SELV (5 V → 12 V boost, no mains); `COMPLIANCE-001` does not apply. The 1+ hour run is characterisation, **not** certification. |

### Exact remaining evidence checklist

To advance the still-open electrical / thermal characterisation the
operator (or a follow-up bench) must still supply:

1. **Measured current per channel** — A per channel at full speed, with
   method (`PWM-6`).
2. **Measured aggregate current with all four channels active** — total A
   at full speed, plus the MT3608 measured output-current ceiling / any
   sag under the four-fan load and the inrush / locked-rotor peak
   (`PWM-6`).
3. **Measured thermal temperature** — measured °C (or a documented
   thermal method) at the hottest location with ambient, **if policy
   requires more than the qualitative 1+ hour observation already
   recorded** (`PWM-13`).
4. **Optional TachIO / GPIO16 observation** — only if RPM / diagnostics
   ever become in scope; this is **not** an RPM claim and is not required
   for the current FanPWM (PWM-drive-only) posture (`PWM-12`).
5. **Photo / video / log evidence** — if policy requires more than the
   operator-notes-only attestation recorded here (item 17).

### Out of scope (stays blocked regardless of this result)

RPM support (`rpm_supported: false`; `TachIO`/`GPIO16` reserved; any RPM
→ `COMPONENT-SX1509-TACH-001`, future); WebFlash exposure (`PWM-15`,
`NEEDS WEBFLASH ACCESS`); release artifact (`RELEASE-PWM-001`); import
readiness (`WF-IMPORT-PWM-001`); hardware-stable promotion (`S360-311`
stays `cataloged_unverified`); compliance approval (board is SELV —
`COMPLIANCE-001` does not apply).

### Next-PR recommendation

- **If measured current / thermal remains required** → the next FanPWM PR
  is **`S360-311-CURRENT-THERMAL-001`** (measured per-channel current,
  measured four-fan aggregate current + MT3608 ceiling / inrush, and a
  measured thermal temperature or documented thermal method).
- **WebFlash stays separate and blocked** — operator notes are enough for
  the **product bench**, but **not** for WebFlash: the live-access
  re-check **`WEBFLASH-PWM-LIVE-CHECK-001`** stays blocked behind
  `sense360store/WebFlash` access restoration and the still-owed
  `S360-311` module-availability classification.
- **Do not recommend a WebFlash wrapper** (`WEBFLASH-PWM-001`) **until**
  measured current / thermal *and* the WebFlash live classification are
  done; `RELEASE-PWM-001` / `WF-IMPORT-PWM-001` stay gated behind that.

### Guardrails honoured / non-claims

This PR is **documentation-only**. It edits **no** `packages/**`,
`products/**`, `products/webflash/**`, `config/**`, `firmware/**`,
`manifest.json`, `firmware/sources.json`, release artifacts, checksums,
build-info manifests, any WebFlash repo file, `.github/workflows/**`,
`components/**`, or `include/**`. It changes **no** FanPWM package
behaviour, adds / edits **no** product YAML, adds **no** WebFlash
wrapper, flips **no** `webflash_build_matrix`, adds **no** `artifact_name`
or release artifact, claims **no** RPM support, and makes **no**
WebFlash / import / release / compliance / hardware-stable readiness
claim. It promotes **no** `schematic_status` (`S360-311` stays
`cataloged_unverified`) and fabricates **no** photo / video / log /
measurement evidence — the operator result is recorded as an attestation,
and the un-measured rows are kept explicitly open. Release-One
(`Ceiling-POE-VentIQ-RoomIQ` / stable) and the LED preview
(`Ceiling-POE-VentIQ-RoomIQ-LED` / preview) are unchanged.

## PWM-BLOCKER-RECLASSIFY-001 — FanPWM remaining blockers reclassified by release scope (2026-05-27)

The FanPWM package / product / compile chain is **complete**
(`PACKAGE-PWM-001-IMPLEMENT-001` / PR #590, `FW-COMPILE-PWM-001` / PR #591,
`FW-COMPILE-PWM-RESULT-001` / PR #592, `PRODUCT-PWM-001` / PR #593,
`FW-COMPILE-PWM-PRODUCT-001` / PR #594), `BLOCKER-BURNDOWN-001` (PR #599)
already found FanPWM is **evidence-gated, not repo-gated**, and
`S360-311-BENCH-RESULT-001` (PR #601) recorded the operator functional
bench. The remaining open items — **measured per-channel current**,
**measured aggregate current**, **measured thermal temperature**,
**`TachIO` / `GPIO16` observation**, **RPM support**, and the
**WebFlash live-access / wrapper / build / artifact / import / release**
chain — have, until now, been read as if they blocked *everything*. This
section **reclassifies** them by the surface each one actually gates.

It is **documentation only** — a classification decision, not a new
evidence record. It records **no** measurement, flips **no** posture,
changes **no** package / product / config / WebFlash / firmware / release
behaviour, and relaxes **no** guardrail in
[§Do-not-change guardrails](#do-not-change-guardrails). It makes **no**
RPM / WebFlash / import / release / compliance / hardware-stable readiness
claim and asserts **no** measured current / thermal value. RPM stays
unsupported (no `pulse_counter`; the SX1509 PWM-drive output is supported
and is the basis of FanPWM drive, kept distinct from the per-fan RPM
limitation that is compile-proven via `PWM-SX1509-TACH-PROOF-001`).

### Decision

The remaining FanPWM measured-current / thermal / `TachIO` gaps are **no
longer treated as blockers for repo / package / product / config work**.
They are reclassified as blockers **only** for WebFlash exposure, release
artifacts, import readiness, hardware-stable promotion, the production
electrical-margin claim, RPM / `TachIO` claims, and compliance / safety
claims. The non-claims stay exactly intact.

**Not a blocker for** (these may proceed without new bench evidence):

- FanPWM **package implementation** (`fan_pwm.yaml`, PWM-drive-only).
- FanPWM **product YAML** (`products/sense360-ceiling-poe-fanpwm.yaml`).
- FanPWM **compile-only target** (`ceiling-poe-fanpwm-compile-only`).
- **`config/` / product-catalog presence** of the FanPWM product row.
- The **no-WebFlash product-readiness posture** (`hardware-pending`,
  `webflash_build_matrix: false`, `rpm_supported: false`).
- **Future clean repo / YAML / firmware cleanup PRs** that do **not**
  expose WebFlash / release artifacts and do **not** claim
  hardware-stable / RPM / compliance.

**Still a blocker for** (these stay gated until the measured / access
evidence lands):

- **WebFlash exposure** (wrapper, `config/webflash-builds.json` row,
  `webflash_build_matrix` flip, `module-availability` classification).
- **Release artifacts** (`artifact_name`, `.bin` / tag / SHA256 / MD5 /
  build-info `manifest.json` / release-proof row; `RELEASE-PWM-001`).
- **Import readiness** (`WF-IMPORT-PWM-001`).
- **Hardware-stable promotion** (`S360-311 schematic_status` stays
  `cataloged_unverified`).
- **Production electrical-margin claim** (current / thermal headroom).
- **RPM / `TachIO` claims** (`rpm_supported` stays `false`).
- **Compliance / safety claims** (SELV board; `COMPLIANCE-001` n/a, and a
  qualitative 1+ hour run is characterisation, not certification).

### Scope classification table

| Blocker | Current evidence | Blocks package / product / config? | Blocks WebFlash / release? | Blocks hardware-stable? | Next evidence needed |
|---|---|---|---|---|---|
| **Measured per-channel current** (`PWM-6`) | Not measured; qualitative 1+ hour all-four run, no sag reported (operator notes only) | **No** | **Yes** | **Yes** | Measured A per channel at full speed + method → `S360-311-CURRENT-THERMAL-001` |
| **Measured aggregate current, all 4 active** (`PWM-6`) | Not measured | **No** | **Yes** | **Yes** | Measured total A + MT3608 measured ceiling / sag + inrush / locked-rotor peak → `S360-311-CURRENT-THERMAL-001` |
| **Measured thermal temperature** (`PWM-13`) | Qualitative "no heat issue" over 1+ hour; no measured °C / IR / thermocouple | **No** | **Yes** | **Yes** | Measured °C at hottest location + ambient, or a documented thermal method → `S360-311-CURRENT-THERMAL-001` |
| **Production electrical-margin claim** | Functional bench only; margins not characterised | **No** | **Yes** | **Yes** | The measured current + thermal rows above |
| **`TachIO` / `GPIO16` observation** (`PWM-12`) | Not measured | **No** | **No** — **RPM / diagnostics blocker only** | **No** | Optional observation **only if** RPM / diagnostics ever become in scope (not an RPM claim) |
| **RPM support** (`PWM-12`) | Compile-proven unsupported (`[sx1509] is an invalid option for [pin]`); `rpm_supported: false` | **No** | **No** | **No** | **Out of scope** for the current PWM-drive-only product; a separate approved tach strategy (`COMPONENT-SX1509-TACH-001`, future) |
| **WebFlash live access / `S360-311` module-availability** (`PWM-15`, `WF-1`/`WF-2`) | Read denied this session; not in any `module-availability.js` snapshot | **No** | **Yes** — **WebFlash exposure blocker only** | **No** | Restore `sense360store/WebFlash` read access → `WEBFLASH-PWM-LIVE-CHECK-001` |
| **WebFlash wrapper / build / artifact / import** (`PWM-15`, `RELEASE-PWM-001`, `WF-IMPORT-PWM-001`) | None | **No** | **Yes** | **No** | Wrapper + build-matrix + artifact, gated behind measured current/thermal **and** the WebFlash live classification |
| **Release readiness** (`RELEASE-PWM-001`) | None | **No** | **Yes** | **No** | Release-proof chain after the WebFlash wrapper |
| **Hardware-stable promotion** (`schematic_status`) | `cataloged_unverified`; operator-notes-only functional bench | **No** | **No** | **Yes** | Measured current / thermal (+ photo/video/log if policy requires) via a separate JSON-only PR |
| **Board-rev silkscreen / connector confirmation** (`PWM-3`) | Board tested = `S360-311-R4`; silkscreen pin-1 / UART-on-`J3`-11/12 not confirmed | **No** | Informs only | **Yes** | Silkscreen pin-1 read once an R4 silkscreen exists (fleet `G01`) + UART routing on bench |
| **Compliance / safety** (`PWM-14` / `CMP-2`) | SELV (5 V → 12 V boost); no mains path | **No** | **No** | **No** | None — `COMPLIANCE-001` mains gate does not apply |

### Explicit scope markings (as required)

- **Measured current / thermal** → **release / WebFlash / hardware-stable
  blocker only** (not a package / product / config blocker).
- **`TachIO` / `GPIO16`** → **RPM / diagnostics blocker only** (not a
  drive, product, release, or hardware-stable blocker).
- **RPM** → **out of scope for the current PWM-drive-only product**
  (`rpm_supported: false`; any RPM is a separate future component PR).
- **WebFlash live access** → **WebFlash exposure blocker only** (does not
  gate package / product / config, and does not gate hardware-stable).

## S360-311-CURRENT-THERMAL-EVIDENCE-REQUEST-001 — FanPWM current & thermal evidence checklist & contract (2026-05-27)

`S360-311-BENCH-RESULT-001` (PR #601) closed the FanPWM **functional**
gates (PWM polarity `PWM-10`, product bench `PWM-11`) on operator notes,
and `PWM-BLOCKER-RECLASSIFY-001` (PR #602) confirmed the remaining
**measured current / thermal** rows (`PWM-6` / `PWM-13`) gate **only**
WebFlash exposure, release artifacts, import readiness, hardware-stable
promotion, and the production electrical-margin claim — **not** clean
repo / YAML / firmware work. This section turns that still-open
measured-current / thermal lane into one **operator-answerable checklist**
and an explicit **pass/fail evidence contract**, so the later result PR
(`S360-311-CURRENT-THERMAL-001`) is small and evidence-backed.

It is **documentation only**: it **requests** evidence, records none,
changes no package / product / config / WebFlash / firmware / release
behaviour, and relaxes no guardrail in
[§Do-not-change guardrails](#do-not-change-guardrails). It asserts **no**
measured current / thermal value, makes **no** RPM / WebFlash / import /
release / compliance / hardware-stable readiness claim, and promotes
**no** `schematic_status` (`S360-311` stays `cataloged_unverified`). It
expands the brief "exact remaining evidence checklist" recorded in
[§S360-311-BENCH-RESULT-001](#s360-311-bench-result-001--fanpwm-operator-bench-result-2026-05-26)
into a precise fill-in form; it does **not** re-open any gate that
`S360-311-BENCH-RESULT-001` already closed.

### Drive re-search result (2026-05-27)

A fresh Drive search for measured FanPWM current / thermal evidence
(`S360-311`, `S360-311-R4`, `FanPWM`, `PWM`, `current`, `thermal`,
`inrush`, `MT3608`, `bench`, `fan`, plus spreadsheets / PDFs / photos)
found **no measurement artifact** — no per-channel or aggregate current
log, no inrush / locked-rotor capture, no MT3608 output-current ceiling
note, and no measured thermal / IR / thermocouple reading. The only
FanPWM-bearing material is **design / CAD only**: the already-recorded
`12vFan_PWM_PulseCounter` set (schematic PDF, `.xlsx` BOM, gerbers, CPL,
STEP, KiCad sources, renders incl. `PWM.png`); the canonically-named
`S360-311-R4` Drive folder (from the PCB design owner) holding
`S360-311-R4.kicad_sch` / `.kicad_pcb` / `.kicad_pro`,
`S360-311-R4.step`, `S360-311-R4_GERBERS.zip`,
`S360-311-R4_positions.csv` (CPL), `S360-311-R4.pdf` (schematic),
`S360-311-R4_BOM.xlsx`, and the board renders; and the unchanged
`Sense360_R4_Tracker` (2026-05-18). This is the same artifact class as the
committed [`schematics/S360-311-R4.pdf`](schematics/S360-311-R4.pdf), is
recorded for provenance only, closes no measurement blocker, and **no
Drive file is committed by this PR and no measurement evidence is
fabricated.** `S360-311-CURRENT-THERMAL-001` stays **gated** until the
operator supplies the measured rows below.

### Operator checklist (fill in and attach evidence)

Every row is answerable by the hardware owner at the bench. Leave a row
`UNANSWERED` rather than guessing. Each row names the blocker it feeds.
Where `S360-311-BENCH-RESULT-001` already recorded an operator answer it
is shown as the **starting point** so the operator only needs to add the
*measured* data.

| # | Item | Answer (operator fills in) | Feeds |
|---|---|---|---|
| 1 | **Board revision tested** (silkscreen P/N + rev; note if blank per tracker `G01`) — starting point: `S360-311-R4` | | PWM-3 |
| 2 | **Fan model + label current rating** (make / model; rated A from the fan label / datasheet) — starting point: Arctic P14 Plus | | PWM-6 |
| 3 | **Supply voltage** (rail into the fans; e.g. 12 V from the on-board MT3608 boost) — starting point: 12 V MT3608 | | PWM-6 |
| 4 | **Measured supply current** (total A drawn from the supply during the test; meter / method) | | PWM-6 |
| 5 | **Per-channel current at full speed** (measured A per channel `J1`/`J2`/`J4`/`J5`; meter / method) | | PWM-6 |
| 6 | **Aggregate current, all four channels active** (measured total A at full speed) | | PWM-6 |
| 7 | **Inrush / startup current** (peak A at spin-up; locked-rotor draw — *if measurable*) | | PWM-6 |
| 8 | **MT3608 input / output current or measured ceiling** (boost output-current ceiling; input current; any sag / dropout under 4-fan load) | | PWM-6 |
| 9 | **Thermal method** (IR thermometer / thermal camera / thermocouple / qualitative only) | | PWM-13 |
| 10 | **Test duration** (how long the worst-case load ran) — starting point: 1+ hour all-four | | PWM-13 |
| 11 | **Ambient temperature** (°C) | | PWM-13 |
| 12 | **Hottest component / location** (e.g. MT3608, `L1`, an `ME15N10-G` FET) | | PWM-13 |
| 13 | **Measured max temperature** (°C at the hottest location; or `qualitative only` if no instrument) | | PWM-13 |
| 14 | **Did all four channels run at high / full duty?** (yes / no; which duty) | | PWM-6 / PWM-13 |
| 15 | **Any voltage drop, instability, or reset?** (rail sag, brown-out, ESP reset, fan stall — yes / no + detail) | | PWM-6 |
| 16 | **TachIO / GPIO16 observation (only if tested)** — *no RPM claim unless separately proven* (idle level, transitions; **not** an RPM figure) | | PWM-12 (deferred) |
| 17 | **Photos / videos / logs** (multimeter / clamp-meter shots, scope captures, thermal photos, ESPHome log — *if available*) | | all |
| 18 | **Operator / date / source / provenance** (who, when, board serial, Drive path of uploaded evidence) | | all |

### Pass/fail evidence contract

What evidence **closes** each open measured-current / thermal blocker, and
what does **not**.

| Blocker | Closes when (PASS) | Does NOT close / FAIL |
|---|---|---|
| **Per-channel current (`PWM-6`)** | Measured per-channel current at full speed for the fan/load and supply under test, with meter / method (items 2–5, 14). | Fan-label / datasheet rating only, with no board-side measurement. |
| **Aggregate current (`PWM-6`)** | Measured total current with all four channels active at full speed, plus measured supply current and — if measurable — the inrush / locked-rotor peak (items 4, 6–7, 14). | A single-channel figure multiplied by four; no measured aggregate. |
| **MT3608 / boost ceiling (`PWM-6`)** | Measured MT3608 input / output current or a documented output-current ceiling, with any sag / dropout under the four-fan load noted (items 8, 15). | "~2 A available" capability quoted as if it were a measured ceiling. |
| **Electrical-margin observation (`PWM-6`)** | The measured aggregate + inrush vs the MT3608 ceiling, with the voltage-drop / instability / reset answer recorded (items 6–8, 15). Bench characterisation only — **not** a production margin certification. | A "looks fine" claim with no measured headroom, or a certification claim. |
| **Measured thermal (`PWM-13`)** | A worst-case-load thermal observation with method, duration, ambient, hottest location, and a measured max temperature (items 9–13) — or an explicit documented `qualitative only` method if no instrument was used. Characterisation, **not** a compliance / EMC approval. | "No heat issue" with no method / duration / ambient context, or a claim of certification. |

### Out of scope (stays blocked regardless of this checklist)

These are **not** unlocked by any answer above and must not be claimed:

- **RPM support** — no `pulse_counter`; per-fan RPM via an SX1509 pin is
  compile-proven unsupported (`PWM-SX1509-TACH-PROOF-001`). `TachIO` /
  `GPIO16` (item 16) is a diagnostic observation only; any RPM is a
  separate future component PR (`COMPONENT-SX1509-TACH-001`).
- **WebFlash exposure** (`PWM-15`, `NEEDS WEBFLASH ACCESS`) — measured
  current / thermal does not grant WebFlash read access; classification
  stays owed to `WEBFLASH-PWM-LIVE-CHECK-001`.
- **Release artifact** (`RELEASE-PWM-001`) and **import readiness**
  (`WF-IMPORT-PWM-001`).
- **Hardware-stable promotion** — `S360-311 schematic_status` stays
  `cataloged_unverified`; promotion is a separate JSON-only PR.
- **Compliance approval** — board is SELV (5 V → 12 V boost, no mains);
  `COMPLIANCE-001` does not apply, and any bench thermal run is
  characterisation, **not** certification.

## S360-311-NATIVE-FANPWM-BENCH-001 — native FanPWM operator bench result (2026-05-29)

The operator (`@wifispray`) flashed the **native** ESP32-S3 GPIO FanPWM
firmware and re-ran the FanPWM bench. This section **records that operator
evidence** for the **native composition** and closes / partially closes
**only** the bench gates it actually supports; every measurement and
access gate the operator did **not** cover stays open exactly as before.

This is distinct from
[`S360-311-BENCH-RESULT-001`](#s360-311-bench-result-001--fanpwm-operator-bench-result-2026-05-26)
(2026-05-26), which ran the **legacy SX1509** composition. Because the
native candidate re-binds FanPWM control to **different pins**
(`TachPMW1..4` -> `IO10`/`IO11`/`IO12`/`IO39` via `ledc`, with no SX1509),
the earlier functional bench does **not** automatically transfer — the
same reasoning the compile lane applied (the legacy SX1509 full-compile
run `26414398902` did not transfer to the native composition either, so
S360-311-NATIVE-FANPWM-COMPILE-001 ran the native composition's own
compile). This PR records the native composition's **own** functional
bench.

Evidence type is **operator notes only** — no photo, video, scope
capture, multimeter log, or thermal image was uploaded — so it is
recorded as an operator attestation (provenance: operator `@wifispray`,
2026-05-29), the same evidence class that closed the functional rows in
`S360-311-BENCH-RESULT-001`. It is **documentation only**: it changes no
package / product / config / WebFlash / firmware / release behaviour and
relaxes no guardrail in
[§Do-not-change guardrails](#do-not-change-guardrails). RPM stays
unsupported (`rpm_supported: false`); tach / RPM and current / thermal
stay **unvalidated** because they were not measured.

### Hardware setup (recorded)

| Field | Value (recorded) |
|---|---|
| S360-100 Core revision | **S360-100-R4** (native ESP32-S3 GPIO fan path per [`s360-100-native-fan-gpio-map.md`](s360-100-native-fan-gpio-map.md), S360-100-NATIVE-FAN-GPIO-MAP-001) |
| S360-311 PWM board revision | **S360-311-R4** |
| Fan model / load | **Arctic P14 Plus** (12 V 4-wire PWM fan), one per channel across `J1`/`J2`/`J4`/`J5` (same bench rig as `S360-311-BENCH-RESULT-001`) |
| Supply voltage / current source | **12 V** from the on-board S360-311 **MT3608 boost** stage; **up to ~2 A available** (capability, **not** a measured ceiling) |
| Firmware target flashed | **native composition** — `packages/expansions/fan_pwm_native.yaml` composed via [`products/compile-only/ceiling-poe-fanpwm-native.yaml`](../../products/compile-only/ceiling-poe-fanpwm-native.yaml) (target `ceiling-poe-fanpwm-native-compile-only`); native `ledc` PWM on `IO10`/`IO11`/`IO12`/`IO39` |
| Commit SHA / build source | native composition **compile-proven at commit `643bbd3`** (S360-311-NATIVE-FANPWM-COMPILE-001); operator flashed a local build of that composition (no published / release artifact) |

### Functional PWM test (recorded — PASS)

| # | Item | Operator answer (recorded) | Result |
|---|---|---|---|
| 1 | Channel 1 control (`J1`) | Individually speed-controlled | **PASS** |
| 2 | Channel 2 control (`J2`) | Individually speed-controlled | **PASS** |
| 3 | Channel 3 control (`J4`) | Individually speed-controlled | **PASS** |
| 4 | Channel 4 control (`J5`) | Individually speed-controlled | **PASS** |
| 5 | All-four simultaneous control | All four driven at the same time | **PASS** |
| 6 | High / medium / low command | Low / medium / high tracked commanded duty (qualitative; exact Hz / min%–max% not recorded) | **PASS** |
| 7 | Restart-retention | Fans retained the last commanded speed across a restart | **PASS** |

All four channels were individually speed-controlled on the **native**
firmware, all four ran simultaneously, low / medium / high commands
tracked, and the fans retained the last commanded speed across a restart.
Operator summary: **confirms working on native firmware.**

### Tach / RPM test (recorded — NOT measured)

| Item | Recorded |
|---|---|
| Tach / RPM measured? | **NO — not measured** |
| Per-channel tach / RPM values | **None** — tach / RPM stays **unvalidated** |
| `rpm_supported` | **false** (unchanged) |
| Native pulse-counter inputs (`Pul_Cou1`/`Pul_Cou2`/`Pul_Cou4` -> `IO17`/`IO18`/`IO9`) | internal-diagnostic only; **not read for RPM** on this bench |
| `Pul_Cou3` (`IO46`) caveat | **still applicable — disabled / TBD** (collides with the Core `fan_status_led_pin` `GPIO46`) |
| `TachIO` (`IO16`) | **reserved / pending** (ambiguous shared-passthrough role) |

No RPM / tach value is claimed. Any future RPM is a separate
firmware-binding + bench PR; this bench did not measure it.

### Power / current / thermal (recorded — NOT measured)

| Item | Recorded |
|---|---|
| Current draw per channel | **NOT measured** |
| Aggregate current (all four) | **NOT measured** |
| MT3608 measured output-current ceiling / inrush | **NOT measured** |
| Thermal observation duration | **Not separately quantified** for the native run |
| Heat / no-heat result | **NOT measured** (no measured °C / IR / thermocouple); measured thermal stays open |
| Instability / reset / brownout / supply issue | **None reported** during the functional native bench (functional speed control across all four channels and restart-retention succeeded, indicating stable operation during the test); a *measured* MT3608 ceiling / sag / inrush characterisation was **not** captured |

The measured electrical / thermal envelope stays open and is carried by
`PWM-6` / `PWM-13` →
[`S360-311-CURRENT-THERMAL-001`](#s360-311-current-thermal-evidence-request-001--fanpwm-current--thermal-evidence-checklist--contract-2026-05-27).

### Outcome classification

| Dimension | Disposition |
|---|---|
| **PWM functional (native)** | **VALIDATED — operator-attested PASS** (operator-notes-only) on the native composition: all four channels individual + simultaneous + high/med/low + restart-retention. |
| **Tach / RPM** | **NOT MEASURED — stays unvalidated** (`rpm_supported: false`); `Pul_Cou3`/`IO46` disabled/TBD; `TachIO`/`IO16` reserved/pending. |
| **Current / thermal** | **NOT MEASURED — stays unvalidated** (carried by `PWM-6` / `PWM-13` → `S360-311-CURRENT-THERMAL-001`). |
| **Release / WebFlash** | **REMAINS BLOCKED** — all gates intentionally stay closed; no wrapper / build-matrix / artifact / import / release. |

### Gate dispositions (what this evidence does and does not close)

| Gate / blocker | Disposition | Why |
|---|---|---|
| **Native FanPWM candidate functional bench** (`PWM-16`) | **FUNCTIONAL BENCH — operator-attested PASS (native)** | Adds operator-attested functional PASS on the native composition to the existing compile validation; current / thermal / RPM stay carried by `PWM-6` / `PWM-12` / `PWM-13`. |
| **PWM polarity / functional control (native)** | **PASS — observed behaviour** | All four channels tracked commanded duty (low/med/high); restart retained last commanded speed. |
| **Per-channel + aggregate current** (`PWM-6`) | **OPEN — not measured** | Not measured on the native bench. |
| **Measured thermal temperature** (`PWM-13`) | **OPEN — not measured** | No measured °C; thermal stays open. |
| **TachIO / GPIO16 observation** (`PWM-12`) | **OPEN / deferred** | Not measured; not an RPM claim; `Pul_Cou3`/`IO46` disabled/TBD. |
| **RPM support** (`PWM-12`) | **OPEN — stays unsupported** | Not measured; `rpm_supported` stays `false`. |
| **WebFlash wrapper / build / artifact / import** (`PWM-15`, `RELEASE-PWM-001`, `WF-IMPORT-PWM-001`) | **OPEN — gated** | No wrapper, no `config/webflash-builds.json` row, no `webflash_build_matrix` flip, no `artifact_name`, no `.bin` / import. |
| **Release readiness** (`RELEASE-PWM-001`) | **OPEN — gated** | Bench evidence discharges no release gate. |
| **Hardware-stable promotion** | **OUT OF SCOPE — not promoted** | `S360-311 schematic_status` stays `cataloged_unverified`. |
| **Compliance approval** (`PWM-14` / `CMP-2`) | **N/A — unchanged** | Board is SELV (5 V → 12 V boost, no mains); `COMPLIANCE-001` does not apply. |

### Guardrails honoured / non-claims

This PR is **documentation-only**. It edits **no** `packages/**`,
`products/**`, `products/webflash/**`, `firmware/**`, `manifest.json`,
`firmware/sources.json`, release artifacts, checksums, build-info
manifests, any WebFlash repo file, `.github/workflows/**`,
`components/**`, or `include/**`, and touches `config/**` only to record
evidence / status notes (no `webflash_build_matrix` flip, no
`artifact_name`, no `config/webflash-builds.json` row). It changes **no**
FanPWM package behaviour, adds / edits **no** product YAML, adds **no**
WebFlash wrapper, adds **no** release artifact, and asserts **no**
measured current, **no** measured thermal temperature, and **no** RPM /
tach value — those rows are kept explicitly open. It makes **no**
WebFlash / import / release / compliance / hardware-stable readiness
claim, claims **no** S360-410 PoE blocker resolution, promotes **no**
`schematic_status` (`S360-311` stays `cataloged_unverified`), and
fabricates **no** photo / video / log / measurement evidence — the
operator functional result is recorded as an attestation, and the
un-measured rows are kept explicitly open. Release-One
(`Ceiling-POE-VentIQ-RoomIQ` / stable) and the LED preview
(`Ceiling-POE-VentIQ-RoomIQ-LED` / preview) are unchanged.

## S360-311-CURRENT-THERMAL-001 — measured current & thermal bench run (2026-05-29 + 2026-05-31; no values recorded)

This section is the dated result record for the measured-current /
thermal bench run requested by
[§S360-311-CURRENT-THERMAL-EVIDENCE-REQUEST-001](#s360-311-current-thermal-evidence-request-001--fanpwm-current--thermal-evidence-checklist--contract-2026-05-27)
and owed by `PWM-6` (output electrical characteristics) and `PWM-13`
(board-level thermal / EMI) for the **native** ESP32-S3 GPIO FanPWM
composition on the `S360-100-R4` Core + `S360-311-R4` PWM board. It is
the measured follow-up to the **functional-only** native bench recorded
in
[§S360-311-NATIVE-FANPWM-BENCH-001](#s360-311-native-fanpwm-bench-001--native-fanpwm-operator-bench-result-2026-05-29)
(2026-05-29), which explicitly left current and thermal unmeasured.

**Outcome: NO measured current or thermal values were recorded.** The
measurement intake for this PR arrived **blank** — no per-channel
current, no aggregate current, no MT3608 measured output voltage / sag /
ceiling, no inrush / locked-rotor peak, no thermal method / ambient /
hottest-location / measured temperature, and no EMI observation. Per the
evidence-request contract and the project no-fabrication rule, **no
value is inferred, estimated, or back-filled from the fan label, the
MT3608 datasheet, or the "~2 A available" supply capability.** The
measured-current / thermal envelope therefore **stays owed**; `PWM-6`
and `PWM-13` stay **Partial** exactly as before this PR, and
`S360-311-CURRENT-THERMAL-001` remains **gated** until the operator
supplies the measured rows.

### 2026-05-31 re-run (second pass — functional re-confirmed; current / thermal / tach again NOT measured)

The `S360-311-CURRENT-THERMAL-001` bench pass was **re-run on 2026-05-31**
by the operator (`@wifispray`) on the same native ESP32-S3 GPIO FanPWM
composition and rig recorded below. The result is recorded honestly: the
**functional PWM behaviour re-confirmed PASS**, but the **measured
current / thermal / tach intake again arrived blank** — exactly the same
disposition as the 2026-05-29 first pass. No `PWM-6` / `PWM-13` row moves.

| Dimension | 2026-05-31 re-run disposition |
|---|---|
| **Functional PWM (native)** | **RE-CONFIRMED PASS** (operator-notes-only) — all four channels (`J1`/`J2`/`J4`/`J5`) individually speed-controlled, all four simultaneously, low / medium / high tracked commanded duty, last commanded speed retained across a restart. No instability / reset / brownout reported during the functional run. Re-affirms `S360-311-NATIVE-FANPWM-BENCH-001`; adds no new measured envelope. |
| **Per-channel current** (`PWM-6`) | **NOT measured** — no per-fan A captured. Stays owed / Partial. |
| **Aggregate current + MT3608 ceiling** (`PWM-6`) | **NOT measured** — no aggregate A, no measured MT3608 output voltage / sag / current ceiling / inrush. Stays owed / Partial. |
| **Thermal** (`PWM-13`) | **NOT measured** — no sustained-load thermal run; no method / ambient / hottest-location / measured °C on `Q1..Q4` / MT3608 / `L1` / `D1`. Stays owed / Partial. |
| **Tach / RPM** (`PWM-12`) | **Explicitly NOT measured** — RPM stays **unvalidated**; `rpm_supported` stays **false**; the native pulse-counter inputs (`Pul_Cou1`/`Pul_Cou2`/`Pul_Cou4` -> `IO17`/`IO18`/`IO9`) were not read for RPM. |
| **`Pul_Cou3` (`IO46`)** | **Disabled / TBD** — unchanged; collides with the Core `fan_status_led_pin` `GPIO46`. Not resolved on this run. |
| **`TachIO` (`IO16`)** | **Reserved / pending** — unchanged; ambiguous shared-passthrough role. Not resolved on this run. |
| **`J3` 1-to-13 silkscreen order** | **OWED** — not proven on this run. |
| **`J6`↔`J3` 13-pin harness mapping** | **OWED** — not proven on this run. |
| **`"NINE 4pin FANs"` label** | **OWED** — not explained on this run. |
| **`J3` 11/12 UART routing** | **OWED** — not proven on this run. |
| **Release / WebFlash / hardware-stable** | **REMAIN BLOCKED** — no wrapper / build-matrix / artifact / import / release; `S360-311 schematic_status` stays `cataloged_unverified`. |

Fan model / load and supply were **not re-specified** by the operator on
this pass; the established rig on file (recorded below from
`S360-311-NATIVE-FANPWM-BENCH-001`) is carried for provenance only and is
**not** re-attested as a 2026-05-31 measurement. Per the no-fabrication
rule, no current / thermal / RPM value is inferred or back-filled. The
measured-current / thermal envelope and per-fan RPM therefore **stay
owed**; the exact still-owed measurement list under
[§Exact measurements still owed](#exact-measurements-still-owed) is
unchanged by this re-run.

### Rig on file (unchanged; recorded for provenance)

| Field | Value (recorded) |
|---|---|
| S360-100 Core revision | **S360-100-R4** (native ESP32-S3 GPIO fan path; S360-100-NATIVE-FAN-GPIO-MAP-001) |
| S360-311 PWM board revision | **S360-311-R4** |
| Fan model / load | **Arctic P14 Plus** (12 V 4-wire PWM fan), one per channel across `J1`/`J2`/`J4`/`J5` |
| Supply / current source | **12 V** from the on-board S360-311 **MT3608 boost**; **up to ~2 A available** (capability, **not** a measured ceiling) |
| Firmware target | **native composition** — `packages/expansions/fan_pwm_native.yaml` via [`products/compile-only/ceiling-poe-fanpwm-native.yaml`](../../products/compile-only/ceiling-poe-fanpwm-native.yaml); compile-proven at commit `643bbd3` (S360-311-NATIVE-FANPWM-COMPILE-001) |
| Operator | `@wifispray` |

This rig matches the functional native bench (S360-311-NATIVE-FANPWM-BENCH-001);
the only addition this run would have made is the **measured** electrical /
thermal data, and that data was not captured.

### Measured current (recorded — NOT measured)

| Item | Recorded value | Feeds |
|---|---|---|
| Per-channel current at high speed, `J1` | **NOT measured** | PWM-6 |
| Per-channel current at high speed, `J2` | **NOT measured** | PWM-6 |
| Per-channel current at high speed, `J4` | **NOT measured** | PWM-6 |
| Per-channel current at high speed, `J5` | **NOT measured** | PWM-6 |
| Aggregate current, all four at high | **NOT measured** | PWM-6 |
| MT3608 measured output voltage under four-fan load (and no-load) | **NOT measured** | PWM-6 |
| MT3608 measured output-current ceiling before sag / fold-back | **NOT measured** | PWM-6 |
| Locked-rotor / inrush peak (single channel) + method | **NOT measured** | PWM-6 |

### Measured thermal / EMI (recorded — NOT measured)

| Item | Recorded value | Feeds |
|---|---|---|
| Thermal method (IR camera / thermocouple) | **NOT recorded** | PWM-13 |
| Ambient during thermal run (°C) | **NOT recorded** | PWM-13 |
| Hottest measured location + value (after 1+ hour, four fans high) | **NOT measured** | PWM-13 |
| EMI qualitative observation | **NOT recorded** | PWM-13 |

### Gate dispositions (what this run does and does not close)

| Gate / blocker | Disposition | Why |
|---|---|---|
| **Per-channel + aggregate current** (`PWM-6`) | **OPEN — not measured; stays Partial** | No measured A on this run; intake blank. |
| **MT3608 measured ceiling / sag / inrush** (`PWM-6`) | **OPEN — not measured; stays Partial** | No measured boost output voltage / current / inrush. |
| **Measured thermal temperature** (`PWM-13`) | **OPEN — not measured; stays Partial** | No method / ambient / hottest-location / °C recorded. |
| **EMI observation** (`PWM-13`) | **OPEN — not recorded** | None captured; an EMI observation would be an observation, **never** a compliance approval. |
| **RPM support** (`PWM-12`) | **OUT OF SCOPE — stays unsupported** | Not in scope; `rpm_supported` stays `false`; `Pul_Cou3`/`IO46` disabled/TBD; `TachIO`/`IO16` reserved/pending. |
| **WebFlash / release / import** (`PWM-15`, `RELEASE-PWM-001`, `WF-IMPORT-PWM-001`) | **OPEN — gated** | Unchanged; a measured PASS would close `PWM-6`/`PWM-13` only and would **not** by itself enable WebFlash (`PWM-15` live-check gate) or promote the board. |
| **Hardware-stable promotion** | **OUT OF SCOPE — not promoted** | `S360-311 schematic_status` stays `cataloged_unverified`. |
| **Compliance approval** (`PWM-14` / `CMP-2`) | **N/A — unchanged** | Board is SELV (5 V → 12 V boost, no mains). |

### Exact measurements still owed

The following must be supplied by the operator at the bench before
`PWM-6` / `PWM-13` can move from Partial toward CLOSED (a re-run of
`S360-311-CURRENT-THERMAL-001` with values filled in):

1. Per-channel current at high speed for `J1`, `J2`, `J4`, `J5` (measured A + meter / method).
2. Aggregate current with all four channels at high (measured total A).
3. MT3608 output voltage under four-fan load and at no-load (sag), plus the measured output-current ceiling before sag / fold-back.
4. Locked-rotor / inrush peak on a single channel, with the method used.
5. Thermal method (IR camera / thermocouple), ambient °C, hottest measured location, and the measured temperature after a 1+ hour four-fan-high run.
6. The EMI qualitative observation (recorded as an observation only — never a compliance claim).

### Guardrails honoured / non-claims

This PR is **documentation + catalog-notes only**. It edits **no**
`packages/**`, `products/**`, `products/webflash/**`, `firmware/**`,
`manifest.json`, `firmware/sources.json`, release artifacts, checksums,
build-info manifests, any WebFlash repo file, `.github/workflows/**`,
`components/**`, or `include/**`, and touches `config/**` only to append
an evidence note to the existing FanPWM `notes` field (no
`webflash_build_matrix` flip, no `artifact_name`, no
`config/webflash-builds.json` row, no `status` change). It changes **no**
FanPWM package behaviour, adds / edits **no** product YAML, adds **no**
WebFlash wrapper, adds **no** release artifact, and asserts **no**
measured current, **no** measured thermal temperature, **no** EMI
compliance approval, and **no** RPM / tach value — every measured row is
kept explicitly open. A measured current / thermal PASS would close
`PWM-6` / `PWM-13` **only**; it would **not** by itself enable WebFlash
(`PWM-15` live-check gate) or promote the board. It makes **no** WebFlash /
import / release / compliance / hardware-stable readiness claim, claims
**no** S360-410 PoE blocker resolution, keeps `rpm_supported: false`
(`PWM-12` out of scope; `Pul_Cou3`/`IO46` disabled/TBD; `TachIO`/`IO16`
reserved/pending), does **not** promote `S360-311` `schematic_status`
(stays `cataloged_unverified`), and fabricates **no** measurement /
photo / video / log evidence — the intake was blank and is recorded as
such. Release-One (`Ceiling-POE-VentIQ-RoomIQ` / stable) and the LED
preview (`Ceiling-POE-VentIQ-RoomIQ-LED` / preview) are unchanged.

## Do-not-change guardrails

This PR does **not** edit:

- [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
- [`config/product-catalog.json`](../../config/product-catalog.json)
- [`config/webflash-builds.json`](../../config/webflash-builds.json)
- [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json)
- any product YAML under [`products/`](../../products/), including
  [`products/sense360-fan-pwm.yaml`](../../products/sense360-fan-pwm.yaml)
- any WebFlash wrapper under
  [`products/webflash/`](../../products/webflash/)
- any package YAML under [`packages/`](../../packages/), including
  [`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml),
  [`packages/expansions/sense360_fan_pwm.yaml`](../../packages/expansions/sense360_fan_pwm.yaml),
  [`packages/expansions/gpio_expander_sx1509.yaml`](../../packages/expansions/gpio_expander_sx1509.yaml),
  [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml),
  and [`packages/hardware/sense360_core.yaml`](../../packages/hardware/sense360_core.yaml)
- any script under `scripts/`
- any test under `tests/`
- any workflow under `.github/workflows/`
- any component under `components/`
- any header under `include/`
- `.gitignore`
- the per-board reference docs
  ([`s360-100-r4-core.md`](s360-100-r4-core.md) and siblings) —
  the Core `J6` capture stays as it is; the
  UART-on-`J3`-pins-11/12 discrepancy is recorded here and is
  **not** rewritten on the Core-side doc.
- the curated artifact index
  [`docs/hardware/artifacts/S360-311-R4.md`](artifacts/S360-311-R4.md) —
  its content is consumed by this audit, not rewritten by it.
- [`docs/hardware/schematics/S360-311-R4.pdf`](schematics/S360-311-R4.pdf) —
  the schematic PDF stays byte-identical to the HW-ASSETS-003
  commit.

This PR does **not**:

- mark `S360-311` `verified`,
- add or set `schematic_file` for `S360-311` in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json),
- mark the pin map confirmed,
- change [`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml)
  from `package-yaml-pending` to `confirmed-ok`,
- promote `S360-311` to `preview` / `stable` / `production`,
- add a `FanPWM` token to any Release-One or preview config string,
- add a `FanPWM`-bearing entry to
  [`config/webflash-builds.json`](../../config/webflash-builds.json),
- regenerate firmware, create a GitHub Release or tag, or change
  any WebFlash manifest / import,
- resolve the SX1509-channel vs direct-ESP32-GPIO mapping
  disagreement,
- resolve the single-channel vs four-channel canonical abstraction
  decision,
- resolve the Core `J6` 1-to-13 silkscreen verify flag,
- resolve the UART-on-`J3`-pins-11/12 routing question,
- resolve the `"NINE 4pin FANs"` section-title documentation
  question,
- change LED preview path or Sense360 LED Release-One exclusion,
- unblock FanTRIAC (HW-005 stays a separate gate),
- change the mains-voltage compliance status for `S360-320` or
  `S360-400` (COMPLIANCE-001),
- resolve the Core J10 vs RoomIQ J6 pin-order open question (HW-009
  `needs-silkscreen/bench-verification`),
- resolve the systemic Core abstract-bus mismatch enumerated in
  [`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3 (archived)](../archive-index.md).

## See also

- The former standalone HW-PINMAP-311 reconciliation audit
  (`docs/hardware/s360-311-r4-pwm.md`) was merged into this document
  under DOCS-DISPOSITION-001 Step 4; the operator bench records are
  carried above, and the original (including the dated
  HW-PINMAP-311-FOLLOWUP audit log) is indexed by SHA in
  [`docs/archive-index.md`](../archive-index.md).
- [`docs/hardware/s360-100-core-connector-pin-map.md`](s360-100-core-connector-pin-map.md)
  — canonical Core-to-module connector pin map
  (S360-100-CONNECTOR-PINMAP-001); §J6 12 V PWM fan connector (13-pin).
- [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json)
  — reserves `FanPWM` as a `canonical_modules` token (line 12), subject
  to the fan-driver `max-one-of` rule enforced by `FAN_DRIVER_TOKENS` in
  [`tests/validate_webflash_builds.py`](../../tests/validate_webflash_builds.py).
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
- [`docs/release-one-hardware-audit.md` (archived)](../archive-index.md)
  — Required follow-ups #2 / #3, the owner (`CORE-ABSTRACT-BUS-001`) of the
  systemic Core abstract-bus rebind this reference defers question #1 to.
- [`docs/hardware/board-readiness-matrix.md` (archived)](../archive-index.md)
  — per-board readiness; the `S360-311` row (classification unchanged by
  this PR).
- [Hardware Artifact Policy (HW-ASSETS-001) (archived)](../archive-index.md)
  — the retained-but-not-committed policy this reference respects.
- [`docs/cleanup-audit.md` (archived)](../archive-index.md) — CLEANUP-001
  classification; carries the HW-PINMAP-311 / HW-PINMAP-311-FOLLOWUP
  registration rows and the explicit do-not list this PR honours.

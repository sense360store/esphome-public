# S360-311 Module-Side Pinmap (MODULE-PINMAPS-GDRIVE-001)

## Status

**Status: documentation-only schematic-backed module-side pinmap.
`S360-311` stays `cataloged_unverified`; FanPWM stays out of
release; no tach / pulse-counter line is mapped through the
SX1509 expander.** Companion to the canonical Core-side
[`s360-100-core-connector-pin-map.md`](s360-100-core-connector-pin-map.md)
(S360-100-CONNECTOR-PINMAP-001) and to the canonical FanPWM
native-GPIO map
[`s360-100-native-fan-gpio-map.md`](s360-100-native-fan-gpio-map.md)
(S360-100-NATIVE-FAN-GPIO-MAP-001). This document records the
**module-side** view of the Sense360 PWM (`S360-311`) board and
reconciles every per-fan PWM-drive (`TachPMW1..4`), per-fan
tach / pulse-counter (`Pul_Cou1..4`), shared tach passthrough
(`TachIO`), and Nextion UART line back to the mating Core
connector `J6`.

It is **documentation only**. It does **not**:

- publish firmware, create release artifacts, or promote any
  release target;
- promote `S360-311` `schematic_status` in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  beyond its current `cataloged_unverified` value;
- promote `FanPWM` to release; the `FanPWM` token does not appear
  in [`config/webflash-builds.json`](../../config/webflash-builds.json);
  FanPWM products keep `webflash_build_matrix: false`,
  no `artifact_name`, `rpm_supported: false`;
- claim measured PWM polarity, current, thermal envelope, RPM,
  or tach validation;
- re-bind any firmware YAML against the native ESP32-S3 GPIO map
  (the FanPWM YAML
  [`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml)
  and
  [`packages/expansions/fan_pwm_sx1509.yaml`](../../packages/expansions/fan_pwm_sx1509.yaml)
  remain `legacy / superseded` under
  S360-100-NATIVE-FAN-GPIO-MAP-001);
- fabricate connector type, pin order, signal mapping, or ESP32
  GPIO allocation. Values not proven by the committed module-side
  schematic PDF or the canonical Core schematic carry **TBD** or
  **needs silkscreen confirmation**.

## Native ESP32-S3 GPIO architectural rule (explicit FanPWM / tach reconciliation)

Per the canonical refreshed `S360-100-R4` schematic and per the
architectural rule recorded in
[`s360-100-native-tach-pulse-strategy.md`](s360-100-native-tach-pulse-strategy.md)
(S360-100-NATIVE-TACH-PULSE-001):

| Net | Native ESP32-S3 GPIO | Role |
|---|---|---|
| `TachIO` | `IO16` | Shared tach passthrough — drains tied to per-fan low-side MOSFET drain on the module |
| `Pul_Cou1` | `IO17` | Per-fan tach feedback channel 1 |
| `Pul_Cou2` | `IO18` | Per-fan tach feedback channel 2 |
| `Pul_Cou3` | `IO46` | Per-fan tach feedback channel 3 |
| `Pul_Cou4` | `IO9` | Per-fan tach feedback channel 4 |
| `TachPMW1` | `IO10` | FanPWM control channel 1 (`Q1` gate) |
| `TachPMW2` | `IO11` | FanPWM control channel 2 (`Q2` gate) |
| `TachPMW3` | `IO12` | FanPWM control channel 3 (`Q3` gate) |
| `TachPMW4` | `IO39` | FanPWM control channel 4 (`Q4` gate) |

**Tach / pulse-counter inputs MUST terminate on native ESP32-S3
GPIO.** No row in this document maps `TachIO` / `Pul_Cou1..4` /
any other pulse-counter signal through an SX1509 or other I/O
expander. The SX1509 (`U3`) is **removed from the S360-100 fan
signal path** by the refreshed canonical schematic; the historical
SX1509-routed FanPWM firmware path is `legacy / superseded` per
S360-100-NATIVE-FAN-GPIO-MAP-001 and is **not** revived by this
pinmap. The `PWM-SX1509-TACH-PROOF-001` compile/config proof
([`tests/test_sx1509_tach_pulse_counter_proof.py`](../../tests/test_sx1509_tach_pulse_counter_proof.py))
remains the authoritative evidence that an SX1509 pin cannot back
an ESPHome `pulse_counter`; the proof fixture / test stay in
place.

## Board identity

| Field | Value |
|---|---|
| Friendly name | Sense360 PWM |
| SKU | `S360-311` |
| Rev | R4 |
| Mating Core connector | `J6` (13-pin "12 V PWM fan connector") on `S360-100-R4` |
| Module-side connector | `J3` (13-pin "From Core") on `S360-311-R4` |
| Module-side fan-output connectors | `J1`, `J2`, `J4`, `J5` — 4-pin each (`+12V` / `GND` / `Pul_Cou*` / `TachPMW*`) |
| Module-side display connector | `J6` (4-pin "NEXTION DISPLAY") |
| Companion audit doc | [`s360-311-r4-pwm.md`](s360-311-r4-pwm.md) |

## Google Drive source evidence

The canonical Google Drive hardware folder for this board is
`PCB 2026 Sense360_r4 / PCB Project Files / Sense360 (Celling) / S360-311-R4`,
organized under per-type subfolders (`sch_pdf` / `bom` / `cpl` /
`gerbers` / `step_file` / `images` / `Assets`).

| Drive item | Type | Notes |
|---|---|---|
| `S360-311-R4 / sch_pdf / S360-311-R4.pdf` | Schematic PDF | Module-side schematic. Byte-identical copy committed in-repo at [`schematics/S360-311-R4.pdf`](schematics/S360-311-R4.pdf). |
| `S360-311-R4 / bom / S360-311-R4_BOM.xlsx` | BOM (.xlsx) | Retained-but-not-committed per [`hardware-artifact-policy.md` (archived)](../archive-index.md). |
| `S360-311-R4 / cpl` | Pick-and-place | Retained-but-not-committed. |
| `S360-311-R4 / gerbers` | Gerbers | Retained-but-not-committed. |
| `S360-311-R4 / step_file` | 3D STEP | Retained-but-not-committed. |
| `S360-311-R4 / images` | Renders / photos | Retained-but-not-committed. |
| `S360-311-R4 / Assets` | Misc. | Retained-but-not-committed. |

## Evidence status

| Artifact class | Evidence available | Status |
|---|---|---|
| Module-side schematic PDF | [`schematics/S360-311-R4.pdf`](schematics/S360-311-R4.pdf) (committed; SHA256 + size recorded in [`artifacts/S360-311-R4.md`](artifacts/S360-311-R4.md)) | schematic-backed |
| KiCad source | Not committed in-repo | TBD |
| Gerber / drill files | Drive `gerbers` (retained-but-not-committed) | TBD |
| 3D render / STEP | Drive `step_file` (retained-but-not-committed) | TBD |
| Board photographs | Drive `images` (retained-but-not-committed) | TBD |
| BOM | Drive `bom / S360-311-R4_BOM.xlsx` (retained-but-not-committed) | partial |
| Silkscreen / bench evidence | None committed; `PWM-12` per [`docs/blocker-burndown.md` (archived)](../archive-index.md) stays NEEDS BENCH | TBD |

## Mating Core connector

| Element | Value |
|---|---|
| Core connector ref | `J6` |
| Core connector type | TBD (13-pin header; type not annotated on the visible Core sheet) |
| Pin count | 13 |
| Pin-1 orientation | TBD — needs silkscreen confirmation |
| Module-side connector ref | `J3` (`S360-311-R4`) |
| Module-side 1-to-13 pin order | Schematic-confirmed against the committed module PDF per [`s360-311-r4-pwm.md` § Schematic summary](s360-311-r4-pwm.md#schematic-summary) |

## Module-side pinmap (`J3` ↔ Core `J6`)

The Core-side master table for `J6` is in
[`s360-100-core-connector-pin-map.md` § J6 — 12 V PWM fan connector (13-pin)](s360-100-core-connector-pin-map.md#j6--12-v-pwm-fan-connector-13-pin).
The module-side capture is taken from
[`s360-311-r4-pwm.md` § Module-side `J3` ↔ Core-side `J6`](s360-311-r4-pwm.md#module-side-j3--core-side-j6-13-pin-harness).
The pin-number column follows the **module-side** 1-to-13 order
(schematic-confirmed) so Core-side and module-side rows can be
lined up.

| Pin number | Module-side signal | Core net | ESP32 GPIO | Module-side signal type | Voltage / domain | Status |
|---|---|---|---|---|---|---|
| 1 | `+5V` input to MT3608 boost → +12V fan rail | `+5V` | N/A | power | `+5V` | needs silkscreen confirmation |
| 2 | Shared tach passthrough — drains tied to the per-fan low-side MOSFET drain on the module | `TachIO` | `IO16` | digital input (interrupt-capable) | `Logic 3.3V (ESP32-S3)` | schematic-backed |
| 3 | FanPWM control channel 1 — `Q1` gate (1 kΩ gate resistor `R1`) | `TachPMW1` | `IO10` | PWM output (native) | `Logic 3.3V (ESP32-S3)` | schematic-backed |
| 4 | Per-fan tach feedback channel 1 (from fan `J1` tach line) | `Pul_Cou1` | `IO17` | digital input (interrupt-capable) | `Logic 3.3V (ESP32-S3)` | schematic-backed |
| 5 | FanPWM control channel 2 — `Q2` gate (1 kΩ gate resistor `R2`) | `TachPMW2` | `IO11` | PWM output (native) | `Logic 3.3V (ESP32-S3)` | schematic-backed |
| 6 | Per-fan tach feedback channel 2 (from fan `J2` tach line) | `Pul_Cou2` | `IO18` | digital input (interrupt-capable) | `Logic 3.3V (ESP32-S3)` | schematic-backed |
| 7 | FanPWM control channel 3 — `Q3` gate (1 kΩ gate resistor `R6`) | `TachPMW3` | `IO12` | PWM output (native) | `Logic 3.3V (ESP32-S3)` | schematic-backed |
| 8 | Per-fan tach feedback channel 3 (from fan `J4` tach line) | `Pul_Cou3` | `IO46` | digital input (interrupt-capable) | `Logic 3.3V (ESP32-S3)` | schematic-backed |
| 9 | FanPWM control channel 4 — `Q4` gate (1 kΩ gate resistor `R7`) | `TachPMW4` | `IO39` | PWM output (native) | `Logic 3.3V (ESP32-S3)` | schematic-backed |
| 10 | Per-fan tach feedback channel 4 (from fan `J5` tach line) | `Pul_Cou4` | `IO9` | digital input (interrupt-capable) | `Logic 3.3V (ESP32-S3)` | schematic-backed |
| 11 | Module-side route from `J3` pin 11 to the on-board Nextion display connector `J6` (module side) | `UART_RX` (module-side label) | TBD on the Core side — see [Open questions](#open-questions--verification-needed) #1 | UART | `Logic 3.3V (ESP32-S3)` | TBD |
| 12 | Module-side route from `J3` pin 12 to the on-board Nextion display connector `J6` (module side) | `UART_TX` (module-side label) | TBD on the Core side — see [Open questions](#open-questions--verification-needed) #1 | UART | `Logic 3.3V (ESP32-S3)` | TBD |
| 13 | Shared ground | `GND` | N/A | ground | `GND` | needs silkscreen confirmation |

> **Native GPIO requirement satisfied on the schematic side.**
> Every tach / pulse-counter / PWM-drive net on this connector
> terminates at a native ESP32-S3 GPIO on the canonical R4
> schematic. No row above maps `TachIO` / `Pul_Cou1..4` through
> the SX1509 (`U3`) I/O expander — the SX1509 is removed from
> the S360-100 fan signal path per
> [`s360-100-native-fan-gpio-map.md`](s360-100-native-fan-gpio-map.md).

## Module-side fan-output connectors (4-pin × 4)

Each of `J1`, `J2`, `J4`, `J5` is a 4-pin fan-output connector
carrying `+12V`, `GND`, `Pul_Cou*`, `TachPMW*`. The per-fan-output
drive topology (low-side N-channel MOSFET on the `TachPMW*` gate
path with a 1 kΩ gate resistor; drain to shared `TachIO` net;
source to `GND`) is recorded in
[`s360-311-r4-pwm.md` § Per-fan-output drive topology](s360-311-r4-pwm.md#per-fan-output-drive-topology-module-side).
Per-fan rated current, the MOSFET part number's actual ratings
(symbol is `Q_NMOS_GSD`), and any thermal characterisation are
**TBD**.

| Fan output | Module connector | `TachPMW*` channel (Core net) | `Pul_Cou*` channel (Core net) | Status |
|---|---|---|---|---|
| Fan 1 | `J1` (module side) | `TachPMW1` (Core net) | `Pul_Cou1` (Core net) | schematic-backed |
| Fan 2 | `J2` (module side) | `TachPMW2` (Core net) | `Pul_Cou2` (Core net) | schematic-backed |
| Fan 3 | `J4` (module side) | `TachPMW3` (Core net) | `Pul_Cou3` (Core net) | schematic-backed |
| Fan 4 | `J5` (module side) | `TachPMW4` (Core net) | `Pul_Cou4` (Core net) | schematic-backed |

## Open questions / verification needed

1. **`J6` Core-side pins 11 / 12 — UART or unconnected?** The
   module-side `J3` schematic prints `UART_RX` / `UART_TX` on
   pins 11 / 12 and routes them on-board to the Nextion display
   connector `J6` (module side). The Core-side `J6` capture in
   [`s360-100-r4-core.md` § J6](s360-100-r4-core.md#j6--12-v-pwm-fan-connector-13-pin)
   currently lists only the 11 power / GND / fan-signal nets and
   does not record UART pins. Either the Core capture is
   incomplete (UART pair is on Core `J6` pins 11 / 12) or the
   Nextion UART is delivered via a separate harness. See
   [`s360-100-core-connector-pin-map.md` Open Questions](s360-100-core-connector-pin-map.md#open-questions--verification-needed)
   #2.
2. **Silkscreen pin-1 orientation on Core `J6` and module `J3`.**
   The module-side 1-to-13 order is schematic-confirmed; the
   Core-side 1-to-13 silkscreen order is `verify` per
   [`s360-100-r4-core.md` Open Question #9](s360-100-r4-core.md#open-questions--verification-needed).
3. **`Q_NMOS_GSD` actual part number / ratings.** The schematic
   symbol carries no part number; per-fan current, MOSFET
   ratings, and thermal characterisation are TBD.
4. **`"NINE 4pin FANs"` section title vs four populated fan
   outputs.** The schematic sheet's fan-section title reads
   `"NINE 4pin FANs"` but only four 4-pin fan output connectors
   are visible. Stale label / project code / undelivered intent
   is **unresolved** per
   [`s360-311-r4-pwm.md` § Open documentation questions](s360-311-r4-pwm.md#open-documentation-questions).
5. **Bench / harness / waveform evidence.** `PWM-12` per
   [`docs/blocker-burndown.md` (archived)](../archive-index.md) stays
   NEEDS BENCH; no RPM / tach / PWM polarity / current / thermal
   measurement is in scope here.

## Cross references

- [`s360-100-core-connector-pin-map.md`](s360-100-core-connector-pin-map.md) — canonical Core-to-module connector pin map (S360-100-CONNECTOR-PINMAP-001).
- [`s360-100-r4-core.md`](s360-100-r4-core.md) — Core per-pin / per-net reference.
- [`s360-100-native-fan-gpio-map.md`](s360-100-native-fan-gpio-map.md) — canonical FanPWM control + tach native ESP32-S3 GPIO map (S360-100-NATIVE-FAN-GPIO-MAP-001).
- [`s360-100-native-tach-pulse-strategy.md`](s360-100-native-tach-pulse-strategy.md) — architectural rule for tach / pulse-counter native ESP32-S3 GPIO.
- [`s360-311-r4-pwm.md`](s360-311-r4-pwm.md) — PWM board-side audit (HW-PINMAP-311).
- [`artifacts/S360-311-R4.md`](artifacts/S360-311-R4.md) — curated artifact index (HW-ASSETS-003).
- [`schematics/S360-311-R4.pdf`](schematics/S360-311-R4.pdf) — committed module-side schematic PDF.
- [`docs/blocker-burndown.md` (archived)](../archive-index.md) — blocker / scope-classification table (PWM-12).

## Do-not-change guardrails

This document does **not**:

- promote `S360-311` `schematic_status` beyond `cataloged_unverified`;
- promote `FanPWM` to release;
- add a `FanPWM` token to
  [`config/webflash-builds.json`](../../config/webflash-builds.json);
- flip any FanPWM `webflash_build_matrix`, add an
  `artifact_name`, or add a WebFlash wrapper;
- claim measured PWM polarity, current, thermal envelope, RPM,
  or tach validation;
- re-bind any firmware YAML against the native ESP32-S3 GPIO map;
- weaken the historical SX1509 + `pulse_counter` compile/config
  proof fixture
  [`tests/esphome/sx1509_pulse_counter_proof.yaml`](../../tests/esphome/sx1509_pulse_counter_proof.yaml)
  or guard
  [`tests/test_sx1509_tach_pulse_counter_proof.py`](../../tests/test_sx1509_tach_pulse_counter_proof.py);
- fabricate connector type, pin order, or signal assignment;
- map any tach / pulse-counter signal through an expander.

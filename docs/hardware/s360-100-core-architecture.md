# S360-100 Core Architecture (S360-100-NATIVE-TACH-PULSE-001 — R4 Refresh)

## Status

**Status: documentation-only architectural clarification + evidence
refresh.** This document promotes the newly delivered
[`S360-100-R4.pdf`](schematics/S360-100-R4.pdf) (SHA256
`4c9e8b06d129fbb55f61e143b648e03762d06cb4dc67fe3120c268cd3a4bdf16`,
837,443 bytes, KiCad E.D.A. 10.0.3, single sheet `1/1`) as the
**current canonical S360-100 Core schematic evidence source**, and
formally records:

1. The Sense360 Core (`S360-100`) is the **central Core / backplane
   controller** of the Sense360 module stack.
2. The Core MCU is the **ESP32-S3-WROOM-1-N16R8** (16 MB flash,
   8 MB octal-SPI PSRAM), reference designator **U6**.
3. Each per-module connector is dedicated to one specific Sense360
   module SKU, with the signal family carried by that connector
   captured from the new R4 schematic (see
   [§ Connector / module matrix](#connector--module-matrix) below).
4. The architectural rule that **tach / pulse-counter signals MUST
   terminate on native ESP32-S3 GPIO** is restated and, on the
   schematic side, is now visibly satisfied by the new R4 sheet
   (see [§ Native ESP32-S3 GPIO termination for tach /
   pulse counter](#native-esp32-s3-gpio-termination-for-tach--pulse-counter)
   below).

It is **documentation only**. It does not:

- publish firmware, create release artifacts, change
  [`firmware/sources.json`](../../firmware/sources.json), change
  [`manifest.json`](../../manifest.json), or promote any release
  target;
- promote Sense360 LED from `preview` to `stable`;
- promote `FanRelay` / `FanPWM` / `FanDAC` to release;
- claim measured RPM / tach / pulse-counter operation on any board;
- claim final firmware GPIO allocation beyond what the new R4
  schematic itself prints;
- claim the `S360-410` PoE PSU blocker is solved;
- claim fan WebFlash / release readiness;
- fabricate any hardware verification evidence (no bench session,
  scope trace, continuity measurement, or operator-attributed
  observation is invented here).

The current canonical homes for tach / pulse-counter architecture and
for the Core schematic remain
[`docs/hardware/s360-100-native-tach-pulse-strategy.md`](s360-100-native-tach-pulse-strategy.md)
and [`docs/hardware/s360-100-r4-core.md`](s360-100-r4-core.md). This
document is the **architectural index** that ties the new R4
schematic to those records and to the bundle / release layer.

## Core identity

| Field | Value |
|---|---|
| Friendly name | Sense360 Core |
| Role | Central Core / backplane controller; carries the MCU and every per-module connector |
| Board SKU | `S360-100` |
| Revision | `R4` |
| MCU | `ESP32-S3-WROOM-1-N16R8` (reference designator `U6`) |
| Power inlet (PoE path) | `J2` `PoE_ACDC`, fed by the off-board `S360-410` Sense360 PoE PSU |
| Power inlet (USB path) | `J8` USB-C 2.0 receptacle (`VBUS` → ideal-diode-OR with `PoE_ACDC` into `+5V`) |
| Buck converter | `U1` `RT8059GJ5`, 5 V → 3.3 V (`L1` 2.2 µH, `R5` / `R6` feedback) |
| LED data buffer | `U2` `74LVC1G07SE-7` open-drain buffer / level shifter (`LED_DATA` → `LED_DATA_3V3`) |
| USB power-path switch | `Q2` `Si2319CDS` p-channel MOSFET |
| Canonical schematic | [`docs/hardware/schematics/S360-100-R4.pdf`](schematics/S360-100-R4.pdf) (SHA256 `4c9e8b06d129fbb55f61e143b648e03762d06cb4dc67fe3120c268cd3a4bdf16`) |
| `schematic_status` (catalog) | `verified` — unchanged by this document |

This row mirrors the entries in
[`docs/hardware-catalog.md`](../hardware-catalog.md) and
[`config/hardware-catalog.json`](../../config/hardware-catalog.json).
The catalog `schematic_status: verified` value for `S360-100` is **not
changed** by this PR — the new R4 PDF is the same revision identifier
as the prior committed PDF, only the underlying schematic content has
been refreshed.

## Core is the central hub

The new R4 schematic confirms that `S360-100` is the **central Core /
backplane controller** of the Sense360 module stack. Every Sense360
module — RoomIQ (`S360-200`), AirIQ (`S360-210`), VentIQ (`S360-211`),
LED (`S360-300`), Relay (`S360-310`), PWM (`S360-311`), DAC
(`S360-312`), TRIAC (`S360-320`) — and the off-board PoE PSU
(`S360-410`) attach through a dedicated connector on the Core. Module
boards do not interconnect directly; every signal flows through the
Core.

A **room bundle** (see
[`docs/sense360-room-bundles.md`](../sense360-room-bundles.md), the
canonical PoE room bundle SKU matrix) is therefore always:

- **S360-100 Core**, *plus*
- one or more **room modules** (RoomIQ / AirIQ / VentIQ / LED / Relay /
  PWM / DAC / TRIAC), *plus*
- **S360-410 PoE PSU** (or the USB-C path for non-PoE bench builds).

No bundle is built by combining module boards without the Core — the
Core is the only board that carries the MCU and the only board that
can address the module connectors.

## Connector / module matrix

The table below maps each Sense360 Core connector on the new R4
schematic to its dedicated module SKU, the signal family the
connector carries, the intended use, and the native-MCU constraint
(if any). Every row is taken from the
[committed `S360-100-R4.pdf`](schematics/S360-100-R4.pdf) and is
captioned with the schematic's "*Formerly used as …*" legacy label
where one exists, because the R4 KiCad sheet still carries the
legacy module-name annotations next to the connectors.

| Core connector | Pin count | Attached module SKU | Friendly name | Signal family | Intended use | Native MCU requirement? | Notes / caveats |
|---|---:|---|---|---|---|---|---|
| `J1` | 5 | `S360-211` | Sense360 VentIQ | `+5V`, `+3.3V`, `I2C_SCL`, `I2C_SDA`, `GND` | Bathroom ventilation IQ module (humidity / fan trigger logic) | I²C bus must originate at the ESP32-S3 (`IO48` / `IO45`). | Schematic legacy label: *"Formerly used as AirIQ Bathroom Module connector"*. |
| `J2` | 2 | `S360-410` | Sense360 PoE PSU | `PoE_ACDC`, `GND` | Off-board PoE PSU power inlet (DC output from `S360-410` AC/DC) | None (power inlet). | `S360-410` blocker chain is **not** resolved by this document — see [`docs/blocker-burndown.md` § 1B](../blocker-burndown.md) and [`docs/package-poe-410-001-audit.md`](../package-poe-410-001-audit.md). |
| `J3` | 3 | `S360-300` | Sense360 LED | `+3.3V`, `GND`, `LED_DATA_3V3` | WS2812B LED ring data | `LED_DATA` source must originate at native ESP32 `IO38` (then through `U2` `74LVC1G07SE-7` open-drain buffer and `R8` 330 Ω series). | LED stays `preview` (`Ceiling-POE-VentIQ-RoomIQ-LED`); this PR does not promote it. |
| `J4` | 3 | `S360-310` | Sense360 Relay | `+5V`, `Relay`, `GND` | Relay drive | `Relay` drive line must originate at native ESP32 `IO3`. | Schematic legacy label: *"Formerly was Relay Module connector"*. |
| `J6` | 13 | `S360-311` | Sense360 PWM (12 V PWM fan) | `+5V`, `GND`, `TachIO`, `TachPMW1..4`, `Pul_Cou1..4`, `UART_RX`, `UART_TX` | Up to four 12 V PWM-driven fans with per-fan tach lines plus the shared `TachIO` passthrough | **Yes** — `TachIO` and `Pul_Cou1..4` must terminate on native ESP32-S3 GPIO; `TachPMW1..4` are PWM-drive outputs from native ESP32-S3 GPIO. See [§ Pin allocation table — native ESP32-S3 GPIO termination](#pin-allocation-table--native-esp32-s3-gpio-termination). | Schematic legacy label: *"Formerly used as 12v PWM Fan connector"*. |
| `J7` | 6 | `S360-312` | Sense360 DAC | `+5V`, `I2C_SDA`, `I2C_SCL`, `UART_RX`, `UART_TX`, `GND` | GP8403 DAC fan-controller driver (I²C + UART) | I²C must originate at the ESP32-S3 (`IO48` / `IO45`); UART must originate at `TXD0` / `RXD0`. | Schematic legacy label: *"Formerly used as GP8403 Fan connector"*. |
| `J8` | — | — | (USB-C 2.0 receptacle) | `VBUS`, `D+` / `D-`, `CC1` / `CC2`, `SBU1` / `SBU2`, `SHIELD` / `GND` | USB-C power + ESP32-S3 USB data (bench flashing / serial) | `D+` / `D-` route to native ESP32-S3 `IO20` / `IO19`. | Not a module connector; included for completeness. |
| `J9` | 7 | `S360-210` | Sense360 AirIQ | `+5V`, `+3.3V`, `I2C_SDA`, `I2C_SCL`, `AirQ_Status_Led`, `AirQ_Led`, `GND` | Air-quality module (SPS30 / SGP41 / SCD41 / BMP390 stack on the AirIQ board) | I²C bus must originate at the ESP32-S3 (`IO48` / `IO45`); `AirQ_Status_Led` / `AirQ_Led` originate at ESP32-S3 `IO7` / `IO8`. | Schematic legacy label: *"Formerly used as AirIQ Module connector"*. |
| `J10` | 12 | `S360-200` | Sense360 RoomIQ | `+3.3V`, `+5V`, `SEN0609_RX`, `SEN0609_TX`, `out(gpio6)`, `Hi-Link_RX`, `Hi-Link_TX`, `PIR`, `ALS_INT`, `I2C_SDA`, `I2C_SCL`, `GND` | Presence / comfort module (mmWave radar, PIR, ALS) | All ESP32-side nets (`SEN0609_RX/TX`, `Hi-Link_RX/TX`, `PIR`, `ALS_INT`, `I2C_SDA/SCL`, `out(gpio6)`) originate at native ESP32-S3 GPIO. | Schematic legacy label: *"Formerly used as Presence Comfort Module Connector"*. |
| `J13` | 2 | — | (Generic on-board fan output) | `+5V` / `FAN`, `GND` *(verify silkscreen pin order)* | Single on-board PWM fan drive (`FAN` net) | `FAN` net originates at native ESP32-S3 `IO21`. | Two-pin JST `B2B-XH-A` header in the new R4 BOM; not associated with any Sense360 module SKU. |
| `J15` | 4 | `S360-320` | Sense360 TRIAC | `+3.3V`, `TRI_GPIO1`, `TRI_GPIO2`, `GND` | TRIAC fan-module gate / zero-cross control | `TRI_GPIO1` / `TRI_GPIO2` source ESP32 pins are recorded in the [`s360-100-r4-core.md` Open Questions](s360-100-r4-core.md#open-questions--verification-needed) and the [`docs/blocker-burndown.md` `HW-005`](../blocker-burndown.md) row; FanTRIAC `HW-005` remains **blocked** by this document. | Schematic legacy label: *"Formerly used as a TRIAC Fan Module connector"*. |

The Core also exposes `MTMS` (`TP10`), `MTDO` (`TP13`), and `MTCK`
test pads (no dedicated JTAG connector on the visible sheet), the
`SW3` boot button (`IO_0` strap), and the `SW4` reset button — none
of which are module connectors.

## Native ESP32-S3 GPIO termination for tach / pulse counter

The architectural rule recorded in
[`docs/hardware/s360-100-native-tach-pulse-strategy.md`](s360-100-native-tach-pulse-strategy.md)
(S360-100-NATIVE-TACH-PULSE-001) applies to every Sense360 Core
revision, every firmware package, every product, and every WebFlash
build:

1. **Tach / pulse-counter inputs MUST land on a native ESP32-S3
   GPIO.** Any `sensor: platform: pulse_counter` pin, any RPM input,
   any per-fan / aggregate tach line, and any "pulse counting" signal
   of any kind must terminate at an interrupt-capable native
   ESP32-S3 `InternalGPIOPin`.
2. **An I/O expander MUST NOT be used for tach / pulse-counter
   inputs.** An SX1509 (or any other I²C/SPI expander) pin is **not**
   an `InternalGPIOPin` and **cannot** back an ESPHome
   `pulse_counter` — this is compile-proven by
   [`PWM-SX1509-TACH-PROOF-001`](../../tests/test_sx1509_tach_pulse_counter_proof.py)
   (the captured `esphome config` rejection is `sensor.pulse_counter:
   pin: [sx1509] is an invalid option for [pin]`).
3. **PWM-drive output capability and tach-input capability are
   separate gates.** An expander LED-driver PWM engine **may** back
   PWM-drive **output** (`output: platform: sx1509`, channels 0..7),
   and that capability remains a separate architectural choice. It
   does **not** grant tach / pulse-counter input support.
4. **The expander may be used for suitable low-speed, non-tach
   signals only.** Polled `binary_sensor: platform: gpio` reads of an
   expander channel and similar low-speed expander-friendly signals
   remain supported. None of those constitute tach / pulse-counter /
   RPM support.

## Pin allocation table — native ESP32-S3 GPIO termination

The new R4 schematic prints the per-fan tach / pulse-counter / PWM
nets directly on ESP32-S3 module pins (with the ESP32-S3 module pin
numbers shown to the right of each net). The table below records the
**schematic-printed** native-GPIO terminations from the new
[`S360-100-R4.pdf`](schematics/S360-100-R4.pdf) sheet. None of these
GPIO terminations is **bench-verified** by this PR — the
[`docs/hardware/s360-311-r4-pwm.md`](s360-311-r4-pwm.md)
`schematic-evidence-pending` and `bench-evidence-pending` gates stay
exactly as they were; firmware status and `rpm_supported` stay
exactly as they were.

| Tach / pulse-counter / PWM-drive net | Schematic-printed ESP32-S3 GPIO | Required pin family | Schematic-printed → rule-compliant? | Bench-verified? |
|---|---|---|---|---|
| `TachIO` (shared 12 V PWM fan tach passthrough) | `IO16` (ESP32-S3 module pin 9) | Native ESP32-S3 GPIO (interrupt-capable) | **Yes** (native pin) | **No** — not bench-verified |
| `Pul_Cou1` (per-fan tach, channel 1) | `IO17` (ESP32-S3 module pin 10) | Native ESP32-S3 GPIO (interrupt-capable) | **Yes** (native pin) | **No** — not bench-verified |
| `Pul_Cou2` (per-fan tach, channel 2) | `IO18` (ESP32-S3 module pin 11) | Native ESP32-S3 GPIO (interrupt-capable) | **Yes** (native pin) | **No** — not bench-verified |
| `Pul_Cou3` (per-fan tach, channel 3) | `IO46` (ESP32-S3 module pin 16) | Native ESP32-S3 GPIO (interrupt-capable) | **Yes** (native pin) | **No** — not bench-verified |
| `Pul_Cou4` (per-fan tach, channel 4) | `IO9` (ESP32-S3 module pin 17) | Native ESP32-S3 GPIO (interrupt-capable) | **Yes** (native pin) | **No** — not bench-verified |
| `TachPMW1` (per-fan PWM-drive output, channel 1) | `IO10` (ESP32-S3 module pin 18) | Native ESP32-S3 GPIO (PWM-capable) | **Yes** (native pin) | **No** — not bench-verified |
| `TachPMW2` (per-fan PWM-drive output, channel 2) | `IO11` (ESP32-S3 module pin 19) | Native ESP32-S3 GPIO (PWM-capable) | **Yes** (native pin) | **No** — not bench-verified |
| `TachPMW3` (per-fan PWM-drive output, channel 3) | `IO12` (ESP32-S3 module pin 20) | Native ESP32-S3 GPIO (PWM-capable) | **Yes** (native pin) | **No** — not bench-verified |
| `TachPMW4` (per-fan PWM-drive output, channel 4) | `IO39` (ESP32-S3 module pin 32) | Native ESP32-S3 GPIO (PWM-capable) | **Yes** (native pin) | **No** — not bench-verified |

### Reconciliation against the prior `S360-100-R4` schematic

The **prior** committed `S360-100-R4.pdf` snapshot routed the
per-fan `TachPMW1..4` / `Pul_Cou1..4` lines through the SX1509 (`U3`)
I/O expander, and that routing was the basis for the pending /
forbidden classification in
[`docs/hardware/s360-100-native-tach-pulse-strategy.md`](s360-100-native-tach-pulse-strategy.md)
(`Pul_Cou1..4` rows marked **"TBD — pending hardware revision /
harness"**). The **new** R4 PDF terminates every tach / pulse-counter /
PWM-drive net directly at a native ESP32-S3 GPIO — the schematic
side of the architectural rule is now satisfied. **The bench /
firmware sides are not.** This PR records the schematic refresh and
does **not**:

- bind `Pul_Cou1..4` as `sensor: platform: pulse_counter` in any
  `packages/**` or `products/**` YAML;
- flip `rpm_supported: false` on any FanPWM product;
- add a WebFlash build for FanPWM;
- promote `S360-311` `schematic_status` to anything stronger.

Per-fan RPM / measured-tach claims require the separate
`S360-311-CURRENT-THERMAL-001` / `COMPONENT-NATIVE-TACH-001` work
and bench evidence under
[`docs/hardware/s360-311-r4-pwm.md`](s360-311-r4-pwm.md).

## Bundle SKU ≠ firmware config string ≠ board SKU

The Sense360 architecture deliberately separates four identifier
spaces (see also [`docs/sense360-room-bundles.md` §
Identifier separation](../sense360-room-bundles.md)):

| Identifier space | Example | Source of truth |
|---|---|---|
| Board SKU | `S360-100`, `S360-200`, `S360-210`, `S360-211`, `S360-300`, `S360-310`, `S360-311`, `S360-312`, `S360-320`, `S360-410` | [`config/hardware-catalog.json`](../../config/hardware-catalog.json) |
| Firmware config string | `Ceiling-POE-VentIQ-RoomIQ`, `Ceiling-POE-VentIQ-RoomIQ-LED` | [`config/firmware-combination-matrix.json`](../../config/firmware-combination-matrix.json) |
| Release artifact name | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` | [`config/webflash-builds.json`](../../config/webflash-builds.json) |
| Room bundle SKU | `S360-KIT-BATH-P`, `S360-KIT-KITCHEN-P`, `S360-KIT-LIVING-P`, `S360-KIT-BEDROOM-P`, `S360-KIT-CORRIDOR-P` | [`config/room-bundle-skus.json`](../../config/room-bundle-skus.json) |

Firmware targets are built around **S360-100 Core plus room
modules**. The Release-One stable target
(`Ceiling-POE-VentIQ-RoomIQ` /
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`) is the
bathroom-bundle firmware: Core + RoomIQ + VentIQ + PoE PSU. Other
bundles still need their own promotion path through
[`docs/stable-target-expansion-plan.md`](../stable-target-expansion-plan.md)
and the per-bundle stable-target follow-up PRs.

| Room bundle | Included boards | Firmware config string | Current release class |
|---|---|---|---|
| Bathroom (`S360-KIT-BATH-P`) | `S360-100` Core + `S360-200` RoomIQ + `S360-211` VentIQ + `S360-410` PoE PSU | `Ceiling-POE-VentIQ-RoomIQ` | **`stable-release`** (Release-One) |
| Kitchen (`S360-KIT-KITCHEN-P`) | `S360-100` Core + `S360-200` RoomIQ + `S360-210` AirIQ + `S360-410` PoE PSU | `Ceiling-POE-AirIQ-RoomIQ` | `stable-candidate` (gated on AirIQ stack + PoE-410) |
| Living (`S360-KIT-LIVING-P`) | `S360-100` Core + `S360-200` RoomIQ + `S360-300` LED + `S360-410` PoE PSU | `Ceiling-POE-RoomIQ-LED` (or equivalent) | `preview-candidate` (LED stays `preview`) |
| Bedroom (`S360-KIT-BEDROOM-P`) | `S360-100` Core + `S360-200` RoomIQ + `S360-410` PoE PSU | `Ceiling-POE-RoomIQ` | `stable-candidate` (gated on PoE-410 chain) |
| Corridor (`S360-KIT-CORRIDOR-P`) | `S360-100` Core + `S360-200` RoomIQ + `S360-300` LED + `S360-410` PoE PSU | `Ceiling-POE-RoomIQ-LED` (or equivalent) | `preview-candidate` (shares Living's board set) |

This table is the architectural framing only. Per-bundle stable-
promotion gates are owned by
[`docs/sense360-room-bundles.md`](../sense360-room-bundles.md) and
[`docs/stable-target-expansion-plan.md`](../stable-target-expansion-plan.md);
this PR does **not** promote any of the candidate rows.

## Caveats preserved by this PR

Schematic evidence is one axis. Several caveats from earlier audits
are **explicitly preserved** by this document:

- **Bench / manufacturing evidence is still pending** for the Core
  board. The
  [`docs/hardware/s360-100-r4-core.md` § S360-100-BENCH-001 status](s360-100-r4-core.md#s360-100-bench-001-status)
  record stays `pending — bench/manufacturing evidence required` —
  no operator, no observed board serial, no silkscreen photo, no
  scope trace, no continuity measurement has been supplied.
- **`S360-311` (Sense360 PWM) stays `cataloged_unverified`** — the
  S360-311 schematic PDF is **not** committed to this repo, and the
  PWM-drive-only `fan_pwm.yaml` package keeps `rpm_supported: false`.
  This PR does **not** flip any of those rows.
- **FanTRIAC `HW-005` stays blocked.** The `TRI_GPIO1` /
  `TRI_GPIO2` ESP32-side source pins on `J15` are not unambiguously
  pinned by the new R4 sheet either; the
  [`docs/hardware/s360-100-r4-core.md` Open Questions](s360-100-r4-core.md#open-questions--verification-needed)
  list remains in force.
- **`S360-410` PoE PSU stays `cataloged_unverified`.** The
  [`PACKAGE-POE-410-001`](../package-poe-410-001-audit.md) audit lane
  is unchanged.
- **Sense360 LED stays `preview`** and remains excluded from the
  Release-One firmware.
- **Release-One** stays `Ceiling-POE-VentIQ-RoomIQ`, version
  `1.0.0`, channel `stable`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`.

## Do-not-change guardrails (S360-100-NATIVE-TACH-PULSE-001 — R4 refresh)

This document and the tests added with it must not:

- publish firmware, create release artifacts, change
  [`firmware/sources.json`](../../firmware/sources.json), change
  [`manifest.json`](../../manifest.json), or promote any release
  target;
- change Release-One (`Ceiling-POE-VentIQ-RoomIQ` / stable /
  `v1.0.0`) or the LED preview entry
  (`Ceiling-POE-VentIQ-RoomIQ-LED` / preview);
- promote `S360-311` `schematic_status` (stays
  `cataloged_unverified`);
- flip `S360-311` `webflash_build_matrix`, add `artifact_name`,
  add a WebFlash wrapper, add a `config/webflash-builds.json` row,
  or claim WebFlash / release / import readiness;
- claim measured RPM / tach support — `rpm_supported: false`
  stays the posture;
- claim final per-fan `Pul_Cou1..4` / `TachPMW1..4` firmware GPIO
  bindings beyond what the new R4 schematic itself prints (no
  firmware YAML edit is performed);
- claim the FanTRIAC `HW-005` blocker is solved;
- claim the `S360-410` PoE PSU is `verified` (separate
  `PACKAGE-POE-410-001` lane);
- alter the SX1509 PWM-drive output path used by `fan_pwm.yaml` /
  `fan_pwm_sx1509.yaml` — the package layer continues to expose
  PWM-drive only, with no per-fan RPM, until a separate firmware PR
  re-binds it against this new R4 evidence.

## See also

- [`docs/hardware/s360-100-native-fan-gpio-map.md`](s360-100-native-fan-gpio-map.md)
  — canonical S360-100 / S360-311 fan GPIO map
  (S360-100-NATIVE-FAN-GPIO-MAP-001): records the native ESP32-S3
  GPIO termination of `TachPMW1..4` / `Pul_Cou1..4` / `TachIO`,
  classifies the SX1509-routed fan path as legacy / superseded, and
  carries the FanPWM firmware-binding pending status.
- [`docs/hardware/schematics/S360-100-R4.pdf`](schematics/S360-100-R4.pdf)
  — current canonical S360-100 Core schematic (SHA256
  `4c9e8b06d129fbb55f61e143b648e03762d06cb4dc67fe3120c268cd3a4bdf16`,
  837,443 bytes).
- [`docs/hardware/s360-100-r4-core.md`](s360-100-r4-core.md) —
  per-pin / per-connector / per-net Core reference (pre-existing).
- [`docs/hardware/s360-100-native-tach-pulse-strategy.md`](s360-100-native-tach-pulse-strategy.md)
  — canonical architectural rule (native ESP32-S3 GPIO termination
  for tach / pulse counter; compile/config proof; pending pin-
  allocation table).
- [`docs/hardware/artifacts/S360-100-R4.md`](artifacts/S360-100-R4.md)
  — curated artifact index (HW-ASSETS-002).
- [`docs/hardware/hardware-artifact-policy.md`](hardware-artifact-policy.md)
  — hardware source / manufacturing artifact policy
  (HW-ASSETS-001).
- [`docs/sense360-room-bundles.md`](../sense360-room-bundles.md) —
  canonical PoE room bundle SKU matrix (Core + room modules +
  PoE PSU).
- [`docs/stable-target-expansion-plan.md`](../stable-target-expansion-plan.md)
  — actionable expansion plan for non-Bathroom bundles.
- [`docs/hardware/s360-311-r4-pwm.md`](s360-311-r4-pwm.md) — FanPWM
  audit; PWM-drive-only scope and the SX1509 / `pulse_counter`
  compile-proof.
- [`tests/test_sx1509_tach_pulse_counter_proof.py`](../../tests/test_sx1509_tach_pulse_counter_proof.py)
  — compile/config proof of the SX1509 / `pulse_counter` rejection.
- [`tests/test_native_tach_pulse_pin_strategy.py`](../../tests/test_native_tach_pulse_pin_strategy.py)
  — guards for the architectural rule across `packages/**`,
  `products/**`, docs, and `config/*.json`.
- [`tests/test_s360_100_core_architecture.py`](../../tests/test_s360_100_core_architecture.py)
  — guards for this document (canonical schematic reference, Core
  hub framing, connector / module matrix, pending native-GPIO
  pin-allocation table, do-not-change guardrails).

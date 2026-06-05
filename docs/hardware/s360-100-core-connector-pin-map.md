# S360-100 Core-to-Module Connector Pin Map (S360-100-CONNECTOR-PINMAP-001)

## Status

**Status: documentation-only canonical Core connector pin map.** This
document is the **canonical S360-100 Core-to-module connector pin map**.
It records, for every per-module connector on the Sense360 Core
(`S360-100`), the connector reference, the connected module SKU, the
connector type / pin count / pin-1 orientation, the per-pin signal
mapping, the native ESP32-S3 GPIO (or `N/A` / `TBD`), the signal type,
the voltage / domain, and a per-row verification status
(`verified` / `schematic-backed` / `TBD` / `needs silkscreen
confirmation`).

It exists because the prior architecture and per-board hardware docs
each capture a slice of the Core-to-module connector layer
([`s360-100-r4-core.md`](s360-100-r4-core.md) for per-connector net
lists, [`s360-100-core-architecture.md`](s360-100-core-architecture.md)
for the connector / module SKU matrix,
[`s360-100-native-fan-gpio-map.md`](s360-100-native-fan-gpio-map.md)
for the FanPWM fan-path GPIO map, plus the per-module audit docs for
`S360-200` / `S360-210` / `S360-211` / `S360-300` / `S360-310` /
`S360-311` / `S360-312` / `S360-320` / `S360-410`) but **no single
document** in this repository sits one level up and lists every Core
connector with its module SKU + per-pin signal + ESP32-S3 GPIO + status
in one consolidated table. This is that document.

It is **documentation only**. It does **not**:

- publish firmware, create release artifacts, change
  [`firmware/sources.json`](../../firmware/sources.json), change
  [`manifest.json`](../../manifest.json), or promote any release
  target;
- promote Sense360 LED from `preview` to `stable`;
- promote `FanRelay` / `FanPWM` / `FanDAC` to release;
- claim measured RPM / tach / pulse-counter operation on any board
  or any per-fan firmware-binding;
- claim a final firmware GPIO allocation beyond what the canonical
  R4 schematic itself prints;
- claim the `S360-410` PoE PSU blocker is solved (`PACKAGE-POE-410-001`
  lane is unchanged);
- clear the FanTRIAC bench (`PACKAGE-TRIAC-001`) or mains-voltage
  compliance (`COMPLIANCE-001`) blockers, or promote FanTRIAC beyond
  `status: blocked` — the `J15` `HW-005` BUILDABILITY +
  `HW-PINMAP-320-FOLLOWUP` pin resolution recorded below is buildability
  only;
- claim WebFlash / release readiness for any module that is not
  already shipping in a Release-One artifact;
- fabricate connector types, pin orders, signal assignments, or GPIO
  allocations — every value below is either taken verbatim from the
  current canonical [`S360-100-R4.pdf`](schematics/S360-100-R4.pdf)
  schematic (SHA256
  `4c9e8b06d129fbb55f61e143b648e03762d06cb4dc67fe3120c268cd3a4bdf16`,
  837,443 bytes, KiCad E.D.A. 10.0.3, single sheet `1/1`) and the
  per-module audit docs, or explicitly marked **TBD** /
  **needs silkscreen confirmation**.

The canonical homes for the per-connector and per-net reference text
remain [`s360-100-r4-core.md`](s360-100-r4-core.md) (per-pin / per-net
Core reference) and [`s360-100-core-architecture.md`](s360-100-core-architecture.md)
(connector / module SKU matrix). This document is the **one-shot
canonical Core-to-module pin map** that sits on top of both and is
cross-referenced from the per-module audit docs.

## Status-language rules

Every row in the [connector matrix](#connector-matrix) and every row
in the [per-connector pin tables](#per-connector-pin-tables) below
carries one of the following status values. They are the only values
this document may use, and the rules below are the only way a row may
move between them:

- **`verified`** — net identity and connector role are proven both on
  the canonical R4 schematic **and** on the bench / silkscreen. No
  row in this document carries `verified` today — the Core-side
  silkscreen, harness, and bench evidence are tracked as
  `pending — bench/manufacturing evidence required` under
  [`s360-100-r4-core.md` § S360-100-BENCH-001 status](s360-100-r4-core.md#s360-100-bench-001-status).
- **`schematic-backed`** — the net, connector role, and (where
  applicable) ESP32-S3 GPIO assignment are taken verbatim from the
  current canonical [`S360-100-R4.pdf`](schematics/S360-100-R4.pdf)
  schematic. Bench / silkscreen verification is still owed; this is
  the dominant status of this document.
- **`TBD`** — the value is not proven by the current canonical
  schematic and is not yet recorded as `schematic-backed` here. The
  value must NOT be invented; the row must say `TBD` until evidence
  arrives.
- **`needs silkscreen confirmation`** — the net assignment / pin
  number is taken from the schematic but the **1-to-N pin order**
  on the physical connector is not yet visually confirmed against
  the Core-side silkscreen photograph (and, where applicable, the
  module-side silkscreen). The schematic side is recorded; the
  connector-pin-to-net assignment is pending. This is the standard
  status for multi-pin headers where the schematic prints the net
  list but the visible 1-to-N order is `verify` per
  [`s360-100-r4-core.md` Open Question #9](s360-100-r4-core.md#open-questions--verification-needed).

Anything stronger than `schematic-backed` requires evidence committed
to this repository per [`s360-100-r4-core.md` § Status-language rules](s360-100-r4-core.md#status-language-rules).

## Connector matrix

The table below lists every per-module connector on the Sense360
Core (`S360-100`). The connector ref, pin count, pin-1 orientation,
attached module SKU, and intended function come from the canonical
R4 schematic and the per-module audit docs cited in
[See also](#see-also). Pin-1 orientation values are **TBD** where
the schematic prints the net list but the visible 1-to-N pin order
on the physical connector is not yet silkscreen-verified — the
authoritative pending-silkscreen list is
[`s360-100-r4-core.md` Open Question #9](s360-100-r4-core.md#open-questions--verification-needed).

| Connector ref | Connected module | Module SKU | Connector type | Pin count | Pin-1 orientation | Intended function | Notes / caveats |
|---|---|---|---|---|---|---|---|
| `J1` | Sense360 VentIQ | `S360-211` | TBD (header — type not annotated on the visible sheet) | 5 | TBD — needs silkscreen confirmation | Bathroom ventilation IQ module (humidity / fan trigger logic) — see [§ J1 — VentIQ module connector (5-pin)](#j1--ventiq-module-connector-5-pin) | Schematic legacy label: *"Formerly used as AirIQ Bathroom Module connector"*. Note: the `S360-211` board-side audit ([`s360-211-r4-ventiq.md` § Module connector mating](s360-211-r4-ventiq.md#module-connector-mating)) records VentIQ plugging into the Core 7-pin `J9` "AirIQ Module Connector" slot; the Core-side architecture doc places VentIQ on `J1` (5-pin). This cross-doc disagreement is preserved as an open silkscreen / harness question — see [Open questions](#open-questions--verification-needed) #1. |
| `J2` | Sense360 PoE PSU | `S360-410` | 2-pin power inlet header (type — needs silkscreen confirmation) | 2 | TBD — needs silkscreen confirmation | Off-board PoE PSU DC inlet (`PoE_ACDC` from `S360-410`) — see [§ J2 — PoE PSU inlet (2-pin)](#j2--poe-psu-inlet-2-pin) | `S360-410` `schematic_status` stays `cataloged_unverified`; `PACKAGE-POE-410-001` lane is unchanged. J2 PoE harness identity is [`s360-100-r4-core.md` Open Question #6](s360-100-r4-core.md#open-questions--verification-needed). |
| `J3` | Sense360 LED | `S360-300` | TBD (3-pin header — type not annotated on the visible sheet) | 3 | TBD — needs silkscreen confirmation | WS2812B LED ring data output — see [§ J3 — LED ring connector (3-pin)](#j3--led-ring-connector-3-pin) | LED stays `preview` (`Ceiling-POE-VentIQ-RoomIQ-LED`); this PR does not promote it. Schematic Core `J3` pin 2 rail identity (`+5V` vs `+3.3V`) carries an [open question](s360-300-r4-led.md#open-questions--verification-needed) on the module-side audit. |
| `J4` | Sense360 Relay | `S360-310` | TBD (3-pin header — type not annotated on the visible sheet) | 3 | TBD — needs silkscreen confirmation | Relay-module drive (`Relay` gate from `IO3`) — see [§ J4 — Relay module connector (3-pin)](#j4--relay-module-connector-3-pin) | Schematic legacy label: *"Formerly was Relay Module connector"*. `S360-310` stays `cataloged_unverified`. |
| `J6` | Sense360 PWM | `S360-311` | TBD (13-pin header — type not annotated on the visible sheet) | 13 | TBD — needs silkscreen confirmation | 12 V PWM-fan driver harness (up to 4 fans with per-fan `TachPMW1..4` PWM-drive outputs + per-fan `Pul_Cou1..4` tach inputs + shared `TachIO` passthrough + optional Nextion UART) — see [§ J6 — 12 V PWM fan connector (13-pin)](#j6--12-v-pwm-fan-connector-13-pin) | Schematic legacy label: *"Formerly used as 12v PWM Fan connector"*. Core-side 1-to-13 silkscreen pin order is `verify` per [`s360-100-r4-core.md` Open Question #9](s360-100-r4-core.md#open-questions--verification-needed). Module-side `J3` (S360-311) 1-to-13 pin order is schematic-confirmed ([`s360-311-r4-pwm.md` § Module-side `J3` ↔ Core-side `J6`](s360-311-r4-pwm.md#module-side-j3--core-side-j6-13-pin-harness)). Module-side `J3` carries `UART_RX` / `UART_TX` on pins 11 / 12; whether the Core-side `J6` also carries those is **TBD** — see [Open questions](#open-questions--verification-needed) #2. |
| `J7` | Sense360 DAC | `S360-312` | TBD (6-pin header — type not annotated on the visible sheet) | 6 | TBD — needs silkscreen confirmation | GP8403 DAC fan-controller driver (I²C + UART) — see [§ J7 — DAC module connector (6-pin)](#j7--dac-module-connector-6-pin) | Schematic legacy label: *"Formerly used as GP8403 Fan connector"*. `S360-312` stays `cataloged_unverified`. |
| `J8` | (USB-C 2.0 receptacle) | N/A | USB-C 2.0 receptacle | — | N/A | USB-C power inlet + ESP32-S3 USB data (bench flashing / boot log) — see [§ J8 — USB-C receptacle](#j8--usb-c-receptacle) | Not a Sense360 module connector. Included for completeness. |
| `J9` | Sense360 AirIQ | `S360-210` | TBD (7-pin header — type not annotated on the visible sheet) | 7 | TBD — needs silkscreen confirmation | Air-quality module (SPS30 / SGP41 / SCD41 / BMP390 stack on the AirIQ board) — see [§ J9 — AirIQ module connector (7-pin)](#j9--airiq-module-connector-7-pin) | Schematic legacy label: *"Formerly used as AirIQ Module connector"*. VentIQ (`S360-211`) audit ([`s360-211-r4-ventiq.md` § Module connector mating](s360-211-r4-ventiq.md#module-connector-mating)) also records VentIQ plugging into this connector — see [Open questions](#open-questions--verification-needed) #1. |
| `J10` | Sense360 RoomIQ | `S360-200` | TBD (12-pin header — type not annotated on the visible sheet) | 12 | TBD — needs silkscreen confirmation | Presence / comfort module (mmWave radar + PIR + ambient-light sensor) — see [§ J10 — RoomIQ module connector (12-pin)](#j10--roomiq-module-connector-12-pin) | Schematic legacy label: *"Formerly used as Presence Comfort Module Connector"*. Core-side `J10` 1-to-12 silkscreen pin order and the Core `J10` vs RoomIQ `J6` pin-order reconciliation are pending — see [`s360-100-r4-core.md` Open Question #9](s360-100-r4-core.md#open-questions--verification-needed) and [`firmware-package-mapping-audit.md` Core J10 vs RoomIQ J6](firmware-package-mapping-audit.md#core-j10-vs-roomiq-j6-pin-order). |
| `J13` | (Generic on-board fan output) | N/A | TBD (2-pin / 3-pin — needs silkscreen confirmation) | 2–3 | TBD — needs silkscreen confirmation | Single on-board PWM-style fan drive (`FAN` net from `IO21`) — see [§ J13 — Generic FAN connector](#j13--generic-fan-connector) | Not a Sense360 module SKU connector. `s360-100-core-architecture.md` records `J13` as 2-pin; `s360-100-r4-core.md` § J13 records 3 pins (`+5V`, `FAN`, `GND`). Cross-doc pin-count reconciliation is preserved as **TBD** — see [Open questions](#open-questions--verification-needed) #3. |
| `J15` | Sense360 TRIAC | `S360-320` | TBD (4-pin header — type not annotated on the visible sheet) | 4 | TBD — needs silkscreen confirmation | TRIAC fan-module gate / zero-cross control — see [§ J15 — TRIAC module connector (4-pin)](#j15--triac-module-connector-4-pin) | Schematic legacy label: *"Formerly used as a TRIAC Fan Module connector"*. FanTRIAC `HW-005` BUILDABILITY + `HW-PINMAP-320-FOLLOWUP` resolved (TRIAC-PINMAP-CORRECT-001): `TRI_GPIO1` = `IO14` (`GPIO14`, gate), `TRI_GPIO2` = `IO13` (`GPIO13`, zero-cross), schematic-verified per S360-100-R4 + S360-320-R4. Product stays `status: blocked` (bench `PACKAGE-TRIAC-001` + `COMPLIANCE-001`). |

`TP10` / `TP13` / `TP14` (JTAG test pads), `SW3` (boot button — `IO_0`
strap), and `SW4` (reset button) are intentionally **not** included
above — they are test pads / on-board controls, not module
connectors. Per [`s360-100-r4-core.md` JTAG test points](s360-100-r4-core.md#jtag-test-points-no-dedicated-connector)
the presence of a dedicated JTAG / programming header on a hidden
sheet remains `verify`.

## Native ESP32-S3 GPIO requirements (architectural rule)

The architectural rule recorded in
[`s360-100-native-tach-pulse-strategy.md`](s360-100-native-tach-pulse-strategy.md)
(`S360-100-NATIVE-TACH-PULSE-001`) and in
[`s360-100-native-fan-gpio-map.md`](s360-100-native-fan-gpio-map.md)
(`S360-100-NATIVE-FAN-GPIO-MAP-001`) is preserved by every per-pin
table below:

1. **Tach / pulse-counter inputs (`TachIO`, `Pul_Cou1..4`) MUST
   terminate on native ESP32-S3 GPIO.** Any ESPHome
   `sensor: platform: pulse_counter`, any per-fan RPM input, and any
   pulse-counting line must land on an interrupt-capable native
   ESP32-S3 `InternalGPIOPin`. The schematic-printed terminations are
   `TachIO`→`IO16`, `Pul_Cou1`→`IO17`, `Pul_Cou2`→`IO18`,
   `Pul_Cou3`→`IO46`, `Pul_Cou4`→`IO9` (canonical
   [`S360-100-R4.pdf`](schematics/S360-100-R4.pdf), R4 refresh).
2. **FanPWM control (`TachPMW1..4`) is now on native ESP32-S3 GPIO.**
   The refreshed R4 schematic prints `TachPMW1`→`IO10`,
   `TachPMW2`→`IO11`, `TachPMW3`→`IO12`, `TachPMW4`→`IO39`. The
   SX1509 (`U3`) I/O expander block that hosted the prior R4
   snapshot's FanPWM control / tach paths is no longer printed on
   the visible sheet; the SX1509 is **removed from the S360-100 fan
   signal path** by the refreshed schematic.
3. **Historical SX1509 fan-path assumptions are superseded.** The
   FanPWM-via-SX1509 firmware binding in
   [`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml)
   and
   [`packages/expansions/fan_pwm_sx1509.yaml`](../../packages/expansions/fan_pwm_sx1509.yaml)
   is classified **legacy / superseded** under
   `S360-100-NATIVE-FAN-GPIO-MAP-001`. The
   [`PWM-SX1509-TACH-PROOF-001`](../../tests/test_sx1509_tach_pulse_counter_proof.py)
   compile/config proof remains the authoritative evidence for the
   architectural rule (an SX1509 pin cannot back an ESPHome
   `pulse_counter`); the proof fixture / test stay in place as
   historical evidence and are not removed by this document.
4. **Expander pins for tach / pulse counter are forbidden in every
   per-pin table below.** No row in any per-connector pin table
   below maps `TachIO` / `Pul_Cou1..4` / any other pulse-counter
   signal through an expander GPIO. ESP32-S3 GPIO is the **only**
   permitted pin family for tach / pulse counter; `TBD` is the
   correct value if the native pin is not schematic-printed.

## Per-connector pin tables

Every per-connector table below uses the following columns:

| Column | Meaning |
|---|---|
| **Pin number** | The connector pin number (1..N) as labelled by the per-module audit / Core schematic. Where the 1-to-N silkscreen pin order is `verify`, the row's overall status is `needs silkscreen confirmation`. |
| **Core net / signal name** | The net label printed on the canonical R4 schematic (`+5V`, `+3.3V`, `GND`, `I2C_SDA`, `LED_DATA_3V3`, `TachPMW1`, `Pul_Cou1`, etc.). |
| **ESP32 GPIO (or N/A / TBD)** | The native ESP32-S3 module pin that sources or sinks the net at the MCU, taken from the canonical R4 schematic per [`s360-100-r4-core.md` § ESP32-S3 pin and net mapping](s360-100-r4-core.md#esp32-s3-pin-and-net-mapping) and the architecture doc's [pin allocation table](s360-100-core-architecture.md#pin-allocation-table--native-esp32-s3-gpio-termination). `N/A` for power / ground / off-chip rails; `TBD` where the schematic does not unambiguously print the ESP32-side source. |
| **Module-side signal / function** | The role the same net plays on the attached module board (taken from the per-module audit docs). |
| **Signal type** | One of: `power`, `ground`, `digital input (interrupt-capable)`, `digital input (polled)`, `digital output`, `PWM output (native)`, `I²C (open-drain)`, `UART`, `analog`, `power inlet`. |
| **Voltage / domain** | `+5V`, `+3.3V`, `GND`, `Vbus (5V)`, `PoE_ACDC` (DC inlet from `S360-410`; voltage is `PoE_ACDC` rail, off-board), `Logic 3.3V (ESP32-S3)`, `Mains-domain` (TRIAC drive — galvanically isolated on the module side via opto/SSR; **not** routed on the Core side), etc. |
| **Status** | One of `verified` / `schematic-backed` / `TBD` / `needs silkscreen confirmation` per [§ Status-language rules](#status-language-rules). |

### J1 — VentIQ module connector (5-pin)

| Pin | Core net / signal | ESP32 GPIO | Module-side signal / function | Signal type | Voltage / domain | Status |
|---|---|---|---|---|---|---|
| 1 | `+5V` | N/A | VentIQ +5 V rail (off-board sensors, fan-relay coil supply path — verify on the module side) | power | `+5V` | needs silkscreen confirmation |
| 2 | `+3.3V` | N/A | VentIQ +3.3 V rail (sensor logic supply) | power | `+3.3V` | needs silkscreen confirmation |
| 3 | `I2C_SCL` | `IO45` | Shared I²C bus clock — VentIQ on-board sensors (SPS30 / IR temperature / fan-relay control as wired by the VentIQ board) | I²C (open-drain) | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 4 | `I2C_SDA` | `IO48` | Shared I²C bus data — same as above | I²C (open-drain) | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 5 | `GND` | N/A | VentIQ ground reference | ground | `GND` | needs silkscreen confirmation |

> **Cross-doc reconciliation flag.** The Core-side architecture doc
> [`s360-100-core-architecture.md` § Connector / module matrix](s360-100-core-architecture.md#connector--module-matrix)
> records `J1` as the 5-pin VentIQ connector. The VentIQ board-side
> audit
> [`s360-211-r4-ventiq.md` § Module connector mating](s360-211-r4-ventiq.md#module-connector-mating)
> records VentIQ plugging into the Core's 7-pin `J9` "AirIQ Module
> Connector". This document records both: the 5-pin `J1` row above
> reflects the Core-side architecture doc; the 7-pin `J9` row below
> reflects the per-module audit. The Core-side silkscreen / harness
> review under [`s360-100-r4-core.md` § S360-100-BENCH-001 status](s360-100-r4-core.md#s360-100-bench-001-status)
> owes the answer.

### J2 — PoE PSU inlet (2-pin)

| Pin | Core net / signal | ESP32 GPIO | Module-side signal / function | Signal type | Voltage / domain | Status |
|---|---|---|---|---|---|---|
| 1 | `PoE_ACDC` | N/A | DC output from the off-board `S360-410` PoE PSU (post-magnetics, post-PD-controller, post-isolated-DC/DC); routed through `Q2` `Si2319CDS` p-MOSFET ideal-diode-OR with `VBUS` into the `+5V` rail | power inlet | `PoE_ACDC` (DC inlet; off-board) | needs silkscreen confirmation |
| 2 | `GND` | N/A | Core / PSU ground reference | ground | `GND` | needs silkscreen confirmation |

> **`S360-410` PoE PSU stays `cataloged_unverified`.** The
> `PACKAGE-POE-410-001` audit lane is unchanged. The J2 PoE harness
> identity (cable / pigtail between the off-board `S360-410` and
> Core `J2`) is [`s360-100-r4-core.md` Open Question #6](s360-100-r4-core.md#open-questions--verification-needed)
> and is recorded as `pending — bench/manufacturing evidence required`
> in [`s360-100-r4-core.md` § S360-100-BENCH-001 status](s360-100-r4-core.md#s360-100-bench-001-status).

### J3 — LED ring connector (3-pin)

| Pin | Core net / signal | ESP32 GPIO | Module-side signal / function | Signal type | Voltage / domain | Status |
|---|---|---|---|---|---|---|
| 1 | `+3.3V` | N/A | LED-ring power rail (per Core schematic; module-side `J1` pin 2 is labelled `+5V` — cross-doc reconciliation is [`s360-300-r4-led.md` Open Question 1](s360-300-r4-led.md#open-questions--verification-needed)) | power | `+3.3V` (Core side) | needs silkscreen confirmation |
| 2 | `GND` | N/A | LED-ring ground | ground | `GND` | needs silkscreen confirmation |
| 3 | `LED_DATA_3V3` | `IO38` (source `LED_DATA` → `U2A` `74LVC1G07SE-7` open-drain buffer → `R8` 330 Ω series → pin 3) | WS2812B serial data input on the LED board | digital output | `Logic 3.3V (ESP32-S3)` | schematic-backed |

> **LED stays `preview`.** This document does not add `LED` to the
> Release-One config string and does not promote `Ceiling-POE-VentIQ-RoomIQ-LED`
> away from `preview`. The Core schematic prints `+3.3V` on Core
> `J3` pin 1; the module-side audit records `+5V` on LED `J1` pin
> 2 — see the cross-doc reconciliation flag at
> [`s360-300-r4-led.md` § Open questions](s360-300-r4-led.md#open-questions--verification-needed).

### J4 — Relay module connector (3-pin)

| Pin | Core net / signal | ESP32 GPIO | Module-side signal / function | Signal type | Voltage / domain | Status |
|---|---|---|---|---|---|---|
| 1 | `+5V` | N/A | Relay-module coil rail / driver supply | power | `+5V` | needs silkscreen confirmation |
| 2 | `Relay` | `IO3` | Relay-module drive (transistor / opto base) — load-side `J1` "Inline Fan" mains switching is on the module, see [`s360-310-r4-relay.md` § Module-side `J2` ↔ Core-side `J4`](s360-310-r4-relay.md#module-side-j2--core-side-j4-3-pin-harness) | digital output | `Logic 3.3V (ESP32-S3)` (drive line; mains switching is module-side / isolated) | schematic-backed |
| 3 | `GND` | N/A | Relay-module ground reference | ground | `GND` | needs silkscreen confirmation |

### J6 — 12 V PWM fan connector (13-pin)

Carries the Sense360 PWM (S360-311) FanPWM hardware path. The
**module-side** 13-pin connector is `J3` on `S360-311-R4` and the
1-to-13 net order on the module side is schematic-confirmed in
[`s360-311-r4-pwm.md` § Module-side `J3` ↔ Core-side `J6`](s360-311-r4-pwm.md#module-side-j3--core-side-j6-13-pin-harness).
The **Core-side** 1-to-13 silkscreen pin order is `verify` per
[`s360-100-r4-core.md` Open Question #9](s360-100-r4-core.md#open-questions--verification-needed),
so the Core-side rows below carry `needs silkscreen confirmation`
on the pin numbers themselves; the **net-to-GPIO** assignments are
**schematic-backed** by the canonical R4 sheet.

The pin-number column below follows the **module-side** `J3` 1-to-13
order from [`s360-311-r4-pwm.md` § Schematic summary](s360-311-r4-pwm.md#schematic-summary)
(the only side where the order is schematic-confirmed) so the
Core-side and module-side rows can be lined up 1-to-13.

| Pin | Core net / signal | ESP32 GPIO | Module-side signal / function | Signal type | Voltage / domain | Status |
|---|---|---|---|---|---|---|
| 1 | `+5V` | N/A | S360-311 +5 V input → MT3608 boost → +12V fan rail | power | `+5V` | needs silkscreen confirmation |
| 2 | `TachIO` | `IO16` (module pin 9) | Shared tach passthrough — drains tied to the per-fan low-side MOSFET drain on the module | digital input (interrupt-capable) | `Logic 3.3V (ESP32-S3)` | schematic-backed |
| 3 | `TachPMW1` | `IO10` (module pin 18) | FanPWM control channel 1 — `Q1` gate (1 kΩ gate resistor `R1`) | PWM output (native) | `Logic 3.3V (ESP32-S3)` | schematic-backed |
| 4 | `Pul_Cou1` | `IO17` (module pin 10) | Per-fan tach feedback channel 1 (from fan `J1` tach line) | digital input (interrupt-capable) | `Logic 3.3V (ESP32-S3)` | schematic-backed |
| 5 | `TachPMW2` | `IO11` (module pin 19) | FanPWM control channel 2 — `Q2` gate (1 kΩ gate resistor `R2`) | PWM output (native) | `Logic 3.3V (ESP32-S3)` | schematic-backed |
| 6 | `Pul_Cou2` | `IO18` (module pin 11) | Per-fan tach feedback channel 2 (from fan `J2` tach line) | digital input (interrupt-capable) | `Logic 3.3V (ESP32-S3)` | schematic-backed |
| 7 | `TachPMW3` | `IO12` (module pin 20) | FanPWM control channel 3 — `Q3` gate (1 kΩ gate resistor `R6`) | PWM output (native) | `Logic 3.3V (ESP32-S3)` | schematic-backed |
| 8 | `Pul_Cou3` | `IO46` (module pin 16) | Per-fan tach feedback channel 3 (from fan `J4` tach line) | digital input (interrupt-capable) | `Logic 3.3V (ESP32-S3)` | schematic-backed |
| 9 | `TachPMW4` | `IO39` (module pin 32) | FanPWM control channel 4 — `Q4` gate (1 kΩ gate resistor `R7`) | PWM output (native) | `Logic 3.3V (ESP32-S3)` | schematic-backed |
| 10 | `Pul_Cou4` | `IO9` (module pin 17) | Per-fan tach feedback channel 4 (from fan `J5` tach line) | digital input (interrupt-capable) | `Logic 3.3V (ESP32-S3)` | schematic-backed |
| 11 | `UART_RX` (module-side label) | TBD on the Core side — see [Open questions](#open-questions--verification-needed) #2 | Module-side route from `J3` pin 11 to the on-board Nextion display connector `J6` (S360-311 module side) | UART | `Logic 3.3V (ESP32-S3)` | TBD |
| 12 | `UART_TX` (module-side label) | TBD on the Core side — see [Open questions](#open-questions--verification-needed) #2 | Module-side route from `J3` pin 12 to the on-board Nextion display connector `J6` (S360-311 module side) | UART | `Logic 3.3V (ESP32-S3)` | TBD |
| 13 | `GND` | N/A | Shared ground | ground | `GND` | needs silkscreen confirmation |

> **Native GPIO requirement satisfied on the schematic side.** Every
> tach / pulse-counter / PWM-drive net on this connector terminates
> at a native ESP32-S3 GPIO on the canonical R4 schematic. No row
> above maps `TachIO` / `Pul_Cou1..4` through the SX1509 (`U3`) I/O
> expander — the SX1509 is removed from the S360-100 fan signal
> path per
> [`s360-100-native-fan-gpio-map.md`](s360-100-native-fan-gpio-map.md).
> Firmware-binding (the current FanPWM YAML is still wired against
> the prior SX1509 routing, classified **legacy / superseded** per
> the same doc) and bench evidence (`PWM-12` in
> [`docs/blocker-burndown.md`](../blocker-burndown.md) stays
> NEEDS BENCH) are **out of scope** for this document.

### J7 — DAC module connector (6-pin)

| Pin | Core net / signal | ESP32 GPIO | Module-side signal / function | Signal type | Voltage / domain | Status |
|---|---|---|---|---|---|---|
| 1 | `+5V` | N/A | DAC-module +5 V supply | power | `+5V` | needs silkscreen confirmation |
| 2 | `I2C_SDA` | `IO48` | Shared I²C bus data — GP8403 DAC control bus | I²C (open-drain) | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 3 | `I2C_SCL` | `IO45` | Shared I²C bus clock — GP8403 DAC control bus | I²C (open-drain) | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 4 | `UART_RX` | `RXD0` (ESP32-S3 module pin 36) | GP8403 fan-controller UART receive (Core side) | UART | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 5 | `UART_TX` | `TXD0` (ESP32-S3 module pin 37) | GP8403 fan-controller UART transmit (Core side) | UART | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 6 | `GND` | N/A | DAC-module ground reference | ground | `GND` | needs silkscreen confirmation |

### J8 — USB-C receptacle

`J8` is a USB-C 2.0 receptacle, not a Sense360 module connector. It is
recorded here only because it carries `VBUS` into the +5 V
ideal-diode-OR network and exposes the ESP32-S3 USB `D+` / `D-` pair
for bench flashing and the boot log. Per-pin assignments below follow
the standard USB-C 2.0 pinout as recorded in
[`s360-100-r4-core.md` § J8](s360-100-r4-core.md#j8--usb-c-receptacle-usb-20).

| Pin | Core net / signal | ESP32 GPIO | Module-side signal / function | Signal type | Voltage / domain | Status |
|---|---|---|---|---|---|---|
| VBUS | `VBUS` | N/A | USB-C bus power; ideal-diode-OR with `PoE_ACDC` (`Q2`) into the `+5V` rail | power | `Vbus (5V)` | schematic-backed |
| D+ | `D+` | `IO20` | ESP32-S3 USB data plus | digital input/output | `Logic 3.3V (ESP32-S3)` | schematic-backed |
| D- | `D-` | `IO19` | ESP32-S3 USB data minus | digital input/output | `Logic 3.3V (ESP32-S3)` | schematic-backed |
| CC1 | (divider) | N/A | CC1 to R39 5.1 kΩ to GND (USB-C sink role) | digital input (polled) | `Vbus (5V) — CC` | schematic-backed |
| CC2 | (divider) | N/A | CC2 to R39 5.1 kΩ to GND (USB-C sink role) | digital input (polled) | `Vbus (5V) — CC` | schematic-backed |
| SBU1 / SBU2 | unused | N/A | unused | — | — | schematic-backed |
| SHIELD | `GND` | N/A | USB-C shield to GND | ground | `GND` | schematic-backed |

### J9 — AirIQ module connector (7-pin)

| Pin | Core net / signal | ESP32 GPIO | Module-side signal / function | Signal type | Voltage / domain | Status |
|---|---|---|---|---|---|---|
| 1 | `+5V` | N/A | AirIQ +5 V rail (SPS30, sensor sub-modules that need +5 V) | power | `+5V` | needs silkscreen confirmation |
| 2 | `+3.3V` | N/A | AirIQ +3.3 V rail (sensor logic supply) | power | `+3.3V` | needs silkscreen confirmation |
| 3 | `I2C_SDA` | `IO48` | Shared I²C bus data (SCD41 / SGP41 / BMP390 / SFA40 stack on the AirIQ board) | I²C (open-drain) | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 4 | `I2C_SCL` | `IO45` | Shared I²C bus clock (same devices as above) | I²C (open-drain) | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 5 | `AirQ_Status_Led` | `IO7` | AirIQ status-LED line (legacy `AirQ` net name preserved for backwards compatibility; VentIQ may reuse the same line — see [`s360-100-r4-core.md` Open Question #4](s360-100-r4-core.md#open-questions--verification-needed)) | digital output | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 6 | `AirQ_Led` | `IO8` | AirIQ LED control line (legacy net name; VentIQ may reuse) | digital output | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 7 | `GND` | N/A | AirIQ ground reference | ground | `GND` | needs silkscreen confirmation |

### J10 — RoomIQ module connector (12-pin)

| Pin | Core net / signal | ESP32 GPIO | Module-side signal / function | Signal type | Voltage / domain | Status |
|---|---|---|---|---|---|---|
| 1 | `+3.3V` | N/A | RoomIQ sensor-logic supply (per Core schematic; the RoomIQ-side `J6` schematic prints `+5V` on pin 1 — cross-doc reconciliation is [`firmware-package-mapping-audit.md` Core J10 vs RoomIQ J6](firmware-package-mapping-audit.md#core-j10-vs-roomiq-j6-pin-order)) | power | `+3.3V` (Core side) | needs silkscreen confirmation |
| 2 | `+5V` | N/A | RoomIQ radar supply (LD2450 / SEN0609) | power | `+5V` | needs silkscreen confirmation |
| 3 | `SEN0609_RX` | `IO4` | DFRobot SEN0609 / C4001 radar UART (Core RX) | UART | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 4 | `SEN0609_TX` | `IO5` | DFRobot SEN0609 / C4001 radar UART (Core TX) | UART | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 5 | `out(gpio6)` | `IO6` | Auxiliary line to the DFRobot radar `J3` (RoomIQ side); purpose at the SEN0609 side is `verify` | digital output | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 6 | `Hi-Link_RX` | `IO1` | Hi-Link LD2450 radar UART (Core RX) | UART | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 7 | `Hi-Link_TX` | `IO2` | Hi-Link LD2450 radar UART (Core TX) | UART | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 8 | `PIR` | `IO15` | EKMC1601111 PIR motion output (from RoomIQ board `U3` pin 2) | digital input (polled) | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 9 | `ALS_INT` | `IO47` | LTR-303ALS-01 ambient-light-sensor interrupt output (from RoomIQ board `U1` pin 5) | digital input (interrupt-capable) | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 10 | `I2C_SDA` | `IO48` | Shared I²C bus data — RoomIQ on-board sensors (LTR-303ALS-01 / SHT4x / BMP581) | I²C (open-drain) | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 11 | `I2C_SCL` | `IO45` | Shared I²C bus clock — same devices as above | I²C (open-drain) | `Logic 3.3V (ESP32-S3)` | needs silkscreen confirmation |
| 12 | `GND` | N/A | RoomIQ ground reference | ground | `GND` | needs silkscreen confirmation |

### J13 — Generic FAN connector

`J13` is **not** a Sense360 module SKU connector. It carries the
single `FAN` net (sourced at ESP32-S3 `IO21`) plus power / ground.
The architecture doc records 2 pins; the per-Core net doc records 3
pins. The exact pin count and 1-to-N order on this header are not
unambiguously fixed on the canonical R4 schematic and are recorded
as **TBD** — see [Open questions](#open-questions--verification-needed)
#3.

| Pin | Core net / signal | ESP32 GPIO | Module-side signal / function | Signal type | Voltage / domain | Status |
|---|---|---|---|---|---|---|
| 1 | `+5V` | N/A | Generic fan supply (where +5 V is present on this header per [`s360-100-r4-core.md` § J13](s360-100-r4-core.md#j13--fan-connector-3-pin)) | power | `+5V` | TBD |
| 2 | `FAN` | `IO21` | Single-fan PWM-style drive line (Core source — IO21) | digital output | `Logic 3.3V (ESP32-S3)` | TBD |
| 3 | `GND` (if 3-pin) | N/A | Ground (3-pin variant per [`s360-100-r4-core.md` § J13](s360-100-r4-core.md#j13--fan-connector-3-pin); absent on the 2-pin variant per [`s360-100-core-architecture.md` § Connector / module matrix](s360-100-core-architecture.md#connector--module-matrix)) | ground | `GND` | TBD |

### J15 — TRIAC module connector (4-pin)

| Pin | Core net / signal | ESP32 GPIO | Module-side signal / function | Signal type | Voltage / domain | Status |
|---|---|---|---|---|---|---|
| 1 | `+3.3V` | N/A | TRIAC-module sensor / opto supply (Core side; mains domain is module-side, opto-isolated) | power | `+3.3V` | needs silkscreen confirmation |
| 2 | `TRI_GPIO1` | `IO14` (`GPIO14`) | TRIAC gate drive — drives the `U1` MOC3023M opto-triac LED side (module-side opto-isolation provides mains isolation; the Core-side line is `Logic 3.3V (ESP32-S3)`). Net→pin per S360-100-R4; gate role per S360-320-R4. | digital output | `Logic 3.3V (ESP32-S3)` (Core side); module side opto-isolates to `Mains-domain` | schematic-backed |
| 3 | `TRI_GPIO2` | `IO13` (`GPIO13`) | Zero-cross sense, interrupt-capable input — reads the `OK1` EL814 collector (`R4` 10 kΩ pull-up to `+3V3`). Net→pin per S360-100-R4; zero-cross role per S360-320-R4. | digital input (interrupt-capable) | `Logic 3.3V (ESP32-S3)` (Core side); module side opto-isolates to `Mains-domain` | schematic-backed |
| 4 | `GND` | N/A | TRIAC-module ground reference (Core side) | ground | `GND` | needs silkscreen confirmation |

> **FanTRIAC `HW-005` BUILDABILITY and `HW-PINMAP-320-FOLLOWUP`
> resolved; the product stays blocked (TRIAC-PINMAP-CORRECT-001).** The
> ESP32-side source pins for `TRI_GPIO1` / `TRI_GPIO2` are now
> schematic-verified: the SX1509-free `S360-100-R4` Core routes both nets
> DIRECT to interrupt-capable ESP32-S3 GPIOs — **`TRI_GPIO1` = `IO14`
> (`GPIO14`), TRIAC gate drive** (drives the `U1` MOC3023M opto-triac) and
> **`TRI_GPIO2` = `IO13` (`GPIO13`), zero-cross sense** (reads the `OK1`
> EL814 collector). The net→pin assignment is taken from
> [`S360-100-R4.pdf`](schematics/S360-100-R4.pdf); the gate-vs-zero-cross
> roles are taken from [`S360-320-R4.pdf`](schematics/S360-320-R4.pdf)
> (`TRI_GPIO1` drives the MOC3023M gate opto-driver; `TRI_GPIO2` is the
> EL814 zero-cross phototransistor collector, `R4` 10 kΩ pull-up). The
> Release-One bundle
> [`products/bundles/ceiling-poe-ventiq-fantriac-roomiq.yaml`](../../products/bundles/ceiling-poe-ventiq-fantriac-roomiq.yaml)
> binds `fan_triac_gate_pin: GPIO14` / `fan_triac_zc_pin: GPIO13`
> accordingly — this corrected the earlier gate/zero-cross transposition
> and the placeholder `GPIO5` / `GPIO6` that collided with RoomIQ
> `SEN0609` on `J10`. `IO13` / `IO14` also carry the shared connector
> bus's `SCS` / `SCLK` labels, but no SPI peripheral is active in this
> composition, so both pins are free for the TRIAC. This is a
> **buildability** resolution only: the product **stays `status:
> blocked`**, gated by bench (`PACKAGE-TRIAC-001`) and mains-voltage
> compliance (`COMPLIANCE-001`); it is never stable / recommended /
> default / buyable / WebFlash-exposed, and the 1-to-4 silkscreen pin
> order is still owed.

## Voltage / domain summary

Domain identifiers used in the per-connector tables above:

| Domain identifier | Meaning |
|---|---|
| `+5V` | Core `+5V` rail (ORed VBUS / `PoE_ACDC` through `Q2` `Si2319CDS` + `D12` `1N5819WS`). Available on most module connectors. |
| `+3.3V` | Core `+3.3V` rail from `U1` `RT8059GJ5` buck (`L1` 2.2 µH, `R5` / `R6` feedback). Sensor / radar logic supply. |
| `GND` | Common ground reference. |
| `PoE_ACDC` | DC inlet from off-board `S360-410` PoE PSU. Voltage is the PoE PSU's DC output; the Core does not regulate this rail before `Q2`. |
| `Vbus (5V)` | USB-C bus power from `J8`. ORed into the `+5V` rail via `Q2`. |
| `Logic 3.3V (ESP32-S3)` | ESP32-S3 module digital logic level. All native ESP32-S3 GPIO signals are nominally 3.3 V CMOS. |
| `Mains-domain` | Mains-voltage domain on the TRIAC module-side load path. Opto- / SSR-isolated from the Core-side `Logic 3.3V (ESP32-S3)` drive line. **Never** carried on the Core side of `J15`. |

## Cross references

This document is cross-referenced from / to:

- [`s360-100-r4-core.md`](s360-100-r4-core.md) — per-pin / per-net /
  per-connector Core reference (authoritative source for net /
  GPIO assignments).
- [`s360-100-core-architecture.md`](s360-100-core-architecture.md) —
  connector / module SKU matrix (authoritative source for the Core
  ↔ module SKU mapping).
- [`s360-100-native-fan-gpio-map.md`](s360-100-native-fan-gpio-map.md) —
  canonical FanPWM control + tach native ESP32-S3 GPIO map
  (`TachPMW1..4` / `Pul_Cou1..4` / `TachIO`).
- [`s360-100-native-tach-pulse-strategy.md`](s360-100-native-tach-pulse-strategy.md) —
  canonical architectural rule: native ESP32-S3 GPIO required for
  tach / pulse-counter inputs; SX1509 expander forbidden;
  compile/config proof recorded.
- [`s360-200-r4-roomiq.md`](s360-200-r4-roomiq.md) — RoomIQ board-side
  audit (J10 mating; Core J10 vs RoomIQ J6 pin-order discrepancy).
- [`s360-210-r4-airiq.md`](s360-210-r4-airiq.md) — AirIQ board-side
  audit (J9 mating).
- [`s360-211-r4-ventiq.md`](s360-211-r4-ventiq.md) — VentIQ board-side
  audit (records VentIQ plugging into Core `J9`; cross-doc tension
  with the architecture doc's `J1` row).
- [`s360-300-r4-led.md`](s360-300-r4-led.md) — LED board-side audit
  (J3 mating; +5V vs +3.3V rail-identity Open Question).
- [`s360-310-r4-relay.md`](s360-310-r4-relay.md) — Relay board-side
  audit (J4 mating).
- [`s360-310-relay-pinmap-reconcile.md`](s360-310-relay-pinmap-reconcile.md)
  — Relay GPIO cross-layer reconcile record
  (S360-310-RELAY-PINMAP-RECONCILE-001; `Relay` = `IO3` = `GPIO3`).
- [`s360-311-r4-pwm.md`](s360-311-r4-pwm.md) — PWM board-side audit
  (module-side `J3` ↔ Core-side `J6` reconciliation; UART pins on
  `J3` pins 11–12).
- [`s360-312-r4-dac.md`](s360-312-r4-dac.md) — DAC board-side audit
  (J7 mating).
- [`s360-320-r4-triac.md`](s360-320-r4-triac.md) — TRIAC board-side
  audit (J15 mating; TRI_GPIO source-pin question).
- [`s360-410-r4-poe.md`](s360-410-r4-poe.md) — PoE PSU board-side
  audit (J2 inlet; `PACKAGE-POE-410-001` lane).
- Per-module **module-side pinmap docs** (MODULE-PINMAPS-GDRIVE-001):
  [`s360-200-module-pinmap.md`](s360-200-module-pinmap.md),
  [`s360-210-module-pinmap.md`](s360-210-module-pinmap.md),
  [`s360-211-module-pinmap.md`](s360-211-module-pinmap.md),
  [`s360-300-module-pinmap.md`](s360-300-module-pinmap.md),
  [`s360-310-module-pinmap.md`](s360-310-module-pinmap.md),
  [`s360-311-module-pinmap.md`](s360-311-module-pinmap.md),
  [`s360-312-module-pinmap.md`](s360-312-module-pinmap.md),
  [`s360-320-module-pinmap.md`](s360-320-module-pinmap.md),
  [`s360-400-module-pinmap.md`](s360-400-module-pinmap.md),
  [`s360-410-module-pinmap.md`](s360-410-module-pinmap.md). Each
  records the **module-side** view of its board and reconciles
  every pin back to the matching Core connector row above.
- [`docs/sense360-room-bundles.md`](../sense360-room-bundles.md) —
  canonical PoE room bundle SKU matrix (Core + room modules + PoE
  PSU).
- [`docs/blocker-burndown.md`](../blocker-burndown.md) — blocker /
  scope-classification table (PWM-12 / HW-005 / PACKAGE-POE-410-001).

## Open questions / verification needed

These items are not closed by this document; they are recorded so
that bench / silkscreen / harness follow-up work has an actionable
list. None of them by itself blocks the canonical pin map above;
each is a row that may move from `TBD` / `needs silkscreen
confirmation` to `verified` once the listed evidence exists.

1. **`J1` vs `J9` reconciliation for VentIQ (`S360-211`).** The
   architecture doc places VentIQ on the 5-pin `J1` connector; the
   VentIQ board-side audit records VentIQ plugging into the Core
   7-pin `J9` "AirIQ Module Connector". Bench / silkscreen
   evidence is required to determine which connector the Release-
   One VentIQ harness actually mates with on the physical Core
   board.
2. **`J6` Core-side pins 11 / 12 — UART or unconnected?** The
   module-side `J3` (S360-311) schematic prints `UART_RX` /
   `UART_TX` on pins 11 / 12 and routes them on-board to the
   Nextion display connector. The Core-side `J6` capture in
   [`s360-100-r4-core.md` § J6](s360-100-r4-core.md#j6--12-v-pwm-fan-connector-13-pin)
   currently lists only the 11 power / GND / fan-signal nets and
   does not record UART pins. Either the Core capture is
   incomplete (UART pair is in fact on Core `J6` pins 11 / 12), or
   the Nextion UART is delivered to the S360-311 module via a
   separate harness and pins 11 / 12 are unconnected on the
   13-pin Core-to-module cable.
3. **`J13` pin count (2-pin vs 3-pin).** The architecture doc
   records `J13` as 2-pin; the per-Core net doc records 3 pins
   (`+5V`, `FAN`, `GND`). The exact pin count and 1-to-N order on
   this header are not unambiguously fixed on the canonical R4
   schematic — both `+5V` / `FAN` / `GND` are present at this
   connector but the pin numbering is `verify`.
4. **`J15` `TRI_GPIO1` / `TRI_GPIO2` ESP32-side source pins —
   RESOLVED (HW-PINMAP-320-FOLLOWUP; TRIAC-PINMAP-CORRECT-001).** The
   SX1509-free `S360-100-R4` Core routes these nets DIRECT to
   interrupt-capable ESP32-S3 GPIOs: `TRI_GPIO1` = `IO14` (`GPIO14`,
   TRIAC gate drive → MOC3023M) and `TRI_GPIO2` = `IO13` (`GPIO13`,
   zero-cross sense ← EL814), schematic-verified per S360-100-R4
   (net→pin) + S360-320-R4 (gate-vs-zero-cross roles). The old
   `GPIO5` / `GPIO6` placeholders are gone (the bundle binds `GPIO14` /
   `GPIO13`, correcting the earlier transposition). The `SCS` / `SCLK`
   shared-bus labels on `IO13` / `IO14` are inactive in this
   composition. This closes FanTRIAC `HW-005` BUILDABILITY and the
   `HW-PINMAP-320-FOLLOWUP` source-pin question; the product stays
   `status: blocked`, gated by bench (`PACKAGE-TRIAC-001`) and mains
   compliance (`COMPLIANCE-001`), and the 1-to-4 silkscreen pin order
   is still owed.
5. **All multi-pin headers — 1-to-N silkscreen pin order.** The
   per-pin tables above record `needs silkscreen confirmation` on
   every pin number where the schematic prints the net list but
   the 1-to-N visible silkscreen order is not yet bench-verified.
   The canonical pending-silkscreen list is
   [`s360-100-r4-core.md` Open Question #9](s360-100-r4-core.md#open-questions--verification-needed)
   and is owned by [`s360-100-r4-core.md` § S360-100-BENCH-001 status](s360-100-r4-core.md#s360-100-bench-001-status).
6. **Connector type / part number per header.** This document does
   **not** invent connector part numbers (e.g. `B2B-XH-A`, `PH`,
   `SH`, generic 1.27 mm or 2.54 mm headers). The visible R4
   schematic symbols print net lists and pin numbers but do not
   annotate the connector part identity in every case. Where the
   part identity is not annotated on the visible sheet, the
   Connector type column in the [connector matrix](#connector-matrix)
   carries `TBD` and a `needs silkscreen confirmation` flag.

## Do-not-change guardrails (S360-100-CONNECTOR-PINMAP-001)

This document and the tests added with it must not:

- publish firmware, create release artifacts, change
  [`firmware/sources.json`](../../firmware/sources.json), change
  [`manifest.json`](../../manifest.json), or promote any release
  target;
- change Release-One (`Ceiling-POE-VentIQ-RoomIQ` / stable /
  `v1.0.0`) or the LED preview entry
  (`Ceiling-POE-VentIQ-RoomIQ-LED` / preview);
- promote `S360-300` (LED) from `preview` to `stable`;
- promote `S360-310` / `S360-311` / `S360-312` `schematic_status`
  (each stays `cataloged_unverified`);
- promote `S360-320` (TRIAC) beyond `schematic-backed`, or claim the
  FanTRIAC bench (`PACKAGE-TRIAC-001`) or mains-voltage compliance
  (`COMPLIANCE-001`) blockers are solved, or promote FanTRIAC beyond
  `status: blocked` — the `J15` `HW-005` BUILDABILITY +
  `HW-PINMAP-320-FOLLOWUP` pin resolution recorded here is buildability
  only (NOT bench, NOT compliance, NOT stable);
- promote `S360-410` (PoE PSU) `schematic_status` (stays
  `cataloged_unverified`) or claim the `PACKAGE-POE-410-001`
  blocker chain is solved;
- promote `FanRelay` / `FanPWM` / `FanDAC` to release;
- flip any module's `webflash_build_matrix`, add an `artifact_name`,
  add a WebFlash wrapper, or add a `config/webflash-builds.json`
  row;
- claim RPM / tach validation, measured PWM polarity / current /
  thermal envelope, or any other bench-measured fan capability;
- claim final firmware GPIO allocations beyond what the canonical
  R4 schematic itself prints (no firmware YAML edit is performed);
- fabricate connector types, pin orders, signal assignments, or
  ESP32 GPIO allocations — values that are not proven by the
  canonical R4 schematic carry `TBD` and `needs silkscreen
  confirmation`;
- map any tach / pulse-counter signal (`TachIO` / `Pul_Cou1..4`)
  through an expander GPIO — native ESP32-S3 GPIO is the only
  permitted pin family for those signals;
- alter or weaken the SX1509 / `pulse_counter` compile-proof
  fixture
  [`tests/esphome/sx1509_pulse_counter_proof.yaml`](../../tests/esphome/sx1509_pulse_counter_proof.yaml)
  or guard
  [`tests/test_sx1509_tach_pulse_counter_proof.py`](../../tests/test_sx1509_tach_pulse_counter_proof.py).

## See also

- [`docs/hardware/s360-100-r4-core.md`](s360-100-r4-core.md) — per-pin /
  per-net Core reference; authoritative source for net / GPIO
  assignments.
- [`docs/hardware/s360-100-core-architecture.md`](s360-100-core-architecture.md) —
  canonical Core architecture index: central-hub framing,
  connector / module SKU matrix, native-GPIO pin-allocation table.
- [`docs/hardware/s360-100-native-fan-gpio-map.md`](s360-100-native-fan-gpio-map.md) —
  canonical S360-100 / S360-311 fan GPIO map; classifies the
  SX1509-routed fan path as legacy / superseded.
- [`docs/hardware/s360-100-native-tach-pulse-strategy.md`](s360-100-native-tach-pulse-strategy.md) —
  canonical architectural rule: native ESP32-S3 GPIO required for
  tach / pulse-counter inputs.
- [`docs/hardware/schematics/S360-100-R4.pdf`](schematics/S360-100-R4.pdf) —
  current canonical S360-100 Core schematic (SHA256
  `4c9e8b06d129fbb55f61e143b648e03762d06cb4dc67fe3120c268cd3a4bdf16`,
  837,443 bytes, KiCad E.D.A. 10.0.3, single sheet `1/1`).
- [`docs/sense360-room-bundles.md`](../sense360-room-bundles.md) —
  canonical PoE room bundle SKU matrix.
- [`docs/blocker-burndown.md`](../blocker-burndown.md) — blocker /
  scope-classification table (PWM-12 / HW-005 /
  PACKAGE-POE-410-001).
- [`tests/test_s360_100_core_connector_pin_map.py`](../../tests/test_s360_100_core_connector_pin_map.py) —
  guards for this document (canonical connector matrix present,
  every Sense360 module SKU covered, status-language vocabulary
  honoured, no tach signal mapped through an expander, do-not-change
  guardrails on Release-One / LED / FanPWM / FanTRIAC / PoE).

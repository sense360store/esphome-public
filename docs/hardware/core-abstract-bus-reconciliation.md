# Core Abstract Bus Reconciliation (CORE-ABSTRACT-BUS-001)

## Status

**Status: investigation merged; all three implementation slices
(`CORE-ABSTRACT-BUS-001A` / `B` / `C`) have landed at the substitution
layer.** `001C` landed in PR #557 (UART split, status LED move,
`pir_sensor_pin`, `comfort_ceiling_als_int_pin`, `expander_int_pin`,
`sx1509_interrupt_pin`). `001A` landed in PR #558 (`relay_pin → GPIO3`
across the five non-voice Core abstract packages). `001B` landed as the
hard rename to the canonical shared `core_i2c` bus id (`GPIO48` SDA /
`GPIO45` SCL / `400kHz`) across the seven in-scope Core abstract
packages, the 11 in-scope expansion-package `*_i2c_id` consumer
defaults, and the hard-coded literal in
[`packages/features/ceiling_halo_leds.yaml`](../../packages/features/ceiling_halo_leds.yaml).
The voice-variant Core `relay_pin: GPIO4` stays deliberately out of
scope (`001A` non-voice scope). The S3-variant Core
(`sense360_core_ceiling_s3.yaml` / `airiq_ceiling_s3.yaml` /
`comfort_ceiling_s3.yaml`) and the Mini family
(`sense360_core_mini.yaml` / `mini_onboard_sensors.yaml` / the six
`sense360-mini-*.yaml` products) stay deliberately out of scope
(`001B` operator decision #10). No WebFlash exposure or release
posture changes by any of the three slices.

This document is the **CORE-ABSTRACT-BUS-001** audit record. It
investigates the systemic disagreement between the Core package YAML
abstract substitutions (`relay_pin`, `halo_i2c`, `expansion_i2c`,
`uart_bus`, `status_led_pin`, `pir_sensor_pin`, `expansion_gpio1` /
`expansion_gpio2`, etc.) and the verified `S360-100-R4` Core schematic
captured in
[`docs/hardware/s360-100-r4-core.md`](s360-100-r4-core.md), classifies
every substitution against the schematic, and splits the implementation
work into three coordinated future PR slices so that no single slice
silently destabilizes Release-One.

It is the alias-doc for
[`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3](../release-one-hardware-audit.md#required-follow-ups)
and is consumed by
[`docs/hardware/package-readiness-matrix.md` Follow-up PR sequence `CORE-ABSTRACT-BUS-001` row](package-readiness-matrix.md#follow-up-pr-sequence)
and
[`docs/hardware/firmware-package-mapping-audit.md` Release-One product YAML package stack](firmware-package-mapping-audit.md#release-one-product-yaml-package-stack)
(HW-009 systemic Core-vs-schematic mismatch bullet).

This PR does **not** edit any package YAML, any product YAML, any
WebFlash wrapper, any JSON catalog, any script, any test, any
workflow, any component, any include, any firmware artifact, or any
manifest. It changes only this new document plus the existing
docs-only audit / matrix / tracker files cross-linked under
[§See also](#see-also).

## Purpose and scope

CORE-ABSTRACT-BUS-001 is the systemic rebind of the Core abstract
substitutions consumed by Release-One and by every downstream
fan-driver / RoomIQ / AirIQ / VentIQ / LED slice. The matrix entry at
[`docs/hardware/package-readiness-matrix.md` Follow-up PR sequence](package-readiness-matrix.md#follow-up-pr-sequence)
gates the work on three preconditions, none of which has landed:

1. **S360-100-BENCH-001 silkscreen verification** — pending; see
   [`docs/hardware/s360-100-r4-core.md` §S360-100-BENCH-001 status](s360-100-r4-core.md#s360-100-bench-001-status).
2. **RoomIQ / AirIQ / VentIQ package rebind plan** — not yet drafted.
3. **Re-validation pass for every non-Release-One product YAML** that
   consumes the affected Core abstract packages — not yet designed.

This audit, therefore, performs a docs-only inventory + slice
definition. It produces the implementation roadmap; it does not
execute it.

The PACKAGE-RELAY-001 deferral note in
[`docs/cleanup-audit.md` §PACKAGE-RELAY-001 update](../cleanup-audit.md#package-relay-001-update-deferred--core-abstract-bus-001--silkscreen--harness--k1-bom-evidence-not-landed)
already records that Relay package implementation is gated on this
audit landing. This audit confirms that gate stays closed and refines
the upstream dependency from "CORE-ABSTRACT-BUS-001" (generic) to
**CORE-ABSTRACT-BUS-001A** (the `relay_pin` slice specifically).

## Source of truth references

Schematic-backed:

- [`docs/hardware/s360-100-r4-core.md`](s360-100-r4-core.md) — Sense360
  Core (`S360-100-R4`) pin / net / connector reference. JSON
  `schematic_status: verified` under HW-008; PDF committed at
  [`docs/hardware/schematics/S360-100-R4.pdf`](schematics/S360-100-R4.pdf)
  under HW-007.
- [`docs/hardware/s360-200-r4-roomiq.md`](s360-200-r4-roomiq.md) —
  Sense360 RoomIQ (`S360-200-R4`).
- [`docs/hardware/s360-211-r4-ventiq.md`](s360-211-r4-ventiq.md) —
  Sense360 VentIQ (`S360-211-R4`).
- [`docs/hardware/s360-310-r4-relay.md`](s360-310-r4-relay.md) —
  Sense360 Relay (`S360-310-R4`); HW-PINMAP-310-FOLLOWUP audit `partial
  — schematic evidence available; package reconciliation pending`.

Companion audits:

- [`docs/release-one-hardware-audit.md`](../release-one-hardware-audit.md)
  — HW-004 release-readiness audit; this doc closes its Required
  follow-ups #2 / #3 only at the docs-only planning layer.
- [`docs/hardware/firmware-package-mapping-audit.md`](firmware-package-mapping-audit.md)
  — HW-009 firmware-package-mapping audit; the Release-One package
  stack entry (lines 372–445) enumerates the systemic mismatch but
  explicitly marks it out-of-scope for HW-009.
- [`docs/hardware/package-readiness-matrix.md`](package-readiness-matrix.md)
  — PACKAGE-GAP-001 readiness matrix; the `CORE-ABSTRACT-BUS-001`
  row (Follow-up PR sequence, line 830) names the dependency.

Package YAML inspected (not edited):

- [`packages/hardware/sense360_core.yaml`](../../packages/hardware/sense360_core.yaml)
- [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml)
- [`packages/hardware/sense360_core_ceiling_s3.yaml`](../../packages/hardware/sense360_core_ceiling_s3.yaml)
- [`packages/hardware/sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml)
- [`packages/hardware/sense360_core_poe.yaml`](../../packages/hardware/sense360_core_poe.yaml)
- [`packages/hardware/sense360_core_wall.yaml`](../../packages/hardware/sense360_core_wall.yaml)
- [`packages/expansions/comfort_ceiling.yaml`](../../packages/expansions/comfort_ceiling.yaml)
- [`packages/expansions/comfort_ceiling_s3.yaml`](../../packages/expansions/comfort_ceiling_s3.yaml)
- [`packages/expansions/gpio_expander_sx1509.yaml`](../../packages/expansions/gpio_expander_sx1509.yaml)
- [`packages/expansions/fan_relay.yaml`](../../packages/expansions/fan_relay.yaml)

## Core abstract substitution inventory

Every Core abstract substitution defined under
[`packages/hardware/`](../../packages/hardware/), captured verbatim
from the package YAML it lives in. "Schematic value" is the
`S360-100-R4` net source per
[`docs/hardware/s360-100-r4-core.md` §ESP32-S3 pin and net mapping](s360-100-r4-core.md#esp32-s3-pin-and-net-mapping)
(lines 85–122). "Verdict" classifies the disagreement.

Verdict vocabulary:

- `schematic-backed-correct` — substitution value matches the
  schematic net source for the function it names.
- `schematic-backed-conflict` — substitution value points at a GPIO
  that the schematic uses for a different signal.
- `unverified` — substitution value cannot be checked against
  committed schematic evidence (the board is not yet verified or the
  function is not directly bound by the schematic).
- `out-of-scope` — substitution belongs to a different board family
  (e.g. Core Mini, Core PoE Ethernet) and is not part of the
  Release-One blast radius.

### relay_pin

| File | Line | Value | Schematic net | Verdict | Notes |
|---|---|---|---|---|---|
| [`packages/hardware/sense360_core.yaml`](../../packages/hardware/sense360_core.yaml) | 63 | `GPIO10` | `IO10` label not legible per [§ESP32-S3 pin and net mapping](s360-100-r4-core.md#esp32-s3-pin-and-net-mapping) line 103; `Relay` net is on `IO3` per same table line 100 | `schematic-backed-conflict` | Generic-Core baseline; legacy value |
| [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml) | 61 | `GPIO4` | `IO4 = SEN0609_RX` (RoomIQ J10 radar UART RX) per [§ESP32-S3 pin and net mapping](s360-100-r4-core.md#esp32-s3-pin-and-net-mapping) line 89 | `schematic-backed-conflict` | Consumed by Release-One via [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq.yaml) line 116 |
| [`packages/hardware/sense360_core_ceiling_s3.yaml`](../../packages/hardware/sense360_core_ceiling_s3.yaml) | — | not defined | n/a | `out-of-scope` | Ceiling S3 variant does not expose `relay_pin`; no `main_relay` switch in this file |
| [`packages/hardware/sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml) | 47 | `GPIO10` | `Relay = IO3` per Core schematic | `schematic-backed-conflict` | Companion / mapping board variant |
| [`packages/hardware/sense360_core_poe.yaml`](../../packages/hardware/sense360_core_poe.yaml) | 76 | `GPIO10` | `Relay = IO3` per Core schematic | `schematic-backed-conflict` | Consumed by [`products/sense360-poe.yaml`](../../products/sense360-poe.yaml) |
| [`packages/hardware/sense360_core_wall.yaml`](../../packages/hardware/sense360_core_wall.yaml) | 65 | `GPIO4` | `IO4 = SEN0609_RX` per Core schematic | `schematic-backed-conflict` | Wall-mount variant |

Schematic ground truth:
[`docs/hardware/s360-100-r4-core.md`](s360-100-r4-core.md) line 100 —
`| IO3 | Relay | J4 Relay module gate |` — and §J4 Relay module
connector (3-pin), pin 2 — `| 2 | Relay | Drive signal from ESP32 IO3 |`.

### I²C bus substitutions

`S360-100-R4` schematic exposes a **single shared I²C bus** on `IO48`
(SDA) / `IO45` (SCL), pulled up by R22 / R21 (10 kΩ); see
[`docs/hardware/s360-100-r4-core.md` lines 110–111](s360-100-r4-core.md#esp32-s3-pin-and-net-mapping).
Multiple Core packages still define one or two separate I²C buses on
GPIOs that do not match this single shared bus.

| File | Lines | Bus id | SDA value | SCL value | Schematic match | Verdict |
|---|---|---|---|---|---|---|
| [`packages/hardware/sense360_core.yaml`](../../packages/hardware/sense360_core.yaml) | 46–49, 100–112 | `i2c0` | `GPIO39` | `GPIO40` | None — `IO39`/`IO40` are JTAG / peripheral test-point territory per [§ESP32-S3 pin and net mapping](s360-100-r4-core.md#esp32-s3-pin-and-net-mapping) lines 115–116 | `schematic-backed-conflict` |
| [`packages/hardware/sense360_core.yaml`](../../packages/hardware/sense360_core.yaml) | 48–49, 107–112 | `i2c1` | `GPIO21` | `GPIO18` | `IO21 = FAN` (J13) per line 108; `IO18 = RST1` per line 97 | `schematic-backed-conflict` |
| [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml) | 50–53, 104–117 | `halo_i2c` | `GPIO39` | `GPIO40` | None | `schematic-backed-conflict` |
| [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml) | 52–53, 112–117 | `expansion_i2c` | `GPIO21` | `GPIO18` | `IO21 = FAN`, `IO18 = RST1` | `schematic-backed-conflict` |
| [`packages/hardware/sense360_core_ceiling_s3.yaml`](../../packages/hardware/sense360_core_ceiling_s3.yaml) | 102–104, 203–208 | `i2c_primary` | `GPIO17` | `GPIO18` | None — `IO17 = expander_int` per line 96, `IO18 = RST1` per line 97 | `out-of-scope` (different board layout per header lines 1–95) |
| [`packages/hardware/sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml) | 22–29, 93–104 | `i2c_primary` | `GPIO39` | `GPIO40` | None | `schematic-backed-conflict` |
| [`packages/hardware/sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml) | 27–29, 100–104 | `i2c_expander` | `GPIO21` | `GPIO18` | `IO21 = FAN`, `IO18 = RST1` | `schematic-backed-conflict` |
| [`packages/hardware/sense360_core_poe.yaml`](../../packages/hardware/sense360_core_poe.yaml) | 59–62, 124–137 | `i2c0` | `GPIO39` | `GPIO40` | None | `schematic-backed-conflict` |
| [`packages/hardware/sense360_core_poe.yaml`](../../packages/hardware/sense360_core_poe.yaml) | 61–62, 132–137 | `i2c1` | `GPIO21` | `GPIO18` | None | `schematic-backed-conflict` |
| [`packages/hardware/sense360_core_wall.yaml`](../../packages/hardware/sense360_core_wall.yaml) | 54–57, 114–127 | `i2c0` | `GPIO39` | `GPIO40` | None | `schematic-backed-conflict` |
| [`packages/hardware/sense360_core_wall.yaml`](../../packages/hardware/sense360_core_wall.yaml) | 56–57, 122–127 | `i2c1` | `GPIO21` | `GPIO18` | None | `schematic-backed-conflict` |

Bus-id naming also diverges across the Core packages (`i2c0` /
`i2c1` / `halo_i2c` / `expansion_i2c` / `i2c_primary` / `i2c_expander`),
which means every downstream expansion package that references an
I²C bus has to know which Core package it is being included into.
[`packages/expansions/comfort.yaml`](../../packages/expansions/comfort.yaml)
and the AirIQ / VentIQ / DAC / SX1509-expander packages each carry
their own `*_i2c_id` substitution defaulting to one of these names;
this coupling has to be resolved as part of slice **001B**.

### UART bus substitutions

`S360-100-R4` schematic exposes two distinct ESP32 UARTs used by
RoomIQ:

- `Hi-Link_RX / Hi-Link_TX` on `IO1` / `IO2` (RoomIQ J10 Hi-Link radar
  UART) per [§ESP32-S3 pin and net mapping](s360-100-r4-core.md#esp32-s3-pin-and-net-mapping)
  lines 121–122.
- `SEN0609_RX / SEN0609_TX` on `IO4` / `IO5` (RoomIQ J10 DFRobot SEN0609
  radar UART) per lines 89–90.

Plus the on-board USB-UART on `TXD0 / RXD0` (pin 37 / pin 36; J7
GP8403 fan UART per lines 119–120). None of the existing Core
packages models this two-radar-UART split.

| File | Lines | Bus id | TX pin | RX pin | Baud | Schematic match | Verdict |
|---|---|---|---|---|---|---|---|
| [`packages/hardware/sense360_core.yaml`](../../packages/hardware/sense360_core.yaml) | 52–54, 115–119 | `uart_bus` | `GPIO1` | `GPIO2` | `115200` | `IO1 = Hi-Link_RX`, `IO2 = Hi-Link_TX` per Core schematic — RoomIQ-specific, not generic | `schematic-backed-conflict` (directionality also inverted relative to schematic) |
| [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml) | 56–58, 120–124 | `uart_bus` | `GPIO1` | `GPIO2` | `256000` | Same Hi-Link nets | `schematic-backed-conflict` |
| [`packages/hardware/sense360_core_ceiling_s3.yaml`](../../packages/hardware/sense360_core_ceiling_s3.yaml) | 109–117, 213–219 | `uart_presence` (incl. `_hilink_*` / `_sen0609_*` alt) | `GPIO38` / `GPIO4` | `GPIO39` / `GPIO5` | `256000` / `115200` | None for Core; appears to target the S3-variant board layout per header lines 1–95 | `out-of-scope` |
| [`packages/hardware/sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml) | 32–39, 106–119 | `uart_presence` + `uart_auxiliary` | `GPIO1` / `GPIO43` | `GPIO2` / `GPIO44` | `256000` / `115200` | Hi-Link nets for presence; auxiliary not on schematic | `schematic-backed-conflict` (presence); `unverified` (auxiliary) |
| [`packages/hardware/sense360_core_poe.yaml`](../../packages/hardware/sense360_core_poe.yaml) | 65–67, 140–144 | `uart_bus` | `GPIO1` | `GPIO2` | `115200` | Hi-Link nets | `schematic-backed-conflict` |
| [`packages/hardware/sense360_core_wall.yaml`](../../packages/hardware/sense360_core_wall.yaml) | 60–62, 130–134 | `uart_bus` | `GPIO1` | `GPIO2` | `115200` | Hi-Link nets | `schematic-backed-conflict` |

### Status LED substitutions

`S360-100-R4` schematic shows three distinct LED-adjacent nets, all on
the Core side rather than on a dedicated status-LED net:

- `IO38 = LED_DATA` → buffered `LED_DATA_3V3` → J3 WS2812B LED
  connector (line 114). This is the canonical halo LED data line; see
  [`docs/hardware/firmware-package-mapping-audit.md` §LED_DATA / Sense360 LED](firmware-package-mapping-audit.md#led_data--sense360-led)
  for the HW-010 reconciliation.
- `IO7 = AirQ_Status_Led` → J9 AirIQ status LED (line 92).
- `IO46 = GP_Fan_Status_Led` → indicator LED (line 101).
- `IO48 = I2C_SDA` — **claimed by the shared I²C bus**, not by any
  status LED (line 110).

| File | Line | Substitution | Value | Schematic net at that GPIO | Verdict |
|---|---|---|---|---|---|
| [`packages/hardware/sense360_core.yaml`](../../packages/hardware/sense360_core.yaml) | 66 | `status_led_rgb_pin` | `GPIO48` | `I2C_SDA` (shared bus) | `schematic-backed-conflict` |
| [`packages/hardware/sense360_core.yaml`](../../packages/hardware/sense360_core.yaml) | 67 | `status_led_pin` | `GPIO2` | `Hi-Link_TX` (RoomIQ J10 UART TX) | `schematic-backed-conflict` |
| [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml) | 76 | `status_led_pin` | `GPIO48` | `I2C_SDA` | `schematic-backed-conflict` |
| [`packages/hardware/sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml) | 48 | `status_led_rgb_pin` | `GPIO48` | `I2C_SDA` | `schematic-backed-conflict` |
| [`packages/hardware/sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml) | 49 | `status_led_simple_pin` | `GPIO47` | `ALS_INT` (RoomIQ ambient-light interrupt) | `schematic-backed-conflict` |
| [`packages/hardware/sense360_core_poe.yaml`](../../packages/hardware/sense360_core_poe.yaml) | 79 | `status_led_pin` | `GPIO8` | `AirQ_Led` (J9 AirIQ LED) | `schematic-backed-conflict` |
| [`packages/hardware/sense360_core_wall.yaml`](../../packages/hardware/sense360_core_wall.yaml) | 79 | `status_led_rgb_pin` | `GPIO48` | `I2C_SDA` | `schematic-backed-conflict` |
| [`packages/hardware/sense360_core_wall.yaml`](../../packages/hardware/sense360_core_wall.yaml) | 80 | `status_led_pin` | `GPIO47` | `ALS_INT` | `schematic-backed-conflict` |

### PIR substitution

`S360-100-R4` schematic places PIR on `IO15 = PIR` per
[§ESP32-S3 pin and net mapping](s360-100-r4-core.md#esp32-s3-pin-and-net-mapping)
line 94 (RoomIQ J10 PIR motion input).

| File | Line | Substitution | Value | Schematic net | Verdict |
|---|---|---|---|---|---|
| [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml) | 77 | `pir_sensor_pin` | `GPIO47` | `ALS_INT` (not PIR) | `schematic-backed-conflict` |

(No other Core package defines `pir_sensor_pin` today.)

### Expansion GPIO substitutions

`S360-100-R4` does not expose a generic "expansion GPIO" header. Most
free / expander-bound GPIOs are already named on the schematic. The
abstract `expansion_gpio1..4` substitutions therefore have to be
re-mapped against schematic nets one-by-one — not by picking the next
unused integer.

| File | Lines | Substitution | Value | Schematic net at that GPIO | Verdict |
|---|---|---|---|---|---|
| [`packages/hardware/sense360_core.yaml`](../../packages/hardware/sense360_core.yaml) | 57–60 | `expansion_gpio1..4` | `GPIO4..GPIO7` | `IO4 = SEN0609_RX`, `IO5 = SEN0609_TX`, `IO6 = out(gpio6)`, `IO7 = AirQ_Status_Led` | `schematic-backed-conflict` |
| [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml) | 65–68 | `expansion_gpio1..4` | `GPIO5..GPIO8` | `IO5 = SEN0609_TX`, `IO6 = out(gpio6)`, `IO7 = AirQ_Status_Led`, `IO8 = AirQ_Led` | `schematic-backed-conflict` |
| [`packages/hardware/sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml) | 57–59 | `expansion_gpio1..3` | `GPIO6..GPIO8` | `IO6 = out(gpio6)`, `IO7 = AirQ_Status_Led`, `IO8 = AirQ_Led` | `schematic-backed-conflict` |
| [`packages/hardware/sense360_core_poe.yaml`](../../packages/hardware/sense360_core_poe.yaml) | 70–73 | `expansion_gpio1..4` | `GPIO4..GPIO7` | RoomIQ-claimed nets | `schematic-backed-conflict` |
| [`packages/hardware/sense360_core_wall.yaml`](../../packages/hardware/sense360_core_wall.yaml) | 69–72 | `expansion_gpio1..4` | `GPIO5..GPIO8` | RoomIQ-claimed nets | `schematic-backed-conflict` |

Downstream effect: [`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml)
binds `fan_pwm_pin: ${expansion_gpio1}` and `fan_tach_pin: ${expansion_gpio2}`,
so on a Release-One-style stack today those resolve to RoomIQ-claimed
GPIOs. Captured separately in
[`docs/hardware/s360-311-r4-pwm.md`](s360-311-r4-pwm.md)
(HW-PINMAP-311-FOLLOWUP), owned by `PACKAGE-PWM-001` once that
audit has the evidence to proceed.

## GPIO collision matrix

This matrix is the central reason the relay slice cannot land in
isolation. Several different abstract substitutions across different
packages claim the same physical GPIO numbers, and the schematic ground
truth makes those claims internally contradictory. The collisions
discovered during this audit:

| GPIO | Schematic net (S360-100-R4) | Existing substitution claims | Collision class |
|---|---|---|---|
| `GPIO1` | `Hi-Link_RX` (RoomIQ J10) | `uart_tx_pin` in Core / Ceiling / Wall / PoE / Mapping (5 files) | direction inversion + misuse as generic UART |
| `GPIO2` | `Hi-Link_TX` (RoomIQ J10) | `uart_rx_pin` in 5 Core packages; `status_led_pin` in [`sense360_core.yaml`](../../packages/hardware/sense360_core.yaml) line 67 | direction inversion + LED-vs-UART collision |
| **`GPIO3`** | **`Relay` (J4 Relay module gate)** | `comfort_ceiling_als_int_pin` in [`comfort_ceiling.yaml`](../../packages/expansions/comfort_ceiling.yaml) line 42; `comfort_als_int_pin` in [`comfort_ceiling_s3.yaml`](../../packages/expansions/comfort_ceiling_s3.yaml) line 29 and [`sense360_core_ceiling_s3.yaml`](../../packages/hardware/sense360_core_ceiling_s3.yaml) line 140; `expander_int_pin` in [`sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml) line 54; `sx1509_interrupt_pin` in [`gpio_expander_sx1509.yaml`](../../packages/expansions/gpio_expander_sx1509.yaml) line 17 | **Blocks the relay slice from landing in isolation** — the schematic-correct `relay_pin: GPIO3` collides with the existing ALS-INT / expander-INT bindings inside Release-One via [`comfort_ceiling.yaml`](../../packages/expansions/comfort_ceiling.yaml) (consumed at [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq.yaml) line 140) |
| `GPIO4` | `SEN0609_RX` (RoomIQ J10) | `relay_pin` in [`sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml) line 61 and [`sense360_core_wall.yaml`](../../packages/hardware/sense360_core_wall.yaml) line 65; `expansion_gpio1` in [`sense360_core.yaml`](../../packages/hardware/sense360_core.yaml) line 57 and [`sense360_core_poe.yaml`](../../packages/hardware/sense360_core_poe.yaml) line 70; `fan_pwm_pin` in [`sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml) line 42 | relay-vs-radar-RX collision + expansion-vs-radar-RX collision |
| `GPIO5` | `SEN0609_TX` (RoomIQ J10) | `expansion_gpio1` in ceiling / wall; `expansion_gpio2` in core / PoE; `fan_tach_pin` in mapping line 43 | expansion-vs-radar-TX collision; also the FanTRIAC `fan_triac_gate_pin` placeholder in [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml) (HW-005 blocker) |
| `GPIO6` | `out(gpio6)` (RoomIQ J10 auxiliary) | `expansion_gpio2` in ceiling / wall; `expansion_gpio3` in core / PoE; `expansion_gpio1` in mapping line 57 | expansion-vs-RoomIQ-aux collision; also the FanTRIAC `fan_triac_zc_pin` placeholder (HW-005) |
| `GPIO15` | `PIR` (RoomIQ J10 motion input) | `w5500_int_pin` in [`sense360_core_poe.yaml`](../../packages/hardware/sense360_core_poe.yaml) line 55 | PIR-vs-Ethernet-INT collision (different boards but same Core abstract namespace) |
| `GPIO47` | `ALS_INT` (RoomIQ J10 ambient-light-sensor interrupt) | `pir_sensor_pin` in [`sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml) line 77; `status_led_simple_pin` in [`sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml) line 49; `status_led_pin` in [`sense360_core_wall.yaml`](../../packages/hardware/sense360_core_wall.yaml) line 80 | PIR-vs-ALS-INT swap + LED-vs-ALS-INT collisions |
| `GPIO48` | `I2C_SDA` (shared I²C bus) | `status_led_pin` in [`sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml) line 76; `status_led_rgb_pin` in [`sense360_core.yaml`](../../packages/hardware/sense360_core.yaml) / [`sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml) / [`sense360_core_wall.yaml`](../../packages/hardware/sense360_core_wall.yaml) | LED-vs-I²C-SDA collision; landing slice **001B** (shared-I²C-bus consolidation) frees this GPIO of the LED claim |
| `GPIO38` | `LED_DATA` → J3 WS2812B | `uart_hilink_tx_pin` in [`sense360_core_ceiling_s3.yaml`](../../packages/hardware/sense360_core_ceiling_s3.yaml) line 110 | LED-vs-UART collision (S3 variant — out of Release-One scope but recorded for future S3-board rebind) |

The `GPIO3` row is the operative one for the relay slice: the
schematic-correct value for `relay_pin` is `GPIO3`, but `GPIO3` is
also currently the abstract binding for ALS_INT inside the
comfort-ceiling package that Release-One includes. Without first
rebinding `comfort_ceiling_als_int_pin: GPIO3 → GPIO47` (schematic
ALS_INT net) — which is slice **001C** — the relay slice would
produce a binary in which two different ESPHome components try to own
the same ESP32 pin.

## Implementation slice definitions

### CORE-ABSTRACT-BUS-001A — `relay_pin` slice

**Scope.** Rebind `relay_pin` to `GPIO3` in every Core abstract package
that currently exposes it: [`sense360_core.yaml`](../../packages/hardware/sense360_core.yaml)
line 63 (`GPIO10 → GPIO3`),
[`sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml)
line 61 (`GPIO4 → GPIO3`),
[`sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml)
line 47 (`GPIO10 → GPIO3`),
[`sense360_core_poe.yaml`](../../packages/hardware/sense360_core_poe.yaml)
line 76 (`GPIO10 → GPIO3`), and
[`sense360_core_wall.yaml`](../../packages/hardware/sense360_core_wall.yaml)
line 65 (`GPIO4 → GPIO3`).

**Hard preconditions (none satisfied today).**

1. Slice **001C** must land first (or as part of the same PR) so that
   `comfort_ceiling_als_int_pin: GPIO3` no longer collides with
   `relay_pin: GPIO3` in any Release-One stack. See
   [§GPIO collision matrix](#gpio-collision-matrix) row `GPIO3`.
2. **S360-100-BENCH-001 silkscreen evidence** must land confirming
   Core-side `J4` pin-1 orientation and the Core-to-relay-module
   harness identity. See
   [`docs/hardware/s360-100-r4-core.md` §S360-100-BENCH-001 status](s360-100-r4-core.md#s360-100-bench-001-status)
   and
   [`docs/hardware/s360-310-r4-relay.md` Required evidence before promotion](s360-310-r4-relay.md#required-evidence-before-promotion).
3. **GPIO3 strap-pin boot behaviour** must be characterised against a
   populated `S360-310-R4` + `S360-100-R4` pair. On ESP32-S3, `GPIO3`
   is a JTAG-select strap pin; the relay module's `Q1` MMBT3904 NPN
   low-side topology and `K1` mechanical relay coil arrangement
   (recorded in
   [`docs/hardware/artifacts/S360-310-R4.md`](artifacts/S360-310-R4.md)
   and
   [`docs/hardware/s360-310-r4-relay.md` Reconciliation findings](s360-310-r4-relay.md#reconciliation-findings))
   suggests `RESTORE_DEFAULT_OFF` keeps the strap in a benign state at
   boot, but this must be verified, not assumed.
4. `K1` BOM identity, contact-current rating, and harness identity
   must be on file — same evidence already listed for
   `HW-PINMAP-310-FOLLOWUP` and `PACKAGE-RELAY-001`. See
   [`docs/cleanup-audit.md` §PACKAGE-RELAY-001 update](../cleanup-audit.md#package-relay-001-update-deferred--core-abstract-bus-001--silkscreen--harness--k1-bom-evidence-not-landed)
   for the full list.
5. A new pin-pinning test (modeled on
   [`tests/test_led_package_mapping.py`](../../tests/test_led_package_mapping.py))
   that asserts the new `relay_pin` value across every Core abstract
   package must land in the same PR.

**Blast radius.** Every product YAML listed under
[§Blast radius per Core package](#blast-radius-per-core-package) for
`sense360_core_ceiling.yaml`, `sense360_core.yaml`,
`sense360_core_mapping.yaml`, `sense360_core_poe.yaml`, and
`sense360_core_wall.yaml`. In particular, Release-One
([`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq.yaml))
re-builds because the `main_relay` switch in
[`sense360_core_ceiling.yaml` lines 132–143](../../packages/hardware/sense360_core_ceiling.yaml)
binds `pin: ${relay_pin}`. The change is intentionally semantic-only
(the relay still exists as an entity), but the binary differs
byte-by-byte and the Release-One re-validation pass under
[§Validation plan for implementation slices](#validation-plan-for-implementation-slices)
has to run before the artifact is re-published.

### CORE-ABSTRACT-BUS-001B — Shared-I²C-bus consolidation slice

**Scope.** Collapse the duplicated `halo_i2c` / `expansion_i2c` /
`i2c0` / `i2c1` / `i2c_primary` / `i2c_expander` bus definitions in
[`sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml),
[`sense360_core.yaml`](../../packages/hardware/sense360_core.yaml),
[`sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml),
[`sense360_core_poe.yaml`](../../packages/hardware/sense360_core_poe.yaml),
and [`sense360_core_wall.yaml`](../../packages/hardware/sense360_core_wall.yaml)
down to the **single shared I²C bus** on `IO48` (SDA) / `IO45` (SCL)
that the schematic actually has. Decide a canonical bus id (likely
`shared_i2c` or `core_i2c`, but to be determined by the rebind PR) and
align every downstream package that currently references one of the
old names — `airiq.yaml`, `airiq_bathroom_base.yaml`, `airiq_ceiling.yaml`,
`airiq_wall.yaml`, `comfort.yaml`, `comfort_ceiling.yaml`,
`comfort_wall.yaml`, `fan_gp8403.yaml`, `gpio_expander_sx1509.yaml`,
`presence_*.yaml`, and the matching feature profiles.

**Hard preconditions (none satisfied today).**

1. A complete downstream-consumer audit: every package YAML, every
   product YAML, and every feature YAML that resolves an `*_i2c_id`
   substitution. Without it the rename will break parse-time
   substitution resolution in some product.
2. A canonical I²C bus id naming decision recorded in
   [`docs/hardware/firmware-package-mapping-audit.md`](firmware-package-mapping-audit.md)
   or a sibling doc. Today the matrix entry at
   [`docs/hardware/package-readiness-matrix.md` line 830](package-readiness-matrix.md#follow-up-pr-sequence)
   does not name a canonical id.
3. A pin-pinning test that asserts the I²C SDA / SCL values across
   every Core abstract package.
4. Re-validation of every non-Release-One product YAML — this slice
   touches more packages than 001A and the blast radius is larger.

**Scope-extension addendum (2026-05-19, recorded by the `001B`
investigation pass — see [§2026-05-19 — CORE-ABSTRACT-BUS-001B
investigation pass](#2026-05-19--core-abstract-bus-001b-investigation-pass-deferred-preconditions-still-open)
below).** Two Core packages that mirror the same conflicting dual-bus
definitions were missed when the slice scope was originally drafted
and must be included in the eventual `001B` implementation slice:

- [`packages/hardware/sense360_core_voice_ceiling.yaml`](../../packages/hardware/sense360_core_voice_ceiling.yaml)
  lines 113–124 — defines `halo_i2c` (`GPIO39` / `GPIO40`) plus
  `expansion_i2c` (`GPIO21` / `GPIO18`), identical to the ceiling
  variant.
- [`packages/hardware/sense360_core_voice_wall.yaml`](../../packages/hardware/sense360_core_voice_wall.yaml)
  lines 134–143 — defines `i2c0` (`GPIO39` / `GPIO40`) plus
  `i2c1` (`GPIO21` / `GPIO18`), identical to the wall variant.

In addition,
[`packages/features/ceiling_halo_leds.yaml`](../../packages/features/ceiling_halo_leds.yaml)
line 6 hard-codes `i2c_id: halo_i2c` and currently has no product
`!include`r, so the eventual `001B` PR must either rebind that
literal to the canonical bus id or document the feature as dead
code.
[`packages/hardware/sense360_core_ceiling_s3.yaml`](../../packages/hardware/sense360_core_ceiling_s3.yaml)
(`i2c_primary` on `GPIO17` / `GPIO18`) and
[`packages/hardware/sense360_core_mini.yaml`](../../packages/hardware/sense360_core_mini.yaml)
(`i2c0` already on the schematic-correct `GPIO48` / `GPIO45` via
[`packages/hardware/mini_onboard_sensors.yaml`](../../packages/hardware/mini_onboard_sensors.yaml))
remain out-of-scope per their separate board lineage.

### CORE-ABSTRACT-BUS-001C — UART / status LED / PIR / expansion GPIO slice

**Scope.** This is the largest slice and the one that has to land
first if `001A` is to land safely. It contains:

- **UART split.** Replace the single `uart_bus` definition in the
  Core packages with two named buses: `roomiq_hi_link_uart` on
  `IO1 (TX) / IO2 (RX)` and `roomiq_sen0609_uart` on `IO4 (TX) /
  IO5 (RX)` (note the schematic naming has the RX/TX direction
  reversed relative to the abstract substitutions; see
  [§UART bus substitutions](#uart-bus-substitutions)). Update every
  downstream presence / radar package that currently references
  `uart_bus` — at minimum `presence_ceiling.yaml`,
  `presence_wall.yaml`, `presence_ld2412.yaml`,
  `presence_ld2450.yaml`, `presence_module_ceiling.yaml`.
- **Status LED.** Move `status_led_pin` off `GPIO48` (claimed by the
  shared I²C bus per slice 001B) to `IO46 = GP_Fan_Status_Led` or
  `IO7 = AirQ_Status_Led` depending on the board variant. The
  Ceiling Core, Wall Core, and Mapping Core entries each need their
  own decision because the schematic only has the two status-LED
  nets above plus the WS2812B halo data line on `IO38`.
- **PIR.** Rebind `pir_sensor_pin` in
  [`sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml)
  line 77 from `GPIO47` to `GPIO15`. The schematic line 94 reads
  `IO15 = PIR (RoomIQ J10 PIR motion input)`.
- **ALS_INT (frees GPIO3 for the relay slice).** Rebind
  `comfort_ceiling_als_int_pin` in
  [`comfort_ceiling.yaml`](../../packages/expansions/comfort_ceiling.yaml)
  line 42 from `GPIO3` to `GPIO47`. The schematic line 109 reads
  `IO47 = ALS_INT (RoomIQ J10 ambient-light-sensor interrupt)`. This
  also fixes the `GPIO47` collision with `pir_sensor_pin`. The
  matching `expander_int_pin` in
  [`sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml)
  line 54 and `sx1509_interrupt_pin` in
  [`gpio_expander_sx1509.yaml`](../../packages/expansions/gpio_expander_sx1509.yaml)
  line 17 must each be rebound to a schematic-backed value (the SX1509
  `INT` is on `IO17 = expander_int` per Core schematic line 96 — so
  `expander_int_pin: GPIO3 → GPIO17` in mapping, and
  `sx1509_interrupt_pin: GPIO3 → GPIO17` in the SX1509 expansion
  package).
- **Expansion GPIO.** Rebind `expansion_gpio1..4` in every Core
  package to schematic-free pins. **Open evidence requirement.** The
  schematic does not currently document a generic "expansion GPIO"
  header; this requires either (a) bench evidence that specific pins
  are routed to the expansion connector and have no schematic-named
  function, or (b) a documented decision to retire the
  `expansion_gpio*` abstraction in favour of explicit
  function-named substitutions (e.g. `fan_pwm_pin`, `fan_tach_pin`)
  bound to schematic nets. Downstream consumers
  ([`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml),
  [`packages/expansions/fan_relay.yaml`](../../packages/expansions/fan_relay.yaml)
  override hook on line 25) have to be updated accordingly.

**Hard preconditions (none satisfied today).**

1. S360-100-BENCH-001 silkscreen evidence (same as 001A) confirming
   the J10 RoomIQ connector pin order so the UART RX/TX direction
   reconciliation is unambiguous. Also resolves the Core J10 vs
   RoomIQ J6 pin-order discrepancy flagged in
   [`docs/release-one-hardware-audit.md` Findings → Core / RoomIQ connector](../release-one-hardware-audit.md#findings)
   (table row "Core / RoomIQ connector").
2. RoomIQ package rebind plan (`comfort_ceiling.yaml` /
   `presence_ceiling.yaml` rebound to actual schematic nets, not the
   current abstract names).
3. AirIQ / VentIQ package rebind decision — the AirIQ J9 indicator
   lines (`IO7 = AirQ_Status_Led`, `IO8 = AirQ_Led`) carry legacy
   names that VentIQ may or may not reuse; documented in
   [`docs/hardware/firmware-package-mapping-audit.md` §VentIQ J9 / `AirQ_Led` / `AirQ_Status_Led`](firmware-package-mapping-audit.md#ventiq-j9--airq_led--airq_status_led).
4. Pin-pinning test coverage for every rebound substitution in this
   slice.
5. Re-validation of every non-Release-One product YAML consuming
   any affected Core package.

## Inter-slice dependency graph

```text
S360-100-BENCH-001 (silkscreen evidence) ─┐
                                           │
RoomIQ rebind plan ────────────────────────┤
AirIQ / VentIQ rebind plan ────────────────┤
expansion-GPIO bench evidence ─────────────┤
                                           ▼
                                    CORE-ABSTRACT-BUS-001C
                                    (UART + status + PIR
                                     + ALS_INT + expansion GPIO)
                                           │
                                           ▼
                                    CORE-ABSTRACT-BUS-001A
                                    (relay_pin → GPIO3)
                                           │
                                           ▼
                                    PACKAGE-RELAY-001
                                    (fan_relay.yaml reconciliation)
                                           │
                                           ▼
                                    PRODUCT-RELAY-001
                                    WEBFLASH-RELAY-001
                                    RELEASE-RELAY-001
                                    WF-IMPORT-RELAY-001

CORE-ABSTRACT-BUS-001B
(I²C bus consolidation) — independent of 001A / 001C ordering
but should land before PACKAGE-PWM-001 / PACKAGE-DAC-001 to avoid
re-doing the downstream `*_i2c_id` substitution rewrite twice.
```

001A and 001C may also be combined into a single PR if the operator
chooses, provided the same precondition / test / re-validation
requirements are met. They are listed separately because the relay
slice is the narrowest tractable unit and may be the first to attract
implementation effort.

## Blast radius per Core package

Maps each Core abstract package to the product YAMLs that `!include`
it (verified via `grep -RIln "<package_basename>\\.yaml" products/`).
Any slice that edits a given Core package re-builds every listed
product and requires those products to be re-validated against
`tests/test_product_substitutions.py`, `tests/validate_configs.py`,
and the WebFlash / catalog / release tests listed under
[§Validation plan for implementation slices](#validation-plan-for-implementation-slices).

### `sense360_core_ceiling.yaml` (Release-One Core)

- [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq.yaml)
  — **Release-One production** (`Ceiling-POE-VentIQ-RoomIQ`,
  `v1.0.0-stable`).
- [`products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq-led.yaml)
  — LED preview (`Ceiling-POE-VentIQ-RoomIQ-LED`, `v1.0.0-preview`).
- [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml)
  — FanTRIAC blocked-reference (HW-005; not in WebFlash build matrix).
- [`products/sense360-core-ceiling.yaml`](../../products/sense360-core-ceiling.yaml)
- [`products/sense360-core-ceiling-bathroom.yaml`](../../products/sense360-core-ceiling-bathroom.yaml)
- [`products/sense360-core-ceiling-presence.yaml`](../../products/sense360-core-ceiling-presence.yaml)
- [`products/sense360-core-c-poe.yaml`](../../products/sense360-core-c-poe.yaml)
- [`products/sense360-core-c-pwr.yaml`](../../products/sense360-core-c-pwr.yaml)
- [`products/sense360-core-c-usb.yaml`](../../products/sense360-core-c-usb.yaml)

### `sense360_core.yaml` (generic Core baseline)

No `!include`s discovered in `products/` — this file is referenced by
the matrix doc and by the audit notes but does not appear in any
current product YAML composition. Confirm before editing: a slice
that edits `sense360_core.yaml` only has to ensure no future product
YAML adds an `!include` for it.

### `sense360_core_wall.yaml`

- [`products/sense360-core-wall.yaml`](../../products/sense360-core-wall.yaml)
- [`products/sense360-core-wall-presence.yaml`](../../products/sense360-core-wall-presence.yaml)
- [`products/sense360-core-w-poe.yaml`](../../products/sense360-core-w-poe.yaml)
- [`products/sense360-core-w-pwr.yaml`](../../products/sense360-core-w-pwr.yaml)
- [`products/sense360-core-w-usb.yaml`](../../products/sense360-core-w-usb.yaml)

### `sense360_core_voice_ceiling.yaml`

- [`products/sense360-core-voice-ceiling.yaml`](../../products/sense360-core-voice-ceiling.yaml)
- [`products/sense360-core-v-c-poe.yaml`](../../products/sense360-core-v-c-poe.yaml)
- [`products/sense360-core-v-c-pwr.yaml`](../../products/sense360-core-v-c-pwr.yaml)
- [`products/sense360-core-v-c-usb.yaml`](../../products/sense360-core-v-c-usb.yaml)

This package was not directly inspected in the substitution inventory
above (it carries its own `_voice_` variant of the substitutions).
Any slice that touches the Ceiling Core abstractions should mirror
the equivalent voice-ceiling change here.

### `sense360_core_voice_wall.yaml`

- [`products/sense360-core-voice-wall.yaml`](../../products/sense360-core-voice-wall.yaml)
- [`products/sense360-core-v-w-poe.yaml`](../../products/sense360-core-v-w-poe.yaml)
- [`products/sense360-core-v-w-pwr.yaml`](../../products/sense360-core-v-w-pwr.yaml)
- [`products/sense360-core-v-w-usb.yaml`](../../products/sense360-core-v-w-usb.yaml)

### `sense360_core_poe.yaml`

- [`products/sense360-poe.yaml`](../../products/sense360-poe.yaml)

### `sense360_core_voice.yaml`

- [`products/sense360-fan-pwm.yaml`](../../products/sense360-fan-pwm.yaml)
  (the legacy four-channel FanPWM compile-only product)

### `sense360_core_mini.yaml`

- [`products/sense360-mini-presence.yaml`](../../products/sense360-mini-presence.yaml)
- [`products/sense360-mini-presence-ld2412.yaml`](../../products/sense360-mini-presence-ld2412.yaml)
- [`products/sense360-mini-airiq.yaml`](../../products/sense360-mini-airiq.yaml)
- [`products/sense360-mini-airiq-ld2412.yaml`](../../products/sense360-mini-airiq-ld2412.yaml)

Mini boards have a different hardware baseline (`mini_onboard_sensors.yaml`)
and are recorded here only for completeness; they are out of scope
for the Core abstract-bus slice unless evidence later shows the same
abstract substitutions leaking into their composition.

### `sense360_core_ceiling_s3.yaml`, `sense360_core_mapping.yaml`

No current product YAML `!include` was discovered. Both files exist
in the repo and define their own substitutions; any slice that
touches them needs to confirm whether they are reachable via any
future product YAML before editing.

## Test scaffolding plan

There is no existing test that asserts Core-abstract-substitution
values against the schematic. The pattern to follow is
[`tests/test_led_package_mapping.py`](../../tests/test_led_package_mapping.py)
(HW-010), which asserts that `led_data_pin: GPIO38` in
[`packages/hardware/led_ring_ceiling.yaml`](../../packages/hardware/led_ring_ceiling.yaml)
and that `GPIO14` does not appear in that file.

Each implementation slice should introduce / extend a single test
file at `tests/test_core_abstract_bus.py` (proposed name) that
asserts:

- **001A.** `relay_pin: GPIO3` in each of the five Core abstract
  packages listed under [§CORE-ABSTRACT-BUS-001A — `relay_pin` slice](#core-abstract-bus-001a--relay_pin-slice);
  `GPIO4` and `GPIO10` do not appear as `relay_pin` values in any
  Core package; `main_relay` switch GPIO binding is `GPIO3`.
- **001B.** The canonical I²C bus id (whatever 001B chooses) is bound
  to `IO48` / `IO45` in every Core package; no Core package defines
  more than one I²C bus; every downstream package that resolves
  `*_i2c_id` resolves to the canonical id.
- **001C.** UART, status LED, PIR, ALS_INT, and expansion GPIO
  substitutions match their schematic nets per
  [§CORE-ABSTRACT-BUS-001C — UART / status LED / PIR / expansion GPIO slice](#core-abstract-bus-001c--uart--status-led--pir--expansion-gpio-slice).
  `comfort_ceiling_als_int_pin: GPIO47`. `pir_sensor_pin: GPIO15`.
  `expander_int_pin: GPIO17`. No collisions between
  `comfort_ceiling_als_int_pin`, `relay_pin`, `expander_int_pin`,
  or `sx1509_interrupt_pin` in any Core stack.

The harness already runs Python tests via
[`tests/validate_configs.py`](../../tests/validate_configs.py) and the
existing per-product / per-catalog tests; the new file fits the same
pattern.

## Validation plan for implementation slices

The implementation PRs for 001A / 001B / 001C must each run the full
existing validator suite plus the new `tests/test_core_abstract_bus.py`
once it lands:

```text
python3 tests/test_hardware_catalog.py
python3 tests/test_product_catalog.py
python3 tests/test_product_catalog_consistency.py
python3 tests/validate_webflash_builds.py
python3 tests/test_webflash_compatibility.py
python3 tests/test_webflash_artifact_naming.py
python3 tests/test_validate_webflash_release_notes.py
python3 tests/test_generate_webflash_release_notes.py
python3 tests/test_product_substitutions.py
python3 tests/test_release_one_entity_names.py
python3 tests/validate_configs.py
python3 tests/test_led_package_mapping.py
python3 tests/test_core_abstract_bus.py            # new, lands with the slice
```

Plus an explicit Release-One generated-config diff check (`esphome
config` against
[`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq.yaml)
before-and-after) so the operator can see exactly which entities
move which pins. The diff is expected to show `main_relay` moving
from `GPIO4` to `GPIO3` (for 001A) and the equivalent UART / LED /
PIR / ALS-INT moves for 001C; any other change is a regression.

## Validation plan for this PR (docs-only)

This PR changes no functional code. Running the full validator
suite is therefore expected to pass unchanged:

```text
python3 tests/test_hardware_catalog.py
python3 tests/test_product_catalog.py
python3 tests/test_product_catalog_consistency.py
python3 tests/validate_webflash_builds.py
python3 tests/test_webflash_compatibility.py
python3 tests/test_webflash_artifact_naming.py
python3 tests/test_validate_webflash_release_notes.py
python3 tests/test_generate_webflash_release_notes.py
python3 tests/test_product_substitutions.py
python3 tests/test_release_one_entity_names.py
python3 tests/validate_configs.py
python3 tests/test_led_package_mapping.py
```

The expected `git diff` footprint of this PR is restricted to:

- `docs/hardware/core-abstract-bus-reconciliation.md` (new file)
- `docs/hardware/package-readiness-matrix.md` (CORE-ABSTRACT-BUS-001
  row cross-link addendum)
- `docs/hardware/firmware-package-mapping-audit.md` (Release-One
  package-stack cross-link addendum)
- `docs/cleanup-audit.md` (CORE-ABSTRACT-BUS-001 audit-pass entry)
- `UPCOMING_PR.md` (queue split into 001A / 001B / 001C; PACKAGE-RELAY-001
  blocker reference refined)

`git diff packages products products/webflash config scripts tests
.github/workflows components include firmware manifest.json
firmware/sources.json` is expected to be empty.

## Required evidence before any slice can land

| Evidence | Slice(s) blocked | Source-of-truth doc |
|---|---|---|
| S360-100-BENCH-001 silkscreen capture of Core `J4` 1-to-3 pin order | 001A | [`s360-100-r4-core.md` §S360-100-BENCH-001 status](s360-100-r4-core.md#s360-100-bench-001-status) |
| S360-100-BENCH-001 silkscreen capture of Core `J10` 1-to-12 pin order | 001A, 001C | same |
| RoomIQ `J6` silkscreen pin-order reconciliation against Core `J10` | 001A, 001C | [`release-one-hardware-audit.md` Findings → Core / RoomIQ connector](../release-one-hardware-audit.md#findings) |
| S360-310 module-side `J2` 1-to-3 pin order, `J1` `NO`/`COM`/`NC` mapping, `K1` BOM, harness identity | 001A → PACKAGE-RELAY-001 | [`s360-310-r4-relay.md` Required evidence before promotion](s360-310-r4-relay.md#required-evidence-before-promotion) |
| ESP32-S3 `GPIO3` strap-pin boot-behaviour characterisation against populated `S360-310-R4` + `S360-100-R4` pair | 001A | new — to be recorded as part of S360-100-BENCH-001 |
| AirIQ / VentIQ rebind plan for `AirQ_Status_Led` / `AirQ_Led` indicator lines | 001C | [`firmware-package-mapping-audit.md` §VentIQ J9 / `AirQ_Led` / `AirQ_Status_Led`](firmware-package-mapping-audit.md#ventiq-j9--airq_led--airq_status_led), [§AirIQ J9 / `AirQ_Led` / `AirQ_Status_Led`](firmware-package-mapping-audit.md#airiq-j9--airq_led--airq_status_led) |
| RoomIQ package rebind plan for `comfort_ceiling.yaml` / `presence_ceiling.yaml` against `PIR` / `ALS_INT` / `I2C_SDA` / `I2C_SCL` / `Hi-Link_*` / `SEN0609_*` / `out(gpio6)` | 001C → PACKAGE-RELAY-001 | [`release-one-hardware-audit.md` Required follow-ups #3](../release-one-hardware-audit.md#required-follow-ups) |
| Expansion-GPIO bench evidence (which pins are routed to the expansion connector and have no schematic-named function) OR documented decision to retire `expansion_gpio*` abstraction | 001C → PACKAGE-PWM-001 / PACKAGE-DAC-001 | new — to be recorded against S360-100-BENCH-001 |
| Re-validation pass for every product listed under [§Blast radius per Core package](#blast-radius-per-core-package) | all three slices | per slice |
| `tests/test_core_abstract_bus.py` scaffolding | all three slices | this doc |

## Do-not-change list

CORE-ABSTRACT-BUS-001 — this audit — performs **none** of the
following. Anyone reading this audit looking for justification to
change one of them must use a separate, scoped, evidence-bearing PR.

- No edits to any package YAML under
  [`packages/`](../../packages/), including:
  - [`packages/hardware/sense360_core.yaml`](../../packages/hardware/sense360_core.yaml),
    [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml),
    [`packages/hardware/sense360_core_ceiling_s3.yaml`](../../packages/hardware/sense360_core_ceiling_s3.yaml),
    [`packages/hardware/sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml),
    [`packages/hardware/sense360_core_poe.yaml`](../../packages/hardware/sense360_core_poe.yaml),
    [`packages/hardware/sense360_core_wall.yaml`](../../packages/hardware/sense360_core_wall.yaml),
    [`packages/hardware/sense360_core_voice.yaml`](../../packages/hardware/sense360_core_voice.yaml),
    [`packages/hardware/sense360_core_voice_ceiling.yaml`](../../packages/hardware/sense360_core_voice_ceiling.yaml),
    [`packages/hardware/sense360_core_voice_wall.yaml`](../../packages/hardware/sense360_core_voice_wall.yaml),
    [`packages/hardware/sense360_core_mini.yaml`](../../packages/hardware/sense360_core_mini.yaml);
  - [`packages/expansions/fan_relay.yaml`](../../packages/expansions/fan_relay.yaml),
    [`packages/expansions/comfort_ceiling.yaml`](../../packages/expansions/comfort_ceiling.yaml),
    [`packages/expansions/comfort_ceiling_s3.yaml`](../../packages/expansions/comfort_ceiling_s3.yaml),
    [`packages/expansions/gpio_expander_sx1509.yaml`](../../packages/expansions/gpio_expander_sx1509.yaml),
    and any other expansion package.
- No edits to
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json),
  [`config/product-catalog.json`](../../config/product-catalog.json),
  [`config/webflash-builds.json`](../../config/webflash-builds.json),
  or
  [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json).
- No edits to any product YAML under [`products/`](../../products/)
  or any WebFlash wrapper under [`products/webflash/`](../../products/webflash/).
- No edits to any test under [`tests/`](../../tests/), any script
  under [`scripts/`](../../scripts/), any workflow under
  `.github/workflows/`, any component under `components/`, any
  header under `include/`, `firmware/*`, `manifest.json`, or
  `firmware/sources.json`.
- No firmware regenerated; no GitHub Release created or modified;
  no manifest signed; no WebFlash import; no kit added.
- No `schematic_status` promotion for any board. `S360-100` stays
  `verified` (already from HW-008). `S360-310` stays
  `cataloged_unverified`. `S360-311`, `S360-312`, `S360-320`,
  `S360-400`, `S360-410` stay as recorded today.
- Release-One stays `Ceiling-POE-VentIQ-RoomIQ`, version `1.0.0`,
  channel `stable`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
  `v1.0.0`. No re-release. No re-stamp.
- LED preview entry `Ceiling-POE-VentIQ-RoomIQ-LED` stays
  `status: preview`, `channel: preview`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`.
- FanTRIAC stays `status: blocked`, `blocker: HW-005`,
  `webflash_build_matrix: false`.
- COMPLIANCE-001 mains-voltage status for `S360-320` / `S360-400`
  unchanged.
- No advancement of `PACKAGE-RELAY-001`, `PRODUCT-RELAY-001`,
  `WEBFLASH-RELAY-001`, `RELEASE-RELAY-001`,
  `WF-IMPORT-RELAY-001`, `PACKAGE-PWM-001`, `PACKAGE-DAC-001`,
  `PACKAGE-TRIAC-001`, `PRODUCT-TRIAC-002`, `WF-TRIAC-001`,
  `RELEASE-TRIAC-001`, or `WF-IMPORT-TRIAC-001`.
- No closure of `S360-100-BENCH-001`, `HW-PINMAP-310-FOLLOWUP`,
  `HW-PINMAP-311-FOLLOWUP`, `HW-PINMAP-312-FOLLOWUP`,
  `HW-PINMAP-320-FOLLOWUP`, `HW-PINMAP-400-FOLLOWUP`, or
  `HW-PINMAP-410-FOLLOWUP`.
- No claim that any bench / silkscreen / harness / `K1` BOM
  evidence exists; no claim of compliance evidence for any
  mains-switching product.

## See also

- [`docs/release-one-hardware-audit.md`](../release-one-hardware-audit.md)
  — Required follow-ups #2 / #3 (HW-004) — the alias source-of-truth
  for this audit.
- [`docs/hardware/package-readiness-matrix.md`](package-readiness-matrix.md)
  — Follow-up PR sequence; `CORE-ABSTRACT-BUS-001` row.
- [`docs/hardware/firmware-package-mapping-audit.md`](firmware-package-mapping-audit.md)
  — HW-009 Release-One product YAML package stack; systemic
  Core-vs-schematic mismatch bullet.
- [`docs/hardware/s360-100-r4-core.md`](s360-100-r4-core.md) —
  schematic-backed Core pin/net/connector reference.
- [`docs/hardware/s360-310-r4-relay.md`](s360-310-r4-relay.md) —
  HW-PINMAP-310 / HW-PINMAP-310-FOLLOWUP audit.
- [`docs/cleanup-audit.md` §CORE-ABSTRACT-BUS-001 update](../cleanup-audit.md#core-abstract-bus-001-update-2026-05-19--docs-only-audit--slice-plan)
  — audit-log entry for this PR.
- [`UPCOMING_PR.md`](../../UPCOMING_PR.md) — repo queue source of
  truth; updated by this PR to split the queue entry into 001A /
  001B / 001C.

## CORE-ABSTRACT-BUS-001 audit log

### 2026-05-19 — docs-only audit + slice plan (this PR)

Performed the docs-only investigation that the matrix entry at
[`docs/hardware/package-readiness-matrix.md` Follow-up PR sequence](package-readiness-matrix.md#follow-up-pr-sequence)
gated on RoomIQ / AirIQ / VentIQ rebind plan + re-validation pass +
silkscreen evidence. The investigation produced:

- Full inventory of every Core abstract substitution across the six
  Core packages (`sense360_core.yaml`, `sense360_core_ceiling.yaml`,
  `sense360_core_ceiling_s3.yaml`, `sense360_core_mapping.yaml`,
  `sense360_core_poe.yaml`, `sense360_core_wall.yaml`) under
  [§Core abstract substitution inventory](#core-abstract-substitution-inventory).
- GPIO collision matrix under
  [§GPIO collision matrix](#gpio-collision-matrix) proving that the
  schematic-correct `relay_pin: GPIO3` collides with the existing
  `comfort_ceiling_als_int_pin: GPIO3` binding consumed by
  Release-One via
  [`packages/expansions/comfort_ceiling.yaml`](../../packages/expansions/comfort_ceiling.yaml)
  line 42.
- Three implementation slices —
  [`CORE-ABSTRACT-BUS-001A`](#core-abstract-bus-001a--relay_pin-slice),
  [`CORE-ABSTRACT-BUS-001B`](#core-abstract-bus-001b--shared-i²c-bus-consolidation-slice),
  and
  [`CORE-ABSTRACT-BUS-001C`](#core-abstract-bus-001c--uart--status-led--pir--expansion-gpio-slice).
- Inter-slice dependency graph proving 001C must land at-or-before
  001A.
- Per-Core-package blast-radius enumeration of consuming product
  YAMLs.
- Test-scaffolding plan for `tests/test_core_abstract_bus.py`
  (proposed name) modelled on
  [`tests/test_led_package_mapping.py`](../../tests/test_led_package_mapping.py).
- Open-evidence checklist with explicit gates per slice.
- Updated cross-links:
  [`docs/hardware/package-readiness-matrix.md`](package-readiness-matrix.md)
  Follow-up PR sequence + fan_relay row;
  [`docs/hardware/firmware-package-mapping-audit.md`](firmware-package-mapping-audit.md)
  Release-One package-stack mismatch bullet;
  [`docs/cleanup-audit.md`](../cleanup-audit.md) audit-pass entry;
  [`UPCOMING_PR.md`](../../UPCOMING_PR.md) queue split.
- `PACKAGE-RELAY-001` stays deferred. Its blocker reference is
  refined from generic `CORE-ABSTRACT-BUS-001` to
  `CORE-ABSTRACT-BUS-001A` (the relay slice), which itself depends
  on `CORE-ABSTRACT-BUS-001C` landing first.

### 2026-05-19 — CORE-ABSTRACT-BUS-001C investigation pass (deferred; six preconditions still open)

Performed the docs-only `CORE-ABSTRACT-BUS-001C` investigation pass
gated by
[§CORE-ABSTRACT-BUS-001C — UART / status LED / PIR / expansion GPIO slice](#core-abstract-bus-001c--uart--status-led--pir--expansion-gpio-slice)
and by the queue row at
[`UPCOMING_PR.md`](../../UPCOMING_PR.md) (entry #1 `CORE-ABSTRACT-BUS-001C`).
This pass evaluated whether `001C` could safely proceed now, either as
a docs-only Path A deferral, as a Path B test-scaffold-only PR, or as
a Path C implementation PR, against the current state of the repo.

#### Outcome

**Path A — docs-only investigation / deferral.** `001C` is **confirmed
deferred at the implementation layer.** Every readiness gate it
depends on is still open. The pass produced no package YAML, product
YAML, WebFlash wrapper, JSON catalog, script, test, workflow,
component, include, firmware artifact, or manifest edit.

#### Verification of scope against current repo state

Re-verified the `001C` scope inventory against the live YAML (no
changes; the values quoted match
[§Core abstract substitution inventory](#core-abstract-substitution-inventory)
and [§GPIO collision matrix](#gpio-collision-matrix) byte-for-byte):

- **UART split.** `uart_bus` is still a single bus in
  [`sense360_core.yaml`](../../packages/hardware/sense360_core.yaml)
  line 115,
  [`sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml)
  line 121,
  [`sense360_core_poe.yaml`](../../packages/hardware/sense360_core_poe.yaml)
  line 141, and
  [`sense360_core_wall.yaml`](../../packages/hardware/sense360_core_wall.yaml)
  line 131 — all on `GPIO1` (TX) / `GPIO2` (RX), all matching the
  `Hi-Link` net only (direction also inverted relative to the
  schematic which labels `IO1 = Hi-Link_RX`, `IO2 = Hi-Link_TX` per
  [`s360-100-r4-core.md` lines 121–122](s360-100-r4-core.md#esp32-s3-pin-and-net-mapping)
  and §UART / radar-related signals line 350). The
  [`sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml)
  variant carries `uart_presence` (line 107) + `uart_auxiliary` (line
  114). No `roomiq_hi_link_uart` / `roomiq_sen0609_uart` named bus
  exists anywhere in the repo today.
- **Status LED.** `status_led_pin: GPIO48` still binds on the I²C SDA
  net in
  [`sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml)
  line 76; `status_led_rgb_pin: GPIO48` still binds in
  [`sense360_core.yaml`](../../packages/hardware/sense360_core.yaml)
  line 66,
  [`sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml)
  line 48, and
  [`sense360_core_wall.yaml`](../../packages/hardware/sense360_core_wall.yaml)
  line 79. The per-board re-bind decision (`IO46 = GP_Fan_Status_Led`
  vs `IO7 = AirQ_Status_Led` vs leave-as-RGB-on-shared-bus) has not
  been recorded anywhere in the repo.
- **PIR.** `pir_sensor_pin: GPIO47` still binds on the `ALS_INT` net
  in
  [`sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml)
  line 77. The schematic-correct target `GPIO15` (`PIR` net per
  [`s360-100-r4-core.md` line 94](s360-100-r4-core.md#esp32-s3-pin-and-net-mapping))
  is not bound.
- **ALS_INT.** `comfort_ceiling_als_int_pin: GPIO3` still binds in
  [`comfort_ceiling.yaml`](../../packages/expansions/comfort_ceiling.yaml)
  line 42, on the schematic-correct `Relay` net rather than on the
  schematic-correct `ALS_INT` net (`IO47`). The S3 variant
  [`comfort_ceiling_s3.yaml`](../../packages/expansions/comfort_ceiling_s3.yaml)
  line 29 still binds `comfort_als_int_pin: GPIO3`; the S3 Core
  [`sense360_core_ceiling_s3.yaml`](../../packages/hardware/sense360_core_ceiling_s3.yaml)
  line 140 still binds `comfort_als_int_pin: GPIO3`. These S3 entries
  remain classified `out-of-scope` per the original audit until
  bench evidence proves the S3 board uses the same Core schematic
  net layout.
- **Expander INT.** `expander_int_pin: GPIO3` still binds in
  [`sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml)
  line 54; `sx1509_interrupt_pin: GPIO3` still binds in
  [`gpio_expander_sx1509.yaml`](../../packages/expansions/gpio_expander_sx1509.yaml)
  line 17. Both target `GPIO17` per Core schematic
  [`s360-100-r4-core.md` line 96](s360-100-r4-core.md#esp32-s3-pin-and-net-mapping)
  (`IO17 = expander_int`); neither is rebound.
- **Expansion GPIO.** `expansion_gpio1..4` still bind in
  [`sense360_core.yaml`](../../packages/hardware/sense360_core.yaml)
  lines 57–60 (`GPIO4..GPIO7`),
  [`sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml)
  lines 65–68 (`GPIO5..GPIO8`),
  [`sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml)
  lines 57–59 (`GPIO6..GPIO8`),
  [`sense360_core_poe.yaml`](../../packages/hardware/sense360_core_poe.yaml)
  lines 70–73 (`GPIO4..GPIO7`), and
  [`sense360_core_wall.yaml`](../../packages/hardware/sense360_core_wall.yaml)
  lines 69–72 (`GPIO5..GPIO8`) — every value is on a RoomIQ-claimed
  net. No expansion-connector schematic, bench-evidence record, or
  documented retirement decision for the `expansion_gpio*`
  abstraction exists anywhere in the repo.

#### Six open preconditions

Each precondition is recorded against the doc that owns its closure.
None has been satisfied since the original audit landed.

1. **`S360-100-BENCH-001` silkscreen evidence** — Core `J4` 1-to-3
   pin order, Core `J10` 1-to-12 pin order, RoomIQ `J6` 1-to-12 pin
   order. Owner: [`s360-100-r4-core.md` §S360-100-BENCH-001 status](s360-100-r4-core.md#s360-100-bench-001-status).
   Status as of the most recent re-check on 2026-05-18 is
   `pending — bench/manufacturing evidence required`. No
   operator-attributed silkscreen captures, harness photos, or
   continuity traces are committed.
2. **RoomIQ / AirIQ / VentIQ rebind plan** — a sibling-doc plan
   rebinding [`packages/expansions/comfort_ceiling.yaml`](../../packages/expansions/comfort_ceiling.yaml),
   [`packages/expansions/presence_ceiling.yaml`](../../packages/expansions/presence_ceiling.yaml),
   [`packages/expansions/airiq_bathroom_base.yaml`](../../packages/expansions/airiq_bathroom_base.yaml),
   [`packages/expansions/airiq_ceiling.yaml`](../../packages/expansions/airiq_ceiling.yaml),
   [`packages/expansions/airiq_wall.yaml`](../../packages/expansions/airiq_wall.yaml),
   and the matching feature profiles to the schematic-correct shared
   I²C bus on `IO48` / `IO45` and the two radar UARTs `Hi-Link` on
   `IO1` / `IO2` + `SEN0609` on `IO4` / `IO5`. Owner:
   [`release-one-hardware-audit.md` Required follow-ups #3](../release-one-hardware-audit.md#required-follow-ups).
   Not drafted. The companion AirIQ / VentIQ J9 `AirQ_Led` /
   `AirQ_Status_Led` rebind decision is also unresolved per
   [`firmware-package-mapping-audit.md` §VentIQ J9 / `AirQ_Led` / `AirQ_Status_Led`](firmware-package-mapping-audit.md#ventiq-j9--airq_led--airq_status_led)
   and
   [§AirIQ J9 / `AirQ_Led` / `AirQ_Status_Led`](firmware-package-mapping-audit.md#airiq-j9--airq_led--airq_status_led).
3. **Expansion-GPIO bench evidence or documented retirement
   decision** — either (a) bench evidence that specific pins are
   routed to the expansion connector and have no schematic-named
   function, or (b) a documented decision to retire the
   `expansion_gpio*` abstraction in favour of explicit
   function-named substitutions (e.g. `fan_pwm_pin`, `fan_tach_pin`)
   bound to schematic nets. Owner: this doc
   [§CORE-ABSTRACT-BUS-001C — UART / status LED / PIR / expansion GPIO slice](#core-abstract-bus-001c--uart--status-led--pir--expansion-gpio-slice).
   Neither has been recorded. Downstream consumer
   [`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml)
   binds `fan_pwm_pin: ${expansion_gpio1}` and `fan_tach_pin: ${expansion_gpio2}`,
   so the abstraction is not orphan.
4. **ESP32-S3 `GPIO3` strap-pin boot-behaviour bench
   characterisation** — characterisation against a populated
   `S360-310-R4` + `S360-100-R4` pair confirming that the relay
   module's `Q1` MMBT3904 NPN low-side topology keeps `GPIO3` in a
   benign JTAG-select state at boot. Owner: this doc
   [§Required evidence before any slice can land](#required-evidence-before-any-slice-can-land).
   Strictly a `001A` precondition; recorded here because `001C` is
   what frees `GPIO3` for `001A` to consume.
5. **`tests/test_core_abstract_bus.py` scaffold** — modeled on
   [`tests/test_led_package_mapping.py`](../../tests/test_led_package_mapping.py)
   per
   [§Test scaffolding plan](#test-scaffolding-plan). Confirmed
   absent from the repo today. Per
   [§Test scaffolding plan](#test-scaffolding-plan) the file lands
   **with the first implementation slice**, not as a standalone PR.
6. **Re-validation pass for every non-Release-One product YAML
   consuming an affected Core abstract package** — the ~30 product
   YAMLs enumerated per Core package in
   [§Blast radius per Core package](#blast-radius-per-core-package).
   Not designed.

#### Why neither Path B nor Path C is taken now

- **Path B (test-scaffold-only).** A test must assert a value. Pinning
  the **current** YAML state would enshrine schematic-conflicting
  values (`status_led_pin: GPIO48` on the I²C SDA net,
  `comfort_ceiling_als_int_pin: GPIO3` on the `Relay` net,
  `pir_sensor_pin: GPIO47` on the `ALS_INT` net, `expansion_gpio1..4`
  on RoomIQ-claimed nets) and become a tripwire that fails the
  moment the future implementation slice tries to do the right
  thing. Pinning the **target** schematic-correct values is also
  unsafe today because the per-board `status_led_pin` re-bind
  decision (`IO46` vs `IO7` vs another candidate) and the
  `expansion_gpio*` retirement-or-rebind decision are both
  undecided — precondition #2 / #3 have not landed. The test file
  is recorded by
  [§Test scaffolding plan](#test-scaffolding-plan) as a prerequisite
  that lands **with** the first implementation slice, not before it.
- **Path C (implementation).** All six preconditions above are open.
  Implementing `001C` now would silently re-bind Release-One
  ([`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq.yaml)
  consumes both
  [`sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml)
  and
  [`comfort_ceiling.yaml`](../../packages/expansions/comfort_ceiling.yaml))
  and the LED preview product on unverified silkscreen, unverified
  RoomIQ pin-order direction, unverified expansion-GPIO routing, and
  without a pin-pinning regression test. Explicitly forbidden by
  [§Do-not-change list](#do-not-change-list) above and by the
  per-slice guardrails throughout this doc.

#### Recommendation for the next `001C` PR

The next PR that touches `001C` should land **bench evidence plus
the pin-pinning test plus the YAML rebind as a single atomic
slice**, not as a test-scaffold-only PR alone. The atomic slice
must include: (i) the silkscreen / harness / boot-behaviour
evidence enumerated in
[§Required evidence before any slice can land](#required-evidence-before-any-slice-can-land);
(ii) `tests/test_core_abstract_bus.py` asserting the new values per
[§Test scaffolding plan](#test-scaffolding-plan); (iii) the YAML
edits across the Core packages and the affected expansion packages
per
[§CORE-ABSTRACT-BUS-001C — UART / status LED / PIR / expansion GPIO slice](#core-abstract-bus-001c--uart--status-led--pir--expansion-gpio-slice);
(iv) the Release-One generated-config diff check per
[§Validation plan for implementation slices](#validation-plan-for-implementation-slices);
(v) the re-validation pass for every non-Release-One product YAML
listed per Core package in
[§Blast radius per Core package](#blast-radius-per-core-package).
The `001C` PR must land at-or-before `001A` to keep `GPIO3` free for
the relay slice (per
[§GPIO collision matrix](#gpio-collision-matrix)).

#### Queue effect

- `CORE-ABSTRACT-BUS-001C` stays at the top of the
  [`UPCOMING_PR.md`](../../UPCOMING_PR.md) active queue, blocked on
  the six preconditions above.
- `CORE-ABSTRACT-BUS-001A` stays blocked behind `001C` (per
  [§GPIO collision matrix](#gpio-collision-matrix) row `GPIO3`).
- `CORE-ABSTRACT-BUS-001B` stays independent of `001A` / `001C`
  ordering but must land before `PACKAGE-PWM-001` /
  `PACKAGE-DAC-001`.
- `PACKAGE-RELAY-001` / `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` /
  `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001` stay blocked behind
  `001A` (which is itself blocked behind `001C`).
- `PACKAGE-PWM-001` / `PACKAGE-DAC-001` stay blocked behind
  `001B` + `001C` (which both affect their `*_i2c_id` and
  `${expansion_gpio*}` substitutions).
- `HW-PINMAP-410-FOLLOWUP` merged as **PR #517** on 2026-05-19 and
  is unrelated to `001C`'s six preconditions; its merge does not
  unblock any `001C` precondition.
- Release-One stays `Ceiling-POE-VentIQ-RoomIQ`, version `1.0.0`,
  channel `stable`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
  [`v1.0.0`](https://github.com/sense360store/esphome-public/releases/tag/v1.0.0).
- LED preview entry `Ceiling-POE-VentIQ-RoomIQ-LED` stays
  `status: preview`, `channel: preview`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`.
- FanTRIAC stays `status: blocked`, `blocker: HW-005`,
  `webflash_build_matrix: false`. HW-005 is not advanced.
- COMPLIANCE-001 mains-voltage status for `S360-320` / `S360-400`
  unchanged. PoE is SELV and out of scope.

#### What this audit-log entry does **not** do

Mirrors the
[§Do-not-change list](#do-not-change-list) above. The
2026-05-19 `001C` investigation pass adds no package YAML, no
product YAML, no WebFlash wrapper, no JSON catalog change, no
script, no test, no workflow, no component, no include, no firmware
artifact, no manifest, no GitHub Release, no tag, no WebFlash
import, no kit, and no `schematic_status` / `schematic_file` /
hardware-verified claim. No `CORE-ABSTRACT-BUS-001*` slice has
moved its status as a result. No precondition is closed by this
pass.

### 2026-05-19 — CORE-ABSTRACT-BUS-001B investigation pass (deferred; preconditions still open)

Performed the docs-only `CORE-ABSTRACT-BUS-001B` investigation pass
gated by
[§CORE-ABSTRACT-BUS-001B — Shared-I²C-bus consolidation slice](#core-abstract-bus-001b--shared-i²c-bus-consolidation-slice)
and by the queue row at
[`UPCOMING_PR.md`](../../UPCOMING_PR.md) (entry #3
`CORE-ABSTRACT-BUS-001B`). The companion `001C` investigation pass
merged earlier the same day as **PR #518** and is recorded above at
[§2026-05-19 — CORE-ABSTRACT-BUS-001C investigation pass](#2026-05-19--core-abstract-bus-001c-investigation-pass-deferred-six-preconditions-still-open).
This `001B` pass evaluated whether `001B` could safely proceed now,
either as a docs-only Path A deferral, as a Path B test-scaffold-only
PR, or as a Path C implementation PR, against the current state of
the repo.

#### Outcome

**Path A — docs-only investigation / deferral.** `001B` is
**confirmed deferred at the implementation layer.** The four
preconditions enumerated under
[§CORE-ABSTRACT-BUS-001B — Shared-I²C-bus consolidation slice](#core-abstract-bus-001b--shared-i²c-bus-consolidation-slice)
remain open (the downstream-consumer audit lands in this pass —
see [§Downstream consumer inventory](#downstream-consumer-inventory-2026-05-19)
immediately below — but is **not by itself** sufficient to land
an implementation slice). The pass produced no package YAML,
product YAML, WebFlash wrapper, JSON catalog, script, test,
workflow, component, include, firmware artifact, or manifest edit.

#### Verification of scope against current repo state

Re-verified the `001B` scope inventory against the live YAML (no
changes; the values quoted match
[§I²C bus substitutions](#i²c-bus-substitutions) and
[§GPIO collision matrix](#gpio-collision-matrix) byte-for-byte, plus
two Core packages newly added to scope by this investigation):

- **In-scope Core packages defining I²C buses.** Eight Core
  packages still carry the schematic-conflicting `GPIO39`/`GPIO40`
  + `GPIO21`/`GPIO18` dual-bus definitions, none on the
  schematic-correct `IO48`/`IO45` shared bus:
  - [`packages/hardware/sense360_core.yaml`](../../packages/hardware/sense360_core.yaml)
    lines 100–112 — `i2c0` (`GPIO39`/`GPIO40`) + `i2c1`
    (`GPIO21`/`GPIO18`).
  - [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml)
    lines 104–117 — `halo_i2c` (`GPIO39`/`GPIO40`) + `expansion_i2c`
    (`GPIO21`/`GPIO18`). Consumed by Release-One.
  - [`packages/hardware/sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml)
    lines 93–104 — `i2c_primary` + `i2c_expander`.
  - [`packages/hardware/sense360_core_poe.yaml`](../../packages/hardware/sense360_core_poe.yaml)
    lines 124–137 — `i2c0` + `i2c1`.
  - [`packages/hardware/sense360_core_wall.yaml`](../../packages/hardware/sense360_core_wall.yaml)
    lines 114–127 — `i2c0` + `i2c1`.
  - [`packages/hardware/sense360_core_voice_ceiling.yaml`](../../packages/hardware/sense360_core_voice_ceiling.yaml)
    lines 113–124 — `halo_i2c` + `expansion_i2c`.
    **Newly added to `001B` scope** by this investigation.
  - [`packages/hardware/sense360_core_voice_wall.yaml`](../../packages/hardware/sense360_core_voice_wall.yaml)
    lines 134–143 — `i2c0` + `i2c1`.
    **Newly added to `001B` scope** by this investigation.

  The scope-extension addendum at the end of
  [§CORE-ABSTRACT-BUS-001B — Shared-I²C-bus consolidation slice](#core-abstract-bus-001b--shared-i²c-bus-consolidation-slice)
  records both newly-in-scope files.

- **Out-of-scope Core packages.** Recorded for completeness so a
  later implementation PR does not accidentally edit them:
  - [`packages/hardware/sense360_core_ceiling_s3.yaml`](../../packages/hardware/sense360_core_ceiling_s3.yaml)
    lines 203–208 — `i2c_primary` on `GPIO17`/`GPIO18`; different
    board layout (S3 variant). Already classified `out-of-scope`
    by [§I²C bus substitutions](#i²c-bus-substitutions).
  - [`packages/hardware/sense360_core_mini.yaml`](../../packages/hardware/sense360_core_mini.yaml)
    lines 68–71 — `i2c0` on `GPIO48`/`GPIO45` already (via
    [`packages/hardware/mini_onboard_sensors.yaml`](../../packages/hardware/mini_onboard_sensors.yaml)).
    The Mini family is a separate board baseline; `001B`
    intentionally does not touch it. The Mini family also serves
    as a useful precedent that the canonical bus id **could** be
    named `i2c0` if the implementation slice chooses, although
    `shared_i2c` and `core_i2c` are equally valid candidates.

- **Schematic ground truth.** A **single shared I²C bus** on `IO48`
  (SDA) / `IO45` (SCL), pulled up by R22 / R21 10 kΩ, shared by the
  on-board SX1509 (U3) GPIO expander, J7 GP8403 fan, J9 AirIQ, and
  J10 RoomIQ. Recorded in
  [`docs/hardware/s360-100-r4-core.md` §I2C bus, lines 334–337](s360-100-r4-core.md#i2c-bus).

#### Downstream consumer inventory (2026-05-19)

This is the downstream-consumer audit listed as precondition #1 under
[§CORE-ABSTRACT-BUS-001B — Shared-I²C-bus consolidation slice](#core-abstract-bus-001b--shared-i²c-bus-consolidation-slice).
It lands as part of this investigation pass; the implementation
slice still has to translate it into a rename + re-validation plan.

**Expansion-package `*_i2c_id` substitution defaults (13 entries
across 13 files).** Every default below resolves to one of the
existing conflicting Core bus ids and must be re-evaluated when the
canonical bus id is chosen:

| Package | Substitution | Default value |
|---|---|---|
| [`packages/expansions/airiq.yaml`](../../packages/expansions/airiq.yaml) line 27 | `airiq_i2c_id` | `i2c0` |
| [`packages/expansions/airiq_wall.yaml`](../../packages/expansions/airiq_wall.yaml) line 32 | `airiq_i2c_id` | `i2c0` |
| [`packages/expansions/airiq_ceiling.yaml`](../../packages/expansions/airiq_ceiling.yaml) line 35 | `airiq_i2c_id` | `expansion_i2c` |
| [`packages/expansions/airiq_ceiling_s3.yaml`](../../packages/expansions/airiq_ceiling_s3.yaml) line 28 | `airiq_i2c_id` | `i2c_primary` |
| [`packages/expansions/airiq_bathroom_base.yaml`](../../packages/expansions/airiq_bathroom_base.yaml) line 29 | `bathroom_i2c_id` | `expansion_i2c` (consumed by Release-One via VentIQ) |
| [`packages/expansions/airiq_bathroom_pro.yaml`](../../packages/expansions/airiq_bathroom_pro.yaml) line 31 | `bathroom_i2c_id` | `expansion_i2c` |
| [`packages/expansions/comfort.yaml`](../../packages/expansions/comfort.yaml) line 24 | `comfort_i2c_id` | `i2c0` |
| [`packages/expansions/comfort_wall.yaml`](../../packages/expansions/comfort_wall.yaml) line 27 | `comfort_i2c_id` | `i2c0` |
| [`packages/expansions/comfort_ceiling.yaml`](../../packages/expansions/comfort_ceiling.yaml) line 39 | `comfort_ceiling_i2c_id` | `expansion_i2c` (consumed by Release-One via RoomIQ comfort) |
| [`packages/expansions/comfort_ceiling_s3.yaml`](../../packages/expansions/comfort_ceiling_s3.yaml) line 24 | `comfort_i2c_id` | `i2c_primary` |
| [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) line 26 | `fan_dac_i2c_id` | `i2c0` |
| [`packages/expansions/gpio_expander_sx1509.yaml`](../../packages/expansions/gpio_expander_sx1509.yaml) line 15 | `sx1509_i2c_id` | `i2c1` |
| [`packages/features/ceiling_halo_leds.yaml`](../../packages/features/ceiling_halo_leds.yaml) line 6 | (literal `i2c_id: halo_i2c`) | not overridable — hard-coded |

The `ceiling_halo_leds.yaml` row is the awkward one: the literal
`i2c_id: halo_i2c` is not exposed as a substitution and the feature
file currently has **no product `!include`r** (`grep -RIln
"ceiling_halo_leds\\|features/halo_leds" products/ packages/`
returns no product YAML). The eventual `001B` PR must either
rebind the literal to the canonical bus id or document this
feature file as dead code (and decide separately whether to retain
it for future products).

**Release-One + LED preview consumer paths.** Both
[`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq.yaml)
and
[`products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq-led.yaml)
include the same Core stack via
[`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml)
(which defines `halo_i2c` + `expansion_i2c`) and consume
`expansion_i2c` indirectly through:

- VentIQ — [`packages/expansions/airiq_bathroom_base.yaml`](../../packages/expansions/airiq_bathroom_base.yaml)
  line 29 — `bathroom_i2c_id: expansion_i2c`.
- RoomIQ comfort — [`packages/expansions/comfort_ceiling.yaml`](../../packages/expansions/comfort_ceiling.yaml)
  line 39 — `comfort_ceiling_i2c_id: expansion_i2c`.

The LED preview product additionally `!include`s
[`packages/hardware/led_ring_ceiling.yaml`](../../packages/hardware/led_ring_ceiling.yaml),
which uses `led_data_pin: GPIO38` (WS2812B, **not** I²C). Neither
product `!include`s `packages/features/ceiling_halo_leds.yaml`, so
the `halo_i2c` bus is **defined-but-unused** by both shipping
configurations today.

**Mini family inline I²C definitions.**
[`products/sense360-mini-airiq-advanced.yaml`](../../products/sense360-mini-airiq-advanced.yaml)
line 99,
[`products/sense360-mini-airiq-basic.yaml`](../../products/sense360-mini-airiq-basic.yaml)
line 87,
[`products/sense360-mini-full-ld2412.yaml`](../../products/sense360-mini-full-ld2412.yaml)
line 126,
[`products/sense360-mini-presence-advanced.yaml`](../../products/sense360-mini-presence-advanced.yaml)
line 78,
[`products/sense360-mini-presence-advanced-ld2412.yaml`](../../products/sense360-mini-presence-advanced-ld2412.yaml)
line 79, and
[`products/sense360-mini-presence-basic.yaml`](../../products/sense360-mini-presence-basic.yaml)
line 67 all define an inline `i2c0` bus on the substitution pair
exposed by
[`packages/hardware/mini_onboard_sensors.yaml`](../../packages/hardware/mini_onboard_sensors.yaml)
(`mini_sensors_i2c_id: i2c0`, `i2c_sda_pin: GPIO48`,
`i2c_scl_pin: GPIO45`). These are already schematic-correct for
the Mini board family and are explicitly out-of-scope for `001B`.

#### Four open preconditions

Each precondition is recorded against the doc that owns its closure.
The downstream-consumer audit lands in this pass; the remaining
three remain open.

1. **Canonical I²C bus-id decision** — candidates `shared_i2c` /
   `core_i2c` / `i2c0` are recorded above and at
   [§CORE-ABSTRACT-BUS-001B — Shared-I²C-bus consolidation slice](#core-abstract-bus-001b--shared-i²c-bus-consolidation-slice)
   but **not chosen** by this PR. Owner: the `001B` implementation
   slice; the chosen value must be recorded in this doc and in
   [`docs/hardware/firmware-package-mapping-audit.md`](firmware-package-mapping-audit.md)
   or a sibling doc per the original §CORE-ABSTRACT-BUS-001B
   precondition #2.
2. **`tests/test_core_abstract_bus.py` pin-pinning scaffold** —
   confirmed absent from the repo today (same finding as the
   2026-05-19 `001C` investigation pass / PR #518). Per
   [§Test scaffolding plan](#test-scaffolding-plan) the test file
   lands **with** the first implementation slice; for `001B` the
   test must assert (a) each in-scope Core package defines exactly
   one `i2c:` bus, (b) `sda: GPIO48` / `scl: GPIO45`, (c) the bus
   id matches the canonical name in every in-scope Core package,
   and (d) every downstream `*_i2c_id` substitution default
   resolves to the canonical name.
3. **Re-validation plan for every non-Release-One product YAML** —
   not designed. The implementation slice must enumerate the
   ~25 product YAMLs in [§Blast radius per Core package](#blast-radius-per-core-package)
   under each in-scope Core package, plus the Release-One and LED
   preview generated-config diff check per
   [§Validation plan for implementation slices](#validation-plan-for-implementation-slices).
4. **Downstream-consumer audit lands in this PR** (above), but
   implementation still needs the canonical name + the pin-pinning
   test + the non-Release-One product re-validation pass before
   any YAML edit. The audit alone is not a substitute for any of
   the other three preconditions.

#### Why neither Path B nor Path C is taken now

- **Path B (test-scaffold-only).** A test must assert a value.
  Pinning the **current** YAML state would enshrine the
  schematic-conflicting `GPIO39`/`GPIO40` + `GPIO21`/`GPIO18` dual
  buses on six Core packages (eight after the scope-extension
  above) and become a tripwire that fails the moment the future
  implementation slice tries to do the right thing. Pinning the
  **target** schematic-correct values (`GPIO48`/`GPIO45` on a
  single bus) is also unsafe today because the canonical bus-id
  name is undecided — pinning any of `shared_i2c` / `core_i2c` /
  `i2c0` pre-commits a choice that may not match the eventual
  implementation slice and would fail immediately against the
  current YAML state. The test file is recorded by
  [§Test scaffolding plan](#test-scaffolding-plan) as a
  prerequisite that lands **with** the first implementation slice,
  not before it.
- **Path C (implementation).** All four preconditions above are
  open. Renaming any of the six current bus ids (`halo_i2c` /
  `expansion_i2c` / `i2c0` / `i2c1` / `i2c_primary` /
  `i2c_expander`) without simultaneously updating every
  downstream `*_i2c_id` consumer would break parse-time
  substitution resolution in some product. Even an in-place
  rebind of `halo_i2c` to `GPIO48`/`GPIO45` (without renaming)
  would silently re-bind Release-One because
  [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq.yaml)
  consumes
  [`sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml)
  and
  [`comfort_ceiling.yaml`](../../packages/expansions/comfort_ceiling.yaml),
  and the LED preview product similarly re-builds — both without
  the pin-pinning regression test. Explicitly forbidden by
  [§Do-not-change list](#do-not-change-list) above and by the
  per-slice guardrails throughout this doc.

#### Recommendation for the next `001B` PR

The next PR that touches `001B` should land **the canonical
bus-id decision plus the pin-pinning test plus the YAML rebind
(Core packages plus every downstream `*_i2c_id` consumer) plus
the product re-validation pass as a single atomic slice**, not as
a test-scaffold-only PR alone. The atomic slice must include:

1. The canonical I²C bus-id name (from the candidate set
   `shared_i2c` / `core_i2c` / `i2c0`, or another name justified
   by the slice) recorded in this doc and in
   [`docs/hardware/firmware-package-mapping-audit.md`](firmware-package-mapping-audit.md)
   or a sibling doc.
2. `tests/test_core_abstract_bus.py` asserting (a) each in-scope
   Core package defines exactly one `i2c:` bus, (b) `sda: GPIO48`
   / `scl: GPIO45`, (c) the bus id matches the canonical name in
   every in-scope Core package, and (d) every downstream
   `*_i2c_id` substitution default resolves to the canonical
   name — per [§Test scaffolding plan](#test-scaffolding-plan).
3. The YAML edits across the eight in-scope Core packages plus
   every downstream expansion / feature package that resolves an
   `*_i2c_id` substitution (or carries a hard-coded `i2c_id:`
   reference such as
   [`packages/features/ceiling_halo_leds.yaml`](../../packages/features/ceiling_halo_leds.yaml)).
4. The Release-One generated-config diff check per
   [§Validation plan for implementation slices](#validation-plan-for-implementation-slices).
5. The re-validation pass for every non-Release-One product YAML
   listed per in-scope Core package in
   [§Blast radius per Core package](#blast-radius-per-core-package),
   plus the
   [`packages/hardware/sense360_core_voice_ceiling.yaml`](../../packages/hardware/sense360_core_voice_ceiling.yaml)
   and
   [`packages/hardware/sense360_core_voice_wall.yaml`](../../packages/hardware/sense360_core_voice_wall.yaml)
   consumers
   ([`products/sense360-core-voice-ceiling.yaml`](../../products/sense360-core-voice-ceiling.yaml),
   [`products/sense360-core-v-c-poe.yaml`](../../products/sense360-core-v-c-poe.yaml),
   [`products/sense360-core-v-c-pwr.yaml`](../../products/sense360-core-v-c-pwr.yaml),
   [`products/sense360-core-v-c-usb.yaml`](../../products/sense360-core-v-c-usb.yaml),
   [`products/sense360-core-voice-wall.yaml`](../../products/sense360-core-voice-wall.yaml),
   [`products/sense360-core-v-w-poe.yaml`](../../products/sense360-core-v-w-poe.yaml),
   [`products/sense360-core-v-w-pwr.yaml`](../../products/sense360-core-v-w-pwr.yaml),
   [`products/sense360-core-v-w-usb.yaml`](../../products/sense360-core-v-w-usb.yaml))
   that the scope-extension addendum now brings in.

`001B` remains independent of `001A` / `001C` ordering but must
land before `PACKAGE-PWM-001` and `PACKAGE-DAC-001` to avoid
re-doing the downstream `*_i2c_id` substitution rewrite twice.

#### Queue effect

- `CORE-ABSTRACT-BUS-001B` is now **investigated and deferred** in
  the [`UPCOMING_PR.md`](../../UPCOMING_PR.md) active queue
  (entry #3), blocked on the four preconditions above.
- `CORE-ABSTRACT-BUS-001C` stays at the top of the active queue
  (entry #1), blocked on its own six preconditions per the
  2026-05-19 `001C` investigation pass merged as **PR #518**.
- `CORE-ABSTRACT-BUS-001A` stays blocked behind `001C` (per
  [§GPIO collision matrix](#gpio-collision-matrix) row `GPIO3`).
- `PACKAGE-PWM-001` and `PACKAGE-DAC-001` stay blocked behind
  `001B` implementation (plus their own evidence gates). The
  PWM / DAC chains specifically need the canonical bus-id rebind
  so that `fan_gp8403.yaml` (`fan_dac_i2c_id: i2c0`) and the
  SX1509 expander (`sx1509_i2c_id: i2c1`) resolve to the shared
  bus on `IO48` / `IO45`.
- `PACKAGE-RELAY-001` / `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001`
  / `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001` stay blocked
  behind `001A` (which is itself blocked behind `001C`).
- Release-One stays `Ceiling-POE-VentIQ-RoomIQ`, version `1.0.0`,
  channel `stable`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
  [`v1.0.0`](https://github.com/sense360store/esphome-public/releases/tag/v1.0.0).
- LED preview entry `Ceiling-POE-VentIQ-RoomIQ-LED` stays
  `status: preview`, `channel: preview`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`.
- FanTRIAC stays `status: blocked`, `blocker: HW-005`,
  `webflash_build_matrix: false`. HW-005 is not advanced.
- COMPLIANCE-001 mains-voltage status for `S360-320` / `S360-400`
  unchanged. PoE is SELV and out of scope.

#### What this audit-log entry does **not** do

Mirrors the [§Do-not-change list](#do-not-change-list) above. The
2026-05-19 `001B` investigation pass adds no package YAML, no
product YAML, no WebFlash wrapper, no JSON catalog change, no
script, no test, no workflow, no component, no include, no
firmware artifact, no manifest, no GitHub Release, no tag, no
WebFlash import, no kit, and no `schematic_status` /
`schematic_file` / hardware-verified claim. The canonical I²C
bus-id is **not chosen** by this pass — only the candidate set
`shared_i2c` / `core_i2c` / `i2c0` is recorded. No
`CORE-ABSTRACT-BUS-001*` slice has moved its status as a result.
No precondition is closed by this pass — the downstream-consumer
audit lands here but is not a substitute for the canonical name,
the test scaffold, or the non-Release-One product re-validation
pass.

### 2026-05-21 — CORE-ABSTRACT-BUS-001C rebind plan evidence

Recorded the schematic-backed and operator-confirmed
`CORE-ABSTRACT-BUS-001C` rebind plan in a new sibling doc at
[`docs/hardware/core-abstract-bus-001c-rebind-plan.md`](core-abstract-bus-001c-rebind-plan.md).
The plan closes the *planning* layer of the long-standing `001C`
preconditions enumerated at
[§Six open preconditions](#six-open-preconditions): the RoomIQ /
AirIQ / VentIQ rebind plan is closed for RoomIQ and at the planning
layer for AirIQ / VentIQ (operator decisions #11 / #12 record
`AirQ_Status_Led` and `AirQ_Led` as AirIQ-only and VentIQ as having
no Core-driven LED line); the expansion-GPIO retirement decision is
recorded (operator decision #13 retires the generic
`expansion_gpio*` abstraction in favour of function-specific
substitutions); the ESP32-S3 `GPIO3` strap-pin boot behaviour is
operator-confirmed OK for the populated `S360-310-R4` +
`S360-100-R4` pair under operator review (operator decisions #16 /
#17 — scoped to that pair, **not** a generic claim); and the
schematic-side net order for Core `J10` and RoomIQ `J6` is recorded
against operator review of the committed schematic screenshots
(operator decisions #1–#4, #5 UART direction, #7 baud rates, #14
SEN0609 output identity, #15 canonical substitution naming).

The proposed `001C` substitution map is recorded inside the new doc
at
[`core-abstract-bus-001c-rebind-plan.md` §Proposed 001C substitution map](core-abstract-bus-001c-rebind-plan.md#proposed-001c-substitution-map)
and covers:

- **RoomIQ UARTs.** `roomiq_hi_link_uart` (`tx_pin: GPIO2`, `rx_pin:
  GPIO1`, `baud_rate: 256000`) and `roomiq_sen0609_uart` (`tx_pin:
  GPIO5`, `rx_pin: GPIO4`, `baud_rate: 115200`).
- **RoomIQ GPIO.** `pir_sensor_pin: GPIO15`,
  `comfort_ceiling_als_int_pin` (or canonical RoomIQ alias
  equivalent): `GPIO47`, `roomiq_sen0609_output_pin: GPIO6`.
- **Expander interrupt.** `expander_int_pin: GPIO17` and
  `sx1509_interrupt_pin: GPIO17` — both rebound off `GPIO3`,
  freeing `GPIO3` for the relay slice.
- **LED / status decisions.** Retire the generic Core `status_led_pin`
  substitution; retain S360-300 LED ring data on `GPIO38` owned by
  the LED ring package; introduce / retain `fan_status_led_pin:
  GPIO46`; classify `airiq_status_led_pin: GPIO7` and `airiq_led_pin:
  GPIO8` as AirIQ-only and owned by the AirIQ expansion package;
  record VentIQ as having no dedicated Core-driven LED / status
  line.
- **Expansion GPIO.** Retire `expansion_gpio1..4` and replace with
  function-specific substitutions only.
- **Relay / 001A dependency.** Reserve `GPIO3` for the Relay; the
  `001C` slice frees `GPIO3` by moving `ALS_INT` and expander
  interrupt away from `GPIO3`; the boot behaviour is
  operator-confirmed OK for the populated `S360-310-R4` +
  `S360-100-R4` pair; the Relay electrical / load / `K1` rating
  proof remains a separate evidence stream and does **not** become
  complete here.

**Status as a result.** `001C` moves from `deferred — six
preconditions still open` to **implementation-plannable** at the
planning layer. The implementation layer remains gated on the
items recorded at
[`core-abstract-bus-001c-rebind-plan.md` §Implementation readiness classification](core-abstract-bus-001c-rebind-plan.md#implementation-readiness-classification):
the bench-side `S360-100-BENCH-001` silkscreen / harness /
continuity-trace evidence (preconditions #1); the
`tests/test_core_abstract_bus.py` scaffold landing **with** the
first implementation slice (precondition #5); and the
re-validation pass for every non-Release-One product YAML
consuming an affected Core package (precondition #6). The next
`001C` PR must land **the schematic-backed substitution map + the
pin-pinning test scaffold + the YAML edits + the Release-One
generated-config diff check + the non-Release-One product
re-validation pass as a single atomic slice**, per
[§Recommendation for the next `001C` PR](#recommendation-for-the-next-001c-pr).

`001C` must still land at-or-before `001A` per [§GPIO collision
matrix](#gpio-collision-matrix) row `GPIO3` — this rebind plan does
not change that ordering.

#### Queue effect

- `CORE-ABSTRACT-BUS-001C-REBIND-PLAN-001` (this PR) is recorded
  in [`UPCOMING_PR.md`](../../UPCOMING_PR.md) as the docs-only
  planning record that unblocks `001C` at the planning layer.
- `CORE-ABSTRACT-BUS-001C` remains at the top of the
  [`UPCOMING_PR.md`](../../UPCOMING_PR.md) active queue; the
  blocker summary is refreshed to record that schematic / operator
  decisions are now committed but implementation still requires a
  scoped YAML / test PR.
- `CORE-ABSTRACT-BUS-001A` stays blocked behind `001C`
  implementation (per [§GPIO collision matrix](#gpio-collision-matrix)
  row `GPIO3`).
- `CORE-ABSTRACT-BUS-001B` stays independent of `001A` / `001C`
  ordering.
- `PACKAGE-RELAY-001` / `PRODUCT-RELAY-001` /
  `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` /
  `WF-IMPORT-RELAY-001` stay blocked behind `001A` (which is
  itself blocked behind `001C` implementation).
- `PACKAGE-PWM-001` / `PACKAGE-DAC-001` stay blocked behind
  `001B` + `001C` (which both affect their `*_i2c_id` and
  `${expansion_gpio*}` substitutions).
- Release-One stays `Ceiling-POE-VentIQ-RoomIQ`, version `1.0.0`,
  channel `stable`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
  `v1.0.0`. No re-release. No re-stamp.
- LED preview entry `Ceiling-POE-VentIQ-RoomIQ-LED` stays
  `status: preview`, `channel: preview`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`.
- FanTRIAC stays `status: blocked`, `blocker: HW-005`,
  `webflash_build_matrix: false`. HW-005 is not advanced.
- `COMPLIANCE-001` mains-voltage status for `S360-320` / `S360-400`
  unchanged. PoE is SELV and out of scope.
- `S360-100` `schematic_status: verified` (HW-008) unchanged.
  `S360-310` `schematic_status: cataloged_unverified` unchanged.

#### What this audit-log entry does **not** do

Mirrors the [§Do-not-change list](#do-not-change-list) above. The
2026-05-21 `001C` rebind-plan evidence record adds no package
YAML, no product YAML, no WebFlash wrapper, no JSON catalog
change, no script, no test, no workflow, no component, no
include, no firmware artifact, no manifest, no GitHub Release, no
tag, no WebFlash import, no kit, no `schematic_status` /
`schematic_file` / hardware-verified claim, no compliance claim,
no WebFlash import-readiness claim, and no hardware-release-readiness
claim. No `CORE-ABSTRACT-BUS-001*` slice has changed its
implementation status as a result. No
`S360-100-BENCH-001` precondition is closed at the bench-side
layer. No `PACKAGE-RELAY-001` / `RELEASE-RELAY-001` precondition
is closed. `tests/test_core_abstract_bus.py` is **not** added by
this PR — the test file lands **with** the first implementation
slice per [§Test scaffolding plan](#test-scaffolding-plan).

### 2026-05-21 — CORE-ABSTRACT-BUS-001C implementation

Applied the schematic-backed `CORE-ABSTRACT-BUS-001C` rebind plan
recorded in [`core-abstract-bus-001c-rebind-plan.md`](core-abstract-bus-001c-rebind-plan.md)
as YAML edits across the affected Core abstract packages and the
affected expansion packages, and landed the pin-pinning regression
scaffold at
[`tests/test_core_abstract_bus.py`](../../tests/test_core_abstract_bus.py).

#### YAML edits applied

| Package | Change |
| --- | --- |
| [`packages/expansions/comfort_ceiling.yaml`](../../packages/expansions/comfort_ceiling.yaml) | `comfort_ceiling_als_int_pin: GPIO3 → GPIO47` (schematic ALS_INT net per S360-100-R4 IO47). |
| [`packages/expansions/gpio_expander_sx1509.yaml`](../../packages/expansions/gpio_expander_sx1509.yaml) | `sx1509_interrupt_pin: GPIO3 → GPIO17` (schematic expander_int net per S360-100-R4 IO17). |
| [`packages/hardware/sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml) | `expander_int_pin: GPIO3 → GPIO17`; `expansion_gpio1..3` retired; `status_led_simple_pin: GPIO47` retired; `uart_presence` collapsed into the new `roomiq_hi_link_uart` block; `fan_status_led_pin: GPIO46` introduced; `roomiq_sen0609_output_pin: GPIO6` introduced. |
| [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml) | `pir_sensor_pin: GPIO47 → GPIO15` (schematic PIR net per S360-100-R4 IO15); `status_led_pin: GPIO48` retired; `expansion_gpio1..4` retired; default `fan_pwm_pin`/`fan_tach_pin` mappings on `expansion_gpio*` removed; `uart_bus` replaced by `roomiq_hi_link_uart` (256000) and `roomiq_sen0609_uart` (115200); `fan_status_led_pin: GPIO46` introduced; `roomiq_sen0609_output_pin: GPIO6` introduced. |
| [`packages/hardware/sense360_core.yaml`](../../packages/hardware/sense360_core.yaml) | `status_led_pin: GPIO2` retired (was Hi-Link_TX); `expansion_gpio1..4` retired; `uart_bus` replaced by the two named RoomIQ UARTs; `fan_status_led_pin: GPIO46` introduced. |
| [`packages/hardware/sense360_core_poe.yaml`](../../packages/hardware/sense360_core_poe.yaml) | `status_led_pin: GPIO8` retired (was AirQ_Led, AirIQ-only); `expansion_gpio1..4` retired; `uart_bus` replaced by the two named RoomIQ UARTs; `fan_status_led_pin: GPIO46` introduced. |
| [`packages/hardware/sense360_core_wall.yaml`](../../packages/hardware/sense360_core_wall.yaml) | `status_led_pin: GPIO47` retired (was ALS_INT); `expansion_gpio1..4` retired; default `fan_pwm_pin`/`fan_tach_pin` mappings removed; `uart_bus` replaced by the two named RoomIQ UARTs; `fan_status_led_pin: GPIO46` introduced. |
| [`packages/hardware/sense360_core_voice_ceiling.yaml`](../../packages/hardware/sense360_core_voice_ceiling.yaml) | `status_led_pin: GPIO48` retired (was I2C_SDA); `expansion_gpio1..4` retired; default `fan_pwm_pin`/`fan_tach_pin` mappings removed; `uart_bus` replaced by the two named RoomIQ UARTs; `fan_status_led_pin: GPIO46` introduced. |
| [`packages/hardware/sense360_core_voice_wall.yaml`](../../packages/hardware/sense360_core_voice_wall.yaml) | `status_led_pin: GPIO47` retired (was ALS_INT); `expansion_gpio1..4` retired; default `fan_pwm_pin`/`fan_tach_pin` mappings removed; `uart_bus` replaced by the two named RoomIQ UARTs; `fan_status_led_pin: GPIO46` introduced. |
| [`packages/hardware/sense360_core_voice.yaml`](../../packages/hardware/sense360_core_voice.yaml) | `voice_status_led_pin` default rebound from `${status_led_pin}` (retired) to `${fan_status_led_pin}` (GPIO46); products that override `voice_status_led_pin` are unaffected. |
| [`packages/expansions/presence_ceiling.yaml`](../../packages/expansions/presence_ceiling.yaml), [`packages/expansions/presence_wall.yaml`](../../packages/expansions/presence_wall.yaml), [`packages/expansions/presence_ld2450.yaml`](../../packages/expansions/presence_ld2450.yaml) | `ld2450_uart_id: uart_bus → roomiq_hi_link_uart`; `ld2450_baud` aligned to the Hi-Link 256000 default. |

#### Test scaffold

The new pin-pinning regression scaffold at
[`tests/test_core_abstract_bus.py`](../../tests/test_core_abstract_bus.py)
asserts:

- `pir_sensor_pin: GPIO15` in `sense360_core_ceiling.yaml`.
- `comfort_ceiling_als_int_pin: GPIO47` in `comfort_ceiling.yaml`;
  active substitution does not bind `GPIO3`.
- `roomiq_sen0609_output_pin: GPIO6` wherever defined.
- `expander_int_pin: GPIO17` in `sense360_core_mapping.yaml`.
- `sx1509_interrupt_pin: GPIO17` in `gpio_expander_sx1509.yaml`.
- `roomiq_hi_link_uart` block: `tx_pin: GPIO2`, `rx_pin: GPIO1`,
  `baud_rate: 256000` wherever defined.
- `roomiq_sen0609_uart` block: `tx_pin: GPIO5`, `rx_pin: GPIO4`,
  `baud_rate: 115200` wherever defined.
- `status_led_pin` substitution **absent** from every affected Core
  abstract package.
- `led_data_pin: GPIO38` remains in `led_ring_ceiling.yaml`.
- `fan_status_led_pin: GPIO46` wherever defined (and defined in at
  least one Core abstract package).
- `airiq_status_led_pin: GPIO7` if defined.
- `airiq_led_pin: GPIO8` if defined.
- No `ventiq*_led_pin` substitution anywhere under `packages/`.
- `expansion_gpio1..4` substitutions **absent** from every affected
  Core abstract package.
- No pin collision between `relay_pin`,
  `comfort_ceiling_als_int_pin`, `expander_int_pin`, and
  `sx1509_interrupt_pin`. `expander_int_pin` and
  `sx1509_interrupt_pin` intentionally share `GPIO17` (same
  schematic net).
- `relay_pin` holds its pre-001A value in every Core abstract package
  (the relay move to `GPIO3` belongs to `CORE-ABSTRACT-BUS-001A`).

#### Outcome

`001C` moves from `implementation-plannable` (per the
[2026-05-21 rebind plan evidence entry](#2026-05-21--core-abstract-bus-001c-rebind-plan-evidence)
above) to **implementation-landed**. `CORE-ABSTRACT-BUS-001A` is now
unblocked at the `GPIO3`-collision layer recorded in
[§GPIO collision matrix](#gpio-collision-matrix): the Release-One
package stack no longer claims `GPIO3` for ALS_INT or for the SX1509
expander interrupt.

`001A` retains its other preconditions:

1. `S360-100-BENCH-001` silkscreen evidence (Core `J4` pin-order, the
   Core-to-relay harness identity).
2. ESP32-S3 `GPIO3` strap-pin boot-behaviour bench characterisation
   against a populated `S360-310-R4` + `S360-100-R4` pair. Operator
   decisions #16 / #17 in the [001C rebind plan](core-abstract-bus-001c-rebind-plan.md)
   were scoped to the pair under operator review and do **not**
   generalize.
3. `K1` BOM identity, contact-current rating, harness identity per
   [`s360-310-r4-relay.md` Required evidence before promotion](s360-310-r4-relay.md#required-evidence-before-promotion).

#### Queue effect

- `CORE-ABSTRACT-BUS-001C` moves from active-queue item #1
  (`implementation-plannable`) to **completed-merged**.
- `CORE-ABSTRACT-BUS-001A` stays in the active queue as the next
  systemic slice once its bench / strap / `K1` BOM preconditions
  close.
- `CORE-ABSTRACT-BUS-001B` stays independent of `001A` / `001C`
  ordering.
- `PACKAGE-RELAY-001` / `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` /
  `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001` stay blocked behind
  `001A`.
- `PACKAGE-PWM-001` / `PACKAGE-DAC-001` stay blocked behind `001B` +
  `001C`. The `${expansion_gpio*}` references in their downstream
  consumers
  ([`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml)
  comment block,
  [`packages/expansions/fan_relay.yaml`](../../packages/expansions/fan_relay.yaml)
  line 27 override hook) are unaffected by this PR (those files
  carry comment-only references to `${expansion_gpio*}`; no active
  substitution binding survives in any Core abstract package).
- Release-One stays `Ceiling-POE-VentIQ-RoomIQ`, version `1.0.0`,
  channel `stable`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag `v1.0.0`.
- LED preview entry `Ceiling-POE-VentIQ-RoomIQ-LED` stays
  `status: preview`, `channel: preview`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`.
- FanTRIAC stays `status: blocked`, `blocker: HW-005`,
  `webflash_build_matrix: false`. HW-005 is not advanced.
- `COMPLIANCE-001` mains-voltage status for `S360-320` / `S360-400`
  unchanged. PoE is SELV and out of scope.

#### What this entry does **not** do

- No package promotion. No product YAML added. No WebFlash wrapper
  added. No catalog edit
  ([`config/hardware-catalog.json`](../../config/hardware-catalog.json),
  [`config/product-catalog.json`](../../config/product-catalog.json),
  [`config/webflash-builds.json`](../../config/webflash-builds.json),
  [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json),
  [`config/compile-only-targets.json`](../../config/compile-only-targets.json),
  [`config/firmware-combination-matrix.json`](../../config/firmware-combination-matrix.json),
  [`config/kit-intent-matrix.json`](../../config/kit-intent-matrix.json)
  all stay byte-identical). No `webflash_build_matrix: true` flip. No
  `artifact_name` / `webflash_wrapper` / `config_string` /
  `release_one_required_configs` / `lifecycle_statuses` /
  `canonical_modules` / `canonical_power` / `forbidden_tokens` /
  kit / `REQUIRED_CONFIGS` change.
- No `schematic_status` / `schematic_file` promotion. No
  `S360-100-BENCH-001` precondition is closed at the bench-side
  silkscreen / harness / continuity-trace layer.
- No `COMPLIANCE-001` movement. No release artifact built or
  attached. No `firmware/` change. No `manifest.json` change. No
  `.github/workflows/**` change.
- No claim that `PACKAGE-RELAY-001` / `PRODUCT-RELAY-001` /
  `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` /
  `WF-IMPORT-RELAY-001` is advanced or unblocked beyond the
  `GPIO3`-collision layer that this 001C implementation frees.
- No WebFlash import-readiness claim. No
  hardware-release-readiness claim. No FanPWM / FanDAC / FanTRIAC /
  LED stable promotion.
- `relay_pin` is not changed.

### 2026-05-21 — CORE-ABSTRACT-BUS-001A implementation

Applied the schematic-backed `CORE-ABSTRACT-BUS-001A` relay-pin rebind
recorded in
[§CORE-ABSTRACT-BUS-001A — `relay_pin` slice](#core-abstract-bus-001a--relay_pin-slice)
across the five affected Core abstract packages. The `GPIO3` collision
that previously blocked `001A` from landing was resolved by the
`CORE-ABSTRACT-BUS-001C-IMPLEMENT-001` slice merged earlier the same
day as **PR #557** (see the
[2026-05-21 — CORE-ABSTRACT-BUS-001C implementation](#2026-05-21--core-abstract-bus-001c-implementation)
audit-log entry above): ALS_INT moved off `GPIO3` to `GPIO47` in
[`packages/expansions/comfort_ceiling.yaml`](../../packages/expansions/comfort_ceiling.yaml),
the SX1509 expander interrupt moved off `GPIO3` to `GPIO17` in
[`packages/expansions/gpio_expander_sx1509.yaml`](../../packages/expansions/gpio_expander_sx1509.yaml)
and
[`packages/hardware/sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml),
and the pin-pinning regression scaffold
[`tests/test_core_abstract_bus.py`](../../tests/test_core_abstract_bus.py)
landed.

#### YAML edits applied

| Package | Before | After | Schematic net |
| --- | --- | --- | --- |
| [`packages/hardware/sense360_core.yaml`](../../packages/hardware/sense360_core.yaml) | `relay_pin: GPIO10` | `relay_pin: GPIO3` | `Relay` (Core schematic IO3) |
| [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml) | `relay_pin: GPIO4` | `relay_pin: GPIO3` | `Relay` |
| [`packages/hardware/sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml) | `relay_pin: GPIO10` | `relay_pin: GPIO3` | `Relay` |
| [`packages/hardware/sense360_core_poe.yaml`](../../packages/hardware/sense360_core_poe.yaml) | `relay_pin: GPIO10` | `relay_pin: GPIO3` | `Relay` |
| [`packages/hardware/sense360_core_wall.yaml`](../../packages/hardware/sense360_core_wall.yaml) | `relay_pin: GPIO4` | `relay_pin: GPIO3` | `Relay` |

Voice-variant Core packages
([`packages/hardware/sense360_core_voice_ceiling.yaml`](../../packages/hardware/sense360_core_voice_ceiling.yaml)
and
[`packages/hardware/sense360_core_voice_wall.yaml`](../../packages/hardware/sense360_core_voice_wall.yaml))
remain at their pre-001A `relay_pin: GPIO4` values. Those packages are
deliberately out of scope for this PR — they are not in the
`RELAY_REBIND_PACKAGES` list under
[§CORE-ABSTRACT-BUS-001A — `relay_pin` slice](#core-abstract-bus-001a--relay_pin-slice)
and a later, separately-evidenced slice will address them once the
voice-variant board family has independent silkscreen / harness
evidence.

#### Pin-pinning regression updates

[`tests/test_core_abstract_bus.py`](../../tests/test_core_abstract_bus.py)
extends the 001C scaffold with a `RELAY_REBIND_PACKAGES` list and three
new assertions:

- `RelayPinRebindTests.test_relay_pin_is_gpio3_in_every_affected_core_package`
  pins `relay_pin: GPIO3` in each of the five affected Core abstract
  packages.
- `RelayPinRebindTests.test_relay_pin_is_not_gpio4_or_gpio10_in_any_affected_core_package`
  asserts that none of the affected packages still carries the
  pre-001A `GPIO4` or `GPIO10` value.
- `MainRelaySwitchBindingTests.test_main_relay_pin_is_relay_pin_substitution`
  asserts that `id: main_relay` in
  [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml)
  binds `pin: ${relay_pin}` so the schematic-correct value is consumed
  by downstream products through substitution.

The pre-existing 001C assertions (`pir_sensor_pin: GPIO15`,
`comfort_ceiling_als_int_pin: GPIO47`, `expander_int_pin: GPIO17`,
`sx1509_interrupt_pin: GPIO17`, RoomIQ Hi-Link UART on `GPIO2`/`GPIO1`
at 256000 baud, RoomIQ SEN0609 UART on `GPIO5`/`GPIO4` at 115200 baud,
`led_data_pin: GPIO38` in
[`packages/hardware/led_ring_ceiling.yaml`](../../packages/hardware/led_ring_ceiling.yaml),
`fan_status_led_pin: GPIO46`, AirIQ-only `airiq_status_led_pin: GPIO7`
and `airiq_led_pin: GPIO8`, no VentIQ Core-driven LED, `status_led_pin`
absent, `expansion_gpio1..4` absent, no collision between `relay_pin`
and the 001C-rebound nets) remain intact and are re-asserted by the
same test file. The collision test now confirms that `relay_pin:
GPIO3` does not collide with `comfort_ceiling_als_int_pin: GPIO47`,
`expander_int_pin: GPIO17`, or `sx1509_interrupt_pin: GPIO17`.

#### Generated-config diff expectations for Release-One

For
[`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq.yaml)
(Release-One) and
[`products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq-led.yaml)
(LED preview sibling), running `esphome config` before-and-after this
PR is expected to show only:

- The `main_relay` switch's underlying `pin: number:` moves from
  `GPIO4` (the pre-001A
  [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml)
  `relay_pin` value) to `GPIO3` (the schematic-correct Relay net per
  S360-100-R4 IO3).
- All 001C changes recorded under the
  [2026-05-21 — CORE-ABSTRACT-BUS-001C implementation](#2026-05-21--core-abstract-bus-001c-implementation)
  audit-log entry remain unchanged byte-for-byte (UART blocks, status
  LED pin, ALS interrupt pin, PIR pin, RoomIQ aux pin).
- No `config_string` change, no `artifact_name` change, no WebFlash
  exposure change, no release-channel change, no product-catalog
  change, no LED-ring pin change, no entity name change.

If any other change appears (new entities, renamed entities, removed
entities, a `relay_pin` move to a value other than `GPIO3`, a
`led_data_pin` move, an `expansion_gpio*` reappearing, an
`artifact_name` change, etc.), stop and fix before merging.

#### Outcome

`CORE-ABSTRACT-BUS-001A` moves from `unblocked at the GPIO3-collision
layer; bench / strap / K1 BOM preconditions still open` to
**implementation-landed** at the YAML / test-scaffold / static-
validation layer. The schematic-correct `relay_pin: GPIO3` value is
now bound in every affected Core abstract package and is asserted by
the pin-pinning regression scaffold.

This PR explicitly does **not** prove the Relay load / contact / `K1`
rating. It does **not** complete `PACKAGE-RELAY-001`. It does **not**
release any Relay artifact. It does **not** unblock WebFlash import by
itself. The S360-100-BENCH-001 silkscreen evidence (Core `J4` pin-order,
Core-to-relay harness identity) and the general ESP32-S3 `GPIO3`
strap-pin boot-behaviour bench characterisation remain owed.

#### Queue effect

- `CORE-ABSTRACT-BUS-001A` moves from active-queue item #1
  (`unblocked at the GPIO3-collision layer`) to **completed-merged**.
- `CORE-ABSTRACT-BUS-001B` stays independent of `001A` / `001C`
  ordering.
- `PACKAGE-RELAY-001` / `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` /
  `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001` stay blocked behind:
  (1) S360-100-BENCH-001 silkscreen evidence; (2) general ESP32-S3
  `GPIO3` strap-pin boot-behaviour characterisation; (3) `K1` BOM
  identity, contact-current rating, harness identity per
  [`s360-310-r4-relay.md` Required evidence before promotion](s360-310-r4-relay.md#required-evidence-before-promotion).
- `PACKAGE-PWM-001` / `PACKAGE-DAC-001` stay blocked behind `001B` +
  their own evidence gates.
- Release-One stays `Ceiling-POE-VentIQ-RoomIQ`, version `1.0.0`,
  channel `stable`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag `v1.0.0`.
- LED preview entry `Ceiling-POE-VentIQ-RoomIQ-LED` stays
  `status: preview`, `channel: preview`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`.
- FanTRIAC stays `status: blocked`, `blocker: HW-005`,
  `webflash_build_matrix: false`. HW-005 is not advanced.
- `COMPLIANCE-001` mains-voltage status for `S360-320` / `S360-400`
  unchanged. PoE is SELV and out of scope.

#### What this entry does **not** do

- No package promotion. No product YAML added. No WebFlash wrapper
  added. No catalog edit
  ([`config/hardware-catalog.json`](../../config/hardware-catalog.json),
  [`config/product-catalog.json`](../../config/product-catalog.json),
  [`config/webflash-builds.json`](../../config/webflash-builds.json),
  [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json),
  [`config/compile-only-targets.json`](../../config/compile-only-targets.json),
  [`config/firmware-combination-matrix.json`](../../config/firmware-combination-matrix.json),
  [`config/kit-intent-matrix.json`](../../config/kit-intent-matrix.json)
  all stay byte-identical). No `webflash_build_matrix: true` flip. No
  `artifact_name` / `webflash_wrapper` / `config_string` /
  `release_one_required_configs` / `lifecycle_statuses` /
  `canonical_modules` / `canonical_power` / `forbidden_tokens` /
  kit / `REQUIRED_CONFIGS` change.
- No `schematic_status` / `schematic_file` promotion. No
  `S360-100-BENCH-001` precondition is closed at the bench-side
  silkscreen / harness / continuity-trace layer.
- No `COMPLIANCE-001` movement. No release artifact built or
  attached. No `firmware/` change. No `manifest.json` change. No
  `.github/workflows/**` change.
- No claim that `PACKAGE-RELAY-001` / `PRODUCT-RELAY-001` /
  `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` /
  `WF-IMPORT-RELAY-001` is advanced or unblocked beyond the
  `relay_pin: GPIO3` substitution layer that this 001A
  implementation lands.
- No claim of Relay load / contact / `K1` rating proof. No claim of
  S360-310 silkscreen / harness / BOM evidence closure.
- No WebFlash import-readiness claim. No
  hardware-release-readiness claim. No FanPWM / FanDAC / FanTRIAC /
  LED stable promotion.

### 2026-05-22 — CORE-ABSTRACT-BUS-001B core_i2c plan

Recorded the operator-confirmed implementation plan for
`CORE-ABSTRACT-BUS-001B` (the shared-I²C-bus consolidation slice).
This is a **docs / planning / inventory** entry. No package YAML,
product YAML, WebFlash wrapper, JSON catalog, script, test, workflow,
component, include, firmware artifact, or manifest is edited by this
PR. The downstream-consumer inventory previously recorded by the
2026-05-19 `001B` investigation pass (merged as **PR #519** — see
[§2026-05-19 — CORE-ABSTRACT-BUS-001B investigation pass](#2026-05-19--core-abstract-bus-001b-investigation-pass-deferred-preconditions-still-open))
is re-verified, refreshed against the post-`001A` / post-`001C`
repo state, and extended with the decisions enumerated below. The
remaining `001B` preconditions stay open at the implementation
layer.

This entry refines the
[§CORE-ABSTRACT-BUS-001B — Shared-I²C-bus consolidation slice](#core-abstract-bus-001b--shared-i²c-bus-consolidation-slice)
section above: the **canonical I²C bus id is now decided** (`core_i2c`)
and the **migration style is hard rename only** (no compatibility
aliases by default). Future references to "the canonical bus id"
elsewhere in this document should be read as `core_i2c`.

#### Operator decisions (2026-05-22)

| # | Decision | Value |
|---|---|---|
| 1 | Canonical shared Core I²C bus id | **`core_i2c`** |
| 2 | Migration style | **Hard rename only** |
| 3 | Compatibility aliases | **None by default** — added only if implementation tests later prove an alias unavoidable |
| 4 | Legacy bus ids (`halo_i2c`, `expansion_i2c`, `i2c0`, `i2c1`, `i2c_primary`, `i2c_expander`) in affected Core packages | **Removed** — no parallel definitions, no fall-through |
| 5 | Downstream `*_i2c_id` substitution defaults | **Rebound to `core_i2c`** in the same PR as the Core rename |
| 6 | Hard-coded `i2c_id: halo_i2c` in `packages/features/ceiling_halo_leds.yaml` | **Rebound to `i2c_id: core_i2c`** (the feature now has product `!include`rs — see [§Consumer inventory](#core-abstract-bus-001b-core_i2c-plan--consumer-inventory) below) |
| 7 | Package-specific private I²C buses (not Core-shared) | **Left in place if explicitly documented**; otherwise renamed to `core_i2c` along with the Core packages |
| 8 | Sequencing within the implementation PR | **Atomic** — Core rename + every consumer + test scaffold + Release-One generated-config diff check land together |
| 9 | Scope boundary | **Substitution layer only** — no product YAML, WebFlash wrapper, JSON catalog, build matrix, release artifact, or compliance claim |
| 10 | Out-of-scope Core packages | [`sense360_core_ceiling_s3.yaml`](../../packages/hardware/sense360_core_ceiling_s3.yaml) (`i2c_primary` on `GPIO17`/`GPIO18`, different board lineage); [`sense360_core_mini.yaml`](../../packages/hardware/sense360_core_mini.yaml) (`i2c0` already on schematic-correct `GPIO48`/`GPIO45`); the six `sense360-mini-*.yaml` products that define their own inline `i2c0` block |

#### Rationale for the canonical id choice

- `core_i2c` is **self-describing** (names the board family it belongs
  to) and is **not currently in use** anywhere in the repo (`grep -RIln
  "core_i2c" packages products config tests` returns no functional
  references; the existing mentions are docs-only). It will not
  collide with any pre-existing substitution or literal.
- `shared_i2c` was a candidate but is **less specific** — every I²C
  bus is "shared" by definition, and a future per-board variant could
  reuse the name.
- `i2c0` was a candidate but is **already used** by the Mini board
  baseline and by six inline product definitions. Choosing `i2c0` for
  the Core consolidation would either re-bind the Mini family
  silently (out of `001B` scope) or require renaming every Mini
  reference in the same PR (expanding `001B`'s blast radius without
  benefit).
- Hard rename only — no aliases — keeps the substitution graph
  single-rooted. ESPHome's `!include` substitution model resolves
  every `*_i2c_id` default once at parse time; layering an alias
  layer adds maintenance debt for no runtime benefit. If a later
  implementation pass discovers an unavoidable consumer that cannot
  follow the rename, that single consumer's alias can be recorded
  inline in this audit doc against the implementation PR.

#### Refreshed bus-definition inventory (2026-05-22)

Re-verified against the live YAML. Eight Core packages still carry
the schematic-conflicting dual-bus definitions; no rename has
occurred yet:

| File | Lines | Current bus id(s) | SDA pin | SCL pin | In scope for 001B? |
|---|---|---|---|---|---|
| [`packages/hardware/sense360_core.yaml`](../../packages/hardware/sense360_core.yaml) | 89–98 | `i2c0` + `i2c1` | `GPIO39` / `GPIO21` | `GPIO40` / `GPIO18` | **Yes** |
| [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml) | 121–130 | `halo_i2c` + `expansion_i2c` | `GPIO39` / `GPIO21` | `GPIO40` / `GPIO18` | **Yes** (Release-One Core) |
| [`packages/hardware/sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml) | 100–110 | `i2c_primary` + `i2c_expander` | `${i2c0_sda_pin}` / `${i2c1_sda_pin}` | `${i2c0_scl_pin}` / `${i2c1_scl_pin}` | **Yes** |
| [`packages/hardware/sense360_core_poe.yaml`](../../packages/hardware/sense360_core_poe.yaml) | 118–127 | `i2c0` + `i2c1` | `GPIO39` / `GPIO21` | `GPIO40` / `GPIO18` | **Yes** |
| [`packages/hardware/sense360_core_wall.yaml`](../../packages/hardware/sense360_core_wall.yaml) | 116–125 | `i2c0` + `i2c1` | `GPIO39` / `GPIO21` | `GPIO40` / `GPIO18` | **Yes** |
| [`packages/hardware/sense360_core_voice_ceiling.yaml`](../../packages/hardware/sense360_core_voice_ceiling.yaml) | 115–123 | `halo_i2c` + `expansion_i2c` | `GPIO39` / `GPIO21` | `GPIO40` / `GPIO18` | **Yes** |
| [`packages/hardware/sense360_core_voice_wall.yaml`](../../packages/hardware/sense360_core_voice_wall.yaml) | 135–143 | `i2c0` + `i2c1` | `GPIO39` / `GPIO21` | `GPIO40` / `GPIO18` | **Yes** |
| [`packages/hardware/sense360_core_ceiling_s3.yaml`](../../packages/hardware/sense360_core_ceiling_s3.yaml) | 204–208 | `i2c_primary` | `GPIO17` | `GPIO18` | **No** (different board layout) |
| [`packages/hardware/sense360_core_mini.yaml`](../../packages/hardware/sense360_core_mini.yaml) | 69–72 | `i2c0` | `GPIO48` | `GPIO45` | **No** (Mini baseline; already on schematic-correct pins) |

Pin-substitution defaults in
[`packages/hardware/sense360_core.yaml`](../../packages/hardware/sense360_core.yaml)
lines 36–49 still expose the dual-bus pin substitutions
(`i2c0_sda_pin` / `i2c0_scl_pin` / `i2c0_frequency` / `i2c1_sda_pin` /
`i2c1_scl_pin` / `i2c1_frequency`). The implementation slice must
decide whether to retain the dual-pin substitutions as a single
`core_i2c_sda_pin` / `core_i2c_scl_pin` / `core_i2c_frequency`
triple or to retire them entirely and inline `GPIO48` / `GPIO45` /
`400kHz` against `core_i2c`. The latter (retirement + inline) keeps
the substitution graph shallow and matches the existing Mini
baseline pattern; the former preserves an override hook for boards
whose I²C frequency differs from 400 kHz. **Recommended:** retire the
pin substitutions; inline `GPIO48` / `GPIO45` / `400kHz` against
`core_i2c` in each affected Core package, and let any future
per-board override use the standard ESPHome substitution mechanism
when needed.

#### CORE-ABSTRACT-BUS-001B / core_i2c plan — Consumer inventory

The downstream-consumer audit landed in PR #519 is re-verified
against the live YAML on 2026-05-22 and extended with three
categories the 2026-05-19 pass did not separate cleanly. Every
file:line below mentions `i2c_id:` (substitution default or literal
reference) and must be touched by the implementation PR.

**A. Core I²C bus definitions (rename target).** Eight files listed
in the inventory table above. Renamed verbatim to `core_i2c`.

**B. Package consumers using `i2c_id` substitution defaults (13
entries across 13 files).** Every default below must be rebound to
`core_i2c`:

| Package | Line | Substitution name | Default (before) | Default (after) |
|---|---|---|---|---|
| [`packages/expansions/airiq.yaml`](../../packages/expansions/airiq.yaml) | 27 | `airiq_i2c_id` | `i2c0` | `core_i2c` |
| [`packages/expansions/airiq_wall.yaml`](../../packages/expansions/airiq_wall.yaml) | 32 | `airiq_i2c_id` | `i2c0` | `core_i2c` |
| [`packages/expansions/airiq_ceiling.yaml`](../../packages/expansions/airiq_ceiling.yaml) | 35 | `airiq_i2c_id` | `expansion_i2c` | `core_i2c` |
| [`packages/expansions/airiq_ceiling_s3.yaml`](../../packages/expansions/airiq_ceiling_s3.yaml) | 28 | `airiq_i2c_id` | `i2c_primary` | **out-of-scope** (S3 board lineage) |
| [`packages/expansions/airiq_bathroom_base.yaml`](../../packages/expansions/airiq_bathroom_base.yaml) | 29 | `bathroom_i2c_id` | `expansion_i2c` | `core_i2c` (consumed by Release-One via VentIQ) |
| [`packages/expansions/airiq_bathroom_pro.yaml`](../../packages/expansions/airiq_bathroom_pro.yaml) | 31 | `bathroom_i2c_id` | `expansion_i2c` | `core_i2c` |
| [`packages/expansions/comfort.yaml`](../../packages/expansions/comfort.yaml) | 24 | `comfort_i2c_id` | `i2c0` | `core_i2c` |
| [`packages/expansions/comfort_wall.yaml`](../../packages/expansions/comfort_wall.yaml) | 27 | `comfort_i2c_id` | `i2c0` | `core_i2c` |
| [`packages/expansions/comfort_ceiling.yaml`](../../packages/expansions/comfort_ceiling.yaml) | 39 | `comfort_ceiling_i2c_id` | `expansion_i2c` | `core_i2c` (consumed by Release-One via RoomIQ comfort) |
| [`packages/expansions/comfort_ceiling_s3.yaml`](../../packages/expansions/comfort_ceiling_s3.yaml) | 24 | `comfort_i2c_id` | `i2c_primary` | **out-of-scope** (S3 board lineage) |
| [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) | 26 | `fan_dac_i2c_id` | `i2c0` | `core_i2c` |
| [`packages/expansions/gpio_expander_sx1509.yaml`](../../packages/expansions/gpio_expander_sx1509.yaml) | 15 | `sx1509_i2c_id` | `i2c1` | `core_i2c` |
| [`packages/hardware/mini_onboard_sensors.yaml`](../../packages/hardware/mini_onboard_sensors.yaml) | 19 | `mini_sensors_i2c_id` | `i2c0` | **out-of-scope** (Mini baseline; already on schematic-correct pins) |

**C. Hard-coded `i2c_id:` literals (no override hook).**

| File | Line | Literal | Action |
|---|---|---|---|
| [`packages/features/ceiling_halo_leds.yaml`](../../packages/features/ceiling_halo_leds.yaml) | 6 | `i2c_id: halo_i2c` | **Rebind to `i2c_id: core_i2c`**. Per PR #519 audit this file had no product `!include`r; as of 2026-05-22 it is included by four products — [`products/sense360-core-ceiling.yaml`](../../products/sense360-core-ceiling.yaml) line 73, [`products/sense360-core-ceiling-bathroom.yaml`](../../products/sense360-core-ceiling-bathroom.yaml) line 66, [`products/sense360-core-ceiling-presence.yaml`](../../products/sense360-core-ceiling-presence.yaml) line 62, [`products/sense360-core-voice-ceiling.yaml`](../../products/sense360-core-voice-ceiling.yaml) line 76. The literal **must** be rebound (not dead-code-retired) so those four products continue to parse |

**D. LED / halo-specific buses.** `packages/hardware/led_ring_ceiling.yaml`
binds `led_data_pin: GPIO38` (WS2812B, **not** I²C — out of scope).
The `halo_i2c` bus name lived in
[`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml)
and the `pca9685` block in
[`packages/features/ceiling_halo_leds.yaml`](../../packages/features/ceiling_halo_leds.yaml);
both are renamed to `core_i2c` (per categories A and C). No
separate "halo I²C bus" survives the rename.

**E. GP8403 / FanDAC consumers.** Single consumer:
[`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)
line 26 (`fan_dac_i2c_id: i2c0 → core_i2c`). The `gp8403:` block at
lines 40–43 references `${fan_dac_i2c_id}` so no further edit is
needed inside that file once the default is updated. The `output:
- platform: gp8403` block (lines 48–57) binds to the `gp8403:` id and
is not I²C-bound directly.

**F. SX1509 expander consumers.** Single consumer:
[`packages/expansions/gpio_expander_sx1509.yaml`](../../packages/expansions/gpio_expander_sx1509.yaml)
line 15 (`sx1509_i2c_id: i2c1 → core_i2c`). The `sx1509:` block at
lines 23–25 references `${sx1509_i2c_id}` so no further edit is
needed. The 16 channel definitions at lines 30–68 bind to the
`sx1509_expander` id and are not I²C-bound directly. The
`sx1509_interrupt_pin: GPIO17` rebind landed under `001C` / PR #557
and is not touched by `001B`.

**G. RoomIQ / VentIQ / AirIQ sensor consumers.** Eleven consumers
(category B above). Release-One
([`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq.yaml))
resolves `expansion_i2c → core_i2c` indirectly via VentIQ
([`packages/expansions/airiq_bathroom_base.yaml`](../../packages/expansions/airiq_bathroom_base.yaml)
line 29) and RoomIQ comfort
([`packages/expansions/comfort_ceiling.yaml`](../../packages/expansions/comfort_ceiling.yaml)
line 39). The LED preview product
([`products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq-led.yaml))
follows the same path plus a WS2812B LED ring (non-I²C).
**Expected Release-One / LED preview `esphome config`
generated-config diff:** every I²C-bound sensor entity moves from
`i2c_id: expansion_i2c` to `i2c_id: core_i2c` and every bus definition
moves from `id: halo_i2c` + `id: expansion_i2c` to a single
`id: core_i2c` on `sda: GPIO48` / `scl: GPIO45`. No entity name change,
no `config_string` change, no `artifact_name` change, no LED-ring
pin change.

**H. Unused / dead / legacy references.** None. Every literal under
`grep -RIln "halo_i2c\|expansion_i2c\|i2c_primary\|i2c_expander" packages products`
resolves to an active consumer in categories A–G above. Re-verified
2026-05-22.

**I. Tests and config catalogs.** Two test files mention
`CORE-ABSTRACT-BUS-001B` as a blocker label (not a bus id):
[`tests/test_compile_expansion_candidates.py`](../../tests/test_compile_expansion_candidates.py)
line 131 and lines 462 / 487 / 512. One config catalog,
[`config/compile-only-candidates.json`](../../config/compile-only-candidates.json),
carries the `001B` blocker label on the FanPWM (`S360-311`) and
FanDAC (`S360-312`) compile-only candidate rows. **No** I²C bus id
appears in `config/firmware-combination-matrix.json` or in any
other JSON catalog. Test helper
[`tests/generate_test_configs.py`](../../tests/generate_test_configs.py)
line 145 records `fan_dac_i2c_id: expansion_i2c` as a per-product
override for the ceiling lineage; this override must be flipped to
`fan_dac_i2c_id: core_i2c` (or, more cleanly, removed entirely once
the default at
[`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)
line 26 is updated).

#### Final desired mapping

After the implementation slice lands, the steady-state shape is:

```yaml
# Every in-scope Core abstract package (substitution layer):
i2c:
  - id: core_i2c
    sda: GPIO48          # IO48 = I2C_SDA per S360-100-R4
    scl: GPIO45          # IO45 = I2C_SCL per S360-100-R4
    frequency: 400kHz    # pulled-up by R22/R21 10 kΩ
```

Every downstream `*_i2c_id` substitution default resolves to
`core_i2c`. Every hard-coded `i2c_id: halo_i2c` literal is rebound
to `i2c_id: core_i2c`. The six legacy bus ids (`halo_i2c`,
`expansion_i2c`, `i2c0`, `i2c1`, `i2c_primary`, `i2c_expander`) are
**removed** from every in-scope Core package — they remain in:

- [`packages/hardware/sense360_core_ceiling_s3.yaml`](../../packages/hardware/sense360_core_ceiling_s3.yaml)
  (`i2c_primary` on `GPIO17` / `GPIO18` — different board layout;
  documented as out-of-scope per decision #10 above).
- [`packages/hardware/sense360_core_mini.yaml`](../../packages/hardware/sense360_core_mini.yaml)
  and the six `sense360-mini-*.yaml` inline product definitions
  (`i2c0` on `GPIO48` / `GPIO45` — Mini baseline; already on the
  schematic-correct pins; documented as out-of-scope per
  decision #10).
- The two S3-variant expansion packages
  ([`packages/expansions/airiq_ceiling_s3.yaml`](../../packages/expansions/airiq_ceiling_s3.yaml)
  line 28, [`packages/expansions/comfort_ceiling_s3.yaml`](../../packages/expansions/comfort_ceiling_s3.yaml)
  line 24) — both default to `i2c_primary` and consume the
  out-of-scope S3 Core (documented as out-of-scope per decision #10).

Every other `halo_i2c` / `expansion_i2c` / `i2c0` / `i2c1` /
`i2c_primary` / `i2c_expander` literal is removed by the same PR.

#### Implementation scope

The future `CORE-ABSTRACT-BUS-001B-IMPLEMENT-001` PR must land **all
of the following as a single atomic slice**:

1. **Core abstract packages (seven files, in-scope per decision #10
   plus the
   [§Scope-extension addendum](#core-abstract-bus-001b--shared-i²c-bus-consolidation-slice)).**
   Replace the dual-bus `i2c:` block with a single `i2c: - id:
   core_i2c, sda: GPIO48, scl: GPIO45, frequency: 400kHz` block.
   Remove the legacy id lines. Remove (or alternatively rename) the
   `i2c0_sda_pin` / `i2c0_scl_pin` / `i2c0_frequency` / `i2c1_*`
   pin-substitution defaults per the **recommended** retirement
   path under [§Refreshed bus-definition inventory (2026-05-22)](#refreshed-bus-definition-inventory-2026-05-22).
2. **Expansion package consumers (11 files in scope per category B
   above).** Rebind every `*_i2c_id` substitution default from the
   legacy bus id to `core_i2c`. Two S3-variant expansion packages
   stay at `i2c_primary` (out of scope).
3. **Feature package consumer.** Rebind the hard-coded
   `i2c_id: halo_i2c` in
   [`packages/features/ceiling_halo_leds.yaml`](../../packages/features/ceiling_halo_leds.yaml)
   line 6 to `i2c_id: core_i2c`. Four product `!include`rs
   (enumerated in category C above) inherit the rename
   automatically.
4. **Test helper.** Update or remove the
   [`tests/generate_test_configs.py`](../../tests/generate_test_configs.py)
   line 145 `fan_dac_i2c_id: expansion_i2c` override. Recommended:
   delete the override — the default at
   [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)
   line 26 resolves correctly to `core_i2c` after the rename.
5. **Pin-pinning test scaffold.** Extend
   [`tests/test_core_abstract_bus.py`](../../tests/test_core_abstract_bus.py)
   with a new `SharedI2CBusTests` class asserting the conditions
   enumerated under [§Test plan for implementation PR](#core-abstract-bus-001b-core_i2c-plan--test-plan).
6. **Release-One generated-config diff check.** Run `esphome config`
   against
   [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq.yaml)
   (Release-One) and
   [`products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq-led.yaml)
   (LED preview sibling) before-and-after the rename. The expected
   diff is the I²C bus identity move only — every I²C-bound sensor
   moves from `i2c_id: expansion_i2c` (or whichever legacy id its
   path resolved to) to `i2c_id: core_i2c`; the single bus block
   moves from `id: halo_i2c` + `id: expansion_i2c` to one
   `id: core_i2c` on `sda: GPIO48` / `scl: GPIO45`. Any other
   change is a regression.
7. **Re-validation pass for every non-Release-One product YAML**
   listed under
   [§Blast radius per Core package](#blast-radius-per-core-package)
   for each of the seven in-scope Core packages. The seven Core
   packages plus the four `ceiling_halo_leds.yaml` `!include`r
   products bring in ~25 product YAMLs. Each must pass
   `python3 tests/validate_configs.py` after the rename.

The PR must update this audit doc's audit log with a new
`### 2026-05-22 — CORE-ABSTRACT-BUS-001B implementation` (or later
date) entry recording the result, mirroring the structure used by
the `001A` and `001C` implementation entries above.

#### Non-goals

The future `001B` implementation slice explicitly does **not**:

- Edit any product YAML (the four `ceiling_halo_leds.yaml`
  `!include`r products inherit the rename via the existing
  `!include` — they are not edited directly).
- Edit any WebFlash wrapper under
  [`products/webflash/`](../../products/webflash/).
- Edit
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json),
  [`config/product-catalog.json`](../../config/product-catalog.json),
  [`config/webflash-builds.json`](../../config/webflash-builds.json),
  [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json),
  [`config/firmware-combination-matrix.json`](../../config/firmware-combination-matrix.json),
  [`config/kit-intent-matrix.json`](../../config/kit-intent-matrix.json),
  [`config/compile-only-targets.json`](../../config/compile-only-targets.json),
  or
  [`config/compile-only-candidates.json`](../../config/compile-only-candidates.json).
- Flip `webflash_build_matrix: true` on any catalog row.
- Add, rename, or delete any `artifact_name` / `webflash_wrapper` /
  `config_string` / `release_one_required_configs` /
  `lifecycle_statuses` / `canonical_modules` / `canonical_power` /
  `forbidden_tokens` / `REQUIRED_CONFIGS` / kit entry.
- Promote any `schematic_status` / `schematic_file`.
- Move `COMPLIANCE-001` for `S360-320` / `S360-400`.
- Build, sign, attach, or import any firmware artifact. No
  GitHub Release. No tag. No checksum. No build-info manifest. No
  proof row.
- Change Release-One identity
  (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable` / artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` / tag
  `v1.0.0`).
- Change LED preview identity
  (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview` / artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`).
- Change FanTRIAC (`blocked` / `HW-005` /
  `webflash_build_matrix: false`).
- Claim `PACKAGE-PWM-001` or `PACKAGE-DAC-001` unblocked. Those
  slices have their own evidence gates beyond `001B`
  (`HW-PINMAP-311-FOLLOWUP` / `HW-PINMAP-312-FOLLOWUP` and BOM
  cross-checks).
- Claim `RELEASE-PWM-001` / `RELEASE-DAC-001` /
  `RELEASE-RELAY-001` / `RELEASE-TRIAC-001` /
  `RELEASE-POWER-400-001` / `RELEASE-POE-410-001` advanced.
- Claim WebFlash import-readiness for any board / family.
- Add a compile-only target for FanPWM / FanDAC. The compile-only
  candidate gating in
  [`config/compile-only-candidates.json`](../../config/compile-only-candidates.json)
  loses one of its blockers (`CORE-ABSTRACT-BUS-001B`) on the FanPWM
  and FanDAC rows once `001B` implementation lands, but the other
  per-row blockers (`HW-PINMAP-311-FOLLOWUP` / `PACKAGE-PWM-001` for
  FanPWM; `HW-PINMAP-312-FOLLOWUP` / `PACKAGE-DAC-001` for FanDAC)
  stay. The `001B` PR does not flip those.

#### Risk notes

1. **Substitution graph reach.** The rename touches eight Core
   packages, 11 expansion packages, one feature file, and one test
   helper — and Release-One + LED preview both consume the
   substitution graph transitively. A single missed consumer would
   break parse-time substitution resolution at `python3
   tests/validate_configs.py` time. The atomic-slice requirement
   (every consumer in one PR) and the pin-pinning regression test
   (asserts every `*_i2c_id` default resolves to `core_i2c`) are the
   two layered guards.
2. **`ceiling_halo_leds.yaml` literal vs override hook.** The
   feature file hard-codes `i2c_id: halo_i2c` rather than reading a
   substitution. The rename target is mechanical (`halo_i2c` →
   `core_i2c`) but a reader who only inspects `grep -RIln
   "i2c_id:.*core_i2c"` might miss the literal because there is no
   substitution default to chase. The implementation PR should
   verify the literal rename with an explicit assertion in the new
   test class.
3. **Out-of-scope ceiling_s3 and Mini lineages.** Two S3 expansion
   packages (`airiq_ceiling_s3.yaml`, `comfort_ceiling_s3.yaml`)
   default to `i2c_primary`, and six Mini product YAMLs define
   their own `i2c0` inline. The implementation PR must explicitly
   **not** rename these. The pin-pinning test should assert their
   continued existence so a future "rename everything" sweep does
   not silently fold them into the Core namespace.
4. **Frequency mismatch in mapping Core.**
   [`packages/hardware/sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml)
   line 104 defines `i2c_primary` at `${i2c0_frequency}Hz` which
   resolves to `100kHz` (not `400kHz`). The implementation PR must
   decide whether the consolidated `core_i2c` bus runs at `400kHz`
   (the Mini precedent at
   [`packages/hardware/sense360_core_mini.yaml`](../../packages/hardware/sense360_core_mini.yaml)
   line 71 is `100kHz`; every other in-scope Core package's `i2c0` /
   `halo_i2c` / `i2c_primary` runs at `400kHz`). **Recommended:**
   inline `frequency: 400kHz` in every in-scope Core package; record
   the Mini `100kHz` default as out-of-scope; record any per-bus
   sensor that requires `100kHz` (none known today) as a future
   per-board override.
5. **Pull-up evidence assumption.** The schematic shows `R22` / `R21`
   10 kΩ pull-ups on `IO48` / `IO45`
   ([`docs/hardware/s360-100-r4-core.md`](s360-100-r4-core.md) §I2C
   bus). The implementation slice depends on that schematic value;
   the slice does **not** add new pull-up evidence or rerun
   `S360-100-BENCH-001`. If a future bench measurement contradicts
   the 10 kΩ value, the `core_i2c` bus may need to move its
   frequency or surface an explicit `frequency:` override hook.
6. **GP8403 / SX1509 share the bus.** Decision #5 routes both the
   GP8403 DAC and the SX1509 expander to `core_i2c`. The Core
   schematic confirms both are on the shared bus (`U3 SX1509`,
   `J7 GP8403`), so this is the schematic-correct topology. No new
   address-collision risk is introduced (GP8403 default `0x58` /
   SX1509 default `0x3E` — both inside the standard 7-bit space).
7. **Voice-variant Cores.** The two voice-variant Core packages
   (`sense360_core_voice_ceiling.yaml`,
   `sense360_core_voice_wall.yaml`) are in scope for `001B` per
   decision #10 (they mirror the same dual-bus topology). This
   matches the `001C` precedent (voice-variant packages were edited
   for the UART / status LED / ALS_INT rebinds) but differs from
   `001A` (voice-variant relay_pin is deliberately deferred). The
   implementation PR's pin-pinning test must assert `core_i2c` in
   every in-scope Core package, voice variants included.
8. **001A / 001C ordering independence.** `001B` is independent of
   `001A` / `001C` ordering per the inter-slice dependency graph
   at [§Inter-slice dependency graph](#inter-slice-dependency-graph).
   Since both `001A` (PR #558) and `001C` (PR #557) have landed,
   there is no longer a sequencing concern. The implementation PR
   should still verify the pre-existing `001A` and `001C`
   assertions in
   [`tests/test_core_abstract_bus.py`](../../tests/test_core_abstract_bus.py)
   continue to pass after the I²C rename.

#### CORE-ABSTRACT-BUS-001B / core_i2c plan — Test plan

The future `001B` implementation PR must extend
[`tests/test_core_abstract_bus.py`](../../tests/test_core_abstract_bus.py)
with a new `SharedI2CBusTests` class (or equivalent) asserting:

1. **Canonical bus id present in every affected Core package.**
   Each of the seven in-scope Core packages
   (`sense360_core.yaml`, `sense360_core_ceiling.yaml`,
   `sense360_core_mapping.yaml`, `sense360_core_poe.yaml`,
   `sense360_core_wall.yaml`, `sense360_core_voice_ceiling.yaml`,
   `sense360_core_voice_wall.yaml`) defines exactly one `i2c:` bus,
   the bus id is `core_i2c`, the `sda:` is `GPIO48`, the `scl:` is
   `GPIO45`, and the `frequency:` is `400kHz`.
2. **Legacy bus ids absent.** None of the seven in-scope Core
   packages contains any of `halo_i2c`, `expansion_i2c`, `i2c0`,
   `i2c1`, `i2c_primary`, `i2c_expander` as a top-level `i2c:` bus
   id (commentary / docstrings may still mention the names; an
   active `id: <legacy>` binding must not survive).
3. **Every `*_i2c_id` consumer default resolves to `core_i2c`.**
   Each of the 11 in-scope expansion-package consumer defaults
   (`airiq.yaml`, `airiq_wall.yaml`, `airiq_ceiling.yaml`,
   `airiq_bathroom_base.yaml`, `airiq_bathroom_pro.yaml`,
   `comfort.yaml`, `comfort_wall.yaml`, `comfort_ceiling.yaml`,
   `fan_gp8403.yaml`, `gpio_expander_sx1509.yaml`) has its
   `*_i2c_id` substitution default equal to `core_i2c`. The two
   S3-variant consumers (`airiq_ceiling_s3.yaml`,
   `comfort_ceiling_s3.yaml`) keep `i2c_primary` (an
   "out-of-scope-preserved" assertion).
4. **Hard-coded `i2c_id: core_i2c` in
   `packages/features/ceiling_halo_leds.yaml`.** The literal at
   line 6 is rebound from `halo_i2c` to `core_i2c`. Assertion is an
   exact-text match on the line (not a substitution-default check).
5. **Package-specific private buses documented.** The two
   out-of-scope Core packages
   (`sense360_core_ceiling_s3.yaml` keeps `i2c_primary` on
   `GPIO17` / `GPIO18`;
   `sense360_core_mini.yaml` keeps `i2c0` on `GPIO48` / `GPIO45`)
   each retain their existing bus definition byte-for-byte. The
   six `sense360-mini-*.yaml` inline product `i2c0` definitions
   also stay byte-for-byte. The test asserts these continued
   existences so a future sweep cannot accidentally rename them.
6. **FanDAC / GP8403 binds `core_i2c`.** The
   [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)
   `fan_dac_i2c_id` substitution default at line 26 equals
   `core_i2c`. The `gp8403:` block at lines 40–43 references
   `${fan_dac_i2c_id}`; the test verifies the runtime resolution.
7. **SX1509 binds `core_i2c`.** The
   [`packages/expansions/gpio_expander_sx1509.yaml`](../../packages/expansions/gpio_expander_sx1509.yaml)
   `sx1509_i2c_id` substitution default at line 15 equals
   `core_i2c`. The `sx1509:` block at lines 23–25 references
   `${sx1509_i2c_id}`; the test verifies the runtime resolution.
8. **Release-One and LED preview products parse.** A smoke test
   asserts `python3 tests/validate_configs.py` exits 0 against the
   full repo (the existing validator already iterates every
   `products/**/*.yaml`).
9. **WebFlash build rows unchanged.**
   [`config/webflash-builds.json`](../../config/webflash-builds.json)
   and
   [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json)
   are byte-identical before and after the rename. The test
   asserts the file SHA256 against the pre-rename baseline (the
   implementation PR records the baseline value in the test
   constant).
10. **No product / catalog / release / WebFlash exposure changes.**
    [`config/product-catalog.json`](../../config/product-catalog.json),
    [`config/hardware-catalog.json`](../../config/hardware-catalog.json),
    [`config/firmware-combination-matrix.json`](../../config/firmware-combination-matrix.json),
    [`config/kit-intent-matrix.json`](../../config/kit-intent-matrix.json),
    [`config/compile-only-targets.json`](../../config/compile-only-targets.json),
    [`config/compile-only-candidates.json`](../../config/compile-only-candidates.json),
    [`manifest.json`](../../manifest.json) (if present),
    `firmware/sources.json` (if present), and every artifact under
    `firmware/` are byte-identical before and after the rename.

The new test class lands in the **same atomic PR** as the YAML
rebind, not before. Test-scaffold-only is explicitly rejected by
[§Why neither Path B nor Path C is taken now](#why-neither-path-b-nor-path-c-is-taken-now)
under the 2026-05-19 `001B` investigation pass and that rejection
stands.

#### Validation plan for this PR (docs-only)

This PR changes no functional code. Running the full validator
suite is therefore expected to pass unchanged:

```text
python3 tests/validate_configs.py
python3 scripts/validate_compile_targets.py --metadata-only
python3 tests/test_core_abstract_bus.py
python3 tests/test_compile_targets.py
python3 tests/test_compile_expansion_candidates.py
python3 tests/test_firmware_combination_matrix.py
python3 tests/test_firmware_build_gap_report.py
python3 tests/validate_webflash_builds.py
python3 -m unittest discover -s tests -p "test_*.py"
```

The expected `git diff` footprint of this PR is restricted to:

- `docs/hardware/core-abstract-bus-reconciliation.md` (this
  audit-log entry and the existing §CORE-ABSTRACT-BUS-001B
  reference becoming `core_i2c`-resolved).
- `UPCOMING_PR.md` (current queue summary refresh, Completed /
  merged PRs row for this PR, queue entry status update).

`git diff packages products products/webflash config scripts tests
.github/workflows components include firmware manifest.json
firmware/sources.json` is expected to be empty.

#### Status as a result

`CORE-ABSTRACT-BUS-001B` moves from `confirmed deferred (Path A
docs-only); four preconditions still open` to
**implementation-plannable** at the planning layer. The
implementation layer remains gated on the items recorded under
[§Implementation scope](#implementation-scope-1) above: the YAML
rebind across the seven in-scope Core packages, the 11 expansion
package consumer rebinds, the
[`packages/features/ceiling_halo_leds.yaml`](../../packages/features/ceiling_halo_leds.yaml)
literal rebind, the test scaffold, the Release-One generated-config
diff check, and the re-validation pass for every non-Release-One
product YAML.

Of the four preconditions enumerated under
[§Four open preconditions](#four-open-preconditions) by PR #519:

| Precondition | Status as of 2026-05-22 |
|---|---|
| 1 — Canonical I²C bus-id decision | **Closed** — `core_i2c` chosen, hard rename only, no aliases by default |
| 2 — `tests/test_core_abstract_bus.py` pin-pinning scaffold | **Open** — extension lands **with** the implementation slice |
| 3 — Re-validation plan for every non-Release-One product YAML | **Open** — designed at [§Implementation scope](#implementation-scope-1) item 7 above; **execution** lands with the implementation slice |
| 4 — Downstream-consumer audit | **Closed by PR #519 / refreshed here** — see [§CORE-ABSTRACT-BUS-001B / core_i2c plan — Consumer inventory](#core-abstract-bus-001b--core_i2c-plan--consumer-inventory) |

#### Queue effect

- `CORE-ABSTRACT-BUS-001B-PLAN-001` (this PR) is recorded in
  [`UPCOMING_PR.md`](../../UPCOMING_PR.md) as the docs-only planning
  record that closes precondition #1 and refreshes precondition #4.
- `CORE-ABSTRACT-BUS-001B` stays in the active queue (next behind
  the in-flight relay / power / PoE evidence-population work),
  blocked at the implementation layer on preconditions #2 and #3
  (test scaffold + non-Release-One product re-validation, both of
  which land **with** the implementation slice).
- `CORE-ABSTRACT-BUS-001A` is **completed-merged** (PR #558).
  Voice-variant `relay_pin` remains deliberately pre-001A out of
  scope per the 001A audit-log entry.
- `CORE-ABSTRACT-BUS-001C` is **completed-merged** (PR #557).
- `PACKAGE-RELAY-001` / `PRODUCT-RELAY-001` /
  `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` /
  `WF-IMPORT-RELAY-001` stay blocked behind `PACKAGE-RELAY-001`
  bench / silkscreen / harness / `K1` BOM gates. `001B` does **not**
  unblock the Relay chain.
- `PACKAGE-PWM-001` / `PRODUCT-PWM-001` / `WEBFLASH-PWM-001` /
  `RELEASE-PWM-001` stay blocked on the underlying
  `HW-PINMAP-311-FOLLOWUP` evidence **and** on `001B`
  implementation. The canonical-id decision recorded here does
  **not** unblock `PACKAGE-PWM-001`; the implementation slice
  must land first.
- `PACKAGE-DAC-001` / `PRODUCT-DAC-001` / `WEBFLASH-DAC-001` /
  `RELEASE-DAC-001` stay blocked on the underlying
  `HW-PINMAP-312-FOLLOWUP` evidence **and** on `001B`
  implementation. The canonical-id decision recorded here does
  **not** unblock `PACKAGE-DAC-001`.
- Release-One stays `Ceiling-POE-VentIQ-RoomIQ`, version `1.0.0`,
  channel `stable`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
  `v1.0.0`.
- LED preview stays `Ceiling-POE-VentIQ-RoomIQ-LED`, status
  `preview`, channel `preview`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`.
- FanTRIAC stays `status: blocked`, `blocker: HW-005`,
  `webflash_build_matrix: false`. HW-005 is not advanced.
- `COMPLIANCE-001` mains-voltage status for `S360-320` / `S360-400`
  unchanged. PoE is SELV and out of scope.
- `S360-100` `schematic_status: verified` (HW-008) unchanged.
  `S360-310` `schematic_status: cataloged_unverified` unchanged.

#### What this entry does **not** do

Mirrors the [§Do-not-change list](#do-not-change-list) above. The
2026-05-22 `001B` core_i2c-plan record:

- Adds **no** package YAML, product YAML, WebFlash wrapper, JSON
  catalog, script, test, workflow, component, include, firmware
  artifact, manifest, GitHub Release, tag, WebFlash import, or kit
  edit. No `i2c:` bus is renamed by this PR. No `*_i2c_id`
  consumer default is changed. No literal `i2c_id: halo_i2c` is
  rebound. No test scaffolding is added.
- Does **not** advance `CORE-ABSTRACT-BUS-001B` past the planning
  layer. The implementation slice must still land separately and
  atomically per [§Implementation scope](#implementation-scope-1).
- Does **not** advance `PACKAGE-PWM-001` / `PACKAGE-DAC-001` /
  `PRODUCT-PWM-001` / `PRODUCT-DAC-001` / `WEBFLASH-PWM-001` /
  `WEBFLASH-DAC-001` / `RELEASE-PWM-001` / `RELEASE-DAC-001` /
  any compile-only candidate row in
  [`config/compile-only-candidates.json`](../../config/compile-only-candidates.json).
- Does **not** advance `PACKAGE-RELAY-001` /
  `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` /
  `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001`. Those have their
  own bench / harness / `K1` BOM gates that are independent of
  `001B`.
- Does **not** promote any `schematic_status` / `schematic_file`.
- Does **not** move `COMPLIANCE-001`.
- Does **not** change Release-One, LED preview, or FanTRIAC
  identity.
- Does **not** claim any new bench / silkscreen / harness / `K1`
  BOM / `S360-100-BENCH-001` evidence. The 001A / 001C / Relay
  bench-evidence chain stays at its pre-this-PR state per the
  audit-log entries above.
- Does **not** claim any WebFlash import-readiness.
- Does **not** add any compile-only target.

The only files this entry touches are this audit-log section in
[`docs/hardware/core-abstract-bus-reconciliation.md`](core-abstract-bus-reconciliation.md)
and the queue refresh in
[`UPCOMING_PR.md`](../../UPCOMING_PR.md) (Current queue summary
bullet, queue entry #N status block, Completed / merged PRs row
for this PR).

### 2026-05-22 — CORE-ABSTRACT-BUS-001B implementation

`CORE-ABSTRACT-BUS-001B-IMPLEMENT-001` applied the schematic-correct
hard rename to the canonical `core_i2c` bus id recorded by the
[2026-05-22 — CORE-ABSTRACT-BUS-001B core_i2c plan](#2026-05-22--core-abstract-bus-001b-core_i2c-plan)
entry above. The implementation slice landed all seven items
enumerated by [§Implementation scope](#implementation-scope-1) in a
single atomic PR.

#### What landed

| Layer | File | Change |
|---|---|---|
| Core abstract | [`packages/hardware/sense360_core.yaml`](../../packages/hardware/sense360_core.yaml) | Dual `i2c0` / `i2c1` block replaced with single `i2c: - id: core_i2c, sda: GPIO48, scl: GPIO45, frequency: 400kHz` block; `i2c0_*` / `i2c1_*` pin substitutions retired |
| Core abstract | [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml) | Dual `halo_i2c` / `expansion_i2c` block replaced with single `core_i2c` block; `halo_i2c_*` / `expansion_i2c_*` pin substitutions retired |
| Core abstract | [`packages/hardware/sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml) | Dual `i2c_primary` / `i2c_expander` block replaced with single `core_i2c` block; `i2c0_*` / `i2c1_*` pin and frequency substitutions retired; `i2c_primary_healthy` / `i2c_expander_healthy` globals consolidated to single `core_i2c_healthy` flag |
| Core abstract | [`packages/hardware/sense360_core_poe.yaml`](../../packages/hardware/sense360_core_poe.yaml) | Dual `i2c0` / `i2c1` block replaced with single `core_i2c` block; `i2c0_*` / `i2c1_*` pin substitutions retired |
| Core abstract | [`packages/hardware/sense360_core_wall.yaml`](../../packages/hardware/sense360_core_wall.yaml) | Dual `i2c0` / `i2c1` block replaced with single `core_i2c` block; `i2c0_*` / `i2c1_*` pin substitutions retired |
| Core abstract | [`packages/hardware/sense360_core_voice_ceiling.yaml`](../../packages/hardware/sense360_core_voice_ceiling.yaml) | Dual `halo_i2c` / `expansion_i2c` block replaced with single `core_i2c` block; `i2c0_*` / `expansion_i2c_*` pin substitutions retired |
| Core abstract | [`packages/hardware/sense360_core_voice_wall.yaml`](../../packages/hardware/sense360_core_voice_wall.yaml) | Dual `i2c0` / `i2c1` block replaced with single `core_i2c` block; `i2c0_*` / `i2c1_*` pin substitutions retired |
| Expansion | [`packages/expansions/airiq.yaml`](../../packages/expansions/airiq.yaml) | `airiq_i2c_id: i2c0` → `core_i2c` |
| Expansion | [`packages/expansions/airiq_wall.yaml`](../../packages/expansions/airiq_wall.yaml) | `airiq_i2c_id: i2c0` → `core_i2c` |
| Expansion | [`packages/expansions/airiq_ceiling.yaml`](../../packages/expansions/airiq_ceiling.yaml) | `airiq_i2c_id: expansion_i2c` → `core_i2c`; `airiq_i2c_sda` / `airiq_i2c_scl` rebound to `GPIO48` / `GPIO45` |
| Expansion | [`packages/expansions/airiq_bathroom_base.yaml`](../../packages/expansions/airiq_bathroom_base.yaml) | `bathroom_i2c_id: expansion_i2c` → `core_i2c` |
| Expansion | [`packages/expansions/airiq_bathroom_pro.yaml`](../../packages/expansions/airiq_bathroom_pro.yaml) | `bathroom_i2c_id: expansion_i2c` → `core_i2c` |
| Expansion | [`packages/expansions/comfort.yaml`](../../packages/expansions/comfort.yaml) | `comfort_i2c_id: i2c0` → `core_i2c` |
| Expansion | [`packages/expansions/comfort_wall.yaml`](../../packages/expansions/comfort_wall.yaml) | `comfort_i2c_id: i2c0` → `core_i2c` |
| Expansion | [`packages/expansions/comfort_ceiling.yaml`](../../packages/expansions/comfort_ceiling.yaml) | `comfort_ceiling_i2c_id: expansion_i2c` → `core_i2c`; `comfort_ceiling_i2c_sda` / `comfort_ceiling_i2c_scl` rebound to `GPIO48` / `GPIO45`; J1 pinout comment refreshed |
| Expansion | [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) | `fan_dac_i2c_id: i2c0` → `core_i2c` (FanDAC alias `packages/expansions/fan_dac.yaml` inherits via `!include`) |
| Expansion | [`packages/expansions/gpio_expander_sx1509.yaml`](../../packages/expansions/gpio_expander_sx1509.yaml) | `sx1509_i2c_id: i2c1` → `core_i2c` |
| Feature | [`packages/features/ceiling_halo_leds.yaml`](../../packages/features/ceiling_halo_leds.yaml) | Hard-coded `i2c_id: halo_i2c` → `i2c_id: core_i2c` (the PCA9685 halo LED driver now binds the shared Core I²C bus) |
| Test helper | [`tests/generate_test_configs.py`](../../tests/generate_test_configs.py) | Removed the per-product `fan_dac_i2c_id: expansion_i2c` override (line 145 in PR #568); the new default at `fan_gp8403.yaml` resolves to `core_i2c` directly |
| Test scaffold | [`tests/test_core_abstract_bus.py`](../../tests/test_core_abstract_bus.py) | New `SharedI2CBusTests` class (13 cases): canonical `core_i2c` bus present in each in-scope Core package with `GPIO48` / `GPIO45` / `400kHz`; legacy bus ids absent; each in-scope Core defines exactly one i2c bus; every in-scope `*_i2c_id` consumer default equals `core_i2c`; `ceiling_halo_leds.yaml` literal rebound; FanDAC / GP8403 bind `core_i2c` via substitution; FanDAC alias `!include`s the GP8403 implementation; SX1509 binds `core_i2c` via substitution; `generate_test_configs.py` no longer sets `expansion_i2c` override; ceiling_s3 retains `i2c_primary`; Mini retains `i2c0`; no legacy bus id appears on any active consumer line outside the documented out-of-scope set; no legacy pin substitutions survive in the seven in-scope Core packages |

#### Out-of-scope packages — verified unchanged

The implementation slice deliberately leaves the following packages
byte-for-byte unchanged on the I²C bus axis, matching the
[2026-05-22 — CORE-ABSTRACT-BUS-001B core_i2c plan §Final desired mapping](#final-desired-mapping)
exception list:

- [`packages/hardware/sense360_core_ceiling_s3.yaml`](../../packages/hardware/sense360_core_ceiling_s3.yaml)
  retains `i2c_primary` on `GPIO17` / `GPIO18` (different board
  lineage; operator decision #10).
- [`packages/hardware/sense360_core_mini.yaml`](../../packages/hardware/sense360_core_mini.yaml)
  retains `i2c0` on `GPIO48` / `GPIO45` (Mini baseline already on the
  schematic-correct pins; operator decision #10).
- [`packages/expansions/airiq_ceiling_s3.yaml`](../../packages/expansions/airiq_ceiling_s3.yaml)
  retains `airiq_i2c_id: i2c_primary` (S3 lineage).
- [`packages/expansions/comfort_ceiling_s3.yaml`](../../packages/expansions/comfort_ceiling_s3.yaml)
  retains `comfort_i2c_id: i2c_primary` (S3 lineage).
- [`packages/hardware/mini_onboard_sensors.yaml`](../../packages/hardware/mini_onboard_sensors.yaml)
  retains `mini_sensors_i2c_id: i2c0` (Mini baseline).
- The six `products/sense360-mini-*.yaml` inline product
  `i2c0` definitions and their `i2c_id: i2c0` consumer lines (Mini
  baseline).

The new `SharedI2CBusTests.test_out_of_scope_ceiling_s3_keeps_i2c_primary`
and `SharedI2CBusTests.test_out_of_scope_mini_keeps_i2c0` assertions
lock these against future regression.

#### Validation result

Static validation against the post-rename repo state:

- `python3 tests/validate_configs.py` — **PASS** (202 files checked,
  0 failed). Every Core / power / LED / expansion / feature package
  and every product YAML parses with the new `core_i2c` bus.
- `python3 scripts/validate_compile_targets.py --metadata-only` —
  **PASS** (8 compile-only targets validated).
- `python3 tests/test_core_abstract_bus.py` — **PASS** (33 cases:
  20 pre-existing 001A / 001C cases + 13 new
  `SharedI2CBusTests` cases).
- `python3 -m unittest discover -s tests -p "test_*.py"` — **PASS**
  (515 tests; +13 vs the pre-001B baseline of 502).

ESPHome is **not** available in this implementation environment, so
the `esphome config` generated-config diff check called out by
[§Implementation scope](#implementation-scope-1) item 6 was **not**
executed. The implementation relies on the static validators above
plus the new `SharedI2CBusTests` substitution-graph assertions. The
expected diff against
[`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq.yaml)
(Release-One) and
[`products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq-led.yaml)
(LED preview) is the I²C bus identity move only — every I²C-bound
sensor moves from `i2c_id: expansion_i2c` (or whichever legacy id
its path resolved to) to `i2c_id: core_i2c`; the single bus block
moves from `id: halo_i2c` + `id: expansion_i2c` to one `id: core_i2c`
on `sda: GPIO48` / `scl: GPIO45` at `frequency: 400kHz`. No entity
name change, no `config_string` change, no `artifact_name` change,
no LED-ring pin change, no WebFlash exposure change, no release-
channel change.

#### Status

`CORE-ABSTRACT-BUS-001B` moves from `implementation-plannable` to
**implemented**. All four preconditions enumerated under
[§Four open preconditions](#four-open-preconditions) are now closed:

| Precondition | Status |
|---|---|
| 1 — Canonical I²C bus-id decision | **Closed** (PR #568; chose `core_i2c`) |
| 2 — `tests/test_core_abstract_bus.py` pin-pinning scaffold | **Closed** (this PR; `SharedI2CBusTests` added) |
| 3 — Re-validation plan for every non-Release-One product YAML | **Closed** (this PR; `python3 tests/validate_configs.py` exits 0 across all 202 configs including the ~25 product YAMLs that transitively consume the affected packages) |
| 4 — Downstream-consumer audit | **Closed** (PR #519 / refreshed PR #568 / verified against the post-rename live YAML by this PR) |

`PACKAGE-PWM-001` and `PACKAGE-DAC-001` are now unblocked only at the
**shared-I²C-bus layer**. Both still require their own per-board
evidence / BOM cross-checks (`HW-PINMAP-311-FOLLOWUP` /
`HW-PINMAP-312-FOLLOWUP`) and stay blocked on those independently.
The compile-only candidate rows for FanPWM (`S360-311`) and FanDAC
(`S360-312`) in
[`config/compile-only-candidates.json`](../../config/compile-only-candidates.json)
keep their remaining blockers; this PR does **not** flip
`PACKAGE-PWM-001` or `PACKAGE-DAC-001` to `complete`, does **not**
add any compile-only target, and does **not** edit the catalog.

#### What this entry does **not** do

Mirrors the non-goals list under
[§Non-goals](#non-goals-2) of the plan entry. The implementation
slice:

- Adds **no** product YAML, WebFlash wrapper, JSON catalog,
  workflow, component, include, firmware artifact, manifest, GitHub
  Release, tag, WebFlash import, or kit edit.
- Does **not** flip `webflash_build_matrix` on any catalog row.
- Does **not** add, rename, or delete any `artifact_name` /
  `webflash_wrapper` / `config_string` /
  `release_one_required_configs` / `lifecycle_statuses` /
  `canonical_modules` / `canonical_power` / `forbidden_tokens` /
  `REQUIRED_CONFIGS` / kit entry.
- Does **not** promote any `schematic_status` / `schematic_file`.
- Does **not** move `COMPLIANCE-001` for `S360-320` / `S360-400`.
- Does **not** claim `PACKAGE-PWM-001` / `PACKAGE-DAC-001` /
  `PRODUCT-PWM-001` / `PRODUCT-DAC-001` / `WEBFLASH-PWM-001` /
  `WEBFLASH-DAC-001` / `RELEASE-PWM-001` / `RELEASE-DAC-001`
  complete.
- Does **not** advance `PACKAGE-RELAY-001` / `PRODUCT-RELAY-001` /
  `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001`.
- Does **not** change Release-One identity
  (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable` / artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`).
- Does **not** change LED preview identity
  (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`).
- Does **not** change FanTRIAC posture (`blocked` / `HW-005` /
  `webflash_build_matrix: false`).
- Does **not** claim WebFlash import-readiness for any board /
  family.
- Does **not** close `S360-100-BENCH-001`,
  `HW-PINMAP-311-FOLLOWUP`, `HW-PINMAP-312-FOLLOWUP`,
  `HW-PINMAP-320-FOLLOWUP`, or `COMPLIANCE-001`.
- Does **not** add any compatibility alias. The Mini-family `i2c0`
  and S3-family `i2c_primary` are preserved as **package-private**
  bus ids on different board lineages (documented out-of-scope per
  operator decision #10), not as aliases of `core_i2c`.

### Next audit-log trigger

The next CORE-ABSTRACT-BUS-001 audit-log entry should appear when one
of the following lands:

- S360-100-BENCH-001 silkscreen evidence (Core `J4`, Core `J10`,
  RoomIQ `J6` pin orders) committed to the repo with operator
  attribution.
- ESP32-S3 `GPIO3` strap-pin boot-behaviour characterisation against
  populated `S360-310-R4` + `S360-100-R4` pair (general, not the
  pair-scoped operator-confirmed OK recorded by 001C operator
  decisions #16 / #17).
- An `esphome config` generated-config diff against Release-One
  ([`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq.yaml))
  and the LED preview sibling
  ([`products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq-led.yaml))
  is captured in an environment where ESPHome is installed, so the
  bus-identity-only diff expected by
  [§Implementation scope](#implementation-scope-1) item 6 can be
  recorded as evidence (this implementation pass relies on the
  static `SharedI2CBusTests` + `tests/validate_configs.py` exits-0
  validation only).
- Voice-variant Core `relay_pin` rebind is scoped (the pre-001A
  `relay_pin: GPIO4` in
  [`packages/hardware/sense360_core_voice_ceiling.yaml`](../../packages/hardware/sense360_core_voice_ceiling.yaml)
  and
  [`packages/hardware/sense360_core_voice_wall.yaml`](../../packages/hardware/sense360_core_voice_wall.yaml)
  remains deliberately out of scope for `001A` and `001B`; a future
  audit must decide whether and how to rebind it).

Until any of those land, the next audit-log entry should report the
same `CORE-ABSTRACT-BUS-001B implemented; Release-One generated-
config diff still uncaptured (ESPHome unavailable at implementation
time)` outcome with the new inspection date.

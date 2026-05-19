# Core Abstract Bus Reconciliation (CORE-ABSTRACT-BUS-001)

## Status

**Status: docs-only investigation — implementation deferred and split into
three slices (`CORE-ABSTRACT-BUS-001A` / `B` / `C`).**

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

### Next audit-log trigger

The next CORE-ABSTRACT-BUS-001 audit-log entry should appear when one
of the following lands:

- S360-100-BENCH-001 silkscreen evidence (Core `J4`, Core `J10`,
  RoomIQ `J6` pin orders) committed to the repo with operator
  attribution.
- ESP32-S3 `GPIO3` strap-pin boot-behaviour characterisation against
  populated `S360-310-R4` + `S360-100-R4` pair.
- RoomIQ / AirIQ / VentIQ rebind plan committed to a sibling doc.
- Expansion-GPIO bench evidence committed, or a documented decision
  to retire the `expansion_gpio*` abstraction recorded in
  [§CORE-ABSTRACT-BUS-001C — UART / status LED / PIR / expansion GPIO slice](#core-abstract-bus-001c--uart--status-led--pir--expansion-gpio-slice).
- **Canonical I²C bus-id decision** recorded against `001B`
  (from candidates `shared_i2c` / `core_i2c` / `i2c0`, or another
  name justified by the slice).
- `tests/test_core_abstract_bus.py` scaffold lands together with
  the first implementation slice (`001A`, `001B`, or `001C`).
- Implementation slice `CORE-ABSTRACT-BUS-001C` lands (rebinding
  `comfort_ceiling_als_int_pin: GPIO3 → GPIO47`, freeing `GPIO3`
  for the relay slice; UART split; status LED move off `GPIO48`;
  `pir_sensor_pin: GPIO47 → GPIO15`; `expander_int_pin: GPIO3 → GPIO17`;
  `sx1509_interrupt_pin: GPIO3 → GPIO17`; `expansion_gpio*` rebind or
  retirement; pin-pinning test).
- Implementation slice `CORE-ABSTRACT-BUS-001A` lands (rebinding
  `relay_pin → GPIO3` across Core packages).
- Implementation slice `CORE-ABSTRACT-BUS-001B` lands (collapsing
  the duplicated I²C bus definitions to the single shared bus on
  `IO48 / IO45`; rebinding every downstream `*_i2c_id` consumer
  including
  [`packages/features/ceiling_halo_leds.yaml`](../../packages/features/ceiling_halo_leds.yaml)'s
  hard-coded `i2c_id: halo_i2c` literal or retiring the file as
  dead code).

Until any of those land, the next audit-log entry should report the
same `CORE-ABSTRACT-BUS-001B / 001C investigation pass — preconditions
still open` outcome with the new inspection date.

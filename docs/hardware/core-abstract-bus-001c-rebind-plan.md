# CORE-ABSTRACT-BUS-001C — Rebind plan (schematic-backed)

## Status

**Status: docs-only planning record — implementation still requires a
separate scoped YAML / test PR.**

This document is the schematic-backed and operator-confirmed rebind plan
for **CORE-ABSTRACT-BUS-001C** — the UART / status LED / PIR / ALS_INT /
expander interrupt / expansion GPIO slice of the
`CORE-ABSTRACT-BUS-001` series. It is the planning record that closes
several of the long-standing `001C` preconditions enumerated in
[`docs/hardware/core-abstract-bus-reconciliation.md` §CORE-ABSTRACT-BUS-001C — UART / status LED / PIR / expansion GPIO slice](core-abstract-bus-reconciliation.md#core-abstract-bus-001c--uart--status-led--pir--expansion-gpio-slice)
and at
[`docs/hardware/core-abstract-bus-reconciliation.md` §Six open preconditions](core-abstract-bus-reconciliation.md#six-open-preconditions).

This PR does **not** edit any package YAML, any product YAML, any
WebFlash wrapper, any JSON catalog, any script, any test, any workflow,
any component, any include, any firmware artifact, any release artifact,
any checksum file, any build-info manifest, or any kit / lifecycle /
canonical / required-config / webflash_build_matrix / artifact_name /
webflash_wrapper / config_string entry. It records the schematic-backed
and operator-confirmed decisions needed to unblock `001C` implementation
planning, and nothing else.

`001C` is now **implementation-plannable** — but landing the substitution
map below still requires a separate scoped YAML / test PR that itself
must include (i) the pin-pinning regression test scaffold
`tests/test_core_abstract_bus.py`, (ii) the YAML edits across the affected
Core abstract packages and the affected expansion packages, (iii) the
Release-One generated-config diff check per the
[validation plan for implementation slices](core-abstract-bus-reconciliation.md#validation-plan-for-implementation-slices),
and (iv) the re-validation pass for every non-Release-One product YAML
listed under
[§Blast radius per Core package](core-abstract-bus-reconciliation.md#blast-radius-per-core-package).

`001C` must land at-or-before `001A` (the `relay_pin: GPIO3` slice) so
that the `GPIO3` collision recorded in
[`docs/hardware/core-abstract-bus-reconciliation.md` §GPIO collision matrix](core-abstract-bus-reconciliation.md#gpio-collision-matrix)
is resolved before the relay slice tries to consume `GPIO3`.

## Evidence summary

### Provenance

Schematic-backed evidence in this doc is sourced from the committed
`S360-100-R4` Core schematic and `S360-200-R4` RoomIQ schematic. Both
PDFs are committed under HW-007 / HW-ASSETS-001:

- [`docs/hardware/schematics/S360-100-R4.pdf`](schematics/S360-100-R4.pdf)
  — Sense360 Core (`S360-100-R4`).
- [`docs/hardware/schematics/S360-200-R4.pdf`](schematics/S360-200-R4.pdf)
  — Sense360 RoomIQ (`S360-200-R4`).

The S360-100-R4 schematic is classified `schematic_status: verified`
under HW-008 per
[`config/hardware-catalog.json`](../../config/hardware-catalog.json).
Bench-side / silkscreen-side closure of `S360-100-BENCH-001` remains
`pending — bench/manufacturing evidence required` per
[`docs/hardware/s360-100-r4-core.md` §S360-100-BENCH-001 status](s360-100-r4-core.md#s360-100-bench-001-status);
this rebind plan is **not** a closure of `S360-100-BENCH-001`. The
operator-confirmed decisions below stand on schematic evidence plus
operator review of the committed schematic screenshots; full
bench-side silkscreen evidence (Core `J4` 1-to-3 pin order, Core `J10`
1-to-12 pin order, RoomIQ `J6` 1-to-12 pin order, harness identity,
continuity traces, board-serial / batch attribution) remains owed to
the later `S360-100-BENCH-001` closure PR.

### Operator-confirmed decisions

The following decisions are recorded from operator review against the
committed `S360-100-R4` schematic and `S360-200-R4` schematic. They
unblock the `001C` planning layer but do **not** by themselves close
the bench-side silkscreen / harness / continuity gates owned by
`S360-100-BENCH-001`.

1. **Screenshots used in this review come from the committed
   S360-100-R4 schematic** at
   [`docs/hardware/schematics/S360-100-R4.pdf`](schematics/S360-100-R4.pdf).
2. **Core J10 carries the following twelve nets**, in connector pin
   order on the Core side:
   - `SEN0609_RX`
   - `SEN0609_TX`
   - `out(gpio6)`
   - `Hi-Link_RX`
   - `Hi-Link_TX`
   - `PIR`
   - `ALS_INT`
   - `I2C_SDA`
   - `I2C_SCL`

   (The remaining J10 pins are `+3.3V`, `+5V`, and `GND` — confirmed
   present per the schematic net inventory at
   [`docs/hardware/s360-100-r4-core.md` §J10 — Presence / Comfort module connector (12-pin)](s360-100-r4-core.md#j10--presence--comfort-module-connector-12-pin)
   and at [§ESP32-S3 pin and net mapping](s360-100-r4-core.md#esp32-s3-pin-and-net-mapping)
   lines 89–94, 109–111, and 121–122.)
3. **RoomIQ J6 schematic shows the same net order as Core J10** —
   i.e. the connector mates as a straight-through pair on the
   schematic.
4. **The Core J10 to RoomIQ J6 harness is intended straight-through,
   pin 1 to pin 1** — no twist, no swap, no cross-over.
5. **UART labels are ESP32 / Core-perspective**, not radar-module
   perspective:
   - `Hi-Link_TX` = ESPHome `tx_pin` (ESP32 transmits to Hi-Link)
   - `Hi-Link_RX` = ESPHome `rx_pin` (ESP32 receives from Hi-Link)
   - `SEN0609_TX` = ESPHome `tx_pin` (ESP32 transmits to SEN0609)
   - `SEN0609_RX` = ESPHome `rx_pin` (ESP32 receives from SEN0609)
6. **Both Hi-Link and SEN0609 radar UARTs are populated / intended to
   be supported** on the RoomIQ module.
7. **Baud rates confirmed** for each radar UART:
   - `Hi-Link` = **256000**
   - `SEN0609` = **115200**
8. **S360-300 LED ring / status ring data is `GPIO38` / `LED_DATA`**,
   buffered by U2A 74LVC1G07 → `LED_DATA_3V3` → R8 330 Ω → J3 WS2812B
   connector. This line is owned by the LED ring package (e.g.
   [`packages/hardware/led_ring_ceiling.yaml`](../../packages/hardware/led_ring_ceiling.yaml))
   already reconciled under HW-010; **not** by the Core abstract
   `status_led_*` substitutions.
9. **The generic Core `status_led_pin` substitution should be
   retired.** It currently binds to schematic-conflicting GPIOs (the
   shared I²C SDA on `GPIO48`, the RoomIQ Hi-Link TX on `GPIO2`, the
   ALS_INT line on `GPIO47`, and the AirIQ LED on `GPIO8` across
   different Core variants — see
   [`docs/hardware/core-abstract-bus-reconciliation.md` §Status LED substitutions](core-abstract-bus-reconciliation.md#status-led-substitutions)).
10. **`GPIO46` / `GP_Fan_Status_Led` is retained as a Core-side
    indicator** under a function-specific substitution name
    `fan_status_led_pin`. This line is schematic-named on the Core
    board itself (`IO46 = GP_Fan_Status_Led` per Core schematic at
    [`docs/hardware/s360-100-r4-core.md` §ESP32-S3 pin and net mapping](s360-100-r4-core.md#esp32-s3-pin-and-net-mapping)
    line 101) and does not depend on any module being attached.
11. **`GPIO7` / `AirQ_Status_Led` and `GPIO8` / `AirQ_Led` are
    AirIQ-only.** These two lines are the J9 AirIQ module indicator
    lines per Core schematic
    [`docs/hardware/s360-100-r4-core.md` §ESP32-S3 pin and net mapping](s360-100-r4-core.md#esp32-s3-pin-and-net-mapping)
    lines 92–93. They are not Core-baseline indicator lines and must
    be owned by the AirIQ expansion package, not the Core abstract
    `status_led_*` substitutions.
12. **VentIQ has no dedicated Core-driven LED / status line.** This is
    deliberately recorded: VentIQ (`S360-211`) is the bathroom-extract
    variant that mates with J9 in place of AirIQ but does not require
    a Core-driven LED/status indicator line.
13. **Generic `expansion_gpio1..4` substitutions should be retired and
    replaced with function-specific names** bound to schematic nets.
    The current `expansion_gpio1..4` bindings all resolve to
    RoomIQ-claimed nets per
    [`docs/hardware/core-abstract-bus-reconciliation.md` §Expansion GPIO substitutions](core-abstract-bus-reconciliation.md#expansion-gpio-substitutions);
    the abstraction has therefore not earned its keep and the
    function-specific names below replace it.
14. **`out(gpio6)` is the SEN0609 output pin** — the auxiliary
    output line carried alongside the SEN0609 UART (Core schematic
    [`docs/hardware/s360-100-r4-core.md` §ESP32-S3 pin and net mapping](s360-100-r4-core.md#esp32-s3-pin-and-net-mapping)
    line 91, `IO6 = out(gpio6) — J10 RoomIQ auxiliary output`).
15. **Canonical substitution name for `out(gpio6)` is
    `roomiq_sen0609_output_pin`.**
16. **GPIO3 boot / strap behaviour is operator-confirmed OK on
    S360-100-R4 with S360-310 Relay attached.** During operator
    review the populated `S360-310-R4` Relay module was attached to
    the Core J4 connector and the board booted normally with `GPIO3`
    in its ESP32-S3 JTAG-select strap-pin role; no boot loop, no
    JTAG-mode latch was observed. This decision is **scoped to the
    populated `S360-310-R4` + `S360-100-R4` pair under operator
    review**; it is not a generic claim about any future relay /
    expansion module attached to J4.
17. **Relay stayed off / not energized during boot.** The
    `S360-310-R4` relay topology (with `Q1` MMBT3904 NPN low-side
    drive and `K1` mechanical relay coil) was observed to leave the
    relay de-energized at boot with `GPIO3` in its default strap
    state, consistent with the `RESTORE_DEFAULT_OFF` design intent
    recorded for the eventual `relay_pin: GPIO3` slice (`001A`).
18. **S360-310 revision is accepted as R4 for this planning record.**
    Schematic-side / artifact-side classification of the S360-310
    Relay module remains `cataloged_unverified` per
    [`config/hardware-catalog.json`](../../config/hardware-catalog.json);
    this planning record does not promote it.
19. **The S360-310 relay connector / harness is accepted as
    straight-through / keyed correctly for this planning record.**
    Full bench-side harness identity (Core `J4` 1-to-3 pin order,
    module-side `J2` 1-to-3 pin order, harness keying, harness
    continuity trace, `K1` BOM identity / contact rating /
    approvals) remains owed to `S360-100-BENCH-001` closure and to
    `HW-PINMAP-310-FOLLOWUP` (per
    [`docs/hardware/s360-310-r4-relay.md` Required evidence before promotion](s360-310-r4-relay.md#required-evidence-before-promotion)).

The decisions above unblock `001C` **implementation planning**. They
do not, by themselves, close any silkscreen / harness / bench /
compliance / `K1` BOM / `schematic_status: verified` gate. They do
not promote any package, any product, any WebFlash wrapper, or any
release artifact. They make no compliance claim. They make no
WebFlash import-readiness claim. They make no Release-One stable /
release-readiness claim. They make no `RELEASE-RELAY-001` unblock
claim.

## Schematic net tables

The two tables below restate the connector net order on the Core side
and on the RoomIQ side, in the order required for the
straight-through-harness intent recorded above.

### Core J10 — Presence / Comfort module connector (12-pin)

Schematic source:
[`docs/hardware/s360-100-r4-core.md` §J10 — Presence / Comfort module connector (12-pin)](s360-100-r4-core.md#j10--presence--comfort-module-connector-12-pin).

| Pin | Net           | ESP32 pin / role                                | Notes                                                 |
| --- | ------------- | ----------------------------------------------- | ----------------------------------------------------- |
| 1   | +3.3V         | Sensor logic supply                              | Feeds RoomIQ sensors                                  |
| 2   | +5V           | Radar power rail                                 | Feeds Hi-Link / SEN0609 radars                        |
| 3   | SEN0609_RX    | ESP32 `IO4`                                     | DFRobot SEN0609 radar UART RX (Core-perspective)      |
| 4   | SEN0609_TX    | ESP32 `IO5`                                     | DFRobot SEN0609 radar UART TX (Core-perspective)      |
| 5   | out(gpio6)    | ESP32 `IO6`                                     | SEN0609 output / auxiliary line                       |
| 6   | Hi-Link_RX    | ESP32 `IO1`                                     | Hi-Link radar UART RX (Core-perspective)              |
| 7   | Hi-Link_TX    | ESP32 `IO2`                                     | Hi-Link radar UART TX (Core-perspective)              |
| 8   | PIR           | ESP32 `IO15`                                    | PIR motion input                                      |
| 9   | ALS_INT       | ESP32 `IO47`                                    | Ambient-light-sensor interrupt                        |
| 10  | I2C_SDA       | ESP32 `IO48` (shared I²C bus)                   | Pulled up by R22 10 kΩ on Core                        |
| 11  | I2C_SCL       | ESP32 `IO45` (shared I²C bus)                   | Pulled up by R21 10 kΩ on Core                        |
| 12  | GND           | Ground                                          |                                                       |

### RoomIQ J6 — Module-side mate of Core J10 (12-pin)

Schematic source:
[`docs/hardware/s360-200-r4-roomiq.md` §Module connector](s360-200-r4-roomiq.md#module-connector).

| Pin | Net           | RoomIQ-side destination                                                 | Notes                                                 |
| --- | ------------- | ----------------------------------------------------------------------- | ----------------------------------------------------- |
| 1   | +3.3V         | Feeds U1 LTR-303ALS-01, U2 SHT4x, U3 EKMC1601111 PIR, U4 BMP581         | Sensor logic supply                                   |
| 2   | +5V           | Feeds J2 (LD2450 Hi-Link) and J3 (DFRobot SEN0609)                      | Radar power rail                                      |
| 3   | SEN0609_RX    | J3 DFRobot SEN0609 radar UART                                           | Core-perspective TX/RX direction (see decision #5)    |
| 4   | SEN0609_TX    | J3 DFRobot SEN0609 radar UART                                           | Core-perspective TX/RX direction                      |
| 5   | out(gpio6)    | J3 DFRobot SEN0609 auxiliary line                                       | SEN0609 output pin (see decision #14)                 |
| 6   | Hi-Link_RX    | J2 Hi-Link LD2450 radar UART                                            | Core-perspective TX/RX direction                      |
| 7   | Hi-Link_TX    | J2 Hi-Link LD2450 radar UART                                            | Core-perspective TX/RX direction                      |
| 8   | PIR           | U3 EKMC1601111 motion `OUT` pin 2                                       | PIR motion output                                     |
| 9   | ALS_INT       | U1 LTR-303ALS-01 `INT` pin 5                                            | Open-drain interrupt                                  |
| 10  | I2C_SDA       | U1 / U2 / U4 shared I²C bus                                             | Pull-ups on Core side only (R22 10 kΩ)                |
| 11  | I2C_SCL       | U1 / U2 / U4 shared I²C bus                                             | Pull-ups on Core side only (R21 10 kΩ)                |
| 12  | GND           | Ground                                                                  |                                                       |

The two tables match net-for-net in the same pin order, consistent
with the straight-through, pin-1-to-pin-1 harness intent recorded as
operator decision #4 above. The schematic-side discrepancy between
Core J10 and RoomIQ J6 connector-numbering that was previously
flagged in
[`docs/hardware/s360-200-r4-roomiq.md`](s360-200-r4-roomiq.md)
(`+3.3V` vs `+5V` at pin 1 / pin 2 on the two sheets) is **reconciled
in operator review against the schematic screenshots** in favour of
the table above; the canonical source-of-truth is the Core J10 row
order recorded here. Bench-side silkscreen evidence for the physical
pin-1 indicator on each connector remains owed to
`S360-100-BENCH-001`.

## Proposed 001C substitution map

The substitution map below is the **proposed** set of values that the
later `001C` implementation slice should land. This planning record
does **not** edit any package YAML; the values below are
documentation only.

Substitution names that already exist in the codebase keep their
current names. New substitutions introduced by this rebind are
explicitly named function-specific (no generic `expansion_gpio*`).

### RoomIQ UARTs

| Substitution name        | Pin              | Schematic net | Baud rate | Source                                                                                                                                                                              |
| ------------------------ | ---------------- | ------------- | --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `roomiq_hi_link_uart` `tx_pin` | `GPIO2`     | `Hi-Link_TX`  | 256000    | Core schematic [§ESP32-S3 pin and net mapping](s360-100-r4-core.md#esp32-s3-pin-and-net-mapping) line 122; operator decisions #5, #6, #7                                              |
| `roomiq_hi_link_uart` `rx_pin` | `GPIO1`     | `Hi-Link_RX`  | 256000    | Core schematic [§ESP32-S3 pin and net mapping](s360-100-r4-core.md#esp32-s3-pin-and-net-mapping) line 121; operator decisions #5, #6, #7                                              |
| `roomiq_sen0609_uart` `tx_pin` | `GPIO5`     | `SEN0609_TX`  | 115200    | Core schematic [§ESP32-S3 pin and net mapping](s360-100-r4-core.md#esp32-s3-pin-and-net-mapping) line 90; operator decisions #5, #6, #7                                               |
| `roomiq_sen0609_uart` `rx_pin` | `GPIO4`     | `SEN0609_RX`  | 115200    | Core schematic [§ESP32-S3 pin and net mapping](s360-100-r4-core.md#esp32-s3-pin-and-net-mapping) line 89; operator decisions #5, #6, #7                                               |

### RoomIQ GPIO

| Substitution name                                            | Pin     | Schematic net   | Source                                                                                                                                                  |
| ------------------------------------------------------------ | ------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `pir_sensor_pin`                                             | `GPIO15`| `PIR`           | Core schematic [§ESP32-S3 pin and net mapping](s360-100-r4-core.md#esp32-s3-pin-and-net-mapping) line 94                                                  |
| `comfort_ceiling_als_int_pin` (or canonical RoomIQ alias equivalent) | `GPIO47`| `ALS_INT` | Core schematic [§ESP32-S3 pin and net mapping](s360-100-r4-core.md#esp32-s3-pin-and-net-mapping) line 109                                                 |
| `roomiq_sen0609_output_pin`                                  | `GPIO6` | `out(gpio6)`    | Core schematic [§ESP32-S3 pin and net mapping](s360-100-r4-core.md#esp32-s3-pin-and-net-mapping) line 91; operator decisions #14, #15                    |

The `comfort_ceiling_als_int_pin` (or the canonical RoomIQ-aliased
equivalent the implementation slice chooses to expose) is the
substitution currently defined in
[`packages/expansions/comfort_ceiling.yaml`](../../packages/expansions/comfort_ceiling.yaml)
line 42. The eventual implementation slice may also choose to rename
or alias this substitution under the RoomIQ-canonical naming scheme
landed by `PACKAGE-NAMING-ALIASES-ROOMIQ-001` / PR #553 — that
naming choice is left to the implementation PR.

### Expander interrupt

The SX1509 (U3) GPIO/PWM expander interrupt line.

| Substitution name        | Pin     | Schematic net   | Source                                                                                                                |
| ------------------------ | ------- | --------------- | --------------------------------------------------------------------------------------------------------------------- |
| `expander_int_pin`       | `GPIO17`| `expander_int`  | Core schematic [§ESP32-S3 pin and net mapping](s360-100-r4-core.md#esp32-s3-pin-and-net-mapping) line 96                |
| `sx1509_interrupt_pin`   | `GPIO17`| `expander_int`  | Core schematic [§ESP32-S3 pin and net mapping](s360-100-r4-core.md#esp32-s3-pin-and-net-mapping) line 96                |

`expander_int_pin` is defined in
[`packages/hardware/sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml)
line 54 and `sx1509_interrupt_pin` in
[`packages/expansions/gpio_expander_sx1509.yaml`](../../packages/expansions/gpio_expander_sx1509.yaml)
line 17 — both currently bind to `GPIO3` (the schematic-correct
`Relay` net), which is the GPIO3 collision recorded in
[`docs/hardware/core-abstract-bus-reconciliation.md` §GPIO collision matrix](core-abstract-bus-reconciliation.md#gpio-collision-matrix).
Both rebind to `GPIO17`.

### LED / status decisions

| Substitution name           | Pin       | Schematic net           | Source / scope                                                                                                                                                                                                                                                 |
| --------------------------- | --------- | ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `led_data_pin` (LED ring)   | `GPIO38`  | `LED_DATA`              | Owned by LED ring package per HW-010 (e.g. [`packages/hardware/led_ring_ceiling.yaml`](../../packages/hardware/led_ring_ceiling.yaml)); operator decision #8; **not part of this rebind**                                                                       |
| generic Core `status_led_pin` | retired | n/a                     | Operator decisions #9, #12; no Core-baseline status LED net exists on the schematic                                                                                                                                                                            |
| `fan_status_led_pin`        | `GPIO46`  | `GP_Fan_Status_Led`     | Core schematic [§ESP32-S3 pin and net mapping](s360-100-r4-core.md#esp32-s3-pin-and-net-mapping) line 101; operator decision #10                                                                                                                               |
| `airiq_status_led_pin`      | `GPIO7`   | `AirQ_Status_Led`       | Core schematic [§ESP32-S3 pin and net mapping](s360-100-r4-core.md#esp32-s3-pin-and-net-mapping) line 92; operator decision #11; **AirIQ-only**, owned by AirIQ expansion package                                                                              |
| `airiq_led_pin`             | `GPIO8`   | `AirQ_Led`              | Core schematic [§ESP32-S3 pin and net mapping](s360-100-r4-core.md#esp32-s3-pin-and-net-mapping) line 93; operator decision #11; **AirIQ-only**, owned by AirIQ expansion package                                                                              |
| (no VentIQ Core-driven LED) | —         | —                       | Operator decision #12 — VentIQ has no dedicated Core-driven LED / status line                                                                                                                                                                                  |

The S360-300 LED ring remains on `GPIO38 / LED_DATA` and continues to
be owned by the LED ring package (per HW-010 reconciliation). The
S360-300 LED ring `led_data_pin` substitution is **not part of this
rebind** — it was already schematic-correct prior to this planning
record and the rebind plan does not change it.

### Expansion GPIO

| Substitution                | Decision                                                                                                                                                                                                                                                                                                  |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `expansion_gpio1..4`        | **Retired.** Per operator decision #13, the generic `expansion_gpio*` abstraction is replaced with function-specific substitutions (e.g. `roomiq_sen0609_output_pin`, `fan_status_led_pin`, `airiq_status_led_pin`, `airiq_led_pin`, and other function-named substitutions bound to schematic nets).      |

Downstream consumers
([`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml)
binds `fan_pwm_pin: ${expansion_gpio1}` and `fan_tach_pin:
${expansion_gpio2}`;
[`packages/expansions/fan_relay.yaml`](../../packages/expansions/fan_relay.yaml)
override hook on line 25) must each be rebound to schematic-named
substitutions by the `001C` implementation PR. The exact rebind
target is owed to `PACKAGE-PWM-001` / `PACKAGE-RELAY-001` evidence
plus the eventual implementation slice; this rebind plan records the
retirement decision only.

### Relay / 001A dependency

| Item                                                                                | Decision                                                                                                                                                                                                                                                                                                |
| ----------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GPIO3` reservation                                                                 | **Reserved for Relay.** Per Core schematic [§ESP32-S3 pin and net mapping](s360-100-r4-core.md#esp32-s3-pin-and-net-mapping) line 100 (`IO3 = Relay — J4 Relay module gate`).                                                                                                                            |
| 001C effect on `GPIO3`                                                              | **Frees `GPIO3`** by moving `comfort_ceiling_als_int_pin` from `GPIO3` to `GPIO47` (the schematic-correct `ALS_INT` net), and by moving `expander_int_pin` / `sx1509_interrupt_pin` from `GPIO3` to `GPIO17` (the schematic-correct `expander_int` net).                                                  |
| `GPIO3` boot strap behaviour with `S360-310` attached                               | **Operator-confirmed OK** under operator decisions #16 and #17, scoped to the populated `S360-310-R4` + `S360-100-R4` pair under operator review. **Not** a generic claim about any future relay / expansion module attached to J4.                                                                      |
| Relay electrical / load / `K1` rating proof                                         | **Separate evidence stream.** Stays owed to `HW-PINMAP-310-FOLLOWUP` and `PACKAGE-RELAY-001`; **does not become complete in this PR.** No relay electrical / load / contact-rating / `K1` BOM identity / `K1` contact-current rating / harness identity / silkscreen claim is made by this planning record. |

## Implementation readiness classification

`001C` was previously classified `deferred — six preconditions still
open` per
[`docs/hardware/core-abstract-bus-reconciliation.md` §Six open preconditions](core-abstract-bus-reconciliation.md#six-open-preconditions).
This rebind plan closes the *planning* layer of several of those
preconditions:

| Precondition (per [§Six open preconditions](core-abstract-bus-reconciliation.md#six-open-preconditions)) | State after this PR                                                                                                                                                                                                                                                                                                                                                  |
| ----------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. `S360-100-BENCH-001` silkscreen evidence                                                            | **Still open** at the bench-side / silkscreen-side / harness-side / continuity-trace layer. Schematic-side net order is recorded above against the committed `S360-100-R4` and `S360-200-R4` schematic PDFs; full silkscreen / harness / continuity-trace evidence remains owed to `S360-100-BENCH-001` closure.                                                       |
| 2. RoomIQ / AirIQ / VentIQ rebind plan                                                                 | **Closed for RoomIQ** (the substitution map above covers the RoomIQ Hi-Link / SEN0609 UART split, PIR rebind, ALS_INT rebind, and SEN0609 auxiliary output rebind) and **closed at the planning layer for AirIQ / VentIQ** (operator decisions #11, #12 record that `AirQ_Status_Led` and `AirQ_Led` are AirIQ-only and VentIQ has no Core-driven LED). YAML edits still owed. |
| 3. Expansion-GPIO bench evidence or documented retirement decision                                     | **Closed at the planning layer** by operator decision #13 — the generic `expansion_gpio*` abstraction is retired in favour of function-specific substitutions. YAML edits still owed.                                                                                                                                                                                  |
| 4. ESP32-S3 `GPIO3` strap-pin boot-behaviour bench characterisation                                    | **Operator-confirmed OK** for the populated `S360-310-R4` + `S360-100-R4` pair under operator decisions #16 and #17. **Not** a closure of the general boot-strap characterisation evidence — that remains a `001A` precondition recorded against this same row in [`docs/hardware/core-abstract-bus-reconciliation.md`](core-abstract-bus-reconciliation.md). The scope of decisions #16 and #17 is the observed pair under operator review only. |
| 5. `tests/test_core_abstract_bus.py` scaffold                                                          | **Still open.** Per [§Test scaffolding plan](core-abstract-bus-reconciliation.md#test-scaffolding-plan), the test file lands **with** the first implementation slice and is not added by this planning record.                                                                                                                                                          |
| 6. Re-validation pass for every non-Release-One product YAML consuming an affected Core abstract package | **Still open.** Per [§Blast radius per Core package](core-abstract-bus-reconciliation.md#blast-radius-per-core-package), the full re-validation pass lands with the implementation slice; this planning record does not perform it.                                                                                                                                    |

**Outcome.** `001C` is **implementation-plannable** after this PR.
Implementation still requires a separate scoped YAML / test PR that
lands the substitution map above as YAML edits, lands
`tests/test_core_abstract_bus.py` per the test-scaffolding plan, runs
the Release-One generated-config diff check, and runs the
re-validation pass for every non-Release-One product YAML enumerated
in
[`docs/hardware/core-abstract-bus-reconciliation.md` §Blast radius per Core package](core-abstract-bus-reconciliation.md#blast-radius-per-core-package).

## Remaining caveats

The following caveats are recorded so that no reader of this planning
record mistakes it for closure of any of the listed gates.

- **`S360-100-BENCH-001` silkscreen / harness / continuity-trace
  evidence remains owed.** This rebind plan reconciles the
  schematic-side net order against operator review of the committed
  schematic screenshots; bench-side silkscreen captures of Core
  `J4` 1-to-3 pin order, Core `J10` 1-to-12 pin order, RoomIQ `J6`
  1-to-12 pin order, harness keying, harness continuity traces,
  board-serial / batch attribution, and operator / reviewer
  identity / review date for each row remain owed to the later
  `S360-100-BENCH-001` closure PR per
  [`docs/hardware/s360-100-r4-core.md` §S360-100-BENCH-001 status](s360-100-r4-core.md#s360-100-bench-001-status).
- **GPIO3 boot-strap evidence is scoped, not general.** Operator
  decisions #16 and #17 record the observed-OK boot behaviour for
  the populated `S360-310-R4` + `S360-100-R4` pair under operator
  review. They do **not** generalize to any future module attached
  to J4, to any future Core-board revision, or to any future relay
  module revision. They do **not** by themselves substitute for the
  general ESP32-S3 `GPIO3` strap-pin boot-behaviour bench
  characterisation that
  [`docs/hardware/core-abstract-bus-reconciliation.md` §Required evidence before any slice can land](core-abstract-bus-reconciliation.md#required-evidence-before-any-slice-can-land)
  enumerates as a `001A` precondition.
- **`K1` BOM identity, contact-current rating, harness identity, and
  approvals remain owed.** Operator decision #19 accepts the
  Relay connector / harness as straight-through / keyed correctly
  for this planning record only. Full bench-side evidence (Core
  `J4` 1-to-3 pin order, module-side `J2` 1-to-3 pin order, `J1`
  `NO`/`COM`/`NC` mapping, `K1` BOM line item with manufacturer +
  part number + revision, `K1` contact-current rating, `K1` UL /
  EN / IEC approval references, harness continuity trace, harness
  keying / pin-1 indicator) remains owed to
  `HW-PINMAP-310-FOLLOWUP` and to the eventual `PACKAGE-RELAY-001`
  / `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` /
  `RELEASE-RELAY-001` slices per
  [`docs/hardware/s360-310-r4-relay.md` Required evidence before promotion](s360-310-r4-relay.md#required-evidence-before-promotion).
- **`tests/test_core_abstract_bus.py` scaffold is not added by this
  PR.** Per [§Test scaffolding plan](core-abstract-bus-reconciliation.md#test-scaffolding-plan)
  the file lands **with** the first implementation slice. Pinning
  the *current* YAML state would enshrine schematic-conflicting
  values and become a tripwire against the eventual implementation
  slice; pinning the *target* values now would fail immediately
  against the current YAML state. This PR therefore does not add
  the test file.
- **No YAML edit, no package promotion, no product promotion, no
  WebFlash exposure, no release artifact, no compliance claim, no
  WebFlash import-readiness claim, no hardware-release-readiness
  claim is made by this PR.** Specifically:
  - No package YAML edit (everything under
    [`packages/`](../../packages/) stays byte-identical to PR #553
    / `PACKAGE-NAMING-ALIASES-ROOMIQ-001`).
  - No product YAML edit; no product added.
  - No WebFlash wrapper added under
    [`products/webflash/`](../../products/webflash/);
    [`config/webflash-builds.json`](../../config/webflash-builds.json),
    [`config/product-catalog.json`](../../config/product-catalog.json),
    [`config/hardware-catalog.json`](../../config/hardware-catalog.json),
    [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json),
    [`config/firmware-combination-matrix.json`](../../config/firmware-combination-matrix.json),
    [`config/kit-intent-matrix.json`](../../config/kit-intent-matrix.json),
    and
    [`config/compile-only-targets.json`](../../config/compile-only-targets.json)
    stay byte-identical.
  - No compile-only target added.
  - No `artifact_name` / `webflash_wrapper` / `config_string` /
    `webflash_build_matrix` flip / `release_one_required_configs` /
    `lifecycle_statuses` / `canonical_modules` / `canonical_power` /
    `forbidden_tokens` / `REQUIRED_CONFIGS` / kit change.
  - No `schematic_status` / `schematic_file` promotion for any
    board.
  - No `COMPLIANCE-001` movement (PoE is SELV; the mains-voltage
    `S360-320` / `S360-400` slices are unchanged and unrelated to
    `001C`).
  - No Release-One change (`Ceiling-POE-VentIQ-RoomIQ` /
    `v1.0.0` / `stable` /
    `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` / tag
    `v1.0.0`).
  - No LED preview change (`Ceiling-POE-VentIQ-RoomIQ-LED` /
    `preview` /
    `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`).
  - No FanTRIAC change (`blocked` / `HW-005`).
  - No claim that `PACKAGE-RELAY-001` /
    `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` /
    `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001` are advanced or
    unblocked. Relay package implementation stays blocked behind
    `CORE-ABSTRACT-BUS-001A` (which itself is now planning-unblocked
    by this PR but implementation-blocked until `001C`
    implementation lands first).
  - No WebFlash import readiness claim. No
    hardware-release-readiness claim.

## Validation plan

This PR is docs-only. Running the validator suite is expected to
pass unchanged. The implementation slice that consumes this rebind
plan will have its own validation plan per
[`docs/hardware/core-abstract-bus-reconciliation.md` §Validation plan for implementation slices](core-abstract-bus-reconciliation.md#validation-plan-for-implementation-slices),
including the Release-One generated-config diff check and the
re-validation pass for every non-Release-One product YAML.

Commands run against this PR (all pass unchanged):

```text
python3 tests/validate_configs.py
python3 scripts/validate_compile_targets.py --metadata-only
python3 tests/test_compile_targets.py
python3 tests/test_compile_expansion_candidates.py
python3 tests/test_firmware_combination_matrix.py
python3 tests/test_firmware_build_gap_report.py
python3 tests/test_kit_intent_matrix.py
python3 tests/validate_webflash_builds.py
python3 -m unittest discover -s tests -p "test_*.py"
```

The expected `git diff` footprint of this PR is restricted to:

- `docs/hardware/core-abstract-bus-001c-rebind-plan.md` (this new
  file)
- `docs/hardware/core-abstract-bus-reconciliation.md` (audit-log
  addendum cross-linking to this doc)
- `UPCOMING_PR.md` (queue update — completed-merged row plus 001C
  blocker summary refresh)

`git diff packages products products/webflash config scripts tests
.github/workflows components include firmware manifest.json
firmware/sources.json` is expected to be empty.

## See also

- [`docs/hardware/core-abstract-bus-reconciliation.md`](core-abstract-bus-reconciliation.md)
  — `CORE-ABSTRACT-BUS-001` docs-only audit + slice plan; the
  parent doc for all three `001A` / `001B` / `001C` slices.
- [`docs/hardware/s360-100-r4-core.md`](s360-100-r4-core.md) —
  schematic-backed Core pin / net / connector reference.
- [`docs/hardware/s360-200-r4-roomiq.md`](s360-200-r4-roomiq.md) —
  schematic-backed RoomIQ pin / net / connector reference.
- [`docs/hardware/s360-310-r4-relay.md`](s360-310-r4-relay.md) —
  S360-310 Relay module reference; `HW-PINMAP-310-FOLLOWUP` partial
  audit.
- [`docs/release-one-hardware-audit.md`](../release-one-hardware-audit.md)
  — HW-004 Release-One hardware audit; Required follow-ups #2 / #3.
- [`docs/hardware/package-readiness-matrix.md`](package-readiness-matrix.md)
  — PACKAGE-GAP-001 readiness matrix.
- [`docs/hardware/firmware-package-mapping-audit.md`](firmware-package-mapping-audit.md)
  — HW-009 firmware-package-mapping audit.
- [`UPCOMING_PR.md`](../../UPCOMING_PR.md) — repo queue source of
  truth; the `CORE-ABSTRACT-BUS-001C` row at active-queue entry #1
  is updated by this PR.

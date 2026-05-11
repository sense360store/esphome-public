# Release-One Hardware Audit

## Scope

This document audits the Release-One ESPHome shipping configuration —
[`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml) —
against the two schematic-backed hardware references currently committed to
this repository:

- [`docs/hardware/s360-100-r4-core.md`](hardware/s360-100-r4-core.md) —
  Sense360 Core (`S360-100-R4`)
- [`docs/hardware/s360-200-r4-roomiq.md`](hardware/s360-200-r4-roomiq.md) —
  Sense360 RoomIQ (`S360-200-R4`)

It also cross-checks against the canonical naming source of truth:

- [`docs/hardware-catalog.md`](hardware-catalog.md)
- [`config/hardware-catalog.json`](../config/hardware-catalog.json)

…and the WebFlash compatibility contract:

- [`docs/webflash-contract.md`](webflash-contract.md)
- [`config/webflash-builds.json`](../config/webflash-builds.json)
- [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)

The audit covers the Release-One YAML and every package it `!include`s:

- `packages/hardware/sense360_core_ceiling.yaml`
- `packages/hardware/led_ring_ceiling.yaml`
- `packages/features/ceiling_halo_leds.yaml`
- `packages/expansions/fan_triac.yaml`
- `packages/features/fan_control_profile.yaml`
- `packages/expansions/comfort_ceiling.yaml`
- `packages/features/comfort_basic_profile.yaml`
- `packages/expansions/presence_ceiling.yaml`
- `packages/features/presence_basic_profile.yaml`
- `packages/expansions/airiq_bathroom_base.yaml`
- `packages/features/bathroom_profile.yaml`
- `packages/hardware/power_poe.yaml`

This audit is documentation and minimal-fix work only. It does not change
firmware build behaviour, WebFlash manifest behaviour, signing, or release
artifact naming. The WebFlash config string and artifact name for Release-One
remain:

```text
Ceiling-POE-VentIQ-FanTRIAC-RoomIQ
Sense360-Ceiling-POE-VentIQ-FanTRIAC-RoomIQ-v1.0.0-stable.bin
```

## Source hardware references

| Board                | Doc                                                                         | Schematic     | Status                                  |
| -------------------- | --------------------------------------------------------------------------- | ------------- | --------------------------------------- |
| Sense360 Core        | [`s360-100-r4-core.md`](hardware/s360-100-r4-core.md)                       | `S360-100-R4` | schematic-backed / verified             |
| Sense360 RoomIQ      | [`s360-200-r4-roomiq.md`](hardware/s360-200-r4-roomiq.md)                   | `S360-200-R4` | schematic-backed / verified             |
| Sense360 VentIQ      | (not yet committed)                                                         | `S360-211`    | **cataloged, schematic verification pending** |
| Sense360 LED         | (not yet committed)                                                         | `S360-300`    | cataloged, schematic verification pending    |
| Sense360 TRIAC       | (not yet committed)                                                         | `S360-320`    | cataloged, schematic verification pending    |
| Sense360 PoE PSU     | (not yet committed)                                                         | `S360-410`    | cataloged, schematic verification pending    |

Only the two `verified` boards above are considered authoritative for the pin
checks below. Everything else in the catalog is named and SKU'd, but pin
behaviour cannot be confirmed by this audit.

## Summary

The Release-One YAML and its package tree have **systemic mismatches** against
the S360-100-R4 schematic that go beyond what this audit can safely fix
in-place. The firmware composition currently uses an *abstract* "expansion
bus" pin map (`expansion_gpio1`/`2`/`3`/`4`, `halo_i2c`, `expansion_i2c`) in
[`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml)
that does not correspond to the actual S360-100-R4 nets. For example:

| Firmware abstraction (sense360_core_ceiling.yaml) | S360-100-R4 schematic reality                               |
| ------------------------------------------------- | ----------------------------------------------------------- |
| `halo_i2c` on `GPIO39`/`GPIO40`                   | No separate halo I²C bus. The schematic has **one** shared I²C bus on `IO48` (`I2C_SDA`) / `IO45` (`I2C_SCL`). |
| `expansion_i2c` on `GPIO21`/`GPIO18`              | `IO21` is `FAN` (J13). `IO18` is `RST1`. Neither carries I²C. |
| `uart_tx_pin: GPIO1`, `uart_rx_pin: GPIO2`        | `IO1` is `Hi-Link_RX`, `IO2` is `Hi-Link_TX` — the **Hi-Link radar UART for RoomIQ J10**, not a generic expansion UART. |
| `relay_pin: GPIO4`                                | `IO4` is `SEN0609_RX` (RoomIQ radar). The Relay net (`IO3`) is on a different pin. |
| `status_led_pin: GPIO48`                          | `IO48` is `I2C_SDA` (shared I²C bus).                       |
| `pir_sensor_pin: GPIO47`                          | `IO47` is `ALS_INT` (light-sensor interrupt). PIR is on `IO15`. |
| `expansion_gpio1: GPIO5`, `expansion_gpio2: GPIO6` | `IO5` is `SEN0609_TX` (RoomIQ radar). `IO6` is `out(gpio6)` (RoomIQ aux). Neither is a free expansion GPIO. |

Because of that systemic decoupling, the four discrete reconciliation flags
HW-002 raised (FanTRIAC pins, LED data pin, LED-vs-config-string, J10/J6
pin-order) cannot be honestly resolved by editing only the substitution
values in the product YAML — the correct values are not knowable from current
public docs, and inventing them would violate the audit's "no invented pin
mappings" acceptance criterion.

What this audit therefore does:

- **Records** every discrepancy below in the findings table.
- **Removes** the LED package includes from Release-One YAML (per Option A:
  the WebFlash config string `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` does not
  carry a `LED` token, so a Release-One-stamped binary must not light up an
  LED ring as if it were part of this product).
- **Replaces stale legacy names** in Release-One YAML comments with the
  current friendly names from
  [`docs/hardware-catalog.md`](hardware-catalog.md).
- **Marks** FanTRIAC pin mapping in the YAML comments as **blocked /
  unverified** without inventing replacement GPIOs.
- **Marks** VentIQ as **schematic verification pending** in the YAML
  comments because `S360-211` does not yet have a committed schematic.
- **Does not** rename, move, or delete any package file.
- **Does not** change the WebFlash config string, artifact name, or build
  matrix.
- **Does not** edit firmware workflow, signing, or manifest behaviour.

## Findings

| Area                     | Status                                  | Finding                                                                                                                                                                                                                                                                       | Action                                                                                                                                                                                |
| ------------------------ | --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| FanTRIAC                 | **blocked**                             | `fan_triac_gate_pin: GPIO5` and `fan_triac_zc_pin: GPIO6` in Release-One YAML conflict with S360-100-R4: `IO5 = SEN0609_TX` (RoomIQ radar UART) and `IO6 = out(gpio6)` (RoomIQ aux). J15 TRIAC connector carries `TRI_GPIO1` / `TRI_GPIO2`, which appear to route via the SX1509 expander (`U3`), not directly to any ESP32 GPIO. The correct ESP32 ↔ TRIAC mapping is not determinable from current docs. | Mark the substitutions in Release-One YAML as **blocked / unverified** in comments. Do **not** invent SX1509-mapped pins here. Resolve in a later HW PR after the `S360-320` schematic is committed and SX1509-channel ↔ TRI_GPIOx is mapped. |
| Sense360 LED             | **policy decision (removed)**           | WebFlash config string `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` (see [`webflash-contract.md`](webflash-contract.md)) does **not** contain the `LED` token. The `LED` token (`S360-300`) is a separate selectable module. Release-One YAML currently `!include`s both `packages/hardware/led_ring_ceiling.yaml` (WS2812B on `GPIO14`) and `packages/features/ceiling_halo_leds.yaml` (PCA9685 monochromatic halo segments on `halo_i2c`), which are two different LED systems anyway. S360-100-R4 schematic shows `IO14 = SCS` (peripheral SPI chip-select), with `LED_DATA` actually on `IO38`. | **Option A applied**: remove both LED package includes from Release-One YAML so the binary built from this YAML matches the LED-less WebFlash config string. LED packages remain in the repo for other products and for a future `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ-LED` config. Update comment block to drop "Halo LED ring" legacy name. |
| RoomIQ                   | **partial — abstraction mismatch**      | `packages/expansions/comfort_ceiling.yaml` and `packages/expansions/presence_ceiling.yaml` reference firmware-abstraction substitutions (`expansion_i2c`, `uart_bus`, `comfort_ceiling_als_int_pin: GPIO3`) that do **not** match S360-200-R4 / S360-100-R4 J10/J6 nets. Schematic-required signals (`PIR` on `IO15`, `ALS_INT` on `IO47`, `I2C_SDA` on `IO48`, `I2C_SCL` on `IO45`, `Hi-Link_RX/TX` on `IO1`/`IO2`, `SEN0609_RX/TX` on `IO4`/`IO5`, `out(gpio6)` on `IO6`) are not directly bound in the package YAML. The packages function as logical sensor wrappers but the underlying pin map is wrong. | Keep package includes in place (the *logical* RoomIQ composition is correct). Do **not** rename or move package files. Track the full pin-map rework as **HW follow-up** outside this audit. |
| VentIQ                   | **schematic pending**                   | Release-One YAML `!include`s `packages/expansions/airiq_bathroom_base.yaml` and `packages/features/bathroom_profile.yaml`. These represent the `S360-211` (Sense360 VentIQ) module. There is no committed schematic for `S360-211` in this repository yet, so no pin-by-pin verification is possible. The package targets `expansion_i2c` (the same abstract bus as RoomIQ), which is also unverified against S360-100-R4 J9 (AirIQ Module Connector). | Mark VentIQ as **package-level expected / schematic verification pending** in YAML comments. Do **not** claim the J9 pinout is verified. Drop the legacy "Bathroom Pro" name from any user-facing comments. |
| PoE PSU                  | **cataloged, schematic pending**        | `packages/hardware/power_poe.yaml` is a logical PoE-power package that emits diagnostic sensors only; it does not bind to any specific GPIO. The `S360-410` PoE PSU module schematic is not committed to this repo. `S360-100-R4` shows `J2 = PoE_ACDC` (2-pin power inlet to the Core). The exact harness between the off-board PoE PSU and the Core's `J2` is unverified. | No code change. Comment update only — refer to the module as **Sense360 PoE PSU** (`S360-410`), not "PoE module". |
| Core / RoomIQ connector  | **discrepancy**                         | `s360-100-r4-core.md` J10 table puts `+3.3V` at pin 1, `+5V` at pin 2 (signal nets at pins 3–11, `GND` at pin 12). `s360-200-r4-roomiq.md` J6 table puts `+5V` at pin 1, `+3.3V` at pin 7 (signal nets at pins 2–6, 8–11, `GND` at pin 12). These connectors are nominally a mating pair. One of the two tables is wrong. | Capture the discrepancy here only (already flagged in both hardware docs). Do **not** edit either hardware reference doc in this audit PR. Resolve in a follow-up by checking both schematics and the physical silkscreen on `S360-100-R4` and `S360-200-R4` boards. |

### Detail: FanTRIAC

S360-100-R4 nets directly relevant to FanTRIAC:

| Net          | Schematic source / destination                              |
| ------------ | ------------------------------------------------------------ |
| `TRI_GPIO1`  | J15 pin 2 (TRIAC Fan Module connector). Source pin: appears to route through the SX1509 expander (U3) — **not directly visible on a free ESP32 GPIO**. |
| `TRI_GPIO2`  | J15 pin 3. Source pin: same caveat as `TRI_GPIO1`.           |
| `IO5`        | `SEN0609_TX` → J10 RoomIQ pin 4. **Already used by RoomIQ.** |
| `IO6`        | `out(gpio6)` → J10 RoomIQ pin 5. **Already used by RoomIQ.** |

Conclusion: the current `GPIO5` / `GPIO6` substitutions in Release-One YAML
are **provably wrong on a Release-One unit** (because a Release-One unit ships
with RoomIQ, which already claims those pins). The right ESP32 GPIO ↔
`TRI_GPIO1`/`TRI_GPIO2` mapping is not derivable from this repo's docs and
must wait for `S360-320` schematic commit plus SX1509-channel mapping.

### Detail: Sense360 LED policy

The WebFlash module taxonomy at
[`docs/webflash-contract.md`](webflash-contract.md) §3 lists `LED`
(`S360-300`) as a **selectable** module token, alongside `AirIQ`, `VentIQ`,
`RoomIQ`, `FanRelay`, `FanPWM`, `FanDAC`, `FanTRIAC`. The Release-One config
string is:

```text
Ceiling-POE-VentIQ-FanTRIAC-RoomIQ
```

`LED` is not present in this string. Per WebFlash contract rules (§7 module
ordering), a config string that includes a `LED` module would be a different,
explicitly named product — for example:

```text
Ceiling-POE-VentIQ-FanTRIAC-RoomIQ-LED
```

For this audit, that LED-included variant is **out of scope** — the
shipping Release-One slot does not include it. Therefore the LED package
includes are removed from Release-One YAML so that the firmware compiled
from this YAML matches the WebFlash config string.

The two LED package files remain unchanged in the repo (other products and
the future LED-included variant still reference them). The S360-100-R4
schematic reconciliation flags about `IO14` vs `IO38` for `LED_DATA` are
**preserved** in
[`s360-100-r4-core.md`](hardware/s360-100-r4-core.md#led-output) and remain
unresolved; they will be picked up by the future LED-variant audit, not by
Release-One.

### Detail: VentIQ schematic status

- Catalog: `Sense360 VentIQ`, SKU `S360-211`, Rev `R4`.
- Old name: `Bathroom Pro`. Do not reuse `Bathroom Pro` in new user-facing
  text.
- Schematic in this repo: **none committed**.
  [`config/hardware-catalog.json`](../config/hardware-catalog.json) lists
  `S360-211` with `"schematic_status": "cataloged_unverified"`.
- Package YAML used: `packages/expansions/airiq_bathroom_base.yaml`. The
  filename retains the legacy `airiq_bathroom_base` form for backwards
  compatibility (per the WebFlash contract §6 footnote about legacy package
  filenames) — do not rename it in this audit.
- The S360-100-R4 Core schematic shows the VentIQ module would plug into
  `J9` (the "AirIQ Module Connector"), which currently carries the legacy
  `AirQ_Led` / `AirQ_Status_Led` net names. Whether `VentIQ` reuses those
  same physical lines is **verify** — flagged in HW-002 Open Questions #4.

Release-One YAML therefore marks VentIQ as schematic-pending in its comment
block, while keeping the package include.

### Detail: Core / RoomIQ pin-order discrepancy

The two committed hardware docs disagree on the 12-pin RoomIQ connector
pin order:

| Pin | S360-100-R4 J10 table (Core side)   | S360-200-R4 J6 table (RoomIQ side) |
| --- | ------------------------------------ | ----------------------------------- |
| 1   | `+3.3V`                              | `+5V`                               |
| 2   | `+5V`                                | `SEN0609_RX`                        |
| 3   | `SEN0609_RX`                         | `SEN0609_TX`                        |
| 4   | `SEN0609_TX`                         | `out(gpio6)`                        |
| 5   | `out(gpio6)`                         | `Hi-Link_RX`                        |
| 6   | `Hi-Link_RX`                         | `Hi-Link_TX`                        |
| 7   | `Hi-Link_TX`                         | `+3.3V`                             |
| 8   | `PIR`                                | `PIR`                               |
| 9   | `ALS_INT`                            | `ALS_INT`                           |
| 10  | `I2C_SDA`                            | `I2C_SDA`                           |
| 11  | `I2C_SCL`                            | `I2C_SCL`                           |
| 12  | `GND`                                | `GND`                               |

These connectors mate, so one of the two tables is wrong. This audit
**does not** edit either hardware doc — both already flag the discrepancy as
an Open Question. The fix requires confirming the silkscreen on the physical
board. Until then, do not derive firmware pin assignments from either pin
order.

## Required follow-ups

These items are explicitly out of scope for this PR (HW-004) and are written
here so they are not silently lost when later HW PRs land.

1. **TRIAC GPIO source.** Commit `S360-320` schematic; identify which SX1509
   I/O channels drive `TRI_GPIO1` and `TRI_GPIO2`; document the resulting
   ESP32 ↔ SX1509 ↔ J15 path; update `fan_triac.yaml` and Release-One YAML
   accordingly. Only then should the `GPIO5` / `GPIO6` substitutions be
   replaced with verified values (likely SX1509-driven via `gpio_expander_sx1509.yaml`,
   not raw ESP32 pins).
2. **Core-side I²C and UART pinmap.** Realign `sense360_core_ceiling.yaml`
   with the S360-100-R4 schematic so that:
   - `I2C_SDA` is on `IO48`, `I2C_SCL` is on `IO45`.
   - The `Hi-Link` UART (`IO1`/`IO2`) and the `SEN0609` UART (`IO4`/`IO5`)
     are each exposed as separate UART buses with the correct directionality.
   - `Relay` is on `IO3` (not `GPIO4`), `FAN` is on `IO21`, `TachIO` is on
     `IO16`, `expander_int` is on `IO17`.
   - `LED_DATA` is on `IO38` (not `GPIO14`).
   - The duplicated and inconsistent `halo_i2c` / `expansion_i2c` buses are
     reconciled into the single shared I²C bus the schematic actually has.
3. **RoomIQ package pinmap.** Once the Core pinmap is correct, rebind
   `comfort_ceiling.yaml` and `presence_ceiling.yaml` to use the actual
   `PIR`, `ALS_INT`, `I2C_SDA`, `I2C_SCL`, `Hi-Link_*`, `SEN0609_*`, and
   `out(gpio6)` nets via the unified I²C bus and the two radar UARTs.
4. **VentIQ schematic.** Commit `S360-211` schematic + pin/connector
   reference doc, mirroring the structure of
   [`s360-100-r4-core.md`](hardware/s360-100-r4-core.md) and
   [`s360-200-r4-roomiq.md`](hardware/s360-200-r4-roomiq.md). Then verify
   `airiq_bathroom_base.yaml` against it. The Release-One YAML can drop the
   "schematic verification pending" caveat at that point.
5. **LED module schematic.** Commit `S360-300` schematic if a dedicated LED
   variant is added to the Release-One taxonomy. Reconcile `LED_DATA = IO38`
   (Core) with the `GPIO14` value currently in
   `packages/hardware/led_ring_ceiling.yaml`. Only then add `LED` to the
   shipping config string (e.g. `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ-LED`).
   Update `config/webflash-builds.json` and the artifact name in the same
   PR.
6. **PoE PSU schematic.** Commit `S360-410` schematic and confirm the J2
   harness between PSU and Core. No firmware change is expected.
7. **TRIAC PCB.** Commit `S360-320` schematic. Without it FanTRIAC cannot be
   marked verified.
8. **Connector pin-order reconciliation.** Confirm S360-100-R4 J10 vs
   S360-200-R4 J6 pin order against the physical board silkscreen; update
   whichever doc is wrong.

## Files changed

This audit PR changes only the following files:

- `docs/release-one-hardware-audit.md` — new file (this document).
- `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`:
  - Update header `Hardware:` block to use current friendly names from
    [`docs/hardware-catalog.md`](hardware-catalog.md). Drop the legacy
    "Halo LED ring" line.
  - Remove the two LED package `!include`s (`led_ring`, `led_effects`) per
    Option A. The Release-One config string does not include the `LED`
    token; the WebFlash artifact must not bundle LED firmware.
  - Update package-group comments to refer to **Sense360 VentIQ**,
    **Sense360 RoomIQ**, **Sense360 TRIAC**, **Sense360 PoE PSU**, instead
    of stale or legacy names ("AirIQ", "Comfort + Presence", "Halo LED
    ring", "PoE module").
  - Annotate FanTRIAC substitutions (`fan_triac_gate_pin`,
    `fan_triac_zc_pin`) as **blocked / unverified**: keep the existing
    `GPIO5` / `GPIO6` placeholder values so the YAML still parses, but
    document next to them that they conflict with the S360-100-R4 RoomIQ
    nets and that the correct mapping requires `S360-320` plus SX1509-channel
    mapping (see this document).
  - Annotate the VentIQ package group as schematic-pending.
- `docs/release-one.md`: minor link to this audit doc so the audit is
  discoverable from the Release-One page.

This PR does **not** change:

- `packages/hardware/sense360_core_ceiling.yaml` (systemic pinmap rework
  belongs to a separate HW PR — see Required follow-ups).
- `packages/hardware/led_ring_ceiling.yaml` (still used by other products).
- `packages/features/ceiling_halo_leds.yaml` (still used by other products).
- `packages/expansions/fan_triac.yaml` (no GPIO content to change; the
  invalid pins live in the product YAML).
- Any RoomIQ package file (`comfort_ceiling.yaml`, `presence_ceiling.yaml`,
  `comfort_basic_profile.yaml`, `presence_basic_profile.yaml`).
- `packages/expansions/airiq_bathroom_base.yaml` or
  `packages/features/bathroom_profile.yaml`.
- `config/webflash-builds.json`, `config/webflash-compatibility.json`,
  `config/hardware-catalog.json`.
- `docs/webflash-contract.md`, `docs/webflash-ci-alignment.md`,
  `docs/webflash-release-handoff.md`, `docs/hardware/s360-100-r4-core.md`,
  `docs/hardware/s360-200-r4-roomiq.md`, `docs/hardware-catalog.md`.

## See also

- [`docs/release-one.md`](release-one.md) — Release-One shipping
  configuration page.
- [`docs/webflash-contract.md`](webflash-contract.md) — WebFlash
  compatibility contract (config-string grammar, allowed tokens, fan-driver
  rules).
- [`docs/hardware-catalog.md`](hardware-catalog.md) — canonical board /
  module friendly names, SKUs, revisions, and legacy names.
- [`docs/hardware/s360-100-r4-core.md`](hardware/s360-100-r4-core.md) —
  Sense360 Core pin / connector / net reference.
- [`docs/hardware/s360-200-r4-roomiq.md`](hardware/s360-200-r4-roomiq.md) —
  Sense360 RoomIQ pin / connector / net reference.

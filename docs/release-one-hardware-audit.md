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
artifact naming.

> **Update (REL-001):** the production Release-One config string and
> artifact name have since been changed to **exclude** FanTRIAC while the
> blocker captured below remains open. Production Release-One is now:
>
> ```text
> Ceiling-POE-VentIQ-RoomIQ
> Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin
> ```
>
> The FanTRIAC product YAML and WebFlash wrapper are retained in the repo
> as **blocked / reference** files but are NOT in the WebFlash build
> matrix. The FanTRIAC findings, timing constraint, and resolution table
> below all remain authoritative — they are now the gate that decides when
> FanTRIAC can re-enter the production Release-One build.
>
> The pre-REL-001 names are preserved here for historical context:
>
> ```text
> Ceiling-POE-VentIQ-FanTRIAC-RoomIQ
> Sense360-Ceiling-POE-VentIQ-FanTRIAC-RoomIQ-v1.0.0-stable.bin
> ```

## Source hardware references

| Board                | Doc                                                                         | Schematic     | Status                                  |
| -------------------- | --------------------------------------------------------------------------- | ------------- | --------------------------------------- |
| Sense360 Core        | [`s360-100-r4-core.md`](hardware/s360-100-r4-core.md)                       | `S360-100-R4` | schematic-backed / verified (PDF committed under HW-007 at [`hardware/schematics/S360-100-R4.pdf`](hardware/schematics/S360-100-R4.pdf); JSON `schematic_status: verified` with `schematic_file: docs/hardware/schematics/S360-100-R4.pdf` under HW-008) |
| Sense360 RoomIQ      | [`s360-200-r4-roomiq.md`](hardware/s360-200-r4-roomiq.md)                   | `S360-200-R4` | schematic-backed / verified (PDF committed under HW-007 at [`hardware/schematics/S360-200-R4.pdf`](hardware/schematics/S360-200-R4.pdf); JSON `schematic_status: verified` with `schematic_file: docs/hardware/schematics/S360-200-R4.pdf` under HW-008) |
| Sense360 AirIQ       | [`s360-210-r4-airiq.md`](hardware/s360-210-r4-airiq.md)                     | `S360-210-R4` | schematic-backed / verified (PDF committed under HW-007 at [`hardware/schematics/S360-210-R4.pdf`](hardware/schematics/S360-210-R4.pdf); JSON `schematic_status: verified` with `schematic_file: docs/hardware/schematics/S360-210-R4.pdf` under HW-008). Not in Release-One; AirIQ ↔ VentIQ mutex unchanged. |
| Sense360 VentIQ      | [`s360-211-r4-ventiq.md`](hardware/s360-211-r4-ventiq.md)                   | `S360-211-R4` | schematic-backed / verified (PDF committed under HW-007 at [`hardware/schematics/S360-211-R4.pdf`](hardware/schematics/S360-211-R4.pdf); JSON `schematic_status: verified` with `schematic_file: docs/hardware/schematics/S360-211-R4.pdf` under HW-008). VentIQ remains the Release-One air-quality slot. |
| Sense360 LED         | [`s360-300-r4-led.md`](hardware/s360-300-r4-led.md)                         | `S360-300-R4` | schematic-backed / verified (PDF committed under HW-007 at [`hardware/schematics/S360-300-R4.pdf`](hardware/schematics/S360-300-R4.pdf); JSON `schematic_status: verified` with `schematic_file: docs/hardware/schematics/S360-300-R4.pdf` under HW-008). **Sense360 LED remains excluded from Release-One**; HW-008 does not add `LED` to the config string and the `GPIO14` (package) vs `IO38` (schematic) `LED_DATA` discrepancy is still unresolved. |
| Sense360 TRIAC       | (not yet committed)                                                         | `S360-320`    | cataloged, schematic verification pending. **HW-005 blocked**; PDF is not committed; JSON `schematic_status` stays `cataloged_unverified` after HW-008. |
| Sense360 PoE PSU     | (not yet committed)                                                         | `S360-410`    | cataloged, schematic verification pending. PDF is not committed; JSON `schematic_status` stays `cataloged_unverified` after HW-008. |

The pin-by-pin checks below were written against the Core and RoomIQ
schematic-backed reference docs. Under HW-007 + HW-008, AirIQ, VentIQ, and
Sense360 LED also gain module-side schematic PDFs, standalone reference
docs, and `schematic_status: verified` rows in
[`config/hardware-catalog.json`](../config/hardware-catalog.json) with
`schematic_file` values pointing under `docs/hardware/schematics/`. The
pin-binding rework that would turn that hardware evidence into firmware
changes (package-YAML rebinds, Core J10 / RoomIQ J6 pin-order
reconciliation, `GPIO14` vs `IO38` `LED_DATA` reconciliation) is **not**
in scope for this audit and is **not** in scope for HW-008 — both
discrepancies are still open. HW-008 also does **not** change the
Release-One config string, the WebFlash build matrix, the artifact name,
any product YAML, any package YAML, or the FanTRIAC / LED / mains-voltage
policies.

See also: [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md)
— companion HW-004 / HW-006 audit that classifies every catalog row's
documentation state and records evidence available vs. evidence missing.
HW-007 ingest is recorded in
[`hardware/remaining-board-documentation-audit.md#hw-007-schematic-ingest`](hardware/remaining-board-documentation-audit.md#hw-007-schematic-ingest).

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
| FanTRIAC                 | **blocked — must not ship** (HW-005)    | `fan_triac_gate_pin: GPIO5` and `fan_triac_zc_pin: GPIO6` in Release-One YAML conflict with S360-100-R4: `IO5 = SEN0609_TX` (RoomIQ radar UART) and `IO6 = out(gpio6)` (RoomIQ aux). J15 TRIAC connector carries `TRI_GPIO1` / `TRI_GPIO2`, visible only at the SX1509 (`U3`) side of the Core sheet, with no direct ESP32 route. The `S360-320` Sense360 TRIAC schematic is not committed. Additionally, ESPHome's `ac_dimmer` requires direct interrupt-capable ESP32 GPIOs for both `gate_pin` and `zero_cross_pin`, so even a verified SX1509 mapping would not unblock this slot. | See [FanTRIAC mapping resolution](#fantriac-mapping-resolution) for the resolution table, the timing constraint, and the explicit ship verdict. The Release-One FanTRIAC binary must not be published as TRIAC-capable until the `S360-320` schematic plus a verified direct-ESP32 mapping (or a replacement non-`ac_dimmer` driver) is delivered. Do not invent SX1509 pin mappings here. |
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
- Schematic in this repo: **committed** under HW-007 at
  [`hardware/schematics/S360-211-R4.pdf`](hardware/schematics/S360-211-R4.pdf)
  with a standalone reference doc at
  [`hardware/s360-211-r4-ventiq.md`](hardware/s360-211-r4-ventiq.md).
  Under HW-008,
  [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  lists `S360-211` with `"schematic_status": "verified"` and
  `"schematic_file": "docs/hardware/schematics/S360-211-R4.pdf"`.
- Package YAML used: `packages/expansions/airiq_bathroom_base.yaml`. The
  filename retains the legacy `airiq_bathroom_base` form for backwards
  compatibility (per the WebFlash contract §6 footnote about legacy package
  filenames) — do not rename it in this audit.
- The S360-100-R4 Core schematic shows the VentIQ module would plug into
  `J9` (the "AirIQ Module Connector"), which currently carries the legacy
  `AirQ_Led` / `AirQ_Status_Led` net names. Whether `VentIQ` reuses those
  same physical lines is **verify** — flagged in HW-002 Open Questions #4.
  This question is **not** resolved by HW-008.

The Release-One YAML's "VentIQ schematic-pending" comment block is left
unchanged by HW-008 (any YAML edit is out of scope for this PR). The
machine-readable JSON evidence is now `verified`, but the pin-binding
rework that would let firmware claim VentIQ pins are verified against the
schematic is still open.

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

## FanTRIAC mapping resolution

> **HW-005 — still blocked. Missing evidence.**
>
> The Release-One FanTRIAC slot remains **blocked**. The `S360-320` Sense360
> TRIAC schematic is still not committed, no SX1509 channel is allocated to
> `TRI_GPIO1` / `TRI_GPIO2`, and the placeholder `GPIO5` / `GPIO6`
> substitutions in the canonical FanTRIAC product YAML still collide with the
> RoomIQ J10 nets on `S360-100-R4`. See
> [Missing evidence checklist](#missing-evidence-checklist) and
> [Re-verification](#re-verification) below.

This section is the HW-005 resolution for the FanTRIAC pin-mapping blocker
flagged in PR #440 and in the [Findings](#findings) table above. It is the
single explicit answer to "can Release-One ship FanTRIAC firmware today?".

### Verdict

**Outcome C — mapping cannot be verified.** The Release-One FanTRIAC slot is
**blocked**: a binary built from
[`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml)
must **not** be published as TRIAC-capable until the resolution work below is
done. There is additional **Outcome D risk** because the SX1509 expander
cannot meet the timing the ESPHome `ac_dimmer` component requires, so even a
verified SX1509-only mapping would still not unblock this slot — see
[Timing constraint](#timing-constraint-ac_dimmer-vs-sx1509-expander).

### Resolution table

| Question | Answer | Evidence |
| --- | --- | --- |
| Is `TRI_GPIO1` direct ESP32? | **Unverified.** Not visible as a direct ESP32 GPIO on the `S360-100-R4` Core sheet. | [`s360-100-r4-core.md`](hardware/s360-100-r4-core.md#fan--driver-outputs) lists `TRI_GPIO1` only at the J15 connector and on the SX1509 (U3) side. The Open Question is captured explicitly at [Open Questions #1](hardware/s360-100-r4-core.md#open-questions--verification-needed). |
| Is `TRI_GPIO2` direct ESP32? | **Unverified.** Same status as `TRI_GPIO1`. | Same row of [`s360-100-r4-core.md`](hardware/s360-100-r4-core.md#fan--driver-outputs); the source pin is "not unambiguously visible" on the visible Core sheet. |
| SX1509 (U3) involved? | **Strongly suspected, not confirmed.** | The other expander-driven fan nets on the Core sheet (`TachPMW1..4`, `Pul_Cou1..4`) are visible only on the SX1509 side, and `TRI_GPIO1` / `TRI_GPIO2` appear in the same routing region. The repo's SX1509 channel map in [`packages/expansions/gpio_expander_sx1509.yaml`](../packages/expansions/gpio_expander_sx1509.yaml) does **not** allocate any channel to TRIAC (0–3 fan PWM, 4–7 tach, 8–11 aux PWM, 12–15 generic inputs). The `S360-320` schematic that would complete the trace is not committed (`config/hardware-catalog.json` → `S360-320` → `schematic_status: cataloged_unverified`). |
| Timing safe? | **No.** Even if the SX1509 routing is later confirmed, it cannot meet the timing `ac_dimmer` requires. | [`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml) uses ESPHome's `output: ac_dimmer` platform. That platform attaches a hardware interrupt to `zero_cross_pin` and drives `gate_pin` from a timed ISR with sub-millisecond precision. The SX1509 is an I²C-driven expander; register reads/writes go over the shared 400 kHz I²C bus and take hundreds of microseconds each, with no host-visible interrupt for input changes. On 50/60 Hz mains the half-cycle is only ~8.33–10 ms, and gate-firing delay normally needs <100 µs resolution. The expander cannot deliver that. |
| Mapping verified? | **No.** | Two missing pieces: (a) the `S360-320` Sense360 TRIAC schematic is not committed to this repo, and (b) no SX1509 channel in [`packages/expansions/gpio_expander_sx1509.yaml`](../packages/expansions/gpio_expander_sx1509.yaml) is assigned to `TRI_GPIO1` or `TRI_GPIO2`. The current placeholders `fan_triac_gate_pin: GPIO5` and `fan_triac_zc_pin: GPIO6` are **provably wrong** on a Release-One unit because `IO5 = SEN0609_TX` and `IO6 = out(gpio6)` are already claimed by RoomIQ at J10. |
| Release-One allowed to ship with FanTRIAC? | **No.** Do not publish a Release-One binary as FanTRIAC-capable until the resolution work below is complete. | All four rows above are failing. The current YAML still parses, but firmware compiled from it cannot actually drive the J15 TRIAC connector and may attempt to drive RoomIQ UART/aux nets via the dimmer ISR if any of `GPIO5`/`GPIO6` are ever taken seriously. |

### Missing evidence checklist

HW-005 stays blocked until **all** of the following land. Until then,
FanTRIAC is not preview-ready and is not stable-ready. Do not invent any of
these items in the meantime.

- [ ] **`S360-320` Sense360 TRIAC schematic committed** to `docs/hardware/`
  (e.g. `docs/hardware/s360-320-r4-triac.md`), mirroring the structure of
  [`s360-100-r4-core.md`](hardware/s360-100-r4-core.md) and
  [`s360-200-r4-roomiq.md`](hardware/s360-200-r4-roomiq.md), and the
  catalog entry in [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  flipped from `cataloged_unverified` to `verified`.
- [ ] **End-to-end ESP32 ↔ J15 path documented** for `TRI_GPIO1` (gate) and
  `TRI_GPIO2` (zero-cross), traced through `S360-100-R4` + `S360-320`
  together. Acceptable outcomes are (a) direct ESP32 GPIOs or (b) an
  on-board TRIAC controller IC on `S360-320` that exposes only a "dim
  level" interface — see
  [What needs to happen to clear the blocker](#what-needs-to-happen-to-clear-the-blocker)
  for the two acceptable paths and the rejected SX1509-only hypothesis.
- [ ] **Two free, interrupt-capable ESP32 pins identified** (only required
  for outcome (a) above). Pins must not already be consumed by RoomIQ J10
  (`SEN0609_RX/TX`, `out(gpio6)`, `Hi-Link_RX/TX`, `PIR`, `ALS_INT`,
  `I2C_SDA`, `I2C_SCL`), VentIQ/AirIQ J9, the shared I²C bus
  (`IO48`/`IO45`), the SPI peripheral block, UART0, or SX1509 control.
  Update `fan_triac_gate_pin` / `fan_triac_zc_pin` in
  [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml)
  and the example block in
  [`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml)
  to the verified values in the same PR that lands the schematic.
- [ ] **Replacement driver** (only required for outcome (b) above):
  [`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml)
  rewritten to target the on-board TRIAC controller IC over I²C — `ac_dimmer`
  must not be used, because it is the wrong abstraction for an I²C "dim
  level" register.

Until that checklist is fully satisfied:

- The FanTRIAC product YAML, WebFlash wrapper, and `fan_triac.yaml` package
  remain `blocked-reference` and are not added to
  [`config/webflash-builds.json`](../config/webflash-builds.json).
- The Release-One WebFlash config string stays `Ceiling-POE-VentIQ-RoomIQ`
  and the artifact name stays
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`.
- No FanTRIAC binary may be published as TRIAC-capable, even for preview.

### Timing constraint: `ac_dimmer` vs SX1509 expander

`packages/expansions/fan_triac.yaml` instantiates ESPHome's `output: ac_dimmer`
platform. That platform:

- attaches a **hardware interrupt** to `zero_cross_pin` to detect mains
  zero-crossing edges, and
- toggles `gate_pin` from a **timed ISR** at a precise delay after each
  zero-cross to set the phase-cut firing angle.

Both pins must therefore be **direct, interrupt-capable ESP32 GPIOs**. The
SX1509 (U3) is an I²C GPIO/PWM expander. Every read or write of an SX1509
register goes through the shared I²C bus (`IO48/IO45` on `S360-100-R4`,
running at 400 kHz alongside RoomIQ, AirIQ/VentIQ, and the on-board
expander). Each I²C transaction is hundreds of microseconds, sometimes
milliseconds under contention, and the host CPU cannot attach an interrupt
to an SX1509 input pin.

Because of this:

- A zero-cross **input** cannot be reliably timed across I²C — the latency
  alone exceeds the precision phase-cut dimming requires.
- A TRIAC **gate** output cannot be toggled across I²C with sub-millisecond
  precision either — the gate-firing delay between zero cross and gate
  assertion sets the dimmer's output level, so I²C latency would dominate
  and produce flicker, runaway current, or no useful control at all.

Therefore, **even if the suspected SX1509 routing is later confirmed**, the
current `fan_triac.yaml` driver cannot be used as-is to drive
`TRI_GPIO1`/`TRI_GPIO2` through the SX1509. A working FanTRIAC build needs
either:

a. **Direct ESP32 GPIOs** for both the gate and the zero-cross input — both
   pins must be free, interrupt-capable, and not already consumed by RoomIQ
   (J10), VentIQ/AirIQ (J9), the shared I²C bus, the SPI peripheral block,
   UART0/Hi-Link/SEN0609, or SX1509 control; or
b. **A different driver** entirely — for example, an on-board TRIAC
   controller chip on the `S360-320` board that handles all gate-timing
   internally and only exposes a "dim level" register over I²C. In that case
   `packages/expansions/fan_triac.yaml` must be replaced (not just rewired),
   because `ac_dimmer` is the wrong abstraction.

The "use SX1509 channels directly for `gate_pin` / `zero_cross_pin`"
hypothesis is **rejected** for Release-One regardless of how the schematic
turns out.

### What this PR does (HW-005)

This PR does **not** invent GPIOs and does **not** unblock FanTRIAC. It only
makes the blocker more explicit and surfaces the timing constraint:

- Adds this resolution section to the audit doc.
- Updates [`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml)
  header comments to remove the misleading "GPIO5 / GPIO6 = expansion bus"
  example and to spell out the `ac_dimmer` timing requirement (direct,
  interrupt-capable ESP32 GPIOs only — no expander pins).
- Updates the Release-One product YAML header comments to point at this
  resolution section as the single source of truth for the ship verdict.
- Updates [`docs/release-one.md`](release-one.md) with the explicit
  FanTRIAC ship status.

It does **not** change:

- The WebFlash config string `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` (per the
  HW-004 ground rules; removing the FanTRIAC slot from the Release-One
  taxonomy is a separate product decision, not a hardware-audit decision).
- The `config/webflash-builds.json` / `config/webflash-compatibility.json` /
  `config/hardware-catalog.json` entries.
- Any hardware-reference doc under `docs/hardware/`.
- The actual GPIO substitutions in the Release-One YAML — `GPIO5` / `GPIO6`
  remain only so the YAML still parses, with a stronger pointer to this
  resolution section. **A Release-One binary built from this YAML must not
  be published as FanTRIAC-capable.**

### What needs to happen to clear the blocker

1. Commit the `S360-320` Sense360 TRIAC schematic into `docs/hardware/`
   following the structure of
   [`s360-100-r4-core.md`](hardware/s360-100-r4-core.md) and
   [`s360-200-r4-roomiq.md`](hardware/s360-200-r4-roomiq.md).
2. From `S360-100-R4` + `S360-320` together, document the actual end-to-end
   path that drives `TRI_GPIO1` and `TRI_GPIO2`. Acceptable outcomes:

   a. **Direct ESP32 GPIOs.** Identify the specific `IOxx` pins on the
      ESP32-S3 that drive `TRI_GPIO1` (gate) and `TRI_GPIO2` (zero-cross).
      Both must be free, interrupt-capable, and not already consumed by
      RoomIQ, VentIQ/AirIQ, shared I²C, SPI, UART0/Hi-Link/SEN0609, or
      SX1509 control. Then update `fan_triac_gate_pin` and
      `fan_triac_zc_pin` in the Release-One YAML and the example block in
      `packages/expansions/fan_triac.yaml`.
   b. **On-board TRIAC controller IC.** If `S360-320` carries a dedicated
      TRIAC controller that handles gate timing internally and exposes only
      a "dim level" interface over I²C, replace
      `packages/expansions/fan_triac.yaml` with a driver that targets that
      controller. Do **not** keep `ac_dimmer`.

   The "SX1509 channel for gate / SX1509 input for zero-cross" hypothesis
   is rejected — see [Timing constraint](#timing-constraint-ac_dimmer-vs-sx1509-expander).
3. Until either (2a) or (2b) is delivered:
   - The Release-One FanTRIAC binary must not be uploaded to WebFlash
     release assets.
   - Product owners may also choose to drop the FanTRIAC slot from the
     Release-One WebFlash config string entirely. That would change
     `config/webflash-builds.json`, `config/webflash-compatibility.json`,
     the artifact name, and `docs/release-one.md`; it is **out of scope for
     HW-005** and requires an explicit product decision.

### Re-verification

HW-005 was re-checked as a docs-only re-verification pass. The verdict is
**unchanged**: still blocked, missing evidence. No new schematic, pin map,
or driver evidence has landed since the original resolution above was
written.

Files inspected for this re-verification (read-only):

- [`docs/hardware/`](hardware/) — directory listing shows only
  [`s360-100-r4-core.md`](hardware/s360-100-r4-core.md) and
  [`s360-200-r4-roomiq.md`](hardware/s360-200-r4-roomiq.md). **No
  `s360-320-*-triac.md` schematic doc exists.**
- [`config/hardware-catalog.json`](../config/hardware-catalog.json) —
  `S360-320` row still carries `"schematic_status": "cataloged_unverified"`.
- [`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml)
  — still uses `output: ac_dimmer` and still requires direct
  interrupt-capable ESP32 GPIOs; BLOCKED / UNVERIFIED banner intact.
- [`packages/expansions/gpio_expander_sx1509.yaml`](../packages/expansions/gpio_expander_sx1509.yaml)
  — SX1509 channels 0–3 are fan PWM, 4–7 are tach, 8–11 are aux PWM, 12–15
  are inputs. **No channel is allocated to `TRI_GPIO1` / `TRI_GPIO2`.**
- [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml)
  — `fan_triac_gate_pin: GPIO5` and `fan_triac_zc_pin: GPIO6` still in
  place as parse-only placeholders; BLOCKED / UNVERIFIED banner intact;
  `IO5 = SEN0609_TX` and `IO6 = out(gpio6)` on `S360-100-R4` are still
  claimed by RoomIQ at J10.
- [`products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml)
  — still flagged `BLOCKED / REFERENCE`, still not present in
  [`config/webflash-builds.json`](../config/webflash-builds.json).
- [`docs/hardware/s360-100-r4-core.md`](hardware/s360-100-r4-core.md) —
  J15 row still shows `TRI_GPIO1` / `TRI_GPIO2` reachable only via the
  SX1509 (`U3`) side; `IO5` / `IO6` still tagged "Do not reuse blindly for
  FanTRIAC".

Files intentionally left unchanged by this re-verification pass (no
evidence supports any edit):

- All product YAMLs under `products/` — including the Release-One no-TRIAC
  files and the FanTRIAC `blocked-reference` files.
- All package YAMLs under `packages/` — including
  `packages/expansions/fan_triac.yaml` and
  `packages/expansions/gpio_expander_sx1509.yaml`.
- All config JSON under `config/` — `webflash-builds.json`,
  `webflash-compatibility.json`, `hardware-catalog.json`.
- All hardware reference docs under `docs/hardware/`.
- `docs/release-one.md`, `docs/webflash-contract.md`,
  `docs/webflash-ci-alignment.md`, `docs/webflash-release-handoff.md`,
  `docs/hardware-catalog.md`.
- All workflows under `.github/workflows/`, scripts under `scripts/`,
  tests under `tests/`, components under `components/`, headers under
  `include/`.

No new `s360-320-*-triac.md` doc was created. Inventing a schematic doc
without source-of-truth schematic evidence would itself be a HW-005
violation. The absence of that file is the blocker; this PR documents the
absence, it does not paper over it.

Next evidence needed to move HW-005 from "still blocked" to either
"resolved / preview-ready" or "invalid / unsafe": every item in the
[Missing evidence checklist](#missing-evidence-checklist) above. Until
that lands, FanTRIAC stays out of WebFlash and out of any release matrix.

### Cross-references

- Schematic source (Core): [`docs/hardware/s360-100-r4-core.md`](hardware/s360-100-r4-core.md)
- Schematic source (RoomIQ): [`docs/hardware/s360-200-r4-roomiq.md`](hardware/s360-200-r4-roomiq.md)
- TRIAC driver package: [`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml)
- Fan-control profile (downstream user-facing entities): [`packages/features/fan_control_profile.yaml`](../packages/features/fan_control_profile.yaml)
- Release-One product YAML: [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml)
- SX1509 channel map (no TRIAC channels assigned today): [`packages/expansions/gpio_expander_sx1509.yaml`](../packages/expansions/gpio_expander_sx1509.yaml)
- Hardware catalog (S360-320 — `cataloged_unverified`): [`config/hardware-catalog.json`](../config/hardware-catalog.json)

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

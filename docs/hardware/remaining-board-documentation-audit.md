# Remaining Board Documentation Audit (HW-004 / HW-006)

## Purpose

This document classifies the documentation state of **every** board and module
listed in [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
against the schematic-backed evidence currently committed to this repository.

It exists so that downstream work — Release-One preview/stable gates, future
WebFlash config strings, and hardware-audit follow-ups — has a single,
evidence-citable answer to "do we have enough hardware documentation to safely
ship this module?".

This audit is **documentation only**. It does not:

- change any firmware, product YAML, package YAML, workflow, script, test,
  or build matrix,
- change any value in `config/hardware-catalog.json` (the `schematic_status`
  field of every row is left exactly as committed),
- promote or demote any module's Release-One status,
- invent pin maps, infer pin assignments from board names, or pretend a
  module-side schematic exists when it does not.

The Release-One shipping configuration remains
`Ceiling-POE-VentIQ-RoomIQ` with artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`. **Sense360 TRIAC /
FanTRIAC stays blocked under HW-005.** **Sense360 LED stays excluded from
production Release-One** because the WebFlash config string does not carry a
`LED` token. The build matrix, artifact name, signing flow, and WebFlash
contract are not changed by this audit.

## Scope

In scope:

- Each row in [`config/hardware-catalog.json`](../../config/hardware-catalog.json).
- Documentation that is **already in this repository** as of this audit:
  - [`docs/hardware-catalog.md`](../hardware-catalog.md)
  - [`docs/hardware/s360-100-r4-core.md`](s360-100-r4-core.md)
  - [`docs/hardware/s360-200-r4-roomiq.md`](s360-200-r4-roomiq.md)
  - [`docs/release-one-hardware-audit.md`](../release-one-hardware-audit.md)
  - [`docs/release-one.md`](../release-one.md)
  - [`docs/cleanup-audit.md`](../cleanup-audit.md)
  - the relevant `packages/**` files

Out of scope (deliberately):

- Adding new per-board pin/connector docs for modules whose own schematic is
  not committed. The Allowed-changes rule for this audit is "only create new
  per-board docs if evidence is actually present." Where the evidence is not
  there, this doc records what is missing instead of inventing it.
- Any change to YAML, JSON, workflow, script, test, or build behaviour.
- Any change to FanTRIAC or LED status.

## Taxonomy

Every catalog row in the [Decision table](#decision-table) is classified using
the labels below. The Release-One axis (`not-needed-for-release-one`) is
applied **alongside** one of the primary labels where it applies — it is not a
substitute for the primary classification.

| Label | Meaning |
|---|---|
| `documented` | The module has a schematic-backed standalone pin/connector reference doc committed under `docs/hardware/`, and `config/hardware-catalog.json` records the schematic as `verified` with a `schematic_file` value. Pin-level firmware questions can be checked against the doc. |
| `partially-documented` | The Core (`S360-100-R4`) schematic exposes the **connector** side of the module on a J-header and the nets visible at that header are captured in [`docs/hardware/s360-100-r4-core.md`](s360-100-r4-core.md), but the module's **own** schematic is not committed to this repo. The Core-side connector view is real evidence; the module-internal pin map is unverified. |
| `cataloged-unverified` | The module exists as a row in `config/hardware-catalog.json` and `docs/hardware-catalog.md`, but neither a module-side schematic nor a Core-side connector capture is committed to this repo. Friendly name, SKU, revision, and `old_name` are committed naming; everything below the SKU level is unverified. |
| `blocked` | The module is intentionally **not** promoted to preview or stable until a named blocker is resolved. Currently this applies only to Sense360 TRIAC under HW-005 (see [`release-one-hardware-audit.md#fantriac-mapping-resolution`](../release-one-hardware-audit.md#fantriac-mapping-resolution)). |
| `not-needed-for-release-one` | The module is **not** part of the production Release-One config string `Ceiling-POE-VentIQ-RoomIQ`. Schematic / pin evidence for it is therefore not a gate on the current Release-One artifact. Applied alongside one of the primary labels above. |
| `unknown` | Cannot be classified from currently committed evidence. Not used in this audit pass; every catalog row was placeable under one of the labels above. |

This taxonomy intentionally distinguishes between **"the Core schematic shows
the connector for this module"** (→ `partially-documented`) and **"only the
catalog row exists"** (→ `cataloged-unverified`). The two are not the same
level of evidence, and conflating them would weaken downstream decisions about
which modules are ready to enter a config string.

The `schematic_status` field in
[`config/hardware-catalog.json`](../../config/hardware-catalog.json) is a
**separate**, machine-readable axis. As of HW-008 (see
[HW-008 schematic-status refresh](#hw-008-schematic-status-refresh)), the
JSON value is `verified` for the five boards with a committed module-side
schematic PDF (`S360-100`, `S360-200`, `S360-210`, `S360-211`, `S360-300`);
every other row stays `cataloged_unverified` (underscore form). The
hyphenated form used in this taxonomy (`documented` /
`partially-documented` / `cataloged-unverified`) is the audit-classification
name and coexists with the JSON form on purpose — `verified` schematic
evidence does not by itself make a module WebFlash-shippable, production-
ready, or Release-One-eligible.

## Decision table

Every row from [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
is included.

| Board / module | SKU | Current evidence in repo | Status | Needed before preview | Needed before stable |
|---|---|---|---|---|---|
| Sense360 Core | `S360-100` | [`docs/hardware/s360-100-r4-core.md`](s360-100-r4-core.md) (schematic-backed; PDF `S360-100-R4.pdf` cited); `schematic_status: verified` in JSON. | `documented` | None — already documented. | Resolve open-questions list at [`s360-100-r4-core.md#open-questions--verification-needed`](s360-100-r4-core.md#open-questions--verification-needed). |
| Sense360 RoomIQ | `S360-200` | [`docs/hardware/s360-200-r4-roomiq.md`](s360-200-r4-roomiq.md) (schematic-backed; PDF `S360-200-R4.pdf` cited); `schematic_status: verified` in JSON. | `documented` | None — already documented. | Resolve open-questions list at [`s360-200-r4-roomiq.md#open-questions--verification-needed`](s360-200-r4-roomiq.md#open-questions--verification-needed); reconcile the Core J10 vs RoomIQ J6 pin-order discrepancy already flagged in both docs. |
| Sense360 AirIQ | `S360-210` | Module-side schematic committed under HW-007 at [`schematics/S360-210-R4.pdf`](schematics/S360-210-R4.pdf); standalone reference doc at [`s360-210-r4-airiq.md`](s360-210-r4-airiq.md) (SGP41, SCD41, SFA40 connector, SPS30 connector, MICS-4514 + STM8 I²C bridge sub-sheet). Core-side `J9` mating captured in [`s360-100-r4-core.md` J9](s360-100-r4-core.md#j9--airiq-module-connector-7-pin) with legacy `AirQ_*` nets. `airiq_*.yaml` packages exist (logical, not pin-bound to a verified schematic). Mutually exclusive with VentIQ; not in Release-One. JSON `schematic_status` is `verified` with `schematic_file: docs/hardware/schematics/S360-210-R4.pdf` under HW-008. | `documented`, `not-needed-for-release-one` | Not required (Release-One ships `VentIQ`, not `AirIQ`). | Any future `AirIQ`-bearing config string is a separate product PR with its own catalog entry, build-matrix entry, and onboarding-gate clearance — HW-008's `verified` schematic evidence is not by itself a shippability claim. Confirm `AirQ_Led` / `AirQ_Status_Led` net reuse at `J9` (HW-002 Open Question #4) before any such promotion. |
| Sense360 VentIQ | `S360-211` | **Used in Release-One.** Module-side schematic committed under HW-007 at [`schematics/S360-211-R4.pdf`](schematics/S360-211-R4.pdf); standalone reference doc at [`s360-211-r4-ventiq.md`](s360-211-r4-ventiq.md) (SGP41 on board, IR-temperature connector, SPS30 connector, on-board fan-relay drive circuitry). Core-side `J9` (AirIQ Module Connector) captured in [`s360-100-r4-core.md` J9](s360-100-r4-core.md#j9--airiq-module-connector-7-pin) with legacy `AirQ_*` nets. Firmware package: [`packages/expansions/airiq_bathroom_base.yaml`](../../packages/expansions/airiq_bathroom_base.yaml) (legacy filename retained per WebFlash contract §6). JSON `schematic_status` is `verified` with `schematic_file: docs/hardware/schematics/S360-211-R4.pdf` under HW-008; the "schematic verification pending" caveat that previously lived in [`release-one-hardware-audit.md` Findings → VentIQ](../release-one-hardware-audit.md#findings) and in [`webflash-compatibility-taxonomy-audit.md`](../webflash-compatibility-taxonomy-audit.md) has been retired by HW-008. | `documented` | None — already documented and JSON-verified under HW-008. | Confirm `AirQ_Led` / `AirQ_Status_Led` reuse at `J9` (HW-002 Open Question #4); confirm fan-relay drive-signal source for any future fan-driver audit; mains-side compliance evidence for the on-board relay remains tracked under COMPLIANCE-001 and is **not** cleared by HW-008. |
| Sense360 LED | `S360-300` | **Excluded from Release-One by policy.** Module-side schematic committed under HW-007 at [`schematics/S360-300-R4.pdf`](schematics/S360-300-R4.pdf); standalone reference doc at [`s360-300-r4-led.md`](s360-300-r4-led.md) (3-pin `J1` carrying `LED_DATA` / `+5V` / `GND`; WS2812B LED chain). Core-side `J3` connector and the `LED_DATA → U2A 74LVC1G07 → R8 → J3` path are captured in [`s360-100-r4-core.md` LED output](s360-100-r4-core.md#led-output). The ceiling LED package [`packages/hardware/led_ring_ceiling.yaml`](../../packages/hardware/led_ring_ceiling.yaml) binds `led_data_pin: GPIO38` after **HW-010**, matching `LED_DATA = IO38` on the schematic (`IO14` is `SCS`, not LED). JSON `schematic_status` is `verified` with `schematic_file: docs/hardware/schematics/S360-300-R4.pdf` under HW-008. | `documented`, `not-needed-for-release-one` | Not required. The Release-One WebFlash config string `Ceiling-POE-VentIQ-RoomIQ` does not carry a `LED` token, and the Release-One YAML omits LED package includes on purpose. HW-008's `verified` schematic evidence and HW-010's package-level pin fix do not change this. | Required only if a future Release-One variant adds a `LED` token (e.g. `Ceiling-POE-VentIQ-RoomIQ-LED`). The package-level `LED_DATA` pin reconciliation is now done (HW-010); a future LED-bearing config still needs its own product YAML, catalog entry, build-matrix entry, and release-notes draft. **HW-010 does not add `LED` to the Release-One config string; Sense360 LED stays excluded from Release-One.** |
| Sense360 Relay | `S360-310` | Core-side `J4` connector documented in [`s360-100-r4-core.md` J4](s360-100-r4-core.md#j4--relay-module-connector-3-pin): 3-pin (`+5V`, `Relay`, `GND`), drive signal `Relay` from ESP32 `IO3`. Module-side schematic not committed. Firmware package: [`packages/expansions/fan_relay.yaml`](../../packages/expansions/fan_relay.yaml). Not in Release-One. | `partially-documented`, `not-needed-for-release-one` | Not required (no `FanRelay` in Release-One). | Commit `S360-310` schematic and a standalone pin/connector doc before any `FanRelay`-bearing config string ships as stable. |
| Sense360 PWM | `S360-311` | Core-side `J6` (12 V PWM fan connector, 13-pin) documented in [`s360-100-r4-core.md` J6](s360-100-r4-core.md#j6--12-v-pwm-fan-connector-13-pin). Net list captured (`+5V`, `GND`, `TachIO`, `TachPMW1..4`, `Pul_Cou1..4`); `TachPMW*` / `Pul_Cou*` are driven by the SX1509 expander per [`s360-100-r4-core.md` fan-driver outputs](s360-100-r4-core.md#fan--driver-outputs). The 1-to-13 pin order is explicitly marked **verify** in the Core doc. Module-side schematic not committed. Firmware package: [`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml). Not in Release-One. | `partially-documented`, `not-needed-for-release-one` | Not required (no `FanPWM` in Release-One). | Commit `S360-311` schematic + standalone pin/connector doc; resolve the J6 pin-order **verify** flag against the silkscreen. |
| Sense360 DAC | `S360-312` | Core-side `J7` (GP8403 fan connector, 6-pin) fully captured in [`s360-100-r4-core.md` J7](s360-100-r4-core.md#j7--gp8403-fan-connector-6-pin) — `+5V`, `I2C_SDA`, `I2C_SCL`, `UART_RX`, `UART_TX`, `GND`. Module-side schematic not committed. Firmware package: [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml). Not in Release-One. | `partially-documented`, `not-needed-for-release-one` | Not required (no `FanDAC` in Release-One). | Commit `S360-312` schematic + standalone pin/connector doc. |
| Sense360 TRIAC | `S360-320` | **HW-005 blocked — must not ship as TRIAC-capable.** Core-side `J15` (TRIAC fan module connector, 4-pin) documented in [`s360-100-r4-core.md` J15](s360-100-r4-core.md#j15--triac-fan-module-connector-4-pin): `+3.3V`, `TRI_GPIO1`, `TRI_GPIO2`, `GND`. Source pins for `TRI_GPIO1` / `TRI_GPIO2` are **not visible** as direct ESP32 GPIOs on the Core sheet; they appear to route via the SX1509 (U3). Module-side schematic **not committed**. The ESPHome `ac_dimmer` driver in [`packages/expansions/fan_triac.yaml`](../../packages/expansions/fan_triac.yaml) requires direct interrupt-capable ESP32 GPIOs that the SX1509 cannot deliver — see [`release-one-hardware-audit.md#timing-constraint-ac_dimmer-vs-sx1509-expander`](../release-one-hardware-audit.md#timing-constraint-ac_dimmer-vs-sx1509-expander). | `blocked` (HW-005), `not-needed-for-release-one` | **Stays blocked.** Do not promote to preview. | Stays blocked until the HW-005 missing-evidence checklist at [`release-one-hardware-audit.md#missing-evidence-checklist`](../release-one-hardware-audit.md#missing-evidence-checklist) is fully satisfied — either (a) direct, interrupt-capable ESP32 GPIOs for both `gate_pin` and `zero_cross_pin`, traced end-to-end through `S360-100-R4` + `S360-320`; or (b) a replacement non-`ac_dimmer` driver that targets an on-board TRIAC controller IC over I²C. The SX1509-only hypothesis is rejected. **Mains-voltage compliance is additionally tracked in [`../compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md) (COMPLIANCE-001); HW-005 remains a separate, prior blocker.** |
| Sense360 240v PSU | `S360-400` | Catalog row only. No Core-side connector documented (the 240 V PSU is off-board; Release-One uses PoE instead). No module-side schematic committed. Firmware-side, [`packages/hardware/power_240v.yaml`](../../packages/hardware/power_240v.yaml) is a logical-power package and does not bind to any specific GPIO. Not in Release-One. | `cataloged-unverified`, `not-needed-for-release-one` | Not required (Release-One uses `POE`, not `PWR`). | Commit `S360-400` schematic + standalone pin/connector doc before any `PWR`-bearing config string ships as stable. **Also subject to the mains-voltage safety/compliance review noted below; tracked in [`../compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md) (COMPLIANCE-001).** |
| Sense360 PoE PSU | `S360-410` | **Used in Release-One.** Core-side `J2` (`PoE_ACDC`, 2-pin power inlet) documented in [`s360-100-r4-core.md` J2](s360-100-r4-core.md#j2--poe_acdc-inlet-2-pin) and in the Core power-rails section. PSU module itself lives off-board; module-side schematic **not committed**. Firmware-side, [`packages/hardware/power_poe.yaml`](../../packages/hardware/power_poe.yaml) is a logical package that emits diagnostic sensors only and does not bind to any specific GPIO. [`release-one-hardware-audit.md` Findings → PoE PSU](../release-one-hardware-audit.md#findings) already classifies this as "cataloged, schematic pending". HW-002 Open Question #6 (J2 harness identity) is still open. | `partially-documented` | Acceptable as-is for preview. The Core-side inlet capture plus the logical-only firmware package are sufficient evidence for the current Release-One use; the schematic-pending caveat in `release-one-hardware-audit.md` must remain visible. | Commit `S360-410` schematic + a standalone pin/connector doc; verify the J2 cable/harness between the off-board PSU and the Core inlet (HW-002 Open Question #6). |

### Release-One coverage summary

The four modules that compose the production Release-One config string
`Ceiling-POE-VentIQ-RoomIQ` are:

| Slot | Module | SKU | Audit status |
|---|---|---|---|
| Mount / Core | Sense360 Core | `S360-100` | `documented` |
| Power | Sense360 PoE PSU | `S360-410` | `partially-documented` (connector-side captured on Core; module-side schematic pending) |
| Air Quality | Sense360 VentIQ | `S360-211` | `documented` (module-side schematic committed under HW-007; JSON `verified` under HW-008) |
| Room Sense | Sense360 RoomIQ | `S360-200` | `documented` |

Three of the four Release-One modules are `documented`. `PoE PSU`
remains `partially-documented` — its connector-side capture is on the
Core sheet but the module-side `S360-410` schematic is still not
committed; this audit does **not** upgrade it to `documented` and does
**not** invent a per-board pin/connector doc for it.

## Evidence available / Evidence missing

### Sense360 Core (`S360-100`)

- **Evidence available.** Full schematic-backed reference at
  [`docs/hardware/s360-100-r4-core.md`](s360-100-r4-core.md): ESP32-S3 pin
  map, every J-header, the I²C bus, the UART layout, the LED net path, and
  every fan-related net are documented from the `S360-100-R4` PDF. The PDF
  filename is recorded in `config/hardware-catalog.json` as
  `schematic_file: S360-100-R4.pdf`.
- **Evidence missing.** The PDF itself is not committed to this repo (only
  the Markdown reference is). Several rows in the Core doc are explicitly
  marked **verify**: the `IO10` net label, the pin-to-test-point mapping
  among `IO39 / IO40 / IO41 / IO42`, the 1-to-N pin order on `J6` (13 pins)
  and `J10` (12 pins), and the `R5`/`R6` divider value. The open-questions
  list at [`s360-100-r4-core.md#open-questions--verification-needed`](s360-100-r4-core.md#open-questions--verification-needed)
  enumerates all of them.

### Sense360 RoomIQ (`S360-200`)

- **Evidence available.** Full schematic-backed reference at
  [`docs/hardware/s360-200-r4-roomiq.md`](s360-200-r4-roomiq.md): every
  on-board sensor (`U1` LTR-303ALS, `U2` SHT4x, `U3` EKMC1601111 PIR,
  `U4` BMP581), the radar connectors `J2` (LD2450) and `J3`
  (SEN0609 / C4001), the 12-pin module connector `J6`, the I²C bus, the
  `JP1` address strap, and the power rails are documented from the
  `S360-200-R4` PDF (`schematic_file: S360-200-R4.pdf`).
- **Evidence missing.** The PDF itself is not committed. The Core J10 vs
  RoomIQ J6 pin-order discrepancy (already captured in both hardware docs
  and in [`release-one-hardware-audit.md`](../release-one-hardware-audit.md#detail-core--roomiq-pin-order-discrepancy))
  remains unresolved against the physical silkscreen. Several minor
  **verify** items remain (BMP581 `INT` routing, `out(gpio6)` purpose at
  the SEN0609 connector, `RX`/`TX` directionality, `JP1` production strap,
  `J2` / `J3` exact pin order, `R1` / `R2` / `R4` exact roles).

### Sense360 AirIQ (`S360-210`)

- **Evidence available.** Catalog row in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json) and
  [`docs/hardware-catalog.md`](../hardware-catalog.md). The Core sheet has
  a connector named `J9` ("AirIQ Module Connector") that AirIQ would plug
  into; the J9 nets are captured in [`s360-100-r4-core.md` J9](s360-100-r4-core.md#j9--airiq-module-connector-7-pin)
  but are labelled with the legacy `AirQ_*` prefix and are shared between
  AirIQ and VentIQ. Firmware packages exist (`airiq_ceiling.yaml`,
  `airiq_wall.yaml`, etc.). **Under HW-007**, the module-side schematic
  PDF is now committed at [`schematics/S360-210-R4.pdf`](schematics/S360-210-R4.pdf)
  and a standalone reference doc is available at
  [`s360-210-r4-airiq.md`](s360-210-r4-airiq.md) (visible on the sheet:
  SGP41, SCD41, SFA40 connector, SPS30 connector, MICS-4514 + STM8
  I²C-bridge sub-sheet).
- **Evidence missing.** Whether the legacy `AirQ_Led` /
  `AirQ_Status_Led` nets at the J9 connector are reused by AirIQ vs
  VentIQ is still unverified (HW-002 Open Question #4). 1-to-7 pin order
  on the AirIQ side of J9 is **verify** against silkscreen. STM8
  firmware identity and I²C register map are not in the schematic. The
  SFA40 and SPS30 connector interfaces (UART vs I²C) are **verify**.
  JSON `schematic_status` for `S360-210` is `verified` under HW-008 with
  `schematic_file: docs/hardware/schematics/S360-210-R4.pdf`.

### Sense360 VentIQ (`S360-211`)

- **Evidence available.** Catalog row. The same Core `J9` connector
  capture used for AirIQ also applies physically to VentIQ. VentIQ is
  consumed by the Release-One product YAML
  [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq.yaml)
  via the firmware package
  [`packages/expansions/airiq_bathroom_base.yaml`](../../packages/expansions/airiq_bathroom_base.yaml)
  (the package filename retains the legacy `airiq_bathroom_base` form on
  purpose per the WebFlash contract). The Release-One hardware audit
  flags VentIQ as "schematic verification pending":
  [`release-one-hardware-audit.md` Findings → VentIQ](../release-one-hardware-audit.md#findings)
  and [`release-one-hardware-audit.md#detail-ventiq-schematic-status`](../release-one-hardware-audit.md#detail-ventiq-schematic-status).
  **Under HW-007**, the module-side schematic PDF is now committed at
  [`schematics/S360-211-R4.pdf`](schematics/S360-211-R4.pdf) and a
  standalone reference doc is available at
  [`s360-211-r4-ventiq.md`](s360-211-r4-ventiq.md) (visible on the
  sheet: SGP41 on board, IR-temperature connector, SPS30 connector,
  on-board fan-relay drive circuitry, J9 mating).
- **Evidence missing.** The Core J9 / `AirQ_Led` / `AirQ_Status_Led`
  reuse question (HW-002 Open Question #4) is still unresolved. 1-to-7
  pin order on the VentIQ side of J9 is **verify** against silkscreen.
  The fan-relay drive-signal source on the Core / J9 side is **verify**;
  mains-side topology, contact rating, and creepage / clearance for the
  on-board relay are tracked separately under COMPLIANCE-001 and are
  not cleared by HW-008. JSON `schematic_status` for `S360-211` is
  `verified` under HW-008 with `schematic_file:
  docs/hardware/schematics/S360-211-R4.pdf`; the "schematic verification
  pending" caveat that previously lived in
  `release-one-hardware-audit.md` and
  `webflash-compatibility-taxonomy-audit.md` has been retired by HW-008.

### Sense360 LED (`S360-300`)

- **Evidence available.** The Core `J3` connector (3-pin WS2812B output)
  and the full LED-data path through the `U2A` 74LVC1G07 buffer and the
  330 Ω `R8` series resistor are documented at
  [`s360-100-r4-core.md` LED output](s360-100-r4-core.md#led-output).
  Firmware-side, [`packages/hardware/led_ring_ceiling.yaml`](../../packages/hardware/led_ring_ceiling.yaml)
  drives WS2812B on `GPIO38` (HW-010), matching the schematic
  (`LED_DATA = IO38`; `IO14 = SCS`). **Under HW-007**, the module-side
  schematic PDF is committed at
  [`schematics/S360-300-R4.pdf`](schematics/S360-300-R4.pdf) and a
  standalone reference doc is available at
  [`s360-300-r4-led.md`](s360-300-r4-led.md) (visible on the sheet:
  3-pin `J1` carrying `LED_DATA` / `+5V` / `GND`; WS2812B LED chain).
- **Evidence missing.** The package-level `GPIO14` (package) vs `IO38`
  (Core schematic) reconciliation for `LED_DATA` is **resolved by
  HW-010** — the ceiling LED package now binds `led_data_pin: GPIO38`.
  HW-010 is a one-package edit; it does **not** add `LED` to the
  Release-One config string, does **not** add a WebFlash LED build,
  does **not** add a product-catalog LED entry, and does **not** change
  the FanTRIAC HW-005 blocker. Sense360 LED remains intentionally
  excluded from Release-One; the Release-One YAML continues to omit
  LED package includes. Other Open Questions raised by the LED board
  itself (rail identity on `J1` pin 2, LED count on the chain, harness
  identity between Core `J3` and LED `J1`) are recorded in
  [`s360-300-r4-led.md`](s360-300-r4-led.md). The wall LED package
  ([`packages/hardware/led_ring_wall.yaml`](../../packages/hardware/led_ring_wall.yaml),
  `GPIO48`) and the legacy S3 Core package
  ([`packages/hardware/sense360_core_ceiling_s3.yaml`](../../packages/hardware/sense360_core_ceiling_s3.yaml),
  `GPIO14`) were intentionally not changed by HW-010 — neither has a
  Core-side schematic that proves the same `LED_DATA` path; both
  remain documented as unresolved. JSON `schematic_status` for
  `S360-300` is `verified` under HW-008 with
  `schematic_file: docs/hardware/schematics/S360-300-R4.pdf`.

### Sense360 Relay (`S360-310`)

- **Evidence available.** Core `J4` connector (3-pin, `+5V` / `Relay` /
  `GND`) documented at [`s360-100-r4-core.md` J4](s360-100-r4-core.md#j4--relay-module-connector-3-pin).
  Drive signal `Relay` originates at ESP32 `IO3`. Firmware-side,
  [`packages/expansions/fan_relay.yaml`](../../packages/expansions/fan_relay.yaml)
  is the on/off relay driver package.
- **Evidence missing.** No `S360-310` schematic is committed. The
  module-side relay circuitry (relay coil drive, snubber, contact rating,
  on-board indicator) is not in this repo.

### Sense360 PWM (`S360-311`)

- **Evidence available.** Core `J6` (12 V PWM fan connector, 13-pin)
  documented at [`s360-100-r4-core.md` J6](s360-100-r4-core.md#j6--12-v-pwm-fan-connector-13-pin):
  full net list (`+5V`, `GND`, `TachIO`, `TachPMW1..4`, `Pul_Cou1..4`).
  The `TachPMW*` / `Pul_Cou*` lines are driven by the SX1509 expander
  per [`s360-100-r4-core.md` fan-driver outputs](s360-100-r4-core.md#fan--driver-outputs);
  `TachIO` is the ESP32 `IO16` passthrough. The SX1509 channel map is in
  [`packages/expansions/gpio_expander_sx1509.yaml`](../../packages/expansions/gpio_expander_sx1509.yaml).
  Firmware-side, [`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml)
  is the PWM-fan driver.
- **Evidence missing.** No `S360-311` schematic is committed. The
  1-to-13 pin order on J6 is explicitly **verify** on the Core sheet. The
  module-side circuitry (fan power switch, tach pull-up, level shifting)
  is not in this repo.

### Sense360 DAC (`S360-312`)

- **Evidence available.** Core `J7` (GP8403 fan connector, 6-pin) fully
  captured at [`s360-100-r4-core.md` J7](s360-100-r4-core.md#j7--gp8403-fan-connector-6-pin):
  `+5V`, `I2C_SDA`, `I2C_SCL`, `UART_RX`, `UART_TX`, `GND`. UART0 at
  ESP32 `TXD0` / `RXD0` and the shared I²C bus reach this connector.
  Firmware-side, [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)
  is the 0–10 V analog-fan driver.
- **Evidence missing.** No `S360-312` schematic is committed. The
  module-side GP8403 circuit (DAC, 0–10 V output stage, isolation if any)
  is not in this repo.

### Sense360 TRIAC (`S360-320`)

- **Evidence available.** Core `J15` (TRIAC fan module connector, 4-pin)
  documented at [`s360-100-r4-core.md` J15](s360-100-r4-core.md#j15--triac-fan-module-connector-4-pin):
  `+3.3V`, `TRI_GPIO1`, `TRI_GPIO2`, `GND`. The full HW-005 blocker
  analysis (mapping, timing constraint, missing-evidence checklist,
  re-verification) is in
  [`release-one-hardware-audit.md#fantriac-mapping-resolution`](../release-one-hardware-audit.md#fantriac-mapping-resolution).
  Firmware-side, [`packages/expansions/fan_triac.yaml`](../../packages/expansions/fan_triac.yaml)
  carries an explicit BLOCKED / UNVERIFIED banner.
- **Evidence missing.** No `S360-320` schematic is committed. The source
  ESP32 pins (or rejection of the direct-ESP32 path in favour of an
  on-board controller IC) for `TRI_GPIO1` / `TRI_GPIO2` are unverified.
  The SX1509 channel map does not assign any channel to TRIAC and, per
  the timing analysis in the audit, **cannot** be the answer for an
  `ac_dimmer`-based driver. **This module stays blocked under HW-005;
  this audit does not change that status. Mains-voltage compliance is
  additionally tracked in
  [`../compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md)
  (COMPLIANCE-001); HW-005 remains a separate, prior blocker.**

### Sense360 240v PSU (`S360-400`)

- **Evidence available.** Catalog row only. No Core-side connector is
  documented for the 240 V PSU because Release-One ships with PoE; the
  mains-PSU variant is not currently part of any production config.
  Firmware-side, [`packages/hardware/power_240v.yaml`](../../packages/hardware/power_240v.yaml)
  is a logical-power package that does not bind to a specific GPIO.
- **Evidence missing.** No `S360-400` schematic is committed. The
  HLK-5M05-based mains-to-5 V topology, isolation barriers, mains
  filtering, fusing, and creepage/clearance are not in this repo.
  **Also subject to the mains-voltage safety/compliance review noted
  below; tracked in
  [`../compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md)
  (COMPLIANCE-001).**

### Sense360 PoE PSU (`S360-410`)

- **Evidence available.** Core `J2` (`PoE_ACDC`, 2-pin power inlet)
  documented at [`s360-100-r4-core.md` J2](s360-100-r4-core.md#j2--poe_acdc-inlet-2-pin)
  and in [`s360-100-r4-core.md` power inputs and rails](s360-100-r4-core.md#power-inputs-and-rails).
  Firmware-side, [`packages/hardware/power_poe.yaml`](../../packages/hardware/power_poe.yaml)
  is a logical-power package that emits diagnostic sensors only and does
  not bind to any specific GPIO. The Release-One hardware audit already
  flags this module as "cataloged, schematic pending":
  [`release-one-hardware-audit.md` Findings → PoE PSU](../release-one-hardware-audit.md#findings).
- **Evidence missing.** No `S360-410` schematic is committed. The PoE
  magnetics, the RJ45, the 802.3af PD controller, and the harness
  between the off-board PSU module and the Core's `J2` inlet are not in
  this repo. HW-002 Open Question #6 captures the harness-identity gap.

## Release-One callouts

- **Release-One stays `Ceiling-POE-VentIQ-RoomIQ`.** Artifact name stays
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`. The build matrix
  in [`config/webflash-builds.json`](../../config/webflash-builds.json),
  the compatibility list in
  [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json),
  and the product catalog in
  [`config/product-catalog.json`](../../config/product-catalog.json) are
  not changed by this audit.
- **FanTRIAC stays blocked under HW-005.** The verdict, the missing
  evidence checklist, and the re-verification record are owned by
  [`release-one-hardware-audit.md#fantriac-mapping-resolution`](../release-one-hardware-audit.md#fantriac-mapping-resolution).
  This audit does not promote FanTRIAC to preview or stable. The
  blocked-reference files
  ([`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml),
  [`products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`](../../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml),
  [`packages/expansions/fan_triac.yaml`](../../packages/expansions/fan_triac.yaml))
  remain retained-and-not-shippable.
- **Sense360 LED stays excluded from production Release-One.** The
  WebFlash config string `Ceiling-POE-VentIQ-RoomIQ` does not carry a
  `LED` token. The Release-One YAML omits LED package includes on purpose
  per Option A in the Release-One hardware audit
  ([`release-one-hardware-audit.md` Findings → Sense360 LED](../release-one-hardware-audit.md#findings),
  [`release-one-hardware-audit.md#detail-sense360-led-policy`](../release-one-hardware-audit.md#detail-sense360-led-policy)).
  This audit does not add an `LED` token to the Release-One config string
  and does not bundle LED packages into the Release-One product YAML.
- **No build matrix, artifact, or firmware changes.** This audit is
  documentation only.

## Mains-voltage safety and compliance note

Two modules in the catalog operate on **mains AC voltage**:

- **`S360-400` Sense360 240v PSU** — HLK-5M05 mains-to-5 V converter.
- **`S360-320` Sense360 TRIAC** — phase-cut dimmer for mains-driven fans
  or lamps (additionally HW-005-blocked as above).

Before either module is promoted to preview or stable in any future
config string, an **electrical safety and compliance review** is required.
That review is **out of scope** for this audit. It must include, at
minimum: isolation barriers between mains and low-voltage logic;
creepage/clearance distances; fusing and over-current protection; PCB
finger and connector ratings; CE/UKCA/FCC/UL applicability for the
intended deployment region; appropriate enclosure and ingress protection;
and any standards specific to TRIAC phase-cut dimming of fans and lamps.
**Documentation alone is not sufficient to ship mains hardware.** This
audit makes no claim about the electrical safety of either module; it only
records the documentation gap.

See [`../compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md)
(COMPLIANCE-001) for the structured compliance-assessment tracker that
expands this note into a per-board evidence checklist for UK / EU mains
voltage. That tracker is also documentation only and makes no compliance
claim.

## HW-007 schematic ingest

HW-007 is a separate, later PR that lands **new module-side schematic
evidence** for three boards plus the two existing Core / RoomIQ boards.
This subsection records the ingest in one place so the audit stays
discoverable.

### What HW-007 commits

- Five schematic PDFs under [`schematics/`](schematics/):
  - [`schematics/S360-100-R4.pdf`](schematics/S360-100-R4.pdf) — Sense360 Core
  - [`schematics/S360-200-R4.pdf`](schematics/S360-200-R4.pdf) — Sense360 RoomIQ
  - [`schematics/S360-210-R4.pdf`](schematics/S360-210-R4.pdf) — Sense360 AirIQ
  - [`schematics/S360-211-R4.pdf`](schematics/S360-211-R4.pdf) — Sense360 VentIQ
  - [`schematics/S360-300-R4.pdf`](schematics/S360-300-R4.pdf) — Sense360 LED
- Three new standalone reference docs:
  - [`s360-210-r4-airiq.md`](s360-210-r4-airiq.md) — AirIQ
  - [`s360-211-r4-ventiq.md`](s360-211-r4-ventiq.md) — VentIQ
  - [`s360-300-r4-led.md`](s360-300-r4-led.md) — Sense360 LED
- Cross-link refreshes in this audit's [Decision table](#decision-table)
  and [Evidence available / Evidence missing](#evidence-available--evidence-missing)
  rows for AirIQ / VentIQ / LED so they point at the new PDFs and docs.
- Cross-link refreshes in
  [`docs/hardware-catalog.md`](../hardware-catalog.md) (expand the
  "Verified schematics currently available" list),
  [`docs/release-one-hardware-audit.md`](../release-one-hardware-audit.md)
  (VentIQ and LED rows in the Source-hardware-references table), and
  [`docs/webflash-compatibility-taxonomy-audit.md`](../webflash-compatibility-taxonomy-audit.md)
  (HW-007 note block + per-token footnotes for AirIQ / VentIQ / LED).
- A `cleanup-audit.md` findings row per new doc / new schematic
  directory.

### What HW-007 does **not** do

- Does **not** change
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json).
  Every row's `schematic_status` and `schematic_file` value remains
  exactly as committed before HW-007. Status promotion (e.g. AirIQ /
  VentIQ / LED → `verified`, with `schematic_file` populated) is
  deferred to **HW-008**.
- Does **not** drop the "schematic verification pending" caveat for
  VentIQ in `release-one-hardware-audit.md` or
  `webflash-compatibility-taxonomy-audit.md`. That caveat is tied to the
  JSON status field and is HW-008's responsibility.
- Does **not** change the Release-One config string
  `Ceiling-POE-VentIQ-RoomIQ`, the Release-One artifact name, the
  WebFlash build matrix, the WebFlash compatibility snapshot, the
  product catalog, or any product / package YAML.
- Does **not** unblock FanTRIAC. The HW-005 missing-evidence checklist
  in [`../release-one-hardware-audit.md#missing-evidence-checklist`](../release-one-hardware-audit.md#missing-evidence-checklist)
  is untouched. The `S360-320` schematic is **not** in this batch.
- Does **not** add `LED` to the Release-One config string. The new
  Sense360 LED reference doc explicitly records "schematic evidence
  exists; LED is not in Release-One".
- Does **not** promote AirIQ to WebFlash-shippable. AirIQ stays mutually
  exclusive with VentIQ; the AirIQ reference doc explicitly records
  "this improves legacy / manual hardware documentation only".
- Does **not** resolve the Core J10 vs RoomIQ J6 pin-order discrepancy.
- Does **not** resolve the `GPIO14` (package) vs `IO38` (Core
  schematic) `LED_DATA` discrepancy. (That package-level reconciliation
  was later landed by **HW-010** — the ceiling LED package now binds
  `led_data_pin: GPIO38`. HW-010 did not add `LED` to the Release-One
  config string and did not promote Sense360 LED to WebFlash-shippable.)
- Does **not** make any mains-voltage safety or compliance claim. The
  VentIQ on-board fan-relay drive circuitry is noted as **present** in
  [`s360-211-r4-ventiq.md`](s360-211-r4-ventiq.md); mains compliance
  remains tracked under COMPLIANCE-001.

### What remains unproven after HW-007

The following items remain open after HW-007 lands and are inputs to
later PRs:

- FanTRIAC (`S360-320`) — schematic still uncommitted; HW-005 still
  blocked.
- Sense360 Relay (`S360-310`), PWM (`S360-311`), DAC (`S360-312`),
  240v PSU (`S360-400`), PoE PSU (`S360-410`) — module-side schematics
  still uncommitted.
- Core J10 vs RoomIQ J6 pin-order — still requires silkscreen
  verification.
- LED_DATA `GPIO14` (package) vs `IO38` (Core schematic) — **resolved
  by HW-010** at the package level for the ceiling LED package only
  (`led_ring_ceiling.yaml` now binds `GPIO38`). The wall LED package
  and the legacy S3 Core package remain unresolved (no Core-side
  schematic proving the same `LED_DATA` path).
- `AirQ_Led` / `AirQ_Status_Led` net reuse on AirIQ vs VentIQ (HW-002
  Open Question #4) — still unverified.
- Mains-voltage safety / compliance for any mains-switching surface
  on the VentIQ fan-relay path — tracked separately under
  COMPLIANCE-001.
- Machine-readable `config/hardware-catalog.json` `schematic_status`
  refresh — owned by HW-008 (see
  [HW-008 schematic-status refresh](#hw-008-schematic-status-refresh)).

## HW-008 schematic-status refresh

HW-008 is the follow-up PR that aligns the machine-readable
[`config/hardware-catalog.json`](../../config/hardware-catalog.json)
with the schematic evidence HW-007 committed. It is the JSON-only
counterpart of HW-007's documentation ingest.

### What HW-008 commits

- `schematic_status: verified` and `schematic_file` set to the matching
  `docs/hardware/schematics/*.pdf` path for the five boards with a
  committed module-side schematic PDF:
  - `S360-100` Sense360 Core — `docs/hardware/schematics/S360-100-R4.pdf`
  - `S360-200` Sense360 RoomIQ — `docs/hardware/schematics/S360-200-R4.pdf`
  - `S360-210` Sense360 AirIQ — `docs/hardware/schematics/S360-210-R4.pdf`
  - `S360-211` Sense360 VentIQ — `docs/hardware/schematics/S360-211-R4.pdf`
  - `S360-300` Sense360 LED — `docs/hardware/schematics/S360-300-R4.pdf`
- Re-paths the existing `S360-100` / `S360-200` `schematic_file` values
  from bare filenames to the `docs/hardware/schematics/` repo-relative
  paths so every `schematic_file` resolves directly against the on-disk
  evidence.
- New unit test [`tests/test_hardware_catalog.py`](../../tests/test_hardware_catalog.py)
  that locks in: JSON parses; every entry has `sku` / `friendly_name` /
  `schematic_status`; every status is one of `verified` /
  `cataloged_unverified`; every `verified` entry has a `schematic_file`
  that resolves to a real file under the repo root; the five
  HW-007-evidenced SKUs are `verified`; `S360-320` and `S360-400` are
  still **not** `verified`; entries that are not `verified` may omit
  `schematic_file`.
- Doc cross-link refresh in this audit (decision-table rows for AirIQ,
  VentIQ, LED reclassified from `cataloged-unverified` /
  `partially-documented` to `documented`; Release-One coverage summary
  updated), in
  [`docs/hardware-catalog.md`](../hardware-catalog.md) (verified-schematics
  list refreshed and HW-007 / HW-008 ingest paragraph rewritten), in
  [`docs/release-one-hardware-audit.md`](../release-one-hardware-audit.md)
  (Source-hardware-references table refreshed; VentIQ schematic-pending
  caveat retired), and in
  [`docs/webflash-compatibility-taxonomy-audit.md`](../webflash-compatibility-taxonomy-audit.md)
  (HW-007 note block extended with HW-008; per-token cells for AirIQ /
  VentIQ / LED show JSON `verified`; VentIQ schematic-pending caveat
  retired).

### What HW-008 does **not** do

- Does **not** change the Release-One config string
  `Ceiling-POE-VentIQ-RoomIQ`, the Release-One artifact name, the
  WebFlash build matrix, the WebFlash compatibility snapshot, or any
  product-catalog lifecycle status.
- Does **not** edit any product YAML, WebFlash wrapper, package YAML,
  workflow, component, header, or script. The only test added is the
  new hardware-catalog validator.
- Does **not** unblock FanTRIAC. `S360-320` stays `cataloged_unverified`;
  the HW-005 missing-evidence checklist in
  [`../release-one-hardware-audit.md#missing-evidence-checklist`](../release-one-hardware-audit.md#missing-evidence-checklist)
  is unchanged.
- Does **not** add a `LED` token to the Release-One config string.
  `S360-300`'s JSON status flips to `verified`, but Sense360 LED stays
  excluded from Release-One; the Release-One YAML keeps omitting LED
  package includes on purpose.
- Does **not** clear the mains-voltage compliance gate. `S360-400` and
  `S360-320` remain tracked under
  [`../compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md)
  (COMPLIANCE-001); HW-008 makes no compliance claim.
- Does **not** resolve the Core J10 vs RoomIQ J6 pin-order discrepancy
  or the `GPIO14` (package) vs `IO38` (Core schematic) `LED_DATA`
  discrepancy. Both stay flagged in the per-board docs at HW-008 time.
  (The package-level `LED_DATA` reconciliation was later landed by
  **HW-010** for the ceiling LED package only; HW-010 did not add
  `LED` to the Release-One config string.)
- Does **not** infer pin maps, package YAML rebinds, or new firmware
  behaviour from the now-verified schematics. `verified` schematic
  evidence is not a WebFlash-shippability, production-readiness, or
  Release-One-inclusion claim.

### What remains unproven after HW-008

- FanTRIAC (`S360-320`) — schematic still uncommitted; HW-005 still
  blocked.
- Sense360 Relay (`S360-310`), PWM (`S360-311`), DAC (`S360-312`),
  240v PSU (`S360-400`), PoE PSU (`S360-410`) — module-side schematics
  still uncommitted; JSON `schematic_status` stays `cataloged_unverified`.
- Core J10 vs RoomIQ J6 pin-order — still requires silkscreen
  verification.
- LED_DATA `GPIO14` (package) vs `IO38` (Core schematic) — **resolved
  by HW-010** at the package level for the ceiling LED package only
  (`led_ring_ceiling.yaml` now binds `GPIO38`). HW-010 did not add
  `LED` to the Release-One config string; Sense360 LED stays excluded
  from Release-One. The wall LED package
  (`packages/hardware/led_ring_wall.yaml`) and the legacy S3 Core
  package (`packages/hardware/sense360_core_ceiling_s3.yaml`) remain
  unresolved at the package level.
- `AirQ_Led` / `AirQ_Status_Led` net reuse on AirIQ vs VentIQ (HW-002
  Open Question #4) — still unverified.
- Mains-voltage safety / compliance for any mains-switching surface on
  the VentIQ fan-relay path, on `S360-400`, and on `S360-320` — tracked
  separately under COMPLIANCE-001.

The firmware-package-mapping classification of each item above —
`confirmed-ok` / `needs-package-change` / `needs-doc-fix` /
`needs-silkscreen/bench-verification` / `blocked` / `unknown` — is
recorded in
[`firmware-package-mapping-audit.md`](firmware-package-mapping-audit.md)
(HW-009). HW-009 is documentation only; it does not change any
firmware, product YAML, package YAML, JSON, or test.

## Sanity-grep expectations

After this audit lands, the following greps should hold:

- `grep -RIn "FanTRIAC" docs config products packages` — every FanTRIAC
  reference must still read as `blocked` or HW-005, not as preview-ready
  or stable-ready.
- `grep -RIn "LED" docs config products packages` — no LED reference may
  imply Release-One support. The Release-One config string still does not
  carry a `LED` token.
- `grep -RIn "cataloged-unverified" docs config` — surfaces this audit's
  classification rows (the hyphenated form). The underscore form
  `cataloged_unverified` in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  must now hit only the six rows that remain unverified after HW-008:
  `S360-310`, `S360-311`, `S360-312`, `S360-320`, `S360-400`, `S360-410`.
- `grep -n "schematic_status" config/hardware-catalog.json` — `verified`
  must occur exactly five times, matching `S360-100`, `S360-200`,
  `S360-210`, `S360-211`, `S360-300`.
- `grep -RIn "S360-100-R4.pdf\|S360-200-R4.pdf\|S360-210-R4.pdf\|S360-211-R4.pdf\|S360-300-R4.pdf" docs config`
  — surfaces the schematic-evidence pointers committed under HW-007
  plus the new `docs/hardware/schematics/`-prefixed `schematic_file`
  values committed under HW-008.

## Guardrails (what this audit explicitly does NOT do)

- **No invented pins.** Where a module-side schematic is not committed,
  this audit does not guess pin assignments, does not infer them from the
  board's friendly name, and does not derive them from the firmware
  package YAML.
- **No fake schematics.** This audit does not create per-board reference
  docs for modules whose own schematic is not committed. Only Core
  (`S360-100-R4`) and RoomIQ (`S360-200-R4`) have such docs; this audit
  adds zero new ones.
- **No `schematic_status` JSON changes.** Every row in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  keeps the exact `schematic_status` value it had before this audit.
- **No FanTRIAC promotion.** Sense360 TRIAC stays `blocked` under HW-005.
- **No LED Release-One promotion.** Sense360 LED stays excluded from
  production Release-One.
- **No firmware / product / workflow behaviour changes.** No YAML, no
  JSON, no workflow, no script, no test, no component, no header, no
  example file is touched by this audit beyond the docs-only cross-links
  noted below.

## Files changed by this audit

This audit is intentionally minimal. It adds **one** new doc and applies
**three** small cross-link edits so the audit is discoverable:

- **New** — `docs/hardware/remaining-board-documentation-audit.md`
  (this document).
- **Edited (cross-link only)** —
  [`docs/release-one-hardware-audit.md`](../release-one-hardware-audit.md)
  gains a one-line "See also" pointer to this audit in the
  source-hardware-references intro.
- **Edited (cross-link only)** —
  [`docs/hardware-catalog.md`](../hardware-catalog.md) gains a bullet
  under "Companion file" pointing at this audit.
- **Edited (audit row only)** —
  [`docs/cleanup-audit.md`](../cleanup-audit.md) gains a single row in
  the findings table for this new doc, classified as `current`.

No other file is changed.

## See also

- [Sense360 Hardware Catalog](../hardware-catalog.md) — canonical board /
  module names, SKUs, revisions, and legacy names.
- [`config/hardware-catalog.json`](../../config/hardware-catalog.json) —
  machine-readable mirror of the catalog with `schematic_status` per row.
- [S360-100-R4 Core Hardware Reference](s360-100-r4-core.md) — the only
  schematic-backed Core doc.
- [S360-200-R4 RoomIQ Hardware Reference](s360-200-r4-roomiq.md) — the
  only schematic-backed RoomIQ doc.
- [Firmware Package Mapping Audit (HW-009)](firmware-package-mapping-audit.md)
  — companion docs-only audit that classifies each
  package-vs-schematic gap against the boards this audit covers
  (`confirmed-ok` / `needs-package-change` /
  `needs-silkscreen/bench-verification` / `blocked` / etc.) and
  proposes the scoped follow-up PRs.
- [Release-One Hardware Audit](../release-one-hardware-audit.md) — the
  firmware-vs-schematic audit for the production Release-One YAML, the
  FanTRIAC HW-005 blocker, and the LED policy.
- [Release-One Configuration](../release-one.md) — the
  `Ceiling-POE-VentIQ-RoomIQ` shipping configuration.
- [Cleanup Audit](../cleanup-audit.md) — companion classification of
  stale / current / blocked-reference / legacy-compatible repo content.
- [Mains-voltage Safety and Compliance Assessment — UK / EU (COMPLIANCE-001)](../compliance/mains-voltage-uk-eu-assessment.md)
  — structured compliance-assessment tracker for `S360-400` and
  `S360-320`; documentation only, no compliance claim.
- [Product Availability Taxonomy (PRODUCT-AVAIL-001)](../product-availability-taxonomy.md)
  — cross-cutting availability ladder. Reuses this audit's
  `documented` / `partially-documented` / `cataloged-unverified` /
  `blocked` / `not-needed-for-release-one` vocabulary as the
  pin-map-axis label set, and adds the policy-only `design-pending`
  and `firmware-missing` exception labels for modules that exist
  in docs but are not buildable today.

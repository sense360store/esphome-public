# Firmware Package Mapping Audit (HW-009)

## Purpose

This document reconciles the ESPHome **firmware package YAMLs** under
[`packages/`](../../packages/) against the now-`verified` module-side
schematics committed under [`schematics/`](schematics/) and recorded in
[`config/hardware-catalog.json`](../../config/hardware-catalog.json) as
`schematic_status: verified`.

It exists so that the questions left open by HW-007 (PDF commits and
standalone reference docs) and HW-008 (JSON `schematic_status` refresh)
have a single, evidence-citable answer to: **"now that the schematics are
verified, which firmware package mappings are actually correct, which
mappings need a follow-up PR, and which mappings need physical evidence
the schematic alone cannot supply?"**

This audit is **documentation only**. It does **not**:

- change any product YAML, WebFlash wrapper, or package YAML,
- change any value in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json),
  [`config/product-catalog.json`](../../config/product-catalog.json),
  [`config/webflash-builds.json`](../../config/webflash-builds.json), or
  [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json),
- change any workflow, script, test, component, or include file,
- promote, demote, or rename any board / module / SKU,
- change the Release-One shipping configuration
  `Ceiling-POE-VentIQ-RoomIQ` or its artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`,
- change the FanTRIAC HW-005 blocked status,
- change the Sense360 LED Release-One exclusion status,
- change any package GPIO assignment,
- rename any package file (legacy filenames retained per
  [`docs/webflash-contract.md`](../webflash-contract.md) §6).

The source-of-truth documents this audit threads together are listed in
[Source files inspected](#source-files-inspected). If this audit and any
source-of-truth document drift, the source-of-truth document wins and
this audit must be updated.

## Scope

In scope:

- The five SKUs whose module-side schematic PDFs are now committed and
  whose JSON `schematic_status` is `verified` after HW-008:
  `S360-100` Sense360 Core, `S360-200` Sense360 RoomIQ, `S360-210`
  Sense360 AirIQ, `S360-211` Sense360 VentIQ, `S360-300` Sense360 LED.
- The package YAMLs and product YAMLs that consume those boards in the
  current repo state.
- The Release-One product YAML stack
  [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq.yaml)
  and the blocked / reference FanTRIAC YAML
  [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml).

Out of scope (deliberately):

- Any change to the Release-One config string `Ceiling-POE-VentIQ-RoomIQ`
  or its artifact name.
- Any change to the WebFlash build matrix, the product catalog lifecycle
  statuses, the hardware catalog `schematic_status` values, or the
  WebFlash compatibility taxonomy.
- Any change to FanTRIAC's HW-005 blocked status (additionally blocked by
  COMPLIANCE-001 mains-voltage gate).
- Any change to Sense360 LED's Release-One exclusion.
- Any pin-mapping rebind in `packages/hardware/sense360_core_ceiling.yaml`
  — the systemic Core abstract-bus rework is already enumerated as
  [`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3](../release-one-hardware-audit.md#required-follow-ups)
  and is **not** unblocked by HW-009.
- Inventing any pin assignment that is not directly proven by the
  schematic evidence committed to this repo.

## Source files inspected

The audit reads from the following committed evidence. No invented pin
maps; no fabricated nets.

### Schematic-backed hardware references (verified, HW-007 + HW-008)

- [`docs/hardware/s360-100-r4-core.md`](s360-100-r4-core.md) — Sense360 Core (`S360-100-R4`)
- [`docs/hardware/s360-200-r4-roomiq.md`](s360-200-r4-roomiq.md) — Sense360 RoomIQ (`S360-200-R4`)
- [`docs/hardware/s360-210-r4-airiq.md`](s360-210-r4-airiq.md) — Sense360 AirIQ (`S360-210-R4`)
- [`docs/hardware/s360-211-r4-ventiq.md`](s360-211-r4-ventiq.md) — Sense360 VentIQ (`S360-211-R4`)
- [`docs/hardware/s360-300-r4-led.md`](s360-300-r4-led.md) — Sense360 LED (`S360-300-R4`)
- Committed PDFs under [`docs/hardware/schematics/`](schematics/):
  `S360-100-R4.pdf`, `S360-200-R4.pdf`, `S360-210-R4.pdf`,
  `S360-211-R4.pdf`, `S360-300-R4.pdf`.

### Companion audits

- [`docs/hardware/remaining-board-documentation-audit.md`](remaining-board-documentation-audit.md)
  — HW-004 / HW-006 per-board classification.
- [`docs/release-one-hardware-audit.md`](../release-one-hardware-audit.md)
  — Release-One firmware-vs-schematic audit, FanTRIAC HW-005 resolution,
  and Sense360 LED policy.
- [`docs/webflash-compatibility-taxonomy-audit.md`](../webflash-compatibility-taxonomy-audit.md)
  — COMPAT-001 per-token taxonomy audit.
- [`docs/product-onboarding.md`](../product-onboarding.md) — PRODUCT-004
  ordered safe sequence.

### Product YAML

- [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq.yaml)
  — Release-One (production).
- [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml)
  — blocked / reference FanTRIAC variant.
- [`products/webflash/ceiling-poe-ventiq-roomiq.yaml`](../../products/webflash/ceiling-poe-ventiq-roomiq.yaml)
  — Release-One WebFlash wrapper.

### Package YAML

Hardware:

- [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml)
  — Sense360 Core ceiling abstract-bus board package.
- [`packages/hardware/led_ring_ceiling.yaml`](../../packages/hardware/led_ring_ceiling.yaml)
  — Sense360 LED WS2812B driver.
- [`packages/hardware/power_poe.yaml`](../../packages/hardware/power_poe.yaml)
  — Sense360 PoE PSU diagnostic-only logical package. **Module-side
  schematic now committed under HW-ASSETS-410 / PR #516 at
  [`docs/hardware/schematics/S360-410-R4.pdf`](schematics/S360-410-R4.pdf)**
  and consumed by HW-PINMAP-410-FOLLOWUP at
  [`s360-410-r4-poe.md`](s360-410-r4-poe.md). The package-header
  whole-module PoE-module hint (`Ag9712M / Silvertel Ag9700 / or
  similar`) **disagrees** with the schematic-shown discrete
  topology (`TPS2378DDAR(HSOIC-8)` + `TX4138(ESOIC-8)` +
  `F0505S-2WR2(SIP-7)` with `AM1D-0505S-NZ` annotated alternate +
  `RJP-003TC1(LPJ4112CNL)`). Resolution is BOM-bound and belongs
  to `PACKAGE-POE-410-001`, not HW-009.

Expansions:

- [`packages/expansions/airiq_bathroom_base.yaml`](../../packages/expansions/airiq_bathroom_base.yaml)
  — Sense360 VentIQ I²C sensor stack (filename retained; legacy).
- [`packages/expansions/airiq_ceiling.yaml`](../../packages/expansions/airiq_ceiling.yaml)
  — Sense360 AirIQ I²C sensor stack.
- [`packages/expansions/airiq.yaml`](../../packages/expansions/airiq.yaml)
  — generic AirIQ sensor stack.
- [`packages/expansions/comfort_ceiling.yaml`](../../packages/expansions/comfort_ceiling.yaml)
  — Sense360 RoomIQ comfort sub-block.
- [`packages/expansions/presence_ceiling.yaml`](../../packages/expansions/presence_ceiling.yaml)
  — Sense360 RoomIQ presence sub-block.
- [`packages/expansions/fan_triac.yaml`](../../packages/expansions/fan_triac.yaml)
  — Sense360 TRIAC driver (`ac_dimmer`; HW-005 blocked).
- [`packages/expansions/gpio_expander_sx1509.yaml`](../../packages/expansions/gpio_expander_sx1509.yaml)
  — SX1509 channel map (no TRIAC channel assigned).

### Config JSON

- [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
- [`config/product-catalog.json`](../../config/product-catalog.json)
- [`config/webflash-builds.json`](../../config/webflash-builds.json)
- [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json)

## Reconciliation taxonomy

Each mapping below is classified with exactly one label. The labels are
the same set the task brief requires.

| Label | Meaning |
|---|---|
| `confirmed-ok` | The current package mapping is **not provably wrong** against the verified schematic. Either it does not bind a pin the schematic disagrees with, or the package is logical (no GPIO binding) and the abstraction is consistent with the schematic at the bus / connector level. May still carry a documented caveat (e.g. legacy net naming). |
| `needs-package-change` | The current package mapping is **provably wrong** against the verified schematic. The fix is a package-YAML edit. **HW-009 does not perform that edit** — it documents the gap and proposes a scoped follow-up PR. |
| `needs-doc-fix` | The current package mapping is correct but a Markdown reference doc records a stale or contradictory value. Out of scope for HW-009 unless the contradiction is in one of the four cross-link docs listed at the bottom of this audit. |
| `needs-silkscreen/bench-verification` | The mismatch cannot be resolved from PDFs alone. Two `verified` schematics disagree, or the schematic carries an explicit **verify** flag against the physical silkscreen, or a connector-pair pinout is ambiguous on the PDF. Resolution requires the physical board, not another PR. |
| `blocked` | The slot is **intentionally not shippable** because a named blocker is open. Currently this applies to FanTRIAC under HW-005 (additionally subject to COMPLIANCE-001 mains-voltage compliance). HW-009 makes no shippability claim. |
| `unknown` | Cannot be classified from currently committed evidence. Not used in this audit pass — every area below was placeable under one of the labels above. |

A row may carry one primary label plus an explicit policy note (e.g.
`confirmed-ok` with a legacy-naming caveat; `needs-package-change`
deferred-to-follow-up).

## Decision table

| Mapping / package area | Schematic evidence | Current YAML / package mapping | Status | Recommended action |
|---|---|---|---|---|
| **LED_DATA / Sense360 LED** | Core (`S360-100-R4`) `IO38 = LED_DATA` → `U2A` 74LVC1G07 buffer → `R8` 330 Ω → `J3` → S360-300 `J1` `LED_DATA` input. Core `IO14 = SCS` (peripheral SPI chip-select). Verified in [`s360-100-r4-core.md`](s360-100-r4-core.md) and [`s360-300-r4-led.md`](s360-300-r4-led.md). | [`packages/hardware/led_ring_ceiling.yaml`](../../packages/hardware/led_ring_ceiling.yaml) binds `led_data_pin: GPIO38` (HW-010). Release-One YAML **does not include** this package — the WebFlash config string `Ceiling-POE-VentIQ-RoomIQ` carries no `LED` token. | `confirmed-ok` (resolved by HW-010) | **HW-010 has landed.** Ceiling LED package pin now matches the verified schematic (`GPIO38`). LED remains excluded from Release-One; no `LED` token was added to the config string; no WebFlash LED build was added. The wall LED package ([`led_ring_wall.yaml`](../../packages/hardware/led_ring_wall.yaml)) and the legacy S3 Core package ([`sense360_core_ceiling_s3.yaml`](../../packages/hardware/sense360_core_ceiling_s3.yaml)) stay unchanged — neither has a Core-side schematic proving the same `LED_DATA` path; both remain documented as unresolved. |
| **Core J10 vs RoomIQ J6 pin-order** | Two `verified` schematics disagree on the 12-pin mating connector. Core J10: pin 1 = `+3.3V`, pin 2 = `+5V`, signals at pins 3–11, pin 12 = `GND`. RoomIQ J6: pin 1 = `+5V`, pin 7 = `+3.3V`, signals at pins 2–6 / 8–11, pin 12 = `GND`. Both nominally mate. | No package YAML binds J10 / J6 pins by number. RoomIQ packages ([`comfort_ceiling.yaml`](../../packages/expansions/comfort_ceiling.yaml), [`presence_ceiling.yaml`](../../packages/expansions/presence_ceiling.yaml)) target the abstract `expansion_i2c` bus and `uart_bus` UART — no pin-number drift in firmware today. | `needs-silkscreen/bench-verification` | Document. **Do not edit** either hardware reference doc in HW-009; both already flag the discrepancy as an Open Question. The resolution must come from the physical silkscreen on `S360-100-R4` and `S360-200-R4`. Until then, no firmware change is safe. |
| **VentIQ J9 / `AirQ_Led` / `AirQ_Status_Led`** | Core J9 (S360-100-R4) carries `AirQ_Status_Led` at pin 5 (Core `IO7`) and `AirQ_Led` at pin 6 (Core `IO8`). [`s360-211-r4-ventiq.md`](s360-211-r4-ventiq.md) explicitly marks whether VentIQ reuses these as **verify**. | [`packages/expansions/airiq_bathroom_base.yaml`](../../packages/expansions/airiq_bathroom_base.yaml) declares only I²C sensors (SHT4x at `0x44`, BMP390 at `0x77`, SGP41 at `0x59`) on the abstract `expansion_i2c` bus. **It does not bind `AirQ_Led` / `AirQ_Status_Led` to any GPIO.** [`packages/features/bathroom_profile.yaml`](../../packages/features/bathroom_profile.yaml) is logic-only. | `confirmed-ok` (legacy-naming caveat) | Document. **Do not rename** the legacy `AirQ_*` nets — they are schematic labels, not firmware identifiers. **Do not change** the VentIQ package. Whether the nets actually drive a VentIQ-side indicator on the physical board is HW-002 Open Question #4 and is out of scope for HW-009. |
| **AirIQ J9 / `AirQ_Led` / `AirQ_Status_Led`** | Same Core J9 nets, shared between AirIQ and VentIQ at the connector. [`s360-210-r4-airiq.md`](s360-210-r4-airiq.md) marks AirIQ-side consumption as **verify**. AirIQ ↔ VentIQ mutex preserved in [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json) (`rules.airiq_and_ventiq_mutually_exclusive: true`). | [`packages/expansions/airiq_ceiling.yaml`](../../packages/expansions/airiq_ceiling.yaml), [`packages/expansions/airiq.yaml`](../../packages/expansions/airiq.yaml), and the AirIQ feature-side packages declare I²C sensors only (SPS30 at `0x69`, SGP41 at `0x59`, SCD41 at `0x62`, BMP390 at `0x77`) on the abstract `expansion_i2c` / `airiq_i2c_id` bus. **They do not bind `AirQ_Led` / `AirQ_Status_Led` to any GPIO.** AirIQ is not in Release-One. | `confirmed-ok` (legacy-naming caveat) | Document. **Do not rename** AirIQ packages or nets. **Do not change** the mutex with VentIQ. Indicator-line reuse remains HW-002 Open Question #4. |
| **VentIQ legacy package filename `airiq_bathroom_base.yaml`** | [`docs/webflash-contract.md`](../webflash-contract.md) §6 explicitly retains legacy package filenames; the canonical module name lives in the WebFlash config string, not on disk. [`s360-211-r4-ventiq.md`](s360-211-r4-ventiq.md) confirms the package filename is intentionally kept. | Release-One YAML at line 133 of [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq.yaml) consumes the VentIQ slot via `ventiq_module: !include ../packages/expansions/airiq_bathroom_base.yaml`. | `confirmed-ok` | Document. **Do not rename** the file. The legacy filename is a policy decision, not a schematic mismatch. A rename would break customer remote-package URLs and is forbidden by the WebFlash contract. |
| **Release-One product YAML package stack** | The Core schematic-vs-package mismatches in [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml) (`halo_i2c` on `GPIO39/40`, `expansion_i2c` on `GPIO21/18`, `uart_bus` on `GPIO1/2`, `relay_pin: GPIO4`, `status_led_pin: GPIO48`, `pir_sensor_pin: GPIO47`, `expansion_gpio1/2: GPIO5/6`) are enumerated as a systemic abstraction-vs-schematic mismatch in [`release-one-hardware-audit.md` Summary](../release-one-hardware-audit.md#summary). The Release-One YAML composes Core + PoE + VentIQ + RoomIQ packages; LED packages omitted; FanTRIAC omitted. | The Release-One binary built from this YAML is the recorded production artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`. The systemic Core abstract-bus mismatch is **already documented** as an open follow-up. | `needs-package-change` (systemic; **explicit out-of-scope for HW-009**) | Document the gap by reference. **Do not rebind** any pin in `sense360_core_ceiling.yaml`. The systemic Core rebind is owned by [`release-one-hardware-audit.md` Required follow-ups #2 and #3](../release-one-hardware-audit.md#required-follow-ups). HW-009 inherits that out-of-scope decision unchanged. |
| **FanTRIAC placeholder GPIOs (`GPIO5` / `GPIO6`)** | Core `IO5 = SEN0609_TX` (RoomIQ radar UART → J10 pin 4) and Core `IO6 = out(gpio6)` (RoomIQ aux → J10 pin 5). Both are already claimed by RoomIQ on a Release-One unit. J15 TRIAC nets `TRI_GPIO1` / `TRI_GPIO2` appear only on the SX1509 (U3) side of the Core sheet. `S360-320` Sense360 TRIAC schematic is **not committed**. ESPHome's `ac_dimmer` requires direct interrupt-capable ESP32 GPIOs; SX1509 timing cannot satisfy this. Full analysis: [`release-one-hardware-audit.md#fantriac-mapping-resolution`](../release-one-hardware-audit.md#fantriac-mapping-resolution). | [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml) lines 115–116 keep `fan_triac_gate_pin: GPIO5` and `fan_triac_zc_pin: GPIO6` as parse-only placeholders. [`packages/expansions/fan_triac.yaml`](../../packages/expansions/fan_triac.yaml) carries a BLOCKED / UNVERIFIED banner. [`config/product-catalog.json`](../../config/product-catalog.json) records the FanTRIAC entry as `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`. | `blocked` | Document. **Do not change** the FanTRIAC GPIOs, the blocker status, or any FanTRIAC reference in the catalog / build matrix / artifact. HW-009 does **not** unblock FanTRIAC. The mains-voltage compliance gate ([`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md), COMPLIANCE-001) remains a separate, additional gate. |

## Per-area findings

This section pull-quotes the exact schematic / package evidence for each
row of the decision table. File paths and line numbers are recorded so
later audits and follow-up PRs can verify quickly.

### LED_DATA / Sense360 LED

Schematic evidence (Core):

- `s360-100-r4-core.md` line 107: `| IO14 | SCS | Peripheral SPI chip-select |`.
- `s360-100-r4-core.md` line 114: `| IO38 | LED_DATA | → U2A 74LVC1G07 buffer → LED_DATA_3V3 → R8 → J3 | Source pin for WS2812B data |`.
- `s360-100-r4-core.md` §LED output (lines 305–326): documents the
  `LED_DATA → U2A → R8 → J3 → S360-300 J1` path and explicitly carries
  the reconciliation flag: *"`packages/hardware/led_ring_ceiling.yaml`
  uses `GPIO14`. In the schematic, `IO14` is `SCS` (peripheral SPI
  chip-select), and the actual `LED_DATA` source is `IO38`."*

Schematic evidence (LED board):

- `s360-300-r4-led.md` §J1 — module connector (3-pin) (lines 74–86):
  `LED_DATA` / `+5V` / `GND`. Mates with Core `J3`.
- `s360-300-r4-led.md` lines 111–120: explicitly records that HW-007
  does not resolve the `GPIO14` (package) vs `IO38` (Core schematic)
  discrepancy.

Package evidence (after HW-010):

- `packages/hardware/led_ring_ceiling.yaml` now binds
  `led_data_pin: GPIO38` and cites the `S360-100-R4` / `S360-300-R4`
  schematic evidence in a short comment. The substitution is consumed
  by the `esp32_rmt_led_strip` light platform via `pin: ${led_data_pin}`.

Release-One impact:

- The Release-One YAML
  [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq.yaml)
  still intentionally omits LED package includes (see comments at lines
  121–128). The WebFlash config string `Ceiling-POE-VentIQ-RoomIQ`
  still carries no `LED` token. HW-010 does **not** add `LED` to the
  Release-One config string, the Release-One artifact name, the WebFlash
  build matrix, or the product catalog.

Status: `confirmed-ok` (resolved by HW-010 — this PR). HW-010 is the
scoped one-package edit anticipated by the HW-009 audit: it changes the
ceiling LED `led_data_pin` substitution from `GPIO14` to `GPIO38`,
adds [`tests/test_led_package_mapping.py`](../../tests/test_led_package_mapping.py)
to lock in the new value, the Release-One LED exclusion, and the
FanTRIAC HW-005 blocker, and updates the surrounding documentation. The
non-Release-One products that consume the ceiling LED package
([`sense360-core-ceiling.yaml`](../../products/sense360-core-ceiling.yaml),
[`sense360-core-ceiling-bathroom.yaml`](../../products/sense360-core-ceiling-bathroom.yaml),
[`sense360-core-ceiling-presence.yaml`](../../products/sense360-core-ceiling-presence.yaml))
are `legacy-compatible` in the product catalog and are not part of the
WebFlash build matrix; they now drive the WS2812B ring on the
schematic-correct pin.

### Core J10 vs RoomIQ J6 pin-order

Schematic evidence (Core):

- `s360-100-r4-core.md` §J10 — Presence / Comfort module connector
  (12-pin), lines 191–209:
  pin 1 = `+3.3V`, pin 2 = `+5V`, pin 3 = `SEN0609_RX`, pin 4 =
  `SEN0609_TX`, pin 5 = `out(gpio6)`, pin 6 = `Hi-Link_RX`, pin 7 =
  `Hi-Link_TX`, pin 8 = `PIR`, pin 9 = `ALS_INT`, pin 10 = `I2C_SDA`,
  pin 11 = `I2C_SCL`, pin 12 = `GND`.

Schematic evidence (RoomIQ):

- `s360-200-r4-roomiq.md` §Module connector (lines 90–118):
  pin 1 = `+5V`, pin 2 = `SEN0609_RX`, pin 3 = `SEN0609_TX`, pin 4 =
  `out(gpio6)`, pin 5 = `Hi-Link_RX`, pin 6 = `Hi-Link_TX`, pin 7 =
  `+3.3V`, pin 8 = `PIR`, pin 9 = `ALS_INT`, pin 10 = `I2C_SDA`, pin 11
  = `I2C_SCL`, pin 12 = `GND`.

Both docs are JSON-`verified` after HW-008, but they disagree on the
location of the `+3.3V` rail (pin 1 vs pin 7) and on the placement of
the radar / aux signals (pins 2–6 shifted by one). Both connectors are
nominally a mating pair, so exactly one of the two tables is wrong.

Package evidence:

- No package YAML in this repo binds J10 or J6 by pin number.
  `comfort_ceiling.yaml` uses `comfort_ceiling_i2c_id: expansion_i2c`
  and `comfort_ceiling_als_int_pin: GPIO3` (abstract; consumed via
  substitutions). `presence_ceiling.yaml` uses
  `ld2450_uart_id: uart_bus` (abstract).
- No firmware drift surface exists today: firmware does not care about
  the 1-to-12 pin order, only about the ESP32-side pin map declared in
  `sense360_core_ceiling.yaml`. That Core pin map itself is the subject
  of a separate, larger systemic-rework follow-up (see
  [Release-One product YAML package stack](#release-one-product-yaml-package-stack)
  below).

Status: `needs-silkscreen/bench-verification`. The resolution path is
physical: confirm which doc matches the silkscreen on the manufactured
`S360-100-R4` and `S360-200-R4` boards. Until that lands, do not derive
firmware pin assignments from either pin order. HW-009 does **not**
edit either reference doc. The bench-side / manufacturing-side
companion record for the Core J10 silkscreen observation is
[**S360-100-BENCH-001**](s360-100-r4-core.md#s360-100-bench-001-status),
currently `pending — bench/manufacturing evidence required`.

### VentIQ J9 / `AirQ_Led` / `AirQ_Status_Led`

Schematic evidence (Core):

- `s360-100-r4-core.md` line 92: `| IO7 | AirQ_Status_Led | J9 AirIQ status LED | Net name is legacy; VentIQ may reuse the same line |`.
- `s360-100-r4-core.md` line 93: `| IO8 | AirQ_Led | J9 AirIQ LED | Net name is legacy; VentIQ may reuse the same line |`.
- `s360-100-r4-core.md` §J9 — AirIQ module connector (7-pin), lines
  179–189: pin 5 = `AirQ_Status_Led`, pin 6 = `AirQ_Led`.

Schematic evidence (VentIQ):

- `s360-211-r4-ventiq.md` §Module connector mating, lines 76–96:
  retains the Core J9 view; explicitly marks VentIQ-side reuse of
  `AirQ_Led` / `AirQ_Status_Led` as **verify**.
- `s360-211-r4-ventiq.md` line 148 (Open Question #2): *"`AirQ_Led` /
  `AirQ_Status_Led` reuse on VentIQ. HW-002 Open Question #4 stays
  open."*

Package evidence:

- `packages/expansions/airiq_bathroom_base.yaml` (VentIQ package):
  - line 29: `bathroom_i2c_id: expansion_i2c` (abstract bus).
  - lines 51–74: SHT4x at I²C `0x44`.
  - lines 80–97: BMP390 at I²C `0x77`.
  - lines 104–131: SGP41 at I²C `0x59`.
  - **No `AirQ_Led` / `AirQ_Status_Led` GPIO substitution anywhere in
    the file.** The package never claims those nets.
- `packages/features/bathroom_profile.yaml` is feature-logic only and
  does not bind pins.

Status: `confirmed-ok` (legacy-naming caveat). The package neither
references nor depends on `AirQ_*` directionality. The "VentIQ may
reuse the same line" question is a schematic-side Open Question, not a
firmware drift. **Filename `airiq_bathroom_base.yaml` retained per
WebFlash contract §6 footnote.**

### AirIQ J9 / `AirQ_Led` / `AirQ_Status_Led`

Schematic evidence:

- Same Core J9 view as VentIQ above. AirIQ ↔ VentIQ are mutually
  exclusive at the connector slot
  ([`config/webflash-compatibility.json`](../../config/webflash-compatibility.json)
  `rules.airiq_and_ventiq_mutually_exclusive: true`).
- `s360-210-r4-airiq.md` §Module connector mating (lines 78–98):
  retains the Core J9 view; explicitly marks AirIQ-side consumption of
  `AirQ_Led` / `AirQ_Status_Led` as **verify**.
- `s360-210-r4-airiq.md` lines 137–143 (Open Question #2): *"`AirQ_Led`
  / `AirQ_Status_Led` reuse on AirIQ. HW-002 Open Question #4 is still
  open."*

Package evidence:

- `packages/expansions/airiq_ceiling.yaml`:
  - line 35: `airiq_i2c_id: expansion_i2c` (abstract bus).
  - I²C sensors only: SPS30 at `0x69`, SGP41 at `0x59`, SCD41 at `0x62`,
    BMP390 at `0x77`.
  - **No `AirQ_Led` / `AirQ_Status_Led` substitution.**
- `packages/expansions/airiq.yaml` and other `airiq_*.yaml` packages:
  same pattern — I²C-only sensor declarations on `airiq_i2c_id`. No
  `AirQ_*` net binding.

Status: `confirmed-ok` (legacy-naming caveat). AirIQ is not in
Release-One. The legacy `AirQ_*` nets remain unused by firmware on both
sides of the mutex. Indicator-line reuse remains HW-002 Open Question
#4.

### VentIQ legacy package filename `airiq_bathroom_base.yaml`

Policy evidence:

- [`docs/webflash-contract.md`](../webflash-contract.md) §6 footnote:
  package filenames retain the legacy `airiq_bathroom_*` / `comfort_*` /
  `presence_*` form on purpose. The canonical module name lives in the
  WebFlash config string, not on disk.
- `s360-211-r4-ventiq.md` line 173: *"The package filename retains the
  legacy `airiq_bathroom_base` form **on purpose** per the WebFlash
  contract §6 footnote about legacy package filenames — do not rename
  it."*

Usage evidence:

- `products/sense360-ceiling-poe-ventiq-roomiq.yaml` line 133:
  `ventiq_module: !include ../packages/expansions/airiq_bathroom_base.yaml`.
- `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml` line 153:
  same include (blocked / reference YAML).
- Customer / community remote-package URLs may reference
  `airiq_bathroom_base.yaml` directly; renaming would break those.

Status: `confirmed-ok`. The filename is a deliberate policy decision,
not a schematic mismatch. **Do not rename.**

### Release-One product YAML package stack

Composition evidence:

- `products/sense360-ceiling-poe-ventiq-roomiq.yaml` lines 104–159:
  - `external_components`, `base_wifi`, `base_logging`, `base_api`,
    `base_ota`, `base_time` — base system.
  - `core_hardware: !include ../packages/hardware/sense360_core_ceiling.yaml`
    — Sense360 Core (S360-100).
  - `power_config: !include ../packages/hardware/power_poe.yaml` —
    Sense360 PoE PSU (S360-410); logical, no GPIO binding.
  - LED packages **omitted** by policy (lines 121–128).
  - `ventiq_module: !include ../packages/expansions/airiq_bathroom_base.yaml`
    + `ventiq_profile: !include ../packages/features/bathroom_profile.yaml`
    — Sense360 VentIQ (S360-211).
  - `roomiq_comfort` / `roomiq_comfort_profile` / `roomiq_presence` /
    `roomiq_presence_profile` — Sense360 RoomIQ (S360-200) via the
    legacy `comfort_*` / `presence_*` filenames.
  - FanTRIAC **omitted** by HW-005 (lines 145–156).
  - `health: !include ../packages/features/device_health.yaml`.

Systemic Core-vs-schematic mismatch (already documented; out of scope
for HW-009):

- `packages/hardware/sense360_core_ceiling.yaml` defines an abstract bus
  pin map that does not match the `S360-100-R4` schematic:
  - `halo_i2c_sda_pin: GPIO39`, `halo_i2c_scl_pin: GPIO40` — no separate
    halo I²C bus on the schematic; the only shared I²C bus is on `IO48`
    / `IO45`.
  - `expansion_i2c_sda_pin: GPIO21`, `expansion_i2c_scl_pin: GPIO18` —
    `IO21` is `FAN` (J13), `IO18` is `RST1` on the schematic.
  - `uart_tx_pin: GPIO1`, `uart_rx_pin: GPIO2` — these are
    `Hi-Link_RX/TX` for RoomIQ J10, not a generic expansion UART.
  - `relay_pin: GPIO4` — `IO4` is `SEN0609_RX`; the `Relay` net is on
    `IO3`. The companion `packages/hardware/sense360_core.yaml` binds
    `relay_pin: GPIO10`, which also does not match the Core
    schematic's `IO3` `Relay` source pin. The full `IO3` vs `GPIO4`
    vs `GPIO10` disagreement (and the fact that
    `packages/expansions/fan_relay.yaml` inherits whichever value the
    parent Core package binds via `${relay_pin}`) is recorded in
    [`s360-310-r4-relay.md` Reconciliation findings](s360-310-r4-relay.md#reconciliation-findings)
    (HW-PINMAP-310 audit, **status: `partial — schematic evidence
    available; package reconciliation pending`** after
    HW-PINMAP-310-FOLLOWUP consumed the HW-ASSETS-310 schematic).
    Neither HW-PINMAP-310 nor HW-PINMAP-310-FOLLOWUP resolves it;
    the resolution stays with this systemic Core abstract-bus
    rebind (`CORE-ABSTRACT-BUS-001`). **PACKAGE-RELAY-001 was
    subsequently investigated against this finding and confirmed
    deferred** — it did **not** edit
    `packages/expansions/fan_relay.yaml` because the package is
    already correctly abstracted (`fan_relay_pin: ${relay_pin}`
    inherits whichever value the parent Core abstract package binds)
    and the wrong values live in the Core abstract packages, not in
    `fan_relay.yaml`. The Core abstract `relay_pin` variable
    therefore **remains** the source of conflict, and resolution
    stays owned by `CORE-ABSTRACT-BUS-001`. The PACKAGE-RELAY-001
    investigation outcome is recorded in
    [`s360-310-r4-relay.md` Package YAML status](s360-310-r4-relay.md#package-yaml-status),
    [`package-readiness-matrix.md` `fan_relay.yaml` / S360-310](package-readiness-matrix.md#fan_relayyaml--s360-310),
    and
    [`docs/cleanup-audit.md` §PACKAGE-RELAY-001 update](../cleanup-audit.md#package-relay-001-update-deferred--core-abstract-bus-001--silkscreen--harness--k1-bom-evidence-not-landed).
    **Update (2026-05-21).** `CORE-ABSTRACT-BUS-001A` landed via PR
    #558 and rebound `relay_pin: GPIO4 → GPIO3` (ceiling Core) /
    `GPIO10 → GPIO3` (generic Core) plus the parallel mapping / PoE /
    wall Core packages. The `GPIO3` collision that previously
    blocked the rebind was resolved by `CORE-ABSTRACT-BUS-001C` / PR
    #557 (ALS_INT moved to `GPIO47`, expander interrupt moved to
    `GPIO17`). The schematic-correct `relay_pin: GPIO3` is now bound
    in the five non-voice Core abstract packages and pinned by
    [`tests/test_core_abstract_bus.py`](../../tests/test_core_abstract_bus.py)
    `RelayPinRebindTests` / `MainRelaySwitchBindingTests`. The
    voice-variant Core packages stay at pre-001A `relay_pin: GPIO4`
    (out of scope for 001A). `packages/expansions/fan_relay.yaml`
    is unchanged — `fan_relay_pin: ${relay_pin}` (line 27) now
    resolves to `GPIO3` automatically. The
    `PACKAGE-RELAY-001-READINESS-REFRESH` PR (2026-05-21, docs-only)
    re-evaluated the `PACKAGE-RELAY-001` blocker set against this
    post-001A / 001C state and recorded the readiness table at
    [`s360-310-r4-relay.md` PACKAGE-RELAY-001 readiness refresh after CORE-ABSTRACT-BUS-001C / 001A](s360-310-r4-relay.md#package-relay-001-readiness-refresh-after-core-abstract-bus-001c--001a):
    the substitution-layer blockers are **resolved**, but
    `PACKAGE-RELAY-001` stays blocked on the hardware-evidence
    blockers — S360-100 Core `J4` silkscreen, module-side `J2` / `J1`
    silkscreen, `J1` `NO` / `COM` / `NC` mapping, Core ↔ module
    harness identity, `K1` BOM identity, `K1` contact-current
    rating, Relay load / contact proof, and the general (not
    pair-scoped) ESP32-S3 `GPIO3` strap-pin boot-behaviour bench
    characterisation. The conservative recommended next PR is a
    bench-evidence-capture slice for `S360-310`, **not**
    `PACKAGE-RELAY-001` implementation, **not** a Relay product
    YAML, **not** a WebFlash wrapper, **not** a compile-only target,
    and **not** a release artifact.
    **Update (2026-05-22).** `S360-310-BENCH-EVIDENCE-001` (docs-only)
    populated the ten enumerated `S360-310-BENCH-001` hardware-evidence
    rows from operator-attested + BOM-backed + public-reference-backed
    sources supplied by operator `@wifispray` (Wifi Guy). Relay pin
    substitution is **resolved** by PR #558 (`CORE-ABSTRACT-BUS-001A`);
    `S360-310` evidence is now populated enough for `PACKAGE-RELAY-001`
    implementation **at the package-evidence layer only**.
    `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` /
    `WF-IMPORT-RELAY-001` gates stay separately blocked behind
    `PACKAGE-RELAY-001`; no product, WebFlash, release, compliance,
    mains-safety, board-level installation-approval, or
    hardware-stable readiness claim is made. The captured-evidence
    table lives at
    [`s360-310-r4-relay.md` §S360-310-BENCH-001 — Relay bench evidence](s360-310-r4-relay.md#s360-310-bench-001--relay-bench-evidence),
    and the readiness-matrix refresh lives at
    [`package-readiness-matrix.md` `fan_relay.yaml` / S360-310](package-readiness-matrix.md#fan_relayyaml--s360-310).
    No photo / video / oscilloscope / continuity-meter artifacts are
    attached; the operator-uploaded `S360-310-R4_BOM.xlsx` is consumed
    for the `K1` BOM-backed row only and is **not** committed to this
    repository.
    **Update (PACKAGE-RELAY-001 implementation).** PACKAGE-RELAY-001
    landed as a **test + readiness reconciliation** PR after the
    package-evidence layer closed. No YAML edit was required: the
    package was already correctly abstracted
    (`fan_relay_pin: ${relay_pin}` in
    [`packages/expansions/fan_relay.yaml`](../../packages/expansions/fan_relay.yaml)
    line 27 inherits the parent Core abstract package binding, and
    post-001A `${relay_pin}` resolves to the schematic-correct
    `GPIO3`). The PR added
    [`tests/test_fan_relay_package.py`](../../tests/test_fan_relay_package.py)
    pinning the package abstraction (the package exists and parses
    as YAML; `fan_relay_pin` defaults to `${relay_pin}`; the package
    does not hard-code any GPIO; `fan_relay_switch` binds
    `pin: ${fan_relay_pin}`; the five non-voice Core abstract
    packages bind `relay_pin: GPIO3`; the voice-variant Core
    packages stay at the pre-001A `relay_pin: GPIO4`; no FanRelay
    product YAML or WebFlash-builds entry was added). PACKAGE-RELAY-001
    is recorded as **implemented / reconciled at the package layer
    only**; PRODUCT-RELAY-001 is the next Relay-chain PR but
    remains separate and gated on its own evidence. No WebFlash /
    product / release / compliance / mains-safety / hardware-stable
    readiness claim is made.
  - `status_led_pin: GPIO48` — `IO48` is `I2C_SDA`.
  - `pir_sensor_pin: GPIO47` — `IO47` is `ALS_INT`; `PIR` is on `IO15`.
  - `expansion_gpio1: GPIO5`, `expansion_gpio2: GPIO6` — `IO5` is
    `SEN0609_TX`, `IO6` is `out(gpio6)`; both claimed by RoomIQ.
- This systemic mismatch is enumerated in
  [`release-one-hardware-audit.md` Summary](../release-one-hardware-audit.md#summary)
  and as Required follow-ups #2 / #3.

Status: `needs-package-change` (systemic; **explicit out-of-scope for
HW-009**). HW-009 does **not** rebind any pin. The systemic rework is
gated on a separate, larger follow-up that must also re-validate every
non-Release-One product YAML that consumes
`sense360_core_ceiling.yaml`. The `CORE-ABSTRACT-BUS-001` docs-only
audit / slice plan landed at
[`core-abstract-bus-reconciliation.md`](core-abstract-bus-reconciliation.md)
and split that follow-up into three implementation slices:
**`CORE-ABSTRACT-BUS-001A`** (`relay_pin → GPIO3` across all Core
packages — depends on 001C to free `GPIO3`),
**`CORE-ABSTRACT-BUS-001B`** (consolidate `halo_i2c` /
`expansion_i2c` / `i2c0` / `i2c1` / `i2c_primary` / `i2c_expander`
definitions to the single shared I²C bus on `IO48`/`IO45`), and
**`CORE-ABSTRACT-BUS-001C`** (UART split, status LED move off
`GPIO48`, `pir_sensor_pin: GPIO47 → GPIO15`,
`comfort_ceiling_als_int_pin: GPIO3 → GPIO47` in
[`packages/expansions/comfort_ceiling.yaml`](../../packages/expansions/comfort_ceiling.yaml)
line 42, `expander_int_pin: GPIO3 → GPIO17`,
`sx1509_interrupt_pin: GPIO3 → GPIO17`, `expansion_gpio1..4`
rebind). HW-009 still does not perform any of those slices; they
remain owned by the corresponding `CORE-ABSTRACT-BUS-001*`
implementation PRs.

### FanTRIAC placeholder GPIOs

Schematic evidence:

- `s360-100-r4-core.md` line 90: `| IO5 | SEN0609_TX | J10 RoomIQ —
  SEN0609 radar UART TX | **Do not reuse blindly for FanTRIAC** — see
  Open Questions |`.
- `s360-100-r4-core.md` line 91: `| IO6 | out(gpio6) | J10 RoomIQ —
  auxiliary output | **Do not reuse blindly for FanTRIAC** — see Open
  Questions |`.
- `s360-100-r4-core.md` §J15 — TRIAC fan module connector (4-pin),
  lines 220–226: `TRI_GPIO1` / `TRI_GPIO2` nets. Source pins on the
  Core sheet appear only at the SX1509 (U3) side.
- `s360-100-r4-core.md` Open Question #1 (lines 358–361): TRIAC source
  pins not visible as direct ESP32 GPIOs.
- `S360-320` schematic: **module-side PDF committed under HW-ASSETS-003**
  at [`docs/hardware/schematics/S360-320-R4.pdf`](../hardware/schematics/S360-320-R4.pdf)
  (curated index at
  [`docs/hardware/artifacts/S360-320-R4.md`](../hardware/artifacts/S360-320-R4.md));
  `config/hardware-catalog.json` still records `S360-320` →
  `schematic_status: cataloged_unverified` (HW-ASSETS-003 deliberately
  does **not** flip the JSON status; promotion is owed to a separate
  PR after `HW-PINMAP-320` resolves, and is additionally gated by HW-005
  unblock and COMPLIANCE-001 clearance). The module-side schematic
  shows discrete `MOC3023M` + `BT136` + `EL814` with no on-board
  controller IC; this eliminates Option (b) from the HW-005
  missing-evidence checklist for this revision but does **not** unblock
  HW-005 — Option (a) (direct interrupt-capable ESP32 GPIOs traced
  end-to-end through `S360-100-R4` + `S360-320`) remains required and
  unmet because the Core-side `TRI_GPIO1` / `TRI_GPIO2` nets still
  route via the SX1509. The **HW-PINMAP-320 audit doc** has landed at
  [`docs/hardware/s360-320-r4-triac.md`](../hardware/s360-320-r4-triac.md)
  with **status: `partial — schematic evidence available; package
  reconciliation, timing validation, and compliance/certification
  pending`**; records the module-side `J3` ↔ Core-side `J15`
  reconciliation, the `TRI_GPIO*` vs `ESP_GPIO*` naming divergence,
  the `ac_dimmer` timing constraint, the package YAML status as
  `package-yaml-pending` / `needs-package-reconciliation`, and the
  intended advanced / manual-warning long-term product posture
  (visible / selectable, buildable after package evidence, installable
  only through an advanced / manual-warning path; **not** Release-One,
  **not** REQUIRED_CONFIGS, **not** recommended, **not** kit / default,
  **not** compliance-certified). The audit doc explicitly **does not**
  change this HW-009 row's `blocked` classification, **does not**
  unblock FanTRIAC, and **does not** clear COMPLIANCE-001.

Driver constraint:

- `packages/expansions/fan_triac.yaml` lines 17–34: ESPHome's
  `output: ac_dimmer` requires direct interrupt-capable ESP32 GPIOs for
  both `gate_pin` and `zero_cross_pin`. SX1509-attached GPIOs **cannot**
  satisfy this. Full analysis:
  [`release-one-hardware-audit.md#timing-constraint-ac_dimmer-vs-sx1509-expander`](../release-one-hardware-audit.md#timing-constraint-ac_dimmer-vs-sx1509-expander).

Package evidence:

- `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml` line 115:
  `fan_triac_gate_pin: GPIO5`.
- `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml` line 116:
  `fan_triac_zc_pin: GPIO6`.
- Both values are **provably wrong** on a Release-One unit because
  RoomIQ already claims `IO5` (`SEN0609_TX`) and `IO6` (`out(gpio6)`)
  at J10.

Lifecycle evidence:

- `config/product-catalog.json` for `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`:
  `"status": "blocked"`, `"blocker": "HW-005"`,
  `"webflash_build_matrix": false`.
- `config/webflash-builds.json`: **not** present. The FanTRIAC binary
  is never built or shipped.
- Release-One config string in `config/webflash-compatibility.json`:
  remains `Ceiling-POE-VentIQ-RoomIQ` (no `FanTRIAC` token).
- Mains compliance: additionally gated by
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md)
  (COMPLIANCE-001).

Status: `blocked`. HW-009 does **not** change the GPIOs, the blocker
status, the catalog entry, or any reference to FanTRIAC.

### `power_240v.yaml` AC/DC part-identity disagreement (S360-400)

Schematic evidence:

- `S360-400` schematic: **module-side PDF committed under
  HW-ASSETS-400 (PR #514)** at
  [`docs/hardware/schematics/S360-400-R4.pdf`](schematics/S360-400-R4.pdf)
  (curated index at
  [`docs/hardware/artifacts/S360-400-R4.md`](artifacts/S360-400-R4.md));
  `config/hardware-catalog.json` still records `S360-400` →
  `schematic_status: cataloged_unverified` (HW-ASSETS-400 / HW-PINMAP-400-FOLLOWUP
  deliberately do **not** flip the JSON status; promotion is owed
  to a separate JSON-only PR after BOM cross-check + silkscreen
  evidence land, and is additionally gated by `COMPLIANCE-001`
  clearance). The module-side schematic shows
  `PS1 = HLK-10M05` (4-pin pinout `AC(L)` / `AC(N)` / `-VO` /
  `+VO`); 3-pin AC input `J1` (`LIVE` / `NEUTRAL` /
  `Earth_Protective`); resettable fuse `F1 A250-1200` on the LIVE
  leg; MOV `RV1 10D391K` across the AC line; X-cap `C1 470nF`
  across the AC line; four-cap output filter
  `C5 100uF` / `C6 10u` / `C7 100n` / `C8 100uF` between `+VO`
  and `-VO` / `GND`; 2-pin output `J2` (`+5VP` / `GND`); mounting
  holes `H1`..`H4` with no nets; no Y-caps, no CM/DM line filter,
  no secondary regulator, no on-board indicator LED, no thermal
  cutout, no I²C / UART / SPI / GPIO. The **HW-PINMAP-400 audit
  doc** has landed at
  [`docs/hardware/s360-400-r4-power.md`](s360-400-r4-power.md)
  with **status: `partial — schematic evidence available;
  package reconciliation, BOM, silkscreen, creepage/clearance,
  and COMPLIANCE-001 pending`** (promoted by
  HW-PINMAP-400-FOLLOWUP from the prior
  `pending — schematic/design evidence required`); records the
  three-way AC/DC part-identity disagreement (catalog `HLK-5M05`
  vs package header `HLK-PM01 or similar` vs schematic
  `HLK-10M05`) as **unresolved by this PR**, BOM-bound, and owed
  to `PACKAGE-POWER-400-001`; records the package YAML status as
  `schematic-evidence-pending` + `needs-package-reconciliation` +
  `timing/compliance-pending` (compliance-gated); preserves the
  COMPLIANCE-001 mains-voltage UK / EU sign-off requirement as a
  separate gate before any product-side promotion.

Package file:
[`packages/hardware/power_240v.yaml`](../../packages/hardware/power_240v.yaml)
is a logical-power package emitting diagnostic sensors only
(`Supply Voltage`, `Power Source`, `Power Configuration`,
`AC Power Connected`); no GPIO binding. Header comments at
lines 5–10 carry the disagreed `HLK-PM01 or similar` AC-DC part
hint plus the unverified input / output / isolation / protection
claims; line 15 carries a recommended `1A` AC-input fusing line
that disagrees with the on-board `F1 A250-1200` polyfuse class.
**None of those comments is edited by HW-009 or by
HW-PINMAP-400-FOLLOWUP** — comment-only cleanup is deferred to
`PACKAGE-POWER-400-001` once BOM evidence lands.

Status: `package-yaml-pending` / `needs-package-reconciliation` +
`timing/compliance-pending` (compliance-gated). HW-009 does
**not** change the package, the catalog `description`, the
COMPLIANCE-001 status, the JSON `schematic_status`, or any
reference to PWR-240V.

The 2026-05-19 `PACKAGE-POWER-400-001` investigation pass
(docs-only Path A deferral) re-confirmed this status against the
live files (`packages/hardware/power_240v.yaml` byte-identical to
PR #515; `config/hardware-catalog.json` `S360-400` row
byte-identical to PR #515 — `schematic_status: cataloged_unverified`
with no `schematic_file`; `tests/test_hardware_catalog.py:53`
still asserts `S360-400` in `EXPECTED_STILL_UNVERIFIED_SKUS`;
COMPLIANCE-001 last re-checked PR #506 and remains open). All
five preconditions stay open — BOM cross-check missing; `S360-400`
`schematic_status: verified` JSON PR not landed; COMPLIANCE-001
`S360-400` slice still open; silkscreen / PCB / creepage /
clearance / bench / thermal / EMI evidence missing; three-way
AC/DC part-identity disagreement (catalog `HLK-5M05` vs package
header `HLK-PM01 or similar` vs schematic `PS1 = HLK-10M05`)
stays unresolved and BOM-bound. See
[`s360-400-r4-power.md` §2026-05-19 — PACKAGE-POWER-400-001
investigation pass](s360-400-r4-power.md#2026-05-19--package-power-400-001-investigation-pass-deferred-preconditions-still-open)
and
[`docs/cleanup-audit.md` §PACKAGE-POWER-400-001 update](../cleanup-audit.md#package-power-400-001-update-2026-05-19--docs-only-investigation-pass).
`CORE-ABSTRACT-BUS-001B` merged the same day as PR #519 (docs-only
Path A deferral) but is unrelated to the power package because
`power_240v.yaml` binds no shared Core variables (no GPIO / I²C /
UART / SPI / DAC binding).

**2026-05-20 — `HW-BOM-ASSETS-002` BOM-evidence ingest addendum
(record-only).** The `HW-BOM-ASSETS-002` record-only BOM ingest
landed the `S360-400-R4_BOM.xlsx`
(`95878198-S360400R4_BOM.xlsx`; 10,987 bytes; SHA256
`bb59f56da11fe83f83b2547322af4e594b658384ade9f06267af367ffb603a1d`)
as retained-but-not-committed evidence inventoried at
[`docs/hardware/artifacts/S360-400-R4.md` §HW-BOM-ASSETS-002 BOM ingest (2026-05-20)](artifacts/S360-400-R4.md#hw-bom-assets-002-bom-ingest-2026-05-20).
The BOM `PS1` row records `Value: HLK-5M05` / `MFR#: HLK-5M05` /
`Manufacturer: HI-LINK` / footprint
`greencharge-footprints:CONV_HLK-5M05`, agreeing with the catalog
`description: "Mains to 5V using HLK-5M05."` and **reclassifying**
the three-way disagreement above: catalog `HLK-5M05` + BOM
`HLK-5M05` = **BOM/user-confirmed sourcing truth** for the
populated `PS1`; schematic `PS1 = HLK-10M05` (committed PDF) =
**schematic-label discrepancy** (committed PDF stays byte-identical;
correction owed to a later HW-ASSETS-400 follow-up); package header
`HLK-PM01 or similar`
([`packages/hardware/power_240v.yaml`](../../packages/hardware/power_240v.yaml)
line 7) = **disproved package-header comment text**, comment-only
cleanup deferred to `PACKAGE-POWER-400-001`. The
`packages/hardware/power_240v.yaml` file stays **byte-identical to
PR #515 / PR #520** (stale `HLK-PM01 or similar` line 7, input /
output / isolation / protection / recommended-fusing claims all
preserved; substitutions / globals / template diagnostic sensors /
logger blocks all preserved). The `config/hardware-catalog.json`
`S360-400` row at lines 102–110 stays byte-identical (no
`schematic_status` promotion, no `schematic_file` set, no
`description` edit). Other BOM-confirmed component identities:
`F1 A250-1200` (JDTfuse), `RV1 10D391K` (RUILON), `C1 470nF`
(WALSON `C322S47438P40001`), `C5, C8 100uF` (KNSCHA `189RV0058`),
`C6 10u` (Chinocera), `C7 100n` (CCTC), `J1` WAGO 2601-3103 1×3
terminal block, `J2` JST SH `SM02B-SRSS-TB(LF)(SN)` 1×2.
Per-component voltage / energy / safety-class ratings remain
vendor-datasheet / silkscreen / bench / EMI / EMC evidence and are
**not** resolved by this ingest. COMPLIANCE-001 mains-voltage UK
/ EU sign-off is unchanged. The `BOM cross-check missing`
precondition listed under `PACKAGE-POWER-400-001` /
`PRODUCT-POWER-400-001` / `WEBFLASH-POWER-400-001` /
`RELEASE-POWER-400-001` is now **resolved at the AC/DC
part-identity layer**; each slice stays blocked on its other
recorded preconditions (the `S360-400` `schematic_status:
verified` JSON PR; `COMPLIANCE-001` `S360-400` slice closure;
silkscreen / PCB / creepage / clearance / bench / thermal / EMI
evidence; package / catalog reconciliation; product-onboarding
approval; UX-class decision; release-time sub-gates). The status
above stays `package-yaml-pending` /
`needs-package-reconciliation` + `timing/compliance-pending`. See
[`s360-400-r4-power.md` §2026-05-20 — HW-BOM-ASSETS-002 BOM ingest](s360-400-r4-power.md#2026-05-20--hw-bom-assets-002-bom-ingest-bom-confirmed-part-identity-reclassified-package-header-cleanup-still-deferred)
and [`docs/cleanup-audit.md` §HW-BOM-ASSETS-002 update](../cleanup-audit.md#hw-bom-assets-002-update-2026-05-20--s360-400--s360-410-bom-evidence-ingest).

**2026-05-20 — `PACKAGE-POWER-400-001` package-header cleanup
(Path B / limited implementation).** Following `HW-BOM-ASSETS-002`
/ PR #535 BOM-confirmation of `PS1 = HLK-5M05` (HI-LINK), the
comment-only package-header cleanup that PR #515 + PR #520
deferred has now landed against
[`packages/hardware/power_240v.yaml`](../../packages/hardware/power_240v.yaml).
The header at lines 1–42 has been edited to:

- replace the disproved `HLK-PM01 or similar` AC/DC part hint
  with the BOM-confirmed `PS1 = HLK-5M05 (HI-LINK)` part
  identity (consistent with the catalog
  `description: "Mains to 5V using HLK-5M05."` at
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  line 109);
- group the BOM-confirmed mains-side topology in the header:
  `F1 A250-1200` polyfuse, `RV1 10D391K` MOV, `C1 470nF` X-cap,
  `J1` WAGO 2601-3103 1×3 terminal block (LIVE / NEUTRAL /
  Earth_Protective), `J2` JST SH `SM02B-SRSS-TB(LF)(SN)` 1×2
  (`+5VP` / `GND`);
- reclassify input / output / isolation / protection ratings
  under an explicit "Vendor-datasheet typicals (NOT BOM-confirmed
  and NOT compliance evidence)" heading;
- remove the misleading `1A recommended` AC-input fusing line
  that disagreed with the on-board `F1 A250-1200` polyfuse class;
  the safety-notes block now points at the populated
  `F1 A250-1200` polyfuse plus `RV1` / `C1` as the on-board
  mains-side fault protection;
- restate that mains-voltage UK / EU compliance is tracked by
  COMPLIANCE-001 and remains **OPEN**, and that no CE / UKCA /
  FCC / UL / LVD / EMC / RoHS / IEC claim is made by this
  package.

The `substitutions: power_source: "240v_ac"`,
`globals: power_source_type`, the four template diagnostic
sensors (`Supply Voltage` / `Power Source` / `Power Configuration`
/ `AC Power Connected`), and the `logger` block from line 44
onward are **byte-identical** to PR #515 / PR #520 / PR #535
state — no runtime YAML behavior change. The
[`config/hardware-catalog.json`](../../config/hardware-catalog.json)
`S360-400` row at lines 102–110 stays byte-identical (no
`schematic_status` promotion, no `schematic_file` set, no
`description` edit). The committed schematic PDF
[`docs/hardware/schematics/S360-400-R4.pdf`](schematics/S360-400-R4.pdf)
stays byte-identical (the `PS1 = HLK-10M05` value-field
discrepancy stays recorded but is **not** corrected; correction
owed to a separate later HW-ASSETS-400 follow-up). COMPLIANCE-001
mains-voltage UK / EU sign-off is unchanged (last re-check
PR #506). The status above stays `package-yaml-pending` /
`needs-package-reconciliation` + `timing/compliance-pending`:
Path B is the header-reconciliation component of the coordinated
`PACKAGE-POWER-400-001` slice; the catalog `description` is
already BOM-consistent, the `S360-400`
`schematic_status: verified` JSON-only PR is still owed
(additionally gated on the schematic-side correction of the
committed PDF's `PS1` value-field string), and the
COMPLIANCE-001 closure plus the silkscreen / PCB / creepage /
clearance / bench / thermal / EMI evidence remain owed.
`PRODUCT-POWER-400-001`, `WEBFLASH-POWER-400-001`,
`RELEASE-POWER-400-001`, and `WF-IMPORT-POWER-400-001`
(cross-repo) stay blocked on their other recorded preconditions.
See
[`s360-400-r4-power.md` §2026-05-20 — PACKAGE-POWER-400-001 package-header cleanup](s360-400-r4-power.md#2026-05-20--package-power-400-001-package-header-cleanup-bom-confirmed-part-identity-in-header-ratings-softened-downstream-slices-still-blocked)
and [`docs/cleanup-audit.md` §PACKAGE-POWER-400-001 update (2026-05-20 — Path B package-header cleanup)](../cleanup-audit.md#package-power-400-001-update-2026-05-20--path-b-package-header-cleanup).

### `power_poe.yaml` PoE-module part-identity disagreement (S360-410)

Schematic evidence:

- `S360-410` schematic: **module-side PDF committed under
  HW-ASSETS-410 (PR #516)** at
  [`docs/hardware/schematics/S360-410-R4.pdf`](schematics/S360-410-R4.pdf)
  (curated index at
  [`docs/hardware/artifacts/S360-410-R4.md`](artifacts/S360-410-R4.md));
  `config/hardware-catalog.json` still records `S360-410` →
  `schematic_status: cataloged_unverified` (HW-ASSETS-410 /
  HW-PINMAP-410-FOLLOWUP deliberately do **not** flip the JSON
  status; promotion is owed to a separate JSON-only PR after BOM
  cross-check + HW-002 OQ#6 / `S360-100-BENCH-001` J2-harness
  closure). The module-side schematic shows a **discrete** PoE PSU
  topology: `LAN_CON1 = RJP-003TC1(LPJ4112CNL)` integrated 10/100
  BASE-TX magnetics / RJ45 module with Bob-Smith bridge
  (`2x1000pF/2KV` + `2x75 Ω` + `C3 1nF` shield-to-`Lan_earth`
  bridge); `U1 = TPS2378DDAR(HSOIC-8)` PoE PD controller with
  `R1 24.9k` DEN, `R2 1.27k` CLS (`Class=0 (0.44 to 12.95W)`),
  `D1 SMAJ58A` TVS, `C2 15uF` CBULK, `R5 0.03R` RTN sense; `U2 =
  TX4138(ESOIC-8)` buck with `R3/R4 9.1k` ILIM, `L1 33uH`, `D2
  ss510`, `C6 470u`, and a `R7 10.5k` (Rd) / `R8 56.2k` (Rc)
  feedback divider giving nominal `Vout = 0.8 · (1 + Rc/Rd) ≈
  5.08 V` on `Sw_Vin_Poe`; `DCDC1 = F0505S-2WR2(SIP-7)` isolated
  5 V → 5 V (with `AM1D-0505S-NZ` annotated as alternate;
  pinout `Vin+` / `Vin-` / `Vout-` / `Vout+`); `J3` 2-pin
  "Connection to Cores" output (pin 1 = `+5VP`, pin 2 = `GND`;
  `C8 22u` bulk, `R9 1k` bleed); `D3 Green` status LED on buck
  output; four mounting holes `H1`..`H4` each labelled `Earth`;
  no on-board PoE-link / activity LED on the primary side, no
  spare-pair vs data-pair selection, no explicit 802.3at
  signature network, no secondary regulator after isolation, no
  I²C / UART / SPI / GPIO / digital-bus circuitry. The
  **HW-PINMAP-410 audit doc** has landed at
  [`docs/hardware/s360-410-r4-poe.md`](s360-410-r4-poe.md) with
  **status: `partial — schematic evidence available; package
  reconciliation, PoE PD controller / magnetics / buck / isolated
  DC/DC / harness identity evidence pending`** (promoted by
  HW-PINMAP-410-FOLLOWUP from the prior `pending —
  schematic/design evidence required`); records the
  package-header whole-module `Ag9712M / Silvertel Ag9700 / or
  similar` hint vs the schematic-shown discrete topology
  (`TPS2378DDAR / TX4138 / F0505S-2WR2 / RJP-003TC1(LPJ4112CNL)`)
  as **unresolved by this PR**, BOM-bound, and owed to
  `PACKAGE-POE-410-001`; preserves the Release-One PoE
  "schematic verification pending" caveat verbatim. PoE is SELV;
  **not** in scope for COMPLIANCE-001.

Package file:
[`packages/hardware/power_poe.yaml`](../../packages/hardware/power_poe.yaml)
is a logical PoE-power package emitting diagnostic sensors only
(`Supply Voltage`, `Power Source`, `Power Configuration`, `PoE
Power Connected`); no GPIO binding. Header comments at line 6
carry the disagreed `Ag9712M, Silvertel Ag9700, or similar`
whole-module PoE-PSU hint plus the partially-evidenced
`IEEE 802.3af / 802.3at` / `Class 0 / Class 1` / `36-57V DC` /
`5V DC, 2A (10W) or 3.3V DC` / `Overcurrent, overvoltage,
short-circuit` claims. **None of those comments is edited by
HW-009 or by HW-PINMAP-410-FOLLOWUP** — comment-only cleanup is
deferred to `PACKAGE-POE-410-001` once BOM evidence lands,
matching the rule HW-PINMAP-400-FOLLOWUP applied to
`power_240v.yaml`.

Status: `reference-only` (logical, no GPIO binding) +
`schematic-evidence-pending` (schematic consumed by
HW-PINMAP-410-FOLLOWUP; package-header reconciliation still owed)
+ `do-not-change-release-one`. HW-009 does **not** change the
package, the catalog `description` (`PoE to 5V.`), the JSON
`schematic_status`, the Release-One PoE caveat, or any reference
to PoE-410. `PACKAGE-POE-410-001` stays blocked behind BOM
cross-check, the `S360-410` `schematic_status: verified` JSON
PR, and HW-002 OQ#6 / `S360-100-BENCH-001` closure.

**2026-05-20 — `PACKAGE-POE-410-001` investigation pass addendum
(docs-only deferral).** The 2026-05-20
`PACKAGE-POE-410-001` investigation pass re-verified all five
preconditions (BOM cross-check; `S360-410`
`schematic_status: verified` JSON PR; HW-002 OQ#6 /
`S360-100-BENCH-001` J2-harness closure; package-header
reconciliation against the schematic-shown discrete topology;
Release-One PoE caveat closure as a separate later PR) remain
open and confirmed deferral.
[`packages/hardware/power_poe.yaml`](../../packages/hardware/power_poe.yaml)
stays byte-identical to PR #517 state — the stale `Ag9712M,
Silvertel Ag9700, or similar` line at line 6, the `IEEE 802.3af
(PoE) or 802.3at (PoE+)` standard line at line 7, the
`Class 0 (0.44-12.95W) or Class 1 (0.44-3.84W)` class line at
line 8, the `36-57V DC` input line at line 9, the
`5V DC, 2A (10W) or 3.3V DC` output line at line 10, the
`Overcurrent, overvoltage, short-circuit` protection line at
line 11, the `substitutions: power_source: "poe"` /
`poe_class: "0"` / `poe_standard: "802.3af"` block at lines
28–31, the `globals: power_source_type` block at lines 33–38,
the template diagnostic sensors `Supply Voltage` (constant-`5.0`
lambda) / `Power Source` / `Power Configuration` /
`PoE Power Connected` (constant-`true` lambda), the logger
config, and the `on_boot` logger statements are all preserved
byte-for-byte. The package binds **no** GPIO, I²C, UART, SPI,
DAC, or runtime hardware. The three-way catalog
[`config/hardware-catalog.json`](../../config/hardware-catalog.json)
`description: "PoE to 5V."` (line 119; no part identity
asserted) vs package header `Ag9712M, Silvertel Ag9700, or
similar` (line 6; whole-module hint) vs schematic discrete
topology (`TPS2378DDAR + TX4138 + F0505S-2WR2 +
RJP-003TC1(LPJ4112CNL)`) part-identity disagreement therefore
**stays unresolved** and remains BOM-bound. Per the explicit
HW-PINMAP-410-FOLLOWUP / PR #517 decision in
[`s360-410-r4-poe.md` §Existing package abstraction](s360-410-r4-poe.md#existing-package-abstraction)
and §Package YAML status, even a comment-only YAML cleanup that
removed the `Ag9712M, Silvertel Ag9700, or similar` line (and
softened the standard / class / input / output / protection
lines) without claiming a replacement is **deferred** to the
eventual `PACKAGE-POE-410-001` implementation PR so header
reconciliation + BOM citation + catalog `description`
reconciliation can land as one coordinated change — the same
rule PR #520 applied to the parallel `PACKAGE-POWER-400-001`
slice and `packages/hardware/power_240v.yaml`. PoE is SELV;
**not** in scope for COMPLIANCE-001. Release-One PoE
"schematic verification pending" caveat in
[`docs/release-one-hardware-audit.md` Findings → PoE PSU](../release-one-hardware-audit.md#findings)
is **preserved verbatim**. Investigation outcome recorded at
[`s360-410-r4-poe.md` §2026-05-20 — PACKAGE-POE-410-001 investigation pass](s360-410-r4-poe.md#2026-05-20--package-poe-410-001-investigation-pass)
and
[`docs/cleanup-audit.md` §PACKAGE-POE-410-001 update](../cleanup-audit.md#package-poe-410-001-update-2026-05-20--docs-only-investigation-pass).

**2026-05-20 — `HW-BOM-ASSETS-002` BOM-evidence ingest addendum
(record-only).** The `HW-BOM-ASSETS-002` record-only BOM ingest
landed the `S360-410-R4_BOM.xlsx`
(`0de7679d-S360410R4_BOM.xlsx`; 11,980 bytes; SHA256
`b5f4bad842a930de03cd47327f477c21afcb82e4533a9d8be38b54990b38f285`)
as retained-but-not-committed evidence inventoried at
[`docs/hardware/artifacts/S360-410-R4.md` §HW-BOM-ASSETS-002 BOM ingest (2026-05-20)](artifacts/S360-410-R4.md#hw-bom-assets-002-bom-ingest-2026-05-20).
The accompanying PDF re-upload (`7f920771-S360410R4.pdf`;
975,137 bytes; SHA256
`4a8b7a3b2a89006a9332eaa486743f687aaedc4b6bb807c6b25670f742ac2414`)
is **byte-identical** to the committed
[`docs/hardware/schematics/S360-410-R4.pdf`](schematics/S360-410-R4.pdf)
(HW-ASSETS-410 / PR #516); no re-commit. The BOM confirms each
load-bearing schematic part with manufacturer attribution
(`U1 TPS2378DDAR` TI, `U2 TX4138` XDS, `DCDC1 F0505S-2WR2`
EVISUN, `LAN_CON1 LPJ4112CNL` Link-PP) and **reclassifies** the
package-header / schematic disagreement above:
schematic-shown discrete topology (`TPS2378DDAR + TX4138 +
F0505S-2WR2 + RJP-003TC1(LPJ4112CNL)`) = **BOM-confirmed
sourcing truth**; package-header whole-module hint
`Ag9712M, Silvertel Ag9700, or similar`
([`packages/hardware/power_poe.yaml`](../../packages/hardware/power_poe.yaml)
line 6) = **disproved package-header comment text** (neither
`Ag9712M` nor `Silvertel Ag9700` appears anywhere in the BOM),
comment-only cleanup deferred to `PACKAGE-POE-410-001`;
schematic-annotated `AM1D-0505S-NZ` = **schematic-annotation-only
alternate not present in the BOM** (`F0505S-2WR2` EVISUN is the
BOM-confirmed populated primary for `DCDC1`); catalog
`description: "PoE to 5V."` carries no part identity and is
unchanged. PoE class declaration: BOM `R2 1.27k` (PANASONIC) is
consistent with the schematic-recorded `Class=0 (0.44 to 12.95W)`
programming; whether the design is intended as 802.3af-only or
802.3af/at-capable remains a design-intent question. Output
rating: BOM `DCDC1 F0505S-2WR2` + BOM `R7 10.5k` / `R8 56.2k`
feedback divider are consistent with the schematic-recorded
5 V → 5 V isolated output only; the package-header `or 3.3V DC`
option is not schematic- or BOM-evidenced. The
`packages/hardware/power_poe.yaml` file stays **byte-identical to
PR #517 / PR #526** (stale `Ag9712M, Silvertel Ag9700, or
similar` header at line 6, IEEE 802.3af / 802.3at standard line,
Class 0 / Class 1 line, 36–57 V DC input line, 5 V / 3.3 V
output line, OCP / OVP / SCP protection line, substitutions /
globals / template sensors / logger / on_boot blocks all
preserved). The `config/hardware-catalog.json` `S360-410` row at
lines 112–120 stays byte-identical (no `schematic_status`
promotion, no `schematic_file` set). Other BOM-confirmed
components: `R1 24.9k` (EVER OHMS) DEN; `R3, R4 9.1k`
(UNI-ROYAL) paired ILIM; `R5 0.03R` (YAGEO) RTN sense; `R7
10.5k` (KOA) `Rd` / `R8 56.2k` (FOJAN) `Rc` feedback divider;
`L1 33uH` (Yanchuang); `D1 SMAJ58A` (Littelfuse) TVS; `D2 ss510`
(MDD SS510C) Schottky; `D3 Green` (Orient) indicator; `C2 15uF`
(Rubycon) CBULK; `C6 470u` (ROQANG) buck-output bulk; `C8 22u`
(muRata) `+5VP` output bulk; `J3` JST `SM02B-SRSS-TB(LF)(SN)`
1×2 Core-facing connector. Per-component tolerance / power
rating evidence beyond the BOM strings, silkscreen pin-1 markers
on `J3`, PCB / isolation-barrier / `H1`–`H4` bonding evidence,
PoE link-up / signature / classification / load regulation /
inrush / thermal / insulation / Hi-pot / earth-continuity /
leakage / EMI / EMC measurements, IEEE 802.3af / 802.3at
compliance test reports, and the `F0505S-2WR2`-vs-`AM1D-0505S-NZ`
primary-vs-alternate intent resolution are all bench /
silkscreen / vendor-datasheet evidence and are **not** resolved
by this ingest. PoE is SELV; **not** in scope for
COMPLIANCE-001. Release-One PoE "schematic verification pending"
caveat is **preserved verbatim**. The `BOM cross-check missing`
precondition listed under `PACKAGE-POE-410-001` /
`PRODUCT-POE-410-001` / `WEBFLASH-POE-410-001` /
`RELEASE-POE-410-001` is now **resolved at the discrete-topology
part-identity layer**; each slice stays blocked on its other
recorded preconditions (the `S360-410` `schematic_status:
verified` JSON PR; HW-002 OQ#6 / `S360-100-BENCH-001`
J2-harness closure; the package-header comment cleanup itself;
the Release-One PoE caveat closure as a separate later PR;
product-onboarding approval; UX-class decision; release-time
sub-gates). The status above stays `reference-only` +
`schematic-evidence-pending` + `do-not-change-release-one`. See
[`s360-410-r4-poe.md` §2026-05-20 — HW-BOM-ASSETS-002 BOM ingest](s360-410-r4-poe.md#2026-05-20--hw-bom-assets-002-bom-ingest-bom-confirmed-part-identity-reclassified-package-header-cleanup-still-deferred)
and [`docs/cleanup-audit.md` §HW-BOM-ASSETS-002 update](../cleanup-audit.md#hw-bom-assets-002-update-2026-05-20--s360-400--s360-410-bom-evidence-ingest).

## Recommended follow-up PRs

Each item below is **separate**, **scoped**, and **not approved by
HW-009**. They are recorded here so the audit's findings have a clear
next-action chain.

### HW-010 — Fix Sense360 LED package pin mapping (resolved)

- **Status.** **Resolved.** HW-010 landed as a scoped one-package edit:
  [`packages/hardware/led_ring_ceiling.yaml`](../../packages/hardware/led_ring_ceiling.yaml)
  now binds `led_data_pin: GPIO38`, matching the verified `S360-100-R4`
  schematic (`IO38 = LED_DATA → U2A 74LVC1G07 → R8 → J3 → S360-300 J1`).
- **Test guard.** [`tests/test_led_package_mapping.py`](../../tests/test_led_package_mapping.py)
  locks in the new pin value, the Release-One LED exclusion, the
  absence of any `LED` token in
  [`config/webflash-builds.json`](../../config/webflash-builds.json), and
  the FanTRIAC `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` entry's
  `status: blocked`, `blocker: HW-005`,
  `webflash_build_matrix: false`. The existing test suite
  (`tests/validate_configs.py` and the WebFlash / catalog / product /
  release-notes validators) passes unchanged.
- **What HW-010 did not change.** No `LED` token added to the
  Release-One config string. No WebFlash LED build added. No product
  catalog LED entry added. No `LED` Release-One YAML include added. The
  Release-One config string remains `Ceiling-POE-VentIQ-RoomIQ` and the
  artifact remains
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`.
- **Still unresolved after HW-010.** The wall LED package
  ([`packages/hardware/led_ring_wall.yaml`](../../packages/hardware/led_ring_wall.yaml),
  `led_data_pin: GPIO48`) and the legacy S3 Core package
  ([`packages/hardware/sense360_core_ceiling_s3.yaml`](../../packages/hardware/sense360_core_ceiling_s3.yaml),
  `led_data_pin: GPIO14`) are **not** changed by HW-010. Neither has a
  Core-side schematic that proves the same `LED_DATA` path; both are
  documented here as unresolved. The S3 Core package has no product
  YAML consumer in this repo. The wall LED package is consumed by
  `legacy-compatible` products only.
- **Still required before any LED-bearing config can ship.** A future
  LED-bearing config (e.g. `Ceiling-POE-VentIQ-RoomIQ-LED`) is a
  **separate** product PR with its own catalog entry, build-matrix
  entry, release-notes draft, and onboarding gate per
  [`docs/product-onboarding.md`](../product-onboarding.md). HW-010 only
  fixes the underlying package mapping.

### J10 / J6 silkscreen reconciliation

- **Scope.** Physical inspection of the manufactured `S360-100-R4` and
  `S360-200-R4` boards to determine which of the two existing
  schematic-backed reference docs matches the silkscreen pin order.
  Once identified, update **only** the doc that disagrees with the
  physical board — not both.
- **Gate.** Requires a real board, not another PDF. No firmware change
  is expected; package YAMLs do not bind J10 / J6 by pin number.
- **Out of scope.** Any firmware pin rebind. Until the silkscreen check
  is done, do not derive any pin assignment from either pin order.

### `AirQ_Led` / `AirQ_Status_Led` indicator-line verification

- **Scope.** Resolve HW-002 Open Question #4: whether the legacy
  `AirQ_Led` (`IO8`) and `AirQ_Status_Led` (`IO7`) nets actually drive a
  module-side indicator on AirIQ vs VentIQ, or whether one or both
  modules leave them unconnected.
- **Gate.** Requires bench verification on both the AirIQ
  (`S360-210-R4`) and VentIQ (`S360-211-R4`) boards. The schematic PDFs
  alone do not commit to a behaviour.
- **Out of scope.** Any package YAML rename (the legacy filenames are
  retained per WebFlash contract §6). Any change to the AirIQ ↔ VentIQ
  mutex.

### Systemic Core abstract-bus rebind

- **Scope.** The systemic mismatch between
  [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml)
  and the `S360-100-R4` schematic — the `halo_i2c` / `expansion_i2c` /
  `uart_bus` / relay / PIR / status-LED / `expansion_gpio*`
  abstractions are not pin-correct against the schematic.
- **Gate.** Owned by
  [`release-one-hardware-audit.md` Required follow-ups #2 and #3](../release-one-hardware-audit.md#required-follow-ups).
  Cannot land without:
  - re-validating every non-Release-One product YAML that consumes
    `sense360_core_ceiling.yaml`,
  - reconciling the Core J10 vs RoomIQ J6 pin-order silkscreen check
    above,
  - rebinding `comfort_ceiling.yaml` and `presence_ceiling.yaml` (and
    the AirIQ / VentIQ package family) to the schematic-correct shared
    I²C bus (`IO48` / `IO45`) and the two radar UARTs
    (`Hi-Link` on `IO1` / `IO2`; `SEN0609` on `IO4` / `IO5`).
- **Out of scope for HW-009.** HW-009 only documents the gap.
- **Investigation outcome.** The `CORE-ABSTRACT-BUS-001` docs-only
  audit + slice plan has since landed at
  [`core-abstract-bus-reconciliation.md`](core-abstract-bus-reconciliation.md).
  It splits the implementation into three coordinated future PRs —
  `CORE-ABSTRACT-BUS-001A` (`relay_pin → GPIO3`),
  `CORE-ABSTRACT-BUS-001B` (single shared I²C bus consolidation), and
  `CORE-ABSTRACT-BUS-001C` (UART split + status LED + PIR + ALS_INT
  + expansion GPIO rebind) — and records the GPIO3 collision between
  the schematic-correct `relay_pin` and the existing
  `comfort_ceiling_als_int_pin: GPIO3` (which prevents the relay
  slice from landing in isolation). The audit performs no firmware
  rebind; it is the planning artifact that the future implementation
  PRs will reference.
- **`CORE-ABSTRACT-BUS-001C` investigation pass (2026-05-19).**
  A docs-only `001C` investigation pass ran on 2026-05-19 and is
  **confirmed deferred** — all six preconditions
  (`S360-100-BENCH-001` silkscreen evidence, RoomIQ / AirIQ / VentIQ
  rebind plan, expansion-GPIO bench evidence or documented retirement
  decision, ESP32-S3 `GPIO3` strap-pin boot-behaviour bench
  characterisation, `tests/test_core_abstract_bus.py` scaffold, and
  the non-Release-One product re-validation pass) remain open. See
  [`core-abstract-bus-reconciliation.md` §CORE-ABSTRACT-BUS-001 audit log](core-abstract-bus-reconciliation.md#core-abstract-bus-001-audit-log)
  and
  [`docs/cleanup-audit.md` §CORE-ABSTRACT-BUS-001C update](../cleanup-audit.md#core-abstract-bus-001c-update-2026-05-19--docs-only-investigation-pass).
  HW-009 makes no firmware change as a result of this re-check.
- **All three CORE-ABSTRACT-BUS-001 slices have now landed at the
  substitution layer (2026-05-22).** `CORE-ABSTRACT-BUS-001C` landed
  via PR #557, `CORE-ABSTRACT-BUS-001A` via PR #558, and
  `CORE-ABSTRACT-BUS-001B` via `CORE-ABSTRACT-BUS-001B-IMPLEMENT-001`
  (the same PR as this audit-log update) — the hard rename to the
  canonical shared `core_i2c` bus id (`GPIO48` SDA / `GPIO45` SCL
  / `400kHz`) was applied across the seven in-scope Core abstract
  packages, the 10 in-scope expansion-package `*_i2c_id` consumer
  defaults, and the hard-coded `packages/features/ceiling_halo_leds.yaml`
  literal. The `SharedI2CBusTests` class in
  [`tests/test_core_abstract_bus.py`](../../tests/test_core_abstract_bus.py)
  (13 new cases) pins the rename against future regression. The
  Release-One product YAML package-stack systemic mismatch
  enumerated at [§Release-One product YAML package stack](#release-one-product-yaml-package-stack)
  above (lines 382 ff.) is **closed at the substitution layer for the
  I²C bus axis** — every I²C-bound sensor on Release-One and the LED
  preview now resolves to `i2c_id: core_i2c` on the schematic-correct
  `GPIO48` / `GPIO45` bus. The HW-009 row stays at
  `needs-package-change` for the **other** historical mismatches
  (UART nets, relay pin, status LED, PIR, expansion GPIO) that are
  owned by `001A` / `001C` (already merged) and the still-deferred
  voice-variant `relay_pin: GPIO4`. No Release-One identity or
  WebFlash exposure change results from `001B`.

### HW-005 (FanTRIAC) — remains blocked separately

- **Status.** HW-009 makes **no change** to HW-005. FanTRIAC stays
  blocked. The full missing-evidence checklist is at
  [`release-one-hardware-audit.md#missing-evidence-checklist`](../release-one-hardware-audit.md#missing-evidence-checklist).
- **Additional gate.** Even after HW-005's hardware evidence lands,
  FanTRIAC is also subject to the mains-voltage compliance review
  tracked under COMPLIANCE-001
  ([`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md)).

## Do-not-change list

This audit does **not** change any of the following. If you are reading
this audit looking for justification to change one of them, look
elsewhere — this audit explicitly does not provide that justification.

- The Release-One config string `Ceiling-POE-VentIQ-RoomIQ`.
- The Release-One artifact name
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`.
- [`config/webflash-builds.json`](../../config/webflash-builds.json) —
  no entries added, removed, or renamed.
- [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json)
  — no taxonomy values changed.
- [`config/product-catalog.json`](../../config/product-catalog.json) —
  no lifecycle statuses changed; no `blocked_modules` lists changed.
- [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  — no `schematic_status`, `schematic_file`, or SKU rows changed.
- Any product YAML under [`products/`](../../products/) (including
  legacy / Mini / Voice legacy variants and the FanTRIAC blocked /
  reference YAML).
- Any WebFlash wrapper under [`products/webflash/`](../../products/webflash/).
- Any package YAML under [`packages/`](../../packages/) (hardware,
  expansions, features, base). **No package GPIO is changed.**
- Any package filename. Legacy `airiq_bathroom_base.yaml`,
  `comfort_ceiling.yaml`, `presence_ceiling.yaml`, `led_ring_*.yaml`
  filenames are retained per WebFlash contract §6.
- Any workflow under [`.github/workflows/`](../../.github/workflows/).
- Any script under [`scripts/`](../../scripts/).
- Any test under [`tests/`](../../tests/). **HW-009 adds no tests.**
- Any component under [`components/`](../../components/).
- Any include under [`include/`](../../include/).
- The Sense360 LED Release-One exclusion. HW-009 does **not** add
  `LED` to the Release-One config string; HW-009 does **not** edit
  `led_ring_ceiling.yaml`. The `GPIO14` → `GPIO38` fix is a future
  follow-up (HW-010), not part of HW-009.
- The FanTRIAC HW-005 blocked status. HW-009 does **not** change the
  GPIOs, the catalog entry, or the missing-evidence checklist.
- The mains-voltage compliance status for `S360-320` or `S360-400`
  (COMPLIANCE-001).
- Any pin map in any reference doc under
  [`docs/hardware/`](.). HW-009 does **not** edit the per-board
  reference docs; their existing Open-Questions lists remain the
  authoritative record of unresolved pin / connector questions.

## Validation results

The following read-only validations and sanity greps were run after
this audit doc was written. All passed; none of the do-not-change
artifacts above were modified.

### Test commands

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
python3 scripts/validate_product_catalog_consistency.py
```

Each command exited zero. None of them mutated any file; they read the
existing catalog, build matrix, compatibility snapshot, package
includes, and product YAMLs and asserted invariants.

### Sanity grep expectations

After HW-009 lands, these greps should hold:

- `grep -RIn "GPIO14\|IO38\|LED_DATA" docs packages products config` —
  after HW-010 has also landed, the `led_ring_ceiling.yaml` hit binds
  `GPIO38`, not `GPIO14`. Remaining `GPIO14` hits in package YAML are
  on unrelated boards / signals
  ([`packages/hardware/sense360_core_ceiling_s3.yaml`](../../packages/hardware/sense360_core_ceiling_s3.yaml)
  — legacy S3 Core; no schematic backing; no product consumer in this
  repo;
  [`packages/hardware/sense360_core_poe.yaml`](../../packages/hardware/sense360_core_poe.yaml)
  — `w5500_cs_pin`, different signal;
  [`packages/expansions/sense360_fan_pwm.yaml`](../../packages/expansions/sense360_fan_pwm.yaml)
  — `fan3_tach_pin`, different signal). Every documentation `GPIO14`
  hit is either historical narration of the HW-009 / HW-010 chain or
  the unresolved wall LED / S3 Core legacy note. The `IO38` /
  `LED_DATA` evidence remains the authoritative schematic value in the
  Core and LED reference docs.
- `grep -RIn "J10\|J6\|RoomIQ" docs packages products config` — the
  Core J10 and RoomIQ J6 pin-order tables are unchanged in both
  reference docs; the discrepancy is unresolved by HW-009 (it requires
  silkscreen verification).
- `grep -RIn "AirQ_Led\|AirQ_Status_Led\|airiq_bathroom_base" docs packages products config`
  — no AirIQ / VentIQ package binds `AirQ_Led` / `AirQ_Status_Led`;
  the `airiq_bathroom_base.yaml` filename is unchanged.
- `grep -RIn "FanTRIAC\|GPIO5\|GPIO6" docs packages products config` —
  the `fan_triac_gate_pin: GPIO5` / `fan_triac_zc_pin: GPIO6`
  placeholders in
  [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml)
  are unchanged; FanTRIAC stays `blocked` under HW-005.

## See also

- [`docs/hardware/s360-100-r4-core.md`](s360-100-r4-core.md) — Sense360
  Core schematic-backed pin / connector reference; authoritative for
  `IO38 = LED_DATA`, `IO14 = SCS`, `IO5 = SEN0609_TX`, `IO6 =
  out(gpio6)`, and the J9 / J10 / J15 connector tables.
- [`docs/hardware/s360-200-r4-roomiq.md`](s360-200-r4-roomiq.md) —
  Sense360 RoomIQ schematic-backed reference; carries the J6 pin order
  that disagrees with the Core J10 table.
- [`docs/hardware/s360-210-r4-airiq.md`](s360-210-r4-airiq.md) —
  Sense360 AirIQ schematic-backed reference.
- [`docs/hardware/s360-211-r4-ventiq.md`](s360-211-r4-ventiq.md) —
  Sense360 VentIQ schematic-backed reference.
- [`docs/hardware/s360-300-r4-led.md`](s360-300-r4-led.md) — Sense360
  LED schematic-backed reference; explicitly records the `GPIO14` vs
  `IO38` `LED_DATA` discrepancy.
- [`docs/hardware/remaining-board-documentation-audit.md`](remaining-board-documentation-audit.md)
  — HW-004 / HW-006 per-board documentation-state classification, plus
  HW-007 schematic ingest and HW-008 JSON refresh subsections.
- [`docs/hardware/hardware-artifact-policy.md`](hardware-artifact-policy.md)
  — HW-ASSETS-001 canonical policy for hardware source / manufacturing
  artifacts (schematic PDF / KiCad / BOM / CPL / Gerbers / STEP /
  images / raw vendor ZIPs). Defines the per-board artifact index
  schema whose `package_yaml_status` field mirrors this audit's
  six-label classification taxonomy.
  — HW-ASSETS-001 commit / exclude rules for hardware artifacts and the
  per-board curated-index pattern under
  [`docs/hardware/artifacts/`](artifacts/) (HW-ASSETS-002 lands the first
  per-board index for `S360-100-R4`).
- [`docs/release-one-hardware-audit.md`](../release-one-hardware-audit.md)
  — Release-One firmware-vs-schematic audit, the FanTRIAC HW-005
  resolution, the Sense360 LED policy, and the Required follow-ups
  list (#2 / #3 own the systemic Core rebind).
- [`docs/webflash-compatibility-taxonomy-audit.md`](../webflash-compatibility-taxonomy-audit.md)
  — COMPAT-001 per-token taxonomy audit.
- [`docs/product-onboarding.md`](../product-onboarding.md) — PRODUCT-004
  ordered safe sequence for adding any new product / config; HW-010
  and a future LED-bearing config would each go through this gate.
- [`docs/cleanup-audit.md`](../cleanup-audit.md) — classification of
  stale / current / blocked-reference / legacy-compatible repo content.
- [`docs/webflash-contract.md`](../webflash-contract.md) — canonical
  WebFlash artifact / grammar / token contract; §6 retains legacy
  package filenames on purpose.
- [`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md)
  — COMPLIANCE-001 mains-voltage UK / EU compliance tracker;
  additional gate on any future FanTRIAC unblock.
- [`config/hardware-catalog.json`](../../config/hardware-catalog.json) —
  machine-readable hardware catalog. After HW-008, the five SKUs
  inspected here (`S360-100`, `S360-200`, `S360-210`, `S360-211`,
  `S360-300`) are `schematic_status: verified`.
- [`config/product-catalog.json`](../../config/product-catalog.json) —
  product lifecycle catalog. Release-One is `status: production`;
  FanTRIAC variant is `status: blocked`, `blocker: HW-005`.
- [`config/webflash-builds.json`](../../config/webflash-builds.json) —
  WebFlash build matrix; contains only `Ceiling-POE-VentIQ-RoomIQ`.
- [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json)
  — WebFlash compatibility taxonomy; preserves the AirIQ ↔ VentIQ
  mutex and the fan-driver max-one-of rule.
- [`docs/product-availability-taxonomy.md`](../product-availability-taxonomy.md)
  — PRODUCT-AVAIL-001 canonical product availability taxonomy.
  Maps this audit's six-label classification onto the
  `package-yaml-ready` rung (`confirmed-ok` and `confirmed-ok` with
  caveats) and the `package-yaml-pending` rung (every other label
  except `blocked`, which is its own axis). Documentation only.
- [`docs/hardware/board-readiness-matrix.md`](board-readiness-matrix.md)
  — HW-GAP-001 board-level readiness matrix. Cross-board view that
  consumes this audit's package-mapping vocabulary as the
  `Package YAML status` column. Documentation only.
- [`docs/hardware/package-readiness-matrix.md`](package-readiness-matrix.md)
  — PACKAGE-GAP-001 package-level readiness gate. Documents the
  per-package verdict for the six in-scope expansion / power
  packages
  ([`packages/expansions/fan_relay.yaml`](../../packages/expansions/fan_relay.yaml),
  [`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml),
  [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml),
  [`packages/expansions/fan_triac.yaml`](../../packages/expansions/fan_triac.yaml),
  [`packages/hardware/power_240v.yaml`](../../packages/hardware/power_240v.yaml),
  [`packages/hardware/power_poe.yaml`](../../packages/hardware/power_poe.yaml))
  using the policy-only labels
  (`ready-for-package-change` / `needs-package-reconciliation` /
  `schematic-evidence-pending` / `bench-evidence-pending` /
  `timing/compliance-pending` / `reference-only` /
  `do-not-change-release-one` /
  `blocked-from-standard-exposure`). Records the load-bearing
  rule "package YAML changes require schematic-backed pin-map
  evidence", the per-slice follow-up PRs
  (`PACKAGE-RELAY-001` / `PACKAGE-PWM-001` / `PACKAGE-DAC-001` /
  `PACKAGE-TRIAC-001` / `PACKAGE-POWER-400-001` /
  `PACKAGE-POE-410-001`), and the paired
  `CORE-ABSTRACT-BUS-001` follow-up that owns the systemic Core
  abstract-bus mismatch enumerated by HW-009. Documentation only;
  no package YAML edits.
- [`docs/product-readiness-matrix.md`](../product-readiness-matrix.md)
  — PRODUCT-GAP-001 product-level readiness gate. Per-family
  verdict for the FanRelay / FanPWM / FanDAC / FanTRIAC /
  PWR-240V / PoE-410 candidate product families; consumes this
  audit (transitively, via the package matrix) for the
  `Package readiness` column and records the downstream
  per-family follow-up PRs (`PRODUCT-RELAY-001` /
  `PRODUCT-PWM-001` / `PRODUCT-DAC-001` / `PRODUCT-TRIAC-001` /
  `PRODUCT-POWER-400-001` / `PRODUCT-POE-410-001`) plus the
  separate WebFlash exposure chain
  (`WEBFLASH-GAP-001` / `RELEASE-GAP-001` / `WF-IMPORT-GAP-001`,
  `WF-TRIAC-001` for the FanTRIAC advanced-flow). Documentation
  only; no product YAML edits.
- [`docs/hardware/s360-311-r4-pwm.md`](s360-311-r4-pwm.md) —
  HW-PINMAP-311 pin / package mapping audit for `S360-311` Sense360
  PWM, **status: `partial — schematic evidence available; package
  reconciliation pending`**. Records the SX1509-channel vs
  direct-ESP32-GPIO mapping disagreement for
  [`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml)
  (`fan_pwm_pin: ${expansion_gpio1}` and `fan_tach_pin:
  ${expansion_gpio2}` resolve to direct ESP32 expansion GPIOs while
  the Core schematic routes `TachPMW*` / `Pul_Cou*` through the
  SX1509 expander); explicitly defers this to the systemic Core
  abstract-bus rebind owned by Required follow-ups #2 / #3 in
  [`release-one-hardware-audit.md`](../release-one-hardware-audit.md#required-follow-ups)
  and to a future `PACKAGE-GAP-001` FanPWM slice. HW-009 does not
  reclassify `fan_pwm.yaml` here — `package-yaml-pending` / `needs-
  package-reconciliation` is recorded in the per-board audit doc.
- [`docs/hardware/s360-312-r4-dac.md`](s360-312-r4-dac.md) —
  HW-PINMAP-312 pin / package mapping audit for `S360-312` Sense360
  DAC, **status: `partial — schematic evidence available; package
  reconciliation pending`**. Records the Core `J7` pin-1 `+5V` vs
  Module `J1` pin-1 `+3.3V` voltage-rail discrepancy, the DIP-switch
  I²C address-selection scheme on the two `GP8403-TC50-EW` DACs
  (`IC1` / `IC2`), the UART0-vs-Nextion arbitration question on
  Module `J1` pins 4 / 5, and the stale header-comment connector /
  GPIO claims (file lines 13–18 reading `Pin 4 SDA → GPIO39`,
  `Pin 5 SCL → GPIO40`, `Pin 2 3.3V → Power`, `Pin 1 GND → Ground`)
  in [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)
  that disagree with both the Core `J7` capture and the Module `J1`
  capture. HW-PINMAP-312 is out of scope for HW-009 today — `S360-312`
  is still `schematic_status: cataloged_unverified` and is therefore
  out of HW-009's verified-schematic scope — but the per-board audit
  doc records `fan_gp8403.yaml` as `package-yaml-pending` / `needs-
  package-reconciliation`. The active YAML body's `${fan_dac_i2c_id}`
  / `${fan_dac_address}` substitutions are abstract-bus inheritance
  and do not depend on the stale header-comment claims; resolution
  belongs to `HW-PINMAP-312-FOLLOWUP` and to a future `PACKAGE-GAP-001`
  FanDAC slice.

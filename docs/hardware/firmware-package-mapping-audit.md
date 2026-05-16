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
  — Sense360 PoE PSU diagnostic-only logical package.

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
edit either reference doc.

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
    `IO3`.
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
`sense360_core_ceiling.yaml`.

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
  route via the SX1509.

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

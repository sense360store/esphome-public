# Sense360 Hardware Catalog

## Purpose

This document is the canonical mapping of Sense360 boards and modules to their
**friendly names**, **SKUs**, **revisions**, and **legacy names**. It is the
naming source of truth for ESPHome product YAML comments, customer-facing docs,
WebFlash module labels, and future hardware pin/connector reference documents.

The machine-readable mirror of this catalog is
[`../config/hardware-catalog.json`](../config/hardware-catalog.json).

## Naming rule

Friendly names (the **Friendly name** column below) are canonical going forward.
Old names appear only in the **Old name** column for legacy reference and must
not be used in new user-facing documentation, YAML, or build artifacts.

Use `Ceiling`, never `Celling`. `Celling` is only acceptable when literally
quoting a legacy old-name field that contained the typo.

## Catalog

| Group   | Type      | Friendly name      | SKU      | Rev | Old name                        | What it does |
|---------|-----------|--------------------|----------|-----|---------------------------------|--------------|
| Ceiling | Hub       | Sense360 Core      | S360-100 | R4  | 360Core_Ceiling_V3_R            | Main board. Has the ESP32-S3 and connectors for all other modules. |
| Ceiling | Sensor    | Sense360 RoomIQ    | S360-200 | R4  | Presence + Comfort (two boards) | Merged board. PIR, LD2450, SEN0609, LTR-303ALS light, SHT4x temp/humidity, BMP581 pressure. |
| Ceiling | Sensor    | Sense360 AirIQ     | S360-210 | R4  | AirIQ Ceiling                   | Air quality board. CO2 SCD41, VOC SGP41, gas MICS-4514 with STM8. Connectors for SPS30 PM and SFA40 HCHO. |
| Ceiling | Sensor    | Sense360 VentIQ    | S360-211 | R4  | Bathroom Pro                    | Smaller bathroom air-quality board. SGP41 on board. Connectors for IR temp and SPS30. |
| Ceiling | Indicator | Sense360 LED       | S360-300 | R4  | LED Ring                        | Ring of WS2812B LEDs. |
| Inline  | Driver    | Sense360 Relay     | S360-310 | R4  | S360-Relay-C                    | On/off relay for bathroom fans. |
| Inline  | Driver    | Sense360 PWM       | S360-311 | R4  | 12vFan_PWM_PulseCounter         | 12V PWM fan driver, up to 4 fans with tach feedback. |
| Inline  | Driver    | Sense360 DAC       | S360-312 | R4  | Fan_GP8403                      | 0 to 10V analog fan driver, for example Cloudlift S12. |
| Inline  | Driver    | Sense360 TRIAC     | S360-320 | R4  | TRIAC_Board                     | Phase dimmer for mains fan or lamp. |
| Power   | PSU       | Sense360 240v PSU  | S360-400 | R4  | PWR Module                      | Mains to 5V using HLK-5M05. |
| Power   | PSU       | Sense360 PoE PSU   | S360-410 | R4  | PoE Module                      | PoE to 5V. |

## SKU → board package

Each catalog SKU maps to a SKU-aligned **board package** under
[`../packages/boards/`](../packages/boards/) — the authoritative, self-contained
firmware definition of that board (chip / pin map / connector nets). The legacy
functional package names are retained as thin `!include` **aliases** of the
board package (path preserved; see
[`arch-board-bundle-plan.md`](arch-board-bundle-plan.md) §3.3). Full layout:
[`system-architecture.md`](system-architecture.md#inside-esphome-public-board--bundle--alias--shim-layers).

| SKU | Friendly name | Authoritative board package |
|-----|---------------|-----------------------------|
| S360-100 | Sense360 Core | [`packages/boards/s360-100-core.yaml`](../packages/boards/s360-100-core.yaml) (+ mount/power/voice overlays; Core mount paths still wrap the legacy `hardware/sense360_core_*.yaml` source until its flip lands) |
| S360-200 | Sense360 RoomIQ | [`packages/boards/s360-200-roomiq.yaml`](../packages/boards/s360-200-roomiq.yaml) (authoritative per driver: `…-climate` + `…-radar`, ceiling & wall) |
| S360-210 | Sense360 AirIQ | [`packages/boards/s360-210-airiq.yaml`](../packages/boards/s360-210-airiq.yaml) (+ `-wall`, `-ceiling-s3`) |
| S360-211 | Sense360 VentIQ | [`packages/boards/s360-211-ventiq.yaml`](../packages/boards/s360-211-ventiq.yaml) (+ `-pro`) |
| S360-300 | Sense360 LED | [`packages/boards/s360-300-led.yaml`](../packages/boards/s360-300-led.yaml) (+ mic/voice variant) |
| S360-410 | Sense360 PoE PSU | [`packages/boards/s360-410-poe-psu.yaml`](../packages/boards/s360-410-poe-psu.yaml) |
| S360-310 / 311 / 312 / 320 / 400 | Relay / PWM / DAC / TRIAC / 240v PSU | *Not in the board layer yet* — remain expansion/hardware packages behind their evidence / compliance gates. |

This mapping is naming/structure only; it changes **no** `schematic_status`,
config string, artifact name, or shippability — those remain governed by
[`../config/hardware-catalog.json`](../config/hardware-catalog.json) and the
release configs.

## Verified schematics currently available

The following boards have schematic PDFs pinned to this repository under
[`hardware/schematics/`](hardware/schematics/), a standalone pin /
connector reference doc under `docs/hardware/`, and
`schematic_status: verified` with a `schematic_file` path in
[`../config/hardware-catalog.json`](../config/hardware-catalog.json):

- `S360-100-R4` — Sense360 Core ([PDF](hardware/schematics/S360-100-R4.pdf),
  [doc](hardware/s360-100-r4-core.md))
- `S360-200-R4` — Sense360 RoomIQ ([PDF](hardware/schematics/S360-200-R4.pdf),
  [doc](hardware/s360-200-r4-roomiq.md))
- `S360-210-R4` — Sense360 AirIQ ([PDF](hardware/schematics/S360-210-R4.pdf),
  [doc](hardware/s360-210-r4-airiq.md))
- `S360-211-R4` — Sense360 VentIQ ([PDF](hardware/schematics/S360-211-R4.pdf),
  [doc](hardware/s360-211-r4-ventiq.md))
- `S360-300-R4` — Sense360 LED ([PDF](hardware/schematics/S360-300-R4.pdf),
  [doc](hardware/s360-300-r4-led.md))

The remaining catalog rows — `S360-310` Sense360 Relay, `S360-311` Sense360
PWM, `S360-312` Sense360 DAC, `S360-320` Sense360 TRIAC, `S360-400` Sense360
240v PSU, and `S360-410` Sense360 PoE PSU — are still marked
`schematic_status: cataloged_unverified` in
[`../config/hardware-catalog.json`](../config/hardware-catalog.json). Their
friendly names, SKUs, and revisions are committed naming, but the underlying
module-side schematics have not been pinned to this repo yet.

> **HW-007 / HW-008 ingest.** HW-007 committed the schematic PDFs and the
> three new standalone reference docs for AirIQ, VentIQ, and Sense360 LED.
> HW-008 then aligned the machine-readable
> [`../config/hardware-catalog.json`](../config/hardware-catalog.json) with
> that committed evidence: `S360-100`, `S360-200`, `S360-210`, `S360-211`,
> and `S360-300` are now `schematic_status: verified` with their
> `schematic_file` pointing under `docs/hardware/schematics/`. **Verified
> schematic evidence is not a shippability claim.** HW-008 does not promote
> any module into Release-One, does not unblock FanTRIAC (HW-005), does not
> add `LED` to the Release-One config string `Ceiling-POE-VentIQ-RoomIQ`,
> and does not change the mains-voltage compliance status of `S360-400` or
> `S360-320` (see [COMPLIANCE-001](compliance/mains-voltage-uk-eu-assessment.md)).

> Firmware pin mappings must not be considered verified merely because a
> board has a schematic-backed reference doc. Release-One YAML and package
> pin maps remain subject to the separate firmware-audit follow-ups tracked
> in [`release-one-hardware-audit.md`](release-one-hardware-audit.md).

## Companion file

- [`../config/hardware-catalog.json`](../config/hardware-catalog.json) —
  machine-readable mirror of this catalog with `schematic_status` per entry.
- [`hardware/remaining-board-documentation-audit.md` (archived)](archive-index.md)
  — HW-004 / HW-006 audit that classifies every catalog row's documentation
  state (`documented` / `partially-documented` / `cataloged-unverified` /
  `blocked` / `not-needed-for-release-one`) and records the evidence
  available vs. missing for each board.
- [`compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
  — COMPLIANCE-001 mains-voltage UK / EU compliance-assessment tracker
  for `S360-400` Sense360 240v PSU and `S360-320` Sense360 TRIAC.
  Documentation only; not a compliance declaration. Release-One uses
  PoE (`S360-410`) and is separate from this tracker.

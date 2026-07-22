# Sense360 blower framework (BLOWER-FRAMEWORK-001)

**Canonical id:** `BLOWER-FRAMEWORK-001`
**Type:** Firmware behaviour framework + compile-only validation fixture.
This document describes the customer blower experience for the Sense360 Core's
dedicated on-board FAN net. It changes no release, channel, WebFlash or
commercial state; the blower is a fan output and ships **compile-only** under
the *Fans are never stable* standing gate
([`docs/standing-invariants.md`](../standing-invariants.md)).

Nothing here claims hardware, bench, airflow, electrical-safety, thermal,
compliance or commercial validation.

## Purpose

One polished, simple customer experience for the Core's on-board blower — the
customer never needs to know about GPIOs, MOSFETs or the AirIQ engine:

* **Blower** — the single customer control: a binary (on/off) fan. There is
  deliberately **no** speed / preset / oscillation / direction control.
* **Blower Mode** — *Manual* (the customer owns the blower) or *Auto* (the
  blower follows the canonical AirIQ ventilation demand).
* **Blower Auto Trigger** — *Ventilate now* / *Ventilate soon*: the AirIQ demand
  level at which Auto starts the blower (conservative default: only *Ventilate
  now*).

## Hardware contract (verified S360-100-R4)

Source of truth: [`docs/hardware/s360-100-r4-core.md`](../hardware/s360-100-r4-core.md)
and the owner-provided `S360-100-R4` schematic. This framework encodes no more
than the contract proves.

| Fact | Value |
|---|---|
| Blower drive net | Core `FAN` net — schematic `IO21` (ESP32-S3 `GPIO21`) |
| Switching element | `Q4` `SI2302S` low-side MOSFET |
| Connector | `J13`, a two-wire binary 5 V blower output (pins: +5V, FAN, GND) |
| Feedback | **None** — no tach, speed-PWM, current, airflow or physical-rotation feedback exists on J13 |
| `GPIO46` | `GP_Fan_Status_Led`, a Core-side status indicator — **never** rotation feedback; the blower framework never touches it |
| `GPIO3` | the generic Relay net (J4), a **separate** control owned by the Core board (`main_relay`) — the blower framework never drives it |

Because the FAN net is a one-way binary drive, the firmware commands only
`on`/`off` and can never verify the blower physically spun. The framework
therefore makes **no** speed / airflow / current / rotation claim, and the
*Blower Output Verification* diagnostic states this limit on-device.

## Customer entities

| Entity | Platform | Default | Purpose |
|---|---|---|---|
| Blower | `fan` (binary) | enabled | The single on/off blower control (no speed). |
| Blower Mode | `select` | enabled (config) | Manual / Auto. |
| Blower Auto Trigger | `select` | enabled (config) | Ventilate now / Ventilate soon. |
| Blower Control Status | `text_sensor` | diagnostic, disabled | What the blower is doing and why (incl. honest downgrade / fail-safe). |
| Blower Air-Quality Demand | `text_sensor` | diagnostic, disabled | The AirIQ demand the blower is reading. |
| Blower Output Verification | `text_sensor` | diagnostic, disabled | On-device statement of the one-way, no-feedback limit. |

## Behaviour engine

The behaviour logic lives in the header-only engine
[`include/sense360/blower_controller.h`](../../include/sense360/blower_controller.h)
— the **same** implementation compiled into production firmware (via
`esphome: includes:` in
[`packages/features/blower_framework.yaml`](../../packages/features/blower_framework.yaml))
and exercised by the deterministic native simulation tests
([`tests/unit/test_blower_controller.cpp`](../../tests/unit/test_blower_controller.cpp)
and
[`tests/unit/test_blower_airiq_coexist.cpp`](../../tests/unit/test_blower_airiq_coexist.cpp)),
so tested logic and shipped logic cannot drift. The contract is pinned by
[`tests/test_blower_framework.py`](../../tests/test_blower_framework.py).

The engine owns:

* **Mode arbitration** — Auto requires the AirIQ demand contract; without it the
  engine honestly downgrades to Manual (the engine, not the YAML, is the single
  source of that fallback).
* **Demand mapping** — the one interpretation of the canonical AirIQ
  recommendation as a ventilation `Demand`.
* **Fail-safe** — an `UNKNOWN` demand never starts the blower.
* **Anti-short-cycle** — minimum on-time / off-time dwell windows.

## Optional input — AirIQ is not required (the canonical demand contract)

The canonical AirIQ air-quality service (AIRIQ-FRAMEWORK-001) is the blower's
demand producer, but it is **not** a hard dependency. One compile-time flag
declares whether it is composed:

* `blower_has_airiq` — is the AirIQ framework composed? Default `"false"`.

The framework reads the demand through the **shared header-only engine
singleton** `sense360::airiq::global_engine().recommendation()` — never a hard
`id()` to an AirIQ entity, and it never duplicates pollutant thresholds (the
AirIQ engine owns pollutant truth). The AirIQ engine header is compiled by this
framework unconditionally (idempotent under `#pragma once`), so the demand read
compiles with or without the AirIQ framework; when AirIQ is absent the singleton
is simply unfed and its recommendation stays *Sensor initialising* →
`DEMAND_UNKNOWN`.

### Demand mapping

The AirIQ `Recommendation` (a stable enum, single-sourced in
[`include/sense360/airiq_engine.h`](../../include/sense360/airiq_engine.h)) maps
to a blower `Demand`:

| AirIQ recommendation | Blower demand | Auto (Trigger = now) | Auto (Trigger = soon) |
|---|---|---|---|
| Sensor initialising | Unknown | off (fail-safe) | off (fail-safe) |
| No action needed | None | off | off |
| Ventilate soon | Ventilate soon | off | **on** |
| Ventilate now | Ventilate now | **on** | **on** |
| Check pollution source | None | off | off |
| Unavailable | Unknown | off (fail-safe) | off (fail-safe) |

*Check pollution source* is deliberately **not** a ventilation demand: outdoor
air quality is unknown, so the AirIQ contract does not recommend ventilation for
it, and neither does the blower. The integer contract this mapping relies on is
pinned against the AirIQ enum by `test_blower_airiq_coexist.cpp`.

### Fallback rules and fail-safe semantics

| Composition | Blower Mode = Auto |
|---|---|
| No AirIQ (`blower_has_airiq: "false"`) | honestly downgraded to Manual; *Blower Control Status* says so |
| AirIQ present, demand Unknown / Initialising / Unavailable | blower **off** — missing air-quality data never ventilates |
| AirIQ present, demand at/above the trigger | blower on (subject to anti-short-cycle) |

Manual mode, the Blower Mode select and the Blower Auto Trigger work in **every**
composition. In Manual (or Auto downgraded to Manual) the customer's Blower
control is authoritative and is never overridden.

## Anti-short-cycle

Provisional engineering defaults (pending the bench checklist), substitution-
tunable: `blower_min_on_ms` (60 s) and `blower_min_off_ms` (60 s). Minimum run
time protects the blower motor once started; minimum off time prevents a rapid
restart. Neither delays the first-ever start (there is no prior run to
short-cycle against at boot).

## Remote consumption

A Home Assistant ESPHome user pulls
[`packages/remote/blower-framework.yaml`](../../packages/remote/blower-framework.yaml)
through a git package; the shared engines
(`include/sense360/blower_controller.h` and `airiq_engine.h`) are delivered via
the `sense360` external component (registered in
[`include/sense360/__init__.py`](../../include/sense360/__init__.py)), with no
`/config/include` setup and no `type: local` package. See
[`docs/remote-package-consumption.md`](../remote-package-consumption.md).

## Gate posture and honesty limits

* The blower is a fan output. The *Fans are never stable* standing gate applies
  unchanged: this framework ships **compile-only** — no
  [`config/webflash-builds.json`](../../config/webflash-builds.json) row, no
  artifact, never stable / preview / customer-default / buyable / kit-exposed /
  in `release_one_required_configs`. Release-One (`Ceiling-POE-VentIQ-RoomIQ`)
  is unchanged.
* The representative device is the compile-only validation fixture
  [`products/sense360-core-ceiling-airiq-blower.yaml`](../../products/sense360-core-ceiling-airiq-blower.yaml)
  (config string `Ceiling-Core-AirIQ-Blower`), cataloged
  `status: compile-only`, `webflash_build_matrix: false`, and registered in
  [`config/compile-only-targets.json`](../../config/compile-only-targets.json).
* Compile / config / simulation success is **firmware-build proof of
  buildability only** — never hardware, bench, airflow, electrical-safety,
  thermal, compliance or commercial proof.
* Provisional timing values are software-defined engineering defaults pending
  bench validation
  ([`docs/hardware/blower-framework-bench-checklist.md`](../hardware/blower-framework-bench-checklist.md)).

## Limitations and hardware verification still required

* No physical blower has been driven; no airflow, current draw, motor
  compatibility, thermal envelope or acoustic behaviour is verified.
* The J13 pinout and the `IO21 → Q4 → J13` net are schematic-backed
  (`S360-100-R4`); silkscreen / bench confirmation of the connector and the
  blower load is bench work.
* The anti-short-cycle windows are placeholders pending a real blower load.

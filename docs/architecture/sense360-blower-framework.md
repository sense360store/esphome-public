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

The Core's on-board blower is an **enclosure air-circulation fan** (owner
decision, 2026-07-31): it moves room air through the Sense360 enclosure so the
on-board sensors sample representative air. It is **not** a room-ventilation
output and no room-air-change effect is claimed. One polished, simple customer
experience — the customer never needs to know about GPIOs, MOSFETs or the
AirIQ engine:

* **Circulation Fan Mode** — the single **authoritative** control: *Off* /
  *Auto* / *On*, default **Auto** (the fan circulates automatically out of the
  box). *Off* always commands the fan off; *On* always commands it on; *Auto*
  runs a periodic duty-cycle circulation, boosted to continuous while the
  canonical AirIQ demand is at/above the boost trigger. The mode is persisted
  across restart.
* **Circulation Boost Trigger** — *Ventilate now* / *Ventilate soon*: the AirIQ
  demand level at which Auto boosts to continuous circulation (conservative
  default: only *Ventilate now*).
* **Circulation Fan** — a **read-only** commanded-state representation
  (on/off). There is deliberately **no** customer on/off toggle and **no**
  speed control: because the mode is the only control, nothing can transiently
  contradict the selected mode (no "toggle that Auto silently reverses").
  Interface choice **A** — the mode select is authoritative; the `Circulation
  Fan` binary sensor is the read-only commanded state ESPHome permits.

## Hardware contract (verified S360-100-R4)

Source of truth: [`docs/hardware/s360-100-r4-core.md`](../hardware/s360-100-r4-core.md)
and the owner-provided `S360-100-R4` schematic. This framework encodes no more
than the contract proves.

| Fact | Value |
|---|---|
| Fan drive net | Core `FAN` net — schematic `IO21` (ESP32-S3 `GPIO21`) |
| Switching element | `Q4` `SI2302S` low-side MOSFET |
| Connector | `J13`, a two-wire binary 5 V blower output (pins: +5V, FAN, GND) |
| Feedback | **None** — no tach, speed-PWM, current, airflow or physical-rotation feedback exists on J13 |
| `GPIO46` | `GP_Fan_Status_Led`, a Core-side status indicator — **never** rotation feedback; the framework never touches it |
| `GPIO3` | the generic Relay net (J4), a **separate** control owned by the Core board (`main_relay`) — the framework never drives it |

Because the FAN net is a one-way binary drive, the firmware commands only
`on`/`off` and can never verify the fan physically spun. The framework
therefore makes **no** speed / airflow / current / rotation claim, and the
*Circulation Fan Output Verification* diagnostic states this limit on-device.

## Customer entities

| Entity | Platform | Default | Purpose |
|---|---|---|---|
| Circulation Fan Mode | `select` | enabled (config), default **Auto**, persisted | The authoritative control: Off / Auto / On. |
| Circulation Boost Trigger | `select` | enabled (config) | Ventilate now / Ventilate soon. |
| Circulation Fan | `binary_sensor` (read-only) | enabled | The commanded fan state (on/off) — not a toggle. |
| Circulation Fan Boost | `binary_sensor` | diagnostic, disabled | Distinct air-quality boost indication. |
| Circulation Fan Status | `text_sensor` | diagnostic, disabled | What the fan is doing and why (run / rest / boost). |
| Circulation Fan Air-Quality Demand | `text_sensor` | diagnostic, disabled | The AirIQ demand the boost is reading. |
| Circulation Fan Output Verification | `text_sensor` | diagnostic, disabled | On-device statement of the one-way, no-feedback limit. |

Boot safety: the FAN-net GPIO output boots **off**; the persisted mode is
restored during setup and applied by the late (`priority: -100`) `on_boot`
evaluation, so the output is safely off until the restored mode is evaluated.

## Behaviour engine

The behaviour logic lives in the header-only engine
[`components/sense360/blower_controller.h`](../../components/sense360/blower_controller.h)
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

* **Mode arbitration** — Off / Auto / On. Off and On command the output
  directly; Auto runs the duty cycle + boost. The engine owns the output in
  every mode, so a customer toggle can never contradict the selected mode.
* **Demand mapping** — the one interpretation of the canonical AirIQ
  recommendation as a `Demand`.
* **Fail-safe** — an `UNKNOWN` demand (AirIQ initialising / unavailable / not
  composed) never boosts the fan; missing air-quality data never changes the
  fan's behaviour.
* **Auto duty cycle** — run / rest windows plus the air-quality boost (see
  below).

## Optional input — AirIQ is not required (the canonical demand contract)

The canonical AirIQ air-quality service (AIRIQ-FRAMEWORK-001) is the boost's
demand producer, but it is **not** a hard dependency. The base duty cycle is
deliberately **independent** of AirIQ — circulation is an enclosure-sampling
function, not a response to air quality — so Auto circulates with or without
AirIQ composed. One compile-time flag declares whether AirIQ is composed:

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
[`components/sense360/airiq_engine.h`](../../components/sense360/airiq_engine.h)) maps
to a `Demand`; a demand at/above the boost trigger switches Auto from the duty
cycle to continuous circulation:

| AirIQ recommendation | Demand | Boost (Trigger = now) | Boost (Trigger = soon) |
|---|---|---|---|
| Sensor initialising | Unknown | no (fail-safe) | no (fail-safe) |
| No action needed | None | no | no |
| Ventilate soon | Ventilate soon | no | **yes** |
| Ventilate now | Ventilate now | **yes** | **yes** |
| Check pollution source | None | no | no |
| Unavailable | Unknown | no (fail-safe) | no (fail-safe) |

*Check pollution source* is deliberately **not** a boost demand: outdoor air
quality is unknown, so the AirIQ contract does not recommend ventilation for
it, and the fan does not boost for it either. The integer contract this mapping
relies on is pinned against the AirIQ enum by `test_blower_airiq_coexist.cpp`.

### Fallback rules and fail-safe semantics

| Composition | Circulation Fan Mode = Auto |
|---|---|
| No AirIQ (`blower_has_airiq: "false"`) | the base duty cycle runs; no boost is ever possible |
| AirIQ present, demand Unknown / Initialising / Unavailable | the base duty cycle runs unchanged — a boost never starts on missing data, and a boost already running ends (rest, then resume the cycle) rather than running forever on stale data |
| AirIQ present, demand at/above the boost trigger | continuous circulation (boost) |

`Off` and `On` always command the output directly, in every composition. `Auto`
is the default. The mode is the single control, so there is no separate toggle
that can transiently contradict it.

## Auto duty cycle

Provisional engineering defaults (pending the bench checklist), substitution-
tunable: `blower_circulate_on_ms` (60 s run) and `blower_circulate_off_ms`
(240 s rest — a 20% duty cycle). In Auto:

1. Entering Auto (boot restore or a mode change) starts a circulation run
   immediately, then the cycle repeats: on for `blower_circulate_on_ms`, off
   for `blower_circulate_off_ms`.
2. **Boost**: while a real AirIQ demand is at/above the boost trigger the fan
   runs continuously so sampling stays fresh while air quality is changing.
3. When the boost ends (demand cleared **or** data gone stale/unavailable) the
   cycle resumes with a **full rest period** — the fan has just been running.

Fail-safe: an `UNKNOWN` demand never boosts; the base cycle is unaffected by
AirIQ state in every case. All transitions use rollover-safe unsigned timing.
These rules are pinned by the deterministic C++ suite
(`tests/unit/test_blower_controller.cpp`): cycle repetition, boost entry from
run and rest phases, trigger levels, UNKNOWN handling, boost wind-down,
mode-change reseeding, and millis rollover.

## Remote consumption

The supported remote-consumer entrypoint is
[`packages/remote/ceiling-blower.yaml`](../../packages/remote/ceiling-blower.yaml)
(REMOTE-PACKAGE-HEADER-RESOLUTION-001 pattern, alongside `ceiling-airiq` /
`ceiling-roomiq-presence` / `led-framework`). Do **not** pull
`packages/features/blower_framework.yaml` directly through a git package: its
repository-local `esphome: includes:` paths
(`../components/sense360/*.h`) resolve against the *consumer's* config
directory and fail with
`Could not find file '/config/.../components/sense360/blower_controller.h'`.
The wrapper composes the framework unchanged and instead delivers
`blower_controller.h` + `airiq_engine.h` through the `sense360` external
component ([`components/sense360/__init__.py`](../../components/sense360/__init__.py)),
so no header is ever copied into the consumer's `/config`.

A Home Assistant ESPHome device adds the blower like this (pin `ref` and
`sense360_remote_ref` to the same release tag for reproducible builds):

```yaml
substitutions:
  blower_has_airiq: "true"   # only when ceiling-airiq is composed too

packages:
  core:
    url: "https://github.com/sense360store/esphome-public"
    ref: "main"
    files:
      - "packages/boards/s360-100-core-ceiling.yaml"
    refresh: 0s
  airiq:                     # optional — enables the Auto demand input
    url: "https://github.com/sense360store/esphome-public"
    ref: "main"
    files:
      - "packages/remote/ceiling-airiq.yaml"
    refresh: 0s
  blower:
    url: "https://github.com/sense360store/esphome-public"
    ref: "main"
    files:
      - "packages/remote/ceiling-blower.yaml"
    refresh: 0s
```

Without the `airiq` package, leave `blower_has_airiq` at its `"false"`
default: Auto then has no actionable demand and the blower stays off
(fail-safe). The regression suite
([`tests/test_remote_package_consumer.py`](../../tests/test_remote_package_consumer.py))
validates both compositions from an isolated consumer directory through
ESPHome's git-package mechanism, and pins that the delivered
`blower_controller.h` is byte-identical to the canonical tested source.

History: the former `packages/remote/blower-framework.yaml` was deleted under
the owner decision of 2026-07-28 (SENSE360-CANONICALISATION-001 PR 07) as the
unpublished remainder of `packages/remote/`; that legacy path stays deleted
(`tests/test_blower_framework.py`), and `ceiling-blower.yaml` is its
convention-named published successor.

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

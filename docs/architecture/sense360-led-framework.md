# Sense360 LED framework (LED-FRAMEWORK-001)

**Type:** Firmware module framework. This document describes the
customer-focused LED experience for the Sense360 LED board (S360-300,
12-LED WS2812B halo ring). It changes no product lifecycle, commercial
state, release declaration, WebFlash surface, Shopify state, or SOT
programme state, and it claims **no hardware, bench, compliance or safety
proof** — firmware-build and logic/simulation proof only (standing
invariant: *no false proof*,
[`docs/standing-invariants.md`](../standing-invariants.md)). WS2812B colour
order, emitted light, perceived brightness, thermal and power behaviour
remain unverified until the operator executes the bench checklist
([`docs/hardware/led-framework-bench-checklist.md`](../hardware/led-framework-bench-checklist.md)).

Contract sources: this doc describes; the contract is enforced by
[`tests/test_led_framework.py`](../../tests/test_led_framework.py) and
[`tests/unit/test_led_controller.cpp`](../../tests/unit/test_led_controller.cpp).
Implementation:
[`include/sense360/led_controller.h`](../../include/sense360/led_controller.h)
(controller engine, single implementation),
[`packages/features/led_framework.yaml`](../../packages/features/led_framework.yaml)
(customer/behaviour layer) and
[`packages/boards/s360-300-led.yaml`](../../packages/boards/s360-300-led.yaml)
(hardware driver adapter + Room Light entity).

## Purpose

The S360-300 halo ring should give customers **useful room lighting, a
predictable night light and discreet device feedback** — not a decorative
effects showcase. The customer never needs to know about LED channels,
GPIOs, RMT drivers or internal effects. Priorities, in order: useful
light; predictable night behaviour; unobtrusive status indication; simple
customer controls; safe recovery and diagnostics.

## Hardware driver authority

| Fact | Value | Evidence |
|---|---|---|
| LED type | WS2812B addressable RGB, 12 LEDs (ceiling standard) | `packages/boards/s360-300-led.yaml`; count is firmware-asserted, **not silkscreen-verified** (open question, `docs/hardware/s360-300-r4-led.md`) |
| Data path | Core IO38 = LED_DATA → 74LVC1G07 buffer + 330 Ω → Core J3 → S360-300 J1 | HW-010; verified S360-100-R4 / S360-300-R4 schematics |
| Colour order | GRB (firmware binding) | pre-existing binding; physical verification pending (bench checklist) |
| Colour model | RGB only — **no white/CCT channel exists**, so no colour-temperature control is exposed | WS2812B datasheet-level fact; unsupported controls are never fabricated |
| Supply rail | **Unresolved**: Core J3 pin 1 captured `+3.3V` vs LED J1 pin 2 labelled `+5V` | open schematic question, `S360-300-BENCH-001` — bench work, does not change firmware behaviour |
| Electrical/thermal ceiling | **None recorded anywhere in this repository** | the full-load thermal bench template was retired unexecuted |

The framework changes **no hardware binding**. The PCA9685 halo
(`packages/features/ceiling_halo_leds.yaml`) is different hardware on the
shared I²C bus and is not part of this framework; the Core's single
fan-status LED (GPIO46) is likewise a separate device.

## Customer entities (enabled by default)

The default-enabled surface is exactly this set (stable IDs; no
`${friendly_name}` prefix per the Core-Framework naming rules):

| Entity ID | Name | Type | Meaning |
|---|---|---|---|
| `led_ring` | Room Light | light (brightness + RGB) | The single customer light (LED-01). No per-channel entities; no colour-temperature control (no CCT hardware). |
| `s360_led_night_mode` | Night Mode | switch | Applies the provisional low/warm night profile; turning it off restores the previous customer state (LED-02). |
| `s360_led_night_behaviour` | Night Mode Behaviour | select (config) | Manual (default) / When dark / When dark and occupied (LED-03). |
| `s360_led_status_indicator` | Status Indicator | select (config) | Off / Essential (default) / Detailed (LED-06). |
| `s360_led_identify` | Identify Device | button | Short, recognisable, non-disruptive pulse; restores the previous state (LED-08). |
| `s360_led_darkness_threshold` | Darkness Threshold | number (config) | 1–200 lx, default 20 lx, with hysteresis (LED-05). |

There is deliberately **no customer "Maximum Brightness" control**
(LED-09): no verified hardware ceiling exists, so such a control would
imply a safety contract the firmware cannot honour. The software cap is
the documented `led_max_brightness_pct` substitution (below).

**"Scheduled" Night Mode Behaviour is deferred** (LED-03): the base
packages provide only SNTP (internet NTP) and Home Assistant time sources
— neither is a reliable local-first scheduler, so a Scheduled option would
add cloud/network dependence to core device behaviour. It can be added
later if a genuinely reliable local time source lands.

## State ownership

The engine tracks who caused each light change, so automation only ever
reverses its own actions:

* **Customer/manual control** — detected by comparing the light's current
  target against the engine's last arbitrated output on every evaluation
  tick: a difference the engine did not command is customer intent.
  Customer intent always wins: it cancels transient overlays, disengages
  Night Mode, and (for an automation-owned Night Mode) suppresses
  re-activation until the trigger condition resets.
* **Night Mode automation** — activations are marked automation-owned
  (`night_automation_owned`); only automation-owned activations are
  reversed by occupancy-clear or brightness. A manually enabled Night Mode
  is never reversed by the automation.
* **Transient overlays (Identify, Status)** — never own state: they render
  above the stack and the previous output returns when they complete. They
  are RAM-only and never persisted.
* **Fault** — persistent overlay reserved for an explicit fault signal; it
  never destroys the stored customer state.

Ownership state (`night_on` / `night_automation_owned`) persists across
restart so a reboot cannot convert an automation-owned night light into a
customer-owned one.

## Night Mode (LED-02)

* Provisional profile: **5% brightness**, warm red-dominant RGB mix
  (`1.0 / 0.58 / 0.16`) — avoids blue-heavy light. **Both values are
  software definitions pending bench validation**; perceived warmth and
  the minimum visible brightness through the diffuser are bench work.
* Enabling Night Mode stores nothing destructive: the customer's previous
  state (including an active approved effect) is preserved and restored
  when Night Mode turns off — including a previous *off* state.
* Manual light changes while Night Mode is active win cleanly: Night Mode
  disengages and the light follows the customer.
* The night profile obeys the software brightness cap and runs without
  effects.

## Night Mode Behaviour — automation (LED-03/04/05)

* **Manual** (default): no automation; occupancy and lux are ignored.
* **When dark**: Night Mode turns on when the room is dark and off (if
  automation-owned) when it is bright. Hysteresis prevents flapping.
* **When dark and occupied**: requires darkness AND fused occupancy.
  Occupancy-clear starts a provisional 60 s auto-off delay; a fresh
  occupancy event cancels the pending off. (The fused Occupancy entity
  already carries the Presence clear delay; this window only smooths the
  night light.)

Presence integration rules (LED-04):

* The input is the merged **Occupancy** contract from
  PRESENCE-FRAMEWORK-001 — never raw PIR / radar / SEN0609 states
  (test-enforced).
* Validity comes from the Presence module runtime status: anything other
  than Available/Degraded marks occupancy **invalid**, which freezes the
  automation — no flashing, no repeated toggles, no auto-off from unknown
  data.
* Automation may switch **only Night Mode**, never the normal Room Light
  output, and it never activates while the customer's Room Light is on
  (an in-use light is never dimmed by automation).
* There is no feedback loop: the light state feeds nothing back into
  Presence.

Darkness decision (LED-05):

* Source (ROOMIQ-FRAMEWORK-001): the **canonical RoomIQ darkness
  service** (`include/sense360/roomiq_engine.h`) — computed from the
  CALIBRATED illuminance path over the compiled lux driver
  (`comfort_ceiling_illuminance`, VEML7700 at I²C 0x10, publishing every
  10 s), with freshness from real update callbacks. The LED framework
  passes the customer threshold into that service and consumes the
  decision (`input_darkness`); it no longer implements any lux threshold
  logic of its own (regression-tested), and the customer's Illuminance
  Calibration therefore also corrects night-mode behaviour.
* Dark below the customer threshold (default **20 lx**, range 1–200 lx);
  not-dark above threshold × 1.5 (hysteresis factor, provisional). In
  between, the previous decision holds.
* Missing, NaN or stale (> 60 s) lux is **Unknown** — deliberately
  distinct from darkness. Unknown never activates Night Mode and never
  toggles an active one; the automation holds and fails safe.

**Known documentation-vs-firmware mismatch (reported, unresolved):** the
hardware catalog documents the S360-200 RoomIQ light sensor as
**LTR-303ALS**, while the compiled firmware drives a **VEML7700** at 0x10.
If the physical board actually carries an LTR-303ALS, the lux path will
never produce data and darkness automation will honestly report Unknown
and stay inactive (fail-safe). Resolving the sensor identity is bench/
catalog work and is on the checklist; this framework neither hides nor
papers over the conflict.

## Status indication (LED-06)

Status feedback is short, discreet and subordinate to the Room Light.
Every indication maps to a **real supported firmware signal** — nothing is
claimed without one:

| Event | Real signal | Level |
|---|---|---|
| Startup | `on_boot` completion | Essential |
| Connected | API client connected (Home Assistant) | Essential |
| Warning (recoverable) | API client disconnected | Essential |
| Network info | WiFi connected | Detailed |
| Network warning | WiFi lost | Detailed |

* **Off** silences all status indications (Identify still works — it is
  owner-requested, not a status).
* Indications are single brief blips (provisional 1.5 s); there are **no
  constant animated status effects** during normal operation.
* A persistent fault indication exists in the engine (steady dim red) but
  **no producer is wired**: no composed component exposes a supported LED
  fault signal today, so production YAML never sets it. It is a tested
  contract reserved for a future real signal — statuses that lack real
  signals are not claimed.
* AirIQ / VentIQ / installer-feedback indications are future extensions of
  the same event vocabulary (foundations, not shipped claims).

## Status priority (LED-07)

Highest first — implemented in the engine, tested deterministically:

1. **Fault** (explicit fault/recovery state; persistent)
2. **Identify** (temporary owner-requested action)
3. **Night Mode**
4. **Room Light** (customer state)
5. **Transient status** (informational blips)

Consequences (all test-pinned): a transient status never interrupts an ON
Room Light or an active Night Mode; Identify temporarily overrides Night
Mode and returns to it; Fault overrides everything and persists; every
transient restores the exact prior state; repeated events never leave the
ring stuck; an error never destroys the customer's chosen colour or
brightness.

## Identify (LED-08)

A gentle 4 s soft-white pulse cycling 10–40% brightness (clamped to the
software cap) — recognisable but non-disruptive, local-only, and it
restores the previous state automatically. Useful for installers and
multi-device homes.

## Brightness protection (LED-09)

**No verified electrical/thermal ceiling exists for the S360-300 anywhere
in this repository** (the full-load thermal bench template was retired
unexecuted). Accordingly:

* The framework does **not** claim hardware-level safety for any
  brightness value.
* The pre-existing 100% software limit is preserved as the explicit,
  documented, **provisional** substitution `led_max_brightness_pct`
  (board package). A lower cap was considered and rejected because no
  evidence justifies any particular number — inventing "50% is safe"
  would be exactly the kind of unsupported electrical conclusion this
  repository forbids.
* The engine clamps **every** layer to the cap: customer light, night
  profile, identify, status, fault, and the "Gentle Pulse" effect's
  `max_brightness` binds to the same substitution.
* Maximum safe brightness, thermal behaviour and power draw are bench
  checklist items — **physical validation pending**.

## Effects (LED-10)

Customer-visible effects are exactly: **None** (native), **Gentle Pulse**
(slow 3 s pulse, 20% to cap) and **Night Glow** (very slow 6 s pulse,
3–10%). The pre-framework Alert/strobe, Rainbow, Random, Scan and Color
Wipe effects were removed — no strobe, rapid flashing or novelty patterns
ship by default (accessibility decision). Effects obey the brightness cap;
Night Mode and overlays run without effects and restore the customer's
effect afterwards.

## Restart and restore contract (LED-11)

* The framework persists **only** the stable customer state
  (`on/brightness/RGB/effect`) and Night Mode ownership in
  `restore_value` globals, written from the engine's customer state —
  transient overlays are RAM-only and can never survive a reboot.
* The Room Light itself boots `ALWAYS_OFF`; the late `on_boot` hook
  (priority −100) re-applies the engine-arbitrated state from the
  persisted globals. This means an identify/status pulse interrupted by a
  power cut can never flash back at boot, and no ESPHome flash-restore
  race exists.
* Invalid stored values are sanitised (NaN brightness → 50%, colours
  clamped into range) — **never an unexpected full-brightness boot**.
* **Safe mode**: ESPHome safe-mode boots run a minimal config without this
  package, so the ring stays dark — the preferred low-risk behaviour after
  a fault recovery.
* Compositions that use the board package without the framework (legacy
  include paths) get a plain light that boots off.

## Bundle membership (bundle authority)

Six layers are never conflated: board capability ≠ connector availability
≠ compiled firmware ≠ physically fitted LED ≠ commercial bundle ≠ runtime
operation. What this repository can decide is the **compiled firmware**
layer:

* Exactly **two** catalog-declared LED-bearing configs exist
  (`config/core-framework.json` / `config/product-catalog.json`):
  `Ceiling-POE-VentIQ-RoomIQ-LED` and `Ceiling-POE-RoomIQ-LED` — both
  **preview** channel. Only their bundles compose the LED board package
  and this framework (test-enforced); no non-LED bundle gains any LED
  package, and the framework is never added merely because the Core could
  drive a ring.
* SOT (`products.yaml`) lists the S360-300 module itself as a production
  product, but **no SOT bundle carries LED** and both firmware configs
  remain preview with the LED preview-to-stable gauntlet as the stable
  blocker. This PR changes no SOT, WebFlash, release or commercial state;
  the SOT module-status/firmware-channel reconciliation stays owner work.
* Compile-time capability (`s360_module_led: "Included"`) remains distinct
  from runtime status (below) and from physical fitment (bench).

## Optional RoomIQ / Presence inputs (LED-FRAMEWORK-002)

RoomIQ (the darkness decision) and Presence (fused occupancy) are **optional
inputs**, not hard dependencies. The full customer LED experience — Room
Light, **Manual** Night Mode, the warm low-brightness night profile, saved
Room Light / Night Mode state, Identify Device, Status Indicator, the
startup / API / Wi-Fi status overlays, priority arbitration, transient
overlay restoration, the approved *Gentle Pulse* / *Night Glow* effects, the
LED Output Verification diagnostic and local operation without Home Assistant
— works with **neither** input composed.

How it stays compile-safe with an input absent:

* The framework reads each input from the **shared, header-only engine
  singleton** the owning framework feeds when composed — the canonical RoomIQ
  darkness engine (`sense360::roomiq::global_engine()`,
  `include/sense360/roomiq_engine.h`) and the canonical Presence fusion
  engine (`sense360::presence::global_engine()`,
  `include/sense360/presence_fusion.h`). It reads their **outputs**; it never
  re-implements lux thresholding or sensor fusion, and it never holds a hard
  ESPHome `id(...)` reference to a RoomIQ / Presence *entity* (which would be
  an undefined-id compile error when that package is absent). Including those
  two headers (idempotent under `#pragma once`) is what lets the behaviour
  compile with or without the frameworks.
* When a framework is **not** composed, nothing feeds its singleton, so
  darkness stays `UNKNOWN` and Presence health stays `Initialising` (invalid).
  Fail-safe holds: missing/stale lux is never read as dark, and missing
  occupancy is never read as occupied. No fake lux or occupancy entity is
  invented.

**Capability declaration.** Each composing bundle / remote wrapper sets two
compile-time substitutions truthfully (safe default `"false"`; they double as
C++ bool literals):

| Substitution | Meaning |
|---|---|
| `led_has_roomiq` | the canonical RoomIQ darkness engine is composed |
| `led_has_presence` | the fused Presence occupancy contract is composed |

**Night Mode Behaviour by composition.** ESPHome cannot conditionally
generate a select's option list, so the full list is always offered and an
unsupported pick is **refused at runtime**: it snaps visibly back to
**Manual** and the reason is published to the diagnostic **LED Capability
Notice**. The unsupported mode is never left selected and never reported
active (the evaluate loop also caps the effective behaviour to Manual, so a
restored value cannot drive automation either).

| Composition | Supported Night Mode Behaviour options |
|---|---|
| LED only (no RoomIQ, no Presence) | Manual |
| LED + RoomIQ (no Presence) | Manual, When dark |
| LED + Presence (no RoomIQ) | Manual *(Presence alone never activates Night Mode)* |
| LED + RoomIQ + Presence | Manual, When dark, When dark and occupied |

**Representative target.** `Ceiling-Core-LED-AirIQ` (Core + AirIQ + LED, **no
RoomIQ, no Presence**; `led_has_roomiq: "false"`, `led_has_presence:
"false"`) is the compile fixture for this model — the top-level entry point
`products/sense360-ceiling-core-led-airiq.yaml` over the skeleton
`products/compile-only/ceiling-core-led-airiq.yaml`, registered in the
compile-only lane. It changes no release, channel or commercial state; LED
stays preview-gated.

**Remote consumption.** `packages/remote/ceiling-led.yaml` delivers the whole
feature through a git package (both engine headers arrive via the `sense360`
external component; no `type: local` source, no `/config/include` setup),
defaulting `led_has_roomiq` / `led_has_presence` to `"false"` — see
[Remote package consumption](../remote-package-consumption.md).

## Module status and diagnostics — honesty limits

The WS2812B data line is **one-way**: the firmware can never verify that
light was actually emitted, and no driver communication status exists
(the ring is not an I²C device). Therefore:

* The Core-Framework "LED Module Status" entity keeps the **compile-time**
  vocabulary (`Included`) — the reserved runtime values (Initialising /
  Available / Degraded / Unavailable / Fault) are **not** wired, because
  no real supported signal exists to back them
  (`config/core-framework.json` guardrails; a compiled package is never
  hardware availability).
* The diagnostic **LED Output Verification** entity states the limit
  on-device: *"WS2812B data line is one-way; firmware cannot verify
  emitted light."*
* Device Health is untouched: a customer turning the light off is a light
  state, never a health state.

Diagnostic entities (all `diagnostic`, disabled by default):

| Entity ID | Name | Meaning |
|---|---|---|
| `s360_led_active_layer` | LED Active Layer | Which priority layer owns the ring (Fault / Identify / Night Mode / Room Light / Status) |
| `s360_led_last_status_event` | LED Last Status Event | Last engine status event, with "(suppressed)" when priority/level kept it off the ring |
| `s360_led_darkness_state` | LED Darkness State | Raw darkness decision: Dark / Not dark / Unknown |
| `s360_led_output_verification` | LED Output Verification | The one-way output limitation statement |
| `s360_led_optional_inputs` | LED Optional Inputs | Which optional inputs were composed (RoomIQ darkness / Presence occupancy) — LED-FRAMEWORK-002 |
| `s360_led_capability_notice` | LED Capability Notice | Last Night Mode Behaviour capability decision (refused → Manual, or accepted) — LED-FRAMEWORK-002 |
| (board) LED Ring SKU | — | existing SKU identity sensor |

Raw channels, driver frequency, internal automation ownership flags,
thermal/current assumptions and transition-debug state are **not** exposed
as entities at all — the engine keeps them internal; the four diagnostics
above are the complete debugging surface.

## Compatibility impact

LED-bearing firmware has only ever shipped on the **preview** channel
(acknowledgement-gated; no stability promise). The framework replaces the
pre-framework board-level surface:

* `"${friendly_name} LED Ring"` light → **Room Light** (same `led_ring`
  internal ID; the Home Assistant object ID changes with the name).
* `"${friendly_name} LED Brightness"` number and
  `"${friendly_name} Night Mode"` switch → removed, replaced by the Room
  Light's native brightness and the framework's **Night Mode** switch.
  (Keeping both surfaces would have shipped two conflicting night-mode
  controls.)
* Effect list reduced to the approved set.

Legacy include paths (`packages/hardware/led_ring_ceiling.yaml`, the
legacy `products/sense360-core-ceiling*.yaml` compositions) keep
resolving; customers pinning a release tag see no change until they move
tags. The voice variant (`s360-300-led-mic-ceiling.yaml`) is
self-contained and unchanged.

## Provisional defaults (single list)

All of these are software-defined engineering defaults, **pending bench
validation**, and none is customer-tested: night profile (5%, warm mix),
darkness threshold default (20 lx) and hysteresis factor (1.5), lux stale
window (60 s), auto-off delay (60 s), identify pattern/duration (4 s,
10–40%), status blip duration (1.5 s) and colours, software brightness cap
(100%), effect parameters.

## Test expectations

* [`tests/test_led_framework.py`](../../tests/test_led_framework.py) —
  contract tests (entity set, naming, diagnostic policy, effects
  allowlist, bundle authority, module-status honesty, matrix/contract/doc
  sync, CI wiring). Runs in the per-PR "CI: Quick Validation" gate and in
  the compile lane's contract gate.
* [`tests/unit/test_led_controller.cpp`](../../tests/unit/test_led_controller.cpp)
  — the deterministic simulation layer: synthetic timestamped inputs
  through the production controller header; covers customer state, night
  mode, behaviour automation, lux hysteresis and staleness, identify and
  status overlays, priority pre-emption, fault persistence, restart
  restoration and invalid inputs. **Never** hardware validation.
* Representative **compile evidence** comes from the existing hosted lane
  "CI: Core Framework Representative Compile"
  (`.github/workflows/core-framework-compile.yml`), whose matrix now
  covers both LED-bearing bundles (`Ceiling-POE-VentIQ-RoomIQ-LED`,
  `Ceiling-POE-RoomIQ-LED` — each a Presence + LED composition) alongside
  the LED-less targets that double as the not-accidentally-included
  regression check (Release-One among them). Zero-artifact /
  no-publication / read-only guarantees unchanged. A green run is
  firmware-build proof only.

## Limitations and hardware verification still required

* **No hardware validation is claimed anywhere.** Colour order, LED
  count, minimum visible brightness, maximum safe brightness, thermal
  behaviour, power draw, diffuser appearance, flicker and transition
  quality, and the supply-rail question are all bench checklist items
  ([`docs/hardware/led-framework-bench-checklist.md`](../hardware/led-framework-bench-checklist.md);
  results and attestation are operator-only, never machine-written).
* The lux path depends on the unresolved VEML7700-vs-LTR-303ALS sensor
  identity (above); until bench confirmation, darkness automation is
  compile/simulation-proven logic over an unverified sensor.
* Emitted light is unverifiable from firmware (one-way data line); the
  fault layer has no producer until a real signal exists.
* "Scheduled" night behaviour is deferred (no reliable local time source).
* Night profile warmth/comfort, identify visibility and status
  discreetness are perception questions — bench work, not software facts.

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
  (`comfort_ceiling_illuminance`, LTR-303ALS-01 at I²C 0x29 via the built-in
  `ltr_als_ps` platform, publishing every 10 s), with freshness from real
  update callbacks. The LED framework
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

**Lux-sensor identity (driver reconciled, runtime pending):** the S360-200
RoomIQ light sensor is **LTR-303ALS-01** per the schematic/BOM, and
`S360-200-R4-HARDWARE-RECONCILIATION-001` corrected the compiled firmware to
drive that exact part at its fixed I²C address **0x29** via the built-in
`ltr_als_ps` platform (the earlier **VEML7700** @ 0x10 driver drift is removed).
On-hardware response is still pending bench: the board under test does not yet
list 0x29 on its I²C scan. Until the sensor answers on the bus the lux path
produces no data and darkness automation honestly reports Unknown and stays
inactive (fail-safe); this framework neither hides nor papers over that
remaining runtime gap.

## Optional inputs — RoomIQ and Presence are not required (LED-FRAMEWORK-002)

RoomIQ (darkness) and Presence (occupancy) are **optional** inputs, not hard
dependencies. The full customer LED framework composes and degrades cleanly
across every supported composition. Two compile-time substitution flags
declare what a composition actually includes:

| Flag | Default | Set `"true"` when… |
|---|---|---|
| `led_has_roomiq` | `"false"` | a RoomIQ framework is composed (enables **When dark**) |
| `led_has_presence` | `"false"` | a Presence framework is composed **and** `packages/features/led_presence_bridge.yaml` is included (enables **When dark and occupied**) |

The flags substitute into the engine as C++ bool literals
(`controller.set_capabilities(${led_has_roomiq}, ${led_has_presence})`), so
**no reference to an absent RoomIQ / Presence id is ever compiled**. The
capability model itself lives in the shared, deterministically-tested engine
(`include/sense360/led_controller.h`), not in YAML.

### Supported composition matrix

| Composition | `led_has_roomiq` / `led_has_presence` | Night Mode Behaviour available | Always available |
|---|---|---|---|
| Core + LED | false / false | Manual | Room Light, Manual Night Mode, Status Indicator, Identify, effects, restore, priority |
| Core + AirIQ + LED | false / false | Manual | (as above) |
| Core + RoomIQ + LED | true / false | Manual, When dark | (as above) |
| Core + Presence + LED | false / true | Manual | (as above) |
| Core + RoomIQ + Presence + LED | true / true | Manual, When dark, When dark and occupied | (as above) — **existing behaviour, unchanged** |

Presence **alone** never enables an automatic mode: without a valid RoomIQ
darkness input there is nothing to trigger on, so a Presence-only device
offers Manual only.

### How the inputs flow

* **Darkness** — the LED framework compiles the canonical RoomIQ engine
  header unconditionally and always consults it. When RoomIQ is not composed
  the engine simply never receives lux, so its darkness decision is
  **Unknown** (never invented). There is still exactly one lux-threshold
  implementation and no duplicate darkness logic.
* **Occupancy** — the LED framework reads occupancy from its own globals
  (`s360_led_occupied` / `s360_led_occupancy_valid`), which default to
  *not occupied / not valid*. The optional `led_presence_bridge.yaml` — the
  **only** place the fused Occupancy entity `s360_occupancy` is referenced by
  the LED feature layer — copies the fused Occupancy contract and its
  validity into those globals. A Presence-less device never references a
  Presence id and never fabricates a placeholder occupancy sensor.

### Fallback rules and fail-safe semantics

The Night Mode Behaviour select always offers the full option list (ESPHome
cannot make an option list conditional without a customer-visible compromise
such as reworking the entity id, which would break restore and Home Assistant
history). Honesty is enforced downstream instead:

* the engine **downgrades** any behaviour whose required framework is absent
  to Manual (`effective_behaviour()`), so the automation never runs off an
  input it does not have;
* the disabled-by-default **LED Night Mode Behaviour** diagnostic states
  which absent framework caused the fallback (e.g. *"When dark needs RoomIQ
  (not composed) — using Manual"*), so an unsupported mode is **never
  silently pretended active** — the LED Active Layer stays *Room Light*;
* **Unknown darkness never means dark** and **invalid occupancy never means
  occupied** — belt-and-suspenders with the capability downgrade.

### How bundles / consumers set the flags

* Repo-local bundles that compose RoomIQ + Presence
  (`Ceiling-POE-VentIQ-RoomIQ-LED`, `Ceiling-POE-RoomIQ-LED`) declare
  `led_has_roomiq: "true"` and `led_has_presence: "true"` at the bundle top
  level and compose `packages/features/led_presence_bridge.yaml`.
* The `Ceiling-Core-LED-AirIQ` compile-only fixture
  (`products/sense360-core-ceiling-led-airiq.yaml`) leaves both `"false"` and
  composes no bridge — the representative AirIQ-only device.
* Remote consumers pull `packages/remote/led-framework.yaml` (see
  [remote-package consumption](../remote-package-consumption.md)); the wrapper
  defaults both flags `"false"`.

No fake darkness and no fake occupancy is ever created; a missing input is a
first-class *unavailable* state, not a fabricated zero.

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
* The lux path uses the reconciled LTR-303ALS-01 @ 0x29 driver (above), but
  the sensor is not yet proven to respond on the board under test; until bench
  confirmation, darkness automation is compile/simulation-proven logic over an
  as-yet unconfirmed sensor.
* Emitted light is unverifiable from firmware (one-way data line); the
  fault layer has no producer until a real signal exists.
* "Scheduled" night behaviour is deferred (no reliable local time source).
* Night profile warmth/comfort, identify visibility and status
  discreetness are perception questions — bench work, not software facts.

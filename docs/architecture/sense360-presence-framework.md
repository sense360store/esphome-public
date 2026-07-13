# Sense360 Presence framework (PRESENCE-FRAMEWORK-001)

**Type:** Firmware module framework. This document describes the tri-sensor
customer Presence experience for the Sense360 RoomIQ board (S360-200). It
changes no product lifecycle, commercial state, release declaration,
WebFlash surface, Shopify state, or SOT programme state, and it claims
**no hardware, bench, compliance or safety proof** — firmware-build and
logic/simulation proof only (standing invariant: *no false proof*,
[`docs/standing-invariants.md`](../standing-invariants.md)). PIR, LD2450 and
SEN0609 physical behaviour remains unverified until the operator executes
the bench checklist
([`docs/hardware/presence-framework-bench-checklist.md`](../hardware/presence-framework-bench-checklist.md)).

Contract sources: this doc describes; the machine-readable wiring lives in
[`config/core-framework.json`](../../config/core-framework.json)
(`module_runtime_status.presence`) and is enforced by
[`tests/test_presence_framework.py`](../../tests/test_presence_framework.py)
and [`tests/unit/test_presence_fusion.cpp`](../../tests/unit/test_presence_fusion.cpp).
Implementation:
[`include/sense360/presence_fusion.h`](../../include/sense360/presence_fusion.h)
(fusion engine, single implementation),
[`packages/features/presence_framework.yaml`](../../packages/features/presence_framework.yaml)
(fusion/customer/health layer) and the three sensor adapters
([`packages/boards/s360-200-roomiq-radar.yaml`](../../packages/boards/s360-200-roomiq-radar.yaml),
[`s360-200-roomiq-pir.yaml`](../../packages/boards/s360-200-roomiq-pir.yaml),
[`s360-200-roomiq-sen0609.yaml`](../../packages/boards/s360-200-roomiq-sen0609.yaml)).

## Purpose

The RoomIQ board carries three presence sensors with complementary
strengths. Customers should experience **one dependable occupancy
capability**, not three unrelated technical sensors:

| Sensor | Role | Bus / pin (authoritative: Core board package) |
|---|---|---|
| PIR (schematic IO15) | Immediate movement response | `pir_sensor_pin: GPIO15` |
| HLK-LD2450 | Movement, target tracking, position, radar target count | `roomiq_hi_link_uart` (TX=GPIO2 / RX=GPIO1, 256000 baud) |
| DFRobot SEN0609 (C4001) | Static-presence hold for still occupants | digital output `roomiq_sen0609_output_pin: GPIO6`; UART `roomiq_sen0609_uart` (TX=GPIO5 / RX=GPIO4, 115200) reserved |

The customer never needs to know which sensor produced the result.

## Customer entities (enabled by default)

The default-enabled surface is exactly this set (stable IDs; names are the
accepted customer contract; no `${friendly_name}` prefix per the
Core-Framework naming rules):

| Entity ID | Name | Type | Meaning |
|---|---|---|---|
| `s360_occupancy` | Occupancy | binary sensor (occupancy) | The fused room-occupied result (PD-01) |
| `s360_presence_status` | Presence Status | text sensor | One customer-facing story value (PD-02, below) |
| `s360_radar_target_count` | Radar Target Count | sensor | Instantaneous LD2450 target count; **unknown** (not 0) while radar data is stale (PD-09) |
| `s360_presence_mode` | Presence Mode | select (config) | Balanced / Responsive / Stable / Custom (PD-10) |
| `s360_presence_clear_delay` | Clear Delay | number (config) | 5–600 s, step 5, default 30 s; persisted across reboot; runtime-applied (PD-04) |

There is deliberately **no "Presence Sensitivity" entity** (PD-05): the
LD2450 native component and the SEN0609 digital output expose no supported
runtime sensitivity command, and PIR has none — one numeric control would
be a fabricated promise. Mode-based tuning ships first; a real sensitivity
contract can follow if a supported per-sensor mechanism lands.

There is **no "People Count" entity** (PD-09): radar targets are not
verified people.

## Presence Status values and precedence (PD-02)

`Presence Status` publishes exactly one of: **Initialising**, **Clear**,
**Movement detected**, **Still presence**, **Multiple targets**,
**Sensor degraded**, **Unavailable**.

**Wording decision ("Multiple targets", not "Multiple people"):** the
accepted product decision offered "Multiple people" as customer wording,
but the LD2450 reports radar targets and no physical validation exists yet.
Shipping "Multiple people" before bench evidence would present an
unverified people-claim as fact, so the entity uses the factual
**Multiple targets** first. Promoting the wording to "Multiple people" is
an explicit owner decision reserved until the bench checklist's
multi-occupant counting evidence exists; the trade-off (slightly more
technical wording now vs. an unsupportable people-claim) is accepted.

Factual precedence, evaluated top-down (single-sourced in
`status_to_string` / the engine; tested deterministically):

1. **Unavailable** — no usable Presence sensor remains (also shown on an
   explicit module fault).
2. **Initialising** — sensors are inside their startup windows and no
   higher-priority fault exists. Occupancy may already assert from valid
   data (e.g. an early radar frame) while the status still reads
   Initialising; Initialising is never falsely shown as Unavailable.
3. **Multiple targets** — occupied and fresh LD2450 data reports ≥ 2 valid
   radar targets. The value is **radar-derived** — radar targets, not
   confirmed people — and remains subject to physical validation (bench
   checklist; see the wording decision above).
4. **Movement detected** — occupied with an active movement signal (PIR
   within its hold window, or LD2450 moving target).
5. **Still presence** — occupied without movement (SEN0609 static presence
   or LD2450 still target; also shown while occupancy is held during the
   clear-delay countdown).
6. **Sensor degraded** — not occupied and the module is degraded.
7. **Clear** — no usable sensor reports presence and the clear delay has
   expired. Clear never appears before the delay expires.

**Documented deviation from the recommended ordering (customer-clarity
decision):** while the room is *occupied*, Presence Status keeps showing
occupancy activity (Multiple/Movement/Still) and the diagnostic
**Presence Module Status** entity carries the degradation. "Sensor
degraded" appears in the customer status only when there is no occupancy
activity to report. Rationale: hiding "Movement detected" behind "Sensor
degraded" would suppress the information customers automate on; the
degradation is still visible (module status below), and the accepted
contract's precedence list was recommended, not mandated — the prompt's
customer-clarity alternative is chosen and documented here.

## Fusion behaviour (PD-01 / PD-03) — fail-safe rules

Implemented in
[`include/sense360/presence_fusion.h`](../../include/sense360/presence_fusion.h)
(the same code the simulation tests exercise; no second implementation):

* **Any valid sensor asserts occupancy**: a PIR edge (after PIR warm-up), a
  fresh LD2450 frame with any target, or SEN0609 static presence (after its
  warm-up) turns Occupancy on. PIR edges re-evaluate the engine
  immediately (not on the next periodic tick).
* **Stale or unavailable data is unknown, never clear.** The LD2450 has a
  real freshness signal: every processed frame publishes the target-count
  sensor whose `on_value` callback timestamps `s360_radar_last_frame_ms`;
  no frame for `presence_radar_stale_ms` (default 5 s) makes the radar
  channel stale and removes it from all voting.
* **Clear requires unanimity of the usable set + the delay**: the clear
  timer starts only when every *currently usable* sensor reports clear;
  Occupancy turns off after the configured clear delay. A new detection
  cancels a pending clear.
* **A sensor failure never clears an occupied room**: a channel that goes
  stale while occupancy is active simply leaves the usable set. If usable
  sensors remain, the normal clear rules apply to them. If **no** usable
  sensor remains, occupancy is held conservatively and released only after
  the mode's documented degraded fallback timeout (Balanced 60 s,
  Responsive 30 s, Stable 300 s) — so a dead sensor set can neither
  instantly clear the room nor latch it forever.
* **No synthetic confidence**: the former 0.95/0.7/0.6 tiers in the radar
  package had no evidence basis and were removed. The legacy
  `presence_confidence` global remains only as a documented binary
  compatibility signal (1.0 = radar target present, 0.0 = none) for the
  pre-framework profiles still used by legacy products and compile-only
  skeletons.

## Sensor adapter contracts

Each adapter feeds the engine's internal per-channel contract
(expected / verifiable / warm-up window / freshness evidence / assertions):

* **LD2450** (verifiable): frame-driven update timestamps, target count,
  moving/still counts, three target coordinate sets. Its first real frame
  ends its initialisation early.
* **PIR** (non-verifiable): immediate movement assertion with 100 ms input
  debounce; movement retention (`pir_hold`) is mode-controlled fusion
  state, not a filter on the raw diagnostic.
* **SEN0609** (non-verifiable) — **GPIO-presence integration, phase 1, not
  a complete SEN0609 integration**: static presence from the documented
  digital output line only. ESPHome 2026.4.5 carries **no supported
  C4001/SEN0609 UART component** (only `dfrobot_sen0395`, a different
  sensor), and this repository approves no external component for it — so
  no UART protocol parser is invented, no target count / distance / speed
  detail is fabricated, and no runtime sensitivity command is claimed. The
  authoritative `roomiq_sen0609_uart` bus stays Core-owned and reserved.
  UART-based health / configuration / diagnostics is the tracked follow-up
  work item **PRESENCE-SEN0609-UART-001** (roadmap §13) — it requires a
  supported component, primary protocol documentation, and its own review.
  *Evaluated alternatives:* excluding SEN0609 from production fusion until
  UART support exists was rejected because the digital output is the
  sensor's documented primary detection interface and provides the
  still-occupant value the tri-sensor product intent exists for; marking
  it preview/experimental was rejected because channels are release-lane
  concepts, not per-entity flags — the phase-1 label plus unverifiable
  health modelling is the honest per-entity statement.

**Honest limitation (PIR and SEN0609):** a bare GPIO level cannot prove
communication health — a permanently low input may be a physically healthy
sensor in an empty room **or** a disconnected sensor; the hardware provides
no separate diagnostic signal to tell them apart. These channels therefore
assert occupancy and vote clear, but a binary `false` is never treated as
proof of health: they cannot qualify the module as fully Available on their
own and never drive it Unavailable. Their outputs are ignored during their
warm-up windows (PIR modules stabilise for tens of seconds after power-on
and emit false triggers meanwhile).

## Startup and warm-up

Sensor-specific windows (**provisional** engineering defaults pending bench
validation — deliberately not one arbitrary shared value; substitutions in
the fusion package): PIR 30 s, LD2450 10 s, SEN0609 15 s. The 100 ms GPIO
debounce and the 5 s radar stale window are provisional in the same sense.

During startup: Presence Status and the module status read **Initialising**;
occupancy may assert if a valid sensor reports presence; missing data inside
a warm-up window is never a fault. After warm-up, missing expected LD2450
data drives Degraded/Unavailable per the health rules below.

## Module health (PD-07) — Presence Module Status

The framework drives the Core-Framework entity
`s360_module_status_presence` ("Presence Module Status", diagnostic,
disabled by default — see
[`sense360-core-framework.md`](sense360-core-framework.md)) with the
reserved runtime vocabulary, from a real supported signal (LD2450
frame-driven freshness):

* **Initialising** — expected sensors inside their startup windows.
* **Available** — defined **strictly** (health-contract audit, Option A):
  the verifiable Presence transport — currently the LD2450 UART, whose
  frame-driven updates are the only real health signal — is fresh after
  warm-up and the fusion service is operational. This is **service
  availability, not full tri-sensor hardware health**: the PIR and SEN0609
  GPIO channels remain unverifiable (a low GPIO can mean clear,
  disconnected or failed) and are never claimed healthy. The diagnostic
  entity `s360_presence_verification_limits` ("Presence Sensor
  Verification") states this coverage limit on-device, and the contract
  wording is test-enforced. *Rejected alternative (Option B):* reporting
  permanent Degraded because GPIO sensors cannot be verified would make
  every healthy device look faulty forever, normalising Degraded and
  masking real radar failures — worse for customers and no more honest.
* **Degraded** — one or more expected sensors have failed or gone stale,
  but at least one usable sensor remains (a GPIO trigger channel keeps the
  module usable — it can never be proven dead).
* **Unavailable** — no usable Presence sensor remains (in the tri-sensor
  composition this requires losing the radar in a composition with no GPIO
  channels; expected-sensor membership is configuration-driven).
* **Fault** — reserved for an explicit unrecoverable component/configuration
  error. No composed sensor exposes a supported fault signal today, so
  Fault is never emitted from ordinary stale data; the engine input exists
  and is tested for future use.

Device Health aggregation: per the CORE-FRAMEWORK-001 contract, overall
Device Health may only aggregate module states once modules report real
runtime health; this PR wires the **Presence module status only** and does
not change the Device Health lambda — a degraded Presence module never
marks unrelated modules unavailable, and Device-Health aggregation remains
the documented follow-up in the core-framework contract.

## Modes (PD-10)

`Presence Mode` presets change **only** documented, genuinely
runtime-configurable fusion settings (see `mode_params()` in the shared
header) — no unsupported dynamic sensor commands are issued:

| Mode | Clear-delay preset | PIR movement hold | Degraded fallback |
|---|---|---|---|
| Balanced (default) | 30 s | 10 s | 60 s |
| Responsive | 10 s | 5 s | 30 s |
| Stable | 120 s | 20 s | 300 s |
| Custom | user's Clear Delay value | 10 s | 60 s |

**Every value in this table — plus the warm-up windows, the radar stale
window and the GPIO debounce — is a provisional engineering default
pending hardware validation.** None of them is customer-tested; presets
may change after bench evidence and such changes will be documented. All
four modes ship now (rather than only Balanced + Custom) because presets
differ solely in these deterministic, simulation-tested timing parameters
— the fail-safe fusion invariants are identical in every mode — and a
"Stable vs Responsive" choice is exactly the control still-occupant vs
quick-clear customers need; the provisional labelling, not a reduced
option list, is what keeps the claim honest.

Selecting Balanced/Responsive/Stable applies the preset to the Clear Delay
control (the number always shows and controls the live value); manually
editing Clear Delay away from the active preset switches the mode to
Custom, which never overwrites user values. **Future tuning (not claimed
today):** per-sensor thresholds/sensitivity (needs a supported SEN0609 UART
component and supported LD2450 runtime commands), still-presence retention
shaping, and bench-derived preset values.

## Clear Delay (PD-04)

Home-Assistant-adjustable number: minimum 5 s, maximum 600 s, step 5 s,
default 30 s; persisted across reboot (`restore_value`); read by the fusion
engine on every evaluation, so changes apply at runtime — **changing the
clear delay never requires recompilation.**

## Diagnostic entities (disabled by default and/or diagnostic)

Individual-sensor and technical detail stays out of the default view:

| Entity ID | Name | Where |
|---|---|---|
| `s360_pir_motion` | PIR Motion | PIR adapter |
| `s360_sen0609_presence` | SEN0609 Static Presence | SEN0609 adapter |
| `ld2450_occupancy` / `ld2450_has_moving` / `ld2450_has_still` | Radar Presence / Radar Moving Target / Radar Still Target | radar adapter |
| `ld2450_moving_target_count` / `ld2450_still_target_count` | Radar Moving/Still Target Count | radar adapter |
| `ld2450_t{1..3}_{x,y,speed,distance,angle}` | Radar Target N X/Y/Speed/Distance/Angle | radar adapter |
| `s360_radar_data_age` | Radar Data Age (stale-data timer) | fusion layer |
| `s360_presence_verification_limits` | Presence Sensor Verification (which sensors carry a real health signal) | fusion layer |
| `s360_module_status_presence` | Presence Module Status | core framework, driven by fusion |

Legacy compatibility entities `presence_binary`
("`${friendly_name}` Presence") and `presence_score`
("`${friendly_name}` Presence Score") keep their exact IDs and names —
existing Home Assistant entity IDs continue to work — and are now driven by
the fused occupancy result (Presence Score publishes the documented values
100/0, a state indicator, not a probability). Both are disabled by default
for new installs; already-registered entities in existing installs are
unaffected (Home Assistant applies disabled-by-default only at first
registration).

## Sense360Zones data contract (PD-06)

Future Sense360Zones work consumes the LD2450 target stream. The stable
API surface this framework guarantees (extend by addition only; never
rename, remove, or reduce resolution):

* Sensor IDs `ld2450_t1_x`, `ld2450_t1_y`, `ld2450_t1_speed`,
  `ld2450_t1_distance`, `ld2450_t1_angle` (and the `t2`/`t3` sets) at full
  component resolution/fidelity;
* `ld2450_target_count`, `ld2450_moving_target_count`,
  `ld2450_still_target_count`;
* the freshness evidence `s360_radar_last_frame_ms` /
  `s360_radar_frame_seen` globals.

No cross-repository Zones change is part of this work item.

## Board vs kit authority (reconciliation status)

Six distinct layers must never be conflated:

1. **Board BOM / schematic** (verified `S360-200-R4.pdf`,
   `config/hardware-catalog.json`): the **PIR (EKMC1601111, U3) is a
   soldered on-board component**; the **LD2450 (J2) and SEN0609 (J3) are
   connector-attached modules**, not board-soldered parts.
2. **Connector/pin capability** (Core board package): `pir_sensor_pin`
   GPIO15, `roomiq_hi_link_uart`, `roomiq_sen0609_uart` +
   `roomiq_sen0609_output_pin` GPIO6 — wiring capability only.
3. **Firmware compiled** (this framework): tri-sensor adapters composed in
   every presence-bearing bundle.
4. **Physical sensor fitted**: provable from this repository **only for
   the soldered PIR**; for the J2 (LD2450) and J3 (SEN0609) modules, SOT
   product authority (layer 5) defines them as included in every S360-200,
   while per-unit physical verification remains bench evidence
   (`PRESENCE-BENCH-001`).
5. **Commercial bundle sold** (SOT `products.yaml` / `bundles.yaml`,
   mirrored by `config/room-bundle-skus.json`,
   `config/shop-commercial-source-of-truth.json`): kits list board SKUs;
   every RoomIQ kit includes the complete S360-200 product.
6. **Runtime detected/healthy**: only the LD2450 UART produces a real
   runtime signal (see the health contract above).

**Layers 4–5 are resolved by product authority** (direct SOT inspection,
performed after the original audit which could not reach SOT):

* SOT `products.yaml` defines S360-200 RoomIQ as a **single product with
  no variant axis** whose defining capability is presence detection
  (legacy names *Comfort, Presence* — the Presence board carried the
  radars).
* SOT `bundles.yaml` composes every bundle from whole board SKUs; no
  bundle carves modules out of a board SKU.
* SOT `roadmap.yaml` ships Zone Studio publicly as "LD2450 and SEN0609
  radar zone configuration for Home Assistant" — an owner-authored
  statement that the customer RoomIQ product carries both radars.
* The canonical hardware catalog (`docs/hardware-catalog.md` /
  `config/hardware-catalog.json`) lists PIR, LD2450 and SEN0609 as
  S360-200 components, in deliberate contrast to its "Connectors for …"
  phrasing reserved for genuinely optional attachments (AirIQ: SPS30,
  SFA40; VentIQ: IR temp, SPS30). WebFlash's constraint matrix
  (`scripts/data/module-requirements.js`) mirrors the same sensor list.

**Conclusion: every RoomIQ-bearing bundle includes the LD2450 and SEN0609
modules by product definition; no radar-less RoomIQ variant exists in
SOT, this repository, or WebFlash.** Connector attachment at J2/J3 is an
assembly detail of the S360-200 product, not a per-kit option. This is
product authority, **not hardware proof** — per-unit fitment and sensor
behaviour stay on the operator bench checklist (`PRESENCE-BENCH-001`).

**Fail-safe posture (retained as defence-in-depth against assembly
defects):** if a J3 SEN0609 module is absent, its pulled-down GPIO reads
clear — it can neither assert false occupancy, nor block clearing, nor
affect health (unverifiable channel); if a J2 LD2450 module is absent,
the module status honestly reports Degraded after warm-up. Firmware
misbehaviour is bounded either way; the
`presence_sen0609_expected` / `presence_radar_expected` substitutions
remain available for any future composition that deliberately omits a
sensor.

## Compile-time inclusion vs runtime health

Compile-time membership (which adapters a bundle composes, the
`s360_module_presence: "Included"` substitution) remains distinct from
runtime health (this framework's Presence Module Status). Expected-sensor
membership for the fusion engine is configuration-driven
(`presence_pir_expected` / `presence_radar_expected` /
`presence_sen0609_expected` substitutions): a future composition that
intentionally omits a sensor overrides the flag and that absence is never
a fault. All current presence-bearing bundles are tri-sensor.

## Test expectations

* [`tests/test_presence_framework.py`](../../tests/test_presence_framework.py)
  — contract tests (entity set, naming, diagnostic policy, bundle wiring,
  adapter pin/bus authority, matrix/contract/doc sync, CI wiring). Runs in
  the per-PR "CI: Quick Validation" gate and in the compile lane's
  contract gate.
* [`tests/unit/test_presence_fusion.cpp`](../../tests/unit/test_presence_fusion.cpp)
  — the deterministic simulation layer: synthetic timestamped sensor events
  through the production fusion header; covers every accepted fusion,
  precedence, health and mode rule. Isolated from production publication
  paths; **never** hardware validation.
* Representative **compile evidence** comes from the existing hosted lane
  "CI: Core Framework Representative Compile"
  (`.github/workflows/core-framework-compile.yml`), whose matrix already
  covers the required tri-sensor targets: `Ceiling-POE-RoomIQ` (PoE RoomIQ
  tri-sensor), `Ceiling-USB-RoomIQ` (USB RoomIQ tri-sensor),
  `Ceiling-POE-VentIQ-RoomIQ` (Release-One) and
  `Ceiling-POE-VentIQ-RoomIQ-LED` (LED preview). Its path triggers were
  extended to the presence surfaces; its zero-artifact / no-publication /
  read-only guarantees are unchanged. A green run is firmware-build proof
  only.

## Limitations and hardware verification still required

* **No hardware validation is claimed.** All timing values (warm-ups,
  stale window, mode presets, debounce) are provisional engineering
  defaults pending bench measurement; the operator bench checklist is
  [`docs/hardware/presence-framework-bench-checklist.md`](../hardware/presence-framework-bench-checklist.md)
  (results and attestation are operator-only, never machine-written).
* PIR/SEN0609 health cannot be runtime-verified (GPIO levels); Available
  attests the verifiable sensor set only.
* SEN0609 UART features (sensitivity, distance, explicit errors) require a
  supported component that does not exist in ESPHome 2026.4.5.
* "Multiple targets" is radar-derived target counting, not verified people
  counting; the "Multiple people" wording stays reserved for an owner
  decision after bench evidence.
* Sensitivity and timing tuning remains pending; presets may change after
  bench evidence, and such changes will be documented.

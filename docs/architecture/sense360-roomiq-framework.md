# Sense360 RoomIQ framework (ROOMIQ-FRAMEWORK-001)

**Status: software foundation implemented — compile + simulation proof only.
Physical validation pending
([bench checklist](../hardware/roomiq-framework-bench-checklist.md)).**

This document is the authoritative architecture / customer reference for the
Sense360 RoomIQ environmental framework: the canonical local environmental
service for the platform. It turns the S360-200 RoomIQ climate half from a
collection of raw sensors into calibrated, freshness-aware, human-friendly
environmental truth that customers and other frameworks (LED today; VentIQ /
AirIQ / Zones later) consume.

Related contracts:

* Entity / behaviour contract test: `tests/test_roomiq_framework.py`
* Shared engine (single implementation): `include/sense360/roomiq_engine.h`
* Deterministic simulation: `tests/unit/test_roomiq_engine.cpp`
* Production package: `packages/features/roomiq_framework.yaml`
* Module-status contract: `config/core-framework.json`
  (`module_runtime_status.roomiq`)
* Core framework: [sense360-core-framework.md](sense360-core-framework.md);
  Presence: [sense360-presence-framework.md](sense360-presence-framework.md);
  LED: [sense360-led-framework.md](sense360-led-framework.md)

Everything below is **local-first**: all logic runs on the device and works
without internet. Home Assistant is a consumer, never a dependency.

---

## 1. Customer entities

Default-enabled set (the ONLY default-enabled RoomIQ surface):

| Entity | Type | Values / range | Meaning |
|---|---|---|---|
| Temperature | sensor (°C) | calibrated | Canonical room temperature |
| Humidity | sensor (%) | calibrated | Canonical relative humidity |
| Illuminance | sensor (lx) | calibrated | Canonical light level |
| Comfort | text | Initialising · Comfortable · Cool · Cold · Warm · Hot · Dry · Humid · Warm and humid · Unavailable | Concise comfort assessment (temperature + humidity only) |
| Environment State | text | the Comfort values plus Dark · Bright | ONE headline description of the room |
| Brightness | text | Initialising · Dark · Dim · Normal · Bright · Very bright · Unavailable | Human-friendly light category |
| Temperature Offset | number (config) | −15…+15 °C, 0.1 steps | Local calibration |
| Humidity Offset | number (config) | −30…+30 %, 0.5 steps | Local calibration |
| Illuminance Calibration | number (config) | ×0.2…×5.0, 0.05 steps | Local calibration multiplier |

There is deliberately **no customer-facing numeric comfort score** (accepted
owner decision: human-friendly states). No customer entity name carries a
sensor model (`VEML7700`, `LTR-303ALS`, `SHT4x`), `raw`, `filtered`, or other
technical jargon — technical identity lives in diagnostics and this document.

Wording rule: the light entity is called **Illuminance** (never a model name)
as a matter of customer-surface style. The compiled driver is reconciled to the
schematic/BOM part LTR-303ALS-01 @ 0x29 (§8); on-hardware sensor response is
still pending bench.

### Diagnostics (diagnostic category, disabled by default)

Raw Temperature / Raw Humidity / Raw Illuminance (uncalibrated), Climate Data
Age, Illuminance Data Age, RoomIQ State Detail (why the current states are
what they are), RoomIQ Calibration State (active offsets/multiplier), and
RoomIQ Sensor Verification (the on-device honesty note about freshness
coverage and the light-sensor driver identity / pending on-hardware response).

### Legacy compatibility entities (disabled by default)

Every pre-framework published entity id keeps existing so no Home Assistant
entity id or automation ever breaks. They are now driven by the **calibrated**
canonical outputs and are honest about missing data (unknown instead of a
frozen stale value) — a documented semantic upgrade:

| Legacy id | Legacy name | Now driven by |
|---|---|---|
| `comfort_temperature_display` | RoomIQ Temperature | copy of canonical Temperature |
| `comfort_humidity_display` | RoomIQ Humidity | copy of canonical Humidity |
| `comfort_light_display` | RoomIQ Light Level | copy of canonical Illuminance |
| `comfort_feels_like` | RoomIQ Feels Like | engine heat index (Rothfusz) |
| `comfort_score_display` | RoomIQ Comfort Score | engine legacy 0-100 score |
| `comfort_status` | Comfort Status | engine legacy score bands |
| `comfort_light_status` | Light Status | canonical Brightness mapped to the legacy 4-value vocabulary (Very bright → "Bright"; bands are now the canonical 10/50/300 lx instead of the old 10/100/500 lx) |
| `comfort_temp_advice` | Temperature Advice | engine (legacy thresholds preserved) |
| `comfort_humidity_advice` | Humidity Advice | engine (legacy thresholds preserved) |

They ship disabled-by-default in framework bundles (the canonical surface
replaces them), exactly the migration pattern PRESENCE-FRAMEWORK-001
established for `presence_binary` / `presence_score`. Legacy include paths
(`packages/features/comfort_basic_profile.yaml`, `roomiq_profile.yaml`,
`packages/expansions/comfort_ceiling.yaml`) keep resolving with their exact
pre-framework behaviour for pinned customer configs.

---

## 2. Canonical environmental outputs (internal reuse contract)

RoomIQ is the **single platform source** for environmental truth. The stable
internal contract other frameworks consume:

| Output | Where | Contract |
|---|---|---|
| Calibrated temperature | sensor `s360_temperature` / `engine.temperature()` | °C; unknown (NAN) unless fresh |
| Calibrated humidity | sensor `s360_humidity` / `engine.humidity()` | %, clamped 0–100; unknown unless fresh |
| Calibrated illuminance | sensor `s360_illuminance` / `engine.illuminance()` | lx; unknown unless fresh |
| Freshness | `engine.temperature_fresh()` etc. | valid-update-driven, per channel |
| Comfort | text `s360_comfort` / `engine.comfort()` | see §4 |
| Brightness | text `s360_brightness` / `engine.brightness()` | see §6 |
| Environment State | text `s360_environment_state` / `engine.environment()` | see §5 |
| Darkness decision | `engine.darkness()` (Dark / Not dark / Unknown) | consumer-parameterised threshold service (§7) |
| Module health | `s360_module_status_roomiq` | Initialising / Available / Degraded / Unavailable (/ reserved Fault) |

In-firmware consumers call `sense360::roomiq::global_engine()` directly (the
LED framework does); Home-Assistant-level consumers use the canonical
entities. **No framework may re-read `comfort_ceiling_*` raw sensors or
re-apply calibration when a canonical output exists** — that would duplicate
threshold logic or calibrate twice (both test-guarded).

Future consumers (documented intent, NOT implemented here): VentIQ can
consume calibrated humidity/temperature for shower and ventilation logic;
AirIQ can fold Comfort into a combined air-quality/environment statement;
Zones/mobile can consume Environment State and Brightness as headline
context. Those integrations are separate work items.

---

## 3. Calibration model

* **Applied exactly once**, inside the shared engine. Raw sensors stay
  internal and uncalibrated; canonical and legacy entities all carry the
  calibrated value; the LED darkness decision uses the calibrated
  illuminance, so one customer calibration corrects the whole platform.
* Offsets for temperature (±15 °C) and humidity (±30 %) — additive errors
  dominate the climate path. A **multiplier** (×0.2…×5.0) for illuminance —
  ambient-light error is dominated by multiplicative effects (gain, diffuser
  attenuation, mounting), so a scale factor is the least misleading model.
* Changes apply at runtime (next evaluation, with an immediate canonical
  republish) and **persist across restart** (`restore_value: true`).
* Safety: the engine clamps every calibration value to its safe band and
  recovers invalid stored values (NaN, non-positive scale) to neutral;
  calibrated humidity is clamped to the physical 0–100 % range. The UI
  control limits and the engine clamps are kept in agreement (test-guarded).
* Bounds context: the ranges were widened from ±5 °C / ±10 % to ±15 °C /
  ±30 % after the S360-200-R4 bench found the prototype board needed roughly
  −7.7 °C and +17 %RH corrections — beyond the former limits. A correction
  this large is **not** a normal calibration need: it indicates a
  board/enclosure thermal-placement problem (SHT45 self-heating / heat bias)
  that requires hardware investigation. Software calibration makes the
  current prototype usable but is **not** proof that the production thermal
  design is acceptable. Neutral defaults remain 0 / 0 / ×1.0 — the large
  values are per-device bench corrections entered through the persisted
  runtime controls, never shared framework defaults.
* "Calibrated" means **calibrated locally by the customer against their own
  reference** — no factory accuracy claim is made before calibration.

---

## 4. Comfort model

Comfort is based on calibrated temperature and humidity **only** (accepted
owner decision; illuminance never changes Comfort). Values: Initialising,
Comfortable, Cool, Cold, Warm, Hot, Dry, Humid, Warm and humid, Unavailable.

Provisional bands (comfort heuristics — never medical, health or regulatory
thresholds; pending customer and bench validation):

| Temperature | Band | | Humidity | Band |
|---|---|---|---|---|
| < 16 °C | Cold | | < 30 % | Dry |
| 16–18 °C | Cool | | 30–60 % | Comfortable |
| 18–24 °C | Comfortable | | > 60 % | Humid |
| 24–27 °C | Warm | | | |
| > 27 °C | Hot | | | |

Deterministic precedence: **Unavailable > Initialising > Warm and humid
(warm-or-hot AND humid) > temperature discomfort > humidity discomfort >
Comfortable.** Cold+humid therefore reports Cold (the temperature problem).

Hysteresis: band changes require crossing the boundary by 0.3 °C / 2 %RH, so
sensor noise at a boundary never flaps the state. Comfort requires **both**
climate channels fresh; otherwise it is honestly Initialising (startup) or
Unavailable — never computed from stale data.

Advanced tuning: thresholds are substitutions
(`roomiq_temp_*`, `roomiq_humidity_*` in `roomiq_framework.yaml`) — one
coherent, documented contract instead of a dashboard of engineering
constants. Customer-facing profiles may follow if customer testing proves
useful.

---

## 5. Environment State

One glanceable headline. It is deliberately **not** a duplicate of Comfort:

* Comfort answers "does temperature/humidity feel comfortable?"
* Environment State summarises **the most relevant condition**: any climate
  discomfort is the headline; when the climate is comfortable, a notable
  light condition surfaces (**Dark**, or **Bright** for the very-bright
  band); otherwise it is Comfortable. Unremarkable light (Dim / Normal /
  ordinary Bright) never overrides Comfortable — that information lives in
  the Brightness entity.
* Partial honesty: with the climate unavailable but fresh lux, a notable
  light condition (Dark / Bright) is still reported; anything else is
  Unavailable — never a fabricated climate statement.

Scope assessment (required by the work item): the duplication risk was
evaluated against dropping the entity. It stays because (a) it is the only
entity that can serve as a single-headline consumer contract for future
combined states (AirIQ air quality, VentIQ shower state), and (b) the
precedence above keeps it deterministic and non-contradictory
(simulation-tested: it never disagrees with Comfort). If customer testing
shows confusion, the documented fallback is to hide it by default — a
one-line change that breaks nothing.

---

## 6. Brightness model

Calibrated illuminance plus a human-friendly category. Provisional
room-ambience bands (not lighting-standard compliance values):

| Illuminance | Category |
|---|---|
| < 10 lx | Dark |
| 10–50 lx | Dim |
| 50–300 lx | Normal |
| 300–1000 lx | Bright |
| > 1000 lx | Very bright |

Hysteresis prevents category flapping: rising crosses the plain boundary;
falling requires dropping 20 % below it. Stale or invalid lux is
Initialising/Unavailable — invalid lux is **never** interpreted as Dark. A
small median filter (window 3 over ~10 s samples) rejects single-sample
outliers with at most ~20 s added lag; temperature/humidity get no extra
smoothing (30 s cadence, high-precision mode). All filter windows are
provisional pending bench testing.

---

## 7. LED integration (darkness service)

Before this work item the LED framework owned its own lux freshness,
threshold and hysteresis logic (`led_controller.h`) fed by the raw
`comfort_ceiling_illuminance` sensor. That duplicate engine is **gone**:

* The darkness decision (dark below threshold; not-dark above threshold ×
  hysteresis factor; Unknown on missing/stale/invalid lux) now lives in the
  RoomIQ engine as a consumer-parameterised service, computed from the
  **calibrated** illuminance path and its staleness window.
* The LED framework passes its customer **Darkness Threshold** number (id,
  range, default and semantics unchanged) and hysteresis factor into the
  service each evaluation and injects the decision into the LED controller
  (`input_darkness`). Customer behaviour, entity ids and fail-safe rules
  (Unknown never activates or toggles Night Mode) are preserved; simulation
  tests pin both sides, and regression tests prove no duplicate
  lux-threshold implementation remains.
* Because the service consumes calibrated illuminance, the customer's
  Illuminance Calibration now also corrects night-mode behaviour — one
  calibration, whole platform.

LED behaviour was otherwise deliberately not redesigned.

---

## 8. Sensor identity evidence (driver reconciled — runtime pending)

The evidence layers for the ambient-light sensor now **agree** on the part;
`S360-200-R4-HARDWARE-RECONCILIATION-001` corrected the firmware to match:

| Layer | Evidence | Says |
|---|---|---|
| Designed hardware | S360-200-R4 schematic (`docs/hardware/s360-200-r4-roomiq.md`) | `U1` = LTR-303ALS-01 |
| Fitted production component | BOM capture (`docs/hardware/artifacts/S360-200-R4.md`) | LTR-303ALS-01 (Lite-On) |
| Firmware component compiled | `packages/boards/s360-200-roomiq-climate.yaml` | LTR-303ALS-01 at I²C 0x29 (built-in `ltr_als_ps`, ALS-only) |
| Runtime communication | board under test: I²C scan lists 0x59/0x60/0x62 only (AirIQ); no 0x29 yet | pending bench |
| Customer-facing claim | this framework | "Illuminance" — no model name |

The earlier compiled `veml7700` @ 0x10 was firmware drift (no VEML7700 on the
schematic/BOM/catalog, and the board under test does not answer at 0x10). It is
removed; the firmware now drives the schematic/BOM part LTR-303ALS-01 at its
fixed address 0x29 via ESPHome's built-in `ltr_als_ps` platform, configured
ALS-only (`type: ALS`, no proximity entities). The `0x29` address is
datasheet-fixed for the LTR-303/329 family — it is not a board strap and is not
guessed.

**Runtime is not yet proven.** The physical board under test currently lists
only the AirIQ sensors (0x59/0x60/0x62) on its I²C scan and does **not** yet
show 0x29 (LTR) or 0x44 (SHT45). The bus is proven live (AirIQ answers on it),
so the RoomIQ climate sensors' non-appearance is a **physical population /
connector-seating / +3.3 V-rail question on that assembly**, not a firmware
address error. Until the sensor answers on the bus the framework fails honestly:
Illuminance unknown, Brightness Unavailable, darkness Unknown (LED night
automation freezes safe), module status Degraded, Comfort still available.
On-hardware confirmation is tracked as the `ENTITY-RECONCILE-200-ALS-001` matrix
row and the bench checklist's sensor-identity section. The SHT45 climate
identity is consistent across all layers (schematic U2, BOM `SHT45-AD1B-R3`,
firmware `sht4x` @ 0x44 — the `AD1B` variant is the 0x44 address part).

---

## 9. Freshness and module health

A value is usable only after a real, valid (non-NaN) update callback:

* climate (SHT4x, 30 s cadence): stale after 90 s (3 missed updates);
  warm-up window 60 s.
* illuminance (10 s cadence): stale after 60 s; warm-up window 30 s.

Module status (`RoomIQ Module Status`, Core-Framework entity, reserved
runtime vocabulary — the second wired module after Presence):

| State | Meaning |
|---|---|
| Initialising | required channels warming up / awaiting first valid data (never a fault) |
| Available | every channel fresh — **data-service availability only**, not accuracy, calibration correctness or hardware health |
| Degraded | some channels fresh, some not (e.g. illuminance failed, climate alive: Comfort stays available, Brightness goes unavailable) |
| Unavailable | no channel fresh after warm-up |
| Fault | reserved for an explicit component error — **no production producer exists today**; never emitted from ordinary stale data |

Temperature and humidity share one physical sensor (SHT4x), so their shared
failure appears as both channels going stale together — tracked independently
but honestly documented. Compilation is never claimed as sensor health.

---

## 10. Bundle membership and compile evidence

Every catalog-declared RoomIQ-bearing config (all 14 in
`config/core-framework.json`, including the Release-One stable
`Ceiling-POE-VentIQ-RoomIQ`) composes `roomiq_framework.yaml` exactly once
and drops the legacy display profile. Non-RoomIQ configs gain nothing —
enforced by tests and by the representative compile lane
(`.github/workflows/core-framework-compile.yml`), which covers PoE/USB
RoomIQ, AirIQ+RoomIQ, VentIQ+RoomIQ (Release-One), both LED-bearing bundles
and the non-RoomIQ regression target `Ceiling-POE-FanDAC`. The lane uploads
no artifacts and publishes nothing.

Proof boundaries (do not overclaim): `esphome config` proof is not compile
proof; compile proof is not hardware proof; the 50-scenario simulation suite
is logic proof only, never customer validation. **Physical validation
pending** — see the results-free
[bench checklist](../hardware/roomiq-framework-bench-checklist.md); operator
attestations are never machine-written.

---

## 11. Limitations and honest scope

* All comfort/brightness thresholds, freshness windows and filter values are
  provisional engineering defaults pending bench + customer validation.
* No medical or health claim; comfort is a heuristic. No mould/condensation
  statement of any kind. No lighting-standard claim.
* No accuracy claim before local calibration; no hardware reliability claim
  before bench testing.
* The BMP581 pressure sensor on the S360-200 BOM remains uncompiled and
  unexposed (existing `ENTITY-FILL-200-PRESSURE-001` matrix row — out of
  scope here).
* Dew point remains an internal legacy value only (no owner ask to expose
  it).
* No SOT, WebFlash, Shopify, provisioning, release-declaration or commercial
  state changed. Programme-level status changes belong to SOT.

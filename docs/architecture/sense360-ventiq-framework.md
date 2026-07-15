# Sense360 VentIQ framework (VENTIQ-FRAMEWORK-001)

Canonical bathroom ventilation service for the S360-211 VentIQ board:
one deterministic, explainable customer answer to *Is ventilation
required, why, what is driving it, and what should I do?* — built by
consuming the platform's existing canonical services (the AirIQ
pollutant engine, the RoomIQ environmental service and the Core runtime
framework) plus the VentIQ-owned ventilation logic (shower detection,
moisture clearing, damp/mould tracking, odour), produced by one shared
engine ([`include/sense360/ventiq_engine.h`](../../include/sense360/ventiq_engine.h))
that is compiled into production firmware
([`packages/features/ventiq_framework.yaml`](../../packages/features/ventiq_framework.yaml))
and into the deterministic simulation tests
([`tests/unit/test_ventiq_engine.cpp`](../../tests/unit/test_ventiq_engine.cpp))
so tested logic and shipped logic cannot drift. The contract is pinned by
[`tests/test_ventiq_framework.py`](../../tests/test_ventiq_framework.py).

Everything in this document is **compile / simulation proof only**.
There is no hardware, bench, compliance, safety or commercial claim made
anywhere in it;
physical validation is pending
([`docs/hardware/ventiq-framework-bench-checklist.md`](../hardware/ventiq-framework-bench-checklist.md),
tracked as `VENTIQ-FRAMEWORK-BENCH-001`).

---

## 1. Hardware authority — what the S360-211 actually is

Established by direct audit of the primary sources: the **verified R4
schematic** `docs/hardware/schematics/S360-211-R4.pdf`
(`schematic_status: verified` in
[`config/hardware-catalog.json`](../../config/hardware-catalog.json)),
[`docs/hardware-catalog.md`](../hardware-catalog.md),
[`docs/hardware/s360-211-r4-ventiq.md`](../hardware/s360-211-r4-ventiq.md)
(HW-007), [`docs/hardware/s360-211-module-pinmap.md`](../hardware/s360-211-module-pinmap.md),
[`packages/boards/s360-211-ventiq.yaml`](../../packages/boards/s360-211-ventiq.yaml),
[`config/feature-entity-matrix.json`](../../config/feature-entity-matrix.json),
[`config/core-framework.json`](../../config/core-framework.json),
[`config/product-catalog.json`](../../config/product-catalog.json) and SOT
`products.yaml` / `bundles.yaml`.

The evidence layers **schematic / BOM / assembly / firmware / bundle /
customer / bench** are recorded separately and never merged: a schematic
symbol is not population proof; a connector is not fitted hardware; a
compiled driver is not product hardware; a bundle include is not a
customer entity; transport liveness is not accuracy; nothing below is
bench evidence.

### 1.1 What the verified schematic shows (single sheet, Id 1/1)

| Item | Evidence | Framework treatment |
|---|---|---|
| **SGP41 (U3)** — VOC/NOx, shared I2C | The ONLY on-board sensor drawn. Matches the catalog line "SGP41 on board". BOM/CPL not committed (Drive `bom`/`cpl` retained-but-not-committed; `docs/hardware/artifacts/` has **no S360-211 record**), so *population* itself is schematic + compiled-firmware + catalog agreement, not assembly proof. | The board's only expected module-health channels (VOC, NOx). |
| **J1 "FROM CORE"** — 5-pin: +3.3V, +5V, I2C_SCL, I2C_SDA, GND | Drawn on the sheet; matches pinmap candidate A (Core `J1`, 5-pin). The Core-side connector identity (`J1` 5-pin vs `J9` 7-pin) remains an open cross-doc disagreement — **recorded, not resolved here** (silkscreen/harness evidence owed under S360-100-BENCH-001). | No framework dependency on the connector identity. |
| **J4 "SPS30"** — 5-pin, I2C + 5V | External particulate module connector. Catalog doctrine reserves "Connectors for …" phrasing for genuinely optional attachments (VentIQ: IR temp, SPS30). No driver compiled in the canonical board package; no kit/SOT record declares the module supplied. | No PM entity exists; nothing pretended. A future declared attachment would opt in through the engine's expected-channel passthrough. |
| **J3 "Temperature Sensor Digital, Infrared"** — 4-pin, I2C | External IR-temperature connector (off-board module; interface details **verify** per HW-007). No driver compiled in the canonical board package. | No surface-temperature entity exists; nothing pretended. |
| **Inline fan-relay stage (K1, D1, Q1 MMBT3904, R2, R3, J2 "Inline Fan")** | Drawn with the components **crossed out** — the KiCad exclude/do-not-populate convention. No BOM/CPL is committed to confirm either way; no drive-signal source is identified; no driver is bound; the Release-One config string carries no fan token. | **No runtime fan health exists and none is invented.** Population/DNP status is the `VENTIQ-RELAY-POPULATION-001` follow-up; compliance stays COMPLIANCE-001. Compile-time fan-module presence stays with the Core framework's Fan Control Module Status. |
| **No SHT4x. No BMP390.** | Neither part appears anywhere on the verified single-sheet schematic, nor in the catalog description, and no BOM record exists. | See the drift conflict below (§1.2 C1). |

### 1.2 Conflicts found by this audit — recorded, not silently resolved

* **C1 — compiled SHT4x/BMP390 vs the verified schematic (firmware/schematic
  drift).** The board package compiles `sht4x` @0x44 and `bmp3xx_i2c` @0x77,
  and the entire pre-framework shower/mould/odour logic ran on that SHT4x —
  but the verified schematic shows neither part, the catalog BOM line names
  neither, and [`config/feature-entity-matrix.json`](../../config/feature-entity-matrix.json)
  already CONFIRM-flags both rows ("not called out on the VentIQ catalog BOM
  line; confirm against the landed BOM"). Composition-level observation
  (fact, not proof): in every current VentIQ product the S360-200 RoomIQ
  board's SHT4x sits at the **same address (0x44) on the same shared
  `core_i2c` bus**, so the two compiled `sht4x` components poll one physical
  device — the "VentIQ Temperature/Humidity" customers saw most plausibly
  came from the RoomIQ board. No plausible device answers the `bmp3xx`
  driver at 0x77 in a VentIQ+RoomIQ composition (the RoomIQ catalog pressure
  part is a BMP581, which is not compiled). **Resolution path:** the board
  package stays byte-compatible in this PR (raw ids internal, addresses and
  intervals unchanged); the reconciliation — remove/rebind the drifted
  drivers, or land contrary BOM/CPL evidence — is the **`VENTIQ-HW-DRIFT-001`**
  follow-up with owner sign-off. The framework itself takes **no input**
  from the drifted drivers.
* **C2 — `S360-BATH-B` module-SKU label.** The board package publishes a
  diagnostic text sensor "AirIQ Module SKU" with `module_sku: S360-BATH-B` —
  an identifier that exists in **no** hardware catalog (canonical SKU:
  `S360-211`), under a stale "AirIQ" label. Changing it alters the published
  legacy surface, so it is preserved byte-identically here and tracked as
  **`VENTIQ-SKU-LABEL-001`**.
* **C3 — Core connector identity `J1` (5-pin) vs `J9` (7-pin).** The
  module-side verified schematic draws a 5-pin `J1 FROM CORE` (supporting
  pinmap candidate A), while the HW-007 board audit recorded mating with the
  Core 7-pin `J9`. Already tracked (S360-100-BENCH-001 silkscreen/harness
  evidence); this framework adds no dependency on the answer.
* **C4 — stale status text in `docs/hardware/s360-211-r4-ventiq.md`.** The
  HW-007 reference doc still says `schematic_status` "stays
  `cataloged_unverified`" pending HW-008, while the catalog JSON now says
  `verified`. The JSON is the machine-readable source of truth; the doc
  correction belongs to the hardware-doc chain, not this framework PR
  (noted here so it is not re-discovered).
* **C5 — placebo customer controls (customer-experience defect, fixed
  here).** The shipped profile exposed three threshold Numbers
  (`bathroom_shower_threshold`, `bathroom_post_shower_duration`,
  `bathroom_mold_threshold`) that **no logic ever read** (the detection
  lambdas used compile-time substitutions), and an "Auto Ventilation" switch
  whose only action was a log line (no fan driver is bound to VentIQ in any
  composition). The framework wires the three Numbers into the engine
  (their ids, names and ranges preserved) and moves the do-nothing switch
  off the default surface (id preserved, disabled by default).

### 1.3 There is no Base / Pro axis

The product taxonomy is flat: one SKU per product, and S360-211
"Sense360 VentIQ" is the only VentIQ SKU (SOT lists exactly one, status
stable, production lane). The legacy "Pro" overlay
(`s360-211-ventiq-pro.yaml`, adding MLX90614 + SPS30 drivers) and the
`S360-BATH-B` "bathroom_base" naming are legacy artifacts, not product
authority; no current catalog composition binds the Pro overlay. This
framework does not invent a Base/Pro flag: expected-channel membership is
configuration-driven by the `ventiq_expected_*` substitutions and the
engine's expected-channel passthrough.

---

## 2. Reuse — consume canonical services, never duplicate

Accepted design rule: the framework consumes existing canonical services
and owns only VentIQ behaviour.

* **Pollutant truth = the canonical AirIQ engine.** The VentIQ engine
  embeds `sense360::airiq::AirIQEngine`
  ([`include/sense360/airiq_engine.h`](../../include/sense360/airiq_engine.h))
  with expected channels VOC + NOx (the AirIQ default of an expected CO2
  channel is composition configuration for the S360-210 board, overridden
  for S360-211 which has no CO2 sensor). **No VOC/NOx band value is
  re-declared anywhere** — the AirIQ defaults are the values (enforced by
  contract test). The odour signal is defined as *VOC or NOx at Fair or
  worse*: the canonical Fair boundary (VOC index 150) is exactly the
  legacy VentIQ odour threshold, so the legacy semantics survive without a
  second threshold. This is precisely the consumption path the AirIQ
  architecture doc reserved for VentIQ.
* **Environmental truth = the RoomIQ canonical service.** Humidity and
  temperature inputs are `s360_humidity` / `s360_temperature`
  (ROOMIQ-FRAMEWORK-001: calibrated, freshness-gated, going unknown when
  stale). Raw board sensors are never re-read; RoomIQ Comfort is never
  merged into ventilation state; RoomIQ's comfort thresholds are not
  duplicated — the shower/damp values here are **ventilation** heuristics
  (humidity *dynamics* and *duration*), semantics RoomIQ does not own.
  Every VentIQ-bearing catalog composition also carries RoomIQ, so the
  canonical source is always present (checked against
  `config/core-framework.json` configs).
* **Core runtime framework.** VentIQ module health publishes into the
  existing `s360_module_status_ventiq` entity
  (`packages/base/device_framework.yaml`) as the **fourth wired runtime
  module** (contract: `config/core-framework.json`
  `module_runtime_status.ventiq`). "Is the ventilation hardware
  available?" is answered by the existing compile-time **Fan Control
  Module Status** entity — deliberately not duplicated.
* **Presence framework:** evaluated and **not** consumed in this slice. An
  occupancy-aware ventilation refinement (e.g. suppressing advice in an
  empty home) is a behaviour change with customer-visible consequences
  that deserves its own decision; nothing in the current model needs
  presence to be honest. Recorded as a possible future refinement, not a
  gap.

---

## 3. Customer experience

Customer questions → entities (default-enabled set, the ONLY
default-enabled set):

| Question | Entity | id | Values / unit |
|---|---|---|---|
| Is ventilation required? | Ventilation Needed (binary) | `s360_ventilation_needed` | on = Ventilate soon/now |
| What should I do? | Recommendation | `s360_ventiq_recommendation` | Sensor initialising / No action needed / Ventilate soon / Ventilate now / Unavailable |
| Why? | Ventilation Reason | `s360_ventiq_reason` | No ventilation needed / Ventilation requested / Shower in progress / Clearing shower moisture / Poor air quality / Damp for a long time / Odour detected / High humidity / Sensor initialising / Unavailable |
| What is the air like? | Air Quality | `s360_ventiq_air_quality` | Initialising / Good / Fair / Poor / Very poor / Unavailable |
| What is it measuring? | VOC, NOx | `s360_ventiq_voc`, `s360_ventiq_nox` | relative indices (unitless by design — never concentrations) |
| Is someone showering? | Shower Active (binary) | `s360_ventiq_shower` | moisture |
| Is damp building up? | Mould Risk (binary) | `s360_ventiq_mould_risk` | problem (medium/high accumulated damp) |

Plus the preserved customer controls, now genuinely wired (§1.2 C5):
Shower Detection Threshold, Post-Shower Ventilation Duration, Mold Risk
Threshold (numbers), Shower Detection (switch), Force Ventilation / Reset
Shower Detection / Reset Mold Risk (buttons).

Deliberately absent: a duplicate Temperature/Humidity pair (RoomIQ owns
the canonical entities in the same composition), any pressure entity
(§1.2 C1), any IR-temp/PM entity (§1.1), any AQI, any blended score, any
"fan status"/"ventilation hardware health" runtime claim, and any
threshold-control farm. Diagnostics (`VentIQ State Detail`, `VentIQ
Expected Sensors`, `VentIQ Sensor Verification`, data ages) are
diagnostic-category and **disabled by default**.

### 3.1 The ventilation model (deterministic priority ladder)

Highest active tier wins; one reason, always explainable; evaluated by
the shared engine on every input and a 10 s tick:

1. **Ventilation requested** (Force Ventilation button; honoured
   regardless of sensor state) → Ventilate now.
2. **Shower in progress** → Ventilate now. Start: humidity rate-of-rise
   ≥ 5 %/min (over a 3-minute sample window) OR absolute humidity ≥
   threshold (default 75 %). End: humidity below threshold − 10 % and
   falling — or a 60-minute timeout so a saturated bathroom is never
   claimed to be an hour-long shower (the absolute trigger then re-arms
   only after humidity falls below the threshold).
3. **Clearing shower moisture** (post-shower window, default 15 min) →
   Ventilate soon (fan 70 % on the compatibility surface). Very poor air
   still outranks it.
4. **Poor air quality** (canonical severity: Very poor → now; Poor →
   soon).
5. **Damp for a long time** (mould-risk accumulator: humidity ≥ 65 % for
   ≥ 30 min → medium/soon; ≥ 60 min → high/now; accumulator freezes —
   no accumulation, no reset — while humidity data is missing).
6. **Odour detected** (VOC or NOx at Fair or worse) → Ventilate soon.
7. **High humidity** (≥ 60 % with 2 % release hysteresis) → Ventilate
   soon.
8. Otherwise **No action needed**.

If no usable input exists at all: *Sensor initialising* during warm-up,
otherwise *Unavailable* — and Ventilation Needed is off (no fabricated
demand). If one side is lost (humidity vs air), the service continues
honestly on the remaining side and the diagnostics say which input is
missing. All values are **provisional engineering heuristics** pending
bench and customer validation — never medical, health, building-standard
or regulatory claims (indoor-humidity/mould guidance informed the 60–75 %
bands; no standard is claimed to be implemented).

---

## 4. Module health

Uses the Core-Framework reserved vocabulary
(`config/core-framework.json` `module_runtime_status.ventiq` — the fourth
wired module after Presence, RoomIQ and AirIQ), over the S360-211's own
verifiable channels ONLY — the SGP41 VOC/NOx update callbacks:

* **Initialising** — SGP41 channels inside the 120 s conditioning warm-up;
* **Available** — both expected channels fresh (data-service availability
  only: never accuracy, calibration correctness or hardware health);
* **Degraded** — one SGP41 channel stale while the other stays fresh;
* **Unavailable** — both gone (the humidity-driven ventilation service
  may still be running from the RoomIQ canonical input — service
  availability and module health are deliberately separate);
* **Fault** — reserved engine contract; no composed component exposes a
  supported fault signal today, and ordinary staleness never produces it.

The RoomIQ-owned humidity/temperature inputs **never** participate: their
loss quiets the shower/damp features honestly (values go unknown, no
shower claim is maintained, the accumulator freezes) while the RoomIQ
module status reports its own outage. A healthy VentIQ board is never
blamed for a RoomIQ failure, and vice versa. The on-device
`VentIQ Sensor Verification` diagnostic states these limits.

---

## 5. Compatibility

* The framework **supersedes `bathroom_profile.yaml` in bundles**
  (composing both would duplicate the preserved ids — enforced by
  ESPHome validation and contract test). Legacy shim products
  (`products/sense360-core-ceiling-bathroom.yaml`) and compile-only
  skeletons keep the profile and its exact pre-framework behaviour; the
  legacy include paths (`bathroom_profile.yaml`, `ventiq_profile.yaml`,
  `airiq_bathroom_base.yaml`, …) keep resolving unchanged.
* `diagnostics.yaml` was nested inside the superseded profile; the
  bundles now include it directly so the shipped surface (CPU Duty) does
  not shrink.
* **Every pre-framework published entity id is preserved** as a
  disabled-by-default compatibility entity with its exact id and name.
  Semantic upgrades (documented, deliberate):
  * the climate displays (`bathroom_temp_display`,
    `bathroom_humidity_display`) are driven by the RoomIQ **canonical
    calibrated** values, never the drifted SHT4x driver (§1.2 C1 —
    most plausibly the same physical sensor, now honestly labelled);
  * the derived displays (dew point, humidity rate, post-shower timer,
    fan speed, mould level) and the state/advice texts are driven by the
    engine (the duplicated ad-hoc formulas, including the legacy
    "Excellent" air band, are retired);
  * `bathroom_pressure_display` is the ONE exception that keeps its
    pre-framework source (the drifted BMP390 driver, which reads unknown
    on real VentIQ+RoomIQ hardware) — its disposition belongs to
    `VENTIQ-HW-DRIFT-001`;
  * the three threshold Numbers keep their ids/names/ranges and now
    actually apply (§1.2 C5); `bathroom_auto_ventilation` is preserved
    but leaves the default surface (it controls nothing physical in any
    current composition — stated plainly rather than implied).
* The board package is untouched behaviourally: raw ids stay internal,
  addresses/intervals unchanged; its legacy globals/interval logic keeps
  running for the legacy-shim products and is simply not consumed by the
  framework (the framework never reads `bathroom_shower_active` /
  `bathroom_mold_risk` / `bathroom_fan_recommendation`).

---

## 6. Evidence levels and follow-ups

Evidence levels kept separate: source inspection ✔ (this doc §1) ·
simulation ✔ (40 deterministic scenarios) · compile proof ✔/CI
(representative compile lane) · hardware validation ✘ pending
(`VENTIQ-FRAMEWORK-BENCH-001`) · customer validation ✘ pending. Bundle
composition changed for the 7 VentIQ-bearing configs; **no release
declaration changed** (`config/webflash-builds.json` untouched; no SOT,
WebFlash, Shopify, provisioning or commercial state is modified by this
PR).

Follow-up programmes created by this work item (tracked in
[`docs/sense360-roadmap-status.md`](../sense360-roadmap-status.md), not
started here):

* **`VENTIQ-FRAMEWORK-BENCH-001`** — physical validation via the
  results-free bench checklist
  ([`docs/hardware/ventiq-framework-bench-checklist.md`](../hardware/ventiq-framework-bench-checklist.md));
* **`VENTIQ-HW-DRIFT-001`** — the SHT4x/BMP390 compiled-vs-schematic
  reconciliation (§1.2 C1): land the S360-211 BOM/CPL/board-photo
  evidence (Drive artifacts retained-but-not-committed), then decide with
  owner sign-off whether the drifted drivers leave the board package (and
  what happens to the pressure compatibility entity) or a hardware
  revision adds the parts; also owns the matching
  `config/feature-entity-matrix.json` CONFIRM-flag closures;
* **`VENTIQ-RELAY-POPULATION-001`** — the fan-relay stage: crossed-out
  (do-not-populate) drawing vs the HW-007 prose describing on-board relay
  circuitry; population evidence, drive-signal source, and the existing
  COMPLIANCE-001 linkage for anything mains-facing;
* **`VENTIQ-SKU-LABEL-001`** — the `S360-BATH-B` "AirIQ Module SKU"
  diagnostic label vs the canonical `S360-211` SKU (§1.2 C2): a
  board-layer published-entity change requiring its own compatibility
  decision.

Also recorded (owned elsewhere, not duplicated here): the `J1`/`J9`
connector identity (S360-100-BENCH-001), the HW-007 doc's stale
schematic-status caveat (§1.2 C4), and SOT programme-status propagation —
an owner action in SOT, in a separate PR, never bundled here.

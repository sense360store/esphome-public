# Sense360 AirIQ framework (AIRIQ-FRAMEWORK-001)

Canonical local indoor-air-quality service for the S360-210 AirIQ board:
honest individual pollutant measurements, ONE headline **Air Quality**
state, ONE customer **Recommendation**, independent per-sensor warm-up and
freshness, and the AirIQ module runtime status — produced by one shared
engine ([`include/sense360/airiq_engine.h`](../../include/sense360/airiq_engine.h))
that is compiled into production firmware
([`packages/features/airiq_framework.yaml`](../../packages/features/airiq_framework.yaml))
and into the deterministic simulation tests
([`tests/unit/test_airiq_engine.cpp`](../../tests/unit/test_airiq_engine.cpp))
so tested logic and shipped logic cannot drift. The contract is pinned by
[`tests/test_airiq_framework.py`](../../tests/test_airiq_framework.py).

Everything in this document is **compile / simulation proof only**. No
hardware, bench, compliance, safety or commercial claim is made anywhere;
physical validation is pending
([`docs/hardware/airiq-framework-bench-checklist.md`](../hardware/airiq-framework-bench-checklist.md),
tracked as `AIRIQ-FRAMEWORK-BENCH-001`).

---

## 1. Sensor authority — what the S360-210 actually is

Established by direct audit of the primary sources: the **verified R4
schematic** `docs/hardware/schematics/S360-210-R4.pdf`
(`schematic_status: verified`, HW-008), the R4 BOM artifact record
`docs/hardware/artifacts/S360-210-R4.md`, `docs/hardware-catalog.md` +
`config/hardware-catalog.json`, `docs/hardware/s360-210-r4-airiq.md`,
`packages/boards/s360-210-airiq.yaml`, `config/feature-entity-matrix.json`,
`config/webflash-builds.json`, and SOT `products.yaml` / `bundles.yaml`.

Five layers are recorded **separately** and never conflated: (a) PCB
footprint present on the design, (b) component populated in the
production assembly, (c) external connector-supported, (d) firmware
driver compiled, (e) customer functionality available. A schematic
footprint is not population proof; a connector is not fitted hardware;
a compiled driver is not product hardware; transport liveness is not
accuracy.

### 1.1 There is no Base / Pro axis

The product taxonomy is **flat**: one SKU per product, and S360-210
"Sense360 AirIQ" is the only AirIQ SKU. No repository or SOT source defines
an "AirIQ Base" vs "AirIQ Pro" product. (Historically the legacy token
`AirIQPro` meant different things in different places — the WebFlash naming
policy collapses it to `AirIQ` while a legacy URL alias mapped it to VentIQ,
whose old name was "Bathroom Pro". None of that is a current product axis.)
This framework therefore does **not** invent a Base/Pro flag: expected-sensor
membership is configuration-driven by the `airiq_expected_*` substitutions,
so a future authoritative composition can widen the expected set without a
taxonomy change. No current composition pretends optional sensors are
present.

### 1.2 Sensor matrix — five layers recorded separately

Layers: **F** = PCB footprint present (verified schematic) · **P** =
populated in the production assembly · **X** = external
connector-supported · **D** = firmware driver compiled · **C** = customer
functionality available.

| Sensor | F (footprint) | P (populated) | X (external connector) | D (driver compiled) | C (customer functionality) | Framework treatment |
|---|---|---|---|---|---|---|
| SCD41 (CO2) | Yes — `U3` | Yes (BOM; all sources agree) | n/a | Yes — `scd4x` @0x62, 30 s | **CO2** (ppm, default) | Expected pollutant |
| SGP41 (VOC/NOx) | Yes — `U1` | Yes (BOM; all sources agree) | n/a | Yes — `sgp4x` @0x59, 30 s | **VOC**, **NOx** (relative indices, default; never concentrations) | Expected pollutants |
| SPS30 (PM1/2.5/4/10) | No (external Sensirion module) | No (off-board) | **Yes — `J2`** (5-pin JST SH; schematic sheet "SPS30") | Yes — `sps30` @0x69, 30 s | **None by default** — every PM entity (PM2.5/PM1/PM4/PM10, µg/m³) ships disabled by default; a declared composition opts in | Supported external attachment; commercial inclusion UNPROVEN (§1.5), so `expected=false` by default — an absent module never degrades health; opt-in contract for declared compositions |
| MICS-4514 + STM8 | Yes — `U4` (+ `U5` STM8S003F3U, `U6` LMV358 front-end on the MICS_SEN0321 sub-sheet) | Yes (BOM) — **PCB-mounted** | n/a | **No** — no driver; STM8 readout interface unverified (`ENTITY-FILL-210-MICS-001`) | None | Diagnostic-only engine channels; promotion gated on calibration evidence (§7) |
| SFA40 (formaldehyde) | **Yes — `U2`** with local decoupling on the shared I2C bus; the verified schematic shows **no SFA40 connector** | **Unresolved conflict**: the BOM lists `U2 = SFA40-D-R` as a populated line item, while `docs/hardware-catalog.md` and the reference doc describe a connector-attached off-board module; no CPL / silkscreen / assembly evidence exists (`HW-PINMAP-210-FOLLOWUP`) | Catalog claims a connector; none exists on the verified R4 schematic | **No** — no driver; interface unverified (`ENTITY-FILL-210-HCHO-001`) | None — no Formaldehyde entity until BOTH population and a compiled supported driver are proven | Engine contract slot, `expected=false` everywhere |
| SEN0321 (ZE27-O3 ozone) | No (external DFRobot module) | No | **Designed external input into the STM8 stage** — the verified schematic's sub-sheet and STM8 block are titled "STM8 MCU for SEN0321(ZE27-O3) and MICS-4514 to I2C"; the physical attach path is not identified on the sheet (`J4` carries the SWIM programming signals; connector mapping owed to `HW-PINMAP-210-FOLLOWUP`) | No | None | Engine contract slot only (`expected=false`); no entity, no claim |
| ZE07 (electrochemical) | No | No | No record | No | None | Not modelled; no authoritative record anywhere |
| Pressure (any part) | **No — absent from the verified schematic** (both sheets) | No — absent from the BOM and from `docs/hardware-catalog.md` | No | **Yes — `bmp3xx_i2c` @0x77, 60 s: FIRMWARE/CATALOG DRIFT** (pin-map prose and waiver text repeat the drift) | **None — pressure is not S360-210 product hardware** and is excluded from customer entities, severity, recommendation, health and product claims | Unwired engine contract channel only; the board package's internal BMP390 stays untouched pending the drift reconciliation |
| BMP581 | RoomIQ (S360-200) only — never attributed to AirIQ | — | — | No (nowhere) | None | Not an AirIQ sensor; closes the BMP390-vs-BMP581 question: the drifted compiled driver is BMP390 |

The framework changes **no compiled sensor, address or update interval**:
the board package `packages/boards/s360-210-airiq.yaml` stays the owner of
the raw (internal) sensors exactly as shipped, including the drifted
BMP390 (removing it is the drift reconciliation's decision, not this
framework's).

### 1.3 SFA40 fitment — conflict analysis (not silently resolved)

Is `docs/hardware-catalog.md` stale, is the schematic using an optional
footprint convention, or does another record resolve it?

* The **verified R4 schematic** draws `U2 = SFA40-D-Rx` as an on-board
  part with its own decoupling network on the shared I2C bus, and
  contains **no SFA40 connector at all** (the only connectors are `J2`
  SPS30, `J3` From-Core, `J4` SWIM programming). Nothing on the sheet
  marks `U2` as do-not-populate or optional.
* The **BOM** lists `U2 = SFA40-D-R` (qty 1, dedicated footprint) as an
  ordinary populated line item — and the BOM artifact record itself
  flags this as "a clarification against the standalone reference doc"
  with reconciliation owed.
* The **catalog and reference doc** ("Connectors for SPS30 PM and SFA40
  HCHO"; "sensor lives off-board") predate the schematic/BOM ingest and
  are contradicted by the connector-less verified schematic — they are
  therefore **very likely stale for SFA40**.
* **What is missing to close it**: no CPL, silkscreen, board photos or
  assembly evidence exists in the tree, so *production population* is
  still unproven. The repository has already assigned exactly this
  reconciliation to **`HW-PINMAP-210-FOLLOWUP`** (silkscreen +
  populated-board evidence, then the doc-text fix).

Consequence for this PR: the catalog is **not** edited here (governance:
the catalog is the canonical naming source and the artifact record
explicitly routes the fitment/doc correction through
`HW-PINMAP-210-FOLLOWUP` with physical evidence). The framework treats
SFA40 as footprint-present / population-unresolved / driver-absent, and
no Formaldehyde entity may appear until both population and a compiled
supported driver are proven.

### 1.5 SPS30 inclusion audit — is the external module actually supplied?

A `J2` connector and a compiled driver do not prove that an external
module is physically supplied. Six layers audited separately for SPS30:

1. **S360-210 connector capability** — yes (`J2`, verified schematic).
2. **Driver compiled** — yes (`sps30` @0x69 in the board package).
3. **Physically fitted to the PCB** — no (external module by design).
4. **Supplied in a commercial kit** — **UNPROVEN.** The kit records
   (`config/room-bundle-skus.json` `included_board_skus`,
   `config/kit-intent-matrix.json`) enumerate **board SKUs only**
   (S360-100/200/210/410) with no SPS30 line item; **no SPS30 SKU exists
   anywhere in the hardware catalog**; SOT `products.yaml` /
   `bundles.yaml` never name SPS30 (their PM-monitoring prose is
   CONFIRM-flagged and self-contradictory — e.g. "CO2 optional at
   checkout" despite the PCB-mounted SCD41); the WebFlash
   module-requirements matrix explicitly lists "SPS30 connector
   (particulate matter, **optional**)"; and this repository's roadmap
   doctrine reserves the catalog's "Connectors for …" phrasing "for
   genuinely optional attachments (AirIQ: SPS30, SFA40)". The
   `HW-AIRIQ-WAIVER-2026-06` text naming SPS30 in the "sensor-stack" is
   a compiled-firmware statement, not fitment proof — the same sentence
   names the drifted BMP390.
5. **Expected by firmware health** — therefore **opt-in**:
   `airiq_expected_pm` defaults `"false"`; an absent SPS30 never
   degrades AirIQ health; a composition that declares the attachment
   sets it `"true"`, after which a missing/stale module degrades
   honestly while useful service remains (simulation-tested).
6. **PM entities customer-visible** — therefore **disabled by default**
   everywhere; the opt-in for a declared composition is
   `airiq_expected_pm: "true"` plus re-enabling the PM entities
   (`!extend s360_pm2_5` → `disabled_by_default: false`) in that bundle.

**Product/SOT follow-up required to declare a fitted attachment**
(`AIRIQ-SPS30-INCLUSION-001`, recorded in the roadmap): add an explicit
SPS30 attachment line item (its own SKU or kit content entry) to the
kit/SOT records for any composition that ships the module, then flip
that bundle's opt-in contract. A firmware driver never creates a
commercial decision.

### 1.3 Pre-framework customer surface (compatibility baseline)

The shipped AirIQ bundles exposed **no pollutant measurements at all**:
every board sensor is `internal: true`, and the only published AirIQ
entities were the `air_quality_state` text sensor (a placeholder that always
read "unknown"), the diagnostic module SKU/status entities, and an MQTT
block wired to (empty-by-default) substitutions. See §8 for how that
surface is preserved.

---

## 2. Customer experience

Default-enabled entities (the ONLY default-enabled set):

| Entity | id | Unit / values |
|---|---|---|
| CO2 | `s360_co2` | ppm |
| VOC | `s360_voc` | relative index (unitless by design) |
| NOx | `s360_nox` | relative index (unitless by design) |
| Air Quality | `s360_air_quality` | Initialising / Good / Fair / Poor / Very poor / Unavailable |
| Recommendation | `s360_recommendation` | Sensor initialising / No action needed / Ventilate soon / Ventilate now / Check pollution source / Unavailable |

Available but disabled by default (standard sensors, not diagnostics):
**PM2.5** (`s360_pm2_5`), **PM1** (`s360_pm1`), **PM4** (`s360_pm4`),
**PM10** (`s360_pm10`) — the SPS30 is an external attachment whose
commercial inclusion is unproven (§1.5), so no PM entity is
default-enabled anywhere; a customer with an attached module can enable
PM2.5 manually, and a future SPS30-declared composition enables it (and
expects the sensor) via the documented opt-in contract.

There is deliberately **no pressure entity of any kind**: pressure is not
S360-210 product hardware (§1.2), and the compiled BMP390 is
firmware/catalog drift whose readings stay internal at the board layer.

There is deliberately **no AQI entity**: no recognised jurisdictional AQI
standard is implemented, so none is claimed. There is no blended score, no
per-pollutant threshold control farm, and no single opaque "sensitivity"
control. Formaldehyde and ozone entities do not exist in any current
composition (owner decision 7: optional sensors are never pretended
present).

### 2.1 The strongest simpler alternative (adopted)

The evaluated alternative — expose formaldehyde, ozone and MiCS-derived CO /
NO2 immediately — was rejected in favour of the smaller surface above:
CO2 + VOC + NOx + PM2.5 + headline + recommendation delivers most of the
customer value with none of the unresolved calibration burden, no
Base-style/Pro-style leakage risk (nothing unfitted is shown), a small
entity count, lower support burden and trivial rollback. The wider set
stays available through engine contract slots that activate only with
authoritative evidence, so reducing the default surface now costs nothing
later. Strongest counterargument: shipping the gas slots immediately would
surface more of the BOM's sensors — but with an unverified STM8 interface
and conflicted SFA40 fitment that would be false precision, not value.

---

## 3. Worst-pollutant model (severity)

Each participating pollutant maps deterministically to a severity —
**Good / Fair / Poor / Very poor** (plus Initialising / Unavailable for its
freshness state). The headline **Air Quality** is the worst severity among
the *expected, fresh* pollutants:

* one severe pollutant is never averaged away (no blended score);
* stale data never counts as good — a stale channel drops out of the
  headline and degrades module health instead;
* an optional (not expected) sensor never influences headline or health;
* if every expected channel is still warming: **Initialising**;
* if some are ready and others warming: an honest partial headline from
  the ready channels (module status Initialising until warm-up resolves,
  Degraded if an expected channel goes missing after warm-up);
* if no usable pollutant data exists: **Unavailable**.

Participants by default: CO2, VOC, NOx (the PCB-mounted compiled
sensors). PM2.5 participates only in a composition that declares the
external SPS30 attachment (§1.5) — none does today — and the
formaldehyde / ozone contract slots only when a future composition
expects them. **Pressure never participates.** RoomIQ temperature / humidity / illuminance are never mixed
into pollutant severity (Comfort is not Air Quality and the two are never
merged).

### 3.1 Provisional thresholds (fair / poor / very-poor lower bounds)

All values are **provisional engineering thresholds** — indoor-air-quality
heuristics pending bench and customer validation. They are never medical
or regulatory claims. They are centralised in the engine defaults and the
framework substitutions; downstream consumers must never duplicate them.

| Pollutant | Good < | Fair | Poor | Very poor ≥ | Hysteresis | Basis |
|---|---|---|---|---|---|---|
| CO2 (ppm) | 800 | 800–1000 | 1000–1500 | 1500 | 50 | accepted owner comfort/ventilation bands — not health limits |
| VOC (index) | 150 | 150–250 | 250–400 | 400 | 10 | relative-index heuristic informed by Sensirion's published guidance (100 = learning-phase average); no concentration conversion is invented |
| NOx (index) | 100 | 100–200 | 200–300 | 300 | 10 | relative-index heuristic (NOx index baseline is 1; values above ~100 indicate elevated NOx) |
| PM2.5 (µg/m³) | 12 | 12–35.5 | 35.5–55.5 | 55.5 | 3 | derived from published US EPA PM2.5 breakpoints, used as provisional indoor heuristics only — explicitly NOT a regulatory AQI implementation and not a compliance statement |
| Formaldehyde (ppb, contract slot) | 80 | 80–120 | 120–250 | 250 | 10 | provisional bands referencing the WHO indoor guideline magnitude (~81 ppb); inactive in every current composition |
| Ozone (ppb, contract slot) | 50 | 50–70 | 70–120 | 120 | 5 | provisional bands; inactive in every current composition |

Worsening classifies immediately (a severe pollutant must show at once);
improvement requires clearing the band boundary by the hysteresis margin so
states never flap at a boundary.

---

## 4. Recommendation model

Deterministic, explainable, local-only (works with no internet access), and
conservative — outdoor air quality is unknown, so no absolute health advice
is ever produced. Mapping:

| Situation | Recommendation |
|---|---|
| Every expected channel still warming | Sensor initialising |
| No usable pollutant data | Unavailable |
| Headline Good or Fair | No action needed |
| Headline Poor, worst driver is CO2 / VOC / NOx | Ventilate soon |
| Headline Very poor, worst driver is CO2 / VOC / NOx | Ventilate now |
| Headline Poor / Very poor, worst driver is PM2.5 (or a gas slot) | Check pollution source |

Rationale (documented trade-off): ventilation demonstrably reduces CO2,
VOC and NOx indoors, so those drive ventilation advice. For particulates
the outdoor air may itself be the source, so unconditional ventilation
advice would be dishonest — the customer is asked to check the pollution
source (filtration may help; that judgement is theirs). The same
conservative wording covers the formaldehyde / ozone slots. Ties at the
same severity are broken by a fixed priority order (CO2, VOC, NOx, PM2.5,
Formaldehyde, Ozone); if any ventilation-responsive pollutant sits at the
worst severity, ventilation advice wins. The
`s360_airiq_recommendation_reason` diagnostic states the worst pollutant
and severity behind every recommendation.

---

## 5. Warm-up and freshness (per sensor, never shared)

Each sensor is tracked independently — there is deliberately no single
arbitrary warm-up period:

| Channel | Warm-up (data availability) | Stale window | Note |
|---|---|---|---|
| CO2 (SCD41) | 60 s | 90 s (3 × 30 s updates) | warm-up covers first-data delivery only — never an accuracy claim |
| VOC (SGP41) | 120 s | 90 s | the SGP41 runs conditioning and its index keeps adapting its baseline for much longer; that is documented, not hidden |
| NOx (SGP41) | 120 s | 90 s | as VOC |
| PM (SPS30) | 60 s | 90 s | fan spin-up / first measurement |
| Pressure | n/a (no producer — unwired drift contract) | 180 s (engine default) | never severity/health; no entity, no production wiring |
| MiCS channels | n/a (no producer) | 90 s | diagnostic contract only |

A channel is Initialising until its first valid sample (or its warm-up
window expires), Fresh while valid updates arrive inside the stale window,
and unusable (values go unknown, never frozen) otherwise. A NaN or negative
sample is an invalid update and never refreshes a channel.

---

## 6. Module health

Uses the Core-Framework reserved vocabulary
(`config/core-framework.json module_runtime_status.airiq` — the third wired
module after Presence and RoomIQ), over the **expected** channels only —
by default the PCB-mounted compiled sensors (CO2, VOC, NOx); a declared
external attachment (e.g. SPS30 in a future opted-in composition, §1.5)
joins the expected set and then degrades honestly when missing:

* **Initialising** — expected channels inside valid warm-up windows;
* **Available** — every expected channel fresh after warm-up (data-service
  availability only: never accuracy, calibration correctness or hardware
  health);
* **Degraded** — at least one expected channel unavailable/stale while a
  useful air-quality service remains (honest partial headline);
* **Unavailable** — no usable pollutant measurements remain;
* **Fault** — reserved engine contract; no composed component exposes a
  supported fault signal today, and ordinary staleness never produces it.

A composition is never degraded by sensors it does not expect (owner
decision: optional absence is normal, not a failure), and transport
liveness is never presented as gas accuracy. Pressure and the MiCS
channels are excluded from health while their reconciliations are open.

---

## 7. MiCS-4514 treatment and promotion gate

MiCS-4514 (+ its STM8 co-processor) is on the S360-210 BOM and is part of
this architecture — it is deliberately not ignored. Facts: no ESPHome
driver exists in the tree, the STM8 readout interface (I2C address,
register map, heater control) is unverified, and no calibration evidence
exists (`ENTITY-FILL-210-MICS-001`; the PACKAGE-AIRIQ-001 operator bench
proof container is retired/empty).

Posture in this slice:

* the engine carries **diagnostic-only** reducing / oxidising channels
  (`input_mics_reducing` / `input_mics_oxidising`, freshness-gated,
  simulation-tested) so the downstream contract is stable;
* **no production input exists** (nothing is wired in YAML — there is no
  driver to wire) and no entity is exposed;
* **no customer CO / NO2 / ppm value is claimed anywhere**, no historical
  approximate output is treated as a reference-grade measurement, and no
  confidence number is fabricated.

Promotion of a MiCS-derived pollutant into the customer set requires ALL
of: (1) the STM8 interface confirmed from the schematic and exercised on
hardware; (2) heater warm-up and baseline (R0) capture characterised;
(3) calibration against reference instrumentation with documented formulas
and error bounds; (4) an owner decision accepting the resulting claim
wording. Tracked as follow-up work (§10) — it is explicitly out of scope
for this PR.

---

## 8. Compatibility

* `air_quality_state` (name "… Air Quality State") — the only published
  pre-framework customer entity — keeps its exact id and name. **Semantic
  upgrade (documented):** it previously always read "unknown" (a
  placeholder; "no IAQ sensor configured"); it now publishes the canonical
  headline vocabulary. It ships disabled by default for new installs (the
  canonical "Air Quality" replaces it); existing Home Assistant
  registrations and automations keep resolving.
* The legacy **MQTT block** (broker/port/username/password substitutions,
  `discovery: false`, `${device_name}/air_quality` topic prefix) moves
  verbatim from the superseded `airiq_basic_profile.yaml` into the
  framework package, so the shipped capability surface does not shrink and
  customer substitution overrides keep working.
* The legacy include paths (`airiq_basic_profile.yaml`,
  `airiq_mqtt_profile.yaml`, `airiq_ceiling.yaml`, …) keep resolving with
  exact pre-framework behaviour for the legacy shim products and
  compile-only skeletons that pin them. Bundles compose the framework
  INSTEAD of the profile (composing both would duplicate the
  `air_quality_state` id and the MQTT block — enforced by contract test).
* All board sensor ids (`airiq_co2`, `airiq_voc_index`, `airiq_nox_index`,
  `airiq_pm*`, `airiq_pressure`) are unchanged and stay internal; no
  published entity is removed or renamed; no duplicate CO2 / VOC / NOx /
  PM entities exist in any composition.

---

## 9. Platform reuse and RoomIQ integration

* **AirIQ owns pollutant interpretation for the whole platform.** VentIQ,
  Pure, Zones, Home Assistant dashboards and future mobile applications
  consume `s360_co2` / `s360_voc` / `s360_nox` / `s360_pm2_5` /
  `s360_air_quality` / `s360_recommendation` (and the engine's severity
  API) instead of duplicating thresholds. The engine's input sources and
  expected flags are substitutions, so a future VentIQ composition can
  feed its SGP41 through the same engine rather than a second model.
* **RoomIQ reuse audit:** the SGP41 temperature/humidity compensation
  stays SCD41-sourced at the board layer — it is on-module, present in
  every AirIQ composition (RoomIQ may be absent), and changing the
  compiled compensation source is out of scope. AirIQ never re-reads raw
  RoomIQ sensors, and RoomIQ Comfort is never merged into Air Quality.
  Future recommendation refinements that want canonical RoomIQ
  temperature/humidity would consume `s360_temperature` / `s360_humidity`
  (the canonical ids), never the raw board sensors.
* Nothing unrelated (fan control, light, occupancy) is centralised here.
* **Sensor reconciliations stay open and tracked**: the BMP390
  firmware/catalog drift (compiled driver for hardware the verified
  schematic / BOM / catalog do not contain), SFA40 population
  (`HW-PINMAP-210-FOLLOWUP`, §1.3), the STM8 readout path, and the
  SEN0321 (ZE27-O3) external ozone input (named on the verified schematic
  but with no identified attach connector and no driver; ZE07 has no
  record anywhere). If an ozone module ships, its exact gas and unit must
  come from authoritative sources first, never guessed from the module
  family name.

---

## 10. Evidence levels and follow-ups

Evidence levels kept separate (accepted owner decision 10): source
inspection ✔ (this doc §1) · simulation ✔ (37 deterministic scenarios) ·
compile proof ✔/CI (representative compile lane) · hardware validation ✘
pending (`AIRIQ-FRAMEWORK-BENCH-001`) · customer validation ✘ pending.

Follow-ups created by this work item (tracked, not started):

* `AIRIQ-FRAMEWORK-BENCH-001` — physical validation via the results-free
  bench checklist;
* MiCS-4514 calibration / promotion programme (§7) — separate programme
  recommended;
* `AIRIQ-SPS30-INCLUSION-001` — the product/SOT declaration follow-up for
  the external SPS30 attachment (§1.5): an explicit kit/SOT line item for
  any composition that ships the module, then that bundle's opt-in flip;
* BMP390 firmware/catalog drift reconciliation — decide (with owner
  sign-off) whether the drifted `bmp3xx_i2c` driver leaves the board
  package or a pressure part is added to a future hardware revision;
  until then no pressure product claim exists;
* `HW-PINMAP-210-FOLLOWUP` — SFA40 population evidence (silkscreen /
  CPL / board photos), the `J*` connector-to-sensor mapping and the
  SEN0321 attach path; **it also owns the directly evidenced correction
  of the stale `docs/hardware-catalog.md` / reference-doc SFA40
  "connector" wording** (deliberately not edited in this PR — the
  catalog is the canonical naming source and repository governance
  routes fitment corrections through that follow-up with physical
  evidence);
* SFA40 interface + driver work after fitment resolves
  (`ENTITY-FILL-210-HCHO-001`);
* ozone module productisation, if ever, via the schematic's SEN0321
  (ZE27-O3) external input — identity/unit confirmation first;
* customer threshold tuning from bench + customer feedback;
* VentIQ consumption of the canonical engine; Pure consumption when that
  product programme starts.

SOT programme-status propagation (AirIQ software foundation implemented)
is an owner action in SOT, in a separate PR — never bundled here.

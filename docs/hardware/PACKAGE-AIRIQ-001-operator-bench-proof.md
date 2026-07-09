# PACKAGE-AIRIQ-001 — Sense360 AirIQ Operator Bench Proof

**Programme:** `KITCHEN-BUNDLE-PROMOTE-001` (tracking:
[`docs/kitchen-bundle-promote-001.md`](../kitchen-bundle-promote-001.md))

**Status: PENDING — awaiting bench. No step has been run; no evidence has
been recorded. Every capture cell and the operator attestation below are
intentionally empty.**

| Field | Value |
|---|---|
| Board under proof | Sense360 AirIQ, SKU **S360-210**, rev R4 (ceiling air-quality module) plus its off-board SPS30 particulate module |
| Sensor stack proven | SPS30 (PM₁ / PM₂.₅ / PM₄ / PM₁₀), SGP41 (VOC index / NOₓ index), SCD41 (CO₂ + temp/RH), BMP390 (pressure + temp) |
| Bench firmware | The served **`Ceiling-POE-AirIQ-RoomIQ`** build ([`products/sense360-ceiling-poe-airiq-roomiq.yaml`](../../products/sense360-ceiling-poe-airiq-roomiq.yaml)) — released artifact or locally compiled at a recorded `main` SHA |
| Target config(s) | `Ceiling-POE-AirIQ-RoomIQ` |
| Promotion channel | **stable** (the config is already served stable; this proof supplies the hardware evidence behind it) |
| Promotion unlocked | Kitchen bundle SKU **S360-KIT-KITCHEN-P** stable-candidate → stable-release in [`config/room-bundle-skus.json`](../../config/room-bundle-skus.json), clearing gate `G8-AirIQ-stack-hardware-evidence-SPS30-SGP41-SCD41-BMP390` |
| Attestation rule | **Section F is owner-authored only.** Agents never author, edit, complete, or summarise attestation content or any capture-table measurement. This file ships with those cells empty; only the owner fills them, at the bench, in their own words. |

**Type:** operator-evidence record. Docs only. This file asserts no firmware,
catalog, manifest, release, or WebFlash change. Completing it is the
bench-evidence precondition for the Kitchen bundle promotion PR (step K2 of
the programme — a separate, human-reviewed change); it promotes nothing by
itself. It makes no safety / EMC / compliance claim. It covers the **AirIQ
sensor-stack evidence gate only** — the two S360-410 PoE-PSU evidence gates
(`G8-PRODUCT-POE-410-001`, `G8-S360-410-schematic-status-verified`) are
separate and are not automatically cleared by this proof. Bench observations
recorded here should also feed the open **verify** items in
[`s360-210-r4-airiq.md`](s360-210-r4-airiq.md) where they overlap (SPS30
connector interface, J9 pin order) — that record stays the source of truth
for those specific questions.

---

## Hardware under test

| Item | Value |
|---|---|
| Core | S360-100-R4 (serial / rev: ____) |
| AirIQ module | S360-210-R4 (serial / rev: ____) |
| SPS30 module | Off-board Sensirion SPS30 (serial: ____) on the AirIQ SPS30 connector |
| RoomIQ module | S360-200-R4 (serial / rev: ____) — present because the config under test is AirIQ + RoomIQ |
| Data path | AirIQ on Core `J9` (shared I²C bus `core_i2c`); SPS30 via the AirIQ SPS30 connector |
| Power | PoE via S360-410 (serial / rev: ____) |
| Reference instruments (if any) | CO₂ / PM / pressure reference or ambient expectation (record: ____) |

---

## Procedure and capture — fill each row at the bench

### Step A — Identity

| Capture | Value |
|---|---|
| AirIQ board serial / marking (S360-210) | |
| Core serial / marking (S360-100) | |
| Firmware flashed (released artifact version, or `main` SHA if locally compiled) | |
| ESPHome version used (if locally compiled) | |
| Date | |

**Step A result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

### Step B — Boot / read sanity

All four sensors must initialise at power-on with no I²C errors in the log,
and report a first reading within a plausible range (per the Step C tables)
within a few minutes of boot.

| Capture | Expected | Observed |
|---|---|---|
| Boot log clean (no I²C errors / sensor init failures) | clean | |
| SPS30 reporting after boot | first PM reading within ~1 min | |
| SGP41 reporting after boot | VOC/NOₓ indices after warm-up (~1 min conditioning) | |
| SCD41 reporting after boot | first CO₂ reading within ~1 min | |
| BMP390 reporting after boot | pressure + temp within ~1 min | |

**Step B result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

### Step C — Per-sensor plausibility

Each sensor's reading sanity-checked against a known reference or an ambient
expectation. Record the reference used (instrument, or "ambient expectation").

#### C.1 — SPS30 particulate matter

| Capture | Expected | Observed |
|---|---|---|
| PM₂.₅ at clean ambient | plausible indoor ambient (typically < 35 µg/m³) | |
| PM₁ / PM₄ / PM₁₀ ordering | PM₁ ≤ PM₂.₅ ≤ PM₄ ≤ PM₁₀ | |
| Response to a brief particulate stimulus (record which, e.g. extinguished match nearby) | clear rise, then decay back toward ambient | |
| Reference used | | |

**C.1 result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

#### C.2 — SGP41 VOC / NOₓ index

| Capture | Expected | Observed |
|---|---|---|
| VOC index at clean ambient (after warm-up) | settles near baseline (~100 on the 1–500 index) | |
| NOₓ index at clean ambient (after warm-up) | settles near baseline (~1 on the 1–500 index) | |
| Response to a brief VOC stimulus (record which, e.g. alcohol wipe nearby) | clear VOC-index rise, then decay | |
| Reference used | | |

**C.2 result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

#### C.3 — SCD41 CO₂

| Capture | Expected | Observed |
|---|---|---|
| CO₂ at ambient | plausible indoor ambient (~400–1500 ppm) | |
| Response to exhaled breath near the sensor | clear rise, then decay toward ambient | |
| SCD41 temperature vs ambient reference | plausible (within a few °C) | |
| SCD41 humidity vs ambient reference | plausible | |
| Reference used | | |

**C.3 result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

#### C.4 — BMP390 pressure / temperature

| Capture | Expected | Observed |
|---|---|---|
| Absolute pressure vs local expectation | plausible for site altitude (typically ~950–1050 hPa) | |
| BMP390 temperature vs ambient reference | plausible (within a few °C) | |
| Reference used | | |

**C.4 result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

### Step D — Stability

Values stable / non-drifting over a short observation window at steady
ambient; no stuck (never-changing) and no wildly oscillating readings.

| Capture | Expected | Observed |
|---|---|---|
| Observation window | ≥ 30 min at steady ambient (record duration) | |
| SPS30 PM₂.₅ over the window | stable, no stuck value, no runaway drift | |
| SGP41 VOC/NOₓ over the window | stable near baseline, still updating | |
| SCD41 CO₂ over the window | stable, tracks room occupancy plausibly | |
| BMP390 pressure over the window | stable (weather-scale drift only) | |

**Step D result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

### Step E — Soak

A period powered with zero reboots and all four sensors still reporting at
the end.

| Capture | Expected | Observed |
|---|---|---|
| Soak duration | record (target ≥ 24 h; record actual) | |
| Reboots (check HA uptime sensor) | zero | |
| All four sensors still reporting at end | yes | |
| Anomalies | none | |

**Step E result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

---

## Step F — Operator attestation

> **To be completed by the owner only, at the bench, in their own words:**
> what was tested, what was observed, and whether the AirIQ sensor stack is
> fit to back the Kitchen bundle's promotion to **stable-release**. The entry
> cells below are intentionally empty — no attestation content is
> machine-written, ever. The Kitchen bundle promotion PR (K2) may only be
> opened when Steps A–E are all recorded PASS above and this section
> contains non-empty owner-authored text.

| Field | Entry |
|---|---|
| Operator | |
| Date | |
| Units under test | |
| Statement | |
| Signature | |

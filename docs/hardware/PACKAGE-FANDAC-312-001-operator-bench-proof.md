# PACKAGE-FANDAC-312-001 — Sense360 DAC Operator Bench Proof

**RETIRED — informational only, superseded by owner declaration
(HW-RELEASE-001, [`docs/hw-release-001.md`](../hw-release-001.md)). This
template is no longer a release gate; its capture cells and attestation
remain intentionally empty and no evidence was or will be recorded here.**

**Programme:** `BENCH-VALIDATION-001` (tracking:
[`docs/bench-validation-001.md`](../bench-validation-001.md))

**Status: PENDING — awaiting bench. No step has been run; no evidence has
been recorded. Every capture cell and the operator attestation below are
intentionally empty.**

| Field | Value |
|---|---|
| Board under proof | Sense360 DAC, SKU **S360-312**, rev R4 (0–10 V analog fan driver, two GP8403 dual-channel I²C DACs) |
| Bench firmware | Locally compiled **`Ceiling-POE-FanDAC`** ([`products/sense360-ceiling-poe-fandac.yaml`](../../products/sense360-ceiling-poe-fandac.yaml)) at a recorded `main` SHA |
| Target config(s) on promotion | `Ceiling-POE-FanDAC`, `Ceiling-POE-VentIQ-FanDAC-RoomIQ`, `Ceiling-POE-AirIQ-FanDAC-RoomIQ` |
| Promotion channel | **preview** (low-voltage board) |
| Equipment | Multimeter **required** for every voltage capture |
| Attestation rule | **Section F is owner-authored only.** Agents never author, edit, complete, or summarise attestation content or any capture-table measurement. This file ships with those cells empty; only the owner fills them, at the bench, in their own words. |

**Type:** operator-evidence record. Docs only. This file asserts no firmware,
catalog, manifest, release, or WebFlash change. Completing it is the
bench-evidence precondition for the board's promotion PR (a separate,
human-reviewed change); it promotes nothing by itself. It makes no
safety / EMC / compliance claim.

> **`FANDAC-I2C-ADDR-001` interaction.** The two room-bundle target configs
> (`Ceiling-POE-VentIQ-FanDAC-RoomIQ`, `Ceiling-POE-AirIQ-FanDAC-RoomIQ`)
> additionally owe the GP8403 I²C address bench verification — IC1 `0x58`,
> IC2 relocated to `0x5A`, and **no GP8403 at `0x59`** when VentIQ/AirIQ is
> present (SGP41 collision). That evidence has its own checklist and
> template in
> [`fandac-i2c-address-verification.md`](fandac-i2c-address-verification.md)
> and should be completed at the same bench sitting; this proof does not
> duplicate it.

---

## Hardware under test

| Item | Value |
|---|---|
| Core | S360-100-R4 (serial / rev: ____) |
| DAC module | S360-312-R4 (serial / rev: ____) |
| DACs | GP8403 ×2 — IC1 (`SW1`, default `0x58`) → J2 VOUT0/VOUT1; IC2 (`SW2`, default `0x59`) → J3 VOUT0/VOUT1 |
| I²C bus | Shared `core_i2c` — SDA `GPIO48`, SCL `GPIO45` (CORE-ABSTRACT-BUS-001B) |
| Output range | 0–10 V (firmware register-driven, `voltage: "10V"` per chip) |
| Test fan | EC/DC fan with 0–10 V input (make / model: ____) |
| Meter | (make / model: ____) |
| Power | PoE via S360-410 (serial / rev: ____) |

---

## Procedure and capture — fill each row at the bench

### Step A — Identity

| Capture | Value |
|---|---|
| Board serial / marking (S360-312) | |
| Core serial / marking (S360-100) | |
| DIP positions as found (SW1 / SW2) | |
| Firmware `main` SHA compiled | |
| ESPHome version used | |
| Date | |

**Step A result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

### Step B — Boot safety

DAC output must read 0 V at power-on, after reset, and during OTA.
Measure with the meter on the output under test.

| Capture | Expected | Measured |
|---|---|---|
| Output at power-on (cold boot) | 0 V | |
| Output after software reset | 0 V | |
| Output during an OTA update cycle | 0 V (no transient) | |

**Step B result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

### Step C — Output accuracy

Command each set-point from Home Assistant; measure the DAC output with the
meter. Record the tolerance you applied.

| Commanded | Expected | Measured | Within tolerance (state it: ____) |
|---|---|---|---|
| 0% | 0 V | | |
| 25% | 2.5 V | | |
| 50% | 5 V | | |
| 75% | 7.5 V | | |
| 100% | 10 V | | |

**Step C result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

### Step D — Real fan response

Connected EC/DC fan follows the command curve; tach feedback (if fitted)
reports plausible RPM at two set-points.

| Capture | Expected | Observed |
|---|---|---|
| Fan follows the 0→100% curve | speed tracks the set-point | |
| Set-point 1 (record %) — RPM if tach fitted | plausible | |
| Set-point 2 (record %) — RPM if tach fitted | plausible | |
| Tach fitted? | record yes / no | |

**Step D result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

### Step E — Failsafe + soak

| Capture | Expected | Observed |
|---|---|---|
| HA disconnect: output behaviour | holds or falls to safe state as designed — **document which** | |
| Wi-Fi drop: output behaviour | holds or falls to safe state as designed — **document which** | |
| Soak duration | ≥ 24 h | |
| Reboots during soak (HA uptime sensor) | zero | |

**Step E result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

---

## Step F — Operator attestation

> **To be completed by the owner only, at the bench, in their own words:**
> what was tested, what was observed, and whether the board is fit to
> promote to **preview**. The entry cells below are intentionally empty —
> no attestation content is machine-written, ever. A promotion PR for this
> board may only be opened when Steps A–E are all recorded PASS above and
> this section contains non-empty owner-authored text.

| Field | Entry |
|---|---|
| Operator | |
| Date | |
| Units under test | |
| Statement | |
| Signature | |

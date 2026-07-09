# PACKAGE-FANPWM-311-001 — Sense360 PWM Operator Bench Proof

**Programme:** `BENCH-VALIDATION-001` (tracking:
[`docs/bench-validation-001.md`](../bench-validation-001.md))

**Status: PENDING — awaiting bench. No step has been run; no evidence has
been recorded. Every capture cell and the operator attestation below are
intentionally empty.**

| Field | Value |
|---|---|
| Board under proof | Sense360 PWM, SKU **S360-311**, rev R4 (12 V PWM fan driver, up to 4 fans with tach feedback) |
| Bench firmware | Locally compiled **`Ceiling-POE-FanPWM`** ([`products/sense360-ceiling-poe-fanpwm.yaml`](../../products/sense360-ceiling-poe-fanpwm.yaml)) at a recorded `main` SHA |
| Target config(s) on promotion | `Ceiling-POE-FanPWM`, `Ceiling-POE-VentIQ-FanPWM-RoomIQ`, `Ceiling-POE-AirIQ-FanPWM-RoomIQ` |
| Promotion channel | **preview** (low-voltage board) |
| Attestation rule | **Section F is owner-authored only.** Agents never author, edit, complete, or summarise attestation content or any capture-table measurement. This file ships with those cells empty; only the owner fills them, at the bench, in their own words. |

**Type:** operator-evidence record. Docs only. This file asserts no firmware,
catalog, manifest, release, or WebFlash change. Completing it is the
bench-evidence precondition for the board's promotion PR (a separate,
human-reviewed change); it promotes nothing by itself. It makes no
safety / EMC / compliance claim.

> **Tach path note.** The shipping FanPWM driver
> ([`packages/expansions/fan_pwm_native.yaml`](../../packages/expansions/fan_pwm_native.yaml))
> reads tach on **native ESP32-S3 `pulse_counter` inputs** — `Pul_Cou1` →
> `IO17`, `Pul_Cou2` → `IO18`, `Pul_Cou4` → `IO9` (`Pul_Cou3` → `IO46` is
> deliberately disabled pending the `fan_status_led_pin` reconciliation).
> The legacy SX1509 pulse path is superseded and is **not** what this bench
> exercises (tach inputs must not use the SX1509, per
> [`s360-100-native-fan-gpio-map.md`](s360-100-native-fan-gpio-map.md)).
> The pulse-counter readings are internal diagnostic pulse-rate values —
> firmware surfaces no RPM entity today; Step D captures the observed
> pulse-rate / derived RPM plausibility from logs or diagnostics (this is
> the measured evidence PWM-13 has been waiting on).

---

## Hardware under test

| Item | Value |
|---|---|
| Core | S360-100-R4 (serial / rev: ____) |
| PWM module | S360-311-R4 (serial / rev: ____) |
| PWM drive | Native `ledc` — `TachPMW1..4` → `IO10` / `IO11` / `IO12` / `IO39` (fan connectors J1 / J2 / J4 / J5) |
| Tach inputs | Native `pulse_counter` — `Pul_Cou1` → `IO17`, `Pul_Cou2` → `IO18`, `Pul_Cou4` → `IO9` (`Pul_Cou3` disabled) |
| Test fan(s) | 12 V PWM fan with tach (make / model, channel used: ____) |
| Power | PoE via S360-410 (serial / rev: ____); 12 V supply for fans (source: ____) |

---

## Procedure and capture — fill each row at the bench

### Step A — Identity

| Capture | Value |
|---|---|
| Board serial / marking (S360-311) | |
| Core serial / marking (S360-100) | |
| Fan channel(s) exercised (J1 / J2 / J4 / J5) | |
| Firmware `main` SHA compiled | |
| ESPHome version used | |
| Date | |

**Step A result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

### Step B — Boot safety

PWM output must be at 0% duty at power-on, after reset, and during OTA
(fan does not spin uncommanded).

| Capture | Expected | Observed |
|---|---|---|
| Output at power-on (cold boot) | 0% duty — fan off | |
| Output after software reset | 0% duty — fan off | |
| Output during an OTA update cycle | 0% duty — no transient spin | |

**Step B result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

### Step C — Duty control

Command each set-point from Home Assistant; fan speed visibly or
tach-measurably tracks. Document the minimum-spin behaviour at low duty.

| Commanded | Expected | Observed (visible / tach) |
|---|---|---|
| 0% | fan stopped | |
| 25% | spinning, slow | |
| 50% | tracks | |
| 75% | tracks | |
| 100% | full speed | |

| Capture | Observed |
|---|---|
| Minimum duty at which the fan reliably spins | |
| Behaviour below that duty (stall / hum / stop) | |

**Step C result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

### Step D — Tach

Pulse-rate reported at two set-points via the native `pulse_counter`
inputs, plausible values captured (see the tach path note above — no RPM
entity is surfaced; capture from logs / diagnostics and record how the
value was read).

| Capture | Expected | Observed |
|---|---|---|
| Set-point 1 (record %) — pulse-rate / derived RPM | plausible for the fan | |
| Set-point 2 (record %) — pulse-rate / derived RPM | plausible, scales with duty | |
| How the value was read (log / diagnostic) | record | |

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

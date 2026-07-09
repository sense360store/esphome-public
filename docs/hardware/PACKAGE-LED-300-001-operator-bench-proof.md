# PACKAGE-LED-300-001 — Sense360 LED Operator Bench Proof

**Programme:** `BENCH-VALIDATION-001` (tracking:
[`docs/bench-validation-001.md`](../bench-validation-001.md))

**Status: PENDING — awaiting bench. No step has been run; no evidence has
been recorded. Every capture cell and the operator attestation below are
intentionally empty.**

| Field | Value |
|---|---|
| Board under proof | Sense360 LED, SKU **S360-300**, rev R4 (low-voltage WS2812B LED ring) |
| Bench firmware | Locally compiled **`Ceiling-POE-RoomIQ-LED`** ([`products/sense360-ceiling-poe-roomiq-led.yaml`](../../products/sense360-ceiling-poe-roomiq-led.yaml)) at a recorded `main` SHA |
| Target config(s) on promotion | `Ceiling-POE-RoomIQ-LED` |
| Promotion channel | **preview** (low-voltage board) |
| Attestation rule | **Section F is owner-authored only.** Agents never author, edit, complete, or summarise attestation content or any capture-table measurement. This file ships with those cells empty; only the owner fills them, at the bench, in their own words. |

**Type:** operator-evidence record. Docs only. This file asserts no firmware,
catalog, manifest, release, or WebFlash change. Completing it is the
bench-evidence precondition for the board's promotion PR (a separate,
human-reviewed change); it promotes nothing by itself. It makes no
safety / EMC / compliance claim. Bench observations recorded here should
also close the open `S360-300-BENCH-001` questions in
[`s360-300-r4-led.md`](s360-300-r4-led.md) where they overlap (harness rail,
LED count, harness identity) — that record stays the source of truth for
those specific questions.

---

## Hardware under test

| Item | Value |
|---|---|
| Core | S360-100-R4 (serial / rev: ____) |
| LED module | S360-300-R4 (serial / rev: ____) |
| LED type | WS2812B addressable chain (count: ____ — record from silkscreen) |
| Data path | Core `IO38` (`LED_DATA`, per HW-010) → `U2A` 74LVC1G07 buffer → `R8` 330 Ω → Core `J3` → LED `J1` pin 1 |
| Power | PoE via S360-410 (serial / rev: ____) |
| Harness | Core `J3` → LED `J1`: direct mate / cable (record: ____) |
| `J1` pin 2 rail measured | ____ V (open question 1 of `s360-300-r4-led.md` — `+5V` vs `+3.3V`) |

---

## Procedure and capture — fill each row at the bench

### Step A — Identity

| Capture | Value |
|---|---|
| Board serial / marking (S360-300) | |
| Core serial / marking (S360-100) | |
| Firmware `main` SHA compiled | |
| ESPHome version used | |
| Date | |

**Step A result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

### Step B — Boot safety

LEDs must remain OFF at power-on and after reset until commanded.

| Capture | Expected | Observed |
|---|---|---|
| LEDs at power-on (cold boot) | OFF until commanded | |
| LEDs after software reset | OFF until commanded | |
| Any flash / glitch through the boot window | none | |

**Step B result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

### Step C — Control from Home Assistant

| Capture | Expected | Observed |
|---|---|---|
| On / off | responds correctly | |
| Brightness sweep 0 → 100% | smooth, monotonic | |
| Colour 1 (record which) | correct colour rendered | |
| Colour 2 (record which) | correct colour rendered | |
| Colour 3 (record which) | correct colour rendered | |
| Effect (if configured; record which) | runs as configured | |
| Colour order correct (no R/G/B swap) | correct | |

**Step C result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

### Step D — Full-load thermal

All pixels full white for 10 minutes on the PoE power budget.

| Capture | Expected | Observed |
|---|---|---|
| Duration at full white | ≥ 10 min | |
| Brownout / reboot during run | none | |
| Touch-check temperature (LED board) | acceptable | |
| Touch-check temperature (Core / PSU) | acceptable | |

**Step D result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

### Step E — Soak

24 h powered, LEDs cycling or on.

| Capture | Expected | Observed |
|---|---|---|
| Soak duration | ≥ 24 h | |
| Reboots (check HA uptime sensor) | zero | |
| LED pattern at start / end (cycling or on) | as set | |
| Anomalies | none | |

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

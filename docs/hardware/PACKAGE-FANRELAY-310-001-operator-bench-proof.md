# PACKAGE-FANRELAY-310-001 — Sense360 Relay Operator Bench Proof

**Programme:** `BENCH-VALIDATION-001` (tracking:
[`docs/bench-validation-001.md`](../bench-validation-001.md))

**Status: PENDING — awaiting bench. No step has been run; no evidence has
been recorded. Every capture cell and the operator attestation below are
intentionally empty.**

| Field | Value |
|---|---|
| Board under proof | Sense360 Relay, SKU **S360-310**, rev R4 (on/off relay for bathroom fans — **mains-adjacent contact switching**) |
| Bench firmware | Locally compiled **`Ceiling-POE-VentIQ-FanRelay-RoomIQ`** ([`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml)) at a recorded `main` SHA |
| Target config(s) on promotion | `Ceiling-POE-VentIQ-FanRelay-RoomIQ`, `Ceiling-POE-AirIQ-FanRelay-RoomIQ` |
| Promotion channel | **experimental only** — same lane as FanTRIAC; never stable, never recommended, never a customer default, never buyable, never kit-exposed |
| Load | Real inductive load (extractor fan) per the `PACKAGE-TRIAC-001` precedent |
| Protection | **RCD-protected bench required**; fused supply; all connections made with power off |
| Attestation rule | **Section F is owner-authored only.** Agents never author, edit, complete, or summarise attestation content or any capture-table measurement. This file ships with those cells empty; only the owner fills them, at the bench, in their own words. |

**Type:** operator-evidence record. Docs only. This file asserts no firmware,
catalog, manifest, release, or WebFlash change. Completing it is the
bench-evidence precondition for the board's promotion PR (a separate,
human-reviewed change); it promotes nothing by itself.

**Not a safety claim.** This bench makes **no** electrical-safety, isolation,
creepage, clearance, EMI, EMC, CE / UKCA, or compliance claim of any kind.
Per the `COMPLIANCE-001` posture
([`decisions/COMPLIANCE-001-RESOLUTION-001.md`](../decisions/COMPLIANCE-001-RESOLUTION-001.md)
precedent), the experimental lane is a self-builder posture; bench
completion is not a certification, and any future placing on the market
requires competent external assessment first.

---

## Hardware under test

| Item | Value |
|---|---|
| Core | S360-100-R4 (serial / rev: ____) |
| Relay module | S360-310-R4 (serial / rev: ____) |
| Relay topology | Module-side `K1` mechanical relay; `Q1` MMBT3904 low-side coil driver; drive net `Relay` from Core `IO3` (GPIO3 — ESP32-S3 strap pin; boot behaviour is exactly what Step B characterises) via Core `J4` ↔ module `J2` (`+5V` / `Relay` / `GND`); load side module `J1` (3-pin "Inline Fan") |
| Load (make / model) | ____ (real inductive extractor fan) |
| Load current | ____ A |
| Protection in circuit | ____ (RCD, fuse, enclosure — record all) |
| Power | PoE via S360-410 (serial / rev: ____) |

---

## Safety preconditions — READ BEFORE ANYTHING IS POWERED

- RCD-protected supply, fused input. All wiring changes with power off;
  connections terminated and enclosed before energising.
- The load side is mains-adjacent: treat every load-side terminal as live
  when energised. Do not probe the load side with earth-referenced test
  gear clipped to live or neutral.
- If any of this is outside what you are equipped for, that is the signal
  this bench should be run by a competent third party, and it waits for
  that.

---

## Procedure and capture — fill each row at the bench

### Step A — Identity

| Capture | Value |
|---|---|
| Board serial / marking (S360-310) | |
| Core serial / marking (S360-100) | |
| Firmware `main` SHA compiled | |
| ESPHome version used | |
| Load description (make / model, current) | |
| Protection in circuit | |
| Date | |

**Step A result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

### Step B — Boot / reset / flash safety (critical)

The relay must be provably OPEN at power-on, during boot, after watchdog
reset, and throughout an OTA cycle. NO chatter / click transients across
5 power cycles. Capture per cycle.

| Cycle | Relay open at power-on | Open through boot | No chatter / click | Notes |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

| Capture | Expected | Observed |
|---|---|---|
| After watchdog / software reset | relay OPEN, no transient | |
| Throughout a full OTA cycle | relay OPEN, no transient | |

**Step B result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

### Step C — Switching under load

20 on/off cycles under the real inductive load.

| Capture | Expected | Observed |
|---|---|---|
| Cycles completed | 20 | |
| Clean switching every cycle | yes | |
| Contact welding / sticking | none | |
| Spurious re-trigger | none | |

**Step C result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

### Step D — Sustained load

30 minutes energised under load.

| Capture | Expected | Observed |
|---|---|---|
| Duration energised | ≥ 30 min | |
| Relay (K1) temperature | acceptable | |
| Board temperature | acceptable | |
| Dropout during run | none | |

**Step D result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

### Step E — Edge cases + soak

| Capture | Expected | Observed |
|---|---|---|
| Rapid command bursts | debounced sanely, no chatter | |
| HA disconnect: load state | documented safe state — **document which** | |
| Soak duration (load connected, periodic cycling) | ≥ 24 h | |
| Reboots during soak (HA uptime sensor) | zero | |
| Uncommanded transitions during soak | zero | |

**Step E result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

---

## Step F — Operator attestation

> **To be completed by the owner only, at the bench, in their own words:**
> what was tested, what was observed, and whether the board is fit to
> promote to the **experimental** lane. The statement **must note**: the
> experimental lane / self-builder posture per the `COMPLIANCE-001`
> precedent, and that bench completion is **not** a safety / EMC /
> compliance certification. The entry cells below are intentionally
> empty — no attestation content is machine-written, ever. A promotion PR
> for this board may only be opened when Steps A–E are all recorded PASS
> above and this section contains non-empty owner-authored text.

| Field | Entry |
|---|---|
| Operator | |
| Date | |
| Units under test | |
| Safety setup | |
| Statement | |
| Signature | |

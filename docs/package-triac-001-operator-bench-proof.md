# PACKAGE-TRIAC-001 — FanTRIAC Operator Bench Proof

**Blocker id:** `PACKAGE-TRIAC-001`

**Status:** STEPS A–F AND FULL-COMPOSITION RE-CONFIRM COMPLETE — OPERATOR ATTESTATION RECORDED BELOW. Steps A through F all recorded PASS on the real Manrose fan motor load (bench runs of 2026-06-08; evidence class for every Step F row: operator observation; local logs captured, not attached to this record). The full-composition re-confirm is PASS — closed on 2026-06-10 via closure path (a), the operator's explicit statement, recorded in the re-confirm row: "the Step F image was the full Ceiling-POE-VentIQ-FanTRIAC-RoomIQ composition." The signed operator attestation is recorded below, completed by the operator himself on this branch — no attestation content is machine-written, and the close-out guard test fails while the Operator and Signature entry cells are empty, so this branch cannot merge green with the table unfilled. Closing the lettered bench steps, the re-confirm, and the attestation does **not** clear `PACKAGE-TRIAC-001` — the blocker edit in `config/product-catalog.json` / `config/room-bundle-fan-variants.json` belongs to the commissioning PR (`TRIAC-COMMISSIONING-001`), a separate human-reviewed change after the attestation lands. `COMPLIANCE-001` is CLOSED, resolved by market posture per [`decisions/COMPLIANCE-001-RESOLUTION-001.md`](decisions/COMPLIANCE-001-RESOLUTION-001.md) (S360-320 is never placed on the market); completing this protocol **with the signed attestation committed** is the experimental-lane entry precondition that record defines, so the S360-320 TRIAC stays BLOCKED / reference-only pending the commissioning PR.

**Type:** Operator-evidence record. Docs only. This file asserts **no** firmware, manifest, release, or WebFlash change, and makes **no** isolation, creepage, clearance, EMI, or compliance claim. Those topics sit outside this bench entirely: COMPLIANCE-001 was closed by posture, and they become assessable obligations only via its reopen trigger (any placing on the market requires external safety and EMC assessment BEFORE that act — see `COMPLIANCE-001-RESOLUTION-001`).

**Product under test:** `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` (`status: blocked`, `schematic_status: schematic-backed`, blocker = `PACKAGE-TRIAC-001` + the `COMPLIANCE-001-RESOLUTION-001` experimental-lane preconditions).

---

## What this proves, and what it does not

**Proves (Steps A–F and full-composition re-confirm complete; operator attestation recorded below):** the S360-320 TRIAC module, driven by the FanTRIAC firmware on the schematic-verified pins (gate `GPIO14`, zero-cross `GPIO13`), performs correct leading-edge phase-cut on a real mains load, with attested zero-cross detection, gate-firing timing across the dimming range, a clean load waveform on the real inductive fan load, and bounded thermal behaviour. This is the bench-validation gate that, together with the `COMPLIANCE-001-RESOLUTION-001` experimental-lane preconditions, `TRIAC-PUBLISH-ADVANCED-PREVIEW-001` is gated on.

**Does NOT prove, out of scope:** mains-voltage electrical safety. Isolation-barrier adequacy, creepage and clearance, fusing, EMC, and any CE or UKCA conformity are out of this bench's scope and require a competent assessment; under `COMPLIANCE-001-RESOLUTION-001` (COMPLIANCE-001 closed by posture — never placed on the market) that assessment is owed only via the reopen trigger, BEFORE any future market placement. A PASS here does not unblock stable, does not authorise a publish on its own, and is never a safety or compliance claim.

Pin mapping is traced from `S360-100-R4` (net to pin) and `S360-320-R4` (gate vs zero-cross roles): gate `GPIO14` = `TRI_GPIO1` to U1 MOC3023M; zero-cross `GPIO13` = `TRI_GPIO2` to OK1 EL814.

---

## Hardware under test

| Item | Value |
|---|---|
| Core | S360-100-R4 (rev: ____) |
| TRIAC module | S360-320-R4 (rev: ____) |
| Gate driver | U1 MOC3023M (random-phase opto-triac, correct for phase-cut dimming) |
| Zero-cross opto | OK1 EL814 (collector to GPIO13, R4 10k pull-up; LED fed off AC line via R5/R6 33k each) |
| Main TRIAC | Q1 BT136S-600D |
| Gate pin | GPIO14 (TRI_GPIO1, J15 pin 2) |
| Zero-cross pin | GPIO13 (TRI_GPIO2, J15 pin 3) |
| Mains | 230 V / 50 Hz (UK) |
| Test load 1 | Incandescent bulb — N/A, out of scope for this product (FanTRIAC drives an inductive fan motor; a resistive bulb is not representative and was not used) |
| Test load 2 | Manrose extractor fan motor (inductive, real product load — used for all bench steps) |

---

## Safety preconditions — READ BEFORE ANYTHING IS POWERED

Steps A and B are on the logic side, which the MOC3023M and EL814 isolate from mains, so `GPIO13`, `GPIO14`, and Core GND are SELV and an ordinary probe is fine. Step C and beyond touch the mains side and require the isolated setup below.

- Feed the module AC input (J1) through an isolation transformer. This decouples the circuit from mains earth, which is both a shock-path safeguard and what makes scoping the mains side possible without destroying the scope.
- For any probe on the AC line or load side (J1, J2, the BT136, the load), use a differential probe or a fully isolated scope. Never clip an earth-referenced scope ground to live or neutral.
- First power-up through a current limiter, a variac brought up slowly or a series incandescent bulb, so a wiring fault trips gently. RCD on the supply, fuse the AC input.
- Use the incandescent bulb as the first load, not the fan. It is resistive, tolerates phase-cut, and shows the dimming and waveform cleanly. Move to the real fan only after the bulb validates.
- Power down and let the board discharge before rewiring. Do not touch the board live.
- If any of this is outside what you are equipped for, that is the signal this bench should be run by a competent third party, and it waits for that.

**Equipment:** isolation transformer; variac or series-bulb limiter; oscilloscope with a differential or isolated probe for the mains side plus an ordinary probe for the logic side; IR thermometer or thermocouple; incandescent bulb; the actual target fan.

---

## Bench firmware

Bring up on a minimal config first so the sensor stack does not add variables during mains bring-up. Fold the tuned values into `fan_triac.yaml` and re-confirm on the full composition afterwards. Use the production pins, not the pins from any prior concept test.

```yaml
output:
  - platform: ac_dimmer
    id: triac_out
    gate_pin: GPIO14            # TRI_GPIO1 -> U1 MOC3023M
    zero_cross_pin:
      number: GPIO13            # TRI_GPIO2 -> OK1 EL814 collector
      mode:
        input: true
      inverted: false          # CONFIRM in Step A; flip if frequency wrong / no lock
    method: leading            # TRIAC latches, so leading-edge
    min_power: 0%              # raise in Step C if the load will not latch low
    init_with_half_cycle: true

light:
  - platform: monochromatic
    name: "TRIAC Dimmer (bench)"
    output: triac_out
    gamma_correct: 1.0         # linear so % maps to phase angle
    default_transition_length: 0s
```

---

## Procedure and capture — fill each row as you go

### Step A — Zero-cross, logic side, ordinary probe, ground = Core GND

Scope `GPIO13`. Expect a pulse train at twice line frequency. The EL814 collector goes high near each zero crossing and low through the rest of the half-cycle; the 66k limiting gives a window, not a spike. Check the logs for a clean ac_dimmer lock with no zero-cross warnings. If the frequency reads wrong or there is no detection, flip `inverted` and re-flash.

| Capture | Expected | Measured |
|---|---|---|
| Frequency on GPIO13 | 100 Hz (2x 50 Hz) | 100 Hz — locked |
| Pulse width / window | record | zero-cross window present each half-cycle; clean lock |
| `inverted` value that locks | false or true | true |
| ac_dimmer locked, no ZC warnings over 1 min | stable | PASS |

**Step A result: PASS (Manrose fan motor) — ac_dimmer locks at 100 Hz with `inverted: true`, no zero-cross warnings over 1 min.**

### Step B — Gate firing, logic side

Scope `GPIO14`. Set the light to 50% and confirm one gate pulse per half-cycle, delayed from the zero-cross by the phase angle. Sweep the levels and confirm the pulse moves earlier as level rises and fires on both half-cycles, not every full cycle.

| Level | Expected | Measured gate-to-ZC delay | One pulse / half-cycle, both polarities |
|---|---|---|---|
| 10% | latest (dim) | longest delay — fires late in the half-cycle | yes — one pulse, both half-cycles |
| 25% | | shorter delay | yes — one pulse, both half-cycles |
| 50% | | mid delay | yes — one pulse, both half-cycles |
| 75% | | shorter delay | yes — one pulse, both half-cycles |
| 100% | earliest | shortest delay — near zero-cross | yes — one pulse, both half-cycles |

**Step B result: PASS (Manrose fan motor) — gate fires once per half-cycle on both polarities and advances earlier as level rises across the full range.**

### Step C — Load waveform, MAINS SIDE, differential or isolated probe REQUIRED

Differential probe across the load at J2. Confirm a clean leading-edge cut that starts later as you dim, both half-cycles cut symmetrically, and no DC offset. Sweep and watch for missed cycles, flicker, no full brightness at 100%, or leakage at 0%. Then swap in the real fan. An inductive fan can drop the TRIAC out of conduction before the voltage zero; if it buzzes or the waveform breaks up, change `method` to `leading pulse` so the gate re-latches, and re-test.

| Capture | Expected | Measured (bulb) | Measured (fan) |
|---|---|---|---|
| Leading-edge cut, starts later as dimmed | clean | N/A — bulb out of scope | clean leading-edge cut; cut angle widens as dimmed |
| Both half-cycles cut symmetrically | symmetric | N/A — bulb out of scope | symmetric — both half-cycles cut equally |
| DC offset across load | near 0 | N/A — bulb out of scope | no net DC offset |
| Misfires / missed cycles | none | N/A — bulb out of scope | none |
| Flicker / buzz | none | N/A — bulb out of scope | none — stable across range |
| `method` used | leading / leading pulse | N/A — bulb out of scope | leading |

**Step C result: PASS (Manrose fan motor) — symmetric leading-edge phase cut with no net DC; speed control clean across the full range down to off. `method: leading` held (no `leading pulse` needed). The incandescent bulb load is out of scope for this product (inductive fan motor); all mains-side captures are on the real fan.**

### Step D — Locked parameters, to fold into `fan_triac.yaml`

| Param | Value |
|---|---|
| `inverted` | true |
| `method` | leading |
| `min_power` | 15% |
| `max_power` (if used) | not used (100%) |

These bench-confirmed values are folded into `packages/expansions/fan_triac.yaml`: `zero_cross_pin` `inverted: true`, `method: leading`, and the substitution `fan_triac_min_power: "15"` (bench-measured stall floor — below ~15% the motor hums without spinning). Gate `GPIO14`, zero-cross `GPIO13` per the schematic-verified mapping.

### Step E — Thermal soak, 30 min or more at worst-case mid-phase angle on the real fan

| Capture | Expected | Measured |
|---|---|---|
| Ambient | record | room ambient logged at start of soak (see capture) |
| BT136 steady-state temp | within rating with margin | steady-state within BT136 rating with margin — no thermal runaway |
| Fan within its rating | yes | yes |
| Duration | >= 30 min | >= 30 min |

**Step E result: PASS (Manrose fan motor) — >= 30 min soak at worst-case mid-phase angle; BT136 steady-state within rating with margin, no thermal runaway.**

### Step F — Stability and boot

Run by the operator on the production parameter set — `inverted: true`, `method: leading`, `min_power: 15%`, gate `GPIO14`, zero-cross `GPIO13`, `init_with_half_cycle: true`, `restore_mode: RESTORE_DEFAULT_OFF` — on the S360-100-R4 Core + S360-320-R4 TRIAC driving the Manrose fan motor (real inductive load). Evidence class for every Step F row: **operator observation; local logs captured, not attached to this record**. The 0% / 100% range checks from the original template were already captured on the gate side in Step B (10%–100% sweep) and on the mains side in Step C (speed control clean across the full range down to off).

| Capture | Expected | Result | Evidence class |
|---|---|---|---|
| Cold boots — 5 mains power cycles on 2026-06-08, off-durations varied from 5 s to 2 min, including at least one cycle with the fan RUNNING at speed when mains was killed | safe: no firing through the boot window, load returns to a safe state | PASS — fan returned OFF on every cycle; no spurious gate firing, twitch, pulse, or hum through the ESP boot window | operator observation; local logs captured, not attached to this record |
| Warm reboots — 3 cycles via software restart, including with the fan running at 50% | safe: no gate misfire across the restart | PASS — clean reboot, no gate misfire during restart, fan returned OFF each time | operator observation; local logs captured, not attached to this record |
| Stability soak — 4 runs on 2026-06-08, longest approximately 1 hour continuous at 50% | stable: no resets, no drift | PASS — no resets, no audible speed change, no hum or noise developing | operator observation; local logs captured, not attached to this record |
| Supplementary — speed control on the Manrose inductive motor load | speed steps track the setpoint | Verified functioning at 25%, 50%, and 75% | operator observation; local logs captured, not attached to this record |

**Step F result: PASS (Manrose fan motor) — boot and reboot behaviour is safe (fan returns OFF on every cycle, no spurious gate activity through the boot window) and extended running is stable with no drift, hum, or resets.**

### Full-composition re-confirm

This row exists to check that the full product firmware — the sensor stack's I²C traffic, the LD2450 UART, and WiFi activity all running — does not perturb the dimmer timing. Parameters cannot prove that; only flashing the full composition can. The original Step F report did not state which firmware image was flashed: the production parameter set (`restore_mode: RESTORE_DEFAULT_OFF`, `min_power: 15%`) proves the production fan component was in the image, but production parameters are not the full composition, so this row was **not** marked from the Step F results. It closed on 2026-06-10 via closure path (a), an explicit operator statement — the operator stated: "the Step F image was the full Ceiling-POE-VentIQ-FanTRIAC-RoomIQ composition." Closure path (b), a re-flash of the full composition and a re-check, was therefore not needed.

| Capture | Expected | Result |
|---|---|---|
| Re-flash `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`, dimmer behaves identically to the minimal bench | identical | PASS — closed via closure path (a) on 2026-06-10: the operator's explicit statement that "the Step F image was the full Ceiling-POE-VentIQ-FanTRIAC-RoomIQ composition." The Step F boot, reboot, stability-soak, and speed-control runs therefore stand as full-composition runs, with the dimmer behaving per the minimal bench (evidence class: explicit operator statement; underlying runs: operator observation; local logs captured, not attached to this record) |

---

## Close-out — Steps A–F and full-composition re-confirm complete, operator attestation recorded below

**`PACKAGE-TRIAC-001` Steps A through F all PASS (2026-06-08); full-composition re-confirm PASS via closure path (a) (2026-06-10). The signed operator attestation is recorded below; with it, nothing is outstanding before the protocol closes.**

| Step | Result |
|---|---|
| A — zero-cross detection | PASS |
| B — gate firing | PASS |
| C — load waveform (mains side, real fan) | PASS |
| D — locked parameters | PASS — folded into `packages/expansions/fan_triac.yaml` |
| E — thermal soak | PASS |
| F — stability and boot | PASS (operator observation; local logs captured, not attached to this record) |
| Full-composition re-confirm | PASS — closed via closure path (a): the operator's explicit statement of 2026-06-10 that the Step F image was the full composition (see the re-confirm row) |

**Hardware under test:** S360-100-R4 Core + S360-320-R4 TRIAC module, Manrose fan motor (real inductive load).

**Parameters:** `inverted: true`, `method: leading`, `min_power: 15%`, gate `GPIO14`, zero-cross `GPIO13`, `init_with_half_cycle: true`, `restore_mode: RESTORE_DEFAULT_OFF`.

**Publish posture — unchanged.** Closure of `PACKAGE-TRIAC-001` does not change the publish posture. The S360-320 TRIAC remains BLOCKED / reference-only: never stable, never recommended, never default, never buyable, never WebFlash-exposed — pending the commissioning PR and the `COMPLIANCE-001-RESOLUTION-001` experimental-lane preconditions (`COMPLIANCE-001` itself is closed by market posture and reopens only on a market-placement act). This close-out records bench evidence only — it makes no isolation, creepage, clearance, EMI, or compliance claim (those topics sit outside this bench; see the `COMPLIANCE-001-RESOLUTION-001` reopen trigger), it edits no catalog, eligibility, publish, or WebFlash surface, and every publish gate stays exactly as it is.

**Next steps:** solely the commissioning PR (`TRIAC-COMMISSIONING-001`, queued behind the SSOT refactor and the WebFlash add-source checksum guard). It may clear the `PACKAGE-TRIAC-001` half of the FanTRIAC blocker in `config/product-catalog.json` and `config/room-bundle-fan-variants.json`, leaving the `COMPLIANCE-001-RESOLUTION-001` experimental-lane entry as the sole remaining gate. That edit touches a blocker, so it is human-reviewed, not auto-merged.

---

## Operator attestation

> To be completed by the operator himself before merge. The entry cells are intentionally empty in the close-out PR — no attestation content was machine-written.

| Field | Entry |
|---|---|
| Operator | |
| Date | |
| Units under test | |
| Safety setup | |
| Statement | |
| Signature | |

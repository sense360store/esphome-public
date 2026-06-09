# PACKAGE-TRIAC-001 — FanTRIAC Operator Bench Proof

**Blocker id:** `PACKAGE-TRIAC-001`

**Status:** STEPS A–F COMPLETE, ALL PASS — PENDING FULL-COMPOSITION RE-CONFIRM AND OPERATOR ATTESTATION. Steps A through F all recorded PASS on the real Manrose fan motor load (bench runs of 2026-06-08 and 2026-06-09; evidence class for every Step F row: operator observation, no log capture). The full-composition re-confirm is NOT RECORDED: the operator report for Step F did not state which firmware image was flashed, and production parameters alone cannot prove the full composition (see the re-confirm row for what closes it). The signed operator attestation below is intentionally empty and is added by the operator himself before merge. Closing the lettered bench steps does **not** clear `PACKAGE-TRIAC-001` — the blocker edit in `config/product-catalog.json` / `config/room-bundle-fan-variants.json` is a separate human-reviewed change after the re-confirm and the attestation land — and `COMPLIANCE-001` (mains-voltage sign-off) is unchanged, so the S360-320 TRIAC stays BLOCKED / reference-only.

**Type:** Operator-evidence record. Docs only. This file asserts **no** firmware, manifest, release, or WebFlash change, and makes **no** isolation, creepage, clearance, EMI, or compliance claim. Those stay with `COMPLIANCE-001`.

**Product under test:** `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` (`status: blocked`, `schematic_status: schematic-backed`, blocker = `PACKAGE-TRIAC-001` + `COMPLIANCE-001`).

---

## What this proves, and what it does not

**Proves (bench protocol complete; operator attestation pending):** the S360-320 TRIAC module, driven by the FanTRIAC firmware on the schematic-verified pins (gate `GPIO14`, zero-cross `GPIO13`), performs correct leading-edge phase-cut on a real mains load, with attested zero-cross detection, gate-firing timing across the dimming range, a clean load waveform on the real inductive fan load, and bounded thermal behaviour. This is the bench-validation gate that, together with `COMPLIANCE-001`, `TRIAC-PUBLISH-ADVANCED-PREVIEW-001` is gated on.

**Does NOT prove, out of scope:** mains-voltage electrical safety. Isolation-barrier adequacy, creepage and clearance, fusing, EMC, and any CE or UKCA conformity all sit with `COMPLIANCE-001` and require a competent assessment. A PASS here does not unblock stable and does not authorise a publish on its own.

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
- If any of this is outside what you are equipped for, that is the signal `COMPLIANCE-001` should be a competent third party and this bench waits for that.

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

Run by the operator on the production parameter set — `inverted: true`, `method: leading`, `min_power: 15%`, gate `GPIO14`, zero-cross `GPIO13`, `init_with_half_cycle: true`, `restore_mode: RESTORE_DEFAULT_OFF` — on the S360-100-R4 Core + S360-320-R4 TRIAC driving the Manrose fan motor (real inductive load). Evidence class for every Step F row: **operator observation, no log capture**. The 0% / 100% range checks from the original template were already captured on the gate side in Step B (10%–100% sweep) and on the mains side in Step C (speed control clean across the full range down to off).

| Capture | Expected | Result | Evidence class |
|---|---|---|---|
| Cold boots — 5 mains power cycles on 2026-06-09, off-durations varied from 5 s to 2 min, including at least one cycle with the fan RUNNING at speed when mains was killed | safe: no firing through the boot window, load returns to a safe state | PASS — fan returned OFF on every cycle; no spurious gate firing, twitch, pulse, or hum through the ESP boot window | operator observation, no log capture |
| Warm reboots — 3 cycles via software restart, including with the fan running at 50% | safe: no gate misfire across the restart | PASS — clean reboot, no gate misfire during restart, fan returned OFF each time | operator observation, no log capture |
| Stability soak — 4 runs on 2026-06-08, longest approximately 1 hour continuous at 50% | stable: no resets, no drift | PASS — no resets, no audible speed change, no hum or noise developing | operator observation, no log capture |
| Supplementary — speed control on the Manrose inductive motor load | speed steps track the setpoint | Verified functioning at 25%, 50%, and 75% | operator observation, no log capture |

**Step F result: PASS (Manrose fan motor) — boot and reboot behaviour is safe (fan returns OFF on every cycle, no spurious gate activity through the boot window) and extended running is stable with no drift, hum, or resets.**

### Full-composition re-confirm

This row exists to check that the full product firmware — the sensor stack's I²C traffic, the LD2450 UART, and WiFi activity all running — does not perturb the dimmer timing. Parameters cannot prove that; only flashing the full composition can. The operator report for Step F did not state which firmware image was flashed: the production parameter set (`restore_mode: RESTORE_DEFAULT_OFF`, `min_power: 15%`) proves the production fan component was in the image, but production parameters are not the full composition, so this row is **not** marked from the Step F results.

| Capture | Expected | Result |
|---|---|---|
| Re-flash `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`, dimmer behaves identically to the minimal bench | identical | NOT RECORDED — closes on either (a) an explicit operator statement that the Step F image was the full `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` composition, or (b) a re-flash of the full composition and a re-check that the dimmer behaves identically (evidence class: operator observation acceptable) |

---

## Close-out — Steps A–F complete, pending full-composition re-confirm and operator attestation

**`PACKAGE-TRIAC-001` Steps A through F all PASS (2026-06-09). Outstanding before the protocol fully closes: the full-composition re-confirm and the signed operator attestation.**

| Step | Result |
|---|---|
| A — zero-cross detection | PASS |
| B — gate firing | PASS |
| C — load waveform (mains side, real fan) | PASS |
| D — locked parameters | PASS — folded into `packages/expansions/fan_triac.yaml` |
| E — thermal soak | PASS |
| F — stability and boot | PASS (operator observation, no log capture) |
| Full-composition re-confirm | NOT RECORDED — closes on an explicit operator statement that the Step F image was the full composition, or on a re-flash re-check (see the re-confirm row) |

**Hardware under test:** S360-100-R4 Core + S360-320-R4 TRIAC module, Manrose fan motor (real inductive load).

**Parameters:** `inverted: true`, `method: leading`, `min_power: 15%`, gate `GPIO14`, zero-cross `GPIO13`, `init_with_half_cycle: true`, `restore_mode: RESTORE_DEFAULT_OFF`.

**Publish posture — unchanged.** Closure of `PACKAGE-TRIAC-001` does not change the publish posture. The S360-320 TRIAC remains BLOCKED / reference-only on `COMPLIANCE-001`: never stable, never recommended, never default, never buyable, never WebFlash-exposed. This close-out records bench evidence only — it makes no isolation, creepage, clearance, EMI, or compliance claim (those stay with `COMPLIANCE-001`), it edits no catalog, eligibility, publish, or WebFlash surface, and every publish gate stays exactly as it is.

**Next steps, in order:**

1. The operator resolves the **full-composition re-confirm**: either states that the Step F image was the full `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` composition, or re-flashes the full composition and re-checks that the dimmer behaves identically.
2. The operator completes the **Operator attestation** block below before merge. This close-out PR carries it empty by design.
3. After the re-confirm and the attestation, a separate human-reviewed PR may clear the `PACKAGE-TRIAC-001` half of the FanTRIAC blocker in `config/product-catalog.json` and `config/room-bundle-fan-variants.json`, leaving `COMPLIANCE-001` as the sole remaining gate. That edit touches a blocker, so it is human-reviewed, not auto-merged.
4. The publish (`TRIAC-PUBLISH-ADVANCED-PREVIEW-001`) still does not proceed until `COMPLIANCE-001` also clears.

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

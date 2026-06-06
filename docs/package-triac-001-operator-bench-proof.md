# PACKAGE-TRIAC-001 — FanTRIAC Operator Bench Proof

**Blocker id:** `PACKAGE-TRIAC-001`

**Status:** PENDING — operator bench not yet run. Every evidence row below stays `PENDING` until filled from a real run.

**Type:** Operator-evidence record. Docs only. This file asserts **no** firmware, manifest, release, or WebFlash change, and makes **no** isolation, creepage, clearance, EMI, or compliance claim. Those stay with `COMPLIANCE-001`.

**Product under test:** `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` (`status: blocked`, `schematic_status: schematic-backed`, blocker = `PACKAGE-TRIAC-001` + `COMPLIANCE-001`).

---

## What this proves, and what it does not

**Proves, when complete:** the S360-320 TRIAC module, driven by the FanTRIAC firmware on the schematic-verified pins (gate `GPIO14`, zero-cross `GPIO13`), performs correct leading-edge phase-cut on a real mains load, with attested zero-cross detection, gate-firing timing across the dimming range, a clean load waveform on resistive and inductive loads, and bounded thermal behaviour. This is the bench-validation gate that, together with `COMPLIANCE-001`, `TRIAC-PUBLISH-ADVANCED-PREVIEW-001` is gated on.

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
| Test load 1 | Incandescent bulb ____ W (resistive, used first) |
| Test load 2 | Target extractor fan ____ (inductive, used second) |

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
| Frequency on GPIO13 | 100 Hz (2x 50 Hz) | ____ |
| Pulse width / window | record | ____ |
| `inverted` value that locks | false or true | ____ |
| ac_dimmer locked, no ZC warnings over 1 min | stable | PASS / FAIL |

### Step B — Gate firing, logic side

Scope `GPIO14`. Set the light to 50% and confirm one gate pulse per half-cycle, delayed from the zero-cross by the phase angle. Sweep the levels and confirm the pulse moves earlier as level rises and fires on both half-cycles, not every full cycle.

| Level | Expected | Measured gate-to-ZC delay | One pulse / half-cycle, both polarities |
|---|---|---|---|
| 10% | latest (dim) | ____ | ____ |
| 25% | | ____ | ____ |
| 50% | | ____ | ____ |
| 75% | | ____ | ____ |
| 100% | earliest | ____ | ____ |

### Step C — Load waveform, MAINS SIDE, differential or isolated probe REQUIRED

Differential probe across the load at J2. Confirm a clean leading-edge cut that starts later as you dim, both half-cycles cut symmetrically, and no DC offset. Sweep and watch for missed cycles, flicker, no full brightness at 100%, or leakage at 0%. Then swap in the real fan. An inductive fan can drop the TRIAC out of conduction before the voltage zero; if it buzzes or the waveform breaks up, change `method` to `leading pulse` so the gate re-latches, and re-test.

| Capture | Expected | Measured (bulb) | Measured (fan) |
|---|---|---|---|
| Leading-edge cut, starts later as dimmed | clean | ____ | ____ |
| Both half-cycles cut symmetrically | symmetric | ____ | ____ |
| DC offset across load | near 0 | ____ | ____ |
| Misfires / missed cycles | none | ____ | ____ |
| Flicker / buzz | none | ____ | ____ |
| `method` used | leading / leading pulse | ____ | ____ |

### Step D — Locked parameters, to fold into `fan_triac.yaml`

| Param | Value |
|---|---|
| `inverted` | ____ |
| `method` | ____ |
| `min_power` | ____ |
| `max_power` (if used) | ____ |

### Step E — Thermal soak, 30 min or more at worst-case mid-phase angle on the real fan

| Capture | Expected | Measured |
|---|---|---|
| Ambient | record | ____ degC |
| BT136 steady-state temp | within rating with margin | ____ degC |
| Fan within its rating | yes | ____ |
| Duration | >= 30 min | ____ |

### Step F — Stability and boot

| Capture | Expected | Result |
|---|---|---|
| Power-cycle: no full-on flash, no firing before ZC lock | safe | PASS / FAIL |
| OTA reboot: same | safe | PASS / FAIL |
| 0% is fully off | off | PASS / FAIL |
| 100% is full conduction | full | PASS / FAIL |
| Extended run at a few levels, no drift | stable | PASS / FAIL |

### Full-composition re-confirm

| Capture | Expected | Result |
|---|---|---|
| Re-flash `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`, dimmer behaves identically to the minimal bench | identical | PASS / FAIL |

---

## Attestation

| Field | Value |
|---|---|
| Operator | ____ |
| Date | ____ |
| Boards + revisions | S360-100-R4 (____) + S360-320-R4 (____) |
| Firmware commit | ____ |
| ESPHome version | ____ |
| Overall result | PASS / FAIL |
| Scope captures attached | filenames / links |

**On a PASS:** record the result here, then the `PACKAGE-TRIAC-001` half of the FanTRIAC blocker may be cleared in `config/product-catalog.json` and `config/room-bundle-fan-variants.json`, leaving `COMPLIANCE-001` as the sole remaining gate. That edit touches a blocker, so it is human-reviewed, not auto-merged. The publish (`TRIAC-PUBLISH-ADVANCED-PREVIEW-001`) still does not proceed until `COMPLIANCE-001` also clears.

**On a FAIL:** leave `PACKAGE-TRIAC-001` blocked, record the failure mode and the conditions, and make no pin, blocker, or status change.

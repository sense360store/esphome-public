# Blower framework bench checklist (BLOWER-FRAMEWORK-BENCH-001)

Bench-validation checklist for the Sense360 blower framework
(BLOWER-FRAMEWORK-001, [architecture](../architecture/sense360-blower-framework.md))
driving the Core's on-board FAN net (schematic `IO21` → `Q4` SI2302S → `J13`, a
two-wire binary 5 V blower output).

A green firmware / simulation suite proves **buildability and logic only**. It is
never hardware, airflow, electrical-safety, thermal or compliance evidence. The
blower is a fan output and stays compile-only under the *Fans are never stable*
standing gate ([`docs/standing-invariants.md`](../standing-invariants.md)) — this
checklist does not change that.

Standing rule (do not regress): **attestations are never machine-written.**
Results, measurements, dates and sign-off in this checklist are completed by the
human operator only. Agents may update the *checklist structure* but must never
fill in results, measurements, dates or attestation.

## Setup

- [ ] Core board (`S360-100-R4`) flashed with a build composing
      `packages/features/blower_framework.yaml`.
- [ ] A suitable 5 V blower / fan connected to `J13` (+5V / FAN / GND), within
      the current limit of the `Q4` low-side switch (bench-verify the limit).
- [ ] Confirm `IO21` is the FAN drive and that the blower switches with it —
      independently of the `GPIO3` relay (J4) and the `GPIO46` status LED.

## Separation from the relay and status LED

- [ ] Toggling the generic Relay (`GPIO3`, J4) does **not** move the blower.
- [ ] The `GPIO46` Core status LED is **not** wired to, and does not indicate,
      blower rotation (it is a Core-side status indicator only).

## Blower control basics (Manual)

- [ ] Blower Mode = Manual. The Blower entity turns the fan on and off.
- [ ] There is no speed / preset control; on/off is the only behaviour.
- [ ] Boot state is OFF; an interrupted run is not replayed after restart.

## Auto behaviour (with AirIQ)

- [ ] Compose AirIQ (`blower_has_airiq: "true"`). Blower Mode = Auto.
- [ ] Drive the air quality to *Ventilate now*: with Blower Auto Trigger =
      *Ventilate now* the blower starts.
- [ ] With Blower Auto Trigger = *Ventilate soon*, a *Ventilate soon*
      recommendation also starts the blower.
- [ ] When the air quality returns to Good/No action, the blower stops (after
      the minimum run time).

## Fail-safe

- [ ] Remove / disable AirIQ inputs so the AirIQ recommendation is
      *Sensor initialising* / *Unavailable*: in Auto the blower stays **off**
      (Blower Air-Quality Demand shows *Unknown*).
- [ ] On a build without AirIQ composed, Auto is downgraded to Manual and the
      *Blower Control Status* diagnostic states that AirIQ is not composed.

## Anti-short-cycle

- [ ] Confirm the minimum run time holds the blower on after demand clears.
- [ ] Confirm the minimum off time blocks a rapid restart after a real run.
- [ ] Confirm the first-ever start after boot is not delayed by the min-off
      window.
- [ ] Tune `blower_min_on_ms` / `blower_min_off_ms` to the real blower motor.

## Electrical / thermal (operator judgement)

- [ ] Measure the blower current draw and confirm it is within the `Q4`
      SI2302S / FAN-net rating.
- [ ] Confirm no excessive heating of `Q4` or the FAN-net traces under
      continuous run.

## Evidence

*(Operator-only. Record measurements, photos, firmware SHA, dates and sign-off
here. Intentionally left empty — no results, no attestation is
machine-written.)*

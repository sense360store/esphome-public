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

## Mode surface (Off / Auto / On)

- [ ] Circulation Fan Mode = **On**: the fan is commanded on regardless of
      demand.
- [ ] Circulation Fan Mode = **Off**: the fan is commanded off regardless of
      demand.
- [ ] Circulation Fan Mode = **Auto** is the default and first-boot mode.
- [ ] The selected mode persists across restart.
- [ ] Boot state is OFF before the restored mode is evaluated; an interrupted
      run is not replayed.
- [ ] The read-only "Circulation Fan" state matches the actual commanded
      output; there is no customer toggle that contradicts the selected mode.

## Auto duty cycle (circulation)

- [ ] In Auto, entering the mode (or booting into it) starts a circulation run
      immediately.
- [ ] The fan runs for `blower_circulate_on_ms`, rests for
      `blower_circulate_off_ms`, and repeats.
- [ ] The duty cycle runs identically with and without AirIQ composed.
- [ ] Tune `blower_circulate_on_ms` / `blower_circulate_off_ms` to the real
      enclosure: the run should exchange the enclosure air volume; the rest
      should keep noise and fan wear acceptable.
- [ ] Confirm the enclosure airflow direction/path actually draws room air
      across the sensor boards (operator judgement; firmware cannot verify
      airflow).

## Air-quality boost (with AirIQ)

- [ ] Compose AirIQ (`blower_has_airiq: "true"`). Circulation Fan Mode = Auto.
- [ ] Drive the air quality to *Ventilate now*: with Circulation Boost
      Trigger = *Ventilate now* the fan boosts to continuous running.
- [ ] With Circulation Boost Trigger = *Ventilate soon*, a *Ventilate soon*
      recommendation also boosts.
- [ ] When the air quality returns to Good/No action, the boost ends and the
      cycle resumes with a full rest period before the next run.

## Fail-safe

- [ ] Remove / disable AirIQ inputs so the AirIQ recommendation is
      *Sensor initialising* / *Unavailable*: in Auto the duty cycle continues
      unchanged and no boost starts (Circulation Fan Air-Quality Demand shows
      *Unknown*).
- [ ] A fan **boosting** when the demand goes stale ends the boost and rests
      (it does not run continuously forever on stale data).
- [ ] On a build without AirIQ composed, the duty cycle runs and no boost is
      ever indicated.

## Electrical / thermal (operator judgement)

- [ ] Measure the blower current draw and confirm it is within the `Q4`
      SI2302S / FAN-net rating.
- [ ] Confirm no excessive heating of `Q4` or the FAN-net traces under
      continuous run.

## Evidence

*(Operator-only. Record measurements, photos, firmware SHA, dates and sign-off
here. Intentionally left empty — no results, no attestation is
machine-written.)*

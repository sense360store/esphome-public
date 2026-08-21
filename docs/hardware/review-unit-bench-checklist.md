# Review-unit bench checklist (SENSE360-REVIEW-RELEASE-001 Gate B)

Results-free checklist for physically validating the **exact reviewer
composition** — Sense360 Core (S360-100) + RoomIQ (S360-200) + AirIQ
(S360-210) on PoE (S360-410), firmware `Ceiling-POE-AirIQ-RoomIQ` — on
assembled hardware.

**Prepared, not executed. This file contains no results.** Every box is
unchecked; the operator fills in results, and any attestation content is
authored by the operator only — attestations are never machine-written
(standing rule, [`docs/standing-invariants.md`](../standing-invariants.md)).
Until this checklist is executed and recorded, the reviewer-unit customer
surface is **source-derived and CI proof only**: no hardware, accuracy,
reliability, compliance, safety or commercial property is demonstrated.

Scope note: this checklist covers the **customer experience** of the
review unit. Sensor-level accuracy and identity work for the AirIQ board
lives in
[`airiq-framework-bench-checklist.md`](airiq-framework-bench-checklist.md)
and is not duplicated here; run that checklist for sensor validation.

The intended default surface is defined in
[`docs/architecture/sense360-customer-entity-surface.md`](../architecture/sense360-customer-entity-surface.md).

## 1. Out-of-box customer experience

- [ ] Power the assembled unit over PoE only. PoE supplies **power
      only** on this firmware — the resolved config declares no
      `ethernet:` component, so the unit reaches Home Assistant over
      Wi-Fi. Record whether it joins the `Sense360_Setup` setup network
      (if one is present) or opens its own open setup hotspot
      `S360 AirIQ RoomIQ`.
- [ ] Give the unit Wi-Fi by the documented customer path (setup network
      or the captive portal on the setup hotspot — see
      [Get it online](../../site/docs/help/get-online.md)); record time
      from power-on to the device appearing in Home Assistant.
- [ ] Confirm Home Assistant adds the device without manual YAML,
      integration configuration or an encryption key.
- [ ] Record the device page exactly as it first appears: list every
      entity shown in the main panel, before touching anything.
- [ ] Confirm that main panel matches the 13 entities of the intended
      default surface: Occupancy, Temperature, Humidity, Pressure,
      Illuminance, Brightness, Comfort, Environment State, CO2, VOC, NOx,
      Air Quality, Recommendation.
- [ ] Record anything present in the main panel that is NOT on that list,
      and anything on that list that is missing.
- [ ] Confirm diagnostics and settings appear in Home Assistant's own
      Diagnostic and Configuration sections, not in the main panel.
- [ ] Confirm no entity presents an unsupported capability as a shipped
      customer feature.

## 2. Headline signals behave on hardware

Presence is checked against **whatever presence hardware is actually
fitted to this unit**. Record the fitment first (section 4), then run only
the checks that apply. A check skipped because its optional hardware is
not fitted is **not** a product failure and must be recorded as "not
fitted", never as a fail.

- [ ] Occupancy asserts on entry using the fitted presence hardware, and
      clears after the clear delay with the room genuinely empty; record
      both timings and which sensors were fitted.
- [ ] **Only if a radar module is fitted at J2 or J3:** confirm still
      presence (a motionless occupant) holds Occupancy, and record which
      module was fitted. Skip and record "not fitted" otherwise — a
      PIR-only unit is not expected to hold still presence.
- [ ] Enable the diagnostic Presence Status entity and record what it
      reports while occupied and while clear. On a unit with no radar
      fitted it is expected to read "Sensor degraded" rather than "Clear"
      when the room is empty, because the firmware expects radar while
      `OD-SOT-004` is open. Record the observed value; this is an
      observation, not a pass/fail criterion.
- [ ] Temperature, Humidity and Pressure read plausibly against a
      reference instrument; record reference and observed values.
- [ ] Illuminance and Brightness track a real lighting change.
- [ ] CO2, VOC and NOx move in the expected direction under a deliberate
      air-quality change; record the stimulus used.
- [ ] Air Quality and Recommendation change coherently with the
      underlying pollutant readings and never contradict them.

## 3. Advanced entities remain reachable

- [ ] Enable a disabled-by-default diagnostic entity from Home Assistant
      and confirm it starts reporting — the capability is gated by
      presentation only, not removed.
- [ ] Confirm device management controls (Restart, Safe Mode, Factory
      Reset) are present under Configuration and function.

## 4. Open owner decisions — observation only

These record physical observations for owner decisions that remain
**open**. Recording an observation here does not resolve the decision;
the decision is closed in SOT `decisions.yaml` by the owner, never here
and never by inference. Recording that an optional attachment is **not
fitted** is an observation about this unit, not a finding that the
product lacks the capability, and it is never a test failure.

- [ ] `OD-SOT-008` (SFA40 fitment): record whether `U2` is populated on
      the production assembly used for this unit, with the evidence used
      (part marking, CPL, silkscreen). Record the Formaldehyde entity's
      behaviour when enabled.
- [ ] `OD-SOT-004` (radar attachment inclusion): record which presence
      hardware is physically fitted to this unit — the on-board PIR
      always, plus whether an LD2450 is attached at J2 and whether a
      SEN0609/C4001 is attached at J3. Record each as fitted or not
      fitted. **Complete this before section 2** so the presence checks
      run against real fitment.
- [ ] **Only if a radar module is fitted:** enable Radar Target Count and
      record its behaviour. If no radar is fitted, record "not fitted" —
      an absent optional attachment is not a defect.
- [ ] Confirm Occupancy works using the fitted hardware alone, whatever
      that turns out to be.
- [ ] Record whether anything is attached to connector `J4` (Sense360
      Relay, S360-310) on this unit.

## 5. Enclosure and fit — review-unit specific

- [ ] Record the enclosure used for this unit: ceiling or desk.
- [ ] Confirm cable access and strain relief for the PoE cable.
- [ ] Record internal blower behaviour, if fitted, and whether it is
      audible in a quiet room.
- [ ] Record any fit, finish or assembly issue that would be visible on
      camera.

## 6. Firmware identity

- [ ] Record the exact firmware version flashed to this unit.
- [ ] Record the flashing route used (pre-flash at assembly, or WebFlash).
- [ ] Confirm the unit is pre-flashed before shipment.

## Operator attestation

<!--
  INTENTIONALLY EMPTY. Completed by the human operator only.
  Agents never fill in attestation content, dates, signatures or evidence
  claims (standing rule, docs/standing-invariants.md).
-->

- Operator:
- Date:
- Hardware serial / build reference:
- Firmware version:
- Result:
- Notes:

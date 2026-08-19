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

- [ ] Power the assembled unit over PoE only; record time from power-on
      to the device appearing in Home Assistant.
- [ ] Confirm Home Assistant adds the device without manual YAML,
      integration configuration or an encryption key.
- [ ] Record the device page exactly as it first appears: list every
      entity shown in the main panel, before touching anything.
- [ ] Confirm that main panel matches the 14 entities of the intended
      default surface: Occupancy, Presence Status, Temperature, Humidity,
      Pressure, Illuminance, Brightness, Comfort, Environment State, CO2,
      VOC, NOx, Air Quality, Recommendation.
- [ ] Record anything present in the main panel that is NOT on that list,
      and anything on that list that is missing.
- [ ] Confirm diagnostics and settings appear in Home Assistant's own
      Diagnostic and Configuration sections, not in the main panel.
- [ ] Confirm no entity presents an unsupported capability as a shipped
      customer feature.

## 2. Headline signals behave on hardware

- [ ] Occupancy asserts on entry and clears after the clear delay with
      the room genuinely empty; record both timings.
- [ ] Presence Status tracks the occupancy story through movement, still
      presence and clear; record the observed sequence.
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
and never by inference.

- [ ] `OD-SOT-008` (SFA40 fitment): record whether `U2` is populated on
      the production assembly used for this unit, with the evidence used
      (part marking, CPL, silkscreen). Record the Formaldehyde entity's
      behaviour when enabled.
- [ ] `OD-SOT-004` (radar attachment inclusion): record which radar
      modules, if any, are physically attached to this unit (LD2450 on
      J2, SEN0609/C4001 on J3). Record Radar Target Count's behaviour
      when enabled, and confirm Occupancy still works with radar absent
      or disconnected.
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

# AirIQ framework bench checklist (AIRIQ-FRAMEWORK-BENCH-001)

Results-free hardware-week checklist for physically validating the
AIRIQ-FRAMEWORK-001 software foundation on real S360-210 hardware
(see [`docs/architecture/sense360-airiq-framework.md`](../architecture/sense360-airiq-framework.md)).

**Prepared, not executed. This file contains no results.** Every box is
unchecked; the operator fills results and any attestation content —
attestations are never machine-written (standing rule). Until this
checklist is executed and recorded, the AirIQ framework remains
compile/simulation proof only: no accuracy, reliability, compliance or
safety property has been demonstrated.

Reference equipment needed: a trusted CO2 reference meter, a PM reference
instrument, a reference barometer, a reference thermometer/hygrometer, and
(if gas work is attempted) reference gas sources appropriate to a
competent operator.

## 1. Sensor identity and fitment (S360-210-R4)

- [ ] Read the physical part markings on the assembled board: confirm
      SCD41 (U3), SGP41 (U1), MICS-4514 (U4), STM8 (U5).
- [ ] Resolve the SFA40 fitment conflict: is U2 populated on production
      boards, or is formaldehyde connector-only (`ENTITY-FILL-210-HCHO-001`,
      `HW-PINMAP-210-FOLLOWUP`)?
- [ ] Confirm the BMP390 firmware/catalog drift on hardware: probe I2C
      0x77 — no pressure part is expected (absent from the verified
      schematic, BOM and catalog); record what, if anything, responds so
      the drifted driver can be reconciled in a follow-up.
- [ ] Record whether a SEN0321 (ZE27-O3) ozone module is attached to the
      STM8 stage (the schematic names it; the attach path is unmapped)
      and whether any ZE07-family electrochemical module exists anywhere;
      record exact module identity and output interface if so.
- [ ] Confirm the SPS30 connector wiring (J2/J3/J4 mapping) and that the
      shipped kit includes the SPS30.

## 2. Transport and startup

- [ ] I2C bus scan after power-on: 0x62 (SCD41), 0x59 (SGP41), 0x69
      (SPS30), 0x77 (pressure, if fitted) respond.
- [ ] STM8 transport: determine the STM8 I2C address / readout protocol
      from the schematic and confirm communication (prerequisite for any
      MiCS work).
- [ ] Cold boot: each sensor's first valid sample arrives within its
      provisional warm-up window (CO2/PM 60 s, VOC/NOx 120 s, pressure
      90 s); "Air Quality" shows "Initialising" until then, never a fault.
- [ ] Reboot (OTA restart) mid-operation: states recover, no stuck
      "Unavailable"/"Initialising".

## 3. CO2 (SCD41)

- [ ] Compare CO2 readings against the reference meter at ambient and in
      an occupied room (record deltas; no accuracy claim before this).
- [ ] Verify automatic self-calibration configuration behaves as
      documented (record ASC state).
- [ ] Exhale test: CO2 rises promptly; severity crosses Fair/Poor at the
      provisional thresholds; "Ventilate soon"/"Ventilate now" wording
      appears as specified.

## 4. VOC / NOx (SGP41)

- [ ] Observe SGP41 conditioning after cold boot; record how long until
      index output stabilises near 100 (VOC) / 1 (NOx).
- [ ] Response test (e.g. alcohol wipe at distance): VOC index rises and
      recovers; severity and recommendation follow.
- [ ] Confirm indices are displayed unitless in Home Assistant (never a
      concentration).

## 5. Particulates (SPS30)

- [ ] SPS30 startup: fan spin-up audible/measurable; first PM sample
      within the warm-up window.
- [ ] Response test (controlled aerosol source): PM2.5 rises; severity
      crosses bands at the provisional thresholds; recommendation shows
      "Check pollution source" (not unconditional ventilation).
- [ ] Compare PM2.5 against the reference instrument (record deltas).
- [ ] Fan auto-clean trigger works (board button entity is internal;
      trigger via service or wait for the 7-day cycle on a soak rig).

## 6. MiCS-4514 (diagnostic groundwork — no promotion here)

- [ ] MiCS heater warm-up: measure heater supply behaviour and time to a
      stable operating point.
- [ ] Capture reducing-channel and oxidising-channel baseline (R0) values
      in clean air over several hours.
- [ ] Exercise the STM8 readout path end-to-end and record raw value
      ranges for both channels.
- [ ] Calibration against reference values: expose to known CO / NO2
      concentrations (competent operator only) and record raw-vs-reference
      curves. This is the evidence gate for any future customer promotion
      — do not fill any customer-facing value before it exists.

## 7. Formaldehyde / ozone (only if hardware exists per §1)

- [ ] SFA40: verify interface and unit; record warm-up and a response
      test against a known source.
- [ ] Ozone module (SEN0321 / ZE27-O3 via the STM8 stage): verify
      identity, interface and unit; record warm-up and response.

## 8. Pressure

- [ ] If a pressure part is fitted: compare against the reference
      barometer; record deltas and update interval.
- [ ] Confirm pressure never influences "Air Quality" or module status.

## 9. Freshness, failure and recovery

- [ ] Disconnect the SPS30 mid-operation: PM values go unknown (never
      frozen/stale values standing), module status becomes "Degraded",
      headline continues from remaining sensors.
- [ ] Reconnect: values return, module status returns to "Available".
- [ ] Power the board with all air-quality sensors detached: headline
      "Unavailable", recommendation "Unavailable", module status
      "Unavailable" — never "Fault" from ordinary absence.
- [ ] Confirm stale handling windows: block a sensor's updates and verify
      the value drops out after its stale window (90 s / 180 s).

## 10. Customer experience and multi-pollutant behaviour

- [ ] Air Quality headline: verify worst-pollutant behaviour with two
      simultaneous elevated pollutants (e.g. CO2 Poor + PM Very poor →
      headline Very poor, recommendation "Check pollution source").
- [ ] Recommendation wording review on-device: values match the contract
      exactly (Sensor initialising / No action needed / Ventilate soon /
      Ventilate now / Check pollution source / Unavailable).
- [ ] Home Assistant entity clarity: default-enabled set is exactly CO2,
      VOC, NOx, PM2.5, Air Quality, Recommendation (+ module status
      diagnostics); names carry no sensor part numbers or jargon.
- [ ] Diagnostics (enable manually): state detail, recommendation reason,
      expected sensors, data ages behave as documented.

## 11. Thermal, power and enclosure

- [ ] Thermal impact: record board temperature rise with the full stack
      running; check SCD41/SGP41 readings for self-heating effects in the
      enclosure vs open air.
- [ ] Power impact: record supply current of the full AirIQ stack (PoE
      and USB variants).
- [ ] Enclosure airflow effects: compare readings assembled-in-enclosure
      vs open board (diffusion paths for CO2/VOC/PM).

## 12. Operator sign-off (to be completed by the human operator only)

Intentionally empty — the operator records results, dates and any
attestation. Agents must never fill this section.

- Operator:
- Date:
- Hardware serials:
- Notes:

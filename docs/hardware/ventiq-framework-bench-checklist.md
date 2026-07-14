# VentIQ framework bench checklist (VENTIQ-FRAMEWORK-BENCH-001)

Results-free hardware-week checklist for physically validating the
VENTIQ-FRAMEWORK-001 software foundation on real S360-211 hardware in a
real bathroom composition (see
[`docs/architecture/sense360-ventiq-framework.md`](../architecture/sense360-ventiq-framework.md)).

**Prepared, not executed. This file contains no results.** Every box is
unchecked; the operator fills results and any attestation content —
attestations are never machine-written (standing rule). Until this
checklist is executed and recorded, the VentIQ framework remains
compile/simulation proof only: no accuracy, reliability, compliance or
safety property has been demonstrated, and every ventilation threshold
stays a provisional heuristic.

Reference equipment needed: a trusted reference hygrometer/thermometer,
a VOC source appropriate to a competent operator (e.g. a controlled
solvent/odour sample), a shower or humidifier able to raise room
humidity quickly, and a stopwatch/logger.

## 1. Board identity and fitment (S360-211-R4)

- [ ] Read the physical part markings on the assembled board: confirm
      the SGP41 (U3) — the only on-board sensor on the verified
      schematic.
- [ ] Resolve the SHT4x/BMP390 firmware/schematic drift on hardware
      (`VENTIQ-HW-DRIFT-001`): visually confirm whether ANY
      temperature/humidity or pressure part is populated on the VentIQ
      board; probe I2C 0x44 and 0x77 with the RoomIQ module DISCONNECTED
      and record what, if anything, responds.
- [ ] With RoomIQ connected, confirm the composition-level 0x44 sharing:
      record which physical sensor answers 0x44 on the shared bus.
- [ ] Record the fan-relay stage population (`VENTIQ-RELAY-POPULATION-001`):
      are K1 / D1 / Q1 / R2 / R3 fitted, or do-not-populate as the
      crossed-out schematic drawing suggests? Photograph the area. Make
      no mains connection during this identity check.
- [ ] Record the module-side connector silkscreen reference and pin
      count, and which Core connector (J1 5-pin vs J9 7-pin) the harness
      actually mates with (S360-100-BENCH-001 cross-item).
- [ ] Record whether an SPS30 (J4) or IR-temperature (J3) module is
      attached (both are optional external attachments; none is expected
      by the framework).

## 2. Transport and startup

- [ ] I2C bus scan after power-on with the full composition assembled:
      record every responding address on the shared bus.
- [ ] Cold boot: the SGP41's first valid VOC/NOx samples arrive within
      the provisional 120 s conditioning window; "Recommendation" shows
      "Sensor initialising" until usable data exists, never a fault.
- [ ] VentIQ Module Status transitions Initialising → Available on real
      data; never reports Available before a real SGP41 sample.
- [ ] Reboot (OTA restart) mid-operation: states recover, no stuck
      "Unavailable"/"Initialising".

## 3. Humidity service (RoomIQ canonical input)

- [ ] Canonical Humidity vs the reference hygrometer at steady state:
      record the delta at typical bathroom conditions.
- [ ] Disconnect/mask the RoomIQ climate path: canonical humidity goes
      unknown; Shower Active drops (never a frozen claim); the mould
      accumulator freezes; VentIQ Module Status stays driven by the
      SGP41 only (RoomIQ status reports its own outage).
- [ ] Verify the "Humidity Input Data Age" diagnostic tracks the real
      update cadence.

## 4. Shower detection (real shower)

- [ ] Run a real shower: record time-to-detect from water-on (rate
      trigger) and the humidity trace.
- [ ] Confirm the reason ladder: "Shower in progress" → (shower ends) →
      "Clearing shower moisture" → "No ventilation needed", with the
      post-shower window matching the configured duration.
- [ ] Confirm a slow passive humidity rise (no shower) does NOT trigger
      shower detection but does raise "High humidity" advice at the
      configured threshold.
- [ ] Adjust the Shower Detection Threshold number and confirm the new
      value actually applies (pre-framework these controls were placebo).
- [ ] Toggle the Shower Detection switch off and confirm detection
      pauses while humidity/air advice continues.

## 5. Damp / mould tracking

- [ ] Hold humidity above the mould threshold and confirm the risk
      ladder timing (low ≈ half the configured duration, medium at the
      duration, high at twice) and the "Damp for a long time" reason.
- [ ] Confirm drying below the threshold resets the accumulator, and
      Reset Mold Risk clears it immediately.

## 6. Air quality and odour (SGP41)

- [ ] Introduce a controlled VOC/odour source: VOC index rises; "Odour
      detected" appears at the canonical Fair boundary; Air Quality and
      Recommendation escalate at Poor / Very poor with the ventilation
      reasons matching.
- [ ] Confirm VOC/NOx values go unknown (not frozen) when the SGP41 is
      masked/disconnected, VentIQ Module Status degrades honestly, and
      the humidity-driven service keeps operating.
- [ ] Record the SGP41 conditioning behaviour after long power-off
      (index re-baselining) for threshold-tuning input.

## 7. Manual actions

- [ ] Force Ventilation: recommendation goes to "Ventilate now" /
      "Ventilation requested" for the configured window, then releases.
- [ ] Reset Shower Detection: clears an active shower/clearing state.

## 8. Long-run

- [ ] 48 h soak in a real bathroom: no reboot loops, no stuck states,
      module status reflects reality throughout; record any false
      shower/odour positives for threshold tuning.

## 9. Operator sign-off (to be completed by the human operator only)

This section is deliberately empty scaffolding for the operator's
attestation. Agents must never fill this section.

- Operator:
- Date:
- Hardware serials:
- Results summary:
- Threshold changes recommended:

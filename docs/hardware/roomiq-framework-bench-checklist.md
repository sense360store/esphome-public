# RoomIQ framework bench checklist (ROOMIQ-FRAMEWORK-001)

**Status: PREPARED — NOT EXECUTED. No results are recorded here.**

This is the operator bench checklist for physically validating the RoomIQ
environmental framework
([`docs/architecture/sense360-roomiq-framework.md`](../architecture/sense360-roomiq-framework.md))
on real S360-100 + S360-200 hardware. Until the operator completes it, the
climate path, the ambient-light path (including the unresolved sensor
identity), every threshold, filter window and freshness default remain
**unverified** — the firmware carries compile and logic/simulation proof
only (standing invariant: *no false proof*).

Standing rule (do not regress): **attestations are never machine-written.**
This file is intentionally results-free; the human operator records
evidence and completes any attestation. Agents must not tick a box, fill a
result, or add dates/signatures here.

## Setup

- [ ] S360-100 Core (ceiling) + S360-200 RoomIQ fitted, running a
      framework build (any RoomIQ-bearing bundle)
- [ ] Home Assistant connected; default entities visible (Temperature,
      Humidity, Illuminance, Comfort, Environment State, Brightness,
      Temperature Offset, Humidity Offset, Illuminance Calibration);
      diagnostic entities enabled for the session
- [ ] Trusted reference thermometer, reference hygrometer and (where
      available) a lux meter on hand

## Sensor identity (ENTITY-RECONCILE-200-ALS-001)

Firmware is now reconciled to the schematic/BOM part: the compiled driver is
LTR-303ALS-01 @ 0x29 via the built-in `ltr_als_ps` platform (ALS-only), and
SHT45 (`SHT45-AD1B-R3`) @ 0x44 via `sht4x`
(S360-200-R4-HARDWARE-RECONCILIATION-001), and — added by
S360-200-R4-BMP581-001 — the fitted BMP581 pressure sensor (`U4`) @ 0x47 via
the built-in `bmp581_i2c` platform (JP1 default `VDD` strap). This checklist
now confirms the parts **respond on hardware** — the current board under test
lists 0x29 (LTR-303ALS-01), 0x44 (SHT45), 0x47 (BMP581), 0x59 (SGP41), 0x60
(STM8/MICS) and 0x62 (SCD41) on its I²C scan, with the LTR and SHT45 now
initialising.

- [ ] Read the fitted ambient-light sensor part marking on `U1` (expect
      LTR-303ALS-01), the temp/humidity part on `U2` (expect SHT45) and the
      pressure part on `U4` (expect BMP581)
- [ ] Probe / scan the I²C bus: does a device answer at **0x29**
      (LTR-303ALS-01), at **0x44** (SHT45) and at **0x47** (BMP581)?
- [ ] If absent, investigate the physical population / J6 connector seating /
      +3.3 V rail to U1/U2/U4 (the bus is proven live if AirIQ answers at
      0x59/0x60/0x62)
- [ ] Record whether the reconciled `ltr_als_ps` lux path and `sht4x`
      temperature/humidity path produce live data on this board
- [ ] Record whether the `bmp581_i2c` pressure path produces live data on this
      board
- [ ] Record the ALS_INT line behaviour on GPIO47 (open-drain, active-low,
      raw diagnostic only — `ltr_als_ps` does not arm the LTR thresholds)
- [ ] Confirm the fitted `JP1` strap position matches the firmware address
      (default `VDD` → 0x47; `GND` → 0x46). If the physical strap is `GND`,
      the firmware address must be reconciled to 0x46 before pressure reads

## Temperature

- [ ] Temperature comparison against the trusted reference at stable
      room conditions (record delta before calibration)
- [ ] Temperature response time: move the device between two rooms /
      apply a controlled temperature step; record time to settle
- [ ] Sensor update interval observed (expected: one valid update per
      30 s)
- [ ] Self-heating / mounting bias noted (ceiling vs reference height)

## Humidity

- [ ] Humidity comparison against the trusted reference (record delta
      before calibration)
- [ ] Humidity response time: shower/kettle step test; record rise and
      recovery behaviour
- [ ] Warm and humid scenario: confirm Comfort reports "Warm and humid"
      under a real warm + humid condition and recovers afterwards

## Pressure (BMP581, U4 — S360-200-R4-BMP581-001)

The customer-facing pressure entity is `comfort_ceiling_pressure`
("<friendly_name> Pressure", hPa). The BMP581 die-temperature channel is a
disabled-by-default diagnostic only — SHT45 stays the canonical RoomIQ
temperature.

- [ ] Pressure entity reads a plausible sea-level-adjusted value for the test
      altitude against a trusted reference barometer (record delta; expect
      roughly 950–1050 hPa near sea level)
- [ ] Pressure update interval observed (expected: one valid update per 30 s)
- [ ] Value is reported in hPa (the driver's raw pascals are converted by the
      documented Pa → hPa unit filter)
- [ ] BMP581 diagnostic temperature, when enabled, tracks the room within the
      part's tolerance but is NOT used as the canonical Temperature
- [ ] Stale/disconnect: pressure goes unknown (never frozen) if the BMP581
      stops answering; RoomIQ framework availability is unaffected (pressure is
      not a framework input in this slice)

## Illuminance

- [ ] Lux comparison against a trusted meter at several levels (dark
      room, dim lamp, normal lighting, bright daylight) where available
- [ ] Illuminance update interval observed (expected: ~10 s cadence)
- [ ] Median filter behaviour: brief light flicker does not flap the
      reading; a real light change lands within ~20-30 s

## Brightness categories

- [ ] Each category reachable: Dark / Dim / Normal / Bright / Very
      bright at the provisional 10 / 50 / 300 / 1000 lx bands — record
      whether the bands match room perception
- [ ] Hysteresis: hold light near a band boundary; confirm the category
      does not flap

## Comfort thresholds

- [ ] Cold / Cool / Comfortable / Warm / Hot bands compared against
      occupant perception (record proposed threshold adjustments)
- [ ] Dry / Humid bands compared against occupant perception
- [ ] Boundary behaviour: temperature held near 24 °C does not flap
      Comfort (0.3 °C hysteresis)

## Calibration

- [ ] Apply a Temperature Offset from the reference delta; confirm the
      canonical Temperature, Comfort and legacy entities all move once
      (no double application anywhere)
- [ ] Apply a Humidity Offset; same single-application check
- [ ] Apply an Illuminance Calibration multiplier from the lux-meter
      ratio; confirm Illuminance, Brightness and the LED darkness
      behaviour all follow
- [ ] Reboot persistence: all three calibration values survive a power
      cycle
- [ ] Bounds: attempting out-of-range values is clamped, never applied

## Stale data / disconnect / recovery

- [ ] Disconnect / disturb the RoomIQ module (or its I²C bus) while
      running: Temperature/Humidity/Illuminance go unknown (never
      frozen), Comfort/Brightness go Unavailable, module status goes
      Degraded then Unavailable as channels expire
- [ ] Partial failure: with climate alive and light failed (or vice
      versa) module status reports Degraded and the surviving outputs
      stay usable
- [ ] Recovery: reconnect; confirm values, states and module status
      return to Available without a reboot
- [ ] Startup: after power-on the states show Initialising (never a
      fault) until first valid data

## LED integration (with an LED-bearing build)

- [ ] Darkness Threshold behaviour unchanged: room below threshold →
      "When dark" Night Mode activates; above threshold × 1.5 it
      deactivates; near-threshold light does not flap (hysteresis)
- [ ] Stale/failed lux freezes night automation safely (no toggling,
      LED Darkness State diagnostic shows Unknown)
- [ ] Illuminance Calibration shifts the effective darkness point as
      documented

## Home Assistant entity clarity

- [ ] Default entity set reads clearly to a non-technical user (names,
      values, no jargon, no sensor model names)
- [ ] Environment State adds value next to Comfort and Brightness
      (record whether customers find it duplicative — scope fallback is
      documented in the architecture doc)
- [ ] Diagnostics stay hidden by default; legacy compatibility entities
      remain available (disabled) for existing automations

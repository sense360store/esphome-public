# LED framework bench checklist (LED-FRAMEWORK-BENCH-001)

**Status: PREPARED — NOT EXECUTED. No results are recorded in this file.**

Operator bench checklist for physically validating the LED-FRAMEWORK-001
customer experience on real S360-100 Core + S360-300 LED hardware
(framework: [`docs/architecture/sense360-led-framework.md`](../architecture/sense360-led-framework.md)).
Every brightness, colour and timing value in the framework is a
provisional software definition until the items below are executed.

Standing rule (do not regress): **attestations are never machine-written.**
Results, measurements, dates and sign-off in this checklist are completed
by the human operator only. Agents may update the *checklist structure*
but must never fill in results or evidence claims.

## Setup

- [ ] S360-100 Core (R4) + S360-300 LED (R4) + S360-200 RoomIQ (R4) on the
      PoE PSU, flashed with a LED-bearing preview build
      (`Ceiling-POE-RoomIQ-LED` or `Ceiling-POE-VentIQ-RoomIQ-LED`).
- [ ] Record firmware version, config string and head SHA used.
- [ ] Resolve the **supply rail question**: measure the actual voltage on
      LED J1 pin 2 (schematic capture says Core J3 pin 1 = +3.3V while the
      LED module labels J1 pin 2 = +5V; open question in
      `docs/hardware/s360-300-r4-led.md`, S360-300-BENCH-001).
- [ ] Confirm the physical LED count against the silkscreen (firmware
      asserts 12 for the ceiling ring — not yet silkscreen-verified).
- [ ] Confirm which ambient-light sensor the S360-200 actually carries
      (hardware catalog says LTR-303ALS; compiled firmware drives a
      VEML7700 at 0x10 — documentation-vs-firmware mismatch to resolve).

## Room Light basics

- [ ] Correct colour / channel order: commanded red is red, green is
      green, blue is blue (GRB firmware binding verified physically).
- [ ] Minimum visible brightness through the diffuser (find the lowest
      distinguishable brightness step).
- [ ] Maximum safe brightness: full white at 100% for a sustained period —
      record current draw, PSU behaviour and any brown-out/flicker.
- [ ] Thermal behaviour: full white for 10+ minutes — record temperature
      rise on the LED board and Core, and any colour shift.
- [ ] Power draw at 25 / 50 / 100% white and in the night profile.
- [ ] Diffuser appearance: hot spots, colour uniformity, bleed.
- [ ] Transitions and flicker: 300 ms default transitions are smooth; no
      visible PWM/RMT flicker at low brightness; slow effects (Gentle
      Pulse, Night Glow) show no stepping.

## Night Mode

- [ ] Night-mode comfort in a dark room: is 5% warm output non-disruptive
      and still useful? Record a better brightness/colour if found.
- [ ] Warm colour quality of the provisional mix (1.0/0.58/0.16) through
      the diffuser (blue-heaviness check).
- [ ] Turning Night Mode off restores the exact previous light state
      (including a previous off state and a previous active effect).

## Restore after restart

- [ ] Power-cycle with the Room Light on at a chosen brightness/colour —
      the same state returns after boot; no full-brightness flash.
- [ ] Power-cycle mid-identify and mid-status-blip — the transient does
      NOT reappear; the stable customer state returns.
- [ ] Power-cycle with Night Mode on — Night Mode state and ownership
      survive.
- [ ] Safe-mode boot leaves the ring dark.

## Identify action

- [ ] Identify Device runs the pulse and automatically restores the
      previous state (test from idle, from light-on, and from Night Mode).
- [ ] Identify visibility: recognisable across the room but
      non-disruptive; record perceived intensity.

## Status indication visibility

- [ ] Startup blip visible after boot when the ring is idle.
- [ ] Home Assistant connect blip appears on (re)connection; disconnect
      warning appears when HA drops (Essential level).
- [ ] No status blip interrupts an ON Room Light or active Night Mode.
- [ ] Status Indicator "Off" silences everything; "Detailed" adds the
      network events.

## Automation (Presence + lux)

- [ ] Presence-triggered Night Mode: "When dark and occupied" turns the
      night light on when entering a dark room, and off after the room
      clears (Presence clear delay + 60 s auto-off).
- [ ] A fresh occupancy event during the auto-off window cancels the
      pending off.
- [ ] Manual override: turning Night Mode off while dark+occupied stays
      off; it re-arms only after the room goes bright/empty.
- [ ] Lux threshold: measure real lux at the mounted position and verify
      dark/not-dark transitions around the configured threshold.
- [ ] Hysteresis: lux hovering just around the threshold does not flap
      the light.
- [ ] Stale lux fail-safe: cover/disconnect the light sensor — darkness
      state reports Unknown, automation freezes, no toggling.
- [ ] Degraded Presence (unplug the LD2450): no flashing or repeated
      night-mode toggles.

## Modes and controls

- [ ] Compare Manual / When dark / When dark and occupied behaviours in a
      realistic evening scenario; record which defaults feel right.
- [ ] Effects: Gentle Pulse and Night Glow look calm through the
      diffuser; no strobe-like artefacts.
- [ ] Home Assistant control latency: light commands, Night Mode switch
      and Identify respond promptly (record worst-case latency).

## Failure / recovery behaviour

- [ ] Disconnect the LED module data line while running — record firmware
      behaviour (no crash/reboot loop) and that no false health claim
      appears (LED Module Status stays "Included").
- [ ] WiFi loss and recovery: warning/info blips at the configured level;
      no stuck overlay.
- [ ] Rapid repeated events (identify spam, connect/disconnect cycles)
      leave the ring in a correct, non-stuck state.

## Evidence

*(Operator-only. Record measurements, photos, firmware SHA, dates and
sign-off here. Intentionally left empty — no results, no attestation is
machine-written.)*

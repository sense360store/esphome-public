# Presence framework bench checklist (PRESENCE-FRAMEWORK-001)

**Status: PREPARED — NOT EXECUTED. No results are recorded here.**

This is the operator bench checklist for physically validating the
tri-sensor Presence framework
([`docs/architecture/sense360-presence-framework.md`](../architecture/sense360-presence-framework.md))
on real S360-100 + S360-200 hardware. Until the operator completes it,
PIR / LD2450 / SEN0609 behaviour, all timing defaults, and every fusion
preset remain **unverified** — the merged firmware carries compile and
logic/simulation proof only (standing invariant: *no false proof*).

Standing rule (do not regress): **attestations are never machine-written.**
This file is intentionally results-free; the human operator records
evidence and completes any attestation. Agents must not tick a box, fill a
result, or add dates/signatures here.

## Setup

- [ ] S360-100 Core (ceiling) + S360-200 RoomIQ with PIR (IO15), LD2450
      (`roomiq_hi_link_uart`, 256000) and SEN0609 (out on IO6,
      `roomiq_sen0609_uart` idle) fitted, running a tri-sensor build
- [ ] Home Assistant connected; default entities visible (Occupancy,
      Presence Status, Radar Target Count, Presence Mode, Clear Delay);
      diagnostic entities enabled for the session

## PIR

- [ ] PIR trigger latency: walk-in to Occupancy=on (target: immediate;
      record measured latency)
- [ ] PIR false triggers: empty room, 30 min observation (HVAC on/off);
      count false Movement detected events
- [ ] PIR warm-up: power-cycle; confirm edges inside the 30 s window are
      ignored and no false fault is raised

## LD2450

- [ ] Moving detection: walking occupant tracked as Movement detected
- [ ] Still detection: motionless occupant held as Still presence
- [ ] Target count: 1 / 2 / 3 occupants vs Radar Target Count readings
- [ ] Coordinate accuracy: known positions vs Radar Target N X/Y/distance
      (record deviations; Zones prerequisite)
- [ ] Target speed / angle plausibility during walking passes

## SEN0609

- [ ] Static presence: seated occupant, 30+ min, no false clear
- [ ] SEN0609 warm-up: power-cycle; levels inside the 15 s window ignored

## Fusion scenarios

- [ ] Seated occupant (low motion): Occupancy stays on; status Still presence
- [ ] Sleeping / very still occupant: extended hold in Stable mode
- [ ] Walking entry: immediate assertion (which sensor fired first)
- [ ] Rapid room exit: clear after configured Clear Delay (measure actual)
- [ ] Multiple occupants: "Multiple targets" status appears; count
      plausibility (bench evidence here is the prerequisite for any owner
      decision to promote the wording to "Multiple people")
- [ ] Clear delay: verify 5 s / 30 s / 600 s settings honoured; persistence
      across reboot
- [ ] Mode comparison: Balanced vs Responsive vs Stable side-by-side
      (assertion latency, clear behaviour, false-clear resistance);
      Custom preserves user clear delay

## Failure / recovery

- [ ] One sensor disconnected (LD2450 unplugged): module status Degraded;
      occupancy maintained by PIR/SEN0609; no false clear
- [ ] Two sensors disconnected: remaining sensor still asserts; module
      status Degraded; conservative fallback observed
- [ ] UART recovery: reconnect LD2450; frames resume; module status returns
      to Available without reboot
- [ ] Startup timing: boot-to-Available time; Initialising shown during
      warm-up; no false Unavailable

## Interactions

- [ ] Sense360Zones prerequisites: coordinate stream fidelity and freshness
      evidence sufficient for zone mapping (no Zones firmware change in
      scope — data-contract observation only)

## Evidence

(intentionally blank — operator records bench evidence, dates and any
attestation here; agents must not fill this section)

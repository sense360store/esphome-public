<!--
Sense360 EXPERIMENTAL self-build mains release-notes DRAFT.
Canonical id: TRIAC-COMMISSIONING-001.
Lane: experimental self-build mains (EXPERIMENTAL-SELF-BUILD-MAINS-LANE),
defined by docs/decisions/COMPLIANCE-001-RESOLUTION-001.md.

Config string : Ceiling-POE-VentIQ-FanTRIAC-RoomIQ
Family        : FanTRIAC (S360-320)
Version       : 1.0.0
Channel       : experimental
Artifact      : Sense360-Ceiling-POE-VentIQ-FanTRIAC-RoomIQ-v1.0.0-experimental.bin
Bench proof   : docs/package-triac-001-operator-bench-proof.md (PACKAGE-TRIAC-001, operator-attested)

DRY-RUN DRAFT ONLY. This body is NOT attached to any GitHub Release by the
TRIAC-COMMISSIONING-001 PR; that PR adds the config/webflash-builds.json
experimental row but does NOT cut a release tag. The four H2 sections below are
validated structurally by `scripts/validate-webflash-release-notes.py
--channel experimental`. Replace the Changelog bullets with the human-authored,
user-visible changes before this draft is ever attached to a real experimental
Release.
-->

# Sense360 Bathroom PoE + mains TRIAC fan (VentIQ + FanTRIAC + RoomIQ) — EXPERIMENTAL self-build firmware

> ☠️ **EXPERIMENTAL — SELF-BUILD MAINS HARDWARE.** This firmware targets an
> open-source mains-voltage board design that Sense360 does not sell, supply,
> or place on the market in any form. If you build this board you are the
> manufacturer of your own device and act entirely at your own risk.
> Functional bench completion is NOT a safety, EMC, or compliance
> certification. Mains wiring must only be performed by a competent person.
> Incorrect installation can cause fire, electric shock, or death.

> ⚠️ **Self-build, competent-person manual install only.** The Sense360 TRIAC
> (`S360-320`) is an **open-source CERN-OHL-P design that Sense360 never sells,
> supplies, or places on the market**. You source the parts and build the board
> yourself, as a **self-builder of your own device**. This is **NOT stable**,
> **NOT recommended**, **NEVER a customer default**, **not buyable as a public
> shop product**, and **not part of any kit**. Normal customers should use the
> **stable Bathroom PoE release** (`S360-KIT-BATH-P` / `Ceiling-POE-VentIQ-RoomIQ`,
> artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`) instead.

## Changelog

- First **experimental self-build** firmware for the
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` target (Bathroom PoE with the `S360-320`
  Sense360 TRIAC mains phase-cut fan/lamp dimmer), published on the
  **experimental** channel via the experimental self-build mains lane
  (`docs/decisions/COMPLIANCE-001-RESOLUTION-001.md`).
- **Firmware is bench-validated, functionally.** The `PACKAGE-TRIAC-001`
  operator bench protocol is complete and **operator-attested**
  (`docs/package-triac-001-operator-bench-proof.md`): zero-cross lock, gate
  timing, a clean leading-edge phase cut on a real Manrose inductive fan motor,
  a thermal soak, boot/stability, and the full-composition re-confirm all
  passed on the schematic-verified pins (gate `IO14`, zero-cross `IO13`). This
  is **functional bench + firmware-build proof only** and carries **no
  electrical-safety, EMC, or compliance claim** of any kind.
- No customer-facing change to any stable build. This does **NOT** make
  FanTRIAC stable, recommended, a customer default, buyable, or part of any kit
  or kit picker, and it adds no entry to `release_one_required_configs`.

## Known Issues

- **Mains-voltage / AC-load risk.** TRIAC phase-cut control switches a
  mains-connected (AC) load. Installation is for a **competent person**
  performing a manual install only, and all mains wiring must be done **to
  local regulations**. Incorrect installation can cause fire, electric shock,
  or death.
- **No safety, EMC, or compliance certification.** The bench proof validates
  function only. Electrical safety, isolation, creepage, clearance, EMC, and
  CE / UKCA conformity sit outside that bench. Because the `S360-320` is never
  placed on the market by Sense360, no conformity assessment is owed; it would
  become an obligation only if the board were ever placed on the market, which
  Sense360 does not do.
- **Self-build, own-risk.** You build the open-source board from your own
  sourcing and **flash and use this firmware entirely at your own risk**. Keep
  the rescue / stable firmware on hand to recover.

## Features

- PoE-powered Sense360 Core configuration
- VentIQ bathroom air-quality sensing
- RoomIQ room sensing
- Mains TRIAC phase-cut fan/lamp dimming on the `S360-320` Sense360 TRIAC
  (experimental self-build; competent-person manual install only)

## Hardware Requirements

- Sense360 Core (`S360-100`)
- Sense360 PoE PSU (`S360-410`)
- Sense360 VentIQ (`S360-211`)
- Sense360 RoomIQ (`S360-200`)
- Sense360 TRIAC (`S360-320`) — mains phase-cut dimmer; **open-source CERN-OHL-P
  design that Sense360 never sells, supplies, or places on the market**.
  Schematic-verified pin mapping (`TRI_GPIO1`/`TRI_GPIO2` → `IO14`/`IO13`),
  operator bench attestation recorded (`PACKAGE-TRIAC-001`); self-built and
  installed by a competent person, to local regulations, at the builder's own
  risk.

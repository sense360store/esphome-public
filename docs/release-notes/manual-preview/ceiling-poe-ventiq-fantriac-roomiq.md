<!--
Sense360 ADVANCED PREVIEW release-notes DRAFT (advanced-manual-preview lane).
Canonical id: RELEASE-PREVIEW-FAN-TRIAC-BUILD-ROWS-001.

Config string : Ceiling-POE-VentIQ-FanTRIAC-RoomIQ
Family        : FanTRIAC (S360-320)
Version       : 1.0.0
Channel       : preview (advanced-preview tier)
Delivery lane : advanced-manual-preview
Artifact      : Sense360-Ceiling-POE-VentIQ-FanTRIAC-RoomIQ-v1.0.0-preview.bin (buildable; not yet published)
WebFlash      : NOT WebFlash-importable (advanced acknowledgement UX gated; no config/webflash-builds.json row)
Build status  : BUILDABLE — TRIAC-UNBLOCK-BUILD-001 resolved the HW-005 buildability blocker (firmware-build compile only).

DRY-RUN DRAFT ONLY. This body is NOT attached to any GitHub Release by the
RELEASE-PREVIEW-FAN-TRIAC-BUILD-ROWS-001 PR. No firmware binary, GitHub Release,
tag, manifest.json, or firmware/sources.json is produced. The four H2 sections
below are validated structurally by
`scripts/validate-webflash-release-notes.py --channel preview`. This draft
records the ADVANCED-PREVIEW posture only; it claims firmware-build compile proof
only and NO hardware, bench, electrical-safety, or compliance proof. Replace the
Changelog bullets with the human-authored, user-visible changes before this draft
is ever attached to a real preview Release (publishing the artifact is the
separate TRIAC-PUBLISH-ADVANCED-PREVIEW-001 follow-up).
-->

# Sense360 Bathroom PoE + mains TRIAC fan (VentIQ + FanTRIAC + RoomIQ) — ADVANCED PREVIEW firmware draft

> ☠️ **ADVANCED PREVIEW — MAINS-VOLTAGE RISK.** This firmware drives
> mains-voltage hardware (TRIAC phase-control dimming) and is for **competent
> persons performing a manual installation only**. It is **NOT hardware
> verified**, **NOT stable**, **NOT recommended**, and is **NEVER a default**.
> **No bench evidence and no electrical-safety / compliance certification is
> claimed.** **Incorrect installation can cause fire, electric shock, or
> death. Do not install unless you are qualified to work on mains wiring.**

> ⚠️ **Advanced / manual install only.** This is an **advanced-preview**,
> installer-only configuration. It is **NOT a customer default**, **NOT
> compliance certified**, and **not buyable as a public shop product**. It is
> delivered via the **advanced-manual-preview** lane only and is **not**
> WebFlash-importable. The `HW-005` buildability blocker is **resolved**
> (TRIAC-UNBLOCK-BUILD-001: the SX1509-free Core respin routes TRI_GPIO1/TRI_GPIO2
> direct to interrupt-capable ESP32-S3 GPIOs — gate IO14, zero-cross IO13), so
> the target now compiles; this is **firmware-build compile proof only** and
> **no hardware, bench, or compliance proof exists or is claimed.** The artifact
> is buildable but **not yet published** (publish is a separate follow-up).
> Normal customers should use the **stable Bathroom PoE release**
> (`S360-KIT-BATH-P` / `Ceiling-POE-VentIQ-RoomIQ`, artifact
> `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`) instead.

## Changelog

- ADVANCED-PREVIEW dry-run draft for the advanced-manual-preview
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` target (Bathroom PoE with the S360-320
  Sense360 TRIAC mains phase-cut fan/lamp dimmer). This records the
  advanced-preview posture only — it is **NOT stable**, **NOT recommended**, and
  **NOT a customer default**.
- **Buildability resolved (firmware-build compile proof only).**
  TRIAC-UNBLOCK-BUILD-001 cleared the `HW-005` buildability blocker: the
  SX1509-free S360-100-R4 Core respin routes the J15 TRIAC nets
  TRI_GPIO1/TRI_GPIO2 direct to interrupt-capable ESP32-S3 GPIOs (gate IO14,
  zero-cross IO13), replacing the placeholder GPIO5/GPIO6 that collided with
  RoomIQ on J10, so ESPHome `ac_dimmer` compiles. The target is registered in
  the compile-only validation lane. No hardware, bench, compliance, or
  commercial-availability proof is claimed.
- No GitHub Release, tag, `.bin`, `manifest.json`, or `firmware/sources.json`
  is published. The target is **not** added to `config/webflash-builds.json` and
  is **not** forced into the normal WebFlash preview path; it stays
  advanced-manual-preview behind an explicit acknowledgement gate.

## Known Issues

- **Mains-voltage / AC-load risk.** TRIAC phase-cut control switches a
  mains-connected (AC) load. Installation is for a competent person performing a
  manual install only; incorrect installation can cause fire, electric shock, or
  death.
- NOT hardware verified and NOT compliance certified: stable / full release
  stays blocked by `PACKAGE-TRIAC-001` and the `COMPLIANCE-001` mains-voltage
  review. This target never auto-promotes to stable, is **not buyable as a public
  shop product**, and is **not a customer default**; the launch shop product
  stays the stable Bathroom PoE kit (`S360-KIT-BATH-P`).
- Buildability is firmware-build compile proof only; bench validation of the
  zero-cross detection, gate timing, and real-load behaviour has **not** been
  performed.

## Features

- PoE-powered Sense360 Core configuration
- VentIQ bathroom air-quality sensing
- RoomIQ room sensing
- Mains TRIAC phase-cut fan/lamp dimming on the S360-320 Sense360 TRIAC (advanced, competent-person manual install only)

## Hardware Requirements

- Sense360 Core (`S360-100`)
- Sense360 PoE PSU (`S360-410`)
- Sense360 VentIQ (`S360-211`)
- Sense360 RoomIQ (`S360-200`)
- Sense360 TRIAC (`S360-320`) — mains phase-cut dimmer; schematic-backed pin mapping (TRI_GPIO1/2 → IO14/IO13), bench verification + `COMPLIANCE-001` pending

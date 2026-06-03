<!--
Sense360 ADVANCED PREVIEW release-notes DRAFT (advanced-manual-preview lane).
Canonical id: RELEASE-PREVIEW-FAN-TRIAC-BUILD-ROWS-001.

Config string : Ceiling-POE-VentIQ-FanTRIAC-RoomIQ
Family        : FanTRIAC (S360-320)
Version       : 1.0.0
Channel       : preview (advanced-preview tier)
Delivery lane : advanced-manual-preview
Artifact      : Sense360-Ceiling-POE-VentIQ-FanTRIAC-RoomIQ-v1.0.0-preview.bin (NOT yet buildable)
WebFlash      : NOT WebFlash-importable (advanced acknowledgement UX gated; no config/webflash-builds.json row)
Build status  : BUILD-BLOCKED by HW-005 — no compile / firmware artifact exists.

DRY-RUN DRAFT ONLY. This body is NOT attached to any GitHub Release by the
RELEASE-PREVIEW-FAN-TRIAC-BUILD-ROWS-001 PR. No firmware binary, GitHub Release,
tag, manifest.json, or firmware/sources.json is produced. The four H2 sections
below are validated structurally by
`scripts/validate-webflash-release-notes.py --channel preview`. This draft
records the ADVANCED-PREVIEW posture only; it claims NO compile, build, hardware,
bench, electrical-safety, or compliance proof. Replace the Changelog bullets with
the human-authored, user-visible changes before this draft is ever attached to a
real preview Release (which cannot happen until the HW-005 buildability blocker
is resolved).
-->

# Sense360 Bathroom PoE + mains TRIAC fan (VentIQ + FanTRIAC + RoomIQ) — ADVANCED PREVIEW firmware draft

> ☠️ **ADVANCED PREVIEW — MAINS-VOLTAGE RISK.** This firmware drives
> mains-voltage hardware (TRIAC phase-control dimming) and is for **competent
> persons performing a manual installation only**. It is **NOT hardware
> verified**, **NOT stable**, **NOT recommended**, and is **NEVER a default**.
> **No bench evidence and no electrical-safety / compliance certification is
> claimed.** **Incorrect installation can cause fire, electric shock, or
> death. Do not install unless you are qualified to work on mains wiring.**

> ⚠️ **Advanced / manual install only — and not yet buildable.** This is an
> **advanced-preview**, installer-only configuration. It is **NOT a customer
> default**, **NOT compliance certified**, and **not buyable as a public shop
> product**. It is delivered (once buildable) via the **advanced-manual-preview**
> lane only and is **not** WebFlash-importable. **It is NOT yet buildable:** the
> `HW-005` buildability blocker means no firmware artifact can be cut, so **no
> compile, hardware, bench, or compliance proof exists or is claimed.** Normal
> customers should use the **stable Bathroom PoE release** (`S360-KIT-BATH-P` /
> `Ceiling-POE-VentIQ-RoomIQ`, artifact
> `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`) instead.

## Changelog

- ADVANCED-PREVIEW dry-run draft for the advanced-manual-preview
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` target (Bathroom PoE with the S360-320
  Sense360 TRIAC mains phase-cut fan/lamp dimmer). This records the
  advanced-preview posture only — it is **NOT stable**, **NOT recommended**, and
  **NOT a customer default**.
- **No compile or build proof:** unlike the FanRelay / FanPWM / FanDAC
  manual-preview builds, this target is **build-blocked by `HW-005`** (S360-320
  schematic uncommitted; placeholder GPIO5/GPIO6 collide with RoomIQ J10 nets;
  ESPHome `ac_dimmer` cannot run across the SX1509 expander). It is **not
  buildable end-to-end**, so it was **not** added to the preview compile matrix
  and no firmware artifact can be cut. No hardware, bench, compliance, or
  commercial-availability proof is claimed.
- No GitHub Release, tag, `.bin`, `manifest.json`, or `firmware/sources.json`
  is published. The target is **not** added to `config/webflash-builds.json` and
  is **not** forced into the normal WebFlash preview path; it stays
  advanced-manual-preview behind an explicit acknowledgement gate.

## Known Issues

- **Build-blocked (`HW-005`).** The advanced-preview artifact **cannot be cut**
  until the S360-320 schematic is committed and the GPIO5/GPIO6 collision and
  `ac_dimmer`-across-SX1509 timing defect are resolved. No `-preview.bin`
  currently exists.
- **Mains-voltage / AC-load risk.** TRIAC phase-cut control switches a
  mains-connected (AC) load. Installation is for a competent person performing a
  manual install only; incorrect installation can cause fire, electric shock, or
  death.
- NOT hardware verified and NOT compliance certified: stable / full release
  stays additionally blocked by `PACKAGE-TRIAC-001` and the `COMPLIANCE-001`
  mains-voltage review. This target never auto-promotes to stable, is **not
  buyable as a public shop product**, and is **not a customer default**; the
  launch shop product stays the stable Bathroom PoE kit (`S360-KIT-BATH-P`).

## Features

- *(Intended capability — NOT yet buildable; see Known Issues.)*
- PoE-powered Sense360 Core configuration
- VentIQ bathroom air-quality sensing
- RoomIQ room sensing
- Mains TRIAC phase-cut fan/lamp dimming on the S360-320 Sense360 TRIAC (advanced, competent-person manual install only)

## Hardware Requirements

- Sense360 Core (`S360-100`)
- Sense360 PoE PSU (`S360-410`)
- Sense360 VentIQ (`S360-211`)
- Sense360 RoomIQ (`S360-200`)
- Sense360 TRIAC (`S360-320`) — mains phase-cut dimmer; schematic / pin mapping unverified (`HW-005`)

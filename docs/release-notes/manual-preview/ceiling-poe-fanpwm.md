<!--
Sense360 PREVIEW release-notes DRAFT (manual-preview lane).
Canonical id: RELEASE-PREVIEW-FAN-TRIAC-BUILD-ROWS-001.

Config string : Ceiling-POE-FanPWM
Family        : FanPWM (S360-311)
Version       : 1.0.0
Channel       : preview
Delivery lane : manual-preview (config/manual-firmware-artifacts.json)
Artifact      : Sense360-Ceiling-POE-FanPWM-v1.0.0-preview.bin
WebFlash      : NOT WebFlash-importable (fan-token guardrail; no config/webflash-builds.json row)

DRY-RUN DRAFT ONLY. This body is NOT attached to any GitHub Release by the
RELEASE-PREVIEW-FAN-TRIAC-BUILD-ROWS-001 PR. No firmware binary, GitHub Release,
tag, manifest.json, or firmware/sources.json is produced. The four H2 sections
below are validated structurally by
`scripts/validate-webflash-release-notes.py --channel preview`. Replace the
Changelog bullets with the human-authored, user-visible changes before this
draft is ever attached to a real preview Release.
-->

# Sense360 PoE + PWM fan (12V PWM fan control) — PREVIEW firmware draft

> ⚠️ **PREVIEW FIRMWARE — not for normal customers.** This is a **PREVIEW**
> build. It is **NOT stable**, **NOT recommended**, and **NOT a customer
> default**. It is **NOT hardware verified** and **NOT compliance certified**,
> and it is **not buyable as a public shop product**. The only evidence behind
> this build is **firmware-build proof only, from hosted compile run
> `26821900127`** (`Preview Compile Dry-Run`, `workflow_dispatch` /
> `compile_mode=full`, 2026-06-02, ESPHome 2026.4.5). **No hardware, bench,
> compliance, or commercial-availability proof is claimed.** This build is
> delivered to testers via the **manual-preview** lane only — it is **not**
> WebFlash-importable. Normal customers should use the **stable Bathroom PoE
> release** (`S360-KIT-BATH-P` / `Ceiling-POE-VentIQ-RoomIQ`, artifact
> `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`) instead.

## Changelog

- PREVIEW dry-run draft for the manual-preview `Ceiling-POE-FanPWM` build (PoE
  Core driving the S360-311 Sense360 PWM board over the native ESP32-S3 GPIO
  PWM path). This is a PREVIEW, testers-only build: **NOT stable**, **NOT
  recommended**, and **NOT a customer default**.
- Firmware-build proof only: the canonical product YAML
  (`products/sense360-ceiling-poe-fanpwm.yaml`) compiled GREEN on hosted compile
  run `26821900127` (`Compile Dry-Run: Ceiling-POE-FanPWM`, result `success`).
  No hardware, bench, compliance, or commercial-availability proof is claimed.
- No GitHub Release, tag, `.bin`, `manifest.json`, or `firmware/sources.json`
  is published by this draft. The build is **not** added to
  `config/webflash-builds.json` (the fan-token guardrail keeps fan drivers off
  the WebFlash build matrix); it is delivered via the manual-preview lane only.

## Known Issues

- NOT hardware verified and NOT compliance certified: this preview build has no
  bench, hardware, EMC, or electrical-safety / compliance proof, and no
  commercial-availability proof.
- No RPM / tach claim: the native `pulse_counter` tach inputs are exposed as
  internal diagnostic pulse-rate inputs only (`rpm_supported: false`).
- Stable promotion stays blocked by measured current / thermal evidence
  (`S360-311-CURRENT-THERMAL-001`). This build is preview-only and never
  auto-promotes to stable.
- Not a shop product: this configuration is **not buyable as a public shop
  product** and is **not a customer default**; the launch shop product stays the
  stable Bathroom PoE kit (`S360-KIT-BATH-P`).

## Features

- PoE-powered Sense360 Core configuration
- Four-channel 12V PWM fan-speed control on the S360-311 Sense360 PWM board (native ESP32-S3 GPIO `ledc` outputs)
- Internal diagnostic tach pulse-rate inputs (no RPM claim)

## Hardware Requirements

- Sense360 Core (`S360-100`)
- Sense360 PoE PSU (`S360-410`)
- Sense360 PWM (`S360-311`)

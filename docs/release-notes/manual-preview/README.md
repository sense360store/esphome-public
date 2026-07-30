# Fan-control & TRIAC PREVIEW release-note drafts (dry-run)

**Canonical id:** `RELEASE-PREVIEW-FAN-TRIAC-BUILD-ROWS-001`

This directory holds **dry-run** release-note **drafts** for the four buildable
fan-control and TRIAC preview targets that are delivered on the **non-WebFlash**
preview lanes — the `manual-preview` lane (FanRelay / FanPWM / FanDAC) and the
`advanced-manual-preview` lane (FanTRIAC). They are deliberately kept **separate**
from the WebFlash preview drafts in
[`docs/release-notes/preview/`](../preview/) because these targets are **not**
WebFlash-importable (the fan-token guardrail keeps fan / TRIAC tokens out of
[`config/webflash-builds.json`](../../../config/webflash-builds.json)).

| Config string | Lane | Channel | Draft | Build status |
|---|---|---|---|---|
| `Ceiling-POE-VentIQ-FanRelay-RoomIQ` | `manual-preview` | preview | § `ceiling-poe-ventiq-fanrelay-roomiq` (below, marked section) | buildable (run `26821900127`) |
| `Ceiling-POE-FanPWM` | `manual-preview` | preview | § `ceiling-poe-fanpwm` (below, marked section) | buildable (run `26821900127`) |
| `Ceiling-POE-FanDAC` | `manual-preview` | preview | § `ceiling-poe-fandac` (below, marked section) | buildable (run `26821900127`) |
| `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` | `advanced-manual-preview` | advanced-preview | § `ceiling-poe-ventiq-fantriac-roomiq` (below, marked section) | **build-blocked (`HW-005`)** |

## These are drafts, not releases

Each draft is **validated structurally** against the WebFlash release-body
contract with `scripts/validate-webflash-release-notes.py --channel preview`
(the four required H2 sections: `## Changelog`, `## Known Issues`,
`## Features`, `## Hardware Requirements`), and is locked by
[`tests/test_preview_fan_triac_build_rows.py`](../../../tests/test_preview_fan_triac_build_rows.py).

They are **not** attached to any GitHub Release. No firmware binary, GitHub
Release, tag, `manifest.json`, or `firmware/sources.json` is produced; nothing
is promoted to stable; nothing becomes recommended / default / buyable.

* **FanRelay / FanPWM / FanDAC** are **firmware-build proof only** (hosted
  compile run `26821900127`, `proof_class: firmware-build-only`). A green
  compile is **not** hardware proof, bench evidence, compliance, stable
  promotion, or commercial availability.
* **FanTRIAC** is **build-blocked by `HW-005`** — it is **not buildable
  end-to-end**, so **no compile / firmware artifact exists** and **no compile,
  hardware, bench, or compliance proof is claimed**. Its draft carries the
  mandatory **mains-voltage** / AC-load warning and the installer-only,
  advanced-manual posture, and it is never forced into the normal WebFlash
  preview path.

Every draft is explicit that it is **PREVIEW** firmware — not stable, not
recommended, not a customer default, not hardware verified, not compliance
certified, and not buyable as a public shop product — and points normal
customers to the **stable Bathroom PoE release**
(`S360-KIT-BATH-P` / `Ceiling-POE-VentIQ-RoomIQ`).

See [`docs/release-preview-fan-triac-build-rows.md`](../../release-preview-fan-triac-build-rows.md)
for the full build-row readiness record, and
[`config/preview-fan-triac-build-rows.json`](../../../config/preview-fan-triac-build-rows.json)
for the machine-readable build-row ledger.

> **REPO-CONSOLIDATION-001 (2026-07-30): this README is now the single
> index page for the manual-preview lane.** The former per-config draft
> files were collapsed into the marked sections below (owner decision of
> 2026-07-30: advanced/experimental-lane notes collapse to one index page
> per channel; customer-configuration release notes under
> [`../preview/`](../preview/) keep individual pages). Every draft body,
> including all required warning copy, is preserved verbatim inside
> `<!-- draft:<Config-String>:start/end -->` markers; the drafting-record
> guards in `tests/test_preview_fan_triac_build_rows.py` assert against
> those sections. The links in the table above now resolve within this
> page.

---

<!-- draft:Ceiling-POE-VentIQ-FanRelay-RoomIQ:start -->
<!--
Sense360 PREVIEW release-notes DRAFT (manual-preview lane).
Canonical id: RELEASE-PREVIEW-FAN-TRIAC-BUILD-ROWS-001.

Config string : Ceiling-POE-VentIQ-FanRelay-RoomIQ
Family        : FanRelay (S360-310)
Version       : 1.0.0
Channel       : preview
Delivery lane : manual-preview (config/manual-firmware-artifacts.json)
Artifact      : Sense360-Ceiling-POE-VentIQ-FanRelay-RoomIQ-v1.0.0-preview.bin
WebFlash      : NOT WebFlash-importable (fan-token guardrail; no config/webflash-builds.json row)

DRY-RUN DRAFT ONLY. This body is NOT attached to any GitHub Release by the
RELEASE-PREVIEW-FAN-TRIAC-BUILD-ROWS-001 PR. No firmware binary, GitHub Release,
tag, manifest.json, or firmware/sources.json is produced. The four H2 sections
below are validated structurally by
`scripts/validate-webflash-release-notes.py --channel preview`. Replace the
Changelog bullets with the human-authored, user-visible changes before this
draft is ever attached to a real preview Release.
-->

# Sense360 Bathroom PoE + Relay fan (VentIQ + FanRelay + RoomIQ) — PREVIEW firmware draft

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
>
> ⚠️ **Fan switching — competent-person install.** The FanRelay path switches a
> mains-connected bathroom fan through the on-board K1 relay. Installation,
> wiring, and load suitability are the installer's responsibility. No
> electrical-safety, creepage / clearance, or installation-approval evidence is
> claimed.

## Changelog

- PREVIEW dry-run draft for the manual-preview `Ceiling-POE-VentIQ-FanRelay-RoomIQ`
  build (Bathroom PoE with the S360-310 Sense360 Relay on/off fan driver). This
  is a PREVIEW, testers-only build: **NOT stable**, **NOT recommended**, and
  **NOT a customer default**.
- Firmware-build proof only: the canonical product YAML
  (`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`) compiled GREEN
  on hosted compile run `26821900127`
  (`Compile Dry-Run: Ceiling-POE-VentIQ-FanRelay-RoomIQ`, result `success`). No
  hardware, bench, compliance, or commercial-availability proof is claimed.
- No GitHub Release, tag, `.bin`, `manifest.json`, or `firmware/sources.json`
  is published by this draft. The build is **not** added to
  `config/webflash-builds.json` (the fan-token guardrail keeps fan drivers off
  the WebFlash build matrix); it is delivered via the manual-preview lane only.

## Known Issues

- NOT hardware verified and NOT compliance certified: this preview build has no
  bench, hardware, EMC, or electrical-safety / compliance proof, and no
  commercial-availability proof. The relay drives a mains-connected fan —
  installation and load suitability are a competent person's responsibility.
- Stable promotion stays blocked by mains-safety / installation-approval /
  creepage / clearance evidence, competent-person sign-off, and GPIO3 strap-pin
  boot characterisation. This build is preview-only and never auto-promotes to
  stable.
- Not a shop product: this configuration is **not buyable as a public shop
  product** and is **not a customer default**; the launch shop product stays the
  stable Bathroom PoE kit (`S360-KIT-BATH-P`).

## Features

- PoE-powered Sense360 Core configuration
- VentIQ bathroom air-quality sensing
- RoomIQ room sensing
- On/off (single-speed) bathroom-fan control via the S360-310 Sense360 Relay (K1)

## Hardware Requirements

- Sense360 Core (`S360-100`)
- Sense360 PoE PSU (`S360-410`)
- Sense360 VentIQ (`S360-211`)
- Sense360 RoomIQ (`S360-200`)
- Sense360 Relay (`S360-310`)
<!-- draft:Ceiling-POE-VentIQ-FanRelay-RoomIQ:end -->

---

<!-- draft:Ceiling-POE-FanPWM:start -->
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
<!-- draft:Ceiling-POE-FanPWM:end -->

---

<!-- draft:Ceiling-POE-FanDAC:start -->
<!--
Sense360 PREVIEW release-notes DRAFT (manual-preview lane).
Canonical id: RELEASE-PREVIEW-FAN-TRIAC-BUILD-ROWS-001.

Config string : Ceiling-POE-FanDAC
Family        : FanDAC (S360-312)
Version       : 1.0.0
Channel       : preview
Delivery lane : manual-preview (config/manual-firmware-artifacts.json)
Artifact      : Sense360-Ceiling-POE-FanDAC-v1.0.0-preview.bin
WebFlash      : NOT WebFlash-importable (fan-token guardrail; no config/webflash-builds.json row)

DRY-RUN DRAFT ONLY. This body is NOT attached to any GitHub Release by the
RELEASE-PREVIEW-FAN-TRIAC-BUILD-ROWS-001 PR. No firmware binary, GitHub Release,
tag, manifest.json, or firmware/sources.json is produced. The four H2 sections
below are validated structurally by
`scripts/validate-webflash-release-notes.py --channel preview`. Replace the
Changelog bullets with the human-authored, user-visible changes before this
draft is ever attached to a real preview Release.
-->

# Sense360 PoE + 0–10V DAC fan (analog fan control) — PREVIEW firmware draft

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

- PREVIEW dry-run draft for the manual-preview `Ceiling-POE-FanDAC` build (PoE
  Core driving the S360-312 Sense360 DAC for 0–10V analog fan control, for
  example a Cloudlift S12 duct fan). This is a PREVIEW, testers-only build:
  **NOT stable**, **NOT recommended**, and **NOT a customer default**.
- Firmware-build proof only: the canonical product YAML
  (`products/sense360-ceiling-poe-fandac.yaml`) compiled GREEN on hosted compile
  run `26821900127` (`Compile Dry-Run: Ceiling-POE-FanDAC`, result `success`).
  No hardware, bench, compliance, or commercial-availability proof is claimed.
- No GitHub Release, tag, `.bin`, `manifest.json`, or `firmware/sources.json`
  is published by this draft. The build is **not** added to
  `config/webflash-builds.json` (the fan-token guardrail keeps fan drivers off
  the WebFlash build matrix); it is delivered via the manual-preview lane only.

## Known Issues

- NOT hardware verified and NOT compliance certified: this preview build has no
  bench, hardware, EMC, or electrical-safety / compliance proof, and no
  commercial-availability proof. The 0–10V analog output is SELV control
  signalling, but no harness or fan-side proof is claimed.
- Not Cloudlift-ready: stable promotion stays blocked by Cloudlift S12 / J3
  harness + product-bench evidence and the S360-312 schematic / BOM. This build
  is preview-only and never auto-promotes to stable.
- Not a shop product: this configuration is **not buyable as a public shop
  product** and is **not a customer default**; the launch shop product stays the
  stable Bathroom PoE kit (`S360-KIT-BATH-P`).

## Features

- PoE-powered Sense360 Core configuration
- 0–10V analog fan control on the S360-312 Sense360 DAC (four neutral analog outputs via GP8403 DACs), e.g. Cloudlift S12 duct fans

## Hardware Requirements

- Sense360 Core (`S360-100`)
- Sense360 PoE PSU (`S360-410`)
- Sense360 DAC (`S360-312`)
<!-- draft:Ceiling-POE-FanDAC:end -->

---

<!-- draft:Ceiling-POE-VentIQ-FanTRIAC-RoomIQ:start -->
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
- NOT hardware verified and NOT compliance certified: publication stays
  blocked by `PACKAGE-TRIAC-001` (signed attestation) and the
  `COMPLIANCE-001-RESOLUTION-001` experimental-lane preconditions
  (`COMPLIANCE-001` closed by market posture — the S360-320 board is never
  placed on the market by Sense360; self-build open-source only). This target never auto-promotes to stable, is **not buyable as a public
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
- Sense360 TRIAC (`S360-320`) — mains phase-cut dimmer; schematic-backed pin mapping (TRI_GPIO1/2 → IO14/IO13), bench attestation pending; self-build board under `COMPLIANCE-001-RESOLUTION-001` (never placed on the market)
<!-- draft:Ceiling-POE-VentIQ-FanTRIAC-RoomIQ:end -->

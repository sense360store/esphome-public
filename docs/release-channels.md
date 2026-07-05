# Release channels — what your device is running and what that means

Sense360 firmware is published on three build channels: **stable**,
**preview**, and **experimental**. The channel is part of every artifact
name (`Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin`) and of every
release tag, so you can always tell what a device is running.

This document **describes** the channel policy for customers. The policy
itself is declared machine-readably in
[`config/release-channel-policy.json`](../config/release-channel-policy.json)
(policy `RELEASE-PREVIEW-ALL-PRODUCTS-001`), and what actually ships is
declared in [`config/webflash-builds.json`](../config/webflash-builds.json)
(ESP-007). Where this description and those files disagree, the config files
win. The standing gates behind the channels live in
[`docs/standing-invariants.md`](standing-invariants.md).

## The channels at a glance

| Channel | Who it is for | Hardware verified? | Recommended? | Support |
|---------|---------------|--------------------|--------------|---------|
| **stable** | Customers | Evidence-gated (or explicit owner waiver) | Yes — the customer default | Supported: file defects via [GitHub Issues](https://github.com/sense360store/esphome-public/issues); see [SUPPORT.md](../SUPPORT.md) |
| **preview** | Testers | **No** | No — never a default | Best effort via Issues / [Discussions](https://github.com/sense360store/esphome-public/discussions); expect to recover with stable/rescue firmware |
| **experimental** | Self-builders of open-source mains boards | **No** | No — never stable, never recommended, never buyable | Published design + firmware information only; you build and operate at your own risk |

## Stable

Stable is the supported customer baseline. It is hardware/evidence-gated
(or, for specific bundles, promoted under an explicit owner risk-acceptance
waiver recorded in the policy), recommended, and the only channel WebFlash
Simple install resolves to. The production stable baseline is
**Release-One**, config string `Ceiling-POE-VentIQ-RoomIQ`.

- Artifact: `…-v{VERSION}-stable.bin`, from a plain `v{VERSION}` release tag.
- What you get: production firmware; defects are actionable bugs — please
  report them.

## Preview

Preview builds are **buildable and installable for testers only**. They are
NOT hardware verified, NOT stable, NOT recommended, and NOT a customer
default. No bench evidence and no compliance is claimed for any preview
artifact. WebFlash exposure, where it exists, is acknowledgement-gated;
fan-driver previews (FanRelay / FanPWM / FanDAC) ship via the manual-preview
lane only.

The **advanced-preview** tier (mains-voltage-risk installs, competent-person
manual installation only) also builds on the preview channel, with stronger
mandatory warning copy.

- Artifact: `…-v{VERSION}-preview.bin`, from a `v{VERSION}-preview`
  prerelease tag.
- What you get: early access for testing. Flash at your own risk and expect
  to recover with the rescue/stable firmware.

## Experimental

The experimental channel exists for firmware targeting **self-build
mains-voltage boards** (e.g. the S360-320 TRIAC) that Sense360 **never
places on the market** — not sold assembled, not as a kit, not as a
populated PCB, never bundled. Design files and firmware are published
open-source under CERN-OHL-P; customers who build these boards do so
entirely from their own sourcing, as self-builders of their own devices, at
their own risk. See
[`docs/decisions/COMPLIANCE-001-RESOLUTION-001.md`](decisions/COMPLIANCE-001-RESOLUTION-001.md).

> **EXPERIMENTAL — SELF-BUILD MAINS HARDWARE.** This firmware targets an
> open-source mains-voltage board design that Sense360 does not sell,
> supply, or place on the market in any form. If you build this board you
> are the manufacturer of your own device and act entirely at your own risk.
> Functional bench completion is NOT a safety, EMC, or compliance
> certification. Mains wiring must only be performed by a competent person.
> Incorrect installation can cause fire, electric shock, or death.

- Artifact: `…-v{VERSION}-experimental.bin`, from a
  `v{VERSION}-experimental` prerelease tag.
- Experimental firmware is never stable, never recommended, never a customer
  default, never in any kit or kit picker.

## How to identify what a device runs

1. **The artifact you flashed.** The channel is the filename suffix:
   `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.4-stable.bin` is stable v1.0.4.
2. **The release tag.** Plain `vX.Y.Z` tags are stable; `vX.Y.Z-preview`
   and `vX.Y.Z-experimental` prerelease tags mark the other channels. All
   releases: <https://github.com/sense360store/esphome-public/releases>.
3. **On the device.** In Home Assistant / the ESPHome API, the device
   exposes a **Product SKU** text sensor identifying its configuration, and
   ESPHome reports the firmware/ESPHome version. If you pinned this repo
   manually, the `ref:` in your device YAML is the authoritative version.
4. **Via WebFlash.** Devices flashed through Simple install run the stable
   Release-One build; anything acknowledgement-gated or manually installed
   is preview or experimental.

If you are unsure, ask in
[Discussions](https://github.com/sense360store/esphome-public/discussions)
with your artifact name or device YAML (credentials removed).

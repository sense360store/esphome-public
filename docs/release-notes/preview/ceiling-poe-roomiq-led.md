<!--
Sense360 WebFlash PREVIEW release-notes DRAFT.
Canonical id: RELEASE-PREVIEW-RELEASE-NOTES-DRYRUN-001.

Config string : Ceiling-POE-RoomIQ-LED
Version       : 1.0.0
Channel       : preview
Artifact      : Sense360-Ceiling-POE-RoomIQ-LED-v1.0.0-preview.bin
Catalog status: preview (release_state: metadata-ready-unpublished)
Consuming kits: S360-KIT-LIVING-P, S360-KIT-CORRIDOR-P (hidden / not buyable)

DRY-RUN DRAFT ONLY. This body is NOT attached to any GitHub Release by the
RELEASE-PREVIEW-RELEASE-NOTES-DRYRUN-001 PR. No firmware binary, GitHub
Release, tag, manifest.json, or firmware/sources.json is produced. The four
H2 sections below are validated structurally by
`scripts/validate-webflash-release-notes.py --channel preview`. Replace the
Changelog bullets with the human-authored, user-visible changes before this
draft is ever attached to a real preview Release. This is the RoomIQ + LED
sibling and is DISTINCT from the already-published VentIQ LED preview
(`Ceiling-POE-VentIQ-RoomIQ-LED`), which is unchanged.
-->

# Sense360 Living-room / Corridor PoE (RoomIQ + LED) — PREVIEW firmware draft

> ⚠️ **PREVIEW FIRMWARE — not for normal customers.** This is a **PREVIEW**
> build. It is **NOT stable**, **NOT recommended**, and **NOT a customer
> default**. It is **NOT hardware verified**, and it is **not buyable as a
> public shop product** — the consuming `S360-KIT-LIVING-P` and
> `S360-KIT-CORRIDOR-P` candidate bundles stay hidden / not buyable. The only
> evidence behind this build is **firmware-build proof only, from hosted
> compile run `26821900127`** (`Preview Compile Dry-Run`, `workflow_dispatch` /
> `compile_mode=full`, 2026-06-02, ESPHome 2026.4.5). **No hardware, bench,
> compliance, or commercial-availability proof is claimed.** The LED ring stays
> a preview feature and never auto-promotes to stable. Normal customers should
> use the **stable Bathroom PoE release** (`S360-KIT-BATH-P` /
> `Ceiling-POE-VentIQ-RoomIQ`, artifact
> `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`) instead.

## Changelog

- PREVIEW dry-run draft for the metadata-ready `Ceiling-POE-RoomIQ-LED` preview
  WebFlash build row (the shared Living-room / Corridor PoE RoomIQ + LED
  firmware). This is the RoomIQ + LED sibling and is DISTINCT from the
  published VentIQ LED preview (`Ceiling-POE-VentIQ-RoomIQ-LED`), which is
  unchanged. This is a PREVIEW, testers-only build: NOT stable, NOT
  recommended, and NOT a customer default.
- Firmware-build proof only: the canonical product YAML compiled GREEN on
  hosted run `26821900127` (`Compile Dry-Run: Ceiling-POE-RoomIQ-LED`, result
  `success`). No hardware, bench, compliance, or commercial-availability proof
  is claimed.
- No GitHub Release, tag, `.bin`, `manifest.json`, or `firmware/sources.json`
  is published by this draft; the `S360-KIT-LIVING-P` / `S360-KIT-CORRIDOR-P`
  candidate bundles stay hidden / not buyable.

## Known Issues

- NOT hardware verified: this preview build has no bench, hardware, EMC, or
  electrical-safety / compliance proof, and no commercial-availability proof.
- LED stays preview: stable promotion stays blocked by S360-410 PoE-PSU
  schematic verification (`PRODUCT-POE-410-001` / `PACKAGE-POE-410-001`) plus
  the LED preview-to-stable gauntlet. This build is preview-only and never
  auto-promotes to stable.
- Not a shop product: the consuming `S360-KIT-LIVING-P` and
  `S360-KIT-CORRIDOR-P` bundles are hidden and not buyable; the launch shop
  product stays the Bathroom PoE kit (`S360-KIT-BATH-P`).

## Features

- PoE-powered Sense360 Core configuration
- RoomIQ room sensing
- Sense360 LED ring (preview)

## Hardware Requirements

- Sense360 Core (`S360-100`)
- Sense360 RoomIQ (`S360-200`)
- Sense360 PoE PSU (`S360-410`)
- Sense360 LED (`S360-300`)

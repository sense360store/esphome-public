# ROOM-BUNDLE-FAN-COMPILE-RESULTS-001 — Hosted compile results for the room-bundle fan configs

## Status

**Firmware-build compile proof only — recorded, GREEN.**

This document records the successful hosted full ESPHome compile validation for
the five full-composition Bathroom / Kitchen fan-control **preview** configs
added by `ROOM-BUNDLE-FAN-CONFIGS-001` (#713). It is **compile-proof
documentation and metadata only**.

It does **not**:

- publish firmware, create a release or tag, or commit a `.bin`;
- change the WebFlash repository or `config/webflash-builds.json`;
- mark anything stable, recommended, default, or buyable;
- claim any hardware, bench, safety, compliance, or commercial-availability
  proof;
- complete `FANDAC-I2C-ADDR-001` (FanDAC I²C address bench verification stays
  **pending**);
- change the TRIAC status (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays
  **build-blocked** under HW-005);
- change the stable Bathroom PoE build (`Ceiling-POE-VentIQ-RoomIQ`).

A green compile means the YAML composes / substitutes / includes / generates
code cleanly under the current ESPHome version. **It is not hardware,
bench, safety, or compliance evidence.**

## Configs validated

`ROOM-BUNDLE-FAN-CONFIGS-001` (#713) added five full-composition preview
fan-bundle configs. All five compiled successfully in the hosted run:

| Config string | Variant SKU | Fan driver | Notes |
|---|---|---|---|
| `Ceiling-POE-VentIQ-FanPWM-RoomIQ` | `S360-KIT-BATH-P-PWM` | S360-311 (PWM) | Native ESP32-S3 ledc PWM; no RPM claimed. |
| `Ceiling-POE-VentIQ-FanDAC-RoomIQ` | `S360-KIT-BATH-P-DAC` | S360-312 (DAC) | Compiled with FanDAC IC2 `0x5A` override. |
| `Ceiling-POE-AirIQ-FanRelay-RoomIQ` | `S360-KIT-KITCHEN-P-REL` | S360-310 (Relay) | Relay proxied from the Core main_relay. |
| `Ceiling-POE-AirIQ-FanDAC-RoomIQ` | `S360-KIT-KITCHEN-P-DAC` | S360-312 (DAC) | Compiled with FanDAC IC2 `0x5A` override; WebFlash-grammar-excluded (`fandac_conflicts_with_airiq`). |
| `Ceiling-POE-AirIQ-FanPWM-RoomIQ` | `S360-KIT-KITCHEN-P-PWM` | S360-311 (PWM) | Native ESP32-S3 ledc PWM; policy-gated; no RPM claimed. |

Related supporting work:

- `COMPILE-VALIDATOR-PROGRESS-LOGGING-001` (#714) added per-target compile
  logging and a per-target timeout.
- `FANDAC-I2C-ADDR-001` (#715) added the FanDAC I²C address verification
  checklist ([`docs/hardware/fandac-i2c-address-verification.md`](hardware/fandac-i2c-address-verification.md)).

## Hosted compile run

| Field | Value |
|---|---|
| Workflow name | **Compile-only Firmware Validation** |
| Workflow file | `.github/workflows/compile-only.yml` |
| Run id | **`26913592989`** |
| Run URL | <https://github.com/sense360store/esphome-public/actions/runs/26913592989> |
| Branch / ref | `main` |
| Event | `workflow_dispatch` |
| Compile mode | `full` |
| Date | 2026-06-04 |
| ESPHome version | `2026.4.5` |
| Metadata Validation | **success** |
| Full ESPHome Compile | **success** |
| Overall result | **success** |
| Artifacts | none expected, none produced |
| Proof scope | `firmware-build-only` |

## Where the result is recorded

- [`config/compile-only-targets.json`](../config/compile-only-targets.json) —
  each of the five targets now carries `compile_validation_status:
  validated-full-compile` plus a `compile_evidence` block citing run
  `26913592989`.
- [`config/room-bundle-fan-variants.json`](../config/room-bundle-fan-variants.json)
  — the five variants move from `buildable-preview-compile-pending` to
  `buildable-preview-compile-validated`; each variant's
  `firmware_config_evidence.compile_validation_status` is now
  `validated-full-compile` with a `compile_evidence` block, and the
  document-level `compile_results` object records the run.

## FanDAC IC2 address note (`FANDAC-I2C-ADDR-001` stays pending)

The two FanDAC room-bundle configs — `Ceiling-POE-VentIQ-FanDAC-RoomIQ`
(Bathroom DAC) and `Ceiling-POE-AirIQ-FanDAC-RoomIQ` (Kitchen DAC) — compiled
**with the FanDAC IC2 address override** `fan_dac_2_i2c_address: "0x5A"`. This
relocates the second GP8403 (IC2) off its `0x59` package default so it does not
collide with the air-quality SGP41 at `0x59` on the shared `core_i2c` bus.

This is a **compile-time configuration only**:

- The physical IC2 DIP-switch (SW2) → I²C address mapping is **NOT bench
  verified**. The DIP-position → address truth table remains owed by
  `FANDAC-I2C-ADDR-001`, which stays **pending**.
- GP8403 `0x59` **must not** be used with VentIQ/AirIQ (it collides with the
  SGP41 @ `0x59`).

A successful compile does not prove the installer's switch setting; it only
proves the firmware composes with the `0x5A` override applied.

## What is still gated

These five configs remain **advanced / manual, compile-validated previews**:
not published, no `.bin`, not WebFlash-exposed, not a preview release target,
not stable, not recommended, not a customer default, not buyable. Stable / full
release of every fan-control variant still requires hardware, bench evidence,
and compliance sign-off (and, for FanDAC, `FANDAC-I2C-ADDR-001`). See
[`docs/sense360-room-bundles.md`](sense360-room-bundles.md),
[`docs/pre-hardware-room-bundle-release-handoff.md`](pre-hardware-room-bundle-release-handoff.md),
and [`docs/first-release-gates.md`](first-release-gates.md).

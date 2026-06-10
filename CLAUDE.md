# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository. Every fact here is derived from the tree; where this
file and a source-of-truth file disagree, the source-of-truth file wins and
this file is the one to fix.

## Project overview

This repository is the ESPHome firmware **source** for Sense360 environmental
monitoring devices (ESP32-S3 ceiling hubs plus sensor / driver / PSU modules).
It holds the product YAML compositions, builds and publishes the **unsigned**
release `.bin` artifacts via GitHub Actions, and is the manual / custom
firmware path for advanced users. It sits **upstream** of
[`sense360store/WebFlash`](https://github.com/sense360store/WebFlash) — the
production signing / manifest / flash authority — and the cross-repo contract
is exactly three stable surfaces: release **tags**, WebFlash **config-string**
values (e.g. `Ceiling-POE-VentIQ-RoomIQ`), and **artifact names**
(`Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin`). This repo does **not**
sign firmware. The production stable customer baseline is Release-One, config
string `Ceiling-POE-VentIQ-RoomIQ`. The single canonical status / roadmap /
blocker document is
[`docs/sense360-roadmap-status.md`](docs/sense360-roadmap-status.md); the
detailed PR working queue is [`UPCOMING_PR.md`](UPCOMING_PR.md).

## Sense360 hardware reference (canonical SKUs)

The naming source of truth is
[`docs/hardware-catalog.md`](docs/hardware-catalog.md) with the
machine-readable mirror at
[`config/hardware-catalog.json`](config/hardware-catalog.json) (which also
carries `schematic_status` per entry). **Friendly names are canonical**; old
names exist only for legacy reference and must not be used in new YAML, docs,
or artifacts. Use `Ceiling`, never `Celling` (legacy typo).

| Group   | Type      | Friendly name      | SKU      | Rev | Old name                        | What it does |
|---------|-----------|--------------------|----------|-----|---------------------------------|--------------|
| Ceiling | Hub       | Sense360 Core      | S360-100 | R4  | 360Core_Ceiling_V3_R            | Main board. Has the ESP32-S3 and connectors for all other modules. |
| Ceiling | Sensor    | Sense360 RoomIQ    | S360-200 | R4  | Presence + Comfort (two boards) | Merged board. PIR, LD2450, SEN0609, LTR-303ALS light, SHT4x temp/humidity, BMP581 pressure. |
| Ceiling | Sensor    | Sense360 AirIQ     | S360-210 | R4  | AirIQ Ceiling                   | Air quality board. CO2 SCD41, VOC SGP41, gas MICS-4514 with STM8. Connectors for SPS30 PM and SFA40 HCHO. |
| Ceiling | Sensor    | Sense360 VentIQ    | S360-211 | R4  | Bathroom Pro                    | Smaller bathroom air-quality board. SGP41 on board. Connectors for IR temp and SPS30. |
| Ceiling | Indicator | Sense360 LED       | S360-300 | R4  | LED Ring                        | Ring of WS2812B LEDs. |
| Inline  | Driver    | Sense360 Relay     | S360-310 | R4  | S360-Relay-C                    | On/off relay for bathroom fans. |
| Inline  | Driver    | Sense360 PWM       | S360-311 | R4  | 12vFan_PWM_PulseCounter         | 12V PWM fan driver, up to 4 fans with tach feedback. |
| Inline  | Driver    | Sense360 DAC       | S360-312 | R4  | Fan_GP8403                      | 0 to 10V analog fan driver, for example Cloudlift S12. |
| Inline  | Driver    | Sense360 TRIAC     | S360-320 | R4  | TRIAC_Board                     | Phase dimmer for mains fan or lamp. |
| Power   | PSU       | Sense360 240v PSU  | S360-400 | R4  | PWR Module                      | Mains to 5V using HLK-5M05. |
| Power   | PSU       | Sense360 PoE PSU   | S360-410 | R4  | PoE Module                      | PoE to 5V. |

## Repo layout

The YAML is a **board / bundle / alias / shim** layered composition (see
[`docs/system-architecture.md`](docs/system-architecture.md) and
[`docs/arch-board-bundle-plan.md`](docs/arch-board-bundle-plan.md)); the
declaration layer that governs what ships lives in `config/`.

- **`products/sense360-*.yaml`** — customer include paths. Thin compat
  **shims** that do nothing but `!include` the matching bundle. Customers pin
  these exact paths at a release tag (`ref: v1.0.0`), so they are never
  deleted or renamed.
- **`products/bundles/`** — one YAML per WebFlash config string; the
  **canonical composition** (board packages + base infrastructure + feature
  profiles) for that config.
- **`products/webflash/`** — release-gate **wrappers**. Thin re-exports of the
  canonical product YAML so [`config/webflash-builds.json`](config/webflash-builds.json)
  can address builds via the `products/webflash/` namespace the release
  workflow consumes.
- **`products/compile-only/`** — compile-only validation **skeletons** for the
  pre-hardware buildability lane (listed in
  [`config/compile-only-targets.json`](config/compile-only-targets.json)).
  Deliberately outside top-level catalog scanning; never WebFlash-exposed,
  never a release artifact, never hardware proof.
- **`packages/`** — composition layers: `packages/boards/` (SKU-aligned
  **authoritative** board packages, e.g. `s360-211-ventiq.yaml`),
  `packages/base/` (WiFi, encrypted API, OTA, logging, time, external
  components), `packages/hardware/` and `packages/expansions/` (legacy
  functional paths retained as thin `!include` **aliases** of the board
  packages, plus drivers not yet flipped into the board layer),
  `packages/features/` (behaviour profiles / automations). The S360-100 Core
  mount paths are the inverse today: the board overlay still wraps the legacy
  `packages/hardware/sense360_core_*.yaml` source until Core's
  source-of-truth flip lands.
- **`config/`** — the **catalog source of truth** (machine-readable
  declarations; JSON, validated by `scripts/` + `tests/`):
  [`product-catalog.json`](config/product-catalog.json) (product lifecycle /
  status / blockers), [`webflash-builds.json`](config/webflash-builds.json)
  (the release/build matrix — what release publishing ships, per ESP-007),
  [`hardware-catalog.json`](config/hardware-catalog.json),
  [`webflash-compatibility.json`](config/webflash-compatibility.json)
  (contract snapshot), [`preview-release-targets.json`](config/preview-release-targets.json),
  [`release-channel-policy.json`](config/release-channel-policy.json),
  [`room-bundle-skus.json`](config/room-bundle-skus.json),
  [`room-bundle-fan-variants.json`](config/room-bundle-fan-variants.json),
  [`compile-only-targets.json`](config/compile-only-targets.json), and
  companions. Docs describe; `config/` decides.
- **`components/`** — external ESPHome C++ components (`ld2412`, `ld2450`,
  `ld24xx`). **`include/sense360/`** — extracted C++ logic headers
  (`led_logic.h`, `calibration.h`, `thresholds.h`, `time_utils.h`) unit-tested
  natively from `tests/unit/`.
- **`scripts/`** — release / validation / planning tooling (each with a
  `tests/test_*.py` counterpart). **`tests/`** — Python test suite +
  validators + C++ test Makefile. **`docs/`** — reference docs; canonical
  roadmap at [`docs/sense360-roadmap-status.md`](docs/sense360-roadmap-status.md);
  hardware evidence under `docs/hardware/`. **`examples/`** — customer
  configuration templates.

## ESPHome conventions used here

- **Full configs, not snippets.** Every `products/` entry resolves (shim →
  bundle → packages) to a complete, standalone ESPHome config: bundles include
  the base packages (`wifi`, `api_encrypted`, `ota`, `logging`, `time`,
  `external_components`) plus board and feature packages, so
  `esphome config products/<file>.yaml` validates each product directly.
  Customers override only `device_name` / `friendly_name` substitutions.
- **List syntax for component blocks.** `script:`, `sensor:`, `switch:`,
  `binary_sensor:` (and other multi-entry component blocks) are written in
  ESPHome list form (`- id: …` / `- platform: …`), because ESPHome merges
  packages by concatenating lists — map-form blocks would collide across
  packages.
- **Composition via `packages:` + `!include`.** Products never duplicate
  package wiring; they include it. Legacy `packages/hardware/*` and
  `packages/expansions/*` paths must keep resolving (alias files), since
  customers pin them.
- **Secrets only via `!secret`.** Copy
  [`secrets.example.yaml`](secrets.example.yaml) to `secrets.yaml` (gitignored
  — never commit it; `scripts/check-no-tracked-secrets.py` and the fallback-AP
  password guard enforce this). CI generates placeholder secrets for builds.
- **YAML style** (`.yamllint`): 2-space indent, indented sequences, max line
  length 120 (warning), no `---` document start. ESPHome custom tags
  (`!secret`, `!include`, `!lambda`, `!extend`, `!remove`) are why pre-commit's
  `check-yaml` runs with `--unsafe` (syntax-only parse) — do not remove that
  flag, and do not mirror unsafe loading into real config-loading code (use
  `yaml.safe_load` with registered tag constructors, as
  `tests/validate_configs.py` does).
- **Python tests are stdlib `unittest` modules** (no pytest-specific APIs),
  runnable individually (`python3 tests/test_x.py`) and as a suite under
  plain pytest. Do not add module-level `test_*` functions that invoke
  `unittest.main()` — pytest collects them and they raise `SystemExit`.

## Commands

```bash
# Python test suite — full suite must stay green under plain pytest
python3 -m pytest tests/
python3 -m pytest tests/test_room_bundle_fan_variants.py     # one file
python3 tests/test_product_catalog.py                        # files also run directly
python3 -m unittest tests.test_room_bundle_fan_variants -v   # or via unittest

# YAML lint (uses .yamllint at the repo root)
yamllint .

# Repo validators (the per-PR CI gate, validate.yml, runs these and more)
python3 tests/validate_configs.py                        # YAML syntax/structure of products+packages
python3 tests/validate_webflash_builds.py                # build matrix vs contract snapshot
python3 scripts/validate_product_catalog_consistency.py  # catalog cross-file consistency
python3 scripts/generate_firmware_matrix.py --check      # generated-matrix freshness
python3 scripts/report_firmware_build_gaps.py --check    # generated-gap-report freshness

# ESPHome config validation (needs esphome installed; pin: requirements-dev.txt)
esphome config products/sense360-ceiling-poe-ventiq-roomiq.yaml

# Compile lanes (hosted CI; the full-compile passes are workflow_dispatch only)
python3 scripts/validate_compile_targets.py --metadata-only   # compile-only lane, no ESPHome
python3 scripts/validate_compile_targets.py --compile         # full `esphome compile` pass
#   CI lanes: validate.yml ("CI: Quick Validation" — the per-push/PR gate)
#   · compile-only.yml ("CI: Compile-Only") and preview-compile-dryrun.yml
#     ("CI: Preview Compile Dry-Run") — manual dispatch, metadata or full compile
#   · ci-validate-configs.yml ("CI: Validate Configs") — manual broad legacy sweep
#   · firmware-build-release.yml ("Release 3: Build & Release") — builds and
#     publishes the release .bin set on release publish, driven by
#     config/webflash-builds.json (ESP-007)

# C++ unit tests for the extracted logic headers
cd tests && make test

# Pre-commit hooks (yamllint, black, flake8, clang-format, secret guards)
pre-commit run --all-files
```

## Standing gates (do not regress)

[`UPCOMING_PR.md`](UPCOMING_PR.md) → *Standing invariants (do not regress)* is
the live source for these; the quotes below are verbatim as of this commit.
If they drift, `UPCOMING_PR.md` wins.

> * **Production stable Release-One is the customer baseline.** Config string
>   `Ceiling-POE-VentIQ-RoomIQ` (current stable version per
>   [`config/webflash-builds.json`](config/webflash-builds.json); v1.0.4 as of
>   2026-06-07), launch shop SKU **`S360-KIT-BATH-P`**. Simple install resolves
>   to the stable Bathroom PoE build only. The Bedroom (`Ceiling-POE-RoomIQ`,
>   stable v1.0.5, 2026-06-08) and Kitchen (`Ceiling-POE-AirIQ-RoomIQ`, stable
>   v1.0.6, 2026-06-09) bundles were later promoted to stable under owner
>   risk-acceptance waivers (`HW-S360-410-WAIVER-2026-06`,
>   `HW-AIRIQ-WAIVER-2026-06`) — owner waivers, not hardware verification — and
>   their candidate / room bundles stay **hidden / not buyable / never the
>   customer default**.
> * **FanTRIAC is commissioned to the experimental self-build mains lane —
>   never stable / recommended / default / buyable / kit-exposed.**
>   `TRIAC-COMMISSIONING-001` (human-review only) cleared the `PACKAGE-TRIAC-001`
>   half of the former blocker (operator-attested bench proof
>   `docs/package-triac-001-operator-bench-proof.md`), with `COMPLIANCE-001`
>   closed by market posture (`COMPLIANCE-001-RESOLUTION-001`), and moved
>   `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` into the `experimental_lane`. It is now
>   `status: preview` / `channel: experimental` / `webflash_build_matrix: true`
>   with a `config/webflash-builds.json` row on the new **experimental** build
>   channel (artifact `Sense360-Ceiling-POE-VentIQ-FanTRIAC-RoomIQ-v1.0.0-experimental.bin`;
>   `experimental` is also in `config/webflash-compatibility.json`
>   `allowed_channels` and emitted by `scripts/derive_release_version_channel.py`).
>   The permanent teeth stand: **never stable, never recommended, never a
>   customer default, never buyable, never in any kit or kit picker, never in
>   `release_one_required_configs`** — the S360-320 is a self-build, open-source
>   (CERN-OHL-P) board Sense360 **never places on the market**, and the
>   commissioning makes **no electrical-safety / EMC / compliance claim** and
>   cuts **no release tag**. `TRIAC-PUBLISH-ADVANCED-PREVIEW-001` is **executed**;
>   downstream one-click WebFlash import (`WF-IMPORT-TRIAC-001`) stays gated,
>   unblocked only once the experimental release is cut. The standalone
>   manual-preview fan drivers (FanRelay / FanPWM / FanDAC) stay off
>   `config/webflash-builds.json` (the fan-token guardrail holds for them). Any
>   further FanTRIAC blocker / status change is **human-review only — do NOT
>   auto-merge**.
> * **Fans are preview-only.** FanRelay / FanPWM / FanDAC (and the five
>   full-composition fan room-bundle configs) are `manual-preview`, published only
>   on the shared `v1.0.0-preview` prerelease, and are preview WebFlash-import
>   eligible (Advanced-install-only, acknowledgement-gated). **No fan row is added
>   to `config/webflash-builds.json`** — the fan-token guardrail stays intact.
>   Stable / full release stays blocked (`RELEASE-RELAY-001` / `RELEASE-PWM-001` /
>   `RELEASE-DAC-001`); catalog `status` stays `hardware-pending`.
> * **FanDAC I²C address requirement is pending bench.** GP8403 IC1 `0x58` /
>   IC2 `0x5A`; `0x59` is forbidden when VentIQ/AirIQ is present (SGP41 collision).
>   The DIP-switch mapping is compile-time only — `FANDAC-I2C-ADDR-001` stays
>   **PENDING** (no FanDAC hardware verification claimed). See
>   [`docs/hardware/fandac-i2c-address-verification.md`](docs/hardware/fandac-i2c-address-verification.md).
> * **No false proof.** Preview / compile work is **firmware-build proof only** —
>   no hardware / bench / compliance / safety / commercial-availability proof is
>   claimed for any preview artifact.

Three further standing rules travel with the invariants:

- **TRIAC changes are human-review only.** Verbatim from the
  `PACKAGE-TRIAC-001` queue item in [`UPCOMING_PR.md`](UPCOMING_PR.md):
  "**Do NOT auto-merge** any FanTRIAC pin / blocker / status change —
  human-review only."
- **Attestations are never machine-written.** Operator attestation /
  bench-evidence blocks are completed by the human operator only; agents may
  scaffold an intentionally empty block but must never fill in attestation
  content, dates, signatures, or evidence claims. Verbatim from
  [`docs/package-triac-001-operator-bench-proof.md`](docs/package-triac-001-operator-bench-proof.md):
  "To be completed by the operator himself before merge. The entry cells are
  intentionally empty in the close-out PR — no attestation content was
  machine-written."
- **The release matrix is declaration-driven (ESP-007).** Verbatim from
  [`.github/workflows/firmware-build-release.yml`](.github/workflows/firmware-build-release.yml):
  "ESP-007: the release/build matrix is driven by
  config/webflash-builds.json, filtered by the version + channel derived from
  the release tag. This replaces the previous broad `find products/` scan,
  which built every legacy / reference / blocked product (including FanTRIAC)
  when a real Release was published. The WebFlash build matrix is the single
  source of truth for what release publishing ships." Never reintroduce a
  broad scan of `products/`; releases ship only what
  `config/webflash-builds.json` declares.

## UPCOMING_PR.md maintenance rule

[`UPCOMING_PR.md`](UPCOMING_PR.md) is the source-of-truth queue for the next
planned change set: the *Next queue (actionable)* section is the only
genuinely open work, and everything below it is standing invariants plus the
condensed record of merged PRs. **Every PR that changes queue state —
completing, blocking, deferring, or queueing work — must update
`UPCOMING_PR.md` in the same PR** (completed work moves to the one-line
history, newest first). High-level status belongs in
[`docs/sense360-roadmap-status.md`](docs/sense360-roadmap-status.md), which
links here rather than duplicating queue detail.

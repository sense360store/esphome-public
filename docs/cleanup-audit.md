# Cleanup Audit (CLEANUP-001)

This document classifies stale or misleading repo content against the current
Release-One / WebFlash source of truth. It is an **audit and classification
document only**. No files are deleted, renamed, or otherwise changed by the PR
that introduces it. Concrete cleanup work is deferred to follow-up PRs listed
at the end.

## Current source of truth

The Release-One shipping configuration is pinned by the following artifacts
and is the basis for every classification in this document:

| Field | Value |
|---|---|
| WebFlash config string | `Ceiling-POE-VentIQ-RoomIQ` |
| Product YAML | [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml) |
| WebFlash wrapper | [`products/webflash/ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml) |
| Firmware artifact | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` |
| GitHub Release tag | `v1.0.0` |
| Release proof run | <https://github.com/sense360store/esphome-public/actions/runs/25763009641> |
| WebFlash compatibility | [`config/webflash-compatibility.json`](../config/webflash-compatibility.json) |
| WebFlash build matrix | [`config/webflash-builds.json`](../config/webflash-builds.json) |
| WebFlash contract | [`docs/webflash-contract.md`](webflash-contract.md) |
| Release-One overview | [`docs/release-one.md`](release-one.md) |
| Hardware audit | [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md) |
| Release proof record | [`docs/webflash-release-proof.md`](webflash-release-proof.md) |

Workflow roles:

- `.github/workflows/firmware-build-release.yml` — Release-One build/release
  gate. Builds only the WebFlash matrix (excludes `products/webflash/*`
  wrappers from matrix discovery; the matrix runs the canonical product
  YAMLs).
- `.github/workflows/ci-validate-configs.yml` — broad legacy / manual sweep.
  Validates every YAML in `products/` (including legacy
  `sense360-core-*`, `sense360-mini-*`, `sense360-poe.yaml`,
  `sense360-fan-pwm.yaml`) and the generated module-combination configs from
  `tests/generate_test_configs.py`. **Not** the Release-One PR gate.
- `.github/workflows/validate.yml` — ~30s YAML-syntax pre-flight, runs on
  every push/PR.

Exclusions retained pending hardware verification:

- **Sense360 TRIAC / FanTRIAC** is excluded from production Release-One
  pending HW-005 (S360-320 schematic uncommitted, GPIO5 / GPIO6 collide
  with RoomIQ J10 nets, ESPHome `ac_dimmer` requires direct
  interrupt-capable ESP32 GPIOs that the SX1509 expander cannot provide).
  The FanTRIAC product YAML, the FanTRIAC WebFlash wrapper, and
  `packages/expansions/fan_triac.yaml` are retained in the repo as
  blocked / reference files.
- **Sense360 LED** is excluded because the WebFlash config string
  `Ceiling-POE-VentIQ-RoomIQ` does not contain the `LED` token. The LED
  packages remain in the repo for non-Release-One products and for a future
  LED-bearing config string (e.g. `Ceiling-POE-VentIQ-RoomIQ-LED`).

## Audit method

Statuses applied below use the definitions from the task:

| Status | Definition |
|---|---|
| `current` | Matches current Release-One / WebFlash truth. |
| `legacy-compatible` | Old, but may be public API or manual-user path; keep. |
| `blocked-reference` | Intentionally retained, not production-ready (e.g. FanTRIAC). |
| `stale` | Wording or docs contradict current truth; doc-only fix needed. |
| `candidate-for-removal` | Likely removable, needs a separate PR. |
| `dead` | Proven unused, safe to delete later. |
| `unknown` | Cannot prove either way; treat conservatively. |

Search terms run from the repo root (representative):

```text
grep -RIn "FanTRIAC"
grep -RIn "TRIAC"
grep -RIn "LED Ring"
grep -RIn "Sense360 LED"
grep -RIn "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"
grep -RIn "Ceiling-POE-VentIQ-RoomIQ"
grep -RIn "release-one"
grep -RIn "webflash"
grep -RIn "Bathroom Pro"
grep -RIn "AirIQ"
grep -RIn "Celling"
grep -RIn "ci-validate-configs"
grep -RIn "31+ products"
grep -RIn "all products"
grep -RIn "v3\\.0\\.0|v2\\.2\\.0|v2\\.0\\.0"
grep -Rl "github://sense360store/esphome-public"
find . -name "*.bak" -o -name "*.orig" -o -name "*~" -o -name "*.tmp"
```

Inspected paths: `README.md`, `CHANGELOG.md`, `docs/**`, `examples/**`,
`products/**`, `products/webflash/**`, `packages/**`, `config/**`,
`.github/workflows/**`, `tests/**`, `scripts/**`, `components/**`,
`include/**`, and the top-level `base/`, `features/`, `hardware/` symlinks
(which resolve into `packages/base/`, `packages/features/`,
`packages/hardware/`).

## Findings summary

| Path | Status | Finding | Recommended action |
|---|---|---|---|
| `products/sense360-ceiling-poe-ventiq-roomiq.yaml` | `current` | Canonical Release-One YAML; builds `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`. | Keep. |
| `products/webflash/ceiling-poe-ventiq-roomiq.yaml` | `current` | Thin WebFlash wrapper for Release-One. | Keep. |
| `config/webflash-builds.json` | `current` | WebFlash build matrix. Carries the Release-One stable build `Ceiling-POE-VentIQ-RoomIQ` (channel=`stable`, version=`1.0.0`, artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`) and, after PRODUCT-009, the LED-bearing preview sibling `Ceiling-POE-VentIQ-RoomIQ-LED` (channel=`preview`, version=`1.0.0`, artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`, `product_yaml: products/webflash/ceiling-poe-ventiq-roomiq-led.yaml`, `chip_family: ESP32-S3`, hardware-requirements and features lists carry the Sense360 LED entries). FanTRIAC stays out of the build matrix under HW-005. | Keep. |
| `config/webflash-compatibility.json` | `current` | Canonical module / forbidden-token list; `release_one_required_configs: ["Ceiling-POE-VentIQ-RoomIQ"]`. | Keep. |
| `config/hardware-catalog.json` | `current` | Canonical SKU → friendly-name table; carries `old_name` entries for `LED Ring` (S360-300) and `Bathroom Pro` (S360-211), which is correct. | Keep. |
| `config/product-catalog.json` | `current` | Product source-of-truth catalog (PRODUCT-001). Records lifecycle status for each Sense360 product configuration; Release-One `Ceiling-POE-VentIQ-RoomIQ` is `production` on `stable`, FanTRIAC `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` is `blocked` (HW-005), and after PRODUCT-009 the LED-bearing sibling `Ceiling-POE-VentIQ-RoomIQ-LED` is `preview` with `webflash_build_matrix: true`, `version: 1.0.0`, `channel: preview`, `artifact_name: Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`, `blocked_modules: ["FanTRIAC"]` (LED omitted because this entry carries the `LED` token), `hardware` SKU map (Core / VentIQ / RoomIQ / PoE / LED), and `modules` map. Lifecycle layer on top of `config/webflash-builds.json`. | Keep. |
| `tests/test_product_catalog.py` | `current` | Validates `config/product-catalog.json`: schema, required fields per status, path existence, config-string uniqueness, artifact-name pattern, and one-way cross-check against `config/webflash-builds.json` (blocked entries must not appear in the build matrix; build entries must appear in the catalog with a WebFlash-eligible status). | Keep. |
| `scripts/validate_product_catalog_consistency.py` | `current` | PRODUCT-003 read-only catalog consistency validator. Cross-checks `config/product-catalog.json` against `config/webflash-builds.json`, `config/webflash-compatibility.json`, `config/hardware-catalog.json`, `scripts/product_name_mapper.py`, product YAML paths, and WebFlash wrapper paths. Provides `--checklist` and `--product` modes for the add-product workflow. Read-only; no mutation, no scaffold generation. | Keep. |
| `tests/test_product_catalog_consistency.py` | `current` | Stdlib `unittest` suite covering `scripts/validate_product_catalog_consistency.py`: current-repo-state pass, Release-One production checks, FanTRIAC blocked checks, legacy-compatible non-shippability sweep, mapper agreement, wrapper basename agreement, and checklist mode. | Keep. |
| `.github/workflows/firmware-build-release.yml` | `current` | Release-One build/release gate; excludes `products/webflash/*` from matrix discovery; runs `tests/check_webflash_build_output.py`. RELEASE-004 delegates the version/channel derivation in the `Determine version and channel` step to `scripts/derive_release_version_channel.py` so preview release tags can carry a suffix (`v1.0.0-led-preview` or `v1.0.0-preview`) while still resolving to the semver in `config/webflash-builds.json`; stable releases must use plain semantic tags (`vX.Y.Z`) and any suffixed stable tag or unrecognized prerelease suffix is rejected with a clear error. | Keep. |
| `scripts/derive_release_version_channel.py` | `current` | RELEASE-004 tag-normalization helper. Maps a GitHub release tag plus the release's `prerelease` flag to the `(version, channel)` pair the build matrix filters on. Allowed prerelease suffixes: `-led-preview`, `-preview`. Stable releases must use plain semantic tags (`vX.Y.Z`); any suffix on a non-prerelease tag is rejected. Unknown prerelease suffixes are rejected with an explicit error so operator typos fail fast at the derive step instead of later in the matrix filter. Env-driven CLI (`GITHUB_REF_NAME`, `PRERELEASE`); writes `version=` / `channel=` lines to stdout and, when set, to `$GITHUB_OUTPUT`. Does **not** build firmware, tag releases, change the LED preview version, mark LED stable, commit `.bin` files, or unblock FanTRIAC. | Keep. |
| `tests/test_derive_release_version_channel.py` | `current` | RELEASE-004 stdlib `unittest` suite for `scripts/derive_release_version_channel.py`. Covers stable plain tag, stable tag without `v` prefix, preview `-led-preview` suffix, preview `-preview` suffix, prerelease plain tag, stable suffixed tag rejection, prerelease unknown / typo suffix rejection, nested-dash rejection, empty tag rejection, and a CLI smoke section that runs the script via `subprocess` to confirm exit codes, stdout, and `$GITHUB_OUTPUT` writes. | Keep. |
| `.github/workflows/validate.yml` | `current` | Quick YAML syntax pre-flight; also runs the WebFlash builds / catalog / release-notes generator / RELEASE-002 release-notes-draft-workflow smoke tests. | Keep. |
| `.github/workflows/release-notes-draft.yml` | `current` | RELEASE-002 manual release-notes draft workflow (`workflow_dispatch` only). Inputs: `config_string`, `version`, `channel` (`stable`/`preview`), optional `changelog`. Runs `scripts/generate_webflash_release_notes.py`, then `scripts/validate-webflash-release-notes.py`, then uploads `release-notes.md` as a workflow artifact. Does not create a GitHub Release, does not publish firmware, does not commit the draft, does not infer changelog content from git history, does not pass `--require-changelog`, and does not modify the release-publish gates in `firmware-build-release.yml`. | Keep. |
| `scripts/product_name_mapper.py` | `current` | Maps product YAML basenames → WebFlash artifact names; explicit comment retains FanTRIAC mapping as legacy reference. | Keep. |
| `scripts/check-webflash-release-assets.py` | `current` | Asset-existence gate. | Keep. |
| `scripts/validate-webflash-release-notes.py` | `current` | Release-body format gate. | Keep. |
| `scripts/generate_webflash_release_notes.py` | `current` | RELEASE-001 read-only release-notes draft generator. Produces a Markdown draft body matching the format enforced by `scripts/validate-webflash-release-notes.py`, sourcing lifecycle / SKU data from `config/product-catalog.json`, feature bullets from `config/webflash-builds.json`, and friendly hardware names from `config/hardware-catalog.json`. Refuses blocked / legacy-compatible / deprecated / removed entries; refuses preview entries on the stable channel; emits FanTRIAC and Sense360 LED as Known-Issues exclusions when listed in the catalog entry's `blocked_modules`. For the Release-One catalog entry both FanTRIAC and LED stay in `blocked_modules` so the Release-One body lists them as Known Issues; for the LED preview catalog entry only FanTRIAC is in `blocked_modules`, so the LED preview body places Sense360 LED in `## Features` and `## Hardware Requirements` while keeping FanTRIAC in `## Known Issues` with the HW-005 reference. PRODUCT-009 softened the FanTRIAC Known-Issues wording from "this Release-One firmware" to "this firmware" so the bullet is accurate for both Release-One and the LED preview. Read-only: does not create releases, publish firmware, infer changelog content from git history, or call any external service. | Keep. |
| `tests/test_generate_webflash_release_notes.py` | `current` | Stdlib `unittest` suite covering `scripts/generate_webflash_release_notes.py`: Release-One generation, validator pass, config-string / artifact / SKU presence, FanTRIAC / LED as exclusions, blocked / legacy-compatible / unknown-config refusal, stable-channel requires production status, custom changelog text and file, `--output` file write, `--validate` shell-out to the existing release-notes validator. | Keep. |
| `tests/test_release_notes_draft_workflow.py` | `current` | RELEASE-002 stdlib `unittest` smoke test for `.github/workflows/release-notes-draft.yml`. Asserts the workflow file exists, declares `workflow_dispatch:` and no other triggers, references the generator and validator scripts, uploads an artifact, and does not pass `--require-changelog`. Intentionally a substring smoke check rather than a YAML schema parse. | Keep. |
| `tests/validate_webflash_builds.py` | `current` | Validates `config/webflash-builds.json` against `config/webflash-compatibility.json`. | Keep. |
| `tests/test_webflash_compatibility.py` | `current` | Asserts canonical-module / Release-One required-config invariants. | Keep. |
| `tests/test_webflash_artifact_naming.py` | `current` | Pins Release-One artifact filename. | Keep. |
| `tests/test_validate_webflash_builds.py` | `current` | Unit tests for build-matrix validator. | Keep. |
| `tests/test_validate_webflash_release_notes.py` | `current` | Unit tests for release-notes validator. | Keep. |
| `tests/test_release_one_entity_names.py` | `current` | Pins Release-One entity names against legacy drift. | Keep. |
| `tests/test_product_substitutions.py` | `current` | Substitutions invariants for Release-One. | Keep. |
| `tests/check_webflash_build_output.py` | `current` | Build-time artifact-name assertion. | Keep. |
| `tests/validate_configs.py` | `current` | Repo-wide YAML/syntax validator. | Keep. |
| `docs/release-one.md` | `current` | Source of truth for Release-One config string / artifact / exclusions. | Keep. |
| `docs/release-one-hardware-audit.md` | `current` | HW-005 / FanTRIAC mapping resolution; LED policy. | Keep. |
| `docs/hardware/remaining-board-documentation-audit.md` | `current` | HW-004 / HW-006 audit classifying every `config/hardware-catalog.json` row by documentation state (`documented` / `partially-documented` / `cataloged-unverified` / `blocked` / `not-needed-for-release-one`); records evidence available vs. missing per board; preserves FanTRIAC blocked and LED Release-One-excluded statuses; no firmware / product / workflow / build-matrix change. | Keep. |
| `docs/hardware/hardware-artifact-policy.md` | `current` | HW-ASSETS-001 hardware artifact policy. Defines what hardware-related artifacts (schematics, KiCad source, KiCad PCB, project metadata, BOM, CPL / pick-and-place, gerbers, drill files, STEP, board images, vendor exports) may be committed to this repo, in what form, and at what review level. Forbids raw unreviewed ZIP dumps; explicitly excludes `__MACOSX/`, `.DS_Store`, `Icon` files / AppleDouble resource forks, `.history/`, embedded `.git/`, KiCad temporary / cache / backup files, vendor scratch exports, and private supplier / customer data. Classifies KiCad source, KiCad PCB, KiCad project metadata, BOM, CPL, gerbers, drill files, STEP, and board images as **retained-but-not-committed** under the current policy; explicitly states no Git LFS is introduced in this PR and that the long-term storage backend for large binary artifacts is an open decision. Records the per-board curated-index pattern under `docs/hardware/artifacts/` and the section structure such an index must follow. States that hardware artifact availability does not imply firmware support, WebFlash availability, build-matrix inclusion, product-catalog status, or Release-One promotion. Documentation only; preserves the Release-One product / artifact / build matrix / compatibility JSON / hardware-catalog statuses / product-catalog statuses / FanTRIAC HW-005 blocked status / Sense360 LED Release-One-excluded status; makes no compliance claim. Follow-up PR list: HW-ASSETS-002 (already lands together under Option C), HW-ASSETS-003 / 004 / 005 / 006 (expected only if artifact sources are provided for the named boards), HW-GAP-001 (board readiness matrix), S360-100-BENCH-001 (Core bench / manufacturing pass). | Keep. |
| `docs/hardware/artifacts/S360-310-R4.md` | `current` | HW-ASSETS-310 curated artifact index for Sense360 Relay (`S360-310-R4`). Records the uploaded module-side schematic `bb83a6a1-S360310R4.pdf` (38,967 bytes; SHA256 `441f0ccd681b5425fa9d276e6d7fb1bf289597674342dc8d9b8e656a23896c7d`), now committed byte-identical at `docs/hardware/schematics/S360-310-R4.pdf`. Records visible schematic content (section title "INLINE FAN CONTROL USING RELAY"; KiCad 10.0.3 single-sheet A4 export; title-block File `S360-310-R4.kicad_sch`; Title / Date / Rev fields blank; `J2` 3-pin "From Core" connector with pins 1 / 2 / 3 = `+5V` / `Relay` / `GND` matching Core-side `J4` net order; `K1` mechanical relay with 3-pin switching-contact side wired to `J1`; `Q1` MMBT3904 NPN low-side coil driver with `R1` 1 kΩ base series, `R2` 10 kΩ base pull-down, `D1` flyback diode across the coil; `J1` 3-pin "Inline Fan" load-side output; coil rail `+5V` with no on-board boost; **no opto-isolator, no on-board indicator LED, no mains-side snubber, no relay part number / coil-voltage / contact-current rating, no `NEXTION DISPLAY` connector, no mounting-hole references visible on the sheet**). Records reconciliation flags owed to `HW-PINMAP-310-FOLLOWUP` (silkscreen pin-1 on `J1` / `J2`; `J1` `NO` / `COM` / `NC` mapping; `K1` part identity / contact rating from BOM; Core-to-module harness identity) and to `CORE-ABSTRACT-BUS-001` (the `IO3` (Core schematic) vs `GPIO4` (`sense360_core_ceiling.yaml`) vs `GPIO10` (`sense360_core.yaml`) `relay_pin` disagreement). Records that KiCad source, KiCad PCB, KiCad project metadata, BOM, CPL, gerbers, drill files, STEP, board images, silkscreen photos, and bench / continuity / harness photos were not present in this upload (marked `not provided in this upload`, not fabricated). Explicitly does not change `config/hardware-catalog.json` (`S360-310` stays `schematic_status: cataloged_unverified`, `schematic_file` not set), does not change `config/product-catalog.json` / `config/webflash-builds.json` / `config/webflash-compatibility.json`, does not change any product YAML / WebFlash wrapper / package YAML (including `packages/expansions/fan_relay.yaml`, `packages/hardware/sense360_core_ceiling.yaml`, and `packages/hardware/sense360_core.yaml`), does not resolve the `IO3` vs `GPIO4` vs `GPIO10` `relay_pin` disagreement, does not edit the HW-PINMAP-310 audit doc at `docs/hardware/s360-310-r4-relay.md` beyond a cross-link addendum (status remains `pending — schematic/design evidence required`), does not unblock `PACKAGE-RELAY-001` / `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001`, does not unblock FanTRIAC (HW-005 stays a separate gate), does not change Release-One (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0-stable`), does not change the LED preview path (`Ceiling-POE-VentIQ-RoomIQ-LED`), does not change `REQUIRED_CONFIGS` or kits, does not change the mains-voltage compliance status of `S360-320` or `S360-400` (COMPLIANCE-001). | Keep. |
| `docs/hardware/artifacts/S360-311-R4.md` | `current` | HW-ASSETS-003 curated artifact index for Sense360 PWM (`S360-311-R4`). Records the uploaded module-side schematic `b4db0d64-S360311R4.pdf` (91,543 bytes; SHA256 `c910b3364be1d58fc44d12b5a189dade47efddf6cae158a86577ec7501e48006`), now committed byte-identical at `docs/hardware/schematics/S360-311-R4.pdf`. Records visible schematic content (MT3608 `+5V`→`+12V` boost; four 4-pin fan outputs `J1`/`J2`/`J4`/`J5` with low-side N-FETs; 13-pin `J3` "From Core" with pins 1–13 `+5V`/`TachIO`/`TachPMW1`/`Pul_Cou1`/`TachPMW2`/`Pul_Cou2`/`TachPMW3`/`Pul_Cou3`/`TachPMW4`/`Pul_Cou4`/`UART_RX`/`UART_TX`/`GND`; 4-pin Nextion `J6`; mounting holes `H1..H4`; section title "NINE 4pin FANs" recorded as an open documentation question). Records reconciliation flags owed to `HW-PINMAP-311` (Core J6 1-to-13 verify; UART on J3 pins 11/12 not yet captured Core-side). Records that KiCad source, KiCad PCB, KiCad project metadata, BOM, CPL, gerbers, drill files, STEP, and board images were not present in this upload (marked `not provided in this upload`, not fabricated). Explicitly does not change `config/hardware-catalog.json` (`S360-311` stays `schematic_status: cataloged_unverified`, `schematic_file` not set), does not change `config/product-catalog.json` / `config/webflash-builds.json` / `config/webflash-compatibility.json`, does not change any product YAML / WebFlash wrapper / package YAML, does not unblock FanTRIAC (HW-005 stays a separate gate), does not change Release-One. | Keep. |
| `docs/hardware/artifacts/S360-312-R4.md` | `current` | HW-ASSETS-003 curated artifact index for Sense360 DAC (`S360-312-R4`). Records the uploaded module-side schematic `682cf9e8-S360312R4.pdf` (122,230 bytes; SHA256 `2888f626bfa0139d2190f154f9b02ecf4cb06f2522a5b5802eaf96e16de39e28`), now committed byte-identical at `docs/hardware/schematics/S360-312-R4.pdf`. Records visible schematic content (MT3608 `+3.3V`→`+12V` boost; **two** `GP8403-TC50-EW` DACs `IC1` / `IC2` on a shared I²C bus, address-selectable via DIP `SW1` / `SW2` with 4.7 kΩ pullups; two 3-pin Cloudlift-style outputs `J2` / `J3`; 6-pin `J1` "From Core" with pins 1–6 `+3.3V`/`I2C_SDA`/`I2C_SCL`/`UART_RX`/`UART_TX`/`GND`; 4-pin Nextion `J7`; mounting holes `H1..H4`). Records reconciliation flags owed to `HW-PINMAP-312` (Module J1 pin-1 `+3.3V` vs Core J7 pin-1 `+5V` voltage-rail discrepancy; dual-DAC capacity broader than singular catalog description; I²C address-selection scheme). Records that KiCad source, KiCad PCB, KiCad project metadata, BOM, CPL, gerbers, drill files, STEP, and board images were not present in this upload (marked `not provided in this upload`, not fabricated). Explicitly does not change `config/hardware-catalog.json` (`S360-312` stays `schematic_status: cataloged_unverified`, `schematic_file` not set), does not change `config/product-catalog.json` / `config/webflash-builds.json`, does not change the `FanDAC` ↔ `AirIQ` mutex in `config/webflash-compatibility.json`, does not change any product YAML / WebFlash wrapper / package YAML, does not unblock FanTRIAC, does not change Release-One. | Keep. |
| `docs/hardware/artifacts/S360-410-R4.md` | `current` | HW-ASSETS-410 curated artifact index for Sense360 PoE PSU (`S360-410-R4`). Records the uploaded module-side schematic `c67f54ed-S360410R4.pdf` (975,137 bytes; SHA256 `4a8b7a3b2a89006a9332eaa486743f687aaedc4b6bb807c6b25670f742ac2414`), now committed byte-identical at `docs/hardware/schematics/S360-410-R4.pdf`. Records visible schematic content (KiCad 10.0.3 single-sheet A4 export; PDF version 1.5; title-block File `S360-410-R4.kicad_sch`; Title / Date / Rev fields blank; two visible section labels "PoE Power Supply" (upper block) and "Galvanic Isolated Part" (lower dashed-boundary block); `LAN_CON1` integrated magnetics / RJ45 connector module part `RJP-003TC1(LPJ4112CNL)` "Single 10/100 BASE-TX Filter Connector Module" with pin map 0=`Shield` / 1=`TD+` / 2=`TD-` / 3=`RD+` / 4=`TCT` / 5=`RCT` / 6=`RD-` / 7=`GND/NC` / 8=`NC/GND` / 9=`PW+` / 10=`PW-`, plus magnetics-side `J1`/`J2`/`J3`/`J6` data-pair termini, `J4,5` centre-tap network, `J7,8` PoE power-out side, Bob-Smith `2x1000pF/2KV` bridge + `2x75 Ohm` terminations, and `C3 1nF` shield-to-earth bridge; `U1 TPS2378DDAR(HSOIC-8)` PoE PD controller with pin map 1=`VDD` / 2=`DEN` / 3=`CLS` / 4=`VSS` / 5=`RTN` / 6=`CDB` / 7=`T2P` / 8=`APD` / 9=`EPAD`, `R1 24.9k` detection signature resistor, `R2 1.27k` classification programming with schematic-visible label `Class=0 (0.44 to 12.95W)`, `D1 SMAJ58A` TVS, `C1 100n` decoupling, `C2 15uf` labelled `CBULK`, `R5 0.03R` current sense, and schematic-visible MPS notes; `U2 TX4138(ESOIC-8)` buck with datasheet box "Input Range 4.5V to 60V Continuous Output Current 4A IBIAS(FB)=10nA Standby Current 400uA Output Adjustable 0.8V to 40V VFB=0.805V", pin map 1=`SW` / 2=`ILIM` / 3=`Vin` / 4=`GND` / 5=`FB` / 6=`EN` / 7=`POK` / 8=`BS` / 9=`ILIM`, `R3 9.1k` / `R4 9.1k` paired current-limit setting, `C4 100n`, `C5 12p`, `D2 ss510` Schottky catch, `L1 33uH` buck inductor, `R6 4.7R`, `C6 470u` output bulk, `C7 1n`, `R8 56.2k` (labelled `Rc`) and `R7 10.5k` (labelled `Rd`) feedback divider with formula `Vout = 0.8 * (1 + Rc/Rd)` on the sheet, and EN-pin note "TX4138's EN-Enable pin. Connect to low off the chip, Floating is enabled"; `DCDC1 F0505S-2WR2(SIP-7)` isolated 5V→5V DC/DC with `AM1D-0505S-NZ` annotated as alternate part and "ISOLATION" legend, pin map 1=`Vin+` / 2=`Vin-` / 4=`Vout-` / 6=`Vout+`; `J3` 2-pin output "Connection to Cores" with pin 1 = `+5VP` and pin 2 = `GND`, plus `C8 22u` output bulk and `R9 1k` output bleed; `D3 Green` status LED on buck output; four mounting holes `H1` / `H2` / `H3` / `H4` each labelled `Earth`; visible pre-isolation net names `Spare1` / `Spare2` / `Lan_earth` / `PoE_Power` / `PoE_SW` / `Sw_Vin_Poe` / `Earth` and post-isolation rails `+5VP` / `GND`; **no on-board PoE-present / link / activity indicator LED on the primary side, no spare-pair vs. data-pair selection switch, no explicit IEEE 802.3at signature classification network (schematic-visible `Class=0` annotation classifies the design as 802.3af Class 0), no on-board secondary regulator or LDO after the F0505S-2WR2 isolation block, no I²C / UART / SPI / DAC / GPIO / digital-bus circuitry, no JTAG / programming / Nextion connectors, no Core-side mating connector pinout (off-board)**). Records the **part-identity disagreement** between the package header in `packages/hardware/power_poe.yaml` (`Ag9712M, Silvertel Ag9700, or similar`) and the schematic-shown discrete topology (`TPS2378DDAR` + `TX4138` + `F0505S-2WR2` + `RJP-003TC1(LPJ4112CNL)`) as **unresolved by HW-ASSETS-410**; resolution belongs to `HW-PINMAP-410-FOLLOWUP` + BOM cross-check + `PACKAGE-POE-410-001`. Records reconciliation flags owed to `HW-PINMAP-410-FOLLOWUP` (silkscreen pin-1 on `J3`; PoE class declaration intent (`Class=0` on schematic vs `Class 0 / Class 1` in package header); whether the design is 802.3af-only or 802.3af/at-capable; on-board indicator topology against silkscreen; mounting-hole `H1`–`H4` electrical bonding to RJ45 shield through PCB; `F0505S-2WR2` isolation rating against datasheet) and to **PoE bench / load / link-up / thermal / EMI / isolation evidence** (PoE link-up against an 802.3af PSE and 802.3at PSE; signature / classification observation; load regulation at 5 V output; thermal rise of `U1` / `U2` / `DCDC1`; cold-start inrush; insulation resistance / Hi-pot / earth-continuity / leakage; conducted / radiated EMI / EMC — none derivable from a schematic alone). Records that KiCad schematic source, KiCad PCB source, KiCad project metadata, BOM, CPL, gerbers, drill files, STEP, board images, silkscreen photos, bench / load / link-up / thermal / EMI photos and measurements, IEEE 802.3af / 802.3at compliance test reports, and isolation / Hi-pot / earth-continuity / leakage reports were not present in this upload (marked `not provided in this upload`, not fabricated). Explicitly does not change `config/hardware-catalog.json` (`S360-410` stays `schematic_status: cataloged_unverified`, `schematic_file` not set), does not change `config/product-catalog.json` (Release-One `Ceiling-POE-VentIQ-RoomIQ` stays `status: production` / `channel: stable`, LED preview `Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview` / `channel: preview`, FanTRIAC `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked` / `blocker: HW-005` / `webflash_build_matrix: false`, the six `legacy-compatible` `*-poe` Core variants stay `legacy-compatible` and `webflash_build_matrix: false`), does not change `config/webflash-builds.json` (`Ceiling-POE-VentIQ-RoomIQ` `stable` and `Ceiling-POE-VentIQ-RoomIQ-LED` `preview` both stay verbatim), does not change `config/webflash-compatibility.json` (`POE` stays in `canonical_power` consumed by both committed builds), does not change any product YAML / WebFlash wrapper / package YAML (including `packages/hardware/power_poe.yaml`, which stays `package-yaml-ready` (logical, no GPIO binding) with its stale `Ag9712M / Silvertel Ag9700 / or similar` header), does not resolve the package-header vs schematic-shown part-identity disagreement, does not edit the HW-PINMAP-410 audit doc at `docs/hardware/s360-410-r4-poe.md` beyond a cross-link addendum (audit status remains `pending — schematic/design evidence required`), does not unblock `PACKAGE-POE-410-001` / `PRODUCT-POE-410-001` / `WEBFLASH-POE-410-001` / `RELEASE-POE-410-001` / `WF-IMPORT-POE-410-001`, does not promote the Release-One "schematic verification pending" caveat in `docs/release-one-hardware-audit.md` Findings → PoE PSU (the caveat language is preserved verbatim), does not resolve **HW-002 Open Question #6** (J2 PoE harness identity) and does not change the [S360-100-BENCH-001](hardware/s360-100-r4-core.md#s360-100-bench-001-status) status away from `pending — bench/manufacturing evidence required`, does not unblock FanTRIAC (HW-005 stays a separate gate), does not change Release-One (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0-stable` / `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`), does not change the LED preview path, does not change `REQUIRED_CONFIGS` or kits, does not change the `S360-400` Sense360 240v PSU status, does not change the mains-voltage compliance status of `S360-320` or `S360-400` (COMPLIANCE-001; PoE is SELV and `S360-410` is **not** in scope for COMPLIANCE-001). Makes no IEEE 802.3af / 802.3at PoE-compliance claim, no isolation / Hi-pot / earth-continuity / leakage claim, no thermal / EMI / EMC claim, and no Release-One requalification. | Keep. |
| `docs/hardware/artifacts/S360-400-R4.md` | `current` | HW-ASSETS-400 curated artifact index for Sense360 240v PSU (`S360-400-R4`). Records the uploaded module-side schematic `bb3c2227-S360400R4.pdf` (461,206 bytes; SHA256 `295e3ec9192603fd4ca7d89b8cda68777e5cb8e9713ed8b0fba2316babb0e765`), now committed byte-identical at `docs/hardware/schematics/S360-400-R4.pdf`. Records visible schematic content (section title "AC-DC REGULATION TO 5V"; KiCad 10.0.3 single-sheet A4 export; title-block File `S360-400-R4.kicad_sch`; Title / Date / Rev fields blank; 3-pin AC input `J1` with pins 1 / 2 / 3 = `LIVE` / `NEUTRAL` / `Earth_Protective`; resettable fuse `F1` value `A250-1200` in series on the LIVE leg; MOV `RV1` value `10D391K` across the AC line after `F1`; X-cap `C1` value `470nF` across the AC line in parallel with `RV1`; AC/DC module `PS1` value `HLK-10M05` with pins 1–4 = `AC(L)` / `AC(N)` / `-VO` / `+VO`; four-cap output filter `C5 100uF` / `C6 10u` / `C7 100n` / `C8 100uF` between `+VO` and `-VO`/`GND`; 2-pin output `J2` with pins 1 / 2 = `+5VP` / `GND`; four mounting holes `H1` / `H2` / `H3` / `H4` with no nets; **no Y-class capacitors, no common-mode line filter inductor, no secondary regulator, no on-board indicator LED, no thermal cut-out / NTC inrush limiter, no I²C / UART / DAC / GPIO circuitry visible on the sheet**). Records the **three-way AC/DC part-identity disagreement** between the catalog `description: Mains to 5V using HLK-5M05.` (`config/hardware-catalog.json` line 109), the package header in `packages/hardware/power_240v.yaml` (`HLK-PM01 or similar`), and the schematic-shown `PS1 = HLK-10M05` — recorded as **unresolved by HW-ASSETS-400**; resolution belongs to `HW-PINMAP-400-FOLLOWUP` + BOM cross-check. Records reconciliation flags owed to `HW-PINMAP-400-FOLLOWUP` (silkscreen pin-1 on `J1` / `J2`; `J1` / `J2` connector identity and rating; `F1` `A250-1200` hold / trip / voltage rating; `RV1` `10D391K` clamp voltage / energy rating; `C1` `470nF` X-cap safety class X1 / X2; absence of Y-caps as designed-or-not; output-filter cap voltage / dielectric / ESR ratings) and to `COMPLIANCE-001` (creepage / clearance / isolation / thermal / inrush / EMI / EMC / safety-review evidence — none of which is derivable from a schematic alone). Records that KiCad schematic source, KiCad PCB source, KiCad project metadata, BOM, CPL, gerbers, drill files, STEP, board images, silkscreen photos, bench / load / thermal / EMI photos and measurements, and compliance test reports (LVD / EMC / RoHS / CE / UKCA / FCC / UL) were not present in this upload (marked `not provided in this upload`, not fabricated). Explicitly does not change `config/hardware-catalog.json` (`S360-400` stays `schematic_status: cataloged_unverified`, `schematic_file` not set), does not change `config/product-catalog.json` (the four `legacy-compatible` `*-pwr` Core variants `sense360-core-c-pwr.yaml` / `sense360-core-w-pwr.yaml` / `sense360-core-v-c-pwr.yaml` / `sense360-core-v-w-pwr.yaml` stay `legacy-compatible` and `webflash_build_matrix: false`), does not change `config/webflash-builds.json` / `config/webflash-compatibility.json` (`PWR` stays reserved in `canonical_power` without any `webflash_build_matrix: true` entry), does not change any product YAML / WebFlash wrapper / package YAML (including `packages/hardware/power_240v.yaml`, which stays `package-yaml-pending` with its stale `HLK-PM01 or similar` header), does not resolve the three-way `HLK-5M05` / `HLK-PM01 or similar` / `HLK-10M05` part-identity disagreement, does not edit the HW-PINMAP-400 audit doc at `docs/hardware/s360-400-r4-power.md` beyond a cross-link addendum (status remains `pending — schematic/design evidence required`), does not unblock `PACKAGE-POWER-400-001` / `PRODUCT-POWER-400-001` / `WEBFLASH-POWER-400-001` / `RELEASE-POWER-400-001` / `WF-IMPORT-POWER-400-001`, does not clear `COMPLIANCE-001` for `S360-400` (or for `S360-320`), does not unblock FanTRIAC (HW-005 stays a separate gate), does not change Release-One (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0-stable`), does not change the LED preview path (`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`, `channel: preview`), does not change FanTRIAC state (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`), does not change `REQUIRED_CONFIGS` or kits, does not change the `S360-410` PoE PSU status or its documented "schematic verification pending" caveat. Makes no CE / UKCA / FCC / UL / LVD / EMC / RoHS claim and no standard or advanced / manual-warning WebFlash exposure approval. | Keep. |
| `docs/hardware/artifacts/S360-320-R4.md` | `blocked-reference` | HW-ASSETS-003 curated artifact index for Sense360 TRIAC (`S360-320-R4`). Records the uploaded module-side schematic `631ef0c1-S360320R4.pdf` (54,565 bytes; SHA256 `4cd0685251dcdbc7aa8933cbfa92008df46940b6349f0dea91d32e1028c2911f`), now committed byte-identical at `docs/hardware/schematics/S360-320-R4.pdf`. Records visible schematic content ("TRIAC CIRCUIT"; 3-pin AC LINE `J1`; 2-pin LOAD `J2`; `Q1 BT136S-600D,118` TRIAC; `U1 MOC3023M` optotriac driver with `R3 220 Ω` LED-side limit and `R1 1 kΩ` / `R2 100 Ω` snub / gate resistors; `OK1 EL814` zero-cross optocoupler with symmetric `R5 33 kΩ` / `R6 33 kΩ` mains-side bias and `R4 10 kΩ` pull-up to `+3V3`; 4-pin `J3` "From Core" with pins 1–4 `+3V3`/`ESP_GPIO1`/`ESP_GPIO2`/`GND`). Records reconciliation flags owed to `HW-PINMAP-320` (Core `TRI_GPIO*` vs Module `ESP_GPIO*` naming; AC LINE `J1` 3-pin function open). Records that the module uses discrete `MOC3023M` + `BT136` + `EL814` with no on-board controller IC, **eliminating Option (b) (replacement non-`ac_dimmer` driver targeting an on-board controller IC) from the HW-005 missing-evidence checklist for this revision**, but **not** unblocking HW-005 — Option (a) (end-to-end direct interrupt-capable ESP32 GPIOs traced through `S360-100-R4` + `S360-320`) still requires the Core-side `TRI_GPIO*` trace, which currently routes via SX1509. Records that KiCad PCB, BOM, and gerbers are COMPLIANCE-001-adjacent (creepage / clearance / component voltage ratings) and were not in this upload. Explicitly does not change `config/hardware-catalog.json` (`S360-320` stays `schematic_status: cataloged_unverified`, `schematic_file` not set), does not change `config/product-catalog.json` (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`), does not change `config/webflash-builds.json` / `config/webflash-compatibility.json` (Release-One `blocked_modules` still includes `FanTRIAC`), does not change any product YAML / WebFlash wrapper / package YAML (`packages/expansions/fan_triac.yaml` keeps its BLOCKED / UNVERIFIED banner and placeholder GPIOs), **does not unblock FanTRIAC under HW-005, and does not clear `S360-320` under COMPLIANCE-001 — both blockers remain in force**, does not change Release-One. | Keep. |
| `docs/hardware/artifacts/S360-100-R4.md` | `current` | HW-ASSETS-002 curated artifact index for Sense360 Core (`S360-100-R4`). Records that the upload was five loose files (not a packed ZIP): `83537ddc-S360100R4.pdf` (849,828 bytes), `bc386261-S360100R4_BOM.xlsx` (12,543 bytes), `d5bb9e7b-S360100R4pos.csv` (4,803 bytes), `2248fe0e-S360100R4gerbers.zip` (290,097 bytes, 15 inner files under `S360-100-R4-gerbers/` with legacy prefix `Sense360_Core_R4-*`, 4-layer board: F_Cu / In1_Cu / In2_Cu / B_Cu), and `0a7f7965-S360100R4.step` (6,335,475 bytes), each with its SHA256. Records that the uploaded PDF is byte-identical (SHA256 `173a60792703923c69639772c4e23531faedf8a88e5147656d133a6317acf435`, 849,828 bytes) to the already-committed `docs/hardware/schematics/S360-100-R4.pdf` and is therefore not re-committed. Records that KiCad schematic source, KiCad PCB source, KiCad project metadata (`.kicad_pro`, `.kicad_prl`, `fp-lib-table`), board images, the raw `S360-100-R4.zip`, `__MACOSX/`, `.DS_Store`, `Icon` files, `.history/`, and embedded `.git/` were **not** present in this upload; missing files are recorded as `not provided in this upload` (not fabricated, not labelled `pending`). Applies the HW-ASSETS-001 policy: BOM / CPL / gerbers / drill / STEP are **retained-but-not-committed** under the current policy and are not committed in this PR. Records artifact-specific open questions (long-term storage backend, KiCad source delivery, gerber inner-filename prefix `Sense360_Core_R4-*` vs canonical `S360-100-R4-*`, image set, manufacturing-archive retention). Cross-references the pre-existing Core schematic-level Open Questions in `docs/hardware/s360-100-r4-core.md` (J6 / J10 pin order, IO10 net label, IO39–42 ↔ TPx mapping, J2 PoE harness identity, `AirQ_Led` / `AirQ_Status_Led` reuse, FanTRIAC GPIO mapping) without re-litigating them. States explicitly that this index does not edit `config/hardware-catalog.json` (`S360-100` row stays `schematic_status: verified`, `schematic_file: docs/hardware/schematics/S360-100-R4.pdf`), does not edit `config/product-catalog.json`, `config/webflash-builds.json`, or `config/webflash-compatibility.json`, does not edit any product YAML, WebFlash wrapper, or package YAML, does not change WebFlash availability, does not regenerate firmware, does not create releases, does not unblock FanTRIAC (HW-005 stays a separate gate), and does not promote Sense360 LED into the Release-One config string. Release-One stays `Ceiling-POE-VentIQ-RoomIQ`; the LED preview path `Ceiling-POE-VentIQ-RoomIQ-LED` is unchanged. Follow-up PR list: HW-ASSETS-003 / 004 / 005 / 006 (expected only if artifact sources are provided for the named boards), HW-GAP-001, S360-100-BENCH-001. | Keep. |
| `docs/compliance/mains-voltage-uk-eu-assessment.md` | `current` | COMPLIANCE-001 mains-voltage UK / EU compliance-assessment tracker for `S360-400` Sense360 240v PSU and `S360-320` Sense360 TRIAC; expands the mains-voltage safety / compliance note in `docs/hardware/remaining-board-documentation-audit.md` into a per-board evidence checklist (product classification, protection-class decision tree, standards / regulations applicability, electrical-safety topics, EMC topics, preview-vs-stable evidence, technical-file checklist, DoC checklist, open questions for compliance engineer / test lab, release blockers); documentation only; makes no CE / UKCA / LVD / EMC / RED / RoHS / "safe for mains" / "approved for mains" claim and uses `Likely applicable` / `To be confirmed` / `Requires qualified review` / `Not proven by this repository` framing throughout; preserves the FanTRIAC HW-005 blocked status, the Sense360 LED Release-One-excluded status, every `config/hardware-catalog.json` `schematic_status` value, every `config/product-catalog.json` lifecycle status, and the Release-One PoE-only config string `Ceiling-POE-VentIQ-RoomIQ`; no firmware / product / config / workflow / build-matrix change. | Keep. |
| `docs/product-onboarding.md` (PRODUCT-005 cross-link refresh; RELEASE-005 LED proof refresh) | `current` | PRODUCT-004 cross-doc product onboarding guide. Orders the existing guardrails (hardware audit, mains-voltage compliance tracker, product catalog, consistency validator, WebFlash build matrix, release-notes generator, build / release proof, WebFlash handoff) into a safe sequence for adding a new product / config; lists preview-vs-production evidence gates, where each source of truth lives, the read-only commands to run, the explicit guardrails ("do not mark `production` just because YAML compiles", "do not add blocked products to the build matrix", "do not add FanTRIAC until HW-005 evidence changes", "do not add `LED` to Release-One without an LED token and hardware evidence", "do not treat `legacy-compatible` as WebFlash-shippable", "do not use mains-voltage boards before compliance review", "do not hand-edit generated manifests"), a Release-One worked example and a blocked-FanTRIAC worked example, and the future WebFlash handoff contract; documentation only; preserves the Release-One product / artifact / build matrix / compatibility JSON / hardware SKUs / catalog statuses / FanTRIAC HW-005 blocked status / Sense360 LED Release-One-excluded status. PRODUCT-005 refreshes the LED guardrail and the See-also list with a pointer to `docs/product-led-preview-decision.md` and the PRODUCT-006 / PRODUCT-007 / PRODUCT-008 / PRODUCT-009 follow-up PR sequence. RELEASE-005 updates the LED guardrail and the `docs/webflash-release-proof.md` See-also entry to record that the LED preview build / release proof is now recorded (tag `v1.0.0-led-preview`, run `25918422743`, artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` (1,135,904 bytes; SHA256 `93310d2cbc27355e399f36a232336b6b9075dacfc178d603c7a92aa1089182d3`), validators passed); the LED catalog entry stays `preview`; Release-One stays unchanged; FanTRIAC stays blocked; WebFlash-side import remains the only outstanding step before LED becomes WebFlash-shippable. | Keep. |
| `docs/product-led-preview-decision.md` (RELEASE-005 LED proof refresh) | `current` | PRODUCT-005 LED preview product path decision doc. Records that verified Sense360 LED schematic evidence (HW-007 / HW-008) plus the ceiling LED package pin fix (HW-010) do not by themselves make Sense360 LED WebFlash-shippable; enumerates the current evidence, the canonical LED-bearing config string `Ceiling-POE-VentIQ-RoomIQ-LED`, the catalog status options against the consistency validator's lifecycle rule blocks, and the product YAML / WebFlash wrapper / build-matrix entry / release-notes draft / build-release proof artefacts that would still be required. Decision table covers Options A–E (documented only / `compile-only` catalog entry / `preview` entry without build matrix / `preview` entry with wrapper + build matrix / Release-One `production` edit) and picks **Option A for this PR, with Option C later**. Defines the scoped follow-up PR sequence: PRODUCT-006 (add LED-bearing product YAML), PRODUCT-007 (add `compile-only` catalog entry), PRODUCT-008 (add WebFlash wrapper and promote to `preview`), PRODUCT-009 (add `preview` build to the build matrix + record a build / release proof + re-scope `tests/test_led_package_mapping.py` LED-exclusion to the Release-One build only + update `scripts/generate_webflash_release_notes.py` so the LED-bearing build emits Sense360 LED as a Feature). States the guardrails: verified LED schematic + fixed package pin mapping does not equal shippable product; LED is still not in current Release-One; WebFlash must not expose LED until there is a catalog-eligible product, artifact, and manifest; FanTRIAC remains unrelated and blocked. Documentation only; preserves the Release-One product / artifact / build matrix / compatibility JSON / hardware-catalog statuses / product-catalog statuses / FanTRIAC HW-005 blocked status / mains-voltage compliance status / Sense360 LED Release-One-excluded status; PRODUCT-005 adds no product YAML, no WebFlash wrapper, no catalog entry, no build-matrix entry, no release-notes draft, no tests, no scripts, no workflow change. RELEASE-005 updates the PRODUCT-009 outstanding-proof paragraph and the "Current evidence" no-artifact bullet to reflect that the LED preview build / release proof is now recorded (tag `v1.0.0-led-preview`, run `25918422743`, artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` (1,135,904 bytes; SHA256 `93310d2cbc27355e399f36a232336b6b9075dacfc178d603c7a92aa1089182d3`)), and updates the See-also pointer to `docs/webflash-release-proof.md` to mention the RELEASE-005 backfill; the LED catalog entry stays `preview`, Release-One stays unchanged, FanTRIAC stays blocked, and WebFlash-side import remains the only outstanding step. | Keep. |
| `docs/preview-to-stable-promotion-gates.md` (RELEASE-006) | `current` | RELEASE-006 canonical, cross-cutting preview-to-stable promotion gate document. Defines, for any future preview product (today the LED preview; tomorrow AirIQ-bearing / FanRelay-bearing / FanPWM-bearing / FanDAC-bearing / PWR-bearing variants), what evidence + sign-offs are required to promote a preview build to `status: production` / `channel: stable`. Includes: a 17-row gate summary table (product YAML, WebFlash wrapper, catalog preview entry, build-matrix preview entry, preview release artifact, preview release proof recorded, WebFlash import, live preview deploy, real WebFlash flash proof (WF-HW-TEST-001), hardware bench verification, stable release notes, production catalog promotion, stable build artifact, stable WebFlash import, REQUIRED_CONFIGS decision, kit / UI decision, human approval) with an owning-repo column and a live LED-preview status column; required upstream / firmware / hardware / WebFlash / operator evidence; per-field promotion diffs for `config/product-catalog.json` and `config/webflash-builds.json`; the human approval checklist (hardware, release engineer, WebFlash operator, compliance if mains, REQUIRED_CONFIGS decision, kit decision, release authority); the explicit "preview artifact + WebFlash import + deployed manifest do not equal stable" guardrails; the separate `REQUIRED_CONFIGS` policy (a stable build is **not** automatically added to baseline-health REQUIRED_CONFIGS — that is a separate WebFlash decision); the separate kit policy (a stable build does **not** automatically get a kit — that is a separate WebFlash product decision); a six-PR follow-up sequence for a future stable promotion (hardware bench verification → operator flash proof → stable release-notes + tag → catalog + build-matrix promotion → WebFlash stable import → optional REQUIRED_CONFIGS / kit PRs); and an LED preview case study marking rows 1–8 (preview floor) `done` and rows 9–17 explicitly `pending` / `decision needed` (operator flash proof WF-HW-TEST-001, S360-300 bench verification of harness rail / LED count / harness identity per `docs/hardware/s360-300-r4-led.md`, stable release notes, production catalog promotion, stable build artifact, stable WebFlash import, REQUIRED_CONFIGS decision, kit decision, recorded human approval). RELEASE-006 itself is documentation only: no `config/*`, `products/*`, `products/webflash/*`, `packages/*`, `scripts/*`, `tests/*`, `.github/workflows/*`, `components/*`, or `include/*` change; no firmware regenerated; no LED promotion (LED catalog stays `status: preview`, `channel: preview`); no Release-One change (`Ceiling-POE-VentIQ-RoomIQ`, `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag `v1.0.0`); no FanTRIAC unblock (HW-005 stays open; FanTRIAC is called out as the canonical blocked-module example and is explicitly **not** on the stable promotion path); no `REQUIRED_CONFIGS` or kit additions in the WebFlash repo. Cross-linked from `docs/product-onboarding.md`, `docs/product-led-preview-decision.md`, `docs/webflash-release-proof.md`, `docs/webflash-release-handoff.md`, and `docs/hardware/s360-300-r4-led.md` (Open Questions section). | Keep. |
| `docs/webflash-compatibility-taxonomy-audit.md` | `current` | COMPAT-001 per-token audit of `config/webflash-compatibility.json` against `config/product-catalog.json`, `config/webflash-builds.json`, `config/hardware-catalog.json`, `docs/hardware/remaining-board-documentation-audit.md`, `docs/compliance/mains-voltage-uk-eu-assessment.md`, and `docs/product-onboarding.md`. Records the source-of-truth separation (taxonomy / lifecycle / build matrix / hardware), the explicit "taxonomy != shippability" policy, a full per-token decision table (Ceiling, POE, PWR, USB, AirIQ, VentIQ, RoomIQ, FanRelay, FanPWM, FanDAC, FanTRIAC, LED, Voice) with hardware-evidence and follow-up columns, the current Release-One mapping, the blocked / excluded modules summary (FanTRIAC per HW-005, LED per Release-One config-string policy), the future-token policy, a test-coverage summary (existing tests + the six drift-protection tests added in the same PR), recommended follow-up PRs (HW-007 schematic ingest, future LED variant, FanTRIAC unblock, AirIQ / FanRelay / FanPWM / FanDAC preview entries, future PWR-bearing entry, optional forbidden-token alignment with `docs/webflash-contract.md` §3), and an explicit do-not-change list; flags that new schematic PDFs for `S360-100`, `S360-200`, `S360-210`, `S360-211`, and `S360-300` are deferred to HW-007 and do not change COMPAT-001 decisions; documentation only; preserves the Release-One product / artifact / build matrix / compatibility JSON / hardware SKUs / catalog statuses / FanTRIAC HW-005 blocked status / Sense360 LED Release-One-excluded status. HW-007 has now landed: the HW-007 note block is refreshed to record that the PDFs and per-board AirIQ / VentIQ / LED docs are committed and that the JSON `schematic_status` refresh is deferred to HW-008 (per-token cells for AirIQ / VentIQ / LED gain inline pointers to the new docs; no verdict / shippability cell changes; the VentIQ "schematic verification pending" caveat is retained until HW-008). | Keep. |
| `docs/hardware/schematics/` | `current` | HW-007 schematic evidence directory. Contains the committed module-side schematic PDFs: `S360-100-R4.pdf` (Core, HW-007), `S360-200-R4.pdf` (RoomIQ, HW-007), `S360-210-R4.pdf` (AirIQ, HW-007), `S360-211-R4.pdf` (VentIQ, HW-007), `S360-300-R4.pdf` (Sense360 LED, HW-007), `S360-311-R4.pdf` (PWM, HW-ASSETS-003), `S360-312-R4.pdf` (DAC, HW-ASSETS-003), `S360-320-R4.pdf` (FanTRIAC, HW-ASSETS-003), `S360-310-R4.pdf` (Relay, HW-ASSETS-310), `S360-400-R4.pdf` (240v PSU, HW-ASSETS-400 / PR #514), and `S360-410-R4.pdf` (PoE PSU, HW-ASSETS-410). Each PDF is the authoritative source of truth for its corresponding standalone reference doc under `docs/hardware/` (or for its curated artifact index under `docs/hardware/artifacts/` for the boards whose pin-map audit has not yet promoted to schematic-backed). | Keep. |
| `docs/hardware/s360-210-r4-airiq.md` | `current` | HW-007 standalone pin / connector reference doc for `S360-210-R4` Sense360 AirIQ. Mirrors the structure of `docs/hardware/s360-100-r4-core.md` / `docs/hardware/s360-200-r4-roomiq.md`: board identity, schematic source (citing `schematics/S360-210-R4.pdf`), main components visible on the sheet (SGP41, SCD41, SFA40 connector, SPS30 connector, MICS-4514 + STM8 I²C-bridge sub-sheet), Core-side J9 mating table, I²C bus, Open Questions, firmware-mapping notes, and an explicit HW-007 scope / non-scope block. Explicitly states AirIQ remains mutually exclusive with VentIQ, not in Release-One, and not WebFlash-shippable — HW-007 only improves legacy / manual hardware documentation. JSON `schematic_status` flip is now refreshed by HW-008 (`verified`, `schematic_file: docs/hardware/schematics/S360-210-R4.pdf`); HW-008 does not change AirIQ's WebFlash-shippability, mutex, or Release-One status. | Keep. |
| `docs/hardware/s360-211-r4-ventiq.md` | `current` | HW-007 standalone pin / connector reference doc for `S360-211-R4` Sense360 VentIQ. Same template as the AirIQ doc. Captures SGP41 on board, IR-temperature connector, SPS30 connector, on-board fan-relay drive circuitry, and Core-side J9 mating. Explicitly records: Release-One config string remains `Ceiling-POE-VentIQ-RoomIQ`; package filename `airiq_bathroom_base.yaml` retained per WebFlash contract §6; mains-side topology, contact rating, and creepage / clearance for the on-board relay are tracked separately under COMPLIANCE-001 — HW-007 makes no compliance claim. JSON `schematic_status` and the "schematic verification pending" caveat in `release-one-hardware-audit.md` / `webflash-compatibility-taxonomy-audit.md` are now refreshed by HW-008 (JSON: `verified`, `schematic_file: docs/hardware/schematics/S360-211-R4.pdf`; the caveat is retired). HW-008 does not change Release-One config / build matrix / artifact / lifecycle / mains compliance. | Keep. |
| `docs/hardware/s360-300-r4-led.md` (HW-010 refresh) | `current` | HW-007 standalone reference doc for `S360-300-R4` Sense360 LED. Captures J1 (3-pin: LED_DATA / +5V / GND) and the on-board WS2812B LED chain. Explicitly records: Sense360 LED is **not** in Release-One; the Release-One config string `Ceiling-POE-VentIQ-RoomIQ` carries no `LED` token; the Release-One YAML omits LED package includes on purpose. JSON `schematic_status` flip refreshed by HW-008 (`verified`, `schematic_file: docs/hardware/schematics/S360-300-R4.pdf`); HW-008 did **not** add `LED` to the Release-One config string. The `GPIO14` (package) vs `IO38` (Core schematic) `LED_DATA` discrepancy at the package level has since been **resolved by HW-010** — the ceiling LED package now binds `led_data_pin: GPIO38`. HW-010 did not add `LED` to the Release-One config string, did not add a WebFlash LED build, did not add a product-catalog LED entry, did not promote Sense360 LED to WebFlash-shippable, and did not change the FanTRIAC HW-005 blocker. The wall LED and legacy S3 Core packages remain unresolved at the package level. | Keep. |
| `docs/hardware/s360-300-r4-led.md` (S360-300-BENCH-001 section) | `current` | S360-300-BENCH-001 bench-verification tracking record for the Sense360 LED (`S360-300-R4`) board. Companion to the schematic-side Open Questions in the same doc and to RELEASE-006 row 10 (hardware bench verification) in `docs/preview-to-stable-promotion-gates.md`. Records the bench gate as **`pending — bench hardware evidence required`**: no operator, no bench date, no physical S360-300 board / Core board / revision identification, no harness used, no Core / LED connector exercised, no rail measurement (`J1` pin 2 `+5V` vs `+3.3V`), no data-pin / signal-path observation, no ground / power continuity observation, no LED count, no LED type identification, no test / preview firmware used, no flash source, no observed LED ring behaviour (boot pattern, brightness, colour order), no photos / screenshots / serial logs / scope captures / measurements, no known anomalies. The four per-question rows (harness rail per Open Question 1; LED count per Open Question 2; harness identity per Open Question 4; observed LED ring behaviour) are each `pending — bench hardware evidence required`. Allowed status vocabulary fixed at: `pending — bench hardware evidence required` / `partial — some bench evidence recorded, but open questions remain` / `verified — all listed bench questions answered by evidence` / `failed / blocked — bench test produced a blocking issue`. Implicit acceptance is not allowed; values are not invented. Section is documentation only and explicitly **does not**: promote Sense360 LED to `status: production` / `channel: stable`; add `LED` to the Release-One config string (Release-One stays `Ceiling-POE-VentIQ-RoomIQ`, artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag `v1.0.0`); add Sense360 LED to WebFlash-side `REQUIRED_CONFIGS` (default per RELEASE-006 §REQUIRED_CONFIGS policy stays **do not add**); add a Sense360 LED kit entry to WebFlash-side `scripts/data/kits.json` (default per RELEASE-006 §Kit policy stays **do not add**); substitute for the WebFlash operator flash proof (`WF-HW-TEST-001` row 9 stays separately `pending` in the WebFlash repo); flip `S360-300` in `config/hardware-catalog.json` (already `schematic_status: verified` under HW-008 — bench evidence is a separate axis); change FanTRIAC (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`); change mains-voltage compliance status for `S360-320` or `S360-400` (owned by COMPLIANCE-001); advance any future "RELEASE-007" LED stable promotion (any such promotion still requires closing all four bench questions here **and** clearing every other RELEASE-006 row). Adds no edits to `config/*`, `products/*`, `products/webflash/*`, `packages/*`, `tests/*`, `scripts/*`, `components/*`, `include/*`, or `.github/workflows/*`. Cross-linked from `docs/hardware/s360-300-r4-led.md` (Open Questions section), `docs/preview-to-stable-promotion-gates.md` (row 10 and §Pending → Row 10 bullet), and `docs/hardware/board-readiness-matrix.md` (S360-300 productization-axis row, S360-300 §Open work / stable gate bullet, §Preserved guardrail block). | Keep. |
| `docs/hardware/s360-100-r4-core.md` (HW-007 cross-link refresh) | `current` | Existing Core hardware reference doc; HW-007 changes the `Schematic source` table to point at `[`schematics/S360-100-R4.pdf`](schematics/S360-100-R4.pdf)` and adds a one-line `HW-007 — PDF committed` admonition. No pin tables, Open Questions, or reconciliation flags changed. | Keep. |
| `docs/hardware/s360-100-r4-core.md` (S360-100-BENCH-001 section) | `current` | S360-100-BENCH-001 bench / manufacturing tracking record for the Sense360 Core (`S360-100-R4`) board. Companion to the schematic-side Open Questions in the same doc and to the artifact-side Open Questions in `docs/hardware/artifacts/S360-100-R4.md` (HW-ASSETS-002). Records the Core board bench / manufacturing gate as **`pending — bench/manufacturing evidence required`**: no operator / reviewer, no review date, no physical S360-100-R4 board (serial / batch) identification, no board revision marking, no connector silkscreen / J-numbering observation, no `J2` PoE harness identity, no `J6` 1-to-13 silkscreen pin order, no `J10` 1-to-12 silkscreen pin order, no `IO10` net label observation, no `IO39`–`IO42` ↔ TP mapping, no JTAG-header observation, no `AirQ_Led` / `AirQ_Status_Led` reuse observation, no BOM review (`bc386261-S360100R4_BOM.xlsx`, 12,543 B), no CPL review (`d5bb9e7b-S360100R4pos.csv`, 4,803 B), no Gerber review (`2248fe0e-S360100R4gerbers.zip`, 290,097 B, 4-layer `F_Cu` / `In1_Cu` / `In2_Cu` / `B_Cu`), no STEP / mechanical review (`0a7f7965-S360100R4.step`, 6,335,475 B), no schematic-to-fabrication consistency observation, no photos / silkscreen captures / scope traces / continuity measurements / serial logs, no known anomalies. The per-question rows (`J2` PoE harness identity; `J6` 1-to-13 silkscreen pin order; `J10` 1-to-12 silkscreen pin order; `IO10` net label; `IO39`–`IO42` ↔ TPx mapping; JTAG / programming header existence; `AirQ_Led` / `AirQ_Status_Led` reuse on VentIQ vs AirIQ; BOM / CPL / Gerber / STEP manufacturing-artifact review; gerber inner-filename prefix `Sense360_Core_R4-*` vs canonical `S360-100-R4-*`; schematic-to-fabrication consistency) are each `pending — bench/manufacturing evidence required`. Allowed status vocabulary fixed at: `pending — bench/manufacturing evidence required` / `partial — some evidence recorded, but open questions remain` / `verified — all listed Core board bench/manufacturing questions answered by evidence` / `failed / blocked — evidence produced a blocking issue`. Implicit acceptance is not allowed; values are not invented. Section is documentation only and explicitly **does not**: change Release-One (Release-One stays `Ceiling-POE-VentIQ-RoomIQ`, artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag `v1.0.0`); change the LED preview path (`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`, `channel: preview`); unblock FanTRIAC (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`); change mains-voltage compliance status for `S360-320` or `S360-400` (owned by COMPLIANCE-001); flip `S360-100` in `config/hardware-catalog.json` (already `schematic_status: verified` under HW-008 — bench/manufacturing evidence is a separate axis); add or modify any product YAML, WebFlash wrapper, package YAML, WebFlash build, `REQUIRED_CONFIGS`, or kit entry; resolve any schematic-side Open Question on its own (it records bench / manufacturing observations against them); substitute for any Release-One firmware proof (REL-001) or LED preview build / import / deploy proof (WF-LED-001 / WF-LED-002 / WF-LED-003 / WF-DEPLOY-001). Adds no edits to `config/*`, `products/*`, `products/webflash/*`, `packages/*`, `tests/*`, `scripts/*`, `components/*`, `include/*`, or `.github/workflows/*`. Cross-linked from `docs/hardware/s360-100-r4-core.md` (Open Questions section forward-pointer), `docs/hardware/artifacts/S360-100-R4.md` (Open Questions paragraph + Follow-up PRs row), `docs/hardware/board-readiness-matrix.md` (S360-100 productization-axis row, S360-100 §Board-by-board notes Open-work bullet, §Preserved guardrail block), `docs/hardware/firmware-package-mapping-audit.md` (Core J10 vs RoomIQ J6 row resolution paragraph), `docs/hardware/remaining-board-documentation-audit.md` (Sense360 Core §Evidence missing bullet), and `docs/release-one-hardware-audit.md` (PoE PSU + Core / RoomIQ connector findings rows). | Keep. |
| `docs/hardware/s360-320-r4-triac.md` (HW-PINMAP-320) | `current` | HW-PINMAP-320 per-board pin / package mapping audit doc for `S360-320-R4` Sense360 TRIAC (FanTRIAC). Records the audit as **`partial — schematic evidence available; package reconciliation, timing validation, and compliance/certification pending`**: the module-side schematic PDF `docs/hardware/schematics/S360-320-R4.pdf` and the curated artifact index `docs/hardware/artifacts/S360-320-R4.md` are both committed under HW-ASSETS-003, but the standalone schematic-backed reference doc, the pin-map reconciliation against the verified end-to-end ESP32 GPIO trace, the package YAML reconciliation, the timing / zero-cross / real-load bench validation, the mains-voltage UK / EU compliance review, and any advanced / manual-warning WebFlash exposure are not produced by this PR. Consumes the HW-ASSETS-003 artifact index without rewriting it. Inventories the current committed evidence (committed module-side schematic PDF; curated artifact index; Core-side `J15` 4-pin connector capture in `docs/hardware/s360-100-r4-core.md` §J15 — `+3.3V` / `TRI_GPIO1` / `TRI_GPIO2` / `GND`; module-side `J3` 4-pin "From Core" capture with `+3V3` / `ESP_GPIO1` / `ESP_GPIO2` / `GND`; TRIAC switching device `Q1 BT136S-600D,118`; optotriac driver `U1 MOC3023M` with `R3 220 Ω` LED-side limit, `R1 1 kΩ` gate resistor, `R2 100 Ω` AC-side return snub; zero-cross optocoupler `OK1 EL814` with symmetric `R5 33 kΩ` / `R6 33 kΩ` mains-side bias and `R4 10 kΩ` pull-up to `+3V3`; 3-pin AC LINE `J1`; 2-pin LOAD `J2`; no on-board controller IC; firmware package `packages/expansions/fan_triac.yaml` with BLOCKED / UNVERIFIED banner and `ac_dimmer` driver topology requiring direct interrupt-capable ESP32 GPIOs; blocked reference product YAML `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml` with placeholder `fan_triac_gate_pin: GPIO5` / `fan_triac_zc_pin: GPIO6`; blocked WebFlash wrapper `products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`; product-catalog entry `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` at `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`; `FanTRIAC` token reservation in `config/webflash-compatibility.json` `canonical_modules` subject to the fan-driver `max-one-of` rule and carried in Release-One / LED preview `blocked_modules` lists; existing classifications in `docs/hardware/board-readiness-matrix.md`, `docs/hardware/remaining-board-documentation-audit.md`, `docs/hardware/firmware-package-mapping-audit.md`, `docs/product-availability-taxonomy.md`, `docs/hardware/hardware-artifact-policy.md`). Records the `TRI_GPIO*` (Core) vs `ESP_GPIO*` (Module) net-name divergence as **conflict / unresolved** — same physical wires, different labels — and owes the canonical-naming choice to HW-PINMAP-320-FOLLOWUP. Records the `ac_dimmer`-vs-SX1509 timing constraint as **conflict / unresolved**: `ac_dimmer` requires direct interrupt-capable ESP32 GPIOs for both `gate_pin` and `zero_cross_pin`; the Core-side `TRI_GPIO1` / `TRI_GPIO2` nets continue to route via the SX1509 expander (`U3`) on the Core sheet, which the timing analysis in `docs/release-one-hardware-audit.md#timing-constraint-ac_dimmer-vs-sx1509-expander` rejects. Records that the module-side schematic eliminates Option (b) (replacement non-`ac_dimmer` driver targeting an on-board controller IC) from the HW-005 missing-evidence checklist for this revision (no on-board controller IC), but does **not** unblock HW-005 — Option (a) (direct ESP32 GPIOs traced end-to-end through `S360-100-R4` + `S360-320`) still requires the Core re-trace. Records the placeholder `fan_triac_gate_pin: GPIO5` / `fan_triac_zc_pin: GPIO6` mapping as **disagreeing with the Core schematic** (RoomIQ J10 nets `SEN0609_TX` / `out(gpio6)` already claim those pins). Records the AC LINE `J1` 3-pin function (L / N / PE / doubled-line) as **not recorded** — requires silkscreen / PCB-source evidence and is COMPLIANCE-001-adjacent. Records the intended **advanced / manual-warning long-term product posture** for FanTRIAC: **visible / selectable**, **buildable after package evidence**, **installable only through an advanced / manual-warning path**; **not** Release-One, **not** REQUIRED_CONFIGS, **not** recommended, **not** kit / default, **not** compliance-certified. **Compliance status is not a reason to remove or hide the board from the repo; it is a reason to keep explicit warning / advanced-manual / non-certified language attached to every surface that mentions FanTRIAC, until both HW-005 and COMPLIANCE-001 clear.** The advanced / manual-warning posture is **intent only**; this PR does **not** realise it. Lists missing evidence in full: confirmed pin map (HW-PINMAP-320-FOLLOWUP), package YAML reconciliation (PACKAGE-TRIAC-001 / `PACKAGE-GAP-001` FanTRIAC slice), timing validation, zero-cross / phase-control validation, real-load test evidence, thermal / safety review, mains compliance / certification (COMPLIANCE-001), operator flash / runtime validation, advanced-warning UX approval, release / import gate approval, schematic-status promotion PR (HW-CATALOG-320). Defines the follow-up PR sequence (`HW-PINMAP-320-FOLLOWUP` standalone schematic-backed reference doc + pin-map reconciliation; `HW-005` unblock work — Option (a) Core re-trace; separate JSON PR `HW-CATALOG-320` for `S360-320` `schematic_status` promotion; `PACKAGE-TRIAC-001` for package YAML reconciliation; `COMPLIANCE-001` independent mains-voltage review; `PRODUCT-TRIAC-001` catalog-policy reclassification to advanced / manual-warning; `PRODUCT-TRIAC-002` product YAML / catalog entry rework; `WF-TRIAC-001` advanced / manual-warning WebFlash exposure; `RELEASE-TRIAC-001` advanced-channel build / release artifact; `WF-IMPORT-TRIAC-001` advanced / manual artifact import). Documentation only and explicitly **does not**: edit `config/hardware-catalog.json`, `config/product-catalog.json`, `config/webflash-builds.json`, or `config/webflash-compatibility.json`; add or change `schematic_file` for `S360-320`; flip `S360-320` `schematic_status` from `cataloged_unverified`; mark `S360-320` `verified`; mark the pin map confirmed; mark `packages/expansions/fan_triac.yaml` `confirmed-ok` (its status stays `package-yaml-pending` / `needs-package-reconciliation`); remove the BLOCKED / UNVERIFIED banner or the mains-voltage / qualified-electrician warnings from `packages/expansions/fan_triac.yaml`; edit any package YAML (`packages/expansions/fan_triac.yaml` stays unchanged); edit any product YAML (`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml` stays unchanged); edit any WebFlash wrapper (`products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml` stays unchanged); edit the curated artifact index `docs/hardware/artifacts/S360-320-R4.md`; edit the schematic PDF `docs/hardware/schematics/S360-320-R4.pdf` (byte-identical to HW-ASSETS-003 commit); resolve the `TRI_GPIO*` / `ESP_GPIO*` naming reconciliation; resolve the Core-side source ESP32 GPIO question for `TRI_GPIO1` / `TRI_GPIO2`; resolve the AC LINE `J1` 3-pin function; perform any bench / silkscreen / real-load measurement; unblock FanTRIAC under HW-005 (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`); clear COMPLIANCE-001 for `S360-320` or `S360-400` (compliance status is owned by `docs/compliance/mains-voltage-uk-eu-assessment.md`); claim that FanTRIAC is compliance-certified; promote `S360-320` to `preview` / `stable` / `production`; add a `FanTRIAC` token to any Release-One or preview config string; add a `FanTRIAC`-bearing entry to `config/webflash-builds.json`; add FanTRIAC to `release_one_required_configs` / REQUIRED_CONFIGS; add FanTRIAC to any kit / default onboarding flow; make FanTRIAC recommended; generate firmware; create a GitHub Release or tag; perform a WebFlash import; change Release-One (`Ceiling-POE-VentIQ-RoomIQ`, `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag `v1.0.0`); change the LED preview path (`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`, `channel: preview`); resolve the Core J10 vs RoomIQ J6 pin-order open question; resolve the systemic Core abstract-bus mismatch (`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3). Adds no edits to `config/*`, `products/*`, `products/webflash/*`, `packages/*`, `scripts/*`, `tests/*`, `components/*`, `include/*`, `.github/workflows/*`, `manifest.json`, or `firmware/sources.json`. Cross-linked from `docs/hardware/board-readiness-matrix.md` (`S360-320` evidence-axis row, `S360-320` productization-axis row, `S360-320` board-by-board notes, follow-up-PR-sequence item #4), `docs/hardware/remaining-board-documentation-audit.md` (Sense360 TRIAC (`S360-320`) decision-table row + audit-doc bullet), `docs/hardware/firmware-package-mapping-audit.md` (FanTRIAC placeholder GPIOs schematic-evidence list), and `docs/product-availability-taxonomy.md` (`S360-320 Sense360 TRIAC` snapshot row). | Keep. |
| `docs/hardware/s360-311-r4-pwm.md` (HW-PINMAP-311) | `current` | HW-PINMAP-311 per-board pin / package mapping audit doc for `S360-311-R4` Sense360 PWM. Records the audit as **`partial — schematic evidence available; package reconciliation pending`**: the module-side schematic PDF `docs/hardware/schematics/S360-311-R4.pdf` and the curated artifact index `docs/hardware/artifacts/S360-311-R4.md` are both committed under HW-ASSETS-003, but the standalone schematic-backed reference doc, the pin-map reconciliation, and the package YAML reconciliation are not produced by this PR. Consumes the HW-ASSETS-003 artifact index without rewriting it. Inventories the current committed evidence (committed module-side schematic PDF; curated artifact index; Core-side `J6` 13-pin connector capture in `docs/hardware/s360-100-r4-core.md` §J6 — `+5V` / `GND` / `TachIO` / `TachPMW1..4` / `Pul_Cou1..4`, pin order **verify** against silkscreen per Open Question #9; Core-side `Fan / driver outputs` showing `TachPMW*` / `Pul_Cou*` driven by SX1509 expander, `TachIO` direct from ESP32 `IO16`; SX1509 channel map in `packages/expansions/gpio_expander_sx1509.yaml` channels 0–3 fan PWM, 4–7 tach; single-channel firmware package `packages/expansions/fan_pwm.yaml` with `fan_pwm_pin: ${fan_pwm_pin}` / `fan_tach_pin: ${fan_tach_pin}` inherited from parent Core package; legacy four-channel firmware package `packages/expansions/sense360_fan_pwm.yaml` used only by legacy-compatible `products/sense360-fan-pwm.yaml`; `FanPWM` token reservation in `config/webflash-compatibility.json` `canonical_modules` subject to the fan-driver `max-one-of` rule; existing classifications in `docs/hardware/board-readiness-matrix.md`, `docs/hardware/remaining-board-documentation-audit.md`, `docs/hardware/firmware-package-mapping-audit.md`, `docs/product-availability-taxonomy.md`, `docs/hardware/hardware-artifact-policy.md`). Records the schematic-vs-package mapping disagreement as **unresolved by this PR**: `packages/hardware/sense360_core_ceiling.yaml` binds `fan_pwm_pin: ${expansion_gpio1}` (= `GPIO5`) and `fan_tach_pin: ${expansion_gpio2}` (= `GPIO6`); `packages/hardware/sense360_core.yaml` binds `expansion_gpio1` / `expansion_gpio2` to `GPIO4` / `GPIO5`; the verified Core schematic routes `TachPMW1..4` / `Pul_Cou1..4` through the SX1509 expander (channels 0–3 / 4–7), not directly via ESP32 expansion GPIOs, and the direct-ESP32 `TachIO` net is on `IO16` (not `GPIO5` / `GPIO6`). Resolution belongs to the systemic Core abstract-bus rebind owned by `docs/release-one-hardware-audit.md` Required follow-ups #2 / #3 plus a future evidence-bearing HW-PINMAP-311-FOLLOWUP, not to this PR. Records the UART-on-`J3`-pins-11/12 question as **unresolved by this PR**: the module-side `J3` capture labels pins 11 / 12 as `UART_RX` / `UART_TX` routed on-board to the module-side Nextion `J6` 4-pin connector; the Core-side `J6` capture in `docs/hardware/s360-100-r4-core.md` §J6 does not list any UART pins on the 13-pin connector. Records the `"NINE 4pin FANs"` schematic section-title question as **unresolved by this PR** (four 4-pin fan output connectors `J1` / `J2` / `J4` / `J5` visible; title says "NINE"). Records the single-channel-vs-four-channel canonical-abstraction decision as **unresolved by this PR** (`fan_pwm.yaml` binds one channel; the board exposes four fan outputs; legacy `sense360_fan_pwm.yaml` binds four with direct ESP32 GPIO mappings that also disagree with the schematic). Lists missing evidence in full: bench verification (PWM / tach / `TachIO` waveforms), silkscreen verification of `J6` 1-to-13 / `J3` 1-to-13 pin orders, harness verification (13-pin Core ↔ module cable inspection), KiCad source / KiCad PCB / project metadata, BOM, CPL, gerbers, drill files, STEP, board images, tach waveform verification, operator validation, standalone schematic-backed reference doc (`HW-PINMAP-311-FOLLOWUP`). Defines the follow-up PR sequence (HW-PINMAP-311-FOLLOWUP standalone schematic-backed reference doc + pin-map reconciliation; separate JSON PR for `S360-311` `schematic_status` promotion; PACKAGE-GAP-001 FanPWM slice for package YAML reconciliation; PRODUCT-GAP-001 FanPWM slice for product YAML if/when decided; WEBFLASH-GAP-001 / RELEASE-GAP-001 / WF-IMPORT-GAP-001 FanPWM slice for wrapper + build + release + import; stable promotion goes through the 17-row `docs/preview-to-stable-promotion-gates.md` gate). Documentation only and explicitly **does not**: edit `config/hardware-catalog.json`, `config/product-catalog.json`, `config/webflash-builds.json`, or `config/webflash-compatibility.json`; add or change `schematic_file` for `S360-311`; flip `S360-311` `schematic_status` from `cataloged_unverified`; mark `S360-311` `verified`; mark the pin map confirmed; mark `packages/expansions/fan_pwm.yaml` `confirmed-ok`; edit any package YAML (`packages/expansions/fan_pwm.yaml`, `packages/expansions/sense360_fan_pwm.yaml`, `packages/expansions/gpio_expander_sx1509.yaml`, `packages/hardware/sense360_core_ceiling.yaml`, `packages/hardware/sense360_core.yaml` all stay unchanged); edit the curated artifact index `docs/hardware/artifacts/S360-311-R4.md`; edit the schematic PDF `docs/hardware/schematics/S360-311-R4.pdf` (byte-identical to HW-ASSETS-003 commit); resolve the SX1509-channel vs direct-ESP32-GPIO mapping disagreement; resolve the UART-on-`J3`-pins-11/12 routing question; resolve the `"NINE 4pin FANs"` section-title question; resolve the single-channel-vs-four-channel canonical-abstraction decision; add a product YAML; add a WebFlash wrapper; add a build-matrix entry; generate firmware; create a GitHub Release or tag; perform a WebFlash import; promote `S360-311` to `preview` / `stable` / `production`; add a `FanPWM` token to any Release-One or preview config string; change Release-One (`Ceiling-POE-VentIQ-RoomIQ`, `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag `v1.0.0`); change the LED preview path (`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`, `channel: preview`); unblock FanTRIAC (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`); change the mains-voltage compliance status for `S360-320` or `S360-400` (owned by COMPLIANCE-001); resolve the Core J10 vs RoomIQ J6 pin-order open question; resolve the systemic Core abstract-bus mismatch (`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3). Adds no edits to `config/*`, `products/*`, `products/webflash/*`, `packages/*`, `scripts/*`, `tests/*`, `components/*`, `include/*`, or `.github/workflows/*`. Cross-linked from `docs/hardware/board-readiness-matrix.md` (`S360-311` evidence-axis row, `S360-311` board-by-board notes, follow-up-PR-sequence item #2, Missing / unfinished boards `S360-311` bullet, See-also per-board reference docs list), `docs/hardware/remaining-board-documentation-audit.md` (Sense360 PWM (`S360-311`) audit-doc bullet), `docs/hardware/firmware-package-mapping-audit.md` (See also entry recording the FanPWM SX1509-vs-direct-GPIO reconciliation as deferred), and `docs/product-availability-taxonomy.md` (`S360-311 Sense360 PWM` snapshot row). | Keep. |
| `docs/hardware/s360-312-r4-dac.md` (HW-PINMAP-312) | `current` | HW-PINMAP-312 per-board pin / package mapping audit doc for `S360-312-R4` Sense360 DAC. Records the audit as **`partial — schematic evidence available; package reconciliation pending`**: the module-side schematic PDF `docs/hardware/schematics/S360-312-R4.pdf` and the curated artifact index `docs/hardware/artifacts/S360-312-R4.md` are both committed under HW-ASSETS-003, but the standalone schematic-backed reference doc, the pin-map reconciliation, and the package YAML reconciliation are not produced by this PR. Consumes the HW-ASSETS-003 artifact index without rewriting it. Inventories the current committed evidence (committed module-side schematic PDF; curated artifact index; Core-side `J7` 6-pin connector capture in `docs/hardware/s360-100-r4-core.md` §J7 — `+5V` / `I2C_SDA` / `I2C_SCL` / `UART_RX` / `UART_TX` / `GND`, no `verify` flag on the pin order; Core-side I²C bus capture showing `I2C_SDA` at ESP32 `IO48` with `R22 10 kΩ` pull-up and `I2C_SCL` at `IO45` with `R21 10 kΩ` pull-up; Core-side UART0 capture showing `TXD0` / `RXD0` ↔ `UART_TX` / `UART_RX` and "also used as boot log on USB"; dual-channel firmware package `packages/expansions/fan_gp8403.yaml` with `gp8403.i2c_id: ${fan_dac_i2c_id}` / `gp8403.address: ${fan_dac_address}` / `gp8403.voltage: ${fan_dac_voltage_mode}` and two `fan` speed entities; `FanDAC` token reservation in `config/webflash-compatibility.json` `canonical_modules` subject to the fan-driver `max-one-of` rule **and** the explicit `FanDAC` ↔ `AirIQ` mutex `rules.fandac_conflicts_with_airiq: true`; existing classifications in `docs/hardware/board-readiness-matrix.md`, `docs/hardware/remaining-board-documentation-audit.md`, `docs/hardware/firmware-package-mapping-audit.md`, `docs/product-availability-taxonomy.md`, `docs/hardware/hardware-artifact-policy.md`). Records the Core `J7` pin-1 `+5V` vs Module `J1` pin-1 `+3.3V` voltage-rail discrepancy as **unresolved by this PR**: the module schematic additionally labels the on-board MT3608 boost-converter `IN` pin as `+3.3V` while boosting to `+12V` for the fan outputs. Records the DIP-switch I²C address-selection scheme on `SW1` / `SW2` (6-position each, 4.7 kΩ pull-ups `R3` / `R5` / `R7` for `IC1` `A0` / `A1` / `A2` and `R4` / `R6` / `R8` for `IC2` `2A0` / `2A1` / `2A2`) as **unresolved by this PR**: the schematic shows the hardware but not the DIP-position-to-address mapping; `fan_gp8403.yaml` `${fan_dac_address}` defaults to `0x58` with `0x59` as the only alternate, and the package addresses `IC1` only. Records the UART0-vs-Nextion arbitration question as **unresolved by this PR**: Module `J1` pins 4 / 5 carry `UART_RX` / `UART_TX` routed on-board to Module `J7` 4-pin Nextion connector; Core ties the same nets to ESP32 `TXD0` / `RXD0` (UART0), which is also the boot-log path on USB; the package YAML binds no `uart:` or `display:` component on this pair. Records the stale header-comment block in `packages/expansions/fan_gp8403.yaml` lines 13–18 (`Pin 4 (SDA) → GPIO39`, `Pin 5 (SCL) → GPIO40`, `Pin 2 (3.3V) → Power`, `Pin 1 (GND) → Ground`) as **disagreeing with both the Core `J7` capture and the Module `J1` capture** (which agree pin 1 is a power rail, pin 2 is I²C SDA, pin 4 is UART RX, pin 5 is UART TX, pin 6 is GND; Core I²C is `IO48` / `IO45`, not `GPIO39` / `GPIO40`) — the active YAML body's `${fan_dac_i2c_id}` / `${fan_dac_address}` substitutions are abstract-bus inheritance and do not depend on the stale comment, but the comment is still a documentation-side disagreement and is recorded as unresolved by this PR. Records the dual-DAC capacity (two `GP8403-TC50-EW` `IC1` / `IC2` driving two 3-pin Cloudlift outputs `J2` / `J3`) as broader than the singular hardware-catalog `description` ("0 to 10V analog fan driver, for example Cloudlift S12"); broadening the catalog row is a separate later PR, not in scope here. Records the `J2` / `J3` Cloudlift output silkscreen pin-1 question and the `fan_dac_voltage_mode` 5 V vs 10 V hardware-jumper identification as additional unresolved items. Lists missing evidence in full: bench verification (DAC outputs / I²C bus exchange / Nextion-vs-boot-log arbitration), silkscreen verification of Core `J7` / Module `J1` / `J2` / `J3` pin orders, harness verification (6-pin Core ↔ module cable inspection), I²C address-selection measurement, `fan_dac_voltage_mode` jumper identification, KiCad source / KiCad PCB / project metadata, BOM, CPL, gerbers, drill files, STEP, board images, operator validation, standalone schematic-backed reference doc (`HW-PINMAP-312-FOLLOWUP`). Defines the follow-up PR sequence (HW-PINMAP-312-FOLLOWUP standalone schematic-backed reference doc + pin-map reconciliation + voltage-rail / I²C address / UART-arbitration / Cloudlift pin-order / voltage-mode-jumper resolution; separate JSON PR for `S360-312` `schematic_status` promotion; PACKAGE-GAP-001 FanDAC slice for package YAML reconciliation including the stale header-comment block; PRODUCT-GAP-001 FanDAC slice for product YAML if/when decided; WEBFLASH-GAP-001 / RELEASE-GAP-001 / WF-IMPORT-GAP-001 FanDAC slice for wrapper + build + release + import; stable promotion goes through the 17-row `docs/preview-to-stable-promotion-gates.md` gate; HW-ASSETS-003-followup if manufacturing evidence later arrives). Documentation only and explicitly **does not**: edit `config/hardware-catalog.json`, `config/product-catalog.json`, `config/webflash-builds.json`, or `config/webflash-compatibility.json`; add or change `schematic_file` for `S360-312`; flip `S360-312` `schematic_status` from `cataloged_unverified`; mark `S360-312` `verified`; mark the pin map confirmed; mark `packages/expansions/fan_gp8403.yaml` `confirmed-ok`; edit any package YAML (`packages/expansions/fan_gp8403.yaml`, `packages/hardware/sense360_core_ceiling.yaml`, `packages/hardware/sense360_core.yaml` all stay unchanged); edit the curated artifact index `docs/hardware/artifacts/S360-312-R4.md`; edit the schematic PDF `docs/hardware/schematics/S360-312-R4.pdf` (byte-identical to HW-ASSETS-003 commit); edit `docs/hardware/s360-100-r4-core.md` (the Core `J7` capture stays as it is; the voltage-rail discrepancy is recorded here and is not rewritten on the Core-side doc); resolve the Core `J7` pin-1 `+5V` vs Module `J1` pin-1 `+3.3V` voltage-rail discrepancy; resolve the DIP-switch I²C address-selection scheme; resolve the UART0-vs-Nextion arbitration question; resolve the stale header-comment connector / GPIO claims in `packages/expansions/fan_gp8403.yaml`; resolve the `fan_dac_voltage_mode` 5 V vs 10 V hardware-jumper identification; resolve the `J2` / `J3` Cloudlift output silkscreen pin-1 question; broaden the hardware-catalog `description` to record the dual-DAC capacity; add a product YAML; add a WebFlash wrapper; add a build-matrix entry; generate firmware; create a GitHub Release or tag; perform a WebFlash import; promote `S360-312` to `preview` / `stable` / `production`; add a `FanDAC` token to any Release-One or preview config string; relax or change the `FanDAC` ↔ `AirIQ` mutex; relax or change the fan-driver `max-one-of` rule; change Release-One (`Ceiling-POE-VentIQ-RoomIQ`, `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag `v1.0.0`); change the LED preview path (`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`, `channel: preview`); unblock FanTRIAC (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`); change the mains-voltage compliance status for `S360-320` or `S360-400` (owned by COMPLIANCE-001); resolve the Core J10 vs RoomIQ J6 pin-order open question; resolve the systemic Core abstract-bus mismatch (`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3). Adds no edits to `config/*`, `products/*`, `products/webflash/*`, `packages/*`, `scripts/*`, `tests/*`, `components/*`, `include/*`, or `.github/workflows/*`. Cross-linked from `docs/hardware/board-readiness-matrix.md` (`S360-312` evidence-axis row, `S360-312` productization-axis row, `S360-312` board-by-board notes, follow-up-PR-sequence item #3, Missing / unfinished boards `S360-312` bullet), `docs/hardware/remaining-board-documentation-audit.md` (Sense360 DAC (`S360-312`) audit-doc bullet), `docs/hardware/firmware-package-mapping-audit.md` (See also entry recording the FanDAC pin / package reconciliation as out-of-scope for HW-009 today), and `docs/product-availability-taxonomy.md` (`S360-312 Sense360 DAC` snapshot row). | Keep. |
| `docs/hardware/s360-310-r4-relay.md` (HW-PINMAP-310 / HW-PINMAP-310-FOLLOWUP) | `current` | HW-PINMAP-310 per-board pin / package mapping audit doc for `S360-310-R4` Sense360 Relay. After **HW-PINMAP-310-FOLLOWUP** consumed the HW-ASSETS-310 schematic, the audit status is **`partial — schematic evidence available; package reconciliation pending`** (promoted from the original `pending — schematic/design evidence required`). The module-side schematic PDF `docs/hardware/schematics/S360-310-R4.pdf` and the curated artifact index `docs/hardware/artifacts/S360-310-R4.md` are both committed under HW-ASSETS-310 and consumed by this audit; the standalone per-board schematic-backed reference doc (in the `s360-200-r4-roomiq.md` / `s360-211-r4-ventiq.md` / `s360-300-r4-led.md` style), the silkscreen / harness / `K1` BOM / bench evidence, and the package YAML reconciliation are not produced by this PR. Inventories the current committed evidence (committed module-side schematic PDF; curated artifact index; Core-side `J4` 3-pin connector capture in `docs/hardware/s360-100-r4-core.md` §J4 — `+5V` / `Relay` / `GND`, drive `Relay` from ESP32 `IO3`; firmware package `packages/expansions/fan_relay.yaml` with default `fan_relay_pin: ${relay_pin}`; `FanRelay` token reservation in `config/webflash-compatibility.json` `canonical_modules` subject to the fan-driver `max-one-of` rule; existing classifications in `docs/hardware/board-readiness-matrix.md`, `docs/hardware/remaining-board-documentation-audit.md`, `docs/hardware/firmware-package-mapping-audit.md`, `docs/product-availability-taxonomy.md`, `docs/hardware/hardware-artifact-policy.md`). Records the schematic-backed module-side findings: `J2` 3-pin "From Core" connector with pins 1 / 2 / 3 = `+5V` / `Relay` / `GND` (net-by-net match to Core `J4`); `K1` mechanical relay; `Q1` MMBT3904 NPN low-side coil driver with `R1` 1 kΩ base series, `R2` 10 kΩ base pull-down, `D1` flyback diode across the coil; `J1` 3-pin "Inline Fan" load-side output; coil rail `+5V` with no on-board boost; no opto-isolator; no on-board indicator LED; no mains-side snubber; no relay part number / coil-voltage / contact-rating label visible. Records the `IO3` vs `GPIO4` vs `GPIO10` `relay_pin` disagreement as **unresolved by this PR**: the module schematic confirms the input topology but does not establish which Core-side ESP32 GPIO physically connects to the `Relay` net; the Core schematic places `Relay` on `IO3`; `packages/hardware/sense360_core_ceiling.yaml` binds `relay_pin: GPIO4` (HW-009 flags `IO4 = SEN0609_RX`); `packages/hardware/sense360_core.yaml` binds `relay_pin: GPIO10`; `packages/expansions/fan_relay.yaml` inherits whichever value the parent Core package binds via `${relay_pin}`. Resolution belongs to `CORE-ABSTRACT-BUS-001` (alias for `docs/release-one-hardware-audit.md` Required follow-ups #2 / #3), not to HW-PINMAP-310 or HW-PINMAP-310-FOLLOWUP. Lists missing evidence in full: module-side `J2` silkscreen pin-1 location; module-side `J1` silkscreen pin-1 location and NO / COM / NC mapping; Core-side `J4` silkscreen pin-1 location (paired with the broader Core silkscreen gate in `s360-100-r4-core.md` §S360-100-BENCH-001 status); `K1` BOM identity (part number, coil voltage, contact configuration, contact current / voltage / AC vs DC rating, isolation rating); whether `Q1` MMBT3904 SOA is adequate for the chosen `K1` coil current; Core-to-module 3-pin harness identity (conductor count, length, key / polarity at both ends, conductor-by-conductor mapping); bench / continuity / waveform evidence against a populated `S360-310-R4` + `S360-100-R4` pair; KiCad source / KiCad PCB / project metadata / CPL / gerbers / drill / STEP / board images / silkscreen photos / bench photos; standalone per-board schematic-backed reference doc rewrite. Defines the follow-up PR sequence (`CORE-ABSTRACT-BUS-001` resolves the `IO3` / `GPIO4` / `GPIO10` disagreement; separate JSON-only PR for `S360-310` `schematic_status` promotion after silkscreen / harness / BOM evidence lands; `PACKAGE-RELAY-001` / `PACKAGE-GAP-001` FanRelay slice for package YAML reconciliation; `PRODUCT-RELAY-001` for product YAML if/when decided; `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001` for wrapper + build + release + import; stable promotion goes through the 17-row `docs/preview-to-stable-promotion-gates.md` gate; HW-ASSETS-310-followup if manufacturing evidence later arrives). Carries an `HW-PINMAP-310-FOLLOWUP audit log` section that records (i) the 2026-05-18 schematic-backed reconciliation work this PR performs (status promotion + reconciliation findings + open-gap inventory) and (ii) the future docs-only re-checks of silkscreen / harness / BOM / bench / Core abstract-bus rebind evidence that must land before the audit can move off `partial — schematic evidence available; package reconciliation pending`. Documentation only and explicitly **does not**: edit `config/hardware-catalog.json`, `config/product-catalog.json`, `config/webflash-builds.json`, or `config/webflash-compatibility.json`; edit the committed schematic PDF under `docs/hardware/schematics/S360-310-R4.pdf` (stays byte-identical to the HW-ASSETS-310 commit); edit the curated artifact index `docs/hardware/artifacts/S360-310-R4.md` (its content is consumed by this audit, not rewritten); add or change `schematic_file` for `S360-310`; flip `S360-310` `schematic_status` from `cataloged_unverified`; mark `S360-310` `verified`; mark the pin map confirmed; mark `packages/expansions/fan_relay.yaml` `confirmed-ok`; edit any package YAML (`packages/expansions/fan_relay.yaml`, `packages/hardware/sense360_core_ceiling.yaml`, `packages/hardware/sense360_core.yaml` all stay unchanged); resolve the `IO3` vs `GPIO4` vs `GPIO10` `relay_pin` disagreement; add a product YAML; add a WebFlash wrapper; add a build-matrix entry; generate firmware; create a GitHub Release or tag; perform a WebFlash import; promote `S360-310` to `preview` / `stable` / `production`; add a `FanRelay` token to any Release-One or preview config string; change Release-One (`Ceiling-POE-VentIQ-RoomIQ`, `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag `v1.0.0`); change the LED preview path (`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`, `channel: preview`); unblock FanTRIAC (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`); change the mains-voltage compliance status for `S360-320` or `S360-400` (owned by COMPLIANCE-001); resolve the Core J10 vs RoomIQ J6 pin-order open question; resolve the systemic Core abstract-bus mismatch (`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3); claim that any bench / continuity / harness / silkscreen evidence exists; claim that any compliance evidence for a mains-switching FanRelay product exists. Adds no edits to `config/*`, `products/*`, `products/webflash/*`, `packages/*`, `scripts/*`, `tests/*`, `components/*`, `include/*`, or `.github/workflows/*`. Cross-linked from `docs/hardware/board-readiness-matrix.md` (`S360-310` evidence-axis row, `S360-310` board-by-board notes, follow-up-PR-sequence item #1, See-also per-board reference docs list), `docs/hardware/remaining-board-documentation-audit.md` (Sense360 Relay (`S360-310`) audit-doc bullet), `docs/hardware/package-readiness-matrix.md` (`fan_relay.yaml` row + §`fan_relay.yaml` / S360-310 detail), `docs/hardware/firmware-package-mapping-audit.md` (Release-One package stack `relay_pin: GPIO4` reconciliation note), `docs/product-availability-taxonomy.md` (`S360-310 Sense360 Relay` snapshot row), `docs/product-readiness-matrix.md` (`FanRelay / S360-310` row), `docs/webflash-exposure-readiness-matrix.md` (`Relay / S360-310 WebFlash posture` subsection), and `docs/release-artifact-readiness-matrix.md` (`Relay / S360-310 release posture` subsection). | Keep. |
| `docs/hardware/s360-400-r4-power.md` (HW-PINMAP-400 / HW-PINMAP-400-FOLLOWUP) | `current` | HW-PINMAP-400 per-board pin / package mapping audit doc for `S360-400-R4` Sense360 240v PSU. After **HW-PINMAP-400-FOLLOWUP** (this PR) consumed the HW-ASSETS-400 (PR #514) schematic, the audit status is **`partial — schematic evidence available; package reconciliation, BOM, silkscreen, creepage/clearance, and COMPLIANCE-001 pending`** (promoted from the original `pending — schematic/design evidence required`). The module-side schematic PDF `docs/hardware/schematics/S360-400-R4.pdf` and the curated artifact index `docs/hardware/artifacts/S360-400-R4.md` are both committed under HW-ASSETS-400 / PR #514 and consumed by this audit; the standalone per-board schematic-backed reference-doc rewrite (in the `s360-200-r4-roomiq.md` / `s360-211-r4-ventiq.md` / `s360-300-r4-led.md` style), the BOM cross-check, the silkscreen / connector-identity evidence, the PCB / creepage / clearance evidence, the bench / load / thermal / EMI evidence, and the COMPLIANCE-001 mains-voltage UK / EU sign-off are not produced by this PR. Inventories the current committed evidence (committed module-side schematic PDF; curated artifact index; firmware package `packages/hardware/power_240v.yaml` is a logical-power package with no GPIO binding; `PWR` token reservation in `config/webflash-compatibility.json` `canonical_power` with no `webflash_build_matrix: true` entry; existing classifications in `docs/hardware/board-readiness-matrix.md`, `docs/hardware/remaining-board-documentation-audit.md`, `docs/hardware/package-readiness-matrix.md`, `docs/hardware/firmware-package-mapping-audit.md`, `docs/product-availability-taxonomy.md`, `docs/hardware/hardware-artifact-policy.md`; COMPLIANCE-001 tracker at `docs/compliance/mains-voltage-uk-eu-assessment.md`). Records the schematic-backed module-side findings: 3-pin AC input `J1` with pins 1 / 2 / 3 = `LIVE` / `NEUTRAL` / `Earth_Protective`; mains-input protection network `F1` resettable polyfuse value `A250-1200` on the LIVE leg, MOV `RV1` value `10D391K` across the AC line, X-cap `C1` value `470nF` across the AC line in parallel with `RV1`; AC/DC converter `PS1` value `HLK-10M05` with pinout `AC(L)` / `AC(N)` / `-VO` / `+VO`; output filter bank `C5 100uF` / `C6 10u` / `C7 100n` / `C8 100uF` between `+VO` and `-VO` / `GND`; 2-pin output `J2` with pins 1 / 2 = `+5VP` / `GND`; four mounting holes `H1` / `H2` / `H3` / `H4` with no nets; no Y-class capacitors; no common-mode / differential-mode line-filter inductor; no secondary regulator; no on-board indicator LED; no thermal cutout / NTC inrush limiter; no I²C / UART / SPI / DAC / GPIO. Records the three-way AC/DC part-identity disagreement as **unresolved by this PR**: catalog `description: Mains to 5V using HLK-5M05.` (`config/hardware-catalog.json` line 109) vs package header `HLK-PM01 or similar` (`packages/hardware/power_240v.yaml` line 7) vs schematic-shown `PS1 = HLK-10M05`. Resolution is BOM-bound and belongs to `PACKAGE-POWER-400-001`, not to HW-PINMAP-400 or HW-PINMAP-400-FOLLOWUP. Lists missing evidence in full: BOM cross-check for `PS1` / `F1` / `RV1` / `C1` / `C5..C8` / `J1` / `J2`; module-side `J1` and `J2` silkscreen pin-1 location; `J1` mains-rated connector identity / current / voltage / approvals; `J2` low-voltage connector identity / current rating; `F1 A250-1200` polyfuse hold / trip / voltage rating; `RV1 10D391K` clamp voltage / energy rating; `C1 470nF` X-cap safety class X1 / X2; `C5..C8` voltage / dielectric / ESR; creepage / clearance between AC LINE / NEUTRAL / `Earth_Protective` / secondary `+5VP` / `GND`; Y-class capacitor presence-or-absence as designed; common-mode / differential-mode line-filter inductor absence as designed; integrated thermal protection in the `HLK-10M05` module; mounting-hole electrical bonding; bench / load / thermal / inrush / insulation / Hi-pot / earth-continuity / leakage / EMI / EMC measurements; integration path with Core `+5V` rail; harness identity if any cable is part of the assembly; KiCad source / KiCad PCB / project metadata / CPL / gerbers / drill / STEP / board images / silkscreen photos / bench photos; compliance test reports (LVD / EMC / RoHS / CE / UKCA / FCC / UL); standalone per-board schematic-backed reference-doc rewrite. Defines the follow-up PR sequence (`COMPLIANCE-001` `S360-400` slice resolves the mains-voltage UK / EU evidence checklist; separate JSON-only PR for `S360-400` `schematic_status` promotion after BOM + silkscreen evidence lands; `PACKAGE-POWER-400-001` / `PACKAGE-GAP-001` PWR slice for package YAML header / part-identity / rating reconciliation against the now-verified schematic and module BOM; `PRODUCT-POWER-400-001` for product YAML if/when decided; `WEBFLASH-POWER-400-001` / `RELEASE-POWER-400-001` / `WF-IMPORT-POWER-400-001` for wrapper + build + release + import; stable promotion goes through the 17-row `docs/preview-to-stable-promotion-gates.md` gate; HW-ASSETS-400-followup if manufacturing evidence later arrives). Carries an `HW-PINMAP-400-FOLLOWUP audit log` section that records (i) the 2026-05-19 schematic-backed reconciliation work this PR performs (status promotion + reconciliation findings + open-gap inventory) and (ii) the future docs-only re-checks of BOM / silkscreen / PCB / creepage / clearance / bench / load / thermal / EMI / compliance evidence that must land before the audit can move off `partial — schematic evidence available; package reconciliation, BOM, silkscreen, creepage/clearance, and COMPLIANCE-001 pending`. Documentation only and explicitly **does not**: edit `config/hardware-catalog.json`, `config/product-catalog.json`, `config/webflash-builds.json`, or `config/webflash-compatibility.json`; edit the committed schematic PDF under `docs/hardware/schematics/S360-400-R4.pdf` (stays byte-identical to the HW-ASSETS-400 / PR #514 commit); edit the curated artifact index `docs/hardware/artifacts/S360-400-R4.md` (its content is consumed by this audit, not rewritten); edit `docs/compliance/mains-voltage-uk-eu-assessment.md` (COMPLIANCE-001 unchanged); add or change `schematic_file` for `S360-400`; flip `S360-400` `schematic_status` from `cataloged_unverified`; mark `S360-400` `verified`; mark the rail / connector / safety map confirmed; mark `packages/hardware/power_240v.yaml` `confirmed-ok`; edit `packages/hardware/power_240v.yaml` at all (the stale `HLK-PM01 or similar` header at line 7, the `100-240V AC, 50/60Hz` / `5V DC, 2A (10W)` / `3000VAC` / protection claims at lines 7–10, and the recommended `1A` fusing line at line 15 are all preserved byte-for-byte — comment-only cleanup deferred to `PACKAGE-POWER-400-001` once BOM evidence lands); add a cross-link comment to `power_240v.yaml`; replace `HLK-PM01` with `HLK-10M05` in `power_240v.yaml`; resolve the three-way `HLK-5M05` / `HLK-PM01 or similar` / `HLK-10M05` AC/DC part-identity disagreement; add a product YAML; add a WebFlash wrapper; add a build-matrix entry; generate firmware; create a GitHub Release or tag; perform a WebFlash import; promote `S360-400` to `preview` / `stable` / `production`; add a `PWR` token to any Release-One or preview config string; change Release-One (`Ceiling-POE-VentIQ-RoomIQ`, `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag `v1.0.0`); change the LED preview path (`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`, `channel: preview`); unblock FanTRIAC (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`); clear `COMPLIANCE-001` for `S360-400` (or `S360-320`); change the `S360-410` PoE PSU status or its documented "schematic verification pending" caveat; change `REQUIRED_CONFIGS` or kits; resolve the systemic Core abstract-bus mismatch (`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3); claim that any bench / load / thermal / inrush / insulation / Hi-pot / earth-continuity / leakage / EMI / EMC evidence exists; claim that any compliance evidence for a mains-voltage `PWR`-bearing product exists. Makes no CE / UKCA / FCC / UL / LVD / EMC / RoHS claim and no standard or advanced / manual-warning WebFlash exposure approval. Adds no edits to `config/*`, `products/*`, `products/webflash/*`, `packages/*`, `scripts/*`, `tests/*`, `components/*`, `include/*`, `firmware/*`, `manifest.json`, `firmware/sources.json`, or `.github/workflows/*`. Cross-linked from `docs/hardware/board-readiness-matrix.md` (`S360-400` evidence-axis row, `S360-400` productization-axis row, `S360-400` Sense360 240v PSU board-by-board notes, follow-up-PR-sequence item #5), `docs/hardware/remaining-board-documentation-audit.md` (Sense360 240v PSU (`S360-400`) audit-doc bullet, row at line 106), `docs/hardware/package-readiness-matrix.md` (`power_240v.yaml` row + §`power_240v.yaml` / S360-400 detail), `docs/hardware/firmware-package-mapping-audit.md` (new `power_240v.yaml` AC/DC part-identity disagreement (S360-400) per-area finding), `docs/product-availability-taxonomy.md` (`S360-400 Sense360 240v PSU` snapshot row), `docs/product-readiness-matrix.md` (`PWR-240V / S360-400` row + subsection), `docs/webflash-exposure-readiness-matrix.md` (`PWR-240V / S360-400` exposure-table row and §`Power / S360-400 WebFlash posture` subsection), and `docs/release-artifact-readiness-matrix.md` (`PWR-240V / S360-400` release-table row and §`Power / S360-400 release posture` subsection). | Keep. |
| `docs/hardware/s360-200-r4-roomiq.md` (HW-007 cross-link refresh) | `current` | Existing RoomIQ hardware reference doc; HW-007 changes the `Schematic source` table to point at `[`schematics/S360-200-R4.pdf`](schematics/S360-200-R4.pdf)` and adds a one-line `HW-007 — PDF committed` admonition. The Core J10 vs RoomIQ J6 pin-order discrepancy remains an Open Question and is not resolved by HW-007. | Keep. |
| `docs/hardware/remaining-board-documentation-audit.md` (HW-007 ingest + HW-008 refresh) | `current` | HW-004 / HW-006 per-board documentation audit. HW-007 refreshed the AirIQ / VentIQ / LED decision-table and evidence rows to point at the newly committed PDFs and standalone docs, and added an `HW-007 schematic ingest` subsection. HW-008 then reclassified those rows from `cataloged-unverified` / `partially-documented` to `documented` (with `not-needed-for-release-one` retained for AirIQ and LED), updated the Release-One coverage summary (VentIQ moves to `documented`; PoE PSU stays `partially-documented`), and added an `HW-008 schematic-status refresh` subsection recording what HW-008 commits and what it does **not** change (no Release-One config / build matrix / artifact / lifecycle change; no FanTRIAC unblock; no LED Release-One promotion; no mains-compliance change). What remains unproven after HW-008: FanTRIAC (`S360-320`), Relay / PWM / DAC / 240v PSU / PoE PSU module-side schematics, Core J10 vs RoomIQ J6 pin order, `GPIO14` vs `IO38` LED_DATA discrepancy, `AirQ_Led` / `AirQ_Status_Led` reuse on AirIQ vs VentIQ, mains-voltage compliance for COMPLIANCE-001 boards. HW-009 adds the firmware-package-mapping classification on top: see `docs/hardware/firmware-package-mapping-audit.md`. | Keep. |
| `docs/hardware/firmware-package-mapping-audit.md` (HW-009 + HW-010 refresh) | `current` | HW-009 docs-only audit reconciling firmware package YAMLs against the now-`verified` HW-007 / HW-008 schematics (`S360-100`, `S360-200`, `S360-210`, `S360-211`, `S360-300`). Classifies each mapping using a six-label taxonomy (`confirmed-ok`, `needs-package-change`, `needs-doc-fix`, `needs-silkscreen/bench-verification`, `blocked`, `unknown`). HW-010 has since reclassified the LED_DATA / Sense360 LED row from `needs-package-change` (deferred) to `confirmed-ok` — the ceiling LED package now binds `led_data_pin: GPIO38`. The remaining rows are unchanged: Core J10 vs RoomIQ J6 pin-order discrepancy (`needs-silkscreen/bench-verification`); VentIQ J9 `AirQ_Led` / `AirQ_Status_Led` reuse (`confirmed-ok` with legacy-naming caveat — package does not bind those nets); AirIQ J9 `AirQ_Led` / `AirQ_Status_Led` reuse (`confirmed-ok` with legacy-naming caveat); VentIQ legacy package filename `airiq_bathroom_base.yaml` (`confirmed-ok`, retained per WebFlash contract §6); Release-One product YAML package stack systemic Core abstract-bus mismatch (`needs-package-change` — explicit out-of-scope; owned by `release-one-hardware-audit.md` Required follow-ups #2 / #3); FanTRIAC `GPIO5` / `GPIO6` placeholders (`blocked` under HW-005; additionally gated by COMPLIANCE-001). Records recommended follow-up PRs (HW-010 LED pin fix — **resolved**; J10/J6 silkscreen reconciliation; `AirQ_*` indicator-line bench verification; systemic Core abstract-bus rebind; HW-005 remains blocked separately). HW-009 itself was documentation only. HW-010 is the scoped one-package follow-up: it edits `packages/hardware/led_ring_ceiling.yaml` (`GPIO14` → `GPIO38`) and adds `tests/test_led_package_mapping.py`; it does **not** edit any product YAML, WebFlash wrapper, JSON config, workflow, script, component, or include; it does **not** rename any package filename, change any hardware-catalog `schematic_status`, change any product-catalog lifecycle status, add a `LED` token to the Release-One config string, add a WebFlash LED build, add an LED product-catalog entry, or change the FanTRIAC HW-005 blocked status. Preserves the Release-One config string `Ceiling-POE-VentIQ-RoomIQ`, the Release-One artifact name `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, the WebFlash build matrix, the WebFlash compatibility snapshot, and the mains-voltage compliance status for `S360-400` and `S360-320`. The wall LED package (`led_ring_wall.yaml`, `GPIO48`) and the legacy S3 Core package (`sense360_core_ceiling_s3.yaml`, `GPIO14`) are intentionally not changed by HW-010 — neither has Core-side schematic evidence proving the same `LED_DATA` path; both remain documented as unresolved. Validated by the existing test suite (`tests/test_hardware_catalog.py`, `tests/test_product_catalog.py`, `tests/test_product_catalog_consistency.py`, `tests/validate_webflash_builds.py`, `tests/test_webflash_compatibility.py`, `tests/test_webflash_artifact_naming.py`, `tests/test_validate_webflash_release_notes.py`, `tests/test_generate_webflash_release_notes.py`, `tests/test_product_substitutions.py`, `tests/test_release_one_entity_names.py`, `tests/validate_configs.py`, `scripts/validate_product_catalog_consistency.py`) plus the new `tests/test_led_package_mapping.py`. | Keep. |
| `packages/hardware/led_ring_ceiling.yaml` (HW-010 pin fix) | `current` | Ceiling LED ring package. HW-010 changes `led_data_pin` from `GPIO14` to `GPIO38` so the package matches the verified `S360-100-R4` schematic (`IO38 = LED_DATA → U2A 74LVC1G07 buffer → R8 330 Ω → J3 → S360-300 J1`). Pin substitution is consumed by `esp32_rmt_led_strip` via `pin: ${led_data_pin}`; the rest of the package (LED count, RGB order, chipset, effects, brightness / night-mode controls, SKU text sensor) is unchanged. Filename retained per WebFlash contract §6 (legacy package filenames are public API). Consumers are `legacy-compatible` products only (`sense360-core-ceiling.yaml`, `sense360-core-ceiling-bathroom.yaml`, `sense360-core-ceiling-presence.yaml`); Release-One does **not** `!include` this package and HW-010 does not add it. | Keep. |
| `tests/test_led_package_mapping.py` | `current` | HW-010 stdlib `unittest` validator for the ceiling LED package pin mapping and PRODUCT-009 stable-channel LED exclusion. Locks in: `packages/hardware/led_ring_ceiling.yaml` contains `led_data_pin: GPIO38` and no `GPIO14`; the Release-One YAML `products/sense360-ceiling-poe-ventiq-roomiq.yaml` does not `!include` `led_ring_ceiling.yaml`; the Release-One build `Ceiling-POE-VentIQ-RoomIQ` remains in `config/webflash-builds.json` on `channel: stable` with no `LED` token in its `config_string` or `artifact_name`; every `stable`-channel build is LED-less; every LED-bearing build is non-stable and points at the LED WebFlash wrapper `products/webflash/ceiling-poe-ventiq-roomiq-led.yaml`; the FanTRIAC entry `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` in `config/product-catalog.json` remains `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`; the Release-One catalog entry keeps `LED` and `FanTRIAC` in `blocked_modules`. PRODUCT-009 re-scoped the previous "no LED token in any build" assertion to the stable channel and added the LED-preview-shape assertions. Read-only file-content checks; no ESPHome compile required. | Keep. |
| `products/sense360-ceiling-poe-ventiq-roomiq-led.yaml` (PRODUCT-006) | `current` | LED-bearing sibling-candidate product YAML for the WebFlash config string `Ceiling-POE-VentIQ-RoomIQ-LED`. Same Core ceiling + PoE PSU + VentIQ + RoomIQ package stack as the Release-One YAML `products/sense360-ceiling-poe-ventiq-roomiq.yaml`, plus `packages/hardware/led_ring_ceiling.yaml` (which binds `led_data_pin: GPIO38` after HW-010). Differs from Release-One only in: `device_name` (`s360-ceil-poe-ventiq-rm-led`), `friendly_name` (`Sense360 Ceiling Bathroom LED`), `fallback_ssid` (`S360 VentIQ RoomIQ LED`), and the `WebFlash Config` text-sensor return value (`Ceiling-POE-VentIQ-RoomIQ-LED`). FanTRIAC is intentionally omitted (HW-005 blocker unchanged). PRODUCT-006 added the YAML plus the **minimum** `status: compile-only` entry in `config/product-catalog.json` needed to satisfy the existing PRODUCT-002 enumeration gate at `tests/test_product_catalog.py::test_every_top_level_product_yaml_is_in_catalog`. **PRODUCT-008 has since added the WebFlash wrapper `products/webflash/ceiling-poe-ventiq-roomiq-led.yaml` and promoted the catalog entry from `compile-only` to `preview` with `webflash_build_matrix: false`, `hardware_status: verified-led-candidate`, and a `webflash_wrapper` pointer.** PRODUCT-006/008 do **not** edit the Release-One YAML; do **not** add a `config/webflash-builds.json` build (deferred to PRODUCT-009); do **not** declare an `artifact_name` / `version` / `channel`; do **not** generate or release any firmware; do **not** change `tests/test_led_package_mapping.py` (the Release-One YAML still does not `!include` the LED package, no WebFlash build carries an `LED` token, and FanTRIAC stays `status: blocked` / `blocker: HW-005` / `webflash_build_matrix: false`); do **not** change `config/webflash-compatibility.json`, `config/hardware-catalog.json`, the Release-One config string, the Release-One artifact name, the WebFlash build matrix, or the mains-voltage compliance status for `S360-400` / `S360-320`. PRODUCT-007 remains a no-op absorbed by PRODUCT-006; next active work is PRODUCT-009 (build-matrix entry + release proof). Decision-doc record: `docs/product-led-preview-decision.md` (PRODUCT-005, Option A → C). Validated by the existing surface: `tests/validate_configs.py`, `tests/test_product_substitutions.py`, `tests/test_product_catalog.py`, `tests/test_product_catalog_consistency.py`, `tests/test_led_package_mapping.py`, plus `scripts/validate_product_catalog_consistency.py`. | Keep. |
| `products/webflash/ceiling-poe-ventiq-roomiq-led.yaml` (PRODUCT-008 / PRODUCT-009) | `current` | LED-bearing **preview** WebFlash wrapper for the config string `Ceiling-POE-VentIQ-RoomIQ-LED`. Thin wrapper that `!include`s the canonical product YAML `products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`, in the same pattern as the Release-One wrapper `products/webflash/ceiling-poe-ventiq-roomiq.yaml`. Basename (`ceiling-poe-ventiq-roomiq-led`) equals the lower-cased config string per the validator rule in `scripts/validate_product_catalog_consistency.py`. Referenced both by the catalog entry's `webflash_wrapper` field (PRODUCT-008) and by the new LED preview build entry in `config/webflash-builds.json` (PRODUCT-009) as the build's `product_yaml`. After PRODUCT-009 the LED preview build declares `channel: preview`, `version: 1.0.0`, `artifact_name: Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`, `chip_family: ESP32-S3`. RELEASE-005 records the corresponding build / release proof in `docs/webflash-release-proof.md` (tag `v1.0.0-led-preview`, run `25918422743`, artifact built and attached at 1,135,904 bytes; SHA256 `93310d2cbc27355e399f36a232336b6b9075dacfc178d603c7a92aa1089182d3`). **NOT** Release-One stable (Release-One stays `Ceiling-POE-VentIQ-RoomIQ`, LED-less, on `stable`); **NOT** yet imported or published by WebFlash (WebFlash-side ingest, sign, manifest, and publish are owned by the follow-up `WF-LED-001` PR in the WebFlash repo). FanTRIAC stays blocked under HW-005. Decision-doc record: `docs/product-led-preview-decision.md` (PRODUCT-005, Option C → D landed via PRODUCT-008 / PRODUCT-009; LED-preview build / release proof recorded by RELEASE-005). | Keep. |
| `docs/hardware-catalog.md` (HW-007 + HW-008 cross-link refresh) | `current` | Hardware catalog naming source-of-truth. HW-007 expanded the "Verified schematics currently available" section from two boards to five (Core, RoomIQ, AirIQ, VentIQ, LED) with links to the PDFs under `docs/hardware/schematics/` and the standalone per-board docs. HW-008 then rewrote the HW-007 / HW-008 ingest paragraph to record that the machine-readable JSON has now been refreshed (the five SKUs are `schematic_status: verified` with `schematic_file` paths under `docs/hardware/schematics/`), kept the six unverified SKUs explicit, and reiterated the guardrails: verified schematic evidence is not WebFlash-shippability, not Release-One inclusion, not FanTRIAC unblock, not mains compliance. No changes to the canonical naming table, naming rules, or `old_name` entries. | Keep. |
| `docs/release-one-hardware-audit.md` (HW-007 cross-link refresh) | `current` | Release-One hardware audit; HW-007 refreshes the `Source hardware references` table to add rows for AirIQ / VentIQ / LED with pointers to the committed PDFs and new standalone docs. The VentIQ "schematic verification pending" caveat was retained at HW-007 time and has since been retired by HW-008. FanTRIAC findings, the HW-005 missing-evidence checklist, the timing constraint, the re-verification record, and the LED policy section are all unchanged. | Keep. |
| `config/hardware-catalog.json` (HW-008 schematic_status refresh) | `current` | HW-008 aligns the machine-readable hardware catalog with the module-side schematic PDFs HW-007 committed under `docs/hardware/schematics/`. Five rows flip to `schematic_status: verified` with `schematic_file` paths under `docs/hardware/schematics/`: `S360-100` (Core), `S360-200` (RoomIQ), `S360-210` (AirIQ), `S360-211` (VentIQ), `S360-300` (LED). The remaining six rows (`S360-310` Relay, `S360-311` PWM, `S360-312` DAC, `S360-320` TRIAC, `S360-400` 240v PSU, `S360-410` PoE PSU) stay `cataloged_unverified`. HW-008 is JSON + doc cross-link only: it does **not** edit any product YAML, WebFlash wrapper, package YAML, workflow, component, header, or script; it does **not** change the Release-One config string `Ceiling-POE-VentIQ-RoomIQ`, the Release-One artifact name, the WebFlash build matrix, the WebFlash compatibility snapshot, or any product-catalog lifecycle status; it does **not** unblock FanTRIAC (HW-005 still applies; `S360-320` stays `cataloged_unverified`); it does **not** add a `LED` token to the Release-One config string (`S360-300` flips to `verified` but Sense360 LED stays excluded from Release-One); it does **not** clear the mains-voltage compliance gate (`S360-400` stays `cataloged_unverified` under COMPLIANCE-001); it does **not** resolve the Core J10 vs RoomIQ J6 pin-order discrepancy or the `GPIO14` (package) vs `IO38` (schematic) `LED_DATA` discrepancy. Validated by the new `tests/test_hardware_catalog.py`. | Keep. |
| `tests/test_hardware_catalog.py` | `current` | HW-008 stdlib `unittest` validator for `config/hardware-catalog.json`. Locks in: JSON parses; every entry has `sku` / `friendly_name` / `schematic_status`; every status is one of `verified` / `cataloged_unverified`; every `verified` entry has a `schematic_file`; every `schematic_file` path exists on disk under the repo root; `S360-100`, `S360-200`, `S360-210`, `S360-211`, `S360-300` are `verified`; `S360-320` remains not `verified` (HW-005 still blocked); `S360-400` remains not `verified` (COMPLIANCE-001 still applies); entries that are not `verified` may omit `schematic_file`. Read-only; no firmware / product / workflow change. | Keep. |
| `docs/webflash-contract.md` | `current` | Canonical WebFlash artifact/grammar/token contract. | Keep. |
| `docs/webflash-ci-alignment.md` | `current` | CI ↔ WebFlash alignment record. | Keep. |
| `docs/webflash-release-handoff.md` | `current` | Release-handoff record. | Keep. |
| `docs/webflash-release-proof.md` | `current` | ESP-006 / ESP-007 Release-One proof record (run `25763009641`) plus the LED preview proof section seeded by RELEASE-003 and backfilled by RELEASE-005. RELEASE-003 originally landed the "LED preview release proof (RELEASE-003)" section with a pending-proof table, operator runbook, and proof checklist whose dynamic fields (tag, run URL, asset size, SHA256, validator/asset-check pass states) were marked `pending`. **RELEASE-005 replaced the `pending` values with the real recorded values from the successful prerelease run:** GitHub Release <https://github.com/sense360store/esphome-public/releases/tag/v1.0.0-led-preview> (tag `v1.0.0-led-preview`, title `Sense360 LED Preview Firmware v1.0.0`, `prerelease: true`); workflow `Build & Release Firmware` run [`25918422743`](https://github.com/sense360store/esphome-public/actions/runs/25918422743) (event `release`, git SHA `4493e0c9b3914d5dfcf41f71b4129cf23cda75d2`); firmware asset `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` (1,135,904 bytes; SHA256 `93310d2cbc27355e399f36a232336b6b9075dacfc178d603c7a92aa1089182d3`); uploaded asset set `.bin`, `checksums-sha256.txt`, `checksums-md5.txt`, `manifest.json`; release-body validation passed; release-asset assertion passed; WebFlash-import source URL recorded; checklist boxes ticked; status flipped from "pending — RELEASE-003 not yet proven" to "proven — RELEASE-005 records the LED preview prerelease proof; ready for WebFlash import planning". A new "What RELEASE-005 does NOT do" guardrail block sits alongside the original RELEASE-003 guardrails: RELEASE-005 is documentation-only — it does **not** generate firmware, modify any release asset, change the artifact filename / version / channel, promote `Ceiling-POE-VentIQ-RoomIQ-LED` to `production` / `stable`, add `LED` to stable Release-One (`Ceiling-POE-VentIQ-RoomIQ`, `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag `v1.0.0`), import into WebFlash (owned by the follow-up `WF-LED-001` PR in the WebFlash repo), unblock FanTRIAC (HW-005 stays open; `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `blocked`; the LED preview catalog entry still carries `blocked_modules: ["FanTRIAC"]`), or modify any `config/*`, `products/*`, `products/webflash/*`, `packages/*`, `.github/workflows/*`, `scripts/*`, `tests/*`, `components/*`, or `include/*` file. Cross-linked from `docs/product-led-preview-decision.md` (PRODUCT-009 outstanding-proof paragraph now reads "recorded by RELEASE-005") and `docs/product-onboarding.md` (LED guardrail bullet). | Keep. |
| `docs/installation.md` | `current` | Manual/custom install path, pinned to `Ceiling-POE-VentIQ-RoomIQ`. Contains legacy Mini snippet (see "Legacy docs/examples"). | Keep; tweak the Mini snippet in CLEANUP-005. |
| `docs/product-matrix.md` | `current` | Frames `Ceiling-POE-VentIQ-RoomIQ` as the Release-One config but still includes a `Bathroom Pro` row at line 357 and "Bathroom Pro (additional)" header at line 366. | Reword in CLEANUP-003. |
| `docs/hardware-catalog.md` | `current` | Maps `Sense360 LED` (canonical) / `LED Ring` (old_name), and `Sense360 VentIQ` (canonical) / `Bathroom Pro` (old_name). | Keep. |
| `docs/manual-user-walkthrough.md` | `current` | Explicitly states "Sense360 LED is excluded from Release-One firmware." | Keep. |
| `docs/configuration.md` | `current` | Customer snippets pin `ref: v1.0.0`. Mini AirIQ/Presence variants described as "Product Variants" without a Release-One pointer. | Keep; add a Release-One pointer in CLEANUP-005. |
| `docs/development.md` | `current` | Lists Mini variants as locally testable; legacy-compatible. | Keep. |
| `docs/repo-structure-audit.md` | `current` | Companion classification doc (ESP-009 / ESP-010); already flags `docs/*.html` as "audit follow-up". | Keep. |
| `README.md` | `current` | Header, Release-One section, WebFlash taxonomy, FanTRIAC-excluded callout. | Keep. |
| `CHANGELOG.md` | `current` (with one `stale` paragraph) | The `Unreleased / Changed` REL-001 bullet is correct. The `Unreleased / Added` "WebFlash compatibility contract" bullet at lines 25–34 still names `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` as the release-one config, contradicting REL-001 above it. | Record only — do **not** fix in this PR. Defer to CLEANUP-002. |
| `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml` | `blocked-reference` | FanTRIAC product YAML; not in build matrix; retained per HW-005. | Keep. |
| `products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml` | `blocked-reference` | FanTRIAC WebFlash wrapper; retained per HW-005. | Keep. |
| `packages/expansions/fan_triac.yaml` | `blocked-reference` | FanTRIAC driver package, BLOCKED / UNVERIFIED banner. | Keep. |
| `config/hardware-catalog.json` (Sense360 TRIAC row) | `blocked-reference` | Cataloged row for S360-320 (`old_name: TRIAC_Board`); retained. | Keep. |
| FanTRIAC explainer paragraphs in `README.md`, `docs/release-one.md`, `docs/release-one-hardware-audit.md`, `docs/webflash-contract.md`, `docs/webflash-ci-alignment.md`, `docs/webflash-release-handoff.md`, `docs/product-matrix.md`, `docs/installation.md` | `blocked-reference` | Explicitly call FanTRIAC excluded / blocked. | Keep. |
| `products/sense360-core-*.yaml` (15 files: c-poe, c-pwr, c-usb, v-c-poe, v-c-pwr, v-c-usb, v-w-poe, v-w-pwr, v-w-usb, w-poe, w-pwr, w-usb, ceiling, ceiling-bathroom, ceiling-presence, voice-ceiling, voice-wall, wall, wall-presence) | `legacy-compatible` | Pre-WebFlash product YAMLs; still referenced by `ci-validate-configs.yml` matrix discovery and `docs/development.md`. Inline `ref: v2.2.0` / `ref: v3.0.0` comments are stale (lines 21, 24, 26, 28, 29, 103). | Keep YAMLs. Defer doc-comment fix to CLEANUP-002. |
| `products/sense360-mini-*.yaml` (10 files) | `legacy-compatible` | Pre-WebFlash Mini product YAMLs; still referenced by `ci-validate-configs.yml` and `docs/development.md`. `ref: v3.0.0` comments at lines 145, 258, 358, 474 are stale. | Keep YAMLs. Defer doc-comment fix to CLEANUP-002. |
| `products/sense360-poe.yaml`, `products/sense360-fan-pwm.yaml` | `legacy-compatible` | Legacy single-purpose YAMLs; still validated by the broad sweep. | Keep. |
| `packages/base/**` | `legacy-compatible` | Loaded by every product; reachable as `github://sense360store/esphome-public/packages/base/...` from customer ESPHome configs. | Keep. Treat as public API. |
| `packages/features/**` | `legacy-compatible` | Includes `ceiling_halo_leds.yaml`, `ceiling_led_ring_air_quality.yaml`, `airiq_*`, `bathroom_*`, `comfort_*`, `presence_*`, fan-control profiles. Used by both Release-One and legacy products, and reachable as remote packages. | Keep. Treat as public API. |
| `packages/hardware/**` | `legacy-compatible` | Includes `led_ring_ceiling.yaml`, `led_ring_mic_*.yaml`, `led_ring_wall.yaml`, `sense360_core_*.yaml`, `power_*.yaml`, `presence_*.yaml`, `mini_onboard_sensors.yaml`. Used by Release-One and legacy products. | Keep. Treat as public API. |
| `packages/expansions/**` (excluding `fan_triac.yaml`) | `legacy-compatible` | Includes `airiq_*`, `bathroom.yaml`, `comfort_*`, `fan_*`, `gpio_expander_sx1509.yaml`, `presence_*`. | Keep. Treat as public API. |
| `packages/README.md` | `legacy-compatible` | Token list aligned with WebFlash; legacy section headers (Comfort/Presence/Bathroom/Fan) flagged with WebFlash equivalents. | Keep. |
| `packages/SENSE360_MODULES.md` | `legacy-compatible` / `candidate-for-removal` | Long Mini/AirIQ inventory; only referenced by `packages/README.md`. Not part of WebFlash flow. | Keep for now; revisit in CLEANUP-006 after the user-facing docs sweep lands. |
| `base/`, `features/`, `hardware/` (top-level symlinks) | `legacy-compatible` | Symlinks to `packages/base`, `packages/features`, `packages/hardware`. Likely targeted by remote-package URLs that omit the `packages/` prefix. | Keep. Do not remove without first auditing remote-package URL shapes. |
| `components/ld2412/`, `components/ld2450/`, `components/ld24xx/` | `legacy-compatible` | ESPHome external components, loaded via `packages/base/external_components.yaml` (a `github://` source pinned to this repo). | Keep. Treat as public API. |
| `include/sense360/` (+ `include/README.md`) | `legacy-compatible` | C++ headers consumed via `github://sense360store/esphome-public/include/sense360/*` (see `examples/custom-with-remote-headers.yaml:22-24`, `tests/INTEGRATION_GUIDE.md:32-38`). | Keep. Treat as public API. |
| `tests/generate_test_configs.py`, `tests/batch_validate_esphome.py`, `tests/find_duplicate_entities.py`, `tests/quick_check_duplicates.sh`, `tests/unit/**`, `tests/esphome/**`, `tests/README.md`, `tests/INTEGRATION_GUIDE.md`, `tests/Makefile` | `legacy-compatible` | Broad-sweep test infrastructure used by `ci-validate-configs.yml`. Not Release-One-specific but still load-bearing for the manual sweep. | Keep. |
| `examples/customer-basic.yaml` | `legacy-compatible` | Customer config example; already pinned to `ref: v1.0.0`. Long AirIQ-centric phrasing without a VentIQ/Release-One pointer. | Keep; refresh wording in CLEANUP-005. |
| `examples/custom-with-remote-headers.yaml` | `legacy-compatible` | Documents the `github://...` headers usage pattern (currently pinned `@v2.0.0`). | Keep. Consider pinning to a Release-One tag in CLEANUP-006 once the C++ header API is confirmed in `v1.0.0`. |
| `examples/secrets.yaml.template` | `legacy-compatible` | Example secrets file. | Keep. |
| `secrets.example.yaml` | `legacy-compatible` (with `stale` comments) | Lines 42 and 50 still describe MQTT as "required for AirIQ MQTT publishing" / "AirIQ-specific MQTT substitutions". Does not mention VentIQ/RoomIQ. | Keep file; reword comments in CLEANUP-002. |
| `.github/workflows/ci-validate-configs.yml` | `legacy-compatible` (header `stale`) | Workflow itself is fine as the broad legacy sweep, but the file header at lines 10 ("Test all existing product configurations (31+ products)") presents it as a production gate. | Keep workflow; reword header in CLEANUP-002. |
| `docs/ci-pipeline.md` | `stale` | Line 3 "ensures all products can be compiled successfully before release". Line 110 "Complete ESPHome validation of all products". Line 125 "automatically discovers all products". Lines 27–84 frame the Mini board as the primary CI surface. Reads like the legacy-sweep workflow gates production releases. | Reword in CLEANUP-002. |
| `docs/modular-combinations.md` | `stale` | Uses `Bathroom Pro` and `LED Ring` as current-tense names across ~30 lines (50, 53, 92, 107, 171, 184, 204–207, 227–230, 253–257, 276–280, 294–295, 306–307, 419–469, 515–553, 667). `release-one-hardware-audit.md:191` explicitly forbids reusing "Bathroom Pro" in user-facing material. | Reword in CLEANUP-003. |
| `docs/product-matrix.md` | `stale` (one row + section) | Line 357 row `Sense360_Module_Bathroom_Pro` / "Sense 360 Bathroom Pro". Line 366 "Bathroom Pro (additional)" sub-header. (Rest of the doc is `current`.) | Reword in CLEANUP-003. |
| `docs/product-release-matrix.md` | `stale` | Whole doc framed at v3.0.0 / 2025-12-05. Lines 51 ("S360-LED-C / LED Ring Ceiling") and 53 ("S360-LED-W / LED Ring Wall") and 62–63 ("LED Ring Optional") use the old name. Does not mention Release-One config string or `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`. | Reword in CLEANUP-003 (apply `LED Ring` → `Sense360 LED`; add Release-One header banner). |
| `docs/board-combinations.md` | `stale` | Same family as `modular-combinations.md`: section 5 "LED Rings" (line 98), ASCII diagram (line 358), power-budget row (line 377), package-reference table (line 388) all use `LED Ring`. Bathroom Pro / AirIQ as current modules. Does not mention WebFlash config strings. | Reword in CLEANUP-003. |
| `docs/configuration.md` (Mini sections) | `stale` framing | Lines 48–89 frame Mini AirIQ / Presence variants as the primary "Product Variants" without a Release-One pointer. Lines 315–349 describe a Mini night-brightness flow. | Add a Release-One pointer / "this is a legacy-compatible Mini path" admonition in CLEANUP-005. |
| `docs/development.md` (Mini list) | `stale` framing | Lines 60, 141–148 list Mini variants as canonical local-test surface. | Add a Release-One pointer in CLEANUP-005. |
| `docs/installation.md:280-281` | `stale` framing | Mini snippet at lines 280–281 in the "Option / advanced" walkthrough. The doc header already pins Release-One, so this is minor. | Reword in CLEANUP-005. |
| `docs/architecture.html` | `stale` | References `LED Ring Ceiling` (`S360-LED-C`), `LED Ring Wall` (`S360-LED-W`); does not name Release-One config string. | See CLEANUP-004 — pick from: regenerate from Markdown, add a legacy banner, or remove only after confirming nothing serves/links these. |
| `docs/configuration.html` | `stale` | HTML snapshot whose Markdown twin (`docs/configuration.md`) has been updated; HTML still says "Mini core board" without Release-One framing. | CLEANUP-004 decision. |
| `docs/index.html` | `stale` | HTML landing snapshot, not linked from any `*.md`, `*.yaml`, `*.py`, or workflow inside the repo (confirmed by grep). | CLEANUP-004 decision. |
| `docs/installation.html` | `stale` | HTML twin of an updated Markdown (`docs/installation.md`). | CLEANUP-004 decision. |
| `docs/product-guide.html` | `stale` | References Sense360 Mini as the primary product. | CLEANUP-004 decision. |
| `docs/technical-reference.html` | `stale` | "LED Rings" section (lines 313, 439, 452, 458, 728). | CLEANUP-004 decision. |
| `tests/INTEGRATION_GUIDE.md` | `stale` framing | Pins `@v2.0.0` and `ref: v2.0.0` for the C++ header API. Header API is still legacy-compatible, but the version reference is older than `v1.0.0` Release-One. | Pin to a Release-One-aware tag in CLEANUP-006. |
| `scripts/scaffold_product.py` (PRODUCT-010) | `current` | PRODUCT-010 conservative product scaffold report generator. Read-only / dry-run: emits a Markdown report to stdout and never writes any file. Parses the proposed config string against `config/webflash-compatibility.json` (mounting / power / modules / forbidden tokens / mutex / fan-driver "max one of" / FanDAC↔AirIQ); cross-references `config/product-catalog.json` and `config/webflash-builds.json` for duplicate detection; validates every `--hardware slot=SKU` against `config/hardware-catalog.json`; derives the canonical WebFlash artifact name via `scripts/product_name_mapper.py` (read-only import). Allowed scaffold statuses: `compile-only`, `hardware-pending`, `preview`, `blocked`. Rejects `production`, `deprecated`, `removed`, `legacy-compatible`. Forces any FanTRIAC-bearing config to `--status blocked --blocker HW-005`. Does **not** write `config/product-catalog.json`, `config/webflash-builds.json`, `config/webflash-compatibility.json`, `config/hardware-catalog.json`, any product YAML, any WebFlash wrapper, any package, any workflow, any component, any header, or any test. Does **not** generate firmware, draft release notes, create GitHub releases, or import into WebFlash. Does **not** scaffold a production entry, unblock FanTRIAC, change LED status, change Release-One, or change mains-voltage compliance. | Keep. |
| `tests/test_scaffold_product.py` (PRODUCT-010) | `current` | Stdlib `unittest` suite for `scripts/scaffold_product.py`. Covers: valid compile-only happy path; validation-commands section present; do-not-change-guardrails section present; invalid module / mounting tokens; AirIQ vs VentIQ mutex; future tokens (LED / FanRelay / FanPWM / FanDAC / AirIQ) parse cleanly; duplicate catalog entry; unknown hardware SKU; `production` / `legacy-compatible` status rejection; preview with `--channel stable` rejection; preview `--webflash-build-matrix` without `--webflash-wrapper` rejection; preview must not claim a Release-One required config; preview catalog-only happy path; FanTRIAC compile-only rejection / FanTRIAC blocked with `HW-005` accepted / FanTRIAC blocked with wrong blocker rejected; compile-only must not request build matrix; hardware-pending requires `--missing-hardware-evidence`; `products/webflash/*` rejected as `--product-yaml`; read-only invariant (no fixture file is mutated by a run). Uses synthetic JSON fixtures via the script's `--catalog` / `--builds` / `--compat` / `--hardware-catalog` override flags so the real catalog state cannot influence the assertions. | Keep. |
| `docs/product-scaffold-generator.md` (PRODUCT-010) | `current` | PRODUCT-010 workflow doc for `scripts/scaffold_product.py`. Explains the conservative-by-default principle (dry-run, no production, no build-matrix by default, no firmware, no release artifacts, no WebFlash import, human review required); enumerates the allowed scaffold statuses and per-status required flags; gives worked invocations for compile-only / blocked-FanTRIAC / preview-catalog-only / preview-with-build-matrix; documents the Markdown report structure and exit codes; states explicitly that the tool does not write `config/*.json`, product YAML, wrapper YAML, `product_name_mapper.py`, `validate_product_catalog_consistency.py`, packages, workflows, components, headers, or tests; does not generate firmware or release notes; does not unblock FanTRIAC; does not change Release-One or the LED preview catalog entry or the mains-voltage compliance status. Cross-linked from `docs/product-onboarding.md` (step 4) and `docs/preview-to-stable-promotion-gates.md` (See also). | Keep. |
| `docs/product-availability-taxonomy.md` (PRODUCT-AVAIL-001) | `current` | PRODUCT-AVAIL-001 canonical cross-cutting product availability taxonomy. Names the 13-rung availability ladder (`hardware-listed` → `artifact-indexed` → `schematic-verified` → `pin-map-ready` → `package-yaml-ready` → `product-yaml-ready` → `build-matrix-ready` → `release-artifact-ready` → `webflash-imported` → `webflash-live-preview` → `webflash-live-stable` → `production-required` → `kit-exposed`); defines the per-axis availability states (hardware-side, product-lifecycle, WebFlash-availability, and exception states); introduces the two policy-only exception labels `design-pending` (module named in docs / taxonomy / wizard but not buildable) and `firmware-missing` (board evidenced but no product YAML consumes it); maps every existing enum / classification verbatim — `config/product-catalog.json` `lifecycle_statuses` (`production` / `preview` / `compile-only` / `hardware-pending` / `blocked` / `legacy-compatible` / `deprecated` / `removed`), `config/hardware-catalog.json` `schematic_status` (`verified` / `cataloged_unverified`), HW-004 / HW-006 audit labels (`documented` / `partially-documented` / `cataloged-unverified` / `blocked` / `not-needed-for-release-one`), HW-009 package-mapping labels (`confirmed-ok` / `needs-package-change` / `needs-doc-fix` / `needs-silkscreen/bench-verification` / `blocked` / `unknown`), and the HW-ASSETS-001 per-board artifact index field schema (`pin_map_status` / `package_yaml_status` / `product_yaml_status` / `webflash_status`); records the hardware-evidence vs product-support vs WebFlash-support axis separations; records the preview-vs-stable distinction by reference to RELEASE-006; records the blocked / legacy-compatible / deprecated / removed exception lifecycles by reference to PRODUCT-DEP-001; carries a current-state snapshot table for every SKU in the hardware catalog (`S360-100` Core schematic-verified + artifact-indexed + Release-One + LED preview; `S360-200` RoomIQ schematic-verified + Release-One + LED preview; `S360-210` AirIQ schematic-verified + not-needed-for-release-one + no product YAML; `S360-211` VentIQ schematic-verified + Release-One + LED preview; `S360-300` LED schematic-verified + LED preview only + stable blocked by RELEASE-006 rows 9–17; `S360-310` Relay partially-documented + design-pending; `S360-311` PWM partially-documented + design-pending; `S360-312` DAC partially-documented + design-pending; `S360-320` TRIAC blocked under HW-005 + COMPLIANCE-001; `S360-400` 240v PSU cataloged-unverified + COMPLIANCE-001-gated; `S360-410` PoE PSU partially-documented + Release-One with schematic-verification-pending caveat preserved); records how WebFlash should eventually consume the taxonomy (wizard distinguishes buildable from unbuildable; import readiness rejects blocked / deprecated / removed; wizard must not imply installability when YAML / build / manifest is missing; kits only reference WebFlash-ready products; REQUIRED_CONFIGS remains stable-only and intentionally chosen; wizard surfaces blocker names; wizard respects mutex / max-one-of rules) and lists the future validator / schema candidate fields (`artifact_index_status`, `pin_map_status`, `package_yaml_status`, `product_yaml_status`, `webflash_status`, `availability_notes`, `missing_evidence`) as policy-only names belonging to a future PRODUCT-AVAIL-002 PR; records the follow-up PR sequence (HW-GAP-001 readiness matrix → WF-WIZARD-AVAIL-001 wizard gating → WF-STALE-001 / PRODUCT-STALE-001 stale-data cleanup → PRODUCT-AVAIL-002 machine-readable fields → HW-PINMAP-310 / -311 / -312 / -320 / -400 / -410 → PACKAGE-GAP-001 → PRODUCT-GAP-001); carries the explicit do-not-change guardrails. Documentation only. PRODUCT-AVAIL-001 adds **no** JSON fields and changes **no** statuses: `config/product-catalog.json` `lifecycle_statuses` unchanged; `config/hardware-catalog.json` `schematic_status` unchanged for every SKU; `config/webflash-builds.json` build matrix unchanged; `config/webflash-compatibility.json` unchanged; every product YAML, WebFlash wrapper, and package YAML unchanged; every script, test, workflow, component, and include unchanged. Release-One stays `Ceiling-POE-VentIQ-RoomIQ` on `stable` with artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` and tag `v1.0.0`; the LED preview entry `Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`, `channel: preview`; FanTRIAC stays `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`; mains-voltage compliance status for `S360-320` / `S360-400` (COMPLIANCE-001) is not changed. Cross-linked from `docs/product-onboarding.md`, `docs/product-deprecation-removal-policy.md`, `docs/preview-to-stable-promotion-gates.md`, `docs/hardware/hardware-artifact-policy.md`, `docs/hardware/firmware-package-mapping-audit.md`, and `docs/hardware/remaining-board-documentation-audit.md`. | Keep. |
| `docs/webflash-exposure-readiness-matrix.md` (WEBFLASH-GAP-001) | `current` | WEBFLASH-GAP-001 canonical WebFlash-layer exposure readiness matrix. Sits one layer downstream of `docs/product-readiness-matrix.md` (PRODUCT-GAP-001); where PRODUCT-GAP-001 decides whether a product YAML may be added, WEBFLASH-GAP-001 decides whether — and how — a product YAML, once it exists, may be exposed through WebFlash (wrapper under `products/webflash/`, catalog entry in `config/product-catalog.json` with `webflash_wrapper` / `webflash_build_matrix: true`, build-matrix row in `config/webflash-builds.json`, signed release artifact, and eventual import into the WebFlash repo's `manifest.json` / `firmware-N.json`). Records the namespace convention: `WEBFLASH-GAP-001` is the readiness / gating matrix (this PR); the per-family implementation slices are `WEBFLASH-RELAY-001` (FanRelay), `WEBFLASH-PWM-001` (FanPWM), `WEBFLASH-DAC-001` (FanDAC), `WF-TRIAC-001` (FanTRIAC advanced / manual-warning), `WEBFLASH-POWER-400-001` (PWR-240V), `WEBFLASH-POE-410-001` (PoE-410, if warranted), each followed by `RELEASE-GAP-001` / `RELEASE-TRIAC-001` and `WF-IMPORT-GAP-001` / `WF-IMPORT-TRIAC-001`. Records the policy-only status vocabulary (`not-webflash-ready` / `missing-product-yaml` / `missing-package-readiness` / `missing-hardware-evidence` / `preview-candidate` / `advanced/manual-warning-only` / `standard-exposure-candidate` / `production-candidate` / `not-required-configs` / `not-recommended` / `not-kit-default` / `docs-only` / `legacy-only` / `blocked-from-standard-exposure` / `unknown`) as cell labels only — adds **no** JSON enum, schema, or validator. Records the six WebFlash exposure classes (`none` / `docs-only` / `preview-candidate` / `advanced/manual-warning-only` / `production-candidate` / `legacy-only`) with the explicit rule that `advanced/manual-warning-only` is an exposure class, not a certification claim. Carries the candidate exposure table (FanRelay / FanPWM / FanDAC / FanTRIAC / PWR-240V / PoE-410), per-family WebFlash posture sections (Relay / S360-310, PWM / S360-311, DAC / S360-312, TRIAC / S360-320 advanced/manual-warning-only, Power / S360-400, PoE / S360-410), the Release-One + LED preview safety section, the REQUIRED_CONFIGS policy (advanced/manual-warning products are never REQUIRED_CONFIGS by default; FanTRIAC is never REQUIRED_CONFIGS by default; new preview candidates are not REQUIRED_CONFIGS; LED's stable promotion remains separate; any future REQUIRED_CONFIGS addition requires a separate explicit PR), the kit/recommended path policy (separate from WebFlash installability; advanced/manual-warning products must not be kit / default / recommended; FanTRIAC must not be kit / default / recommended; Relay/PWM/DAC need separate product/UX decisions before kit/recommended exposure), the wrapper/catalog/build sub-gate table, the release/import sub-gate table, the follow-up PR sequence, the do-not-change guardrails, and the validation suite. Documentation only. WEBFLASH-GAP-001 adds **no** JSON fields and changes **no** statuses: `config/hardware-catalog.json` `schematic_status` unchanged for every SKU; `config/product-catalog.json` `lifecycle_statuses` and every product entry unchanged; `config/webflash-builds.json` build matrix unchanged (the two existing builds `Ceiling-POE-VentIQ-RoomIQ` stable and `Ceiling-POE-VentIQ-RoomIQ-LED` preview are not touched); `config/webflash-compatibility.json` unchanged (no new `canonical_modules` token, no new `forbidden_tokens` entry, no new `release_one_required_configs` member, no mutex relaxation); every product YAML under `products/`, every WebFlash wrapper under `products/webflash/`, every package YAML under `packages/`, every script under `scripts/`, every test under `tests/`, every workflow under `.github/workflows/`, every component / include / firmware artifact unchanged; no firmware regenerated, no GitHub Release created or modified, no WebFlash import. Release-One stays `Ceiling-POE-VentIQ-RoomIQ` on `stable` with artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` and tag `v1.0.0`; the LED preview entry `Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`, `channel: preview`, artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`, `blocked_modules: ["FanTRIAC"]`; FanTRIAC stays `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`; the FanTRIAC long-term posture `advanced/manual-warning-only` is documented but **not** realised (no flip off `blocked`, no live build matrix, no release, no import); mains-voltage compliance status for `S360-320` / `S360-400` (COMPLIANCE-001) is not changed; the Core J10 vs RoomIQ J6 pin-order discrepancy is not resolved; the systemic Core abstract-bus mismatch (`CORE-ABSTRACT-BUS-001`, owned by `release-one-hardware-audit.md` Required follow-ups #2 / #3) is not resolved; the `S360-410` PoE PSU schematic-pending caveat in `release-one-hardware-audit.md` Findings → PoE PSU is preserved; the `S360-300` bench-verification Open Questions are preserved; every `legacy-compatible` entry stays `legacy-compatible`; no entry is deprecated or removed. Cross-linked from `docs/product-readiness-matrix.md` (See also). | Keep. |
| `docs/release-artifact-readiness-matrix.md` (RELEASE-GAP-001) | `current` | RELEASE-GAP-001 canonical release-layer artifact readiness matrix. Sits one layer downstream of `docs/webflash-exposure-readiness-matrix.md` (WEBFLASH-GAP-001), two layers downstream of `docs/product-readiness-matrix.md` (PRODUCT-GAP-001), three layers downstream of `docs/hardware/package-readiness-matrix.md` (PACKAGE-GAP-001), and four layers downstream of `docs/hardware/board-readiness-matrix.md` (HW-GAP-001); where WEBFLASH-GAP-001 decides whether — and how — a product YAML, once it exists, may be exposed through WebFlash, RELEASE-GAP-001 decides whether — and how — a WebFlash-exposed build, once it exists, may be released as a signed firmware artifact through the existing `.github/workflows/firmware-build-release.yml` flow, attached to a GitHub Release as `Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin` with `checksums-sha256.txt`, `checksums-md5.txt`, and the build-info `manifest.json`, validated against the artifact-naming / release-notes / release-assets guards, and recorded in `docs/webflash-release-proof.md` for WebFlash-side ingest by `WF-IMPORT-GAP-001` / `WF-IMPORT-TRIAC-001`. Records the namespace convention: `RELEASE-GAP-001` is the readiness / gating matrix (this PR); the per-family implementation slices are `RELEASE-RELAY-001` (FanRelay), `RELEASE-PWM-001` (FanPWM), `RELEASE-DAC-001` (FanDAC), `RELEASE-TRIAC-001` (FanTRIAC advanced / manual-warning, dedicated channel), `RELEASE-POWER-400-001` (PWR-240V), `RELEASE-POE-410-001` (PoE-410, if warranted), each followed by `WF-IMPORT-GAP-001` / `WF-IMPORT-TRIAC-001`. Treats `RELEASE-007` (LED stable promotion of `Ceiling-POE-VentIQ-RoomIQ-LED` from `preview` / `preview` to `production` / `stable`, including the artifact rename from `…-v1.0.0-preview.bin` to `…-v1.0.0-stable.bin` and the tag bump from `v1.0.0-led-preview` to a plain `vX.Y.Z`) as **reference-only and out-of-scope**: LED stable is owned by `docs/preview-to-stable-promotion-gates.md` and gated by the existing 17-row LED preview-to-stable gauntlet (rows 9–17 still pending), including `WF-HW-TEST-002` operator proof and `S360-300-BENCH-001` bench verification; RELEASE-GAP-001 does **not** advance any of these. Records the policy-only status vocabulary (`not-release-ready` / `missing-build-matrix` / `missing-webflash-wrapper` / `missing-product-yaml` / `missing-package-readiness` / `missing-hardware-evidence` / `preview-artifact-candidate` / `advanced/manual-warning-artifact-only` / `stable-candidate-after-promotion` / `stable-not-approved` / `not-required-configs` / `not-recommended` / `not-kit-default` / `operator-proof-required` / `release-proof-required` / `legacy-only` / `docs-only` / `blocked-from-standard-release` / `unknown`) as cell labels only — adds **no** JSON enum, schema, or validator and reuses every existing classification vocabulary verbatim (`config/product-catalog.json` `lifecycle_statuses`; `config/webflash-compatibility.json` `allowed_channels` with `production_channel: stable` and `rescue_config_string: "Rescue"`; PACKAGE-GAP-001 / PRODUCT-GAP-001 / WEBFLASH-GAP-001 labels; PRODUCT-AVAIL-001 13-rung ladder). Records the seven release classes (`none` / `docs-only` / `preview-artifact-candidate` / `advanced/manual-warning-artifact-only` / `stable-candidate-after-promotion` / `production/stable` / `legacy-only`) with the explicit rules that `advanced/manual-warning-artifact-only` is an exposure class, not a certification claim; that a `preview-artifact-candidate` is not a stable release; that a `production/stable` artifact is not automatically REQUIRED_CONFIGS; and that a release artifact is not automatically a kit or recommended path. Carries the current release surface (Release-One stable artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` at tag `v1.0.0` with release proof; LED preview artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` at tag `v1.0.0-led-preview` per RELEASE-005 with proof row; FanTRIAC reference no-artifact; 31 `legacy-compatible` no-artifact), the candidate release table (FanRelay / FanPWM / FanDAC / FanTRIAC / PWR-240V / PoE-410 all `not-release-ready` today with per-family allowed-action / future-class / stable-eligibility / REQUIRED_CONFIGS-eligibility / kit-recommended-eligibility / follow-up-owner columns), per-family release posture sections (Relay / S360-310, PWM / S360-311, DAC / S360-312, TRIAC / S360-320 `advanced/manual-warning-artifact-only` + `stable-not-approved` + `blocked-from-standard-release`, Power / S360-400, PoE / S360-410), the Release-One + LED preview safety section, the Stable promotion policy (preview-to-stable is not automatic; LED stable is owned by `RELEASE-007` and gated by the 17-row gauntlet, `WF-HW-TEST-002`, and `S360-300-BENCH-001`; future Relay / PWM / DAC artifacts start as `preview-artifact-candidate`; advanced / manual-warning TRIAC artifacts must not become stable by default; PWR-240V stable is gated additionally by COMPLIANCE-001; PoE-410 stable is reserved for the existing Release-One caveat path), the REQUIRED_CONFIGS policy (release artifact does not imply REQUIRED_CONFIGS; new preview artifacts are not REQUIRED_CONFIGS; advanced / manual-warning artifacts are never REQUIRED_CONFIGS by default; FanTRIAC is never REQUIRED_CONFIGS by default; LED's stable promotion remains separate; any future REQUIRED_CONFIGS addition requires a separate explicit PR), the kit / recommended release policy (release artifact existence is separate from kit / recommended; a product can be released but not recommended; advanced / manual-warning artifacts must not be kit / default / recommended; FanTRIAC must not be kit / default / recommended; Relay / PWM / DAC need separate product / UX decisions; PWR-240V kit / recommended is gated additionally by COMPLIANCE-001; Release-One's existing kit / recommended membership is not touched; LED's kit / recommended is separate), the release note / artifact / checksum gate table (product catalog entry / build-matrix entry / artifact-name conformance / release tag conformance / release notes generated and valid / artifact built / SHA256 + MD5 checksums attached / build-info manifest attached / release proof recorded / WebFlash import-readiness — each cross-referenced to the existing validator at `scripts/derive_release_version_channel.py`, `scripts/generate_webflash_release_notes.py`, `scripts/validate-webflash-release-notes.py`, `scripts/check-webflash-release-assets.py`, `scripts/validate_product_catalog_consistency.py`, `tests/test_webflash_artifact_naming.py`, `tests/validate_webflash_builds.py`, `tests/test_webflash_compatibility.py`, `tests/test_validate_webflash_release_notes.py`, `tests/test_generate_webflash_release_notes.py`, `tests/test_derive_release_version_channel.py`, `tests/test_product_catalog.py`, `tests/test_product_catalog_consistency.py`, `tests/test_release_one_entity_names.py`, `tests/test_led_package_mapping.py`, `tests/validate_configs.py`), the operator proof gate table (Release-One done; LED preview pending via `WF-HW-TEST-002` + `S360-300-BENCH-001` for `RELEASE-007`; family-specific containers for Relay / PWM / DAC / TRIAC / PWR-240V / PoE-410 are future-only; TRIAC requires additional timing / real-load / compliance warnings even for advanced / manual-warning release), the follow-up PR sequence (`RELEASE-RELAY-001`, `RELEASE-PWM-001`, `RELEASE-DAC-001`, `RELEASE-TRIAC-001`, `RELEASE-POWER-400-001`, `RELEASE-POE-410-001`, `RELEASE-007` reference-only, `WF-IMPORT-GAP-001`, `WF-IMPORT-TRIAC-001`), the do-not-change guardrails, and the validation suite. Documentation only. RELEASE-GAP-001 adds **no** JSON fields and changes **no** statuses: `config/hardware-catalog.json` `schematic_status` unchanged for every SKU; `config/product-catalog.json` `lifecycle_statuses` and every product entry unchanged; `config/webflash-builds.json` build matrix unchanged (the two existing builds `Ceiling-POE-VentIQ-RoomIQ` stable and `Ceiling-POE-VentIQ-RoomIQ-LED` preview are not touched); `config/webflash-compatibility.json` unchanged (no new `canonical_modules` token, no new `forbidden_tokens` entry, no new `release_one_required_configs` member, no `allowed_channels` change, no `production_channel` change, no `artifact_pattern` change, no mutex relaxation); every product YAML under `products/`, every WebFlash wrapper under `products/webflash/`, every package YAML under `packages/`, every script under `scripts/`, every test under `tests/`, every workflow under `.github/workflows/` (`firmware-build-release.yml`, `release-notes-draft.yml`, `validate.yml`, `ci-validate-configs.yml`), every component / include / firmware artifact unchanged; no firmware regenerated, no GitHub Release created or modified, no checksums recorded, no release-notes drafted, no release-proof row added or modified in `docs/webflash-release-proof.md`, no WebFlash import performed. Release-One stays `Ceiling-POE-VentIQ-RoomIQ` on `stable` with artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` and tag `v1.0.0` (no re-release, no re-stamp, no re-qualification); the LED preview entry `Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`, `channel: preview`, version `1.0.0`, artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`, tag `v1.0.0-led-preview`, `blocked_modules: ["FanTRIAC"]` (no promotion to `production` / `stable`; no addition to `release_one_required_configs`; no kit added; LED stable is owned by the separate `RELEASE-007` slice, not by RELEASE-GAP-001); the FanTRIAC reference `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false` (the advanced / manual-warning long-term posture is documented but **not** realised — no flip off `blocked`, no live build matrix, no release artifact, no advanced-channel build, no import); mains-voltage compliance status for `S360-320` / `S360-400` (COMPLIANCE-001) is not changed; the Core J10 vs RoomIQ J6 pin-order discrepancy is not resolved; the systemic Core abstract-bus mismatch (`CORE-ABSTRACT-BUS-001`, owned by `release-one-hardware-audit.md` Required follow-ups #2 / #3) is not resolved; the `S360-410` PoE PSU schematic-pending caveat in `release-one-hardware-audit.md` Findings → PoE PSU is preserved; the `S360-300` bench-verification Open Questions and `S360-300-BENCH-001` record are preserved; the WebFlash-side `WF-HW-TEST-002` LED operator-proof container stays unfilled; every `legacy-compatible` entry stays `legacy-compatible`; no entry is deprecated or removed. Cross-linked from `docs/product-readiness-matrix.md` (See also), `docs/webflash-exposure-readiness-matrix.md` (See also), and `docs/preview-to-stable-promotion-gates.md` (See also). | Keep. |
| `docs/hardware/board-readiness-matrix.md` (HW-GAP-001) | `current` | HW-GAP-001 canonical board-level readiness matrix for every SKU in `config/hardware-catalog.json`. Threads together the per-board evidence axes — hardware catalog status, schematic PDF, per-board artifact index (HW-ASSETS-001 / 002), pin-map / standalone reference doc (HW-004 / HW-006 / HW-008), package YAML (HW-009 / HW-010), product YAML, WebFlash wrapper, WebFlash build matrix, release artifact, WebFlash manifest / import, bench / operator proof (RELEASE-006), blockers / open questions, and current classification — into a single per-board × per-axis matrix. Uses two summary tables (hardware-evidence axis and productization / WebFlash axis) plus per-board notes that link back to the source-of-truth docs. Records the policy-only status vocabulary (`done` / `partial` / `missing` / `not applicable` / `blocked` / `compliance-gated` / `preview-only` / `legacy-only` / `unknown`) as cell labels only — adds **no** JSON enum, schema, or validator. Records ready / evidenced boards (`S360-100` Core, `S360-200` RoomIQ, `S360-210` AirIQ, `S360-211` VentIQ, `S360-300` LED), missing / unfinished boards (`S360-310` Relay, `S360-311` PWM, `S360-312` DAC, `S360-400` 240v PSU, `S360-410` PoE PSU) and the blocked / compliance-gated boards (`S360-320` TRIAC under HW-005 + COMPLIANCE-001; `S360-400` under COMPLIANCE-001). Records the follow-up PR sequence (`HW-PINMAP-310` / `-311` / `-312` / `-320` / `-400` / `-410` → `PACKAGE-GAP-001` → `PRODUCT-GAP-001` → `WEBFLASH-GAP-001` → `RELEASE-GAP-001` → `WF-IMPORT-GAP-001`). Carries the explicit do-not-change guardrails. Documentation only. HW-GAP-001 adds **no** JSON fields and changes **no** statuses: `config/hardware-catalog.json` `schematic_status` unchanged for every SKU; `config/product-catalog.json` `lifecycle_statuses` unchanged; `config/webflash-builds.json` build matrix unchanged; `config/webflash-compatibility.json` unchanged; every product YAML, WebFlash wrapper, and package YAML unchanged; every script, test, workflow, component, and include unchanged; no firmware regenerated, no GitHub Release created or modified, no WebFlash import. Release-One stays `Ceiling-POE-VentIQ-RoomIQ` on `stable` with artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` and tag `v1.0.0`; the LED preview entry `Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`, `channel: preview`; FanTRIAC stays `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`; mains-voltage compliance status for `S360-320` / `S360-400` (COMPLIANCE-001) is not changed; the Core J10 vs RoomIQ J6 pin-order discrepancy (HW-009 `needs-silkscreen/bench-verification`) is not resolved; the systemic Core abstract-bus mismatch (HW-009 `needs-package-change`, owned by `release-one-hardware-audit.md` Required follow-ups #2 / #3) is not resolved; the `S360-410` PoE PSU schematic-pending caveat in `release-one-hardware-audit.md` Findings → PoE PSU is preserved; the `S360-300` bench-verification Open Questions are preserved; every `legacy-compatible` entry stays `legacy-compatible`. Cross-linked from `docs/product-availability-taxonomy.md` (See also + Follow-up-PR-sequence row #1), `docs/hardware/hardware-artifact-policy.md` (See also + Follow-up-PR-sequence row #2), `docs/hardware/firmware-package-mapping-audit.md` (See also), and `docs/hardware/remaining-board-documentation-audit.md` (See also). | Keep. |
| Backup / tmp files | `dead` (none found) | `find . -name '*.bak' -o -name '*.orig' -o -name '*~' -o -name '*.tmp'` returns no matches. | None. |

## Stale Release-One references

These are repo locations whose wording contradicts the current Release-One
source of truth. Every entry in this section is **doc-only** — none of them
require firmware or workflow logic changes.

- `CHANGELOG.md` lines 25–34 (`Unreleased / Added` "WebFlash compatibility
  contract" bullet). Still says the release-one config is
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`, contradicting the REL-001 Changed
  bullet at lines 11–22 immediately above which pins
  `Ceiling-POE-VentIQ-RoomIQ`. Also lines 32–34 ("Release-One product YAML…
  matches `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`…") and line 46
  ("`Sense360-Ceiling-POE-VentIQ-FanTRIAC-RoomIQ-v1.0.0-stable.bin`").
  *Per user instruction, this PR records the issue only and does not fix
  it. Resolution belongs to CLEANUP-002.*
- `.github/workflows/ci-validate-configs.yml:10` — header bullet "Test all
  existing product configurations (31+ products)" presents this workflow
  as the Release-One gate. It is in fact the broad legacy sweep.
- `docs/ci-pipeline.md:3` — "ensures all products can be compiled
  successfully before release". `docs/ci-pipeline.md:110` — "Complete
  ESPHome validation of all products". `docs/ci-pipeline.md:125` — "The
  CI automatically discovers all products". Same framing problem as the
  workflow header.
- `secrets.example.yaml:42` and `secrets.example.yaml:50` — describes
  MQTT as "required for AirIQ MQTT publishing" / "AirIQ-specific MQTT
  substitutions". Release-One is VentIQ, not AirIQ; these comments need
  to either drop the "AirIQ" framing or call out that the same vars are
  used for VentIQ too.
- `products/sense360-core-*.yaml` and `products/sense360-mini-*.yaml`
  comment headers — pinned `ref: v2.2.0` / `ref: v3.0.0` examples
  (lines 21, 24, 26, 28, 29, 103, 145, 258, 358, 474 across the affected
  files). Current Release-One tag is `v1.0.0`. Comments only; no code
  effect.

## FanTRIAC / TRIAC references

> **HW-005 re-verified: still blocked — missing evidence.** No new schematic,
> pin map, or driver evidence has landed; the `S360-320` schematic is still
> uncommitted, no SX1509 channel is assigned to `TRI_GPIO1` / `TRI_GPIO2`,
> and the placeholder GPIO5/GPIO6 substitutions still collide with RoomIQ
> J10. See
> [`docs/release-one-hardware-audit.md#fantriac-mapping-resolution`](release-one-hardware-audit.md#fantriac-mapping-resolution)
> for the full verdict, the missing-evidence checklist, and the
> re-verification record.

FanTRIAC is intentionally excluded from production Release-One while HW-005
is open. Every FanTRIAC reference in the repo is **`blocked-reference`** —
retained on purpose so the slot can be re-armed once the
`S360-320` schematic is committed and a direct-ESP32 mapping (or a
replacement non-`ac_dimmer` driver) is verified.

Authoritative explanation: see
[`docs/release-one-hardware-audit.md#fantriac-mapping-resolution`](release-one-hardware-audit.md).

Retained files:

- `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml` (carries
  `BLOCKED / UNVERIFIED — must not ship as FanTRIAC-capable` banner;
  `fallback_ssid: "S360 TRIAC BLOCKED"`; explicit comment that fixing the
  hostname was a cosmetic 31-char fix, not an unblock).
- `products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml` (explicit
  "retained in the repo for future use only" banner; not in the build
  matrix).
- `packages/expansions/fan_triac.yaml` (BLOCKED / UNVERIFIED banner and
  pin caveats; resolution pointer to the hardware audit).
- `config/hardware-catalog.json` (Sense360 TRIAC row, `friendly_name`
  + `old_name: TRIAC_Board`).
- `config/webflash-compatibility.json` (FanTRIAC remains in
  `canonical_modules`; this is correct — the token is still a valid
  WebFlash module, just not part of Release-One's required configs).

Retained docs that explain the exclusion (each clearly states FanTRIAC is
**not** in Release-One):

- `README.md` ("FanTRIAC excluded from production Release-One" callout).
- `docs/release-one.md` (top-of-doc admonition + Files table).
- `docs/release-one-hardware-audit.md` (full HW-005 row, FanTRIAC mapping
  resolution section).
- `docs/webflash-contract.md` (FanTRIAC token remains valid; production
  exclusion called out).
- `docs/webflash-ci-alignment.md` (FanTRIAC admonition).
- `docs/webflash-release-handoff.md` (FanTRIAC admonition).
- `docs/product-matrix.md`, `docs/installation.md` (FanTRIAC admonitions).

Test-side anchors that hold this contract in place:

- `tests/test_webflash_compatibility.py` (asserts `FanTRIAC` is in
  `canonical_modules`).
- `tests/test_validate_webflash_release_notes.py:30,137` (release-body
  text asserts "FanTRIAC is excluded from production Release-One while
  HW-005 is open").
- `tests/test_webflash_artifact_naming.py:21-23` (commentary that
  FanTRIAC is retained as a blocked/reference file).
- `tests/validate_webflash_builds.py` (FanTRIAC is one of the four
  permitted `FAN_DRIVER_TOKENS`).
- `scripts/product_name_mapper.py:35-36,46,173,176` (FanTRIAC mapping
  kept with explicit "intentionally excluded" comment).

**Recommendation: keep all FanTRIAC artifacts and references untouched.**
No FanTRIAC cleanup belongs in this audit-only PR or in CLEANUP-002 /
CLEANUP-003. FanTRIAC is unblocked only by HW-005, not by repo cleanup.

> **PRODUCT-TRIAC-001 update.** `PRODUCT-TRIAC-001` has separately
> reclassified the catalog-entry policy for
> `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` from
> "intentionally-excluded / blocked-reference" framing to
> **advanced / manual-warning candidate** framing via a notes-only
> edit on
> [`config/product-catalog.json`](../config/product-catalog.json).
> The structural fields (`status: blocked`, `blocker: HW-005`,
> `reason`, `webflash_build_matrix: false`, no `artifact_name`) and
> every blocked-reference artifact listed above remain unchanged.
> FanTRIAC is **still** blocked from standard exposure, **still**
> not Release-One, **still** not REQUIRED_CONFIGS, **still** not
> recommended, **still** not kit / default, and **still** not
> compliance-certified. HW-005 and COMPLIANCE-001 remain open. See
> [§PRODUCT-TRIAC-001 update](#product-triac-001-update-reclassify-fantriac-as-advancedmanual-warning).

## LED / LED Ring references

Two distinct things to keep straight:

1. **Sense360 LED (S360-300)** is the canonical name. `LED Ring` is the
   **old name**, preserved as `old_name` in
   `config/hardware-catalog.json:55` and as a labelled column in
   `docs/hardware-catalog.md:30`. `docs/release-one-hardware-audit.md`
   (Sense360 LED row, lines 131–132 and 155+) explicitly applies "Option A":
   remove the LED package includes from Release-One YAML so the binary
   matches the LED-less WebFlash config string. The LED packages remain in
   the repo for other products and for a future LED-bearing config string
   such as `Ceiling-POE-VentIQ-RoomIQ-LED`.
2. **LED token** is not in the Release-One WebFlash config string
   `Ceiling-POE-VentIQ-RoomIQ`. It is still a valid WebFlash module per
   `config/webflash-compatibility.json:14` (`canonical_modules` includes
   `LED`).

Status per location:

| Path | Status | Notes |
|---|---|---|
| `packages/hardware/led_ring_ceiling.yaml`, `led_ring_wall.yaml`, `led_ring_mic_ceiling.yaml`, `led_ring_mic_wall.yaml` | `legacy-compatible` | LED package YAMLs; consumed by non-Release-One products and reachable as remote packages. The filenames themselves use the old `led_ring_*` naming, but renaming would break customer remote-package URLs. Keep filenames. |
| `packages/features/ceiling_led_ring_air_quality.yaml`, `packages/features/ceiling_halo_leds.yaml` | `legacy-compatible` | Feature-side LED packages used by Core ceiling products. Keep. |
| `features/`, `hardware/` symlinks (resolve into `packages/...`) | `legacy-compatible` | Same LED files surfaced via the short-form path. Keep. |
| `products/sense360-core-ceiling.yaml`, `sense360-core-ceiling-presence.yaml`, `sense360-core-ceiling-bathroom.yaml`, `sense360-core-wall.yaml`, `sense360-core-wall-presence.yaml`, `sense360-core-voice-ceiling.yaml` | `legacy-compatible` | Headers describe "LED Ring: Halo LED for visual feedback" using the legacy name. Acceptable as YAML-internal comments. |
| `products/sense360-ceiling-poe-ventiq-roomiq.yaml` | `current` | Comment block at lines 121–146 explicitly notes Sense360 LED is **not** included and explains the policy. Aligned. |
| `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml` | `blocked-reference` | Same LED-not-included comment block; aligned. |
| `config/hardware-catalog.json` (Sense360 LED row, lines 52–55) | `current` | Canonical name + `old_name: LED Ring`; correct. |
| `docs/hardware-catalog.md:30` | `current` | Canonical-name table; calls `LED Ring` "old name". Correct. |
| `docs/release-one-hardware-audit.md` (Sense360 LED row, "Sense360 LED policy" section) | `current` | Authoritative explanation of the Option-A removal. |
| `docs/release-one.md:51-110-205` | `current` | Reiterates the LED exclusion. |
| `docs/manual-user-walkthrough.md:181` | `current` | Plain statement that Sense360 LED is excluded from Release-One firmware. |
| `docs/modular-combinations.md` (LED Ring sections), `docs/board-combinations.md` (Section 5, line 98 etc.), `docs/product-release-matrix.md` (S360-LED-C / S360-LED-W rows) | `stale` | Use `LED Ring` as the current-tense product name and do not flag Release-One LED exclusion. |
| `docs/product-matrix.md` (LED Rings section, lines 50, 65, 95, 261, 270, 280, 284, 684, 722) | `stale` framing | Heading "LED Rings" / "Standard LED Ring (Ceiling)" — same canonical-name issue. |
| `docs/configuration.md:317` | `stale` framing | Calls the Mini LED package "the Mini LED package" — Mini-specific, not a Release-One claim, but the surrounding section frames Mini as primary. |
| `docs/architecture.html`, `docs/product-guide.html`, `docs/technical-reference.html` | `stale` | HTML snapshots that still call out `LED Ring Ceiling`/`LED Ring Wall`. |
| `CHANGELOG.md:151` ("Ceiling LED Ring: Air quality visualization for ceiling-mounted devices") | `legacy-compatible` | Historical changelog entry; should not be rewritten. |

**Recommendation:** in CLEANUP-003, replace "LED Ring" → "Sense360 LED" in
user-facing docs (`modular-combinations.md`, `product-matrix.md`,
`board-combinations.md`, `product-release-matrix.md`) and add a sentence
explaining Release-One does not carry an LED. **Do not rename**
`led_ring_*.yaml` package filenames, the canonical-name table column in
`docs/hardware-catalog.md`, or the `old_name` field in
`config/hardware-catalog.json`.

## Legacy product YAMLs

These predate the WebFlash matrix but are still load-bearing:

- They are validated by `.github/workflows/ci-validate-configs.yml` via
  dynamic product discovery (`find products/ -name "*.yaml" -type f !
  -name "secrets.yaml"`).
- They are exercised by `tests/generate_test_configs.py` and the broader
  unit/integration tests.
- They are listed by name in `docs/development.md` and `docs/ci-pipeline.md`
  as Mini-board references.
- They may be referenced by external customers via
  `github://sense360store/esphome-public/products/...` URLs.

Files in scope:

```
products/sense360-core-c-poe.yaml
products/sense360-core-c-pwr.yaml
products/sense360-core-c-usb.yaml
products/sense360-core-v-c-poe.yaml
products/sense360-core-v-c-pwr.yaml
products/sense360-core-v-c-usb.yaml
products/sense360-core-v-w-poe.yaml
products/sense360-core-v-w-pwr.yaml
products/sense360-core-v-w-usb.yaml
products/sense360-core-w-poe.yaml
products/sense360-core-w-pwr.yaml
products/sense360-core-w-usb.yaml
products/sense360-core-ceiling.yaml
products/sense360-core-ceiling-bathroom.yaml
products/sense360-core-ceiling-presence.yaml
products/sense360-core-voice-ceiling.yaml
products/sense360-core-voice-wall.yaml
products/sense360-core-wall.yaml
products/sense360-core-wall-presence.yaml
products/sense360-mini-airiq.yaml
products/sense360-mini-airiq-basic.yaml
products/sense360-mini-airiq-advanced.yaml
products/sense360-mini-airiq-ld2412.yaml
products/sense360-mini-full-ld2412.yaml
products/sense360-mini-presence.yaml
products/sense360-mini-presence-basic.yaml
products/sense360-mini-presence-advanced.yaml
products/sense360-mini-presence-ld2412.yaml
products/sense360-mini-presence-advanced-ld2412.yaml
products/sense360-poe.yaml
products/sense360-fan-pwm.yaml
```

**Recommendation:** classify all of these as `legacy-compatible`. Keep
files as-is. Only the inline `ref: v2.2.0` / `ref: v3.0.0` comment hints
are stale; fix those in CLEANUP-002 alongside the other doc-only rewords.
**Do not** rename, restructure, or delete these YAMLs in any of the
follow-up cleanup PRs without first auditing customer remote-package
URLs.

**Status:** PRODUCT-002 has applied this classification in
[`config/product-catalog.json`](../config/product-catalog.json) — every
top-level product YAML listed above now has a `status: legacy-compatible`
catalog entry with `webflash_build_matrix: false`, no `config_string`, no
`artifact_name`, and a `legacy_config_id` equal to the YAML basename
(without `.yaml`).
[`tests/test_product_catalog.py`](../tests/test_product_catalog.py) now
enforces that every top-level product YAML is cataloged, that no catalog
`product_yaml` points at a `products/webflash/*` wrapper, that
`legacy_config_id` values are unique and disjoint from WebFlash
`config_string` values, and that `legacy-compatible` and `blocked`
entries carry no `artifact_name`. `legacy-compatible` does **not** mean
WebFlash-shippable: [`config/webflash-builds.json`](../config/webflash-builds.json)
remains the authoritative WebFlash build matrix, and PRODUCT-002 does not
add any product to it. Release-One remains the only `production` entry;
FanTRIAC (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`) remains `blocked` per
HW-005; Sense360 LED remains excluded from Release-One.

## Legacy docs/examples

| Path | Issue | Recommended action |
|---|---|---|
| `docs/modular-combinations.md` | `Bathroom Pro` and `LED Ring` as current product names across ~30 lines. Does not mention WebFlash config strings or Release-One. | CLEANUP-003: replace with `Sense360 VentIQ` / `Sense360 LED`; add a Release-One header banner. Keep the combination tables. |
| `docs/board-combinations.md` | Section 5 "LED Rings", `Bathroom AirIQ Pro` / "Bathroom Pro" in module tables, no WebFlash framing. | CLEANUP-003. |
| `docs/product-release-matrix.md` | Pinned to release `3.0.0` / `2025-12-05`; uses `LED Ring Ceiling` / `LED Ring Wall`; no Release-One framing. | CLEANUP-003: update release header to v1.0.0, replace `LED Ring` with `Sense360 LED`. |
| `docs/product-matrix.md` lines 357, 366 | Single `Bathroom Pro` row in the SKU table and "Bathroom Pro (additional)" sub-section. (Rest of the doc is current.) | CLEANUP-003: replace with `Sense360 VentIQ`. |
| `docs/configuration.md` lines 48–89, 315–349 | Frames the Mini AirIQ / Presence variants as the primary "Product Variants" without a Release-One pointer. | CLEANUP-005: add a "Production Release-One ships `Ceiling-POE-VentIQ-RoomIQ`; this section documents legacy-compatible Mini variants" admonition; keep content. |
| `docs/development.md` lines 60, 141–148 | Lists Mini product YAMLs as the canonical local-test surface. | CLEANUP-005: add a Release-One pointer; keep the Mini list. |
| `docs/installation.md` lines 280–281 | Mini snippet in the advanced walkthrough; doc header already pins Release-One. | CLEANUP-005: minor reword. |
| `docs/ci-pipeline.md` | Repeatedly frames the broad sweep as the production release gate (see "Stale Release-One references"). | CLEANUP-002: reword. |
| `examples/customer-basic.yaml` | Long AirIQ-centric template; does not mention VentIQ or Release-One. `ref: v1.0.0` is correct. | CLEANUP-005: add a banner pointing to Release-One; keep the template body. |
| `examples/custom-with-remote-headers.yaml` | Pinned `@v2.0.0` for the C++ header API. Still legacy-compatible, but older than `v1.0.0`. | CLEANUP-006: pin to a Release-One-aware tag after verifying header API in `v1.0.0`. |
| `secrets.example.yaml` lines 42, 50 | "Required for AirIQ MQTT publishing" / "AirIQ-specific MQTT substitutions". | CLEANUP-002: reword (Release-One is VentIQ; the same vars apply). |
| `tests/INTEGRATION_GUIDE.md` lines 32–38 | Pins `@v2.0.0` / `ref: v2.0.0` for the C++ header example. | CLEANUP-006: same as `custom-with-remote-headers.yaml`. |
| `CHANGELOG.md` historical entries (3.0.0 / older) | Use legacy terminology (`Ceiling LED Ring`, `AirIQ 4-LED Status`, `Bathroom Pro`, generic `Fan`). | **No action.** Historical CHANGELOG entries describe the state at the time of release and should not be rewritten. |
| `packages/SENSE360_MODULES.md` | Mini-centric module inventory; not part of the WebFlash flow. | Defer. Revisit in CLEANUP-006. |

## Workflow/CI wording

| Path | Issue | Recommended action |
|---|---|---|
| `.github/workflows/ci-validate-configs.yml:10` | Header bullet "Test all existing product configurations (31+ products)" presents the workflow as the production gate. | CLEANUP-002: doc-only reword inside the workflow header comment; **do not** touch the workflow logic, triggers, jobs, or path filters. |
| `.github/workflows/ci-validate-configs.yml:32,40` | Path filters reference the workflow file itself — fine, leave as-is. | None. |
| `.github/workflows/validate.yml:13` | Comment "For full ESPHome compilation tests, see ci-validate-configs.yml" — accurate. | None. |
| `.github/workflows/firmware-build-release.yml` | Header comments describe the Release-One build/release flow accurately. | None. |
| README badge for `ci-validate-configs.yml` | Badge label "CI - Validate Firmware Configs" is accurate but currently implies it gates production releases. | CLEANUP-002: relabel badge or add a one-line caption ("broad legacy sweep — not the Release-One gate"). |
| `docs/ci-pipeline.md` | Whole-document framing — see "Stale Release-One references". | CLEANUP-002: reframe as "broad legacy sweep + Mini-board QA companion to `firmware-build-release.yml`". |

**Do not** in any follow-up PR:

- Change `.github/workflows/firmware-build-release.yml` job logic, build
  matrix, artifact naming, or release-asset attachment steps.
- Change `.github/workflows/ci-validate-configs.yml` job logic, dynamic
  product discovery (`find products/ -name '*.yaml' …`), path filters,
  or workflow triggers.
- Change `.github/workflows/validate.yml`.
- Remove or rename `ci-validate-configs.yml`.

## Public API / remote package risk

The following paths are reachable from customer ESPHome configurations via
`github://sense360store/esphome-public/...` URLs (or expected to be, based on
the public examples that demonstrate the pattern). They must be treated as
public API.

| Path | Evidence |
|---|---|
| `packages/base/**` | Required by every Release-One and legacy product; loaded by `external_components.yaml`. |
| `packages/features/**` | Loaded by every product YAML; example feature paths appear in `packages/README.md` snippets pinned `ref: v1.0.0`. |
| `packages/hardware/**` | Same. |
| `packages/expansions/**` | Same. |
| `base/`, `features/`, `hardware/` (top-level symlinks) | Provide a `github://.../base/...` short-form path. Likely already linked from customer configs. |
| `components/ld2412/`, `components/ld2450/`, `components/ld24xx/` | Loaded as ESPHome external components via `packages/base/external_components.yaml` (a `git` source pinning this repo). Documented in `docs/repo-structure-audit.md:51` as public API. |
| `include/sense360/**` | Consumed via `github://sense360store/esphome-public/include/sense360/*` — proven by `examples/custom-with-remote-headers.yaml:22-24` and `tests/INTEGRATION_GUIDE.md:32-38`. |
| `products/sense360-core-*.yaml`, `products/sense360-mini-*.yaml`, `products/sense360-poe.yaml`, `products/sense360-fan-pwm.yaml` | May be referenced as `github://sense360store/esphome-public/products/...` by manual users. |
| `scripts/product_name_mapper.py` | Used by `firmware-build-release.yml`. Public-ish: removing a mapping breaks unmapped-product fallback. |

Treat all of these as **do not rename / do not delete** in any cleanup PR
without a separate deprecation cycle and a release-note callout.

## Recommended cleanup PRs

Sequenced so the lowest-risk doc-wording fixes land first and the
content-change PRs land after:

1. **CLEANUP-002 — Doc-wording sync to Release-One.** Pure wording fixes,
   no logic changes.
   - `CHANGELOG.md` lines 25–34 and 46: replace
     `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` mentions in the
     `Unreleased / Added` block with `Ceiling-POE-VentIQ-RoomIQ`, or
     re-attribute those Added bullets as historical-context entries.
   - `.github/workflows/ci-validate-configs.yml` header comment (lines
     1–21): reword to "broad legacy sweep + Mini-board QA companion",
     drop "(31+ products)" framing as a release gate.
   - `docs/ci-pipeline.md` lines 3, 110, 125, 27–84: reframe so it does
     not imply the broad sweep gates production releases.
   - `secrets.example.yaml` lines 42, 50: replace AirIQ-only framing
     with a VentIQ/AirIQ-shared note.
   - `products/sense360-core-*.yaml`, `products/sense360-mini-*.yaml`
     comment headers: replace stale `ref: v2.2.0` / `ref: v3.0.0`
     example pins with `ref: v1.0.0`. Comments only — do not touch
     `substitutions` or `packages` blocks.
   - README badge caption for `ci-validate-configs.yml`.

2. **CLEANUP-003 — Legacy-naming docs sweep.** Apply the
   canonical → old-name mapping in user-facing docs.
   - `docs/modular-combinations.md`, `docs/board-combinations.md`,
     `docs/product-matrix.md` (line 357 + line 366),
     `docs/product-release-matrix.md`: replace `Bathroom Pro` →
     `Sense360 VentIQ` and `LED Ring (Ceiling|Wall)` →
     `Sense360 LED (Ceiling|Wall)`. Add a Release-One header banner
     stating that none of these docs override
     `Ceiling-POE-VentIQ-RoomIQ`.
   - Keep the canonical-name table column in
     `docs/hardware-catalog.md:30`, the `old_name` field in
     `config/hardware-catalog.json`, and the `led_ring_*` filenames in
     `packages/hardware/`. These are part of public API or public
     reference.

3. **CLEANUP-004 — `docs/*.html` decision.** Six files:
   `docs/architecture.html`, `docs/configuration.html`,
   `docs/index.html`, `docs/installation.html`,
   `docs/product-guide.html`, `docs/technical-reference.html`.
   These are stale snapshots whose Markdown twins (`configuration.md`,
   `installation.md`) have been updated. Recommended decision matrix:
   - If an HTML pipeline exists outside this repo that regenerates these
     from the Markdown, regenerate.
   - Otherwise, prepend a one-line legacy banner to each HTML head
     section pointing to the Markdown source-of-truth.
   - Only consider removal after confirming the files are not served by
     a Pages / docs site and not linked from any external resource. No
     internal `*.md`, `*.yaml`, `*.py`, or workflow inside the repo
     links these HTML files (the only references are inside the HTML
     files themselves, plus a follow-up note in
     `docs/repo-structure-audit.md`).

4. **CLEANUP-005 — Examples / Mini section refresh.** Doc framing only.
   - `examples/customer-basic.yaml`: add a "this is a customer template;
     production Release-One ships `Ceiling-POE-VentIQ-RoomIQ`" banner.
   - `docs/configuration.md` lines 48–89, 315–349: add a Release-One
     pointer to the Mini section; keep content.
   - `docs/development.md` lines 60, 141–148: add a Release-One pointer
     to the Mini-test list.
   - `docs/installation.md:280-281`: minor reword.

5. **CLEANUP-006 — Header / version refresh.** Lowest priority.
   - `examples/custom-with-remote-headers.yaml` and
     `tests/INTEGRATION_GUIDE.md`: pin to a Release-One-aware tag after
     verifying the C++ header API is published in `v1.0.0`.
   - Consider trimming `packages/SENSE360_MODULES.md` after CLEANUP-002
     – CLEANUP-005 land.

## Do-not-delete list

These paths must **not** be deleted by any of the cleanup PRs above
without a separate, explicit deprecation cycle. Many are public-API or
remote-package surfaces, blocked-reference files retained pending
HW-005, or load-bearing for the broad legacy CI sweep.

```
products/sense360-ceiling-poe-ventiq-roomiq.yaml
products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml    # blocked-reference
products/webflash/ceiling-poe-ventiq-roomiq.yaml
products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml    # blocked-reference
products/sense360-core-*.yaml                                # legacy-compatible
products/sense360-mini-*.yaml                                # legacy-compatible
products/sense360-poe.yaml                                   # legacy-compatible
products/sense360-fan-pwm.yaml                               # legacy-compatible
packages/base/**
packages/features/**
packages/hardware/**
packages/expansions/**                                       # incl. fan_triac.yaml (blocked-reference)
packages/README.md
packages/SENSE360_MODULES.md
base/, features/, hardware/                                  # top-level symlinks (public-API short form)
components/ld2412/, components/ld2450/, components/ld24xx/
include/sense360/**, include/README.md
config/webflash-builds.json
config/webflash-compatibility.json
config/hardware-catalog.json
.github/workflows/firmware-build-release.yml
.github/workflows/ci-validate-configs.yml
.github/workflows/validate.yml
scripts/check-webflash-release-assets.py
scripts/check-no-tracked-secrets.py
scripts/product_name_mapper.py
scripts/validate-webflash-release-notes.py
tests/**                                                     # tests + generators + Makefile + READMEs
examples/customer-basic.yaml
examples/custom-with-remote-headers.yaml
examples/secrets.yaml.template
secrets.example.yaml
README.md
CHANGELOG.md
docs/release-one.md
docs/release-one-hardware-audit.md
docs/webflash-contract.md
docs/webflash-ci-alignment.md
docs/webflash-release-handoff.md
docs/webflash-release-proof.md
docs/installation.md
docs/configuration.md
docs/development.md
docs/product-matrix.md
docs/hardware-catalog.md
docs/manual-user-walkthrough.md
docs/repo-structure-audit.md
docs/hardware/s360-100-r4-core.md
docs/hardware/s360-200-r4-roomiq.md
```

## Validation

The following commands were run against the working tree after writing
this document. None of them should be affected by the addition of a
docs-only audit file, and all `current`-classified tests continue to
pass.

```
python3 tests/validate_webflash_builds.py
python3 tests/test_webflash_compatibility.py
python3 tests/test_webflash_artifact_naming.py
python3 tests/test_validate_webflash_release_notes.py
python3 tests/test_product_substitutions.py
python3 tests/test_release_one_entity_names.py
python3 tests/validate_configs.py
pre-commit run --all-files   # if available
yamllint .                   # if available
```

Results are captured in the commit body for the PR that introduces this
document.

## What this PR does NOT change

- No WebFlash config strings, artifact names, or build-matrix entries.
- No release workflow behavior, no firmware behavior, no signing or
  manifest changes.
- No edits to `products/*.yaml`, `packages/**`, `config/*.json`,
  `.github/workflows/*`, `scripts/*`, or `tests/*`.
- No FanTRIAC unblock; FanTRIAC remains excluded from production
  Release-One pending HW-005.
- No removal of LED packages or `led_ring_*.yaml` filenames; LED remains
  excluded from Release-One because the config string does not contain
  the `LED` token.
- No deletion of `docs/*.html`. The HTML decision is deferred to
  CLEANUP-004.
- No `CHANGELOG.md` edits — the stale `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`
  mention in the `Unreleased / Added` block is recorded above and
  deferred to CLEANUP-002.

## CLEANUP-003 update (legacy naming docs sweep)

This section records what CLEANUP-003 actually swept. It does **not**
rewrite the audit above. Findings and recommendations recorded earlier
in this document remain accurate; the entries below summarise the
applied changes.

### Files swept (docs/comments only)

| Path | Sweep |
|---|---|
| `docs/modular-combinations.md` | Added Release-One scope banner + legacy-naming banner. Replaced `Bathroom Pro` → `Sense360 VentIQ` in current-tense tables. Tagged `Bathroom Base` as `*(legacy, retired)*` in definition tables. Replaced LED-Ring section heading + per-row product labels with `Sense360 LED`. |
| `docs/board-combinations.md` | Added Release-One + legacy-naming banner. Replaced `Bathroom AirIQ Pro` → `Sense360 VentIQ` and tagged `Bathroom AirIQ Base` as `*(legacy, retired)*`. Replaced section 5 heading `LED Rings` → `Sense360 LED`; updated ASCII decision tree, power-budget row, and file-reference table to use `Sense360 LED` / `Sense360 VentIQ`. Updated the Example 3 `Bathroom AirIQ Pro Module` comment to call out the canonical name. |
| `docs/product-matrix.md` | Updated TOC + section heading `LED Rings` → `Sense360 LED` (anchor `#sense360-led`). Updated Step 3 heading, ASCII assembly diagram, YAML example comment, and SKU → Package mapping label. Renamed the `Bathroom Module` heading to `Sense360 VentIQ (Bathroom) Module`; renamed the SKU-row entry `Sense360_Module_Bathroom_Pro` / "Sense 360 Bathroom Pro" to `Sense360_Module_VentIQ` / "Sense360 VentIQ"; flagged `Sense360_Module_Bathroom_Base` row as `*(legacy, retired)*`. |
| `docs/product-release-matrix.md` | Refreshed the stale `v3.0.0 / 2025-12-05` release header to current Release-One v1.0.0 framing (with explicit "not a historical release matrix" caveat). Section 3 heading `LED Attachments` → `Sense360 LED Attachments`; product labels `LED Ring Ceiling/Wall` → `Sense360 LED (Ceiling)/(Wall)`. Refreshed install example refs from `v3.0.0` to `v1.0.0` and the canonical Release-One product YAML. Flagged the `S360-BATH-C` row as a legacy SKU pending a separate SKU / catalog audit. |

### Legacy aliases intentionally preserved

The following references are **clearly labelled legacy / old_name /
schematic / compatibility references** and are preserved on purpose. No
sweep was applied to them.

- `config/hardware-catalog.json` — `old_name` JSON fields (e.g.
  `"Bathroom Pro"` for `S360-211`, `"LED Ring"` for `S360-300`).
- `docs/hardware-catalog.md` — canonical-name table with "Old name"
  column (`LED Ring` / `Bathroom Pro`).
- `docs/hardware/s360-100-r4-core.md` — explicit `Old name: LED Ring`
  rows tied to schematic-level discussion.
- `docs/release-one-hardware-audit.md` — explicit "Old name: `Bathroom
  Pro`. Do not reuse `Bathroom Pro` in new user-facing material" guidance
  (and surrounding context).
- `docs/webflash-contract.md` — legacy → WebFlash mapping table
  (`Bathroom` → `VentIQ`, `LED` → S360-300, etc.).
- `docs/webflash-ci-alignment.md` — legacy-token discussion (the
  ESP-009 inventory bullet).
- `packages/README.md` — `### Bathroom (legacy → WebFlash VentIQ)`
  section header and adjacent legacy-mapping commentary.
- `docs/manual-user-walkthrough.md` — "Sense360 LED (ceiling LED ring)
  is excluded from Release-One firmware" framing.
- `CHANGELOG.md` — historical entries (3.0.0 and earlier) that mention
  `Ceiling LED Ring`, `LED ring`, `Bathroom Pro`. Historical changelog
  entries describe the state at the time of release and were not
  rewritten.
- `packages/SENSE360_MODULES.md` — register-map context (`0x59 |
  GP8403 alt, SGP40 (Bathroom)`).
- `docs/architecture.html`, `docs/configuration.html`,
  `docs/product-guide.html`, `docs/technical-reference.html` —
  HTML doc snapshots; decision deferred to CLEANUP-004.
- Package and product YAML filenames + YAML-internal comments
  (`packages/hardware/led_ring_*.yaml`,
  `packages/features/ceiling_led_ring_air_quality.yaml`,
  `packages/expansions/airiq_bathroom_*.yaml`,
  `products/sense360-core-ceiling*.yaml`, etc.) — preserved as public
  API / remote-package surface per the recommendation above.

### Bathroom Base treatment

`Bathroom Base` (`S360-BATH-B`) has **no canonical successor** in
`docs/hardware-catalog.md`. Per CLEANUP-003 decision, the term was
**not** silently collapsed into `Sense360 VentIQ`. Where it appears as a
current-tense product label in user-facing docs, it is now annotated as
a retired legacy bathroom SKU (`*(legacy, retired)*`) in the relevant
definition tables. A separate SKU / catalog audit is needed to decide
whether `Bathroom Base` should be removed from the docs entirely or
formally cataloged.

### Out of scope (unchanged by CLEANUP-003)

CLEANUP-003 is docs/comments only. The following remain untouched:

- `products/*.yaml`, `products/webflash/*.yaml`, `packages/*.yaml`.
- `config/webflash-builds.json`, `config/webflash-compatibility.json`,
  `config/hardware-catalog.json` (including `old_name` fields).
- `.github/workflows/*`, `scripts/*`, `tests/*`, `components/*`,
  `include/*`.
- File renames (none performed).
- WebFlash config strings, artifact names, build matrix, firmware
  package IDs, hardware SKUs.
- FanTRIAC blocked status (remains blocked pending HW-005).
- LED exclusion status (remains excluded from Release-One).
- HTML doc snapshots in `docs/*.html` (deferred to CLEANUP-004).

### Validation run for CLEANUP-003

The commands at the top of this document, plus the sanity greps below,
were re-run after the sweep. Results are captured in the commit body
for the CLEANUP-003 PR.

```text
grep -RIn "Celling"      README.md CHANGELOG.md docs examples packages products config tests scripts
grep -RIn "AirlQ"        README.md CHANGELOG.md docs examples packages products config tests scripts
grep -RIn "Bathroom Pro" README.md CHANGELOG.md docs examples packages products config tests scripts
grep -RIn "LED Ring"     README.md CHANGELOG.md docs examples packages products config tests scripts
```

Any remaining `Bathroom Pro` / `LED Ring` hits after the sweep are
clearly framed as legacy / old_name / schematic / compatibility /
historical references in the locations listed under "Legacy aliases
intentionally preserved" above.

## CLEANUP-004 update (HTML docs decision)

This section records what CLEANUP-004 actually did. As with the
CLEANUP-003 update above, it does **not** rewrite the audit earlier in
this document. The "Findings summary" rows at lines 169–174, the
"Recommended cleanup PRs" item at lines 476–491, the "What this PR does
NOT change" bullet at lines 602–603, the "Out of scope" bullet at
line 688, and the "Legacy aliases intentionally preserved" entry at
lines 653–655 (four HTML files deferred to CLEANUP-004) all remain
accurate as historical records; the entry below summarises the applied
change and supersedes those `CLEANUP-004 decision` placeholders.

### Decision: remove

All six `docs/*.html` files were **deleted**:

- `docs/architecture.html`
- `docs/configuration.html`
- `docs/index.html`
- `docs/installation.html`
- `docs/product-guide.html`
- `docs/technical-reference.html`

### Rationale

The "preferred — remove unused stale HTML" branch of the CLEANUP-004
decision policy applied cleanly. All four conditions held simultaneously:

1. **Not generated by any repo pipeline.** No `mkdocs.yml`,
   `_config.yml`, `package.json`, `Gemfile`, or `conf.py` exists in the
   repo. No workflow under `.github/workflows/` references `.html`, and
   no entry in `scripts/` does either.
2. **Not linked from `README.md` or any current Markdown doc.** The
   only inbound references in the repo were the HTML cluster's own
   internal cross-links (`index.html` ↔ `product-guide.html` ↔ etc.)
   and the audit-narrative mentions inside this file and
   `docs/repo-structure-audit.md`. `README.md:411-412` only links the
   Markdown twins (`docs/installation.md`, `docs/configuration.md`).
3. **Not served by any GitHub Pages / docs workflow from this repo.**
   The HTML cluster was added in a single commit titled "Add GitHub
   Pages documentation site", but GitHub Pages was never wired up here:
   no Pages config in `.github/`, no `gh-pages` branch, no deploy
   workflow. The lone `sense360store.github.io/...` link in the HTML
   pointed to the *WebFlash* repo's Pages site, not this repo's.
4. **Contradicted current Release-One Markdown.** The HTML files
   predated the Release-One framing entirely — no `Release-One` /
   `Ceiling-POE-VentIQ-RoomIQ` string in any of them; they still framed
   `Sense360 Mini` as the primary product
   (`architecture.html`, `technical-reference.html`,
   `product-guide.html`) and used the retired `LED Ring` / `S360-LED-*`
   SKU names (`architecture.html`, `technical-reference.html`).

Adding a legacy banner was the runner-up option but would have left six
stale documents in the tree and a half-broken HTML cluster pointing to
a Pages site that does not exist. Regeneration was not considered: no
generator pipeline exists in this repo, and the task explicitly
forbids inventing one in this PR.

### Markdown links repaired

None. No `.md`, `.yaml`, `.py`, or workflow file inside the repo linked
the deleted HTML files, so no Markdown link repair was required.
`README.md` and the Markdown twins (`docs/installation.md`,
`docs/configuration.md`, etc.) are unchanged. `docs/cleanup-audit.md`
(this file) and `docs/repo-structure-audit.md` retain their historical
mentions of the HTML filenames as audit-narrative; that is the intended
record of the CLEANUP-004 decision and was not rewritten.

### Out of scope (unchanged by CLEANUP-004)

CLEANUP-004 is HTML-doc removal only. The following remain untouched:

- `products/*.yaml`, `products/webflash/*.yaml`, `packages/*.yaml`.
- `config/webflash-builds.json`, `config/webflash-compatibility.json`,
  `config/hardware-catalog.json` (including `old_name` fields).
- `.github/workflows/*`, `scripts/*`, `tests/*`, `components/*`,
  `include/*`.
- WebFlash config strings, artifact names, build matrix, firmware
  package IDs, hardware SKUs.
- FanTRIAC blocked status (remains blocked pending HW-005).
- LED exclusion status (remains excluded from Release-One).
- `README.md`, current Release-One Markdown docs, and
  `docs/repo-structure-audit.md`.

### Validation run for CLEANUP-004

After the deletions the test suite listed at the top of this document
was re-run, together with the sanity greps below. Results are captured
in the commit body for the CLEANUP-004 PR.

```text
find docs -maxdepth 1 -name "*.html" -print
grep -RIn "\.html" README.md docs .github scripts package.json mkdocs.yml _config.yml 2>/dev/null || true
```

After the sweep, the `find` returns nothing and the `grep` returns only
unrelated `.html` mentions (the SemVer URL at
`docs/webflash-contract.md:53`, the googletest URL at
`tests/README.md:383`) plus the audit-narrative mentions inside this
file and `docs/repo-structure-audit.md` that record the CLEANUP-004
decision history.

## CLEANUP-005 update (examples refresh)

This section records what CLEANUP-005 actually swept. As with the
CLEANUP-003 and CLEANUP-004 updates above, it does **not** rewrite the
audit earlier in this document. The "Findings summary" rows for the
files listed below remain accurate as historical records; the entry
below summarises the applied changes and supersedes the
`Reword in CLEANUP-005` / `refresh wording in CLEANUP-005` placeholders.

### Goal

Refresh user-facing examples and Mini-centric doc sections so that
production Release-One (`Ceiling-POE-VentIQ-RoomIQ`) is the leading
default, while preserving legacy-compatible Mini / AirIQ / custom
examples as clearly-labelled alternatives.

### Files swept (docs / examples only)

| Path | Sweep |
|---|---|
| `examples/customer-basic.yaml` | Restructured: replaced the Mini-centric header with a Release-One-leading banner; flipped the active default include to `products/sense360-ceiling-poe-ventiq-roomiq.yaml` (OPTION 0); demoted the four Mini variants to commented-out alternatives (OPTIONS 1–4) explicitly labelled `legacy`; bumped `min_version` `2024.11.0` → `2025.10.0` to match Release-One; reworded the MQTT/Required-for-AirIQ framing to AirIQ / VentIQ; refreshed the bottom "Quick Start" guide so STEP 1 explains OPTION 0 vs the Mini options. Body and threshold-customisation examples preserved. |
| `examples/custom-with-remote-headers.yaml` | Prepended a top-of-file banner: "Advanced / custom example — NOT the Release-One path." Points readers at `examples/customer-basic.yaml` and `docs/release-one.md`. The `@v2.0.0` C++ header pin is **not** changed (deferred to CLEANUP-006 per the audit); the banner explains why it predates the Release-One firmware tag `v1.0.0`. |
| `examples/secrets.yaml.template` | No change. Already a 9-line pointer to `secrets.example.yaml`. |
| `secrets.example.yaml` | Reworded line-42 "MQTT CREDENTIALS (required for AirIQ MQTT publishing)" → "(required for AirIQ / VentIQ MQTT publishing)", and the line-50 "AirIQ-specific MQTT substitutions" comment → "AirIQ / VentIQ MQTT substitutions" with a Release-One note that the same vars cover both modules. No variable names changed. (This was assigned to CLEANUP-002 in the audit; bringing it forward keeps the secrets template consistent with the customer-basic example.) |
| `docs/configuration.md` | Inserted a Release-One pointer admonition before `### Product Variants`, plus a new `#### Release-One — Ceiling-POE-VentIQ-RoomIQ (Recommended)` sub-section that points at the canonical product YAML. Suffixed the four Mini/Ceiling sub-headings with `— _legacy-compatible_`. Inserted a Sense360-LED-excluded admonition before `### Night Mode and LED Controls` and suffixed `#### Mini Night Brightness` with `— _legacy-compatible (Mini board only)_`. Suffixed `#### Mini Board Default Pins` similarly and added a pointer to `docs/hardware/s360-100-r4-core.md` for Release-One pin reference. Added a "this is not the Release-One path" preamble to `### Component-Level Customization` and tagged its `sense360_core_mini.yaml` hardware line accordingly. Content (thresholds, automations, scenarios) preserved. |
| `docs/development.md` | Replaced the canonical `esphome config products/sense360-mini-airiq.yaml` example with a two-snippet pair: Release-One first (`sense360-ceiling-poe-ventiq-roomiq.yaml`), Mini second (labelled legacy). Above the "Matrix testing" list, inserted a banner clarifying that `firmware-build-release.yml` is the Release-One gate and the matrix below is the broad legacy sweep run by `ci-validate-configs.yml`. Added the Release-One YAML as the first entry in the matrix list and suffixed each Mini / Ceiling-presence entry with `— _legacy-compatible_`. List itself preserved. |
| `docs/installation.md` | Reworded the "Change Product Variant" snippet so the active uncommented file is `sense360-ceiling-poe-ventiq-roomiq.yaml` (Release-One) and the three Mini / Ceiling-presence YAMLs become commented-out alternatives flagged as legacy. Reworded the "MQTT Credentials (required for AirIQ MQTT publishing)" comment line and the matching "AirIQ-enabled product" sentence to mention `AirIQ / VentIQ`. |
| `packages/README.md` | Inserted a Release-One pointer at the top (above the existing WebFlash-compatibility note) so the package README leads with `Ceiling-POE-VentIQ-RoomIQ`. Reworded the "Using Pre-Built Products" example so the active product is `sense360-ceiling-poe-ventiq-roomiq.yaml`. Added a "this is a legacy-compatible custom build" preamble to the "Custom Module Combinations" example and inline-tagged the `airiq_ceiling.yaml` / `led_ring_ceiling.yaml` lines to call out that AirIQ + LED are not in Release-One. Section bodies preserved. |
| `packages/SENSE360_MODULES.md` | Prepended a top-of-file admonition labelling the whole document as a legacy / advanced module inventory and pointing at `docs/release-one.md` and `docs/hardware-catalog.md`. Body content (pin reference, module descriptions, examples) preserved. Defer fuller content revisit to CLEANUP-006. |

### Files not touched

- `README.md` — already leads with Release-One, the FanTRIAC-excluded
  callout, and a "Legacy Terminology" table. No CLEANUP-005-shaped edit
  needed.
- `docs/manual-user-walkthrough.md` — already pinned to Release-One with
  explicit FanTRIAC / LED exclusion language.

### Legacy aliases intentionally preserved

The following references remain on purpose, in line with the
"Legacy aliases intentionally preserved" lists for CLEANUP-003 /
CLEANUP-004:

- The four legacy Mini OPTION blocks in `examples/customer-basic.yaml`
  are kept (commented out) so users with older Mini hardware still have
  a working manual-flash template.
- The Mini sub-sections in `docs/configuration.md` and the Mini matrix
  entries in `docs/development.md` are kept (with `_legacy-compatible_`
  labels) so customers running Mini hardware can still find their docs.
- The `@v2.0.0` header pin in `examples/custom-with-remote-headers.yaml`
  is intentionally retained; the C++ header API is stable across
  `v2.0.0` and the Release-One `v1.0.0` firmware tag. Re-pinning is
  deferred to CLEANUP-006 (audit row at lines 388, 390, 503–505).
- `packages/SENSE360_MODULES.md` body content is not restructured;
  fuller revisit is deferred to CLEANUP-006 (audit row at lines 392, 506–507).
- Legacy filenames (`comfort_*.yaml`, `airiq_bathroom_*.yaml`,
  `led_ring_*.yaml`, `sense360_core_mini.yaml`, etc.) remain unchanged —
  these are public API / remote-package surfaces.

### Out of scope (unchanged by CLEANUP-005)

CLEANUP-005 is docs / examples wording only. The following remain
untouched:

- `products/*.yaml`, `products/webflash/*.yaml`, `packages/*.yaml`.
- `config/webflash-builds.json`, `config/webflash-compatibility.json`,
  `config/hardware-catalog.json` (including `old_name` fields).
- `.github/workflows/*`, `scripts/*`, `tests/*`, `components/*`,
  `include/*`.
- File renames (none performed).
- WebFlash config strings, artifact names, build matrix, firmware
  package IDs, hardware SKUs.
- FanTRIAC blocked status (remains blocked pending HW-005).
- LED exclusion status (remains excluded from Release-One).

### Validation run for CLEANUP-005

The commands at the top of this document, plus the sanity greps below,
were re-run after the sweep. Results are captured in the commit body
for the CLEANUP-005 PR.

```text
python3 tests/validate_webflash_builds.py
python3 tests/test_webflash_compatibility.py
python3 tests/test_webflash_artifact_naming.py
python3 tests/test_validate_webflash_release_notes.py
python3 tests/test_product_substitutions.py
python3 tests/test_release_one_entity_names.py
python3 tests/validate_configs.py

grep -RIn "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ" examples README.md docs packages secrets.example.yaml
grep -RIn "FanTRIAC"                            examples README.md docs packages secrets.example.yaml
grep -RIn "LED Ring"                            examples README.md docs packages secrets.example.yaml
grep -RIn "Bathroom Pro"                        examples README.md docs packages secrets.example.yaml
grep -RIn "customer-basic"                      examples README.md docs packages secrets.example.yaml
```

After the sweep, any remaining hits for `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`,
`FanTRIAC`, `LED Ring`, or `Bathroom Pro` are clearly framed as
blocked-reference, legacy / old_name, schematic, historical-context, or
compatibility references in the locations listed under "Legacy aliases
intentionally preserved" (CLEANUP-003 + CLEANUP-005) above.

## CLEANUP-006 update (remote header / pinned version refresh)

This section records what CLEANUP-006 actually swept. As with the
CLEANUP-003, CLEANUP-004, and CLEANUP-005 updates above, it does **not**
rewrite the audit earlier in this document. The "Findings summary" rows
at lines 157, 175, 388, 390, and the "Recommended cleanup PRs" entry at
lines 502–507 remain accurate as historical records; the entry below
summarises the applied changes and supersedes the
`pin to a Release-One-aware tag in CLEANUP-006` placeholders for the
files that were actually in scope for this PR.

### Goal

Audit the remote-package / external-header examples in user-facing
docs and examples, and decide whether each pinned version reference
should be re-pinned to current Release-One (`v1.0.0`), kept as an
explicit legacy example, replaced with a `<release-tag>` placeholder,
or carry a clearer pinning warning. The goal is to prevent users from
copying stale remote-package examples without understanding they are
advanced / legacy paths.

Before any edits, the C++ header API at `v1.0.0` was verified to
contain every symbol used in
`examples/custom-with-remote-headers.yaml`
(`compute_level`, `color_for_severity`, `LEVEL_POOR`,
`compute_pulse_multiplier`, `scale_color`, `classify_value`,
`PM25_GOOD` / `PM25_MODERATE` / `PM25_UNHEALTHY`, `AirQualityStatus`,
`status_to_string`, `CalibrationResult`,
`compute_single_point_calibration`, `Time`, `is_within_night_mode`),
confirmed via `git show v1.0.0:include/sense360/*.h`. Re-pinning the
example to `@v1.0.0` therefore does not break the lambda body.

### Files swept (docs / examples only)

| Path | Sweep |
|---|---|
| `examples/custom-with-remote-headers.yaml` | Re-pinned the three `includes:` lines from `@v2.0.0` to `@v1.0.0` so the example matches the Release-One firmware tag. Inserted a guidance comment block above the `includes:` list explaining how to substitute another tag for future releases, with a `@<release-tag>` placeholder shape. Updated the top-of-file banner (the "predates the Release-One firmware tag `v1.0.0`" sentence) to reflect the new pin. No lambda, sensor, package, or `min_version` changes — the `min_version: 2025.10.0` already matches Release-One. |
| `docs/product-matrix.md` | Inserted a "Legacy examples" admonition immediately above `### Example 1: Core Ceiling with Full Monitoring` (the start of the three "Configuration Examples" snippets that pin `ref: v2.2.0`). The admonition explains that the snippets intentionally pin to the historical `v2.2.0` tag for legacy Core/Wall/Bathroom package examples, that current Release-One WebFlash firmware is `Ceiling-POE-VentIQ-RoomIQ` at `v1.0.0`, and that custom / manual users should pin to a known-compatible release tag and never use `ref: main` for production. The three `ref: v2.2.0` lines themselves are **not changed** — Release-One `v1.0.0` has not been proven as the baseline for those legacy package paths, so re-pinning would be misleading. |
| `docs/installation.md` | Replaced the "Wireless Updates → Update your configuration" placeholder `ref: v2.2.0  # Change to the new version number` with `ref: <new-release-tag>  # Example: v1.0.0. Replace with the release tag you are updating to.`. This block is an update-to-future-tag instruction, not a working copy-paste, so a generic placeholder is more appropriate than a concrete pin that would re-stale next release. |

### Files not touched

The following files were inspected and confirmed to need no
CLEANUP-006-shaped edit:

- `examples/customer-basic.yaml` — `ref: v1.0.0` is already current
  Release-One; banner / structure already refreshed in CLEANUP-005.
- `README.md` — every `ref:` snippet (lines 24, 269, 303, 317, 344)
  already pins `v1.0.0`; the production-vs-`main` warning is already
  present.
- `docs/configuration.md` — every `ref:` snippet (lines 71, 93, 443,
  607) already pins `v1.0.0`; the `ref: main` development-only example
  at line 622 is explicitly framed as "Development only — never for
  production devices".
- `docs/release-one.md` — `ref: v1.0.0` snippet at line 193 already
  current.
- `docs/manual-user-walkthrough.md` — "Suggested ref / tag: `v1.0.0`"
  scope table at line 36 already current.
- `docs/development.md` — no remote-package pins in the doc body
  (only the `git clone` URL); nothing to re-pin.
- `docs/product-release-matrix.md` — `ref: v1.0.0` snippets at lines
  261 and 309 already current.
- `packages/README.md` — `ref: v1.0.0` snippets at lines 91 and 121
  already current after CLEANUP-005.
- `packages/SENSE360_MODULES.md` — no `ref:` or `@vX` pins to audit.
  The deeper "Mini-centric module inventory revisit" deferred at the
  end of CLEANUP-005 remains deferred; the task scope here was
  remote-package pins, not module-inventory rewording.
- `CHANGELOG.md` — every `ref: vX` / `ref: main` mention is historical
  narrative ("`ref: v3.0.0` with `ref: main`", etc.) describing past
  releases. Historical changelog entries are not rewritten.
- `docs/repo-structure-audit.md` — the `@v2.0.0` mentions at lines 52
  and 113 are descriptive prose recording the public-API surface at
  the time the audit was written. Historical-snapshot doc; not
  rewritten, mirroring the CLEANUP-005 pattern of leaving earlier
  audit rows intact.

### Legacy pins intentionally preserved

The following references remain on purpose, in line with the
"Legacy aliases intentionally preserved" lists for CLEANUP-003 /
CLEANUP-004 / CLEANUP-005:

- The three `ref: v2.2.0` snippets in `docs/product-matrix.md` lines
  601, 631, 661 (`Example 1: Core Ceiling with Full Monitoring`,
  `Example 2: Core Wall with All Sensors`,
  `Example 3: Core Ceiling Bathroom Installation`). Re-pinning to
  `v1.0.0` would imply Release-One `v1.0.0` has been proven against
  the legacy Core / Wall / Bathroom product YAML set, which it has
  not. Instead, a "Legacy examples" admonition was added above them.
- The `ref: main` development-only example in `docs/configuration.md`
  line 622 is intentionally retained as a maintainer-testing example,
  with the explicit "Never for production devices" warning preserved
  above it.
- The `ref: main` internal-loader references in
  `packages/base/external_components.yaml:26` and
  `products/sense360-mini-full-ld2412.yaml:99` are internal
  self-references inside the repo, not user copy-paste examples, and
  are out of CLEANUP-006 scope (`packages/*.yaml` and
  `products/*.yaml` are in the "do not edit" list).

### Deferred / out of scope

The following `@v2.0.0` / `ref: v2.0.0` references are still in the
repo after CLEANUP-006. They are recorded here as a deferred follow-up
rather than fixed in this PR, because the directories that contain
them are in the CLEANUP-006 task's explicit "do not change" list:

- `include/README.md` lines 79–80 — Header API usage example showing
  `@v2.0.0`. Out of scope: `include/*` is reserved. A future PR with
  scope for `include/*` should re-pin these to `@v1.0.0` to match
  `examples/custom-with-remote-headers.yaml`.
- `tests/INTEGRATION_GUIDE.md` lines 32–38 — Integration guide for
  the C++ header API, pinning `@v2.0.0` / `ref: v2.0.0`. Out of
  scope: `tests/*` is reserved. The original audit row paired this
  file with `custom-with-remote-headers.yaml` for CLEANUP-006; only
  the example file was actually in scope this round.
- `products/sense360-core-*.yaml` and `products/sense360-mini-*.yaml`
  comment-block `ref: v2.2.0` / `ref: v3.0.0` example pins (lines 21,
  24, 26, 28, 29, 103, 145, 258, 358, 474 across the affected files).
  Already tracked under CLEANUP-002 in the audit rows at lines 143,
  144, and 207–209; `products/*.yaml` is out of CLEANUP-006 scope.

### Out of scope (unchanged by CLEANUP-006)

CLEANUP-006 is docs / examples wording and example-pin alignment only.
The following remain untouched:

- `products/*.yaml`, `products/webflash/*.yaml`, `packages/*.yaml`.
- `config/webflash-builds.json`, `config/webflash-compatibility.json`,
  `config/hardware-catalog.json` (including `old_name` fields).
- `.github/workflows/*`, `scripts/*`, `tests/*`, `components/*`,
  `include/*`.
- File renames (none performed).
- WebFlash config strings, artifact names, build matrix, firmware
  package IDs, hardware SKUs.
- FanTRIAC blocked status (remains blocked pending HW-005).
- LED exclusion status (remains excluded from Release-One).

### Validation run for CLEANUP-006

The commands at the top of this document, plus the sanity greps below,
were re-run after the sweep. Results are captured in the commit body
for the CLEANUP-006 PR.

```text
python3 tests/validate_webflash_builds.py
python3 tests/test_webflash_compatibility.py
python3 tests/test_webflash_artifact_naming.py
python3 tests/test_validate_webflash_release_notes.py
python3 tests/test_product_substitutions.py
python3 tests/test_release_one_entity_names.py
python3 tests/validate_configs.py

grep -RIn "@v[0-9]"                              README.md docs examples packages products include components CHANGELOG.md
grep -RIn "ref: main"                            README.md docs examples packages products include components CHANGELOG.md
grep -RIn "ref: v"                               README.md docs examples packages products include components CHANGELOG.md
grep -RIn "github://sense360store/esphome-public" README.md docs examples packages products include components CHANGELOG.md
```

After the sweep, the remaining `@v[0-9]`, `ref: v`, and `ref: main`
hits are clearly framed as one of:

- current Release-One pins (`@v1.0.0` / `ref: v1.0.0`) in
  `examples/custom-with-remote-headers.yaml`, `examples/customer-basic.yaml`,
  `README.md`, `docs/configuration.md`, `docs/installation.md`,
  `docs/release-one.md`, `docs/product-release-matrix.md`,
  `docs/manual-user-walkthrough.md`, `packages/README.md`;
- intentionally-legacy pins (`ref: v2.2.0` in `docs/product-matrix.md`
  Examples 1–3) under the new "Legacy examples" admonition;
- deferred follow-ups (`@v2.0.0` in `include/README.md` and
  `tests/INTEGRATION_GUIDE.md`; stale `ref: v2.2.0` / `ref: v3.0.0`
  comment headers in `products/sense360-core-*.yaml` and
  `products/sense360-mini-*.yaml`) explicitly listed above;
- historical audit / changelog prose (`docs/cleanup-audit.md`,
  `docs/repo-structure-audit.md`, `CHANGELOG.md`) which is not
  rewritten;
- production-warning text in `README.md`, `docs/configuration.md`,
  `docs/webflash-release-handoff.md`, and `CHANGELOG.md` that
  explicitly cautions against `ref: main` in production; the
  maintainer-only `ref: main` example at `docs/configuration.md:622`;
  and the in-repo `ref: main` self-references in
  `packages/base/external_components.yaml:26` and
  `products/sense360-mini-full-ld2412.yaml:99` (internal loader
  paths, not user copy-paste examples).

## PRODUCT-003 update (add-product validator)

PRODUCT-003 adds a read-only product-catalog consistency validator and a
companion unit-test suite. It does not change any product, wrapper, package,
build matrix, compatibility JSON, hardware catalog, artifact name, mapper,
Release-One config, FanTRIAC blocked status, or LED exclusion status.

### Files added

- `scripts/validate_product_catalog_consistency.py` — read-only validator.
  Cross-checks `config/product-catalog.json` against
  `config/webflash-builds.json`, `config/webflash-compatibility.json`,
  `config/hardware-catalog.json`, `scripts/product_name_mapper.py`, and the
  product / wrapper YAML paths. Supports `--checklist
  <CONFIG_STRING_OR_LEGACY_ID>` and `--product <PATH>` modes for the
  add-product workflow.
- `tests/test_product_catalog_consistency.py` — stdlib `unittest` suite that
  asserts: the current repo state passes; Release-One passes every
  production-specific check; FanTRIAC passes every blocked-specific check;
  every legacy-compatible entry stays non-WebFlash-shippable; the mapper
  agrees with every production entry's declared `artifact_name`; every
  WebFlash-eligible entry's wrapper basename equals lowercased
  `config_string`; and the checklist mode resolves real entries cleanly.

### CI wiring

`.github/workflows/validate.yml` runs both new commands after the existing
`Validate product catalog` step:

```text
python3 scripts/validate_product_catalog_consistency.py
python3 tests/test_product_catalog_consistency.py
```

### Out of scope (unchanged by PRODUCT-003)

- `products/*.yaml`, `products/webflash/*.yaml`, `packages/**`
- `config/webflash-builds.json`, `config/webflash-compatibility.json`,
  `config/hardware-catalog.json`, `config/product-catalog.json`
- `scripts/product_name_mapper.py`
- `tests/test_product_catalog.py` (kept as-is; new validator is additive)
- Release-One config string, artifact name, build matrix, hardware SKUs
- FanTRIAC blocked status, LED exclusion status

## PRODUCT-DEP-001 update (deprecation / removal policy)

PRODUCT-DEP-001 adds a canonical cross-cutting deprecation / removal
policy at
[`docs/product-deprecation-removal-policy.md`](product-deprecation-removal-policy.md).
Documentation only. No catalog row is set to `deprecated` or
`removed`; no entry is reclassified; no product, wrapper, package,
build-matrix entry, manifest, kit, or `REQUIRED_CONFIGS` membership
is touched. Release-One stays `production`, LED stays `preview`,
FanTRIAC stays `blocked` under HW-005, every `legacy-compatible`
entry stays `legacy-compatible`. Cross-linked from
[`docs/product-onboarding.md`](product-onboarding.md),
[`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md),
and [`docs/product-scaffold-generator.md`](product-scaffold-generator.md).

## HW-ASSETS-001 update (hardware artifact policy)

HW-ASSETS-001 adds a canonical hardware source and manufacturing
artifact policy at
[`docs/hardware/hardware-artifact-policy.md`](hardware/hardware-artifact-policy.md).
The policy defines the artifact classes (schematic PDF, KiCad
project / schematic / PCB source, BOM, CPL / pick-and-place,
Gerbers, drill files, STEP, board images, raw vendor ZIPs, and
the OS / IDE / SCM noise classes); the storage locations
(`docs/hardware/schematics/` for PDFs today; future
`docs/hardware/artifacts/`, `docs/hardware/sources/<SKU>-<REV>/`,
`docs/hardware/manufacturing/<SKU>-<REV>/`, and
`docs/hardware/images/<SKU>-<REV>/` directories deferred to
HW-ASSETS-002); the commit-vs-exclude rules; the raw-ZIP
workflow (extract outside the repo, checksum the original,
inventory the expansion, curate selected commits, retain the raw
ZIP externally); the per-board artifact index requirement
(`docs/hardware/artifacts/<SKU>-<REV>.md`) and its 22-field
schema (`board_sku`, `revision`, `artifact_source`,
`artifact_date`, `schematic_pdf`, `kicad_project`,
`kicad_schematic`, `kicad_pcb`, `bom`, `cpl`, `gerbers`,
`drill_files`, `step_file`, `images`, `excluded_files`,
`checksums`, `known_open_questions`, `pin_map_status`,
`package_yaml_status`, `product_yaml_status`, `webflash_status`,
`reviewer_notes`); the relationship to
`config/hardware-catalog.json` (JSON wins on drift; the artifact
index does not introduce any new JSON fields); the relationship
to product availability (the key rule: *hardware artifact
availability does not equal firmware support or WebFlash
availability*); the relationship to pin maps / package YAML /
product YAML (the recommended ordering); the manufacturing-
evidence handling options (commit directly / Git LFS / GitHub
Release / dedicated hardware repo / external-only with
checksum); the versioning and revision naming convention; the
finished-board inventory (`S360-100`, `S360-200`, `S360-210`,
`S360-211`, `S360-300`, all R4); the design-pending board
inventory (`S360-310`, `S360-311`, `S360-312`, `S360-320`,
`S360-400`, `S360-410`, all R4) with the per-board evidence
required before package / product / WebFlash work; the
follow-up PR sequence (HW-ASSETS-002, HW-GAP-001, HW-PINMAP-310
/ -311 / -312 / -320 / HW-PINMAP-400 / -410, PACKAGE-GAP-001,
PRODUCT-GAP-001); and the explicit do-not-change guardrails.
Documentation only. No raw vendor / fab ZIP contents are
added; no KiCad / BOM / CPL / Gerbers / drill / STEP / image
files are added; the per-board artifact index for
`S360-100-R4` is **not** added (that is the scope of
HW-ASSETS-002); no entry in `config/hardware-catalog.json`,
`config/product-catalog.json`, `config/webflash-builds.json`,
or `config/webflash-compatibility.json` is changed; no product
YAML, WebFlash wrapper, or package YAML is changed; no script,
test, workflow, component, or include is changed;
`.gitignore` / `.gitattributes` / pre-commit configuration are
not changed (actual exclusion-rule additions are deferred to
HW-ASSETS-002, which is the first PR to land a curated
artifact tree); Git LFS is **not** introduced (it is listed in
the policy as a future decision option only); no firmware is
regenerated; no GitHub Release is created or modified;
Release-One (`Ceiling-POE-VentIQ-RoomIQ`,
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
`v1.0.0`) stays unchanged; the Sense360 LED preview catalog
entry stays `status: preview`, `channel: preview`; FanTRIAC
stays `blocked` under HW-005; the mains-voltage compliance
status for `S360-320` / `S360-400` (COMPLIANCE-001) is not
changed. Cross-linked from
[`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md),
[`docs/product-onboarding.md`](product-onboarding.md),
[`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md),
[`docs/hardware/s360-100-r4-core.md`](hardware/s360-100-r4-core.md),
and [`docs/hardware/s360-300-r4-led.md`](hardware/s360-300-r4-led.md).

## PRODUCT-AVAIL-001 update (product availability taxonomy)

PRODUCT-AVAIL-001 adds a canonical cross-cutting product
availability taxonomy at
[`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md).
The doc threads together the hardware-evidence vocabulary
(HW-ASSETS-001 per-board artifact index field schema; HW-004 /
HW-006 / HW-008 audit labels; HW-009 / HW-010 package-mapping
labels) with the product-lifecycle vocabulary
(`config/product-catalog.json` `lifecycle_statuses`; PRODUCT-004
onboarding gates; PRODUCT-DEP-001 deprecation / removal lifecycles;
RELEASE-006 preview-to-stable gates) and the WebFlash-availability
vocabulary (`config/webflash-builds.json` matrix;
`config/webflash-compatibility.json` taxonomy;
`docs/webflash-contract.md` artifact / grammar / token contract)
into a 13-rung availability ladder
(`hardware-listed` → `artifact-indexed` → `schematic-verified` →
`pin-map-ready` → `package-yaml-ready` → `product-yaml-ready` →
`build-matrix-ready` → `release-artifact-ready` →
`webflash-imported` → `webflash-live-preview` →
`webflash-live-stable` → `production-required` → `kit-exposed`).
Introduces the two policy-only exception labels `design-pending`
(module named in docs / taxonomy / wizard but not buildable today)
and `firmware-missing` (board evidenced but no product YAML
consumes it as the customer surface). Maps every existing enum /
classification verbatim and adds none of its own. Records a
current-state snapshot for every SKU in
`config/hardware-catalog.json`: `S360-100` Core, `S360-200` RoomIQ,
`S360-210` AirIQ, `S360-211` VentIQ, `S360-300` LED (all five
`schematic-verified` under HW-008; only `S360-100` is
`artifact-indexed` under HW-ASSETS-002 today); `S360-310` Relay,
`S360-311` PWM, `S360-312` DAC, `S360-400` 240v PSU, `S360-410` PoE
PSU as `partially-documented` or `cataloged-unverified` with
`design-pending` / `firmware-missing` consequences for any
not-yet-existing product YAML; `S360-320` TRIAC `blocked` under
HW-005 and additionally gated by COMPLIANCE-001. Records how
WebFlash should consume the taxonomy in WF-WIZARD-AVAIL-001 (wizard
gating), WF-STALE-001 / PRODUCT-STALE-001 (stale-data cleanup), and
WF-PRODUCT-005 (import-readiness enforcement) without implementing
any of them. Records the future-validator / future-schema backlog —
PRODUCT-AVAIL-002 (machine-readable availability fields), HW-GAP-001
(board readiness matrix), PRODUCT-DEP-002 (`_validate_deprecated` /
`_validate_removed` validator rule blocks) — but adds **no** new
JSON fields and **no** new status values in this PR. Documentation
only. No entry in
[`config/hardware-catalog.json`](../config/hardware-catalog.json),
[`config/product-catalog.json`](../config/product-catalog.json),
[`config/webflash-builds.json`](../config/webflash-builds.json), or
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
is changed; no product YAML, WebFlash wrapper, or package YAML is
changed; no script, test, workflow, component, or include is
changed; no firmware is regenerated; no GitHub Release is created
or modified. Release-One stays `Ceiling-POE-VentIQ-RoomIQ` on
`stable` with artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` and tag
`v1.0.0`; the LED preview catalog entry stays `status: preview`,
`channel: preview`; FanTRIAC stays `status: blocked`,
`blocker: HW-005`, `webflash_build_matrix: false`; the
mains-voltage compliance status for `S360-320` / `S360-400`
(COMPLIANCE-001) is not changed; the Core J10 vs RoomIQ J6
pin-order discrepancy (HW-009 `needs-silkscreen/bench-verification`)
is not resolved; the systemic Core abstract-bus mismatch
(HW-009 `needs-package-change`, owned by
`release-one-hardware-audit.md` Required follow-ups #2 / #3) is not
resolved; every `legacy-compatible` entry stays
`legacy-compatible`. Cross-linked from
[`docs/product-onboarding.md`](product-onboarding.md),
[`docs/product-deprecation-removal-policy.md`](product-deprecation-removal-policy.md),
[`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md),
[`docs/hardware/hardware-artifact-policy.md`](hardware/hardware-artifact-policy.md),
[`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md),
and [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md).

## HW-GAP-001 update (board readiness matrix)

HW-GAP-001 adds the canonical board-level readiness matrix at
[`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md).
The matrix threads together the per-board evidence axes — hardware
catalog status, schematic PDF, per-board artifact index (HW-ASSETS-001
/ 002), pin-map / standalone reference doc (HW-004 / HW-006 / HW-008),
package YAML (HW-009 / HW-010), product YAML, WebFlash wrapper,
WebFlash build matrix, release artifact, WebFlash manifest / import,
bench / operator proof (RELEASE-006), blockers / open questions, and
current classification — into a single per-board × per-axis matrix
for every SKU in
[`config/hardware-catalog.json`](../config/hardware-catalog.json)
(`S360-100` Core, `S360-200` RoomIQ, `S360-210` AirIQ, `S360-211`
VentIQ, `S360-300` LED, `S360-310` Relay, `S360-311` PWM, `S360-312`
DAC, `S360-320` TRIAC, `S360-400` 240v PSU, `S360-410` PoE PSU). Uses
two summary tables (hardware-evidence axis and productization /
WebFlash axis) plus per-board notes that link back to the
source-of-truth docs rather than re-summarising them. Records the
policy-only status vocabulary (`done` / `partial` / `missing` / `not
applicable` / `blocked` / `compliance-gated` / `preview-only` /
`legacy-only` / `unknown`) as cell labels only — adds **no** JSON
enum, schema, or validator and reuses every existing classification
vocabulary verbatim. Distinguishes ready / evidenced boards from
missing / unfinished boards and from blocked / compliance-gated
boards. Records the follow-up PR sequence (`HW-PINMAP-310` / `-311` /
`-312` / `-320` / `-400` / `-410` → `PACKAGE-GAP-001` →
`PRODUCT-GAP-001` → `WEBFLASH-GAP-001` → `RELEASE-GAP-001` →
`WF-IMPORT-GAP-001`). Carries the explicit do-not-change guardrails.
Documentation only. No entry in
[`config/hardware-catalog.json`](../config/hardware-catalog.json),
[`config/product-catalog.json`](../config/product-catalog.json),
[`config/webflash-builds.json`](../config/webflash-builds.json), or
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
is changed; no product YAML, WebFlash wrapper, or package YAML is
changed; no script, test, workflow, component, or include is changed;
no firmware is regenerated; no GitHub Release is created or modified;
no WebFlash import is performed. Release-One stays
`Ceiling-POE-VentIQ-RoomIQ` on `stable` with artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` and tag
`v1.0.0`; the LED preview entry `Ceiling-POE-VentIQ-RoomIQ-LED` stays
`status: preview`, `channel: preview`; FanTRIAC stays `status:
blocked`, `blocker: HW-005`, `webflash_build_matrix: false`; the
mains-voltage compliance status for `S360-320` / `S360-400`
(COMPLIANCE-001) is not changed; the Core J10 vs RoomIQ J6 pin-order
discrepancy (HW-009 `needs-silkscreen/bench-verification`) is not
resolved; the systemic Core abstract-bus mismatch (HW-009
`needs-package-change`, owned by
[`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups))
is not resolved; the `S360-410` PoE PSU schematic-pending caveat in
[`docs/release-one-hardware-audit.md` Findings → PoE PSU](release-one-hardware-audit.md#findings)
is preserved, not promoted away; the `S360-300` bench-verification
Open Questions in
[`docs/hardware/s360-300-r4-led.md`](hardware/s360-300-r4-led.md#open-questions--verification-needed)
(harness rail, LED count, harness identity, observed behaviour) are
preserved; every `legacy-compatible` entry stays `legacy-compatible`.
Cross-linked from
[`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md)
(See also + Follow-up-PR-sequence row #1),
[`docs/hardware/hardware-artifact-policy.md`](hardware/hardware-artifact-policy.md)
(See also + Follow-up-PR-sequence row #2),
[`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
(See also), and
[`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md)
(See also).

## PRODUCT-STALE-001 update (stale upstream product/catalog inventory)

PRODUCT-STALE-001 is the upstream paired cleanup for the WebFlash-side
`WF-STALE-001`. It performs a fresh inventory of the upstream product
catalog, build matrix, WebFlash wrappers, and the cross-cutting
docs/scripts/tests that govern them, records the no-action verdict, and
strengthens the catalog test surface so the current shape cannot
silently regress. PRODUCT-STALE-001 changes **no** catalog data, **no**
YAML, **no** build-matrix entry, **no** wrapper, **no** package,
**no** workflow, **no** firmware, and **no** release.

### Inventory pass

| Surface | Status today | Action by PRODUCT-STALE-001 |
|---|---|---|
| [`config/product-catalog.json`](../config/product-catalog.json) — 34 entries (1 `production` Release-One, 1 `preview` LED, 1 `blocked` FanTRIAC, 31 `legacy-compatible`) | Clean. Every entry is correctly classified. Every top-level `products/*.yaml` is enumerated. Every `legacy-compatible` entry has `webflash_build_matrix: false`, no `config_string`, no `artifact_name`, no `webflash_wrapper`, and a `notes` field calling out non-WebFlash / non-Release-One / manual / custom status. | None. No status flip, no entry add, no entry remove. |
| [`config/webflash-builds.json`](../config/webflash-builds.json) — 2 builds (Release-One stable + LED preview) | Clean. No stale entries. | None. |
| [`config/webflash-compatibility.json`](../config/webflash-compatibility.json) — taxonomy snapshot | Clean. `forbidden_tokens` covers `Bathroom` / `Comfort` / `Presence` / `Fan` / `FanAnalog`. Stricter upstream aliases (`BathroomAirIQ` / `BathroomAirIQBase` / `BathroomAirIQPro` / `Base` / `Pro` / `AirIQBase` / `AirIQPro` / `AirIQProv`) remain a non-blocking documentation observation tracked in [`docs/webflash-compatibility-taxonomy-audit.md`](webflash-compatibility-taxonomy-audit.md). | None. PRODUCT-STALE-001 does not add tokens. The deferred alignment stays a future scoped PR per the COMPAT-001 follow-up list. |
| [`config/hardware-catalog.json`](../config/hardware-catalog.json) | Clean. All `old_name` aliases (e.g. `Bathroom Pro`, `LED Ring`, `TRIAC_Board`) are deliberate historical references. | None. |
| [`products/`](../products/) (34 top-level YAMLs) and [`products/webflash/`](../products/webflash/) (3 wrappers) | Clean. Every wrapper is referenced by exactly one catalog entry. Legacy YAMLs are retained as `legacy-compatible` per the [Do-not-delete list](#do-not-delete-list) above. | None. No YAML added, removed, renamed, or rewritten. |
| Scripts that consume the catalog ([`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py), [`scripts/scaffold_product.py`](../scripts/scaffold_product.py)) | Already refuse `blocked` / `legacy-compatible` / `deprecated` / `removed` / `compile-only` / `hardware-pending` via `REFUSED_STATUSES` and reject `production` / `deprecated` / `removed` / `legacy-compatible` scaffolds via `REJECTED_STATUSES`. | None. PRODUCT-STALE-001 does not edit these scripts. |
| Tests | All green before and after PRODUCT-STALE-001 (see [Validation](#validation-run-for-product-stale-001) below). | **Strengthened** at the catalog layer — three new tests in [`tests/test_product_catalog.py`](../tests/test_product_catalog.py), three new synthetic-fixture test classes in [`tests/test_product_catalog_consistency.py`](../tests/test_product_catalog_consistency.py), and one new rule block + one extended rule block in [`scripts/validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py). |

### Findings against the PRODUCT-STALE-001 design questions

The investigation walked the 22 design questions in the task description.
Summary:

- **Production / preview / blocked / legacy-compatible totals.** 1 / 1 / 1 / 31 respectively. No drift.
- **Legacy-compatible WebFlash-shippability.** None look WebFlash-shippable. None carry `config_string`, `artifact_name`, `webflash_wrapper`, or `webflash_build_matrix: true`. Every `notes` string explicitly says "Pre-WebFlash … retained for manual/custom users. Not Release-One WebFlash firmware."
- **Stale tokens in current-tense docs/scripts.** None. References to `AirIQPro` / `AirIQBase` / `CoreVoice` / `Wall` / `Ceiling-USB` / `Ceiling-PWR` / `Ceiling-POE-AirIQ` / `Ceiling-Voice` only appear in: (a) the legacy → WebFlash alias table in [`docs/webflash-contract.md`](webflash-contract.md) §3, (b) the COMPAT-001 audit at [`docs/webflash-compatibility-taxonomy-audit.md`](webflash-compatibility-taxonomy-audit.md), (c) audit-narrative inside this file, (d) `legacy-compatible` catalog entries (notes) and legacy YAML header comments, (e) historical CHANGELOG / `packages/SENSE360_MODULES.md` context. None of these are presented as current WebFlash products.
- **Stale WebFlash wrappers / build-matrix entries.** None.
- **Product YAMLs referencing blocked modules.** Only `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`, which is the `blocked` catalog entry; the LED preview entry carries `blocked_modules: ["FanTRIAC"]` correctly.
- **PRODUCT-DEP-001 metadata requirements.** Tombstoning requires substantial metadata. No catalog entry is a candidate for `deprecated` / `removed` today.
- **Validator support for `deprecated` / `removed`.** [`scripts/validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py) accepts both as valid statuses but does **not** yet enforce their required-metadata blocks. That enforcement is owned by **PRODUCT-DEP-002** per the backlog in [`docs/product-deprecation-removal-policy.md`](product-deprecation-removal-policy.md#recommended-future-enforcement-not-added-by-product-dep-001). PRODUCT-STALE-001 does not preempt PRODUCT-DEP-002.
- **Status flips.** None proposed. No catalog entry is a clean candidate for `deprecated` or `removed` today.
- **YAML / doc deletions.** None. The `legacy-compatible` YAMLs are public-API / remote-package surfaces per the [Public API / remote package risk](#public-api--remote-package-risk) section above, and PRODUCT-DEP-001 still requires explicit per-entry tombstone metadata before deletion.
- **Historical references.** All retained: COMPAT-001 audit, this cleanup audit, the deprecation/removal policy, the availability taxonomy, the board readiness matrix, legacy YAML comments, and historical CHANGELOG entries.
- **Current-tense reword candidates.** None remain in scope for PRODUCT-STALE-001. The lingering `docs/ci-pipeline.md` Mini-centric framing is a CLEANUP-002 straggler explicitly listed under [Stale Release-One references](#stale-release-one-references) above and is **deferred** from this PR.
- **Test strengthening needed.** Yes: three new catalog-level guards (see [Test strengthening](#test-strengthening-product-stale-001) below).

### Test strengthening (PRODUCT-STALE-001)

These guards pin down rules that are already documented in the catalog
description and in [`docs/product-onboarding.md`](product-onboarding.md)
but were not directly enforced by the test surface. They are additive —
the current real catalog passes all of them.

[`tests/test_product_catalog.py`](../tests/test_product_catalog.py):

- `test_legacy_compatible_entries_have_no_config_string` — every
  `legacy-compatible` entry must omit `config_string`. The WebFlash
  `config_string` namespace is reserved for WebFlash-shippable entries;
  legacy-compatible entries use `legacy_config_id` instead.
- `test_legacy_compatible_entry_notes_call_out_non_webflash` — every
  `legacy-compatible` entry's `notes` field must contain at least one of
  the markers `not release-one`, `not webflash`, `manual/custom`, or
  `manual users` (case-insensitive). Locks the disclaimer wording so a
  future edit cannot silently drop the "not WebFlash" framing.
- `test_no_webflash_eligible_entry_uses_forbidden_token` — for every
  `production` / `preview` catalog entry, every hyphen-separated token
  of `config_string` must not be in the `forbidden_tokens` list of
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json).
  Catalog-layer mirror of the build-matrix-level guard in
  [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py),
  so a stale alias is caught even if `webflash_build_matrix: false`.

[`scripts/validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py):

- `_validate_legacy_compatible` is extended to reject `config_string`
  presence on any `legacy-compatible` entry.
- A new cross-cutting `_validate_forbidden_tokens` rule block rejects
  any catalog entry whose `config_string` contains a token from the
  compatibility snapshot's `forbidden_tokens` list, regardless of
  lifecycle status or `webflash_build_matrix` value.

[`tests/test_product_catalog_consistency.py`](../tests/test_product_catalog_consistency.py):

- New `LegacyCompatibleConfigStringRejectionTests` — synthetic-fixture
  cases for the new `config_string` rejection rule.
- New `ForbiddenTokenGuardTests` — synthetic-fixture cases for the
  cross-cutting forbidden-token rule (`Bathroom`, `Comfort`), plus a
  positive case (`Ceiling-POE-VentIQ-RoomIQ`).
- New `CurrentCatalogPassesAfterStrengtheningTests` — regression guard
  asserting the real catalog still passes the strengthened validator.

### Deferrals

PRODUCT-STALE-001 deliberately does **not** roll in the following.
Each is named for traceability so the next maintainer knows where the
work lives:

- **`_validate_deprecated` / `_validate_removed` validator rule
  blocks → PRODUCT-DEP-002.** PRODUCT-DEP-001 explicitly defers the
  required-metadata enforcement for `deprecated` / `removed` to a
  scoped follow-up PR. PRODUCT-STALE-001 does not add either rule
  block. No catalog entry is `deprecated` or `removed` today.
- **`docs/ci-pipeline.md` Mini-centric framing → CLEANUP-002.**
  Section 1 / section 2 distinction is in place but the document
  header (line 3) and the "Mini Board Product Configurations" /
  "Adding New Mini Board Configs" sections still frame the Mini board
  as the primary product type. This is documented under
  [Stale Release-One references](#stale-release-one-references) and
  [Workflow/CI wording](#workflowci-wording) above; PRODUCT-STALE-001
  does not edit it.
- **Stricter `forbidden_tokens` alignment with upstream WebFlash
  `validate-naming-policy.js` → future scoped PR.** Adding
  `BathroomAirIQ` / `BathroomAirIQBase` / `BathroomAirIQPro` / `Base`
  / `Pro` / `AirIQBase` / `AirIQPro` / `AirIQProv` to
  `config/webflash-compatibility.json` `forbidden_tokens` is a
  COMPAT-001 follow-up; PRODUCT-STALE-001 does not edit
  `config/webflash-compatibility.json`.
- **WebFlash-side stale-data cleanup → WF-STALE-001.** The paired
  WebFlash repo PR removes stale `REQUIRED_CONFIGS` / kit / manifest /
  `firmware/sources.json` / wizard-taxonomy references on the
  WebFlash side. PRODUCT-STALE-001 does not edit anything in the
  WebFlash repo.
- **Future machine-readable availability fields → PRODUCT-AVAIL-002.**
  The candidate field names (`artifact_index_status` /
  `pin_map_status` / `package_yaml_status` / `product_yaml_status` /
  `webflash_status` / `availability_notes` / `missing_evidence`) are
  enumerated in
  [`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md);
  PRODUCT-STALE-001 adds none of them to any JSON.

### Out of scope (unchanged by PRODUCT-STALE-001)

PRODUCT-STALE-001 does **not**:

- edit
  [`config/product-catalog.json`](../config/product-catalog.json),
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
  or [`config/hardware-catalog.json`](../config/hardware-catalog.json);
- edit any product YAML under [`products/`](../products/) or any
  WebFlash wrapper under [`products/webflash/`](../products/webflash/);
- edit any package YAML under [`packages/`](../packages/);
- edit any workflow under `.github/workflows/`, any component under
  `components/`, any include under `include/`,
  [`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py),
  or [`scripts/scaffold_product.py`](../scripts/scaffold_product.py);
- generate, regenerate, sign, import, deploy, or otherwise produce
  firmware;
- create, edit, or delete any GitHub Release, tag, or asset;
- change the Release-One config string `Ceiling-POE-VentIQ-RoomIQ`,
  its artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, or its tag
  `v1.0.0`;
- change the LED preview catalog entry `Ceiling-POE-VentIQ-RoomIQ-LED`
  (stays `status: preview`, `channel: preview`);
- unblock FanTRIAC (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays
  `status: blocked`, `blocker: HW-005`,
  `webflash_build_matrix: false`);
- change the mains-voltage compliance status for `S360-320` or
  `S360-400` (COMPLIANCE-001);
- flip any catalog entry to `deprecated` or `removed`;
- delete, rename, restructure, or rewrite any `legacy-compatible`
  product YAML or any WebFlash wrapper;
- add a new product YAML, WebFlash wrapper, package YAML,
  build-matrix entry, or catalog entry;
- add, remove, or modify any entry in WebFlash-side
  `REQUIRED_CONFIGS`, `scripts/data/kits.json`,
  `firmware/sources.json`, or `manifest.json` — those are
  WebFlash-owned and are not touched by this repo.

Every `legacy-compatible` entry remains `legacy-compatible`; the 30+
manual / remote-package surfaces stay public-API per the
[Do-not-delete list](#do-not-delete-list) above.

### Validation run for PRODUCT-STALE-001

The full validator and test surface was re-run after the strengthening.
All green.

```text
python3 scripts/validate_product_catalog_consistency.py
python3 tests/test_product_catalog.py
python3 tests/test_product_catalog_consistency.py
python3 tests/validate_webflash_builds.py
python3 tests/test_webflash_compatibility.py
python3 tests/test_webflash_artifact_naming.py
python3 tests/test_validate_webflash_release_notes.py
python3 tests/test_generate_webflash_release_notes.py
python3 tests/test_product_substitutions.py
python3 tests/test_release_one_entity_names.py
python3 tests/validate_configs.py
python3 tests/test_hardware_catalog.py
python3 tests/test_led_package_mapping.py
python3 tests/test_scaffold_product.py
```

Sanity grep run from the repo root:

```text
grep -RIn "AirIQPro\|AirIQBase\|CoreVoice\|Core Voice\|Voice\|voice\|Wall\|wall\|Ceiling-USB\|Ceiling-PWR\|Ceiling-POE-AirIQ\|Ceiling-Voice\|FanTRIAC\|legacy-compatible\|deprecated\|removed\|tombstone\|not WebFlash-shippable\|PRODUCT-STALE-001" config products packages scripts tests docs README.md
```

Remaining hits after the run are exclusively one of: historical
references (this cleanup audit, COMPAT-001 audit, deprecation /
removal policy, availability taxonomy, board readiness matrix),
legacy-compatible / blocked-reference catalog entries and their YAML
headers, parser / negative test fixtures, the legacy → WebFlash alias
table in
[`docs/webflash-contract.md`](webflash-contract.md) §3, or PRODUCT-STALE-001
itself. No stale upstream config is presented as current
WebFlash-shippable; Release-One stays `Ceiling-POE-VentIQ-RoomIQ` on
`stable`; LED stays `preview`; FanTRIAC stays `blocked` under HW-005;
no unsupported YAML / build-matrix / release change occurs.

### See also (PRODUCT-STALE-001)

- [`docs/product-deprecation-removal-policy.md`](product-deprecation-removal-policy.md)
  — PRODUCT-DEP-001 canonical deprecation / removal policy. Owns the
  `deprecated` / `removed` validator-rule-block backlog
  (PRODUCT-DEP-002).
- [`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md)
  — PRODUCT-AVAIL-001 canonical availability taxonomy. Names
  `PRODUCT-STALE-001` in its follow-up PR sequence.
- [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
  — HW-GAP-001 per-board readiness matrix. Names `WF-STALE-001` as
  the WebFlash-side paired cleanup.
- [`tests/test_product_catalog.py`](../tests/test_product_catalog.py),
  [`tests/test_product_catalog_consistency.py`](../tests/test_product_catalog_consistency.py),
  [`scripts/validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py)
  — the three files this PR strengthens.
- [`docs/webflash-compatibility-taxonomy-audit.md`](webflash-compatibility-taxonomy-audit.md)
  — COMPAT-001 audit. Owns the stricter-`forbidden_tokens`-alignment
  backlog.

## PACKAGE-GAP-001 update (package readiness matrix)

PACKAGE-GAP-001 adds the canonical package-level readiness gate at
[`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md).
The matrix records, per package, the current evidence state, the
known schematic / pin-map conflicts, the allowed action right now,
and the named follow-up PR that owns reconciliation for each of the
six in-scope expansion / power packages:
[`packages/expansions/fan_relay.yaml`](../packages/expansions/fan_relay.yaml)
(`S360-310`),
[`packages/expansions/fan_pwm.yaml`](../packages/expansions/fan_pwm.yaml)
(`S360-311`),
[`packages/expansions/fan_gp8403.yaml`](../packages/expansions/fan_gp8403.yaml)
(`S360-312`),
[`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml)
(`S360-320`),
[`packages/hardware/power_240v.yaml`](../packages/hardware/power_240v.yaml)
(`S360-400`), and
[`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml)
(`S360-410`). The matrix also records the Core abstract-bus packages
([`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml)
and
[`packages/hardware/sense360_core.yaml`](../packages/hardware/sense360_core.yaml))
as `do-not-change-release-one` + `needs-package-reconciliation`
deferred to the systemic `CORE-ABSTRACT-BUS-001` rebind that aliases
[`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups).
Carries the load-bearing **Core rule**: *"Package YAML changes are
allowed only when the target board has verified pin-map evidence and
the package change can be traced to a schematic-backed audit.
Partial, pending, or blocked audits may produce follow-up
requirements, but must not be treated as implementation approval."*
Uses a policy-only label vocabulary (`ready-for-package-change` /
`needs-package-reconciliation` / `schematic-evidence-pending` /
`bench-evidence-pending` / `timing/compliance-pending` /
`reference-only` / `do-not-change-release-one` /
`blocked-from-standard-exposure` / `unknown`) — adds **no** JSON
enum, schema, or validator and reuses every existing classification
vocabulary verbatim
(`confirmed-ok` / `needs-package-change` / `needs-doc-fix` /
`needs-silkscreen/bench-verification` / `blocked` / `unknown` from
HW-009; `documented` / `partially-documented` /
`cataloged-unverified` / `blocked` / `not-needed-for-release-one`
from HW-004 / HW-006 / HW-008; `package-yaml-ready` /
`package-yaml-pending` from PRODUCT-AVAIL-001). Status summary: **no
package YAML is `ready-for-package-change` today** — every in-scope
package carries at least one of `schematic-evidence-pending`,
`needs-package-reconciliation`, `bench-evidence-pending`,
`timing/compliance-pending`, `reference-only`,
`do-not-change-release-one`, or `blocked-from-standard-exposure`.
Records the per-slice implementation gates (schematic ingest /
pin-map standalone reference doc / JSON `schematic_status` promotion
/ bench evidence / timing & compliance / Core abstract-bus rebind)
and the follow-up PR sequence (`PACKAGE-RELAY-001`,
`PACKAGE-PWM-001`, `PACKAGE-DAC-001`, `PACKAGE-TRIAC-001`,
`PACKAGE-POWER-400-001`, `PACKAGE-POE-410-001`,
`CORE-ABSTRACT-BUS-001`) as separate scoped PRs with their own gate
evidence. Carries the explicit do-not-change guardrails.
Documentation only. **No** package YAML under
[`packages/`](../packages/) is edited (including all six in-scope
packages, the legacy four-channel
[`packages/expansions/sense360_fan_pwm.yaml`](../packages/expansions/sense360_fan_pwm.yaml),
the legacy alias
[`packages/expansions/fan_12v_pwm.yaml`](../packages/expansions/fan_12v_pwm.yaml),
[`packages/expansions/gpio_expander_sx1509.yaml`](../packages/expansions/gpio_expander_sx1509.yaml),
the Core abstract packages, and every other package in the tree).
[`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml)
retains its BLOCKED / UNVERIFIED banner, its `ac_dimmer` driver
topology, and its mains-voltage / qualified-electrician warnings
verbatim. No entry in
[`config/hardware-catalog.json`](../config/hardware-catalog.json),
[`config/product-catalog.json`](../config/product-catalog.json),
[`config/webflash-builds.json`](../config/webflash-builds.json), or
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
is changed; no product YAML, WebFlash wrapper, script, test,
workflow, component, or include is changed; no firmware is
regenerated; no GitHub Release is created or modified; no WebFlash
import is performed; no kit is added; no `REQUIRED_CONFIGS` /
`scripts/data/kits.json` / `firmware/sources.json` / `manifest.json`
entry is added or removed. Release-One stays
`Ceiling-POE-VentIQ-RoomIQ` on `stable` with artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` and tag
`v1.0.0`; the LED preview entry `Ceiling-POE-VentIQ-RoomIQ-LED`
stays `status: preview`, `channel: preview`; FanTRIAC stays
`status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`
(the advanced / manual-warning long-term posture in
[`docs/hardware/s360-320-r4-triac.md`](hardware/s360-320-r4-triac.md)
is **intent only**; the JSON lifecycle row is unchanged); the
mains-voltage compliance status for `S360-320` / `S360-400`
(COMPLIANCE-001) is not changed; HW-005 is not resolved; the Core
J10 vs RoomIQ J6 pin-order discrepancy (HW-009
`needs-silkscreen/bench-verification`) is not resolved; the
systemic Core abstract-bus mismatch (HW-009 `needs-package-change`,
owned by
[`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups);
recorded by this matrix as `CORE-ABSTRACT-BUS-001`) is not
resolved; the `S360-410` PoE PSU schematic-pending caveat in
[`docs/release-one-hardware-audit.md` Findings → PoE PSU](release-one-hardware-audit.md#findings)
is preserved, not promoted away; every `legacy-compatible` entry
stays `legacy-compatible`. No new test is added; a future
per-package slice PR may add a structural file-content guard
analogous to
[`tests/test_led_package_mapping.py`](../tests/test_led_package_mapping.py)
once it edits the corresponding package. Cross-linked from
[`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
(See also + Follow-up-PR-sequence row #7),
[`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
(See also),
[`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md)
(See also), and
[`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)
(See also). Source-of-truth consumed: the per-board pin / package
mapping audits
[`docs/hardware/s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md)
(HW-PINMAP-310, `pending`),
[`docs/hardware/s360-311-r4-pwm.md`](hardware/s360-311-r4-pwm.md)
(HW-PINMAP-311, `partial`),
[`docs/hardware/s360-312-r4-dac.md`](hardware/s360-312-r4-dac.md)
(HW-PINMAP-312, `partial`),
[`docs/hardware/s360-320-r4-triac.md`](hardware/s360-320-r4-triac.md)
(HW-PINMAP-320, `partial`),
[`docs/hardware/s360-400-r4-power.md`](hardware/s360-400-r4-power.md)
(HW-PINMAP-400, `partial`),
[`docs/hardware/s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md)
(HW-PINMAP-410, `pending`).

## PRODUCT-GAP-001 update (product readiness matrix)

PRODUCT-GAP-001 adds the canonical product-level readiness gate at
[`docs/product-readiness-matrix.md`](product-readiness-matrix.md).
The matrix records, per candidate product family, the current
package-evidence state, the WebFlash compatibility grammar verdict,
the allowed action right now, and the named follow-up PR that owns
each family's product slice for the six candidate product families
(FanRelay / `S360-310`, FanPWM / `S360-311`, FanDAC / `S360-312`,
FanTRIAC / `S360-320`, PWR-240V / `S360-400`, PoE-410 / `S360-410`).
Carries the load-bearing **Core rule**: *"Product YAML changes are
allowed only when (a) every package the product would consume is
`ready-for-package-change` per
[`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md),
(b) the combination is permitted by the WebFlash compatibility
grammar in
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
and (c) the
[`docs/product-onboarding.md`](product-onboarding.md) safe sequence
is followed end-to-end. Package readiness, product readiness, and
WebFlash exposure are three separate gates; product YAML existence
does not itself authorise WebFlash exposure."* Uses a policy-only
label vocabulary (`ready-for-product-yaml` /
`needs-package-reconciliation` / `schematic-evidence-pending` /
`hardware-evidence-pending` / `timing/compliance-pending` /
`advanced/manual-warning-only` / `blocked-from-standard-exposure` /
`not-webflash-default` / `not-recommended` / `not-required-configs`
/ `not-kit` / `legacy-only` / `invalid-combination` / `unknown`) —
adds **no** JSON enum, schema, or validator and reuses every
existing classification vocabulary verbatim
(`production` / `preview` / `compile-only` / `hardware-pending` /
`blocked` / `legacy-compatible` / `deprecated` / `removed` from
[`config/product-catalog.json`](../config/product-catalog.json)
`lifecycle_statuses`; `ready-for-package-change` /
`needs-package-reconciliation` /
`schematic-evidence-pending` / `bench-evidence-pending` /
`timing/compliance-pending` / `reference-only` /
`do-not-change-release-one` / `blocked-from-standard-exposure` from
PACKAGE-GAP-001; `hardware-listed` / `artifact-indexed` /
`schematic-verified` / `pin-map-ready` / `package-yaml-ready` /
`product-yaml-ready` / `build-matrix-ready` /
`release-artifact-ready` / `webflash-imported` /
`webflash-live-preview` / `webflash-live-stable` /
`production-required` / `kit-exposed` from PRODUCT-AVAIL-001).
Status summary: **no candidate product family is
`ready-for-product-yaml` today** — every candidate carries at least
one of `needs-package-reconciliation`, `schematic-evidence-pending`,
`hardware-evidence-pending`, `timing/compliance-pending`,
`reference-only`, `blocked-from-standard-exposure`, or
`do-not-change-release-one`. Records the current product surface
(1 `production` Release-One, 1 `preview` LED, 1 `blocked` FanTRIAC
reference, 31 `legacy-compatible`) verbatim from
[`config/product-catalog.json`](../config/product-catalog.json), the
WebFlash compatibility grammar from
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
(canonical modules `AirIQ` / `VentIQ` / `RoomIQ` / `FanRelay` /
`FanPWM` / `FanDAC` / `FanTRIAC` / `LED`; AirIQ ↔ VentIQ mutex;
FanDAC ↔ AirIQ mutex; `fan_variants_are_firmware_distinct: true`;
`generic_fan_token_forbidden: true`; forbidden tokens `Bathroom` /
`Comfort` / `Presence` / `Fan` / `FanAnalog`;
`release_one_required_configs: ["Ceiling-POE-VentIQ-RoomIQ"]`), the
WebFlash exposure class table (`none` / `docs-only` /
`preview-candidate` / `advanced/manual-warning-only` /
`production-candidate` / `legacy-only`), and the follow-up PR
sequence (`PRODUCT-RELAY-001`, `PRODUCT-PWM-001`, `PRODUCT-DAC-001`,
`PRODUCT-TRIAC-001`, `PRODUCT-POWER-400-001`, `PRODUCT-POE-410-001`,
`WEBFLASH-GAP-001`, `RELEASE-GAP-001`, `WF-IMPORT-GAP-001`,
`WF-TRIAC-001`) as separate scoped PRs with their own gate
evidence. Carries the explicit do-not-change guardrails.
Documentation only. **No** product YAML under
[`products/`](../products/) is added or edited (including all 34
existing entries: Release-One, LED preview, the blocked FanTRIAC
reference, and the 31 `legacy-compatible` Core / Core-Voice / Mini /
standalone-legacy entries such as
[`products/sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml)
and [`products/sense360-poe.yaml`](../products/sense360-poe.yaml));
no WebFlash wrapper under
[`products/webflash/`](../products/webflash/) is added or edited
(`ceiling-poe-ventiq-roomiq.yaml`,
`ceiling-poe-ventiq-roomiq-led.yaml`, and the blocked
`ceiling-poe-ventiq-fantriac-roomiq.yaml` all stay verbatim); no
package YAML under [`packages/`](../packages/) is edited; no entry
in [`config/hardware-catalog.json`](../config/hardware-catalog.json),
[`config/product-catalog.json`](../config/product-catalog.json),
[`config/webflash-builds.json`](../config/webflash-builds.json), or
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
is changed; no script, test, workflow, component, or include is
changed; no firmware is regenerated; no GitHub Release is created
or modified; no WebFlash import is performed; no kit is added; no
`REQUIRED_CONFIGS` / `scripts/data/kits.json` /
`firmware/sources.json` / `manifest.json` entry is added or
removed. Release-One stays `Ceiling-POE-VentIQ-RoomIQ` on `stable`
with artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` and tag
`v1.0.0`; the LED preview entry `Ceiling-POE-VentIQ-RoomIQ-LED`
stays `status: preview`, `channel: preview`, version `1.0.0`,
artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` (no
promotion to `production` / `stable`; no addition to
`release_one_required_configs`; no kit added); the FanTRIAC
reference `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status:
blocked`, `blocker: HW-005`, `webflash_build_matrix: false` (the
advanced / manual-warning long-term posture in
[`docs/hardware/s360-320-r4-triac.md`](hardware/s360-320-r4-triac.md)
is **intent only**; the JSON lifecycle row is unchanged); the
mains-voltage compliance status for `S360-320` / `S360-400`
(COMPLIANCE-001) is not changed; HW-005 is not resolved; the Core
J10 vs RoomIQ J6 pin-order discrepancy (HW-009
`needs-silkscreen/bench-verification`) is not resolved; the
systemic Core abstract-bus mismatch (HW-009 `needs-package-change`,
owned by
[`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups);
recorded by PACKAGE-GAP-001 as `CORE-ABSTRACT-BUS-001`) is not
resolved; the `S360-410` PoE PSU schematic-pending caveat in
[`docs/release-one-hardware-audit.md` Findings → PoE PSU](release-one-hardware-audit.md#findings)
is preserved, not promoted away; every `legacy-compatible` entry
(31 today) stays `legacy-compatible`. No new test is added; a
future per-family slice PR may add a structural file-content guard
analogous to
[`tests/test_release_one_entity_names.py`](../tests/test_release_one_entity_names.py)
once it adds the corresponding product YAML. Cross-linked from
[`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
(See also),
[`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
(See also; Follow-up PR sequence row #8 already names
PRODUCT-GAP-001),
[`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
(See also),
[`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md)
(See also; the existing PRODUCT-GAP-001 future-PR mentions at
lines 69, 705, and 735 are preserved),
[`docs/product-onboarding.md`](product-onboarding.md) (See also),
[`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
(See also), and
[`docs/product-deprecation-removal-policy.md`](product-deprecation-removal-policy.md)
(See also). Source-of-truth consumed: PACKAGE-GAP-001
[`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
(per-package verdict for every required package); the six per-board
pin / package mapping audits
[`docs/hardware/s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md)
(HW-PINMAP-310, `pending`),
[`docs/hardware/s360-311-r4-pwm.md`](hardware/s360-311-r4-pwm.md)
(HW-PINMAP-311, `partial`),
[`docs/hardware/s360-312-r4-dac.md`](hardware/s360-312-r4-dac.md)
(HW-PINMAP-312, `partial`),
[`docs/hardware/s360-320-r4-triac.md`](hardware/s360-320-r4-triac.md)
(HW-PINMAP-320, `partial`),
[`docs/hardware/s360-400-r4-power.md`](hardware/s360-400-r4-power.md)
(HW-PINMAP-400, `partial`),
[`docs/hardware/s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md)
(HW-PINMAP-410, `pending`); the cross-cutting
[`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md)
(13-rung availability ladder); the WebFlash grammar in
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json);
the product catalog in
[`config/product-catalog.json`](../config/product-catalog.json);
and the build matrix in
[`config/webflash-builds.json`](../config/webflash-builds.json).

## PRODUCT-TRIAC-001 update (reclassify FanTRIAC as advanced/manual-warning)

PRODUCT-TRIAC-001 reclassifies the FanTRIAC product policy from
"intentionally excluded / hidden / blocked-as-if-unavailable" to
**advanced / manual-warning candidate**, while preserving every
existing blocker and exclusion. The change is **wording-only /
notes-only**: a single edit to the `notes` field of the
`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` entry in
[`config/product-catalog.json`](../config/product-catalog.json),
plus reinforcement of the policy posture across the listed docs.
**No** new lifecycle enum value is added; **no** product YAML, no
WebFlash wrapper, no build-matrix entry, no release artifact, and
no WebFlash import is created or modified. The structural fields
on the FanTRIAC catalog entry are preserved verbatim:
`status: blocked`, `blocker: HW-005`, `reason` unchanged,
`webflash_build_matrix: false`, no `artifact_name`. The
`lifecycle_statuses` enum in
[`config/product-catalog.json`](../config/product-catalog.json) is
unchanged. The blocked-reference WebFlash wrapper
[`products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml)
is retained verbatim and stays out of the build matrix. The
blocked-reference product YAML
[`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml)
is unchanged; the BLOCKED / UNVERIFIED banner, the
`fallback_ssid: "S360 TRIAC BLOCKED"` admonition, and the
placeholder `fan_triac_gate_pin: GPIO5` / `fan_triac_zc_pin: GPIO6`
all stay. The package YAML
[`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml)
is unchanged; its BLOCKED / UNVERIFIED banner, its mains-voltage /
qualified-electrician warnings, and its `ac_dimmer` driver topology
all remain in place. The `FanTRIAC` token remains in
`canonical_modules` in
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
and remains in the Release-One `blocked_modules` list (carried in
[`config/product-catalog.json`](../config/product-catalog.json) on
the `Ceiling-POE-VentIQ-RoomIQ` Release-One entry and the
`Ceiling-POE-VentIQ-RoomIQ-LED` LED preview entry). HW-005 and
COMPLIANCE-001 remain open and unresolved; this update makes no
compliance claim. The advanced / manual-warning posture recorded
on the FanTRIAC catalog entry's `notes` field reads as: "Advanced /
manual-warning candidate after HW-005 unblock,
HW-PINMAP-320-FOLLOWUP, PACKAGE-TRIAC-001, COMPLIANCE-001 advanced
/ manual-warning sign-off, and WebFlash-side manual-warning UX
gates clear. Not Release-One, not REQUIRED_CONFIGS, not
recommended, not kit / default, not compliance-certified. Retained
as documented hardware; blocked from standard exposure until gates
clear." Every exclusion is durable: **not** Release-One, **not**
`REQUIRED_CONFIGS`, **not** recommended, **not** kit / default,
**not** compliance-certified — irrespective of any future product
YAML, WebFlash wrapper, build, release, or import existence. The
follow-up PR sequence has been updated across
[`docs/hardware/s360-320-r4-triac.md`](hardware/s360-320-r4-triac.md)
(§Advanced / manual-warning product posture; §Follow-up PR sequence
PRODUCT-TRIAC-001 row marked landed; §Do-not-change guardrails
clarified that PRODUCT-TRIAC-001's notes-only edit preserves the
structural fields),
[`docs/product-readiness-matrix.md`](product-readiness-matrix.md)
(§FanTRIAC / S360-320; Product readiness table FanTRIAC row;
Follow-up PR sequence — adds `PRODUCT-TRIAC-002` as the product
YAML / catalog-entry rework slice gated on PRODUCT-TRIAC-001 +
PACKAGE-TRIAC-001),
[`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md)
(§TRIAC / S360-320 WebFlash posture; exposure class table; family
row),
[`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
(§TRIAC / S360-320 release posture; release class table; family
row),
[`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md)
(§Blocked, legacy-compatible, deprecated, and removed — adds the
"`blocked` does not mean removed or hidden" clarification; S360-320
snapshot row updated from "intent only" to "policy-recorded by
PRODUCT-TRIAC-001"),
[`docs/product-onboarding.md`](product-onboarding.md) (§What not to
do — adds the "Advanced / manual-warning products are not standard
onboarding" rule),
[`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
(FanTRIAC carve-out clarified — `RELEASE-006` preview-to-stable does
**not** apply; FanTRIAC's release class is
`advanced/manual-warning-artifact-only`, owned by `WF-TRIAC-001` /
`RELEASE-TRIAC-001` / `WF-IMPORT-TRIAC-001`), and
[`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
(§`S360-320` Sense360 TRIAC — Role and Productization paragraphs
updated to reflect policy-recorded posture). Documentation only and
explicitly **does not**: edit
[`config/hardware-catalog.json`](../config/hardware-catalog.json),
[`config/webflash-builds.json`](../config/webflash-builds.json), or
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json);
edit any product YAML under [`products/`](../products/) (including
[`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml));
edit any WebFlash wrapper under
[`products/webflash/`](../products/webflash/) (including
[`products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml));
edit any package YAML under [`packages/`](../packages/) (including
[`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml));
edit any script under [`scripts/`](../scripts/); edit any test
under [`tests/`](../tests/); edit any workflow under
[`.github/workflows/`](../.github/workflows/); edit any component
under [`components/`](../components/); edit any header under
[`include/`](../include/); edit any firmware sources or manifests
([`firmware/sources.json`](../firmware/sources.json),
[`manifest.json`](../manifest.json)); add or modify any new
lifecycle enum value; unblock FanTRIAC under HW-005
(`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`,
`blocker: HW-005`, `webflash_build_matrix: false`); clear
COMPLIANCE-001 for `S360-320` or `S360-400` (compliance status is
owned by
[`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md));
claim that FanTRIAC is compliance-certified; promote `S360-320` to
`preview` / `stable` / `production`; add a `FanTRIAC` token to any
Release-One or preview config string; add a `FanTRIAC`-bearing
entry to
[`config/webflash-builds.json`](../config/webflash-builds.json);
add FanTRIAC to `release_one_required_configs` / REQUIRED_CONFIGS;
add FanTRIAC to any kit / default onboarding flow; make FanTRIAC
recommended; generate firmware; create a GitHub Release or tag;
perform a WebFlash import; change Release-One
(`Ceiling-POE-VentIQ-RoomIQ`,
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
`v1.0.0`); change the LED preview path
(`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`,
`channel: preview`); resolve HW-005, COMPLIANCE-001,
`HW-PINMAP-320-FOLLOWUP`, or PACKAGE-TRIAC-001. Adds no edits to
[`config/hardware-catalog.json`](../config/hardware-catalog.json),
[`config/webflash-builds.json`](../config/webflash-builds.json),
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
[`products/*`](../products/), [`products/webflash/*`](../products/webflash/),
[`packages/*`](../packages/), [`scripts/*`](../scripts/),
[`tests/*`](../tests/), [`.github/workflows/*`](../.github/workflows/),
[`components/*`](../components/), [`include/*`](../include/),
[`manifest.json`](../manifest.json), or
[`firmware/sources.json`](../firmware/sources.json). Cross-linked
from
[`docs/hardware/s360-320-r4-triac.md`](hardware/s360-320-r4-triac.md)
(Advanced / manual-warning product posture; Follow-up PR sequence),
[`docs/product-readiness-matrix.md`](product-readiness-matrix.md)
(FanTRIAC family section; Product readiness table; Follow-up PR
sequence),
[`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md)
(TRIAC / S360-320 WebFlash posture; FanTRIAC family row),
[`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
(TRIAC / S360-320 release posture; FanTRIAC family row),
[`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md)
(Blocked discussion; S360-320 snapshot row),
[`docs/product-onboarding.md`](product-onboarding.md) (What not to
do — advanced / manual-warning rule),
[`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
(FanTRIAC carve-out), and
[`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
(§`S360-320` Sense360 TRIAC). Source of truth consumed:
[`docs/hardware/s360-320-r4-triac.md` Advanced / manual-warning product posture](hardware/s360-320-r4-triac.md#advanced--manual-warning-product-posture)
(intended long-term posture);
[`config/product-catalog.json`](../config/product-catalog.json) (the
catalog entry whose `notes` field is updated); the existing
HW-005 record at
[`docs/release-one-hardware-audit.md#fantriac-mapping-resolution`](release-one-hardware-audit.md#fantriac-mapping-resolution);
the existing COMPLIANCE-001 tracker at
[`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md).

## PRODUCT-TRIAC-002 update (deferred — PACKAGE-TRIAC-001 not landed)

PRODUCT-TRIAC-002 is the **FanTRIAC product YAML / catalog-entry
rework** slice that would, when its readiness gates clear, decide
whether to retain `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` as the
canonical FanTRIAC shape or to add an alternative variant, remove
the placeholder `fan_triac_gate_pin: GPIO5` /
`fan_triac_zc_pin: GPIO6` from
[`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml),
and route the product through the
[`docs/product-onboarding.md`](product-onboarding.md) safe
sequence. PRODUCT-TRIAC-002 was investigated in this PR against
the readiness gates recorded in
[`docs/product-readiness-matrix.md`](product-readiness-matrix.md)
and
[`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
and is **confirmed deferred**: every gate it depends on is still
open. `PACKAGE-TRIAC-001` has not landed
([`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml)
still carries the BLOCKED / UNVERIFIED banner and the
`ac_dimmer` driver topology that requires direct interrupt-capable
ESP32 GPIOs for both `gate_pin` and `zero_cross_pin`); the
placeholder `fan_triac_gate_pin: GPIO5` / `fan_triac_zc_pin: GPIO6`
in the blocked reference product YAML still collide with the
RoomIQ J10 nets (`IO5 = SEN0609_TX`, `IO6 = out(gpio6)`); `HW-005`
([`docs/release-one-hardware-audit.md#fantriac-mapping-resolution`](release-one-hardware-audit.md#fantriac-mapping-resolution))
is unresolved; `HW-PINMAP-320-FOLLOWUP` (the standalone
schematic-backed reference doc + pin-map reconciliation called
out in
[`docs/hardware/s360-320-r4-triac.md`](hardware/s360-320-r4-triac.md))
is outstanding; `COMPLIANCE-001` advanced / manual-warning
sign-off ([`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md))
has not landed. Because PRODUCT-TRIAC-002's named prerequisite —
`PACKAGE-TRIAC-001` — has not landed, the per-family decision
rule in
[`docs/product-readiness-matrix.md` §FanTRIAC / S360-320](product-readiness-matrix.md#fantriac--s360-320)
forbids any product YAML or catalog implementation in this PR.
The update is therefore **docs-only**: this section records the
investigation outcome and the deferral; the FanTRIAC follow-up
bullet and the Follow-up PR sequence row in
[`docs/product-readiness-matrix.md`](product-readiness-matrix.md)
are tightened to explicitly state PRODUCT-TRIAC-002 was
investigated and confirmed deferred, and to cross-link this
section. No structural change is made anywhere else. The
blocked-reference product YAML
[`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml)
is unchanged; the BLOCKED / UNVERIFIED banner, the
`fallback_ssid: "S360 TRIAC BLOCKED"` admonition, and the
placeholder `fan_triac_gate_pin: GPIO5` / `fan_triac_zc_pin: GPIO6`
all stay. The blocked-reference WebFlash wrapper
[`products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml)
is unchanged and stays out of the build matrix. The package YAML
[`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml)
is unchanged; its BLOCKED / UNVERIFIED banner, its mains-voltage
/ qualified-electrician warnings, and its `ac_dimmer` driver
topology all remain in place. The FanTRIAC catalog entry in
[`config/product-catalog.json`](../config/product-catalog.json)
(`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`) is unchanged — `status`
stays `blocked`, `blocker` stays `HW-005`, `reason` is unchanged,
`webflash_build_matrix` stays `false`, no `artifact_name` is
added, and the `notes` field reclassified by PRODUCT-TRIAC-001 to
advanced / manual-warning is preserved verbatim. The
`lifecycle_statuses` enum in
[`config/product-catalog.json`](../config/product-catalog.json) is
unchanged. The `FanTRIAC` token remains in `canonical_modules` in
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
the Release-One `release_one_required_configs` stays
`["Ceiling-POE-VentIQ-RoomIQ"]`, and `FanTRIAC` remains in the
Release-One and LED preview `blocked_modules` lists in
[`config/product-catalog.json`](../config/product-catalog.json).
HW-005 and COMPLIANCE-001 remain open and unresolved; this update
makes no compliance claim. Every exclusion is durable and
explicitly reaffirmed: **not** Release-One, **not**
`REQUIRED_CONFIGS`, **not** recommended, **not** kit / default,
**not** compliance-certified — irrespective of any future product
YAML, WebFlash wrapper, build, release, or import existence.
Documentation only and explicitly **does not**: edit
[`config/hardware-catalog.json`](../config/hardware-catalog.json),
[`config/product-catalog.json`](../config/product-catalog.json),
[`config/webflash-builds.json`](../config/webflash-builds.json), or
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json);
edit any product YAML under [`products/`](../products/) (including
[`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml));
edit any WebFlash wrapper under
[`products/webflash/`](../products/webflash/) (including
[`products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml));
edit any package YAML under [`packages/`](../packages/) (including
[`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml));
edit any script under [`scripts/`](../scripts/); edit any test
under [`tests/`](../tests/); edit any workflow under
[`.github/workflows/`](../.github/workflows/); edit any component
under [`components/`](../components/); edit any header under
[`include/`](../include/); edit any firmware sources or manifests
([`firmware/sources.json`](../firmware/sources.json),
[`manifest.json`](../manifest.json)); add or modify any
lifecycle enum value; add or modify any `canonical_modules`
token, any `release_one_required_configs` membership, any
build-matrix entry, any `webflash_build_matrix` flip, any
`artifact_name`, any release tag, or any new channel; unblock
FanTRIAC under HW-005 (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`
stays `status: blocked`, `blocker: HW-005`,
`webflash_build_matrix: false`); clear COMPLIANCE-001 for
`S360-320` or `S360-400` (compliance status is owned by
[`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md));
claim that FanTRIAC is compliance-certified; promote `S360-320`
to `preview` / `stable` / `production`; add a `FanTRIAC` token to
any Release-One or preview config string; add a `FanTRIAC`-bearing
entry to
[`config/webflash-builds.json`](../config/webflash-builds.json);
add FanTRIAC to `release_one_required_configs` / REQUIRED_CONFIGS;
add FanTRIAC to any kit / default onboarding flow; make FanTRIAC
recommended; generate firmware; create a GitHub Release or tag;
perform a WebFlash import; change Release-One
(`Ceiling-POE-VentIQ-RoomIQ`,
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
`v1.0.0`); change the LED preview path
(`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`,
`channel: preview`); resolve HW-005, COMPLIANCE-001,
`HW-PINMAP-320-FOLLOWUP`, or `PACKAGE-TRIAC-001`. Adds no edits
to [`config/hardware-catalog.json`](../config/hardware-catalog.json),
[`config/product-catalog.json`](../config/product-catalog.json),
[`config/webflash-builds.json`](../config/webflash-builds.json),
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
[`products/*`](../products/),
[`products/webflash/*`](../products/webflash/),
[`packages/*`](../packages/), [`scripts/*`](../scripts/),
[`tests/*`](../tests/), [`.github/workflows/*`](../.github/workflows/),
[`components/*`](../components/), [`include/*`](../include/),
[`manifest.json`](../manifest.json), or
[`firmware/sources.json`](../firmware/sources.json). The remaining
chain after PRODUCT-TRIAC-002 stays exactly as recorded in
[`docs/product-readiness-matrix.md` Follow-up PR sequence](product-readiness-matrix.md#follow-up-pr-sequence)
and
[`docs/hardware/s360-320-r4-triac.md` Follow-up PR sequence](hardware/s360-320-r4-triac.md#follow-up-pr-sequence):
`HW-005` unblock (Option (a) direct-ESP32 pair or Core respin) +
`HW-PINMAP-320-FOLLOWUP` + bench timing / waveform / real-load
evidence + `COMPLIANCE-001` advanced / manual-warning sign-off →
`PACKAGE-TRIAC-001` → `PRODUCT-TRIAC-002` (this slice; **deferred
until those prerequisites land**) → `WF-TRIAC-001` (advanced-flow
WebFlash wrapper / catalog / build with the manual-warning UX
gate) → `RELEASE-TRIAC-001` (advanced-channel build / release
artifact) → `WF-IMPORT-TRIAC-001` (advanced / manual artifact
import). Cross-linked from
[`docs/product-readiness-matrix.md` §FanTRIAC / S360-320](product-readiness-matrix.md#fantriac--s360-320)
and the Follow-up PR sequence
`PRODUCT-TRIAC-002` row. Source of truth consumed:
[`docs/hardware/s360-320-r4-triac.md` Advanced / manual-warning product posture](hardware/s360-320-r4-triac.md#advanced--manual-warning-product-posture)
(intended long-term posture);
[`docs/hardware/package-readiness-matrix.md` `fan_triac.yaml` / S360-320](hardware/package-readiness-matrix.md#fan_triacyaml--s360-320)
(PACKAGE-TRIAC-001 prerequisites);
[`docs/release-one-hardware-audit.md#fantriac-mapping-resolution`](release-one-hardware-audit.md#fantriac-mapping-resolution)
(HW-005);
[`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
(COMPLIANCE-001); and the existing PRODUCT-TRIAC-001 catalog
reclassification recorded in
[§PRODUCT-TRIAC-001 update](#product-triac-001-update-reclassify-fantriac-as-advancedmanual-warning).

## PACKAGE-TRIAC-001 update (deferred — HW-005 / HW-PINMAP-320-FOLLOWUP / COMPLIANCE-001 not landed)

PACKAGE-TRIAC-001 is the **FanTRIAC package YAML reconciliation**
slice that would, when its readiness gates clear, reconcile
[`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml)
against the verified end-to-end direct-ESP32-GPIO pin pair, decide
whether the body of the package needs any edit beyond removing the
BLOCKED / UNVERIFIED banner (the topology may already be correct —
`output: ac_dimmer` on direct interrupt-capable ESP32 GPIOs supplied
via parent substitutions `fan_triac_gate_pin` / `fan_triac_zc_pin`),
preserve the mains-voltage / qualified-electrician warnings, and
preserve the advanced / manual-warning posture wording per
[`docs/hardware/s360-320-r4-triac.md` Advanced / manual-warning product posture](hardware/s360-320-r4-triac.md#advanced--manual-warning-product-posture).
PACKAGE-TRIAC-001 was investigated in this PR against the readiness
gates recorded in
[`docs/hardware/package-readiness-matrix.md` `fan_triac.yaml` / S360-320](hardware/package-readiness-matrix.md#fan_triacyaml--s360-320),
[`docs/hardware/s360-320-r4-triac.md` Package YAML status](hardware/s360-320-r4-triac.md#package-yaml-status),
and
[`docs/release-one-hardware-audit.md#fantriac-mapping-resolution`](release-one-hardware-audit.md#fantriac-mapping-resolution),
and is **confirmed deferred**: every gate it depends on is still
open. (1) `HW-005` is unresolved — the Core-side `TRI_GPIO1` /
`TRI_GPIO2` nets are visible only on the SX1509 (`U3`) side of the
Core sheet (per [`docs/hardware/s360-100-r4-core.md` §J15 — TRIAC fan module connector (4-pin)](hardware/s360-100-r4-core.md#j15--triac-fan-module-connector-4-pin),
[`docs/hardware/s360-100-r4-core.md` §Fan / driver outputs](hardware/s360-100-r4-core.md#fan--driver-outputs),
and Open Question #1); no direct interrupt-capable ESP32 GPIO trace
is established end-to-end through `S360-100-R4` + `S360-320`. Option
(a) of the HW-005 missing-evidence checklist
([`release-one-hardware-audit.md#missing-evidence-checklist`](release-one-hardware-audit.md#missing-evidence-checklist))
is unmet; Option (b) is **eliminated for this revision** of
`S360-320` (the committed module-side schematic at
[`docs/hardware/schematics/S360-320-R4.pdf`](hardware/schematics/S360-320-R4.pdf)
shows no on-board controller IC). (2) `HW-PINMAP-320-FOLLOWUP` is
outstanding — the standalone schematic-backed reference doc, the
`TRI_GPIO*` (Core) ↔ `ESP_GPIO*` (Module) canonical naming choice,
the end-to-end pin-map reconciliation, and the AC LINE `J1` 3-pin
function are all owed to that follow-up per
[`docs/hardware/s360-320-r4-triac.md` Follow-up PR sequence](hardware/s360-320-r4-triac.md#follow-up-pr-sequence).
(3) ESPHome's `ac_dimmer` driver continues to require direct
interrupt-capable ESP32 GPIOs for both `gate_pin` and
`zero_cross_pin`; the timing analysis in
[`docs/release-one-hardware-audit.md#timing-constraint-ac_dimmer-vs-sx1509-expander`](release-one-hardware-audit.md#timing-constraint-ac_dimmer-vs-sx1509-expander)
rejects the SX1509 expander as a viable source. No direct
interrupt-capable ESP32 GPIO pair has been proven for the FanTRIAC
nets on this revision. (4) No bench / waveform / real-load /
zero-cross / phase-control / thermal evidence has been recorded on
any populated `S360-100-R4` + `S360-320-R4` pair; the full
missing-evidence inventory is enumerated in
[`docs/hardware/s360-320-r4-triac.md` Required evidence before implementation](hardware/s360-320-r4-triac.md#required-evidence-before-implementation).
(5) `COMPLIANCE-001` is not cleared — the mains-voltage UK / EU
assessment tracker at
[`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
is documentation only and makes no compliance claim; creepage /
clearance / fusing / BOM / EMI / certification evidence remains
owed. (6) The placeholder `fan_triac_gate_pin: GPIO5` /
`fan_triac_zc_pin: GPIO6` in the blocked-reference product YAML
[`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml)
still collide with the RoomIQ J10 nets (`IO5 = SEN0609_TX`,
`IO6 = out(gpio6)`) per
[`docs/hardware/s360-100-r4-core.md` §Pin assignments](hardware/s360-100-r4-core.md#pin-assignments)
and
[`docs/hardware/s360-100-r4-core.md` §Release-One YAML pin reconciliation flag](hardware/s360-100-r4-core.md#release-one-yaml-pin-reconciliation-flag);
that resolution belongs to `PRODUCT-TRIAC-002`, not to
PACKAGE-TRIAC-001.

The package YAML itself is **already correctly authored** for the
state of the evidence: it exposes the two required pin choices as
substitutions (`fan_triac_gate_pin` / `fan_triac_zc_pin`) rather
than hardcoding GPIOs; it uses `output: ac_dimmer` matching the
module-side schematic topology (gate trigger through `MOC3023M`
optotriac, zero-cross sensed through `EL814` collector pull-up to
`+3V3`); it carries the BLOCKED / UNVERIFIED banner; it carries the
explicit "direct, interrupt-capable ESP32 GPIO" requirement and the
SX1509-rejection clause for both `gate_pin` and `zero_cross_pin`;
it carries the mains-voltage / qualified-electrician warnings; it
keeps `method: leading`, `init_with_half_cycle: true`,
`fan_triac_line_frequency: "50"` (parent override for 60 Hz
regions), and `fan_triac_min_power: "10"` as package-assumed
defaults; and it does not bind any specific GPIO value. The
topology is correct; what is missing is upstream evidence (the
Core re-trace, the bench / waveform / real-load proof, the
mains-voltage compliance posture) — none of which lives in this
file. **There is no safe functional package YAML edit available
today.** Because PACKAGE-TRIAC-001's named prerequisites — `HW-005`
unblock, `HW-PINMAP-320-FOLLOWUP`, bench timing / waveform /
real-load evidence, and `COMPLIANCE-001` advanced / manual-warning
sign-off — have not landed, the per-family decision rule in
[`docs/hardware/package-readiness-matrix.md` `fan_triac.yaml` / S360-320](hardware/package-readiness-matrix.md#fan_triacyaml--s360-320)
forbids any functional package YAML edit in this PR. The update is
therefore **docs-only**: this section records the investigation
outcome and the deferral; the `fan_triac.yaml` / S360-320 row in
[`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
and the **Package YAML status** section in
[`docs/hardware/s360-320-r4-triac.md`](hardware/s360-320-r4-triac.md)
are tightened to cross-link this entry and to state PACKAGE-TRIAC-001
was investigated and confirmed deferred. No structural change is
made anywhere else.

The `WF-TRIAC-001` slice has landed in the
[`sense360store/WebFlash`](https://github.com/sense360store/WebFlash)
repo as a runtime UX gate that makes FanTRIAC visible /
selectable in the WebFlash custom path as advanced / manual-warning
with explicit acknowledgement and install blocking. **It does not
satisfy any PACKAGE-TRIAC-001 gate.** WF-TRIAC-001 did not import
firmware, did not add a manifest build, did not change
REQUIRED_CONFIGS, did not add kits, did not promote FanTRIAC to
Release-One, did not claim compliance certification, and crucially
did not produce direct ESP32 GPIO trace evidence, bench / waveform /
real-load evidence, or COMPLIANCE-001 sign-off — all of which
PACKAGE-TRIAC-001 still requires from upstream hardware /
compliance work in this repo.

The package YAML
[`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml)
is unchanged; its BLOCKED / UNVERIFIED banner, its
direct-interrupt-capable-GPIO requirement, its SX1509-rejection
clause, its mains-voltage / qualified-electrician warnings, its
`output: ac_dimmer` topology, its
`fan_triac_gate_pin` / `fan_triac_zc_pin` substitutions, its default
`fan_triac_line_frequency: "50"`, `method: leading`,
`init_with_half_cycle: true`, and `fan_triac_min_power: "10"` all
remain in place. The blocked-reference product YAML
[`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml)
is unchanged; the BLOCKED / UNVERIFIED banner, the
`fallback_ssid: "S360 TRIAC BLOCKED"` admonition, and the
placeholder `fan_triac_gate_pin: GPIO5` / `fan_triac_zc_pin: GPIO6`
all stay. The blocked-reference WebFlash wrapper
[`products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml)
is unchanged and stays out of the build matrix. The FanTRIAC
catalog entry in
[`config/product-catalog.json`](../config/product-catalog.json)
(`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`) is unchanged — `status` stays
`blocked`, `blocker` stays `HW-005`, `reason` is unchanged,
`webflash_build_matrix` stays `false`, no `artifact_name` is added,
and the `notes` field reclassified by PRODUCT-TRIAC-001 to
advanced / manual-warning is preserved verbatim. The
`lifecycle_statuses` enum in
[`config/product-catalog.json`](../config/product-catalog.json) is
unchanged. The `FanTRIAC` token remains in `canonical_modules` in
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
the Release-One `release_one_required_configs` stays
`["Ceiling-POE-VentIQ-RoomIQ"]`, and `FanTRIAC` remains in the
Release-One and LED preview `blocked_modules` lists in
[`config/product-catalog.json`](../config/product-catalog.json).
The `S360-320` row in
[`config/hardware-catalog.json`](../config/hardware-catalog.json)
stays `schematic_status: cataloged_unverified` with no
`schematic_file` set. HW-005 and COMPLIANCE-001 remain open and
unresolved; this update makes no compliance claim. Every exclusion
is durable and explicitly reaffirmed: **not** Release-One, **not**
`REQUIRED_CONFIGS`, **not** recommended, **not** kit / default,
**not** compliance-certified — irrespective of any future product
YAML, WebFlash wrapper, build, release, or import existence, and
irrespective of WF-TRIAC-001 having landed on the WebFlash side.

Documentation only and explicitly **does not**: edit
[`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml)
(BLOCKED / UNVERIFIED banner, `ac_dimmer` topology, substitutions,
defaults, and mains-voltage / qualified-electrician warnings all
preserved); edit any other package YAML under
[`packages/`](../packages/) (including
[`packages/hardware/sense360_core.yaml`](../packages/hardware/sense360_core.yaml)
and
[`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml));
edit
[`config/hardware-catalog.json`](../config/hardware-catalog.json),
[`config/product-catalog.json`](../config/product-catalog.json),
[`config/webflash-builds.json`](../config/webflash-builds.json), or
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json);
edit any product YAML under [`products/`](../products/) (including
[`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml));
edit any WebFlash wrapper under
[`products/webflash/`](../products/webflash/) (including
[`products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml));
edit any script under [`scripts/`](../scripts/); edit any test
under [`tests/`](../tests/); edit any workflow under
[`.github/workflows/`](../.github/workflows/); edit any component
under [`components/`](../components/); edit any header under
[`include/`](../include/); edit any firmware sources or manifests
([`firmware/sources.json`](../firmware/sources.json),
[`manifest.json`](../manifest.json)); edit the curated artifact
index [`docs/hardware/artifacts/S360-320-R4.md`](hardware/artifacts/S360-320-R4.md)
or the schematic PDF
[`docs/hardware/schematics/S360-320-R4.pdf`](hardware/schematics/S360-320-R4.pdf)
(both byte-identical to HW-ASSETS-003); edit
[`docs/hardware/s360-100-r4-core.md`](hardware/s360-100-r4-core.md),
[`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md),
or
[`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
(owned by HW-005 / HW-PINMAP-320-FOLLOWUP / COMPLIANCE-001
respectively); add or modify any lifecycle enum value; add or
modify any `canonical_modules` token, any
`release_one_required_configs` membership, any build-matrix entry,
any `webflash_build_matrix` flip, any `artifact_name`, any release
tag, or any new channel; remove the BLOCKED / UNVERIFIED banner
from
[`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml);
remove the mains-voltage / qualified-electrician warnings; mark the
pin map confirmed; mark
[`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml)
`confirmed-ok`; unblock FanTRIAC under HW-005
(`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`,
`blocker: HW-005`, `webflash_build_matrix: false`); clear
COMPLIANCE-001 for `S360-320` or `S360-400` (compliance status is
owned by
[`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md));
claim that FanTRIAC is compliance-certified; promote `S360-320` to
`preview` / `stable` / `production`; add a `FanTRIAC` token to any
Release-One or preview config string; add a `FanTRIAC`-bearing
entry to
[`config/webflash-builds.json`](../config/webflash-builds.json);
add FanTRIAC to `release_one_required_configs` / REQUIRED_CONFIGS;
add FanTRIAC to any kit / default onboarding flow; make FanTRIAC
recommended; generate firmware; create a GitHub Release or tag;
perform a WebFlash import; change Release-One
(`Ceiling-POE-VentIQ-RoomIQ`,
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
`v1.0.0`); change the LED preview path
(`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`,
`channel: preview`); resolve HW-005, COMPLIANCE-001,
`HW-PINMAP-320-FOLLOWUP`, `PRODUCT-TRIAC-002`, `WF-TRIAC-001`
(landed in the WebFlash repo; not this repo's gate),
`RELEASE-TRIAC-001`, or `WF-IMPORT-TRIAC-001`. Adds no edits to
[`config/hardware-catalog.json`](../config/hardware-catalog.json),
[`config/product-catalog.json`](../config/product-catalog.json),
[`config/webflash-builds.json`](../config/webflash-builds.json),
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
[`products/*`](../products/),
[`products/webflash/*`](../products/webflash/),
[`packages/*`](../packages/), [`scripts/*`](../scripts/),
[`tests/*`](../tests/), [`.github/workflows/*`](../.github/workflows/),
[`components/*`](../components/), [`include/*`](../include/),
[`manifest.json`](../manifest.json), or
[`firmware/sources.json`](../firmware/sources.json). The remaining
chain after PACKAGE-TRIAC-001 stays exactly as recorded in
[`docs/hardware/package-readiness-matrix.md` Follow-up PR sequence](hardware/package-readiness-matrix.md#follow-up-pr-sequence)
and
[`docs/hardware/s360-320-r4-triac.md` Follow-up PR sequence](hardware/s360-320-r4-triac.md#follow-up-pr-sequence):
`HW-005` unblock (Option (a) direct-ESP32 pair or Core respin) +
`HW-PINMAP-320-FOLLOWUP` + bench timing / waveform / real-load
evidence + `COMPLIANCE-001` advanced / manual-warning sign-off →
`PACKAGE-TRIAC-001` (this slice; **deferred until those
prerequisites land**) → `PRODUCT-TRIAC-002` (FanTRIAC product YAML
/ catalog-entry rework; also currently deferred per
[§PRODUCT-TRIAC-002 update](#product-triac-002-update-deferred--package-triac-001-not-landed))
→ `WF-TRIAC-001` (advanced-flow WebFlash wrapper / catalog / build
with the manual-warning UX gate; runtime-UX slice landed in the
WebFlash repo, but the in-repo wrapper / catalog / build remains
outstanding) → `RELEASE-TRIAC-001` (advanced-channel build /
release artifact) → `WF-IMPORT-TRIAC-001` (advanced / manual
artifact import). Cross-linked from
[`docs/hardware/package-readiness-matrix.md` `fan_triac.yaml` / S360-320](hardware/package-readiness-matrix.md#fan_triacyaml--s360-320),
[`docs/hardware/package-readiness-matrix.md` Follow-up PR sequence `PACKAGE-TRIAC-001` row](hardware/package-readiness-matrix.md#follow-up-pr-sequence),
and
[`docs/hardware/s360-320-r4-triac.md` Package YAML status](hardware/s360-320-r4-triac.md#package-yaml-status).
Source of truth consumed:
[`docs/hardware/s360-320-r4-triac.md` Reconciliation findings](hardware/s360-320-r4-triac.md#reconciliation-findings),
[`docs/hardware/s360-320-r4-triac.md` Timing constraint against the package](hardware/s360-320-r4-triac.md#timing-constraint-against-the-package),
[`docs/hardware/s360-320-r4-triac.md` HW-005 evidence updates that do not unblock](hardware/s360-320-r4-triac.md#hw-005-evidence-updates-that-do-not-unblock),
[`docs/hardware/s360-320-r4-triac.md` Required evidence before implementation](hardware/s360-320-r4-triac.md#required-evidence-before-implementation),
[`docs/hardware/s360-100-r4-core.md` §J15 — TRIAC fan module connector (4-pin)](hardware/s360-100-r4-core.md#j15--triac-fan-module-connector-4-pin),
[`docs/hardware/s360-100-r4-core.md` §Fan / driver outputs](hardware/s360-100-r4-core.md#fan--driver-outputs),
[`docs/hardware/artifacts/S360-320-R4.md`](hardware/artifacts/S360-320-R4.md),
[`docs/release-one-hardware-audit.md#fantriac-mapping-resolution`](release-one-hardware-audit.md#fantriac-mapping-resolution),
[`docs/release-one-hardware-audit.md#timing-constraint-ac_dimmer-vs-sx1509-expander`](release-one-hardware-audit.md#timing-constraint-ac_dimmer-vs-sx1509-expander),
[`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md),
and the existing PRODUCT-TRIAC-001 / PRODUCT-TRIAC-002 entries
recorded in
[§PRODUCT-TRIAC-001 update](#product-triac-001-update-reclassify-fantriac-as-advancedmanual-warning)
and
[§PRODUCT-TRIAC-002 update](#product-triac-002-update-deferred--package-triac-001-not-landed).

## TRIAC-QUEUE-001 update (remaining FanTRIAC chain normalized after package deferral)

TRIAC-QUEUE-001 is a **docs-only queue normalization** that makes
the remaining FanTRIAC follow-up sequence explicit after
`PACKAGE-TRIAC-001` was investigated and deferred (see
[§PACKAGE-TRIAC-001 update](#package-triac-001-update-deferred--hw-005--hw-pinmap-320-followup--compliance-001-not-landed))
and `PRODUCT-TRIAC-002` was confirmed deferred (see
[§PRODUCT-TRIAC-002 update](#product-triac-002-update-deferred--package-triac-001-not-landed)).
The purpose of this update is to prevent accidental downstream
work on `PRODUCT-TRIAC-002`, `WF-TRIAC-001` (in-repo wrapper /
catalog / build slice), `RELEASE-TRIAC-001`, or
`WF-IMPORT-TRIAC-001` while their named prerequisites — `HW-005`,
`HW-PINMAP-320-FOLLOWUP`, bench / waveform / real-load evidence,
and `COMPLIANCE-001` advanced / manual-warning sign-off — remain
open.

**Queue state after PACKAGE-TRIAC-001 deferral.**

- `PACKAGE-TRIAC-001` — **investigated and deferred** (per
  [§PACKAGE-TRIAC-001 update](#package-triac-001-update-deferred--hw-005--hw-pinmap-320-followup--compliance-001-not-landed)).
  The named prerequisites `HW-005` unblock, `HW-PINMAP-320-FOLLOWUP`,
  bench / waveform / real-load timing evidence, and `COMPLIANCE-001`
  advanced / manual-warning sign-off have not landed.
  [`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml)
  is unchanged.
- `PRODUCT-TRIAC-002` — **remains deferred** (per
  [§PRODUCT-TRIAC-002 update](#product-triac-002-update-deferred--package-triac-001-not-landed)).
  The product YAML / catalog-entry rework cannot proceed because
  its named prerequisite `PACKAGE-TRIAC-001` has not landed, and
  the upstream `HW-005` / `HW-PINMAP-320-FOLLOWUP` / `COMPLIANCE-001`
  gates remain open.
  [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml)
  and the `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` catalog entry in
  [`config/product-catalog.json`](../config/product-catalog.json)
  are unchanged (`status: blocked`, `blocker: HW-005`,
  `webflash_build_matrix: false`, no `artifact_name`; the
  PRODUCT-TRIAC-001 notes-only reclassification is preserved
  verbatim).
- `RELEASE-TRIAC-001` — **blocked after PACKAGE-TRIAC-001 deferral**.
  No advanced-channel build, no GitHub Release, no signing, no
  checksums, no build-info `manifest.json`, no release-proof row
  in [`docs/webflash-release-proof.md`](webflash-release-proof.md).
  Its named prerequisites
  (`WF-TRIAC-001` in-repo wrapper / catalog / build, `HW-005`
  unblock, `COMPLIANCE-001` advanced sufficiently for the
  advanced channel) are not satisfied.
- `WF-IMPORT-TRIAC-001` — **blocked after PACKAGE-TRIAC-001 deferral**.
  No WebFlash-side import behind manual-warning UX. Its named
  prerequisite `RELEASE-TRIAC-001` is not satisfied.

**WF-TRIAC-001 runtime UX vs in-repo wrapper / catalog / build.**
The `WF-TRIAC-001` slice has **landed in the
[`sense360store/WebFlash`](https://github.com/sense360store/WebFlash)
repo as a runtime UX-only gate**: FanTRIAC is now visible /
selectable in the WebFlash custom path as advanced /
manual-warning with explicit acknowledgement and install
blocking. **The runtime UX slice does not unblock
`PACKAGE-TRIAC-001`, `PRODUCT-TRIAC-002`, `RELEASE-TRIAC-001`,
or `WF-IMPORT-TRIAC-001`.** It did not produce direct ESP32 GPIO
trace evidence, did not produce bench / waveform / real-load
evidence, did not clear `COMPLIANCE-001`, did not import
firmware, did not add a manifest build, did not flip
`webflash_build_matrix` to `true`, did not change
REQUIRED_CONFIGS, did not add kits, did not promote FanTRIAC to
Release-One, and did not produce the in-repo `WF-TRIAC-001`
wrapper under
[`products/webflash/`](../products/webflash/) /
catalog flip in
[`config/product-catalog.json`](../config/product-catalog.json) /
build-matrix row in
[`config/webflash-builds.json`](../config/webflash-builds.json).
The in-repo `WF-TRIAC-001` wrapper / catalog / build slice
remains outstanding and is itself gated by `PRODUCT-TRIAC-002`
and `PACKAGE-TRIAC-001`, both deferred.

**Next actionable FanTRIAC work (evidence / compliance only).**
The only actionable downstream work today is **upstream
evidence and compliance**, not product / release / import work:

- `HW-005` unblock — direct interrupt-capable ESP32 GPIO trace
  end-to-end through `S360-100-R4` + `S360-320`, Option (a) per
  [`release-one-hardware-audit.md#missing-evidence-checklist`](release-one-hardware-audit.md#missing-evidence-checklist),
  or a Core revision respin. Option (b) on-board controller IC
  is eliminated for this `S360-320` revision per the committed
  module-side schematic.
- `HW-PINMAP-320-FOLLOWUP` — standalone schematic-backed
  reference doc; J3 ↔ J15 reconciliation; `TRI_GPIO*` / `ESP_GPIO*`
  canonical-naming choice; `ac_dimmer` ISR timing budget
  recomputation; AC LINE `J1` 3-pin function resolution against
  silkscreen / PCB-source evidence.
- Bench / waveform / real-load proof — `ac_dimmer` ISR runs
  against the reconciled pin pair on a populated board, on at
  least one real load, with measured zero-crossing edges,
  gate-trigger pulses, and the `EL814` zero-cross /
  optotriac-driver topology characterised.
- `COMPLIANCE-001` advanced / manual-warning sign-off — UK / EU
  mains-voltage compliance evidence; qualified-electrician
  acknowledgement; document approval per
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md).

`PRODUCT-TRIAC-002`, the in-repo `WF-TRIAC-001` wrapper / catalog
/ build slice, `RELEASE-TRIAC-001`, and `WF-IMPORT-TRIAC-001`
are **not** actionable until the evidence / compliance work
above lands.

**Exclusions (reaffirmed).** Every durable FanTRIAC exclusion
recorded by `PRODUCT-TRIAC-001`, `PRODUCT-TRIAC-002`, and
`PACKAGE-TRIAC-001` is reaffirmed verbatim and is **not**
relaxed by this update: **not** Release-One, **not**
`REQUIRED_CONFIGS`, **not** recommended, **not** kit / default,
**not** compliance-certified — irrespective of any future product
YAML, WebFlash wrapper, build, release, or import existence, and
irrespective of `WF-TRIAC-001` having landed as runtime UX on
the WebFlash side.

Documentation only and explicitly **does not**: edit
[`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml)
(BLOCKED / UNVERIFIED banner, `ac_dimmer` topology,
substitutions, defaults, and mains-voltage /
qualified-electrician warnings all preserved); edit any other
package YAML under [`packages/`](../packages/); edit
[`config/hardware-catalog.json`](../config/hardware-catalog.json),
[`config/product-catalog.json`](../config/product-catalog.json),
[`config/webflash-builds.json`](../config/webflash-builds.json),
or
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json);
edit any product YAML under [`products/`](../products/)
(including
[`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml));
edit any WebFlash wrapper under
[`products/webflash/`](../products/webflash/) (including
[`products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml));
edit any script under [`scripts/`](../scripts/); edit any test
under [`tests/`](../tests/); edit any workflow under
[`.github/workflows/`](../.github/workflows/); edit any
component under [`components/`](../components/); edit any
header under [`include/`](../include/); edit any firmware
sources or manifests
([`firmware/sources.json`](../firmware/sources.json),
[`manifest.json`](../manifest.json)); edit the curated artifact
index [`docs/hardware/artifacts/S360-320-R4.md`](hardware/artifacts/S360-320-R4.md)
or the schematic PDF
[`docs/hardware/schematics/S360-320-R4.pdf`](hardware/schematics/S360-320-R4.pdf)
(both byte-identical to HW-ASSETS-003); edit
[`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md),
[`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md),
[`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md),
[`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md),
or
[`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
(owned by HW-005 / HW-PINMAP-320-FOLLOWUP / COMPLIANCE-001
respectively); add or modify any lifecycle enum value; add or
modify any `canonical_modules` token, any
`release_one_required_configs` membership, any build-matrix
entry, any `webflash_build_matrix` flip, any `artifact_name`,
any release tag, or any new channel; remove the BLOCKED /
UNVERIFIED banner from
[`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml);
remove the mains-voltage / qualified-electrician warnings; mark
the pin map confirmed; unblock FanTRIAC under HW-005
(`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`,
`blocker: HW-005`, `webflash_build_matrix: false`); clear
`COMPLIANCE-001` for `S360-320` or `S360-400` (compliance
status is owned by
[`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md));
claim that FanTRIAC is compliance-certified; promote `S360-320`
to `preview` / `stable` / `production`; add a `FanTRIAC` token
to any Release-One or preview config string; add a
`FanTRIAC`-bearing entry to
[`config/webflash-builds.json`](../config/webflash-builds.json);
add FanTRIAC to `release_one_required_configs` /
REQUIRED_CONFIGS; add FanTRIAC to any kit / default onboarding
flow; make FanTRIAC recommended; generate firmware; create a
GitHub Release or tag; perform a WebFlash import; change
Release-One (`Ceiling-POE-VentIQ-RoomIQ`,
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
`v1.0.0`); change the LED preview path
(`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`,
`channel: preview`); resolve `HW-005`, `COMPLIANCE-001`,
`HW-PINMAP-320-FOLLOWUP`, or `PACKAGE-TRIAC-001`; advance
`PRODUCT-TRIAC-002`, the in-repo `WF-TRIAC-001` wrapper /
catalog / build slice, `RELEASE-TRIAC-001`, or
`WF-IMPORT-TRIAC-001` past their currently-blocked state.
Adds no edits to
[`config/hardware-catalog.json`](../config/hardware-catalog.json),
[`config/product-catalog.json`](../config/product-catalog.json),
[`config/webflash-builds.json`](../config/webflash-builds.json),
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
[`products/*`](../products/),
[`products/webflash/*`](../products/webflash/),
[`packages/*`](../packages/), [`scripts/*`](../scripts/),
[`tests/*`](../tests/),
[`.github/workflows/*`](../.github/workflows/),
[`components/*`](../components/), [`include/*`](../include/),
[`manifest.json`](../manifest.json), or
[`firmware/sources.json`](../firmware/sources.json).

The remaining chain after TRIAC-QUEUE-001 is recorded exactly
as in
[`docs/hardware/package-readiness-matrix.md` Follow-up PR sequence](hardware/package-readiness-matrix.md#follow-up-pr-sequence),
[`docs/hardware/s360-320-r4-triac.md` Follow-up PR sequence](hardware/s360-320-r4-triac.md#follow-up-pr-sequence),
[`docs/product-readiness-matrix.md` FanTRIAC / S360-320](product-readiness-matrix.md#fantriac--s360-320),
[`docs/webflash-exposure-readiness-matrix.md` TRIAC / S360-320 WebFlash posture](webflash-exposure-readiness-matrix.md#triac--s360-320-webflash-posture),
and
[`docs/release-artifact-readiness-matrix.md` TRIAC / S360-320 release posture](release-artifact-readiness-matrix.md#triac--s360-320-release-posture):
`HW-005` unblock (Option (a) direct-ESP32 pair or Core respin) +
`HW-PINMAP-320-FOLLOWUP` + bench timing / waveform / real-load
evidence + `COMPLIANCE-001` advanced / manual-warning sign-off →
`PACKAGE-TRIAC-001` (currently deferred) → `PRODUCT-TRIAC-002`
(currently deferred) → in-repo `WF-TRIAC-001` wrapper / catalog /
build slice (currently blocked; runtime UX slice has landed
separately in the WebFlash repo) → `RELEASE-TRIAC-001`
(currently blocked) → `WF-IMPORT-TRIAC-001` (currently
blocked). Cross-linked from
[§PACKAGE-TRIAC-001 update](#package-triac-001-update-deferred--hw-005--hw-pinmap-320-followup--compliance-001-not-landed),
[§PRODUCT-TRIAC-002 update](#product-triac-002-update-deferred--package-triac-001-not-landed),
and
[§PRODUCT-TRIAC-001 update](#product-triac-001-update-reclassify-fantriac-as-advancedmanual-warning).

## S360-100-BENCH-001 update (2026-05-18 evidence-pass investigation)

S360-100-BENCH-001 is a **docs-only evidence-pass investigation**
against the Core board bench / manufacturing tracking record at
[`docs/hardware/s360-100-r4-core.md` S360-100-BENCH-001 status](hardware/s360-100-r4-core.md#s360-100-bench-001-status).
The purpose of this update is to re-check, on 2026-05-18, whether
any new bench-side or manufacturing-side evidence has been
committed against the field-evidence and per-question tables in
that record since it was created, and to record the result of
that re-check as a dated audit-log entry. **The status remains
`pending — bench/manufacturing evidence required`.** No
per-question row has been promoted. No downstream gate moves.
Release-One is unchanged.

**Why this is the next actionable item.** The follow-up PR list
in [§Findings summary](#findings-summary) row 1 already names
`S360-100-BENCH-001 (Core bench / manufacturing pass)` as a
pending follow-up. FanTRIAC downstream work (`PRODUCT-TRIAC-002`,
in-repo `WF-TRIAC-001`, `RELEASE-TRIAC-001`,
`WF-IMPORT-TRIAC-001`) is explicitly blocked after
[§PACKAGE-TRIAC-001 update](#package-triac-001-update-deferred--hw-005--hw-pinmap-320-followup--compliance-001-not-landed)
and
[§TRIAC-QUEUE-001 update](#triac-queue-001-update-remaining-fantriac-chain-normalized-after-package-deferral),
so the next docs-only actionable work shifts onto evidence rather
than product / release / import slices. S360-100-BENCH-001 is the
broad Core-board evidence pass that the package-readiness matrix
(`bench-evidence-pending` rows for FanRelay, FanPWM, FanDAC,
FanTRIAC; Core abstract-bus row for `CORE-ABSTRACT-BUS-001`), the
PoE-PSU `J2` harness identity question (`HW-002` Open Question #6),
and the Core J10 vs RoomIQ J6 silkscreen verification all
forward-reference.

**Investigation scope.** The 2026-05-18 re-check inspected the
following committed files and re-confirmed each against the
S360-100-BENCH-001 evidence rules in
[`docs/hardware/s360-100-r4-core.md` §Status-language rules](hardware/s360-100-r4-core.md#status-language-rules):

- [`docs/hardware/schematics/S360-100-R4.pdf`](../docs/hardware/schematics/S360-100-R4.pdf)
  — schematic-tier evidence; already committed under HW-007
  (`schematic_status: verified` in
  [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  under HW-008). Schematic evidence cannot promote a bench /
  manufacturing-side row by itself per the evidence rules.
- [`docs/hardware/artifacts/S360-100-R4.md`](hardware/artifacts/S360-100-R4.md)
  — HW-ASSETS-002 curated artifact index. Records that BOM
  (`bc386261-S360100R4_BOM.xlsx`, 12,543 B), CPL
  (`d5bb9e7b-S360100R4pos.csv`, 4,803 B), Gerbers
  (`2248fe0e-S360100R4gerbers.zip`, 290,097 B, 4-layer
  `F_Cu` / `In1_Cu` / `In2_Cu` / `B_Cu`), and STEP
  (`0a7f7965-S360100R4.step`, 6,335,475 B) are
  **retained-but-not-committed** under HW-ASSETS-001 by SHA256
  pointer only. No KiCad schematic source, no KiCad PCB source,
  no KiCad project metadata, no packed archive, and no board
  images are committed. No manufacturing-artifact review
  findings have been recorded since the artifact index was
  added.
- [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  `S360-100` row — `schematic_status: verified`,
  `schematic_file: docs/hardware/schematics/S360-100-R4.pdf` (HW-008).
  This is schematic-tier evidence and is not changed by this
  re-check.
- [`docs/hardware/s360-100-r4-core.md`](hardware/s360-100-r4-core.md)
  Open Questions list and S360-100-BENCH-001 field-evidence and
  per-question tables — every row still reads `not recorded —
  pending bench/manufacturing evidence` or `pending —
  bench/manufacturing evidence required`. No operator initials,
  no review date, no observed board serial / batch, no observed
  silkscreen / J-numbering / harness / rail value, and no
  manufacturing-artifact review finding have been added since
  the record was created.
- [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
  `S360-100` row — already cross-references S360-100-BENCH-001
  as `pending — bench/manufacturing evidence required`. The
  productization-axis row (Release-One, LED preview, blocked
  FanTRIAC) is unchanged by this re-check.
- [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
  `bench-evidence-pending` legend and per-package rows for
  FanRelay (`packages/expansions/fan_relay.yaml`), FanPWM
  (`packages/expansions/fan_pwm.yaml`), FanDAC
  (`packages/expansions/fan_gp8403.yaml`), FanTRIAC
  (`packages/expansions/fan_triac.yaml`), and the Core
  abstract-bus row
  (`packages/hardware/sense360_core_ceiling.yaml` +
  `packages/hardware/sense360_core.yaml`) — none of these rows
  is moved off `bench-evidence-pending` or
  `schematic-evidence-pending` by this re-check.
- [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)
  PoE PSU + Core / RoomIQ connector findings — both rows still
  forward-reference S360-100-BENCH-001 as the bench-side
  companion. Neither is moved by this re-check. Required
  follow-ups #2 / #3 (Core abstract-bus rebind, alias
  `CORE-ABSTRACT-BUS-001`) are not advanced.
- [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md)
  Sense360 Core (`S360-100`) Evidence missing bullet — the
  remaining `verify` flags on `IO10` net label, `IO39`–`IO42` ↔
  TPx mapping, J6 1-to-13 / J10 1-to-12 silkscreen pin order
  stay unresolved. No row is moved.
- [`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
  Core J10 vs RoomIQ J6 row — stays
  `needs-silkscreen/bench-verification`. The Core abstract-bus
  systemic mismatch (`needs-package-change`) is unchanged.

**Outcome.** A dated audit-log entry recording the 2026-05-18
re-check is appended to
[`docs/hardware/s360-100-r4-core.md` §Audit log](hardware/s360-100-r4-core.md#audit-log)
under the existing `## S360-100-BENCH-001 status` heading. Every
row of the field-evidence table and per-question table in that
section stays `pending — bench/manufacturing evidence required` /
`not recorded — pending bench/manufacturing evidence`.

**Short cross-reference notes** are added to:

- [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
  `S360-100` §Open work bullet — records the 2026-05-18
  re-check confirms S360-100-BENCH-001 stays `pending —
  bench/manufacturing evidence required` and no per-question
  row has been promoted; HW-GAP-001 resolution scope is
  unchanged.
- [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)
  Findings table tail — short admonition that the 2026-05-18
  re-check does **not** move the PoE PSU `cataloged, schematic
  pending` row or the Core / RoomIQ connector `discrepancy`
  row. Release-One stays unchanged. None of the Required
  follow-ups is closed.
- [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
  §Status labels tail — short admonition that the 2026-05-18
  re-check does **not** move any package row off
  `bench-evidence-pending` or `schematic-evidence-pending`. The
  follow-up PR chain for every fan-driver slice and for
  `CORE-ABSTRACT-BUS-001` is unchanged.
- [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md)
  Sense360 Core §Evidence missing bullet — one-line
  cross-reference to the dated audit-log entry.

`docs/hardware/firmware-package-mapping-audit.md` and
`docs/hardware/artifacts/S360-100-R4.md` already
forward-reference S360-100-BENCH-001 correctly and are **not**
edited by this update.

**What this update does NOT do.** S360-100-BENCH-001 is
documentation-only. The 2026-05-18 re-check explicitly does
**not**:

- promote any field of the S360-100-BENCH-001 field-evidence
  table from `not recorded — pending bench/manufacturing
  evidence` to anything stronger;
- promote any per-question row from `pending —
  bench/manufacturing evidence required` to `partial`,
  `verified`, or `failed / blocked`;
- close any of the schematic-side Open Questions in
  [`docs/hardware/s360-100-r4-core.md` Open questions](hardware/s360-100-r4-core.md#open-questions--verification-needed)
  (J2 PoE harness identity, J6 / J10 silkscreen pin order,
  `IO10` net label, `IO39`–`IO42` ↔ TPx mapping,
  `AirQ_Led` / `AirQ_Status_Led` reuse, TRI_GPIO1 / TRI_GPIO2
  routing, IO5 / IO6 vs FanTRIAC);
- record any BOM, CPL, Gerber, drill, or STEP review finding
  (those artifacts remain retained-but-not-committed under
  HW-ASSETS-001; no review can be cited from this repo);
- commit KiCad schematic source, KiCad PCB source, KiCad
  project metadata, board images, or any packed archive
  (HW-ASSETS-002 records them as `not provided in this upload`;
  the 2026-05-18 re-check does not alter that record);
- flip `S360-100` `schematic_status` in
  [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  (already `verified` under HW-008; bench/manufacturing
  evidence is a separate axis);
- change Release-One. Release-One stays `Ceiling-POE-VentIQ-RoomIQ`,
  version `1.0.0`, channel `stable`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
  [`v1.0.0`](https://github.com/sense360store/esphome-public/releases/tag/v1.0.0);
- change the LED preview path
  (`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`,
  `channel: preview`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`);
- unblock FanTRIAC
  (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`,
  `blocker: HW-005`, `webflash_build_matrix: false`);
- close `HW-005`, `HW-PINMAP-310`, `HW-PINMAP-311`,
  `HW-PINMAP-312`, `HW-PINMAP-320`, `HW-PINMAP-320-FOLLOWUP`,
  `HW-PINMAP-400`, `HW-PINMAP-410`, `HW-PINMAP-410-FOLLOWUP`,
  `HW-ASSETS-310`, `HW-ASSETS-400`, `HW-ASSETS-410`,
  `PACKAGE-GAP-001`, `PRODUCT-GAP-001`, `WEBFLASH-GAP-001`,
  `RELEASE-GAP-001`, `WF-IMPORT-GAP-001`, `PACKAGE-TRIAC-001`,
  `PRODUCT-TRIAC-002`, `WF-TRIAC-001`, `RELEASE-TRIAC-001`,
  `WF-IMPORT-TRIAC-001`, or `COMPLIANCE-001`;
- advance `CORE-ABSTRACT-BUS-001` (alias for
  [`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups));
- claim that any bench evidence (operator observation,
  silkscreen photo, scope trace, continuity measurement,
  serial log) exists;
- claim that any manufacturing-artifact review (BOM, CPL,
  Gerber, drill, STEP) has been performed;
- claim that any compliance certification or mains-voltage
  assessment for `S360-320` or `S360-400` has been performed
  (owned by `COMPLIANCE-001`;
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md));
- edit any file under
  [`config/`](../config/), [`products/`](../products/),
  [`products/webflash/`](../products/webflash/),
  [`packages/`](../packages/), [`scripts/`](../scripts/),
  [`tests/`](../tests/),
  [`.github/workflows/`](../.github/workflows/),
  [`components/`](../components/), [`include/`](../include/),
  [`firmware/`](../firmware/),
  [`manifest.json`](../manifest.json), or
  [`firmware/sources.json`](../firmware/sources.json).

**When the next S360-100-BENCH-001 audit-log entry should be
recorded.** When committed evidence is added to this repository
that the S360-100-BENCH-001 field-evidence rules can cite:
operator-attributed silkscreen photos / scope or continuity
traces / serial logs against the open Core-board questions; a
committed manufacturing-artifact review record citing the
retained-but-not-committed BOM / CPL / Gerbers / STEP; or
committed KiCad source / Gerbers / BOM / CPL / STEP that the
audit can cite by repo path. Until then, the next audit-log
entry should report the same `pending` outcome with the new
inspection date.

## HW-PINMAP-320-FOLLOWUP update (2026-05-18 evidence-pass investigation)

HW-PINMAP-320-FOLLOWUP is a **docs-only evidence-pass
investigation** against the FanTRIAC pin-map / direct-GPIO /
timing / mains-compliance gates owed by the HW-PINMAP-320 audit
record at
[`docs/hardware/s360-320-r4-triac.md`](hardware/s360-320-r4-triac.md).
The purpose of this update is to re-check, on 2026-05-18, whether
any new committed evidence supports an end-to-end direct
interrupt-capable ESP32 GPIO trace through `S360-100-R4` +
`S360-320` reaching Core `J15` pins 2 / 3 (HW-005 Option (a)), a
replacement non-`ac_dimmer` path against an on-board controller
IC (HW-005 Option (b)), bench / scope / waveform / real-load /
zero-cross / phase-control / thermal / EMI validation of the
FanTRIAC package, silkscreen / KiCad PCB / Gerber / BOM evidence
resolving the AC LINE `J1` 3-pin (L / N / PE) function or
supporting any creepage / clearance / component-rating claim, a
`TRI_GPIO*` / `ESP_GPIO*` canonical-naming reconciliation, or a
COMPLIANCE-001 mains-voltage UK / EU sign-off — and to record the
result of that re-check as a dated audit-log entry in
[`docs/hardware/s360-320-r4-triac.md` HW-PINMAP-320-FOLLOWUP audit log](hardware/s360-320-r4-triac.md#hw-pinmap-320-followup-audit-log).
**The status remains `partial — schematic evidence available;
package reconciliation, timing validation, and
compliance/certification pending`.** No reconciliation row has
been promoted. No canonical-naming choice is recorded. The AC
LINE `J1` 3-pin function is not resolved. The Core-side source
ESP32 GPIO for `TRI_GPIO1` / `TRI_GPIO2` is not identified.
HW-005 stays blocked. PACKAGE-TRIAC-001 stays deferred. The
downstream FanTRIAC chain (`PRODUCT-TRIAC-002`, in-repo
`WF-TRIAC-001`, `RELEASE-TRIAC-001`, `WF-IMPORT-TRIAC-001`) stays
blocked. COMPLIANCE-001 stays in force. Release-One is unchanged.
The LED preview path is unchanged.

**Why this is the next actionable evidence item.** After
[§PACKAGE-TRIAC-001 update](#package-triac-001-update-deferred--hw-005--hw-pinmap-320-followup--compliance-001-not-landed)
deferred PACKAGE-TRIAC-001 explicitly until HW-005 /
HW-PINMAP-320-FOLLOWUP / COMPLIANCE-001 advance, and after
[§TRIAC-QUEUE-001 update](#triac-queue-001-update-remaining-fantriac-chain-normalized-after-package-deferral)
normalised the remaining FanTRIAC chain — `PRODUCT-TRIAC-002`,
in-repo `WF-TRIAC-001` wrapper / catalog / build slice,
`RELEASE-TRIAC-001`, and `WF-IMPORT-TRIAC-001` — as **blocked
until the upstream evidence / compliance gates clear**, the next
actionable FanTRIAC work is evidence rather than product /
release / import slices. The
[§S360-100-BENCH-001 update](#s360-100-bench-001-update-2026-05-18-evidence-pass-investigation)
of 2026-05-18 was the broad Core-board evidence pass; this
HW-PINMAP-320-FOLLOWUP update is its FanTRIAC-board companion. It
covers the schematic-side evidence path (Core `J15` source pin
for `TRI_GPIO1` / `TRI_GPIO2`), the package-side timing path
(`ac_dimmer` ISR vs SX1509-routed pins), the bench-side path
(zero-cross waveform, gate-trigger pulse, phase-control output,
thermal, EMI, real-load), and the COMPLIANCE-001-adjacent path
(AC LINE `J1` 3-pin function, creepage / clearance, component
voltage / power ratings) that the package-readiness matrix
(`timing/compliance-pending` + `needs-package-reconciliation` +
`blocked-from-standard-exposure` for FanTRIAC), the
board-readiness matrix (`S360-320` `blocked` + `compliance-gated`
rows), the firmware-package-mapping audit (`fan_triac.yaml`
`blocked` row), and the remaining-board-documentation audit
(`Sense360 TRIAC (S360-320)` `blocked` + `not-needed-for-release-one`
classification) all forward-reference.

**Investigation scope.** The 2026-05-18 re-check inspected the
following committed files and re-confirmed each against the
HW-PINMAP-320 reconciliation rules in
[`docs/hardware/s360-320-r4-triac.md`](hardware/s360-320-r4-triac.md)
and the HW-005 missing-evidence rules in
[`docs/release-one-hardware-audit.md` Missing evidence checklist](release-one-hardware-audit.md#missing-evidence-checklist):

- [`docs/hardware/schematics/S360-320-R4.pdf`](../docs/hardware/schematics/S360-320-R4.pdf)
  — HW-ASSETS-003 module-side schematic, byte-identical to the
  upload (SHA256
  `4cd0685251dcdbc7aa8933cbfa92008df46940b6349f0dea91d32e1028c2911f`,
  54,565 bytes). Schematic-tier evidence; not changed by this
  re-check. Confirms the discrete `MOC3023M` + `BT136` + `EL814`
  topology (specifically `Q1 BT136S-600D,118`, `U1 MOC3023M`,
  `OK1 EL814`) with no on-board controller IC, no MCU, and no
  I²C peripheral, which **continues to eliminate HW-005 Option
  (b) for this `S360-320` revision**.
- [`docs/hardware/artifacts/S360-320-R4.md`](hardware/artifacts/S360-320-R4.md)
  — HW-ASSETS-003 curated artifact index. Records the visible
  schematic content, the module-side `J3` 4-pin pinout
  (`+3V3` / `ESP_GPIO1` / `ESP_GPIO2` / `GND`), the AC LINE `J1`
  3-pin connector (function unrecorded), the LOAD `J2` 2-pin
  connector, and the artifact-side Open Questions. KiCad
  schematic source, KiCad PCB source, KiCad project metadata,
  BOM, CPL, Gerbers, drill files, STEP, and board images all
  remain marked `not provided in this upload` per
  [`docs/hardware/artifacts/S360-320-R4.md` Files NOT provided in this upload](hardware/artifacts/S360-320-R4.md#files-not-provided-in-this-upload).
  No new artifact has been added since HW-ASSETS-003.
- [`docs/hardware/s360-320-r4-triac.md`](hardware/s360-320-r4-triac.md)
  — HW-PINMAP-320 audit doc. Status row stays `partial —
  schematic evidence available; package reconciliation, timing
  validation, and compliance/certification pending`. Every row
  of the [Connector / pin-map findings](hardware/s360-320-r4-triac.md#connector--pin-map-findings),
  [Reconciliation flag classification](hardware/s360-320-r4-triac.md#reconciliation-flag-classification),
  and [Reconciliation findings](hardware/s360-320-r4-triac.md#reconciliation-findings)
  tables is unchanged. The
  [Net-name divergence: `TRI_GPIO*` vs `ESP_GPIO*`](hardware/s360-320-r4-triac.md#net-name-divergence-tri_gpio-vs-esp_gpio)
  section continues to record the divergence as `conflict /
  unresolved`. The
  [Timing constraint against the package](hardware/s360-320-r4-triac.md#timing-constraint-against-the-package)
  section and the
  [HW-005 evidence updates that do **not** unblock](hardware/s360-320-r4-triac.md#hw-005-evidence-updates-that-do-not-unblock)
  section remain authoritative. The
  [Known unresolved issues](hardware/s360-320-r4-triac.md#known-unresolved-issues)
  inventory is unchanged.
- [`docs/hardware/s360-100-r4-core.md`](hardware/s360-100-r4-core.md)
  §[J15 — TRIAC fan module connector (4-pin)](hardware/s360-100-r4-core.md#j15--triac-fan-module-connector-4-pin),
  §[Fan / driver outputs](hardware/s360-100-r4-core.md#fan--driver-outputs),
  §[Release-One YAML pin reconciliation flag](hardware/s360-100-r4-core.md#release-one-yaml-pin-reconciliation-flag),
  and §[Open Questions #1](hardware/s360-100-r4-core.md#open-questions--verification-needed)
  — Core-side `J15` 4-pin connector capture
  (`+3.3V` / `TRI_GPIO1` / `TRI_GPIO2` / `GND`); `TRI_GPIO1` /
  `TRI_GPIO2` source pins still **not visible as direct ESP32
  GPIOs** on the Core sheet; the nets still appear only on the
  J15 / SX1509 (`U3`) side. **HW-005 Option (a) remains unmet.**
  No edit to this doc.
- [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)
  §[FanTRIAC mapping resolution](release-one-hardware-audit.md#fantriac-mapping-resolution),
  §[Missing evidence checklist](release-one-hardware-audit.md#missing-evidence-checklist),
  §[Timing constraint: `ac_dimmer` vs SX1509 expander](release-one-hardware-audit.md#timing-constraint-ac_dimmer-vs-sx1509-expander),
  §[Re-verification](release-one-hardware-audit.md#re-verification),
  and §[Required follow-ups](release-one-hardware-audit.md#required-follow-ups)
  — HW-005 verdict stays `blocked`. The Missing evidence
  checklist boxes remain unchecked. The timing analysis (why the
  SX1509 cannot satisfy `ac_dimmer`'s ISR-timed gate firing
  across an I²C transaction) is unchanged. The Required
  follow-ups list is not advanced. A short
  `HW-PINMAP-320-FOLLOWUP re-check (2026-05-18)` admonition is
  added at the tail of the Findings block as a parallel of the
  existing `S360-100-BENCH-001 re-check (2026-05-18)` admonition;
  the [FanTRIAC mapping resolution](release-one-hardware-audit.md#fantriac-mapping-resolution)
  section body is not edited.
- [`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml)
  — BLOCKED / UNVERIFIED banner intact. `output: ac_dimmer`
  topology intact. `fan_triac_gate_pin` / `fan_triac_zc_pin`
  substitutions intact. `method: leading`,
  `init_with_half_cycle: true`, default
  `fan_triac_line_frequency: "50"`, `fan_triac_min_power: "10"`
  intact. SX1509-rejection clause intact. Mains-voltage /
  qualified-electrician warnings intact. **No edit.**
- [`packages/expansions/gpio_expander_sx1509.yaml`](../packages/expansions/gpio_expander_sx1509.yaml)
  — SX1509 channel map (0–3 fan PWM, 4–7 tach, 8–11 aux PWM,
  12–15 inputs) unchanged. **No channel allocated to
  `TRI_GPIO1` / `TRI_GPIO2`** — confirmed during this re-check
  so no SX1509-side allocation can be mistaken for a TRIAC path.
- [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml)
  — placeholder `fan_triac_gate_pin: GPIO5` /
  `fan_triac_zc_pin: GPIO6` intact, BLOCKED / UNVERIFIED banner
  intact, **provably disagrees** with the `S360-100-R4`
  schematic (`IO5 = SEN0609_TX` → RoomIQ J10 pin 4 and
  `IO6 = out(gpio6)` → RoomIQ J10 pin 5 are already claimed by
  RoomIQ on Release-One). **No edit.**
- [`products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml)
  — blocked WebFlash wrapper; retained as reference only; not in
  any build matrix. **No edit.**
- [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  `S360-320` row — `schematic_status: cataloged_unverified`, no
  `schematic_file`. **No edit.** The `HW-CATALOG-320`
  schematic-status promotion stays gated on HW-PINMAP-320-FOLLOWUP +
  HW-005 + COMPLIANCE-001 sufficiency.
- [`config/product-catalog.json`](../config/product-catalog.json)
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` entry —
  `status: blocked`, `blocker: HW-005`, `reason` unchanged,
  `webflash_build_matrix: false`, no `artifact_name`, advanced /
  manual-warning candidate posture recorded notes-only by
  PRODUCT-TRIAC-001. **No edit.**
- [`config/webflash-builds.json`](../config/webflash-builds.json)
  — no FanTRIAC-bearing build; the two existing builds
  (`Ceiling-POE-VentIQ-RoomIQ` stable;
  `Ceiling-POE-VentIQ-RoomIQ-LED` preview) are unchanged. **No
  edit.**
- [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  — `FanTRIAC` stays reserved in `canonical_modules` subject to
  the fan-driver `max-one-of` rule enforced by
  `FAN_DRIVER_TOKENS` in
  [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py);
  `FanTRIAC` stays in Release-One and LED preview
  `blocked_modules`. **No edit.**
- [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
  — COMPLIANCE-001 mains-voltage UK / EU assessment tracker.
  No new mains-voltage clearance, isolation-barrier measurement,
  creepage / clearance measurement, fusing / over-current-protection
  decision, PCB-finger / connector-rating decision, CE / UKCA /
  FCC / UL applicability decision, enclosure / ingress decision,
  or TRIAC-phase-cut-dimming-specific standards decision is
  recorded for `S360-320` (or `S360-400`). **No edit.**
- [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
  `S360-320` hardware-evidence and productization-axis rows and
  §[`S360-320` Sense360 TRIAC](hardware/board-readiness-matrix.md#s360-320-sense360-triac)
  board-by-board notes — `blocked` (HW-005) +
  `compliance-gated` (COMPLIANCE-001). A short cross-link to the
  new HW-PINMAP-320-FOLLOWUP audit log is appended to the
  `S360-320` notes; no row state changes.
- [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
  `fan_triac.yaml` row stays `timing/compliance-pending` +
  `needs-package-reconciliation` +
  `blocked-from-standard-exposure`; §[`fan_triac.yaml` / S360-320](hardware/package-readiness-matrix.md#fan_triacyaml--s360-320)
  detail unchanged. A short admonition parallel to the existing
  2026-05-18 S360-100-BENCH-001 admonition is added confirming
  the re-check does not move this row.
- [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md)
  §[Sense360 TRIAC (`S360-320`)](hardware/remaining-board-documentation-audit.md#sense360-triac-s360-320)
  — `blocked` (HW-005), `not-needed-for-release-one`. **No
  edit.**
- [`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
  FanTRIAC placeholder-GPIOs row — `blocked`. **No edit.**
- [`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md)
  `S360-320 Sense360 TRIAC` snapshot row — `blocked` +
  `compliance-gated`. **No edit.**
- This file —
  [§PRODUCT-TRIAC-001 update](#product-triac-001-update-reclassify-fantriac-as-advancedmanual-warning),
  [§PRODUCT-TRIAC-002 update](#product-triac-002-update-deferred--package-triac-001-not-landed),
  [§PACKAGE-TRIAC-001 update](#package-triac-001-update-deferred--hw-005--hw-pinmap-320-followup--compliance-001-not-landed),
  [§TRIAC-QUEUE-001 update](#triac-queue-001-update-remaining-fantriac-chain-normalized-after-package-deferral),
  [§S360-100-BENCH-001 update](#s360-100-bench-001-update-2026-05-18-evidence-pass-investigation)
  — the pre-existing FanTRIAC-chain updates this section
  follows. They are unchanged; this section appends after them.

**Outcome.** A dated audit-log entry recording the 2026-05-18
re-check is appended to
[`docs/hardware/s360-320-r4-triac.md` HW-PINMAP-320-FOLLOWUP audit log](hardware/s360-320-r4-triac.md#hw-pinmap-320-followup-audit-log)
under a newly-added `## HW-PINMAP-320-FOLLOWUP audit log`
heading (the doc had no audit-log section before this PR). Every
row of the
[Connector / pin-map findings](hardware/s360-320-r4-triac.md#connector--pin-map-findings),
[Reconciliation flag classification](hardware/s360-320-r4-triac.md#reconciliation-flag-classification),
and
[Reconciliation findings](hardware/s360-320-r4-triac.md#reconciliation-findings)
tables stays at its current value. Every item in the
[Known unresolved issues](hardware/s360-320-r4-triac.md#known-unresolved-issues)
list stays open.

**Short cross-reference notes** are added to:

- [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)
  Findings table tail — short admonition that the 2026-05-18
  HW-PINMAP-320-FOLLOWUP re-check does **not** move the
  [FanTRIAC mapping resolution](release-one-hardware-audit.md#fantriac-mapping-resolution),
  the
  [Missing evidence checklist](release-one-hardware-audit.md#missing-evidence-checklist),
  the
  [Timing constraint](release-one-hardware-audit.md#timing-constraint-ac_dimmer-vs-sx1509-expander)
  analysis, the [Re-verification](release-one-hardware-audit.md#re-verification)
  section, or the [Required follow-ups](release-one-hardware-audit.md#required-follow-ups).
  HW-005 stays blocked. The PoE PSU `cataloged, schematic
  pending` row and the Core / RoomIQ connector `discrepancy`
  row are also unchanged (already covered by the parallel
  S360-100-BENCH-001 re-check admonition).
- [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
  §Status labels tail — short admonition that the 2026-05-18
  HW-PINMAP-320-FOLLOWUP re-check does **not** move the
  `fan_triac.yaml` row off `timing/compliance-pending` +
  `needs-package-reconciliation` +
  `blocked-from-standard-exposure`. The `PACKAGE-TRIAC-001`
  follow-up PR chain is unchanged.
- [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
  §[`S360-320` Sense360 TRIAC](hardware/board-readiness-matrix.md#s360-320-sense360-triac)
  — short Open work bullet recording the re-check outcome:
  HW-005 Option (a) unmet, Option (b) eliminated, no bench /
  waveform / real-load / KiCad PCB / Gerber / BOM evidence, no
  canonical-naming choice, no COMPLIANCE-001 sign-off; no row
  state changes.

[`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md),
[`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md),
[`docs/hardware/artifacts/S360-320-R4.md`](hardware/artifacts/S360-320-R4.md),
[`docs/hardware/s360-100-r4-core.md`](hardware/s360-100-r4-core.md),
[`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md),
and
[`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
already forward-reference HW-PINMAP-320 / HW-005 / COMPLIANCE-001
correctly and are **not** edited by this update.

**What this update does NOT do.** HW-PINMAP-320-FOLLOWUP is
documentation-only. The 2026-05-18 re-check explicitly does
**not**:

- promote the HW-PINMAP-320 status away from `partial —
  schematic evidence available; package reconciliation, timing
  validation, and compliance/certification pending`;
- promote any row of the
  [Connector / pin-map findings](hardware/s360-320-r4-triac.md#connector--pin-map-findings),
  [Reconciliation flag classification](hardware/s360-320-r4-triac.md#reconciliation-flag-classification),
  or
  [Reconciliation findings](hardware/s360-320-r4-triac.md#reconciliation-findings)
  tables from `conflict / unresolved`,
  `Core-side captured only`, `needs-package-reconciliation`,
  `not recorded`, or any other current value to anything
  stronger;
- close any item in the
  [Known unresolved issues](hardware/s360-320-r4-triac.md#known-unresolved-issues)
  list (HW-005 unblock, COMPLIANCE-001, no verified pin map,
  no timing validation, no zero-cross / phase-control runtime
  proof, no real-load test evidence, no thermal
  characterisation, no EMI / compliance review, no bench /
  operator validation, no package YAML confirmation, no
  product / WebFlash exposure approval, hardware catalog not
  promoted to verified, not Release-One / not recommended /
  not kit / default / not REQUIRED_CONFIGS, no KiCad source /
  KiCad PCB / project metadata / BOM / CPL / gerbers / drill
  files / STEP / board images);
- resolve the `TRI_GPIO*` (Core) ↔ `ESP_GPIO*` (module)
  net-name divergence in
  [§Net-name divergence: `TRI_GPIO*` vs `ESP_GPIO*`](hardware/s360-320-r4-triac.md#net-name-divergence-tri_gpio-vs-esp_gpio);
- resolve the AC LINE `J1` 3-pin (L / N / PE / doubled-line)
  function;
- identify the Core-side source ESP32 GPIO for `TRI_GPIO1` or
  `TRI_GPIO2`;
- claim that the SX1509-routed Core path can be made to satisfy
  the `ac_dimmer` ISR-timed gate firing — it cannot, per
  [`release-one-hardware-audit.md#timing-constraint-ac_dimmer-vs-sx1509-expander`](release-one-hardware-audit.md#timing-constraint-ac_dimmer-vs-sx1509-expander);
- claim that HW-005 Option (b) is reintroducible on this
  `S360-320` revision — it is not (no on-board controller IC,
  no MCU, no I²C peripheral on the module side per
  [§Schematic summary](hardware/s360-320-r4-triac.md#schematic-summary)
  and
  [`artifacts/S360-320-R4.md` §What the schematic appears to contain](hardware/artifacts/S360-320-R4.md#what-the-schematic-appears-to-contain));
- claim that any bench / scope / waveform / real-load /
  zero-cross / phase-control / thermal / EMI evidence exists on
  a populated `S360-100-R4` + `S360-320-R4` pair (none does);
- record any KiCad schematic source, KiCad PCB source, KiCad
  project metadata, BOM, CPL, Gerbers, drill files, STEP, or
  board-image review finding for `S360-320-R4` (none has been
  committed; see
  [`docs/hardware/artifacts/S360-320-R4.md` Files NOT provided in this upload](hardware/artifacts/S360-320-R4.md#files-not-provided-in-this-upload));
- commit any KiCad schematic source, KiCad PCB source, KiCad
  project metadata, BOM, CPL, Gerbers, drill files, STEP, or
  board images for `S360-320-R4`;
- flip `S360-320` `schematic_status` in
  [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  away from `cataloged_unverified` or set `schematic_file`
  (the `HW-CATALOG-320` schematic-status promotion stays gated
  on HW-PINMAP-320-FOLLOWUP + HW-005 + COMPLIANCE-001
  sufficiency);
- mark
  [`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml)
  `confirmed-ok` (it stays `package-yaml-pending` /
  `needs-package-reconciliation`);
- remove the BLOCKED / UNVERIFIED banner from
  [`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml);
- remove the mains-voltage / qualified-electrician warnings
  from
  [`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml);
- edit
  [`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml)
  at all (the `output: ac_dimmer` topology, the
  `fan_triac_gate_pin` / `fan_triac_zc_pin` substitutions, the
  `method: leading`, `init_with_half_cycle: true`, default
  `fan_triac_line_frequency: "50"`, `fan_triac_min_power: "10"`,
  the SX1509-rejection clause, and the header comments are all
  preserved);
- edit
  [`packages/expansions/gpio_expander_sx1509.yaml`](../packages/expansions/gpio_expander_sx1509.yaml)
  (no channel is allocated to `TRI_GPIO1` / `TRI_GPIO2`, and
  nothing in this re-check changes the channel map);
- edit
  [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml)
  (the placeholder `fan_triac_gate_pin: GPIO5` /
  `fan_triac_zc_pin: GPIO6` substitutions stay; they remain
  provably wrong against the Core schematic);
- edit
  [`products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml);
- edit the
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` entry in
  [`config/product-catalog.json`](../config/product-catalog.json)
  (`status` stays `blocked`, `blocker` stays `HW-005`, `reason`
  is unchanged, `webflash_build_matrix` stays `false`, no
  `artifact_name`, advanced / manual-warning candidate posture
  recorded notes-only by PRODUCT-TRIAC-001 is preserved);
- add or change `release_one_required_configs` /
  `REQUIRED_CONFIGS` in
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json);
- add a FanTRIAC build to
  [`config/webflash-builds.json`](../config/webflash-builds.json);
- add a `FanTRIAC` token to any current or future config
  string;
- add FanTRIAC to any kit, recommended bundle, or default
  onboarding flow;
- make FanTRIAC recommended;
- generate firmware, create a GitHub Release or tag, or perform
  any WebFlash manifest / import operation;
- change Release-One (stays `Ceiling-POE-VentIQ-RoomIQ`,
  version `1.0.0`, channel `stable`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
  [`v1.0.0`](https://github.com/sense360store/esphome-public/releases/tag/v1.0.0));
- change the LED preview path
  (`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`,
  `channel: preview`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`);
- change the Sense360 LED Release-One exclusion;
- resolve the Core J10 vs RoomIQ J6 pin-order open question;
- advance CORE-ABSTRACT-BUS-001 (alias for
  [`release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups));
- close `HW-005`, `HW-PINMAP-310`, `HW-PINMAP-311`,
  `HW-PINMAP-312`, `HW-PINMAP-320`, `HW-PINMAP-320-FOLLOWUP`,
  `HW-PINMAP-400`, `HW-PINMAP-410`, `HW-PINMAP-410-FOLLOWUP`,
  `HW-ASSETS-310`, `HW-ASSETS-400`, `HW-ASSETS-410`,
  `HW-CATALOG-320`, `S360-100-BENCH-001`, `PACKAGE-GAP-001`,
  `PRODUCT-GAP-001`, `WEBFLASH-GAP-001`, `RELEASE-GAP-001`,
  `WF-IMPORT-GAP-001`, `PACKAGE-TRIAC-001`, `PRODUCT-TRIAC-002`,
  `WF-TRIAC-001`, `RELEASE-TRIAC-001`, `WF-IMPORT-TRIAC-001`,
  or `COMPLIANCE-001`;
- claim that any compliance certification, mains-voltage UK / EU
  assessment, CE / UKCA / FCC / UL applicability decision,
  isolation-barrier measurement, creepage / clearance
  measurement, fusing / over-current-protection decision, or
  enclosure / ingress decision has been performed for
  `S360-320` (or `S360-400`) — COMPLIANCE-001 owns the
  compliance gate at
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md);
- realise the long-term advanced / manual-warning posture per
  [`s360-320-r4-triac.md` Advanced / manual-warning product posture](hardware/s360-320-r4-triac.md#advanced--manual-warning-product-posture)
  beyond the wording-only PRODUCT-TRIAC-001 catalog notes edit
  that already landed (the JSON `status` stays `blocked`, no
  new lifecycle enum value, no advanced channel, no WebFlash
  wrapper edit, no build-matrix entry, no release artifact, no
  WebFlash import);
- treat the
  [`sense360store/WebFlash`](https://github.com/sense360store/WebFlash)
  runtime advanced / manual-warning UX `WF-TRIAC-001` slice as
  satisfying any HW-005 / HW-PINMAP-320-FOLLOWUP /
  PACKAGE-TRIAC-001 / PRODUCT-TRIAC-002 / in-repo
  `WF-TRIAC-001` / RELEASE-TRIAC-001 / WF-IMPORT-TRIAC-001 /
  COMPLIANCE-001 gate — it does not import firmware, does not
  add a manifest build, does not flip
  `webflash_build_matrix`, and does not change REQUIRED_CONFIGS
  or kits;
- edit any file under
  [`config/`](../config/), [`products/`](../products/),
  [`products/webflash/`](../products/webflash/),
  [`packages/`](../packages/), [`scripts/`](../scripts/),
  [`tests/`](../tests/),
  [`.github/workflows/`](../.github/workflows/),
  [`components/`](../components/), [`include/`](../include/),
  [`firmware/`](../firmware/),
  [`manifest.json`](../manifest.json), or
  [`firmware/sources.json`](../firmware/sources.json);
- edit
  [`docs/hardware/artifacts/S360-320-R4.md`](hardware/artifacts/S360-320-R4.md),
  [`docs/hardware/artifacts/S360-100-R4.md`](hardware/artifacts/S360-100-R4.md),
  [`docs/hardware/schematics/S360-320-R4.pdf`](hardware/schematics/S360-320-R4.pdf)
  (the schematic stays byte-identical to the HW-ASSETS-003
  commit; SHA256 unchanged),
  [`docs/hardware/s360-100-r4-core.md`](hardware/s360-100-r4-core.md),
  [`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md),
  [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md),
  or
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md).

**When the next HW-PINMAP-320-FOLLOWUP audit-log entry should
be recorded.** When committed evidence is added to this
repository that the field-evidence rules in
[`docs/hardware/s360-320-r4-triac.md` HW-PINMAP-320-FOLLOWUP audit log](hardware/s360-320-r4-triac.md#hw-pinmap-320-followup-audit-log)
can cite: a Core schematic re-trace (or a Core revision
respin landing as `S360-100-R5` or later) documenting an
end-to-end direct interrupt-capable ESP32 GPIO route to Core
`J15` pins 2 / 3 (HW-005 Option (a) per
[`release-one-hardware-audit.md#missing-evidence-checklist`](release-one-hardware-audit.md#missing-evidence-checklist));
a future `S360-320-R5` (or later) revision introducing an I²C
TRIAC controller IC plus a replacement non-`ac_dimmer` driver
(HW-005 Option (b)); committed KiCad PCB source, Gerbers, BOM,
or board images for `S360-320-R4` that the audit can cite by
repo path (also COMPLIANCE-001-adjacent for creepage /
clearance / component-rating evidence); operator-attributed
bench / scope / continuity / silkscreen / serial / real-load /
zero-cross / phase-control / thermal / EMI captures against a
populated `S360-100-R4` + `S360-320-R4` pair; committed
silkscreen evidence resolving the AC LINE `J1` 3-pin
(L / N / PE / doubled-line) function; a `TRI_GPIO*` /
`ESP_GPIO*` canonical-naming choice propagated into a future
standalone schematic-backed reference doc; or COMPLIANCE-001
advanced / manual-warning sign-off recorded in
[`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md).
Until any of those land, the next audit-log entry should
report the same `partial — schematic evidence available;
package reconciliation, timing validation, and
compliance/certification pending` outcome with the new
inspection date.

## COMPLIANCE-001 update (2026-05-18 mains-voltage advanced/manual-warning sign-off evidence-pass investigation)

COMPLIANCE-001 is a **docs-only evidence-pass investigation**
against the mains-voltage UK / EU compliance tracker at
[`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md).
The purpose of this update is to re-check, on 2026-05-18, whether
any new committed evidence supports (i) **standard-exposure
clearance** for `S360-320` under COMPLIANCE-001 (CE / UKCA / FCC /
UL / LVD / RED / EMC / RoHS conformity for the finished product
placed on the market); (ii) a **limited advanced / manual-warning
sign-off** that records, by named qualified party and date, the
scope of an advanced / manual-warning posture distinct from
compliance certification; or (iii) **formal compliance
certification** evidence (accredited test-lab report, signed
Declaration of Conformity, marking artwork, production-control
plan) for any `S360-320`-bearing finished product — and to record
the result of that re-check as a dated audit-log entry in
[`docs/compliance/mains-voltage-uk-eu-assessment.md` COMPLIANCE-001 audit log](compliance/mains-voltage-uk-eu-assessment.md#compliance-001-audit-log).
**COMPLIANCE-001 remains open / not cleared** for `S360-320`
under all three evaluation paths. No row of the COMPLIANCE-001
tracker is promoted from `Not proven by this repository` /
`To be confirmed` / `Requires qualified review` /
`Likely applicable` to anything stronger. No CE / UKCA / FCC /
UL / LVD / RED / EMC / RoHS conformity claim is produced. No
limited advanced / manual-warning sign-off is recorded (no
qualified-electrician / safety-review record on file). No
formal compliance certification is recorded (no accredited
test-lab report, no signed Declaration of Conformity, no
marking artwork, no production-control plan). The intended
advanced / manual-warning long-term product posture per
[`docs/hardware/s360-320-r4-triac.md` Advanced / manual-warning product posture](hardware/s360-320-r4-triac.md#advanced--manual-warning-product-posture)
stays **intent only** — the only realised piece is the
wording-only [`PRODUCT-TRIAC-001`](#product-triac-001-update-reclassify-fantriac-as-advancedmanual-warning)
catalog-notes edit, which is a policy-direction record and is
**not** a compliance sign-off. HW-005 stays blocked.
HW-PINMAP-320-FOLLOWUP stays outstanding. PACKAGE-TRIAC-001 stays
deferred. PRODUCT-TRIAC-002, in-repo WF-TRIAC-001,
RELEASE-TRIAC-001, and WF-IMPORT-TRIAC-001 stay blocked.
HW-ASSETS-400 / HW-PINMAP-400-FOLLOWUP / PACKAGE-POWER-400-001
stay outstanding for `S360-400`. Release-One is unchanged. The
LED preview path is unchanged.

**Why this is the next actionable evidence item.** After
[§PACKAGE-TRIAC-001 update](#package-triac-001-update-deferred--hw-005--hw-pinmap-320-followup--compliance-001-not-landed)
deferred PACKAGE-TRIAC-001 explicitly until HW-005 /
HW-PINMAP-320-FOLLOWUP / COMPLIANCE-001 advance, after
[§TRIAC-QUEUE-001 update](#triac-queue-001-update-remaining-fantriac-chain-normalized-after-package-deferral)
normalised the remaining FanTRIAC chain as **blocked until the
upstream evidence / compliance gates clear**, after
[§S360-100-BENCH-001 update](#s360-100-bench-001-update-2026-05-18-evidence-pass-investigation)
re-confirmed the broad Core-board bench / manufacturing evidence
remains pending, and after
[§HW-PINMAP-320-FOLLOWUP update](#hw-pinmap-320-followup-update-2026-05-18-evidence-pass-investigation)
re-confirmed the FanTRIAC-board pin-map / direct-GPIO / timing
evidence remains pending, the next docs-only actionable work on
the FanTRIAC chain is the **compliance side** — the
`COMPLIANCE-001` mains-voltage advanced / manual-warning sign-off
slice. It covers the schematic-side evidence path (AC LINE `J1`
3-pin function, isolation-barrier identity), the
fabrication-side path (PCB / KiCad / Gerbers / BOM / CPL / drill
/ STEP / board images for creepage / clearance / component
ratings), the bench-side path (real-load, thermal, EMI, conducted
/ radiated emissions, immunity, harmonics / flicker), the
regulatory path (CE / UKCA / FCC / UL applicability decision,
accredited test-lab report, signed Declaration of Conformity,
marking artwork, production-control plan), and the
qualified-review path (named qualified-electrician /
safety-review record with date, board serial / batch, scope
statement, and "**this is not compliance certification**"
framing) that the package-readiness matrix
(`timing/compliance-pending` + `needs-package-reconciliation` +
`blocked-from-standard-exposure` for FanTRIAC), the
board-readiness matrix (`S360-320` `blocked` +
`compliance-gated` rows), the firmware-package-mapping audit
(`fan_triac.yaml` `blocked` row), the
remaining-board-documentation audit (`Sense360 TRIAC (S360-320)`
`blocked` + `not-needed-for-release-one` classification), the
product-availability taxonomy, and every prior FanTRIAC chain
entry all forward-reference.

**Investigation scope.** The 2026-05-18 re-check inspected the
following committed files and re-confirmed each against the
COMPLIANCE-001 evidence standards at
[`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
(a schematic identifies components and nets but does **not** prove
compliance; an artifact index identifies missing files but does
**not** prove compliance; PCB / Gerber / KiCad / layout is needed
for creepage / clearance and isolation geometry; BOM / CPL is
needed for component ratings and assembly review; bench / thermal
/ EMI / real-load data is needed for operating behaviour; formal
certification requires actual certification / test evidence;
advanced / manual-warning sign-off can be a policy decision but
must clearly say it is **not** compliance certification;
compliance must not be inferred from "advanced / manual-warning
UX exists" nor from "schematic exists"):

- [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
  — COMPLIANCE-001 mains-voltage UK / EU assessment tracker.
  Every row of [Board table](compliance/mains-voltage-uk-eu-assessment.md#board-table),
  [Product classification — questions](compliance/mains-voltage-uk-eu-assessment.md#product-classification--questions),
  [Protection class — decision tree](compliance/mains-voltage-uk-eu-assessment.md#protection-class--decision-tree),
  [Standards and regulations — applicability checklist](compliance/mains-voltage-uk-eu-assessment.md#standards-and-regulations--applicability-checklist),
  [Electrical-safety topics — checklist](compliance/mains-voltage-uk-eu-assessment.md#electrical-safety-topics--checklist),
  [EMC topics — checklist](compliance/mains-voltage-uk-eu-assessment.md#emc-topics--checklist),
  [Evidence required before any "preview" promotion](compliance/mains-voltage-uk-eu-assessment.md#evidence-required-before-any-preview-promotion),
  [Evidence required before any "stable" / shipping promotion](compliance/mains-voltage-uk-eu-assessment.md#evidence-required-before-any-stable--shipping-promotion),
  [Technical-file checklist](compliance/mains-voltage-uk-eu-assessment.md#technical-file-checklist),
  [Declaration of Conformity — checklist](compliance/mains-voltage-uk-eu-assessment.md#declaration-of-conformity--checklist),
  [Open questions for compliance engineer / test lab](compliance/mains-voltage-uk-eu-assessment.md#open-questions-for-compliance-engineer--test-lab),
  [Release blockers](compliance/mains-voltage-uk-eu-assessment.md#release-blockers),
  and
  [Do-not-change / do-not-claim](compliance/mains-voltage-uk-eu-assessment.md#do-not-change--do-not-claim)
  stays at its current value. A new
  [§COMPLIANCE-001 audit log](compliance/mains-voltage-uk-eu-assessment.md#compliance-001-audit-log)
  section is appended to record the dated re-check.
- [`docs/hardware/schematics/S360-320-R4.pdf`](../docs/hardware/schematics/S360-320-R4.pdf)
  — HW-ASSETS-003 module-side schematic (SHA256
  `4cd0685251dcdbc7aa8933cbfa92008df46940b6349f0dea91d32e1028c2911f`,
  54,565 bytes). Identifies `Q1 BT136S-600D,118`, `U1 MOC3023M`,
  `OK1 EL814`, mains-side resistor network, 3-pin AC LINE `J1`,
  2-pin LOAD `J2`, 4-pin "From Core" `J3`. **Does not** establish
  any creepage / clearance value, any component rating, any
  isolation-barrier rating, any L / N / PE assignment on `J1`,
  any fusing / over-current decision, any thermal envelope, any
  EMI behaviour, or any compliance claim. **No edit.**
- [`docs/hardware/artifacts/S360-320-R4.md`](hardware/artifacts/S360-320-R4.md)
  — HW-ASSETS-003 curated artifact index. KiCad schematic source,
  KiCad PCB source, KiCad project metadata, BOM, CPL, Gerbers,
  drill files, STEP, and board images all remain marked
  `not provided in this upload` per
  [§Files NOT provided in this upload](hardware/artifacts/S360-320-R4.md#files-not-provided-in-this-upload).
  No new artifact has been added since HW-ASSETS-003. AC LINE
  `J1` 3-pin function, PCB-level creepage / clearance, and
  component voltage / power ratings remain COMPLIANCE-001-adjacent
  per [§Open questions / verification needed](hardware/artifacts/S360-320-R4.md#open-questions--verification-needed).
  **No edit.**
- [`docs/hardware/s360-320-r4-triac.md`](hardware/s360-320-r4-triac.md)
  — HW-PINMAP-320 audit doc. Status stays `partial — schematic
  evidence available; package reconciliation, timing validation,
  and compliance/certification pending`. A short COMPLIANCE-001
  re-check cross-reference paragraph is appended to
  [§Compliance / safety status](hardware/s360-320-r4-triac.md#compliance--safety-status)
  pointing at the new audit-log entry; no other section is
  rewritten. The
  [§Advanced / manual-warning product posture](hardware/s360-320-r4-triac.md#advanced--manual-warning-product-posture)
  framing is unchanged.
- [`docs/hardware/s360-100-r4-core.md`](hardware/s360-100-r4-core.md)
  §[J15 — TRIAC fan module connector (4-pin)](hardware/s360-100-r4-core.md#j15--triac-fan-module-connector-4-pin)
  — Core-side `J15` 4-pin connector capture. Low-voltage
  interface only; not in COMPLIANCE-001 scope on its own. **No
  edit.**
- [`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml)
  — BLOCKED / UNVERIFIED banner intact. `output: ac_dimmer`
  topology intact. `fan_triac_gate_pin` / `fan_triac_zc_pin`
  substitutions intact. `method: leading`,
  `init_with_half_cycle: true`, default
  `fan_triac_line_frequency: "50"`, `fan_triac_min_power: "10"`
  intact. SX1509-rejection clause intact. The `IMPORTANT:` block
  stating "**The fan load is mains AC. Wiring must be done by a
  qualified electrician and only with a TRIAC dimmer module rated
  for the load.**" intact. Mains-voltage / qualified-electrician
  warnings preserved. **No edit.**
- [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml)
  — blocked-reference product YAML; placeholder
  `fan_triac_gate_pin: GPIO5` / `fan_triac_zc_pin: GPIO6` intact;
  **provably disagrees** with the `S360-100-R4` schematic per
  HW-PINMAP-320. **No edit.**
- [`products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml)
  — blocked WebFlash wrapper; retained as reference only; not in
  any build matrix. **No edit.**
- [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  `S360-320` row — `schematic_status: cataloged_unverified`, no
  `schematic_file`; `S360-400` row —
  `schematic_status: cataloged_unverified`, no `schematic_file`.
  **No edit.** The `HW-CATALOG-320` schematic-status promotion
  stays gated on HW-PINMAP-320-FOLLOWUP + HW-005 + COMPLIANCE-001
  sufficiency.
- [`config/product-catalog.json`](../config/product-catalog.json)
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` entry —
  `status: blocked`, `blocker: HW-005`, `reason` unchanged,
  `webflash_build_matrix: false`, no `artifact_name`, advanced /
  manual-warning candidate posture recorded notes-only by
  PRODUCT-TRIAC-001. **No edit.**
- [`config/webflash-builds.json`](../config/webflash-builds.json)
  — no FanTRIAC-bearing build, no PWR-bearing build; the two
  existing builds (`Ceiling-POE-VentIQ-RoomIQ` stable;
  `Ceiling-POE-VentIQ-RoomIQ-LED` preview) are unchanged. **No
  edit.**
- [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  — `FanTRIAC` reserved in `canonical_modules` subject to the
  fan-driver `max-one-of` rule; `FanTRIAC` carried in Release-One
  and LED preview `blocked_modules`;
  `release_one_required_configs` unchanged. **No edit.**
- [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
  `S360-320` hardware-evidence and productization-axis rows and
  §[`S360-320` Sense360 TRIAC](hardware/board-readiness-matrix.md#s360-320-sense360-triac)
  board-by-board notes — `blocked` (HW-005) +
  `compliance-gated` (COMPLIANCE-001). A short cross-reference
  sentence is appended to the `S360-320` Open work bullet
  recording the 2026-05-18 COMPLIANCE-001 re-check outcome; no
  row state changes. `S360-400` row stays
  `cataloged_unverified / compliance-gated`; no edit.
- [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
  `fan_triac.yaml` row stays `timing/compliance-pending` +
  `needs-package-reconciliation` +
  `blocked-from-standard-exposure`; `power_240v.yaml` row stays
  `schematic-evidence-pending` + `needs-package-reconciliation` +
  `timing/compliance-pending`. A short admonition parallel to the
  existing 2026-05-18 S360-100-BENCH-001 and HW-PINMAP-320-FOLLOWUP
  admonitions is added confirming the re-check does not move
  either row.
- [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)
  §[FanTRIAC mapping resolution](release-one-hardware-audit.md#fantriac-mapping-resolution),
  §[Missing evidence checklist](release-one-hardware-audit.md#missing-evidence-checklist),
  §[Timing constraint: `ac_dimmer` vs SX1509 expander](release-one-hardware-audit.md#timing-constraint-ac_dimmer-vs-sx1509-expander),
  §[Re-verification](release-one-hardware-audit.md#re-verification),
  and §[Required follow-ups](release-one-hardware-audit.md#required-follow-ups)
  — unchanged. A short
  `COMPLIANCE-001 re-check (2026-05-18)` admonition is added at
  the tail of the Findings block as a parallel of the existing
  `S360-100-BENCH-001 re-check (2026-05-18)` and
  `HW-PINMAP-320-FOLLOWUP re-check (2026-05-18)` admonitions; the
  body of the FanTRIAC mapping resolution section is not edited.
- [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md)
  §[Sense360 TRIAC (`S360-320`)](hardware/remaining-board-documentation-audit.md#sense360-triac-s360-320)
  — `blocked` (HW-005), `not-needed-for-release-one`. **No edit.**
- [`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
  FanTRIAC placeholder-GPIOs row — `blocked`. **No edit.**
- [`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md)
  `S360-320 Sense360 TRIAC` snapshot row — `blocked` +
  `compliance-gated`; `S360-400 Sense360 240v PSU` snapshot row —
  `design-pending` + `compliance-gated`. **No edit.**
- This file —
  [§PRODUCT-TRIAC-001 update](#product-triac-001-update-reclassify-fantriac-as-advancedmanual-warning),
  [§PRODUCT-TRIAC-002 update](#product-triac-002-update-deferred--package-triac-001-not-landed),
  [§PACKAGE-TRIAC-001 update](#package-triac-001-update-deferred--hw-005--hw-pinmap-320-followup--compliance-001-not-landed),
  [§TRIAC-QUEUE-001 update](#triac-queue-001-update-remaining-fantriac-chain-normalized-after-package-deferral),
  [§S360-100-BENCH-001 update](#s360-100-bench-001-update-2026-05-18-evidence-pass-investigation),
  [§HW-PINMAP-320-FOLLOWUP update](#hw-pinmap-320-followup-update-2026-05-18-evidence-pass-investigation)
  — the pre-existing FanTRIAC-chain updates this section
  follows. They are unchanged; this section appends after them.
- The [`sense360store/WebFlash`](https://github.com/sense360store/WebFlash)
  repository's runtime advanced / manual-warning UX
  `WF-TRIAC-001` slice — out-of-repo reference only; runtime UX
  gate; **does not** import firmware, **does not** add a
  manifest build, **does not** flip `webflash_build_matrix`,
  **does not** change `release_one_required_configs` /
  REQUIRED_CONFIGS or kits, and **does not** constitute
  compliance evidence, qualified electrical-safety review, or
  formal certification of any kind. Not affected by this re-check.

**Outcome.** A dated audit-log entry recording the 2026-05-18
re-check is appended to
[`docs/compliance/mains-voltage-uk-eu-assessment.md` COMPLIANCE-001 audit log](compliance/mains-voltage-uk-eu-assessment.md#compliance-001-audit-log)
under a newly-added `## COMPLIANCE-001 audit log` heading (the
doc had no audit-log section before this PR). Every row of the
[Board table](compliance/mains-voltage-uk-eu-assessment.md#board-table),
[Product classification — questions](compliance/mains-voltage-uk-eu-assessment.md#product-classification--questions),
[Protection class — decision tree](compliance/mains-voltage-uk-eu-assessment.md#protection-class--decision-tree),
[Standards and regulations — applicability checklist](compliance/mains-voltage-uk-eu-assessment.md#standards-and-regulations--applicability-checklist),
[Electrical-safety topics — checklist](compliance/mains-voltage-uk-eu-assessment.md#electrical-safety-topics--checklist),
[EMC topics — checklist](compliance/mains-voltage-uk-eu-assessment.md#emc-topics--checklist),
[Evidence required before any "preview" promotion](compliance/mains-voltage-uk-eu-assessment.md#evidence-required-before-any-preview-promotion),
[Evidence required before any "stable" / shipping promotion](compliance/mains-voltage-uk-eu-assessment.md#evidence-required-before-any-stable--shipping-promotion),
[Technical-file checklist](compliance/mains-voltage-uk-eu-assessment.md#technical-file-checklist),
[Declaration of Conformity — checklist](compliance/mains-voltage-uk-eu-assessment.md#declaration-of-conformity--checklist),
[Open questions for compliance engineer / test lab](compliance/mains-voltage-uk-eu-assessment.md#open-questions-for-compliance-engineer--test-lab),
[Release blockers](compliance/mains-voltage-uk-eu-assessment.md#release-blockers),
and
[Do-not-change / do-not-claim](compliance/mains-voltage-uk-eu-assessment.md#do-not-change--do-not-claim)
stays at its current value.

**Short cross-reference notes** are added to:

- [`docs/hardware/s360-320-r4-triac.md`](hardware/s360-320-r4-triac.md)
  §[Compliance / safety status](hardware/s360-320-r4-triac.md#compliance--safety-status)
  — a short `COMPLIANCE-001 re-check (2026-05-18)` paragraph is
  appended pointing at the new COMPLIANCE-001 audit-log entry;
  the HW-PINMAP-320 audit-doc status stays `partial — schematic
  evidence available; package reconciliation, timing validation,
  and compliance/certification pending`; HW-005 stays blocked.
- [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
  §[`S360-320` Sense360 TRIAC](hardware/board-readiness-matrix.md#s360-320-sense360-triac)
  — the `S360-320` Open work bullet gains one short sentence
  recording the 2026-05-18 COMPLIANCE-001 re-check outcome; no
  row state changes.
- [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
  §Status labels tail — short admonition parallel to the existing
  2026-05-18 S360-100-BENCH-001 and HW-PINMAP-320-FOLLOWUP
  admonitions confirming the re-check does not move the
  `fan_triac.yaml` row off `timing/compliance-pending` +
  `needs-package-reconciliation` + `blocked-from-standard-exposure`
  or the `power_240v.yaml` row off `schematic-evidence-pending` +
  `needs-package-reconciliation` + `timing/compliance-pending`.
- [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)
  Findings table tail — short `COMPLIANCE-001 re-check (2026-05-18)`
  admonition parallel to the existing
  `S360-100-BENCH-001 re-check (2026-05-18)` and
  `HW-PINMAP-320-FOLLOWUP re-check (2026-05-18)` admonitions
  confirming the re-check does not move the
  [FanTRIAC mapping resolution](release-one-hardware-audit.md#fantriac-mapping-resolution),
  the
  [Missing evidence checklist](release-one-hardware-audit.md#missing-evidence-checklist),
  the
  [Timing constraint](release-one-hardware-audit.md#timing-constraint-ac_dimmer-vs-sx1509-expander)
  analysis, the [Re-verification](release-one-hardware-audit.md#re-verification)
  section, or the [Required follow-ups](release-one-hardware-audit.md#required-follow-ups).
  FanTRIAC stays compliance-gated.

[`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md),
[`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md),
[`docs/hardware/artifacts/S360-320-R4.md`](hardware/artifacts/S360-320-R4.md),
[`docs/hardware/s360-100-r4-core.md`](hardware/s360-100-r4-core.md),
and
[`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md)
already forward-reference COMPLIANCE-001 correctly and are
**not** edited by this update.

**What this update does NOT do.** COMPLIANCE-001 is
documentation-only. The 2026-05-18 re-check explicitly does
**not**:

- promote any row of the COMPLIANCE-001 tracker (`Board table`,
  `Product classification — questions`, `Protection class —
  decision tree`, `Standards and regulations — applicability
  checklist`, `Electrical-safety topics — checklist`, `EMC
  topics — checklist`, `Evidence required before any "preview"
  promotion`, `Evidence required before any "stable" / shipping
  promotion`, `Technical-file checklist`, `Declaration of
  Conformity — checklist`, `Open questions for compliance
  engineer / test lab`) from `Not proven by this repository` /
  `To be confirmed` / `Requires qualified review` /
  `Likely applicable` to anything stronger;
- claim CE / UKCA / FCC / UL / LVD / RED / EMC / RoHS conformity
  for any Sense360 board, module, or product;
- produce a limited advanced / manual-warning sign-off (no
  qualified-electrician / safety-review record with named party,
  review date, observed board serial / batch, covered load types,
  installation context, and "**this is not compliance
  certification**" framing is on file);
- mark COMPLIANCE-001 resolved or cleared for `S360-320` or
  `S360-400`;
- claim that any qualified electrical-safety review,
  isolation-barrier measurement, creepage / clearance
  measurement, fusing / over-current / surge / thermal-protection
  decision, PCB-finger / connector-rating decision, enclosure /
  IP / IK / flame-rating decision, conducted / radiated EMI
  capture, immunity test, harmonics / flicker test, real-load
  test, phase-cut dimming standards analysis, or accredited
  test-lab report has been performed;
- claim that any AC LINE `J1` 3-pin function resolution
  (L / N / PE / doubled-line) is on file;
- resolve the `S360-320` `J1` 3-pin function, the AC LINE
  isolation barrier, the `J2` LOAD connector rating, or any
  on-board component voltage / power rating;
- commit KiCad schematic source, KiCad PCB source, KiCad project
  metadata, BOM, CPL / pick-and-place, Gerbers, drill files,
  STEP, or board images for `S360-320-R4`;
- flip `S360-320` `schematic_status` in
  [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  away from `cataloged_unverified` or set `schematic_file` (the
  `HW-CATALOG-320` schematic-status promotion stays gated on
  HW-PINMAP-320-FOLLOWUP + HW-005 + COMPLIANCE-001 sufficiency);
- flip `S360-400` `schematic_status` away from
  `cataloged_unverified` or set `schematic_file` (`HW-ASSETS-400`
  / `HW-PINMAP-400-FOLLOWUP` / `PACKAGE-POWER-400-001` /
  `COMPLIANCE-001` `S360-400` slice stay outstanding);
- mark
  [`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml)
  `confirmed-ok` (it stays `package-yaml-pending` /
  `needs-package-reconciliation`);
- remove the BLOCKED / UNVERIFIED banner from
  [`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml);
- remove the mains-voltage / qualified-electrician warnings
  from
  [`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml)
  (including the `IMPORTANT:` block stating "**The fan load is
  mains AC. Wiring must be done by a qualified electrician and
  only with a TRIAC dimmer module rated for the load.**");
- edit
  [`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml)
  at all (the `output: ac_dimmer` topology, the
  `fan_triac_gate_pin` / `fan_triac_zc_pin` substitutions, the
  `method: leading`, `init_with_half_cycle: true`, default
  `fan_triac_line_frequency: "50"`, `fan_triac_min_power: "10"`,
  the SX1509-rejection clause, and the header comments are all
  preserved);
- edit
  [`packages/expansions/gpio_expander_sx1509.yaml`](../packages/expansions/gpio_expander_sx1509.yaml)
  or any other package YAML under
  [`packages/`](../packages/);
- edit
  [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml)
  (the placeholder `fan_triac_gate_pin: GPIO5` /
  `fan_triac_zc_pin: GPIO6` substitutions stay; they remain
  provably wrong against the Core schematic);
- edit
  [`products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml)
  or any other product YAML / WebFlash wrapper;
- edit the `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` entry in
  [`config/product-catalog.json`](../config/product-catalog.json)
  (`status` stays `blocked`, `blocker` stays `HW-005`, `reason`
  is unchanged, `webflash_build_matrix` stays `false`, no
  `artifact_name`, advanced / manual-warning candidate posture
  recorded notes-only by PRODUCT-TRIAC-001 is preserved);
- add or change `release_one_required_configs` /
  `REQUIRED_CONFIGS` in
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json);
- add a FanTRIAC build (or any PWR-bearing build) to
  [`config/webflash-builds.json`](../config/webflash-builds.json);
- add a `FanTRIAC` token (or any PWR token) to any current or
  future config string;
- add FanTRIAC to any kit, recommended bundle, or default
  onboarding flow;
- make FanTRIAC recommended;
- generate firmware, create a GitHub Release or tag, or perform
  any WebFlash manifest / import operation;
- change Release-One (stays `Ceiling-POE-VentIQ-RoomIQ`,
  version `1.0.0`, channel `stable`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
  [`v1.0.0`](https://github.com/sense360store/esphome-public/releases/tag/v1.0.0));
- change the LED preview path
  (`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`,
  `channel: preview`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`);
- change the Sense360 LED Release-One exclusion;
- resolve the Core J10 vs RoomIQ J6 pin-order open question;
- advance CORE-ABSTRACT-BUS-001 (alias for
  [`release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups));
- close `HW-005`, `HW-PINMAP-310`, `HW-PINMAP-311`,
  `HW-PINMAP-312`, `HW-PINMAP-320`, `HW-PINMAP-320-FOLLOWUP`,
  `HW-PINMAP-400`, `HW-PINMAP-400-FOLLOWUP`, `HW-PINMAP-410`,
  `HW-PINMAP-410-FOLLOWUP`, `HW-ASSETS-310`, `HW-ASSETS-400`,
  `HW-ASSETS-410`, `HW-CATALOG-320`, `S360-100-BENCH-001`,
  `PACKAGE-GAP-001`, `PRODUCT-GAP-001`, `WEBFLASH-GAP-001`,
  `RELEASE-GAP-001`, `WF-IMPORT-GAP-001`, `PACKAGE-TRIAC-001`,
  `PACKAGE-POWER-400-001`, `PACKAGE-POE-410-001`,
  `PRODUCT-TRIAC-001`, `PRODUCT-TRIAC-002`, in-repo `WF-TRIAC-001`,
  `RELEASE-TRIAC-001`, `WF-IMPORT-TRIAC-001`, or
  `COMPLIANCE-001` itself;
- realise the long-term advanced / manual-warning posture per
  [`s360-320-r4-triac.md` Advanced / manual-warning product posture](hardware/s360-320-r4-triac.md#advanced--manual-warning-product-posture)
  beyond the wording-only PRODUCT-TRIAC-001 catalog notes edit
  that already landed (the JSON `status` stays `blocked`, no
  new lifecycle enum value, no advanced channel, no WebFlash
  wrapper edit, no build-matrix entry, no release artifact, no
  WebFlash import);
- treat the
  [`sense360store/WebFlash`](https://github.com/sense360store/WebFlash)
  runtime advanced / manual-warning UX `WF-TRIAC-001` slice as
  satisfying any HW-005 / HW-PINMAP-320-FOLLOWUP /
  PACKAGE-TRIAC-001 / PRODUCT-TRIAC-002 / in-repo
  `WF-TRIAC-001` / RELEASE-TRIAC-001 / WF-IMPORT-TRIAC-001 /
  COMPLIANCE-001 gate — it does not import firmware, does not
  add a manifest build, does not flip
  `webflash_build_matrix`, does not change REQUIRED_CONFIGS or
  kits, and is **not** compliance evidence, a qualified
  electrical-safety review, an accredited test-lab report, a
  signed Declaration of Conformity, or a limited advanced /
  manual-warning sign-off as defined by
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md);
- edit any file under
  [`config/`](../config/), [`products/`](../products/),
  [`products/webflash/`](../products/webflash/),
  [`packages/`](../packages/), [`scripts/`](../scripts/),
  [`tests/`](../tests/),
  [`.github/workflows/`](../.github/workflows/),
  [`components/`](../components/), [`include/`](../include/),
  [`firmware/`](../firmware/),
  [`manifest.json`](../manifest.json), or
  [`firmware/sources.json`](../firmware/sources.json);
- edit
  [`docs/hardware/artifacts/S360-320-R4.md`](hardware/artifacts/S360-320-R4.md),
  [`docs/hardware/artifacts/S360-100-R4.md`](hardware/artifacts/S360-100-R4.md),
  [`docs/hardware/schematics/S360-320-R4.pdf`](hardware/schematics/S360-320-R4.pdf)
  (the schematic stays byte-identical to the HW-ASSETS-003
  commit; SHA256 unchanged),
  [`docs/hardware/s360-100-r4-core.md`](hardware/s360-100-r4-core.md),
  [`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md),
  [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md),
  or
  [`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md).

**When the next COMPLIANCE-001 audit-log entry should be
recorded.** When committed evidence is added to this repository
that the field-evidence rules in
[`docs/compliance/mains-voltage-uk-eu-assessment.md` COMPLIANCE-001 audit log](compliance/mains-voltage-uk-eu-assessment.md#compliance-001-audit-log)
can cite: a qualified-electrician / electrical-safety reviewer's
signed scope-and-finding record (with named party, review date,
observed board serial / batch, covered load types, installation
context, and explicit "**this is not compliance certification**"
framing) sufficient to record a limited advanced / manual-warning
sign-off; committed KiCad PCB source, Gerbers, BOM, CPL, drill
files, STEP, or board images for `S360-320-R4` (or any future
`S360-320-R5`) that the audit can cite by repo path and that
supports a creepage / clearance / isolation / component-rating /
fusing / thermal / EMI review; committed silkscreen / KiCad
PCB-source / board-image evidence resolving the AC LINE `J1`
3-pin (L / N / PE / doubled-line) function; an accredited
test-lab report covering the applicable LVD / EESR safety
standard(s), the applicable EMC standard(s), and (if the finished
product carries a radio) the applicable RED / UK RER standards
for an `S360-320`-bearing finished product; a signed Declaration
of Conformity for an `S360-320`-bearing finished product;
marking artwork; a production-control plan; a CE / UKCA / FCC /
UL applicability decision recorded with its standards set and
notified-body reference (if applicable); or any equivalent
evidence for `S360-400` (`HW-ASSETS-400` /
`HW-PINMAP-400-FOLLOWUP` / `COMPLIANCE-001` `S360-400` slice).
Until any of those land, the next audit-log entry should report
the same `open / not cleared` outcome with the new inspection
date.

## HW-PINMAP-311-FOLLOWUP update (2026-05-18 evidence-pass investigation)

HW-PINMAP-311-FOLLOWUP is a **docs-only evidence-pass
investigation** against the FanPWM pin-map / connector / package
reconciliation gates owed by the HW-PINMAP-311 audit record at
[`docs/hardware/s360-311-r4-pwm.md`](hardware/s360-311-r4-pwm.md).
The purpose of this update is to re-check, on 2026-05-18, whether
any new committed evidence supports silkscreen reading of the
Core-side `J6` 1-to-13 pin order (paired with the parallel
module-side `J3` 1-to-13 silkscreen reading), physical 13-pin
Core ↔ module harness inspection, bench / scope / waveform
capture of the per-fan PWM drive (`TachPMW*`) / per-fan tach
feedback (`Pul_Cou*`) / shared open-drain (`TachIO`) paths,
pulses-per-revolution validation of the `multiply: 0.5` factor
in [`packages/expansions/fan_pwm.yaml`](../packages/expansions/fan_pwm.yaml),
UART-on-`J3`-pins-11/12 routing resolution, PWM polarity (
active-high vs active-low for the per-fan low-side N-FET gate
path) and tach pull-up identification, the single-channel vs
four-channel canonical-abstraction decision for the FanPWM
token, KiCad schematic source / KiCad PCB source / KiCad project
metadata / BOM / CPL / Gerber / drill / STEP / board-image
evidence for `S360-311-R4`, or progress on the systemic Core
abstract-bus rebind (`CORE-ABSTRACT-BUS-001`, alias for
[`release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups))
— and to record the result of that re-check as a dated audit-log
entry in
[`docs/hardware/s360-311-r4-pwm.md` HW-PINMAP-311-FOLLOWUP audit log](hardware/s360-311-r4-pwm.md#hw-pinmap-311-followup-audit-log).
**The status remains `partial — schematic evidence available;
package reconciliation pending`.** No reconciliation row has
been promoted. No silkscreen / harness / bench / waveform
evidence is on file. No single-vs-four-channel canonical
choice is recorded. No UART-on-J3-pins-11/12 alternative is
chosen. The SX1509-channel vs direct-ESP32-GPIO routing
disagreement is not resolved (resolution belongs to
`CORE-ABSTRACT-BUS-001`, not HW-PINMAP-311-FOLLOWUP). The
`"NINE 4pin FANs"` section-title documentation question is
not resolved. `PACKAGE-PWM-001` (alias: `PACKAGE-GAP-001`
FanPWM slice) stays blocked. The downstream FanPWM chain
(`PRODUCT-PWM-001`, `WEBFLASH-PWM-001`, `RELEASE-PWM-001`,
`WF-IMPORT-PWM-001`) stays blocked. Release-One is unchanged.
The LED preview path is unchanged. FanTRIAC stays
`status: blocked`. The Sense360 LED Release-One exclusion is
unchanged.

**Why this is the next actionable evidence item.** After
[§S360-100-BENCH-001 update](#s360-100-bench-001-update-2026-05-18-evidence-pass-investigation),
[§HW-PINMAP-320-FOLLOWUP update](#hw-pinmap-320-followup-update-2026-05-18-evidence-pass-investigation),
and
[§COMPLIANCE-001 update](#compliance-001-update-2026-05-18-mains-voltage-advancedmanual-warning-sign-off-evidence-pass-investigation)
re-confirmed the broad Core-board evidence gate, the
FanTRIAC-board pin-map / direct-GPIO / timing / mains-compliance
gates, and the COMPLIANCE-001 mains-voltage advanced /
manual-warning sign-off gates all stay open, and after
[§PACKAGE-TRIAC-001 update](#package-triac-001-update-deferred--hw-005--hw-pinmap-320-followup--compliance-001-not-landed)
deferred PACKAGE-TRIAC-001 and
[§TRIAC-QUEUE-001 update](#triac-queue-001-update-remaining-fantriac-chain-normalized-after-package-deferral)
normalised the remaining FanTRIAC chain as blocked until the
upstream evidence / compliance gates clear, the next actionable
docs-only follow-up shifts onto the FanPWM (`S360-311`) track
because HW-ASSETS-003 already committed the module-side
schematic PDF + curated artifact index and HW-PINMAP-311
already landed the audit doc, leaving the pin-map / package
reconciliation as the named next step. The package-readiness
matrix (`fan_pwm.yaml` `needs-package-reconciliation` +
`bench-evidence-pending`), the board-readiness matrix
(`S360-311` `partially-documented` + `package-yaml-pending`),
the firmware-package-mapping audit (`fan_pwm.yaml` HW-009 row),
the product-readiness matrix (`Ceiling-POE-VentIQ-FanPWM-RoomIQ`
`missing-product-yaml`), and the webflash-exposure-readiness
matrix (FanPWM `not-webflash-ready`) all forward-reference
HW-PINMAP-311-FOLLOWUP. The Core abstract-bus disagreement that
binds `fan_pwm_pin` / `fan_tach_pin` to direct ESP32 expansion
GPIOs (`expansion_gpio1` / `expansion_gpio2` → `GPIO5` / `GPIO6`
on the ceiling Core; `GPIO4` / `GPIO5` on the generic Core)
remains owed to `CORE-ABSTRACT-BUS-001`, not to this update.

**Investigation scope.** The 2026-05-18 re-check inspected the
following committed files and re-confirmed each against the
HW-PINMAP-311 reconciliation rules in
[`docs/hardware/s360-311-r4-pwm.md`](hardware/s360-311-r4-pwm.md)
and the HW-ASSETS-003 artifact-index rules in
[`docs/hardware/artifacts/S360-311-R4.md`](hardware/artifacts/S360-311-R4.md):

- [`docs/hardware/schematics/S360-311-R4.pdf`](../docs/hardware/schematics/S360-311-R4.pdf)
  — HW-ASSETS-003 module-side schematic, byte-identical to the
  upload (SHA256
  `c910b3364be1d58fc44d12b5a189dade47efddf6cae158a86577ec7501e48006`,
  91,543 bytes). Schematic-tier evidence; not changed by this
  re-check. Confirms the visible content: MT3608 `+5V` → `+12V`
  boost (`U1`, `L1 22 µH`, `D1 SS34`, `R3 38 kΩ` / `R5 2 kΩ`
  feedback divider, `C1` / `C2 22 µF / 10 V`, indicator `R4 330 Ω`
  + blue LED `D2`); four 4-pin fan output connectors (`J1`,
  `J2`, `J4`, `J5`) under the `"NINE 4pin FANs"` section title;
  per-fan low-side N-channel MOSFET (`Q1..Q4`) with 1 kΩ gate
  resistor (`R1`, `R2`, `R6`, `R7`) on the `TachPMW*` gate path;
  13-pin module-side `J3` "From Core" with pinout `+5V` /
  `TachIO` / `TachPMW1` / `Pul_Cou1` / `TachPMW2` / `Pul_Cou2` /
  `TachPMW3` / `Pul_Cou3` / `TachPMW4` / `Pul_Cou4` / `UART_RX` /
  `UART_TX` / `GND`; 4-pin Nextion display connector `J6`
  module-side (`+5V` / `ESP32_TXD` / `ESP32_RXD` / `GND`);
  mounting holes `H1..H4`. **No edit.**
- [`docs/hardware/artifacts/S360-311-R4.md`](hardware/artifacts/S360-311-R4.md)
  — HW-ASSETS-003 curated artifact index. Records the uploaded
  inventory (single 91,543-byte PDF; canonical name
  `S360-311-R4.pdf`), the visible schematic content, the
  retained-but-not-committed list (KiCad schematic source, KiCad
  PCB source, KiCad project metadata, BOM, CPL, Gerbers, drill
  files, STEP, board images all marked `not provided in this
  upload`), and the artifact-side Open Questions (HW-PINMAP-311
  pin-map reconciliation; `"NINE 4pin FANs"` section title;
  UART-on-J3-pins-11/12 routing; long-term storage decision for
  retained-but-not-committed artifacts; standalone hardware
  reference doc not yet committed). No new artifact has been
  added since HW-ASSETS-003. **No edit.**
- [`docs/hardware/s360-311-r4-pwm.md`](hardware/s360-311-r4-pwm.md)
  — HW-PINMAP-311 audit doc. Status row stays `partial —
  schematic evidence available; package reconciliation pending`.
  Every row of the
  [Schematic summary](hardware/s360-311-r4-pwm.md#schematic-summary),
  [Connector / pin-map findings](hardware/s360-311-r4-pwm.md#connector--pin-map-findings),
  [UART pins on `J3` pins 11–12](hardware/s360-311-r4-pwm.md#uart-pins-on-j3-pins-1112),
  [Per-fan-output drive topology (module side)](hardware/s360-311-r4-pwm.md#per-fan-output-drive-topology-module-side),
  [Open documentation questions](hardware/s360-311-r4-pwm.md#open-documentation-questions),
  [Existing package abstraction](hardware/s360-311-r4-pwm.md#existing-package-abstraction),
  [Parent Core packages that resolve `fan_pwm_pin` / `fan_tach_pin`](hardware/s360-311-r4-pwm.md#parent-core-packages-that-resolve-fan_pwm_pin--fan_tach_pin),
  and
  [Reconciliation findings](hardware/s360-311-r4-pwm.md#reconciliation-findings)
  tables is unchanged. Every item in the
  [Known unresolved issues](hardware/s360-311-r4-pwm.md#known-unresolved-issues)
  list stays open. A new
  [HW-PINMAP-311-FOLLOWUP audit log](hardware/s360-311-r4-pwm.md#hw-pinmap-311-followup-audit-log)
  section is appended by this update; no other section of the
  doc is rewritten.
- [`docs/hardware/s360-100-r4-core.md`](hardware/s360-100-r4-core.md)
  §[J6 — 12 V PWM fan connector (13-pin)](hardware/s360-100-r4-core.md#j6--12-v-pwm-fan-connector-13-pin),
  §[Fan / driver outputs](hardware/s360-100-r4-core.md#fan--driver-outputs),
  §[Pin assignments](hardware/s360-100-r4-core.md#pin-assignments)
  (`IO16 = TachIO`), §[Open Questions #9](hardware/s360-100-r4-core.md#open-questions--verification-needed)
  (`J6` 1-to-13 silkscreen pin-order **verify**), and
  §[S360-100-BENCH-001 status](hardware/s360-100-r4-core.md#s360-100-bench-001-status)
  — Core-side `J6` 13-pin capture (`+5V` / `GND` / `TachIO` /
  `TachPMW1..4` / `Pul_Cou1..4`, 11 nets); UART pins not
  recorded on Core-side `J6`; `TachPMW*` / `Pul_Cou*` driven by
  the SX1509 (`U3`) I/O bank; `TachIO` is the ESP32 `IO16` direct
  passthrough; the 1-to-13 pin order stays **verify** against
  silkscreen; S360-100-BENCH-001 stays `pending —
  bench/manufacturing evidence required`. **No edit.**
- [`packages/expansions/fan_pwm.yaml`](../packages/expansions/fan_pwm.yaml)
  — single-channel FanPWM package. `output.platform: ledc` /
  `pin: ${fan_pwm_pin}` (line 45), `fan_pwm_frequency: "25000"`
  (line 32), `sensor.platform: pulse_counter` /
  `pin.number: ${fan_tach_pin}` (line 67), `mode: input: true,
  pullup: true` (lines 68–70), `multiply: 0.5` "Standard fans
  output 2 pulses per revolution" (lines 76–80), parent-Core
  substitution comment block (lines 22–29), fan-stall logic,
  quiet-mode logic — all intact. **No edit.**
- [`packages/expansions/sense360_fan_pwm.yaml`](../packages/expansions/sense360_fan_pwm.yaml)
  — legacy four-channel FanPWM package. `fan1_pwm_pin: GPIO7` /
  `fan2_pwm_pin: GPIO11` / `fan3_pwm_pin: GPIO13` /
  `fan4_pwm_pin: GPIO15` (lines 40–43); `fan1_tach_pin: GPIO8` /
  `fan2_tach_pin: GPIO12` / `fan3_tach_pin: GPIO14` /
  `fan4_tach_pin: GPIO16` (lines 46–49); `tach_io_pin: GPIO6`
  (line 52); `nextion_tx_pin: GPIO43` / `nextion_rx_pin: GPIO44`
  (lines 55–56). Consumed only by
  [`products/sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml)
  (`legacy-compatible`; not WebFlash-shippable). **No edit.**
- [`packages/expansions/gpio_expander_sx1509.yaml`](../packages/expansions/gpio_expander_sx1509.yaml)
  — SX1509 channel map. Channels 0–3 reserved for fan PWM
  outputs; channels 4–7 reserved for tachometer inputs; channels
  8–11 aux PWM; channels 12–15 generic inputs. Schematic-backed
  source for the per-fan `TachPMW*` / `Pul_Cou*` route on the
  Core sheet. **No edit.**
- [`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml)
  — Ceiling Core abstract package. `expansion_gpio1: GPIO5` /
  `expansion_gpio2: GPIO6` (lines 65–66); `fan_pwm_pin:
  ${expansion_gpio1}` / `fan_tach_pin: ${expansion_gpio2}` (lines
  72–73). Disagrees with the Core schematic — `IO5 = SEN0609_TX`
  (RoomIQ radar UART), `IO6 = out(gpio6)` — and disagrees with
  the per-fan SX1509-routed `TachPMW*` / `Pul_Cou*` schematic
  paths. Resolution belongs to `CORE-ABSTRACT-BUS-001` (alias
  for
  [`release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups)),
  **not** to HW-PINMAP-311-FOLLOWUP. **No edit.**
- [`packages/hardware/sense360_core.yaml`](../packages/hardware/sense360_core.yaml)
  — generic Core abstract package. `expansion_gpio1: GPIO4` /
  `expansion_gpio2: GPIO5` (lines 57–58). Same systemic
  disagreement. **No edit.**
- [`products/sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml)
  — legacy pre-WebFlash standalone fan-board product YAML.
  Consumes the four-channel
  [`packages/expansions/sense360_fan_pwm.yaml`](../packages/expansions/sense360_fan_pwm.yaml),
  not the single-channel
  [`packages/expansions/fan_pwm.yaml`](../packages/expansions/fan_pwm.yaml).
  Classified `legacy-compatible`; not WebFlash-shippable; not
  the FanPWM productization candidate. **No edit.**
- [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  `S360-311` row (lines 72–81) — `group: Inline`, `type:
  Driver`, `friendly_name: Sense360 PWM`, `sku: S360-311`,
  `rev: R4`, `old_name: 12vFan_PWM_PulseCounter`, `description:
  12V PWM fan driver, up to 4 fans with tach feedback.`,
  `schematic_status: cataloged_unverified`, no `schematic_file`.
  The `S360-311 schematic_status` promotion stays gated on
  HW-PINMAP-311-FOLLOWUP. **No edit.**
- [`config/product-catalog.json`](../config/product-catalog.json)
  — no FanPWM-bearing entry. The two shipping entries are
  `Ceiling-POE-VentIQ-RoomIQ` (`status: production`, `channel:
  stable`, artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`,
  tag `v1.0.0`) and `Ceiling-POE-VentIQ-RoomIQ-LED` (`status:
  preview`, `channel: preview`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`).
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`,
  `blocker: HW-005`, `webflash_build_matrix: false`, no
  `artifact_name`. **No edit.**
- [`config/webflash-builds.json`](../config/webflash-builds.json)
  — no FanPWM-bearing build; only `Ceiling-POE-VentIQ-RoomIQ`
  stable and `Ceiling-POE-VentIQ-RoomIQ-LED` preview. **No
  edit.**
- [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  — `FanPWM` reserved in `canonical_modules` (line 12), subject
  to the fan-driver `max-one-of` rule enforced by
  `FAN_DRIVER_TOKENS` in
  [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py).
  Not consumed by any current build. **No edit.**
- [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
  `S360-311` hardware-evidence and productization-axis rows and
  §[`S360-311` Sense360 PWM](hardware/board-readiness-matrix.md#s360-311-sense360-pwm)
  board-by-board notes — `partially-documented`,
  `not-needed-for-release-one`, `package-yaml-pending`. A short
  Open work bullet recording the 2026-05-18 re-check outcome is
  appended to the §`S360-311` Sense360 PWM subsection;
  no row state changes.
- [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
  `fan_pwm.yaml` row stays `needs-package-reconciliation` +
  `bench-evidence-pending`; §[`fan_pwm.yaml` / S360-311](hardware/package-readiness-matrix.md#fan_pwmyaml--s360-311)
  detail unchanged. A short admonition parallel to the existing
  2026-05-18 S360-100-BENCH-001 / HW-PINMAP-320-FOLLOWUP /
  COMPLIANCE-001 admonitions is added confirming the re-check
  does not move this row.
- [`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
  HW-009 row for `fan_pwm.yaml` — `package-yaml-pending` /
  `needs-package-reconciliation`. **No edit.**
- [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md)
  §[Sense360 PWM (`S360-311`)](hardware/remaining-board-documentation-audit.md#sense360-pwm-s360-311)
  — `partially-documented`, `not-needed-for-release-one`. **No
  edit.**
- [`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md)
  `S360-311` snapshot row — `partially-documented` +
  `design-pending`. **No edit.**
- [`docs/product-readiness-matrix.md`](product-readiness-matrix.md)
  `Ceiling-POE-VentIQ-FanPWM-RoomIQ` row — `missing-product-yaml`
  / no build / no kit / not Release-One. **No edit.**
- [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md)
  §[PWM / S360-311 WebFlash posture](webflash-exposure-readiness-matrix.md#pwm--s360-311-webflash-posture)
  — `not-webflash-ready`, `preview-candidate`. **No edit.**
- [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
  — no FanPWM artifact; the two shipping artifacts
  (`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` and
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`)
  are unchanged. **No edit.**
- [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)
  §[Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups)
  — `CORE-ABSTRACT-BUS-001` (Core abstract-bus rebind) not
  advanced; the systemic mismatch between the Core abstract
  `${expansion_gpio1}` / `${expansion_gpio2}` resolutions and
  the Core schematic stays open. **No edit.**
- [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
  — COMPLIANCE-001 tracker (applies to `S360-320` /
  `S360-400`; FanPWM is SELV and not in COMPLIANCE-001 scope).
  Recorded here only as a sibling evidence record so the
  re-check is fully transparent about adjacent compliance status.
  **No edit.**
- This file —
  [§S360-100-BENCH-001 update](#s360-100-bench-001-update-2026-05-18-evidence-pass-investigation),
  [§HW-PINMAP-320-FOLLOWUP update](#hw-pinmap-320-followup-update-2026-05-18-evidence-pass-investigation),
  [§COMPLIANCE-001 update](#compliance-001-update-2026-05-18-mains-voltage-advancedmanual-warning-sign-off-evidence-pass-investigation),
  [§PACKAGE-TRIAC-001 update](#package-triac-001-update-deferred--hw-005--hw-pinmap-320-followup--compliance-001-not-landed),
  [§TRIAC-QUEUE-001 update](#triac-queue-001-update-remaining-fantriac-chain-normalized-after-package-deferral),
  [§PRODUCT-TRIAC-001 update](#product-triac-001-update-reclassify-fantriac-as-advancedmanual-warning),
  [§PRODUCT-TRIAC-002 update](#product-triac-002-update-deferred--package-triac-001-not-landed)
  — the pre-existing 2026-05-18 evidence-pass / FanTRIAC-chain
  updates this section follows. They are unchanged; this section
  appends after them.

**Outcome.** A dated audit-log entry recording the 2026-05-18
re-check is appended to
[`docs/hardware/s360-311-r4-pwm.md` HW-PINMAP-311-FOLLOWUP audit log](hardware/s360-311-r4-pwm.md#hw-pinmap-311-followup-audit-log)
under a newly-added `## HW-PINMAP-311-FOLLOWUP audit log`
heading (the doc had no audit-log section before this PR). Every
row of the
[Schematic summary](hardware/s360-311-r4-pwm.md#schematic-summary),
[Connector / pin-map findings](hardware/s360-311-r4-pwm.md#connector--pin-map-findings),
[UART pins on `J3` pins 11–12](hardware/s360-311-r4-pwm.md#uart-pins-on-j3-pins-1112),
[Per-fan-output drive topology (module side)](hardware/s360-311-r4-pwm.md#per-fan-output-drive-topology-module-side),
[Open documentation questions](hardware/s360-311-r4-pwm.md#open-documentation-questions),
[Existing package abstraction](hardware/s360-311-r4-pwm.md#existing-package-abstraction),
[Parent Core packages that resolve `fan_pwm_pin` / `fan_tach_pin`](hardware/s360-311-r4-pwm.md#parent-core-packages-that-resolve-fan_pwm_pin--fan_tach_pin),
and
[Reconciliation findings](hardware/s360-311-r4-pwm.md#reconciliation-findings)
tables stays at its current value. Every item in the
[Known unresolved issues](hardware/s360-311-r4-pwm.md#known-unresolved-issues)
list stays open.

**Short cross-reference notes** are added to:

- [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
  §Status labels tail — short admonition that the 2026-05-18
  HW-PINMAP-311-FOLLOWUP re-check does **not** move the
  `fan_pwm.yaml` row off `needs-package-reconciliation` +
  `bench-evidence-pending`. The legacy
  [`sense360_fan_pwm.yaml`](../packages/expansions/sense360_fan_pwm.yaml)
  stays `legacy-compatible`-only. The `PACKAGE-PWM-001`
  follow-up PR chain (`HW-PINMAP-311-FOLLOWUP` → `S360-311
  schematic_status` promotion (separate JSON PR) →
  `PACKAGE-PWM-001` paired with `CORE-ABSTRACT-BUS-001`) is
  unchanged.
- [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
  §[`S360-311` Sense360 PWM](hardware/board-readiness-matrix.md#s360-311-sense360-pwm)
  — short Open work bullet recording the re-check outcome: no
  new committed silkscreen / bench / harness / waveform /
  KiCad-source / KiCad-PCB / BOM / CPL / Gerber / drill / STEP /
  board-image evidence; Core J6 1-to-13 silkscreen pin order and
  module J3 1-to-13 silkscreen pin order still open;
  SX1509-channel vs direct-ESP32-GPIO routing, UART-on-J3-pins-11/12,
  single-vs-four-channel cardinality, and `"NINE 4pin FANs"`
  title still open; `fan_pwm.yaml` stays
  `package-yaml-pending` / `needs-package-reconciliation`;
  legacy `sense360_fan_pwm.yaml` stays `legacy-compatible`;
  `S360-311` JSON `schematic_status` stays
  `cataloged_unverified`; no row state changes.

[`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md),
[`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md),
[`docs/hardware/artifacts/S360-311-R4.md`](hardware/artifacts/S360-311-R4.md),
[`docs/hardware/s360-100-r4-core.md`](hardware/s360-100-r4-core.md),
[`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md),
[`docs/product-readiness-matrix.md`](product-readiness-matrix.md),
[`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md),
[`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md),
[`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md),
and
[`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
already forward-reference HW-PINMAP-311 / HW-PINMAP-311-FOLLOWUP /
`CORE-ABSTRACT-BUS-001` / `S360-100-BENCH-001` / `COMPLIANCE-001`
correctly and are **not** edited by this update.

**What this update does NOT do.** HW-PINMAP-311-FOLLOWUP is
documentation-only. The 2026-05-18 re-check explicitly does
**not**:

- promote the HW-PINMAP-311 status away from `partial —
  schematic evidence available; package reconciliation pending`;
- promote any row of the
  [Schematic summary](hardware/s360-311-r4-pwm.md#schematic-summary),
  [Connector / pin-map findings](hardware/s360-311-r4-pwm.md#connector--pin-map-findings),
  [UART pins on `J3` pins 11–12](hardware/s360-311-r4-pwm.md#uart-pins-on-j3-pins-1112),
  [Per-fan-output drive topology (module side)](hardware/s360-311-r4-pwm.md#per-fan-output-drive-topology-module-side),
  [Existing package abstraction](hardware/s360-311-r4-pwm.md#existing-package-abstraction),
  [Parent Core packages that resolve `fan_pwm_pin` / `fan_tach_pin`](hardware/s360-311-r4-pwm.md#parent-core-packages-that-resolve-fan_pwm_pin--fan_tach_pin),
  or
  [Reconciliation findings](hardware/s360-311-r4-pwm.md#reconciliation-findings)
  tables from `needs-package-reconciliation`, `verify`,
  `Schematic-only`, `Core-side captured only`, or any other
  current value to anything stronger;
- close any item in the
  [Known unresolved issues](hardware/s360-311-r4-pwm.md#known-unresolved-issues)
  list (systemic Core abstract-bus mismatch, no bench
  verification, no silkscreen verification, no harness
  verification, no KiCad source / KiCad PCB / project metadata,
  no BOM, no CPL / pick-and-place, no board photography, no tach
  waveform verification, no operator validation, no standalone
  schematic-backed reference doc);
- close any of the
  [Open documentation questions](hardware/s360-311-r4-pwm.md#open-documentation-questions)
  (`"NINE 4pin FANs"` section title; Date / Title / Rev fields
  blank on the schematic);
- close the
  [`s360-100-r4-core.md` Open Questions #9](hardware/s360-100-r4-core.md#open-questions--verification-needed)
  `J6` 1-to-13 silkscreen pin-order `verify` flag (owned by
  `S360-100-BENCH-001`);
- choose between the two UART-on-`J3`-pins-11/12 alternatives
  (extend the Core-side `J6` capture to record `UART_RX` /
  `UART_TX` on pins 11 / 12, or document a separate harness);
- choose the single-channel vs four-channel canonical
  abstraction for the FanPWM token (`PACKAGE-PWM-001` /
  `PACKAGE-GAP-001` FanPWM slice's job);
- choose the SX1509-channel vs direct-ESP32-GPIO routing for the
  per-fan PWM / tach paths (`CORE-ABSTRACT-BUS-001` /
  `PACKAGE-PWM-001`'s job — not HW-PINMAP-311-FOLLOWUP);
- record any PWM polarity / tach pull-up source /
  pulses-per-revolution validation finding;
- edit
  [`packages/expansions/fan_pwm.yaml`](../packages/expansions/fan_pwm.yaml)
  (the single-channel `${fan_pwm_pin}` / `${fan_tach_pin}`
  bindings, `fan_pwm_frequency: "25000"`, `multiply: 0.5` factor,
  stall-detection and quiet-mode logic, and the parent-Core
  substitution comment block are preserved);
- edit
  [`packages/expansions/sense360_fan_pwm.yaml`](../packages/expansions/sense360_fan_pwm.yaml)
  (the four-channel `fan1..4_pwm_pin` / `fan1..4_tach_pin` /
  `tach_io_pin` / `nextion_tx_pin` / `nextion_rx_pin` bindings
  are preserved);
- edit
  [`packages/expansions/gpio_expander_sx1509.yaml`](../packages/expansions/gpio_expander_sx1509.yaml)
  (the SX1509 channel map — channels 0–3 fan PWM, 4–7 tach,
  8–11 aux PWM, 12–15 inputs — is preserved);
- edit
  [`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml)
  or
  [`packages/hardware/sense360_core.yaml`](../packages/hardware/sense360_core.yaml)
  (the `${expansion_gpio1}` / `${expansion_gpio2}` ↔
  `${fan_pwm_pin}` / `${fan_tach_pin}` bindings are preserved;
  Core abstract-bus rebind is owned by `CORE-ABSTRACT-BUS-001`);
- edit
  [`products/sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml)
  (the legacy pre-WebFlash standalone fan-board product YAML
  stays `legacy-compatible`);
- flip `S360-311` `schematic_status` in
  [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  from `cataloged_unverified` (the schematic-status promotion
  remains gated on HW-PINMAP-311-FOLLOWUP);
- set `schematic_file` for `S360-311` in
  [`config/hardware-catalog.json`](../config/hardware-catalog.json);
- add a FanPWM-bearing product entry to
  [`config/product-catalog.json`](../config/product-catalog.json),
  a FanPWM-bearing build entry to
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  or modify
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  (`FanPWM` stays reserved in `canonical_modules` subject to the
  fan-driver `max-one-of` rule; no current build consumes it);
- add a product YAML under
  [`products/`](../products/), a WebFlash wrapper under
  [`products/webflash/`](../products/webflash/), or a
  build-matrix entry for any FanPWM-bearing configuration;
- regenerate firmware, create a GitHub Release or tag, change
  any WebFlash manifest / import for any FanPWM-bearing
  configuration;
- advance `PACKAGE-PWM-001` (alias: `PACKAGE-GAP-001` FanPWM
  slice), `PRODUCT-PWM-001`, `WEBFLASH-PWM-001`,
  `RELEASE-PWM-001` (alias: `RELEASE-GAP-001` FanPWM slice), or
  `WF-IMPORT-PWM-001` (alias: `WF-IMPORT-GAP-001` FanPWM slice);
- advance `CORE-ABSTRACT-BUS-001` (alias for
  [`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups));
- close `S360-100-BENCH-001` (
  [`docs/hardware/s360-100-r4-core.md` S360-100-BENCH-001 status](hardware/s360-100-r4-core.md#s360-100-bench-001-status)
  stays `pending — bench/manufacturing evidence required`);
- close `HW-PINMAP-320-FOLLOWUP` (
  [`docs/hardware/s360-320-r4-triac.md` HW-PINMAP-320-FOLLOWUP audit log](hardware/s360-320-r4-triac.md#hw-pinmap-320-followup-audit-log)
  stays `partial`);
- close `COMPLIANCE-001` (
  [`docs/compliance/mains-voltage-uk-eu-assessment.md` COMPLIANCE-001 audit log](compliance/mains-voltage-uk-eu-assessment.md#compliance-001-audit-log)
  stays `open / not cleared`);
- change Release-One. Release-One stays `Ceiling-POE-VentIQ-RoomIQ`,
  version `1.0.0`, channel `stable`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
  [`v1.0.0`](https://github.com/sense360store/esphome-public/releases/tag/v1.0.0);
- change the LED preview path
  (`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`,
  `channel: preview`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`);
- change the Sense360 LED Release-One exclusion;
- unblock FanTRIAC
  (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`,
  `blocker: HW-005`, `webflash_build_matrix: false`);
- change `REQUIRED_CONFIGS` or any kit / default list;
- claim that any bench evidence (operator observation,
  silkscreen photo, scope trace, continuity measurement, serial
  log, harness inspection) exists for `S360-311-R4`;
- claim that any manufacturing-artifact review (KiCad source,
  KiCad PCB, KiCad project metadata, BOM, CPL, Gerber, drill,
  STEP, board images) has been performed for `S360-311-R4`;
- edit any file under
  [`config/`](../config/), [`products/`](../products/),
  [`products/webflash/`](../products/webflash/),
  [`packages/`](../packages/), [`scripts/`](../scripts/),
  [`tests/`](../tests/),
  [`.github/workflows/`](../.github/workflows/),
  [`components/`](../components/), [`include/`](../include/),
  [`firmware/`](../firmware/),
  [`manifest.json`](../manifest.json), or
  [`firmware/sources.json`](../firmware/sources.json);
- edit
  [`docs/hardware/artifacts/S360-311-R4.md`](hardware/artifacts/S360-311-R4.md),
  [`docs/hardware/schematics/S360-311-R4.pdf`](hardware/schematics/S360-311-R4.pdf)
  (the schematic stays byte-identical to the HW-ASSETS-003
  commit; SHA256
  `c910b3364be1d58fc44d12b5a189dade47efddf6cae158a86577ec7501e48006`
  unchanged),
  [`docs/hardware/s360-100-r4-core.md`](hardware/s360-100-r4-core.md),
  [`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md),
  [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md),
  [`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md),
  [`docs/product-readiness-matrix.md`](product-readiness-matrix.md),
  [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md),
  [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md),
  [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md),
  or
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md).

**When the next HW-PINMAP-311-FOLLOWUP audit-log entry should
be recorded.** When committed evidence is added to this
repository that the field-evidence rules in
[`docs/hardware/s360-311-r4-pwm.md` HW-PINMAP-311-FOLLOWUP audit log](hardware/s360-311-r4-pwm.md#hw-pinmap-311-followup-audit-log)
can cite: operator-attributed silkscreen captures of the
Core-side `J6` 1-to-13 pin order and the parallel module-side
`J3` 1-to-13 pin order; physical 13-pin Core ↔ module harness
inspection with conductor-by-conductor pin mapping recorded;
oscilloscope captures of the per-fan PWM drive (`TachPMW*` on
`J1` / `J2` / `J4` / `J5`), the per-fan tach feedback
(`Pul_Cou*`), or the shared open-drain `TachIO` net against a
populated `S360-100-R4` + `S360-311-R4` pair, with operator /
reviewer identity and review date recorded; pulses-per-revolution
validation of the `multiply: 0.5` factor in
[`packages/expansions/fan_pwm.yaml`](../packages/expansions/fan_pwm.yaml)
against a real fan; resolution of the UART-on-`J3`-pins-11/12
routing alternative; PWM polarity (active-high vs active-low
for the per-fan low-side N-FET gate path) and tach pull-up
source identification (discrete external, SX1509 on-die
channel pull-up, or fan-side); a standalone schematic-backed
reference doc (e.g. `docs/hardware/s360-311-r4-fanpwm.md`) in
the per-board reference pattern; a single-channel vs
four-channel canonical-abstraction decision against the
FanPWM token; a `"NINE 4pin FANs"` section-title
documentation resolution; KiCad schematic source
(`S360-311-R4.kicad_sch`) / KiCad PCB source
(`S360-311-R4.kicad_pcb`) / KiCad project metadata
(`*.kicad_pro` / `*.kicad_prl` / `fp-lib-table` /
`sym-lib-table`) / BOM / CPL / Gerbers / drill / STEP /
board images for `S360-311-R4` that the audit can cite by
repo path; or progress on the systemic Core abstract-bus
rebind (`CORE-ABSTRACT-BUS-001`, alias for
[`release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups)).
Until any of those land, the next audit-log entry should
report the same `partial — schematic evidence available;
package reconciliation pending` outcome with the new
inspection date.

## HW-PINMAP-312-FOLLOWUP update (2026-05-18 evidence-pass investigation)

HW-PINMAP-312-FOLLOWUP is a **docs-only evidence-pass
investigation** against the FanDAC pin-map / connector / I²C-
address / UART-arbitration / voltage-rail / Cloudlift-output /
voltage-mode-jumper / package reconciliation gates owed by the
HW-PINMAP-312 audit record at
[`docs/hardware/s360-312-r4-dac.md`](hardware/s360-312-r4-dac.md).
The purpose of this update is to re-check, on 2026-05-18, whether
any new committed evidence supports silkscreen reading of the
Core-side `J7` 1-to-6 pin order and the parallel module-side
`J1` 1-to-6 pin order (particularly the pin-1 rail value `+5V`
vs `+3.3V`), physical 6-pin Core ↔ module harness inspection
(conductor-by-conductor pin mapping), silkscreen reading of the
module-side `J2` / `J3` Cloudlift S12 output connector pin-1
location and the harness mapping to the fan, bench / scope /
I²C / waveform / Cloudlift-functional capture of the GP8403 DAC
outputs at `J2` / `J3` and the shared I²C bus exchange to
`IC1` / `IC2`, DIP-switch I²C address-selection measurement on
`SW1` / `SW2` to determine which switch positions produce which
I²C address pair on `IC1` / `IC2`, `fan_dac_voltage_mode` 5 V vs
10 V hardware-select identification (jumper / solder-bridge /
DIP position), UART0-vs-Nextion arbitration evidence (whether a
FanDAC build can co-exist with USB boot-log output on UART0,
given Module `J1` pins 4 / 5 carry `UART_RX` / `UART_TX` routed
on-board to Module `J7` Nextion connector while Core ties the
same nets to ESP32 `TXD0` (pin 37) / `RXD0` (pin 36) — UART0,
also the boot-log path on USB per
[`s360-100-r4-core.md` §UART buses](hardware/s360-100-r4-core.md#uart-buses)
line 349), resolution of the stale header-comment block in
[`packages/expansions/fan_gp8403.yaml`](../packages/expansions/fan_gp8403.yaml)
lines 13–18 (`Pin 4 (SDA) → GPIO39`, `Pin 5 (SCL) → GPIO40`,
`Pin 2 (3.3V) → Power`, `Pin 1 (GND) → Ground`) against the
Module `J1` schematic and the Core `J7` schematic and the Core
I²C bus identity (`IO48` / `IO45`), a standalone schematic-
backed reference doc in the per-board `docs/hardware/s360-312-r4-*.md`
pattern, KiCad schematic source / KiCad PCB source / KiCad
project metadata / BOM / CPL / Gerber / drill / STEP / board-
image evidence for `S360-312-R4`, or progress on the systemic
Core abstract-bus rebind (`CORE-ABSTRACT-BUS-001`, alias for
[`release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups))
— and to record the result of that re-check as a dated audit-log
entry in
[`docs/hardware/s360-312-r4-dac.md` HW-PINMAP-312-FOLLOWUP audit log](hardware/s360-312-r4-dac.md#hw-pinmap-312-followup-audit-log).
**The status remains `partial — schematic evidence available;
package reconciliation pending`.** No reconciliation row has
been promoted. No silkscreen / harness / bench / I²C / Cloudlift
/ UART / DIP-switch-address / voltage-mode-jumper evidence is
on file. The Core `J7` pin-1 `+5V` vs Module `J1` pin-1
`+3.3V` voltage-rail discrepancy is not resolved. The DIP-
switch I²C address-selection scheme on `SW1` / `SW2` is not
resolved (the schematic shows the address-select hardware via
4.7 kΩ pull-ups `R3` / `R5` / `R7` for `IC1` `A0` / `A1` / `A2`
and `R4` / `R6` / `R8` for `IC2` `2A0` / `2A1` / `2A2`, but
not the DIP-position-to-address mapping). The UART0-vs-Nextion
arbitration question on Module `J1` pins 4 / 5 is not resolved.
The `J2` / `J3` Cloudlift S12 output silkscreen pin-1 location
is not resolved. The `fan_dac_voltage_mode` 5 V vs 10 V
hardware-select identity is not resolved. The stale header-
comment block in
[`packages/expansions/fan_gp8403.yaml`](../packages/expansions/fan_gp8403.yaml)
lines 13–18 (which disagrees with both Module `J1` and Core
`J7` schematics) is not corrected — the active YAML body is
unaffected because `${fan_dac_i2c_id}` uses abstract-bus
inheritance, but the comment is left in place. The dual-DAC /
dual-output canonical-abstraction decision stays in its current
form (the package YAML is already dual-channel and matches the
schematic's two `IC1` / `IC2` DACs on two `J2` / `J3` outputs;
broadening the singular hardware-catalog `description` belongs
to a separate later JSON-only PR, not to HW-PINMAP-312-FOLLOWUP).
`PACKAGE-DAC-001` (alias: `PACKAGE-GAP-001` FanDAC slice) stays
blocked. The downstream FanDAC chain (`PRODUCT-DAC-001`,
`WEBFLASH-DAC-001`, `RELEASE-DAC-001`, `WF-IMPORT-DAC-001`)
stays blocked. Release-One is unchanged. The LED preview path
is unchanged. FanTRIAC stays `status: blocked`. The Sense360
LED Release-One exclusion is unchanged. The FanDAC ↔ AirIQ
mutex (`rules.fandac_conflicts_with_airiq: true`) and the
fan-driver `max-one-of` rule are unchanged.

**Why this is the next actionable evidence item.** After
[§S360-100-BENCH-001 update](#s360-100-bench-001-update-2026-05-18-evidence-pass-investigation),
[§HW-PINMAP-320-FOLLOWUP update](#hw-pinmap-320-followup-update-2026-05-18-evidence-pass-investigation),
and
[§COMPLIANCE-001 update](#compliance-001-update-2026-05-18-mains-voltage-advancedmanual-warning-sign-off-evidence-pass-investigation)
re-confirmed the broad Core-board evidence gate, the
FanTRIAC-board pin-map / direct-GPIO / timing / mains-compliance
gates, and the COMPLIANCE-001 mains-voltage advanced /
manual-warning sign-off gates all stay open, and after
[§PACKAGE-TRIAC-001 update](#package-triac-001-update-deferred--hw-005--hw-pinmap-320-followup--compliance-001-not-landed)
deferred PACKAGE-TRIAC-001,
[§TRIAC-QUEUE-001 update](#triac-queue-001-update-remaining-fantriac-chain-normalized-after-package-deferral)
normalised the remaining FanTRIAC chain as blocked, and
[§HW-PINMAP-311-FOLLOWUP update](#hw-pinmap-311-followup-update-2026-05-18-evidence-pass-investigation)
re-confirmed the FanPWM pin-map / package reconciliation gate
stays open, the next actionable docs-only follow-up shifts onto
the FanDAC (`S360-312`) track because HW-ASSETS-003 already
committed the module-side schematic PDF + curated artifact
index and HW-PINMAP-312 already landed the audit doc, leaving
the pin-map / DIP-switch / UART-arbitration / Cloudlift-output /
voltage-mode-jumper / package reconciliation as the named next
step. The package-readiness matrix (`fan_gp8403.yaml`
`needs-package-reconciliation` + `bench-evidence-pending`), the
board-readiness matrix (`S360-312` `partially-documented` +
`package-yaml-pending`), the firmware-package-mapping audit
See-also entry (HW-PINMAP-312 out of scope for HW-009 today),
the product-readiness matrix (`Ceiling-POE-FanDAC-RoomIQ`
`missing-product-yaml`), the webflash-exposure-readiness matrix
(FanDAC `not-webflash-ready`), and the release-artifact-readiness
matrix (FanDAC `not-release-ready`) all forward-reference
HW-PINMAP-312-FOLLOWUP. The Core abstract-bus disagreements that
bind `${expansion_i2c}` / `${halo_i2c}` / `${fan_dac_i2c_id}`
remain owed to `CORE-ABSTRACT-BUS-001`, not to this update.

**Investigation scope.** The 2026-05-18 re-check inspected the
following committed files and re-confirmed each against the
HW-PINMAP-312 reconciliation rules in
[`docs/hardware/s360-312-r4-dac.md`](hardware/s360-312-r4-dac.md)
and the HW-ASSETS-003 artifact-index rules in
[`docs/hardware/artifacts/S360-312-R4.md`](hardware/artifacts/S360-312-R4.md):

- [`docs/hardware/schematics/S360-312-R4.pdf`](../docs/hardware/schematics/S360-312-R4.pdf)
  — HW-ASSETS-003 module-side schematic, byte-identical to the
  upload (SHA256
  `2888f626bfa0139d2190f154f9b02ecf4cb06f2522a5b5802eaf96e16de39e28`,
  122,230 bytes). Schematic-tier evidence; not changed by this
  re-check. Confirms the visible content: MT3608 `+3.3V` →
  `+12V` boost (`U1`, `L1 22 µH`, `D1 SS34`, `R1 2 kΩ` / `R2
  38 kΩ` feedback divider, `C1` / `C2 22 µF / 0805 / 10 V`,
  indicator `R9 500 Ω` + blue LED `D6`); two `GP8403-TC50-EW`
  DACs (`IC1` / `IC2`) on a shared I²C bus, each with its own
  6-position DIP switch (`SW1` / `SW2`) with 4.7 kΩ pull-ups
  (`R3` / `R5` / `R7` for `IC1` `A0` / `A1` / `A2`; `R4` / `R6`
  / `R8` for `IC2` `2A0` / `2A1` / `2A2`) and its own 3-pin
  Cloudlift S12 output (`VOUT0` / `VOUT1` → `C7` / `C8 10 µF` +
  `D4` / `D2` blocking diodes → `J2` for `IC1`; `VOUT0` /
  `VOUT1` → `C9` / `C10 10 µF` + `D5` / `D3` blocking diodes →
  `J3` for `IC2`); 6-pin "From Core" connector `J1` (pins 1–6:
  `+3.3V` / `I2C_SDA` / `I2C_SCL` / `UART_RX` / `UART_TX` /
  `GND`); 4-pin "NEXTION DISPLAY" connector `J7` (`+5V` /
  `ESP32_RXD` / `ESP32_TXD` / `GND`); mounting holes `H1..H4`.
  **No edit.**
- [`docs/hardware/artifacts/S360-312-R4.md`](hardware/artifacts/S360-312-R4.md)
  — HW-ASSETS-003 curated artifact index. Records the uploaded
  inventory (single 122,230-byte PDF; canonical name
  `S360-312-R4.pdf`), the visible schematic content, the
  retained-but-not-committed list (KiCad schematic source, KiCad
  PCB source, KiCad project metadata, BOM, CPL, Gerbers, drill
  files, STEP, board images all marked `not provided in this
  upload`), and the artifact-side Open Questions (HW-PINMAP-312
  voltage-rail discrepancy; dual-DAC capacity broader than
  singular catalog description; I²C address-selection scheme;
  Cloudlift S12 output connector pin order; long-term storage
  decision for retained-but-not-committed artifacts; standalone
  hardware reference doc not yet committed). No new artifact has
  been added since HW-ASSETS-003. **No edit.**
- [`docs/hardware/s360-312-r4-dac.md`](hardware/s360-312-r4-dac.md)
  — HW-PINMAP-312 audit doc. Status row stays `partial —
  schematic evidence available; package reconciliation pending`.
  Every row of the
  [Schematic summary](hardware/s360-312-r4-dac.md#schematic-summary),
  [Connector / pin-map findings](hardware/s360-312-r4-dac.md#connector--pin-map-findings),
  [Voltage-rail discrepancy](hardware/s360-312-r4-dac.md#voltage-rail-discrepancy),
  [UART pins on `J1` pins 4–5](hardware/s360-312-r4-dac.md#uart-pins-on-j1-pins-45),
  [I²C address-selection scheme](hardware/s360-312-r4-dac.md#i2c-address-selection-scheme),
  [Open documentation questions](hardware/s360-312-r4-dac.md#open-documentation-questions),
  [Existing package abstraction](hardware/s360-312-r4-dac.md#existing-package-abstraction),
  [Header-comment claims vs schematic evidence](hardware/s360-312-r4-dac.md#header-comment-claims-vs-schematic-evidence),
  [Parent Core packages that resolve `fan_dac_i2c_id`](hardware/s360-312-r4-dac.md#parent-core-packages-that-resolve-fan_dac_i2c_id),
  and
  [Reconciliation findings](hardware/s360-312-r4-dac.md#reconciliation-findings)
  tables is unchanged. Every item in the
  [Known unresolved issues](hardware/s360-312-r4-dac.md#known-unresolved-issues)
  list stays open. A new
  [HW-PINMAP-312-FOLLOWUP audit log](hardware/s360-312-r4-dac.md#hw-pinmap-312-followup-audit-log)
  section is added with a single 2026-05-18 audit row recording
  this re-check; no other section is edited.
- [`docs/hardware/s360-100-r4-core.md`](hardware/s360-100-r4-core.md)
  — Core schematic-backed reference. The §[J7 — GP8403 fan
  connector (6-pin)](hardware/s360-100-r4-core.md#j7--gp8403-fan-connector-6-pin)
  net list (`+5V` / `I2C_SDA` / `I2C_SCL` / `UART_RX` /
  `UART_TX` / `GND`, no `verify` flag on the pin order), the
  §[I2C bus](hardware/s360-100-r4-core.md#i2c-bus) capture
  (`I2C_SDA` at ESP32 `IO48` with `R22 10 kΩ`; `I2C_SCL` at
  `IO45` with `R21 10 kΩ`; bus reaches `J7` / `J9` / `J10` /
  SX1509 expander `U3`), the §[Pin assignments](hardware/s360-100-r4-core.md#pin-assignments)
  rows for `TXD0` (pin 37) / `RXD0` (pin 36) → `J7` UART pair,
  and the §[UART buses](hardware/s360-100-r4-core.md#uart-buses)
  line 349 note that UART0 is "also used as boot log on USB" all
  stay as the schematic-only source of truth for the Core side
  of HW-PINMAP-312-FOLLOWUP. **No edit** — the voltage-rail
  discrepancy is recorded in [`s360-312-r4-dac.md`](hardware/s360-312-r4-dac.md)
  and is **not** rewritten on the Core-side doc.
- [`packages/expansions/fan_gp8403.yaml`](../packages/expansions/fan_gp8403.yaml)
  — single FanDAC firmware package (dual-channel). The header-
  comment block (lines 13–18) that claims `Pin 4 (SDA) → GPIO39`,
  `Pin 5 (SCL) → GPIO40`, `Pin 2 (3.3V) → Power`, `Pin 1 (GND) →
  Ground` continues to disagree with both Module `J1` and Core
  `J7` schematics and with the Core I²C bus identity (`IO48` /
  `IO45`). The active YAML body uses
  `gp8403.i2c_id: ${fan_dac_i2c_id}` (default `i2c0` line 26),
  `gp8403.address: ${fan_dac_address}` (default `0x58`, alternate
  `0x59` line 27), and `gp8403.voltage: ${fan_dac_voltage_mode}`
  (default `10V`, alternate `5V` line 30); two
  `output.platform: gp8403` channels 0 / 1; two `fan.platform:
  speed` entities with `speed_count: 100`; per-channel template
  sensors / voltage calculations; `fan_0_set_speed` /
  `fan_1_set_speed` / `fan_set_both_speed` / `fan_emergency_stop`
  scripts; `fan_0_target_speed` / `fan_1_target_speed` /
  `fan_auto_mode` / `fan_link_mode` globals. Resolution of the
  stale header-comment block belongs to `PACKAGE-DAC-001` /
  `PACKAGE-GAP-001` FanDAC slice, not to HW-PINMAP-312-FOLLOWUP.
  **No edit.**
- [`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml)
  and
  [`packages/hardware/sense360_core.yaml`](../packages/hardware/sense360_core.yaml)
  — Core abstract-bus parent packages. Both inherit the
  `${fan_dac_i2c_id}` substitution path: ceiling form factor
  uses `expansion_i2c` (per
  [`tests/generate_test_configs.py`](../tests/generate_test_configs.py)
  lines 140–145), non-ceiling form factor uses the
  package-level default `i2c0`. Whether `i2c0` and
  `expansion_i2c` both ultimately resolve to the schematic-
  verified Core I²C bus at `IO48` / `IO45` (with the shared
  SX1509 / J7 / J9 / J10 fan-out per
  [§I2C bus](hardware/s360-100-r4-core.md#i2c-bus)) belongs to
  `CORE-ABSTRACT-BUS-001` (alias for
  [`release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups)),
  **not** to HW-PINMAP-312-FOLLOWUP. **No edit.**
- [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  — `S360-312` row lines 82–91. `group: Inline`, `type: Driver`,
  `friendly_name: Sense360 DAC`, `sku: S360-312`, `rev: R4`,
  `old_name: Fan_GP8403`, `description: 0 to 10V analog fan
  driver, for example Cloudlift S12.`,
  `schematic_status: cataloged_unverified`, no `schematic_file`.
  No new evidence supports flipping `schematic_status` to
  `verified` or setting `schematic_file` to
  `docs/hardware/schematics/S360-312-R4.pdf`. The singular
  `description` is broader-than-current-capacity (the board
  carries two GP8403 DACs on two Cloudlift outputs); broadening
  belongs to a separate later JSON-only PR. **No edit.**
- [`config/product-catalog.json`](../config/product-catalog.json),
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  — no FanDAC-bearing product / build exists; `FanDAC` stays
  reserved in `canonical_modules` (line 13) subject to the
  fan-driver `max-one-of` rule (`FAN_DRIVER_TOKENS` in
  [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py)
  line 37) **and** the explicit `FanDAC` ↔ `AirIQ` mutex
  (`rules.fandac_conflicts_with_airiq: true` line 30). The two
  shipping product-catalog entries (`Ceiling-POE-VentIQ-RoomIQ`
  `status: production` / `channel: stable`,
  `Ceiling-POE-VentIQ-RoomIQ-LED` `status: preview` /
  `channel: preview`) and the blocked
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` (`status: blocked`,
  `blocker: HW-005`, `webflash_build_matrix: false`) are
  unchanged. The two webflash-builds entries
  (`Ceiling-POE-VentIQ-RoomIQ` stable and
  `Ceiling-POE-VentIQ-RoomIQ-LED` preview) are unchanged. **No
  edit.**
- [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
  — `S360-312` hardware-evidence and productization-axis table
  rows are unchanged. The
  [§`S360-312` Sense360 DAC](hardware/board-readiness-matrix.md#s360-312-sense360-dac)
  subsection gains a new `Open work` bullet recording this
  2026-05-18 re-check; the `Role`, `Hardware evidence`, `Package
  YAML`, `Productization`, and `Required before promotion`
  bullets are preserved. **Edit limited to one new bullet.**
- [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
  — `fan_gp8403.yaml` row stays `needs-package-reconciliation`
  + `bench-evidence-pending`. The Core rule preamble gains a new
  paragraph recording this 2026-05-18 re-check (after the
  existing HW-PINMAP-311-FOLLOWUP paragraph, before
  `## Status summary`); no table row edits; the per-package
  §[`fan_gp8403.yaml` / S360-312](hardware/package-readiness-matrix.md#fan_gp8403yaml--s360-312)
  subsection is unchanged. **Edit limited to one new preamble
  paragraph.**
- [`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
  — HW-009 See-also entry for FanDAC is unchanged (FanDAC is
  out of scope for HW-009 today because `S360-312` is still
  `cataloged_unverified`). **No edit.**
- [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md)
  — §[Sense360 DAC (`S360-312`)](hardware/remaining-board-documentation-audit.md#sense360-dac-s360-312)
  classification stays `partially-documented`, `not-needed-for-
  release-one`. **No edit.**
- [`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md)
  — `S360-312` snapshot row stays `partially-documented` +
  `design-pending`. **No edit.**
- [`docs/product-readiness-matrix.md`](product-readiness-matrix.md)
  — `Ceiling-POE-FanDAC-RoomIQ` (FanDAC slice; AirIQ excluded
  by mutex) row stays `missing-product-yaml`. **No edit.**
- [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md)
  — §[FanDAC / S360-312](webflash-exposure-readiness-matrix.md#fandac--s360-312)
  stays `not-webflash-ready` (AirIQ-bearing FanDAC variants
  forbidden by mutex). **No edit.**
- [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
  — §[FanDAC / S360-312](release-artifact-readiness-matrix.md#fandac--s360-312)
  stays `not-release-ready`. **No edit.**
- [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)
  — §[Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups)
  records the Core abstract-bus rebind (alias
  `CORE-ABSTRACT-BUS-001`); the bus identity question owed by
  the FanDAC chain is included there, **not** in
  HW-PINMAP-312-FOLLOWUP. **No edit.**
- [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
  — COMPLIANCE-001 mains-voltage tracker applies to `S360-320` /
  `S360-400` and does not gate FanDAC. Tracked here as a sibling
  evidence record only. **No edit.**

**Outcome.** The
[`docs/hardware/s360-312-r4-dac.md` HW-PINMAP-312-FOLLOWUP audit log](hardware/s360-312-r4-dac.md#hw-pinmap-312-followup-audit-log)
under a newly-added `## HW-PINMAP-312-FOLLOWUP audit log`
section records a single 2026-05-18 audit row mirroring the
preceding HW-PINMAP-311-FOLLOWUP / HW-PINMAP-320-FOLLOWUP /
COMPLIANCE-001 / S360-100-BENCH-001 structure: scope (re-check
the named evidence items), files inspected (those enumerated
above), outcome (status remains `partial — schematic evidence
available; package reconciliation pending`; all six
reconciliation flags stay open; downstream gates stay blocked;
Release-One / LED preview / FanTRIAC blocked / Sense360 LED
Release-One exclusion / FanDAC ↔ AirIQ mutex / fan-driver
`max-one-of` rule all unchanged). The
[`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
Core rule preamble gains a parallel short paragraph confirming
the `fan_gp8403.yaml` row stays `needs-package-reconciliation`
+ `bench-evidence-pending`. The
[`docs/hardware/board-readiness-matrix.md` §`S360-312` Sense360 DAC](hardware/board-readiness-matrix.md#s360-312-sense360-dac)
subsection gains a parallel short `Open work` bullet confirming
the same outcome. No other documentation, configuration,
package, product, WebFlash wrapper, test, script, workflow,
firmware, manifest, schematic PDF, artifact index, or Core-side
reference doc is changed.

**Out of scope (unchanged by this update).** This
HW-PINMAP-312-FOLLOWUP re-check does **not** move the
HW-PINMAP-312 audit doc off `partial — schematic evidence
available; package reconciliation pending`; does **not** resolve
the Core `J7` pin-1 `+5V` vs Module `J1` pin-1 `+3.3V`
voltage-rail discrepancy; does **not** resolve the DIP-switch
I²C address-selection scheme on `SW1` / `SW2`; does **not**
resolve the UART0-vs-Nextion arbitration question on Module
`J1` pins 4 / 5; does **not** resolve the `J2` / `J3` Cloudlift
S12 output silkscreen pin-1 location; does **not** resolve the
`fan_dac_voltage_mode` 5 V vs 10 V hardware-select identity;
does **not** correct the stale header-comment block in
[`packages/expansions/fan_gp8403.yaml`](../packages/expansions/fan_gp8403.yaml)
lines 13–18; does **not** broaden the singular hardware-catalog
`description` to record the dual-DAC capacity; does **not** edit
[`packages/expansions/fan_gp8403.yaml`](../packages/expansions/fan_gp8403.yaml),
[`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml),
or
[`packages/hardware/sense360_core.yaml`](../packages/hardware/sense360_core.yaml);
does **not** edit
[`docs/hardware/s360-100-r4-core.md`](hardware/s360-100-r4-core.md),
[`docs/hardware/artifacts/S360-312-R4.md`](hardware/artifacts/S360-312-R4.md),
or
[`docs/hardware/schematics/S360-312-R4.pdf`](hardware/schematics/S360-312-R4.pdf);
does **not** edit any other per-board reference doc
([`s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md),
[`s360-311-r4-pwm.md`](hardware/s360-311-r4-pwm.md),
[`s360-320-r4-triac.md`](hardware/s360-320-r4-triac.md),
[`s360-400-r4-power.md`](hardware/s360-400-r4-power.md),
[`s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md), etc.); does
**not** flip `S360-312` `schematic_status` from
`cataloged_unverified` in
[`config/hardware-catalog.json`](../config/hardware-catalog.json);
does **not** set `schematic_file` for `S360-312`; does **not**
add a `FanDAC`-bearing entry to
[`config/product-catalog.json`](../config/product-catalog.json)
or
[`config/webflash-builds.json`](../config/webflash-builds.json);
does **not** add or modify any product YAML under
[`products/`](../products/) or any WebFlash wrapper under
[`products/webflash/`](../products/webflash/); does **not** add
or modify any package YAML under [`packages/`](../packages/);
does **not** edit any test under [`tests/`](../tests/), any
script under [`scripts/`](../scripts/), any workflow under
`.github/workflows/`, any component under `components/`, any
header under `include/`, `firmware/*`, `manifest.json`, or
`firmware/sources.json`; does **not** regenerate firmware,
create a GitHub Release or tag, or change any WebFlash manifest
/ import; does **not** advance `HW-PINMAP-312-FOLLOWUP`,
`PACKAGE-DAC-001`, `PRODUCT-DAC-001`, `WEBFLASH-DAC-001`,
`RELEASE-DAC-001`, `WF-IMPORT-DAC-001`, or
`CORE-ABSTRACT-BUS-001`; does **not** close
`S360-100-BENCH-001`, `HW-PINMAP-320-FOLLOWUP`,
`HW-PINMAP-311-FOLLOWUP`, or `COMPLIANCE-001`; does **not**
unblock FanTRIAC (HW-005 stays a separate gate); does **not**
change the Release-One configuration
(`Ceiling-POE-VentIQ-RoomIQ`, version `1.0.0`, channel
`stable`, artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
`v1.0.0`); does **not** change the LED preview entry
(`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`,
`channel: preview`, artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`);
does **not** change the Sense360 LED Release-One exclusion;
does **not** relax or change the `FanDAC` ↔ `AirIQ` mutex
(`rules.fandac_conflicts_with_airiq: true`) or the fan-driver
`max-one-of` rule (`FAN_DRIVER_TOKENS` in
[`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py));
does **not** resolve the Core J10 vs RoomIQ J6 pin-order open
question (HW-009 `needs-silkscreen/bench-verification`); does
**not** resolve the systemic Core abstract-bus mismatch
enumerated in
[`release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups);
and does **not** change the mains-voltage compliance status for
`S360-320` or `S360-400` (owned by COMPLIANCE-001).

**Next audit-log trigger.** The next
HW-PINMAP-312-FOLLOWUP audit-log row should appear when
committed evidence is added to this repository that the
field-evidence rules above can cite: operator-attributed
silkscreen captures of the Core-side `J7` 1-to-6 pin order and
the parallel module-side `J1` 1-to-6 pin order (particularly
the pin-1 rail value `+5V` vs `+3.3V`); physical 6-pin Core ↔
module harness inspection with conductor-by-conductor pin
mapping recorded; silkscreen reading of the module-side `J2` /
`J3` Cloudlift S12 output connector pin-1 location and harness
mapping to the fan; oscilloscope / I²C-logic-analyser captures
of the GP8403 DAC outputs at `J2` / `J3`, the shared I²C bus
exchange to `IC1` / `IC2`, the `vout0` / `vout1` analog rail
behaviour at the configured `${fan_dac_voltage_mode}`, or the
Cloudlift S12 functional response against a populated
`S360-100-R4` + `S360-312-R4` pair, with operator / reviewer
identity and review date recorded; DIP-switch I²C address-
selection measurement on `SW1` / `SW2` to determine which
switch positions produce which I²C address pair on `IC1` /
`IC2`; identification of the operator-selectable hardware that
switches between 5 V and 10 V output modes (jumper / solder-
bridge / DIP position); UART0-vs-Nextion arbitration evidence
(whether a FanDAC build can co-exist with USB boot-log output
on UART0, or whether the Nextion display path is mutually
exclusive with USB debugging); a standalone schematic-backed
reference doc (e.g. `docs/hardware/s360-312-r4-fandac.md`)
tying together the module-side `J1`, the Core-side `J7`, the
Core I²C bus, the Core UART0 path, the Nextion display
routing, and the FanDAC package bindings; resolution of the
stale header-comment connector / GPIO claims in
[`packages/expansions/fan_gp8403.yaml`](../packages/expansions/fan_gp8403.yaml)
lines 13–18; KiCad schematic source / KiCad PCB source / KiCad
project metadata / BOM / CPL / Gerbers / drill files / STEP /
or board images for `S360-312-R4` that the audit can cite by
repo path; or progress on the systemic Core abstract-bus
rebind (`CORE-ABSTRACT-BUS-001`, alias for
[`release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups)).
Until any of those land, the next audit-log entry should
report the same `partial — schematic evidence available;
package reconciliation pending` outcome with the new
inspection date.

## HW-PINMAP-310-FOLLOWUP update (2026-05-18 — schematic-backed reconciliation)

HW-PINMAP-310-FOLLOWUP is the **docs-only schematic-backed
reconciliation** that consumes the module-side schematic evidence
committed under HW-ASSETS-310 at
[`docs/hardware/schematics/S360-310-R4.pdf`](hardware/schematics/S360-310-R4.pdf)
and inventoried in
[`docs/hardware/artifacts/S360-310-R4.md`](hardware/artifacts/S360-310-R4.md),
and uses that evidence to promote the HW-PINMAP-310 audit doc at
[`docs/hardware/s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md)
from `pending — schematic/design evidence required` to
`partial — schematic evidence available; package reconciliation
pending`. The purpose of this update is to record, on 2026-05-18,
what schematic-backed reconciliation work HW-PINMAP-310-FOLLOWUP
performed against the FanRelay pin-map / connector / drive-topology /
package gates owed by HW-PINMAP-310, and what stays unresolved
after the FOLLOWUP — and to record the result as a dated audit-log
entry in
[`docs/hardware/s360-310-r4-relay.md` HW-PINMAP-310-FOLLOWUP audit log](hardware/s360-310-r4-relay.md#hw-pinmap-310-followup-audit-log).
**The status is `partial — schematic evidence available; package
reconciliation pending`** after this update (promoted from the
prior `pending — schematic/design evidence required`). Schematic-
backed logical alignment between module-side `J2` and Core-side
`J4` is recorded; module-side relay coil-drive topology
(`Q1` MMBT3904 NPN low-side; `R1` 1 kΩ base; `R2` 10 kΩ pull-down;
`D1` flyback; coil rail `+5V`; no opto; no indicator LED; no
snubber) is recorded; module-side `J1` 3-pin load-side connector
identity is recorded at the connector / pin-count layer; the
`K1` mechanical-relay reference is recorded with the explicit
caveat that no part number / coil-voltage label / contact-current
rating is on the sheet. No silkscreen / harness / `K1` BOM / bench
evidence is on file. The `IO3` vs `GPIO4` vs `GPIO10` `relay_pin`
abstract-bus disagreement is **not** resolved (resolution belongs
to `CORE-ABSTRACT-BUS-001`, not HW-PINMAP-310-FOLLOWUP).
`PACKAGE-RELAY-001` (alias: `PACKAGE-GAP-001` FanRelay slice)
stays blocked behind `CORE-ABSTRACT-BUS-001` + silkscreen /
harness / `K1` BOM evidence. The downstream FanRelay chain
(`PRODUCT-RELAY-001`, `WEBFLASH-RELAY-001`, `RELEASE-RELAY-001`,
`WF-IMPORT-RELAY-001`) stays blocked. Release-One is unchanged.
The LED preview path is unchanged. FanTRIAC stays
`status: blocked`. The Sense360 LED Release-One exclusion is
unchanged. COMPLIANCE-001 status for `S360-320` / `S360-400` is
unchanged.

**Why this is the next actionable evidence item.** After
[§HW-PINMAP-311-FOLLOWUP update](#hw-pinmap-311-followup-update-2026-05-18-evidence-pass-investigation)
and
[§HW-PINMAP-312-FOLLOWUP update](#hw-pinmap-312-followup-update-2026-05-18-evidence-pass-investigation)
re-confirmed that the FanPWM and FanDAC pin-map / package
reconciliation gates stay open against `partial — schematic
evidence available; package reconciliation pending`, the next
actionable docs-only follow-up shifts onto the FanRelay
(`S360-310`) track because the HW-ASSETS-310 schematic ingest
landed but the HW-PINMAP-310 audit doc still carried the
historical `pending — schematic/design evidence required` status
text. HW-PINMAP-310-FOLLOWUP closes that documentation gap by
consuming the committed schematic, producing the schematic-backed
reconciliation view, and recording the remaining silkscreen /
harness / `K1` BOM / bench / Core abstract-bus evidence gaps in
the per-board audit doc and across the downstream readiness
matrices.

**Scope.** Documentation only and cross-link only. Specifically
this update:

- Promotes [`docs/hardware/s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md)
  from `pending — schematic/design evidence required` to
  `partial — schematic evidence available; package reconciliation
  pending`. Rewrites the audit doc body to add the new schematic-
  backed sections (Schematic summary; Connector / pin-map
  findings; Relay drive findings; Load / contact findings;
  Existing package abstraction; Reconciliation findings; Known
  unresolved issues; Required evidence before promotion; Follow-up
  PR sequence) in the per-audit pattern used by
  [`s360-311-r4-pwm.md`](hardware/s360-311-r4-pwm.md) /
  [`s360-312-r4-dac.md`](hardware/s360-312-r4-dac.md) /
  [`s360-320-r4-triac.md`](hardware/s360-320-r4-triac.md), and
  appends an `HW-PINMAP-310-FOLLOWUP audit log` section that
  carries the 2026-05-18 dated entry.
- Refreshes the cross-link wording in
  [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
  (`S360-310` hardware-evidence row and §`S360-310` Sense360
  Relay board-by-board notes) so the audit-doc status reads
  `partial — schematic evidence available; package reconciliation
  pending` instead of the pre-FOLLOWUP `pending — schematic/design
  evidence required`.
- Refreshes the cross-link wording in
  [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md)
  (Sense360 Relay (`S360-310`) audit-doc bullet) for the same
  reason.
- Refreshes the cross-link wording in
  [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
  (PACKAGE-GAP-001 dependency bullet for HW-PINMAP-310;
  `fan_relay.yaml` row; §`fan_relay.yaml` / S360-310 detail) so
  the audit-doc status reads `partial — schematic evidence
  available; package reconciliation pending` and the allowed-action
  cell records that HW-PINMAP-310-FOLLOWUP has landed but
  `PACKAGE-RELAY-001` stays blocked behind `CORE-ABSTRACT-BUS-001`
  + silkscreen / harness / `K1` BOM evidence.
- Refreshes the cross-link wording in
  [`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
  (HW-009 Release-One package-stack `relay_pin: GPIO4` bullet)
  so it cites
  [`s360-310-r4-relay.md` Reconciliation findings](hardware/s360-310-r4-relay.md#reconciliation-findings)
  (instead of the pre-FOLLOWUP §`Pin-map reconciliation status`)
  and records the audit status as `partial — schematic evidence
  available; package reconciliation pending` after
  HW-PINMAP-310-FOLLOWUP.
- Refreshes the cross-link wording in
  [`docs/product-readiness-matrix.md`](product-readiness-matrix.md)
  (§`FanRelay / S360-310` subsection) so the descriptive narrative
  stops saying "no `S360-310-R4` schematic is committed" and
  reflects the post-HW-ASSETS-310 / post-HW-PINMAP-310-FOLLOWUP
  state — without changing any readiness class.
- Refreshes the cross-link wording in
  [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md)
  (`FanRelay / S360-310` exposure-table row and §`Relay / S360-310
  WebFlash posture` subsection) so the descriptive narrative stops
  saying "schematic uncommitted" / "no committed module-side
  schematic PDF" and reflects the post-HW-ASSETS-310 / post-HW-
  PINMAP-310-FOLLOWUP state — without changing any exposure class.
- Refreshes the cross-link wording in
  [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
  (`FanRelay / S360-310` release-table row and §`Relay / S360-310
  release posture` subsection) so the descriptive narrative reflects
  the post-HW-ASSETS-310 / post-HW-PINMAP-310-FOLLOWUP state —
  without changing any release class.
- Refreshes the inventory entry for
  [`docs/hardware/s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md)
  in this cleanup audit's [§Findings summary](#findings-summary)
  table to record the promoted status and the schematic-backed
  reconciliation content.

**Files inspected.**
[`docs/hardware/schematics/S360-310-R4.pdf`](hardware/schematics/S360-310-R4.pdf)
(HW-ASSETS-310 module-side schematic, byte-identical to upload;
SHA256
`441f0ccd681b5425fa9d276e6d7fb1bf289597674342dc8d9b8e656a23896c7d`;
38,967 bytes);
[`docs/hardware/artifacts/S360-310-R4.md`](hardware/artifacts/S360-310-R4.md)
(HW-ASSETS-310 curated artifact index — uploaded inventory,
schematic content capture, retained-but-not-committed list,
artifact-side Open Questions);
[`docs/hardware/s360-100-r4-core.md`](hardware/s360-100-r4-core.md)
§[J4 — Relay module connector (3-pin)](hardware/s360-100-r4-core.md#j4--relay-module-connector-3-pin),
§[Pin assignments](hardware/s360-100-r4-core.md#pin-assignments)
(`IO3 = Relay`),
§[Fan / driver outputs](hardware/s360-100-r4-core.md#fan--driver-outputs),
and
§[S360-100-BENCH-001 status](hardware/s360-100-r4-core.md#s360-100-bench-001-status)
(bench / silkscreen / manufacturing-artifact gate);
[`docs/hardware/s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md)
(rewritten by this update — §Status, §Purpose and scope,
§Board identity, §Repository evidence, §Schematic summary,
§Connector / pin-map findings, §Relay drive findings,
§Load / contact findings, §Existing package abstraction,
§Reconciliation findings, §Known unresolved issues,
§Package YAML status, §Product / WebFlash status,
§Required evidence before promotion, §Follow-up PR sequence,
§Do-not-change guardrails, §See also, §HW-PINMAP-310-FOLLOWUP
audit log);
[`packages/expansions/fan_relay.yaml`](../packages/expansions/fan_relay.yaml)
(`fan_relay_pin: ${relay_pin}` line 27; override-hook comment
lines 22–25; `switch.platform: gpio` with `pin: ${fan_relay_pin}`
line 38; `script: fan_emergency_stop` lines 58–65);
[`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml)
(`relay_pin: GPIO4` line 61 — disagrees with Core schematic
`Relay = IO3`);
[`packages/hardware/sense360_core.yaml`](../packages/hardware/sense360_core.yaml)
(`relay_pin: GPIO10` line 63 — disagrees with Core schematic);
[`config/hardware-catalog.json`](../config/hardware-catalog.json)
`S360-310` row lines 62–70 (`group: Inline`, `type: Driver`,
`friendly_name: Sense360 Relay`, `sku: S360-310`, `rev: R4`,
`old_name: S360-Relay-C`, `description: On/off relay for bathroom
fans.`, `schematic_status: cataloged_unverified`, no
`schematic_file`);
[`config/product-catalog.json`](../config/product-catalog.json)
(no FanRelay-bearing entry);
[`config/webflash-builds.json`](../config/webflash-builds.json)
(no FanRelay-bearing build);
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
(`FanRelay` reserved in `canonical_modules` line 11, subject to
the fan-driver `max-one-of` rule enforced by `FAN_DRIVER_TOKENS`
in [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py));
[`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
(`S360-310` hardware-evidence row + §`S360-310` Sense360 Relay
notes — refreshed by this update);
[`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md)
(Sense360 Relay (`S360-310`) row + §Sense360 Relay (`S360-310`)
subsection — refreshed by this update);
[`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
(`fan_relay.yaml` row + §`fan_relay.yaml` / S360-310 detail +
HW-PINMAP-310 bullet — refreshed by this update);
[`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
(HW-009 Release-One package-stack `relay_pin: GPIO4` bullet —
refreshed by this update);
[`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md)
(`S360-310 Sense360 Relay` snapshot row — unchanged by this
update; class assignments stay `partially-documented` +
`design-pending`);
[`docs/product-readiness-matrix.md`](product-readiness-matrix.md)
(§`FanRelay / S360-310` subsection — descriptive cross-link
refreshed by this update; readiness class unchanged);
[`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md)
(`FanRelay / S360-310` exposure-table row + §`Relay / S360-310
WebFlash posture` subsection — descriptive cross-link refreshed
by this update; exposure class unchanged);
[`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
(`FanRelay / S360-310` release-table row + §`Relay / S360-310
release posture` subsection — descriptive cross-link refreshed by
this update; release class unchanged);
[`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)
§[Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups)
(Core abstract-bus rebind, alias `CORE-ABSTRACT-BUS-001` —
unchanged by this update);
[`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
(COMPLIANCE-001 mains-voltage tracker — unchanged; applies to
`S360-320` / `S360-400`; does not gate FanRelay unless a future
product switches mains loads).

**Outcome.** **Status promoted to `partial — schematic evidence
available; package reconciliation pending`** in
[`docs/hardware/s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md).
HW-PINMAP-310-FOLLOWUP consumed the HW-ASSETS-310 schematic and
produced the schematic-backed reconciliation view: module-`J2` ↔
Core-`J4` logical net match (`+5V` ↔ `+5V`, `Relay` ↔ `Relay`,
`GND` ↔ `GND`) is schematic-backed; module-side relay coil-drive
topology (`Q1` MMBT3904 NPN low-side; `R1` 1 kΩ; `R2` 10 kΩ; `D1`
flyback; coil rail `+5V`; no opto; no indicator LED; no snubber)
is schematic-backed; module-side `J1` 3-pin load-side connector
identity is schematic-confirmed at the connector / pin-count
layer. **The following stay unresolved:** module-side `J2`
silkscreen pin-1 orientation; module-side `J1` silkscreen pin-1
orientation; module-side `J1` NO / COM / NC mapping; Core-side
`J4` silkscreen pin-1 orientation (paired with the broader Core
silkscreen gate in
[`s360-100-r4-core.md` §S360-100-BENCH-001 status](hardware/s360-100-r4-core.md#s360-100-bench-001-status));
Core-to-module 3-pin harness identity (conductor count, length,
key / polarity at both ends, conductor-by-conductor pin
mapping); `K1` BOM identity (part number, coil voltage, contact
configuration, contact current / voltage / AC vs DC rating,
isolation rating); whether the `Q1` MMBT3904 SOA is adequate for
the chosen `K1` coil-current draw; any bench / continuity /
waveform evidence against a populated `S360-310-R4` +
`S360-100-R4` pair; and the systemic `IO3` (Core schematic) vs
`GPIO4` ([`sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml)
line 61) vs `GPIO10`
([`sense360_core.yaml`](../packages/hardware/sense360_core.yaml)
line 63) `relay_pin` disagreement (resolution belongs to
`CORE-ABSTRACT-BUS-001`, alias for
[`release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups),
**not** to HW-PINMAP-310-FOLLOWUP).

This update does **not** edit
[`docs/hardware/schematics/S360-310-R4.pdf`](hardware/schematics/S360-310-R4.pdf)
(stays byte-identical to the HW-ASSETS-310 commit); does **not**
edit
[`docs/hardware/artifacts/S360-310-R4.md`](hardware/artifacts/S360-310-R4.md)
(its content is consumed by HW-PINMAP-310-FOLLOWUP, not
rewritten); does **not** edit any value in
[`config/hardware-catalog.json`](../config/hardware-catalog.json)
(`S360-310` row stays `schematic_status: cataloged_unverified`
with no `schematic_file`),
[`config/product-catalog.json`](../config/product-catalog.json),
[`config/webflash-builds.json`](../config/webflash-builds.json),
or [`config/webflash-compatibility.json`](../config/webflash-compatibility.json);
does **not** add or modify any product YAML under
[`products/`](../products/) or any WebFlash wrapper under
[`products/webflash/`](../products/webflash/); does **not** add
or modify any package YAML under [`packages/`](../packages/)
(including
[`packages/expansions/fan_relay.yaml`](../packages/expansions/fan_relay.yaml),
[`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml),
and
[`packages/hardware/sense360_core.yaml`](../packages/hardware/sense360_core.yaml));
does **not** edit any test under [`tests/`](../tests/), any
script under [`scripts/`](../scripts/), any workflow under
`.github/workflows/`, any component under `components/`, any
header under `include/`, `firmware/*`, `manifest.json`, or
`firmware/sources.json`; does **not** regenerate firmware,
create a GitHub Release or tag, or change any WebFlash manifest
/ import; does **not** advance `PACKAGE-RELAY-001`,
`PRODUCT-RELAY-001`, `WEBFLASH-RELAY-001`, `RELEASE-RELAY-001`,
`WF-IMPORT-RELAY-001`, or `CORE-ABSTRACT-BUS-001`; does **not**
close `S360-100-BENCH-001`, `HW-PINMAP-311-FOLLOWUP`,
`HW-PINMAP-312-FOLLOWUP`, `HW-PINMAP-320-FOLLOWUP`,
`HW-PINMAP-400-FOLLOWUP`, `HW-PINMAP-410-FOLLOWUP`, or
`COMPLIANCE-001`; does **not** unblock FanTRIAC (HW-005 stays a
separate gate); does **not** change the Release-One
configuration (`Ceiling-POE-VentIQ-RoomIQ`, version `1.0.0`,
channel `stable`, artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
`v1.0.0`); does **not** change the LED preview entry
(`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`,
`channel: preview`, artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`);
does **not** change the Sense360 LED Release-One exclusion; does
**not** relax or change the fan-driver `max-one-of` rule
(`FAN_DRIVER_TOKENS` in
[`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py));
does **not** resolve the Core J10 vs RoomIQ J6 pin-order open
question (HW-009 `needs-silkscreen/bench-verification`); does
**not** resolve the systemic Core abstract-bus mismatch
enumerated in
[`release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups);
and does **not** change the mains-voltage compliance status for
`S360-320` or `S360-400` (owned by COMPLIANCE-001); does **not**
claim that any bench / continuity / harness / silkscreen
evidence exists; does **not** claim that any compliance
evidence for a mains-switching FanRelay product exists.

**Next audit-log trigger.** The next HW-PINMAP-310-FOLLOWUP
audit-log row should appear when committed evidence is added to
this repository that the field-evidence rules above can cite:
operator-attributed silkscreen captures of the module-side `J2`
1-to-3 pin order, the module-side `J1` 1-to-3 pin order (with
NO / COM / NC labels if present), and the Core-side `J4` 1-to-3
pin order; physical 3-pin Core ↔ module harness inspection with
conductor-by-conductor pin mapping recorded; `K1` BOM identity
(part number, manufacturer, coil voltage, contact configuration,
contact current / voltage / AC vs DC rating, isolation rating);
oscilloscope or bench captures of the relay coil-drive waveform,
the `K1` switching behaviour, the load-side continuity through
`J1` NO / COM / NC contacts, or the `Q1` MMBT3904 SOA under the
actual coil-current draw, against a populated `S360-310-R4` +
`S360-100-R4` pair, with operator / reviewer identity and review
date recorded; a standalone schematic-backed reference doc (e.g.
a rewritten `docs/hardware/s360-310-r4-relay.md` or a companion
`docs/hardware/s360-310-r4-relay-reference.md` in the per-board
reference pattern of
[`s360-200-r4-roomiq.md`](hardware/s360-200-r4-roomiq.md) /
[`s360-211-r4-ventiq.md`](hardware/s360-211-r4-ventiq.md) /
[`s360-300-r4-led.md`](hardware/s360-300-r4-led.md)); KiCad
schematic source (`S360-310-R4.kicad_sch`) / KiCad PCB source
(`S360-310-R4.kicad_pcb`) / KiCad project metadata
(`*.kicad_pro` / `*.kicad_prl` / `fp-lib-table` /
`sym-lib-table`) / BOM / CPL / Gerbers / drill files / STEP / or
board images for `S360-310-R4` that the audit can cite by repo
path; or progress on the systemic Core abstract-bus rebind
(`CORE-ABSTRACT-BUS-001`, alias for
[`release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups)).
Until any of those land, the next audit-log entry should report
the same `partial — schematic evidence available; package
reconciliation pending` outcome with the new inspection date.

## PACKAGE-RELAY-001 update (deferred — CORE-ABSTRACT-BUS-001 / silkscreen / harness / K1 BOM evidence not landed)

PACKAGE-RELAY-001 is the **FanRelay package YAML reconciliation**
slice that would, when its readiness gates clear, reconcile
[`packages/expansions/fan_relay.yaml`](../packages/expansions/fan_relay.yaml)
and the Core abstract packages' `relay_pin` value(s) against the
verified Core schematic + module schematic + silkscreen / harness /
`K1` BOM evidence, and decide whether
`fan_relay_pin: ${relay_pin}` is the right abstraction or whether
the package should bind an explicit module-side connector pin.
PACKAGE-RELAY-001 was investigated in this PR against the
readiness gates recorded in
[`docs/hardware/package-readiness-matrix.md` `fan_relay.yaml` / S360-310](hardware/package-readiness-matrix.md#fan_relayyaml--s360-310),
[`docs/hardware/s360-310-r4-relay.md` Package YAML status](hardware/s360-310-r4-relay.md#package-yaml-status),
[`docs/hardware/s360-310-r4-relay.md` Required evidence before promotion](hardware/s360-310-r4-relay.md#required-evidence-before-promotion),
[`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
(HW-009 Release-One package-stack `relay_pin: GPIO4` bullet), and
[`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups),
and is **confirmed deferred**: every gate it depends on is still
open.

(1) `CORE-ABSTRACT-BUS-001` (alias for
[`release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups))
has not landed. The systemic `IO3` (Core schematic per
[`docs/hardware/s360-100-r4-core.md` §Pin assignments](hardware/s360-100-r4-core.md#pin-assignments)
line 100 — `IO3 → Relay (J4 Relay module gate)` — and
[`docs/hardware/s360-100-r4-core.md` §J4 — Relay module connector (3-pin)](hardware/s360-100-r4-core.md#j4--relay-module-connector-3-pin)
pin 2 — and
[`docs/hardware/s360-100-r4-core.md` §Fan / driver outputs](hardware/s360-100-r4-core.md#fan--driver-outputs)
line 276 — `Relay ↔ J4 Relay module (3-pin)` originating at ESP32
`IO3`) vs `GPIO4`
([`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml)
line 61 — `IO4` is `SEN0609_RX` per HW-009 in
[`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md))
vs `GPIO10`
([`packages/hardware/sense360_core.yaml`](../packages/hardware/sense360_core.yaml)
line 63) `relay_pin` disagreement is unresolved. Resolution belongs
to `CORE-ABSTRACT-BUS-001`, not to `PACKAGE-RELAY-001`. The Core
abstract-bus rebind is also broader than `relay_pin` alone: per
[`docs/hardware/firmware-package-mapping-audit.md` Release-One package stack](hardware/firmware-package-mapping-audit.md#release-one-product-yaml-package-stack)
and
[`docs/release-one-hardware-audit.md` Summary](release-one-hardware-audit.md#summary)
it must also re-anchor `halo_i2c`, `expansion_i2c`, `uart_bus`,
`status_led_pin`, `pir_sensor_pin`, and `expansion_gpio1` /
`expansion_gpio2` against the verified `S360-100-R4` schematic,
and must re-validate every non-Release-One product YAML that
consumes the Ceiling Core abstract package. That broader scope is
incompatible with a single relay-only PR.

(2) Module-side silkscreen / harness / `K1` BOM evidence is not
on file. Per
[`docs/hardware/s360-310-r4-relay.md` Known unresolved issues](hardware/s360-310-r4-relay.md#known-unresolved-issues):
no operator-attributed silkscreen reading of the module-side `J2`
1-to-3 pin order; no operator-attributed silkscreen reading of the
module-side `J1` 1-to-3 pin order or NO / COM / NC labelling; no
operator-attributed silkscreen reading of the Core-side `J4`
1-to-3 pin order (paired with the broader Core silkscreen gate in
[`docs/hardware/s360-100-r4-core.md` §S360-100-BENCH-001 status](hardware/s360-100-r4-core.md#s360-100-bench-001-status));
no physical Core ↔ module 3-pin harness inspection with
conductor-by-conductor mapping; no `K1` BOM identity (part number,
manufacturer, coil voltage, contact configuration SPST / SPDT,
contact current / voltage / AC vs DC rating, isolation rating); no
SOA analysis of the `Q1` MMBT3904 against the chosen `K1`
coil-current draw.

(3) No bench / continuity / waveform evidence exists. No populated
`S360-310-R4` board on a populated `S360-100-R4` Core has been
exercised with operator / reviewer / serial recorded; no
oscilloscope or bench capture of the relay coil-drive waveform,
the `K1` switching behaviour, or the load-side continuity through
`J1` NO / COM / NC contacts is on file.

(4) The `S360-310` JSON `schematic_status` stays
`cataloged_unverified` with no `schematic_file` set in
[`config/hardware-catalog.json`](../config/hardware-catalog.json)
(`S360-310` row lines 62–70). The separate JSON-only
`schematic_status` promotion PR for `S360-310` is itself gated on
silkscreen / harness / BOM evidence per
[`docs/hardware/s360-310-r4-relay.md` Follow-up PR sequence](hardware/s360-310-r4-relay.md#follow-up-pr-sequence)
and is not in scope here.

The package YAML
[`packages/expansions/fan_relay.yaml`](../packages/expansions/fan_relay.yaml)
itself is **already structurally correct** for the state of the
evidence: it binds the relay-drive signal as a single substitution
`fan_relay_pin: ${relay_pin}` (file line 27) that inherits
whichever value the parent Core abstract package binds; it carries
an override-hook comment block (lines 22–25) documenting how a
parent product YAML can drive an external SSR from an expansion
pin instead (`fan_relay_pin: ${expansion_gpio1}`); it exposes one
`switch.platform: gpio` with `pin: ${fan_relay_pin}` (line 38);
it preserves `restore_mode: RESTORE_DEFAULT_OFF`, `on_turn_on` /
`on_turn_off` log actions, the `fan_auto_mode` global (lines
50–53), and the `fan_emergency_stop` script (lines 58–65); and it
does **not** hardcode any GPIO. The wrong values live in the
**Core abstract packages**
([`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml)
`relay_pin: GPIO4` at line 61;
[`packages/hardware/sense360_core.yaml`](../packages/hardware/sense360_core.yaml)
`relay_pin: GPIO10` at line 63), and the resolution is owned by
`CORE-ABSTRACT-BUS-001`. **There is no safe functional package
YAML edit available today.** A definitive binding change on
`fan_relay.yaml` cannot be authored without picking a Core-side
GPIO, and that choice belongs to `CORE-ABSTRACT-BUS-001`. Because
PACKAGE-RELAY-001's named prerequisites — `CORE-ABSTRACT-BUS-001`
+ module-side silkscreen / harness / `K1` BOM evidence + bench /
continuity / waveform evidence — have not landed, the per-family
decision rule in
[`docs/hardware/package-readiness-matrix.md` `fan_relay.yaml` / S360-310](hardware/package-readiness-matrix.md#fan_relayyaml--s360-310)
forbids any functional package YAML edit in this PR. The update is
therefore **docs-only**: this section records the investigation
outcome and the deferral; the `fan_relay.yaml` / S360-310
subsection and the `PACKAGE-RELAY-001` Follow-up PR sequence row
in
[`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
are tightened to cross-link this entry; the **Package YAML
status** section in
[`docs/hardware/s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md)
gains a PACKAGE-RELAY-001 investigation-outcome paragraph; and the
HW-009 Release-One package-stack `relay_pin: GPIO4` bullet in
[`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
is tightened to record that PACKAGE-RELAY-001 did not edit
`fan_relay.yaml` because the package inherits `${relay_pin}` and
the Core abstract `relay_pin` variable remains the source of
conflict. No structural change is made anywhere else.

The package YAML
[`packages/expansions/fan_relay.yaml`](../packages/expansions/fan_relay.yaml)
is unchanged; the header (lines 1–17) describing the FanRelay
single-speed AC fan ON / OFF role and the cross-driver
non-interchangeability notice with `fan_pwm.yaml` /
`fan_gp8403.yaml` / `fan_triac.yaml`, the `substitutions` block
(lines 19–29) including `fan_relay_pin: ${relay_pin}` and
`fan_default_state: "OFF"`, the override-hook comment block (lines
22–25) showing `fan_relay_pin: ${expansion_gpio1}` as the
external-SSR override, the `switch.platform: gpio` declaration
(lines 34–44) with `id: fan_relay_switch`, `name: "${friendly_name}
Fan"`, `pin: ${fan_relay_pin}`, `icon: mdi:fan`,
`restore_mode: RESTORE_DEFAULT_OFF`, and `on_turn_on` /
`on_turn_off` log actions, the `fan_auto_mode` global declaration
(lines 49–53), and the `fan_emergency_stop` script (lines 58–65)
all remain in place. The Core abstract packages
[`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml)
(`relay_pin: GPIO4` line 61; ceiling-Core abstract) and
[`packages/hardware/sense360_core.yaml`](../packages/hardware/sense360_core.yaml)
(`relay_pin: GPIO10` line 63; generic Core abstract) are
unchanged. The sibling Core abstract packages
[`packages/hardware/sense360_core_voice_ceiling.yaml`](../packages/hardware/sense360_core_voice_ceiling.yaml),
[`packages/hardware/sense360_core_poe.yaml`](../packages/hardware/sense360_core_poe.yaml),
[`packages/hardware/sense360_core_mapping.yaml`](../packages/hardware/sense360_core_mapping.yaml),
and
[`packages/hardware/sense360_core_wall.yaml`](../packages/hardware/sense360_core_wall.yaml)
(which also bind `relay_pin` to `GPIO4` or `GPIO10`) are
unchanged. The `S360-310` row in
[`config/hardware-catalog.json`](../config/hardware-catalog.json)
(lines 62–70) stays `schematic_status: cataloged_unverified` with
no `schematic_file` set; no `FanRelay`-bearing entry is added to
[`config/product-catalog.json`](../config/product-catalog.json)
or
[`config/webflash-builds.json`](../config/webflash-builds.json);
the `FanRelay` token reservation in
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
`canonical_modules` (line 11) is unchanged and stays subject to
the fan-driver `max-one-of` rule enforced by `FAN_DRIVER_TOKENS`
in
[`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py).
No product YAML under [`products/`](../products/) is added or
modified — the legacy
[`products/sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml)
remains `legacy-compatible` and targets `S360-311` Sense360 PWM,
not `S360-310`; no `FanRelay`-bearing product YAML exists. No
WebFlash wrapper under [`products/webflash/`](../products/webflash/)
is added or modified. The Release-One YAML
[`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml)
and its WebFlash wrapper
[`products/webflash/ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml)
are unchanged; the LED preview product
[`products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq-led.yaml)
and its WebFlash wrapper
[`products/webflash/ceiling-poe-ventiq-roomiq-led.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq-led.yaml)
are unchanged; the blocked FanTRIAC reference
[`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml)
and its WebFlash wrapper are unchanged. Every exclusion is durable
and explicitly reaffirmed: **not** Release-One, **not**
`REQUIRED_CONFIGS`, **not** recommended, **not** kit / default,
**not** verified — irrespective of any future product YAML,
WebFlash wrapper, build, release, or import existence.

Documentation only and explicitly **does not**: edit
[`packages/expansions/fan_relay.yaml`](../packages/expansions/fan_relay.yaml)
(header, `substitutions` block, override-hook comment, `switch`
declaration, `fan_auto_mode` global, and `fan_emergency_stop`
script all preserved); edit
[`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml)
(`relay_pin: GPIO4` line 61 preserved);  edit
[`packages/hardware/sense360_core.yaml`](../packages/hardware/sense360_core.yaml)
(`relay_pin: GPIO10` line 63 preserved); edit any sibling Core
abstract package
([`packages/hardware/sense360_core_voice_ceiling.yaml`](../packages/hardware/sense360_core_voice_ceiling.yaml),
[`packages/hardware/sense360_core_poe.yaml`](../packages/hardware/sense360_core_poe.yaml),
[`packages/hardware/sense360_core_mapping.yaml`](../packages/hardware/sense360_core_mapping.yaml),
[`packages/hardware/sense360_core_wall.yaml`](../packages/hardware/sense360_core_wall.yaml));
edit any other package YAML under [`packages/`](../packages/);
drop the `fan_relay.yaml` line 12 comment text (`Built-in 10 A
relay on the Core board (GPIO4 by default).`) — the comment is
preserved verbatim because changing it requires either picking a
concrete GPIO (which belongs to `CORE-ABSTRACT-BUS-001`) or
removing the GPIO reference (a cosmetic Path B edit that this PR
deliberately does not make); edit
[`config/hardware-catalog.json`](../config/hardware-catalog.json),
[`config/product-catalog.json`](../config/product-catalog.json),
[`config/webflash-builds.json`](../config/webflash-builds.json),
or [`config/webflash-compatibility.json`](../config/webflash-compatibility.json);
edit any product YAML under [`products/`](../products/) (including
the Release-One, LED preview, blocked FanTRIAC reference, and
legacy four-channel PWM accessory entries); edit any WebFlash
wrapper under [`products/webflash/`](../products/webflash/); edit
any script under [`scripts/`](../scripts/); edit any test under
[`tests/`](../tests/); edit any workflow under
[`.github/workflows/`](../.github/workflows/); edit any component
under [`components/`](../components/); edit any header under
[`include/`](../include/); edit any firmware sources or manifests
([`firmware/sources.json`](../firmware/sources.json),
[`manifest.json`](../manifest.json)); edit the committed
module-side schematic PDF
[`docs/hardware/schematics/S360-310-R4.pdf`](hardware/schematics/S360-310-R4.pdf)
(byte-identical to the HW-ASSETS-310 commit); edit the curated
artifact index
[`docs/hardware/artifacts/S360-310-R4.md`](hardware/artifacts/S360-310-R4.md)
(its content is consumed by HW-PINMAP-310-FOLLOWUP and by this
investigation, not rewritten); edit
[`docs/product-readiness-matrix.md`](product-readiness-matrix.md),
[`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md),
or
[`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
(their existing FanRelay / S360-310 wording already enumerates
`PACKAGE-RELAY-001` as a future PR with the same prerequisites; no
"not investigated" stale wording exists to refresh — the
classifications stay `not-webflash-ready` and `not-release-ready`
respectively); add or modify any lifecycle enum value; add or
modify any `canonical_modules` token, any
`release_one_required_configs` membership, any build-matrix entry,
any `webflash_build_matrix` flip, any `artifact_name`, any release
tag, or any new channel; mark the pin map confirmed; mark
[`packages/expansions/fan_relay.yaml`](../packages/expansions/fan_relay.yaml)
`confirmed-ok`; promote `S360-310` to `preview` / `stable` /
`production`; add `FanRelay` to `release_one_required_configs` /
REQUIRED_CONFIGS; add FanRelay to any kit / default onboarding
flow; make FanRelay recommended; mark `S360-310` `verified`; add
or set `schematic_file` for `S360-310` in
[`config/hardware-catalog.json`](../config/hardware-catalog.json);
flip the `S360-310` JSON `schematic_status` from
`cataloged_unverified`; claim a `K1` relay part number, coil
voltage, contact configuration, or contact rating; claim a `J1`
NO / COM / NC mapping; claim that any bench / continuity /
waveform / silkscreen / harness evidence exists; claim that any
compliance evidence for a mains-switching FanRelay product exists;
generate firmware; create a GitHub Release or tag; perform a
WebFlash import; change the Release-One configuration
(`Ceiling-POE-VentIQ-RoomIQ`,
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
`v1.0.0`); change the LED preview path
(`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`,
`channel: preview`); unblock FanTRIAC
(`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`,
`blocker: HW-005`, `webflash_build_matrix: false`); change the
Sense360 LED Release-One exclusion; change the mains-voltage
compliance status for `S360-320` or `S360-400` (owned by
COMPLIANCE-001); resolve `HW-005`, `COMPLIANCE-001`,
`S360-100-BENCH-001`, `HW-PINMAP-311-FOLLOWUP`,
`HW-PINMAP-312-FOLLOWUP`, `HW-PINMAP-320-FOLLOWUP`,
`HW-PINMAP-400-FOLLOWUP`, `HW-PINMAP-410-FOLLOWUP`, or
`CORE-ABSTRACT-BUS-001`; advance `PRODUCT-RELAY-001`,
`WEBFLASH-RELAY-001`, `RELEASE-RELAY-001`, or
`WF-IMPORT-RELAY-001` (all stay blocked behind `PACKAGE-RELAY-001`);
or change the fan-driver `max-one-of` rule (`FAN_DRIVER_TOKENS`
in
[`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py)).
Adds no edits to
[`config/hardware-catalog.json`](../config/hardware-catalog.json),
[`config/product-catalog.json`](../config/product-catalog.json),
[`config/webflash-builds.json`](../config/webflash-builds.json),
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
[`products/*`](../products/),
[`products/webflash/*`](../products/webflash/),
[`packages/*`](../packages/), [`scripts/*`](../scripts/),
[`tests/*`](../tests/), [`.github/workflows/*`](../.github/workflows/),
[`components/*`](../components/), [`include/*`](../include/),
[`manifest.json`](../manifest.json), or
[`firmware/sources.json`](../firmware/sources.json).

The remaining chain after PACKAGE-RELAY-001 stays exactly as
recorded in
[`docs/hardware/package-readiness-matrix.md` Follow-up PR sequence](hardware/package-readiness-matrix.md#follow-up-pr-sequence)
and
[`docs/hardware/s360-310-r4-relay.md` Follow-up PR sequence](hardware/s360-310-r4-relay.md#follow-up-pr-sequence):
`CORE-ABSTRACT-BUS-001` (alias for
[`release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups))
+ silkscreen / harness / `K1` BOM evidence + bench / continuity /
waveform evidence → `S360-310` `schematic_status: verified`
(separate JSON-only PR) → `PACKAGE-RELAY-001` (this slice;
**deferred until those prerequisites land**) → `PRODUCT-RELAY-001`
(FanRelay product YAML under [`products/`](../products/); through
the [`docs/product-onboarding.md`](product-onboarding.md) ordered
safe sequence) → `WEBFLASH-RELAY-001` (FanRelay WebFlash wrapper +
catalog + build-matrix on a non-`stable` channel) →
`RELEASE-RELAY-001` (preview-artifact slice; alias:
`RELEASE-GAP-001` FanRelay slice) → `WF-IMPORT-RELAY-001`
(WebFlash-side import; alias: `WF-IMPORT-GAP-001` FanRelay slice).

Cross-linked from
[`docs/hardware/package-readiness-matrix.md` `fan_relay.yaml` / S360-310](hardware/package-readiness-matrix.md#fan_relayyaml--s360-310),
[`docs/hardware/package-readiness-matrix.md` Follow-up PR sequence `PACKAGE-RELAY-001` row](hardware/package-readiness-matrix.md#follow-up-pr-sequence),
[`docs/hardware/s360-310-r4-relay.md` Package YAML status](hardware/s360-310-r4-relay.md#package-yaml-status),
and
[`docs/hardware/firmware-package-mapping-audit.md` Release-One product YAML package stack](hardware/firmware-package-mapping-audit.md#release-one-product-yaml-package-stack)
(HW-009 `relay_pin: GPIO4` bullet).

Source of truth consumed:
[`docs/hardware/s360-310-r4-relay.md` Status](hardware/s360-310-r4-relay.md#status),
[`docs/hardware/s360-310-r4-relay.md` Reconciliation findings](hardware/s360-310-r4-relay.md#reconciliation-findings),
[`docs/hardware/s360-310-r4-relay.md` Existing package abstraction](hardware/s360-310-r4-relay.md#existing-package-abstraction),
[`docs/hardware/s360-310-r4-relay.md` Known unresolved issues](hardware/s360-310-r4-relay.md#known-unresolved-issues),
[`docs/hardware/s360-310-r4-relay.md` Required evidence before promotion](hardware/s360-310-r4-relay.md#required-evidence-before-promotion),
[`docs/hardware/s360-310-r4-relay.md` Follow-up PR sequence](hardware/s360-310-r4-relay.md#follow-up-pr-sequence),
[`docs/hardware/s360-310-r4-relay.md` HW-PINMAP-310-FOLLOWUP audit log](hardware/s360-310-r4-relay.md#hw-pinmap-310-followup-audit-log),
[`docs/hardware/s360-100-r4-core.md` §Pin assignments](hardware/s360-100-r4-core.md#pin-assignments),
[`docs/hardware/s360-100-r4-core.md` §J4 — Relay module connector (3-pin)](hardware/s360-100-r4-core.md#j4--relay-module-connector-3-pin),
[`docs/hardware/s360-100-r4-core.md` §Fan / driver outputs](hardware/s360-100-r4-core.md#fan--driver-outputs),
[`docs/hardware/s360-100-r4-core.md` §S360-100-BENCH-001 status](hardware/s360-100-r4-core.md#s360-100-bench-001-status),
[`docs/hardware/artifacts/S360-310-R4.md`](hardware/artifacts/S360-310-R4.md),
[`docs/hardware/schematics/S360-310-R4.pdf`](hardware/schematics/S360-310-R4.pdf),
[`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md),
[`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md),
[`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups),
[`packages/expansions/fan_relay.yaml`](../packages/expansions/fan_relay.yaml),
[`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml),
and
[`packages/hardware/sense360_core.yaml`](../packages/hardware/sense360_core.yaml),
together with the existing
[§HW-PINMAP-310-FOLLOWUP update](#hw-pinmap-310-followup-update-2026-05-18-schematic-backed-reconciliation),
[§PACKAGE-TRIAC-001 update](#package-triac-001-update-deferred--hw-005--hw-pinmap-320-followup--compliance-001-not-landed),
[§HW-PINMAP-311-FOLLOWUP update](#hw-pinmap-311-followup-update-2026-05-18-evidence-pass-investigation),
and
[§HW-PINMAP-312-FOLLOWUP update](#hw-pinmap-312-followup-update-2026-05-18-evidence-pass-investigation)
entries that this PR follows in pattern.

## CORE-ABSTRACT-BUS-001 update (2026-05-19 — docs-only audit + slice plan)

CORE-ABSTRACT-BUS-001 is the systemic rebind of the Core abstract
substitutions (`halo_i2c`, `expansion_i2c`, `uart_bus`, `relay_pin`,
`status_led_pin`, `pir_sensor_pin`, `expansion_gpio1` /
`expansion_gpio2`) in
[`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml)
and the sibling Core abstract packages
([`packages/hardware/sense360_core.yaml`](../packages/hardware/sense360_core.yaml),
[`packages/hardware/sense360_core_mapping.yaml`](../packages/hardware/sense360_core_mapping.yaml),
[`packages/hardware/sense360_core_poe.yaml`](../packages/hardware/sense360_core_poe.yaml),
[`packages/hardware/sense360_core_wall.yaml`](../packages/hardware/sense360_core_wall.yaml),
[`packages/hardware/sense360_core_ceiling_s3.yaml`](../packages/hardware/sense360_core_ceiling_s3.yaml))
against the verified `S360-100-R4` schematic captured in
[`docs/hardware/s360-100-r4-core.md`](hardware/s360-100-r4-core.md).
It is the alias for
[`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups)
and is named as the gating systemic blocker for `PACKAGE-RELAY-001`
([§PACKAGE-RELAY-001 update](#package-relay-001-update-deferred--core-abstract-bus-001--silkscreen--harness--k1-bom-evidence-not-landed)),
`PACKAGE-PWM-001`, `PACKAGE-DAC-001`, and the wider fan-driver chain
in
[`docs/hardware/package-readiness-matrix.md` Follow-up PR sequence](hardware/package-readiness-matrix.md#follow-up-pr-sequence).

CORE-ABSTRACT-BUS-001 was investigated in this PR against the
readiness gates recorded in
[`docs/hardware/package-readiness-matrix.md` `CORE-ABSTRACT-BUS-001` row](hardware/package-readiness-matrix.md#follow-up-pr-sequence)
(Core J10 vs RoomIQ J6 silkscreen verification via S360-100-BENCH-001
evidence + RoomIQ / AirIQ / VentIQ package rebind plan +
re-validation pass for every non-Release-One product YAML that
consumes the Ceiling Core abstract package) and is **confirmed
deferred at the implementation layer**, with the investigation
producing a docs-only audit / slice plan rather than any package YAML
edit. Every readiness gate it depends on is still open.

(1) `S360-100-BENCH-001` Core silkscreen evidence (Core `J4` 1-to-3
pin order, Core `J10` 1-to-12 pin order, RoomIQ `J6` 1-to-12 pin
order) has not been committed; the
[`docs/hardware/s360-100-r4-core.md` §S360-100-BENCH-001 status](hardware/s360-100-r4-core.md#s360-100-bench-001-status)
record stays `pending — bench/manufacturing evidence required` per
the most recent re-check in
[§S360-100-BENCH-001 update (2026-05-18)](#s360-100-bench-001-update-2026-05-18--evidence-pass-investigation)
(if present in this file) and per the inline re-check note in
[`docs/release-one-hardware-audit.md` Findings → Core / RoomIQ connector](release-one-hardware-audit.md#findings).

(2) The RoomIQ / AirIQ / VentIQ package rebind plan (rebinding
[`packages/expansions/comfort_ceiling.yaml`](../packages/expansions/comfort_ceiling.yaml),
[`packages/expansions/presence_ceiling.yaml`](../packages/expansions/presence_ceiling.yaml),
[`packages/expansions/airiq_bathroom_base.yaml`](../packages/expansions/airiq_bathroom_base.yaml),
[`packages/expansions/airiq_ceiling.yaml`](../packages/expansions/airiq_ceiling.yaml),
[`packages/expansions/airiq_wall.yaml`](../packages/expansions/airiq_wall.yaml),
and the matching feature profiles to the schematic-correct shared
I²C bus on `IO48` / `IO45` and the two radar UARTs `Hi-Link` on
`IO1` / `IO2` + `SEN0609` on `IO4` / `IO5`) has not been drafted.

(3) The re-validation pass for every non-Release-One product YAML
that consumes any affected Core abstract package — at minimum the
~30 product YAMLs enumerated in
[`docs/hardware/core-abstract-bus-reconciliation.md` Blast radius per Core package](hardware/core-abstract-bus-reconciliation.md#blast-radius-per-core-package)
— has not been designed.

(4) The GPIO3 collision between the schematic-correct
`relay_pin: GPIO3` (per
[`docs/hardware/s360-100-r4-core.md` §ESP32-S3 pin and net mapping](hardware/s360-100-r4-core.md#esp32-s3-pin-and-net-mapping)
line 100 — `IO3 → Relay (J4 Relay module gate)` — and §J4 Relay
module connector (3-pin) pin 2 — `Relay (drive signal from ESP32
IO3)`) and the existing
`comfort_ceiling_als_int_pin: GPIO3`
([`packages/expansions/comfort_ceiling.yaml`](../packages/expansions/comfort_ceiling.yaml)
line 42 — consumed by Release-One via
[`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml)
line 140) was first surfaced in this investigation. The same `GPIO3`
is also currently bound to `comfort_als_int_pin` in
[`packages/expansions/comfort_ceiling_s3.yaml`](../packages/expansions/comfort_ceiling_s3.yaml)
line 29 and
[`packages/hardware/sense360_core_ceiling_s3.yaml`](../packages/hardware/sense360_core_ceiling_s3.yaml)
line 140, to `expander_int_pin` in
[`packages/hardware/sense360_core_mapping.yaml`](../packages/hardware/sense360_core_mapping.yaml)
line 54, and to `sx1509_interrupt_pin` in
[`packages/expansions/gpio_expander_sx1509.yaml`](../packages/expansions/gpio_expander_sx1509.yaml)
line 17. These bindings are themselves schematic-conflicting (the
RoomIQ `ALS_INT` net is on `IO47` per
[`docs/hardware/s360-100-r4-core.md` §ESP32-S3 pin and net mapping](hardware/s360-100-r4-core.md#esp32-s3-pin-and-net-mapping)
line 109; the SX1509 `expander_int` net is on `IO17` per line 96) —
so resolving the collision requires moving every `GPIO3` consumer to
its schematic-correct net before the relay slice can use `GPIO3`.

(5) ESP32-S3 `GPIO3` is a strap pin (JTAG-select). The relay
module's `Q1` MMBT3904 NPN low-side topology recorded in
[`docs/hardware/artifacts/S360-310-R4.md`](hardware/artifacts/S360-310-R4.md)
suggests `RESTORE_DEFAULT_OFF` keeps the strap in a benign state at
boot, but no bench evidence against a populated `S360-310-R4` +
`S360-100-R4` pair has been committed to verify this; the
characterisation is recorded as an open gate in
[`docs/hardware/core-abstract-bus-reconciliation.md` Required evidence before any slice can land](hardware/core-abstract-bus-reconciliation.md#required-evidence-before-any-slice-can-land).

(6) No test today asserts Core-abstract-substitution values against
the schematic. The pattern to follow when the implementation slices
land is
[`tests/test_led_package_mapping.py`](../tests/test_led_package_mapping.py)
(HW-010); a proposed new file `tests/test_core_abstract_bus.py`
recorded in
[`docs/hardware/core-abstract-bus-reconciliation.md` Test scaffolding plan](hardware/core-abstract-bus-reconciliation.md#test-scaffolding-plan)
must land with the first implementation slice.

Because every readiness gate is open and the GPIO3 collision means
no single substitution can land safely on its own, the only
CORE-ABSTRACT-BUS-001 work recorded in this PR is the docs-only
audit / slice plan committed to
[`docs/hardware/core-abstract-bus-reconciliation.md`](hardware/core-abstract-bus-reconciliation.md),
together with the cross-link addenda in
[`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
(`fan_relay.yaml` row + Core abstract-bus row + Follow-up PR sequence
`CORE-ABSTRACT-BUS-001` row),
[`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
(Release-One product YAML package stack `relay_pin: GPIO4` bullet +
Systemic Core abstract-bus rebind recommended-follow-up entry), this
file, and
[`UPCOMING_PR.md`](../UPCOMING_PR.md) (queue split into
`CORE-ABSTRACT-BUS-001A` / `B` / `C`; `PRODUCT-RELAY-001` /
`PACKAGE-RELAY-001` / `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` /
`WF-IMPORT-RELAY-001` blocker references refined to cite
`CORE-ABSTRACT-BUS-001A` rather than generic `001`). The package
YAML files
[`packages/hardware/sense360_core.yaml`](../packages/hardware/sense360_core.yaml)
(`relay_pin: GPIO10` line 63),
[`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml)
(`relay_pin: GPIO4` line 61, `status_led_pin: GPIO48` line 76,
`pir_sensor_pin: GPIO47` line 77, `expansion_gpio1..4: GPIO5..GPIO8`
lines 65–68, `halo_i2c` on `GPIO39/40` lines 50–51, 105–110,
`expansion_i2c` on `GPIO21/18` lines 52–53, 113–117, `uart_bus` on
`GPIO1/2/256000` lines 56–58, 120–124),
[`packages/hardware/sense360_core_mapping.yaml`](../packages/hardware/sense360_core_mapping.yaml)
(`relay_pin: GPIO10` line 47, `expander_int_pin: GPIO3` line 54),
[`packages/hardware/sense360_core_poe.yaml`](../packages/hardware/sense360_core_poe.yaml)
(`relay_pin: GPIO10` line 76),
[`packages/hardware/sense360_core_wall.yaml`](../packages/hardware/sense360_core_wall.yaml)
(`relay_pin: GPIO4` line 65),
[`packages/hardware/sense360_core_ceiling_s3.yaml`](../packages/hardware/sense360_core_ceiling_s3.yaml)
(`comfort_als_int_pin: GPIO3` line 140),
[`packages/expansions/fan_relay.yaml`](../packages/expansions/fan_relay.yaml)
(`fan_relay_pin: ${relay_pin}` line 27 — already correctly
abstracted; the wrong values live in the parent Core packages, not
in this file),
[`packages/expansions/comfort_ceiling.yaml`](../packages/expansions/comfort_ceiling.yaml)
(`comfort_ceiling_als_int_pin: GPIO3` line 42),
[`packages/expansions/comfort_ceiling_s3.yaml`](../packages/expansions/comfort_ceiling_s3.yaml)
(`comfort_als_int_pin: GPIO3` line 29), and
[`packages/expansions/gpio_expander_sx1509.yaml`](../packages/expansions/gpio_expander_sx1509.yaml)
(`sx1509_interrupt_pin: GPIO3` line 17) all stay **byte-identical**
to their pre-PR state.

The `IO3` (Core schematic) vs `GPIO4` (Ceiling Core) vs `GPIO10`
(generic / Mapping / PoE Core) `relay_pin` resolution stays owned by
`CORE-ABSTRACT-BUS-001A` (the relay slice, depends on `001C`
landing first), not by this audit. The `halo_i2c` /
`expansion_i2c` / `i2c0` / `i2c1` / `i2c_primary` / `i2c_expander`
consolidation to the single shared I²C bus on `IO48` / `IO45` stays
owned by `CORE-ABSTRACT-BUS-001B`. The UART split, status LED
move, PIR rebind to `IO15`, ALS_INT rebind to `IO47`, and expansion
GPIO rebind stay owned by `CORE-ABSTRACT-BUS-001C`.

Documentation only. CORE-ABSTRACT-BUS-001 (this audit) does **not**
edit
[`config/hardware-catalog.json`](../config/hardware-catalog.json)
(`S360-100` stays `schematic_status: verified` per HW-008; `S360-310`
stays `cataloged_unverified`; `S360-311` / `S360-312` / `S360-320` /
`S360-400` / `S360-410` stay as recorded today),
[`config/product-catalog.json`](../config/product-catalog.json),
[`config/webflash-builds.json`](../config/webflash-builds.json),
or
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json);
does **not** edit any product YAML under
[`products/`](../products/) or any WebFlash wrapper under
[`products/webflash/`](../products/webflash/); does **not** edit any
package YAML under [`packages/`](../packages/) (no Core, no
expansion, no feature profile); does **not** edit any test under
[`tests/`](../tests/), any script under [`scripts/`](../scripts/),
any workflow under `.github/workflows/`, any component under
`components/`, any header under `include/`, `firmware/*`,
`manifest.json`, or `firmware/sources.json`; does **not** regenerate
firmware, create a GitHub Release or tag, or change any WebFlash
manifest / import; does **not** advance `PACKAGE-RELAY-001`,
`PRODUCT-RELAY-001`, `WEBFLASH-RELAY-001`, `RELEASE-RELAY-001`,
`WF-IMPORT-RELAY-001`, `PACKAGE-PWM-001`, `PRODUCT-PWM-001`,
`WEBFLASH-PWM-001`, `RELEASE-PWM-001`, `PACKAGE-DAC-001`,
`PRODUCT-DAC-001`, `WEBFLASH-DAC-001`, `RELEASE-DAC-001`,
`PACKAGE-TRIAC-001`, `PRODUCT-TRIAC-002`, `WF-TRIAC-001`,
`RELEASE-TRIAC-001`, or `WF-IMPORT-TRIAC-001`; does **not** close
`S360-100-BENCH-001`, `HW-PINMAP-310-FOLLOWUP`,
`HW-PINMAP-311-FOLLOWUP`, `HW-PINMAP-312-FOLLOWUP`,
`HW-PINMAP-320-FOLLOWUP`, `HW-PINMAP-400-FOLLOWUP`,
`HW-PINMAP-410-FOLLOWUP`, or `COMPLIANCE-001`; does **not** unblock
FanTRIAC (HW-005 stays a separate gate); does **not** change the
Release-One configuration (`Ceiling-POE-VentIQ-RoomIQ`, version
`1.0.0`, channel `stable`, artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
`v1.0.0`); does **not** change the LED preview entry
(`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`,
`channel: preview`, artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`); does
**not** change the Sense360 LED Release-One exclusion; does **not**
relax or change the fan-driver `max-one-of` rule
(`FAN_DRIVER_TOKENS` in
[`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py));
does **not** resolve the Core J10 vs RoomIQ J6 pin-order open
question (HW-009 `needs-silkscreen/bench-verification`); does
**not** itself resolve the systemic Core abstract-bus mismatch
enumerated in
[`release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups)
(it produces the implementation plan; the implementation PRs
`CORE-ABSTRACT-BUS-001A` / `B` / `C` perform the actual rebind);
does **not** change the mains-voltage compliance status for
`S360-320` or `S360-400` (owned by COMPLIANCE-001); does **not**
claim that any bench / silkscreen / harness / `K1` BOM evidence
exists; does **not** claim that any compliance evidence for a
mains-switching FanRelay product exists; does **not** characterise
ESP32-S3 `GPIO3` strap-pin boot behaviour (that characterisation is
itself an open gate for `CORE-ABSTRACT-BUS-001A`).

**Next audit-log trigger.** The next CORE-ABSTRACT-BUS-001
audit-log entry should appear when committed evidence is added to
this repository that one of the implementation slices can cite:
S360-100-BENCH-001 silkscreen captures of Core `J4` / `J10` and
RoomIQ `J6`; ESP32-S3 `GPIO3` strap-pin boot-behaviour bench
characterisation against a populated `S360-310-R4` + `S360-100-R4`
pair; a committed RoomIQ / AirIQ / VentIQ package rebind plan;
landing of `CORE-ABSTRACT-BUS-001C` (rebinding
`comfort_ceiling_als_int_pin: GPIO3 → GPIO47`,
`expander_int_pin: GPIO3 → GPIO17`,
`sx1509_interrupt_pin: GPIO3 → GPIO17`, and the UART / status LED /
PIR / expansion GPIO substitutions per
[`docs/hardware/core-abstract-bus-reconciliation.md`](hardware/core-abstract-bus-reconciliation.md));
landing of `CORE-ABSTRACT-BUS-001A` (`relay_pin → GPIO3` across the
Core abstract packages plus the new
`tests/test_core_abstract_bus.py` regression coverage); or landing
of `CORE-ABSTRACT-BUS-001B` (single shared I²C bus consolidation).
Until any of those land, the next audit-log entry should report the
same `docs-only audit + slice plan; implementation deferred` outcome
with the new inspection date.

Cross-linked from
[`docs/hardware/core-abstract-bus-reconciliation.md`](hardware/core-abstract-bus-reconciliation.md)
(See also section + audit log),
[`docs/hardware/package-readiness-matrix.md` Follow-up PR sequence `CORE-ABSTRACT-BUS-001` row](hardware/package-readiness-matrix.md#follow-up-pr-sequence),
[`docs/hardware/package-readiness-matrix.md` `fan_relay.yaml` / S360-310](hardware/package-readiness-matrix.md#fan_relayyaml--s360-310),
[`docs/hardware/firmware-package-mapping-audit.md` Release-One product YAML package stack](hardware/firmware-package-mapping-audit.md#release-one-product-yaml-package-stack)
(HW-009 systemic Core-vs-schematic mismatch bullet + `Systemic Core
abstract-bus rebind` recommended-follow-up entry), and
[`UPCOMING_PR.md`](../UPCOMING_PR.md) (queue split). Source of
truth consumed:
[`docs/hardware/s360-100-r4-core.md` §ESP32-S3 pin and net mapping](hardware/s360-100-r4-core.md#esp32-s3-pin-and-net-mapping),
[`docs/hardware/s360-100-r4-core.md` §J4 — Relay module connector (3-pin)](hardware/s360-100-r4-core.md#j4--relay-module-connector-3-pin),
[`docs/hardware/s360-100-r4-core.md` §S360-100-BENCH-001 status](hardware/s360-100-r4-core.md#s360-100-bench-001-status),
[`docs/hardware/s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md),
[`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)
(Findings + Required follow-ups #2 / #3),
[`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
(HW-009),
[`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
(PACKAGE-GAP-001),
[`packages/hardware/sense360_core.yaml`](../packages/hardware/sense360_core.yaml),
[`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml),
[`packages/hardware/sense360_core_ceiling_s3.yaml`](../packages/hardware/sense360_core_ceiling_s3.yaml),
[`packages/hardware/sense360_core_mapping.yaml`](../packages/hardware/sense360_core_mapping.yaml),
[`packages/hardware/sense360_core_poe.yaml`](../packages/hardware/sense360_core_poe.yaml),
[`packages/hardware/sense360_core_wall.yaml`](../packages/hardware/sense360_core_wall.yaml),
[`packages/expansions/fan_relay.yaml`](../packages/expansions/fan_relay.yaml),
[`packages/expansions/comfort_ceiling.yaml`](../packages/expansions/comfort_ceiling.yaml),
[`packages/expansions/comfort_ceiling_s3.yaml`](../packages/expansions/comfort_ceiling_s3.yaml),
[`packages/expansions/gpio_expander_sx1509.yaml`](../packages/expansions/gpio_expander_sx1509.yaml),
and
[`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml),
together with the existing
[§HW-PINMAP-310-FOLLOWUP update](#hw-pinmap-310-followup-update-2026-05-18-schematic-backed-reconciliation)
and
[§PACKAGE-RELAY-001 update](#package-relay-001-update-deferred--core-abstract-bus-001--silkscreen--harness--k1-bom-evidence-not-landed)
entries that this PR follows in pattern.

## HW-PINMAP-400-FOLLOWUP update (2026-05-19 — schematic-backed reconciliation)

HW-PINMAP-400-FOLLOWUP is the **docs-only schematic-backed
reconciliation** that consumes the module-side schematic evidence
committed under HW-ASSETS-400 (PR #514) at
[`docs/hardware/schematics/S360-400-R4.pdf`](hardware/schematics/S360-400-R4.pdf)
and inventoried in
[`docs/hardware/artifacts/S360-400-R4.md`](hardware/artifacts/S360-400-R4.md),
and uses that evidence to promote the HW-PINMAP-400 audit doc at
[`docs/hardware/s360-400-r4-power.md`](hardware/s360-400-r4-power.md)
from `pending — schematic/design evidence required` to
`partial — schematic evidence available; package reconciliation,
BOM, silkscreen, creepage/clearance, and COMPLIANCE-001 pending`.
The purpose of this update is to record, on 2026-05-19, what
schematic-backed reconciliation work HW-PINMAP-400-FOLLOWUP
performed against the PWR-240V pin-map / connector / protection-
topology / converter-identity / package gates owed by
HW-PINMAP-400, and what stays unresolved after the FOLLOWUP — and
to record the result as a dated audit-log entry in
[`docs/hardware/s360-400-r4-power.md` HW-PINMAP-400-FOLLOWUP audit log](hardware/s360-400-r4-power.md#hw-pinmap-400-followup-audit-log).
**The status is `partial — schematic evidence available; package
reconciliation, BOM, silkscreen, creepage/clearance, and
COMPLIANCE-001 pending`** after this update (promoted from the
prior `pending — schematic/design evidence required`). Schematic-
backed module-side `J1` 3-pin AC input is recorded (`LIVE` /
`NEUTRAL` / `Earth_Protective`); mains-input protection network is
recorded at the topology layer (`F1 A250-1200` polyfuse on LIVE;
`RV1 10D391K` MOV across the AC line; `C1 470nF` X-cap across the
AC line in parallel with `RV1`); AC/DC converter is recorded
(`PS1 = HLK-10M05` with pinout `AC(L)` / `AC(N)` / `-VO` / `+VO`);
output filter bank is recorded (`C5 100uF` / `C6 10u` / `C7 100n`
/ `C8 100uF` between `+VO` and `-VO` / `GND`); module-side `J2`
2-pin output is recorded (`+5VP` / `GND`); four mounting holes
`H1`..`H4` are recorded at the symbol layer; absences (no Y-caps,
no CM/DM line-filter inductor, no secondary regulator, no on-board
LED, no thermal cutout, no GPIO) are recorded. **No BOM evidence,
no silkscreen evidence, no PCB / creepage / clearance evidence,
no bench / load / thermal / inrush / EMI / EMC evidence, and no
COMPLIANCE-001 sign-off** is on file. The three-way AC/DC
part-identity disagreement (catalog `HLK-5M05` vs package header
`HLK-PM01 or similar` vs schematic `HLK-10M05`) is **not**
resolved (resolution belongs to `PACKAGE-POWER-400-001` after BOM
lands, not HW-PINMAP-400-FOLLOWUP). `PACKAGE-POWER-400-001` stays
blocked behind BOM cross-check + the `S360-400`
`schematic_status: verified` JSON PR + `COMPLIANCE-001` sign-off.
The downstream PWR-240V chain (`PRODUCT-POWER-400-001`,
`WEBFLASH-POWER-400-001`, `RELEASE-POWER-400-001`,
`WF-IMPORT-POWER-400-001`) stays blocked. Release-One is
unchanged. The LED preview path is unchanged. FanTRIAC stays
`status: blocked`. The Sense360 LED Release-One exclusion is
unchanged. COMPLIANCE-001 status for `S360-320` / `S360-400` is
unchanged (last re-check PR #506).

**Why this is the next actionable evidence item.** After
HW-ASSETS-400 (PR #514) merged and committed the
`S360-400-R4.pdf` schematic plus the curated artifact index, the
HW-PINMAP-400 audit doc still carried the historical
`pending — schematic/design evidence required` status text;
[`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
and downstream readiness matrices likewise read as if no
schematic-backed reconciliation had been performed.
HW-PINMAP-400-FOLLOWUP closes that documentation gap by consuming
the committed schematic, producing the schematic-backed
reconciliation view, and recording the remaining BOM / silkscreen
/ PCB / creepage / clearance / bench / EMI / compliance evidence
gaps in the per-board audit doc and across the downstream
readiness matrices.

**Scope.** Documentation only and cross-link only. Specifically
this update:

- Promotes [`docs/hardware/s360-400-r4-power.md`](hardware/s360-400-r4-power.md)
  from `pending — schematic/design evidence required` to
  `partial — schematic evidence available; package reconciliation,
  BOM, silkscreen, creepage/clearance, and COMPLIANCE-001
  pending`. Rewrites the audit doc body to add the new schematic-
  backed sections (Schematic summary; Connector / pin-map
  findings; Protection / power topology findings; AC/DC converter
  findings; Part identity reconciliation; Existing package
  abstraction; Reconciliation findings; Known unresolved issues;
  Required evidence before promotion; Follow-up PR sequence) in
  the per-audit pattern used by
  [`s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md) /
  [`s360-311-r4-pwm.md`](hardware/s360-311-r4-pwm.md) /
  [`s360-312-r4-dac.md`](hardware/s360-312-r4-dac.md) /
  [`s360-320-r4-triac.md`](hardware/s360-320-r4-triac.md), and
  appends an `HW-PINMAP-400-FOLLOWUP audit log` section that
  carries the 2026-05-19 dated entry.
- Refreshes the cross-link wording in
  [`UPCOMING_PR.md`](../UPCOMING_PR.md): adds `HW-ASSETS-400 →
  PR #514` to the Completed / merged PRs table; removes
  `HW-ASSETS-400` from the active queue (item 4) and promotes
  `HW-PINMAP-400-FOLLOWUP` to the in-flight slot; renumbers items
  5–35 accordingly; refreshes the Current queue summary bullets
  and the Recently uploaded evidence section to past-tense the
  S360-400-R4.pdf entry.
- Refreshes the cross-link wording in
  [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
  (`S360-400` hardware-evidence row, `S360-400` productization
  row, and §`S360-400` Sense360 240v PSU board-by-board notes) so
  the audit-doc status reads `partial — schematic evidence
  available; package reconciliation, BOM, silkscreen,
  creepage/clearance, and COMPLIANCE-001 pending` instead of the
  pre-FOLLOWUP `pending — schematic/design evidence required`.
- Refreshes the cross-link wording in
  [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md)
  (Sense360 240v PSU (`S360-400`) row and audit-doc subsection)
  for the same reason.
- Refreshes the cross-link wording in
  [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
  (`power_240v.yaml` row + §`power_240v.yaml` / S360-400 detail)
  so the audit-doc status reads `partial — schematic evidence
  available; package reconciliation, BOM, silkscreen,
  creepage/clearance, and COMPLIANCE-001 pending` and the
  allowed-action cell records that HW-PINMAP-400-FOLLOWUP has
  landed but `PACKAGE-POWER-400-001` stays blocked behind BOM +
  the `S360-400` `schematic_status: verified` JSON PR + the
  `COMPLIANCE-001` sign-off.
- Refreshes the cross-link wording in
  [`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
  with a new `power_240v.yaml` AC/DC part-identity disagreement
  (S360-400) per-area finding that cites the committed PDF, the
  curated artifact index, the three-way disagreement, and the
  package YAML's preserved status.
- Refreshes the cross-link wording in
  [`docs/product-readiness-matrix.md`](product-readiness-matrix.md)
  (`Ceiling-PWR-{AIR}-{ROOM}` PWR-240V row and §`PWR-240V /
  S360-400` subsection) so the descriptive narrative reflects the
  post-HW-ASSETS-400 / post-HW-PINMAP-400-FOLLOWUP state — without
  changing any readiness class.
- Refreshes the cross-link wording in
  [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md)
  (`PWR-240V / S360-400` exposure-table row and §`Power /
  S360-400 WebFlash posture` subsection) so the descriptive
  narrative stops saying "no committed module-side schematic
  PDF" / "no curated artifact index" / "audit-stub at status
  pending" and reflects the post-HW-ASSETS-400 / post-HW-PINMAP-
  400-FOLLOWUP state — without changing any exposure class.
- Refreshes the cross-link wording in
  [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
  (`PWR-240V / S360-400` release-table row and §`Power /
  S360-400 release posture` subsection) so the descriptive
  narrative reflects the post-HW-ASSETS-400 / post-HW-PINMAP-
  400-FOLLOWUP state — without changing any release class.
- Refreshes the inventory entry for
  [`docs/hardware/s360-400-r4-power.md`](hardware/s360-400-r4-power.md)
  in this cleanup audit's [§Findings summary](#findings-summary)
  table to record the promoted status and the schematic-backed
  reconciliation content; refreshes the
  `(HW-PINMAP-400, pending)` mentions to
  `(HW-PINMAP-400, partial)`.

**Files inspected.**
[`docs/hardware/schematics/S360-400-R4.pdf`](hardware/schematics/S360-400-R4.pdf)
(HW-ASSETS-400 / PR #514 module-side schematic, byte-identical
to upload; SHA256
`295e3ec9192603fd4ca7d89b8cda68777e5cb8e9713ed8b0fba2316babb0e765`;
461,206 bytes);
[`docs/hardware/artifacts/S360-400-R4.md`](hardware/artifacts/S360-400-R4.md)
(HW-ASSETS-400 / PR #514 curated artifact index — uploaded
inventory, schematic content capture, retained-but-not-committed
list, artifact-side Open Questions);
[`docs/hardware/s360-400-r4-power.md`](hardware/s360-400-r4-power.md)
(rewritten by this update — §Status, §Purpose and scope, §Board
identity, §Repository evidence, §Schematic summary, §Connector /
pin-map findings, §Protection / power topology findings, §AC/DC
converter findings, §Part identity reconciliation, §Existing
package abstraction, §Reconciliation findings, §Known unresolved
issues, §Package YAML status, §Product / WebFlash status,
§Compliance / safety status, §Required evidence before
promotion, §Follow-up PR sequence, §Do-not-change guardrails,
§See also, §HW-PINMAP-400-FOLLOWUP audit log);
[`packages/hardware/power_240v.yaml`](../packages/hardware/power_240v.yaml)
(header comments at lines 1–26 documenting the `HLK-PM01 or
similar` AC-DC part hint, `100-240V AC, 50/60Hz` input, `5V DC,
2A (10W)` output, `3000VAC` isolation, `Overcurrent, overvoltage,
short-circuit` protection, and recommended `1A` AC-input fusing;
`substitutions: power_source: "240v_ac"` at line 29; globals
`power_source_type` at lines 32–36; template diagnostic sensors
`Supply Voltage` / `Power Source` / `Power Configuration` /
`AC Power Connected`; logger config; **not edited by this PR**);
[`config/hardware-catalog.json`](../config/hardware-catalog.json)
`S360-400` row lines 102–110 (`group: Power`, `type: PSU`,
`friendly_name: Sense360 240v PSU`, `sku: S360-400`, `rev: R4`,
`old_name: PWR Module`, `description: Mains to 5V using
HLK-5M05.`, `schematic_status: cataloged_unverified`, no
`schematic_file`);
[`config/product-catalog.json`](../config/product-catalog.json)
(no active `PWR`-bearing entry; the four `legacy-compatible`
`*-pwr` Core variants `sense360-core-c-pwr.yaml` /
`sense360-core-w-pwr.yaml` / `sense360-core-v-c-pwr.yaml` /
`sense360-core-v-w-pwr.yaml` stay `legacy-compatible` and
`webflash_build_matrix: false`; the two shipping entries are
`Ceiling-POE-VentIQ-RoomIQ` `status: production` /
`channel: stable` and `Ceiling-POE-VentIQ-RoomIQ-LED`
`status: preview` / `channel: preview`;
`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked` /
`blocker: HW-005` / `webflash_build_matrix: false`);
[`config/webflash-builds.json`](../config/webflash-builds.json)
(no `PWR`-bearing build; only `Ceiling-POE-VentIQ-RoomIQ`
stable and `Ceiling-POE-VentIQ-RoomIQ-LED` preview);
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
(`PWR` reserved in `canonical_power`, no
`webflash_build_matrix: true` entry consumes it today);
[`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
`S360-400` hardware-evidence and productization-axis rows + §
[`S360-400` Sense360 240v PSU](hardware/board-readiness-matrix.md#s360-400-sense360-240v-psu)
board-by-board notes;
[`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
`power_240v.yaml` row + §
[`power_240v.yaml` / S360-400](hardware/package-readiness-matrix.md#power_240vyaml--s360-400)
detail;
[`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
new `power_240v.yaml` AC/DC part-identity disagreement
(S360-400) per-area finding;
[`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md)
§[Sense360 240v PSU (`S360-400`)](hardware/remaining-board-documentation-audit.md#sense360-240v-psu-s360-400);
[`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md)
`S360-400` snapshot row (`cataloged-unverified` +
`design-pending` + `compliance-gated` — unchanged by this
update; class assignments stay the same);
[`docs/product-readiness-matrix.md`](product-readiness-matrix.md)
§[PWR-240V / S360-400](product-readiness-matrix.md#pwr-240v--s360-400);
[`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md)
§[Power / S360-400 WebFlash posture](webflash-exposure-readiness-matrix.md#power--s360-400-webflash-posture);
[`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
§[Power / S360-400 release posture](release-artifact-readiness-matrix.md#power--s360-400-release-posture);
[`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
(COMPLIANCE-001 mains-voltage tracker — **unchanged**; applies
to `S360-320` / `S360-400`; last re-check PR #506);
[`UPCOMING_PR.md`](../UPCOMING_PR.md) (Completed / merged PRs row
added for HW-ASSETS-400 / PR #514; active-queue HW-ASSETS-400
row removed; HW-PINMAP-400-FOLLOWUP promoted to in-flight;
items 5–35 renumbered; Current queue summary bullets refreshed;
Recently uploaded evidence section refreshed to past-tense the
S360-400-R4.pdf entry).

**Outcome.** **Status promoted to `partial — schematic evidence
available; package reconciliation, BOM, silkscreen,
creepage/clearance, and COMPLIANCE-001 pending`** in
[`docs/hardware/s360-400-r4-power.md`](hardware/s360-400-r4-power.md).
HW-PINMAP-400-FOLLOWUP consumed the HW-ASSETS-400 / PR #514
schematic and produced the schematic-backed reconciliation view:
module-side `J1` 3-pin AC input (`LIVE` / `NEUTRAL` /
`Earth_Protective`) is schematic-backed; mains-input protection
network (`F1 A250-1200` polyfuse on LIVE; `RV1 10D391K` MOV
across the AC line; `C1 470nF` X-cap across the AC line in
parallel with `RV1`) is schematic-backed at the topology layer
(per-component ratings BOM-bound); AC/DC converter reference
(`PS1 = HLK-10M05` with pinout `AC(L)` / `AC(N)` / `-VO` /
`+VO`) is schematic-confirmed at the value-field / pinout layer
(manufacturer / part-revision BOM-bound); output filter bank
(`C5 100uF` / `C6 10u` / `C7 100n` / `C8 100uF` between `+VO`
and `-VO` / `GND`) is schematic-backed at the topology layer
(per-component ratings BOM-bound); module-side `J2` 2-pin output
(`+5VP` / `GND`) is schematic-backed; mounting holes `H1`..`H4`
are schematic-confirmed at the symbol layer (electrical bonding
unknown); absences (no Y-caps, no CM/DM line-filter inductor,
no secondary regulator, no on-board LED, no thermal cutout, no
NTC, no I²C / UART / SPI / DAC / GPIO) are schematic-confirmed.
**The following stay unresolved:** three-way AC/DC part-identity
disagreement (catalog `HLK-5M05` vs package header `HLK-PM01 or
similar` vs schematic `HLK-10M05`); `J1` and `J2` silkscreen
pin-1 orientation; `J1` and `J2` connector identity / current /
voltage / approval rating; `F1 A250-1200` polyfuse hold / trip /
voltage rating; `RV1 10D391K` clamp voltage / energy rating;
`C1 470nF` X-cap safety class X1 / X2; `C5..C8` voltage /
dielectric / ESR; creepage / clearance distances between AC LINE
/ NEUTRAL, `Earth_Protective`, and secondary `+5VP` / `GND`;
Y-class capacitor presence-or-absence as designed; common-mode /
differential-mode line-filter inductor absence as designed;
integrated thermal protection in the `HLK-10M05` module;
mounting-hole electrical bonding to `Earth_Protective` or a
chassis-bond plane; thermal rise under continuous load; inrush
current at cold-start; load regulation; insulation resistance;
Hi-pot; earth-continuity; leakage current; EMI / EMC conducted /
radiated emissions and immunity; the Core integration path
(`+5VP` ↔ Core `+5V` rail through `Q2 Si2319CDS` ideal-diode-OR,
through USB-C `VBUS`, or through a distinct path); harness
identity if any cable is part of the assembly;
**`COMPLIANCE-001` mains-voltage UK / EU sign-off** (last
re-check PR #506; status remains open).

This update does **not** edit
[`docs/hardware/schematics/S360-400-R4.pdf`](hardware/schematics/S360-400-R4.pdf)
(stays byte-identical to the HW-ASSETS-400 / PR #514 commit);
does **not** edit
[`docs/hardware/artifacts/S360-400-R4.md`](hardware/artifacts/S360-400-R4.md)
(its content is consumed by HW-PINMAP-400-FOLLOWUP, not
rewritten); does **not** edit
[`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
(COMPLIANCE-001 mains-voltage tracker unchanged); does **not**
edit any value in
[`config/hardware-catalog.json`](../config/hardware-catalog.json)
(`S360-400` row stays `schematic_status: cataloged_unverified`
with no `schematic_file`),
[`config/product-catalog.json`](../config/product-catalog.json),
[`config/webflash-builds.json`](../config/webflash-builds.json),
or
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json);
does **not** add or modify any product YAML under
[`products/`](../products/) or any WebFlash wrapper under
[`products/webflash/`](../products/webflash/); does **not** add
or modify any package YAML under [`packages/`](../packages/)
(including
[`packages/hardware/power_240v.yaml`](../packages/hardware/power_240v.yaml)
— comment-only cleanup of the stale `HLK-PM01 or similar`
header is **deferred to `PACKAGE-POWER-400-001`** once BOM
evidence lands, per the brief's evidence standards "BOM is
required to resolve part number/rating disputes"); does **not**
edit any test under [`tests/`](../tests/), any script under
[`scripts/`](../scripts/), any workflow under
`.github/workflows/`, any component under `components/`, any
header under `include/`, `firmware/*`, `manifest.json`, or
`firmware/sources.json`; does **not** regenerate firmware,
create a GitHub Release or tag, or change any WebFlash manifest
/ import; does **not** advance `PACKAGE-POWER-400-001`,
`PRODUCT-POWER-400-001`, `WEBFLASH-POWER-400-001`,
`RELEASE-POWER-400-001`, `WF-IMPORT-POWER-400-001`, or
`COMPLIANCE-001`; does **not** close `S360-100-BENCH-001`,
`HW-PINMAP-311-FOLLOWUP`, `HW-PINMAP-312-FOLLOWUP`,
`HW-PINMAP-320-FOLLOWUP`, `HW-PINMAP-310-FOLLOWUP`,
`HW-PINMAP-410-FOLLOWUP`, or `CORE-ABSTRACT-BUS-001`; does
**not** unblock FanTRIAC (HW-005 stays a separate gate); does
**not** change the Release-One configuration
(`Ceiling-POE-VentIQ-RoomIQ`, version `1.0.0`, channel
`stable`, artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
`v1.0.0`); does **not** change the LED preview entry
(`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`,
`channel: preview`, artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`);
does **not** change FanTRIAC state
(`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`,
`blocker: HW-005`, `webflash_build_matrix: false`); does
**not** change `REQUIRED_CONFIGS`, kits, or any WebFlash-side
artifact; does **not** change the `S360-410` Sense360 PoE PSU
status or its documented "schematic verification pending"
caveat; does **not** resolve the systemic Core abstract-bus
mismatch enumerated in
[`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups);
does **not** claim that any bench / load / thermal / inrush /
insulation / Hi-pot / earth-continuity / leakage / EMI / EMC
evidence exists; does **not** claim that any compliance evidence
for a mains-voltage `PWR`-bearing product exists; does **not**
make any CE / UKCA / FCC / UL / LVD / EMC / RoHS / IEC claim.

**Next audit-log trigger.** The next HW-PINMAP-400-FOLLOWUP
audit-log entry should appear when committed evidence is added
to this repository that the field-evidence rules above can cite:
a BOM line item with manufacturer + part number + revision for
`PS1` (settling the three-way `HLK-5M05` / `HLK-PM01 or similar`
/ `HLK-10M05` disagreement); BOM lines for `F1` / `RV1` / `C1`
/ `C5..C8` / `J1` / `J2` with ratings; operator-attributed
silkscreen captures of the module-side `J1` 1-to-3 pin order
and the module-side `J2` 1-to-2 pin order; KiCad PCB source /
gerbers / board photos sufficient to measure creepage /
clearance between the AC LINE / NEUTRAL / `Earth_Protective` /
secondary `+5VP` / `GND` nets; bench / load / thermal / inrush
/ insulation resistance / Hi-pot / earth-continuity / leakage /
EMI / EMC measurements against a populated `S360-400-R4` board
with operator / reviewer / serial recorded; a standalone
schematic-backed reference doc (e.g. a rewritten
`docs/hardware/s360-400-r4-power.md` in the per-board reference
pattern of
[`s360-200-r4-roomiq.md`](hardware/s360-200-r4-roomiq.md) /
[`s360-211-r4-ventiq.md`](hardware/s360-211-r4-ventiq.md) /
[`s360-300-r4-led.md`](hardware/s360-300-r4-led.md), or a
companion `docs/hardware/s360-400-r4-power-reference.md`); KiCad
schematic source (`S360-400-R4.kicad_sch`) / KiCad PCB source
(`S360-400-R4.kicad_pcb`) / KiCad project metadata
(`*.kicad_pro` / `*.kicad_prl` / `fp-lib-table` /
`sym-lib-table`) / CPL / drill files / STEP for `S360-400-R4`
that the audit can cite by repo path; compliance test reports
(LVD / EMC / RoHS / CE / UKCA / FCC / UL); or any documented
`COMPLIANCE-001` mains-voltage UK / EU sign-off for `S360-400`.
Until any of those land, the next audit-log entry should report
the same `partial — schematic evidence available; package
reconciliation, BOM, silkscreen, creepage/clearance, and
COMPLIANCE-001 pending` outcome with the new inspection date.

This update is recorded together with the existing
[§HW-PINMAP-310-FOLLOWUP update](#hw-pinmap-310-followup-update-2026-05-18-schematic-backed-reconciliation)
entry that this PR follows in pattern.

## HW-PINMAP-410-FOLLOWUP update (2026-05-19 — schematic-backed reconciliation)

HW-PINMAP-410-FOLLOWUP is the **docs-only schematic-backed
reconciliation** that consumes the module-side schematic evidence
committed under HW-ASSETS-410 (PR #516) at
[`docs/hardware/schematics/S360-410-R4.pdf`](hardware/schematics/S360-410-R4.pdf)
and inventoried in
[`docs/hardware/artifacts/S360-410-R4.md`](hardware/artifacts/S360-410-R4.md),
and uses that evidence to promote the HW-PINMAP-410 audit doc at
[`docs/hardware/s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md)
from `pending — schematic/design evidence required` to
`partial — schematic evidence available; package reconciliation,
PoE PD controller / magnetics / buck / isolated DC/DC / harness
identity evidence pending`. The purpose of this update is to
record, on 2026-05-19, what schematic-backed reconciliation work
HW-PINMAP-410-FOLLOWUP performed against the PoE-410 pin-map /
connector / PoE-controller / magnetics / buck / isolated-DC/DC /
output / mounting-hole / package-header part-identity gates owed
by HW-PINMAP-410, and what stays unresolved after the FOLLOWUP —
and to record the result as a dated audit-log entry in
[`docs/hardware/s360-410-r4-poe.md` HW-PINMAP-410-FOLLOWUP audit log](hardware/s360-410-r4-poe.md#hw-pinmap-410-followup-audit-log).
**The status is `partial — schematic evidence available; package
reconciliation, PoE PD controller / magnetics / buck / isolated
DC/DC / harness identity evidence pending`** after this update
(promoted from the prior `pending — schematic/design evidence
required`). Schematic-backed module-side `LAN_CON1
RJP-003TC1(LPJ4112CNL)` integrated 10/100 BASE-TX magnetics / RJ45
module with Bob-Smith bridge (`2x1000pF/2KV` + `2x75 Ω` + `C3 1nF`
shield bridge) is recorded; `U1 TPS2378DDAR(HSOIC-8)` PoE PD
controller with `R1 24.9k` DEN / `R2 1.27k` CLS (`Class=0 (0.44 to
12.95W)`) / `D1 SMAJ58A` TVS / `C2 15uF` CBULK / `R5 0.03R` RTN
sense is recorded; `U2 TX4138(ESOIC-8)` buck with `R3/R4 9.1k`
ILIM / `L1 33uH` / `D2 ss510` Schottky / `C6 470u` output bulk /
`R7 10.5k` (Rd) / `R8 56.2k` (Rc) feedback divider with on-sheet
formula `Vout = 0.8 · (1 + Rc/Rd)` ≈ 5.08 V design set-point on
`Sw_Vin_Poe` is recorded; `DCDC1 F0505S-2WR2(SIP-7)` isolated
DC/DC with `AM1D-0505S-NZ` annotated alternate (5 V → 5 V;
pinout `Vin+` / `Vin-` / `Vout-` / `Vout+`) is recorded;
module-side `J3` 2-pin output (`+5VP` / `GND`; `C8 22u` bulk,
`R9 1k` bleed) is recorded; `D3 Green` status LED on buck output
is recorded; four mounting holes `H1`..`H4` each labelled `Earth`
are recorded at the symbol layer; absences (no on-board
PoE-present LED on primary, no spare-pair vs data-pair selection,
no explicit 802.3at signature network, no secondary regulator
after isolation, no I²C / UART / SPI / GPIO / JTAG / Nextion, no
Core-side mating connector pinout) are recorded. **No BOM
evidence, no silkscreen evidence, no PCB / isolation-barrier
evidence, no bench / load / PoE-link-up / thermal / inrush /
insulation / Hi-pot / earth-continuity / leakage / EMI / EMC
evidence, and no HW-002 OQ#6 / `S360-100-BENCH-001` J2-harness
closure** is on file. The **part-identity disagreement** between
the package header in
[`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml)
line 6 (`Ag9712M, Silvertel Ag9700, or similar` — whole-module
hint) and the schematic-shown discrete topology
(`TPS2378DDAR + TX4138 + F0505S-2WR2 + RJP-003TC1(LPJ4112CNL)`) is
**not** resolved — BOM evidence is required, and resolution
belongs to `PACKAGE-POE-410-001`, not HW-PINMAP-410-FOLLOWUP.
`PACKAGE-POE-410-001` stays blocked behind (a) BOM cross-check,
(b) the `S360-410` `schematic_status: verified` JSON-only PR
(itself gated on BOM + HW-002 OQ#6 closure), (c) HW-002 OQ#6 /
`S360-100-BENCH-001` J2-harness identity closure, and (d) the
package-header reconciliation itself. The downstream PoE-410
chain (`PRODUCT-POE-410-001`, `WEBFLASH-POE-410-001`,
`RELEASE-POE-410-001`, `WF-IMPORT-POE-410-001`) stays blocked.
Release-One is unchanged. The LED preview path is unchanged.
FanTRIAC stays `status: blocked`. The Sense360 LED Release-One
exclusion is unchanged. The mains-voltage compliance status of
`S360-320` (FanTRIAC) and `S360-400` (240 V PSU) is unchanged
(COMPLIANCE-001; `S360-410` PoE PSU is **not** in scope because
PoE is SELV). The Release-One PoE "schematic verification
pending" caveat in
[`docs/release-one-hardware-audit.md` Findings → PoE PSU](release-one-hardware-audit.md#findings)
and [Required follow-ups #6](release-one-hardware-audit.md#required-follow-ups)
is **preserved verbatim**.

The HW-PINMAP-410-FOLLOWUP entry in the queue is moved from
`Next / after HW-ASSETS-410 merges` to `In flight (this PR) — PR
open / PR number pending`. The HW-ASSETS-410 entry is moved from
`In flight (this PR) — PR open / PR number pending` to
**Completed / merged PRs** as `HW-ASSETS-410 | #516`.

This update edits the following docs-only files:
[`docs/hardware/s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md)
(promotes the top-line status; rewrites the audit body into the
schematic-backed-partial pattern of
[`docs/hardware/s360-400-r4-power.md`](hardware/s360-400-r4-power.md)
/
[`docs/hardware/s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md);
adds the schematic-summary tables for `LAN_CON1` / `U1` / `U2` /
`DCDC1` / `J3` / `D3` / `H1`–`H4` / net topology; adds the
PoE-PD-controller / buck-stage / isolated-DC/DC / output /
mounting-hole findings sections; adds the part-identity
reconciliation table; updates the reconciliation findings table
and the known-unresolved-issues list; updates the package-YAML
status / product-WebFlash status / compliance-safety status /
required-evidence-before-promotion / follow-up PR sequence /
do-not-change guardrails sections; adds the HW-PINMAP-410-FOLLOWUP
audit log section with the 2026-05-19 dated row);
[`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
(refreshes the `S360-410` evidence-axis row, the `S360-410`
productization-axis row, the §`S360-410 Sense360 PoE PSU`
board-by-board notes, the Missing / unfinished boards narrative
`S360-410` bullet, and the Follow-up PR sequence item #6);
[`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md)
(refreshes the `S360-410` decision-table row and the
§Sense360 PoE PSU (`S360-410`) Evidence-available /
Evidence-missing bullets);
[`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
(refreshes the `power_poe.yaml` row and the §`power_poe.yaml` /
S360-410 detail subsection);
[`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
(refreshes the `power_poe.yaml` cross-link mention and adds the
new §`power_poe.yaml` PoE-module part-identity disagreement
(S360-410) per-area finding);
[`docs/product-readiness-matrix.md`](product-readiness-matrix.md)
(refreshes the PoE-410 candidate-product row and the §PoE-410 /
S360-410 subsection);
[`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md)
(refreshes the `S360-410` snapshot-row note to reflect
HW-PINMAP-410-FOLLOWUP consumption of the schematic);
[`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md)
(refreshes the PoE-410 candidate-product row and the §PoE /
S360-410 WebFlash posture Current-state paragraph);
[`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
(refreshes the PoE-410 candidate-product row and the §PoE /
S360-410 release-posture Current-state paragraph);
[`UPCOMING_PR.md`](../UPCOMING_PR.md) (records HW-ASSETS-410 as
PR #516 in Completed / merged PRs, removes HW-ASSETS-410 from the
in-flight slot, promotes HW-PINMAP-410-FOLLOWUP into the
in-flight slot, renumbers downstream queue items, refreshes the
PACKAGE-POE-410-001 row blocker notes, and updates the
"Recently uploaded evidence" S360-410 bullet); and this entry in
[`docs/cleanup-audit.md`](cleanup-audit.md).

This update explicitly **does not** edit
[`docs/hardware/schematics/S360-410-R4.pdf`](hardware/schematics/S360-410-R4.pdf)
(stays byte-identical to the HW-ASSETS-410 / PR #516 commit);
does **not** edit
[`docs/hardware/artifacts/S360-410-R4.md`](hardware/artifacts/S360-410-R4.md)
(its content is consumed by HW-PINMAP-410-FOLLOWUP, not
rewritten); does **not** edit
[`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)
(the PoE PSU caveat language is preserved verbatim); does
**not** edit
[`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
(COMPLIANCE-001 unchanged; PoE is SELV and `S360-410` is **not**
in scope); does **not** edit any value in
[`config/hardware-catalog.json`](../config/hardware-catalog.json)
(`S360-410` row stays `schematic_status: cataloged_unverified`
with no `schematic_file`),
[`config/product-catalog.json`](../config/product-catalog.json),
[`config/webflash-builds.json`](../config/webflash-builds.json),
or
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json);
does **not** add or modify any product YAML under
[`products/`](../products/) or any WebFlash wrapper under
[`products/webflash/`](../products/webflash/); does **not** add
or modify any package YAML under [`packages/`](../packages/)
(including
[`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml)
— comment-only cleanup of the stale `Ag9712M / Silvertel
Ag9700 / or similar` header, the partially-evidenced `IEEE
802.3af / 802.3at` / `Class 0 / Class 1` / `36-57V DC` / `5V DC,
2A (10W) or 3.3V DC` / `Overcurrent, overvoltage, short-circuit`
header lines, and the substitutions / globals / sensors / logger
/ on_boot blocks are **all** preserved byte-for-byte; comment-only
cleanup is **deferred to `PACKAGE-POE-410-001`** once BOM
evidence lands, per the brief's evidence standards "BOM is
required to resolve part number/rating disputes"); does **not**
edit any test under [`tests/`](../tests/), any script under
[`scripts/`](../scripts/), any workflow under
`.github/workflows/`, any component under `components/`, any
header under `include/`, `firmware/*`, `manifest.json`, or
`firmware/sources.json`; does **not** regenerate firmware,
create a GitHub Release or tag, or change any WebFlash manifest
/ import; does **not** advance `PACKAGE-POE-410-001`,
`PRODUCT-POE-410-001`, `WEBFLASH-POE-410-001`,
`RELEASE-POE-410-001`, or `WF-IMPORT-POE-410-001`; does **not**
close `S360-100-BENCH-001`, `HW-PINMAP-311-FOLLOWUP`,
`HW-PINMAP-312-FOLLOWUP`, `HW-PINMAP-320-FOLLOWUP`,
`HW-PINMAP-310-FOLLOWUP`, `HW-PINMAP-400-FOLLOWUP`, or
`CORE-ABSTRACT-BUS-001`; does **not** unblock FanTRIAC (HW-005
stays a separate gate); does **not** clear `COMPLIANCE-001` (for
`S360-320` or `S360-400`); does **not** change the Release-One
configuration (`Ceiling-POE-VentIQ-RoomIQ`, version `1.0.0`,
channel `stable`, artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
`v1.0.0`); does **not** change the LED preview entry
(`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`,
`channel: preview`, artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`);
does **not** change FanTRIAC state
(`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`,
`blocker: HW-005`, `webflash_build_matrix: false`); does
**not** change `REQUIRED_CONFIGS`, kits, or any WebFlash-side
artifact; does **not** change the `S360-400` Sense360 240v PSU
status or its documented part-identity disagreement; does
**not** resolve the systemic Core abstract-bus mismatch
enumerated in
[`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups);
does **not** claim that any bench / load / PoE-link-up / thermal
/ inrush / insulation / Hi-pot / earth-continuity / leakage /
EMI / EMC evidence exists; does **not** claim IEEE 802.3af /
802.3at PoE compliance for the design; does **not** claim
isolation / Hi-pot / earth-continuity / leakage compliance for
the assembled board; does **not** claim Release-One
requalification, product readiness, or WebFlash readiness; does
**not** make any CE / UKCA / FCC / UL / LVD / EMC / RoHS / IEC
claim.

**Next audit-log trigger.** The next HW-PINMAP-410-FOLLOWUP
audit-log entry should appear when committed evidence is added
to this repository that the field-evidence rules above can cite:
a BOM line item with manufacturer + part number + revision for
`U1` (settling the package-header whole-module vs
schematic-shown discrete topology disagreement), `U2`, `DCDC1`
(settling primary `F0505S-2WR2` vs alternate `AM1D-0505S-NZ`),
`LAN_CON1`, `D1`, `D2`, `D3`, `L1`, `R1`–`R9`, `C1`–`C8`, and
`J3` with ratings; operator-attributed silkscreen captures of
the module-side `J3` 1-to-2 pin order; KiCad PCB source /
gerbers / board photos sufficient to verify isolation-barrier
widths around the `F0505S-2WR2` and `H1`–`H4` PCB-level bonding
to `Lan_earth` / RJ45 shield; bench / load / PoE link-up
against 802.3af and 802.3at PSE / signature / classification /
load regulation / cold-start inrush / thermal rise / insulation
resistance / Hi-pot / earth-continuity / leakage / EMI / EMC
measurements against a populated `S360-410-R4` board with
operator / reviewer / serial recorded; HW-002 Open Question #6
/ `S360-100-BENCH-001` J2-harness identity closure (cable /
pigtail manufacturer, length, conductor count, connector key /
polarity at both ends); a standalone schematic-backed reference
doc (e.g. a new
`docs/hardware/s360-410-r4-poe-reference.md` companion in the
per-board reference pattern of
[`s360-200-r4-roomiq.md`](hardware/s360-200-r4-roomiq.md) /
[`s360-211-r4-ventiq.md`](hardware/s360-211-r4-ventiq.md) /
[`s360-300-r4-led.md`](hardware/s360-300-r4-led.md)); KiCad
schematic source (`S360-410-R4.kicad_sch`) / KiCad PCB source
(`S360-410-R4.kicad_pcb`) / KiCad project metadata
(`*.kicad_pro` / `*.kicad_prl` / `fp-lib-table` /
`sym-lib-table`) / CPL / drill files / STEP for `S360-410-R4`
that the audit can cite by repo path; or IEEE 802.3af /
802.3at compliance test reports / isolation / Hi-pot /
earth-continuity / leakage reports. Until any of those land,
the next audit-log entry should report the same
`partial — schematic evidence available; package reconciliation,
PoE PD controller / magnetics / buck / isolated DC/DC / harness
identity evidence pending` outcome with the new inspection date.

This update is recorded together with the existing
[§HW-PINMAP-400-FOLLOWUP update](#hw-pinmap-400-followup-update-2026-05-19-schematic-backed-reconciliation)
entry that this PR follows in pattern.

## CORE-ABSTRACT-BUS-001C update (2026-05-19 — docs-only investigation pass)

`CORE-ABSTRACT-BUS-001C` is the UART split (`uart_bus` →
`roomiq_hi_link_uart` on `IO1` / `IO2` + `roomiq_sen0609_uart` on
`IO4` / `IO5`) + status LED move off `GPIO48` (claimed by the shared
I²C SDA net per
[`docs/hardware/s360-100-r4-core.md` §ESP32-S3 pin and net mapping](hardware/s360-100-r4-core.md#esp32-s3-pin-and-net-mapping)
line 110) + `pir_sensor_pin: GPIO47 → GPIO15` (Core schematic
`IO15 = PIR`, line 94) + `comfort_ceiling_als_int_pin: GPIO3 → GPIO47`
(Core schematic `IO47 = ALS_INT`, line 109) +
`expander_int_pin: GPIO3 → GPIO17` (Core schematic
`IO17 = expander_int`, line 96) +
`sx1509_interrupt_pin: GPIO3 → GPIO17` + `expansion_gpio1..4` rebind
slice of `CORE-ABSTRACT-BUS-001`. It is the slice that must land
at-or-before `CORE-ABSTRACT-BUS-001A` (the `relay_pin → GPIO3`
slice) because the schematic-correct `relay_pin: GPIO3` collides with
the existing `comfort_ceiling_als_int_pin: GPIO3` in
[`packages/expansions/comfort_ceiling.yaml`](../packages/expansions/comfort_ceiling.yaml)
line 42 (consumed by Release-One via
[`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml)
line 140), per
[`docs/hardware/core-abstract-bus-reconciliation.md` §GPIO collision matrix](hardware/core-abstract-bus-reconciliation.md#gpio-collision-matrix).
It is named as the next active queue item in
[`UPCOMING_PR.md`](../UPCOMING_PR.md) (entry #1) and as the gating
systemic blocker for `CORE-ABSTRACT-BUS-001A` and therefore for
`PACKAGE-RELAY-001` / `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` /
`RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001`, plus for
`PACKAGE-PWM-001` / `PACKAGE-DAC-001` via the
`${expansion_gpio*}` substitutions in
[`packages/expansions/fan_pwm.yaml`](../packages/expansions/fan_pwm.yaml).

`CORE-ABSTRACT-BUS-001C` was investigated in this PR against the
readiness gates recorded in
[`docs/hardware/core-abstract-bus-reconciliation.md` §CORE-ABSTRACT-BUS-001C — UART / status LED / PIR / expansion GPIO slice](hardware/core-abstract-bus-reconciliation.md#core-abstract-bus-001c--uart--status-led--pir--expansion-gpio-slice)
and
[§Required evidence before any slice can land](hardware/core-abstract-bus-reconciliation.md#required-evidence-before-any-slice-can-land),
and against the three implementation paths defined by the queue task
brief (Path A docs-only deferral; Path B test-scaffold-only; Path C
implementation). It is **confirmed deferred** at the implementation
layer: the investigation produced a docs-only audit-log entry and the
queue / cross-link refresh below, rather than any package YAML,
product YAML, WebFlash wrapper, JSON catalog, script, test, workflow,
component, include, firmware artifact, or manifest edit. Every
readiness gate it depends on is still open.

The six open preconditions, each cited against the doc that owns its
closure, are:

(1) **`S360-100-BENCH-001` silkscreen evidence** — Core `J4` 1-to-3
pin order, Core `J10` 1-to-12 pin order, and RoomIQ `J6` 1-to-12 pin
order — has not been committed. The
[`docs/hardware/s360-100-r4-core.md` §S360-100-BENCH-001 status](hardware/s360-100-r4-core.md#s360-100-bench-001-status)
record stays `pending — bench/manufacturing evidence required` per
the most recent 2026-05-18 re-check captured in the audit log there.
No operator-attributed silkscreen captures, harness photos, scope /
continuity traces, or BOM / CPL / Gerber / STEP review findings have
been committed since.

(2) The **RoomIQ / AirIQ / VentIQ rebind plan** (rebinding
[`packages/expansions/comfort_ceiling.yaml`](../packages/expansions/comfort_ceiling.yaml),
[`packages/expansions/presence_ceiling.yaml`](../packages/expansions/presence_ceiling.yaml),
[`packages/expansions/airiq_bathroom_base.yaml`](../packages/expansions/airiq_bathroom_base.yaml),
[`packages/expansions/airiq_ceiling.yaml`](../packages/expansions/airiq_ceiling.yaml),
[`packages/expansions/airiq_wall.yaml`](../packages/expansions/airiq_wall.yaml),
and the matching feature profiles to the schematic-correct shared
I²C bus on `IO48` / `IO45` and the two radar UARTs `Hi-Link` on
`IO1` / `IO2` + `SEN0609` on `IO4` / `IO5`) has not been drafted.
The companion AirIQ / VentIQ J9 `AirQ_Led` / `AirQ_Status_Led`
re-bind decision is also unresolved per
[`docs/hardware/firmware-package-mapping-audit.md` §VentIQ J9 / `AirQ_Led` / `AirQ_Status_Led`](hardware/firmware-package-mapping-audit.md#ventiq-j9--airq_led--airq_status_led)
and
[§AirIQ J9 / `AirQ_Led` / `AirQ_Status_Led`](hardware/firmware-package-mapping-audit.md#airiq-j9--airq_led--airq_status_led).

(3) The **expansion-GPIO bench evidence or documented retirement
decision** — either (a) bench evidence that specific pins are routed
to the expansion connector and have no schematic-named function, or
(b) a documented decision to retire the `expansion_gpio*`
abstraction in favour of explicit function-named substitutions
(e.g. `fan_pwm_pin`, `fan_tach_pin`) bound to schematic nets — has
not been recorded. Downstream consumer
[`packages/expansions/fan_pwm.yaml`](../packages/expansions/fan_pwm.yaml)
binds `fan_pwm_pin: ${expansion_gpio1}` and
`fan_tach_pin: ${expansion_gpio2}`, so the abstraction is not orphan.

(4) The **ESP32-S3 `GPIO3` strap-pin boot-behaviour
characterisation** against a populated `S360-310-R4` + `S360-100-R4`
pair has not been committed. `GPIO3` is a JTAG-select strap pin on
ESP32-S3; the relay module's `Q1` MMBT3904 NPN low-side topology
recorded in
[`docs/hardware/artifacts/S360-310-R4.md`](hardware/artifacts/S360-310-R4.md)
suggests `RESTORE_DEFAULT_OFF` keeps the strap in a benign state at
boot, but no bench evidence verifies this. Strictly a
`CORE-ABSTRACT-BUS-001A` precondition; recorded here because `001C`
frees `GPIO3` for the relay slice to consume.

(5) The proposed pin-pinning regression test
**`tests/test_core_abstract_bus.py`** (modeled on
[`tests/test_led_package_mapping.py`](../tests/test_led_package_mapping.py)
per
[`docs/hardware/core-abstract-bus-reconciliation.md` §Test scaffolding plan](hardware/core-abstract-bus-reconciliation.md#test-scaffolding-plan))
does not exist. Per the test-scaffolding plan, the file lands **with
the first implementation slice**, not as a standalone PR — a
test-scaffold-only PR would either enshrine the current
schematic-conflicting values (`status_led_pin: GPIO48` on the I²C
SDA net; `comfort_ceiling_als_int_pin: GPIO3` on the `Relay` net;
`pir_sensor_pin: GPIO47` on the `ALS_INT` net; `expansion_gpio1..4`
on RoomIQ-claimed nets) and become a tripwire against the future
correct values, or pin unverified target values (the per-board
`status_led_pin` re-bind and the `expansion_gpio*`
retirement-or-rebind decision are still undecided because
preconditions (2) / (3) are open).

(6) The **re-validation pass for every non-Release-One product YAML
consuming any affected Core abstract package** — at minimum the
~30 product YAMLs enumerated per Core package in
[`docs/hardware/core-abstract-bus-reconciliation.md` §Blast radius per Core package](hardware/core-abstract-bus-reconciliation.md#blast-radius-per-core-package)
— has not been designed.

Because all six preconditions are open and the GPIO3 collision means
no single `001C` substitution can land safely on its own, **Path A
(docs-only investigation / deferral)** is taken: this PR records the
investigation outcome and refreshes the queue / cross-link state,
without any package YAML, product YAML, WebFlash wrapper, JSON
catalog, script, test, workflow, component, include, firmware
artifact, or manifest change. **Path B (test-scaffold-only)** is
**not useful right now** for the reason recorded above against
precondition (5): target values are not fully decided and
current-value tests would enshrine schematic-conflicting values.
**Path C (implementation)** is **unsafe right now** because the six
preconditions above remain open and an implementation PR would
silently re-bind Release-One on unverified silkscreen / strap-pin /
expansion-GPIO evidence. The reconciliation doc's own
[§Do-not-change list](hardware/core-abstract-bus-reconciliation.md#do-not-change-list)
explicitly forbids any package YAML edit until the slice
preconditions have landed.

Verified `001C` scope against the live YAML in this pass — every
value below matches
[`docs/hardware/core-abstract-bus-reconciliation.md` §Core abstract substitution inventory](hardware/core-abstract-bus-reconciliation.md#core-abstract-substitution-inventory)
byte-for-byte: `uart_bus` is still a single
`GPIO1` / `GPIO2` bus in
[`packages/hardware/sense360_core.yaml`](../packages/hardware/sense360_core.yaml)
line 115,
[`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml)
line 121,
[`packages/hardware/sense360_core_poe.yaml`](../packages/hardware/sense360_core_poe.yaml)
line 141, and
[`packages/hardware/sense360_core_wall.yaml`](../packages/hardware/sense360_core_wall.yaml)
line 131 (no `roomiq_hi_link_uart` / `roomiq_sen0609_uart` named
bus exists anywhere in the repo today); `status_led_pin: GPIO48`
still binds on the I²C SDA net in
[`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml)
line 76, with `status_led_rgb_pin: GPIO48` still binding in
[`packages/hardware/sense360_core.yaml`](../packages/hardware/sense360_core.yaml)
line 66,
[`packages/hardware/sense360_core_mapping.yaml`](../packages/hardware/sense360_core_mapping.yaml)
line 48, and
[`packages/hardware/sense360_core_wall.yaml`](../packages/hardware/sense360_core_wall.yaml)
line 79; `pir_sensor_pin: GPIO47` still binds on the `ALS_INT` net
in
[`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml)
line 77; `comfort_ceiling_als_int_pin: GPIO3` still binds in
[`packages/expansions/comfort_ceiling.yaml`](../packages/expansions/comfort_ceiling.yaml)
line 42; `comfort_als_int_pin: GPIO3` still binds in
[`packages/expansions/comfort_ceiling_s3.yaml`](../packages/expansions/comfort_ceiling_s3.yaml)
line 29 and
[`packages/hardware/sense360_core_ceiling_s3.yaml`](../packages/hardware/sense360_core_ceiling_s3.yaml)
line 140 (both still classified `out-of-scope` for `001C` until the
S3 board layout is verified); `expander_int_pin: GPIO3` still binds
in
[`packages/hardware/sense360_core_mapping.yaml`](../packages/hardware/sense360_core_mapping.yaml)
line 54; `sx1509_interrupt_pin: GPIO3` still binds in
[`packages/expansions/gpio_expander_sx1509.yaml`](../packages/expansions/gpio_expander_sx1509.yaml)
line 17; and `expansion_gpio1..4` still bind on RoomIQ-claimed nets
in
[`packages/hardware/sense360_core.yaml`](../packages/hardware/sense360_core.yaml)
lines 57–60,
[`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml)
lines 65–68,
[`packages/hardware/sense360_core_mapping.yaml`](../packages/hardware/sense360_core_mapping.yaml)
lines 57–59,
[`packages/hardware/sense360_core_poe.yaml`](../packages/hardware/sense360_core_poe.yaml)
lines 70–73, and
[`packages/hardware/sense360_core_wall.yaml`](../packages/hardware/sense360_core_wall.yaml)
lines 69–72. Every one of these package YAML files stays
**byte-identical** to its pre-PR state.

The `IO1` / `IO2` / `IO4` / `IO5` (Core schematic) vs single-bus
`uart_bus` on `GPIO1` / `GPIO2` (Core packages) UART resolution,
the `IO46` vs `IO7` vs `IO48` `status_led_pin` resolution, the
`GPIO47 → GPIO15` PIR resolution, the `GPIO3 → GPIO47` ALS_INT
resolution, the `GPIO3 → GPIO17` `expander_int` / `sx1509_interrupt`
resolution, and the `expansion_gpio1..4` rebind / retirement
decision all stay owned by `CORE-ABSTRACT-BUS-001C`. The
`IO3` (Core schematic) vs `GPIO4` / `GPIO10` `relay_pin` resolution
stays owned by `CORE-ABSTRACT-BUS-001A` (which itself depends on
`001C` landing first). The shared I²C bus consolidation
(`halo_i2c` / `expansion_i2c` / `i2c0` / `i2c1` / `i2c_primary` /
`i2c_expander` → single shared bus on `IO48` / `IO45`) stays owned
by `CORE-ABSTRACT-BUS-001B`.

Companion fact captured in the queue refresh below:
`HW-PINMAP-410-FOLLOWUP` merged as **PR #517** on 2026-05-19 and
brings no `001C`-relevant precondition closer. The PR #517 audit log
in [`docs/hardware/s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md)
records the schematic-backed PoE PSU mapping promotion to
`partial — schematic evidence available; package reconciliation,
PoE PD controller / magnetics / buck / isolated DC/DC / harness
identity evidence pending` and the unresolved package-header
whole-module-hint (`Ag9712M / Silvertel Ag9700 / or similar`) vs
schematic-shown discrete topology
(`TPS2378DDAR / TX4138 / F0505S-2WR2 / RJP-003TC1(LPJ4112CNL)`)
part-identity disagreement. None of that touches the
`CORE-ABSTRACT-BUS-001C` scope; `PACKAGE-POE-410-001` remains
blocked behind BOM / `S360-410 schematic_status: verified` JSON PR
/ HW-002 OQ#6 / `S360-100-BENCH-001` closure / package-header
reconciliation.

Documentation only. CORE-ABSTRACT-BUS-001C (this investigation pass)
does **not** edit
[`config/hardware-catalog.json`](../config/hardware-catalog.json)
(`S360-100` stays `schematic_status: verified` per HW-008; `S360-310`
stays `cataloged_unverified`; `S360-311` / `S360-312` / `S360-320` /
`S360-400` / `S360-410` stay as recorded today),
[`config/product-catalog.json`](../config/product-catalog.json),
[`config/webflash-builds.json`](../config/webflash-builds.json),
or
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json);
does **not** edit any product YAML under
[`products/`](../products/) or any WebFlash wrapper under
[`products/webflash/`](../products/webflash/); does **not** edit any
package YAML under [`packages/`](../packages/) (no Core, no
expansion, no feature profile, no `comfort_ceiling.yaml`, no
`comfort_ceiling_s3.yaml`, no `gpio_expander_sx1509.yaml`, no
`fan_relay.yaml`, no `fan_pwm.yaml`, no presence / AirIQ / VentIQ
package); does **not** add `tests/test_core_abstract_bus.py` or edit
any test under [`tests/`](../tests/), any script under
[`scripts/`](../scripts/), any workflow under `.github/workflows/`,
any component under `components/`, any header under `include/`,
`firmware/*`, `manifest.json`, or `firmware/sources.json`; does
**not** regenerate firmware, create a GitHub Release or tag, or
change any WebFlash manifest / import; does **not** advance
`CORE-ABSTRACT-BUS-001A`, `CORE-ABSTRACT-BUS-001B`,
`PACKAGE-RELAY-001`, `PRODUCT-RELAY-001`, `WEBFLASH-RELAY-001`,
`RELEASE-RELAY-001`, `WF-IMPORT-RELAY-001`, `PACKAGE-PWM-001`,
`PRODUCT-PWM-001`, `WEBFLASH-PWM-001`, `RELEASE-PWM-001`,
`PACKAGE-DAC-001`, `PRODUCT-DAC-001`, `WEBFLASH-DAC-001`,
`RELEASE-DAC-001`, `PACKAGE-TRIAC-001`, `PRODUCT-TRIAC-002`,
`WF-TRIAC-001`, `RELEASE-TRIAC-001`, `WF-IMPORT-TRIAC-001`,
`PACKAGE-POE-410-001`, `PRODUCT-POE-410-001`, `WEBFLASH-POE-410-001`,
`RELEASE-POE-410-001`, `PACKAGE-POWER-400-001`,
`PRODUCT-POWER-400-001`, `WEBFLASH-POWER-400-001`, or
`RELEASE-POWER-400-001`; does **not** close
`S360-100-BENCH-001`, `HW-PINMAP-310-FOLLOWUP`,
`HW-PINMAP-311-FOLLOWUP`, `HW-PINMAP-312-FOLLOWUP`,
`HW-PINMAP-320-FOLLOWUP`, `HW-PINMAP-400-FOLLOWUP`,
`HW-PINMAP-410-FOLLOWUP`, `COMPLIANCE-001`, or `S360-300-BENCH-001`;
does **not** unblock FanTRIAC (HW-005 stays a separate gate); does
**not** change the Release-One configuration (`Ceiling-POE-VentIQ-RoomIQ`,
version `1.0.0`, channel `stable`, artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
`v1.0.0`); does **not** change the LED preview entry
(`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`,
`channel: preview`, artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`); does
**not** change `REQUIRED_CONFIGS` or kits; does **not** promote any
`schematic_status`; does **not** set any `schematic_file`; does
**not** claim any hardware-verified evidence; does **not** claim
that any bench / silkscreen / strap-pin / expansion-GPIO /
RoomIQ-rebind / AirIQ-rebind / VentIQ-rebind / re-validation
evidence exists; does **not** claim any compliance evidence for any
mains-switching product.

The only files this update touches are this `CORE-ABSTRACT-BUS-001C
update` section in `docs/cleanup-audit.md`, the new audit-log entry
`### 2026-05-19 — CORE-ABSTRACT-BUS-001C investigation pass (deferred; six preconditions still open)`
in
[`docs/hardware/core-abstract-bus-reconciliation.md`](hardware/core-abstract-bus-reconciliation.md),
single-sentence cross-link addenda in
[`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
(`CORE-ABSTRACT-BUS-001` row in the Follow-up PR sequence),
[`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
(`Systemic Core abstract-bus rebind` section), and
[`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)
(Required follow-ups #2 / #3 trailing note), and the queue refresh
in [`UPCOMING_PR.md`](../UPCOMING_PR.md) (HW-PINMAP-410-FOLLOWUP
moved into the Completed / merged PRs table as PR #517;
`CORE-ABSTRACT-BUS-001C` queue row annotated with the investigation
outcome).

**Next CORE-ABSTRACT-BUS-001C audit-log trigger.** The next
audit-log entry against this slice should appear when one of the
six preconditions above lands or when the next implementation PR
makes a `001C` package YAML / test edit. Until then, the next
audit-log entry should report the same
`CORE-ABSTRACT-BUS-001C investigation pass — six preconditions
still open` outcome with the new inspection date.

## CORE-ABSTRACT-BUS-001B update (2026-05-19 — docs-only investigation pass)

This update records the 2026-05-19 docs-only investigation pass
against `CORE-ABSTRACT-BUS-001B` (the shared-I²C-bus consolidation
slice). The companion `CORE-ABSTRACT-BUS-001C` investigation pass
merged earlier the same day as **PR #518** and is recorded above at
[§CORE-ABSTRACT-BUS-001C update](#core-abstract-bus-001c-update-2026-05-19--docs-only-investigation-pass).

**Outcome — Path A docs-only investigation / deferral.**
`CORE-ABSTRACT-BUS-001B` is **confirmed deferred at the
implementation layer.** Four preconditions remain open. The
downstream-consumer audit (precondition #1 of the four enumerated
under
[`docs/hardware/core-abstract-bus-reconciliation.md` §CORE-ABSTRACT-BUS-001B](hardware/core-abstract-bus-reconciliation.md#core-abstract-bus-001b--shared-i²c-bus-consolidation-slice))
lands inside this pass as
[`docs/hardware/core-abstract-bus-reconciliation.md` §Downstream consumer inventory (2026-05-19)](hardware/core-abstract-bus-reconciliation.md#downstream-consumer-inventory-2026-05-19),
but **is not by itself** sufficient to land an implementation
slice.

**Findings recorded.** Re-verified against the live YAML
(byte-identical to the existing `CORE-ABSTRACT-BUS-001` audit
inventory at
[`docs/hardware/core-abstract-bus-reconciliation.md` §I²C bus substitutions](hardware/core-abstract-bus-reconciliation.md#i²c-bus-substitutions)
and [§GPIO collision matrix](hardware/core-abstract-bus-reconciliation.md#gpio-collision-matrix)):

- **Eight in-scope Core packages defining I²C buses** —
  `packages/hardware/sense360_core.yaml` (`i2c0` + `i2c1`),
  `packages/hardware/sense360_core_ceiling.yaml` (`halo_i2c` +
  `expansion_i2c`),
  `packages/hardware/sense360_core_mapping.yaml` (`i2c_primary` +
  `i2c_expander`),
  `packages/hardware/sense360_core_poe.yaml` (`i2c0` + `i2c1`),
  `packages/hardware/sense360_core_wall.yaml` (`i2c0` + `i2c1`),
  `packages/hardware/sense360_core_voice_ceiling.yaml` (`halo_i2c`
  + `expansion_i2c` — **newly added to `001B` scope by this
  investigation**), and
  `packages/hardware/sense360_core_voice_wall.yaml` (`i2c0` +
  `i2c1` — **newly added to `001B` scope by this
  investigation**).
- **Two out-of-scope Core packages** —
  `packages/hardware/sense360_core_ceiling_s3.yaml`
  (different board layout) and
  `packages/hardware/sense360_core_mini.yaml`
  (Mini baseline, `i2c0` already on `GPIO48` / `GPIO45`).
- **Schematic ground truth** for `S360-100-R4` is a **single
  shared I²C bus** on `IO48` (SDA) / `IO45` (SCL), pulled up by
  R22 / R21 10 kΩ, shared by SX1509 (U3), J7 GP8403, J9 AirIQ,
  J10 RoomIQ, per
  [`docs/hardware/s360-100-r4-core.md` §I2C bus](hardware/s360-100-r4-core.md#i2c-bus).
- **13 downstream expansion-package `*_i2c_id` consumers** —
  `airiq.yaml` (`i2c0`), `airiq_wall.yaml` (`i2c0`),
  `airiq_ceiling.yaml` (`expansion_i2c`),
  `airiq_ceiling_s3.yaml` (`i2c_primary`),
  `airiq_bathroom_base.yaml` (`expansion_i2c` — consumed by
  Release-One via VentIQ),
  `airiq_bathroom_pro.yaml` (`expansion_i2c`),
  `comfort.yaml` (`i2c0`), `comfort_wall.yaml` (`i2c0`),
  `comfort_ceiling.yaml` (`expansion_i2c` — consumed by
  Release-One via RoomIQ comfort),
  `comfort_ceiling_s3.yaml` (`i2c_primary`),
  `fan_gp8403.yaml` (`i2c0`),
  `gpio_expander_sx1509.yaml` (`i2c1`), and
  `packages/features/ceiling_halo_leds.yaml` which **hard-codes
  `i2c_id: halo_i2c`** and currently has **no product `!include`r**
  — needs rebind or dead-code decision in the eventual `001B` PR.
- **Release-One and LED preview consumer paths** both resolve
  `expansion_i2c` via VentIQ
  (`packages/expansions/airiq_bathroom_base.yaml` line 29) and
  RoomIQ comfort (`packages/expansions/comfort_ceiling.yaml`
  line 39). The LED preview additionally `!include`s
  `packages/hardware/led_ring_ceiling.yaml` (WS2812B
  `led_data_pin: GPIO38`, **not** I²C). Neither product
  `!include`s `packages/features/ceiling_halo_leds.yaml`, so the
  `halo_i2c` bus is defined-but-unused by both shipping
  configurations.
- **Canonical bus-id candidates recorded but not chosen** —
  `shared_i2c`, `core_i2c`, `i2c0`. The decision belongs to the
  implementation slice.

**Open preconditions (carried forward).**

1. Canonical I²C bus-id decision remains open.
2. `tests/test_core_abstract_bus.py` pin-pinning scaffold remains
   absent (same finding as PR #518); per the test-scaffolding
   plan it lands **with** the first implementation slice.
3. Re-validation plan for every non-Release-One product YAML
   consuming an affected Core / expansion package is not designed.
4. The downstream-consumer audit lands in this PR but
   implementation still needs canonical name + tests + product
   re-validation before YAML edits.

**Why Path B and Path C are not taken now.**

- **Path B (test-scaffold-only)** is not useful right now because
  it would either pin the schematic-conflicting current values
  (`halo_i2c` / `expansion_i2c` / `i2c0` / `i2c1` / `i2c_primary`
  / `i2c_expander` all on `GPIO39`/`GPIO40` + `GPIO21`/`GPIO18`)
  or pre-commit one of the three undecided canonical bus-id
  candidates. Per
  [`docs/hardware/core-abstract-bus-reconciliation.md` §Test scaffolding plan](hardware/core-abstract-bus-reconciliation.md#test-scaffolding-plan)
  the test file lands **with** the first implementation slice.
- **Path C (implementation)** is unsafe right now because the
  four preconditions above are open. Renaming any of the six
  current bus ids without simultaneously updating every
  downstream `*_i2c_id` consumer would break parse-time
  substitution resolution; even an in-place rebind without
  renaming would silently re-bind Release-One on unverified
  end-to-end behaviour, without the pin-pinning regression test.

**Recommendation for the next `001B` PR.** Land **the canonical
bus-id decision plus the pin-pinning test plus the YAML rebind
(Core packages plus every downstream `*_i2c_id` consumer) plus
the product re-validation pass as a single atomic slice**, not
as a test-scaffold-only PR alone. Details recorded at
[`docs/hardware/core-abstract-bus-reconciliation.md` §2026-05-19 — CORE-ABSTRACT-BUS-001B investigation pass](hardware/core-abstract-bus-reconciliation.md#2026-05-19--core-abstract-bus-001b-investigation-pass-deferred-preconditions-still-open).

**Queue effect.**

- `CORE-ABSTRACT-BUS-001B` is now **investigated and deferred** in
  the [`UPCOMING_PR.md`](../UPCOMING_PR.md) active queue (entry
  #3), blocked on the four preconditions above. Stays independent
  of `001A` / `001C` ordering; must land before `PACKAGE-PWM-001`
  / `PACKAGE-DAC-001`.
- `CORE-ABSTRACT-BUS-001C` stays at the top of the active queue
  (entry #1), blocked on its own six preconditions per the
  2026-05-19 `001C` investigation pass merged as **PR #518**.
- `CORE-ABSTRACT-BUS-001A` stays blocked behind `001C` (per the
  GPIO3 collision row of
  [`docs/hardware/core-abstract-bus-reconciliation.md` §GPIO collision matrix](hardware/core-abstract-bus-reconciliation.md#gpio-collision-matrix)).
- `PACKAGE-PWM-001` and `PACKAGE-DAC-001` stay blocked behind
  `001B` implementation (and their own evidence gates).
  `PACKAGE-PWM-001` specifically needs the canonical bus-id
  rebind so that
  [`packages/expansions/gpio_expander_sx1509.yaml`](../packages/expansions/gpio_expander_sx1509.yaml)'s
  `sx1509_i2c_id: i2c1` resolves to the shared bus on `IO48` /
  `IO45`. `PACKAGE-DAC-001` needs the same rebind for
  [`packages/expansions/fan_gp8403.yaml`](../packages/expansions/fan_gp8403.yaml)'s
  `fan_dac_i2c_id: i2c0`.
- `PACKAGE-RELAY-001` / `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001`
  / `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001` stay blocked
  behind `001A` (which is itself blocked behind `001C`).

**What this update does *not* do.** Adds **no** package YAML,
product YAML, WebFlash wrapper, JSON catalog change, script,
test, workflow, component, include, firmware artifact, manifest,
GitHub Release, tag, WebFlash import, or kit edit. The canonical
I²C bus-id is **not chosen** by this pass — only the candidate
set `shared_i2c` / `core_i2c` / `i2c0` is recorded. No
`CORE-ABSTRACT-BUS-001*` slice has changed status as a result.
No precondition is closed by this pass — the downstream-consumer
audit lands here but is not a substitute for the canonical name,
the test scaffold, or the non-Release-One product re-validation
pass. Specifically: does **not** advance
`CORE-ABSTRACT-BUS-001A`, `CORE-ABSTRACT-BUS-001B`, or
`CORE-ABSTRACT-BUS-001C`; does **not** advance
`PACKAGE-RELAY-001`, `PRODUCT-RELAY-001`, `WEBFLASH-RELAY-001`,
`RELEASE-RELAY-001`, `WF-IMPORT-RELAY-001`, `PACKAGE-PWM-001`,
`PRODUCT-PWM-001`, `WEBFLASH-PWM-001`, `RELEASE-PWM-001`,
`PACKAGE-DAC-001`, `PRODUCT-DAC-001`, `WEBFLASH-DAC-001`,
`RELEASE-DAC-001`, `PACKAGE-TRIAC-001`, `PRODUCT-TRIAC-002`,
`WF-TRIAC-001`, `RELEASE-TRIAC-001`, `WF-IMPORT-TRIAC-001`,
`PACKAGE-POE-410-001`, `PRODUCT-POE-410-001`,
`WEBFLASH-POE-410-001`, `RELEASE-POE-410-001`,
`PACKAGE-POWER-400-001`, `PRODUCT-POWER-400-001`,
`WEBFLASH-POWER-400-001`, or `RELEASE-POWER-400-001`; does
**not** close `S360-100-BENCH-001`, `HW-PINMAP-310-FOLLOWUP`,
`HW-PINMAP-311-FOLLOWUP`, `HW-PINMAP-312-FOLLOWUP`,
`HW-PINMAP-320-FOLLOWUP`, `HW-PINMAP-400-FOLLOWUP`,
`HW-PINMAP-410-FOLLOWUP`, `COMPLIANCE-001`, or
`S360-300-BENCH-001`; does **not** unblock FanTRIAC (HW-005
stays a separate gate); does **not** change the Release-One
configuration (`Ceiling-POE-VentIQ-RoomIQ`, version `1.0.0`,
channel `stable`, artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
`v1.0.0`); does **not** change the LED preview entry
(`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`,
`channel: preview`, artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`);
does **not** change `REQUIRED_CONFIGS` or kits; does **not**
promote any `schematic_status`; does **not** set any
`schematic_file`; does **not** claim any hardware-verified
evidence; does **not** claim that any bench / silkscreen /
strap-pin / canonical-name / pin-pinning-test / non-Release-One
re-validation evidence exists; does **not** claim any compliance
evidence for any mains-switching product.

The only files this update touches are this
`CORE-ABSTRACT-BUS-001B update` section in
`docs/cleanup-audit.md`, the new audit-log entry
`### 2026-05-19 — CORE-ABSTRACT-BUS-001B investigation pass (deferred; preconditions still open)`
plus the scope-extension addendum in
[`docs/hardware/core-abstract-bus-reconciliation.md`](hardware/core-abstract-bus-reconciliation.md),
and the queue refresh in [`UPCOMING_PR.md`](../UPCOMING_PR.md)
(`CORE-ABSTRACT-BUS-001C` recorded as PR #518 in the
Completed / merged PRs table, current-queue-summary updated, and
`CORE-ABSTRACT-BUS-001B` queue row annotated with the
investigation outcome).

**Next CORE-ABSTRACT-BUS-001B audit-log trigger.** The next
audit-log entry against this slice should appear when one of the
four preconditions above lands or when the next implementation PR
makes a `001B` package YAML / test edit. Until then, the next
audit-log entry should report the same
`CORE-ABSTRACT-BUS-001B investigation pass — preconditions still
open` outcome with the new inspection date.

## PACKAGE-POWER-400-001 update (2026-05-19 — docs-only investigation pass)

This update records the 2026-05-19 docs-only investigation pass
against `PACKAGE-POWER-400-001` (the S360-400 240 V PSU power
package reconciliation slice). `CORE-ABSTRACT-BUS-001B` merged
earlier the same day as **PR #519** and is recorded above at
[§CORE-ABSTRACT-BUS-001B update](#core-abstract-bus-001b-update-2026-05-19--docs-only-investigation-pass);
`001B` is unrelated to `PACKAGE-POWER-400-001` because the power
package binds **no** shared Core variables (no GPIO / I²C / UART
/ SPI / DAC binding in
[`packages/hardware/power_240v.yaml`](../packages/hardware/power_240v.yaml)).

**Outcome — Path A docs-only investigation / deferral.**
`PACKAGE-POWER-400-001` is **confirmed deferred at the
implementation layer.** Five preconditions remain open. No BOM has
arrived since HW-PINMAP-400-FOLLOWUP / PR #515 (see
[`docs/hardware/artifacts/S360-400-R4.md` §Files NOT provided in this upload](hardware/artifacts/S360-400-R4.md#files-not-provided-in-this-upload));
the package, the catalog, and the JSON `schematic_status` all
stay byte-identical to their PR #515 state.

**Findings recorded.** Re-verified against the live files
(byte-identical to the HW-PINMAP-400-FOLLOWUP / PR #515 inventory
at
[`docs/hardware/s360-400-r4-power.md` §Package YAML status](hardware/s360-400-r4-power.md#package-yaml-status)
and
[§Part identity reconciliation](hardware/s360-400-r4-power.md#part-identity-reconciliation)):

- [`packages/hardware/power_240v.yaml`](../packages/hardware/power_240v.yaml)
  is a logical-power package emitting diagnostic sensors only
  (`Supply Voltage` / `Power Source` / `Power Configuration` /
  `AC Power Connected`); **no GPIO / I²C / UART / SPI / DAC
  binding**. Header comments at lines 1–26 carry the stale
  `HLK-PM01 or similar` AC/DC part hint (line 7), the
  `100-240V AC, 50/60Hz` input claim (line 7), the
  `5V DC, 2A (10W)` output claim (line 8), the `3000VAC`
  isolation claim (line 9), the `Overcurrent, overvoltage,
  short-circuit` protection text (line 10), and the recommended
  `1A` AC-input fusing line (line 15). The
  `substitutions: power_source: "240v_ac"` (line 29), the
  `globals: power_source_type` (lines 32–36), and the `logger`
  config are also preserved byte-for-byte.
- [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  `S360-400` row at lines 102–110 still records
  `description: Mains to 5V using HLK-5M05.` (line 109),
  `schematic_status: cataloged_unverified` (line 110), and no
  `schematic_file`.
- [`tests/test_hardware_catalog.py`](../tests/test_hardware_catalog.py)
  `EXPECTED_STILL_UNVERIFIED_SKUS = frozenset({"S360-320",
  "S360-400"})` at line 53 actively enforces the `S360-400`
  `cataloged_unverified` / no `schematic_file` state via the
  assertion at lines 220–251.
- [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
  COMPLIANCE-001 mains-voltage UK / EU assessment tracker
  applies to `S360-400` (one of two mains-voltage SKUs in scope,
  the other being `S360-320` Sense360 TRIAC). Last re-check
  PR #506; status remains open / not cleared.
- [`docs/hardware/artifacts/S360-400-R4.md`](hardware/artifacts/S360-400-R4.md)
  §Files NOT provided in this upload confirms **no** BOM /
  KiCad source / KiCad PCB / project metadata / CPL / gerbers /
  drill / STEP / board images / silkscreen photos / bench /
  load / thermal / EMI photos or measurements / compliance test
  reports have arrived for `S360-400-R4` since PR #514.
- The HW-PINMAP-400 top-line status stays `partial — schematic
  evidence available; package reconciliation, BOM, silkscreen,
  creepage/clearance, and COMPLIANCE-001 pending` (no change
  from PR #515).
- The
  [`power_240v.yaml` row in package-readiness-matrix.md](hardware/package-readiness-matrix.md#power_240vyaml--s360-400)
  stays `schematic-evidence-pending` +
  `needs-package-reconciliation` + `timing/compliance-pending`
  (compliance-gated).

**Three-way AC/DC part-identity disagreement stays unresolved and
BOM-bound:**

- catalog
  [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  line 109 `Mains to 5V using HLK-5M05.`
- package header
  [`packages/hardware/power_240v.yaml`](../packages/hardware/power_240v.yaml)
  line 7 `HLK-PM01 or similar`
- schematic
  [`docs/hardware/schematics/S360-400-R4.pdf`](hardware/schematics/S360-400-R4.pdf)
  (HW-ASSETS-400 / PR #514) `PS1 = HLK-10M05`

**Open preconditions (carried forward).**

1. **BOM cross-check missing.** No BOM line item with
   manufacturer + part number + revision for `PS1`; no BOM lines
   for `F1 A250-1200` / `RV1 10D391K` / `C1 470nF` / `C5..C8` /
   `J1` / `J2` with ratings.
2. **`S360-400` `schematic_status: verified` JSON PR not landed.**
   Separate JSON-only PR after BOM + silkscreen evidence land.
3. **`COMPLIANCE-001` `S360-400` slice still open.** Last
   re-checked PR #506; mains-voltage UK / EU assessment not
   cleared.
4. **Silkscreen / PCB / creepage / clearance / bench / thermal /
   EMI evidence missing.** All of: `J1` / `J2` silkscreen pin-1
   orientation; `J1` mains-rated connector identity / current /
   voltage / approvals; `J2` low-voltage connector identity;
   `F1` polyfuse hold / trip / voltage rating; `RV1` clamp
   voltage / energy rating; `C1` X-cap safety class X1 / X2;
   `C5..C8` voltage / dielectric / ESR; Y-cap presence-or-absence
   as designed; common-mode / differential-mode line-filter
   inductor absence as designed; integrated thermal protection in
   the `HLK-10M05` module; mounting-hole electrical bonding to
   `Earth_Protective`; creepage / clearance distances between AC
   LINE / NEUTRAL / `Earth_Protective` / secondary `+5VP` /
   `GND`; load regulation; thermal rise of `PS1`; inrush current;
   insulation resistance / Hi-pot / earth-continuity / leakage;
   EMI / EMC conducted / radiated emissions and immunity.
5. **Three-way AC/DC part-identity disagreement** stays
   unresolved and BOM-bound per the explicit decision recorded by
   HW-PINMAP-400-FOLLOWUP / PR #515.

**Why Path B and Path C are not taken now.**

- **Path B (comment-only package cleanup)** is not useful right
  now because PR #515 explicitly recorded comment-only cleanup as
  deferred to `PACKAGE-POWER-400-001` once BOM evidence lands
  ("Replacing one unsourced claim with another would not raise
  the evidence quality of the package and would muddy the future
  PACKAGE-POWER-400-001 PR's scope" —
  [`docs/hardware/s360-400-r4-power.md` §Package YAML status](hardware/s360-400-r4-power.md#package-yaml-status)).
  The only safe comment-only edit would be to remove the
  `HLK-PM01 or similar` line altogether **without** claiming
  `HLK-10M05` or any replacement, but PR #515's recorded decision
  was specifically that even that removal should wait for BOM so
  that the eventual `PACKAGE-POWER-400-001` PR can land header
  reconciliation + catalog `description` reconciliation + BOM
  citation as one coordinated change.
- **Path C (implementation)** is unsafe right now because all
  five preconditions above are open. Editing the package header
  or the catalog `description` without BOM evidence would
  substitute one unsourced claim for another and would muddy the
  scope of the eventual coordinated `PACKAGE-POWER-400-001` PR.

**Recommendation for the next `PACKAGE-POWER-400-001` PR.** Land
**the BOM cross-check plus the `S360-400` `schematic_status:
verified` JSON promotion (separate PR) plus the package header
reconciliation plus the catalog `description` reconciliation as a
single atomic slice**, not as a comment-only cleanup alone.
Details recorded at
[`docs/hardware/s360-400-r4-power.md` §2026-05-19 — PACKAGE-POWER-400-001 investigation pass](hardware/s360-400-r4-power.md#2026-05-19--package-power-400-001-investigation-pass-deferred-preconditions-still-open).

**Queue effect.**

- `PACKAGE-POWER-400-001` is now **investigated and deferred** in
  the [`UPCOMING_PR.md`](../UPCOMING_PR.md) active queue
  (entry #4), blocked on the five preconditions above.
- `PRODUCT-POWER-400-001`, `WEBFLASH-POWER-400-001`,
  `RELEASE-POWER-400-001`, and `WF-IMPORT-POWER-400-001`
  (cross-repo) stay **blocked** behind `PACKAGE-POWER-400-001`
  and `COMPLIANCE-001`.
- `CORE-ABSTRACT-BUS-001B` is recorded as **PR #519** in the
  [`UPCOMING_PR.md`](../UPCOMING_PR.md) Completed / merged PRs
  table. Per the
  [§CORE-ABSTRACT-BUS-001B update](#core-abstract-bus-001b-update-2026-05-19--docs-only-investigation-pass)
  entry, `001B` stays at queue entry #3, blocked on its own four
  preconditions, and independent of `001A` / `001C` ordering.
- `CORE-ABSTRACT-BUS-001C` stays at the top of the active queue
  (entry #1), blocked on its own six preconditions per the
  2026-05-19 `001C` investigation pass merged as PR #518.
- `CORE-ABSTRACT-BUS-001A` stays blocked behind `001C`.
- `PACKAGE-PWM-001` / `PACKAGE-DAC-001` stay blocked behind
  `001B` implementation + their own evidence gates.
- `PACKAGE-RELAY-001` and downstream relay slices stay blocked
  behind `001A` (which is itself blocked behind `001C`).
- `PACKAGE-POE-410-001` / `PRODUCT-POE-410-001` /
  `WEBFLASH-POE-410-001` / `RELEASE-POE-410-001` /
  `WF-IMPORT-POE-410-001` stay blocked behind their own evidence
  gates (BOM cross-check, `S360-410 schematic_status: verified`
  JSON PR, HW-002 OQ#6 / `S360-100-BENCH-001` J2-harness closure,
  package-header reconciliation).
- `PACKAGE-TRIAC-001` / `PRODUCT-TRIAC-002` / `WF-TRIAC-001` /
  `RELEASE-TRIAC-001` / `WF-IMPORT-TRIAC-001` stay blocked behind
  HW-005 / `HW-PINMAP-320-FOLLOWUP` / COMPLIANCE-001.

**What this update does *not* do.** Adds **no** package YAML,
product YAML, WebFlash wrapper, JSON catalog change, script,
test, workflow, component, include, firmware artifact, manifest,
GitHub Release, tag, WebFlash import, or kit edit. Does **not**
edit
[`packages/hardware/power_240v.yaml`](../packages/hardware/power_240v.yaml)
(stays byte-identical to PR #515 — no comment-only edits; the
stale `HLK-PM01 or similar` header at line 7, the
`100-240V AC, 50/60Hz` input claim at line 7, the
`5V DC, 2A (10W)` output claim at line 8, the `3000VAC`
isolation claim at line 9, the `Overcurrent, overvoltage,
short-circuit` protection text at line 10, and the recommended
`1A` AC-input fusing line at line 15 are all preserved); does
**not** edit
[`config/hardware-catalog.json`](../config/hardware-catalog.json)
(`S360-400` row stays byte-identical to PR #515 — no
`schematic_status` promotion, no `schematic_file` set, no
`description` edit); does **not** edit
[`config/product-catalog.json`](../config/product-catalog.json)
(the four `legacy-compatible` `*-pwr` Core variants
`sense360-core-c-pwr.yaml` / `sense360-core-w-pwr.yaml` /
`sense360-core-v-c-pwr.yaml` / `sense360-core-v-w-pwr.yaml`
stay `legacy-compatible` and `webflash_build_matrix: false`);
does **not** edit
[`config/webflash-builds.json`](../config/webflash-builds.json)
(no `PWR`-bearing build); does **not** edit
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
(`PWR` stays reserved in `canonical_power` with no
`webflash_build_matrix: true` entry); does **not** edit any
product YAML under [`products/`](../products/) or any WebFlash
wrapper under [`products/webflash/`](../products/webflash/);
does **not** edit
[`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
(COMPLIANCE-001 unchanged; last re-check PR #506); does **not**
edit
[`docs/hardware/schematics/S360-400-R4.pdf`](hardware/schematics/S360-400-R4.pdf)
or
[`docs/hardware/artifacts/S360-400-R4.md`](hardware/artifacts/S360-400-R4.md)
(both stay byte-identical to HW-ASSETS-400 / PR #514). No
precondition is closed by this pass. Specifically: does **not**
advance `PACKAGE-POWER-400-001`, `PRODUCT-POWER-400-001`,
`WEBFLASH-POWER-400-001`, `RELEASE-POWER-400-001`, or
`WF-IMPORT-POWER-400-001`; does **not** advance
`PACKAGE-POE-410-001`, `PRODUCT-POE-410-001`,
`WEBFLASH-POE-410-001`, or `RELEASE-POE-410-001`; does **not**
advance `PACKAGE-RELAY-001`, `PRODUCT-RELAY-001`,
`WEBFLASH-RELAY-001`, `RELEASE-RELAY-001`, or
`WF-IMPORT-RELAY-001`; does **not** advance `PACKAGE-PWM-001`,
`PRODUCT-PWM-001`, `WEBFLASH-PWM-001`, or `RELEASE-PWM-001`;
does **not** advance `PACKAGE-DAC-001`, `PRODUCT-DAC-001`,
`WEBFLASH-DAC-001`, or `RELEASE-DAC-001`; does **not** advance
`PACKAGE-TRIAC-001`, `PRODUCT-TRIAC-002`, `WF-TRIAC-001`,
`RELEASE-TRIAC-001`, or `WF-IMPORT-TRIAC-001`; does **not**
advance `CORE-ABSTRACT-BUS-001A`, `CORE-ABSTRACT-BUS-001B`, or
`CORE-ABSTRACT-BUS-001C`; does **not** close
`S360-100-BENCH-001`, `HW-PINMAP-310-FOLLOWUP`,
`HW-PINMAP-311-FOLLOWUP`, `HW-PINMAP-312-FOLLOWUP`,
`HW-PINMAP-320-FOLLOWUP`, `HW-PINMAP-400-FOLLOWUP`,
`HW-PINMAP-410-FOLLOWUP`, `COMPLIANCE-001`, or
`S360-300-BENCH-001`; does **not** unblock FanTRIAC (HW-005
stays a separate gate); does **not** change the Release-One
configuration (`Ceiling-POE-VentIQ-RoomIQ`, version `1.0.0`,
channel `stable`, artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
`v1.0.0`); does **not** change the LED preview entry
(`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`,
`channel: preview`, artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`);
does **not** change `REQUIRED_CONFIGS` or kits; does **not**
promote any `schematic_status`; does **not** set any
`schematic_file`; does **not** claim any hardware-verified
evidence; does **not** claim that any BOM / silkscreen / PCB /
creepage / clearance / bench / thermal / EMI / compliance
evidence exists; does **not** make any CE / UKCA / FCC / UL /
LVD / EMC / RoHS / IEC claim.

The only files this update touches are this
`PACKAGE-POWER-400-001 update` section in
`docs/cleanup-audit.md`, the new
`### 2026-05-19 — PACKAGE-POWER-400-001 investigation pass`
subsection plus the matching audit-log table row in
[`docs/hardware/s360-400-r4-power.md`](hardware/s360-400-r4-power.md),
the investigation-outcome cross-link addendums in
[`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
and
[`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md),
and the queue refresh in
[`UPCOMING_PR.md`](../UPCOMING_PR.md) (`CORE-ABSTRACT-BUS-001B`
recorded as PR #519 in the Completed / merged PRs table,
current-queue-summary updated, active-queue entry #4
`PACKAGE-POWER-400-001` annotated with the investigation
outcome, new entry added under §Recently uploaded evidence for
"No new evidence committed for `PACKAGE-POWER-400-001`
preconditions").

**Next `PACKAGE-POWER-400-001` audit-log trigger.** The next
audit-log entry against this slice should appear when one of the
five preconditions above lands or when the next implementation
PR makes a `PACKAGE-POWER-400-001` package YAML / catalog
`description` / JSON `schematic_status` edit. Until then, the
next audit-log entry should report the same
`PACKAGE-POWER-400-001 investigation pass — preconditions still
open` outcome with the new inspection date.

## PRODUCT-POWER-400-001 update (2026-05-19 — docs-only investigation pass)

This update records the 2026-05-19 docs-only investigation pass
against `PRODUCT-POWER-400-001` (the S360-400 PWR-240V product
YAML / catalog slice). The upstream `PACKAGE-POWER-400-001`
investigation pass merged earlier the same day as **PR #520**
(docs-only Path A deferral) and is recorded above at
[§PACKAGE-POWER-400-001 update](#package-power-400-001-update-2026-05-19--docs-only-investigation-pass);
`PACKAGE-POWER-400-001` is the named immediate gate for
`PRODUCT-POWER-400-001` per
[`docs/product-readiness-matrix.md` Follow-up PR sequence](product-readiness-matrix.md#follow-up-pr-sequence),
and the package slice is **not** advanced by PR #520 — the
package YAML reconciliation, the catalog `description`
reconciliation, the `S360-400` `schematic_status: verified` JSON
promotion, and the BOM citation that PR #520 enumerated as the
required atomic slice all remain owed to a future
evidence-bearing `PACKAGE-POWER-400-001` PR.

**Outcome — Path A docs-only investigation / deferral.**
`PRODUCT-POWER-400-001` is **confirmed deferred at the
implementation layer.** Six preconditions remain open. No new
package, product, WebFlash, build, release, compliance, JSON
catalog, test, script, workflow, component, include, firmware,
or manifest evidence has arrived since PR #520; the live state
of every product / WebFlash / release surface that
`PRODUCT-POWER-400-001` would touch stays byte-identical to PR
#520.

**Findings recorded.** Re-verified against the live files
(byte-identical to the post-PR #520 inventory):

- **No S360-400-explicit / `PWR`-bearing WebFlash-shippable
  product YAML exists** under
  [`products/`](../products/) or
  [`products/webflash/`](../products/webflash/). The only
  `pwr`-bearing products are the four `legacy-compatible` Core
  variants
  [`products/sense360-core-c-pwr.yaml`](../products/sense360-core-c-pwr.yaml),
  [`products/sense360-core-w-pwr.yaml`](../products/sense360-core-w-pwr.yaml),
  [`products/sense360-core-v-c-pwr.yaml`](../products/sense360-core-v-c-pwr.yaml),
  and
  [`products/sense360-core-v-w-pwr.yaml`](../products/sense360-core-v-w-pwr.yaml),
  each consuming the logical
  [`packages/hardware/power_240v.yaml`](../packages/hardware/power_240v.yaml)
  via `power_config: !include ../packages/hardware/power_240v.yaml`.
  Those four products are **not** S360-400-specific
  product-readiness evidence — the package itself binds no GPIO
  / I²C / UART / SPI / DAC and emits diagnostic sensors only
  (`Supply Voltage` / `Power Source` / `Power Configuration` /
  `AC Power Connected`); its header carries the stale
  `HLK-PM01 or similar` AC/DC part hint plus unverified input /
  output / isolation / protection / fusing claims that remain
  BOM-bound.
- [`config/product-catalog.json`](../config/product-catalog.json)
  contains **no S360-400-specific product**. The four
  `legacy-compatible` `*-pwr` Core variant rows
  (`sense360-core-c-pwr`, `sense360-core-w-pwr`,
  `sense360-core-v-c-pwr`, `sense360-core-v-w-pwr`) each carry
  `status: legacy-compatible`, `webflash_build_matrix: false`,
  no `config_string`, no `webflash_wrapper`, and no
  `artifact_name`. The two shipping entries
  (`Ceiling-POE-VentIQ-RoomIQ` `status: production` /
  `channel: stable` / version `1.0.0` / artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, and
  `Ceiling-POE-VentIQ-RoomIQ-LED` `status: preview` /
  `channel: preview` / version `1.0.0` / artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`)
  and the FanTRIAC blocked-reference entry
  (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` `status: blocked` /
  `blocker: HW-005` / `webflash_build_matrix: false`) are
  unchanged.
- [`config/webflash-builds.json`](../config/webflash-builds.json)
  contains **no `PWR` build** — only Release-One
  `Ceiling-POE-VentIQ-RoomIQ` (stable) and
  `Ceiling-POE-VentIQ-RoomIQ-LED` (preview).
- [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  reserves `PWR` in `canonical_power: ["USB", "POE", "PWR"]`
  but **no `webflash_build_matrix: true` row consumes it**.
  `release_one_required_configs` stays
  `["Ceiling-POE-VentIQ-RoomIQ"]`.
- [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  `S360-400` row at lines 102–110 stays byte-identical to PR
  #520: `description: Mains to 5V using HLK-5M05.` (line 109),
  `schematic_status: cataloged_unverified` (line 110), and no
  `schematic_file`. The three-way AC/DC part-identity
  disagreement — catalog `HLK-5M05` vs package header
  `HLK-PM01 or similar` (line 7 of
  [`packages/hardware/power_240v.yaml`](../packages/hardware/power_240v.yaml))
  vs HW-ASSETS-400 schematic `PS1 = HLK-10M05` — stays
  unresolved and BOM-bound.
- [`tests/test_hardware_catalog.py`](../tests/test_hardware_catalog.py)
  line 53 still asserts
  `EXPECTED_STILL_UNVERIFIED_SKUS = frozenset({"S360-320",
  "S360-400"})`, actively enforcing the `S360-400`
  `cataloged_unverified` / no-`schematic_file` state.
- [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
  COMPLIANCE-001 `S360-400` slice last re-checked at PR #506;
  remains open / not cleared. `S360-400` is one of two
  mains-voltage SKUs in scope.
- [`docs/hardware/s360-400-r4-power.md`](hardware/s360-400-r4-power.md)
  top-line status stays `partial — schematic evidence
  available; package reconciliation, BOM, silkscreen,
  creepage/clearance, and COMPLIANCE-001 pending`; the
  per-board `### 2026-05-19 — PACKAGE-POWER-400-001
  investigation pass (deferred; preconditions still open)`
  entry remains the most recent audit-log entry against this
  board.
- The
  [`power_240v.yaml` row in package-readiness-matrix.md](hardware/package-readiness-matrix.md#power_240vyaml--s360-400)
  stays `schematic-evidence-pending` +
  `needs-package-reconciliation` + `timing/compliance-pending`
  (compliance-gated).

**Three-way AC/DC part-identity disagreement stays unresolved and
BOM-bound** (same as PR #520):

- catalog
  [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  line 109 `Mains to 5V using HLK-5M05.`
- package header
  [`packages/hardware/power_240v.yaml`](../packages/hardware/power_240v.yaml)
  line 7 `HLK-PM01 or similar`
- schematic
  [`docs/hardware/schematics/S360-400-R4.pdf`](hardware/schematics/S360-400-R4.pdf)
  (HW-ASSETS-400 / PR #514) `PS1 = HLK-10M05`

**Open preconditions (carried forward).**

1. **`PACKAGE-POWER-400-001` implementation slice has not
   landed.** Only the docs-only investigation pass merged as
   PR #520. The package YAML header reconciliation, the catalog
   `description` reconciliation, the `S360-400`
   `schematic_status: verified` JSON promotion, and the BOM
   citation that PR #520 enumerated as the required atomic
   slice all remain owed to a future evidence-bearing
   `PACKAGE-POWER-400-001` PR. Per
   [`docs/product-readiness-matrix.md` Follow-up PR sequence](product-readiness-matrix.md#follow-up-pr-sequence)
   the `PRODUCT-POWER-400-001` row is explicitly gated on
   "`PACKAGE-POWER-400-001` landed".
2. **BOM cross-check missing.** Same five-component gap PR #520
   recorded for the package slice: no BOM line item with
   manufacturer + part number + revision for `PS1` (so the
   three-way `HLK-5M05` / `HLK-PM01 or similar` / `HLK-10M05`
   disagreement stays unresolved), and no BOM lines for
   `F1 A250-1200` / `RV1 10D391K` / `C1 470nF` / `C5..C8` /
   `J1` / `J2`.
3. **`S360-400` `schematic_status: verified` JSON PR not
   landed.** Separate JSON-only PR after BOM + silkscreen
   evidence land.
4. **`COMPLIANCE-001` `S360-400` slice still open.** Last
   re-checked PR #506; the mains-voltage UK / EU assessment
   at
   [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
   is not cleared. Per the
   [Follow-up PR sequence](product-readiness-matrix.md#follow-up-pr-sequence)
   `PRODUCT-POWER-400-001` is additionally gated on
   "`COMPLIANCE-001` `S360-400` slice closed".
5. **Package / catalog reconciliation owed to
   `PACKAGE-POWER-400-001`.** The three-way AC/DC part-identity
   disagreement and the input / output / isolation / protection
   / fusing header text in
   [`packages/hardware/power_240v.yaml`](../packages/hardware/power_240v.yaml)
   remain unresolved and BOM-bound; the catalog `description:
   Mains to 5V using HLK-5M05.` at
   [`config/hardware-catalog.json`](../config/hardware-catalog.json)
   line 109 remains uncorrected. A product YAML cannot rely on
   any of those claims while they remain BOM-bound.
6. **Product-onboarding approval missing.** Per the
   [Core rule](product-readiness-matrix.md#core-rule),
   adding a product YAML requires (a) every consumed package to
   be `ready-for-package-change` —
   [`power_240v.yaml`](../packages/hardware/power_240v.yaml)
   stays `schematic-evidence-pending` +
   `needs-package-reconciliation` +
   `timing/compliance-pending`; (b) the combination to clear
   the WebFlash compatibility grammar in
   [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
   — `PWR` is reserved in `canonical_power` but no
   `webflash_build_matrix: true` row consumes it, and the
   `airiq_and_ventiq_mutually_exclusive` rule plus the
   `forbidden_tokens` list constrain any candidate
   `Ceiling-PWR-{AIR}-{ROOM}` shape; and (c) the
   [`docs/product-onboarding.md`](product-onboarding.md) safe
   sequence to be followed end-to-end. None of the three has
   been satisfied for `PRODUCT-POWER-400-001`.

**Why Path B and Path C are not taken now.**

- **Path B (documentation / catalog-note-only cleanup)** is not
  useful right now because the readiness matrices
  ([`docs/product-readiness-matrix.md` §PWR-240V / S360-400](product-readiness-matrix.md#pwr-240v--s360-400),
  [`docs/webflash-exposure-readiness-matrix.md` §Power / S360-400 WebFlash posture](webflash-exposure-readiness-matrix.md#power--s360-400-webflash-posture),
  [`docs/release-artifact-readiness-matrix.md` §Power / S360-400 release posture](release-artifact-readiness-matrix.md#power--s360-400-release-posture))
  already correctly classify the slice as `no product YAML` /
  `not-webflash-ready` / `not-release-ready`, and the
  `PRODUCT-POWER-400-001` Follow-up PR sequence row already
  names the package-gate. Any further documentation cleanup
  (for example, retiring the stale "(this PR; docs-only)" prose
  left over from HW-PINMAP-400-FOLLOWUP / PR #515 in the
  Follow-up owner cells of those matrix sections) belongs to a
  separate CLEANUP slice, not to `PRODUCT-POWER-400-001`. The
  legacy-compatible `*-pwr` Core variants
  ([`products/sense360-core-c-pwr.yaml`](../products/sense360-core-c-pwr.yaml),
  [`products/sense360-core-w-pwr.yaml`](../products/sense360-core-w-pwr.yaml),
  [`products/sense360-core-v-c-pwr.yaml`](../products/sense360-core-v-c-pwr.yaml),
  [`products/sense360-core-v-w-pwr.yaml`](../products/sense360-core-v-w-pwr.yaml))
  carry the same stale `HLK-PM01 or similar` reference in their
  own header comments, but rewriting those comments before BOM
  evidence lands would substitute one unsourced claim for
  another and would muddy the eventual coordinated
  `PACKAGE-POWER-400-001` PR's scope (the same reasoning PR
  #515 recorded for the package header).
- **Path C (implementation)** is unsafe right now because every
  gate is open. Adding a canonical S360-400 / `PWR`-bearing
  product YAML while
  [`packages/hardware/power_240v.yaml`](../packages/hardware/power_240v.yaml)
  carries `schematic-evidence-pending` +
  `needs-package-reconciliation` +
  `timing/compliance-pending` would break the
  [`docs/product-readiness-matrix.md` Core rule](product-readiness-matrix.md#core-rule)
  ("Product YAML changes are allowed only when (a) every
  package the product would consume is
  `ready-for-package-change` …"). Adding a `webflash_wrapper`,
  catalog `webflash_build_matrix: true`, build-matrix row,
  release artifact, kit entry, `REQUIRED_CONFIGS` membership,
  or release tag for a mains-voltage path while
  `COMPLIANCE-001` `S360-400` is open would additionally
  violate the
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
  gate.

**Recommendation for the next `PRODUCT-POWER-400-001` PR.** Land
**the canonical S360-400 / `PWR`-bearing product YAML under
[`products/`](../products/) (candidate shape
`Ceiling-PWR-{AIR}-{ROOM}`; AirIQ ↔ VentIQ mutex honoured) +
the matching entry in
[`config/product-catalog.json`](../config/product-catalog.json) +
the legacy-compatible `*-pwr` Core variant relationship decision
(retain / migrate / coexist) as a single atomic slice**, after
`PACKAGE-POWER-400-001` implementation, the `S360-400`
`schematic_status: verified` JSON PR, the `COMPLIANCE-001`
`S360-400` slice, and product-onboarding approval per
[`docs/product-onboarding.md`](product-onboarding.md) all land.
**Does not** add a WebFlash wrapper, catalog
`webflash_build_matrix: true` flip, build-matrix entry, release
artifact, kit entry, or `REQUIRED_CONFIGS` membership — those
belong to `WEBFLASH-POWER-400-001`, `RELEASE-POWER-400-001`, and
`WF-IMPORT-POWER-400-001` (cross-repo) respectively, and are
additionally gated by `COMPLIANCE-001` `S360-400` slice closure.

**Queue effect.**

- `PRODUCT-POWER-400-001` is now **investigated and deferred** in
  the [`UPCOMING_PR.md`](../UPCOMING_PR.md) active queue
  (entry #4), blocked on the six preconditions above.
- `PACKAGE-POWER-400-001` is recorded as **PR #520** in the
  [`UPCOMING_PR.md`](../UPCOMING_PR.md) Completed / merged PRs
  table. Per the
  [§PACKAGE-POWER-400-001 update](#package-power-400-001-update-2026-05-19--docs-only-investigation-pass)
  entry, `PACKAGE-POWER-400-001` stays blocked on its own five
  preconditions; the package slice is **not** advanced by PR
  #520.
- `WEBFLASH-POWER-400-001`, `RELEASE-POWER-400-001`, and
  `WF-IMPORT-POWER-400-001` (cross-repo) stay **blocked** behind
  `PRODUCT-POWER-400-001` and `COMPLIANCE-001`.
- `CORE-ABSTRACT-BUS-001C` stays at the top of the active queue
  (entry #1), blocked on its own six preconditions per the
  2026-05-19 `001C` investigation pass merged as PR #518.
- `CORE-ABSTRACT-BUS-001A` stays blocked behind `001C`.
- `CORE-ABSTRACT-BUS-001B` stays at queue entry #3, blocked on
  its own four preconditions per the 2026-05-19 `001B`
  investigation pass merged as PR #519.
- `PACKAGE-PWM-001` / `PACKAGE-DAC-001` stay blocked behind
  `001B` implementation + their own evidence gates.
- `PACKAGE-RELAY-001` and downstream relay slices stay blocked
  behind `001A` (which is itself blocked behind `001C`).
- `PACKAGE-POE-410-001` / `PRODUCT-POE-410-001` /
  `WEBFLASH-POE-410-001` / `RELEASE-POE-410-001` /
  `WF-IMPORT-POE-410-001` stay blocked behind their own evidence
  gates (BOM cross-check, `S360-410 schematic_status: verified`
  JSON PR, HW-002 OQ#6 / `S360-100-BENCH-001` J2-harness closure,
  package-header reconciliation).
- `PACKAGE-TRIAC-001` / `PRODUCT-TRIAC-002` / `WF-TRIAC-001` /
  `RELEASE-TRIAC-001` / `WF-IMPORT-TRIAC-001` stay blocked behind
  HW-005 / `HW-PINMAP-320-FOLLOWUP` / COMPLIANCE-001.

**What this update does *not* do.** Adds **no** package YAML,
product YAML, WebFlash wrapper, JSON catalog change, script,
test, workflow, component, include, firmware artifact, manifest,
GitHub Release, tag, WebFlash import, or kit edit. Does **not**
edit
[`packages/hardware/power_240v.yaml`](../packages/hardware/power_240v.yaml)
(byte-identical to PR #520 / PR #515 state — the stale
`HLK-PM01 or similar` header at line 7, the `100-240V AC,
50/60Hz` input claim at line 7, the `5V DC, 2A (10W)` output
claim at line 8, the `3000VAC` isolation claim at line 9, the
`Overcurrent, overvoltage, short-circuit` protection text at
line 10, the recommended `1A` AC-input fusing line at line 15,
the `substitutions: power_source: "240v_ac"` at line 29, the
`globals: power_source_type` at lines 32–36, the template
diagnostic sensors `Supply Voltage` / `Power Source` /
`Power Configuration` / `AC Power Connected`, and the logger
config are all preserved); does **not** edit any other file
under [`packages/`](../packages/); does **not** edit
[`config/hardware-catalog.json`](../config/hardware-catalog.json)
(`S360-400` row stays byte-identical — no `schematic_status`
promotion, no `schematic_file` set, no `description` edit); does
**not** edit
[`config/product-catalog.json`](../config/product-catalog.json)
(no S360-400-specific product added; the four `legacy-compatible`
`*-pwr` Core variants stay `legacy-compatible` /
`webflash_build_matrix: false`; the two shipping entries and the
FanTRIAC blocked-reference entry stay verbatim; the
`lifecycle_statuses` enum is unchanged); does **not** edit
[`config/webflash-builds.json`](../config/webflash-builds.json)
(no `PWR`-bearing build added); does **not** edit
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
(`PWR` stays reserved in `canonical_power` with no
`webflash_build_matrix: true` entry; `canonical_modules` /
`canonical_mounting` / `forbidden_tokens` / mutex rules /
`release_one_required_configs` / `artifact_pattern` /
`allowed_channels` / `production_channel` /
`rescue_config_string` all unchanged); does **not** edit any
product YAML under [`products/`](../products/) (including the
four legacy-compatible `*-pwr` Core variants
[`sense360-core-c-pwr.yaml`](../products/sense360-core-c-pwr.yaml),
[`sense360-core-w-pwr.yaml`](../products/sense360-core-w-pwr.yaml),
[`sense360-core-v-c-pwr.yaml`](../products/sense360-core-v-c-pwr.yaml),
and
[`sense360-core-v-w-pwr.yaml`](../products/sense360-core-v-w-pwr.yaml));
does **not** edit any WebFlash wrapper under
[`products/webflash/`](../products/webflash/); does **not** edit
[`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
(COMPLIANCE-001 unchanged; last re-check PR #506); does **not**
edit
[`docs/hardware/s360-400-r4-power.md`](hardware/s360-400-r4-power.md)
(byte-identical to PR #520 — the `### 2026-05-19 —
PACKAGE-POWER-400-001 investigation pass (deferred;
preconditions still open)` entry stays the most recent
audit-log entry); does **not** edit
[`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
(cross-link addendums for the package slice already in place
from PR #520); does **not** edit
[`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
(cross-link addendums for the package slice already in place
from PR #520); does **not** edit
[`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
(`S360-400` row stays correct); does **not** edit
[`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md)
(`S360-400` snapshot row stays `cataloged-unverified` /
`design-pending` / `compliance-gated`); does **not** edit
[`docs/hardware/artifacts/S360-400-R4.md`](hardware/artifacts/S360-400-R4.md)
or
[`docs/hardware/schematics/S360-400-R4.pdf`](hardware/schematics/S360-400-R4.pdf)
(both byte-identical to HW-ASSETS-400 / PR #514). No precondition
is closed by this pass. Specifically: does **not** advance
`PRODUCT-POWER-400-001`, `PACKAGE-POWER-400-001`,
`WEBFLASH-POWER-400-001`, `RELEASE-POWER-400-001`, or
`WF-IMPORT-POWER-400-001`; does **not** advance
`PACKAGE-POE-410-001`, `PRODUCT-POE-410-001`,
`WEBFLASH-POE-410-001`, or `RELEASE-POE-410-001`; does **not**
advance `PACKAGE-RELAY-001`, `PRODUCT-RELAY-001`,
`WEBFLASH-RELAY-001`, `RELEASE-RELAY-001`, or
`WF-IMPORT-RELAY-001`; does **not** advance `PACKAGE-PWM-001`,
`PRODUCT-PWM-001`, `WEBFLASH-PWM-001`, or `RELEASE-PWM-001`;
does **not** advance `PACKAGE-DAC-001`, `PRODUCT-DAC-001`,
`WEBFLASH-DAC-001`, or `RELEASE-DAC-001`; does **not** advance
`PACKAGE-TRIAC-001`, `PRODUCT-TRIAC-002`, `WF-TRIAC-001`,
`RELEASE-TRIAC-001`, or `WF-IMPORT-TRIAC-001`; does **not**
advance `CORE-ABSTRACT-BUS-001A`, `CORE-ABSTRACT-BUS-001B`, or
`CORE-ABSTRACT-BUS-001C`; does **not** close
`S360-100-BENCH-001`, `HW-PINMAP-310-FOLLOWUP`,
`HW-PINMAP-311-FOLLOWUP`, `HW-PINMAP-312-FOLLOWUP`,
`HW-PINMAP-320-FOLLOWUP`, `HW-PINMAP-400-FOLLOWUP`,
`HW-PINMAP-410-FOLLOWUP`, `COMPLIANCE-001`, or
`S360-300-BENCH-001`; does **not** unblock FanTRIAC (HW-005
stays a separate gate); does **not** change the Release-One
configuration (`Ceiling-POE-VentIQ-RoomIQ`, version `1.0.0`,
channel `stable`, artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
`v1.0.0`); does **not** change the LED preview entry
(`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`,
`channel: preview`, artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`);
does **not** change `REQUIRED_CONFIGS` or kits; does **not**
promote any `schematic_status`; does **not** set any
`schematic_file`; does **not** claim any hardware-verified
evidence; does **not** claim that any BOM / silkscreen / PCB /
creepage / clearance / bench / thermal / EMI / compliance
evidence exists; does **not** make any CE / UKCA / FCC / UL /
LVD / EMC / RoHS / IEC claim.

The only files this update touches are this
`PRODUCT-POWER-400-001 update` section in
`docs/cleanup-audit.md`, cross-link addendums in
[`docs/product-readiness-matrix.md`](product-readiness-matrix.md)
§PWR-240V / S360-400 and §Follow-up PR sequence,
[`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md)
§Power / S360-400 WebFlash posture, and
[`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
§Power / S360-400 release posture, and the queue refresh in
[`UPCOMING_PR.md`](../UPCOMING_PR.md) (`PACKAGE-POWER-400-001`
recorded as PR #520 in the Completed / merged PRs table,
current-queue-summary updated with the PRODUCT-POWER-400-001
investigation pass bullet, active-queue entry #4 swapped from
`PACKAGE-POWER-400-001` to `PRODUCT-POWER-400-001` and annotated
with the investigation outcome, subsequent entries renumbered,
new entry added under §Recently uploaded evidence for "No new
evidence committed for `PRODUCT-POWER-400-001` preconditions").

**Next `PRODUCT-POWER-400-001` audit-log trigger.** The next
audit-log entry against this slice should appear when one of the
six preconditions above lands or when the next implementation
PR makes a `PRODUCT-POWER-400-001` product YAML / catalog entry
edit. Until then, the next audit-log entry should report the
same `PRODUCT-POWER-400-001 investigation pass — preconditions
still open` outcome with the new inspection date.

## WEBFLASH-POWER-400-001 update (2026-05-19 — docs-only investigation pass)

This update records the 2026-05-19 docs-only investigation pass
against `WEBFLASH-POWER-400-001` (the S360-400 PWR-240V WebFlash
wrapper / catalog `webflash_build_matrix: true` flip / build-matrix
row slice). The upstream `PRODUCT-POWER-400-001` investigation
pass merged earlier the same day as **PR #521** (docs-only Path A
deferral) and is recorded above at
[§PRODUCT-POWER-400-001 update](#product-power-400-001-update-2026-05-19--docs-only-investigation-pass);
`PRODUCT-POWER-400-001` is the named immediate gate for
`WEBFLASH-POWER-400-001` per
[`docs/webflash-exposure-readiness-matrix.md` Follow-up PR sequence](webflash-exposure-readiness-matrix.md#follow-up-pr-sequence),
and the product slice is **not** advanced by PR #521 — the
canonical S360-400 / `PWR`-bearing product YAML, the matching
`config/product-catalog.json` entry, and the legacy-compatible
`*-pwr` Core variant relationship decision that PR #521 enumerated
as the required atomic slice all remain owed to a future
evidence-bearing `PRODUCT-POWER-400-001` PR.

**Outcome — Path A docs-only investigation / deferral.**
`WEBFLASH-POWER-400-001` is **confirmed deferred at the
implementation layer** and **merged as PR #522** on 2026-05-19.
Five preconditions remain open. No new package, product, WebFlash,
build, release, compliance, JSON catalog, test, script, workflow,
component, include, firmware, or manifest evidence has arrived
since PR #521; the live state of every WebFlash surface that
`WEBFLASH-POWER-400-001` would touch stays byte-identical to PR
#521.
wrapper / catalog / build slice). The upstream
`PRODUCT-POWER-400-001` investigation pass merged earlier the
same day as **PR #521** (docs-only Path A deferral) and is
recorded above at
[§PRODUCT-POWER-400-001 update](#product-power-400-001-update-2026-05-19--docs-only-investigation-pass);
`PRODUCT-POWER-400-001` is the named immediate gate for
`WEBFLASH-POWER-400-001` per the
[`docs/webflash-exposure-readiness-matrix.md` wrapper / catalog / build sub-gate table](webflash-exposure-readiness-matrix.md),
and the product slice is **not** advanced by PR #521 — the
canonical S360-400 / `PWR`-bearing product YAML under
[`../products/`](../products/), the matching entry in
[`../config/product-catalog.json`](../config/product-catalog.json),
and the legacy-compatible `*-pwr` Core variant relationship
decision that PR #521 enumerated as the required atomic slice
all remain owed to a future evidence-bearing
`PRODUCT-POWER-400-001` PR.

**Outcome — Path A docs-only investigation / deferral.**
`WEBFLASH-POWER-400-001` is **confirmed deferred at the
implementation layer.** Eight preconditions remain open. No new
package, product, WebFlash, build, release, compliance, JSON
catalog, test, script, workflow, component, include, firmware,
or manifest evidence has arrived since PR #521; the live state
of every WebFlash wrapper / catalog / build / release surface
that `WEBFLASH-POWER-400-001` would touch stays byte-identical
to PR #521.

**Findings recorded.** Re-verified against the live files
(byte-identical to the post-PR #521 inventory):

- **No S360-400 WebFlash wrapper exists** under
  [`products/webflash/`](../products/webflash/). The directory
  contains exactly three wrappers, all PoE-based and unchanged:
  [`ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml),
  [`ceiling-poe-ventiq-roomiq-led.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq-led.yaml),
  and
  [`ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml).
- [`config/webflash-builds.json`](../config/webflash-builds.json)
  contains **no `PWR` build** — only Release-One
  `Ceiling-POE-VentIQ-RoomIQ` (stable) and
  `Ceiling-POE-VentIQ-RoomIQ-LED` (preview); no new entry for a
  PWR-240V product.
- [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  reserves `PWR` in `canonical_power: ["USB", "POE", "PWR"]` but
  **no `webflash_build_matrix: true` row consumes it**.
  `release_one_required_configs` stays
  `["Ceiling-POE-VentIQ-RoomIQ"]`. The
  `airiq_and_ventiq_mutually_exclusive` rule, the
  `forbidden_tokens` list, the `canonical_modules`, the
  `canonical_mounting`, the `artifact_pattern`, the
  `allowed_channels`, the `production_channel`, and the
  `rescue_config_string` all unchanged.
- [`config/product-catalog.json`](../config/product-catalog.json)
- **No S360-400-explicit / `PWR`-bearing WebFlash wrapper
  exists** under
  [`../products/webflash/`](../products/webflash/). The
  directory contains only three POE wrappers
  [`ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml),
  [`ceiling-poe-ventiq-roomiq-led.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq-led.yaml),
  and
  [`ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml);
  each wraps Release-One or the LED preview, not a PWR-240V
  product.
- **No S360-400-explicit / `PWR`-bearing WebFlash-shippable
  product YAML exists** under
  [`../products/`](../products/) for a WebFlash wrapper to
  wrap. The four `legacy-compatible` `*-pwr` Core variants
  [`../products/sense360-core-c-pwr.yaml`](../products/sense360-core-c-pwr.yaml),
  [`../products/sense360-core-w-pwr.yaml`](../products/sense360-core-w-pwr.yaml),
  [`../products/sense360-core-v-c-pwr.yaml`](../products/sense360-core-v-c-pwr.yaml),
  and
  [`../products/sense360-core-v-w-pwr.yaml`](../products/sense360-core-v-w-pwr.yaml)
  are pre-WebFlash YAMLs only and not WebFlash-shippable; they
  are not WebFlash exposure evidence.
- [`../config/webflash-builds.json`](../config/webflash-builds.json)
  contains **no `PWR` build**. The only two entries are
  Release-One `Ceiling-POE-VentIQ-RoomIQ` (`stable` / `v1.0.0` /
  artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`) and
  the LED preview `Ceiling-POE-VentIQ-RoomIQ-LED` (`preview` /
  `v1.0.0` / artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`).
- [`../config/product-catalog.json`](../config/product-catalog.json)
  contains **no S360-400-specific product**. The four
  `legacy-compatible` `*-pwr` Core variant rows
  (`sense360-core-c-pwr`, `sense360-core-w-pwr`,
  `sense360-core-v-c-pwr`, `sense360-core-v-w-pwr`) each carry
  `status: legacy-compatible`, `webflash_build_matrix: false`,
  no `config_string`, no `webflash_wrapper`, and no
  `artifact_name`. The two shipping entries
  (`Ceiling-POE-VentIQ-RoomIQ` `status: production` /
  `channel: stable` / version `1.0.0` / artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, and
  `Ceiling-POE-VentIQ-RoomIQ-LED` `status: preview` /
  `channel: preview` / version `1.0.0` / artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`)
  and the FanTRIAC blocked-reference entry
  (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` `status: blocked` /
  `blocker: HW-005` / `webflash_build_matrix: false`) are
  unchanged.
- [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  `channel: stable` and `Ceiling-POE-VentIQ-RoomIQ-LED`
  `status: preview` / `channel: preview`) and the FanTRIAC
  blocked-reference entry (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`
  `status: blocked` / `blocker: HW-005` /
  `webflash_build_matrix: false`) are unchanged.
- [`../config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  reserves `PWR` in `canonical_power: ["USB", "POE", "PWR"]`
  but **no `webflash_build_matrix: true` row consumes it**.
  Reservation of `PWR` is grammar-only and does **not** imply
  WebFlash exposure. `release_one_required_configs` stays
  `["Ceiling-POE-VentIQ-RoomIQ"]`; `canonical_modules`,
  `forbidden_tokens`, and the
  `airiq_and_ventiq_mutually_exclusive` rule are unchanged.
- [`../config/hardware-catalog.json`](../config/hardware-catalog.json)
  `S360-400` row at lines 102–110 stays byte-identical to PR
  #521: `description: Mains to 5V using HLK-5M05.` (line 109),
  `schematic_status: cataloged_unverified` (line 110), and no
  `schematic_file`. The three-way AC/DC part-identity
  disagreement (catalog `HLK-5M05` vs package header
  `HLK-PM01 or similar` vs schematic `PS1 = HLK-10M05`) stays
  unresolved and BOM-bound.
- [`tests/test_hardware_catalog.py`](../tests/test_hardware_catalog.py)
  disagreement — catalog `HLK-5M05` vs package header
  `HLK-PM01 or similar` (line 7 of
  [`../packages/hardware/power_240v.yaml`](../packages/hardware/power_240v.yaml))
  vs HW-ASSETS-400 schematic `PS1 = HLK-10M05` — stays
  unresolved and BOM-bound.
- [`../tests/test_hardware_catalog.py`](../tests/test_hardware_catalog.py)
  line 53 still asserts
  `EXPECTED_STILL_UNVERIFIED_SKUS = frozenset({"S360-320",
  "S360-400"})`, actively enforcing the `S360-400`
  `cataloged_unverified` / no-`schematic_file` state.
- [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py),
  [`tests/test_webflash_compatibility.py`](../tests/test_webflash_compatibility.py),
  and
  [`tests/test_webflash_artifact_naming.py`](../tests/test_webflash_artifact_naming.py)
  all enforce the existing two-build matrix; no test scaffold for
  a PWR-240V build has been added.
- [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
  COMPLIANCE-001 `S360-400` slice last re-checked at PR #506;
  remains open / not cleared. `S360-400` is one of two
  mains-voltage SKUs in scope.
- [`packages/hardware/power_240v.yaml`](../packages/hardware/power_240v.yaml)
  stays byte-identical to PR #515 / PR #520 / PR #521 state
  (stale `HLK-PM01 or similar` header at line 7; unverified
  input / output / isolation / protection / fusing claims;
  diagnostic template sensors; logger config; substitutions /
  globals all preserved).

**UX-class decision (standard preview-candidate vs advanced /
manual-warning) stays undecided.** Per the
[`docs/webflash-exposure-readiness-matrix.md` §Power / S360-400 WebFlash posture](webflash-exposure-readiness-matrix.md#power--s360-400-webflash-posture)
"Future exposure class (intent)" entry, the advanced /
manual-warning posture is **not** the default for PWR-240V; the
per-family `PRODUCT-POWER-400-001` slice compliance verdict
decides whether mains-voltage PWR-240V products are standard
preview-candidate, advanced / manual-warning-only, or both
depending on intended UX. `PRODUCT-POWER-400-001` is deferred and
the compliance verdict has not been rendered, so
`WEBFLASH-POWER-400-001` cannot set the UX class either.
- [`compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
  COMPLIANCE-001 `S360-400` slice last re-checked at PR #506;
  remains open / not cleared. `S360-400` is one of two
  mains-voltage SKUs in scope.
- **No release / build / artifact readiness exists for
  S360-400.** There is no `artifact_name`, no `.bin` artifact,
  no GitHub Release, no checksums, no proof, no WebFlash
  import. The candidate
  `Sense360-Ceiling-PWR-{AIR}-{ROOM}-v{VERSION}-{CHANNEL}.bin`
  pattern cannot be reified until `PRODUCT-POWER-400-001`
  lands a canonical product YAML with a decided
  `config_string`.
- The
  [`../docs/webflash-exposure-readiness-matrix.md` §Power / S360-400 WebFlash posture](webflash-exposure-readiness-matrix.md#power--s360-400-webflash-posture)
  stays `not-webflash-ready` / `no wrapper` / `no build-matrix
  row`; the
  [`../docs/release-artifact-readiness-matrix.md` §Power / S360-400 release posture](release-artifact-readiness-matrix.md#power--s360-400-release-posture)
  stays `not-release-ready` / `missing-build-matrix` /
  `missing-webflash-wrapper` / `missing-product-yaml` /
  `missing-package-readiness`.

**Open preconditions (carried forward).**

1. **`PRODUCT-POWER-400-001` implementation slice has not
   landed.** Only the docs-only investigation pass merged as
   PR #521. The canonical S360-400 / `PWR`-bearing product YAML,
   the matching `config/product-catalog.json` entry, and the
   legacy-compatible `*-pwr` Core variant relationship decision
   that PR #521 enumerated as the required atomic slice all
   remain owed to a future evidence-bearing
   `PRODUCT-POWER-400-001` PR. Per
   [`docs/webflash-exposure-readiness-matrix.md` Follow-up PR sequence](webflash-exposure-readiness-matrix.md#follow-up-pr-sequence)
   the `WEBFLASH-POWER-400-001` row is explicitly gated on
   "`PRODUCT-POWER-400-001` landed + `COMPLIANCE-001` S360-400
   slice closed".
2. **`PACKAGE-POWER-400-001` implementation slice has not
   landed.** Only the docs-only investigation pass merged as
   PR #520. The package YAML header reconciliation, the catalog
   `description` reconciliation, the `S360-400`
   `schematic_status: verified` JSON promotion, and the BOM
   citation that PR #520 enumerated as the required atomic
   slice all remain owed to a future evidence-bearing
   `PACKAGE-POWER-400-001` PR. A WebFlash wrapper cannot be
   added while the consumed package stays
   `schematic-evidence-pending` + `needs-package-reconciliation`
   + `timing/compliance-pending`.
3. **`S360-400` `schematic_status: verified` JSON PR not
   landed.** Separate JSON-only PR after BOM + silkscreen
   evidence land.
4. **`COMPLIANCE-001` `S360-400` slice still open.** Last
   re-checked PR #506; the mains-voltage UK / EU assessment at
   [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
   is not cleared. Per the
   [Follow-up PR sequence](webflash-exposure-readiness-matrix.md#follow-up-pr-sequence)
   `WEBFLASH-POWER-400-001` is additionally gated on
   "`COMPLIANCE-001` S360-400 slice closed".
5. **UX-class decision pending.** Standard preview-candidate vs
   advanced / manual-warning posture has not been chosen.
   Decision belongs to `PRODUCT-POWER-400-001` (compliance
   verdict) + `WEBFLASH-POWER-400-001` (exposure class). Cannot
   be made while COMPLIANCE-001 is open and PRODUCT-POWER-400-001
   is unimplemented.

**Why Path B and Path C are not taken now.**

- **Path B (notes-only catalog-classification cleanup)** is not
  useful right now because the readiness matrices
  ([`docs/webflash-exposure-readiness-matrix.md` §Power / S360-400 WebFlash posture](webflash-exposure-readiness-matrix.md#power--s360-400-webflash-posture),
  [`docs/release-artifact-readiness-matrix.md` §Power / S360-400 release posture](release-artifact-readiness-matrix.md#power--s360-400-release-posture),
  [`docs/product-readiness-matrix.md` §PWR-240V / S360-400](product-readiness-matrix.md#pwr-240v--s360-400))
  already correctly classify the slice as `not-webflash-ready` /
  `not-release-ready` / `no product YAML` / `no wrapper` / `no
  build-matrix entry`, and the `WEBFLASH-POWER-400-001` Follow-up
  PR sequence row already names the product-and-compliance gate.
  Any further documentation cleanup belongs to a separate
  CLEANUP slice, not to `WEBFLASH-POWER-400-001`.
- **Path C (implementation)** is unsafe right now because every
  upstream gate is open. Adding a WebFlash wrapper under
  [`products/webflash/`](../products/webflash/), flipping
  `webflash_build_matrix: true` on any PWR-bearing
  [`config/product-catalog.json`](../config/product-catalog.json)
  row, or adding a `PWR`-bearing build row to
  [`config/webflash-builds.json`](../config/webflash-builds.json)
  for a mains-voltage path while `COMPLIANCE-001` `S360-400` is
  open would violate the
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
  gate; and adding any of those while
  `PRODUCT-POWER-400-001` has no canonical S360-400 / `PWR`-bearing
  product YAML to wrap would break the
  [`docs/webflash-exposure-readiness-matrix.md` Core rule](webflash-exposure-readiness-matrix.md#core-rule)
  ("WebFlash exposure changes are allowed only when a canonical
  product YAML exists and every gate above is satisfied").

**Recommendation for the next `WEBFLASH-POWER-400-001` PR.** Land
**the WebFlash wrapper under
[`products/webflash/`](../products/webflash/) + the catalog
`webflash_build_matrix: true` flip + the build-matrix row in
[`config/webflash-builds.json`](../config/webflash-builds.json) +
the UX-class decision (standard preview-candidate vs advanced /
manual-warning) as a single atomic slice**, after
`PRODUCT-POWER-400-001` implementation and the `COMPLIANCE-001`
`S360-400` slice closure both land. **Does not** build / sign /
attach a release artifact, generate or validate release notes,
emit checksums, or add a WebFlash import — those belong to
`RELEASE-POWER-400-001` and `WF-IMPORT-POWER-400-001` (cross-repo)
respectively.
   PR #521. The canonical S360-400 / `PWR`-bearing product
   YAML, the matching `config/product-catalog.json` entry, and
   the legacy-compatible `*-pwr` Core variant relationship
   decision (retain / migrate / coexist) that PR #521
   enumerated all remain owed to a future evidence-bearing
   `PRODUCT-POWER-400-001` PR. Per the
   [`docs/webflash-exposure-readiness-matrix.md` wrapper / catalog / build sub-gate table](webflash-exposure-readiness-matrix.md)
   `WEBFLASH-POWER-400-001` is explicitly gated on
   "`PRODUCT-POWER-400-001` landed".
2. **`PACKAGE-POWER-400-001` implementation slice has not
   landed.** Only the docs-only investigation pass merged as
   PR #520. The package YAML header reconciliation, the
   catalog `description` reconciliation, the `S360-400`
   `schematic_status: verified` JSON promotion, and the BOM
   citation that PR #520 enumerated as the required atomic
   slice all remain owed.
3. **BOM cross-check missing.** Same five-component gap PR #520
   / PR #521 recorded for the package slice: no BOM line item
   with manufacturer + part number + revision for `PS1` (so the
   three-way `HLK-5M05` / `HLK-PM01 or similar` / `HLK-10M05`
   disagreement stays unresolved), and no BOM lines for
   `F1 A250-1200` / `RV1 10D391K` / `C1 470nF` / `C5..C8` /
   `J1` / `J2`.
4. **`S360-400` `schematic_status: verified` JSON PR not
   landed.** Separate JSON-only PR after BOM + silkscreen
   evidence land.
5. **`COMPLIANCE-001` `S360-400` slice still open.** Last
   re-checked PR #506; the mains-voltage UK / EU assessment at
   [`compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
   is not cleared. Per the
   [`docs/webflash-exposure-readiness-matrix.md` wrapper / catalog / build sub-gate table](webflash-exposure-readiness-matrix.md)
   `WEBFLASH-POWER-400-001` is additionally gated on
   "`COMPLIANCE-001` `S360-400` slice closed".
6. **Package / catalog reconciliation owed to
   `PACKAGE-POWER-400-001`.** The three-way AC/DC part-identity
   disagreement and the input / output / isolation / protection
   / fusing header text in
   [`../packages/hardware/power_240v.yaml`](../packages/hardware/power_240v.yaml)
   remain unresolved and BOM-bound; the catalog `description:
   Mains to 5V using HLK-5M05.` at
   [`../config/hardware-catalog.json`](../config/hardware-catalog.json)
   line 109 remains uncorrected. A WebFlash wrapper cannot rely
   on any of those claims while they remain BOM-bound.
7. **Product-onboarding approval missing.** Per the
   [Core rule](product-readiness-matrix.md#core-rule) of
   `docs/product-readiness-matrix.md`, exposing a product
   through WebFlash requires (a) every consumed package to be
   `ready-for-package-change` —
   [`../packages/hardware/power_240v.yaml`](../packages/hardware/power_240v.yaml)
   stays `schematic-evidence-pending` +
   `needs-package-reconciliation` +
   `timing/compliance-pending`; (b) an upstream product YAML to
   exist for the wrapper to wrap (none does); and (c) the
   [`product-onboarding.md`](product-onboarding.md) safe
   sequence to be followed end-to-end. None of the three has
   been satisfied for `WEBFLASH-POWER-400-001`.
8. **Release / build / artifact readiness missing.** No
   `artifact_name`, no `.bin` artifact, no GitHub Release, no
   checksums, no proof, no WebFlash import. The candidate
   `Sense360-Ceiling-PWR-{AIR}-{ROOM}-v{VERSION}-{CHANNEL}.bin`
   pattern cannot be reified until `PRODUCT-POWER-400-001`
   lands a canonical product YAML with a decided
   `config_string`. Mains-voltage compliance posture is
   gating-priority over stable promotion;
   `operator-proof-required` + `release-proof-required` both
   apply.

**Why Path B and Path C are not taken now.**

- **Path B (documentation-only cleanup)** is not useful right
  now because the readiness matrices
  ([`webflash-exposure-readiness-matrix.md` §Power / S360-400 WebFlash posture](webflash-exposure-readiness-matrix.md#power--s360-400-webflash-posture),
  [`release-artifact-readiness-matrix.md` §Power / S360-400 release posture](release-artifact-readiness-matrix.md#power--s360-400-release-posture),
  [`product-readiness-matrix.md` §PWR-240V / S360-400](product-readiness-matrix.md#pwr-240v--s360-400))
  already correctly classify the slice as `not-webflash-ready`
  / `not-release-ready` / `no product YAML` / `no wrapper` /
  `no build-matrix row`, and the
  `WEBFLASH-POWER-400-001` wrapper / catalog / build sub-gate
  rows already name the upstream gates. Any further
  documentation cleanup (for example, retiring stale "(this
  PR; docs-only)" prose left over from earlier passes in the
  Follow-up owner cells of those matrix sections) belongs to a
  separate CLEANUP slice, not to `WEBFLASH-POWER-400-001`.
- **Path C (implementation)** is unsafe right now because every
  gate is open. Adding a WebFlash wrapper under
  [`../products/webflash/`](../products/webflash/) while no
  S360-400 product YAML exists under
  [`../products/`](../products/) would have nothing to wrap;
  flipping `webflash_build_matrix: true` in
  [`../config/product-catalog.json`](../config/product-catalog.json)
  while no S360-400-specific entry exists would have nothing
  to flip; adding a build-matrix row to
  [`../config/webflash-builds.json`](../config/webflash-builds.json)
  with an `artifact_name` and a `config_string` while
  [`../packages/hardware/power_240v.yaml`](../packages/hardware/power_240v.yaml)
  carries `schematic-evidence-pending` +
  `needs-package-reconciliation` +
  `timing/compliance-pending` would break the
  [`product-readiness-matrix.md` Core rule](product-readiness-matrix.md#core-rule);
  building / signing / attaching a `.bin` for a mains-voltage
  path while `COMPLIANCE-001` `S360-400` is open would
  additionally violate the
  [`compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
  gate. Adding any `REQUIRED_CONFIGS` / kit / recommended /
  default membership for a PWR-240V product on the WebFlash
  surface before compliance is cleared is similarly unsafe.

**Recommendation for the next `WEBFLASH-POWER-400-001` PR.**
Land **the `products/webflash/` wrapper YAML (candidate path
`products/webflash/ceiling-pwr-{air}-{room}.yaml`; AirIQ ↔
VentIQ mutex honoured) + the matching
[`config/product-catalog.json`](../config/product-catalog.json)
entry promotion (`webflash_wrapper` set +
`webflash_build_matrix: true` flip + `artifact_name` set +
`config_string` set + `channel` set + `version` set) + the
build-matrix row in
[`config/webflash-builds.json`](../config/webflash-builds.json)
as a single atomic slice**, after `PRODUCT-POWER-400-001`
implementation, `PACKAGE-POWER-400-001` implementation, the
`S360-400` `schematic_status: verified` JSON PR, the
`COMPLIANCE-001` `S360-400` slice, and product-onboarding
approval per
[`docs/product-onboarding.md`](product-onboarding.md) all
land. **Does not** build / sign / attach a `.bin` artifact,
create a GitHub Release, generate release notes, mint
checksums, file a release-proof entry, or trigger a WebFlash
import — those belong to `RELEASE-POWER-400-001` and
`WF-IMPORT-POWER-400-001` (cross-repo) respectively, and are
additionally gated by `COMPLIANCE-001` `S360-400` slice
closure. **Does not** modify `release_one_required_configs`,
`canonical_modules`, `canonical_power`, `forbidden_tokens`,
`lifecycle_statuses`, kit membership, or `REQUIRED_CONFIGS`.

**Queue effect.**

- `WEBFLASH-POWER-400-001` is now **investigated and deferred**
  in the [`UPCOMING_PR.md`](../UPCOMING_PR.md) active queue
  (entry #5), blocked on the five preconditions above.
- `PRODUCT-POWER-400-001` is recorded as **PR #521** in the
  [`UPCOMING_PR.md`](../UPCOMING_PR.md) Completed / merged PRs
  table.
- `PACKAGE-POWER-400-001` is recorded as **PR #520** in the
  [`UPCOMING_PR.md`](../UPCOMING_PR.md) Completed / merged PRs
  table.
- `RELEASE-POWER-400-001` and `WF-IMPORT-POWER-400-001`
  (cross-repo) stay **blocked** behind `WEBFLASH-POWER-400-001`
  and `COMPLIANCE-001`.
- `CORE-ABSTRACT-BUS-001C` stays at the top of the active queue
  (entry #1), blocked on its own six preconditions.
- `CORE-ABSTRACT-BUS-001A` stays blocked behind `001C`.
- `CORE-ABSTRACT-BUS-001B` stays at queue entry #3, blocked on
  its own four preconditions.
  (entry #4), blocked on the eight preconditions above.
- `PRODUCT-POWER-400-001` is recorded as **PR #521** in the
  [`UPCOMING_PR.md`](../UPCOMING_PR.md) Completed / merged PRs
  table. Per the
  [§PRODUCT-POWER-400-001 update](#product-power-400-001-update-2026-05-19--docs-only-investigation-pass)
  entry, `PRODUCT-POWER-400-001` stays blocked on its own six
  preconditions; the product slice is **not** advanced by PR
  #521.
- `PACKAGE-POWER-400-001` stays at PR #520 (recorded
  previously) and stays blocked on its own five preconditions.
- `RELEASE-POWER-400-001` and `WF-IMPORT-POWER-400-001`
  (cross-repo) stay **blocked** behind `WEBFLASH-POWER-400-001`
  and `COMPLIANCE-001`.
- `CORE-ABSTRACT-BUS-001C` stays at the top of the active
  queue (entry #1), blocked on its own six preconditions per
  PR #518.
- `CORE-ABSTRACT-BUS-001A` stays blocked behind `001C`.
- `CORE-ABSTRACT-BUS-001B` stays at queue entry #3, blocked on
  its own four preconditions per PR #519.
- `PACKAGE-PWM-001` / `PACKAGE-DAC-001` stay blocked behind
  `001B` implementation + their own evidence gates.
- `PACKAGE-RELAY-001` and downstream relay slices stay blocked
  behind `001A` (which is itself blocked behind `001C`).
- `PACKAGE-POE-410-001` / `PRODUCT-POE-410-001` /
  `WEBFLASH-POE-410-001` / `RELEASE-POE-410-001` /
  `WF-IMPORT-POE-410-001` stay blocked behind their own evidence
  gates.
  `WF-IMPORT-POE-410-001` stay blocked behind their own
  evidence gates.
- `PACKAGE-TRIAC-001` / `PRODUCT-TRIAC-002` / `WF-TRIAC-001` /
  `RELEASE-TRIAC-001` / `WF-IMPORT-TRIAC-001` stay blocked
  behind HW-005 / `HW-PINMAP-320-FOLLOWUP` / COMPLIANCE-001.

**What this update does *not* do.** Adds **no** package YAML,
product YAML, WebFlash wrapper, JSON catalog change, script,
test, workflow, component, include, firmware artifact, manifest,
GitHub Release, tag, WebFlash import, or kit edit. Does **not**
edit
[`packages/hardware/power_240v.yaml`](../packages/hardware/power_240v.yaml)
(byte-identical to PR #515 / PR #520 / PR #521 state); does
**not** edit any other file under
[`packages/`](../packages/); does **not** edit
[`config/hardware-catalog.json`](../config/hardware-catalog.json)
(`S360-400` row stays byte-identical); does **not** edit
[`config/product-catalog.json`](../config/product-catalog.json)
(no S360-400-specific product added; the four `legacy-compatible`
`*-pwr` Core variants stay `legacy-compatible` /
`webflash_build_matrix: false`; the two shipping entries and the
FanTRIAC blocked-reference entry stay verbatim); does **not**
edit
[`config/webflash-builds.json`](../config/webflash-builds.json)
(no `PWR`-bearing build added); does **not** edit
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
(`PWR` stays reserved in `canonical_power` with no
`webflash_build_matrix: true` entry); does **not** edit any
product YAML under [`products/`](../products/); does **not** edit
any WebFlash wrapper under
[`products/webflash/`](../products/webflash/); does **not** edit
[`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)
or any other workflow; does **not** edit any test under
[`tests/`](../tests/) or any script under
[`scripts/`](../scripts/); does **not** edit
[`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
(COMPLIANCE-001 unchanged); does **not** edit
[`docs/hardware/s360-400-r4-power.md`](hardware/s360-400-r4-power.md);
does **not** edit
[`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md),
[`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md),
[`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md),
or
[`docs/product-readiness-matrix.md`](product-readiness-matrix.md);
does **not** edit
[`docs/webflash-release-proof.md`](webflash-release-proof.md) or
[`docs/webflash-release-handoff.md`](webflash-release-handoff.md).
No precondition is closed by this pass. Specifically: does
**not** advance `WEBFLASH-POWER-400-001`,
`PRODUCT-POWER-400-001`, `PACKAGE-POWER-400-001`,
`RELEASE-POWER-400-001`, or `WF-IMPORT-POWER-400-001`; does
**not** advance any other PWR / POE-410 / RELAY / PWM / DAC /
TRIAC / CORE-ABSTRACT-BUS slice; does **not** close
`COMPLIANCE-001`; does **not** change Release-One
(`Ceiling-POE-VentIQ-RoomIQ` / version `1.0.0` / channel
`stable` / artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` / tag
`v1.0.0`); does **not** change the LED preview entry
(`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview` /
`Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`);
does **not** change `REQUIRED_CONFIGS` or kits; does **not**
promote any `schematic_status`; does **not** set any
`schematic_file`; does **not** claim any hardware-verified
evidence; does **not** claim that any BOM / silkscreen / PCB /
creepage / clearance / bench / thermal / EMI / compliance
evidence exists; does **not** make any CE / UKCA / FCC / UL /
LVD / EMC / RoHS / IEC claim.

The only files this update touches are this
`WEBFLASH-POWER-400-001 update` section in
`docs/cleanup-audit.md`, the new audit-log entry in
[`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md)
§Power / S360-400 WebFlash posture, the new audit-log entry in
[`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
§Power / S360-400 release posture, and the queue refresh in
[`UPCOMING_PR.md`](../UPCOMING_PR.md) (`PRODUCT-POWER-400-001`
recorded as PR #521 in the Completed / merged PRs table,
`WEBFLASH-POWER-400-001` recorded as PR #522 in the same table,
current-queue-summary updated with the WEBFLASH-POWER-400-001
investigation pass bullet, active-queue entry #5 expanded with
the investigation outcome, new entry added under §Recently
uploaded evidence for "No new evidence committed for
`WEBFLASH-POWER-400-001` preconditions").

**Next `WEBFLASH-POWER-400-001` audit-log trigger.** The next
audit-log entry against this slice should appear when one of the
five preconditions above lands or when the next implementation
PR makes a `WEBFLASH-POWER-400-001` wrapper / catalog
`webflash_build_matrix: true` / build-matrix-row edit. Until
then, the next audit-log entry should report the same
`WEBFLASH-POWER-400-001 investigation pass — preconditions still
open` outcome with the new inspection date.

## RELEASE-POWER-400-001 update (2026-05-19 — docs-only investigation pass)

This update records the 2026-05-19 docs-only investigation pass
against `RELEASE-POWER-400-001` (the S360-400 PWR-240V
release-artifact / release-notes / checksum / manifest / proof /
WebFlash-import-handoff slice). The upstream
`WEBFLASH-POWER-400-001` investigation pass merged earlier the
same day as **PR #522** (docs-only Path A deferral) and is
recorded above at
[§WEBFLASH-POWER-400-001 update](#webflash-power-400-001-update-2026-05-19--docs-only-investigation-pass);
`WEBFLASH-POWER-400-001` is the named immediate gate for
`RELEASE-POWER-400-001` per
[`docs/release-artifact-readiness-matrix.md` Follow-up PR sequence](release-artifact-readiness-matrix.md#follow-up-pr-sequence)
("**`RELEASE-POWER-400-001`** … gated on **`WEBFLASH-POWER-400-001`
landed + `COMPLIANCE-001` `S360-400` slice closed**"), and the
WebFlash slice is **not** advanced by PR #522 — the WebFlash
wrapper, the catalog `webflash_build_matrix: true` flip, the
build-matrix row, and the UX-class decision that PR #522
enumerated as the required atomic slice all remain owed to a
future evidence-bearing `WEBFLASH-POWER-400-001` PR.

**Outcome — Path A docs-only investigation / deferral.**
`RELEASE-POWER-400-001` is **confirmed deferred at the
implementation layer.** Seven preconditions remain open. No new
package, product, WebFlash, build, release, compliance, JSON
catalog, test, script, workflow, component, include, firmware,
or manifest evidence has arrived since PR #522; the live state
of every release surface that `RELEASE-POWER-400-001` would
touch stays byte-identical to PR #522.

**Findings recorded — answers to the 15 investigation
questions.** Each finding is a verifiable live-state fact
re-runnable against the repo via `find` / `grep`:

1. **Q1: Does any S360-400 product YAML exist?** No. No file
   under [`products/`](../products/) or
   [`products/webflash/`](../products/webflash/) names
   `S360-400`, `Ceiling-PWR-*`, or `PWR-240V`. The only
   `pwr`-bearing products are the four `legacy-compatible` Core
   variants
   [`sense360-core-c-pwr.yaml`](../products/sense360-core-c-pwr.yaml),
   [`sense360-core-w-pwr.yaml`](../products/sense360-core-w-pwr.yaml),
   [`sense360-core-v-c-pwr.yaml`](../products/sense360-core-v-c-pwr.yaml),
   and
   [`sense360-core-v-w-pwr.yaml`](../products/sense360-core-v-w-pwr.yaml),
   and they are not S360-400-specific.
2. **Q2: Does any S360-400 WebFlash wrapper exist?** No.
   [`products/webflash/`](../products/webflash/) contains
   exactly three PoE wrappers
   ([`ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml),
   [`ceiling-poe-ventiq-roomiq-led.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq-led.yaml),
   [`ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml));
   no `Ceiling-PWR-*` wrapper.
3. **Q3: Does `config/webflash-builds.json` contain any PWR
   build?** No. The build matrix contains exactly two PoE-based
   builds: `Ceiling-POE-VentIQ-RoomIQ` (stable) and
   `Ceiling-POE-VentIQ-RoomIQ-LED` (preview). No PWR-240V build.
4. **Q4: Does `config/product-catalog.json` contain any S360-400
   `artifact_name`?** No. The catalog contains exactly two
   `artifact_name` entries
   (`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` and
   `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`),
   both PoE-based. No S360-400 product, no PWR `artifact_name`.
5. **Q5: Does `firmware/configurations` contain any S360-400 /
   PWR artifact?** No — and the directory does not exist. The
   repository has no `firmware/` directory at all; release
   infrastructure is
   [`config/webflash-builds.json`](../config/webflash-builds.json)
   (as the build matrix) consumed by
   [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)
   (as the build / sign / checksum / release-attach pipeline).
6. **Q6: Does `firmware/sources.json` include any S360-400 / PWR
   source?** No — and the file does not exist.
7. **Q7: Does `manifest.json` include any S360-400 / PWR build?**
   No — and the file does not exist at the repo root. No
   `firmware-*.json` file exists at the repo root either.
8. **Q8: Did PACKAGE-POWER-400-001 implement package
   reconciliation?** No. The 2026-05-19
   `PACKAGE-POWER-400-001` investigation pass merged as
   **PR #520** is docs-only Path A deferral. The package YAML
   header reconciliation, the catalog `description`
   reconciliation, the `S360-400` `schematic_status: verified`
   JSON promotion, and the BOM citation all remain owed.
   [`packages/hardware/power_240v.yaml`](../packages/hardware/power_240v.yaml)
   stays byte-identical (stale `HLK-PM01 or similar` header).
9. **Q9: Did PRODUCT-POWER-400-001 implement product YAML /
   catalog?** No. The 2026-05-19 `PRODUCT-POWER-400-001`
   investigation pass merged as **PR #521** is docs-only Path A
   deferral. No canonical S360-400 / `PWR`-bearing product YAML
   was added; no matching
   [`config/product-catalog.json`](../config/product-catalog.json)
   entry was added; no legacy-compatible `*-pwr` Core variant
   relationship decision was made.
10. **Q10: Did WEBFLASH-POWER-400-001 implement wrapper / build
    matrix?** No. The 2026-05-19 `WEBFLASH-POWER-400-001`
    investigation pass merged as **PR #522** is docs-only Path A
    deferral. No WebFlash wrapper was added under
    [`products/webflash/`](../products/webflash/); no
    `webflash_build_matrix: true` flip on any PWR-bearing row;
    no `PWR`-bearing entry in
    [`config/webflash-builds.json`](../config/webflash-builds.json);
    UX-class decision pending.
11. **Q11: Is COMPLIANCE-001 S360-400 cleared?** No. Last
    re-checked **PR #506**; the mains-voltage UK / EU
    assessment at
    [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
    is not cleared. `S360-400` is one of two mains-voltage SKUs
    in scope.
12. **Q12: Is S360-400 `schematic_status` verified?** No.
    [`config/hardware-catalog.json`](../config/hardware-catalog.json)
    line 110 stays `schematic_status: cataloged_unverified` with
    no `schematic_file`.
    [`tests/test_hardware_catalog.py:53`](../tests/test_hardware_catalog.py)
    `EXPECTED_STILL_UNVERIFIED_SKUS = frozenset({"S360-320",
    "S360-400"})` actively enforces this state. The separate
    JSON-only PR for the `schematic_status: verified` promotion
    has not landed.
13. **Q13: Is BOM evidence committed?** No. No BOM line item
    with manufacturer + part number + revision for `PS1` is
    committed (so the three-way catalog `HLK-5M05` vs package
    header `HLK-PM01 or similar` vs schematic
    `PS1 = HLK-10M05` AC/DC part-identity disagreement stays
    unresolved and BOM-bound); no BOM lines for
    `F1 A250-1200` / `RV1 10D391K` / `C1 470nF` / `C5..C8` /
    `J1` / `J2` are committed.
14. **Q14: Are release notes / checksum / artifact proof gates
    satisfied?** No. No GitHub Release for any PWR-240V tag
    exists; no `Sense360-Ceiling-PWR-{AIR}-{ROOM}-v{VERSION}-{CHANNEL}.bin`
    artifact has been built, signed, attached, or imported; no
    SHA256 / MD5 checksum files for any PWR-240V artifact; no
    build-info `manifest.json` asset for any PWR-240V release;
    no proof row in
    [`docs/webflash-release-proof.md`](webflash-release-proof.md)
    for any PWR-240V artifact;
    [`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py)
    has no `(config_string, version, channel)` input matrix row
    for PWR-240V to consume;
    [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py)
    has no body to validate.
15. **Q15: Would generating a release artifact now violate
    release-readiness gates?** Yes. All eight release-time
    sub-gates listed in
    [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
    §Release note / artifact / checksum gates are unmet for any
    PWR-240V `.bin`: (a) product-catalog entry — none;
    (b) build-matrix entry — none; (c) artifact-name conformance
    — no `artifact_name` exists; (d) release-tag conformance —
    no tag; (e) release-notes generated — no
    `(config_string, version, channel)` input; (f) release-notes
    valid — no body exists; (g) artifact built — no input
    matrix row; (h) checksums attached / manifest attached / proof
    recorded — no asset to checksum / manifest / prove. Plus
    `WF-IMPORT-POWER-400-001` (cross-repo) cannot proceed without
    an artifact to import.

**Open preconditions (carried forward).**

1. **`WEBFLASH-POWER-400-001` implementation slice has not
   landed.** Only the docs-only investigation pass merged as
   PR #522. The WebFlash wrapper, the catalog
   `webflash_build_matrix: true` flip, the build-matrix row, and
   the UX-class decision all remain owed.
2. **`PRODUCT-POWER-400-001` implementation slice has not
   landed.** Only the docs-only investigation pass merged as
   PR #521.
3. **`PACKAGE-POWER-400-001` implementation slice has not
   landed.** Only the docs-only investigation pass merged as
   PR #520.
4. **`S360-400` `schematic_status: verified` JSON PR not
   landed.** Separate JSON-only PR after BOM + silkscreen
   evidence land.
5. **`COMPLIANCE-001` `S360-400` slice still open.** Last
   re-checked PR #506.
6. **BOM / silkscreen / creepage / clearance / bench / thermal /
   EMI evidence missing.** Same five-component gap PR #520
   recorded for `PS1` / `F1 A250-1200` / `RV1 10D391K` /
   `C1 470nF` / `C5..C8` / `J1` / `J2`, plus no operator-attributed
   silkscreen captures of the module-side `J1` 1-to-3 / `J2`
   1-to-2 pin orders, no KiCad PCB / gerbers / board photos
   sufficient to measure creepage / clearance, and no bench /
   load / thermal / inrush / insulation / Hi-pot /
   earth-continuity / leakage / EMI / EMC measurements against
   a populated `S360-400-R4` board.
7. **UX-class decision pending.** Standard preview-candidate vs
   advanced / manual-warning posture has not been chosen.
   Decision belongs upstream to `PRODUCT-POWER-400-001`
   (compliance verdict) and `WEBFLASH-POWER-400-001` (exposure
   class). Per the
   [`docs/release-artifact-readiness-matrix.md` Follow-up PR sequence](release-artifact-readiness-matrix.md#follow-up-pr-sequence)
   row 1502, the `RELEASE-POWER-400-001` UX class is decided
   per the `PRODUCT-POWER-400-001` / `WEBFLASH-POWER-400-001`
   compliance verdict; that verdict has not been rendered.

**Why Path B and Path C are not taken now.**

- **Path B (release-notes / proof-template-only PR)** is
  rejected because (a)
  [`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py)
  consumes
  [`config/webflash-builds.json`](../config/webflash-builds.json)
  as the matrix source and needs a
  `(config_string, version, channel)` input tuple that does not
  exist for PWR-240V; (b) a proof-template-only edit to
  [`docs/webflash-release-proof.md`](webflash-release-proof.md)
  would introduce a forward-reference to an artifact that has
  never been built and would degrade the proof file's
  evidentiary integrity; (c) per the
  [`docs/release-artifact-readiness-matrix.md` Follow-up PR sequence](release-artifact-readiness-matrix.md#follow-up-pr-sequence)
  row 1502, `RELEASE-POWER-400-001` is explicitly **"Build,
  sign, attach the `.bin`; release notes; checksums; proof
  row"** — that is the atomic slice, not a notes-only or
  proof-only split.
- **Path C (implementation)** is unsafe right now because every
  upstream gate is open. Building / signing / attaching a
  PWR-240V `.bin` while
  `WEBFLASH-POWER-400-001` / `PRODUCT-POWER-400-001` /
  `PACKAGE-POWER-400-001` have only docs-only investigation
  passes (no wrapper / product YAML / package reconciliation
  exists), while `COMPLIANCE-001` `S360-400` is open, and while
  the schematic / BOM / silkscreen / creepage-clearance / bench
  / thermal / EMI evidence is missing would violate the
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
  gate, the
  [`docs/release-artifact-readiness-matrix.md` Core rule](release-artifact-readiness-matrix.md#core-rule),
  and the
  [`docs/webflash-exposure-readiness-matrix.md` Core rule](webflash-exposure-readiness-matrix.md#core-rule).
  Additionally,
  [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)
  is in the do-not-change guardrail and processes only entries
  in
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  which has no PWR-240V row.

**Recommendation for the next `RELEASE-POWER-400-001` PR.** Land
**the build + sign + attach `.bin` + generate release notes +
validate release notes + emit SHA256 + emit MD5 + attach
build-info manifest + record proof row in
[`docs/webflash-release-proof.md`](webflash-release-proof.md) +
hand off to `WF-IMPORT-POWER-400-001` (cross-repo) as a single
atomic slice**, after `WEBFLASH-POWER-400-001` implementation
and the `COMPLIANCE-001` `S360-400` slice closure both land. UX
class (standard preview vs advanced / manual-warning) decided
per the `PRODUCT-POWER-400-001` / `WEBFLASH-POWER-400-001`
compliance verdict per
[`docs/release-artifact-readiness-matrix.md` Follow-up PR sequence](release-artifact-readiness-matrix.md#follow-up-pr-sequence)
row 1502.

**Queue effect.**

- `RELEASE-POWER-400-001` is now **investigated and deferred**
  in the [`UPCOMING_PR.md`](../UPCOMING_PR.md) active queue
  (entry #6), blocked on the seven preconditions above.
- `WEBFLASH-POWER-400-001` is recorded as **PR #522** in the
  [`UPCOMING_PR.md`](../UPCOMING_PR.md) Completed / merged PRs
  table.
- `PRODUCT-POWER-400-001` is recorded as **PR #521** in the
  [`UPCOMING_PR.md`](../UPCOMING_PR.md) Completed / merged PRs
  table.
- `PACKAGE-POWER-400-001` is recorded as **PR #520** in the
  [`UPCOMING_PR.md`](../UPCOMING_PR.md) Completed / merged PRs
  table.
- `WF-IMPORT-POWER-400-001` (cross-repo) stays **blocked**
  behind `RELEASE-POWER-400-001`.
- `CORE-ABSTRACT-BUS-001C` / `001A` / `001B` stay deferred.
- All PoE-410 / RELAY / PWM / DAC / TRIAC slices stay blocked
  behind their own evidence gates.

**What this update does *not* do.** Adds **no** package YAML,
product YAML, WebFlash wrapper, JSON catalog change, script,
test, workflow, component, include, firmware artifact, manifest,
GitHub Release, tag, WebFlash import, or kit edit. Does **not**
edit
[`packages/hardware/power_240v.yaml`](../packages/hardware/power_240v.yaml)
(byte-identical to PR #515 / PR #520 / PR #521 / PR #522
state); does **not** edit any other file under
[`packages/`](../packages/); does **not** edit
[`config/hardware-catalog.json`](../config/hardware-catalog.json)
(`S360-400` row stays `schematic_status: cataloged_unverified`,
no `schematic_file`); does **not** edit
[`config/product-catalog.json`](../config/product-catalog.json)
(no S360-400-specific product added; the two shipping entries
and the FanTRIAC blocked-reference entry stay verbatim); does
**not** edit
[`config/webflash-builds.json`](../config/webflash-builds.json)
(no `PWR`-bearing build added); does **not** edit
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
(`PWR` stays reserved in `canonical_power` with no
`webflash_build_matrix: true` consumer;
`release_one_required_configs` stays
`["Ceiling-POE-VentIQ-RoomIQ"]`); does **not** edit any product
YAML under [`products/`](../products/); does **not** edit any
WebFlash wrapper under
[`products/webflash/`](../products/webflash/); does **not**
create `firmware/`, `firmware/configurations/`,
`firmware/sources.json`, `manifest.json`, or any `firmware-*.json`
file (none of those paths exist at HEAD; this PR does not add
them); does **not** edit
[`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)
or any other workflow; does **not** edit
[`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py),
[`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py),
[`scripts/derive_release_version_channel.py`](../scripts/derive_release_version_channel.py),
[`scripts/product_name_mapper.py`](../scripts/product_name_mapper.py),
or any other script; does **not** edit
[`tests/test_validate_webflash_release_notes.py`](../tests/test_validate_webflash_release_notes.py),
[`tests/test_generate_webflash_release_notes.py`](../tests/test_generate_webflash_release_notes.py),
[`tests/test_webflash_artifact_naming.py`](../tests/test_webflash_artifact_naming.py),
or any other test; does **not** edit
[`docs/webflash-release-proof.md`](webflash-release-proof.md),
[`docs/webflash-release-handoff.md`](webflash-release-handoff.md),
[`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
(COMPLIANCE-001 unchanged),
[`docs/hardware/s360-400-r4-power.md`](hardware/s360-400-r4-power.md),
[`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md),
[`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md),
[`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md),
or
[`docs/product-readiness-matrix.md`](product-readiness-matrix.md);
does **not** create or modify any GitHub Release; does **not**
create or modify any release tag; does **not** emit or attach
any SHA256 / MD5 / asset checksum; does **not** attach or
modify any build-info manifest; does **not** record or modify
any release-proof row; does **not** trigger or modify any
WebFlash import. No precondition is closed by this pass.
Specifically: does **not** advance `RELEASE-POWER-400-001`,
`WEBFLASH-POWER-400-001`, `PRODUCT-POWER-400-001`,
`PACKAGE-POWER-400-001`, or `WF-IMPORT-POWER-400-001`; does
**not** advance any other PWR / POE-410 / RELAY / PWM / DAC /
TRIAC / CORE-ABSTRACT-BUS slice; does **not** close
`COMPLIANCE-001`, `S360-100-BENCH-001`, `HW-PINMAP-*-FOLLOWUP`,
or `S360-300-BENCH-001`; does **not** change Release-One
(`Ceiling-POE-VentIQ-RoomIQ` / version `1.0.0` / channel
`stable` / artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` / tag
`v1.0.0`); does **not** change the LED preview entry
(`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview` /
`Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`);
does **not** change `REQUIRED_CONFIGS` or kits; does **not**
promote any `schematic_status`; does **not** set any
`schematic_file`; does **not** claim any hardware-verified
evidence; does **not** claim that any BOM / silkscreen / PCB /
creepage / clearance / bench / thermal / EMI / compliance
evidence exists; does **not** make any CE / UKCA / FCC / UL /
LVD / EMC / RoHS / IEC claim.

The only files this update touches are this
`RELEASE-POWER-400-001 update` section in
`docs/cleanup-audit.md`, the new audit-log entry in
[`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
§Power / S360-400 release posture, and the queue refresh in
[`UPCOMING_PR.md`](../UPCOMING_PR.md) (`PRODUCT-POWER-400-001`
recorded as PR #521 and `WEBFLASH-POWER-400-001` recorded as
PR #522 in the Completed / merged PRs table,
current-queue-summary updated with the RELEASE-POWER-400-001
investigation pass bullet, active-queue entry #6 expanded with
the investigation outcome, new entry added under §Recently
uploaded evidence for "No new evidence committed for
`RELEASE-POWER-400-001` preconditions").

**Next `RELEASE-POWER-400-001` audit-log trigger.** The next
audit-log entry against this slice should appear when one of
the seven preconditions above lands or when the next
implementation PR makes a `RELEASE-POWER-400-001` build / sign /
attach / release-notes / checksum / manifest / proof / WebFlash
import edit. Until then, the next audit-log entry should report
the same `RELEASE-POWER-400-001 investigation pass —
preconditions still open` outcome with the new inspection date.
test, workflow, component, include, firmware artifact,
manifest, GitHub Release, tag, WebFlash import, or kit edit.
Does **not** edit
[`../packages/hardware/power_240v.yaml`](../packages/hardware/power_240v.yaml)
(byte-identical to PR #520 / PR #515 state). Does **not** edit
[`../config/hardware-catalog.json`](../config/hardware-catalog.json),
[`../config/product-catalog.json`](../config/product-catalog.json),
[`../config/webflash-builds.json`](../config/webflash-builds.json),
or
[`../config/webflash-compatibility.json`](../config/webflash-compatibility.json).
Does **not** add a `webflash_wrapper`, a
`webflash_build_matrix: true` flip, an `artifact_name`, a
`config_string`, a `channel`, or a `version` for any
S360-400-bearing entry. Does **not** add a wrapper YAML under
[`../products/webflash/`](../products/webflash/). Does **not**
add a build-matrix row to
[`../config/webflash-builds.json`](../config/webflash-builds.json).
Does **not** promote `S360-400` `schematic_status` or set
`schematic_file`. Does **not** clear `COMPLIANCE-001` for
`S360-400` (or `S360-320`). Does **not** modify
`release_one_required_configs`, `canonical_modules`,
`canonical_power`, `forbidden_tokens`, `lifecycle_statuses`,
kit membership, or `REQUIRED_CONFIGS`. Does **not** change
Release-One (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0-stable`).
Does **not** change the LED preview path
(`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`). Does **not**
unblock FanTRIAC (stays `blocked` / `HW-005` /
`webflash_build_matrix: false`). Does **not** advance
`PACKAGE-POWER-400-001`, `PRODUCT-POWER-400-001`,
`RELEASE-POWER-400-001`, or `WF-IMPORT-POWER-400-001`.

**Cross-links updated.**

- `UPCOMING_PR.md` (PRODUCT-POWER-400-001 recorded as PR #521
  in the Completed / merged PRs table;
  `WEBFLASH-POWER-400-001` queue row promoted from "Planned"
  placeholder to investigated-and-deferred entry #4;
  Current queue summary bullet added; Recently uploaded
  evidence entry added).
- `docs/webflash-exposure-readiness-matrix.md` §Power / S360-400
  WebFlash posture (audit-log paragraph added).
- `docs/release-artifact-readiness-matrix.md` §Power / S360-400
  release posture (audit-log paragraph added).
- This file (new entry added; existing
  `PRODUCT-POWER-400-001 update (2026-05-19 — docs-only
  investigation pass)` entry preserved unchanged).

**Next `WEBFLASH-POWER-400-001` audit-log trigger.** The next
audit-log entry against this slice should appear when one of
the eight preconditions above lands or when the next
implementation PR makes a `WEBFLASH-POWER-400-001` wrapper /
catalog / build edit. Until then, the next audit-log entry
should report the same `WEBFLASH-POWER-400-001 investigation
pass — preconditions still open` outcome with the new
inspection date.

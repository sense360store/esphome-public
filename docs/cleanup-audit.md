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
| `docs/hardware/artifacts/S360-311-R4.md` | `current` | HW-ASSETS-003 curated artifact index for Sense360 PWM (`S360-311-R4`). Records the uploaded module-side schematic `b4db0d64-S360311R4.pdf` (91,543 bytes; SHA256 `c910b3364be1d58fc44d12b5a189dade47efddf6cae158a86577ec7501e48006`), now committed byte-identical at `docs/hardware/schematics/S360-311-R4.pdf`. Records visible schematic content (MT3608 `+5V`→`+12V` boost; four 4-pin fan outputs `J1`/`J2`/`J4`/`J5` with low-side N-FETs; 13-pin `J3` "From Core" with pins 1–13 `+5V`/`TachIO`/`TachPMW1`/`Pul_Cou1`/`TachPMW2`/`Pul_Cou2`/`TachPMW3`/`Pul_Cou3`/`TachPMW4`/`Pul_Cou4`/`UART_RX`/`UART_TX`/`GND`; 4-pin Nextion `J6`; mounting holes `H1..H4`; section title "NINE 4pin FANs" recorded as an open documentation question). Records reconciliation flags owed to `HW-PINMAP-311` (Core J6 1-to-13 verify; UART on J3 pins 11/12 not yet captured Core-side). Records that KiCad source, KiCad PCB, KiCad project metadata, BOM, CPL, gerbers, drill files, STEP, and board images were not present in this upload (marked `not provided in this upload`, not fabricated). Explicitly does not change `config/hardware-catalog.json` (`S360-311` stays `schematic_status: cataloged_unverified`, `schematic_file` not set), does not change `config/product-catalog.json` / `config/webflash-builds.json` / `config/webflash-compatibility.json`, does not change any product YAML / WebFlash wrapper / package YAML, does not unblock FanTRIAC (HW-005 stays a separate gate), does not change Release-One. | Keep. |
| `docs/hardware/artifacts/S360-312-R4.md` | `current` | HW-ASSETS-003 curated artifact index for Sense360 DAC (`S360-312-R4`). Records the uploaded module-side schematic `682cf9e8-S360312R4.pdf` (122,230 bytes; SHA256 `2888f626bfa0139d2190f154f9b02ecf4cb06f2522a5b5802eaf96e16de39e28`), now committed byte-identical at `docs/hardware/schematics/S360-312-R4.pdf`. Records visible schematic content (MT3608 `+3.3V`→`+12V` boost; **two** `GP8403-TC50-EW` DACs `IC1` / `IC2` on a shared I²C bus, address-selectable via DIP `SW1` / `SW2` with 4.7 kΩ pullups; two 3-pin Cloudlift-style outputs `J2` / `J3`; 6-pin `J1` "From Core" with pins 1–6 `+3.3V`/`I2C_SDA`/`I2C_SCL`/`UART_RX`/`UART_TX`/`GND`; 4-pin Nextion `J7`; mounting holes `H1..H4`). Records reconciliation flags owed to `HW-PINMAP-312` (Module J1 pin-1 `+3.3V` vs Core J7 pin-1 `+5V` voltage-rail discrepancy; dual-DAC capacity broader than singular catalog description; I²C address-selection scheme). Records that KiCad source, KiCad PCB, KiCad project metadata, BOM, CPL, gerbers, drill files, STEP, and board images were not present in this upload (marked `not provided in this upload`, not fabricated). Explicitly does not change `config/hardware-catalog.json` (`S360-312` stays `schematic_status: cataloged_unverified`, `schematic_file` not set), does not change `config/product-catalog.json` / `config/webflash-builds.json`, does not change the `FanDAC` ↔ `AirIQ` mutex in `config/webflash-compatibility.json`, does not change any product YAML / WebFlash wrapper / package YAML, does not unblock FanTRIAC, does not change Release-One. | Keep. |
| `docs/hardware/artifacts/S360-320-R4.md` | `blocked-reference` | HW-ASSETS-003 curated artifact index for Sense360 TRIAC (`S360-320-R4`). Records the uploaded module-side schematic `631ef0c1-S360320R4.pdf` (54,565 bytes; SHA256 `4cd0685251dcdbc7aa8933cbfa92008df46940b6349f0dea91d32e1028c2911f`), now committed byte-identical at `docs/hardware/schematics/S360-320-R4.pdf`. Records visible schematic content ("TRIAC CIRCUIT"; 3-pin AC LINE `J1`; 2-pin LOAD `J2`; `Q1 BT136S-600D,118` TRIAC; `U1 MOC3023M` optotriac driver with `R3 220 Ω` LED-side limit and `R1 1 kΩ` / `R2 100 Ω` snub / gate resistors; `OK1 EL814` zero-cross optocoupler with symmetric `R5 33 kΩ` / `R6 33 kΩ` mains-side bias and `R4 10 kΩ` pull-up to `+3V3`; 4-pin `J3` "From Core" with pins 1–4 `+3V3`/`ESP_GPIO1`/`ESP_GPIO2`/`GND`). Records reconciliation flags owed to `HW-PINMAP-320` (Core `TRI_GPIO*` vs Module `ESP_GPIO*` naming; AC LINE `J1` 3-pin function open). Records that the module uses discrete `MOC3023M` + `BT136` + `EL814` with no on-board controller IC, **eliminating Option (b) (replacement non-`ac_dimmer` driver targeting an on-board controller IC) from the HW-005 missing-evidence checklist for this revision**, but **not** unblocking HW-005 — Option (a) (end-to-end direct interrupt-capable ESP32 GPIOs traced through `S360-100-R4` + `S360-320`) still requires the Core-side `TRI_GPIO*` trace, which currently routes via SX1509. Records that KiCad PCB, BOM, and gerbers are COMPLIANCE-001-adjacent (creepage / clearance / component voltage ratings) and were not in this upload. Explicitly does not change `config/hardware-catalog.json` (`S360-320` stays `schematic_status: cataloged_unverified`, `schematic_file` not set), does not change `config/product-catalog.json` (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`), does not change `config/webflash-builds.json` / `config/webflash-compatibility.json` (Release-One `blocked_modules` still includes `FanTRIAC`), does not change any product YAML / WebFlash wrapper / package YAML (`packages/expansions/fan_triac.yaml` keeps its BLOCKED / UNVERIFIED banner and placeholder GPIOs), **does not unblock FanTRIAC under HW-005, and does not clear `S360-320` under COMPLIANCE-001 — both blockers remain in force**, does not change Release-One. | Keep. |
| `docs/hardware/artifacts/S360-100-R4.md` | `current` | HW-ASSETS-002 curated artifact index for Sense360 Core (`S360-100-R4`). Records that the upload was five loose files (not a packed ZIP): `83537ddc-S360100R4.pdf` (849,828 bytes), `bc386261-S360100R4_BOM.xlsx` (12,543 bytes), `d5bb9e7b-S360100R4pos.csv` (4,803 bytes), `2248fe0e-S360100R4gerbers.zip` (290,097 bytes, 15 inner files under `S360-100-R4-gerbers/` with legacy prefix `Sense360_Core_R4-*`, 4-layer board: F_Cu / In1_Cu / In2_Cu / B_Cu), and `0a7f7965-S360100R4.step` (6,335,475 bytes), each with its SHA256. Records that the uploaded PDF is byte-identical (SHA256 `173a60792703923c69639772c4e23531faedf8a88e5147656d133a6317acf435`, 849,828 bytes) to the already-committed `docs/hardware/schematics/S360-100-R4.pdf` and is therefore not re-committed. Records that KiCad schematic source, KiCad PCB source, KiCad project metadata (`.kicad_pro`, `.kicad_prl`, `fp-lib-table`), board images, the raw `S360-100-R4.zip`, `__MACOSX/`, `.DS_Store`, `Icon` files, `.history/`, and embedded `.git/` were **not** present in this upload; missing files are recorded as `not provided in this upload` (not fabricated, not labelled `pending`). Applies the HW-ASSETS-001 policy: BOM / CPL / gerbers / drill / STEP are **retained-but-not-committed** under the current policy and are not committed in this PR. Records artifact-specific open questions (long-term storage backend, KiCad source delivery, gerber inner-filename prefix `Sense360_Core_R4-*` vs canonical `S360-100-R4-*`, image set, manufacturing-archive retention). Cross-references the pre-existing Core schematic-level Open Questions in `docs/hardware/s360-100-r4-core.md` (J6 / J10 pin order, IO10 net label, IO39–42 ↔ TPx mapping, J2 PoE harness identity, `AirQ_Led` / `AirQ_Status_Led` reuse, FanTRIAC GPIO mapping) without re-litigating them. States explicitly that this index does not edit `config/hardware-catalog.json` (`S360-100` row stays `schematic_status: verified`, `schematic_file: docs/hardware/schematics/S360-100-R4.pdf`), does not edit `config/product-catalog.json`, `config/webflash-builds.json`, or `config/webflash-compatibility.json`, does not edit any product YAML, WebFlash wrapper, or package YAML, does not change WebFlash availability, does not regenerate firmware, does not create releases, does not unblock FanTRIAC (HW-005 stays a separate gate), and does not promote Sense360 LED into the Release-One config string. Release-One stays `Ceiling-POE-VentIQ-RoomIQ`; the LED preview path `Ceiling-POE-VentIQ-RoomIQ-LED` is unchanged. Follow-up PR list: HW-ASSETS-003 / 004 / 005 / 006 (expected only if artifact sources are provided for the named boards), HW-GAP-001, S360-100-BENCH-001. | Keep. |
| `docs/compliance/mains-voltage-uk-eu-assessment.md` | `current` | COMPLIANCE-001 mains-voltage UK / EU compliance-assessment tracker for `S360-400` Sense360 240v PSU and `S360-320` Sense360 TRIAC; expands the mains-voltage safety / compliance note in `docs/hardware/remaining-board-documentation-audit.md` into a per-board evidence checklist (product classification, protection-class decision tree, standards / regulations applicability, electrical-safety topics, EMC topics, preview-vs-stable evidence, technical-file checklist, DoC checklist, open questions for compliance engineer / test lab, release blockers); documentation only; makes no CE / UKCA / LVD / EMC / RED / RoHS / "safe for mains" / "approved for mains" claim and uses `Likely applicable` / `To be confirmed` / `Requires qualified review` / `Not proven by this repository` framing throughout; preserves the FanTRIAC HW-005 blocked status, the Sense360 LED Release-One-excluded status, every `config/hardware-catalog.json` `schematic_status` value, every `config/product-catalog.json` lifecycle status, and the Release-One PoE-only config string `Ceiling-POE-VentIQ-RoomIQ`; no firmware / product / config / workflow / build-matrix change. | Keep. |
| `docs/product-onboarding.md` (PRODUCT-005 cross-link refresh; RELEASE-005 LED proof refresh) | `current` | PRODUCT-004 cross-doc product onboarding guide. Orders the existing guardrails (hardware audit, mains-voltage compliance tracker, product catalog, consistency validator, WebFlash build matrix, release-notes generator, build / release proof, WebFlash handoff) into a safe sequence for adding a new product / config; lists preview-vs-production evidence gates, where each source of truth lives, the read-only commands to run, the explicit guardrails ("do not mark `production` just because YAML compiles", "do not add blocked products to the build matrix", "do not add FanTRIAC until HW-005 evidence changes", "do not add `LED` to Release-One without an LED token and hardware evidence", "do not treat `legacy-compatible` as WebFlash-shippable", "do not use mains-voltage boards before compliance review", "do not hand-edit generated manifests"), a Release-One worked example and a blocked-FanTRIAC worked example, and the future WebFlash handoff contract; documentation only; preserves the Release-One product / artifact / build matrix / compatibility JSON / hardware SKUs / catalog statuses / FanTRIAC HW-005 blocked status / Sense360 LED Release-One-excluded status. PRODUCT-005 refreshes the LED guardrail and the See-also list with a pointer to `docs/product-led-preview-decision.md` and the PRODUCT-006 / PRODUCT-007 / PRODUCT-008 / PRODUCT-009 follow-up PR sequence. RELEASE-005 updates the LED guardrail and the `docs/webflash-release-proof.md` See-also entry to record that the LED preview build / release proof is now recorded (tag `v1.0.0-led-preview`, run `25918422743`, artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` (1,135,904 bytes; SHA256 `93310d2cbc27355e399f36a232336b6b9075dacfc178d603c7a92aa1089182d3`), validators passed); the LED catalog entry stays `preview`; Release-One stays unchanged; FanTRIAC stays blocked; WebFlash-side import remains the only outstanding step before LED becomes WebFlash-shippable. | Keep. |
| `docs/product-led-preview-decision.md` (RELEASE-005 LED proof refresh) | `current` | PRODUCT-005 LED preview product path decision doc. Records that verified Sense360 LED schematic evidence (HW-007 / HW-008) plus the ceiling LED package pin fix (HW-010) do not by themselves make Sense360 LED WebFlash-shippable; enumerates the current evidence, the canonical LED-bearing config string `Ceiling-POE-VentIQ-RoomIQ-LED`, the catalog status options against the consistency validator's lifecycle rule blocks, and the product YAML / WebFlash wrapper / build-matrix entry / release-notes draft / build-release proof artefacts that would still be required. Decision table covers Options A–E (documented only / `compile-only` catalog entry / `preview` entry without build matrix / `preview` entry with wrapper + build matrix / Release-One `production` edit) and picks **Option A for this PR, with Option C later**. Defines the scoped follow-up PR sequence: PRODUCT-006 (add LED-bearing product YAML), PRODUCT-007 (add `compile-only` catalog entry), PRODUCT-008 (add WebFlash wrapper and promote to `preview`), PRODUCT-009 (add `preview` build to the build matrix + record a build / release proof + re-scope `tests/test_led_package_mapping.py` LED-exclusion to the Release-One build only + update `scripts/generate_webflash_release_notes.py` so the LED-bearing build emits Sense360 LED as a Feature). States the guardrails: verified LED schematic + fixed package pin mapping does not equal shippable product; LED is still not in current Release-One; WebFlash must not expose LED until there is a catalog-eligible product, artifact, and manifest; FanTRIAC remains unrelated and blocked. Documentation only; preserves the Release-One product / artifact / build matrix / compatibility JSON / hardware-catalog statuses / product-catalog statuses / FanTRIAC HW-005 blocked status / mains-voltage compliance status / Sense360 LED Release-One-excluded status; PRODUCT-005 adds no product YAML, no WebFlash wrapper, no catalog entry, no build-matrix entry, no release-notes draft, no tests, no scripts, no workflow change. RELEASE-005 updates the PRODUCT-009 outstanding-proof paragraph and the "Current evidence" no-artifact bullet to reflect that the LED preview build / release proof is now recorded (tag `v1.0.0-led-preview`, run `25918422743`, artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` (1,135,904 bytes; SHA256 `93310d2cbc27355e399f36a232336b6b9075dacfc178d603c7a92aa1089182d3`)), and updates the See-also pointer to `docs/webflash-release-proof.md` to mention the RELEASE-005 backfill; the LED catalog entry stays `preview`, Release-One stays unchanged, FanTRIAC stays blocked, and WebFlash-side import remains the only outstanding step. | Keep. |
| `docs/preview-to-stable-promotion-gates.md` (RELEASE-006) | `current` | RELEASE-006 canonical, cross-cutting preview-to-stable promotion gate document. Defines, for any future preview product (today the LED preview; tomorrow AirIQ-bearing / FanRelay-bearing / FanPWM-bearing / FanDAC-bearing / PWR-bearing variants), what evidence + sign-offs are required to promote a preview build to `status: production` / `channel: stable`. Includes: a 17-row gate summary table (product YAML, WebFlash wrapper, catalog preview entry, build-matrix preview entry, preview release artifact, preview release proof recorded, WebFlash import, live preview deploy, real WebFlash flash proof (WF-HW-TEST-001), hardware bench verification, stable release notes, production catalog promotion, stable build artifact, stable WebFlash import, REQUIRED_CONFIGS decision, kit / UI decision, human approval) with an owning-repo column and a live LED-preview status column; required upstream / firmware / hardware / WebFlash / operator evidence; per-field promotion diffs for `config/product-catalog.json` and `config/webflash-builds.json`; the human approval checklist (hardware, release engineer, WebFlash operator, compliance if mains, REQUIRED_CONFIGS decision, kit decision, release authority); the explicit "preview artifact + WebFlash import + deployed manifest do not equal stable" guardrails; the separate `REQUIRED_CONFIGS` policy (a stable build is **not** automatically added to baseline-health REQUIRED_CONFIGS — that is a separate WebFlash decision); the separate kit policy (a stable build does **not** automatically get a kit — that is a separate WebFlash product decision); a six-PR follow-up sequence for a future stable promotion (hardware bench verification → operator flash proof → stable release-notes + tag → catalog + build-matrix promotion → WebFlash stable import → optional REQUIRED_CONFIGS / kit PRs); and an LED preview case study marking rows 1–8 (preview floor) `done` and rows 9–17 explicitly `pending` / `decision needed` (operator flash proof WF-HW-TEST-001, S360-300 bench verification of harness rail / LED count / harness identity per `docs/hardware/s360-300-r4-led.md`, stable release notes, production catalog promotion, stable build artifact, stable WebFlash import, REQUIRED_CONFIGS decision, kit decision, recorded human approval). RELEASE-006 itself is documentation only: no `config/*`, `products/*`, `products/webflash/*`, `packages/*`, `scripts/*`, `tests/*`, `.github/workflows/*`, `components/*`, or `include/*` change; no firmware regenerated; no LED promotion (LED catalog stays `status: preview`, `channel: preview`); no Release-One change (`Ceiling-POE-VentIQ-RoomIQ`, `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag `v1.0.0`); no FanTRIAC unblock (HW-005 stays open; FanTRIAC is called out as the canonical blocked-module example and is explicitly **not** on the stable promotion path); no `REQUIRED_CONFIGS` or kit additions in the WebFlash repo. Cross-linked from `docs/product-onboarding.md`, `docs/product-led-preview-decision.md`, `docs/webflash-release-proof.md`, `docs/webflash-release-handoff.md`, and `docs/hardware/s360-300-r4-led.md` (Open Questions section). | Keep. |
| `docs/webflash-compatibility-taxonomy-audit.md` | `current` | COMPAT-001 per-token audit of `config/webflash-compatibility.json` against `config/product-catalog.json`, `config/webflash-builds.json`, `config/hardware-catalog.json`, `docs/hardware/remaining-board-documentation-audit.md`, `docs/compliance/mains-voltage-uk-eu-assessment.md`, and `docs/product-onboarding.md`. Records the source-of-truth separation (taxonomy / lifecycle / build matrix / hardware), the explicit "taxonomy != shippability" policy, a full per-token decision table (Ceiling, POE, PWR, USB, AirIQ, VentIQ, RoomIQ, FanRelay, FanPWM, FanDAC, FanTRIAC, LED, Voice) with hardware-evidence and follow-up columns, the current Release-One mapping, the blocked / excluded modules summary (FanTRIAC per HW-005, LED per Release-One config-string policy), the future-token policy, a test-coverage summary (existing tests + the six drift-protection tests added in the same PR), recommended follow-up PRs (HW-007 schematic ingest, future LED variant, FanTRIAC unblock, AirIQ / FanRelay / FanPWM / FanDAC preview entries, future PWR-bearing entry, optional forbidden-token alignment with `docs/webflash-contract.md` §3), and an explicit do-not-change list; flags that new schematic PDFs for `S360-100`, `S360-200`, `S360-210`, `S360-211`, and `S360-300` are deferred to HW-007 and do not change COMPAT-001 decisions; documentation only; preserves the Release-One product / artifact / build matrix / compatibility JSON / hardware SKUs / catalog statuses / FanTRIAC HW-005 blocked status / Sense360 LED Release-One-excluded status. HW-007 has now landed: the HW-007 note block is refreshed to record that the PDFs and per-board AirIQ / VentIQ / LED docs are committed and that the JSON `schematic_status` refresh is deferred to HW-008 (per-token cells for AirIQ / VentIQ / LED gain inline pointers to the new docs; no verdict / shippability cell changes; the VentIQ "schematic verification pending" caveat is retained until HW-008). | Keep. |
| `docs/hardware/schematics/` | `current` | HW-007 schematic evidence directory. Contains the committed module-side schematic PDFs: `S360-100-R4.pdf` (Core), `S360-200-R4.pdf` (RoomIQ), `S360-210-R4.pdf` (AirIQ), `S360-211-R4.pdf` (VentIQ), `S360-300-R4.pdf` (Sense360 LED). Each PDF is the authoritative source of truth for its corresponding standalone reference doc under `docs/hardware/`. The PDFs do not include FanTRIAC (`S360-320`), Relay (`S360-310`), PWM (`S360-311`), DAC (`S360-312`), 240v PSU (`S360-400`), or PoE PSU (`S360-410`) — those module-side schematics are still uncommitted post-HW-007. | Keep. |
| `docs/hardware/s360-210-r4-airiq.md` | `current` | HW-007 standalone pin / connector reference doc for `S360-210-R4` Sense360 AirIQ. Mirrors the structure of `docs/hardware/s360-100-r4-core.md` / `docs/hardware/s360-200-r4-roomiq.md`: board identity, schematic source (citing `schematics/S360-210-R4.pdf`), main components visible on the sheet (SGP41, SCD41, SFA40 connector, SPS30 connector, MICS-4514 + STM8 I²C-bridge sub-sheet), Core-side J9 mating table, I²C bus, Open Questions, firmware-mapping notes, and an explicit HW-007 scope / non-scope block. Explicitly states AirIQ remains mutually exclusive with VentIQ, not in Release-One, and not WebFlash-shippable — HW-007 only improves legacy / manual hardware documentation. JSON `schematic_status` flip is now refreshed by HW-008 (`verified`, `schematic_file: docs/hardware/schematics/S360-210-R4.pdf`); HW-008 does not change AirIQ's WebFlash-shippability, mutex, or Release-One status. | Keep. |
| `docs/hardware/s360-211-r4-ventiq.md` | `current` | HW-007 standalone pin / connector reference doc for `S360-211-R4` Sense360 VentIQ. Same template as the AirIQ doc. Captures SGP41 on board, IR-temperature connector, SPS30 connector, on-board fan-relay drive circuitry, and Core-side J9 mating. Explicitly records: Release-One config string remains `Ceiling-POE-VentIQ-RoomIQ`; package filename `airiq_bathroom_base.yaml` retained per WebFlash contract §6; mains-side topology, contact rating, and creepage / clearance for the on-board relay are tracked separately under COMPLIANCE-001 — HW-007 makes no compliance claim. JSON `schematic_status` and the "schematic verification pending" caveat in `release-one-hardware-audit.md` / `webflash-compatibility-taxonomy-audit.md` are now refreshed by HW-008 (JSON: `verified`, `schematic_file: docs/hardware/schematics/S360-211-R4.pdf`; the caveat is retired). HW-008 does not change Release-One config / build matrix / artifact / lifecycle / mains compliance. | Keep. |
| `docs/hardware/s360-300-r4-led.md` (HW-010 refresh) | `current` | HW-007 standalone reference doc for `S360-300-R4` Sense360 LED. Captures J1 (3-pin: LED_DATA / +5V / GND) and the on-board WS2812B LED chain. Explicitly records: Sense360 LED is **not** in Release-One; the Release-One config string `Ceiling-POE-VentIQ-RoomIQ` carries no `LED` token; the Release-One YAML omits LED package includes on purpose. JSON `schematic_status` flip refreshed by HW-008 (`verified`, `schematic_file: docs/hardware/schematics/S360-300-R4.pdf`); HW-008 did **not** add `LED` to the Release-One config string. The `GPIO14` (package) vs `IO38` (Core schematic) `LED_DATA` discrepancy at the package level has since been **resolved by HW-010** — the ceiling LED package now binds `led_data_pin: GPIO38`. HW-010 did not add `LED` to the Release-One config string, did not add a WebFlash LED build, did not add a product-catalog LED entry, did not promote Sense360 LED to WebFlash-shippable, and did not change the FanTRIAC HW-005 blocker. The wall LED and legacy S3 Core packages remain unresolved at the package level. | Keep. |
| `docs/hardware/s360-300-r4-led.md` (S360-300-BENCH-001 section) | `current` | S360-300-BENCH-001 bench-verification tracking record for the Sense360 LED (`S360-300-R4`) board. Companion to the schematic-side Open Questions in the same doc and to RELEASE-006 row 10 (hardware bench verification) in `docs/preview-to-stable-promotion-gates.md`. Records the bench gate as **`pending — bench hardware evidence required`**: no operator, no bench date, no physical S360-300 board / Core board / revision identification, no harness used, no Core / LED connector exercised, no rail measurement (`J1` pin 2 `+5V` vs `+3.3V`), no data-pin / signal-path observation, no ground / power continuity observation, no LED count, no LED type identification, no test / preview firmware used, no flash source, no observed LED ring behaviour (boot pattern, brightness, colour order), no photos / screenshots / serial logs / scope captures / measurements, no known anomalies. The four per-question rows (harness rail per Open Question 1; LED count per Open Question 2; harness identity per Open Question 4; observed LED ring behaviour) are each `pending — bench hardware evidence required`. Allowed status vocabulary fixed at: `pending — bench hardware evidence required` / `partial — some bench evidence recorded, but open questions remain` / `verified — all listed bench questions answered by evidence` / `failed / blocked — bench test produced a blocking issue`. Implicit acceptance is not allowed; values are not invented. Section is documentation only and explicitly **does not**: promote Sense360 LED to `status: production` / `channel: stable`; add `LED` to the Release-One config string (Release-One stays `Ceiling-POE-VentIQ-RoomIQ`, artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag `v1.0.0`); add Sense360 LED to WebFlash-side `REQUIRED_CONFIGS` (default per RELEASE-006 §REQUIRED_CONFIGS policy stays **do not add**); add a Sense360 LED kit entry to WebFlash-side `scripts/data/kits.json` (default per RELEASE-006 §Kit policy stays **do not add**); substitute for the WebFlash operator flash proof (`WF-HW-TEST-001` row 9 stays separately `pending` in the WebFlash repo); flip `S360-300` in `config/hardware-catalog.json` (already `schematic_status: verified` under HW-008 — bench evidence is a separate axis); change FanTRIAC (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`); change mains-voltage compliance status for `S360-320` or `S360-400` (owned by COMPLIANCE-001); advance any future "RELEASE-007" LED stable promotion (any such promotion still requires closing all four bench questions here **and** clearing every other RELEASE-006 row). Adds no edits to `config/*`, `products/*`, `products/webflash/*`, `packages/*`, `tests/*`, `scripts/*`, `components/*`, `include/*`, or `.github/workflows/*`. Cross-linked from `docs/hardware/s360-300-r4-led.md` (Open Questions section), `docs/preview-to-stable-promotion-gates.md` (row 10 and §Pending → Row 10 bullet), and `docs/hardware/board-readiness-matrix.md` (S360-300 productization-axis row, S360-300 §Open work / stable gate bullet, §Preserved guardrail block). | Keep. |
| `docs/hardware/s360-100-r4-core.md` (HW-007 cross-link refresh) | `current` | Existing Core hardware reference doc; HW-007 changes the `Schematic source` table to point at `[`schematics/S360-100-R4.pdf`](schematics/S360-100-R4.pdf)` and adds a one-line `HW-007 — PDF committed` admonition. No pin tables, Open Questions, or reconciliation flags changed. | Keep. |
| `docs/hardware/s360-100-r4-core.md` (S360-100-BENCH-001 section) | `current` | S360-100-BENCH-001 bench / manufacturing tracking record for the Sense360 Core (`S360-100-R4`) board. Companion to the schematic-side Open Questions in the same doc and to the artifact-side Open Questions in `docs/hardware/artifacts/S360-100-R4.md` (HW-ASSETS-002). Records the Core board bench / manufacturing gate as **`pending — bench/manufacturing evidence required`**: no operator / reviewer, no review date, no physical S360-100-R4 board (serial / batch) identification, no board revision marking, no connector silkscreen / J-numbering observation, no `J2` PoE harness identity, no `J6` 1-to-13 silkscreen pin order, no `J10` 1-to-12 silkscreen pin order, no `IO10` net label observation, no `IO39`–`IO42` ↔ TP mapping, no JTAG-header observation, no `AirQ_Led` / `AirQ_Status_Led` reuse observation, no BOM review (`bc386261-S360100R4_BOM.xlsx`, 12,543 B), no CPL review (`d5bb9e7b-S360100R4pos.csv`, 4,803 B), no Gerber review (`2248fe0e-S360100R4gerbers.zip`, 290,097 B, 4-layer `F_Cu` / `In1_Cu` / `In2_Cu` / `B_Cu`), no STEP / mechanical review (`0a7f7965-S360100R4.step`, 6,335,475 B), no schematic-to-fabrication consistency observation, no photos / silkscreen captures / scope traces / continuity measurements / serial logs, no known anomalies. The per-question rows (`J2` PoE harness identity; `J6` 1-to-13 silkscreen pin order; `J10` 1-to-12 silkscreen pin order; `IO10` net label; `IO39`–`IO42` ↔ TPx mapping; JTAG / programming header existence; `AirQ_Led` / `AirQ_Status_Led` reuse on VentIQ vs AirIQ; BOM / CPL / Gerber / STEP manufacturing-artifact review; gerber inner-filename prefix `Sense360_Core_R4-*` vs canonical `S360-100-R4-*`; schematic-to-fabrication consistency) are each `pending — bench/manufacturing evidence required`. Allowed status vocabulary fixed at: `pending — bench/manufacturing evidence required` / `partial — some evidence recorded, but open questions remain` / `verified — all listed Core board bench/manufacturing questions answered by evidence` / `failed / blocked — evidence produced a blocking issue`. Implicit acceptance is not allowed; values are not invented. Section is documentation only and explicitly **does not**: change Release-One (Release-One stays `Ceiling-POE-VentIQ-RoomIQ`, artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag `v1.0.0`); change the LED preview path (`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`, `channel: preview`); unblock FanTRIAC (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`); change mains-voltage compliance status for `S360-320` or `S360-400` (owned by COMPLIANCE-001); flip `S360-100` in `config/hardware-catalog.json` (already `schematic_status: verified` under HW-008 — bench/manufacturing evidence is a separate axis); add or modify any product YAML, WebFlash wrapper, package YAML, WebFlash build, `REQUIRED_CONFIGS`, or kit entry; resolve any schematic-side Open Question on its own (it records bench / manufacturing observations against them); substitute for any Release-One firmware proof (REL-001) or LED preview build / import / deploy proof (WF-LED-001 / WF-LED-002 / WF-LED-003 / WF-DEPLOY-001). Adds no edits to `config/*`, `products/*`, `products/webflash/*`, `packages/*`, `tests/*`, `scripts/*`, `components/*`, `include/*`, or `.github/workflows/*`. Cross-linked from `docs/hardware/s360-100-r4-core.md` (Open Questions section forward-pointer), `docs/hardware/artifacts/S360-100-R4.md` (Open Questions paragraph + Follow-up PRs row), `docs/hardware/board-readiness-matrix.md` (S360-100 productization-axis row, S360-100 §Board-by-board notes Open-work bullet, §Preserved guardrail block), `docs/hardware/firmware-package-mapping-audit.md` (Core J10 vs RoomIQ J6 row resolution paragraph), `docs/hardware/remaining-board-documentation-audit.md` (Sense360 Core §Evidence missing bullet), and `docs/release-one-hardware-audit.md` (PoE PSU + Core / RoomIQ connector findings rows). | Keep. |
| `docs/hardware/s360-320-r4-triac.md` (HW-PINMAP-320) | `current` | HW-PINMAP-320 per-board pin / package mapping audit doc for `S360-320-R4` Sense360 TRIAC (FanTRIAC). Records the audit as **`partial — schematic evidence available; package reconciliation, timing validation, and compliance/certification pending`**: the module-side schematic PDF `docs/hardware/schematics/S360-320-R4.pdf` and the curated artifact index `docs/hardware/artifacts/S360-320-R4.md` are both committed under HW-ASSETS-003, but the standalone schematic-backed reference doc, the pin-map reconciliation against the verified end-to-end ESP32 GPIO trace, the package YAML reconciliation, the timing / zero-cross / real-load bench validation, the mains-voltage UK / EU compliance review, and any advanced / manual-warning WebFlash exposure are not produced by this PR. Consumes the HW-ASSETS-003 artifact index without rewriting it. Inventories the current committed evidence (committed module-side schematic PDF; curated artifact index; Core-side `J15` 4-pin connector capture in `docs/hardware/s360-100-r4-core.md` §J15 — `+3.3V` / `TRI_GPIO1` / `TRI_GPIO2` / `GND`; module-side `J3` 4-pin "From Core" capture with `+3V3` / `ESP_GPIO1` / `ESP_GPIO2` / `GND`; TRIAC switching device `Q1 BT136S-600D,118`; optotriac driver `U1 MOC3023M` with `R3 220 Ω` LED-side limit, `R1 1 kΩ` gate resistor, `R2 100 Ω` AC-side return snub; zero-cross optocoupler `OK1 EL814` with symmetric `R5 33 kΩ` / `R6 33 kΩ` mains-side bias and `R4 10 kΩ` pull-up to `+3V3`; 3-pin AC LINE `J1`; 2-pin LOAD `J2`; no on-board controller IC; firmware package `packages/expansions/fan_triac.yaml` with BLOCKED / UNVERIFIED banner and `ac_dimmer` driver topology requiring direct interrupt-capable ESP32 GPIOs; blocked reference product YAML `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml` with placeholder `fan_triac_gate_pin: GPIO5` / `fan_triac_zc_pin: GPIO6`; blocked WebFlash wrapper `products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`; product-catalog entry `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` at `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`; `FanTRIAC` token reservation in `config/webflash-compatibility.json` `canonical_modules` subject to the fan-driver `max-one-of` rule and carried in Release-One / LED preview `blocked_modules` lists; existing classifications in `docs/hardware/board-readiness-matrix.md`, `docs/hardware/remaining-board-documentation-audit.md`, `docs/hardware/firmware-package-mapping-audit.md`, `docs/product-availability-taxonomy.md`, `docs/hardware/hardware-artifact-policy.md`). Records the `TRI_GPIO*` (Core) vs `ESP_GPIO*` (Module) net-name divergence as **conflict / unresolved** — same physical wires, different labels — and owes the canonical-naming choice to HW-PINMAP-320-FOLLOWUP. Records the `ac_dimmer`-vs-SX1509 timing constraint as **conflict / unresolved**: `ac_dimmer` requires direct interrupt-capable ESP32 GPIOs for both `gate_pin` and `zero_cross_pin`; the Core-side `TRI_GPIO1` / `TRI_GPIO2` nets continue to route via the SX1509 expander (`U3`) on the Core sheet, which the timing analysis in `docs/release-one-hardware-audit.md#timing-constraint-ac_dimmer-vs-sx1509-expander` rejects. Records that the module-side schematic eliminates Option (b) (replacement non-`ac_dimmer` driver targeting an on-board controller IC) from the HW-005 missing-evidence checklist for this revision (no on-board controller IC), but does **not** unblock HW-005 — Option (a) (direct ESP32 GPIOs traced end-to-end through `S360-100-R4` + `S360-320`) still requires the Core re-trace. Records the placeholder `fan_triac_gate_pin: GPIO5` / `fan_triac_zc_pin: GPIO6` mapping as **disagreeing with the Core schematic** (RoomIQ J10 nets `SEN0609_TX` / `out(gpio6)` already claim those pins). Records the AC LINE `J1` 3-pin function (L / N / PE / doubled-line) as **not recorded** — requires silkscreen / PCB-source evidence and is COMPLIANCE-001-adjacent. Records the intended **advanced / manual-warning long-term product posture** for FanTRIAC: **visible / selectable**, **buildable after package evidence**, **installable only through an advanced / manual-warning path**; **not** Release-One, **not** REQUIRED_CONFIGS, **not** recommended, **not** kit / default, **not** compliance-certified. **Compliance status is not a reason to remove or hide the board from the repo; it is a reason to keep explicit warning / advanced-manual / non-certified language attached to every surface that mentions FanTRIAC, until both HW-005 and COMPLIANCE-001 clear.** The advanced / manual-warning posture is **intent only**; this PR does **not** realise it. Lists missing evidence in full: confirmed pin map (HW-PINMAP-320-FOLLOWUP), package YAML reconciliation (PACKAGE-TRIAC-001 / `PACKAGE-GAP-001` FanTRIAC slice), timing validation, zero-cross / phase-control validation, real-load test evidence, thermal / safety review, mains compliance / certification (COMPLIANCE-001), operator flash / runtime validation, advanced-warning UX approval, release / import gate approval, schematic-status promotion PR (HW-CATALOG-320). Defines the follow-up PR sequence (`HW-PINMAP-320-FOLLOWUP` standalone schematic-backed reference doc + pin-map reconciliation; `HW-005` unblock work — Option (a) Core re-trace; separate JSON PR `HW-CATALOG-320` for `S360-320` `schematic_status` promotion; `PACKAGE-TRIAC-001` for package YAML reconciliation; `COMPLIANCE-001` independent mains-voltage review; `PRODUCT-TRIAC-001` catalog-policy reclassification to advanced / manual-warning; `PRODUCT-TRIAC-002` product YAML / catalog entry rework; `WF-TRIAC-001` advanced / manual-warning WebFlash exposure; `RELEASE-TRIAC-001` advanced-channel build / release artifact; `WF-IMPORT-TRIAC-001` advanced / manual artifact import). Documentation only and explicitly **does not**: edit `config/hardware-catalog.json`, `config/product-catalog.json`, `config/webflash-builds.json`, or `config/webflash-compatibility.json`; add or change `schematic_file` for `S360-320`; flip `S360-320` `schematic_status` from `cataloged_unverified`; mark `S360-320` `verified`; mark the pin map confirmed; mark `packages/expansions/fan_triac.yaml` `confirmed-ok` (its status stays `package-yaml-pending` / `needs-package-reconciliation`); remove the BLOCKED / UNVERIFIED banner or the mains-voltage / qualified-electrician warnings from `packages/expansions/fan_triac.yaml`; edit any package YAML (`packages/expansions/fan_triac.yaml` stays unchanged); edit any product YAML (`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml` stays unchanged); edit any WebFlash wrapper (`products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml` stays unchanged); edit the curated artifact index `docs/hardware/artifacts/S360-320-R4.md`; edit the schematic PDF `docs/hardware/schematics/S360-320-R4.pdf` (byte-identical to HW-ASSETS-003 commit); resolve the `TRI_GPIO*` / `ESP_GPIO*` naming reconciliation; resolve the Core-side source ESP32 GPIO question for `TRI_GPIO1` / `TRI_GPIO2`; resolve the AC LINE `J1` 3-pin function; perform any bench / silkscreen / real-load measurement; unblock FanTRIAC under HW-005 (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`); clear COMPLIANCE-001 for `S360-320` or `S360-400` (compliance status is owned by `docs/compliance/mains-voltage-uk-eu-assessment.md`); claim that FanTRIAC is compliance-certified; promote `S360-320` to `preview` / `stable` / `production`; add a `FanTRIAC` token to any Release-One or preview config string; add a `FanTRIAC`-bearing entry to `config/webflash-builds.json`; add FanTRIAC to `release_one_required_configs` / REQUIRED_CONFIGS; add FanTRIAC to any kit / default onboarding flow; make FanTRIAC recommended; generate firmware; create a GitHub Release or tag; perform a WebFlash import; change Release-One (`Ceiling-POE-VentIQ-RoomIQ`, `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag `v1.0.0`); change the LED preview path (`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`, `channel: preview`); resolve the Core J10 vs RoomIQ J6 pin-order open question; resolve the systemic Core abstract-bus mismatch (`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3). Adds no edits to `config/*`, `products/*`, `products/webflash/*`, `packages/*`, `scripts/*`, `tests/*`, `components/*`, `include/*`, `.github/workflows/*`, `manifest.json`, or `firmware/sources.json`. Cross-linked from `docs/hardware/board-readiness-matrix.md` (`S360-320` evidence-axis row, `S360-320` productization-axis row, `S360-320` board-by-board notes, follow-up-PR-sequence item #4), `docs/hardware/remaining-board-documentation-audit.md` (Sense360 TRIAC (`S360-320`) decision-table row + audit-doc bullet), `docs/hardware/firmware-package-mapping-audit.md` (FanTRIAC placeholder GPIOs schematic-evidence list), and `docs/product-availability-taxonomy.md` (`S360-320 Sense360 TRIAC` snapshot row). | Keep. |
| `docs/hardware/s360-311-r4-pwm.md` (HW-PINMAP-311) | `current` | HW-PINMAP-311 per-board pin / package mapping audit doc for `S360-311-R4` Sense360 PWM. Records the audit as **`partial — schematic evidence available; package reconciliation pending`**: the module-side schematic PDF `docs/hardware/schematics/S360-311-R4.pdf` and the curated artifact index `docs/hardware/artifacts/S360-311-R4.md` are both committed under HW-ASSETS-003, but the standalone schematic-backed reference doc, the pin-map reconciliation, and the package YAML reconciliation are not produced by this PR. Consumes the HW-ASSETS-003 artifact index without rewriting it. Inventories the current committed evidence (committed module-side schematic PDF; curated artifact index; Core-side `J6` 13-pin connector capture in `docs/hardware/s360-100-r4-core.md` §J6 — `+5V` / `GND` / `TachIO` / `TachPMW1..4` / `Pul_Cou1..4`, pin order **verify** against silkscreen per Open Question #9; Core-side `Fan / driver outputs` showing `TachPMW*` / `Pul_Cou*` driven by SX1509 expander, `TachIO` direct from ESP32 `IO16`; SX1509 channel map in `packages/expansions/gpio_expander_sx1509.yaml` channels 0–3 fan PWM, 4–7 tach; single-channel firmware package `packages/expansions/fan_pwm.yaml` with `fan_pwm_pin: ${fan_pwm_pin}` / `fan_tach_pin: ${fan_tach_pin}` inherited from parent Core package; legacy four-channel firmware package `packages/expansions/sense360_fan_pwm.yaml` used only by legacy-compatible `products/sense360-fan-pwm.yaml`; `FanPWM` token reservation in `config/webflash-compatibility.json` `canonical_modules` subject to the fan-driver `max-one-of` rule; existing classifications in `docs/hardware/board-readiness-matrix.md`, `docs/hardware/remaining-board-documentation-audit.md`, `docs/hardware/firmware-package-mapping-audit.md`, `docs/product-availability-taxonomy.md`, `docs/hardware/hardware-artifact-policy.md`). Records the schematic-vs-package mapping disagreement as **unresolved by this PR**: `packages/hardware/sense360_core_ceiling.yaml` binds `fan_pwm_pin: ${expansion_gpio1}` (= `GPIO5`) and `fan_tach_pin: ${expansion_gpio2}` (= `GPIO6`); `packages/hardware/sense360_core.yaml` binds `expansion_gpio1` / `expansion_gpio2` to `GPIO4` / `GPIO5`; the verified Core schematic routes `TachPMW1..4` / `Pul_Cou1..4` through the SX1509 expander (channels 0–3 / 4–7), not directly via ESP32 expansion GPIOs, and the direct-ESP32 `TachIO` net is on `IO16` (not `GPIO5` / `GPIO6`). Resolution belongs to the systemic Core abstract-bus rebind owned by `docs/release-one-hardware-audit.md` Required follow-ups #2 / #3 plus a future evidence-bearing HW-PINMAP-311-FOLLOWUP, not to this PR. Records the UART-on-`J3`-pins-11/12 question as **unresolved by this PR**: the module-side `J3` capture labels pins 11 / 12 as `UART_RX` / `UART_TX` routed on-board to the module-side Nextion `J6` 4-pin connector; the Core-side `J6` capture in `docs/hardware/s360-100-r4-core.md` §J6 does not list any UART pins on the 13-pin connector. Records the `"NINE 4pin FANs"` schematic section-title question as **unresolved by this PR** (four 4-pin fan output connectors `J1` / `J2` / `J4` / `J5` visible; title says "NINE"). Records the single-channel-vs-four-channel canonical-abstraction decision as **unresolved by this PR** (`fan_pwm.yaml` binds one channel; the board exposes four fan outputs; legacy `sense360_fan_pwm.yaml` binds four with direct ESP32 GPIO mappings that also disagree with the schematic). Lists missing evidence in full: bench verification (PWM / tach / `TachIO` waveforms), silkscreen verification of `J6` 1-to-13 / `J3` 1-to-13 pin orders, harness verification (13-pin Core ↔ module cable inspection), KiCad source / KiCad PCB / project metadata, BOM, CPL, gerbers, drill files, STEP, board images, tach waveform verification, operator validation, standalone schematic-backed reference doc (`HW-PINMAP-311-FOLLOWUP`). Defines the follow-up PR sequence (HW-PINMAP-311-FOLLOWUP standalone schematic-backed reference doc + pin-map reconciliation; separate JSON PR for `S360-311` `schematic_status` promotion; PACKAGE-GAP-001 FanPWM slice for package YAML reconciliation; PRODUCT-GAP-001 FanPWM slice for product YAML if/when decided; WEBFLASH-GAP-001 / RELEASE-GAP-001 / WF-IMPORT-GAP-001 FanPWM slice for wrapper + build + release + import; stable promotion goes through the 17-row `docs/preview-to-stable-promotion-gates.md` gate). Documentation only and explicitly **does not**: edit `config/hardware-catalog.json`, `config/product-catalog.json`, `config/webflash-builds.json`, or `config/webflash-compatibility.json`; add or change `schematic_file` for `S360-311`; flip `S360-311` `schematic_status` from `cataloged_unverified`; mark `S360-311` `verified`; mark the pin map confirmed; mark `packages/expansions/fan_pwm.yaml` `confirmed-ok`; edit any package YAML (`packages/expansions/fan_pwm.yaml`, `packages/expansions/sense360_fan_pwm.yaml`, `packages/expansions/gpio_expander_sx1509.yaml`, `packages/hardware/sense360_core_ceiling.yaml`, `packages/hardware/sense360_core.yaml` all stay unchanged); edit the curated artifact index `docs/hardware/artifacts/S360-311-R4.md`; edit the schematic PDF `docs/hardware/schematics/S360-311-R4.pdf` (byte-identical to HW-ASSETS-003 commit); resolve the SX1509-channel vs direct-ESP32-GPIO mapping disagreement; resolve the UART-on-`J3`-pins-11/12 routing question; resolve the `"NINE 4pin FANs"` section-title question; resolve the single-channel-vs-four-channel canonical-abstraction decision; add a product YAML; add a WebFlash wrapper; add a build-matrix entry; generate firmware; create a GitHub Release or tag; perform a WebFlash import; promote `S360-311` to `preview` / `stable` / `production`; add a `FanPWM` token to any Release-One or preview config string; change Release-One (`Ceiling-POE-VentIQ-RoomIQ`, `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag `v1.0.0`); change the LED preview path (`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`, `channel: preview`); unblock FanTRIAC (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`); change the mains-voltage compliance status for `S360-320` or `S360-400` (owned by COMPLIANCE-001); resolve the Core J10 vs RoomIQ J6 pin-order open question; resolve the systemic Core abstract-bus mismatch (`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3). Adds no edits to `config/*`, `products/*`, `products/webflash/*`, `packages/*`, `scripts/*`, `tests/*`, `components/*`, `include/*`, or `.github/workflows/*`. Cross-linked from `docs/hardware/board-readiness-matrix.md` (`S360-311` evidence-axis row, `S360-311` board-by-board notes, follow-up-PR-sequence item #2, Missing / unfinished boards `S360-311` bullet, See-also per-board reference docs list), `docs/hardware/remaining-board-documentation-audit.md` (Sense360 PWM (`S360-311`) audit-doc bullet), `docs/hardware/firmware-package-mapping-audit.md` (See also entry recording the FanPWM SX1509-vs-direct-GPIO reconciliation as deferred), and `docs/product-availability-taxonomy.md` (`S360-311 Sense360 PWM` snapshot row). | Keep. |
| `docs/hardware/s360-312-r4-dac.md` (HW-PINMAP-312) | `current` | HW-PINMAP-312 per-board pin / package mapping audit doc for `S360-312-R4` Sense360 DAC. Records the audit as **`partial — schematic evidence available; package reconciliation pending`**: the module-side schematic PDF `docs/hardware/schematics/S360-312-R4.pdf` and the curated artifact index `docs/hardware/artifacts/S360-312-R4.md` are both committed under HW-ASSETS-003, but the standalone schematic-backed reference doc, the pin-map reconciliation, and the package YAML reconciliation are not produced by this PR. Consumes the HW-ASSETS-003 artifact index without rewriting it. Inventories the current committed evidence (committed module-side schematic PDF; curated artifact index; Core-side `J7` 6-pin connector capture in `docs/hardware/s360-100-r4-core.md` §J7 — `+5V` / `I2C_SDA` / `I2C_SCL` / `UART_RX` / `UART_TX` / `GND`, no `verify` flag on the pin order; Core-side I²C bus capture showing `I2C_SDA` at ESP32 `IO48` with `R22 10 kΩ` pull-up and `I2C_SCL` at `IO45` with `R21 10 kΩ` pull-up; Core-side UART0 capture showing `TXD0` / `RXD0` ↔ `UART_TX` / `UART_RX` and "also used as boot log on USB"; dual-channel firmware package `packages/expansions/fan_gp8403.yaml` with `gp8403.i2c_id: ${fan_dac_i2c_id}` / `gp8403.address: ${fan_dac_address}` / `gp8403.voltage: ${fan_dac_voltage_mode}` and two `fan` speed entities; `FanDAC` token reservation in `config/webflash-compatibility.json` `canonical_modules` subject to the fan-driver `max-one-of` rule **and** the explicit `FanDAC` ↔ `AirIQ` mutex `rules.fandac_conflicts_with_airiq: true`; existing classifications in `docs/hardware/board-readiness-matrix.md`, `docs/hardware/remaining-board-documentation-audit.md`, `docs/hardware/firmware-package-mapping-audit.md`, `docs/product-availability-taxonomy.md`, `docs/hardware/hardware-artifact-policy.md`). Records the Core `J7` pin-1 `+5V` vs Module `J1` pin-1 `+3.3V` voltage-rail discrepancy as **unresolved by this PR**: the module schematic additionally labels the on-board MT3608 boost-converter `IN` pin as `+3.3V` while boosting to `+12V` for the fan outputs. Records the DIP-switch I²C address-selection scheme on `SW1` / `SW2` (6-position each, 4.7 kΩ pull-ups `R3` / `R5` / `R7` for `IC1` `A0` / `A1` / `A2` and `R4` / `R6` / `R8` for `IC2` `2A0` / `2A1` / `2A2`) as **unresolved by this PR**: the schematic shows the hardware but not the DIP-position-to-address mapping; `fan_gp8403.yaml` `${fan_dac_address}` defaults to `0x58` with `0x59` as the only alternate, and the package addresses `IC1` only. Records the UART0-vs-Nextion arbitration question as **unresolved by this PR**: Module `J1` pins 4 / 5 carry `UART_RX` / `UART_TX` routed on-board to Module `J7` 4-pin Nextion connector; Core ties the same nets to ESP32 `TXD0` / `RXD0` (UART0), which is also the boot-log path on USB; the package YAML binds no `uart:` or `display:` component on this pair. Records the stale header-comment block in `packages/expansions/fan_gp8403.yaml` lines 13–18 (`Pin 4 (SDA) → GPIO39`, `Pin 5 (SCL) → GPIO40`, `Pin 2 (3.3V) → Power`, `Pin 1 (GND) → Ground`) as **disagreeing with both the Core `J7` capture and the Module `J1` capture** (which agree pin 1 is a power rail, pin 2 is I²C SDA, pin 4 is UART RX, pin 5 is UART TX, pin 6 is GND; Core I²C is `IO48` / `IO45`, not `GPIO39` / `GPIO40`) — the active YAML body's `${fan_dac_i2c_id}` / `${fan_dac_address}` substitutions are abstract-bus inheritance and do not depend on the stale comment, but the comment is still a documentation-side disagreement and is recorded as unresolved by this PR. Records the dual-DAC capacity (two `GP8403-TC50-EW` `IC1` / `IC2` driving two 3-pin Cloudlift outputs `J2` / `J3`) as broader than the singular hardware-catalog `description` ("0 to 10V analog fan driver, for example Cloudlift S12"); broadening the catalog row is a separate later PR, not in scope here. Records the `J2` / `J3` Cloudlift output silkscreen pin-1 question and the `fan_dac_voltage_mode` 5 V vs 10 V hardware-jumper identification as additional unresolved items. Lists missing evidence in full: bench verification (DAC outputs / I²C bus exchange / Nextion-vs-boot-log arbitration), silkscreen verification of Core `J7` / Module `J1` / `J2` / `J3` pin orders, harness verification (6-pin Core ↔ module cable inspection), I²C address-selection measurement, `fan_dac_voltage_mode` jumper identification, KiCad source / KiCad PCB / project metadata, BOM, CPL, gerbers, drill files, STEP, board images, operator validation, standalone schematic-backed reference doc (`HW-PINMAP-312-FOLLOWUP`). Defines the follow-up PR sequence (HW-PINMAP-312-FOLLOWUP standalone schematic-backed reference doc + pin-map reconciliation + voltage-rail / I²C address / UART-arbitration / Cloudlift pin-order / voltage-mode-jumper resolution; separate JSON PR for `S360-312` `schematic_status` promotion; PACKAGE-GAP-001 FanDAC slice for package YAML reconciliation including the stale header-comment block; PRODUCT-GAP-001 FanDAC slice for product YAML if/when decided; WEBFLASH-GAP-001 / RELEASE-GAP-001 / WF-IMPORT-GAP-001 FanDAC slice for wrapper + build + release + import; stable promotion goes through the 17-row `docs/preview-to-stable-promotion-gates.md` gate; HW-ASSETS-003-followup if manufacturing evidence later arrives). Documentation only and explicitly **does not**: edit `config/hardware-catalog.json`, `config/product-catalog.json`, `config/webflash-builds.json`, or `config/webflash-compatibility.json`; add or change `schematic_file` for `S360-312`; flip `S360-312` `schematic_status` from `cataloged_unverified`; mark `S360-312` `verified`; mark the pin map confirmed; mark `packages/expansions/fan_gp8403.yaml` `confirmed-ok`; edit any package YAML (`packages/expansions/fan_gp8403.yaml`, `packages/hardware/sense360_core_ceiling.yaml`, `packages/hardware/sense360_core.yaml` all stay unchanged); edit the curated artifact index `docs/hardware/artifacts/S360-312-R4.md`; edit the schematic PDF `docs/hardware/schematics/S360-312-R4.pdf` (byte-identical to HW-ASSETS-003 commit); edit `docs/hardware/s360-100-r4-core.md` (the Core `J7` capture stays as it is; the voltage-rail discrepancy is recorded here and is not rewritten on the Core-side doc); resolve the Core `J7` pin-1 `+5V` vs Module `J1` pin-1 `+3.3V` voltage-rail discrepancy; resolve the DIP-switch I²C address-selection scheme; resolve the UART0-vs-Nextion arbitration question; resolve the stale header-comment connector / GPIO claims in `packages/expansions/fan_gp8403.yaml`; resolve the `fan_dac_voltage_mode` 5 V vs 10 V hardware-jumper identification; resolve the `J2` / `J3` Cloudlift output silkscreen pin-1 question; broaden the hardware-catalog `description` to record the dual-DAC capacity; add a product YAML; add a WebFlash wrapper; add a build-matrix entry; generate firmware; create a GitHub Release or tag; perform a WebFlash import; promote `S360-312` to `preview` / `stable` / `production`; add a `FanDAC` token to any Release-One or preview config string; relax or change the `FanDAC` ↔ `AirIQ` mutex; relax or change the fan-driver `max-one-of` rule; change Release-One (`Ceiling-POE-VentIQ-RoomIQ`, `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag `v1.0.0`); change the LED preview path (`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`, `channel: preview`); unblock FanTRIAC (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`); change the mains-voltage compliance status for `S360-320` or `S360-400` (owned by COMPLIANCE-001); resolve the Core J10 vs RoomIQ J6 pin-order open question; resolve the systemic Core abstract-bus mismatch (`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3). Adds no edits to `config/*`, `products/*`, `products/webflash/*`, `packages/*`, `scripts/*`, `tests/*`, `components/*`, `include/*`, or `.github/workflows/*`. Cross-linked from `docs/hardware/board-readiness-matrix.md` (`S360-312` evidence-axis row, `S360-312` productization-axis row, `S360-312` board-by-board notes, follow-up-PR-sequence item #3, Missing / unfinished boards `S360-312` bullet), `docs/hardware/remaining-board-documentation-audit.md` (Sense360 DAC (`S360-312`) audit-doc bullet), `docs/hardware/firmware-package-mapping-audit.md` (See also entry recording the FanDAC pin / package reconciliation as out-of-scope for HW-009 today), and `docs/product-availability-taxonomy.md` (`S360-312 Sense360 DAC` snapshot row). | Keep. |
| `docs/hardware/s360-310-r4-relay.md` (HW-PINMAP-310) | `current` | HW-PINMAP-310 per-board pin / package mapping audit doc for `S360-310-R4` Sense360 Relay. Records the audit as **`pending — schematic/design evidence required`**: no `S360-310-R4` schematic PDF is committed under `docs/hardware/schematics/`, no curated artifact index exists under `docs/hardware/artifacts/`, no standalone schematic-backed reference doc exists in the `docs/hardware/sXXX-r4-<role>.md` pattern, no upload of a module-side schematic was supplied to the task environment that produced the PR, no active product YAML consumes `S360-310`, no WebFlash wrapper / build-matrix entry / release artifact / WebFlash import exists. Inventories the current committed evidence (Core-side `J4` connector capture in `docs/hardware/s360-100-r4-core.md` §J4 — 3-pin `+5V` / `Relay` / `GND`, drive `Relay` from ESP32 `IO3`; firmware package `packages/expansions/fan_relay.yaml` with default `fan_relay_pin: ${relay_pin}`; `FanRelay` token reservation in `config/webflash-compatibility.json` `canonical_modules` subject to the fan-driver `max-one-of` rule; existing classifications in `docs/hardware/board-readiness-matrix.md`, `docs/hardware/remaining-board-documentation-audit.md`, `docs/hardware/firmware-package-mapping-audit.md`, `docs/product-availability-taxonomy.md`, `docs/hardware/hardware-artifact-policy.md`). Records the `relay_pin` disagreement as **unresolved by this PR**: the Core schematic places the `Relay` net on ESP32 `IO3` at `J4` pin 2; `packages/hardware/sense360_core_ceiling.yaml` binds `relay_pin: GPIO4` (HW-009 flags `IO4 = SEN0609_RX`); `packages/hardware/sense360_core.yaml` binds `relay_pin: GPIO10`; `packages/expansions/fan_relay.yaml` inherits whichever value the parent Core package binds via `${relay_pin}`. Resolution belongs to the systemic Core abstract-bus rebind owned by `docs/release-one-hardware-audit.md` Required follow-ups #2 / #3 plus a future evidence-bearing HW-PINMAP-310 follow-up, not to this PR. Lists missing evidence in full: module-side schematic PDF, connector pinout against silkscreen, power rail requirements, relay output topology (mechanical vs SSR, contact rating, configuration), coil / driver circuit details, on-board indicator circuit, Core-to-module harness identity, definitive GPIO mapping reconciled against the Core schematic + abstract packages + module-side schematic + bench observation, package YAML reconciliation decision (out of scope for HW-PINMAP-310; belongs to PACKAGE-GAP-001 FanRelay slice), silkscreen / bench verification if needed. Defines the follow-up PR sequence (HW-ASSETS-310 curated artifact index once schematic evidence is supplied; HW-PINMAP-310-FOLLOWUP standalone schematic-backed reference doc + pin-map reconciliation; separate JSON PR for `S360-310` `schematic_status` promotion; PACKAGE-GAP-001 FanRelay slice for package YAML reconciliation; PRODUCT-GAP-001 FanRelay slice for product YAML if/when decided; WEBFLASH-GAP-001 / RELEASE-GAP-001 / WF-IMPORT-GAP-001 FanRelay slice for wrapper + build + release + import; stable promotion goes through the 17-row `docs/preview-to-stable-promotion-gates.md` gate). Documentation only and explicitly **does not**: edit `config/hardware-catalog.json`, `config/product-catalog.json`, `config/webflash-builds.json`, or `config/webflash-compatibility.json`; add a committed schematic PDF under `docs/hardware/schematics/`; add a curated artifact index under `docs/hardware/artifacts/`; add or change `schematic_file` for `S360-310`; flip `S360-310` `schematic_status` from `cataloged_unverified`; mark `S360-310` `verified`; mark the pin map confirmed; mark `packages/expansions/fan_relay.yaml` `confirmed-ok`; edit any package YAML (`packages/expansions/fan_relay.yaml`, `packages/hardware/sense360_core_ceiling.yaml`, `packages/hardware/sense360_core.yaml` all stay unchanged); resolve the `IO3` vs `GPIO4` vs `GPIO10` `relay_pin` disagreement; add a product YAML; add a WebFlash wrapper; add a build-matrix entry; generate firmware; create a GitHub Release or tag; perform a WebFlash import; promote `S360-310` to `preview` / `stable` / `production`; add a `FanRelay` token to any Release-One or preview config string; change Release-One (`Ceiling-POE-VentIQ-RoomIQ`, `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag `v1.0.0`); change the LED preview path (`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`, `channel: preview`); unblock FanTRIAC (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`); change the mains-voltage compliance status for `S360-320` or `S360-400` (owned by COMPLIANCE-001); resolve the Core J10 vs RoomIQ J6 pin-order open question; resolve the systemic Core abstract-bus mismatch (`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3). Adds no edits to `config/*`, `products/*`, `products/webflash/*`, `packages/*`, `scripts/*`, `tests/*`, `components/*`, `include/*`, or `.github/workflows/*`. Cross-linked from `docs/hardware/board-readiness-matrix.md` (`S360-310` board-by-board notes, follow-up-PR-sequence item #1, See-also per-board reference docs list), `docs/hardware/remaining-board-documentation-audit.md` (Sense360 Relay (`S360-310`) audit-doc bullet), `docs/hardware/firmware-package-mapping-audit.md` (Release-One package stack `relay_pin: GPIO4` reconciliation note), and `docs/product-availability-taxonomy.md` (`S360-310 Sense360 Relay` snapshot row). | Keep. |
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
(HW-PINMAP-400, `pending`),
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
(HW-PINMAP-400, `pending`),
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

# Compile-only Firmware Validation Lane (FW-COMPILE-MATRIX-001)

## Purpose and scope

This document explains the **compile-only firmware validation lane**
at [`config/compile-only-targets.json`](../config/compile-only-targets.json),
the validator script at [`scripts/validate_compile_targets.py`](../scripts/validate_compile_targets.py),
and the tests at [`tests/test_compile_targets.py`](../tests/test_compile_targets.py).

The lane lets CI assert that a curated list of product YAMLs **builds
under the current ESPHome version** — that the YAML composes, the
substitutions resolve, the `!include`s resolve, the package config
matches the component config, and the codegen pass produces source —
before any hardware has been bench-validated for the configuration.
Compile success is necessary but **not** sufficient for preview or
stable readiness.

This document and the artefacts it describes do **not**:

- expose new WebFlash builds,
- create release artifacts,
- import firmware to WebFlash,
- promote any product,
- add product YAMLs under `products/**`,
- add WebFlash wrappers under `products/webflash/**`,
- add `webflash_build_matrix: true` to any product,
- add `artifact_name` to any product,
- promote LED to stable,
- promote any blocked fan module,
- promote `PWR` / `S360-400`,
- promote `POE` / `S360-410`,
- claim hardware proof exists,
- claim `RELEASE-007` is unblocked,
- claim WebFlash import is ready,
- change [`config/webflash-builds.json`](../config/webflash-builds.json),
  [`config/product-catalog.json`](../config/product-catalog.json),
  [`config/hardware-catalog.json`](../config/hardware-catalog.json),
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
  [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json),
  or [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json),
- change `products/**`, `products/webflash/**`, `packages/**`,
  `firmware/**`, `manifest.json`, `firmware/sources.json`,
  release artifacts, checksums, or build-info manifests,
- change `REQUIRED_CONFIGS`.

## What "compile-only" means

A target listed in [`config/compile-only-targets.json`](../config/compile-only-targets.json)
is a YAML that CI is allowed to feed to `esphome compile` so that
YAML / package / config / codegen errors surface as early as possible.

Concretely, a passing compile-only run tells us:

- the YAML parses and the substitutions resolve;
- the `packages:` composition resolves and every `!include` resolves;
- ESPHome's component / config schema validates;
- the codegen pass produces compilable source.

It does **not** tell us:

- that the resulting firmware will boot on real hardware;
- that the hardware bench-tests pass (bench / harness / silkscreen /
  schematic / pinmap evidence is owned by the `S360-*-BENCH-*`,
  `HW-*`, and `HW-ASSETS-*` slices);
- that compliance gates close
  (`COMPLIANCE-001` / `WF-HW-TEST-*`);
- that the build is shippable, releasable, or WebFlash-installable.

Stable / preview readiness still requires the full 17-row gauntlet in
[`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md).
The compile-only lane is **pre-hardware confidence**, not release
proof.

## Per-target schema

Each row in the `targets` array carries the following fields:

| Field                                | Meaning                                                                                                          |
|--------------------------------------|------------------------------------------------------------------------------------------------------------------|
| `id`                                 | Stable identifier for the target. Unique. Example: `ceiling-poe-ventiq-roomiq-webflash`.                          |
| `product_yaml`                       | Repo-relative path to the product YAML to compile. Must exist on disk.                                            |
| `config_string`                      | WebFlash config string this YAML maps to, when applicable. Must appear in `config/firmware-combination-matrix.json`. |
| `expected_channel`                   | Channel the corresponding `config/webflash-builds.json` entry sits on (`stable`, `preview`, etc.), when applicable. |
| `reason`                             | Free-text explanation of why this YAML is in the compile-only lane.                                              |
| `shipment_status`                    | One of `webflash-current`, `preview-current`, `compile-only`.                                                    |
| `hardware_required_for_validation`   | `true` if real hardware is required before compile success can be turned into a shipment claim.                  |
| `webflash_exposure_allowed_now`      | `true` only if the corresponding `config_string` is currently committed to `config/webflash-builds.json`.        |
| `blocked`                            | Optional. `true` if the target carries a blocked module (`FanTRIAC`, `PWR`) and is in the lane only as reference. |
| `notes`                              | Free-text narrative. Used to record why the row exists and what it does not imply.                                |

### Allowed `shipment_status` values

| Value               | Meaning                                                                                                          |
|---------------------|------------------------------------------------------------------------------------------------------------------|
| `webflash-current`  | The YAML maps to a `config_string` currently committed to `config/webflash-builds.json` on the `stable` channel. |
| `preview-current`   | The YAML maps to a `config_string` currently committed to `config/webflash-builds.json` on a non-`stable` channel (preview / beta / dev / rescue). |
| `compile-only`      | The YAML is in the compile-only lane for build-confidence reasons only. It is **not** in `config/webflash-builds.json`. |

A `compile-only` target must not claim `webflash_exposure_allowed_now: true`.

## Rules

The compile-only lane enforces the following rules:

- **Compile is not WebFlash exposure.** A row in this file does not
  add a build to [`config/webflash-builds.json`](../config/webflash-builds.json)
  and does not flip `webflash_build_matrix: true` on any product. The
  validator rejects any target that declares `webflash_build_matrix`
  itself.
- **Compile is not a release artifact.** A row in this file does not
  create firmware binaries, checksums, build-info manifests, or
  GitHub Releases. The validator rejects any target that declares
  `artifact_name`.
- **Compile is not stable promotion.** A `preview-current` target
  does not become `stable` because its compile pass succeeded.
- **Compile is not hardware proof.** Compile success says nothing
  about bench / harness / silkscreen / schematic / pinmap evidence.
  `hardware_required_for_validation: false` only means
  "compile-only validation does not require hardware"; it does **not**
  mean the product is safe to ship without hardware.
- **No blocked FanTRIAC / PWR target without an explicit marker.**
  Any target whose `config_string` contains a `FanTRIAC` token or a
  `PWR` token must declare `blocked: true`,
  `webflash_exposure_allowed_now: false`, and must not carry the
  `webflash-current` or `preview-current` shipment status. The
  current row set carries no such reference target; this rule is a
  guardrail for the future.
- **Compile success is necessary, not sufficient.** Promotion to
  preview / stable still requires the per-row evidence gates
  documented in
  [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md).

## Current compile-only targets

The current row set is intentionally conservative — only the two
product YAMLs that already build and that are already committed to
[`config/webflash-builds.json`](../config/webflash-builds.json):

### `ceiling-poe-ventiq-roomiq-webflash`

- **`product_yaml`.** `products/webflash/ceiling-poe-ventiq-roomiq.yaml`
- **`config_string`.** `Ceiling-POE-VentIQ-RoomIQ`
- **`expected_channel`.** `stable`
- **`shipment_status`.** `webflash-current`
- **`hardware_required_for_validation`.** `false`
- **`webflash_exposure_allowed_now`.** `true`

Release-One stable WebFlash build. Compile-only validation pins that
the canonical Release-One YAML still composes / substitutes /
includes / generates code cleanly under the current ESPHome version.

### `ceiling-poe-ventiq-roomiq-led-webflash`

- **`product_yaml`.** `products/webflash/ceiling-poe-ventiq-roomiq-led.yaml`
- **`config_string`.** `Ceiling-POE-VentIQ-RoomIQ-LED`
- **`expected_channel`.** `preview`
- **`shipment_status`.** `preview-current`
- **`hardware_required_for_validation`.** `false`
- **`webflash_exposure_allowed_now`.** `true`

LED-bearing preview WebFlash build. Compile-only validation pins that
the LED-bearing canonical YAML still composes / substitutes /
includes / generates code cleanly under the current ESPHome version.
Compile success is **not** LED-stable proof; the LED stable gauntlet
(`S360-300-BENCH-001`, `WF-HW-TEST-001`, `WF-HW-TEST-003`,
`RELEASE-007`) remains open.

## Running the validator

The validator at [`scripts/validate_compile_targets.py`](../scripts/validate_compile_targets.py)
has two modes:

```sh
# metadata-only (default; safe without ESPHome installed)
python3 scripts/validate_compile_targets.py
python3 scripts/validate_compile_targets.py --metadata-only

# full compile pass (requires the `esphome` CLI on PATH)
python3 scripts/validate_compile_targets.py --compile
```

Metadata-only mode asserts:

- every target's `product_yaml` exists on disk;
- every target with a `config_string` appears in
  [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json);
- every `webflash-current` or `preview-current` target's
  `config_string` is committed in
  [`config/webflash-builds.json`](../config/webflash-builds.json) and
  carries `webflash_exposure_allowed_now: true`;
- a target's `expected_channel`, when set, matches the channel in
  [`config/webflash-builds.json`](../config/webflash-builds.json);
- no compile-only target declares `webflash_build_matrix` or
  `artifact_name`;
- no blocked `FanTRIAC` or `PWR` target sneaks in without the explicit
  `blocked: true` + `webflash_exposure_allowed_now: false` marker.

`--compile` mode requires the `esphome` CLI to be available. If it is
not, the script exits non-zero with an explicit error — it **does
not** fake a compile pass.

### Test secrets must sit next to the target YAML

ESPHome resolves `!secret` lookups relative to the top-level YAML being
compiled, so the directory each `product_yaml` lives in must contain a
`secrets.yaml` at compile time. Current targets live under
`products/webflash/` (FW-COMPILE-MATRIX-001) and
`products/compile-only/` (FW-COMPILE-POE-NONFAN-001), so the workflow
at
[`.github/workflows/compile-only.yml`](../.github/workflows/compile-only.yml)
provisions a test `secrets.yaml` at the repo root, under `products/`,
under `products/webflash/`, and under `products/compile-only/`. Any
future compile-only target placed in a new directory needs the same
provisioning extended to that directory. The `secrets.yaml` written
by the workflow is a CI-only stub; it contains no real credentials
and is gitignored.

## CI integration

The metadata-only validator is safe to run on any CI lane that already
has Python available; it has no ESPHome dependency.

A full compile pass requires the `esphome` Python package on the
runner. The repository already exercises full ESPHome compile sweeps
manually via
[`.github/workflows/ci-validate-configs.yml`](../.github/workflows/ci-validate-configs.yml),
which is `workflow_dispatch`-only. The compile-only lane is a
**different** mechanism with a different scope: it is a curated, stable
set of YAMLs that are committed to
[`config/compile-only-targets.json`](../config/compile-only-targets.json)
specifically so that adding / removing a target is a code change
reviewed in PR, not a runtime workflow input.

If a dedicated compile-only workflow is added in the future, it must:

- be named clearly (for example `compile-only.yml`);
- not produce release artifacts (no `firmware-*.bin` upload, no
  GitHub Release tag);
- not write to [`config/webflash-builds.json`](../config/webflash-builds.json),
  [`config/product-catalog.json`](../config/product-catalog.json), or
  any other shipment manifest;
- treat ESPHome compile output as ephemeral CI artefact only.

## Adding or removing a target

Any change to the compile-only target set is a reviewed code change:

1. Edit [`config/compile-only-targets.json`](../config/compile-only-targets.json).
2. Run the metadata validator (`--metadata-only` is default-safe):

   ```sh
   python3 scripts/validate_compile_targets.py --metadata-only
   ```

3. Run the test suite:

   ```sh
   python3 tests/test_compile_targets.py
   ```

4. If ESPHome is available locally, also run the full compile pass:

   ```sh
   python3 scripts/validate_compile_targets.py --compile
   ```

A target should be added **only** if:

- the `product_yaml` already exists and already compiles cleanly;
- the YAML does not require secrets, hardware-only local files, or
  manual user input to compile;
- adding the row does not imply WebFlash exposure (the validator
  enforces this);
- adding the row does not imply stable promotion (the validator
  enforces this).

A target should be removed if:

- the underlying YAML has been deleted;
- the YAML now requires secrets / hardware-only files at compile time;
- the YAML now needs evidence the compile-only lane cannot pretend to
  carry (in which case the row belongs in a hardware / bench /
  compliance slice, not the compile-only lane).

## Audit log

### 2026-05-21 — FW-COMPILE-RESULT-001 successful full compile run

The `Compile-only Firmware Validation` workflow was manually run via
`workflow_dispatch` with `compile_mode=full` and **passed**. This is
the first recorded successful full compile pass for the compile-only
validation lane against the two committed WebFlash product YAMLs.

- **Workflow.** `Compile-only Firmware Validation`
  ([`.github/workflows/compile-only.yml`](../.github/workflows/compile-only.yml))
- **Run number.** `#9`
- **Run URL.** <https://github.com/sense360store/esphome-public/actions/runs/26228528326>
- **Job URL.** <https://github.com/sense360store/esphome-public/actions/runs/26228528326/job/77182121905>
- **Job name.** `Compile-only Targets — Full ESPHome Compile`
- **Result.** `succeeded`
- **Duration.** `7m 33s`
- **ESPHome version.** `2026.4.5`
- **Python.** `3.11.15`
- **Command.** `python3 scripts/validate_compile_targets.py --compile`

Observed output:

- Metadata validation passed.
- `ceiling-poe-ventiq-roomiq-webflash`: `rc=0`
- `ceiling-poe-ventiq-roomiq-led-webflash`: `rc=0`
- All 2 compile target(s) passed.

Targets exercised by this run:

1. `ceiling-poe-ventiq-roomiq-webflash`
   - `product_yaml`: `products/webflash/ceiling-poe-ventiq-roomiq.yaml`
   - `config_string`: `Ceiling-POE-VentIQ-RoomIQ`
   - `expected_channel`: `stable`
2. `ceiling-poe-ventiq-roomiq-led-webflash`
   - `product_yaml`: `products/webflash/ceiling-poe-ventiq-roomiq-led.yaml`
   - `config_string`: `Ceiling-POE-VentIQ-RoomIQ-LED`
   - `expected_channel`: `preview`

#### What this successful run proves

This `workflow_dispatch` full compile pass proves
**YAML / package / ESPHome compile confidence** for the two current
WebFlash product YAMLs under ESPHome `2026.4.5`. Concretely, for each
of the two `product_yaml` files above:

- the YAML parses and the substitutions resolve;
- the `packages:` composition resolves and every `!include` resolves;
- ESPHome's component / config schema validates;
- the codegen pass produces compilable source;
- the validator script's metadata gates pass alongside the compile
  pass (`rc=0` from `python3 scripts/validate_compile_targets.py --compile`).

#### What this successful run does **not** prove

Compile success is necessary but **not sufficient** for any
shipment-readiness claim. In particular, this run does **not** prove
any of the following, and nothing in this audit-log entry should be
read as a claim that any of them are now closed:

- **Hardware behavior.** No bench, harness, silkscreen, schematic,
  pinmap, thermal, or EMI evidence is generated by a compile pass.
- **Web Serial flashing.** A compile pass does not exercise the Web
  Serial / WebFlash flashing path.
- **Boot on real hardware.** A compile pass does not boot the
  resulting firmware on a device.
- **Sensors or LED behavior.** A compile pass does not exercise any
  sensor, peripheral, or LED behavior at runtime.
- **Improv or Home Assistant handoff.** A compile pass does not
  exercise the Improv provisioning flow or the Home Assistant
  hand-off / API path.
- **Release readiness.** A compile pass does not produce a firmware
  binary, checksum, build-info manifest, or GitHub Release tag.
- **LED stable readiness.** The LED-bearing target remains `preview`;
  the LED stable gauntlet (`S360-300-BENCH-001`, `WF-HW-TEST-001`,
  `WF-HW-TEST-003`, `RELEASE-007`) is unchanged.
- **WebFlash import readiness.** A compile pass does not import,
  publish, or otherwise expose any build to the WebFlash UI.
- **Compliance.** A compile pass produces no compliance evidence;
  `COMPLIANCE-001` and the `WF-HW-TEST-*` slices remain governed by
  their own evidence gates.

The full 17-row stable-promotion gauntlet documented in
[`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
remains the source of truth for preview / stable readiness; this
audit-log entry does not close any row in that gauntlet.

### 2026-05-21 — FW-COMPILE-POE-NONFAN-001 POE non-fan compile-only expansion

This entry records the addition of five compile-only product YAML
skeletons for POE non-fan candidates to the
[`config/compile-only-targets.json`](../config/compile-only-targets.json)
lane. The candidates are config-string-valid per
[`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json)
and reuse package-composition patterns already proven to compile by
the Release-One WebFlash build
(`Ceiling-POE-VentIQ-RoomIQ`) and the LED preview build
(`Ceiling-POE-VentIQ-RoomIQ-LED`).

#### Target list

The five new compile-only targets, all with
`shipment_status: compile-only`,
`webflash_exposure_allowed_now: false`, and
`hardware_required_for_validation: true`:

| `id`                                       | `product_yaml`                                          | `config_string`             |
|--------------------------------------------|---------------------------------------------------------|-----------------------------|
| `ceiling-poe-compile-only`                 | `products/compile-only/ceiling-poe.yaml`                | `Ceiling-POE`               |
| `ceiling-poe-roomiq-compile-only`          | `products/compile-only/ceiling-poe-roomiq.yaml`         | `Ceiling-POE-RoomIQ`        |
| `ceiling-poe-ventiq-compile-only`          | `products/compile-only/ceiling-poe-ventiq.yaml`         | `Ceiling-POE-VentIQ`        |
| `ceiling-poe-airiq-compile-only`           | `products/compile-only/ceiling-poe-airiq.yaml`          | `Ceiling-POE-AirIQ`         |
| `ceiling-poe-airiq-roomiq-compile-only`    | `products/compile-only/ceiling-poe-airiq-roomiq.yaml`   | `Ceiling-POE-AirIQ-RoomIQ`  |

Each YAML composes only from existing packages — `sense360_core_ceiling.yaml`,
`power_poe.yaml`, base packages, `device_health.yaml`, and (where the
config string carries the token) `airiq_ceiling.yaml` /
`airiq_basic_profile.yaml`, `airiq_bathroom_base.yaml` /
`bathroom_profile.yaml`, `comfort_ceiling.yaml` /
`comfort_basic_profile.yaml`, `presence_ceiling.yaml` /
`presence_basic_profile.yaml`. No new package is added by this
expansion.

#### Why these are lower-risk than fan / PWR targets

- **No FanTRIAC** (blocked under `HW-005`,
  `HW-PINMAP-320-FOLLOWUP`, `PACKAGE-TRIAC-001`, and `COMPLIANCE-001`).
  These five candidates carry no `FanTRIAC` token.
- **No FanRelay / FanPWM / FanDAC**. The relay package
  `packages/expansions/fan_relay.yaml` remains blocked behind
  `CORE-ABSTRACT-BUS-001A` / `S360-310` silkscreen / `GPIO3`
  strap-pin bench evidence; PWM and FanDAC packages remain blocked
  behind `CORE-ABSTRACT-BUS-001B` and their own evidence gates.
  These five candidates carry no fan token at all.
- **No PWR / S360-400**. Mains-voltage compliance
  (`COMPLIANCE-001` UK / EU assessment) and the
  `PACKAGE-POWER-400-001` / `PRODUCT-POWER-400-001` /
  `WEBFLASH-POWER-400-001` / `RELEASE-POWER-400-001` chain are open;
  these five candidates carry only `POE` in the `power` slot.
- **No LED**. The LED stable gauntlet (`S360-300-BENCH-001`,
  `WF-HW-TEST-001`, `WF-HW-TEST-003`, `RELEASE-007`) is unchanged;
  these five candidates carry no `LED` token.
- **No new packages**. Every `!include` resolves to a package already
  consumed by either the Release-One YAML
  (`products/webflash/ceiling-poe-ventiq-roomiq.yaml`) or the
  enumerated `products/sense360-core-ceiling.yaml` reference YAML.

The package compositions are therefore subsets / sibling variants of
compositions already exercised by the WebFlash-shipping Release-One
build, so the compile-confidence risk is proportionally lower than
fan / PWR / new-package targets.

#### What compile-only proves for these five candidates

Once
[`scripts/validate_compile_targets.py --compile`](../scripts/validate_compile_targets.py)
is run against the expanded lane, a passing run proves the following
for each of the five new YAMLs (and only for them, only under the
ESPHome version recorded in the workflow):

- the YAML parses and the substitutions resolve;
- the `packages:` composition resolves and every `!include` resolves;
- ESPHome's component / config schema validates;
- the codegen pass produces compilable source;
- the validator script's metadata gates pass alongside the compile
  pass.

#### What compile-only does **not** prove for these five candidates

These five candidates are **pre-hardware confidence** only. A
passing compile run does **not** prove any of the following, and
nothing in this audit-log entry should be read as a claim that any
of them are now closed:

- **Hardware behavior.** No bench, harness, silkscreen, schematic,
  pinmap, thermal, or EMI evidence is generated. The PoE PSU
  (`S360-410`) `schematic_status: cataloged_unverified` and the
  Release-One PoE "schematic verification pending" caveat remain
  open. The VentIQ (`S360-211`) "schematic verification pending"
  caveat remains open.
- **AirIQ hardware proof.** The AirIQ stack (`SPS30` / `SGP41` /
  `SCD41` / `BMP390`) has no committed bench or schematic evidence
  in this repo; compile success does not imply AirIQ stable /
  preview readiness.
- **Web Serial flashing.** None of the five candidates are imported
  into WebFlash. No `.bin`, no `manifest.json`, no
  `firmware/sources.json` entry, no GitHub Release tag, and no
  proof row in `docs/webflash-release-proof.md` is created.
- **WebFlash exposure.** None of the five candidates are added to
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  none flip `webflash_build_matrix: true` on any product, and none
  have a `webflash_wrapper` under
  [`products/webflash/`](../products/webflash/).
- **Product-catalog promotion.** None of the five candidates are
  added to
  [`config/product-catalog.json`](../config/product-catalog.json).
  The YAMLs live under `products/compile-only/`, which is excluded
  from `tests/test_product_catalog.py::_top_level_product_yamls`
  enumeration scanning.
- **Stable or preview promotion.** Release-One stays
  `Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`; the LED preview
  stays `Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`. FanTRIAC stays
  `blocked` / `HW-005`.
- **Release artifacts.** No checksum, build-info manifest, or
  release tag is created.
- **Hardware-required gates.** Every candidate sets
  `hardware_required_for_validation: true` precisely because
  shipment-readiness for any of these five config strings still
  needs the full 17-row gauntlet in
  [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md).

Compile success for the five new candidates is therefore a
**necessary-but-insufficient** input to the broader
preview-to-stable promotion process; it does not unblock any
hardware / compliance / release gate on its own.

### 2026-05-21 — POE non-fan 7-target full compile result

After FW-COMPILE-POE-NONFAN-001 / PR #548 expanded the compile-only
lane from 2 to 7 targets, the `Compile-only Firmware Validation`
workflow was manually re-run via `workflow_dispatch` with
`compile_mode=full` against the expanded lane and **passed**. This is
the first recorded successful full compile pass across all seven
compile-only targets — the two committed WebFlash product YAMLs from
FW-COMPILE-MATRIX-001 plus the five POE non-fan compile-only skeletons
from FW-COMPILE-POE-NONFAN-001.

- **Workflow.** `Compile-only Firmware Validation`
  ([`.github/workflows/compile-only.yml`](../.github/workflows/compile-only.yml))
- **Run URL.** <https://github.com/sense360store/esphome-public/actions/runs/26236882386>
- **Full compile job ID.** `77212453770`
- **Job name.** `Compile-only Targets — Full ESPHome Compile`
- **Result.** `success`
- **Commit tested.** `1b587cd25cdf5d7bd400cf9b783dccbbb8de3442`
- **Start / end.** `2026-05-21T15:48:46Z` → `2026-05-21T16:10:03Z`
- **ESPHome version.** `2026.4.5`
- **Python.** `3.11.15`
- **Command.** `python3 scripts/validate_compile_targets.py --compile`

Observed output:

- Read 7 compile-only target(s) from `config/compile-only-targets.json`.
- Metadata validation passed.
- `ceiling-poe-ventiq-roomiq-webflash`: `rc=0`
- `ceiling-poe-ventiq-roomiq-led-webflash`: `rc=0`
- `ceiling-poe-compile-only`: `rc=0`
- `ceiling-poe-roomiq-compile-only`: `rc=0`
- `ceiling-poe-ventiq-compile-only`: `rc=0`
- `ceiling-poe-airiq-compile-only`: `rc=0`
- `ceiling-poe-airiq-roomiq-compile-only`: `rc=0`
- All 7 compile target(s) passed.

Targets exercised by this run:

1. `ceiling-poe-ventiq-roomiq-webflash`
   - `product_yaml`: `products/webflash/ceiling-poe-ventiq-roomiq.yaml`
   - `config_string`: `Ceiling-POE-VentIQ-RoomIQ`
   - `shipment_status`: `webflash-current`
2. `ceiling-poe-ventiq-roomiq-led-webflash`
   - `product_yaml`: `products/webflash/ceiling-poe-ventiq-roomiq-led.yaml`
   - `config_string`: `Ceiling-POE-VentIQ-RoomIQ-LED`
   - `shipment_status`: `preview-current`
3. `ceiling-poe-compile-only`
   - `product_yaml`: `products/compile-only/ceiling-poe.yaml`
   - `config_string`: `Ceiling-POE`
   - `shipment_status`: `compile-only`
4. `ceiling-poe-roomiq-compile-only`
   - `product_yaml`: `products/compile-only/ceiling-poe-roomiq.yaml`
   - `config_string`: `Ceiling-POE-RoomIQ`
   - `shipment_status`: `compile-only`
5. `ceiling-poe-ventiq-compile-only`
   - `product_yaml`: `products/compile-only/ceiling-poe-ventiq.yaml`
   - `config_string`: `Ceiling-POE-VentIQ`
   - `shipment_status`: `compile-only`
6. `ceiling-poe-airiq-compile-only`
   - `product_yaml`: `products/compile-only/ceiling-poe-airiq.yaml`
   - `config_string`: `Ceiling-POE-AirIQ`
   - `shipment_status`: `compile-only`
7. `ceiling-poe-airiq-roomiq-compile-only`
   - `product_yaml`: `products/compile-only/ceiling-poe-airiq-roomiq.yaml`
   - `config_string`: `Ceiling-POE-AirIQ-RoomIQ`
   - `shipment_status`: `compile-only`

#### What this successful run proves

This `workflow_dispatch` full compile pass proves
**YAML / package / ESPHome compile confidence** for all seven
compile-only targets under ESPHome `2026.4.5`. Concretely:

- the two current WebFlash product YAMLs
  (`products/webflash/ceiling-poe-ventiq-roomiq.yaml` and
  `products/webflash/ceiling-poe-ventiq-roomiq-led.yaml`) still
  compose / substitute / `!include`-resolve / codegen cleanly under
  the current ESPHome version, so no regression has been introduced
  to the Release-One stable build or the LED preview build;
- the five POE non-fan compile-only skeletons under
  `products/compile-only/` compose / substitute / `!include`-resolve /
  codegen cleanly under the current ESPHome version, against the
  package set already proven by the Release-One YAML and
  `products/sense360-core-ceiling.yaml`;
- for every target, the YAML parses and the substitutions resolve,
  the `packages:` composition resolves and every `!include` resolves,
  ESPHome's component / config schema validates, and the codegen pass
  produces compilable source;
- the validator script's metadata gates pass alongside the compile
  pass (`rc=0` from `python3 scripts/validate_compile_targets.py --compile`);
- CI will now catch future package drift across the 7-target compile
  lane on subsequent `workflow_dispatch` `compile_mode=full` runs.

#### What this successful run does **not** prove

Compile success is necessary but **not sufficient** for any
shipment-readiness claim. In particular, this run does **not** prove
any of the following, and nothing in this audit-log entry should be
read as a claim that any of them are now closed:

- **Hardware behavior.** No bench, harness, silkscreen, schematic,
  pinmap, thermal, or EMI evidence is generated by a compile pass.
- **Web Serial flashing.** A compile pass does not exercise the Web
  Serial / WebFlash flashing path for any target.
- **Boot on real hardware.** A compile pass does not boot the
  resulting firmware on a device.
- **Sensor behavior.** A compile pass does not exercise any sensor
  or peripheral at runtime (AirIQ `SPS30` / `SGP41` / `SCD41` /
  `BMP390`, VentIQ, RoomIQ, presence, comfort, or PoE-PSU
  diagnostics).
- **LED behavior.** A compile pass does not exercise any LED
  runtime behavior on the LED-bearing preview target.
- **Improv or Home Assistant handoff.** A compile pass does not
  exercise the Improv provisioning flow or the Home Assistant
  hand-off / API path.
- **Release artifacts.** A compile pass does not produce a firmware
  binary, checksum, build-info manifest, or GitHub Release tag for
  any target. The compile-only workflow treats ESPHome compile
  output as ephemeral CI artefact only.
- **WebFlash import readiness.** A compile pass does not import,
  publish, or otherwise expose any build to the WebFlash UI. The
  five compile-only skeletons are not imported to WebFlash.
- **WebFlash exposure.** None of the five compile-only skeletons
  are added to [`config/webflash-builds.json`](../config/webflash-builds.json),
  none flip `webflash_build_matrix: true` on any product, and none
  have a `webflash_wrapper` under
  [`products/webflash/`](../products/webflash/).
- **`REQUIRED_CONFIGS` eligibility.** A compile pass does not add
  any of the five compile-only config strings to
  `release_one_required_configs` / `REQUIRED_CONFIGS`. Release-One
  stays `Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`.
- **Stable promotion.** A compile pass does not promote any
  compile-only target to `stable` (or to `preview` /
  `webflash-current`). The LED-bearing target remains `preview`;
  the five compile-only skeletons remain `compile-only`.
- **LED stable promotion.** The LED stable gauntlet
  (`S360-300-BENCH-001`, `WF-HW-TEST-001`, `WF-HW-TEST-003`,
  `RELEASE-007`) is unchanged. LED preview stays
  `Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`.
- **`RELEASE-007` unblock.** A compile pass does not close or
  unblock `RELEASE-007`.
- **Compliance.** A compile pass produces no compliance evidence;
  `COMPLIANCE-001` and the `WF-HW-TEST-*` slices remain governed by
  their own evidence gates.

The full 17-row stable-promotion gauntlet documented in
[`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
remains the source of truth for preview / stable readiness; this
audit-log entry does not close any row in that gauntlet.

### 2026-05-22 — FW-COMPILE-RELAY-001 FanRelay compile-only validation

This entry records the addition of a single FanRelay compile-only
target to the
[`config/compile-only-targets.json`](../config/compile-only-targets.json)
lane after `PRODUCT-RELAY-001` / PR #564 landed the canonical FanRelay
product YAML at
[`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml)
and `WEBFLASH-RELAY-001-READINESS-REFRESH` / PR #565 confirmed that
WebFlash Relay exposure remains blocked behind seven separate gates.
The target reuses the canonical FanRelay product YAML (it does **not**
introduce a new YAML under `products/compile-only/` or
`products/webflash/`); the catalog row landed by PR #564 (status
`hardware-pending`, `webflash_build_matrix: false`, no
`artifact_name`, no `webflash_wrapper`) is consumed unchanged.

#### Target

The single new compile-only target:

| `id`                                                | `product_yaml`                                                       | `config_string`                       |
|-----------------------------------------------------|----------------------------------------------------------------------|---------------------------------------|
| `ceiling-poe-ventiq-fanrelay-roomiq-compile-only`   | `products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`          | `Ceiling-POE-VentIQ-FanRelay-RoomIQ`  |

Settings on the row:

- `shipment_status: compile-only`
- `webflash_exposure_allowed_now: false`
- `hardware_required_for_validation: true`
- `blocked: false`
- `advanced_manual_warning_only: true`
- `hardware_pending: true`

The two flags `advanced_manual_warning_only` and `hardware_pending`
are FanRelay-specific markers that record the product-layer
disposition defined by `PRODUCT-RELAY-001-READINESS-REFRESH` / PR
#563 and confirmed by `PRODUCT-RELAY-001` / PR #564. They do **not**
gate the compile-only validator itself; they record posture so a
later reader of the compile-only target row can see at a glance that
the row corresponds to an `advanced/manual-warning-only` +
hardware-pending product and does **not** silently re-promote the
FanRelay product to a less-restricted exposure class.

#### Why FanRelay is now safely compile-only

The compile-only target became safe to add only because the
upstream evidence layer closed:

- **`CORE-ABSTRACT-BUS-001C`** / PR #557 freed `GPIO3` (the
  schematic-correct Relay net per `S360-100-R4` `IO3`).
- **`CORE-ABSTRACT-BUS-001A`** / PR #558 rebound `relay_pin` to
  `GPIO3` across the five non-voice Core abstract packages.
- **`PACKAGE-RELAY-001-READINESS-REFRESH`** / PR #559 separated the
  substitution-layer blockers (resolved) from the hardware-evidence
  blockers (open at that point).
- **`S360-310-BENCH-001`** / PR #560 added the ten-row bench
  evidence checklist.
- **`S360-310-BENCH-EVIDENCE-001`** / PR #561 populated the
  operator / BOM / public-reference rows.
- **`PACKAGE-RELAY-001`** / PR #562 added
  [`tests/test_fan_relay_package.py`](../tests/test_fan_relay_package.py)
  pinning the FanRelay package abstraction.
- **`PRODUCT-RELAY-001-READINESS-REFRESH`** / PR #563 defined the
  product-layer posture as
  `advanced/manual-warning-only + product-YAML-allowed + compile-only-allowed + WebFlash-blocked`.
- **`PRODUCT-RELAY-001`** / PR #564 landed the canonical product
  YAML.
- **`WEBFLASH-RELAY-001-READINESS-REFRESH`** / PR #565 confirmed
  WebFlash Relay exposure remains blocked behind the seven WebFlash
  gates.

Compile-only validation is the next safe step in the chain because
the product YAML is structurally landed and consumes only packages
that already compose / substitute / `!include`-resolve under the
current ESPHome version. The compile-only lane has historically
required the underlying YAML to already exist; the FanRelay YAML
landed at PR #564, so the YAML / package / ESPHome compile drift
risk can now be guarded by CI.

#### What compile-only proves for the FanRelay target

Once
[`scripts/validate_compile_targets.py --compile`](../scripts/validate_compile_targets.py)
is run against the expanded lane, a passing run proves the following
for the FanRelay product YAML (and only for it, only under the
ESPHome version recorded in the workflow):

- the YAML parses and the substitutions resolve (including the
  `${relay_pin}` → `GPIO3` inheritance chain from the parent Core
  abstract package);
- the `packages:` composition resolves and every `!include` resolves
  (Core ceiling, PoE PSU, VentIQ, RoomIQ, FanRelay, base, health);
- ESPHome's component / config schema validates;
- the codegen pass produces compilable source;
- the validator script's metadata gates pass alongside the compile
  pass.

#### What compile-only does **not** prove for the FanRelay target

Compile success is necessary but **not sufficient** for any
shipment-readiness claim. In particular, this target does **not**
prove any of the following, and nothing in this audit-log entry
should be read as a claim that any of them are now closed:

- **WebFlash exposure.** No `products/webflash/` wrapper is added;
  no `config/webflash-builds.json` row is added; no
  `webflash_build_matrix: true` flip; no `artifact_name`. WebFlash
  Relay exposure stays **blocked** behind the seven WebFlash gates
  documented in
  [`docs/webflash-exposure-readiness-matrix.md` §Relay / S360-310 WebFlash posture](webflash-exposure-readiness-matrix.md#relay--s360-310-webflash-posture).
- **WebFlash import readiness.** Cross-repo `WF-IMPORT-RELAY-001`
  stays blocked behind upstream `RELEASE-RELAY-001`.
- **Release artifact.** No FanRelay `.bin` is built / signed /
  attached / imported; no checksum file; no build-info
  `manifest.json`; no GitHub Release tag; no proof row in
  [`docs/webflash-release-proof.md`](webflash-release-proof.md).
  `RELEASE-RELAY-001` stays **blocked**.
- **Compliance approval.** Mains-voltage compliance
  (`COMPLIANCE-001` UK / EU assessment) is not advanced; no
  competent-person sign-off; no installation-approval evidence; no
  creepage / clearance / thermal / EMI certification claim.
- **Hardware behavior.** No bench, harness, silkscreen, schematic,
  pinmap, thermal, or EMI evidence is generated by a compile pass.
  The pair-scoped boot-OK observation in
  [`docs/hardware/core-abstract-bus-001c-rebind-plan.md`](hardware/core-abstract-bus-001c-rebind-plan.md)
  decisions #16 / #17 and the `S360-310-BENCH-EVIDENCE-001`
  pair-scoped 10-cycle × 4-power-path boot evidence are **not**
  generic `GPIO3` strap-pin boot-behaviour claims and remain
  unchanged.
- **Production-wide / multi-unit hardware characterisation.** Single
  pair-scoped evidence does not generalise to production batches; no
  multi-unit / oscilloscope-traced generalisation is implied by
  compile success.
- **Web Serial flashing.** A compile pass does not exercise the Web
  Serial / WebFlash flashing path; the FanRelay target is not
  imported to WebFlash.
- **Boot on real hardware.** A compile pass does not boot the
  resulting firmware on a device.
- **Sensor / Relay / LED behavior.** A compile pass does not
  exercise the FanRelay switch / `K1` contact / VentIQ / RoomIQ
  sensors at runtime.
- **`RELEASE-RELAY-001` unblock.** A compile pass does not close or
  unblock `RELEASE-RELAY-001`. The atomic `RELEASE-RELAY-001` slice
  (build / sign / attach the `.bin`, generate release notes, emit
  SHA256 + MD5 checksums, attach the build-info `manifest.json`,
  record the release-proof row, hand off to WebFlash-side import)
  remains owed to a later PR.
- **`WEBFLASH-RELAY-001` unblock.** A compile pass does not advance
  any of the seven WebFlash gates owned by `WEBFLASH-RELAY-001`.
- **Default-kit / recommended status.** The `S360-KIT-BATH-RELAY`
  row in
  [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json)
  stays `future-expansion` / `hardware-pending` /
  `webflash_exposure_allowed_now: false` /
  `stable_ready_now: false`; the default sellable bathroom kit
  remains `S360-KIT-BATH-POE` mapped to Release-One.
- **Stable or preview promotion.** Release-One stays
  `Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`; the LED preview
  stays `Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`; FanTRIAC stays
  `blocked` / `HW-005`.

The full 17-row stable-promotion gauntlet documented in
[`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
remains the source of truth for preview / stable readiness; this
audit-log entry does not close any row in that gauntlet.

### 2026-05-22 — FW-COMPILE-RELAY-RESULT-001

> **Superseded / corrected by FW-COMPILE-RELAY-FULL-FIX-001
> (2026-05-24).** A later full-compile run (`26334334727`) **failed**
> on the FanRelay target with a `GPIO3` double-bind (the Core
> `main_relay` `switch.gpio` and the FanRelay `fan_relay_switch`
> `switch.gpio` both bound `${relay_pin}` → `GPIO3`). The "successful
> full compile" claim below did not exercise the composed GPIO binding
> that the full-compile lane catches. The double-bind is fixed by
> FW-COMPILE-RELAY-FULL-FIX-001 (see the 2026-05-24 audit-log entry
> below); full-compile success is **not** re-claimed until a manual
> `workflow_dispatch` `compile_mode=full` rerun passes.

This entry records the **successful GitHub Actions compile-only
validation result** for the FanRelay compile-only target added by
`FW-COMPILE-RELAY-001` / PR #566. The
`Compile-only Firmware Validation` workflow ran against the
expanded eight-target compile-only lane and **passed**: the
FanRelay compile-only target
(`ceiling-poe-ventiq-fanrelay-roomiq-compile-only`, pointing at
[`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml)
with `config_string: Ceiling-POE-VentIQ-FanRelay-RoomIQ`,
`shipment_status: compile-only`,
`webflash_exposure_allowed_now: false`,
`advanced_manual_warning_only: true`, `hardware_pending: true`)
now has a **green CI result**.

- **Workflow.** `Compile-only Firmware Validation`
  ([`.github/workflows/compile-only.yml`](../.github/workflows/compile-only.yml))
- **Run ID.** `26298089904`
- **Status.** `completed`
- **Conclusion.** `success`
- **Scope.** PR/head validation for `FW-COMPILE-RELAY-001` / PR #566
- **Target count.** **8** compile-only targets (the two
  WebFlash-current product YAMLs from FW-COMPILE-MATRIX-001 + the
  five POE non-fan compile-only skeletons from
  FW-COMPILE-POE-NONFAN-001 + the new FanRelay compile-only
  target from FW-COMPILE-RELAY-001 / PR #566).
- **Companion run.** Quick Validation run ID `26298090061` also
  succeeded against the same head.

#### What this successful run proves

A passing `Compile-only Firmware Validation` run against the
eight-target compile-only lane proves
**YAML / package / ESPHome compile confidence** for the FanRelay
compile-only target alongside the seven prior targets. Concretely,
for the FanRelay product YAML
[`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml):

- the YAML parses and the substitutions resolve (including the
  `${relay_pin}` → `GPIO3` inheritance chain from the parent Core
  abstract package post-`CORE-ABSTRACT-BUS-001A`);
- the `packages:` composition resolves and every `!include`
  resolves (Core ceiling, PoE PSU, VentIQ, RoomIQ, FanRelay, base,
  health);
- ESPHome's component / config schema validates;
- the codegen pass produces compilable source;
- the validator script's metadata gates pass alongside the
  compile pass;
- the prior seven compile-only targets continue to compose /
  substitute / `!include`-resolve / codegen cleanly under the
  current ESPHome version (no regression introduced by the
  FanRelay target add).

#### What this successful run does **not** prove

Compile success is necessary but **not sufficient** for any
shipment-readiness claim. In particular, this run does **not**
prove any of the following, and nothing in this audit-log entry
should be read as a claim that any of them are now closed:

- **WebFlash exposure.** No FanRelay
  [`products/webflash/`](../products/webflash/) wrapper is added;
  no FanRelay row in
  [`config/webflash-builds.json`](../config/webflash-builds.json);
  no `webflash_build_matrix: true` flip; no `artifact_name`.
  WebFlash Relay exposure stays **blocked** behind the seven
  WebFlash gates documented in
  [`docs/webflash-exposure-readiness-matrix.md` §Relay / S360-310 WebFlash posture](webflash-exposure-readiness-matrix.md#relay--s360-310-webflash-posture).
- **WebFlash import readiness.** Cross-repo
  `WF-IMPORT-RELAY-001` stays blocked behind upstream
  `RELEASE-RELAY-001`.
- **Release artifact.** No FanRelay `.bin` is built / signed /
  attached / imported; no checksum file; no build-info
  `manifest.json`; no GitHub Release tag; no proof row in
  [`docs/webflash-release-proof.md`](webflash-release-proof.md).
  `RELEASE-RELAY-001` stays **blocked** because no WebFlash
  wrapper / build matrix / artifact path exists.
- **Compliance approval.** Mains-voltage compliance
  (`COMPLIANCE-001` UK / EU assessment) is not advanced; no
  competent-person sign-off; no installation-approval evidence;
  no creepage / clearance / thermal / EMI certification claim.
- **Hardware behavior.** No bench, harness, silkscreen,
  schematic, pinmap, thermal, or EMI evidence is generated by a
  compile pass. The pair-scoped boot-OK observations recorded in
  the prior FanRelay evidence audit (PRs #557 / #561) remain
  pair-scoped and are **not** generic ESP32-S3 `GPIO3` strap-pin
  boot-behaviour claims.
- **Production-wide / multi-unit hardware characterisation.**
  Single pair-scoped evidence does not generalise to production
  batches; no multi-unit / oscilloscope-traced generalisation is
  implied by compile success.
- **Web Serial flashing.** A compile pass does not exercise the
  Web Serial / WebFlash flashing path; the FanRelay target is
  not imported to WebFlash.
- **Boot on real hardware.** A compile pass does not boot the
  resulting firmware on a device.
- **Sensor / Relay / LED behavior.** A compile pass does not
  exercise the FanRelay switch / `K1` contact / VentIQ / RoomIQ
  sensors at runtime.
- **`RELEASE-RELAY-001` unblock.** A green CI result does not
  close or unblock `RELEASE-RELAY-001`. The atomic
  `RELEASE-RELAY-001` slice (build / sign / attach the `.bin`,
  generate release notes, emit SHA256 + MD5 checksums, attach
  the build-info `manifest.json`, record the release-proof row,
  hand off to WebFlash-side import) remains owed to a later PR
  because no WebFlash wrapper / build matrix / artifact path
  exists.
- **`WEBFLASH-RELAY-001` unblock.** A green CI result does not
  advance any of the seven WebFlash gates owned by
  `WEBFLASH-RELAY-001`.
- **Default-kit / recommended status.** The `S360-KIT-BATH-RELAY`
  row in
  [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json)
  stays `future-expansion` / `hardware-pending` /
  `webflash_exposure_allowed_now: false` /
  `stable_ready_now: false`; the default sellable bathroom kit
  remains `S360-KIT-BATH-POE` mapped to Release-One.
- **Stable or preview promotion.** Release-One stays
  `Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`; the LED
  preview stays `Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`;
  FanTRIAC stays `blocked` / `HW-005`.

The full 17-row stable-promotion gauntlet documented in
[`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
remains the source of truth for preview / stable readiness; this
audit-log entry does not close any row in that gauntlet.

### 2026-05-23 — FW-COMPILE-DAC-001 FanDAC compile-only validation

This entry records the addition of a single FanDAC compile-only
target to the
[`config/compile-only-targets.json`](../config/compile-only-targets.json)
lane after `PACKAGE-DAC-001` / PR #573 implemented the FanDAC package
(two GP8403 dual-channel I²C DACs, four neutral outputs) and
`PRODUCT-DAC-001-READINESS-REFRESH` / PR #574 recorded the gp8403
voltage-enum concern and blocked the FanDAC product YAML until this
compile-only validation confirms or fixes it.

Unlike `FW-COMPILE-RELAY-001` (which reused a landed canonical
product YAML at the top level of `products/`), **FanDAC has no landed
product YAML** — `PRODUCT-DAC-001` is gated on this validation, and a
top-level `products/` YAML would require a
[`config/product-catalog.json`](../config/product-catalog.json) entry,
which this slice must not add. The FanDAC compile-only skeleton
therefore lives **under `products/compile-only/`** (the namespace
excluded from the top-level catalog-enumeration gate at
[`tests/test_product_catalog.py`](../tests/test_product_catalog.py)),
and is the one explicitly-registered fan target permitted under that
directory.

#### Target

| `id`                              | `product_yaml`                                | `config_string`      |
|-----------------------------------|-----------------------------------------------|----------------------|
| `ceiling-poe-fandac-compile-only` | `products/compile-only/ceiling-poe-fandac.yaml` | `Ceiling-POE-FanDAC` |

Settings on the row:

- `shipment_status: compile-only`
- `webflash_exposure_allowed_now: false`
- `hardware_required_for_validation: true`
- `blocked: false`
- `compile_validation_status: pending-ci`
- `voltage_enum_fixed: true`

The skeleton composes Core ceiling + PoE PSU + base + health (the
proven `Ceiling-POE` base) plus the canonical FanDAC alias
[`packages/expansions/fan_dac.yaml`](../packages/expansions/fan_dac.yaml)
(a pure `!include` wrapper of the legacy
[`packages/expansions/fan_gp8403.yaml`](../packages/expansions/fan_gp8403.yaml)).
The GP8403 chips bind the shared `core_i2c` bus the Core ceiling
package provides.

#### The gp8403 voltage-enum concern — resolved (Option A)

PR #574 flagged that the package fed the gp8403 `voltage:` field the
neutral string `0-10V`, while ESPHome's gp8403 component accepts only
the bare enum tokens **`10V`** or **`5V`**
([esphome.io/components/output/gp8403](https://esphome.io/components/output/gp8403)).
ESPHome config validation rejects `0-10V` / `0-5V`. This is a static
(documented-schema) defect, so FW-COMPILE-DAC-001 **fixes** it rather
than merely tracking it:

- `fan_dac_1_output_range` and `fan_dac_2_output_range` in
  [`packages/expansions/fan_gp8403.yaml`](../packages/expansions/fan_gp8403.yaml)
  are corrected from `"0-10V"` to `"10V"`.
- The **customer-facing** range that `10V` produces stays **0-10V**;
  the user-facing `0-10V` / `0-5V` labels live in the product / kit
  docs (e.g. `S360-KIT-DUCT-0-10V`), never in the `voltage:`
  substitution.
- This matches the default `10V` the output-range policy already
  implied (operator decision D3,
  [`docs/hardware/s360-312-r4-fandac.md` §Output-range policy — row 6](hardware/s360-312-r4-fandac.md#output-range-policy--row-6-closed)).
- A single GP8403 still **cannot** drive one output at 0-5V and the
  other at 0-10V (one `V5V` reference / one range register `0x01` per
  chip); this target makes no such claim.

[`tests/test_fandac_package.py`](../tests/test_fandac_package.py)
pins the corrected enum (`10V`, never `0-10V` / `0-5V`); the new
[`tests/test_compile_targets.py`](../tests/test_compile_targets.py)
`FanDACCompileOnlyCoverageTests` pins the target invariants.

#### What compile-only proves for the FanDAC target

Once
[`scripts/validate_compile_targets.py --compile`](../scripts/validate_compile_targets.py)
(or `esphome config products/compile-only/ceiling-poe-fandac.yaml`)
is run **in CI**, a passing run proves the following for the FanDAC
skeleton (and only for it, only under the ESPHome version recorded in
the workflow):

- the YAML parses and substitutions resolve (including the
  `fan_dac_i2c_id: core_i2c` bus binding and the per-chip `address`
  / `voltage` enum substitutions);
- the `packages:` composition and every `!include` resolve;
- ESPHome's gp8403 component / config schema validates the corrected
  `voltage: 10V` enum;
- the codegen pass produces compilable source.

#### What is NOT claimed

- **Compile success is not claimed yet.** ESPHome is not assumed
  present in the local environment; `compile_validation_status:
  pending-ci` records that compile success is **unproven** until the
  `--compile` lane runs in CI. The metadata lane
  (`--metadata-only`) is what is asserted by this PR. No "compiles
  cleanly" claim is made until CI proves it.
- **No product YAML.** No FanDAC YAML is added at the top level of
  `products/`; no `config/product-catalog.json` entry;
  `PRODUCT-DAC-001` stays gated.
- **No WebFlash exposure.** No `products/webflash/` wrapper; no
  `config/webflash-builds.json` entry; no `webflash_build_matrix`
  flip; no `artifact_name`. The `FanDAC` token does not appear in
  `config/webflash-builds.json`.
- **No release artifact.** No `.bin`, checksum, build-info manifest,
  GitHub Release tag, or proof row.
- **No hardware / schematic / BOM proof.** S360-312
  `schematic_status` and BOM evidence remain open; compile success
  proves none of it.
- **No stable / preview promotion.** Release-One stays
  `Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`; the LED preview
  stays `Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`; FanTRIAC stays
  `blocked` / `HW-005`.

### 2026-05-23 — FW-COMPILE-DAC-RESULT-001

> **Update — FW-COMPILE-DAC-FULL-RESULT-001 (2026-05-24).** The full
> `esphome compile` pass that this entry recorded as **owed** (the
> `Compile-only Targets — Full ESPHome Compile` job was `skipped` on the
> PR #575 head, so `compile_validation_status: pending-ci` stood) has now
> **passed** — the manual `workflow_dispatch` `compile_mode=full` run
> `26364679370` against post-#578 `main` (merge commit `4906a22`)
> compiled all nine compile-only targets green, including the FanDAC
> target `ceiling-poe-fandac-compile-only` →
> [`products/compile-only/ceiling-poe-fandac.yaml`](../products/compile-only/ceiling-poe-fandac.yaml)
> (see the `FW-COMPILE-DAC-FULL-RESULT-001` entry below). For the
> full-compile concern this **metadata-only** result is therefore
> superseded; the `compile_validation_status: pending-ci` marker in
> [`config/compile-only-targets.json`](../config/compile-only-targets.json)
> is now satisfied by run `26364679370` (the literal config-flag flip is a
> separate config-layer change, out of scope for this docs-only record).

This entry records the **GitHub Actions compile-only validation
result** for the FanDAC compile-only target added by
`FW-COMPILE-DAC-001` / PR #575
(`ceiling-poe-fandac-compile-only`, pointing at
[`products/compile-only/ceiling-poe-fandac.yaml`](../products/compile-only/ceiling-poe-fandac.yaml)
with `config_string: Ceiling-POE-FanDAC`,
`shipment_status: compile-only`,
`webflash_exposure_allowed_now: false`,
`hardware_required_for_validation: true`,
`compile_validation_status: pending-ci`, `voltage_enum_fixed: true`).
The `Compile-only Firmware Validation` workflow ran against the
expanded nine-target compile-only lane on the PR head and the
metadata-validation lane **passed**.

- **Workflow.** `Compile-only Firmware Validation`
  ([`.github/workflows/compile-only.yml`](../.github/workflows/compile-only.yml))
- **Run ID.** `26332462496`
- **Status.** `completed`
- **Conclusion.** `success`
- **Head SHA.** `9989861befdec81e630f7a0749f9f4019084c607`
- **Scope.** PR/head validation for `FW-COMPILE-DAC-001` / PR #575.
- **Target count.** **9** compile-only targets (the two
  WebFlash-current product YAMLs from FW-COMPILE-MATRIX-001 + the
  five POE non-fan compile-only skeletons from
  FW-COMPILE-POE-NONFAN-001 + the FanRelay compile-only target from
  FW-COMPILE-RELAY-001 / PR #566 + the new FanDAC compile-only
  target from FW-COMPILE-DAC-001 / PR #575).
- **Jobs.**
  - `Compile-only Targets — Metadata Validation` — **`success`**
    (the `--metadata-only` lane plus `tests/test_compile_targets.py`).
  - `Compile-only Targets — Full ESPHome Compile` — **`skipped`**.
    This job is gated
    `if: github.event_name == 'workflow_dispatch' && github.event.inputs.compile_mode == 'full'`
    ([`.github/workflows/compile-only.yml`](../.github/workflows/compile-only.yml)
    line 103), so it does **not** run on a `pull_request` / `push`
    event — only on a manual `workflow_dispatch` with
    `compile_mode=full`. No such dispatch was run for this head, so
    **no `esphome config` / `esphome compile` was executed against
    the FanDAC skeleton in CI**.
- **Companion run.** `Quick Validation` run ID `26332462516`
  (`YAML Syntax Check`) also succeeded against the same head; that
  job runs only Python / `pyyaml` validators
  ([`.github/workflows/validate.yml`](../.github/workflows/validate.yml)),
  **not** `esphome config` / `compile`.

#### What this result proves

The green `Compile-only Firmware Validation` run proves the
**metadata / structural** lane for the nine-target compile-only
lane, including the new FanDAC target. Concretely, for
`ceiling-poe-fandac-compile-only`:

- the target's `product_yaml`
  ([`products/compile-only/ceiling-poe-fandac.yaml`](../products/compile-only/ceiling-poe-fandac.yaml))
  exists on disk and the row's metadata is well-formed;
- the `config_string` `Ceiling-POE-FanDAC` cross-references cleanly
  against
  [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json);
- the row carries no `webflash_build_matrix` / `artifact_name`
  declaration, is absent from
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  and is not in `release_one_required_configs` — the compile-only
  guardrails hold;
- the lane total is **9** and the prior eight targets are unchanged
  (no metadata regression);
- `tests/test_compile_targets.py`
  (`FanDACCompileOnlyCoverageTests`) and `tests/test_fandac_package.py`
  pass — the latter pins the corrected GP8403 `voltage:`
  substitutions to the ESPHome-**documented** bare enum **`10V`**
  (never `0-10V` / `0-5V`).

The GP8403 voltage-enum fix (Option A — `0-10V` → `10V`) is therefore
confirmed against the **documented** ESPHome `gp8403` schema and
pinned by string-equality tests, and the metadata lane is green.

#### What this result does **not** prove

The full `esphome config` / `esphome compile` lane was **skipped** on
this PR (it runs only via `workflow_dispatch` with
`compile_mode=full`). This green result therefore does **not** prove
that ESPHome itself compiled the FanDAC skeleton, and the
`compile_validation_status: pending-ci` marker on the target
**stands** — an actual `esphome config` / `--compile` pass for
`Ceiling-POE-FanDAC` is still owed to a manual `workflow_dispatch`
full-compile run. Specifically, this result does **not** prove:

- **Skeleton compiles in ESPHome.** No `esphome config` /
  `esphome compile` was executed against
  `products/compile-only/ceiling-poe-fandac.yaml`; the `packages:`
  composition / `!include` resolution / component-schema validation /
  codegen pass were **not** exercised by ESPHome in this run.
- **The `voltage: 10V` enum is accepted by the ESPHome config
  validator at runtime.** The fix is validated only against ESPHome's
  *documented* schema and pinned by tests; ESPHome's own validator
  did not run on this PR.
- **DAC product readiness.** No FanDAC product YAML at the top level
  of [`products/`](../products/); no
  [`config/product-catalog.json`](../config/product-catalog.json)
  entry. `PRODUCT-DAC-001` stays gated.
- **WebFlash readiness.** No `products/webflash/` wrapper, no
  [`config/webflash-builds.json`](../config/webflash-builds.json) row,
  no `webflash_build_matrix` flip, no `artifact_name`.
  `WEBFLASH-DAC-001` stays blocked.
- **Release artifact.** No `.bin`, checksum, build-info manifest,
  GitHub Release tag, or proof row. `RELEASE-DAC-001` stays blocked.
- **Harness / fan bench validation.** No bench, harness, silkscreen,
  schematic, pinmap, thermal, or EMI evidence is generated. The
  `J2` / `J3` → Cloudlift S12 harness conductor trace and the `J3`
  `out0` / `out1` silkscreen-transposition caveat remain open.
  `S360-312` `schematic_status` stays `cataloged_unverified`.
- **Compliance.** No compliance claim; no simultaneous per-output
  0-5V + 0-10V on a single GP8403 is claimed (one `V5V` reference /
  one range register `0x01` per chip).

The target is **compile-only only**: a green metadata CI result is a
necessary-but-insufficient input to the broader preview-to-stable
promotion process and discharges none of the DAC product / WebFlash /
release / hardware / compliance gates. The full 17-row
stable-promotion gauntlet in
[`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
remains the source of truth for preview / stable readiness; this
audit-log entry does not close any row in that gauntlet.

### 2026-05-24 — FW-COMPILE-RELAY-FULL-FIX-001 FanRelay GPIO3 double-bind fix

> **Update — FW-COMPILE-RELAY-FULL-RESULT-001 (2026-05-24).** The manual
> `workflow_dispatch` `compile_mode=full` rerun owed by this entry has now
> **passed** — run `26364679370` (see the
> `FW-COMPILE-RELAY-FULL-RESULT-001` entry below). The previously failed
> run `26334334727` is superseded.

This entry records the **fix** for the FanRelay full-compile failure.
The `Compile-only Firmware Validation` full-compile lane run
**`26334334727`** **failed** on the FanRelay target
(`Ceiling-POE-VentIQ-FanRelay-RoomIQ`,
[`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml))
with a `GPIO3` double-bind. FanDAC validated cleanly in the same set
and is **not** touched by this fix.

#### Root cause

The parent Core abstract package
[`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml)
already declares the `main_relay` `switch.gpio` on
`pin: ${relay_pin}` (the schematic-correct `GPIO3` post-`CORE-ABSTRACT-BUS-001A`).
[`packages/expansions/fan_relay.yaml`](../packages/expansions/fan_relay.yaml)
additionally declared a **second** `switch.platform: gpio`
(`id: fan_relay_switch`) on `pin: ${fan_relay_pin}`, whose default is
`${relay_pin}`. When the FanRelay product composes both packages, two
GPIO components bind the same resolved pin (`GPIO3`), which ESPHome
rejects at config validation. The package-layer / metadata gates that
ran on earlier PRs never composed the two `gpio` switches together, so
only the full `esphome` compile lane surfaced the collision.

#### Fix (shape C — split ownership, no pin rebind)

The FanRelay package now exposes `fan_relay_switch` as a
`switch.platform: template` that **proxies** the Core `main_relay`
(`turn_on_action: switch.turn_on: main_relay`,
`turn_off_action: switch.turn_off: main_relay`,
`lambda: 'return id(main_relay).state;'`). It declares no
`gpio`-platform component and names no GPIO, so the resolved relay pin
has exactly **one** owner (`main_relay`). `${relay_pin}` stays abstract
and resolves through the Core substitution layer; the `relay_pin` value
is unchanged (`GPIO3`). The `fan_relay_pin` substitution is retired (it
no longer has a consumer). Invariants are pinned by the updated
[`tests/test_fan_relay_package.py`](../tests/test_fan_relay_package.py)
(`FanRelaySwitchReusesMainRelayTests`, `FanRelayNoGpioPlatformTests`,
`FanRelaySingleRelayGpioOwnerTests`, `FanDacCompileOnlyTargetUnchangedTests`).

#### What this fix proves — and does **not** prove

The double-bind is removed at the YAML / package layer and the local
metadata / structural lane is green
(`tests/validate_configs.py`,
`scripts/validate_compile_targets.py --metadata-only`,
`tests/test_fan_relay_package.py`, `tests/test_relay_product_readiness.py`,
`tests/test_core_abstract_bus.py`, `tests/test_compile_targets.py`, and
the full `python3 -m unittest discover -s tests` suite all pass).

**Full compile success is NOT claimed.** ESPHome is not available in the
authoring environment, so neither `esphome config
products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml` nor
`scripts/validate_compile_targets.py --compile` was run here. A manual
`workflow_dispatch` of the `Compile-only Firmware Validation` lane with
`compile_mode=full` remains **required** to confirm the FanRelay target
now compiles green. This fix supersedes the FW-COMPILE-RELAY-RESULT-001
(2026-05-22) "successful full compile" claim, which run `26334334727`
contradicted.

This entry does **not** advance WebFlash exposure, release, or import:
no `products/webflash/` wrapper, no
[`config/webflash-builds.json`](../config/webflash-builds.json) row, no
`webflash_build_matrix` flip, no `artifact_name`, no release artifact.
`WEBFLASH-RELAY-001`, `RELEASE-RELAY-001`, and `WF-IMPORT-RELAY-001`
stay blocked; the FanRelay compile-only target stays
`shipment_status: compile-only` /
`webflash_exposure_allowed_now: false` /
`advanced_manual_warning_only: true` / `hardware_pending: true`. No
compliance / installation-approval / competent-person sign-off claim is
made.

### 2026-05-24 — FW-COMPILE-RELAY-FULL-RESULT-001 FanRelay full compile result after #578

This entry records the **successful manual full-compile run** for the
FanRelay target after `FW-COMPILE-RELAY-FULL-FIX-001` / PR #578 fixed the
`GPIO3` double-bind. A `workflow_dispatch` run of the
`Compile-only Firmware Validation` lane with `compile_mode=full` — the
mode that actually invokes `esphome` against every
[`config/compile-only-targets.json`](../config/compile-only-targets.json)
target per
[`.github/workflows/compile-only.yml`](../.github/workflows/compile-only.yml)
line 103 — was triggered against the post-#578 `main` and **passed**.

- **Workflow.** `Compile-only Firmware Validation`
  ([`.github/workflows/compile-only.yml`](../.github/workflows/compile-only.yml))
- **Run ID.** `26364679370`
- **Event.** `workflow_dispatch`
- **Mode.** `compile_mode=full`
- **Status.** `completed`
- **Conclusion.** `success`
- **Jobs.** `Compile-only Targets — Metadata Validation` (job
  `77606314361`, conclusion `success`) → `Compile-only Targets — Full
  ESPHome Compile` (job `77606324332`, conclusion `success`; the
  "Run compile-only validator (full compile)" step completed
  successfully).
- **Target count.** **9** compile-only targets — the FanRelay target
  `ceiling-poe-ventiq-fanrelay-roomiq-compile-only` →
  [`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml)
  alongside the eight others.
- **Ref.** post-#578 `main` (merge commit `4906a22`).

**The previous full-compile run `26334334727` — which failed on the
FanRelay target (`Ceiling-POE-VentIQ-FanRelay-RoomIQ`) with the `GPIO3`
double-bind — is superseded by this successful run `26364679370`.** The
FW-COMPILE-RELAY-FULL-FIX-001 shape-C fix (`fan_relay_switch` as a
`switch.template` proxying the Core `main_relay`; single owner of the
resolved relay pin; `relay_pin` unchanged at `GPIO3`) now composes and
full-compiles green.

#### What this successful run proves

A passing `compile_mode=full` run proves that the FanRelay target — and
all nine compile-only targets — pass a real `esphome` compile under the
pinned ESPHome version: YAML parse, substitution resolution (including
`${relay_pin}` → `GPIO3`), `packages:` / `!include` composition, the
single-relay-owner GPIO binding, component / config schema validation,
and the codegen pass. It confirms the `GPIO3` double-bind is gone at the
full-compile layer, not just the metadata layer.

#### What this successful run does **not** prove

Compile success is necessary but **not sufficient** for any
shipment-readiness claim. This run does **not** advance WebFlash
exposure, release, or import for the Relay product, and is **not** a
hardware, bench, compliance, installation-approval, or safety claim:

- **Relay stays no-WebFlash / no-release.** No `products/webflash/`
  wrapper; no
  [`config/webflash-builds.json`](../config/webflash-builds.json) row;
  no `webflash_build_matrix` flip; no `artifact_name`; no release
  artifact / tag / checksum / build-info manifest.
- `WEBFLASH-RELAY-001`, `RELEASE-RELAY-001`, and `WF-IMPORT-RELAY-001`
  stay **blocked**; WebFlash import / release readiness is **not**
  claimed.
- The FanRelay compile-only target stays `shipment_status: compile-only`
  / `webflash_exposure_allowed_now: false` /
  `advanced_manual_warning_only: true` / `hardware_pending: true`.
- `S360-310` `schematic_status` stays `cataloged_unverified`; no
  COMPLIANCE-001 movement; no compliance / board-level mains-safety
  certification, installation-approval, competent-person sign-off, or
  production-wide / multi-unit hardware characterisation claim.
- FanDAC is untouched; the artefact produced by `--compile` is CI-only
  confidence and is **not** a shippable build.

This is a docs-only record. No `packages/**`, `products/**`,
`products/webflash/**`, `config/**`, `scripts/**`,
`.github/workflows/**`, `components/**`, `include/**`, `tests/**`,
`firmware/**`, `manifest.json`, `firmware/sources.json`, release
artifact, checksum, or build-info edit is made; the WebFlash repository
(`sense360store/WebFlash`) is untouched.

### 2026-05-24 — FW-COMPILE-DAC-FULL-RESULT-001 FanDAC full compile result in run 26364679370

This entry records that the **successful manual full-compile run
`26364679370`** — the same `workflow_dispatch` `compile_mode=full` run
that `FW-COMPILE-RELAY-FULL-RESULT-001` recorded for the FanRelay
target — **also validates the FanDAC compile-only target**. The
`compile_mode=full` lane invokes `esphome` against **every**
[`config/compile-only-targets.json`](../config/compile-only-targets.json)
target via `scripts/validate_compile_targets.py --compile`
([`.github/workflows/compile-only.yml`](../.github/workflows/compile-only.yml)
lines 100-153); `run_compile()` returns non-zero if **any** target
fails, so a `success` conclusion proves **all nine** targets compiled —
FanDAC included. No separate FanDAC-only run was needed.

- **Workflow.** `Compile-only Firmware Validation`
  ([`.github/workflows/compile-only.yml`](../.github/workflows/compile-only.yml))
- **Run ID.** `26364679370`
- **Event.** `workflow_dispatch`
- **Mode.** `compile_mode=full`
- **Status.** `completed`
- **Conclusion.** `success`
- **Jobs.** `Compile-only Targets — Metadata Validation` (job
  `77606314361`, conclusion `success`) → `Compile-only Targets — Full
  ESPHome Compile` (job `77606324332`, conclusion `success`; the
  "Run compile-only validator (full compile)" step completed
  successfully after ~26m of `esphome compile` work).
- **Target count.** **9** compile-only targets.
- **FanDAC target included.** The 9th target
  `ceiling-poe-fandac-compile-only` →
  [`products/compile-only/ceiling-poe-fandac.yaml`](../products/compile-only/ceiling-poe-fandac.yaml)
  (`config_string: Ceiling-POE-FanDAC`) was present in
  [`config/compile-only-targets.json`](../config/compile-only-targets.json)
  at the ref the run validated and the YAML existed on disk there.
- **Ref.** post-#578 `main` (merge commit `4906a22`) — the same ref
  `FW-COMPILE-RELAY-FULL-RESULT-001` recorded.

#### How FanDAC inclusion is proven

The run was triggered against merge commit `4906a22` (post-#578 `main`).
At that commit, [`config/compile-only-targets.json`](../config/compile-only-targets.json)
declared exactly **9** targets (`totals.targets: 9`), the ninth being
`ceiling-poe-fandac-compile-only` pointing at
`products/compile-only/ceiling-poe-fandac.yaml`, and that YAML existed.
The `--compile` validator iterates over every target and fails the job
on the first non-zero `esphome compile`, so the job's `success`
conclusion means **each** of the nine — FanDAC among them — compiled
under the pinned ESPHome `2026.4.5`. FanDAC inclusion is therefore proven
from the target manifest at the validated ref combined with the
all-or-nothing semantics of the full-compile job, not inferred.

#### What this successful run proves

A passing `compile_mode=full` run proves the FanDAC compile-only target
passes a real `esphome` compile: YAML parse, substitution resolution
(including the corrected GP8403 `voltage: 10V` enum), `packages:` /
`!include` composition of the two GP8403 dual-channel DACs on the shared
`core_i2c` bus, component / config-schema validation, and the codegen
pass. The **GP8403 voltage-enum fix** (Option A, `0-10V` → `10V`, from
`FW-COMPILE-DAC-001` / PR #575) is now **compile-validated by ESPHome's
own validator**, not only against the documented schema and the
string-equality tests in `tests/test_fandac_package.py`. This supersedes
the **full-compile** concern that `FW-COMPILE-DAC-RESULT-001`
(2026-05-23) left owed: that entry recorded only the green
**metadata** lane (the full-compile job was `skipped` on the PR head).

#### What this successful run does **not** prove

Compile success is necessary but **not sufficient** for any
shipment-readiness claim. This run does **not** advance DAC product
WebFlash exposure, release, or import, and is **not** a hardware, bench,
schematic, compliance, or safety claim:

- **`PRODUCT-DAC-001` has product YAML but stays no-WebFlash /
  no-release.** The canonical product YAML
  [`products/sense360-ceiling-poe-fandac.yaml`](../products/sense360-ceiling-poe-fandac.yaml)
  (PR #577) and its `hardware-pending`
  [`config/product-catalog.json`](../config/product-catalog.json) row
  (`webflash_build_matrix: false`, no `artifact_name`, no
  `webflash_wrapper`) are unchanged; no `products/webflash/` wrapper; no
  [`config/webflash-builds.json`](../config/webflash-builds.json) row
  (the `FanDAC` token is absent there).
- `WEBFLASH-DAC-001`, `RELEASE-DAC-001`, and `WF-IMPORT-DAC-001` stay
  **blocked**; WebFlash import / release readiness is **not** claimed.
- The FanDAC compile-only target stays `shipment_status: compile-only` /
  `webflash_exposure_allowed_now: false`. The
  `compile_validation_status: pending-ci` marker in
  [`config/compile-only-targets.json`](../config/compile-only-targets.json)
  is now satisfied by this run; flipping that literal config flag is a
  separate config-layer change outside this docs-only record's scope.
- `S360-312` `schematic_status` stays `cataloged_unverified`; the `J2` /
  `J3` → Cloudlift S12 harness conductor trace and the `J3` `out0` /
  `out1` silkscreen-transposition caveat remain open; no compliance or
  safety-certification claim is made. A single GP8403 still cannot drive
  one output at 0-5V and the other at 0-10V (one `V5V` reference / one
  range register per chip); this run claims no such thing.
- The artefact produced by `--compile` is CI-only confidence and is
  **not** a shippable build.

This is a docs-only record. No `packages/**`, `products/**`,
`products/webflash/**`, `config/**`, `scripts/**`,
`.github/workflows/**`, `components/**`, `include/**`, `tests/**`,
`firmware/**`, `manifest.json`, `firmware/sources.json`, release
artifact, checksum, or build-info edit is made; FanDAC and FanRelay code
is untouched; the WebFlash repository (`sense360store/WebFlash`) is
untouched.

## See also

- [`docs/firmware-combination-matrix.md`](firmware-combination-matrix.md) — FW-MATRIX-001, the 168-row source matrix the `config_string` field cross-references.
- [`docs/firmware-build-gap-report.md`](firmware-build-gap-report.md) — FW-MATRIX-002, the priority-lane lens.
- [`docs/kit-intent-matrix.md`](kit-intent-matrix.md) — KIT-MATRIX-001, the productized kit-intent layer.
- [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md) — the 17-row stable-promotion gauntlet.
- [`docs/webflash-contract.md`](webflash-contract.md) — canonical config-string grammar.
- [`docs/ci-pipeline.md`](ci-pipeline.md) — the broader CI layout.

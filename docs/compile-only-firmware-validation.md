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
`secrets.yaml` at compile time. The current targets all live under
`products/webflash/`, so the workflow at
[`.github/workflows/compile-only.yml`](../.github/workflows/compile-only.yml)
provisions a test `secrets.yaml` at the repo root, under `products/`,
and under `products/webflash/`. Any future compile-only target placed in
a new directory needs the same provisioning extended to that directory.
The `secrets.yaml` written by the workflow is a CI-only stub; it
contains no real credentials and is gitignored.

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

## See also

- [`docs/firmware-combination-matrix.md`](firmware-combination-matrix.md) — FW-MATRIX-001, the 168-row source matrix the `config_string` field cross-references.
- [`docs/firmware-build-gap-report.md`](firmware-build-gap-report.md) — FW-MATRIX-002, the priority-lane lens.
- [`docs/kit-intent-matrix.md`](kit-intent-matrix.md) — KIT-MATRIX-001, the productized kit-intent layer.
- [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md) — the 17-row stable-promotion gauntlet.
- [`docs/webflash-contract.md`](webflash-contract.md) — canonical config-string grammar.
- [`docs/ci-pipeline.md`](ci-pipeline.md) — the broader CI layout.

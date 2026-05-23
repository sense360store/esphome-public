# Compile-only Expansion Candidates (FW-COMPILE-EXPAND-001)

## Purpose and scope

This document is the **reviewed candidate list for the next compile-only
firmware targets**. It is a planning ledger only. It does **not** add
any compile-only target, product YAML, WebFlash wrapper, or build / release
artifact. The source-of-truth compile-only lane remains
[`config/compile-only-targets.json`](../config/compile-only-targets.json);
the source-of-truth WebFlash build matrix remains
[`config/webflash-builds.json`](../config/webflash-builds.json).

The candidate list lives in machine-readable form at
[`config/compile-only-candidates.json`](../config/compile-only-candidates.json).
The structural / cross-reference / guardrail tests live in
[`tests/test_compile_expansion_candidates.py`](../tests/test_compile_expansion_candidates.py).

This document and the artefacts it describes do **not**:

- add any compile-only target to [`config/compile-only-targets.json`](../config/compile-only-targets.json),
- add any product YAML under `products/**`,
- add any WebFlash wrapper under `products/webflash/**`,
- add any entry to [`config/webflash-builds.json`](../config/webflash-builds.json),
- flip `webflash_build_matrix: true` on any product,
- add `artifact_name` to any product,
- build or attach any firmware binary,
- import any firmware to WebFlash,
- promote any product to `preview` or `stable`,
- promote `LED` to `stable`,
- promote `PWR` / `S360-400`,
- promote `POE` / `S360-410`,
- claim hardware proof exists,
- claim WebFlash import readiness exists,
- claim `RELEASE-007` is unblocked,
- change [`config/webflash-builds.json`](../config/webflash-builds.json),
  [`config/product-catalog.json`](../config/product-catalog.json),
  [`config/hardware-catalog.json`](../config/hardware-catalog.json),
  [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json),
  [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json), or
  [`config/compile-only-targets.json`](../config/compile-only-targets.json),
- change `products/**`, `products/webflash/**`, `packages/**`,
  `firmware/**`, `manifest.json`, `firmware/sources.json`,
  release artifacts, checksums, build-info manifests, or
  `.github/workflows/**`,
- change `REQUIRED_CONFIGS`.

## Why this ledger exists right now

- **FW-COMPILE-MATRIX-001** / [PR #544](https://github.com/sense360store/esphome-public/pull/544)
  added the compile-only validation lane with the two committed WebFlash
  product YAMLs (`Ceiling-POE-VentIQ-RoomIQ` stable and
  `Ceiling-POE-VentIQ-RoomIQ-LED` preview).
- **FW-COMPILE-FIX-001** / [PR #546](https://github.com/sense360store/esphome-public/pull/546)
  fixed compile-only secrets provisioning so `!secret` resolves
  relative to the per-directory product YAML.
- **FW-COMPILE-RESULT-001** / [PR #547](https://github.com/sense360store/esphome-public/pull/547)
  recorded a successful full ESPHome compile for both committed
  WebFlash product YAMLs (`rc=0` from
  `python3 scripts/validate_compile_targets.py --compile`,
  ESPHome `2026.4.5`, run `#9`).
- **FW-COMPILE-POE-NONFAN-001** / [PR #548](https://github.com/sense360store/esphome-public/pull/548)
  added five POE non-fan compile-only product YAML skeletons under
  `products/compile-only/` and enrolled them in the lane.

The compile-only lane currently covers **7 targets** (the two committed
WebFlash product YAMLs plus the five POE non-fan skeletons). This
ledger answers the question: **which config strings should become
compile-only next, which require product YAML first, which are blocked,
and which should stay out of the compile-only lane for now?**

Adding a candidate to this ledger:

- is **not** a compile-only target add;
- is **not** a product YAML add;
- is **not** a WebFlash import;
- does **not** promote any product to `preview` or `stable`;
- does **not** create or attach a firmware artifact;
- does **not** close any hardware / bench / silkscreen / schematic /
  pinmap / compliance gate.

Hardware proof remains required for any release / preview / stable
promotion. The full 17-row stable-promotion gauntlet documented in
[`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
remains the source of truth for preview / stable readiness.

## Per-candidate schema

Each row in
[`config/compile-only-candidates.json`](../config/compile-only-candidates.json)
`candidates` array carries the following fields:

| Field                          | Meaning                                                                                                          |
|--------------------------------|------------------------------------------------------------------------------------------------------------------|
| `config_string`                | WebFlash config string. Must appear in [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json). |
| `rank`                         | Integer working priority. Lower = higher priority. Non-blocked-lane ranks must all be lower than blocked-lane ranks. |
| `lane`                         | Coarse grouping. One of `poe-non-fan`, `poe-non-fan-led`, `usb-non-fan`, `usb-non-fan-led`, `pwr`, `fanrelay`, `fanpwm`, `fandac`, `fantriac`. |
| `use_case`                     | One-sentence description of what this combination is meant to express.                                            |
| `proposed_product_yaml`        | Repo-relative path the eventual compile-only YAML **would** live at. Planning hint only — no file is created by listing it here. |
| `candidate_status`             | One of `ready-for-product-yaml`, `needs-product-yaml`, `blocked-package`, `blocked-core-bus`, `blocked-hardware`, `blocked-compliance`, `defer`. |
| `reason`                       | Free-text explanation of why the candidate sits where it does.                                                   |
| `blockers`                     | Array of named blockers (PR / audit / evidence references) that gate this candidate.                              |
| `would_be_webflash_exposed_now`| Always `false` for entries in this file. A candidate is **not** a WebFlash build.                                |
| `compile_only_safe`            | `true` if the candidate is safe to add to the compile-only lane today, `false` if it must wait for upstream work. |
| `notes`                        | Free-text narrative. Used to record what the row does not imply.                                                  |

### Allowed `candidate_status` values

| Value                     | Meaning                                                                                                          |
|---------------------------|------------------------------------------------------------------------------------------------------------------|
| `ready-for-product-yaml`  | A compile-only product YAML already exists (or is trivially derivable from existing packages) and the candidate is the next slice ready to be picked up for a real product YAML / catalog promotion. Already-compile-only rows live here. |
| `needs-product-yaml`      | The candidate is the next compile-only product YAML to author. Listing the row does NOT author the YAML; it only ranks the candidate. |
| `blocked-package`         | A required package YAML (`packages/expansions/**`, `packages/hardware/**`) is deferred or not yet authored.       |
| `blocked-core-bus`        | A `CORE-ABSTRACT-BUS-001*` slice (001A / 001B / 001C) is the gating slice.                                       |
| `blocked-hardware`        | Hardware evidence (silkscreen / schematic / pinmap / bench / harness / BOM) is missing.                          |
| `blocked-compliance`      | A `COMPLIANCE-001` slice is open (mains-voltage / TRIAC / etc.).                                                 |
| `defer`                   | Multi-gate deferral (compliance + hardware + package + core-bus + product chain) — the row is documented as deferred so no compile-only PR picks it up by mistake. |

## Initial ranking (highest priority first)

The candidates are grouped by lane in working priority order. Non-blocked
lanes are ranked **strictly ahead** of blocked lanes — this invariant
is enforced by
[`tests/test_compile_expansion_candidates.py`](../tests/test_compile_expansion_candidates.py).

### Lane 1 — POE non-fan (ranks 1–5) — `ready-for-product-yaml`

The five POE non-fan compile-only skeletons added by
FW-COMPILE-POE-NONFAN-001 / PR #548. These are **already** in the
compile-only lane; they are listed here so the candidate ledger anchors
the ranking and so promotion to a full product-catalog product YAML is
tracked as the next slice.

| Rank | `config_string`            | Notes                                                                                              |
|------|----------------------------|----------------------------------------------------------------------------------------------------|
| 1    | `Ceiling-POE`              | Minimum Ceiling POE Core. Already compile-only.                                                    |
| 2    | `Ceiling-POE-RoomIQ`       | Plus RoomIQ (comfort_ceiling + presence_ceiling). Already compile-only.                            |
| 3    | `Ceiling-POE-VentIQ`       | Plus VentIQ (airiq_bathroom_base + bathroom_profile). Already compile-only.                        |
| 4    | `Ceiling-POE-AirIQ`        | Plus AirIQ (airiq_ceiling + airiq_basic_profile). Already compile-only.                            |
| 5    | `Ceiling-POE-AirIQ-RoomIQ` | Plus AirIQ + RoomIQ. Already compile-only.                                                         |

Promotion to a real product-catalog entry is blocked behind
**PRODUCT-POE-410-001** / **PACKAGE-POE-410-001** / `S360-410`
`schematic_status: verified` / S360-410 BOM evidence / Release-One PoE
caveat closure / product-onboarding approval — see the per-row
`blockers` list in
[`config/compile-only-candidates.json`](../config/compile-only-candidates.json).

### Lane 2 — POE non-fan LED preview (ranks 6–10) — `needs-product-yaml`

Compile-only **preview** candidates. The LED ring (`S360-300`) is
`schematic_status: verified` (HW-007 / HW-008) but the LED stable
gauntlet (`S360-300-BENCH-001`, `WF-HW-TEST-001`, `WF-HW-TEST-003`,
`RELEASE-007`) is open, so these candidates can only ever be
**compile-only preview confidence**, never LED stable proof.

| Rank | `config_string`                 |
|------|---------------------------------|
| 6    | `Ceiling-POE-LED`               |
| 7    | `Ceiling-POE-RoomIQ-LED`        |
| 8    | `Ceiling-POE-VentIQ-LED`        |
| 9    | `Ceiling-POE-AirIQ-LED`         |
| 10   | `Ceiling-POE-AirIQ-RoomIQ-LED`  |

`compile_only_safe: true`. Each candidate's `proposed_product_yaml`
points at a `products/compile-only/ceiling-poe-*-led.yaml` path that
does **not** yet exist; listing it here does not create the file.

The LED preview product `products/webflash/ceiling-poe-ventiq-roomiq-led.yaml`
(`Ceiling-POE-VentIQ-RoomIQ-LED`) is already in `config/webflash-builds.json`
and is **not** re-listed here.

### Lane 3 — USB non-fan (ranks 11–16) — `needs-product-yaml`

USB-powered non-fan candidates. The USB family is **not** opened in
this repo today:

- no `S360-*` USB PSU board exists in
  [`config/hardware-catalog.json`](../config/hardware-catalog.json);
- USB on `S360-100` is debug-only;
- no `PACKAGE-USB-*` / `PRODUCT-USB-*` / `WEBFLASH-USB-*` /
  `RELEASE-USB-*` chain has been opened;
- no `packages/hardware/power_usb.yaml` (or equivalent) exists.

So USB candidates are `compile_only_safe: false` until a USB-family
scope decision and a USB power package land.

| Rank | `config_string`              |
|------|------------------------------|
| 11   | `Ceiling-USB`                |
| 12   | `Ceiling-USB-RoomIQ`         |
| 13   | `Ceiling-USB-VentIQ`         |
| 14   | `Ceiling-USB-AirIQ`          |
| 15   | `Ceiling-USB-AirIQ-RoomIQ`   |
| 16   | `Ceiling-USB-VentIQ-RoomIQ`  |

USB non-fan ranks ahead of the blocked Fan / PWR lanes because the
USB-family chain is opened-once, not gated on compliance or
core-bus rebinds. Once a USB-family scope decision and a USB power
package exist, these become the simplest compile-only candidates to
add.

### Lane 4 — USB non-fan LED preview (ranks 17–21) — `needs-product-yaml`

USB-powered LED preview candidates. Same USB-family prerequisites as
Lane 3, plus the same LED-preview-only stance as Lane 2.
`compile_only_safe: false` for the same USB-family reason.

| Rank | `config_string`                  |
|------|----------------------------------|
| 17   | `Ceiling-USB-LED`                |
| 18   | `Ceiling-USB-RoomIQ-LED`         |
| 19   | `Ceiling-USB-VentIQ-LED`         |
| 20   | `Ceiling-USB-AirIQ-LED`          |
| 21   | `Ceiling-USB-AirIQ-RoomIQ-LED`   |

### Lane 5 — PWR / S360-400 (rank 22) — `defer` / `blocked-compliance`

Representative deferral row for the entire **56-row** PWR lane
(`Ceiling-PWR` plus 55 PWR-bearing variants).

| Rank | `config_string` | Status  |
|------|-----------------|---------|
| 22   | `Ceiling-PWR`   | `defer` |

`compile_only_safe: false`. Mains-voltage `COMPLIANCE-001` (UK / EU
assessment at
[`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md))
is not cleared. The
`PACKAGE-POWER-400-001` / `PRODUCT-POWER-400-001` /
`WEBFLASH-POWER-400-001` / `RELEASE-POWER-400-001` chain is in
docs-only deferral state. The `S360-400` row in
[`config/hardware-catalog.json`](../config/hardware-catalog.json)
stays `schematic_status: cataloged_unverified` and is asserted
unverified by
`tests/test_hardware_catalog.py::EXPECTED_STILL_UNVERIFIED_SKUS`.

The three-way `HLK-PM01 or similar` / `HLK-5M05` / `HLK-10M05`
AC/DC part-identity disagreement remains BOM-bound.

**Do not** add any PWR-bearing compile-only target until
`COMPLIANCE-001` closes and the `PACKAGE-POWER-400-001` implementation
slice lands. This deferral covers every PWR-bearing `config_string`
in the matrix, not just the representative row.

### Lane 6 — FanRelay (rank 23) — `defer` / `blocked-package` + `blocked-core-bus`

Representative deferral row for the entire **36-row** FanRelay lane.

| Rank | `config_string`        | Status  |
|------|------------------------|---------|
| 23   | `Ceiling-POE-FanRelay` | `defer` |

`compile_only_safe: false`. FanRelay (`S360-310`) is blocked by:

- **PACKAGE-RELAY-001** — deferred until `CORE-ABSTRACT-BUS-001A` +
  `S360-100-BENCH-001` silkscreen + `K1` BOM + harness evidence land;
- **CORE-ABSTRACT-BUS-001A** (`relay_pin -> GPIO3` rebind) — itself
  blocked on **CORE-ABSTRACT-BUS-001C** to free `GPIO3` (the
  schematic-correct `relay_pin: GPIO3` collides with the existing
  `comfort_ceiling_als_int_pin: GPIO3` that Release-One consumes via
  `packages/expansions/comfort_ceiling.yaml`);
- ESP32-S3 `GPIO3` strap-pin boot-behaviour bench characterisation
  against a populated `S360-310-R4` + `S360-100-R4` pair;
- `tests/test_core_abstract_bus.py` pin-pinning scaffold.

Adding a compile-only FanRelay target before all of those land would
either pin schematic-conflicting pin values or pre-commit an undecided
rebind. The blockers list on this candidate carries both
`PACKAGE-RELAY-001-deferred` and `CORE-ABSTRACT-BUS-001A-not-landed` /
`CORE-ABSTRACT-BUS-001C-not-landed` so the
`blocked-package` and `blocked-core-bus` evidence is captured.

### Lane 7 — FanPWM (rank 24) — `defer` / `blocked-core-bus`

Representative deferral row for the entire **36-row** FanPWM lane.

| Rank | `config_string`      | Status  |
|------|----------------------|---------|
| 24   | `Ceiling-POE-FanPWM` | `defer` |

`compile_only_safe: false`. FanPWM (`S360-311`) is blocked by:

- **PACKAGE-PWM-001** — own evidence gates open;
- **CORE-ABSTRACT-BUS-001B** — canonical I²C / expansion-GPIO bus-id
  consolidation not yet implemented. `packages/expansions/fan_pwm.yaml`
  binds `fan_pwm_pin: ${expansion_gpio1}` and
  `fan_tach_pin: ${expansion_gpio2}`, both of which depend on the
  unresolved `expansion_gpio*` abstraction.

Adding a compile-only FanPWM target would pin currently-undefined or
undecided pin values. The blockers list carries
`CORE-ABSTRACT-BUS-001B-not-landed` to capture the `blocked-core-bus`
evidence.

### Lane 8 — FanDAC (rank 25) — `defer` / `blocked-core-bus`

Representative deferral row for the **24-row** FanDAC lane. FanDAC +
AirIQ is forbidden by the grammar (12 rows excluded from the matrix),
so this lane carries 24 rows rather than 36.

| Rank | `config_string`      | Status  |
|------|----------------------|---------|
| 25   | `Ceiling-POE-FanDAC` | `defer` |

`compile_only_safe: false` **at the lane level**. `PACKAGE-DAC-001`
(PR #573) implemented the package and `CORE-ABSTRACT-BUS-001B` landed
the `core_i2c` bus the GP8403 I²C peripheral binds, and
**`FW-COMPILE-DAC-001`** (this PR) added a **single** compile-only
validation target for `Ceiling-POE-FanDAC`
(`products/compile-only/ceiling-poe-fandac.yaml`, now listed in
`currently_compile_only_config_strings`) and fixed the gp8403
`voltage:` substitutions `0-10V` → `10V`. The broader **24-row** FanDAC
lane nonetheless stays `defer` / `compile_only_safe: false`:

- **PRODUCT-DAC-001** — not landed; no FanDAC product YAML exists.
- **PACKAGE-DAC-001** — implemented at the package layer only (PR #573);
  no product-layer slice.
- **S360-312 BOM evidence** — still missing.

A single compile-only validation target is **not** lane-wide
compile-only readiness; the candidate row's blockers carry a
`PACKAGE-DAC-001` substring and a `CORE-ABSTRACT-BUS-001B` substring to
capture the `blocked-package` / `blocked-core-bus` history.

### Lane 9 — FanTRIAC (rank 26) — `defer` / `blocked-hardware` + `blocked-compliance`

Representative deferral row for the entire **36-row** FanTRIAC lane.

| Rank | `config_string`        | Status  |
|------|------------------------|---------|
| 26   | `Ceiling-POE-FanTRIAC` | `defer` |

`compile_only_safe: false`. FanTRIAC (`S360-320`) is blocked by:

- **HW-005** — not cleared;
- **HW-PINMAP-320-FOLLOWUP** — not landed;
- **PACKAGE-TRIAC-001** — not landed;
- **COMPLIANCE-001** — TRIAC switches a mains-voltage load.

Adding any FanTRIAC compile-only target would imply mains-voltage /
TRIAC compile confidence that hardware and compliance evidence has
not granted. **Do not** add any FanTRIAC compile-only target until
`HW-005` / `PACKAGE-TRIAC-001` / `COMPLIANCE-001` all close. This
deferral covers every FanTRIAC-bearing `config_string` in the
matrix, not just the representative row.

## Lane ranking invariant

The non-blocked lanes (`poe-non-fan`, `poe-non-fan-led`, `usb-non-fan`,
`usb-non-fan-led`) are ranked **strictly ahead** of the blocked lanes
(`pwr`, `fanrelay`, `fanpwm`, `fandac`, `fantriac`):

```
max(rank in non-blocked lanes)  <  min(rank in blocked lanes)
```

The test
[`tests/test_compile_expansion_candidates.py`](../tests/test_compile_expansion_candidates.py)
pins this invariant. Re-ordering the list to put a blocked-lane
candidate ahead of a non-blocked-lane candidate fails the test.

## Hard guardrails

This PR (and any future candidate-ledger PR) does **not** change:

- [`config/compile-only-targets.json`](../config/compile-only-targets.json),
- [`config/webflash-builds.json`](../config/webflash-builds.json),
- [`config/product-catalog.json`](../config/product-catalog.json),
- [`config/hardware-catalog.json`](../config/hardware-catalog.json),
- [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json),
- [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json),
- `products/**`,
- `products/webflash/**`,
- `packages/**`,
- `firmware/**`,
- `manifest.json`,
- `firmware/sources.json`,
- `.github/workflows/**`,
- release artifacts,
- checksums,
- build-info manifests.

This PR (and any future candidate-ledger PR) does **not**:

- add compile-only targets,
- add product YAMLs,
- add WebFlash wrappers,
- add `webflash_build_matrix: true` to any product,
- add `artifact_name` to any product,
- upload firmware binaries,
- promote LED to stable,
- claim hardware proof exists,
- claim WebFlash import readiness,
- claim `RELEASE-007` is unblocked.

The candidate ledger is **planning input** for future compile-only
slices, not a substitute for the per-slice evidence and review that
each compile-only / product / WebFlash / release PR still owes.

## Running the tests

```sh
python3 tests/test_compile_expansion_candidates.py
```

or via `unittest` discovery:

```sh
python3 -m unittest discover -s tests -p "test_*.py"
```

The full local validation sweep recommended on candidate-ledger
changes is:

```sh
python3 scripts/generate_firmware_matrix.py --check
python3 scripts/report_firmware_build_gaps.py --check
python3 scripts/validate_compile_targets.py --metadata-only
python3 tests/test_compile_targets.py
python3 tests/test_firmware_combination_matrix.py
python3 tests/test_firmware_build_gap_report.py
python3 tests/test_kit_intent_matrix.py
python3 tests/test_compile_expansion_candidates.py
python3 -m unittest discover -s tests -p "test_*.py"
```

## See also

- [`config/compile-only-candidates.json`](../config/compile-only-candidates.json) — FW-COMPILE-EXPAND-001, the machine-readable candidate ledger.
- [`tests/test_compile_expansion_candidates.py`](../tests/test_compile_expansion_candidates.py) — FW-COMPILE-EXPAND-001 tests.
- [`docs/compile-only-firmware-validation.md`](compile-only-firmware-validation.md) — FW-COMPILE-MATRIX-001 / FW-COMPILE-RESULT-001 / FW-COMPILE-POE-NONFAN-001, the source-of-truth compile-only lane.
- [`config/compile-only-targets.json`](../config/compile-only-targets.json) — the actual compile-only target list.
- [`docs/firmware-combination-matrix.md`](firmware-combination-matrix.md) — FW-MATRIX-001, the 168-row source matrix.
- [`docs/firmware-build-gap-report.md`](firmware-build-gap-report.md) — FW-MATRIX-002, the priority-lane lens this ledger ranks against.
- [`docs/kit-intent-matrix.md`](kit-intent-matrix.md) — KIT-MATRIX-001, the productized kit-intent layer.
- [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md) — the 17-row stable-promotion gauntlet.
- [`docs/webflash-contract.md`](webflash-contract.md) — canonical config-string grammar.

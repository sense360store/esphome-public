# Firmware Build Gap Report (FW-MATRIX-002)

## Purpose and scope

This document is the **generated build-gap report** over the 168-row firmware combination readiness matrix produced by [`scripts/generate_firmware_matrix.py`](../scripts/generate_firmware_matrix.py). It groups every valid WebFlash-style combination into a practical implementation lane so future PRs can pick build / package / product work in priority order rather than randomly.

The report is **planning / reporting only**. It does **not**:

- build firmware,
- create release artifacts,
- expose new WebFlash builds,
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
  [`config/hardware-catalog.json`](../config/hardware-catalog.json), or
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
- change `products/**`, `products/webflash/**`, `packages/**`,
  `firmware/**`, `manifest.json`, `firmware/sources.json`,
  `.github/workflows/**`, release artifacts, checksums, or
  build-info manifests,
- change `REQUIRED_CONFIGS`.

## How the report is generated

The script [`scripts/report_firmware_build_gaps.py`](../scripts/report_firmware_build_gaps.py) reads [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json), applies a fixed ordered list of lane predicates, and writes this Markdown report. The first lane whose predicate matches a row wins; the final `missing-product-yaml` lane is an unconditional catch-all sentinel.

```sh
python3 scripts/report_firmware_build_gaps.py            # regenerate
python3 scripts/report_firmware_build_gaps.py --check    # CI-style freshness check
```

## Source matrix totals

- Total valid combinations: **168**
- `blocked-hardware`: 36
- `missing-product-yaml`: 130
- `webflash-preview`: 1
- `webflash-shipping`: 1

## Currently committed WebFlash builds

These are the only combinations in [`config/webflash-builds.json`](../config/webflash-builds.json) today. No build, wrapper, artifact, or release is added by this report.

- `Ceiling-POE-VentIQ-RoomIQ`
- `Ceiling-POE-VentIQ-RoomIQ-LED`

## Lane summary

| Lane | Rows | Compile-only safe now? | WebFlash exposure allowed now? | Stable-ready now? |
|------|-----:|------------------------|--------------------------------|--------------------|
| `current-webflash` | 2 | no | yes | no |
| `fantriac-blocked-hardware-compliance` | 36 | no | no | no |
| `fanrelay-blocked-package-or-core-bus` | 36 | no | no | no |
| `fanpwm-blocked-package-or-core-bus` | 36 | no | no | no |
| `fandac-blocked-package-or-core-bus` | 24 | no | no | no |
| `pwr-blocked-compliance` | 12 | no | no | no |
| `led-preview-and-stable-candidates` | 11 | no | no | no |
| `poe-non-fan-candidates` | 5 | no | no | no |
| `usb-non-fan-candidates` | 6 | no | no | no |
| `missing-product-yaml` | 0 | no | no | no |

All 168 lane-assigned rows must equal the 168 matrix combinations. The test [`tests/test_firmware_build_gap_report.py`](../tests/test_firmware_build_gap_report.py) pins this invariant.

## Lanes

### `current-webflash` — Current WebFlash builds (2 rows)

- **Compile-only coverage safe now:** no
- **WebFlash exposure allowed now:** yes
- **Stable-ready now:** no

**Blocker summary.** None for these two rows specifically — they are the only combinations committed to `config/webflash-builds.json`. Release-One stable (`Ceiling-POE-VentIQ-RoomIQ`) and the LED preview (`Ceiling-POE-VentIQ-RoomIQ-LED`).

**Recommended next PR type.** No new build PR for these two rows. Preserve both committed entries verbatim. Promotion of the LED preview to stable requires the full 17-row gauntlet in `docs/preview-to-stable-promotion-gates.md`, including `S360-300-BENCH-001` bench evidence and the WebFlash operator-proof container `WF-HW-TEST-001`.

**Notes.** `Ceiling-POE-VentIQ-RoomIQ` is the only `stable`-channel build; `Ceiling-POE-VentIQ-RoomIQ-LED` is `preview` only. Stable LED promotion remains blocked by S360-300-BENCH-001 Open Questions (harness rail, LED count, harness identity) and the WebFlash operator-proof container `WF-HW-TEST-001`.

**Representative config strings.**

- `Ceiling-POE-VentIQ-RoomIQ`
- `Ceiling-POE-VentIQ-RoomIQ-LED`

### `fantriac-blocked-hardware-compliance` — FanTRIAC — blocked on hardware + compliance (36 rows)

- **Compile-only coverage safe now:** no
- **WebFlash exposure allowed now:** no
- **Stable-ready now:** no

**Blocker summary.** FanTRIAC (S360-320) blocked under **HW-005**: S360-320 schematic is uncommitted; placeholder GPIO5 / GPIO6 collide with RoomIQ J10 nets; ESPHome `ac_dimmer` cannot run across the SX1509 expander. Also blocked under **HW-PINMAP-320-FOLLOWUP** (audit partial), **PACKAGE-TRIAC-001** (package deferred), and **COMPLIANCE-001** (mains-voltage advanced / manual-warning sign-off open).

**Recommended next PR type.** No FanTRIAC build, package, or product PR. The catalog entry for `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked` / `blocker: HW-005`. Subsequent PRs are evidence-pass investigations only until HW-005 + COMPLIANCE-001 close. See `docs/release-one-hardware-audit.md#fantriac-mapping-resolution`.

**Notes.** All 36 FanTRIAC rows inherit the same HW-005 blocker via the token-level inference in `scripts/generate_firmware_matrix.py`. Mains-voltage handling means FanTRIAC additionally needs compliance sign-off before any preview-class WebFlash exposure can even be considered.

**Representative config strings.**

- `Ceiling-POE-AirIQ-FanTRIAC`
- `Ceiling-POE-AirIQ-FanTRIAC-LED`
- `Ceiling-POE-AirIQ-FanTRIAC-RoomIQ`
- `Ceiling-POE-AirIQ-FanTRIAC-RoomIQ-LED`
- `Ceiling-POE-FanTRIAC`
- … and 31 more (see `config/firmware-combination-matrix.json` for the full list)

### `fanrelay-blocked-package-or-core-bus` — FanRelay — blocked on package + Core abstract bus (36 rows)

- **Compile-only coverage safe now:** no
- **WebFlash exposure allowed now:** no
- **Stable-ready now:** no

**Blocker summary.** FanRelay (S360-310) blocked behind **PACKAGE-RELAY-001** (deferred) and **CORE-ABSTRACT-BUS-001A** (which is itself blocked behind **CORE-ABSTRACT-BUS-001C** due to a `GPIO3` collision). Still owed: silkscreen / harness / `K1` BOM evidence for `S360-310`; ESP32-S3 `GPIO3` strap-pin boot-behaviour bench characterisation; `S360-100-BENCH-001`; a `tests/test_core_abstract_bus.py` pin-pinning scaffold.

**Recommended next PR type.** No FanRelay build or product PR. Implementation chain is **CORE-ABSTRACT-BUS-001C → CORE-ABSTRACT-BUS-001A → PACKAGE-RELAY-001 → PRODUCT-RELAY-001 → WEBFLASH-RELAY-001 → RELEASE-RELAY-001**. Stay on docs-only investigation passes until 001A lands together with the listed evidence.

**Notes.** `packages/expansions/fan_relay.yaml` cannot be safely edited until CORE-ABSTRACT-BUS-001A frees `GPIO3` and the bench / silkscreen / BOM evidence lands. Compile-only coverage is **not** safe yet because the abstract-bus rebind would change the consumed substitution names.

**Representative config strings.**

- `Ceiling-POE-AirIQ-FanRelay`
- `Ceiling-POE-AirIQ-FanRelay-LED`
- `Ceiling-POE-AirIQ-FanRelay-RoomIQ`
- `Ceiling-POE-AirIQ-FanRelay-RoomIQ-LED`
- `Ceiling-POE-FanRelay`
- … and 31 more (see `config/firmware-combination-matrix.json` for the full list)

### `fanpwm-blocked-package-or-core-bus` — FanPWM — blocked on package + Core abstract bus (36 rows)

- **Compile-only coverage safe now:** no
- **WebFlash exposure allowed now:** no
- **Stable-ready now:** no

**Blocker summary.** FanPWM (S360-311) blocked behind **PACKAGE-PWM-001** (deferred) and **CORE-ABSTRACT-BUS-001B** (canonical I²C bus-id consolidation). Still owed: BOM evidence (`HW-BOM-ASSETS-S360-311`); further `HW-PINMAP-311-FOLLOWUP` evidence; `tests/test_core_abstract_bus.py` pin-pinning scaffold; canonical I²C bus-id decision.

**Recommended next PR type.** No FanPWM build or product PR. Implementation chain is **CORE-ABSTRACT-BUS-001B → PACKAGE-PWM-001 → PRODUCT-PWM-001 → WEBFLASH-PWM-001 → RELEASE-PWM-001**. Stay on docs-only investigation passes until 001B lands.

**Notes.** `packages/expansions/fan_pwm.yaml` consumes `expansion_gpio1` / `expansion_gpio2`, so the abstract-bus rebind in 001B / 001C must complete before any product-level edits are safe.

**Representative config strings.**

- `Ceiling-POE-AirIQ-FanPWM`
- `Ceiling-POE-AirIQ-FanPWM-LED`
- `Ceiling-POE-AirIQ-FanPWM-RoomIQ`
- `Ceiling-POE-AirIQ-FanPWM-RoomIQ-LED`
- `Ceiling-POE-FanPWM`
- … and 31 more (see `config/firmware-combination-matrix.json` for the full list)

### `fandac-blocked-package-or-core-bus` — FanDAC — blocked on package + Core abstract bus (24 rows)

- **Compile-only coverage safe now:** no
- **WebFlash exposure allowed now:** no
- **Stable-ready now:** no

**Blocker summary.** FanDAC (S360-312) blocked behind **PACKAGE-DAC-001** (deferred) and **CORE-ABSTRACT-BUS-001B** (canonical I²C bus-id consolidation; the GP8403 DAC is an I²C peripheral). Still owed: BOM evidence (`HW-BOM-ASSETS-S360-312`); further `HW-PINMAP-312-FOLLOWUP` evidence; `tests/test_core_abstract_bus.py` pin-pinning scaffold. FanDAC + AirIQ is forbidden by the grammar (12 rows excluded from the matrix), so this lane carries 24 rows.

**Recommended next PR type.** No FanDAC build or product PR. Implementation chain is **CORE-ABSTRACT-BUS-001B → PACKAGE-DAC-001 → PRODUCT-DAC-001 → WEBFLASH-DAC-001 → RELEASE-DAC-001**. Stay on docs-only investigation passes until 001B lands.

**Notes.** `packages/expansions/fan_gp8403.yaml` consumes the to-be-consolidated I²C bus-id. Compile-only coverage cannot be added safely before the canonical bus-id is chosen.

**Representative config strings.**

- `Ceiling-POE-FanDAC`
- `Ceiling-POE-FanDAC-LED`
- `Ceiling-POE-FanDAC-RoomIQ`
- `Ceiling-POE-FanDAC-RoomIQ-LED`
- `Ceiling-POE-VentIQ-FanDAC`
- … and 19 more (see `config/firmware-combination-matrix.json` for the full list)

### `pwr-blocked-compliance` — PWR-240V — blocked on compliance (12 rows)

- **Compile-only coverage safe now:** no
- **WebFlash exposure allowed now:** no
- **Stable-ready now:** no

**Blocker summary.** PWR-240V (S360-400) blocked under **COMPLIANCE-001** (mains-voltage UK / EU advanced / manual-warning sign-off open) and behind **PACKAGE-POWER-400-001** / **PRODUCT-POWER-400-001** / **WEBFLASH-POWER-400-001** / **RELEASE-POWER-400-001**. `S360-400` is `schematic_status: cataloged_unverified` (HW-PINMAP-400-FOLLOWUP partial; the schematic PDF's `PS1 = HLK-10M05` value-field discrepancy still unresolved).

**Recommended next PR type.** No PWR build, package, or product PR. Subsequent PRs are docs-only investigation passes until COMPLIANCE-001 closes and `S360-400` is `schematic_status: verified`. WebFlash exposure for mains-voltage power is **not** allowed under any channel without a qualified electrical-safety review.

**Notes.** PWR-240V touches mains voltage. Documentation alone is not sufficient to clear compliance; a qualified electrical-safety / compliance review recorded outside this repo is required.

**Representative config strings.**

- `Ceiling-PWR`
- `Ceiling-PWR-AirIQ`
- `Ceiling-PWR-AirIQ-LED`
- `Ceiling-PWR-AirIQ-RoomIQ`
- `Ceiling-PWR-AirIQ-RoomIQ-LED`
- … and 7 more (see `config/firmware-combination-matrix.json` for the full list)

### `led-preview-and-stable-candidates` — LED preview / stable candidates (non-fan, non-PWR) (11 rows)

- **Compile-only coverage safe now:** no
- **WebFlash exposure allowed now:** no
- **Stable-ready now:** no

**Blocker summary.** LED-bearing combinations on POE / USB power that are not yet in `config/webflash-builds.json`. Blocked from preview exposure by missing product YAML, missing WebFlash wrapper, and missing catalog entries. Blocked from **stable** promotion by `S360-300-BENCH-001` (harness rail, LED count, harness identity Open Questions remain `verify`) and the WebFlash operator-proof container `WF-HW-TEST-001` (not yet filled).

**Recommended next PR type.** No LED build PR for these rows. Compile-only coverage may become safe **after** the per-power product family (POE-410 / USB-power) clears its own gates; until then keep LED candidates as docs-only readiness rows. Stable promotion of *any* LED build requires S360-300-BENCH-001 to close and `WF-HW-TEST-001` to be filled — neither has happened yet.

**Notes.** `S360-300` is `schematic_status: verified` (HW-007 / HW-008), but stable readiness requires bench evidence and an operator-flash proof in addition to package + product + wrapper + build + release proof for the **specific** config string.

**Representative config strings.**

- `Ceiling-POE-AirIQ-LED`
- `Ceiling-POE-AirIQ-RoomIQ-LED`
- `Ceiling-POE-LED`
- `Ceiling-POE-RoomIQ-LED`
- `Ceiling-POE-VentIQ-LED`
- … and 6 more (see `config/firmware-combination-matrix.json` for the full list)

### `poe-non-fan-candidates` — POE non-fan candidates (5 rows)

- **Compile-only coverage safe now:** no
- **WebFlash exposure allowed now:** no
- **Stable-ready now:** no

**Blocker summary.** POE (S360-410) candidates without a fan and without LED, excluding `Ceiling-POE-VentIQ-RoomIQ` (already shipping). `S360-410` is `schematic_status: cataloged_unverified` (HW-PINMAP-410-FOLLOWUP partial). **PACKAGE-POE-410-001** / **PRODUCT-POE-410-001** / **WEBFLASH-POE-410-001** / **RELEASE-POE-410-001** all blocked behind BOM cross-check, `schematic_status: verified` JSON PR, HW-002 OQ#6, `S360-100-BENCH-001` J2-harness identity closure, Release-One PoE caveat closure, product-onboarding approval.

**Recommended next PR type.** No POE non-fan product or build PR for these rows. They are documented as readiness-tracking placeholders; the catalog carries no product YAML for them today. Wait for the PACKAGE/PRODUCT/WEBFLASH/RELEASE-POE-410-001 chain to complete before any compile-only or preview-class work.

**Notes.** These rows are valid grammar combinations but have no product YAML in `config/product-catalog.json` and no entry in `config/webflash-builds.json`. They are tracking entries only, not requests to add a product.

**Representative config strings.**

- `Ceiling-POE`
- `Ceiling-POE-AirIQ`
- `Ceiling-POE-AirIQ-RoomIQ`
- `Ceiling-POE-RoomIQ`
- `Ceiling-POE-VentIQ`

### `usb-non-fan-candidates` — USB non-fan candidates (6 rows)

- **Compile-only coverage safe now:** no
- **WebFlash exposure allowed now:** no
- **Stable-ready now:** no

**Blocker summary.** USB-powered candidates without a fan and without LED. The catalog has no S360-* USB PSU board entry and no S360-* USB product family. USB on `S360-100` is debug-only per the catalog. No `PACKAGE-USB-*` / `PRODUCT-USB-*` / `WEBFLASH-USB-*` / `RELEASE-USB-*` chain has been opened.

**Recommended next PR type.** No USB product or build PR. USB-family product onboarding has not been opened; readiness-tracking only until a deliberate USB-family scope decision is recorded. Compile-only coverage cannot bypass the missing PSU / harness / catalog evidence.

**Notes.** Until a USB-family scope decision is documented, these rows are tracking entries only. No compile-only build or product YAML is added by this report.

**Representative config strings.**

- `Ceiling-USB`
- `Ceiling-USB-AirIQ`
- `Ceiling-USB-AirIQ-RoomIQ`
- `Ceiling-USB-RoomIQ`
- `Ceiling-USB-VentIQ`
- … and 1 more (see `config/firmware-combination-matrix.json` for the full list)

### `missing-product-yaml` — Missing-product-yaml (sentinel) (0 rows)

- **Compile-only coverage safe now:** no
- **WebFlash exposure allowed now:** no
- **Stable-ready now:** no

**Blocker summary.** Sentinel lane for rows that do not match any specific lane above. With the current matrix and lane policies this lane is empty; it is retained so any future grammar drift (`config/webflash-compatibility.json`) or new combination shape is forced into an explicit lane by an explicit follow-up PR rather than silently disappearing.

**Recommended next PR type.** If this lane is non-empty in a future run, open a follow-up PR to extend the lane policies in `scripts/report_firmware_build_gaps.py`. Do not promote any row to a more permissive lane without explicit evidence.

**Notes.** An empty sentinel lane is the expected steady state; a non-empty value indicates either matrix grammar drift or a stale lane policy.

**Representative config strings.** (none — lane is empty.)

## Coverage

All 168 matrix rows are accounted for by exactly one lane. Subtotals:

- `current-webflash`: 2
- `fantriac-blocked-hardware-compliance`: 36
- `fanrelay-blocked-package-or-core-bus`: 36
- `fanpwm-blocked-package-or-core-bus`: 36
- `fandac-blocked-package-or-core-bus`: 24
- `pwr-blocked-compliance`: 12
- `led-preview-and-stable-candidates`: 11
- `poe-non-fan-candidates`: 5
- `usb-non-fan-candidates`: 6
- `missing-product-yaml`: 0

Sum: **168**.

## Guardrails

- No lane in this report claims WebFlash exposure is allowed unless every row in the lane is already committed to [`config/webflash-builds.json`](../config/webflash-builds.json). The test [`tests/test_firmware_build_gap_report.py`](../tests/test_firmware_build_gap_report.py) enforces this.
- No lane is marked stable-ready. The LED candidate lane explicitly requires `S360-300-BENCH-001` to close and the WebFlash operator-proof container `WF-HW-TEST-001` to be filled.
- The FanTRIAC lane references **HW-005** verbatim. The PWR lane references **COMPLIANCE-001** verbatim. Removing those references is a deliberate evidence-pass PR, not a side-effect of this report.
- The `missing-product-yaml` lane is a sentinel: it should be empty under steady-state. A non-empty value indicates matrix grammar drift or stale lane policies and requires a follow-up PR to extend [`scripts/report_firmware_build_gaps.py`](../scripts/report_firmware_build_gaps.py).

## See also

- [`docs/firmware-combination-matrix.md`](firmware-combination-matrix.md) — FW-MATRIX-001, the source matrix this report consumes.
- [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md) — the 17-row stable-promotion gauntlet that LED candidates must clear.
- [`docs/product-readiness-matrix.md`](product-readiness-matrix.md) — PRODUCT-GAP-001, product-layer readiness.
- [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md) — WEBFLASH-GAP-001, WebFlash-exposure readiness.
- [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md) — RELEASE-GAP-001, release-artifact readiness.
- [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md) — PACKAGE-GAP-001, package-layer readiness.
- [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md) — Release-One hardware audit (HW-005 source-of-truth).

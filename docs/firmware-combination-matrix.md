# Firmware Combination Readiness Matrix (FW-MATRIX-001)

## Purpose and scope

This document explains the **generated firmware combination readiness
matrix** at [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json),
the generator script at [`scripts/generate_firmware_matrix.py`](../scripts/generate_firmware_matrix.py),
and the tests at [`tests/test_firmware_combination_matrix.py`](../tests/test_firmware_combination_matrix.py).

The matrix enumerates every valid WebFlash-style firmware combination
allowed by the canonical grammar in
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
then classifies each combination against
[`config/product-catalog.json`](../config/product-catalog.json) and
[`config/webflash-builds.json`](../config/webflash-builds.json). It is
**readiness tracking**, not WebFlash exposure.

This document and the artefacts it describes do **not**:

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
  [`config/product-catalog.json`](../config/product-catalog.json), or
  [`config/hardware-catalog.json`](../config/hardware-catalog.json),
- change `products/**`, `products/webflash/**`, `packages/**`,
  `firmware/**`, `manifest.json`, `firmware/sources.json`,
  `.github/workflows/**`, release artifacts, checksums, or build-info
  manifests,
- change `REQUIRED_CONFIGS`.

## What "readiness tracking" means

The matrix is the answer to the question *"what valid WebFlash-style
config strings exist, and which of them does this repo currently know
how to build / ship / not ship?"*. It is a generated audit, not a
promotion mechanism:

- **`webflash-shipping`** does not mean "shippable now"; it means
  *"this combination is currently committed to [`config/webflash-builds.json`](../config/webflash-builds.json)
  on the stable channel and is therefore the current
  Release-One target"*. Today that is exactly
  `Ceiling-POE-VentIQ-RoomIQ`.
- **`webflash-preview`** does not mean "promoted" or "stable"; it
  means *"this combination is in [`config/webflash-builds.json`](../config/webflash-builds.json)
  on a non-stable channel (preview / beta / dev / rescue)"*. Today
  that is exactly `Ceiling-POE-VentIQ-RoomIQ-LED` (preview). Preview
  is **not** `REQUIRED_CONFIGS` and stable promotion still requires
  the hardware-evidence, bench-verification, and release gates
  documented in [`docs/preview-to-stable-promotion-gates.md` (archived)](archive-index.md).
- **`compile-only-candidate`** does not mean shippable. It means the
  product catalog records a `compile-only` status; firmware may build,
  but the product is not WebFlash-eligible.
- **`missing-product-yaml`** means the combination is valid grammar
  but no product YAML exists for it in
  [`config/product-catalog.json`](../config/product-catalog.json) and
  no build entry exists in
  [`config/webflash-builds.json`](../config/webflash-builds.json). It
  is a tracking entry, not a request to add a product.
- **`blocked-hardware`** / **`blocked-compliance`** / **`blocked-package`**
  classify combinations that currently fail one of the
  hardware-evidence, compliance, or package-readiness gates. They
  carry the `blockers` list from the source-of-truth audit (for
  example `HW-005` for FanTRIAC; see
  [`docs/release-one-hardware-audit.md#fantriac-mapping-resolution` (archived)](archive-index.md)).
- **`invalid-by-grammar`** is reserved for future drift detection; the
  generator never emits combinations that violate the grammar in
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
  so this status currently does not appear in the matrix.

WebFlash import (the side that actually exposes a build to end users)
happens **separately** in the [WebFlash repo](https://github.com/sense360store/WebFlash);
nothing in this matrix imports a build to WebFlash, alters
[`config/webflash-builds.json`](../config/webflash-builds.json), or
claims a build is import-ready.

## Generation

```sh
python3 scripts/generate_firmware_matrix.py            # regenerate
python3 scripts/generate_firmware_matrix.py --check    # CI-style freshness check
```

The generator reads:

| Input                                                                                    | Role                                                  |
|------------------------------------------------------------------------------------------|-------------------------------------------------------|
| [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)             | Canonical grammar (mounting / power / modules / rules) |
| [`config/webflash-builds.json`](../config/webflash-builds.json)                            | Committed WebFlash builds (stable + non-stable channels) |
| [`config/product-catalog.json`](../config/product-catalog.json)                            | Lifecycle layer (production / preview / blocked / etc.) |

The generator never **writes** to those files. The only file it writes
is [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json).

## Grammar

Per [`docs/webflash-contract.md`](webflash-contract.md) §2 and §5, the
canonical config-string grammar is:

```text
{Mounting}-{Power}-[AirIQ|VentIQ]-[FanRelay|FanPWM|FanDAC|FanTRIAC]-[RoomIQ]-[LED]
```

The generator enumerates the cross-product of:

| Slot         | Choices                                                    |
|--------------|------------------------------------------------------------|
| Mounting     | `Ceiling` (only mounting in scope for Release-One)         |
| Power        | `USB`, `POE`, `PWR`                                        |
| Air quality  | (none), `AirIQ`, `VentIQ` (mutually exclusive — single slot) |
| Fan driver   | (none), `FanRelay`, `FanPWM`, `FanDAC`, `FanTRIAC` (single slot) |
| Room sense   | (none), `RoomIQ`                                           |
| LED          | (absent), `LED`                                            |

and applies the following grammar rules from
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json):

- `AirIQ` and `VentIQ` are mutually exclusive (enforced structurally by
  using a single air-quality slot).
- `FanDAC` conflicts with `AirIQ` (`FanDAC` + `AirIQ` combinations are
  dropped during enumeration).
- Only one fan-driver token may appear (enforced structurally by using a
  single fan slot).
- Generic `Fan` token is forbidden (never emitted).
- Legacy tokens `Bathroom`, `Comfort`, `Presence`, `Fan`, `FanAnalog`
  are forbidden (never emitted; pinned by
  [`tests/test_firmware_combination_matrix.py`](../tests/test_firmware_combination_matrix.py)
  against `forbidden_tokens` in
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)).

The total enumeration is **168 valid combinations**:

```text
1 × 3 × 3 × 5 × 2 × 2  raw combinations   = 180
−  1 × 3 × 1 × 1 × 2 × 2  AirIQ + FanDAC   = −12
=                                            168
```

## Per-row schema

Each row in the `combinations` array carries the following fields:

| Field              | Meaning                                                                       |
|--------------------|-------------------------------------------------------------------------------|
| `config_string`    | Canonical hyphen-joined config string, exactly as it would appear in WebFlash. |
| `tokens`           | Ordered token list (mounting, power, modules…).                                |
| `mounting`         | The mounting token (`Ceiling`).                                                |
| `power`            | The power token (`USB` / `POE` / `PWR`).                                        |
| `air_quality`      | One of `none`, `AirIQ`, `VentIQ`.                                              |
| `room_sense`       | One of `none`, `RoomIQ`.                                                       |
| `fan`              | One of `none`, `FanRelay`, `FanPWM`, `FanDAC`, `FanTRIAC`.                       |
| `led`              | One of `none`, `LED`.                                                          |
| `status`           | One of the statuses below.                                                     |
| `product_yaml`     | Path to the product YAML if the catalog records one. Optional.                 |
| `webflash_wrapper` | Path to the WebFlash wrapper YAML if the catalog records one. Optional.        |
| `artifact_name`    | Artifact name for `webflash-shipping` / `webflash-preview` rows. Optional.     |
| `blockers`         | List of blocker tokens (e.g. `HW-005`). Optional.                              |
| `notes`            | Human-readable note carried from the catalog or generator. Optional.           |

## Statuses

| Status                          | Meaning                                                                                                                                                          |
|---------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `webflash-shipping`             | In [`config/webflash-builds.json`](../config/webflash-builds.json) on the `stable` channel. Today: `Ceiling-POE-VentIQ-RoomIQ`.                                  |
| `webflash-preview`              | In [`config/webflash-builds.json`](../config/webflash-builds.json) on a non-stable channel. Today: `Ceiling-POE-VentIQ-RoomIQ-LED` (preview).                    |
| `product-exists-not-webflash`   | Has a product YAML in [`config/product-catalog.json`](../config/product-catalog.json) but no build entry in [`config/webflash-builds.json`](../config/webflash-builds.json). |
| `compile-only-candidate`        | Catalog status `compile-only`: firmware may build, product is not WebFlash-eligible.                                                                              |
| `missing-product-yaml`          | Valid grammar combination with no product YAML and no build entry.                                                                                                |
| `blocked-hardware`              | Catalog blocker prefix `HW-*`, or token-level inference (e.g. `FanTRIAC` carries `HW-005`).                                                                       |
| `blocked-compliance`            | Catalog blocker prefix `COMPLIANCE-*` (e.g. mains-voltage advanced/manual-warning sign-off).                                                                      |
| `blocked-package`               | Catalog blocker prefix `PACKAGE-*` (e.g. package implementation deferred behind evidence).                                                                        |
| `invalid-by-grammar`            | Reserved for future drift detection; not emitted by the current generator.                                                                                        |

The generator chooses one status per row, in this priority order:

1. If the combination is in [`config/webflash-builds.json`](../config/webflash-builds.json),
   the row is `webflash-shipping` (stable) or `webflash-preview`
   (any other channel).
2. Otherwise, if the combination has a `config_string`-keyed entry in
   [`config/product-catalog.json`](../config/product-catalog.json),
   the row is classified from that entry's `status` (and `blocker`
   prefix for `status=blocked`).
3. Otherwise, if the combination contains a token that the catalog
   records as blocked elsewhere (today: `FanTRIAC` → `HW-005`), the
   row inherits that blocker as `blocked-hardware`.
4. Otherwise, the row is `missing-product-yaml`.

## Test coverage

[`tests/test_firmware_combination_matrix.py`](../tests/test_firmware_combination_matrix.py)
pins:

- the schema-version / shape / required fields,
- the count (168) and uniqueness of combinations,
- the canonical module order from
  [`docs/webflash-contract.md`](webflash-contract.md) §5,
- `Ceiling-POE-VentIQ-RoomIQ` is `webflash-shipping`,
- `Ceiling-POE-VentIQ-RoomIQ-LED` is `webflash-preview`,
- `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` is `blocked-hardware` with
  `HW-005` in `blockers`,
- every entry in [`config/webflash-builds.json`](../config/webflash-builds.json)
  appears in the matrix,
- no `AirIQ` + `VentIQ` combination is emitted,
- no `FanDAC` + `AirIQ` combination is emitted,
- no generic `Fan` token appears,
- no forbidden legacy token appears,
- every emitted config string conforms to
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
- only entries committed to
  [`config/webflash-builds.json`](../config/webflash-builds.json)
  may carry a `webflash-*` status,
- the on-disk
  [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json)
  matches a fresh regeneration (freshness gate).

Run the tests with:

```sh
python3 tests/test_firmware_combination_matrix.py
```

or via the standard validators:

```sh
python3 tests/validate_webflash_builds.py
python3 tests/test_webflash_compatibility.py
python3 tests/test_firmware_combination_matrix.py
```

## Non-goals

This matrix is intentionally narrow. It is **not**:

- a WebFlash import or runtime change — see the
  [WebFlash repository](https://github.com/sense360store/WebFlash) for
  the import side,
- a stable promotion of any preview or blocked combination — see
  [`docs/preview-to-stable-promotion-gates.md` (archived)](archive-index.md),
- a hardware-proof claim — see
  [`docs/release-one-hardware-audit.md` (archived)](archive-index.md)
  and the per-board audits under
  [`docs/hardware/`](hardware/),
- a `REQUIRED_CONFIGS` change — Release-One stays
  `["Ceiling-POE-VentIQ-RoomIQ"]` per
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
- a build-matrix expansion — Release-One stays the only stable build;
  the LED preview stays the only preview build.

Future work that depends on this matrix (e.g. surfacing per-row gating
status in CI, cross-referencing the
[`docs/product-readiness-matrix.md` (archived)](archive-index.md) and
[`docs/release-artifact-readiness-matrix.md` (archived)](archive-index.md)
gate columns) is out of scope for FW-MATRIX-001.

## See also

- [`docs/firmware-build-gap-report.md`](firmware-build-gap-report.md) —
  FW-MATRIX-002, the generated build-gap report that groups every row
  in this matrix into a practical implementation lane (
  `current-webflash`, the four fan lanes, `pwr-blocked-compliance`,
  `led-preview-and-stable-candidates`, `poe-non-fan-candidates`,
  `usb-non-fan-candidates`, and the `missing-product-yaml` sentinel).
  The build-gap report is planning / reporting only; it does not add
  builds, wrappers, artifacts, or releases, and it never marks a lane
  as WebFlash-exposable unless every row in that lane is already in
  [`config/webflash-builds.json`](../config/webflash-builds.json).

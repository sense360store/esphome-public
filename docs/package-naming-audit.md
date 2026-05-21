# Package Naming Audit (PACKAGE-NAMING-AUDIT-001)

## Purpose and scope

This document is the **audit of every YAML file under [`packages/**`](../packages/)
against the productized naming model** described in
[`docs/webflash-contract.md`](webflash-contract.md) (the WebFlash token
list — `AirIQ`, `VentIQ`, `RoomIQ`, `FanRelay`, `FanPWM`, `FanDAC`,
`FanTRIAC`, `LED` — and the deprecated/forbidden token list).

It is a **planning / audit ledger only**. It does **not** rename, move,
delete, or otherwise change any YAML file under `packages/**`,
`products/**`, `products/webflash/**`, `firmware/**`, `config/**`,
`tests/**`, `scripts/**`, `.github/workflows/**`, `components/**`, or
`include/**`. It does not change runtime YAML behavior, package
filenames, the `forbidden_tokens` snapshot in
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
or the Release-One config string `Ceiling-POE-VentIQ-RoomIQ`.

This document and the audit it captures do **not**:

- rename any file under `packages/**`,
- move any file under `packages/**`,
- delete any file under `packages/**`,
- change runtime YAML behavior,
- add compile-only targets,
- add product YAMLs,
- add WebFlash wrappers,
- add `webflash_build_matrix: true` to any product,
- add `artifact_name` to any product,
- promote `LED` to `stable`,
- promote `AirIQ` / `VentIQ` / `RoomIQ`,
- promote fan modules,
- promote `PWR` / `S360-400`,
- promote `POE` / `S360-410`,
- claim hardware proof exists,
- claim WebFlash import readiness,
- claim `RELEASE-007` is unblocked,
- change [`config/compile-only-targets.json`](../config/compile-only-targets.json),
  [`config/compile-only-candidates.json`](../config/compile-only-candidates.json),
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  [`config/product-catalog.json`](../config/product-catalog.json),
  [`config/hardware-catalog.json`](../config/hardware-catalog.json),
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
  [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json),
  or [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json),
- change `products/**`, `products/webflash/**`, `packages/**`,
  `firmware/**`, `manifest.json`, `firmware/sources.json`,
  release artifacts, checksums, build-info manifests, or
  `.github/workflows/**`,
- change `REQUIRED_CONFIGS`.

## Why this audit exists

Recent productization work in this repo established a layered model:

- **Firmware combination matrix** ([FW-MATRIX-001 / PR #539](../UPCOMING_PR.md))
  at [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json)
  enumerates the 168 valid WebFlash config strings under the
  [`docs/webflash-contract.md`](webflash-contract.md) grammar.
- **Firmware build-gap report** ([FW-MATRIX-002 / PR #540](../UPCOMING_PR.md))
  at [`docs/firmware-build-gap-report.md`](firmware-build-gap-report.md)
  partitions those 168 rows into priority lanes.
- **Kit intent matrix** ([KIT-MATRIX-001 / PR #542](../UPCOMING_PR.md))
  at [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json)
  and [`docs/kit-intent-matrix.md`](kit-intent-matrix.md) layers
  productized kit / bundle intent on top of the matrix.
- **Compile-only validation lane** ([FW-COMPILE-MATRIX-001 / PR #544](../UPCOMING_PR.md))
  at [`config/compile-only-targets.json`](../config/compile-only-targets.json)
  and [`docs/compile-only-firmware-validation.md`](compile-only-firmware-validation.md).
- **POE non-fan compile-only skeletons** (FW-COMPILE-POE-NONFAN-001).
- **Compile-only candidate ledger** ([FW-COMPILE-EXPAND-001](../UPCOMING_PR.md))
  at [`config/compile-only-candidates.json`](../config/compile-only-candidates.json)
  and [`docs/compile-only-expansion-candidates.md`](compile-only-expansion-candidates.md).

That layered model surfaced the productized identifier separation
documented in [`docs/kit-intent-matrix.md`](kit-intent-matrix.md):

| Identifier space            | Audience                | Source of truth                                                                                  |
|-----------------------------|-------------------------|--------------------------------------------------------------------------------------------------|
| **Customer-facing bundle / outcome** | End customer           | [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json)                              |
| **Module SKU**              | Inventory / support     | [`config/hardware-catalog.json`](../config/hardware-catalog.json)                                |
| **Firmware config string**  | Build / WebFlash / release | [`config/webflash-compatibility.json`](../config/webflash-compatibility.json) + [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json) + [`config/webflash-builds.json`](../config/webflash-builds.json) |
| **Package filename**        | Repo-internal           | this repo (`packages/**`)                                                                        |

Several `packages/**` filenames still reflect older terminology that
predates the productized identifier separation:

- `packages/features/airiq_basic.yaml`
- `packages/features/airiq_advanced.yaml`
- `packages/features/airiq_basic_profile.yaml`
- `packages/features/airiq_advanced_profile.yaml`
- `packages/features/bathroom_profile.yaml`
- `packages/features/bathroom_pro_profile.yaml`

Observed naming problems with the current package surface:

- **Ambiguous tier tokens.** `basic`, `advanced`, and `pro` are not
  defined anywhere as customer-visible product tiers, productized SKUs,
  or WebFlash tokens. They appear only in package filenames and product
  YAML comments.
- **Generic vs module-specific overlap.** `AirIQ` is used both as the
  productized module name for `S360-210` (the general IAQ module) and
  as a generic IAQ-feature name across packages that do not target
  `S360-210` at all (`airiq_basic_profile.yaml` is consumed by
  bathroom-focused `S360-211` / VentIQ products via
  `sense360-ceiling-poe-ventiq-roomiq.yaml`'s sibling files).
- **Behavior hidden by name.** `airiq_advanced_profile.yaml` looks like
  an IAQ feature profile but also adds an automated `fan_switch` on
  `GPIO15`, an `auto_fan_control` script, and a `5min` interval that
  reads `air_quality_state` and toggles the fan. Auto fan control
  inside an IAQ-named profile is not discoverable from the filename.
- **Legacy customer-facing tokens.** `bathroom_profile.yaml` and
  `bathroom_pro_profile.yaml` use the `bathroom` token, which
  [`docs/webflash-contract.md`](webflash-contract.md) §3 lists as
  deprecated in favor of `VentIQ`.
- **Mixed identity in expansions.** `packages/expansions/airiq_bathroom_base.yaml`
  and `packages/expansions/airiq_bathroom_pro.yaml` carry the productized
  `VentIQ` module identity (`S360-211`) under the legacy `airiq_bathroom_*`
  filename. The package-readiness-matrix and HW-009 firmware-package-mapping
  audit already cross-link this discrepancy.
- **Renaming risk.** A blind filename rename would break product YAMLs
  under `products/**` (legacy Mini-board products, legacy Core
  variants, compile-only product YAMLs, and Release-One product YAMLs
  all `!include` these package files by path), the compile-only
  expansion candidate ledger, third-party remote-package consumers,
  and any pinned-version downstream user that flashes via WebFlash or
  reads our YAML through `github://sense360store/esphome-public/...`
  URLs.

This audit therefore catalogs the current state, classifies each
package against the productized naming model, and proposes a phased
migration path that **does not** touch any package filename or any
runtime YAML in this PR.

## Reconciliation taxonomy

Every package YAML under `packages/**` is classified using one or more
of the following tags. A package may carry more than one tag (for
example, a package can be both `canonical-current` and
`candidate-for-alias` if it is the source-of-truth implementation but
its filename could be wrapped under a more product-facing alias for
future product YAMLs).

| Tag                              | Meaning                                                                                                                                                |
|----------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| `canonical-current`              | Filename matches the productized naming model and the file is the source-of-truth implementation; keep as-is.                                          |
| `acceptable-internal`            | Filename is repo-internal scaffolding (e.g. `base/`, `hardware/*core*`) that customers never see; keep as-is, no productized name required.            |
| `legacy-compatible`              | Filename is legacy / pre-productized but no current evidence of customer confusion. Retained because consumers (product YAMLs, remote-package users, generated configs) bind to the path. Treat as public-API. |
| `misleading-name`                | Filename actively misleads — implies a different product, tier, or capability than the file actually implements.                                       |
| `behavior-hidden-by-name`        | Filename describes one capability (e.g. IAQ sensors) but the file also implements another (e.g. fan control, auto-ventilation, GPIO output).           |
| `candidate-for-alias`            | A productized-name wrapper / alias package should be added later (Phase 2) so new product YAMLs can `!include` the canonical name without renaming.    |
| `candidate-for-future-rename`    | The filename should eventually be replaced with a productized name (Phase 3–5). Not done in this PR; requires consumer migration first.                |

These tags are descriptive only. They do **not** drive any change to
runtime YAML, the WebFlash build matrix, the product catalog, the
hardware catalog, the compile-only target list, the kit-intent matrix,
the firmware combination matrix, or the WebFlash compatibility
snapshot.

## Source files inspected

The audit reads from the following committed evidence. No invented
file names, no fabricated consumers.

- All 79 YAML files under [`packages/**`](../packages/) enumerated by
  `find packages -type f -name "*.yaml"` (9 under `base/`, 24 under
  `expansions/`, 24 under `features/`, 22 under `hardware/`).
- [`docs/webflash-contract.md`](webflash-contract.md) — canonical
  WebFlash token list and deprecated/forbidden token list.
- [`docs/release-one.md`](release-one.md) — Release-One slot/file/binary
  mapping.
- [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)
  — Release-One firmware-vs-schematic audit and Sense360 LED policy.
- [`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
  — HW-009 per-package schematic-vs-firmware reconciliation.
- [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
  — PACKAGE-GAP-001 per-package readiness.
- [`docs/cleanup-audit.md`](cleanup-audit.md) — repo-wide cleanup audit.
- [`docs/kit-intent-matrix.md`](kit-intent-matrix.md) — productized
  kit / bundle intent.
- [`packages/README.md`](../packages/README.md) and
  [`packages/SENSE360_MODULES.md`](../packages/SENSE360_MODULES.md) —
  legacy package surface documentation.
- Consumer cross-references found by:
  - `grep -rln "<filename>" products/ packages/`
  - `grep -rn "<filename>" docs/`

The "current known consumers" column lists only consumers under
[`products/`](../products/) and other `packages/**` files. Consumers
outside this repo (third-party Home Assistant configurations, pinned
remote-package URLs) cannot be enumerated and are treated as part of
the migration risk.

## Decision table

| Rank | Classification action                                                                                                          |
|------|--------------------------------------------------------------------------------------------------------------------------------|
| 1    | If `acceptable-internal`, leave alone.                                                                                         |
| 2    | If `canonical-current`, leave alone.                                                                                           |
| 3    | If `legacy-compatible` only, leave alone; record as public API.                                                                |
| 4    | If `misleading-name`, recommend Phase-2 alias and Phase-5 retirement; **do not rename in this PR**.                            |
| 5    | If `behavior-hidden-by-name`, recommend Phase-2 split / wrapper that names the hidden behavior; **do not change YAML in this PR**. |
| 6    | If `candidate-for-alias`, list the proposed alias filename for Phase 2.                                                        |
| 7    | If `candidate-for-future-rename`, list the proposed canonical filename for Phase 3.                                            |

## Per-area findings

For brevity, the per-file detail tables below cover only the
non-`acceptable-internal` packages. The `acceptable-internal` packages
(`packages/base/**`) are summarised separately in
[Base packages](#base-packages).

### Base packages

All files under [`packages/base/`](../packages/base/) are
**`acceptable-internal`**. They are infrastructure scaffolding (WiFi,
API encryption, OTA, time, logging, ethernet, bluetooth proxy) consumed
via `complete.yaml` / `complete_ethernet.yaml`. They do not carry a
productized identity, are not customer-visible, and do not need
productized names.

| Path                                       | Apparent purpose                                                  | Tag                    |
|--------------------------------------------|-------------------------------------------------------------------|------------------------|
| `packages/base/api_encrypted.yaml`         | ESPHome API with encryption + 15-min reboot timeout               | `acceptable-internal`  |
| `packages/base/bluetooth_proxy.yaml`       | Bluetooth proxy block for ESPHome                                 | `acceptable-internal`  |
| `packages/base/complete.yaml`              | Wraps all base packages for WiFi-connected devices                | `acceptable-internal`  |
| `packages/base/complete_ethernet.yaml`     | Wraps all base packages for Ethernet-connected devices (no WiFi)  | `acceptable-internal`  |
| `packages/base/external_components.yaml`   | External components fetch block                                   | `acceptable-internal`  |
| `packages/base/logging.yaml`               | ESPHome logger block                                              | `acceptable-internal`  |
| `packages/base/ota.yaml`                   | ESPHome OTA block                                                 | `acceptable-internal`  |
| `packages/base/time.yaml`                  | ESPHome SNTP time block                                           | `acceptable-internal`  |
| `packages/base/wifi.yaml`                  | WiFi configuration block                                          | `acceptable-internal`  |

Recommendation: keep all base packages as-is. No alias, no rename, no
behavior change.

### AirIQ packages

This is the highest-risk naming area. The `AirIQ` token is used in
three distinct ways across the package surface:

1. As the **module identity** for `S360-210` (the productized AirIQ
   IAQ module on the I²C expansion bus); used in
   `packages/expansions/airiq_ceiling.yaml`, `airiq_wall.yaml`, and
   `airiq.yaml` (Mini-board variant).
2. As a **legacy module identity** for `S360-211` (the productized
   VentIQ bathroom IAQ module) inside the legacy filenames
   `packages/expansions/airiq_bathroom_base.yaml` and
   `airiq_bathroom_pro.yaml`. The WebFlash contract treats
   `BathroomAirIQ`, `AirIQBase`, `AirIQPro`, and `AirIQProv` as
   **deprecated/forbidden** tokens that must not appear in artifact
   filenames; the schematic-backed module identity is `VentIQ` /
   `S360-211`. The filenames here are retained per
   [`docs/hardware/firmware-package-mapping-audit.md` §`VentIQ legacy package filename airiq_bathroom_base.yaml`](hardware/firmware-package-mapping-audit.md)
   as `legacy-compatible` — but the legacy naming hides the VentIQ
   identity at a glance.
3. As a **generic IAQ feature-profile token** unrelated to either
   `S360-210` or `S360-211`, in `packages/features/airiq_basic.yaml`,
   `airiq_advanced.yaml`, `airiq_basic_profile.yaml`, and
   `airiq_advanced_profile.yaml`. These feature profiles are consumed
   by Core / Voice / Mini products that may or may not have an `AirIQ`
   module attached — they describe IAQ telemetry behavior, not the
   `S360-210` module.

| Path                                              | Apparent purpose                                                                                                                            | Customer-facing concept              | Module identity              | Config-string token relationship                       | Current known consumers (search results)                                                                                                                                                                                                                                                                            | Recommended canonical name (Phase 3 target)             | Migration risk                                                                 | Compatibility shim recommended? | Tag(s)                                                                  |
|---------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------|------------------------------|--------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------|--------------------------------------------------------------------------------|---------------------------------|-------------------------------------------------------------------------|
| `packages/expansions/airiq.yaml`                  | Mini-board AirIQ stack on `i2c0` (SPS30, SCD41, SGP41 + optional SHT30)                                                                     | "Sense360 Mini AirIQ"                | `S360-210` (Mini variant)    | `AirIQ` token                                          | `packages/features/airiq_advanced.yaml` (legacy advanced profile); `products/sense360-mini-airiq.yaml`; `packages/hardware/sense360_core_ceiling_s3.yaml` (S3 variant); `packages/features/ceiling_led_ring_air_quality.yaml`                                                                                          | `airiq.yaml` (already canonical)                        | Low (already matches the productized token).                                   | No                              | `canonical-current` (filename matches WebFlash token)                   |
| `packages/expansions/airiq_ceiling.yaml`          | Ceiling-mount AirIQ stack on `expansion_i2c` (SPS30 + SCD41 + SGP41 + SHT30)                                                                | "Sense360 AirIQ" (ceiling)           | `S360-210-R4` (Ceiling)      | `AirIQ` token                                          | `products/sense360-core-voice-ceiling.yaml`; `products/sense360-core-ceiling.yaml`; `products/compile-only/ceiling-poe-airiq.yaml`; `products/sense360-core-c-usb.yaml` / `core-c-poe.yaml` / `core-c-pwr.yaml` / `core-v-c-usb.yaml` / `core-v-c-poe.yaml` / `core-v-c-pwr.yaml` (comment-only)                       | `airiq_ceiling.yaml` (already canonical)                | Low.                                                                           | No                              | `canonical-current`                                                     |
| `packages/expansions/airiq_wall.yaml`             | Wall-mount AirIQ stack                                                                                                                       | "Sense360 AirIQ" (wall)              | `S360-210-R4` (Wall variant) | `AirIQ` token                                          | `products/sense360-core-voice-wall.yaml`; `products/sense360-core-wall.yaml`; `products/sense360-core-w-*.yaml` (comment-only)                                                                                                                                                                                       | `airiq_wall.yaml` (already canonical)                   | Low.                                                                           | No                              | `canonical-current`                                                     |
| `packages/expansions/airiq_ceiling_s3.yaml`       | ESP32-S3 ceiling AirIQ variant                                                                                                              | "Sense360 AirIQ" (ceiling, S3)       | `S360-210` (S3 variant)      | `AirIQ` token                                          | No current product YAML consumer detected (scaffolding for ESP32-S3 ceiling variants); referenced in `docs/hardware/core-abstract-bus-reconciliation.md`.                                                                                                                                                            | `airiq_ceiling_s3.yaml` (already canonical)             | Low.                                                                           | No                              | `canonical-current` (orphan — no current product consumer)              |
| `packages/expansions/airiq_bathroom_base.yaml`    | Bathroom IAQ stack on `expansion_i2c` (SHT4x + BMP390 + SGP41). Carries `module_sku: S360-BATH-B`, `module_variant: bathroom_base`.         | "Sense360 VentIQ" (bathroom AirIQ)   | `S360-211` (VentIQ Base)     | `VentIQ` token (legacy filename uses `airiq_bathroom`) | `packages/expansions/bathroom.yaml` (legacy wrapper); `products/sense360-core-ceiling-bathroom.yaml`; `products/compile-only/ceiling-poe-ventiq.yaml`; `products/sense360-ceiling-poe-ventiq-roomiq.yaml` (Release-One); `products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`; `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml` | `ventiq_base.yaml` (Phase 3)                            | **High** — Release-One product `!include`s this file directly by path.        | Yes (Phase 2 alias `ventiq_base.yaml` !include-wrapping current file) | `misleading-name` (uses legacy `airiq_bathroom` filename for `VentIQ` module); `legacy-compatible` (Release-One depends on path); `candidate-for-alias`; `candidate-for-future-rename` |
| `packages/expansions/airiq_bathroom_pro.yaml`     | Pro bathroom IAQ stack adds MLX90614 + SPS30. Carries `module_sku: S360-BATH-P`, `module_variant: bathroom_pro`.                            | "Sense360 VentIQ Pro" (no productized "Pro" SKU exists today) | `S360-211` Pro variant (no separate SKU committed) | `VentIQ` token (legacy filename); no separate `VentIQPro` token in WebFlash | `packages/features/bathroom_pro_profile.yaml` (legacy feature profile)                                                                                                                                                                                                                                              | `ventiq_pro.yaml` (Phase 3, only if a Pro SKU is productized) | Medium — `pro` tier semantics are not productized; no current product YAML in `products/` consumes the Pro path. | Yes (Phase 2 alias once Pro SKU productization is decided)         | `misleading-name`; `behavior-hidden-by-name` (Pro implies a tier that doesn't yet exist as a productized SKU); `candidate-for-future-rename`               |
| `packages/expansions/bathroom.yaml`               | Compatibility wrapper — `!include`s `airiq_bathroom_base.yaml` + `../features/bathroom_profile.yaml`. Header explicitly says "compatibility wrapper for some generated or legacy configs". | "Sense360 Bathroom" (legacy customer-facing) | `S360-211` (VentIQ Base)     | `VentIQ` token (legacy `Bathroom` filename — forbidden token) | `products/sense360-core-c-*.yaml` / `core-v-c-*.yaml` (comment-only references)                                                                                                                                                                                                                                     | `ventiq.yaml` (Phase 3)                                 | Medium — comment-only consumers only; no current `!include` path.             | Yes (Phase 2 alias `ventiq.yaml`)                                  | `misleading-name` (uses forbidden `Bathroom` token); `legacy-compatible`; `candidate-for-alias`                                                                                                                          |
| `packages/features/airiq_basic.yaml`              | Mini-board AirIQ "basic" feature profile (Excellent/Good/Fair/Poor air quality rating template sensors)                                     | "Air Quality (Basic)"                | Generic IAQ (any module)     | No direct token — IAQ-feature-only                     | `products/sense360-mini-airiq-basic.yaml`                                                                                                                                                                                                                                                                           | `airiq_features_simple.yaml` (Phase 3 candidate)        | Medium — `basic` is not a productized tier; only the Mini "AirIQ Basic" product binds to it. | Yes (Phase 2 alias)                                                | `misleading-name` (`basic` is undefined in the productized model); `legacy-compatible`; `candidate-for-future-rename`                                                                                                                                          |
| `packages/features/airiq_advanced.yaml`           | Mini-board AirIQ "advanced" feature profile (full CO₂/PM/VOC/NOx sensors, threshold globals, calibration buttons, auto-ventilation script). `packages: airiq_base: !include airiq_basic.yaml`. | "Air Quality (Advanced)"             | Generic IAQ (any module)     | No direct token — IAQ-feature-only                     | `products/sense360-mini-airiq-advanced.yaml`; `products/sense360-mini-airiq.yaml`; `products/sense360-mini-airiq-ld2412.yaml`; `products/sense360-mini-full-ld2412.yaml`                                                                                                                                              | `airiq_features_full.yaml` (Phase 3 candidate)          | Medium — `advanced` is not a productized tier; multiple Mini products bind.    | Yes (Phase 2 alias)                                                | `misleading-name` (`advanced` is undefined in the productized model); `behavior-hidden-by-name` (contains `evaluate_air_quality` script + threshold mutation buttons not described by "AirIQ" alone); `legacy-compatible`; `candidate-for-future-rename` |
| `packages/features/airiq_basic_profile.yaml`      | Generic AirIQ MQTT-publish profile + placeholder `air_quality_state` template. Used by Core / Voice / Mini products as the base IAQ glue.   | "Air Quality (telemetry)"            | Generic IAQ (any module)     | No direct token                                        | `products/sense360-core-voice-ceiling.yaml`; `products/sense360-core-ceiling.yaml`; `products/sense360-core-voice-wall.yaml`; `products/sense360-core-wall.yaml`; `products/compile-only/ceiling-poe-airiq.yaml`; `products/compile-only/ceiling-poe-airiq-roomiq.yaml` (also referenced in `products/sense360-mini-airiq*.yaml` substitutions header comments) | `airiq_profile_base.yaml` (Phase 3 candidate)           | Medium — six product YAMLs and two compile-only YAMLs bind to this path.       | Yes (Phase 2 alias)                                                | `misleading-name` (`basic` ambiguous); `legacy-compatible`; `candidate-for-future-rename`                                                                                                                                                                                                            |
| `packages/features/airiq_advanced_profile.yaml`   | Layers `auto_fan_control` (GPIO15 output, `fan_switch`, 5-minute interval reading `air_quality_state`) on top of `airiq_basic_profile.yaml`. | "Air Quality + auto fan exchange"    | Generic IAQ (any module)     | No direct token; **hidden** fan-control behavior        | `docs/product-release-matrix.md` (mentioned as a feature). No current product YAML consumer detected in `products/`.                                                                                                                                                                                                | `airiq_profile_with_auto_fan.yaml` (Phase 3 candidate)  | Low — no current `products/` consumer.                                          | Yes (Phase 2 alias / split)                                        | **`behavior-hidden-by-name`** — fan output on GPIO15 + `auto_fan_control` script not described by name; `misleading-name` (`advanced`); `legacy-compatible`; `candidate-for-future-rename` |

> **AirIQ vs VentIQ separation reminder.** The WebFlash contract makes
> `AirIQ` and `VentIQ` mutually exclusive (one I²C IAQ slot per device).
> When naming-policy work resumes in Phase 3, no canonical name should
> blur the AirIQ / VentIQ boundary — the legacy `airiq_bathroom_*`
> filenames are the only files that currently do this, and they should
> move to `ventiq_*` canonical names with backward-compatible aliases.

### VentIQ / bathroom packages

The `Bathroom` customer-facing token is **forbidden** in WebFlash
artifact filenames per [`docs/webflash-contract.md`](webflash-contract.md)
§3 ("`Bathroom` → use `VentIQ`"). However, the file system still
carries `bathroom_*` filenames because Release-One product YAMLs
`!include` them by path. The package-readiness matrix and HW-009
already note this as a `legacy-compatible` retention; this audit
records the same retention plus a proposed Phase-2 alias path.

| Path                                              | Apparent purpose                                                                                                                                                                                                                                                                                | Customer-facing concept                  | Module identity         | Config-string token relationship                  | Current known consumers (search results)                                                                                                                                                                                                                                                          | Recommended canonical name (Phase 3 target)         | Migration risk                                                                                                                            | Compatibility shim recommended? | Tag(s)                                                                                            |
|---------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|-------------------------|---------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------|---------------------------------------------------------------------------------------------------|
| `packages/features/bathroom_profile.yaml`         | User-facing VentIQ feature profile — bathroom-themed sensors (shower detection, mold risk, ventilation advice, post-shower timer, copy-sensors of `bathroom_*` globals defined in `airiq_bathroom_base.yaml`). Entity names already use the productized `VentIQ` prefix in user-facing labels.   | "Sense360 VentIQ profile (Base)"          | `S360-211` (VentIQ Base) | `VentIQ` token (legacy `Bathroom` filename — forbidden token) | `products/sense360-ceiling-poe-ventiq-roomiq.yaml` (Release-One); `products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`; `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`; `products/sense360-core-ceiling-bathroom.yaml`; `products/compile-only/ceiling-poe-ventiq.yaml`; `packages/features/bathroom_pro_profile.yaml` (legacy include); `packages/expansions/bathroom.yaml` (legacy compatibility wrapper) | `ventiq_profile.yaml` (Phase 3)                     | **High** — Release-One product YAML `!include`s by path; LED preview product `!include`s by path; FanTRIAC product `!include`s by path. | Yes (Phase 2 alias)                                                  | `misleading-name` (forbidden `Bathroom` token); `legacy-compatible`; `candidate-for-alias`; `candidate-for-future-rename` |
| `packages/features/bathroom_pro_profile.yaml`     | VentIQ Pro feature profile (adds surface-temperature, condensation margin, PM1/PM2.5/PM10, AQI lambda) on top of `bathroom_profile.yaml`.                                                                                                                                                       | "Sense360 VentIQ profile (Pro)"           | `S360-211` Pro variant (no separate productized SKU committed) | `VentIQ` token (legacy `Bathroom` filename); no separate `VentIQPro` WebFlash token | `docs/product-matrix.md` (documentation only); no current product YAML consumer detected in `products/`.                                                                                                                                                                                          | `ventiq_pro_profile.yaml` (Phase 3, only after Pro SKU productization decision) | Low — no current `products/` consumer.                                                                                                    | Yes (Phase 2 alias only after Pro tier is productized as a real SKU) | `misleading-name`; `behavior-hidden-by-name` (`pro` tier not productized); `candidate-for-future-rename`                  |

> **VentIQ + RoomIQ + Bathroom feature naming.** The bathroom feature
> packages already use `VentIQ` in user-facing entity names (`"${friendly_name}
> VentIQ Temperature"`, `"${friendly_name} VentIQ Humidity"`, etc.). The
> filename is the only remaining legacy surface. Renaming the file in
> Phase 3 + shipping a compatibility shim in Phase 2 lets the user-facing
> name and the filename converge without breaking Release-One.

### RoomIQ / comfort / presence packages

The `RoomIQ` token (`S360-200`) is the productized identity for the
"comfort + presence" room sensor module. The repo splits RoomIQ into a
**comfort** sub-block (temperature / humidity / pressure / light) and a
**presence** sub-block (mmWave / PIR), plus generic LD2412 / LD2450
hardware drivers used by the Mini board. Filenames still use the
legacy `comfort_*` / `presence_*` tokens (both listed as forbidden in
the WebFlash contract); the package contents and entity names already
adopt `RoomIQ` in user-facing labels.

| Path                                                       | Apparent purpose                                                                                                          | Customer-facing concept           | Module identity                | Config-string token relationship                                   | Current known consumers (search results)                                                                                                                                                                                                                                                | Recommended canonical name (Phase 3 target)         | Migration risk                                                                                                                                          | Compatibility shim recommended? | Tag(s)                                                                                            |
|------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|-----------------------------------|--------------------------------|--------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------|---------------------------------------------------------------------------------------------------|
| `packages/expansions/comfort.yaml`                         | Generic comfort hardware driver (SHT40 + BH1750 + BME680 on `i2c0`)                                                       | "Sense360 RoomIQ (comfort half)"  | `S360-200` (comfort sub-block) | `RoomIQ` token (legacy `Comfort` filename — forbidden)             | `packages/SENSE360_MODULES.md`; `packages/features/comfort_advanced_profile.yaml`; `docs/hardware/core-abstract-bus-reconciliation.md`. No current product YAML consumer in `products/`.                                                                                                  | `roomiq_comfort.yaml` (Phase 3)                     | Low — no `products/` consumer.                                                                                                                          | Yes (Phase 2 alias)             | `misleading-name` (forbidden `Comfort` token); `legacy-compatible`; `candidate-for-alias`         |
| `packages/expansions/comfort_ceiling.yaml`                 | Ceiling-mount comfort driver. Includes `comfort_ceiling_als_int_pin` (CORE-ABSTRACT-BUS-001C area).                       | "Sense360 RoomIQ" (ceiling)       | `S360-200-R4` (ceiling)         | `RoomIQ` token (legacy `Comfort` filename — forbidden)             | `products/sense360-ceiling-poe-ventiq-roomiq.yaml` (Release-One); `products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`; `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`; `products/compile-only/ceiling-poe-roomiq.yaml`; `products/compile-only/ceiling-poe-airiq-roomiq.yaml`; `products/sense360-core-voice-ceiling.yaml`; `products/sense360-core-ceiling.yaml` | `roomiq_comfort_ceiling.yaml` (Phase 3)             | **High** — Release-One product `!include`s this file directly. Affected by CORE-ABSTRACT-BUS-001C pin rebind (independent track).                       | Yes (Phase 2 alias)             | `misleading-name`; `legacy-compatible`; `candidate-for-alias`; `candidate-for-future-rename`      |
| `packages/expansions/comfort_wall.yaml`                    | Wall-mount comfort driver                                                                                                 | "Sense360 RoomIQ" (wall)          | `S360-200-R4` (wall)            | `RoomIQ` token                                                     | `products/sense360-core-voice-wall.yaml`; `products/sense360-core-wall.yaml`                                                                                                                                                                                                              | `roomiq_comfort_wall.yaml` (Phase 3)                | Medium — two Core wall products bind.                                                                                                                   | Yes (Phase 2 alias)             | `misleading-name`; `legacy-compatible`; `candidate-for-alias`                                     |
| `packages/expansions/comfort_ceiling_s3.yaml`              | ESP32-S3 ceiling comfort variant                                                                                          | "Sense360 RoomIQ" (S3 ceiling)    | `S360-200` (S3 variant)         | `RoomIQ` token                                                     | No current product YAML consumer in `products/`.                                                                                                                                                                                                                                          | `roomiq_comfort_ceiling_s3.yaml` (Phase 3)          | Low — no current consumer.                                                                                                                              | Optional (alias not needed if file remains orphan) | `misleading-name`; `legacy-compatible`                                                            |
| `packages/expansions/presence_ceiling.yaml`                | Ceiling-mount presence driver (LD2450 + PIR)                                                                              | "Sense360 RoomIQ" (presence half) | `S360-200-R4` (ceiling)         | `RoomIQ` token (legacy `Presence` filename — forbidden)            | `products/sense360-ceiling-poe-ventiq-roomiq.yaml` (Release-One); `products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`; `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`; `products/compile-only/ceiling-poe-roomiq.yaml`; `products/compile-only/ceiling-poe-airiq-roomiq.yaml`; `products/sense360-core-voice-ceiling.yaml`; `products/sense360-core-ceiling.yaml`; `products/sense360-core-ceiling-bathroom.yaml`; `products/sense360-core-ceiling-presence.yaml` | `roomiq_presence_ceiling.yaml` (Phase 3)            | **High** — Release-One product `!include`s this file directly.                                                                                          | Yes (Phase 2 alias)             | `misleading-name`; `legacy-compatible`; `candidate-for-alias`; `candidate-for-future-rename`      |
| `packages/expansions/presence_wall.yaml`                   | Wall-mount presence driver                                                                                                | "Sense360 RoomIQ" (presence wall) | `S360-200-R4` (wall)            | `RoomIQ` token                                                     | `products/sense360-core-voice-wall.yaml`; `products/sense360-core-wall-presence.yaml`                                                                                                                                                                                                     | `roomiq_presence_wall.yaml` (Phase 3)               | Medium.                                                                                                                                                 | Yes (Phase 2 alias)             | `misleading-name`; `legacy-compatible`; `candidate-for-alias`                                     |
| `packages/expansions/presence_ld2412.yaml`                 | Generic LD2412 24GHz radar driver (used by Mini-board presence products)                                                  | Hardware-driver-only               | `RoomIQ` sub-component or Mini  | No direct token (raw sensor)                                       | `products/sense360-mini-presence-ld2412.yaml`; `products/sense360-mini-airiq-ld2412.yaml` (via comment, presence module include is in feature profile)                                                                                                                                    | `presence_ld2412.yaml` (acceptable as hardware-driver) | Low — narrow consumer set.                                                                                                                              | No                              | `legacy-compatible` (hardware driver — the LD2412 vendor name is acceptable)                      |
| `packages/expansions/presence_ld2450.yaml`                 | Generic LD2450 mmWave driver                                                                                              | Hardware-driver-only               | `RoomIQ` sub-component or Mini  | No direct token                                                    | `products/sense360-mini-presence.yaml`                                                                                                                                                                                                                                                    | `presence_ld2450.yaml` (acceptable as hardware-driver) | Low.                                                                                                                                                    | No                              | `legacy-compatible`                                                                               |
| `packages/expansions/presence_module_ceiling.yaml`         | Ceiling presence module mapping (supports LD2450 and LD2412 selection)                                                    | "Sense360 RoomIQ" (presence module, ceiling) | `S360-200-R4` (ceiling) | `RoomIQ` token (legacy `Presence` filename — forbidden)             | No current product YAML consumer in `products/`; referenced in `docs/hardware/core-abstract-bus-reconciliation.md`.                                                                                                                                                                       | `roomiq_presence_module_ceiling.yaml` (Phase 3)     | Low — no current `products/` consumer.                                                                                                                  | Optional                        | `misleading-name`; `legacy-compatible` (orphan)                                                   |
| `packages/expansions/presence_ceiling_s3.yaml`             | ESP32-S3 ceiling presence variant                                                                                          | "Sense360 RoomIQ" (presence, S3 ceiling) | `S360-200` (S3 variant) | `RoomIQ` token                                                     | No current product YAML consumer in `products/`.                                                                                                                                                                                                                                          | `roomiq_presence_ceiling_s3.yaml` (Phase 3)         | Low — orphan.                                                                                                                                            | Optional                        | `misleading-name`; `legacy-compatible` (orphan)                                                   |
| `packages/features/comfort_basic_profile.yaml`             | Ceiling RoomIQ comfort feature profile — user-facing entities (RoomIQ Temperature / Humidity / Light Level / Comfort)     | "RoomIQ comfort (ceiling)"        | `S360-200-R4` (ceiling)         | `RoomIQ` token (legacy `Comfort` + `basic`)                         | `products/sense360-ceiling-poe-ventiq-roomiq.yaml` (Release-One); `products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`; `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`; `products/compile-only/ceiling-poe-roomiq.yaml`; `products/compile-only/ceiling-poe-airiq-roomiq.yaml`; `products/sense360-core-voice-ceiling.yaml`; `products/sense360-core-ceiling.yaml` | `roomiq_comfort_profile.yaml` (Phase 3)             | **High** — Release-One product binds.                                                                                                                  | Yes (Phase 2 alias)             | `misleading-name` (`basic` + forbidden `Comfort` token); `legacy-compatible`; `candidate-for-alias` |
| `packages/features/comfort_basic_profile_wall.yaml`        | Wall RoomIQ comfort profile                                                                                                | "RoomIQ comfort (wall)"           | `S360-200-R4` (wall)            | `RoomIQ` token                                                     | `products/sense360-core-wall.yaml`; `products/sense360-core-voice-wall.yaml`                                                                                                                                                                                                              | `roomiq_comfort_profile_wall.yaml` (Phase 3)        | Medium.                                                                                                                                                 | Yes (Phase 2 alias)             | `misleading-name`; `legacy-compatible`                                                            |
| `packages/features/comfort_advanced_profile.yaml`          | Advanced comfort feature profile (orphan — no current product YAML consumer)                                              | "RoomIQ comfort (advanced)"        | `S360-200`                      | `RoomIQ` token                                                     | No current product YAML consumer.                                                                                                                                                                                                                                                          | `roomiq_comfort_profile_full.yaml` (Phase 3)        | Low — orphan.                                                                                                                                           | Optional                        | `misleading-name` (`advanced` + forbidden `Comfort` token); `legacy-compatible`                   |
| `packages/features/presence_basic.yaml`                    | Mini-board presence basic profile                                                                                          | "Presence (Mini, basic)"          | Mini (generic)                  | `RoomIQ` token (Mini)                                              | `products/sense360-mini-presence-basic.yaml`                                                                                                                                                                                                                                              | `presence_features_simple.yaml` (Phase 3 candidate) | Low.                                                                                                                                                    | Yes (Phase 2 alias)             | `misleading-name` (`basic`); `legacy-compatible`                                                  |
| `packages/features/presence_advanced.yaml`                 | Mini-board presence advanced profile                                                                                       | "Presence (Mini, advanced)"       | Mini (generic)                  | `RoomIQ` token                                                     | `products/sense360-mini-presence-advanced.yaml`                                                                                                                                                                                                                                            | `presence_features_full.yaml` (Phase 3 candidate)    | Low.                                                                                                                                                    | Yes (Phase 2 alias)             | `misleading-name` (`advanced`); `legacy-compatible`                                               |
| `packages/features/presence_advanced_ld2412.yaml`          | LD2412 presence advanced profile                                                                                           | "Presence LD2412 (advanced)"      | Mini-LD2412                     | `RoomIQ` token                                                     | `packages/features/presence_advanced_profile_ld2412.yaml`                                                                                                                                                                                                                                  | `presence_features_full_ld2412.yaml` (Phase 3 candidate) | Low.                                                                                                                                                    | Yes                             | `misleading-name`; `legacy-compatible`                                                            |
| `packages/features/presence_basic_profile.yaml`            | Generic presence basic feature profile (used by RoomIQ-bearing ceiling / wall products and Mini-LD2450 presence product)  | "RoomIQ presence (basic)"         | `S360-200` or Mini              | `RoomIQ` token (legacy `Presence` + `basic`)                       | `products/sense360-ceiling-poe-ventiq-roomiq.yaml` (Release-One); `products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`; `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`; `products/compile-only/ceiling-poe-roomiq.yaml`; `products/compile-only/ceiling-poe-airiq-roomiq.yaml`; multiple Core / Mini presence product YAMLs | `roomiq_presence_profile.yaml` (Phase 3 — RoomIQ scope only) or `presence_features_profile_simple.yaml` (if kept generic) | **High** — Release-One binds.                                                                                                                          | Yes (Phase 2 alias)             | `misleading-name`; `legacy-compatible`; `candidate-for-alias`                                     |
| `packages/features/presence_basic_profile_ld2412.yaml`     | LD2412 presence basic profile                                                                                              | "Presence LD2412 (basic)"         | Mini-LD2412                     | `RoomIQ` token                                                     | `products/sense360-mini-presence-ld2412.yaml`; `products/sense360-mini-airiq-ld2412.yaml`                                                                                                                                                                                                  | `presence_features_simple_ld2412.yaml` (Phase 3 candidate) | Low.                                                                                                                                                    | Yes                             | `misleading-name`; `legacy-compatible`                                                            |
| `packages/features/presence_advanced_profile.yaml`         | Generic presence advanced profile (orphan today)                                                                            | "Presence (advanced)"             | RoomIQ or Mini                  | `RoomIQ` token                                                     | No current product YAML consumer.                                                                                                                                                                                                                                                          | `presence_features_profile_full.yaml` (Phase 3 candidate) | Low — orphan.                                                                                                                                           | Optional                        | `misleading-name`; `legacy-compatible`                                                            |
| `packages/features/presence_advanced_profile_ld2412.yaml`  | LD2412 presence advanced profile (variant)                                                                                  | "Presence LD2412 (advanced)"      | Mini-LD2412                     | `RoomIQ` token                                                     | `products/sense360-mini-presence-advanced-ld2412.yaml`                                                                                                                                                                                                                                     | `presence_features_profile_full_ld2412.yaml` (Phase 3 candidate) | Low.                                                                                                                                                    | Yes                             | `misleading-name`; `legacy-compatible`                                                            |

### LED / status ring packages

The `LED` token is the productized identity for `S360-300` (the WS2812B
addressable LED ring). It is currently a **preview-only** module
because Release-One excludes the LED slot (config string
`Ceiling-POE-VentIQ-RoomIQ` has no `LED` segment); the LED preview
config is `Ceiling-POE-VentIQ-RoomIQ-LED`. LED package filenames carry
a mix of legacy and productized vocabulary — `led_ring_*` for hardware
drivers (consistent with the WebFlash module name), and
`ceiling_halo_leds` / `ceiling_led_ring_air_quality` /
`mini_four_leds_*` for feature behaviour.

The cleanup audit ([`docs/cleanup-audit.md`](cleanup-audit.md) §LED /
LED Ring references) already calls these `legacy-compatible` and
explicitly says not to rename them.

| Path                                                          | Apparent purpose                                                                                                                                                  | Customer-facing concept                       | Module identity     | Config-string token relationship                          | Current known consumers (search results)                                                                                                                                                                                                                                                    | Recommended canonical name (Phase 3 target)               | Migration risk                                                            | Compatibility shim recommended? | Tag(s)                                                                                  |
|---------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------|---------------------|-----------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------|---------------------------------------------------------------------------|---------------------------------|-----------------------------------------------------------------------------------------|
| `packages/hardware/led_ring_ceiling.yaml`                     | WS2812B ceiling LED ring hardware driver                                                                                                                          | "Sense360 LED" (ceiling)                       | `S360-300-R4` (ceiling) | `LED` token                                                | `products/sense360-ceiling-poe-ventiq-roomiq-led.yaml` (LED preview); `products/sense360-core-ceiling.yaml`; `products/sense360-core-ceiling-bathroom.yaml`; `products/sense360-core-ceiling-presence.yaml`                                                                                    | `led_ring_ceiling.yaml` (acceptable — `LED` token matches) | Low.                                                                       | No                              | `legacy-compatible` (filename matches `LED` token at module-level)                      |
| `packages/hardware/led_ring_wall.yaml`                        | WS2812B wall LED ring hardware driver                                                                                                                             | "Sense360 LED" (wall)                          | `S360-300-R4` (wall)    | `LED` token                                                | `products/sense360-core-wall-presence.yaml`                                                                                                                                                                                                                                                  | `led_ring_wall.yaml` (acceptable)                          | Low.                                                                       | No                              | `legacy-compatible`                                                                     |
| `packages/hardware/led_ring_mic_ceiling.yaml`                 | LED ring + microphone variant (voice ceiling)                                                                                                                     | "Sense360 LED Voice" (ceiling)                  | Voice variant         | `LED` token (voice variant)                                | `products/sense360-core-voice-ceiling.yaml`; `products/sense360-core-v-c-poe.yaml`; `products/sense360-core-v-c-usb.yaml`; `products/sense360-core-v-c-pwr.yaml`                                                                                                                              | `led_ring_voice_ceiling.yaml` (Phase 3, low priority)      | Low.                                                                       | Optional                        | `legacy-compatible`                                                                     |
| `packages/hardware/led_ring_mic_wall.yaml`                    | LED ring + microphone variant (voice wall)                                                                                                                        | "Sense360 LED Voice" (wall)                     | Voice variant         | `LED` token (voice variant)                                | `products/sense360-core-voice-wall.yaml`; `products/sense360-core-v-w-poe.yaml`; `products/sense360-core-v-w-usb.yaml`; `products/sense360-core-v-w-pwr.yaml`                                                                                                                                | `led_ring_voice_wall.yaml` (Phase 3, low priority)         | Low.                                                                       | Optional                        | `legacy-compatible`                                                                     |
| `packages/features/ceiling_halo_leds.yaml`                    | LED ring effects / animations for ceiling halo                                                                                                                    | "Sense360 LED effects" (ceiling)                | `S360-300-R4`         | `LED` token (feature side)                                 | `products/sense360-core-voice-ceiling.yaml`; `products/sense360-core-ceiling-bathroom.yaml`; `products/sense360-core-ceiling.yaml`; `products/sense360-core-ceiling-presence.yaml`                                                                                                            | `led_ring_effects_ceiling.yaml` (Phase 3, low priority)    | Medium — four product YAML consumers.                                      | Optional                        | `legacy-compatible` (cleanup-audit treats as canonical)                                  |
| `packages/features/ceiling_led_ring_air_quality.yaml`         | LED ring air-quality colour-coding feature (orphan today)                                                                                                          | "Sense360 LED Air-Quality colours" (ceiling)    | `S360-300-R4`         | `LED` + `AirIQ` tokens                                     | No current product YAML consumer.                                                                                                                                                                                                                                                            | `led_ring_air_quality_ceiling.yaml` (Phase 3, low priority) | Low — orphan.                                                              | Optional                        | `legacy-compatible`                                                                     |
| `packages/features/mini_four_leds_addr.yaml`                  | Mini-board addressable four-LED status feature                                                                                                                    | "Sense360 Mini status LEDs"                     | Mini-onboard          | Mini-board (no productized `LED` token directly)            | `tests/INTEGRATION_GUIDE.md`, `docs/ci-pipeline.md` (mentions); no current product YAML consumer in `products/`.                                                                                                                                                                              | `mini_status_leds_addressable.yaml` (Phase 3, low priority) | Low.                                                                       | Optional                        | `legacy-compatible`                                                                     |
| `packages/features/mini_four_leds_air_quality.yaml`           | Mini-board four-LED air-quality status                                                                                                                            | "Sense360 Mini AirIQ status LEDs"               | Mini-onboard          | Mini-board                                                  | `products/sense360-mini-airiq-ld2412.yaml`; `products/sense360-mini-airiq.yaml`                                                                                                                                                                                                              | `mini_status_leds_air_quality.yaml` (Phase 3, low priority) | Low.                                                                       | Optional                        | `legacy-compatible`                                                                     |

> **LED stable promotion is out of scope.** This audit does not change
> the Sense360 LED Release-One exclusion ([`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)
> §Sense360 LED policy) or move `LED` from preview to stable. The
> filename audit and the lifecycle status are independent tracks; LED
> preview-vs-stable is gated by `S360-300-BENCH-001` and the WebFlash
> hardware-test follow-ups, not by package naming.

### Fan-control packages

The four productized fan tokens (`FanRelay` / `FanPWM` / `FanDAC` /
`FanTRIAC`) each map to a distinct hardware driver. The current
filenames mix vendor wording (`fan_relay`, `fan_pwm`, `fan_triac`,
`fan_gp8403`) and one Sense360-specific PWM (`sense360_fan_pwm.yaml`).
The `fan_control_*` feature profiles add an additional hidden
behavior: they are named "fan control" but the basic profile only
exposes user-facing entities — the actual auto-ventilation logic is
inside `airiq_advanced_profile.yaml` (see
[AirIQ packages](#airiq-packages) — that is the
`behavior-hidden-by-name` case).

| Path                                              | Apparent purpose                                                                                                                                          | Customer-facing concept                                 | Module identity         | Config-string token relationship  | Current known consumers (search results)                                                                                                                                                                                                                       | Recommended canonical name (Phase 3 target)         | Migration risk                                                                                                                                       | Compatibility shim recommended? | Tag(s)                                                                                          |
|---------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------|-------------------------|-----------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------|-------------------------------------------------------------------------------------------------|
| `packages/expansions/fan_relay.yaml`              | Relay-driven fan driver (currently deferred — `PACKAGE-RELAY-001` blocked behind `CORE-ABSTRACT-BUS-001A`)                                               | "Sense360 FanRelay"                                     | `S360-310`              | `FanRelay` token                  | No current product YAML consumer in `products/`. Referenced by candidate ledger and FanRelay product roadmap.                                                                                                                                                | `fan_relay.yaml` (acceptable) or `fanrelay.yaml`    | Low.                                                                                                                                                  | Optional (Phase 2 alias `fanrelay.yaml`) | `legacy-compatible` (filename close to canonical, only difference is the underscore)            |
| `packages/expansions/fan_pwm.yaml`                | PWM fan driver (12V via expansion GPIO)                                                                                                                   | "Sense360 FanPWM"                                       | `S360-311`              | `FanPWM` token                    | Comment-only references in `products/sense360-core-*-poe.yaml` / `*-usb.yaml` / `*-pwr.yaml` and `products/sense360-core-ceiling-bathroom.yaml`.                                                                                                              | `fan_pwm.yaml` (acceptable) or `fanpwm.yaml`        | Low.                                                                                                                                                  | Optional                        | `legacy-compatible`                                                                              |
| `packages/expansions/fan_12v_pwm.yaml`            | Alternate 12V PWM fan driver                                                                                                                              | "Sense360 FanPWM 12V"                                   | `S360-311` variant      | `FanPWM` token                    | `packages/SENSE360_MODULES.md` only; no current product YAML consumer.                                                                                                                                                                                       | `fan_pwm_12v.yaml` (Phase 3 candidate)              | Low — orphan in products.                                                                                                                            | Optional                        | `legacy-compatible`; `candidate-for-future-rename` (token order — vendor `12v_pwm` reads as variant) |
| `packages/expansions/fan_gp8403.yaml`             | GP8403 DAC fan driver (0–10V analog)                                                                                                                      | "Sense360 FanDAC"                                       | `S360-312`              | `FanDAC` token                    | Comment-only references in multiple `products/sense360-core-*.yaml`; `packages/features/fan_control_advanced_profile.yaml`.                                                                                                                                  | `fan_dac.yaml` or `fandac.yaml` (Phase 3)            | Low — comment-only consumers.                                                                                                                        | Yes (Phase 2 alias `fan_dac.yaml`) | `misleading-name` (filename uses vendor `gp8403`, not productized `FanDAC`); `legacy-compatible`; `candidate-for-alias`; `candidate-for-future-rename` |
| `packages/expansions/fan_triac.yaml`              | TRIAC mains-fan dimmer (`ac_dimmer`). HW-005 blocked; COMPLIANCE-001 blocked.                                                                              | "Sense360 FanTRIAC"                                     | `S360-320`              | `FanTRIAC` token                  | `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml` (blocked / reference)                                                                                                                                                                            | `fan_triac.yaml` (acceptable) or `fantriac.yaml`    | Low — filename close to canonical.                                                                                                                   | Optional                        | `legacy-compatible`                                                                              |
| `packages/expansions/sense360_fan_pwm.yaml`       | Sense360-branded PWM fan stand-alone product (used by the dedicated FanPWM product YAML)                                                                  | "Sense360 FanPWM module"                                | `S360-311` (standalone) | `FanPWM` token                    | `products/sense360-fan-pwm.yaml`                                                                                                                                                                                                                              | `fanpwm_standalone.yaml` or `fan_pwm_standalone.yaml` (Phase 3) | Low.                                                                                                                                                  | Optional                        | `legacy-compatible`                                                                              |
| `packages/features/fan_control_profile.yaml`      | User-facing fan control entities (speed, quiet mode, auto mode). Header explicitly says auto-mode requires temperature/humidity sensor.                  | "Fan control entities"                                  | Any fan module          | `Fan*` tokens (feature side)      | `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`; `products/sense360-core-ceiling-bathroom.yaml`; `packages/features/fan_control_advanced_profile.yaml`                                                                                          | `fan_control_profile.yaml` (acceptable; describes feature) | Low.                                                                                                                                                  | Optional                        | `legacy-compatible`                                                                              |
| `packages/features/fan_control_advanced_profile.yaml` | Advanced fan control entities (dual-channel, voltage display, RPM, stall, custom curves)                                                                  | "Fan control entities (advanced)"                       | FanPWM / FanDAC          | `Fan*` tokens                     | No current product YAML consumer.                                                                                                                                                                                                                              | `fan_control_profile_full.yaml` (Phase 3 candidate)   | Low — orphan.                                                                                                                                        | Optional                        | `misleading-name` (`advanced` tier undefined); `legacy-compatible`                              |

> **Auto fan control behavior hidden by AirIQ profile name.** The
> existing auto-ventilation behavior currently lives in
> `packages/features/airiq_advanced_profile.yaml` (GPIO15 + `fan_switch`
> + `auto_fan_control` script), **not** in any `fan_control_*` package.
> A future Phase-3 PR should consider splitting that behavior out into a
> productized `airiq_auto_fan_exchange.yaml` (or naming the existing
> file `airiq_profile_with_auto_fan.yaml`) so that fan control is not
> hidden inside an IAQ-named profile. This audit does **not** perform
> that split.

### Power / PSU packages

Power packages name PSU topology (`240v_ac`, `poe`, `usb`) which maps
to WebFlash power tokens (`PWR`, `POE`, `USB`). Filenames are
acceptable internal-implementation names; no Phase-3 rename is needed.

| Path                                              | Apparent purpose                                                                                                            | Customer-facing concept                 | Module identity        | Config-string token relationship | Current known consumers (search results)                                                                                                                                                                                                                                                       | Recommended canonical name (Phase 3 target) | Migration risk                                                                                                              | Compatibility shim recommended? | Tag(s)                                                              |
|---------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|-----------------------------------------|------------------------|----------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|---------------------------------|---------------------------------------------------------------------|
| `packages/hardware/power_240v.yaml`               | 240V AC PSU (HLK-5M05). PACKAGE-POWER-400-001 cleanup deferred behind BOM cross-check / COMPLIANCE-001.                     | "Sense360 PWR-240V" (S360-400)            | `S360-400`             | `PWR` token                       | `products/sense360-core-c-pwr.yaml` / `core-v-c-pwr.yaml` / `core-w-pwr.yaml` / `core-v-w-pwr.yaml`                                                                                                                                                                                          | `power_240v.yaml` (acceptable)              | Low — already canonical.                                                                                                     | No                              | `acceptable-internal` (power topology naming is acceptable)         |
| `packages/hardware/power_poe.yaml`                | PoE PSU (S360-410 discrete topology, BOM-confirmed via `HW-BOM-ASSETS-002`). Comment-only header cleanup landed in PR #538. | "Sense360 PoE PSU" (S360-410)             | `S360-410`             | `POE` token                       | `products/sense360-ceiling-poe-ventiq-roomiq.yaml` (Release-One); `products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`; `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`; `products/compile-only/ceiling-poe*.yaml`; `products/sense360-core-*-poe.yaml`; `products/sense360-poe.yaml` | `power_poe.yaml` (acceptable)               | Low — already canonical.                                                                                                     | No                              | `acceptable-internal`                                               |
| `packages/hardware/power_usb.yaml`                | USB-C PSU                                                                                                                  | "Sense360 USB PSU"                       | n/a (no SKU)            | `USB` token                       | `products/sense360-core-*-usb.yaml`; `products/sense360-core-v-w-usb.yaml`                                                                                                                                                                                                                    | `power_usb.yaml` (acceptable)               | Low.                                                                                                                         | No                              | `acceptable-internal`                                               |
| `packages/hardware/power_management.yaml`         | Generic power management entities (orphan today — verified via grep against `products/`)                                   | "Generic power management"               | n/a                    | n/a                              | No current product YAML consumer.                                                                                                                                                                                                                                                              | `power_management.yaml` (acceptable)        | Low — orphan.                                                                                                                | No                              | `acceptable-internal`                                               |

### Core / hardware abstract-bus packages

Core hardware packages name the board (`sense360_core`,
`sense360_core_ceiling`, `sense360_core_wall`, etc.). The `voice` and
`mini` variants extend the Core identity for voice-capable and Mini-
board boards. These are `acceptable-internal` because they describe
the implementation hardware abstract bus — they are not customer-facing
product identifiers (which live in the kit-intent matrix and config
strings).

| Path                                                | Apparent purpose                                              | Module identity                | Tag                    |
|-----------------------------------------------------|---------------------------------------------------------------|-------------------------------|------------------------|
| `packages/hardware/sense360_core.yaml`              | Sense360 Core base (S360-100 abstract substitution surface)   | `S360-100`                    | `acceptable-internal`  |
| `packages/hardware/sense360_core_ceiling.yaml`      | Sense360 Core ceiling-mount variant                           | `S360-100-R4` (ceiling)        | `acceptable-internal`  |
| `packages/hardware/sense360_core_ceiling_s3.yaml`   | Sense360 Core ESP32-S3 ceiling variant                        | `S360-100` (S3 variant)        | `acceptable-internal`  |
| `packages/hardware/sense360_core_mapping.yaml`      | Sense360 Core abstract-bus pin map (relay_pin, expander_int_pin, status LED) | `S360-100-R4`         | `acceptable-internal`  |
| `packages/hardware/sense360_core_mini.yaml`         | Sense360 Mini board core                                      | Mini                          | `acceptable-internal`  |
| `packages/hardware/sense360_core_poe.yaml`          | Sense360 Core PoE bundle                                      | `S360-100-R4` + `S360-410`    | `acceptable-internal`  |
| `packages/hardware/sense360_core_voice.yaml`        | Sense360 Core voice variant                                   | Voice                         | `acceptable-internal`  |
| `packages/hardware/sense360_core_voice_ceiling.yaml`| Voice ceiling variant                                         | Voice + Ceiling                | `acceptable-internal`  |
| `packages/hardware/sense360_core_voice_wall.yaml`   | Voice wall variant                                            | Voice + Wall                   | `acceptable-internal`  |
| `packages/hardware/sense360_core_wall.yaml`         | Sense360 Core wall-mount variant                              | `S360-100-R4` (wall)            | `acceptable-internal`  |
| `packages/hardware/mini_onboard_sensors.yaml`       | Mini-board onboard sensors (LTR-303, SHT30, SCD40)            | Mini                          | `acceptable-internal`  |
| `packages/hardware/presence_dfrobot_c4001.yaml`     | DFRobot C4001 mmWave hardware driver                          | C4001 (3rd-party radar)         | `acceptable-internal`  |
| `packages/hardware/presence_ld2412.yaml`            | LD2412 24GHz radar driver                                     | LD2412 (3rd-party radar)        | `acceptable-internal` (hardware-driver vendor naming acceptable) |
| `packages/hardware/presence_ld2450.yaml`            | LD2450 mmWave radar driver                                    | LD2450 (3rd-party radar)        | `acceptable-internal`  |
| `packages/expansions/gpio_expander_sx1509.yaml`     | SX1509 I²C GPIO expander                                      | SX1509 (3rd-party expander)     | `acceptable-internal`  |

### Other feature packages

| Path                                                | Apparent purpose                                                                              | Tag                    |
|-----------------------------------------------------|-----------------------------------------------------------------------------------------------|------------------------|
| `packages/features/device_health.yaml`              | Device-health diagnostic entities (uptime, free heap, signal strength)                        | `acceptable-internal`  |
| `packages/features/diagnostics.yaml`                | Diagnostic logging / state surfacing                                                          | `acceptable-internal`  |

## Naming policy

This section documents the **naming policy that future package /
product / config-string work should follow**. It does **not** require
any current file to change; it is the rule set that the Phase 2–5
migration plan applies.

### Rule 1 — Package filenames are internal implementation details

- Package filenames under `packages/**` are repo-internal. Customers do
  not see them. End-user docs (WebFlash UI, Home Assistant device
  cards, customer purchase flow) must continue to talk about the
  productized identifiers, not the filenames.
- Existing legacy filenames remain `legacy-compatible` until at least
  the migration plan (below) explicitly retires them. Treat the
  current paths as **public API** for the duration of the deprecation
  window because third-party downstream users can pin to
  `github://sense360store/esphome-public/packages/...` URLs.

### Rule 2 — Customer-facing names must be outcome-first

- Customer-facing names belong in
  [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json)
  (kit / bundle SKU) and in entity `name:` fields surfaced to Home
  Assistant. They should describe what the customer gets, not which
  PCB it uses.
- Examples already in the repo: `S360-KIT-BATH-POE` ("Sense360 Bathroom
  Kit — PoE"), entity names like `${friendly_name} VentIQ Temperature`
  and `${friendly_name} RoomIQ Temperature`.
- Filenames should not invent new customer-facing names. If a new
  outcome is identified, it goes into the kit-intent matrix or the
  WebFlash contract, not into a package filename.

### Rule 3 — Module names map to SKUs where possible

- Module identifiers (`AirIQ`, `VentIQ`, `RoomIQ`, `LED`, `FanRelay`,
  `FanPWM`, `FanDAC`, `FanTRIAC`) are the productized SKUs from
  [`docs/webflash-contract.md`](webflash-contract.md) §3.
- When a package binds to a specific module SKU, the canonical filename
  should mirror the module token (e.g. `ventiq_*.yaml` for `S360-211`,
  `roomiq_*.yaml` for `S360-200`, `fandac.yaml` for `S360-312`).
- Hardware-driver packages may still use vendor names (e.g.
  `presence_ld2412.yaml`, `gpio_expander_sx1509.yaml`) because they
  describe the IC, not the product.

### Rule 4 — Config strings remain grammar / build identity

- Config strings (`Ceiling-POE-VentIQ-RoomIQ`,
  `Ceiling-POE-VentIQ-RoomIQ-LED`, etc.) are defined by
  [`docs/webflash-contract.md`](webflash-contract.md) §2 + §3 and stay
  the **only** firmware-artifact-naming source of truth.
- Package filenames do not feed into config strings. The mapping is
  one-way: a product YAML composes one config string from multiple
  package files, but a package filename never appears in an artifact
  name.

### Rule 5 — Avoid `basic`, `advanced`, and `pro` unless explicitly defined

- `basic`, `advanced`, `pro`, `simple`, `full`, and similar tier
  tokens carry no productized meaning today. They appear only in
  package and feature-profile filenames.
- Future packages should describe the **feature shape** (e.g. `_simple`
  if it really is a simpler surface, `_full` if it exposes the full
  raw sensor stack) only when the tier is documented and reviewed.
- A package filename containing `pro` must not imply a Pro tier
  customer SKU unless that SKU exists in
  [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  and in [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json).
- Existing `_basic` / `_advanced` / `_pro` package filenames stay
  `legacy-compatible` until Phase 5; new packages must not introduce
  them.

### Rule 6 — Avoid package names that hide control behavior

- A package that performs control behaviour (GPIO output, fan switch,
  relay actuation, automation script that toggles a switch) must
  carry that behaviour in its filename.
- Example violation: `airiq_advanced_profile.yaml` adds an
  `auto_fan_control` script + `fan_switch` on `GPIO15`. Its name
  describes IAQ, not fan control.
- Phase 3 should split such files (or rename them with the hidden
  behaviour included, e.g. `airiq_profile_with_auto_fan.yaml`).
- New packages must declare control behaviour in the filename or
  refuse to include it.

### Rule 7 — Deprecated WebFlash tokens must not appear in **new** filenames

- The WebFlash contract §3 deprecated/forbidden token list
  (`Bathroom`, `Comfort`, `Presence`, generic `Fan`, `BathroomAirIQ`,
  `AirIQBase`, `AirIQPro`, `AirIQProv`, `FanAnalog`) **must not** be
  used in any newly added package filename.
- Existing files using deprecated tokens stay `legacy-compatible` so
  consumers keep working. Phase 2 wraps them under canonical aliases;
  Phase 5 retires them.

### Rule 8 — Compatibility shims live in the repo, never in customer YAML

- When a canonical alias is added (Phase 2), the canonical-name file
  `!include`s the legacy file and adds **no new substitutions or
  globals**. The legacy file remains the source-of-truth implementation
  until Phase 5.
- This way Release-One product YAMLs continue to work byte-identical,
  but new product YAMLs (Phase 3) can compose using canonical names.
- The shim file must contain a one-line comment pointing back at the
  legacy file so future readers know the canonical name is a wrapper.

## Migration plan

This is a multi-phase plan. **Only Phase 1 lands in this PR.** Each
later phase is its own scoped PR with its own evidence and tests.

### Phase 1 — Audit only (this PR)

- Add this document (`docs/package-naming-audit.md`).
- Add a `UPCOMING_PR.md` row under **Completed / merged PRs**
  recording `PACKAGE-NAMING-AUDIT-001 / PR #XXX` (placeholder until
  the PR number is known).
- **Do not** rename any file under `packages/**`.
- **Do not** create alias / wrapper files.
- **Do not** edit any product YAML, WebFlash wrapper, config JSON,
  test, script, workflow, component, include, firmware, manifest, or
  release artifact.
- **Do not** change `REQUIRED_CONFIGS`, `forbidden_tokens`,
  `canonical_modules`, `canonical_power`, or `lifecycle_statuses`.
- **Do not** promote `LED`, `AirIQ` / `VentIQ` / `RoomIQ`, fan modules,
  `PWR` / `S360-400`, or `POE` / `S360-410`.
- **Do not** claim hardware proof, WebFlash import readiness, or
  `RELEASE-007` unblock.

### Phase 2 — Add canonical aliases / wrapper packages

For every `candidate-for-alias` package, add a sibling canonical-name
file that `!include`s the legacy file and adds nothing else. Example
shape:

```yaml
# packages/expansions/ventiq.yaml (Phase 2 alias — DO NOT add new content)
# Canonical alias for the VentIQ bathroom IAQ module (S360-211).
# The legacy path packages/expansions/bathroom.yaml remains the
# implementation source. This alias lets new product YAMLs use the
# canonical name without breaking existing consumers.
packages:
  ventiq_legacy: !include bathroom.yaml
```

Each Phase-2 PR must:

- add the alias file only,
- be byte-identical-for-runtime (the alias `!include`s the legacy file
  with no new substitutions, globals, or YAML blocks),
- pass `python3 tests/validate_configs.py`,
- pass `python3 tests/validate_webflash_builds.py`,
- not change Release-One identity or the LED preview product,
- not flip `webflash_build_matrix`,
- not promote any module to stable.

Suggested Phase-2 alias inventory (initial, non-binding):

| Legacy filename                                                                  | Proposed Phase-2 alias                                              |
|----------------------------------------------------------------------------------|---------------------------------------------------------------------|
| `packages/expansions/airiq_bathroom_base.yaml`                                   | `packages/expansions/ventiq_base.yaml`                              |
| `packages/expansions/bathroom.yaml`                                              | `packages/expansions/ventiq.yaml`                                   |
| `packages/expansions/comfort_ceiling.yaml`                                       | `packages/expansions/roomiq_comfort_ceiling.yaml`                   |
| `packages/expansions/comfort_wall.yaml`                                          | `packages/expansions/roomiq_comfort_wall.yaml`                      |
| `packages/expansions/presence_ceiling.yaml`                                      | `packages/expansions/roomiq_presence_ceiling.yaml`                  |
| `packages/expansions/presence_wall.yaml`                                         | `packages/expansions/roomiq_presence_wall.yaml`                     |
| `packages/expansions/fan_gp8403.yaml`                                            | `packages/expansions/fan_dac.yaml`                                  |
| `packages/features/bathroom_profile.yaml`                                        | `packages/features/ventiq_profile.yaml`                             |
| `packages/features/comfort_basic_profile.yaml`                                   | `packages/features/roomiq_comfort_profile.yaml`                     |
| `packages/features/comfort_basic_profile_wall.yaml`                              | `packages/features/roomiq_comfort_profile_wall.yaml`                |
| `packages/features/presence_basic_profile.yaml`                                  | `packages/features/roomiq_presence_profile.yaml`                    |
| `packages/features/airiq_basic_profile.yaml`                                     | `packages/features/airiq_profile_base.yaml`                         |
| `packages/features/airiq_advanced_profile.yaml`                                  | `packages/features/airiq_profile_with_auto_fan.yaml` (renamed to reveal hidden behaviour) |

Phase 2 is **planning only** in this PR; the alias inventory is
non-binding and may be refined in the per-alias PRs.

#### Phase 2 progress — VentIQ aliases landed (2026-05-21)

`PACKAGE-NAMING-ALIASES-VENTIQ-001` is the first Phase 2 slice and
adds the four canonical `VentIQ` alias files listed below. Each
alias is a thin `!include` wrapper around the legacy implementation
file; the legacy file remains the source of truth and is not edited,
moved, renamed, or deleted. New product / compile-only YAMLs that
want to use the canonical productized `VentIQ` name may include any
of the alias files instead of the legacy filename; existing
consumers of the legacy paths continue to work unchanged.

| Canonical alias (added)                                       | Legacy implementation file (unchanged)                          |
|---------------------------------------------------------------|-----------------------------------------------------------------|
| [`packages/expansions/ventiq.yaml`](../packages/expansions/ventiq.yaml)                                   | [`packages/expansions/airiq_bathroom_base.yaml`](../packages/expansions/airiq_bathroom_base.yaml) |
| [`packages/expansions/ventiq_extended.yaml`](../packages/expansions/ventiq_extended.yaml)                 | [`packages/expansions/airiq_bathroom_pro.yaml`](../packages/expansions/airiq_bathroom_pro.yaml)  |
| [`packages/features/ventiq_profile.yaml`](../packages/features/ventiq_profile.yaml)                       | [`packages/features/bathroom_profile.yaml`](../packages/features/bathroom_profile.yaml)          |
| [`packages/features/ventiq_extended_profile.yaml`](../packages/features/ventiq_extended_profile.yaml)     | [`packages/features/bathroom_pro_profile.yaml`](../packages/features/bathroom_pro_profile.yaml)  |

Notes on the chosen alias names:

- The `_extended` suffix on `ventiq_extended.yaml` and
  `ventiq_extended_profile.yaml` is deliberately not `_pro`. Per
  Rule 5 above, a filename containing `pro` must not imply a
  productized Pro tier customer SKU unless that SKU exists in
  [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  and [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json),
  which is not the case today for any VentIQ Pro variant.
- The alias filenames carry no token listed in
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)'s
  `forbidden_tokens` (`Bathroom`, `Comfort`, `Presence`, generic
  `Fan`, `FanAnalog`). The pinning test
  [`tests/test_ventiq_alias_packages.py`](../tests/test_ventiq_alias_packages.py)
  enforces this.
- The alias for `packages/expansions/bathroom.yaml` (the legacy
  compatibility wrapper) is **not** added in this slice. The
  audit's non-binding Phase-2 inventory proposed
  `packages/expansions/ventiq.yaml` against `bathroom.yaml`; this
  slice instead points `ventiq.yaml` at the underlying
  `airiq_bathroom_base.yaml` hardware driver, which is the
  schematic-bound S360-211 module driver. A future Phase-2 slice may
  add an additional alias for `bathroom.yaml` if a consumer needs
  the hardware+profile combined entry point under a canonical name.
- The aliases for `airiq_bathroom_pro.yaml` and
  `bathroom_pro_profile.yaml` are included even though neither
  legacy file has a current product YAML consumer, because the
  `_extended` naming neutralizes the Pro-tier-implication concern
  flagged in the audit's per-area findings and the wrappers cost
  nothing at runtime (pure include shims).

The next Phase-2 slices (`roomiq_*`, `fan_dac.yaml`,
`airiq_profile_*`, etc.) are each their own scoped PR with their
own evidence and tests and are not landed here.

### Phase 3 — Update new compile-only / product YAMLs to canonical names

Once Phase-2 aliases exist:

- New compile-only target YAMLs added via the FW-COMPILE-EXPAND-001
  candidate ledger reference canonical names.
- New product YAMLs (post-Phase-2) reference canonical names.
- Existing Release-One / LED preview product YAMLs continue to
  reference legacy names (no rename in their `!include` paths).
- Phase 3 PRs do not modify any existing product YAML, do not modify
  any existing package YAML, and do not change runtime behavior.

### Phase 4 — Deprecate legacy names with comments

- Phase-4 PRs add a leading deprecation comment to each legacy
  filename pointing to the canonical alias, e.g.:

  ```yaml
  # DEPRECATED FILENAME — use packages/expansions/ventiq_base.yaml.
  # This file is retained for backwards compatibility with existing
  # product YAMLs and remote-package pinned URLs. The implementation
  # source remains here; the canonical alias is a `!include` wrapper.
  ```

- Phase-4 PRs do **not** change any YAML below the comment. They do
  not rename the file. They do not delete the file.

### Phase 5 — Remove legacy names only after all consumers are migrated

- The legacy filename is removed only when:
  - No `products/**` YAML `!include`s it.
  - No `products/webflash/**` wrapper `!include`s it.
  - No `packages/**` YAML `!include`s it.
  - No `docs/**` document references it as a path consumer (mentions
    in audit logs are acceptable).
  - The deprecation comment from Phase 4 has been in place for at
    least one published release tag (so external pinned consumers had
    a chance to migrate).
  - The matching PR carries a `release notes` entry calling out the
    removal as a breaking change for any external consumer pinning
    the legacy path.

- Phase-5 deletion PRs run the full validation sweep (see
  [Validation results](#validation-results)) and re-run
  `python3 tests/validate_configs.py` and
  `python3 tests/validate_webflash_builds.py` to confirm no remaining
  consumer.

## Hard guardrails

This audit must not, directly or via any follow-up action documented
herein:

- rename, move, or delete any file under `packages/**`,
- change runtime YAML behavior of any package,
- add a compile-only target to
  [`config/compile-only-targets.json`](../config/compile-only-targets.json),
- add a candidate to
  [`config/compile-only-candidates.json`](../config/compile-only-candidates.json),
- add or modify a product under `products/**`,
- add or modify a WebFlash wrapper under `products/webflash/**`,
- modify `packages/**`,
- modify `firmware/**`,
- modify `manifest.json` or `firmware/sources.json`,
- modify `.github/workflows/**`,
- emit, attach, or modify any release artifact, checksum, or
  build-info manifest,
- add `webflash_build_matrix: true` to any product,
- add `artifact_name` to any product,
- promote `LED` to `stable`,
- promote `AirIQ` / `VentIQ` / `RoomIQ`,
- promote fan modules,
- promote `PWR` / `S360-400`,
- promote `POE` / `S360-410`,
- claim hardware proof exists,
- claim WebFlash import readiness,
- claim `RELEASE-007` is unblocked,
- change `REQUIRED_CONFIGS`, `forbidden_tokens`, `canonical_modules`,
  `canonical_power`, `lifecycle_statuses`, or
  `release_one_required_configs`,
- change [`config/webflash-builds.json`](../config/webflash-builds.json),
  [`config/product-catalog.json`](../config/product-catalog.json),
  [`config/hardware-catalog.json`](../config/hardware-catalog.json),
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
  [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json),
  or [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json),
- change [`docs/webflash-contract.md`](webflash-contract.md) (this
  audit consumes the contract; it does not edit it),
- change [`docs/release-one.md`](release-one.md) Release-One identity,
- change Release-One FanTRIAC `blocked` status or the Release-One
  LED-exclusion status,
- modify `tests/**` test files,
- modify `scripts/**` scripts.

The audit is **planning ledger confidence only**. Each Phase 2–5 PR
must carry its own evidence and gate review.

## Validation results

The audit text is documentation only; the runtime YAML, the WebFlash
build matrix, the product catalog, the hardware catalog, the
firmware combination matrix, the kit-intent matrix, the compile-only
target list, and the compile-only candidate ledger are byte-identical
before and after this PR.

The following validations were run to confirm no regression:

```sh
python3 scripts/generate_firmware_matrix.py --check
python3 scripts/report_firmware_build_gaps.py --check
python3 scripts/validate_compile_targets.py --metadata-only
python3 tests/test_compile_targets.py
python3 tests/test_firmware_combination_matrix.py
python3 tests/test_firmware_build_gap_report.py
python3 tests/test_kit_intent_matrix.py
python3 tests/test_compile_expansion_candidates.py
python3 tests/validate_webflash_builds.py
python3 tests/validate_configs.py
python3 -m unittest discover -s tests -p "test_*.py"
```

All commands pass with the runtime YAML byte-identical to the
pre-audit state. No new tests are added for this PR — the existing
docs/index/link-check tooling has no pattern to extend for prose-only
documentation, and per the audit task, tests are not invented for
prose alone.

## See also

- [`docs/webflash-contract.md`](webflash-contract.md) — canonical
  WebFlash token list and deprecated/forbidden token list.
- [`docs/release-one.md`](release-one.md) — Release-One identity.
- [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)
  — Release-One firmware-vs-schematic audit and Sense360 LED policy.
- [`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
  — HW-009 per-package schematic-vs-firmware reconciliation.
- [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
  — PACKAGE-GAP-001 per-package readiness.
- [`docs/cleanup-audit.md`](cleanup-audit.md) — repo-wide cleanup audit.
- [`docs/kit-intent-matrix.md`](kit-intent-matrix.md) — productized
  kit / bundle intent.
- [`docs/compile-only-expansion-candidates.md`](compile-only-expansion-candidates.md)
  — FW-COMPILE-EXPAND-001 candidate ledger.
- [`packages/README.md`](../packages/README.md) and
  [`packages/SENSE360_MODULES.md`](../packages/SENSE360_MODULES.md) —
  legacy package surface documentation.

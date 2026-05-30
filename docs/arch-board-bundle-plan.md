# Board-package & bundle-YAML architecture plan (ARCH-BOARD-BUNDLE-PLAN-001)

> **Status: planning only — no code, config, workflow, product, package, or
> firmware change.** This document is the canonical target-shape decision for
> restructuring the firmware YAML into SKU-aligned **board packages** plus
> product-named **bundle YAMLs**. It defines the rename and
> backward-compatibility policy, maps the CI and docs impact across both
> repositories, and emits the ordered PR sequence that implements it. Every
> code, config, and workflow file stays byte-identical under this PR.
>
> Cross-references the canonical Core connector pin map
> [`docs/hardware/s360-100-core-connector-pin-map.md`](hardware/s360-100-core-connector-pin-map.md)
> and the roadmap/status snapshot
> [`docs/sense360-roadmap-status.md`](sense360-roadmap-status.md). The detailed
> per-PR queue state for the epic emitted here lives in
> [`UPCOMING_PR.md`](../UPCOMING_PR.md).

## 1. Problem statement and current model (verified)

The firmware YAML is today a **four-tier functional composition**:

| Tier | Directory | Holds | Examples |
|------|-----------|-------|----------|
| Base | `packages/base/` | wifi, api, ota, time, logging, external_components, bluetooth_proxy, complete | `wifi.yaml`, `api_encrypted.yaml`, `external_components.yaml` |
| Hardware | `packages/hardware/` | `sense360_core*` (split by mount/power), `power_*`, `led_ring_*`, `presence_*` radar | `sense360_core_ceiling.yaml`, `power_poe.yaml`, `led_ring_ceiling.yaml` |
| Expansions | `packages/expansions/` | airiq, roomiq, ventiq, comfort, presence, bathroom, `fan_*` | `airiq_ceiling.yaml`, `comfort_ceiling.yaml`, `fan_gp8403.yaml` |
| Features | `packages/features/` | `*_profile`, diagnostics, device_health | `bathroom_profile.yaml`, `device_health.yaml` |

Products in `products/` assemble these tiers through a `packages:` include
block (see the Release-One target
[`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml)).

**The naming gap.** The catalog speaks **SKUs** — `S360-100`, `S360-200`,
`S360-210`, `S360-211`, `S360-300`, `S360-310`, `S360-311`, `S360-312`,
`S360-320`, `S360-400`, `S360-410` (see
[`config/hardware-catalog.json`](../config/hardware-catalog.json) /
[`docs/hardware-catalog.md`](hardware-catalog.md)). The YAML speaks
**functional names** (`comfort_ceiling`, `presence_ceiling`, `fan_gp8403`).
The only bridge between the two is product-header comments. A reader cannot
look at `packages/` and see which physical board owns which file.

**Target.** A `packages/boards/` layer with **one canonical package per board
SKU** that owns the board's chip / pin map / connector nets, and a **bundle
layer** of product-named YAMLs aligned 1:1 to the catalog config strings, each
of which assembles `boards + expansions + base + profiles`. Functional/legacy
package names are retired into SKU-aligned names where every consumer can be
rebound, and retained as aliases where legacy-compatible products still bind
them.

## 2. Target layout

### 2.1 Board layer — `packages/boards/`

One canonical package per board SKU. The Core package owns the ESP32-S3 chip
definition, the schematic pin map, and the single shared `core_i2c` bus
(`GPIO48`/`GPIO45` @ `400 kHz`, per CORE-ABSTRACT-BUS-001B). Sensor/driver
board packages own their connector nets, I²C addresses, and UART bindings on
that shared bus — they do **not** redefine the chip or the bus.

| Board SKU | Board (friendly) | Group / class | Target board package | Folds in (current source packages) | Shippable? |
|-----------|------------------|---------------|----------------------|-------------------------------------|------------|
| `S360-100` | Sense360 Core | Ceiling Hub (ESP32-S3) | `packages/boards/s360-100-core.yaml` (+ mount/power/voice variant overlays) | `sense360_core.yaml`, `sense360_core_ceiling.yaml`, `sense360_core_wall.yaml`, `sense360_core_poe.yaml`, `sense360_core_voice*.yaml`, `sense360_core_ceiling_s3.yaml`, `sense360_core_mapping.yaml` (reference) | yes |
| `S360-200` | Sense360 RoomIQ | Ceiling Sensor (merged) | `packages/boards/s360-200-roomiq.yaml` | `presence_ceiling.yaml`, `presence_wall.yaml`, `comfort_ceiling.yaml`, `comfort_wall.yaml`, `presence_ld2450.yaml`, `presence_ld2412.yaml`, `roomiq*.yaml` | yes |
| `S360-210` | Sense360 AirIQ | Ceiling Sensor | `packages/boards/s360-210-airiq.yaml` | `airiq_ceiling.yaml`, `airiq_wall.yaml`, `airiq.yaml`, `airiq_ceiling_s3.yaml` | yes |
| `S360-211` | Sense360 VentIQ | Ceiling Sensor (bath) | `packages/boards/s360-211-ventiq.yaml` | `airiq_bathroom_base.yaml`, `airiq_bathroom_pro.yaml`, `bathroom.yaml`, `ventiq*.yaml` | yes |
| `S360-300` | Sense360 LED | Indicator (WS2812B ring) | `packages/boards/s360-300-led.yaml` (+ mic/voice variant) | `led_ring_ceiling.yaml`, `led_ring_wall.yaml`, `led_ring_mic_ceiling.yaml`, `led_ring_mic_wall.yaml`, `ceiling_halo_leds.yaml` (feature) | yes (preview-gated) |
| `S360-410` | Sense360 PoE PSU | Power | `packages/boards/s360-410-poe-psu.yaml` | `power_poe.yaml` | yes |
| `S360-310` | Sense360 Relay | Inline Driver (mains load) | `packages/boards/s360-310-relay.yaml` | `fan_relay.yaml` | **open-source-only** |
| `S360-320` | Sense360 TRIAC | Inline Driver (mains dimmer) | `packages/boards/s360-320-triac.yaml` | `fan_triac.yaml` | **open-source-only** |
| `S360-400` | Sense360 240V PSU | Power (mains) | `packages/boards/s360-400-mains-psu.yaml` | `power_240v.yaml` | **open-source-only** |

**Open-source-only** means the board package exists and compiles, but is not
exposed as a WebFlash stable build and carries no `config/webflash-builds.json`
row. This preserves the existing posture for mains-voltage hardware
(`S360-320` TRIAC is blocked per HW-005; `S360-400`/`S360-310` mains work is
compliance-gated — see
[`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)).

> **First-cut board layer — COMPLETE (2026-05-30).** The first-cut
> `packages/boards/` layer is the **six SELV / low-voltage SKUs**: Core
> (`S360-100`, BOARD-PACKAGE-LAYER-001) plus the five sensor/PSU boards
> `S360-200` RoomIQ, `S360-210` AirIQ, `S360-211` VentIQ, `S360-300` LED, and
> `S360-410` PoE PSU (BOARD-PACKAGE-LAYER-002). Each is authored as a thin
> `!include` wrapper (base package + mount/variant overlays) over the existing
> functional source package(s), so behaviour is byte-identical and every
> product / test keeps resolving unchanged; the legacy paths are preserved as
> source-of-truth aliases (§3.3, §5.5) and are **not** rewired to one-line
> includes in this slice (the consumer-side flip + test repoint travels with a
> later PACKAGE-RENAME slice / CI-REFACTOR-VERIFY-001, because
> `tests/test_core_abstract_bus.py` and `tests/test_led_package_mapping.py`
> assert on the self-contained text of the folded functional packages). *(The
> LED family has since been flipped by **PACKAGE-RENAME-001** (§7 item 4): the
> `s360-300-led*` board packages are now authoritative and the `led_ring_*`
> paths are thin aliases, with both named tests repointed onto the board
> package. The **AirIQ** family (S360-210) has likewise been flipped by
> **PACKAGE-RENAME-002**: the `s360-210-airiq` / `-wall` / `-ceiling-s3` board
> packages are now authoritative and the `airiq_ceiling` / `airiq_wall` /
> `airiq_ceiling_s3` paths are thin aliases, with the `test_core_abstract_bus.py`
> AirIQ assertions repointed (the generic base driver `airiq.yaml` stays a
> cross-referenced, un-folded driver). The remaining families flip in later
> PACKAGE-RENAME slices.)* The
> **mains boards `S360-310` / `S360-320` / `S360-400` remain OUT of the board
> layer for now** (compliance-gated, deferred to a later slice), and
> `S360-311` / `S360-312` stay expansions behind their evidence gates (below).
> The next phase is **BUNDLE-LAYER-001**.

#### Deferred board promotions — `S360-311`, `S360-312`

The task's canonical board enumeration is `S360-100, 200, 210, 211, 300, 410`
plus the mains `310/320/400`. The two **low-voltage (SELV) fan-driver SKUs**,
`S360-311` (PWM, `fan_pwm.yaml` / `fan_pwm_sx1509.yaml` / `fan_pwm_native.yaml`)
and `S360-312` (DAC, `fan_gp8403.yaml` / `fan_dac.yaml`), are deliberately
**not** promoted to `packages/boards/` in the first cut. Both are
`schematic_status: cataloged_unverified` in
[`config/hardware-catalog.json`](../config/hardware-catalog.json) and both are
blocked behind their own per-board evidence gates
(`HW-PINMAP-311-FOLLOWUP` / `HW-PINMAP-312-FOLLOWUP`) in the queue. They remain
**expansion packages** until those follow-ups close; their board-package
promotion is assigned to a later `PACKAGE-RENAME-00x` slice (see §7), gated on
the same evidence that already gates their product layer. This is recorded as
an open decision, not silently resolved.

### 2.2 Bundle layer — product-named YAMLs aligned 1:1 to config strings

The bundle layer holds one YAML per **catalog config string** (the seven
config-string products in [`config/product-catalog.json`](../config/product-catalog.json)).
Each bundle assembles `boards + expansions + base + profiles`. The config
string and artifact name are the stable WebFlash contract; the bundle file is
named to match it 1:1.

| Config string | Catalog status | Bundle YAML (target) | Boards assembled |
|---------------|----------------|----------------------|------------------|
| `Ceiling-POE-VentIQ-RoomIQ` | production / stable | `bundles/ceiling-poe-ventiq-roomiq.yaml` | `S360-100` + `S360-410` + `S360-211` + `S360-200` |
| `Ceiling-POE-VentIQ-RoomIQ-LED` | preview | `bundles/ceiling-poe-ventiq-roomiq-led.yaml` | + `S360-300` |
| `Ceiling-POE-VentIQ-FanRelay-RoomIQ` | hardware-pending | `bundles/ceiling-poe-ventiq-fanrelay-roomiq.yaml` | + `S360-310` |
| `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` | blocked (HW-005) | `bundles/ceiling-poe-ventiq-fantriac-roomiq.yaml` | + `S360-320` |
| `Ceiling-POE-FanDAC` | hardware-pending | `bundles/ceiling-poe-fandac.yaml` | `S360-100` + `S360-410` + `S360-312` |
| `Ceiling-POE-FanPWM` | hardware-pending | `bundles/ceiling-poe-fanpwm.yaml` | `S360-100` + `S360-410` + `S360-311` |
| `Ceiling-POE-RoomIQ` | blocked (PRODUCT-POE-410-001) | `bundles/ceiling-poe-roomiq.yaml` | `S360-100` + `S360-410` + `S360-200` |

The exact bundle directory (`bundles/` vs `products/bundles/`) is settled by
BUNDLE-LAYER-001 against the CI globs in §5; the placement constraint is that
it must remain discoverable by the existing `find products/` sweeps **or** the
sweeps are extended in the same slice. The default proposal is
`products/bundles/` so the unchanged `find products/ -name "*.yaml"`
discovery in `validate.yml` / `ci-validate-configs.yml` keeps finding them
without a workflow edit (see §5).

> **Settled (BUNDLE-LAYER-001, 2026-05-30): `products/bundles/`.** The bundle
> directory is `products/bundles/`, so the recursive `find products/` sweeps and
> the `PRODUCTS_DIR.rglob` walkers (e.g. `scripts/classify_all_yaml_release_matrix.py`,
> `tests/validate_configs.py`) discover bundles with **no** workflow or glob
> edit; the catalog enumeration test stays scoped to top-level files
> (`tests/test_product_catalog.py` uses `PRODUCTS_DIR.iterdir()`, which skips the
> `bundles/` subdirectory), so bundles need no catalog row. The first two
> config-string bundles (the WebFlash-shipping production + preview pair) land in
> BUNDLE-LAYER-001; the remaining five land in BUNDLE-LAYER-002 (§7 item 3 / 3a).

### 2.3 What does **not** move

- `packages/base/**` — base system tier is functional, not board-bound. It
  stays as-is and is included by bundles unchanged.
- `packages/features/**` — `*_profile`, `diagnostics`, `device_health` are
  behaviour profiles layered on top of boards; they stay in the features tier.
  (`ceiling_halo_leds.yaml` is the one feature with a board-hardware identity
  and is cross-referenced from the `S360-300` board package.)
- `power_usb.yaml` — USB-C power is **Core-native**, not a separate board SKU;
  it stays a power-config helper, not a board package.
- All catalog JSON, all `products/webflash/**` wrappers, all
  `config/webflash-builds.json` entries — these are the stable contract layer
  (§3).

## 3. Compatibility policy (explicit)

Three independent contracts are held stable. None may break in any slice of
this epic.

### 3.1 WebFlash contract — config strings & artifact names HELD STABLE

WebFlash couples to esphome-public **only** through GitHub release tags,
`config_string` values, and `artifact_name` values — confirmed read-only
against `WebFlash/firmware/sources.json`, `WebFlash/manifest.json`, and
`WebFlash/scripts/data/`. **No** WebFlash file references any esphome-public
`packages/` or `products/` path. Therefore:

- Every existing config string (`Ceiling-POE-VentIQ-RoomIQ`,
  `Ceiling-POE-VentIQ-RoomIQ-LED`, …) stays byte-identical.
- Every artifact name (`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`,
  …) stays byte-identical.
- `config/webflash-builds.json`, `manifest.json`, and `firmware/sources.json`
  are **not** touched by any rename slice.

Because the build matrix is driven by `config/webflash-builds.json` (which
points at `product_yaml` paths), and because those paths are preserved as
compat shims (§3.2), the rename is **invisible to WebFlash**.

### 3.2 Customer include contract — renamed product files keep a compat shim

Customers pin a release tag and `!include` a `products/sense360-*.yaml` path
in their own ESPHome config (the header of every product YAML documents this;
e.g. `files: - products/sense360-ceiling-poe-ventiq-roomiq.yaml`, `ref: v1.0.0`).

Policy: **the old product path is never deleted.** When a product's
composition moves into a bundle YAML, the old `products/sense360-*.yaml` path
is retained as a **thin compat shim** that does nothing but
`!include` the new bundle:

```yaml
# products/sense360-ceiling-poe-ventiq-roomiq.yaml  (compat shim, v1.0.0 pinned)
packages:
  bundle: !include bundles/ceiling-poe-ventiq-roomiq.yaml
```

This is the same wrapper pattern already proven by
`products/webflash/ceiling-poe-ventiq-roomiq.yaml`, which re-exports the
canonical product via `!include ../sense360-ceiling-poe-ventiq-roomiq.yaml`.
A customer who pinned `v1.0.0` is unaffected (the v1.0.0 tag is immutable); a
customer who follows `main` gets the same resolved config through the shim.

### 3.3 Legacy package aliases — retained until their products are removed

Many legacy/functional package names are still bound by `legacy-compatible`
products under `products/` (the ~20 `sense360-core-*` files with no config
string). Verified bindings (include counts across `products/`):
`presence_ceiling.yaml` ×23, `airiq_ceiling.yaml` ×16, `comfort_ceiling.yaml`
×15, `presence_wall.yaml` ×15, `airiq_wall.yaml` ×14, `comfort_wall.yaml` ×8,
plus the `fan_*` family.

Policy: when a board package is introduced, the **legacy package name is
retained as an alias** (a thin `!include` of the new board package, or a kept
filename) **until every product that binds it is removed or rebound.** Legacy
products are removed by the existing queue items `PRODUCT-DEP-CORE-001`
(non-Mini legacy range) and the already-completed `PRODUCT-DEP-MINI-001`. No
alias is dropped while a live binder exists. Alias removal is a separate,
later slice gated on the binder count reaching zero.

### 3.4 Summary table

| Contract | Surface | Policy | Owner slice |
|----------|---------|--------|-------------|
| WebFlash | config strings, artifact names, `webflash-builds.json`, `manifest.json`, `sources.json` | byte-identical, never touched | all slices (guardrail) |
| Customer include | `products/sense360-*.yaml` paths | retained as compat shim → new bundle | BUNDLE-LAYER-001 |
| Legacy packages | `packages/expansions/*`, `packages/hardware/*` legacy names | aliased until binder count = 0 | PACKAGE-RENAME-00x |

## 4. Core chip drift — recorded and assigned

A real discrepancy exists in the Core definitions and must be resolved against
the verified `S360-100-R4` schematic **as the first act of
BOARD-PACKAGE-LAYER-001**, before any board package is authored.

### 4.1 Flash / PSRAM drift (8 MB / 2 MB vs 16 MB / 8 MB)

| File | Chip comment | `board:` | `flash_size` | PSRAM |
|------|--------------|----------|--------------|-------|
| `packages/hardware/sense360_core.yaml` | `ESP32-S3-WROOM-1 (8MB Flash, 2MB PSRAM)` | `esp32-s3-devkitc-1` | *(unset)* | `SPIRAM_SUPPORT` + `MODE_OCT` only |
| `packages/hardware/sense360_core_ceiling.yaml` | `8MB Flash, 2MB PSRAM` | `esp32-s3-devkitc-1` | *(unset)* | same |
| `packages/hardware/sense360_core_wall.yaml` | `8MB Flash, 2MB PSRAM` | `esp32-s3-devkitc-1` | *(unset)* | same |
| `packages/hardware/sense360_core_poe.yaml` | `8MB Flash, 2MB PSRAM` | `esp32-s3-devkitc-1` | *(unset)* | same |
| `packages/hardware/sense360_core_mapping.yaml` | `ESP32-S3-WROOM-1-N16R8 (16MB Flash, 8MB PSRAM)` | `esp32-s3-devkitc-1` | **`16MB`** | `mode: octal` + `speed: 80MHz` + `SPIRAM_SPEED_80M` |

The **product-bound** core packages (`*_ceiling`, `*_wall`, `*_poe` — these
are the ones products actually `!include`) all say **8 MB / 2 MB**. The
**16 MB / 8 MB N16R8** value lives only in `sense360_core_mapping.yaml`, which
**no product includes** (it is referenced only as a pin-map reference by
`packages/expansions/fan_pwm_sx1509.yaml` and by three tests:
`test_core_abstract_bus.py`, `test_fan_relay_package.py`,
`test_relay_pinmap_reconcile.py`).

**Resolution assigned to BOARD-PACKAGE-LAYER-001:** reconcile the chip variant
(flash size + PSRAM size/speed + `flash_size` key) against the verified
`docs/hardware/schematics/S360-100-R4.pdf` and the canonical pin-map doc, pick
**one** authoritative value, and bake it into the single
`packages/boards/s360-100-core.yaml`. This plan does **not** pre-decide the
value — that is an evidence call owned by that PR.

### 4.2 Fan-pin / RoomIQ-UART collision (GPIO4 / GPIO5)

`sense360_core_mapping.yaml` assigns `fan_pwm_pin: GPIO4` and
`fan_tach_pin: GPIO5`, while the **same file** and `sense360_core.yaml` assign
the RoomIQ SEN0609 radar UART to `tx_pin: GPIO5` / `rx_pin: GPIO4`
(`roomiq_sen0609_uart`). GPIO4/GPIO5 are therefore double-claimed: native fan
PWM/tach **vs** the RoomIQ J10 DFRobot radar UART. This is consistent with the
known native-fan-vs-radar contention already tracked in
[`docs/hardware/s360-100-native-fan-gpio-map.md`](hardware/s360-100-native-fan-gpio-map.md).

**Resolution assigned to BOARD-PACKAGE-LAYER-001 (first act):** record which
function owns GPIO4/GPIO5 on the canonical Core board package against the
schematic, and ensure the board package cannot simultaneously expose both the
SEN0609 UART and native fan PWM/tach on those pins. No pin value is changed by
this planning PR.

### 4.3 Resolution (BOARD-PACKAGE-LAYER-001 — Core, 2026-05-30)

**Chip variant — RESOLVED to `ESP32-S3-WROOM-1-N16R8` (16 MB flash / 8 MB
octal-SPI PSRAM @ 80 MHz).** The schematic and the BOM **agree**, so the
chip-definition step proceeds (no conflict to flag):

- Schematic [`docs/hardware/schematics/S360-100-R4.pdf`](hardware/schematics/S360-100-R4.pdf)
  (SHA256 `4c9e8b06d129fbb55f61e143b648e03762d06cb4dc67fe3120c268cd3a4bdf16`,
  837,443 bytes, KiCad E.D.A. 10.0.3) — component **U6** is the
  `ESP32-S3-WROOM-1-N16R8` module; `IO35`/`IO36`/`IO37` reserved for on-module
  octal-SPI PSRAM (transcribed in
  [`docs/hardware/s360-100-r4-core.md`](hardware/s360-100-r4-core.md)
  §"Main components" / §"ESP32-S3 pin and net mapping").
- BOM `bc386261-S360100R4_BOM.xlsx`
  (SHA256 `e289f135a2c88dd747689c70075e2f1cf49906f4bda8b4c4abad67d0dad961fc`),
  U6 module, per
  [`docs/hardware/artifacts/S360-100-R4.md`](hardware/artifacts/S360-100-R4.md)
  §"Board identity".

The drifted product-bound packages (`sense360_core.yaml`,
`sense360_core_ceiling.yaml`, `sense360_core_wall.yaml`,
`sense360_core_poe.yaml`) are raised from 8 MB / 2 MB to the N16R8 value
(`flash_size: 16MB` + `psram: { mode: octal, speed: 80MHz }`), matching the
value already carried by `sense360_core_mapping.yaml` and the voice / S3
variants, and the canonical value is baked into
`packages/boards/s360-100-core.yaml`.

**GPIO4/GPIO5 — RESOLVED: RoomIQ SEN0609 radar UART owns IO4/IO5.** Schematic
`IO4 = SEN0609_RX`, `IO5 = SEN0609_TX`. The canonical Core board package binds
GPIO4/GPIO5 only to `roomiq_sen0609_uart` and does **not** expose native fan
PWM/tach on those pins; native fan tach/PWM terminate on dedicated GPIOs
(`TachIO = IO16`; `Pul_Cou1..4 = IO17/IO18/IO46/IO9`;
`TachPMW1..4 = IO10/IO11/IO12/IO39`). The legacy `fan_pwm_pin: GPIO4` /
`fan_tach_pin: GPIO5` in `sense360_core_mapping.yaml` (no product includes it)
is left untouched as a legacy reference and is not reproduced in the canonical
board package.

## 5. CI impact

Every workflow glob, `find`, and `sed` that a rename or new directory touches,
with the change each needs. Verified against the four workflows.

### 5.1 `ci-validate-configs.yml` (manual broad/legacy sweep — not a PR gate)

| Line / step | Construct | Touched by | Required change |
|-------------|-----------|------------|-----------------|
| `discover-products` | `find products/ -name "*.yaml" -type f ! -name "secrets.yaml" ! -path "products/webflash/*"` | new `products/bundles/` auto-discovered; compat shims still discovered | **none** if bundles live under `products/`; the recursive `find` already covers subdirs. If bundles live outside `products/`, add the bundle dir to the `find`. |
| `validate-yaml` | `yamllint -c .yamllint products/ packages/` | dir-level lint | **none** — covers new `packages/boards/` and `products/bundles/` automatically |
| `test-all-products` / `test-generated-configs` | `sed -i "s\|ref: main\|ref: $BRANCH\|g" packages/base/external_components.yaml` | hard-coded path; **not** renamed | **none** — `external_components.yaml` is base tier, untouched by this epic |
| same | `find packages/features -name "*.yaml" -exec sed -i "s\|@main\|@$BRANCH\|g" {} \;` | hard-coded `packages/features` dir; **not** renamed | **none** — features tier untouched |

### 5.2 `compile-only.yml` (pre-hardware compile lane)

| Step | Construct | Touched by | Required change |
|------|-----------|------------|-----------------|
| metadata-validate | driven by `config/compile-only-targets.json` + `scripts/validate_compile_targets.py` + `tests/test_compile_targets.py` | targets reference `products/webflash/*` and `products/compile-only/*` paths | **none** for the rename itself (those paths are preserved). If a bundle is added as a new compile-only target, add its row to `config/compile-only-targets.json` in that slice — **not** in this epic's scope unless a bundle needs a compile target. |
| full-compile | provisions `secrets.yaml` into `products/`, `products/webflash/`, `products/compile-only/` (hard-coded) | hard-coded secret dirs | if compile-only targets are added under a **new** bundle dir, provision `secrets.yaml` there too. Otherwise **none**. |

### 5.3 `validate.yml` (the PR gate) — behaviour preserved

| Line | Construct | Touched by | Required change |
|------|-----------|------------|-----------------|
| 94 | `PRODUCT_COUNT=$(find products/ -name "*.yaml" -type f ! -name "secrets.yaml" \| wc -l)` | informational count only; bundles + shims change the number | **none** — the count is reported, not asserted against a fixed value |
| 95 | `PACKAGE_COUNT=$(find packages/ -name "*.yaml" -type f \| wc -l)` | informational count only | **none** |
| 50–90 | runs `validate_configs.py`, `test_product_substitutions.py`, `test_release_one_entity_names.py`, `validate_webflash_builds.py`, `test_webflash_artifact_naming.py`, `test_product_catalog.py`, `test_product_catalog_consistency.py`, … | these tests hard-code product paths and walk `products/` (see §5.5) | tests update **with** the slice that renames the files they assert on; the gate scripts themselves are unchanged. |

**Gate behaviour is preserved:** `validate.yml` gates on the test scripts'
pass/fail, not on directory shape. As long as each rename slice updates the
tests in the same PR (CI-REFACTOR-VERIFY-001 enforces this), the gate keeps its
exact semantics: Release-One substitutions, entity names, WebFlash build
validity, artifact naming, and catalog consistency.

### 5.4 `firmware-build-release.yml` (release gate) — behaviour preserved

This workflow is **config-string-driven, not glob-driven**. Verified couplings:

- It enumerates release targets from `config/webflash-builds.json` (not from a
  `find products/` scan — the old broad scan was explicitly replaced, see the
  in-file comment at line ~185).
- For a `products/webflash/*` wrapper entry it compiles the canonical
  `products/sense360-<stem>.yaml` instead (line ~254).
- It rewrites `packages/base/external_components.yaml` to a local source (base
  tier — untouched by this epic).
- It greps `packages/base products` for `type: git` external_components.

**Required change: none for the rename**, provided the compat shims at
`products/sense360-*.yaml` are retained (§3.2) so the
`products/webflash/* → products/sense360-<stem>.yaml` resolution and the
`webflash-builds.json` `product_yaml` paths still hit real files. The release
gate's behaviour — which config strings build, what they are named, what gets
tagged — is therefore **preserved unchanged**.

### 5.5 Tests that move with their slice (not workflow changes, but CI-blocking)

Inventory verified: **~19 test files reference `packages/`** and **~26
reference `products/`**. The ones that will break on a rename, and so must be
updated in the same slice:

- **Directory walkers:** `tests/validate_configs.py` (hard-coded
  `config_dirs` list incl. `products`, `packages`, `hardware`, `features` +
  `rglob`), `tests/test_product_catalog.py` (`PRODUCTS_DIR.iterdir()`,
  `WEBFLASH_WRAPPER_DIR.glob`), `tests/test_all_yaml_release_matrix.py`
  (`PRODUCTS_DIR.rglob`), `tests/test_compile_expansion_candidates.py`
  (`startswith("products/")`).
- **Generated includes:** `tests/generate_test_configs.py` emits
  `../../packages/base/…`, `../../packages/hardware/{core}.yaml`,
  `../../packages/expansions/{module}.yaml` — these strings change with the
  board rename.
- **Hard-coded product/package path constants:** `test_relay_product_readiness.py`,
  `test_pwm_product_readiness.py`, `test_dac_product_readiness.py`,
  `test_native_fan_gpio_map.py`, `test_native_fanpwm_yaml.py`,
  `test_plan_room_release_notes.py`, `test_relay_pinmap_reconcile.py`,
  `test_firmware_combination_matrix.py`, `test_manual_firmware_artifacts.py`,
  `test_led_package_mapping.py`, `test_core_abstract_bus.py`,
  `test_fan_relay_package.py`, `test_fandac_package.py`,
  `test_fan_pwm_package.py`, plus the `*_alias_packages.py` family that asserts
  the `packages/**` subdirectory comment convention.

`tests/test_roadmap_status_doc.py` has **no** `packages/` or `products/`
coupling and is unaffected by the rename.

## 6. Docs impact

Every doc that must update, in both repos.

### 6.1 esphome-public

| Doc | Why it updates |
|-----|----------------|
| [`docs/system-architecture.md`](system-architecture.md) | Describes the repo boundary and product→release→WebFlash flow; add the board/bundle layer to the architecture picture. |
| [`docs/ci-pipeline.md`](ci-pipeline.md) | Per-workflow classification; record the §5 findings (which globs/seds are/are not touched, gate-preservation). |
| [`packages/SENSE360_MODULES.md`](../packages/SENSE360_MODULES.md) | Legacy module inventory; add the SKU→board-package map and the alias-retention note. |
| [`packages/README.md`](../packages/README.md) | Documents the four-tier layout and the legacy→WebFlash-token map; add the `packages/boards/` tier and the bundle layer. |
| [`README.md`](../README.md) | Top-level entry point; document the board-package + bundle model as the third configuration approach. |
| [`docs/hardware-catalog.md`](hardware-catalog.md) | SKU source-of-truth; cross-link each SKU to its board package. |
| [`docs/product-matrix.md`](product-matrix.md) | Module/SKU + profile reference; align with the bundle layer. |
| [`docs/sense360-room-bundles.md`](sense360-room-bundles.md) | Already distinguishes bundle SKU ≠ board SKU ≠ artifact name; cross-link the YAML bundle layer to `config/room-bundle-skus.json`. |
| [`docs/sense360-roadmap-status.md`](sense360-roadmap-status.md) | Canonical roadmap snapshot; add the epic (DOCS-ARCH-REFRESH-001 owns this edit). |

The DOCS-ARCH-REFRESH-001 slice owns these edits; they are **not** made by this
planning PR (which adds only this doc + the queue).

### 6.2 WebFlash (read-only confirmation; one doc updates)

| Doc | Why it updates |
|-----|----------------|
| `WebFlash/docs/architecture.md` | Describes the two-halves model and that `manifest.json` is the only bridge. It must record that an esphome-public board/bundle rename leaves the WebFlash contract unchanged (config strings + artifact names + release tags only). |
| `WebFlash/docs/firmware-import.md` | Importer contract (tags, asset names, SHA256, `config_string` match). A confirmation note that no esphome YAML path is consumed. |

The WebFlash edit is owned by **WEBFLASH-ARCH-SYNC-001** in the WebFlash repo.
This planning PR touches **no** WebFlash file.

## 7. Ordered PR sequence (the epic)

Each slice is small, independently reviewable, and keeps every contract in §3
intact. Dependencies are strict: a slice does not start until its predecessor
merges and CI is green.

1. **ARCH-BOARD-BUNDLE-PLAN-001** *(this PR — docs only)*
   - Scope: this document + the queue entries below.
   - Guardrails: no code/config/workflow/product/package/test/firmware change.
   - Dependency: none.

2. **BOARD-PACKAGE-LAYER-001** — introduce `packages/boards/` (Core first)
   - **Status: in progress — Core done (2026-05-30).** The §4 chip drift is
     resolved (see §4.4) and the canonical Core board layer is authored:
     `packages/boards/s360-100-core.yaml` (base) plus the mount/power/voice
     variant overlays `s360-100-core-{ceiling,wall,poe,voice-ceiling,voice-wall,ceiling-s3}.yaml`,
     each a thin `!include` wrapper over the corresponding existing functional
     `packages/hardware/sense360_core*.yaml` package (behaviour byte-identical).
     The legacy paths are retained unchanged as source-of-truth aliases (§3.3
     "kept filename") so every existing product and test keeps resolving; they
     are **not** rewired to one-line includes in this slice because
     `tests/test_core_abstract_bus.py` asserts on the self-contained text of
     each `sense360_core*.yaml` and the slice keeps every test green
     (CI-REFACTOR-VERIFY-001 / §5.5 owns the source-of-truth flip + test
     repoint in a later PACKAGE-RENAME slice). The remaining board SKUs
     (`s360-200/210/211/300/410` and the mains `310/320/400`) are **not** in
     this slice — Core only.
   - **BOARD-PACKAGE-LAYER-002 — DONE (2026-05-30).** The five first-cut
     sensor/PSU board packages landed as thin `!include` wrappers mirroring the
     Core pattern: `packages/boards/s360-200-roomiq.yaml` (+ `-wall` overlay),
     `s360-210-airiq.yaml` (+ `-wall`, `-ceiling-s3` overlays),
     `s360-211-ventiq.yaml` (+ `-pro` overlay), `s360-300-led.yaml` (+ `-wall`,
     `-mic-ceiling`, `-mic-wall` overlays), and `s360-410-poe-psu.yaml`. Each
     wraps the existing functional source package(s) so behaviour is
     byte-identical; the legacy expansion/hardware paths are preserved
     unchanged as source-of-truth aliases (§3.3) and are **not** rewired to
     one-line includes (the consumer-side flip + test repoint is deferred to a
     PACKAGE-RENAME slice / CI-REFACTOR-VERIFY-001 per §5.5, because the folded
     packages are asserted on by text-grep tests). `ceiling_halo_leds.yaml`
     stays a feature (cross-referenced by the LED board, not absorbed). The
     production (`Ceiling-POE-VentIQ-RoomIQ`) and LED-preview
     (`Ceiling-POE-VentIQ-RoomIQ-LED`) products still resolve and validate
     unchanged through the preserved legacy paths; metadata validators pass and
     full `esphome compile` is **pending-ci** (ESPHome not available). The
     mains boards `s360-310/320/400` remain OUT of the board layer (deferred),
     and `S360-311`/`S360-312` stay expansions. **First-cut board layer is now
     complete (Core + these five); next phase is BUNDLE-LAYER-001.**
   - Scope: **first act** resolves the §4 chip drift (flash/PSRAM + GPIO4/5
     fan-vs-radar) against `S360-100-R4`; then author
     `packages/boards/s360-100-core.yaml` and the sensor/PSU board packages
     (`s360-200`, `s360-210`, `s360-211`, `s360-300`, `s360-410`) plus the
     open-source-only mains boards (`s360-310`, `s360-320`, `s360-400`). Each
     new board package wraps/`!include`s the existing functional package(s) so
     behaviour is byte-identical; **no** legacy file is renamed yet.
   - Guardrails: WebFlash contract untouched; no product rebinds yet; legacy
     packages all still present. `S360-311`/`S360-312` stay expansions
     (evidence-gated).
   - Dependency: ARCH-BOARD-BUNDLE-PLAN-001.

3. **BUNDLE-LAYER-001** — introduce the bundle layer + compat shims
   - **Status: DONE (2026-05-30), scoped to the two WebFlash-shipping config
     strings.** Created `products/bundles/` (directory settled to
     `products/bundles/` per §2.2 / §5 — the unchanged `find products/` sweeps
     auto-discover it, no workflow edit) and authored the two config-string-named
     bundles for the live WebFlash builds:
     `products/bundles/ceiling-poe-ventiq-roomiq.yaml` (production / stable) and
     `products/bundles/ceiling-poe-ventiq-roomiq-led.yaml` (preview). Each
     assembles its §2.2 board stack from `packages/boards/`
     (`s360-100-core-ceiling` + `s360-410-poe-psu` + `s360-211-ventiq` +
     `s360-200-roomiq` [+ `s360-300-led` for the preview]) plus the base tier and
     the feature profiles, carrying the same substitutions, entity names, config
     string, and artifact-name identity as the product it replaces. The two
     shipping products `products/sense360-ceiling-poe-ventiq-roomiq.yaml` and
     `products/sense360-ceiling-poe-ventiq-roomiq-led.yaml` were converted into
     thin compat shims (§3.2) that do nothing but `!include` their bundle, paths
     preserved. Identical resolution was proven offline (leaf functional
     packages, merged substitutions, and `text_sensor` identity all byte-equal
     between the pre-shim product and the shim→bundle→board-package chain); full
     `esphome compile` is **pending-ci** (ESPHome not available — no compile
     result claimed).
   - **Scoped to the shipping pair (open decision, recorded):** the remaining
     **five non-shipping config strings** (`Ceiling-POE-VentIQ-FanRelay-RoomIQ`,
     `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`, `Ceiling-POE-FanDAC`,
     `Ceiling-POE-FanPWM`, `Ceiling-POE-RoomIQ`) are **deferred to
     BUNDLE-LAYER-002**. Authoring their bundles and/or shimming their products
     breaks the package-/product-layer guardrail tests that assert on the
     product-internal content the bundle move relocates
     (`tests/test_fandac_package.py` "exactly one product may `!include` the
     FanDAC package"; `tests/test_fan_relay_package.py` "no extra FanRelay
     product YAML under `products/`"; and the substitutions / include /
     header-wording assertions in `tests/test_{relay,pwm,dac}_product_readiness.py`).
     Per §5.5 those tests must travel in the **same** slice that moves the
     content they assert on, so the fan/blocked/roomiq conversions and their test
     repoints are pulled into BUNDLE-LAYER-002 rather than weakening tests in this
     slice. The two shipping products carry no such content-asserting tests, so
     they convert with **no test edit** here.
   - Scope (as planned): author `bundles/*.yaml` 1:1 with the config strings
     (§2.2), each assembling boards + expansions + base + profiles; convert each
     existing `products/sense360-*.yaml` config-string product into a thin compat
     shim (§3.2) that `!include`s its bundle. Keep `products/webflash/*` wrappers
     pointing where `webflash-builds.json` expects.
   - Guardrails (honoured): config strings, artifact names, `webflash-builds.json`,
     `manifest.json`, `sources.json` byte-identical; no workflow / `config/*.json`
     / test edit; customer include paths preserved; no lifecycle / `schematic_status`
     change; LED not marked stable; `S360-410` not verified; no fan blocker closed;
     v1.0.0 resolved config unchanged (offline diff-proof; `esphome config`
     pending-ci).
   - Dependency: BOARD-PACKAGE-LAYER-001 / -002.

3a. **BUNDLE-LAYER-002** — bundle the five non-shipping config strings + shim
   conversions (with the §5.5 test repoints)
   - **Status: DONE (2026-05-30). The bundle layer is now complete.** Authored
     the five remaining config-string bundles under `products/bundles/`
     (`ceiling-poe-roomiq`, `ceiling-poe-fanpwm`, `ceiling-poe-fandac`,
     `ceiling-poe-ventiq-fanrelay-roomiq`, `ceiling-poe-ventiq-fantriac-roomiq`),
     each carrying the moved product composition verbatim — same substitutions,
     entity names, config string, artifact-name identity, and header wording,
     with the include depth adjusted `../packages` → `../../packages` — and
     converted the five `products/sense360-*.yaml` config-string products into
     thin compat shims (§3.2), paths preserved. Repointed the structural /
     fan-readiness tests that read the now-moved product-internal layout
     (`test_{pwm,dac,relay}_product_readiness`, `test_native_fan_gpio_map`,
     `test_fan_pwm_package`, `test_fan_relay_package`, `test_fandac_package`,
     `test_compile_targets`) onto the bundle files — assertions preserved, only
     the path read follows the moved content; catalog / compile-only-target
     path-identity references stay on the product shim. The two
     shipping-identity tests (`test_release_one_entity_names`,
     `test_product_substitutions`) are untouched and green, and the two LAYER-001
     shipping bundles + shims are untouched. Resolution stays byte-identical;
     full `esphome compile` is **pending-ci**. With BUNDLE-LAYER-001 (the
     shipping pair) and this slice, **the bundle layer is done** — all seven
     config strings are bundled + shimmed. Next phase: PACKAGE-RENAME-00x.
   - Scope: author the remaining five config-string bundles under
     `products/bundles/` (FanRelay / FanTRIAC / FanDAC / FanPWM / RoomIQ-only),
     each assembling boards + expansions (the fan-driver SKUs
     `S360-310`/`320`/`311`/`312` stay expansions, not board packages) + base +
     profiles, and convert each remaining `products/sense360-*.yaml`
     config-string product into its thin compat shim. Repoint the
     content-asserting tests (`test_fandac_package`, `test_fan_relay_package`,
     `test_{relay,pwm,dac}_product_readiness`) onto the bundle (the new home of
     the moved includes / substitutions / header wording) **in the same slice**
     per §5.5.
   - Guardrails: same as BUNDLE-LAYER-001 — config strings + artifact names +
     `webflash-builds.json` byte-identical; fan blockers stay blocked; FanTRIAC
     stays blocked under HW-005; resolution proven identical.
   - Dependency: BUNDLE-LAYER-001.

4. **PACKAGE-RENAME-001 … 00N** — SKU-aligned renames in safe slices
   - **Status: in progress — PACKAGE-RENAME-001 (LED) and PACKAGE-RENAME-002
     (AirIQ) done (2026-05-30).**
   - **PACKAGE-RENAME-002 (AirIQ) — DONE (2026-05-30).** The S360-210 AirIQ
     family source-of-truth is flipped: the SKU-aligned board package
     `packages/boards/s360-210-airiq.yaml` (plus its `-wall` and `-ceiling-s3`
     overlays) now holds the authoritative, self-contained definition, and the
     three legacy `packages/expansions/airiq_ceiling.yaml` / `airiq_wall.yaml` /
     `airiq_ceiling_s3.yaml` paths are reduced to thin `!include` aliases of
     those board packages (paths preserved per §3.3 — legacy
     `sense360-core-*` ceiling/wall products and the AirIQ compile-only targets
     still bind them; no alias dropped while a live binder exists). The generic
     base driver `packages/expansions/airiq.yaml` is **cross-referenced, not
     folded** — it has no board package and stays authoritative (mirroring how
     `ceiling_halo_leds.yaml` stayed a feature in RENAME-001), so its
     `airiq_i2c_id` consumer-default assertion is unchanged. The
     content-asserting checks that travel with the moved AirIQ content per §5.5
     (`test_core_abstract_bus.py`'s `AIRIQ_CEILING_S3_PACKAGE`, the ceiling /
     wall entries of `SHARED_I2C_CONSUMER_DEFAULTS`, and the `i2c_primary`
     allow-list in `test_no_legacy_bus_id_in_any_active_consumer_line`) are
     repointed onto the board packages in the **same** slice, assertions intact.
     Resolution is proven byte-identical (the board-package bodies are
     character-for-character equal to the pre-flip legacy file bodies, reached
     through the preserved `!include` paths); full `esphome compile` is
     **pending-ci** (esphome not available in this environment — metadata
     validators run and green, full suite 1154 tests / 3 skipped). No
     config-string, artifact, WebFlash, readiness, lifecycle, or
     `schematic_status` change. **Next slice: PACKAGE-RENAME-003 (VentIQ),
     which also folds the `airiq_bathroom_base.yaml` / `airiq_bathroom_pro.yaml`
     pair (S360-211 family, deliberately out of scope here).**
   - **PACKAGE-RENAME-001 (LED) done (2026-05-30).**
     The LED family source-of-truth is flipped: the SKU-aligned board package
     `packages/boards/s360-300-led.yaml` (plus its `-wall` / `-mic-ceiling` /
     `-mic-wall` overlays) now holds the authoritative, self-contained
     definition, and the four legacy `packages/hardware/led_ring_*.yaml` paths
     are reduced to thin `!include` aliases of those board packages (paths
     preserved per §3.3 — legacy `sense360-core-*` products and the LED-bearing
     preview still bind them; no alias dropped while a live binder exists). The
     content-asserting tests that travel with the LED content per §5.5
     (`test_led_package_mapping.py`'s `LED_CEILING_PACKAGE`,
     `test_core_abstract_bus.py`'s `LED_RING_CEILING_PACKAGE`) are repointed onto
     the board package in the **same** slice, assertions intact. Resolution is
     proven byte-identical for the LED preview product (through its bundle +
     shim) and for the legacy core products; full `esphome compile` is
     **pending-ci** (esphome not available in this environment — metadata
     validators run and green). LED stays preview-gated (no config-string,
     artifact, WebFlash, readiness, or status change; LED not marked stable).
   - Scope: per board family, rebind consumers onto the board package and
     retire the legacy functional name into an **alias** (§3.3); one board
     family (or a few low-binder packages) per slice. Suggested ordering by
     blast radius: LED (`led_ring_*`, done) → AirIQ (`airiq_*`, done) → VentIQ
     (`ventiq*` + `airiq_bathroom_*`) → RoomIQ
     (`presence_*`/`comfort_*`, highest binder count, last) → PSU → mains
     drivers. A later slice promotes `S360-311`/`S360-312` to board packages
     **once** `HW-PINMAP-311/312-FOLLOWUP` evidence closes.
   - Guardrails: an alias is dropped only when its binder count reaches zero;
     legacy-compatible products keep resolving until `PRODUCT-DEP-CORE-001`
     removes them; tests updated in the same slice.
   - Dependency: BUNDLE-LAYER-001 (+ per-driver evidence gates for 311/312).

5. **CI-REFACTOR-VERIFY-001** — confirm CI/gate parity
   - Scope: apply the §5 test updates that travel with each rename slice
     (directory walkers, generated includes, hard-coded path constants); prove
     `validate.yml` and `firmware-build-release.yml` gate behaviour is
     identical (same config strings build, same artifacts named, same
     Release-One entity/substitution checks). No workflow YAML edit unless §5
     identifies one (none required if bundles live under `products/`).
   - Guardrails: gate semantics unchanged; no new build exposed.
   - Dependency: runs alongside / after each PACKAGE-RENAME slice.

6. **DOCS-ARCH-REFRESH-001** — refresh esphome-public docs
   - Scope: the §6.1 doc set (system-architecture, ci-pipeline,
     SENSE360_MODULES, packages/README, README, hardware-catalog,
     product-matrix, room-bundles, roadmap-status).
   - Guardrails: docs-only; no functional/config/workflow change.
   - Dependency: PACKAGE-RENAME slices substantially landed.

7. **WEBFLASH-ARCH-SYNC-001** — refresh WebFlash architecture docs *(WebFlash repo)*
   - Scope: the §6.2 docs (`architecture.md`, `firmware-import.md`) — record
     that the esphome-public board/bundle rename is invisible to the WebFlash
     contract (config strings + artifact names + tags only).
   - Guardrails: docs-only; no `sources.json`/`manifest.json`/importer change.
   - Dependency: DOCS-ARCH-REFRESH-001 (so cross-repo wording matches).

### Dependency graph

```
ARCH-BOARD-BUNDLE-PLAN-001
        │
        ▼
BOARD-PACKAGE-LAYER-001  ──(resolves §4 drift first)
        │
        ▼
BUNDLE-LAYER-001  ──(compat shims; WebFlash contract held)
        │
        ▼
PACKAGE-RENAME-001..00N ──┬── CI-REFACTOR-VERIFY-001  (parity proof)
   (311/312 gated on       │
    HW-PINMAP follow-ups)   ▼
                        DOCS-ARCH-REFRESH-001
                                │
                                ▼
                        WEBFLASH-ARCH-SYNC-001  (WebFlash repo)
```

## 8. Guardrails for this planning PR

This PR adds **only** `docs/arch-board-bundle-plan.md` and the
`UPCOMING_PR.md` queue entries. It does not rename, move, create, or delete any
package, product, board, or bundle YAML; change any config string, artifact
name, or WebFlash build; modify any workflow; modify `config/*.json`,
`manifest.json`, or `firmware/sources.json`; modify any test; or touch the
WebFlash repo. Every code, config, and workflow file stays byte-identical.

**Validation (this PR):**

```
python3 tests/validate_configs.py
python3 tests/test_roadmap_status_doc.py
python3 -m unittest discover -s tests -p "test_*.py"
```

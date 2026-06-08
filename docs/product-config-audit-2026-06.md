# Product config audit (`products/`) — reference map and orphan classification

> **Branch:** `ci/audit-product-configs` — **DO NOT MERGE** without review.
> **Type:** review-first, evidence-based audit. The only code change is one
> CI-glob exclusion (`products/secrets.example.yaml`); **no product YAML is
> deleted** because none is proven unreferenced.

## Scope and method

The `products/` tree carries four naming families that look like four
representations of the same products:

```
products/bundles/        16 files   config-string-named compositions
products/webflash/        6 files   thin WebFlash-namespace wrappers
products/sense360-*.yaml 23 files   customer-pinned compat shims + legacy core templates
products/compile-only/    8 files   compile-only CI validation skeletons
products/secrets.example.yaml       tracked placeholder secrets template
```

The names are misleading, so every file was classified **by what references
it**, not by its name. For each file the whole repo was searched (workflows,
`scripts/`, `config/*.json` including `webflash-builds.json` and
`product-catalog.json`, `tests/`, `packages/`, `docs/`) by explicit path, by
the intra-`products/` `!include` graph, and against the two enumeration
mechanisms. A reference was scored **live** only when it is consumed by a
real build / release / validation / config path. A path that is merely swept
up by an enumerator (the `ci-validate-configs.yml` full-mode
`products/**/*.yaml` glob, or `yamllint products/`) is **not** a live use.

### The decisive structural fact: a three-layer `!include` chain

`products/` is **not** four copies of each product. It is a layered include
chain (settled by `BUNDLE-LAYER-001`, see `docs/repo-structure.md`):

```
config/webflash-builds.json
   -> products/webflash/<sku>.yaml      (wrapper:  !include ../sense360-<sku>.yaml)
   -> products/sense360-<sku>.yaml       (shim:     !include bundles/<sku>.yaml)
   -> products/bundles/<sku>.yaml        (CANONICAL composition: substitutions, packages, identity)
   -> packages/...                       (boards / expansions / features / base)
```

The shim is *nothing but* the bundle include, e.g.
`products/sense360-ceiling-poe-roomiq.yaml` in full:

```yaml
# Compat shim — see products/bundles/ceiling-poe-roomiq.yaml for the composition.
packages:
  bundle: !include bundles/ceiling-poe-roomiq.yaml
```

So `products/bundles/` is the layer that actually carries the composition.
Deleting a bundle breaks the protected `sense360-*` shim that includes it (and,
for the five release stems, the release build itself). **The "bundles look
redundant" hypothesis is the misleading-name trap; the evidence inverts it.**

### Machine-verified resolution (run at audit time)

```
A. Release path (webflash-builds wrapper -> sense360 shim -> bundle): all 5 chains resolve on disk.
   Ceiling-POE-VentIQ-RoomIQ      -> sense360-...-ventiq-roomiq.yaml      -> bundles/ceiling-poe-ventiq-roomiq.yaml      OK
   Ceiling-POE-VentIQ-RoomIQ-LED  -> sense360-...-ventiq-roomiq-led.yaml  -> bundles/ceiling-poe-ventiq-roomiq-led.yaml  OK
   Ceiling-POE-AirIQ-RoomIQ       -> sense360-...-airiq-roomiq.yaml       -> bundles/ceiling-poe-airiq-roomiq.yaml       OK
   Ceiling-POE-RoomIQ             -> sense360-...-roomiq.yaml             -> bundles/ceiling-poe-roomiq.yaml             OK
   Ceiling-POE-RoomIQ-LED         -> sense360-...-roomiq-led.yaml         -> bundles/ceiling-poe-roomiq-led.yaml         OK

B. bundles on disk: 16 | included by exactly one sense360-* shim: 16 | ORPHAN bundles: [] | included by >1 shim: []

C. compile-only-targets.json referenced product YAMLs: 24 | missing on disk: []
```

**Result: every file under `products/` is referenced by a live path. Zero
orphans.**

## STEP 1 — Reference map (file -> referenced-by -> USED / ORPHANED)

### `products/webflash/` (6) — PROTECTED, all USED

| File | Live references | Status |
|---|---|---|
| `ceiling-poe-ventiq-roomiq.yaml` | `webflash-builds.json` (stable release row); `product-catalog.json`; `compile-only-targets.json`; `firmware-combination-matrix.json` | **USED** |
| `ceiling-poe-ventiq-roomiq-led.yaml` | `webflash-builds.json` (preview release row); `product-catalog.json`; `compile-only-targets.json`; `firmware-combination-matrix.json` | **USED** |
| `ceiling-poe-airiq-roomiq.yaml` | `webflash-builds.json` (preview row); `preview-release-targets.json`; `product-catalog.json`; `firmware-combination-matrix.json`; `tests/test_preview_webflash_wrappers.py` | **USED** |
| `ceiling-poe-roomiq.yaml` | `webflash-builds.json` (preview row); `preview-release-targets.json`; `product-catalog.json`; `firmware-combination-matrix.json`; `tests/test_preview_webflash_wrappers.py` | **USED** |
| `ceiling-poe-roomiq-led.yaml` | `webflash-builds.json` (preview row); `preview-release-targets.json`; `product-catalog.json`; `firmware-combination-matrix.json`; `tests/test_preview_webflash_wrappers.py` | **USED** |
| `ceiling-poe-ventiq-fantriac-roomiq.yaml` | `product-catalog.json`; `firmware-combination-matrix.json`; `tests/test_preview_webflash_wrappers.py` (asserts it is the *only* TRIAC wrapper). **Not** in `webflash-builds.json` by design (blocked TRIAC reference) | **USED** |

### `products/sense360-*.yaml` (23) — PROTECTED, all USED

**16 config-string shims** (each `!include`s its bundle; on the build/validate
path; catalogued):

| File | Live references (beyond `product-catalog.json`) | Status |
|---|---|---|
| `sense360-ceiling-poe-ventiq-roomiq.yaml` | release-path canonical (stable); `preview-release-targets.json`; `release-channel-policy.json`; `compile-only-targets.json` | **USED** |
| `sense360-ceiling-poe-ventiq-roomiq-led.yaml` | release-path canonical (preview); `preview-release-targets.json`; `release-channel-policy.json` | **USED** |
| `sense360-ceiling-poe-airiq-roomiq.yaml` | release-path canonical (preview); `preview-release-targets.json`; `compile-only-targets.json` | **USED** |
| `sense360-ceiling-poe-roomiq.yaml` | release-path canonical (preview); `preview-release-targets.json`; `compile-only-targets.json` | **USED** |
| `sense360-ceiling-poe-roomiq-led.yaml` | release-path canonical (preview); `preview-release-targets.json`; `compile-only-targets.json` | **USED** |
| `sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml` | `manual-firmware-artifacts.json`; `room-bundle-fan-variants.json`; `preview-fan-triac-build-rows.json`; `preview-release-targets.json`; `compile-only-targets.json`; `firmware-combination-matrix.json`; `release-channel-policy.json` | **USED** |
| `sense360-ceiling-poe-ventiq-fanpwm-roomiq.yaml` | `room-bundle-fan-variants.json`; `compile-only-targets.json`; `firmware-combination-matrix.json` | **USED** |
| `sense360-ceiling-poe-ventiq-fandac-roomiq.yaml` | `room-bundle-fan-variants.json`; `compile-only-targets.json`; `firmware-combination-matrix.json` | **USED** |
| `sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml` | `preview-release-targets.json`; `room-bundle-fan-variants.json`; `preview-fan-triac-build-rows.json`; `compile-only-targets.json`; `firmware-combination-matrix.json`; `release-channel-policy.json` | **USED** |
| `sense360-ceiling-poe-airiq-fanrelay-roomiq.yaml` | `room-bundle-fan-variants.json`; `compile-only-targets.json`; `firmware-combination-matrix.json` | **USED** |
| `sense360-ceiling-poe-airiq-fandac-roomiq.yaml` | `room-bundle-fan-variants.json`; `compile-only-targets.json` | **USED** |
| `sense360-ceiling-poe-airiq-fanpwm-roomiq.yaml` | `room-bundle-fan-variants.json`; `compile-only-targets.json`; `firmware-combination-matrix.json` | **USED** |
| `sense360-ceiling-poe-fandac.yaml` | `manual-firmware-artifacts.json`; `preview-fan-triac-build-rows.json`; `preview-release-targets.json`; `compile-only-targets.json`; `firmware-combination-matrix.json`; `release-channel-policy.json` | **USED** |
| `sense360-ceiling-poe-fanpwm.yaml` | `manual-firmware-artifacts.json`; `preview-fan-triac-build-rows.json`; `preview-release-targets.json`; `compile-only-targets.json`; `firmware-combination-matrix.json`; `release-channel-policy.json` | **USED** |
| `sense360-ceiling-usb-roomiq.yaml` | `compile-only-targets.json`; `compile-only-candidates.json`; `firmware-combination-matrix.json` (status `compile-only` / `manual-custom`) | **USED** |
| `sense360-ceiling-usb-ventiq-roomiq.yaml` | `compile-only-targets.json`; `compile-only-candidates.json`; `firmware-combination-matrix.json` (status `compile-only` / `manual-custom`) | **USED** |

**7 legacy core / power templates** (self-contained, no bundle include;
catalogued as `legacy-compatible` authoring templates):

| File | Live references | Status |
|---|---|---|
| `sense360-core-c-poe.yaml` | `product-catalog.json` (legacy-compatible template) | **USED** |
| `sense360-core-c-usb.yaml` | `product-catalog.json` (legacy-compatible template) | **USED** |
| `sense360-core-ceiling.yaml` | `product-catalog.json` (legacy-compatible template) | **USED** |
| `sense360-core-ceiling-bathroom.yaml` | `product-catalog.json` (legacy-compatible template) | **USED** |
| `sense360-core-ceiling-presence.yaml` | `product-catalog.json` (legacy-compatible template) | **USED** |
| `sense360-fan-pwm.yaml` | `product-catalog.json` | **USED** |
| `sense360-poe.yaml` | `product-catalog.json` | **USED** |

### `products/bundles/` (16) — the questionable family — all USED

Every bundle is `!include`d by exactly one `products/sense360-*` shim (the
universal live reference; the shim is protected and on the build/validate/
compile path). Several carry reinforcing live references too:

| File | Live references | Status |
|---|---|---|
| `ceiling-poe-ventiq-roomiq.yaml` | shim `!include` — **release path** (stable Release-One) | **USED** |
| `ceiling-poe-ventiq-roomiq-led.yaml` | shim `!include` — **release path** (preview) | **USED** |
| `ceiling-poe-airiq-roomiq.yaml` | shim `!include` — **release path** (preview); `preview-release-targets.json` notes | **USED** |
| `ceiling-poe-roomiq.yaml` | shim `!include` — **release path** (preview); `preview-release-targets.json` notes | **USED** |
| `ceiling-poe-roomiq-led.yaml` | shim `!include` — **release path** (preview); `preview-release-targets.json` notes | **USED** |
| `ceiling-poe-ventiq-fanrelay-roomiq.yaml` | shim `!include`; `tests/test_fan_relay_package.py` | **USED** |
| `ceiling-poe-ventiq-fanpwm-roomiq.yaml` | shim `!include`; `room-bundle-fan-variants.json` (`bundle_yaml`); `tests/test_compile_targets.py`; `tests/test_fan_pwm_package.py` | **USED** |
| `ceiling-poe-ventiq-fandac-roomiq.yaml` | shim `!include`; `room-bundle-fan-variants.json`; `tests/test_fandac_package.py` | **USED** |
| `ceiling-poe-ventiq-fantriac-roomiq.yaml` | shim `!include`; `docs/hardware/s360-100-core-connector-pin-map.md` | **USED** |
| `ceiling-poe-airiq-fanrelay-roomiq.yaml` | shim `!include`; `room-bundle-fan-variants.json`; `tests/test_fan_relay_package.py` | **USED** |
| `ceiling-poe-airiq-fandac-roomiq.yaml` | shim `!include`; `room-bundle-fan-variants.json`; `tests/test_fandac_package.py` | **USED** |
| `ceiling-poe-airiq-fanpwm-roomiq.yaml` | shim `!include`; `room-bundle-fan-variants.json`; `tests/test_compile_targets.py`; `tests/test_fan_pwm_package.py` | **USED** |
| `ceiling-poe-fandac.yaml` | shim `!include`; `tests/test_fandac_package.py` | **USED** |
| `ceiling-poe-fanpwm.yaml` | shim `!include`; `tests/test_compile_targets.py`; `tests/test_fan_pwm_package.py` | **USED** |
| `ceiling-usb-roomiq.yaml` | shim `!include` (manual-custom compile-only product) | **USED** |
| `ceiling-usb-ventiq-roomiq.yaml` | shim `!include` (manual-custom compile-only product) | **USED** |

### `products/compile-only/` (8) — PROTECTED, all USED

All eight are enumerated by `config/compile-only-targets.json` and consumed by
the `compile-only.yml` workflow (`scripts/validate_compile_targets.py`).

| File | Live references | Status |
|---|---|---|
| `ceiling-poe.yaml` | `compile-only-targets.json`; `compile-only-candidates.json` | **USED** |
| `ceiling-poe-roomiq.yaml` | `compile-only-targets.json`; `compile-only-candidates.json`; `release-channel-policy.json` | **USED** |
| `ceiling-poe-ventiq.yaml` | `compile-only-targets.json`; `compile-only-candidates.json` | **USED** |
| `ceiling-poe-airiq.yaml` | `compile-only-targets.json`; `compile-only-candidates.json` | **USED** |
| `ceiling-poe-airiq-roomiq.yaml` | `compile-only-targets.json`; `compile-only-candidates.json`; `release-channel-policy.json` | **USED** |
| `ceiling-poe-fandac.yaml` | `compile-only-targets.json`; `compile-only-candidates.json` | **USED** |
| `ceiling-poe-fanpwm.yaml` | `compile-only-targets.json`; `compile-only-candidates.json` | **USED** |
| `ceiling-poe-fanpwm-native.yaml` | `compile-only-targets.json` | **USED** |

### `products/secrets.example.yaml` (1) — template, not a config

| File | Findings | Status |
|---|---|---|
| `secrets.example.yaml` | Tracked placeholder secrets template (`SEC-ESP-SECRET-GUARD-001`); copied to the gitignored `products/secrets.yaml` for local builds; CI provisions its own throwaway secrets independently. `tests/validate_configs.py` **already skips it** for product validation. It is **not** an ESPHome product config. | **template — keep** |

## STEP 2 — Classification of the questioned families

- **`products/bundles/*`** — referenced by far more than the validate glob:
  every file is the `!include` target of a protected `sense360-*` shim (and
  the five release stems are on the live release build path). **Not a deletion
  candidate.**
- **`ceiling-usb-*`** (in `bundles/` and `sense360-`) — correct that they are
  not in `webflash-builds.json` and have no sellable kit, but they are **not**
  dev/legacy junk: the catalog marks them `status: compile-only`,
  `target_channel: manual-custom`; their shims are registered compile-only
  targets (`compile-only-targets.json`), appear in `compile-only-candidates.json`
  and `firmware-combination-matrix.json`, and `!include` their USB bundles.
  **Referenced by live paths; not orphaned.**
- **`products/secrets.example.yaml`** — confirmed a template, not a config.
  **Fix applied: excluded from the discover glob, not deleted.**

## STEP 3 — Applied changes

### Deleted files: NONE

No file under `products/` is referenced by nothing live, so the "delete only
proven orphans" rule deletes nothing. Per-family evidence of non-orphan status
is the reference map above (every row is **USED** or a kept template).

### CI fix: exclude `secrets.example.yaml` from the full-mode discover glob

`.github/workflows/ci-validate-configs.yml` (manual, `workflow_dispatch`-only
broad/legacy sweep) discovered `products/secrets.example.yaml` in **full** mode
(`products/**/*.yaml`, excluding only `secrets.yaml` and `products/webflash/`)
and would run `esphome config` against it. The template is a placeholder
secrets map with no `esphome:`/`substitutions:` block, so that step would fail.
The fix adds `secrets.example.yaml` to the basename exclusion (it is the
canonical "exclude from the discover glob" remedy, not a deletion). Verified:
full-mode discovery drops from 48 to 47 entries (only `secrets.example.yaml`
removed); all 16 bundles, 8 compile-only, and 23 `sense360-*` files remain
discovered; the 6 `webflash/` wrappers stay excluded as before.

## Protected list (never deletion candidates; all confirmed USED)

- `products/sense360-*.yaml` (23) — release-path canonical targets + legacy
  authoring templates; the `firmware-build-release.yml` matrix compiles
  `products/sense360-<stem>.yaml` when `webflash-builds.json` points at a
  `products/webflash/` wrapper.
- `products/webflash/*` (6) — the wrappers `webflash-builds.json` points at.
- `products/compile-only/*` (8) — consumed by `compile-only.yml`.

## "Needs Neil" list (not proven orphans — product-level decisions only)

1. **USB power-axis family** (`Ceiling-USB-RoomIQ`, `Ceiling-USB-VentIQ-RoomIQ`
   shims + their bundles). Live via the compile-only lane + catalog + shim
   chain, so **not** an orphan cleanup. If the USB power axis is to be retired
   (it has no sellable kit per `docs/v1-r4-product-gap.md`), that is a
   deliberate product-lifecycle change spanning `compile-only-targets.json`,
   `compile-only-candidates.json`, `product-catalog.json`, the shim, and the
   bundle **together** — out of scope for an orphan audit. Left in place.
2. **`config/compile-only-candidates.json`** enumerates several
   `products/compile-only/*.yaml` candidate paths that do not exist on disk yet
   (future targets, e.g. `ceiling-poe-led.yaml`, `ceiling-usb*.yaml`,
   `ceiling-poe-fantriac.yaml`). Informational; nothing to delete.
3. **Cosmetic:** the `validate.yml` "Count products" step
   (`find products/ -name "*.yaml" ! -name "secrets.yaml"`) counts
   `secrets.example.yaml` in its product tally (over-count by one). It is a log
   line only (no validation), so this PR leaves it untouched to stay scoped to
   the discover glob; flag if exact counts matter.

## Acceptance

- **Quick Validation** (`.github/workflows/validate.yml`) test set: all 15
  steps green (`validate_configs.py`, `test_product_substitutions.py`,
  `check_fallback_ap_password.py`, `test_release_one_entity_names.py`,
  `validate_webflash_builds.py`, `test_validate_webflash_release_notes.py`,
  `test_generate_webflash_release_notes.py`,
  `test_release_notes_draft_workflow.py`, `test_check_pending_version_bump.py`,
  `test_webflash_artifact_naming.py`, `test_product_catalog.py`,
  `validate_product_catalog_consistency.py`,
  `test_product_catalog_consistency.py`, `test_bump_release_version.py`,
  `test_plan_release.py`).
- **Release build path** (`sense360-*` / `webflash/`) and **compile-only path**
  are **untouched** by this PR and still resolve (machine-verified: all 5
  release chains resolve, all 24 compile-only targets exist on disk).
- The only change to an executable surface is the `ci-validate-configs.yml`
  full-mode discover-glob exclusion; the Quick Validation workflow, the release
  workflow, and the compile-only workflow are unmodified.

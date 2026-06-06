# CI/CD Pipeline & Firmware Validation

This document explains how the Continuous Integration (CI) pipeline validates firmware configurations and ensures all products can be compiled successfully before release.

## Table of Contents

- [Overview](#overview)
- [Refactored YAML layout: boards, bundles, aliases, and shims](#refactored-yaml-layout-boards-bundles-aliases-and-shims)
- [Mini Board Product Configurations](#mini-board-product-configurations)
- [CI Workflows](#ci-workflows)
- [Validation Process](#validation-process)
- [Running Validation Locally](#running-validation-locally)
- [Troubleshooting CI Failures](#troubleshooting-ci-failures)

---

## Overview

The CI pipeline has two layers:

1. **Per-PR gate** (`validate.yml` + `firmware-build-release.yml`) — runs on
   every push and pull request, plus on release publish. Covers YAML syntax,
   product substitutions, Release-One entity-name collisions, and the full
   WebFlash build/artifact-naming contract.
2. **Manual broad sweep** (`ci-validate-configs.yml`) — runs only on manual
   dispatch. Sweeps every legacy/manual/reference product YAML through
   `esphome config`, exercises generated module combinations, and lints C++
   headers. Useful for spotting drift in older configs without blocking
   day-to-day PRs.

What this pipeline ensures:

1. **Release-One/WebFlash compiles and ships correctly** - `validate.yml`
   guards the WebFlash build matrix and artifact names on every PR;
   `firmware-build-release.yml` builds and publishes the signed `.bin` set
   on release.
2. **No broken packages** - Package references are validated by both layers.
3. **Module combinations work** - Generated configs test various module
   permutations (manual sweep).
4. **Code quality** - YAML syntax, C++ formatting, and style checks.

---

## Refactored YAML layout: boards, bundles, aliases, and shims

The firmware YAML has been restructured into SKU-aligned **board packages**
plus product-named **bundle YAMLs** (the
[`ARCH-BOARD-BUNDLE-PLAN-001`](arch-board-bundle-plan.md) epic). This section
records the new directory layout and how each CI workflow handles it. The key
property for CI is that **every glob, `find`, and `sed` keeps its existing
semantics** — the refactor was designed to land under the unchanged sweeps, and
`CI-REFACTOR-VERIFY-001` proved that parity holds with **no workflow edit**.

### The four layers CI walks

| Layer | Location | What it holds | CI relevance |
|-------|----------|---------------|--------------|
| **Board packages (authoritative)** | `packages/boards/s360-*.yaml` | One canonical, self-contained package per board SKU (`S360-100` Core, `S360-200` RoomIQ, `S360-210` AirIQ, `S360-211` VentIQ, `S360-300` LED, `S360-410` PoE PSU) plus mount/power/variant overlays | Linted by the recursive `yamllint … packages/`; validated by `validate_configs.py`'s `packages/` walk |
| **Legacy aliases** | `packages/expansions/*.yaml`, `packages/hardware/*.yaml` (legacy functional names, e.g. `led_ring_ceiling.yaml`, `airiq_ceiling.yaml`, `comfort_ceiling.yaml`, `power_poe.yaml`) | Thin `!include` wrappers of their board package — the **path is preserved** (never deleted) so legacy-compatible products and tests keep resolving. An alias is dropped only when its binder count reaches zero (gated on `PRODUCT-DEP-CORE-001`). | Same recursive lint/walk as boards; their `!include` chain resolves through the board package |
| **Bundles (config-string-named)** | `products/bundles/*.yaml` | One YAML per WebFlash config string, assembling `boards + expansions + base + profiles`. Carries the substitutions, entity names, config string, and artifact-name identity of the product it backs. | **Auto-discovered** by the recursive `find products/` sweep; linted by `yamllint … products/`; walked by `validate_configs.py` |
| **Product shims (customer include contract)** | `products/sense360-*.yaml` (the seven config-string products) | Thin `!include` of the matching bundle. The customer-pinned path (`files: - products/sense360-…yaml`) is preserved byte-for-byte. | Discovered by the same `find products/` sweep; resolves shim → bundle → boards |

The base tier (`packages/base/**`) and the feature tier
(`packages/features/**`) **did not move** — they are functional, not
board-bound, and bundles include them unchanged. This is why the two `sed`
substitution targets are untouched (see below).

### How each workflow handles the new layout (verified, no edit required)

- **`yamllint -c .yamllint products/ packages/`** (`validate-yaml` job in
  `ci-validate-configs.yml`). `yamllint` recurses into directories, so
  `packages/boards/` and `products/bundles/` are covered automatically. Verified
  clean across boards, bundles, aliases, and shims.

- **`find products/ -name "*.yaml" -type f ! -name "secrets.yaml" ! -path "products/webflash/*"`**
  (the `discover-products` sweep in `ci-validate-configs.yml`, mirrored as the
  informational product count in `validate.yml`). Because `find` is recursive,
  the new `products/bundles/*.yaml` and the existing `products/compile-only/*.yaml`
  are enumerated alongside the top-level shims/legacy products; the
  `products/webflash/*` wrappers remain excluded by the unchanged `! -path`
  predicate. Every discovered file's `!include` chain resolves (shim → bundle →
  board package → base/feature tiers).

- **`sed -i "s|ref: main|ref: $BRANCH|g" packages/base/external_components.yaml`**
  and
  **`find packages/features -name "*.yaml" -exec sed -i "s|@main|@$BRANCH|g" {} \;`**
  (the branch-rewrite step in `ci-validate-configs.yml`, and the
  `external_components` rewrite in `firmware-build-release.yml`). Both targets
  are in the base/feature tiers, which the refactor left in place, so the paths
  still exist and the substitutions still apply. Bundles pull
  `external_components` from the **exact** sed target via
  `external_components: !include ../../packages/base/external_components.yaml`,
  so the release-time rewrite reaches them through the include.

- **Compile-only lane** (`compile-only.yml` →
  `config/compile-only-targets.json` + `scripts/validate_compile_targets.py`).
  Every compile-only `product_yaml` still points at a real file: the
  `products/webflash/*` wrapper targets resolve to their canonical product, the
  `products/compile-only/*` targets are unchanged, and the
  `products/sense360-*.yaml` product targets now resolve through the shim →
  bundle chain. Metadata validation passes unchanged.

- **Release gate** (`firmware-build-release.yml`). This workflow is
  **config-string-driven, not glob-driven**: it enumerates release targets from
  `config/webflash-builds.json` and, for a `products/webflash/*` wrapper entry,
  compiles the canonical `products/sense360-<stem>.yaml` (the shim) instead. The
  shim's config_dir stays `products/`, so the `path: ../components`
  external-components rewrite still resolves to the repo-root `components/` tree.
  Config strings, artifact names, and `config/webflash-builds.json` are
  byte-identical, so the same builds ship under the same names.

### Gate identity (required-status-check names)

Branch protection matches required checks by workflow `name:`. The two gate
workflow `name:` fields are:

| Gate workflow | `name:` field | Role |
|---------------|---------------|------|
| `validate.yml` | `CI: Quick Validation` | Per-PR gate (every push/PR) |
| `firmware-build-release.yml` | `Release 3: Build & Release` | Release-time gate (release publish) |

These `name:` fields were renamed to the role-and-step scheme (from
`Quick Validation` and `Build & Release Firmware`). The workflow **file** names
are unchanged, so dispatch URLs and badge paths still resolve. Because branch
protection matches required checks by workflow `name:`, the required-status-check
contexts must be updated from the old names to the new ones, or they report as
"expected, never reported" and block merges.

---

## Mini Board Product Configurations

The Sense360 Mini is a compact board with integrated sensors. The following product configurations are validated by CI:

### Current Mini Board Configs

| Config File | Description | Presence Sensor | LED Type |
|-------------|-------------|-----------------|----------|
| `sense360-mini-airiq.yaml` | AirIQ + LD2450 presence | LD2450 | 4x WS2812B addressable |
| `sense360-mini-airiq-basic.yaml` | Basic air quality profile | None | GPIO2 status LED |
| `sense360-mini-airiq-advanced.yaml` | Advanced air quality with calibration | None | GPIO2 status LED |
| `sense360-mini-airiq-ld2412.yaml` | AirIQ + LD2412 radar | LD2412 | 4x WS2812B addressable |
| `sense360-mini-full-ld2412.yaml` | Full sensors + LD2412 | LD2412 | 4x WS2812B addressable |
| `sense360-mini-presence.yaml` | Presence detection only | LD2450 | 4x WS2812B addressable |
| `sense360-mini-presence-basic.yaml` | Basic presence profile | LD2450 | 4x WS2812B addressable |
| `sense360-mini-presence-advanced.yaml` | Advanced presence with zones | LD2450 | 4x WS2812B addressable |
| `sense360-mini-presence-ld2412.yaml` | Presence with LD2412 | LD2412 | 4x WS2812B addressable |
| `sense360-mini-presence-advanced-ld2412.yaml` | Advanced presence + LD2412 | LD2412 | 4x WS2812B addressable |

### Mini Board Hardware

All mini boards share the same core hardware (ESP32-S3):

| Component | Specification |
|-----------|---------------|
| MCU | ESP32-S3-WROOM-2 (16MB Flash) |
| I2C Pins | SDA: GPIO48, SCL: GPIO45 |
| UART Pins | TX: GPIO43, RX: GPIO44 |
| LED Data | GPIO8 (4x WS2812B via level shifter) |
| Onboard Sensors | LTR-303 (Light), SHT30 (Temp/Humidity), SCD40 (CO2) |

### Config Structure Variations

There are two structural patterns for mini configs:

**Pattern 1: Package-based (Modular)**
Used by: `sense360-mini-airiq.yaml`, `sense360-mini-presence*.yaml`, `*-ld2412.yaml`
```yaml
packages:
  core_hardware: !include ../packages/hardware/sense360_core_mini.yaml
  presence_hardware: !include ../packages/hardware/presence_ld2450.yaml
  onboard_sensors: !include ../packages/hardware/mini_onboard_sensors.yaml
  status_leds: !include ../packages/features/mini_four_leds_addr.yaml  # 4x addressable LEDs
```

**Pattern 2: Inline (Self-contained)**
Used by: `sense360-mini-airiq-basic.yaml`, `sense360-mini-airiq-advanced.yaml`
```yaml
# Hardware defined inline
substitutions:
  status_led_pin: GPIO2  # Simple GPIO LED

output:
  - platform: gpio
    id: status_led_output
    pin: ${status_led_pin}
```

---

## CI Workflows

The repository has six GitHub Actions workflows. Only `validate.yml` (every
push/PR) and `firmware-build-release.yml` (release publish) gate; the other
four are manual or release-time helpers.

| Workflow | `name:` | Trigger | Role |
|----------|---------|---------|------|
| `validate.yml` | CI: Quick Validation | push + pull_request | **Per-PR gate** (Release-One / WebFlash) |
| `firmware-build-release.yml` | Release 3: Build & Release | release publish + manual dispatch | **Release-time gate** — builds/publishes `.bin` set |
| `ci-validate-configs.yml` | CI: Validate Configs | manual dispatch only | Manual broad legacy/manual sweep — **not a PR gate** |
| `compile-only.yml` | CI: Compile-Only | push + pull_request (metadata only); manual dispatch for full compile | Pre-hardware compile/codegen check — **not the Release-One/WebFlash gate** |
| `manual-firmware-artifacts.yml` | Tools: Manual Firmware Artifacts | manual dispatch only | Builds expiring, non-release operator artifacts — **not a PR gate, never a release** |
| `release-notes-draft.yml` | Release 2: Draft Notes | manual dispatch only | Drafts/validates WebFlash release notes — **preflight only, does not gate** |

The first three workflows are described in detail below; the remaining three
follow in sections 4–6.

The first three workflows handle the core validate/release flow:

### 1. CI: Quick Validation (`validate.yml`)

**Triggers:** Every push and PR
**Duration:** ~30 seconds
**Purpose:** Release-One / WebFlash per-PR gate. Lightweight, fast feedback;
not a full ESPHome compilation sweep (that lives in
`firmware-build-release.yml` on release and in the manual
`ci-validate-configs.yml` sweep).

**What it checks:**
- YAML syntax validity (`tests/validate_configs.py`)
- Product substitutions — fallback SSID length, AP password, `device_name`
  (`tests/test_product_substitutions.py`)
- Release-One profile entity-name collisions
  (`tests/test_release_one_entity_names.py`)
- WebFlash build matrix vs. compatibility snapshot
  (`tests/validate_webflash_builds.py`)
- WebFlash release-notes validator self-test
  (`tests/test_validate_webflash_release_notes.py`)
- WebFlash artifact naming — `scripts/product_name_mapper.py` agrees with
  `config/webflash-builds.json` (`tests/test_webflash_artifact_naming.py`)
- Product and package counts

This workflow does **not** run `esphome config` on the full product set.
For a broad legacy/manual ESPHome compilation sweep, manually dispatch
`ci-validate-configs.yml`.

```
Push/PR → YAML + WebFlash gate checks → Pass/Fail (~30 sec)
```

### 2. Broad Legacy/Manual Config Sweep (`ci-validate-configs.yml`)

**Triggers:** Manual (`workflow_dispatch`) only
**Duration:** ~5-10 minutes
**Purpose:** Broad ESPHome validation of legacy/manual/reference product
configurations and generated module combinations.

> **Not a PR gate.** This workflow does **not** run on push or pull request.
> Release-One/WebFlash gating lives in `validate.yml` (every push/PR) and
> `firmware-build-release.yml` (release publish). Failures here indicate
> legacy/manual compatibility drift — they do not block normal PRs and do
> not by themselves indicate a Release-One/WebFlash regression.

**Jobs:**

| Job | Description |
|-----|-------------|
| `validate-yaml` | YAML syntax + yamllint checks |
| `discover-products` | Dynamically finds product YAML files (excludes WebFlash wrappers) |
| `test-all-products` | Runs `esphome config` on every discovered legacy/manual product |
| `test-generated-configs` | Tests module combination permutations |
| `lint-cpp` | Checks C++ header formatting |
| `test-summary` | Reports overall results |

**Dynamic Product Discovery:**
```bash
# The sweep automatically discovers product YAMLs. The WebFlash wrappers in
# products/webflash/ are intentionally excluded: they are not standalone
# product configs but thin mappers from WebFlash config strings to canonical
# products/sense360-*.yaml files (see firmware-build-release.yml and
# config/webflash-builds.json).
PRODUCTS=$(find products/ -name "*.yaml" -type f ! -name "secrets.yaml" ! -path "products/webflash/*" | sort)
```

This means:
- Adding a new product automatically includes it in the manual sweep
- No workflow changes needed when adding products
- Every non-wrapper product in `products/` is validated when the sweep is run
- The recursive `find` also covers the `products/bundles/*.yaml` config-string
  bundles and the `products/compile-only/*.yaml` lane introduced by the
  board/bundle refactor — they were designed to land under this unchanged sweep
  (see [Refactored YAML layout](#refactored-yaml-layout-boards-bundles-aliases-and-shims)).
  The `products/sense360-*.yaml` files that became thin compat shims still
  resolve through `shim → bundle → board package`.

### 3. Build & Release (`firmware-build-release.yml`)

**Triggers:** GitHub release creation or manual dispatch
**Purpose:** Compile and publish firmware binaries

**Process:**
1. Generate the build matrix from `config/webflash-builds.json` (filtered by
   version + channel) — **not** a `find products/` scan. For a
   `products/webflash/*` wrapper entry the canonical
   `products/sense360-<stem>.yaml` (now a compat shim → bundle) is compiled
   instead.
2. Compile each selected product with ESPHome
3. Rename binaries to WebFlash format (e.g., `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`)
4. Attach to GitHub release with checksums

### 4. CI: Compile-Only (`compile-only.yml`)

**Triggers:** push + pull_request (metadata-only job); manual (`workflow_dispatch`)
for the full `esphome compile` pass
**Purpose:** Validate YAML / config / codegen buildability for a curated set of
product YAMLs (`config/compile-only-targets.json`) **before hardware is
available**.

> **Not the Release-One/WebFlash PR gate.** On push/PR it runs only the
> metadata-validation job (no ESPHome, no artifacts). The full ESPHome compile
> runs only on manual dispatch with `compile_mode=full`. Compile success is
> necessary but **not** sufficient for preview/stable readiness, and this
> workflow never uploads `.bin` files, tags a release, or modifies
> `config/webflash-builds.json`.

### 5. Tools: Manual Firmware Artifacts (`manual-firmware-artifacts.yml`)

**Triggers:** Manual (`workflow_dispatch`) only
**Purpose:** Compile the FanRelay / FanPWM / FanDAC manual / no-WebFlash
firmware candidates and upload **only** temporary, expiring GitHub Actions
artifacts for point-to-point operator handoff.

> **Not a PR gate and never a release.** It requires an explicit
> `artifact_mode=manual-candidate` input before it builds anything, names every
> artifact `<product-stem>-manual-<short-sha>-nonrelease`, and never creates a
> GitHub Release, writes `firmware/sources.json` / `manifest.json`, or produces
> a `vX.Y.Z` / `-stable` / `-preview` asset.

### 6. Release 2: Draft Notes (`release-notes-draft.yml`)

**Triggers:** Manual (`workflow_dispatch`) only
**Purpose:** Produce a WebFlash release-notes draft from the product catalog,
validate it against the WebFlash release-body contract, and upload the result as
a workflow artifact.

> **Preflight only — does not gate.** It does not create a GitHub Release,
> compile or publish firmware, or commit the generated `release-notes.md`.
> Publication of the actual release body remains gated separately by
> `scripts/validate-webflash-release-notes.py` inside `firmware-build-release.yml`
> at `release.published` time.

---

## Validation Process

### What Gets Validated

| Check | Tool | Catches |
|-------|------|---------|
| YAML Syntax | `pyyaml` | Indentation errors, invalid YAML |
| YAML Style | `yamllint` | Style violations, line length |
| ESPHome Config | `esphome config` | Invalid components, missing references, type errors |
| Package References | ESPHome | Broken `!include` paths |
| Substitution Usage | ESPHome | Undefined substitutions |
| Component Conflicts | ESPHome | Duplicate IDs, conflicting pins |
| C++ Headers | `clang-format` | Code style violations |

### Test Modes

The `ci-validate-configs.yml` workflow supports two modes for the generated
module combinations job. The workflow is manual-only (`workflow_dispatch`), so
both modes are reached by manually dispatching the workflow.

| Mode | Description |
|------|-------------|
| `quick` | Representative subset of module combinations (default) |
| `full` | All possible module combinations |

To run the broad legacy/manual sweep:
1. Go to Actions → "CI: Validate Configs"
2. Click "Run workflow"
3. Select `test_mode: quick` (representative) or `full` (all combinations)

---

## Running Validation Locally

### Quick Syntax Check

```bash
# Validate YAML syntax
python3 tests/validate_configs.py
```

### Validate a Single Product

```bash
# Test one config
esphome config products/sense360-mini-airiq.yaml
```

### Validate All Products

```bash
# Test all products (same as CI)
for file in products/*.yaml; do
  echo "Testing: $file"
  esphome config "$file" || echo "FAILED: $file"
done
```

### Run Full CI Checks Locally

```bash
# 1. Install dependencies
pip install pyyaml yamllint esphome==2026.4.5

# 2. Create test secrets
cat > secrets.yaml << 'EOF'
wifi_ssid: "TestNetwork"
wifi_password: "TestPassword123"
api_encryption_key: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa="
ota_password: "test-ota-password"
fallback_ap_password: "fallback123"
web_username: "admin"
web_password: "test_web_password"
EOF
cp secrets.yaml products/secrets.yaml

# 3. Run validation
python3 tests/validate_configs.py

# 4. Run yamllint
yamllint -c .yamllint products/ packages/

# 5. Test all products
for file in products/*.yaml; do
  esphome config "$file"
done
```

### Generate and Test Module Combinations

```bash
# List all possible combinations
python3 tests/generate_test_configs.py --mode list --full

# Generate test configs
python3 tests/generate_test_configs.py --mode generate --representative --output-dir tests/generated

# Test generated configs
for file in tests/generated/*.yaml; do
  esphome config "$file"
done
```

---

## Troubleshooting CI Failures

### Common Failure Types

#### 1. YAML Syntax Error
```
ERROR: while parsing a block mapping
  in "products/sense360-mini-airiq.yaml", line 45, column 3
expected <block end>, but found '<block mapping start>'
```
**Fix:** Check indentation at the specified line.

#### 2. Missing Package Reference
```
ERROR: Could not find file '../packages/hardware/missing_file.yaml'
```
**Fix:** Verify the package path exists and is spelled correctly.

#### 3. Undefined Substitution
```
ERROR: Undefined substitution: device_name
```
**Fix:** Add the missing substitution to the `substitutions:` section.

#### 4. Duplicate Component ID
```
ERROR: ID 'i2c0' already exists
```
**Fix:** Check for duplicate I2C bus definitions across included packages.

#### 5. External Components Branch Mismatch
```
ERROR: Could not fetch external component from branch 'main'
```
**Note:** CI automatically updates `external_components.yaml` to use the current branch. This error usually means the branch hasn't been pushed yet.

### Viewing CI Logs

1. Go to the repository's **Actions** tab
2. Click on the failed workflow run
3. Expand the failed job
4. Look for the specific error message

### CI Passes but Local Fails (or vice versa)

Common causes:
- **Different ESPHome version:** CI uses `ESPHOME_VERSION: "2026.4.5"`
- **Missing secrets.yaml:** Copy the tracked template to a local file —
  `cp secrets.example.yaml secrets.yaml`. CI writes its own placeholder
  `secrets.yaml` at runtime, so the tracked template is not used by CI.
- **External components:** CI patches `external_components.yaml` to use the current branch

---

## Adding New Mini Board Configs

When adding a new mini board product configuration:

1. **Create the config file** in `products/`:
   ```bash
   touch products/sense360-mini-new-variant.yaml
   ```

2. **CI automatically includes it** - No workflow changes needed!

3. **Verify locally** before pushing:
   ```bash
   esphome config products/sense360-mini-new-variant.yaml
   ```

4. **Push and check CI** - The new product will appear in the test matrix.

5. **Update product name mapper** (if needed for releases):
   Edit `scripts/product_name_mapper.py` to add WebFlash naming.

---

## Related Documentation

- [Development Guide](development.md) - Local setup and contribution guidelines
- [Product Matrix](product-matrix.md) - Complete product and module reference
- [Configuration Reference](configuration.md) - Customization options

---

## CI Environment Details

| Setting | Value |
|---------|-------|
| ESPHome Version | 2026.4.5 |
| Python Version | 3.11 |
| Runner | ubuntu-latest |
| Cache | PlatformIO (~/.platformio) |

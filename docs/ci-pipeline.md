# CI/CD Pipeline & Firmware Validation

This document explains how the Continuous Integration (CI) pipeline validates firmware configurations and ensures all products can be compiled successfully before release.

## Table of Contents

- [Overview](#overview)
- [Mini Board Product Configurations](#mini-board-product-configurations)
- [CI Workflows](#ci-workflows)
- [Validation Process](#validation-process)
- [Running Validation Locally](#running-validation-locally)
- [Troubleshooting CI Failures](#troubleshooting-ci-failures)

---

## Overview

The CI pipeline automatically validates all firmware configurations on every push and pull request. This ensures:

1. **All product configs compile** - Every YAML file in `products/` is tested with ESPHome
2. **No broken packages** - Package references are validated
3. **Module combinations work** - Generated configs test various module permutations
4. **Code quality** - YAML syntax, C++ formatting, and style checks

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

Three GitHub Actions workflows handle firmware validation:

### 1. Quick Validation (`validate.yml`)

**Triggers:** Every push and PR
**Duration:** ~30 seconds
**Purpose:** Fast pre-flight syntax check

**What it checks:**
- YAML syntax validity
- Basic structure validation
- Product and package counts

```
Push/PR → YAML Syntax Check → Pass/Fail (30 sec)
```

### 2. Full Config Validation (`ci-validate-configs.yml`)

**Triggers:** Push/PR when config files change
**Duration:** ~5-10 minutes
**Purpose:** Complete ESPHome validation of all products

**Jobs:**

| Job | Description |
|-----|-------------|
| `validate-yaml` | YAML syntax + yamllint checks |
| `discover-products` | Dynamically finds ALL products in `products/` |
| `test-all-products` | Runs `esphome config` on every product |
| `test-generated-configs` | Tests module combination permutations |
| `lint-cpp` | Checks C++ header formatting |
| `test-summary` | Reports overall results |

**Dynamic Product Discovery:**
```bash
# The CI automatically discovers all products - no hardcoded list!
PRODUCTS=$(find products/ -name "*.yaml" -type f ! -name "secrets.yaml" | sort)
```

This means:
- Adding a new product automatically includes it in CI
- No workflow changes needed when adding products
- Every product in `products/` is validated

### 3. Build & Release (`firmware-build-release.yml`)

**Triggers:** GitHub release creation or manual dispatch
**Purpose:** Compile and publish firmware binaries

**Process:**
1. Generate build matrix from `products/` directory
2. Compile each product with ESPHome
3. Rename binaries to WebFlash format (e.g., `Sense360-Mini-AirIQ-v3.0.0-stable.bin`)
4. Attach to GitHub release with checksums

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

The `ci-validate-configs.yml` workflow supports two modes:

| Mode | Description | When Used |
|------|-------------|-----------|
| `quick` | Representative subset of module combinations | Default on push/PR |
| `full` | All possible module combinations | Manual dispatch |

To run full validation manually:
1. Go to Actions → "CI - Validate Firmware Configs"
2. Click "Run workflow"
3. Select `test_mode: full`

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
pip install pyyaml yamllint esphome==2025.3.0

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
- **Different ESPHome version:** CI uses `ESPHOME_VERSION: "2025.3.0"`
- **Missing secrets.yaml:** Create a local test secrets file
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
| ESPHome Version | 2025.3.0 |
| Python Version | 3.11 |
| Runner | ubuntu-latest |
| Cache | PlatformIO (~/.platformio) |

# Sense360 ESPHome Firmware

Official ESPHome firmware repository for [Sense360](https://mysense360.com) environmental monitoring devices.

[![ESPHome](https://img.shields.io/badge/ESPHome-2025.10%2B-blue)](https://esphome.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Release](https://img.shields.io/github/v/release/sense360store/esphome-public)](https://github.com/sense360store/esphome-public/releases)
[![CI - Build & Release Firmware](https://github.com/sense360store/esphome-public/actions/workflows/firmware-build-release.yml/badge.svg)](https://github.com/sense360store/esphome-public/actions/workflows/firmware-build-release.yml)
[![CI - Validate Firmware Configs](https://github.com/sense360store/esphome-public/actions/workflows/ci-validate-configs.yml/badge.svg)](https://github.com/sense360store/esphome-public/actions/workflows/ci-validate-configs.yml)

---

## Product Overview

The Sense360 system is a **modular smart home sensor platform** built around an ESP32-S3 core. Mix and match sensor modules to build the perfect environmental monitoring solution for any room.

### How It Works

```
CORE BOARD  +  POWER MODULE  +  SENSOR MODULES  =  Your Sense360
(Ceiling/Wall)   (USB/PoE/PWR)    (AirIQ/Comfort/Presence/Fan/Bathroom)
```

---

## Sensor Modules

### AirIQ - Air Quality Monitoring

Comprehensive air quality monitoring for health-conscious environments.

| Sensor | Measurements |
|--------|-------------|
| SPS30 | PM1.0, PM2.5, PM4.0, PM10 (Particulate Matter) |
| SGP41 | VOC Index, NOx Index (Air Quality) |
| SCD41 | CO2, Temperature, Humidity |
| BMP390 | Barometric Pressure |

**Best for:** Living rooms, bedrooms, offices, workshops

---

### Comfort - Environmental Monitoring

Basic environmental comfort sensing for everyday use.

| Sensor | Measurements |
|--------|-------------|
| SHT40 | Temperature, Humidity |
| LTR-303 | Ambient Light (Lux) |

**Best for:** Any room needing basic climate and light monitoring

---

### Presence - Occupancy Detection

mmWave radar-based presence detection for automation.

**For Presence Module (S360-PRES-C, S360-PRES-W):**

| Sensor | Features |
|--------|----------|
| HLK-LD2450 | Multi-target tracking (up to 3 targets), still/moving detection, zone-based sensing |
| DFRobot C4001 | 24GHz FMCW, 16m presence range, 25m motion range, speed measurement |

**For Presence Mini:**

| Sensor | Features |
|--------|----------|
| HLK-LD2450 | Multi-target tracking (up to 3 targets), still/moving detection, zone-based sensing |
| HLK-LD2412 | Single-zone detection, gate thresholds, better still detection (alternative option) |

**Best for:** Lighting automation, HVAC control, security

---

### Fan - HVAC Control

Fan speed control for ventilation automation.

| Interface | Output | Use Case |
|-----------|--------|----------|
| GP8403 DAC | 0-10V analog | Commercial HVAC, EC motors, VFDs |
| PWM | 25kHz PWM signal | Standard fans, 4-pin PC fans |

**Best for:** Bathroom ventilation, whole-house fans, HVAC integration

---

### Bathroom - Specialty Module

Optimized for bathroom environments. **Ceiling mount only. Replaces AirIQ (cannot be used together).**

| Variant | Sensors | Features |
|---------|---------|----------|
| Base | SHT4x, BMP390, SGP41 | Shower detection, mold risk, odor detection |
| Pro | + MLX90614, SPS30 | + IR surface temp, condensation risk, PM monitoring |

**Best for:** Bathrooms, laundry rooms, high-humidity areas

---

## Mounting Options

| Form Factor | Description | Available Modules |
|-------------|-------------|-------------------|
| **Ceiling** | Flush ceiling mount | AirIQ, Comfort, Presence, Fan, Bathroom |
| **Wall** | Wall or desk mount | AirIQ, Comfort, Presence, Fan |

---

## Power Options

| Option | Input | Description | Use Case |
|--------|-------|-------------|----------|
| **USB** | 5V USB-C | Built-in, no additional hardware | Development, portable setups |
| **PoE** | 36-57V DC (IEEE 802.3af/at) | Power over Ethernet module | Professional installations, single-cable runs |
| **PWR** | 100-240V AC | Mains power module (HLK-PM01) | Permanent installations |

---

## Core Boards

| SKU | Name | Form Factor | Description |
|-----|------|-------------|-------------|
| CORE-C | Sense360 Core | Ceiling | Standard ceiling-mount core |
| CORE-W | Sense360 Core | Wall/Desk | Standard wall/desk-mount core |

### Core Board Specifications

- **MCU**: ESP32-S3-WROOM-1-N16R8 (16MB Flash, 8MB PSRAM)
- **Connectivity**: WiFi 2.4GHz, Bluetooth 5.0 LE
- **I2C Buses**: Dual I2C for sensors and expansion
- **Relay**: Built-in 10A relay for load switching
- **Visual Indicators**: WS2812 addressable LED ring

---

## Product Configurations

### Ready-to-Use Products

The `products/` directory contains complete, tested configurations:

#### Full Sensor Packages (AirIQ + Comfort + Presence)

| Product | Mounting | Power Variants |
|---------|----------|----------------|
| Sense360 Core Ceiling | Ceiling | USB, PoE, PWR |
| Sense360 Core Wall | Wall/Desk | USB, PoE, PWR |

**Config files:**
- `products/sense360-core-ceiling.yaml`
- `products/sense360-core-wall.yaml`
- Power variants: `sense360-core-c-usb.yaml`, `sense360-core-c-poe.yaml`, `sense360-core-c-pwr.yaml`
- Power variants: `sense360-core-w-usb.yaml`, `sense360-core-w-poe.yaml`, `sense360-core-w-pwr.yaml`

#### Presence Only

| Product | Config File |
|---------|-------------|
| Sense360 Core Ceiling Presence | `products/sense360-core-ceiling-presence.yaml` |
| Sense360 Core Wall Presence | `products/sense360-core-wall-presence.yaml` |

#### Bathroom (Ceiling Only)

| Product | Config File |
|---------|-------------|
| Sense360 Core Ceiling Bathroom | `products/sense360-core-ceiling-bathroom.yaml` |

#### Specialty Products

| Product | Description | Config File |
|---------|-------------|-------------|
| Sense360 PoE | Ethernet-connected sensor hub | `products/sense360-poe.yaml` |
| Sense360 Fan PWM | 4-channel PWM fan controller | `products/sense360-fan-pwm.yaml` |
| Sense360 Ceiling S3 | Full ESP32-S3 ceiling board | `products/sense360-ceiling-s3-full.yaml` |

---

## Configuration Approaches

This repository supports three configuration methods. Choose based on your needs:

| Approach | Best For | Complexity |
|----------|----------|------------|
| **Product files** | Standard setups, most users | Simple |
| **Individual packages** | Custom module combinations | Moderate |
| **External components only** | From-scratch builds, experts | Advanced |

### Approach 1: Product Files (Recommended)

Use a single pre-built product file. Everything is included and tested:

```yaml
packages:
  sense360_firmware:
    url: https://github.com/sense360store/esphome-public
    ref: v3.0.0
    files:
      - products/sense360-core-ceiling.yaml
```

### Approach 2: Individual Packages

Pick and choose specific modules. See the [Package Reference](#package-reference) below:

```yaml
packages:
  sense360_base:
    url: https://github.com/sense360store/esphome-public
    ref: v3.0.0
    files:
      - packages/base/wifi.yaml
      - packages/base/api_encrypted.yaml
      - packages/expansions/presence_ceiling.yaml
```

### Approach 3: External Components Only (Expert)

⚠️ **Warning**: This only pulls C++ component code, NOT YAML configuration.

```yaml
external_components:
  - source:
      type: git
      url: https://github.com/sense360store/esphome-public
      ref: v3.0.0
    components: [ld2412, ld24xx]
```

With this approach, you must write ALL configuration yourself (UART, sensors, automations, etc.). Only use this if you need the radar drivers for a completely custom build.

---

## Quick Start Guide

### Step 1: Choose Your Configuration

Select a product configuration that matches your hardware and use case from the table above.

### Step 2: Configure Required Secrets

The firmware packages use secrets for WiFi, API, OTA, and web server authentication. Add these to your `secrets.yaml`:

```yaml
# WiFi credentials
wifi_ssid: "YourNetworkName"
wifi_password: "YourWiFiPassword"

# Security credentials
api_encryption_key: "GENERATE_WITH_ESPHOME_WIZARD"  # Generate: esphome wizard
ota_password: "your-secure-ota-password"

# Web server authentication (required)
web_username: "admin"
web_password: "your-secure-web-password"
```

> **Generate API Key**: Run `esphome wizard` or use: `openssl rand -base64 32`

### Step 3: Create Your Device Configuration

In your ESPHome dashboard, create a new file (e.g., `sense360-living-room.yaml`):

```yaml
# Load firmware from GitHub - this handles WiFi, API, OTA automatically via secrets
packages:
  sense360_firmware:
    url: https://github.com/sense360store/esphome-public
    ref: v3.0.0  # Always use a version tag (check releases for latest)
    files:
      - products/sense360-core-ceiling.yaml
    refresh: 1d

# Override device identification (optional)
substitutions:
  device_name: sense360-living-room
  friendly_name: "Living Room Sense360"
```

> **Important**: Do NOT add `wifi:`, `api:`, or `ota:` sections to your config. The packages already handle these using your secrets. Adding them again will cause conflicts.

### Step 4: Flash Your Device

1. **Initial flash**: Connect via USB-C, click "Install" > "Plug into this computer"
2. **Future updates**: Click "Install" > "Wirelessly"

---

## Module Combination Rules

You can combine modules freely with two constraints:

1. **AirIQ and Bathroom cannot be used together** (Bathroom replaces AirIQ)
2. **Bathroom is ceiling-only**

### Valid Combinations

**Ceiling:**
- Any single module: AirIQ, Comfort, Presence, Fan, Bathroom
- AirIQ + Comfort, AirIQ + Presence, AirIQ + Fan
- Bathroom + Comfort, Bathroom + Presence, Bathroom + Fan
- AirIQ + Comfort + Presence + Fan (full package)
- Bathroom + Comfort + Presence + Fan

**Wall:**
- Any single module: AirIQ, Comfort, Presence, Fan
- Any combination of: AirIQ, Comfort, Presence, Fan

---

## Package Reference

For custom builds using Approach 2, here are the available packages:

| Category | Package | Purpose |
|----------|---------|---------|
| **Base** | `packages/base/wifi.yaml` | WiFi connectivity |
| | `packages/base/api_encrypted.yaml` | Home Assistant API |
| | `packages/base/ota.yaml` | Over-the-air updates |
| | `packages/base/time.yaml` | Time synchronization |
| **Hardware** | `packages/hardware/sense360_core_ceiling.yaml` | Ceiling core board |
| | `packages/hardware/sense360_core_wall.yaml` | Wall core board |
| | `packages/hardware/led_ring_ceiling.yaml` | Ceiling LED ring |
| **Expansions** | `packages/expansions/presence_ceiling.yaml` | Presence module (ceiling) |
| | `packages/expansions/presence_wall.yaml` | Presence module (wall) |
| | `packages/expansions/fan_pwm.yaml` | PWM fan control |
| | `packages/expansions/airiq.yaml` | Air quality sensors |
| **Features** | `packages/features/presence_basic_profile.yaml` | Basic presence config |
| | `packages/features/fan_control_profile.yaml` | Fan automation |

See [docs/product-matrix.md](docs/product-matrix.md) for the complete module reference.

---

## Repository Structure

```
esphome-public/
├── products/           # Ready-to-use device configurations (start here)
├── packages/
│   ├── base/           # Core system (WiFi, API, OTA, logging)
│   ├── hardware/       # Core board and LED ring definitions
│   ├── expansions/     # Sensor module drivers
│   └── features/       # Feature profiles and behaviors
├── examples/           # Customer configuration templates
├── docs/               # Installation and configuration guides
└── tests/              # Validation and testing infrastructure
```

---

## Documentation

- [Product Matrix](docs/product-matrix.md) - Complete product hierarchy and module reference
- [Installation Guide](docs/installation.md) - Step-by-step setup instructions
- [Configuration Reference](docs/configuration.md) - Customization options
- [Development Guide](docs/development.md) - Contributing and testing
- [Changelog](CHANGELOG.md) - Version history

---

## System Requirements

- **ESPHome**: Version 2025.10.0 or newer
- **Home Assistant**: Version 2024.1.0 or newer (recommended)

---

## Use Cases

| Room | Recommended Modules | Why |
|------|---------------------|-----|
| Living Room | AirIQ + Comfort + Presence | Full environmental awareness + automation |
| Bedroom | Comfort + Presence | Sleep environment + lighting automation |
| Home Office | AirIQ + Presence | CO2 for productivity + occupancy |
| Bathroom | Bathroom + Presence + Fan | Humidity control + ventilation automation |
| Kitchen | AirIQ + Presence | Cooking air quality + occupancy |
| Workshop | AirIQ | VOC and PM monitoring for safety |

---

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/sense360store/esphome-public/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sense360store/esphome-public/discussions)
- **Email**: support@mysense360.com
- **Purchase**: [mysense360.com](https://mysense360.com)

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Future Products

- **Sense360 Voice**: Core boards with integrated voice assistant support (coming soon)

# Sense360 ESPHome Firmware

Official ESPHome firmware repository for [Sense360](https://mysense360.com) environmental monitoring devices.

[![ESPHome](https://img.shields.io/badge/ESPHome-2025.10%2B-blue)](https://esphome.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Release](https://img.shields.io/github/v/release/sense360store/esphome-public)](https://github.com/sense360store/esphome-public/releases)
[![CI](https://github.com/sense360store/esphome-public/workflows/Test%20ESPHome%20Configs/badge.svg)](https://github.com/sense360store/esphome-public/actions)

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

**For Sense360 Core and Presence Modules:**

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

## Quick Start Guide

### Step 1: Choose Your Configuration

Select a product configuration that matches your hardware and use case from the table above.

### Step 2: Create Your Device Configuration

In your ESPHome dashboard, create a new file (e.g., `sense360-living-room.yaml`):

```yaml
# Device identification
substitutions:
  device_name: sense360-living-room
  friendly_name: "Living Room Sense360"

# ESPHome configuration
esphome:
  name: ${device_name}
  friendly_name: ${friendly_name}
  min_version: 2025.10.0

# Load firmware from GitHub
packages:
  sense360_firmware:
    url: https://github.com/sense360store/esphome-public
    ref: v2.2.0  # Use the latest stable version
    files:
      - products/sense360-core-ceiling.yaml
    refresh: 1d

# WiFi credentials (stored in secrets.yaml)
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

# Home Assistant API
api:
  encryption:
    key: !secret api_encryption_key

# Over-the-air updates
ota:
  - platform: esphome
    password: !secret ota_password
```

### Step 3: Configure Secrets

Add to your `secrets.yaml`:

```yaml
wifi_ssid: "YourNetworkName"
wifi_password: "YourWiFiPassword"
api_encryption_key: "GENERATE_WITH_ESPHOME_WIZARD"
ota_password: "your-secure-password"
```

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

## Advanced Configuration

For custom module combinations, load individual packages:

```yaml
packages:
  sense360_base:
    url: https://github.com/sense360store/esphome-public
    ref: v2.2.0
    files:
      # Base system
      - packages/base/wifi.yaml
      - packages/base/api_encrypted.yaml
      - packages/base/ota.yaml
      - packages/base/time.yaml
      # Core hardware
      - packages/hardware/sense360_core_ceiling.yaml
      - packages/hardware/led_ring_ceiling.yaml
      # Modules - pick what you need
      - packages/expansions/presence_ceiling.yaml
      - packages/features/presence_basic_profile.yaml
      - packages/expansions/fan_pwm.yaml
      - packages/features/fan_control_profile.yaml
    refresh: 1d
```

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

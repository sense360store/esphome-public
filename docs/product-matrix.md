# Sense360 Product Matrix

Complete product hierarchy and configuration guide for the Sense360 modular sensor platform.

## Table of Contents

- [Product Overview](#product-overview)
- [Quick Assembly Guide](#quick-assembly-guide)
- [Core Boards](#core-boards)
- [Power Modules](#power-modules)
- [LED Rings](#led-rings)
- [Sensor Modules](#sensor-modules)
- [Module Combination Rules](#module-combination-rules)
- [Fan Control Modules](#fan-control-modules)
- [Pre-Built Product Configurations](#pre-built-product-configurations)
- [Configuration Examples](#configuration-examples)

---

## Product Overview

The Sense360 system is a modular smart home sensor platform built around an ESP32-S3 core. The system consists of:

1. **Core Board** - The ESP32-S3 base that connects all modules
2. **Power Module** - How the system is powered (USB, POE, or PWR)
3. **LED Ring** - Visual feedback (Standard LED or LED+MIC for voice)
4. **Sensor Modules** - Optional expansion modules (AirIQ, Comfort, Presence, Bathroom, Fan)

---

## Quick Assembly Guide

Building a Sense360 system follows this simple formula:

```
CORE (1x) + POWER (1x) + LED (see rules) + MODULES (any combination*)

* Only constraint: AirIQ and Bathroom cannot be used together
```

### Step 1: Choose Your Core

| SKU | Name | Form Factor | Description |
|-----|------|-------------|-------------|
| **CORE-C** | Core Ceiling | Ceiling mount | Standard ceiling-mount core |
| **CORE-W** | Core Wall | Wall/Desk mount | Standard wall/desk-mount core |

### Step 2: Choose Your Power

| Option | SKU | Description |
|--------|-----|-------------|
| USB | - | Built-in USB-C (development, portable) |
| POE | S360-POE | Power over Ethernet (professional installations) |
| PWR | S360-PWR | 240V AC mains power (permanent installations) |

### Step 3: Add LED Ring (Optional)

| Core Type | LED Ring | Description |
|-----------|----------|-------------|
| CORE-C | Standard LED (Ceiling) | Visual feedback for air quality and status |
| CORE-W | Standard LED (Wall) | Visual feedback for air quality and status |

### Step 4: Add Modules

Add any combination of modules following the [Module Combination Rules](#module-combination-rules).

### Assembly Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                     CORE BOARD (Required)                    │
│  ┌─────────────────────┐    ┌─────────────────────────────┐ │
│  │  Ceiling Variant    │    │     Wall/Desk Variant       │ │
│  │  - CORE-C           │    │     - CORE-W                │ │
│  └─────────────────────┘    └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ POWER MODULE  │    │   LED RING    │    │SENSOR MODULES │
│  (Required)   │    │  (Optional)   │    │  (Optional)   │
│               │    │               │    │               │
│  - USB        │    │  Standard LED │    │  - AirIQ      │
│  - POE        │    │  (Ceiling or  │    │  - Comfort    │
│  - PWR (240V) │    │   Wall)       │    │  - Presence   │
│               │    │               │    │  - Bathroom*  │
│               │    │               │    │  - Fan GP8403 │
│               │    │               │    │  - Fan PWM    │
└───────────────┘    └───────────────┘    └───────────────┘

* Bathroom is Ceiling-only and replaces AirIQ
```

---

## Core Boards

The core board contains the ESP32-S3 microcontroller and provides connections for all modules.

| Project Name | Product Name | Variant | SKU | Description |
|-------------|--------------|---------|-----|-------------|
| `Sense360_Core_Ceiling` | Sense 360 Core | Ceiling | S360-CORE-C | Base core for ceiling mount installations |
| `Sense360_Core_Wall` | Sense 360 Core | Wall/Desk | S360-CORE-W | Base core for wall-mounted or desk installations |
| `Sense360_Core_Mini` | Sense 360 Mini | Compact | S360-MINI | Compact board with integrated sensors |

> **Future Product**: Sense360 Voice (CORE-V-C, CORE-V-W) - Core boards with integrated voice assistant support (coming soon)

### Sense360 Mini - Integrated Sensors

The Mini board has sensors integrated directly on the PCB (no expansion modules needed):

| Designator | Sensor | I2C Address | Measurements |
|------------|--------|-------------|--------------|
| U4 | LTR-303ALS-01 | 0x29 | Ambient Light (lux) |
| U3 | SHT30-DIS | 0x44 | Temperature, Humidity |
| U5 | SCD40-D-R2 | 0x62 | CO2 (ppm) |

**Mini External Connectors:**
- **JST3_UART**: TX/RX for LD2412 radar (115200 baud)
- **JST4_SEN**: I2C for external sensors (e.g., SEN55 @ 0x69)
- **JST4_RADAR**: GPIO11/12 for TRIG/ECHO (not used with LD2412)

**Mini Pin Assignments:**
| Function | GPIO | Notes |
|----------|------|-------|
| I2C SDA | 48 | Onboard sensors |
| I2C SCL | 45 | Strapping pin (warning expected) |
| UART TX | 43 | Radar via JST3_UART |
| UART RX | 44 | Radar via JST3_UART |
| LED Data | 8 | WS2812B via level shifter |
| Boot Button | 0 | Input |

**Mini Package Files:**
```yaml
# Core Mini hardware
packages:
  core: !include packages/hardware/sense360_core_mini.yaml

# Onboard sensors (LTR-303, SHT30, SCD40)
packages:
  onboard_sensors: !include packages/hardware/mini_onboard_sensors.yaml

# LD2412 Radar (for presence detection)
packages:
  presence: !include packages/hardware/presence_ld2412.yaml
```

**Mini Product Configurations:**
| Product | Description | Config File |
|---------|-------------|-------------|
| Mini AirIQ Basic | Air quality + presence | `products/sense360-mini-airiq-basic.yaml` |
| Mini AirIQ + LD2412 | Air quality + LD2412 radar | `products/sense360-mini-airiq-ld2412.yaml` |
| Mini Full LD2412 | Full sensors + LD2412 | `products/sense360-mini-full-ld2412.yaml` |
| Mini Presence | Presence detection only | `products/sense360-mini-presence.yaml` |
| Mini Presence LD2412 | Presence with LD2412 | `products/sense360-mini-presence-ld2412.yaml` |

### Core Board Specifications

- **MCU**: ESP32-S3-WROOM-1-N16R8 (16MB Flash, 8MB PSRAM)
- **Connectivity**: WiFi 2.4GHz, Bluetooth 5.0 LE
- **I2C Buses**: Dual I2C for sensors and expansion
- **UART**: For presence sensor communication
- **Relay**: Built-in 10A relay for load switching

### YAML Package Files

```yaml
# Ceiling Core (non-voice)
packages:
  core: !include packages/hardware/sense360_core_ceiling.yaml

# Ceiling Core with Voice
packages:
  core: !include packages/hardware/sense360_core_voice_ceiling.yaml

# Wall/Desk Core (non-voice)
packages:
  core: !include packages/hardware/sense360_core_wall.yaml

# Wall/Desk Core with Voice
packages:
  core: !include packages/hardware/sense360_core_voice_wall.yaml
```

---

## Power Modules

Choose how to power your Sense360 system. Only one power option is needed.

| Project Name | Product Name | Compatible With | SKU | Description |
|-------------|--------------|-----------------|-----|-------------|
| `Sense360_Power_POE` | Sense 360 POE | Ceiling + Wall/Desk | S360-POE | IEEE 802.3af PoE power module |
| `Sense360_Power_PWR` | Sense 360 PWR | Ceiling + Wall/Desk | S360-PWR | 240V AC mains power module |
| *(USB)* | *(Built-in)* | Ceiling + Wall/Desk | - | USB-C power (built into core) |

### Power Module Specifications

| Module | Input | Output | Use Case |
|--------|-------|--------|----------|
| POE | 36-57V DC (PoE) | 5V/2A | Professional installations, single cable |
| PWR | 100-240V AC | 5V/2A | Permanent installations |
| USB | 5V USB-C | 5V/2A | Development, portable setups |

### YAML Package Files

```yaml
# PoE Power
packages:
  power: !include packages/hardware/power_poe.yaml

# 240V AC Power
packages:
  power: !include packages/hardware/power_240v.yaml

# USB Power (no additional package needed - built into core)
```

---

## LED Rings

LED rings provide visual feedback for air quality, presence, and system status.

| Project Name | Product Name | Variant | SKU | Pairs With |
|-------------|--------------|---------|-----|------------|
| `Sense360_LED_Ceiling` | Sense 360 LEDs | Ceiling | S360-LED-C | Core Ceiling |
| `Sense360_LED_Wall` | Sense 360 LEDs | Wall/Desk | S360-LED-W | Core Wall |

### LED Ring Specifications

| Ring Type | LEDs | Description |
|-----------|------|-------------|
| Standard Ceiling (S360-LED-C) | WS2812B RGB | Visual feedback for ceiling mount |
| Standard Wall (S360-LED-W) | WS2812B RGB | Visual feedback for wall/desk mount |

### YAML Package Files

```yaml
# Standard LED Ring (Ceiling)
packages:
  led_ring: !include packages/hardware/led_ring_ceiling.yaml

# Standard LED Ring (Wall/Desk)
packages:
  led_ring: !include packages/hardware/led_ring_wall.yaml
```

> **Future Product**: LED+MIC rings (S360-LED-V-C, S360-LED-V-W) for Sense360 Voice (coming soon)

---

## Sensor Modules

Optional expansion modules for environmental monitoring and presence detection.

### AirIQ Module (Air Quality)

Comprehensive air quality monitoring with multiple sensors.

| Project Name | Product Name | Variant | SKU | Sensors |
|-------------|--------------|---------|-----|---------|
| `Sense360_Module_AirIQ_Ceiling` | Sense 360 AirIQ | Ceiling | S360-AIR-C | SPS30, SGP41, SCD41, BMP390 |
| `Sense360_Module_AirIQ_Wall` | Sense 360 AirIQ | Wall/Desk | S360-AIR-W | SPS30, SGP41, SCD41, BMP390 |

**Measured Parameters:**
- CO2 (SCD41)
- VOC/NOx Index (SGP41)
- PM1.0, PM2.5, PM4.0, PM10 (SPS30)
- Temperature & Humidity (SCD41)
- Barometric Pressure (BMP390)

### Comfort Module

Basic environmental comfort monitoring.

| Project Name | Product Name | Variant | SKU | Sensors |
|-------------|--------------|---------|-----|---------|
| `Sense360_Module_Comfort_Ceiling` | Sense 360 Comfort | Ceiling | S360-CMFT-C | SHT40, LTR-303 |
| `Sense360_Module_Comfort_Wall` | Sense 360 Comfort | Wall/Desk | S360-CMFT-W | SHT40, LTR-303 |

**Measured Parameters:**
- Temperature (SHT40)
- Humidity (SHT40)
- Ambient Light (LTR-303)

### Presence Module

mmWave radar-based presence and occupancy detection.

| Project Name | Product Name | Variant | SKU | Sensors |
|-------------|--------------|---------|-----|---------|
| `Sense360_Module_Presence_Ceiling` | Sense 360 Presence | Ceiling | S360-PRES-C | HLK-LD2450, DFRobot C4001 |
| `Sense360_Module_Presence_Wall` | Sense 360 Presence | Wall/Desk | S360-PRES-W | HLK-LD2450, DFRobot C4001 |

**Sensors:**

| Sensor | Features | Best For |
|--------|----------|----------|
| HLK-LD2450 | Multi-target tracking (up to 3 targets), still/moving detection, distance/angle measurement | General presence detection with target counting |
| DFRobot C4001 | 24GHz FMCW, 16m presence range, 25m motion range, speed measurement | Long-range detection, speed-based automation |

**Features:**
- Multi-target tracking (up to 3 targets with LD2450)
- Still and moving target differentiation
- Zone-based detection
- Distance and angle measurement
- Speed measurement (C4001)

### Bathroom Module

Specialized module for bathroom environments. **Ceiling mount only.**

| Project Name | Product Name | Variant | SKU | Sensors |
|-------------|--------------|---------|-----|---------|
| `Sense360_Module_Bathroom_Base` | Sense 360 Bathroom Base | Ceiling | S360-BATH-B | SHT4x, BMP390, SGP41 |
| `Sense360_Module_Bathroom_Pro` | Sense 360 Bathroom Pro | Ceiling | S360-BATH-P | SHT4x, BMP390, SGP41, MLX90614, SPS30 |

> **Note**: The Bathroom module **replaces the AirIQ module** - they cannot be used together.

**Bathroom Base Features:**
- SHT4x (Temperature, Humidity)
- BMP390 (Pressure)
- SGP41 (VOC/NOx)

**Bathroom Pro (additional):**
- MLX90614 (IR surface temperature / condensation risk)
- SPS30 (PM1.0, PM2.5, PM10)

**Special Features:**
- Shower detection (humidity spike analysis)
- Mold risk assessment
- Ventilation recommendations
- Odor detection

### YAML Package Files

```yaml
# AirIQ Module (Ceiling)
packages:
  airiq: !include packages/expansions/airiq_ceiling.yaml
  airiq_profile: !include packages/features/airiq_basic_profile.yaml

# AirIQ Module (Wall/Desk)
packages:
  airiq: !include packages/expansions/airiq_wall.yaml
  airiq_profile: !include packages/features/airiq_basic_profile.yaml

# Comfort Module (Ceiling)
packages:
  comfort: !include packages/expansions/comfort_ceiling.yaml
  comfort_profile: !include packages/features/comfort_basic_profile.yaml

# Comfort Module (Wall/Desk)
packages:
  comfort: !include packages/expansions/comfort_wall.yaml
  comfort_profile: !include packages/features/comfort_basic_profile.yaml

# Presence Module (Ceiling)
packages:
  presence: !include packages/expansions/presence_ceiling.yaml
  presence_profile: !include packages/features/presence_basic_profile.yaml

# Presence Module (Wall/Desk)
packages:
  presence: !include packages/expansions/presence_wall.yaml
  presence_profile: !include packages/features/presence_basic_profile.yaml

# Bathroom Module Base (Ceiling only)
packages:
  bathroom: !include packages/expansions/airiq_bathroom_base.yaml
  bathroom_profile: !include packages/features/bathroom_profile.yaml

# Bathroom Module Pro (Ceiling only)
packages:
  bathroom: !include packages/expansions/airiq_bathroom_pro.yaml
  bathroom_profile: !include packages/features/bathroom_pro_profile.yaml
```

---

## Module Combination Rules

This section defines all valid module combinations for Ceiling and Wall configurations.

### The Complete Rule

Any module can be used on its own OR in any combination, with only two constraints:

**Ceiling Constraints:**
1. AirIQ-C and Bathroom-C **cannot be used together**
2. Everything else is free: Comfort, Presence, Fan can appear alone, paired, triple, added to AirIQ, added to Bathroom, or with no environmental module at all

**Wall Constraints:**
1. Wall has **no Bathroom module** (Bathroom is ceiling-only)
2. Everything else is free: AirIQ, Comfort, Presence, Fan can appear alone or in any mix

---

### Ceiling Module Configurations

All valid module combinations for ceiling-mounted cores (CORE-C, CORE-V-C):

#### Single-Module Builds
- Comfort only
- Presence only
- Fan only
- AirIQ only
- Bathroom only

#### Two-Module Builds
- Comfort + Presence
- Comfort + Fan
- Presence + Fan
- AirIQ + Comfort
- AirIQ + Presence
- AirIQ + Fan
- Bathroom + Comfort
- Bathroom + Presence
- Bathroom + Fan

#### Three-Module Builds
- Comfort + Presence + Fan
- AirIQ + Comfort + Presence
- AirIQ + Comfort + Fan
- AirIQ + Presence + Fan
- Bathroom + Comfort + Presence
- Bathroom + Comfort + Fan
- Bathroom + Presence + Fan

#### Four-Module Builds
- AirIQ + Comfort + Presence + Fan
- Bathroom + Comfort + Presence + Fan

---

### Wall/Desk Module Configurations

All valid module combinations for wall-mounted cores (CORE-W, CORE-V-W):

> **Note:** No Bathroom module for Wall configurations.

#### Single-Module Builds
- Comfort only
- Presence only
- Fan only
- AirIQ only

#### Two-Module Builds
- Comfort + Presence
- Comfort + Fan
- Presence + Fan
- AirIQ + Comfort
- AirIQ + Presence
- AirIQ + Fan

#### Three-Module Builds
- Comfort + Presence + Fan
- AirIQ + Comfort + Presence
- AirIQ + Comfort + Fan
- AirIQ + Presence + Fan

#### Four-Module Builds
- AirIQ + Comfort + Presence + Fan

---

## Fan Control Modules

Optional modules for HVAC fan control.

| Project Name | Product Name | Compatible With | SKU | Interface |
|-------------|--------------|-----------------|-----|-----------|
| `Sense360_Module_GP8403` | Sense 360 Fan GP8403 | Ceiling + Wall/Desk | S360-GP8403 | 0-10V analog (DAC) |
| `Sense360_Module_PWM` | Sense 360 Fan PWM | Ceiling + Wall/Desk | S360-PWM | PWM signal |

### Fan Control Specifications

| Module | Output | Resolution | Use Case |
|--------|--------|------------|----------|
| GP8403 | 0-10V or 0-5V | 12-bit (0.01V) | Commercial HVAC, EC motors, VFDs |
| PWM | 25kHz PWM | 8-bit | Standard PWM fans, 4-pin PC fans |

### YAML Package Files

```yaml
# GP8403 DAC Fan Control
packages:
  fan: !include packages/expansions/fan_gp8403.yaml
  fan_profile: !include packages/features/fan_control_profile.yaml

# PWM Fan Control
packages:
  fan: !include packages/expansions/fan_pwm.yaml
  fan_profile: !include packages/features/fan_control_profile.yaml
```

---

## Pre-Built Product Configurations

The `products/` directory contains ready-to-use configurations for common setups.

### Core Products (Recommended)

| Product File | Description | Core | Modules |
|--------------|-------------|------|---------|
| `sense360-core-ceiling.yaml` | Full ceiling with all modules | CORE-C | AirIQ + Comfort + Presence |
| `sense360-core-ceiling-presence.yaml` | Ceiling presence only | CORE-C | Presence |
| `sense360-core-ceiling-bathroom.yaml` | Ceiling bathroom installation | CORE-C | Bathroom + Presence |
| `sense360-core-wall.yaml` | Full wall with all modules | CORE-W | AirIQ + Comfort + Presence |
| `sense360-core-wall-presence.yaml` | Wall presence only | CORE-W | Presence |

### Power Variant Products

Each core product is available with specific power configurations:

| Base Product | USB Variant | PoE Variant | PWR Variant |
|--------------|-------------|-------------|-------------|
| Core Ceiling | `sense360-core-c-usb.yaml` | `sense360-core-c-poe.yaml` | `sense360-core-c-pwr.yaml` |
| Core Wall | `sense360-core-w-usb.yaml` | `sense360-core-w-poe.yaml` | `sense360-core-w-pwr.yaml` |

### Specialty Products

| Product File | Description | Hardware |
|--------------|-------------|----------|
| `sense360-ceiling-s3-full.yaml` | Full-featured ESP32-S3 ceiling board | Sense360 Ceiling S3 |
| `sense360-poe.yaml` | Power over Ethernet configuration | Sense360 PoE |
| `sense360-fan-pwm.yaml` | 4-channel PWM fan controller | Sense360 Fan PWM |

---

## Configuration Examples

### Example 1: Core Ceiling with Full Monitoring

Complete ceiling-mounted system with AirIQ, Comfort, and Presence.

```yaml
substitutions:
  device_name: "sense360-living-room"
  friendly_name: "Living Room Sense360"

packages:
  # Use the pre-built Core Ceiling configuration
  sense360_firmware:
    url: https://github.com/sense360store/esphome-public
    ref: v2.2.0
    files:
      - products/sense360-core-ceiling.yaml
    refresh: 1d

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_encryption_key

ota:
  - platform: esphome
    password: !secret ota_password
```

### Example 2: Core Wall with All Sensors

Wall-mounted system with full environmental monitoring.

```yaml
substitutions:
  device_name: "sense360-bedroom"
  friendly_name: "Bedroom Sense360"

packages:
  sense360_firmware:
    url: https://github.com/sense360store/esphome-public
    ref: v2.2.0
    files:
      - products/sense360-core-wall.yaml
    refresh: 1d

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_encryption_key

ota:
  - platform: esphome
    password: !secret ota_password
```

### Example 3: Core Ceiling Bathroom Installation

Bathroom-specific ceiling installation with shower detection and fan control.

```yaml
substitutions:
  device_name: "sense360-bathroom"
  friendly_name: "Bathroom Sense360"

packages:
  sense360_firmware:
    url: https://github.com/sense360store/esphome-public
    ref: v2.2.0
    files:
      - products/sense360-core-ceiling-bathroom.yaml
    refresh: 1d

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_encryption_key

ota:
  - platform: esphome
    password: !secret ota_password
```

### Example 4: Custom Module Combination (Presence + Fan Only)

For minimal builds with specific modules.

```yaml
substitutions:
  device_name: "sense360-hallway"
  friendly_name: "Hallway Sense360"

packages:
  # Base System
  base_wifi: !include packages/base/wifi.yaml
  base_api: !include packages/base/api_encrypted.yaml
  base_ota: !include packages/base/ota.yaml
  base_time: !include packages/base/time.yaml

  # Core Hardware
  core: !include packages/hardware/sense360_core_ceiling.yaml

  # LED Ring (optional)
  led_ring: !include packages/hardware/led_ring_ceiling.yaml

  # Modules - Presence + Fan only
  presence: !include packages/expansions/presence_ceiling.yaml
  presence_profile: !include packages/features/presence_basic_profile.yaml
  fan: !include packages/expansions/fan_pwm.yaml
  fan_profile: !include packages/features/fan_control_profile.yaml

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_encryption_key

ota:
  - platform: esphome
    password: !secret ota_password
```

---

## Quick Reference: SKU to Package Mapping

### Core Boards
| SKU | Package File |
|-----|--------------|
| S360-CORE-C | `packages/hardware/sense360_core_ceiling.yaml` |
| S360-CORE-W | `packages/hardware/sense360_core_wall.yaml` |

### Power Modules
| SKU | Package File |
|-----|--------------|
| S360-POE | `packages/hardware/power_poe.yaml` |
| S360-PWR | `packages/hardware/power_240v.yaml` |

### LED Rings
| SKU | Package File |
|-----|--------------|
| S360-LED-C | `packages/hardware/led_ring_ceiling.yaml` |
| S360-LED-W | `packages/hardware/led_ring_wall.yaml` |

### Sensor Modules
| SKU | Package File |
|-----|--------------|
| S360-AIR-C | `packages/expansions/airiq_ceiling.yaml` |
| S360-AIR-W | `packages/expansions/airiq_wall.yaml` |
| S360-CMFT-C | `packages/expansions/comfort_ceiling.yaml` |
| S360-CMFT-W | `packages/expansions/comfort_wall.yaml` |
| S360-PRES-C | `packages/expansions/presence_ceiling.yaml` |
| S360-PRES-W | `packages/expansions/presence_wall.yaml` |
| S360-BATH-B | `packages/expansions/airiq_bathroom_base.yaml` |
| S360-BATH-P | `packages/expansions/airiq_bathroom_pro.yaml` |
| S360-GP8403 | `packages/expansions/fan_gp8403.yaml` |
| S360-PWM | `packages/expansions/fan_pwm.yaml` |

---

## Need Help?

- [Installation Guide](installation.md)
- [Configuration Reference](configuration.md)
- [GitHub Issues](https://github.com/sense360store/esphome-public/issues)
- **Support**: support@mysense360.com

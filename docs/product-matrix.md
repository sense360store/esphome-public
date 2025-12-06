# Sense360 Product Matrix

Complete product hierarchy and configuration guide for the Sense360 modular sensor platform.

## Table of Contents

- [Product Overview](#product-overview)
- [Core Boards](#core-boards)
- [Power Modules](#power-modules)
- [LED Rings](#led-rings)
- [Sensor Modules](#sensor-modules)
- [Fan Control Modules](#fan-control-modules)
- [Configuration Examples](#configuration-examples)

---

## Product Overview

The Sense360 system is a modular smart home sensor platform built around an ESP32-S3 core. The system consists of:

1. **Core Board** - The ESP32-S3 base that connects all modules
2. **Power Module** - How the system is powered (USB, POE, or 240V)
3. **LED Ring** - Visual feedback (Standard or with Microphones for voice)
4. **Sensor Modules** - Optional expansion modules (AirIQ, Comfort, Presence, Bathroom)
5. **Fan Control** - Optional fan control modules (GP8403 DAC or PWM)

### Assembly Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                     CORE BOARD (Required)                    │
│  ┌─────────────────────┐    ┌─────────────────────────────┐ │
│  │  Ceiling Variants   │    │     Wall/Desk Variants      │ │
│  │  - Core Ceiling     │    │     - Core Desk             │ │
│  │  - Core Voice Ceil. │    │     - Core Voice Desk       │ │
│  └─────────────────────┘    └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ POWER MODULE  │    │   LED RING    │    │SENSOR MODULES │
│  (Required)   │    │  (Optional)   │    │  (Optional)   │
│  - USB        │    │  - Standard   │    │  - AirIQ      │
│  - POE        │    │  - LED+MIC    │    │  - Comfort    │
│  - PWR (240V) │    │               │    │  - Presence   │
└───────────────┘    └───────────────┘    │  - Bathroom   │
                                          │  - Fan GP8403 │
                                          │  - Fan PWM    │
                                          └───────────────┘
```

---

## Core Boards

The core board contains the ESP32-S3 microcontroller and provides connections for all modules.

| Project Name | Product Name | Variant | SKU | Description |
|-------------|--------------|---------|-----|-------------|
| `Sense360_Core_Ceiling` | Sense 360 Core | Ceiling | S360-CORE-C | Base core for ceiling mount installations |
| `Sense360_Core_Voice_Ceiling` | Sense 360 Core Voice | Ceiling | S360-CORE-V-C | Core with voice assistant/speaker support |
| `Sense360_Core_Desk` | Sense 360 Core | Wall/Desk | S360-CORE-W | Base core for wall-mounted or desk installations |
| `Sense360_Core_Voice_Desk` | Sense 360 Core Voice | Wall/Desk | S360-CORE-V-W | Core with voice assistant/speaker support |

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
| `Sense360_LED_Ceiling` | Sense 360 LEDs | Ceiling | S360-LED-C | Core Ceiling (non-voice) |
| `Sense360_LED_MIC_Ceiling` | Sense 360 LED+Mics | Ceiling | S360-LED-V-C | Core Voice Ceiling |
| `Sense360_LED_Wall` | Sense 360 LEDs | Wall/Desk | S360-LED-C | Core Desk (non-voice) |
| `Sense360_LED_MIC_Wall` | Sense 360 LED+Mics | Wall/Desk | S360-LED-V-C | Core Voice Desk |

### LED Ring Pairing Rules

> **Important**: Match LED ring type to core board type:
> - **Standard LED Ring** → Non-voice Core boards
> - **LED+MIC Ring** → Voice Core boards

### LED Ring Specifications

| Ring Type | LEDs | Microphones | Use Case |
|-----------|------|-------------|----------|
| Standard (S360-LED-C) | WS2812B RGB | None | Visual feedback only |
| LED+MIC (S360-LED-V-C) | WS2812B RGB | I2S MEMS array | Voice assistant support |

### YAML Package Files

```yaml
# Standard LED Ring (Ceiling)
packages:
  led_ring: !include packages/hardware/led_ring_ceiling.yaml

# LED+MIC Ring (Ceiling Voice)
packages:
  led_ring: !include packages/hardware/led_ring_mic_ceiling.yaml

# Standard LED Ring (Wall/Desk)
packages:
  led_ring: !include packages/hardware/led_ring_wall.yaml

# LED+MIC Ring (Wall/Desk Voice)
packages:
  led_ring: !include packages/hardware/led_ring_mic_wall.yaml
```

---

## Sensor Modules

Optional expansion modules for environmental monitoring and presence detection.

### AirIQ Module (Air Quality)

Comprehensive air quality monitoring with multiple sensors.

| Project Name | Product Name | Variant | SKU | Sensors |
|-------------|--------------|---------|-----|---------|
| `Sense360_Module_AirIQ_Ceiling` | Sense 360 AirIQ | Ceiling | S360-AIR-C | SPS30, SGP41, SCD41, BMP390, MiCS4514, Formaldehyde, Ozone |
| `Sense360_Module_AirIQ_Wall` | Sense 360 AirIQ | Wall/Desk | S360-AIR-W | SPS30, SGP41, SCD41, BMP390, MiCS4514, Formaldehyde, Ozone |

**Measured Parameters:**
- CO2 (SCD41)
- VOC/NOx Index (SGP41)
- PM1.0, PM2.5, PM4.0, PM10, Particle Count (SPS30)
- Temperature & Humidity (SCD41)
- Barometric Pressure (BMP390)
- Formaldehyde
- Ozone

> **Note:** The Mini ESP products use the SEN55 all-in-one sensor instead of the SPS30+SGP41 combination.

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

| Project Name | Product Name | Variant | SKU | Sensor |
|-------------|--------------|---------|-----|--------|
| `Sense360_Module_Presence_Ceiling` | Sense 360 Presence | Ceiling | S360-PRES-C | SEN0609 / HLK-LD2450 |
| `Sense360_Module_Presence_Wall` | Sense 360 Presence | Wall/Desk | S360-PRES-W | SEN0609 / HLK-LD2450 |

**Features:**
- Multi-target tracking (up to 3 targets)
- Still and moving target differentiation
- Zone-based detection
- Distance and angle measurement

### Bathroom Module

Specialized module for bathroom environments. **Ceiling mount only.**

| Project Name | Product Name | Variant | SKU | Sensors |
|-------------|--------------|---------|-----|---------|
| `Sense360_Module_Bathroom_Ceiling` | Sense 360 Bathroom | Ceiling | S360-BATH-C | See below |

> **Note**: The Bathroom module can **replace the AirIQ module** for bathroom-specific monitoring.

**AirIQ Bathroom Base:**
- SHT4x (Temperature, Humidity)
- BMP390 (Pressure)
- SGP41 (VOC/NOx)

**AirIQ Bathroom Pro (additional):**
- SHT4x, BMP390, SGP41
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

# Bathroom Module (Ceiling only)
packages:
  bathroom: !include packages/expansions/bathroom.yaml
  bathroom_profile: !include packages/features/bathroom_profile.yaml
```

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

## Configuration Examples

### Example 1: Ceiling Installation with Full Air Quality

Complete ceiling-mounted system with AirIQ and presence detection.

```yaml
substitutions:
  device_name: "sense360-living-room"
  friendly_name: "Living Room Sense360"

packages:
  # Core board
  core: !include packages/hardware/sense360_core_ceiling.yaml

  # Power (choose one)
  power: !include packages/hardware/power_poe.yaml

  # LED ring (standard for non-voice)
  led_ring: !include packages/hardware/led_ring_ceiling.yaml

  # Modules
  airiq: !include packages/expansions/airiq_ceiling.yaml
  airiq_profile: !include packages/features/airiq_basic_profile.yaml

  presence: !include packages/expansions/presence_ceiling.yaml
  presence_profile: !include packages/features/presence_basic_profile.yaml

  # Base configuration
  wifi: !include packages/base/wifi.yaml
  api: !include packages/base/api_encrypted.yaml
  ota: !include packages/base/ota.yaml
```

### Example 2: Wall-Mounted Voice Assistant

Wall-mounted system with voice assistant and comfort monitoring.

```yaml
substitutions:
  device_name: "sense360-bedroom"
  friendly_name: "Bedroom Sense360"

packages:
  # Core board (voice variant)
  core: !include packages/hardware/sense360_core_voice_wall.yaml

  # Power
  power: !include packages/hardware/power_240v.yaml

  # LED ring (MIC variant for voice)
  led_ring: !include packages/hardware/led_ring_mic_wall.yaml

  # Modules
  comfort: !include packages/expansions/comfort_wall.yaml
  comfort_profile: !include packages/features/comfort_basic_profile.yaml

  # Base configuration
  wifi: !include packages/base/wifi.yaml
  api: !include packages/base/api_encrypted.yaml
  ota: !include packages/base/ota.yaml
```

### Example 3: Bathroom Ceiling Installation

Bathroom-specific ceiling installation with shower detection.

```yaml
substitutions:
  device_name: "sense360-bathroom"
  friendly_name: "Bathroom Sense360"

packages:
  # Core board
  core: !include packages/hardware/sense360_core_ceiling.yaml

  # Power
  power: !include packages/hardware/power_poe.yaml

  # LED ring
  led_ring: !include packages/hardware/led_ring_ceiling.yaml

  # Bathroom module (replaces AirIQ for bathrooms)
  bathroom: !include packages/expansions/bathroom.yaml
  bathroom_profile: !include packages/features/bathroom_profile.yaml

  # Fan control for exhaust fan
  fan: !include packages/expansions/fan_pwm.yaml
  fan_profile: !include packages/features/fan_control_profile.yaml

  # Base configuration
  wifi: !include packages/base/wifi.yaml
  api: !include packages/base/api_encrypted.yaml
  ota: !include packages/base/ota.yaml
```

---

## Quick Reference: SKU to Package Mapping

| SKU | Package File |
|-----|--------------|
| S360-CORE-C | `packages/hardware/sense360_core_ceiling.yaml` |
| S360-CORE-V-C | `packages/hardware/sense360_core_voice_ceiling.yaml` |
| S360-CORE-W | `packages/hardware/sense360_core_wall.yaml` |
| S360-CORE-V-W | `packages/hardware/sense360_core_voice_wall.yaml` |
| S360-POE | `packages/hardware/power_poe.yaml` |
| S360-PWR | `packages/hardware/power_240v.yaml` |
| S360-LED-C | `packages/hardware/led_ring_ceiling.yaml` or `led_ring_wall.yaml` |
| S360-LED-V-C | `packages/hardware/led_ring_mic_ceiling.yaml` or `led_ring_mic_wall.yaml` |
| S360-AIR-C | `packages/expansions/airiq_ceiling.yaml` |
| S360-AIR-W | `packages/expansions/airiq_wall.yaml` |
| S360-CMFT-C | `packages/expansions/comfort_ceiling.yaml` |
| S360-CMFT-W | `packages/expansions/comfort_wall.yaml` |
| S360-PRES-C | `packages/expansions/presence_ceiling.yaml` |
| S360-PRES-W | `packages/expansions/presence_wall.yaml` |
| S360-BATH-C | `packages/expansions/bathroom.yaml` |
| S360-GP8403 | `packages/expansions/fan_gp8403.yaml` |
| S360-PWM | `packages/expansions/fan_pwm.yaml` |

---

## Pre-Built Product Configurations

The `products/` directory contains ready-to-use configurations for common setups:

| Product File | Description | Hardware |
|--------------|-------------|----------|
| `sense360-mini-airiq.yaml` | Full air quality + presence detection | Sense360 Mini |
| `sense360-mini-airiq-basic.yaml` | Simplified air quality UI | Sense360 Mini |
| `sense360-mini-airiq-advanced.yaml` | Full technical controls | Sense360 Mini |
| `sense360-mini-airiq-ld2412.yaml` | Air quality with LD2412 radar | Sense360 Mini |
| `sense360-mini-presence.yaml` | Presence detection only | Sense360 Mini |
| `sense360-mini-presence-basic.yaml` | Simplified presence UI | Sense360 Mini |
| `sense360-mini-presence-advanced.yaml` | Full presence controls | Sense360 Mini |
| `sense360-mini-presence-ld2412.yaml` | Presence with LD2412 radar | Sense360 Mini |
| `sense360-mini-presence-advanced-ld2412.yaml` | Advanced presence + LD2412 | Sense360 Mini |
| `sense360-ceiling-presence.yaml` | Ceiling-mounted presence | Sense360 Ceiling |
| `sense360-ceiling-s3-full.yaml` | Full-featured ESP32-S3 ceiling board | Sense360 Ceiling S3 |
| `sense360-poe.yaml` | Power over Ethernet configuration | Sense360 PoE |
| `sense360-fan-pwm.yaml` | 4-channel PWM fan controller | Sense360 Fan PWM |

---

## Need Help?

- [Installation Guide](installation.md)
- [Configuration Reference](configuration.md)
- [GitHub Issues](https://github.com/sense360store/esphome-public/issues)
- **Support**: support@mysense360.com

# Sense360 Modular Board Combinations Guide

This document provides a clear overview of all possible board combinations for the Sense360 modular sensor platform.

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SENSE360 MODULAR SYSTEM                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────┐   ┌─────────┐   ┌──────────┐   ┌──────────┐   ┌─────────┐   │
│   │  CORE   │ + │  POWER  │ + │ MOUNTING │ + │  MODULE  │ + │   LED   │   │
│   └─────────┘   └─────────┘   └──────────┘   └──────────┘   └─────────┘   │
│                                                                             │
│   Required      Required      Required       Optional       Required        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. CORE Boards

The brain of your Sense360 system. Choose based on voice assistant requirements.

| Core Type | SKU | Description | Key Features |
|-----------|-----|-------------|--------------|
| **Core** | `S360-CORE` | Standard core board | ESP32-S3, 10A relay, dual I2C, UART |
| **Core Voice** | `S360-CORE-V` | Voice-enabled core | All Core features + integrated microphone support |

### Core Specifications
- **MCU**: ESP32-S3-WROOM-1-N16R8 (16MB Flash, 8MB PSRAM)
- **Connectivity**: WiFi 2.4GHz + Bluetooth 5.0 LE
- **Built-in**: 10A relay for fan/light switching
- **Expansion**: 10-pin connector (I2C, UART, GPIO)

---

## 2. POWER Boards

Choose your power source based on installation requirements.

| Power Type | SKU | Input | Output | Best For |
|------------|-----|-------|--------|----------|
| **USB** | Built-in | 5V USB-C | 5V/2A | Development, portable setups |
| **PoE** | `S360-POE` | 36-57V PoE | 5V/2A | Professional installs, single-cable |
| **PWR240V** | `S360-PWR` | 100-240V AC | 5V/2A | Permanent installations |

---

## 3. MOUNTING Options

Determines form factor and enclosure type.

| Mounting | Form Factor | Description | Compatible Enclosures |
|----------|-------------|-------------|----------------------|
| **Ceiling** | `-C` | Ceiling-mount with halo LED | Round ceiling enclosure |
| **Wall** | `-W` | Wall or desk mount | Wall-mount enclosure, PCB-only |

---

## 4. MODULES (Expansions)

Add sensor capabilities to your core. Multiple modules can be combined (with some restrictions).

### Air Quality Modules

| Module | SKU | Sensors | Use Case |
|--------|-----|---------|----------|
| **AirIQ** | `S360-AIR` | SPS30 (PM), SGP41 (VOC/NOx), SCD41 (CO2), BMP390 (Pressure) | General air quality monitoring |
| **Bathroom AirIQ Base** | `S360-BATH-B` | SHT4x, BMP390, SGP41 | Shower detection, mold risk |
| **Bathroom AirIQ Pro** | `S360-BATH-P` | Base + MLX90614 (IR), SPS30 (PM) | Condensation risk, PM monitoring |

> **Note**: Bathroom modules are **ceiling-only** and **replace** AirIQ (cannot use both together).

### Environmental Modules

| Module | SKU | Sensors | Use Case |
|--------|-----|---------|----------|
| **Comfort** | `S360-CMFT` | SHT40 (Temp/Humidity), LTR-303 (Light) | Basic environmental monitoring |
| **Presence** | `S360-PRES` | HLK-LD2450 mmWave radar | Occupancy detection, multi-target tracking |

### Fan Control Modules

| Module | SKU | Interface | Resolution | Use Case |
|--------|-----|-----------|------------|----------|
| **Fan GP8403** | `S360-GP8403` | 0-10V DAC | 12-bit (0.01V steps) | Commercial HVAC, VFDs, EC motors |
| **Fan PWM** | `S360-PWM` | 25kHz PWM | 8-bit | Standard fans, 4-pin PC fans |
| **Fan Relay** | Built-in | On/Off relay | Binary | Simple fan switching |

---

## 5. LED Rings

Visual feedback system. Choose based on core type and mounting.

| LED Type | SKU | Features | Pairs With |
|----------|-----|----------|-----------|
| **LED Ceiling** | `S360-LED-C` | WS2812B halo ring | Core Ceiling |
| **LED Wall** | `S360-LED-W` | WS2812B standard ring | Core Wall |
| **LED Voice Ceiling** | `S360-LED-V-C` | LED + Microphone | Core Voice Ceiling |
| **LED Voice Wall** | `S360-LED-V-W` | LED + Microphone | Core Voice Wall |

---

## Combination Matrix

### Valid Core + Power + Mounting Combinations

```
                    ┌─────────────────────────────────────────────────┐
                    │              POWER OPTIONS                      │
                    ├─────────────┬─────────────┬─────────────────────┤
                    │    USB      │    PoE      │      PWR240V        │
┌───────────────────┼─────────────┼─────────────┼─────────────────────┤
│ CORE              │             │             │                     │
│   └─ Ceiling      │     ✓       │      ✓      │        ✓            │
│   └─ Wall         │     ✓       │      ✓      │        ✓            │
├───────────────────┼─────────────┼─────────────┼─────────────────────┤
│ CORE VOICE        │             │             │                     │
│   └─ Ceiling      │     ✓       │      ✓      │        ✓            │
│   └─ Wall         │     ✓       │      ✓      │        ✓            │
└───────────────────┴─────────────┴─────────────┴─────────────────────┘
```

**Total Base Combinations**: 12 (2 cores × 3 power × 2 mounting)

---

### Module Compatibility Matrix

```
                    ┌─────────────────────────────────────────────────────────────────┐
                    │                    MODULES                                      │
                    ├─────────┬───────────┬─────────┬──────────┬─────────┬───────────┤
                    │ AirIQ   │ Bathroom  │ Comfort │ Presence │   Fan   │    LED    │
                    │         │  AirIQ    │         │          │         │           │
┌───────────────────┼─────────┼───────────┼─────────┼──────────┼─────────┼───────────┤
│ Ceiling Mount     │    ✓    │     ✓     │    ✓    │    ✓     │    ✓    │     ✓     │
├───────────────────┼─────────┼───────────┼─────────┼──────────┼─────────┼───────────┤
│ Wall Mount        │    ✓    │     ✗     │    ✓    │    ✓     │    ✓    │     ✓     │
└───────────────────┴─────────┴───────────┴─────────┴──────────┴─────────┴───────────┘

Legend: ✓ = Compatible, ✗ = Not Available
```

---

### Module Stacking Rules

| Combination | Allowed? | Notes |
|-------------|----------|-------|
| AirIQ + Comfort | ✓ | Full environmental monitoring |
| AirIQ + Presence | ✓ | Air quality + occupancy |
| AirIQ + Fan | ✓ | Smart ventilation control |
| AirIQ + Bathroom | ✗ | **Mutually exclusive** - Bathroom replaces AirIQ |
| Bathroom + Comfort | ✓ | Enhanced bathroom monitoring |
| Bathroom + Presence | ✓ | Bathroom occupancy detection |
| Bathroom + Fan | ✓ | Smart bathroom ventilation |
| Comfort + Presence | ✓ | Climate + occupancy |
| Comfort + Fan | ✓ | Climate-controlled ventilation |
| Presence + Fan | ✓ | Occupancy-based ventilation |
| Any combination + LED | ✓ | LED always compatible |

---

## Fan Control Options Detail

### GP8403 (0-10V DAC)
```
┌─────────────────────────────────────────────┐
│  GP8403 DAC Module                          │
├─────────────────────────────────────────────┤
│  • Interface: I2C (0x58)                    │
│  • Output: 0-10V analog                     │
│  • Resolution: 12-bit (4096 steps)          │
│  • Precision: 0.01V per step                │
│  • Use Case: Commercial HVAC, EC motors     │
└─────────────────────────────────────────────┘
```

### PWM Control
```
┌─────────────────────────────────────────────┐
│  PWM Fan Control                            │
├─────────────────────────────────────────────┤
│  • Interface: GPIO PWM (25kHz)              │
│  • Resolution: 8-bit (256 steps)            │
│  • Use Case: PC fans, standard PWM fans     │
│  • Multi-fan: Via SX1509 GPIO expander      │
└─────────────────────────────────────────────┘
```

### Relay Control (Built-in)
```
┌─────────────────────────────────────────────┐
│  Relay Control (Built-in to Core)           │
├─────────────────────────────────────────────┤
│  • Type: 10A relay on core board            │
│  • Control: On/Off binary switching         │
│  • Use Case: Simple fan/light switching     │
│  • No additional module required            │
└─────────────────────────────────────────────┘
```

---

## Complete Configuration Examples

### Example 1: Basic Ceiling Sensor (USB)
```yaml
# Components:
# - Core Ceiling
# - USB Power (built-in)
# - Comfort Module
# - LED Ceiling

packages:
  core: !include packages/hardware/sense360_core_ceiling.yaml
  led: !include packages/hardware/led_ring_ceiling.yaml
  comfort: !include packages/expansions/comfort_ceiling.yaml
```

### Example 2: Professional Air Quality Monitor (PoE)
```yaml
# Components:
# - Core Ceiling
# - PoE Power
# - AirIQ Module
# - Presence Module
# - LED Ceiling

packages:
  core: !include packages/hardware/sense360_core_ceiling.yaml
  power: !include packages/hardware/power_poe.yaml
  led: !include packages/hardware/led_ring_ceiling.yaml
  airiq: !include packages/expansions/airiq_ceiling.yaml
  presence: !include packages/expansions/presence_ceiling.yaml
```

### Example 3: Smart Bathroom (240V)
```yaml
# Components:
# - Core Voice Ceiling
# - 240V Power
# - Bathroom AirIQ Pro Module
# - Presence Module
# - Fan GP8403
# - LED Voice Ceiling

packages:
  core: !include packages/hardware/sense360_core_voice_ceiling.yaml
  power: !include packages/hardware/power_240v.yaml
  led: !include packages/hardware/led_ring_mic_ceiling.yaml
  bathroom: !include packages/expansions/airiq_bathroom_pro.yaml
  presence: !include packages/expansions/presence_ceiling.yaml
  fan: !include packages/expansions/fan_gp8403.yaml
```

### Example 4: Wall-Mount Office Sensor (PoE)
```yaml
# Components:
# - Core Wall
# - PoE Power
# - AirIQ Module
# - Comfort Module
# - Presence Module
# - LED Wall

packages:
  core: !include packages/hardware/sense360_core_wall.yaml
  power: !include packages/hardware/power_poe.yaml
  led: !include packages/hardware/led_ring_wall.yaml
  airiq: !include packages/expansions/airiq_wall.yaml
  comfort: !include packages/expansions/comfort_wall.yaml
  presence: !include packages/expansions/presence_wall.yaml
```

---

## Quick Reference: SKU Naming Convention

```
S360-{CORE}-{MOUNT}-{POWER}

Where:
  CORE   = CORE | CORE-V (Voice)
  MOUNT  = C (Ceiling) | W (Wall)
  POWER  = USB | POE | PWR

Examples:
  S360-CORE-C-USB    = Core + Ceiling + USB
  S360-CORE-V-W-POE  = Core Voice + Wall + PoE
  S360-CORE-C-PWR    = Core + Ceiling + 240V
```

---

## Visual Decision Tree

```
                              START
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Need Voice Support?  │
                    └───────────────────────┘
                         │           │
                        YES          NO
                         │           │
                         ▼           ▼
                    ┌─────────┐ ┌─────────┐
                    │ CORE-V  │ │  CORE   │
                    └─────────┘ └─────────┘
                         │           │
                         └─────┬─────┘
                               ▼
                    ┌───────────────────────┐
                    │   Mounting Location?  │
                    └───────────────────────┘
                         │           │
                      CEILING      WALL
                         │           │
                         ▼           ▼
                    ┌─────────┐ ┌─────────┐
                    │  -C     │ │   -W    │
                    └─────────┘ └─────────┘
                         │           │
                         └─────┬─────┘
                               ▼
                    ┌───────────────────────┐
                    │    Power Source?      │
                    └───────────────────────┘
                      │      │       │
                     USB    PoE    240V
                      │      │       │
                      ▼      ▼       ▼
                   ┌─────┐┌─────┐┌─────┐
                   │ USB ││ POE ││ PWR │
                   └─────┘└─────┘└─────┘
                      │      │       │
                      └──────┴───────┘
                               │
                               ▼
                    ┌───────────────────────┐
                    │   Add Modules...      │
                    │                       │
                    │  □ AirIQ              │
                    │  □ Bathroom AirIQ*    │
                    │  □ Comfort            │
                    │  □ Presence           │
                    │  □ Fan Control        │
                    │  □ LED Ring           │
                    └───────────────────────┘

                    * Ceiling only, replaces AirIQ
```

---

## Power Budget Reference

| Component | 3.3V Draw | 5V Draw | 12V Draw |
|-----------|-----------|---------|----------|
| Core Board | 200mA | 500mA | - |
| AirIQ Module | 500mA | - | - |
| Bathroom Module | 500mA | - | - |
| Comfort Module | 200mA | - | - |
| Presence Module | - | 150mA | - |
| Fan GP8403 | 50mA | - | - |
| Fan PWM | 50mA | - | - |
| LED Ring | - | 500mA | - |
| **Budget Limits** | **500mA** | **2000mA** | **4000mA** |

---

## File Reference

| Category | Directory | Example Files |
|----------|-----------|---------------|
| Core Boards | `packages/hardware/` | `sense360_core_ceiling.yaml`, `sense360_core_voice_wall.yaml` |
| Power | `packages/hardware/` | `power_poe.yaml`, `power_240v.yaml` |
| LED Rings | `packages/hardware/` | `led_ring_ceiling.yaml`, `led_ring_mic_wall.yaml` |
| Modules | `packages/expansions/` | `airiq_ceiling.yaml`, `presence_wall.yaml`, `fan_gp8403.yaml` |
| Complete Products | `products/` | `sense360-core-c-poe.yaml`, `sense360-core-v-w-usb.yaml` |

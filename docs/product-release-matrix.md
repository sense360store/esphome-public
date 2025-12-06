# Sense360 Product Release Matrix

This document defines the complete product SKU matrix for Sense360 devices, including all valid hardware combinations, firmware configurations, and release packages.

## Version Information

- **Release Version**: 3.0.0
- **Release Date**: 2025-12-05
- **ESPHome Minimum Version**: 2025.10.0

---

## 1. Core Boards

| SKU | Name | Description | Voice | Form Factor |
|-----|------|-------------|-------|-------------|
| **S360-CORE-C** | Sense360 Core Ceiling | Standard ceiling-mount core | No | Ceiling |
| **S360-CORE-V-C** | Sense360 Core Voice Ceiling | Voice-enabled ceiling core | Yes | Ceiling |
| **S360-CORE-W** | Sense360 Core Wall | Standard wall/desk core | No | Wall/Desk |
| **S360-CORE-V-W** | Sense360 Core Voice Wall | Voice-enabled wall/desk core | Yes | Wall/Desk |

### Core Hardware Specifications

| Feature | All Cores |
|---------|-----------|
| MCU | ESP32-S3-WROOM-1-N16R8 |
| Flash | 16MB |
| PSRAM | 8MB (Octal) |
| WiFi | 2.4GHz 802.11 b/g/n |
| Bluetooth | 5.0 LE |
| Relay | 10A AC/DC |
| I2C Buses | 2 (Primary + Expansion) |
| UART | Up to 2 buses |

---

## 2. Power Options

| SKU | Name | Input | Output | Use Case |
|-----|------|-------|--------|----------|
| **(USB)** | USB Power | 5V USB-C | 5V/2A | Development, portable |
| **S360-POE** | PoE Power | 36-57V IEEE 802.3af | 5V/2A | Professional installations |
| **S360-PWR** | AC Power | 100-240V AC | 5V/2A | Permanent installations |

---

## 3. LED Attachments

| SKU | Name | LEDs | Microphone | Use With |
|-----|------|------|------------|----------|
| **S360-LED-C** | LED Ring Ceiling | 12x WS2812B | No | CORE-C |
| **S360-LED-V-C** | LED+MIC Ring Ceiling | 12x WS2812B | I2S Array | CORE-V-C (Required) |
| **S360-LED-W** | LED Ring Wall | 12x WS2812B | No | CORE-W |
| **S360-LED-V-W** | LED+MIC Ring Wall | 12x WS2812B | I2S Array | CORE-V-W (Required) |

### LED Attachment Rules

| Core Type | LED Requirement |
|-----------|-----------------|
| CORE-V-C (Voice Ceiling) | **LED+MIC Ring Required** (S360-LED-V-C) |
| CORE-V-W (Voice Wall) | **LED+MIC Ring Required** (S360-LED-V-W) |
| CORE-C (Ceiling) | LED Ring Optional (S360-LED-C) |
| CORE-W (Wall) | LED Ring Optional (S360-LED-W) |

---

## 4. Expansion Modules

### Ceiling Modules (-C suffix)

| SKU | Name | Sensors | Function |
|-----|------|---------|----------|
| **S360-AIR-C** | AirIQ Ceiling | SEN55, SCD41, BMP390 | Air quality monitoring |
| **S360-BATH-C** | Bathroom Ceiling | SHT40, SCD41, SGP40, BH1750 | Bathroom-specific monitoring |
| **S360-CMFT-C** | Comfort Ceiling | SHT4x, VEML7700 | Temperature, humidity, light |
| **S360-PRES-C** | Presence Ceiling | LD2450 mmWave | Multi-target presence detection |
| **S360-FAN-GP** | Fan Control GP8403 | GP8403 DAC | 0-10V analog fan control |
| **S360-FAN-PWM** | Fan Control PWM | PWM + Tachometer | PWM fan control with feedback |

### Wall Modules (-W suffix)

| SKU | Name | Sensors | Function |
|-----|------|---------|----------|
| **S360-AIR-W** | AirIQ Wall | SEN55, SCD41 | Air quality monitoring |
| **S360-CMFT-W** | Comfort Wall | SHT4x, BH1750 | Temperature, humidity, light |
| **S360-PRES-W** | Presence Wall | LD2450 mmWave | Multi-target presence detection |
| **S360-FAN-GP** | Fan Control GP8403 | GP8403 DAC | 0-10V analog fan control |
| **S360-FAN-PWM** | Fan Control PWM | PWM + Tachometer | PWM fan control with feedback |

---

## 5. Module Combination Rules

### Ceiling Module Constraints

1. **AirIQ-C and Bathroom-C are mutually exclusive** (cannot be used together)
2. All other ceiling modules can be freely combined
3. Fan module is optional with any configuration

### Wall Module Constraints

1. **No Bathroom module** (Bathroom-C is ceiling-only)
2. All wall modules can be freely combined
3. Fan module is optional with any configuration

---

## 6. Valid Module Configurations

### Ceiling Configurations (24 Total)

#### Single Module Builds (5)
| Config ID | Modules | SKUs |
|-----------|---------|------|
| C-CMF | Comfort only | S360-CMFT-C |
| C-PRS | Presence only | S360-PRES-C |
| C-FAN | Fan only | S360-FAN-GP or S360-FAN-PWM |
| C-AIR | AirIQ only | S360-AIR-C |
| C-BTH | Bathroom only | S360-BATH-C |

#### Two Module Builds (10)
| Config ID | Modules | SKUs |
|-----------|---------|------|
| C-CMF-PRS | Comfort + Presence | S360-CMFT-C, S360-PRES-C |
| C-CMF-FAN | Comfort + Fan | S360-CMFT-C, S360-FAN-* |
| C-PRS-FAN | Presence + Fan | S360-PRES-C, S360-FAN-* |
| C-AIR-CMF | AirIQ + Comfort | S360-AIR-C, S360-CMFT-C |
| C-AIR-PRS | AirIQ + Presence | S360-AIR-C, S360-PRES-C |
| C-AIR-FAN | AirIQ + Fan | S360-AIR-C, S360-FAN-* |
| C-BTH-CMF | Bathroom + Comfort | S360-BATH-C, S360-CMFT-C |
| C-BTH-PRS | Bathroom + Presence | S360-BATH-C, S360-PRES-C |
| C-BTH-FAN | Bathroom + Fan | S360-BATH-C, S360-FAN-* |
| C-CMF-PRS | Comfort + Presence | S360-CMFT-C, S360-PRES-C |

#### Three Module Builds (7)
| Config ID | Modules | SKUs |
|-----------|---------|------|
| C-CMF-PRS-FAN | Comfort + Presence + Fan | S360-CMFT-C, S360-PRES-C, S360-FAN-* |
| C-AIR-CMF-PRS | AirIQ + Comfort + Presence | S360-AIR-C, S360-CMFT-C, S360-PRES-C |
| C-AIR-CMF-FAN | AirIQ + Comfort + Fan | S360-AIR-C, S360-CMFT-C, S360-FAN-* |
| C-AIR-PRS-FAN | AirIQ + Presence + Fan | S360-AIR-C, S360-PRES-C, S360-FAN-* |
| C-BTH-CMF-PRS | Bathroom + Comfort + Presence | S360-BATH-C, S360-CMFT-C, S360-PRES-C |
| C-BTH-CMF-FAN | Bathroom + Comfort + Fan | S360-BATH-C, S360-CMFT-C, S360-FAN-* |
| C-BTH-PRS-FAN | Bathroom + Presence + Fan | S360-BATH-C, S360-PRES-C, S360-FAN-* |

#### Four Module Builds (2)
| Config ID | Modules | SKUs |
|-----------|---------|------|
| C-AIR-CMF-PRS-FAN | AirIQ + Comfort + Presence + Fan | S360-AIR-C, S360-CMFT-C, S360-PRES-C, S360-FAN-* |
| C-BTH-CMF-PRS-FAN | Bathroom + Comfort + Presence + Fan | S360-BATH-C, S360-CMFT-C, S360-PRES-C, S360-FAN-* |

### Wall Configurations (15 Total)

#### Single Module Builds (4)
| Config ID | Modules | SKUs |
|-----------|---------|------|
| W-CMF | Comfort only | S360-CMFT-W |
| W-PRS | Presence only | S360-PRES-W |
| W-FAN | Fan only | S360-FAN-GP or S360-FAN-PWM |
| W-AIR | AirIQ only | S360-AIR-W |

#### Two Module Builds (6)
| Config ID | Modules | SKUs |
|-----------|---------|------|
| W-CMF-PRS | Comfort + Presence | S360-CMFT-W, S360-PRES-W |
| W-CMF-FAN | Comfort + Fan | S360-CMFT-W, S360-FAN-* |
| W-PRS-FAN | Presence + Fan | S360-PRES-W, S360-FAN-* |
| W-AIR-CMF | AirIQ + Comfort | S360-AIR-W, S360-CMFT-W |
| W-AIR-PRS | AirIQ + Presence | S360-AIR-W, S360-PRES-W |
| W-AIR-FAN | AirIQ + Fan | S360-AIR-W, S360-FAN-* |

#### Three Module Builds (4)
| Config ID | Modules | SKUs |
|-----------|---------|------|
| W-CMF-PRS-FAN | Comfort + Presence + Fan | S360-CMFT-W, S360-PRES-W, S360-FAN-* |
| W-AIR-CMF-PRS | AirIQ + Comfort + Presence | S360-AIR-W, S360-CMFT-W, S360-PRES-W |
| W-AIR-CMF-FAN | AirIQ + Comfort + Fan | S360-AIR-W, S360-CMFT-W, S360-FAN-* |
| W-AIR-PRS-FAN | AirIQ + Presence + Fan | S360-AIR-W, S360-PRES-W, S360-FAN-* |

#### Four Module Build (1)
| Config ID | Modules | SKUs |
|-----------|---------|------|
| W-AIR-CMF-PRS-FAN | AirIQ + Comfort + Presence + Fan | S360-AIR-W, S360-CMFT-W, S360-PRES-W, S360-FAN-* |

---

## 7. Complete Product Matrix

### Product Naming Convention

```
sense360-{core}-{power}-{led}-{modules}.yaml

Examples:
- sense360-core-c-usb-led.yaml           (Ceiling, USB, with LED, no modules)
- sense360-core-v-c-poe-airiq.yaml       (Voice Ceiling, PoE, AirIQ)
- sense360-core-w-pwr-led-comfort-presence.yaml  (Wall, AC Power, LED, Comfort+Presence)
```

### Full SKU Format

```
S360-{CORE}-{POWER}[-{LED}][-{MODULES}]

Examples:
- S360-CORE-C-USB                       (Ceiling Core, USB power)
- S360-CORE-V-C-POE-LED-AIR             (Voice Ceiling, PoE, LED+MIC, AirIQ)
- S360-CORE-W-PWR-LED-CMF-PRS           (Wall, AC Power, LED, Comfort+Presence)
```

---

## 8. Firmware Configuration Files

### Base Configurations (by Core + Power)

| File | Core | Power | Voice | LED |
|------|------|-------|-------|-----|
| `sense360-core-c-usb.yaml` | Ceiling | USB | No | Optional |
| `sense360-core-c-poe.yaml` | Ceiling | PoE | No | Optional |
| `sense360-core-c-pwr.yaml` | Ceiling | AC | No | Optional |
| `sense360-core-v-c-usb.yaml` | Voice Ceiling | USB | Yes | Required |
| `sense360-core-v-c-poe.yaml` | Voice Ceiling | PoE | Yes | Required |
| `sense360-core-v-c-pwr.yaml` | Voice Ceiling | AC | Yes | Required |
| `sense360-core-w-usb.yaml` | Wall | USB | No | Optional |
| `sense360-core-w-poe.yaml` | Wall | PoE | No | Optional |
| `sense360-core-w-pwr.yaml` | Wall | AC | No | Optional |
| `sense360-core-v-w-usb.yaml` | Voice Wall | USB | Yes | Required |
| `sense360-core-v-w-poe.yaml` | Voice Wall | PoE | Yes | Required |
| `sense360-core-v-w-pwr.yaml` | Voice Wall | AC | Yes | Required |

### Module Add-on Configurations

Users can combine base configurations with module packages:

```yaml
# Example: Voice Ceiling with PoE and AirIQ + Presence
packages:
  sense360:
    url: https://github.com/sense360store/esphome-public
    ref: v3.0.0
    files:
      - products/sense360-core-v-c-poe.yaml
      - packages/expansions/airiq_ceiling.yaml
      - packages/expansions/presence_ceiling.yaml
      - packages/features/airiq_advanced_profile.yaml
      - packages/features/presence_advanced.yaml
```

---

## 9. Pre-Built Product Configurations

### Ceiling Products

| File | Description | Modules |
|------|-------------|---------|
| `sense360-ceiling-full.yaml` | Full ceiling system | AirIQ + Comfort + Presence + Fan |
| `sense360-ceiling-airiq.yaml` | Air quality focused | AirIQ + Comfort |
| `sense360-ceiling-presence.yaml` | Presence focused | Presence + Comfort |
| `sense360-ceiling-bathroom.yaml` | Bathroom installation | Bathroom + Presence + Fan |
| `sense360-ceiling-voice-full.yaml` | Voice + Full sensors | Voice + AirIQ + Comfort + Presence |

### Wall Products

| File | Description | Modules |
|------|-------------|---------|
| `sense360-wall-full.yaml` | Full wall system | AirIQ + Comfort + Presence + Fan |
| `sense360-wall-airiq.yaml` | Air quality focused | AirIQ + Comfort |
| `sense360-wall-presence.yaml` | Presence focused | Presence + Comfort |
| `sense360-wall-voice-full.yaml` | Voice + Full sensors | Voice + AirIQ + Comfort + Presence |

---

## 10. Release Packages

### GitHub Release Tags

- `v3.0.0` - Current stable release
- `main` - Development branch (not recommended for production)

### Installation

```yaml
# Recommended: Use specific version tag
packages:
  sense360:
    url: https://github.com/sense360store/esphome-public
    ref: v3.0.0
    files:
      - products/sense360-ceiling-full.yaml

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

## 11. Quick Reference Summary

### Rules at a Glance

1. **Voice cores require LED+MIC ring** - No exceptions
2. **Non-voice cores have optional LED** - Can work without LED ring
3. **AirIQ and Bathroom are mutually exclusive** - Choose one or the other
4. **Bathroom is ceiling-only** - Wall configs don't have Bathroom option
5. **All other modules combine freely** - Any combination is valid
6. **Fan can be GP8403 or PWM** - Choose based on your fan hardware

### Minimum Viable Configurations

| Use Case | Minimum Config |
|----------|----------------|
| Basic presence detection | Core + Presence |
| Air quality monitoring | Core + AirIQ |
| Smart thermostat | Core + Comfort |
| Voice assistant | Voice Core + LED+MIC |
| Bathroom automation | Core + Bathroom + Fan |
| Full smart room | Core + AirIQ + Comfort + Presence + Fan |

---

## Support

- **Documentation**: https://github.com/sense360store/esphome-public/tree/main/docs
- **Issues**: https://github.com/sense360store/esphome-public/issues
- **Email**: support@mysense360.com

# Sense360 Ceiling S3 Board Configuration

## Overview

This document describes the configuration for the **Sense360 Ceiling S3** board based on the schematic `Modular_ESP32-S3_Sensor_Platform.kicad_sch`.

**Hardware:**
- **MCU:** ESP32-S3-WROOM-1-N16R8 (16MB Flash, 8MB PSRAM)
- **Power:** USB-C + Optional PoE with RT6050GJ5 buck converter (5V → 3.3V)
- **Form Factor:** Ceiling recessed mount with expansion module connectors

## Board Features

### Power System
- **USB-C receptacle** (VBUS power input)
- **PoE option** via SQ2310CEDD MOSFET
- **RT6050GJ5 buck converter** (5V to 3.3V @ 3A for MCU)
- Separate 5V rail for sensor modules

### Expansion Modules Supported
1. **Presence Module** (Hi-Link LD2450 or DFRobot SEN0609/C4001)
2. **AirIQ Module** (SEN55, SCD41 air quality sensors)
3. **Comfort Module** (VEML7700, SHT4x climate sensors)
4. **WS2812B LED Ring** (12 LEDs for visual feedback)
5. **Fan Control** (SI2302 MOSFET for fan switching)

## GPIO Pin Mapping

### I2C Buses

| Bus | SDA | SCL | Frequency | Usage |
|-----|-----|-----|-----------|-------|
| Primary | GPIO26 | GPIO8 | 100 kHz | AirIQ + Comfort modules (shared bus) |

**Note:** 100 kHz frequency is required for SEN55 compatibility.

### UART Ports

| Sensor | TX (ESP→Sensor) | RX (ESP←Sensor) | Baud Rate | Usage |
|--------|-----------------|-----------------|-----------|-------|
| Hi-Link LD2450 | GPIO38 | GPIO39 | 256000 | Primary presence option |
| SEN0609/C4001 | GPIO4 | GPIO5 | 115200 | Alternative presence option |

**Important:** Only ONE presence sensor should be installed at a time.

### Module GPIO Assignments

#### Presence Module
- **GPIO5:** `out1@ms11` - Digital presence output
- **GPIO6:** `notEgpio0` - SEN0609 auxiliary signal

#### AirIQ Module
- **GPIO7:** `AirQ_Status_Led` - Status indicator (functional)
- **GPIO8:** `AirQ_Led` - ⚠️ **CONFLICTS WITH I2C_SCL** (cannot be used)

#### Comfort Module
- **GPIO3:** `ALS_INT` - VEML7700 ambient light sensor interrupt (active low)

### LED and Fan Control
- **GPIO14:** `LED_DATA` - WS2812B LED ring (12 LEDs) via 3.3V→5V level shifter
- **GPIO23:** `FAN` - SI2302 MOSFET gate for fan control

### System
- **GPIO0:** Boot button (strapping pin)

## I2C Device Address Map

| Address | Device | Module | Function |
|---------|--------|--------|----------|
| 0x10 | VEML7700 | Comfort | Ambient light sensor (lux) |
| 0x44 | SHT4x | Comfort | Temperature & humidity |
| 0x62 | SCD41 | AirIQ | CO2 sensor |
| 0x69 | SEN55 | AirIQ | PM/VOC/NOx sensor |

## Configuration Files

### Core Hardware
- **`packages/hardware/sense360_core_ceiling_s3.yaml`** - Main board configuration

### Expansion Modules
- **`packages/expansions/presence_ceiling_s3.yaml`** - Presence module base
- **`packages/expansions/airiq_ceiling_s3.yaml`** - AirIQ module (air quality)
- **`packages/expansions/comfort_ceiling_s3.yaml`** - Comfort module (climate)

### Complete Product
- **`products/sense360-ceiling-s3-full.yaml`** - Full configuration with all modules

## Usage Example

```yaml
packages:
  sense360_firmware:
    url: https://github.com/sense360store/esphome-public
    ref: main
    files:
      - products/sense360-ceiling-s3-full.yaml

substitutions:
  device_name: my-ceiling-sensor
  friendly_name: "Living Room Ceiling"
  presence_sensor_type: "hilink"  # or "sen0609"

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

## Known Issues & Warnings

### ⚠️ Critical: GPIO8 Conflict

**Problem:** GPIO8 is used for BOTH:
1. I2C_SCL (primary I2C bus for sensors)
2. AirQ_Led indicator (shown in schematic)

**Impact:** The AirQ_Led cannot be used when I2C is active (which is always, if AirIQ or Comfort modules are installed).

**Solution:**
- Current config: AirQ_Led is **disabled** in software
- Hardware fix: Next PCB revision should move AirQ_Led to an unused GPIO (e.g., GPIO9, GPIO10, GPIO11)

**Workaround:** Use GPIO7 (AirQ_Status_Led) for status indication, or control the LED ring (GPIO14) for visual feedback.

### ⚠️ Presence Sensor Selection

**Problem:** Schematic shows connections for BOTH Hi-Link LD2450 and SEN0609/C4001 sensors.

**Solution:**
- Set `presence_sensor_type` substitution to either `"hilink"` or `"sen0609"`
- Only populate ONE sensor on the physical board
- UART pins are different for each sensor type

### ℹ️ I2C Frequency Limitation

**Requirement:** I2C bus must run at **100 kHz** (not 400 kHz) for SEN55 compatibility.

**Impact:** Slightly slower I2C communication, but required for reliable SEN55 operation.

### ℹ️ Level Shifter for LEDs

**Note:** WS2812B LEDs require 5V logic, but ESP32-S3 outputs 3.3V.

**Solution:** Schematic includes level shifter (labeled U2) for LED_DATA signal. Ensure this is populated on the PCB.

## Power Consumption Estimates

| Component | Power Draw |
|-----------|------------|
| ESP32-S3 base | ~0.5W |
| Presence sensor (LD2450/C4001) | ~0.15W |
| AirIQ module (SEN55 + SCD41) | ~1.2W |
| Comfort module (VEML7700 + SHT4x) | ~0.05W |
| LED ring (12 LEDs @ 50% brightness) | ~0.3-0.6W |
| Fan (when active) | ~2.0W |
| **Total (all modules, no fan)** | **~1.9W** |
| **Total (all modules + fan)** | **~3.9W** |

## Sensor Specifications

### Presence Module

#### Hi-Link LD2450
- Detection range: 0.2m - 6m (configurable)
- Multi-target tracking: up to 3 simultaneous targets
- Zone configuration support
- UART: 256000 baud

#### DFRobot SEN0609/C4001
- Motion detection: up to 25m
- Presence detection: up to 16m
- Distance measurement: 1.2m - 25m
- Speed measurement: 0.1 - 10 m/s
- Detection angle: 100° horizontal
- UART: 115200 baud (also supports I2C)

### AirIQ Module

#### SEN55 (Sensirion)
- PM1.0, PM2.5, PM4.0, PM10 particulate matter
- VOC index (0-500)
- NOx index (0-500)
- Temperature & humidity
- Auto-cleaning fan (configurable interval)

#### SCD41 (Sensirion)
- CO2: 400-5000 ppm
- Accuracy: ±(40 ppm + 5%)
- Temperature & humidity (secondary)
- Automatic self-calibration

### Comfort Module

#### VEML7700 (Vishay)
- Range: 0.0036 to 220,000+ lux
- 16-bit resolution
- Interrupt support (threshold-based)
- Auto-gain adjustment

#### SHT4x (Sensirion)
- Temperature: ±0.2°C accuracy
- Humidity: ±1.8% RH accuracy
- Response time: 5.8s (63% step)

## Troubleshooting

### I2C Devices Not Detected

1. **Check I2C frequency:** Must be 100 kHz for SEN55
2. **Verify pullup resistors:** 4.7kΩ on SDA/SCL lines
3. **Check module connection:** Ensure modules are properly seated
4. **Review logs:** Enable `i2c: DEBUG` in logger config

### Presence Sensor Not Working

1. **Verify sensor type:** Check `presence_sensor_type` matches installed sensor
2. **Check UART pins:** Different for Hi-Link vs SEN0609
3. **Verify baud rate:** 256000 for LD2450, 115200 for C4001
4. **Power supply:** Ensure 5V rail is providing adequate current

### LED Ring Not Working

1. **Check level shifter:** Verify U2 is populated on PCB
2. **Verify GPIO14:** Ensure pin is not configured elsewhere
3. **Test with simple effect:** Use `led_ring.turn_on` with solid color
4. **Check power:** 12 LEDs at full brightness can draw significant current

### Fan Not Responding

1. **Verify GPIO23:** Check pin assignment
2. **Test MOSFET:** SI2302 gate should switch at 3.3V
3. **Check fan power:** Ensure fan has appropriate power supply
4. **Safety:** Verify flyback diode is present for inductive load

## Comparison with Other Sense360 Boards

| Feature | Ceiling S3 (This Board) | Core Ceiling (Old) | Core Mapping |
|---------|-------------------------|---------------------|--------------|
| MCU | ESP32-S3 N16R8 | ESP32-S3 | ESP32-S3 N16R8 |
| Flash / PSRAM | 16MB / 8MB | 8MB / 2MB | 16MB / 8MB |
| I2C Primary | GPIO26/8 | GPIO39/40 | GPIO39/40 |
| UART Presence | GPIO38/39 or 4/5 | GPIO1/2 | GPIO1/2 |
| LED Ring | GPIO14 | GPIO48 | GPIO48 |
| Fan Control | GPIO23 | GPIO4 (relay) | GPIO4 |
| Relay | - | GPIO4 | GPIO10 |

**Note:** This Ceiling S3 board uses a different pinout than previous boards. Configurations are NOT interchangeable.

## Hardware Revision Recommendations

For the next PCB revision, consider these improvements:

1. **Fix GPIO8 conflict:** Move AirQ_Led to unused GPIO (GPIO9, 10, or 11)
2. **Add relay output:** Include relay like other core boards (optional)
3. **Consolidate UART pins:** Consider using same UART pins for all presence sensors via solder jumper
4. **Label test points:** Add TP for key signals (I2C, UART, power rails)
5. **Pull-up/down clarification:** Document all strapping pin states in schematic
6. **Add fan tachometer input:** For RPM sensing (optional GPIO)

## Support

For issues or questions:
- GitHub: https://github.com/sense360store/esphome-public/issues
- Documentation: https://sense360.io/docs

---

**Document Version:** 1.0
**Date:** 2025-12-05
**Board:** Sense360 Ceiling S3 (ESP32-S3-WROOM-1-N16R8)
**Schematic:** Modular_ESP32-S3_Sensor_Platform.kicad_sch

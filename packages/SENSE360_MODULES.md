# Sense360 Module Documentation

## Overview

The Sense360 platform is built on ESP32-S3-WROOM-1-N16R8 and supports modular expansion through I2C, UART, and GPIO interfaces.

## Pin Reference

| Function | GPIO | Notes |
|----------|------|-------|
| I2C Primary SDA | 39 | Sensors |
| I2C Primary SCL | 40 | 100kHz |
| I2C Secondary SDA | 21 | Expander |
| I2C Secondary SCL | 18 | 400kHz |
| UART TX | 1 | Presence |
| UART RX | 2 | Presence |
| Fan PWM | 4 | 25kHz |
| Fan Tach | 5 | RPM input |
| Relay | 10 | 10A |
| Status LED | 48 | RGB |
| User Button | 9 | Input |

## Modules

### Core (sense360_core_mapping.yaml)

Base hardware configuration. Include this first.

```yaml
packages:
  core: !include packages/hardware/sense360_core_mapping.yaml
```

### Power Management (power_management.yaml)

Tracks power consumption per rail. Optional but recommended.

```yaml
packages:
  power: !include packages/hardware/power_management.yaml
```

Power budgets:
- 3.3V: 500mA (MCU, sensors)
- 5V: 2000mA (radar, USB)
- 12V: 4000mA (fans)

### Presence Detection

**For Sense360 Core and Presence Modules:**

**HLK-LD2450** (presence_ld2450.yaml) - Multi-target radar
- UART: 256000 baud
- Power: 5V/150mA
- Tracks up to 3 targets with distance/angle

**DFRobot C4001** (presence_dfrobot_c4001.yaml) - Long-range FMCW radar
- UART: 115200 baud (or I2C at 0x32)
- Power: 5V/180-250mA
- Presence range: 16m, Motion range: 25m
- Speed measurement: 0.1-10 m/s
- Detection angle: 100 degrees horizontal

**For Presence Mini only:**

**HLK-LD2450** (presence_ld2450.yaml) - Multi-target radar (see above)

**HLK-LD2412** (presence_ld2412.yaml) - Single-zone radar
- UART: 115200 baud
- Power: 5V/100mA
- Better still detection, up to 9m

```yaml
# For Sense360 Core/Presence (LD2450 default)
packages:
  presence: !include packages/expansions/presence_ld2450.yaml

# For Sense360 Core/Presence (C4001 alternative)
packages:
  presence: !include packages/hardware/presence_dfrobot_c4001.yaml

# For Presence Mini (LD2412 alternative)
packages:
  presence: !include packages/expansions/presence_ld2412.yaml
```

### Air Quality (airiq.yaml)

SEN55 + SCD41 sensors on I2C.

- PM1.0, PM2.5, PM4.0, PM10
- VOC Index, NOx Index
- CO2 (ppm)
- Temperature, Humidity
- Power: 3.3V/500mA

```yaml
packages:
  airiq: !include packages/expansions/airiq.yaml
```

I2C Addresses: SEN55=0x69, SCD41=0x62

### Comfort (comfort.yaml)

SHT40 + BH1750 on I2C.

- Temperature (high precision)
- Humidity
- Light (lux)
- Power: 3.3V/200mA

```yaml
packages:
  comfort: !include packages/expansions/comfort.yaml
```

I2C Addresses: SHT40=0x44, BH1750=0x23

### Fan Control - GP8403 DAC (fan_gp8403.yaml)

0-10V analog output for HVAC fans.

- 2 channels, 12-bit resolution
- Voltage: 0-10V or 0-5V (jumper)
- Power: 3.3V/50mA

```yaml
packages:
  fan_dac: !include packages/expansions/fan_gp8403.yaml
```

I2C Address: 0x58 (or 0x59)

### GPIO Expander - SX1509 (gpio_expander_sx1509.yaml)

16-channel GPIO/PWM expander on secondary I2C bus.

- IO0-3: Fan PWM outputs
- IO4-7: Tachometer inputs
- IO8-11: Auxiliary PWM
- IO12-15: Digital inputs
- Power: 3.3V/50mA

```yaml
packages:
  expander: !include packages/expansions/gpio_expander_sx1509.yaml
```

I2C Address: 0x3E

### 12V PWM Fans (fan_12v_pwm.yaml)

Multi-channel 12V fan control via SX1509.

Requires gpio_expander_sx1509.yaml.

Features:
- 4 independent fan channels
- Temperature-based auto mode
- Quiet/boost modes
- Per-zone enable

```yaml
packages:
  expander: !include packages/expansions/gpio_expander_sx1509.yaml
  fan_12v: !include packages/expansions/fan_12v_pwm.yaml
```

## Basic Configuration Example

Minimal setup with presence detection:

```yaml
substitutions:
  device_name: my-sense360
  friendly_name: My Sense360

packages:
  core: !include packages/hardware/sense360_core_mapping.yaml
  presence: !include packages/expansions/presence_ld2450.yaml

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_key

logger:
```

## Advanced Configuration Example

Full setup with air quality and fan control:

```yaml
substitutions:
  device_name: sense360-hvac
  friendly_name: HVAC Controller

packages:
  core: !include packages/hardware/sense360_core_mapping.yaml
  power: !include packages/hardware/power_management.yaml
  presence: !include packages/expansions/presence_ld2450.yaml
  airiq: !include packages/expansions/airiq.yaml
  comfort: !include packages/expansions/comfort.yaml
  fan_dac: !include packages/expansions/fan_gp8403.yaml
  expander: !include packages/expansions/gpio_expander_sx1509.yaml
  fan_12v: !include packages/expansions/fan_12v_pwm.yaml

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_key

logger:
```

## I2C Address Conflicts

Be aware of potential conflicts:

| Address | Devices |
|---------|---------|
| 0x44 | SHT40 (Comfort), SHT30 (AirIQ) |
| 0x59 | GP8403 alt, SGP40 (Bathroom) |

Do not use conflicting modules together on the same I2C bus.

## Customization

Override substitutions in your config:

```yaml
substitutions:
  # Change presence sensor baud rate for LD2412
  uart_presence_baud: "115200"

  # Adjust fan temperature thresholds
  fan_temp_low: "22"
  fan_temp_high: "28"
```

## Scripts Reference

### Power Management
- `power_register_module`: Register module power draw
- `power_unregister_module`: Remove module from tracking

### GPIO Expander
- `sx1509_set_fan_speed(fan_num, speed)`: Set single fan
- `sx1509_set_all_fans(speed)`: Set all fans
- `sx1509_emergency_stop`: Stop all fans

### 12V Fans
- `fan_12v_calculate_auto_speed`: Update auto mode
- `fan_12v_set_temperature(temp)`: Set temperature input
- `fan_12v_emergency_stop`: Stop all 12V fans

## Globals Reference

Key globals available for automation:

```
presence_people_count    - Number of detected people
presence_closest_distance - Distance to nearest person (m)
airiq_aqi_value         - Air quality index (0-500)
airiq_co2               - CO2 level (ppm)
comfort_temperature     - Temperature (C)
comfort_humidity        - Humidity (%)
comfort_index_value     - Comfort score (0-100)
fan_12v_auto_enabled    - Auto fan mode active
```

# ESPHome Packages Structure

This directory contains modular ESPHome configuration packages organized by category.

## Directory Structure

```
packages/
├── base/              # Core system components
├── features/          # Feature profiles (basic & advanced)
├── hardware/          # Hardware drivers
└── expansions/        # Sensor module drivers
```

## Feature Profiles - Basic vs Advanced

All features are available in two versions:

### Basic Profiles (Recommended for Most Users)
- **Simple, user-friendly interface**
- **No technical jargon** - uses terms everyone understands
- **Easy-to-read measurements**
- Perfect for home users who want simple, clear information

#### Presence Detection - Basic (`features/presence_basic_profile.yaml`)
- Shows: "Room Occupied" (Yes/No)
- Shows: "Activity Level" (Still/Moving)
- No complex zones or technical data

#### Air Quality - Basic (`features/airiq_basic_profile.yaml`)
- Shows: Overall "Air Quality" (Excellent/Good/Fair/Poor)
- Shows: Temperature & Humidity
- Shows: Simple recommendations ("Open Window" / "Air is Good")
- No PPM, µg/m³, or other technical units

### Advanced Profiles (For Power Users)
- **All technical sensors and measurements**
- **Customizable thresholds** for every parameter
- **Calibration controls** and diagnostics
- **Detailed data** for analysis and automation
- Perfect for technical users, HVAC integration, or commercial applications

#### Presence Detection - Advanced (`features/presence_advanced_profile.yaml`)
- Multi-zone tracking (up to 3 zones)
- Individual target tracking (up to 3 simultaneous targets)
- Distance measurements in cm
- Adjustable sensitivity modes (Quiet Room / Normal / High Traffic)
- Customizable timeout settings
- Full diagnostic sensors

#### Air Quality - Advanced (`features/airiq_advanced_profile.yaml`)
- Individual sensors: CO₂ (ppm), PM1.0, PM2.5, PM4.0, PM10 (µg/m³)
- VOC & NOx Index (0-500 scale)
- Temperature, Humidity, Atmospheric Pressure, Light Level
- Customizable thresholds for every sensor
- Sensor calibration controls
- 24-hour trend analysis
- HVAC integration helpers

## Usage

### Using Pre-Built Products (Recommended)

For most users, start with a pre-built product configuration from the `/products/` directory:

```yaml
substitutions:
  device_name: living-room-sensor
  friendly_name: "Living Room Sensor"

packages:
  firmware:
    url: https://github.com/sense360store/esphome-public
    ref: v2.2.0
    files:
      - products/sense360-core-ceiling.yaml
```

### Custom Module Combinations

For advanced users who want to build custom configurations:

```yaml
substitutions:
  device_name: office-sensor
  friendly_name: "Office IAQ Monitor"
  # Override defaults
  co2_good_limit: "800"
  pm2_5_good_limit: "12"
  presence_timeout: "60"

packages:
  firmware:
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
      # Sensor modules
      - packages/expansions/airiq_ceiling.yaml
      - packages/features/airiq_advanced_profile.yaml
      - packages/expansions/presence_ceiling.yaml
      - packages/features/presence_basic_profile.yaml
```

## Base Components

Located in `packages/base/`:

- `complete.yaml` - All base components combined
- `wifi.yaml` - WiFi configuration
- `api_encrypted.yaml` - Home Assistant API with encryption
- `ota.yaml` - Over-the-air updates
- `time.yaml` - Time synchronization
- `logging.yaml` - Logging configuration
- `bluetooth_proxy.yaml` - Bluetooth proxy functionality

## Hardware Drivers

Located in `packages/hardware/`:

- `sense360_core_ceiling.yaml` - Ceiling core board configuration
- `sense360_core_wall.yaml` - Wall/desk core board configuration
- `led_ring_ceiling.yaml` - Ceiling LED ring
- `led_ring_wall.yaml` - Wall LED ring
- `power_poe.yaml` - PoE power module
- `power_240v.yaml` - 240V AC power module

## Expansion Modules

Located in `packages/expansions/`:

### AirIQ (Air Quality)
- `airiq_ceiling.yaml` - Ceiling mount
- `airiq_wall.yaml` - Wall mount

### Comfort (Environmental)
- `comfort_ceiling.yaml` - Ceiling mount
- `comfort_wall.yaml` - Wall mount

### Presence (Occupancy)
- `presence_ceiling.yaml` - Ceiling mount (LD2450)
- `presence_wall.yaml` - Wall mount (LD2450)
- `presence_ld2412.yaml` - LD2412 variant

### Bathroom (Specialty)
- `airiq_bathroom_base.yaml` - Base bathroom sensors
- `airiq_bathroom_pro.yaml` - Pro bathroom with additional sensors

### Fan Control
- `fan_pwm.yaml` - PWM fan control
- `fan_gp8403.yaml` - 0-10V DAC fan control

## Support

- **Documentation**: [GitHub Docs](https://github.com/sense360store/esphome-public/tree/main/docs)
- **Issues**: [GitHub Issues](https://github.com/sense360store/esphome-public/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sense360store/esphome-public/discussions)

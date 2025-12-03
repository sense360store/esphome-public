# ESPHome Packages Structure

This directory contains modular ESPHome configuration packages organized by category.

## Directory Structure

```
packages/
├── base/              # Core system components
├── features/          # Feature profiles (basic & advanced)
├── hardware/          # Hardware drivers
└── products/          # Legacy product configurations (deprecated)
```

## Feature Profiles - Basic vs Advanced

Starting with v3.0.0, all features are available in two versions:

### Basic Profiles (Recommended for Most Users)
- **Simple, user-friendly interface**
- **No technical jargon** - uses terms everyone understands
- **Easy-to-read measurements**
- Perfect for home users who want simple, clear information

#### Presence Detection - Basic (`features/presence_basic.yaml`)
- Shows: "Room Occupied" (Yes/No)
- Shows: "Activity Level" (Still/Moving)
- No complex zones or technical data

#### Air Quality - Basic (`features/airiq_basic.yaml`)
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

#### Presence Detection - Advanced (`features/presence_advanced.yaml`)
- Multi-zone tracking (up to 3 zones)
- Individual target tracking (up to 3 simultaneous targets)
- Distance measurements in cm
- Adjustable sensitivity modes (Quiet Room / Normal / High Traffic)
- Customizable timeout settings
- Full diagnostic sensors

#### Air Quality - Advanced (`features/airiq_advanced.yaml`)
- Individual sensors: CO₂ (ppm), PM1.0, PM2.5, PM4.0, PM10 (µg/m³)
- VOC & NOx Index (0-500 scale)
- Temperature, Humidity, Atmospheric Pressure, Light Level
- Customizable thresholds for every sensor
- Sensor calibration controls
- 24-hour trend analysis
- HVAC integration helpers

## Usage

### Using Basic Profiles

For simple home automation:

```yaml
substitutions:
  device_name: bedroom-sensor
  friendly_name: "Bedroom Sensor"

packages:
  firmware:
    url: https://github.com/sense360store/esphome-public
    ref: v3.0.0
    files:
      - products/sense360-mini-presence-basic.yaml
      # or
      - products/sense360-mini-airiq-basic.yaml
```

### Using Advanced Profiles

For technical users wanting full control:

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
    ref: v3.0.0
    files:
      - products/sense360-mini-presence-advanced.yaml
      # or
      - products/sense360-mini-airiq-advanced.yaml
```

## Migration from v2.x to v3.0

### Breaking Changes
- Old profile files (`presence_basic_profile.yaml`, `airiq_basic_profile.yaml`) are **deprecated**
- Root-level directories (`/base/`, `/features/`, `/hardware/`) have been **removed**
- All new configurations should use `/packages/` structure

### Migration Steps

1. **Update your product reference** in your device config:

   **Old (v2.x):**
   ```yaml
   files:
     - products/sense360-mini-airiq.yaml
   ```

   **New (v3.0+):**
   ```yaml
   files:
     - products/sense360-mini-airiq-basic.yaml    # Simple version
     # or
     - products/sense360-mini-airiq-advanced.yaml # Full control
   ```

2. **Review sensors in Home Assistant** - names have changed for clarity:
   - Old: "PM2.5" → New (Basic): "Air Quality"
   - Old: "Occupancy" → New (Basic): "Room Occupied"
   - Old: "Target Count" → New (Basic): Hidden (use "Room Occupied" instead)

3. **Update automations** if using old sensor names

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

- `sense360_core_mini.yaml` - Mini board core configuration
- `sense360_core_ceiling.yaml` - Ceiling board core configuration
- `presence_ld2450.yaml` - HLK-LD2450 presence sensor driver

## Support

- **Documentation**: [GitHub Docs](https://github.com/sense360store/esphome-public/tree/main/docs)
- **Issues**: [GitHub Issues](https://github.com/sense360store/esphome-public/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sense360store/esphome-public/discussions)

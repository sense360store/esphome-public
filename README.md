# Sense360 ESPHome Firmware

Official ESPHome firmware repository for [Sense360](https://mysense360.com) environmental monitoring devices.

[![ESPHome](https://img.shields.io/badge/ESPHome-2025.10%2B-blue)](https://esphome.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Release](https://img.shields.io/github/v/release/sense360store/esphome-public)](https://github.com/sense360store/esphome-public/releases)
[![CI](https://github.com/sense360store/esphome-public/workflows/Test%20ESPHome%20Configs/badge.svg)](https://github.com/sense360store/esphome-public/actions)

## What's New in Version 2.1.0

- Overall air quality LED color entity that mirrors consolidated status across the device and dashboards
- New air quality status text sensor and air quality warning binary sensor for Home Assistant automations
- Additional status text sensors (Most Valuable Pollutant, MVP Severity, LED Mode) for clearer UI information
- Human-friendly particulate naming to improve clarity
- Unified and persisted night brightness controls
- Improved AirIQ LED handling with full-bright daytime mode and safe handling of unknown states
- PM LED severity based on the worst particulate tier across all measurements

## Key Features

- **Comprehensive Air Quality Monitoring**: Measures CO2, VOC, NOx, PM1.0, PM2.5, PM4.0, and PM10
- **Advanced Presence Detection**: mmWave radar (LD2450) for accurate occupancy sensing
- **Environmental Sensing**: Temperature, humidity, and ambient light monitoring
- **Visual Feedback**: Addressable RGB LED status indicators
- **Smart Home Integration**: Native Home Assistant support through ESPHome
- **Wireless Updates**: Over-the-air firmware updates
- **Bluetooth Proxy**: Built-in BLE proxy for extended Home Assistant coverage

## Repository Organization

This repository contains firmware and configuration files organized by purpose:

- **base/** - Core functionality (WiFi, API, OTA, logging)
- **hardware/** - Hardware definitions for Mini and Ceiling boards
- **features/** - Feature modules (AirIQ, Presence, LEDs, Health)
- **products/** - Complete device configurations (recommended starting point)
- **packages/** - Modular building blocks for custom composition
- **examples/** - Customer configuration templates
- **docs/** - Installation and configuration guides

### For Most Users

The `products/` directory contains ready-to-use configurations that are fully tested and tagged for each release. Start here unless you need custom functionality.

### For Advanced Users

The `packages/` directory provides modular building blocks for creating custom configurations. These components may change between releases and require more technical knowledge to use correctly.

---

## Quick Start Guide

### Step 1: Choose Your Product

Select the configuration that matches your hardware:

| Product | Description | Config File |
|---------|-------------|-------------|
| Sense360 Mini + AirIQ | Complete air quality monitoring with presence detection | `products/sense360-mini-airiq.yaml` |
| Sense360 Mini + Presence | Presence detection only | `products/sense360-mini-presence.yaml` |
| Sense360 Ceiling + Presence | Ceiling-mounted presence detection | `products/sense360-ceiling-presence.yaml` |

### Step 2: Create Your Configuration

In your ESPHome dashboard, create a new file (for example, `sense360-living-room.yaml`):

```yaml
# Device identification
substitutions:
  device_name: sense360-living-room  # Change this to your device name
  friendly_name: "Living Room Sense360"  # Change this to your preferred name

# ESPHome configuration
esphome:
  name: ${device_name}
  friendly_name: ${friendly_name}
  min_version: 2025.10.0

# Load firmware from GitHub
packages:
  sense360_firmware:
    url: https://github.com/sense360store/esphome-public
    ref: v2.1.0  # Use the latest stable version
    files:
      - products/sense360-mini-airiq.yaml
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

Add the following to your `secrets.yaml` file:

```yaml
wifi_ssid: "YourNetworkName"
wifi_password: "YourWiFiPassword"
api_encryption_key: "GENERATE_WITH_ESPHOME_WIZARD"
ota_password: "your-secure-password"
```

### Step 4: Flash Your Device

1. **Initial flash**: Connect your device via USB-C cable, then click "Install" and select "Plug into this computer"
2. **Future updates**: All updates can be done wirelessly. Just click "Install" and select "Wirelessly"

---

## Updating Firmware

Check the [Releases](https://github.com/sense360store/esphome-public/releases) page to see if a new version is available.

To update your device:
1. Open your configuration file
2. Change the `ref` line to the new version number (for example, change `ref: v2.0.0` to `ref: v2.1.0`)
3. Save the file and install wirelessly

The device will automatically download and apply the updated firmware.

---

## Documentation

- [Installation Guide](docs/installation.md) - Step-by-step setup instructions
- [Configuration Reference](docs/configuration.md) - Customization options and settings
- [Development Guide](docs/development.md) - Contributing and testing
- [Changelog](CHANGELOG.md) - Version history and release notes

---

## Customization Examples

### Adjusting Air Quality Thresholds

You can customize when your device indicates good, moderate, or unhealthy air quality:

```yaml
substitutions:
  device_name: my-sense360
  friendly_name: "My Sense360"

  # Adjust thresholds (all values shown are in ppm or µg/m³)
  co2_good_limit: "800"           # Default: 750 ppm
  sen55_pm2_5_good_limit: "12"    # Default: 10 µg/m³
  sen55_voc_good_limit: "100"     # Default: 80 index
```

### Adding Custom Automations

Example of creating a high CO2 alert:

```yaml
binary_sensor:
  - platform: template
    name: "High CO2 Alert"
    lambda: |-
      return id(scd4x_co2).state > 1200;
```

---

## Advanced Configuration

For users who need to customize specific components, you can load individual modules instead of using a complete product configuration. This requires understanding of ESPHome and the firmware architecture.

Example of loading specific components:

```yaml
packages:
  sense360_base:
    url: https://github.com/sense360store/esphome-public
    ref: v2.1.0
    files:
      - base/wifi.yaml
      - base/api_encrypted.yaml
      - hardware/sense360_core_mini.yaml
      # Select presence sensor (choose one)
      - features/presence_basic_profile.yaml           # For HLK-LD2450
      # - features/presence_basic_profile_ld2412.yaml  # For HLK-LD2412
    refresh: 1d
```

See the [Configuration Reference](docs/configuration.md) for complete details on advanced customization options.

---

## Hardware Information

Purchase Sense360 devices at [mysense360.com](https://mysense360.com)

### Supported Hardware

- **Main Board**: ESP32-S3 (DevKitC-1)
- **Air Quality Sensors**:
  - SEN55 (PM1.0, PM2.5, PM4.0, PM10, VOC, NOx)
  - SCD4x (CO2)
  - SHT30 (Temperature and Humidity)
  - LTR303 (Ambient Light)
- **Presence Sensors**: HLK-LD2450 mmWave radar
- **Visual Indicators**: WS2812 addressable LEDs (4 pixels)
- **Connectivity**: WiFi 2.4GHz, Bluetooth LE

### System Requirements

- **ESPHome**: Version 2025.10.0 or newer
- **Home Assistant**: Version 2024.1.0 or newer (recommended)
- **Power**: USB-C, PoE, or AC adapter depending on model

---

## Use Cases

Common applications for Sense360 devices:

- **Home Office**: Monitor CO2 levels for optimal productivity
- **Bedroom**: Track sleep environment and automate ventilation
- **Living Room**: Occupancy-based lighting and climate control
- **Kitchen**: Air quality monitoring during cooking
- **Bathroom**: Humidity-based ventilation control
- **Workshop**: VOC and particulate monitoring during projects

---

## Support and Community

- **Installation Help**: See the [Installation Guide](docs/installation.md)
- **Report Issues**: [GitHub Issues](https://github.com/sense360store/esphome-public/issues)
- **Discussions**: [Community Forum](https://github.com/sense360store/esphome-public/discussions)
- **Email Support**: support@mysense360.com

---

## Contributing

Contributions are welcome! Please see the [Development Guide](docs/development.md) for:
- Setting up your development environment
- Running tests and validation
- Pre-commit hooks and CI/CD pipeline
- Code quality guidelines

All pull requests must pass automated testing before merging.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Built with [ESPHome](https://esphome.io/)
- Supported by the Home Assistant community
- Thanks to all contributors and testers

---

## Additional Resources

- [Purchase Devices](https://mysense360.com)
- [ESPHome Documentation](https://esphome.io)
- [Home Assistant](https://www.home-assistant.io)
- [GitHub Releases](https://github.com/sense360store/esphome-public/releases)

# Sense360 ESPHome Firmware

Official ESPHome firmware repository for [Sense360](https://mysense360.com) environmental monitoring devices.

[![ESPHome](https://img.shields.io/badge/ESPHome-2025.10%2B-blue)](https://esphome.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Release](https://img.shields.io/github/v/release/sense360store/esphome-public)](https://github.com/sense360store/esphome-public/releases)

## 🌟 Features

- **Comprehensive Air Quality Monitoring**: CO2, VOC, NOx, PM1.0, PM2.5, PM4.0, PM10
- **Advanced Presence Detection**: mmWave radar (LD2450) for precise occupancy sensing
- **Environmental Sensing**: Temperature, humidity, and ambient light monitoring
- **Visual Feedback**: Addressable RGB LED status indicators
- **Smart Home Integration**: Native Home Assistant support via ESPHome
- **Wireless Updates**: OTA firmware updates for hassle-free maintenance
- **Bluetooth Proxy**: Built-in BLE proxy for extended Home Assistant coverage

## 📦 Repository Structure

```
esphome-public/
├── base/          - Core functionality (WiFi, API, OTA, logging)
├── hardware/      - Hardware definitions (Mini, Ceiling boards)
├── features/      - Feature modules (AirIQ, Presence, LEDs, Health)
├── products/      - Complete device configurations
├── packages/      - Modular building blocks for custom composition
├── examples/      - Customer configuration templates
└── docs/          - Installation and configuration guides
```

`base/`, `features/`, `hardware/`, and `products/` are the release-tested, customer-facing entry points that are tagged for ESPHome package consumption. The `packages/` directory keeps composable building blocks and internal profiles that may change between releases; use these only if you are assembling custom stacks or contributing new product recipes. For production or customer installs, reference the files under `products/`.

## 🚀 Quick Start

### 1. Choose Your Product

| Product | Description | Config File |
|---------|-------------|-------------|
| **Sense360 Mini + AirIQ** | Full air quality + presence (recommended) | `products/sense360-mini-airiq.yaml` |
| **Sense360 Mini + Presence** | Presence detection only | `products/sense360-mini-presence.yaml` |
| **Sense360 Ceiling + Presence** | Ceiling-mounted presence | `products/sense360-ceiling-presence.yaml` |

### 2. Create Your Configuration

In your ESPHome dashboard, create a new file (e.g., `sense360-living-room.yaml`):

```yaml
# Device identification
substitutions:
  device_name: sense360-living-room  # Change this
  friendly_name: "Living Room Sense360"  # Change this

# ESPHome configuration
esphome:
  name: ${device_name}
  friendly_name: ${friendly_name}
  min_version: 2025.10.0

# Load firmware from GitHub
packages:
  sense360_firmware:
    url: https://github.com/sense360store/esphome-public
    ref: v2.0.0  # Latest stable version
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

### 3. Configure Secrets

Add to your `secrets.yaml`:

```yaml
wifi_ssid: "YourNetworkName"
wifi_password: "YourWiFiPassword"
api_encryption_key: "GENERATE_WITH_ESPHOME_WIZARD"
ota_password: "your-secure-password"
```

### 4. Flash Your Device

1. **Initial flash**: Connect via USB-C, click "Install" → "Plug into this computer"
2. **Future updates**: All updates are wireless! Just click "Install" → "Wirelessly"

## 🔄 Updating Firmware

Check [Releases](https://github.com/sense360store/esphome-public/releases) for the latest version.

To update:
1. Edit your configuration file
2. Change `ref: v2.0.0` to the new version when updates are released
3. Save and install wirelessly

**That's it!** Your device will automatically fetch and apply the updated firmware.

## 📖 Documentation

- [Installation Guide](docs/installation.md) - Detailed setup instructions
- [Configuration Reference](docs/configuration.md) - Customization options
- [Troubleshooting](docs/troubleshooting.md) - Common issues and solutions
- [API Reference](docs/api-reference.md) - Sensor and component documentation
- [Changelog](CHANGELOG.md) - Version history

## 🎯 Customization

### Override Air Quality Thresholds

```yaml
substitutions:
  device_name: my-sense360
  friendly_name: "My Sense360"
  
  # Custom thresholds
  co2_good_limit: "800"           # Default: 750 ppm
  sen55_pm2_5_good_limit: "12"    # Default: 10 µg/m³
  sen55_voc_good_limit: "100"     # Default: 80 index
```

### Add Custom Automations

```yaml
# High CO2 alert
binary_sensor:
  - platform: template
    name: "High CO2 Alert"
    lambda: |-
      return id(scd4x_co2).state > 1200;
```

### Mix and Match Components (Advanced)

For custom builds, load specific components:

```yaml
packages:
  sense360_base:
    url: https://github.com/sense360store/esphome-public
    ref: v2.0.0
    files:
      - base/wifi.yaml
      - base/api_encrypted.yaml
      - hardware/sense360_core_mini.yaml
      # Presence (choose one)
      - features/presence_basic_profile.yaml           # HLK-LD2450
      # - features/presence_basic_profile_ld2412.yaml  # HLK-LD2412
    refresh: 1d
```

## 🛒 Hardware

Purchase Sense360 devices at [mysense360.com](https://mysense360.com)

## 💬 Support & Community

- **Documentation**: [Installation Guide](docs/installation.md)
- **Issues**: [Report a bug](https://github.com/sense360store/esphome-public/issues)
- **Discussions**: [Community forum](https://github.com/sense360store/esphome-public/discussions)
- **Email**: support@mysense360.com

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) first.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [ESPHome](https://esphome.io/) - Amazing ESP32 framework
- Inspired by the Home Assistant community
- Thanks to all contributors and testers

## 🔧 Technical Specifications

### Supported Hardware

- **Board**: ESP32-S3 (DevKitC-1)
- **Sensors**:
  - **Air Quality**: SEN55 (PM, VOC, NOx), SCD4x (CO2), SHT30 (T/H), LTR303 (Light)
  - **Presence**: HLK-LD2450 (mmWave radar)
- **Indicators**: WS2812 addressable LEDs (4 pixels)
- **Connectivity**: WiFi 2.4GHz, Bluetooth LE

### Requirements

- **ESPHome**: 2025.10.0 or newer
- **Home Assistant**: 2024.1.0 or newer (recommended)
- **Power**: USB-C, PoE, or AC adapter (depending on model)

## 📊 Example Use Cases

- **Home Office**: Monitor CO2 and air quality for optimal productivity
- **Bedroom**: Track sleep environment and automate ventilation
- **Living Room**: Occupancy-based lighting and climate control
- **Kitchen**: Air quality monitoring while cooking
- **Bathroom**: Humidity-based ventilation control
- **Workshop**: VOC and particulate monitoring during projects

## 🔗 Links

- [Purchase Devices](https://mysense360.com)
- [ESPHome Documentation](https://esphome.io)
- [Home Assistant](https://www.home-assistant.io)
- [GitHub Releases](https://github.com/sense360store/esphome-public/releases)

---

**Made with ❤️ for the smart home community**

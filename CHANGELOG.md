# Changelog

All notable changes to the Sense360 ESPHome firmware will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- None yet.

### Changed
- None yet.

### Breaking Changes
- None.

### Upgrade
- None.

---

## [2.1.0] - 2025-12-03

### Added
- Overall air quality LED color entity to mirror consolidated device status across dashboards and automations.
- New `air_quality_status` text sensor and `air_quality_warning` binary sensor for clear HA-friendly status and alerting.
- MVP Pollutant, MVP Severity, and LED Mode text sensors for clearer status reporting.
- Human-readable particulate names across UI outputs to improve clarity.
- Global persistence for unified night brightness so Mini LED strip settings survive restarts.

### Changed
- Night-mode revamp for the Mini LED strip with unified `mini_night_brightness` control for consistent behavior.
- Daytime full-bright behavior when AirIQ 4-LED Status is enabled to keep indicators legible.
- Unified night brightness via the `mini_night_brightness` number entity with a persisted global fallback for night-mode consistency.
- Optional night-light behavior triggered by presence with an inactivity timeout for graceful fade-out.
- LD2412-driven presence handling with delayed off timing to prevent premature darkening.
- Robust LED state handling when states are unknown or unavailable to avoid glitches.
- PM LED now uses the worst tier across PM1.0/PM2.5/PM4.0/PM10 so alerts reflect the most severe reading.
- Safer PM tier computation with null/unknown handling and corrected PM4.0 globals for accurate air quality signaling.
- Clarified LD2450 basic presence profile tagging and documented selection between LD2450 and LD2412 profile options.

### Breaking Changes
- None.

### Upgrade
- Update package references from `ref: v2.0.2` to `ref: v2.1.0`, and use the new `air_quality_status` and `air_quality_warning` entities in dashboards and automations.

---

## [2.0.1] - 2025-12-01

### Added
- Fan cleaning control for SEN55 sensors to trigger maintenance cycles.

---

## [2.0.0] - 2025-06-02

### Added
- Enhanced presence zone configuration UI with per-zone calibration and live previews.
- Custom LED animation patterns for air quality states and occupancy feedback.
- Energy monitoring integration with power and consumption sensors for Sense360 devices.
- Multi-device synchronization to align presence tracking and air quality baselines across rooms.
- Advanced air quality trending with rolling averages and visual indicators for long-term insights.

---

## [1.1.8] - 2025-12-10

### Fixed
- Ensured SHT30 calibration reruns automatically when reference temperature or humidity values change, even if raw readings arrive later, so reference inputs always adjust live measurements.

---

## [1.1.7] - 2025-11-28

### Changed
- Updated all product and documentation references to the v1.1.7 release tag.

### Removed
- Removed MiCS gas sensor configuration and related documentation from the firmware packages.

---

## [1.0.0] - 2025-11-06

### Initial Public Release

This is the first public release of the Sense360 ESPHome firmware, providing a complete, modular system for environmental monitoring and presence detection.

#### Added

**Core Features:**
- Complete ESPHome firmware for Sense360 devices
- GitHub-based package distribution system
- Modular architecture for easy customization
- Over-the-air (OTA) update support
- Encrypted API communication

**Hardware Support:**
- ESP32-S3 board support (DevKitC-1)
- Sense360 Mini (wall-mounted) hardware profile
- Sense360 Ceiling hardware profile
- I2C bus configuration and management

**Air Quality Monitoring (AirIQ):**
- SEN55 sensor support:
  - PM1.0, PM2.5, PM4.0, PM10 particulate matter
  - VOC (Volatile Organic Compounds) index
  - NOx (Nitrogen Oxides) index
- SCD4x CO2 sensor with automatic calibration
- SHT30 temperature and humidity sensor
- LTR303 ambient light sensor
- MiCS-6814 gas sensor support:
  - NO2 (Nitrogen Dioxide) detection
  - CO (Carbon Monoxide) detection
  - H2 (Hydrogen) detection
  - NH3 (Ammonia) detection
  - Ethanol detection
  - CH4 (Methane) presence detection

**Presence Detection:**
- HLK-LD2450 mmWave radar integration
- Multi-zone occupancy tracking
- Target counting and positioning
- Basic and Pro presence profiles
- Configurable detection zones

**Visual Indicators:**
- 4-pixel addressable LED (WS2812) support
- Air quality status visualization
- Color-coded health indicators
- Customizable LED patterns

**Device Health:**
- WiFi signal strength monitoring
- Uptime tracking
- Sensor status reporting
- Diagnostic information
- Error detection and reporting

**Connectivity:**
- WiFi with fallback access point
- Bluetooth Low Energy proxy for Home Assistant
- mDNS/Bonjour discovery
- Improv Serial for WiFi provisioning

**Product Configurations:**
- Sense360 Mini + AirIQ (full sensor suite)
- Sense360 Mini + Presence (occupancy only)
- Sense360 Ceiling + Presence (ceiling mount)

**Documentation:**
- Comprehensive installation guide
- Configuration reference
- Troubleshooting guide
- API documentation
- Customer configuration templates
- Secrets management guide

**Developer Features:**
- Modular package system
- Reusable base components
- Hardware abstraction layers
- Feature profiles
- Version-controlled releases

#### Component Versions
- ESPHome: 2025.10.0+ required
- ESP-IDF Framework
- Arduino Framework compatible

#### Known Limitations
- Requires ESPHome 2025.10.0 or newer
- Initial flash must be via USB
- WiFi 2.4GHz only (5GHz not supported)
- MiCS sensor requires 48-hour burn-in period
- SCD4x calibration takes up to 7 days

#### Breaking Changes
- N/A (initial release)

---

## Version History Format

Future releases will follow this format:

### [X.Y.Z] - YYYY-MM-DD

#### Added
- New features and capabilities

#### Changed
- Changes to existing functionality

#### Deprecated
- Features being phased out (still functional)

#### Removed
- Removed features

#### Fixed
- Bug fixes and corrections

#### Security
- Security improvements and patches

---

## Upgrade Guide

### From v1.1.x to v2.0.0

If you were using v1.1.x or development versions:

1. Update your configuration to use the new release tag:
   ```yaml
   packages:
     sense360_firmware:
       url: https://github.com/sense360store/esphome-public
       ref: v2.0.0
       files:
         - products/sense360-mini-airiq.yaml
   ```

2. Ensure your `secrets.yaml` has all required keys:
   - `wifi_ssid`
   - `wifi_password`
   - `api_encryption_key`
   - `ota_password`

3. Flash via USB once, then all future updates are OTA

---

## Support

For questions, issues, or feature requests:
- GitHub Issues: https://github.com/sense360store/esphome-public/issues
- Documentation: https://github.com/sense360store/esphome-public/tree/main/docs
- Email: support@mysense360.com

---

## Contributors

Thanks to everyone who contributed to this release:
- Development team at Sense360
- Beta testers from the community
- ESPHome project contributors

---

**Note**: This is a living document. Check back regularly for updates about new releases and features.

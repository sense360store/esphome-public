# Changelog

All notable changes to the Sense360 ESPHome firmware will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Sense360 Ceiling S3 Board**: Complete configuration for ESP32-S3-WROOM-1-N16R8 based ceiling board
  - New hardware profile: `sense360_core_ceiling_s3.yaml` with correct GPIO mappings from schematic
  - I2C primary bus on GPIO26/GPIO8 @ 100kHz for sensor modules
  - Dual UART support for presence sensors: Hi-Link LD2450 (GPIO38/39) and SEN0609/C4001 (GPIO4/5)
  - WS2812B LED ring control on GPIO14 with level shifter support
  - Fan control output on GPIO15 with SI2302 MOSFET
  - Module-specific configurations: `airiq_ceiling_s3.yaml`, `comfort_ceiling_s3.yaml`, `presence_ceiling_s3.yaml`
  - Complete product configuration: `sense360-ceiling-s3-full.yaml`
- **Sense360 Core Board Support**: New board variants and power configurations
  - Sense360 Core Wall and Ceiling board profiles
  - Comprehensive GPIO mapping and power management
  - PoE and USB-C power configurations
- **Expansion Module System**: Modular sensor expansion support
  - AirLQ expansion module with comprehensive sensor mapping
  - Comfort Ceiling expansion module mapping
  - Presence Module Ceiling with Hi-Link LD2450 and DFRobot SEN0609/C4001 support
  - Phase 2 expansion module drivers and feature profiles
- **LD2412 mmWave Sensor**: Multi-sensor presence detection support
  - Gate threshold configuration
  - Advanced and basic presence profiles
- **Ceiling LED Ring**: Air quality visualization for ceiling-mounted devices
- **CI/CD Pipeline**: GitHub Actions workflows for automated testing and validation
  - `test.yml`: Comprehensive test suite validating all product configurations with ESPHome compilation
  - `validate.yml`: Quick YAML syntax and structure validation for fast feedback
  - Matrix testing across all product configurations to catch issues early
  - Automated C++ header formatting checks with clang-format
- **Pre-commit Hooks**: Local validation before commits
  - YAML linting and validation
  - Python code formatting (Black) and linting (Flake8)
  - C++ formatting with clang-format
  - Automated configuration validation script
- **Validation Script** (`tests/validate_configs.py`): Python script to validate YAML syntax and structure
  - Supports ESPHome custom YAML tags (!secret, !include, !extend, !lambda)
  - Validates all configuration files in products/, packages/, base/, features/, hardware/, and tests/
  - Checks for required keys and proper structure
- **Development Documentation** (`docs/development.md`): Comprehensive guide for contributors
- **Development Dependencies** (`requirements-dev.txt`): All tools needed for local development
- **YAML Linting Configuration** (`.yamllint`): Consistent YAML style across the repository
- **Comprehensive Unit Test Suite**: Phase 1 testing infrastructure
- **Reset and Restart Buttons**: Added to product configurations for device management

### Changed
- Restructured headers for ESPHome remote package compatibility
- Refactored YAML structure with Basic/Advanced profile separation
- Hardware sensor outputs now internal for AirIQ advanced profile
- Consolidated LD2412 gate threshold configuration
- Shortened fallback SSID defaults and hostnames for better compatibility
- Adjusted Ethernet log level to match defaults
- Used non-strapping GPIO for diagnostics button
- Consolidated PoE binary sensors
- Improved documentation clarity and user-friendliness
- Updated README.md with CI badge and links to development guide
- Enhanced Contributing section with clear development workflow

### Fixed
- CI/CD pipeline validation for ESPHome YAML tags
- Duplicate entity name conflicts across ESPHome configs
- LD2450 configuration and GPIO3 strapping pin warning
- YAML structure issues and yamllint errors
- I2C extend mappings for mini four LEDs
- Various restore settings for switches and templates
- Removed unsupported LD2450 bluetooth password and zone sensors

### Known Issues
- **Ceiling S3 GPIO8 Conflict**: GPIO8 is used for both I2C_SCL and AirQ_Led in schematic
  - Impact: AirQ_Led cannot be used when I2C is active
  - Workaround: Use GPIO7 (AirQ_Status_Led) or LED ring (GPIO14) for visual feedback
  - Hardware fix needed: Move AirQ_Led to unused GPIO in next PCB revision

### Breaking Changes
- None.

### Upgrade
- For contributors: Install development dependencies with `pip install -r requirements-dev.txt` and set up pre-commit hooks with `pre-commit install`

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

## [1.1.8] - 2025-11-30

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

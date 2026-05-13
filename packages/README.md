# ESPHome Packages Structure

This directory contains modular ESPHome configuration packages organized by category.

> **Production Release-One ships `Ceiling-POE-VentIQ-RoomIQ`** — built from
> [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml)
> and published as `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`.
> Most customers should use [WebFlash](https://mysense360.com); this README
> documents the lower-level package surface used by both Release-One and
> legacy / Mini-board products. FanTRIAC is blocked pending HW-005; the
> Sense360 LED token is excluded from Release-One because the config string
> has no `LED` slot. See [`docs/release-one.md`](../docs/release-one.md).

> **WebFlash compatibility:** see [`docs/webflash-contract.md`](../docs/webflash-contract.md)
> for the canonical token list (`AirIQ`, `VentIQ`, `RoomIQ`, `FanRelay`,
> `FanPWM`, `FanDAC`, `FanTRIAC`, `LED`) used in firmware artifact names.
> Some package filenames below are legacy (`comfort_*.yaml`,
> `presence_*.yaml`, `airiq_bathroom_*.yaml`); the WebFlash contract is the
> source of truth for artifact naming and supersedes filesystem labels.

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

For most users, start with a pre-built product configuration from the
`/products/` directory. The Release-One product is the recommended default:

```yaml
substitutions:
  device_name: sense360-bathroom
  friendly_name: "Bathroom Sense360"

packages:
  firmware:
    url: https://github.com/sense360store/esphome-public
    ref: v1.0.0  # Pin to a release tag — never use 'main' in production
    files:
      - products/sense360-ceiling-poe-ventiq-roomiq.yaml  # Release-One
```

The `sense360-core-*.yaml` and `sense360-mini-*.yaml` products are
**legacy-compatible** and remain available for users with older hardware.

### Custom Module Combinations

For advanced users who want to build custom configurations. **The example
below is a legacy-compatible custom build** (AirIQ + LED-ring ceiling
configuration); it is not the Release-One module set. Release-One users
should reference the Release-One product YAML above instead. The Sense360
LED token is excluded from Release-One — the example below includes
`led_ring_ceiling.yaml` only because this is an explicit non-Release-One
custom build.

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
    ref: v1.0.0  # Pin to a release tag — never use 'main' in production
    files:
      # Base system
      - packages/base/wifi.yaml
      - packages/base/api_encrypted.yaml
      - packages/base/ota.yaml
      - packages/base/time.yaml
      # Core hardware (legacy-compatible AirIQ + LED ceiling build)
      - packages/hardware/sense360_core_ceiling.yaml
      - packages/hardware/led_ring_ceiling.yaml   # Sense360 LED — not in Release-One
      # Sensor modules
      - packages/expansions/airiq_ceiling.yaml    # AirIQ — Release-One uses VentIQ
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

### AirIQ (Air Quality, WebFlash token: `AirIQ`)
- `airiq_ceiling.yaml` - Ceiling mount
- `airiq_wall.yaml` - Wall mount

### Comfort (legacy → WebFlash `RoomIQ`, comfort half)
- `comfort_ceiling.yaml` - Ceiling mount
- `comfort_wall.yaml` - Wall mount

### Presence (legacy → WebFlash `RoomIQ`, mmWave half)
- `presence_ceiling.yaml` - Ceiling mount (LD2450)
- `presence_wall.yaml` - Wall mount (LD2450)
- `presence_ld2412.yaml` - LD2412 variant

### Bathroom (legacy → WebFlash `VentIQ`)
- `airiq_bathroom_base.yaml` - VentIQ Base
- `airiq_bathroom_pro.yaml` - VentIQ Pro

### Fan Control (firmware-distinct WebFlash variants)
- `fan_relay.yaml` - `FanRelay` (S360-310, on/off relay)
- `fan_pwm.yaml` - `FanPWM` (S360-311, 25 kHz PWM)
- `fan_gp8403.yaml` - `FanDAC` (S360-312, 0–10 V analog)
- `fan_triac.yaml` - `FanTRIAC` (S360-320, AC phase-cut dimmer)

> **Do not** publish a WebFlash artifact with a generic `Fan` token —
> each driver variant produces a separate firmware binary. See
> [`docs/webflash-contract.md`](../docs/webflash-contract.md) §3 and §5.

## Support

- **Documentation**: [GitHub Docs](https://github.com/sense360store/esphome-public/tree/main/docs)
- **Issues**: [GitHub Issues](https://github.com/sense360store/esphome-public/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sense360store/esphome-public/discussions)

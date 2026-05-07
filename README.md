# Sense360 ESPHome Firmware

Official ESPHome firmware repository for [Sense360](https://mysense360.com) environmental monitoring devices.

[![ESPHome](https://img.shields.io/badge/ESPHome-2025.10%2B-blue)](https://esphome.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Release](https://img.shields.io/github/v/release/sense360store/esphome-public)](https://github.com/sense360store/esphome-public/releases)
[![CI - Build & Release Firmware](https://github.com/sense360store/esphome-public/actions/workflows/firmware-build-release.yml/badge.svg)](https://github.com/sense360store/esphome-public/actions/workflows/firmware-build-release.yml)
[![CI - Validate Firmware Configs](https://github.com/sense360store/esphome-public/actions/workflows/ci-validate-configs.yml/badge.svg)](https://github.com/sense360store/esphome-public/actions/workflows/ci-validate-configs.yml)

---

## Which Path Should I Use?

| Path | Who | What it gives you |
|------|-----|-------------------|
| **WebFlash** (recommended) | Most customers | Browser-based flashing of official **signed** firmware. No tooling, no YAML. |
| **`esphome-public`** (this repo) | Advanced users | Inspect, fork, and customize the ESPHome YAML used by official Sense360 firmware. |

> **WebFlash is the production path.** It is what you get from the buy/install link on
> [mysense360.com](https://mysense360.com). This repo is the manual/custom firmware path
> linked from WebFlash — use it only if you want to read or modify the YAML.
>
> **Production users must pin to a release tag** (e.g. `ref: v1.0.0`). Never use
> `ref: main` for a device you depend on — `main` is a moving target.

---

## Release-One Configuration

The **Release-One** shipping configuration is:

```text
Ceiling-POE-VentIQ-FanTRIAC-RoomIQ
```

| Slot | Value | Meaning |
|------|-------|---------|
| Mount | `Ceiling` | Flush ceiling-mount Core board |
| Power | `POE` | IEEE 802.3af Power-over-Ethernet |
| Air Quality | `VentIQ` | Vent/bathroom-focused air-quality module |
| Fan Driver | `FanTRIAC` | TRIAC-based AC fan dimming output |
| Room Sense | `RoomIQ` | Comfort + presence sensing |

The matching ESPHome product YAML is
[`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml).

The matching firmware artifact published by CI is:

```text
Sense360-Ceiling-POE-VentIQ-FanTRIAC-RoomIQ-v1.0.0-stable.bin
```

See [Build Output Contract](#build-output-contract) below.

---

## WebFlash Taxonomy

WebFlash describes a device by chaining slot values into a config string:

```text
{Mount}-{Power}-{AirQuality}-{Fan}-{Room}
```

| Slot | Allowed Values |
|------|----------------|
| Mount | `Ceiling` |
| Power | `USB`, `POE`, `PWR` |
| Air Quality | `AirIQ`, `VentIQ` (mutually exclusive) |
| Fan Driver | `FanRelay`, `FanPWM`, `FanDAC`, `FanTRIAC` (firmware-distinct, not interchangeable) |
| Room Sense | `RoomIQ` |

Any config string from WebFlash maps 1:1 to a product YAML in
[`products/`](products/) and a published `.bin` asset on the matching GitHub Release.

---

## Sensor & Driver Modules

### RoomIQ — Room Sensing (Comfort + Presence)

Combines climate, light, and presence detection used to drive room-level
automations (lighting, HVAC, occupancy).

| Sensor | Measurements |
|--------|--------------|
| SHT4x | Temperature, Humidity |
| VEML7700 / LTR-303 | Ambient Light (lux) |
| HLK-LD2450 | mmWave presence, multi-target tracking, zone sensing |

**Best for:** Living rooms, bedrooms, offices — any room needing climate, light, and occupancy.

---

### AirIQ — General Air Quality

Comprehensive air quality monitoring for living spaces.

| Sensor | Measurements |
|--------|--------------|
| SPS30 | PM1.0, PM2.5, PM4.0, PM10 |
| SGP41 | VOC Index, NOx Index |
| SCD41 | CO2, Temperature, Humidity |
| BMP390 | Barometric Pressure |

**Best for:** Living rooms, bedrooms, home offices, workshops.

> **AirIQ and VentIQ are mutually exclusive** — pick one per device.

---

### VentIQ — Vent / Bathroom Air Quality

Vent-and-humidity-focused air-quality module. Optimized for bathrooms, laundry
rooms, and other high-humidity zones with shower/odor/mold detection.

| Variant | Sensors | Features |
|---------|---------|----------|
| Base | SHT4x, BMP390, SGP41 | Shower detection, mold-risk tracking, odor detection |
| Pro | + MLX90614, SPS30 | + IR surface temperature, condensation risk, PM monitoring |

**Best for:** Bathrooms, laundry rooms, shower rooms.

> **VentIQ replaces AirIQ** in the bathroom-focused taxonomy. They share the I2C
> bus and overlap in sensors — only one can be active per device.

---

### Fan Driver Modules

Fan output is **firmware-distinct** — the driver variants are not
interchangeable at runtime. You pick one when you flash:

| Module | Output | Typical Use |
|--------|--------|-------------|
| `FanRelay` | Mechanical/SSR relay (ON/OFF) | Single-speed extractor fans |
| `FanPWM` | 25 kHz PWM duty cycle | 4-pin PC fans, EC motors with PWM input |
| `FanDAC` | 0–10 V analog (GP8403) | Commercial HVAC, EC motors with 0–10 V input |
| `FanTRIAC` | Phase-cut TRIAC (AC dimming) | Standard AC ceiling/extractor fans |

> **TRIAC is not interchangeable with Relay/PWM/DAC.** Each variant produces a
> separate firmware binary because the GPIO + driver code differ.

---

## Mount and Power

| Slot | Value | Notes |
|------|-------|-------|
| Mount | `Ceiling` | Release-one ships ceiling mount only |
| Power | `USB` | 5 V USB-C, dev/portable |
| Power | `POE` | IEEE 802.3af, single-cable installs |
| Power | `PWR` | 100–240 V AC mains (HLK-PM01) |

---

## Compatibility Rules

These rules apply to every WebFlash config string and every product YAML:

1. **`AirIQ` and `VentIQ` are mutually exclusive.** A device runs one or the
   other, never both.
2. **`VentIQ` is the bathroom-focused air-quality module.** Use it for
   bathroom/laundry/shower environments.
3. **`RoomIQ` can be combined with either `AirIQ` or `VentIQ`.** It carries
   comfort and presence sensing and is independent of the air-quality slot.
4. **Fan driver variants are firmware-distinct.** `FanRelay`, `FanPWM`,
   `FanDAC`, and `FanTRIAC` each produce a separate firmware binary.
5. **`FanTRIAC` is not interchangeable with `FanRelay`, `FanPWM`, or `FanDAC`.**
   The GPIO routing and driver code differ; flashing the wrong driver will not
   control the fan correctly and may damage the load.

---

## Build Output Contract

CI in this repo publishes WebFlash-compatible `.bin` assets named:

```text
Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin
```

Where:

| Field | Source | Example |
|-------|--------|---------|
| `CONFIG_STRING` | WebFlash slot chain | `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` |
| `VERSION` | Release tag (`v` stripped) | `1.0.0` |
| `CHANNEL` | `stable`, `preview`, or `beta` | `stable` |

Example for Release-One:

```text
Sense360-Ceiling-POE-VentIQ-FanTRIAC-RoomIQ-v1.0.0-stable.bin
```

The mapping from product YAML → WebFlash filename is implemented in
[`scripts/product_name_mapper.py`](scripts/product_name_mapper.py) and exercised
by [`.github/workflows/firmware-build-release.yml`](.github/workflows/firmware-build-release.yml).

> **Signing:** This repo does **not** sign firmware. WebFlash remains the
> production signing/deployment authority and consumes the unsigned `.bin`
> assets attached to GitHub releases.

---

## Quick Start (Custom / Manual Flash)

> Most customers should use [WebFlash](https://mysense360.com) instead.
> This section is for advanced users running the YAML directly through
> ESPHome.

### 1. Pick a product configuration

Find the YAML matching your hardware in [`products/`](products/). For
Release-One that is:

```text
products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml
```

### 2. Configure secrets

Create a `secrets.yaml` (see [`examples/secrets.yaml.template`](examples/secrets.yaml.template)):

```yaml
wifi_ssid: "YourNetworkName"
wifi_password: "YourWiFiPassword"
api_encryption_key: "GENERATE_WITH_ESPHOME_WIZARD"
ota_password: "your-secure-ota-password"
web_username: "admin"
web_password: "your-secure-web-password"
```

> Generate an API key with `esphome wizard` or `openssl rand -base64 32`.

### 3. Reference the product from your device YAML

```yaml
packages:
  sense360_firmware:
    url: https://github.com/sense360store/esphome-public
    ref: v1.0.0  # Pin to a release tag — never use 'main' in production
    files:
      - products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml
    refresh: 1d

substitutions:
  device_name: sense360-bathroom
  friendly_name: "Bathroom Sense360"
```

> Do **not** add your own `wifi:`, `api:`, or `ota:` blocks — the package
> wires those up via `secrets.yaml`.

### 4. Flash

1. **Initial flash:** USB-C, then ESPHome Dashboard → Install → "Plug into this computer".
2. **Future updates:** ESPHome Dashboard → Install → "Wirelessly".

---

## Configuration Approaches

| Approach | Best For | Complexity |
|----------|----------|------------|
| **Product files** | Standard setups, most users | Simple |
| **Individual packages** | Custom module combinations | Moderate |
| **External components only** | From-scratch builds, experts | Advanced |

### Approach 1 — Product files (recommended)

```yaml
packages:
  sense360_firmware:
    url: https://github.com/sense360store/esphome-public
    ref: v1.0.0
    files:
      - products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml
    refresh: 1d
```

### Approach 2 — Individual packages

Compose your own product from base + hardware + expansion + feature packages:

```yaml
packages:
  sense360_base:
    url: https://github.com/sense360store/esphome-public
    ref: v1.0.0
    files:
      - packages/base/wifi.yaml
      - packages/base/api_encrypted.yaml
      - packages/hardware/sense360_core_ceiling.yaml
      - packages/hardware/power_poe.yaml
      - packages/expansions/airiq_bathroom_base.yaml  # VentIQ Base
      - packages/expansions/comfort_ceiling.yaml      # RoomIQ comfort
      - packages/expansions/presence_ceiling.yaml     # RoomIQ presence
      - packages/expansions/fan_triac.yaml            # FanTRIAC
      - packages/features/bathroom_profile.yaml
      - packages/features/presence_basic_profile.yaml
      - packages/features/fan_control_profile.yaml
    refresh: 1d
```

### Approach 3 — External components only (expert)

> ⚠️ Pulls only the C++ component drivers. You write all YAML yourself.

```yaml
external_components:
  - source:
      type: git
      url: https://github.com/sense360store/esphome-public
      ref: v1.0.0
    components: [ld2412, ld24xx]
    refresh: 1d
```

---

## Package Reference

| Category | Package | Description |
|----------|---------|-------------|
| **Base** | `packages/base/wifi.yaml` | WiFi connectivity |
| | `packages/base/api_encrypted.yaml` | Home Assistant API |
| | `packages/base/ota.yaml` | Over-the-air updates |
| | `packages/base/time.yaml` | Time synchronization |
| **Hardware** | `packages/hardware/sense360_core_ceiling.yaml` | Ceiling core board |
| | `packages/hardware/led_ring_ceiling.yaml` | Ceiling LED ring |
| | `packages/hardware/power_usb.yaml` | USB-C power |
| | `packages/hardware/power_poe.yaml` | PoE power |
| | `packages/hardware/power_240v.yaml` | AC mains power |
| **AirIQ** | `packages/expansions/airiq_ceiling.yaml` | Air-quality sensor pack |
| **VentIQ** | `packages/expansions/airiq_bathroom_base.yaml` | VentIQ Base |
| | `packages/expansions/airiq_bathroom_pro.yaml` | VentIQ Pro |
| **RoomIQ** | `packages/expansions/comfort_ceiling.yaml` | Climate + light |
| | `packages/expansions/presence_ceiling.yaml` | LD2450 presence |
| **Fan drivers** | `packages/expansions/fan_relay.yaml` | FanRelay (ON/OFF) |
| | `packages/expansions/fan_pwm.yaml` | FanPWM (25 kHz PWM) |
| | `packages/expansions/fan_gp8403.yaml` | FanDAC (0–10 V) |
| | `packages/expansions/fan_triac.yaml` | FanTRIAC (AC dimmer) |
| **Features** | `packages/features/airiq_basic_profile.yaml` | AirIQ logic |
| | `packages/features/bathroom_profile.yaml` | VentIQ logic |
| | `packages/features/presence_basic_profile.yaml` | RoomIQ presence logic |
| | `packages/features/fan_control_profile.yaml` | Fan automation |

See [docs/product-matrix.md](docs/product-matrix.md) for the complete module
reference, and [docs/release-one.md](docs/release-one.md) for the Release-One
configuration in detail.

---

## Repository Structure

```
esphome-public/
├── products/           # Ready-to-use device configurations (start here)
├── packages/
│   ├── base/           # Core system (WiFi, API, OTA, logging)
│   ├── hardware/       # Core board, LED ring, power
│   ├── expansions/     # AirIQ / VentIQ / RoomIQ / Fan drivers
│   └── features/       # Feature profiles (logic, automations)
├── examples/           # Customer configuration templates
├── docs/               # Installation, product matrix, release notes
└── tests/              # Validation and testing infrastructure
```

---

## Documentation

- [WebFlash Compatibility Contract](docs/webflash-contract.md) — Artifact naming, config-string grammar, release-body format
- [Release-One Configuration](docs/release-one.md) — Ceiling-POE-VentIQ-FanTRIAC-RoomIQ
- [Product Matrix](docs/product-matrix.md) — Slot/module reference
- [Installation Guide](docs/installation.md) — Step-by-step setup
- [Configuration Reference](docs/configuration.md) — Customization options
- [Development Guide](docs/development.md) — Contributing and testing
- [Changelog](CHANGELOG.md) — Version history

---

## Legacy Terminology

Earlier versions of this repo used a different vocabulary. The mapping to the
current WebFlash taxonomy is:

| Legacy term | Current term | Notes |
|-------------|--------------|-------|
| Comfort | **RoomIQ** (climate + light half) | Folded into RoomIQ |
| Presence | **RoomIQ** (mmWave half) | Folded into RoomIQ |
| Bathroom | **VentIQ** | Same module, renamed |
| Fan (generic) | **FanRelay / FanPWM / FanDAC / FanTRIAC** | Split into firmware-distinct drivers |
| Mini / Wall variants | _Not in Release-One_ | Older form factors not part of release one |

Files under `packages/expansions/` still carry legacy filenames
(`comfort_*.yaml`, `airiq_bathroom_*.yaml`) for backwards compatibility — the
README, product YAML, and WebFlash taxonomy are the source of truth for naming
going forward.

---

## System Requirements

- **ESPHome:** 2025.10.0 or newer
- **Home Assistant:** 2024.1.0 or newer (recommended)

---

## Support

- **Documentation:** [docs/](docs/)
- **Issues:** [GitHub Issues](https://github.com/sense360store/esphome-public/issues)
- **Discussions:** [GitHub Discussions](https://github.com/sense360store/esphome-public/discussions)
- **Email:** support@mysense360.com
- **Purchase:** [mysense360.com](https://mysense360.com)

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

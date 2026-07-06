# Getting Started

How to get Sense360 firmware onto a device — the browser path most
customers use, and the manual / custom ESPHome path for advanced users.
This page was split out of the repository README front door; the full
documentation map is in the [documentation index](README.md).

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

## Quick Start (Custom / Manual Flash)

> Most customers should use [WebFlash](https://mysense360.com) instead.
> This section is for advanced users running the YAML directly through
> ESPHome.

### 1. Pick a product configuration

Find the YAML matching your hardware in [`products/`](../products/). For
Release-One that is:

```text
products/sense360-ceiling-poe-ventiq-roomiq.yaml
```

### 2. Configure secrets

Copy [`secrets.example.yaml`](../secrets.example.yaml) to `secrets.yaml` and
edit it with your real local credentials:

```bash
cp secrets.example.yaml secrets.yaml
```

```yaml
wifi_ssid: "YourNetworkName"
wifi_password: "YourWiFiPassword"
api_encryption_key: "GENERATE_WITH_ESPHOME_WIZARD"
ota_password: "your-secure-ota-password"
web_username: "admin"
web_password: "your-secure-web-password"
```

> `secrets.yaml` is gitignored — never commit it. CI generates its own
> placeholder secrets for validation/builds, so you do not need to commit
> anything for CI to pass.
>
> Generate an API key with `esphome wizard` or `openssl rand -base64 32`.

### 3. Reference the product from your device YAML

```yaml
packages:
  sense360_firmware:
    url: https://github.com/sense360store/esphome-public
    ref: v1.0.0  # Pin to a release tag — never use 'main' in production
    files:
      - products/sense360-ceiling-poe-ventiq-roomiq.yaml
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
      - products/sense360-ceiling-poe-ventiq-roomiq.yaml
    refresh: 1d
```

### Approach 2 — Individual packages

Compose your own product from base + board/expansion + feature packages. The
legacy `packages/hardware/*` and `packages/expansions/*` paths below still
resolve — for the flipped sensor/PSU families they are now thin `!include`
**aliases** of the SKU-aligned board package under `packages/boards/` (e.g.
`packages/expansions/comfort_ceiling.yaml` → `packages/boards/s360-200-roomiq-climate.yaml`,
`packages/expansions/airiq_ceiling.yaml` → `packages/boards/s360-210-airiq.yaml`,
`packages/hardware/power_poe.yaml` → `packages/boards/s360-410-poe-psu.yaml`).
You may reference either the legacy alias path or the board package directly;
both resolve identically. (The `S360-100` Core mount variants are the inverse
today — the board overlay wraps the still-authoritative legacy
`packages/hardware/sense360_core_*.yaml` path — until Core's source-of-truth
flip lands.) See the
[board / bundle / alias / shim layers](system-architecture.md#inside-esphome-public-board--bundle--alias--shim-layers).

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
      # FanTRIAC (packages/expansions/fan_triac.yaml +
      # packages/features/fan_control_profile.yaml) is intentionally
      # omitted from production Release-One while HW-005 is open. See
      # docs/release-one-hardware-audit.md#fantriac-mapping-resolution
      # (archived; see docs/archive-index.md)
      - packages/features/bathroom_profile.yaml
      - packages/features/presence_basic_profile.yaml
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

See [product-matrix.md](product-matrix.md) for the complete module
reference, and [release-one.md (archived)](archive-index.md) for the Release-One
configuration in detail.

## System Requirements

- **ESPHome:** 2025.10.0 or newer
- **Home Assistant:** 2024.1.0 or newer (recommended)

## See Also

- [Product taxonomy & compatibility rules](product-taxonomy.md) — config
  strings, modules, Release-One, build output contract.
- [Installation Guide](installation.md) — step-by-step setup.
- [Configuration Reference](configuration.md) — customization options.
- [Release channels](release-channels.md) — stable / preview / experimental
  and what support each receives.

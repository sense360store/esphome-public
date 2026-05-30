# Sense360 Module Documentation

> **Legacy / advanced module inventory — NOT the Release-One path.**
> Production Release-One ships the WebFlash configuration
> `Ceiling-POE-VentIQ-RoomIQ`, built from
> [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml)
> and published as `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`.
> The AirIQ ceiling module and the other modules documented here are
> retained for legacy / advanced / custom builds. They are not Release-One
> production targets. The legacy Sense360 Mini board range was removed from
> the active repository surface by PRODUCT-DEP-MINI-001 (superseded by the R4
> product line; not part of R4); its catalog rows survive only as `removed`
> tombstones and the tag-pinned `v1.0.0` release still carries the Mini files
> for existing field units. FanTRIAC is blocked pending
> HW-005; the Sense360 LED is excluded from Release-One because the config
> string has no `LED` token. For the Release-One source of truth see
> [`docs/release-one.md`](../docs/release-one.md). For canonical SKU /
> friendly-name mapping see [`docs/hardware-catalog.md`](../docs/hardware-catalog.md).

## Overview

The Sense360 platform is built on ESP32-S3-WROOM-1-N16R8 and supports modular expansion through I2C, UART, and GPIO interfaces.

---

## Board-package layer — SKU-aligned source of truth

> **The authoritative definition of each board now lives in
> `packages/boards/`.** The functional package names listed further down this
> document are, for the migrated families, **thin `!include` aliases** of a
> SKU-aligned board package. See
> [`docs/arch-board-bundle-plan.md`](../docs/arch-board-bundle-plan.md) for the
> full target shape and
> [`docs/system-architecture.md`](../docs/system-architecture.md#inside-esphome-public-board--bundle--alias--shim-layers)
> for how the layers fit the whole pipeline.

The board layer maps each catalog board SKU
([`config/hardware-catalog.json`](../config/hardware-catalog.json) /
[`docs/hardware-catalog.md`](../docs/hardware-catalog.md)) to one canonical,
self-contained package that owns the board's chip / pin map / connector nets:

| Board SKU | Friendly name | Authoritative board package | Legacy alias paths (preserved) |
|-----------|---------------|-----------------------------|--------------------------------|
| `S360-100` | Sense360 Core | `packages/boards/s360-100-core.yaml` (+ mount/power/voice overlays) | `hardware/sense360_core*.yaml` |
| `S360-200` | Sense360 RoomIQ | `packages/boards/s360-200-roomiq.yaml` (authoritative **per driver**: `…-climate.yaml` + `…-radar.yaml`, ceiling & wall) | `expansions/comfort_ceiling.yaml`, `comfort_wall.yaml`, `presence_ceiling.yaml`, `presence_wall.yaml` |
| `S360-210` | Sense360 AirIQ | `packages/boards/s360-210-airiq.yaml` (+ `-wall`, `-ceiling-s3`) | `expansions/airiq_ceiling.yaml`, `airiq_wall.yaml`, `airiq_ceiling_s3.yaml` |
| `S360-211` | Sense360 VentIQ | `packages/boards/s360-211-ventiq.yaml` (+ `-pro`) | `expansions/airiq_bathroom_base.yaml`, `airiq_bathroom_pro.yaml`, `bathroom.yaml` |
| `S360-300` | Sense360 LED | `packages/boards/s360-300-led.yaml` (+ mic/voice variant) | `hardware/led_ring_ceiling.yaml`, `led_ring_wall.yaml`, `led_ring_mic_*.yaml` |
| `S360-410` | Sense360 PoE PSU | `packages/boards/s360-410-poe-psu.yaml` | `hardware/power_poe.yaml` |

**Core flip is still pending.** For `S360-200` / `S360-210` / `S360-211` /
`S360-300` / `S360-410` the board package is authoritative and the legacy paths
are the aliases. For `S360-100` Core the base chip/bus lives authoritatively in
`s360-100-core.yaml`, but the **mount-variant overlays still wrap the legacy
`hardware/sense360_core_*.yaml` path** (the overlay `!include`s the legacy file
— the inverse direction); the legacy Core mount path stays the source of truth
until Core's flip lands in a later slice.

**Alias-retention policy (`docs/arch-board-bundle-plan.md` §3.3).** When a board
package becomes authoritative, the legacy functional path is **retained as a
thin alias** (a one-line `!include` of the board package) so every product and
test that binds the legacy path resolves byte-identically. **No alias is
dropped while a live binder exists**; alias removal is a separate, later slice
gated on the binder count reaching zero (via `PRODUCT-DEP-CORE-001`).

**Authoritative-by-composition vs 1:1.** The `S360-200` RoomIQ family is
authoritative **per driver** — its climate and radar halves live in separate
board packages because the legacy `comfort_*`/`presence_*` paths bind them
under separate package keys, so a single merged file cannot alias both without
duplicate-id breakage. The `S360-300` LED, `S360-210` AirIQ, `S360-211` VentIQ,
and `S360-410` PoE-PSU families are **1:1** — the whole driver folds into one
board file.

**Cross-referenced base drivers stay authoritative (NOT aliased).** The generic
air-quality base driver `airiq.yaml`, the shared radar primitives
`presence_ld2450.yaml` / `presence_ld2412.yaml`, and the feature-tier
`ceiling_halo_leds.yaml` have no board package holding their content; they
remain authoritative and un-folded, cross-referenced from the board layer.

**Not yet promoted.** The mains-voltage driver boards (`S360-310` Relay,
`S360-320` TRIAC, `S360-400` 240V PSU) and the SELV fan-driver SKUs (`S360-311`
PWM, `S360-312` DAC) remain **expansion packages** behind their own evidence /
compliance gates; they are not in the board layer yet.

---

## Sense360 Mini Board (removed)

The legacy Sense360 Mini board range was **removed** from the active
repository surface by **PRODUCT-DEP-MINI-001**. It was a pre-WebFlash,
`legacy-compatible` range that was never WebFlash-shippable and is not part
of the R4 product line. The 10 Mini product YAMLs and the Mini-only packages
(`sense360_core_mini.yaml`, `mini_onboard_sensors.yaml`,
`mini_four_leds_air_quality.yaml`, `mini_four_leds_addr.yaml`) have been
deleted; the catalog rows survive only as `removed` tombstones that reserve
their `legacy_config_id` strings.

Existing Mini field units remain served by the tag-pinned `v1.0.0` release,
which still contains the Mini files. There is no R4 replacement for the Mini
form factor. See
[`docs/product-deprecation-removal-policy.md`](../docs/product-deprecation-removal-policy.md)
(PRODUCT-DEP-001) for the lifecycle policy.

---

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

**For Presence Module (S360-PRES-C, S360-PRES-W):**

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

**Legacy radar alternative:**

**HLK-LD2450** (presence_ld2450.yaml) - Multi-target radar (see above)

**HLK-LD2412** (presence_ld2412.yaml) - Single-zone radar
- UART: 115200 baud
- Power: 5V/100mA
- Better still detection, up to 9m
- Was the radar used by the now-removed Mini range; the package is retained
  for legacy / advanced custom builds.

```yaml
# For Presence Module (LD2450 default)
packages:
  presence: !include packages/expansions/presence_ld2450.yaml

# For Presence Module (C4001 alternative)
packages:
  presence: !include packages/hardware/presence_dfrobot_c4001.yaml

# LD2412 single-zone radar alternative (legacy)
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

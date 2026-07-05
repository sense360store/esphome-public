# Product Taxonomy & Compatibility

The WebFlash config-string taxonomy, the sensor / driver modules behind each
slot, the compatibility rules, and the build output contract. This page was
split out of the repository README front door; the authoritative cross-repo
contract text is [`webflash-contract.md`](webflash-contract.md) and the
machine-readable declarations live under [`config/`](../config/).

## Release-One Configuration

The **Release-One** shipping configuration is:

```text
Ceiling-POE-VentIQ-RoomIQ
```

| Slot | Value | Meaning |
|------|-------|---------|
| Mount | `Ceiling` | Flush ceiling-mount Core board |
| Power | `POE` | IEEE 802.3af Power-over-Ethernet |
| Air Quality | `VentIQ` | Vent/bathroom-focused air-quality module |
| Room Sense | `RoomIQ` | Comfort + presence sensing |

The matching ESPHome product YAML is
[`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml).

The matching firmware artifact published by CI is:

```text
Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin
```

> **FanTRIAC excluded from production Release-One** while HW-005 is open.
> The Sense360 TRIAC (`S360-320`) slot is blocked because the schematic is
> not committed, the placeholder GPIO5/GPIO6 substitutions collide with
> RoomIQ J10 nets, and ESPHome's `ac_dimmer` requires direct
> interrupt-capable ESP32 GPIOs that the SX1509 expander cannot provide.
> The FanTRIAC product YAML
> ([`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml))
> remains in the repo as a blocked / reference file but is NOT in the
> WebFlash build matrix. See
> [`docs/release-one-hardware-audit.md#fantriac-mapping-resolution` (archived)](archive-index.md).

See [Build Output Contract](#build-output-contract) below.

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
[`products/`](../products/) and a published `.bin` asset on the matching GitHub Release.

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

## Mount and Power

| Slot | Value | Notes |
|------|-------|-------|
| Mount | `Ceiling` | Release-one ships ceiling mount only |
| Power | `USB` | 5 V USB-C, dev/portable |
| Power | `POE` | IEEE 802.3af, single-cable installs |
| Power | `PWR` | 100–240 V AC mains (HLK-PM01) |

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

## Build Output Contract

CI in this repo publishes WebFlash-compatible `.bin` assets named:

```text
Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin
```

Where:

| Field | Source | Example |
|-------|--------|---------|
| `CONFIG_STRING` | WebFlash slot chain | `Ceiling-POE-VentIQ-RoomIQ` |
| `VERSION` | Release tag (`v` stripped) | `1.0.0` |
| `CHANNEL` | `stable`, `preview`, or `beta` | `stable` |

Example for Release-One:

```text
Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin
```

The mapping from product YAML → WebFlash filename is implemented in
[`scripts/product_name_mapper.py`](../scripts/product_name_mapper.py) and exercised
by [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml).

The same mapping is published as machine-readable JSON in
[`config/webflash-builds.json`](../config/webflash-builds.json), validated against
the contract snapshot at
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json) by
[`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py).

> **Signing:** This repo does **not** sign firmware. WebFlash remains the
> production signing/deployment authority and consumes the unsigned `.bin`
> assets attached to GitHub releases.

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
product YAML, WebFlash taxonomy, and this document are the source of truth for
naming going forward.

## See Also

- [WebFlash Compatibility Contract](webflash-contract.md) — artifact naming,
  config-string grammar, release-body format (authoritative contract text).
- [Product Matrix](product-matrix.md) — complete slot/module reference.
- [Hardware Catalog](hardware-catalog.md) — canonical board names, SKUs,
  revisions, legacy names.
- [Getting Started](getting-started.md) — flash or adopt the firmware.

# Release-One Configuration

This page is the source of truth for the **Release-One** Sense360 shipping
configuration. It pins the WebFlash config string, the product YAML, and the
firmware artifact name together so that all three stay aligned.

---

## Config String

```text
Ceiling-POE-VentIQ-FanTRIAC-RoomIQ
```

| Slot | Value | Meaning |
|------|-------|---------|
| Mount | `Ceiling` | Flush ceiling-mount Core board |
| Power | `POE` | IEEE 802.3af Power-over-Ethernet |
| Air Quality | `VentIQ` | Vent/bathroom-focused air-quality module |
| Fan Driver | `FanTRIAC` | TRIAC-based AC fan dimming |
| Room Sense | `RoomIQ` | Comfort + presence sensing |

## Files

| Asset | Path |
|-------|------|
| Product YAML | [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml) |
| Air Quality (VentIQ) | [`packages/expansions/airiq_bathroom_base.yaml`](../packages/expansions/airiq_bathroom_base.yaml) |
| RoomIQ Comfort | [`packages/expansions/comfort_ceiling.yaml`](../packages/expansions/comfort_ceiling.yaml) |
| RoomIQ Presence | [`packages/expansions/presence_ceiling.yaml`](../packages/expansions/presence_ceiling.yaml) |
| FanTRIAC Driver | [`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml) |
| Power (POE) | [`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml) |
| Core Hardware | [`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml) |

## Firmware Artifact

CI publishes this as a release asset on the matching GitHub release:

```text
Sense360-Ceiling-POE-VentIQ-FanTRIAC-RoomIQ-v1.0.0-stable.bin
```

The mapping from product YAML → WebFlash filename is implemented in
[`scripts/product_name_mapper.py`](../scripts/product_name_mapper.py) and
exercised by
[`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml).

---

## Compatibility Rules

These rules apply to every WebFlash config string and every product YAML:

1. **`AirIQ` and `VentIQ` are mutually exclusive.** A device runs one or the
   other, never both. They share the I2C bus and overlap in sensors.
2. **`VentIQ` is the bathroom-focused air-quality module.** Use it for
   bathroom, laundry, or shower environments. It carries shower detection,
   mold-risk tracking, and odor detection.
3. **`RoomIQ` can be combined with either `AirIQ` or `VentIQ`.** RoomIQ
   carries comfort (temperature, humidity, light) and presence (mmWave radar)
   sensing. It is independent of the air-quality slot.
4. **Fan driver variants are firmware-distinct.** `FanRelay`, `FanPWM`,
   `FanDAC`, and `FanTRIAC` each produce a separate firmware binary. The
   GPIO routing and driver code differ between them.
5. **`FanTRIAC` is not interchangeable with `FanRelay`, `FanPWM`, or
   `FanDAC`.** Flashing the wrong fan driver will not control the load
   correctly and may damage the fan or wiring. Always pick the driver that
   matches the physical hardware.

### Allowed combinations

| Air Quality | Room | Fan | Allowed? |
|-------------|------|-----|----------|
| AirIQ | RoomIQ | FanRelay / FanPWM / FanDAC / FanTRIAC | Yes |
| VentIQ | RoomIQ | FanRelay / FanPWM / FanDAC / FanTRIAC | Yes |
| AirIQ + VentIQ | (any) | (any) | **No** — mutually exclusive |
| Two fan drivers | (any) | (any) | **No** — pick one |

---

## Build Output Contract

CI in this repo publishes WebFlash-compatible `.bin` assets named:

```text
Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin
```

| Field | Source | Example |
|-------|--------|---------|
| `CONFIG_STRING` | WebFlash slot chain | `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` |
| `VERSION` | Release tag (`v` stripped) | `1.0.0` |
| `CHANNEL` | `stable`, `preview`, `beta` | `stable` |

### Release body

The GitHub Release body should include the following sections so WebFlash
can build a `.meta.json` sidecar from a Release programmatically:

- **Changelog** — what changed in this release
- **Known Issues** — caveats / open bugs the user should know
- **Features** — what this release-one binary actually does
- **Hardware Requirements** — required core/power/expansion modules

> **Signing:** This repo does **not** sign firmware. WebFlash remains the
> production signing/deployment authority and consumes the unsigned `.bin`
> assets attached to GitHub releases.

---

## Customer Usage (manual / custom path)

> Most customers should use [WebFlash](https://mysense360.com) instead.

Pin to a release tag (never `main`) when referencing the product YAML:

```yaml
packages:
  sense360_firmware:
    url: https://github.com/sense360store/esphome-public
    ref: v1.0.0
    files:
      - products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml
    refresh: 1d

substitutions:
  device_name: sense360-bathroom
  friendly_name: "Bathroom Sense360"
```

The product file already wires up `wifi:`, `api:`, `ota:`, time, logging, the
LED ring, VentIQ, RoomIQ, and FanTRIAC — only `device_name` and
`friendly_name` need to be overridden in your device YAML.

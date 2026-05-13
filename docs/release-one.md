# Release-One Configuration

This page is the source of truth for the **Release-One** Sense360 shipping
configuration. It pins the WebFlash config string, the product YAML, and the
firmware artifact name together so that all three stay aligned.

> **Production Release-One excludes Sense360 TRIAC.** The FanTRIAC slot is
> blocked per HW-005 — the `S360-320` schematic is not committed, the
> `TRI_GPIO1` / `TRI_GPIO2` routing is not verified, the placeholder GPIO5
> / GPIO6 substitutions collide with RoomIQ J10 nets, and ESPHome's
> `ac_dimmer` driver requires direct interrupt-capable ESP32 GPIOs that
> SX1509 expander channels cannot provide. The production Release-One
> binary therefore ships **without** a fan driver until the blocker is
> resolved. FanTRIAC remains cataloged and planned, but is not part of the
> production Release-One artifact. See
> [`release-one-hardware-audit.md#fantriac-mapping-resolution`](release-one-hardware-audit.md#fantriac-mapping-resolution)
> for the full hardware audit and ship verdict.

---

## Config String

```text
Ceiling-POE-VentIQ-RoomIQ
```

| Slot | Value | Meaning |
|------|-------|---------|
| Mount | `Ceiling` | Flush ceiling-mount Core board |
| Power | `POE` | IEEE 802.3af Power-over-Ethernet |
| Air Quality | `VentIQ` | Vent/bathroom-focused air-quality module |
| Room Sense | `RoomIQ` | Comfort + presence sensing |

The Fan Driver slot is intentionally empty. A future production build that
includes FanTRIAC would use a distinct config string such as
`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` and a distinct artifact name; that
build is not part of production Release-One while HW-005 is open.

## Files

| Asset | Path |
|-------|------|
| Product YAML | [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml) |
| WebFlash wrapper | [`products/webflash/ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml) |
| Air Quality (VentIQ) | [`packages/expansions/airiq_bathroom_base.yaml`](../packages/expansions/airiq_bathroom_base.yaml) |
| RoomIQ Comfort | [`packages/expansions/comfort_ceiling.yaml`](../packages/expansions/comfort_ceiling.yaml) |
| RoomIQ Presence | [`packages/expansions/presence_ceiling.yaml`](../packages/expansions/presence_ceiling.yaml) |
| Power (POE) | [`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml) |
| Core Hardware | [`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml) |
| Product status catalog | [`config/product-catalog.json`](../config/product-catalog.json) |

The Release-One product status (lifecycle, modules, blocked modules, hardware
SKUs) is also recorded in [`config/product-catalog.json`](../config/product-catalog.json),
the repo's product source-of-truth catalog.
[`config/webflash-builds.json`](../config/webflash-builds.json) remains the
authoritative WebFlash build matrix; the catalog adds the lifecycle layer on
top and is validated by [`tests/test_product_catalog.py`](../tests/test_product_catalog.py).

PRODUCT-002 extended the catalog to enumerate every legacy / manual product
YAML under `products/` as `status: legacy-compatible`. Release-One remains
the only `production` entry and `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` remains
`blocked` (HW-005). `legacy-compatible` entries are not WebFlash-shippable —
they have no `config_string`, no `artifact_name`, no `webflash_wrapper`, and
`webflash_build_matrix` is `false`. The Release-One product, artifact, and
WebFlash build matrix are unchanged by PRODUCT-002.

PRODUCT-003 adds a read-only catalog consistency validator at
[`scripts/validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py)
(unit-tested by
[`tests/test_product_catalog_consistency.py`](../tests/test_product_catalog_consistency.py))
that cross-checks the catalog against the WebFlash build matrix, the
WebFlash compatibility snapshot, the hardware catalog, and the artifact
mapper, and also exposes a `--checklist` mode for adding future product
configs. The Release-One product, artifact, build matrix, and FanTRIAC /
LED policy are unchanged by PRODUCT-003.

RELEASE-001 adds a read-only release-notes draft generator at
[`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py)
(unit-tested by
[`tests/test_generate_webflash_release_notes.py`](../tests/test_generate_webflash_release_notes.py))
that produces a Markdown draft body for a catalog product/version/channel
matching the format enforced by
[`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py).
The generator sources lifecycle and SKU data from
[`config/product-catalog.json`](../config/product-catalog.json), the
human-readable feature bullets from
[`config/webflash-builds.json`](../config/webflash-builds.json), and
friendly hardware names from
[`config/hardware-catalog.json`](../config/hardware-catalog.json). It
refuses blocked, legacy-compatible, deprecated, and removed entries; it
refuses preview entries on the stable channel; and it always emits
FanTRIAC and Sense360 LED as Known-Issues exclusions, never as Features.
The `## Changelog` section remains a TODO placeholder that requires
human review and replacement before a release is tagged. The generator
does not create releases, publish firmware, infer changelog content from
git history, or call any external service. The Release-One product,
artifact, build matrix, and FanTRIAC / LED policy are unchanged by
RELEASE-001.

The Release-One YAML omits the Sense360 LED (`S360-300`) packages on
purpose: the WebFlash config string `Ceiling-POE-VentIQ-RoomIQ` does not
carry a `LED` token, so the binary built from this YAML does not include
LED firmware. See
[`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md) for
the audit decision, the FanTRIAC pin-mapping blocker, the VentIQ
schematic-pending caveat, and the full hardware-vs-firmware findings table.

### Blocked / reference files (not in production Release-One)

The FanTRIAC product YAML and wrapper are kept in the repo so the slot can
be re-enabled when HW-005 is resolved, but they are NOT in the WebFlash
build matrix at [`config/webflash-builds.json`](../config/webflash-builds.json):

| Asset | Path | Status |
|-------|------|--------|
| FanTRIAC product YAML | [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml) | Blocked / reference |
| FanTRIAC WebFlash wrapper | [`products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml) | Blocked / reference |
| FanTRIAC driver package | [`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml) | Blocked / reference |
| Fan control profile | [`packages/features/fan_control_profile.yaml`](../packages/features/fan_control_profile.yaml) | Blocked / reference |

## Firmware Artifact

CI publishes this as a release asset on the matching GitHub release:

```text
Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin
```

The mapping from product YAML → WebFlash filename is implemented in
[`scripts/product_name_mapper.py`](../scripts/product_name_mapper.py) and
exercised by
[`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml).

### Proof of build (recorded)

Per-PR static proof (mapper agrees with `config/webflash-builds.json`) is
covered by
[`tests/test_webflash_artifact_naming.py`](../tests/test_webflash_artifact_naming.py),
and a build-time assertion against the declared `artifact_name` is wired
into the build job via
[`tests/check_webflash_build_output.py`](../tests/check_webflash_build_output.py).

A recorded end-to-end CI run is now in hand. ESP-006 and ESP-007 are
**proven** for Release-One:

| Field | Value |
|-------|-------|
| WebFlash config | `Ceiling-POE-VentIQ-RoomIQ` |
| GitHub Release | [`v1.0.0`](https://github.com/sense360store/esphome-public/releases/tag/v1.0.0) |
| Asset name | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` |
| Actions run | <https://github.com/sense360store/esphome-public/actions/runs/25763009641> |
| Workflow event | `release` |
| Status | ESP-006 and ESP-007 proven for raw build + GitHub Release publish |

Sense360 TRIAC / FanTRIAC remains excluded from production Release-One and
**blocked pending hardware verification** under HW-005 — see
[`release-one-hardware-audit.md#fantriac-mapping-resolution`](release-one-hardware-audit.md#fantriac-mapping-resolution).
Sense360 LED remains excluded because the WebFlash config string
`Ceiling-POE-VentIQ-RoomIQ` does not include a `LED` token.

WebFlash production signing, the WebFlash production-signed
`manifest.json`, and WebFlash deploy remain WebFlash-owned and are not
claimed by this record. See
[`docs/webflash-release-proof.md`](webflash-release-proof.md) and
[`docs/webflash-ci-alignment.md`](webflash-ci-alignment.md#proof-record)
for the full proof record.

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
| VentIQ | RoomIQ | (no fan) | Yes — production Release-One |
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
| `CONFIG_STRING` | WebFlash slot chain | `Ceiling-POE-VentIQ-RoomIQ` |
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
      - products/sense360-ceiling-poe-ventiq-roomiq.yaml
    refresh: 1d

substitutions:
  device_name: sense360-bathroom
  friendly_name: "Bathroom Sense360"
```

The product file already wires up `wifi:`, `api:`, `ota:`, time, logging,
VentIQ, and RoomIQ — only `device_name` and `friendly_name` need to be
overridden in your device YAML. Sense360 LED (`S360-300`) is not bundled
into this product (see the Files table above), and FanTRIAC is intentionally
not included while HW-005 is open.

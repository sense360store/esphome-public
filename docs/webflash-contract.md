# WebFlash Compatibility Contract

This document is the **repo-local compatibility contract** between
[`sense360store/esphome-public`](https://github.com/sense360store/esphome-public)
(this repo, the ESPHome source / firmware build repo) and
[`sense360store/WebFlash`](https://github.com/sense360store/WebFlash) (the
browser-based flasher and the source of truth for product naming, firmware
config strings, and release artifact names).

**WebFlash is the authority** for:

- Product taxonomy (mounting, power, modules).
- Firmware config-string grammar.
- Release artifact filename grammar.
- Signing and deployment of customer-facing firmware.

This repo's job is to publish unsigned `.bin` artifacts and a GitHub Release
body that WebFlash's release importer (`scripts/sync-from-releases.py`) can
ingest without manual intervention.

This document defines what "compatible with WebFlash" means in practice. If
this contract and WebFlash's `DEVELOPER.md` ever drift, **WebFlash wins** and
this document must be updated.

This repository keeps a local compatibility snapshot in
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
so validators and CI in this repo can enforce the same naming rules without
fetching WebFlash. WebFlash remains the upstream source of truth; when
WebFlash product naming changes, update this snapshot, the validators, and
the build matrix together in the same PR.

---

## 1. WebFlash Artifact Naming

Every firmware `.bin` published from this repo as a GitHub Release asset must
match this exact shape:

```text
Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin
```

| Field | Source | Example |
|-------|--------|---------|
| `Sense360-` | Literal prefix | `Sense360-` |
| `CONFIG_STRING` | WebFlash config-string grammar (see §2) | `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` |
| `VERSION` | Release tag with the leading `v` stripped | `1.0.0` |
| `CHANNEL` | `stable`, `preview`, or `beta` | `stable` |

Rules:

- Filenames are case-sensitive — token capitalization must match §3 exactly.
- Versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
- `stable` is the only customer-default channel; `preview` and `beta` are
  user-opt-in in WebFlash and require an extra acknowledgement.
- Never overwrite a previously published `.bin` in place — WebFlash caches
  binaries under `Cache-Control: max-age=31536000`. New builds get a new
  filename via a new version bump.

---

## 2. Canonical Config-String Grammar

```text
{Mounting}-{Power}-{Modules...}
```

- Exactly **one** `Mounting` segment.
- Exactly **one** `Power` segment.
- Zero or more `Modules` segments, joined with `-`.
- Module order within a config string is fixed by §5 below — do not reorder.
- Tokens are joined with a single `-`. There are no spaces, no underscores,
  and no abbreviations beyond those listed in §3.

Examples:

```text
Ceiling-POE-VentIQ-FanTRIAC-RoomIQ
Ceiling-USB-AirIQ
Ceiling-PWR-VentIQ-FanRelay-RoomIQ-LED
```

The wizard frontend in WebFlash parses these strings via
`parseConfigStringState` in `scripts/state.js`; the publishing pipeline emits
them via `scripts/gen-manifests.py` from the canonical filename. They must
match each other byte-for-byte.

---

## 3. Allowed Tokens

### Mounting

| Token | Meaning |
|-------|---------|
| `Ceiling` | Flush ceiling-mount Sense360 Core board (`S360-100`) |

> Release-One supports `Ceiling` only. A legacy `Wall` mount is referenced in
> some WebFlash code paths but is **not** an active product and must not be
> used in artifact names.

### Power

| Token | WebFlash SKU | Meaning |
|-------|--------------|---------|
| `USB`  | — | USB-C power direct to the Core (dev/portable) |
| `POE`  | `S360-410` | Sense360 PoE PSU, IEEE 802.3af |
| `PWR`  | `S360-400` | Sense360 240V PSU (HLK-5M05 mains-to-5V) |

### Modules

| Token | WebFlash SKU | Meaning |
|-------|--------------|---------|
| `AirIQ` | `S360-210` | General air-quality module (CO₂, VOC, gas, optional PM/HCHO) |
| `VentIQ` | `S360-211` | Bathroom-focused air-quality module (SGP41 + IR-temp + PM connectors) |
| `RoomIQ` | `S360-200` | Room sensor (PIR, LD2450, light, temperature, humidity, pressure) |
| `FanRelay` | `S360-310` | On/off relay fan driver |
| `FanPWM` | `S360-311` | 12 V PWM fan driver (up to 4 fans, tach feedback) |
| `FanDAC` | `S360-312` | 0–10 V analog (DAC) fan driver |
| `FanTRIAC` | `S360-320` | Phase-cut TRIAC mains-fan dimmer |
| `LED` | `S360-300` | WS2812B addressable LED ring |

### Deprecated / forbidden tokens

These tokens **must not** appear in any new artifact filename, GitHub Release
asset, or `config_string` value published from this repo:

| Forbidden | Use instead |
|-----------|-------------|
| `Bathroom` | `VentIQ` (the bathroom-focused module) |
| `Comfort` | `RoomIQ` (climate + light half) |
| `Presence` | `RoomIQ` (mmWave half) |
| `Fan` (generic, no variant suffix) | `FanRelay` / `FanPWM` / `FanDAC` / `FanTRIAC` |
| `BathroomAirIQ` (and `Base` / `Pro` suffixes) | `VentIQ` |
| `AirIQBase` | `AirIQ` |
| `AirIQPro`, `AirIQProv` | `AirIQ` |
| `FanAnalog` | `FanDAC` |

WebFlash's `scripts/validate-naming-policy.js` actively rejects these tokens
in new files. They are recognized as read-time aliases for backwards
compatibility only.

---

## 4. Release-One Required Config

The Release-One shipping configuration is:

```text
Ceiling-POE-VentIQ-FanTRIAC-RoomIQ
```

| Slot | Value | Meaning |
|------|-------|---------|
| Mounting | `Ceiling` | Ceiling-mount Sense360 Core |
| Power | `POE` | Sense360 PoE PSU (`S360-410`) |
| Air Quality | `VentIQ` | Sense360 VentIQ (`S360-211`), bathroom-focused |
| Fan Driver | `FanTRIAC` | Sense360 TRIAC (`S360-320`), AC phase-cut |
| Room Sense | `RoomIQ` | Sense360 RoomIQ (`S360-200`), comfort + presence |

The required release artifact is:

```text
Sense360-Ceiling-POE-VentIQ-FanTRIAC-RoomIQ-v1.0.0-stable.bin
```

The matching ESPHome product YAML is
[`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml).

See [`release-one.md`](release-one.md) for the full slot/file/binary mapping.

---

## 5. Compatibility Rules

These rules apply to every WebFlash config string and every product YAML
published from this repo. They mirror the rules enforced in WebFlash's
`scripts/data/module-requirements.js` and `scripts/state.js`.

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
   GPIO routing and driver code differ between them. **Do not collapse fan
   variants to a generic `Fan` token.**
5. **`FanTRIAC` is not interchangeable with `FanRelay`, `FanPWM`, or
   `FanDAC`.** Flashing the wrong fan driver will not control the load
   correctly and may damage the fan or wiring. Always pick the driver that
   matches the physical hardware.
6. **`FanDAC` conflicts with `AirIQ`.** Both contend for the shared DAC bus
   in WebFlash's module-requirements matrix. Do not publish a config string
   that contains both.
7. **Module order in a config string is fixed.** Use this order so the same
   physical configuration always produces the same `config_string`:

   ```text
   {Mounting}-{Power}-[AirIQ|VentIQ]-[FanRelay|FanPWM|FanDAC|FanTRIAC]-[RoomIQ]-[LED]
   ```

   Skip slots that do not apply; do not insert placeholders.

### Allowed combinations (Release-One scope)

| Air Quality | Room | Fan | Allowed? |
|-------------|------|-----|----------|
| AirIQ | RoomIQ | FanRelay / FanPWM / FanTRIAC | Yes |
| AirIQ | RoomIQ | FanDAC | **No** — DAC bus conflict |
| VentIQ | RoomIQ | FanRelay / FanPWM / FanDAC / FanTRIAC | Yes |
| AirIQ + VentIQ | (any) | (any) | **No** — mutually exclusive |
| Two fan drivers | (any) | (any) | **No** — pick one |

---

## 6. Mapping: WebFlash Config Strings → ESPHome Product YAML

Every `config_string` WebFlash advertises must be reachable from a product
YAML in this repo. The Release-One mapping is:

| WebFlash `config_string` | ESPHome product YAML |
|--------------------------|----------------------|
| `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` | [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml) |

The Release-One product YAML is composed from these package files (also
documented in [`release-one.md`](release-one.md)):

| Slot | Package |
|------|---------|
| Core (mount) | [`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml) |
| Power (POE) | [`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml) |
| Air Quality (VentIQ) | [`packages/expansions/airiq_bathroom_base.yaml`](../packages/expansions/airiq_bathroom_base.yaml) |
| Room Sense (RoomIQ comfort) | [`packages/expansions/comfort_ceiling.yaml`](../packages/expansions/comfort_ceiling.yaml) |
| Room Sense (RoomIQ presence) | [`packages/expansions/presence_ceiling.yaml`](../packages/expansions/presence_ceiling.yaml) |
| Fan Driver (FanTRIAC) | [`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml) |

> Package filenames under `packages/expansions/` retain legacy names
> (`airiq_bathroom_*`, `comfort_*`, `presence_*`) for backwards compatibility
> with existing customer references. The WebFlash taxonomy in §3 is the
> source of truth for **artifact names**, not for filesystem paths.

When a new WebFlash `config_string` is added to a release, this table must be
updated in the same PR.

---

## 7. Build Output Expectations

### What this repo produces

- Unsigned `.bin` files attached to a GitHub Release as assets.
- Release asset filename matches §1 exactly.
- A GitHub Release body matching §8 below.

### What this repo does NOT do

- **Sign firmware.** WebFlash is the production signing authority and ingests
  unsigned `.bin` assets attached to GitHub Releases.
- **Host firmware for end users.** WebFlash hosts the customer-facing
  catalog; this repo only publishes assets and metadata.
- **Generate `manifest.json` / `firmware-N.json`.** Those files are generated
  by WebFlash's `scripts/gen-manifests.py` from the binaries it pulls in via
  `scripts/sync-from-releases.py`.

### Pipeline references

- The mapping from product YAML → WebFlash filename lives in
  [`scripts/product_name_mapper.py`](../scripts/product_name_mapper.py).
- The build/release pipeline is
  [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml).

This PR does **not** modify either; it only documents what they must produce.

---

## 8. Release Body Expectations (WebFlash Metadata Import)

WebFlash's release importer (`scripts/sync-from-releases.py`) parses the
GitHub Release body into the sidecar metadata it stores alongside each `.bin`.
The body **must** contain these four sections, with these exact headings, in
this order:

```markdown
## Changelog

- Human-authored release note.

## Known Issues

- None.

## Features

- Feature item.

## Hardware Requirements

- Hardware requirement item.
```

Rules:

- All four headings must appear at H2 level (`##`).
- Each section must be a Markdown bullet list (use `-`), even if it has only
  one item.
- The `## Changelog` section must be **human-authored**. Generic filler
  (`Initial release`, `First release`, `Firmware release`,
  `See release notes`, `TBD`, `TODO`, `N/A`, `Placeholder`, `No changes`,
  `Nothing to report`) is rejected by WebFlash for `stable` builds and will
  fail the release importer.
- `## Known Issues` may be `- None.` if there are no open issues.
- `## Features` describes what the firmware actually does (not what changed).
- `## Hardware Requirements` lists every WebFlash SKU the firmware expects.

### Release-One example release body

```markdown
## Changelog

- Initial production stable release for Ceiling-POE-VentIQ-FanTRIAC-RoomIQ
  with PoE power, VentIQ bathroom air-quality sensing, TRIAC fan switching,
  and RoomIQ room sensing.

## Known Issues

- None.

## Features

- PoE-powered Sense360 Core configuration
- VentIQ bathroom air-quality sensing
- TRIAC fan switching
- RoomIQ room sensing

## Hardware Requirements

- Sense360 Core R4 or newer
- Sense360 PoE PSU
- Sense360 VentIQ module
- Sense360 TRIAC board
- Sense360 RoomIQ module
```

WebFlash will produce a sidecar (`*.meta.json`) from this body with the
shape documented in WebFlash's `DEVELOPER.md → Via GitHub Releases`. This
repo never authors the sidecar directly.

---

## Compatibility Rule of Thumb

If you are tempted to invent a token, rename a slot, omit a section, or skip
a heading: **don't.** Either match WebFlash's existing taxonomy verbatim or
file an upstream change in WebFlash first and update this contract afterward.

## See Also

- [`README.md`](../README.md) — repo overview and Release-One quick reference.
- [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  — machine-readable local snapshot of this contract for validators and CI.
- [`docs/release-one.md`](release-one.md) — Release-One configuration with full
  slot/file/binary mapping.
- [`docs/product-matrix.md`](product-matrix.md) — full module/slot reference.
- WebFlash `DEVELOPER.md → Via GitHub Releases` — upstream operator flow.
- WebFlash `CLAUDE.md` — canonical SKU table and product taxonomy.

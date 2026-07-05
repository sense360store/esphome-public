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
| `CONFIG_STRING` | WebFlash config-string grammar (see §2) | `Ceiling-POE-VentIQ-RoomIQ` |
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
Ceiling-POE-VentIQ-RoomIQ
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
Ceiling-POE-VentIQ-RoomIQ
```

| Slot | Value | Meaning |
|------|-------|---------|
| Mounting | `Ceiling` | Ceiling-mount Sense360 Core |
| Power | `POE` | Sense360 PoE PSU (`S360-410`) |
| Air Quality | `VentIQ` | Sense360 VentIQ (`S360-211`), bathroom-focused |
| Room Sense | `RoomIQ` | Sense360 RoomIQ (`S360-200`), comfort + presence |

The required release artifact is:

```text
Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin
```

The matching ESPHome product YAML is
[`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml).

> **FanTRIAC excluded from production Release-One.** The Sense360 TRIAC
> (`S360-320`) slot is blocked per HW-005 (see
> [`docs/release-one-hardware-audit.md#fantriac-mapping-resolution` (archived)](archive-index.md)).
> The FanTRIAC token remains a valid WebFlash module (see §3) for future
> use, and the FanTRIAC product YAML
> ([`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml))
> is retained as a blocked / reference file, but it is NOT in
> [`config/webflash-builds.json`](../config/webflash-builds.json) and must
> not be published as a production Release-One artifact while HW-005 is
> open.

See [`release-one.md` (archived)](archive-index.md) for the full slot/file/binary mapping.

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
| VentIQ | RoomIQ | (no fan) | Yes — production Release-One |
| AirIQ + VentIQ | (any) | (any) | **No** — mutually exclusive |
| Two fan drivers | (any) | (any) | **No** — pick one |

---

## 6. Mapping: WebFlash Config Strings → ESPHome Product YAML

Every `config_string` WebFlash advertises must be reachable from a product
YAML in this repo. The Release-One mapping is:

| WebFlash `config_string` | ESPHome product YAML |
|--------------------------|----------------------|
| `Ceiling-POE-VentIQ-RoomIQ` | [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml) |

The Release-One product YAML is composed from these package files (also
documented in [`release-one.md` (archived)](archive-index.md)):

| Slot | Package |
|------|---------|
| Core (mount) | [`packages/hardware/sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml) |
| Power (POE) | [`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml) |
| Air Quality (VentIQ) | [`packages/expansions/airiq_bathroom_base.yaml`](../packages/expansions/airiq_bathroom_base.yaml) |
| Room Sense (RoomIQ comfort) | [`packages/expansions/comfort_ceiling.yaml`](../packages/expansions/comfort_ceiling.yaml) |
| Room Sense (RoomIQ presence) | [`packages/expansions/presence_ceiling.yaml`](../packages/expansions/presence_ceiling.yaml) |

> The FanTRIAC slot ([`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml)
> and [`packages/features/fan_control_profile.yaml`](../packages/features/fan_control_profile.yaml))
> is intentionally not included in production Release-One while HW-005 is
> open. The FanTRIAC product YAML
> ([`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml))
> and its WebFlash wrapper
> ([`products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml))
> are retained in the repo as blocked / reference files only.

> Package filenames under `packages/expansions/` retain legacy names
> (`airiq_bathroom_*`, `comfort_*`, `presence_*`) for backwards compatibility
> with existing customer references. The WebFlash taxonomy in §3 is the
> source of truth for **artifact names**, not for filesystem paths.

When a new WebFlash `config_string` is added to a release, this table must be
updated in the same PR.

### Repo-local validator

The build matrix this repo declares it will ship lives at
[`config/webflash-builds.json`](../config/webflash-builds.json), and a local
mirror of the contract above lives at
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json).
[`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py)
checks every build entry against that snapshot — config-string grammar,
forbidden tokens, mutual-exclusion rules, artifact-name format, channel
membership, and the existence of each `product_yaml`. Run it locally with
`python3 tests/validate_webflash_builds.py`; CI runs it on every push.

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

- Initial production stable release for Ceiling-POE-VentIQ-RoomIQ with PoE
  power, VentIQ bathroom air-quality sensing, and RoomIQ room sensing.
  FanTRIAC is excluded from production Release-One while HW-005 is open.

## Known Issues

- None.

## Features

- PoE-powered Sense360 Core configuration
- VentIQ bathroom air-quality sensing
- RoomIQ room sensing

## Hardware Requirements

- Sense360 Core R4 or newer
- Sense360 PoE PSU
- Sense360 VentIQ module
- Sense360 RoomIQ module
```

WebFlash will produce a sidecar (`*.meta.json`) from this body with the
shape documented in WebFlash's `DEVELOPER.md → Via GitHub Releases`. This
repo never authors the sidecar directly.

### Drafting the release body

A starting draft for the release body can be produced from the product
catalog with the read-only generator added in RELEASE-001:

```
python3 scripts/generate_webflash_release_notes.py \
    --config-string Ceiling-POE-VentIQ-RoomIQ \
    --version 1.0.0 \
    --channel stable \
    --output release-notes.md \
    --validate
```

RELEASE-002 exposes the same generator behind a manual
`workflow_dispatch` workflow at
[`.github/workflows/release-notes-draft.yml`](../.github/workflows/release-notes-draft.yml).
The workflow takes `config_string`, `version`, `channel`, and an
optional `changelog` input, runs the generator and validator, and
uploads `release-notes.md` as a workflow artifact. It does not create a
GitHub Release, publish firmware, or commit the draft.

The generator emits all four required sections in the exact format
[`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py)
expects, pulls features and hardware metadata from
[`config/webflash-builds.json`](../config/webflash-builds.json) and
[`config/product-catalog.json`](../config/product-catalog.json), and lists
FanTRIAC and Sense360 LED as Known-Issues exclusions for Release-One.
The `## Changelog` section starts as a TODO placeholder; a human must
replace it with the actual user-visible changes for the release before
the body is published. Neither the generator nor the RELEASE-002
workflow creates releases, publishes firmware, or calls any external
service.

---

## Machine-Readable Snapshot

For machine-readable consumption (validators, tooling, the WebFlash importer),
this contract is mirrored in two JSON files at the repo root:

- [`config/webflash-compatibility.json`](../config/webflash-compatibility.json) —
  snapshot of §1–§5: filename pattern, allowed mounting/power/module tokens,
  channels, forbidden-token replacements, mutually-exclusive pairs, conflicts,
  and the fan-driver "max one of" rule.
- [`config/webflash-builds.json`](../config/webflash-builds.json) —
  the build mapping: each entry binds a WebFlash `config_string` to its
  product YAML and the production artifact name.

The Release-One entry references
[`products/webflash/ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml),
a thin wrapper that `!include`s the canonical
[`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml).

[`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py)
loads `config/webflash-compatibility.json` as a required source of truth and
fails fast if it is missing or malformed — there is no hardcoded fallback. If
you change the rules in this document, update the JSON snapshot in the same
PR and re-run the validator.

### Product status catalog

The lifecycle layer on top of the build matrix lives in
[`config/product-catalog.json`](../config/product-catalog.json). It records
the lifecycle status (`production`, `preview`, `blocked`, `legacy-compatible`,
etc.) for each Sense360 product configuration, the canonical product YAML and
WebFlash wrapper paths, the artifact name for production entries, the hardware
SKUs, and any blocked / excluded modules. `config/webflash-builds.json` remains
the authoritative WebFlash build matrix; the catalog adds the lifecycle layer
and is one-way cross-checked against the build matrix by
[`tests/test_product_catalog.py`](../tests/test_product_catalog.py) — every
`status: blocked` entry must NOT appear in the build matrix, and every build
matrix entry must appear in the catalog with a WebFlash-eligible status. New
product configs should declare their status in the catalog before being added
to the build matrix.

PRODUCT-002 extends this catalog to enumerate every legacy/manual product YAML
under `products/` as `status: legacy-compatible`. `legacy-compatible` entries
are retained for manual / custom / remote-package users and are validated by
the broad legacy CI sweep, but they are **not** WebFlash-shippable: they have
no `config_string`, no `artifact_name`, no `webflash_wrapper`, and
`webflash_build_matrix` is `false`. WebFlash builds are still sourced
exclusively from [`config/webflash-builds.json`](../config/webflash-builds.json);
this PR does not add any product to that build matrix and does not change any
WebFlash config string or artifact name.

PRODUCT-003 adds a read-only catalog consistency validator at
[`scripts/validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py)
(unit-tested by
[`tests/test_product_catalog_consistency.py`](../tests/test_product_catalog_consistency.py))
that cross-checks `config/product-catalog.json` against
`config/webflash-builds.json`, `config/webflash-compatibility.json`,
`config/hardware-catalog.json`, `scripts/product_name_mapper.py`, and the
product / wrapper YAML paths. It also exposes a `--checklist` mode for the
add-product workflow:

```text
python3 scripts/validate_product_catalog_consistency.py --checklist Ceiling-POE-VentIQ-RoomIQ
python3 scripts/validate_product_catalog_consistency.py --product products/sense360-ceiling-poe-ventiq-roomiq.yaml
```

The validator does not mutate any file, does not generate any product / wrapper
YAML, and does not change the WebFlash build matrix or artifact name.

---

## Compatibility Rule of Thumb

If you are tempted to invent a token, rename a slot, omit a section, or skip
a heading: **don't.** Either match WebFlash's existing taxonomy verbatim or
file an upstream change in WebFlash first and update this contract afterward.

## See Also

- [`README.md`](../README.md) — repo overview and Release-One quick reference.
- [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  — machine-readable local snapshot of this contract for validators and CI.
- [`docs/release-one.md` (archived)](archive-index.md) — Release-One configuration with full
  slot/file/binary mapping.
- [`docs/product-onboarding.md` (archived)](archive-index.md) — PRODUCT-004 ordered safe sequence for adding a new product / config.
- [`docs/webflash-compatibility-taxonomy-audit.md` (archived)](archive-index.md) — COMPAT-001 per-token audit of the WebFlash taxonomy against the product catalog, hardware evidence, and future-token policy.
- [`docs/product-matrix.md`](product-matrix.md) — full module/slot reference.
- WebFlash `DEVELOPER.md → Via GitHub Releases` — upstream operator flow.
- WebFlash `CLAUDE.md` — canonical SKU table and product taxonomy.

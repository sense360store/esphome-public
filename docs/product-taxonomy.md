# Product Taxonomy & Compatibility

The current Sense360 product taxonomy: board/SKU identity, the WebFlash
config-string grammar, module-slot compatibility, the board/bundle
distinction, the external-attachment model, and how capability differs from
release state. This page is a **navigation document** — it summarises and
links the machine-readable authorities instead of duplicating their detail:

| Question | Authority |
|----------|-----------|
| What boards exist (names, SKUs, sensors, connectors)? | [`config/hardware-catalog.json`](../config/hardware-catalog.json) / [`docs/hardware-catalog.md`](hardware-catalog.md) |
| What lifecycle state is each product configuration in? | [`config/product-catalog.json`](../config/product-catalog.json) |
| What does release publishing actually ship? | [`config/webflash-builds.json`](../config/webflash-builds.json) |
| What config strings / tokens are legal? | [`config/webflash-compatibility.json`](../config/webflash-compatibility.json) / [`docs/webflash-contract.md`](webflash-contract.md) |
| What are the standing release gates? | [`docs/standing-invariants.md`](standing-invariants.md) |

Docs describe; `config/` decides. If this page and a `config/` file ever
disagree, the `config/` file wins and this page is the one to fix.

## Board / SKU taxonomy

The physical product boundary is the **board SKU**. Friendly names are
canonical; old names are legacy reference only (see
[`docs/hardware-catalog.md`](hardware-catalog.md) for the full table with
revisions, old names, and schematic status). There is **no Base/Pro,
Basic/Advanced, or Model/Variant axis** — each SKU is one product, and
optional capability comes from connector attachments, not product variants.

| SKU | Friendly name | Config-string token | PCB-mounted (committed schematic/BOM evidence) | Connector-attached (confirmed) | Unresolved fitment (evidence conflict) |
|-----|---------------|---------------------|------------------------------------------------|--------------------------------|----------------------------------------|
| S360-100 | Sense360 Core | `Ceiling` (mount) | ESP32-S3 hub; connectors for all modules | — | — |
| S360-200 | Sense360 RoomIQ | `RoomIQ` | PIR (EKMC1601111), LTR-303ALS light, SHT4x temp/humidity, BMP581 pressure | LD2450 mmWave radar (connector J2), SEN0609/C4001 radar (connector J3) — see note ¹ | — |
| S360-210 | Sense360 AirIQ | `AirIQ` | SCD41 CO₂, SGP41 VOC/NOx, MICS-4514 gas with STM8 | SPS30 PM (connector; off-board module) | SFA40 HCHO — fitment unresolved, see note ² |
| S360-211 | Sense360 VentIQ | `VentIQ` | SGP41 VOC/NOx | IR surface temperature, SPS30 PM (connectors only) | — |
| S360-300 | Sense360 LED | `LED` | WS2812B LED ring | — | — |
| S360-310 | Sense360 Relay | `FanRelay` | On/off relay for bathroom fans | — | — |
| S360-311 | Sense360 PWM | `FanPWM` | 12 V PWM fan driver, up to 4 fans with tach | — | — |
| S360-312 | Sense360 DAC | `FanDAC` | 0–10 V analog fan driver (GP8403) | — | — |
| S360-320 | Sense360 TRIAC | `FanTRIAC` | Phase dimmer for mains fan or lamp | — | — |
| S360-400 | Sense360 240v PSU | `PWR` (power) | Mains to 5 V (HLK-5M05) | — | — |
| S360-410 | Sense360 PoE PSU | `POE` (power) | PoE to 5 V | — | — |

`USB` (power token) is USB-C power direct to the Core; it is not a separate
board SKU.

¹ **RoomIQ radar modules are connector-attached, not PCB-mounted.** The
committed S360-200 R4 evidence
([`docs/hardware/s360-200-r4-roomiq.md`](hardware/s360-200-r4-roomiq.md))
places the LD2450 on connector `J2` and the SEN0609/C4001 on connector `J3`;
the PCB-mounted parts are U1 LTR-303ALS, U2 SHT4x, U3 EKMC1601111 PIR, and
U4 BMP581. Authoritative RoomIQ product bundles may **include** the radar
modules (the full tri-presence system) — commercial inclusion is a bundle
decision (owned by SOT) and never converts a connector-attached module into
a PCB-mounted component. Which radar connectors are populated in shipped
units is itself an open verify item in that evidence record.

² **SFA40 fitment on S360-210 is unresolved — do not read it as either
column.** Layered posture: PCB design evidence — the R4 schematic/BOM list
`U2 = SFA40-D-Rx` as populated on the board (population still unverified)
([`docs/hardware/artifacts/S360-210-R4.md`](hardware/artifacts/S360-210-R4.md));
production population — not physically/CPL verified; catalog/reference
wording — conflicting/stale (describes an SFA40 connector); firmware /
customer entities — not currently exposed. `HW-PINMAP-210-FOLLOWUP` owns the
reconciliation; until it lands, current docs must carry this conflict
rather than a definitive on-board or connector-only claim.

When reading or writing anything about a board, keep these layers distinct
and never collapse them:

1. **Board/SKU identity** — the row above.
2. **Production population** — what is actually fitted on the PCB
   (per-board evidence lives under `docs/hardware/`).
3. **Connector capability** — what the board *can* accept externally.
   A connector is not a fitted part.
4. **Bundle contents** — what a commercial bundle actually includes
   (owned by SOT, not this repo).
5. **Firmware driver compiled** — what the firmware builds in. Compiled
   drivers can drift from the catalog (see *Known firmware/catalog drift*
   below); a compiled driver is not proof of physical hardware.
6. **Customer functionality exposed** — entities actually surfaced
   (see [`config/feature-entity-matrix.json`](../config/feature-entity-matrix.json)).
7. **Lifecycle / release state** — see *Lifecycle and release state* below.
8. **Hardware-validation status** — `schematic_status` per catalog entry
   and the evidence records under `docs/hardware/`; a build or release is
   not hardware verification.

## Config-string grammar

WebFlash describes a device by chaining slot tokens
(full contract: [`docs/webflash-contract.md`](webflash-contract.md) §2–§3,
snapshot: [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)):

```text
{Mount}-{Power}-[AirIQ|VentIQ]-[FanRelay|FanPWM|FanDAC|FanTRIAC]-[RoomIQ]-[LED]
```

| Slot | Allowed values |
|------|----------------|
| Mount | `Ceiling` |
| Power | `USB`, `POE`, `PWR` |
| Air quality | `AirIQ`, `VentIQ` (mutually exclusive — same module slot) |
| Fan driver | `FanRelay`, `FanPWM`, `FanDAC`, `FanTRIAC` (max one; firmware-distinct) |
| Room sense | `RoomIQ` |
| Indicator | `LED` |

Module order is fixed; skip slots that do not apply. Token capitalization is
case-sensitive and the ordering is canonical — do not reorder, abbreviate, or
invent tokens.

## Compatibility rules

Machine-readable in
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
and enforced by [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py)
and [`tests/test_taxonomy_terminology.py`](../tests/test_taxonomy_terminology.py):

1. **`AirIQ` and `VentIQ` are mutually exclusive.** They occupy the same
   air-quality module slot; a device runs one or the other, never both.
2. **`RoomIQ` is independent.** It may accompany either air-quality module
   or ship without one.
3. **Fan driver variants are distinct products and distinct firmware.**
   `FanRelay`, `FanPWM`, `FanDAC`, and `FanTRIAC` each produce a separate
   binary; they are not interchangeable at runtime, and the generic `Fan`
   token is forbidden.
4. **`FanDAC` conflicts with `AirIQ`/`VentIQ` at I²C `0x59`.** The GP8403
   IC2 default collides with the SGP41; `0x59` is forbidden when an
   air-quality module is present (`FANDAC-I2C-ADDR-001`, pending bench).
   See the address policy in the compatibility snapshot for the single
   documented advanced/manual exception.
5. **External attachments are not inherent board components.** A config
   string names boards, not attachments. Connector-supported parts —
   SPS30 (connector), IR temperature (connector), and the RoomIQ radar
   modules (LD2450/SEN0609 on connectors J2/J3) — are present only when
   explicitly declared for a bundle or fitted by the user. (The SFA40 fitment
   stays unresolved under `HW-PINMAP-210-FOLLOWUP` and is excluded from this
   rule — see note ² above.)

## Boards vs bundles vs YAML layers

- **Board package** (`packages/boards/`) — authoritative firmware definition
  for one SKU.
- **Bundle** (`products/bundles/`) — one YAML per WebFlash config string,
  assembling boards + base infrastructure + feature profiles. Bundle
  filenames are the lowercase config string.
- **Shim** (`products/sense360-*.yaml`) — thin customer include paths that
  `!include` the bundle. Customers pin these at release tags; they are never
  renamed or deleted.
- **WebFlash wrapper** (`products/webflash/`) — thin re-exports the release
  workflow consumes.
- **Commercial bundles** (what a customer buys in a kit) are a different
  thing from YAML bundles: commercial bundle/kit truth is owned by
  [`sense360store/SOT`](https://github.com/sense360store/SOT), with the
  repo-local kit declarations in
  [`config/room-bundle-skus.json`](../config/room-bundle-skus.json) and
  [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json).

See [`docs/system-architecture.md`](system-architecture.md) for the full
board / bundle / alias / shim layering.

## Lifecycle and release state

**A valid config string is not a released product.** Capability (a YAML that
composes and compiles) and release state are different layers:

- [`config/product-catalog.json`](../config/product-catalog.json) records
  lifecycle status per configuration (`production`, `preview`,
  `compile-only`, `hardware-pending`, `blocked`, `legacy-compatible`,
  `deprecated`, `removed`).
- [`config/webflash-builds.json`](../config/webflash-builds.json) is the
  declaration-driven release matrix (ESP-007): releases ship **only** what
  it declares, on the channel it declares (`stable`, `preview`, `beta`,
  `experimental`). Many product YAMLs in this repo have **no** published
  artifact at the current tag, and preview/experimental artifacts are
  firmware-build proof only — never hardware, bench, compliance, or
  commercial-availability proof.
- The production stable customer baseline is config string
  `Ceiling-POE-VentIQ-RoomIQ` (the configuration shipped by the
  **Release-One** programme — see *Naming history* below). The standing
  gates in [`docs/standing-invariants.md`](standing-invariants.md) govern
  what may ever change channel: fan configs never ship stable, and FanTRIAC
  lives in the experimental self-build lane only (never stable, recommended,
  default, buyable, or kit-exposed; `TRIAC-COMMISSIONING-001` — any FanTRIAC
  status change is human-review only).

## Known firmware/catalog drift (tracked, do not restate as fact)

Compiled firmware currently drifts from the hardware catalog in three
places. These are open reconciliation items — current docs must present the
catalog identity as truth and may mention the drifted part only as drift:

| Catalog truth | Compiled today (drift) | Tracking |
|---------------|------------------------|----------|
| RoomIQ light sensor LTR-303ALS | Reconciled to LTR-303ALS-01 @ 0x29 via `ltr_als_ps` (the legacy VEML7700 drift is removed) | `S360-200-R4-HARDWARE-RECONCILIATION-001` (driver reconciled; on-hardware response pending bench) |
| No pressure part on AirIQ/VentIQ (BMP581 is RoomIQ hardware) | BMP390 driver (legacy) compiled in AirIQ/VentIQ packages | roadmap drift records; disposition owner-only |
| AirIQ SFA40 fitment (connector per catalog; on-board U2 per schematic/BOM) | — | `HW-PINMAP-210-FOLLOWUP` (owner decision pending) |

See [`docs/sense360-roadmap-status.md`](sense360-roadmap-status.md) for the
live drift records.

## Current customer-facing names

Use the **friendly names** from the table above, verbatim, in all new
customer-facing text: `Sense360 Core`, `Sense360 RoomIQ`, `Sense360 AirIQ`,
`Sense360 VentIQ`, `Sense360 LED`, `Sense360 Relay`, `Sense360 PWM`,
`Sense360 DAC`, `Sense360 TRIAC`, `Sense360 240v PSU`, `Sense360 PoE PSU`.
Use `Ceiling`, never `Celling` (legacy typo, quoted only in evidence
records).

## Naming history and legacy-name compatibility policy

**Release-One** is the name of the **initial release programme** — the
programme that shipped the first production stable configuration
(`Ceiling-POE-VentIQ-RoomIQ`, first artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`). The name remains
correct in historical records, release evidence, and the standing
invariants that reference that baseline. It is **not** the name of the
product taxonomy or platform architecture: current wording should say
"the current production stable configuration" (per
[`config/product-catalog.json`](../config/product-catalog.json) /
[`config/webflash-builds.json`](../config/webflash-builds.json)) rather than
treating "Release-One" as a permanent product model.

Earlier vocabularies map to the current taxonomy as follows. These legacy
terms are **read-time compatibility only** — they must not drive new
product design, new filenames, new artifacts, or new customer copy:

| Legacy term | Current term | Where the legacy form legitimately survives |
|-------------|--------------|----------------------------------------------|
| Comfort | **RoomIQ** (climate + light half) | `packages/expansions/comfort_*.yaml` alias filenames, ESPHome entity ids |
| Presence | **RoomIQ** (mmWave half) | `packages/expansions/presence_*.yaml` alias filenames, entity ids |
| Bathroom / Bathroom Pro / BathroomAirIQ | **VentIQ** | `packages/expansions/airiq_bathroom_*.yaml` alias filenames; catalog `old_name` |
| AirIQ Base / AirIQ Pro / AirIQProv | **AirIQ** (single SKU) | forbidden-token mapping tables, read-time aliases |
| VentIQ Base / VentIQ Pro | **VentIQ** (single SKU; attachments named explicitly) | legacy alias filenames only |
| Fan (generic) | **FanRelay / FanPWM / FanDAC / FanTRIAC** | forbidden-token mapping tables |
| FanAnalog | **FanDAC** | forbidden-token mapping tables |
| Mini / Wall / Desk variants | *retired* — not in the current product line | tag-pinned legacy releases (`PRODUCT-DEP-MINI-001`); historical docs |

The enforcement policy — which terms are forbidden where, and which paths
legitimately keep legacy vocabulary — is machine-readable in
[`config/legacy-term-allowlist.json`](../config/legacy-term-allowlist.json)
and enforced by
[`tests/test_taxonomy_terminology.py`](../tests/test_taxonomy_terminology.py).

## Build output contract

CI publishes unsigned WebFlash-compatible `.bin` assets named:

```text
Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin
```

The mapping from product YAML to artifact name is implemented in
[`scripts/product_name_mapper.py`](../scripts/product_name_mapper.py),
declared in [`config/webflash-builds.json`](../config/webflash-builds.json),
validated by [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py),
and consumed by
[`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml).
This repo does **not** sign firmware; WebFlash is the production signing /
manifest / flash authority and the **upstream authority for the distribution
naming surfaces** — config-string grammar and release-artifact filename
grammar — which this repo mirrors and enforces locally via
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
(see [`docs/webflash-contract.md`](webflash-contract.md)). That authority is
distribution-scoped only: physical board identity stays with the hardware
catalog in this repo, and commercial product/bundle truth stays with SOT.

## See also

- [`docs/webflash-contract.md`](webflash-contract.md) — the cross-repo
  contract (artifact naming, grammar, release-body format).
- [`docs/hardware-catalog.md`](hardware-catalog.md) — canonical board
  names, SKUs, revisions, legacy names, schematic status.
- [`docs/standing-invariants.md`](standing-invariants.md) — standing
  release gates.
- [`docs/system-architecture.md`](system-architecture.md) — YAML layering.
- [`docs/product-matrix.md`](product-matrix.md) — legacy long-form hardware
  reference (contains retired products; see its status banner).
- [`docs/getting-started.md`](getting-started.md) — flash or adopt the
  firmware.

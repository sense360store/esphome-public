# Sense360 Whole-System Architecture

**Type:** Docs only. This document describes how the existing pieces fit
together. It changes no firmware, CI, config, or release behaviour.

This is the single whole-pipeline view of how a Sense360 device gets its
firmware, from product YAML in this repo to a flashed device. It exists because
the flow spans **two repositories** and the boundary between them is easy to
miss.

## The two repositories

| Repo | Role | Owns |
|------|------|------|
| [`sense360store/esphome-public`](https://github.com/sense360store/esphome-public) (this repo) | **Firmware source + build/publish** | Product YAML, packages, the WebFlash naming contract, and the release `.bin` artifacts. Also the manual/custom ESPHome path for advanced users. |
| [`sense360store/WebFlash`](https://github.com/sense360store/WebFlash) | **Production distribution** | Importing the release artifacts, **signing**, sidecar + production `manifest.json` generation, and browser-based flashing. This is the path most customers use. |

> **Signing boundary.** This repo publishes **unsigned** raw `.bin` assets plus
> checksums and a build-info `manifest.json`. WebFlash is the production
> signing/deployment authority — it consumes the raw assets and generates its
> own production manifest. The build-info `manifest.json` attached to a release
> here is metadata, **not** WebFlash's production manifest.

## The boundary

The handoff is a published GitHub Release in this repo and a single import file
in WebFlash:

- **`esphome-public` side:** `firmware-build-release.yml` compiles each product,
  renames each binary to the WebFlash contract name
  (`Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin`), and attaches the `.bin`
  set + checksums + build-info `manifest.json` to a tagged GitHub Release. See
  [WebFlash Compatibility Contract](webflash-contract.md) and
  [Build Output Contract](product-taxonomy.md#build-output-contract).
- **WebFlash side:** `firmware/sources.json` lists each upstream source pinned
  to a **release tag** (`release_tag`, e.g. `v1.0.0`), the expected
  `asset_name`, and the required release-body sections. WebFlash imports the raw
  asset, signs it, and regenerates its production `manifest.json`.

### Tag-pinning rule

Every cross-repo reference pins to a **release tag**, never a moving branch:

- WebFlash's `firmware/sources.json` pins each source by `release_tag`.
- Manual/custom users pin their `packages:` / `external_components:` `ref:` to a
  release tag (e.g. `ref: v1.0.0`) — **never** `ref: main`. `main` is a moving
  target; see the [pinning note](getting-started.md#which-path-should-i-use).

## Flow: product YAML → flashed device

```
 esphome-public (this repo)                          WebFlash repo
 ┌──────────────────────────────┐                    ┌────────────────────────────┐
 │ products/*.yaml  (+ packages)│                    │ firmware/sources.json      │
 │            │                 │                    │  (pins release_tag,        │
 │            ▼                 │                    │   asset_name per source)   │
 │  validate.yml  (per-PR gate) │                    │            │               │
 │            │                 │                    │            ▼               │
 │            ▼                 │   tagged GitHub    │   import raw .bin +         │
 │ firmware-build-release.yml   │   Release assets   │   verify checksum/contract  │
 │  compile → rename to         │ ─────────────────► │            │               │
 │  Sense360-{CONFIG}-v{VER}-   │  (unsigned .bin +  │            ▼               │
 │  {CHANNEL}.bin + checksums   │   checksums +      │   SIGN + regenerate         │
 │  + build-info manifest.json  │   build-info       │   production manifest.json  │
 └──────────────────────────────┘   manifest.json)   │            │               │
                                                      │            ▼               │
                                                      │   browser flash (Web       │
                                                      │   Serial) ──► device       │
                                                      └────────────────────────────┘
```

## Inside esphome-public: board / product layers

The `products/*.yaml (+ packages)` box on the left of the flow is a
**board / product composition** (the board/bundle refactor, planned in
[`docs/arch-board-bundle-plan.md` (archived)](archive-index.md) and proven for
CI/gate parity by [`docs/ci-pipeline.md`](ci-pipeline.md)). The tiers exist so
the YAML names what the catalog names — physical board SKUs and WebFlash config
strings — instead of only functional package names.

| Tier | Where | What it is |
|------|-------|------------|
| **Board packages (authoritative)** | `packages/boards/s360-*.yaml` | One canonical, self-contained package per board SKU — `S360-100` Core, `S360-200` RoomIQ, `S360-210` AirIQ, `S360-211` VentIQ, `S360-300` LED, `S360-410` PoE PSU — plus mount/power/variant overlays. The board package owns the chip, pin map, connector nets, I²C addresses, and UART bindings. This is the source of truth. |
| **Legacy aliases (REMOVED)** | formerly `packages/expansions/*.yaml`, `packages/hardware/*.yaml` functional names (`led_ring_ceiling.yaml`, `airiq_ceiling.yaml`, `comfort_ceiling.yaml`, `presence_ceiling.yaml`, `power_poe.yaml`, …) | Deleted by SENSE360-CANONICALISATION-001 PR 07 (zero-alias): every live consumer was re-pointed to the authoritative board package first, the PR 06 contract gate proved every resolved composition byte-identical across the removal, and `tests/test_zero_alias.py` pins the deleted paths. Release tags keep every historical path for tag-pinned users. Do not add new alias paths. |
| **Core flip (landed)** | `packages/boards/s360-100-core-ceiling.yaml` (`S360-100` ceiling Core) | The Core source-of-truth flip landed in SENSE360-CANONICALISATION-001 PR 07: the ceiling Core content moved verbatim into the board package, the legacy `hardware/sense360_core_ceiling.yaml` path and the never-wired `boards/s360-100-core.yaml` prototype are deleted, and the remaining `hardware/sense360_core*.yaml` files (generic / PoE / voice) survive only as implementations of catalogued legacy-compatible products. |
| **Cross-referenced base drivers (also authoritative)** | `packages/features/ceiling_halo_leds.yaml` | The one documented base driver with no board package holding its content. It stays **authoritative and un-folded** (cross-referenced from the board layer, not aliased). The formerly cross-referenced `expansions/airiq.yaml` and `expansions/presence_ld2450.yaml` were removed under PR 07 zero-alias (superseded by the board packages that absorbed their content); `expansions/presence_ld2412.yaml` was removed by REPO-CONSOLIDATION-001 (zero composers after the package-level remote-include path retired). |
| **Products (canonical compositions + customer include contract)** | `products/sense360-*.yaml` | One YAML per WebFlash **config string** (`sense360-<config-string>.yaml`, named 1:1 to it) assembling `boards + expansions + base + profiles`, carrying the substitutions, entity names, config string, and artifact-name identity — plus the catalogued legacy compositions. This is ALSO the customer-pinned path (`files: - products/sense360-…yaml`, `ref: v1.0.7`): REPO-CONSOLIDATION-001 folded the former `products/bundles/` layer into these files (the root path had been a thin one-include shim of its bundle), so a pinned include now resolves `product → board packages` directly. Release tags keep the historical `bundles/` paths for tag-pinned users. |

Some families are **authoritative by composition** rather than 1:1: the
`S360-200` RoomIQ board composes two independently-bound halves
(`s360-200-roomiq-climate.yaml` + `s360-200-roomiq-radar.yaml`, each
authoritative), because the legacy `comfort_*`/`presence_*` paths bind them
under separate package keys. The 1:1 LED / AirIQ / VentIQ / PoE-PSU families
fold their whole driver into one board file. The mains-voltage driver boards
(`S360-310` / `S360-320` / `S360-400`) and the SELV fan-driver SKUs
(`S360-311` / `S360-312`) remain expansion packages behind their own evidence /
compliance gates and are **not** in the board layer yet (see
[`docs/arch-board-bundle-plan.md` §2.1 (archived)](archive-index.md)).

### Cross-repo contract: this layering is invisible to WebFlash

The board/product layer restructuring (including the former bundle and
alias layers' removal) is an **esphome-public-internal** concern. WebFlash couples to this repo through **only** three stable surfaces —
GitHub release **tags**, **config-string** values, and **artifact names** — and
**no** WebFlash file references any `packages/` or `products/` path (confirmed
read-only against `WebFlash/firmware/sources.json`, `WebFlash/manifest.json`,
and `WebFlash/scripts/data/`). Therefore:

- Every config string (`Ceiling-POE-VentIQ-RoomIQ`,
  `Ceiling-POE-VentIQ-RoomIQ-LED`, …) and every artifact name
  (`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, …) stays
  byte-identical across the refactor.
- The release gate stays config-string driven
  (`config/webflash-builds.json` → `products/webflash/` wrapper →
  canonical product → boards), so the same config strings build under the same artifact
  names.
- A board/product-layer rename in esphome-public requires **no** change to
  WebFlash's `sources.json`, `manifest.json`, or importer. **esphome-public is
  upstream; WebFlash is downstream**, and the boundary is config strings +
  artifact names + tags, nothing else. (The matching WebFlash-side note is
  owned by `WEBFLASH-ARCH-SYNC-001`.)

## Lifecycle source of record

Release targets, channels, blockers, WebFlash exposure, and the next-PR queue
are tracked in the canonical
[`docs/sense360-roadmap-status.md`](sense360-roadmap-status.md)
(DOCS-CONSOLIDATION-ROADMAP-001), which links each fact back to its
machine-readable source of truth (`config/webflash-builds.json`,
`config/product-catalog.json`, `config/hardware-catalog.json`, …). When this
architecture view and the roadmap doc disagree, the roadmap doc and its
underlying config files win.

## Related documentation

- [Board / product layers](#inside-esphome-public-board--product-layers) — the firmware-YAML composition inside this repo and why it is invisible to WebFlash.
- [Board-package & bundle-YAML architecture plan (archived)](archive-index.md) — the target shape, rename/alias policy, and ordered PR sequence for the refactor.
- [CI/CD Pipeline](ci-pipeline.md) — per-workflow gate-vs-manual map.
- [Roadmap / Status](sense360-roadmap-status.md) — canonical lifecycle source of record.
- [WebFlash Compatibility Contract](webflash-contract.md) — artifact naming + release-body format.
- [WebFlash Release Handoff (archived)](archive-index.md) — operational source-to-installer flow.

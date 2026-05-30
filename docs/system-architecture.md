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
  [Build Output Contract](../README.md#build-output-contract).
- **WebFlash side:** `firmware/sources.json` lists each upstream source pinned
  to a **release tag** (`release_tag`, e.g. `v1.0.0`), the expected
  `asset_name`, and the required release-body sections. WebFlash imports the raw
  asset, signs it, and regenerates its production `manifest.json`.

### Tag-pinning rule

Every cross-repo reference pins to a **release tag**, never a moving branch:

- WebFlash's `firmware/sources.json` pins each source by `release_tag`.
- Manual/custom users pin their `packages:` / `external_components:` `ref:` to a
  release tag (e.g. `ref: v1.0.0`) — **never** `ref: main`. `main` is a moving
  target; see the [README pinning note](../README.md#which-path-should-i-use).

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

## Inside esphome-public: board / bundle / alias / shim layers

The `products/*.yaml (+ packages)` box on the left of the flow is itself a
**four-tier composition** (the board/bundle refactor, planned in
[`docs/arch-board-bundle-plan.md`](arch-board-bundle-plan.md) and proven for
CI/gate parity by [`docs/ci-pipeline.md`](ci-pipeline.md)). The tiers exist so
the YAML names what the catalog names — physical board SKUs and WebFlash config
strings — instead of only functional package names.

| Tier | Where | What it is |
|------|-------|------------|
| **Board packages (authoritative)** | `packages/boards/s360-*.yaml` | One canonical, self-contained package per board SKU — `S360-100` Core, `S360-200` RoomIQ, `S360-210` AirIQ, `S360-211` VentIQ, `S360-300` LED, `S360-410` PoE PSU — plus mount/power/variant overlays. The board package owns the chip, pin map, connector nets, I²C addresses, and UART bindings. This is the source of truth. |
| **Legacy aliases** | `packages/expansions/*.yaml`, `packages/hardware/*.yaml` (legacy functional names — `led_ring_ceiling.yaml`, `airiq_ceiling.yaml`, `comfort_ceiling.yaml`, `presence_ceiling.yaml`, `power_poe.yaml`, …) | Thin `!include` wrappers of their board package. The **path is preserved, never deleted**, so legacy-compatible products and tests resolve byte-identically. An alias is dropped only when its binder count reaches zero (gated on `PRODUCT-DEP-CORE-001`). |
| **Pending-flip legacy paths** | `packages/hardware/sense360_core_*.yaml` (`S360-100` Core mounts) | The Core base chip/bus is authoritative in `boards/s360-100-core.yaml`, but the **mount-variant overlays still wrap the legacy path** (the board overlay `!include`s the legacy file, the inverse of the flipped families). Core's full source-of-truth flip is a later slice; the legacy mount path stays authoritative until then. |
| **Cross-referenced base drivers (also authoritative)** | `packages/expansions/airiq.yaml`, `packages/expansions/presence_ld2450.yaml`, `packages/expansions/presence_ld2412.yaml`, `packages/features/ceiling_halo_leds.yaml` | Documented base drivers / radar primitives with no board package holding their content. They stay **authoritative and un-folded** (cross-referenced from the board layer, not aliased), exactly as `airiq.yaml` (RENAME-002) and `ceiling_halo_leds.yaml` (RENAME-001) did. |
| **Bundles (config-string-named)** | `products/bundles/*.yaml` | One YAML per WebFlash **config string**, named 1:1 to it, assembling `boards + expansions + base + profiles`. Carries the substitutions, entity names, config string, and artifact-name identity of the product it backs. |
| **Product shims (customer include contract)** | `products/sense360-*.yaml` (the seven config-string products) | Thin `!include` of the matching bundle. The customer-pinned path (`files: - products/sense360-…yaml`, `ref: v1.0.0`) is preserved byte-for-byte, so a pinned include resolves `shim → bundle → board packages` unchanged. |

Some families are **authoritative by composition** rather than 1:1: the
`S360-200` RoomIQ board composes two independently-bound halves
(`s360-200-roomiq-climate.yaml` + `s360-200-roomiq-radar.yaml`, each
authoritative), because the legacy `comfort_*`/`presence_*` paths bind them
under separate package keys. The 1:1 LED / AirIQ / VentIQ / PoE-PSU families
fold their whole driver into one board file. The mains-voltage driver boards
(`S360-310` / `S360-320` / `S360-400`) and the SELV fan-driver SKUs
(`S360-311` / `S360-312`) remain expansion packages behind their own evidence /
compliance gates and are **not** in the board layer yet (see
[`docs/arch-board-bundle-plan.md` §2.1](arch-board-bundle-plan.md)).

### Cross-repo contract: this layering is invisible to WebFlash

The board/bundle/alias/shim restructuring is an **esphome-public-internal**
concern. WebFlash couples to this repo through **only** three stable surfaces —
GitHub release **tags**, **config-string** values, and **artifact names** — and
**no** WebFlash file references any `packages/` or `products/` path (confirmed
read-only against `WebFlash/firmware/sources.json`, `WebFlash/manifest.json`,
and `WebFlash/scripts/data/`). Therefore:

- Every config string (`Ceiling-POE-VentIQ-RoomIQ`,
  `Ceiling-POE-VentIQ-RoomIQ-LED`, …) and every artifact name
  (`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, …) stays
  byte-identical across the refactor.
- The release gate stays config-string driven
  (`config/webflash-builds.json` → `products/webflash/` wrapper → product shim →
  bundle → boards), so the same config strings build under the same artifact
  names.
- A board/bundle/alias rename in esphome-public requires **no** change to
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

- [Board / bundle / alias / shim layers](#inside-esphome-public-board--bundle--alias--shim-layers) — the four-tier firmware-YAML composition inside this repo and why it is invisible to WebFlash.
- [Board-package & bundle-YAML architecture plan](arch-board-bundle-plan.md) — the target shape, rename/alias policy, and ordered PR sequence for the refactor.
- [CI/CD Pipeline](ci-pipeline.md) — per-workflow gate-vs-manual map.
- [Roadmap / Status](sense360-roadmap-status.md) — canonical lifecycle source of record.
- [WebFlash Compatibility Contract](webflash-contract.md) — artifact naming + release-body format.
- [WebFlash Release Handoff](webflash-release-handoff.md) — operational source-to-installer flow.

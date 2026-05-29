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

- [CI/CD Pipeline](ci-pipeline.md) — per-workflow gate-vs-manual map.
- [Roadmap / Status](sense360-roadmap-status.md) — canonical lifecycle source of record.
- [WebFlash Compatibility Contract](webflash-contract.md) — artifact naming + release-body format.
- [WebFlash Release Handoff](webflash-release-handoff.md) — operational source-to-installer flow.

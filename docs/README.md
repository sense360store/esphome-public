# Sense360 Documentation Index

The documentation map for `sense360store/esphome-public`. The repository
[README](../README.md) is the front door; everything else lives here.

> **Repo status / roadmap / blockers:** the single canonical document is
> [`sense360-roadmap-status.md`](sense360-roadmap-status.md). The standing
> gates live in [`standing-invariants.md`](standing-invariants.md).
> Archived documents are indexed in [`archive-index.md`](archive-index.md).

## Getting started

- [Getting Started](getting-started.md) — which path to use (WebFlash vs
  manual), quick start for the manual / custom ESPHome path, configuration
  approaches, package reference, system requirements.
- [Installation Guide](installation.md) — step-by-step setup.
- [Release Channels](release-channels.md) — stable / preview / experimental:
  what each means for a customer and what support each receives.
- [Getting help](../SUPPORT.md) — issues, discussions, orders and warranty.

## Hardware reference

- [Hardware Catalog](hardware-catalog.md) — canonical Sense360 board/module
  names, SKUs, revisions, and legacy names (machine-readable mirror:
  [`config/hardware-catalog.json`](../config/hardware-catalog.json)).
- [S360-100-R4 Core Hardware Reference](hardware/s360-100-r4-core.md) — pins,
  connectors, and schematic net names for the Sense360 Core board.
- [S360-200-R4 RoomIQ Hardware Reference](hardware/s360-200-r4-roomiq.md) —
  pins, connectors, sensors, and schematic net names for the RoomIQ board.
- Per-board references and module pin maps for every SKU live under
  [`docs/hardware/`](hardware/).

## Configuration

- [Product Taxonomy & Compatibility](product-taxonomy.md) — WebFlash config
  strings, Release-One, sensor / driver modules, compatibility rules, build
  output contract, legacy terminology.
- [Product Matrix](product-matrix.md) — complete slot/module reference.
- [Configuration Reference](configuration.md) — customization options.
- [WebFlash Compatibility Contract](webflash-contract.md) — artifact naming,
  config-string grammar, release-body format (snapshot:
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)).
- [System Architecture](system-architecture.md) — whole-pipeline view of how
  `esphome-public` and WebFlash relate (product YAML → release artifact →
  WebFlash import → flashed device).
- [Repository Structure & Reference Map](repo-structure.md) — top-level
  directories and the board / bundle / alias / shim include chain.
- [Changelog](../CHANGELOG.md) — version history.

## Contributing

- [Contributing Guide](../CONTRIBUTING.md) — how to file, how to PR, the
  local gate that must pass, doc conventions.
- [Development Guide](development.md) — contributing and testing.
- [CI/CD Pipeline](ci-pipeline.md) — per-workflow gate-vs-manual
  classification for all workflows.
- [Release Pipeline](RELEASE-PIPELINE.md) — the full cross-repo release
  sequence (Bump → Create Release → Build & Release → WebFlash Add Source →
  Import → Deploy), stage by stage.
- Archived process documents (release handoff, Release-One configuration,
  product onboarding, manual-path walkthroughs) are indexed in
  [`archive-index.md`](archive-index.md).

# Sense360 ESPHome Firmware

ESPHome firmware **source** for [Sense360](https://mysense360.com) environmental
monitoring devices (ESP32-S3 ceiling hubs plus sensor / driver / PSU modules).
This repo holds the product YAML, builds and publishes the unsigned release
`.bin` artifacts, and is the manual / custom firmware path for advanced users.
**[WebFlash](https://sense360store.github.io/WebFlash/) is the production path**
most customers use — browser-based flashing of official **signed** firmware, no
tooling, no YAML.

[![ESPHome](https://img.shields.io/badge/ESPHome-2025.10%2B-blue)](https://esphome.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Release](https://img.shields.io/github/v/release/sense360store/esphome-public)](https://github.com/sense360store/esphome-public/releases)
[![CI: Quick Validation (PR gate)](https://github.com/sense360store/esphome-public/actions/workflows/validate.yml/badge.svg)](https://github.com/sense360store/esphome-public/actions/workflows/validate.yml)

## Flash or adopt in three steps

**Most customers:** use [WebFlash](https://sense360store.github.io/WebFlash/) —
flash signed stable firmware from the browser. Done. The steps below are the
**manual / custom path** for advanced users who want to run the YAML through
ESPHome:

1. **Pick a product YAML** from [`products/`](products/) — the production
   stable baseline is
   [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](products/sense360-ceiling-poe-ventiq-roomiq.yaml)
   (`Ceiling-POE-VentIQ-RoomIQ`).
2. **Add your secrets** — copy [`secrets.example.yaml`](secrets.example.yaml)
   to `secrets.yaml` (gitignored, never commit it) and reference the product
   from your device YAML, **pinned to a release tag**:

   ```yaml
   packages:
     sense360_firmware:
       url: https://github.com/sense360store/esphome-public
       ref: v1.0.0  # Pin to a release tag — never 'main' in production
       files: [products/sense360-ceiling-poe-ventiq-roomiq.yaml]
       refresh: 1d
   substitutions:
     device_name: sense360-bathroom
     friendly_name: "Bathroom Sense360"
   ```

3. **Flash** — first time over USB-C via the ESPHome Dashboard, wirelessly
   (OTA) after that.

Full walkthrough, configuration approaches, and the package reference:
[`docs/getting-started.md`](docs/getting-started.md).

## Documentation

Everything lives under [`docs/`](docs/README.md) — start at the
[documentation index](docs/README.md). Key entries:

- [Getting Started](docs/getting-started.md) — WebFlash vs manual path, quick start.
- [Product Taxonomy & Compatibility](docs/product-taxonomy.md) — config strings,
  modules, Release-One, build output contract.
- [Release Channels](docs/release-channels.md) — stable / preview / experimental
  and what support each receives.
- [Hardware Catalog](docs/hardware-catalog.md) — canonical board names, SKUs, revisions.
- [Roadmap & Status](docs/sense360-roadmap-status.md) — the canonical status /
  roadmap / blocker document.

## Where to get help

See [SUPPORT.md](SUPPORT.md) for the full routing. In short:

- **Defects** — [GitHub Issues](https://github.com/sense360store/esphome-public/issues)
  (firmware, YAML, sensors, builds) or
  [WebFlash Issues](https://github.com/sense360store/WebFlash/issues) (the flashing site).
- **Questions & community** — [GitHub Discussions](https://github.com/sense360store/esphome-public/discussions).
- **Orders & warranty** — the contact page at [mysense360.com](https://mysense360.com).

Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for how to file,
how to PR, and the local gate that must pass.

## License

The firmware configurations and source code in this repository are licensed
under the MIT License (© 2026 Sense360). See [LICENSE](LICENSE) for details.

Sense360 **hardware designs** are published separately under
**CERN-OHL-P** (the permissive CERN Open Hardware Licence); they are not part
of this repository's MIT grant. Firmware for the **experimental lane**
(self-build mains-voltage boards) follows the market posture recorded in
[`docs/decisions/COMPLIANCE-001-RESOLUTION-001.md`](docs/decisions/COMPLIANCE-001-RESOLUTION-001.md):
Sense360 never places those boards on the market, self-builders build and
operate them entirely at their own risk, and open publication of the design
files and firmware is not a safety, EMC, or compliance claim of any kind.

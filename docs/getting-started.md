# Getting Started

How to get Sense360 firmware onto a device — the browser path most
customers use, and the manual / custom ESPHome path for advanced users.
This page was split out of the repository README front door; the full
documentation map is in the [documentation index](README.md).

## Which Path Should I Use?

| Path | Who | What it gives you |
|------|-----|-------------------|
| **WebFlash** (recommended) | Most customers | Browser-based flashing of official **signed** firmware. No tooling, no YAML. |
| **`esphome-public`** (this repo) | Advanced users | Inspect, fork, and customize the ESPHome YAML used by official Sense360 firmware. |

> **WebFlash is the production path.** It is the browser-based flasher at
> [sense360store.github.io/WebFlash](https://sense360store.github.io/WebFlash/). This repo is the manual/custom firmware path
> linked from WebFlash — use it only if you want to read or modify the YAML.
>
> **Production users must pin to a release tag** (e.g. `ref: v1.0.7`). Never use
> `ref: main` for a device you depend on — `main` is a moving target.

## Quick Start (Custom / Manual Flash)

> Most customers should use [WebFlash](https://sense360store.github.io/WebFlash/) instead.
> This section is for advanced users running the YAML directly through
> ESPHome.

### 1. Pick a product configuration

Find the YAML matching your hardware in [`products/`](../products/). For
Release-One that is:

```text
products/sense360-ceiling-poe-ventiq-roomiq.yaml
```

### 2. Configure secrets

Copy [`secrets.example.yaml`](../secrets.example.yaml) to `secrets.yaml` and
edit it with your real local credentials:

```bash
cp secrets.example.yaml secrets.yaml
```

```yaml
wifi_ssid: "YourNetworkName"
wifi_password: "YourWiFiPassword"
api_encryption_key: "GENERATE_WITH_ESPHOME_WIZARD"
ota_password: "your-secure-ota-password"
web_username: "admin"
web_password: "your-secure-web-password"
```

> `secrets.yaml` is gitignored — never commit it. CI generates its own
> placeholder secrets for validation/builds, so you do not need to commit
> anything for CI to pass.
>
> Generate an API key with `esphome wizard` or `openssl rand -base64 32`.

### 3. Reference the product from your device YAML

```yaml
packages:
  sense360_firmware:
    url: https://github.com/sense360store/esphome-public
    ref: v1.0.7  # Pin to a release tag — never use 'main' in production
    files:
      - products/sense360-ceiling-poe-ventiq-roomiq.yaml

substitutions:
  device_name: sense360-bathroom
  friendly_name: "Bathroom Sense360"
```

> Do **not** add your own `wifi:`, `api:`, or `ota:` blocks — the package
> wires those up via `secrets.yaml`.

### 4. Flash

1. **Initial flash:** USB-C, then ESPHome Dashboard → Install → "Plug into this computer".
2. **Future updates:** ESPHome Dashboard → Install → "Wirelessly".

## Configuration Approaches

| Approach | Best For | Complexity |
|----------|----------|------------|
| **WebFlash** | Standard setups, most users | Simplest |
| **Product files (manual path)** | Custom builds, advanced users | Simple |

### Product files — the supported manual path

Pin the complete product YAML at a release tag. This is the one supported
advanced path; the product file resolves to a complete, standalone config
(board packages + base infrastructure + behaviour profiles):

```yaml
packages:
  sense360_firmware:
    url: https://github.com/sense360store/esphome-public
    ref: v1.0.7  # Pin to a release tag — never use 'main' in production
    files:
      - products/sense360-ceiling-poe-ventiq-roomiq.yaml
```

Every catalogued product path lives under `products/sense360-*.yaml`
(declared in [`config/product-catalog.json`](../config/product-catalog.json)).
Customers override only the `device_name` / `friendly_name` substitutions.

### Package-level composition (retired)

The former "individual packages" and "external components only" approaches
— remotely composing `packages/…` files or pulling the component drivers
alone — were retired (the guide that documented them,
`docs/remote-package-consumption.md`, is archived; see
[`archive-index.md`](archive-index.md)). Framework-bearing products cannot
resolve their component code through package-level remote includes, and the
radar drivers are ESPHome built-ins on the pinned ESPHome version. Release
tags keep every historical path, so existing tag-pinned configurations
continue to resolve. The `packages/` layer remains repository-internal
composition — see [`packages/README.md`](../packages/README.md) and the
[system architecture](system-architecture.md).

## System Requirements

- **ESPHome:** 2026.4.5 or newer (the `requirements-dev.txt` pin is the
  source of truth)
- **Home Assistant:** 2024.1.0 or newer (recommended)

## See Also

- [Product taxonomy & compatibility rules](product-taxonomy.md) — board/SKU
  taxonomy, config strings, compatibility rules, lifecycle vs release state.
- [Installation Guide](installation.md) — step-by-step setup.
- [Configuration Reference](configuration.md) — customization options.
- [Release channels](release-channels.md) — stable / preview / experimental
  and what support each receives.

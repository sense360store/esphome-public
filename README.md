# Sense360 ESPHome Packages Repository

## Overview
This repository contains the Sense360-maintained catalog of reusable [ESPHome](https://esphome.io/) packages. Each YAML file captures a repeatable configuration pattern that we apply across our in-store sensors, displays, and control devices. Instead of copying boilerplate between projects, reference the packages directly from this repository and allow ESPHome to merge the fragments at build time.

The repository is structured around the Sense360 naming conventions:

- `base/` – Global defaults such as logging, safe mode, and common substitutions.
- `features/` – Optional capabilities (lighting scenes, energy monitoring, occupancy detection, etc.) that can be layered onto any build.
- `hardware/` – Pin mappings and component definitions for the microcontroller variants we deploy.
- `products/` – Complete device bundles that combine base, hardware, and feature packages into a ready-to-flash configuration.
- `docs/` and `examples/` – Supplemental documentation and reference implementations for Sense360 roll-outs.

Use the sections below to get started quickly, manage secrets safely, and tap into advanced customization patterns for Wi-Fi, API, OTA, and release workflows.

## Quick start (Sense360 devices)
1. Ensure your ESPHome project repository is initialized and has a `secrets.yaml` file for credentials.
2. In the device YAML file, add the Sense360 packages block using the Git-based package syntax:

   ```yaml
   packages:
     sense360_base:
       url: https://github.com/sense360store/esphome-public
       ref: main
       files:
         - base/defaults.yaml
     sense360_hardware:
       url: https://github.com/sense360store/esphome-public
       ref: main
       files:
         - hardware/esp32-s3.yaml
     sense360_features:
       url: https://github.com/sense360store/esphome-public
       ref: main
       files:
         - features/lighting/ambient-sensor.yaml
     sense360_product:
       url: https://github.com/sense360store/esphome-public
       ref: main
       files:
         - products/storefront-lighting.yaml
   ```

3. Override substitutions or add-on components directly inside your project file as needed.
4. Run `esphome run <device>.yaml` to compile and upload the configuration.

ESPHome will fetch the specified files from the Sense360 GitHub repository, merge them in the order listed, and apply your local overrides last.

## Managing secrets
Store credentials (Wi-Fi SSIDs, passwords, API keys) inside your project-level `secrets.yaml`. Reference them from the Sense360 packages or your own YAML using the standard `!secret` syntax:

```yaml
wifi:
  ssid: !secret sense360_wifi_ssid
  password: !secret sense360_wifi_password
```

If a Sense360 package expects a secret, the README inside that package directory will document the key name. Keep `secrets.yaml` out of version control by listing it in `.gitignore`.

## Advanced usage
### Customizing Wi-Fi
Add overrides after the imported packages to change Wi-Fi behavior per device:

```yaml
wifi:
  fast_connect: true
  ap:
    ssid: "Sense360 Fallback"
    password: !secret sense360_fallback_password
```

### Tuning native API access
Sense360 devices use the ESPHome native API for monitoring. Override the API block to adjust encryption or HA discovery options:

```yaml
api:
  encryption:
    key: !secret sense360_api_key
  reboot_timeout: 15min
```

### OTA firmware updates
Configure OTA parameters to align with the Sense360 deployment process:

```yaml
ota:
  password: !secret sense360_ota_password
  safe_mode: true
  reboot_timeout: 10min
```

### Layering additional packages
Combine multiple feature packages by appending them to the same repository reference:

```yaml
packages:
  sense360_features:
    url: https://github.com/sense360store/esphome-public
    ref: main
    files:
      - features/lighting/ambient-sensor.yaml
      - features/energy/power-monitor.yaml
      - features/alerts/storefront-chime.yaml
```

### Pinning releases or tags
For stable deployments, pin Sense360 packages to a release tag rather than `main`:

```yaml
packages:
  sense360_product:
    url: https://github.com/sense360store/esphome-public
    ref: v1.4.0
    files:
      - products/storefront-lighting.yaml
```

Create new tags in the Sense360 repository after validating a release candidate:

1. Update the package files in a branch and merge to `main` once reviewed.
2. Tag the commit: `git tag -a v1.4.0 -m "Sense360 storefront lighting release"`.
3. Push the tag: `git push origin v1.4.0`.
4. Update device projects to reference the new tag in their `packages` blocks.

## Documentation and examples
- Sense360 device examples live in [`examples/`](examples/README.md) and illustrate how to compose product builds.
- Deployment notes, onboarding checklists, and troubleshooting guidance are in [`docs/`](docs/README.md) and the nested Sense360-specific files.
- Hardware reference diagrams reside in [`docs/hardware`](docs/hardware) alongside pinout callouts for each `hardware/` package.

Review these resources when onboarding new stores, customizing features, or creating new Sense360 products.

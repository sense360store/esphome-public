# ESPHome Public Packages Repository

## Overview
This repository hosts a curated collection of reusable [ESPHome](https://esphome.io/) packages that can be consumed directly from GitHub. Each package encapsulates a repeatable configuration pattern so you can share core logic across multiple devices without copying YAML between projects. Import the packages by referencing their raw GitHub URLs from the `packages:` section of your ESPHome configuration, and the ESPHome build system will pull in the components automatically.

## Repository structure
The packages are organized into four top-level directories:

- `base/` – Foundation building blocks that establish default settings, logging, Wi-Fi, and other cross-project conventions.
- `hardware/` – Hardware-specific definitions such as sensor pin mappings, display layouts, or actuator wiring.
- `feature/` – Optional features (for example, environmental monitoring, presence detection, lighting scenes) that can be layered onto a device.
- `product/` – Complete device builds that combine base, hardware, and feature packages into a ready-to-flash configuration.

To include a package, reference the raw file URL inside your ESPHome project:

```yaml
packages:
  base: https://github.com/esphome/esphome-public/blob/main/base/defaults.yaml
  hardware: https://github.com/esphome/esphome-public/blob/main/hardware/d1-mini.yaml
  lighting: https://github.com/esphome/esphome-public/blob/main/feature/lighting/scenes.yaml
  device: https://github.com/esphome/esphome-public/blob/main/product/desk-lamp.yaml
```

Adjust the URLs to match the package files you want to consume. ESPHome merges the YAML fragments in the order you specify, so you can layer reusable logic across devices while keeping overrides inside your project repository.

## Examples and documentation
- Example configurations live in the [`examples/`](examples/README.md) directory and demonstrate how to compose multiple packages within a device project.
- Installation guidance is available in [`docs/installation.md`](docs/installation.md).
- Configuration details and customization tips are covered in [`docs/configuration.md`](docs/configuration.md).
- Troubleshooting steps and common issues are documented in [`docs/troubleshooting.md`](docs/troubleshooting.md).
- API references for custom components and services reside in [`docs/api-reference.md`](docs/api-reference.md).

Use these resources to dive deeper into package usage, extend configurations, or debug problems when integrating the packages into your ESPHome projects.

# Technical reference

These guides are the customer documentation. The engineering documentation
— board references, firmware architecture, and the full YAML source — lives
in the [sense360store/esphome-public](https://github.com/sense360store/esphome-public)
repository on GitHub:

- [Getting started with manual / custom firmware](https://github.com/sense360store/esphome-public/blob/main/docs/getting-started.md)
  — pinning the product YAML from your own ESPHome configuration.
- [Hardware catalog](https://github.com/sense360store/esphome-public/blob/main/docs/hardware-catalog.md)
  — the canonical Sense360 board and SKU reference.
- [System architecture](https://github.com/sense360store/esphome-public/blob/main/docs/system-architecture.md)
  — how the board, bundle, and feature layers compose each product.
- [Support](https://github.com/sense360store/esphome-public/blob/main/SUPPORT.md)
  — where to ask questions and how to report problems.
- [Contributing](https://github.com/sense360store/esphome-public/blob/main/CONTRIBUTING.md)
  — filing issues and opening pull requests.

The entity tables in the product guides are generated mechanically from the
firmware YAML by
[`scripts/generate_product_entity_tables.py`](https://github.com/sense360store/esphome-public/blob/main/scripts/generate_product_entity_tables.py)
and freshness-gated in CI, so they always match the firmware source.

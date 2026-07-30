<!--
Advanced corner (SENSE360-CUSTOMER-DOCS-001 Phase 1 skeleton). The one
place the manual path is documented for customers, per the programme
documentation-authority rule (flashing defers to WebFlash as the
production path; the manual path is documented once, here). Fan-driver
and self-build content stays behind this door with its recorded
warnings; nothing here makes any fan configuration look standard,
recommended or one-click.
-->

# Advanced

Everything on this page is optional. The
[installer](https://sense360store.github.io/WebFlash/) is the supported
path for standard setups.

## Build your own firmware

Advanced users can build and flash the firmware with the ESPHome
toolchain instead of the installer. Pin the complete product file at a
release tag — the product resolves to a full, standalone configuration:

```yaml
packages:
  sense360_firmware:
    url: https://github.com/sense360store/esphome-public
    ref: v1.0.7  # Pin to a release tag — never use 'main' in production
    files:
      - products/sense360-ceiling-poe-ventiq-roomiq.yaml
```

Override only the `device_name` and `friendly_name` substitutions. The
full walkthrough lives in the
[getting-started guide](https://github.com/sense360store/esphome-public/blob/main/docs/getting-started.md).

Self-built firmware is also where connection security lives today: your
own build carries your own secrets, including the Home Assistant API
encryption key, and Home Assistant will ask for that key when it adds
the device. Installer firmware connects without a key.

## Fan drivers and self-build configurations

Fan-driver firmware exists for self-build use behind explicit warnings.
None of it is standard, recommended, or a default, and the mains-voltage
TRIAC configuration in particular requires a competent person and
carries serious electrical risk. If you are considering any of it, read
the warnings in the installer's advanced flow first — they are the
authoritative gate, and this site will not restate or soften them.

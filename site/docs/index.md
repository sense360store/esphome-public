# Sense360 Product Guides

Welcome. These are the customer guides for **Sense360** ceiling-mounted
environmental monitoring devices — ESP32-S3 based ceiling hubs with modular
sensing for presence, comfort, and air quality, designed for Home Assistant.

## Install firmware

The recommended way to install or update firmware is the browser-based
flasher at **[sense360store.github.io/WebFlash](https://sense360store.github.io/WebFlash/)** — no tooling, no
YAML. These guides cover what each product does, the Home Assistant
entities it provides, and how to keep it updated.

[Open the flasher](https://sense360store.github.io/WebFlash/){ .md-button .md-button--primary }
[Browse the product guides](products/index.md){ .md-button }

## The products

| Product | What it senses | Channel |
|---|---|---|
| [Bedroom Bundle (RoomIQ)](products/ceiling-poe-roomiq.md) | Presence, temperature, humidity, light | <span class="s360-badge s360-badge--stable">stable</span> |
| [Air Quality Bundle (AirIQ + RoomIQ)](products/ceiling-poe-airiq-roomiq.md) | Air quality plus room sensing | <span class="s360-badge s360-badge--stable">stable</span> |
| [Bathroom Bundle (VentIQ + RoomIQ)](products/ceiling-poe-ventiq-roomiq.md) | Bathroom air quality, shower and mould-risk detection, plus room sensing | <span class="s360-badge s360-badge--stable">stable</span> |
| [Bathroom Bundle + LED ring (VentIQ + RoomIQ + LED)](products/ceiling-poe-ventiq-roomiq-led.md) | The bathroom product plus an LED indicator ring | <span class="s360-badge s360-badge--preview">preview</span> |

All four are PoE-powered configurations of the Sense360 Core ceiling hub.
Every entity table in these guides is generated directly from the firmware
source in this repository, so the docs cannot drift from what the firmware
actually ships.

!!! info "This site is being built out"
    The product guides are live but still being finalised — sections such as
    placement guidance and LED indicator meanings are marked where owner
    input is pending. See each guide for details.

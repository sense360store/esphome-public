# Bathroom + LED ring (VentIQ + RoomIQ + LED)

<span class="s360-badge s360-badge--preview">preview</span>
&nbsp; Config string: `Ceiling-POE-VentIQ-RoomIQ-LED`

!!! danger "Preview firmware — for testers"
    This configuration ships on the **preview channel**. Preview firmware
    is buildable and installable for testers, but it is **not** the stable
    customer release: expect changes, and be prepared to re-flash the
    stable [Bathroom (VentIQ + RoomIQ)](ceiling-poe-ventiq-roomiq.md)
    firmware if you hit problems. If you are not deliberately testing the
    LED ring, use the stable bathroom product instead.

The [Bathroom (VentIQ + RoomIQ)](ceiling-poe-ventiq-roomiq.md) product
plus the **Sense360 LED** ring — 12 addressable LEDs for ambient status
feedback, with brightness control and a night mode.

## Hardware in this configuration

- Sense360 Core (ceiling hub, ESP32-S3)
- Sense360 PoE PSU (powered over Ethernet, IEEE 802.3af)
- Sense360 VentIQ module (bathroom air-quality sensing)
- Sense360 RoomIQ module (presence + comfort sensing)
- Sense360 LED ring (12 × WS2812B LEDs)

## Install

Flash the firmware from your browser at
[mysense360.com](https://mysense360.com) — preview firmware is
acknowledgement-gated in the flasher: read the warning before installing.

!!! note "Full guide coming"
    Detailed installation, Home Assistant adoption, updating, and recovery
    steps arrive in the next docs update (PRODUCT-GUIDES-001 G2).

## Placement and LED meanings

!!! warning "Guidance being finalised"
    Mounting/placement advice and the meaning of each LED indicator state
    are being finalised and will be added here.

## Home Assistant entities

--8<-- "ceiling-poe-ventiq-roomiq-led-entities.md"

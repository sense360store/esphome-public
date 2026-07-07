# Room sensing (RoomIQ)

<span class="s360-badge s360-badge--stable">stable</span>
&nbsp; Config string: `Ceiling-POE-RoomIQ`

A PoE-powered Sense360 Core ceiling hub with the **RoomIQ** room-sensing
module: mmWave radar presence detection plus temperature, humidity, and
ambient-light comfort sensing. The smallest Sense360 configuration —
suited to bedrooms and living spaces.

## Hardware in this configuration

- Sense360 Core (ceiling hub, ESP32-S3)
- Sense360 PoE PSU (powered over Ethernet, IEEE 802.3af)
- Sense360 RoomIQ module (presence + comfort sensing)

## Install

Flash the firmware from your browser at
[mysense360.com](https://mysense360.com) — select the product and follow
the on-screen steps.

!!! note "Full guide coming"
    Detailed installation, Home Assistant adoption, updating, and recovery
    steps arrive in the next docs update (PRODUCT-GUIDES-001 G2).

## Placement

!!! warning "Guidance being finalised"
    Mounting position, height, coverage, and placement advice for this
    product are being finalised and will be added here.

## Home Assistant entities

--8<-- "ceiling-poe-roomiq-entities.md"

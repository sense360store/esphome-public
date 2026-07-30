<!--
Customer room page: Bedroom (SENSE360-CUSTOMER-DOCS-001 Phase 1 skeleton).
BUILT READY, DELIBERATELY UNPUBLISHED: this page is not in the mkdocs nav
and must not join it until the owner changes the bundle's visibility
(the drift gate pins the nav exclusion). Same fixed spine as bathroom.md.
-->

# Bedroom

Quiet, presence-aware sensing for bedrooms. One ceiling-mounted hub
watches occupancy and comfort, and Home Assistant does the rest.

## What's in the box

| Board | What it does |
|---|---|
| Sense360 Core | The hub. ESP32-S3 brain with connectors for every module. |
| Sense360 RoomIQ | Room sensing: presence, light, temperature, humidity, pressure. |
| Sense360 PoE PSU | Power over your network cable. No wall adapter needed. |

Radar attachment modules are **not included**; the RoomIQ board provides
connectors for them as an optional upgrade.

## Mount it

Ceiling mounting instructions land here.

## Flash it

Use the [Sense360 installer](https://sense360store.github.io/WebFlash/) in
Chrome or Edge on a laptop or desktop:

1. Connect the hub over USB-C and open the installer.
2. Choose the **Bedroom** setup when asked for your room.
3. Follow the on-screen steps; the installer verifies the firmware and
   flashes the device.

## Connect to Home Assistant

Home Assistant discovers the device on your network and asks for the API
key shown during setup. Walkthrough content lands here.

## What you'll see

--8<-- "ceiling-poe-roomiq-entities.md"

## Tune it

Presence tuning guidance lands here. For radar zone shaping, use
[Zone Studio](../zone-studio.md).

## Troubleshoot

Common questions and recovery steps land here; see also the
[help section](../help/index.md).

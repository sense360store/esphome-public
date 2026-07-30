<!--
Customer room page: Bathroom (SENSE360-CUSTOMER-DOCS-001 Phase 1 skeleton).
Fixed page spine — do not reorder or rename the seven H2 sections; the
drift gate (tests/test_customer_docs_site.py) pins them. Factual claims
render from the mirrors (config/sot-commercial-mirror.json,
config/webflash-preset-snapshot.json) and the generated entity tables;
narrative fills in Phase 3; photography placeholders fill in Phase 4.
-->

# Bathroom

Humidity, presence and ventilation-focused sensing for bathrooms, shower
rooms, laundry rooms and utility rooms. One ceiling-mounted hub watches
moisture and occupancy, and Home Assistant does the rest.

<!-- owner-asset:bathroom-hero-photo -->

## What's in the box

| Board | What it does |
|---|---|
| Sense360 Core | The hub. ESP32-S3 brain with connectors for every module. |
| Sense360 RoomIQ | Room sensing: presence, light, temperature, humidity, pressure. |
| Sense360 VentIQ | Bathroom air quality: VOC and NOx trends for ventilation decisions. |
| Sense360 PoE PSU | Power over your network cable. No wall adapter needed. |

Radar attachment modules are **not included**; the RoomIQ board provides
connectors for them as an optional upgrade.

<!-- owner-asset:bathroom-box-contents-flatlay -->

## Mount it

Ceiling mounting instructions land here, with photographs of the mounting
sequence.

<!-- owner-asset:bathroom-mounting-sequence -->

## Flash it

Use the [Sense360 installer](https://sense360store.github.io/WebFlash/) in
Chrome or Edge on a laptop or desktop:

1. Connect the hub over USB-C and open the installer.
2. Choose the **Bathroom** setup when asked for your room.
3. Follow the on-screen steps; the installer verifies the firmware and
   flashes the device.

The installer is the supported path. If you build your own firmware
instead, see the [advanced corner](../advanced/index.md).

## Connect to Home Assistant

Home Assistant discovers the device on your network and asks for the API
key shown during setup. Walkthrough content lands here.

## What you'll see

The entities this device creates in Home Assistant, generated from the
firmware source so this list cannot drift:

--8<-- "ceiling-poe-ventiq-roomiq-entities.md"

## Tune it

Ventilation and presence tuning guidance lands here. For radar zone
shaping, use [Zone Studio](../zone-studio.md).

## Troubleshoot

Common questions and recovery steps land here; see also the
[help section](../help/index.md).

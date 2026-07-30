<!--
Customer room page: Kitchen (SENSE360-CUSTOMER-DOCS-001 Phase 1 skeleton).
BUILT READY, DELIBERATELY UNPUBLISHED: this page is not in the mkdocs nav
and must not join it until the owner changes the bundle's visibility
(the drift gate pins the nav exclusion). Same fixed spine as bathroom.md.
-->

# Kitchen

Air-quality-aware sensing for kitchens. One ceiling-mounted hub watches
air quality and occupancy, and Home Assistant does the rest.

## What's in the box

| Board | What it does |
|---|---|
| Sense360 Core | The hub. ESP32-S3 brain with connectors for every module. |
| Sense360 RoomIQ | Room sensing: presence, light, temperature, humidity, pressure. |
| Sense360 AirIQ | Air quality: CO₂, VOC and NOx trends, gas sensing. |
| Sense360 PoE PSU | Power over your network cable. No wall adapter needed. |

Radar attachment modules are **not included**; the RoomIQ board provides
connectors for them as an optional upgrade.

## Mount it

Ceiling mounting instructions land here.

## Flash it

The installer flow for this room lands here when this page is published.

## Connect to Home Assistant

Home Assistant discovers the device on your network and asks for the API
key shown during setup. Walkthrough content lands here.

## What you'll see

--8<-- "ceiling-poe-airiq-roomiq-entities.md"

## Tune it

Air-quality tuning guidance lands here. For radar zone shaping, use
[Zone Studio](../zone-studio.md).

## Troubleshoot

Common questions and recovery steps land here; see also the
[help section](../help/index.md).

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

--8<-- "room-bedroom-box-contents.md"

Radar attachment modules are **not included**; the RoomIQ board provides
connectors for them as an optional upgrade.

## Mount it

Ceiling mounting instructions land here.

## Flash it

Use the [Sense360 installer](https://sense360store.github.io/WebFlash/) in
Chrome or Edge on a laptop or desktop:

--8<-- "room-bedroom-flash-steps.md"

## Connect to Home Assistant

Home Assistant discovers the device on your network shortly after it
comes online and shows it as a new ESPHome device. Adding it takes one
click — installer firmware connects without an encryption key, and Home
Assistant will show the connection as unencrypted on your local network.
After that, every sensor and control on this page appears as entities on
one device — no manual configuration files needed.

If the device does not appear on its own, add it once by IP address:
Settings, then Devices and services, then Add integration, then ESPHome.

## What you'll see

--8<-- "ceiling-poe-roomiq-entities.md"

## Tune it

Presence behaviour is tunable from Home Assistant. The default
thresholds are engineering defaults — validated tuning guidance lands
here once bench measurements confirm the numbers. For radar zone
shaping, use [Zone Studio](../zone-studio.md).

## Troubleshoot

- **The device is not discovered.** Check it has power (the network cable for PoE) and is
  on the same network as Home Assistant, then try adding it by IP
  address as above.
- **Entities show as unavailable.** The device has lost power or
  network; when it reconnects, the entities recover on their own.
- **You want to start over.** Reflash it with the
  [installer](https://sense360store.github.io/WebFlash/) — flashing
  again is always safe and puts the device back in a known state.

More answers in the [help section](../help/index.md).

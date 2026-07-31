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

--8<-- "room-bathroom-box-contents.md"

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

--8<-- "room-bathroom-flash-steps.md"

The installer is the supported path. If you build your own firmware
instead, see the [advanced corner](../advanced/index.md).

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

The entities this device creates in Home Assistant, generated from the
firmware source so this list cannot drift:

--8<-- "ceiling-poe-ventiq-roomiq-entities.md"

## Tune it

Ventilation and presence behaviour is tunable from Home Assistant.
The default thresholds are engineering defaults — validated tuning
guidance lands here once bench measurements confirm the numbers, and
nothing on this page should be read as a validated calibration today.
For radar zone shaping, use [Zone Studio](../zone-studio.md).

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

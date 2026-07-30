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

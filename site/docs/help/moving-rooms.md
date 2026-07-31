<!--
Help article: moving a device between rooms (SENSE360-CUSTOMER-DOCS-001
Phase 3). Honest about the hardware boundary: the firmware setup
follows the boards inside the unit, so a different room *type* is not
just a reflash if the boards differ. Zone guidance stays linked to
Zone Studio (owned by sense360zones), never duplicated here.
-->

# Move it to another room

A Sense360 unit is not tied to the room it was first set up in. Moving
it takes a few minutes.

## Same kind of room

Moving between similar rooms — one bathroom to another, say — is
mostly physical:

1. Power it down, unmount it, and mount it in the new room.
2. Once it is back online, open Home Assistant and move the device to
   the new Area (Settings, then Devices and services, then the device)
   so dashboards and voice assistants place it correctly. Rename it
   there too if you like.
3. Radar zones are shaped to the old room — redraw them for the new
   layout with [Zone Studio](../zone-studio.md).

If the new room is on a different Wi-Fi network, the device opens its
setup hotspot when it cannot find the old one — follow
[Get it online](get-online.md).

## A different kind of room

Each room's setup matches the sensor boards inside the unit — a
bathroom unit and a kitchen unit carry different boards. Firmware
alone does not change that:

- If the unit has the right boards for the new room, run the
  [installer](https://sense360store.github.io/WebFlash/) and choose the
  new room's setup, then follow the steps above.
- If it does not, the unit will serve the new room as far as its
  boards allow — the firmware setup to flash is the one that matches
  the boards you have, not the room label.

What each board does is described in
[What the boards do](sensor-glossary.md).

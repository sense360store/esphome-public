<!--
Light-ring reference (SENSE360-CUSTOMER-DOCS-001 Phase 2). The controls
table is generated from the LED framework source — never hand-edit it
here; edit the wording map in scripts/generate_customer_docs_blocks.py
and regenerate. The layer narrative below is guidance prose; it claims
no timing, colour values, or bench-verified behaviour.
-->

# The light ring

Some setups include a ring of lights on the ceiling unit. When yours
does, it behaves in layers:

- **Room light.** The base layer — the ring is an ordinary light in Home
  Assistant with colour and brightness.
- **Status indications.** When the status indicator is enabled and the
  room light is off, the ring briefly shows device events, then goes
  idle again. Status never interrupts a room light that is on.
- **Identify.** A flash pattern you trigger on purpose, so you can tell
  which ceiling unit is which.
- **Night mode.** Switches the ring to a low, warm night look. You can
  turn it on yourself, or let it activate automatically when the room
  is dark (or dark and occupied, on setups that sense presence).

## The controls

Generated from the firmware source, so this table always matches the
controls your device actually has:

--8<-- "led-behaviour.md"

The ring's Home Assistant entities appear in your room page's "What
you'll see" section when your setup includes the light ring.

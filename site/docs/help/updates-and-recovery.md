<!--
Help article: updates + factory recovery (SENSE360-CUSTOMER-DOCS-001
Phase 3). Both are the same mechanism — reflashing with the installer —
which the room pages already state is always safe. Claims kept modest
and firmware-true: no update-entity or auto-update claim (the shipped
firmware has none), no bootloader-button claims (never infer hardware
population), and no security claim beyond the shipped posture. Wi-Fi
credentials may or may not survive a reflash depending on the erase
path, so the copy covers both outcomes without asserting either.
-->

# Update or start over

Updating the firmware and putting a misbehaving device back in a known
state are the same, simple action: flash it again with the
[installer](https://sense360store.github.io/WebFlash/).

## Updating the firmware

The device does not update itself, and there is no app. When a new
firmware version is available, run the installer again in Chrome or
Edge on a laptop or desktop, connect the device over USB-C, and choose
your room's setup — the installer flashes the current version.

After an update:

- Home Assistant recognises it as the same device — you do not need to
  remove or re-add anything, and your dashboards and automations keep
  working.
- If the device asks for Wi-Fi again, it opens its setup hotspot —
  follow [Get it online](get-online.md).

## Starting over

Reflashing is also the recovery path. Reach for it when the device
seems stuck, entities never appear, or you simply want a clean start.
Flashing again is always safe and puts the device back in a known
state — a failed or interrupted flash is not permanent, either; just
run the installer again.

1. Connect the hub over USB-C and open the
   [installer](https://sense360store.github.io/WebFlash/).
2. Choose your room's setup and follow the on-screen steps.
3. Get it back on your Wi-Fi if it asks — see
   [Get it online](get-online.md).
4. Home Assistant picks the device back up on its own; entities recover
   once it reconnects.

## If the installer cannot see the device

- Use a data-capable USB-C cable — some charging cables carry no data.
- Try a different USB port, and close other apps that might be holding
  the serial port.
- The installer needs Chrome or Edge on a laptop or desktop; phone and
  tablet browsers cannot flash.

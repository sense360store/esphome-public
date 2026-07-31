<!--
Help article: first-boot Wi-Fi (SENSE360-CUSTOMER-DOCS-001 Phase 3).
Every behavioural claim here traces to the shipped firmware:
packages/base/wifi.yaml (fallback AP + captive_portal; the AP SSID
substitutions all start "S360" — checked across products/), and
docs/security/release-firmware-credential-posture.md (released firmware
ships the setup hotspot OPEN, the API keyless — never claim security
stronger than the shipped firmware provides). The ~1 minute figure is
the ESPHome fallback-AP default timeout; the 192.168.4.1 address is the
standard ESPHome captive-portal address.
-->

# Get it online

Your device talks to Home Assistant over Wi-Fi. On PoE setups the
network cable powers the device — the data still travels over Wi-Fi.
Here is how it learns your network the first time, and how to change it
later.

## First time: the setup hotspot

1. Power the device (plug in the network cable on PoE setups). Give it
   a minute.
2. When it has no Wi-Fi network it can reach, the device opens its own
   setup hotspot: a Wi-Fi network whose name starts with **S360**.
3. On your phone or laptop, join that S360 network. It is an open
   network with no password — it only exists while the device has no
   Wi-Fi of its own, and it disappears once yours is saved.
4. A setup page opens by itself. If it does not, open a browser and go
   to `192.168.4.1`.
5. Pick your home Wi-Fi network, enter its password, and save.

The device joins your network, the setup hotspot goes away, and Home
Assistant can discover it — carry on with the "Connect to Home
Assistant" section of your room page.

## Changing Wi-Fi later

The device remembers the network you gave it. If that network ever
disappears — you renamed it, changed router, or moved house — the
device brings the setup hotspot back on its own after a minute or so.
Join it and enter the new network, same as the first time.

## If the hotspot never appears

- Check the device has power: on PoE setups, the network cable must
  come from a PoE-capable switch or injector, not a plain network port.
- Give it a full minute after power-up — the device tries to find a
  known network before it opens the hotspot.
- If it still does not appear, reflash with the
  [installer](https://sense360store.github.io/WebFlash/) and try again
  — see [Update or start over](updates-and-recovery.md).

# Bathroom Bundle + LED ring (VentIQ + RoomIQ + LED)

<span class="s360-badge s360-badge--preview">preview</span>
&nbsp; Config string: `Ceiling-POE-VentIQ-RoomIQ-LED`

!!! danger "Preview firmware — for testers"
    This configuration ships on the **preview channel**. Preview firmware
    is buildable and installable for testers, but it is **not** the stable
    customer release: it is not hardware verified, it is not recommended,
    and you should expect changes. Be prepared to re-flash the stable
    [Bathroom Bundle (VentIQ + RoomIQ)](ceiling-poe-ventiq-roomiq.md) firmware if
    you hit problems. If you are not deliberately testing the LED ring,
    use the stable bathroom product instead.

The [Bathroom Bundle (VentIQ + RoomIQ)](ceiling-poe-ventiq-roomiq.md) product
plus the **Sense360 LED** ring — 12 addressable LEDs for ambient status
feedback.

**What it does** — everything the stable bathroom product does:

- Shower detection from humidity behaviour, with a post-shower
  ventilation timer.
- Mould-risk tracking and warnings.
- Odour (VOC / NOx) monitoring with ventilation advice and a recommended
  fan speed.
- mmWave radar presence plus temperature, humidity, feels-like, and
  ambient light.

…plus the LED ring, controllable from Home Assistant:

- An **LED Ring** light entity with effects.
- An **LED Brightness** control and a **Night Mode** switch.

Everything is exposed to Home Assistant as ordinary entities — the
[full list](#home-assistant-entities) below is generated directly from the
firmware source, so it always matches what the device actually provides.

## Hardware in this configuration

- Sense360 Core (ceiling hub, ESP32-S3)
- Sense360 PoE PSU (powered over Ethernet)
- Sense360 VentIQ module (bathroom air-quality sensing)
- Sense360 RoomIQ module (presence + comfort sensing)
- Sense360 LED ring (12 × WS2812B LEDs)

See [Specifications](#specifications) for the sensor details.

## Install the firmware

Firmware is installed from your browser — no software to download.

1. Open the flasher at **[sense360store.github.io/WebFlash](https://sense360store.github.io/WebFlash/)**.
2. Connect the device to your computer with a USB-C **data** cable
   (some cables are charge-only).
3. Select this product (config string `Ceiling-POE-VentIQ-RoomIQ-LED`)
   and follow the on-screen steps.

Use Chrome, Edge, or Opera — the flasher needs a browser that can talk to
USB serial devices.

!!! warning "Channel: preview"
    Preview firmware is **acknowledgement-gated** in the flasher — read
    the warning it shows before installing. There is no hardware
    verification and no stable-release support for preview builds;
    problems are best-effort via
    [Issues](https://github.com/sense360store/esphome-public/issues) and
    [Discussions](https://github.com/sense360store/esphome-public/discussions),
    and the expected recovery is re-flashing the stable bathroom firmware.

## Connect to Wi-Fi

The device joins **2.4 GHz** Wi-Fi networks (5 GHz is not supported).
After flashing, get it online in either of two ways:

**Option A — setup network.** Create a temporary Wi-Fi hotspot (your phone
works) named `Sense360_Setup` with password `sense360setup`. The freshly
flashed device joins it automatically. These setup credentials are
deliberately public: they name a temporary network *you* create, and are
not a credential to the device itself.

**Option B — setup hotspot.** If the device can't find a network, it opens
its own setup hotspot named `s360-ceil-poe-ventiq-rm-led FB`. Connect to
it and a setup page appears where you enter your home Wi-Fi name and
password.

## Add to Home Assistant

Home Assistant discovers the device automatically through the ESPHome
integration:

1. In Home Assistant go to **Settings → Devices & Services**.
2. The device appears as a discovered ESPHome device — click **Configure**
   and confirm.
3. Its entities appear prefixed with the device's friendly name
   (firmware default: `Sense360 Ceiling Bathroom LED`).

!!! warning "Security note"
    Browser-installed firmware ships **unprovisioned**: the Home Assistant
    connection is unencrypted and there is no OTA or web password, so
    treat the device as trusted-home-network only. Advanced users who want
    an encrypted API and passwords can build the identical firmware from
    source with their own secrets — see
    [getting started](https://github.com/sense360store/esphome-public/blob/main/docs/getting-started.md).

## Placement and LED meanings

!!! warning "Guidance being finalised"
    Mounting/placement advice and the meaning of each LED indicator state
    are being finalised and will be added here.

## Home Assistant entities

--8<-- "ceiling-poe-ventiq-roomiq-led-entities.md"

## Updating

Preview releases are announced on the
[releases page](https://github.com/sense360store/esphome-public/releases)
(preview builds carry `-preview` tags). To update — or to move back to
the stable bathroom firmware — open
[sense360store.github.io/WebFlash](https://sense360store.github.io/WebFlash/), connect the device over USB,
and install the build you want. If the device doesn't reappear in Home
Assistant afterwards, repeat the [Wi-Fi step](#connect-to-wi-fi).

Advanced users running the firmware through their own ESPHome instead pin
a release tag — see the [Technical reference](../reference.md).

## Factory reset and recovery

The firmware exposes maintenance buttons in Home Assistant (they are in
the entity table above):

- **Restart** — reboots the device.
- **Safe Mode** — reboots into a minimal recovery mode; useful if the
  device is misbehaving after a change.
- **Factory Reset** — erases the device's stored settings (including
  Wi-Fi credentials entered through the setup page) and reboots. It is
  *disabled by default* in Home Assistant — enable it on the device page
  before use.

If the device is unresponsive or you want a truly clean start, use the
**rescue flow** in the flasher: open
[sense360store.github.io/WebFlash](https://sense360store.github.io/WebFlash/), connect over USB, flash the
rescue firmware, then install the firmware you want — for this preview
product, that usually means going back to the stable
[Bathroom Bundle (VentIQ + RoomIQ)](ceiling-poe-ventiq-roomiq.md) build.

## Specifications

| | |
|---|---|
| Hub | Sense360 Core (S360-100) — ESP32-S3 |
| Power | Sense360 PoE PSU (S360-410) — powered over Ethernet, 5 V output |
| Air quality | Sense360 VentIQ (S360-211) — SGP41 VOC/NOx sensor on board; connectors for IR temperature and SPS30 particulate add-ons |
| Room sensing | Sense360 RoomIQ (S360-200) — LD2450 mmWave radar, PIR, SEN0609, LTR-303ALS ambient light, SHT4x temperature/humidity, BMP581 pressure |
| Indicator | Sense360 LED (S360-300) — ring of 12 WS2812B addressable LEDs |
| Wi-Fi | 2.4 GHz |

Full engineering references (pinouts, schematics, board revisions) live on
GitHub — see the
[hardware catalog](https://github.com/sense360store/esphome-public/blob/main/docs/hardware-catalog.md)
and the board documents for the
[Core](https://github.com/sense360store/esphome-public/blob/main/docs/hardware/s360-100-r4-core.md),
[VentIQ](https://github.com/sense360store/esphome-public/blob/main/docs/hardware/s360-211-r4-ventiq.md),
[RoomIQ](https://github.com/sense360store/esphome-public/blob/main/docs/hardware/s360-200-r4-roomiq.md),
[LED ring](https://github.com/sense360store/esphome-public/blob/main/docs/hardware/s360-300-r4-led.md),
and
[PoE PSU](https://github.com/sense360store/esphome-public/blob/main/docs/hardware/s360-410-r4-poe.md).

# Room sensing (RoomIQ)

<span class="s360-badge s360-badge--stable">stable</span>
&nbsp; Config string: `Ceiling-POE-RoomIQ`

A PoE-powered Sense360 Core ceiling hub with the **RoomIQ** room-sensing
module. The smallest Sense360 configuration — suited to bedrooms and
living spaces.

**What it does:**

- Detects presence with mmWave radar, with a confidence score alongside
  the on/off state.
- Measures temperature, humidity, feels-like temperature, and ambient
  light.
- Summarises the room in a comfort score, with plain-language temperature
  and humidity advice.

Everything is exposed to Home Assistant as ordinary entities — the
[full list](#home-assistant-entities) below is generated directly from the
firmware source, so it always matches what the device actually provides.

## Hardware in this configuration

- Sense360 Core (ceiling hub, ESP32-S3)
- Sense360 PoE PSU (powered over Ethernet)
- Sense360 RoomIQ module (presence + comfort sensing)

See [Specifications](#specifications) for the sensor details.

## Install the firmware

Firmware is installed from your browser — no software to download.

1. Open the flasher at **[mysense360.com](https://mysense360.com)**.
2. Connect the device to your computer with a USB-C **data** cable
   (some cables are charge-only).
3. Select this product (config string `Ceiling-POE-RoomIQ`) and follow
   the on-screen steps.

Use Chrome, Edge, or Opera — the flasher needs a browser that can talk to
USB serial devices.

!!! note "Channel: stable"
    This product installs from the **stable** channel — the supported
    customer firmware. If something doesn't work, that's a bug:
    [report it](https://github.com/sense360store/esphome-public/issues).

## Connect to Wi-Fi

The device joins **2.4 GHz** Wi-Fi networks (5 GHz is not supported).
After flashing, get it online in either of two ways:

**Option A — setup network.** Create a temporary Wi-Fi hotspot (your phone
works) named `Sense360_Setup` with password `sense360setup`. The freshly
flashed device joins it automatically. These setup credentials are
deliberately public: they name a temporary network *you* create, and are
not a credential to the device itself.

**Option B — setup hotspot.** If the device can't find a network, it opens
its own setup hotspot named `s360-ceil-poe-roomiq FB`. Connect to it and a
setup page appears where you enter your home Wi-Fi name and password.

## Add to Home Assistant

Home Assistant discovers the device automatically through the ESPHome
integration:

1. In Home Assistant go to **Settings → Devices & Services**.
2. The device appears as a discovered ESPHome device — click **Configure**
   and confirm.
3. Its entities appear prefixed with the device's friendly name
   (firmware default: `Sense360 Ceiling RoomIQ`).

!!! warning "Security note"
    Browser-installed firmware ships **unprovisioned**: the Home Assistant
    connection is unencrypted and there is no OTA or web password, so
    treat the device as trusted-home-network only. Advanced users who want
    an encrypted API and passwords can build the identical firmware from
    source with their own secrets — see
    [getting started](https://github.com/sense360store/esphome-public/blob/main/docs/getting-started.md).

## Placement

!!! warning "Guidance being finalised"
    Mounting position, height, coverage, and placement advice for this
    product are being finalised and will be added here.

## Home Assistant entities

--8<-- "ceiling-poe-roomiq-entities.md"

## Updating

New firmware versions are announced on the
[releases page](https://github.com/sense360store/esphome-public/releases).
To update, open [mysense360.com](https://mysense360.com), connect the
device over USB, and install the latest stable build — the same steps as
the first install. If the device doesn't reappear in Home Assistant
afterwards, repeat the [Wi-Fi step](#connect-to-wi-fi).

Advanced users running the firmware through their own ESPHome instead pin
a release tag — see the
[Technical reference](../reference.md).

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
[mysense360.com](https://mysense360.com), connect over USB, flash the
rescue firmware, then install the product firmware again.

## Specifications

| | |
|---|---|
| Hub | Sense360 Core (S360-100) — ESP32-S3 |
| Power | Sense360 PoE PSU (S360-410) — powered over Ethernet, 5 V output |
| Room sensing | Sense360 RoomIQ (S360-200) — LD2450 mmWave radar, PIR, SEN0609, LTR-303ALS ambient light, SHT4x temperature/humidity, BMP581 pressure |
| Wi-Fi | 2.4 GHz |

Full engineering references (pinouts, schematics, board revisions) live on
GitHub — see the
[hardware catalog](https://github.com/sense360store/esphome-public/blob/main/docs/hardware-catalog.md)
and the board documents for the
[Core](https://github.com/sense360store/esphome-public/blob/main/docs/hardware/s360-100-r4-core.md),
[RoomIQ](https://github.com/sense360store/esphome-public/blob/main/docs/hardware/s360-200-r4-roomiq.md),
and
[PoE PSU](https://github.com/sense360store/esphome-public/blob/main/docs/hardware/s360-410-r4-poe.md).

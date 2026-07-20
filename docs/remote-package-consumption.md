# Remote package consumption (Home Assistant ESPHome)

This guide is the supported way to build Sense360 firmware **remotely** — from a
Home Assistant ESPHome device configuration that pulls this repository through
ESPHome [git packages](https://esphome.io/components/packages.html), without
cloning the repository into Home Assistant and without copying any C++ header by
hand.

> Most customers should use [WebFlash](https://sense360store.github.io/WebFlash/)
> for signed stable firmware. This page is the manual / custom path for advanced
> users. It ships **unsigned** firmware you build yourself.

## Why a special step is needed for framework builds

The Sense360 feature *frameworks* (AirIQ / RoomIQ / VentIQ / LED / Presence)
compile a shared, header-only C++ engine (for example
`include/sense360/airiq_engine.h`) — the exact file the native C++ unit tests
exercise, so tested logic and shipped logic never drift. A repository-local
build finds that header through `esphome: includes:` because the build runs from
`products/`. A **remote** consumer's build runs from *its own* config directory,
so the same include path would resolve to `/config/include/sense360/...` — a file
the package does not deliver — and validation fails with:

```text
Could not find file '/config/esphome/../include/sense360/airiq_engine.h'
```

The fix delivers the shared engine as a normal ESPHome **external component**
(`sense360`, rooted at this repository's `include/sense360/` directory) that
travels with the git package and lands on the build's include path for any
consumer layout. This is the same mechanism the repository already uses for its
radar components. You never create `/config/include`, never download a header,
and the framework's behaviour, entities and thresholds are unchanged.

To consume a framework you pull one small **remote wrapper** (under
`packages/remote/`) that composes the board + framework and wires the `sense360`
component for you.

## Prerequisites

Create a `secrets.yaml` next to your device YAML in `/config/esphome/`:

```yaml
wifi_ssid: "your-wifi"
wifi_password: "your-wifi-password"
# `esphome secrets generate` or the dashboard will create a valid key:
api_encryption_key: "base64-32-byte-key=="
ota_password: "your-ota-password"
```

## Pinning (read before production)

Every example below uses `ref: main` for readability. For anything you flash,
**pin to a release tag** so your build is reproducible, and set the matching
`sense360_remote_ref` substitution so the shared engine is fetched from the same
tag:

```yaml
substitutions:
  sense360_remote_ref: v1.0.0        # match your packages' ref:
packages:
  airiq:
    url: https://github.com/sense360store/esphome-public
    ref: v1.0.0                       # pin — never 'main' in production
    files: [packages/remote/ceiling-airiq.yaml]
    refresh: 1d
```

---

## Example 1 — Core only

The Core board carries no framework engine, so it is consumed directly.

```yaml
substitutions:
  device_name: sense360-core
  friendly_name: "Sense360 Core"
  timezone: "Europe/London"

packages:
  core:
    url: https://github.com/sense360store/esphome-public
    ref: main
    files: [packages/hardware/sense360_core_ceiling.yaml]
    refresh: 1d

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_encryption_key

ota:
  - platform: esphome
    password: !secret ota_password

logger:
  level: INFO
```

## Example 2 — Core + LED

Adds the S360-300 LED ring board (the Room Light). Still no framework engine, so
no extra wiring is needed.

```yaml
substitutions:
  device_name: sense360-core
  friendly_name: "Sense360 Core"
  timezone: "Europe/London"

packages:
  core:
    url: https://github.com/sense360store/esphome-public
    ref: main
    files: [packages/hardware/sense360_core_ceiling.yaml]
    refresh: 1d
  led:
    url: https://github.com/sense360store/esphome-public
    ref: main
    files: [packages/boards/s360-300-led.yaml]
    refresh: 1d

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_encryption_key

ota:
  - platform: esphome
    password: !secret ota_password

logger:
  level: INFO
```

## Example 3 — Core + LED + AirIQ

Adds the canonical AirIQ air-quality service. This is the case that needs the
shared engine. Pull the **AirIQ remote wrapper** — it composes the AirIQ board +
framework and delivers `airiq_engine.h` via the `sense360` external component.
The Core Framework package (`device_framework.yaml`) owns the "AirIQ Module
Status" entity the framework publishes, so it is composed here too.

```yaml
substitutions:
  device_name: sense360-core
  friendly_name: "Sense360 Core"
  timezone: "Europe/London"
  device_version: "custom-remote"

  # Core Framework identity (compile-time facts; adjust freely).
  s360_config_string: "Ceiling-Core-LED-AirIQ"
  s360_hardware_model: "S360-100"
  s360_hardware_revision: "R4"
  s360_capabilities: "core,airiq,led"
  s360_capabilities_human: "Core, AirIQ, LED"
  s360_module_led: "Included"

packages:
  airiq:
    url: https://github.com/sense360store/esphome-public
    ref: main
    files: [packages/remote/ceiling-airiq.yaml]
    refresh: 1d
  core:
    url: https://github.com/sense360store/esphome-public
    ref: main
    files: [packages/hardware/sense360_core_ceiling.yaml]
    refresh: 1d
  core_framework:
    url: https://github.com/sense360store/esphome-public
    ref: main
    files: [packages/base/device_framework.yaml]
    refresh: 1d
  led:
    url: https://github.com/sense360store/esphome-public
    ref: main
    files: [packages/boards/s360-300-led.yaml]
    refresh: 1d

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_encryption_key

ota:
  - platform: esphome
    password: !secret ota_password

logger:
  level: INFO

# MQTT is fully consumer-owned for remote installs. Leave this out to have no
# MQTT, or add a real `mqtt:` block to opt in. `mqtt: null` is a harmless no-op.
mqtt: null
```

`esphome config` validates this, and `esphome compile` builds it, on a clean
Home Assistant ESPHome install — no `/config/include`, no manual header copy.

## Other frameworks (RoomIQ / VentIQ / LED / Presence)

Every framework shares the same engine-delivery mechanism. AirIQ ships a
dedicated wrapper (`packages/remote/ceiling-airiq.yaml`); for any other framework
consumed through git packages, add the shared-engines delivery package **as the
last entry** in your `packages:` map (declaring it last lets it neutralise the
frameworks' repository-local include):

```yaml
packages:
  # ... your board + framework packages ...
  sense360_engines:
    url: https://github.com/sense360store/esphome-public
    ref: main
    files: [packages/remote/sense360-shared-engines.yaml]
    refresh: 1d
```

`packages/remote/sense360-shared-engines.yaml` delivers all shared headers via
the `sense360` component and removes the frameworks' local include, exactly like
the AirIQ wrapper does internally. (RoomIQ / VentIQ / LED / Presence
compositions also pull this repository's radar external component, unchanged.)

## What this does not do

- It does **not** require you to download headers, clone the repository into
  Home Assistant, keep local copies, or run any shell command.
- It does **not** change any framework's behaviour, entities, thresholds, sensor
  mappings, product, release, channel or commercial state — it is a
  packaging/delivery convenience only.
- The engine that ships is the **same single implementation**
  (`include/sense360/*.h`) proven by the native C++ unit tests; nothing is
  duplicated or re-implemented in YAML.

See also: [`docs/getting-started.md`](getting-started.md),
[`examples/custom-with-remote-headers.yaml`](../examples/custom-with-remote-headers.yaml)
(fully custom device using individual pinned headers).

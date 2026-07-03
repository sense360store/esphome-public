# Improv Serial for browser device identification: Ethernet compatibility finding

Status: Phase 0 discovery and compile validation complete. Hardware bench validation outstanding, owner gated.

Branch: `feat/improv-serial`. ESPHome version used for all evidence below: 2026.4.5, the version pinned by `ESPHOME_VERSION` in `.github/workflows/firmware-build-release.yml`.

## Why this exists

WebFlash sets `improv: true` and `new_install_improv_wait_time: 15` on every manifest, but this firmware implemented zero Improv Serial before this branch. There was no `improv_serial` or `esp32_improv` component anywhere in the tree. After each flash the browser waited 15 seconds for an Improv handshake that never arrived, and it could never identify a running device, so it always offered a fresh install and never a clean update. This branch adds the firmware side fix and this document records the empirical Ethernet compatibility finding that decided how.

## The premise that had to be tested

The working assumption was that the WebFlash shipped configs are the Ceiling-POE family, that they use `ethernet:`, and that they have no `wifi:`. If that were true, ESPHome's `improv_serial` component would be unusable on them, because Improv Serial exists to provision WiFi credentials.

That premise is false in this tree. "POE" in the Sense360 product names refers to the S360-410 PoE PSU power board, which is power delivery only. The PoE PSU board package (`packages/boards/s360-410-poe-psu.yaml`) binds no network component at all; it emits diagnostic template sensors about the power source. Networking on every shipped config is WiFi.

Evidence, from the current tree:

1. All six rows in `config/webflash-builds.json` resolve through `products/webflash/*.yaml` wrappers to bundles under `products/bundles/`:
   `Ceiling-POE-VentIQ-RoomIQ`, `Ceiling-POE-VentIQ-RoomIQ-LED`, `Ceiling-POE-AirIQ-RoomIQ`, `Ceiling-POE-RoomIQ`, `Ceiling-POE-RoomIQ-LED`, `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`.
2. Every one of the sixteen bundles in `products/bundles/`, including every Ceiling-POE bundle, includes `base_wifi: !include ../../packages/base/wifi.yaml`. None of them includes an `ethernet:` component.
3. The only entry point in the tree with a real `ethernet:` block is `products/sense360-poe.yaml` (W5500 Ethernet controller, via `packages/hardware/sense360_core_poe.yaml` and `packages/base/complete_ethernet.yaml`). It is not in the WebFlash build matrix.

## The pivotal test and its results

Both directions were tested empirically through the dev harness (`dev/*.local.yaml` bench device files, gitignored, with `improv_serial:` in the dev overlay during iteration), using `esphome 2026.4.5`.

### Ethernet only entry point: improv_serial does not validate

Adding `improv_serial:` to `products/sense360-poe.yaml` (the true Ethernet only config) fails ESPHome config validation:

```
Failed config

improv_serial: [source dev-overlay.yaml:23]

  Component improv_serial requires component wifi.
  {}
```

The blocking requirement is declared in the component itself: `esphome/components/improv_serial/__init__.py` sets `DEPENDENCIES = ["logger", "wifi"]`. This is a hard dependency, not a conflict with `ethernet:`. Firmware side Improv Serial is not viable on a config that has no `wifi:` component, and no `wifi:` block may be added to an Ethernet product to work around it.

Consequence: `packages/base/wifi.yaml` is the correct shared layer for `improv_serial:`, and `packages/base/logging.yaml` would be the wrong one, because `packages/base/complete_ethernet.yaml` includes `logging.yaml` and would drag `improv_serial` into Ethernet configs where it cannot validate.

### WebFlash shipped entry points: improv_serial validates and composes cleanly

With `improv_serial:` promoted into `packages/base/wifi.yaml`, all 37 entry points under `products/`, `products/webflash/`, and `products/compile-only/` pass `esphome config` with exit 0. The resolved output confirms:

* All 36 WiFi bearing entry points, including every WebFlash shipped target, resolve `improv_serial: {}`.
* The Ethernet only `products/sense360-poe.yaml` resolves without any `improv_serial` block, because it never includes `wifi.yaml`. It is unchanged by this branch.

Two further constraints from the component's final validation were checked and pass on the shipped configs:

* `improv_serial` requires logger `baud_rate` not 0. The shared logger (`packages/base/logging.yaml`) resolves to `baud_rate: 115200`.
* On ESP32-S3, `improv_serial` rejects `hardware_uart: USB_CDC`. The shipped configs do not set `hardware_uart`, and ESPHome's default for ESP32-S3 is `USB_SERIAL_JTAG`, which is accepted. `USB_SERIAL_JTAG` is the S3's native USB interface, the same link a Web Serial browser session uses to flash the Core, so Improv Serial answers on the port the browser is already connected to.

## What the device reports over Improv Serial

On a GET_DEVICE_INFO request the ESPHome implementation (`improv_serial_component.cpp`, `build_version_info_()`) returns four strings. Because the Core board package (`packages/hardware/sense360_core_ceiling.yaml`) sets an `esphome: project:` block, the project branch is taken:

| Field | Source | Value on shipped ceiling configs |
| --- | --- | --- |
| firmware | `ESPHOME_PROJECT_NAME` | `sense360.ceiling` |
| version | `ESPHOME_PROJECT_VERSION` | `1.0.0` |
| chip family | `ESPHOME_VARIANT` | `ESP32-S3` |
| device name | `App.get_name()` (the `device_name` substitution) | per config, for example `s360-ceil-poe-ventiq-roomiq` |

Two caveats for same firmware detection in WebFlash:

* `firmware` and `version` come from the shared Core project block, so they identify a Sense360 ceiling device but do not distinguish config strings, and the project version is a static `1.0.0`, not the artifact version.
* `device name` is the bundle's `device_name` substitution default, which is distinct per config string in the WebFlash built binaries, but a customer who compiles their own config can override it.

## Compile validation

`esphome compile` could not complete in the sandboxed environment where this branch was authored: PlatformIO's pinned platform download (`github.com/pioarduino/platform-espressif32` release asset) is blocked by the session's egress policy (HTTP 403 at the proxy). Config validation, code generation entry, and every repo validator (`tests/validate_configs.py`, `tests/test_product_substitutions.py`, `scripts/check_dev_harness_guard.py`, yamllint) pass locally. Full compile proof runs through the repository's own hosted compile lane, `.github/workflows/compile-only.yml` dispatched with `compile_mode=full` on this branch, which compiles every target in `config/compile-only-targets.json` including all WebFlash shipped targets. The dispatch result is recorded in the PR for this branch.

## Conclusion

Case A, with a corrected premise. The WebFlash shipped Ceiling-POE configs are WiFi based (PoE is power only), so firmware side Improv Serial is viable on them and is now provided by `improv_serial:` in `packages/base/wifi.yaml`, which every shipped bundle inherits. The Ethernet incompatibility is real but only affects `products/sense360-poe.yaml`, which is outside the WebFlash matrix and stays without Improv.

Handoff to Part 2 (WebFlash manifest correctness): firmware now reports device information over Improv Serial once new binaries are released and imported. WebFlash keeps `improv: true` and can add same firmware detection matching the reported fields above (`sense360.ceiling`, project version `1.0.0`, `ESP32-S3`, per config `device_name`). No manifest should claim Improv support until a release built from this source is imported; until then the 15 second wait remains dead time on existing binaries.

## Outstanding, owner gated

* Hardware bench validation (Phase 3 of the loop): flash a bench device from this branch through the dev harness and confirm a Web Serial browser session (web.esphome.io or a local WebFlash serve) reads the device information fields above. No physical device was reachable from the environment that produced this branch. Until an owner records that proof, browser identification is compile validated only.
* A PoE hardware confirmation specifically (a Ceiling-POE assembled unit, S360-410 powered) remains outstanding for the same reason.
* New signed binaries require the normal release process before WebFlash can rely on any of this. This branch changes source only.

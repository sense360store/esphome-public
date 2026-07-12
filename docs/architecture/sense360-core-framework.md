# Sense360 Core firmware framework (CORE-FRAMEWORK-001)

**Type:** Structural firmware foundation. This document describes the shared
device framework composed by every production bundle. It changes no product
lifecycle, commercial state, release declaration, WebFlash surface, or SOT
programme state, and it claims **no hardware, bench, compliance or safety
proof** — firmware-composition proof only (standing invariant: *no false
proof*, [`docs/standing-invariants.md`](../standing-invariants.md)).

Machine-readable source of truth:
[`config/core-framework.json`](../../config/core-framework.json) (docs
describe; `config/` decides). Enforced by
[`tests/test_core_framework.py`](../../tests/test_core_framework.py) and
[`tests/test_core_framework_doc.py`](../../tests/test_core_framework_doc.py).
Implementation:
[`packages/base/device_framework.yaml`](../../packages/base/device_framework.yaml).

## Purpose

Every Sense360 product needs the same non-module firmware surface: device
identity, firmware information, capability reporting, module presence,
diagnostics, and a device-health summary — with consistent Home Assistant
naming, entity categories, icons and disabled-by-default policy. Before this
framework, that surface lived partly in the Core board package, partly in
per-bundle `text_sensor:` blocks, and partly nowhere.

`packages/base/device_framework.yaml` is the single reusable package that
provides this surface. Each bundle under `products/bundles/` includes it
**exactly once** and declares its own compile-time facts through `s360_*`
substitutions.

**One declared gap:** `Ceiling-POE-FanPWM` is deferred
(`framework_included: false` in the contract). Its bundle is pinned
package-identical to the native full-compile-validated compile-only
skeleton (`S360-311-NATIVE-FANPWM-COMPILE-001`,
`tests/test_pwm_product_readiness.py`); adding the framework would break
that identity and silently invalidate the recorded compile evidence. The
include lands in a follow-up once that lane re-records. Every other bundle
(15 of 16) composes the framework now. Nothing is copy/pasted per product; the design supports
ceiling compositions today and any future authoritative mount, and it works
for USB, PoE and AC-powered compositions because power is just a declared
capability.

Module behaviour (Presence fusion, LED effects, AirIQ calculations, VentIQ
fan logic, RoomIQ comfort scoring) is explicitly **out of scope**; those
arrive in module-specific PRs that build on this contract.

## Shared entities

All framework entities are `entity_category: diagnostic` text sensors with
stable `s360_`-prefixed internal IDs. "Default" below is whether the entity
is enabled by default in Home Assistant.

| Entity ID | Name | Default | Value source |
|---|---|---|---|
| `s360_device_health` | Device Health | enabled | boot warm-up window (see below) |
| `s360_product_configuration` | Product Configuration | enabled | `s360_config_string` (WebFlash config string) |
| `s360_hardware_model` | Hardware Model | enabled | `s360_hardware_model` (catalog SKU, e.g. `S360-100`) |
| `s360_hardware_revision` | Hardware Revision | enabled | `s360_hardware_revision` (catalog rev, e.g. `R4`) |
| `s360_firmware_version` | Firmware Version | enabled | `s360_firmware_version` (defaults to `${device_version}`) |
| `s360_installed_capabilities` | Installed Capabilities | enabled | `s360_capabilities_human` |
| `s360_firmware_channel` | Firmware Channel | disabled | `s360_firmware_channel` (see channel note) |
| `s360_firmware_source` | Firmware Source | disabled | `s360_firmware_source` (repo identifier) |
| `s360_capability_ids` | Capability IDs | disabled | `s360_capabilities` (machine-readable) |
| `s360_module_status_roomiq` | RoomIQ Module Status | disabled | `s360_module_roomiq` |
| `s360_module_status_airiq` | AirIQ Module Status | disabled | `s360_module_airiq` |
| `s360_module_status_ventiq` | VentIQ Module Status | disabled | `s360_module_ventiq` |
| `s360_module_status_presence` | Presence Module Status | disabled | `s360_module_presence` |
| `s360_module_status_led` | LED Module Status | disabled | `s360_module_led` |
| `s360_module_status_fan_control` | Fan Control Module Status | disabled | `s360_module_fan_control` |
| `s360_last_restart_reason` | Last Restart Reason | disabled | ESPHome `debug` reset reason |

Uptime, WiFi signal strength, IP address, SSID, MAC address, ESPHome
version, internal temperature and the restart / safe-mode / factory-reset
buttons are **already provided by the Core board package**
(`packages/hardware/sense360_core_ceiling.yaml` via
`packages/boards/s360-100-core-*.yaml`) and are deliberately not duplicated
by the framework. MAC address remains a diagnostic entity under existing
repository policy. No credential, key, password or provisioning material is
ever exposed — enforced by test.

**Firmware channel note.** The release channel (stable / preview /
experimental) is derived from the release tag by
`firmware-build-release.yml` at build time, not by the YAML, so the YAML
cannot honestly hard-code it. `s360_firmware_channel` therefore defaults to
`unknown` and its entity is disabled by default; a later release-pipeline
slice may inject the real channel with
`esphome compile -s s360_firmware_channel <channel>`. Until then the entity
reports `unknown` rather than a fabricated value.

## Entity naming

Rules for shared entities (module PRs must follow the same rules for new
shared-surface entities):

* **No `${friendly_name}` / `${device_name}` prefix.** ESPHome sets
  `esphome.friendly_name`, so Home Assistant already prefixes the device
  name. Legacy entities that embed the prefix are kept for backwards
  compatibility, but new shared entities never add it.
* **Product-facing words, consistent title case** — "Device Health",
  "Firmware Version", "Hardware Model", "Hardware Revision",
  "Installed Capabilities", "RoomIQ Module Status", "Last Restart Reason".
* **No raw component IDs, no unexplained abbreviations, no developer-only
  jargon** in entity names.
* **Stable internal IDs** (`s360_*`) that never depend on the user-facing
  display text — display text may be refined; IDs may not.

## Diagnostic verbosity policy

Default-enabled entities are limited to genuinely useful operational
information (health, configuration, hardware identity, firmware version,
installed capabilities). Technical internals are **disabled by default**:
firmware channel and source, the raw machine-readable capability list,
every per-module status internal, and the last restart reason. The ESPHome
version, MAC address and SSID text sensors pre-date this framework in the
Core board package and keep their current behaviour for backwards
compatibility. No entity is created merely because a value exists
internally.

## Capability model

Stable machine-readable capability identifiers (never renamed once shipped;
extend by addition only — registry in
[`config/core-framework.json`](../../config/core-framework.json)):

| ID | Kind | Hardware | Meaning |
|---|---|---|---|
| `core` | platform | S360-100 | Core hub board; present in every composition |
| `power_poe` | power | S360-410 | PoE PSU composition |
| `power_usb` | power | — | USB-powered composition (no PSU module board) |
| `roomiq` | module | S360-200 | RoomIQ comfort sensing |
| `airiq` | module | S360-210 | AirIQ air quality |
| `ventiq` | module | S360-211 | VentIQ bathroom air quality |
| `presence` | module | S360-200 | Presence sensing carried by the RoomIQ board |
| `led` | module | S360-300 | LED ring indicator |
| `fan_relay` | module | S360-310 | Relay fan driver (experimental lane) |
| `fan_pwm` | module | S360-311 | PWM fan driver |
| `fan_dac` | module | S360-312 | 0–10 V fan driver |
| `fan_triac` | module | S360-320 | TRIAC fan driver (experimental self-build mains lane) |

Each bundle declares `s360_capabilities` (comma-separated IDs) and
`s360_capabilities_human` (display list). Tests enforce that the declaration
matches the config-string tokens, the entry in `config/core-framework.json`,
and the module declarations in `config/product-catalog.json` — a
configuration without a module can never report that module as installed.
Future expansion capability is handled by adding new IDs to the registry
when (and only when) authoritative hardware exists; no speculative hardware
is invented.

## Compile-time capability vs runtime state

The framework distinguishes three layers and implements only the first:

1. **Compiled capability** (implemented): what the firmware composition
   contains. Declared by bundle substitutions, validated against the
   catalogs. This is what every framework entity reports today.
2. **Detected hardware** (not implemented): runtime discovery of a module on
   the bus. No runtime autodetection is currently proven, so the framework
   never labels a value as "detected".
3. **Available / healthy module** (reserved): runtime health from a real
   supported signal (successful sensor update, component status,
   communication success, explicit availability state). Arrives with the
   module-specific PRs.

## Module status contract

Module status entities publish exactly one of:

* **Not included** — the module's packages are not part of this compiled
  composition. Normal state for an optional module; never a fault.
* **Included** — compile-time presence only: the module's packages are
  compiled into this firmware. **Not** a health, availability, detection or
  hardware claim — a module is never marked Available solely because its
  package compiled.

Reserved runtime values, defined now so module PRs converge on one
vocabulary (meanings in
[`config/core-framework.json`](../../config/core-framework.json)):

* **Initialising** — present, inside its startup warm-up window.
* **Available** — present and confirmed working by a real supported signal.
* **Degraded** — responding, but part of its function impaired or stale.
* **Unavailable** — expected but not responding after warm-up.
* **Fault** — explicit error condition; never used for a merely absent
  module.

The framework must not emit any reserved value until a module-specific PR
wires a real signal — enforced by test.

## Overall device health

`Device Health` publishes:

* **Starting** — inside the boot warm-up window
  (`s360_health_warmup_seconds`, default 120 s).
* **Healthy** — warm-up complete and no negative signal exists.

Inputs that currently drive the summary: **the boot warm-up window only.**
Reserved values — **Degraded**, **Fault**, **Safe mode** — and reserved
inputs (per-module runtime health, safe-mode/recovery state, stale-data
detection) are documented in the contract file and arrive with later module
PRs. Health is never fabricated: the summary only ever reflects signals that
genuinely exist.

Aggregation rules for later module PRs (documented now, implemented then):
one Degraded/Unavailable included module ⇒ device **Degraded**; an explicit
critical fault ⇒ **Fault**; absent optional modules never affect the
summary; warm-up suppresses negative transitions.

## Availability rules

The shared availability pattern the framework establishes (and module PRs
must preserve):

* one failed module must not make unrelated modules unavailable — module
  status is per-module, and aggregation happens only in Device Health;
* an optional module that is absent is `Not included`, never a fault;
* a detected-but-failing module maps to `Degraded` or `Unavailable`, not to
  device-wide failure;
* startup warm-up (`Starting` / `Initialising`) must not immediately produce
  a false fault;
* stale sensor data (module present, data old) must be distinguished from a
  missing module (`Not included`) — stale-data detection is a reserved
  input.

## Extension rules for module PRs

A module-specific PR that adds runtime health must:

1. keep every existing `s360_*` entity ID and substitution key stable;
2. drive its module-status entity from a **real supported signal** and only
   then start using the reserved values;
3. never mark its module Available from compilation alone;
4. extend `config/core-framework.json` (values, inputs) in the same PR and
   keep `tests/test_core_framework.py` green;
5. leave other modules' status and the compile-time capability declarations
   untouched;
6. add new capabilities by addition only — existing IDs are never renamed or
   removed.

## Backwards compatibility

This foundation is **strictly additive**: no existing entity is renamed,
removed or recategorised.

* Legacy prefixed entities (`${friendly_name} Product SKU`,
  `${friendly_name} Firmware Version`, `${friendly_name} WebFlash Config` in
  the bundles, plus the board-package system sensors) keep their exact names
  and IDs. Customers' existing Home Assistant entity IDs do not change.
* The framework's `Firmware Version` intentionally coexists with the legacy
  `${friendly_name} Firmware Version` text sensor (different entity name and
  object ID); both report `device_version`. A future deprecation of the
  legacy entity would be a separate, explicitly-documented breaking change —
  not part of this PR.
* Compile-only skeletons (`products/compile-only/`) and the provisioning
  bench harness (`tests/bench/`) do **not** include the framework, so they
  cannot be mistaken for (or promoted to) customer products.
* Release declarations are untouched: `config/webflash-builds.json` rows,
  channels, versions and artifact names are byte-identical.

## Test expectations

* [`tests/test_core_framework.py`](../../tests/test_core_framework.py) —
  contract tests: stable/unique entity IDs, naming convention (no
  device-name duplication, no raw IDs as display names), diagnostic entity
  categories, disabled-by-default policy, no secret material, capability
  declarations vs config-string tokens vs `config/product-catalog.json`,
  module flags vs capabilities, absent-module-is-never-a-fault, reserved
  values never emitted, framework isolation (bundles only), no duplicate
  entity names/IDs across every resolved bundle composition, and
  release-matrix shape regression.
* [`tests/test_core_framework_doc.py`](../../tests/test_core_framework_doc.py)
  — this document and the roadmap entry stay in sync with the contract.
* `esphome config` (and the hosted compile lanes) remain the compile-time
  source of truth for the representative product matrix.

No hardware validation is claimed by any of these tests; simulation of the
runtime health contract beyond compile-time facts is deliberately deferred
to the module PRs that implement real signals.

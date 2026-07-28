# Sense360 external-component foundation (SENSE360-CANONICALISATION-001 PR 08)

**Canonical id:** `SENSE360-CANONICALISATION-001` PR 08
**Type:** Architecture foundation + machine-enforced conventions.
This document records the ESPHome external-component architecture the PR 09
to PR 12 domain migrations build on. It changes no release, channel, WebFlash
or commercial state, and claims no hardware, bench or compliance proof.

## What PR 08 establishes

1. **`components/sense360/` is the foundation component.** It ships the
   canonical header-only logic engines (the exact files exercised by the
   native deterministic suite in [`tests/unit/`](../../tests/unit/)) and the
   identity schema foundation. It declares **no entities, pins, buses or
   platforms** — enforced by
   [`tests/test_external_components.py`](../../tests/test_external_components.py).
2. **The former `include/sense360/` delivery hack is replaced.** The
   REMOTE-PACKAGE-HEADER-RESOLUTION-001 component existed only to deliver
   headers to remote consumers from a non-standard directory
   (`path: include`). PR 08 moved the headers and the component into the real
   `components/` tree alongside the radar components: one delivery mechanism,
   one directory convention, `path: components` everywhere. The `include/`
   tree is deleted and pinned deleted; release tags keep the historical path
   for tag-pinned consumers (the v1.0.0-pinned
   [`examples/custom-with-remote-headers.yaml`](../../examples/custom-with-remote-headers.yaml)
   per-file fetches stay valid at their tag).
3. **The component manifest.**
   [`config/external-components.json`](../../config/external-components.json)
   declares every directory under `components/` with role, origin, provenance
   and a named disposition owner. Both directions are guard-tested: no
   undeclared component directory, no dangling manifest row.
4. **The no-fork rule, machine-enforced.** Raw sensor communication uses
   built-in ESPHome drivers wherever one exists. Sense360 product behaviour
   lives in the shared engines and the coming domain components — never in a
   forked copy of an upstream sensor driver. A vendored driver directory is
   permitted only with a provenance row in the manifest and a named
   disposition owner (the radar trio is owned by PR 10; `mics_stm8` /
   `sfa40` by PR 11, with OD-SOT-008 staying open for the SFA40).
5. **The common runtime contract.**
   [`components/sense360/sense360_runtime.h`](../../components/sense360/sense360_runtime.h)
   canonicalises the rules every engine already follows — one caller-supplied
   `now_ms` clock, rollover-safe unsigned interval arithmetic, explicit
   `begin`, fail-safe defaults, header-only single implementation — and
   provides the shared helpers (`elapsed_ms`, `interval_elapsed`) pinned by
   [`tests/unit/test_sense360_runtime.cpp`](../../tests/unit/test_sense360_runtime.cpp).
6. **The schema conventions.** The foundation schema accepts optional
   `board_sku` (validated against the canonical
   [`config/hardware-catalog.json`](../../config/hardware-catalog.json) SKU
   axis; the component carries a pinned literal because a consumer build
   cannot read repository config, and the guard test keeps the literal equal
   to the catalog) and `config_string` (the canonical firmware-configuration
   axis). Both surface as compile-time defines only — a compile-time
   declaration is never a hardware-population claim.

## Delivery model

```yaml
external_components:
  - source:
      type: git
      url: https://github.com/sense360store/esphome-public
      ref: <release-tag>          # pin to a tag for reproducible builds
      path: components
    components: [sense360]
    refresh: 1d

sense360:                          # loads the component; delivers the engines
```

The former `esphome: includes:` local-include mechanism is fully retired:
every framework runs on its domain component (RoomIQ under PR 09, Presence
under PR 10, AirIQ / VentIQ under PR 11, LED under PR 12 — the last local
include and its header co-location hazard class went with it), and engine
delivery comes from the `sense360` foundation component the domain
components auto-load. The remote wrappers under
[`packages/remote/`](../../packages/remote/) fetch the needed components
from the git source, so exactly one copy of each header is compiled in
either mode and no `!remove` workaround remains. The consumer-side proof is
[`tests/test_remote_package_consumer.py`](../../tests/test_remote_package_consumer.py).

## Migration map (complete — every domain landed)

| PR | Domain component | Owns |
|----|------------------|------|
| PR 09 | `sense360_roomiq` | compensation, vapour-pressure logic, freshness, calibration, canonical publication |
| PR 10 | `sense360_presence` | PIR + radar fusion; the vendored radar trio's disposition |
| PR 11 | `sense360_airiq` / `sense360_ventiq` | air-quality domains; `mics_stm8` / `sfa40` disposition (OD-SOT-008 open) |
| PR 12 | `sense360_led` | LED domain; Relay / PWM / DAC advanced-path reconciliation |

Each migration replaces YAML-lambda logic with component code **only after
equivalence tests**, preserves stable customer entities, and deletes the
superseded implementation in the same PR (no dead simulated paths).

## Honesty limits

Compile, config and native-simulation success is firmware-build proof of
buildability only — never hardware, bench, compliance, safety or commercial
proof. The identity defines are compile-time declarations, never hardware
autodetection. Nothing in PR 08 changes what ships:
[`config/webflash-builds.json`](../../config/webflash-builds.json) remains the
sole release-eligibility authority (ESP-007) and Release-One
(`Ceiling-POE-VentIQ-RoomIQ`) remains the production stable customer baseline.

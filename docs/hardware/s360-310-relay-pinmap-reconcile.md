# S360-310 Relay Pin-Map Reconcile (S360-310-RELAY-PINMAP-RECONCILE-001)

## Status

**Status: reconciled at the package / substitution layer; release and
WebFlash stay disabled.** This document is the
`S360-310-RELAY-PINMAP-RECONCILE-001` record. It reconciles the relay
drive net between the canonical `S360-100-R4` Core schematic / connector
pin map and the firmware package defaults, and pins the result against
future drift with [`tests/test_relay_pinmap_reconcile.py`](../../tests/test_relay_pinmap_reconcile.py).

It is **documentation + tests only**. It does **not**:

- enable WebFlash for any FanRelay-bearing config or flip any
  `webflash_build_matrix`;
- add a release artifact, an `artifact_name`, a tag, or a checksum;
- publish firmware or add an entry to
  [`config/webflash-builds.json`](../../config/webflash-builds.json);
- promote `S360-310` `schematic_status` beyond `cataloged_unverified`
  in [`config/hardware-catalog.json`](../../config/hardware-catalog.json);
- claim hardware stability, compliance certification, or safety for
  arbitrary mains installation;
- resolve the module-side silkscreen / harness / `K1` BOM / bench
  evidence still owed under `S360-310-BENCH-001`.

## The historical mismatch

The relay drive net disagreed across three layers when the S360-310
documentation first landed:

| Layer | Source | Historical value |
|---|---|---|
| Core schematic / connector pin map | [`s360-100-core-connector-pin-map.md` § J4](s360-100-core-connector-pin-map.md#j4--relay-module-connector-3-pin) | `Relay` on `IO3`, `J4` pin 2 |
| ceiling Core abstract package | [`sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml) | `relay_pin: GPIO4` (pre-001A) |
| generic Core abstract package | [`sense360_core.yaml`](../../packages/hardware/sense360_core.yaml) | `relay_pin: GPIO10` (pre-001A) |

`IO4` on `S360-100-R4` is `SEN0609_RX` (RoomIQ radar UART), so the
historical `GPIO4` binding actively conflicted with another net; the
generic `GPIO10` binding matched nothing schematic-backed.

## Canonical decision

**The canonical relay GPIO for `S360-100-R4` is `IO3` (== `GPIO3`),
`J4` pin 2.**

This is **proven**, not assumed. `IO3` is the only schematic-backed
source for the relay drive net in the repository:

- [`s360-100-core-connector-pin-map.md` § J4](s360-100-core-connector-pin-map.md#j4--relay-module-connector-3-pin)
  records `J4` pin 2 = `Relay` = `IO3`, `schematic-backed`.
- [`s360-100-r4-core.md`](s360-100-r4-core.md) records the pin-assignment
  row `IO3 → Relay (J4 Relay module gate)` and the fan/driver-output row
  `Relay ↔ J4 Relay module (3-pin)` originating at ESP32 `IO3`.
- [`s360-310-module-pinmap.md`](s360-310-module-pinmap.md) records the
  module-side `J2` pin 2 = `Relay` = `IO3`, net-by-net matched to Core
  `J4`.

The module-side schematic ([`schematics/S360-310-R4.pdf`](schematics/S360-310-R4.pdf))
confirms the `Relay` input topology (`J2` pin 2 → `R1` 1 kΩ → `Q1`
MMBT3904 base, `R2` 10 kΩ pull-down, `D1` flyback, `K1` coil on `+5V`)
but does **not** itself name a Core-side ESP32 GPIO — the GPIO identity
comes from the Core schematic above.

## Reconciliation outcome

The substitution-layer disagreement was already closed before this
slice:

- `CORE-ABSTRACT-BUS-001C` freed `GPIO3` (moved `ALS_INT` to `GPIO47`
  and the expander interrupt to `GPIO17`).
- `CORE-ABSTRACT-BUS-001A` rebound `relay_pin` from `GPIO4` / `GPIO10`
  to the schematic-correct `GPIO3` in the five non-voice Core abstract
  packages.
- `PACKAGE-RELAY-001` reconciled
  [`packages/expansions/fan_relay.yaml`](../../packages/expansions/fan_relay.yaml)
  at the package layer. After FW-COMPILE-RELAY-FULL-FIX-001 the package
  exposes `fan_relay_switch` as a `template` switch that proxies the Core
  `main_relay` and names no GPIO; the Core `main_relay` `switch.gpio` on
  `pin: ${relay_pin}` is the sole GPIO owner.

The current state, confirmed by this slice:

| Layer | File | Value | Agrees with `IO3`? |
|---|---|---|---|
| Core connector pin map | [`s360-100-core-connector-pin-map.md`](s360-100-core-connector-pin-map.md) | `Relay` = `IO3` (`J4` pin 2) | ✅ |
| Core reference | [`s360-100-r4-core.md`](s360-100-r4-core.md) | `IO3 → Relay` | ✅ |
| Module pinmap | [`s360-310-module-pinmap.md`](s360-310-module-pinmap.md) | `Relay` = `IO3` (`J2`/`J4` pin 2) | ✅ |
| generic Core abstract | [`sense360_core.yaml`](../../packages/hardware/sense360_core.yaml) | `relay_pin: GPIO3` | ✅ |
| ceiling Core abstract | [`sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml) | `relay_pin: GPIO3` | ✅ |
| mapping Core abstract | [`sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml) | `relay_pin: GPIO3` | ✅ |
| PoE Core abstract | [`sense360_core_poe.yaml`](../../packages/hardware/sense360_core_poe.yaml) | `relay_pin: GPIO3` | ✅ |
| wall Core abstract | [`sense360_core_wall.yaml`](../../packages/hardware/sense360_core_wall.yaml) | `relay_pin: GPIO3` | ✅ |
| Core `main_relay` owner | [`sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml) | `switch.gpio` `main_relay` on `pin: ${relay_pin}` | ✅ (resolves `GPIO3`) |
| FanRelay package | [`fan_relay.yaml`](../../packages/expansions/fan_relay.yaml) | `template` switch proxying `main_relay`; names no GPIO | ✅ (inherits the Core owner) |

The two voice-variant Core packages
([`sense360_core_voice_ceiling.yaml`](../../packages/hardware/sense360_core_voice_ceiling.yaml)
and [`sense360_core_voice_wall.yaml`](../../packages/hardware/sense360_core_voice_wall.yaml))
remain at `relay_pin: GPIO4` — they are **deliberately out of scope**
for the 001A rebind, and their reconciliation is owed to a later,
separately-evidenced slice.

## Drift guard

[`tests/test_relay_pinmap_reconcile.py`](../../tests/test_relay_pinmap_reconcile.py)
locks the reconciliation cross-layer. It parses the `Relay` ESP32 GPIO
number directly out of the connector pin map's `J4` table and asserts
that the same number is bound as `relay_pin` in every non-voice Core
abstract package. If a future edit moves the documented net to a
different `IO` but leaves the package value (or vice versa), the
doc-vs-firmware agreement assertion fails. This complements the existing
per-layer guards in
[`tests/test_core_abstract_bus.py`](../../tests/test_core_abstract_bus.py)
(`RelayPinRebindTests`),
[`tests/test_fan_relay_package.py`](../../tests/test_fan_relay_package.py),
and [`tests/test_module_pinmaps.py`](../../tests/test_module_pinmaps.py).

## Evidence still owed (board promotion remains blocked)

Reconciling the *firmware drive pin* does not make `S360-310` a verified
board or a shippable product. The following evidence is still required
before any promotion of `S360-310` / FanRelay beyond the current
`cataloged_unverified` + compile-only / manual-firmware-candidate
posture, and is tracked under `S360-310-BENCH-001`:

1. **Module-side `J2` silkscreen pin-1 orientation** and the Core-side
   `J4` pin-1 orientation (paired with `S360-100-BENCH-001`).
2. **Core-to-module 3-pin harness identity** — conductor-by-conductor
   mapping, connector keying / polarity.
3. **`J1` "Inline Fan" load-side NO / COM / NC mapping.**
4. **`K1` relay part number, coil voltage, and contact rating**
   (from BOM or board/silkscreen photographs).
5. **Bench / continuity / waveform verification** on a populated
   `S360-310-R4` board mated to a `S360-100-R4` Core, with
   operator / reviewer / serial recorded.
6. **Mains-voltage compliance** for the switched load — owned by
   `COMPLIANCE-001`
   ([`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md)),
   out of scope here.

When (and only when) those gates close, `WEBFLASH-RELAY-001` /
`RELEASE-RELAY-001` may proceed. This slice does not advance any of them.

## Cross references

- [`s360-100-core-connector-pin-map.md`](s360-100-core-connector-pin-map.md) — canonical Core-side connector pin map (S360-100-CONNECTOR-PINMAP-001).
- [`s360-100-r4-core.md`](s360-100-r4-core.md) — Core per-pin / per-net reference (`IO3 → Relay`).
- [`s360-310-module-pinmap.md`](s360-310-module-pinmap.md) — module-side pinmap (MODULE-PINMAPS-GDRIVE-001).
- [`s360-310-r4-relay.md`](s360-310-r4-relay.md) — Relay board-side audit (HW-PINMAP-310 / FOLLOWUP; PACKAGE-RELAY-001).
- [`core-abstract-bus-001c-rebind-plan.md`](core-abstract-bus-001c-rebind-plan.md) — Core abstract-bus rebind plan (CORE-ABSTRACT-BUS-001A / 001C).
- [`tests/test_relay_pinmap_reconcile.py`](../../tests/test_relay_pinmap_reconcile.py) — cross-layer drift guard for this slice.

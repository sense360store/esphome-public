# S360-100 Native Fan GPIO Map (S360-100-NATIVE-FAN-GPIO-MAP-001)

## Status

**Status: documentation-only architectural correction.** This document
records the canonical S360-100 / S360-311 **native ESP32-S3 GPIO map**
for the Sense360 fan signal path on the refreshed
[`S360-100-R4.pdf`](schematics/S360-100-R4.pdf) (SHA256
`4c9e8b06d129fbb55f61e143b648e03762d06cb4dc67fe3120c268cd3a4bdf16`,
837,443 bytes, KiCad E.D.A. 10.0.3, single sheet `1/1`). The new
hardware direction is:

- the **SX1509 I/O expander is removed from the S360-100 fan signal
  path**;
- both **FanPWM control (`TachPMW1..4`) and tach / pulse-counter inputs
  (`Pul_Cou1..4`, `TachIO`) terminate on native ESP32-S3 GPIO**;
- the prior SX1509-routed fan path on the previous R4 snapshot is
  recorded here only as **historical / superseded** context.

It is **documentation only**. It does not:

- publish firmware, create release artifacts, change
  `firmware/sources.json`, change
  `manifest.json`, or promote any release
  target;
- claim measured PWM, RPM, tach, or pulse-counter operation on any
  board;
- claim a final firmware GPIO allocation beyond what the new R4
  schematic itself prints;
- enable `FanPWM` on WebFlash, add a `FanPWM` `artifact_name`, add a
  `FanPWM`-bearing row to
  [`config/webflash-builds.json`](../../config/webflash-builds.json),
  or flip the FanPWM `webflash_build_matrix`;
- claim the `S360-410` PoE PSU blocker is solved;
- claim the FanTRIAC `HW-005` blocker is solved;
- promote `S360-311` `schematic_status` (stays
  `cataloged_unverified`);
- remove the SX1509 globally — the SX1509 may still appear in
  packages / docs for non-fan purposes, and the historical SX1509
  fan-path proof
  ([`tests/test_sx1509_tach_pulse_counter_proof.py`](../../tests/test_sx1509_tach_pulse_counter_proof.py))
  remains the authoritative compile/config-proof record;
- fabricate any hardware verification evidence — no bench session,
  scope trace, continuity measurement, or operator-attributed
  observation is invented here.

The canonical homes for the architectural rule (native ESP32 GPIO for
tach / pulse counter) and for the per-pin Core / module reference
remain
[`docs/hardware/s360-100-native-tach-pulse-strategy.md`](s360-100-native-tach-pulse-strategy.md)
and
[`docs/hardware/s360-100-core-architecture.md`](s360-100-core-architecture.md);
this document is the **fan-path GPIO map** that sits on top of them
and replaces the stale SX1509 fan-path language.

## Hardware-direction change recorded here

| Element | Prior (superseded) snapshot | New canonical (current R4) | Source of truth |
|---|---|---|---|
| FanPWM control path (`TachPMW1..4`) | Routed through SX1509 (`U3`) channels 0..3 on the prior R4 snapshot | **Native ESP32-S3 GPIO** on the refreshed R4 sheet (`IO10` / `IO11` / `IO12` / `IO39`) | [`s360-100-core-architecture.md` § Pin allocation table](s360-100-core-architecture.md#pin-allocation-table--native-esp32-s3-gpio-termination); [`s360-100-r4-core.md` § Fan / driver outputs](s360-100-r4-core.md#fan--driver-outputs) refresh note |
| Tach / pulse-counter inputs (`Pul_Cou1..4`) | Routed through SX1509 (`U3`) channels 4..7 on the prior R4 snapshot | **Native ESP32-S3 GPIO** on the refreshed R4 sheet (`IO17` / `IO18` / `IO46` / `IO9`) | Same as above |
| Shared `TachIO` passthrough | Native ESP32-S3 `IO16` (unchanged) | Native ESP32-S3 `IO16` (unchanged) | Same as above |
| SX1509 (`U3`) role in the FanPWM hardware path | Documented as PWM-drive source for the prior R4 snapshot | **Removed from the FanPWM hardware path** in the refreshed R4 sheet (the SX1509 block is no longer printed on the visible sheet) | [`s360-100-core-architecture.md`](s360-100-core-architecture.md); [`s360-100-r4-core.md` HW-007 refresh note](s360-100-r4-core.md) |
| SX1509 references elsewhere | Used by historical compile-proof fixture and by the SX1509 binding-only package layer | **Allowed only as historical / superseded / non-fan signal context.** No current FanPWM release / WebFlash path uses the SX1509. | This document; [`s360-100-native-tach-pulse-strategy.md`](s360-100-native-tach-pulse-strategy.md) |
| FanPWM firmware-binding side | SX1509 PWM-drive output, polled binary states only, `rpm_supported: false` | **Pending re-bind against the native ESP32-S3 GPIO map below.** This document does **not** perform that re-bind. | [`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml); [`packages/expansions/fan_pwm_sx1509.yaml`](../../packages/expansions/fan_pwm_sx1509.yaml) (legacy / superseded header notes) |
| Bench / measured PWM / tach / RPM evidence | Not on file | **Still not on file.** Required for any release / WebFlash / hardware-stable promotion. | Bench session record (future); [`docs/hardware/s360-311-r4-fanpwm.md`](s360-311-r4-fanpwm.md) |

## Canonical native ESP32-S3 GPIO map

The table below is the canonical S360-100 / S360-311 fan GPIO map on
the refreshed R4 sheet. Every value is **schematic-printed** on the
canonical PDF cited in the [Status](#status) section above; no value
is bench-verified by this document. Any field that is **not** proven
by the schematic is marked **TBD** — values are not invented.

| Logical fan signal | Required pin family | Native ESP32-S3 GPIO (schematic-printed) | Sense360 Core connector (J6 13-pin) | S360-311 module connector (J3 13-pin) | Bench-verified? |
|---|---|---|---|---|---|
| FanPWM control channel 1 (`TachPMW1`) | Native ESP32-S3 GPIO (PWM-capable) | `IO10` (module pin 18) | `J6` net `TachPMW1` | `J3` pin 3 | **No** — not bench-verified |
| FanPWM control channel 2 (`TachPMW2`) | Native ESP32-S3 GPIO (PWM-capable) | `IO11` (module pin 19) | `J6` net `TachPMW2` | `J3` pin 5 | **No** — not bench-verified |
| FanPWM control channel 3 (`TachPMW3`) | Native ESP32-S3 GPIO (PWM-capable) | `IO12` (module pin 20) | `J6` net `TachPMW3` | `J3` pin 7 | **No** — not bench-verified |
| FanPWM control channel 4 (`TachPMW4`) | Native ESP32-S3 GPIO (PWM-capable) | `IO39` (module pin 32) | `J6` net `TachPMW4` | `J3` pin 9 | **No** — not bench-verified |
| Tach / Pul_Cou channel 1 (`Pul_Cou1`) | Native ESP32-S3 GPIO (interrupt-capable) | `IO17` (module pin 10) | `J6` net `Pul_Cou1` | `J3` pin 4 | **No** — not bench-verified |
| Tach / Pul_Cou channel 2 (`Pul_Cou2`) | Native ESP32-S3 GPIO (interrupt-capable) | `IO18` (module pin 11) | `J6` net `Pul_Cou2` | `J3` pin 6 | **No** — not bench-verified |
| Tach / Pul_Cou channel 3 (`Pul_Cou3`) | Native ESP32-S3 GPIO (interrupt-capable) | `IO46` (module pin 16) | `J6` net `Pul_Cou3` | `J3` pin 8 | **No** — not bench-verified |
| Tach / Pul_Cou channel 4 (`Pul_Cou4`) | Native ESP32-S3 GPIO (interrupt-capable) | `IO9` (module pin 17) | `J6` net `Pul_Cou4` | `J3` pin 10 | **No** — not bench-verified |
| Shared `TachIO` passthrough | Native ESP32-S3 GPIO (interrupt-capable) | `IO16` (module pin 9) | `J6` net `TachIO` | `J3` pin 2 | **No** — not bench-verified |

### Cross-link rules

- The connector identities (`J6` Core-side, `J3` module-side, 13-pin
  pair) and the module-side schematic-confirmed pin-to-net order are
  recorded in
  [`docs/hardware/s360-311-r4-fanpwm.md` § Module-side `J3` ↔ Core-side `J6`](s360-311-r4-fanpwm.md#module-side-j3--core-side-j6-13-pin-harness).
  The 1-to-13 silkscreen pin order on the Core side stays **verify**
  per [`s360-100-r4-core.md` Open Question #9](s360-100-r4-core.md#open-questions--verification-needed)
  — this document does not close that bench-side flag.
- The bundle SKU ≠ firmware config string ≠ board SKU separation
  recorded in
  [`docs/hardware/s360-100-core-architecture.md` § Bundle SKU ≠ firmware config string ≠ board SKU](s360-100-core-architecture.md#bundle-sku--firmware-config-string--board-sku)
  is unchanged by this document.

## Status of the firmware path (current FanPWM YAML)

The current FanPWM firmware path in this repository is **still wired
against the prior SX1509 routing** and is now classified
**legacy / superseded** relative to the canonical native-GPIO map
above:

| File | Current binding | Classification under this document |
|---|---|---|
| [`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml) | Four `fan: platform: speed` controllers composed on top of the SX1509 PWM-drive outputs declared by [`fan_pwm_sx1509.yaml`](../../packages/expansions/fan_pwm_sx1509.yaml). No `pulse_counter`, no per-fan RPM, `rpm_supported: false`. | **Legacy / superseded** relative to the new native-GPIO fan-path direction. The package binding is **not** re-wired by this document. |
| [`packages/expansions/fan_pwm_sx1509.yaml`](../../packages/expansions/fan_pwm_sx1509.yaml) | Neutral SX1509 binding layer (SX1509 hub on `core_i2c`, four PWM-drive outputs on SX1509 channels 0..3, four polled binary diagnostic inputs on SX1509 channels 4..7, `tach_io_pin: GPIO16` substitution). | **Legacy / superseded** relative to the new native-GPIO fan-path direction. Binding remains intact so the FanPWM compile-only target still parses; no re-wire is performed here. |
| [`products/sense360-ceiling-poe-fanpwm.yaml`](../../products/sense360-ceiling-poe-fanpwm.yaml) | `Ceiling-POE-FanPWM` product YAML composing the legacy FanPWM package above. `webflash_build_matrix: false`, no `artifact_name`, status `hardware-pending`. | **Legacy / superseded** binding, **not WebFlash-exposed**, **not release-shippable**, no RPM / tach claim. |
| [`products/compile-only/ceiling-poe-fanpwm.yaml`](../../products/compile-only/ceiling-poe-fanpwm.yaml) | Compile-only skeleton mirroring the product YAML composition. `validated-full-compile` recorded for the legacy SX1509 composition (run `26414398902`). | **Legacy / superseded** composition; the compile-only target is retained as historical compile proof. The recorded full-compile run does **not** transfer to the new native-GPIO direction. |

Firmware re-binding against the native ESP32-S3 GPIO map above is
**pending** and is owned by a future firmware PR that must:

1. choose whether `packages/expansions/fan_pwm.yaml` continues to be a
   single-channel abstraction or is reshaped into a per-fan
   four-channel package against the canonical map;
2. bind each `TachPMW1..4` to the schematic-printed native ESP32-S3
   GPIO (`IO10` / `IO11` / `IO12` / `IO39`) — these are the only
   schematic-evidenced FanPWM control pins;
3. bind each `Pul_Cou1..4` and the shared `TachIO` to the
   schematic-printed native ESP32-S3 GPIO (`IO17` / `IO18` / `IO46` /
   `IO9` / `IO16`) — these are the only schematic-evidenced tach
   pins, and an ESPHome `pulse_counter` is now a candidate for these
   native pins (per the architectural rule);
4. compile-validate the re-bound YAML end-to-end against an actual
   `esphome compile` run before any release / WebFlash flip;
5. bench-validate PWM polarity, per-fan and aggregate current,
   thermal envelope, and per-fan RPM (`PWM-6` / `PWM-10` / `PWM-12` /
   `PWM-13` in [`docs/blocker-burndown.md` §2A (archived)](../archive-index.md))
   before any release / WebFlash / hardware-stable promotion.

None of those five steps is performed by this PR.

## Release / WebFlash readiness — unchanged by this document

- `Ceiling-POE-FanPWM` stays `status: hardware-pending`,
  `webflash_build_matrix: false`, no `artifact_name`,
  `rpm_supported: false`. The `FanPWM` token must not appear in
  [`config/webflash-builds.json`](../../config/webflash-builds.json).
  `WEBFLASH-PWM-001` / `RELEASE-PWM-001` / `WF-IMPORT-PWM-001` stay
  blocked.
- `S360-311` stays `schematic_status: cataloged_unverified` in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json).
- Release-One (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable` /
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`) and the LED
  preview (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`) are
  unchanged.
- FanTRIAC stays `status: blocked`, `blocker: HW-005`,
  `webflash_build_matrix: false`.
- `S360-410` PoE PSU stays `cataloged_unverified` — its
  `PACKAGE-POE-410-001` lane is unchanged.

## Compile / config proof for the architectural rule

The architectural rule that an ESPHome `pulse_counter` cannot accept
an SX1509 expander pin is compile-proven by
`PWM-SX1509-TACH-PROOF-001` (`esphome config` rejects the binding
with `sensor.pulse_counter: pin: [sx1509] is an invalid option for
[pin]`). That proof is **separate** from the current hardware path
recorded in this document — it remains valid as historical
compile-time evidence for the rule, and its fixture / test files
stay in place:

- Fixture: [`tests/esphome/sx1509_pulse_counter_proof.yaml`](../../tests/esphome/sx1509_pulse_counter_proof.yaml)
- Guard:   [`tests/test_sx1509_tach_pulse_counter_proof.py`](../../tests/test_sx1509_tach_pulse_counter_proof.py)

This document does not delete those records and does not weaken
their classification. They are evidence for the rule, not for the
current FanPWM hardware path.

## Do-not-change guardrails (S360-100-NATIVE-FAN-GPIO-MAP-001)

This document and the tests added with it must not:

- publish firmware, create release artifacts, change
  `firmware/sources.json`, change
  `manifest.json`, or promote any release
  target;
- change Release-One (`Ceiling-POE-VentIQ-RoomIQ` / stable /
  `v1.0.0`) or the LED preview entry
  (`Ceiling-POE-VentIQ-RoomIQ-LED` / preview);
- promote `S360-311` `schematic_status` (stays
  `cataloged_unverified`);
- flip `S360-311` `webflash_build_matrix`, add `artifact_name`, add
  a WebFlash wrapper, add a `config/webflash-builds.json` row, or
  claim WebFlash / release / import readiness for FanPWM;
- add the `FanPWM` token to
  [`config/webflash-builds.json`](../../config/webflash-builds.json);
- claim measured PWM, RPM, or tach support —
  `rpm_supported: false` stays the FanPWM product / target posture;
- claim final per-fan firmware GPIO bindings beyond what the new R4
  schematic itself prints (no firmware YAML edit is performed);
- re-bind [`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml)
  or [`packages/expansions/fan_pwm_sx1509.yaml`](../../packages/expansions/fan_pwm_sx1509.yaml)
  from SX1509 channels to native ESP32-S3 GPIO — that is a separate
  firmware PR that must include an `esphome compile` pass;
- delete or weaken
  [`tests/esphome/sx1509_pulse_counter_proof.yaml`](../../tests/esphome/sx1509_pulse_counter_proof.yaml)
  or
  [`tests/test_sx1509_tach_pulse_counter_proof.py`](../../tests/test_sx1509_tach_pulse_counter_proof.py)
  — they remain the authoritative compile/config proof of the
  architectural rule;
- claim the FanTRIAC `HW-005` blocker is solved;
- claim the `S360-410` PoE PSU is `verified` (separate
  `PACKAGE-POE-410-001` lane);
- remove the SX1509 globally — the SX1509 may still appear in
  packages / docs for historical / superseded context and for
  non-fan signals.

## See also

- [`docs/hardware/s360-100-core-architecture.md`](s360-100-core-architecture.md)
  — canonical S360-100 Core architecture index: central-hub
  framing, connector / module matrix, native-GPIO pin-allocation
  table from the refreshed R4 schematic, and the bundle SKU ≠
  firmware config string ≠ board SKU separation.
- [`docs/hardware/s360-100-r4-core.md`](s360-100-r4-core.md) — Core
  schematic reference; source of truth for Core nets and
  connectors.
- [`docs/hardware/s360-100-native-tach-pulse-strategy.md`](s360-100-native-tach-pulse-strategy.md)
  — canonical architectural rule: native ESP32 GPIO termination
  for tach / pulse-counter inputs, with the compile/config proof.
- [`docs/hardware/s360-311-r4-fanpwm.md`](s360-311-r4-fanpwm.md) — FanPWM
  audit; module-side schematic, connector reconciliation, and
  remaining bench gates.
- [`docs/hardware/schematics/S360-100-R4.pdf`](schematics/S360-100-R4.pdf)
  — current canonical S360-100 Core schematic (SHA256
  `4c9e8b06d129fbb55f61e143b648e03762d06cb4dc67fe3120c268cd3a4bdf16`).
- [`docs/blocker-burndown.md` §2A FanPWM / S360-311 (archived)](../archive-index.md)
  — blocker / scope-classification table for FanPWM.
- [`docs/product-readiness-matrix.md` §FanPWM / S360-311 (archived)](../archive-index.md)
  — product-readiness view; stays `hardware-pending`,
  `rpm_supported: false`.
- [`docs/manual-install-fan-candidates.md` (archived)](../archive-index.md)
  — FanPWM manual / no-WebFlash candidate posture.
- [`docs/release-artifact-readiness-matrix.md` (archived)](../archive-index.md)
  — FanPWM release-artifact posture (blocked).
- [`tests/test_native_fan_gpio_map.py`](../../tests/test_native_fan_gpio_map.py)
  — guards for this document (canonical GPIO map present, native
  pin family required, FanPWM YAML carries legacy/superseded
  labelling, FanPWM stays out of WebFlash / release, no RPM / tach
  claim).
- [`tests/test_native_tach_pulse_pin_strategy.py`](../../tests/test_native_tach_pulse_pin_strategy.py)
  — pre-existing architectural-rule guard.
- [`tests/test_sx1509_tach_pulse_counter_proof.py`](../../tests/test_sx1509_tach_pulse_counter_proof.py)
  — compile/config proof of the SX1509 / `pulse_counter` rejection
  (historical evidence for the rule; not the current fan-path
  binding).

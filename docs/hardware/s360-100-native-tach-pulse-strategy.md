# S360-100 Core — Native ESP32 Tach / Pulse-Counter Pin Strategy (S360-100-NATIVE-TACH-PULSE-001)

## Status

**Status: documentation-only architecture correction.** This document
records the canonical Sense360 Core pin strategy for tachometer and
pulse-counter inputs across the S360-100 / S360-100-R4 stack, and the
hardware-architecture correction that **tach / pulse-counter signals
must terminate on native ESP32-S3 GPIO** — never on the SX1509 I/O
expander.

It is documentation only. It does **not** publish firmware, create
release artifacts, update `firmware/sources.json`, update
`manifest.json`, promote any release target, claim measured RPM / tach
support, claim a final GPIO mapping where the schematic / design
evidence does not prove it, claim the S360-410 PoE blocker is solved,
or claim fan WebFlash / release readiness. Downstream gates
(`PRODUCT-PWM-001` / `WEBFLASH-PWM-001` / `RELEASE-PWM-001` /
`WF-IMPORT-PWM-001`, `S360-311-CURRENT-THERMAL-001`, FanTRIAC
`HW-005`) remain exactly as recorded in
[`docs/hardware/s360-311-r4-pwm.md`](s360-311-r4-pwm.md),
[`docs/blocker-burndown.md`](../blocker-burndown.md), and
[`docs/product-readiness-matrix.md`](../product-readiness-matrix.md).

## Context — S360-100 Core is the central hub

The new `S360-100-R4` schematic establishes the **Sense360 Core**
(`S360-100`) as the central hub for the room / module stack. Every
module connector — RoomIQ (`J10`), AirIQ / VentIQ (`J9`), LED (`J3`),
Relay (`J4`), 12 V PWM (`J6`), DAC (`J7`), TRIAC (`J15`), `FAN` (`J13`),
and the `PoE_ACDC` inlet (`J2`) — derives its signal set from the Core
board. The canonical per-pin / per-connector inventory is captured in
[`docs/hardware/s360-100-r4-core.md`](s360-100-r4-core.md) and is the
source of truth for Core nets; this document layers a single
architectural constraint on top of that inventory.

## Architectural rule — native ESP32 GPIO for tach / pulse counter

The following rule applies to **all** Sense360 Core / Sense360 module
hardware revisions and to **all** firmware packages, products, and
WebFlash builds:

1. **Tach / pulse-counter inputs MUST land on a native ESP32-S3 GPIO.**
   Any `sensor: platform: pulse_counter` pin, any RPM input, any
   per-fan / aggregate tach line, and any "pulse counting" signal of
   any kind must terminate at an interrupt-capable native ESP32-S3
   `InternalGPIOPin`.
2. **The SX1509 I/O expander MUST NOT be used for tach / pulse-counter
   inputs.** An SX1509 expander pin is **not** an `InternalGPIOPin` and
   **cannot** back an ESPHome `pulse_counter` — this is compile-proven,
   not inferred (see
   [PWM-SX1509-TACH-PROOF-001 finding](#pwm-sx1509-tach-proof-001-finding)
   below).
3. **PWM-drive output capability and tach-input capability are
   separate gates.** The SX1509 LED-driver PWM engine **does** support
   PWM-drive **output** (`output: platform: sx1509`, channels 0..7) and
   is the basis of FanPWM drive today. "SX1509 supports PWM" must
   never be read as "SX1509 supports tach" — they are independent
   capabilities and the rule above applies regardless of PWM-drive
   support.
4. **The expander may be used for suitable low-speed, non-tach
   signals only.** Polled `binary_sensor: platform: gpio` reads of an
   SX1509 channel, `output: platform: sx1509` PWM drive, and other
   low-speed expander-friendly signals remain supported. None of those
   constitute tach / pulse-counter / RPM support.

## PWM-SX1509-TACH-PROOF-001 finding

The architectural rule above is **compile-proven**, not inferred from
online documentation:

- The minimal fixture
  [`tests/esphome/sx1509_pulse_counter_proof.yaml`](../../tests/esphome/sx1509_pulse_counter_proof.yaml)
  puts SX1509 channel 4 (`Pul_Cou1`) behind a `sensor: platform:
  pulse_counter` on the shared `core_i2c` bus.
- `esphome config` (ESPHome 2026.5.1, exit code 2) **rejects it** with:

  ```text
  sensor.pulse_counter: pin:
    [sx1509] is an invalid option for [pin]. Please check the indentation.
  ```

- Two control checks in
  [`tests/test_sx1509_tach_pulse_counter_proof.py`](../../tests/test_sx1509_tach_pulse_counter_proof.py)
  confirm the rejection is `pulse_counter`+SX1509-specific (the same
  SX1509 pin validates as `binary_sensor: platform: gpio`;
  `pulse_counter` validates on a native ESP32 GPIO).

**SX1509 PWM-drive output is supported** (`output: platform: sx1509`,
channels 0..3 used for `TachPMW1..4` per
[`s360-100-r4-core.md` §Fan / driver outputs](s360-100-r4-core.md#fan--driver-outputs))
and is intentionally kept distinct from the tach / pulse-counter
limitation here.

## Hardware decision recorded by this document

| Decision | Value |
|---|---|
| Tach / pulse-counter pin family | **Native ESP32-S3 GPIO only** (interrupt-capable `InternalGPIOPin`). |
| SX1509 (U3) used for tach / pulse counter | **NO.** Forbidden by this rule and by `PWM-SX1509-TACH-PROOF-001`. |
| SX1509 (U3) used for PWM-drive output | Permitted (`output: platform: sx1509`); separate capability. |
| SX1509 (U3) used for polled binary GPIO state | Permitted (`binary_sensor: platform: gpio` — never `pulse_counter`). |
| Any prior "SX1509 can back fan tach" claim | **Incorrect; corrected by this document.** |
| Final GPIO assignment for `Pul_Cou1..4` | **Not yet assigned** — pending pin-allocation table below. |
| Final GPIO assignment for `TachIO` (shared) | `IO16` per the committed S360-100-R4 schematic (`s360-100-r4-core.md` table). |

## Pending pin-allocation table (native GPIO constraint)

The pin-allocation table below is **pending** — the per-fan `Pul_Cou1..4`
lines are still routed through the SX1509 (U3) on the committed
S360-100-R4 schematic (see
[`s360-100-r4-core.md` §Fan / driver outputs](s360-100-r4-core.md#fan--driver-outputs)),
which contradicts this architectural rule. Re-routing to native ESP32
GPIO is a **future hardware revision / harness change**, owned by the
hardware lane and not invented here. Until that revision exists, the
table records the **required constraint** rather than a final pin
mapping.

| Tach / pulse-counter signal | Required pin family | Current schematic source (S360-100-R4) | Pending native-GPIO assignment | Owner |
|---|---|---|---|---|
| `TachIO` (shared 12 V PWM fan tach passthrough) | Native ESP32-S3 GPIO (interrupt-capable) | ESP32 `IO16` — **already native** | `IO16` (already satisfies the rule) | — |
| `Pul_Cou1` (per-fan tach, channel 1) | Native ESP32-S3 GPIO (interrupt-capable) | SX1509 (U3) channel 4 — **violates rule** | **TBD** — pending hardware revision / harness | Hardware lane |
| `Pul_Cou2` (per-fan tach, channel 2) | Native ESP32-S3 GPIO (interrupt-capable) | SX1509 (U3) channel 5 — **violates rule** | **TBD** — pending hardware revision / harness | Hardware lane |
| `Pul_Cou3` (per-fan tach, channel 3) | Native ESP32-S3 GPIO (interrupt-capable) | SX1509 (U3) channel 6 — **violates rule** | **TBD** — pending hardware revision / harness | Hardware lane |
| `Pul_Cou4` (per-fan tach, channel 4) | Native ESP32-S3 GPIO (interrupt-capable) | SX1509 (U3) channel 7 — **violates rule** | **TBD** — pending hardware revision / harness | Hardware lane |

**Until the per-fan `Pul_Cou1..4` lines are re-routed to native ESP32
GPIO**, the firmware lane MUST NOT bind them as `sensor: platform:
pulse_counter` inputs and MUST NOT claim per-fan RPM support. The
existing PWM-drive-only `fan_pwm.yaml` scope (four `fan: platform: speed`
controllers on `output: platform: sx1509`, no `pulse_counter`,
`rpm_supported: false`) honours the rule today; that scope must stay
intact until the hardware-side re-route exists.

## Impact on existing firmware / readiness documents

This document does **not** flip any current status. It records the
architectural rule and the corrections that follow from it.

- **`packages/expansions/fan_pwm.yaml`** — already PWM-drive-only, no
  `pulse_counter`, no RPM claim, `Pul_Cou1..4` exposed only as polled
  binary states via
  [`packages/expansions/fan_pwm_sx1509.yaml`](../../packages/expansions/fan_pwm_sx1509.yaml).
  **Honours the rule today.** No change.
- **`packages/expansions/fan_pwm_sx1509.yaml`** — neutral binding
  layer; carries the compile-proven note that an SX1509 pin cannot
  back `pulse_counter`. Owns no tach / RPM sensor. **Honours the rule
  today.** No change.
- **`packages/hardware/sense360_core_mapping.yaml`** — Core abstract
  binds `fan_tach_pin: GPIO5` (native ESP32 GPIO) and uses
  `sensor: platform: pulse_counter` on `${fan_tach_pin}`. **Honours
  the rule today** (the pin family is native ESP32 GPIO; the exact pin
  number is the Core abstract default, not a per-fan claim against
  the schematic `Pul_Cou1..4` routing).
- **`packages/expansions/sense360_fan_pwm.yaml`** — legacy 4-channel
  package; uses `sensor: platform: pulse_counter` on native ESP32
  GPIOs (`GPIO8` / `GPIO12` / `GPIO14` / `GPIO16`). **Honours the
  pin-family rule** by construction (no SX1509 tach), independent of
  whether the chosen pin numbers match any future S360-100-R4
  re-route.
- **`docs/hardware/s360-311-r4-pwm.md`** — already records the
  PWM-drive-only scope and the compile-proven SX1509 + `pulse_counter`
  rejection. **No status flip.** A cross-reference back here is added.
- **`docs/blocker-burndown.md`** — `PWM-12` (TachIO / GPIO16 + RPM)
  stays **NEEDS BENCH / deferred**, `rpm_supported: false` stays the
  posture, and the FanPWM WebFlash / release / hardware-stable gates
  stay blocked. **No status flip.** A cross-reference back here is
  added.
- **`docs/product-readiness-matrix.md`** — `Ceiling-POE-FanPWM` stays
  `hardware-pending`, `rpm_supported: false`, `webflash_build_matrix:
  false`. **No status flip.** A cross-reference back here is added.
- **`config/hardware-catalog.json`** — `S360-100` `schematic_status:
  verified` is **not** changed (separate axis; bench/manufacturing
  evidence is unaffected by this architectural rule). `S360-311`
  `schematic_status: cataloged_unverified` is **not** changed.
- **`config/product-catalog.json`** — no product status is changed;
  this is a docs / tests slice. The stale FanPWM catalog note
  (`config/product-catalog.json`, `Ceiling-POE-FanPWM` row) already
  reads `RPM is NOT supported … an SX1509 expander pin is
  compile-proven unable to back an ESPHome pulse_counter` and is
  consistent with this rule.

## Tests / guards

A test guard in
[`tests/test_native_tach_pulse_pin_strategy.py`](../../tests/test_native_tach_pulse_pin_strategy.py)
pins the architectural rule:

1. No `pulse_counter` / tach / RPM sensor in `packages/**` or
   `products/**` maps its pin through an `sx1509:` expander key.
2. Any tach / pulse-counter product-readiness text in `docs/**` and
   `config/product-catalog.json` requires native ESP32 GPIO (the
   forbidden phrasings "SX1509 fan tach", "SX1509-backed tach RPM",
   "SX1509 pulse counter", "SX1509 backed pulse_counter", etc. do not
   appear as positive claims).
3. PWM-drive output via the SX1509 (`output: platform: sx1509`) must
   not be conflated with tach / pulse-counter support — the two
   capabilities are explicitly separated in this strategy doc and in
   `packages/expansions/fan_pwm_sx1509.yaml`.
4. `S360-311` does not claim RPM / tach readiness anywhere in
   `config/product-catalog.json`, `config/hardware-catalog.json`, or
   `config/webflash-builds.json` until measured native-GPIO tach
   evidence exists.

The pre-existing
[`tests/test_sx1509_tach_pulse_counter_proof.py`](../../tests/test_sx1509_tach_pulse_counter_proof.py)
remains the authoritative compile/config-proof guard for the SX1509 +
`pulse_counter` rejection itself.

## Do-not-change guardrails (S360-100-NATIVE-TACH-PULSE-001)

This document, and the tests added with it, must not:

- publish firmware, create release artifacts, change
  `firmware/sources.json`, change `manifest.json`, or promote any
  release target;
- change Release-One (`Ceiling-POE-VentIQ-RoomIQ` / stable / `v1.0.0`)
  or the LED preview entry (`Ceiling-POE-VentIQ-RoomIQ-LED` /
  preview);
- promote `S360-311` `schematic_status` (stays
  `cataloged_unverified`);
- flip `S360-311` `webflash_build_matrix`, add `artifact_name`, add a
  WebFlash wrapper, add a `config/webflash-builds.json` row, or claim
  WebFlash / release / import readiness;
- claim measured RPM / tach support — `rpm_supported: false` stays the
  posture;
- claim final per-fan `Pul_Cou1..4` GPIO assignments (pending a
  hardware-side re-route);
- claim the FanTRIAC `HW-005` blocker is solved (TRIAC drive / ZC
  source-pin reconciliation is separate work);
- claim the S360-410 PoE PSU is `verified` (separate
  `PACKAGE-POE-410-001` lane);
- alter the SX1509 PWM-drive output path used by `fan_pwm.yaml` /
  `fan_pwm_sx1509.yaml` — the package layer continues to expose
  PWM-drive only, with no per-fan RPM.

## See also

- [`docs/hardware/s360-100-r4-core.md`](s360-100-r4-core.md) — Core
  schematic reference; source of truth for Core nets and connectors.
- [`docs/hardware/s360-311-r4-pwm.md`](s360-311-r4-pwm.md) — FanPWM
  audit; records PWM-drive-only scope and `PWM-SX1509-TACH-PROOF-001`.
- [`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml)
  — PWM-drive-only FanPWM package; no `pulse_counter`.
- [`packages/expansions/fan_pwm_sx1509.yaml`](../../packages/expansions/fan_pwm_sx1509.yaml)
  — neutral SX1509 binding; PWM-drive outputs + polled diagnostic
  binary states only.
- [`tests/test_sx1509_tach_pulse_counter_proof.py`](../../tests/test_sx1509_tach_pulse_counter_proof.py)
  — compile/config proof of the SX1509 + `pulse_counter` rejection.
- [`tests/test_native_tach_pulse_pin_strategy.py`](../../tests/test_native_tach_pulse_pin_strategy.py)
  — guard pinning the architectural rule recorded here.
- [`docs/blocker-burndown.md`](../blocker-burndown.md) `§2A FanPWM /
  S360-311` — blocker / scope-classification table for FanPWM.
- [`docs/product-readiness-matrix.md`](../product-readiness-matrix.md)
  `§FanPWM / S360-311` — product-readiness view; stays
  `hardware-pending`, `rpm_supported: false`.

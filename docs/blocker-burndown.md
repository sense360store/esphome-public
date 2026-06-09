# Blocker Burn-Down (BLOCKER-BURNDOWN-001)

This document is a single, consolidated burn-down pass across the
Relay / DAC / PWM driver lanes, WebFlash live access, security action
pinning, release / import / artifact, compliance / safety, LED-stable,
and TRIAC blockers. Its purpose is to let the next implementation PRs be
small, clean, and evidence-backed by gathering every remaining blocker
into one classified table with explicit provenance and an exact
remaining action per row.

It supersedes nothing: each per-family matrix and hardware doc remains
the canonical home of its own blocker rows. This file is the **index +
classification + next-action** view that points back at them.

## 0. Methodology, provenance, and access limits

- **Repo evidence.** Read directly from the committed tree on
  `claude/blocker-burndown-consolidation-fpZyu` (HEAD at the
  `origin/main` tip, PR #598 merged).
- **Drive evidence.** Re-searched the shared hardware design drive this
  session for any **new** bench /
  sign-off / harness / polarity / current / thermal / compliance
  artifact that could close an open blocker. **None was found.** The
  only artifacts present are the already-recorded CAD / manufacturing
  sets (`12vFan_PWM_PulseCounter`, `Fan_GP8403` / `GP8403-Module`,
  `RelayBoard-Module`, `TRIAC.png` / `Relay.png` / `LED.png` design
  renders) plus the project trackers. No artifact is committed by this
  PR; provenance only.
- **Project tracker.** Re-read the `Sense360_R4_Tracker` project tracker
  (from the hardware design source) for status corroboration. New, blocker-relevant
  facts captured below: the Fan Relay board's further work (`Y02`) is
  **Waiting** on the TRIAC merge decision (`T02`, still **Doing**);
  the TRIAC mechanism is SSR + MOC3041 optocoupler (`T01` Done);
  mains connector tasks (`T04` / `Y01` / `Y03` / `Z01`) are Done but
  carry **no** compliance certification; the fleet-wide silkscreen
  P/N / REV / date-code task (`G01`) stays **Waiting** on the design owner's logo
  SVG (`N01`); and the PoE PSU rename (`R11`) is still **To do**.
- **WebFlash access.** A live read of `sense360store/WebFlash` was
  **denied** this session — the GitHub tool scope is
  `sense360store/esphome-public` + `sense360store/esphome` only. Every
  WebFlash-side axis therefore stays prior-recorded (2026-05-22,
  PR #565), not re-verified, and is classified `NEEDS WEBFLASH ACCESS`.
- **ESPHome / CI tooling.** ESPHome is not installed this session and
  the full-compile / `esphome config` lanes are manual-dispatch only,
  so live config compiles are `NEEDS BENCH`-adjacent tooling gaps where
  noted; the recorded full-compile runs (`26364679370`, `26414398902`)
  are prior-recorded green.
- **No fabrication.** Where evidence does not exist it is recorded as
  missing and converted into an operator question (§5), not invented.

## 1. Classification legend

| Class | Meaning |
|---|---|
| **CLOSED** | Gate satisfied; evidence in-repo or prior-recorded; no further action for this scope. |
| **CAN CLOSE NOW** | Closeable by a docs-only / no-op / test-only edit with no new evidence. |
| **NEEDS OPERATOR INPUT** | Only the hardware owner can answer (design intent, confirmation, sign-off). |
| **NEEDS WEBFLASH ACCESS** | Cannot be verified without live `sense360store/WebFlash` read access. |
| **NEEDS DRIVE EVIDENCE** | Needs an artifact that should live in Drive but does not yet exist there. |
| **NEEDS BENCH** | Needs a real-hardware measurement (waveform / current / thermal / multi-unit boot). |
| **BLOCKED BY POLICY / SAFETY** | Held by an explicit policy or mains-safety / compliance gate. |
| **OUT OF SCOPE** | Owned by a different lane or deferred by design. |

## 2. Consolidated blocker table

Columns: **ID** · **Family / board** · **Blocker** · **Status** ·
**Evidence found** · **Provenance** · **Closed?** · **Remaining exact
action** · **Next PR**.

### 2A. FanPWM / S360-311

| ID | Blocker | Status | Evidence found | Provenance | Closed? | Remaining exact action | Next PR |
|---|---|---|---|---|---|---|---|
| PWM-1 | Hardware evidence (schematic / BOM / gerbers / renders) | CLOSED | Committed `schematics/S360-311-R4.pdf`; Drive `12vFan_PWM_PulseCounter` set (PDF / `.xlsx` BOM / gerbers / CPL / STEP / 3 renders) | HW-ASSETS-003; PWM-BLOCKER-REMOVAL-001 / PR #586; Drive re-confirmed this session | Yes | none | — |
| PWM-2 | Schematic / BOM identity | CLOSED (part-identity) | Drive BOM cross-checks committed R4 schematic 1:1; rename `R07` Done | PWM-BLOCKER-REMOVAL-001 / PR #586; tracker `R07` | Yes | minor: explicit `R4` rev-stamp arrives via fleet silkscreen `G01`/`N01` | — (fab silkscreen) |
| PWM-3 | Core connector / bus / GPIO mapping (J6/J3 pin-1 order; UART-on-J3-11/12) | NEEDS BENCH (board-rev recorded) | `core_i2c` rebind landed; connector identity + routing direction resolved (D2/D3); **board revision tested = `S360-311-R4`** (operator bench) | CORE-ABSTRACT-BUS-001B; operator D2/D3; tracker `G01` (no R4 silkscreen yet); S360-311-BENCH-RESULT-001 (operator `@wifispray`, 2026-05-26) | Partial | silkscreen pin-1 read once R4 silkscreen exists; confirm UART routing on bench (board-rev dimension recorded) | S360-311-CURRENT-THERMAL-001 (silkscreen via fleet `G01`) |
| PWM-4 | PWM output pin mapping (4-channel; SX1509 ch0..3 / ch4..7; TachIO IO16) | CLOSED (package layer) | Reconciled `fan_pwm.yaml` → `fan_pwm_sx1509.yaml`; pinned by `test_fan_pwm_package.py` | PACKAGE-PWM-001-IMPLEMENT-001 / PR #590; operator D1/D2 | Yes (package) | none at package layer | — |
| PWM-5 | Controlled load type (≤4× 12 V 4-wire PWM fans on JST-SH SM04B) | CLOSED | Schematic + BOM + render silkscreen | PWM-BLOCKER-REMOVAL-001 / PR #586 | Yes | none | — |
| PWM-6 | Output electrical characteristics (per-fan current, MT3608 ceiling, aggregate load, inrush, thermal) | NEEDS BENCH (fan/load + supply recorded; measured run produced no values) | Boost topology known (MT3608 / L1 22 µH / SS34 / 38k:2k); **fan/load = Arctic P14 Plus**, **supply = 12 V MT3608 boost (~2 A available)**, qualitative 1+ hour all-four run, no sag reported (operator bench); per-channel + aggregate current, **measured** MT3608 ceiling, inrush **still not** measured. **S360-311-CURRENT-THERMAL-001 (2026-05-29):** the measured current/thermal run was recorded but the measurement intake arrived **blank** — **no** per-channel current, aggregate current, MT3608 measured voltage / sag / ceiling, or inrush were captured; nothing inferred / estimated. Row stays Partial; measured rows stay owed. | PWM-BLOCKER-REMOVAL-001 / PR #586; S360-311-BENCH-RESULT-001 (operator `@wifispray`, 2026-05-26); S360-311-CURRENT-THERMAL-001 (no values recorded, 2026-05-29) | Partial | bench: **measured** per-channel + aggregate current draw, MT3608 measured output-current ceiling / sag under 4-fan load, locked-rotor / inrush (all still owed — the 2026-05-29 run recorded none) | S360-311-CURRENT-THERMAL-001 (re-run with values) |
| PWM-7 | Package YAML (PWM-drive-only scope) | CLOSED | `fan_pwm.yaml` four `fan: platform: speed` controllers on SX1509 PWM-drive outputs | PACKAGE-PWM-001-IMPLEMENT-001 / PR #590 | Yes | none | — |
| PWM-8 | Product YAML (no-WebFlash slice) | CLOSED | `products/sense360-ceiling-poe-fanpwm.yaml` (`Ceiling-POE-FanPWM`); catalog row `hardware-pending` | PRODUCT-PWM-001 / PR #593; FW-COMPILE-PWM-PRODUCT-001 / PR #594 | Yes | none | — |
| PWM-9 | Compile-only target / full-compile result | CLOSED | `ceiling-poe-fanpwm-compile-only`; `validated-full-compile`, `rpm_supported: false` | FW-COMPILE-PWM-001 / PR #591; FW-COMPILE-PWM-RESULT-001 / PR #592 (run `26414398902`) | Yes | none | — |
| PWM-10 | PWM polarity (active-high vs active-low at the low-side N-FET gate) | CLOSED (observed behaviour) | Operator: increasing commanded duty increased fan speed across low/med/high duty → **non-inverting, no inversion required**; observed behaviour (not scope-traced); exact Hz / min%–max% not recorded | S360-311-BENCH-RESULT-001 (operator `@wifispray`, 2026-05-26) | Yes (observed behaviour) | optional: scope-trace gate waveform / record exact Hz + duty % | — |
| PWM-11 | Product bench (FanPWM end-to-end) | CLOSED (functional; operator-notes-only) | Operator-attested on `S360-311-R4`: all 4 channels individually speed-controlled, all 4 simultaneous for 1+ hour, restart retained last commanded speed; operator notes only (no photo/video/log). Measured current/thermal carried by PWM-6 / PWM-13; **S360-311-CURRENT-THERMAL-001 (2026-05-29) recorded NO measured values** (blank intake) so those rows stay owed. | S360-311-BENCH-RESULT-001 (operator `@wifispray`, 2026-05-26) | Yes (functional) | **measured** current + **measured** thermal carried by PWM-6 / PWM-13 (still owed — the 2026-05-29 run recorded none) | S360-311-CURRENT-THERMAL-001 (re-run with values) |
| PWM-12 | TachIO / GPIO16 + RPM | NEEDS BENCH / deferred (native GPIO allocation documented + FanPWM YAML reclassified legacy / superseded) | No `pulse_counter`; per-fan RPM via SX1509 `pulse_counter` is compile-proven unsupported (`[sx1509] is an invalid option for [pin]`); architectural rule pinned by [S360-100-NATIVE-TACH-PULSE-001](hardware/s360-100-native-tach-pulse-strategy.md) — **tach / pulse-counter inputs must terminate on native ESP32 GPIO; the SX1509 expander must not be used for tach** (PWM-drive output via SX1509 is a separate capability and stays supported). **R4 refresh (2026-05-28):** the new canonical `S360-100-R4.pdf` now prints `TachIO` / `Pul_Cou1..4` / `TachPMW1..4` directly against native ESP32-S3 module pins — schematic-side termination is now visibly rule-compliant ([`s360-100-core-architecture.md` § Pin allocation table](hardware/s360-100-core-architecture.md#pin-allocation-table--native-esp32-s3-gpio-termination)). **S360-100-TACH-GPIO-ALLOCATION-001 (2026-05-28 / PR #636):** the per-fan native GPIO allocation (`TachIO`→`IO16`, `Pul_Cou1`→`IO17`, `Pul_Cou2`→`IO18`, `Pul_Cou3`→`IO46`, `Pul_Cou4`→`IO9`, `TachPMW1..4`→`IO10`/`IO11`/`IO12`/`IO39`) is recorded on the Core hardware reference ([`s360-100-r4-core.md` § S360-100-TACH-GPIO-ALLOCATION-001](hardware/s360-100-r4-core.md#s360-100-tach-gpio-allocation-001--native-esp32-gpio-allocation-for-fanpwm-tach-inputs)) and on the FanPWM module audit ([`s360-311-r4-pwm.md` § S360-100-TACH-GPIO-ALLOCATION-001](hardware/s360-311-r4-pwm.md#s360-100-tach-gpio-allocation-001--core-side-native-esp32-gpio-allocation-2026-05-28)). **S360-100-NATIVE-FAN-GPIO-MAP-001 (2026-05-28):** the canonical FanPWM control + tach GPIO map is also recorded in [`s360-100-native-fan-gpio-map.md`](hardware/s360-100-native-fan-gpio-map.md) (same per-net allocation), and the SX1509-routed FanPWM control / tach path in the current FanPWM YAML (`packages/expansions/fan_pwm.yaml` + `packages/expansions/fan_pwm_sx1509.yaml`) is classified **legacy / superseded** with banner headers added to the package + product YAMLs. **S360-100-CONNECTOR-PINMAP-001 (PR #638, 2026-05-28):** the canonical Core-to-module connector pin map ([`s360-100-core-connector-pin-map.md`](hardware/s360-100-core-connector-pin-map.md)) is added — per-connector matrix + per-connector pin tables for every Sense360 module connector (J1 / J2 / J3 / J4 / J6 / J7 / J9 / J10 / J13 / J15); the J6 (S360-311) per-pin table records the `TachPMW1..4` / `Pul_Cou1..4` / `TachIO` native ESP32-S3 GPIO terminations with `schematic-backed` status, and no row maps a tach / pulse-counter signal through an expander. Firmware-binding and bench-measured RPM remain **out of scope** for this row; `rpm_supported: false` stays the posture and no FanPWM WebFlash / release exposure is enabled. **MODULE-PINMAPS-GDRIVE-001 (this PR, 2026-05-28):** the **module-side** companion pin maps land alongside the canonical Core-side pin map — one document per Sense360 module ([`s360-200-module-pinmap.md`](hardware/s360-200-module-pinmap.md), [`s360-210-module-pinmap.md`](hardware/s360-210-module-pinmap.md), [`s360-211-module-pinmap.md`](hardware/s360-211-module-pinmap.md), [`s360-300-module-pinmap.md`](hardware/s360-300-module-pinmap.md), [`s360-310-module-pinmap.md`](hardware/s360-310-module-pinmap.md), [`s360-311-module-pinmap.md`](hardware/s360-311-module-pinmap.md), [`s360-312-module-pinmap.md`](hardware/s360-312-module-pinmap.md), [`s360-320-module-pinmap.md`](hardware/s360-320-module-pinmap.md), [`s360-400-module-pinmap.md`](hardware/s360-400-module-pinmap.md), [`s360-410-module-pinmap.md`](hardware/s360-410-module-pinmap.md)); the `S360-311` row explicitly reconciles `TachPMW1..4` PWM-drive + `Pul_Cou1..4` + `TachIO` tach lines to **native ESP32-S3 GPIO** (no SX1509 routing) and reaffirms `PWM-12` stays NEEDS BENCH with `rpm_supported: false` and no FanPWM WebFlash / release exposure. | PWM-SX1509-TACH-PROOF-001 / PR #589; PACKAGE-PWM-TACH-STRATEGY-001 / PR #588; S360-100-NATIVE-TACH-PULSE-001 / PR #634; S360-100-NATIVE-TACH-PULSE-001 — R4 refresh (PR #635); S360-100-TACH-GPIO-ALLOCATION-001 (PR #636); S360-100-NATIVE-FAN-GPIO-MAP-001 (PR #637); S360-100-CONNECTOR-PINMAP-001 (PR #638); MODULE-PINMAPS-GDRIVE-001 (this PR) | No (kept false) | keep `rpm_supported: false`; any RPM still needs a separate firmware-binding PR + a bench session that captures measured RPM on the schematic-printed native-GPIO termination; remaining strapping / silkscreen open questions live in [`s360-100-r4-core.md` § S360-100-TACH-GPIO-ALLOCATION-001](hardware/s360-100-r4-core.md#s360-100-tach-gpio-allocation-001--native-esp32-gpio-allocation-for-fanpwm-tach-inputs) | COMPONENT-NATIVE-TACH-001 (future) |
| PWM-13 | Board-level thermal / EMI note | NEEDS BENCH (qualitative recorded; measured run produced no values) | SELV board; not certified; **qualitative: all 4 fans ran 1+ hour, no heat issue noticed** (operator notes); no measured °C / IR / thermocouple / EMI. **S360-311-CURRENT-THERMAL-001 (2026-05-29):** the measured thermal run was recorded but the intake arrived **blank** — **no** thermal method, ambient, hottest-location, measured °C, or EMI observation captured; nothing inferred. Row stays Partial; measured thermal stays owed. | WEBFLASH-PWM-001-READINESS / PR #598; S360-311-BENCH-RESULT-001 (operator `@wifispray`, 2026-05-26); S360-311-CURRENT-THERMAL-001 (no values recorded, 2026-05-29) | Partial | **measured** thermal temp / ambient / hottest-location (IR or thermocouple); EMI observation (not a compliance approval) — all still owed (the 2026-05-29 run recorded none) | S360-311-CURRENT-THERMAL-001 (re-run with values) |
| PWM-14 | Compliance / mains gate | CLOSED (no mains) | SELV (5 V → 12 V boost); no mains path | PWM-BLOCKER-REMOVAL-001 / PR #586 | Yes | none — `COMPLIANCE-001` mains gate does not apply | — |
| PWM-15 | WebFlash wrapper / build-matrix / artifact / module-availability | NEEDS WEBFLASH ACCESS + OUT OF SCOPE | No wrapper; `S360-311` not in any `module-availability.js` snapshot (drift #16) | WEBFLASH-DRIFT-001 / PR #595; WEBFLASH-PWM-001-READINESS / PR #598 | No | record `S360-311` classification on live re-check; wrapper gated behind bench | WEBFLASH-PWM-LIVE-CHECK-001 |
| PWM-16 | Native ESP32-S3 GPIO FanPWM YAML candidate (re-bind off SX1509) | NATIVE CANDIDATE COMPILE-VALIDATED + FUNCTIONAL BENCH PASS (native, operator-attested) | Native package [`packages/expansions/fan_pwm_native.yaml`](../packages/expansions/fan_pwm_native.yaml) binds `TachPMW1..4`→`IO10`/`IO11`/`IO12`/`IO39` via `output: platform: ledc` (NO SX1509) and `Pul_Cou1`/`Pul_Cou2`/`Pul_Cou4`→`IO17`/`IO18`/`IO9` via internal-diagnostic `sensor: platform: pulse_counter` (NO SX1509); `Pul_Cou3`/`IO46` disabled/TBD (collides with Core `fan_status_led_pin`/`GPIO46`), `TachIO`/`IO16` reserved/pending. Compile-only skeleton [`products/compile-only/ceiling-poe-fanpwm-native.yaml`](../products/compile-only/ceiling-poe-fanpwm-native.yaml) + target `ceiling-poe-fanpwm-native-compile-only` (`compile_validation_status: validated-full-compile`, `rpm_supported: false`). **Full `esphome compile` run against the native composition PASSED** (S360-311-NATIVE-FANPWM-COMPILE-001, LOCAL run 2026-05-28, ESPHome 2026.4.5, `esp32-s3-devkitc-1` / espidf / ESP-IDF v5.5.4, commit `643bbd3`; rc=0, RAM 13.2% / Flash 51.7% / 948679 bytes); LOCAL run, no GitHub Actions run id (none fabricated); legacy SX1509 run `26414398902` does not transfer. A green compile is compile coverage only — NOT a release artifact, NOT WebFlash exposure, NOT RPM/tach bench validation. No WebFlash wrapper / build-matrix / artifact. Pinned by [`test_native_fanpwm_yaml.py`](../tests/test_native_fanpwm_yaml.py). **S360-311-NATIVE-FANPWM-BENCH-001 (this PR, 2026-05-29):** the operator (`@wifispray`) flashed the native firmware (compile-proven at `643bbd3`) onto `S360-100-R4` + `S360-311-R4` and re-ran the **functional** bench — **FUNCTIONAL PWM PASS** (operator-notes-only): all four channels individual + simultaneous + high/med/low + restart-retention. This is the native composition's own functional bench (the 2026-05-26 legacy SX1509 bench does NOT transfer). **Current/thermal NOT measured; tach/RPM NOT measured** (`rpm_supported: false`; `Pul_Cou3`/`IO46` disabled/TBD; `TachIO`/`IO16` reserved/pending) — those stay carried by `PWM-6` / `PWM-12` / `PWM-13`. No WebFlash / release / hardware-stable claim. | S360-311-NATIVE-FANPWM-YAML-001; S360-311-NATIVE-FANPWM-COMPILE-001; S360-311-NATIVE-FANPWM-BENCH-001 (this PR) | No (compile + functional bench; candidate) | RPM/tach + current/thermal stay carried by `PWM-6` / `PWM-12` / `PWM-13` (functional PASS does not close them) | `S360-311-CURRENT-THERMAL-001` (bench) |

**Scope reclassification — `PWM-BLOCKER-RECLASSIFY-001` (2026-05-27).**
The FanPWM package / product / compile chain is complete and PR #599 found
FanPWM is evidence-gated, not repo-gated. The remaining `PWM-3` / `PWM-6` /
`PWM-12` / `PWM-13` / `PWM-15` gaps are therefore reclassified by the
surface each actually gates: they are **not** blockers for package
implementation, product YAML, the compile-only target, `config/` /
product-catalog presence, the no-WebFlash product posture, or future clean
repo / YAML / firmware PRs that do not expose WebFlash / release and do not
claim hardware-stable / RPM / compliance; they **stay** blockers for
WebFlash exposure, release artifacts, import readiness, hardware-stable
promotion, the production electrical-margin claim, RPM / `TachIO` claims,
and compliance / safety claims. Canonical table:
[`s360-311-r4-pwm.md` §PWM-BLOCKER-RECLASSIFY-001](hardware/s360-311-r4-pwm.md#pwm-blocker-reclassify-001--fanpwm-remaining-blockers-reclassified-by-release-scope-2026-05-27).

| Blocker | Current evidence | Blocks package / product / config? | Blocks WebFlash / release? | Blocks hardware-stable? | Next evidence needed |
|---|---|---|---|---|---|
| Measured per-channel current (`PWM-6`) | Not measured (qualitative 1+ hour run; `S360-311-CURRENT-THERMAL-001` 2026-05-29 recorded no values) | **No** | **Yes** | **Yes** | Measured A/channel + method → `S360-311-CURRENT-THERMAL-001` (re-run with values) |
| Measured aggregate current, all 4 (`PWM-6`) | Not measured (`S360-311-CURRENT-THERMAL-001` 2026-05-29 recorded no values) | **No** | **Yes** | **Yes** | Measured total A + MT3608 ceiling / inrush |
| Measured thermal temperature (`PWM-13`) | Qualitative no-heat 1+ hour; no °C (`S360-311-CURRENT-THERMAL-001` 2026-05-29 recorded no values) | **No** | **Yes** | **Yes** | Measured °C or documented method |
| Production electrical-margin claim | Functional only | **No** | **Yes** | **Yes** | The measured current + thermal rows |
| `TachIO` / `GPIO16` observation (`PWM-12`) | Not measured | **No** | **No** — RPM / diagnostics blocker only | **No** | Optional, only if RPM / diagnostics in scope |
| RPM support (`PWM-12`) | Compile-proven unsupported; `rpm_supported: false` | **No** | **No** | **No** | Out of scope for PWM-drive-only product (`COMPONENT-SX1509-TACH-001`, future) |
| WebFlash live access / module-availability (`PWM-15`, `WF-1`/`WF-2`) | Read denied; not in any snapshot | **No** | **Yes** — WebFlash exposure blocker only | **No** | Restore access → `WEBFLASH-PWM-LIVE-CHECK-001` |
| WebFlash wrapper / build / artifact / import (`PWM-15`, `RELEASE-PWM-001`, `WF-IMPORT-PWM-001`) | None | **No** | **Yes** | **No** | Wrapper gated behind measured current/thermal + live classification |
| Release readiness (`RELEASE-PWM-001`) | None | **No** | **Yes** | **No** | Release-proof chain after wrapper |
| Hardware-stable promotion (`schematic_status`) | `cataloged_unverified`; operator-notes-only bench | **No** | **No** | **Yes** | Measured current/thermal (+ photo/video/log if policy requires), separate JSON PR |
| Board-rev silkscreen / connector (`PWM-3`) | `S360-311-R4` tested; silkscreen / UART not confirmed | **No** | Informs only | **Yes** | Silkscreen pin-1 once R4 silkscreen exists + UART routing |
| Compliance / safety (`PWM-14` / `CMP-2`) | SELV; no mains | **No** | **No** | **No** | None — `COMPLIANCE-001` n/a |

### 2B. FanDAC / S360-312

| ID | Blocker | Status | Evidence found | Provenance | Closed? | Remaining exact action | Next PR |
|---|---|---|---|---|---|---|---|
| DAC-1 | Shared-I²C-bus naming | CLOSED | `core_i2c` | PR #569 | Yes | none | — |
| DAC-2 | GP8403 BOM identity | CLOSED | Drive `Fan_GP8403` BOM cross-check | PR #570 | Yes | none | — |
| DAC-3 | DIP-switch ↔ I²C-address truth table | CLOSED | Datasheet bit ordering + `0x58` base + PCB pole→pin map | HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001 / PR #571 | Yes | as-shipped DIP default is a non-blocking bench nicety | — |
| DAC-4 | DAC chip / channel capacity (2 chips, 4 outputs) | CLOSED | PCB: `IC1`→`J2`, `IC2`→`J3`; operator D1 | PR #571 | Yes | none | — |
| DAC-5 | Range-selection mechanism (register `0x01`, per chip) | CLOSED | Datasheet | PR #571 | Yes | none | — |
| DAC-6 | Range policy (per-chip; both default 0–10 V; independent override) | CLOSED | Operator D2–D4 | PR #571 | Yes | none | — |
| DAC-7 | Per-output range mixing on one GP8403 | CLOSED (hard constraint) | Register `0x01` is chip-level; **no** simultaneous per-output 0–5 V + 0–10 V claim | Guardrail D6; PR #571 | Yes | keep the no-mix guardrail | — |
| DAC-8a | `J2`/`J3` pin-1 + pin order + silkscreen | CLOSED (board-level) | KiCad PCB + bottom-silk render; `VOUT0`/`GND`/`VOUT1` order | PR #571 / PR #572 | Yes | none at board level | — |
| DAC-8b | `J3` `out0`/`out1` silkscreen transposition confirmation | NEEDS OPERATOR INPUT | Layout shows `J3` pin-1 net `2vout0` (`IC2` VOUT0) silk-labelled `out1`, and pin-3 net `2vout1` silk-labelled `out0` — **transposed** | PR #572 (layout assets) | No | operator / bench confirmation of the printed `J3` `out0`/`out1` text before it is relied upon | S360-312-BENCH-EVIDENCE-REQUEST-001 |
| DAC-8c | Cloudlift S12 harness conductor-by-conductor trace | NEEDS BENCH / NEEDS DRIVE EVIDENCE | No fan / harness artifact exists in Drive (re-confirmed this session) | PR #572; Drive re-search this session | No | bench / harness trace from `J2`/`J3` to the physical Cloudlift S12 fan input | S360-312-BENCH-EVIDENCE-REQUEST-001 |
| DAC-8d | Cloudlift S12 product-bench evidence | NEEDS BENCH | Not captured | — | No | operator product-bench against a Cloudlift S12 load | S360-312-BENCH-EVIDENCE-REQUEST-001 |
| DAC-9 | Nextion / `J7` + UART0 | OUT OF SCOPE | Deferred to a future product slice | PR #571 | n/a | none here | (future product slice) |
| DAC-10 | Package YAML (two-chip / four-output / per-chip range) | CLOSED | `fan_gp8403.yaml` reconciled; pinned by `test_fandac_package.py` | PACKAGE-DAC-001-IMPLEMENT-001 / PR #573 | Yes | none | — |
| DAC-11 | Product YAML + compile-only / full-compile | CLOSED | `products/sense360-ceiling-poe-fandac.yaml` (`Ceiling-POE-FanDAC`); `validated-full-compile` | FW-COMPILE-DAC-001; PRODUCT-DAC-001; COMPILE-STATUS-FLAGS-001 (run `26364679370`) | Yes | none | — |
| DAC-12 | Voltage-mode UX requirements | CAN CLOSE NOW (design decided) → product follow-up | Per-chip range substitutions default 0–10 V, independently overridable; outcome-first naming planned | PR #573; PRODUCT-DAC-001 | Design closed | product-layer UX naming / exposure owned by PRODUCT-DAC follow-ups; no per-output mix claim | (PRODUCT-DAC follow-up) |
| DAC-13 | `FanDAC ↔ AirIQ` mutex | CLOSED | `fandac_conflicts_with_airiq: true`; 0 AirIQ-bearing FanDAC config strings | WEBFLASH-DAC-001-READINESS / PR #597 | Yes | keep mutex; do not relax | — |
| DAC-14 | `S360-312` `schematic_status` JSON promotion | NEEDS OPERATOR INPUT | Stays `cataloged_unverified`; `schematic_file` unset | PR #573 | No | operator decision to promote (separate JSON PR) | (config-only follow-up) |
| DAC-15 | WebFlash wrapper / build-matrix / artifact / module-availability | NEEDS WEBFLASH ACCESS + OUT OF SCOPE | No wrapper; `S360-312` not in any `module-availability.js` snapshot (drift #17) | WEBFLASH-DRIFT-001 / PR #595; WEBFLASH-DAC-001-READINESS / PR #597 | No | record `S360-312` classification on live re-check; wrapper gated | WEBFLASH-DAC-LIVE-CHECK-001 |

**Scope reclassification — `DAC-BLOCKER-RECLASSIFY-001` (2026-05-27).**
The FanDAC package / product / full-compile chain is complete
(`compile_validation_status: validated-full-compile`, `voltage_enum_fixed:
true`, run `26364679370`), PR #597 kept FanDAC off WebFlash, and PR #599
found no new DAC bench / harness / Cloudlift-S12 artifact in Drive. The
remaining `DAC-8b` / `DAC-8c` / `DAC-8d` / `DAC-12` / `DAC-14` / `DAC-15`
gaps are therefore reclassified by the surface each actually gates: they
are **not** blockers for package implementation, product YAML, the
compile-only target, `config/` / product-catalog presence, the no-WebFlash
product posture, or future clean repo / YAML / firmware PRs that do not
expose WebFlash / release and do not claim Cloudlift-ready / hardware-stable
/ compliance; they **stay** blockers for WebFlash exposure, release
artifacts, import readiness, hardware-stable promotion, the production
voltage-control / product claim, the Cloudlift S12 product claim, and
compliance / safety claims. The `DAC-7` no-simultaneous-per-output-0–5 V /
0–10 V constraint stays correct. Canonical table:
[`s360-312-r4-fandac.md` §DAC-BLOCKER-RECLASSIFY-001](hardware/s360-312-r4-fandac.md#dac-blocker-reclassify-001--fandac-remaining-blockers-reclassified-by-release-scope-2026-05-27).

| Blocker | Current evidence | Blocks package / product / config? | Blocks WebFlash / release? | Blocks hardware-stable? | Next evidence needed |
|---|---|---|---|---|---|
| `J3` `out0`/`out1` silkscreen transposition (`DAC-8b`) | Layout transposed; not operator-confirmed | **No** | **Yes** — product / installation-doc and WebFlash / release blocker only | Informs only | Operator / bench confirmation → `S360-312-BENCH-RESULT-001` |
| Cloudlift S12 harness trace (`DAC-8c`) | No Drive artifact (PR #599) | **No** | **Yes** — Cloudlift product-claim / WebFlash / release blocker only | **No** | Harness trace `J2`/`J3` → fan input → `S360-312-BENCH-RESULT-001` |
| Cloudlift S12 product bench (`DAC-8d`) | Not captured | **No** | **Yes** — Cloudlift product-claim / WebFlash / release blocker only | **No** | Operator product-bench vs Cloudlift S12 load → `S360-312-BENCH-RESULT-001` |
| Voltage-mode / product UX (`DAC-12`) | Per-chip range design decided; UX exposure owed | **No** | **Yes** — WebFlash / product UX blocker only | **No** | Product-UX naming / exposure (`PRODUCT-DAC` follow-up); no per-output mix |
| WebFlash live access / module-availability (`DAC-15`) | Read denied; `S360-312` not in any snapshot (drift #17) | **No** | **Yes** — WebFlash exposure blocker only | **No** | Restore access → `WEBFLASH-DAC-LIVE-CHECK-001` |
| WebFlash wrapper / build / artifact / import (`DAC-15`, `RELEASE-DAC-001`, `WF-IMPORT-DAC-001`) | None | **No** | **Yes** | **No** | Wrapper gated behind bench + live classification |
| Release readiness (`RELEASE-DAC-001`) | None; full-compile necessary-but-insufficient | **No** | **Yes** | **No** | Release-proof chain after wrapper |
| Hardware-stable promotion (`schematic_status`, `DAC-14`) | `cataloged_unverified`; `schematic_file` unset | **No** | **No** | **Yes** | Operator decision + bench, separate JSON PR |
| Per-output range mixing on one GP8403 (`DAC-7`) | Chip-level register `0x01`; **no** simultaneous 0–5 V + 0–10 V claim | **No (constraint)** | Keep no-mix guardrail | **No** | None — hard guardrail; do not relax |
| Compliance / safety approval | SELV; no mains path; no sign-off claimed | **No** | **No** | **No** | None — `COMPLIANCE-001` mains gate n/a; release / compliance only |

### 2C. FanRelay / S360-310

| ID | Blocker | Status | Evidence found | Provenance | Closed? | Remaining exact action | Next PR |
|---|---|---|---|---|---|---|---|
| RLY-1 | Package-evidence rows (J4/J2/J1 pin order, harness, `K1` identity, load proof, boot state) | CLOSED (package-evidence layer) | Operator-attested + BOM-backed + public-reference-backed (10 rows) | S360-310-BENCH-EVIDENCE-001 / PR #561–#562 (operator `@wifispray`, 2026-05-22) | Yes (package) | none at package-evidence layer | — |
| RLY-2 | Product YAML (advanced / manual-warning wording) | CLOSED | `products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`; safety + competent-person caveats in header | PRODUCT-RELAY-001 / PR #564 | Yes | none | — |
| RLY-3 | GPIO3 strap-pin characterization (production-wide / multi-unit / scope-traced) | NEEDS BENCH | Pair-scoped only: relay de-energized across 10 boot cycles × 4 power paths on a single `S360-100-R4` + `S360-310-R4` pair; **no** oscilloscope trace, **no** multi-unit | S360-310-BENCH-EVIDENCE-001 / PR #561; core-abstract-bus-001c-rebind-plan decisions #16/#17 | No (general claim) | multi-unit oscilloscope-traced ESP32-S3 GPIO3 reset / boot / strap-state captures | S360-310-SAFETY-EVIDENCE-REQUEST-001 |
| RLY-4 | Competent-person sign-off | NEEDS OPERATOR INPUT | None exists; operator "as per UK standards" is a self-report, **not** an independent sign-off; none in Drive | S360-310-BENCH-EVIDENCE-001 / PR #561; Drive re-search this session | No | independent competent-person installation sign-off | S360-310-SAFETY-EVIDENCE-REQUEST-001 |
| RLY-5 | Manual / advanced warning UX expectation | CLOSED (product-doc layer) / NEEDS WEBFLASH ACCESS (UX) | Product YAML carries the advanced / manual-warning + safety + competent-person wording | PRODUCT-RELAY-001 / PR #564; PRODUCT-RELAY-001-READINESS-REFRESH / PR #563 | Partial | WebFlash-side manual-warning UX parity (when/if exposed) | WEBFLASH-RELAY-LIVE-CHECK-001 (gated) |
| RLY-6 | Mains / compliance caveats | BLOCKED BY POLICY / SAFETY (stable/market path); COMPLIANCE-001 itself CLOSED by posture | `K1` SRD-05VDC-SL-C contact rating is relay-datasheet evidence only — **not** board-level compliance / creepage / clearance / EMI / mains-safety certification. S360-310 is a mains-touching board under `COMPLIANCE-001-RESOLUTION-001`: never placed on the market; self-build open-source | S360-310-BENCH-EVIDENCE-001 / PR #561; resolution record | Partial (posture closure; no certification exists) | none while posture holds — market placement of S360-310 would reopen COMPLIANCE-001 (external safety + EMC assessment first) | (reopen path per COMPLIANCE-001-RESOLUTION-001) |
| RLY-7 | Further board work gated on TRIAC merge decision | NEEDS OPERATOR INPUT | Tracker `Y02` **Waiting** on `T02` (TRIAC separate-board-vs-merge, **Doing**); mains-connector tasks `T04`/`Y01`/`Y03` Done | `Sense360_R4_Tracker` (2026-05-18) | No | operator decision on `T02` (TRIAC merge) before more Relay board work | (operator decision) |
| RLY-8 | WebFlash wrapper / build-matrix / artifact / module-availability | NEEDS WEBFLASH ACCESS + BLOCKED BY POLICY/SAFETY | No wrapper; `S360-310` = `design-pending` (prior-recorded 2026-05-22); `WF-IMPORT-RELAY-001` blocked behind `RELEASE-RELAY-001` | PR #565 (prior-recorded); WEBFLASH-RELAY-001-READINESS / PR #596 | No | re-record classification on live re-check; exposure gated on RLY-3/4/6 | WEBFLASH-RELAY-LIVE-CHECK-001 |

**Scope reclassification — `RELAY-BLOCKER-RECLASSIFY-001` (2026-05-27).**
The FanRelay package / product / full-compile chain is complete
(`PACKAGE-RELAY-001` / PR #562, `PRODUCT-RELAY-001` / PR #564,
`FW-COMPILE-RELAY-FULL-FIX-001` / PR #578; full-compile-green in run
`26364679370`), PR #596 kept FanRelay off WebFlash, and PR #599 found no
new Relay safety / `GPIO3` / competent-person artifact in Drive. The
remaining `RLY-3` / `RLY-4` / `RLY-5` / `RLY-6` / `RLY-7` / `RLY-8` gaps are
therefore reclassified by the surface each actually gates: they are **not**
blockers for package implementation, product YAML, the compile-only target,
`config/` / product-catalog presence, the no-WebFlash product posture, or
future clean repo / YAML / firmware PRs that do not expose WebFlash / release
and do not claim hardware-stable / compliance / kit-default; they **stay**
blockers for WebFlash exposure, release artifacts, import readiness,
hardware-stable promotion, the production safety / install claim, mains /
compliance / safety claims, and kit / default / recommended membership. The
`RLY-6` mains-switching safety posture stays correct. Canonical table:
[`s360-310-r4-relay.md` §RELAY-BLOCKER-RECLASSIFY-001](hardware/s360-310-r4-relay.md#relay-blocker-reclassify-001--fanrelay-remaining-blockers-reclassified-by-release-scope-2026-05-27).

| Blocker | Current evidence | Blocks package / product / config? | Blocks WebFlash / release? | Blocks hardware-stable? | Next evidence needed |
|---|---|---|---|---|---|
| Production-wide / multi-unit `GPIO3` strap-pin characterisation (`RLY-3`) | Pair-scoped only (single pair, 10 cycles × 4 power paths); no scope trace, no multi-unit | **No** | **Yes** — production / hardware-stable / WebFlash / release blocker only | **Yes** | Multi-unit oscilloscope-traced `GPIO3` captures → `S360-310-SAFETY-BENCH-RESULT-001` |
| Competent-person / qualified-person sign-off (`RLY-4`) | None; operator self-report ≠ independent sign-off; none in Drive (PR #599) | **No** | **Yes** — safety / compliance / release blocker only | **No** | Independent competent-person installation sign-off → `S360-310-SAFETY-EVIDENCE-REQUEST-001` |
| Manual / advanced-warning UX (`RLY-5`) | Product YAML carries the wording; WebFlash-side UX parity owed | **No** | **Yes** — WebFlash UX blocker only | **No** | WebFlash-side manual-warning UX parity → `WEBFLASH-RELAY-LIVE-CHECK-001` |
| WebFlash live access / module-availability (`RLY-8`, `WF-1`/`WF-2`) | Read denied; `S360-310` `design-pending`, not in any live snapshot | **No** | **Yes** — WebFlash exposure blocker only | **No** | Restore access → `WEBFLASH-RELAY-LIVE-CHECK-001` |
| WebFlash wrapper / build / artifact / import (`RLY-8`, `RELEASE-RELAY-001`, `WF-IMPORT-RELAY-001`) | None | **No** | **Yes** | **No** | Wrapper gated behind `GPIO3` + sign-off + live classification |
| Release readiness (`RELEASE-RELAY-001`) | None; full-compile necessary-but-insufficient | **No** | **Yes** | **No** | Release-proof chain after wrapper |
| Mains / compliance approval (`RLY-6`) | `K1` contact rating is datasheet-only; no board-level cert | **No** | **Yes** — release / compliance blocker only | **No** | `COMPLIANCE-001-RESOLUTION-001` reopen path (assessment owed only before any market placement; posture: never placed on the market) |
| Hardware-stable promotion (`schematic_status`) | `cataloged_unverified`; `schematic_file` unset | **No** | **No** | **Yes** | Operator decision + bench, separate JSON PR |
| TRIAC / fan-relay-board merge dependency (`RLY-7`) | `Y02` **Waiting** on `T02` (TRIAC merge, **Doing**) | **No** | Informs only — separate board-decision context | Informs only | Operator decision on `T02` (out of scope here) |
| Kit / default / recommended membership | Excluded; `S360-KIT-BATH-RELAY` future-expansion; default kit is `S360-KIT-BATH-POE` | **No** | Out of scope unless separately approved | **No** | Separate explicit kit-default PR with UX + compliance sign-off |

### 2D. WebFlash live access / module availability

| ID | Blocker | Status | Evidence found | Provenance | Closed? | Remaining exact action | Next PR |
|---|---|---|---|---|---|---|---|
| WF-1 | Live `sense360store/WebFlash` read access | NEEDS WEBFLASH ACCESS | Read denied this session; GitHub scope = `esphome-public` + `esphome` only | This session; WEBFLASH-DRIFT-001 / PR #595 | No | operator / tooling: grant read access to `sense360store/WebFlash` | (tooling remediation) |
| WF-2 | `module-availability.js` `S360-311` / `S360-312` classification (drift #16/#17) | NEEDS WEBFLASH ACCESS | Not recorded in any snapshot | WEBFLASH-DRIFT-001 / PR #595 | No | record once access restored | WEBFLASH-{PWM,DAC}-LIVE-CHECK-001 |
| WF-3 | `artifact_pattern` source / grammar parity / full channel list (drift #4/#5/#11) | NEEDS WEBFLASH ACCESS | Prior-recorded subset consistent; sources not inspected | WEBFLASH-DRIFT-001 / PR #595 | No | re-run drift audit with live access | WEBFLASH-DRIFT-001 (re-run) |
| WF-4 | Cross-repo product / import drift | CLOSED (no confirmed drift) | Every Relay/DAC/PWM/TRIAC axis `INTENTIONALLY-BLOCKED` or `NEEDS-OPERATOR-INPUT`; no `WEBFLASH-DRIFT-FIX-001` prerequisite | WEBFLASH-DRIFT-001 / PR #595 | Yes | none (re-run only to close `NEEDS WEBFLASH ACCESS` axes) | — |
| WF-5 | Intra-repo stale "FanPWM product/package missing" headline (drift #20) | CAN CLOSE NOW (doc) | Already reconciled in-repo; re-confirmed | WEBFLASH-DRIFT-001 / PR #595; WEBFLASH-PWM-001-READINESS / PR #598 | Yes | none | — |

**Live re-check — `WEBFLASH-LIVE-CHECK-001` (2026-05-27).** The consolidated
live-WebFlash re-run that `WF-1` / `WF-2` / `WF-3` queue was performed this
session: `sense360store/WebFlash` was re-read via three read-only GitHub
methods (repo root, `scripts/utils/module-availability.js`, and a branch
listing) and **all three returned access denied** — the session GitHub scope is
still `esphome-public` + `esphome` only. So `WF-1` (live read access), `WF-2`
(`S360-311` / `S360-312` classification), and `WF-3` (`artifact_pattern` source
/ grammar / channel-list parity) **stay `NEEDS WEBFLASH ACCESS`** — none can be
closed, and `S360-310` stays prior-recorded `design-pending` (2026-05-22,
PR #565) while `S360-311` / `S360-312` stay not-recorded. The esphome-public
side was re-verified fresh this session and is unchanged (2 WebFlash builds;
Relay/DAC/PWM all `hardware-pending` / `webflash_build_matrix: false` / no
`artifact_name`; 3 wrappers; grammar unchanged), so `WF-4` (no confirmed
cross-repo drift) and `WF-5` stay closed. The remaining exact action is
unchanged: operator/tooling must grant read access to `sense360store/WebFlash`
(or supply an operator-attested snapshot), then re-run `WEBFLASH-LIVE-CHECK-001`
(or a `WEBFLASH-DRIFT-001` re-run). Full record in
[`webflash-drift-audit.md` §4.4](webflash-drift-audit.md#44-follow-up-resolution-log-updated-2026-05-27-by-webflash-live-check-001).
Docs-only; no config / product / WebFlash / workflow / test edit; no
`webflash_build_matrix` flip; no `artifact_name`; no exposure / import /
release / compliance / hardware-stable claim; no fabricated evidence.

### 2E. Security

| ID | Blocker | Status | Evidence found | Provenance | Closed? | Remaining exact action | Next PR |
|---|---|---|---|---|---|---|---|
| SEC-1 | Workflow least-privilege `permissions:` | CLOSED | All five workflows declare top-level `contents: read`; guarded by `test_workflow_permissions.py` | SECURITY-AUDIT-FIX-001 / PR (2026-05-25) | Yes | none | — |
| SEC-2 | Action SHA pinning (6 mutable major-tag pins) | CLOSED | All six actions converted to immutable commit SHAs (version preserved in trailing comment); guard tightened to require SHA pins | SECURITY-ACTION-PINNING-001 / PR (2026-05-27); `workflow-security-hardening.md` §2 | Yes | none — refreshing SHAs is a manual maintenance action (re-resolve tag → update SHA + comment + inventory) | — |
| SEC-3 | Dependabot / code-scanning / secret-scanning alert feed | NEEDS TOOLING | No alert feed available this session | repo-freshness-roadmap-audit §5 | No | operator/tooling: enable + review alert feed | (tooling) |
| SEC-4 | `requirements-dev.txt` floating upper bounds | OUT OF SCOPE (low) | Dev deps unbounded-above; workflows pin ESPHome exactly | repo-freshness-roadmap-audit §5 | No | optional reproducibility pin | (low-pri follow-up) |

### 2F. Release / import / artifact

| ID | Blocker | Status | Evidence found | Provenance | Closed? | Remaining exact action | Next PR |
|---|---|---|---|---|---|---|---|
| REL-1 | FanRelay / FanDAC / FanPWM release artifacts (.bin / tag / checksum / build-info) | OUT OF SCOPE (gated) | None; correct current posture | release-artifact-readiness-matrix §per-family | No | gated behind each `PRODUCT-*` + `WEBFLASH-*` slice | RELEASE-{RELAY,DAC,PWM}-001 (gated) |
| REL-2 | `WF-IMPORT-RELAY-001` cross-repo import | NEEDS WEBFLASH ACCESS (gated) | Blocked behind `RELEASE-RELAY-001`; WebFlash-owned | webflash-drift-audit; UPCOMING_PR Cross-repo | No | WebFlash-owned; not this repo | WF-IMPORT-RELAY-001 (cross-repo) |
| REL-3 | Release-One + LED preview unchanged | CLOSED (must stay) | `Ceiling-POE-VentIQ-RoomIQ` stable + LED preview verbatim | catalog; webflash-builds.json | Yes | do not change | — |

### 2G. Compliance / safety

| ID | Blocker | Status | Evidence found | Provenance | Closed? | Remaining exact action | Next PR |
|---|---|---|---|---|---|---|---|
| CMP-1 | `COMPLIANCE-001` mains UK/EU (S360-320 TRIAC, S360-400 PSU, mains-switching FanRelay) | **CLOSED — resolved by posture** (`COMPLIANCE-001-RESOLUTION-001`, 2026-06-09) | Owner decision record [`decisions/COMPLIANCE-001-RESOLUTION-001.md`](decisions/COMPLIANCE-001-RESOLUTION-001.md): mains-touching boards are never placed on the market (self-build open-source under CERN-OHL-P); tracker `compliance/mains-voltage-uk-eu-assessment.md` closed, retained as the reopen-path checklist | resolution record; tracker closure entry | Yes (by posture; **no conformity claimed, no checklist row promoted**) | none while posture holds — **reopen trigger**: any market-placement act reopens COMPLIANCE-001 and requires external safety + EMC assessment BEFORE that act; experimental-lane publish preconditions live in `config/release-channel-policy.json` | commissioning PR (experimental-lane move; queued in `UPCOMING_PR.md`) |
| CMP-2 | FanPWM / FanDAC mains gate | CLOSED (not applicable) | Both SELV low-voltage; no mains path | PWM/DAC docs | Yes | none | — |

### 2H. LED stable / S360-300

| ID | Blocker | Status | Evidence found | Provenance | Closed? | Remaining exact action | Next PR |
|---|---|---|---|---|---|---|---|
| LED-1 | LED preview → stable promotion | NEEDS BENCH + NEEDS OPERATOR INPUT | LED preview live (`Ceiling-POE-VentIQ-RoomIQ-LED` / preview); only a `LED.png` design render in Drive; no operator/bench stable proof | catalog; preview-to-stable-promotion-gates.md; Drive re-search this session | No | 17-row promotion gauntlet + operator proof + LED bench | (LED stable PR; not this scope) |
| LED-2 | LED stays preview (do not promote) | CLOSED (must stay) | `status: preview`, `channel: preview` | catalog | Yes | do not promote | — |

### 2I. TRIAC / S360-320

| ID | Blocker | Status | Evidence found | Provenance | Closed? | Remaining exact action | Next PR |
|---|---|---|---|---|---|---|---|
| TRI-1 | HW-005 unblock + `HW-PINMAP-320-FOLLOWUP` + `PACKAGE-TRIAC-001` | BLOCKED BY POLICY / SAFETY + OUT OF SCOPE | FanTRIAC reference stays `status: blocked`, `blocker: HW-005` | catalog; PRODUCT-TRIAC-001/002 (deferred) | No | bench timing / waveform / real-load + compliance | PACKAGE-TRIAC-001 (deferred) |
| TRI-2 | TRIAC separate-board-vs-merge decision (`T02`) | NEEDS OPERATOR INPUT | Tracker `T02` **Doing**; design (SSR + MOC3041) `T01` Done; also gates Relay `Y02` | `Sense360_R4_Tracker` (2026-05-18) | No | operator decision on `T02` | (operator decision) |
| TRI-3 | TRIAC compliance / mains sign-off | **CLOSED — resolved by posture** (see CMP-1) | `COMPLIANCE-001-RESOLUTION-001` closed COMPLIANCE-001 by market posture; publish stays gated by PACKAGE-TRIAC-001 (signed attestation) + the experimental-lane preconditions | resolution record | Yes (by posture; behaviour unchanged — still not published / buyable / kit-exposed) | commissioning PR moves FanTRIAC into the experimental lane; market placement would reopen COMPLIANCE-001 | commissioning PR |

### 2J. PoE PSU / S360-410

`S360-410` Sense360 PoE PSU is the **largest remaining blocker** to
expanding stable PoE room bundles beyond the already-shipping
`S360-KIT-BATH-P`. The full per-evidence-class audit is
[`docs/package-poe-410-001-audit.md`](package-poe-410-001-audit.md)
(E1–E15); the consolidated evidence matrix, stable-bundle impact
assessment, and next-evidence checklist are
[`docs/package-poe-410-evidence-result.md`](package-poe-410-evidence-result.md)
(PACKAGE-POE-410-EVIDENCE-RESULT-001). `S360-410` stays
`cataloged_unverified`; the hardware-verification block is now **lifted under
owner waiver `HW-S360-410-WAIVER-2026-06`** (2026-06-08, risk accepted — the
remaining E11/E12 evidence was **not measured**; see the dated waiver update at
the end of this section).

| ID | Blocker | Status | Evidence found | Provenance | Closed? | Remaining exact action | Next PR |
|---|---|---|---|---|---|---|---|
| POE-1 | Board SKU / R4 / canonical naming | CLOSED | `S360-410` row `rev: R4`, `Sense360 PoE PSU`, `Power` / `PSU` | `config/hardware-catalog.json` lines 116–121; `test_hardware_catalog.py` | Yes | none | — |
| POE-2 | Module-side schematic PDF committed | CLOSED | `schematics/S360-410-R4.pdf` (975,137 B; SHA256 `4a8b7a3b…2414`) | HW-ASSETS-410 / PR #516 | Yes | none (the `schematic_status: verified` JSON flip is POE-9) | — |
| POE-3 | Schematic-shown discrete topology | CLOSED | `LAN_CON1 RJP-003TC1(LPJ4112CNL)` / `U1 TPS2378DDAR` / `U2 TX4138` / `DCDC1 F0505S-2WR2` / `J3` output / `H1`–`H4` Earth | HW-PINMAP-410-FOLLOWUP / PR #517 | Yes | none | — |
| POE-4 | BOM cross-check (part identity) | CLOSED (part-identity) | BOM-confirms the discrete stack; `Ag9712M`/`Silvertel Ag9700` disproved; `AM1D-0505S-NZ` not in BOM | HW-BOM-ASSETS-002 / PR #535 | Yes (part identity) | `F0505S-2WR2` vs `AM1D-0505S-NZ` populated-primary intent → POE-8 | — |
| POE-5 | SELV classification / no mains caveat | CLOSED | PoE 36–57 V DC SELV; post-isolation LV; not in COMPLIANCE-001 mains scope | `docs/compliance/mains-voltage-uk-eu-assessment.md` | Yes | none | — |
| POE-6 | `J3` connector pin-1 polarity / orientation | ON FILE (render basis, 2026-06) | Schematic-side `J3` pin 1 = `+5VP`, pin 2 = `GND`; BOM `SM02B-SRSS-TB`; **on-header signal-name silkscreen `5V` / `GND`** + KiCad 3D CAD renders (six views); **no physical as-built pin-1 photo / no `.kicad_pcb` net-map** (polarity assured by the on-header labels rather than pin number) | HW-S360-410-EVIDENCE-2026-06; `s360-410-module-pinmap.md` (E9) | Yes (E9, render basis) | physical as-built pin-1 photo still nice-to-have for the full `verified` path | (covered by E9 record) |
| POE-7 | J2 harness identity (HW-002 OQ#6) | ON FILE (spec, 2026-06) | 2-conductor lead PSU `J3` (`SM02B-SRSS-TB`, 1×2) → Core `J2 PoE_ACDC`, `+5VP`→`+5VP` / `GND`→`GND`; polarized JST housing prevents reversed mating; both ends silkscreen-labeled; JST-latch retention. As-shipped **wire-colour map not documented — informational-only, not a safety gate** (keyed connector). `S360-100-BENCH-001` stays `pending` for any measured row | HW-S360-410-EVIDENCE-2026-06 (E10) | Yes (E10, spec) | measured as-shipped harness still owed for `verified` (not for the E15 caveat) | `S360-100-BENCH-001` update |
| POE-8 | Package-header reconciliation + DC/DC alternate intent | NEEDS OPERATOR INPUT | Header-cleanup component landed (PR #538, disproved whole-module hint removed); design-intent (af-only vs af/at; 5 V vs 5 V/3.3 V; protection claim; alternate DC/DC) unresolved | PACKAGE-POE-410-001 docs PR #526; PR #538 (E8/E14) | No | designer answers to the four E8/E14 questions → `PACKAGE-POE-410-001` implementation | `PACKAGE-POE-410-001` (impl) |
| POE-9 | PoE link-up / 5 V load / inrush / thermal / EMI/EMC bench | PARTIAL (2026-06); remainder **WAIVED** (HW-S360-410-WAIVER-2026-06, 2026-06-08) | **link-up confirmed** (board negotiated and powered from a PSE) + **5 V conversion confirmed** (output measured at 5 V with a multimeter); **load regulation, cold-start inrush, thermal rise of `U1`/`U2`/`DCDC1`, and EMI/EMC NOT measured** (owner-waived, risk accepted — not tested, not passed); PSE class (af vs at) not recorded | HW-S360-410-EVIDENCE-2026-06 (E11); HW-S360-410-WAIVER-2026-06 (waiver) | WAIVED (not measured) | none required under the waiver; a future `S360-410-BENCH-001` may still record load + inrush + thermal + EMI/EMC + a link-up class | `S360-410-BENCH-001` (optional, future) |
| POE-10 | Isolation / Hi-pot / insulation / leakage / earth continuity | **WAIVED** (HW-S360-410-WAIVER-2026-06, 2026-06-08) — NOT measured | `F0505S-2WR2` datasheet rating only (not as-built); `H1`–`H4` PCB bonding not recorded; Hi-pot / insulation resistance / leakage / earth continuity **NOT measured** (owner-waived, risk accepted — not tested, not passed) | `package-poe-410-001-audit.md` E12; HW-S360-410-WAIVER-2026-06 (waiver) | WAIVED (not measured) | none required under the waiver; an optional future isolation/safety bench may still record Hi-pot + insulation resistance + leakage + earth continuity | (owner-waived; optional future isolation/safety bench) |
| POE-11 | PCB source / gerbers (manufacturing readiness) | ON FILE (E13, 2026-06-08) | Complete 2-layer KiCad gerber set (13 files) committed at `docs/hardware/gerbers/S360-410-R4/` (archive SHA256 `e2fb70bb…3ac8`); editable `*.kicad_pcb` not committed (not required); `R4` silkscreen P/N/REV (`G01`) Waiting; PoE rename (`R11`) To do | HW-S360-410-GERBERS-E13 (E13) | Yes (E13 PCB-source line) | manufacturing silkscreen P/N-REV stamp (`G01`) still owed; does not block E15 | (per-board PCB-evidence, future) |
| POE-12 | `S360-410 schematic_status: verified` JSON PR | OUT OF SCOPE (POE-6/7 on file; still gated by the POE-9 bench remainder + POE-10) | `cataloged_unverified`, no `schematic_file` | `config/hardware-catalog.json`; `test_hardware_catalog.py` `EXPECTED_STILL_UNVERIFIED_SKUS` | No | mechanical JSON flip **after** the POE-9 bench remainder + POE-10 isolation close | `S360-410-SCHEMATIC-STATUS-VERIFIED` (JSON) |
| POE-13 | Release-One PoE caveat closure | CLOSED (2026-06-08, on POE-6 + POE-7 / E9 + E10 basis) | Flagship PoE `"schematic verification pending"` caveat reworded to record closure; documentation-caveat closure only, **no** S360-410 `verified` claim, Release-One stable status unchanged | HW-S360-410-EVIDENCE-2026-06; `release-one-hardware-audit.md` Findings → PoE PSU (E15) | Yes (E15) | none — the board `verified` path is the separate POE-9 remainder + POE-10 + POE-12 chain | — |

**Stable-bundle impact (PACKAGE-POE-410-EVIDENCE-RESULT-001).**
`S360-KIT-BATH-P` ships today (Release-One; **not blocked**; PoE
documentation caveat **closed** 2026-06 on the E9 + E10 basis, flagship
stable status unchanged). `S360-KIT-BEDROOM-P` is **blocked by S360-410**
(sole remaining hardware blocker). `S360-KIT-KITCHEN-P` (also AirIQ stack),
`S360-KIT-LIVING-P` and `S360-KIT-CORRIDOR-P` (also LED gauntlet) are
**partially blocked** — S360-410 is necessary but not sufficient. See
[`docs/package-poe-410-evidence-result.md` §3](package-poe-410-evidence-result.md#3-stable-bundle-impact-assessment).
*(That is the pre-waiver assessment. Under owner waiver
`HW-S360-410-WAIVER-2026-06` (2026-06-08, see the dated update below) these
bundles **no longer block on the S360-410 hardware-verification basis** and
proceed under the waiver; their non-S360-410 gates — AirIQ stack; LED gauntlet —
stay in force.)*

## 3. Summary by class

| Class | Count | IDs |
|---|---|---|
| CLOSED | 29 | PWM-1/2/4/5/7/8/9/10/11/14, DAC-1..8a/10/11/13, RLY-1/2, WF-4/5, SEC-1/2, REL-3, CMP-2, LED-2 |
| CAN CLOSE NOW (separate / docs) | 2 | DAC-12 (design), WF-5 (doc) |
| NEEDS BENCH | 7 | PWM-3/6/13 (partial — board-rev / fan-load / qualitative-thermal recorded by S360-311-BENCH-RESULT-001), DAC-8c/8d, RLY-3, LED-1 |
| NEEDS OPERATOR INPUT | 7 | DAC-8b/14, RLY-4/7, TRI-2, LED-1, (SEC-3 tooling) |
| NEEDS WEBFLASH ACCESS | 6 | PWM-15, DAC-15, RLY-8, WF-1/2/3, REL-2 |
| NEEDS DRIVE EVIDENCE | 1 | DAC-8c |
| BLOCKED BY POLICY / SAFETY | 4 | RLY-6, CMP-1, TRI-1/3 |
| OUT OF SCOPE | 5 | DAC-9, SEC-4, REL-1, PWM-12 (deferred RPM) |

(IDs may appear under more than one class where a blocker has both a
bench and an access dimension; the table in §2 is authoritative.)

**Headline (BLOCKER-BURNDOWN-001 pass, 2026-05-26).** No remaining
hardware / WebFlash / compliance blocker could be closed in that
docs-only pass without new bench, operator, WebFlash, or Drive evidence —
none of which appeared in that session. The hardware lanes (PWM / DAC /
Relay) are all package + product + compile complete and are now **bench /
operator / safety gated**, not repo gated. The one non-hardware lane that
can advance immediately is **`SECURITY-ACTION-PINNING-001`** (SEC-2).

**Update — `S360-311-BENCH-RESULT-001` (2026-05-26).** The operator then
ran the FanPWM bench. On operator-notes-only evidence (no photo/video/log)
this **closed `PWM-10`** (PWM polarity — increasing duty increased fan
speed, non-inverting) and **`PWM-11`** (functional product bench — all 4
channels individually speed-controlled, all 4 simultaneous for 1+ hour,
restart retained the last commanded speed on `S360-311-R4`), and
**partially advanced `PWM-3`** (board revision tested = `S360-311-R4`),
**`PWM-6`** (fan/load = Arctic P14 Plus; supply = 12 V MT3608 boost
~2 A available; qualitative 1+ hour run) and **`PWM-13`** (qualitative
1+ hour no-heat observation). The **measured** rows stay open — per-channel
current, aggregate current + MT3608 measured ceiling / inrush, and
measured thermal temperature — and feed the recommended next FanPWM PR
**`S360-311-CURRENT-THERMAL-001`**. RPM (`PWM-12`), WebFlash (`PWM-15`),
release, import, hardware-stable promotion (`S360-311` stays
`cataloged_unverified`), and compliance stay exactly as before. See
[`s360-311-r4-pwm.md` §S360-311-BENCH-RESULT-001](hardware/s360-311-r4-pwm.md#s360-311-bench-result-001--fanpwm-operator-bench-result-2026-05-26)
and [§5B](#5b-s360-311-bench-result-001--fanpwm-operator-bench-result-2026-05-26).

**Update — `PWM-BLOCKER-RECLASSIFY-001` (2026-05-27).** The remaining
FanPWM gaps were then **reclassified by release scope** (docs-only; no
posture flip). The measured-current / thermal / `TachIO` / WebFlash gaps
are **no longer blockers** for package / product / compile-only / config /
no-WebFlash-posture work or for future clean repo / YAML / firmware PRs
that do not expose WebFlash / release; they **stay blockers** only for
WebFlash exposure, release artifacts, import readiness, hardware-stable
promotion, the production electrical-margin claim, RPM / `TachIO` claims,
and compliance. Measured current / thermal = release / WebFlash /
hardware-stable blocker only; `TachIO`/`GPIO16` = RPM / diagnostics blocker
only; RPM = out of scope for the PWM-drive-only product; WebFlash live
access = WebFlash exposure blocker only. See the §2A scope-classification
table and [`s360-311-r4-pwm.md` §PWM-BLOCKER-RECLASSIFY-001](hardware/s360-311-r4-pwm.md#pwm-blocker-reclassify-001--fanpwm-remaining-blockers-reclassified-by-release-scope-2026-05-27).

**Update — `S360-311-NATIVE-FANPWM-BENCH-001` (2026-05-29).** The operator
(`@wifispray`) then flashed the **native** ESP32-S3 GPIO FanPWM firmware
(`fan_pwm_native.yaml` via the `ceiling-poe-fanpwm-native` skeleton,
compile-proven at commit `643bbd3` under S360-311-NATIVE-FANPWM-COMPILE-001)
onto `S360-100-R4` + `S360-311-R4` and re-ran the **functional** bench. On
operator-notes-only evidence this records a **functional PWM PASS on the
native composition** (`PWM-16`): all four channels individually
speed-controlled, all four simultaneous, low/med/high tracked, restart
retained the last commanded speed. This is the native composition's **own**
functional bench — the 2026-05-26 `S360-311-BENCH-RESULT-001` ran the
legacy SX1509 composition and does **not** transfer (different pins).
**Current / thermal were NOT measured** and **tach / RPM were NOT
measured**, so those rows stay open and unvalidated: per-channel +
aggregate current and measured thermal stay carried by `PWM-6` / `PWM-13`
→ **`S360-311-CURRENT-THERMAL-001`**; RPM stays unsupported
(`rpm_supported: false`, `PWM-12`), with `Pul_Cou3`/`IO46` disabled/TBD and
`TachIO`/`IO16` reserved/pending. WebFlash (`PWM-15`), release, import,
hardware-stable promotion (`S360-311` stays `cataloged_unverified`), and
compliance stay exactly as before. See
[`s360-311-r4-pwm.md` §S360-311-NATIVE-FANPWM-BENCH-001](hardware/s360-311-r4-pwm.md#s360-311-native-fanpwm-bench-001--native-fanpwm-operator-bench-result-2026-05-29)
and [§5F](#5f-s360-311-native-fanpwm-bench-001--native-fanpwm-operator-bench-result-2026-05-29).

**Update — `S360-311-CURRENT-THERMAL-001` (2026-05-29; no values recorded).**
The measured current / thermal bench run owed by `PWM-6` / `PWM-13` was
then **recorded, but the measurement intake arrived blank** — **no**
per-channel current (`J1`/`J2`/`J4`/`J5`), **no** aggregate current, **no**
MT3608 measured output voltage / sag / output-current ceiling, **no**
inrush / locked-rotor peak, **no** thermal method / ambient /
hottest-location / measured °C, and **no** EMI observation. Per the
no-fabrication rule **nothing was inferred, estimated, or back-filled**
from the fan label, the MT3608 datasheet, or the "~2 A available" supply
capability. **No status changed anywhere:** `PWM-6` and `PWM-13` stay
**Partial** with the measured rows still owed; `S360-311` stays
`cataloged_unverified`; no matrix flip, no WebFlash / release / artifact
enablement, no `webflash_build_matrix` flip, no `artifact_name`. The
measured envelope is still carried by `PWM-6` / `PWM-13` and a re-run of
**`S360-311-CURRENT-THERMAL-001`** with values filled in remains the next
step. A measured PASS, when it lands, closes `PWM-6` / `PWM-13` **only** —
it does **not** by itself enable WebFlash (`PWM-15` live-check gate) or
promote the board. See
[`s360-311-r4-pwm.md` §S360-311-CURRENT-THERMAL-001](hardware/s360-311-r4-pwm.md#s360-311-current-thermal-001--measured-current--thermal-bench-run-2026-05-29-no-values-recorded).

**Update — `DAC-BLOCKER-RECLASSIFY-001` (2026-05-27).** The remaining
FanDAC gaps were likewise **reclassified by release scope** (docs-only; no
posture flip). The package / product / full-compile chain is complete
(`validated-full-compile`, `voltage_enum_fixed: true`, run `26364679370`),
so the `J3`-silk (`DAC-8b`) / Cloudlift S12 harness + product-bench
(`DAC-8c`/`DAC-8d`) / voltage-UX (`DAC-12`) / `schematic_status` (`DAC-14`) /
WebFlash (`DAC-15`) gaps are **no longer blockers** for package / product /
compile-only / config / no-WebFlash-posture work or for future clean repo /
YAML / firmware PRs that do not expose WebFlash / release; they **stay
blockers** only for WebFlash exposure, release artifacts, import readiness,
hardware-stable promotion, the production voltage-control / product claim,
the Cloudlift S12 product claim, and compliance. The `J3` `out0`/`out1`
silkscreen transposition is a product / installation-documentation and
WebFlash / release blocker only; the Cloudlift S12 harness / product bench
is a Cloudlift product-claim / WebFlash / release blocker only; voltage-mode
UX is a WebFlash / product UX blocker only; WebFlash live access is a
WebFlash exposure blocker only; compliance / safety approval is a release /
compliance blocker only. The `DAC-7` no-per-output-mix constraint stays
correct. See the §2B scope-classification table and
[`s360-312-r4-fandac.md` §DAC-BLOCKER-RECLASSIFY-001](hardware/s360-312-r4-fandac.md#dac-blocker-reclassify-001--fandac-remaining-blockers-reclassified-by-release-scope-2026-05-27).

**Update — `RELAY-BLOCKER-RECLASSIFY-001` (2026-05-27).** The remaining
FanRelay gaps were likewise **reclassified by release scope** (docs-only; no
posture flip). The package / product / full-compile chain is complete
(`PACKAGE-RELAY-001` / PR #562, `PRODUCT-RELAY-001` / PR #564,
`FW-COMPILE-RELAY-FULL-FIX-001` / PR #578; full-compile-green in run
`26364679370`), so the production-wide `GPIO3` strap-pin (`RLY-3`) /
competent-person sign-off (`RLY-4`) / manual-UX (`RLY-5`) / mains-compliance
(`RLY-6`) / TRIAC-merge (`RLY-7`) / WebFlash (`RLY-8`) gaps are **no longer
blockers** for package / product / compile-only / config / no-WebFlash-posture
work or for future clean repo / YAML / firmware PRs that do not expose
WebFlash / release; they **stay blockers** only for WebFlash exposure,
release artifacts, import readiness, hardware-stable promotion, the
production safety / install claim, mains / compliance / safety claims, and
kit / default / recommended membership. The production-wide `GPIO3` strap-pin
characterisation is a production / hardware-stable / WebFlash / release
blocker only; competent-person sign-off is a safety / compliance / release
blocker only; manual / advanced-warning UX is a WebFlash UX blocker only;
WebFlash live access is a WebFlash exposure blocker only; mains / compliance
approval is a release / compliance blocker only; kit / default / recommended
membership is out of scope unless separately approved. The `RLY-6`
mains-switching safety posture stays correct. See the §2C
scope-classification table and
[`s360-310-r4-relay.md` §RELAY-BLOCKER-RECLASSIFY-001](hardware/s360-310-r4-relay.md#relay-blocker-reclassify-001--fanrelay-remaining-blockers-reclassified-by-release-scope-2026-05-27).

**Update — `SECURITY-ACTION-PINNING-001` (2026-05-27).** The one actionable
non-hardware lane (`SEC-2`) is now **CLOSED**. All six GitHub Actions
referenced under `.github/workflows/` were converted from mutable major
tags to **immutable commit SHAs**, with the resolved upstream version
preserved in a trailing `# vX.Y.Z` comment, and
`tests/test_workflow_permissions.py` was tightened to **require** SHA pins
(local composite actions and documented exceptions — currently none —
excepted). This is a security-pinning-only change: no workflow trigger,
permission, job, script, environment, secret, or build-logic edit, and the
`firmware-build-release.yml` `release`-job `contents: write` scope is
unchanged. The per-action security-pinning table (workflow file · action ·
previous ref · pinned SHA · resolves-to · reason · next maintenance action)
is the canonical
[`workflow-security-hardening.md` §2](workflow-security-hardening.md#2-action-pin-inventory-sha-pinned-by-security-action-pinning-001):

| Action | Previous ref | Pinned SHA | Resolves to | Next maintenance action |
|---|---|---|---|---|
| `actions/checkout` | `@v4` | `34e114876b0b11c390a56381ad16ebd13914f8d5` | `v4.3.1` | re-resolve tag → bump SHA + comment + inventory |
| `actions/setup-python` | `@v5` | `a26af69be951a213d495a4c3e4e4022e16d87065` | `v5.6.0` | re-resolve tag → bump SHA + comment + inventory |
| `actions/cache` | `@v4` | `0057852bfaa89a56745cba8c7296529d2fc39830` | `v4.3.0` | re-resolve tag → bump SHA + comment + inventory |
| `actions/upload-artifact` | `@v4` | `ea165f8d65b6e75b540449e92b4886f43607fa02` | `v4.6.2` | re-resolve tag → bump SHA + comment + inventory |
| `actions/download-artifact` | `@v4` | `d3f86a106a0bac45b974a628896c90dbdf5c8093` | `v4.3.0` | re-resolve tag → bump SHA + comment + inventory |
| `softprops/action-gh-release` (third-party) | `@v2` | `3bb12739c298aeb8a4eeaf626c5b8d85266b0e65` | `v2.6.2` | re-resolve tag → bump SHA + comment + inventory |

No exception rows: every referenced action is SHA-pinned. SHA pins do not
self-update, so refreshing them is a manual maintenance action. This does
**not** change any WebFlash / import / release / compliance / hardware
posture.

**Update — `PACKAGE-POE-410-EVIDENCE-RESULT-001` (2026-05-29).** The
S360-410 PoE-PSU evidence was reconciled into a single
evidence-result record at
[`docs/package-poe-410-evidence-result.md`](package-poe-410-evidence-result.md)
and the new §2J PoE PSU / S360-410 row block was added above. **No
posture flip:** `S360-410` stays `cataloged_unverified`, the
Release-One PoE caveat is preserved verbatim, no WebFlash / release /
bundle target is promoted, and no `config/**` / `packages/**` /
`firmware/**` file is edited. The reconciliation confirms five evidence
classes on file (POE-1 board SKU/R4, POE-2 schematic PDF, POE-3 discrete
topology, POE-4 BOM part-identity, POE-5 SELV) and the **bench (POE-9
PoE link-up + load + inrush + thermal + EMI/EMC), isolation/safety
(POE-10), connector silkscreen (POE-6), J2 harness (POE-7), and PCB
source (POE-11) classes are all still missing** — so the
`schematic_status: verified` JSON flip (POE-12) and the Release-One
caveat closure (POE-13) stay gated. Promoting `S360-410` to `verified`
without POE-9 + POE-10 would be a fabricated verification.
**Stable-bundle impact:** `S360-KIT-BATH-P` not blocked (ships under
preserved caveat); `S360-KIT-BEDROOM-P` blocked by S360-410 (sole
remaining hardware blocker); `S360-KIT-KITCHEN-P` /
`S360-KIT-LIVING-P` / `S360-KIT-CORRIDOR-P` partially blocked
(S360-410 plus AirIQ-stack or LED-gauntlet respectively). The operator
/ designer next-evidence checklist is recorded at
[`docs/package-poe-410-evidence-result.md` §5](package-poe-410-evidence-result.md#5-next-evidence-checklist-operator--designer-requests).

**Update — `HW-S360-410-EVIDENCE-2026-06` (2026-06-08).** The S360-410
PoE-PSU evidence gathered in 2026-06 was recorded into the §2J rows above
and into
[`docs/package-poe-410-evidence-result.md` §0](package-poe-410-evidence-result.md).
**No board posture flip:** `S360-410` stays `cataloged_unverified` (no
`config/hardware-catalog.json` change, no `schematic_file`), and no
WebFlash / release / bundle target is promoted. What moved: **POE-6**
connector pin-1 polarity (E9) and **POE-7** J2-harness identity (E10) are
now **on file** (E9 on a CAD-render + as-labeled-connector basis — no
physical as-built pin-1 photo / no `.kicad_pcb` net-map; E10 as a spec —
the as-shipped wire-colour map is informational-only, not a safety gate),
**POE-11** PCB-source / gerbers (E13) is **on file**, and **POE-9** PoE
bench (E11) is **PARTIAL** (link-up + 5 V confirmed; load / cold-start
inrush / thermal / EMI-EMC NOT measured). On the POE-6 + POE-7 (E9 + E10)
basis, **POE-13** the Release-One PoE documentation caveat (E15) is
**CLOSED** — a flagship documentation closure that changes no stable
status and makes no S360-410 hardware claim. Still missing / open: the
**POE-9 bench remainder** (load + inrush + thermal + EMI-EMC) and
**POE-10** isolation / safety (E12 — Hi-pot / insulation / leakage / earth
continuity, untouched), so **POE-12** the `schematic_status: verified`
JSON flip stays gated. Promoting `S360-410` to `verified` without the
POE-9 remainder + POE-10 would still be a fabricated verification.
**Stable-bundle impact unchanged:** `S360-KIT-BEDROOM-P` stays blocked by
S360-410; `S360-KIT-KITCHEN-P` / `S360-KIT-LIVING-P` /
`S360-KIT-CORRIDOR-P` stay partially blocked.

**Update — `HW-S360-410-WAIVER-2026-06` (2026-06-08) — owner release waiver,
block lifted on risk-acceptance basis.** The owner decided to release S360-410
**without** completing the remaining bench (POE-9 / E11 load regulation +
cold-start inrush + thermal rise + EMI/EMC) and isolation (POE-10 / E12 Hi-pot +
insulation resistance + leakage + earth continuity) evidence, and **accepted the
risk**. **Recorded as a WAIVER, not as completed or passed tests:** those
measurements were **NOT measured, NOT performed, and NOT passed** — see the
updated POE-9 / POE-10 rows above and
[`docs/package-poe-410-evidence-result.md` §0.1](package-poe-410-evidence-result.md).
**No verification claim:** `S360-410` stays `cataloged_unverified` (no
`config/hardware-catalog.json` `schematic_status` flip, no `schematic_file`); the
catalog records the waiver in a new `release_disposition` field only, and **no
`S360-410 verified` claim is made anywhere in this repo**. **Effect:** the
S360-410 hardware-verification **blocker is lifted** for release purposes, so
`S360-KIT-BEDROOM-P` / `S360-KIT-KITCHEN-P` / `S360-KIT-LIVING-P` /
`S360-KIT-CORRIDOR-P` **no longer block on the S360-410 hardware-verification
basis** and proceed under this waiver; their non-S360-410 gates (the AirIQ stack;
the LED preview→stable gauntlet) are unaffected. The waiver lifts the block
**only** — it does **not** flip any `config/webflash-builds.json` channel,
promote any bundle to stable, or productize Bedroom (separate, explicit steps).

## 3A. Final blocker-status — clean repo / YAML / firmware path unblocked (`BLOCKER-STATUS-FINALIZE-001`, 2026-05-27)

This row finalizes the blocker-removal chain (`BLOCKER-BURNDOWN-001` /
PR #599 → `S360-311-BENCH-EVIDENCE-REQUEST-001` / PR #600 →
`S360-311-BENCH-RESULT-001` / PR #601 → `PWM-BLOCKER-RECLASSIFY-001` /
PR #602 → `DAC-BLOCKER-RECLASSIFY-001` / PR #603 →
`RELAY-BLOCKER-RECLASSIFY-001` / PR #604 → `SECURITY-ACTION-PINNING-001` /
PR #605). It is **docs-only** and flips no posture: it simply records the
decision that **clean, no-WebFlash repo / YAML / firmware work is now
unblocked for FanPWM / FanDAC / FanRelay**, while the WebFlash / release /
import / hardware-stable / compliance lanes remain separately gated exactly
as the per-family reclassification PRs left them.

**Decision recorded.** A clean repo / YAML / firmware PR for PWM / DAC /
Relay may now proceed **provided it**:

- does **not** expose WebFlash (no wrapper under `products/webflash/`);
- does **not** add a release artifact (`.bin` / tag / checksum / build-info);
- does **not** flip `webflash_build_matrix`;
- does **not** add `artifact_name`;
- does **not** claim hardware-stable (no `schematic_status` promotion);
- does **not** claim compliance / safety approval;
- does **not** claim RPM / `TachIO` for PWM;
- does **not** claim Cloudlift-ready for DAC;
- does **not** claim production safety / install or kit / default readiness
  for Relay.

**Still-blocked lanes (unchanged).** WebFlash wrappers / build matrix /
import / module availability; release artifacts; hardware-stable promotion;
compliance / safety claims; PWM measured current / thermal before
WebFlash / release / hardware-stable; DAC `J3` / Cloudlift evidence before
WebFlash / release / hardware-stable / Cloudlift-ready; Relay `GPIO3` /
competent-person evidence before WebFlash / release / hardware-stable /
safety / install; and WebFlash live-access checks.

**Final blocker-status table.** Columns: **lane** · **clean repo / YAML /
firmware status** · **WebFlash / release status** · **hardware-stable /
compliance status** · **remaining evidence** · **next clean PR**.

| Lane | Clean repo / YAML / firmware (no-WebFlash) | WebFlash / release / import | Hardware-stable / compliance | Remaining evidence (before WebFlash / release / hardware-stable) | Next clean PR |
|---|---|---|---|---|---|
| FanPWM / S360-311 | **UNBLOCKED** — package + product + compile-only chain complete; clean no-WebFlash repo / YAML / firmware cleanup may proceed (no WebFlash, no release artifact, no `webflash_build_matrix` flip, no `artifact_name`, no hardware-stable / RPM / compliance claim) | **BLOCKED** — wrapper / build-matrix / artifact / import gated (`PWM-15`, `RELEASE-PWM-001`, `WF-IMPORT-PWM-001`) | **BLOCKED** — `cataloged_unverified`; compliance n/a (SELV, `COMPLIANCE-001` does not apply) | Measured per-channel + aggregate current, MT3608 ceiling / inrush, measured thermal → `S360-311-CURRENT-THERMAL-001`; RPM / `TachIO` out of scope | `REPO-CLEANUP-NOWEBFLASH-001` |
| FanDAC / S360-312 | **UNBLOCKED** — same conditions; no Cloudlift-ready claim; `DAC-7` no-per-output-mix guardrail kept | **BLOCKED** — wrapper / build-matrix / artifact / import gated (`DAC-15`, `RELEASE-DAC-001`, `WF-IMPORT-DAC-001`) | **BLOCKED** — `cataloged_unverified`; compliance n/a (SELV) | `J3` `out0`/`out1` silkscreen confirm, Cloudlift S12 harness trace + product bench → `S360-312-BENCH-RESULT-001` (requested via `S360-312-BENCH-EVIDENCE-REQUEST-001`) | `REPO-CLEANUP-NOWEBFLASH-001` |
| FanRelay / S360-310 | **UNBLOCKED** — same conditions; no production safety / install or kit / default / recommended readiness claim | **BLOCKED** — wrapper / build-matrix / artifact / import gated (`RLY-8`, `RELEASE-RELAY-001`, `WF-IMPORT-RELAY-001`) | **BLOCKED** — `cataloged_unverified`; mains compliance gated (`RLY-6`, `CMP-1`) | Multi-unit scope-traced `GPIO3` strap characterization + competent-person sign-off → `S360-310-SAFETY-BENCH-RESULT-001` (requested via `S360-310-SAFETY-EVIDENCE-REQUEST-001`) | `REPO-CLEANUP-NOWEBFLASH-001` |
| WebFlash live access (`WF-1`/`WF-2`/`WF-3`) | n/a — no repo-side clean-path claim | **BLOCKED** — `sense360store/WebFlash` read denied; live checks queued | n/a | Restore `sense360store/WebFlash` read access (or operator-attested snapshot) | `WEBFLASH-{PWM,DAC,RELAY}-LIVE-CHECK-001` (gated) |
| Security action SHA-pinning (`SEC-2`) | **CLOSED** — `SECURITY-ACTION-PINNING-001` (2026-05-27); all six actions SHA-pinned, guard tightened | n/a — no WebFlash / release posture change | n/a | none — refreshing SHAs is a manual maintenance action | — |

**`SECURITY-ACTION-PINNING-001` (`SEC-2`) is CLOSED.** It is recorded
closed in §2E, the §3-update note above, §4, §5 item 15,
[`workflow-security-hardening.md` §2/§3](workflow-security-hardening.md#2-action-pin-inventory-sha-pinned-by-security-action-pinning-001),
and `repo-freshness-roadmap-audit.md` §5/§7/§10. No row anywhere should
still show it open.

**Next implementation PR recommended — `REPO-CLEANUP-NOWEBFLASH-001`.**
A clean repo PR scoped to **(a)** clearing any stale docs / config
references that still imply clean repo / YAML / firmware work is blocked,
and **(b)** no-WebFlash YAML / firmware cleanup only. It must make **no**
WebFlash / release / import / hardware-stable claim, add no WebFlash
wrapper, flip no `webflash_build_matrix`, add no `artifact_name` or release
artifact, and claim no compliance / safety / RPM / Cloudlift-ready /
kit-default readiness. The measured-evidence PRs
(`S360-311-CURRENT-THERMAL-001`, `S360-312-BENCH-RESULT-001`,
`S360-310-SAFETY-BENCH-RESULT-001`) and the WebFlash live checks stay
queued behind their own evidence / access gates.

## 3B. Config-validation evidence recorded for the no-WebFlash product YAML path (`FW-CONFIG-RUN-NOWEBFLASH-001`, 2026-05-27)

After `SHIP-YAML-FIRMWARE-NOWEBFLASH-001` / PR #612 corrected the FanRelay
customer-usage `files:` example path, `FW-CONFIG-RUN-NOWEBFLASH-001`
records the **actual** config-validation status of the no-WebFlash product
YAML path. Canonical evidence table lives in
[`product-readiness-matrix.md` §FW-CONFIG-RUN-NOWEBFLASH-001](product-readiness-matrix.md#fw-config-run-nowebflash-001--recorded-config-validation-evidence-for-the-no-webflash-product-yaml-path-2026-05-27);
summarized here for the cross-lane view:

- **CI on the #612 commit `1424f074d9940db7164c0a468f39c49f8c74658e`** (merge
  commit `ed57523`): run `26504904676` **YAML Syntax Check → success**; run
  `26504904607` **Compile-only Targets — Metadata Validation → success**;
  run `26504904607` **Compile-only Targets — Full ESPHome Compile →
  skipped** (full lane is `workflow_dispatch` + `compile_mode=full` only).
- **Local (ESPHome-independent) validators, 2026-05-27:** `validate_configs.py`
  208 files / 0 failed; `validate_compile_targets.py --metadata-only` 10
  targets passed; relay (61) / pwm (62) / dac (44) / catalog (31) /
  compile-target (119) / matrix (24) / gap-report (27) / webflash-builds /
  workflow-permission suites OK; `python3 -m unittest discover` 759 tests OK
  (3 skipped).
- **Proves:** the three target product YAMLs parse + pass structural
  validation, target metadata is schema-valid, and the full guard suite
  (incl. the #612 path guard) passes. **Does NOT prove:** a full
  `esphome config` / compile of the **top-level** product YAMLs (the #612
  full lane was skipped; ESPHome unavailable locally). The recorded
  full-compile runs (`26414398902` PWM, `26364679370` DAC) exercise the
  `products/compile-only/` **skeletons**, not the top-level FanPWM / FanDAC
  product YAMLs; the FanRelay top-level target carries no
  `compile_validation_status` flag. No WebFlash / release / import /
  hardware-stable / compliance / RPM / Cloudlift-ready / kit-default claim
  is made; all lanes in §3A stay as recorded.

## 3C. Full ESPHome compile evidence recorded for the compile-only lane (`FW-FULL-COMPILE-NOWEBFLASH-001`, 2026-05-27)

`FW-FULL-COMPILE-NOWEBFLASH-001` closes the **full-compile gap** that §3B
left open: it **runs** the full `esphome compile` lane
(`scripts/validate_compile_targets.py --compile`, the command
`.github/workflows/compile-only.yml` runs in its `workflow_dispatch` +
`compile_mode=full` job) and records the real result. Canonical evidence
table lives in
[`product-readiness-matrix.md` §FW-FULL-COMPILE-NOWEBFLASH-001](product-readiness-matrix.md#fw-full-compile-nowebflash-001--recorded-full-esphome-compile-evidence-for-the-compile-only-lane-2026-05-27);
summarized here for the cross-lane view:

- **Provenance (honest):** this is a **local** full-compile run, **not** a
  GitHub Actions `workflow_dispatch` run. The Actions dispatch/run API was
  **unavailable** this session, so the CI full lane could not be triggered
  or observed and **no CI run ID exists** — none is fabricated. The lane's
  own script was run locally with ESPHome `2026.4.5` (the workflow's pinned
  version), board `esp32-s3-devkitc-1`, framework `espidf`, against commit
  `449d8c442e92b0562c22af8cbfedc3c0f8f0a4d5` on
  `claude/full-compile-validation-record-byyBY`.
- **Result:** `✅ All 10 compile target(s) passed.` — **10/10** registered
  compile-only targets `rc=0`, each `Successfully compiled program` with a
  real `firmware.bin`; **0** skipped, **0** failures. All three fan targets
  included: **FanRelay** (#8) is the **top-level** product YAML
  `products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml` (the
  #612-fixed file) — its top-level full-compile gap is now **closed**;
  **FanDAC** (#9) / **FanPWM** (#10) are the `products/compile-only/`
  **skeletons**, so the top-level FanPWM / FanDAC product-YAML full-compile
  gap stays **pending** (registering those top-level YAMLs is a separate
  scoped change, not made here).
- **Clean-tree validators (re-run after removing `.esphome` build trees):**
  `validate_configs.py` 208 files / 0 failed; `--metadata-only` 10 targets;
  relay (61) / pwm (62) / dac (44) / catalog (31) / compile-target (119) /
  matrix (24) / gap-report (27) / webflash-builds / workflow-permission
  suites OK; `python3 -m unittest discover` 759 tests OK (3 skipped).
- **Proves:** all 10 registered targets compile end-to-end under ESPHome
  `2026.4.5`, and the FanRelay top-level YAML builds clean. **Does NOT
  prove:** a CI-side `workflow_dispatch` record (no run ID), a top-level
  full-compile of `sense360-ceiling-poe-fanpwm.yaml` /
  `sense360-ceiling-poe-fandac.yaml` (only skeletons are registered), or
  any WebFlash / release / import / hardware-stable / compliance / RPM /
  Cloudlift-ready / kit-default readiness. Compile success is necessary but
  not sufficient; no `.bin` / checksum / artifact / release is uploaded or
  committed. All lanes in §3A stay as recorded.

## 3D. Top-level FanPWM / FanDAC product YAMLs registered as compile-only targets (`TOPLEVEL-FAN-COMPILE-TARGETS-001`, 2026-05-27)

`TOPLEVEL-FAN-COMPILE-TARGETS-001` closes the **registration** half of the
top-level FanPWM / FanDAC gap that §3C flagged as pending (lines noting the
top-level product-YAML full-compile gap "stays pending"). It does **not**
close the full-compile half — that stays owed to the recommended follow-up
`FW-FULL-COMPILE-TOPLEVEL-FANS-001`.

- **What changed.** Two new compile-only targets were added to
  [`config/compile-only-targets.json`](../config/compile-only-targets.json):
  `ceiling-poe-fandac-product-compile-only` →
  [`products/sense360-ceiling-poe-fandac.yaml`](../products/sense360-ceiling-poe-fandac.yaml)
  and `ceiling-poe-fanpwm-product-compile-only` →
  [`products/sense360-ceiling-poe-fanpwm.yaml`](../products/sense360-ceiling-poe-fanpwm.yaml).
  These register the **actual top-level product YAMLs** (the
  consumer-facing PRODUCT-DAC-001 / PRODUCT-PWM-001 deliverables) directly
  in the compile-only lane, mirroring the FanRelay precedent
  (`ceiling-poe-ventiq-fanrelay-roomiq-compile-only` already registers the
  top-level FanRelay product YAML). The compile-only target total moves
  **10 → 12** (`totals.targets`).
- **Skeletons preserved.** The existing `ceiling-poe-fandac-compile-only`
  and `ceiling-poe-fanpwm-compile-only` skeleton targets (under
  `products/compile-only/`) are **kept unchanged** and stay
  `compile_validation_status: validated-full-compile`. The skeleton is the
  historical CI validation file; the new row makes the shipped product YAML
  a first-class compile-only target. The distinction is explicit via the
  `…-product-compile-only` ids and the `notes` fields.
- **No full-compile claim.** Both new targets carry
  `compile_validation_status: pending-ci` — **not**
  `validated-full-compile`. No full `esphome compile` run has executed
  against these registered targets, so **no full-compile success is
  claimed** for them. (Their package compositions are byte-equivalent to
  the already-green skeletons — proven by the composition-parity tests in
  [`tests/test_pwm_product_readiness.py`](../tests/test_pwm_product_readiness.py)
  / [`tests/test_dac_product_readiness.py`](../tests/test_dac_product_readiness.py)
  — but parity is not a recorded compile of the registered target.) The
  real `--compile` result is owed to `FW-FULL-COMPILE-TOPLEVEL-FANS-001`.
- **Pinned by tests.**
  [`tests/test_compile_targets.py`](../tests/test_compile_targets.py)
  `TopLevelFanProductCompileTargetTests` proves both top-level targets are
  registered, the skeletons remain present + `validated-full-compile`,
  neither new target nor catalog entry declares `webflash_build_matrix` /
  `artifact_name` / `webflash_wrapper`, neither config string is in
  `config/webflash-builds.json`, and the FanPWM target keeps
  `rpm_supported: false`.
- **Guardrails.** Config / tests / docs only. No `packages/**` /
  `products/**` / `products/webflash/**` / `firmware/**` / `manifest.json`
  / `firmware/sources.json` edit; no WebFlash wrapper; no
  `webflash_build_matrix` flip; no `artifact_name`; no release artifact; no
  WebFlash / import / release / hardware-stable / compliance / RPM /
  Cloudlift-ready claim; no fabricated compile evidence. `S360-311` /
  `S360-312` stay `cataloged_unverified`; all §3A lanes stay as recorded.

## 3E. Full ESPHome compile evidence recorded for the top-level FanPWM / FanDAC product YAMLs (`FW-FULL-COMPILE-TOPLEVEL-FANS-001`, 2026-05-27)

`FW-FULL-COMPILE-TOPLEVEL-FANS-001` closes the **full-compile half** that §3D
left **owed**: §3D registered the top-level FanPWM / FanDAC product YAMLs as
compile-only targets but kept them `compile_validation_status: pending-ci`
because no `esphome --compile` run had yet executed against them. This slice
**runs** the full lane and records the real result. Canonical evidence table
lives in
[`product-readiness-matrix.md` §FW-FULL-COMPILE-TOPLEVEL-FANS-001](product-readiness-matrix.md#fw-full-compile-toplevel-fans-001--recorded-full-esphome-compile-evidence-for-the-top-level-fanpwm--fandac-product-yamls-2026-05-27);
summarized here for the cross-lane view:

- **Provenance (honest):** this is a **local** full-compile run, **not** a
  GitHub Actions `workflow_dispatch` run. The Actions dispatch/run API was
  **unavailable** this session, so the CI full lane could not be triggered or
  observed and **no CI run ID exists** — none is fabricated. The lane's own
  script (`python3 scripts/validate_compile_targets.py --compile`, the
  command `.github/workflows/compile-only.yml` runs in its
  `workflow_dispatch` + `compile_mode=full` job) was run locally with ESPHome
  `2026.4.5` (the workflow's pinned version), board `esp32-s3-devkitc-1`,
  framework `espidf` (ESP-IDF 5.5.4), against commit
  `17caa86f05c7b0ebcc9336b849f621f2d111839c` on
  `claude/toplevel-fans-compile-validation-n8LRb`.
- **Result:** `✅ All 12 compile target(s) passed.` — **12/12** registered
  compile-only targets `rc=0`, each `Successfully compiled program` with a
  real `firmware.bin`; **0** skipped, **0** failures. The two registered
  **top-level fan product** targets both compiled clean:
  `ceiling-poe-fandac-product-compile-only` →
  [`sense360-ceiling-poe-fandac.yaml`](../products/sense360-ceiling-poe-fandac.yaml)
  (Flash 50.6% / 927815 B) and `ceiling-poe-fanpwm-product-compile-only` →
  [`sense360-ceiling-poe-fanpwm.yaml`](../products/sense360-ceiling-poe-fanpwm.yaml)
  (Flash 51.1% / 937775 B). Both flip
  `compile_validation_status: pending-ci → validated-full-compile`; the
  `products/compile-only/` skeletons stay `validated-full-compile`
  (unchanged).
- **Clean-tree validators (re-run after removing `.esphome` build trees):**
  `validate_configs.py` 0 failed; `--metadata-only` 12 targets;
  `test_compile_targets.py` 139 OK; pwm / dac / catalog / matrix /
  gap-report / webflash-builds / workflow-permission suites OK;
  `python3 -m unittest discover` OK.
- **Proves:** all 12 registered targets compile end-to-end under ESPHome
  `2026.4.5`, and the top-level FanDAC / FanPWM product YAMLs build clean.
  **Does NOT prove:** a CI-side `workflow_dispatch` record (no run ID), or
  any WebFlash / release / import / hardware-stable / compliance / RPM /
  Cloudlift-ready / kit-default readiness. Compile success is necessary but
  not sufficient; no `.bin` / checksum / artifact / release is uploaded or
  committed; `S360-311` / `S360-312` stay `cataloged_unverified`. All lanes
  in §3A stay as recorded.

## 3F. FanRelay / FanPWM / FanDAC marked as manual / no-WebFlash firmware candidates (`MANUAL-FIRMWARE-CANDIDATE-001`, 2026-05-27)

`MANUAL-FIRMWARE-CANDIDATE-001` consumes the §3E / §3D compile evidence to
record a single narrow rollup status for the three fan product families:
**manual / no-WebFlash firmware candidate** = the top-level product YAML is
**present**, **structurally validated**, and **full-compile validated**.
Canonical definition + per-family evidence table live in
[`product-readiness-matrix.md` §MANUAL-FIRMWARE-CANDIDATE-001](product-readiness-matrix.md#manual-firmware-candidate-001--fanrelay--fanpwm--fandac-marked-as-manual--no-webflash-firmware-candidates-2026-05-27);
summarized here for the cross-lane view:

- **Scope:** notes-only `config/product-catalog.json` edit (the three fan rows'
  `notes`), one recorded `compile_validation_status: validated-full-compile`
  on the FanRelay compile-only target (from the **already-committed** §3E /
  PR #616 run, target #8, `rc=0` — the field was simply never set), plus tests
  (`test_product_catalog.py`, `test_relay_product_readiness.py`,
  `test_pwm_product_readiness.py`, `test_dac_product_readiness.py`) and docs.
- **No new compile:** the full-compile evidence is the committed §3E run; no
  `esphome --compile` is re-run and no CI run ID is fabricated.
- **Proves:** each of FanRelay / FanPWM / FanDAC has a top-level product YAML
  that exists, passes its structural readiness suite, and full-compiles — i.e.
  it can be installed manually (local `esphome` or remote-package include).
  **Does NOT prove / does NOT claim:** any release artifact, WebFlash exposure
  or import, hardware-stable readiness, compliance / mains-safety approval,
  Cloudlift-ready (DAC), RPM support (PWM), or kit-default / recommended
  (Relay). `webflash_build_matrix` stays `false`; no `artifact_name`; no
  `webflash_wrapper`; no `config/webflash-builds.json` row; lifecycle `status`
  stays `hardware-pending`; `S360-311` / `S360-312` stay
  `cataloged_unverified`. All lanes in §3A stay as recorded.

## 3G. Non-release artifact policy defined for the manual fan candidates (`MANUAL-FIRMWARE-ARTIFACT-POLICY-001`, 2026-05-27)

`MANUAL-FIRMWARE-ARTIFACT-POLICY-001` answers the question raised by §3F /
PR #617 and PR #618: **may an operator generate a firmware `.bin` for the
FanRelay / FanPWM / FanDAC manual candidates without it becoming a release
artifact or WebFlash build?** Canonical definitions + the seven-point
precondition list live in
[`product-readiness-matrix.md` §MANUAL-FIRMWARE-ARTIFACT-POLICY-001](product-readiness-matrix.md#manual-firmware-artifact-policy-001--non-release-artifact-rules-for-the-manual-fan-candidates-2026-05-27);
summarized here for the cross-lane view:

- **Scope:** docs-only policy edit (`product-readiness-matrix.md`,
  `release-artifact-readiness-matrix.md`, `manual-install-fan-candidates.md`,
  this file, `UPCOMING_PR.md`). **Generates nothing:** no `.bin`, checksum,
  build-info `manifest.json`, release upload, WebFlash import, or
  `firmware/sources.json` update.
- **Defines:** a **manual / private artifact** (a `.bin` from a local
  `esphome compile` or an explicitly non-release CI job, handed point-to-point
  to a named operator; pinned to a reviewed commit SHA; ephemeral; never
  committed; never published) vs a **release artifact** (channel-labelled,
  tagged, checksummed, build-info-manifested, GitHub-Release-attached, and/or
  WebFlash-imported).
- **Answer:** a manual / private `.bin` **may** be generated locally (already
  the PR #618 path) or by an explicitly non-release, expiring CI job — but a
  manual artifact is **not** a release artifact and **not** a
  `preview-artifact-candidate`.
- **Preconditions before any artifact-export PR:** (1) full-compile evidence
  already exists (committed §3E / PR #616 run; nothing fabricated); (2) artifact
  naming that cannot be confused with a release artifact (`-manual` + short SHA,
  no `vX.Y.Z`, no channel suffix); (3) any checksum is plain integrity SHA256
  for handoff only, never committed; (4) non-release storage only (never under
  `firmware/`, never committed, never a GitHub Release asset, never in
  `firmware/sources.json`); (5) non-release / expiring labelling; (6) no
  WebFlash exposure (`webflash_build_matrix` stays `false`); (7) no
  hardware-stable / compliance / Cloudlift / RPM / kit-default claim.
- **Proves:** nothing new about hardware or release readiness; it records a
  policy. `webflash_build_matrix` stays `false`; no `artifact_name`; no
  `webflash_wrapper`; no `config/webflash-builds.json` row; lifecycle `status`
  stays `hardware-pending`; `S360-311` / `S360-312` stay `cataloged_unverified`.
  All lanes in §3A stay as recorded.

## 3H. Non-release artifact CI run recorded for the manual fan candidates (`MANUAL-FIRMWARE-CI-ARTIFACTS-RESULT-001`, 2026-05-27)

`MANUAL-FIRMWARE-CI-ARTIFACTS-RESULT-001` records the **actual successful run**
of the explicitly non-release, expiring CI lane added by
`MANUAL-FIRMWARE-CI-ARTIFACTS-001` / PR #620
([`.github/workflows/manual-firmware-artifacts.yml`](../.github/workflows/manual-firmware-artifacts.yml)).
Canonical evidence table lives in
[`product-readiness-matrix.md` §MANUAL-FIRMWARE-CI-ARTIFACTS-RESULT-001](product-readiness-matrix.md#manual-firmware-ci-artifacts-result-001--recorded-non-release-artifact-ci-run-for-the-manual-fan-candidates-2026-05-27);
summarized here for the cross-lane view:

- **Provenance (honest):** this **is** a real GitHub Actions `workflow_dispatch`
  run (the first recorded run for which a CI run ID exists). The summary is the
  operator-supplied handoff; the Actions run / log API is not available from this
  session to re-fetch it, so the values are recorded as handed off — not
  fabricated, not independently re-derived here.
- **Run:** run ID `26530245113`, trigger `workflow_dispatch` with
  `artifact_mode=manual-candidate`, branch `main`, commit
  `9683d0ea13aea3814fd5056a18d049e1388d3586` (short `9683d0ea`),
  conclusion **success**.
- **Per-job result (all success):** Manual Artifacts — Generate Matrix;
  Manual Artifact: `fanpwm`; Manual Artifact: `fanrelay`; Manual Artifact:
  `fandac`; Manual Artifacts — Summary.
- **Artifacts (ephemeral, expiring):** one per family, named
  `<product-stem>-manual-9683d0ea-nonrelease` —
  `sense360-ceiling-poe-fanpwm-manual-9683d0ea-nonrelease`,
  `sense360-ceiling-poe-fandac-manual-9683d0ea-nonrelease`,
  `sense360-ceiling-poe-ventiq-fanrelay-roomiq-manual-9683d0ea-nonrelease`;
  retention 7 days, **expire 2026-06-03**; temporary GitHub Actions artifacts
  only, for **point-to-point operator handoff**.
- **Proves:** the **non-release CI artifact lane builds all three fan
  candidates** (FanRelay / FanPWM / FanDAC) on a real `workflow_dispatch` run.
  **Does NOT prove / does NOT claim:** any **release** artifact (the run
  published **no** GitHub Release and attached **no** Release asset), WebFlash
  exposure or import (`webflash_build_matrix` stays `false`; no
  `webflash_wrapper`; no `config/webflash-builds.json` row), any
  `firmware/sources.json` / `manifest.json` write, any committed `.bin` /
  checksum / build-info file, any `artifact_name`, or any hardware-stable /
  compliance / RPM (PWM) / Cloudlift-ready (DAC) / kit-default / recommended
  (Relay) readiness. The artifacts **expire**. Lifecycle `status` stays
  `hardware-pending`; `S360-311` / `S360-312` stay `cataloged_unverified`. All
  lanes in §3A stay as recorded.

## 4. Next-PR recommendations

Applying the burn-down decision rules:

- **FanPWM bench result is now recorded** (`S360-311-BENCH-RESULT-001`,
  2026-05-26): the operator bench closed PWM polarity (`PWM-10`) and the
  functional product bench (`PWM-11`) and partially advanced `PWM-3` /
  `PWM-6` / `PWM-13`. The **measured** current / thermal rows remain →
  **`S360-311-CURRENT-THERMAL-001`** (measured per-channel + aggregate
  current, MT3608 measured ceiling / inrush, measured thermal temperature
  or documented thermal method; J6/J3 silkscreen pin order once the R4
  silkscreen exists). The exact measured rows needed are now defined as an
  operator-answerable checklist + pass/fail contract by
  **`S360-311-CURRENT-THERMAL-EVIDENCE-REQUEST-001`** (2026-05-27; §5D), so
  **`S360-311-CURRENT-THERMAL-001`** stays **gated until the operator
  supplies the measured rows**. WebFlash stays separate and blocked
  (`WEBFLASH-PWM-LIVE-CHECK-001` behind access); do **not** recommend a
  `WEBFLASH-PWM-001` wrapper until measured current/thermal *and* the
  WebFlash live classification are done.
- **FanPWM remaining gaps are now scope-classified** (`PWM-BLOCKER-RECLASSIFY-001`,
  2026-05-27): the measured-current / thermal / `TachIO` / WebFlash gaps do
  **not** block package / product / compile-only / `config` / no-WebFlash
  work, so **clean repo / YAML / firmware cleanup PRs may proceed** as long
  as they do not expose WebFlash / release artifacts and do not claim
  hardware-stable / RPM / compliance. WebFlash wrapper / build / artifact /
  import PRs **remain blocked**, and **`S360-311-CURRENT-THERMAL-001`**
  stays a later evidence PR required before WebFlash exposure / release /
  hardware-stable promotion.
- **Native FanPWM functional bench is now recorded** (`S360-311-NATIVE-FANPWM-BENCH-001`,
  2026-05-29): the operator flashed the **native** ESP32-S3 GPIO firmware
  (compile-proven at `643bbd3`) onto `S360-100-R4` + `S360-311-R4` and
  re-ran the functional bench — **functional PWM PASS on the native
  composition** (all four channels individual + simultaneous + high/med/low
  + restart-retention; operator-notes-only). This is the native
  composition's **own** functional bench (the 2026-05-26 legacy SX1509 bench
  does **not** transfer). **Current / thermal and tach / RPM were NOT
  measured**, so they stay open / unvalidated → **`S360-311-CURRENT-THERMAL-001`**
  (measured rows) and `PWM-12` (RPM stays `rpm_supported: false`;
  `Pul_Cou3`/`IO46` disabled/TBD; `TachIO`/`IO16` reserved/pending). No
  WebFlash / release / hardware-stable claim; gates stay closed.
- **FanDAC bench evidence is missing** → **`S360-312-BENCH-EVIDENCE-REQUEST-001`**
  (request `J3` `out0`/`out1` transposition confirmation, Cloudlift S12
  harness trace, Cloudlift S12 product bench). *Not*
  `S360-312-BENCH-RESULT-001`.
- **FanDAC remaining gaps are now scope-classified** (`DAC-BLOCKER-RECLASSIFY-001`,
  2026-05-27): the `J3`-silk / Cloudlift S12 harness + product-bench /
  voltage-UX / `schematic_status` / WebFlash gaps do **not** block package /
  product / compile-only / `config` / no-WebFlash work, so **clean repo /
  YAML / firmware cleanup PRs may proceed** as long as they do not expose
  WebFlash / release artifacts and do not claim Cloudlift-ready /
  hardware-stable / compliance. WebFlash wrapper / build / artifact / import
  PRs **remain blocked**, and **`S360-312-BENCH-RESULT-001`** (requested via
  `S360-312-BENCH-EVIDENCE-REQUEST-001`) stays a later evidence PR required
  before WebFlash exposure / release / hardware-stable promotion or any
  Cloudlift-ready claim.
- **FanRelay safety evidence is missing** → **`S360-310-SAFETY-EVIDENCE-REQUEST-001`**
  (request multi-unit oscilloscope-traced GPIO3 strap characterization +
  competent-person sign-off). *Not* `S360-310-SAFETY-BENCH-RESULT-001`.
- **FanRelay remaining gaps are now scope-classified** (`RELAY-BLOCKER-RECLASSIFY-001`,
  2026-05-27): the production-wide `GPIO3` strap-pin / competent-person /
  manual-UX / mains-compliance / TRIAC-merge / WebFlash gaps do **not** block
  package / product / compile-only / `config` / no-WebFlash work, so **clean
  repo / YAML / firmware cleanup PRs may proceed** as long as they do not
  expose WebFlash / release artifacts and do not claim hardware-stable /
  compliance / kit-default. WebFlash wrapper / build / artifact / import PRs
  **remain blocked**, and **`S360-310-SAFETY-BENCH-RESULT-001`** (requested
  via `S360-310-SAFETY-EVIDENCE-REQUEST-001`) stays a later evidence PR
  required before WebFlash exposure / release / hardware-stable promotion or
  any production safety / install / compliance claim.
- **WebFlash live access is unavailable** → keep all live WebFlash PRs
  blocked; record access remediation as an operator / tooling action
  (WF-1). The live checks (`WEBFLASH-{PWM,DAC,RELAY}-LIVE-CHECK-001`,
  `WEBFLASH-DRIFT-001` re-run) stay queued behind access restoration.
- **Hardware evidence lanes are blocked** → the actionable non-hardware
  PR was **`SECURITY-ACTION-PINNING-001`** (SEC-2): convert the six
  inventoried mutable major-tag action pins to immutable commit SHAs.
  **Delivered 2026-05-27** (see the update note below); SEC-2 is now
  CLOSED. The remaining open non-hardware items are the three
  bench-evidence-request docs and the WebFlash-access-gated live checks.
- **Clean repo / YAML / firmware path is now finalized as unblocked**
  (`BLOCKER-STATUS-FINALIZE-001`, 2026-05-27): see §3A. The actionable
  clean-repo PR recommended next is **`REPO-CLEANUP-NOWEBFLASH-001`** —
  clear stale docs / config references and no-WebFlash YAML / firmware
  cleanup only, with **no** WebFlash / release / import / hardware-stable /
  compliance / RPM / Cloudlift-ready / kit-default claim. WebFlash wrapper /
  build / artifact / import PRs stay blocked, and the measured-evidence PRs
  (`S360-311-CURRENT-THERMAL-001`, `S360-312-BENCH-RESULT-001`,
  `S360-310-SAFETY-BENCH-RESULT-001`) stay queued behind their evidence
  gates.

## 5. Minimum operator checklist

Short, answerable items. Each maps to a blocker ID. No vague language.

**FanPWM / S360-311 (S360-311-BENCH-EVIDENCE-REQUEST-001):** the
short items below are expanded into the full operator-answerable
fill-in checklist + pass/fail evidence contract in
[§5A](#5a-s360-311-bench-evidence-request-001--fanpwm-detailed-bench-checklist--evidence-contract-2026-05-26)
and in
[`s360-311-r4-pwm.md` §S360-311-BENCH-EVIDENCE-REQUEST-001](hardware/s360-311-r4-pwm.md#s360-311-bench-evidence-request-001--fanpwm-bench-evidence-checklist--contract-2026-05-26).
1. PWM polarity at the SX1509 PWM-drive output vs the fan PWM input —
   active-high or active-low? (PWM-10)
2. Per-fan current draw and the 4-fan aggregate current at full speed? (PWM-6)
3. MT3608 boost output-current ceiling and observed locked-rotor /
   inrush behaviour? (PWM-6)
4. Board thermal rise under the worst-case 4-fan load? (PWM-6 / PWM-13)
5. Did the FanPWM product bench pass end-to-end? (PWM-11)
6. (When an R4 silkscreen exists) Core `J6` / module `J3` 1-to-13 pin-1
   order, and is UART on `J3` pins 11/12? (PWM-3)

**FanDAC / S360-312 (S360-312-BENCH-EVIDENCE-REQUEST-001):** the
short items below are expanded into the full operator-answerable
fill-in checklist + pass/fail evidence contract in
[§5C](#5c-s360-312-bench-evidence-request-001--fandac-detailed-bench-checklist--evidence-contract-2026-05-27)
and in
[`s360-312-r4-fandac.md` §S360-312-BENCH-EVIDENCE-REQUEST-001](hardware/s360-312-r4-fandac.md#s360-312-bench-evidence-request-001--fandac-bench-evidence-checklist--contract-2026-05-27).
7. Confirm the `J3` printed `out0`/`out1` silkscreen transposition
   (pin-1 = `IC2` VOUT0 is labelled `out1`)? (DAC-8b)
8. Cloudlift S12 harness conductor-by-conductor trace from `J2`/`J3` to
   the fan input? (DAC-8c)
9. Did the Cloudlift S12 product bench pass? (DAC-8d)
10. Promote `S360-312` `schematic_status` from `cataloged_unverified`? (DAC-14)

**FanRelay / S360-310 (S360-310-SAFETY-EVIDENCE-REQUEST-001):** the
short items below are expanded into the full operator- /
qualified-person-answerable fill-in checklist + pass/fail evidence
contract in
[§5E](#5e-s360-310-safety-evidence-request-001--fanrelay-detailed-safety--gpio3-checklist--evidence-contract-2026-05-27)
and in
[`s360-310-r4-relay.md` §S360-310-SAFETY-EVIDENCE-REQUEST-001](hardware/s360-310-r4-relay.md#s360-310-safety-evidence-request-001--fanrelay-safety--gpio3-evidence-checklist--contract-2026-05-27).
11. Multi-unit, oscilloscope-traced ESP32-S3 GPIO3 strap / boot state
    across several `S360-310` + `S360-100` pairs? (RLY-3)
12. Independent competent-person installation sign-off for mains
    switching? (RLY-4 / RLY-6)
13. TRIAC separate-board-vs-merge decision (`T02`) — does Relay board
    work proceed independently or wait for the merge? (RLY-7 / TRI-2)

**WebFlash / tooling:**
14. Restore read access to `sense360store/WebFlash` (or supply an
    operator-attested `module-availability.js` / `manifest.json` /
    `sources.json` snapshot) so the `LIVE-CHECK` PRs can run? (WF-1/2/3)

**Security:**
15. ~~Approve **`SECURITY-ACTION-PINNING-001`** as the next non-hardware
    PR (SHA-pin the six actions)? (SEC-2)~~ **DONE (2026-05-27)** — the six
    actions are SHA-pinned and the guard is tightened; SEC-2 is CLOSED.

### 5A. S360-311-BENCH-EVIDENCE-REQUEST-001 — FanPWM detailed bench checklist & evidence contract (2026-05-26)

`S360-311-BENCH-EVIDENCE-REQUEST-001` expands the short FanPWM items in
§5 into one precise, operator-answerable evidence request. It is
**documentation only** — it requests evidence, records none, and changes
no behaviour. The canonical board-side copy lives in
[`s360-311-r4-pwm.md` §S360-311-BENCH-EVIDENCE-REQUEST-001](hardware/s360-311-r4-pwm.md#s360-311-bench-evidence-request-001--fanpwm-bench-evidence-checklist--contract-2026-05-26);
this is the cross-lane index copy.

**Drive re-search (2026-05-26).** A fresh search (`S360-311`,
`S360-311-R4`, `FanPWM`, `PWM bench`, `polarity`, `current`, `thermal`,
`TachIO`, `GPIO16`, `fan test`, `product bench`, photos / videos /
spreadsheets / logs) found **no bench artifact** — only **design / CAD**
material: the already-recorded `12vFan_PWM_PulseCounter` set, a
canonically-named `S360-311-R4` Drive folder (from the PCB design owner:
KiCad sources, gerbers,
`positions.csv` CPL, STEP, `S360-311-R4_BOM.xlsx`, `S360-311-R4.pdf`
schematic, three renders), and the unchanged `Sense360_R4_Tracker`
(2026-05-18). This is the same artifact class as the committed
[`schematics/S360-311-R4.pdf`](hardware/schematics/S360-311-R4.pdf), is
recorded for provenance only, closes no bench blocker, and **no Drive
file is committed by this PR**. So `S360-311-BENCH-RESULT-001` stays
gated until the operator uploads / answers the checklist below.

**Operator checklist (fill in; leave `UNANSWERED` rather than guess):**

| # | Item | Feeds |
|---|---|---|
| 1 | Board revision tested (silkscreen P/N + rev; note if blank per `G01`) | PWM-3 |
| 2 | Fan / load model tested (make / model; rated current) | PWM-6 |
| 3 | Supply voltage (input rail into the board) | PWM-6 |
| 4 | PSU / current limit (bench PSU; set current limit) | PWM-6 |
| 5 | Number of channels tested (1–4 of `J1`/`J2`/`J4`/`J5`) | PWM-6 |
| 6 | PWM frequency used (Hz) | PWM-10 |
| 7 | PWM duty range tested (min%–max%) | PWM-10 |
| 8a | PWM polarity — does increasing duty increase fan speed? | PWM-10 |
| 8b | PWM polarity — is inversion required? (where) | PWM-10 |
| 9a | Boot / default output — before ESPHome boots | PWM-10 / PWM-11 |
| 9b | Boot / default output — after ESPHome boots | PWM-10 / PWM-11 |
| 9c | Boot / default output — after restart | PWM-10 / PWM-11 |
| 10 | Per-channel current measured (A at full speed) | PWM-6 |
| 11 | Aggregate current, all four channels active (A) | PWM-6 |
| 12 | Inrush / startup behaviour (peak A; locked-rotor) | PWM-6 |
| 13a | Thermal — duration | PWM-6 / PWM-13 |
| 13b | Thermal — ambient temp | PWM-6 / PWM-13 |
| 13c | Thermal — hottest component / location | PWM-6 / PWM-13 |
| 13d | Thermal — measured temp or qualitative observation | PWM-6 / PWM-13 |
| 14 | MT3608 / boost observation (output-current ceiling; sag) | PWM-6 |
| 15 | Connector / pin-1 / silkscreen confirmation (`J6`/`J3` 1-to-13; fan-output pin-1; UART on `J3` 11/12?) | PWM-3 |
| 16 | TachIO / GPIO16 observation — **no RPM claim unless separately proven** | PWM-12 (deferred) |
| 17 | Photos / videos / logs attached | all |
| 18 | Operator / date / source / provenance (who, when, serial, Drive path) | all |

**Pass/fail evidence contract:**

| Blocker | Closes when (PASS) | FAIL |
|---|---|---|
| PWM polarity (PWM-10) | Duty sweep showing increasing duty → increasing fan speed, with inversion-required answer (items 6–8b) | Un-scoped "it works"; no recorded direction |
| Per-fan current (PWM-6) | Measured per-channel current at full speed with method (items 2–5, 10) | Datasheet rating only; no board-side measurement |
| Aggregate current (PWM-6) | Measured 4-channel total at full speed + inrush / locked-rotor peak (items 11–12, 14) | Single-channel × 4; no inrush capture |
| Thermal (PWM-6 / PWM-13) | Worst-case-load observation with duration, ambient, hottest location, reading (items 13a–13d) — characterisation, **not** certification | No duration/ambient; or a certification claim |
| Product bench (PWM-11) | Operator end-to-end sign-off on `S360-311-R4` (boot items 9a–9c + polarity/current/thermal) with operator/date/serial + attached evidence | Compile-pass or package test treated as a product bench |

**Out of scope (stays blocked regardless of answers):** RPM support
(`rpm_supported: false`; `TachIO`/`GPIO16` reserved; RPM →
`COMPONENT-SX1509-TACH-001`, future); WebFlash exposure (`PWM-15`,
`NEEDS WEBFLASH ACCESS`); release artifact (`RELEASE-PWM-001`); import
readiness (`WF-IMPORT-PWM-001`); hardware-stable promotion (`S360-311`
stays `cataloged_unverified` unless policy allows); compliance approval
(board is SELV — `COMPLIANCE-001` does not apply).

**Next PR:** if the operator uploads / answers the checklist with bench
evidence → **`S360-311-BENCH-RESULT-001`** (record results, close the
rows it proves); while evidence is missing → `S360-311-BENCH-RESULT-001`
stays gated. WebFlash wrapper / build PRs stay blocked.

### 5B. S360-311-BENCH-RESULT-001 — FanPWM operator bench result (2026-05-26)

The operator (`@wifispray`) ran the §5A bench and reported a result.
`S360-311-BENCH-RESULT-001` **records** it (cross-lane index copy; the
canonical board-side record is
[`s360-311-r4-pwm.md` §S360-311-BENCH-RESULT-001](hardware/s360-311-r4-pwm.md#s360-311-bench-result-001--fanpwm-operator-bench-result-2026-05-26)).
Evidence type is **operator notes only** — no photo / video / scope /
multimeter log / thermal image — recorded as an operator attestation
(provenance: operator `@wifispray`, 2026-05-26), the same evidence class
that closed the package-evidence rows in `S360-310-BENCH-EVIDENCE-001`.

**Operator answers (recorded):** board tested = **S360-311-R4**;
fan/load = **Arctic P14 Plus** (12 V 4-wire PWM); supply = **12 V** from
the on-board **MT3608 boost** (~**2 A** available); **all 4 channels
(`J1`/`J2`/`J4`/`J5`) tested individually for speed / control**; **all 4
ran simultaneously for 1+ hour with no heat issue noticed**; **increasing
duty increased fan speed** (non-inverting, no inversion required) across
**low / medium / high** duty (qualitative); **fans stayed on at the last
commanded speed during restart**; per-channel current **not measured**;
aggregate current **not measured**; TachIO / GPIO16 **not measured**;
operator summary **confirms working.**

**Gate dispositions:**

| Gate / blocker | Disposition |
|---|---|
| PWM polarity (`PWM-10`) | **CLOSED** — observed behaviour, non-inverting (contract accepts observed behaviour) |
| Four-channel individual speed/control (`PWM-11`) | **CLOSED** — operator-attested |
| All-four simultaneous operation (`PWM-11`) | **CLOSED** — operator-attested |
| Restart retained last commanded speed (`PWM-11`) | **CLOSED** — operator-attested |
| Product bench end-to-end (`PWM-11`) | **CLOSED** — functional, operator-notes-only (measured current/thermal carried by `PWM-6` / `PWM-13`) |
| Board revision tested (`PWM-3`) | **PARTIAL** — `S360-311-R4` recorded; silkscreen pin-1 / UART routing still bench |
| Fan/load model + supply (`PWM-6`) | **PARTIAL** — Arctic P14 Plus + 12 V MT3608 (~2 A) recorded; measured current / ceiling / inrush still open |
| Qualitative thermal 1+ hour (`PWM-13`) | **PARTIAL** — no-heat note recorded; measured °C / IR / thermocouple / EMI still open |
| Per-channel + aggregate current (`PWM-6`) | **OPEN** — not measured |
| Measured thermal temperature (`PWM-13`) | **OPEN** — qualitative only |
| TachIO / GPIO16 (`PWM-12`) | **OPEN / deferred** — not measured; not an RPM claim |
| RPM support (`PWM-12`) | **OPEN** — stays unsupported (`rpm_supported: false`) |
| WebFlash live access / module-availability (`PWM-15`, `WF-1`/`WF-2`) | **OPEN** — `NEEDS WEBFLASH ACCESS` |
| WebFlash wrapper / build / artifact / import (`PWM-15` / `RELEASE-PWM-001` / `WF-IMPORT-PWM-001`) | **OPEN** — gated |
| Release readiness (`RELEASE-PWM-001`) | **OPEN** — gated |
| Hardware-stable promotion | **OUT OF SCOPE** — not promoted; `S360-311` stays `cataloged_unverified` |
| Compliance approval (`PWM-14` / `CMP-2`) | **N/A** — SELV; `COMPLIANCE-001` does not apply |

**Exact remaining evidence checklist:** (1) measured current per channel;
(2) measured aggregate current with all 4 active + MT3608 measured
ceiling / sag + inrush; (3) measured thermal temperature or a documented
thermal method, **if** policy requires more than the recorded qualitative
1+ hour observation; (4) optional TachIO / GPIO16 observation **only if**
RPM / diagnostics ever become in scope (not an RPM claim); (5) photo /
video / log evidence **if** policy requires more than the operator-notes-
only attestation recorded here.

**Next PR:** **`S360-311-CURRENT-THERMAL-001`** for the measured current /
thermal rows. WebFlash stays separate and blocked
(`WEBFLASH-PWM-LIVE-CHECK-001` behind `sense360store/WebFlash` access);
**no** `WEBFLASH-PWM-001` wrapper is recommended until measured
current / thermal *and* the WebFlash live classification are done.

### 5C. S360-312-BENCH-EVIDENCE-REQUEST-001 — FanDAC detailed bench checklist & evidence contract (2026-05-27)

`S360-312-BENCH-EVIDENCE-REQUEST-001` expands the short FanDAC items in
§5 into one precise, operator-answerable evidence request. It is
**documentation only** — it requests evidence, records none, and changes
no behaviour. The canonical board-side copy lives in
[`s360-312-r4-fandac.md` §S360-312-BENCH-EVIDENCE-REQUEST-001](hardware/s360-312-r4-fandac.md#s360-312-bench-evidence-request-001--fandac-bench-evidence-checklist--contract-2026-05-27);
this is the cross-lane index copy.

**Drive re-search (2026-05-27).** A fresh search (`S360-312`,
`S360-312-R4`, `FanDAC`, `GP8403`, `Cloudlift`, `Cloudlift S12`, `0-10V`,
`VOUT`, `voltage reading`, `DAC bench`, `harness`, photos / videos /
spreadsheets / logs) found **no bench artifact** — only **design / CAD**
material: the `Fan_GP8403` design set (`Fan_GP8403.kicad_sch` + the
timestamped `Fan_GP8403-*.zip` gerber/CPL snapshot series + the related
`GP8403.zip` / `GP8403-Module`, from the hardware design source), the
canonical `S360-312-R4.pdf` schematic (from the PCB design owner —
already committed byte-identical as
[`schematics/S360-312-R4.pdf`](hardware/schematics/S360-312-R4.pdf)), and
the unchanged `Sense360_R4_Tracker` (2026-05-18). This is recorded for
provenance only, closes no bench blocker, and **no Drive file is committed
by this PR**. So `S360-312-BENCH-RESULT-001` stays gated until the
operator uploads / answers the checklist below.

**Operator checklist (fill in; leave `UNANSWERED` rather than guess):**

| # | Item | Feeds |
|---|---|---|
| 1 | Board revision tested (silkscreen P/N + rev; note if blank per `G01`) | DAC-8b |
| 2 | `J3` `out0`/`out1` silkscreen transposition — read the printed text (layout shows pin-1 `2vout0`=`IC2` VOUT0 silk `out1`; transposed?) | DAC-8b |
| 3 | Actual `J3` channel mapping observed (drive `IC2` VOUT0/VOUT1 one at a time; which physical pin) | DAC-8b |
| 4a | Voltage mode tested — 0–10 V? | DAC-12 |
| 4b | Voltage mode tested — 0–5 V? (or `NOT TESTED`) | DAC-12 |
| 5 | Both DAC channels tested (`J2` ch0/ch1 + `J3` ch0/ch1) | DAC-8d |
| 6 | Both channels tested simultaneously (vs one at a time) | DAC-8d |
| 7 | Controlled load / device tested (Cloudlift S12, DMM, simulator, scope, or other) | DAC-8d |
| 8 | Harness used (Cloudlift S12 harness, custom harness, bare probe / none) | DAC-8c |
| 9a | Voltage reading — low / 0 % command (V) | DAC-12 |
| 9b | Voltage reading — medium / 25–50 % command (V) | DAC-12 |
| 9c | Voltage reading — high / 75–100 % command (V) | DAC-12 |
| 10 | Did increasing command increase output voltage? (monotonic) | DAC-12 |
| 11 | Do channel labels match expected UI / product behaviour? | DAC-8b / DAC-12 |
| 12 | Noise / flicker / instability | DAC-8d |
| 13 | Thermal observation (GP8403 / MT3608 boost / board; duration) | DAC-8d |
| 14 | Photos / videos / logs attached | all |
| 15 | Operator / date / source / provenance (who, when, serial, Drive path) | all |

**Pass/fail evidence contract:**

| Blocker | Closes when (PASS) | FAIL |
|---|---|---|
| `J3` silkscreen transposition (DAC-8b) | Photo / read of printed `J3` `out0`/`out1` silk + observed per-channel mapping (items 1–3, 11) | Layout-only inference; "looks right" with no per-channel drive test |
| Cloudlift S12 harness (DAC-8c) | Conductor-by-conductor trace `J2`/`J3` → S12 fan input, harness identified (items 7–8) | Assumed pinout; "straight through" without verification |
| Cloudlift S12 product bench (DAC-8d) | Both channels (ideally simultaneous) into the controlled load + noise/flicker + thermal + operator/date/serial + evidence (items 5–7, 12–15) | Compile-pass / package test treated as a product bench; single-channel spot check called a full bench |
| Voltage-mode / linearity (DAC-12) | Output readings at low/medium/high (or 0/25/50/75/100 %) for mode(s) tested showing increasing command → increasing output, 0–10 V (and 0–5 V if tested) recorded (items 4a–4b, 9a–10) | Mode asserted not measured; no command→output direction; per-output 0–5 V + 0–10 V mix on one GP8403 (forbidden by DAC-7) |

**Out of scope (stays blocked regardless of answers):** per-output range
mixing on one GP8403 (`DAC-7`, hard guardrail — register `0x01` chip-level,
one `V5V` per chip → `+12V`); WebFlash exposure (`DAC-15`, `NEEDS WEBFLASH
ACCESS`; drift #17); release artifact (`RELEASE-DAC-001`); import readiness
(`WF-IMPORT-DAC-001`); hardware-stable promotion (`DAC-14`; `S360-312` stays
`cataloged_unverified`); Cloudlift-ready / production voltage-control
product claim; compliance approval (board is SELV — `COMPLIANCE-001` does
not apply).

**Next PR:** if the operator uploads / answers the checklist with bench
evidence → **`S360-312-BENCH-RESULT-001`** (record results, close the rows
it proves); while evidence is missing → `S360-312-BENCH-RESULT-001` stays
gated. WebFlash wrapper / build PRs stay blocked.

### 5D. S360-311-CURRENT-THERMAL-EVIDENCE-REQUEST-001 — FanPWM current & thermal checklist & contract (2026-05-27)

`S360-311-CURRENT-THERMAL-EVIDENCE-REQUEST-001` expands the brief "exact
remaining evidence checklist" in §5B into a precise, operator-answerable
**measured current / thermal** request, so the later result PR
(`S360-311-CURRENT-THERMAL-001`) is small and evidence-backed. It is
**documentation only** — it requests evidence, records none, and changes
no behaviour. The canonical board-side copy lives in
[`s360-311-r4-pwm.md` §S360-311-CURRENT-THERMAL-EVIDENCE-REQUEST-001](hardware/s360-311-r4-pwm.md#s360-311-current-thermal-evidence-request-001--fanpwm-current--thermal-evidence-checklist--contract-2026-05-27);
this is the cross-lane index copy. Scope is per
`PWM-BLOCKER-RECLASSIFY-001` (§2A): measured current (`PWM-6`) / thermal
(`PWM-13`) gate **only** WebFlash / release / hardware-stable /
electrical-margin, **not** repo / package / product / config work.

**Drive re-search (2026-05-27).** A fresh search (`S360-311`,
`S360-311-R4`, `FanPWM`, `PWM`, `current`, `thermal`, `inrush`, `MT3608`,
`bench`, `fan`, spreadsheets / PDFs / photos) found **no measurement
artifact** — only **design / CAD** material (the `12vFan_PWM_PulseCounter`
set incl. `PWM.png`, the canonically-named `S360-311-R4` Drive folder
owned by the PCB design owner with KiCad sources /
gerbers / CPL / STEP / BOM / schematic PDF / renders, and the unchanged
`Sense360_R4_Tracker`). Same artifact class as the committed
[`schematics/S360-311-R4.pdf`](hardware/schematics/S360-311-R4.pdf),
recorded for provenance only, **no Drive file committed**. So
`S360-311-CURRENT-THERMAL-001` stays gated until the operator supplies the
measured rows below.

**Operator checklist (fill in; leave `UNANSWERED` rather than guess):**

| # | Item | Feeds |
|---|---|---|
| 1 | Board revision tested (start: `S360-311-R4`) | PWM-3 |
| 2 | Fan model + label current rating (start: Arctic P14 Plus) | PWM-6 |
| 3 | Supply voltage (start: 12 V MT3608) | PWM-6 |
| 4 | Measured supply current (total A; method) | PWM-6 |
| 5 | Per-channel current at full speed (A per `J1`/`J2`/`J4`/`J5`) | PWM-6 |
| 6 | Aggregate current, all four channels active (total A) | PWM-6 |
| 7 | Inrush / startup current (peak A; locked-rotor — if measurable) | PWM-6 |
| 8 | MT3608 input / output current or measured ceiling (sag / dropout) | PWM-6 |
| 9 | Thermal method (IR / thermal camera / thermocouple / qualitative only) | PWM-13 |
| 10 | Test duration (start: 1+ hour all-four) | PWM-13 |
| 11 | Ambient temperature (°C) | PWM-13 |
| 12 | Hottest component / location | PWM-13 |
| 13 | Measured max temperature (°C, or `qualitative only`) | PWM-13 |
| 14 | Did all four channels run at high / full duty? | PWM-6 / PWM-13 |
| 15 | Any voltage drop, instability, or reset? | PWM-6 |
| 16 | TachIO / GPIO16 observation (only if tested) — **no RPM claim** | PWM-12 (deferred) |
| 17 | Photos / videos / logs (if available) | all |
| 18 | Operator / date / source / provenance | all |

**Pass/fail evidence contract:**

| Blocker | Closes when (PASS) | FAIL |
|---|---|---|
| Per-channel current (PWM-6) | Measured A per channel at full speed with meter / method (items 2–5, 14) | Fan-label / datasheet rating only |
| Aggregate current (PWM-6) | Measured total + supply current + inrush if measurable (items 4, 6–7, 14) | Single-channel × 4; no measured aggregate |
| MT3608 ceiling (PWM-6) | Measured input / output current or documented ceiling + sag note (items 8, 15) | "~2 A available" quoted as measured ceiling |
| Electrical margin (PWM-6) | Measured aggregate + inrush vs ceiling + voltage-drop / reset answer (items 6–8, 15) — characterisation, **not** certification | "Looks fine" with no headroom; or a certification claim |
| Measured thermal (PWM-13) | Method + duration + ambient + hottest location + measured max °C (items 9–13), or explicit `qualitative only` | "No heat issue" with no method / duration / ambient |

**Out of scope (stays blocked regardless of answers):** RPM support
(`rpm_supported: false`; `TachIO`/`GPIO16` reserved; RPM →
`COMPONENT-SX1509-TACH-001`, future); WebFlash exposure (`PWM-15`,
`NEEDS WEBFLASH ACCESS`); release artifact (`RELEASE-PWM-001`); import
readiness (`WF-IMPORT-PWM-001`); hardware-stable promotion (`S360-311`
stays `cataloged_unverified`); compliance approval (board is SELV —
`COMPLIANCE-001` does not apply).

**Next PR:** if the operator supplies the measured rows →
**`S360-311-CURRENT-THERMAL-001`** (record results, close the rows it
proves); while evidence is missing → it stays gated. WebFlash wrapper /
build PRs stay blocked.

### 5E. S360-310-SAFETY-EVIDENCE-REQUEST-001 — FanRelay detailed safety / `GPIO3` checklist & evidence contract (2026-05-27)

`S360-310-SAFETY-EVIDENCE-REQUEST-001` expands the short FanRelay items in
§5 into one precise, operator- / qualified-person-answerable evidence
request. It is **documentation only** — it requests evidence, records none,
and changes no behaviour. The canonical board-side copy lives in
[`s360-310-r4-relay.md` §S360-310-SAFETY-EVIDENCE-REQUEST-001](hardware/s360-310-r4-relay.md#s360-310-safety-evidence-request-001--fanrelay-safety--gpio3-evidence-checklist--contract-2026-05-27);
this is the cross-lane index copy. Package / product / full-compile are
complete (`PACKAGE-RELAY-001` / PR #562, `PRODUCT-RELAY-001` / PR #564,
`FW-COMPILE-RELAY-FULL-FIX-001` / PR #578; run `26364679370`), so the lane
is **safety / operator / qualified-person / WebFlash-access gated, not repo
gated** (see §2C, scope-classified by `RELAY-BLOCKER-RECLASSIFY-001`).

**Drive re-search (2026-05-27).** A fresh search (`S360-310`, `S360-310-R4`,
`FanRelay`, `Relay`, `GPIO3`, `competent person`, `relay safety`,
`sign-off`, `safety`, plus boot / scope / load / thermal / photo / log
terms) found **no safety / `GPIO3` / competent-person artifact** — only
**design / CAD** material: the legacy `RelayBoard-Module` set
(`RelayBoard.pdf` / `.xlsx` BOM / `RelayBoardGerbers.zip` /
`RelayBoardpositions.csv` / `Relay.png`) and a canonically-named
`S360-310-R4` set (from the PCB design owner: KiCad
sources, `S360-310-R4_GERBERS.zip`, `positions.csv` CPL, STEP,
`S360-310-R4_BOM.xlsx`, `S360-310-R4.pdf` schematic, `Relay_logo.pretty`,
renders `_2`–`_6.png`), plus the unchanged `Sense360_R4_Tracker` and
`Current PRs.xlsx`. This is the same artifact class as the committed
[`schematics/S360-310-R4.pdf`](hardware/schematics/S360-310-R4.pdf), is
recorded for provenance only, closes no safety blocker, and **no Drive file
is committed by this PR** (re-confirms `BLOCKER-BURNDOWN-001` / PR #599). So
`S360-310-SAFETY-BENCH-RESULT-001` stays gated until the operator /
qualified person uploads / answers the checklist below.

**Operator / qualified-person checklist (fill in; leave `UNANSWERED` rather
than guess):** today the relay-boot rows are **pair-scoped operator-attested
only** (relay de-energised across 10 boot cycles × 4 power paths — USB / PoE
/ 5 V PSU / 240 V — on a single `S360-100-R4` + `S360-310-R4` pair; no scope
trace, no second unit; `S360-310-BENCH-EVIDENCE-001`).

| # | Item | Feeds |
|---|---|---|
| 1 | Board revision tested (`S360-310-R4` silkscreen P/N + rev; serial / batch) | RLY-3 |
| 2a | `GPIO3` boot behaviour (scope-traced level during power-on / boot) | RLY-3 |
| 2b | `GPIO3` reset behaviour (scope-traced level during reset / EN toggle; transient?) | RLY-3 |
| 2c | Relay state during boot (does `K1` stay de-energised through boot?) | RLY-3 |
| 2d | Relay state during restart / reboot (glitch / momentary energise?) | RLY-3 |
| 2e | `GPIO3` boot / strap conflict? (JTAG-select strap issue from relay-drive load — yes / no + evidence) | RLY-3 |
| 2f | Multiple units checked? (how many distinct pairs / serials; same result?) | RLY-3 |
| 3a | Relay load tested — load type (fan / resistive dummy / SSR input) | RLY-4 / RLY-6 |
| 3b | Relay load tested — voltage / current (switched-side V; measured A) | RLY-4 / RLY-6 |
| 3c | Relay load tested — AC/mains or low-voltage simulator (which) | RLY-4 / RLY-6 |
| 4a | Competent-person sign-off — who (name / role / qualification; not self-report) | RLY-4 |
| 4b | Sign-off — scope (install method / mains wiring / contact-rating use / enclosure) | RLY-4 / RLY-6 |
| 4c | Sign-off — date | RLY-4 |
| 4d | Sign-off — caveats / conditions | RLY-4 / RLY-6 |
| 5a | Manual / advanced warning text required (exact warning string) | RLY-5 |
| 5b | Install disclaimer (mains-safety disclaimer wording) | RLY-5 |
| 5c | WebFlash hidden / advanced-only? (yes / no; advanced / acknowledge-risk gate?) | RLY-5 |
| 6a | Thermal — duration / ambient (worst-case load run time; ambient °C) | RLY-6 |
| 6b | Thermal — `K1` / `Q1` / board observation (measured °C or qualitative; hottest location) | RLY-6 |
| 6c | Enclosure / spacing observations (creepage / clearance / isolation / mounting) — characterisation, not certification | RLY-6 |
| 7 | Photos / videos / logs attached | all |
| 8 | Operator / date / source / provenance (who, when, serial(s), Drive path) | all |

**Pass/fail evidence contract:**

| Blocker | Closes when (PASS) | FAIL |
|---|---|---|
| Production-wide `GPIO3` (RLY-3) | Scope-traced `GPIO3` reset / boot / strap captures across **multiple** units showing relay de-energised + no strap conflict (items 1, 2a–2f), serials + method recorded | Existing single-pair, operator-attested 10-cycle observation with no scope trace / no second unit; "boots fine" with no `GPIO3` capture |
| Competent-person sign-off (RLY-4) | **Independent** qualified person records who / scope / date / caveats for the mains install (items 4a–4d) | Build operator self-attesting; datasheet rating treated as a sign-off |
| Relay-load proof (RLY-4 / RLY-6) | Load test naming load type, switched V, measured A, and mains vs. low-voltage simulator (items 3a–3c) | "Fan switches" with no V / A and no mains-vs-simulator statement |
| Manual / advanced-warning UX (RLY-5) | Warning text + install disclaimer + WebFlash hidden / advanced-only decision stated (items 5a–5c) for a later WebFlash surface to implement | A WebFlash exposure shipped without the warning / disclaimer / advanced gate |
| Thermal / enclosure (RLY-6) | Worst-case-load thermal + enclosure / spacing observation with duration, ambient, hottest location (items 6a–6c) — characterisation, **not** certification | No duration / ambient; or a certification / compliance claim |

**Out of scope (stays blocked regardless of answers):** mains / compliance
certification (`RLY-6` / `CMP-1` — `K1` contact rating is datasheet
evidence, not board-level creepage / clearance / EMI / mains-safety cert);
WebFlash exposure (`RLY-8`, `WEBFLASH-RELAY-001`; `NEEDS WEBFLASH ACCESS`);
release artifact (`RELEASE-RELAY-001`); import readiness
(`WF-IMPORT-RELAY-001`); hardware-stable promotion (`S360-310` stays
`cataloged_unverified` unless policy allows); kit / default / recommended
membership (`S360-KIT-BATH-RELAY` future-expansion; default kit is
`S360-KIT-BATH-POE`); TRIAC separate-board-vs-merge (`RLY-7` / `T02`,
operator board decision).

**Next PR:** if the operator / qualified person uploads / answers the
checklist with evidence → **`S360-310-SAFETY-BENCH-RESULT-001`** (record
results, close the rows it proves); while evidence is missing →
`S360-310-SAFETY-BENCH-RESULT-001` stays gated. WebFlash wrapper / build /
artifact / import PRs stay blocked.

### 5F. S360-311-NATIVE-FANPWM-BENCH-001 — native FanPWM operator bench result (2026-05-29)

The operator (`@wifispray`) flashed the **native** ESP32-S3 GPIO FanPWM
firmware and re-ran the FanPWM bench. `S360-311-NATIVE-FANPWM-BENCH-001`
**records** it (cross-lane index copy; the canonical board-side record is
[`s360-311-r4-pwm.md` §S360-311-NATIVE-FANPWM-BENCH-001](hardware/s360-311-r4-pwm.md#s360-311-native-fanpwm-bench-001--native-fanpwm-operator-bench-result-2026-05-29)).
Evidence type is **operator notes only** — no photo / video / scope /
multimeter log / thermal image — recorded as an operator attestation
(provenance: operator `@wifispray`, 2026-05-29), the same evidence class
that closed the functional rows in `S360-311-BENCH-RESULT-001`.

This is **distinct** from `S360-311-BENCH-RESULT-001` (2026-05-26), which
ran the **legacy SX1509** composition. The native candidate re-binds
FanPWM control to **different pins** (`TachPMW1..4` ->
`IO10`/`IO11`/`IO12`/`IO39` via `ledc`, no SX1509), so the earlier
functional bench does **not** transfer — exactly as the legacy SX1509
full-compile run did not transfer to the native composition. This records
the native composition's **own** functional bench.

**Hardware setup (recorded):** Core = **S360-100-R4** (native ESP32-S3
GPIO fan path); PWM board = **S360-311-R4**; fan/load = **Arctic P14
Plus** (12 V 4-wire PWM), one per channel; supply = **12 V** from the
on-board **MT3608 boost** (~**2 A** available, capability not a measured
ceiling); firmware = **native composition** (`fan_pwm_native.yaml` via the
`ceiling-poe-fanpwm-native` skeleton); build source = native composition
**compile-proven at commit `643bbd3`** (S360-311-NATIVE-FANPWM-COMPILE-001),
operator-flashed local build (no published / release artifact).

**Functional PWM (recorded — PASS):** channel 1 (`J1`), channel 2 (`J2`),
channel 3 (`J4`), channel 4 (`J5`) each individually speed-controlled;
**all four simultaneous**; **low / medium / high** commands tracked
(qualitative; exact Hz / min%–max% not recorded); **restart retained the
last commanded speed**. Operator summary **confirms working on native
firmware.**

**Tach / RPM (recorded — NOT measured):** tach / RPM **not measured**;
no per-channel value; `rpm_supported` stays **false**; the native
pulse-counter inputs (`Pul_Cou1`/`Pul_Cou2`/`Pul_Cou4` ->
`IO17`/`IO18`/`IO9`) are internal-diagnostic only and were **not** read
for RPM; **`Pul_Cou3` (`IO46`) stays disabled / TBD** (collides with the
Core `fan_status_led_pin` `GPIO46`); **`TachIO` (`IO16`) stays reserved /
pending**.

**Power / current / thermal (recorded — NOT measured):** per-channel
current **not measured**; aggregate current **not measured**; MT3608
measured ceiling / inrush **not measured**; thermal observation duration
**not separately quantified** for the native run; heat / no-heat **not
measured** (no measured °C); **no instability / reset / brownout reported**
during the functional run (functional control + restart-retention
succeeded, indicating stable operation during the test).

**Outcome classification:** PWM functional (native) — **operator-attested
PASS**; tach / RPM — **not measured (unvalidated)**; current / thermal —
**not measured (unvalidated)**; release / WebFlash — **remain blocked**.

**Gate dispositions:**

| Gate / blocker | Disposition |
|---|---|
| Native FanPWM functional bench (`PWM-16`) | **FUNCTIONAL BENCH — operator-attested PASS (native)** (compile + functional; current/thermal/RPM carried by `PWM-6`/`PWM-12`/`PWM-13`) |
| Four-channel individual + simultaneous + restart-retention (native) | **PASS** — operator-attested |
| Per-channel + aggregate current (`PWM-6`) | **OPEN** — not measured |
| Measured thermal temperature (`PWM-13`) | **OPEN** — not measured |
| TachIO / GPIO16 + RPM (`PWM-12`) | **OPEN / deferred** — not measured; `rpm_supported: false`; `Pul_Cou3`/`IO46` disabled/TBD |
| WebFlash / release / import (`PWM-15` / `RELEASE-PWM-001` / `WF-IMPORT-PWM-001`) | **OPEN** — gated |
| Hardware-stable promotion | **OUT OF SCOPE** — `S360-311` stays `cataloged_unverified` |
| Compliance (`PWM-14` / `CMP-2`) | **N/A** — SELV; `COMPLIANCE-001` does not apply |

**Next PR:** **`S360-311-CURRENT-THERMAL-001`** for the measured current /
thermal rows (and a separate firmware-binding + bench PR for any RPM).
WebFlash stays separate and blocked (`WEBFLASH-PWM-LIVE-CHECK-001` behind
`sense360store/WebFlash` access); **no** `WEBFLASH-PWM-001` wrapper is
recommended until measured current / thermal *and* the WebFlash live
classification are done.

## 6. Guardrails honoured / non-claims

This PR is **documentation-only**. It does **not** edit
`packages/**`, `products/**`, `products/webflash/**`,
`config/webflash-builds.json`, `firmware/**`, `manifest.json`,
`firmware/sources.json`, release artifacts, checksums, build-info
manifests, any WebFlash repo file, `.github/workflows/**`,
`components/**`, or `include/**`. It adds **no** product YAML, **no**
WebFlash wrapper, flips **no** `webflash_build_matrix`, adds **no**
`artifact_name` or release artifact, claims **no** RPM support, and
makes **no** WebFlash-exposure / import / release / compliance /
hardware-stable readiness claim. It promotes **no** `schematic_status`.
No Drive / operator / WebFlash evidence is fabricated; missing evidence
is recorded as an operator question (§5). Release-One
(`Ceiling-POE-VentIQ-RoomIQ` / stable) and the LED preview
(`Ceiling-POE-VentIQ-RoomIQ-LED` / preview) are unchanged.

## 7. Validation evidence (run for this burn-down, 2026-05-26)

| Command | Result |
|---|---|
| `python3 tests/validate_configs.py` | ✅ all configuration files valid |
| `python3 scripts/validate_compile_targets.py --metadata-only` | ✅ 10 targets, metadata passed |
| `python3 tests/test_product_catalog.py` | ✅ 31 tests OK |
| `python3 tests/test_pwm_product_readiness.py` | ✅ OK |
| `python3 tests/test_dac_product_readiness.py` | ✅ OK |
| `python3 tests/test_firmware_combination_matrix.py` | ✅ OK |
| `python3 tests/test_firmware_build_gap_report.py` | ✅ OK |
| `python3 tests/validate_webflash_builds.py` | ✅ 2 builds checked, 0 failed |
| `python3 -m unittest discover -s tests -p "test_*.py"` | ✅ 756 tests OK (3 skipped) |
| WebFlash live read / `npm` tooling | ⚠️ NEEDS WEBFLASH ACCESS — repo read denied; no Node project here |

## 8. See also

- [`docs/webflash-drift-audit.md`](webflash-drift-audit.md) — cross-repo drift (WF rows).
- [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md) — per-family WebFlash posture.
- [`docs/product-readiness-matrix.md`](product-readiness-matrix.md) — per-family product-YAML posture.
- [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md) — per-family release-artifact posture.
- [`docs/repo-freshness-roadmap-audit.md`](repo-freshness-roadmap-audit.md) §5/§7/§8 — security + follow-up queue + blocker-cleanup notes.
- [`docs/hardware/s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md), [`s360-311-r4-pwm.md`](hardware/s360-311-r4-pwm.md), [`s360-312-r4-fandac.md`](hardware/s360-312-r4-fandac.md) — per-board blocker tables.
- [`docs/workflow-security-hardening.md`](workflow-security-hardening.md) — `SECURITY-ACTION-PINNING-001` inventory.
- [`UPCOMING_PR.md`](../UPCOMING_PR.md) — queue + cross-repo dependencies.

# Upcoming PR

This file tracks the next planned change set for the esphome-public repository.

## PRE-HW-PREP-FW-312-CLOSEOUT-001 — close out S360-312 DAC pre-hardware prep gaps

**Status:** documentation / CI closeout (promotes nothing, verifies nothing,
resolves no owed hardware item; no `schematic_status` flipped, no lifecycle
change, no WebFlash exposure, no `artifact_name` set, no release, no compile
or measurement fabricated). Closes the remaining narrative / forward-pointer
pre-hardware gaps for the S360-312 DAC (FanDAC) board.

### Summary

Audited the merged S360-312 design-complete work (PR #674) and **confirmed all
six deliverables D1–D6 are complete**:

* D1 pinmap — [`docs/hardware/s360-312-r4-dac.md`](docs/hardware/s360-312-r4-dac.md)
  + [`docs/hardware/s360-312-module-pinmap.md`](docs/hardware/s360-312-module-pinmap.md).
* D2 firmware — [`packages/expansions/fan_gp8403.yaml`](packages/expansions/fan_gp8403.yaml)
  (+ alias [`packages/expansions/fan_dac.yaml`](packages/expansions/fan_dac.yaml)).
* D3 bundle — [`products/bundles/ceiling-poe-fandac.yaml`](products/bundles/ceiling-poe-fandac.yaml)
  (config string `Ceiling-POE-FanDAC`).
* D4 compile-only — `config/compile-only-targets.json` (`validated-full-compile`,
  run `26364679370`).
* D5 release-note template + D6 bench/evidence matrix —
  [`docs/hardware/s360-312-r4-fandac.md`](docs/hardware/s360-312-r4-fandac.md).

The audit also confirmed that the repo **already records** the next FanDAC
hardware task under its established naming convention —
**`S360-312-BENCH-RESULT-001`** — in the §8 "Next PR queue" fan-driver evidence
lane (alongside the sibling `S360-311-CURRENT-THERMAL-001` and
`S360-310-SAFETY-BENCH-RESULT-001`), with the pre-written owed-evidence contract
`S360-312-BENCH-EVIDENCE-REQUEST-001` and the D6 fill-in matrix in
[`docs/hardware/s360-312-r4-fandac.md`](docs/hardware/s360-312-r4-fandac.md).
The remaining "gap" was therefore not a missing forward pointer but the absence
of a regression guard: nothing pinned that the FanDAC bench task stays named and
that no fabricated DAC bench evidence is introduced. This closeout adds that
guard. It is a forward pointer only: nothing is promoted, no bench evidence is
claimed, no new task id is minted, and no gate is flipped.

### What changed

* [`tests/test_roadmap_status_doc.py`](tests/test_roadmap_status_doc.py) — a new
  guard (`NextHardwareTaskTests`) asserting (a) the canonical FanDAC bench task
  `S360-312-BENCH-RESULT-001` stays named as the next real hardware task in the
  "Next PR queue" lane, (b) no parallel/duplicate bench id is introduced, and
  (c) no measured DAC bench evidence is claimed (`S360-312` stays
  `cataloged_unverified`).
* This `UPCOMING_PR.md` entry.

No `docs/sense360-roadmap-status.md`, `docs/pre-hardware-prep-plan.md`, or
`docs/hardware/s360-312-r4-fandac.md` content change was needed: the next-task
forward pointer (§8 "Next PR queue"), the §6 bench handoff row, and the D6
matrix already reference `S360-312-BENCH-RESULT-001`.

### Owed (recorded, not resolved)

The seven S360-312 hardware-evidence items stay **OWED** to
`S360-312-BENCH-RESULT-001` (no physical board exists yet); none is resolved here:

1. Measured voltage output (per channel).
2. GP8403 detection / I²C address.
3. Output range / calibration.
4. Fan / controller response.
5. Current draw under load.
6. Thermal under sustained load.
7. Harness / silkscreen confirmation.

### Guardrails (explicitly NOT changed)

* **No S360-312 bench evidence claimed** — no GP8403 detection, no voltage,
  current, thermal, or calibration measurement is fabricated; every D6 row stays
  unfilled / owed.
* **No WebFlash enabled** — no `config/webflash-builds.json` row, the `FanDAC`
  token stays absent, the WebFlash repo (`sense360store/webflash`) is untouched.
* **No `artifact_name` added**, **no `webflash_build_matrix` flip**, **no
  firmware published** — no release / tag / `.bin`, no `manifest.json` /
  [`firmware/sources.json`](firmware/sources.json) change.
* No `config/*.json` changed (`config/product-catalog.json`,
  `config/compile-only-targets.json`, `config/manual-firmware-artifacts.json`
  untouched); no `schematic_status` / lifecycle flip; nothing marked
  hardware-stable or verified; `S360-312` stays `cataloged_unverified`.
* No `packages/**` / `products/**` change; this PR is docs + tests only.

### Validation

* `python3 tests/validate_configs.py`
* `python3 scripts/validate_compile_targets.py --metadata-only`
* `python3 tests/test_product_catalog.py`
* `python3 tests/test_module_pinmaps.py`
* `python3 tests/test_compile_expansion_candidates.py`
* `python3 tests/test_roadmap_status_doc.py`
* `python3 -m unittest discover -s tests -p "test_*.py"`

---

## S360-311-CURRENT-THERMAL-001 — record FanPWM current and thermal evidence

**Status:** documentation-only bench-evidence record (promotes nothing, verifies
nothing, resolves no owed hardware item). Records the `S360-311-CURRENT-THERMAL-001`
bench pass (2026-05-29 first pass + **2026-05-31 re-run**) on the **native**
ESP32-S3 GPIO FanPWM composition (`S360-100-R4` Core + `S360-311-R4` PWM board),
following `PRE-HW-PREP-FW-311-001`.

### Summary

The operator (`@wifispray`) re-ran the queued current / thermal / tach bench pass.
The result is recorded **honestly**: **functional PWM re-confirmed PASS**
(operator-notes-only — no photo / video / scope / multimeter log / thermal image),
but **current, thermal, and tach/RPM were all NOT measured**. Per the project
no-fabrication rule, **no current / thermal / RPM value is inferred, estimated, or
back-filled** from the fan label, the MT3608 datasheet, or the supply capability.
`PWM-6` / `PWM-13` (current / thermal) and `PWM-12` (per-fan RPM) **stay owed**;
`rpm_supported` stays **false**. The board is **not** claimed hardware-stable.

### Recorded result (per the required evidence list)

* **PWM channel 1–4** — individually speed-controlled, **PASS** (operator-notes).
* **All-four simultaneous** — **PASS**.
* **High / medium / low command** — tracked commanded duty, **PASS**.
* **Restart retention** — last commanded speed retained across a restart, **PASS**.
* **Fan model / load** — **not re-specified** this pass; the established rig on
  file (Arctic P14 Plus, one per channel) is carried for provenance only, not
  re-attested as a 2026-05-31 measurement.
* **Supply used** — **not re-specified**; rig on file is the on-board MT3608 12 V
  boost (~2 A available capability, **not** a measured ceiling).
* **Per-channel current** — **NOT measured.**
* **Aggregate current** — **NOT measured** (no measured MT3608 ceiling / sag / inrush).
* **Thermal duration / result** — **NOT measured** (no sustained thermal run; no
  method / ambient / hottest-location / measured °C).
* **Tach / RPM** — **explicitly NOT measured**; `rpm_supported` stays false.
* **`Pul_Cou3` / `IO46`** — stays **disabled / TBD** (collides with the Core
  `fan_status_led_pin` `GPIO46`); `TachIO` / `IO16` stays reserved / pending.
* **`J3` silkscreen order / `J6`↔`J3` harness / `"NINE 4pin FANs"` label / `J3`
  11/12 UART routing** — **remain OWED;** none proven on this run.

### What changed

* [`docs/hardware/s360-311-r4-pwm.md`](docs/hardware/s360-311-r4-pwm.md) — new
  top-of-file `S360-311-CURRENT-THERMAL-001` re-run callout (2026-05-31); the
  existing `§S360-311-CURRENT-THERMAL-001` section header dated for both passes
  and a **2026-05-31 re-run** subsection added (functional re-confirmed;
  current / thermal / tach again not measured; every owed item restated).
* [`docs/hardware/s360-311-r4-fanpwm.md`](docs/hardware/s360-311-r4-fanpwm.md) —
  new **D6 bench-session result so far** subsection recording the two-pass outcome
  against the D6 matrix (T3 functional PASS; T4/T5/T6/T7/T8 + T1/T2/T9/T10/T11
  owed); the `Measured` / `Pass?` columns stay empty by design.
* [`docs/hardware/board-readiness-matrix.md`](docs/hardware/board-readiness-matrix.md)
  — new **Bench evidence (`S360-311-CURRENT-THERMAL-001`)** bullet under the
  `S360-311` subsection; `schematic_status` / lifecycle classifications unchanged.
* This `UPCOMING_PR.md` entry.

### Guardrails (explicitly NOT changed)

* **No WebFlash enabled** — no wrapper, no `config/webflash-builds.json` row, no
  WebFlash repo (`sense360store/webflash`) edit; the `FanPWM` token stays absent.
* **No `artifact_name` added**, **no `webflash_build_matrix` flip**, **no firmware
  published** — no release / tag / `.bin`, no `manifest.json` /
  [`firmware/sources.json`](firmware/sources.json) change.
* **No hardware-stable claim** — current / thermal / RPM stay unvalidated; the
  evidence does not support it, so it is not claimed.
* No `config/*.json` changed — `S360-311` stays `cataloged_unverified`, no
  `schematic_status` flip, no lifecycle change; nothing marked `verified`.
* No `packages/**` / `products/**` behaviour change; no compile re-run or compile
  result fabricated; no measurement / photo / video / log fabricated — the intake
  was blank and is recorded as such. Release-One (`Ceiling-POE-VentIQ-RoomIQ` /
  stable) and the LED preview are untouched.

### Validation

* `python3 tests/validate_configs.py`
* `python3 scripts/validate_compile_targets.py --metadata-only`
* `python3 tests/test_native_fanpwm_yaml.py`
* `python3 tests/test_pwm_product_readiness.py`
* `python3 tests/test_product_catalog.py`
* `python3 -m unittest discover -s tests -p "test_*.py"`

---

## PRE-HW-PREP-FW-311-001 — bring the S360-311 PWM firmware to design-complete

**Status:** design-complete annotation + firmware finalisation (promotes
nothing, verifies nothing, resolves no owed hardware item; no `schematic_status`
flipped, no lifecycle change, no WebFlash exposure, no `artifact_name` set, no
release, no compile result fabricated). Executes slice #3
(`PRE-HW-PREP-FW-311-001`) of
[`docs/pre-hardware-prep-plan.md`](docs/pre-hardware-prep-plan.md).

### Summary

Records the `Sense360 PWM` board (`S360-311-R4`, FanPWM) as **design-complete**
— a prose / documentation annotation that is explicitly **not** `verified`
(per [`docs/pre-hardware-prep-plan.md` §1.2 / §1.4](docs/pre-hardware-prep-plan.md)).
Builds on the completed `SX1509-RECONCILE-001` + `PACKAGE-PWM-001`: finalises
[`packages/expansions/fan_pwm_native.yaml`](packages/expansions/fan_pwm_native.yaml)
as the design-complete **four-channel** native PWM+tach driver (four `ledc`
PWM-drive outputs `TachPMW1..4` -> `IO10`/`IO11`/`IO12`/`IO39` feeding four
`fan: speed` controllers; three native `pulse_counter` tach inputs
`Pul_Cou1`/`2`/`4` -> `IO17`/`IO18`/`IO9` as the per-fan-RPM mechanism, internal
diagnostic / no RPM claim), and reconciles the stale single-channel
`fan_pwm_pin: GPIO4` / `fan_tach_pin: GPIO5` placeholder in
[`packages/hardware/sense360_core_mapping.yaml`](packages/hardware/sense360_core_mapping.yaml)
to the four-channel native map (marked legacy/superseded). The FanPWM bundle
(D3) and the native compile-only targets (D4, `validated-full-compile` by
`S360-311-NATIVE-FANPWM-COMPILE-001`, local run 2026-05-28, commit `643bbd3`,
rc=0) were already landed by `SX1509-RECONCILE-001`. This slice adds the missing
design-complete pieces (D5 + D6) and the prose annotation, all from the
committed schematic.

### What changed

* [`packages/expansions/fan_pwm_native.yaml`](packages/expansions/fan_pwm_native.yaml)
  — header finalised from "NATIVE-GPIO CANDIDATE / NOT compile-proven /
  pending-ci" to "FINALISED / DESIGN-COMPLETE / compile-proven
  (validated-full-compile)", with the four-channel framing and the
  `Pul_Cou3`/`IO46` + `TachIO`/`IO16` owed notes made explicit. The
  `substitutions:` / `output:` / `fan:` / `sensor:` body is byte-identical (no
  pin / entity-name change; the recorded compile still holds).
* [`packages/hardware/sense360_core_mapping.yaml`](packages/hardware/sense360_core_mapping.yaml)
  — the stale single-channel `fan_pwm_pin: GPIO4` / `fan_tach_pin: GPIO5`
  placeholder marked **legacy / superseded** against the four-channel native
  map (header pin-map note, substitution banner, the `fan_pwm_output` /
  `fan_tach_sensor` blocks, and the SX1509 I²C address-table comment). The
  `GPIO4`/`GPIO5` values are retained as the legacy source-of-truth alias
  (consumed by `fan_control_advanced_profile.yaml`); the production
  `roomiq_sen0609_uart` radar binding (GPIO5/GPIO4) is untouched.
* [`docs/hardware/s360-311-r4-fanpwm.md`](docs/hardware/s360-311-r4-fanpwm.md)
  — new **Design-complete status** section (the four-condition §1.1 checklist
  with the compile-run reference), new **D5** release-note template +
  artifact-naming scheme (template only — no artifact, no release), new **D6**
  pre-written bench / evidence test matrix (silkscreen `J3` order, `J6`↔`J3`
  harness, native PWM drive on `IO10/11/12/39`, per-fan + aggregate current,
  thermal envelope, per-fan RPM via native `pulse_counter`, `Pul_Cou3`/`IO46`
  collision, `"NINE 4pin FANs"` label, `J3` 11/12 UART routing, `TachIO` role).
* [`docs/hardware/board-readiness-matrix.md`](docs/hardware/board-readiness-matrix.md)
  — added a `design_status: design-complete` prose bullet to the `S360-311`
  subsection; `Hardware evidence`, `schematic_status`, and `Package YAML`
  classifications unchanged.
* [`docs/pre-hardware-prep-plan.md`](docs/pre-hardware-prep-plan.md) — §3.1
  Executed note + §7 ordered-slice-sequence row 3 marked **DONE**.
* This `UPCOMING_PR.md` entry.

### Owed (recorded, not resolved)

The hardware-only items stay **OWED** to `HW-PINMAP-311` and are captured in the
D6 matrix, not resolved here: the `"NINE 4pin FANs"` label vs four-connector
question, the `J3` pins 11/12 UART-routing question, the `J3` 1-to-13
silkscreen order, the `J6`↔`J3` 13-pin harness, the `Pul_Cou3`/`IO46`
fourth-tach collision with the Core `fan_status_led_pin`, the `TachIO`/`IO16`
shared-net role, PWM polarity (`PWM-6`), per-fan + aggregate fan current, the
thermal envelope, and per-fan RPM via native `pulse_counter` (`PWM-13`).
`PWM-6` / `PWM-13` stay owed; `S360-311-CURRENT-THERMAL` is the queued bench
session that fills the D6 checklist.

### Guardrails (explicitly NOT changed)

* No `packages/boards/` board package for `S360-311` (that promotion is gated
  on HW-PINMAP-311 evidence per the plan); the driver package and bundle are
  finalised only.
* The native driver's `substitutions:` / `output:` / `fan:` / `sensor:` body is
  byte-identical (only comments/header changed); the bundle
  [`products/bundles/ceiling-poe-fanpwm.yaml`](products/bundles/ceiling-poe-fanpwm.yaml)
  is untouched (config string `Ceiling-POE-FanPWM` and entity names
  `${friendly_name} Fan 1..4` byte-identical, no `artifact_name`).
* Production `GPIO4`/`GPIO5` radar-UART binding in
  [`packages/boards/s360-100-core.yaml`](packages/boards/s360-100-core.yaml) is
  unchanged; the legacy SX1509 packages (`fan_pwm.yaml` / `fan_pwm_sx1509.yaml`)
  and the historical SX1509 proof are not revived.
* No `config/*.json` changed — `S360-311` stays `cataloged_unverified`, no
  `schematic_file`, no lifecycle / `webflash_build_matrix` / `artifact_name`
  change. `design-complete` is a doc annotation, never a JSON field.
* No `schematic_status` flip; nothing marked `verified` or
  design-complete-as-verified; no PWM current / thermal / RPM bench evidence
  claimed; `PWM-6` / `PWM-13` not closed; `rpm_supported` stays false; no
  compile result fabricated (ESPHome unavailable here; the recorded compile is
  the already-committed local run `643bbd3`).
* No WebFlash exposure, no `artifact_name`, no `webflash_build_matrix` flip, no
  `config/webflash-builds.json` row, no release / tag / artifact; the `FanPWM`
  token stays absent from `config/webflash-builds.json`.
* The production product and `tests/test_release_one_entity_names.py` are
  untouched; no edit to `manifest.json` / [`firmware/sources.json`](firmware/sources.json);
  the WebFlash repo (`sense360store/webflash`) is untouched.

### Validation

* `python3 tests/validate_configs.py`
* `python3 scripts/validate_compile_targets.py --metadata-only`
* `python3 tests/test_native_fanpwm_yaml.py`
* `python3 tests/test_pwm_product_readiness.py`
* `python3 tests/test_product_catalog.py`
* `python3 tests/test_release_one_entity_names.py`
* `python3 tests/test_product_substitutions.py`
* `python3 -m unittest discover -s tests -p "test_*.py"`

---

## PRE-HW-PREP-FW-312-001 — bring the S360-312 DAC firmware to design-complete

**Status:** design-complete annotation (docs-only; promotes nothing, verifies
nothing, resolves no owed hardware item; no `schematic_status` flipped, no
lifecycle change, no WebFlash exposure, no `artifact_name` set, no release, no
compile result fabricated). Executes slice #2
(`PRE-HW-PREP-FW-312-001`) of
[`docs/pre-hardware-prep-plan.md`](docs/pre-hardware-prep-plan.md).

### Summary

Records the `Sense360 DAC` board (`S360-312-R4`, FanDAC) as **design-complete**
— a prose / documentation annotation that is explicitly **not** `verified`
(per [`docs/pre-hardware-prep-plan.md` §1.2 / §1.4](docs/pre-hardware-prep-plan.md)).
The dual-GP8403 driver (D2), the FanDAC bundle (D3), and the compile-only
targets (D4) were already landed by the earlier FanDAC slices
(`PACKAGE-DAC-001` / `PRODUCT-DAC-001` / `FW-COMPILE-DAC-001`; the
[`packages/expansions/fan_gp8403.yaml`](packages/expansions/fan_gp8403.yaml)
driver already exposes both DACs `IC1`/`IC2` on the shared `core_i2c` bus as
four neutral outputs, with the stale `GPIO39`/`GPIO40` header comment already
corrected to the Core `IO48`/`IO45` bus), and D1 by `HW-PINMAP-312` /
`HW-PINMAP-312-FOLLOWUP`. This slice adds the missing design-complete pieces
(D5 + D6) and the design-complete prose annotation, all from the committed
schematic; it edits no YAML and no `config/*.json`.

### What changed

* [`docs/hardware/s360-312-r4-fandac.md`](docs/hardware/s360-312-r4-fandac.md)
  — new **Design-complete status** section (the four-condition §1.1 checklist
  with the compile-run link), new **D5** release-note template + artifact-naming
  scheme (template only — no artifact, no release), new **D6** pre-written
  bench / evidence test matrix (the fill-in checklist covering the verify-pending
  D1 items plus per-channel output linearity/range, Cloudlift drive, and the
  voltage-mode jumper), and a reconciliation-log row.
* [`docs/hardware/board-readiness-matrix.md`](docs/hardware/board-readiness-matrix.md)
  — added a `design_status: design-complete` prose row to the `S360-312`
  subsection with a link to the compile run; `Readiness`, `schematic_status`,
  and `Package status` are unchanged.
* [`docs/pre-hardware-prep-plan.md`](docs/pre-hardware-prep-plan.md) — §3.2
  Executed note + §7 ordered-slice-sequence row 2 marked **DONE**.
* This `UPCOMING_PR.md` entry.

### Owed (recorded, not resolved)

The hardware-only items stay **OWED** to `HW-PINMAP-312-FOLLOWUP` and are
captured in the D6 matrix, not resolved here: the Core-`J7`-`+5V`-vs-module-
`J1`-`+3.3V` rail question, the `SW1`/`SW2` DIP-switch → I²C-address mapping,
the `J2`/`J3` Cloudlift output silkscreen pin order (incl. the `J3` out0/out1
transposition), and the `5V`/`10V` voltage-mode jumper identification.

### Guardrails (explicitly NOT changed)

* No `packages/boards/` board package for `S360-312` (that promotion is gated
  on HW-PINMAP-312 evidence); the driver package and bundle are finalised only.
* No YAML edited — [`packages/expansions/fan_gp8403.yaml`](packages/expansions/fan_gp8403.yaml),
  [`packages/expansions/fan_dac.yaml`](packages/expansions/fan_dac.yaml), and
  [`products/bundles/ceiling-poe-fandac.yaml`](products/bundles/ceiling-poe-fandac.yaml)
  are byte-identical (config string `Ceiling-POE-FanDAC` and the artifact-name
  scheme unchanged).
* No `config/*.json` changed — `S360-312` stays `cataloged_unverified`, no
  `schematic_file`, no lifecycle / `webflash_build_matrix` / `artifact_name`
  change. `design-complete` is a doc annotation, never a JSON field.
* No `schematic_status` flip; nothing marked `verified` or
  design-complete-as-verified; no DAC bench / hardware evidence claimed; no
  compile result fabricated (ESPHome unavailable here; the recorded compile is
  the already-committed run `26364679370`).
* No WebFlash exposure, no `artifact_name`, no `webflash_build_matrix` flip, no
  `config/webflash-builds.json` row, no release / tag / artifact.
* FanDAC ↔ AirIQ mutex and the fan-driver `max-one-of` rule unchanged; the
  production product and `tests/test_release_one_entity_names.py` untouched.
* No edit to `manifest.json` / [`firmware/sources.json`](firmware/sources.json);
  the WebFlash repo (`sense360store/webflash`) is untouched.

### Validation

* `python3 tests/validate_configs.py`
* `python3 scripts/validate_compile_targets.py`
* `python3 tests/test_release_one_entity_names.py`
* `python3 -m unittest discover -s tests -p "test_*.py"` (1175 tests, 3 skipped)

---

## SX1509-RECONCILE-001 — migrate fan PWM path off SX1509 to native GPIO

**Status:** design-complete fan-path migration (NOT verified, NOT released; no
board promoted, no `schematic_status` flipped, no WebFlash exposure, no
`artifact_name`, no compile result fabricated). Executes slice #1
(`PRE-HW-PREP-SX1509-RECONCILE-001`) of
[`docs/pre-hardware-prep-plan.md`](docs/pre-hardware-prep-plan.md).

### Summary

Reconciles the deprecated SX1509 I/O expander out of the fan PWM path per the
operator confirmation that the SX1509 is no longer used and the schematic-printed
native fan GPIO map ([`docs/hardware/s360-100-native-fan-gpio-map.md`](docs/hardware/s360-100-native-fan-gpio-map.md):
`TachPMW1..4` -> IO10/IO11/IO12/IO39, `Pul_Cou1/2/4` -> IO17/IO18/IO9, `TachIO`
= IO16). The FanPWM bundle is migrated to compose the native
`packages/expansions/fan_pwm_native.yaml` driver instead of the deprecated
`fan_pwm.yaml` -> `fan_pwm_sx1509.yaml` chain; the per-fan entity names
(`${friendly_name} Fan 1..4`) and the `Ceiling-POE-FanPWM` config string are
kept **byte-identical**, and no `artifact_name` is added. The native
composition is full-compile validated by structural parity to the native
compile-only skeleton (`S360-311-NATIVE-FANPWM-COMPILE-001`, commit `643bbd3`,
rc=0); the legacy SX1509 full-compile run `26414398902` is preserved as the
historical proof for the SX1509 skeleton only and does not transfer.

### What changed

* [`products/bundles/ceiling-poe-fanpwm.yaml`](products/bundles/ceiling-poe-fanpwm.yaml)
  — composes `packages/expansions/fan_pwm_native.yaml` (key
  `fan_pwm_native_module`) instead of the SX1509 `fan_pwm.yaml`; header /
  binding comments rewritten to the native path. Substitutions, config string,
  and entity names byte-identical.
* [`packages/boards/s360-100-core.yaml`](packages/boards/s360-100-core.yaml) —
  removed the stale `SX1509 expander` entry from the Core I²C-device comment
  (the SX1509 is no longer a current Core I²C device on the fan path).
* [`config/product-catalog.json`](config/product-catalog.json) /
  [`config/compile-only-targets.json`](config/compile-only-targets.json) — the
  current FanPWM product / product-compile-only rows retargeted to the native
  composition + native compile evidence; the legacy SX1509 compile-only
  skeleton row + run `26414398902` preserved unchanged as historical proof.
* [`packages/expansions/gpio_expander_sx1509.yaml`](packages/expansions/gpio_expander_sx1509.yaml)
  and [`packages/expansions/fan_12v_pwm.yaml`](packages/expansions/fan_12v_pwm.yaml)
  — added LEGACY / SUPERSEDED banners recording the **kept-with-reason**
  retirement disposition (no live binder, but read by tests and forbidden from
  global removal by `S360-100-NATIVE-FAN-GPIO-MAP-001`).
* [`tests/test_pwm_product_readiness.py`](tests/test_pwm_product_readiness.py)
  and [`tests/test_native_fan_gpio_map.py`](tests/test_native_fan_gpio_map.py)
  — updated to assert the migrated native composition (the bundle composes the
  native package, mirrors the native validated-full-compile skeleton, and no
  longer carries the legacy SX1509 banner).
* [`docs/pre-hardware-prep-plan.md`](docs/pre-hardware-prep-plan.md) — slice #1
  marked **DONE** (§5.3 executed-note + §7 table).
* This `UPCOMING_PR.md` entry.

### Retirement disposition (PRODUCT-DEP-001)

No SX1509 package is deleted. `fan_pwm.yaml` / `fan_pwm_sx1509.yaml` stay bound
by the preserved legacy compile-only skeleton (historical SX1509 compile proof,
required by `tests/test_native_fanpwm_yaml.py`); `gpio_expander_sx1509.yaml` and
`fan_12v_pwm.yaml` have no live `!include` binder but are read directly by
`tests/test_core_abstract_bus.py` / `tests/test_dac_product_readiness.py` and
may not be removed globally per `S360-100-NATIVE-FAN-GPIO-MAP-001`. All four are
therefore **kept-with-reason** with legacy/superseded banners; a hard delete is
left to a future cleanup PR once the doc/test references are also retired.

### Guardrails (explicitly NOT changed)

* Release-One (`Ceiling-POE-VentIQ-RoomIQ`) byte-identical — it uses no SX1509
  and no fan package; `tests/test_release_one_entity_names.py` passes untouched.
* No fan board verified / promoted; all stay `hardware-pending` / unverified
  (design-complete only). `S360-311` `schematic_status` stays
  `cataloged_unverified`.
* No WebFlash exposure, no `artifact_name`, no `webflash_build_matrix` flip, no
  `config/webflash-builds.json` row; FanPWM token stays absent.
* No PWM current/thermal evidence claimed; `PWM-6` / `PWM-13` stay owed;
  `rpm_supported` stays false.
* FanTRIAC stays `blocked` / `HW-005`; its SX1509 blocker-explanation comments
  are factual and left intact.
* No edit to `manifest.json` / `firmware/sources.json` (absent here); the
  WebFlash repo is untouched; no compile result fabricated.

### Validation

* `python3 tests/validate_configs.py`
* `python3 scripts/validate_compile_targets.py --metadata-only`
* `python3 tests/test_native_fanpwm_yaml.py`
* `python3 tests/test_pwm_product_readiness.py`
* `python3 tests/test_release_one_entity_names.py`
* `python3 tests/test_product_substitutions.py`
* `python3 -m unittest discover -s tests -p "test_*.py"` (1175 tests, 3 skipped)

---

## HW-SENSOR-SFA40-CORRECTION-001 — correct AirIQ HCHO sensor from SFA30 to SFA40

**Status:** metadata / docs-only (corrects a recorded part identity; promotes
nothing, verifies nothing, no gate closed, no `schematic_status` or lifecycle
flipped, no entity added)

### Summary

Corrects the formaldehyde / HCHO sensor identity on the `S360-210` AirIQ from
**SFA30** to **SFA40** — the newer Sensirion HCHO module the operator confirms
is the fitted / intended part — across the catalog, the feature/entity matrix
(JSON + MD), and the AirIQ board / readiness docs. The HCHO entity still does
**not** exist and stays gated; the SFA40 connector interface/address (bus, I²C
address, ESPHome driver) remains **verify-pending** in the AirIQ pin-map and is
not asserted here. This part-identity fix re-points the queued
`ENTITY-FILL-210-HCHO-001` fill slice at the correct sensor.

### What changed

* [`config/hardware-catalog.json`](config/hardware-catalog.json) — `S360-210`
  description connector list now reads `SFA40 HCHO`.
* [`config/feature-entity-matrix.json`](config/feature-entity-matrix.json) —
  AirIQ board note and the HCHO row label now read `SFA40`; the HCHO row note
  records that SFA40 is the newer module superseding the SFA30, that its
  connector interface/address is verify-pending, and that
  `ENTITY-FILL-210-HCHO-001` now targets the SFA40 and still depends on
  interface confirmation.
* [`docs/feature-entity-matrix.md`](docs/feature-entity-matrix.md) — AirIQ
  headline-gaps row now reads `SFA40 HCHO` with the newer-module /
  verify-pending note.
* [`docs/hardware-catalog.md`](docs/hardware-catalog.md) — `S360-210` row
  connector list now reads `SFA40 HCHO`.
* [`docs/hardware/board-readiness-matrix.md`](docs/hardware/board-readiness-matrix.md)
  — `S360-210` Role bullet now reads `SFA40 HCHO connector`.
* This `UPCOMING_PR.md` update.

### Guardrails (explicitly NOT changed)

* No HCHO (or any) sensor entity added; no package / board / product / bundle /
  expansion YAML edited. The HCHO entity stays absent and gated.
* SFA40 bus, I²C address, and ESPHome driver are **not** asserted — marked
  verify-pending.
* No `schematic_status` flip; no lifecycle / status promotion on `S360-210` or
  any board.
* No other board's sensor labels changed.
* No edit to [`config/webflash-builds.json`](config/webflash-builds.json),
  `manifest.json`, or [`firmware/sources.json`](firmware/sources.json).
* The WebFlash repo (`sense360store/webflash`) is untouched.

### Validation

* `python3 tests/validate_configs.py`
* `python3 tests/test_product_catalog.py`
* `python3 tests/test_roadmap_status_doc.py`
* `python3 -m unittest discover -s tests -p "test_*.py"`

---

## PRE-HARDWARE-PREP-PLAN-001 — plan the design-derived readiness program

**Status:** docs-only / planning (promotes nothing, verifies nothing, resolves
nothing; no gate closed; no `schematic_status` flipped)

### Summary

Authors [`docs/pre-hardware-prep-plan.md`](docs/pre-hardware-prep-plan.md), the
design-derived readiness program that brings the six driver / PSU boards
(`S360-310` / `S360-311` / `S360-312` / `S360-320` / `S360-400` / `S360-410`)
to a **design-complete** state from the schematic PDFs the repo already holds,
**ahead of hardware**, so the eventual bench session is pure test-and-record.
The plan defines a `design-complete` status concept that is explicitly distinct
from `verified` (firmware authored + compile-validated from design artifacts,
recorded as a doc/metadata annotation — never a `config/*.json` field — and
which **never flips `schematic_status` on its own**), enumerates the six
per-board deliverables, flags every gerber/BOM-dependent item as
**ARTIFACT-BLOCKED**, captures the operator-stated **SX1509 deprecation** as
its own early reconcile slice, fixes the per-board hardware-verification
handoff, and emits the ordered slice sequence.

### What changed

* New [`docs/pre-hardware-prep-plan.md`](docs/pre-hardware-prep-plan.md) —
  the program: `design-complete` policy + non-flip rule, per-board D1–D6
  deliverable tables, ARTIFACT-BLOCKED flags (clearance/creepage for the
  PoE `S360-410` and mains `S360-310`/`S360-320`/`S360-400` boards), the
  SX1509 reference inventory + native-GPIO resolution targets, the
  `design-complete → verified` bench handoff per board, and the ordered
  slice sequence.
* This `UPCOMING_PR.md` entry.

### Ordered slice sequence (queued; this PR authors none of them)

1. `PRE-HW-PREP-SX1509-RECONCILE-001` — re-bind the fan path to native
   ESP32-S3 GPIO; mark residual SX1509 fan refs legacy/superseded
   (coordinates with `CORE-ABSTRACT-BUS-001` + the native fan GPIO map).
2. `PRE-HW-PREP-FW-312-001` — `S360-312` DAC (native I²C, no SX1509 dep).
3. `PRE-HW-PREP-FW-311-001` — `S360-311` PWM (native re-bind; `PACKAGE-PWM-001`).
4. `PRE-HW-PREP-FW-310-001` — `S360-310` Relay (SELV logic side).
5. `PRE-HW-PREP-TESTMATRIX-SELV-001` — finalise the SELV bench matrices.
6. `PRE-HW-PREP-GERBER-REVIEW-001` *(ARTIFACT-BLOCKED)* — clearance/creepage
   reviews; **gated on gerbers + BOM being committed**.
7. `PRE-HW-PREP-TRIAC-320-001` *(HW-005 / COMPLIANCE-001)*.
8. `PRE-HW-PREP-MAINS-400-001` *(COMPLIANCE-001)*.
9. `PRE-HW-PREP-POE-410-001` *(isolation / Hi-pot; `PACKAGE-POE-410-001`)*.

### Guardrails (explicitly NOT changed)

* No YAML, package, board, bundle, expansion, or product file edited.
* No `config/*.json` changed — `S360-310/311/312/320/400/410` stay
  `cataloged_unverified`, no `schematic_file`, no config string, artifact
  name, or lifecycle touched.
* No `schematic_status` flip; nothing marked `verified` or
  design-complete-as-verified; nothing promoted.
* No WebFlash exposure / release; no edit to
  [`firmware/sources.json`](firmware/sources.json) or `manifest.json`.
* The SX1509 reconciliation is **planned only**, not performed; no GPIO
  numbers invented beyond schematic-printed values.
* No gerbers / BOM / measurement fabricated; the WebFlash repo is untouched.

### Validation

* `python3 tests/validate_configs.py`
* `python3 tests/test_roadmap_status_doc.py`
* `python3 -m unittest discover -s tests -p "test_*.py"`

---

## HW-PINMAP-311-FOLLOWUP — standalone schematic-backed reference doc for S360-311 PWM

**Status:** docs-only (records, resolves nothing; no gate closed; board package still gated)

### Summary

Authors the standalone schematic-backed hardware reference doc for the
Sense360 PWM board (`S360-311-R4`) at
[`docs/hardware/s360-311-r4-fanpwm.md`](docs/hardware/s360-311-r4-fanpwm.md),
sourced **only** from the already-committed module-side schematic PDF
[`docs/hardware/schematics/S360-311-R4.pdf`](docs/hardware/schematics/S360-311-R4.pdf)
(HW-ASSETS-003; SHA256 `c910b3364be1d58fc44d12b5a189dade47efddf6cae158a86577ec7501e48006`).
It transcribes the connector and pin map exactly as the schematic shows
(`J3` 13-pin "From Core"; the four fan outputs `J1` / `J2` / `J4` / `J5`;
the Nextion `J6`; mounting holes `H1..H4`; the MT3608 boost) and records
every open reconciliation question as **STILL OWED**. Per
[`docs/cleanup-audit.md`](docs/cleanup-audit.md) the reconciliation itself
needs silkscreen, harness, and bench evidence plus the systemic Core
abstract-bus resolution, none of which this PR performs.

### What changed

* New `docs/hardware/s360-311-r4-fanpwm.md` — the standalone reference doc.
* `docs/hardware/s360-311-r4-pwm.md` — added a See-also cross-link to the
  new reference doc (no other section rewritten; status row unchanged).
* `docs/hardware/board-readiness-matrix.md` — replaced the "still no
  standalone reference doc" note in the `S360-311` subsection with a link
  to the new doc, and added a See-also entry. `S360-311` classification
  (`partially-documented`, `not-needed-for-release-one`,
  `package-yaml-pending`) is unchanged.
* This `UPCOMING_PR.md` update.

### Open reconciliation questions recorded as STILL OWED (resolved: none)

1. SX1509-expander-vs-direct-ESP32-GPIO mapping disagreement → owned by
   `CORE-ABSTRACT-BUS-001` /
   [`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3](docs/release-one-hardware-audit.md).
2. UART on `J3` pins 11 / 12 (module-side labels not in the Core `J6`
   capture).
3. `"NINE 4pin FANs"` section title vs four visible outputs
   (`J1` / `J2` / `J4` / `J5`).
4. Single-channel-vs-four-channel canonical abstraction for the `FanPWM`
   token (`PACKAGE-PWM-001`).

Each records the evidence (silkscreen, harness, bench waveforms) that
would close it. The reconciliation and the S360-311 board-package
promotion **remain gated** on that owed evidence.

### Guardrails (explicitly NOT changed)

* No edit to `config/hardware-catalog.json` (`S360-311` stays
  `cataloged_unverified`, no `schematic_file`),
  `config/product-catalog.json`, `config/webflash-builds.json`, or
  `config/webflash-compatibility.json`.
* No `schematic_status` flip; no `verified` / `pin-map-confirmed` mark.
* No package YAML edited (`fan_pwm.yaml`, `sense360_fan_pwm.yaml`,
  `gpio_expander_sx1509.yaml`, `sense360_core*.yaml` all unchanged).
* No product YAML, WebFlash wrapper, build entry, release, tag, or import
  added; no firmware regenerated.
* Release-One, the LED preview path, and FanTRIAC (`blocked` / `HW-005`)
  are unchanged; `S360-320` / `S360-400` compliance is unchanged.
* The schematic PDF and the curated artifact index
  (`docs/hardware/artifacts/S360-311-R4.md`) are not edited.
* The WebFlash repo (`sense360store/webflash`) is untouched.

### Validation

* `python3 tests/validate_configs.py`
* `python3 tests/test_roadmap_status_doc.py`
* `python3 -m unittest discover -s tests -p "test_*.py"`

---

## PRODUCT-DEP-CORE-001 — retire non-template legacy core-c/v/w configs

**Status:** retired (14 legacy `sense360-core-*` configs moved to `removed`; 5 kept as live authoring templates)

### Summary

Executes the `core-c` / `core-v` / `core-w` disposition recommended in
[`docs/v1-r4-product-gap.md`](docs/v1-r4-product-gap.md) (§"`core-c` / `core-v`
/ `core-w` disposition"), the deprecation-series sibling of
`PRODUCT-DEP-MINI-001`. Of the 19 legacy `sense360-core-*` `legacy-compatible`
entries, the **14** with no R4-v1 reuse are retired through the
`PRODUCT-DEP-001` `legacy-compatible -> removed` (intentional-retirement)
transition — the same path the Mini range used; no `deprecated` step is needed
because these were never WebFlash-shippable and never appeared in
`config/webflash-builds.json`. The **5** ceiling Core bases / sensor stacks that
the gap doc flags as authoring templates for not-yet-authored `V1-R4-CREATE-*`
configs stay `legacy-compatible`; their retirement is **deferred** to land with
the CREATE config they template.

### KEEP / RETIRE split (from the gap-doc template-source table)

**KEEP-as-template (5, stay `legacy-compatible`, annotated; retirement deferred):**

* `sense360-core-c-poe` — ceiling + PoE base → templates V1-R4-CREATE-002 / 003.
* `sense360-core-c-usb` — ceiling + USB base → templates V1-R4-CREATE-005 / 006.
* `sense360-core-ceiling` — full AirIQ stack → templates V1-R4-CREATE-002 / 005.
* `sense360-core-ceiling-bathroom` — VentIQ-intent stack → templates V1-R4-CREATE-006
  (V1-R4-CREATE-004 already authored).
* `sense360-core-ceiling-presence` — presence(+LED) stack → templates
  V1-R4-CREATE-003 / 006 (V1-R4-CREATE-001 / 004 already authored).

**RETIRE (14, moved to `removed` tombstones; product YAMLs deleted):**

* mains: `sense360-core-c-pwr`.
* wall (5): `sense360-core-w-poe`, `-w-pwr`, `-w-usb`, `sense360-core-wall`,
  `sense360-core-wall-presence`.
* voice (8): `sense360-core-v-c-poe`, `-v-c-pwr`, `-v-c-usb`, `-v-w-poe`,
  `-v-w-pwr`, `-v-w-usb`, `sense360-core-voice-ceiling`,
  `sense360-core-voice-wall`.

The two standalone legacy entries (`sense360-fan-pwm`, `sense360-poe`) are
**outside** `PRODUCT-DEP-CORE-001` scope and stay `legacy-compatible`.

### What changed

* `config/product-catalog.json`: the 14 RETIRE rows flip
  `legacy-compatible -> removed` with `removed_since: 2026-05-30`,
  `removal_reason` ("Superseded by R4 product line; not an R4 config and not a
  live authoring template." + the `legacy-compatible -> removed` transition
  note), a per-family `no_replacement_reason`, and tombstone `notes`; each drops
  `product_yaml` (tombstone contract, exactly as the Mini entries). The 5 KEEP
  rows keep `status: legacy-compatible` and gain a template-retention annotation
  in `notes`.
* `products/`: the 14 RETIRE `sense360-core-*.yaml` files are removed.

### Guardrails (explicitly NOT changed)

* No KEEP-as-template config retired; their lifecycle is unchanged.
* No shared package under `packages/` deleted — the legacy core configs
  referenced core/board/expansion packages that R4 still uses; only the legacy
  product YAMLs and their catalog rows are retired.
* No touch to the 6 R4 configs, the 2 USB configs, or the 10 Mini tombstones.
* No edits to `config/webflash-builds.json`, `manifest.json`, or
  `firmware/sources.json`; no board `schematic_status` change; nothing promoted.
* `v1.0.0` is untouched — it keeps the legacy files for tag-pinned field units.
* No new tests and no test assertions weakened: the `packages/`-level package
  tests (`test_core_abstract_bus.py`) and the auto-discovering
  `test_product_substitutions.py` / `generate_test_configs.py` reference shared
  packages (which survive) and discover product YAMLs dynamically, so the suite
  passes with the RETIRE set gone with no test edits.

### Deferred work

The KEEP-as-template set's retirement is **deferred**: each of the 5 retained
configs is retired in the PR that authors its last templated `V1-R4-CREATE-*`
config (CREATE-002 / 003 / 005 / 006), through the same
`legacy-compatible -> removed` transition used here.

### Validation

* `python3 tests/validate_configs.py`
* `python3 tests/test_product_catalog.py`
* `python3 tests/test_product_substitutions.py`
* `python3 tests/test_core_abstract_bus.py`
* `python3 tests/test_all_yaml_release_matrix.py`
* `python3 -m unittest discover -s tests -p "test_*.py"`

---

## V1-R4-CREATE-004 — author USB sensor variants (Ceiling-USB-VentIQ-RoomIQ, Ceiling-USB-RoomIQ)

**Status:** authored (manual / custom channel; compile-validation pending-ci; no WebFlash promotion)

### Summary

This change authors the two unblocked R4 USB sensor configs from
[`docs/v1-r4-product-gap.md`](docs/v1-r4-product-gap.md) (V1-R4-CREATE-004),
each as a config-string-named bundle + thin compat shim + catalog row composed
from the `packages/boards/` layer:

* `Ceiling-USB-VentIQ-RoomIQ` — Core(ceiling) + USB-C power + S360-211 VentIQ +
  S360-200 RoomIQ (the USB power-axis variant of the WebFlash-shipping
  `Ceiling-POE-VentIQ-RoomIQ`, PoE PSU board swapped for the USB-C power package).
* `Ceiling-USB-RoomIQ` — Core(ceiling) + USB-C power + S360-200 RoomIQ (the USB
  power-axis variant of the authored `Ceiling-POE-RoomIQ`).

These are **manual / custom** firmwares available for manual ESPHome / GitHub
use, **NOT** WebFlash-exposed. USB variants carry **no PoE PSU board** (no
S360-410); all three boards (S360-100, S360-211, S360-200) are
`schematic_status: verified` and there is **no evidence blocker**.

### What changed

* New bundles `products/bundles/ceiling-usb-ventiq-roomiq.yaml` and
  `products/bundles/ceiling-usb-roomiq.yaml` (full configs composed from the
  board packages + `packages/hardware/power_usb.yaml` + base tier + the same
  behaviour profiles the PoE sensor bundle uses).
* New compat shims `products/sense360-ceiling-usb-ventiq-roomiq.yaml` and
  `products/sense360-ceiling-usb-roomiq.yaml` (each does nothing but `!include`
  its bundle, per §3.2).
* `config/product-catalog.json`: two rows, `status: compile-only`,
  `target_channel: manual-custom`, `webflash_build_matrix: false`, no
  `artifact_name`, no `webflash_wrapper`, no kit preset.
* `config/compile-only-targets.json`: two top-level targets
  (`ceiling-usb-ventiq-roomiq-product-compile-only`,
  `ceiling-usb-roomiq-product-compile-only`), `compile_validation_status:
  pending-ci`.
* `config/compile-only-candidates.json`,
  `config/firmware-combination-matrix.json` (regenerated;
  `compile-only-candidate`), `docs/firmware-build-gap-report.md` (regenerated),
  `docs/product-readiness-matrix.md`, `docs/all-yaml-release-matrix.md`, and
  `docs/v1-r4-product-gap.md` (CREATE-004 marked authored) updated to match.

### Guardrails (explicitly NOT changed)

* No edits to `config/webflash-builds.json`, `firmware/sources.json`, or
  `manifest.json`.
* No `artifact_name`; no `webflash_build_matrix` flip; no kit preset; no
  WebFlash wrapper / exposure.
* No PoE PSU (no S360-410) in these USB variants.
* No board `schematic_status` change; LED not marked stable; S360-410 not marked
  verified; nothing preview-promoted or claimed as a kit.
* No compile result fabricated (ESPHome unavailable in the authoring
  environment; a CI `--compile` run is owed).

### Queue status (maintenance rule)

`V1-R4-CREATE-004` delivers the unblocked non-LED USB pair. The remaining
`V1-R4-CREATE-*` slices stay **queued behind their gates**:

* **V1-R4-CREATE-002** — `Ceiling-POE-AirIQ-RoomIQ` (S360-410 + AirIQ-stack
  evidence-gated).
* **V1-R4-CREATE-003** — `Ceiling-POE-RoomIQ-LED` (LED preview gauntlet;
  S360-410-gated).
* **V1-R4-CREATE-005** — `Ceiling-USB-AirIQ-RoomIQ` (AirIQ-stack evidence-gated).
* **V1-R4-CREATE-006** — `Ceiling-USB-VentIQ-RoomIQ-LED`,
  `Ceiling-USB-RoomIQ-LED` (LED preview-gated).

### Validation

* `python3 tests/validate_configs.py`
* `python3 scripts/validate_compile_targets.py --metadata-only`
* `python3 tests/test_product_catalog.py`
* `python3 tests/test_all_yaml_release_matrix.py`
* `python3 tests/test_product_substitutions.py`
* `python3 tests/test_release_one_entity_names.py`
* `python3 tests/validate_webflash_builds.py`
* `python3 -m unittest discover -s tests -p "test_*.py"`

### Retained cross-references (maintenance)

The module-side pinmap ledger `MODULE-PINMAPS-GDRIVE-001` and the canonical Core
connector pin map [`docs/hardware/s360-100-core-connector-pin-map.md`](docs/hardware/s360-100-core-connector-pin-map.md)
are unchanged by this slice and remain the source of truth for the S360-100
ceiling Core bus that the USB variants bind.

---

## ROOM-BUNDLE-FAN-VARIANTS-001 — Planning-only fan-control variants (Bathroom & Kitchen)

**Status:** planning-only (no firmware release, no WebFlash promotion)

### Summary

This change adds a planning-only proposal for optional fan-control variants of the
Bathroom and Kitchen PoE room bundles. The base room bundles remain the primary
product line. The fan variants are Bathroom/Kitchen-only add-ons and are captured
in a separate config file (Option A) so the stable room-bundle matrix stays clean.

### What changed

* New `config/room-bundle-fan-variants.json` describing five planning variants:
  * `S360-KIT-BATH-P-REL` (relay)
  * `S360-KIT-BATH-P-DAC` (0-10V DAC)
  * `S360-KIT-BATH-P-PWM` (PWM)
  * `S360-KIT-KITCHEN-P-DAC` (0-10V DAC)
  * `S360-KIT-KITCHEN-P-REL` (relay)
* New docs section in `docs/sense360-room-bundles.md` with the variant table and prose.
* New contract test `tests/test_room_bundle_fan_variants.py`.
* This `UPCOMING_PR.md` update.

### Guardrails (explicitly NOT changed)

* No edits to `webflash-builds.json`, `sources.json`, or `manifest.json`.
* No `artifact_name` fields anywhere.
* No `webflash_build_matrix` flip.
* No LED/fan-driver stable promotion.
* No TRIAC variant.
* No Corridor/Living/Bedroom fan variant.
* No existing bundle SKU or lifecycle changed.

### Validation

* `python3 -m unittest discover -s tests -p "test_*.py"` (1163 tests, 3 skipped).
* `validate_configs.py`.
* Per-test scripts for the new contract test.

### Variants

| Variant SKU | Base bundle | Room | Fan control |
| --- | --- | --- | --- |
| S360-KIT-BATH-P-REL | S360-KIT-BATH-P | Bathroom | relay |
| S360-KIT-BATH-P-DAC | S360-KIT-BATH-P | Bathroom | dac_0_10v |
| S360-KIT-BATH-P-PWM | S360-KIT-BATH-P | Bathroom | pwm |
| S360-KIT-KITCHEN-P-DAC | S360-KIT-KITCHEN-P | Kitchen | dac_0_10v |
| S360-KIT-KITCHEN-P-REL | S360-KIT-KITCHEN-P | Kitchen | relay |

### Notes

* relay vs DAC(0-10V) vs PWM are not runtime-interchangeable; each is a separate SKU.
* Bundle SKUs are kept separate from firmware config strings.
* Kitchen fan control is framed as extract/MVHR/EC boost, not a cooker-hood replacement.
* No variant is exposed to WebFlash.

### Next steps

* A future implementation PR would define firmware configs, build artifacts, and
  validation before any WebFlash promotion.

---

_Previous entries below this line are historical and unchanged._

## (historical placeholder)

Earlier planning notes are intentionally omitted from this excerpt.

(end)

## Historical: ROOM-BUNDLE-MATRIX baseline

The room-bundle matrix (Corridor, Living, Bedroom, Bathroom, Kitchen) across PoE and
USB power options remains the stable, released baseline. This planning entry does not
modify that matrix; it only proposes additive Bathroom/Kitchen fan variants for a
future PR.

* Corridor: S360-KIT-CORR-P / S360-KIT-CORR-U
* Living: S360-KIT-LIV-P / S360-KIT-LIV-U
* Bedroom: S360-KIT-BED-P / S360-KIT-BED-U
* Bathroom: S360-KIT-BATH-P / S360-KIT-BATH-U
* Kitchen: S360-KIT-KITCHEN-P / S360-KIT-KITCHEN-U

* Base bundles remain the main product line; fan variants are add-ons.
* No bundle SKU or lifecycle is changed by this planning entry.

(end of file)

<!-- planning-only; no firmware release implied -->

<!-- ROOM-BUNDLE-FAN-VARIANTS-001 -->

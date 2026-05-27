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
- **Drive evidence.** Re-searched Google Drive this session (owner
  `neilmcrae@googlemail.com`, R4 shared drive) for any **new** bench /
  sign-off / harness / polarity / current / thermal / compliance
  artifact that could close an open blocker. **None was found.** The
  only artifacts present are the already-recorded CAD / manufacturing
  sets (`12vFan_PWM_PulseCounter`, `Fan_GP8403` / `GP8403-Module`,
  `RelayBoard-Module`, `TRIAC.png` / `Relay.png` / `LED.png` design
  renders) plus the project trackers. No artifact is committed by this
  PR; provenance only.
- **Project tracker.** Re-read `Sense360_R4_Tracker`
  (Google Sheet, owner `neilmcrae@googlemail.com`, last modified
  **2026-05-18**) for status corroboration. New, blocker-relevant
  facts captured below: the Fan Relay board's further work (`Y02`) is
  **Waiting** on the TRIAC merge decision (`T02`, still **Doing**);
  the TRIAC mechanism is SSR + MOC3041 optocoupler (`T01` Done);
  mains connector tasks (`T04` / `Y01` / `Y03` / `Z01`) are Done but
  carry **no** compliance certification; the fleet-wide silkscreen
  P/N / REV / date-code task (`G01`) stays **Waiting** on Neil's logo
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
| PWM-6 | Output electrical characteristics (per-fan current, MT3608 ceiling, aggregate load, inrush, thermal) | NEEDS BENCH (fan/load + supply recorded) | Boost topology known (MT3608 / L1 22 µH / SS34 / 38k:2k); **fan/load = Arctic P14 Plus**, **supply = 12 V MT3608 boost (~2 A available)**, qualitative 1+ hour all-four run, no sag reported (operator bench); per-channel + aggregate current, **measured** MT3608 ceiling, inrush **still not** measured | PWM-BLOCKER-REMOVAL-001 / PR #586; S360-311-BENCH-RESULT-001 (operator `@wifispray`, 2026-05-26) | Partial | bench: **measured** per-channel + aggregate current draw, MT3608 measured output-current ceiling / sag under 4-fan load, locked-rotor / inrush | S360-311-CURRENT-THERMAL-001 |
| PWM-7 | Package YAML (PWM-drive-only scope) | CLOSED | `fan_pwm.yaml` four `fan: platform: speed` controllers on SX1509 PWM-drive outputs | PACKAGE-PWM-001-IMPLEMENT-001 / PR #590 | Yes | none | — |
| PWM-8 | Product YAML (no-WebFlash slice) | CLOSED | `products/sense360-ceiling-poe-fanpwm.yaml` (`Ceiling-POE-FanPWM`); catalog row `hardware-pending` | PRODUCT-PWM-001 / PR #593; FW-COMPILE-PWM-PRODUCT-001 / PR #594 | Yes | none | — |
| PWM-9 | Compile-only target / full-compile result | CLOSED | `ceiling-poe-fanpwm-compile-only`; `validated-full-compile`, `rpm_supported: false` | FW-COMPILE-PWM-001 / PR #591; FW-COMPILE-PWM-RESULT-001 / PR #592 (run `26414398902`) | Yes | none | — |
| PWM-10 | PWM polarity (active-high vs active-low at the low-side N-FET gate) | CLOSED (observed behaviour) | Operator: increasing commanded duty increased fan speed across low/med/high duty → **non-inverting, no inversion required**; observed behaviour (not scope-traced); exact Hz / min%–max% not recorded | S360-311-BENCH-RESULT-001 (operator `@wifispray`, 2026-05-26) | Yes (observed behaviour) | optional: scope-trace gate waveform / record exact Hz + duty % | — |
| PWM-11 | Product bench (FanPWM end-to-end) | CLOSED (functional; operator-notes-only) | Operator-attested on `S360-311-R4`: all 4 channels individually speed-controlled, all 4 simultaneous for 1+ hour, restart retained last commanded speed; operator notes only (no photo/video/log) | S360-311-BENCH-RESULT-001 (operator `@wifispray`, 2026-05-26) | Yes (functional) | **measured** current + **measured** thermal carried by PWM-6 / PWM-13 | S360-311-CURRENT-THERMAL-001 (measured rows) |
| PWM-12 | TachIO / GPIO16 + RPM | NEEDS BENCH / deferred | No `pulse_counter`; per-fan RPM via SX1509 `pulse_counter` is compile-proven unsupported (`[sx1509] is an invalid option for [pin]`) | PWM-SX1509-TACH-PROOF-001 / PR #589; PACKAGE-PWM-TACH-STRATEGY-001 / PR #588 | No (kept false) | keep `rpm_supported: false`; any RPM needs a separate approved tach strategy | COMPONENT-SX1509-TACH-001 (future) |
| PWM-13 | Board-level thermal / EMI note | NEEDS BENCH (qualitative recorded) | SELV board; not certified; **qualitative: all 4 fans ran 1+ hour, no heat issue noticed** (operator notes); no measured °C / IR / thermocouple / EMI | WEBFLASH-PWM-001-READINESS / PR #598; S360-311-BENCH-RESULT-001 (operator `@wifispray`, 2026-05-26) | Partial | **measured** thermal temp / ambient / hottest-location (IR or thermocouple); EMI observation (not a compliance approval) | S360-311-CURRENT-THERMAL-001 |
| PWM-14 | Compliance / mains gate | CLOSED (no mains) | SELV (5 V → 12 V boost); no mains path | PWM-BLOCKER-REMOVAL-001 / PR #586 | Yes | none — `COMPLIANCE-001` mains gate does not apply | — |
| PWM-15 | WebFlash wrapper / build-matrix / artifact / module-availability | NEEDS WEBFLASH ACCESS + OUT OF SCOPE | No wrapper; `S360-311` not in any `module-availability.js` snapshot (drift #16) | WEBFLASH-DRIFT-001 / PR #595; WEBFLASH-PWM-001-READINESS / PR #598 | No | record `S360-311` classification on live re-check; wrapper gated behind bench | WEBFLASH-PWM-LIVE-CHECK-001 |

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
| Measured per-channel current (`PWM-6`) | Not measured (qualitative 1+ hour run) | **No** | **Yes** | **Yes** | Measured A/channel + method → `S360-311-CURRENT-THERMAL-001` |
| Measured aggregate current, all 4 (`PWM-6`) | Not measured | **No** | **Yes** | **Yes** | Measured total A + MT3608 ceiling / inrush |
| Measured thermal temperature (`PWM-13`) | Qualitative no-heat 1+ hour; no °C | **No** | **Yes** | **Yes** | Measured °C or documented method |
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
| RLY-6 | Mains / compliance caveats | BLOCKED BY POLICY / SAFETY | `K1` SRD-05VDC-SL-C contact rating is relay-datasheet evidence only — **not** board-level compliance / creepage / clearance / EMI / mains-safety certification | S360-310-BENCH-EVIDENCE-001 / PR #561 | No | COMPLIANCE-001-equivalent mains slice for any mains-switching FanRelay | (COMPLIANCE-001 mains slice) |
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
| Mains / compliance approval (`RLY-6`) | `K1` contact rating is datasheet-only; no board-level cert | **No** | **Yes** — release / compliance blocker only | **No** | `COMPLIANCE-001`-equivalent mains slice |
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
| CMP-1 | `COMPLIANCE-001` mains UK/EU (S360-320 TRIAC, S360-400 PSU, mains-switching FanRelay) | BLOCKED BY POLICY / SAFETY | No independent sign-off; `compliance/mains-voltage-uk-eu-assessment.md` open | release/product matrices; tracker (mains connectors done, no cert) | No | competent compliance assessment / sign-off | COMPLIANCE-001 |
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
| TRI-3 | TRIAC compliance / mains sign-off | BLOCKED BY POLICY / SAFETY | See CMP-1 | — | No | COMPLIANCE-001 | COMPLIANCE-001 |

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
canonically-named `S360-311-R4` Drive folder (owner
`kanyugistash@gmail.com`, created 2026-05-16: KiCad sources, gerbers,
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
`GP8403.zip` / `GP8403-Module`, owner `neilmcrae@googlemail.com`), the
canonical `S360-312-R4.pdf` schematic (owner `kanyugistash@gmail.com`,
modified 2026-05-16 — already committed byte-identical as
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
owned by `kanyugistash@gmail.com` created 2026-05-16 with KiCad sources /
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
`S360-310-R4` set (owner `kanyugistash@gmail.com`, 2026-05-18: KiCad
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

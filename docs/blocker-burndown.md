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
| PWM-3 | Core connector / bus / GPIO mapping (J6/J3 pin-1 order; UART-on-J3-11/12) | NEEDS BENCH | `core_i2c` rebind landed; connector identity + routing direction resolved (D2/D3) | CORE-ABSTRACT-BUS-001B; operator D2/D3; tracker `G01` (no R4 silkscreen yet) | No | silkscreen pin-1 read once R4 silkscreen exists; confirm UART routing on bench | S360-311-BENCH-EVIDENCE-REQUEST-001 |
| PWM-4 | PWM output pin mapping (4-channel; SX1509 ch0..3 / ch4..7; TachIO IO16) | CLOSED (package layer) | Reconciled `fan_pwm.yaml` → `fan_pwm_sx1509.yaml`; pinned by `test_fan_pwm_package.py` | PACKAGE-PWM-001-IMPLEMENT-001 / PR #590; operator D1/D2 | Yes (package) | none at package layer | — |
| PWM-5 | Controlled load type (≤4× 12 V 4-wire PWM fans on JST-SH SM04B) | CLOSED | Schematic + BOM + render silkscreen | PWM-BLOCKER-REMOVAL-001 / PR #586 | Yes | none | — |
| PWM-6 | Output electrical characteristics (per-fan current, MT3608 ceiling, aggregate load, inrush, thermal) | NEEDS BENCH | Boost topology known (MT3608 / L1 22 µH / SS34 / 38k:2k); per-fan + aggregate current, ceiling, inrush, thermal **not** specified | PWM-BLOCKER-REMOVAL-001 / PR #586; no Drive bench artifact (re-confirmed) | No | bench: per-fan + aggregate current draw, MT3608 output-current ceiling, locked-rotor / inrush, thermal rise | S360-311-BENCH-EVIDENCE-REQUEST-001 |
| PWM-7 | Package YAML (PWM-drive-only scope) | CLOSED | `fan_pwm.yaml` four `fan: platform: speed` controllers on SX1509 PWM-drive outputs | PACKAGE-PWM-001-IMPLEMENT-001 / PR #590 | Yes | none | — |
| PWM-8 | Product YAML (no-WebFlash slice) | CLOSED | `products/sense360-ceiling-poe-fanpwm.yaml` (`Ceiling-POE-FanPWM`); catalog row `hardware-pending` | PRODUCT-PWM-001 / PR #593; FW-COMPILE-PWM-PRODUCT-001 / PR #594 | Yes | none | — |
| PWM-9 | Compile-only target / full-compile result | CLOSED | `ceiling-poe-fanpwm-compile-only`; `validated-full-compile`, `rpm_supported: false` | FW-COMPILE-PWM-001 / PR #591; FW-COMPILE-PWM-RESULT-001 / PR #592 (run `26414398902`) | Yes | none | — |
| PWM-10 | PWM polarity (active-high vs active-low at the low-side N-FET gate) | NEEDS BENCH | Not waveform-confirmed | WEBFLASH-PWM-001-READINESS / PR #598 | No | bench: scope the SX1509 PWM-drive output vs fan PWM input polarity | S360-311-BENCH-EVIDENCE-REQUEST-001 |
| PWM-11 | Product bench (FanPWM end-to-end) | NEEDS BENCH | Product YAML exists for manual / compile-your-own use only | WEBFLASH-PWM-001-READINESS / PR #598 | No | operator product-bench sign-off | S360-311-BENCH-EVIDENCE-REQUEST-001 |
| PWM-12 | TachIO / GPIO16 + RPM | NEEDS BENCH / deferred | No `pulse_counter`; per-fan RPM via SX1509 `pulse_counter` is compile-proven unsupported (`[sx1509] is an invalid option for [pin]`) | PWM-SX1509-TACH-PROOF-001 / PR #589; PACKAGE-PWM-TACH-STRATEGY-001 / PR #588 | No (kept false) | keep `rpm_supported: false`; any RPM needs a separate approved tach strategy | COMPONENT-SX1509-TACH-001 (future) |
| PWM-13 | Board-level thermal / EMI note | NEEDS BENCH | SELV board; not certified | WEBFLASH-PWM-001-READINESS / PR #598 | No | bench thermal / EMI observation (not a compliance approval) | S360-311-BENCH-EVIDENCE-REQUEST-001 |
| PWM-14 | Compliance / mains gate | CLOSED (no mains) | SELV (5 V → 12 V boost); no mains path | PWM-BLOCKER-REMOVAL-001 / PR #586 | Yes | none — `COMPLIANCE-001` mains gate does not apply | — |
| PWM-15 | WebFlash wrapper / build-matrix / artifact / module-availability | NEEDS WEBFLASH ACCESS + OUT OF SCOPE | No wrapper; `S360-311` not in any `module-availability.js` snapshot (drift #16) | WEBFLASH-DRIFT-001 / PR #595; WEBFLASH-PWM-001-READINESS / PR #598 | No | record `S360-311` classification on live re-check; wrapper gated behind bench | WEBFLASH-PWM-LIVE-CHECK-001 |

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

### 2D. WebFlash live access / module availability

| ID | Blocker | Status | Evidence found | Provenance | Closed? | Remaining exact action | Next PR |
|---|---|---|---|---|---|---|---|
| WF-1 | Live `sense360store/WebFlash` read access | NEEDS WEBFLASH ACCESS | Read denied this session; GitHub scope = `esphome-public` + `esphome` only | This session; WEBFLASH-DRIFT-001 / PR #595 | No | operator / tooling: grant read access to `sense360store/WebFlash` | (tooling remediation) |
| WF-2 | `module-availability.js` `S360-311` / `S360-312` classification (drift #16/#17) | NEEDS WEBFLASH ACCESS | Not recorded in any snapshot | WEBFLASH-DRIFT-001 / PR #595 | No | record once access restored | WEBFLASH-{PWM,DAC}-LIVE-CHECK-001 |
| WF-3 | `artifact_pattern` source / grammar parity / full channel list (drift #4/#5/#11) | NEEDS WEBFLASH ACCESS | Prior-recorded subset consistent; sources not inspected | WEBFLASH-DRIFT-001 / PR #595 | No | re-run drift audit with live access | WEBFLASH-DRIFT-001 (re-run) |
| WF-4 | Cross-repo product / import drift | CLOSED (no confirmed drift) | Every Relay/DAC/PWM/TRIAC axis `INTENTIONALLY-BLOCKED` or `NEEDS-OPERATOR-INPUT`; no `WEBFLASH-DRIFT-FIX-001` prerequisite | WEBFLASH-DRIFT-001 / PR #595 | Yes | none (re-run only to close `NEEDS WEBFLASH ACCESS` axes) | — |
| WF-5 | Intra-repo stale "FanPWM product/package missing" headline (drift #20) | CAN CLOSE NOW (doc) | Already reconciled in-repo; re-confirmed | WEBFLASH-DRIFT-001 / PR #595; WEBFLASH-PWM-001-READINESS / PR #598 | Yes | none | — |

### 2E. Security

| ID | Blocker | Status | Evidence found | Provenance | Closed? | Remaining exact action | Next PR |
|---|---|---|---|---|---|---|---|
| SEC-1 | Workflow least-privilege `permissions:` | CLOSED | All five workflows declare top-level `contents: read`; guarded by `test_workflow_permissions.py` | SECURITY-AUDIT-FIX-001 / PR (2026-05-25) | Yes | none | — |
| SEC-2 | Action SHA pinning (6 mutable major-tag pins) | CAN CLOSE NOW (separate PR) | Inventoried + regression-guarded; **not** converted to immutable SHAs | SECURITY-AUDIT-FIX-001; `workflow-security-hardening.md` | No | convert the 6 pins to commit SHAs (start `softprops/action-gh-release@v2`); tighten the guard | **SECURITY-ACTION-PINNING-001** |
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
| CLOSED | 26 | PWM-1/2/4/5/7/8/9/14, DAC-1..8a/10/11/13, RLY-1/2, WF-4/5, SEC-1, REL-3, CMP-2, LED-2 |
| CAN CLOSE NOW (separate / docs) | 3 | DAC-12 (design), WF-5 (doc), SEC-2 (separate PR) |
| NEEDS BENCH | 9 | PWM-3/6/10/11/13, DAC-8c/8d, RLY-3, LED-1 |
| NEEDS OPERATOR INPUT | 7 | DAC-8b/14, RLY-4/7, TRI-2, LED-1, (SEC-3 tooling) |
| NEEDS WEBFLASH ACCESS | 6 | PWM-15, DAC-15, RLY-8, WF-1/2/3, REL-2 |
| NEEDS DRIVE EVIDENCE | 1 | DAC-8c |
| BLOCKED BY POLICY / SAFETY | 4 | RLY-6, CMP-1, TRI-1/3 |
| OUT OF SCOPE | 5 | DAC-9, SEC-4, REL-1, PWM-12 (deferred RPM) |

(IDs may appear under more than one class where a blocker has both a
bench and an access dimension; the table in §2 is authoritative.)

**Headline.** No remaining hardware / WebFlash / compliance blocker can
be closed in this docs-only pass without new bench, operator, WebFlash,
or Drive evidence — none of which appeared this session. The hardware
lanes (PWM / DAC / Relay) are all package + product + compile complete
and are now **bench / operator / safety gated**, not repo gated. The one
non-hardware lane that can advance immediately is
**`SECURITY-ACTION-PINNING-001`** (SEC-2).

## 4. Next-PR recommendations

Applying the burn-down decision rules:

- **FanPWM bench evidence is missing** → **`S360-311-BENCH-EVIDENCE-REQUEST-001`**
  (request PWM polarity, per-fan + aggregate current, MT3608 ceiling,
  inrush, thermal, product bench; J6/J3 silkscreen pin order once R4
  silkscreen exists). *Not* `S360-311-BENCH-RESULT-001` (no results to
  record).
- **FanDAC bench evidence is missing** → **`S360-312-BENCH-EVIDENCE-REQUEST-001`**
  (request `J3` `out0`/`out1` transposition confirmation, Cloudlift S12
  harness trace, Cloudlift S12 product bench). *Not*
  `S360-312-BENCH-RESULT-001`.
- **FanRelay safety evidence is missing** → **`S360-310-SAFETY-EVIDENCE-REQUEST-001`**
  (request multi-unit oscilloscope-traced GPIO3 strap characterization +
  competent-person sign-off). *Not* `S360-310-SAFETY-BENCH-RESULT-001`.
- **WebFlash live access is unavailable** → keep all live WebFlash PRs
  blocked; record access remediation as an operator / tooling action
  (WF-1). The live checks (`WEBFLASH-{PWM,DAC,RELAY}-LIVE-CHECK-001`,
  `WEBFLASH-DRIFT-001` re-run) stay queued behind access restoration.
- **Hardware evidence lanes are blocked** → the actionable non-hardware
  PR is **`SECURITY-ACTION-PINNING-001`** (SEC-2): convert the six
  inventoried mutable major-tag action pins to immutable commit SHAs.
  It is kept **visible and separate** and is **not** merged into this
  burn-down PR (the guardrails forbid `.github/workflows/**` edits here,
  and not all blocker docs point to it as the *only* remaining
  non-hardware blocker — the three bench-evidence-request docs are also
  open).

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

**FanDAC / S360-312 (S360-312-BENCH-EVIDENCE-REQUEST-001):**
7. Confirm the `J3` printed `out0`/`out1` silkscreen transposition
   (pin-1 = `IC2` VOUT0 is labelled `out1`)? (DAC-8b)
8. Cloudlift S12 harness conductor-by-conductor trace from `J2`/`J3` to
   the fan input? (DAC-8c)
9. Did the Cloudlift S12 product bench pass? (DAC-8d)
10. Promote `S360-312` `schematic_status` from `cataloged_unverified`? (DAC-14)

**FanRelay / S360-310 (S360-310-SAFETY-EVIDENCE-REQUEST-001):**
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
15. Approve **`SECURITY-ACTION-PINNING-001`** as the next non-hardware
    PR (SHA-pin the six actions)? (SEC-2)

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

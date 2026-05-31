# Pre-Hardware Preparation Plan (PRE-HARDWARE-PREP-PLAN-001)

## Status

**Status: planning / docs-only. Promotes nothing, verifies nothing,
resolves nothing.** This document defines the design-derived readiness
program that brings the six driver / PSU boards
(`S360-310` / `S360-311` / `S360-312` / `S360-320` / `S360-400` /
`S360-410`) to a **design-complete** state from the design artifacts
the repository already holds, **ahead of hardware**, so that the
eventual bench session is pure test-and-record rather than
design-from-scratch.

It is a plan. It does **not**:

- change any YAML under [`packages/`](../packages/), any board,
  bundle, expansion, or product file;
- change any config JSON under [`config/`](../config/) — not
  [`config/hardware-catalog.json`](../config/hardware-catalog.json),
  [`config/product-catalog.json`](../config/product-catalog.json),
  [`config/compile-only-targets.json`](../config/compile-only-targets.json),
  or any other — and changes no config string, artifact name,
  lifecycle, or `schematic_status`;
- mark any board `verified`, or treat **design-complete** as a
  synonym for `verified`;
- promote anything to `preview` / `stable` / `production`;
- enable any WebFlash exposure or release; it does not touch
  [`firmware/sources.json`](../firmware/sources.json) or
  [`manifest.json`](../manifest.json);
- fabricate the existence of gerbers, BOM, CPL, STEP, KiCad source, or
  any measurement;
- resolve the SX1509 deprecation (it **plans** that reconciliation as
  its own slice — see [§5](#5-sx1509-deprecation-reconciliation-slice));
- touch the WebFlash repository.

The only files this PR adds or edits are this document and the
[`UPCOMING_PR.md`](../UPCOMING_PR.md) queue.

## Why now (verified repository state)

The repository holds, for each of the six boards, **only a curated
schematic PDF** under
[`docs/hardware/schematics/`](hardware/schematics/). No gerbers, BOM,
CPL / pick-and-place, drill files, STEP / 3D model, or KiCad
schematic / PCB source is committed for any of the six. This is
recorded board-by-board in the HW-ASSETS-003 artifact indexes
([`docs/hardware/artifacts/S360-311-R4.md`](hardware/artifacts/S360-311-R4.md),
[`docs/hardware/artifacts/S360-312-R4.md`](hardware/artifacts/S360-312-R4.md),
and the sibling `S360-31{0}`, `S360-3{20}`, `S360-4{00,10}` records),
each of which states the upload was a *single loose PDF, nothing else*.

In `config/hardware-catalog.json` every one of the six carries
`schematic_status: cataloged_unverified` with no `schematic_file`
pointer:

| SKU | Friendly name | Group / Type | Domain | `schematic_status` |
|---|---|---|---|---|
| `S360-310` | Sense360 Relay | Inline / Driver | mains-switching | `cataloged_unverified` |
| `S360-311` | Sense360 PWM | Inline / Driver | SELV (12 V) | `cataloged_unverified` |
| `S360-312` | Sense360 DAC | Inline / Driver | SELV (0–10 V) | `cataloged_unverified` |
| `S360-320` | Sense360 TRIAC | Inline / Driver | mains phase-dim | `cataloged_unverified` |
| `S360-400` | Sense360 240v PSU | Power / PSU | mains | `cataloged_unverified` |
| `S360-410` | Sense360 PoE PSU | Power / PSU | PoE / isolated | `cataloged_unverified` |

The fan products that consume these driver boards (`FanRelay`,
`FanDAC`, `FanPWM`, `FanTRIAC`) sit `hardware-pending` / `blocked`;
the PSUs are `cataloged_unverified`. The point of this program is to
do **everything the design artifacts permit** now, fence off
**everything that needs gerbers / BOM** as artifact-blocked, and leave
a clean test-and-record checklist for the bench.

This plan does not re-litigate the existing per-board pin-map opens.
Those remain owned authoritatively by their existing follow-ups
(`HW-PINMAP-311` / `HW-PINMAP-312` / `HW-PINMAP-410`,
`PACKAGE-PWM-001`, `PACKAGE-POWER-400-001`, `PACKAGE-POE-410-001`,
`COMPLIANCE-001`, and the systemic
[`CORE-ABSTRACT-BUS-001`](hardware/core-abstract-bus-reconciliation.md)
slices) and are referenced, not duplicated.

---

## 1. The `design-complete` status concept

### 1.1 Definition

**`design-complete`** is a new, explicitly **pre-hardware** readiness
state for a board's firmware / config. A board is `design-complete`
when **all** of the following are true:

1. its firmware board + driver package(s) are **authored and finalised
   to the current design artifacts** (the committed schematic PDF and
   the schematic-backed reference docs);
2. that firmware **compiles** — it passes an `esphome compile`
   end-to-end in a compile-only CI target — so the design is proven
   *buildable*, not merely *written*;
3. every pin / net / connector binding in the firmware is **traceable
   to a schematic-printed value** (no invented GPIO numbers, no
   assumed addresses), with each schematic-only value carried as such;
4. the per-board release-note template, artifact-naming scheme, and a
   **pre-written bench / evidence test matrix** exist, so the bench
   session has a checklist to fill rather than a design to invent.

### 1.2 What `design-complete` is explicitly NOT

`design-complete` is deliberately weaker than `verified`. It is:

- **NOT** `schematic_status: verified`. Authoring and compiling
  firmware from a schematic PDF does not confirm the schematic against
  silkscreen, harness, or bench evidence. `schematic_status` stays
  `cataloged_unverified` until a *separate* JSON-catalog change made
  under the existing per-board promotion rule flips it.
- **NOT** released. No GitHub release, tag, artifact publish, or
  `firmware/sources.json` / `manifest.json` change is implied.
- **NOT** WebFlash-exposed. No `webflash_build_matrix: true`, no
  `artifact_name`, no row in
  [`config/webflash-builds.json`](../config/webflash-builds.json), no
  product / WebFlash wrapper.
- **NOT** a lifecycle value. `design-complete` does not appear in the
  `production` / `preview` / `compile-only` / `hardware-pending` /
  `blocked` / `legacy-compatible` / `deprecated` / `removed` ladder of
  [`docs/product-deprecation-removal-policy.md`](product-deprecation-removal-policy.md).
  A `design-complete` board remains `hardware-pending` (or `blocked`)
  in the lifecycle; `design-complete` is an *orthogonal* design-readiness
  annotation, not a lifecycle transition.
- **NOT** a substitute for any safety gate. For the mains and PoE
  boards, `design-complete` can never substitute for COMPLIANCE-001
  sign-off or hi-pot / isolation evidence (see
  [§6](#6-hardware-verification-handoff-per-board)).

### 1.3 Where `design-complete` is recorded

`design-complete` is a **documentation-level annotation, never a
`config/*.json` field.** Concretely:

- **Master ledger:** the per-board *design-readiness ledger* in this
  document ([§3](#3-per-board-design-complete-deliverables)) is the
  authoritative list of what `design-complete` requires per board. As
  each board's prep slice lands, that slice updates the board's row in
  the narrative readiness docs
  ([`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md))
  with a `design_status: design-complete` **prose annotation** plus a
  link to the CI run that proves the compile. The slice does **not**
  add a `design_status` key to any JSON catalog.
- **Per-board:** the board's own schematic-backed reference doc
  (`docs/hardware/s360-3xx-r4-*.md` / `s360-4xx-r4-*.md`) gains a
  `Design-complete checklist` section recording which of the four
  §1.1 conditions are met and which remain owed.

The choice of a **doc/metadata annotation rather than a JSON field** is
deliberate: it keeps `design-complete` physically separate from
`schematic_status`, so the two can never be confused or co-edited, and
so no test, build matrix, or WebFlash generator can read
`design-complete` as a promotion signal.

### 1.4 The non-flip rule (hard)

> **`design-complete` never flips `schematic_status`, lifecycle, or
> any WebFlash / release surface on its own.**

Reaching `design-complete` is a *precondition* recorded in prose. The
transition `cataloged_unverified → verified` continues to require its
existing, separate gate: the per-board pin-map reconciliation
(`HW-PINMAP-3xx`) **plus** physical evidence **plus** a distinct
JSON-catalog PR that sets `schematic_status: verified` and
`schematic_file`. A board can be `design-complete` and still
`cataloged_unverified` indefinitely — that is the normal, expected
state for every board in this program until its bench session runs.

---

## 2. Program shape

The program is a sequence of **single-purpose slices** (each its own
future PR). This plan authors none of them; it specifies them. Each
slice is docs/firmware-scoped to exactly one concern and carries its
own guardrails. The ordered sequence is in
[§7](#7-ordered-slice-sequence). Slice identifiers are reserved here
under the `PRE-HW-PREP-*` family and cross-referenced to the existing
follow-up IDs they coordinate with.

---

## 3. Per-board `design-complete` deliverables

Each board's `design-complete` definition is the **same six
deliverables**, instantiated against that board's design artifacts:

| # | Deliverable | What it is |
|---|---|---|
| D1 | **Pinmap / netlist reconciliation** | Module-side connector / net map reconciled against the schematic PDF and the Core-side connector capture; every schematic-only value flagged as such. |
| D2 | **Firmware board + driver package finalised** | The `packages/` board + driver package authored / updated to the *current* design (post-SX1509-deprecation where relevant), bindings traceable to schematic-printed values. |
| D3 | **Product bundle / config-string** | The product-facing bundle + config string drafted (kept distinct from the board SKU), not exposed to WebFlash. |
| D4 | **Compile-only CI target** | A compile-only target that proves D2 builds end-to-end via `esphome compile`. |
| D5 | **Release-note template + artifact-naming** | A pre-written firmware release-note template and the canonical artifact-naming string for the eventual build. |
| D6 | **Bench / evidence test matrix** | The pre-written checklist of measurements the bench session must record to move the board from `design-complete` to `verified`. |

Deliverables that **cannot proceed without gerbers / BOM** are flagged
**ARTIFACT-BLOCKED** in [§4](#4-artifact-blocked-deliverables). The
per-board tables below mark each deliverable `AUTHORABLE NOW`,
`PARTIAL`, or `ARTIFACT-BLOCKED`.

### 3.1 `S360-311` Sense360 PWM (SELV, 12 V) — lead SELV board

Source artifacts:
[schematic PDF](hardware/schematics/S360-311-R4.pdf),
[artifact index](hardware/artifacts/S360-311-R4.md),
reference docs
[`s360-311-r4-pwm.md`](hardware/s360-311-r4-pwm.md) /
[`s360-311-r4-fanpwm.md`](hardware/s360-311-r4-fanpwm.md),
native fan GPIO map
[`s360-100-native-fan-gpio-map.md`](hardware/s360-100-native-fan-gpio-map.md).

| Deliverable | State | Notes / owed |
|---|---|---|
| D1 pinmap | AUTHORABLE NOW | `J3` 13-pin "From Core", four fan outputs `J1`/`J2`/`J4`/`J5`, Nextion `J6`, MT3608 boost — all schematic-printed. Carries the open `"NINE 4pin FANs"` label vs four-connector question and the `J3` 11/12 UART-routing question (owned by `HW-PINMAP-311`) as **STILL OWED**, not invented away. |
| D2 firmware package | PARTIAL — blocked on SX1509 reconcile | `packages/expansions/fan_pwm.yaml` + the SX1509 binding layer `fan_pwm_sx1509.yaml` are **legacy / superseded**: the refreshed R4 design terminates `TachPMW1..4` / `Pul_Cou1..4` / `TachIO` on **native ESP32-S3 GPIO** (`IO10/11/12/39` drive; `IO17/18/46/9` tach; `IO16` shared). Re-bind is owned by the SX1509 reconcile slice ([§5](#5-sx1509-deprecation-reconciliation-slice)) and `PACKAGE-PWM-001`. |
| D3 bundle / config-string | AUTHORABLE NOW (draft) | `FanPWM` token already in `canonical_modules`; subject to the fan-driver `max-one-of` rule. Draft only; no WebFlash. |
| D4 compile-only target | PARTIAL | A legacy SX1509 compile-only target exists as historical proof; the native-GPIO re-bind needs its own compile-only target proven green. |
| D5 release-note template + artifact name | AUTHORABLE NOW | Template + `Sense360-…-FanPWM-…` naming draftable now. |
| D6 bench test matrix | AUTHORABLE NOW | PWM polarity, per-fan + aggregate current, thermal, per-fan RPM via native `pulse_counter` (the SX1509 pulse-counter path is compile-proven unsupported — see `fan_pwm_sx1509.yaml` capability note). |

> **Executed (`PRE-HW-PREP-FW-311-001`, 2026-05-31).** `S360-311` is
> **design-complete** (prose annotation; not `verified`). D1 (pinmap from
> the committed schematic — `J3` 13-pin, four fan outputs `J1`/`J2`/`J4`/`J5`,
> Nextion `J6`, MT3608 boost) and D2 (firmware) build on the completed
> `SX1509-RECONCILE-001` + `PACKAGE-PWM-001`: D2 finalises
> [`packages/expansions/fan_pwm_native.yaml`](../packages/expansions/fan_pwm_native.yaml)
> as the **four-channel** native PWM+tach driver (four `ledc` PWM-drive
> outputs `TachPMW1..4` -> `IO10`/`IO11`/`IO12`/`IO39` feeding four
> `fan: speed` controllers; three native `pulse_counter` tach inputs
> `Pul_Cou1`/`2`/`4` -> `IO17`/`IO18`/`IO9` as the per-fan-RPM mechanism,
> internal/no-RPM-claim), and reconciles the stale single-channel
> `fan_pwm_pin: GPIO4` / `fan_tach_pin: GPIO5` placeholder in
> [`packages/hardware/sense360_core_mapping.yaml`](../packages/hardware/sense360_core_mapping.yaml)
> to the four-channel native map (marked legacy/superseded) **without**
> changing the production `GPIO4`/`GPIO5` radar-UART binding in the Core
> board package and **without** adding a `packages/boards/` package for
> `S360-311`. D3 (the `Ceiling-POE-FanPWM` bundle composing the native
> driver, config string + entity names byte-identical) and D4 (compile-only
> targets `validated-full-compile` by `S360-311-NATIVE-FANPWM-COMPILE-001`,
> local run 2026-05-28, commit `643bbd3`, rc=0) were landed by
> `SX1509-RECONCILE-001`; ESPHome is unavailable here so no new compile is
> run or fabricated. This slice adds **D5** (release-note template +
> artifact-naming scheme) and **D6** (the pre-written bench / evidence test
> matrix), and records the design-complete checklist
> ([`s360-311-r4-fanpwm.md` §Design-complete status](hardware/s360-311-r4-fanpwm.md#design-complete-status-pre-hw-prep-fw-311-001)).
> The owed items — the `"NINE 4pin FANs"` label, the `J3` 11/12 UART
> routing, the `J3` 1-to-13 silkscreen order, the `J6`↔`J3` harness, the
> `Pul_Cou3`/`IO46` fourth-tach collision, PWM polarity (`PWM-6`), per-fan +
> aggregate current, the thermal envelope, and per-fan RPM (`PWM-13`) — stay
> **OWED** to `HW-PINMAP-311` and are captured in the D6 matrix, resolved
> none. No `schematic_status` / lifecycle / WebFlash flip.

### 3.2 `S360-312` Sense360 DAC (SELV, 0–10 V) — lead SELV board

Source artifacts:
[schematic PDF](hardware/schematics/S360-312-R4.pdf),
[artifact index](hardware/artifacts/S360-312-R4.md),
reference docs
[`s360-312-r4-dac.md`](hardware/s360-312-r4-dac.md) /
[`s360-312-r4-fandac.md`](hardware/s360-312-r4-fandac.md).

| Deliverable | State | Notes / owed |
|---|---|---|
| D1 pinmap | AUTHORABLE NOW (one flag owed) | `J1` 6-pin "From Core", dual `GP8403` DACs (`IC1`/`IC2`) on shared I²C, `J2`/`J3` Cloudlift outputs, Nextion `J7`. Carries the **voltage-rail discrepancy** (Core J7 pin-1 `+5V` vs module J1 pin-1 `+3.3V`) as a wiring-relevant **STILL OWED** flag (owned by `HW-PINMAP-312`); not resolved here. |
| D2 firmware package | AUTHORABLE NOW (no SX1509 dependency) | `packages/expansions/fan_gp8403.yaml`. Dual-DAC I²C address-selection (`SW1`/`SW2`, `A0..A2` / `2A0..2A2`) must be parameterised, not assumed to a single address. DAC path is native I²C — **no SX1509 involvement**, so 312 is the cleanest lead board. |
| D3 bundle / config-string | AUTHORABLE NOW (draft) | `FanDAC` in `canonical_modules`; subject to `max-one-of` **and** the explicit `FanDAC ↔ AirIQ` mutex. Draft only; no WebFlash. |
| D4 compile-only target | AUTHORABLE NOW | Compile-only target for the dual-GP8403 composition. |
| D5 release-note template + artifact name | AUTHORABLE NOW | |
| D6 bench test matrix | AUTHORABLE NOW | 0–10 V output linearity per channel, the +5V-vs-+3.3V rail confirmation, I²C address-collision check against Core devices, blocking-diode behaviour. |

> **Executed (`PRE-HW-PREP-FW-312-001`, 2026-05-31).** `S360-312` is
> **design-complete** (prose annotation; not `verified`). D1–D4 were
> already landed by the earlier FanDAC slices — D1 by `HW-PINMAP-312` /
> `HW-PINMAP-312-FOLLOWUP`
> ([`s360-312-r4-dac.md`](hardware/s360-312-r4-dac.md) /
> [`s360-312-r4-fandac.md`](hardware/s360-312-r4-fandac.md)), D2 by
> `PACKAGE-DAC-001` (the dual-`GP8403`
> [`fan_gp8403.yaml`](../packages/expansions/fan_gp8403.yaml): two DACs
> on `core_i2c`, four neutral outputs, per-chip address + `voltage:`
> substitutions, stale `GPIO39`/`GPIO40` header already corrected to the
> Core `IO48`/`IO45` bus), D3 by `PRODUCT-DAC-001`
> ([`products/bundles/ceiling-poe-fandac.yaml`](../products/bundles/ceiling-poe-fandac.yaml),
> config string `Ceiling-POE-FanDAC`), and D4 by `FW-COMPILE-DAC-001`
> (compile-only targets, full compile green in run
> [`26364679370`](https://github.com/sense360store/esphome-public/actions/runs/26364679370)).
> This slice adds **D5** (release-note template + artifact-naming
> scheme) and **D6** (the pre-written bench / evidence test matrix), and
> records the design-complete checklist
> ([`s360-312-r4-fandac.md` §Design-complete status](hardware/s360-312-r4-fandac.md#design-complete-status-pre-hw-prep-fw-312-001)).
> The owed items — the Core-`J7`-`+5V`-vs-module-`J1`-`+3.3V` rail, the
> `SW1`/`SW2` DIP→I²C-address mapping, the `J2`/`J3` Cloudlift
> silkscreen pin order, and the `5V`/`10V` voltage-mode jumper — stay
> **OWED** to `HW-PINMAP-312-FOLLOWUP` and are captured in the D6 matrix,
> not resolved here. No `schematic_status` / lifecycle / WebFlash flip.

### 3.3 `S360-310` Sense360 Relay (mains-switching)

Source artifacts:
[schematic PDF](hardware/schematics/S360-310-R4.pdf),
[artifact index](hardware/artifacts/S360-310-R4.md),
reference docs
[`s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md) /
[`s360-310-relay-pinmap-reconcile.md`](hardware/s360-310-relay-pinmap-reconcile.md).

| Deliverable | State | Notes / owed |
|---|---|---|
| D1 pinmap | AUTHORABLE NOW | Module + Core-side relay net reconciliation from the schematic. |
| D2 firmware package | AUTHORABLE NOW (logic side) | `FanRelay` on/off control logic is SELV-side firmware; authorable. The relay drives a **mains** fan load — the load-side clearance / contact-rating review is ARTIFACT-BLOCKED (D-Review). |
| D3 bundle / config-string | AUTHORABLE NOW (draft) | |
| D4 compile-only target | AUTHORABLE NOW | |
| D5 release-note template + artifact name | AUTHORABLE NOW | |
| D6 bench test matrix | PARTIAL | SELV switching logic testable; mains-side switching evidence is part of the safety handoff ([§6](#6-hardware-verification-handoff-per-board)). |
| **D-Review** clearance/creepage (load side) | **ARTIFACT-BLOCKED** | Mains load switching; needs gerbers + BOM. See [§4](#4-artifact-blocked-deliverables). |

### 3.4 `S360-320` Sense360 TRIAC (mains phase-dimmer)

Source artifacts:
[schematic PDF](hardware/schematics/S360-320-R4.pdf),
[artifact index](hardware/artifacts/S360-320-R4.md),
reference doc
[`s360-320-r4-triac.md`](hardware/s360-320-r4-triac.md),
compliance tracker
[`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md).

| Deliverable | State | Notes / owed |
|---|---|---|
| D1 pinmap | PARTIAL | `J15` TRIAC connector nets `TRI_GPIO1`/`TRI_GPIO2` are **not** visible on a free ESP32 GPIO on the Core sheet (release-one-hardware-audit Required follow-up). Resolving the gate / zero-cross routing is owned by the SX1509 reconcile slice + `S360-320`-schematic trace. |
| D2 firmware package | **BLOCKED (HW-005)** | `packages/expansions/fan_triac.yaml` uses ESPHome `ac_dimmer`, which needs **direct interrupt-capable ESP32 GPIO** for both `gate_pin` and `zero_cross_pin`. Current placeholders (`GPIO5`/`GPIO6`) are provably wrong on a Release-One unit. Even a verified SX1509 mapping cannot meet `ac_dimmer` timing (I²C-bus latency vs ~8.33–10 ms half-cycle). This is a design-resolution slice, not authorable as-is. |
| D3–D5 | PARTIAL | Draftable only after D1/D2 resolve. |
| D6 bench test matrix | AUTHORABLE NOW (skeleton) | Phase-angle timing, zero-cross detection, mains-load behaviour — as a checklist; values blocked. |
| **D-Review** clearance/creepage + COMPLIANCE-001 | **ARTIFACT-BLOCKED + safety-gated** | Mains phase control; needs gerbers + BOM **and** COMPLIANCE-001 sign-off. |

### 3.5 `S360-400` Sense360 240v PSU (mains → 5 V)

Source artifacts:
[schematic PDF](hardware/schematics/S360-400-R4.pdf),
[artifact index](hardware/artifacts/S360-400-R4.md),
reference doc
[`s360-400-r4-power.md`](hardware/s360-400-r4-power.md).

| Deliverable | State | Notes / owed |
|---|---|---|
| D1 pinmap | AUTHORABLE NOW (with flags) | `J1` 3-pin AC input (`LIVE`/`NEUTRAL`/`Earth_Protective`), `F1` fuse, `RV1` MOV, AC/DC converter. Carries the converter-identity disagreement (catalog `HLK-5M05` vs package header `HLK-PM01 or similar` vs schematic `PS1 = HLK-10M05`) as **STILL OWED** (owned by `PACKAGE-POWER-400-001`). |
| D2 firmware package | N/A (passive PSU) | The 400 is a passive power supply; there is no driver firmware to author. "design-complete" for 400 reduces to D1 + D6 + D-Review. |
| D3–D5 | N/A / PARTIAL | No config string; PSU is composed into a powered product, not flashed. |
| D6 bench test matrix | AUTHORABLE NOW (skeleton) | Output rail under load, ripple, thermal, inrush — checklist only. |
| **D-Review** creepage/clearance + COMPLIANCE-001 | **ARTIFACT-BLOCKED + safety-gated** | Mains isolation; needs gerbers + BOM; needs COMPLIANCE-001 UK/EU sign-off. A schematic is **not** a compliance artefact. |

### 3.6 `S360-410` Sense360 PoE PSU (PoE → 5 V, isolated)

Source artifacts:
[schematic PDF](hardware/schematics/S360-410-R4.pdf),
[artifact index](hardware/artifacts/S360-410-R4.md),
reference doc
[`s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md) (`HW-PINMAP-410`),
package
[`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml).

| Deliverable | State | Notes / owed |
|---|---|---|
| D1 pinmap | AUTHORABLE NOW (with flags) | RJ45 magnetics module (`LAN_CON1`), `TPS2378` PoE PD controller, `TX4138` flyback, `F0505S-2WR2` isolation, the pre-/post-isolation net split (`+5VP`/`GND` re-referenced, **not** the same node as pre-isolation `Earth`/`Lan_earth`). Part-identity disagreement (`power_poe.yaml` integrated-PoE hint vs schematic discrete topology) owed to `PACKAGE-POE-410-001`. |
| D2 firmware package | N/A (passive PSU) | Like 400, the 410 is a power supply; no driver firmware. "design-complete" reduces to D1 + D6 + D-Review. |
| D3–D5 | N/A / PARTIAL | |
| D6 bench test matrix | AUTHORABLE NOW (skeleton) | PoE link-up against 802.3af/at PSE, output rail under load, isolation behaviour — checklist only. |
| **D-Review** isolation / Hi-pot / creepage across the isolation boundary | **ARTIFACT-BLOCKED + safety-gated** | Needs gerbers + BOM for the isolation-boundary clearance/creepage review; Hi-pot / insulation-resistance / leakage are **bench-and-certification** evidence the design review cannot substitute. |

---

## 4. ARTIFACT-BLOCKED deliverables

The repository holds **only schematic PDFs**. Every deliverable below
requires gerbers and/or BOM and **cannot proceed** until those
artifacts are committed. This plan does not fabricate their existence
and does not schedule their authoring against a date — only against the
arrival of the artifacts.

| Board | Blocked deliverable | Blocking artifact(s) | Why a schematic is not enough |
|---|---|---|---|
| `S360-410` | **Clearance / creepage design review across the PoE isolation boundary** | gerbers (copper + soldermask layers), BOM (isolation part ratings) | Clearance/creepage are **physical layout** distances between copper at different potentials; they are measurable only from the board layout (gerbers), not from a netlist/schematic. The `F0505S-2WR2` isolation rating and the pre-/post-isolation `GND` ≠ `Earth` split need the BOM part ratings. |
| `S360-410` | Hi-pot / insulation-resistance / leakage evidence | (bench + certification, not a repo artifact) | Listed here for completeness: this is **never** a design-review deliverable — it is bench-and-certification evidence (see [§6](#6-hardware-verification-handoff-per-board)). |
| `S360-400` | **Creepage / clearance design review (mains isolation)** | gerbers, BOM (X/Y-cap safety class, MOV rating, fuse rating, converter identity) | Same physical-layout reason; plus the `HLK-5M05` / `HLK-PM01` / `HLK-10M05` converter-identity disagreement needs the BOM to settle. |
| `S360-320` | **Creepage / clearance design review (mains phase control)** | gerbers, BOM | Mains-side TRIAC + opto isolation distances are layout-defined. |
| `S360-310` | **Clearance / contact-rating review (mains relay load side)** | gerbers, BOM (relay contact rating, load-side copper) | The relay coil/logic is SELV (authorable); the **switched mains load** clearance and contact current rating are layout/BOM-defined. |
| all six | BOM-dependent procurement / assembly validation, STEP/mechanical fit | BOM, CPL, STEP | Out of scope until the manufacturing artifacts land. |

> **Plainly stated:** the clearance/creepage design reviews for the
> PoE board (`S360-410`) and the three mains boards (`S360-310`,
> `S360-320`, `S360-400`) **cannot proceed until the gerbers and BOM
> for those boards are committed.** No amount of schematic-derived
> work substitutes for the board-layout artifacts. These items are
> queued *after* the artifacts land ([§7](#7-ordered-slice-sequence)),
> not before.

---

## 5. SX1509 deprecation reconciliation slice

The operator has stated the **SX1509 I/O expander is deprecated**. It
is still referenced across the repo. This plan captures the
deprecation as its **own early reconciliation slice**
(`PRE-HW-PREP-SX1509-RECONCILE-001`, coordinating with the systemic
[`CORE-ABSTRACT-BUS-001`](hardware/core-abstract-bus-reconciliation.md)
and the native fan GPIO map
[`S360-100-NATIVE-FAN-GPIO-MAP-001`](hardware/s360-100-native-fan-gpio-map.md)).
**No YAML is changed here.** This section identifies every reference
and the direct / native path it should resolve to, for that slice to
execute.

### 5.1 Why the native path is already evidenced

The refreshed `S360-100-R4` Core schematic terminates the entire fan
signal path on **native ESP32-S3 GPIO**; the SX1509 (`U3`) block is no
longer printed on the visible sheet. The canonical native map (from
[`s360-100-native-fan-gpio-map.md`](hardware/s360-100-native-fan-gpio-map.md),
schematic-printed, **not** bench-verified):

| Logical fan signal | Native ESP32-S3 GPIO | Prior (deprecated) SX1509 route |
|---|---|---|
| `TachPMW1..4` (PWM drive) | `IO10` / `IO11` / `IO12` / `IO39` | SX1509 channels 0..3 |
| `Pul_Cou1..4` (tach) | `IO17` / `IO18` / `IO46` / `IO9` | SX1509 channels 4..7 |
| `TachIO` (shared passthrough) | `IO16` (unchanged) | — (always native) |

A `pulse_counter` on an SX1509 pin is **compile-proven unsupported**
(see the capability note in
[`fan_pwm_sx1509.yaml`](../packages/expansions/fan_pwm_sx1509.yaml) and
[`tests/test_sx1509_tach_pulse_counter_proof.py`](../tests/test_sx1509_tach_pulse_counter_proof.py));
the native interrupt-capable pins above **can** back a `pulse_counter`.
This is the technical reason the native path is the resolution target,
not merely an operator preference.

### 5.2 Reference inventory and resolution targets

Every SX1509 reference and the path the reconcile slice should resolve
it to (the slice executes these; **this PR does not**):

| Reference | Current SX1509 role | Resolution target |
|---|---|---|
| [`packages/expansions/gpio_expander_sx1509.yaml`](../packages/expansions/gpio_expander_sx1509.yaml) | SX1509 hub @ `0x3E`: fan PWM (0–3), tach (4–7), aux PWM (8–11), inputs (12–15) | Mark **legacy / superseded** for the fan path; retire the fan/tach lanes in favour of the native map. Any genuinely non-fan use must be re-justified or removed under the deprecation. |
| [`packages/expansions/fan_pwm_sx1509.yaml`](../packages/expansions/fan_pwm_sx1509.yaml) | Neutral SX1509 binding layer (drive 0–3, tach 4–7, `tach_io_pin: GPIO16`) | Superseded by the native re-bind; the FanPWM package consumes native `IO10/11/12/39` + `IO17/18/46/9` + `IO16` instead. |
| [`packages/expansions/fan_pwm.yaml`](../packages/expansions/fan_pwm.yaml) | Fan controllers composed on the SX1509 drive outputs | Re-bind to native GPIO (owned jointly with `PACKAGE-PWM-001`); decide single-channel vs four-channel abstraction. |
| [`packages/expansions/fan_pwm_native.yaml`](../packages/expansions/fan_pwm_native.yaml), [`fan_12v_pwm.yaml`](../packages/expansions/fan_12v_pwm.yaml) | SX1509 references in 12 V PWM lanes | Reconcile to native map; resolve duplication with `fan_pwm.yaml`. |
| [`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml) | `TRI_GPIO1/2` suspected SX1509-routed | **Cannot** resolve to SX1509 (ac_dimmer timing) — resolve to a **direct interrupt-capable ESP32 GPIO** mapping once the `S360-320` schematic trace lands, or a non-`ac_dimmer` driver. Stays HW-005-blocked. |
| [`packages/boards/s360-100-core.yaml`](../packages/boards/s360-100-core.yaml) | SX1509 expander instantiation on the Core | Remove the SX1509 from the fan path; keep only any re-justified non-fan use. |
| [`packages/hardware/sense360_core_mapping.yaml`](../packages/hardware/sense360_core_mapping.yaml) | I²C `0x3E`/`0x3F` SX1509 address comments; `fan_pwm_pin: GPIO4` / `fan_tach_pin: GPIO5` (contradict the native map) | Reconcile the single-channel `GPIO4/5` placeholder against the four-channel native map; update the address table comment. |
| [`packages/hardware/sense360_core*.yaml`](../packages/hardware/) (core, ceiling, voice variants), [`power_management.yaml`](../packages/hardware/power_management.yaml) | Inherited SX1509 references | Sweep for inherited references; resolve to native or remove. |
| `config/*.json` (`compile-only-targets`, `compile-only-candidates`, `product-catalog`, `kit-intent-matrix`, `firmware-combination-matrix`) | SX1509-bearing compile/candidate rows | The reconcile slice's **config follow-up** retargets these to the native compositions (separate from the YAML slice; still not in this PR). |
| docs (`release-one-hardware-audit.md`, `cleanup-audit.md`, `webflash-drift-audit.md`, et al.) | SX1509 narrative references | Update prose to point at the native map as canonical; keep the historical SX1509 proof as historical. |

### 5.3 Slice guardrails

`PRE-HW-PREP-SX1509-RECONCILE-001` is a **firmware/config reconciliation
slice**, executed *after* this plan, that: (a) re-binds the fan path to
native GPIO per the schematic-printed map; (b) marks every residual
SX1509 fan reference legacy/superseded; (c) keeps the historical
SX1509 compile-proof fixture intact; (d) invents **no** GPIO numbers
beyond schematic-printed values; (e) compiles end-to-end before any
status change; and (f) does **not** by itself promote, verify, or
WebFlash-expose anything. The TRIAC TRI_GPIO routing stays HW-005-blocked
regardless.

> **Executed (`SX1509-RECONCILE-001`).** This slice has landed. The
> FanPWM bundle now composes the native `fan_pwm_native.yaml` driver
> (the native composition is full-compile validated by
> `S360-311-NATIVE-FANPWM-COMPILE-001` / commit `643bbd3`); the stale
> SX1509 Core I²C-device comment and the current FanPWM config rows are
> retargeted to native; the legacy SX1509 packages
> (`fan_pwm.yaml`, `fan_pwm_sx1509.yaml`, `gpio_expander_sx1509.yaml`,
> `fan_12v_pwm.yaml`) and the legacy compile-only skeleton are
> **kept-with-reason** (no live binder remains, but tests / the
> historical compile proof read them and
> `S360-100-NATIVE-FAN-GPIO-MAP-001` forbids removing the SX1509
> globally), each carrying a legacy/superseded banner. The fan boards
> stay `hardware-pending` / unverified (design-complete only); the
> native path's current/thermal evidence (`PWM-6` / `PWM-13`) stays
> owed; TRIAC stays HW-005-blocked.

---

## 6. Hardware-verification handoff per board

`design-complete → verified` happens **only** at the bench. This
section fixes, per board, exactly what the bench session must
measure / confirm to flip the board, and — for PoE / mains — what
safety evidence and sign-off the design review can **never** substitute.

General rule for all six: the `cataloged_unverified → verified` flip is
a **separate JSON-catalog PR** that runs only after the per-board
pin-map reconciliation (`HW-PINMAP-3xx`) is closed against **physical**
silkscreen/harness evidence and the bench matrix (D6) is filled. The
flip is gated per
[`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md).

| Board | Bench must measure / confirm to reach `verified` | Safety evidence the design review CANNOT substitute |
|---|---|---|
| `S360-311` PWM | Silkscreen confirms `J3` 1-to-13 order + the `J6`↔`J3` harness; native PWM drive on `IO10/11/12/39`; per-fan + aggregate fan current; thermal envelope; per-fan RPM via native `pulse_counter`; resolve `"NINE 4pin FANs"` label + `J3` 11/12 UART routing. | — (SELV; no mains/PoE safety gate) |
| `S360-312` DAC | Resolve the **+5V vs +3.3V rail** discrepancy on silkscreen; 0–10 V linearity per channel; dual-DAC I²C addresses (`SW1`/`SW2`) + collision check against Core devices; blocking-diode behaviour; Cloudlift output pin order. (queued as `S360-312-DAC-BENCH-001`, blocked on hardware) | — (SELV) |
| `S360-310` Relay | Relay logic + contact switching of a real mains fan load; contact bounce; SELV/mains domain separation on silkscreen. | **Mains contact-rating + clearance**: switched-load current rating and load-side clearance are layout/BOM + bench evidence; not provable from schematic. |
| `S360-320` TRIAC | Direct-ESP32 gate/zero-cross mapping confirmed; zero-cross detection; phase-angle timing into a real mains load; opto isolation. | **COMPLIANCE-001 UK/EU mains sign-off** + creepage/clearance review (gerbers) + EMC. The design review **cannot** clear COMPLIANCE-001; a schematic is not a compliance artefact. |
| `S360-400` 240v PSU | Output rail under load; ripple; inrush; thermal; converter identity (`HLK-?`) confirmed against the populated part. | **COMPLIANCE-001 mains sign-off** + creepage/clearance (gerbers) + Hi-pot/insulation resistance + X/Y-cap safety-class confirmation. None substitutable by design review. |
| `S360-410` PoE PSU | PoE link-up against an 802.3af/at PSE; output rail under load; PD controller (`TPS2378`) + flyback (`TX4138`) behaviour; pre-/post-isolation `GND`≠`Earth` confirmed. | **Hi-pot / insulation-resistance / leakage across the isolation boundary** + isolation creepage/clearance review (gerbers) + isolation-part rating (`F0505S-2WR2`, BOM). The design review **cannot** stand in for Hi-pot or certification evidence. |

> For the PoE board and the three mains boards, **no design-derived
> artifact — including a fully reconciled, fully compiled
> `design-complete` firmware — moves the board to `verified`.** The
> safety-evidence column is mandatory and bench/certification-sourced.

---

## 7. Ordered slice sequence

The program executes in this order. Each row is a future PR; this plan
authors none of them. SELV-first, artifact-blocked items deferred to
artifact arrival, mains/PoE safety review last.

| # | Slice ID | Scope | Gate / precondition |
|---|---|---|---|
| 1 | `PRE-HW-PREP-SX1509-RECONCILE-001` — **DONE** (landed as `SX1509-RECONCILE-001`) | Re-bind the fan path to native ESP32-S3 GPIO; mark residual SX1509 fan refs legacy/superseded ([§5](#5-sx1509-deprecation-reconciliation-slice)). Firmware + the config retarget. **Executed:** the FanPWM bundle (`products/bundles/ceiling-poe-fanpwm.yaml`) now composes `packages/expansions/fan_pwm_native.yaml` instead of the deprecated `fan_pwm.yaml` -> `fan_pwm_sx1509.yaml` chain (config string + entity names byte-identical); the stale SX1509 Core I²C-device comment + the FanPWM config rows (`product-catalog`, `compile-only-targets`) are retargeted to native; the legacy SX1509 packages + compile-only skeleton + historical proof are kept-with-reason. Fan boards stay hardware-pending/unverified; TRIAC stays HW-005-blocked. | None beyond this plan. Ran **first** so the SELV firmware slices build on the native map, not the deprecated expander. |
| 2 | `PRE-HW-PREP-FW-312-001` — **DONE** (2026-05-31) | `S360-312` DAC: D1–D6 (native I²C, **no SX1509 dependency** — cleanest lead). **Executed:** `S360-312` recorded **design-complete** (prose; not `verified`). D1–D4 carried from the earlier FanDAC slices (`HW-PINMAP-312` / `PACKAGE-DAC-001` / `PRODUCT-DAC-001` / `FW-COMPILE-DAC-001`, full compile green in run [`26364679370`](https://github.com/sense360store/esphome-public/actions/runs/26364679370)); this slice added D5 (release-note template + artifact-naming) + D6 (bench / evidence test matrix) and the design-complete checklist in [`s360-312-r4-fandac.md`](hardware/s360-312-r4-fandac.md). Rail / DIP→address / Cloudlift pin-order / voltage-mode-jumper stay OWED to `HW-PINMAP-312-FOLLOWUP`. No `schematic_status` / lifecycle / WebFlash flip. | Slice 1 not strictly required (no SX1509 in DAC path); may run in parallel with 1. |
| 3 | `PRE-HW-PREP-FW-311-001` — **DONE** (2026-05-31) | `S360-311` PWM: D1–D6 re-bound to native GPIO; resolve single- vs four-channel abstraction (with `PACKAGE-PWM-001`). **Executed:** `S360-311` recorded **design-complete** (prose; not `verified`). D1–D4 build on `SX1509-RECONCILE-001` / `PACKAGE-PWM-001` — D2 finalised the **four-channel** native driver [`fan_pwm_native.yaml`](../packages/expansions/fan_pwm_native.yaml) and reconciled the stale single-channel `GPIO4`/`GPIO5` placeholder in [`sense360_core_mapping.yaml`](../packages/hardware/sense360_core_mapping.yaml) (legacy/superseded; production radar-UART binding untouched; no `packages/boards/` package added); D3/D4 carried from slice 1 (native bundle + `validated-full-compile` by `S360-311-NATIVE-FANPWM-COMPILE-001`, local run 2026-05-28, commit `643bbd3`). This slice added D5 (release-note template + artifact-naming) + D6 (bench / evidence test matrix) and the design-complete checklist in [`s360-311-r4-fanpwm.md`](hardware/s360-311-r4-fanpwm.md). The `"NINE 4pin FANs"` label, `J3` 11/12 UART routing, `J3` silkscreen order, `J6`↔`J3` harness, `Pul_Cou3`/`IO46` collision, PWM polarity, current/thermal, and per-fan RPM (`PWM-6`/`PWM-13`) stay OWED to `HW-PINMAP-311`. No `schematic_status` / lifecycle / WebFlash flip. | Slice 1 (native re-bind). |
| 4 | `PRE-HW-PREP-FW-310-001` | `S360-310` Relay: D1–D6 SELV logic side (relay control). Load-side review deferred to slice 7. | — |
| 5 | `PRE-HW-PREP-TESTMATRIX-SELV-001` | Consolidate / finalise the D6 bench test matrices for 310/311/312 as the bench checklist. | Slices 2–4. |
| 6 | `PRE-HW-PREP-GERBER-REVIEW-001` *(blocked)* | Clearance/creepage + load-side reviews for `S360-310`/`S360-320`/`S360-400`/`S360-410` — the ARTIFACT-BLOCKED D-Review items ([§4](#4-artifact-blocked-deliverables)). | **Gerbers + BOM committed** for the relevant boards. Cannot start before artifacts land. |
| 7 | `PRE-HW-PREP-TRIAC-320-001` *(HW-005 / safety)* | `S360-320` TRIAC: resolve direct-ESP32 gate/zero-cross mapping; D1–D6; **COMPLIANCE-001** mains sign-off. | Slice 6 (gerbers) + `S360-320` schematic trace + COMPLIANCE-001. |
| 8 | `PRE-HW-PREP-MAINS-400-001` *(safety)* | `S360-400` 240v PSU: D1 + D6 + creepage/clearance review; **COMPLIANCE-001** sign-off. | Slice 6 + COMPLIANCE-001. |
| 9 | `PRE-HW-PREP-POE-410-001` *(safety)* | `S360-410` PoE PSU: D1 + D6 + isolation-boundary creepage/clearance review; Hi-pot/isolation evidence framed (bench/cert). | Slice 6 + `PACKAGE-POE-410-001` preconditions. |
| 10 | `S360-312-DAC-BENCH-001` *(next hardware task)* | `S360-312` DAC: run the D6 bench / evidence matrix once a physical board exists; fill the owed measurements (0–10 V output per channel; GP8403 detection + I²C address; range/calibration; fan/controller response; current; thermal; harness/silkscreen). | A physical `S360-312` board in hand (pre-hardware; blocked). |

Rationale: SELV boards (312, 311, 310) carry no mains/PoE safety gate
and are fully or mostly authorable from the schematics now, so they go
first; the SX1509 reconcile precedes them so they build on the native
map. The gerber-dependent reviews and the mains/PoE safety slices are
last because they are blocked on artifacts and/or sign-off that the
design phase cannot produce.

---

## 8. Validation

This PR is docs-only; the commands below confirm it breaks nothing:

* `python3 tests/validate_configs.py`
* `python3 tests/test_roadmap_status_doc.py`
* `python3 -m unittest discover -s tests -p "test_*.py"`

---

## 9. See also

- [Hardware Artifact Policy (HW-ASSETS-001)](hardware/hardware-artifact-policy.md)
- [S360-311-R4](hardware/artifacts/S360-311-R4.md) /
  [S360-312-R4](hardware/artifacts/S360-312-R4.md) artifact indexes
- [Native Fan GPIO Map (S360-100-NATIVE-FAN-GPIO-MAP-001)](hardware/s360-100-native-fan-gpio-map.md)
- [Core Abstract-Bus Reconciliation (CORE-ABSTRACT-BUS-001)](hardware/core-abstract-bus-reconciliation.md)
- [Release-One Hardware Audit](release-one-hardware-audit.md) (FanTRIAC / HW-005, Required follow-ups)
- [Preview-to-Stable Promotion Gates (RELEASE-006)](preview-to-stable-promotion-gates.md)
- [Product Deprecation and Removal Policy (PRODUCT-DEP-001)](product-deprecation-removal-policy.md)
- [Mains-Voltage UK/EU Assessment (COMPLIANCE-001)](compliance/mains-voltage-uk-eu-assessment.md)
- [Board Readiness Matrix (HW-GAP-001)](hardware/board-readiness-matrix.md)
- [First-Release Gates (PRE-HW-PREP-FIRST-RELEASE-GATES-001)](first-release-gates.md) — consolidated "what can ship now / what is blocked / what evidence is required" checklist
- [`UPCOMING_PR.md`](../UPCOMING_PR.md)

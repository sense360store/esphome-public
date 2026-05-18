# Package YAML Readiness Matrix (PACKAGE-GAP-001)

## Purpose and scope

This document is the canonical, **package-level** readiness gate for
the expansion / power packages that PACKAGE-GAP-001 covers — the
fan-driver packages
[`packages/expansions/fan_relay.yaml`](../../packages/expansions/fan_relay.yaml),
[`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml),
[`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml),
[`packages/expansions/fan_triac.yaml`](../../packages/expansions/fan_triac.yaml),
and the power packages
[`packages/hardware/power_240v.yaml`](../../packages/hardware/power_240v.yaml)
and
[`packages/hardware/power_poe.yaml`](../../packages/hardware/power_poe.yaml).
It records, per package, the current evidence state, the known
schematic / pin-map conflicts, the allowed action right now, and the
named follow-up PR that owns the package's reconciliation.

PACKAGE-GAP-001 exists because the original backlog row — *"add or
reconcile package YAMLs for missing modules where pin-map evidence
exists"* — must be gated against actual evidence. The HW-PINMAP-*
audits that PACKAGE-GAP-001 depends on are all `partial`, `pending`,
or `blocked`:

- HW-PINMAP-310 ([`s360-310-r4-relay.md`](s360-310-r4-relay.md)) —
  `pending — schematic/design evidence required`,
- HW-PINMAP-311 ([`s360-311-r4-pwm.md`](s360-311-r4-pwm.md)) —
  `partial — schematic evidence available; package reconciliation
  pending`,
- HW-PINMAP-312 ([`s360-312-r4-dac.md`](s360-312-r4-dac.md)) —
  `partial — schematic evidence available; package reconciliation
  pending`,
- HW-PINMAP-320 ([`s360-320-r4-triac.md`](s360-320-r4-triac.md)) —
  `partial — schematic evidence available; package reconciliation,
  timing validation, and compliance/certification pending`,
- HW-PINMAP-400 ([`s360-400-r4-power.md`](s360-400-r4-power.md)) —
  `pending — schematic/design evidence required`,
- HW-PINMAP-410 ([`s360-410-r4-poe.md`](s360-410-r4-poe.md)) —
  `pending — schematic/design evidence required`.

None of these audits clear PACKAGE-GAP-001's evidence bar today.
Therefore this document is the explicit **implementation gate** for
PACKAGE-GAP-001: it classifies each in-scope package, names the
follow-up PR that must produce the missing evidence, and **forbids**
any package YAML edit in this PR.

This document is **documentation only**. It does **not**:

- add, remove, or modify any package YAML under
  [`packages/`](../../packages/) — including all six in-scope
  packages above plus
  [`packages/expansions/sense360_fan_pwm.yaml`](../../packages/expansions/sense360_fan_pwm.yaml)
  (legacy four-channel), the Core abstract packages
  [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml)
  and
  [`packages/hardware/sense360_core.yaml`](../../packages/hardware/sense360_core.yaml),
  and every other package in the tree,
- add, remove, or modify any entry in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json),
  [`config/product-catalog.json`](../../config/product-catalog.json),
  [`config/webflash-builds.json`](../../config/webflash-builds.json),
  or [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json),
- add, remove, or modify any product YAML under
  [`products/`](../../products/) or any WebFlash wrapper under
  [`products/webflash/`](../../products/webflash/),
- add, remove, or modify any script under
  [`scripts/`](../../scripts/), any test under
  [`tests/`](../../tests/), any workflow under `.github/workflows/`,
  any component under `components/`, or any include under
  `include/`,
- mark `S360-310` / `S360-311` / `S360-312` / `S360-320` /
  `S360-400` / `S360-410` `verified`, or set `schematic_file` for
  any of them in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json),
- mark any package YAML `confirmed-ok` or `ready-for-package-change`,
- unblock FanTRIAC (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays
  `status: blocked`, `blocker: HW-005`,
  `webflash_build_matrix: false`),
- change the mains-voltage compliance status of `S360-320` or
  `S360-400` (owned by COMPLIANCE-001;
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md)),
- resolve the systemic Core abstract-bus mismatch in
  [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml)
  (owned by
  [`release-one-hardware-audit.md` Required follow-ups #2 / #3](../release-one-hardware-audit.md#required-follow-ups);
  recorded here as CORE-ABSTRACT-BUS-001),
- resolve the Core J10 vs RoomIQ J6 pin-order discrepancy
  (`needs-silkscreen/bench-verification` per HW-009),
- change the Release-One configuration
  `Ceiling-POE-VentIQ-RoomIQ` (`status: production`,
  `channel: stable`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
  `v1.0.0`),
- change the LED preview entry `Ceiling-POE-VentIQ-RoomIQ-LED`
  (stays `status: preview`, `channel: preview`),
- generate, regenerate, sign, import, deploy, or otherwise produce
  firmware, or change any WebFlash-side `REQUIRED_CONFIGS`,
  `scripts/data/kits.json`, `firmware/sources.json`, or
  `manifest.json` entry.

If this matrix and any source-of-truth document drift, **the
source-of-truth document wins** and this matrix must be updated. The
sources of truth are listed in [See also](#see-also).

## Core rule

> **Package YAML changes are allowed only when the target board has
> verified pin-map evidence and the package change can be traced to a
> schematic-backed audit. Partial, pending, or blocked audits may
> produce follow-up requirements, but must not be treated as
> implementation approval.**

This is the load-bearing premise of PACKAGE-GAP-001. It is the
package-level form of the
[`board-readiness-matrix.md` Core rule](board-readiness-matrix.md#core-rule)
("board readiness is not the same as product readiness or WebFlash
readiness") and of the
[`product-availability-taxonomy.md` Core rule](../product-availability-taxonomy.md#core-rule)
("hardware evidence does not equal firmware support, product
support, or WebFlash availability"). Any PR that argues "the
schematic PDF was committed, therefore this package is ready to
change" without supplying the named HW-PINMAP-*-FOLLOWUP evidence is
breaking the rule and must be rejected on first read.

Two corollaries follow:

- A schematic PDF on disk is **not** pin-map evidence. The committed
  HW-ASSETS-003 PDFs for `S360-311` / `S360-312` / `S360-320` close
  the schematic-evidence axis (and even for those three the JSON
  `schematic_status` stays `cataloged_unverified` per the per-board
  audits). They do **not** by themselves close the pin-map axis or
  the package-reconciliation axis. See
  [`docs/hardware/artifacts/S360-311-R4.md` Relationship to `config/hardware-catalog.json`](artifacts/S360-311-R4.md#relationship-to-confighardware-catalogjson)
  for the precedent.
- A package YAML's header-comment claims are **not** pin-map
  evidence. Header comments in
  [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)
  (`GPIO39` / `GPIO40`) and
  [`packages/hardware/power_240v.yaml`](../../packages/hardware/power_240v.yaml)
  (`HLK-PM01 or similar`) disagree with the per-board audits and
  with the JSON catalog. The disagreements are recorded here; they
  are **not** resolved by this PR.

## Status value vocabulary (policy-only)

The package readiness table below uses a small set of cell values.
**All are policy-only labels** — they are not JSON enums, not
promoted to any schema, and not added to any validator by this PR.
They sit alongside the existing HW-009 / HW-010 vocabulary
(`confirmed-ok` / `needs-package-change` / `needs-doc-fix` /
`needs-silkscreen/bench-verification` / `blocked` / `unknown` per
[`firmware-package-mapping-audit.md` Reconciliation taxonomy](firmware-package-mapping-audit.md#reconciliation-taxonomy))
and consume it where appropriate.

| Cell value | Meaning |
|---|---|
| `ready-for-package-change` | The package can be edited now. Requires a `verified` board JSON catalog row, a closed HW-PINMAP-*-FOLLOWUP audit with no outstanding `verify` flags or unresolved disagreements, and (where applicable) a closed COMPLIANCE-001 slice and a closed HW-005 work item. **No package in this matrix carries this label today.** |
| `needs-package-reconciliation` | The package is known to disagree with the schematic-backed evidence at a specific, named point (header-comment GPIOs, substitution defaults, channel cardinality, address scheme, etc.). The fix is a package-YAML edit, but only **after** the named HW-PINMAP-*-FOLLOWUP supplies the closing evidence. **Not** approval to edit in this PR. |
| `schematic-evidence-pending` | The package cannot be reconciled at all because the module-side `S360-*-R4` schematic is not committed (catalog `schematic_status: cataloged_unverified`, no `schematic_file` set). HW-ASSETS-310 / HW-ASSETS-400 / HW-ASSETS-410 (the supplier-delivery follow-ups) precede any package edit. |
| `bench-evidence-pending` | The package cannot be reconciled at all because bench / silkscreen / harness / waveform evidence is owed (e.g. PWM polarity, tach pull-up, dimmer waveform, J6 silkscreen pin order). Owned by the named HW-PINMAP-*-FOLLOWUP plus bench evidence (S360-100-BENCH-001 etc.). |
| `timing/compliance-pending` | The package cannot be promoted to a buildable surface because timing-correctness or mains-voltage compliance evidence is owed. Applies to FanTRIAC (`ac_dimmer` ISR timing + COMPLIANCE-001) and to FanPWR (COMPLIANCE-001). |
| `reference-only` | The package is logical (no GPIO binding) or retained as a blocked / reference file. Its byte content is consumed today; **no functional edits are owed** until the named follow-up clarifies whether the logical role is correct against the now-verified schematic. |
| `do-not-change-release-one` | The package is consumed by Release-One (`Ceiling-POE-VentIQ-RoomIQ`) or by the LED preview entry (`Ceiling-POE-VentIQ-RoomIQ-LED`). Any change to its semantics must clear the 17-row [`docs/preview-to-stable-promotion-gates.md`](../preview-to-stable-promotion-gates.md) gate **and** preserve the recorded artifact name / tag / channel. PACKAGE-GAP-001 does not authorise such changes; the Core abstract-bus rebind (CORE-ABSTRACT-BUS-001) owns them. |
| `blocked-from-standard-exposure` | The package is reachable only through an advanced / manual-warning surface and **must not** be added to Release-One, REQUIRED_CONFIGS, recommended / kit / default lists, or compliance-certified surfaces. Today this applies only to FanTRIAC; the intent is documented in [`s360-320-r4-triac.md` Advanced / manual-warning product posture](s360-320-r4-triac.md#advanced--manual-warning-product-posture) but the JSON lifecycle row stays `status: blocked` until HW-005 / COMPLIANCE-001 / HW-PINMAP-320-FOLLOWUP / PACKAGE-TRIAC-001 clear. |
| `unknown` | Cannot be classified from currently committed evidence. Not used in this matrix today; every package below is placeable under the labels above. |

A row may carry one primary label plus one or more additive
qualifier labels (e.g. `needs-package-reconciliation` +
`timing/compliance-pending` + `blocked-from-standard-exposure` for
FanTRIAC).

The 2026-05-18 S360-100-BENCH-001 evidence-pass re-check (see
[`s360-100-r4-core.md` Audit log](s360-100-r4-core.md#audit-log))
confirms no package row below moves off `bench-evidence-pending`
or `schematic-evidence-pending`, and no follow-up PR chain advances
as a result of this re-check. S360-100-BENCH-001 itself remains
`pending — bench/manufacturing evidence required`. The
`bench-evidence-pending` label keeps its current scope for every
fan-driver / Core-abstract-bus row below.

## Status summary

**No package in scope is `ready-for-package-change`.** All six
fan-driver / power packages are gated on at least one of:
schematic-side evidence (HW-ASSETS-310 / -400 / -410), pin-map
reconciliation evidence (HW-PINMAP-*-FOLLOWUP), bench / silkscreen
evidence, timing-correctness evidence (FanTRIAC), or mains-voltage
compliance (COMPLIANCE-001). Core abstract-bus rebinds owed for the
relay / PWM / DAC bindings remain owned by CORE-ABSTRACT-BUS-001 and
are out of scope here.

This is the expected verdict for PACKAGE-GAP-001 today, given the
state of the HW-PINMAP-* audit chain. The follow-up PR sequence in
[Follow-up PR sequence](#follow-up-pr-sequence) records the named,
per-package slices that must each be a separate scoped PR with its
own gate evidence.

## Package readiness table

| Package path | Board / module | Current role | Evidence source | Current audit status | Known conflicts | Allowed action now | Follow-up owner |
|---|---|---|---|---|---|---|---|
| [`packages/expansions/fan_relay.yaml`](../../packages/expansions/fan_relay.yaml) | `S360-310` Sense360 Relay | `FanRelay` — single on/off relay-driven fan via `${fan_relay_pin}` defaulting to `${relay_pin}` | [`s360-310-r4-relay.md`](s360-310-r4-relay.md) (HW-PINMAP-310) **`pending — schematic/design evidence required`**; module-side schematic not committed | `schematic-evidence-pending` + `needs-package-reconciliation` | `relay_pin` abstract-bus disagreement: Core schematic `Relay = IO3`; ceiling Core abstract `relay_pin: GPIO4` (`IO4 = SEN0609_RX`); generic Core abstract `relay_pin: GPIO10` (per [`s360-310-r4-relay.md` Pin-map reconciliation status](s360-310-r4-relay.md#pin-map-reconciliation-status)). Module-side connector pinout, relay-coil drive circuit, harness identity all unknown. | **No package edit.** Schematic must arrive first (HW-ASSETS-310). | `HW-ASSETS-310` → `HW-PINMAP-310-FOLLOWUP` → `PACKAGE-RELAY-001` (alias: `PACKAGE-GAP-001` FanRelay slice). Abstract-bus rebind is `CORE-ABSTRACT-BUS-001`. |
| [`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml) | `S360-311` Sense360 PWM | `FanPWM` — single-channel 25 kHz PWM fan + `pulse_counter` tach via `${fan_pwm_pin}` / `${fan_tach_pin}` | [`s360-311-r4-pwm.md`](s360-311-r4-pwm.md) (HW-PINMAP-311) **`partial — schematic evidence available; package reconciliation pending`**; module-side schematic PDF + curated artifact index committed under HW-ASSETS-003 | `needs-package-reconciliation` + `bench-evidence-pending` | SX1509-channel (`TachPMW1..4`, `Pul_Cou1..4`) vs direct-ESP32-GPIO mismatch (Core abstract `expansion_gpio1/2` resolves to `GPIO5 = SEN0609_TX` / `GPIO6 = out(gpio6)`); UART-on-`J3`-pins-11/12 routing; single-channel YAML vs four 4-pin fan output connectors on the module; PWM polarity, tach pull-up, `"NINE 4pin FANs"` documentation question (per [`s360-311-r4-pwm.md` Reconciliation flags](s360-311-r4-pwm.md#reconciliation-flags-raised-or-strengthened-by-this-schematic) and [§Existing package abstraction](s360-311-r4-pwm.md#existing-package-abstraction)). `S360-311` JSON `schematic_status` stays `cataloged_unverified`. Sibling [`packages/expansions/sense360_fan_pwm.yaml`](../../packages/expansions/sense360_fan_pwm.yaml) (legacy four-channel; direct ESP32 GPIOs) is consumed only by the legacy-compatible product [`products/sense360-fan-pwm.yaml`](../../products/sense360-fan-pwm.yaml) and stays out of any WebFlash-shippable surface. | **No package edit.** HW-PINMAP-311-FOLLOWUP must close first. | `HW-PINMAP-311-FOLLOWUP` → `S360-311` `schematic_status` promotion (separate JSON PR) → `PACKAGE-PWM-001` (alias: `PACKAGE-GAP-001` FanPWM slice). Abstract-bus rebind is `CORE-ABSTRACT-BUS-001`. |
| [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) | `S360-312` Sense360 DAC | `FanDAC` — dual-channel GP8403 12-bit DAC over I²C; two `fan: speed` entities + per-channel voltage / speed templates | [`s360-312-r4-dac.md`](s360-312-r4-dac.md) (HW-PINMAP-312) **`partial — schematic evidence available; package reconciliation pending`**; module-side schematic PDF + curated artifact index committed under HW-ASSETS-003 | `needs-package-reconciliation` + `bench-evidence-pending` | Core `J7` pin-1 `+5V` vs Module `J1` pin-1 `+3.3V` rail discrepancy; DIP-switch I²C address selection on `IC1` / `IC2` (package allows only `0x58` / `0x59`); UART0-vs-Nextion routing on Module `J1` pins 4 / 5 (shared with boot log on Core `TXD0` / `RXD0`); 5 V vs 10 V hardware-select identity; stale header-comment claims `Pin 4 (SDA) → GPIO39`, `Pin 5 (SCL) → GPIO40` disagree with Module `J1` (`I2C_SDA` / `I2C_SCL`) and Core `J7` (`IO48` / `IO45`) (per [`s360-312-r4-dac.md` Header-comment claims vs schematic evidence](s360-312-r4-dac.md#header-comment-claims-vs-schematic-evidence) and [§Reconciliation flags](s360-312-r4-dac.md#reconciliation-flags-raised-or-strengthened-by-this-schematic)). `S360-312` JSON `schematic_status` stays `cataloged_unverified`. Subject to `FanDAC` ↔ `AirIQ` mutex in [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json). | **No package edit.** HW-PINMAP-312-FOLLOWUP must close first. | `HW-PINMAP-312-FOLLOWUP` → `S360-312` `schematic_status` promotion (separate JSON PR) → `PACKAGE-DAC-001` (alias: `PACKAGE-GAP-001` FanDAC slice). |
| [`packages/expansions/fan_triac.yaml`](../../packages/expansions/fan_triac.yaml) | `S360-320` Sense360 TRIAC | `FanTRIAC` — `output: ac_dimmer` + `fan: speed` (phase-cut AC); requires direct interrupt-capable ESP32 GPIOs for `gate_pin` + `zero_cross_pin`; retained with BLOCKED / UNVERIFIED banner | [`s360-320-r4-triac.md`](s360-320-r4-triac.md) (HW-PINMAP-320) **`partial — schematic evidence available; package reconciliation, timing validation, and compliance/certification pending`**; module-side schematic PDF + curated artifact index committed under HW-ASSETS-003 | `timing/compliance-pending` + `needs-package-reconciliation` + `blocked-from-standard-exposure` | `TRI_GPIO1` / `TRI_GPIO2` (Core sheet labels) ↔ `ESP_GPIO1` / `ESP_GPIO2` (module sheet labels) — same wire, two names; placeholder `fan_triac_gate_pin: GPIO5` / `fan_triac_zc_pin: GPIO6` in the Release-One reference product YAML already claimed by RoomIQ J10 (`IO5 = SEN0609_TX`, `IO6 = out(gpio6)`); `ac_dimmer` ISR requires direct interrupt-capable ESP32 GPIOs and explicitly **rejects** SX1509-routed pins; module-side EL814 zero-cross topology + module-side TRIAC drive topology need bench / waveform proof; mains-voltage compliance owed by COMPLIANCE-001 (per [`s360-320-r4-triac.md` Package YAML status](s360-320-r4-triac.md#package-yaml-status)); HW-005 (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` blocker) unresolved. | **No package edit.** HW-005 + HW-PINMAP-320-FOLLOWUP + bench timing evidence + COMPLIANCE-001 advanced/manual-warning sign-off all required. | `HW-PINMAP-320-FOLLOWUP` + `HW-005` unblock + `COMPLIANCE-001` advanced/manual-warning slice → `PACKAGE-TRIAC-001` (alias: `PACKAGE-GAP-001` FanTRIAC slice). Long-term advanced / manual-warning posture in [`s360-320-r4-triac.md` Advanced / manual-warning product posture](s360-320-r4-triac.md#advanced--manual-warning-product-posture); JSON `status: blocked` stays. |
| [`packages/hardware/power_240v.yaml`](../../packages/hardware/power_240v.yaml) | `S360-400` Sense360 240v PSU | `PWR` — logical 240V power package; emits diagnostic sensors (`Supply Voltage`, `Power Source`, `Power Configuration`, `AC Power Connected`); no GPIO binding to module pins | [`s360-400-r4-power.md`](s360-400-r4-power.md) (HW-PINMAP-400) **`pending — schematic/design evidence required`**; module-side schematic not committed | `schematic-evidence-pending` + `needs-package-reconciliation` + `timing/compliance-pending` (compliance-gated) | Catalog `description` says `Mains to 5V using HLK-5M05`; package header-comment says `HLK-PM01 or similar` — part-identity disagreement against [`config/hardware-catalog.json`](../../config/hardware-catalog.json) line 109 + module BOM unknown. Input rating `100-240V AC, 50/60Hz`, output `5V DC, 2A (10W)`, isolation `3000VAC` are package-header text only, **not** schematic-verified (per [`s360-400-r4-power.md` Power / rail mapping status](s360-400-r4-power.md#power--rail-mapping-status)). COMPLIANCE-001 mains-voltage UK / EU sign-off gates any product-side promotion. | **No package edit.** Schematic must arrive (HW-ASSETS-400); compliance review must clear. | `HW-ASSETS-400` → `HW-PINMAP-400-FOLLOWUP` → `COMPLIANCE-001` S360-400 slice → `PACKAGE-POWER-400-001` (alias: `PACKAGE-GAP-001` PWR slice). |
| [`packages/hardware/power_poe.yaml`](../../packages/hardware/power_poe.yaml) | `S360-410` Sense360 PoE PSU | `POE` — logical PoE power package; emits diagnostic sensors (`Supply Voltage`, `Power Source`, `Power Configuration`, `PoE Power Connected`); no GPIO binding; consumed by Release-One under preserved schematic-pending caveat | [`s360-410-r4-poe.md`](s360-410-r4-poe.md) (HW-PINMAP-410) **`pending — schematic/design evidence required`**; module-side schematic not committed | `reference-only` (logical, no GPIO binding) + `schematic-evidence-pending` + `do-not-change-release-one` | Module-side schematic / BOM not committed; PoE module part identity (`Ag9712M`, `Silvertel Ag9700`, `or similar` in package header) and standard / class / input / output ratings not schematic-verified; Core `J2` PoE harness identity is HW-002 Open Question #6 (tracked under [S360-100-BENCH-001](s360-100-r4-core.md#s360-100-bench-001-status), `pending — bench/manufacturing evidence required`). PoE is SELV; **not** in scope for COMPLIANCE-001. Release-One "schematic verification pending" caveat in [`release-one-hardware-audit.md` Findings → PoE PSU](../release-one-hardware-audit.md#findings) is **preserved**. | **No package edit.** The logical role is consumed by Release-One today and may not be changed in PACKAGE-GAP-001. | `HW-ASSETS-410` → `HW-PINMAP-410-FOLLOWUP` → `HW-002 OQ#6` closure / `S360-100-BENCH-001` update → `PACKAGE-POE-410-001` (alias: `PACKAGE-GAP-001` PoE slice). Release-One caveat closure is a separate later PR per [`s360-410-r4-poe.md` Follow-up PRs](s360-410-r4-poe.md#follow-up-prs). |
| [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml) + [`packages/hardware/sense360_core.yaml`](../../packages/hardware/sense360_core.yaml) (Core abstract-bus) | `S360-100` Sense360 Core (abstract-bus substitutions consumed by every fan-driver package) | `relay_pin`, `expansion_gpio1` / `expansion_gpio2`, `halo_i2c`, `expansion_i2c`, `uart_bus`, `status_led_pin`, `pir_sensor_pin` substitutions consumed by Release-One + LED preview + every fan slice | [`firmware-package-mapping-audit.md` Release-One product YAML package stack](firmware-package-mapping-audit.md#release-one-product-yaml-package-stack) (HW-009) `needs-package-change` (systemic; explicit out-of-scope for HW-009) | `do-not-change-release-one` + `needs-package-reconciliation` (systemic; deferred) | Ceiling Core `relay_pin: GPIO4`, `status_led_pin: GPIO48`, `pir_sensor_pin: GPIO47`, `expansion_gpio1/2: GPIO5/6`, `halo_i2c` on `GPIO39/40`, `expansion_i2c` on `GPIO21/18`, `uart_bus` on `GPIO1/2` all disagree with the Core schematic at the connector / net level — enumerated in [`release-one-hardware-audit.md` Summary](../release-one-hardware-audit.md#summary) and owned by Required follow-ups #2 / #3. Resolution feeds into every fan-driver slice. | **No package edit by PACKAGE-GAP-001.** | `CORE-ABSTRACT-BUS-001` (alias: [`release-one-hardware-audit.md` Required follow-ups #2 / #3](../release-one-hardware-audit.md#required-follow-ups)) — must land **before or with** any fan-driver slice that depends on its substitutions. |

The Release-One package stack (`sense360_core_ceiling.yaml`,
`sense360_core_poe.yaml`, `comfort_ceiling.yaml`,
`presence_ceiling.yaml`, `airiq_bathroom_base.yaml`,
`power_poe.yaml`, plus the LED preview's `led_ring_ceiling.yaml`)
carries `do-not-change-release-one` for the purposes of
PACKAGE-GAP-001. Their HW-009 statuses
(`confirmed-ok` / `confirmed-ok with caveat` / `needs-package-change`
systemic) are owned by HW-009 / HW-010 and by
[`release-one-hardware-audit.md` Required follow-ups #2 / #3](../release-one-hardware-audit.md#required-follow-ups);
this matrix does not reclassify them and does not authorise any edit
against them.

## Per-package status

Each subsection below is intentionally short. The schematic-side
evidence, the connector / net-level disagreements, and the exact
file / line citations live in the per-board HW-PINMAP-* audits; the
subsections here only record the package-level verdict and the
named follow-up.

### `fan_relay.yaml` / S360-310

- **Status.** `schematic-evidence-pending` + `needs-package-reconciliation`.
- **What is wrong.** The Core schematic shows `Relay = IO3` at `J4`
  pin 2 (per [`s360-310-r4-relay.md` Pin-map reconciliation status](s360-310-r4-relay.md#pin-map-reconciliation-status)).
  The ceiling Core abstract package binds `relay_pin: GPIO4`; the
  generic Core abstract package binds `relay_pin: GPIO10`. The
  module-side connector pinout, relay-coil drive circuit, and
  harness identity are unknown — no `S360-310-R4` schematic is
  committed.
- **Allowed action now.** None on
  [`fan_relay.yaml`](../../packages/expansions/fan_relay.yaml).
  `fan_relay_pin: ${relay_pin}` inherits whichever value the parent
  Core abstract package binds, and both candidate values disagree
  with the schematic; PACKAGE-GAP-001 cannot resolve which is
  correct.
- **Follow-up owner.** `HW-ASSETS-310` (supplier-side schematic
  delivery) → `HW-PINMAP-310-FOLLOWUP` (standalone schematic-backed
  reference doc + pin-map reconciliation) → `PACKAGE-RELAY-001` /
  `PACKAGE-GAP-001` FanRelay slice. The `IO3` vs `GPIO4` vs `GPIO10`
  resolution belongs to **CORE-ABSTRACT-BUS-001**, not to the
  FanRelay slice itself.
- **Cross-references.** [`s360-310-r4-relay.md` Follow-up PRs](s360-310-r4-relay.md#follow-up-prs);
  [`board-readiness-matrix.md` `S360-310` notes](board-readiness-matrix.md#s360-310-sense360-relay).

### `fan_pwm.yaml` / S360-311

- **Status.** `needs-package-reconciliation` + `bench-evidence-pending`.
- **What is wrong.** [`fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml)
  binds a single `${fan_pwm_pin}` to a direct ESP32 GPIO (resolved
  through the Core abstract package to `GPIO5` on the ceiling
  Core), but the module-side schematic carries four 4-pin fan
  output connectors (`J1` / `J2` / `J4` / `J5`) routed via the
  Core-side `TachPMW1..4` / `Pul_Cou1..4` nets that themselves
  originate at the **SX1509 (U3) I/O bank** on the Core sheet —
  not at the ESP32. The single-channel YAML therefore disagrees
  with the schematic on cardinality (1 vs 4) **and** on
  routing (direct ESP32 vs SX1509). The Core abstract values
  (`GPIO5 = SEN0609_TX`, `GPIO6 = out(gpio6)`) also disagree
  with the Core schematic at the ESP32 side. UART-on-`J3`-pins-11/12
  routing on the module side is unresolved.
  Legacy four-channel [`sense360_fan_pwm.yaml`](../../packages/expansions/sense360_fan_pwm.yaml)
  binds direct ESP32 GPIOs (`GPIO7/8/11/12/13/14/15/16`) that
  also disagree with the schematic; it is consumed only by the
  `legacy-compatible` product
  [`products/sense360-fan-pwm.yaml`](../../products/sense360-fan-pwm.yaml)
  and stays out of any WebFlash-shippable surface.
- **Allowed action now.** None on either FanPWM file. The
  module-side schematic is committed under HW-ASSETS-003 but
  `S360-311` JSON `schematic_status` is still
  `cataloged_unverified`; pin-map reconciliation is owed.
- **Follow-up owner.** `HW-PINMAP-311-FOLLOWUP` (standalone
  schematic-backed reference doc + pin-map reconciliation) +
  `S360-311` `schematic_status` promotion (separate JSON PR) →
  `PACKAGE-PWM-001` / `PACKAGE-GAP-001` FanPWM slice. The single-
  vs four-channel decision, the SX1509-vs-direct-ESP32 decision,
  the PWM polarity / tach pull-up / pulses-per-revolution
  decisions, and the legacy-file fate decision all belong to the
  slice PR. The abstract-bus rebind belongs to
  **CORE-ABSTRACT-BUS-001**.
- **Cross-references.** [`s360-311-r4-pwm.md` Follow-up PR sequence](s360-311-r4-pwm.md#follow-up-pr-sequence);
  [`board-readiness-matrix.md` `S360-311` notes](board-readiness-matrix.md#s360-311-sense360-pwm).

### `fan_gp8403.yaml` / S360-312

- **Status.** `needs-package-reconciliation` + `bench-evidence-pending`.
- **What is wrong.** [`fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)
  header lines 13–18 read `Pin 4 (SDA) → GPIO39`, `Pin 5 (SCL) →
  GPIO40`, `Pin 2 (3.3V) → Power`, `Pin 1 (GND) → Ground`. The
  module `J1` capture is a 6-pin connector with `I2C_SDA` /
  `I2C_SCL` on pins 2 / 3 (not 4 / 5), routed on the Core side
  to ESP32 `IO48` / `IO45` (not `GPIO39` / `GPIO40`) — per
  [`s360-312-r4-dac.md` Header-comment claims vs schematic evidence](s360-312-r4-dac.md#header-comment-claims-vs-schematic-evidence).
  Core `J7` pin-1 is captured as `+5V` and module `J1` pin-1 is
  captured as `+3.3V`; the discrepancy is unresolved. The DIP-
  switch I²C address-selection scheme on the two `GP8403-TC50-EW`
  DACs (`IC1` / `IC2`) is not reflected in the package's allowed
  `${fan_dac_address}` values (`0x58` / `0x59` only). UART-vs-
  Nextion arbitration on Module `J1` pins 4 / 5 (shared with the
  ESP32 boot-log path on `TXD0` / `RXD0`) is unresolved. The
  active YAML body inherits `${fan_dac_i2c_id}` from the Core
  abstract package and does not depend on the stale header-comment
  GPIOs.
- **Allowed action now.** None. `S360-312` JSON `schematic_status`
  is still `cataloged_unverified`; pin-map reconciliation is
  owed. Even the limited "delete the stale header comment block"
  fix is deferred to the slice PR so the change is reviewed
  alongside the address-scheme decision and the UART routing
  decision.
- **Follow-up owner.** `HW-PINMAP-312-FOLLOWUP` (standalone
  schematic-backed reference doc + pin-map reconciliation) +
  `S360-312` `schematic_status` promotion (separate JSON PR) →
  `PACKAGE-DAC-001` / `PACKAGE-GAP-001` FanDAC slice. Subject to
  the `FanDAC` ↔ `AirIQ` mutex in
  [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json).
- **Cross-references.** [`s360-312-r4-dac.md` Follow-up PR sequence](s360-312-r4-dac.md#follow-up-pr-sequence);
  [`board-readiness-matrix.md` `S360-312` notes](board-readiness-matrix.md#s360-312-sense360-dac).

### `fan_triac.yaml` / S360-320

- **Status.** `timing/compliance-pending` + `needs-package-reconciliation` + `blocked-from-standard-exposure`.
- **What is wrong.** [`fan_triac.yaml`](../../packages/expansions/fan_triac.yaml)
  uses `output: ac_dimmer` with `gate_pin: ${fan_triac_gate_pin}`
  and `zero_cross_pin: ${fan_triac_zc_pin}`. Both must be **direct
  interrupt-capable ESP32 GPIOs**; SX1509-routed pins cannot serve
  the ISR timing the driver requires (per
  [`release-one-hardware-audit.md#timing-constraint-ac_dimmer-vs-sx1509-expander`](../release-one-hardware-audit.md#timing-constraint-ac_dimmer-vs-sx1509-expander)
  and [`s360-320-r4-triac.md` Phase-control timing assumption](s360-320-r4-triac.md#mapping-status-and-resolution-table-snapshot)).
  The Release-One reference YAML
  [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml)
  carries `fan_triac_gate_pin: GPIO5` / `fan_triac_zc_pin: GPIO6`
  as parse-only placeholders; both pins are already claimed by
  RoomIQ J10 (`IO5 = SEN0609_TX`, `IO6 = out(gpio6)`). The
  module-side schematic uses `ESP_GPIO1` / `ESP_GPIO2` labels;
  the Core sheet uses `TRI_GPIO1` / `TRI_GPIO2` for the same
  wires. The on-board EL814-based zero-cross topology and the
  on-board TRIAC drive topology are visible on the module
  schematic but need bench / waveform / real-load proof. The
  package retains its **BLOCKED / UNVERIFIED** banner.
- **Allowed action now.** None on
  [`fan_triac.yaml`](../../packages/expansions/fan_triac.yaml).
  The BLOCKED / UNVERIFIED banner stays. The
  `ac_dimmer` topology, the mains-voltage / qualified-electrician
  warnings, the default 50 Hz line frequency, the `method: leading`
  setting, the `init_with_half_cycle: true` setting, and the
  `fan_triac_min_power: "10"` default are **not** changed.
- **Follow-up owner.** `HW-005` unblock (Core re-trace or
  hardware respin) + `HW-PINMAP-320-FOLLOWUP` (standalone
  schematic-backed reference doc + pin-map reconciliation +
  TRIAC-vs-ESP naming reconciliation) + bench timing / waveform /
  real-load evidence + `COMPLIANCE-001` (independent gate; UK / EU
  mains-voltage assessment) → `PACKAGE-TRIAC-001` /
  `PACKAGE-GAP-001` FanTRIAC slice. The advanced / manual-warning
  long-term posture in
  [`s360-320-r4-triac.md` Advanced / manual-warning product posture](s360-320-r4-triac.md#advanced--manual-warning-product-posture)
  is **intent only** today; the JSON lifecycle row
  (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`, `status: blocked`,
  `blocker: HW-005`, `webflash_build_matrix: false`) stays. FanTRIAC
  is **not** Release-One, **not** REQUIRED_CONFIGS, **not** kit /
  default, **not** compliance-certified.
- **Cross-references.** [`s360-320-r4-triac.md` Follow-up PR sequence](s360-320-r4-triac.md#follow-up-pr-sequence);
  [`board-readiness-matrix.md` `S360-320` notes](board-readiness-matrix.md#s360-320-sense360-triac);
  [`release-one-hardware-audit.md#fantriac-mapping-resolution`](../release-one-hardware-audit.md#fantriac-mapping-resolution).
- **PACKAGE-TRIAC-001 investigation outcome.** PACKAGE-TRIAC-001
  was investigated against the readiness gates above and is
  **confirmed deferred**: `HW-005` is unresolved (Core-side
  `TRI_GPIO1` / `TRI_GPIO2` still visible only on the SX1509 side
  of the Core sheet; no direct interrupt-capable ESP32 GPIO trace
  proven end-to-end through `S360-100-R4` + `S360-320`; Option (a)
  unmet; Option (b) eliminated for this revision per the committed
  module-side schematic);
  `HW-PINMAP-320-FOLLOWUP` is outstanding (standalone
  schematic-backed reference doc, `TRI_GPIO*` / `ESP_GPIO*` canonical
  naming, end-to-end pin-map reconciliation, and AC LINE `J1` 3-pin
  function all owed); no bench / waveform / real-load /
  zero-cross / phase-control / thermal evidence on file; and
  `COMPLIANCE-001` advanced / manual-warning sign-off has not landed.
  The package YAML topology itself is **already correct** for the
  state of the evidence (`output: ac_dimmer` on direct
  interrupt-capable ESP32 GPIOs supplied via parent substitutions
  `fan_triac_gate_pin` / `fan_triac_zc_pin`, BLOCKED / UNVERIFIED
  banner, SX1509-rejection clause, mains-voltage /
  qualified-electrician warnings, `method: leading`,
  `init_with_half_cycle: true`, default
  `fan_triac_line_frequency: "50"`, `fan_triac_min_power: "10"`);
  no safe functional package YAML edit exists today. The
  `WF-TRIAC-001` slice has landed in the
  [`sense360store/WebFlash`](https://github.com/sense360store/WebFlash)
  repo as a runtime advanced / manual-warning UX gate, but it does
  **not** satisfy any PACKAGE-TRIAC-001 gate (no direct ESP32 GPIO
  trace evidence, no bench / waveform / real-load evidence, no
  COMPLIANCE-001 sign-off). The investigation outcome and full
  do-not-change inventory are recorded in
  [`docs/cleanup-audit.md` §PACKAGE-TRIAC-001 update](../cleanup-audit.md#package-triac-001-update-deferred--hw-005--hw-pinmap-320-followup--compliance-001-not-landed).
  Status stays `timing/compliance-pending` +
  `needs-package-reconciliation` + `blocked-from-standard-exposure`;
  FanTRIAC remains **not** Release-One, **not** REQUIRED_CONFIGS,
  **not** recommended, **not** kit / default, **not**
  compliance-certified. The JSON lifecycle row
  (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`, `status: blocked`,
  `blocker: HW-005`, `webflash_build_matrix: false`) is unchanged.

### `power_240v.yaml` / S360-400

- **Status.** `schematic-evidence-pending` + `needs-package-reconciliation` + `timing/compliance-pending` (compliance-gated).
- **What is wrong.** [`power_240v.yaml`](../../packages/hardware/power_240v.yaml)
  is a logical-power package with no GPIO binding, but its header
  comment claims `HLK-PM01 or similar` while
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  line 109 records `Mains to 5V using HLK-5M05`. Input rating
  `100-240V AC, 50/60Hz`, output `5V DC, 2A (10W)`, isolation
  `3000VAC`, and the protection / over-current / over-voltage /
  short-circuit claims are package-header text only — not
  schematic-verified for `S360-400-R4` (per
  [`s360-400-r4-power.md` Power / rail mapping status](s360-400-r4-power.md#power--rail-mapping-status)).
  The module-side schematic / mating connector / BOM are not
  committed. COMPLIANCE-001 mains-voltage UK / EU sign-off is a
  separate, additional gate before any `PWR`-bearing product /
  WebFlash work; it cannot be cleared by schematic evidence alone.
- **Allowed action now.** None on
  [`power_240v.yaml`](../../packages/hardware/power_240v.yaml).
  Release-One ships PoE, not `PWR`; the four `legacy-compatible`
  `*-pwr` Core variants stay `legacy-compatible` and stay out of
  the WebFlash build matrix.
- **Follow-up owner.** `HW-ASSETS-400` (supplier-side schematic
  delivery) → `HW-PINMAP-400-FOLLOWUP` (standalone reference doc +
  rail / harness / safety reconciliation) → `COMPLIANCE-001`
  `S360-400` slice (independent track) → `PACKAGE-POWER-400-001` /
  `PACKAGE-GAP-001` PWR slice (header / part-identity / rating
  reconciliation against the now-verified schematic + module BOM).
- **Cross-references.** [`s360-400-r4-power.md` Follow-up PRs](s360-400-r4-power.md#follow-up-prs);
  [`board-readiness-matrix.md` `S360-400` notes](board-readiness-matrix.md#s360-400-sense360-240v-psu);
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md).

### `power_poe.yaml` / S360-410

- **Status.** `reference-only` (logical, no GPIO binding) +
  `schematic-evidence-pending` + `do-not-change-release-one`.
- **What is wrong (or, more accurately, what is unproven).**
  [`power_poe.yaml`](../../packages/hardware/power_poe.yaml) is a
  logical PoE-power package emitting diagnostic sensors only; it
  binds no GPIOs. HW-009 classifies it `confirmed-ok` at the
  abstraction layer. The PoE-module part identity (`Ag9712M` /
  `Silvertel Ag9700` / `or similar`), the IEEE 802.3af / 802.3at
  class assertion, the input range (`36-57V DC`), the output
  rating (`5V DC, 2A (10W)` or `3.3V DC`), and the protection
  claims are package-header text — not schematic-verified for
  `S360-410-R4`. Core `J2` PoE harness identity is HW-002 Open
  Question #6; tracked under
  [S360-100-BENCH-001](s360-100-r4-core.md#s360-100-bench-001-status),
  `pending — bench/manufacturing evidence required`. Release-One
  consumes this package today under the documented
  "schematic verification pending" caveat in
  [`release-one-hardware-audit.md` Findings → PoE PSU](../release-one-hardware-audit.md#findings),
  which is **preserved** here and **not** promoted away. PoE is
  SELV; **not** in scope for COMPLIANCE-001.
- **Allowed action now.** None. The logical role is consumed by
  Release-One; PACKAGE-GAP-001 does not authorise changes to
  Release-One package semantics. Header-text reconciliation is
  deferred to the slice PR after schematic ingest.
- **Follow-up owner.** `HW-ASSETS-410` (supplier-side schematic
  delivery) → `HW-PINMAP-410-FOLLOWUP` (standalone reference doc +
  PoE / rail / connector / harness reconciliation) +
  `HW-002 OQ#6` closure / `S360-100-BENCH-001` update (bench
  evidence) → `PACKAGE-POE-410-001` / `PACKAGE-GAP-001` PoE
  slice → separate later Release-One caveat-closure PR (the
  caveat is **not** closed by this matrix or by the slice PR
  alone).
- **Cross-references.** [`s360-410-r4-poe.md` Follow-up PRs](s360-410-r4-poe.md#follow-up-prs);
  [`board-readiness-matrix.md` `S360-410` notes](board-readiness-matrix.md#s360-410-sense360-poe-psu);
  [`release-one-hardware-audit.md` Findings → PoE PSU](../release-one-hardware-audit.md#findings).

### Core abstract packages (`sense360_core_ceiling.yaml`, `sense360_core.yaml`)

- **Status.** `do-not-change-release-one` + `needs-package-reconciliation` (systemic; deferred).
- **What is wrong.** [`sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml)
  binds `halo_i2c` on `GPIO39 / GPIO40`, `expansion_i2c` on
  `GPIO21 / GPIO18`, `uart_bus` on `GPIO1 / GPIO2`,
  `relay_pin: GPIO4`, `status_led_pin: GPIO48`,
  `pir_sensor_pin: GPIO47`, and `expansion_gpio1 / expansion_gpio2:
  GPIO5 / GPIO6`. The Core schematic disagrees on every one of
  those bindings at the connector / net level (enumerated in
  [`release-one-hardware-audit.md` Summary](../release-one-hardware-audit.md#summary)
  and in [`firmware-package-mapping-audit.md` Release-One product YAML package stack](firmware-package-mapping-audit.md#release-one-product-yaml-package-stack)).
  These abstract-bus values feed into every fan-driver slice —
  FanRelay's `${relay_pin}`, FanPWM's `${fan_pwm_pin}` /
  `${fan_tach_pin}`, FanDAC's `${fan_dac_i2c_id}`,
  FanTRIAC's `${fan_triac_gate_pin}` / `${fan_triac_zc_pin}`.
- **Allowed action now.** None. The Release-One artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` was
  built from this package stack; any change to its semantics
  must clear the full 17-row
  [`docs/preview-to-stable-promotion-gates.md`](../preview-to-stable-promotion-gates.md)
  gate. PACKAGE-GAP-001 does not authorise such changes.
- **Follow-up owner.** `CORE-ABSTRACT-BUS-001` — the named
  alias for
  [`release-one-hardware-audit.md` Required follow-ups #2 / #3](../release-one-hardware-audit.md#required-follow-ups).
  Must land **before or with** any fan-driver slice that depends
  on the substitutions above. The order matters: PACKAGE-RELAY-001
  / PACKAGE-PWM-001 / PACKAGE-DAC-001 / PACKAGE-TRIAC-001 cannot
  land before the abstract-bus values are correct, or else the
  fan-driver slice's "now correct against the schematic" claim
  is conditional on a downstream package rebind it does not
  control.

## Release-One package safety

PACKAGE-GAP-001 **does not change Release-One package behaviour.**
The packages consumed by
[`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq.yaml)
(Release-One stable) and by
[`products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq-led.yaml)
(LED preview) carry `do-not-change-release-one` and are
**explicitly out of scope** for this PR:

- [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml) (Core ceiling abstract; CORE-ABSTRACT-BUS-001).
- [`packages/hardware/sense360_core_poe.yaml`](../../packages/hardware/sense360_core_poe.yaml).
- [`packages/expansions/comfort_ceiling.yaml`](../../packages/expansions/comfort_ceiling.yaml).
- [`packages/expansions/presence_ceiling.yaml`](../../packages/expansions/presence_ceiling.yaml).
- [`packages/expansions/airiq_bathroom_base.yaml`](../../packages/expansions/airiq_bathroom_base.yaml) (legacy filename retained per [`webflash-contract.md`](../webflash-contract.md) §6).
- [`packages/hardware/power_poe.yaml`](../../packages/hardware/power_poe.yaml).
- [`packages/hardware/led_ring_ceiling.yaml`](../../packages/hardware/led_ring_ceiling.yaml) (LED preview only; HW-010 `confirmed-ok` at `led_data_pin: GPIO38`).
- [`packages/features/`](../../packages/features/) feature packages consumed by Release-One and the LED preview.

The recorded Release-One identity stays:

- Config string `Ceiling-POE-VentIQ-RoomIQ`, version `1.0.0`,
  channel `stable`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
  `v1.0.0`.
- LED preview `Ceiling-POE-VentIQ-RoomIQ-LED`, `status: preview`,
  `channel: preview`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`. No
  promotion to `production` / `stable`. No addition to
  REQUIRED_CONFIGS. No kit added.
- FanTRIAC `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`, `status: blocked`,
  `blocker: HW-005`, `webflash_build_matrix: false`. HW-005 is not
  resolved by PACKAGE-GAP-001. COMPLIANCE-001 is not cleared.

## Implementation gates

Each per-package slice PR (`PACKAGE-RELAY-001`, `PACKAGE-PWM-001`,
`PACKAGE-DAC-001`, `PACKAGE-TRIAC-001`, `PACKAGE-POWER-400-001`,
`PACKAGE-POE-410-001`) must clear **all** of its applicable gates
before any package YAML edit is allowed. The gate set per slice is:

| Slice | Schematic ingest | Pin-map / standalone reference doc | JSON `schematic_status` promotion | Bench / silkscreen evidence | Timing / compliance | Core abstract-bus rebind |
|---|---|---|---|---|---|---|
| `PACKAGE-RELAY-001` | `HW-ASSETS-310` | `HW-PINMAP-310-FOLLOWUP` | `S360-310` `schematic_status` promotion (separate JSON PR) | required (silkscreen / harness identity / coil-drive observation) | not applicable | `CORE-ABSTRACT-BUS-001` (paired) |
| `PACKAGE-PWM-001` | done (HW-ASSETS-003) | `HW-PINMAP-311-FOLLOWUP` | `S360-311` `schematic_status` promotion (separate JSON PR) | required (Core `J6` 1-to-13 silkscreen, module `J3` 1-to-13 silkscreen, PWM waveform polarity, tach pull-up identification, four-channel-vs-single-channel decision evidence, UART-on-`J3`-pins-11/12 resolution) | not applicable | `CORE-ABSTRACT-BUS-001` (paired) |
| `PACKAGE-DAC-001` | done (HW-ASSETS-003) | `HW-PINMAP-312-FOLLOWUP` | `S360-312` `schematic_status` promotion (separate JSON PR) | required (Core `J7` vs Module `J1` rail silkscreen, `SW1` / `SW2` DIP-switch I²C address evidence, 5 V / 10 V hardware-select identification, UART0-vs-Nextion arbitration, Cloudlift S12 `J2` / `J3` silkscreen) | not applicable | not strictly required (active YAML inherits `${fan_dac_i2c_id}`); record decision per HW-PINMAP-312-FOLLOWUP |
| `PACKAGE-TRIAC-001` | done (HW-ASSETS-003) | `HW-PINMAP-320-FOLLOWUP` | `S360-320` `schematic_status` promotion (separate JSON PR; after `HW-005` advances) | required (Core `J15` ↔ Module `J3` harness, zero-cross waveform vs `ac_dimmer` ISR expectations, real-load timing, `EL814` characterisation) | **required**: `HW-005` unblock (direct-ESP32 GPIO pair, Option (a) Core re-trace or Core respin) **and** `COMPLIANCE-001` advanced / manual-warning sign-off | not strictly required by routing (FanTRIAC needs direct ESP32 GPIOs, not abstract-bus substitutions); abstract-bus rebind still recommended as a paired clean-up |
| `PACKAGE-POWER-400-001` | `HW-ASSETS-400` | `HW-PINMAP-400-FOLLOWUP` | `S360-400` `schematic_status` promotion (separate JSON PR) | required (mains-input topology, isolation barrier, output regulation, harness identity, BOM cross-check) | **required**: `COMPLIANCE-001` `S360-400` slice closed (UK / EU mains-voltage assessment) before any **product** promotion; the package-header reconciliation itself can proceed once schematic + BOM arrive | not applicable (off-board logical-power package; no GPIO binding) |
| `PACKAGE-POE-410-001` | `HW-ASSETS-410` | `HW-PINMAP-410-FOLLOWUP` | `S360-410` `schematic_status` promotion (separate JSON PR) | required (PoE PD controller identity, magnetics / RJ45 topology, output regulator, harness identity from Core `J2`) | not in scope (PoE is SELV; **not** COMPLIANCE-001) | not applicable (logical-power package) |

A slice that does not have all of its applicable gate cells marked
"done" or "required + supplied" **must not** edit a package YAML.

## Follow-up PR sequence

Each entry below is a separate PR with its own scope, review, and
gate evidence. PACKAGE-GAP-001 does not commit to a calendar and
does not order these beyond the dependencies recorded in
[`docs/hardware/board-readiness-matrix.md` Follow-up PR sequence](board-readiness-matrix.md#follow-up-pr-sequence)
and the per-board audit docs.

| PR | Purpose | Gated on |
|---|---|---|
| **`PACKAGE-RELAY-001`** (alias: `PACKAGE-GAP-001` FanRelay slice) | Reconcile [`packages/expansions/fan_relay.yaml`](../../packages/expansions/fan_relay.yaml) and the Core abstract packages' `relay_pin` value(s) against the now-verified schematic evidence. Decide whether `fan_relay_pin: ${relay_pin}` is the right abstraction or whether the package should bind an explicit module-side connector pin. | `HW-ASSETS-310` + `HW-PINMAP-310-FOLLOWUP` + `S360-310` `schematic_status: verified` + bench / silkscreen evidence + `CORE-ABSTRACT-BUS-001`. |
| **`PACKAGE-PWM-001`** (alias: `PACKAGE-GAP-001` FanPWM slice) | Reconcile [`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml) (and decide the fate of the legacy four-channel [`packages/expansions/sense360_fan_pwm.yaml`](../../packages/expansions/sense360_fan_pwm.yaml)) against the now-verified schematic evidence: single-channel vs four-channel canonical abstraction; SX1509-channel vs direct-ESP32 binding decision; PWM polarity / frequency decision; tach polarity / pull-up / pulses-per-revolution decision; UART-on-`J3`-pins-11/12 resolution. | `HW-PINMAP-311-FOLLOWUP` + `S360-311` `schematic_status: verified` + bench / silkscreen evidence + `CORE-ABSTRACT-BUS-001`. |
| **`PACKAGE-DAC-001`** (alias: `PACKAGE-GAP-001` FanDAC slice) | Reconcile [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) against the now-verified schematic evidence: at minimum delete or correct the stale header-comment connector / GPIO block (file lines 13–18), decide the `${fan_dac_address}` allowed-values set against the DIP-switch evidence, decide whether to add a Nextion `display:` or `uart:` binding on the `UART_RX` / `UART_TX` pair, decide the canonical single- vs dual-channel abstraction (the active YAML is already dual-channel and matches the schematic). | `HW-PINMAP-312-FOLLOWUP` + `S360-312` `schematic_status: verified` + bench / silkscreen / DIP-switch evidence. |
| **`PACKAGE-TRIAC-001`** (alias: `PACKAGE-GAP-001` FanTRIAC slice) | **Investigated and deferred** — readiness gates are not satisfied. Would reconcile [`packages/expansions/fan_triac.yaml`](../../packages/expansions/fan_triac.yaml) against the now-verified schematic + verified direct-ESP32 pin pair: remove the BLOCKED / UNVERIFIED banner **only** if HW-005 and the timing-correctness gate justify it; retain the mains-voltage / qualified-electrician warnings; leave the `ac_dimmer` topology intact (if confirmed correct); add the advanced / manual-warning posture wording per [`s360-320-r4-triac.md` Advanced / manual-warning product posture](s360-320-r4-triac.md#advanced--manual-warning-product-posture). **Must not** add FanTRIAC to Release-One, REQUIRED_CONFIGS, kit / default lists, recommended surfaces, or compliance-certified surfaces. Until the gates clear, the only PACKAGE-TRIAC-001 work recorded in this repo is the docs-only deferral note in [`docs/cleanup-audit.md` §PACKAGE-TRIAC-001 update](../cleanup-audit.md#package-triac-001-update-deferred--hw-005--hw-pinmap-320-followup--compliance-001-not-landed); the package YAML itself is unchanged (BLOCKED / UNVERIFIED banner, `ac_dimmer` topology, substitutions, mains-voltage / qualified-electrician warnings all preserved). `WF-TRIAC-001` having landed in the WebFlash repo (runtime advanced / manual-warning UX gate) does **not** satisfy these package-layer gates. After PACKAGE-TRIAC-001 deferral, the downstream `PRODUCT-TRIAC-002`, in-repo `WF-TRIAC-001` wrapper / catalog / build slice, `RELEASE-TRIAC-001`, and `WF-IMPORT-TRIAC-001` slices remain blocked until `HW-005` + `HW-PINMAP-320-FOLLOWUP` + bench / waveform / real-load evidence + `COMPLIANCE-001` evidence lands; see [`docs/cleanup-audit.md` §TRIAC-QUEUE-001 update](../cleanup-audit.md#triac-queue-001-update-remaining-fantriac-chain-normalized-after-package-deferral). | `HW-005` unblock (Option (a) direct-ESP32 pair or Core respin) + `HW-PINMAP-320-FOLLOWUP` + bench timing / waveform / real-load evidence + `COMPLIANCE-001` advanced/manual-warning sign-off. |
| **`PACKAGE-POWER-400-001`** (alias: `PACKAGE-GAP-001` PWR slice) | Reconcile [`packages/hardware/power_240v.yaml`](../../packages/hardware/power_240v.yaml) header claims (AC-DC part identity `HLK-5M05` vs `HLK-PM01 or similar`, input / output / isolation / protection ratings) against the now-verified schematic and module BOM. | `HW-ASSETS-400` + `HW-PINMAP-400-FOLLOWUP` + `S360-400` `schematic_status: verified` + module BOM cross-check. (Product / WebFlash promotion remains separately gated by `COMPLIANCE-001` `S360-400` slice.) |
| **`PACKAGE-POE-410-001`** (alias: `PACKAGE-GAP-001` PoE slice) | Reconcile [`packages/hardware/power_poe.yaml`](../../packages/hardware/power_poe.yaml) header claims (PoE module part identity, standard / class, input / output / protection ratings) against the now-verified schematic and module BOM. **Does not** by itself close the Release-One "schematic verification pending" caveat in [`release-one-hardware-audit.md` Findings → PoE PSU](../release-one-hardware-audit.md#findings); that closure is a separate later PR per [`s360-410-r4-poe.md` Follow-up PRs](s360-410-r4-poe.md#follow-up-prs). | `HW-ASSETS-410` + `HW-PINMAP-410-FOLLOWUP` + `S360-410` `schematic_status: verified` + `HW-002 OQ#6` closure / `S360-100-BENCH-001` update. |
| **`CORE-ABSTRACT-BUS-001`** (alias for [`release-one-hardware-audit.md` Required follow-ups #2 / #3](../release-one-hardware-audit.md#required-follow-ups)) | Systemic rebind of the Core abstract substitutions (`halo_i2c`, `expansion_i2c`, `uart_bus`, `relay_pin`, `status_led_pin`, `pir_sensor_pin`, `expansion_gpio1` / `expansion_gpio2`) in [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml) and [`packages/hardware/sense360_core.yaml`](../../packages/hardware/sense360_core.yaml) against the verified `S360-100-R4` schematic. Independently drives the resolution of the Core J10 vs RoomIQ J6 pin-order silkscreen check. Must re-validate every non-Release-One product YAML that consumes the Ceiling Core abstract package. | Core J10 vs RoomIQ J6 silkscreen verification (S360-100-BENCH-001 evidence) + RoomIQ / AirIQ / VentIQ package rebind plan + re-validation pass. **Owned by [`release-one-hardware-audit.md` Required follow-ups #2 / #3](../release-one-hardware-audit.md#required-follow-ups), not by PACKAGE-GAP-001.** |

None of these PRs is approved or scoped by PACKAGE-GAP-001 itself.
They are recorded so the matrix has a clear next-action chain.

## Do-not-change guardrails

PACKAGE-GAP-001 — this matrix — performs **none** of the following.
Anyone reading this matrix looking for justification to change one
of them must use a separate, scoped PR with its own gate evidence.

- No edits to any package YAML under
  [`packages/`](../../packages/), including:
  - [`packages/expansions/fan_relay.yaml`](../../packages/expansions/fan_relay.yaml),
    [`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml),
    [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml),
    [`packages/expansions/fan_triac.yaml`](../../packages/expansions/fan_triac.yaml)
    (FanTRIAC retains its BLOCKED / UNVERIFIED banner and all
    mains-voltage warnings);
  - [`packages/hardware/power_240v.yaml`](../../packages/hardware/power_240v.yaml),
    [`packages/hardware/power_poe.yaml`](../../packages/hardware/power_poe.yaml);
  - [`packages/expansions/sense360_fan_pwm.yaml`](../../packages/expansions/sense360_fan_pwm.yaml)
    (legacy four-channel),
    [`packages/expansions/fan_12v_pwm.yaml`](../../packages/expansions/fan_12v_pwm.yaml)
    (legacy alias),
    [`packages/expansions/gpio_expander_sx1509.yaml`](../../packages/expansions/gpio_expander_sx1509.yaml)
    (SX1509 channel map);
  - [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml),
    [`packages/hardware/sense360_core.yaml`](../../packages/hardware/sense360_core.yaml),
    [`packages/hardware/sense360_core_poe.yaml`](../../packages/hardware/sense360_core_poe.yaml),
    and the rest of the Core / RoomIQ / AirIQ / VentIQ / LED
    package family.
- No edits to
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json),
  [`config/product-catalog.json`](../../config/product-catalog.json),
  [`config/webflash-builds.json`](../../config/webflash-builds.json),
  or
  [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json).
  No new JSON fields, status values, channels, lifecycle enums,
  or token reservations.
- No edits to any product YAML under
  [`products/`](../../products/) or any WebFlash wrapper under
  [`products/webflash/`](../../products/webflash/). The
  `fan_triac_gate_pin: GPIO5` / `fan_triac_zc_pin: GPIO6`
  placeholders in
  [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml)
  stay as parse-only placeholders.
- No edits to any workflow under `.github/workflows/`, any script
  under [`scripts/`](../../scripts/), any test under
  [`tests/`](../../tests/), any component under `components/`, or
  any include under `include/`.
- No firmware regenerated; no GitHub Release created or modified;
  no manifest signed; no WebFlash import; no kit added.
- Release-One stays `Ceiling-POE-VentIQ-RoomIQ`, version `1.0.0`,
  channel `stable`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
  `v1.0.0`.
- LED preview entry `Ceiling-POE-VentIQ-RoomIQ-LED` stays
  `status: preview`, `channel: preview`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`. No
  promotion to `production` / `stable`. No addition to
  REQUIRED_CONFIGS. No kit added.
- FanTRIAC stays `status: blocked`, `blocker: HW-005`,
  `webflash_build_matrix: false`. HW-005 is **not** resolved. The
  advanced / manual-warning long-term posture in
  [`s360-320-r4-triac.md` Advanced / manual-warning product posture](s360-320-r4-triac.md#advanced--manual-warning-product-posture)
  is **intent only**; the JSON lifecycle row is unchanged.
- COMPLIANCE-001 mains-voltage UK / EU status for `S360-320`
  (FanTRIAC) and `S360-400` (240v PSU) is unchanged. PoE is SELV
  and is not in scope for COMPLIANCE-001.
- The Core J10 vs RoomIQ J6 pin-order discrepancy
  (`needs-silkscreen/bench-verification` per HW-009) is **not**
  resolved.
- The systemic Core abstract-bus mismatch in
  [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml)
  (CORE-ABSTRACT-BUS-001, owned by
  [`release-one-hardware-audit.md` Required follow-ups #2 / #3](../release-one-hardware-audit.md#required-follow-ups))
  is **not** resolved.
- The `S360-410` PoE PSU schematic-pending caveat in
  [`release-one-hardware-audit.md` Findings → PoE PSU](../release-one-hardware-audit.md#findings)
  is **preserved**, not promoted away.
- The `S360-100` / `S360-300` bench-verification Open Questions
  ([S360-100-BENCH-001](s360-100-r4-core.md#s360-100-bench-001-status),
  [S360-300-BENCH-001](s360-300-r4-led.md#s360-300-bench-001-status))
  remain `pending — bench/manufacturing evidence required` /
  `pending — bench hardware evidence required`.
- No package YAML is marked `confirmed-ok` or
  `ready-for-package-change` by this PR. Every in-scope package
  retains its existing HW-009 / HW-PINMAP-* classification, which
  this matrix consumes verbatim.
- Every `legacy-compatible` product / package entry stays
  `legacy-compatible` and remains out of the WebFlash build
  matrix.
- No entry is added to or removed from WebFlash-side
  `REQUIRED_CONFIGS`, `scripts/data/kits.json`,
  `firmware/sources.json`, or `manifest.json` — those are
  WebFlash-owned and are not touched by this repo.

## Validation

PACKAGE-GAP-001 is documentation only. The relevant invariants
are:

- the existing docs-safe validators continue to pass;
- the diff against code / yaml / json / workflow paths is empty;
- the sanity grep continues to find the expected
  PACKAGE-GAP-001 tokens.

### Test commands

The following are run in this PR; all expected to pass without
modification:

- `python3 tests/test_hardware_catalog.py`
- `python3 tests/test_product_catalog.py`
- `python3 tests/test_product_catalog_consistency.py`
- `python3 tests/validate_webflash_builds.py`
- `python3 tests/test_webflash_compatibility.py`
- `python3 tests/test_webflash_artifact_naming.py`
- `python3 tests/test_validate_webflash_release_notes.py`
- `python3 tests/test_generate_webflash_release_notes.py`
- `python3 tests/test_product_substitutions.py`
- `python3 tests/test_release_one_entity_names.py`
- `python3 tests/validate_configs.py`
- `python3 tests/test_led_package_mapping.py`

No new test is added by this PR. A future per-package slice
(`PACKAGE-RELAY-001` / `PACKAGE-PWM-001` / `PACKAGE-DAC-001` /
`PACKAGE-TRIAC-001` / `PACKAGE-POWER-400-001` /
`PACKAGE-POE-410-001`) may add a structural file-content guard
analogous to
[`tests/test_led_package_mapping.py`](../../tests/test_led_package_mapping.py)
once it edits the corresponding package.

### Diff expectations

`git diff packages config products products/webflash scripts
.github/workflows components include firmware tests` is expected
to be **empty** in this PR — no edits to any of those trees.

### Sanity-grep expectations

`grep -RIn "PACKAGE-GAP-001|ready-for-package-change|needs-package-reconciliation|schematic-evidence-pending|timing/compliance-pending|fan_relay.yaml|fan_pwm.yaml|fan_gp8403.yaml|fan_triac.yaml|S360-310|S360-311|S360-312|S360-320|S360-400|S360-410" docs packages config tests`
is expected to return matches from:

- this new doc
  [`docs/hardware/package-readiness-matrix.md`](package-readiness-matrix.md);
- the per-board audit docs
  [`s360-310-r4-relay.md`](s360-310-r4-relay.md),
  [`s360-311-r4-pwm.md`](s360-311-r4-pwm.md),
  [`s360-312-r4-dac.md`](s360-312-r4-dac.md),
  [`s360-320-r4-triac.md`](s360-320-r4-triac.md),
  [`s360-400-r4-power.md`](s360-400-r4-power.md),
  [`s360-410-r4-poe.md`](s360-410-r4-poe.md);
- the cross-cutting docs
  [`board-readiness-matrix.md`](board-readiness-matrix.md),
  [`firmware-package-mapping-audit.md`](firmware-package-mapping-audit.md),
  [`../product-availability-taxonomy.md`](../product-availability-taxonomy.md),
  [`../release-one-hardware-audit.md`](../release-one-hardware-audit.md),
  [`../cleanup-audit.md`](../cleanup-audit.md);
- the package YAML files themselves (header comments and module
  identity strings); and
- the JSON catalogs in `config/`.

No match outside of those trees is expected.

## See also

- [`docs/hardware/board-readiness-matrix.md`](board-readiness-matrix.md)
  — HW-GAP-001 board-level readiness matrix. Consumes this matrix
  as the source of truth for the `Package YAML status` column on
  each of the six in-scope boards (`S360-310`, `S360-311`,
  `S360-312`, `S360-320`, `S360-400`, `S360-410`). Documentation
  only.
- [`docs/hardware/firmware-package-mapping-audit.md`](firmware-package-mapping-audit.md)
  — HW-009 / HW-010 firmware-package-vs-schematic audit. Source of
  truth for the `confirmed-ok` / `needs-package-change` /
  `needs-doc-fix` / `needs-silkscreen/bench-verification` /
  `blocked` / `unknown` vocabulary this matrix consumes; carries
  the systemic Core abstract-bus mismatch row that
  CORE-ABSTRACT-BUS-001 owns.
- [`docs/hardware/hardware-artifact-policy.md`](hardware-artifact-policy.md)
  — HW-ASSETS-001 hardware artifact policy; defines the per-board
  artifact-index schema and the supplier-delivery follow-up
  pattern that `HW-ASSETS-310` / `HW-ASSETS-400` / `HW-ASSETS-410`
  consume. HW-ASSETS-003 is the precedent for the three boards
  whose schematics are already committed
  (`S360-311` / `S360-312` / `S360-320`).
- [`docs/hardware/remaining-board-documentation-audit.md`](remaining-board-documentation-audit.md)
  — HW-004 / HW-006 / HW-008 per-board documentation-state
  classification. Source of the `documented` /
  `partially-documented` / `cataloged-unverified` / `blocked` /
  `not-needed-for-release-one` vocabulary referenced from the
  per-board audit rows above.
- Per-board pin / package mapping audits —
  [`s360-310-r4-relay.md`](s360-310-r4-relay.md) (HW-PINMAP-310),
  [`s360-311-r4-pwm.md`](s360-311-r4-pwm.md) (HW-PINMAP-311),
  [`s360-312-r4-dac.md`](s360-312-r4-dac.md) (HW-PINMAP-312),
  [`s360-320-r4-triac.md`](s360-320-r4-triac.md) (HW-PINMAP-320),
  [`s360-400-r4-power.md`](s360-400-r4-power.md) (HW-PINMAP-400),
  [`s360-410-r4-poe.md`](s360-410-r4-poe.md) (HW-PINMAP-410). Each
  carries its own evidence inventory, reconciliation flags,
  package-YAML status row, and per-board follow-up PR list. **All
  six are the source of truth for the per-package verdict
  recorded here**; this matrix consolidates the package-level
  outcomes only.
- Curated artifact indexes — [`artifacts/S360-100-R4.md`](artifacts/S360-100-R4.md),
  [`artifacts/S360-311-R4.md`](artifacts/S360-311-R4.md),
  [`artifacts/S360-312-R4.md`](artifacts/S360-312-R4.md),
  [`artifacts/S360-320-R4.md`](artifacts/S360-320-R4.md).
- [`docs/product-availability-taxonomy.md`](../product-availability-taxonomy.md)
  — PRODUCT-AVAIL-001 cross-cutting product availability taxonomy.
  Maps this matrix's `ready-for-package-change` /
  `needs-package-reconciliation` /
  `schematic-evidence-pending` / `bench-evidence-pending` /
  `timing/compliance-pending` / `reference-only` /
  `do-not-change-release-one` /
  `blocked-from-standard-exposure` labels onto the cross-cutting
  `package-yaml-ready` / `package-yaml-pending` rungs without
  changing JSON enums.
- [`docs/release-one-hardware-audit.md`](../release-one-hardware-audit.md)
  — Release-One firmware-vs-schematic audit; source of truth for
  the HW-005 FanTRIAC blocker
  ([§FanTRIAC mapping resolution](../release-one-hardware-audit.md#fantriac-mapping-resolution)),
  the systemic Core abstract-bus rebind (Required follow-ups #2 / #3 =
  CORE-ABSTRACT-BUS-001), and the `S360-410` PoE PSU
  schematic-pending caveat (Findings → PoE PSU).
- [`docs/preview-to-stable-promotion-gates.md`](../preview-to-stable-promotion-gates.md)
  — RELEASE-006 canonical 17-row preview-to-stable promotion
  gate. Applies to any future package-edit that touches a
  preview-channel or stable-channel surface; not bypassed by
  PACKAGE-GAP-001.
- [`docs/product-onboarding.md`](../product-onboarding.md) —
  PRODUCT-004 ordered safe sequence for adding any new product /
  config; any FanRelay / FanPWM / FanDAC / FanTRIAC / PWR product
  that consumes a now-edited package goes through these gates.
- [`docs/webflash-contract.md`](../webflash-contract.md) —
  canonical WebFlash artifact / grammar / token contract; §6
  retains legacy package filenames (including
  `airiq_bathroom_base.yaml`); the fan-driver `max-one-of` rule and
  the `FanDAC` ↔ `AirIQ` mutex bound this matrix's slice-PR
  product policy.
- [`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md)
  — COMPLIANCE-001 mains-voltage UK / EU compliance tracker;
  additional gate for any product / WebFlash work consuming
  `S360-320` (FanTRIAC) or `S360-400` (240v PSU). PoE is SELV and
  is not in scope.
- [`docs/cleanup-audit.md`](../cleanup-audit.md) — classification
  of stale / current / blocked-reference / legacy-compatible repo
  content; carries the PACKAGE-GAP-001 registration row.
- [`docs/product-readiness-matrix.md`](../product-readiness-matrix.md)
  — PRODUCT-GAP-001 product-level readiness gate. Per-candidate-
  product-family verdict (FanRelay / FanPWM / FanDAC / FanTRIAC /
  PWR-240V / PoE-410) that consumes this matrix as the source of
  truth for the `Package readiness` column. Records the per-family
  follow-up PRs (`PRODUCT-RELAY-001` / `PRODUCT-PWM-001` /
  `PRODUCT-DAC-001` / `PRODUCT-TRIAC-001` /
  `PRODUCT-POWER-400-001` / `PRODUCT-POE-410-001`) downstream of
  the per-package slices owned by this matrix, plus the separate
  WebFlash exposure chain (`WEBFLASH-GAP-001` / `RELEASE-GAP-001`
  / `WF-IMPORT-GAP-001`, `WF-TRIAC-001` for the FanTRIAC
  advanced-flow). Documentation only; no product YAML edits.
- [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  — machine-readable hardware catalog. `schematic_status` stays
  `cataloged_unverified` for `S360-310`, `S360-311`, `S360-312`,
  `S360-320`, `S360-400`, `S360-410`. PACKAGE-GAP-001 changes
  none of these values.
- [`config/product-catalog.json`](../../config/product-catalog.json)
  — machine-readable product catalog. Release-One is
  `status: production`; LED preview is `status: preview`;
  FanTRIAC variant is `status: blocked`, `blocker: HW-005`.
- [`config/webflash-builds.json`](../../config/webflash-builds.json)
  — WebFlash build matrix; contains the two existing builds
  (`Ceiling-POE-VentIQ-RoomIQ` stable;
  `Ceiling-POE-VentIQ-RoomIQ-LED` preview) only.
- [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json)
  — WebFlash compatibility taxonomy; preserves the AirIQ ↔ VentIQ
  mutex, the fan-driver `max-one-of` rule, the FanDAC ↔ AirIQ
  mutex, and the reserved tokens for future fan drivers.

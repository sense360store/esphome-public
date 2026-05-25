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
  `partial — schematic evidence available; package reconciliation
  pending` (HW-ASSETS-310 schematic ingest landed at
  [`docs/hardware/artifacts/S360-310-R4.md`](artifacts/S360-310-R4.md)
  + [`schematics/S360-310-R4.pdf`](schematics/S360-310-R4.pdf);
  `HW-PINMAP-310-FOLLOWUP` consumed the schematic and promoted the
  audit status; silkscreen / harness / `K1` BOM / Core abstract-bus
  rebind evidence still owed),
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

The 2026-05-18 HW-005 / HW-PINMAP-320-FOLLOWUP evidence-pass
re-check (see
[`s360-320-r4-triac.md` HW-PINMAP-320-FOLLOWUP audit log](s360-320-r4-triac.md#hw-pinmap-320-followup-audit-log))
confirms no new committed Core direct-ESP32-GPIO trace evidence
(HW-005 Option (a) remains unmet), no on-board controller IC on
`S360-320` (HW-005 Option (b) remains eliminated for this revision
per the committed module-side schematic), no bench / scope /
waveform / real-load / zero-cross / phase-control / thermal / EMI
evidence on a populated `S360-100-R4` + `S360-320-R4` pair, no
KiCad PCB / Gerbers / BOM / board-image evidence for `S360-320-R4`,
no `TRI_GPIO*` / `ESP_GPIO*` canonical-naming choice, no AC LINE
`J1` 3-pin (L / N / PE) function resolution, and no COMPLIANCE-001
mains-voltage UK / EU sign-off has been recorded since HW-PINMAP-320
landed. The
[`fan_triac.yaml`](../../packages/expansions/fan_triac.yaml) row
below stays `timing/compliance-pending` +
`needs-package-reconciliation` + `blocked-from-standard-exposure`
as a result of this re-check; the BLOCKED / UNVERIFIED banner and
the mains-voltage / qualified-electrician warnings in
[`packages/expansions/fan_triac.yaml`](../../packages/expansions/fan_triac.yaml)
are preserved. HW-PINMAP-320 itself remains `partial — schematic
evidence available; package reconciliation, timing validation,
and compliance/certification pending`. The `timing/compliance-pending`,
`needs-package-reconciliation`, and `blocked-from-standard-exposure`
labels keep their current scope for the FanTRIAC row, and the
`PACKAGE-TRIAC-001` follow-up PR chain (`HW-PINMAP-320-FOLLOWUP` +
`HW-005` unblock + `COMPLIANCE-001` advanced / manual-warning
slice → `PACKAGE-TRIAC-001` / `PACKAGE-GAP-001` FanTRIAC slice) is
unchanged.

The 2026-05-18 COMPLIANCE-001 mains-voltage advanced / manual-warning
sign-off evidence-pass re-check (see
[`../compliance/mains-voltage-uk-eu-assessment.md` COMPLIANCE-001 audit log](../compliance/mains-voltage-uk-eu-assessment.md#compliance-001-audit-log))
confirms COMPLIANCE-001 **remains open / not cleared** for
`S360-320` under (i) standard exposure, (ii) a limited advanced /
manual-warning sign-off, and (iii) formal compliance certification.
No qualified-electrician / safety-review sign-off (named party,
review date, observed board serial / batch, covered load types,
installation context, "**this is not compliance certification**"
framing) is on file; no accredited test-lab report, signed
Declaration of Conformity, marking artwork, or production-control
plan exists for any `S360-320`-bearing finished product; no KiCad
PCB / Gerbers / BOM / CPL / drill / STEP / board-image evidence
permitting a creepage / clearance / isolation-coordination /
component-rating review is committed; no fusing / over-current /
surge / thermal-protection analysis is recorded; no `J1` / `J2`
connector voltage / current / wire-range / UL or VDE or TUV or
IEC certification record exists; no enclosure / IP / IK /
flame-rating evidence is on file; no thermal characterisation, no
conducted / radiated EMI capture, no immunity test, no harmonics
/ flicker test, and no UKCA / CE / FCC / UL applicability decision
is recorded. The
[`fan_triac.yaml`](../../packages/expansions/fan_triac.yaml) row
below **does not move** off `timing/compliance-pending` +
`needs-package-reconciliation` + `blocked-from-standard-exposure`
as a result of this re-check; the BLOCKED / UNVERIFIED banner and
the mains-voltage / qualified-electrician warnings remain. The
[`power_240v.yaml`](../../packages/hardware/power_240v.yaml) row
below also does not move off `schematic-evidence-pending` +
`needs-package-reconciliation` + `timing/compliance-pending`. The
`PACKAGE-TRIAC-001` follow-up PR chain stays unchanged; the
`PACKAGE-POWER-400-001` follow-up PR chain (`HW-ASSETS-400` →
`HW-PINMAP-400-FOLLOWUP` → `COMPLIANCE-001` `S360-400` slice →
`PACKAGE-POWER-400-001`) also stays unchanged. The advanced /
manual-warning long-term product posture per
[`s360-320-r4-triac.md` Advanced / manual-warning product posture](s360-320-r4-triac.md#advanced--manual-warning-product-posture)
stays **intent only**.

The 2026-05-18 HW-PINMAP-311-FOLLOWUP evidence-pass re-check (see
[`s360-311-r4-pwm.md` HW-PINMAP-311-FOLLOWUP audit log](s360-311-r4-pwm.md#hw-pinmap-311-followup-audit-log))
confirms no new committed silkscreen evidence for the Core-side
`J6` 1-to-13 pin order or the parallel module-side `J3` 1-to-13
pin order, no physical 13-pin Core ↔ module harness inspection,
no bench / scope / waveform / pulses-per-revolution evidence for
the per-fan PWM (`TachPMW*`) / tach (`Pul_Cou*`) / shared
open-drain (`TachIO`) paths, no UART-on-`J3`-pins-11/12 routing
resolution, no PWM polarity / tach pull-up identification, no
single-channel vs four-channel canonical-abstraction decision
against the FanPWM token, no `"NINE 4pin FANs"`
section-title documentation resolution, no KiCad schematic source
/ KiCad PCB source / KiCad project metadata / BOM / CPL / Gerber
/ drill / STEP / board-image evidence for `S360-311-R4`, and no
progress on `CORE-ABSTRACT-BUS-001` (alias for
[`release-one-hardware-audit.md` Required follow-ups #2 / #3](../release-one-hardware-audit.md#required-follow-ups))
since HW-PINMAP-311 landed. The
[`fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml) row
below stays `needs-package-reconciliation` +
`bench-evidence-pending` as a result of this re-check; the
single-channel `${fan_pwm_pin}` / `${fan_tach_pin}` binding, the
`fan_pwm_frequency: "25000"`, the `multiply: 0.5` pulses-per-revolution
factor, and the parent-Core substitution comment block are all
preserved. The legacy four-channel
[`sense360_fan_pwm.yaml`](../../packages/expansions/sense360_fan_pwm.yaml)
stays `legacy-compatible`-only — consumed solely by
[`products/sense360-fan-pwm.yaml`](../../products/sense360-fan-pwm.yaml)
(pre-WebFlash standalone fan board; not WebFlash-shippable);
the direct ESP32 GPIO bindings (`GPIO7` / `GPIO11` / `GPIO13` /
`GPIO15` PWM; `GPIO8` / `GPIO12` / `GPIO14` / `GPIO16` tach;
`GPIO6` shared `tach_io_pin`; `GPIO43` / `GPIO44` Nextion UART)
remain in place. HW-PINMAP-311 itself remains `partial —
schematic evidence available; package reconciliation pending`.
The `needs-package-reconciliation` and `bench-evidence-pending`
labels keep their current scope for the FanPWM row, and the
`PACKAGE-PWM-001` follow-up PR chain (`HW-PINMAP-311-FOLLOWUP` →
`S360-311 schematic_status` promotion (separate JSON PR) →
`PACKAGE-PWM-001` paired with `CORE-ABSTRACT-BUS-001`) is
unchanged.

`PACKAGE-PWM-TACH-STRATEGY-001` (2026-05-25) records the operator
tach/RPM decision (see
[`s360-311-r4-pwm.md` §Tach / RPM strategy](s360-311-r4-pwm.md#tach--rpm-strategy-package-pwm-tach-strategy-001)):
the `PACKAGE-PWM-001` chain now targets a **PWM-drive-only first
package** (four PWM outputs, no per-fan RPM sensors, optional
diagnostic binary tach states only, `TachIO`/`GPIO16`
reserved/pending), with per-fan RPM deferred to future work. This
is a scope decision only; the FanPWM row stays
`needs-package-reconciliation` + `bench-evidence-pending` and the
package is **not yet implemented**.

`PWM-SX1509-TACH-PROOF-001` (2026-05-25) upgrades the premise of
that decision from an inferred claim to a compile/config proof.
**SX1509 PWM-drive output IS supported** (`output: platform:
sx1509`) and stays the basis of FanPWM drive; SX1509 GPIO/binary
input is supported too. **Only the per-fan RPM path — an SX1509
expander pin used as an ESPHome `pulse_counter` — is compile-proven
unsupported by ESPHome validation.** The minimal fixture
[`tests/esphome/sx1509_pulse_counter_proof.yaml`](../../tests/esphome/sx1509_pulse_counter_proof.yaml)
is rejected by `esphome config` (ESPHome 2026.5.1, exit code 2)
with `[sx1509] is an invalid option for [pin]`; two control checks
in
[`tests/test_sx1509_tach_pulse_counter_proof.py`](../../tests/test_sx1509_tach_pulse_counter_proof.py)
confirm the rejection is `pulse_counter`+SX1509-specific (the same
SX1509 pin validates as a `binary_sensor: gpio`, and
`pulse_counter` validates on a native ESP32 GPIO). The proof
**confirms** the PWM-drive-only-first strategy; it does not revise
it. The wording is now "compile-proven unsupported by ESPHome
validation", not "unsupported online".

The 2026-05-22 `PACKAGE-DAC-001-READINESS-REFRESH` pass (see
[`s360-312-r4-fandac.md` PACKAGE-DAC-001 readiness refresh](s360-312-r4-fandac.md#package-dac-001-readiness-refresh))
re-evaluated the 10 FanDAC-specific blockers enumerated in
[`s360-312-r4-fandac.md` Blockers remaining for PACKAGE-DAC-001](s360-312-r4-fandac.md#blockers-remaining-for-package-dac-001)
after `CORE-ABSTRACT-BUS-001B-IMPLEMENT-001` (PR #569) and
`HW-PINMAP-312-FOLLOWUP` (PR #570) both landed on 2026-05-22.
Rows 1 (shared-I²C-bus naming) and 2 (GP8403 BOM identity) are
**resolved**; rows 5 (firmware/register-driven range mechanism) and
7 (per-channel range mixing on a single GP8403 is **not** a hardware
capability) are **evidence-captured**; row 9 (Nextion / UART0
arbitration) is **out of `PACKAGE-DAC-001` scope** and deferred to a
future product slice. Rows 3 (DIP-switch ↔ I²C address truth table),
6 (output-range policy decision), 8 (`J2` / `J3` silkscreen +
harness), and 10 (package YAML correctness) **still block**: row 3
needs a GP8403 datasheet excerpt or a bench logic-analyser scan; row
6 needs a recorded product / package design decision on
chip-level vs per-chip range exposure; row 8 needs an
operator-attested silkscreen reading + harness conductor trace; row
10 is implementation-pending and gated on rows 3, 6, and 8. The
refresh records the verdict that `PACKAGE-DAC-001` is **not
implementation-plannable yet** and recommends a DAC address /
range / silkscreen evidence PR (provisionally named
`HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001`) as the next step —
**not** `PACKAGE-DAC-001-IMPLEMENT-001`. The
[`fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) row
below stays `needs-package-reconciliation` +
`bench-evidence-pending`; the row notes and the
§[`fan_gp8403.yaml` / S360-312](#fan_gp8403yaml--s360-312) detail
block are refreshed by this PR to cite the readiness refresh
section and to enumerate the four rows that still block. The
package YAML body is byte-identical
(`${fan_dac_i2c_id}` default `core_i2c`, `${fan_dac_address}`
default `0x58` / alternate `0x59`, `${fan_dac_voltage_mode}`
default `10V` / alternate `5V`, two `output.platform: gp8403`
channels 0 and 1, two `fan.platform: speed` entities,
per-channel template sensors / voltage calculations,
fan-control scripts, link-mode / auto-mode globals all
preserved); the FanDAC alias
[`packages/expansions/fan_dac.yaml`](../../packages/expansions/fan_dac.yaml)
is also byte-identical. `S360-312` JSON `schematic_status` stays
`cataloged_unverified`; `schematic_file` stays unset. Release-One,
LED preview, FanTRIAC, `FanDAC` ↔ `AirIQ` mutex, fan-driver
`max-one-of` rule are unchanged. WebFlash repository
(`sense360store/WebFlash`) is untouched.

The 2026-05-22 `HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001` pass (see
[`s360-312-r4-fandac.md` §2026-05-22 — HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001](s360-312-r4-fandac.md#2026-05-22--hw-pinmap-312-followup-dac-evidence-001))
closed the rows that PR #571 left blocking, using the GP8403 public
datasheet and the `Fan_GP8403` (S360-312-R4) Google Drive layout
assets (KiCad PCB source, gerbers, board renders), plus the operator
design decisions. **Row 3 (DIP-switch ↔ I²C-address truth table) is
CLOSED** — the GP8403 datasheet fixes `A0`/`A1`/`A2` as address bits
0/1/2 with base `0x58` (span `0x58`–`0x5F`), and the KiCad PCB maps
`SW1`→`A0`/`A1`/`A2` and `SW2`→`2A0`/`2A1`/`2A2` (opposite pole side
to `GND`; closed = 0, open = 1 via the 4.7 kΩ pull-ups), giving a full
DIP-position → 7-bit-address truth table. **Row 6 (output-range
policy) is CLOSED** — operator decision: per-DAC-chip range, both
chips default 0–10 V, independent `IC1`/`IC2` override; the datasheet
confirms range is register-`0x01`, chip-level (`0x00`→0–5 V,
`0x11`→0–10 V), not per-output and not hardware-jumper. **Row 8
(`J2` / `J3` silkscreen + pin-1 identity) is board-level CLOSED** —
the PCB + bottom-silkscreen render show both connectors wire **pin 1 =
`VOUT0`, pin 2 = `GND` (middle), pin 3 = `VOUT1`**; `J2` silk
(`out0`/`gnd`/`out1`) matches the `IC1` channels, while **`J3` silk
`out0`/`out1` is transposed** relative to the `IC2` channel nets (pin 1
silk `out1` carries net `2vout0`). With rows 3, 6, and 8 closed, the
refresh records the verdict that **`PACKAGE-DAC-001` is now
implementation-plannable**; the recommended next PR is
**`PACKAGE-DAC-001-IMPLEMENT-001`** (bind two GP8403 devices with
per-chip `${fan_dac_address}` / `${fan_dac_address_2}` and
`${fan_dac_voltage_mode}` / `${fan_dac_voltage_mode_2}` substitutions;
four outputs; correct the stale line-6 jumper comment). Residual
**product / bench** items remain but do **not** block the package YAML:
the harness conductor trace from `J2` / `J3` to the physical Cloudlift
S12 fan input (no fan / harness artifact exists in Drive); an operator
/ bench confirmation of the `J3` `out0`/`out1` silkscreen transposition;
the as-shipped factory DIP positions; and the Module `J1` / Core `J7`
`+3.3 V` / `+5 V` rail discrepancy (`S360-100-BENCH-001`). This pass is
**docs / evidence only** — no edit to
[`fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) or
[`fan_dac.yaml`](../../packages/expansions/fan_dac.yaml) (both
byte-identical), no product / WebFlash / config / firmware / scripts /
workflows / components / include / tests edit, no
`webflash_build_matrix` flip, no `artifact_name`, no compile-only
target, no per-output range-mix claim, no DAC product / WebFlash /
release readiness claim, no `schematic_status` / `schematic_file`
promotion (`S360-312` stays `cataloged_unverified`). The KiCad / gerber
/ image binaries stay retained-but-not-committed per the artifact
policy. WebFlash repository (`sense360store/WebFlash`) is untouched.

The 2026-05-22 HW-PINMAP-312-FOLLOWUP evidence-consolidation pass
(see [`s360-312-r4-fandac.md` HW-PINMAP-312-FOLLOWUP audit log](s360-312-r4-fandac.md#hw-pinmap-312-followup-audit-log))
landed a new standalone per-board schematic+BOM reference doc at
[`docs/hardware/s360-312-r4-fandac.md`](s360-312-r4-fandac.md)
after the user supplied the same module-side schematic PDF
(byte-identical to the already-committed schematic; SHA256
`2888f626bfa0139d2190f154f9b02ecf4cb06f2522a5b5802eaf96e16de39e28`)
plus a previously-not-recorded `Fan_GP8403.xlsx` BOM spreadsheet
(SHA256
`1886ecad5b9dd1a683b8c0ccebb770e5c02894854650b5a5553b19875f7e3a20`;
12,744 bytes; 19 rows). The new doc consolidates schematic +
BOM evidence: confirms `IC1` / `IC2` as `GP8403-TC50-EW` (Guestgood),
`U1` as `MT3608`, `J1` as 6-pin JST SH (`SM06B-SRSS-TB`), `J2` / `J3`
as 3-pin Phoenix-compatible terminal blocks (`MX350-3.5-03P-GN01-Cu-Y-A`),
`J7` as 4-pin JST PH (`B4B-PH-K-S`), `SW1` / `SW2` as 3-pole SPST DIP
switches (`219-3MSTR` from CTS), the six `4.7 kΩ` GP8403 address
pull-ups (`R3` / `R5` / `R7` for `IC1` `A0` / `A1` / `A2`;
`R4` / `R6` / `R8` for `IC2` `2A0` / `2A1` / `2A2`); records that
the BOM contains **no** 5 V / 10 V range-select jumper / solder
bridge — output range is therefore firmware/register-driven only
(the schematic ties each chip's `V5V` pin directly to `+12V` from
the MT3608 boost output); records that the BOM contains **no** 5 V
regulator, so the Nextion `J7` pin 1 `+5V` is an expected external
supply not a board-generated rail; records that simultaneous
one-channel-0–5 V plus one-channel-0–10 V on a **single** GP8403
is **not** a hardware capability of this board (one `V5V` reference
per chip), so per-channel range mixing is only achievable across
the two DACs. The new doc explicitly captures the post-PR-#569
state — `${fan_dac_i2c_id}` default `core_i2c` resolves to the
single shared bus on `GPIO48` / `GPIO45` — and re-confirms that
`PACKAGE-DAC-001` is **no longer blocked at the shared-I²C-bus-
naming layer** but **stays blocked** on the 10 enumerated
FanDAC-specific items in
[`s360-312-r4-fandac.md` Blockers remaining for PACKAGE-DAC-001](s360-312-r4-fandac.md#blockers-remaining-for-package-dac-001).
The
[`fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) row
below stays `needs-package-reconciliation` +
`bench-evidence-pending`; the YAML body is byte-identical
(`${fan_dac_i2c_id}` default `core_i2c`,
`${fan_dac_address}` default `0x58` / alternate `0x59`,
`${fan_dac_voltage_mode}` default `10V` / alternate `5V`, two
`output.platform: gp8403` channels, two `fan.platform: speed`
entities, per-channel template sensors / voltage calculations,
fan-control scripts, link-mode / auto-mode globals all preserved);
the FanDAC alias [`packages/expansions/fan_dac.yaml`](../../packages/expansions/fan_dac.yaml)
is also byte-identical. `S360-312` JSON `schematic_status` stays
`cataloged_unverified`; `schematic_file` stays unset. Release-One,
LED preview, FanTRIAC, `FanDAC` ↔ `AirIQ` mutex, fan-driver
`max-one-of` rule are unchanged. WebFlash repository
(`sense360store/WebFlash`) is untouched.

The 2026-05-18 HW-PINMAP-312-FOLLOWUP evidence-pass re-check (see
[`s360-312-r4-dac.md` HW-PINMAP-312-FOLLOWUP audit log](s360-312-r4-dac.md#hw-pinmap-312-followup-audit-log))
confirms no new committed silkscreen evidence for the Core-side
`J7` 1-to-6 pin order or the parallel module-side `J1` 1-to-6
pin order (particularly the pin-1 rail value `+5V` vs `+3.3V`),
no physical 6-pin Core ↔ module harness inspection, no
silkscreen reading of the module-side `J2` / `J3` Cloudlift S12
output connector pin-1 location, no bench / scope / I²C /
waveform / Cloudlift-functional capture of the GP8403 DAC
outputs at `J2` / `J3`, the shared I²C bus exchange to `IC1` /
`IC2`, the `vout0` / `vout1` analog rail behaviour at the
configured `${fan_dac_voltage_mode}`, or the Cloudlift S12
functional response, no DIP-switch I²C address-selection
measurement on `SW1` / `SW2` (the schematic shows the hardware
via 4.7 kΩ pull-ups `R3` / `R5` / `R7` for `IC1` `A0` / `A1` /
`A2` and `R4` / `R6` / `R8` for `IC2` `2A0` / `2A1` / `2A2`,
but not the DIP-position-to-address mapping;
[`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)
still exposes only `0x58` / `0x59` and addresses `IC1` only),
no `fan_dac_voltage_mode` 5 V vs 10 V hardware-select
identification (jumper / solder-bridge / DIP position), no
UART0-vs-Nextion arbitration evidence (Module `J1` pins 4 / 5
carry `UART_RX` / `UART_TX` on-board to Module `J7` Nextion
connector; Core ties same nets to ESP32 `TXD0` / `RXD0` = UART0
= boot-log path on USB per
[`s360-100-r4-core.md` §UART buses](s360-100-r4-core.md#uart-buses)
line 349), no resolution of the stale header-comment block in
[`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)
lines 13–18 (`Pin 4 (SDA) → GPIO39`, `Pin 5 (SCL) → GPIO40`,
`Pin 2 (3.3V) → Power`, `Pin 1 (GND) → Ground` — disagrees with
both Module `J1` and Core `J7` schematics and with the Core
I²C bus identity `IO48` / `IO45`; active YAML body is unaffected
because `${fan_dac_i2c_id}` uses abstract-bus inheritance, but
the comment is uncorrected), no KiCad schematic source / KiCad
PCB source / KiCad project metadata / BOM / CPL / Gerber /
drill / STEP / board-image evidence for `S360-312-R4`, and no
progress on `CORE-ABSTRACT-BUS-001` (alias for
[`release-one-hardware-audit.md` Required follow-ups #2 / #3](../release-one-hardware-audit.md#required-follow-ups))
since HW-PINMAP-312 landed. The
[`fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)
row below stays `needs-package-reconciliation` +
`bench-evidence-pending` as a result of this re-check; the
dual-channel YAML body (two `output.platform: gp8403` channels
0 / 1, two `fan.platform: speed` entities with
`speed_count: 100`, `${fan_dac_i2c_id}` default `i2c0`,
`${fan_dac_address}` default `0x58` / alternate `0x59`,
`${fan_dac_voltage_mode}` default `10V` / alternate `5V`),
the per-channel template sensors / voltage calculations, the
fan-control scripts, and the link-mode / auto-mode globals are
all preserved. HW-PINMAP-312 itself remains `partial — schematic
evidence available; package reconciliation pending`. The
`needs-package-reconciliation` and `bench-evidence-pending`
labels keep their current scope for the FanDAC row, and the
`PACKAGE-DAC-001` follow-up PR chain (`HW-PINMAP-312-FOLLOWUP` →
`S360-312 schematic_status` promotion (separate JSON PR) →
`PACKAGE-DAC-001`) is unchanged. The explicit `FanDAC` ↔ `AirIQ`
mutex
([`config/webflash-compatibility.json`](../../config/webflash-compatibility.json)
`rules.fandac_conflicts_with_airiq: true` line 30) and the
fan-driver `max-one-of` rule (`FAN_DRIVER_TOKENS` in
[`tests/validate_webflash_builds.py`](../../tests/validate_webflash_builds.py)
line 37) are unchanged.

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
| [`packages/expansions/fan_relay.yaml`](../../packages/expansions/fan_relay.yaml) | `S360-310` Sense360 Relay | `FanRelay` — single on/off relay-driven fan via `${fan_relay_pin}` defaulting to `${relay_pin}` | [`s360-310-r4-relay.md`](s360-310-r4-relay.md) (HW-PINMAP-310) **`partial — schematic evidence available; package reconciliation pending`** (audit status promoted by HW-PINMAP-310-FOLLOWUP); module-side schematic PDF + curated artifact index committed under HW-ASSETS-310 at [`docs/hardware/artifacts/S360-310-R4.md`](artifacts/S360-310-R4.md) + [`schematics/S360-310-R4.pdf`](schematics/S360-310-R4.pdf); evidence-capture **checklist** recorded under `S360-310-BENCH-001` at [`s360-310-r4-relay.md` §S360-310-BENCH-001 — Relay bench evidence](s360-310-r4-relay.md#s360-310-bench-001--relay-bench-evidence) **and populated by `S360-310-BENCH-EVIDENCE-001` (2026-05-22)** from operator-attested + BOM-backed + public-reference-backed sources (all ten enumerated hardware-evidence rows now carry captured values; no photo / video / oscilloscope / continuity-meter artifacts attached; operator-uploaded `S360-310-R4_BOM.xlsx` consumed for `K1` BOM-backed row but not committed to this repository); pin-pinning regression for the FanRelay package itself landed in `PACKAGE-RELAY-001` at [`tests/test_fan_relay_package.py`](../../tests/test_fan_relay_package.py) | `package-implemented` + `reconciled-at-package-layer` (substitution-layer blockers resolved by 001A / 001C, PR #557 + PR #558; hardware-evidence blockers populated by `S360-310-BENCH-EVIDENCE-001` from operator-attested + BOM-backed + public-reference-backed sources; package abstraction pinned by `PACKAGE-RELAY-001` test scaffold; product / WebFlash / release / compliance / mains-safety gates stay separately blocked — see [§`fan_relay.yaml` / S360-310](#fan_relayyaml--s360-310)) | **Substitution-layer blockers resolved by 001A / 001C (PR #557 + PR #558, 2026-05-21).** Pre-001A the Core abstract packages bound `relay_pin: GPIO4` (ceiling Core) / `GPIO10` (generic Core), neither matching the Core schematic `Relay = IO3`; the schematic-correct `relay_pin: GPIO3` also collided with `comfort_ceiling_als_int_pin: GPIO3` (Release-One via [`comfort_ceiling.yaml`](../../packages/expansions/comfort_ceiling.yaml)), `expander_int_pin: GPIO3` ([`sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml)), and `sx1509_interrupt_pin: GPIO3` ([`gpio_expander_sx1509.yaml`](../../packages/expansions/gpio_expander_sx1509.yaml)). Post-001C / 001A the five non-voice Core abstract packages bind `relay_pin: GPIO3`; ALS_INT is on `GPIO47`; the expander interrupt is on `GPIO17`; [`tests/test_core_abstract_bus.py`](../../tests/test_core_abstract_bus.py) `RelayPinRebindTests` / `MainRelaySwitchBindingTests` / `NoSubstitutionCollisionTests` pin the rebind. Module schematic confirms `J2` 3-pin "From Core" net order (`+5V` / `Relay` / `GND`) matches Core `J4`, and that the `Relay` net drives a `Q1` MMBT3904 NPN low-side switch (`R1` 1 kΩ base / `R2` 10 kΩ pull-down / `D1` flyback) into a `K1` mechanical relay. **Hardware-evidence blockers still owed (now enumerated as a `S360-310-BENCH-001` checklist with ten rows, every row `pending — bench evidence required`)**: S360-100 Core `J4` silkscreen / pin-1 orientation (gated on `S360-100-BENCH-001`); S360-310 Relay `J2` 1-to-3 pin order; S360-310 Relay `J1` `NO` / `COM` / `NC` mapping; Core `J4` ↔ Relay `J2` harness identity (straight-through or keyed); `K1` BOM identity / manufacturer / part number; `K1` contact-current rating; expected controlled load type; relay boot state with `S360-100-R4` + `S360-310-R4` attached; ESP32-S3 `GPIO3` strap-pin boot characterisation generalisation status (the operator-confirmed pair-scoped boot OK in [`docs/hardware/core-abstract-bus-001c-rebind-plan.md`](core-abstract-bus-001c-rebind-plan.md) decisions #16 / #17 is **pair-scoped**, not generic); Relay load / contact proof. | **Hardware-evidence blockers populated by `S360-310-BENCH-EVIDENCE-001` (2026-05-22)** from operator-attested (Core `J4` pin order `+5V` / `Relay` / `GND`; Relay `J2` pin order `+5V` / `Relay` / `GND`; Relay `J1` mapping `NO` / `COM` / `NC`; straight-through 3-pin harness with J4-N↔J2-N identity; expected controlled load type UK mains Manrose `MT100S`-class extractor fan; relay boot state de-energized across 10 cycles × 4 power paths with firmware `Ceiling-POE-VentIQ-RoomIQ`; load / contact behaviour consistent with `NO` + `COM` wiring) + BOM-backed (`K1` Songle `SRD-05VDC-SL-C` from operator-uploaded `S360-310-R4_BOM.xlsx`, not committed) + public-reference-backed (`K1` contact-current rating `10 A @ 250 VAC; 10 A @ 30 VDC` from SRD-style relay reference) + operator-framed pair-scoped sufficient for package implementation (`GPIO3` strap-pin boot behaviour on the populated `S360-100-R4` + `S360-310-R4` pair). | **`PACKAGE-RELAY-001` is implemented / reconciled at the package layer (this PR).** `fan_relay.yaml` remains structurally correct and **unchanged**: `fan_relay_pin: ${relay_pin}` line 27 resolves to the schematic-correct `GPIO3` automatically post-001A. The reconciliation is the addition of [`tests/test_fan_relay_package.py`](../../tests/test_fan_relay_package.py) which pins the FanRelay package abstraction against future regression (package parses as YAML; `fan_relay_pin` defaults to `${relay_pin}`; no GPIO is hard-coded; `fan_relay_switch` binds `pin: ${fan_relay_pin}`; non-voice Core packages bind `relay_pin: GPIO3`; voice variants stay at the pre-001A `relay_pin: GPIO4`; no FanRelay product YAML or WebFlash-builds entry was added). "Reconciled at the `PACKAGE-RELAY-001` package layer" does **not** mean: product-ready; WebFlash-ready; release-ready; compliance-cleared; safe for arbitrary mains installation; or verified across production batches. `PRODUCT-RELAY-001` is the next Relay-chain PR and stays separately gated on its own evidence. | `HW-ASSETS-310` *(landed)* → `HW-PINMAP-310-FOLLOWUP` *(landed)* → `CORE-ABSTRACT-BUS-001` docs-only audit *(landed)* → `CORE-ABSTRACT-BUS-001C` *(landed PR #557 — ALS_INT / PIR / UART / status / expansion GPIO rebind; freed `GPIO3`)* → `CORE-ABSTRACT-BUS-001A` *(landed PR #558 — `relay_pin → GPIO3` rebound + pin-pinning regression scaffold)* → `PACKAGE-RELAY-001-READINESS-REFRESH` *(landed PR #559 — docs/evidence/readiness only)* → `S360-310-BENCH-001` *(landed PR #560 — evidence-capture **checklist** added)* → `S360-310-BENCH-EVIDENCE-001` *(landed PR #561 — evidence-population only; ten rows captured)* → **`PACKAGE-RELAY-001`** *(this PR — test + readiness reconciliation; no YAML rebind; added `tests/test_fan_relay_package.py`; package status moves to `package-implemented` + `reconciled-at-package-layer`)* → `PRODUCT-RELAY-001` (alias: `PRODUCT-GAP-001` FanRelay slice). |
| [`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml) | `S360-311` Sense360 PWM | `FanPWM` — single-channel 25 kHz PWM fan + `pulse_counter` tach via `${fan_pwm_pin}` / `${fan_tach_pin}` | [`s360-311-r4-pwm.md`](s360-311-r4-pwm.md) (HW-PINMAP-311) **`partial — schematic evidence available; package reconciliation pending`**; module-side schematic PDF + curated artifact index committed under HW-ASSETS-003 | `needs-package-reconciliation` + `bench-evidence-pending` | SX1509-channel (`TachPMW1..4`, `Pul_Cou1..4`) vs direct-ESP32-GPIO mismatch (Core abstract `expansion_gpio1/2` resolves to `GPIO5 = SEN0609_TX` / `GPIO6 = out(gpio6)`); UART-on-`J3`-pins-11/12 routing; single-channel YAML vs four 4-pin fan output connectors on the module; PWM polarity, tach pull-up, `"NINE 4pin FANs"` documentation question (per [`s360-311-r4-pwm.md` Reconciliation flags](s360-311-r4-pwm.md#reconciliation-flags-raised-or-strengthened-by-this-schematic) and [§Existing package abstraction](s360-311-r4-pwm.md#existing-package-abstraction)). `S360-311` JSON `schematic_status` stays `cataloged_unverified`. Sibling [`packages/expansions/sense360_fan_pwm.yaml`](../../packages/expansions/sense360_fan_pwm.yaml) (legacy four-channel; direct ESP32 GPIOs) is consumed only by the legacy-compatible product [`products/sense360-fan-pwm.yaml`](../../products/sense360-fan-pwm.yaml) and stays out of any WebFlash-shippable surface. | **No edit to `fan_pwm.yaml`.** HW-PINMAP-311-FOLLOWUP must close first. The neutral SX1509 binding prerequisite is now provided separately (see next cell), but it does **not** unblock this single-channel package. | `CORE-ABSTRACT-BUS-SX1509-001` *(landed — added the neutral binding-only [`packages/expansions/fan_pwm_sx1509.yaml`](../../packages/expansions/fan_pwm_sx1509.yaml): SX1509 hub on `core_i2c`; four PWM-drive outputs `fan_pwm_drive_1..4` → channels 0..3; four tach inputs `fan_pwm_tach_1..4` → channels 4..7; `tach_io_pin: GPIO16` for the direct line; pinned by [`tests/test_core_abstract_bus.py`](../../tests/test_core_abstract_bus.py) `FanPwm*` classes; **no** FanPWM product / WebFlash / release surface; **records the ESPHome blocker that SX1509 expander pins cannot back a hardware `pulse_counter`, so per-fan RPM via `Pul_Cou1..4` stays open)* → `HW-PINMAP-311-FOLLOWUP` → `S360-311` `schematic_status` promotion (separate JSON PR) → `PACKAGE-PWM-001` (alias: `PACKAGE-GAP-001` FanPWM slice). **`PACKAGE-PWM-TACH-STRATEGY-001` (2026-05-25) resolved the expander-tach RPM decision** (operator: PWM-drive-only first; per-fan RPM deferred) and scoped the first package to **four PWM outputs (SX1509 ch0..3), no per-fan RPM sensors, optional diagnostic binary tach states only (ch4..7), `TachIO`/`GPIO16` reserved/pending** — see [`s360-311-r4-pwm.md` §Tach / RPM strategy](s360-311-r4-pwm.md#tach--rpm-strategy-package-pwm-tach-strategy-001). For that **PWM-only** slice, tach-pull-up / pulses-per-rev no longer gate (no RPM exposed); the remaining `PACKAGE-PWM-001-IMPLEMENT-001` gate is bench **PWM-polarity** + per-fan/aggregate **current/thermal envelope** + the **four-channel reconciliation** of `fan_pwm.yaml`. Per-fan RPM remains future work (`COMPONENT-SX1509-TACH-001` or a bench-confirmed `TachIO` follow-up); the package is **not yet implemented**. Abstract-bus rebind is `CORE-ABSTRACT-BUS-001`. |
| [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) | `S360-312` Sense360 DAC | `FanDAC` — dual-GP8403 (IC1 / IC2) 12-bit DAC over I²C; four neutral package-layer outputs (two per chip); per-chip address + output-range substitutions | [`s360-312-r4-dac.md`](s360-312-r4-dac.md) (HW-PINMAP-312) **`partial — schematic evidence available; package reconciliation pending`**; module-side schematic PDF + curated artifact index committed under HW-ASSETS-003; standalone schematic+BOM reference doc landed at [`s360-312-r4-fandac.md`](s360-312-r4-fandac.md) on 2026-05-22 (HW-PINMAP-312-FOLLOWUP — records `IC1`/`IC2` `GP8403-TC50-EW` BOM-confirmed, `SW1`/`SW2` `219-3MSTR` 3-pole DIP BOM-confirmed, `V5V` of each DAC hardwired to `+12V` ⇒ range is firmware/register-driven only, no `5V`/`10V` jumper present in BOM, both DACs share the canonical `core_i2c` bus after PR #569); `PACKAGE-DAC-001-READINESS-REFRESH` pass (2026-05-22; same doc, [§PACKAGE-DAC-001 readiness refresh](s360-312-r4-fandac.md#package-dac-001-readiness-refresh)) recorded the 10-row readiness table and the verdict that `PACKAGE-DAC-001` is **not implementation-plannable yet**; the subsequent `HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001` pass (2026-05-22; same doc, [§2026-05-22 — HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001](s360-312-r4-fandac.md#2026-05-22--hw-pinmap-312-followup-dac-evidence-001)) then **closed rows 3 / 6 / 8** using the GP8403 public datasheet + the Drive KiCad PCB / gerber / board-render assets + the operator design decisions, recording the verdict that **`PACKAGE-DAC-001` is now implementation-plannable**; `PACKAGE-DAC-001-IMPLEMENT-001` (2026-05-23) then landed the package-layer YAML reconciliation (two GP8403 chips, four neutral outputs, per-chip address + range substitutions, corrected jumper comment) — see [§2026-05-23 — PACKAGE-DAC-001-IMPLEMENT-001](s360-312-r4-fandac.md#2026-05-23--package-dac-001-implement-001) | `package-layer-implemented` (product / WebFlash / release readiness remains blocked) | **Of the 10 FanDAC-specific blockers in [`s360-312-r4-fandac.md`](s360-312-r4-fandac.md#package-dac-001-readiness-refresh), rows 1 (shared-I²C-bus naming), 2 (GP8403 BOM identity), 5 (firmware/register-driven range mechanism), and 7 (per-channel range mixing constraint) are resolved or evidence-captured; row 9 (Nextion / UART0) is deferred out of `PACKAGE-DAC-001` scope; rows 3, 6, and 8 are now CLOSED by `HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001` (2026-05-22), leaving only row 10 implementation-pending.** **Row 3 — CLOSED:** DIP-switch → 7-bit-address truth table from the GP8403 datasheet (`A0`/`A1`/`A2` = bits 0/1/2; base `0x58`; span `0x58`–`0x5F`) + the KiCad PCB pole→pin map (`SW1`→`A0`/`A1`/`A2`, `SW2`→`2A0`/`2A1`/`2A2`; opposite side `GND`; closed = 0 / open = 1); package should expose per-chip `${fan_dac_address}` (`IC1`, default `0x58`) + `${fan_dac_address_2}` (`IC2`, default `0x59`). **Row 6 — CLOSED:** per-DAC-chip range, both default 0–10 V, independent override (operator decisions); datasheet confirms range is register-`0x01`, chip-level (`0x00`→0–5 V, `0x11`→0–10 V), not per-output. **Row 8 — board-level CLOSED:** PCB + bottom-silkscreen render show both `J2` and `J3` wire **pin 1 = `VOUT0` / pin 2 = `GND` / pin 3 = `VOUT1`**; `J2` silk matches `IC1` channels while **`J3` silk `out0`/`out1` is transposed** vs the `IC2` channel nets (pin 1 silk `out1` = net `2vout0`); the harness-to-fan conductor trace remains a product/bench item and does not block the package. **Row 10 — DONE (2026-05-23, `PACKAGE-DAC-001-IMPLEMENT-001`):** bound two GP8403 devices (`fan_dac_1`/IC1, `fan_dac_2`/IC2), added per-chip address (`fan_dac_1_i2c_address` `0x58` / `fan_dac_2_i2c_address` `0x59`) + output-range (`fan_dac_1_output_range` / `fan_dac_2_output_range`, both `0-10V`) substitutions, exposed four neutral outputs (`fan_dac_1_vout0` / `fan_dac_1_vout1` / `fan_dac_2_vout0` / `fan_dac_2_vout1`), corrected the stale "(jumper selectable on hardware)" comment, and removed the product-layer `fan:` / `sensor:` / `globals:` / `script:` blocks (move to `PRODUCT-DAC-001`). Core `J7` pin-1 `+5V` vs Module `J1` pin-1 `+3.3V` voltage-rail discrepancy is still outstanding (parallel `S360-100-BENCH-001` track) but does not block the package. The post-PR-#569 active YAML inherits `${fan_dac_i2c_id}: core_i2c`; the header-comment block lines 13–18 was updated by PR #569 to reference `GPIO48` / `GPIO45`. `S360-312` JSON `schematic_status` stays `cataloged_unverified`. Subject to `FanDAC` ↔ `AirIQ` mutex in [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json). | **Package-layer edit landed (2026-05-23).** `PACKAGE-DAC-001-IMPLEMENT-001` reconciled [`fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) to two GP8403 chips / four neutral outputs with per-chip address + range substitutions and a corrected jumper comment (rows 3 / 6 / 8 closed by `HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001`, 2026-05-22). New regression `tests/test_fandac_package.py`. **Package layer only — no DAC product YAML, no compile-only target, no WebFlash wrapper, no `webflash_build_matrix` flip, no `artifact_name`, no `schematic_status` / `schematic_file` promotion.** [`fan_dac.yaml`](../../packages/expansions/fan_dac.yaml) stays a pure-wrapper. The next PR is **`PRODUCT-DAC-001`**. Residual product / bench items — harness trace to the Cloudlift S12 fan, `J3` silk-transposition confirmation, as-shipped DIP default, and the `J1` / `J7` `+3.3 V` / `+5 V` rail discrepancy — do not block the package YAML. | `HW-PINMAP-312-FOLLOWUP` standalone reference doc *(landed 2026-05-22)* → `PACKAGE-DAC-001-READINESS-REFRESH` *(landed 2026-05-22 — this PR; docs / readiness only)* → `HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001` *(landed 2026-05-22 — this PR; closed rows 3 / 6 / 8 via the GP8403 datasheet + Drive KiCad PCB / gerber / render assets + operator decisions; docs / evidence only)* → **`PACKAGE-DAC-001-IMPLEMENT-001`** *(landed 2026-05-23 — alias: `PACKAGE-GAP-001` FanDAC slice; bound two GP8403s, per-chip address + range substitutions, four outputs, corrected jumper comment)* → `PRODUCT-DAC-001` (product YAML / user-facing fan entities) → `S360-312` `schematic_status` promotion (separate JSON PR). Residual product / bench evidence (harness trace, `J3` silk transposition, as-shipped DIP default, `J1` / `J7` `+3.3 V` / `+5 V` rail via `S360-100-BENCH-001`) is tracked separately and does not block the package. |
| [`packages/expansions/fan_triac.yaml`](../../packages/expansions/fan_triac.yaml) | `S360-320` Sense360 TRIAC | `FanTRIAC` — `output: ac_dimmer` + `fan: speed` (phase-cut AC); requires direct interrupt-capable ESP32 GPIOs for `gate_pin` + `zero_cross_pin`; retained with BLOCKED / UNVERIFIED banner | [`s360-320-r4-triac.md`](s360-320-r4-triac.md) (HW-PINMAP-320) **`partial — schematic evidence available; package reconciliation, timing validation, and compliance/certification pending`**; module-side schematic PDF + curated artifact index committed under HW-ASSETS-003 | `timing/compliance-pending` + `needs-package-reconciliation` + `blocked-from-standard-exposure` | `TRI_GPIO1` / `TRI_GPIO2` (Core sheet labels) ↔ `ESP_GPIO1` / `ESP_GPIO2` (module sheet labels) — same wire, two names; placeholder `fan_triac_gate_pin: GPIO5` / `fan_triac_zc_pin: GPIO6` in the Release-One reference product YAML already claimed by RoomIQ J10 (`IO5 = SEN0609_TX`, `IO6 = out(gpio6)`); `ac_dimmer` ISR requires direct interrupt-capable ESP32 GPIOs and explicitly **rejects** SX1509-routed pins; module-side EL814 zero-cross topology + module-side TRIAC drive topology need bench / waveform proof; mains-voltage compliance owed by COMPLIANCE-001 (per [`s360-320-r4-triac.md` Package YAML status](s360-320-r4-triac.md#package-yaml-status)); HW-005 (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` blocker) unresolved. | **No package edit.** HW-005 + HW-PINMAP-320-FOLLOWUP + bench timing evidence + COMPLIANCE-001 advanced/manual-warning sign-off all required. | `HW-PINMAP-320-FOLLOWUP` + `HW-005` unblock + `COMPLIANCE-001` advanced/manual-warning slice → `PACKAGE-TRIAC-001` (alias: `PACKAGE-GAP-001` FanTRIAC slice). Long-term advanced / manual-warning posture in [`s360-320-r4-triac.md` Advanced / manual-warning product posture](s360-320-r4-triac.md#advanced--manual-warning-product-posture); JSON `status: blocked` stays. |
| [`packages/hardware/power_240v.yaml`](../../packages/hardware/power_240v.yaml) | `S360-400` Sense360 240v PSU | `PWR` — logical 240V power package; emits diagnostic sensors (`Supply Voltage`, `Power Source`, `Power Configuration`, `AC Power Connected`); no GPIO binding to module pins | [`s360-400-r4-power.md`](s360-400-r4-power.md) (HW-PINMAP-400) **`partial — schematic evidence available; package reconciliation, BOM, silkscreen, creepage/clearance, and COMPLIANCE-001 pending`** (promoted by HW-PINMAP-400-FOLLOWUP after consuming HW-ASSETS-400 / PR #514; 2026-05-19 `PACKAGE-POWER-400-001` investigation pass re-confirmed all five preconditions stay open per [`s360-400-r4-power.md` §2026-05-19 — PACKAGE-POWER-400-001 investigation pass](s360-400-r4-power.md#2026-05-19--package-power-400-001-investigation-pass-deferred-preconditions-still-open)); module-side schematic PDF + curated artifact index committed under HW-ASSETS-400 at [`docs/hardware/artifacts/S360-400-R4.md`](artifacts/S360-400-R4.md) + [`schematics/S360-400-R4.pdf`](schematics/S360-400-R4.pdf) | `schematic-evidence-pending` + `needs-package-reconciliation` + `timing/compliance-pending` (compliance-gated) | **Three-way AC/DC part-identity disagreement now visible:** catalog `description` says `Mains to 5V using HLK-5M05`; package header-comment says `HLK-PM01 or similar`; HW-ASSETS-400 schematic shows `PS1 = HLK-10M05` (per [`docs/hardware/artifacts/S360-400-R4.md`](artifacts/S360-400-R4.md) and [`s360-400-r4-power.md` Part identity reconciliation](s360-400-r4-power.md#part-identity-reconciliation)). Reconciliation owed to BOM cross-check + `PACKAGE-POWER-400-001` (investigated 2026-05-19 — confirmed deferred / Path A docs-only; five preconditions still open per [`s360-400-r4-power.md` §2026-05-19 — PACKAGE-POWER-400-001 investigation pass](s360-400-r4-power.md#2026-05-19--package-power-400-001-investigation-pass-deferred-preconditions-still-open)). Input rating `100-240V AC, 50/60Hz`, output `5V DC, 2A (10W)`, isolation `3000VAC` are package-header text only, **not** schematic-verified (the schematic shows a HLK-10M05 module, four-cap output filter `C5 100uF / C6 10u / C7 100n / C8 100uF`, 2-pin `J2 +5VP / GND` output; no isolation barrier or rating annotation). Mains-protection topology schematic-confirmed: resettable fuse `F1 A250-1200`, MOV `RV1 10D391K`, X-cap `C1 470nF` across the AC line; the per-component ratings are BOM-bound. COMPLIANCE-001 mains-voltage UK / EU sign-off gates any product-side promotion. | **No package edit.** HW-PINMAP-400-FOLLOWUP and the 2026-05-19 `PACKAGE-POWER-400-001` investigation pass are both docs-only and do not edit the header; comment-only cleanup is deferred to `PACKAGE-POWER-400-001` once BOM evidence lands. BOM cross-check + `S360-400` `schematic_status: verified` JSON PR + COMPLIANCE-001 must close before any package edit. | `HW-ASSETS-400` *(landed at PR #514)* → `HW-PINMAP-400-FOLLOWUP` *(landed at PR #515; docs-only)* → BOM evidence + silkscreen + creepage / clearance + bench / thermal / EMI evidence → `S360-400` `schematic_status` promotion (separate JSON PR) → `COMPLIANCE-001` S360-400 slice → `PACKAGE-POWER-400-001` (alias: `PACKAGE-GAP-001` PWR slice; investigated 2026-05-19 as docs-only Path A deferral; this PR). |
| [`packages/hardware/power_poe.yaml`](../../packages/hardware/power_poe.yaml) | `S360-410` Sense360 PoE PSU | `POE` — logical PoE power package; emits diagnostic sensors (`Supply Voltage`, `Power Source`, `Power Configuration`, `PoE Power Connected`); no GPIO binding; consumed by Release-One under preserved schematic-pending caveat | [`s360-410-r4-poe.md`](s360-410-r4-poe.md) (HW-PINMAP-410) **status promoted by HW-PINMAP-410-FOLLOWUP** to `partial — schematic evidence available; package reconciliation, PoE PD controller / magnetics / buck / isolated DC/DC / harness identity evidence pending`; module-side schematic committed under HW-ASSETS-410 / PR #516 at [`docs/hardware/schematics/S360-410-R4.pdf`](schematics/S360-410-R4.pdf) (975,137 bytes; SHA256 `4a8b7a3b2a89006a9332eaa486743f687aaedc4b6bb807c6b25670f742ac2414`) with curated artifact index at [`docs/hardware/artifacts/S360-410-R4.md`](artifacts/S360-410-R4.md) | `reference-only` (logical, no GPIO binding) + `schematic-evidence-pending` (schematic consumed by HW-PINMAP-410-FOLLOWUP; package-header reconciliation still owed to `PACKAGE-POE-410-001` after BOM lands) + `do-not-change-release-one` | Module-side schematic committed under HW-ASSETS-410 / PR #516 and consumed by HW-PINMAP-410-FOLLOWUP; BOM not provided in upload; the package-header whole-module PoE-module hint (`Ag9712M`, `Silvertel Ag9700`, `or similar`) disagrees with the schematic-shown discrete `TPS2378DDAR(HSOIC-8)` PoE PD controller + `TX4138(ESOIC-8)` buck + `F0505S-2WR2(SIP-7)` isolated DC/DC (with `AM1D-0505S-NZ` annotated as alternate) + `RJP-003TC1(LPJ4112CNL)` magnetics, recorded as **unresolved by HW-PINMAP-410-FOLLOWUP** (resolution belongs to `PACKAGE-POE-410-001` after BOM lands); the schematic-visible PoE class declaration is `Class=0 (0.44 to 12.95W)` per `R2 1.27k` classification programming; package-header standard / class / input / output / protection ratings remain not schematic-verified against the schematic-shown topology; Core `J2` PoE harness identity is HW-002 Open Question #6 (tracked under [S360-100-BENCH-001](s360-100-r4-core.md#s360-100-bench-001-status), `pending — bench/manufacturing evidence required`). PoE is SELV; **not** in scope for COMPLIANCE-001. Release-One "schematic verification pending" caveat in [`release-one-hardware-audit.md` Findings → PoE PSU](../release-one-hardware-audit.md#findings) is **preserved verbatim** by HW-PINMAP-410-FOLLOWUP. | **No package edit.** The logical role is consumed by Release-One today and may not be changed in PACKAGE-GAP-001. Comment-only cleanup of the stale `Ag9712M / Silvertel Ag9700 / or similar` header is **deferred to `PACKAGE-POE-410-001`** once BOM evidence lands. | BOM cross-check → `HW-002 OQ#6` closure / `S360-100-BENCH-001` update → `S360-410` `schematic_status: verified` JSON PR → `PACKAGE-POE-410-001` (alias: `PACKAGE-GAP-001` PoE slice; reconciles package-header against schematic-shown `TPS2378DDAR / TX4138 / F0505S-2WR2 / RJP-003TC1(LPJ4112CNL)` parts and module BOM). Release-One caveat closure is a separate later PR per [`s360-410-r4-poe.md` Follow-up PR sequence](s360-410-r4-poe.md#follow-up-pr-sequence). |
| [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml) + [`packages/hardware/sense360_core.yaml`](../../packages/hardware/sense360_core.yaml) (Core abstract-bus) | `S360-100` Sense360 Core (abstract-bus substitutions consumed by every fan-driver package) | `relay_pin`, `expansion_gpio1` / `expansion_gpio2`, `halo_i2c`, `expansion_i2c`, `uart_bus`, `status_led_pin`, `pir_sensor_pin` substitutions consumed by Release-One + LED preview + every fan slice | [`firmware-package-mapping-audit.md` Release-One product YAML package stack](firmware-package-mapping-audit.md#release-one-product-yaml-package-stack) (HW-009) `needs-package-change` (systemic; explicit out-of-scope for HW-009); CORE-ABSTRACT-BUS-001 docs-only audit landed at [`core-abstract-bus-reconciliation.md`](core-abstract-bus-reconciliation.md), splitting the implementation into three slices `001A` / `001B` / `001C` | `do-not-change-release-one` + `needs-package-reconciliation` (systemic; split into slices `001A` / `001B` / `001C`; deferred) | Ceiling Core `relay_pin: GPIO4`, `status_led_pin: GPIO48`, `pir_sensor_pin: GPIO47`, `expansion_gpio1/2: GPIO5/6`, `halo_i2c` on `GPIO39/40`, `expansion_i2c` on `GPIO21/18`, `uart_bus` on `GPIO1/2` all disagree with the Core schematic at the connector / net level — enumerated in [`release-one-hardware-audit.md` Summary](../release-one-hardware-audit.md#summary), inventoried per substitution × per Core package in [`core-abstract-bus-reconciliation.md` Core abstract substitution inventory](core-abstract-bus-reconciliation.md#core-abstract-substitution-inventory), and owned by Required follow-ups #2 / #3. The audit also surfaces a GPIO3 collision (schematic-correct `relay_pin: GPIO3` vs existing `comfort_ceiling_als_int_pin: GPIO3` in [`comfort_ceiling.yaml`](../../packages/expansions/comfort_ceiling.yaml) line 42; vs `sx1509_interrupt_pin: GPIO3` in [`gpio_expander_sx1509.yaml`](../../packages/expansions/gpio_expander_sx1509.yaml) line 17; vs `expander_int_pin: GPIO3` in [`sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml) line 54) that prevents the `relay_pin` slice from landing in isolation. Resolution feeds into every fan-driver slice. | **No package edit by PACKAGE-GAP-001.** | `CORE-ABSTRACT-BUS-001` docs-only audit *(landed at [`core-abstract-bus-reconciliation.md`](core-abstract-bus-reconciliation.md))* → `CORE-ABSTRACT-BUS-001C` (UART / status LED / PIR / expansion GPIO + ALS_INT rebind; must land first to free `GPIO3`) → `CORE-ABSTRACT-BUS-001A` (`relay_pin → GPIO3`) → `PACKAGE-RELAY-001`; `CORE-ABSTRACT-BUS-001B` (I²C bus consolidation to single shared bus on `IO48`/`IO45`) runs independent of 001A/001C ordering but must land before `PACKAGE-PWM-001` / `PACKAGE-DAC-001`. Aliases: [`release-one-hardware-audit.md` Required follow-ups #2 / #3](../release-one-hardware-audit.md#required-follow-ups). |

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

- **Status.** `package-implemented` +
  `reconciled-at-package-layer`. PACKAGE-RELAY-001 has landed as a
  **test + readiness reconciliation** after the package-evidence
  layer closed: no YAML edit was required because the FanRelay
  package was already structurally correct
  (`fan_relay_pin: ${relay_pin}` in
  [`packages/expansions/fan_relay.yaml`](../../packages/expansions/fan_relay.yaml)
  line 27 inherits the parent Core abstract package binding, and
  post-001A `${relay_pin}` resolves to the schematic-correct
  `GPIO3`). The PR added
  [`tests/test_fan_relay_package.py`](../../tests/test_fan_relay_package.py)
  pinning the package abstraction against future regression.
  Substitution-layer blockers were resolved by `CORE-ABSTRACT-BUS-001A`
  (PR #558) + `CORE-ABSTRACT-BUS-001C` (PR #557); hardware-evidence
  blockers were populated by `S360-310-BENCH-EVIDENCE-001` (PR #561,
  2026-05-22) from operator-attested + BOM-backed + public-reference-
  backed sources. **No photo / video / oscilloscope / continuity-meter
  artifacts attached.** Product / WebFlash / release / compliance /
  mains-safety gates stay separately blocked. PRODUCT-RELAY-001 is the
  next Relay-chain PR but remains separate and gated on its own
  evidence.
- **Evidence state.** The Core schematic shows `Relay = IO3` at `J4`
  pin 2 (per [`s360-310-r4-relay.md` Reconciliation findings](s360-310-r4-relay.md#reconciliation-findings)).
  **Pre-001A** the ceiling Core abstract package bound
  `relay_pin: GPIO4` and the generic Core abstract package bound
  `relay_pin: GPIO10`. **Post-001A** the five non-voice Core abstract
  packages bind `relay_pin: GPIO3` (schematic-correct); the `GPIO3`
  collision with `comfort_ceiling_als_int_pin` / `expander_int_pin` /
  `sx1509_interrupt_pin` was resolved by 001C moving ALS_INT to
  `GPIO47` and the expander interrupt to `GPIO17`. The module-side
  schematic landed under HW-ASSETS-310 at
  [`docs/hardware/artifacts/S360-310-R4.md`](artifacts/S360-310-R4.md)
  + [`schematics/S360-310-R4.pdf`](schematics/S360-310-R4.pdf), and
  **HW-PINMAP-310-FOLLOWUP** consumed it: a `J2` 3-pin "From Core"
  connector (`+5V` / `Relay` / `GND`) net-order match to Core `J4`,
  and a `K1` mechanical-relay coil-drive topology (`Q1` MMBT3904 NPN
  low-side; `R1` 1 kΩ base; `R2` 10 kΩ base pull-down; `D1`
  flyback). **`S360-310-BENCH-EVIDENCE-001`** (2026-05-22) populated
  the ten enumerated hardware-evidence rows in
  [`s360-310-r4-relay.md` §S360-310-BENCH-001 — Relay bench evidence](s360-310-r4-relay.md#s360-310-bench-001--relay-bench-evidence)
  from four evidence classes:
  - **Operator-attested** (operator `@wifispray` against the
    populated `S360-100-R4` + `S360-310-R4` pair, 2026-05-22):
    Core-side `J4` pin order `+5V` / `Relay` / `GND`; module-side
    `J2` pin order `+5V` / `Relay` / `GND`; module-side `J1`
    mapping `NO` / `COM` / `NC`; 3-pin Core ↔ module harness
    straight-through with J4-1↔J2-1 / J4-2↔J2-2 / J4-3↔J2-3;
    expected controlled load type UK mains Manrose `MT100S`-class
    extractor fan (operator self-report of installation posture
    "as per UK standards", **not** an independent compliance
    sign-off); relay boot state de-energized across **10 boot
    cycles × 4 power paths** (USB, PoE, 5 V PSU, 240 V supply
    path) with firmware `Ceiling-POE-VentIQ-RoomIQ`; relay load /
    contact proof (fan off until relay activates, relay on → fan
    on, relay off → fan off; behaviour consistent with `NO` +
    `COM` wiring).
  - **BOM-backed** (operator-uploaded `S360-310-R4_BOM.xlsx`,
    uploaded operator-side, **not** committed to this repository):
    `K1` Songle Relay `SRD-05VDC-SL-C` (value
    `SRD-05VDC-SL-C-srd_relay`; footprint
    `greencharge-footprints:RELAY_SRD-05VDC-SL-C`; qty 1).
  - **Public-reference-backed** (SRD-style 5 V relay reference /
    datasheet): `K1` contact-current rating
    `10 A @ 250 VAC; 10 A @ 30 VDC`, SPDT (`NO` / `COM` / `NC`
    terminals). **Caveat:** contact-rating evidence only — **not**
    board-level compliance, installation approval, creepage /
    clearance, thermal, EMI, or mains-safety certification.
  - **Pair-scoped sufficient for package implementation**: the
    `GPIO3` strap-pin boot-behaviour row is recorded as
    `captured enough for PACKAGE-RELAY-001 implementation`
    against the operator-attested 10 boot cycles × 4 power paths
    on the populated `S360-100-R4` + `S360-310-R4` pair. **Caveat:**
    **not** a production-wide, multi-unit, oscilloscope-traced,
    compliance, release-readiness, or safety-certification claim.
- **Allowed action now.** **`PACKAGE-RELAY-001` is implemented /
  reconciled at the package layer.**
  [`fan_relay.yaml`](../../packages/expansions/fan_relay.yaml)
  remains structurally correct and unchanged:
  `fan_relay_pin: ${relay_pin}` (line 27) inherits the parent Core
  abstract package binding, and that binding resolves to the
  schematic-correct `GPIO3` automatically post-001A. The
  PACKAGE-RELAY-001 PR added
  [`tests/test_fan_relay_package.py`](../../tests/test_fan_relay_package.py)
  to pin the package abstraction (the package parses as YAML;
  `fan_relay_pin` defaults to `${relay_pin}`; the package does not
  hard-code any GPIO; `fan_relay_switch` binds
  `pin: ${fan_relay_pin}`; the five non-voice Core abstract
  packages bind `relay_pin: GPIO3`; voice variants stay at the
  pre-001A `relay_pin: GPIO4`; no FanRelay product YAML or
  WebFlash-builds entry was added). The next Relay PR is
  `PRODUCT-RELAY-001`, but it stays separately gated on
  product-layer compliance / mains-safety / installation /
  production-wide characterisation evidence. "Implemented /
  reconciled at the `PACKAGE-RELAY-001` package layer" does **not**
  mean product-ready, WebFlash-ready, release-ready,
  compliance-cleared, safe for arbitrary mains installation, or
  verified across production batches.
- **Follow-up owner.** `HW-ASSETS-310` *(landed)* →
  `HW-PINMAP-310-FOLLOWUP` *(landed; schematic-backed reconciliation
  recorded in [`s360-310-r4-relay.md`](s360-310-r4-relay.md))* →
  `CORE-ABSTRACT-BUS-001` docs-only audit *(landed)* →
  `CORE-ABSTRACT-BUS-001C` *(landed PR #557 — freed `GPIO3`)* →
  `CORE-ABSTRACT-BUS-001A` *(landed PR #558 — `relay_pin → GPIO3`)*
  → `PACKAGE-RELAY-001-READINESS-REFRESH` *(landed PR #559 —
  docs/evidence/readiness only)*
  → `S360-310-BENCH-001` *(landed PR #560 — evidence-capture
  **checklist** only; ten enumerated hardware-evidence rows
  recorded against the populated `S360-310-R4` + `S360-100-R4`
  pair, all rows `pending — bench evidence required`; no physical
  evidence supplied)*
  → `S360-310-BENCH-EVIDENCE-001` *(landed PR #561 — evidence-
  population only; ten rows captured from operator-attested +
  BOM-backed + public-reference-backed sources; no photo / video /
  oscilloscope / continuity-meter artifacts attached;
  `PACKAGE-RELAY-001` implementation-ready at package-evidence
  layer only)*
  → **`PACKAGE-RELAY-001`** *(this PR — test + readiness
  reconciliation only; no YAML rebind; added
  `tests/test_fan_relay_package.py` pinning the FanRelay package
  abstraction; package status moves to `package-implemented` +
  `reconciled-at-package-layer`; no Relay product YAML / WebFlash
  wrapper / release artifact / compliance movement)*
  → `PRODUCT-RELAY-001` (alias: `PRODUCT-GAP-001` FanRelay slice).
  The `IO3` vs `GPIO4` vs `GPIO10` substitution-layer resolution
  **belonged to** `CORE-ABSTRACT-BUS-001` and was **resolved by**
  `CORE-ABSTRACT-BUS-001A`; the hardware / bench / silkscreen /
  harness / BOM / load-contact / pair-scoped `GPIO3` strap-pin
  boot-behaviour evidence was captured at the package-evidence
  layer by `S360-310-BENCH-EVIDENCE-001` (PR #561); the package
  reconciliation itself is closed by **this PR**
  (`PACKAGE-RELAY-001`). The next Relay PR is `PRODUCT-RELAY-001`.
- **Cross-references.** [`docs/hardware/artifacts/S360-310-R4.md`](artifacts/S360-310-R4.md);
  [`s360-310-r4-relay.md` PACKAGE-RELAY-001 readiness refresh after CORE-ABSTRACT-BUS-001C / 001A](s360-310-r4-relay.md#package-relay-001-readiness-refresh-after-core-abstract-bus-001c--001a);
  [`s360-310-r4-relay.md` S360-310-BENCH-001 — Relay bench evidence](s360-310-r4-relay.md#s360-310-bench-001--relay-bench-evidence);
  [`s360-310-r4-relay.md` Follow-up PR sequence](s360-310-r4-relay.md#follow-up-pr-sequence);
  [`s360-310-r4-relay.md` HW-PINMAP-310-FOLLOWUP audit log](s360-310-r4-relay.md#hw-pinmap-310-followup-audit-log);
  [`board-readiness-matrix.md` `S360-310` notes](board-readiness-matrix.md#s360-310-sense360-relay);
  [`core-abstract-bus-reconciliation.md` §2026-05-21 — CORE-ABSTRACT-BUS-001A implementation](core-abstract-bus-reconciliation.md#2026-05-21--core-abstract-bus-001a-implementation);
  [`s360-100-r4-core.md` S360-100-BENCH-001 status](s360-100-r4-core.md#s360-100-bench-001-status)
  (Core-side `J4` silkscreen / pin-1 gate still
  `pending — bench/manufacturing evidence required`).
- **PACKAGE-RELAY-001 investigation outcome.** PACKAGE-RELAY-001
  was investigated against the readiness gates above and is
  **confirmed deferred**: `CORE-ABSTRACT-BUS-001` (alias for
  [`release-one-hardware-audit.md` Required follow-ups #2 / #3](../release-one-hardware-audit.md#required-follow-ups))
  has not landed and owns the `IO3` (Core schematic) vs `GPIO4`
  ([`sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml)
  line 61) vs `GPIO10`
  ([`sense360_core.yaml`](../../packages/hardware/sense360_core.yaml)
  line 63) `relay_pin` resolution; the module-side silkscreen /
  harness / `K1` BOM evidence (module-side `J2` pin-1 orientation;
  module-side `J1` pin-1 orientation and NO / COM / NC mapping;
  Core-side `J4` pin-1 orientation; `K1` part identity / coil
  voltage / contact configuration / contact rating / isolation
  rating; Core-to-module 3-pin harness conductor-by-conductor
  mapping) is not on file; and no bench / continuity / waveform
  evidence against a populated `S360-310-R4` + `S360-100-R4` pair
  has been recorded. The package YAML
  [`packages/expansions/fan_relay.yaml`](../../packages/expansions/fan_relay.yaml)
  is **already structurally correct** for the state of the
  evidence: `fan_relay_pin: ${relay_pin}` (line 27) inherits
  whichever value the parent Core abstract package binds, the
  override-hook comment block (lines 22–25) documents how a parent
  product YAML can drive an external SSR from an expansion pin
  (`fan_relay_pin: ${expansion_gpio1}`), the `switch.platform: gpio`
  declaration uses `pin: ${fan_relay_pin}` (line 38), and the
  `restore_mode: RESTORE_DEFAULT_OFF` / `on_turn_on` / `on_turn_off`
  / `fan_auto_mode` global / `fan_emergency_stop` script wiring
  carry no hardcoded GPIOs. The wrong values live in the **Core
  abstract packages**
  ([`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml)
  `relay_pin: GPIO4`,
  [`packages/hardware/sense360_core.yaml`](../../packages/hardware/sense360_core.yaml)
  `relay_pin: GPIO10`), and the resolution is owned by
  `CORE-ABSTRACT-BUS-001`, not by `PACKAGE-RELAY-001`. There is no
  safe functional package YAML edit available today: a definitive
  binding change on `fan_relay.yaml` cannot be authored without
  picking a Core-side GPIO, and that choice belongs to
  `CORE-ABSTRACT-BUS-001`. The investigation outcome and full
  do-not-change inventory are recorded in
  [`docs/cleanup-audit.md` §PACKAGE-RELAY-001 update](../../docs/cleanup-audit.md#package-relay-001-update-deferred--core-abstract-bus-001--silkscreen--harness--k1-bom-evidence-not-landed).
  Status stays `schematic-evidence-pending` +
  `needs-package-reconciliation`; FanRelay remains **not**
  Release-One, **not** REQUIRED_CONFIGS, **not** kit / default,
  **not** recommended, and **not** consumed by any active product
  YAML, WebFlash wrapper, build-matrix row, release artifact, or
  WebFlash import. The `S360-310` JSON `schematic_status` stays
  `cataloged_unverified` with no `schematic_file` in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json);
  the `FanRelay` token reservation in
  [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json)
  `canonical_modules` (line 11) is unchanged.
  **Update (2026-05-22).** `S360-310-BENCH-EVIDENCE-001` (docs-only)
  populated the ten enumerated `S360-310-BENCH-001` hardware-evidence
  rows from operator-attested + BOM-backed + public-reference-backed
  sources supplied by operator `@wifispray` (Wifi Guy). The
  PACKAGE-RELAY-001 deferral is now lifted **at the package-evidence
  layer only** — `PACKAGE-RELAY-001` implementation slice may proceed.
  The package row above is updated to
  `package-evidence-captured` + `implementation-ready at
  PACKAGE-RELAY-001 evidence layer`. **No photo / video /
  oscilloscope / continuity-meter artifacts are attached** by this
  evidence-population PR; the operator-uploaded
  `S360-310-R4_BOM.xlsx` is **not** committed to this repository.
  `fan_relay.yaml` is **still not edited** by `S360-310-BENCH-EVIDENCE-001`;
  the implementation slice is owed to a separate
  `PACKAGE-RELAY-001` PR. "Implementation-ready at the
  `PACKAGE-RELAY-001` evidence layer" does **not** mean
  product-ready, WebFlash-ready, release-ready, compliance-cleared,
  safe for arbitrary mains installation, or verified across
  production batches. `PRODUCT-RELAY-001`, `WEBFLASH-RELAY-001`,
  `RELEASE-RELAY-001`, and `WF-IMPORT-RELAY-001` stay blocked
  behind `PACKAGE-RELAY-001`. `COMPLIANCE-001` is not advanced.
  `S360-100-BENCH-001` is not closed (the operator-attested Core
  `J4` pin order recorded against `S360-310-BENCH-001` does **not**
  discharge the broader Core silkscreen / manufacturing-evidence
  gate). The production-wide / multi-unit / oscilloscope-traced
  general `GPIO3` strap-pin boot-behaviour characterisation stays
  open and is **not** required for `PACKAGE-RELAY-001`
  implementation. The `S360-310` JSON `schematic_status` stays
  `cataloged_unverified` with no `schematic_file` in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json).
  The `FanRelay` token reservation in
  [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json)
  `canonical_modules` (line 11) is unchanged.
  **Update (PACKAGE-RELAY-001 implementation).** PACKAGE-RELAY-001
  has now **landed** as a **test + readiness reconciliation** —
  no YAML rebind, no product / WebFlash / release / compliance
  movement. The package was already structurally correct; the
  reconciliation is the addition of
  [`tests/test_fan_relay_package.py`](../../tests/test_fan_relay_package.py)
  which pins the FanRelay package abstraction (the package parses
  as YAML; `fan_relay_pin` defaults to `${relay_pin}`; the package
  does not hard-code any GPIO; `fan_relay_switch` binds
  `pin: ${fan_relay_pin}`; the five non-voice Core abstract
  packages bind `relay_pin: GPIO3`; voice variants stay at the
  pre-001A `relay_pin: GPIO4`; no FanRelay product YAML or
  WebFlash-builds entry was added by PACKAGE-RELAY-001). Status
  moves to `package-implemented` + `reconciled-at-package-layer`.
  `PRODUCT-RELAY-001` is the next Relay-chain PR but stays
  separately gated on its own evidence (no product / WebFlash /
  release / compliance / mains-safety / board-level installation
  approval / hardware-stable readiness claim is made by
  PACKAGE-RELAY-001).

### `fan_pwm.yaml` / S360-311

- **Status.** `package-layer-implemented (PWM-drive-only)` +
  `bench-evidence-pending`. The package-YAML reconciliation landed via
  `PACKAGE-PWM-001-IMPLEMENT-001` (2026-05-25, PWM-drive-only scope); product
  / WebFlash / release readiness remains blocked (see the
  `PACKAGE-PWM-001-IMPLEMENT-001 addendum` below).
- **What was wrong (pre-`PACKAGE-PWM-001-IMPLEMENT-001`).**
  [`fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml)
  bound a single `${fan_pwm_pin}` to a direct ESP32 GPIO (resolved
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
- **PWM-BLOCKER-REMOVAL-001 addendum (2026-05-25).** Status label
  unchanged (`needs-package-reconciliation` + `bench-evidence-pending`);
  the FanPWM-specific evidence audit recorded in
  [`s360-311-r4-pwm.md` §PWM-BLOCKER-REMOVAL-001 readiness / blocker table](s360-311-r4-pwm.md#pwm-blocker-removal-001-readiness--blocker-table)
  narrows — but does not close — the `PACKAGE-PWM-001` gate:
  - **BOM cross-check resolved at the part-identity layer.** The Drive
    `12vFan_PWM_PulseCounter.xlsx` BOM cross-checks the committed
    `S360-311-R4` schematic 1:1 (`U1` MT3608 boost; `Q1`–`Q4`
    `ME15N10-G` low-side N-FETs; `D1` SS34; `L1` SRN6045TA 22 µH;
    `R3` 38k / `R5` 2k divider; JST-SH `SM04B` ×5 / `SM13B` ×1) — same
    standard `HW-BOM-ASSETS-002` applied to `S360-400` / `S360-410`. No
    `.xlsx` is committed; `schematic_status` is not promoted.
  - **Shared-I²C-bus blocker lifted.** `CORE-ABSTRACT-BUS-001B-IMPLEMENT-001`
    landed the `core_i2c` rename (the SX1509 expander now binds
    `sx1509_i2c_id: core_i2c`), so `PACKAGE-PWM-001` is no longer
    blocked at the shared-I²C-bus layer.
  - **Routing disagreement persists and shifted.** `CORE-ABSTRACT-BUS-001C`
    retired `expansion_gpio1..4`, so this package's documented
    `${expansion_gpio1}` / `${expansion_gpio2}` binding is now stale;
    the ceiling Core no longer defines `fan_pwm_pin` / `fan_tach_pin`,
    while the mapping Core binds them to direct ESP32 `GPIO4` / `GPIO5`
    — both still disagree with the schematic's SX1509-routed
    four-channel topology.
  - **Remaining gate is operator + bench, not evidence.** Single-vs-
    four-channel decision; SX1509-vs-direct-ESP32 routing decision;
    `J3` / `J6` 1-to-13 silkscreen pin order; PWM polarity / tach
    pull-up / pulses-per-revolution; UART-on-`J3`-pins-11/12; per-fan
    current + thermal envelope. `PACKAGE-PWM-001-IMPLEMENT-001` stays
    **NOT READY** *(superseded at the package layer by the addendum
    below — the PWM-drive-only package has since landed)*.
- **PACKAGE-PWM-001-IMPLEMENT-001 addendum (2026-05-25).** The canonical
  FanPWM package has been **implemented at the package layer for the
  PWM-drive-only scope** (operator decision D-T1 / `PACKAGE-PWM-TACH-STRATEGY-001`,
  confirmed by `PWM-SX1509-TACH-PROOF-001`).
  [`fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml) is **rewritten**
  to compose the neutral binding
  [`fan_pwm_sx1509.yaml`](../../packages/expansions/fan_pwm_sx1509.yaml)
  (`packages:` `!include`) and expose **four independent** `fan: platform:
  speed` controllers (`fan_pwm_1..4`) on the SX1509 PWM-drive outputs
  `fan_pwm_drive_1..4` (channels 0..3), pinned by
  [`tests/test_fan_pwm_package.py`](../../tests/test_fan_pwm_package.py).
  - **SX1509 PWM-drive output is supported and is the mechanism used**
    (`output: platform: sx1509`, the on-chip LED-driver PWM engine). The
    package does not re-declare the SX1509 channel map — it reuses the
    binding.
  - **No RPM is implemented or claimed.** Per-fan RPM via an SX1509
    `pulse_counter` is compile-proven unsupported (`PWM-SX1509-TACH-PROOF-001`:
    `esphome config` rejects it with `[sx1509] is an invalid option for
    [pin]`), so the package wires no `pulse_counter` and no RPM sensor. The
    four `Pul_Cou1..4` lines stay as the binding's INTERNAL diagnostic binary
    GPIO states (`fan_pwm_tach_1..4`) — diagnostic only, never labelled or
    surfaced as RPM.
  - **`TachIO` / `GPIO16` stays reserved/pending** — no `TachIO` sensor and
    no aggregate-RPM claim in the package.
  - **No direct ESP32 mapping** is reintroduced for `TachPMW1..4` /
    `Pul_Cou1..4` (no `ledc`, no raw GPIO in the package).
  - **Remaining gates before any FanPWM product surface:** bench **PWM
    polarity**; per-fan / aggregate **current + thermal envelope**; **product
    YAML**; **compile-only target / result**; **WebFlash / release / import /
    compliance**; and the **optional future RPM strategy**
    (`COMPONENT-SX1509-TACH-001` or a bench-confirmed `TachIO` follow-up). No
    product / WebFlash / release / config / firmware surface is advanced here;
    FanRelay and FanDAC are unchanged.
- **FW-COMPILE-PWM-001 addendum (2026-05-25).** A single **compile-only
  validation target** has been added for the PWM-drive-only FanPWM package:
  `ceiling-poe-fanpwm-compile-only` →
  [`products/compile-only/ceiling-poe-fanpwm.yaml`](../../products/compile-only/ceiling-poe-fanpwm.yaml)
  (config string `Ceiling-POE-FanPWM`) in
  [`config/compile-only-targets.json`](../../config/compile-only-targets.json),
  composing Core ceiling + PoE PSU + base + health + the PWM-drive-only
  [`fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml). It **validates the
  PWM-drive-only package scope** (SX1509 hub on `core_i2c`; four
  `output: platform: sx1509` PWM-drive outputs; four `fan: platform: speed`
  controllers) at ESPHome config / compile time.
  - It **does not prove product / WebFlash / release readiness** (no product
    YAML, no `config/webflash-builds.json` row, no `webflash_build_matrix`
    flip, no `artifact_name`, no release artifact; the skeleton lives under
    `products/compile-only/` so no `config/product-catalog.json` entry is
    added) and **does not claim RPM support** (`rpm_supported: false`; no
    `pulse_counter`; `TachIO` / `GPIO16` reserved).
  - The **full compile result remains pending** (`compile_validation_status:
    pending-ci`): ESPHome is not assumed present locally, so a GitHub Actions /
    `workflow_dispatch` `--compile` run is required before any compile result
    is claimed; only the metadata lane is asserted. Pinned by
    [`tests/test_compile_targets.py`](../../tests/test_compile_targets.py)
    `FanPWMCompileOnlyCoverageTests`. The S360-311 bench gates above and the
    optional future RPM strategy stay open; the `Ceiling-POE-FanPWM` lane stays
    `defer` in
    [`config/compile-only-candidates.json`](../../config/compile-only-candidates.json).

### `fan_gp8403.yaml` / S360-312

- **Status.** `package-layer-implemented` (rows 3 / 6 / 8 closed by
  `HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001`, 2026-05-22; the package
  YAML reconciliation landed via `PACKAGE-DAC-001-IMPLEMENT-001`,
  2026-05-23). Product / WebFlash / release readiness remains blocked.
- **What was reconciled (2026-05-23).**
  [`fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)
  previously bound one GP8403 device only (`gp8403.id: fan_dac`,
  single `${fan_dac_address}`) while the schematic + BOM show **two**
  `GP8403-TC50-EW` chips (`IC1` / `IC2`) on a shared I²C bus, each with
  independent DIP-switch address selection (`SW1` / `SW2` —
  BOM-confirmed `219-3MSTR` 3-pole SPST DIP switches from CTS).
  `PACKAGE-DAC-001-IMPLEMENT-001` reconciled the package to the
  schematic-correct **two-DAC / four-output** shape (operator decisions
  D1–D6): two `gp8403:` devices `fan_dac_1` (IC1) / `fan_dac_2` (IC2)
  on `${fan_dac_i2c_id}` (`core_i2c`); per-chip address substitutions
  `fan_dac_1_i2c_address` (`0x58`) / `fan_dac_2_i2c_address` (`0x59`)
  set against the row-3 truth table; per-chip output-range
  substitutions `fan_dac_1_output_range` / `fan_dac_2_output_range`
  (both default `0-10V`, independently overridable — range is per chip
  via datasheet register `0x01`, never per output); and four neutral
  outputs `fan_dac_1_vout0` / `fan_dac_1_vout1` / `fan_dac_2_vout0` /
  `fan_dac_2_vout1`. The stale line-6 comment ("0-10V or 0-5V (jumper
  selectable on hardware)") was corrected to firmware/register-driven
  (the schematic ties each chip's `V5V` pin directly to `+12V` from the
  MT3608 boost, and the BOM contains no range-select hardware — per
  [`s360-312-r4-fandac.md` GP8403 output range capability](s360-312-r4-fandac.md#gp8403-output-range-capability)
  and [§BOM cross-check](s360-312-r4-fandac.md#bom-cross-check)). The
  product-layer `fan:` / `sensor:` / `globals:` / `script:` blocks
  (hard-coded `${friendly_name}` fan names) were removed and move to
  `PRODUCT-DAC-001`. The package still inherits
  `${fan_dac_i2c_id}: core_i2c` from the Core abstract package after
  `CORE-ABSTRACT-BUS-001B-IMPLEMENT-001` (PR #569).
- **Still open (product / bench, not package-blocking).** Core `J7`
  pin-1 `+5V` vs Module `J1` pin-1 `+3.3V` voltage-rail discrepancy
  (`S360-100-BENCH-001`); UART-vs-Nextion arbitration on Module `J1`
  pins 4 / 5; the `J2` / `J3` → physical Cloudlift S12 fan harness
  conductor trace; operator / bench confirmation of the `J3` silk
  transposition; as-shipped factory DIP positions; and `S360-312`
  `schematic_status` promotion (separate JSON PR). User-facing fan
  entities / names move to `PRODUCT-DAC-001`.
- **Readiness refresh (2026-05-22).** The
  `PACKAGE-DAC-001-READINESS-REFRESH` pass at
  [`s360-312-r4-fandac.md` §PACKAGE-DAC-001 readiness refresh](s360-312-r4-fandac.md#package-dac-001-readiness-refresh)
  separates the 10 FanDAC-specific blockers into resolved / evidence-
  captured / deferred / still-blocking categories:
  - **Resolved**: row 1 (shared-I²C-bus naming — PR #569);
    row 2 (GP8403 BOM identity — PR #570).
  - **Evidence captured (constraint or comment-correction
    layer)**: row 5 (range mechanism is firmware/register-driven
    only — supports correcting the stale "(jumper selectable on
    hardware)" comment); row 7 (simultaneous per-channel 0–5 V +
    0–10 V on a single GP8403 is **not** a hardware capability —
    encoded as a hard guardrail).
  - **Deferred out of `PACKAGE-DAC-001` scope**: row 9 (Nextion /
    `J7` and UART0 interaction — belongs to a future product
    slice if a product ever exposes the Nextion display).
  - **Was still blocking; now CLOSED by
    `HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001` (2026-05-22,
    [§2026-05-22 — HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001](s360-312-r4-fandac.md#2026-05-22--hw-pinmap-312-followup-dac-evidence-001))**:
    - **row 3** — DIP-switch ↔ 7-bit I²C address truth table:
      **CLOSED** from the GP8403 datasheet (`A0`/`A1`/`A2` = bits
      0/1/2; base `0x58`; span `0x58`–`0x5F`) + the KiCad PCB
      pole→pin map (`SW1`→`A0`/`A1`/`A2`, `SW2`→`2A0`/`2A1`/`2A2`;
      opposite pole side `GND`; closed = 0 / open = 1).
    - **row 6** — output-range policy: **CLOSED** by operator
      decision (per-DAC-chip range; both default 0–10 V;
      independent `IC1`/`IC2` override) + datasheet register-`0x01`
      chip-level mechanism.
    - **row 8** — `J2` / `J3` silkscreen pin-1 identity:
      **board-level CLOSED** (both connectors pin 1 = `VOUT0` /
      pin 2 = `GND` / pin 3 = `VOUT1`; `J2` silk matches `IC1`
      channels; **`J3` silk `out0`/`out1` is transposed** vs the
      `IC2` channel nets). The harness-to-fan conductor trace
      remains a product/bench item.
  - **Row 10 (package YAML correctness) — DONE (2026-05-23).** Bound
    two GP8403s, added per-chip address + range substitutions, exposed
    four outputs, corrected the jumper comment via
    `PACKAGE-DAC-001-IMPLEMENT-001`.
  - **Verdict**: `PACKAGE-DAC-001` is **implemented at the package
    layer**. Product / WebFlash / release readiness remains blocked;
    the next PR is **`PRODUCT-DAC-001`**.
- **Allowed action now.** Package-layer reconciliation is **done**
  ([`fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml)
  reconciled by `PACKAGE-DAC-001-IMPLEMENT-001`;
  [`fan_dac.yaml`](../../packages/expansions/fan_dac.yaml) unchanged
  pure-wrapper). No DAC product YAML, compile-only target, or WebFlash
  wrapper is added by that slice. `S360-312` JSON `schematic_status`
  is still `cataloged_unverified`. Residual product / bench items
  (harness conductor trace to the Cloudlift S12 fan, operator /
  bench confirmation of the `J3` silk transposition, as-shipped DIP
  default, `J1` / `J7` `+3.3 V` / `+5 V` rail discrepancy) are
  tracked separately and do **not** block the package YAML; they move
  to `PRODUCT-DAC-001`.
- **Follow-up owner.** `HW-PINMAP-312-FOLLOWUP` standalone
  reference doc *(landed 2026-05-22 at
  [`s360-312-r4-fandac.md`](s360-312-r4-fandac.md))* →
  `PACKAGE-DAC-001-READINESS-REFRESH` *(landed 2026-05-22 — this
  PR; docs / readiness only;
  [§PACKAGE-DAC-001 readiness refresh](s360-312-r4-fandac.md#package-dac-001-readiness-refresh))*
  → `HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001` *(landed 2026-05-22 —
  this PR; closed rows 3 / 6 / 8 via the GP8403 datasheet + the
  Drive KiCad PCB / gerber / board-render assets + operator
  decisions; docs / evidence only;
  [§2026-05-22 — HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001](s360-312-r4-fandac.md#2026-05-22--hw-pinmap-312-followup-dac-evidence-001))*
  → **`PACKAGE-DAC-001-IMPLEMENT-001`** / `PACKAGE-GAP-001` FanDAC
  slice *(landed 2026-05-23 — bound two GP8403s, per-chip address +
  range substitutions, four outputs, corrected jumper comment;
  [§2026-05-23 — PACKAGE-DAC-001-IMPLEMENT-001](s360-312-r4-fandac.md#2026-05-23--package-dac-001-implement-001))*
  → `PRODUCT-DAC-001` (product YAML / user-facing fan entities) →
  `S360-312` `schematic_status` promotion (separate JSON PR). Residual
  product
  / bench evidence (harness conductor trace, `J3` silk transposition
  confirmation, as-shipped DIP default, `J1` / `J7` rail discrepancy
  via `S360-100-BENCH-001`) is tracked separately and does not block
  the package. Subject to the `FanDAC` ↔ `AirIQ` mutex in
  [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json).
- **Cross-references.** [`s360-312-r4-fandac.md`](s360-312-r4-fandac.md)
  (standalone schematic+BOM reference doc; HW-PINMAP-312-FOLLOWUP);
  [`s360-312-r4-fandac.md` §PACKAGE-DAC-001 readiness refresh](s360-312-r4-fandac.md#package-dac-001-readiness-refresh)
  (this PR — readiness table + verdict + recommended next PR);
  [`s360-312-r4-dac.md` Follow-up PR sequence](s360-312-r4-dac.md#follow-up-pr-sequence);
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

- **Status.** `schematic-evidence-pending` + `needs-package-reconciliation` + `timing/compliance-pending` (compliance-gated). Class unchanged by HW-PINMAP-400-FOLLOWUP and by the 2026-05-19 `PACKAGE-POWER-400-001` investigation pass. The per-board audit doc [`s360-400-r4-power.md`](s360-400-r4-power.md) is now `partial — schematic evidence available; package reconciliation, BOM, silkscreen, creepage/clearance, and COMPLIANCE-001 pending` after HW-PINMAP-400-FOLLOWUP consumed the HW-ASSETS-400 (PR #514) schematic, but the package row itself stays blocked on BOM + the `S360-400` `schematic_status: verified` JSON PR + COMPLIANCE-001. The 2026-05-19 `PACKAGE-POWER-400-001` investigation pass (Path A docs-only) re-confirmed all five preconditions stay open (BOM cross-check; `S360-400` `schematic_status: verified` JSON PR; COMPLIANCE-001 `S360-400` slice; silkscreen / PCB / creepage / clearance / bench / thermal / EMI evidence; three-way AC/DC part-identity reconciliation); see [`s360-400-r4-power.md` §2026-05-19 — PACKAGE-POWER-400-001 investigation pass](s360-400-r4-power.md#2026-05-19--package-power-400-001-investigation-pass-deferred-preconditions-still-open) and [`docs/cleanup-audit.md` §PACKAGE-POWER-400-001 update](../cleanup-audit.md#package-power-400-001-update-2026-05-19--docs-only-investigation-pass).
- **What is wrong.** [`power_240v.yaml`](../../packages/hardware/power_240v.yaml)
  is a logical-power package with no GPIO binding, but the
  AC/DC part-identity is now confirmed three-way disagreeing: package
  header-comment claims `HLK-PM01 or similar`,
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  line 109 records `Mains to 5V using HLK-5M05`, and the HW-ASSETS-400
  schematic shows `PS1 = HLK-10M05` at
  [`docs/hardware/artifacts/S360-400-R4.md`](artifacts/S360-400-R4.md).
  Input rating `100-240V AC, 50/60Hz`, output `5V DC, 2A (10W)`,
  isolation `3000VAC`, and the protection / over-current /
  over-voltage / short-circuit claims are package-header text only —
  the HW-ASSETS-400 schematic confirms a mains-fuse / MOV / X-cap /
  filter-cap network and a 2-pin `+5VP` / `GND` output but does not
  carry rating annotations or creepage/clearance evidence (per
  [`docs/hardware/artifacts/S360-400-R4.md`](artifacts/S360-400-R4.md)
  and
  [`s360-400-r4-power.md` Reconciliation findings](s360-400-r4-power.md#reconciliation-findings)).
  BOM cross-check, silkscreen pin-1, creepage/clearance, thermal,
  inrush, and EMI/EMC measurements are all owed to evidence-bearing
  follow-up PRs and to `PACKAGE-POWER-400-001`. COMPLIANCE-001
  mains-voltage UK / EU sign-off is a separate, additional gate
  before any `PWR`-bearing product / WebFlash work; it cannot be
  cleared by schematic evidence alone.
- **Allowed action now.** None on
  [`power_240v.yaml`](../../packages/hardware/power_240v.yaml).
  HW-PINMAP-400-FOLLOWUP explicitly **does not** edit the package
  header — comment-only cleanup of the `HLK-PM01 or similar` /
  input / output / isolation / protection / recommended-fusing
  claims is deferred to `PACKAGE-POWER-400-001` once BOM evidence
  lands (per the evidence standard "BOM is required to resolve
  part number/rating disputes"). Release-One ships PoE, not `PWR`;
  the four `legacy-compatible` `*-pwr` Core variants stay
  `legacy-compatible` and stay out of the WebFlash build matrix.
- **Follow-up owner.** `HW-ASSETS-400` *(landed at PR #514)* →
  `HW-PINMAP-400-FOLLOWUP` *(this PR; docs-only schematic-backed
  reconciliation; package row unchanged)* → BOM evidence + PCB /
  silkscreen / creepage / clearance + bench / load / thermal / EMI
  evidence (separate evidence-bearing slices) → `S360-400`
  `schematic_status` promotion (separate JSON PR) →
  `COMPLIANCE-001` `S360-400` slice (independent track) →
  `PACKAGE-POWER-400-001` / `PACKAGE-GAP-001` PWR slice (header /
  part-identity / rating reconciliation against the now-verified
  schematic + module BOM).
- **Cross-references.** [`docs/hardware/artifacts/S360-400-R4.md`](artifacts/S360-400-R4.md);
  [`s360-400-r4-power.md` Follow-up PR sequence](s360-400-r4-power.md#follow-up-pr-sequence);
  [`s360-400-r4-power.md` HW-PINMAP-400-FOLLOWUP audit log](s360-400-r4-power.md#hw-pinmap-400-followup-audit-log);
  [`board-readiness-matrix.md` `S360-400` notes](board-readiness-matrix.md#s360-400-sense360-240v-psu);
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md).
- **2026-05-20 — `HW-BOM-ASSETS-002` BOM-evidence ingest addendum
  (record-only).** The `HW-BOM-ASSETS-002` record-only BOM ingest
  landed the `S360-400-R4_BOM.xlsx`
  (`95878198-S360400R4_BOM.xlsx`; 10,987 bytes; SHA256
  `bb59f56da11fe83f83b2547322af4e594b658384ade9f06267af367ffb603a1d`)
  as retained-but-not-committed evidence inventoried at
  [`docs/hardware/artifacts/S360-400-R4.md` §HW-BOM-ASSETS-002 BOM ingest (2026-05-20)](artifacts/S360-400-R4.md#hw-bom-assets-002-bom-ingest-2026-05-20).
  The BOM `PS1` row (`Value: HLK-5M05` / `MFR#: HLK-5M05` /
  `Manufacturer: HI-LINK` / footprint
  `greencharge-footprints:CONV_HLK-5M05`) agrees with the catalog
  `description: "Mains to 5V using HLK-5M05."` and **reclassifies**
  the three-way AC/DC part-identity disagreement above: catalog
  `HLK-5M05` + BOM `HLK-5M05` = BOM/user-confirmed sourcing truth
  for the populated `PS1`; schematic `PS1 = HLK-10M05` (committed
  PDF) = schematic-label discrepancy (committed PDF stays
  byte-identical; correction owed to a later HW-ASSETS-400
  follow-up); package header `HLK-PM01 or similar`
  ([`packages/hardware/power_240v.yaml`](../../packages/hardware/power_240v.yaml)
  line 7) = disproved package-header comment text, comment-only
  cleanup deferred to `PACKAGE-POWER-400-001`.
  [`packages/hardware/power_240v.yaml`](../../packages/hardware/power_240v.yaml)
  stays **byte-identical to PR #515 / PR #520** (the stale
  `HLK-PM01 or similar` line at line 7, the `100-240V AC,
  50/60Hz` input claim at line 7, the `5V DC, 2A (10W)` output
  claim at line 8, the `3000VAC` isolation claim at line 9, the
  `Overcurrent, overvoltage, short-circuit` protection text at
  line 10, the recommended `1A` AC-input fusing line at line 15,
  the substitutions / globals / template diagnostic sensors /
  logger blocks all preserved); the package binds **no** GPIO /
  I²C / UART / SPI / DAC / runtime hardware.
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  `S360-400` row at lines 102–110 stays byte-identical (no
  `schematic_status` promotion, no `schematic_file` set, no
  `description` edit). Other BOM-confirmed component identities:
  `F1 A250-1200` (JDTfuse) resettable fuse; `RV1 10D391K`
  (RUILON) MOV; `C1 470nF` THT box X-cap (WALSON
  `C322S47438P40001`); `C5, C8 100uF` SMD electrolytic (KNSCHA
  `189RV0058`, two populated); `C6 10u` (Chinocera) / `C7 100n`
  (CCTC); `J1` WAGO 2601-3103 1×3 vertical terminal block; `J2`
  JST SH `SM02B-SRSS-TB(LF)(SN)` 1×2 horizontal connector.
  Per-component voltage / energy / safety-class / dielectric /
  ESR ratings beyond the BOM `MFR#` strings remain
  vendor-datasheet / silkscreen / bench / EMI / EMC evidence and
  are **not** resolved by this ingest. The row above stays
  `schematic-evidence-pending` + `needs-package-reconciliation` +
  `timing/compliance-pending` (compliance-gated); no row-status
  change. The `BOM cross-check missing` precondition listed under
  `PACKAGE-POWER-400-001` / `PRODUCT-POWER-400-001` /
  `WEBFLASH-POWER-400-001` / `RELEASE-POWER-400-001` is now
  **resolved at the AC/DC part-identity layer**; each slice
  stays blocked on its other recorded preconditions
  (`S360-400` `schematic_status: verified` JSON PR;
  `COMPLIANCE-001` `S360-400` slice closure; silkscreen / PCB /
  creepage / clearance / bench / thermal / EMI evidence; package
  / catalog reconciliation; product-onboarding approval where
  applicable; UX-class decision where applicable; release-time
  sub-gates where applicable). Investigation outcome recorded
  at [`s360-400-r4-power.md` §2026-05-20 — HW-BOM-ASSETS-002 BOM ingest](s360-400-r4-power.md#2026-05-20--hw-bom-assets-002-bom-ingest-bom-confirmed-part-identity-reclassified-package-header-cleanup-still-deferred)
  and [`docs/cleanup-audit.md` §HW-BOM-ASSETS-002 update](../cleanup-audit.md#hw-bom-assets-002-update-2026-05-20--s360-400--s360-410-bom-evidence-ingest).
- **2026-05-20 — `PACKAGE-POWER-400-001` package-header cleanup
  (Path B / limited implementation).** Now that
  `HW-BOM-ASSETS-002` / PR #535 BOM-confirmed
  `PS1 = HLK-5M05` (HI-LINK), the comment-only header cleanup
  that PR #515 and PR #520 deferred has landed against
  [`packages/hardware/power_240v.yaml`](../../packages/hardware/power_240v.yaml).
  The header at lines 1–42 now records the BOM-confirmed part
  identity (`PS1 = HLK-5M05 (HI-LINK)`), the BOM-confirmed
  populated mains-side protection components
  (`F1 A250-1200` polyfuse, `RV1 10D391K` MOV, `C1 470nF` X-cap),
  and the BOM-confirmed connectors (`J1` WAGO 2601-3103 1×3
  terminal block, `J2` JST SH `SM02B-SRSS-TB(LF)(SN)` 1×2
  Core-facing output). Input / output / isolation / protection
  ratings are reclassified under an explicit "Vendor-datasheet
  typicals (NOT BOM-confirmed and NOT compliance evidence)"
  heading. The misleading `1A recommended` AC-input fusing line
  that disagreed with the on-board `F1 A250-1200` polyfuse class
  is **removed**; the safety-notes block now points at the
  populated `F1 A250-1200` polyfuse plus `RV1` / `C1` as the
  on-board mains-side fault protection. The header also restates
  that mains-voltage UK / EU compliance is tracked by
  COMPLIANCE-001 and remains **OPEN**, and that no CE / UKCA /
  FCC / UL / LVD / EMC / RoHS / IEC claim is made by this
  package. **Runtime YAML blocks are preserved byte-for-byte** —
  the `substitutions: power_source: "240v_ac"`,
  `globals: power_source_type`, the four template diagnostic
  sensors (`Supply Voltage` / `Power Source` /
  `Power Configuration` / `AC Power Connected`), and the
  `logger` block from line 44 onward are byte-identical to
  PR #515 / PR #520 / PR #535 state. The row above **stays**
  `schematic-evidence-pending` + `needs-package-reconciliation`
  + `timing/compliance-pending` (compliance-gated); Path B is a
  limited slice and does **not** flip the class. The catalog
  `description` is already BOM-consistent and is unchanged
  ([`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  `S360-400` row byte-identical;
  `description: Mains to 5V using HLK-5M05.` at line 109 and
  `schematic_status: cataloged_unverified` at line 110 stay as
  they were). The residual coordinated `PACKAGE-POWER-400-001`
  work is the `S360-400` `schematic_status: verified` JSON-only
  PR (additionally gated on the schematic-side correction of the
  committed PDF's `PS1 = HLK-10M05` value-field string), the
  `COMPLIANCE-001` `S360-400` slice closure, and the silkscreen
  / PCB / creepage / clearance / bench / thermal / EMI evidence.
  `PRODUCT-POWER-400-001`, `WEBFLASH-POWER-400-001`,
  `RELEASE-POWER-400-001`, and `WF-IMPORT-POWER-400-001`
  (cross-repo) stay blocked on their other recorded
  preconditions; Release-One stays
  `Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`; LED preview
  stays `Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`; FanTRIAC
  stays `blocked` / `HW-005`; the four `legacy-compatible`
  `*-pwr` Core variants stay `legacy-compatible` /
  `webflash_build_matrix: false`. Outcome recorded at
  [`s360-400-r4-power.md` §2026-05-20 — PACKAGE-POWER-400-001 package-header cleanup](s360-400-r4-power.md#2026-05-20--package-power-400-001-package-header-cleanup-bom-confirmed-part-identity-in-header-ratings-softened-downstream-slices-still-blocked)
  and [`docs/cleanup-audit.md` §PACKAGE-POWER-400-001 update (2026-05-20 — Path B package-header cleanup)](../cleanup-audit.md#package-power-400-001-update-2026-05-20--path-b-package-header-cleanup).

### `power_poe.yaml` / S360-410

- **Status.** `reference-only` (logical, no GPIO binding) +
  `schematic-evidence-pending` (schematic landed under
  HW-ASSETS-410 / PR #516 and was consumed by
  HW-PINMAP-410-FOLLOWUP; package-header reconciliation still
  owed) + `do-not-change-release-one`.
- **What is wrong (or, more accurately, what is unproven).**
  [`power_poe.yaml`](../../packages/hardware/power_poe.yaml) is a
  logical PoE-power package emitting diagnostic sensors only; it
  binds no GPIOs. HW-009 classifies it `confirmed-ok` at the
  abstraction layer. The PoE-module part identity (`Ag9712M` /
  `Silvertel Ag9700` / `or similar` — whole-module hint) **disagrees
  with the schematic-shown discrete topology** (`TPS2378DDAR(HSOIC-8)`
  PoE PD controller + `TX4138(ESOIC-8)` buck + `F0505S-2WR2(SIP-7)`
  isolated DC/DC, with `AM1D-0505S-NZ` annotated as alternate, +
  `RJP-003TC1(LPJ4112CNL)` magnetics) committed under HW-ASSETS-410
  / PR #516. HW-PINMAP-410-FOLLOWUP recorded the disagreement as
  **unresolved** — BOM evidence is required before
  `PACKAGE-POE-410-001` can resolve the part identity. The IEEE
  802.3af / 802.3at class assertion, the input range (`36-57V DC`),
  the output rating (`5V DC, 2A (10W)` or `3.3V DC`), and the
  protection claims are package-header text — partially schematic-
  evidenced (the schematic-visible `Class=0 (0.44 to 12.95W)`
  annotation matches the `Class 0` half of the header hint; the
  `or Class 1` / 802.3at-capable / 3.3 V output / OCP-OVP-SCP
  assertions are not schematic-evidenced; whether the design is
  802.3af-only or 802.3af/at-capable is BOM-bound). Core `J2` PoE
  harness identity is HW-002 Open Question #6; tracked under
  [S360-100-BENCH-001](s360-100-r4-core.md#s360-100-bench-001-status),
  `pending — bench/manufacturing evidence required`. Release-One
  consumes this package today under the documented
  "schematic verification pending" caveat in
  [`release-one-hardware-audit.md` Findings → PoE PSU](../release-one-hardware-audit.md#findings),
  which is **preserved verbatim** here and **not** promoted away.
  PoE is SELV; **not** in scope for COMPLIANCE-001.
- **Allowed action now.** None. The logical role is consumed by
  Release-One; PACKAGE-GAP-001 does not authorise changes to
  Release-One package semantics. Comment-only cleanup of the
  stale `Ag9712M / Silvertel Ag9700 / or similar` header is
  **deferred to `PACKAGE-POE-410-001`** once BOM evidence lands,
  per the brief's evidence standards ("BOM is required to resolve
  part number / rating disputes") — the same rule HW-PINMAP-400-FOLLOWUP
  applied to [`packages/hardware/power_240v.yaml`](../../packages/hardware/power_240v.yaml).
- **Follow-up owner.** `HW-ASSETS-410` (supplier-side schematic
  delivery — merged as PR #516) → `HW-PINMAP-410-FOLLOWUP`
  (schematic-backed reconciliation; this matrix's row is updated
  by this PR) → BOM cross-check → `HW-002 OQ#6` closure /
  `S360-100-BENCH-001` update (bench evidence) → `S360-410`
  `schematic_status: verified` JSON-only PR (after BOM + HW-002
  OQ#6 closure) → `PACKAGE-POE-410-001` / `PACKAGE-GAP-001` PoE
  slice → separate later Release-One caveat-closure PR (the
  caveat is **not** closed by this matrix or by the slice PR
  alone).
- **Cross-references.** [`s360-410-r4-poe.md` Follow-up PR sequence](s360-410-r4-poe.md#follow-up-pr-sequence);
  [`s360-410-r4-poe.md` HW-PINMAP-410-FOLLOWUP audit log](s360-410-r4-poe.md#hw-pinmap-410-followup-audit-log);
  [`board-readiness-matrix.md` `S360-410` notes](board-readiness-matrix.md#s360-410-sense360-poe-psu);
  [`release-one-hardware-audit.md` Findings → PoE PSU](../release-one-hardware-audit.md#findings).
- **2026-05-20 — `PACKAGE-POE-410-001` investigation pass addendum
  (docs-only deferral).** The 2026-05-20
  `PACKAGE-POE-410-001` investigation pass re-verified all five
  preconditions (BOM cross-check; `S360-410`
  `schematic_status: verified` JSON PR; HW-002 OQ#6 /
  `S360-100-BENCH-001` J2-harness closure; package-header
  reconciliation against the schematic-shown discrete topology;
  Release-One PoE caveat closure as a separate later PR) remain
  open and confirmed deferral. [`power_poe.yaml`](../../packages/hardware/power_poe.yaml)
  stays byte-identical to PR #517 state (the stale `Ag9712M,
  Silvertel Ag9700, or similar` line at line 6, the
  `IEEE 802.3af (PoE) or 802.3at (PoE+)` standard line at
  line 7, the `Class 0 (0.44-12.95W) or Class 1 (0.44-3.84W)`
  class line at line 8, the `36-57V DC` input line at line 9,
  the `5V DC, 2A (10W) or 3.3V DC` output line at line 10, the
  `Overcurrent, overvoltage, short-circuit` protection line at
  line 11, the substitutions / globals / sensors / logger /
  on_boot blocks all preserved); the package binds **no** GPIO
  / I²C / UART / SPI / DAC / runtime hardware. The three-way
  catalog [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  `description: "PoE to 5V."` (line 119) vs package header
  `Ag9712M, Silvertel Ag9700, or similar` (line 6) vs schematic
  discrete topology (`TPS2378DDAR + TX4138 + F0505S-2WR2 +
  RJP-003TC1(LPJ4112CNL)`) part-identity disagreement therefore
  stays unresolved and remains BOM-bound — the same evidence-
  standards rule HW-PINMAP-400-FOLLOWUP / PR #515 + PR #520
  applied to the parallel
  [`power_240v.yaml`](../../packages/hardware/power_240v.yaml)
  slice. The row above stays
  `reference-only` + `schematic-evidence-pending` +
  `do-not-change-release-one`; no row-status change. PoE is
  SELV; **not** in scope for COMPLIANCE-001. Investigation
  outcome recorded at
  [`s360-410-r4-poe.md` §2026-05-20 — PACKAGE-POE-410-001 investigation pass](s360-410-r4-poe.md#2026-05-20--package-poe-410-001-investigation-pass)
  and [`docs/cleanup-audit.md` §PACKAGE-POE-410-001 update](../cleanup-audit.md#package-poe-410-001-update-2026-05-20--docs-only-investigation-pass).
- **2026-05-20 — `HW-BOM-ASSETS-002` BOM-evidence ingest addendum
  (record-only).** The `HW-BOM-ASSETS-002` record-only BOM ingest
  landed the `S360-410-R4_BOM.xlsx`
  (`0de7679d-S360410R4_BOM.xlsx`; 11,980 bytes; SHA256
  `b5f4bad842a930de03cd47327f477c21afcb82e4533a9d8be38b54990b38f285`)
  as retained-but-not-committed evidence inventoried at
  [`docs/hardware/artifacts/S360-410-R4.md` §HW-BOM-ASSETS-002 BOM ingest (2026-05-20)](artifacts/S360-410-R4.md#hw-bom-assets-002-bom-ingest-2026-05-20).
  The accompanying PDF re-upload (`7f920771-S360410R4.pdf`;
  975,137 bytes; SHA256
  `4a8b7a3b2a89006a9332eaa486743f687aaedc4b6bb807c6b25670f742ac2414`)
  is **byte-identical** to the committed
  [`docs/hardware/schematics/S360-410-R4.pdf`](schematics/S360-410-R4.pdf)
  (HW-ASSETS-410 / PR #516); no re-commit. The BOM confirms each
  load-bearing schematic part with manufacturer attribution
  (`U1 TPS2378DDAR` TI; `U2 TX4138` XDS; `DCDC1 F0505S-2WR2`
  EVISUN; `LAN_CON1 LPJ4112CNL` Link-PP) and **reclassifies**
  the package-header / schematic disagreement above:
  schematic-shown discrete topology (`TPS2378DDAR + TX4138 +
  F0505S-2WR2 + RJP-003TC1(LPJ4112CNL)`) = BOM-confirmed
  sourcing truth; package-header whole-module hint `Ag9712M /
  Silvertel Ag9700 / or similar`
  ([`packages/hardware/power_poe.yaml`](../../packages/hardware/power_poe.yaml)
  line 6) = disproved package-header comment text (neither part
  is in the BOM), comment-only cleanup deferred to
  `PACKAGE-POE-410-001`; schematic-annotated `AM1D-0505S-NZ` =
  schematic-annotation-only alternate not present in the BOM
  (`F0505S-2WR2` EVISUN is the BOM-confirmed populated primary
  for `DCDC1`); catalog `description: "PoE to 5V."` carries no
  part identity and is unchanged. PoE class declaration: BOM
  `R2 1.27k` (PANASONIC `ERJ2RKF1301X`) is consistent with the
  schematic-recorded `Class=0 (0.44 to 12.95W)` programming;
  802.3af-only vs 802.3af/at-capable design intent stays open.
  Output rating: BOM `DCDC1 F0505S-2WR2` + BOM `R7 10.5k` /
  `R8 56.2k` feedback divider are consistent with the
  schematic-recorded 5 V → 5 V isolated output only; the
  package-header `or 3.3V DC` option is not schematic- or
  BOM-evidenced.
  [`packages/hardware/power_poe.yaml`](../../packages/hardware/power_poe.yaml)
  stays **byte-identical to PR #517 / PR #526** (the stale
  `Ag9712M, Silvertel Ag9700, or similar` line at line 6, the
  IEEE 802.3af / 802.3at standard line at line 7, the Class 0 /
  Class 1 line at line 8, the 36–57 V DC input line at line 9,
  the 5 V / 3.3 V output line at line 10, the OCP / OVP / SCP
  protection line at line 11, the substitutions / globals /
  template sensors / logger / on_boot blocks all preserved); the
  package binds **no** GPIO / I²C / UART / SPI / DAC / runtime
  hardware.
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  `S360-410` row at lines 112–120 stays byte-identical (no
  `schematic_status` promotion, no `schematic_file` set; PoE is
  SELV and `S360-410` is **not** in scope for COMPLIANCE-001).
  Other BOM-confirmed component identities: `R1 24.9k` (EVER
  OHMS) DEN; `R3, R4 9.1k` (UNI-ROYAL) paired ILIM; `R5 0.03R`
  (YAGEO) RTN sense; `R7 10.5k` (KOA) `Rd` / `R8 56.2k` (FOJAN)
  `Rc` feedback divider; `L1 33uH` (Yanchuang); `D1 SMAJ58A`
  (Littelfuse) TVS; `D2 ss510` (MDD SS510C) Schottky; `D3 Green`
  (Orient) indicator; `C2 15uF` (Rubycon) CBULK; `C6 470u`
  (ROQANG) buck-output bulk; `C8 22u` (muRata) `+5VP` output
  bulk; `J3` JST `SM02B-SRSS-TB(LF)(SN)` 1×2 Core-facing
  connector. Per-component tolerance / power-rating evidence
  beyond the BOM strings, silkscreen pin-1 markers on `J3`,
  KiCad PCB source / gerbers for isolation-barrier widths and
  `H1`–`H4` PCB bonding to `Lan_earth` / RJ45 shield, PoE
  link-up / signature / classification / load regulation /
  cold-start inrush / thermal rise / insulation resistance /
  Hi-pot / earth-continuity / leakage / EMI / EMC measurements,
  IEEE 802.3af / 802.3at compliance test reports, and the
  `F0505S-2WR2`-vs-`AM1D-0505S-NZ` primary-vs-alternate intent
  resolution are all bench / silkscreen / vendor-datasheet
  evidence and are **not** resolved by this ingest. The row
  above stays `reference-only` +
  `schematic-evidence-pending` + `do-not-change-release-one`;
  no row-status change. The Release-One PoE `"schematic
  verification pending"` caveat at
  [`docs/release-one-hardware-audit.md` Findings → PoE PSU](../release-one-hardware-audit.md#findings)
  is **preserved verbatim**. The `BOM cross-check missing`
  precondition listed under `PACKAGE-POE-410-001` /
  `PRODUCT-POE-410-001` / `WEBFLASH-POE-410-001` /
  `RELEASE-POE-410-001` is now **resolved at the
  discrete-topology part-identity layer**; each slice stays
  blocked on its other recorded preconditions (the `S360-410`
  `schematic_status: verified` JSON PR; HW-002 OQ#6 /
  `S360-100-BENCH-001` J2-harness closure; the package-header
  comment cleanup itself; the Release-One PoE caveat closure as
  a separate later PR; product-onboarding approval where
  applicable; UX-class decision where applicable; the eight
  release-time sub-gates where applicable). PoE is SELV;
  **not** in scope for COMPLIANCE-001. Investigation outcome
  recorded at
  [`s360-410-r4-poe.md` §2026-05-20 — HW-BOM-ASSETS-002 BOM ingest](s360-410-r4-poe.md#2026-05-20--hw-bom-assets-002-bom-ingest-bom-confirmed-part-identity-reclassified-package-header-cleanup-still-deferred)
  and [`docs/cleanup-audit.md` §HW-BOM-ASSETS-002 update](../cleanup-audit.md#hw-bom-assets-002-update-2026-05-20--s360-400--s360-410-bom-evidence-ingest).

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
| `PACKAGE-DAC-001-IMPLEMENT-001` (was `PACKAGE-DAC-001`) | done (HW-ASSETS-003) | `HW-PINMAP-312-FOLLOWUP` standalone reference doc *(landed 2026-05-22 at [`s360-312-r4-fandac.md`](s360-312-r4-fandac.md))* + `PACKAGE-DAC-001-READINESS-REFRESH` *(landed 2026-05-22 — this PR; [`s360-312-r4-fandac.md` §PACKAGE-DAC-001 readiness refresh](s360-312-r4-fandac.md#package-dac-001-readiness-refresh))* + `HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001` *(landed 2026-05-22 — closed rows 3 / 6 / 8 of the readiness refresh via the GP8403 datasheet + Drive KiCad PCB / gerber / render assets + operator decisions)* | `S360-312` `schematic_status` promotion (separate JSON PR) | **rows 3 / 6 / 8 satisfied** by `HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001` (row 3 — GP8403 datasheet `A0`/`A1`/`A2` bit ordering + base `0x58` + KiCad PCB pole→pin map; row 6 — operator per-chip range policy + register-`0x01` mechanism; row 8 — `J2` / `J3` PCB + silkscreen pin-1 identity, `VOUT0` / `GND` / `VOUT1` order, `J3` silk transposition flagged) and row 4 (two chips / four outputs) by operator decision. Remaining = row 10 (the YAML edit itself = `PACKAGE-DAC-001-IMPLEMENT-001`). Residual product / bench items do **not** block the package YAML: Cloudlift S12 harness conductor trace, operator / bench confirmation of the `J3` silk transposition, as-shipped DIP default, and the Core `J7` vs Module `J1` rail silkscreen (`S360-100-BENCH-001` parallel track); row 9 UART0-vs-Nextion arbitration stays deferred to a future product slice. | not applicable | resolved at the shared-I²C-bus-naming layer by `CORE-ABSTRACT-BUS-001B-IMPLEMENT-001` (PR #569); active YAML now inherits `${fan_dac_i2c_id}: core_i2c` |
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
| **`PACKAGE-RELAY-001`** (alias: `PACKAGE-GAP-001` FanRelay slice) | **Investigated and deferred** — readiness gates are not satisfied. Would reconcile [`packages/expansions/fan_relay.yaml`](../../packages/expansions/fan_relay.yaml) and the Core abstract packages' `relay_pin` value(s) against the now-verified schematic evidence. Would decide whether `fan_relay_pin: ${relay_pin}` is the right abstraction or whether the package should bind an explicit module-side connector pin. Until the gates clear, the only PACKAGE-RELAY-001 work recorded in this repo is the docs-only deferral note in [`docs/cleanup-audit.md` §PACKAGE-RELAY-001 update](../../docs/cleanup-audit.md#package-relay-001-update-deferred--core-abstract-bus-001--silkscreen--harness--k1-bom-evidence-not-landed); [`packages/expansions/fan_relay.yaml`](../../packages/expansions/fan_relay.yaml) is unchanged (`fan_relay_pin: ${relay_pin}` line 27, override-hook comment lines 22–25, `switch.platform: gpio` with `pin: ${fan_relay_pin}` line 38, `restore_mode: RESTORE_DEFAULT_OFF`, `fan_auto_mode` global, `fan_emergency_stop` script all preserved), and the Core abstract packages [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml) (`relay_pin: GPIO4`) and [`packages/hardware/sense360_core.yaml`](../../packages/hardware/sense360_core.yaml) (`relay_pin: GPIO10`) are also unchanged. The `IO3` (Core schematic) vs `GPIO4` vs `GPIO10` `relay_pin` resolution stays owned by `CORE-ABSTRACT-BUS-001`, not by PACKAGE-RELAY-001. | `HW-ASSETS-310` + `HW-PINMAP-310-FOLLOWUP` + `S360-310` `schematic_status: verified` + bench / silkscreen evidence + `CORE-ABSTRACT-BUS-001`. |
| **`PACKAGE-PWM-001`** (alias: `PACKAGE-GAP-001` FanPWM slice) | Reconcile [`packages/expansions/fan_pwm.yaml`](../../packages/expansions/fan_pwm.yaml) (and decide the fate of the legacy four-channel [`packages/expansions/sense360_fan_pwm.yaml`](../../packages/expansions/sense360_fan_pwm.yaml)) against the now-verified schematic evidence: single-channel vs four-channel canonical abstraction; SX1509-channel vs direct-ESP32 binding decision; PWM polarity / frequency decision; tach polarity / pull-up / pulses-per-revolution decision; UART-on-`J3`-pins-11/12 resolution. | `HW-PINMAP-311-FOLLOWUP` + `S360-311` `schematic_status: verified` + bench / silkscreen evidence. `CORE-ABSTRACT-BUS-001B` no longer blocks this slice at the shared-I²C-bus layer — the rename to `core_i2c` landed via `CORE-ABSTRACT-BUS-001B-IMPLEMENT-001`, so the `sx1509_i2c_id: core_i2c` default in the SX1509 expander package no longer needs further work for FanPWM consumers. **`PACKAGE-PWM-001` is still blocked** on the FanPWM-specific evidence enumerated above. |
| **`PACKAGE-DAC-001-IMPLEMENT-001`** (alias: `PACKAGE-GAP-001` FanDAC slice; was `PACKAGE-DAC-001` before the 2026-05-22 readiness refresh split out a docs-only `PACKAGE-DAC-001-READINESS-REFRESH` and recommended a DAC address / range / silkscreen evidence PR as the next step) | Reconcile [`packages/expansions/fan_gp8403.yaml`](../../packages/expansions/fan_gp8403.yaml) against the now-verified schematic evidence: at minimum delete or correct the stale `"(jumper selectable on hardware)"` comment at file line 6, decide the `${fan_dac_address}` allowed-values set against the DIP-switch ↔ I²C-address truth table, decide the package-design shape (one logical FanDAC, two channels vs two GP8403 devices each with its own `${fan_dac_address*}` / `${fan_dac_voltage_mode*}` vs four logical outputs), decide whether to add a Nextion `display:` or `uart:` binding on the `UART_RX` / `UART_TX` pair (note: row 9 of the readiness refresh defers this to `PRODUCT-DAC-001` scope), decide the canonical single- vs dual-channel abstraction (the active YAML is already dual-channel and matches the schematic for `IC1`). | `HW-PINMAP-312-FOLLOWUP` + `PACKAGE-DAC-001-READINESS-REFRESH` (this PR; landed 2026-05-22; [`s360-312-r4-fandac.md` §PACKAGE-DAC-001 readiness refresh](s360-312-r4-fandac.md#package-dac-001-readiness-refresh)) + `HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001` *(landed 2026-05-22)* closing rows 3 (GP8403 datasheet `A0`/`A1`/`A2` bit ordering + base `0x58` + KiCad PCB pole→pin map), 6 (operator per-chip output-range policy + register-`0x01` mechanism), and 8 (`J2` / `J3` PCB + silkscreen pin-1 identity) of [`s360-312-r4-fandac.md` §PACKAGE-DAC-001 readiness refresh](s360-312-r4-fandac.md#package-dac-001-readiness-refresh) + `S360-312` `schematic_status: verified` (separate JSON PR). `CORE-ABSTRACT-BUS-001B` no longer blocks this slice at the shared-I²C-bus layer — the rename to `core_i2c` landed via `CORE-ABSTRACT-BUS-001B-IMPLEMENT-001`, so the `fan_dac_i2c_id: core_i2c` default in `fan_gp8403.yaml` (and the inherited `FanDAC` alias `packages/expansions/fan_dac.yaml`) no longer needs further work to bind the schematic-correct Core I²C bus. With rows 3 / 6 / 8 closed by `HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001` (2026-05-22), **`PACKAGE-DAC-001-IMPLEMENT-001` is now implementation-plannable** — only row 10 (the YAML edit itself: bind two GP8403s, per-chip address + range substitutions, four outputs, corrected jumper comment) remains. Residual product / bench items (Cloudlift S12 harness conductor trace, operator / bench confirmation of the `J3` `out0`/`out1` silk transposition, as-shipped DIP default, `J1` / `J7` `+3.3 V` / `+5 V` rail via `S360-100-BENCH-001`) are tracked separately and do **not** block the package YAML. |
| **`PACKAGE-TRIAC-001`** (alias: `PACKAGE-GAP-001` FanTRIAC slice) | **Investigated and deferred** — readiness gates are not satisfied. Would reconcile [`packages/expansions/fan_triac.yaml`](../../packages/expansions/fan_triac.yaml) against the now-verified schematic + verified direct-ESP32 pin pair: remove the BLOCKED / UNVERIFIED banner **only** if HW-005 and the timing-correctness gate justify it; retain the mains-voltage / qualified-electrician warnings; leave the `ac_dimmer` topology intact (if confirmed correct); add the advanced / manual-warning posture wording per [`s360-320-r4-triac.md` Advanced / manual-warning product posture](s360-320-r4-triac.md#advanced--manual-warning-product-posture). **Must not** add FanTRIAC to Release-One, REQUIRED_CONFIGS, kit / default lists, recommended surfaces, or compliance-certified surfaces. Until the gates clear, the only PACKAGE-TRIAC-001 work recorded in this repo is the docs-only deferral note in [`docs/cleanup-audit.md` §PACKAGE-TRIAC-001 update](../cleanup-audit.md#package-triac-001-update-deferred--hw-005--hw-pinmap-320-followup--compliance-001-not-landed); the package YAML itself is unchanged (BLOCKED / UNVERIFIED banner, `ac_dimmer` topology, substitutions, mains-voltage / qualified-electrician warnings all preserved). `WF-TRIAC-001` having landed in the WebFlash repo (runtime advanced / manual-warning UX gate) does **not** satisfy these package-layer gates. After PACKAGE-TRIAC-001 deferral, the downstream `PRODUCT-TRIAC-002`, in-repo `WF-TRIAC-001` wrapper / catalog / build slice, `RELEASE-TRIAC-001`, and `WF-IMPORT-TRIAC-001` slices remain blocked until `HW-005` + `HW-PINMAP-320-FOLLOWUP` + bench / waveform / real-load evidence + `COMPLIANCE-001` evidence lands; see [`docs/cleanup-audit.md` §TRIAC-QUEUE-001 update](../cleanup-audit.md#triac-queue-001-update-remaining-fantriac-chain-normalized-after-package-deferral). | `HW-005` unblock (Option (a) direct-ESP32 pair or Core respin) + `HW-PINMAP-320-FOLLOWUP` + bench timing / waveform / real-load evidence + `COMPLIANCE-001` advanced/manual-warning sign-off. |
| **`PACKAGE-POWER-400-001`** (alias: `PACKAGE-GAP-001` PWR slice) | Reconcile [`packages/hardware/power_240v.yaml`](../../packages/hardware/power_240v.yaml) header claims (AC-DC part identity `HLK-5M05` vs `HLK-PM01 or similar`, input / output / isolation / protection ratings) against the now-verified schematic and module BOM. | `HW-ASSETS-400` + `HW-PINMAP-400-FOLLOWUP` + `S360-400` `schematic_status: verified` + module BOM cross-check. (Product / WebFlash promotion remains separately gated by `COMPLIANCE-001` `S360-400` slice.) |
| **`PACKAGE-POE-410-001`** (alias: `PACKAGE-GAP-001` PoE slice) | Reconcile [`packages/hardware/power_poe.yaml`](../../packages/hardware/power_poe.yaml) header claims (PoE module part identity, standard / class, input / output / protection ratings) against the now-verified schematic and module BOM. **Does not** by itself close the Release-One "schematic verification pending" caveat in [`release-one-hardware-audit.md` Findings → PoE PSU](../release-one-hardware-audit.md#findings); that closure is a separate later PR per [`s360-410-r4-poe.md` Follow-up PRs](s360-410-r4-poe.md#follow-up-prs). | `HW-ASSETS-410` + `HW-PINMAP-410-FOLLOWUP` + `S360-410` `schematic_status: verified` + `HW-002 OQ#6` closure / `S360-100-BENCH-001` update. |
| **`CORE-ABSTRACT-BUS-001`** (alias for [`release-one-hardware-audit.md` Required follow-ups #2 / #3](../release-one-hardware-audit.md#required-follow-ups)) | **Investigated** as a docs-only audit / slice plan at [`core-abstract-bus-reconciliation.md`](core-abstract-bus-reconciliation.md). The audit inventoried every Core abstract substitution across the six Core packages ([`sense360_core.yaml`](../../packages/hardware/sense360_core.yaml), [`sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml), [`sense360_core_ceiling_s3.yaml`](../../packages/hardware/sense360_core_ceiling_s3.yaml), [`sense360_core_mapping.yaml`](../../packages/hardware/sense360_core_mapping.yaml), [`sense360_core_poe.yaml`](../../packages/hardware/sense360_core_poe.yaml), [`sense360_core_wall.yaml`](../../packages/hardware/sense360_core_wall.yaml)), classified each against the verified `S360-100-R4` schematic, and split the implementation into three coordinated slices: **`CORE-ABSTRACT-BUS-001A`** (`relay_pin → GPIO3` across all Core packages), **`CORE-ABSTRACT-BUS-001B`** (consolidate `halo_i2c` + `expansion_i2c` + `i2c0` / `i2c1` / `i2c_primary` / `i2c_expander` definitions to the single shared I²C bus on `IO48`/`IO45`), and **`CORE-ABSTRACT-BUS-001C`** (UART split into `roomiq_hi_link_uart` / `roomiq_sen0609_uart`, status LED move off `GPIO48`, `pir_sensor_pin: GPIO47 → GPIO15`, `comfort_ceiling_als_int_pin: GPIO3 → GPIO47`, `expander_int_pin: GPIO3 → GPIO17`, `sx1509_interrupt_pin: GPIO3 → GPIO17`, `expansion_gpio1..4` rebind). The audit also surfaces a GPIO3 collision that requires `001C` to land at-or-before `001A`, and a per-Core-package blast radius of consuming product YAMLs (Release-One [`sense360-ceiling-poe-ventiq-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq.yaml), LED preview [`sense360-ceiling-poe-ventiq-roomiq-led.yaml`](../../products/sense360-ceiling-poe-ventiq-roomiq-led.yaml), FanTRIAC reference [`sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml), and ~25 other product YAMLs). Records that `S360-100-BENCH-001` silkscreen evidence, ESP32-S3 `GPIO3` strap-pin boot-behaviour bench characterisation, RoomIQ / AirIQ / VentIQ rebind plan, and re-validation pass remain prerequisites. Independently drives the resolution of the Core J10 vs RoomIQ J6 pin-order silkscreen check. Must re-validate every non-Release-One product YAML that consumes any affected Core abstract package. | Core J10 vs RoomIQ J6 silkscreen verification (S360-100-BENCH-001 evidence) + RoomIQ / AirIQ / VentIQ package rebind plan + ESP32-S3 `GPIO3` strap-pin boot-behaviour bench characterisation + re-validation pass + `tests/test_core_abstract_bus.py` scaffolding. **Owned by [`release-one-hardware-audit.md` Required follow-ups #2 / #3](../release-one-hardware-audit.md#required-follow-ups), not by PACKAGE-GAP-001.** Per-slice gates recorded in [`core-abstract-bus-reconciliation.md` Implementation slice definitions](core-abstract-bus-reconciliation.md#implementation-slice-definitions) and [§Required evidence before any slice can land](core-abstract-bus-reconciliation.md#required-evidence-before-any-slice-can-land). A `CORE-ABSTRACT-BUS-001C` investigation pass ran on 2026-05-19 and is **confirmed deferred** — all six preconditions (`S360-100-BENCH-001` silkscreen evidence, RoomIQ / AirIQ / VentIQ rebind plan, expansion-GPIO bench evidence or documented retirement decision, ESP32-S3 `GPIO3` strap-pin boot-behaviour bench characterisation, `tests/test_core_abstract_bus.py` scaffold, and the non-Release-One product re-validation pass) remain open; see [`core-abstract-bus-reconciliation.md` §CORE-ABSTRACT-BUS-001 audit log](core-abstract-bus-reconciliation.md#core-abstract-bus-001-audit-log) and [`docs/cleanup-audit.md` §CORE-ABSTRACT-BUS-001C update](../cleanup-audit.md#core-abstract-bus-001c-update-2026-05-19--docs-only-investigation-pass). No `CORE-ABSTRACT-BUS-001*` slice has changed status as a result. **Update (2026-05-22):** `CORE-ABSTRACT-BUS-001C` landed via PR #557, `CORE-ABSTRACT-BUS-001A` landed via PR #558, and `CORE-ABSTRACT-BUS-001B` landed via `CORE-ABSTRACT-BUS-001B-IMPLEMENT-001` (this PR) as the hard rename to the canonical shared `core_i2c` bus id (`GPIO48` SDA / `GPIO45` SCL / `400kHz`) across the seven in-scope Core abstract packages, the 10 in-scope expansion-package consumer defaults, the hard-coded `packages/features/ceiling_halo_leds.yaml` literal, the `tests/generate_test_configs.py` per-product override, and the new `SharedI2CBusTests` (13 cases) in `tests/test_core_abstract_bus.py`. All three slices are now at the substitution layer. `PACKAGE-PWM-001` and `PACKAGE-DAC-001` are unblocked only at the shared-I²C-bus layer; both still require their own per-board evidence and BOM cross-checks per the rows immediately below this one. |

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

# Upcoming PRs — esphome-public

This document is the working queue source of truth for `sense360store/esphome-public`
PR work. It tracks upcoming, blocked, deferred, and completed PRs that are
owned by this repository. WebFlash-owned import/runtime work is tracked in
the WebFlash repository's `UPCOMING_PR.md`; only cross-repo dependencies are
mirrored here.

## Maintenance rule

- Update this file in every PR that changes queue state.
- When a PR merges, record the PR number and status in the
  **Completed / merged PRs** table.
- When a PR is deferred, record the blocker (which evidence, which upstream
  PR, or which gating audit must land first).
- When new evidence arrives (schematic PDF, bench result, compliance
  sign-off, etc.), update the relevant evidence item in
  **Recently uploaded evidence** and, if it unblocks a queued PR, update the
  queue row.
- Keep WebFlash-owned import/runtime rows (the `WF-IMPORT-*` series and other
  WebFlash-runtime work) **out of this repo**. Mirror them only under
  **Cross-repo dependencies** so cross-repo coupling stays visible without
  duplicating ownership.

## Current queue summary

- Relay artifact and pinmap work advanced through **HW-ASSETS-310**,
  **HW-PINMAP-310-FOLLOWUP**, and **PACKAGE-RELAY-001**. The S360-310
  schematic is now committed and the Relay pin/package audit is
  schematic-backed partial.
- **PACKAGE-RELAY-001** was a docs-only deferral. `packages/expansions/fan_relay.yaml`
  did not change in that PR.
- **CORE-ABSTRACT-BUS-001** has now been investigated as a
  docs-only audit + slice plan (see
  `docs/hardware/core-abstract-bus-reconciliation.md`). The audit
  splits the systemic Core abstract-bus rebind into three coordinated
  future implementation slices: **CORE-ABSTRACT-BUS-001A**
  (`relay_pin → GPIO3` across all Core abstract packages),
  **CORE-ABSTRACT-BUS-001B** (consolidate `halo_i2c` /
  `expansion_i2c` / `i2c0` / `i2c1` / `i2c_primary` / `i2c_expander`
  definitions to the single shared I²C bus on `IO48`/`IO45`), and
  **CORE-ABSTRACT-BUS-001C** (UART split into `roomiq_hi_link_uart`
  / `roomiq_sen0609_uart`, status LED move off `GPIO48`,
  `pir_sensor_pin: GPIO47 → GPIO15`,
  `comfort_ceiling_als_int_pin: GPIO3 → GPIO47`,
  `expander_int_pin: GPIO3 → GPIO17`,
  `sx1509_interrupt_pin: GPIO3 → GPIO17`, `expansion_gpio1..4`
  rebind). The audit surfaces a GPIO3 collision (the
  schematic-correct `relay_pin: GPIO3` collides with the existing
  `comfort_ceiling_als_int_pin: GPIO3` that Release-One consumes via
  `comfort_ceiling.yaml`), so **001C must land at-or-before 001A**.
- The next Relay implementation blocker is therefore
  **CORE-ABSTRACT-BUS-001A** specifically (depends on
  **CORE-ABSTRACT-BUS-001C**), not the generic CORE-ABSTRACT-BUS-001
  umbrella. Relay package implementation cannot safely proceed until
  001A lands together with S360-100-BENCH-001 silkscreen evidence,
  ESP32-S3 `GPIO3` strap-pin boot-behaviour bench characterisation,
  silkscreen / harness / `K1` BOM evidence for `S360-310`, and a new
  pin-pinning test scaffold (`tests/test_core_abstract_bus.py`).
- **HW-ASSETS-400** merged as **PR #514** and landed the
  `S360-400-R4` schematic PDF at
  `docs/hardware/schematics/S360-400-R4.pdf` (byte-identical to the
  upload; 461,206 bytes; SHA256
  `295e3ec9192603fd4ca7d89b8cda68777e5cb8e9713ed8b0fba2316babb0e765`)
  and the curated artifact index at
  `docs/hardware/artifacts/S360-400-R4.md`. No `schematic_status`
  promotion, no `schematic_file` set, no package / product / WebFlash
  / build / release / import edit, no COMPLIANCE-001 movement.
- **HW-PINMAP-400-FOLLOWUP** merged as **PR #515** and consumed
  the HW-ASSETS-400 schematic evidence; promoted
  `docs/hardware/s360-400-r4-power.md` from
  `pending — schematic/design evidence required` to
  `partial — schematic evidence available; package reconciliation,
  BOM, silkscreen, creepage/clearance, and COMPLIANCE-001 pending`.
  Recorded the three-way AC/DC part-identity disagreement (catalog
  `HLK-5M05` vs package header `HLK-PM01 or similar` vs schematic
  `HLK-10M05`) as unresolved (BOM-bound). `packages/hardware/power_240v.yaml`
  stayed byte-identical; comment-only cleanup deferred to
  `PACKAGE-POWER-400-001` once BOM evidence lands. **PACKAGE-POWER-400-001
  remains blocked** behind BOM cross-check, the `S360-400`
  `schematic_status: verified` JSON PR, and `COMPLIANCE-001`.
- **HW-ASSETS-410** merged as **PR #516** and landed the
  `S360-410-R4` schematic PDF at
  `docs/hardware/schematics/S360-410-R4.pdf` (byte-identical to
  the upload; 975,137 bytes; SHA256
  `4a8b7a3b2a89006a9332eaa486743f687aaedc4b6bb807c6b25670f742ac2414`)
  and the curated artifact index at
  `docs/hardware/artifacts/S360-410-R4.md`. No `schematic_status`
  promotion, no `schematic_file` set, no package / product /
  WebFlash / build / release / import edit, no COMPLIANCE-001
  movement (`S360-410` is SELV and not in scope).
- **HW-PINMAP-410-FOLLOWUP** merged as **PR #517** on 2026-05-19
  (docs-only schematic-backed reconciliation). It consumed the
  HW-ASSETS-410 / PR #516 schematic evidence and promoted
  `docs/hardware/s360-410-r4-poe.md` from
  `pending — schematic/design evidence required` to
  `partial — schematic evidence available; package reconciliation,
  PoE PD controller / magnetics / buck / isolated DC/DC / harness
  identity evidence pending`. Recorded the **part-identity
  disagreement** between the package header in
  `packages/hardware/power_poe.yaml` (line 6 `Ag9712M, Silvertel
  Ag9700, or similar` — whole-module hint) and the schematic-shown
  discrete topology (`TPS2378DDAR(HSOIC-8)` PoE PD controller +
  `TX4138(ESOIC-8)` buck + `F0505S-2WR2(SIP-7)` isolated DC/DC
  with `AM1D-0505S-NZ` annotated alternate +
  `RJP-003TC1(LPJ4112CNL)` magnetics) as **unresolved** — BOM
  evidence is required before `PACKAGE-POE-410-001` can resolve
  it. `packages/hardware/power_poe.yaml` stayed byte-identical;
  comment-only cleanup deferred to `PACKAGE-POE-410-001` once BOM
  evidence lands. **`PACKAGE-POE-410-001` remains blocked** behind
  BOM cross-check, the `S360-410` `schematic_status: verified`
  JSON PR, HW-002 OQ#6 / `S360-100-BENCH-001` J2-harness closure,
  and the package reconciliation itself. The Release-One PoE
  "schematic verification pending" caveat in
  `docs/release-one-hardware-audit.md` Findings → PoE PSU was
  **preserved verbatim**. LED preview entry
  (`Ceiling-POE-VentIQ-RoomIQ-LED`) unchanged. FanTRIAC stays
  blocked under HW-005. HW-002 Open Question #6 /
  `S360-100-BENCH-001` J2-harness identity stay
  `pending — bench/manufacturing evidence required`.
- **CORE-ABSTRACT-BUS-001C** investigation merged as **PR #518** on
  2026-05-19 (docs-only Path A deferral). The pass evaluated whether
  `001C` could safely proceed now (Path C implementation), as a
  test-scaffold-only PR (Path B), or as a docs-only deferral
  (Path A), and is **confirmed deferred** — all six preconditions
  (`S360-100-BENCH-001` silkscreen evidence for Core `J4` / `J10`
  and RoomIQ `J6` pin orders; RoomIQ / AirIQ / VentIQ rebind plan;
  expansion-GPIO bench evidence or documented retirement decision;
  ESP32-S3 `GPIO3` strap-pin boot-behaviour bench characterisation
  for `S360-310-R4` + `S360-100-R4`; `tests/test_core_abstract_bus.py`
  scaffold; full re-validation pass for every non-Release-One
  product YAML consuming an affected Core package) remain open.
  Path B is not useful right now because target values are not
  fully decided (per-board `status_led_pin` re-bind and
  `expansion_gpio*` retirement-or-rebind both undecided) and a
  current-value test would enshrine schematic-conflicting values;
  Path C is unsafe right now because all six preconditions remain
  open and would silently re-bind Release-One on unverified
  evidence. The investigation outcome is recorded at
  `docs/hardware/core-abstract-bus-reconciliation.md`
  §`### 2026-05-19 — CORE-ABSTRACT-BUS-001C investigation pass`
  and `docs/cleanup-audit.md` §`CORE-ABSTRACT-BUS-001C update
  (2026-05-19 — docs-only investigation pass)`. No package /
  product / WebFlash / build / release / import / test / config /
  workflow / firmware / manifest edits. No
  `CORE-ABSTRACT-BUS-001*` slice has changed status as a result.
  Release-One stays `Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` /
  `stable`; LED preview stays `Ceiling-POE-VentIQ-RoomIQ-LED` /
  `preview`; FanTRIAC stays `blocked` / `HW-005`. The next `001C`
  PR must land **bench evidence + the pin-pinning test + the YAML
  rebind as a single atomic slice**, not as a test-scaffold-only
  PR alone.
- **CORE-ABSTRACT-BUS-001B** investigation merged as **PR #519** on
  2026-05-19 (docs-only Path A deferral). The pass evaluated whether
  `001B` could safely proceed now (Path C implementation), as a
  test-scaffold-only PR (Path B), or as a docs-only deferral
  (Path A), and is **confirmed deferred** — four preconditions
  remain open: (1) canonical I²C bus-id decision (candidates
  `shared_i2c` / `core_i2c` / `i2c0` recorded but not chosen);
  (2) `tests/test_core_abstract_bus.py` pin-pinning scaffold
  confirmed absent (same finding as PR #518); (3) re-validation
  plan for every non-Release-One product YAML consuming an
  affected Core / expansion package not designed; (4) the
  downstream-consumer audit lands in PR #519 but implementation
  still needs canonical name + tests + product re-validation
  before YAML edits. Path B is not useful right now because it
  would either pin schematic-conflicting current values
  (`halo_i2c` / `expansion_i2c` / `i2c0` / `i2c1` / `i2c_primary`
  / `i2c_expander` all on `GPIO39`/`GPIO40` + `GPIO21`/`GPIO18`)
  or pre-commit an undecided canonical bus id; Path C is unsafe
  right now because all four preconditions remain open and
  renaming any of the six current bus ids without updating every
  downstream `*_i2c_id` consumer would break parse-time
  substitution resolution and silently re-bind Release-One
  (which consumes `expansion_i2c` via VentIQ
  `packages/expansions/airiq_bathroom_base.yaml` line 29 and
  RoomIQ comfort `packages/expansions/comfort_ceiling.yaml`
  line 39) and the LED preview product. Findings recorded: the
  eight Core packages defining I²C buses (the six already listed
  in the slice scope — `sense360_core.yaml`,
  `sense360_core_ceiling.yaml`, `sense360_core_mapping.yaml`,
  `sense360_core_poe.yaml`, `sense360_core_wall.yaml`, plus
  `sense360_core_voice_ceiling.yaml` and
  `sense360_core_voice_wall.yaml` newly added by this
  investigation; `sense360_core_ceiling_s3.yaml` and
  `sense360_core_mini.yaml` remain out-of-scope — S3 has a
  different board layout; Mini already binds `i2c0` to the
  schematic-correct `GPIO48`/`GPIO45` via
  `mini_onboard_sensors.yaml`); the schematic ground truth is a
  single shared bus on `IO48` (SDA) / `IO45` (SCL) per
  `docs/hardware/s360-100-r4-core.md` §I2C bus; the 13
  downstream expansion-package `*_i2c_id` substitution defaults
  (`airiq.yaml`, `airiq_wall.yaml`, `airiq_ceiling.yaml`,
  `airiq_ceiling_s3.yaml`, `airiq_bathroom_base.yaml`,
  `airiq_bathroom_pro.yaml`, `comfort.yaml`, `comfort_wall.yaml`,
  `comfort_ceiling.yaml`, `comfort_ceiling_s3.yaml`,
  `fan_gp8403.yaml`, `gpio_expander_sx1509.yaml`, plus the
  feature file `packages/features/ceiling_halo_leds.yaml` which
  hard-codes `i2c_id: halo_i2c` and currently has no product
  includer — needs rebind or dead-code decision). Investigation
  outcome recorded at
  `docs/hardware/core-abstract-bus-reconciliation.md`
  §`### 2026-05-19 — CORE-ABSTRACT-BUS-001B investigation pass`
  and `docs/cleanup-audit.md` §`CORE-ABSTRACT-BUS-001B update
  (2026-05-19 — docs-only investigation pass)`. No package /
  product / WebFlash / build / release / import / test / config /
  workflow / firmware / manifest edits. No
  `CORE-ABSTRACT-BUS-001*` slice has changed status as a result.
  Release-One stays `Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` /
  `stable`; LED preview stays `Ceiling-POE-VentIQ-RoomIQ-LED` /
  `preview`; FanTRIAC stays `blocked` / `HW-005`. The next `001B`
  PR must land **the canonical bus-id decision + the pin-pinning
  test + the YAML rebind (Core packages + every downstream
  `*_i2c_id` consumer) + the product re-validation pass as a
  single atomic slice**, not as a test-scaffold-only PR alone.
  `PACKAGE-PWM-001` and `PACKAGE-DAC-001` therefore stay blocked
  behind 001B implementation (and their own evidence gates).
- **PACKAGE-POWER-400-001** investigation pass ran on 2026-05-19
  (this PR — docs-only Path A deferral). The pass evaluated whether
  `PACKAGE-POWER-400-001` could safely proceed now (Path C
  implementation — header / catalog `description` reconciliation
  against BOM), as a comment-only package cleanup PR (Path B —
  remove or soften the stale `HLK-PM01 or similar` AC/DC part hint
  without claiming a replacement), or as a docs-only deferral
  (Path A), and is **confirmed deferred** — five preconditions
  remain open: (1) BOM cross-check missing (no BOM line item with
  manufacturer + part number + revision for `PS1`, or for
  `F1 A250-1200` / `RV1 10D391K` / `C1 470nF` / `C5..C8` / `J1` /
  `J2`); (2) `S360-400` `schematic_status: verified` JSON PR not
  landed (`config/hardware-catalog.json` line 110 still records
  `S360-400` → `schematic_status: cataloged_unverified` and no
  `schematic_file` is set; `tests/test_hardware_catalog.py:53`
  explicitly asserts this state via `EXPECTED_STILL_UNVERIFIED_SKUS
  = frozenset({"S360-320", "S360-400"})` so the JSON promotion
  remains gated on BOM + silkscreen evidence + a separate
  evidence-bearing JSON-only PR); (3) `COMPLIANCE-001` `S360-400`
  slice still open (last re-checked PR #506; mains-voltage UK / EU
  assessment is not cleared); (4) silkscreen / PCB / creepage /
  clearance / bench / thermal / EMI evidence not committed
  (`J1` / `J2` silkscreen pin-1 orientation, mains-rated connector
  identity / rating / approvals, creepage / clearance distances
  between AC LINE / NEUTRAL / `Earth_Protective` / secondary
  `+5VP` / `GND`, load regulation, thermal rise of `PS1`, inrush
  current, insulation resistance / Hi-pot / earth-continuity /
  leakage all unverified per the HW-ASSETS-400 / PR #514
  artifact-index "Files NOT provided in this upload"); (5) the
  three-way AC/DC part-identity disagreement (catalog `HLK-5M05` —
  `config/hardware-catalog.json` line 109 — vs package header
  `HLK-PM01 or similar` — `packages/hardware/power_240v.yaml`
  line 7 — vs schematic `PS1 = HLK-10M05` from PR #514) **stays
  unresolved** and remains BOM-bound (per the explicit decision
  recorded by HW-PINMAP-400-FOLLOWUP / PR #515 in
  `docs/hardware/s360-400-r4-power.md` §Part identity
  reconciliation and §Package YAML status, "Replacing one
  unsourced claim with another would not raise the evidence
  quality of the package and would muddy the future
  PACKAGE-POWER-400-001 PR's scope"). Path B is not useful right
  now because the only safe comment-only change would be to remove
  the `HLK-PM01 or similar` line altogether without claiming
  `HLK-10M05` (or any replacement) — and PR #515's recorded
  decision was specifically that even that removal should wait for
  BOM, so that the eventual `PACKAGE-POWER-400-001` PR can land
  header reconciliation + catalog `description` reconciliation +
  BOM citation as one coordinated change; Path C is unsafe right
  now because the five preconditions above are open and any
  header / catalog edit without BOM evidence would substitute one
  unsourced claim for another. The investigation outcome confirms
  `packages/hardware/power_240v.yaml` stays byte-identical: the
  stale `HLK-PM01 or similar` header (line 7), the
  `100-240V AC, 50/60Hz` input claim (line 7), the
  `5V DC, 2A (10W)` output claim (line 8), the `3000VAC`
  isolation claim (line 9), the `Overcurrent, overvoltage,
  short-circuit` protection text (line 10), the recommended
  `1A` AC-input fusing line (line 15), and the
  `substitutions: power_source: "240v_ac"` (line 29) /
  `globals: power_source_type` (lines 32–36) / template
  diagnostic sensors (`Supply Voltage` / `Power Source` /
  `Power Configuration` / `AC Power Connected`) / logger config
  are **all** preserved byte-for-byte. Investigation outcome
  recorded at `docs/hardware/s360-400-r4-power.md`
  §`### 2026-05-19 — PACKAGE-POWER-400-001 investigation pass`
  and `docs/cleanup-audit.md` §`PACKAGE-POWER-400-001 update
  (2026-05-19 — docs-only investigation pass)`. No package /
  product / WebFlash / build / release / import / test / config /
  workflow / firmware / manifest edits. No catalog
  `schematic_status` promotion. No `schematic_file` set. No
  COMPLIANCE-001 movement. `PACKAGE-POWER-400-001` stays blocked;
  `PRODUCT-POWER-400-001` / `WEBFLASH-POWER-400-001` /
  `RELEASE-POWER-400-001` / `WF-IMPORT-POWER-400-001` stay
  blocked behind it. The next `PACKAGE-POWER-400-001` PR must
  land **the BOM cross-check + the `S360-400` `schematic_status:
  verified` JSON promotion (separate PR) + the package header
  reconciliation + the catalog `description` reconciliation as a
  single atomic slice**, not as a comment-only cleanup alone.
- **PWM** and **DAC** evidence re-checks (HW-PINMAP-311-FOLLOWUP /
  HW-PINMAP-312-FOLLOWUP) remain insufficient — both audits are still
  partial.
- The **TRIAC** chain remains blocked by **HW-005**, **COMPLIANCE-001**, and
  the **PACKAGE-TRIAC-001** docs-only deferral.
- The **LED stable** chain remains blocked by **S360-300-BENCH-001** (bench
  verification) and the WebFlash-owned operator-proof follow-ups.

## Completed / merged PRs

Only PR numbers verified against the local `git log` are listed here. Do not
add rows without verifying the PR number.

| PR key                       | PR number | Repo            | Status                                 | What merged                                                                          | What did not change                                       | Follow-up impact                                                                  |
|------------------------------|-----------|-----------------|----------------------------------------|--------------------------------------------------------------------------------------|-----------------------------------------------------------|-----------------------------------------------------------------------------------|
| PRODUCT-TRIAC-002            | #501      | esphome-public  | Merged — docs-only deferral             | Recorded deferral of FanTRIAC product implementation until PACKAGE-TRIAC-001 lands   | Product YAML, WebFlash wrapper, build matrix              | Product implementation blocked on PACKAGE-TRIAC-001                                |
| PACKAGE-TRIAC-001            | #502      | esphome-public  | Merged — docs-only deferral             | Recorded deferral until HW-005 / HW-PINMAP-320-FOLLOWUP / COMPLIANCE-001 land        | `packages/expansions/fan_triac.yaml`                       | FanTRIAC package implementation remains blocked on HW + compliance evidence       |
| TRIAC-QUEUE-001              | #503      | esphome-public  | Merged — queue normalization (docs)     | Normalized remaining FanTRIAC follow-up chain after the package deferral             | No functional or catalog files                            | Downstream FanTRIAC queue rows now reflect the deferred package state             |
| S360-100-BENCH-001           | #504      | esphome-public  | Merged — docs-only evidence-pass        | Re-checked Core board bench / manufacturing evidence; status remains pending          | No functional, catalog, or evidence-asset files            | Core bench gate still pending; downstream stable promotions remain blocked        |
| HW-005 / HW-PINMAP-320-FOLLOWUP | #505   | esphome-public  | Merged — docs-only evidence-pass        | Re-checked S360-320 FanTRIAC pin/package evidence; audit remains partial             | `packages/expansions/fan_triac.yaml`, product/WebFlash      | FanTRIAC chain still blocked on HW-005 + COMPLIANCE-001                            |
| COMPLIANCE-001               | #506      | esphome-public  | Merged — docs-only evidence-pass        | Re-checked S360-320 mains-voltage advanced/manual-warning sign-off; remains open     | Compliance status (still not cleared)                      | FanTRIAC product / package release remains blocked on compliance sign-off          |
| HW-PINMAP-311-FOLLOWUP       | #507      | esphome-public  | Merged — docs-only evidence-pass        | Re-checked S360-311 PWM pin/package evidence; audit remains partial                  | `packages/expansions/fan_pwm.yaml`, PWM product/WebFlash    | PWM package/product chain still blocked on additional evidence                     |
| HW-PINMAP-312-FOLLOWUP       | #508      | esphome-public  | Merged — docs-only evidence-pass        | Re-checked S360-312 DAC pin/package evidence; audit remains partial                  | `packages/expansions/fan_gp8403.yaml`, DAC product/WebFlash | DAC package/product chain still blocked on additional evidence                     |
| HW-ASSETS-310                | #509      | esphome-public  | Merged — artifact ingest                | Added S360-310-R4 schematic PDF and curated artifact index                            | No package, product, WebFlash, or release files            | Unblocked HW-PINMAP-310-FOLLOWUP schematic-backed reconciliation                   |
| HW-PINMAP-310-FOLLOWUP       | #510      | esphome-public  | Merged — schematic-backed partial       | Consumed S360-310-R4 schematic; promoted Relay pin/package audit to partial          | `packages/expansions/fan_relay.yaml`, product/WebFlash      | Relay package work surfaced shared-variable mismatches → CORE-ABSTRACT-BUS-001     |
| PACKAGE-RELAY-001            | #511      | esphome-public  | Merged — docs-only deferral             | Recorded deferral until CORE-ABSTRACT-BUS-001 / silkscreen / harness / K1 BOM land   | `packages/expansions/fan_relay.yaml`                        | Relay package implementation now gated by CORE-ABSTRACT-BUS-001                    |
| CORE-ABSTRACT-BUS-001        | #513      | esphome-public  | Merged — docs-only audit + slice plan   | Added `docs/hardware/core-abstract-bus-reconciliation.md` and split implementation into 001A / 001B / 001C | No package YAML, product YAML, config, tests, firmware, or release files changed | Queue now prioritises 001C before 001A (GPIO3 collision); Relay package remains blocked on 001A; PWM / DAC additionally affected by 001B / 001C |
| HW-ASSETS-400                | #514      | esphome-public  | Merged — artifact ingest                | Added `S360-400-R4` schematic PDF (461,206 bytes; SHA256 `295e3ec9192603fd4ca7d89b8cda68777e5cb8e9713ed8b0fba2316babb0e765`) and curated artifact index | No package, product, WebFlash, build, release, compliance, or JSON catalog files | Unblocked HW-PINMAP-400-FOLLOWUP schematic-backed reconciliation |
| HW-PINMAP-400-FOLLOWUP       | #515      | esphome-public  | Merged — schematic-backed partial       | Consumed HW-ASSETS-400 schematic evidence; promoted S360-400 power audit to partial and recorded the three-way `HLK-5M05` / `HLK-PM01 or similar` / `HLK-10M05` part-identity disagreement | No package, product, WebFlash, build, release, compliance, JSON catalog, or `power_240v.yaml` changes | `PACKAGE-POWER-400-001` remains blocked by BOM / JSON promotion / COMPLIANCE-001; `HW-ASSETS-410` becomes next evidence ingest |
| HW-ASSETS-410                | #516      | esphome-public  | Merged — artifact ingest                | Added `S360-410-R4` schematic PDF (975,137 bytes; SHA256 `4a8b7a3b2a89006a9332eaa486743f687aaedc4b6bb807c6b25670f742ac2414`) and curated artifact index | No package, product, WebFlash, build, release, compliance, or JSON catalog files | Unblocked HW-PINMAP-410-FOLLOWUP schematic-backed reconciliation |
| HW-PINMAP-410-FOLLOWUP       | #517      | esphome-public  | Merged — schematic-backed partial       | Consumed HW-ASSETS-410 schematic evidence; promoted S360-410 PoE PSU audit to `partial — schematic evidence available; package reconciliation, PoE PD controller / magnetics / buck / isolated DC/DC / harness identity evidence pending` and recorded the package-header whole-module hint (`Ag9712M / Silvertel Ag9700 / or similar`) vs schematic-shown discrete topology (`TPS2378DDAR / TX4138 / F0505S-2WR2 / RJP-003TC1(LPJ4112CNL)`) part-identity disagreement | No package, product, WebFlash, build, release, compliance, JSON catalog, or `power_poe.yaml` changes; Release-One PoE "schematic verification pending" caveat preserved verbatim | `PACKAGE-POE-410-001` remains blocked by BOM cross-check / `S360-410 schematic_status: verified` JSON PR / HW-002 OQ#6 / `S360-100-BENCH-001` closure / package-header reconciliation; `CORE-ABSTRACT-BUS-001C` becomes next active queue item |
| CORE-ABSTRACT-BUS-001C       | #518      | esphome-public  | Merged — docs-only investigation pass   | Recorded `CORE-ABSTRACT-BUS-001C` investigation outcome as Path A docs-only deferral; re-verified all six preconditions (`S360-100-BENCH-001` silkscreen evidence for Core `J4` / `J10` and RoomIQ `J6` pin orders; RoomIQ / AirIQ / VentIQ rebind plan; expansion-GPIO bench evidence or documented retirement decision; ESP32-S3 `GPIO3` strap-pin boot-behaviour bench characterisation; `tests/test_core_abstract_bus.py` scaffold; full non-Release-One product re-validation pass) remain open; updated `docs/hardware/core-abstract-bus-reconciliation.md` audit log and `docs/cleanup-audit.md` `CORE-ABSTRACT-BUS-001C update` entry | No package, product, WebFlash, build, release, compliance, JSON catalog, test, script, workflow, component, include, firmware, or manifest edits; no `CORE-ABSTRACT-BUS-001*` slice status change; no `schematic_status` / `schematic_file` promotion; Release-One / LED preview / FanTRIAC identity unchanged | `CORE-ABSTRACT-BUS-001C` stays at top of queue, blocked on the six preconditions; `CORE-ABSTRACT-BUS-001A` stays blocked behind `001C`; `CORE-ABSTRACT-BUS-001B` stays independent of `001A` / `001C` ordering; `PACKAGE-RELAY-001` and downstream relay slices still blocked behind `001A`; `PACKAGE-PWM-001` / `PACKAGE-DAC-001` still blocked behind their evidence + `001B` |
| CORE-ABSTRACT-BUS-001B       | #519      | esphome-public  | Merged — docs-only investigation pass   | Recorded `CORE-ABSTRACT-BUS-001B` investigation outcome as Path A docs-only deferral; re-verified all four preconditions (canonical I²C bus-id decision among `shared_i2c` / `core_i2c` / `i2c0` candidates; `tests/test_core_abstract_bus.py` pin-pinning scaffold; re-validation plan for every non-Release-One product YAML consuming an affected Core / expansion package; downstream-consumer audit lands in PR but implementation still needs canonical name + tests + product re-validation before YAML edits) remain open; downstream-consumer audit added to `docs/hardware/core-abstract-bus-reconciliation.md` §`Downstream consumer inventory (2026-05-19)` (eight in-scope Core packages including newly-added `sense360_core_voice_ceiling.yaml` / `sense360_core_voice_wall.yaml`; 13 expansion-package consumers plus `packages/features/ceiling_halo_leds.yaml` hard-coded `i2c_id: halo_i2c` with no current product `!include`r); `docs/cleanup-audit.md` `CORE-ABSTRACT-BUS-001B update` entry recorded | No package, product, WebFlash, build, release, compliance, JSON catalog, test, script, workflow, component, include, firmware, or manifest edits; no `CORE-ABSTRACT-BUS-001*` slice status change; no `schematic_status` / `schematic_file` promotion; Release-One / LED preview / FanTRIAC identity unchanged; canonical I²C bus-id **not chosen** (only candidate set recorded) | `CORE-ABSTRACT-BUS-001B` stays at queue entry #3, blocked on the four preconditions and independent of `001A` / `001C` ordering; `PACKAGE-PWM-001` / `PACKAGE-DAC-001` still blocked behind `001B` implementation + their own evidence gates; `PACKAGE-POWER-400-001` becomes next active queue item |

## Active / upcoming esphome-public queue

Listed in working priority order. WebFlash-owned import PRs are kept out of
this table; see **Cross-repo dependencies**. The only `WF-`-prefixed entry
that appears below is **WF-TRIAC-001**, which is the in-repo
wrapper/catalog/build slice (not a WebFlash-runtime import).

1. **CORE-ABSTRACT-BUS-001C — UART / status LED / PIR / expansion GPIO + ALS_INT rebind**
   - Status: **Investigated 2026-05-19 — confirmed deferred (Path A
     docs-only); six preconditions still open** (next / systemic
     blocker — must land at-or-before the relay slice to free
     `GPIO3`)
   - Purpose: Split the single `uart_bus` into `roomiq_hi_link_uart`
     (IO1/IO2) and `roomiq_sen0609_uart` (IO4/IO5); move
     `status_led_pin` off `GPIO48` (claimed by shared I²C SDA);
     `pir_sensor_pin: GPIO47 → GPIO15`;
     `comfort_ceiling_als_int_pin: GPIO3 → GPIO47` in
     `packages/expansions/comfort_ceiling.yaml`;
     `expander_int_pin: GPIO3 → GPIO17` in
     `packages/hardware/sense360_core_mapping.yaml`;
     `sx1509_interrupt_pin: GPIO3 → GPIO17` in
     `packages/expansions/gpio_expander_sx1509.yaml`;
     `expansion_gpio1..4` rebind. Frees `GPIO3` for the relay slice.
   - Notes: 2026-05-19 investigation pass (this PR) is **docs-only
     deferral**. Re-verified against the live YAML; every value
     listed in
     `docs/hardware/core-abstract-bus-reconciliation.md` §Core
     abstract substitution inventory still matches the live
     packages byte-for-byte. The six open preconditions are: (1)
     `S360-100-BENCH-001` silkscreen evidence (Core `J4` / `J10`
     and RoomIQ `J6` pin orders) — stays
     `pending — bench/manufacturing evidence required` per the
     2026-05-18 re-check at
     `docs/hardware/s360-100-r4-core.md` §S360-100-BENCH-001
     status; (2) RoomIQ / AirIQ / VentIQ package rebind plan — not
     drafted; (3) expansion-GPIO bench evidence or a documented
     decision to retire the `expansion_gpio*` abstraction — not
     recorded (downstream consumer
     `packages/expansions/fan_pwm.yaml` binds
     `fan_pwm_pin: ${expansion_gpio1}` and
     `fan_tach_pin: ${expansion_gpio2}`, so the abstraction is
     not orphan); (4) ESP32-S3 `GPIO3` strap-pin boot-behaviour
     bench characterisation for `S360-310-R4` + `S360-100-R4` —
     not landed (strictly a 001A precondition; recorded here
     because 001C frees `GPIO3` for the relay slice to consume);
     (5) `tests/test_core_abstract_bus.py` scaffolding — confirmed
     absent and, per the test-scaffolding plan, lands **with** the
     first implementation slice (not as a test-scaffold-only PR
     alone); (6) re-validation pass for every product consuming
     any affected Core package (`sense360_core_ceiling.yaml`,
     `sense360_core.yaml`, `sense360_core_mapping.yaml`,
     `sense360_core_poe.yaml`, `sense360_core_wall.yaml`). The
     next `001C` PR must land **bench evidence + the pin-pinning
     test + the YAML rebind as a single atomic slice**, not as a
     test-scaffold-only PR alone. Plan recorded in
     `docs/hardware/core-abstract-bus-reconciliation.md`
     §CORE-ABSTRACT-BUS-001C; investigation pass log recorded at
     `docs/hardware/core-abstract-bus-reconciliation.md` §`### 2026-05-19 — CORE-ABSTRACT-BUS-001C investigation pass`
     and `docs/cleanup-audit.md` §CORE-ABSTRACT-BUS-001C update.

2. **CORE-ABSTRACT-BUS-001A — relay_pin slice (`GPIO3`)**
   - Status: Blocked on **CORE-ABSTRACT-BUS-001C**
   - Purpose: Rebind `relay_pin` to `GPIO3` in
     `packages/hardware/sense360_core.yaml` (line 63),
     `packages/hardware/sense360_core_ceiling.yaml` (line 61),
     `packages/hardware/sense360_core_mapping.yaml` (line 47),
     `packages/hardware/sense360_core_poe.yaml` (line 76), and
     `packages/hardware/sense360_core_wall.yaml` (line 65). Add
     pin-pinning regression coverage in
     `tests/test_core_abstract_bus.py`.
   - Notes: Hard preconditions: 001C lands first (so GPIO3 is free);
     S360-100-BENCH-001 silkscreen evidence; ESP32-S3 `GPIO3`
     strap-pin boot-behaviour bench characterisation against a
     populated `S360-310-R4` + `S360-100-R4` pair; `K1` BOM identity
     and harness identity. Re-validates Release-One because
     `sense360_core_ceiling.yaml` is consumed by
     `products/sense360-ceiling-poe-ventiq-roomiq.yaml`. Plan
     recorded in
     `docs/hardware/core-abstract-bus-reconciliation.md` §CORE-ABSTRACT-BUS-001A.

3. **CORE-ABSTRACT-BUS-001B — Shared-I²C-bus consolidation**
   - Status: **Investigated 2026-05-19 — confirmed deferred (Path A
     docs-only); four preconditions still open**. Independent of
     `001A` / `001C` ordering; should land before `PACKAGE-PWM-001`
     / `PACKAGE-DAC-001`.
   - Purpose: Collapse the duplicated `halo_i2c` / `expansion_i2c` /
     `i2c0` / `i2c1` / `i2c_primary` / `i2c_expander` bus definitions
     in the Core abstract packages down to the **single shared I²C
     bus** on `IO48` (SDA) / `IO45` (SCL) that the `S360-100-R4`
     schematic actually exposes. Realign every downstream expansion
     package that currently references one of the old bus ids.
   - Notes: 2026-05-19 investigation pass (this PR) is **docs-only
     deferral**. Re-verified against the live YAML; the eight Core
     packages that define an I²C bus are
     `packages/hardware/sense360_core.yaml` (lines 100–112; `i2c0`
     `GPIO39`/`GPIO40` + `i2c1` `GPIO21`/`GPIO18`),
     `packages/hardware/sense360_core_ceiling.yaml` (lines 104–117;
     `halo_i2c` `GPIO39`/`GPIO40` + `expansion_i2c`
     `GPIO21`/`GPIO18`),
     `packages/hardware/sense360_core_mapping.yaml` (lines 93–104;
     `i2c_primary` + `i2c_expander`),
     `packages/hardware/sense360_core_poe.yaml` (lines 124–137;
     `i2c0` + `i2c1`),
     `packages/hardware/sense360_core_wall.yaml` (lines 114–127;
     `i2c0` + `i2c1`),
     `packages/hardware/sense360_core_voice_ceiling.yaml`
     (lines 113–124; `halo_i2c` + `expansion_i2c` — **newly added
     to 001B scope by this investigation**), and
     `packages/hardware/sense360_core_voice_wall.yaml` (lines
     134–143; `i2c0` + `i2c1` — **newly added to 001B scope by
     this investigation**); `packages/hardware/sense360_core_ceiling_s3.yaml`
     (`i2c_primary` on `GPIO17`/`GPIO18`) and
     `packages/hardware/sense360_core_mini.yaml` (`i2c0` on
     `GPIO48`/`GPIO45` via `mini_onboard_sensors.yaml`) remain
     out-of-scope — S3 has a different board layout; Mini already
     binds the schematic-correct pins. Schematic ground truth per
     `docs/hardware/s360-100-r4-core.md` §I2C bus is a **single
     shared bus** on `IO48` (SDA) / `IO45` (SCL) pulled up by
     R22/R21 10 kΩ, shared by SX1509 U3 + J7 GP8403 + J9 AirIQ +
     J10 RoomIQ. The 13 downstream expansion-package consumers
     are `airiq.yaml` (`airiq_i2c_id: i2c0`),
     `airiq_wall.yaml` (`i2c0`),
     `airiq_ceiling.yaml` (`expansion_i2c`),
     `airiq_ceiling_s3.yaml` (`i2c_primary`),
     `airiq_bathroom_base.yaml` (`bathroom_i2c_id: expansion_i2c`),
     `airiq_bathroom_pro.yaml` (`expansion_i2c`),
     `comfort.yaml` (`comfort_i2c_id: i2c0`),
     `comfort_wall.yaml` (`i2c0`),
     `comfort_ceiling.yaml` (`comfort_ceiling_i2c_id: expansion_i2c`),
     `comfort_ceiling_s3.yaml` (`comfort_i2c_id: i2c_primary`),
     `fan_gp8403.yaml` (`fan_dac_i2c_id: i2c0`),
     `gpio_expander_sx1509.yaml` (`sx1509_i2c_id: i2c1`), and the
     feature file `packages/features/ceiling_halo_leds.yaml` which
     **hard-codes `i2c_id: halo_i2c`** and has no current product
     includer — needs rebind or dead-code decision. Release-One
     (`products/sense360-ceiling-poe-ventiq-roomiq.yaml`) and the
     LED preview (`products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`)
     both resolve `expansion_i2c` via VentIQ
     `airiq_bathroom_base.yaml` line 29 and RoomIQ
     `comfort_ceiling.yaml` line 39 (the LED preview uses
     WS2812B `led_data_pin: GPIO38` from
     `packages/hardware/led_ring_ceiling.yaml`, **not** I²C).
     Mini products define their own inline `i2c0` on
     `GPIO48`/`GPIO45` and are out of scope. The four open
     preconditions are: (1) **canonical I²C bus-id decision**
     remains open — candidates `shared_i2c`, `core_i2c`, `i2c0`
     recorded but not chosen; (2) **`tests/test_core_abstract_bus.py`
     pin-pinning scaffold** remains absent (confirmed by this
     investigation; same finding as PR #518) and, per the
     test-scaffolding plan, lands **with** the first implementation
     slice; (3) **re-validation plan for every non-Release-One
     product YAML** consuming any affected Core / expansion package
     is not designed; (4) the **downstream-consumer audit** lands
     in this PR (above) but implementation still needs canonical
     name + tests + product re-validation before YAML edits.
     The next `001B` PR must land **the canonical bus-id decision
     + the pin-pinning test + the YAML rebind (Core packages +
     every downstream `*_i2c_id` consumer) + the product
     re-validation pass as a single atomic slice**, not as a
     test-scaffold-only PR alone. Plan recorded in
     `docs/hardware/core-abstract-bus-reconciliation.md`
     §CORE-ABSTRACT-BUS-001B; investigation pass log recorded at
     `docs/hardware/core-abstract-bus-reconciliation.md`
     §`### 2026-05-19 — CORE-ABSTRACT-BUS-001B investigation pass`
     and `docs/cleanup-audit.md` §`CORE-ABSTRACT-BUS-001B update
     (2026-05-19 — docs-only investigation pass)`.

4. **PACKAGE-POWER-400-001**
   - Status: **Investigated 2026-05-19 — confirmed deferred (Path A
     docs-only); five preconditions still open**. Blocked on BOM
     cross-check, `S360-400` `schematic_status: verified` JSON PR,
     `COMPLIANCE-001` `S360-400` slice, silkscreen / PCB / creepage /
     clearance / bench / thermal / EMI evidence, and the three-way
     AC/DC part-identity reconciliation.
   - Purpose: Reconcile
     [`packages/hardware/power_240v.yaml`](packages/hardware/power_240v.yaml)
     header claims (AC/DC part identity — catalog `HLK-5M05` vs
     package header `HLK-PM01 or similar` vs schematic
     `PS1 = HLK-10M05`; `100-240V AC, 50/60Hz` input; `5V DC, 2A
     (10W)` output; `3000VAC` isolation; `Overcurrent, overvoltage,
     short-circuit` protection; recommended `1A` AC-input fusing)
     and the catalog `description` (`Mains to 5V using HLK-5M05.`
     at `config/hardware-catalog.json` line 109) against the
     now-partially-verified schematic and the module BOM.
   - Notes: 2026-05-19 investigation pass (this PR) is **docs-only
     deferral**. Re-verified against the live files;
     `packages/hardware/power_240v.yaml` is byte-identical to its
     state after HW-PINMAP-400-FOLLOWUP / PR #515 (the stale
     `HLK-PM01 or similar` header at line 7, the `100-240V AC,
     50/60Hz` input / `5V DC, 2A (10W)` output / `3000VAC`
     isolation / `Overcurrent, overvoltage, short-circuit`
     protection claims at lines 7–10, and the recommended `1A`
     AC-input fusing at line 15 are **all** preserved
     byte-for-byte; the package emits diagnostic sensors only —
     `Supply Voltage` (template, returns `5.0`), `Power Source`
     (text sensor, returns `"240V AC"`), `Power Configuration`
     (text sensor), `AC Power Connected` (binary sensor, returns
     `true`) — with **no GPIO / I²C / UART / SPI / DAC binding**).
     `config/hardware-catalog.json` line 110 still records
     `S360-400` → `schematic_status: cataloged_unverified` with no
     `schematic_file` set; `tests/test_hardware_catalog.py:53`
     explicitly asserts this state. The five open preconditions
     are: (1) **BOM cross-check missing** — no BOM line item with
     manufacturer + part number + revision for `PS1` (settles the
     three-way `HLK-5M05` / `HLK-PM01 or similar` / `HLK-10M05`
     disagreement), and no BOM lines for `F1 A250-1200` / `RV1
     10D391K` / `C1 470nF` / `C5..C8` / `J1` / `J2`; (2) **`S360-400`
     `schematic_status: verified` JSON PR not landed** — separate
     JSON-only PR after BOM + silkscreen evidence land that flips
     `schematic_status` to `verified` and sets `schematic_file:
     docs/hardware/schematics/S360-400-R4.pdf`; (3) **`COMPLIANCE-001`
     `S360-400` slice still open** — last re-checked PR #506; the
     mains-voltage UK / EU assessment at
     `docs/compliance/mains-voltage-uk-eu-assessment.md` is not
     cleared, and `S360-400` is one of the two mains-voltage SKUs
     in scope; (4) **silkscreen / PCB / creepage / clearance /
     bench / thermal / EMI evidence missing** — `J1` and `J2`
     silkscreen pin-1 orientation, `J1` mains-rated connector
     identity / current / voltage / approvals, `J2` low-voltage
     connector identity, `F1 A250-1200` polyfuse hold / trip /
     voltage rating, `RV1 10D391K` clamp voltage / energy rating,
     `C1 470nF` X-cap safety class X1 / X2, `C5..C8` voltage /
     dielectric / ESR, Y-class capacitor presence-or-absence as
     designed, common-mode / differential-mode line-filter
     inductor absence as designed, integrated thermal protection
     in the `HLK-10M05` module, mounting-hole electrical bonding
     to `Earth_Protective`, creepage / clearance distances
     between AC LINE / NEUTRAL / `Earth_Protective` / secondary
     `+5VP` / `GND`, load regulation, thermal rise of `PS1` under
     continuous load, inrush current at cold-start, insulation
     resistance / Hi-pot / earth-continuity / leakage, EMI / EMC
     conducted / radiated emissions and immunity — none on file
     per the HW-ASSETS-400 / PR #514 artifact-index "Files NOT
     provided in this upload"; (5) **three-way AC/DC
     part-identity disagreement** (catalog `HLK-5M05` vs package
     header `HLK-PM01 or similar` vs schematic `PS1 = HLK-10M05`)
     stays unresolved per the explicit decision recorded by
     HW-PINMAP-400-FOLLOWUP / PR #515 in
     `docs/hardware/s360-400-r4-power.md` §Part identity
     reconciliation. Path B (comment-only package cleanup) is not
     useful right now because PR #515 explicitly recorded
     comment-only cleanup as deferred to `PACKAGE-POWER-400-001`
     once BOM evidence lands ("Replacing one unsourced claim with
     another would not raise the evidence quality of the package
     and would muddy the future PACKAGE-POWER-400-001 PR's
     scope"); the only safe comment-only edit would be to remove
     the `HLK-PM01 or similar` line altogether **without** claiming
     `HLK-10M05` or any replacement, but PR #515's recorded
     decision was specifically that even that removal should wait
     for BOM so that the eventual `PACKAGE-POWER-400-001` PR can
     land header reconciliation + catalog `description`
     reconciliation + BOM citation as one coordinated change.
     Path C (implementation) is unsafe right now because all five
     preconditions are open and any header / catalog edit without
     BOM evidence would substitute one unsourced claim for
     another. Must not destabilize Release-One (Release-One uses
     PoE PSU `S360-410`, not the 240 V PSU `S360-400`); the four
     `legacy-compatible` `*-pwr` Core variants
     (`products/sense360-core-c-pwr.yaml`,
     `products/sense360-core-w-pwr.yaml`,
     `products/sense360-core-v-c-pwr.yaml`,
     `products/sense360-core-v-w-pwr.yaml`) stay
     `legacy-compatible` and `webflash_build_matrix: false`.
     Coordinate with the CORE-ABSTRACT-BUS-001 slices
     (001A/001B/001C) is **not** required for this slice because
     the power package binds no shared Core variables (no GPIO /
     I²C / UART / SPI / DAC binding in `power_240v.yaml`). The
     next `PACKAGE-POWER-400-001` PR must land **the BOM
     cross-check + the `S360-400` `schematic_status: verified`
     JSON promotion (separate PR) + the package header
     reconciliation + the catalog `description` reconciliation as
     a single atomic slice**, not as a comment-only cleanup
     alone. Investigation outcome recorded at
     `docs/hardware/s360-400-r4-power.md`
     §`### 2026-05-19 — PACKAGE-POWER-400-001 investigation pass`
     and `docs/cleanup-audit.md` §`PACKAGE-POWER-400-001 update
     (2026-05-19 — docs-only investigation pass)`.

5. **PRODUCT-POWER-400-001**
   - Status: Planned / after PACKAGE-POWER-400-001
   - Purpose: Add the S360-400 product YAML against the new package.
   - Notes: No WebFlash exposure until WEBFLASH-POWER-400-001.

6. **WEBFLASH-POWER-400-001**
   - Status: Planned / after PRODUCT-POWER-400-001
   - Purpose: Add the WebFlash wrapper, compatibility entry, and build
     matrix row for the S360-400 product.
   - Notes: Pairs with WebFlash-side WF-IMPORT-POWER-400-001 — see
     cross-repo dependencies.

7. **RELEASE-POWER-400-001**
   - Status: Planned / after WEBFLASH-POWER-400-001
   - Purpose: Produce the release artifact + release-proof entries for the
     S360-400 product.
   - Notes: Subject to existing release-artifact readiness gates.

8. **PACKAGE-POE-410-001**
    - Status: **Blocked** — remains blocked after HW-PINMAP-410-FOLLOWUP
      (the schematic-backed reconciliation surfaces the package-header
      vs schematic part-identity disagreement but does not by itself
      resolve it).
    - Purpose: Reconcile [`packages/hardware/power_poe.yaml`](packages/hardware/power_poe.yaml)
      header claims (PoE module part identity `Ag9712M / Silvertel
      Ag9700 / or similar` vs schematic-shown discrete topology
      `TPS2378DDAR / TX4138 / F0505S-2WR2 / RJP-003TC1(LPJ4112CNL)`;
      PoE standard / class / input / output / protection ratings;
      diagnostic-sensor topology) against the now-verified schematic
      and the module BOM.
    - Notes: Blocked on (a) BOM cross-check (settles the
      whole-module-vs-discrete topology disagreement and the
      `F0505S-2WR2`-vs-`AM1D-0505S-NZ` primary-vs-alternate selection),
      (b) the separate `S360-410` `schematic_status: verified`
      JSON-only PR (after BOM and HW-002 OQ#6 closure), (c) HW-002 OQ#6
      / `S360-100-BENCH-001` J2-harness identity closure, and (d) the
      package-header reconciliation itself. Must not implicitly
      requalify Release-One; the "schematic verification pending"
      caveat closure is a separate later PR.

9. **PRODUCT-POE-410-001**
    - Status: Planned / after PACKAGE-POE-410-001 (and only if a new
      PoE-410-explicit product entry is warranted; often the slice will
      close by promoting Release-One's preserved schematic-pending
      caveat alone, without adding a new product entry).
    - Purpose: Add the S360-410 product YAML against the new package.
    - Notes: No WebFlash exposure until WEBFLASH-POE-410-001.

10. **WEBFLASH-POE-410-001**
    - Status: Planned / after PRODUCT-POE-410-001
    - Purpose: Add the WebFlash wrapper, compatibility entry, and build
      matrix row for the S360-410 product.
    - Notes: Pairs with WebFlash-side WF-IMPORT-POE-410-001.

11. **RELEASE-POE-410-001**
    - Status: Planned / after WEBFLASH-POE-410-001
    - Purpose: Produce the release artifact + release-proof entries for the
      S360-410 product.
    - Notes: Subject to existing release-artifact readiness gates.

12. **PRODUCT-RELAY-001**
    - Status: Blocked on CORE-ABSTRACT-BUS-001A (relay_pin slice;
      itself blocked on 001C) + PACKAGE-RELAY-001 implementation
    - Purpose: Add the S360-310 Relay product YAML once the Relay package is
      implemented (not the current docs-only deferral state).
    - Notes: Implementation deferred per PR #511 (PACKAGE-RELAY-001
      docs-only deferral) and now further gated by the
      CORE-ABSTRACT-BUS-001A relay_pin slice landing.

13. **WEBFLASH-RELAY-001**
    - Status: Blocked on PRODUCT-RELAY-001 (which is itself blocked on
      CORE-ABSTRACT-BUS-001A)
    - Purpose: Add the WebFlash wrapper, compatibility entry, and build
      matrix row for the Relay product.
    - Notes: Pairs with WebFlash-side WF-IMPORT-RELAY-001.

14. **RELEASE-RELAY-001**
    - Status: Blocked on WEBFLASH-RELAY-001 (ultimately on
      CORE-ABSTRACT-BUS-001A)
    - Purpose: Produce the release artifact + release-proof entries for the
      Relay product.

15. **PACKAGE-PWM-001**
    - Status: Blocked on HW-PINMAP-311-FOLLOWUP returning sufficient evidence
    - Purpose: Stand up / re-stand up the S360-311 PWM package wiring once
      the pin/package audit is no longer partial.
    - Notes: Also affected by CORE-ABSTRACT-BUS-001B (shared I²C bus
      consolidation) and CORE-ABSTRACT-BUS-001C (`expansion_gpio1`
      / `expansion_gpio2` rebind that `fan_pwm.yaml` consumes via
      `${fan_pwm_pin}` / `${fan_tach_pin}`).

16. **PRODUCT-PWM-001**
    - Status: Blocked on PACKAGE-PWM-001
    - Purpose: Add / re-align the S360-311 PWM product YAML.

17. **WEBFLASH-PWM-001**
    - Status: Blocked on PRODUCT-PWM-001
    - Purpose: WebFlash wrapper, compatibility entry, build matrix row.
    - Notes: Pairs with WebFlash-side WF-IMPORT-PWM-001.

18. **RELEASE-PWM-001**
    - Status: Blocked on WEBFLASH-PWM-001
    - Purpose: Release artifact + release-proof entries for the PWM product.

19. **PACKAGE-DAC-001**
    - Status: Blocked on HW-PINMAP-312-FOLLOWUP returning sufficient evidence
    - Purpose: Stand up / re-stand up the S360-312 DAC (GP8403) package
      wiring once the pin/package audit is no longer partial.
    - Notes: Also affected by CORE-ABSTRACT-BUS-001B (the GP8403
      DAC is I²C-attached, so it consumes whichever bus id 001B
      settles on).

20. **PRODUCT-DAC-001**
    - Status: Blocked on PACKAGE-DAC-001
    - Purpose: Add / re-align the S360-312 DAC product YAML.

21. **WEBFLASH-DAC-001**
    - Status: Blocked on PRODUCT-DAC-001
    - Purpose: WebFlash wrapper, compatibility entry, build matrix row.
    - Notes: Pairs with WebFlash-side WF-IMPORT-DAC-001.

22. **RELEASE-DAC-001**
    - Status: Blocked on WEBFLASH-DAC-001
    - Purpose: Release artifact + release-proof entries for the DAC product.

23. **S360-300-BENCH-001**
    - Status: Pending bench evidence
    - Purpose: LED ring bench / verification gate for S360-300.
    - Notes: Blocks the LED stable chain together with the WebFlash-owned
      operator-proof follow-ups.

24. **RELEASE-007**
    - Status: Planned / promotion of LED stable
    - Purpose: Promote the LED package + product from preview to stable
      once S360-300-BENCH-001 and the WebFlash operator-proof follow-ups
      land.
    - Notes: Subject to preview-to-stable promotion gates.

25. **HW-005 / HW-PINMAP-320-FOLLOWUP**
    - Status: Open / evidence-pass re-checked (PR #505); audit remains
      partial
    - Purpose: Resolve the S360-320 FanTRIAC pin/package collisions and
      provide the schematic/interrupt-capable GPIO evidence needed to
      progress the FanTRIAC chain.
    - Notes: Gating PACKAGE-TRIAC-001 implementation.

26. **COMPLIANCE-001**
    - Status: Open / not cleared (PR #506 re-checked, no sign-off yet)
    - Purpose: Land the S360-320 mains-voltage advanced / manual-warning
      compliance sign-off.
    - Notes: Gating PRODUCT-TRIAC-002 / FanTRIAC release exposure.

27. **PACKAGE-TRIAC-001**
    - Status: Deferred (PR #502 docs-only); blocked on HW-005 /
      HW-PINMAP-320-FOLLOWUP / COMPLIANCE-001
    - Purpose: Implement the FanTRIAC package once the gating HW +
      compliance evidence lands.
    - Notes: `packages/expansions/fan_triac.yaml` retained as-is in the
      meantime.

28. **PRODUCT-TRIAC-002**
    - Status: Deferred (PR #501 docs-only); blocked on PACKAGE-TRIAC-001
    - Purpose: Implement the FanTRIAC product YAML once PACKAGE-TRIAC-001
      lands.

29. **WF-TRIAC-001 — In-repo wrapper/catalog/build slice**
    - Status: Blocked on PRODUCT-TRIAC-002
    - Purpose: Add the in-repo WebFlash wrapper, compatibility entry, and
      build matrix row for the FanTRIAC product. (This is the
      esphome-public-owned slice — the WebFlash-runtime import is tracked
      separately under cross-repo dependencies as WF-IMPORT-TRIAC-001.)
    - Notes: Listed here, not under cross-repo dependencies, because it
      touches `products/webflash/`, `config/`, and the build matrix in this
      repo.

30. **RELEASE-TRIAC-001**
    - Status: Blocked on WF-TRIAC-001 and COMPLIANCE-001
    - Purpose: Release artifact + release-proof entries for the FanTRIAC
      product, contingent on compliance sign-off.

31. **PRODUCT-DEP-002**
    - Status: Planned / housekeeping
    - Purpose: Continue dependency / toolchain alignment work (pre-commit
      tooling, ESPHome pin, Python tooling) without changing functional
      behavior.
    - Notes: Must not destabilize Release-One.

32. **CI-TOOLCHAIN-001**
    - Status: Planned / housekeeping
    - Purpose: CI toolchain alignment follow-ups (workflow images, action
      versions, ESPHome version pinning consistency).
    - Notes: Workflow files are otherwise frozen; this PR scopes only to
      toolchain alignment.

## Cross-repo dependencies

These items are owned by the WebFlash repository and tracked there in its
own `UPCOMING_PR.md`. They are listed here only to keep cross-repo coupling
visible. Do not implement them from this repo.

- **WF-IMPORT-RELAY-001** — WebFlash-side import of the Relay product
- **WF-IMPORT-PWM-001** — WebFlash-side import of the PWM product
- **WF-IMPORT-DAC-001** — WebFlash-side import of the DAC product
- **WF-IMPORT-POWER-400-001** — WebFlash-side import of the S360-400 power
  product
- **WF-IMPORT-POE-410-001** — WebFlash-side import of the S360-410 PoE
  product
- **WF-HW-TEST-002** — WebFlash-side hardware test follow-up
- **WF-LED-STABLE-001** — WebFlash-side LED preview→stable promotion
  follow-up
- **WF-REQUIRED-001** — WebFlash-side REQUIRED_CONFIGS reconciliation
- **WF-KIT-LED-001** — WebFlash-side LED kit follow-up
- **WF-IMPORT-TRIAC-001** — WebFlash-side import of the FanTRIAC product
- **WF-PRODUCT-005** — WebFlash-side product follow-up

## Recently uploaded evidence

- **S360-400-R4.pdf** — ingested by **HW-ASSETS-400** (PR #514);
  committed at `docs/hardware/schematics/S360-400-R4.pdf`
  (461,206 bytes; SHA256
  `295e3ec9192603fd4ca7d89b8cda68777e5cb8e9713ed8b0fba2316babb0e765`)
  with curated artifact index at
  `docs/hardware/artifacts/S360-400-R4.md`. Consumed by
  **HW-PINMAP-400-FOLLOWUP** (PR #515) under
  `docs/hardware/s360-400-r4-power.md` to produce a schematic-backed
  partial audit.
- **S360-410-R4.pdf** — ingested by **HW-ASSETS-410** (PR #516);
  committed at `docs/hardware/schematics/S360-410-R4.pdf`
  (975,137 bytes; SHA256
  `4a8b7a3b2a89006a9332eaa486743f687aaedc4b6bb807c6b25670f742ac2414`)
  with curated artifact index at
  `docs/hardware/artifacts/S360-410-R4.md`. Consumed by
  **HW-PINMAP-410-FOLLOWUP** (PR #517) under
  `docs/hardware/s360-410-r4-poe.md` to produce a schematic-backed
  partial audit (status promoted from
  `pending — schematic/design evidence required` to
  `partial — schematic evidence available; package reconciliation,
  PoE PD controller / magnetics / buck / isolated DC/DC / harness
  identity evidence pending`). The package-header vs schematic
  part-identity disagreement (whole-module `Ag9712M / Silvertel
  Ag9700 / or similar` vs discrete
  `TPS2378DDAR / TX4138 / F0505S-2WR2 / RJP-003TC1(LPJ4112CNL)`) is
  recorded but **not** resolved — BOM evidence is required before
  `PACKAGE-POE-410-001` can resolve it.
- **No new evidence committed for `CORE-ABSTRACT-BUS-001C`
  preconditions (2026-05-19 re-check).** The 2026-05-19
  `CORE-ABSTRACT-BUS-001C` investigation pass (this PR) re-checked
  every precondition and confirmed that none has been satisfied
  since the 2026-05-18 `S360-100-BENCH-001` re-check: no
  operator-attributed silkscreen captures of Core `J4` / Core
  `J10` / RoomIQ `J6` pin orders are committed; no RoomIQ / AirIQ
  / VentIQ package rebind plan has been drafted; no
  expansion-GPIO bench evidence or documented retirement decision
  for the `expansion_gpio*` abstraction is recorded; no ESP32-S3
  `GPIO3` strap-pin boot-behaviour characterisation against
  populated `S360-310-R4` + `S360-100-R4` is committed; and no
  `tests/test_core_abstract_bus.py` scaffold exists. The next
  evidence-bearing PR against `001C` should appear when one of
  those six gates lands. See
  `docs/hardware/core-abstract-bus-reconciliation.md` §`### 2026-05-19 — CORE-ABSTRACT-BUS-001C investigation pass`
  and `docs/cleanup-audit.md` §CORE-ABSTRACT-BUS-001C update.
- **No new evidence committed for `PACKAGE-POWER-400-001`
  preconditions (2026-05-19 re-check).** The 2026-05-19
  `PACKAGE-POWER-400-001` investigation pass (this PR) re-checked
  every precondition and confirmed that none has been satisfied
  since the 2026-05-19 `HW-PINMAP-400-FOLLOWUP` re-check (PR
  #515): no BOM line item with manufacturer + part number +
  revision for `PS1` is committed (the three-way catalog
  `HLK-5M05` vs package header `HLK-PM01 or similar` vs schematic
  `PS1 = HLK-10M05` disagreement therefore stays unresolved); no
  BOM lines for `F1 A250-1200` / `RV1 10D391K` / `C1 470nF` /
  `C5..C8` / `J1` / `J2` are committed; no operator-attributed
  silkscreen captures of the module-side `J1` 1-to-3 pin order or
  the module-side `J2` 1-to-2 pin order are committed; no KiCad
  PCB source / gerbers / board photos sufficient to measure
  creepage / clearance between AC LINE / NEUTRAL /
  `Earth_Protective` / secondary `+5VP` / `GND` are committed; no
  bench / load / thermal / inrush / insulation / Hi-pot /
  earth-continuity / leakage / EMI / EMC measurements against a
  populated `S360-400-R4` board are committed; no separate
  JSON-only PR for `S360-400` `schematic_status` promotion has
  landed (`config/hardware-catalog.json` line 110 stays
  `schematic_status: cataloged_unverified` with no
  `schematic_file`); and no `COMPLIANCE-001` `S360-400` slice
  mains-voltage UK / EU sign-off has landed since PR #506. The
  next evidence-bearing PR against `PACKAGE-POWER-400-001` should
  appear when one of those five gates lands. See
  `docs/hardware/s360-400-r4-power.md`
  §`### 2026-05-19 — PACKAGE-POWER-400-001 investigation pass`
  and `docs/cleanup-audit.md` §`PACKAGE-POWER-400-001 update`.

## Do-not-change guardrails

This tracking PR must not alter any of the following:

- Functional source files
- Catalogs (hardware, product, WebFlash compatibility, build matrix)
- Packages (`packages/**`)
- Product definitions (`products/**`, excluding `products/webflash/**`
  wrappers below)
- WebFlash wrappers (`products/webflash/**`)
- Build matrices (`config/webflash-builds.json`, related config)
- Release artifacts (firmware binaries, release notes, release-proof files)
- Imports (anything WebFlash-owned)
- Firmware files (`firmware/**`)
- Manifests (`manifest.json`, `firmware/sources.json`)
- Tests (`tests/**`)
- Workflows (`.github/workflows/**`)
- Generated outputs (anything produced by `scripts/**` or test generators)
- Components (`components/**`) and includes (`include/**`)
- `docs/cleanup-audit.md` and any other existing documentation file

Tracker-update PRs touch this file and, where the queue state change
requires it, the related audit / cleanup docs cross-linked from the
queue row being updated. Changes to functional source / catalog /
package / product / WebFlash / test / firmware / workflow files
require a separate scoped PR with its own gate evidence.

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
- **HW-ASSETS-410** is the work item for this PR (artifact ingest
  in progress / PR open — PR number pending). It commits the
  uploaded `S360-410-R4` schematic PDF byte-identically at
  `docs/hardware/schematics/S360-410-R4.pdf` (975,137 bytes;
  SHA256 `4a8b7a3b2a89006a9332eaa486743f687aaedc4b6bb807c6b25670f742ac2414`)
  and adds the curated artifact index at
  `docs/hardware/artifacts/S360-410-R4.md`. Records visible schematic
  content (KiCad 10.0.3 single-sheet A4 export; title-block file
  `S360-410-R4.kicad_sch`; "PoE Power Supply" + "Galvanic Isolated
  Part" sections; `LAN_CON1 RJP-003TC1(LPJ4112CNL)` 10/100 BASE-TX
  filter connector module with 2x1000pF/2KV Bob-Smith bridge +
  2x75Ω terminations; `U1 TPS2378DDAR(HSOIC-8)` PoE PD controller
  with `R1 24.9k` detection signature, `R2 1.27k` classification
  programming (`Class=0 (0.44 to 12.95W)`), `D1 SMAJ58A` TVS, `C2
  15uf` CBULK, `R5 0.03R` current sense; `U2 TX4138(ESOIC-8)` buck
  with `R3 9.1k` / `R4 9.1k` paired current-limit, `R6 4.7R`, `R7
  10.5k` (Rd) / `R8 56.2k` (Rc), `L1 33uH` inductor, `D2 ss510`
  Schottky catch, `C6 470u` output bulk, formula `Vout=0.8*(1+Rc/Rd)`;
  `DCDC1 F0505S-2WR2(SIP-7)` isolated 5V→5V DC/DC with `AM1D-0505S-NZ`
  annotated as alternate; `J3` 2-pin "Connection to Cores" output
  pins 1 / 2 = `+5VP` / `GND`; `D3 Green` status LED on buck output;
  four mounting holes `H1`..`H4` each labelled `Earth`). No
  `schematic_status` promotion, no `schematic_file` set, no package /
  product / WebFlash / build / release / import edit. The package
  header in `packages/hardware/power_poe.yaml` (`Ag9712M / Silvertel
  Ag9700 / or similar`) is **not** reconciled against the
  schematic-shown `TPS2378DDAR / TX4138 / F0505S-2WR2 /
  RJP-003TC1(LPJ4112CNL)` parts — that reconciliation belongs to
  `PACKAGE-POE-410-001` after BOM lands. The Release-One
  "schematic verification pending" caveat in
  `docs/release-one-hardware-audit.md` Findings → PoE PSU is
  **preserved verbatim**. PoE is SELV; `S360-410` is **not** in
  scope for COMPLIANCE-001.
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

## Active / upcoming esphome-public queue

Listed in working priority order. WebFlash-owned import PRs are kept out of
this table; see **Cross-repo dependencies**. The only `WF-`-prefixed entry
that appears below is **WF-TRIAC-001**, which is the in-repo
wrapper/catalog/build slice (not a WebFlash-runtime import).

1. **CORE-ABSTRACT-BUS-001C — UART / status LED / PIR / expansion GPIO + ALS_INT rebind**
   - Status: Next / systemic blocker (must land first to free `GPIO3`
     for the relay slice)
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
   - Notes: Blocked on S360-100-BENCH-001 silkscreen evidence (Core
     `J4` / `J10` and RoomIQ `J6` pin orders); RoomIQ / AirIQ / VentIQ
     package rebind plan; expansion-GPIO bench evidence (or a
     documented decision to retire the `expansion_gpio*` abstraction);
     `tests/test_core_abstract_bus.py` scaffolding; re-validation pass
     for every product consuming any affected Core package
     (`sense360_core_ceiling.yaml`, `sense360_core.yaml`,
     `sense360_core_mapping.yaml`, `sense360_core_poe.yaml`,
     `sense360_core_wall.yaml`). Plan recorded in
     `docs/hardware/core-abstract-bus-reconciliation.md` §CORE-ABSTRACT-BUS-001C.

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
   - Status: Independent of 001A / 001C ordering; should land before
     PACKAGE-PWM-001 / PACKAGE-DAC-001
   - Purpose: Collapse the duplicated `halo_i2c` / `expansion_i2c` /
     `i2c0` / `i2c1` / `i2c_primary` / `i2c_expander` bus definitions
     in the Core abstract packages down to the **single shared I²C
     bus** on `IO48` (SDA) / `IO45` (SCL) that the `S360-100-R4`
     schematic actually exposes. Realign every downstream expansion
     package that currently references one of the old bus ids.
   - Notes: Blocked on a downstream-consumer audit (every package and
     product YAML that resolves an `*_i2c_id` substitution), a
     canonical bus-id naming decision, and pin-pinning test
     coverage. Plan recorded in
     `docs/hardware/core-abstract-bus-reconciliation.md` §CORE-ABSTRACT-BUS-001B.

4. **HW-ASSETS-410 — Add curated S360-410 PoE PSU artifacts**
   - Status: **In flight (this PR) — PR open / PR number pending**
   - Purpose: Artifact ingest. Commit the uploaded `S360-410-R4`
     schematic PDF byte-identically at
     `docs/hardware/schematics/S360-410-R4.pdf` (975,137 bytes;
     SHA256 `4a8b7a3b2a89006a9332eaa486743f687aaedc4b6bb807c6b25670f742ac2414`)
     and add the curated artifact index at
     `docs/hardware/artifacts/S360-410-R4.md`. Records visible
     schematic content (KiCad 10.0.3 single-sheet A4 export;
     title-block file `S360-410-R4.kicad_sch`; "PoE Power Supply" +
     "Galvanic Isolated Part" section labels; `LAN_CON1
     RJP-003TC1(LPJ4112CNL)` 10/100 BASE-TX filter connector module
     with 2x1000pF/2KV Bob-Smith bridge caps + 2x75Ω terminations +
     `C3 1nF` shield bridge; `U1 TPS2378DDAR(HSOIC-8)` PoE PD
     controller with `R1 24.9k` detection signature, `R2 1.27k`
     classification programming (`Class=0 (0.44 to 12.95W)`), `D1
     SMAJ58A` TVS, `C2 15uf` CBULK, `R5 0.03R` current sense; `U2
     TX4138(ESOIC-8)` buck with `R3 9.1k` / `R4 9.1k` paired current
     limit, `R6 4.7R`, `R7 10.5k` (Rd) / `R8 56.2k` (Rc), `L1 33uH`
     inductor, `D2 ss510` Schottky, `C6 470u` output bulk, formula
     `Vout=0.8*(1+Rc/Rd)`; `DCDC1 F0505S-2WR2(SIP-7)` isolated 5V→5V
     DC/DC with `AM1D-0505S-NZ` annotated as alternate; `J3` 2-pin
     "Connection to Cores" output with pin 1 = `+5VP`, pin 2 = `GND`;
     `D3 Green` status LED on buck output; four mounting holes
     `H1`..`H4` each labelled `Earth`). Refreshes the `S360-410`
     cross-link narrative in
     [`docs/hardware/board-readiness-matrix.md`](docs/hardware/board-readiness-matrix.md),
     [`docs/hardware/remaining-board-documentation-audit.md`](docs/hardware/remaining-board-documentation-audit.md),
     [`docs/hardware/hardware-artifact-policy.md`](docs/hardware/hardware-artifact-policy.md)
     Follow-up PR sequence item #8,
     [`docs/hardware/package-readiness-matrix.md`](docs/hardware/package-readiness-matrix.md),
     [`docs/cleanup-audit.md`](docs/cleanup-audit.md), and adds a
     cross-link addendum to
     [`docs/hardware/s360-410-r4-poe.md`](docs/hardware/s360-410-r4-poe.md)
     (audit status remains
     `pending — schematic/design evidence required`). No package /
     product / WebFlash / build / release / import edits. No
     `schematic_status` promotion. No `schematic_file` set. The
     Release-One PoE "schematic verification pending" caveat in
     [`docs/release-one-hardware-audit.md` Findings → PoE PSU](docs/release-one-hardware-audit.md#findings)
     is **preserved verbatim**; LED preview entry
     (`Ceiling-POE-VentIQ-RoomIQ-LED`) is not requalified; FanTRIAC
     stays blocked under HW-005; PoE is SELV and `S360-410` is
     **not** in scope for COMPLIANCE-001. HW-002 Open Question #6 /
     S360-100-BENCH-001 J2-harness identity stay
     `pending — bench/manufacturing evidence required`.

5. **HW-PINMAP-410-FOLLOWUP — Complete S360-410 PoE PSU mapping**
   - Status: Next / after HW-ASSETS-410 merges
   - Purpose: Docs-only schematic-backed reconciliation. Consume the
     HW-ASSETS-410 module-side schematic evidence and promote
     `docs/hardware/s360-410-r4-poe.md` from
     `pending — schematic/design evidence required` to
     `partial — schematic evidence available; package reconciliation,
     PoE PD controller / magnetics / buck / isolated DC/DC / harness
     identity pending`. Reconcile the package-header `Ag9712M /
     Silvertel Ag9700 / or similar` hint against the schematic-shown
     `TPS2378DDAR / TX4138 / F0505S-2WR2 / RJP-003TC1(LPJ4112CNL)`
     parts (BOM-bound; resolution owed to `PACKAGE-POE-410-001`).
     Refresh the `S360-410` narrative across the readiness matrices.
     No package / product / WebFlash / build / release / import
     edits. No `schematic_status` promotion. No `schematic_file` set.
     The preserved Release-One PoE caveat stays verbatim.
   - Notes: HW-002 Open Question #6 / S360-100-BENCH-001 J2 harness
     identity is the bench-side companion; resolution is **not**
     in scope for HW-PINMAP-410-FOLLOWUP and is owed independently.

6. **PACKAGE-POWER-400-001**
   - Status: Planned / after HW-PINMAP-400-FOLLOWUP
   - Purpose: Stand up the S360-400 power board package wiring once the
     pin/package audit is schematic-backed.
   - Notes: Must not destabilize Release-One; coordinate with the
     CORE-ABSTRACT-BUS-001 slices (001A/001B/001C) for any shared
     Core variables the power package touches.

7. **PRODUCT-POWER-400-001**
   - Status: Planned / after PACKAGE-POWER-400-001
   - Purpose: Add the S360-400 product YAML against the new package.
   - Notes: No WebFlash exposure until WEBFLASH-POWER-400-001.

8. **WEBFLASH-POWER-400-001**
   - Status: Planned / after PRODUCT-POWER-400-001
   - Purpose: Add the WebFlash wrapper, compatibility entry, and build
     matrix row for the S360-400 product.
   - Notes: Pairs with WebFlash-side WF-IMPORT-POWER-400-001 — see
     cross-repo dependencies.

9. **RELEASE-POWER-400-001**
   - Status: Planned / after WEBFLASH-POWER-400-001
   - Purpose: Produce the release artifact + release-proof entries for the
     S360-400 product.
   - Notes: Subject to existing release-artifact readiness gates.

10. **PACKAGE-POE-410-001**
    - Status: Planned / after HW-PINMAP-410-FOLLOWUP
    - Purpose: Stand up the S360-410 PoE PSU package wiring once the
      pin/package audit is schematic-backed.
    - Notes: Must not implicitly requalify Release-One.

11. **PRODUCT-POE-410-001**
    - Status: Planned / after PACKAGE-POE-410-001
    - Purpose: Add the S360-410 product YAML against the new package.
    - Notes: No WebFlash exposure until WEBFLASH-POE-410-001.

12. **WEBFLASH-POE-410-001**
    - Status: Planned / after PRODUCT-POE-410-001
    - Purpose: Add the WebFlash wrapper, compatibility entry, and build
      matrix row for the S360-410 product.
    - Notes: Pairs with WebFlash-side WF-IMPORT-POE-410-001.

13. **RELEASE-POE-410-001**
    - Status: Planned / after WEBFLASH-POE-410-001
    - Purpose: Produce the release artifact + release-proof entries for the
      S360-410 product.
    - Notes: Subject to existing release-artifact readiness gates.

14. **PRODUCT-RELAY-001**
    - Status: Blocked on CORE-ABSTRACT-BUS-001A (relay_pin slice;
      itself blocked on 001C) + PACKAGE-RELAY-001 implementation
    - Purpose: Add the S360-310 Relay product YAML once the Relay package is
      implemented (not the current docs-only deferral state).
    - Notes: Implementation deferred per PR #511 (PACKAGE-RELAY-001
      docs-only deferral) and now further gated by the
      CORE-ABSTRACT-BUS-001A relay_pin slice landing.

15. **WEBFLASH-RELAY-001**
    - Status: Blocked on PRODUCT-RELAY-001 (which is itself blocked on
      CORE-ABSTRACT-BUS-001A)
    - Purpose: Add the WebFlash wrapper, compatibility entry, and build
      matrix row for the Relay product.
    - Notes: Pairs with WebFlash-side WF-IMPORT-RELAY-001.

16. **RELEASE-RELAY-001**
    - Status: Blocked on WEBFLASH-RELAY-001 (ultimately on
      CORE-ABSTRACT-BUS-001A)
    - Purpose: Produce the release artifact + release-proof entries for the
      Relay product.

17. **PACKAGE-PWM-001**
    - Status: Blocked on HW-PINMAP-311-FOLLOWUP returning sufficient evidence
    - Purpose: Stand up / re-stand up the S360-311 PWM package wiring once
      the pin/package audit is no longer partial.
    - Notes: Also affected by CORE-ABSTRACT-BUS-001B (shared I²C bus
      consolidation) and CORE-ABSTRACT-BUS-001C (`expansion_gpio1`
      / `expansion_gpio2` rebind that `fan_pwm.yaml` consumes via
      `${fan_pwm_pin}` / `${fan_tach_pin}`).

18. **PRODUCT-PWM-001**
    - Status: Blocked on PACKAGE-PWM-001
    - Purpose: Add / re-align the S360-311 PWM product YAML.

19. **WEBFLASH-PWM-001**
    - Status: Blocked on PRODUCT-PWM-001
    - Purpose: WebFlash wrapper, compatibility entry, build matrix row.
    - Notes: Pairs with WebFlash-side WF-IMPORT-PWM-001.

20. **RELEASE-PWM-001**
    - Status: Blocked on WEBFLASH-PWM-001
    - Purpose: Release artifact + release-proof entries for the PWM product.

21. **PACKAGE-DAC-001**
    - Status: Blocked on HW-PINMAP-312-FOLLOWUP returning sufficient evidence
    - Purpose: Stand up / re-stand up the S360-312 DAC (GP8403) package
      wiring once the pin/package audit is no longer partial.
    - Notes: Also affected by CORE-ABSTRACT-BUS-001B (the GP8403
      DAC is I²C-attached, so it consumes whichever bus id 001B
      settles on).

22. **PRODUCT-DAC-001**
    - Status: Blocked on PACKAGE-DAC-001
    - Purpose: Add / re-align the S360-312 DAC product YAML.

23. **WEBFLASH-DAC-001**
    - Status: Blocked on PRODUCT-DAC-001
    - Purpose: WebFlash wrapper, compatibility entry, build matrix row.
    - Notes: Pairs with WebFlash-side WF-IMPORT-DAC-001.

24. **RELEASE-DAC-001**
    - Status: Blocked on WEBFLASH-DAC-001
    - Purpose: Release artifact + release-proof entries for the DAC product.

25. **S360-300-BENCH-001**
    - Status: Pending bench evidence
    - Purpose: LED ring bench / verification gate for S360-300.
    - Notes: Blocks the LED stable chain together with the WebFlash-owned
      operator-proof follow-ups.

26. **RELEASE-007**
    - Status: Planned / promotion of LED stable
    - Purpose: Promote the LED package + product from preview to stable
      once S360-300-BENCH-001 and the WebFlash operator-proof follow-ups
      land.
    - Notes: Subject to preview-to-stable promotion gates.

27. **HW-005 / HW-PINMAP-320-FOLLOWUP**
    - Status: Open / evidence-pass re-checked (PR #505); audit remains
      partial
    - Purpose: Resolve the S360-320 FanTRIAC pin/package collisions and
      provide the schematic/interrupt-capable GPIO evidence needed to
      progress the FanTRIAC chain.
    - Notes: Gating PACKAGE-TRIAC-001 implementation.

28. **COMPLIANCE-001**
    - Status: Open / not cleared (PR #506 re-checked, no sign-off yet)
    - Purpose: Land the S360-320 mains-voltage advanced / manual-warning
      compliance sign-off.
    - Notes: Gating PRODUCT-TRIAC-002 / FanTRIAC release exposure.

29. **PACKAGE-TRIAC-001**
    - Status: Deferred (PR #502 docs-only); blocked on HW-005 /
      HW-PINMAP-320-FOLLOWUP / COMPLIANCE-001
    - Purpose: Implement the FanTRIAC package once the gating HW +
      compliance evidence lands.
    - Notes: `packages/expansions/fan_triac.yaml` retained as-is in the
      meantime.

30. **PRODUCT-TRIAC-002**
    - Status: Deferred (PR #501 docs-only); blocked on PACKAGE-TRIAC-001
    - Purpose: Implement the FanTRIAC product YAML once PACKAGE-TRIAC-001
      lands.

31. **WF-TRIAC-001 — In-repo wrapper/catalog/build slice**
    - Status: Blocked on PRODUCT-TRIAC-002
    - Purpose: Add the in-repo WebFlash wrapper, compatibility entry, and
      build matrix row for the FanTRIAC product. (This is the
      esphome-public-owned slice — the WebFlash-runtime import is tracked
      separately under cross-repo dependencies as WF-IMPORT-TRIAC-001.)
    - Notes: Listed here, not under cross-repo dependencies, because it
      touches `products/webflash/`, `config/`, and the build matrix in this
      repo.

32. **RELEASE-TRIAC-001**
    - Status: Blocked on WF-TRIAC-001 and COMPLIANCE-001
    - Purpose: Release artifact + release-proof entries for the FanTRIAC
      product, contingent on compliance sign-off.

33. **PRODUCT-DEP-002**
    - Status: Planned / housekeeping
    - Purpose: Continue dependency / toolchain alignment work (pre-commit
      tooling, ESPHome pin, Python tooling) without changing functional
      behavior.
    - Notes: Must not destabilize Release-One.

34. **CI-TOOLCHAIN-001**
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
- **S360-410-R4.pdf** — ingested by **HW-ASSETS-410** (this PR);
  committed at `docs/hardware/schematics/S360-410-R4.pdf`
  (975,137 bytes; SHA256
  `4a8b7a3b2a89006a9332eaa486743f687aaedc4b6bb807c6b25670f742ac2414`)
  with curated artifact index at
  `docs/hardware/artifacts/S360-410-R4.md`. Reserved for consumption
  by **HW-PINMAP-410-FOLLOWUP** (the next S360-410 step after merge)
  under `docs/hardware/s360-410-r4-poe.md` to produce a
  schematic-backed partial audit. Until then, the HW-PINMAP-410
  audit doc status stays `pending — schematic/design evidence
  required` (cross-link addendum only by this PR).

**Note:** Consumption of `S360-410-R4.pdf` into the HW-PINMAP-410
audit doc is reserved for the dedicated `HW-PINMAP-410-FOLLOWUP` PR.
This PR scopes only to artifact ingest (PDF + curated artifact index +
minimal cross-link refresh across the readiness matrices). No
`schematic_status` promotion. No `schematic_file` set. No package /
product / WebFlash / build / release / import edit. The Release-One
PoE "schematic verification pending" caveat is preserved verbatim.

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

The only change introduced by this PR is the creation of this
`UPCOMING_PR.md` file at the repository root.

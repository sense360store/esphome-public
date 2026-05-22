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
- **CORE-ABSTRACT-BUS-001C** landed via **CORE-ABSTRACT-BUS-001C-IMPLEMENT-001 / PR #557**
  on 2026-05-21 (the schematic-backed rebind plan from PR #554 applied
  to the affected Core abstract packages plus
  `packages/expansions/comfort_ceiling.yaml`,
  `packages/expansions/gpio_expander_sx1509.yaml`, and the affected
  presence packages; pin-pinning regression scaffold
  `tests/test_core_abstract_bus.py` added). **CORE-ABSTRACT-BUS-001A**
  then landed via PR #558 on 2026-05-21 — the schematic-correct
  `relay_pin: GPIO3` value is now bound in
  `packages/hardware/sense360_core.yaml`,
  `packages/hardware/sense360_core_ceiling.yaml`,
  `packages/hardware/sense360_core_mapping.yaml`,
  `packages/hardware/sense360_core_poe.yaml`, and
  `packages/hardware/sense360_core_wall.yaml`. The
  `tests/test_core_abstract_bus.py` scaffold is extended with
  `RelayPinRebindTests` and `MainRelaySwitchBindingTests` to lock the
  rebind against future regression. Voice-variant Core packages
  (`sense360_core_voice_ceiling.yaml` and
  `sense360_core_voice_wall.yaml`) remain at the pre-001A
  `relay_pin: GPIO4` value — they are deliberately out of scope for
  the 001A slice. Relay package implementation
  (`PACKAGE-RELAY-001`) cannot proceed until S360-100-BENCH-001
  silkscreen evidence, the general ESP32-S3 `GPIO3` strap-pin
  boot-behaviour bench characterisation, and silkscreen / harness /
  `K1` BOM evidence for `S360-310` land. The 001A slice did **not**
  prove Relay load / contact / `K1` rating, did **not** complete
  `PACKAGE-RELAY-001`, did **not** release a Relay artifact, and
  did **not** unblock WebFlash import by itself.
- **PACKAGE-RELAY-001-READINESS-REFRESH** (this PR) is a docs /
  evidence / readiness-only re-evaluation of the `PACKAGE-RELAY-001`
  blocker set against the post-001C / post-001A repo state. It
  records that the Core abstract-bus substitution-layer blockers are
  **resolved** (the `GPIO3` collision; the `relay_pin: IO3` vs
  `GPIO4` vs `GPIO10` disagreement; the absence of a pin-pinning
  regression for `relay_pin`; the structural correctness check on
  `fan_relay.yaml`) and separates them from the still-open
  **hardware-evidence blockers** (S360-100 Core `J4` silkscreen /
  pin-1 orientation; S360-310 module-side `J2` / `J1` silkscreen
  pin-1 orientation; `J1` `NO` / `COM` / `NC` mapping; Core ↔
  module 3-pin harness identity; `K1` BOM identity; `K1`
  contact-current rating; Relay load / contact proof; general
  ESP32-S3 `GPIO3` strap-pin boot-behaviour characterisation — the
  operator-confirmed pair-scoped boot OK in
  `docs/hardware/core-abstract-bus-001c-rebind-plan.md` decisions
  #16 / #17 is **not** a generic claim). The conservative
  recommended next PR is an `S360-310` bench-evidence-capture slice
  (silkscreen / harness / `K1` BOM / load-contact proof; general
  `GPIO3` strap-pin boot characterisation), **not**
  `PACKAGE-RELAY-001` implementation, **not** a Relay product YAML,
  **not** a WebFlash wrapper, **not** a compile-only target, and
  **not** a release artifact. The readiness table (blocker × previous
  state × current state × evidence source × still blocks
  PACKAGE-RELAY-001? × what unblocks it) is recorded at
  `docs/hardware/s360-310-r4-relay.md` §`PACKAGE-RELAY-001 readiness
  refresh after CORE-ABSTRACT-BUS-001C / 001A`. The `fan_relay.yaml`
  row in `docs/hardware/package-readiness-matrix.md` is unchanged at
  `schematic-evidence-pending` + `needs-package-reconciliation` (its
  notes are refreshed to record the substitution-layer resolution).
  No `packages/**`, `products/**`, `products/webflash/**`,
  `config/**`, `scripts/**`, `.github/workflows/**`,
  `components/**`, `include/**`, `firmware/**`, `manifest.json`,
  `firmware/sources.json`, `tests/**` edit; no `webflash_build_matrix`
  flip; no `schematic_status` / `schematic_file` promotion; no
  COMPLIANCE-001 movement; Release-One stays
  `Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`; LED preview
  stays `Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`; FanTRIAC stays
  `blocked` / `HW-005`.
- **S360-310-BENCH-001** (this PR) is the
  evidence-capture-**checklist**-only follow-up to
  `PACKAGE-RELAY-001-READINESS-REFRESH` (PR #559). It adds a new
  top-line §`S360-310-BENCH-001 — Relay bench evidence` section to
  `docs/hardware/s360-310-r4-relay.md` enumerating ten
  `PACKAGE-RELAY-001` hardware-evidence rows against the populated
  `S360-310-R4` + `S360-100-R4` pair: S360-100 Core `J4` silkscreen /
  pin-1 orientation; S360-310 Relay `J2` 1-to-3 pin order; S360-310
  Relay `J1` `NO` / `COM` / `NC` mapping; Core `J4` ↔ Relay `J2`
  harness identity (straight-through or keyed); `K1` BOM identity /
  manufacturer / part number; `K1` contact-current rating; expected
  controlled load type; relay boot state with `S360-100-R4` +
  `S360-310-R4` attached; ESP32-S3 `GPIO3` strap-pin boot
  characterisation generalisation status; Relay load / contact proof
  result. **No physical evidence has been supplied.** Every one of
  the ten rows is recorded as `pending — bench evidence required`;
  no operator, no review date, no observed silkscreen pin-1 marks,
  no harness conductor-by-conductor trace, no `K1` part-number
  reading, no coil-drive scope capture, no contact-side continuity
  measurement, no oscilloscope-traced ESP32-S3 `GPIO3` strap-state
  capture is on file. The pair-scoped operator boot-OK observation
  in `docs/hardware/core-abstract-bus-001c-rebind-plan.md`
  decisions #16 / #17 is cross-referenced for completeness and is
  **not** promoted to a generic claim about ESP32-S3 `GPIO3`
  strap-pin boot behaviour. The `fan_relay.yaml` row in
  `docs/hardware/package-readiness-matrix.md` stays at
  `schematic-evidence-pending` + `needs-package-reconciliation`; the
  Follow-up owner chain is refreshed to insert this PR between
  `PACKAGE-RELAY-001-READINESS-REFRESH` (PR #559) and the next
  S360-310 bench-evidence-capture slice that actually commits
  artifacts. **`PACKAGE-RELAY-001` stays blocked at the evidence
  layer.** No `packages/**`, `products/**`, `products/webflash/**`,
  `config/**`, `scripts/**`, `.github/workflows/**`,
  `components/**`, `include/**`, `firmware/**`, `manifest.json`,
  `firmware/sources.json`, `tests/**` edit; no `webflash_build_matrix`
  flip; no `artifact_name` / `webflash_wrapper` / `config_string` /
  `release_one_required_configs` / `lifecycle_statuses` /
  `canonical_modules` / `canonical_power` / `forbidden_tokens` /
  `REQUIRED_CONFIGS` / kit change; no `schematic_status` /
  `schematic_file` promotion (`S360-310` stays
  `cataloged_unverified`); no COMPLIANCE-001 movement; no Release-One
  change (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`); no LED
  preview change (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`); no
  FanTRIAC change (`blocked` / `HW-005`). **No claim of Relay load /
  contact / `K1` rating proof.** **No WebFlash import-readiness
  claim.** **No hardware release-readiness claim.** **No
  `RELEASE-RELAY-001` unblock claim.** **No `PACKAGE-RELAY-001`
  implementation-readiness claim.** No edit to `fan_relay.yaml`. No
  Relay product YAML. No WebFlash wrapper. No compile-only target.
  No release artifact / tag / checksum / build-info manifest.
- **S360-310-BENCH-EVIDENCE-001** (this PR) is the
  evidence-population follow-up to `S360-310-BENCH-001` (PR #560).
  It populates the ten enumerated `PACKAGE-RELAY-001`
  hardware-evidence rows in `docs/hardware/s360-310-r4-relay.md`
  §`S360-310-BENCH-001 — Relay bench evidence` from
  operator-attested, BOM-backed, and public-reference-backed
  sources supplied by operator `@wifispray` (Wifi Guy) on
  2026-05-22. **Operator-attested** (against the populated
  `S360-100-R4` + `S360-310-R4` pair under operator review):
  Core-side `J4` pin order `+5V` / `Relay` / `GND`; module-side
  `J2` pin order `+5V` / `Relay` / `GND`; module-side `J1` mapping
  `NO` / `COM` / `NC`; 3-pin Core ↔ module harness straight-through
  with J4-1↔J2-1 / J4-2↔J2-2 / J4-3↔J2-3; expected controlled load
  type UK mains Manrose `MT100S`-class extractor fan (operator
  self-report of installation posture "as per UK standards", **not**
  an independent compliance sign-off); relay boot state de-energized
  across 10 boot cycles × 4 power paths (USB, PoE, 5 V PSU, 240 V
  supply path) with firmware `Ceiling-POE-VentIQ-RoomIQ`; relay
  load / contact proof (fan off until relay activates, relay on →
  fan on, relay off → fan off; behaviour consistent with `NO` +
  `COM` wiring; exact terminal use inferred from observed behaviour
  and `J1` mapping unless explicitly photo-proven, which it is not
  in this PR). **BOM-backed** (operator-uploaded
  `S360-310-R4_BOM.xlsx`, uploaded operator-side, **not** committed
  to this repository): `K1` Songle Relay `SRD-05VDC-SL-C` (value
  `SRD-05VDC-SL-C-srd_relay`; footprint
  `greencharge-footprints:RELAY_SRD-05VDC-SL-C`; qty 1).
  **Public-reference-backed** (SRD-style 5 V relay reference /
  datasheet): `K1` contact-current rating
  `10 A @ 250 VAC; 10 A @ 30 VDC`, SPDT (`NO` / `COM` / `NC`
  terminals). **Caveat:** contact-rating evidence only — **not**
  board-level compliance, installation approval, creepage /
  clearance, thermal, EMI, or mains-safety certification.
  **Pair-scoped sufficient for package implementation**: the
  `GPIO3` strap-pin boot-behaviour row is recorded as
  `captured enough for PACKAGE-RELAY-001 implementation` against
  the operator-attested 10 boot cycles × 4 power paths; **caveat**
  that this is **not** a production-wide, multi-unit,
  oscilloscope-traced, compliance, release-readiness, or
  safety-certification claim. **No photo / video / oscilloscope /
  continuity-meter artifacts are attached in this PR.** The
  §`Status-language rules` list is extended with the four new
  status values (`captured — operator-attested`,
  `captured — BOM-backed`, `captured — public-reference-backed`,
  `captured enough for PACKAGE-RELAY-001 implementation`); a new
  §`What this record now unblocks` subsection records the verbatim
  "Implementation-ready at the PACKAGE-RELAY-001 evidence layer"
  caveat block; §`Status` and §`Summary verdict` are refreshed to
  reflect the captured-evidence state; a new 2026-05-22 row is
  appended to §`HW-PINMAP-310-FOLLOWUP audit log`. The
  `fan_relay.yaml` row in `docs/hardware/package-readiness-matrix.md`
  is refreshed to `package-evidence-captured` +
  `implementation-ready at PACKAGE-RELAY-001 evidence layer`, with
  the Allowed-action-now and Follow-up-owner chain refreshed
  accordingly; the §`fan_relay.yaml` / S360-310 detail section's
  bullets are refreshed in parallel. A new 2026-05-22 update
  sub-bullet is appended to the Release-One package-stack
  `relay_pin` finding in `docs/hardware/firmware-package-mapping-audit.md`.
  `PACKAGE-RELAY-001` is now **implementation-ready at the
  package-evidence layer only** — **not** product-ready, **not**
  WebFlash-ready, **not** release-ready, **not** compliance-cleared,
  **not** safe for arbitrary mains installation, **not** verified
  across production batches. The next Relay PR can be
  `PACKAGE-RELAY-001` implementation. `PRODUCT-RELAY-001` /
  `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001`
  stay blocked behind `PACKAGE-RELAY-001`. No `packages/**`,
  `products/**`, `products/webflash/**`, `config/**`, `scripts/**`,
  `.github/workflows/**`, `components/**`, `include/**`,
  `firmware/**`, `manifest.json`, `firmware/sources.json`,
  `tests/**` edit; no `webflash_build_matrix` flip; no
  `artifact_name` / `webflash_wrapper` / `config_string` /
  `release_one_required_configs` / `lifecycle_statuses` /
  `canonical_modules` / `canonical_power` / `forbidden_tokens` /
  `REQUIRED_CONFIGS` / kit change; no `schematic_status` /
  `schematic_file` promotion (`S360-310` stays
  `cataloged_unverified`); no COMPLIANCE-001 movement; no
  Release-One change (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` /
  `stable`); no LED preview change (`Ceiling-POE-VentIQ-RoomIQ-LED`
  / `preview`); no FanTRIAC change (`blocked` / `HW-005`).
  **`S360-100-BENCH-001` is not closed** — the operator-attested
  Core-`J4` pin order is **not** silkscreen / manufacturing
  evidence. **No board-level mains-safety / installation-approval
  / creepage / clearance / thermal / EMI certification claim.**
  **No production-wide / multi-unit / oscilloscope-traced general
  `GPIO3` strap-pin boot-behaviour characterisation claim.** **No
  hardware-stable / release-readiness claim.** No edit to
  `fan_relay.yaml`. No Relay product YAML. No WebFlash wrapper.
  No compile-only target. No release artifact / tag / checksum /
  build-info manifest. The operator-uploaded `S360-310-R4_BOM.xlsx`
  is consumed for the `K1` BOM-backed row only and is **not**
  committed to this repository.
- **PACKAGE-RELAY-001** (this PR) is the **test + readiness
  reconciliation** follow-up after the package-evidence layer
  closed under `S360-310-BENCH-EVIDENCE-001` / PR #561. The
  FanRelay package was already structurally correct
  (`fan_relay_pin: ${relay_pin}` in
  `packages/expansions/fan_relay.yaml` line 27 inherits the parent
  Core abstract package binding, and post-001A `${relay_pin}`
  resolves to the schematic-correct `GPIO3`), so **no YAML rebind
  was required**. The reconciliation is the addition of
  `tests/test_fan_relay_package.py` which pins the FanRelay
  package abstraction against future regression: the package
  parses as YAML; `fan_relay_pin` defaults to `${relay_pin}`; the
  package does **not** hard-code `GPIO3` / `GPIO4` / `GPIO10` or
  any other GPIO on an active line; the `fan_relay_switch` switch
  binds `pin: ${fan_relay_pin}` (the relay output is exposed
  through the substitution layer, not a fixed pin); the five
  non-voice Core abstract packages bind `relay_pin: GPIO3`
  (cross-check against `tests/test_core_abstract_bus.py`); the
  voice-variant Core packages stay at the pre-001A
  `relay_pin: GPIO4` (deliberately out of scope); no FanRelay
  product YAML exists under `products/`; no `FanRelay` token
  exists in `config/webflash-builds.json`. Docs refreshed:
  `docs/hardware/s360-310-r4-relay.md` §Package YAML status
  PACKAGE-RELAY-001 investigation-outcome bullet extended with a
  PACKAGE-RELAY-001 implementation-outcome paragraph; new
  2026-05-22 audit-log row appended to §HW-PINMAP-310-FOLLOWUP
  audit log; `docs/hardware/package-readiness-matrix.md`
  `fan_relay.yaml` row + §`fan_relay.yaml` / S360-310 detail
  section refreshed to `package-implemented` +
  `reconciled-at-package-layer` with the Allowed-action-now and
  Follow-up-owner chain refreshed;
  `docs/hardware/firmware-package-mapping-audit.md` Release-One
  package-stack `relay_pin` bullet appended with a
  PACKAGE-RELAY-001 implementation sub-paragraph; `UPCOMING_PR.md`
  Current queue summary (this bullet), Completed / merged PRs
  (this PR), Active / upcoming queue (PACKAGE-RELAY-001 item #6
  moves from "Evidence-ready" to "Merged"), and Recently uploaded
  evidence refreshed. `PACKAGE-RELAY-001` is now **implemented /
  reconciled at the package layer only**. "Implemented /
  reconciled at the `PACKAGE-RELAY-001` package layer" does
  **not** mean product-ready, WebFlash-ready, release-ready,
  compliance-cleared, safe for arbitrary mains installation, or
  verified across production batches. The next Relay PR is
  `PRODUCT-RELAY-001`, which stays separately gated on
  product-layer compliance / mains-safety / installation /
  production-wide characterisation evidence. **No `products/**`,
  `products/webflash/**`, `config/**`, `scripts/**`,
  `.github/workflows/**`, `components/**`, `include/**`,
  `firmware/**`, `manifest.json`, or `firmware/sources.json`
  edit.** Only `tests/test_fan_relay_package.py` is added under
  `tests/**`; no other test is edited. No `webflash_build_matrix`
  flip; no `artifact_name` / `webflash_wrapper` / `config_string` /
  `release_one_required_configs` / `lifecycle_statuses` /
  `canonical_modules` / `canonical_power` / `forbidden_tokens` /
  `REQUIRED_CONFIGS` / kit change; no `schematic_status` /
  `schematic_file` promotion (`S360-310` stays
  `cataloged_unverified`); no COMPLIANCE-001 movement; no
  Release-One change (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` /
  `stable`); no LED preview change (`Ceiling-POE-VentIQ-RoomIQ-LED`
  / `preview`); no FanTRIAC change (`blocked` / `HW-005`).
  `S360-100-BENCH-001` is **not** closed; `PRODUCT-RELAY-001` /
  `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001`
  stay blocked behind PACKAGE-RELAY-001 → PRODUCT-RELAY-001. No
  Relay product YAML. No WebFlash wrapper. No compile-only target
  for FanRelay. No release artifact / tag / checksum / build-info
  manifest.
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
- **PACKAGE-POWER-400-001** investigation merged as **PR #520** on
  2026-05-19 (docs-only Path A deferral). The pass evaluated whether
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
  PACKAGE-POWER-400-001 PR's scope"). Path B was not useful at
  the time because the only safe comment-only change would be to
  remove the `HLK-PM01 or similar` line altogether without
  claiming `HLK-10M05` (or any replacement) — and PR #515's
  recorded decision was specifically that even that removal
  should wait for BOM, so that the eventual
  `PACKAGE-POWER-400-001` implementation PR can land header
  reconciliation + catalog `description` reconciliation + BOM
  citation as one coordinated change; Path C was unsafe because
  the five preconditions above are open and any header / catalog
  edit without BOM evidence would substitute one unsourced claim
  for another. The investigation outcome confirms
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
- **PRODUCT-POWER-400-001** investigation merged as **PR #521** on
  2026-05-19 (docs-only Path A deferral). The pass evaluated
  whether `PRODUCT-POWER-400-001` could safely proceed now
  (Path C implementation — add a canonical `S360-400` /
  `PWR`-bearing product YAML under
  [`products/`](products/) and a matching entry in
  [`config/product-catalog.json`](config/product-catalog.json)),
  as a documentation / catalog-note-only cleanup PR (Path B —
  for example, tightening the
  [`docs/product-readiness-matrix.md` §PWR-240V / S360-400](docs/product-readiness-matrix.md#pwr-240v--s360-400)
  Follow-up owner chain or the
  [`docs/webflash-exposure-readiness-matrix.md` §Power / S360-400 WebFlash posture](docs/webflash-exposure-readiness-matrix.md#power--s360-400-webflash-posture)
  text), or as a docs-only deferral (Path A), and is
  **confirmed deferred** — six preconditions remain open:
  (1) **`PACKAGE-POWER-400-001` implementation slice has not
  landed** — only the docs-only investigation pass merged as
  PR #520; the underlying package YAML reconciliation, the
  catalog `description` reconciliation, the `S360-400`
  `schematic_status: verified` JSON promotion, and the BOM
  citation that PR #520 enumerated all remain owed to a future
  evidence-bearing `PACKAGE-POWER-400-001` PR; (2) **BOM
  cross-check missing** — same gap PR #520 recorded for the
  package slice; no BOM line item for `PS1` / `F1 A250-1200` /
  `RV1 10D391K` / `C1 470nF` / `C5..C8` / `J1` / `J2`;
  (3) **`S360-400` `schematic_status: verified` JSON PR not
  landed** — `config/hardware-catalog.json` line 110 still
  records `cataloged_unverified` with no `schematic_file`, and
  `tests/test_hardware_catalog.py:53`
  `EXPECTED_STILL_UNVERIFIED_SKUS = frozenset({"S360-320",
  "S360-400"})` actively enforces this state; (4)
  **`COMPLIANCE-001` `S360-400` slice still open** — last
  re-checked PR #506; the mains-voltage UK / EU assessment at
  `docs/compliance/mains-voltage-uk-eu-assessment.md` is not
  cleared, and per the [`docs/product-readiness-matrix.md` Follow-up PR sequence](docs/product-readiness-matrix.md#follow-up-pr-sequence)
  `PRODUCT-POWER-400-001` is explicitly gated on
  "`PACKAGE-POWER-400-001` landed + `COMPLIANCE-001` `S360-400`
  slice closed"; (5) **package / catalog reconciliation owed to
  `PACKAGE-POWER-400-001`** — the three-way `HLK-5M05` /
  `HLK-PM01 or similar` / `HLK-10M05` AC/DC part-identity
  disagreement and the input / output / isolation / protection
  / fusing header text in
  [`packages/hardware/power_240v.yaml`](packages/hardware/power_240v.yaml)
  remain unresolved and BOM-bound, and the catalog
  `description: Mains to 5V using HLK-5M05.` in
  [`config/hardware-catalog.json`](config/hardware-catalog.json)
  remains uncorrected, so a product YAML cannot rely on any of
  those claims; (6) **product-onboarding approval missing** —
  per the [Core rule](docs/product-readiness-matrix.md#core-rule)
  of `docs/product-readiness-matrix.md`, adding a product YAML
  requires every consumed package to be `ready-for-package-change`
  (the `power_240v.yaml` row stays `schematic-evidence-pending` +
  `needs-package-reconciliation` + `timing/compliance-pending`),
  the combination to clear the WebFlash compatibility grammar in
  `config/webflash-compatibility.json` (`PWR` is reserved in
  `canonical_power: ["USB", "POE", "PWR"]` but no
  `webflash_build_matrix: true` entry consumes it), and the
  [`docs/product-onboarding.md`](docs/product-onboarding.md) safe
  sequence to be followed end-to-end (not designed for this
  slice). Path B was rejected because the readiness matrices
  ([`docs/product-readiness-matrix.md` §PWR-240V / S360-400](docs/product-readiness-matrix.md#pwr-240v--s360-400),
  [`docs/webflash-exposure-readiness-matrix.md` §Power / S360-400 WebFlash posture](docs/webflash-exposure-readiness-matrix.md#power--s360-400-webflash-posture),
  [`docs/release-artifact-readiness-matrix.md` §Power / S360-400 release posture](docs/release-artifact-readiness-matrix.md#power--s360-400-release-posture))
  already correctly classify the slice as `not-webflash-ready` /
  `not-release-ready` / `no product YAML` and any further
  documentation cleanup belongs to a separate CLEANUP slice;
  Path C was rejected because every gate is open and adding a
  product YAML without package readiness would break the Core
  rule. The investigation outcome confirms **no S360-400-explicit
  / `PWR`-bearing WebFlash-shippable product YAML exists**,
  [`config/product-catalog.json`](config/product-catalog.json)
  has **no S360-400-specific product** (the four
  `legacy-compatible` `*-pwr` Core variants
  [`products/sense360-core-c-pwr.yaml`](products/sense360-core-c-pwr.yaml),
  [`products/sense360-core-w-pwr.yaml`](products/sense360-core-w-pwr.yaml),
  [`products/sense360-core-v-c-pwr.yaml`](products/sense360-core-v-c-pwr.yaml),
  [`products/sense360-core-v-w-pwr.yaml`](products/sense360-core-v-w-pwr.yaml)
  stay `legacy-compatible` / `webflash_build_matrix: false` /
  no `config_string` / no `webflash_wrapper` / no
  `artifact_name`, and are **not** S360-400-specific
  product-readiness evidence — they consume the logical
  `power_240v.yaml` package without explicit S360-400 binding,
  and the package's stale `HLK-PM01 or similar` header /
  unverified input / output / isolation / protection / fusing
  claims remain BOM-bound); the
  [`config/webflash-builds.json`](config/webflash-builds.json)
  build matrix has **no `PWR` build** (only Release-One
  `Ceiling-POE-VentIQ-RoomIQ` stable and
  `Ceiling-POE-VentIQ-RoomIQ-LED` preview); and
  [`config/webflash-compatibility.json`](config/webflash-compatibility.json)
  reserves `PWR` in `canonical_power` but no
  `webflash_build_matrix: true` row consumes it. Investigation
  outcome recorded at
  `docs/product-readiness-matrix.md` §PWR-240V / S360-400 and
  Follow-up PR sequence,
  `docs/webflash-exposure-readiness-matrix.md` §Power / S360-400
  WebFlash posture,
  `docs/release-artifact-readiness-matrix.md` §Power / S360-400
  release posture, and `docs/cleanup-audit.md`
  §`PRODUCT-POWER-400-001 update
  (2026-05-19 — docs-only investigation pass)`. No package /
  product / WebFlash / build / release / import / test / config /
  workflow / firmware / manifest edits. No catalog
  `schematic_status` promotion. No `schematic_file` set. No
  COMPLIANCE-001 movement. No `lifecycle_statuses` /
  `canonical_modules` / `canonical_power` / `forbidden_tokens` /
  `release_one_required_configs` / `webflash_build_matrix` /
  `artifact_name` / kit / `REQUIRED_CONFIGS` change.
  `PRODUCT-POWER-400-001` stays blocked behind
  `PACKAGE-POWER-400-001` implementation, BOM, the `S360-400`
  `schematic_status: verified` JSON PR, the `COMPLIANCE-001`
  `S360-400` slice, package / catalog reconciliation, and
  product-onboarding approval; `WEBFLASH-POWER-400-001` /
  `RELEASE-POWER-400-001` / `WF-IMPORT-POWER-400-001` stay
  blocked behind it. Release-One stays
  `Ceiling-POE-VentIQ-RoomIQ` / version `1.0.0` / channel
  `stable`; LED preview stays
  `Ceiling-POE-VentIQ-RoomIQ-LED` / `status: preview` /
  `channel: preview`; FanTRIAC stays `status: blocked`,
  `blocker: HW-005`, `webflash_build_matrix: false`. The next
  `PRODUCT-POWER-400-001` PR must land **the canonical S360-400
  / `PWR`-bearing product YAML + the matching
  `config/product-catalog.json` entry + the
  legacy-compatible `*-pwr` Core variant relationship decision
  (retain / migrate / coexist) as a single atomic slice**, not
  as a documentation cleanup alone, and only after
  `PACKAGE-POWER-400-001` implementation, the `S360-400`
  `schematic_status: verified` JSON PR, the `COMPLIANCE-001`
  `S360-400` slice, and product-onboarding approval all land.
- **WEBFLASH-POWER-400-001** investigation merged as **PR #522** on
  2026-05-19 (docs-only Path A deferral). The pass evaluated
  whether `WEBFLASH-POWER-400-001` could safely proceed now
  (Path C implementation — add the WebFlash wrapper under
  [`products/webflash/`](products/webflash/), flip
  `webflash_build_matrix: true` on a PWR-bearing
  [`config/product-catalog.json`](config/product-catalog.json)
  row, and add the matching build-matrix row to
  [`config/webflash-builds.json`](config/webflash-builds.json)),
  as a documentation / catalog-classification-note-only cleanup
  PR (Path B), or as a docs-only deferral (Path A), and is
  **confirmed deferred** — five preconditions remain open:
  (1) **`PRODUCT-POWER-400-001` implementation slice has not
  landed** — only the docs-only investigation pass merged as
  PR #521; the canonical S360-400 / `PWR`-bearing product YAML,
  the matching `config/product-catalog.json` entry, and the
  legacy-compatible `*-pwr` Core variant relationship decision
  that PR #521 enumerated as the required atomic slice all
  remain owed; (2) **`PACKAGE-POWER-400-001` implementation
  slice has not landed** — only the docs-only investigation pass
  merged as PR #520; (3) **`S360-400` `schematic_status:
  verified` JSON PR not landed** — separate JSON-only PR after
  BOM + silkscreen evidence land; (4) **`COMPLIANCE-001`
  `S360-400` slice still open** — last re-checked PR #506;
  (5) **UX-class decision pending** — standard preview-candidate
  vs advanced / manual-warning posture has not been chosen
  (decision belongs upstream to `PRODUCT-POWER-400-001`
  compliance verdict). Path B was rejected because
  [`docs/webflash-exposure-readiness-matrix.md` §Power / S360-400 WebFlash posture](docs/webflash-exposure-readiness-matrix.md#power--s360-400-webflash-posture),
  [`docs/release-artifact-readiness-matrix.md` §Power / S360-400 release posture](docs/release-artifact-readiness-matrix.md#power--s360-400-release-posture),
  and
  [`docs/product-readiness-matrix.md` §PWR-240V / S360-400](docs/product-readiness-matrix.md#pwr-240v--s360-400)
  already correctly classify the slice as `not-webflash-ready`
  / `no wrapper` / `no build-matrix entry` and the Follow-up PR
  sequence row already names the product-and-compliance gate.
  Path C was unsafe because every upstream gate is open: adding
  a WebFlash wrapper for a mains-voltage path while
  `COMPLIANCE-001` `S360-400` is open would violate the
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](docs/compliance/mains-voltage-uk-eu-assessment.md)
  gate; and adding any wrapper without a canonical S360-400 /
  `PWR`-bearing product YAML to wrap would break the
  [`docs/webflash-exposure-readiness-matrix.md` Core rule](docs/webflash-exposure-readiness-matrix.md#core-rule).
  The investigation outcome confirms **no S360-400 WebFlash
  wrapper exists** under
  [`products/webflash/`](products/webflash/) (three PoE wrappers
  only — `ceiling-poe-ventiq-roomiq.yaml`,
  `ceiling-poe-ventiq-roomiq-led.yaml`,
  `ceiling-poe-ventiq-fantriac-roomiq.yaml`);
  [`config/webflash-builds.json`](config/webflash-builds.json)
  has **no `PWR` build** (only Release-One
  `Ceiling-POE-VentIQ-RoomIQ` stable and
  `Ceiling-POE-VentIQ-RoomIQ-LED` preview);
  [`config/webflash-compatibility.json`](config/webflash-compatibility.json)
  reserves `PWR` in `canonical_power: ["USB", "POE", "PWR"]`
  with **no `webflash_build_matrix: true` consumer**;
  [`config/product-catalog.json`](config/product-catalog.json)
  has **no S360-400-specific product** (the four
  `legacy-compatible` `*-pwr` Core variants stay
  `legacy-compatible` / `webflash_build_matrix: false` / no
  `config_string` / no `webflash_wrapper` / no
  `artifact_name`);
  [`config/hardware-catalog.json`](config/hardware-catalog.json)
  `S360-400` row stays `schematic_status: cataloged_unverified`
  with no `schematic_file` (asserted by
  `tests/test_hardware_catalog.py:53`
  `EXPECTED_STILL_UNVERIFIED_SKUS = frozenset({"S360-320",
  "S360-400"})`);
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](docs/compliance/mains-voltage-uk-eu-assessment.md)
  COMPLIANCE-001 `S360-400` slice is unchanged since PR #506
  (open / not cleared). Investigation outcome recorded at
  `docs/webflash-exposure-readiness-matrix.md` §Power / S360-400
  WebFlash posture, `docs/release-artifact-readiness-matrix.md`
  §Power / S360-400 release posture, and `docs/cleanup-audit.md`
  §`WEBFLASH-POWER-400-001 update (2026-05-19 — docs-only
  investigation pass)`. No package / product / WebFlash /
  build / release / import / test / config / workflow / firmware
  / manifest edits. No catalog `schematic_status` promotion. No
  `schematic_file` set. No `webflash_build_matrix` flip. No new
  `artifact_name` added. No COMPLIANCE-001 movement. No
  `lifecycle_statuses` / `canonical_modules` / `canonical_power`
  / `forbidden_tokens` / `release_one_required_configs` / kit /
  `REQUIRED_CONFIGS` change. `WEBFLASH-POWER-400-001` stays
  blocked behind `PRODUCT-POWER-400-001` implementation, the
  `COMPLIANCE-001` `S360-400` slice, and the UX-class decision;
  `RELEASE-POWER-400-001` / `WF-IMPORT-POWER-400-001` stay
  blocked behind it. Release-One stays
  `Ceiling-POE-VentIQ-RoomIQ` / version `1.0.0` / channel
  `stable`; LED preview stays
  `Ceiling-POE-VentIQ-RoomIQ-LED` / `status: preview` /
  `channel: preview`; FanTRIAC stays `status: blocked`,
  `blocker: HW-005`, `webflash_build_matrix: false`. The next
  `WEBFLASH-POWER-400-001` PR must land **the WebFlash wrapper
  + the catalog `webflash_build_matrix: true` flip + the
  build-matrix row + the UX-class decision as a single atomic
  slice**, not as a documentation cleanup alone, and only
  after `PRODUCT-POWER-400-001` implementation and the
  `COMPLIANCE-001` `S360-400` slice closure both land.
- **RELEASE-POWER-400-001** investigation merged as **PR #523** on
  2026-05-19 (docs-only Path A deferral). The pass evaluated
  whether `RELEASE-POWER-400-001` could safely proceed now
  (Path C implementation — build / sign / attach a PWR-240V
  release `.bin`, generate and validate release notes, emit
  SHA256 / MD5 checksums, attach a build-info manifest, record
  a proof row in
  [`docs/webflash-release-proof.md`](docs/webflash-release-proof.md),
  and hand off to `WF-IMPORT-POWER-400-001` cross-repo), as a
  release-notes / proof-template-only PR (Path B), or as a
  docs-only deferral (Path A), and is **confirmed deferred** —
  seven preconditions remain open: (1) **`WEBFLASH-POWER-400-001`
  implementation slice has not landed** — only the docs-only
  investigation pass merged as PR #522; the WebFlash wrapper,
  the catalog `webflash_build_matrix: true` flip, the
  build-matrix row, and the UX-class decision all remain owed;
  (2) **`PRODUCT-POWER-400-001` implementation slice has not
  landed** — only the docs-only investigation pass merged as
  PR #521; (3) **`PACKAGE-POWER-400-001` implementation slice
  has not landed** — only the docs-only investigation pass
  merged as PR #520; (4) **`S360-400` `schematic_status:
  verified` JSON PR not landed** — separate JSON-only PR after
  BOM + silkscreen evidence land; (5) **`COMPLIANCE-001`
  `S360-400` slice still open** — last re-checked PR #506; per
  [`docs/release-artifact-readiness-matrix.md` Follow-up PR sequence](docs/release-artifact-readiness-matrix.md#follow-up-pr-sequence)
  row at line 1502, `RELEASE-POWER-400-001` is explicitly gated
  on "`WEBFLASH-POWER-400-001` landed + `COMPLIANCE-001`
  `S360-400` slice closed"; (6) **BOM / silkscreen / creepage
  / clearance / bench / thermal / EMI evidence missing** —
  same five-component BOM gap PR #520 recorded plus all
  silkscreen / PCB / creepage / clearance / bench / load /
  thermal / inrush / insulation / Hi-pot / earth-continuity /
  leakage / EMI / EMC measurements against a populated
  `S360-400-R4` board still missing; (7) **UX-class decision
  pending** — decision belongs upstream to
  `PRODUCT-POWER-400-001` / `WEBFLASH-POWER-400-001` compliance
  verdict per the Follow-up PR sequence row at line 1502; that
  verdict has not been rendered. Path B was rejected because
  (a) `scripts/generate_webflash_release_notes.py` consumes
  `config/webflash-builds.json` as the matrix source and needs
  a `(config_string, version, channel)` input tuple that does
  not exist for PWR-240V; (b) a proof-template-only edit to
  `docs/webflash-release-proof.md` would introduce a
  forward-reference to an artifact that has never been built
  and would degrade the proof file's evidentiary integrity;
  (c) per the Follow-up PR sequence row at line 1502
  `RELEASE-POWER-400-001` is explicitly **"Build, sign, attach
  the `.bin`; release notes; checksums; proof row"** — that is
  the atomic slice. Path C was unsafe because every upstream
  gate is open and
  [`.github/workflows/firmware-build-release.yml`](.github/workflows/firmware-build-release.yml)
  is in the do-not-change guardrail and processes only entries
  in `config/webflash-builds.json`, which has no PWR-240V row.
  The investigation outcome confirms: **no S360-400 release
  artifact exists** of any kind — no `firmware/` directory,
  no `firmware/configurations/`, no `firmware/sources.json`,
  no top-level `manifest.json`, no `firmware-*.json` (none of
  those paths exist at HEAD); no GitHub Release for any
  PWR-240V tag exists; no
  `Sense360-Ceiling-PWR-{AIR}-{ROOM}-v{VERSION}-{CHANNEL}.bin`
  artifact has been built, signed, attached, or imported; no
  SHA256 / MD5 checksum files for any PWR-240V artifact; no
  build-info `manifest.json` asset for any PWR-240V release;
  no proof row in `docs/webflash-release-proof.md` for any
  PWR-240V artifact; the two existing `artifact_name` entries
  (`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` and
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`)
  stay byte-identical;
  [`config/webflash-compatibility.json`](config/webflash-compatibility.json)
  `release_one_required_configs` stays
  `["Ceiling-POE-VentIQ-RoomIQ"]`;
  [`.github/workflows/firmware-build-release.yml`](.github/workflows/firmware-build-release.yml)
  stays byte-identical. All eight release-time sub-gates at
  [`docs/release-artifact-readiness-matrix.md` §Release note / artifact / checksum gates](docs/release-artifact-readiness-matrix.md#release-note--artifact--checksum-gates)
  remain unmet for any PWR-240V `.bin`: product-catalog entry
  (none), build-matrix entry (none), artifact-name conformance
  (no `artifact_name`), release-tag conformance (no tag),
  release-notes generated (no `(config_string, version,
  channel)` input), release-notes valid (no body to
  validate), artifact built (no input matrix row), checksums
  attached / manifest attached / proof recorded (no asset to
  checksum / manifest / prove). Investigation outcome
  recorded at `docs/release-artifact-readiness-matrix.md`
  §Power / S360-400 release posture and `docs/cleanup-audit.md`
  §`RELEASE-POWER-400-001 update (2026-05-19 — docs-only
  investigation pass)`. No package / product / WebFlash /
  build / release / import / test / config / workflow /
  firmware / manifest edits. No catalog `schematic_status`
  promotion. No `schematic_file` set. No `webflash_build_matrix`
  flip. No new `artifact_name` added. No GitHub Release / tag
  / checksum / manifest / proof row created. No
  COMPLIANCE-001 movement. No `lifecycle_statuses` /
  `canonical_modules` / `canonical_power` / `forbidden_tokens`
  / `release_one_required_configs` / kit / `REQUIRED_CONFIGS`
  change. `RELEASE-POWER-400-001` stays blocked behind
  `WEBFLASH-POWER-400-001` implementation, `PRODUCT-POWER-400-001`
  implementation, `PACKAGE-POWER-400-001` implementation, the
  `COMPLIANCE-001` `S360-400` slice, BOM / silkscreen /
  creepage / clearance / bench / thermal / EMI evidence, and
  the UX-class decision; `WF-IMPORT-POWER-400-001` (cross-repo)
  stays blocked behind it. Release-One stays
  `Ceiling-POE-VentIQ-RoomIQ` / version `1.0.0` / channel
  `stable` / artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` /
  tag `v1.0.0`; LED preview stays
  `Ceiling-POE-VentIQ-RoomIQ-LED` / `status: preview` /
  `channel: preview` / artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`;
  FanTRIAC stays `status: blocked`, `blocker: HW-005`,
  `webflash_build_matrix: false`. The next
  `RELEASE-POWER-400-001` PR must land **the build + sign +
  attach `.bin` + generate release notes + validate release
  notes + emit SHA256 + emit MD5 + attach build-info manifest
  + record proof row + hand off to WF-IMPORT-POWER-400-001
  (cross-repo) as a single atomic slice**, not as a
  release-notes / proof-template-only PR alone, and only
  after `WEBFLASH-POWER-400-001` implementation and the
  `COMPLIANCE-001` `S360-400` slice closure both land.
- **CLEANUP-POWER-RELEASE-001** merged as **PR #524** on 2026-05-19
  and **CLEANUP-POWER-RELEASE-002** merged as **PR #525** on
  2026-05-19 (both docs-only tracker cleanups). PR #524 removed
  stale `WEBFLASH-POWER-400-001` / `RELEASE-POWER-400-001`
  tracker prose left after PR #523 and converted stale "this PR"
  references so `WEBFLASH-POWER-400-001` consistently points to
  PR #522 and `RELEASE-POWER-400-001` consistently points to
  PR #523. PR #525 removed the remaining stale duplicate
  active-queue stub for `RELEASE-POWER-400-001` (and the
  duplicate `PRODUCT-POWER-400-001` #521 merged-table row) and
  renumbered the active queue so `PACKAGE-POE-410-001` is the
  next item. No functional, package, product, WebFlash, config,
  firmware, test, workflow, or compliance file changed.
- **PACKAGE-POE-410-001** investigation merged as **PR #526** on
  2026-05-20 (docs-only Path A deferral). The pass evaluated
  whether `PACKAGE-POE-410-001` could safely proceed now (Path C
  implementation — header / catalog reconciliation against the
  module BOM and the schematic-shown discrete topology), as a
  comment-only package cleanup PR (Path B — soften / remove the
  stale `Ag9712M, Silvertel Ag9700, or similar` whole-module
  PoE-PSU header hint without claiming a replacement), or as a
  docs-only deferral (Path A), and is **confirmed deferred** —
  five preconditions remain open: (1) **BOM cross-check missing**
  (no BOM line item with manufacturer + part number + revision
  for `LAN_CON1 RJP-003TC1(LPJ4112CNL)`, `U1 TPS2378DDAR`,
  `U2 TX4138`, `DCDC1 F0505S-2WR2(SIP-7)` (settling the
  primary-vs-alternate question against the annotated
  `AM1D-0505S-NZ`), `D1 SMAJ58A`, `D2 ss510`, `D3 Green`,
  `L1 33uH`, `R1`–`R9`, `C1`–`C8`, or `J3` with full ratings —
  the three-way disagreement between catalog
  [`config/hardware-catalog.json`](config/hardware-catalog.json)
  line 119 (`description: "PoE to 5V."`), package-header
  [`packages/hardware/power_poe.yaml`](packages/hardware/power_poe.yaml)
  line 6 (`Ag9712M, Silvertel Ag9700, or similar` — whole-module
  hint), and schematic
  [`docs/hardware/schematics/S360-410-R4.pdf`](docs/hardware/schematics/S360-410-R4.pdf)
  discrete topology (`TPS2378DDAR(HSOIC-8)` PoE PD controller +
  `TX4138(ESOIC-8)` buck + `F0505S-2WR2(SIP-7)` isolated DC/DC
  with `AM1D-0505S-NZ` annotated alternate +
  `RJP-003TC1(LPJ4112CNL)` magnetics) therefore stays
  unresolved and remains BOM-bound per the explicit decision
  recorded by HW-PINMAP-410-FOLLOWUP / PR #517 in
  [`docs/hardware/s360-410-r4-poe.md` §Existing package abstraction](docs/hardware/s360-410-r4-poe.md#existing-package-abstraction)
  and §Package YAML status; (2) **`S360-410`
  `schematic_status: verified` JSON PR not landed** —
  [`config/hardware-catalog.json`](config/hardware-catalog.json)
  line 120 still records `S360-410` →
  `schematic_status: cataloged_unverified` and no
  `schematic_file` is set; the separate JSON-only promotion PR
  is gated on BOM cross-check + HW-002 OQ#6 /
  `S360-100-BENCH-001` J2-harness closure + a standalone
  reference-doc rewrite; (3) **HW-002 Open Question #6 /
  `S360-100-BENCH-001` J2-harness identity stays open** — last
  re-checked PR #504 / 2026-05-18; both
  [`docs/hardware/s360-100-r4-core.md` Open Question #6](docs/hardware/s360-100-r4-core.md#open-questions--verification-needed)
  and the
  [S360-100-BENCH-001 J2 PoE harness identity row](docs/hardware/s360-100-r4-core.md#s360-100-bench-001-status)
  stay `pending — bench/manufacturing evidence required`;
  (4) **package-header reconciliation not landed** — the
  package-header `Ag9712M / Silvertel Ag9700 / or similar` line
  (6), the `IEEE 802.3af (PoE) or 802.3at (PoE+)` standard line
  (7), the `Class 0 (0.44-12.95W) or Class 1 (0.44-3.84W)`
  class line (8), the `36-57V DC` input line (9), the
  `5V DC, 2A (10W) or 3.3V DC` output line (10), and the
  `Overcurrent, overvoltage, short-circuit` protection line
  (11) are not yet reconciled against the schematic-shown
  discrete topology; (5) **Release-One PoE caveat closure is a
  separate later PR** — the documented "schematic verification
  pending" caveat in
  [`docs/release-one-hardware-audit.md` Findings → PoE PSU](docs/release-one-hardware-audit.md#findings)
  and
  [Required follow-ups #6](docs/release-one-hardware-audit.md#required-follow-ups)
  is **preserved verbatim** by PR #526 and is owed to a separate
  caveat-closure PR after all of the above land. Path B was
  rejected because the only safe comment-only change would be to
  remove the `Ag9712M, Silvertel Ag9700, or similar` line and to
  soften / remove the standard / class / input / output /
  protection lines without claiming `TPS2378DDAR` / `TX4138` /
  `F0505S-2WR2` / `RJP-003TC1(LPJ4112CNL)` — and PR #517's
  recorded decision was specifically that even that removal
  should wait for BOM so the eventual `PACKAGE-POE-410-001`
  implementation PR can land header reconciliation + BOM
  citation as one coordinated change (the same rule PR #520
  applied to the parallel `PACKAGE-POWER-400-001` slice). Path C
  was unsafe because the five preconditions above are open and
  any header / catalog edit without BOM evidence would
  substitute one unsourced claim for another. The investigation
  outcome confirms
  [`packages/hardware/power_poe.yaml`](packages/hardware/power_poe.yaml)
  stays byte-identical to PR #517 state: the stale
  `Ag9712M, Silvertel Ag9700, or similar` header (line 6), the
  `IEEE 802.3af (PoE) or 802.3at (PoE+)` standard line (7), the
  `Class 0 (0.44-12.95W) or Class 1 (0.44-3.84W)` class line
  (8), the `36-57V DC (from PoE switch/injector)` input line
  (9), the `5V DC, 2A (10W) or 3.3V DC` output line (10), the
  `Overcurrent, overvoltage, short-circuit` protection line
  (11), the `substitutions: power_source: "poe"` /
  `poe_class: "0"` / `poe_standard: "802.3af"` block (lines
  28–31), the `globals: power_source_type` block (lines 33–38),
  the template diagnostic sensors (`Supply Voltage` constant-
  `5.0` lambda, `Power Source`, `Power Configuration`,
  `PoE Power Connected` constant-`true` lambda), the logger
  config, and the `on_boot` logger statements are **all**
  preserved byte-for-byte. The package has **no GPIO / I²C /
  UART / SPI / DAC / runtime binding** — it is a logical PoE
  power package emitting diagnostic sensors only. Investigation
  outcome recorded at `docs/hardware/s360-410-r4-poe.md`
  §`### 2026-05-20 — PACKAGE-POE-410-001 investigation pass`,
  `docs/hardware/package-readiness-matrix.md` §`power_poe.yaml`
  / S360-410 addendum,
  `docs/hardware/firmware-package-mapping-audit.md`
  §`power_poe.yaml` PoE-module part-identity disagreement
  (S360-410) addendum, and `docs/cleanup-audit.md`
  §`PACKAGE-POE-410-001 update (2026-05-20 — docs-only
  investigation pass)`. No package, product, WebFlash, build,
  release, compliance, JSON catalog, test, script, workflow,
  component, include, firmware, or manifest edits; no
  `schematic_status` / `schematic_file` promotion; no
  COMPLIANCE-001 movement (PoE is SELV; `S360-410` is **not** in
  scope); no Release-One caveat closure (preserved verbatim);
  no `lifecycle_statuses` / `canonical_modules` /
  `canonical_power` / `forbidden_tokens` /
  `release_one_required_configs` / `webflash_build_matrix` /
  `artifact_name` / kit / `REQUIRED_CONFIGS` change.
  `PACKAGE-POE-410-001` stays blocked on the five preconditions;
  `PRODUCT-POE-410-001` / `WEBFLASH-POE-410-001` /
  `RELEASE-POE-410-001` / `WF-IMPORT-POE-410-001` stay blocked
  behind it. Release-One stays `Ceiling-POE-VentIQ-RoomIQ` /
  version `1.0.0` / channel `stable`; LED preview stays
  `Ceiling-POE-VentIQ-RoomIQ-LED` / `status: preview` /
  `channel: preview`; FanTRIAC stays `status: blocked` /
  `blocker: HW-005` / `webflash_build_matrix: false`. The next
  `PACKAGE-POE-410-001` PR must land **the BOM cross-check +
  the `S360-410` `schematic_status: verified` JSON promotion
  (separate JSON-only PR after BOM + HW-002 OQ#6 /
  `S360-100-BENCH-001` closure) + the package header
  reconciliation against the schematic-shown discrete topology
  as a single atomic slice**, not as a comment-only cleanup
  alone, and the Release-One PoE caveat closure stays a separate
  later PR.
- **CLEANUP-POE-410-001** merged as **PR #527** on 2026-05-20
  (docs-only tracker cleanup). PR #527 converted the
  unresolved PR-number / `this PR` placeholders that PR #526 left in
  [`UPCOMING_PR.md`](UPCOMING_PR.md) so `PACKAGE-POE-410-001`
  consistently points to PR #526 — the Current queue summary
  bullet, the `Recently uploaded evidence` entry, the active-queue
  entry #7 `Status` / `Notes` lines, and the rejected-Path-B
  reference all now name PR #526 explicitly — and added the
  matching `PACKAGE-POE-410-001 / #526` row to the Completed /
  merged PRs table. No functional, package, product, WebFlash,
  build, release, compliance, JSON catalog, test, script,
  workflow, component, include, firmware, manifest, or
  audit-document file changed; only
  [`UPCOMING_PR.md`](UPCOMING_PR.md) was touched. No queue-ordering
  effect on `PRODUCT-POE-410-001`.
- **PRODUCT-POE-410-001** investigation merged as **PR #528** on
  2026-05-20 (docs-only Path A deferral). The pass evaluated
  whether `PRODUCT-POE-410-001` could safely proceed now (Path C
  implementation — add the first S360-410-explicit /
  `POE`-bearing product YAML under
  [`products/`](products/) that subjects the verified S360-410 PoE
  PSU explicitly, plus the matching entry in
  [`config/product-catalog.json`](config/product-catalog.json)),
  as a documentation / catalog-note-only cleanup PR (Path B —
  for example, tightening the
  [`docs/product-readiness-matrix.md` §PoE-410 / S360-410](docs/product-readiness-matrix.md#poe-410--s360-410)
  Follow-up owner chain or the
  [`docs/webflash-exposure-readiness-matrix.md` §PoE / S360-410 WebFlash posture](docs/webflash-exposure-readiness-matrix.md#poe--s360-410-webflash-posture)
  text), or as a docs-only deferral (Path A), and is
  **confirmed deferred** — eight preconditions remain open:
  (1) **`PACKAGE-POE-410-001` implementation slice has not
  landed** — only the docs-only investigation pass merged as
  PR #526; the package-header reconciliation against the
  schematic-shown discrete topology, the catalog `description`
  reconciliation (if applicable), the BOM citation, and the
  `S360-410` `schematic_status: verified` JSON promotion that
  PR #526 enumerated as the required atomic slice all remain
  owed to a future evidence-bearing `PACKAGE-POE-410-001` PR;
  (2) **BOM cross-check missing** — same gap PR #526 recorded
  for the package slice (no BOM line item with manufacturer +
  part number + revision for `LAN_CON1 RJP-003TC1(LPJ4112CNL)`
  / `U1 TPS2378DDAR(HSOIC-8)` / `U2 TX4138(ESOIC-8)` /
  `DCDC1 F0505S-2WR2(SIP-7)` (settling primary vs the annotated
  `AM1D-0505S-NZ` alternate) / `D1 SMAJ58A` / `D2 ss510` /
  `D3 Green` / `L1 33uH` / `R1`–`R9` / `C1`–`C8` / `J3`);
  (3) **`S360-410` `schematic_status: verified` JSON PR not
  landed** — [`config/hardware-catalog.json`](config/hardware-catalog.json)
  line 120 still records `schematic_status: cataloged_unverified`
  with no `schematic_file`; (4) **HW-002 Open Question #6 /
  `S360-100-BENCH-001` J2-harness identity closure missing**
  — both stay `pending — bench/manufacturing evidence required`
  per the 2026-05-18 re-check; (5) **package-header
  reconciliation owed to `PACKAGE-POE-410-001`** — the
  `Ag9712M, Silvertel Ag9700, or similar` whole-module hint
  (line 6 of [`packages/hardware/power_poe.yaml`](packages/hardware/power_poe.yaml))
  vs the schematic-shown discrete topology
  (`TPS2378DDAR + TX4138 + F0505S-2WR2 + RJP-003TC1(LPJ4112CNL)`)
  stays unresolved and BOM-bound; a product YAML cannot rely on
  any of those claims while they remain BOM-bound; (6) **Release-One
  PoE "schematic verification pending" caveat closure missing**
  — the caveat in
  [`docs/release-one-hardware-audit.md` Findings → PoE PSU](docs/release-one-hardware-audit.md#findings)
  and [Required follow-ups #6](docs/release-one-hardware-audit.md#required-follow-ups)
  is preserved verbatim by PR #526 and stays a separate later
  PR; (7) **product-onboarding approval missing** — per the
  [Core rule](docs/product-readiness-matrix.md#core-rule) of
  `docs/product-readiness-matrix.md`, adding a product YAML
  requires every consumed package to be `ready-for-package-change`
  (the [`power_poe.yaml`](packages/hardware/power_poe.yaml) row
  stays `reference-only` + `schematic-evidence-pending` +
  `do-not-change-release-one`), the combination to clear the
  WebFlash compatibility grammar in
  `config/webflash-compatibility.json` (`POE` is already
  reserved in `canonical_power` and is consumed by both
  committed builds under the preserved Release-One caveat — no
  new `webflash_build_matrix: true` row is required to make
  this product-onboarding gate pass), and the
  [`docs/product-onboarding.md`](docs/product-onboarding.md)
  safe sequence to be followed end-to-end (not designed for
  this slice); (8) **product / catalog readiness approval
  missing** — per the
  [Follow-up PR sequence row](docs/product-readiness-matrix.md#follow-up-pr-sequence)
  `PRODUCT-POE-410-001` "often will close by promoting
  Release-One's preserved schematic-pending caveat alone,
  without adding a new product entry"; the no-new-entry vs
  new-entry decision belongs to this slice and has not been
  made. Path B was rejected because the readiness matrices
  ([`docs/product-readiness-matrix.md` §PoE-410 / S360-410](docs/product-readiness-matrix.md#poe-410--s360-410),
  [`docs/webflash-exposure-readiness-matrix.md` §PoE / S360-410 WebFlash posture](docs/webflash-exposure-readiness-matrix.md#poe--s360-410-webflash-posture),
  [`docs/release-artifact-readiness-matrix.md` §PoE / S360-410 release posture](docs/release-artifact-readiness-matrix.md#poe--s360-410-release-posture))
  already correctly classify the slice as `no new product YAML`
  / `not-webflash-ready` / `not-release-ready` and the Follow-up
  PR sequence row already names the package + caveat-closure +
  product-onboarding gates; rewording those sections before
  `PACKAGE-POE-410-001` lands would muddy the eventual
  coordinated implementation PR's scope (same rule PR #521
  applied to the parallel `PRODUCT-POWER-400-001` slice).
  Path C was rejected because every gate is open: adding a
  S360-410-explicit product YAML while
  [`packages/hardware/power_poe.yaml`](packages/hardware/power_poe.yaml)
  carries `reference-only` + `schematic-evidence-pending` +
  `do-not-change-release-one` would break the
  [`docs/product-readiness-matrix.md` Core rule](docs/product-readiness-matrix.md#core-rule);
  and adding a sibling PoE-410 product entry while the
  Release-One PoE caveat is preserved would implicitly
  requalify Release-One — explicitly forbidden by PR #526 and
  by every prior PoE-410 follow-up document. The investigation
  outcome confirms **no S360-410-explicit /
  `POE`-410-subject WebFlash-shippable product YAML exists**
  under [`products/`](products/) or
  [`products/webflash/`](products/webflash/); the three
  shipping PoE entries in
  [`config/product-catalog.json`](config/product-catalog.json)
  (`Ceiling-POE-VentIQ-RoomIQ` `status: production` /
  `channel: stable`, `Ceiling-POE-VentIQ-RoomIQ-LED`
  `status: preview` / `channel: preview`, and
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` `status: blocked` /
  `blocker: HW-005` / `webflash_build_matrix: false`) each
  carry `hardware.poe: "S360-410"` as a catalog-level mapping
  field only — they consume the **logical** `power_poe.yaml`
  package under Release-One identity and the preserved
  schematic-pending caveat; they are **not**
  S360-410-subject product-readiness evidence; the six
  `legacy-compatible` `*-poe` Core variants stay
  `legacy-compatible` and `webflash_build_matrix: false`;
  [`config/webflash-builds.json`](config/webflash-builds.json)
  has only the Release-One `Ceiling-POE-VentIQ-RoomIQ` `stable`
  build and the `Ceiling-POE-VentIQ-RoomIQ-LED` `preview` build
  (no new PoE-410-explicit build);
  [`config/webflash-compatibility.json`](config/webflash-compatibility.json)
  keeps `POE` reserved in `canonical_power` consumed by both
  committed builds (POE reservation does **not** imply
  S360-410-subject product readiness);
  `release_one_required_configs` stays
  `["Ceiling-POE-VentIQ-RoomIQ"]`;
  [`config/hardware-catalog.json`](config/hardware-catalog.json)
  `S360-410` row stays byte-identical
  (`schematic_status: cataloged_unverified`, no
  `schematic_file`, `description: "PoE to 5V."`). Investigation
  outcome recorded at
  `docs/product-readiness-matrix.md` §PoE-410 / S360-410,
  `docs/webflash-exposure-readiness-matrix.md` §PoE / S360-410
  WebFlash posture,
  `docs/release-artifact-readiness-matrix.md` §PoE / S360-410
  release posture,
  `docs/hardware/s360-410-r4-poe.md`
  §HW-PINMAP-410-FOLLOWUP audit log
  `2026-05-20 — PRODUCT-POE-410-001 investigation pass`,
  and `docs/cleanup-audit.md` §`PRODUCT-POE-410-001 update
  (2026-05-20 — docs-only investigation pass)`. No package,
  product, WebFlash, build, release, compliance, JSON catalog,
  test, script, workflow, component, include, firmware,
  manifest, or audit-document file changed beyond the
  read-only cross-link audit-log addendums; no
  `schematic_status` / `schematic_file` promotion; no
  COMPLIANCE-001 movement (PoE is SELV; `S360-410` is **not**
  in scope); no PoE-410-explicit entry added; no
  `webflash_build_matrix: true` flip; no new `artifact_name`;
  no `lifecycle_statuses` / `canonical_modules` /
  `canonical_power` / `forbidden_tokens` /
  `release_one_required_configs` / kit / `REQUIRED_CONFIGS`
  change; no Release-One caveat closure (preserved verbatim).
  `PRODUCT-POE-410-001` stays blocked on the eight
  preconditions; `WEBFLASH-POE-410-001` /
  `RELEASE-POE-410-001` / `WF-IMPORT-POE-410-001` (cross-repo)
  stay blocked behind it. Release-One stays
  `Ceiling-POE-VentIQ-RoomIQ` / version `1.0.0` / channel
  `stable` / artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` /
  tag `v1.0.0`; LED preview stays
  `Ceiling-POE-VentIQ-RoomIQ-LED` / `status: preview` /
  `channel: preview` / artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`;
  FanTRIAC stays `status: blocked` / `blocker: HW-005` /
  `webflash_build_matrix: false`. The next
  `PRODUCT-POE-410-001` PR must land **the no-new-entry vs
  new-entry decision + (if a new entry is warranted) the
  canonical S360-410 / `POE`-410-subject product YAML + the
  matching `config/product-catalog.json` entry as a single
  atomic slice**, not as a documentation cleanup alone, and
  only after `PACKAGE-POE-410-001` implementation, the
  Release-One PoE caveat-closure PR, and product-onboarding
  approval all land.
- **CLEANUP-POE-410-002** merged as **PR #529** on 2026-05-20
  (docs-only tracker cleanup). PR #529 converted the unresolved
  `PR #XXX` / `this PR` placeholders that PR #528 left in
  [`UPCOMING_PR.md`](UPCOMING_PR.md) so `PRODUCT-POE-410-001`
  consistently points to **PR #528** — the Current queue summary
  bullet, the `CLEANUP-POE-410-001` / `PRODUCT-POE-410-001` rows
  in the Completed / merged PRs table, and the Recently uploaded
  evidence entry now all name PR #528 explicitly — and removed
  the `PRODUCT-POE-410-001` active-queue entry (the investigation
  pass has merged, so the row no longer belongs in the active
  queue; `WEBFLASH-POE-410-001` is now active queue item #7 and
  subsequent entries were renumbered). No functional, package,
  product, WebFlash, build, release, compliance, JSON catalog,
  test, script, workflow, component, include, firmware, manifest,
  or audit-document file changed; only
  [`UPCOMING_PR.md`](UPCOMING_PR.md) was touched. No queue-ordering
  effect on `WEBFLASH-POE-410-001`.
- **WEBFLASH-POE-410-001** investigation merged as **PR #530** on
  2026-05-20 (docs-only Path A deferral). The pass evaluated
  whether `WEBFLASH-POE-410-001` could safely proceed now (Path
  C implementation — add the WebFlash wrapper under
  [`products/webflash/`](products/webflash/), flip
  `webflash_build_matrix: true` on the matching
  [`config/product-catalog.json`](config/product-catalog.json)
  row, and add the build-matrix row to
  [`config/webflash-builds.json`](config/webflash-builds.json)),
  as a documentation / catalog-classification-note-only cleanup
  PR (Path B), or as a docs-only deferral (Path A), and is
  **confirmed deferred** — eight blocker preconditions remain
  open, plus a ninth observation that the slice may not be
  required at all if `PRODUCT-POE-410-001` ultimately closes via
  the default no-new-entry / caveat-closure-only path. The eight
  blockers are: (1) **`PRODUCT-POE-410-001` implementation slice
  has not landed** — only the docs-only investigation pass
  merged as PR #528; the no-new-entry vs new-entry decision, and
  (if a new entry is warranted) the canonical S360-410 /
  `POE`-410-subject product YAML plus the matching
  `config/product-catalog.json` entry, all remain owed; (2)
  **`PACKAGE-POE-410-001` implementation slice has not landed**
  — only the docs-only investigation pass merged as PR #526; a
  wrapper cannot wrap a package that stays `reference-only` +
  `schematic-evidence-pending` + `do-not-change-release-one`;
  (3) **BOM cross-check missing** — same multi-component gap PR
  #526 / PR #528 recorded; (4) **`S360-410` `schematic_status:
  verified` JSON PR not landed** — [`config/hardware-catalog.json`](config/hardware-catalog.json)
  line 120 stays `schematic_status: cataloged_unverified` with
  no `schematic_file`; (5) **HW-002 Open Question #6 /
  `S360-100-BENCH-001` J2-harness identity closure missing** —
  both stay `pending — bench/manufacturing evidence required`
  per the 2026-05-18 re-check; (6) **Release-One PoE "schematic
  verification pending" caveat closure missing** — the caveat
  in [`docs/release-one-hardware-audit.md` Findings → PoE PSU](docs/release-one-hardware-audit.md#findings)
  and [Required follow-ups #6](docs/release-one-hardware-audit.md#required-follow-ups)
  is **preserved verbatim** by this re-check and stays a
  separate later PR; (7) **product-onboarding approval missing**
  — per the [Core rule](docs/webflash-exposure-readiness-matrix.md#core-rule)
  of `docs/webflash-exposure-readiness-matrix.md`, a WebFlash
  wrapper requires product readiness + package readiness + the
  upstream product YAML to exist; none of those is satisfied
  today (`POE` is already reserved in `canonical_power` and is
  consumed by both committed builds under the preserved
  Release-One caveat — no new `webflash_build_matrix: true` row
  is required to make the WebFlash compatibility grammar pass,
  but a wrapper still cannot land without the upstream product
  YAML); (8) **release / build readiness gates open** — a
  wrapper without an existing product YAML to wrap would break
  the Core rule. The ninth observation is recorded but does not
  resolve the slice today: per
  [`docs/product-readiness-matrix.md` §PoE-410 / S360-410](docs/product-readiness-matrix.md#poe-410--s360-410)
  and the
  [§Follow-up PR sequence row](docs/release-artifact-readiness-matrix.md#follow-up-pr-sequence)
  for `WEBFLASH-POE-410-001`, "often this slice is not required
  because `PRODUCT-POE-410-001` closes by extending the
  Release-One caveat without adding a new product"; the queue
  stays blocked / deferred until `PRODUCT-POE-410-001`
  implementation or no-op closure is explicitly decided later.
  Path B was rejected because the readiness matrices already
  correctly classify the slice as `not-webflash-ready` / `no
  wrapper` / `no build-matrix entry` for any new PoE-410 product
  entry and the Follow-up PR sequence rows already name the
  product + caveat-closure + product-onboarding gates (same rule
  PR #522 applied to the parallel `WEBFLASH-POWER-400-001`
  slice). Path C was unsafe because adding a WebFlash wrapper
  without a canonical S360-410 / `POE`-410-subject product YAML
  to wrap would break the
  [`docs/webflash-exposure-readiness-matrix.md` Core rule](docs/webflash-exposure-readiness-matrix.md#core-rule),
  and adding a build-matrix row or flipping
  `webflash_build_matrix: true` on a Release-One-identity entry
  while the Release-One PoE caveat is preserved would
  implicitly requalify Release-One — explicitly forbidden by
  PR #526 / PR #528 and by every prior PoE-410 follow-up
  document. The investigation outcome confirms **no S360-410
  WebFlash wrapper exists** under
  [`products/webflash/`](products/webflash/) (only three PoE
  wrappers — `ceiling-poe-ventiq-roomiq.yaml`,
  `ceiling-poe-ventiq-roomiq-led.yaml`,
  `ceiling-poe-ventiq-fantriac-roomiq.yaml` — all Release-One /
  LED preview / FanTRIAC blocked under Release-One identity,
  not S360-410-subject WebFlash exposure);
  [`config/webflash-builds.json`](config/webflash-builds.json)
  has **no S360-410-explicit build** (only Release-One stable
  and LED preview, both consuming S360-410 logically under
  preserved schematic-pending caveat);
  [`config/webflash-compatibility.json`](config/webflash-compatibility.json)
  reserves `POE` in `canonical_power` consumed by both
  committed builds (POE reservation does **not** imply
  S360-410-subject WebFlash exposure);
  [`config/product-catalog.json`](config/product-catalog.json)
  has **no S360-410-explicit product** (the three shipping PoE
  entries each carry `hardware.poe: "S360-410"` as a
  catalog-level mapping field only; the six `legacy-compatible`
  `*-poe` Core variants stay `legacy-compatible` /
  `webflash_build_matrix: false`);
  [`config/hardware-catalog.json`](config/hardware-catalog.json)
  `S360-410` row stays byte-identical;
  [`packages/hardware/power_poe.yaml`](packages/hardware/power_poe.yaml)
  stays byte-identical to PR #517 / PR #526 / PR #528 state.
  Investigation outcome recorded at
  [`docs/webflash-exposure-readiness-matrix.md` §PoE / S360-410 WebFlash posture](docs/webflash-exposure-readiness-matrix.md#poe--s360-410-webflash-posture),
  [`docs/release-artifact-readiness-matrix.md` §PoE / S360-410 release posture](docs/release-artifact-readiness-matrix.md#poe--s360-410-release-posture),
  [`docs/hardware/s360-410-r4-poe.md`](docs/hardware/s360-410-r4-poe.md)
  §HW-PINMAP-410-FOLLOWUP audit log
  `2026-05-20 — WEBFLASH-POE-410-001 investigation pass`, and
  [`docs/cleanup-audit.md`](docs/cleanup-audit.md)
  §`WEBFLASH-POE-410-001 update (2026-05-20 — docs-only investigation pass)`.
  No package, product, WebFlash, build, release, compliance,
  JSON catalog, test, script, workflow, component, include,
  firmware, manifest, or artifact edits; no `schematic_status`
  / `schematic_file` promotion; no COMPLIANCE-001 movement (PoE
  is SELV; `S360-410` is **not** in scope); no PoE-410-explicit
  entry added; no `webflash_build_matrix: true` flip; no new
  `artifact_name`; no `lifecycle_statuses` / `canonical_modules`
  / `canonical_power` / `forbidden_tokens` /
  `release_one_required_configs` / kit / `REQUIRED_CONFIGS`
  change; no Release-One caveat closure (preserved verbatim).
  `WEBFLASH-POE-410-001` stays blocked on the eight blocker
  preconditions (with the ninth observation carried forward);
  `RELEASE-POE-410-001` / `WF-IMPORT-POE-410-001` (cross-repo)
  stay blocked behind it. Release-One stays
  `Ceiling-POE-VentIQ-RoomIQ` / version `1.0.0` / channel
  `stable` / artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` / tag
  `v1.0.0`; LED preview stays `Ceiling-POE-VentIQ-RoomIQ-LED` /
  `status: preview` / `channel: preview` / artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`;
  FanTRIAC stays `status: blocked` / `blocker: HW-005` /
  `webflash_build_matrix: false`. The next
  `WEBFLASH-POE-410-001` PR (if and only if
  `PRODUCT-POE-410-001` adds a new PoE-410-explicit product
  entry) must land **the WebFlash wrapper + the catalog
  `webflash_build_matrix: true` flip + the build-matrix row +
  the UX-class decision as a single atomic slice**, not as a
  documentation cleanup alone, and only after
  `PRODUCT-POE-410-001` implementation and the Release-One PoE
  caveat-closure PR both land.
- **CLEANUP-POE-410-003** merged as **PR #531** on 2026-05-20
  (docs-only tracker cleanup). It converted the unresolved
  `PR #XXX` / `this PR` placeholders that PR #530 left in
  `UPCOMING_PR.md` so `WEBFLASH-POE-410-001` consistently
  points to PR #530 (Current queue summary bullet,
  `CLEANUP-POE-410-002` Follow-up impact column,
  `WEBFLASH-POE-410-001` row in the Completed / merged PRs
  table, and the Recently uploaded evidence entry all now
  name PR #530 explicitly), removed the
  `WEBFLASH-POE-410-001` active-queue entry (the
  investigation pass has merged), and renumbered subsequent
  entries so `RELEASE-POE-410-001` becomes active queue item
  #7. No functional, package, product, WebFlash, build,
  release, compliance, JSON catalog, test, script, workflow,
  component, include, firmware, manifest, audit-document, or
  artifact files; only `UPCOMING_PR.md` was touched. Per PR
  #531's own commit-message decision and the prior
  `CLEANUP-POE-410-001` / `CLEANUP-POE-410-002` /
  `CLEANUP-POWER-RELEASE-001` / `CLEANUP-POWER-RELEASE-002`
  pattern, PR #531 did **not** add a self-row to the
  Completed / merged PRs table; PR #532
  (`RELEASE-POE-410-001`) adds the `CLEANUP-POE-410-003` /
  #531 row.
- **RELEASE-POE-410-001** investigation merged as **PR #532**
  on 2026-05-20 (docs-only Path A deferral). The pass
  evaluated whether `RELEASE-POE-410-001` could safely
  proceed now (Path C implementation — build / sign / attach
  a PoE-410-explicit release `.bin`, generate and validate
  release notes, emit SHA256 / MD5 checksums, attach a
  build-info `manifest.json`, record a proof row in
  [`docs/webflash-release-proof.md`](docs/webflash-release-proof.md),
  and hand off to `WF-IMPORT-POE-410-001` cross-repo), as a
  release-notes / proof-template-only PR (Path B), or as a
  docs-only deferral (Path A), and is **confirmed deferred**
  — eight blocker preconditions remain open, plus a
  carried-forward observation that the slice may not be
  required at all if `PRODUCT-POE-410-001` /
  `WEBFLASH-POE-410-001` ultimately close via the default
  no-new-entry / caveat-closure-only path. Blockers are: (1)
  **`WEBFLASH-POE-410-001` implementation slice has not
  landed** — only the docs-only investigation pass merged as
  PR #530; the WebFlash wrapper, the catalog
  `webflash_build_matrix: true` flip, the build-matrix row,
  and the UX-class decision all remain owed. (2)
  **`PRODUCT-POE-410-001` implementation slice has not
  landed** — only the docs-only investigation pass merged as
  PR #528. (3) **`PACKAGE-POE-410-001` implementation slice
  has not landed** — only the docs-only investigation pass
  merged as PR #526. (4) **Repo-committed BOM evidence has
  not landed in this repository yet.** BOM files have been
  supplied out-of-band / uploaded, and for `S360-410` the
  uploaded BOM evidence appears to support the
  schematic-shown discrete PoE topology
  (`LAN_CON1 RJP-003TC1(LPJ4112CNL)` magnetics / RJ45,
  `U1 TPS2378DDAR(HSOIC-8)` PoE PD controller,
  `U2 TX4138(ESOIC-8)` buck, `DCDC1 F0505S-2WR2(SIP-7)`
  isolated DC/DC with the `AM1D-0505S-NZ`
  annotated-alternate question, `D1 SMAJ58A`, `D2 ss510`,
  `D3 Green`, `L1 33uH`, `R1`–`R9`, `C1`–`C8`, `J3` 2-pin
  Core-facing connector). This PR does **not** ingest or
  commit that BOM; BOM ingest is the responsibility of a
  separate `HW-BOM-ASSETS-001` follow-up. The release gate
  stays blocked until repo-committed BOM evidence lands and
  the downstream `PACKAGE-POE-410-001` / `PRODUCT-POE-410-001`
  / `WEBFLASH-POE-410-001` gates are updated against that
  committed evidence. (5) **`S360-410` `schematic_status:
  verified` JSON PR not landed** —
  [`config/hardware-catalog.json`](config/hardware-catalog.json)
  line 120 still records `S360-410` →
  `schematic_status: cataloged_unverified` and no
  `schematic_file` is set; the separate JSON-only promotion
  PR is gated on the BOM-ingest follow-up landing +
  HW-002 OQ#6 / `S360-100-BENCH-001` J2-harness closure +
  a standalone reference-doc rewrite. (6) **HW-002 Open
  Question #6 / `S360-100-BENCH-001` J2-harness identity
  stays open** — both stay
  `pending — bench/manufacturing evidence required` per the
  2026-05-18 re-check. (7) **Release-One PoE "schematic
  verification pending" caveat closure missing** — the
  caveat in
  [`docs/release-one-hardware-audit.md` Findings → PoE PSU](docs/release-one-hardware-audit.md#findings)
  and Required follow-ups #6 is **preserved verbatim** by
  this re-check; building / signing / attaching a
  PoE-410-explicit `.bin` (or recording a sibling
  release-proof row) while the caveat is preserved would
  implicitly requalify Release-One — explicitly forbidden by
  PR #526 / PR #528 / PR #530 and by every prior PoE-410
  follow-up document. (8) **Eight release-time sub-gates at
  [`docs/release-artifact-readiness-matrix.md` §Release note / artifact / checksum gates](docs/release-artifact-readiness-matrix.md#release-note--artifact--checksum-gates)
  remain unmet for any PoE-410-explicit `.bin`** —
  product-catalog entry (none), build-matrix entry (none),
  artifact-name conformance (no `artifact_name`),
  release-tag conformance (no tag), release-notes generated
  (no `(config_string, version, channel)` input),
  release-notes valid (no body to validate), artifact built
  (no input matrix row), checksums attached / manifest
  attached / proof recorded (no asset to checksum /
  manifest / prove). Path B was rejected because (a)
  `scripts/generate_webflash_release_notes.py` consumes
  `config/webflash-builds.json` as the matrix source and
  needs a `(config_string, version, channel)` input tuple
  that does not exist for PoE-410-explicit; (b) a
  proof-template-only edit to
  [`docs/webflash-release-proof.md`](docs/webflash-release-proof.md)
  would introduce a forward-reference to an artifact that
  has never been built and would degrade the proof file's
  evidentiary integrity; (c) per the Follow-up PR sequence,
  `RELEASE-POE-410-001` is explicitly **"Build, sign, attach
  the `.bin`; release notes; checksums; proof row"** — that
  is the atomic slice. Path C was unsafe because every
  upstream gate is open and the workflow file is
  workflow-frozen. The investigation outcome confirms: **no
  PoE-410-explicit release artifact exists of any kind** —
  no `firmware/` directory, no `firmware/configurations/`,
  no `firmware/sources.json`, no top-level `manifest.json`,
  no `firmware-*.json` (none of those paths exist at HEAD);
  no GitHub Release for any PoE-410-explicit tag exists; no
  PoE-410-explicit `Sense360-…-v{VERSION}-{CHANNEL}.bin`
  artifact has been built / signed / attached / imported;
  no SHA256 / MD5 checksum files for any PoE-410-explicit
  artifact; no build-info `manifest.json` asset for any
  PoE-410-explicit release; no proof row in
  [`docs/webflash-release-proof.md`](docs/webflash-release-proof.md)
  for any PoE-410-explicit artifact; the two existing
  `artifact_name` entries
  (`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`
  and
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`)
  stay byte-identical;
  [`config/webflash-compatibility.json`](config/webflash-compatibility.json)
  `release_one_required_configs` stays
  `["Ceiling-POE-VentIQ-RoomIQ"]`;
  [`.github/workflows/firmware-build-release.yml`](.github/workflows/firmware-build-release.yml)
  stays byte-identical. Investigation outcome recorded at
  [`docs/release-artifact-readiness-matrix.md` §PoE / S360-410 release posture](docs/release-artifact-readiness-matrix.md#poe--s360-410-release-posture)
  and `docs/cleanup-audit.md` §`RELEASE-POE-410-001 update
  (2026-05-20 — docs-only investigation pass)`. No package /
  product / WebFlash / build / release / import / test /
  script / workflow / component / include / firmware /
  manifest / configuration / catalog / compliance edits.
  No catalog `schematic_status` promotion. No
  `schematic_file` set. No `webflash_build_matrix` flip. No
  new `artifact_name` added. No new GitHub Release / tag /
  checksum / build-info manifest / proof row created. No
  BOM ingest (deferred to `HW-BOM-ASSETS-001`). No
  COMPLIANCE-001 movement (`S360-410` PoE PSU is **not** in
  scope because PoE is SELV). No `lifecycle_statuses` /
  `canonical_modules` / `canonical_power` / `forbidden_tokens`
  / `release_one_required_configs` / kit / `REQUIRED_CONFIGS`
  change. No Release-One caveat closure. `RELEASE-POE-410-001`
  stays blocked on the eight preconditions (with the
  carried-forward no-op observation);
  `WF-IMPORT-POE-410-001` (cross-repo) stays blocked behind
  it. Release-One stays `Ceiling-POE-VentIQ-RoomIQ` / version
  `1.0.0` / channel `stable` / artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` /
  tag `v1.0.0`; LED preview stays
  `Ceiling-POE-VentIQ-RoomIQ-LED` / `status: preview` /
  `channel: preview` / artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`;
  FanTRIAC stays `status: blocked` / `blocker: HW-005` /
  `webflash_build_matrix: false`. The next
  `RELEASE-POE-410-001` PR (if and only if
  `PRODUCT-POE-410-001` / `WEBFLASH-POE-410-001` ultimately
  add a new PoE-410-explicit product entry + WebFlash wrapper
  + build-matrix row) must land **the build + sign + attach
  `.bin` + generate release notes + validate release notes +
  emit SHA256 + emit MD5 + attach build-info manifest +
  record proof row + hand off to `WF-IMPORT-POE-410-001`
  (cross-repo) as a single atomic slice**, not as a
  release-notes / proof-template-only PR alone, and only
  after `WEBFLASH-POE-410-001` implementation,
  `PRODUCT-POE-410-001` implementation, `PACKAGE-POE-410-001`
  implementation, the `HW-BOM-ASSETS-001` BOM-ingest
  follow-up, the `S360-410` `schematic_status: verified`
  JSON PR, HW-002 OQ#6 / `S360-100-BENCH-001` J2-harness
  closure, the Release-One PoE caveat-closure PR, and
  product-onboarding approval all land. If
  `PRODUCT-POE-410-001` / `WEBFLASH-POE-410-001` close via
  the default no-new-entry / caveat-closure-only path,
  `RELEASE-POE-410-001` becomes a no-op and no implementation
  PR is needed.
- **PWM** and **DAC** evidence re-checks (HW-PINMAP-311-FOLLOWUP /
  HW-PINMAP-312-FOLLOWUP) remain insufficient — both audits are still
  partial.
- The **TRIAC** chain remains blocked by **HW-005**, **COMPLIANCE-001**, and
  the **PACKAGE-TRIAC-001** docs-only deferral.
- The **LED stable** chain remains blocked by **S360-300-BENCH-001** (bench
  verification) and the WebFlash-owned operator-proof follow-ups.
- **HW-BOM-ASSETS-001** merged as **PR #533** on 2026-05-20.
  It was a **partial-batch, record-only** BOM-evidence
  ingest. New curated artifact indexes were added for
  `S360-200-R4` (Sense360 RoomIQ) at
  `docs/hardware/artifacts/S360-200-R4.md` and `S360-210-R4`
  (Sense360 AirIQ) at `docs/hardware/artifacts/S360-210-R4.md`,
  each recording the uploaded BOM `.xlsx` by filename + size +
  SHA256 + component summary. The S360-200 BOM is
  `b35d4654-S360200R4_BOM.xlsx` (11,177 bytes; SHA256
  `8b9da0fc669091b6015b6af09408edf1e5dc90a4e0aaf8557047c28e9a7e4ae2`);
  the S360-210 BOM is `c551e467-S360210R4_BOM.xlsx`
  (11,966 bytes; SHA256
  `0b3dc2f73d6f71234170b4f0d0b95cd3231ca93218b80cc1d81e0e013477dd23`).
  The S360-100 BOM `df6da128-S360100R4_BOM.xlsx`
  (12,543 bytes; SHA256
  `e289f135a2c88dd747689c70075e2f1cf49906f4bda8b4c4abad67d0dad961fc`)
  and S360-100 PDF re-upload are **byte-identical** to evidence
  already inventoried under HW-ASSETS-002; no new S360-100
  evidence is added. BOM `.xlsx` files stay
  **retained-but-not-committed** per the current
  [`docs/hardware/hardware-artifact-policy.md`](docs/hardware/hardware-artifact-policy.md)
  per-board decision — the `.xlsx` files are **not** added to
  `git` (no `docs/hardware/bom/` directory created). No
  `config/**`, `packages/**`, `products/**`, `tests/**`,
  `scripts/**`, `.github/workflows/**`, `components/**`,
  `include/**`, `firmware/**`, `manifest.json`, or
  `firmware/sources.json` edit. No `schematic_status` /
  `schematic_file` change. No `webflash_build_matrix` flip. No
  `artifact_name`. No `REQUIRED_CONFIGS` or kit change. No
  COMPLIANCE-001 movement. No Release-One change
  (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`). No LED
  preview change. No FanTRIAC change. No Release-One PoE
  caveat closure.
- **HW-BOM-ASSETS-001 is partial.** The BOMs for **S360-211**,
  **S360-300**, **S360-310**, **S360-311**,
  **S360-312** (Fan_GP8403), **S360-320**, **S360-400**, and
  **S360-410** were **not** ingested by PR #533. Their per-board
  `BOM missing` / `BOM cross-check missing` blocker wording in
  the active queue, in `docs/hardware/board-readiness-matrix.md`,
  and in the per-board audit docs is **unchanged**. A later
  `HW-BOM-ASSETS` follow-up PR is owed to ingest the remaining
  eight BOMs and update those blockers. In particular:
  `PACKAGE-POWER-400-001` stays BOM-bound on the three-way
  `HLK-5M05` / `HLK-PM01 or similar` / `HLK-10M05`
  part-identity disagreement; `PACKAGE-POE-410-001` stays
  BOM-bound on the `Ag9712M / Silvertel Ag9700 / or similar`
  vs discrete `TPS2378DDAR / TX4138 / F0505S-2WR2 /
  RJP-003TC1(LPJ4112CNL)` topology disagreement;
  `PACKAGE-RELAY-001` stays blocked on `K1` BOM identity (plus
  `CORE-ABSTRACT-BUS-001A`); `PACKAGE-PWM-001` /
  `PACKAGE-DAC-001` / `PACKAGE-TRIAC-001` stay blocked on
  their existing gates; LED stable stays blocked on
  `S360-300-BENCH-001` plus the WebFlash operator-proof
  follow-ups (LED BOM evidence is **one** of several gates and
  does **not** by itself promote LED stable when it lands).
- **HW-BOM-ASSETS-002 merged as PR #535 on 2026-05-20.**
  It was a second **partial-batch, record-only**
  BOM-evidence ingest. Ingested `S360-400-R4_BOM.xlsx`
  (`95878198-S360400R4_BOM.xlsx`; 10,987 bytes; SHA256
  `bb59f56da11fe83f83b2547322af4e594b658384ade9f06267af367ffb603a1d`)
  and `S360-410-R4_BOM.xlsx`
  (`0de7679d-S360410R4_BOM.xlsx`; 11,980 bytes; SHA256
  `b5f4bad842a930de03cd47327f477c21afcb82e4533a9d8be38b54990b38f285`)
  as **retained-but-not-committed** evidence at
  `docs/hardware/artifacts/S360-400-R4.md` §HW-BOM-ASSETS-002
  BOM ingest and `docs/hardware/artifacts/S360-410-R4.md`
  §HW-BOM-ASSETS-002 BOM ingest. The accompanying
  `S360-410-R4.pdf` re-upload (`7f920771-S360410R4.pdf`;
  975,137 bytes; SHA256
  `4a8b7a3b2a89006a9332eaa486743f687aaedc4b6bb807c6b25670f742ac2414`)
  is byte-identical to the committed PDF; no re-commit. For
  **S360-400**: BOM `PS1` = `HLK-5M05` (HI-LINK) is
  BOM/user-confirmed sourcing truth, agreeing with the catalog
  `description: "Mains to 5V using HLK-5M05."`; schematic-PDF
  value field `PS1 = HLK-10M05` is reclassified as a
  **schematic-label discrepancy** (committed PDF stays
  byte-identical); package header `HLK-PM01 or similar` is now
  disproved package-header comment text (cleanup deferred to
  `PACKAGE-POWER-400-001`). For **S360-410**: the schematic-shown
  discrete topology (`U1 TPS2378DDAR` TI + `U2 TX4138` XDS +
  `DCDC1 F0505S-2WR2` EVISUN + `LAN_CON1 LPJ4112CNL` Link-PP)
  is BOM-confirmed sourcing truth; package-header
  `Ag9712M, Silvertel Ag9700, or similar` is disproved by BOM
  (cleanup deferred to `PACKAGE-POE-410-001`); schematic-annotated
  `AM1D-0505S-NZ` is recorded as a schematic-annotation-only
  alternate not present in the BOM. `power_240v.yaml` and
  `power_poe.yaml` stay byte-identical (no comment-only cleanup;
  deferred to the respective `PACKAGE-*-001` slices). No
  `config/**`, `packages/**`, `products/**`, `tests/**`,
  `scripts/**`, `.github/workflows/**`, `components/**`,
  `include/**`, `firmware/**`, `manifest.json`, or
  `firmware/sources.json` edit. No `schematic_status` /
  `schematic_file` change. No `webflash_build_matrix` flip. No
  `artifact_name`. No `REQUIRED_CONFIGS` or kit change. No
  COMPLIANCE-001 movement (PoE is SELV). No Release-One change.
  No LED preview change. No FanTRIAC change. The Release-One PoE
  `"schematic verification pending"` caveat is **preserved
  verbatim**.
- **PACKAGE-POWER-400-001 — Path B / limited implementation
  package-header cleanup landed on 2026-05-20.** Following the
  `HW-BOM-ASSETS-002` / PR #535 BOM-confirmation of
  `PS1 = HLK-5M05` (HI-LINK), the comment-only header cleanup
  that PR #515 + PR #520 deferred has now landed against
  [`packages/hardware/power_240v.yaml`](packages/hardware/power_240v.yaml).
  Header lines 1–42 reconciled: the disproved `HLK-PM01 or
  similar` AC/DC part hint is removed; the BOM-confirmed part
  identity (`PS1 = HLK-5M05 (HI-LINK)`) and the BOM-confirmed
  populated mains-side protection / connector components
  (`F1 A250-1200` polyfuse; `RV1 10D391K` MOV; `C1 470nF` X-cap;
  `J1` WAGO 2601-3103 1×3 terminal block; `J2` JST SH
  `SM02B-SRSS-TB(LF)(SN)` 1×2) are now named in the header;
  input / output / isolation / protection ratings are
  reclassified under an explicit "Vendor-datasheet typicals
  (NOT BOM-confirmed and NOT compliance evidence)" heading;
  the misleading `1A recommended` AC-input fusing line that
  conflicted with the on-board `F1 A250-1200` polyfuse class is
  removed; the header now explicitly restates that mains-voltage
  UK / EU compliance is tracked by `COMPLIANCE-001` at
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](docs/compliance/mains-voltage-uk-eu-assessment.md)
  and remains **OPEN**, and that no CE / UKCA / FCC / UL /
  LVD / EMC / RoHS / IEC claim is made by this package.
  **Runtime YAML behavior unchanged** — `substitutions:
  power_source: "240v_ac"`, `globals: power_source_type`, the
  four template diagnostic sensors (`Supply Voltage` / `Power
  Source` / `Power Configuration` / `AC Power Connected`), and
  the `logger` block from line 44 onward are **byte-identical**
  to PR #515 / PR #520 / PR #535 state. **No `config/**`,
  `products/**`, `products/webflash/**`, `tests/**`,
  `scripts/**`, `.github/workflows/**`, `components/**`,
  `include/**`, `firmware/**`, `manifest.json`,
  `firmware/sources.json` edit. No `schematic_status` /
  `schematic_file` promotion (`config/hardware-catalog.json`
  `S360-400` row at lines 102–110 stays byte-identical; the
  catalog `description: "Mains to 5V using HLK-5M05."` was
  already BOM-consistent). No COMPLIANCE-001 movement. No
  schematic-PDF correction (the `PS1 = HLK-10M05` value-field
  discrepancy stays recorded but is not corrected; correction
  owed to a separate later HW-ASSETS-400 follow-up). No
  Release-One change (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` /
  `stable`); no LED preview change
  (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`); no FanTRIAC
  change (`blocked` / `HW-005`); no `REQUIRED_CONFIGS` / kit
  change; the four `legacy-compatible` `*-pwr` Core variants
  (`sense360-core-c-pwr.yaml` / `sense360-core-w-pwr.yaml` /
  `sense360-core-v-c-pwr.yaml` / `sense360-core-v-w-pwr.yaml`)
  stay `legacy-compatible` / `webflash_build_matrix: false`.
  `PRODUCT-POWER-400-001`, `WEBFLASH-POWER-400-001`,
  `RELEASE-POWER-400-001`, and `WF-IMPORT-POWER-400-001`
  (cross-repo) **stay blocked** on their other recorded
  preconditions: the residual coordinated
  `PACKAGE-POWER-400-001` work (the `S360-400`
  `schematic_status: verified` JSON-only PR, additionally gated
  on the schematic-side PDF correction), `COMPLIANCE-001`
  `S360-400` slice closure, silkscreen / PCB / creepage /
  clearance / bench / thermal / EMI evidence,
  product-onboarding approval (downstream), UX-class decision
  (WebFlash), and the eight release-time sub-gates (release).
- **PACKAGE-POE-410-001 — Path B / limited implementation
  package-header cleanup landed as PR #538 on 2026-05-21.**
  Following the
  `HW-BOM-ASSETS-002` / PR #535 BOM-confirmation of the
  S360-410-R4 discrete PoE topology (`LAN_CON1 LPJ4112CNL` /
  RJP-003TC1-style RJ45 magnetics, `U1 TPS2378DDAR` PoE PD
  controller, `U2 TX4138` buck, `DCDC1 F0505S-2WR2` isolated
  DC/DC; `AM1D-0505S-NZ` recorded as schematic-annotation-only
  alternate, not the BOM-populated part), the comment-only
  header cleanup that PR #517 + PR #526 deferred has now landed
  against
  [`packages/hardware/power_poe.yaml`](packages/hardware/power_poe.yaml).
  Header lines 1–58 reconciled: the disproved
  `Ag9712M, Silvertel Ag9700, or similar` whole-module PoE
  hint is removed; the BOM-confirmed discrete topology
  (`LAN_CON1 LPJ4112CNL` (RJP-003TC1-style) integrated RJ45 +
  magnetics; `U1 TPS2378DDAR` HSOIC-8 PoE PD controller;
  `U2 TX4138` ESOIC-8 buck; `DCDC1 F0505S-2WR2` SIP-7
  isolated 5V/5V DC/DC with `AM1D-0505S-NZ` explicitly
  reclassified as a schematic-annotation-only alternate
  **not** the BOM-populated part; `D1 SMAJ58A` TVS;
  `D2 SS510` Schottky catch diode; `D3` Green status LED;
  `L1 33uH` buck inductor; `R1..R9`, `C1..C8`, and the `J3`
  `+5VP` / `GND` output header) is now named in the header;
  IEEE 802.3af / Class 0 / input / output / protection
  ratings are reclassified under an explicit
  "Vendor-datasheet typicals (NOT BOM-confirmed and NOT
  compliance evidence)" heading; the header now explicitly
  restates that the package is **logical / diagnostic only**
  (no GPIO / I2C / UART / SPI / DAC runtime binding; emits
  diagnostic-only template sensors) and that no IEEE 802.3af /
  802.3at PoE-compliance / isolation / Hi-pot /
  earth-continuity / leakage / thermal / EMI / EMC claim is
  made by this package. **Runtime YAML behavior unchanged** —
  `substitutions: power_source: "poe"`, `globals:
  power_source_type`, the diagnostic `sensor` / `text_sensor`
  / `binary_sensor` / `logger` blocks, and the `esphome:
  on_boot:` log automation from `substitutions:` onward are
  **byte-identical** to PR #517 / PR #526 / PR #535 state
  (SHA256 of the `substitutions:`-onward block unchanged
  before and after this PR). **No `config/**`, `products/**`,
  `products/webflash/**`, `tests/**`, `scripts/**`,
  `.github/workflows/**`, `components/**`, `include/**`,
  `firmware/**`, `manifest.json`, `firmware/sources.json`,
  `docs/compliance/**`, `config/hardware-catalog.json`,
  `config/product-catalog.json`, `config/webflash-builds.json`,
  or `config/webflash-compatibility.json` edit. No
  `schematic_status` / `schematic_file` promotion (the
  `S360-410` row in `config/hardware-catalog.json` stays
  byte-identical; `schematic_status: cataloged_unverified` is
  unchanged; `schematic_file` is not set). No COMPLIANCE-001
  movement (PoE is SELV; `S360-410` is **not** in scope for
  COMPLIANCE-001). No Release-One PoE
  `"schematic verification pending"` caveat closure
  (preserved verbatim). No product YAML added. No WebFlash
  wrapper added. No `webflash_build_matrix: true` flip. No
  `artifact_name` added. No release artifact built or
  attached. No Release-One change
  (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`); no
  LED preview change (`Ceiling-POE-VentIQ-RoomIQ-LED` /
  `preview`); no FanTRIAC change (`blocked` / `HW-005`); no
  `REQUIRED_CONFIGS` / kit change; the six
  `legacy-compatible` `*-poe` Core variants stay
  `legacy-compatible` / `webflash_build_matrix: false`.
  `PRODUCT-POE-410-001`, `WEBFLASH-POE-410-001`,
  `RELEASE-POE-410-001`, and `WF-IMPORT-POE-410-001`
  (cross-repo) **stay blocked** on their other recorded
  preconditions: the `S360-410` `schematic_status: verified`
  JSON PR, HW-002 OQ#6 / `S360-100-BENCH-001` J2-harness
  identity closure, the Release-One PoE caveat-closure PR,
  product-onboarding approval (downstream), UX-class decision
  (WebFlash), and the eight release-time sub-gates (release).
- **HW-BOM-ASSETS-002 is also partial.** Six BOMs remain owed
  to a later `HW-BOM-ASSETS` follow-up: **S360-211**,
  **S360-300**, **S360-310**, **S360-311**, **S360-312**
  (Fan_GP8403), and **S360-320**. Their per-board
  `BOM missing` / `BOM cross-check missing` blocker wording is
  unchanged. The `PACKAGE-POWER-400-001` and
  `PACKAGE-POE-410-001` BOM-cross-check preconditions are now
  **landed under HW-BOM-ASSETS-002**, but both implementation
  slices stay blocked on their other recorded preconditions
  (see active-queue entries #4–#7 below for the refreshed
  precondition wording). `PACKAGE-RELAY-001` /
  `PACKAGE-PWM-001` / `PACKAGE-DAC-001` / `PACKAGE-TRIAC-001`
  / LED stable stay blocked on their existing gates.
- **FW-MATRIX-001 — generated firmware combination readiness
  matrix landed as PR #539 on 2026-05-21** and
  **FW-MATRIX-002 — firmware build-gap report landed as PR #540
  on 2026-05-21.** PR #539 added
  `scripts/generate_firmware_matrix.py` (enumerator + classifier
  with a `--check` freshness mode for CI), the 168-row generated
  `config/firmware-combination-matrix.json` (every valid
  WebFlash-style config-string combination enumerated from
  `config/webflash-compatibility.json` and classified against
  `config/product-catalog.json` and
  `config/webflash-builds.json`),
  `tests/test_firmware_combination_matrix.py`, and
  `docs/firmware-combination-matrix.md`. PR #540 added
  `scripts/report_firmware_build_gaps.py`,
  `docs/firmware-build-gap-report.md`,
  `tests/test_firmware_build_gap_report.py`, and a see-also link
  in `docs/firmware-combination-matrix.md`, grouping all 168
  valid combinations into ordered priority lanes so future PRs
  can pick build / package / product work in priority order
  rather than randomly. **Both PRs are readiness / planning
  artifacts only.** No firmware build was added, no product YAML
  was added, no WebFlash wrapper was added, no release artifact
  was produced, no `webflash_build_matrix: true` flip happened,
  `config/webflash-builds.json` was not changed,
  `config/product-catalog.json` was not changed,
  `config/hardware-catalog.json` was not changed,
  `REQUIRED_CONFIGS` was not changed, the LED preview was not
  promoted to stable, and `RELEASE-007` was not unblocked. The
  two committed builds remain authoritative:
  `Ceiling-POE-VentIQ-RoomIQ` (stable) and
  `Ceiling-POE-VentIQ-RoomIQ-LED` (preview). The firmware
  combination matrix and the build-gap report are now the
  planning foundation for future product / build / WebFlash /
  release work in this repo — downstream slices should consult
  the priority lanes in
  [`docs/firmware-build-gap-report.md`](docs/firmware-build-gap-report.md)
  when sequencing work rather than re-enumerating the raw 168
  rows. **KIT-MATRIX-001 has now landed as PR #542** (see the
  next bullet); it added the productized kit / bundle intent
  matrix at `config/kit-intent-matrix.json`,
  `docs/kit-intent-matrix.md`, and
  `tests/test_kit_intent_matrix.py` and is itself planning /
  docs / data only (no product YAML, no WebFlash wrapper, no
  firmware build, no release artifact, no
  `webflash_build_matrix` flip, no `artifact_name`, no stable
  promotion, no `RELEASE-007` unblock). WebFlash installability
  remains controlled exclusively by
  `config/webflash-builds.json` and the WebFlash manifest.
- **KIT-MATRIX-001 — productized kit / bundle intent matrix
  landed as PR #542 on 2026-05-21.** Added the source-of-truth
  planning matrix at `config/kit-intent-matrix.json` (six initial
  kit intent rows: `S360-KIT-BATH-POE` /
  `S360-KIT-BATH-POE-LED` / `S360-KIT-BATH-RELAY` /
  `S360-KIT-BATH-TRIAC` / `S360-KIT-DUCT-PWM` /
  `S360-KIT-DUCT-0-10V`), the documentation at
  `docs/kit-intent-matrix.md` (kit-SKU vs module-SKU vs
  firmware-config-string identifier separation, productization
  rules, wizard usage, hard guardrails), and the tests at
  `tests/test_kit_intent_matrix.py` (21 stdlib-unittest cases
  pinning kit-id uniqueness, default-config-string presence in
  the firmware matrix, S360-KIT-BATH-POE stable-ready mapping,
  S360-KIT-BATH-POE-LED preview blockers including
  `S360-300-BENCH-001` / `WF-HW-TEST-001` / `WF-HW-TEST-003`,
  FanTRIAC blockers including `HW-005` / `COMPLIANCE-001`, PWM
  and FanDAC kits being classified as duct-fan futures rather
  than default bathroom stable kits, and the guardrails that no
  kit with `webflash_exposure_allowed_now=true` points to a
  config string absent from `config/webflash-builds.json` and
  that no PWR-bearing kit claims WebFlash exposure or stable
  readiness). **PR #542 is planning / docs / data only.** No
  product YAML was added, no WebFlash wrapper was added, no
  firmware was built, no release artifact was produced, no
  `webflash_build_matrix: true` flip happened, no `artifact_name`
  was added, the LED preview was not promoted to stable,
  `RELEASE-007` was not unblocked, and
  `config/webflash-builds.json` / `config/product-catalog.json`
  / `config/hardware-catalog.json` /
  `config/webflash-compatibility.json` /
  `config/firmware-combination-matrix.json` were not changed.
  The two committed firmware builds remain authoritative:
  `Ceiling-POE-VentIQ-RoomIQ` (stable) and
  `Ceiling-POE-VentIQ-RoomIQ-LED` (preview). **KIT-MATRIX-001 /
  PR #542 has landed and is now the productized kit-intent
  planning layer above
  [`config/firmware-combination-matrix.json`](config/firmware-combination-matrix.json)
  and
  [`docs/firmware-build-gap-report.md`](docs/firmware-build-gap-report.md)**;
  downstream product / WebFlash / release sequencing should pull
  from the kit intent view rather than the raw combination
  matrix, while WebFlash installability remains controlled
  exclusively by `config/webflash-builds.json` and the WebFlash
  manifest. The next planning-step pointer is
  **WF-KIT-PRESETS-001 — WebFlash Stage 1 productized bundle
  presets**, a future docs / data PR that would surface the
  kit-intent matrix rows as Stage 1 productized bundle presets
  in the WebFlash UI without itself flipping
  `webflash_build_matrix` or adding any new buildable
  config-string to `config/webflash-builds.json`.
- **FW-COMPILE-MATRIX-001 — compile-only firmware validation lane
  landed as PR #544 on 2026-05-21.** Added the compile-only
  target metadata at `config/compile-only-targets.json`, the
  metadata + compile validator at
  `scripts/validate_compile_targets.py`, the structural /
  cross-reference / guardrail tests at
  `tests/test_compile_targets.py`, an optional clearly-named
  GitHub workflow at `.github/workflows/compile-only.yml`, and
  the documentation at
  `docs/compile-only-firmware-validation.md`. The lane currently
  covers the two committed WebFlash product YAMLs
  (`products/webflash/ceiling-poe-ventiq-roomiq.yaml` and
  `products/webflash/ceiling-poe-ventiq-roomiq-led.yaml`).
  **PR #544 is compile-only confidence only.** Compile success is
  necessary but not sufficient: there is no hardware proof, no
  WebFlash import, no release artifact, no stable promotion, and
  no WebFlash build-matrix expansion. Next-step pointer: run the
  workflow's `workflow_dispatch` full compile mode against the
  two committed product YAMLs; if full compile fails, fix the
  compile issues; if full compile passes, future PRs may add
  reviewed compile-only targets or new product YAMLs to the
  lane, still without WebFlash exposure, release artifacts,
  stable promotion, or hardware proof.
- **FW-COMPILE-FIX-001 — compile-only secrets provisioning fix
  landed as PR #546 on 2026-05-21.** The
  `Compile-only Firmware Validation` workflow's full compile job
  was failing at config-validation time because the
  `Provision test secrets` step only wrote `secrets.yaml` at the
  repo root and under `products/`, while the current compile-only
  targets live under `products/webflash/`. ESPHome resolves
  `!secret` lookups relative to the top-level YAML being compiled,
  so the compile step aborted with
  `Error reading file products/webflash/secrets.yaml: No such file
  or directory`. PR #546 provisions
  `products/webflash/secrets.yaml` so `esphome compile` can resolve
  `!secret` for both wrapper YAMLs. **PR #546 is a workflow-only
  bug fix.** It does not add WebFlash exposure, release artifacts,
  product YAMLs, WebFlash wrappers, build-matrix entries, hardware
  proof, or LED stable promotion.
- **FW-COMPILE-RESULT-001 — record successful full compile validation
  (2026-05-21 audit).** The
  `Compile-only Firmware Validation` workflow was manually run via
  `workflow_dispatch` with `compile_mode=full` after PR #546 landed
  and **passed**. Run number `#9`
  (<https://github.com/sense360store/esphome-public/actions/runs/26228528326>),
  job `Compile-only Targets — Full ESPHome Compile`
  (<https://github.com/sense360store/esphome-public/actions/runs/26228528326/job/77182121905>),
  result `succeeded`, duration `7m 33s`, ESPHome `2026.4.5`,
  Python `3.11.15`, command
  `python3 scripts/validate_compile_targets.py --compile`. Both
  compile-only targets returned `rc=0`
  (`ceiling-poe-ventiq-roomiq-webflash` and
  `ceiling-poe-ventiq-roomiq-led-webflash`); the validator reported
  `All 2 compile target(s) passed.` This audit closes the PR #544
  next-step pointer ("run the workflow's `workflow_dispatch` full
  compile mode") and is recorded in
  [`docs/compile-only-firmware-validation.md`](docs/compile-only-firmware-validation.md#2026-05-21--fw-compile-result-001-successful-full-compile-run).
  **FW-COMPILE-RESULT-001 is a docs-only audit recording.** It
  proves YAML / package / ESPHome compile confidence for the two
  current WebFlash product YAMLs under ESPHome `2026.4.5`; it does
  **not** prove hardware behavior, Web Serial flashing, boot on
  real hardware, sensor or LED runtime behavior, Improv / Home
  Assistant handoff, release readiness, LED stable readiness,
  WebFlash import readiness, or compliance. No `config/**`,
  `products/**`, `products/webflash/**`, `packages/**`,
  `firmware/**`, `manifest.json`, `firmware/sources.json`,
  `.github/workflows/**`, release artifact, checksum, or
  build-info manifest is touched; no compile target is added; no
  `webflash_build_matrix: true` flip; no `artifact_name` added; no
  LED stable promotion; no `RELEASE-007` unblock; no Release-One /
  LED preview / FanTRIAC identity change.
- **FW-COMPILE-POE-NONFAN-001 — POE non-fan compile-only expansion
  (2026-05-21).** Added five compile-only product YAML skeletons for
  safe POE non-fan candidates under `products/compile-only/` —
  `ceiling-poe.yaml` (`Ceiling-POE`), `ceiling-poe-roomiq.yaml`
  (`Ceiling-POE-RoomIQ`), `ceiling-poe-ventiq.yaml`
  (`Ceiling-POE-VentIQ`), `ceiling-poe-airiq.yaml`
  (`Ceiling-POE-AirIQ`), and `ceiling-poe-airiq-roomiq.yaml`
  (`Ceiling-POE-AirIQ-RoomIQ`). Each skeleton composes only from
  packages already proven to compose by either the Release-One YAML
  (`products/webflash/ceiling-poe-ventiq-roomiq.yaml`) or
  `products/sense360-core-ceiling.yaml`; no new package is added.
  Each is enrolled in `config/compile-only-targets.json` with
  `shipment_status: compile-only`,
  `webflash_exposure_allowed_now: false`,
  `hardware_required_for_validation: true`, `blocked: false`, and a
  POE-non-fan-compile-confidence reason; totals updated from 2 to 7.
  Added `PoeNonFanCompileOnlyCoverageTests` in
  `tests/test_compile_targets.py` (14 new cases pinning: every
  candidate's product YAML exists on disk under
  `products/compile-only/`; every candidate's `config_string` is
  present in `config/firmware-combination-matrix.json`; no candidate
  is in `config/webflash-builds.json`; every candidate is
  `shipment_status: compile-only`,
  `webflash_exposure_allowed_now: false`,
  `hardware_required_for_validation: true`; no candidate declares
  `webflash_build_matrix` / `artifact_name` / `webflash_wrapper`; no
  candidate carries a `FanRelay` / `FanPWM` / `FanDAC` / `FanTRIAC` /
  `PWR` token; totals match expected count). Extended
  `.github/workflows/compile-only.yml` to provision a
  `products/compile-only/secrets.yaml` stub during the full compile
  job so `!secret` lookups resolve for the new directory. Added the
  `### 2026-05-21 — FW-COMPILE-POE-NONFAN-001 POE non-fan
  compile-only expansion` section to
  `docs/compile-only-firmware-validation.md` (target list table,
  lower-risk rationale, what compile-only proves for the five new
  candidates, and what compile-only does **not** prove). **PR is
  compile-only confidence only.** No `config/webflash-builds.json`
  edit, no `config/product-catalog.json` edit, no
  `config/hardware-catalog.json` edit, no
  `config/webflash-compatibility.json` edit, no
  `config/firmware-combination-matrix.json` edit, no
  `config/kit-intent-matrix.json` edit, no `products/webflash/**`
  edit, no `firmware/**` / `manifest.json` / `firmware/sources.json`
  / release artifact / checksum / build-info manifest edit, no
  WebFlash wrapper added, no `webflash_build_matrix: true` flip, no
  `artifact_name` added, no release artifact built or attached, no
  firmware import, no LED stable promotion, no AirIQ stable / preview
  / release promotion, no POE / `S360-410` promotion, no fan-control
  target added, no PWR / `S360-400` target added, no hardware-proof
  claim, no WebFlash import-readiness claim, no `RELEASE-007`
  unblock claim, no Release-One / LED preview / FanTRIAC identity
  change, no `release_one_required_configs` /
  `lifecycle_statuses` / `canonical_modules` / `canonical_power` /
  `forbidden_tokens` / `REQUIRED_CONFIGS` / kit change, no
  `schematic_status` / `schematic_file` promotion, no COMPLIANCE-001
  movement, no Release-One PoE caveat closure. Next-step pointer:
  run `workflow_dispatch` with `compile_mode=full` against the
  expanded lane; if any new target fails compile, fix the compile
  failure (or, if a target is invalid by grammar / unsafe to
  represent, remove only that target).
- **FW-COMPILE-EXPAND-001 — identify next compile-only target
  candidates (2026-05-21).** Added a reviewed, machine-readable
  candidate ledger for the next compile-only firmware targets at
  `config/compile-only-candidates.json` (26 ranked candidates
  spanning the four non-blocked lanes — `poe-non-fan` /
  `poe-non-fan-led` / `usb-non-fan` / `usb-non-fan-led` — and
  representative deferral rows for each blocked lane: `pwr` /
  `fanrelay` / `fanpwm` / `fandac` / `fantriac`). Each candidate
  carries the required schema (`config_string`, `rank`, `lane`,
  `use_case`, `proposed_product_yaml`, `candidate_status`,
  `reason`, `blockers`, `would_be_webflash_exposed_now: false`,
  `compile_only_safe`). Documentation at
  `docs/compile-only-expansion-candidates.md` explains the
  per-row schema, the lane ranking invariant, the
  already-compile-only POE non-fan anchors, the POE LED preview
  next-up compile-only candidates, the USB non-fan and USB LED
  preview future candidates blocked on the USB-family scope
  decision, and the PWR / FanRelay / FanPWM / FanDAC / FanTRIAC
  deferral rationale. Tests at
  `tests/test_compile_expansion_candidates.py` (37 stdlib-unittest
  cases) pin: schema shape and required / forbidden fields; allowed
  candidate statuses and lanes; no duplicate `config_string` or
  `rank`; every candidate's `config_string` is present in
  `config/firmware-combination-matrix.json`; no candidate appears
  in `config/webflash-builds.json` unless it is one of the two
  currently shipping builds (none do); no PWR candidate is marked
  `compile_only_safe=true`; no FanTRIAC candidate is marked
  `compile_only_safe=true`; FanRelay candidates carry both a
  `PACKAGE-RELAY-001` blocker and a `CORE-ABSTRACT-BUS-001*`
  blocker; FanPWM candidates carry both a `PACKAGE-PWM-001` blocker
  and a `CORE-ABSTRACT-BUS-001*` blocker; FanDAC candidates carry
  both a `PACKAGE-DAC-001` blocker and a `CORE-ABSTRACT-BUS-001*`
  blocker; FanTRIAC candidates carry both an `HW-005` and a
  `COMPLIANCE-001` blocker; non-blocked lane ranks (POE / USB non-fan
  +/- LED) are all strictly lower than blocked lane ranks (PWR /
  FanRelay / FanPWM / FanDAC / FanTRIAC); no candidate declares
  forbidden shipment fields (`artifact_name`, `webflash_build_matrix`,
  `webflash_wrapper`, `release_ready`, `stable_ready`,
  `hardware_proof`, etc.) or claims release readiness or hardware
  proof; the doc references the candidate JSON and the test file;
  `currently_shipping_config_strings` matches the actual two
  WebFlash builds; `currently_compile_only_config_strings` matches
  the seven targets actually present in
  `config/compile-only-targets.json`. **PR is planning-ledger
  confidence only.** No `config/compile-only-targets.json` edit, no
  `config/webflash-builds.json` edit, no `config/product-catalog.json`
  edit, no `config/hardware-catalog.json` edit, no
  `config/webflash-compatibility.json` edit, no
  `config/firmware-combination-matrix.json` edit, no
  `config/kit-intent-matrix.json` edit, no `products/**` edit, no
  `products/webflash/**` edit, no `packages/**` edit, no
  `firmware/**` / `manifest.json` / `firmware/sources.json` /
  release artifact / checksum / build-info manifest edit, no
  `.github/workflows/**` edit, no compile-only target added, no
  product YAML added, no WebFlash wrapper added, no
  `webflash_build_matrix: true` flip, no `artifact_name` added, no
  release artifact built or attached, no firmware import, no LED
  stable promotion, no AirIQ stable / preview / release promotion,
  no POE / `S360-410` promotion, no PWR / `S360-400` promotion, no
  fan-control target added, no hardware-proof claim, no WebFlash
  import-readiness claim, no `RELEASE-007` unblock claim, no
  Release-One / LED preview / FanTRIAC identity change, no
  `release_one_required_configs` / `lifecycle_statuses` /
  `canonical_modules` / `canonical_power` / `forbidden_tokens` /
  `REQUIRED_CONFIGS` / kit change, no `schematic_status` /
  `schematic_file` promotion, no `COMPLIANCE-001` movement, no
  Release-One PoE caveat closure. Next-step pointer: once a
  compile-only PR picks up Lane 2 (POE non-fan LED preview), it
  must add the candidate's `proposed_product_yaml` under
  `products/compile-only/`, enroll it in
  `config/compile-only-targets.json` with
  `shipment_status: compile-only` /
  `webflash_exposure_allowed_now: false` /
  `hardware_required_for_validation: true`, and run
  `workflow_dispatch` with `compile_mode=full` to verify the
  compile; it must NOT promote LED to stable, NOT add a
  `webflash_wrapper`, NOT flip `webflash_build_matrix`, NOT add
  `artifact_name`, NOT add to `config/webflash-builds.json`, and
  NOT close `S360-300-BENCH-001` / `WF-HW-TEST-001` /
  `WF-HW-TEST-003` / `RELEASE-007`. Lane 3 / Lane 4 (USB) require
  a USB-family scope decision and a USB power package first
  (neither exists today). The PWR / FanRelay / FanPWM / FanDAC /
  FanTRIAC deferral rows remain blocked behind their named
  evidence chains and must not be added as compile-only targets
  until those chains close.
- **PACKAGE-NAMING-AUDIT-001 — audit `packages/**` filenames
  against productized naming model (2026-05-21).** Added
  `docs/package-naming-audit.md` recording an inventory of every
  YAML file under `packages/**` (79 files across `base/` (9),
  `expansions/` (24), `features/` (24), and `hardware/` (22))
  classified against
  the WebFlash token list from `docs/webflash-contract.md` §3.
  Per-file rows record current path, apparent purpose,
  customer-facing concept, module identity, config-string token
  relationship, current known consumers (from repo grep across
  `products/**` and `packages/**`), recommended canonical name,
  migration risk, and whether a compatibility shim is recommended.
  The classification taxonomy is `canonical-current` /
  `acceptable-internal` / `legacy-compatible` / `misleading-name`
  / `behavior-hidden-by-name` / `candidate-for-alias` /
  `candidate-for-future-rename`. Four problem areas are documented
  in detail: (1) AirIQ — `AirIQ` is reused for the productized
  `S360-210` module, for the productized `S360-211` (VentIQ)
  module via the legacy `airiq_bathroom_*` filenames, and as a
  generic IAQ-feature token in `packages/features/airiq_*`; (2)
  VentIQ / bathroom — `bathroom_profile.yaml` and
  `bathroom_pro_profile.yaml` use the forbidden `Bathroom` token
  but already carry `VentIQ` in user-facing entity names; (3)
  RoomIQ / comfort / presence — `comfort_*.yaml` and
  `presence_*.yaml` filenames use forbidden `Comfort` and
  `Presence` tokens but entity names already use `RoomIQ`; (4)
  hidden control behaviour —
  `packages/features/airiq_advanced_profile.yaml` adds an
  `auto_fan_control` script and a `fan_switch` output on GPIO15
  that is not described by the filename. The naming-policy section
  documents eight rules (filenames are internal; customer-facing
  names are outcome-first; module names map to SKUs; config
  strings remain build identity; avoid `basic` / `advanced` /
  `pro` unless explicitly productized; avoid filenames that hide
  control behaviour; deprecated WebFlash tokens never appear in
  new filenames; compatibility shims live in the repo). The
  five-phase migration plan is Phase 1 (this audit), Phase 2
  (canonical aliases that `!include` legacy files), Phase 3 (new
  compile-only / product YAMLs use canonical names), Phase 4
  (deprecation comments on legacy files), Phase 5 (legacy
  filename removal after all consumers migrated and one release
  tag has elapsed). **PR is audit / docs / planning only.** No
  `packages/**` rename / move / delete; no `packages/**` content
  edit; no `products/**` / `products/webflash/**` /
  `firmware/**` / `manifest.json` / `firmware/sources.json` /
  `.github/workflows/**` / `components/**` / `include/**` edit;
  no `config/compile-only-targets.json` /
  `config/compile-only-candidates.json` /
  `config/webflash-builds.json` /
  `config/product-catalog.json` /
  `config/hardware-catalog.json` /
  `config/webflash-compatibility.json` /
  `config/firmware-combination-matrix.json` /
  `config/kit-intent-matrix.json` edit; no `tests/**` /
  `scripts/**` edit; no `forbidden_tokens` / `canonical_modules`
  / `canonical_power` / `lifecycle_statuses` /
  `release_one_required_configs` / `REQUIRED_CONFIGS` /
  `webflash_build_matrix` / `artifact_name` / `webflash_wrapper`
  / `config_string` change; no compile-only target added; no
  product YAML added; no WebFlash wrapper added; no LED stable
  promotion; no AirIQ / VentIQ / RoomIQ / fan / PWR / POE
  promotion; no hardware-proof claim; no WebFlash
  import-readiness claim; no `RELEASE-007` unblock claim; no
  Release-One / LED preview / FanTRIAC identity change; no
  `schematic_status` / `schematic_file` promotion; no
  COMPLIANCE-001 movement; no release artifact built or attached.
  Next-step pointer: Phase 2 PRs would add canonical-name alias
  files (e.g. `packages/expansions/ventiq.yaml` `!include`-wrapping
  `packages/expansions/bathroom.yaml`); each Phase-2 PR is its own
  scoped change with its own evidence and tests and must not edit
  the legacy file.
- **FW-COMPILE-POE-NONFAN-RESULT-001 — record 7-target compile success
  (2026-05-21 audit).** After FW-COMPILE-POE-NONFAN-001 / PR #548
  expanded the compile-only lane from 2 to 7 targets, the
  `Compile-only Firmware Validation` workflow was manually re-run via
  `workflow_dispatch` with `compile_mode=full` against the expanded
  lane and **passed**. Run URL
  <https://github.com/sense360store/esphome-public/actions/runs/26236882386>,
  full compile job ID `77212453770`
  (`Compile-only Targets — Full ESPHome Compile`), result `success`,
  commit tested `1b587cd25cdf5d7bd400cf9b783dccbbb8de3442`, start /
  end `2026-05-21T15:48:46Z` → `2026-05-21T16:10:03Z`, ESPHome
  `2026.4.5`, Python `3.11.15`, command
  `python3 scripts/validate_compile_targets.py --compile`. All seven
  compile-only targets returned `rc=0`
  (`ceiling-poe-ventiq-roomiq-webflash`,
  `ceiling-poe-ventiq-roomiq-led-webflash`,
  `ceiling-poe-compile-only`, `ceiling-poe-roomiq-compile-only`,
  `ceiling-poe-ventiq-compile-only`, `ceiling-poe-airiq-compile-only`,
  `ceiling-poe-airiq-roomiq-compile-only`); the validator reported
  `All 7 compile target(s) passed.` This audit closes the
  FW-COMPILE-POE-NONFAN-001 next-step pointer ("run
  `workflow_dispatch` with `compile_mode=full` against the expanded
  lane") and is recorded in
  [`docs/compile-only-firmware-validation.md`](docs/compile-only-firmware-validation.md#2026-05-21--poe-non-fan-7-target-full-compile-result).
  **FW-COMPILE-POE-NONFAN-RESULT-001 is a docs-only audit recording
  of the compile result only.** It proves YAML / package / ESPHome
  compile confidence for the two current WebFlash product YAMLs (no
  regression) and for the five POE non-fan compile-only skeletons
  under `products/compile-only/`, all under ESPHome `2026.4.5`. CI
  will now catch future package drift across the 7-target compile
  lane on subsequent `workflow_dispatch` `compile_mode=full` runs.
  It does **not** prove hardware behavior, Web Serial flashing, boot
  on real hardware, sensor runtime behavior, LED runtime behavior,
  Improv / Home Assistant handoff, release artifacts, WebFlash
  import readiness, WebFlash exposure, `REQUIRED_CONFIGS`
  eligibility, stable promotion, LED stable promotion,
  `RELEASE-007` unblock, or compliance. No `config/**`,
  `products/**`, `products/webflash/**`, `packages/**`,
  `firmware/**`, `manifest.json`, `firmware/sources.json`,
  `.github/workflows/**`, release artifact, checksum, or
  build-info manifest is touched; no compile-only target is added;
  no `webflash_build_matrix: true` flip; no `artifact_name` added;
  no `webflash_wrapper` added; no LED stable promotion; no
  AirIQ / VentIQ / RoomIQ promotion; no POE / `S360-410`
  promotion; no PWR / `S360-400` promotion; no fan-module
  promotion; no `RELEASE-007` unblock; no Release-One / LED
  preview / FanTRIAC identity change; no Release-One PoE caveat
  closure.
- **PACKAGE-NAMING-ALIASES-VENTIQ-001 — add VentIQ canonical
  package aliases (Phase 2 of PACKAGE-NAMING-AUDIT-001 /
  PR #550) (2026-05-21).** Added four canonical VentIQ alias
  package files that wrap the legacy bathroom / airiq_bathroom
  package files via `!include` and add no other YAML:
  `packages/expansions/ventiq.yaml` wraps
  `packages/expansions/airiq_bathroom_base.yaml`;
  `packages/expansions/ventiq_extended.yaml` wraps
  `packages/expansions/airiq_bathroom_pro.yaml`;
  `packages/features/ventiq_profile.yaml` wraps
  `packages/features/bathroom_profile.yaml`;
  `packages/features/ventiq_extended_profile.yaml` wraps
  `packages/features/bathroom_pro_profile.yaml`. The `_extended`
  suffix is deliberately not `_pro`: per naming-audit Rule 5, a
  filename containing `pro` must not imply a productized Pro tier
  customer SKU unless that SKU exists in
  `config/hardware-catalog.json` and
  `config/kit-intent-matrix.json`, which is not the case today
  for any VentIQ Pro variant. Alias filenames carry no token
  listed in `config/webflash-compatibility.json`'s
  `forbidden_tokens` (`Bathroom`, `Comfort`, `Presence`, generic
  `Fan`, `FanAnalog`). Added
  `tests/test_ventiq_alias_packages.py` (9 stdlib-unittest cases:
  alias files exist; aliases parse as YAML; each alias contains
  exactly one `!include` line targeting the intended legacy bare
  basename; alias filenames carry no forbidden customer-facing
  token; alias filenames start with the `ventiq` token; legacy
  implementation files still exist; alias inventory shape pinning
  — exactly four entries, no duplicate alias_path, no duplicate
  legacy_path). Updated `docs/package-naming-audit.md` with a
  new `#### Phase 2 progress — VentIQ aliases landed (2026-05-21)`
  subsection inside the Phase-2 section that records the
  alias / legacy mapping table and the four notes on the chosen
  alias names. **PR is alias-only.** No legacy `packages/**` file
  edited / moved / renamed / deleted; no other `packages/**` file
  added; no `products/**` / `products/webflash/**` /
  `firmware/**` / `manifest.json` / `firmware/sources.json` /
  `.github/workflows/**` / `components/**` / `include/**` edit;
  no `config/compile-only-targets.json` /
  `config/compile-only-candidates.json` /
  `config/webflash-builds.json` /
  `config/product-catalog.json` /
  `config/hardware-catalog.json` /
  `config/webflash-compatibility.json` /
  `config/firmware-combination-matrix.json` /
  `config/kit-intent-matrix.json` edit; no
  `forbidden_tokens` / `canonical_modules` / `canonical_power` /
  `lifecycle_statuses` / `release_one_required_configs` /
  `REQUIRED_CONFIGS` / `webflash_build_matrix` / `artifact_name`
  / `webflash_wrapper` / `config_string` change; no compile-only
  target added; no product YAML added; no WebFlash wrapper added;
  no LED stable promotion; no AirIQ / VentIQ / RoomIQ / fan / PWR
  / POE promotion; no hardware-proof claim; no WebFlash
  import-readiness claim; no `RELEASE-007` unblock claim; no
  Release-One / LED preview / FanTRIAC identity change; no
  `schematic_status` / `schematic_file` promotion; no
  COMPLIANCE-001 movement; no release artifact built or
  attached. Runtime YAML behavior is unchanged: the aliases are
  pure `!include` wrappers; no existing consumer of the legacy
  filenames is affected. Validation suite (`python3
  tests/validate_configs.py`, `python3
  scripts/validate_compile_targets.py --metadata-only`, `python3
  tests/test_compile_targets.py`, `python3
  tests/test_compile_expansion_candidates.py`, `python3
  tests/test_firmware_combination_matrix.py`, `python3
  tests/test_firmware_build_gap_report.py`, `python3
  tests/test_kit_intent_matrix.py`, `python3
  tests/validate_webflash_builds.py`, `python3 -m unittest
  discover -s tests -p "test_*.py"`) all pass. Next-step pointer:
  remaining Phase-2 slices (`roomiq_*` aliases for
  `comfort_*` / `presence_*`; `fan_dac.yaml` alias for
  `fan_gp8403.yaml`; `airiq_profile_*` aliases for the
  `airiq_basic_profile.yaml` / `airiq_advanced_profile.yaml`
  pair, with the latter renamed to reveal the hidden auto-fan
  behaviour) are each their own scoped PR with their own
  evidence and tests and are not landed here.
- **PACKAGE-NAMING-ALIASES-ROOMIQ-001 — add RoomIQ canonical
  package aliases (Phase 2 of PACKAGE-NAMING-AUDIT-001 /
  PR #550, second slice after PACKAGE-NAMING-ALIASES-VENTIQ-001 /
  PR #552) (2026-05-21).** Added four canonical RoomIQ alias
  package files that wrap the legacy comfort / presence package
  files via `!include` and add no other YAML:
  `packages/expansions/roomiq.yaml` wraps
  `packages/expansions/comfort_ceiling.yaml`;
  `packages/expansions/roomiq_radar.yaml` wraps
  `packages/expansions/presence_ceiling.yaml`;
  `packages/features/roomiq_profile.yaml` wraps
  `packages/features/comfort_basic_profile.yaml`;
  `packages/features/roomiq_radar_profile.yaml` wraps
  `packages/features/presence_basic_profile.yaml`. The four
  target legacy files are exactly the ones the Release-One
  product `products/sense360-ceiling-poe-ventiq-roomiq.yaml`
  already binds to under `roomiq_*` package keys. The `_radar`
  suffix on `roomiq_radar.yaml` and `roomiq_radar_profile.yaml`
  is deliberately not `_presence`: per naming-audit Rule 7,
  `Presence` is listed in
  `config/webflash-compatibility.json`'s `forbidden_tokens`
  array and must not appear in any newly added package filename.
  `_radar` describes the underlying 24GHz mmWave radar sensor
  (HLK-LD2450 by default, with optional DFRobot C4001) consumed
  by the legacy `presence_ceiling.yaml` /
  `presence_basic_profile.yaml` files and avoids the deprecated
  `Presence` token. Alias filenames carry no token listed in
  `config/webflash-compatibility.json`'s `forbidden_tokens`
  (`Bathroom`, `Comfort`, `Presence`, generic `Fan`,
  `FanAnalog`). Added `tests/test_roomiq_alias_packages.py`
  (9 stdlib-unittest cases mirroring
  `tests/test_ventiq_alias_packages.py`: alias files exist;
  aliases parse as YAML; each alias contains exactly one
  `!include` line targeting the intended legacy bare basename;
  alias filenames carry no forbidden customer-facing token;
  alias filenames start with the `roomiq` token; legacy
  implementation files still exist; alias inventory shape
  pinning — exactly four entries, no duplicate alias_path, no
  duplicate legacy_path). Updated `docs/package-naming-audit.md`
  with a new `#### Phase 2 progress — RoomIQ aliases landed
  (2026-05-21)` subsection inside the Phase-2 section that
  records the alias / legacy mapping table and the four notes
  on the chosen alias names. **PR is alias-only.** No legacy
  `packages/**` file edited / moved / renamed / deleted; no
  other `packages/**` file added; no `products/**` /
  `products/webflash/**` / `firmware/**` / `manifest.json` /
  `firmware/sources.json` / `.github/workflows/**` /
  `components/**` / `include/**` edit; no
  `config/compile-only-targets.json` /
  `config/compile-only-candidates.json` /
  `config/webflash-builds.json` /
  `config/product-catalog.json` /
  `config/hardware-catalog.json` /
  `config/webflash-compatibility.json` /
  `config/firmware-combination-matrix.json` /
  `config/kit-intent-matrix.json` edit; no
  `forbidden_tokens` / `canonical_modules` / `canonical_power` /
  `lifecycle_statuses` / `release_one_required_configs` /
  `REQUIRED_CONFIGS` / `webflash_build_matrix` / `artifact_name`
  / `webflash_wrapper` / `config_string` change; no compile-only
  target added; no product YAML added; no WebFlash wrapper
  added; no LED stable promotion; no AirIQ / VentIQ / RoomIQ /
  fan / PWR / POE promotion; no hardware-proof claim; no
  WebFlash import-readiness claim; no `RELEASE-007` unblock
  claim; no Release-One / LED preview / FanTRIAC identity
  change; no `schematic_status` / `schematic_file` promotion;
  no COMPLIANCE-001 movement; no release artifact built or
  attached. Runtime YAML behavior is unchanged: the aliases are
  pure `!include` wrappers; no existing consumer of the legacy
  filenames is affected. Validation suite (`python3
  tests/validate_configs.py`, `python3
  scripts/validate_compile_targets.py --metadata-only`,
  `python3 tests/test_compile_targets.py`, `python3
  tests/test_compile_expansion_candidates.py`, `python3
  tests/test_firmware_combination_matrix.py`, `python3
  tests/test_firmware_build_gap_report.py`, `python3
  tests/test_kit_intent_matrix.py`, `python3
  tests/test_ventiq_alias_packages.py`, `python3
  tests/test_roomiq_alias_packages.py`, `python3
  tests/validate_webflash_builds.py`, `python3 -m unittest
  discover -s tests -p "test_*.py"`) all pass. Next-step
  pointer: remaining Phase-2 slices (additional `roomiq_*`
  aliases for wall / S3-ceiling form factors and the orphan
  generic `comfort.yaml`; `fan_dac.yaml` alias for
  `fan_gp8403.yaml`; `airiq_profile_*` aliases for the
  `airiq_basic_profile.yaml` / `airiq_advanced_profile.yaml`
  pair, with the latter renamed to reveal the hidden auto-fan
  behaviour) are each their own scoped PR with their own
  evidence and tests and are not landed here.
- **CORE-ABSTRACT-BUS-001C-REBIND-PLAN-001 — record schematic-backed
  `CORE-ABSTRACT-BUS-001C` rebind plan (2026-05-21).** Docs-only
  planning record. Added a new sibling doc at
  `docs/hardware/core-abstract-bus-001c-rebind-plan.md` that records
  the schematic-backed and operator-confirmed decisions needed to
  unblock `CORE-ABSTRACT-BUS-001C` implementation planning. The
  schematic-side evidence is drawn from the committed
  `S360-100-R4.pdf` Core schematic and `S360-200-R4.pdf` RoomIQ
  schematic and is presented as connector-net tables for Core `J10`
  and RoomIQ `J6` reconciled in the same straight-through, pin-1-to-
  pin-1 net order. Operator-confirmed decisions recorded: (1)
  screenshots are from the committed `S360-100-R4` schematic; (2)
  Core `J10` carries `SEN0609_RX` / `SEN0609_TX` / `out(gpio6)` /
  `Hi-Link_RX` / `Hi-Link_TX` / `PIR` / `ALS_INT` / `I2C_SDA` /
  `I2C_SCL` (plus `+3.3V` / `+5V` / `GND` rails); (3) RoomIQ `J6`
  schematic shows the same net order as Core `J10`; (4) the Core
  `J10` to RoomIQ `J6` harness is intended straight-through, pin 1
  to pin 1; (5) UART labels are ESP32 / Core-perspective
  (`Hi-Link_TX` = ESPHome `tx_pin`, `Hi-Link_RX` = ESPHome `rx_pin`,
  `SEN0609_TX` = ESPHome `tx_pin`, `SEN0609_RX` = ESPHome `rx_pin`);
  (6) both Hi-Link and SEN0609 radars are populated / intended to
  be supported; (7) baud rates confirmed (`Hi-Link` = 256000,
  `SEN0609` = 115200); (8) S360-300 LED ring / status ring data is
  `GPIO38` / `LED_DATA`; (9) the generic Core `status_led_pin`
  should be retired; (10) `GPIO46` / `GP_Fan_Status_Led` should be
  retained as `fan_status_led_pin`; (11) `GPIO7` / `AirQ_Status_Led`
  and `GPIO8` / `AirQ_Led` are AirIQ-only; (12) VentIQ has no
  dedicated Core-driven LED / status line; (13) generic
  `expansion_gpio1..4` should be retired and replaced with
  function-specific names; (14) `out(gpio6)` is the SEN0609 output
  pin; (15) canonical substitution name for `out(gpio6)` is
  `roomiq_sen0609_output_pin`; (16) `GPIO3` boot / strap behaviour
  is operator-confirmed OK on `S360-100-R4` with `S360-310` Relay
  attached (scoped to the populated pair under operator review; not
  a generic claim); (17) the Relay stayed off / not energized
  during boot; (18) `S360-310` revision is accepted as R4 for this
  planning record (no `schematic_status` promotion); (19) the
  Relay connector / harness is accepted as straight-through / keyed
  correctly for this planning record (full bench-side harness
  identity / `K1` BOM / contact-current rating / approvals remain
  owed). The proposed `001C` substitution map is recorded in the
  new doc: RoomIQ UARTs `roomiq_hi_link_uart` (`tx_pin: GPIO2`,
  `rx_pin: GPIO1`, `baud_rate: 256000`) and `roomiq_sen0609_uart`
  (`tx_pin: GPIO5`, `rx_pin: GPIO4`, `baud_rate: 115200`); RoomIQ
  GPIO `pir_sensor_pin: GPIO15`, `comfort_ceiling_als_int_pin` (or
  canonical RoomIQ alias equivalent): `GPIO47`,
  `roomiq_sen0609_output_pin: GPIO6`; expander interrupt
  `expander_int_pin: GPIO17` and `sx1509_interrupt_pin: GPIO17`
  (both rebound off `GPIO3`); LED / status decisions retire the
  generic `status_led_pin`, retain S360-300 LED ring on `GPIO38`
  owned by the LED ring package, introduce / retain
  `fan_status_led_pin: GPIO46`, classify `airiq_status_led_pin:
  GPIO7` and `airiq_led_pin: GPIO8` as AirIQ-only, and record
  VentIQ as having no Core-driven LED / status line; expansion GPIO
  `expansion_gpio1..4` retired in favour of function-specific
  substitutions only; Relay / 001A dependency reserves `GPIO3` for
  the Relay (the `001C` slice frees `GPIO3` by moving `ALS_INT` and
  expander interrupt away from it; the Relay electrical / load /
  `K1` rating proof remains separate and does not become complete
  here). Updated
  `docs/hardware/core-abstract-bus-reconciliation.md` with the
  new dated section `### 2026-05-21 — CORE-ABSTRACT-BUS-001C
  rebind plan evidence` that links to the new rebind plan doc and
  states that `001C` is now implementation-plannable but package
  YAML has not changed. The active-queue `CORE-ABSTRACT-BUS-001C`
  entry above has been refreshed to record that schematic /
  operator decisions are now committed but implementation still
  requires a scoped YAML / test PR. **No package YAML edit, no
  product YAML edit, no WebFlash wrapper, no JSON catalog change,
  no script, no test, no workflow, no component, no include, no
  firmware artifact, no manifest, no release artifact, no
  checksum, no build-info manifest, no kit / lifecycle /
  canonical / required-config / webflash_build_matrix /
  artifact_name / webflash_wrapper / config_string entry change,
  no `schematic_status` / `schematic_file` promotion, no
  COMPLIANCE-001 movement, no Release-One change
  (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`), no LED
  preview change (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`),
  no FanTRIAC change (`blocked` / `HW-005`), no Relay package
  completion claim, no Relay load / contact proof claim, no
  `RELEASE-RELAY-001` unblock claim, no WebFlash import readiness
  claim, no hardware stable / release readiness claim.** Runtime
  YAML behavior is unchanged. Validation suite (`python3
  tests/validate_configs.py`, `python3
  scripts/validate_compile_targets.py --metadata-only`, `python3
  tests/test_compile_targets.py`, `python3
  tests/test_compile_expansion_candidates.py`, `python3
  tests/test_firmware_combination_matrix.py`, `python3
  tests/test_firmware_build_gap_report.py`, `python3
  tests/test_kit_intent_matrix.py`, `python3
  tests/validate_webflash_builds.py`, `python3 -m unittest
  discover -s tests -p "test_*.py"`) all pass. Next-step pointer:
  the next `001C` PR must land the schematic-backed substitution
  map (now recorded in
  `docs/hardware/core-abstract-bus-001c-rebind-plan.md`) plus the
  pin-pinning test scaffold (`tests/test_core_abstract_bus.py`)
  plus the YAML edits across the affected Core abstract packages
  and the affected expansion packages plus the Release-One
  generated-config diff check plus the re-validation pass for
  every non-Release-One product YAML consuming an affected Core
  package as a **single atomic implementation slice**, and must
  land at-or-before `CORE-ABSTRACT-BUS-001A` (the `relay_pin:
  GPIO3` slice) per the `GPIO3` collision recorded in
  `docs/hardware/core-abstract-bus-reconciliation.md` §GPIO
  collision matrix.
- **PACKAGE-NAMING-ALIASES-AIRIQ-001 — add AirIQ canonical
  package aliases (Phase 2 of PACKAGE-NAMING-AUDIT-001 /
  PR #550, third slice after PACKAGE-NAMING-ALIASES-VENTIQ-001 /
  PR #552 and PACKAGE-NAMING-ALIASES-ROOMIQ-001 / PR #553)
  (2026-05-21).** Added four canonical AirIQ alias package files
  that wrap the legacy AirIQ feature-profile files via `!include`
  and add no other YAML:
  `packages/features/airiq_profile.yaml` wraps
  `packages/features/airiq_basic.yaml` (the safest-default
  user-facing AirIQ feature profile — Excellent / Good / Fair /
  Poor rating, Temperature, Humidity, recommendation text,
  air-quality alert binary sensor; no MQTT, no GPIO output);
  `packages/features/airiq_extended_profile.yaml` wraps
  `packages/features/airiq_advanced.yaml` (extended CO₂ / PM1.0 /
  PM2.5 / PM4.0 / PM10 / VOC / NOx sensors, threshold globals,
  customizable threshold controls, sensor-calibration buttons,
  composite `evaluate_air_quality` AQI calculation script — the
  script only calculates AQI, it does not drive any GPIO output
  and does not toggle any fan switch, so the file remains pure
  AirIQ sensing / display behaviour);
  `packages/features/airiq_mqtt_profile.yaml` wraps
  `packages/features/airiq_basic_profile.yaml` (the AirIQ MQTT
  publish profile with `airiq_mqtt_broker` /
  `airiq_mqtt_port` / `airiq_mqtt_username` /
  `airiq_mqtt_password` substitutions, the placeholder
  `air_quality_state` template text sensor, and a top-level
  `mqtt:` block publishing IAQ telemetry under
  `${device_name}/air_quality`); and
  `packages/features/airiq_auto_ventilation_profile.yaml` wraps
  `packages/features/airiq_advanced_profile.yaml` (the
  behaviour-hidden-by-name legacy file that declares a `gpio`
  output on `GPIO15`, a `fan_switch` template switch exposed as
  `${friendly_name} Air Exchange`, and an `auto_fan_control`
  script that toggles the fan switch on changes to
  `air_quality_state`). The `_extended` suffix on
  `airiq_extended_profile.yaml` is deliberately not `_advanced`
  or `_pro`: per naming-audit Rule 5, a filename containing
  `advanced` or `pro` must not imply a productized tier customer
  SKU unless that SKU exists in `config/hardware-catalog.json`
  and `config/kit-intent-matrix.json`, which is not the case
  today for any AirIQ extended tier (mirrors the VentIQ slice's
  `_extended` precedent on `ventiq_extended.yaml` /
  `ventiq_extended_profile.yaml`). The `_mqtt` suffix on
  `airiq_mqtt_profile.yaml` names the dominant behavioural
  surface (MQTT publishing) explicitly so downstream readers and
  new product YAMLs can tell at a glance that including this
  profile turns on MQTT, replacing the ambiguous legacy `basic`
  tier token. The `_auto_ventilation` suffix on
  `airiq_auto_ventilation_profile.yaml` names the hidden
  fan-control behaviour explicitly per naming-audit Rule 6
  (avoid package names that hide control behaviour); the token
  `auto_ventilation` describes the behaviour (automated air
  exchange) without using the forbidden WebFlash customer-facing
  token `Fan` listed in
  `config/webflash-compatibility.json`'s `forbidden_tokens`. All
  four alias filenames carry no token listed in
  `config/webflash-compatibility.json`'s `forbidden_tokens`
  (`Bathroom`, `Comfort`, `Presence`, generic `Fan`,
  `FanAnalog`). All four aliases live under
  `packages/features/` because every legacy AirIQ feature-profile
  file lives there; the existing `packages/expansions/airiq.yaml`
  / `airiq_ceiling.yaml` / `airiq_ceiling_s3.yaml` /
  `airiq_wall.yaml` are already `canonical-current` per the
  per-area findings table and do not need an alias, and the
  legacy `packages/expansions/airiq_bathroom_*` files were
  already aliased under canonical `VentIQ` names in
  PACKAGE-NAMING-ALIASES-VENTIQ-001. Added
  `tests/test_airiq_alias_packages.py` (10 stdlib-unittest cases
  mirroring `tests/test_ventiq_alias_packages.py` and
  `tests/test_roomiq_alias_packages.py`: alias files exist;
  aliases parse as YAML; each alias contains exactly one
  `!include` line targeting the intended legacy bare basename;
  alias filenames carry no forbidden customer-facing token;
  alias filenames start with the `airiq` token; legacy
  implementation files still exist; alias inventory shape
  pinning — exactly four entries, no duplicate alias_path, no
  duplicate legacy_path; plus a new fan-control behaviour-
  revealing-name test that pins the Rule 6 requirement — any
  alias wrapping a legacy file that drives a fan output /
  fan_switch must contain a behaviour-revealing term such as
  `auto_ventilation`). Updated `docs/package-naming-audit.md`
  with a new `#### Phase 2 progress — AirIQ aliases landed
  (2026-05-21)` subsection inside the Phase-2 section that
  records the alias / legacy mapping table and the notes on the
  chosen alias names (covering the safest-default classification
  of `airiq_basic.yaml`, the still-pure-sensing classification
  of `airiq_advanced.yaml`, the MQTT-publish classification of
  `airiq_basic_profile.yaml`, and the
  behaviour-hidden-by-name fan-control classification of
  `airiq_advanced_profile.yaml`). **PR is alias-only.** No
  legacy `packages/**` file edited / moved / renamed / deleted;
  no other `packages/**` file added; no `products/**` /
  `products/webflash/**` / `firmware/**` / `manifest.json` /
  `firmware/sources.json` / `.github/workflows/**` /
  `components/**` / `include/**` edit; no
  `config/compile-only-targets.json` /
  `config/compile-only-candidates.json` /
  `config/webflash-builds.json` /
  `config/product-catalog.json` /
  `config/hardware-catalog.json` /
  `config/webflash-compatibility.json` /
  `config/firmware-combination-matrix.json` /
  `config/kit-intent-matrix.json` edit; no
  `forbidden_tokens` / `canonical_modules` / `canonical_power` /
  `lifecycle_statuses` / `release_one_required_configs` /
  `REQUIRED_CONFIGS` / `webflash_build_matrix` / `artifact_name`
  / `webflash_wrapper` / `config_string` change; no compile-only
  target added; no product YAML added; no WebFlash wrapper
  added; no LED stable promotion; no AirIQ / VentIQ / RoomIQ /
  fan / PWR / POE promotion; no hardware-proof claim; no
  WebFlash import-readiness claim; no `RELEASE-007` unblock
  claim; no Release-One / LED preview / FanTRIAC identity
  change; no `schematic_status` / `schematic_file` promotion;
  no COMPLIANCE-001 movement; no Core bus / GPIO / UART / LED /
  status substitution change; no release artifact built or
  attached. Runtime YAML behavior is unchanged: the aliases are
  pure `!include` wrappers; no existing consumer of the legacy
  filenames is affected. Validation suite (`python3
  tests/validate_configs.py`, `python3
  scripts/validate_compile_targets.py --metadata-only`,
  `python3 tests/test_compile_targets.py`, `python3
  tests/test_compile_expansion_candidates.py`, `python3
  tests/test_firmware_combination_matrix.py`, `python3
  tests/test_firmware_build_gap_report.py`, `python3
  tests/test_kit_intent_matrix.py`, `python3
  tests/test_ventiq_alias_packages.py`, `python3
  tests/test_roomiq_alias_packages.py`, `python3
  tests/test_airiq_alias_packages.py`, `python3
  tests/validate_webflash_builds.py`, `python3 -m unittest
  discover -s tests -p "test_*.py"`) all pass. Next-step
  pointer: remaining Phase-2 slices (`fan_dac.yaml` alias for
  `fan_gp8403.yaml`; wall / S3-ceiling RoomIQ form-factor
  aliases; orphan generic `comfort.yaml` alias) are each their
  own scoped PR with their own evidence and tests and are not
  landed here.
- **PACKAGE-NAMING-ALIASES-FANDAC-001 — add FanDAC canonical
  package alias (Phase 2 of PACKAGE-NAMING-AUDIT-001 / PR #550,
  fourth slice after PACKAGE-NAMING-ALIASES-VENTIQ-001 / PR #552,
  PACKAGE-NAMING-ALIASES-ROOMIQ-001 / PR #553, and
  PACKAGE-NAMING-ALIASES-AIRIQ-001 / PR #555) (2026-05-21).**
  Added one canonical FanDAC alias package file that wraps the
  legacy GP8403 DAC package via `!include` and adds no other YAML:
  `packages/expansions/fan_dac.yaml` wraps
  `packages/expansions/fan_gp8403.yaml`. The legacy filename
  `fan_gp8403.yaml` is named after the GP8403 DAC implementation
  detail (a DFRobot dual-channel 12-bit I²C DAC providing 0–10V
  or 0–5V analog output for commercial HVAC fans / EC motors /
  VFDs); the productized / package-facing module name is `FanDAC`
  (a member of `config/webflash-compatibility.json`'s
  `canonical_modules` array alongside `AirIQ`, `VentIQ`, `RoomIQ`,
  `FanRelay`, `FanPWM`, `FanTRIAC`, and `LED`). The alias filename
  `fan_dac.yaml` is the lowercase `snake_case` rendering of the
  canonical `FanDAC` module token, mirroring the existing
  `airiq.yaml` / `ventiq.yaml` / `roomiq.yaml` precedent where the
  alias filename is the lowercase rendering of the productized
  module token. **Why the alias filename is allowed despite the
  `Fan` forbidden token.** The token `Fan` (uppercase, standalone)
  is listed in `config/webflash-compatibility.json`'s
  `forbidden_tokens` array as a generic / customer-facing label
  that must not appear in WebFlash artifact filenames; the
  productized fan modules are firmware-distinct (`FanRelay` /
  `FanPWM` / `FanDAC` / `FanTRIAC`) per the
  `fan_variants_are_firmware_distinct` rule and the
  `generic_fan_token_forbidden` rule. This file is an internal
  `packages/**` implementation alias, not a WebFlash artifact
  name; the canonical product / module token it represents is
  `FanDAC`, not the forbidden generic `Fan` token. The audit's
  non-binding Phase-2 inventory in `docs/package-naming-audit.md`
  explicitly proposes `fan_dac.yaml` as the canonical alias for
  `fan_gp8403.yaml`. Customer-facing labels surfaced to the
  WebFlash UI / Home Assistant / marketing remain outcome-first
  (for example, "0–10V fan control" describes what the customer
  gets without leaking the GP8403 chip name or the forbidden
  generic `Fan` token); the alias file must not be exposed as a
  loose customer-facing product. Added
  `tests/test_fandac_alias_packages.py` (12 stdlib-unittest cases
  mirroring `tests/test_ventiq_alias_packages.py`,
  `tests/test_roomiq_alias_packages.py`, and
  `tests/test_airiq_alias_packages.py`: alias file exists; alias
  parses as YAML; alias contains exactly one `!include` line
  targeting the intended legacy bare basename; alias `!include`s
  exactly `fan_gp8403.yaml`; alias filename starts with the
  canonical `fan_dac` token; legacy implementation file still
  exists; alias inventory shape pinning — exactly one entry, no
  duplicate alias_path, no duplicate legacy_path; plus new
  pure-wrapper Rule 8 tests that pin the alias contains only the
  `packages:` top-level key, does not redeclare any forbidden
  top-level YAML block such as `substitutions:` / `globals:` /
  `sensor:` / `output:` / `fan:` / `script:` / `gp8403:`, and
  does not embed any fan-control behaviour beyond the single
  `!include` of the legacy file). The forbidden-token assertion
  used by the VentIQ / RoomIQ / AirIQ alias tests is deliberately
  not applied here because `FanDAC` is the canonical module token
  rather than a forbidden token. Updated
  `docs/package-naming-audit.md` with a new `#### Phase 2
  progress — FanDAC alias landed (2026-05-21)` subsection inside
  the Phase-2 section that records the alias / legacy mapping
  table and the notes on the chosen alias name (covering the
  canonical-`FanDAC`-versus-vendor-`gp8403` rationale, the
  `Fan`-forbidden-token justification, the GP8403-is-
  implementation-detail rationale, and the absence of a separate
  behaviour-revealing suffix because `FanDAC` already names the
  underlying DAC-driven 0–10V control behaviour at the module-
  token level). **PR is alias-only.** No legacy `packages/**`
  file edited / moved / renamed / deleted (the legacy
  `fan_gp8403.yaml` file is byte-identical); no other
  `packages/**` file added; no `products/**` /
  `products/webflash/**` / `firmware/**` / `manifest.json` /
  `firmware/sources.json` / `.github/workflows/**` /
  `components/**` / `include/**` edit; no
  `config/compile-only-targets.json` /
  `config/compile-only-candidates.json` /
  `config/webflash-builds.json` /
  `config/product-catalog.json` /
  `config/hardware-catalog.json` /
  `config/webflash-compatibility.json` /
  `config/firmware-combination-matrix.json` /
  `config/kit-intent-matrix.json` edit; no
  `forbidden_tokens` / `canonical_modules` / `canonical_power` /
  `lifecycle_statuses` / `release_one_required_configs` /
  `REQUIRED_CONFIGS` / `webflash_build_matrix` / `artifact_name`
  / `webflash_wrapper` / `config_string` change; no compile-only
  target added; no product YAML added; no WebFlash wrapper added;
  no LED stable promotion; no AirIQ / VentIQ / RoomIQ / fan / PWR
  / POE promotion; no FanDAC promotion; no DAC readiness claim;
  no fan-module promotion; no hardware-proof claim; no WebFlash
  import-readiness claim; no `RELEASE-DAC-001` unblock claim; no
  `RELEASE-007` unblock claim; no Release-One / LED preview /
  FanTRIAC identity change; no `schematic_status` /
  `schematic_file` promotion; no COMPLIANCE-001 movement; no
  Core bus / GPIO / UART / LED / status substitution change; no
  release artifact built or attached. Runtime YAML behavior is
  unchanged: the alias is a pure `!include` wrapper; no existing
  consumer of the legacy `fan_gp8403.yaml` filename is affected.
  Validation suite (`python3 tests/validate_configs.py`, `python3
  scripts/validate_compile_targets.py --metadata-only`, `python3
  tests/test_compile_targets.py`, `python3
  tests/test_compile_expansion_candidates.py`, `python3
  tests/test_firmware_combination_matrix.py`, `python3
  tests/test_firmware_build_gap_report.py`, `python3
  tests/test_kit_intent_matrix.py`, `python3
  tests/test_ventiq_alias_packages.py`, `python3
  tests/test_roomiq_alias_packages.py`, `python3
  tests/test_airiq_alias_packages.py`, `python3
  tests/test_fandac_alias_packages.py`, `python3
  tests/validate_webflash_builds.py`, `python3 -m unittest
  discover -s tests -p "test_*.py"`) all pass. Next-step
  pointer: remaining Phase-2 slices (wall / S3-ceiling RoomIQ
  form-factor aliases; orphan generic `comfort.yaml` alias; any
  future fan-side feature aliases) are each their own scoped PR
  with their own evidence and tests and are not landed here.

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
| PACKAGE-POWER-400-001        | #520      | esphome-public  | Merged — docs-only investigation pass   | Recorded `PACKAGE-POWER-400-001` investigation outcome as Path A docs-only deferral; re-verified all five preconditions (BOM cross-check missing; `S360-400` `schematic_status: verified` JSON PR not landed; `COMPLIANCE-001` `S360-400` slice still open; silkscreen / PCB / creepage / clearance / bench / thermal / EMI evidence missing; three-way AC/DC part-identity disagreement between catalog `HLK-5M05`, package header `HLK-PM01 or similar`, and schematic `PS1 = HLK-10M05` unresolved and BOM-bound) remain open; `power_240v.yaml` re-confirmed byte-identical to PR #515 state (stale `HLK-PM01 or similar` header at line 7, `100-240V AC, 50/60Hz` input claim at line 7, `5V DC, 2A (10W)` output claim at line 8, `3000VAC` isolation claim at line 9, `Overcurrent, overvoltage, short-circuit` protection text at line 10, recommended `1A` AC-input fusing line at line 15, `substitutions: power_source: "240v_ac"` at line 29, `globals: power_source_type` at lines 32–36, template diagnostic sensors `Supply Voltage` / `Power Source` / `Power Configuration` / `AC Power Connected`, and logger config all preserved); `config/hardware-catalog.json` `S360-400` row at lines 102–110 re-confirmed byte-identical (`schematic_status: cataloged_unverified`, no `schematic_file`, `description: Mains to 5V using HLK-5M05.`); `tests/test_hardware_catalog.py:53` `EXPECTED_STILL_UNVERIFIED_SKUS = frozenset({"S360-320", "S360-400"})` actively enforces the `cataloged_unverified` state; `docs/hardware/s360-400-r4-power.md` audit-log entry `### 2026-05-19 — PACKAGE-POWER-400-001 investigation pass (deferred; preconditions still open)` added; `docs/cleanup-audit.md` `PACKAGE-POWER-400-001 update (2026-05-19 — docs-only investigation pass)` entry recorded; `docs/hardware/package-readiness-matrix.md` `power_240v.yaml` row and `docs/hardware/firmware-package-mapping-audit.md` §`power_240v.yaml` AC/DC part-identity disagreement cross-link addendums recorded | No package, product, WebFlash, build, release, compliance, JSON catalog, test, script, workflow, component, include, firmware, or manifest edits; no `schematic_status` / `schematic_file` promotion; no COMPLIANCE-001 movement; no PWR-bearing entry added; `power_240v.yaml` byte-identical to PR #515 (comment-only cleanup still deferred); four `legacy-compatible` `*-pwr` Core variants (`sense360-core-c-pwr.yaml` / `sense360-core-w-pwr.yaml` / `sense360-core-v-c-pwr.yaml` / `sense360-core-v-w-pwr.yaml`) stay `legacy-compatible` / `webflash_build_matrix: false`; Release-One / LED preview / FanTRIAC identity unchanged | `PACKAGE-POWER-400-001` stays blocked on the five preconditions; `PRODUCT-POWER-400-001` / `WEBFLASH-POWER-400-001` / `RELEASE-POWER-400-001` / `WF-IMPORT-POWER-400-001` stay blocked behind it; `PRODUCT-POWER-400-001` becomes next active queue item |
| PRODUCT-POWER-400-001        | #521      | esphome-public  | Merged — docs-only investigation pass   | Recorded `PRODUCT-POWER-400-001` investigation outcome as Path A docs-only deferral; re-verified all six preconditions (`PACKAGE-POWER-400-001` implementation slice not landed — only docs-only investigation merged as PR #520; BOM cross-check missing — same five-component gap as PR #520; `S360-400` `schematic_status: verified` JSON PR not landed; `COMPLIANCE-001` `S360-400` slice still open — last re-check PR #506; package / catalog reconciliation owed to `PACKAGE-POWER-400-001`; product-onboarding approval missing per `docs/product-onboarding.md`) remain open; no S360-400-explicit / `PWR`-bearing WebFlash-shippable product YAML exists under `products/` or `products/webflash/`; `config/product-catalog.json` has no S360-400-specific product (four `legacy-compatible` `*-pwr` Core variants stay `legacy-compatible` / `webflash_build_matrix: false` / no `config_string` / no `webflash_wrapper` / no `artifact_name`); `config/webflash-builds.json` has no `PWR` build (only `Ceiling-POE-VentIQ-RoomIQ` stable + `Ceiling-POE-VentIQ-RoomIQ-LED` preview); `config/webflash-compatibility.json` reserves `PWR` in `canonical_power` with no `webflash_build_matrix: true` consumer; `release_one_required_configs` stays `["Ceiling-POE-VentIQ-RoomIQ"]`; `config/hardware-catalog.json` `S360-400` row stays byte-identical (`schematic_status: cataloged_unverified`, no `schematic_file`, `description: Mains to 5V using HLK-5M05.`); `tests/test_hardware_catalog.py:53` `EXPECTED_STILL_UNVERIFIED_SKUS = frozenset({"S360-320", "S360-400"})` enforces this state; `docs/product-readiness-matrix.md` §PWR-240V / S360-400 + Follow-up PR sequence cross-link addendums recorded; `docs/webflash-exposure-readiness-matrix.md` §Power / S360-400 WebFlash posture audit-log entry added; `docs/release-artifact-readiness-matrix.md` §Power / S360-400 release posture audit-log entry added; `docs/cleanup-audit.md` `PRODUCT-POWER-400-001 update (2026-05-19 — docs-only investigation pass)` section recorded | No package, product, WebFlash, build, release, compliance, JSON catalog, test, script, workflow, component, include, firmware, or manifest edits; no `schematic_status` / `schematic_file` promotion; no COMPLIANCE-001 movement; no PWR-bearing entry added; no `webflash_build_matrix: true` flip; no new `artifact_name`; no `lifecycle_statuses` / `canonical_modules` / `canonical_power` / `forbidden_tokens` / `release_one_required_configs` / `webflash_build_matrix` / kit / `REQUIRED_CONFIGS` change; `packages/hardware/power_240v.yaml` byte-identical to PR #520 state; four `legacy-compatible` `*-pwr` Core variants stay `legacy-compatible` / `webflash_build_matrix: false`; Release-One / LED preview / FanTRIAC identity unchanged | `PRODUCT-POWER-400-001` stays blocked on the six preconditions; `WEBFLASH-POWER-400-001` / `RELEASE-POWER-400-001` / `WF-IMPORT-POWER-400-001` stay blocked behind it; `WEBFLASH-POWER-400-001` becomes next active queue item |
| WEBFLASH-POWER-400-001       | #522      | esphome-public  | Merged — docs-only investigation pass   | Recorded `WEBFLASH-POWER-400-001` investigation outcome as Path A docs-only deferral; re-verified all five preconditions (`PRODUCT-POWER-400-001` implementation slice not landed — only docs-only investigation merged as PR #521; `PACKAGE-POWER-400-001` implementation slice not landed — only docs-only investigation merged as PR #520; `S360-400` `schematic_status: verified` JSON PR not landed; `COMPLIANCE-001` `S360-400` slice still open — last re-check PR #506; UX-class decision pending — standard preview-candidate vs advanced / manual-warning posture owed to per-family `PRODUCT-POWER-400-001` compliance verdict) remain open; no S360-400 WebFlash wrapper exists under `products/webflash/` (three PoE wrappers only: `ceiling-poe-ventiq-roomiq.yaml`, `ceiling-poe-ventiq-roomiq-led.yaml`, `ceiling-poe-ventiq-fantriac-roomiq.yaml`); `config/webflash-builds.json` has no `PWR` build (two PoE builds only); `config/webflash-compatibility.json` reserves `PWR` in `canonical_power` with no `webflash_build_matrix: true` consumer; `release_one_required_configs` stays `["Ceiling-POE-VentIQ-RoomIQ"]`; `config/product-catalog.json` has no S360-400-specific product (four `legacy-compatible` `*-pwr` Core variants unchanged); `config/hardware-catalog.json` `S360-400` row stays byte-identical; `tests/test_hardware_catalog.py:53` continues to enforce `cataloged_unverified`; `docs/webflash-exposure-readiness-matrix.md` §Power / S360-400 WebFlash posture audit-log entry added; `docs/release-artifact-readiness-matrix.md` §Power / S360-400 release posture audit-log entry added; `docs/cleanup-audit.md` `WEBFLASH-POWER-400-001 update (2026-05-19 — docs-only investigation pass)` section recorded | No package, product, WebFlash, build, release, compliance, JSON catalog, test, script, workflow, component, include, firmware, or manifest edits; no `schematic_status` / `schematic_file` promotion; no COMPLIANCE-001 movement; no PWR-bearing entry added; no `webflash_build_matrix: true` flip; no new `artifact_name`; no `lifecycle_statuses` / `canonical_modules` / `canonical_power` / `forbidden_tokens` / `release_one_required_configs` / kit / `REQUIRED_CONFIGS` change; `packages/hardware/power_240v.yaml` byte-identical; `products/webflash/` byte-identical (only three PoE wrappers); `.github/workflows/firmware-build-release.yml` byte-identical; Release-One / LED preview / FanTRIAC identity unchanged | `WEBFLASH-POWER-400-001` stays blocked on the five preconditions; `RELEASE-POWER-400-001` / `WF-IMPORT-POWER-400-001` stay blocked behind it; `RELEASE-POWER-400-001` becomes next active queue item |
| RELEASE-POWER-400-001        | #523      | esphome-public  | Merged — docs-only investigation pass   | Recorded `RELEASE-POWER-400-001` Path A deferral; confirmed no S360-400 release artifact, firmware/source/manifest/release proof/checksum/tag/build-matrix inputs exist; recorded Q1–Q15 release-surface findings; kept all release gates blocked | No package, product, WebFlash, build, release, compliance, JSON catalog, test, script, workflow, component, include, firmware, manifest, checksum, release-proof, or artifact edits | `RELEASE-POWER-400-001` stays blocked behind `WEBFLASH-POWER-400-001` implementation, `PRODUCT-POWER-400-001`, `PACKAGE-POWER-400-001`, `S360-400 schematic_status: verified`, `COMPLIANCE-001`, BOM/silkscreen/bench/thermal/EMI evidence, and UX-class decision; `WF-IMPORT-POWER-400-001` stays blocked |
| CLEANUP-POWER-RELEASE-001    | #524      | esphome-public  | Merged — docs-only tracker cleanup      | Removed stale `WEBFLASH-POWER-400-001` / `RELEASE-POWER-400-001` tracker prose left after PR #523; converted stale "this PR" references so `WEBFLASH-POWER-400-001` consistently points to PR #522 and `RELEASE-POWER-400-001` consistently points to PR #523 | No functional, package, product, WebFlash, build, release, compliance, JSON catalog, test, script, workflow, component, include, firmware, manifest, or artifact files | Prepared the tracker for `CLEANUP-POWER-RELEASE-002` / PR #525, which then removed the remaining duplicate active `RELEASE-POWER-400-001` stub; no queue-ordering effect on `PACKAGE-POE-410-001` |
| CLEANUP-POWER-RELEASE-002    | #525      | esphome-public  | Merged — docs-only tracker cleanup      | Removed the stale duplicate active-queue stub entry for `RELEASE-POWER-400-001` (and the duplicate `PRODUCT-POWER-400-001` #521 merged-table row) left over after PR #523; renumbered the active queue so `PACKAGE-POE-410-001` is the next item | No functional, package, product, WebFlash, build, release, compliance, JSON catalog, test, script, workflow, component, include, firmware, manifest, or artifact files | `PACKAGE-POE-410-001` becomes the next active queue item; downstream `PRODUCT-POE-410-001` / `WEBFLASH-POE-410-001` / `RELEASE-POE-410-001` / `WF-IMPORT-POE-410-001` stay blocked behind it |
| PACKAGE-POE-410-001          | #526      | esphome-public  | Merged — docs-only investigation pass   | Recorded `PACKAGE-POE-410-001` Path A deferral; confirmed BOM cross-check / `S360-410 schematic_status: verified` JSON promotion / HW-002 OQ#6 / `S360-100-BENCH-001` J2-harness identity closure / package-header reconciliation / Release-One PoE "schematic verification pending" caveat-closure preconditions remain open; kept `packages/hardware/power_poe.yaml` byte-identical to PR #517 state | No package, product, WebFlash, build, release, compliance, JSON catalog, test, script, workflow, component, include, firmware, manifest, or artifact edits | `PRODUCT-POE-410-001` / `WEBFLASH-POE-410-001` / `RELEASE-POE-410-001` / `WF-IMPORT-POE-410-001` stay blocked behind `PACKAGE-POE-410-001` implementation and the five preconditions |
| CLEANUP-POE-410-001          | #527      | esphome-public  | Merged — docs-only tracker cleanup      | Converted the unresolved PR-number / `this PR` placeholders that PR #526 left in `UPCOMING_PR.md` so `PACKAGE-POE-410-001` consistently points to PR #526 (Current queue summary bullet, Recently uploaded evidence entry, active-queue entry #7 `Status` / `Notes` lines, and rejected-Path-B reference all now name PR #526 explicitly); added the matching `PACKAGE-POE-410-001 / #526` row to the Completed / merged PRs table | No functional, package, product, WebFlash, build, release, compliance, JSON catalog, test, script, workflow, component, include, firmware, manifest, audit-document, or artifact files; only `UPCOMING_PR.md` was touched | Prepared the tracker for `PRODUCT-POE-410-001` / PR #528; no queue-ordering effect on `PRODUCT-POE-410-001` |
| PRODUCT-POE-410-001          | #528      | esphome-public  | Merged — docs-only investigation pass   | Recorded `PRODUCT-POE-410-001` Path A deferral; confirmed `PACKAGE-POE-410-001` implementation slice / BOM cross-check / `S360-410 schematic_status: verified` JSON PR / HW-002 OQ#6 / `S360-100-BENCH-001` J2-harness identity closure / package-header reconciliation / Release-One PoE caveat closure / product-onboarding approval / product-catalog readiness approval preconditions remain open; no S360-410-explicit / `POE`-410-subject WebFlash-shippable product YAML exists under `products/` or `products/webflash/`; the three shipping PoE entries in `config/product-catalog.json` carry `hardware.poe: "S360-410"` as a catalog mapping field only (Release-One identity); kept Release-One / LED preview / FanTRIAC blocked-reference / six `legacy-compatible` `*-poe` Core variants byte-identical | No package, product, WebFlash, build, release, compliance, JSON catalog, test, script, workflow, component, include, firmware, manifest, or artifact edits; no `schematic_status` / `schematic_file` promotion; no COMPLIANCE-001 movement; no PoE-410-explicit entry added; no `webflash_build_matrix: true` flip; no new `artifact_name`; no `lifecycle_statuses` / `canonical_modules` / `canonical_power` / `forbidden_tokens` / `release_one_required_configs` / kit / `REQUIRED_CONFIGS` change; no Release-One caveat closure | `PRODUCT-POE-410-001` stays blocked on the eight preconditions; `WEBFLASH-POE-410-001` / `RELEASE-POE-410-001` / `WF-IMPORT-POE-410-001` (cross-repo) stay blocked behind it; `WEBFLASH-POE-410-001` becomes next active queue item |
| CLEANUP-POE-410-002          | #529      | esphome-public  | Merged — docs-only tracker cleanup      | Converted the unresolved `PR #XXX` / `this PR` placeholders that PR #528 left in `UPCOMING_PR.md` so `PRODUCT-POE-410-001` consistently points to PR #528 (Current queue summary bullet, `CLEANUP-POE-410-001` / `PRODUCT-POE-410-001` rows in the Completed / merged PRs table, and the Recently uploaded evidence entry all now name PR #528 explicitly); removed the `PRODUCT-POE-410-001` active-queue entry (the investigation pass has merged, so the row no longer belongs in the active queue); promoted `WEBFLASH-POE-410-001` to active queue item #7 and renumbered subsequent entries | No functional, package, product, WebFlash, build, release, compliance, JSON catalog, test, script, workflow, component, include, firmware, manifest, audit-document, or artifact files; only `UPCOMING_PR.md` was touched | Prepared the tracker for `WEBFLASH-POE-410-001` / PR #530; no queue-ordering effect on `WEBFLASH-POE-410-001` |
| WEBFLASH-POE-410-001         | #530      | esphome-public  | Merged — docs-only investigation pass   | Recorded `WEBFLASH-POE-410-001` Path A deferral; confirmed `PRODUCT-POE-410-001` implementation slice / `PACKAGE-POE-410-001` implementation slice / BOM cross-check / `S360-410 schematic_status: verified` JSON PR / HW-002 OQ#6 / `S360-100-BENCH-001` J2-harness identity closure / Release-One PoE caveat closure / product-onboarding approval / release-build readiness gates preconditions remain open; carried forward the ninth observation that `WEBFLASH-POE-410-001` may not be required at all if `PRODUCT-POE-410-001` ultimately closes via the default no-new-entry / caveat-closure-only path (queue stays blocked / deferred until that decision is made later); no S360-410 WebFlash wrapper exists under `products/webflash/`; no S360-410-explicit build exists in `config/webflash-builds.json`; `config/webflash-compatibility.json` reserves `POE` in `canonical_power` consumed by both committed builds (POE reservation does **not** imply S360-410-subject WebFlash exposure); kept Release-One / LED preview / FanTRIAC blocked-reference / six `legacy-compatible` `*-poe` Core variants byte-identical | No package, product, WebFlash, build, release, compliance, JSON catalog, test, script, workflow, component, include, firmware, manifest, or artifact edits; no `schematic_status` / `schematic_file` promotion; no COMPLIANCE-001 movement; no PoE-410-explicit entry added; no `webflash_build_matrix: true` flip; no new `artifact_name`; no `webflash_wrapper` added; no `config_string` added; no `lifecycle_statuses` / `canonical_modules` / `canonical_power` / `forbidden_tokens` / `release_one_required_configs` / kit / `REQUIRED_CONFIGS` change; no Release-One caveat closure | `WEBFLASH-POE-410-001` stays blocked on the eight blocker preconditions (with the ninth observation carried forward); `RELEASE-POE-410-001` / `WF-IMPORT-POE-410-001` (cross-repo) stay blocked behind it |
| CLEANUP-POE-410-003          | #531      | esphome-public  | Merged — docs-only tracker cleanup      | Converted the unresolved `PR #XXX` / `this PR` placeholders that PR #530 left in `UPCOMING_PR.md` so `WEBFLASH-POE-410-001` consistently points to PR #530 (Current queue summary bullet, `CLEANUP-POE-410-002` Follow-up impact column, `WEBFLASH-POE-410-001` row in the Completed / merged PRs table, and the Recently uploaded evidence entry all now name PR #530 explicitly); removed the `WEBFLASH-POE-410-001` active-queue entry (the investigation pass has merged, so the row no longer belongs in the active queue) and renumbered subsequent entries so `RELEASE-POE-410-001` becomes active queue item #7 | No functional, package, product, WebFlash, build, release, compliance, JSON catalog, test, script, workflow, component, include, firmware, manifest, audit-document, or artifact files; only `UPCOMING_PR.md` was touched | Prepared the tracker for `RELEASE-POE-410-001` / PR #532; no queue-ordering effect on `RELEASE-POE-410-001` |
| RELEASE-POE-410-001          | #532      | esphome-public  | Merged — docs-only investigation pass   | Recorded `RELEASE-POE-410-001` Path A deferral; confirmed `WEBFLASH-POE-410-001` implementation slice / `PRODUCT-POE-410-001` implementation slice / `PACKAGE-POE-410-001` implementation slice / repo-committed BOM evidence (the uploaded BOM appears to support the schematic-shown discrete PoE topology — `LAN_CON1 RJP-003TC1(LPJ4112CNL)` magnetics / RJ45, `U1 TPS2378DDAR(HSOIC-8)` PoE PD controller, `U2 TX4138(ESOIC-8)` buck, `DCDC1 F0505S-2WR2(SIP-7)` isolated DC/DC — but BOM ingest is the responsibility of a separate `HW-BOM-ASSETS-001` follow-up, not PR #532) / `S360-410 schematic_status: verified` JSON PR / HW-002 OQ#6 / `S360-100-BENCH-001` J2-harness identity closure / Release-One PoE caveat closure / product-onboarding approval / eight release-time sub-gates preconditions remain open; carried forward the observation that `RELEASE-POE-410-001` may not be required at all if `PRODUCT-POE-410-001` / `WEBFLASH-POE-410-001` ultimately close via the default no-new-entry / caveat-closure-only path (queue stays blocked / deferred until that decision is made later); no PoE-410-explicit release artifact exists of any kind (no `firmware/` directory, no `firmware/configurations/`, no `firmware/sources.json`, no top-level `manifest.json`, no `firmware-*.json`, no PoE-410-explicit GitHub Release tag, no PoE-410-explicit `.bin`, no PoE-410-explicit SHA256 / MD5 checksum files, no PoE-410-explicit build-info `manifest.json`, no PoE-410-explicit proof row in `docs/webflash-release-proof.md`); kept Release-One / LED preview / FanTRIAC blocked-reference / six `legacy-compatible` `*-poe` Core variants byte-identical; kept `.github/workflows/firmware-build-release.yml` byte-identical (workflow-frozen) | No package, product, WebFlash, build, release, compliance, JSON catalog, test, script, workflow, component, include, firmware, manifest, or artifact edits; no `schematic_status` / `schematic_file` promotion; no COMPLIANCE-001 movement; no PoE-410-explicit entry added; no `webflash_build_matrix: true` flip; no new `artifact_name`; no `webflash_wrapper` added; no `config_string` added; no new GitHub Release / tag / checksum / build-info manifest / proof row created; no BOM ingest (deferred to a separate `HW-BOM-ASSETS-001` follow-up); no `lifecycle_statuses` / `canonical_modules` / `canonical_power` / `forbidden_tokens` / `release_one_required_configs` / kit / `REQUIRED_CONFIGS` change; no Release-One caveat closure | `RELEASE-POE-410-001` stays blocked on the eight blocker preconditions (with the no-op observation carried forward); `WF-IMPORT-POE-410-001` (cross-repo) stays blocked behind it |
| HW-BOM-ASSETS-001            | #533      | esphome-public  | Merged — partial record-only BOM evidence ingest | S360-200/S360-210 curated BOM evidence indexes; S360-100 byte-identical re-upload confirmation; retained-but-not-committed BOM policy preserved. | No .xlsx committed; no package/product/config/WebFlash/release/test/workflow/firmware changes; no schematic_status or schematic_file changes. | HW-BOM-ASSETS follow-up still owed for S360-211, S360-300, S360-310, S360-311, S360-312, S360-320, S360-400, S360-410; high-value blockers for S360-400/S360-410/PWM/DAC/TRIAC remain until those BOMs are ingested. |
| PACKAGE-POWER-400-001        | #537      | esphome-public  | Merged — Path B / limited implementation package-header cleanup | Comment-only header cleanup against [`packages/hardware/power_240v.yaml`](packages/hardware/power_240v.yaml) lines 1–42: removed disproved `HLK-PM01 or similar` AC/DC part hint; named BOM-confirmed `PS1 = HLK-5M05 (HI-LINK)` part identity; named BOM-confirmed populated mains-side protection (`F1 A250-1200` polyfuse, `RV1 10D391K` MOV, `C1 470nF` X-cap) and connectors (`J1` WAGO 2601-3103 1×3, `J2` JST SH `SM02B-SRSS-TB(LF)(SN)` 1×2); reclassified input / output / isolation / protection ratings under explicit "Vendor-datasheet typicals (NOT BOM-confirmed and NOT compliance evidence)" heading; removed misleading `1A recommended` AC-input fusing line that conflicted with on-board `F1 A250-1200` polyfuse class; added explicit COMPLIANCE-001 OPEN reminder and explicit no-CE / UKCA / FCC / UL / LVD / EMC / RoHS / IEC claim statement. Runtime YAML blocks (`substitutions: power_source: "240v_ac"`, `globals: power_source_type`, the four template diagnostic sensors `Supply Voltage` / `Power Source` / `Power Configuration` / `AC Power Connected`, `logger` block) preserved **byte-identical** from line 44 onward. Doc / tracker updates: `docs/hardware/s360-400-r4-power.md` new audit-log row + new `### 2026-05-20 — PACKAGE-POWER-400-001 package-header cleanup` subsection + §Existing package abstraction / §Part identity reconciliation / §Package YAML status refreshed; `docs/hardware/package-readiness-matrix.md` §`power_240v.yaml` / S360-400 Path B addendum; `docs/hardware/firmware-package-mapping-audit.md` §`power_240v.yaml` AC/DC part-identity disagreement (S360-400) Path B paragraph; `docs/product-readiness-matrix.md` §PWR-240V / S360-400 Path B note; `docs/webflash-exposure-readiness-matrix.md` §Power / S360-400 WebFlash posture Path B note; `docs/release-artifact-readiness-matrix.md` §Power / S360-400 release posture Path B note; `docs/cleanup-audit.md` §`PACKAGE-POWER-400-001 update (2026-05-20 — Path B package-header cleanup)` new section; `UPCOMING_PR.md` Current queue summary bullet + Completed / merged PRs row added. | No `config/**` edit (`config/hardware-catalog.json` `S360-400` row at lines 102–110 byte-identical; `description: "Mains to 5V using HLK-5M05."` already BOM-consistent; `schematic_status: cataloged_unverified` unchanged; no `schematic_file`); no `products/**` or `products/webflash/**` edit (four `legacy-compatible` `*-pwr` Core variants stay `legacy-compatible` / `webflash_build_matrix: false`); no `tests/**` edit (`tests/test_hardware_catalog.py:53` `EXPECTED_STILL_UNVERIFIED_SKUS = frozenset({"S360-320", "S360-400"})` unchanged); no `scripts/**`, `.github/workflows/**`, `components/**`, `include/**`, `firmware/**`, `manifest.json`, or `firmware/sources.json` edit; no `webflash_build_matrix` flip; no `artifact_name` / `webflash_wrapper` / `config_string`; no `release_one_required_configs` / `lifecycle_statuses` / `canonical_modules` / `canonical_power` / `forbidden_tokens` / `REQUIRED_CONFIGS` / kit change; no COMPLIANCE-001 movement (last re-check PR #506; status still OPEN); no `schematic_status` / `schematic_file` promotion; no schematic-PDF correction (the `PS1 = HLK-10M05` value-field discrepancy stays recorded but is not corrected; correction owed to a separate later HW-ASSETS-400 follow-up); no Release-One change (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`); no LED preview change (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`); no FanTRIAC change (`blocked` / `HW-005`); no Release-One PoE caveat closure (S360-410 PoE caveat unchanged); no `.xlsx` committed; no Git LFS introduced; `hardware-artifact-policy.md` unchanged; no CE / UKCA / FCC / UL / LVD / EMC / RoHS / IEC claim. | `PACKAGE-POWER-400-001`'s package-header cleanup component now landed under Path B; the residual coordinated `PACKAGE-POWER-400-001` work (the `S360-400` `schematic_status: verified` JSON-only PR, additionally gated on the schematic-side correction of the committed PDF's `PS1 = HLK-10M05` value-field string) plus COMPLIANCE-001 `S360-400` slice closure plus silkscreen / PCB / creepage / clearance / bench / thermal / EMI evidence remain owed. `PRODUCT-POWER-400-001` / `WEBFLASH-POWER-400-001` / `RELEASE-POWER-400-001` / `WF-IMPORT-POWER-400-001` stay blocked behind those preconditions; the row class in [`docs/hardware/package-readiness-matrix.md`](docs/hardware/package-readiness-matrix.md#power_240vyaml--s360-400) stays `schematic-evidence-pending` + `needs-package-reconciliation` + `timing/compliance-pending` (compliance-gated). |
| HW-BOM-ASSETS-002            | #535      | esphome-public  | Merged — partial record-only BOM evidence ingest | S360-400 curated BOM evidence index appended (BOM `PS1 = HLK-5M05` HI-LINK confirms catalog `description: "Mains to 5V using HLK-5M05."`; schematic `PS1 = HLK-10M05` reclassified as schematic-label discrepancy; package header `HLK-PM01 or similar` reclassified as disproved comment text). S360-410 curated BOM evidence index appended (schematic-shown discrete topology `U1 TPS2378DDAR` TI + `U2 TX4138` XDS + `DCDC1 F0505S-2WR2` EVISUN + `LAN_CON1 LPJ4112CNL` Link-PP confirmed by BOM; package header `Ag9712M, Silvertel Ag9700, or similar` disproved by BOM; schematic-annotated `AM1D-0505S-NZ` recorded as schematic-annotation-only alternate not present in the BOM). S360-410 PDF re-upload byte-identical to committed schematic; no re-commit. Retained-but-not-committed BOM policy preserved (no `.xlsx` added to git; no `docs/hardware/bom/` directory; no Git LFS; policy doc unchanged). Audit-log + Part identity addendums added to `s360-400-r4-power.md` and `s360-410-r4-poe.md`; package-readiness-matrix and firmware-package-mapping-audit addendums added; board-readiness-matrix S360-400 / S360-410 row notes refreshed; cleanup-audit §HW-BOM-ASSETS-002 update section added. | No .xlsx committed; no package YAML edits (`power_240v.yaml` and `power_poe.yaml` byte-identical to PR #515 / PR #520 and PR #517 / PR #526 respectively; comment-only cleanups still deferred to `PACKAGE-POWER-400-001` and `PACKAGE-POE-410-001`); no product YAML / WebFlash wrapper / `config/**` / `tests/**` / `scripts/**` / `.github/workflows/**` / `components/**` / `include/**` / `firmware/**` / `manifest.json` / `firmware/sources.json` edit; no `schematic_status` / `schematic_file` change; no `webflash_build_matrix` flip; no `artifact_name` / `webflash_wrapper` / `config_string` added; no `release_one_required_configs` / `lifecycle_statuses` / `canonical_modules` / `canonical_power` / `forbidden_tokens` / `REQUIRED_CONFIGS` / kit change; no COMPLIANCE-001 movement (PoE is SELV); no Release-One / LED preview / FanTRIAC identity change; no Release-One PoE caveat closure (preserved verbatim); no schematic-PDF correction for the S360-400 `PS1` value-field discrepancy (committed PDF byte-identical); no schematic-PDF re-commit for S360-410 (upload byte-identical to committed file); no `hardware-artifact-policy.md` edit. | The `BOM cross-check missing` precondition recorded under `PACKAGE-POWER-400-001` / `PRODUCT-POWER-400-001` / `WEBFLASH-POWER-400-001` / `RELEASE-POWER-400-001` and under `PACKAGE-POE-410-001` / `PRODUCT-POE-410-001` / `WEBFLASH-POE-410-001` / `RELEASE-POE-410-001` is now **resolved at the part-identity layer**. Each downstream slice stays blocked on its other recorded preconditions (the respective `schematic_status: verified` JSON PR; COMPLIANCE-001 for S360-400 — PoE-410 is SELV and not in scope; silkscreen / PCB / creepage / clearance / bench / thermal / EMI / PoE-link-up / isolation evidence; HW-002 OQ#6 / `S360-100-BENCH-001` J2-harness closure for S360-410; the package-header comment cleanups themselves; the schematic-label correction PR for the S360-400 `PS1` value field; the Release-One PoE caveat closure for S360-410; product-onboarding / UX-class / release-time sub-gates where applicable). `HW-BOM-ASSETS` follow-up still owed for the six remaining BOMs: `S360-211`, `S360-300`, `S360-310`, `S360-311`, `S360-312` (Fan_GP8403), and `S360-320`. |
| PACKAGE-POE-410-001          | #538      | esphome-public  | Merged — Path B / limited implementation package-header cleanup | Comment-only header cleanup against [`packages/hardware/power_poe.yaml`](packages/hardware/power_poe.yaml) lines 1–58: removed the disproved `Ag9712M, Silvertel Ag9700, or similar` whole-module PoE hint; named the BOM-confirmed S360-410-R4 discrete PoE topology (`LAN_CON1 LPJ4112CNL` (RJP-003TC1-style) integrated RJ45 + magnetics; `U1 TPS2378DDAR` HSOIC-8 PoE PD controller; `U2 TX4138` ESOIC-8 buck; `DCDC1 F0505S-2WR2` SIP-7 isolated 5V/5V DC/DC; `D1 SMAJ58A` TVS; `D2 SS510` Schottky catch diode; `D3` Green status LED; `L1 33uH` buck inductor; `R1..R9`, `C1..C8`, `J3` `+5VP` / `GND` output header); explicitly reclassified `AM1D-0505S-NZ` as a schematic-annotation-only alternate **not** the BOM-populated part; reclassified IEEE 802.3af / Class 0 / input / output / protection ratings under explicit "Vendor-datasheet typicals (NOT BOM-confirmed and NOT compliance evidence)" heading; added an explicit "logical / diagnostic only — no GPIO / I2C / UART / SPI / DAC runtime binding" statement plus an explicit "no release, WebFlash, product-catalog, or schematic-status claim" statement plus an explicit no-IEEE-802.3af / 802.3at / isolation / Hi-pot / earth-continuity / leakage / thermal / EMI / EMC claim statement. Runtime YAML blocks (`substitutions: power_source: "poe"`, `globals: power_source_type`, the diagnostic `sensor` / `text_sensor` / `binary_sensor` / `logger` blocks, and the `esphome: on_boot:` log automation) preserved **byte-identical** from `substitutions:` onward (SHA256 of the `substitutions:`-onward block unchanged before and after this PR). `UPCOMING_PR.md` Current queue summary bullet + Completed / merged PRs row + active-queue entry #7 precondition refresh added. | No `config/**` edit (`config/hardware-catalog.json` `S360-410` row byte-identical; `schematic_status: cataloged_unverified` unchanged; no `schematic_file`); no `products/**` or `products/webflash/**` edit (six `legacy-compatible` `*-poe` Core variants stay `legacy-compatible` / `webflash_build_matrix: false`); no `tests/**`, `scripts/**`, `.github/workflows/**`, `components/**`, `include/**`, `firmware/**`, `manifest.json`, `firmware/sources.json`, `docs/compliance/**`, `config/hardware-catalog.json`, `config/product-catalog.json`, `config/webflash-builds.json`, or `config/webflash-compatibility.json` edit; no `webflash_build_matrix` flip; no `artifact_name` / `webflash_wrapper` / `config_string`; no `release_one_required_configs` / `lifecycle_statuses` / `canonical_modules` / `canonical_power` / `forbidden_tokens` / `REQUIRED_CONFIGS` / kit change; no COMPLIANCE-001 movement (PoE is SELV; `S360-410` is **not** in scope for COMPLIANCE-001); no `schematic_status` / `schematic_file` promotion; no Release-One PoE `"schematic verification pending"` caveat closure (preserved verbatim); no Release-One change (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`); no LED preview change (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`); no FanTRIAC change (`blocked` / `HW-005`); no `.xlsx` committed; no Git LFS introduced; `hardware-artifact-policy.md` unchanged; no IEEE 802.3af / 802.3at / isolation / Hi-pot / earth-continuity / leakage / thermal / EMI / EMC / CE / UKCA / FCC / UL / LVD / RoHS / IEC claim; no release artifact built or attached. | `PACKAGE-POE-410-001`'s package-header cleanup component now landed under Path B; the residual coordinated `PACKAGE-POE-410-001` work (the `S360-410` `schematic_status: verified` JSON-only PR, HW-002 OQ#6 / `S360-100-BENCH-001` J2-harness identity closure, and the Release-One PoE caveat-closure PR) plus silkscreen / PCB / creepage / clearance / bench / thermal / EMI / PoE-link-up / isolation evidence remain owed. `PRODUCT-POE-410-001` / `WEBFLASH-POE-410-001` / `RELEASE-POE-410-001` / `WF-IMPORT-POE-410-001` (cross-repo) stay blocked behind those preconditions. |
| FW-MATRIX-001                | #539      | esphome-public  | Merged — generated readiness matrix             | Added `scripts/generate_firmware_matrix.py` (enumerator + classifier with a `--check` freshness mode for CI), `config/firmware-combination-matrix.json` (168 valid WebFlash-style config-string combinations enumerated from `config/webflash-compatibility.json` and classified against `config/product-catalog.json` / `config/webflash-builds.json`), `tests/test_firmware_combination_matrix.py` (24 stdlib-unittest cases pinning grammar, status classification, on-disk freshness), and `docs/firmware-combination-matrix.md` (scope, gating rules, per-row schema, status definitions, non-goals); grammar handled per `docs/webflash-contract.md` §5 (mounting + power + optional AirIQ / VentIQ + optional fan driver + optional RoomIQ + optional LED; AirIQ/VentIQ mutual exclusion and FanDAC/AirIQ conflict enforced at enumeration time; forbidden legacy tokens and the generic "Fan" token never emitted) | No firmware build, no WebFlash build exposure, no product YAML, no WebFlash wrapper, no release artifact, no `webflash_build_matrix` flip, no `artifact_name` / `webflash_wrapper` / `config_string` added, no `config/webflash-builds.json` / `config/product-catalog.json` / `config/hardware-catalog.json` / `config/webflash-compatibility.json` edit, no `release_one_required_configs` / `lifecycle_statuses` / `canonical_modules` / `canonical_power` / `forbidden_tokens` / `REQUIRED_CONFIGS` / kit change, no `schematic_status` / `schematic_file` promotion, no COMPLIANCE-001 movement, no Release-One / LED preview / FanTRIAC identity change, no LED stable promotion, no `RELEASE-007` unblock | The 168-row matrix is now the planning foundation for downstream product / build / WebFlash / release work in this repo; FW-MATRIX-002 became the next slice (build-gap report grouping the matrix into priority lanes) |
| FW-MATRIX-002                | #540      | esphome-public  | Merged — generated build-gap report             | Added `scripts/report_firmware_build_gaps.py` (reads `config/firmware-combination-matrix.json`, applies ordered lane predicates, writes the Markdown report; `--check` mode fails if the on-disk report is stale relative to the matrix or to the lane predicates), `docs/firmware-build-gap-report.md` (groups all 168 valid combinations from FW-MATRIX-001 into practical implementation lanes so future PRs can pick build / package / product work in priority order), `tests/test_firmware_build_gap_report.py` (lane assignment / ordering / on-disk freshness coverage), and a see-also link in `docs/firmware-combination-matrix.md` pointing at the gap report | No firmware build, no WebFlash build exposure, no product YAML, no WebFlash wrapper, no release artifact, no `webflash_build_matrix` flip, no `artifact_name` / `webflash_wrapper` / `config_string` added, no `config/webflash-builds.json` / `config/product-catalog.json` / `config/hardware-catalog.json` / `config/webflash-compatibility.json` edit, no `release_one_required_configs` / `lifecycle_statuses` / `canonical_modules` / `canonical_power` / `forbidden_tokens` / `REQUIRED_CONFIGS` / kit change, no `schematic_status` / `schematic_file` promotion, no COMPLIANCE-001 movement, no Release-One / LED preview / FanTRIAC identity change, no LED stable promotion, no `RELEASE-007` unblock | The build-gap report is now the priority-lane lens for picking the next firmware / build / product / WebFlash / release slices; KIT-MATRIX-001 then landed as the productized kit-intent planning layer above the matrix and the gap report (see the KIT-MATRIX-001 row below) |
| KIT-MATRIX-001               | #542      | esphome-public  | Merged — productized kit-intent planning matrix | Added the source-of-truth planning matrix at `config/kit-intent-matrix.json` (six initial kit intent rows: `S360-KIT-BATH-POE` / `S360-KIT-BATH-POE-LED` / `S360-KIT-BATH-RELAY` / `S360-KIT-BATH-TRIAC` / `S360-KIT-DUCT-PWM` / `S360-KIT-DUCT-0-10V`), `docs/kit-intent-matrix.md` (kit-SKU vs module-SKU vs firmware-config-string identifier separation, productization rules, wizard usage, hard guardrails), and `tests/test_kit_intent_matrix.py` (21 stdlib-unittest cases pinning kit-id uniqueness, default-config-string presence in the firmware matrix, `S360-KIT-BATH-POE` stable-ready mapping, `S360-KIT-BATH-POE-LED` preview blockers including `S360-300-BENCH-001` / `WF-HW-TEST-001` / `WF-HW-TEST-003`, FanTRIAC blockers including `HW-005` / `COMPLIANCE-001`, PWM and FanDAC kits classified as duct-fan futures rather than default bathroom stable kits, and the guardrails that no kit with `webflash_exposure_allowed_now=true` points to a config string absent from `config/webflash-builds.json` and that no PWR-bearing kit claims WebFlash exposure or stable readiness) | No product YAML, no WebFlash wrapper, no firmware build, no release artifact, no `webflash_build_matrix` flip, no `artifact_name` / `webflash_wrapper` / `config_string` added, no `config/webflash-builds.json` / `config/product-catalog.json` / `config/hardware-catalog.json` / `config/webflash-compatibility.json` / `config/firmware-combination-matrix.json` edit, no `release_one_required_configs` / `lifecycle_statuses` / `canonical_modules` / `canonical_power` / `forbidden_tokens` / `REQUIRED_CONFIGS` change, no `schematic_status` / `schematic_file` promotion, no COMPLIANCE-001 movement, no Release-One / LED preview / FanTRIAC identity change, no LED stable promotion, no `RELEASE-007` unblock | The kit-intent matrix is now the productized planning layer above `config/firmware-combination-matrix.json` and `docs/firmware-build-gap-report.md`; WebFlash installability remains controlled exclusively by `config/webflash-builds.json` and the WebFlash manifest; next planning-step pointer is **WF-KIT-PRESETS-001 — WebFlash Stage 1 productized bundle presets** to surface the kit-intent rows as Stage 1 bundle presets in the WebFlash UI without itself flipping `webflash_build_matrix` or adding any new buildable config-string |
| FW-COMPILE-MATRIX-001        | #544      | esphome-public  | Merged — compile-only firmware validation lane | Added compile-only target metadata at `config/compile-only-targets.json`, metadata + compile validator at `scripts/validate_compile_targets.py`, structural / cross-reference / guardrail tests at `tests/test_compile_targets.py`, an optional clearly-named GitHub workflow at `.github/workflows/compile-only.yml`, and documentation at `docs/compile-only-firmware-validation.md`. The lane covers the two committed WebFlash product YAMLs (`products/webflash/ceiling-poe-ventiq-roomiq.yaml` and `products/webflash/ceiling-poe-ventiq-roomiq-led.yaml`); compile success is necessary but not sufficient for preview / stable readiness | No product YAML edit, no WebFlash wrapper edit, no manifest edit, no firmware artifact built or attached, no WebFlash exposure, no release artifact, no `webflash_build_matrix` flip, no `artifact_name` / `webflash_wrapper` / `config_string` added, no `config/webflash-builds.json` / `config/product-catalog.json` / `config/hardware-catalog.json` / `config/webflash-compatibility.json` / `config/firmware-combination-matrix.json` / `config/kit-intent-matrix.json` edit, no `release_one_required_configs` / `lifecycle_statuses` / `canonical_modules` / `canonical_power` / `forbidden_tokens` / `REQUIRED_CONFIGS` change, no `schematic_status` / `schematic_file` promotion, no COMPLIANCE-001 movement, no Release-One / LED preview / FanTRIAC identity change, no LED stable promotion, no `RELEASE-007` unblock, no hardware proof, no WebFlash import | Compile-only validation now exists for the two committed WebFlash product YAMLs; next-step pointer is to run the workflow's `workflow_dispatch` full compile mode against those YAMLs (if full compile fails, fix the compile issues; if full compile passes, future PRs may add reviewed compile-only targets or new product YAMLs to the lane, still without WebFlash exposure, release artifacts, stable promotion, or hardware proof) |
| CORE-ABSTRACT-BUS-001A       | #558      | esphome-public  | Merged — implementation slice (relay_pin → GPIO3 rebind + pin-pinning regression updates) | Applied the schematic-backed CORE-ABSTRACT-BUS-001A rebind recorded in [`docs/hardware/core-abstract-bus-reconciliation.md` §CORE-ABSTRACT-BUS-001A](docs/hardware/core-abstract-bus-reconciliation.md#core-abstract-bus-001a--relay_pin-slice). YAML edits: `relay_pin: GPIO10 → GPIO3` in `packages/hardware/sense360_core.yaml`; `relay_pin: GPIO4 → GPIO3` in `packages/hardware/sense360_core_ceiling.yaml`; `relay_pin: GPIO10 → GPIO3` in `packages/hardware/sense360_core_mapping.yaml`; `relay_pin: GPIO10 → GPIO3` in `packages/hardware/sense360_core_poe.yaml`; `relay_pin: GPIO4 → GPIO3` in `packages/hardware/sense360_core_wall.yaml`. Header / comment text in each of those five packages updated to record the schematic-correct Relay net per S360-100-R4 IO3 and to attribute the GPIO3-collision resolution to `CORE-ABSTRACT-BUS-001C` / PR #557. Extended `tests/test_core_abstract_bus.py` with a new `RELAY_REBIND_PACKAGES` constant (the five Core abstract packages above) plus `RelayPinRebindTests` (asserts `relay_pin: GPIO3` in every affected package and asserts the pre-001A `GPIO4` / `GPIO10` values are absent) plus `MainRelaySwitchBindingTests` (asserts the `id: main_relay` switch in `packages/hardware/sense360_core_ceiling.yaml` binds `pin: ${relay_pin}` so downstream products inherit the schematic-correct value through substitution). All existing 001C assertions (`pir_sensor_pin: GPIO15`, `comfort_ceiling_als_int_pin: GPIO47`, `expander_int_pin: GPIO17`, `sx1509_interrupt_pin: GPIO17`, RoomIQ Hi-Link UART on GPIO2 / GPIO1 at 256000 baud, RoomIQ SEN0609 UART on GPIO5 / GPIO4 at 115200 baud, `led_data_pin: GPIO38` in `led_ring_ceiling.yaml`, `fan_status_led_pin: GPIO46`, AirIQ-only `airiq_status_led_pin: GPIO7` and `airiq_led_pin: GPIO8`, no VentIQ Core-driven LED, `status_led_pin` absent, `expansion_gpio1..4` absent, no pin collision between `relay_pin` and the 001C-rebound nets) preserved. Added the §`### 2026-05-21 — CORE-ABSTRACT-BUS-001A implementation` audit-log entry to `docs/hardware/core-abstract-bus-reconciliation.md` and the §CORE-ABSTRACT-BUS-001A status update (2026-05-21) addendum to `docs/hardware/core-abstract-bus-001c-rebind-plan.md`. Added a new 2026-05-21 audit-log row to `docs/hardware/s360-310-r4-relay.md` recording CORE-ABSTRACT-BUS-001A landing at the substitution layer; refreshed §`### Parent Core packages that resolve ${relay_pin} differently` to show the pre-001A and post-001A values across the affected and voice-variant packages. `UPCOMING_PR.md` queue updated (active queue: 001A removed as completed-merged; subsequent entries renumbered; PRODUCT-RELAY-001 / WEBFLASH-RELAY-001 / RELEASE-RELAY-001 statuses refreshed to record the CORE-ABSTRACT-BUS-001A substitution-layer precondition as resolved while keeping the other PACKAGE-RELAY-001 / silkscreen / harness / `K1` BOM gates intact). | No `config/**` edit (`config/hardware-catalog.json`, `config/product-catalog.json`, `config/webflash-builds.json`, `config/webflash-compatibility.json`, `config/firmware-combination-matrix.json`, `config/kit-intent-matrix.json`, `config/compile-only-targets.json`, `config/compile-only-candidates.json` all byte-identical); no `products/**` or `products/webflash/**` edit; no `scripts/**`, `.github/workflows/**`, `components/**`, `include/**`, `firmware/**`, `manifest.json`, or `firmware/sources.json` edit; no `webflash_build_matrix` flip; no `artifact_name` / `webflash_wrapper` / `config_string` / `release_one_required_configs` / `lifecycle_statuses` / `canonical_modules` / `canonical_power` / `forbidden_tokens` / `REQUIRED_CONFIGS` / kit change; no `schematic_status` / `schematic_file` promotion; no COMPLIANCE-001 movement; no Release-One change (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`); no LED preview change (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`); no FanTRIAC change (`blocked` / `HW-005`); voice-variant Core packages (`sense360_core_voice_ceiling.yaml`, `sense360_core_voice_wall.yaml`) stay at pre-001A `relay_pin: GPIO4` (deliberately out of scope for the 001A slice); S360-300 LED ring data line stays GPIO38 in `packages/hardware/led_ring_ceiling.yaml`; I²C bus definitions unchanged (001B remains independent); RoomIQ UART blocks unchanged (preserved as 001C / PR #557 landed); `packages/expansions/fan_relay.yaml` not edited (its `fan_relay_pin: ${relay_pin}` substitution inherits the new value automatically); no compile-only target added; no firmware artifact built or attached; no release artifact / tag / checksum / build-info manifest / proof row; no WebFlash import readiness claim; no hardware release-readiness claim; no claim of Relay load / contact / `K1` rating proof; no claim that `PACKAGE-RELAY-001` / `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001` is advanced beyond the substitution layer; no PWM / FanDAC / FanTRIAC / LED stable promotion; no `CORE-ABSTRACT-BUS-001B` advancement. | `CORE-ABSTRACT-BUS-001A` is now completed-merged at the substitution layer. The schematic-correct `relay_pin: GPIO3` is bound in the five affected Core abstract packages. `CORE-ABSTRACT-BUS-001B` stays independent. `PACKAGE-RELAY-001` / `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001` stay blocked behind `PACKAGE-RELAY-001` implementation, which itself stays blocked behind: (1) `S360-100-BENCH-001` silkscreen evidence for Core `J4`; (2) the general ESP32-S3 `GPIO3` strap-pin boot-behaviour bench characterisation against a populated `S360-310-R4` + `S360-100-R4` pair (the 001C operator decisions #16 / #17 record the pair-scoped observed-OK, not a generic claim); (3) `K1` BOM identity, contact-current rating, harness identity per `docs/hardware/s360-310-r4-relay.md`. `PACKAGE-PWM-001` / `PACKAGE-DAC-001` stay blocked behind `001B` + their own evidence gates. |
| CORE-ABSTRACT-BUS-001C-IMPLEMENT-001 | #557      | esphome-public  | Merged — implementation slice (YAML rebind + pin-pinning regression scaffold) | Applied the schematic-backed CORE-ABSTRACT-BUS-001C rebind plan recorded in PR #554. YAML edits: `comfort_ceiling_als_int_pin: GPIO3 → GPIO47` in `packages/expansions/comfort_ceiling.yaml`; `sx1509_interrupt_pin: GPIO3 → GPIO17` in `packages/expansions/gpio_expander_sx1509.yaml`; `expander_int_pin: GPIO3 → GPIO17` in `packages/hardware/sense360_core_mapping.yaml`; `pir_sensor_pin: GPIO47 → GPIO15` in `packages/hardware/sense360_core_ceiling.yaml`. Retired the generic Core `status_led_pin` substitution from the seven affected Core abstract packages (`sense360_core.yaml`, `sense360_core_ceiling.yaml`, `sense360_core_mapping.yaml`, `sense360_core_poe.yaml`, `sense360_core_wall.yaml`, `sense360_core_voice_ceiling.yaml`, `sense360_core_voice_wall.yaml`); retired generic `expansion_gpio1..4` substitutions from the same packages; replaced the single `uart_bus` block with two named RoomIQ UART buses (`roomiq_hi_link_uart` on tx_pin GPIO2 / rx_pin GPIO1 / baud_rate 256000, and `roomiq_sen0609_uart` on tx_pin GPIO5 / rx_pin GPIO4 / baud_rate 115200); introduced schematic-named `fan_status_led_pin: GPIO46` and the corresponding `status_led:` block in the affected Core abstract packages; introduced `roomiq_sen0609_output_pin: GPIO6` in `sense360_core_ceiling.yaml` and `sense360_core_mapping.yaml`. Updated downstream presence packages (`packages/expansions/presence_ceiling.yaml`, `packages/expansions/presence_wall.yaml`, `packages/expansions/presence_ld2450.yaml`) to bind `ld2450_uart_id: roomiq_hi_link_uart`. Updated `packages/hardware/sense360_core_voice.yaml` so the `voice_status_led_pin` default points at the new `fan_status_led_pin` instead of the retired `status_led_pin`. Added `tests/test_core_abstract_bus.py` as the pin-pinning regression scaffold (19 tests asserting `pir_sensor_pin: GPIO15`, `comfort_ceiling_als_int_pin: GPIO47`, `roomiq_sen0609_output_pin: GPIO6`, `expander_int_pin: GPIO17`, `sx1509_interrupt_pin: GPIO17`, the two RoomIQ UART block tx/rx/baud values, `status_led_pin` absence from every affected Core abstract package, `led_data_pin: GPIO38` preserved in `led_ring_ceiling.yaml`, `fan_status_led_pin: GPIO46`, `airiq_status_led_pin: GPIO7` and `airiq_led_pin: GPIO8` AirIQ-only classification, no VentIQ Core-driven LED substitution anywhere under `packages/`, `expansion_gpio1..4` absence from every affected Core abstract package, no pin collision between `relay_pin` / `comfort_ceiling_als_int_pin` / `expander_int_pin` / `sx1509_interrupt_pin`, and `relay_pin` unchanged in this PR — `relay_pin` remains at the pre-001A value in each affected Core abstract package). Added the §Implementation result (2026-05-21) subsection to `docs/hardware/core-abstract-bus-001c-rebind-plan.md` and the §`### 2026-05-21 — CORE-ABSTRACT-BUS-001C implementation` audit-log entry to `docs/hardware/core-abstract-bus-reconciliation.md`. `UPCOMING_PR.md` queue updated (active queue: 001C removed as completed-merged, 001A promoted to active-queue item #1 with `GPIO3`-collision precondition recorded as resolved by this PR, 001B stays independent at item #2). | No `config/**` edit (`config/hardware-catalog.json`, `config/product-catalog.json`, `config/webflash-builds.json`, `config/webflash-compatibility.json`, `config/firmware-combination-matrix.json`, `config/kit-intent-matrix.json`, `config/compile-only-targets.json` all byte-identical); no `products/**` or `products/webflash/**` edit; no `scripts/**`, `.github/workflows/**`, `components/**`, `include/**`, `firmware/**`, `manifest.json`, or `firmware/sources.json` edit; no `webflash_build_matrix` flip; no `artifact_name` / `webflash_wrapper` / `config_string` / `release_one_required_configs` / `lifecycle_statuses` / `canonical_modules` / `canonical_power` / `forbidden_tokens` / `REQUIRED_CONFIGS` / kit change; no `schematic_status` / `schematic_file` promotion; no COMPLIANCE-001 movement; no Release-One change (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`); no LED preview change (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`); no FanTRIAC change (`blocked` / `HW-005`); `relay_pin` not changed (still pre-001A values in each affected Core abstract package); S360-300 LED ring data line stays GPIO38 in `packages/hardware/led_ring_ceiling.yaml`; no compile-only target added; no firmware artifact built or attached; no release artifact / tag / checksum / build-info manifest / proof row; no WebFlash import readiness claim; no hardware release-readiness claim; no claim that `RELEASE-RELAY-001` / `RELEASE-PWM-001` / `RELEASE-DAC-001` are unblocked beyond the `GPIO3`-collision layer; no PWM / FanDAC / FanTRIAC / LED stable promotion. | `CORE-ABSTRACT-BUS-001C` is now completed-merged. `CORE-ABSTRACT-BUS-001A` is unblocked at the `GPIO3`-collision layer (ALS_INT moved to GPIO47, expander interrupt moved to GPIO17); the remaining 001A preconditions are `S360-100-BENCH-001` silkscreen evidence, the general ESP32-S3 `GPIO3` strap-pin boot-behaviour bench characterisation, and `K1` BOM / harness identity. `CORE-ABSTRACT-BUS-001B` stays independent. `PACKAGE-RELAY-001` / `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001` stay blocked behind `001A`. `PACKAGE-PWM-001` / `PACKAGE-DAC-001` stay blocked behind `001B` + their own evidence gates. |
| PACKAGE-RELAY-001-READINESS-REFRESH | #559      | esphome-public  | Merged — docs / evidence / readiness re-evaluation after CORE-ABSTRACT-BUS-001C / 001A | Re-evaluated the `PACKAGE-RELAY-001` blocker set against the post-`CORE-ABSTRACT-BUS-001C` (PR #557) and post-`CORE-ABSTRACT-BUS-001A` (PR #558) repo state. Added a new top-line readiness section §`PACKAGE-RELAY-001 readiness refresh after CORE-ABSTRACT-BUS-001C / 001A` to `docs/hardware/s360-310-r4-relay.md` containing a readiness table (blocker × previous state × current state after #557/#558 × evidence source × still blocks PACKAGE-RELAY-001? × what unblocks it) covering the eleven enumerated blockers (`GPIO3` collision; `relay_pin` substitution disagreement; `fan_relay.yaml` abstraction correctness; pin-pinning regression test for `relay_pin`; S360-100 Core `J4` silkscreen pin-1 orientation; S360-310 module-side `J2` silkscreen pin-1 orientation; S360-310 module-side `J1` silkscreen pin-1 orientation + NO / COM / NC mapping; S360-310 Relay connector / harness identity; `K1` BOM identity; `K1` contact-current rating; Relay load / contact proof; ESP32-S3 `GPIO3` strap-pin boot behaviour general characterisation; whether `fan_relay.yaml` needs behaviour / package cleanup beyond inheriting `${relay_pin}`). Recorded the substitution-layer blockers (the first four rows above plus the structural-correctness check on `fan_relay.yaml`) as **resolved at the Core abstract-bus substitution layer** by PR #557 + PR #558, and the hardware / evidence blockers (silkscreen / harness / `K1` BOM / contact rating / load-contact proof / general `GPIO3` strap-pin boot behaviour) as still owed. Added a new 2026-05-21 audit-log row to `docs/hardware/s360-310-r4-relay.md` §HW-PINMAP-310-FOLLOWUP audit log recording the readiness-refresh pass. Refreshed the `fan_relay.yaml` row in `docs/hardware/package-readiness-matrix.md` table to record the post-001A / 001C substitution-layer resolution while keeping the status `schematic-evidence-pending` + `needs-package-reconciliation`; refreshed the §`fan_relay.yaml` / S360-310 detail section with the post-001A / 001C state and a refreshed Follow-up owner chain pointing at this PR + the S360-310 bench-evidence-capture slice. Appended a 2026-05-21 update sub-bullet to the Release-One product YAML package stack §systemic Core-vs-schematic mismatch `relay_pin: GPIO4` finding in `docs/hardware/firmware-package-mapping-audit.md` recording the post-001A `relay_pin: GPIO3` state and pointing at the new readiness-refresh section. Recorded the conservative recommended next PR as an `S360-310` bench-evidence-capture slice (`HW-ASSETS-S360-310-BENCH-001` / `S360-310-BENCH-001` or sibling) committing operator-attributed silkscreen captures of module-side `J2` / module-side `J1` (with `NO` / `COM` / `NC` labels where present) / Core-side `J4`, the Core ↔ module harness inspection trace, the `K1` BOM identity, the coil-drive waveform capture, and the load-side continuity trace — **not** `PACKAGE-RELAY-001` implementation. Updated `UPCOMING_PR.md` Current queue summary, Completed / merged PRs (this row), active-queue PRODUCT-RELAY-001 / WEBFLASH-RELAY-001 / RELEASE-RELAY-001 blocker enumeration (precondition list refreshed to distinguish the resolved substitution-layer precondition from the still-open hardware-evidence blockers), and Recently uploaded evidence (new 2026-05-21 bullet added). | No `packages/**` edit (the `fan_relay.yaml` package is structurally correct post-001A and is not edited; the Core abstract packages stay at the 001A / 001C values); no `products/**` or `products/webflash/**` edit; no `config/**` edit (`config/hardware-catalog.json`, `config/product-catalog.json`, `config/webflash-builds.json`, `config/webflash-compatibility.json`, `config/firmware-combination-matrix.json`, `config/kit-intent-matrix.json`, `config/compile-only-targets.json`, `config/compile-only-candidates.json` all byte-identical); no `scripts/**`, `.github/workflows/**`, `components/**`, `include/**`, `firmware/**`, `manifest.json`, `firmware/sources.json`, `tests/**` edit (the `tests/test_core_abstract_bus.py` scaffold from 001C / 001A is preserved verbatim and not extended by this PR); no `webflash_build_matrix` flip; no `artifact_name` / `webflash_wrapper` / `config_string` / `release_one_required_configs` / `lifecycle_statuses` / `canonical_modules` / `canonical_power` / `forbidden_tokens` / `REQUIRED_CONFIGS` / kit change; no `schematic_status` / `schematic_file` promotion (`S360-310` row in `config/hardware-catalog.json` stays byte-identical: `schematic_status: cataloged_unverified`, no `schematic_file`); no COMPLIANCE-001 movement; no Release-One change (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`); no LED preview change (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`); no FanTRIAC change (`blocked` / `HW-005`); voice-variant Core packages stay at pre-001A `relay_pin: GPIO4` (out of scope); no compile-only target added; no firmware artifact built or attached; no release artifact / tag / checksum / build-info manifest / proof row; no WebFlash import readiness claim; no hardware release-readiness claim; **no claim of Relay load / contact / `K1` rating proof**; no claim that `PACKAGE-RELAY-001` / `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001` is implementation-ready; no `PACKAGE-RELAY-001` implementation; no Relay product YAML; no WebFlash wrapper; no compile-only target for FanRelay; no PWM / FanDAC / FanTRIAC / LED stable promotion; no `CORE-ABSTRACT-BUS-001B` advancement; no `HW-PINMAP-310-FOLLOWUP` closure (the audit status stays `partial — schematic evidence available; package reconciliation pending`); the operator-confirmed pair-scoped boot OK observation in `docs/hardware/core-abstract-bus-001c-rebind-plan.md` decisions #16 / #17 is **not** promoted to a generic claim about ESP32-S3 `GPIO3` strap-pin boot behaviour. | The substitution-layer blockers recorded under `PACKAGE-RELAY-001` are now **resolved** at the Core abstract-bus substitution layer by PR #557 + PR #558. The hardware-evidence blockers (S360-100 Core `J4` silkscreen; S360-310 module-side `J2` / `J1` silkscreen; `J1` `NO` / `COM` / `NC` mapping; Core ↔ module harness identity; `K1` BOM identity; `K1` contact-current rating; Relay load / contact proof; general ESP32-S3 `GPIO3` strap-pin boot characterisation) **stay open** and continue to block `PACKAGE-RELAY-001` implementation. `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001` stay blocked behind `PACKAGE-RELAY-001`. The recommended next active-queue item is an `S360-310` bench-evidence-capture slice (silkscreen / harness / `K1` BOM / load-contact proof; general `GPIO3` strap-pin boot characterisation), not `PACKAGE-RELAY-001` itself. `CORE-ABSTRACT-BUS-001B` stays independent of 001A / 001C ordering. `S360-100-BENCH-001`, `HW-PINMAP-311-FOLLOWUP`, `HW-PINMAP-312-FOLLOWUP`, and `HW-PINMAP-320-FOLLOWUP` are not closed by this readiness refresh. `COMPLIANCE-001` is not advanced. |
| S360-310-BENCH-EVIDENCE-001 | #561      | esphome-public  | Merged — docs / evidence population for Relay bench checklist | Populated the ten enumerated `PACKAGE-RELAY-001` hardware-evidence rows in `docs/hardware/s360-310-r4-relay.md` §`S360-310-BENCH-001 — Relay bench evidence` from operator-attested + BOM-backed + public-reference-backed sources supplied by operator `@wifispray` (Wifi Guy) on 2026-05-22. **Operator-attested** (against the populated `S360-100-R4` + `S360-310-R4` pair): Core-side `J4` pin order `+5V` / `Relay` / `GND`; module-side `J2` pin order `+5V` / `Relay` / `GND`; module-side `J1` mapping `NO` / `COM` / `NC`; 3-pin Core ↔ module harness straight-through with J4-1↔J2-1 / J4-2↔J2-2 / J4-3↔J2-3; expected controlled load type UK mains Manrose `MT100S`-class extractor fan (operator self-report "as per UK standards"); relay boot state de-energized across 10 boot cycles × 4 power paths (USB / PoE / 5 V PSU / 240 V supply) with firmware `Ceiling-POE-VentIQ-RoomIQ`; relay load / contact proof consistent with `NO` + `COM` wiring. **BOM-backed** (operator-uploaded `S360-310-R4_BOM.xlsx`, **not** committed to this repository): `K1` Songle Relay `SRD-05VDC-SL-C` (value `SRD-05VDC-SL-C-srd_relay`; footprint `greencharge-footprints:RELAY_SRD-05VDC-SL-C`; qty 1). **Public-reference-backed** (SRD-style 5 V relay datasheet): `K1` contact-current rating `10 A @ 250 VAC; 10 A @ 30 VDC`, SPDT — contact-rating evidence only, **not** board-level compliance / installation approval / mains-safety certification. **Pair-scoped sufficient for package implementation**: `GPIO3` strap-pin boot-behaviour row captured as `captured enough for PACKAGE-RELAY-001 implementation`, with explicit caveat that this is **not** a production-wide / multi-unit / oscilloscope-traced / compliance / release / safety-certification claim. Extended §`Status-language rules` with four new status values (`captured — operator-attested`, `captured — BOM-backed`, `captured — public-reference-backed`, `captured enough for PACKAGE-RELAY-001 implementation`); added §`What this record now unblocks` subsection with the verbatim "Implementation-ready at the PACKAGE-RELAY-001 evidence layer" caveat block; refreshed §`Status` and §`Summary verdict`; appended a 2026-05-22 row to §`HW-PINMAP-310-FOLLOWUP audit log`. Refreshed the `fan_relay.yaml` row in `docs/hardware/package-readiness-matrix.md` table to `package-evidence-captured` + `implementation-ready at PACKAGE-RELAY-001 evidence layer` with Allowed-action-now and Follow-up-owner chain refreshed; refreshed the §`fan_relay.yaml` / S360-310 detail section bullets in parallel; appended a 2026-05-22 update sub-paragraph to the PACKAGE-RELAY-001 investigation-outcome bullet. Appended a 2026-05-22 update sub-bullet to the Release-One package-stack `relay_pin` finding in `docs/hardware/firmware-package-mapping-audit.md`. Refreshed `UPCOMING_PR.md` Current queue summary (new bullet), Completed / merged PRs (this row), Active / upcoming queue (new `PACKAGE-RELAY-001` implementation-slice entry inserted ahead of `PRODUCT-RELAY-001`; downstream Relay-chain numbering refreshed; `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` blocker text refreshed), and Recently uploaded evidence (new 2026-05-22 bullet). | **No `packages/**` edit** (`fan_relay.yaml`, the five non-voice Core abstract packages at post-001A `relay_pin: GPIO3`, and the voice-variant Core packages at pre-001A `relay_pin: GPIO4` all stay byte-identical); **no `products/**` or `products/webflash/**` edit**; **no `config/**` edit** (`config/hardware-catalog.json`, `config/product-catalog.json`, `config/webflash-builds.json`, `config/webflash-compatibility.json`, `config/firmware-combination-matrix.json`, `config/kit-intent-matrix.json`, `config/compile-only-targets.json`, `config/compile-only-candidates.json` all byte-identical); **no `scripts/**`, `.github/workflows/**`, `components/**`, `include/**`, `firmware/**`, `manifest.json`, `firmware/sources.json`, `tests/**` edit** (the `tests/test_core_abstract_bus.py` scaffold from 001C / 001A is preserved verbatim); **no `webflash_build_matrix` flip**; **no `artifact_name` / `webflash_wrapper` / `config_string` / `release_one_required_configs` / `lifecycle_statuses` / `canonical_modules` / `canonical_power` / `forbidden_tokens` / `REQUIRED_CONFIGS` / kit change**; **no `schematic_status` / `schematic_file` promotion** (`S360-310` stays `cataloged_unverified`); **no COMPLIANCE-001 movement**; no Release-One change (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`); no LED preview change (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`); no FanTRIAC change (`blocked` / `HW-005`); no `HW-PINMAP-310-FOLLOWUP` top-line status promotion (stays `partial — schematic evidence available; package reconciliation pending`); no compile-only target added; no firmware artifact built or attached; no release artifact / tag / checksum / build-info manifest / proof row; **no WebFlash import-readiness claim**; **no hardware release-readiness claim**; **no `RELEASE-RELAY-001` unblock claim**; **no `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` / `WF-IMPORT-RELAY-001` advancement claim**; **no claim that `PACKAGE-RELAY-001` is product-ready, WebFlash-ready, release-ready, compliance-cleared, safe for arbitrary mains installation, or verified across production batches**; **no `PACKAGE-RELAY-001` implementation** (the implementation slice is owed to a separate PR); no Relay product YAML; no WebFlash wrapper; no compile-only target for FanRelay; no PWM / FanDAC / FanTRIAC / LED stable promotion; no `CORE-ABSTRACT-BUS-001B` advancement; **no closure of `S360-100-BENCH-001`** (the operator-attested Core-`J4` pin order is **not** silkscreen / manufacturing evidence and does **not** discharge that gate); **no board-level mains-safety / installation-approval / creepage / clearance / thermal / EMI certification claim**; **no production-wide / multi-unit / oscilloscope-traced general `GPIO3` strap-pin boot-behaviour characterisation claim**; **no photo / video / oscilloscope / continuity-meter artifacts attached**. The operator-uploaded `S360-310-R4_BOM.xlsx` is consumed for the `K1` BOM-backed row only and is **not** committed to this repository. | `PACKAGE-RELAY-001` is now **implementation-ready at the package-evidence layer only**. "Implementation-ready at the `PACKAGE-RELAY-001` evidence layer" does **not** mean product-ready, WebFlash-ready, release-ready, compliance-cleared, safe for arbitrary mains installation, or verified across production batches. The next Relay PR can be `PACKAGE-RELAY-001` implementation; `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001` stay blocked behind `PACKAGE-RELAY-001`. `S360-100-BENCH-001`, `HW-PINMAP-311-FOLLOWUP`, `HW-PINMAP-312-FOLLOWUP`, `HW-PINMAP-320-FOLLOWUP`, and `COMPLIANCE-001` are **not** closed by this evidence-population PR. `CORE-ABSTRACT-BUS-001B` stays independent. The production-wide / multi-unit / oscilloscope-traced general `GPIO3` strap-pin boot-behaviour characterisation is still owed for future production / compliance / safety work but is **not** a prerequisite for `PACKAGE-RELAY-001` implementation. |
| PACKAGE-RELAY-001            | (this PR) | esphome-public  | Merged — implementation slice (test + readiness reconciliation; no YAML rebind) | Reconciled the FanRelay package after the package-evidence layer closed under PR #557 (`CORE-ABSTRACT-BUS-001C`), PR #558 (`CORE-ABSTRACT-BUS-001A`), PR #559 (`PACKAGE-RELAY-001-READINESS-REFRESH`), PR #560 (`S360-310-BENCH-001` evidence-capture checklist), and PR #561 (`S360-310-BENCH-EVIDENCE-001` evidence population). **No YAML edit required** on `packages/expansions/fan_relay.yaml`: the package was already structurally correct (`fan_relay_pin: ${relay_pin}` line 27 inherits the parent Core abstract package binding; post-001A `${relay_pin}` resolves to the schematic-correct `GPIO3` per S360-100-R4 `IO3 = Relay`); the override-hook comment block (lines 22–25), the `switch.platform: gpio` declaration with `pin: ${fan_relay_pin}` (line 38), `restore_mode: RESTORE_DEFAULT_OFF`, the `fan_auto_mode` global (lines 50–53), and the `fan_emergency_stop` script (lines 58–65) are preserved verbatim. The reconciliation is the addition of `tests/test_fan_relay_package.py` (12 stdlib-unittest cases) pinning the FanRelay package abstraction against future regression: the package exists and parses as YAML; `fan_relay_pin` defaults to `${relay_pin}` and is not a hardcoded GPIO; the package does not hard-code `GPIO3` / `GPIO4` / `GPIO10` or any other GPIO on an active (non-comment) line; the `fan_relay_switch` switch block uses platform `gpio` and binds `pin: ${fan_relay_pin}`; the five non-voice Core abstract packages bind `relay_pin: GPIO3` (cross-check against `tests/test_core_abstract_bus.py` `RelayPinRebindTests`); the voice-variant Core packages stay at the pre-001A `relay_pin: GPIO4` (deliberately out of scope); no FanRelay product YAML exists under `products/`; no `FanRelay` token exists in `config/webflash-builds.json`. Docs refreshed: `docs/hardware/s360-310-r4-relay.md` §Package YAML status PACKAGE-RELAY-001 investigation-outcome bullet extended with a PACKAGE-RELAY-001 implementation-outcome paragraph; new 2026-05-22 audit-log row appended to §HW-PINMAP-310-FOLLOWUP audit log recording the implementation. `docs/hardware/package-readiness-matrix.md` `fan_relay.yaml` row + §`fan_relay.yaml` / S360-310 detail section refreshed to `package-implemented` + `reconciled-at-package-layer` with Allowed-action-now and Follow-up-owner chain refreshed. `docs/hardware/firmware-package-mapping-audit.md` Release-One package-stack `relay_pin` bullet appended with a PACKAGE-RELAY-001 implementation sub-paragraph. `UPCOMING_PR.md` Current queue summary (new bullet), Completed / merged PRs (this row), Active / upcoming queue (PACKAGE-RELAY-001 item #6 moved from "Evidence-ready" to "Merged"), and Recently uploaded evidence (new 2026-05-22 bullet) refreshed. | **No `packages/**` edit** (`fan_relay.yaml`, the five non-voice Core abstract packages at post-001A `relay_pin: GPIO3`, and the voice-variant Core packages at pre-001A `relay_pin: GPIO4` all stay byte-identical); **no `products/**` or `products/webflash/**` edit**; **no `config/**` edit** (`config/hardware-catalog.json`, `config/product-catalog.json`, `config/webflash-builds.json`, `config/webflash-compatibility.json`, `config/firmware-combination-matrix.json`, `config/kit-intent-matrix.json`, `config/compile-only-targets.json`, `config/compile-only-candidates.json` all byte-identical); **no `scripts/**`, `.github/workflows/**`, `components/**`, `include/**`, `firmware/**`, `manifest.json`, or `firmware/sources.json` edit**. Only one `tests/**` addition: `tests/test_fan_relay_package.py` (new file). The `tests/test_core_abstract_bus.py` scaffold from 001A / 001C is preserved verbatim; no other test is edited. **No `webflash_build_matrix` flip**; **no `artifact_name` / `webflash_wrapper` / `config_string` / `release_one_required_configs` / `lifecycle_statuses` / `canonical_modules` / `canonical_power` / `forbidden_tokens` / `REQUIRED_CONFIGS` / kit change**; **no `schematic_status` / `schematic_file` promotion** (`S360-310` stays `cataloged_unverified`); **no COMPLIANCE-001 movement**; no Release-One change (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`); no LED preview change (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`); no FanTRIAC change (`blocked` / `HW-005`); no `HW-PINMAP-310-FOLLOWUP` top-line status promotion (stays `partial — schematic evidence available; package reconciliation pending`); no compile-only target added; no firmware artifact built or attached; no release artifact / tag / checksum / build-info manifest / proof row; **no WebFlash import-readiness claim**; **no hardware release-readiness claim**; **no `RELEASE-RELAY-001` unblock claim**; **no `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` / `WF-IMPORT-RELAY-001` advancement claim**; **no claim that `PACKAGE-RELAY-001` is product-ready, WebFlash-ready, release-ready, compliance-cleared, safe for arbitrary mains installation, or verified across production batches**; no Relay product YAML; no WebFlash wrapper; no compile-only target for FanRelay; no PWM / FanDAC / FanTRIAC / LED stable promotion; no `CORE-ABSTRACT-BUS-001B` advancement; **no closure of `S360-100-BENCH-001`**; **no board-level mains-safety / installation-approval / creepage / clearance / thermal / EMI certification claim**; **no production-wide / multi-unit / oscilloscope-traced general `GPIO3` strap-pin boot-behaviour characterisation claim**. | `PACKAGE-RELAY-001` is now **implemented / reconciled at the package layer only**. "Implemented / reconciled at the `PACKAGE-RELAY-001` package layer" does **not** mean product-ready, WebFlash-ready, release-ready, compliance-cleared, safe for arbitrary mains installation, or verified across production batches. The next Relay PR is `PRODUCT-RELAY-001`, which stays separately gated on product-layer compliance / mains-safety / installation / production-wide characterisation evidence. `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001` stay blocked behind PACKAGE-RELAY-001 → PRODUCT-RELAY-001. `S360-100-BENCH-001`, `HW-PINMAP-311-FOLLOWUP`, `HW-PINMAP-312-FOLLOWUP`, `HW-PINMAP-320-FOLLOWUP`, and `COMPLIANCE-001` are **not** closed by this PR. `CORE-ABSTRACT-BUS-001B` stays independent of 001A / 001C ordering. |

## Active / upcoming esphome-public queue

Listed in working priority order. WebFlash-owned import PRs are kept out of
this table; see **Cross-repo dependencies**. The only `WF-`-prefixed entry
that appears below is **WF-TRIAC-001**, which is the in-repo
wrapper/catalog/build slice (not a WebFlash-runtime import).

1. **CORE-ABSTRACT-BUS-001B — Shared-I²C-bus consolidation**
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

2. **PRODUCT-POWER-400-001**
   - Status: **Investigated 2026-05-19; merged as PR #521;
     confirmed deferred (Path A docs-only); six preconditions
     still open** (BOM cross-check precondition resolved at the
     AC/DC part-identity layer by `HW-BOM-ASSETS-002` / PR #535;
     `PACKAGE-POWER-400-001` package-header cleanup landed under
     Path B / PR #537 on 2026-05-20; see Recently uploaded
     evidence). Blocked on the residual coordinated
     `PACKAGE-POWER-400-001` work (PR #537 landed the
     header-reconciliation component against
     [`packages/hardware/power_240v.yaml`](packages/hardware/power_240v.yaml);
     the catalog `description: "Mains to 5V using HLK-5M05."` in
     [`config/hardware-catalog.json`](config/hardware-catalog.json)
     line 109 is already BOM-consistent and unchanged; the
     `S360-400` `schematic_status: verified` JSON-only PR is
     still owed and is additionally gated on the schematic-label
     correction PR that fixes the committed PDF's
     `PS1 = HLK-10M05` value-field string against the
     BOM-confirmed `HLK-5M05`),
     `COMPLIANCE-001` `S360-400` slice, and product-onboarding
     approval per
     [`docs/product-onboarding.md`](docs/product-onboarding.md).
   - Purpose: Add the first `S360-400` / `PWR`-bearing
     WebFlash-shippable canonical product YAML under
     [`products/`](products/) (candidate shape
     `Ceiling-PWR-{AIR}-{ROOM}`) plus the matching entry in
     [`config/product-catalog.json`](config/product-catalog.json),
     decide the legacy-compatible `*-pwr` Core variant
     relationship (retain / migrate / coexist) for
     [`products/sense360-core-c-pwr.yaml`](products/sense360-core-c-pwr.yaml),
     [`products/sense360-core-w-pwr.yaml`](products/sense360-core-w-pwr.yaml),
     [`products/sense360-core-v-c-pwr.yaml`](products/sense360-core-v-c-pwr.yaml),
     and
     [`products/sense360-core-v-w-pwr.yaml`](products/sense360-core-v-w-pwr.yaml),
     and route the slice through the
     [`docs/product-onboarding.md`](docs/product-onboarding.md)
     safe sequence. **Does not** add a WebFlash wrapper, catalog
     `webflash_build_matrix: true` flip, build-matrix entry, or
     release artifact (those are additionally gated by
     `WEBFLASH-POWER-400-001` and `COMPLIANCE-001` `S360-400`
     slice closure).
   - Notes: 2026-05-19 investigation pass (PR #521) is **docs-only
     deferral**. Re-verified against the live files: **no
     S360-400-explicit / `PWR`-bearing WebFlash-shippable product
     YAML exists** under [`products/`](products/) or
     [`products/webflash/`](products/webflash/).

3. **WEBFLASH-POWER-400-001**
   - Status: **Investigated 2026-05-19; merged as PR #522;
     confirmed deferred (Path A docs-only); five preconditions
     still open**. Blocked on `PRODUCT-POWER-400-001`
     implementation (only the docs-only investigation merged as
     PR #521; the canonical S360-400 / `PWR`-bearing product
     YAML, the matching `config/product-catalog.json` entry, and
     the legacy-compatible `*-pwr` Core variant relationship
     decision all remain owed); `PACKAGE-POWER-400-001`
     package-header cleanup landed under Path B / PR #537 on
     2026-05-20 — runtime YAML behavior unchanged; the residual
     coordinated `PACKAGE-POWER-400-001` work (the `S360-400`
     `schematic_status: verified` JSON-only PR, additionally
     gated on the schematic-side PDF correction) is still owed;
     the `COMPLIANCE-001` `S360-400` slice; and the UX-class
     decision (standard preview-candidate vs advanced /
     manual-warning posture, owed to per-family
     `PRODUCT-POWER-400-001` compliance verdict).
   - Purpose: Add the WebFlash wrapper under
     [`products/webflash/`](products/webflash/), flip
     `webflash_build_matrix: true` on the matching
     [`config/product-catalog.json`](config/product-catalog.json)
     row, add the build-matrix row to
     [`config/webflash-builds.json`](config/webflash-builds.json),
     and decide the UX class (standard preview-candidate vs
     advanced / manual-warning). **Does not** build / sign /
     attach a release artifact, generate or validate release
     notes, emit checksums, or add a WebFlash import (those are
     `RELEASE-POWER-400-001` and `WF-IMPORT-POWER-400-001`
     cross-repo respectively).
   - Notes: 2026-05-19 investigation pass merged as PR #522 is
     **docs-only deferral**. Re-verified against the live files:
     **no S360-400 WebFlash wrapper exists** under
     [`products/webflash/`](products/webflash/) — only three PoE
     wrappers
     ([`ceiling-poe-ventiq-roomiq.yaml`](products/webflash/ceiling-poe-ventiq-roomiq.yaml),
     [`ceiling-poe-ventiq-roomiq-led.yaml`](products/webflash/ceiling-poe-ventiq-roomiq-led.yaml),
     [`ceiling-poe-ventiq-fantriac-roomiq.yaml`](products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml));
     [`config/webflash-builds.json`](config/webflash-builds.json)
     has **no `PWR` build** (only Release-One
     `Ceiling-POE-VentIQ-RoomIQ` `stable` and
     `Ceiling-POE-VentIQ-RoomIQ-LED` `preview`);
     [`config/webflash-compatibility.json`](config/webflash-compatibility.json)
     reserves `PWR` in `canonical_power: ["USB", "POE", "PWR"]`
     with **no `webflash_build_matrix: true` row consuming it**;
     `release_one_required_configs` stays
     `["Ceiling-POE-VentIQ-RoomIQ"]`;
     [`config/product-catalog.json`](config/product-catalog.json)
     has **no S360-400-specific product** (the four
     `legacy-compatible` `*-pwr` Core variants stay
     `legacy-compatible` / `webflash_build_matrix: false` / no
     `config_string` / no `webflash_wrapper` / no
     `artifact_name`);
     [`config/hardware-catalog.json`](config/hardware-catalog.json)
     `S360-400` row stays byte-identical
     (`schematic_status: cataloged_unverified`, no
     `schematic_file`); `tests/test_hardware_catalog.py:53`
     `EXPECTED_STILL_UNVERIFIED_SKUS = frozenset({"S360-320",
     "S360-400"})` actively enforces this state;
     [`docs/compliance/mains-voltage-uk-eu-assessment.md`](docs/compliance/mains-voltage-uk-eu-assessment.md)
     COMPLIANCE-001 `S360-400` slice is unchanged since PR #506
     (open / not cleared). The five open preconditions are:
     (1) **`PRODUCT-POWER-400-001` implementation slice has not
     landed** — only docs-only investigation merged as PR #521;
     per
     [`docs/webflash-exposure-readiness-matrix.md` Follow-up PR sequence](docs/webflash-exposure-readiness-matrix.md#follow-up-pr-sequence)
     `WEBFLASH-POWER-400-001` is explicitly gated on
     "`PRODUCT-POWER-400-001` landed + `COMPLIANCE-001`
     `S360-400` slice closed"; (2) **`PACKAGE-POWER-400-001`
     implementation slice has not landed** — only docs-only
     investigation merged as PR #520; a wrapper cannot wrap a
     package that stays `schematic-evidence-pending` +
     `needs-package-reconciliation` +
     `timing/compliance-pending`; (3) **`S360-400`
     `schematic_status: verified` JSON PR not landed**; (4)
     **`COMPLIANCE-001` `S360-400` slice still open** — last
     re-checked PR #506; (5) **UX-class decision pending** —
     standard preview-candidate vs advanced / manual-warning
     posture has not been chosen; per
     [`docs/webflash-exposure-readiness-matrix.md` §Power / S360-400 WebFlash posture](docs/webflash-exposure-readiness-matrix.md#power--s360-400-webflash-posture)
     "Future exposure class (intent)", the advanced /
     manual-warning posture is **not** the default for
     PWR-240V; the per-family `PRODUCT-POWER-400-001` slice
     compliance verdict decides, and that verdict has not been
     rendered. Path B (documentation /
     catalog-classification-note-only cleanup) was rejected
     because the readiness matrices already correctly classify
     the slice as `not-webflash-ready` / `no wrapper` / `no
     build-matrix entry`; Path C (implementation) was unsafe
     because adding a wrapper for a mains-voltage path while
     `COMPLIANCE-001` `S360-400` is open would violate the
     [`docs/compliance/mains-voltage-uk-eu-assessment.md`](docs/compliance/mains-voltage-uk-eu-assessment.md)
     gate, and adding a wrapper while
     `PRODUCT-POWER-400-001` has no canonical S360-400 /
     `PWR`-bearing product YAML to wrap would break the
     [`docs/webflash-exposure-readiness-matrix.md` Core rule](docs/webflash-exposure-readiness-matrix.md#core-rule).
     Must not destabilize Release-One; the four
     `legacy-compatible` `*-pwr` Core variants stay
     `legacy-compatible` / `webflash_build_matrix: false`;
     Release-One stays `Ceiling-POE-VentIQ-RoomIQ` / version
     `1.0.0` / channel `stable` / artifact
     `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` /
     tag `v1.0.0`; LED preview stays
     `Ceiling-POE-VentIQ-RoomIQ-LED` / `status: preview` /
     `channel: preview` / version `1.0.0` / artifact
     `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`;
     FanTRIAC stays `status: blocked` / `blocker: HW-005` /
     `webflash_build_matrix: false`. The next
     `WEBFLASH-POWER-400-001` PR must land **the WebFlash
     wrapper + the catalog `webflash_build_matrix: true` flip +
     the build-matrix row + the UX-class decision as a single
     atomic slice**, not as a documentation cleanup alone, and
     only after `PRODUCT-POWER-400-001` implementation and the
     `COMPLIANCE-001` `S360-400` slice closure both land.
     Investigation outcome recorded at
     `docs/webflash-exposure-readiness-matrix.md` §Power /
     S360-400 WebFlash posture,
     `docs/release-artifact-readiness-matrix.md` §Power /
     S360-400 release posture, and `docs/cleanup-audit.md`
     §`WEBFLASH-POWER-400-001 update (2026-05-19 — docs-only
     investigation pass)`. Pairs with WebFlash-side
     `WF-IMPORT-POWER-400-001` — see cross-repo dependencies.

4. **RELEASE-POWER-400-001**
   - Status: **Investigated 2026-05-19; merged as PR #523;
     confirmed deferred (Path A docs-only); seven preconditions
     still open**. Blocked on `WEBFLASH-POWER-400-001`
     implementation (only
     docs-only investigation merged as PR #522;
     wrapper + catalog `webflash_build_matrix: true` flip +
     build-matrix row + UX-class decision all remain owed),
     `PRODUCT-POWER-400-001` implementation (only docs-only
     investigation merged as PR #521); `PACKAGE-POWER-400-001`
     package-header cleanup landed under Path B / PR #537 on
     2026-05-20 — runtime YAML behavior unchanged; the residual
     coordinated `PACKAGE-POWER-400-001` work (the `S360-400`
     `schematic_status: verified` JSON-only PR, additionally
     gated on the schematic-side PDF correction) is still owed;
     the `COMPLIANCE-001` `S360-400` slice; the silkscreen /
     PCB / creepage / clearance / bench / thermal / EMI evidence
     (BOM cross-check at the part-identity layer resolved by
     `HW-BOM-ASSETS-002` / PR #535); and the UX-class decision.
   - Purpose: Build / sign / attach the S360-400 PWR-240V
     release `.bin`, generate and validate release notes via
     [`scripts/generate_webflash_release_notes.py`](scripts/generate_webflash_release_notes.py)
     / [`scripts/validate-webflash-release-notes.py`](scripts/validate-webflash-release-notes.py),
     emit SHA256 + MD5 checksums, attach a build-info
     manifest, record a proof row in
     [`docs/webflash-release-proof.md`](docs/webflash-release-proof.md),
     and hand off to `WF-IMPORT-POWER-400-001` (cross-repo) per
     [`docs/webflash-release-handoff.md`](docs/webflash-release-handoff.md).
     Subject to the eight release-time sub-gates at
     [`docs/release-artifact-readiness-matrix.md` §Release note / artifact / checksum gates](docs/release-artifact-readiness-matrix.md#release-note--artifact--checksum-gates).
   - Notes: 2026-05-19 investigation pass merged as PR #523 is
     **docs-only deferral**. Re-verified against the live
     release surface: **no S360-400 release artifact exists of
     any kind** — no `firmware/` directory, no
     `firmware/configurations/`, no `firmware/sources.json`,
     no top-level `manifest.json`, no `firmware-*.json` (none
     of those paths exist at HEAD); release infrastructure is
     [`config/webflash-builds.json`](config/webflash-builds.json)
     consumed by
     [`.github/workflows/firmware-build-release.yml`](.github/workflows/firmware-build-release.yml)
     which is in the do-not-change guardrail and processes only
     entries in that matrix file, and the matrix has no
     PWR-240V row; no GitHub Release for any PWR-240V tag
     exists; no
     `Sense360-Ceiling-PWR-{AIR}-{ROOM}-v{VERSION}-{CHANNEL}.bin`
     artifact has been built / signed / attached / imported; no
     SHA256 / MD5 checksum files for any PWR-240V artifact; no
     build-info `manifest.json` asset for any PWR-240V release;
     no proof row in
     [`docs/webflash-release-proof.md`](docs/webflash-release-proof.md)
     for any PWR-240V artifact; the two existing
     `artifact_name` entries
     (`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` and
     `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`)
     stay byte-identical;
     [`config/webflash-compatibility.json`](config/webflash-compatibility.json)
     `release_one_required_configs` stays
     `["Ceiling-POE-VentIQ-RoomIQ"]`. The seven open
     preconditions are: (1) **`WEBFLASH-POWER-400-001`
     implementation slice has not landed** — only docs-only
     investigation merged as PR #522; per
     [`docs/release-artifact-readiness-matrix.md` Follow-up PR sequence](docs/release-artifact-readiness-matrix.md#follow-up-pr-sequence)
     row at line 1502, `RELEASE-POWER-400-001` is explicitly
     gated on "`WEBFLASH-POWER-400-001` landed +
     `COMPLIANCE-001` `S360-400` slice closed"; (2)
     **`PRODUCT-POWER-400-001` implementation slice has not
     landed** — only docs-only investigation merged as PR #521;
     (3) **`PACKAGE-POWER-400-001` implementation slice has not
     landed** — only docs-only investigation merged as PR #520;
     (4) **`S360-400` `schematic_status: verified` JSON PR not
     landed**; (5) **`COMPLIANCE-001` `S360-400` slice still
     open** — last re-checked PR #506; (6) **silkscreen /
     creepage / clearance / bench / thermal / EMI evidence
     missing** — the five-component BOM gap that PR #520
     recorded is now **landed under
     `HW-BOM-ASSETS-002` / PR #535** (see Recently uploaded
     evidence; BOM `PS1 = HLK-5M05` HI-LINK confirmed as
     populated AC/DC converter; `F1 A250-1200` JDTfuse,
     `RV1 10D391K` RUILON, `C1 470nF` WALSON,
     `C5, C8 100uF` KNSCHA, `C6 10u` Chinocera, `C7 100n` CCTC,
     `J1` WAGO 2601-3103, `J2` JST SH `SM02B-SRSS-TB(LF)(SN)`
     all BOM-confirmed at the part-identity layer; the
     schematic-PDF value-field `PS1 = HLK-10M05` is recorded as
     a schematic-label discrepancy owed to a later HW-ASSETS-400
     follow-up; the package-header `HLK-PM01 or similar` is
     recorded as disproved comment text and cleanup is deferred
     to `PACKAGE-POWER-400-001`); per-component voltage /
     energy / safety-class / X-cap-class ratings beyond the BOM
     `MFR#` strings, all silkscreen / PCB / creepage /
     clearance / bench / load / thermal / inrush / insulation /
     Hi-pot / earth-continuity / leakage / EMI / EMC
     measurements against a populated `S360-400-R4` board, plus
     the schematic-label correction PR for the `PS1` value
     field, all still missing;
     (7) **UX-class decision pending** — decision belongs
     upstream to `PRODUCT-POWER-400-001` /
     `WEBFLASH-POWER-400-001` compliance verdict per the
     Follow-up PR sequence row at line 1502; that verdict has
     not been rendered. Path B (release-notes /
     proof-template-only PR) was rejected because (a)
     `scripts/generate_webflash_release_notes.py` consumes
     `config/webflash-builds.json` as the matrix source and
     needs a `(config_string, version, channel)` input tuple
     that does not exist for PWR-240V; (b) a
     proof-template-only edit to
     `docs/webflash-release-proof.md` would introduce a
     forward-reference to an artifact that has never been
     built and would degrade the proof file's evidentiary
     integrity; (c) per the Follow-up PR sequence row at line
     1502, `RELEASE-POWER-400-001` is explicitly **"Build,
     sign, attach the `.bin`; release notes; checksums; proof
     row"** — that is the atomic slice. Path C
     (implementation) was unsafe because every upstream gate is
     open and the workflow file is workflow-frozen; building /
     signing / attaching a PWR-240V `.bin` while
     `COMPLIANCE-001` `S360-400` is open would violate the
     [`docs/compliance/mains-voltage-uk-eu-assessment.md`](docs/compliance/mains-voltage-uk-eu-assessment.md)
     gate. All eight release-time sub-gates at
     [`docs/release-artifact-readiness-matrix.md` §Release note / artifact / checksum gates](docs/release-artifact-readiness-matrix.md#release-note--artifact--checksum-gates)
     remain unmet for any PWR-240V `.bin`: product-catalog
     entry (none), build-matrix entry (none), artifact-name
     conformance (no `artifact_name`), release-tag conformance
     (no tag), release-notes generated (no
     `(config_string, version, channel)` input), release-notes
     valid (no body), artifact built (no input matrix row),
     checksums attached / manifest attached / proof recorded
     (no asset). Must not destabilize Release-One; Release-One
     stays `Ceiling-POE-VentIQ-RoomIQ` / version `1.0.0` /
     channel `stable` / artifact
     `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` /
     tag `v1.0.0`; LED preview stays
     `Ceiling-POE-VentIQ-RoomIQ-LED` / `preview` / artifact
     `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`;
     FanTRIAC stays `blocked` / `HW-005` /
     `webflash_build_matrix: false`. The next
     `RELEASE-POWER-400-001` PR must land **the build + sign +
     attach `.bin` + generate release notes + validate release
     notes + emit SHA256 + emit MD5 + attach build-info manifest
     + record proof row + hand off to WF-IMPORT-POWER-400-001
     (cross-repo) as a single atomic slice**, not as a
     release-notes / proof-template-only PR alone, and only
     after `WEBFLASH-POWER-400-001` implementation and the
     `COMPLIANCE-001` `S360-400` slice closure both land. UX
     class decided per the `PRODUCT-POWER-400-001` /
     `WEBFLASH-POWER-400-001` compliance verdict. Investigation
     outcome recorded at
     `docs/release-artifact-readiness-matrix.md` §Power /
     S360-400 release posture and `docs/cleanup-audit.md`
     §`RELEASE-POWER-400-001 update (2026-05-19 — docs-only
     investigation pass)`. Pairs with WebFlash-side
     `WF-IMPORT-POWER-400-001` — see cross-repo dependencies.
     [`docs/webflash-exposure-readiness-matrix.md` §Power / S360-400 WebFlash posture](docs/webflash-exposure-readiness-matrix.md#power--s360-400-webflash-posture),
     [`docs/release-artifact-readiness-matrix.md` §Power / S360-400 release posture](docs/release-artifact-readiness-matrix.md#power--s360-400-release-posture),
     and
     [`docs/cleanup-audit.md` §`WEBFLASH-POWER-400-001 update (2026-05-19 — docs-only investigation pass)`](docs/cleanup-audit.md).

5. **RELEASE-POE-410-001**
    - Status: **Investigated 2026-05-20; merged as PR #532;
      confirmed deferred (Path A docs-only); preconditions still
      open**. Blocked on `WEBFLASH-POE-410-001` implementation
      (only the docs-only investigation merged as PR #530;
      the WebFlash wrapper, the catalog
      `webflash_build_matrix: true` flip, the build-matrix row,
      and the UX-class decision all remain owed),
      `PRODUCT-POE-410-001` implementation (only the docs-only
      investigation merged as PR #528),
      `PACKAGE-POE-410-001` implementation (the docs-only
      investigation merged as PR #526; BOM cross-check **landed
      under `HW-BOM-ASSETS-002` / PR #535** at the
      discrete-topology part-identity layer — the schematic-shown
      `LAN_CON1 RJP-003TC1(LPJ4112CNL)` magnetics / RJ45,
      `U1 TPS2378DDAR(HSOIC-8)` PoE PD controller,
      `U2 TX4138(ESOIC-8)` buck, and `DCDC1 F0505S-2WR2(SIP-7)`
      isolated DC/DC are all BOM-confirmed; the
      `PACKAGE-POE-410-001` **package-header cleanup component
      landed under Path B / PR #538 on 2026-05-21** — the
      disproved `Ag9712M, Silvertel Ag9700, or similar`
      whole-module hint is removed from
      [`packages/hardware/power_poe.yaml`](packages/hardware/power_poe.yaml),
      the BOM-confirmed discrete topology is named in the
      header, the schematic-annotated `AM1D-0505S-NZ` is
      explicitly reclassified as a schematic-annotation-only
      alternate, electrical ratings are reclassified as
      vendor-datasheet typicals, the header restates that the
      package is logical / diagnostic only with no GPIO /
      I2C / UART / SPI / DAC runtime binding, and the header
      restates that no release / WebFlash / product-catalog /
      schematic-status claim is made; runtime YAML behavior
      is byte-identical to PR #517 / PR #526 / PR #535 state;
      the residual coordinated `PACKAGE-POE-410-001` work
      (the `S360-410` `schematic_status: verified` JSON-only
      PR, HW-002 OQ#6 / `S360-100-BENCH-001` J2-harness
      identity closure, and the Release-One PoE caveat-closure
      PR) plus silkscreen / PCB / creepage / clearance /
      bench / thermal / EMI / PoE-link-up / isolation evidence
      remain owed), the `S360-410`
      `schematic_status: verified` JSON PR, HW-002 OQ#6 /
      `S360-100-BENCH-001` J2-harness identity closure, the
      Release-One PoE "schematic verification pending"
      caveat-closure PR, product-onboarding approval, and the
      eight release-time sub-gates at
      [`docs/release-artifact-readiness-matrix.md` §Release note / artifact / checksum gates](docs/release-artifact-readiness-matrix.md#release-note--artifact--checksum-gates).
      A carried-forward observation is also recorded: per
      [`docs/product-readiness-matrix.md` §PoE-410 / S360-410](docs/product-readiness-matrix.md#poe-410--s360-410)
      and the
      [`docs/release-artifact-readiness-matrix.md` Follow-up PR sequence](docs/release-artifact-readiness-matrix.md#follow-up-pr-sequence),
      `RELEASE-POE-410-001` may become a no-op if
      `PRODUCT-POE-410-001` / `WEBFLASH-POE-410-001` ultimately
      close via the default no-new-entry / caveat-closure-only
      path; the observation does **not** declare
      `RELEASE-POE-410-001` no-op today.
    - Purpose: Build / sign / attach the S360-410 PoE-410-explicit
      release `.bin`, generate and validate release notes via
      [`scripts/generate_webflash_release_notes.py`](scripts/generate_webflash_release_notes.py)
      / [`scripts/validate-webflash-release-notes.py`](scripts/validate-webflash-release-notes.py),
      emit SHA256 + MD5 checksums, attach a build-info
      manifest, record a proof row in
      [`docs/webflash-release-proof.md`](docs/webflash-release-proof.md),
      and hand off to `WF-IMPORT-POE-410-001` (cross-repo) per
      [`docs/webflash-release-handoff.md`](docs/webflash-release-handoff.md).
      Subject to the eight release-time sub-gates at
      [`docs/release-artifact-readiness-matrix.md` §Release note / artifact / checksum gates](docs/release-artifact-readiness-matrix.md#release-note--artifact--checksum-gates).
    - Notes: 2026-05-20 investigation pass merged as PR #532 is
      **docs-only deferral**. Re-verified against the live
      release surface: **no PoE-410-explicit release artifact
      exists of any kind** beyond the existing Release-One
      stable artifact
      `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`
      (tag `v1.0.0`) and the LED preview artifact
      `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`
      (tag `v1.0.0-led-preview`), both of which consume S360-410
      **logically** under Release-One identity and the preserved
      schematic-pending caveat — no `firmware/` directory, no
      `firmware/configurations/`, no `firmware/sources.json`,
      no top-level `manifest.json`, no `firmware-*.json` (none
      of those paths exist at HEAD); no GitHub Release for any
      PoE-410-explicit tag exists; no PoE-410-explicit
      `Sense360-…-v{VERSION}-{CHANNEL}.bin` artifact has been
      built / signed / attached / imported; no SHA256 / MD5
      checksum files for any PoE-410-explicit artifact; no
      build-info `manifest.json` asset for any PoE-410-explicit
      release; no proof row in
      [`docs/webflash-release-proof.md`](docs/webflash-release-proof.md)
      for any PoE-410-explicit artifact; the two existing
      `artifact_name` entries
      (`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`
      and
      `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`)
      stay byte-identical;
      [`config/webflash-compatibility.json`](config/webflash-compatibility.json)
      `release_one_required_configs` stays
      `["Ceiling-POE-VentIQ-RoomIQ"]`;
      [`.github/workflows/firmware-build-release.yml`](.github/workflows/firmware-build-release.yml)
      stays byte-identical (workflow-frozen, processes only
      entries in
      [`config/webflash-builds.json`](config/webflash-builds.json),
      which has no PoE-410-explicit row). All eight
      release-time sub-gates at
      [`docs/release-artifact-readiness-matrix.md` §Release note / artifact / checksum gates](docs/release-artifact-readiness-matrix.md#release-note--artifact--checksum-gates)
      remain unmet for any PoE-410-explicit `.bin`:
      product-catalog entry (none), build-matrix entry (none),
      artifact-name conformance (no `artifact_name`),
      release-tag conformance (no tag), release-notes generated
      (no `(config_string, version, channel)` input),
      release-notes valid (no body to validate), artifact built
      (no input matrix row), checksums attached / manifest
      attached / proof recorded (no asset to checksum /
      manifest / prove). Path B (release-notes /
      proof-template-only PR) was rejected because (a)
      `scripts/generate_webflash_release_notes.py` consumes
      `config/webflash-builds.json` as the matrix source and
      needs a `(config_string, version, channel)` input tuple
      that does not exist for PoE-410-explicit; (b) a
      proof-template-only edit to
      `docs/webflash-release-proof.md` would introduce a
      forward-reference to an artifact that has never been
      built and would degrade the proof file's evidentiary
      integrity; (c) the
      [`docs/release-artifact-readiness-matrix.md` Follow-up PR sequence](docs/release-artifact-readiness-matrix.md#follow-up-pr-sequence)
      explicitly defines `RELEASE-POE-410-001` as **"Build,
      sign, attach the `.bin`; release notes; checksums;
      proof row"** — that is the atomic slice. Path C
      (implementation) was unsafe because every upstream gate
      is open: `WEBFLASH-POE-410-001` /
      `PRODUCT-POE-410-001` / `PACKAGE-POE-410-001`
      implementation slices have not landed; repo-committed
      BOM evidence has **now landed under
      `HW-BOM-ASSETS-002` / PR #535** (see Recently uploaded
      evidence; the schematic-shown discrete topology
      `U1 TPS2378DDAR` TI + `U2 TX4138` XDS +
      `DCDC1 F0505S-2WR2` EVISUN + `LAN_CON1 LPJ4112CNL`
      Link-PP is BOM-confirmed at the discrete-topology
      part-identity layer; the package-header
      `Ag9712M, Silvertel Ag9700, or similar` is disproved
      and cleanup deferred to `PACKAGE-POE-410-001`; the
      schematic-annotated `AM1D-0505S-NZ` is recorded as a
      schematic-annotation-only alternate not present in the
      BOM); the
      `S360-410` `schematic_status: verified` JSON PR has not
      landed; HW-002 OQ#6 / `S360-100-BENCH-001` J2-harness
      identity closure has not landed; the Release-One PoE
      caveat is preserved verbatim; and
      [`.github/workflows/firmware-build-release.yml`](.github/workflows/firmware-build-release.yml)
      is in the do-not-change guardrail. Must not destabilize
      Release-One; Release-One stays `Ceiling-POE-VentIQ-RoomIQ`
      / version `1.0.0` / channel `stable` / artifact
      `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` /
      tag `v1.0.0`; LED preview stays
      `Ceiling-POE-VentIQ-RoomIQ-LED` / `status: preview` /
      `channel: preview` / artifact
      `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`
      / tag `v1.0.0-led-preview`; FanTRIAC stays
      `status: blocked` / `blocker: HW-005` /
      `webflash_build_matrix: false`. The next
      `RELEASE-POE-410-001` PR (if and only if
      `PRODUCT-POE-410-001` / `WEBFLASH-POE-410-001` ultimately
      add a new PoE-410-explicit product entry + WebFlash
      wrapper + build-matrix row) must land **the build + sign
      + attach `.bin` + generate release notes + validate
      release notes + emit SHA256 + emit MD5 + attach
      build-info manifest + record proof row + hand off to
      `WF-IMPORT-POE-410-001` (cross-repo) as a single atomic
      slice**, not as a release-notes / proof-template-only PR
      alone, and only after `WEBFLASH-POE-410-001`
      implementation, `PRODUCT-POE-410-001` implementation,
      `PACKAGE-POE-410-001` implementation (with the
      BOM-cross-check precondition now landed under
      `HW-BOM-ASSETS-002` / PR #535), the `S360-410`
      `schematic_status: verified` JSON PR, the Release-One PoE
      caveat-closure PR, and product-onboarding approval all
      land. If `PRODUCT-POE-410-001` / `WEBFLASH-POE-410-001`
      close by the default no-new-entry / caveat-closure-only
      path, `RELEASE-POE-410-001` becomes a no-op and no
      implementation PR is needed. Pairs with WebFlash-side
      `WF-IMPORT-POE-410-001` — see cross-repo dependencies.
      Investigation outcome recorded at
      [`docs/release-artifact-readiness-matrix.md` §PoE / S360-410 release posture](docs/release-artifact-readiness-matrix.md#poe--s360-410-release-posture),
      [`docs/webflash-exposure-readiness-matrix.md` §PoE / S360-410 WebFlash posture](docs/webflash-exposure-readiness-matrix.md#poe--s360-410-webflash-posture),
      [`docs/hardware/s360-410-r4-poe.md`](docs/hardware/s360-410-r4-poe.md)
      §HW-PINMAP-410-FOLLOWUP audit log row
      `2026-05-20 — RELEASE-POE-410-001 investigation pass`, and
      [`docs/cleanup-audit.md` §`RELEASE-POE-410-001 update (2026-05-20 — docs-only investigation pass)`](docs/cleanup-audit.md).

6. **PACKAGE-RELAY-001 — implementation slice**
    - Status: **Merged (this PR / 2026-05-22).** Implemented as a
      **test + readiness reconciliation**: no YAML rebind. The
      FanRelay package was already structurally correct
      (`fan_relay_pin: ${relay_pin}` in
      [`packages/expansions/fan_relay.yaml`](packages/expansions/fan_relay.yaml)
      line 27 inherits the parent Core abstract package binding,
      and post-001A `${relay_pin}` resolves to the schematic-
      correct `GPIO3`). The reconciliation is the addition of
      [`tests/test_fan_relay_package.py`](tests/test_fan_relay_package.py)
      pinning the FanRelay package abstraction against future
      regression. Substitution-layer preconditions were resolved
      by `CORE-ABSTRACT-BUS-001C` / PR #557 + `CORE-ABSTRACT-BUS-001A`
      / PR #558; hardware-evidence preconditions were populated by
      `S360-310-BENCH-EVIDENCE-001` / PR #561. **No product /
      WebFlash / release / compliance / mains-safety / hardware-
      stable promotion is made.** `PACKAGE-RELAY-001` is
      implemented / reconciled **at the package layer only**.
    - Purpose: Reconcile
      [`packages/expansions/fan_relay.yaml`](packages/expansions/fan_relay.yaml)
      against the now-closed package-evidence layer. The package's
      structural correctness is now pinned by
      [`tests/test_fan_relay_package.py`](tests/test_fan_relay_package.py).
    - Notes: "Implemented / reconciled at the `PACKAGE-RELAY-001`
      package layer" does **not** mean:
      - product-ready
      - WebFlash-ready
      - release-ready
      - compliance-cleared
      - safe for arbitrary mains installation
      - verified across production batches
      `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` /
      `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001` stay blocked
      behind PACKAGE-RELAY-001 → PRODUCT-RELAY-001.
      `S360-100-BENCH-001` is **not** closed by this PR. The
      production-wide / multi-unit / oscilloscope-traced general
      `GPIO3` strap-pin boot-behaviour characterisation is **not**
      required for `PACKAGE-RELAY-001` implementation but remains
      owed for future production / compliance / safety-
      certification work. The operator-uploaded
      `S360-310-R4_BOM.xlsx` is consumed for the `K1` BOM-backed
      evidence row only and is **not** committed to this
      repository.

7. **PRODUCT-RELAY-001**
    - Status: Blocked on `PACKAGE-RELAY-001` implementation
      (evidence layer satisfied 2026-05-22 by
      `S360-310-BENCH-EVIDENCE-001`; implementation PR has not
      landed). The `CORE-ABSTRACT-BUS-001A` substitution-layer
      precondition (`relay_pin → GPIO3` across the five non-voice
      Core abstract packages) is **resolved** by PR #558; the
      `GPIO3` collision precondition is **resolved** by
      `CORE-ABSTRACT-BUS-001C` / PR #557; the
      `PACKAGE-RELAY-001-READINESS-REFRESH` PR (2026-05-21,
      docs-only) consolidated the readiness table; the
      `S360-310-BENCH-001` checklist PR (PR #560) and the
      `S360-310-BENCH-EVIDENCE-001` evidence-population PR (this
      PR, 2026-05-22) populated the ten hardware-evidence rows at
      the package-evidence layer. Board-level mains-safety /
      installation-approval / production-wide characterisation
      remains owed at the product layer and is **not** discharged
      by the package-evidence-layer captures.
    - Purpose: Add the S360-310 Relay product YAML once
      `PACKAGE-RELAY-001` implementation lands.
    - Notes: Implementation deferred per PR #511 (PACKAGE-RELAY-001
      docs-only deferral). The conservative next active-queue item
      ahead of `PRODUCT-RELAY-001` is `PACKAGE-RELAY-001`
      implementation (item #6 above). The pair-scoped boot-OK
      observation in
      [`docs/hardware/core-abstract-bus-001c-rebind-plan.md`](docs/hardware/core-abstract-bus-001c-rebind-plan.md)
      decisions #16 / #17 and the `S360-310-BENCH-EVIDENCE-001`
      pair-scoped 10-cycle × 4-power-path boot evidence are
      **not** generic `GPIO3` strap-pin boot-behaviour claims and
      do **not** discharge the product-layer mains-safety /
      installation-approval / production-wide characterisation
      gates.

8. **WEBFLASH-RELAY-001**
    - Status: Blocked on `PRODUCT-RELAY-001` implementation
    - Purpose: Add the WebFlash wrapper, compatibility entry, and build
      matrix row for the Relay product.
    - Notes: Pairs with WebFlash-side `WF-IMPORT-RELAY-001`. The
      `CORE-ABSTRACT-BUS-001A` substitution-layer precondition is
      **resolved**; the `GPIO3` collision precondition is
      **resolved**; the `PACKAGE-RELAY-001` evidence layer is
      satisfied (2026-05-22, by `S360-310-BENCH-EVIDENCE-001` —
      this PR); remaining gates are `PACKAGE-RELAY-001`
      implementation + `PRODUCT-RELAY-001` implementation +
      product-layer compliance / mains-safety / installation
      sign-offs. The `PACKAGE-RELAY-001-READINESS-REFRESH` PR
      (2026-05-21, docs-only) consolidated the readiness table at
      [`docs/hardware/s360-310-r4-relay.md` §PACKAGE-RELAY-001 readiness refresh after CORE-ABSTRACT-BUS-001C / 001A](docs/hardware/s360-310-r4-relay.md#package-relay-001-readiness-refresh-after-core-abstract-bus-001c--001a);
      `S360-310-BENCH-EVIDENCE-001` populated the captured-evidence
      table.

9. **RELEASE-RELAY-001**
    - Status: Blocked on `WEBFLASH-RELAY-001`
    - Purpose: Produce the release artifact + release-proof entries for
      the Relay product.
    - Notes: The `CORE-ABSTRACT-BUS-001A` substitution-layer
      precondition is **resolved**; the `GPIO3` collision
      precondition is **resolved**; the `PACKAGE-RELAY-001`
      evidence layer is satisfied (2026-05-22, by
      `S360-310-BENCH-EVIDENCE-001` — this PR); remaining gates
      inherit from `PACKAGE-RELAY-001` / `PRODUCT-RELAY-001` /
      `WEBFLASH-RELAY-001` implementation + product / compliance /
      release-readiness gates. The
      `PACKAGE-RELAY-001-READINESS-REFRESH` PR (2026-05-21,
      docs-only) consolidated the readiness table;
      `S360-310-BENCH-EVIDENCE-001` populated the captured-evidence
      table. **No `RELEASE-RELAY-001` unblock claim is made by
      `S360-310-BENCH-EVIDENCE-001`.**

10. **PACKAGE-PWM-001**
    - Status: Blocked on HW-PINMAP-311-FOLLOWUP returning sufficient evidence
    - Purpose: Stand up / re-stand up the S360-311 PWM package wiring once
      the pin/package audit is no longer partial.
    - Notes: Also affected by CORE-ABSTRACT-BUS-001B (shared I²C bus
      consolidation) and CORE-ABSTRACT-BUS-001C (`expansion_gpio1`
      / `expansion_gpio2` rebind that `fan_pwm.yaml` consumes via
      `${fan_pwm_pin}` / `${fan_tach_pin}`).

11. **PRODUCT-PWM-001**
    - Status: Blocked on PACKAGE-PWM-001
    - Purpose: Add / re-align the S360-311 PWM product YAML.

12. **WEBFLASH-PWM-001**
    - Status: Blocked on PRODUCT-PWM-001
    - Purpose: WebFlash wrapper, compatibility entry, build matrix row.
    - Notes: Pairs with WebFlash-side WF-IMPORT-PWM-001.

13. **RELEASE-PWM-001**
    - Status: Blocked on WEBFLASH-PWM-001
    - Purpose: Release artifact + release-proof entries for the PWM product.

14. **PACKAGE-DAC-001**
    - Status: Blocked on HW-PINMAP-312-FOLLOWUP returning sufficient evidence
    - Purpose: Stand up / re-stand up the S360-312 DAC (GP8403) package
      wiring once the pin/package audit is no longer partial.
    - Notes: Also affected by CORE-ABSTRACT-BUS-001B (the GP8403
      DAC is I²C-attached, so it consumes whichever bus id 001B
      settles on).

15. **PRODUCT-DAC-001**
    - Status: Blocked on PACKAGE-DAC-001
    - Purpose: Add / re-align the S360-312 DAC product YAML.

16. **WEBFLASH-DAC-001**
    - Status: Blocked on PRODUCT-DAC-001
    - Purpose: WebFlash wrapper, compatibility entry, build matrix row.
    - Notes: Pairs with WebFlash-side WF-IMPORT-DAC-001.

17. **RELEASE-DAC-001**
    - Status: Blocked on WEBFLASH-DAC-001
    - Purpose: Release artifact + release-proof entries for the DAC product.

18. **S360-300-BENCH-001**
    - Status: Pending bench evidence
    - Purpose: LED ring bench / verification gate for S360-300.
    - Notes: Blocks the LED stable chain together with the WebFlash-owned
      operator-proof follow-ups.

19. **RELEASE-007**
    - Status: Planned / promotion of LED stable
    - Purpose: Promote the LED package + product from preview to stable
      once S360-300-BENCH-001 and the WebFlash operator-proof follow-ups
      land.
    - Notes: Subject to preview-to-stable promotion gates.

20. **HW-005 / HW-PINMAP-320-FOLLOWUP**
    - Status: Open / evidence-pass re-checked (PR #505); audit remains
      partial
    - Purpose: Resolve the S360-320 FanTRIAC pin/package collisions and
      provide the schematic/interrupt-capable GPIO evidence needed to
      progress the FanTRIAC chain.
    - Notes: Gating PACKAGE-TRIAC-001 implementation.

21. **COMPLIANCE-001**
    - Status: Open / not cleared (PR #506 re-checked, no sign-off yet)
    - Purpose: Land the S360-320 mains-voltage advanced / manual-warning
      compliance sign-off.
    - Notes: Gating PRODUCT-TRIAC-002 / FanTRIAC release exposure.

22. **PACKAGE-TRIAC-001**
    - Status: Deferred (PR #502 docs-only); blocked on HW-005 /
      HW-PINMAP-320-FOLLOWUP / COMPLIANCE-001
    - Purpose: Implement the FanTRIAC package once the gating HW +
      compliance evidence lands.
    - Notes: `packages/expansions/fan_triac.yaml` retained as-is in the
      meantime.

23. **PRODUCT-TRIAC-002**
    - Status: Deferred (PR #501 docs-only); blocked on PACKAGE-TRIAC-001
    - Purpose: Implement the FanTRIAC product YAML once PACKAGE-TRIAC-001
      lands.

24. **WF-TRIAC-001 — In-repo wrapper/catalog/build slice**
    - Status: Blocked on PRODUCT-TRIAC-002
    - Purpose: Add the in-repo WebFlash wrapper, compatibility entry, and
      build matrix row for the FanTRIAC product. (This is the
      esphome-public-owned slice — the WebFlash-runtime import is tracked
      separately under cross-repo dependencies as WF-IMPORT-TRIAC-001.)
    - Notes: Listed here, not under cross-repo dependencies, because it
      touches `products/webflash/`, `config/`, and the build matrix in this
      repo.

25. **RELEASE-TRIAC-001**
    - Status: Blocked on WF-TRIAC-001 and COMPLIANCE-001
    - Purpose: Release artifact + release-proof entries for the FanTRIAC
      product, contingent on compliance sign-off.

26. **PRODUCT-DEP-002**
    - Status: Planned / housekeeping
    - Purpose: Continue dependency / toolchain alignment work (pre-commit
      tooling, ESPHome pin, Python tooling) without changing functional
      behavior.
    - Notes: Must not destabilize Release-One.

27. **CI-TOOLCHAIN-001**
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

- **2026-05-22 — `S360-310-BENCH-EVIDENCE-001` populated the ten
  `S360-310-BENCH-001` Relay bench evidence rows from
  operator-attested + BOM-backed + public-reference-backed sources
  (no physical photo / video / oscilloscope / continuity-meter
  artifacts attached).** Docs / evidence-population follow-up to
  `S360-310-BENCH-001` (PR #560). Operator `@wifispray` (Wifi Guy)
  supplied bench-attested evidence against a populated
  `S360-100-R4` + `S360-310-R4` pair: Core-side `J4` pin order
  `+5V` / `Relay` / `GND`; module-side `J2` pin order
  `+5V` / `Relay` / `GND`; module-side `J1` mapping
  `NO` / `COM` / `NC`; 3-pin Core ↔ module harness
  **straight-through** with J4-1↔J2-1 / J4-2↔J2-2 / J4-3↔J2-3;
  expected controlled load type **UK mains bathroom extractor fan,
  Manrose `MT100S`-class** (operator self-report of installation
  posture "as per UK standards", **not** an independent compliance
  sign-off); **relay boot state de-energized across 10 boot cycles
  × 4 power paths (USB, PoE, 5 V PSU, and 240 V supply path)** with
  firmware `Ceiling-POE-VentIQ-RoomIQ`; **relay load / contact
  proof** (fan off until relay activates, relay on → fan on, relay
  off → fan off; behaviour consistent with `NO` + `COM` wiring;
  exact terminal use inferred from observed behaviour and `J1`
  mapping unless explicitly photo-proven, which it is not).
  Operator also uploaded `S360-310-R4_BOM.xlsx` (header `Reference,
  Qty, Value, Footprint, MFR#, Manufacturer`) with the `K1` row
  `Reference: K1; Qty: 1; Value: SRD-05VDC-SL-C-srd_relay;
  Footprint: greencharge-footprints:RELAY_SRD-05VDC-SL-C; MFR#:
  SRD-05VDC-SL-C; Manufacturer: Songle Relay`. **The BOM file is
  uploaded operator-side and is not committed to this repository.**
  Public SRD-style 5 V relay reference / datasheet cited for the
  `K1` contact-current rating `10 A @ 250 VAC; 10 A @ 30 VDC`,
  SPDT (`NO` / `COM` / `NC` terminals); **caveat: contact-rating
  evidence only — not board-level compliance, installation
  approval, creepage / clearance, thermal, EMI, or mains-safety
  certification.** The `GPIO3` strap-pin boot-behaviour row is
  captured as `captured enough for PACKAGE-RELAY-001
  implementation` against the operator-attested 10 boot cycles × 4
  power paths; **caveat: not a production-wide, multi-unit,
  oscilloscope-traced, compliance, release-readiness, or
  safety-certification claim.** The §`Status-language rules` list
  in [`docs/hardware/s360-310-r4-relay.md`](docs/hardware/s360-310-r4-relay.md)
  is extended with four new status values (`captured —
  operator-attested`, `captured — BOM-backed`, `captured —
  public-reference-backed`, `captured enough for
  PACKAGE-RELAY-001 implementation`); a new §`What this record now
  unblocks` subsection records the verbatim "Implementation-ready
  at the PACKAGE-RELAY-001 evidence layer" caveat block; §`Status`
  and §`Summary verdict` are refreshed to reflect the
  captured-evidence state; a new 2026-05-22 row is appended to
  §`HW-PINMAP-310-FOLLOWUP audit log`. The `fan_relay.yaml` row in
  [`docs/hardware/package-readiness-matrix.md`](docs/hardware/package-readiness-matrix.md)
  is refreshed to `package-evidence-captured` +
  `implementation-ready at PACKAGE-RELAY-001 evidence layer`;
  the §`fan_relay.yaml` / S360-310 detail-section bullets are
  refreshed in parallel; a 2026-05-22 update sub-paragraph is
  appended to the PACKAGE-RELAY-001 investigation-outcome bullet.
  A 2026-05-22 update sub-bullet is appended to the Release-One
  package-stack `relay_pin` finding in
  [`docs/hardware/firmware-package-mapping-audit.md`](docs/hardware/firmware-package-mapping-audit.md).
  `PACKAGE-RELAY-001` is now **implementation-ready at the
  package-evidence layer only**. **"Implementation-ready at the
  PACKAGE-RELAY-001 evidence layer" does not mean: product-ready;
  WebFlash-ready; release-ready; compliance-cleared; safe for
  arbitrary mains installation; or verified across production
  batches.** The active queue is refreshed to insert a new
  `PACKAGE-RELAY-001 — implementation slice` entry at item #6
  ahead of `PRODUCT-RELAY-001` (now item #7), with downstream
  Relay-chain (`PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` /
  `RELEASE-RELAY-001` / `PWM` / `DAC` / `S360-300-BENCH-001` /
  `RELEASE-007` / `HW-005` / `COMPLIANCE-001` / TRIAC chain /
  housekeeping) entries renumbered. **`PACKAGE-RELAY-001`
  implementation has not landed** (the implementation slice is
  owed to a separate PR). `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001`
  / `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001` stay blocked
  behind `PACKAGE-RELAY-001`. **No `packages/**` edit** (
  [`packages/expansions/fan_relay.yaml`](packages/expansions/fan_relay.yaml)
  unchanged; the five non-voice Core abstract packages stay at the
  post-001A `relay_pin: GPIO3` value; the voice-variant Core
  packages stay at pre-001A `relay_pin: GPIO4`, out of scope);
  **no `products/**` or `products/webflash/**` edit**; **no
  `config/**` edit** (
  [`config/hardware-catalog.json`](config/hardware-catalog.json),
  [`config/product-catalog.json`](config/product-catalog.json),
  [`config/webflash-builds.json`](config/webflash-builds.json),
  [`config/webflash-compatibility.json`](config/webflash-compatibility.json),
  [`config/firmware-combination-matrix.json`](config/firmware-combination-matrix.json),
  [`config/kit-intent-matrix.json`](config/kit-intent-matrix.json),
  [`config/compile-only-targets.json`](config/compile-only-targets.json),
  and [`config/compile-only-candidates.json`](config/compile-only-candidates.json)
  all byte-identical); **no `scripts/**` / `.github/workflows/**`
  / `components/**` / `include/**` / `firmware/**` /
  `manifest.json` / `firmware/sources.json` / `tests/**` edit**
  (the
  [`tests/test_core_abstract_bus.py`](tests/test_core_abstract_bus.py)
  scaffold from 001C / 001A is preserved verbatim and not
  extended); **no `webflash_build_matrix` flip**; **no
  `artifact_name` / `webflash_wrapper` / `config_string` /
  `release_one_required_configs` / `lifecycle_statuses` /
  `canonical_modules` / `canonical_power` / `forbidden_tokens` /
  `REQUIRED_CONFIGS` / kit change**; **no `schematic_status` /
  `schematic_file` promotion** (`S360-310` stays
  `cataloged_unverified`; `S360-100` stays `verified` from
  HW-008; `S360-100-BENCH-001` is **not** closed — the
  operator-attested Core `J4` pin order is **not** silkscreen /
  manufacturing evidence); **no COMPLIANCE-001 movement**; no
  Release-One change (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` /
  `stable`); no LED preview change
  (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`); no FanTRIAC
  change (`blocked` / `HW-005`). **No production-wide /
  multi-unit / oscilloscope-traced general `GPIO3` strap-pin
  boot-behaviour characterisation claim.** **No board-level
  mains-safety / installation-approval / creepage / clearance /
  thermal / EMI certification claim.** **No WebFlash import-readiness
  claim.** **No hardware release-readiness claim.** **No
  `RELEASE-RELAY-001` unblock claim.** **No `PACKAGE-RELAY-001`
  implementation.** No Relay product YAML. No WebFlash wrapper.
  No compile-only target.

- **2026-05-22 — `PACKAGE-RELAY-001` implementation (test +
  readiness reconciliation; no YAML rebind).** Implementation
  follow-up to `S360-310-BENCH-EVIDENCE-001` (PR #561). The
  FanRelay package
  [`packages/expansions/fan_relay.yaml`](packages/expansions/fan_relay.yaml)
  was already structurally correct (`fan_relay_pin: ${relay_pin}`
  line 27 inherits the parent Core abstract package binding, which
  post-001A resolves to the schematic-correct `GPIO3` per
  `S360-100-R4` `IO3 = Relay`); the override-hook comment block
  (lines 22–25), the `switch.platform: gpio` declaration with
  `pin: ${fan_relay_pin}` (line 38), `restore_mode:
  RESTORE_DEFAULT_OFF`, the `fan_auto_mode` global (lines 50–53),
  and the `fan_emergency_stop` script (lines 58–65) are preserved
  verbatim. **No YAML edit was required.** The reconciliation is
  the addition of
  [`tests/test_fan_relay_package.py`](tests/test_fan_relay_package.py)
  (12 stdlib-unittest cases) pinning the FanRelay package
  abstraction against future regression: the package exists and
  parses as YAML; `fan_relay_pin` defaults to `${relay_pin}` and
  is not a hardcoded GPIO; the package does not hard-code `GPIO3`
  / `GPIO4` / `GPIO10` or any other GPIO on an active (non-comment)
  line; the `fan_relay_switch` switch block uses platform `gpio`
  and binds `pin: ${fan_relay_pin}`; cross-check that the five
  non-voice Core abstract packages
  ([`sense360_core.yaml`](packages/hardware/sense360_core.yaml),
  [`sense360_core_ceiling.yaml`](packages/hardware/sense360_core_ceiling.yaml),
  [`sense360_core_mapping.yaml`](packages/hardware/sense360_core_mapping.yaml),
  [`sense360_core_poe.yaml`](packages/hardware/sense360_core_poe.yaml),
  [`sense360_core_wall.yaml`](packages/hardware/sense360_core_wall.yaml))
  bind `relay_pin: GPIO3`; the voice-variant Core packages
  ([`sense360_core_voice_ceiling.yaml`](packages/hardware/sense360_core_voice_ceiling.yaml),
  [`sense360_core_voice_wall.yaml`](packages/hardware/sense360_core_voice_wall.yaml))
  stay at the pre-001A `relay_pin: GPIO4` (deliberately out of
  scope); no FanRelay product YAML exists under `products/`; no
  `FanRelay` token exists in `config/webflash-builds.json`. Docs
  refreshed:
  [`docs/hardware/s360-310-r4-relay.md`](docs/hardware/s360-310-r4-relay.md)
  §Package YAML status PACKAGE-RELAY-001 investigation-outcome
  bullet extended with a PACKAGE-RELAY-001 implementation-outcome
  paragraph; new 2026-05-22 audit-log row appended to
  §HW-PINMAP-310-FOLLOWUP audit log recording the implementation.
  [`docs/hardware/package-readiness-matrix.md`](docs/hardware/package-readiness-matrix.md)
  `fan_relay.yaml` row + §`fan_relay.yaml` / S360-310 detail
  section refreshed to `package-implemented` +
  `reconciled-at-package-layer` with Allowed-action-now and
  Follow-up-owner chain refreshed.
  [`docs/hardware/firmware-package-mapping-audit.md`](docs/hardware/firmware-package-mapping-audit.md)
  Release-One package-stack `relay_pin` bullet appended with a
  PACKAGE-RELAY-001 implementation sub-paragraph. `UPCOMING_PR.md`
  Current queue summary (new bullet), Completed / merged PRs
  (this PR), Active / upcoming queue (PACKAGE-RELAY-001 item #6
  moved from "Evidence-ready" to "Merged"), and Recently uploaded
  evidence (this bullet) refreshed. `PACKAGE-RELAY-001` is now
  **implemented / reconciled at the package layer only**.
  **"Implemented / reconciled at the `PACKAGE-RELAY-001` package
  layer" does not mean: product-ready; WebFlash-ready;
  release-ready; compliance-cleared; safe for arbitrary mains
  installation; or verified across production batches.** The next
  Relay PR is `PRODUCT-RELAY-001`, which stays separately gated
  on product-layer compliance / mains-safety / installation /
  production-wide characterisation evidence. `PRODUCT-RELAY-001` /
  `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001`
  stay blocked behind PACKAGE-RELAY-001 → PRODUCT-RELAY-001.
  **No `products/**`, `products/webflash/**`, `config/**`,
  `scripts/**`, `.github/workflows/**`, `components/**`,
  `include/**`, `firmware/**`, `manifest.json`, or
  `firmware/sources.json` edit.** Only one `tests/**` addition:
  `tests/test_fan_relay_package.py`. The
  `tests/test_core_abstract_bus.py` scaffold from 001A / 001C is
  preserved verbatim. No `webflash_build_matrix` flip; no
  `artifact_name` / `webflash_wrapper` / `config_string` /
  `release_one_required_configs` / `lifecycle_statuses` /
  `canonical_modules` / `canonical_power` / `forbidden_tokens` /
  `REQUIRED_CONFIGS` / kit change; no `schematic_status` /
  `schematic_file` promotion (`S360-310` stays
  `cataloged_unverified`); no COMPLIANCE-001 movement; no
  Release-One change (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` /
  `stable`); no LED preview change (`Ceiling-POE-VentIQ-RoomIQ-LED`
  / `preview`); no FanTRIAC change (`blocked` / `HW-005`).
  `S360-100-BENCH-001` is **not** closed; `HW-PINMAP-311-FOLLOWUP`,
  `HW-PINMAP-312-FOLLOWUP`, and `HW-PINMAP-320-FOLLOWUP` are not
  closed. **No board-level mains-safety / installation-approval /
  creepage / clearance / thermal / EMI certification claim.** No
  Relay product YAML. No WebFlash wrapper. No compile-only
  target. No release artifact / tag / checksum / build-info
  manifest.

- **2026-05-21 — `S360-310-BENCH-001` Relay bench evidence-capture
  **checklist** added (no physical artifacts supplied).** Docs /
  evidence-capture-checklist-only follow-up to
  `PACKAGE-RELAY-001-READINESS-REFRESH` (PR #559). New top-line
  §`S360-310-BENCH-001 — Relay bench evidence` section added to
  [`docs/hardware/s360-310-r4-relay.md`](docs/hardware/s360-310-r4-relay.md)
  as the canonical bench-side / silkscreen-side / harness-side /
  BOM-side / load-contact-side companion to the schematic-side
  reconciliation tables. The section enumerates ten
  `PACKAGE-RELAY-001` hardware-evidence rows against a populated
  `S360-310-R4` + `S360-100-R4` pair (S360-100 Core `J4` silkscreen /
  pin-1 orientation; S360-310 Relay `J2` 1-to-3 pin order; S360-310
  Relay `J1` `NO` / `COM` / `NC` mapping; Core `J4` ↔ Relay `J2`
  harness identity / straight-through or keyed; `K1` BOM identity /
  manufacturer / part number; `K1` contact-current rating; expected
  controlled load type; relay boot state with `S360-100-R4` +
  `S360-310-R4` attached; ESP32-S3 `GPIO3` strap-pin boot
  characterisation generalisation status; Relay load / contact proof
  result). Every row carries the required-artifact + current-status
  + captured-value + source/note + still-blocks-PACKAGE-RELAY-001
  columns required by the task brief. **No physical bench,
  silkscreen, harness, BOM, load-contact, or strap-pin
  boot-behaviour evidence has been supplied for this record.** Every
  one of the ten rows stays `pending — bench evidence required`; no
  operator, no review date, no observed silkscreen pin-1 marks, no
  harness conductor-by-conductor trace, no `K1` part-number reading,
  no coil-drive scope capture, no contact-side continuity
  measurement, no oscilloscope-traced ESP32-S3 `GPIO3` strap-state
  capture is on file. The pair-scoped operator boot-OK observation
  in [`docs/hardware/core-abstract-bus-001c-rebind-plan.md`](docs/hardware/core-abstract-bus-001c-rebind-plan.md)
  decisions #16 / #17 is cross-referenced for completeness and is
  **not** promoted to a generic claim about ESP32-S3 `GPIO3`
  strap-pin boot behaviour (the row that would generalise it stays
  `pending — bench characterisation required (general claim, not
  pair-scoped)`). The
  [`docs/hardware/package-readiness-matrix.md`](docs/hardware/package-readiness-matrix.md)
  `fan_relay.yaml` row + §`fan_relay.yaml` / S360-310 detail
  Follow-up owner chain is refreshed to insert `S360-310-BENCH-001`
  (this PR) between `PACKAGE-RELAY-001-READINESS-REFRESH` (PR #559)
  and the next S360-310 bench-evidence-capture slice that actually
  commits artifacts. New 2026-05-21 audit-log row added to
  [`docs/hardware/s360-310-r4-relay.md`](docs/hardware/s360-310-r4-relay.md)
  §HW-PINMAP-310-FOLLOWUP audit log recording the scope, files
  inspected, and outcome of this PR. **`PACKAGE-RELAY-001` stays
  blocked at the evidence layer.** **No `packages/**` edit** (
  [`packages/expansions/fan_relay.yaml`](packages/expansions/fan_relay.yaml)
  unchanged; the five non-voice Core abstract packages stay at the
  post-001A `relay_pin: GPIO3` value; the voice-variant Core packages
  stay at pre-001A `relay_pin: GPIO4`, out of scope); **no
  `products/**` or `products/webflash/**` edit**; **no `config/**`
  edit** (
  [`config/hardware-catalog.json`](config/hardware-catalog.json),
  [`config/product-catalog.json`](config/product-catalog.json),
  [`config/webflash-builds.json`](config/webflash-builds.json),
  [`config/webflash-compatibility.json`](config/webflash-compatibility.json),
  [`config/firmware-combination-matrix.json`](config/firmware-combination-matrix.json),
  [`config/kit-intent-matrix.json`](config/kit-intent-matrix.json),
  [`config/compile-only-targets.json`](config/compile-only-targets.json),
  and [`config/compile-only-candidates.json`](config/compile-only-candidates.json)
  all byte-identical); **no `scripts/**` / `.github/workflows/**`
  / `components/**` / `include/**` / `firmware/**` /
  `manifest.json` / `firmware/sources.json` / `tests/**` edit**
  (the
  [`tests/test_core_abstract_bus.py`](tests/test_core_abstract_bus.py)
  scaffold from 001C / 001A is preserved verbatim and not extended);
  **no `webflash_build_matrix` flip**; **no `artifact_name` /
  `webflash_wrapper` / `config_string` /
  `release_one_required_configs` / `lifecycle_statuses` /
  `canonical_modules` / `canonical_power` / `forbidden_tokens` /
  `REQUIRED_CONFIGS` / kit change**; **no `schematic_status` /
  `schematic_file` promotion** (`S360-310` stays
  `cataloged_unverified`; `S360-100` stays `verified` from HW-008);
  **no COMPLIANCE-001 movement**; no Release-One change
  (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`); no LED
  preview change (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`); no
  FanTRIAC change (`blocked` / `HW-005`). **No claim of Relay load /
  contact / `K1` rating proof.** No claim that `PACKAGE-RELAY-001`
  / `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001`
  / `WF-IMPORT-RELAY-001` is implementation-ready. No
  `PACKAGE-RELAY-001` implementation. No Relay product YAML. No
  WebFlash wrapper. No compile-only target for FanRelay. No release
  artifact / tag / checksum / build-info manifest. Validation suite
  (`python3 tests/validate_configs.py`, `python3
  scripts/validate_compile_targets.py --metadata-only`, `python3
  tests/test_core_abstract_bus.py`, `python3
  tests/test_compile_targets.py`, `python3
  tests/test_compile_expansion_candidates.py`, `python3
  tests/test_firmware_combination_matrix.py`, `python3
  tests/test_firmware_build_gap_report.py`, `python3
  tests/test_kit_intent_matrix.py`, `python3
  tests/validate_webflash_builds.py`, `python3 -m unittest
  discover -s tests -p "test_*.py"`) all pass.
- **2026-05-21 — `PACKAGE-RELAY-001-READINESS-REFRESH` consolidated
  readiness re-evaluation of `PACKAGE-RELAY-001` after
  `CORE-ABSTRACT-BUS-001C` (PR #557) and `CORE-ABSTRACT-BUS-001A`
  (PR #558).** Docs / evidence / readiness only. No new external
  evidence beyond the post-001A / 001C repo state. The refresh re-checked
  the `PACKAGE-RELAY-001` blocker set against the live YAML
  ([`packages/expansions/fan_relay.yaml`](packages/expansions/fan_relay.yaml)
  `fan_relay_pin: ${relay_pin}` line 27 unchanged; the five non-voice
  Core abstract packages all bind `relay_pin: GPIO3`;
  [`packages/expansions/comfort_ceiling.yaml`](packages/expansions/comfort_ceiling.yaml)
  `comfort_ceiling_als_int_pin: GPIO47`;
  [`packages/expansions/gpio_expander_sx1509.yaml`](packages/expansions/gpio_expander_sx1509.yaml)
  `sx1509_interrupt_pin: GPIO17`;
  [`packages/hardware/sense360_core_mapping.yaml`](packages/hardware/sense360_core_mapping.yaml)
  `expander_int_pin: GPIO17`), live tests
  ([`tests/test_core_abstract_bus.py`](tests/test_core_abstract_bus.py)
  `RelayPinRebindTests` / `MainRelaySwitchBindingTests` /
  `NoSubstitutionCollisionTests` / `ComfortCeilingAlsIntTests` /
  `ExpanderIntPinTests` / `SX1509InterruptPinTests` /
  `PirSensorPinTests` / `RoomIQHiLinkUartTests` /
  `RoomIQSen0609UartTests`), and the operator-decision evidence in
  [`docs/hardware/core-abstract-bus-001c-rebind-plan.md`](docs/hardware/core-abstract-bus-001c-rebind-plan.md)
  decisions #16 / #17 (pair-scoped boot-OK observation) / #19
  (connector / harness accepted for planning record only). New top-line
  section §`PACKAGE-RELAY-001 readiness refresh after
  CORE-ABSTRACT-BUS-001C / 001A` added to
  [`docs/hardware/s360-310-r4-relay.md`](docs/hardware/s360-310-r4-relay.md)
  containing a readiness table (blocker × previous state × current
  state after #557/#558 × evidence source × still blocks
  PACKAGE-RELAY-001? × what unblocks it) over eleven enumerated
  blockers. New 2026-05-21 audit-log row added to the same doc's
  §HW-PINMAP-310-FOLLOWUP audit log. `fan_relay.yaml` row in
  [`docs/hardware/package-readiness-matrix.md`](docs/hardware/package-readiness-matrix.md)
  table refreshed; §`fan_relay.yaml` / S360-310 detail section
  refreshed; Follow-up owner chain refreshed to point at this PR
  and the recommended S360-310 bench-evidence-capture slice.
  Release-One package stack §systemic Core-vs-schematic mismatch
  `relay_pin: GPIO4` bullet in
  [`docs/hardware/firmware-package-mapping-audit.md`](docs/hardware/firmware-package-mapping-audit.md)
  appended with a 2026-05-21 update sub-bullet recording the
  post-001A `relay_pin: GPIO3` state. **Substitution-layer blockers
  recorded as resolved by PR #557 / PR #558:** the `GPIO3` collision;
  the `relay_pin: IO3` vs `GPIO4` vs `GPIO10` disagreement; the
  pin-pinning regression scaffold for `relay_pin`; the structural
  correctness check on `fan_relay.yaml`. **Hardware-evidence blockers
  that still block `PACKAGE-RELAY-001`:** S360-100 Core `J4`
  silkscreen / pin-1 orientation; S360-310 module-side `J2` / `J1`
  silkscreen / pin-1 orientation; `J1` `NO` / `COM` / `NC` mapping;
  Core ↔ module 3-pin harness identity; `K1` BOM identity (part
  number, coil voltage, contact configuration, isolation rating);
  `K1` contact-current rating; Relay load / contact proof
  (coil-drive waveform, `K1` switching behaviour, load-side
  continuity through `J1` `NO` / `COM` / `NC` contacts, optionally
  `Q1` MMBT3904 SOA characterisation under actual `K1` coil-current
  draw); general (not pair-scoped) ESP32-S3 `GPIO3` strap-pin
  boot-behaviour bench characterisation. **Recommended conservative
  next PR:** an `S360-310` bench-evidence-capture slice
  (`HW-ASSETS-S360-310-BENCH-001` / `S360-310-BENCH-001` or sibling)
  committing operator-attributed silkscreen captures of module-side
  `J2` / module-side `J1` (with `NO` / `COM` / `NC` labels where
  present) / Core-side `J4`, the Core ↔ module harness inspection
  trace, the `K1` BOM identity, the coil-drive waveform capture,
  and the load-side continuity trace. The general ESP32-S3 `GPIO3`
  strap-pin boot-behaviour bench characterisation may land in the
  same slice or as a sibling slice against `S360-100-BENCH-001`.
  **No `packages/**` edit** (the `fan_relay.yaml` package is
  structurally correct post-001A; the Core abstract packages stay
  at the 001A / 001C values; the voice-variant Core packages stay
  at pre-001A `relay_pin: GPIO4`, out of scope); **no `products/**`
  or `products/webflash/**` edit**; **no `config/**` edit** (
  [`config/hardware-catalog.json`](config/hardware-catalog.json),
  [`config/product-catalog.json`](config/product-catalog.json),
  [`config/webflash-builds.json`](config/webflash-builds.json),
  [`config/webflash-compatibility.json`](config/webflash-compatibility.json),
  [`config/firmware-combination-matrix.json`](config/firmware-combination-matrix.json),
  [`config/kit-intent-matrix.json`](config/kit-intent-matrix.json),
  [`config/compile-only-targets.json`](config/compile-only-targets.json),
  and [`config/compile-only-candidates.json`](config/compile-only-candidates.json)
  all byte-identical); **no `scripts/**` / `.github/workflows/**`
  / `components/**` / `include/**` / `firmware/**` /
  `manifest.json` / `firmware/sources.json` / `tests/**` edit**
  (the `tests/test_core_abstract_bus.py` scaffold from 001C / 001A
  is preserved verbatim and not extended); **no `webflash_build_matrix`
  flip**; **no `artifact_name` / `webflash_wrapper` /
  `config_string` / `release_one_required_configs` /
  `lifecycle_statuses` / `canonical_modules` / `canonical_power`
  / `forbidden_tokens` / `REQUIRED_CONFIGS` / kit change**; **no
  `schematic_status` / `schematic_file` promotion** (`S360-310`
  stays `cataloged_unverified`; `S360-100` stays `verified` from
  HW-008); **no COMPLIANCE-001 movement**; no Release-One change
  (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`); no LED
  preview change (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`);
  no FanTRIAC change (`blocked` / `HW-005`). **No claim of Relay
  load / contact / `K1` rating proof.** No claim that
  `PACKAGE-RELAY-001` / `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001`
  / `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001` is
  implementation-ready. No `PACKAGE-RELAY-001` implementation.
  No Relay product YAML. No WebFlash wrapper. No compile-only
  target for FanRelay. The pair-scoped boot-OK observation in
  [`docs/hardware/core-abstract-bus-001c-rebind-plan.md`](docs/hardware/core-abstract-bus-001c-rebind-plan.md)
  decisions #16 / #17 is **not** promoted to a generic claim about
  ESP32-S3 `GPIO3` strap-pin boot behaviour. Validation suite
  (`python3 tests/validate_configs.py`, `python3
  scripts/validate_compile_targets.py --metadata-only`, `python3
  tests/test_core_abstract_bus.py`, `python3
  tests/test_compile_targets.py`, `python3
  tests/test_compile_expansion_candidates.py`, `python3
  tests/test_firmware_combination_matrix.py`, `python3
  tests/test_firmware_build_gap_report.py`, `python3
  tests/test_kit_intent_matrix.py`, `python3
  tests/validate_webflash_builds.py`, `python3 -m unittest
  discover -s tests -p "test_*.py"`) all pass.
- **2026-05-21 — `CORE-ABSTRACT-BUS-001C-REBIND-PLAN-001` recorded
  schematic-backed `CORE-ABSTRACT-BUS-001C` rebind plan (docs-only
  planning record).** Provenance: the committed `S360-100-R4` Core
  schematic
  ([`docs/hardware/schematics/S360-100-R4.pdf`](docs/hardware/schematics/S360-100-R4.pdf))
  and `S360-200-R4` RoomIQ schematic
  ([`docs/hardware/schematics/S360-200-R4.pdf`](docs/hardware/schematics/S360-200-R4.pdf)),
  plus operator review of the committed schematic screenshots. New
  doc added at
  [`docs/hardware/core-abstract-bus-001c-rebind-plan.md`](docs/hardware/core-abstract-bus-001c-rebind-plan.md)
  records: an evidence summary; schematic net tables for Core `J10`
  and RoomIQ `J6` reconciled in straight-through, pin-1-to-pin-1
  order; nineteen operator-confirmed decisions covering schematic
  source provenance, J10 / J6 net order, harness intent, UART
  directionality (ESP32 / Core-perspective `Hi-Link_TX` /
  `Hi-Link_RX` / `SEN0609_TX` / `SEN0609_RX`), baud rates
  (`Hi-Link = 256000`, `SEN0609 = 115200`), S360-300 LED ring
  ownership (`GPIO38 / LED_DATA`, owned by the LED ring package),
  retirement of the generic Core `status_led_pin`, retention of
  `GPIO46 / GP_Fan_Status_Led` as `fan_status_led_pin`,
  AirIQ-only classification of `GPIO7 / AirQ_Status_Led` and
  `GPIO8 / AirQ_Led`, VentIQ having no dedicated Core-driven LED /
  status line, retirement of generic `expansion_gpio*` in favour
  of function-specific substitutions, identity of `out(gpio6)` as
  the SEN0609 output pin, canonical naming as
  `roomiq_sen0609_output_pin`, operator-confirmed `GPIO3` boot OK
  with `S360-310` Relay attached (scoped to the populated pair
  under operator review), Relay off / not energized at boot,
  `S360-310` revision accepted as R4 for this planning record (no
  `schematic_status` promotion), and Relay connector / harness
  accepted as straight-through / keyed correctly for this planning
  record (full bench-side harness identity / `K1` BOM / contact
  rating / approvals remain owed); the proposed `001C` substitution
  map (RoomIQ UARTs, RoomIQ GPIO, expander interrupt, LED / status
  decisions, expansion GPIO retirement, Relay / 001A dependency);
  implementation readiness classification; remaining caveats; and a
  validation plan. Updated
  [`docs/hardware/core-abstract-bus-reconciliation.md`](docs/hardware/core-abstract-bus-reconciliation.md)
  with a new audit-log section
  `### 2026-05-21 — CORE-ABSTRACT-BUS-001C rebind plan evidence`
  that links to the new rebind plan doc and refreshes the
  precondition state for `001C` (preconditions #2 RoomIQ / AirIQ /
  VentIQ rebind plan, #3 expansion-GPIO retirement decision, and
  #4 ESP32-S3 `GPIO3` strap-pin boot behaviour for the populated
  pair are closed at the planning layer; preconditions #1
  `S360-100-BENCH-001` silkscreen / harness / continuity-trace
  evidence at the bench-side layer, #5
  `tests/test_core_abstract_bus.py` scaffold, and #6
  non-Release-One product re-validation pass remain owed and land
  with the first implementation slice). Updated this file
  (`UPCOMING_PR.md`) with the queue-summary bullet above and the
  refresh to the active-queue `CORE-ABSTRACT-BUS-001C` entry. **No
  package, product, WebFlash, build, release, compliance, JSON
  catalog, test, script, workflow, component, include, firmware,
  manifest, checksum, build-info manifest, or artifact edits;** no
  `schematic_status` / `schematic_file` promotion (`S360-100`
  stays `verified` from HW-008; `S360-310` stays
  `cataloged_unverified`); no `webflash_build_matrix` flip; no
  `artifact_name` / `webflash_wrapper` / `config_string` added; no
  `release_one_required_configs` / `lifecycle_statuses` /
  `canonical_modules` / `canonical_power` / `forbidden_tokens` /
  `REQUIRED_CONFIGS` / kit change; no COMPLIANCE-001 movement; no
  Release-One change (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` /
  `stable`); no LED preview change
  (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`); no FanTRIAC
  change (`blocked` / `HW-005`); no Relay package completion
  claim; no Relay load / `K1` contact rating proof claim; no
  `RELEASE-RELAY-001` unblock claim; no WebFlash import-readiness
  claim; no hardware stable / release readiness claim.
  `CORE-ABSTRACT-BUS-001C` is now **implementation-plannable** at
  the planning layer; implementation still requires a scoped
  YAML / test PR per
  [`docs/hardware/core-abstract-bus-001c-rebind-plan.md` §Implementation readiness classification](docs/hardware/core-abstract-bus-001c-rebind-plan.md#implementation-readiness-classification).
  `CORE-ABSTRACT-BUS-001A` (the `relay_pin: GPIO3` slice) stays
  blocked behind `001C` implementation per the `GPIO3` collision
  in
  [`docs/hardware/core-abstract-bus-reconciliation.md` §GPIO collision matrix](docs/hardware/core-abstract-bus-reconciliation.md#gpio-collision-matrix).
  `PACKAGE-RELAY-001` / `PRODUCT-RELAY-001` /
  `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` /
  `WF-IMPORT-RELAY-001` stay blocked behind `001A`.
- **2026-05-21 — `PACKAGE-POE-410-001` package-header cleanup
  landed under Path B / PR #538 (limited implementation).** No
  new external evidence beyond `HW-BOM-ASSETS-002` / PR #535;
  the cleanup consumes that BOM ingest. Header comments-only
  edit to
  [`packages/hardware/power_poe.yaml`](packages/hardware/power_poe.yaml)
  (lines 1–58) removing the disproved
  `Ag9712M, Silvertel Ag9700, or similar` whole-module PoE
  hint and naming the BOM-confirmed S360-410-R4 discrete PoE
  topology: `LAN_CON1 LPJ4112CNL` (RJP-003TC1-style) RJ45 +
  magnetics; `U1 TPS2378DDAR` (HSOIC-8) PoE PD controller;
  `U2 TX4138` (ESOIC-8) buck converter; `DCDC1 F0505S-2WR2`
  (SIP-7) isolated 5V/5V DC/DC, with `AM1D-0505S-NZ` explicitly
  reclassified as a schematic-annotation-only alternate **not**
  the BOM-populated part; `D1 SMAJ58A` TVS; `D2 SS510`
  Schottky catch; `D3` Green status LED; `L1 33uH` buck
  inductor; `R1..R9`, `C1..C8`, and the `J3` `+5VP` / `GND`
  output header. IEEE 802.3af / Class 0 / input / output /
  protection ratings reclassified under explicit
  "Vendor-datasheet typicals (NOT BOM-confirmed and NOT
  compliance evidence)" heading. Header now explicitly
  restates that the package is logical / diagnostic only (no
  GPIO / I2C / UART / SPI / DAC runtime binding; emits
  diagnostic-only template sensors) and that this PR makes no
  release, WebFlash, product-catalog, or schematic-status
  claim. **Runtime YAML behavior unchanged** — `substitutions`,
  `globals`, `sensor`, `text_sensor`, `binary_sensor`,
  `logger`, and `esphome: on_boot:` blocks from
  `substitutions:` onward stay byte-identical to PR #517 /
  PR #526 / PR #535 state (SHA256 of the
  `substitutions:`-onward block unchanged before and after
  this PR). **No `config/**`, `products/**`,
  `products/webflash/**`, `tests/**`, `scripts/**`,
  `.github/workflows/**`, `components/**`, `include/**`,
  `firmware/**`, `manifest.json`, `firmware/sources.json`,
  `docs/compliance/**`, `config/hardware-catalog.json`,
  `config/product-catalog.json`, `config/webflash-builds.json`,
  or `config/webflash-compatibility.json` edit. No
  `schematic_status` / `schematic_file` promotion (the
  `S360-410` row in `config/hardware-catalog.json` stays
  byte-identical; `schematic_status: cataloged_unverified`
  unchanged; `schematic_file` not set). No COMPLIANCE-001
  movement (PoE is SELV; `S360-410` is **not** in scope for
  COMPLIANCE-001). No Release-One PoE
  `"schematic verification pending"` caveat closure
  (preserved verbatim). No Release-One / LED preview /
  FanTRIAC change. No `REQUIRED_CONFIGS` / kit change. No
  IEEE 802.3af / 802.3at / isolation / Hi-pot /
  earth-continuity / leakage / thermal / EMI / EMC / CE /
  UKCA / FCC / UL / LVD / RoHS / IEC claim. **Effect on
  downstream slices.** `PACKAGE-POE-410-001`'s package-header
  cleanup component is now landed; the residual coordinated
  work (the `S360-410` `schematic_status: verified` JSON-only
  PR, HW-002 OQ#6 / `S360-100-BENCH-001` J2-harness identity
  closure, and the Release-One PoE caveat-closure PR) plus
  silkscreen / PCB / creepage / clearance / bench / thermal /
  EMI / PoE-link-up / isolation evidence remain owed.
  `PRODUCT-POE-410-001` / `WEBFLASH-POE-410-001` /
  `RELEASE-POE-410-001` / `WF-IMPORT-POE-410-001` (cross-repo)
  stay blocked behind those preconditions.
- **2026-05-20 — `PACKAGE-POWER-400-001` package-header cleanup
  landed under Path B / PR #537 (limited implementation).** No
  new external evidence beyond `HW-BOM-ASSETS-002` / PR #535;
  the cleanup consumes that BOM ingest. Header comments-only
  edit to
  [`packages/hardware/power_240v.yaml`](packages/hardware/power_240v.yaml)
  (lines 1–42) replacing the disproved `HLK-PM01 or similar`
  AC/DC part hint with the BOM-confirmed `PS1 = HLK-5M05
  (HI-LINK)` part identity, naming the BOM-confirmed populated
  mains-side protection (`F1 A250-1200`, `RV1 10D391K`,
  `C1 470nF`) and connectors (`J1` WAGO 2601-3103,
  `J2` JST SH `SM02B-SRSS-TB(LF)(SN)`), reclassifying input /
  output / isolation / protection ratings as vendor-datasheet
  typicals (not BOM-confirmed and not compliance evidence),
  removing the misleading `1A recommended` AC-input fusing
  line, and adding an explicit `COMPLIANCE-001` OPEN reminder.
  **Runtime YAML behavior unchanged** — `substitutions`,
  `globals`, `sensor`, `text_sensor`, `binary_sensor`, and
  `logger` blocks from line 44 onward stay byte-identical to
  PR #515 / PR #520 / PR #535 state. **No `config/**`,
  `products/**`, `products/webflash/**`, `tests/**`,
  `scripts/**`, `.github/workflows/**`, `components/**`,
  `include/**`, `firmware/**`, `manifest.json`,
  `firmware/sources.json` edit. No `schematic_status` /
  `schematic_file` promotion (the catalog
  `description: "Mains to 5V using HLK-5M05."` at
  [`config/hardware-catalog.json`](config/hardware-catalog.json)
  line 109 was already BOM-consistent and is unchanged); no
  schematic-PDF correction (the `PS1 = HLK-10M05` value-field
  discrepancy stays recorded but is not corrected; correction
  owed to a separate later HW-ASSETS-400 follow-up). No
  COMPLIANCE-001 movement (last re-check PR #506). No
  Release-One / LED preview / FanTRIAC change. No
  `REQUIRED_CONFIGS` / kit change. No CE / UKCA / FCC / UL /
  LVD / EMC / RoHS / IEC claim. **Effect on downstream
  slices.** `PACKAGE-POWER-400-001`'s package-header cleanup
  component is now landed; the residual coordinated work (the
  `S360-400` `schematic_status: verified` JSON-only PR,
  additionally gated on the schematic-side PDF correction) plus
  `COMPLIANCE-001` `S360-400` slice closure plus silkscreen /
  PCB / creepage / clearance / bench / thermal / EMI evidence
  remain owed. `PRODUCT-POWER-400-001` / `WEBFLASH-POWER-400-001`
  / `RELEASE-POWER-400-001` / `WF-IMPORT-POWER-400-001`
  (cross-repo) stay blocked behind those preconditions. The
  row class in
  [`docs/hardware/package-readiness-matrix.md`](docs/hardware/package-readiness-matrix.md#power_240vyaml--s360-400)
  stays `schematic-evidence-pending` +
  `needs-package-reconciliation` + `timing/compliance-pending`
  (compliance-gated). Outcome recorded at
  [`docs/hardware/s360-400-r4-power.md` §2026-05-20 — PACKAGE-POWER-400-001 package-header cleanup](docs/hardware/s360-400-r4-power.md#2026-05-20--package-power-400-001-package-header-cleanup-bom-confirmed-part-identity-in-header-ratings-softened-downstream-slices-still-blocked)
  and
  [`docs/cleanup-audit.md` §PACKAGE-POWER-400-001 update (2026-05-20 — Path B package-header cleanup)](docs/cleanup-audit.md#package-power-400-001-update-2026-05-20--path-b-package-header-cleanup).
- **S360-200-R4 BOM** — ingested by **HW-BOM-ASSETS-001**
  (PR #533) as `b35d4654-S360200R4_BOM.xlsx` (11,177 bytes; SHA256
  `8b9da0fc669091b6015b6af09408edf1e5dc90a4e0aaf8557047c28e9a7e4ae2`).
  **Retained-but-not-committed** under the current
  [Hardware Artifact Policy](docs/hardware/hardware-artifact-policy.md)
  per-board decision — the `.xlsx` itself is **not** added to
  `git`. Inventoried (filename, size, SHA256, component
  summary) in the new curated artifact index at
  [`docs/hardware/artifacts/S360-200-R4.md`](docs/hardware/artifacts/S360-200-R4.md).
  The S360-200 schematic PDF re-upload
  `5f56a627-S360200R4.pdf` (102,937 bytes; SHA256
  `395e9f6fb04573c5ad91ce065717743cc1aeca5e2187193bd075074526c5f3f7`)
  is **byte-identical** to the already-committed PDF at
  [`docs/hardware/schematics/S360-200-R4.pdf`](docs/hardware/schematics/S360-200-R4.pdf);
  no re-commit of the PDF was needed. Does **not** change
  `schematic_status` (already `verified` under HW-008); does
  **not** resolve the Core J10 vs RoomIQ J6 pin-order
  discrepancy; does **not** edit any package YAML, product
  YAML, or WebFlash wrapper.
- **S360-210-R4 BOM** — ingested by **HW-BOM-ASSETS-001**
  (PR #533) as `c551e467-S360210R4_BOM.xlsx` (11,966 bytes; SHA256
  `0b3dc2f73d6f71234170b4f0d0b95cd3231ca93218b80cc1d81e0e013477dd23`).
  **Retained-but-not-committed**; inventoried (filename, size,
  SHA256, component summary) in the new curated artifact index
  at
  [`docs/hardware/artifacts/S360-210-R4.md`](docs/hardware/artifacts/S360-210-R4.md).
  The S360-210 schematic PDF re-upload
  `9cd56b90-S360210R4.pdf` (152,475 bytes; SHA256
  `4bf05bdab53aa1b083eb30652152da75c03357f41a8a384efae19e90fd58c922`)
  is **byte-identical** to the already-committed PDF at
  [`docs/hardware/schematics/S360-210-R4.pdf`](docs/hardware/schematics/S360-210-R4.pdf).
  The BOM surfaces two BOM-vs-doc reconciliation candidates
  owed to a follow-up: (1) `U2 = SFA40-D-Rx` populated
  on-board (the standalone reference doc describes `SFA40` as
  a connector); (2) `U6 = LMV358B-SR` op-amp not enumerated in
  the standalone reference doc. Does **not** change
  `schematic_status` (already `verified`); does **not** add
  `AirIQ` to any config string, product, or build matrix;
  does **not** change the `airiq ↔ ventiq` mutex; does
  **not** resolve HW-002 Open Question #4 (`AirQ_Led` /
  `AirQ_Status_Led` reuse).
- **S360-100-R4 BOM and PDF re-upload (byte-identical)** —
  byte-identical re-upload confirmed by **HW-BOM-ASSETS-001**
  (PR #533): `df6da128-S360100R4_BOM.xlsx` (12,543 bytes;
  SHA256
  `e289f135a2c88dd747689c70075e2f1cf49906f4bda8b4c4abad67d0dad961fc`)
  matches the BOM already inventoried under HW-ASSETS-002, and
  `f5e98864-S360100R4.pdf` (849,828 bytes; SHA256
  `173a60792703923c69639772c4e23531faedf8a88e5147656d133a6317acf435`)
  matches the committed schematic PDF. **No new S360-100
  evidence is added.** S360-100-BENCH-001 stays
  `pending — bench/manufacturing evidence required`; HW-002
  Open Questions stay open. Confirmation subsection added to
  [`docs/hardware/artifacts/S360-100-R4.md`](docs/hardware/artifacts/S360-100-R4.md)
  Checksums section.
- **S360-400-R4 BOM** — ingested by **HW-BOM-ASSETS-002**
  (PR #535) as `95878198-S360400R4_BOM.xlsx` (10,987 bytes;
  SHA256
  `bb59f56da11fe83f83b2547322af4e594b658384ade9f06267af367ffb603a1d`).
  **Retained-but-not-committed** under the current
  [Hardware Artifact Policy](docs/hardware/hardware-artifact-policy.md)
  per-board decision — the `.xlsx` itself is **not** added to
  `git`. Inventoried (filename, size, SHA256, full 9-row
  component table) in the appended
  `## HW-BOM-ASSETS-002 BOM ingest (2026-05-20)` section of the
  existing curated artifact index
  [`docs/hardware/artifacts/S360-400-R4.md`](docs/hardware/artifacts/S360-400-R4.md).
  The BOM `PS1` row (`Value: HLK-5M05` / `MFR#: HLK-5M05` /
  `Manufacturer: HI-LINK` / footprint
  `greencharge-footprints:CONV_HLK-5M05`) **confirms** the
  catalog `description: "Mains to 5V using HLK-5M05."` at
  `config/hardware-catalog.json` line 109 and **reclassifies**
  the three-way AC/DC part-identity disagreement recorded by
  HW-PINMAP-400-FOLLOWUP / PR #515 + PR #520: catalog
  `HLK-5M05` + BOM `HLK-5M05` = BOM/user-confirmed sourcing
  truth; schematic `PS1 = HLK-10M05` (committed PDF) =
  schematic-label discrepancy (committed PDF stays
  byte-identical; schematic-side correction owed to a later
  HW-ASSETS-400 follow-up); package header `HLK-PM01 or
  similar` (line 7 of
  [`packages/hardware/power_240v.yaml`](packages/hardware/power_240v.yaml))
  = disproved package-header comment text (cleanup deferred to
  `PACKAGE-POWER-400-001`; package YAML stays byte-identical
  to PR #515 / PR #520). Other BOM-confirmed component
  identities: `F1 A250-1200` (JDTfuse), `RV1 10D391K` (RUILON),
  `C1 470nF` THT X-cap (WALSON), `C5, C8 100uF` SMD
  electrolytic (KNSCHA), `C6 10u` 0603 (Chinocera), `C7 100n`
  0603 (CCTC), `J1` WAGO 2601-3103 1×3 vertical terminal
  block, `J2` JST SH `SM02B-SRSS-TB(LF)(SN)` 1×2. Per-component
  voltage / energy / safety-class / X-cap-class ratings beyond
  the BOM `MFR#` strings remain vendor-datasheet, silkscreen,
  bench, and EMI / EMC evidence. Does **not** change
  `schematic_status` (stays `cataloged_unverified`); does
  **not** edit the committed schematic PDF (the `HLK-10M05`
  value-field discrepancy is recorded but not corrected); does
  **not** edit any package YAML; does **not** close
  COMPLIANCE-001 `S360-400` slice; does **not** advance any
  `PACKAGE-POWER-400-001` / `PRODUCT-POWER-400-001` /
  `WEBFLASH-POWER-400-001` / `RELEASE-POWER-400-001` /
  `WF-IMPORT-POWER-400-001` implementation slice.
- **S360-410-R4 BOM and PDF re-upload (byte-identical)** —
  ingested by **HW-BOM-ASSETS-002** (PR #535) as
  `0de7679d-S360410R4_BOM.xlsx` (11,980 bytes; SHA256
  `b5f4bad842a930de03cd47327f477c21afcb82e4533a9d8be38b54990b38f285`).
  **Retained-but-not-committed**; inventoried (filename, size,
  SHA256, full 24-row component table) in the appended
  `## HW-BOM-ASSETS-002 BOM ingest (2026-05-20)` section of the
  existing curated artifact index
  [`docs/hardware/artifacts/S360-410-R4.md`](docs/hardware/artifacts/S360-410-R4.md).
  The accompanying `S360-410-R4.pdf` re-upload
  `7f920771-S360410R4.pdf` (975,137 bytes; SHA256
  `4a8b7a3b2a89006a9332eaa486743f687aaedc4b6bb807c6b25670f742ac2414`)
  is **byte-identical** to the already-committed PDF at
  [`docs/hardware/schematics/S360-410-R4.pdf`](docs/hardware/schematics/S360-410-R4.pdf);
  no re-commit of the PDF was needed. The BOM **confirms** the
  schematic-shown discrete PoE topology at the part-identity
  layer: `U1 = TPS2378DDAR(HSOIC-8)` (TI), `U2 = TX4138(ESOIC-8)`
  (XDS), `DCDC1 = F0505S-2WR2(SIP-7)` (EVISUN), and
  `LAN_CON1 = RJP-003TC1(LPJ4112CNL)` (Link-PP Intl Technology
  / `LPJ4112CNL`). **Reclassifies** the package-header / schematic
  disagreement recorded by HW-PINMAP-410-FOLLOWUP / PR #517 +
  PR #526: schematic discrete topology = BOM-confirmed sourcing
  truth; package-header `Ag9712M, Silvertel Ag9700, or similar`
  (line 6 of
  [`packages/hardware/power_poe.yaml`](packages/hardware/power_poe.yaml))
  = **disproved by BOM** (neither part appears anywhere in the
  BOM; cleanup deferred to `PACKAGE-POE-410-001`; package YAML
  stays byte-identical to PR #517 / PR #526);
  schematic-annotated `AM1D-0505S-NZ` = **schematic-annotation-only
  alternate not present in the BOM** (`F0505S-2WR2` EVISUN is
  the BOM-confirmed populated primary for `DCDC1`). PoE class
  declaration: BOM `R2 1.27k` (PANASONIC) is consistent with the
  schematic-recorded `Class=0 (0.44 to 12.95W)` programming;
  802.3af-only vs 802.3af/at-capable design intent stays open.
  Output rating: BOM `DCDC1 F0505S-2WR2` + BOM `R7 10.5k` /
  `R8 56.2k` feedback divider are consistent with the
  schematic-recorded 5 V → 5 V isolated output only; the
  package-header `or 3.3V DC` option is not schematic- or
  BOM-evidenced. Other BOM-confirmed component identities:
  `R1 24.9k` (EVER OHMS) DEN; `R3, R4 9.1k` (UNI-ROYAL) paired
  ILIM; `R5 0.03R` (YAGEO) RTN sense; `R7 10.5k` (KOA) `Rd` /
  `R8 56.2k` (FOJAN) `Rc` feedback divider; `L1 33uH`
  (Yanchuang); `D1 SMAJ58A` (Littelfuse) TVS; `D2 ss510` (MDD
  SS510C) Schottky; `D3 Green` (Orient); `C2 15uF` (Rubycon)
  CBULK; `C6 470u` (ROQANG) buck-output bulk; `C8 22u` (muRata)
  `+5VP` output bulk; `J3` JST `SM02B-SRSS-TB(LF)(SN)` 1×2
  Core-facing connector. Does **not** change `schematic_status`
  (stays `cataloged_unverified`); does **not** re-commit the
  byte-identical PDF; does **not** edit any package YAML; does
  **not** close HW-002 Open Question #6 / `S360-100-BENCH-001`
  J2-harness identity; does **not** close the Release-One PoE
  `"schematic verification pending"` caveat (preserved verbatim);
  does **not** advance any `PACKAGE-POE-410-001` /
  `PRODUCT-POE-410-001` / `WEBFLASH-POE-410-001` /
  `RELEASE-POE-410-001` / `WF-IMPORT-POE-410-001` (cross-repo)
  implementation slice. PoE is SELV; **not** in scope for
  COMPLIANCE-001.
- **Partial-batch deferral note (HW-BOM-ASSETS-001).** The
  HW-BOM-ASSETS-001 BOM batch is **partial**. Eight additional
  BOM `.xlsx` files (for `S360-211`, `S360-300`, `S360-310`,
  `S360-311`, `S360-312` (Fan_GP8403), `S360-320`, `S360-400`,
  and `S360-410`) were owed to a later `HW-BOM-ASSETS`
  follow-up PR. **`HW-BOM-ASSETS-002` / PR #535 (above)
  ingests two of the eight (`S360-400` and `S360-410`).** Until
  the next `HW-BOM-ASSETS` follow-up lands, the per-board
  `BOM missing` / `BOM cross-check missing` blocker wording
  for the remaining six boards remains the explicit, honest
  gate. Notable still-BOM-bound items (after HW-BOM-ASSETS-002):
  `PACKAGE-DAC-001` (GP8403 / MT3608 BOM cross-check),
  `PACKAGE-PWM-001` (4-channel topology BOM cross-check),
  `PACKAGE-TRIAC-001` (BT136S-600D / MOC3023M BOM
  cross-check; **does not unblock COMPLIANCE-001 or HW-005**
  even when that BOM lands), `PACKAGE-RELAY-001` (`K1` BOM
  identity), and the LED stable promotion (S360-300 BOM
  evidence is one of several inputs to operator flash proof /
  bench behaviour — landing the BOM **does not** by itself
  promote LED stable). `PACKAGE-POWER-400-001` and
  `PACKAGE-POE-410-001` are **no longer BOM-bound** after
  `HW-BOM-ASSETS-002` (each remains blocked on its other
  recorded preconditions; see active-queue entries above).
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
  `PACKAGE-POWER-400-001` investigation pass merged as **PR #520**
  re-checked every precondition and confirmed that none has been
  satisfied since the 2026-05-19 `HW-PINMAP-400-FOLLOWUP` re-check
  (PR #515): no BOM line item with manufacturer + part number +
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
- **No new evidence committed for `PRODUCT-POWER-400-001`
  preconditions (2026-05-19 re-check).** The 2026-05-19
  `PRODUCT-POWER-400-001` investigation pass (merged as **PR #521**)
  re-checked
  every precondition and confirmed that none has been satisfied
  since the 2026-05-19 `PACKAGE-POWER-400-001` re-check (PR #520):
  `PRODUCT-POWER-400-001` investigation pass merged as **PR #521**
  re-checked every precondition and confirmed that none has been
  satisfied since the 2026-05-19 `PACKAGE-POWER-400-001` re-check
  (PR #520):
  the `PACKAGE-POWER-400-001` implementation slice has not landed
  (only the docs-only investigation pass merged as PR #520; the
  package YAML header reconciliation, the catalog `description`
  reconciliation, the `S360-400` `schematic_status: verified` JSON
  promotion, and the BOM citation that PR #520 enumerated as the
  required atomic slice all remain owed); no BOM line item with
  manufacturer + part number + revision for `PS1` is committed
  (so the three-way catalog `HLK-5M05` vs package header
  `HLK-PM01 or similar` vs schematic `PS1 = HLK-10M05`
  disagreement stays unresolved); no BOM lines for
  `F1 A250-1200` / `RV1 10D391K` / `C1 470nF` / `C5..C8` / `J1` /
  `J2` are committed; no separate JSON-only PR for `S360-400`
  `schematic_status` promotion has landed
  (`config/hardware-catalog.json` line 110 stays
  `schematic_status: cataloged_unverified` with no
  `schematic_file`; `tests/test_hardware_catalog.py:53`
  `EXPECTED_STILL_UNVERIFIED_SKUS = frozenset({"S360-320",
  "S360-400"})` actively enforces this state); no `COMPLIANCE-001`
  `S360-400` slice mains-voltage UK / EU sign-off has landed
  since PR #506; no silkscreen / PCB / creepage / clearance /
  bench / thermal / EMI evidence is committed for `S360-400-R4`;
  and no product-onboarding approval has been recorded against
  `PRODUCT-POWER-400-001`. No S360-400-explicit / `PWR`-bearing
  WebFlash-shippable product YAML exists under
  [`products/`](products/) or
  [`products/webflash/`](products/webflash/); the four
  `legacy-compatible` `*-pwr` Core variants
  (`sense360-core-c-pwr.yaml` / `sense360-core-w-pwr.yaml` /
  `sense360-core-v-c-pwr.yaml` / `sense360-core-v-w-pwr.yaml`)
  stay `legacy-compatible` / `webflash_build_matrix: false`; no
  S360-400-specific product is added to
  [`config/product-catalog.json`](config/product-catalog.json);
  no `PWR` build is added to
  [`config/webflash-builds.json`](config/webflash-builds.json);
  `PWR` stays reserved in
  [`config/webflash-compatibility.json`](config/webflash-compatibility.json)
  `canonical_power` without any `webflash_build_matrix: true`
  consumer. The next evidence-bearing PR against
  `PRODUCT-POWER-400-001` should appear when
  `PACKAGE-POWER-400-001` implementation lands (which itself
  requires BOM + the `S360-400` `schematic_status: verified` JSON
  PR + the package header reconciliation + the catalog
  `description` reconciliation as the recorded coordinated
  slice), the `COMPLIANCE-001` `S360-400` slice closes, and
  product-onboarding approval is granted. See
  `docs/product-readiness-matrix.md` §PWR-240V / S360-400,
  `docs/webflash-exposure-readiness-matrix.md` §Power / S360-400
  WebFlash posture,
  `docs/release-artifact-readiness-matrix.md` §Power / S360-400
  release posture, and `docs/cleanup-audit.md`
  §`PRODUCT-POWER-400-001 update`.
- **No new evidence committed for `WEBFLASH-POWER-400-001`
  preconditions (2026-05-19 re-check).** The 2026-05-19
  `WEBFLASH-POWER-400-001` investigation pass merged as **PR #522**
  re-checked every precondition and confirmed that none has been
  satisfied since the 2026-05-19 `PRODUCT-POWER-400-001` re-check
  (PR #521): the `PRODUCT-POWER-400-001` implementation slice has
  not landed (only the docs-only investigation pass merged as
  PR #521; the canonical S360-400 / `PWR`-bearing product YAML,
  the matching `config/product-catalog.json` entry, and the
  legacy-compatible `*-pwr` Core variant relationship decision
  all remain owed); the `PACKAGE-POWER-400-001` implementation
  slice has not landed (only the docs-only investigation pass
  merged as PR #520); no separate JSON-only PR for `S360-400`
  `schematic_status` promotion has landed
  (`config/hardware-catalog.json` line 110 stays
  `schematic_status: cataloged_unverified` with no
  `schematic_file`); no `COMPLIANCE-001` `S360-400` slice
  mains-voltage UK / EU sign-off has landed since PR #506; and
  the UX-class decision (standard preview-candidate vs advanced
  / manual-warning posture, owed to per-family
  `PRODUCT-POWER-400-001` compliance verdict) has not been
  rendered. No S360-400 WebFlash wrapper exists under
  [`products/webflash/`](products/webflash/) — only three PoE
  wrappers (`ceiling-poe-ventiq-roomiq.yaml`,
  `ceiling-poe-ventiq-roomiq-led.yaml`,
  `ceiling-poe-ventiq-fantriac-roomiq.yaml`); no `PWR` build is
  added to
  [`config/webflash-builds.json`](config/webflash-builds.json)
  (only two PoE builds); `PWR` stays reserved in
  [`config/webflash-compatibility.json`](config/webflash-compatibility.json)
  `canonical_power` without any `webflash_build_matrix: true`
  consumer; `release_one_required_configs` stays
  `["Ceiling-POE-VentIQ-RoomIQ"]`; no S360-400-specific product
  is added to
  [`config/product-catalog.json`](config/product-catalog.json)
  (four `legacy-compatible` `*-pwr` Core variants unchanged);
  [`.github/workflows/firmware-build-release.yml`](.github/workflows/firmware-build-release.yml)
  is byte-identical. The next evidence-bearing PR against
  `WEBFLASH-POWER-400-001` should appear when
  `PRODUCT-POWER-400-001` implementation lands, the
  `COMPLIANCE-001` `S360-400` slice closes, and the UX-class
  decision is made. See
  `docs/webflash-exposure-readiness-matrix.md` §Power / S360-400
  WebFlash posture,
  `docs/release-artifact-readiness-matrix.md` §Power / S360-400
  release posture, and `docs/cleanup-audit.md`
  §`WEBFLASH-POWER-400-001 update`.
- **No new evidence committed for `RELEASE-POWER-400-001`
  preconditions (2026-05-19 re-check).** The 2026-05-19
  `RELEASE-POWER-400-001` investigation pass merged as **PR #523**
  re-checked every precondition and confirmed that none has been
  satisfied since the 2026-05-19 `WEBFLASH-POWER-400-001` re-check
  (PR #522):
  the `WEBFLASH-POWER-400-001` implementation slice has not
  landed (only the docs-only investigation pass merged as
  PR #522; the WebFlash wrapper, the catalog
  `webflash_build_matrix: true` flip, the build-matrix row, and
  the UX-class decision all remain owed); the
  `PRODUCT-POWER-400-001` implementation slice has not landed
  (only the docs-only investigation pass merged as PR #521); the
  `PACKAGE-POWER-400-001` implementation slice has not landed
  (only the docs-only investigation pass merged as PR #520); no
  separate JSON-only PR for `S360-400` `schematic_status`
  promotion has landed; no `COMPLIANCE-001` `S360-400` slice
  mains-voltage UK / EU sign-off has landed since PR #506; no
  BOM / silkscreen / PCB / creepage / clearance / bench /
  thermal / inrush / insulation / Hi-pot / earth-continuity /
  leakage / EMI / EMC evidence is committed for `S360-400-R4`;
  and the UX-class decision has not been made. No S360-400
  release artifact exists of any kind — no `firmware/`
  directory exists at HEAD; no `firmware/configurations/`
  directory exists at HEAD; no `firmware/sources.json` file
  exists at HEAD; no top-level `manifest.json` file exists at
  HEAD; no `firmware-*.json` file exists at HEAD; no GitHub
  Release for any PWR-240V tag exists; no
  `Sense360-Ceiling-PWR-{AIR}-{ROOM}-v{VERSION}-{CHANNEL}.bin`
  artifact has been built / signed / attached / imported; no
  SHA256 / MD5 checksum files for any PWR-240V artifact; no
  build-info `manifest.json` asset for any PWR-240V release; no
  proof row in
  [`docs/webflash-release-proof.md`](docs/webflash-release-proof.md)
  for any PWR-240V artifact; the two existing `artifact_name`
  entries (`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`
  and `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`)
  stay byte-identical;
  [`.github/workflows/firmware-build-release.yml`](.github/workflows/firmware-build-release.yml)
  is byte-identical. All eight release-time sub-gates at
  [`docs/release-artifact-readiness-matrix.md` §Release note / artifact / checksum gates](docs/release-artifact-readiness-matrix.md#release-note--artifact--checksum-gates)
  remain unmet (product-catalog entry, build-matrix entry,
  artifact-name conformance, release-tag conformance,
  release-notes generated / valid, artifact built, checksums
  attached / manifest attached / proof recorded). The next
  evidence-bearing PR against `RELEASE-POWER-400-001` should
  appear when `WEBFLASH-POWER-400-001` implementation lands and
  the `COMPLIANCE-001` `S360-400` slice closes. See
  `docs/release-artifact-readiness-matrix.md` §Power / S360-400
  release posture and `docs/cleanup-audit.md`
  §`RELEASE-POWER-400-001 update`.
- **No new evidence committed for `PACKAGE-POE-410-001`
  preconditions (2026-05-20 re-check).** The 2026-05-20
  `PACKAGE-POE-410-001` investigation pass (merged as PR #526) re-checked
  every precondition and confirmed that none has been satisfied
  since the 2026-05-19 `HW-PINMAP-410-FOLLOWUP` re-check
  (PR #517): no BOM line item with manufacturer + part number +
  revision for `LAN_CON1 RJP-003TC1(LPJ4112CNL)` magnetics /
  RJ45, `U1 TPS2378DDAR(HSOIC-8)` PoE PD controller,
  `U2 TX4138(ESOIC-8)` buck, or `DCDC1 F0505S-2WR2(SIP-7)`
  isolated DC/DC (settling the primary-vs-alternate question
  against the annotated `AM1D-0505S-NZ`) is committed (the
  three-way `config/hardware-catalog.json` `description:
  "PoE to 5V."` (line 119) vs package header `Ag9712M,
  Silvertel Ag9700, or similar` (`packages/hardware/power_poe.yaml`
  line 6) vs schematic discrete topology
  (`TPS2378DDAR + TX4138 + F0505S-2WR2 + RJP-003TC1(LPJ4112CNL)`)
  disagreement therefore stays unresolved); no BOM lines for
  `D1 SMAJ58A` / `D2 ss510` / `D3 Green` / `L1 33uH` /
  `R1`–`R9` (including `R1 24.9k` DEN, `R2 1.27k` CLS,
  `R5 0.03R` RTN sense, `R3/R4 9.1k` paired ILIM, `R7 10.5k`
  Rd, `R8 56.2k` Rc) / `C1`–`C8` (including `C2 15uF` CBULK,
  `C6 470u` buck output bulk, `C8 22u` `+5VP` output bulk) /
  `J3` 2-pin Core-facing connector are committed; no
  operator-attributed silkscreen captures of the module-side
  `J3` 1-to-2 pin order are committed; no KiCad PCB source /
  Gerbers / drill / STEP / board photos sufficient to verify
  isolation-barrier widths around the `F0505S-2WR2` or
  `H1`–`H4` PCB-level electrical bonding to `Lan_earth` / RJ45
  shield are committed; no bench / load / PoE-link-up against
  802.3af and 802.3at PSE / thermal / inrush / insulation /
  Hi-pot / earth-continuity / leakage / EMI / EMC measurements
  against a populated `S360-410-R4` board are committed; no
  IEEE 802.3af / 802.3at compliance test reports are
  committed; no isolation / safety test reports (Hi-pot,
  insulation resistance, earth continuity, leakage) are
  committed; no separate JSON-only PR for `S360-410`
  `schematic_status` promotion has landed
  (`config/hardware-catalog.json` line 120 stays
  `schematic_status: cataloged_unverified` with no
  `schematic_file`); no HW-002 Open Question #6 closure /
  `S360-100-BENCH-001` J2-harness identity update has landed
  (both stay `pending — bench/manufacturing evidence
  required` per the 2026-05-18 re-check); and no Release-One
  PoE "schematic verification pending" caveat closure PR has
  landed (the caveat in
  [`docs/release-one-hardware-audit.md` Findings → PoE PSU](docs/release-one-hardware-audit.md#findings)
  and [Required follow-ups #6](docs/release-one-hardware-audit.md#required-follow-ups)
  is **preserved verbatim** by this re-check).
  [`packages/hardware/power_poe.yaml`](packages/hardware/power_poe.yaml)
  stays byte-identical to PR #517 state (the stale `Ag9712M,
  Silvertel Ag9700, or similar` header at line 6, the `IEEE
  802.3af (PoE) or 802.3at (PoE+)` standard line at line 7,
  the `Class 0 (0.44-12.95W) or Class 1 (0.44-3.84W)` class
  line at line 8, the `36-57V DC` input line at line 9, the
  `5V DC, 2A (10W) or 3.3V DC` output line at line 10, the
  `Overcurrent, overvoltage, short-circuit` protection line at
  line 11, the `substitutions: power_source: "poe"` /
  `poe_class: "0"` / `poe_standard: "802.3af"` block at lines
  28–31, the `globals: power_source_type` block at lines
  33–38, the template diagnostic sensors `Supply Voltage` /
  `Power Source` / `Power Configuration` / `PoE Power
  Connected`, the logger config, and the `on_boot` logger
  statements all preserved); the package has **no GPIO /
  I²C / UART / SPI / DAC / runtime binding**; the
  [`docs/hardware/s360-410-r4-poe.md`](docs/hardware/s360-410-r4-poe.md)
  status stays `partial — schematic evidence available;
  package reconciliation, PoE PD controller / magnetics /
  buck / isolated DC/DC / harness identity evidence pending`;
  [`docs/hardware/package-readiness-matrix.md` `power_poe.yaml`](docs/hardware/package-readiness-matrix.md#power_poeyaml--s360-410)
  row stays `reference-only` + `schematic-evidence-pending` +
  `do-not-change-release-one`; no PoE-410-explicit entry
  exists in [`config/product-catalog.json`](config/product-catalog.json),
  [`config/webflash-builds.json`](config/webflash-builds.json),
  [`products/`](products/), or
  [`products/webflash/`](products/webflash/); Release-One stays
  `Ceiling-POE-VentIQ-RoomIQ` / version `1.0.0` / channel
  `stable`; LED preview stays `Ceiling-POE-VentIQ-RoomIQ-LED`
  / `status: preview` / `channel: preview`; FanTRIAC stays
  `status: blocked` / `blocker: HW-005` /
  `webflash_build_matrix: false`. PoE is SELV; `S360-410` is
  **not** in scope for COMPLIANCE-001. The next
  evidence-bearing PR against `PACKAGE-POE-410-001` should
  appear when one of the five gates lands: BOM cross-check;
  the `S360-410` `schematic_status: verified` JSON PR;
  HW-002 Open Question #6 / `S360-100-BENCH-001` J2-harness
  closure; the package-header reconciliation against the
  schematic-shown discrete topology; or the Release-One PoE
  caveat closure. See `docs/hardware/s360-410-r4-poe.md`
  §`### 2026-05-20 — PACKAGE-POE-410-001 investigation pass`
  and `docs/cleanup-audit.md` §`PACKAGE-POE-410-001 update
  (2026-05-20 — docs-only investigation pass)`.
- **No new evidence committed for `PRODUCT-POE-410-001`
  preconditions (2026-05-20 re-check).** The 2026-05-20
  `PRODUCT-POE-410-001` investigation pass (merged as PR #528)
  re-checked every precondition and confirmed that none has
  been satisfied since the 2026-05-20 `PACKAGE-POE-410-001`
  re-check (PR #526) and the 2026-05-20 `CLEANUP-POE-410-001`
  tracker cleanup (PR #527): the `PACKAGE-POE-410-001`
  implementation slice has not landed (only the docs-only
  investigation pass merged as PR #526; the package-header
  reconciliation against the schematic-shown discrete topology,
  the catalog `description` reconciliation (if applicable), the
  BOM citation, and the `S360-410` `schematic_status: verified`
  JSON promotion that PR #526 enumerated as the required atomic
  slice all remain owed); no BOM line item with manufacturer +
  part number + revision for `LAN_CON1 RJP-003TC1(LPJ4112CNL)`
  magnetics / RJ45, `U1 TPS2378DDAR(HSOIC-8)` PoE PD controller,
  `U2 TX4138(ESOIC-8)` buck, `DCDC1 F0505S-2WR2(SIP-7)` isolated
  DC/DC (settling the primary-vs-alternate question against the
  annotated `AM1D-0505S-NZ`), `D1 SMAJ58A`, `D2 ss510`,
  `D3 Green`, `L1 33uH`, `R1`–`R9`, `C1`–`C8`, or `J3` 2-pin
  Core-facing connector is committed; no separate JSON-only PR
  for the `S360-410` `schematic_status: verified` promotion has
  landed (`config/hardware-catalog.json` line 120 stays
  `schematic_status: cataloged_unverified` with no
  `schematic_file`); no HW-002 Open Question #6 closure /
  `S360-100-BENCH-001` J2-harness identity update has landed
  (both stay `pending — bench/manufacturing evidence required`
  per the 2026-05-18 re-check); no Release-One PoE "schematic
  verification pending" caveat closure PR has landed (the caveat
  in [`docs/release-one-hardware-audit.md` Findings → PoE PSU](docs/release-one-hardware-audit.md#findings)
  and [Required follow-ups #6](docs/release-one-hardware-audit.md#required-follow-ups)
  is **preserved verbatim** by this re-check); no
  product-onboarding approval per
  [`docs/product-onboarding.md`](docs/product-onboarding.md) has
  been recorded against `PRODUCT-POE-410-001`; and the
  no-new-entry vs new-entry product-catalog readiness decision
  has not been made. No S360-410-explicit /
  `POE`-410-subject WebFlash-shippable product YAML exists under
  [`products/`](products/) or
  [`products/webflash/`](products/webflash/); the three shipping
  PoE entries in
  [`config/product-catalog.json`](config/product-catalog.json)
  (`Ceiling-POE-VentIQ-RoomIQ` `status: production` /
  `channel: stable`, `Ceiling-POE-VentIQ-RoomIQ-LED`
  `status: preview` / `channel: preview`, and
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` `status: blocked` /
  `blocker: HW-005` / `webflash_build_matrix: false`) each
  carry `hardware.poe: "S360-410"` as a catalog-level mapping
  field only and stay byte-identical; the six
  `legacy-compatible` `*-poe` Core variants stay
  `legacy-compatible` and `webflash_build_matrix: false`;
  [`config/webflash-builds.json`](config/webflash-builds.json)
  stays byte-identical (only Release-One stable and LED
  preview);
  [`config/webflash-compatibility.json`](config/webflash-compatibility.json)
  stays byte-identical (`POE` reserved in `canonical_power`
  consumed by both committed builds; POE reservation does
  **not** imply S360-410-subject product readiness);
  `release_one_required_configs` stays
  `["Ceiling-POE-VentIQ-RoomIQ"]`;
  [`packages/hardware/power_poe.yaml`](packages/hardware/power_poe.yaml)
  stays byte-identical to PR #517 / PR #526 state. The next
  evidence-bearing PR against `PRODUCT-POE-410-001` should
  appear when `PACKAGE-POE-410-001` implementation lands, the
  Release-One PoE caveat-closure PR lands, and
  product-onboarding approval per
  [`docs/product-onboarding.md`](docs/product-onboarding.md)
  is granted (along with the explicit no-new-entry vs new-entry
  decision). See
  [`docs/product-readiness-matrix.md` §PoE-410 / S360-410](docs/product-readiness-matrix.md#poe-410--s360-410),
  [`docs/webflash-exposure-readiness-matrix.md` §PoE / S360-410 WebFlash posture](docs/webflash-exposure-readiness-matrix.md#poe--s360-410-webflash-posture),
  [`docs/release-artifact-readiness-matrix.md` §PoE / S360-410 release posture](docs/release-artifact-readiness-matrix.md#poe--s360-410-release-posture),
  [`docs/hardware/s360-410-r4-poe.md`](docs/hardware/s360-410-r4-poe.md)
  §HW-PINMAP-410-FOLLOWUP audit log row
  `2026-05-20 — PRODUCT-POE-410-001 investigation pass`, and
  [`docs/cleanup-audit.md` §`PRODUCT-POE-410-001 update (2026-05-20 — docs-only investigation pass)`](docs/cleanup-audit.md).
- **No new evidence committed for `WEBFLASH-POE-410-001`
  preconditions (2026-05-20 re-check).** The 2026-05-20
  `WEBFLASH-POE-410-001` investigation pass (merged as PR #530)
  re-checked every precondition and confirmed that none has
  been satisfied since the 2026-05-20 `PRODUCT-POE-410-001`
  re-check (PR #528) and the 2026-05-20 `CLEANUP-POE-410-002`
  tracker cleanup (PR #529): the `PRODUCT-POE-410-001`
  implementation slice has not landed (only the docs-only
  investigation pass merged as PR #528; the no-new-entry vs
  new-entry decision, and — if a new entry is warranted — the
  canonical S360-410 / `POE`-410-subject product YAML plus the
  matching `config/product-catalog.json` entry, all remain
  owed); the `PACKAGE-POE-410-001` implementation slice has
  not landed (only the docs-only investigation pass merged as
  PR #526); no BOM line item with manufacturer + part number
  + revision for `LAN_CON1 RJP-003TC1(LPJ4112CNL)` magnetics
  / RJ45, `U1 TPS2378DDAR(HSOIC-8)` PoE PD controller,
  `U2 TX4138(ESOIC-8)` buck, `DCDC1 F0505S-2WR2(SIP-7)`
  isolated DC/DC (settling the primary-vs-alternate question
  against the annotated `AM1D-0505S-NZ`), `D1 SMAJ58A`,
  `D2 ss510`, `D3 Green`, `L1 33uH`, `R1`–`R9`, `C1`–`C8`,
  or `J3` 2-pin Core-facing connector is committed; no
  separate JSON-only PR for the `S360-410` `schematic_status:
  verified` promotion has landed
  ([`config/hardware-catalog.json`](config/hardware-catalog.json)
  line 120 stays `schematic_status: cataloged_unverified`
  with no `schematic_file`); no HW-002 Open Question #6
  closure / `S360-100-BENCH-001` J2-harness identity update
  has landed (both stay `pending — bench/manufacturing
  evidence required` per the 2026-05-18 re-check); no
  Release-One PoE "schematic verification pending" caveat
  closure PR has landed (the caveat in
  [`docs/release-one-hardware-audit.md` Findings → PoE PSU](docs/release-one-hardware-audit.md#findings)
  and [Required follow-ups #6](docs/release-one-hardware-audit.md#required-follow-ups)
  is **preserved verbatim** by this re-check); no
  product-onboarding approval per
  [`docs/product-onboarding.md`](docs/product-onboarding.md)
  has been recorded against `WEBFLASH-POE-410-001`; and the
  release / build readiness gates remain open (a WebFlash
  wrapper cannot wrap a product YAML that does not exist).
  No S360-410 WebFlash wrapper exists under
  [`products/webflash/`](products/webflash/) — only three
  PoE wrappers
  ([`ceiling-poe-ventiq-roomiq.yaml`](products/webflash/ceiling-poe-ventiq-roomiq.yaml),
  [`ceiling-poe-ventiq-roomiq-led.yaml`](products/webflash/ceiling-poe-ventiq-roomiq-led.yaml),
  [`ceiling-poe-ventiq-fantriac-roomiq.yaml`](products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml)),
  all under Release-One identity, not S360-410-subject
  WebFlash exposure;
  [`config/webflash-builds.json`](config/webflash-builds.json)
  stays byte-identical (only the Release-One `stable` build
  and the LED `preview` build, both consuming S360-410
  logically under the preserved Release-One caveat); no
  PoE-410-subject build is added to
  [`config/webflash-builds.json`](config/webflash-builds.json);
  no PoE-410-subject `webflash_wrapper`, `artifact_name`, or
  `config_string` is added to
  [`config/product-catalog.json`](config/product-catalog.json);
  no PoE-410-subject row is flipped to
  `webflash_build_matrix: true`;
  [`config/webflash-compatibility.json`](config/webflash-compatibility.json)
  reserves `POE` in `canonical_power` consumed by both
  committed builds (POE reservation does **not** imply
  S360-410-subject WebFlash exposure);
  `release_one_required_configs` stays
  `["Ceiling-POE-VentIQ-RoomIQ"]`;
  [`packages/hardware/power_poe.yaml`](packages/hardware/power_poe.yaml)
  stays byte-identical to PR #517 / PR #526 / PR #528 state.
  Per
  [`docs/product-readiness-matrix.md` §PoE-410 / S360-410](docs/product-readiness-matrix.md#poe-410--s360-410)
  and the
  [§Follow-up PR sequence row](docs/release-artifact-readiness-matrix.md#follow-up-pr-sequence)
  for `WEBFLASH-POE-410-001`, the slice may not be required
  at all if `PRODUCT-POE-410-001` ultimately closes via the
  default no-new-entry / caveat-closure-only path; that
  observation is carried forward as the ninth observation
  but does **not** close `WEBFLASH-POE-410-001` today — the
  queue stays blocked / deferred until `PRODUCT-POE-410-001`
  implementation or no-op closure is explicitly decided
  later. The next evidence-bearing PR against
  `WEBFLASH-POE-410-001` should appear when
  `PRODUCT-POE-410-001` implementation lands (either as a
  new product entry or as the no-new-entry / caveat-closure
  decision), the Release-One PoE caveat-closure PR lands,
  and product-onboarding approval per
  [`docs/product-onboarding.md`](docs/product-onboarding.md)
  is granted. See
  [`docs/webflash-exposure-readiness-matrix.md` §PoE / S360-410 WebFlash posture](docs/webflash-exposure-readiness-matrix.md#poe--s360-410-webflash-posture),
  [`docs/release-artifact-readiness-matrix.md` §PoE / S360-410 release posture](docs/release-artifact-readiness-matrix.md#poe--s360-410-release-posture),
  [`docs/hardware/s360-410-r4-poe.md`](docs/hardware/s360-410-r4-poe.md)
  §HW-PINMAP-410-FOLLOWUP audit log row
  `2026-05-20 — WEBFLASH-POE-410-001 investigation pass`, and
  [`docs/cleanup-audit.md` §`WEBFLASH-POE-410-001 update (2026-05-20 — docs-only investigation pass)`](docs/cleanup-audit.md).
- **No new repo-committed evidence for `RELEASE-POE-410-001`
  preconditions (2026-05-20 re-check).** The 2026-05-20
  `RELEASE-POE-410-001` investigation pass (merged as PR #532)
  re-checked every precondition and confirmed that none
  has been satisfied since the 2026-05-20
  `WEBFLASH-POE-410-001` re-check (PR #530) and the
  2026-05-20 `CLEANUP-POE-410-003` tracker cleanup (PR
  #531): the `WEBFLASH-POE-410-001` implementation slice
  has not landed (only the docs-only investigation pass
  merged as PR #530; the WebFlash wrapper, the catalog
  `webflash_build_matrix: true` flip, the build-matrix row,
  and the UX-class decision all remain owed); the
  `PRODUCT-POE-410-001` implementation slice has not landed
  (only the docs-only investigation pass merged as PR
  #528); the `PACKAGE-POE-410-001` implementation slice has
  not landed (only the docs-only investigation pass merged
  as PR #526). Re repo-committed BOM evidence: BOM files
  have been **supplied out-of-band / uploaded**, but
  **repo-committed BOM evidence has not landed in this
  repository yet**; for `S360-410` specifically, the
  uploaded BOM evidence **appears to support** the
  schematic-shown discrete PoE topology
  (`LAN_CON1 RJP-003TC1(LPJ4112CNL)` magnetics / RJ45,
  `U1 TPS2378DDAR(HSOIC-8)` PoE PD controller,
  `U2 TX4138(ESOIC-8)` buck, `DCDC1 F0505S-2WR2(SIP-7)`
  isolated DC/DC including the `AM1D-0505S-NZ`
  annotated-alternate question, `D1 SMAJ58A`, `D2 ss510`,
  `D3 Green`, `L1 33uH`, `R1`–`R9`, `C1`–`C8`, `J3` 2-pin
  Core-facing connector), but PR #532 did **not** ingest
  or commit that BOM — BOM ingest is the responsibility of
  a separate `HW-BOM-ASSETS-001` follow-up. The release
  gate stays blocked until that ingest lands and the
  downstream `PACKAGE-POE-410-001` / `PRODUCT-POE-410-001`
  / `WEBFLASH-POE-410-001` gates are updated against the
  committed evidence. No separate JSON-only PR for the
  `S360-410` `schematic_status: verified` promotion has
  landed
  ([`config/hardware-catalog.json`](config/hardware-catalog.json)
  line 120 stays `schematic_status: cataloged_unverified`
  with no `schematic_file`); no HW-002 Open Question #6
  closure / `S360-100-BENCH-001` J2-harness identity update
  has landed (both stay `pending — bench/manufacturing
  evidence required` per the 2026-05-18 re-check); no
  Release-One PoE "schematic verification pending" caveat
  closure PR has landed (the caveat in
  [`docs/release-one-hardware-audit.md` Findings → PoE PSU](docs/release-one-hardware-audit.md#findings)
  and [Required follow-ups #6](docs/release-one-hardware-audit.md#required-follow-ups)
  is **preserved verbatim** by this re-check); no
  product-onboarding approval per
  [`docs/product-onboarding.md`](docs/product-onboarding.md)
  has been recorded against `RELEASE-POE-410-001`; and the
  eight release-time sub-gates remain unmet. No
  PoE-410-explicit release artifact exists of any kind —
  no `firmware/` directory exists at HEAD; no
  `firmware/configurations/` directory exists at HEAD; no
  `firmware/sources.json` file exists at HEAD; no top-level
  `manifest.json` file exists at HEAD; no `firmware-*.json`
  file exists at HEAD; no GitHub Release for any
  PoE-410-explicit tag exists; no PoE-410-explicit
  `Sense360-…-v{VERSION}-{CHANNEL}.bin` artifact has been
  built / signed / attached / imported; no SHA256 / MD5
  checksum files for any PoE-410-explicit artifact; no
  build-info `manifest.json` asset for any PoE-410-explicit
  release; no proof row in
  [`docs/webflash-release-proof.md`](docs/webflash-release-proof.md)
  for any PoE-410-explicit artifact; the two existing
  `artifact_name` entries
  (`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`
  and
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`)
  stay byte-identical;
  [`.github/workflows/firmware-build-release.yml`](.github/workflows/firmware-build-release.yml)
  is byte-identical. All eight release-time sub-gates at
  [`docs/release-artifact-readiness-matrix.md` §Release note / artifact / checksum gates](docs/release-artifact-readiness-matrix.md#release-note--artifact--checksum-gates)
  remain unmet (product-catalog entry, build-matrix entry,
  artifact-name conformance, release-tag conformance,
  release-notes generated / valid, artifact built,
  checksums attached / manifest attached / proof recorded).
  Per
  [`docs/product-readiness-matrix.md` §PoE-410 / S360-410](docs/product-readiness-matrix.md#poe-410--s360-410)
  and the
  [§Follow-up PR sequence row](docs/release-artifact-readiness-matrix.md#follow-up-pr-sequence)
  for `RELEASE-POE-410-001`, the slice may not be required
  at all if `PRODUCT-POE-410-001` / `WEBFLASH-POE-410-001`
  ultimately close via the default no-new-entry /
  caveat-closure-only path; that observation is carried
  forward but does **not** close `RELEASE-POE-410-001`
  today — the queue stays blocked / deferred until
  `PRODUCT-POE-410-001` / `WEBFLASH-POE-410-001`
  implementation or no-op closure is explicitly decided
  later. The next evidence-bearing PR against
  `RELEASE-POE-410-001` should appear when
  `WEBFLASH-POE-410-001` implementation lands (which itself
  requires `PRODUCT-POE-410-001` implementation,
  `PACKAGE-POE-410-001` implementation, and the
  `HW-BOM-ASSETS-001` BOM-ingest follow-up), the
  Release-One PoE caveat-closure PR lands, and
  product-onboarding approval is granted. See
  [`docs/release-artifact-readiness-matrix.md` §PoE / S360-410 release posture](docs/release-artifact-readiness-matrix.md#poe--s360-410-release-posture),
  [`docs/webflash-exposure-readiness-matrix.md` §PoE / S360-410 WebFlash posture](docs/webflash-exposure-readiness-matrix.md#poe--s360-410-webflash-posture),
  [`docs/hardware/s360-410-r4-poe.md`](docs/hardware/s360-410-r4-poe.md)
  §HW-PINMAP-410-FOLLOWUP audit log row
  `2026-05-20 — RELEASE-POE-410-001 investigation pass`, and
  [`docs/cleanup-audit.md` §`RELEASE-POE-410-001 update (2026-05-20 — docs-only investigation pass)`](docs/cleanup-audit.md).

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

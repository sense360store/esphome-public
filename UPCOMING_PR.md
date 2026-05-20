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
  Completed / merged PRs table; this PR
  (`RELEASE-POE-410-001`) adds the `CLEANUP-POE-410-003` /
  #531 row.
- **RELEASE-POE-410-001** investigation merged as **this PR**
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
- **CLEANUP-POE-410-003** merged as **PR #531** on 2026-05-20
  (docs-only tracker cleanup). Recorded `WEBFLASH-POE-410-001` as
  PR #530 in `UPCOMING_PR.md` after that PR merged. No functional
  or audit-doc edits.
- **HW-BOM-ASSETS-001** is the **current evidence-ingest PR**
  (this PR). It is a **partial-batch, record-only** BOM-evidence
  ingest. New curated artifact indexes are added for
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
  **S360-410** are **not** ingested by this PR. Their per-board
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
| CLEANUP-POE-410-003          | #531      | esphome-public  | Merged — docs-only tracker cleanup      | Recorded `WEBFLASH-POE-410-001` as PR #530 in `UPCOMING_PR.md` after that PR merged; tracker-only cleanup, no functional or audit-doc content changes | No functional, package, product, WebFlash, build, release, compliance, JSON catalog, test, script, workflow, component, include, firmware, manifest, audit-document, or artifact files; only `UPCOMING_PR.md` was touched | Prepared the tracker for `HW-BOM-ASSETS-001` (partial BOM evidence ingest); `RELEASE-POE-410-001` stays blocked behind `WEBFLASH-POE-410-001` |
| CLEANUP-POE-410-003          | #531      | esphome-public  | Merged — docs-only tracker cleanup      | Converted the unresolved `PR #XXX` / `this PR` placeholders that PR #530 left in `UPCOMING_PR.md` so `WEBFLASH-POE-410-001` consistently points to PR #530 (Current queue summary bullet, `CLEANUP-POE-410-002` Follow-up impact column, `WEBFLASH-POE-410-001` row in the Completed / merged PRs table, and the Recently uploaded evidence entry all now name PR #530 explicitly); removed the `WEBFLASH-POE-410-001` active-queue entry (the investigation pass has merged, so the row no longer belongs in the active queue) and renumbered subsequent entries so `RELEASE-POE-410-001` becomes active queue item #7 | No functional, package, product, WebFlash, build, release, compliance, JSON catalog, test, script, workflow, component, include, firmware, manifest, audit-document, or artifact files; only `UPCOMING_PR.md` was touched | Prepared the tracker for `RELEASE-POE-410-001` / this PR; no queue-ordering effect on `RELEASE-POE-410-001` |
| RELEASE-POE-410-001          | this PR   | esphome-public  | Merged — docs-only investigation pass   | Recorded `RELEASE-POE-410-001` Path A deferral; confirmed `WEBFLASH-POE-410-001` implementation slice / `PRODUCT-POE-410-001` implementation slice / `PACKAGE-POE-410-001` implementation slice / repo-committed BOM evidence (the uploaded BOM appears to support the schematic-shown discrete PoE topology — `LAN_CON1 RJP-003TC1(LPJ4112CNL)` magnetics / RJ45, `U1 TPS2378DDAR(HSOIC-8)` PoE PD controller, `U2 TX4138(ESOIC-8)` buck, `DCDC1 F0505S-2WR2(SIP-7)` isolated DC/DC — but BOM ingest is the responsibility of a separate `HW-BOM-ASSETS-001` follow-up, not this PR) / `S360-410 schematic_status: verified` JSON PR / HW-002 OQ#6 / `S360-100-BENCH-001` J2-harness identity closure / Release-One PoE caveat closure / product-onboarding approval / eight release-time sub-gates preconditions remain open; carried forward the observation that `RELEASE-POE-410-001` may not be required at all if `PRODUCT-POE-410-001` / `WEBFLASH-POE-410-001` ultimately close via the default no-new-entry / caveat-closure-only path (queue stays blocked / deferred until that decision is made later); no PoE-410-explicit release artifact exists of any kind (no `firmware/` directory, no `firmware/configurations/`, no `firmware/sources.json`, no top-level `manifest.json`, no `firmware-*.json`, no PoE-410-explicit GitHub Release tag, no PoE-410-explicit `.bin`, no PoE-410-explicit SHA256 / MD5 checksum files, no PoE-410-explicit build-info `manifest.json`, no PoE-410-explicit proof row in `docs/webflash-release-proof.md`); kept Release-One / LED preview / FanTRIAC blocked-reference / six `legacy-compatible` `*-poe` Core variants byte-identical; kept `.github/workflows/firmware-build-release.yml` byte-identical (workflow-frozen) | No package, product, WebFlash, build, release, compliance, JSON catalog, test, script, workflow, component, include, firmware, manifest, or artifact edits; no `schematic_status` / `schematic_file` promotion; no COMPLIANCE-001 movement; no PoE-410-explicit entry added; no `webflash_build_matrix: true` flip; no new `artifact_name`; no `webflash_wrapper` added; no `config_string` added; no new GitHub Release / tag / checksum / build-info manifest / proof row created; no BOM ingest (deferred to a separate `HW-BOM-ASSETS-001` follow-up); no `lifecycle_statuses` / `canonical_modules` / `canonical_power` / `forbidden_tokens` / `release_one_required_configs` / kit / `REQUIRED_CONFIGS` change; no Release-One caveat closure | `RELEASE-POE-410-001` stays blocked on the eight blocker preconditions (with the no-op observation carried forward); `WF-IMPORT-POE-410-001` (cross-repo) stays blocked behind it |

## Active / upcoming esphome-public queue

Listed in working priority order. WebFlash-owned import PRs are kept out of
this table; see **Cross-repo dependencies**. The only `WF-`-prefixed entry
that appears below is **WF-TRIAC-001**, which is the in-repo
wrapper/catalog/build slice (not a WebFlash-runtime import).

1. **HW-BOM-ASSETS-001 — partial BOM evidence ingest (record-only)**
   - Status: **Active / current evidence-ingest PR (this PR);
     partial-batch — only `S360-200` and `S360-210` blocker state
     updated; remaining BOMs deferred to a later `HW-BOM-ASSETS`
     follow-up**
   - Purpose: Land curated per-board artifact indexes for
     `S360-200-R4` (Sense360 RoomIQ) and `S360-210-R4` (Sense360
     AirIQ) recording the BOM evidence delivered to the task
     environment (file name, size, SHA256, component summary).
     Confirm byte-identical re-upload of the already-inventoried
     `S360-100-R4_BOM.xlsx` and `S360-100-R4.pdf` against the
     existing HW-ASSETS-002 inventory. Record the partial-batch
     state explicitly so the deferred boards' `BOM missing`
     blocker wording remains visible.
   - Notes: Follows existing
     [Hardware Artifact Policy](docs/hardware/hardware-artifact-policy.md)
     (HW-ASSETS-001) **without changing it**. BOM `.xlsx` files
     are **retained-but-not-committed** per the current per-board
     decision — recorded by filename + size + SHA256 only; the
     `.xlsx` itself is not added to `git`. No
     `docs/hardware/bom/` directory created. No `.xlsx` in `git`.
     No `config/` / `packages/` / `products/` / `tests/` /
     `scripts/` / `.github/workflows/` / `components/` /
     `include/` / `firmware/` / `manifest.json` /
     `firmware/sources.json` edit. No `schematic_status`
     promotion; no `schematic_file` set; no `webflash_build_matrix`
     flip; no `artifact_name`; no `REQUIRED_CONFIGS` change; no
     compliance claim; no Release-One change
     (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`); no LED
     preview change; no FanTRIAC change; no Release-One PoE
     caveat closure. `PACKAGE-POWER-400-001`,
     `PACKAGE-POE-410-001`, `PACKAGE-RELAY-001`,
     `PACKAGE-PWM-001`, `PACKAGE-DAC-001`, `PACKAGE-TRIAC-001`,
     `CORE-ABSTRACT-BUS-001A/B/C`, `COMPLIANCE-001`,
     `HW-005`, `S360-100-BENCH-001`, `S360-300-BENCH-001`,
     and the HW-PINMAP-* follow-ups all remain blocked on their
     existing gates — this PR does **not** flip the BOM gate
     for any of those boards because their BOMs are not
     ingested in this batch. Files touched (eight total): new
     [`docs/hardware/artifacts/S360-200-R4.md`](docs/hardware/artifacts/S360-200-R4.md);
     new [`docs/hardware/artifacts/S360-210-R4.md`](docs/hardware/artifacts/S360-210-R4.md);
     audit-log subsection added to
     [`docs/hardware/artifacts/S360-100-R4.md`](docs/hardware/artifacts/S360-100-R4.md);
     [`docs/hardware/board-readiness-matrix.md`](docs/hardware/board-readiness-matrix.md)
     `S360-200` / `S360-210` `Artifact index` cells flipped
     `missing` → `done` plus per-board notes expanded;
     `2026-05-20 — HW-BOM-ASSETS-001 partial BOM ingest`
     audit-log entries added to
     [`docs/hardware/s360-200-r4-roomiq.md`](docs/hardware/s360-200-r4-roomiq.md)
     and
     [`docs/hardware/s360-210-r4-airiq.md`](docs/hardware/s360-210-r4-airiq.md);
     [`docs/cleanup-audit.md`](docs/cleanup-audit.md) records
     the `HW-BOM-ASSETS-001 update` section; this
     `UPCOMING_PR.md` queue entry, the merged-PRs row for
     `CLEANUP-POE-410-003 / #531`, and a new
     `Recently uploaded evidence` entry.
   - Deferred to a later `HW-BOM-ASSETS` follow-up:
     `S360-211` BOM, `S360-300` BOM, `S360-310` BOM (including
     `K1` identity), `S360-311` BOM, `S360-312` `Fan_GP8403`
     BOM (GP8403 / MT3608 / DIP-switch evidence), `S360-320`
     BOM (BT136S-600D / MOC3023M evidence — no compliance
     claim), `S360-400` BOM (HLK-5M05 confirmation; the
     three-way `HLK-5M05` / `HLK-PM01 or similar` / `HLK-10M05`
     part-identity disagreement stays BOM-bound), `S360-410`
     BOM (discrete `TPS2378DDAR / TX4138 / F0505S-2WR2 /
     LPJ4112CNL` topology confirmation; the
     `Ag9712M / Silvertel Ag9700 / or similar` package-header
     disagreement stays BOM-bound).

2. **CORE-ABSTRACT-BUS-001C — UART / status LED / PIR / expansion GPIO + ALS_INT rebind**
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

3. **CORE-ABSTRACT-BUS-001A — relay_pin slice (`GPIO3`)**
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

4. **CORE-ABSTRACT-BUS-001B — Shared-I²C-bus consolidation**
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

5. **PRODUCT-POWER-400-001**
   - Status: **Investigated 2026-05-19; merged as PR #521;
     confirmed deferred (Path A docs-only); six preconditions
     still open**. Blocked on
     `PACKAGE-POWER-400-001` implementation (only the docs-only
     investigation merged as PR #520; the package YAML
     reconciliation slice has not run), BOM cross-check,
     `S360-400` `schematic_status: verified` JSON PR,
     `COMPLIANCE-001` `S360-400` slice, package / catalog
     reconciliation, and product-onboarding approval per
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

6. **WEBFLASH-POWER-400-001**
   - Status: **Investigated 2026-05-19; merged as PR #522;
     confirmed deferred (Path A docs-only); five preconditions
     still open**. Blocked on `PRODUCT-POWER-400-001`
     implementation (only the docs-only investigation merged as
     PR #521; the canonical S360-400 / `PWR`-bearing product
     YAML, the matching `config/product-catalog.json` entry, and
     the legacy-compatible `*-pwr` Core variant relationship
     decision all remain owed), `PACKAGE-POWER-400-001`
     implementation (only the docs-only investigation merged as
     PR #520), the `S360-400` `schematic_status: verified` JSON
     PR, the `COMPLIANCE-001` `S360-400` slice, and the UX-class
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

7. **RELEASE-POWER-400-001**
   - Status: **Investigated 2026-05-19; merged as PR #523;
     confirmed deferred (Path A docs-only); seven preconditions
     still open**. Blocked on `WEBFLASH-POWER-400-001`
     implementation (only
     docs-only investigation merged as PR #522;
     wrapper + catalog `webflash_build_matrix: true` flip +
     build-matrix row + UX-class decision all remain owed),
     `PRODUCT-POWER-400-001` implementation (only docs-only
     investigation merged as PR #521), `PACKAGE-POWER-400-001`
     implementation (only docs-only investigation merged as
     PR #520), the `S360-400` `schematic_status: verified` JSON
     PR, the `COMPLIANCE-001` `S360-400` slice, BOM / silkscreen
     / creepage / clearance / bench / thermal / EMI evidence,
     and the UX-class decision.
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
     open** — last re-checked PR #506; (6) **BOM / silkscreen /
     creepage / clearance / bench / thermal / EMI evidence
     missing** — same five-component BOM gap PR #520 recorded
     plus all silkscreen / PCB / creepage / clearance / bench /
     load / thermal / inrush / insulation / Hi-pot /
     earth-continuity / leakage / EMI / EMC measurements
     against a populated `S360-400-R4` board still missing;
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

8. **RELEASE-POE-410-001**
    - Status: Planned / after WEBFLASH-POE-410-001
    - Purpose: Produce the release artifact + release-proof entries for the
      S360-410 product.
    - Notes: Subject to existing release-artifact readiness gates.
7. **RELEASE-POE-410-001**
    - Status: **Investigated 2026-05-20; merged as this PR;
      confirmed deferred (Path A docs-only); preconditions still
      open**. Blocked on `WEBFLASH-POE-410-001` implementation
      (only the docs-only investigation merged as PR #530;
      the WebFlash wrapper, the catalog
      `webflash_build_matrix: true` flip, the build-matrix row,
      and the UX-class decision all remain owed),
      `PRODUCT-POE-410-001` implementation (only the docs-only
      investigation merged as PR #528),
      `PACKAGE-POE-410-001` implementation (only the docs-only
      investigation merged as PR #526), repo-committed BOM
      evidence (uploaded BOM files appear to support the
      schematic-shown discrete PoE topology — `LAN_CON1
      RJP-003TC1(LPJ4112CNL)` magnetics / RJ45,
      `U1 TPS2378DDAR(HSOIC-8)` PoE PD controller,
      `U2 TX4138(ESOIC-8)` buck, `DCDC1 F0505S-2WR2(SIP-7)`
      isolated DC/DC — but this PR does **not** ingest or
      commit that BOM; per the wording adjustment, BOM ingest
      is the responsibility of a separate
      `HW-BOM-ASSETS-001` follow-up), the `S360-410`
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
    - Notes: 2026-05-20 investigation pass merged as this PR is
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
      BOM evidence has not landed (the uploaded BOM appears
      to support the schematic-shown discrete topology but
      has not been ingested into the repository under a
      `HW-BOM-ASSETS-001` follow-up); the
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
      `PACKAGE-POE-410-001` implementation, the
      `HW-BOM-ASSETS-001` BOM-ingest follow-up, the `S360-410`
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

9. **PRODUCT-RELAY-001**
    - Status: Blocked on CORE-ABSTRACT-BUS-001A (relay_pin slice;
      itself blocked on 001C) + PACKAGE-RELAY-001 implementation
    - Purpose: Add the S360-310 Relay product YAML once the Relay package is
      implemented (not the current docs-only deferral state).
    - Notes: Implementation deferred per PR #511 (PACKAGE-RELAY-001
      docs-only deferral) and now further gated by the
      CORE-ABSTRACT-BUS-001A relay_pin slice landing.

10. **WEBFLASH-RELAY-001**
    - Status: Blocked on PRODUCT-RELAY-001 (which is itself blocked on
      CORE-ABSTRACT-BUS-001A)
    - Purpose: Add the WebFlash wrapper, compatibility entry, and build
      matrix row for the Relay product.
    - Notes: Pairs with WebFlash-side WF-IMPORT-RELAY-001.

11. **RELEASE-RELAY-001**
    - Status: Blocked on WEBFLASH-RELAY-001 (ultimately on
      CORE-ABSTRACT-BUS-001A)
    - Purpose: Produce the release artifact + release-proof entries for the
      Relay product.

12. **PACKAGE-PWM-001**
    - Status: Blocked on HW-PINMAP-311-FOLLOWUP returning sufficient evidence
    - Purpose: Stand up / re-stand up the S360-311 PWM package wiring once
      the pin/package audit is no longer partial.
    - Notes: Also affected by CORE-ABSTRACT-BUS-001B (shared I²C bus
      consolidation) and CORE-ABSTRACT-BUS-001C (`expansion_gpio1`
      / `expansion_gpio2` rebind that `fan_pwm.yaml` consumes via
      `${fan_pwm_pin}` / `${fan_tach_pin}`).

13. **PRODUCT-PWM-001**
    - Status: Blocked on PACKAGE-PWM-001
    - Purpose: Add / re-align the S360-311 PWM product YAML.

14. **WEBFLASH-PWM-001**
    - Status: Blocked on PRODUCT-PWM-001
    - Purpose: WebFlash wrapper, compatibility entry, build matrix row.
    - Notes: Pairs with WebFlash-side WF-IMPORT-PWM-001.

15. **RELEASE-PWM-001**
    - Status: Blocked on WEBFLASH-PWM-001
    - Purpose: Release artifact + release-proof entries for the PWM product.

16. **PACKAGE-DAC-001**
    - Status: Blocked on HW-PINMAP-312-FOLLOWUP returning sufficient evidence
    - Purpose: Stand up / re-stand up the S360-312 DAC (GP8403) package
      wiring once the pin/package audit is no longer partial.
    - Notes: Also affected by CORE-ABSTRACT-BUS-001B (the GP8403
      DAC is I²C-attached, so it consumes whichever bus id 001B
      settles on).

17. **PRODUCT-DAC-001**
    - Status: Blocked on PACKAGE-DAC-001
    - Purpose: Add / re-align the S360-312 DAC product YAML.

18. **WEBFLASH-DAC-001**
    - Status: Blocked on PRODUCT-DAC-001
    - Purpose: WebFlash wrapper, compatibility entry, build matrix row.
    - Notes: Pairs with WebFlash-side WF-IMPORT-DAC-001.

19. **RELEASE-DAC-001**
    - Status: Blocked on WEBFLASH-DAC-001
    - Purpose: Release artifact + release-proof entries for the DAC product.

20. **S360-300-BENCH-001**
    - Status: Pending bench evidence
    - Purpose: LED ring bench / verification gate for S360-300.
    - Notes: Blocks the LED stable chain together with the WebFlash-owned
      operator-proof follow-ups.

21. **RELEASE-007**
    - Status: Planned / promotion of LED stable
    - Purpose: Promote the LED package + product from preview to stable
      once S360-300-BENCH-001 and the WebFlash operator-proof follow-ups
      land.
    - Notes: Subject to preview-to-stable promotion gates.

22. **HW-005 / HW-PINMAP-320-FOLLOWUP**
    - Status: Open / evidence-pass re-checked (PR #505); audit remains
      partial
    - Purpose: Resolve the S360-320 FanTRIAC pin/package collisions and
      provide the schematic/interrupt-capable GPIO evidence needed to
      progress the FanTRIAC chain.
    - Notes: Gating PACKAGE-TRIAC-001 implementation.

23. **COMPLIANCE-001**
    - Status: Open / not cleared (PR #506 re-checked, no sign-off yet)
    - Purpose: Land the S360-320 mains-voltage advanced / manual-warning
      compliance sign-off.
    - Notes: Gating PRODUCT-TRIAC-002 / FanTRIAC release exposure.

24. **PACKAGE-TRIAC-001**
    - Status: Deferred (PR #502 docs-only); blocked on HW-005 /
      HW-PINMAP-320-FOLLOWUP / COMPLIANCE-001
    - Purpose: Implement the FanTRIAC package once the gating HW +
      compliance evidence lands.
    - Notes: `packages/expansions/fan_triac.yaml` retained as-is in the
      meantime.

25. **PRODUCT-TRIAC-002**
    - Status: Deferred (PR #501 docs-only); blocked on PACKAGE-TRIAC-001
    - Purpose: Implement the FanTRIAC product YAML once PACKAGE-TRIAC-001
      lands.

26. **WF-TRIAC-001 — In-repo wrapper/catalog/build slice**
    - Status: Blocked on PRODUCT-TRIAC-002
    - Purpose: Add the in-repo WebFlash wrapper, compatibility entry, and
      build matrix row for the FanTRIAC product. (This is the
      esphome-public-owned slice — the WebFlash-runtime import is tracked
      separately under cross-repo dependencies as WF-IMPORT-TRIAC-001.)
    - Notes: Listed here, not under cross-repo dependencies, because it
      touches `products/webflash/`, `config/`, and the build matrix in this
      repo.

27. **RELEASE-TRIAC-001**
    - Status: Blocked on WF-TRIAC-001 and COMPLIANCE-001
    - Purpose: Release artifact + release-proof entries for the FanTRIAC
      product, contingent on compliance sign-off.

28. **PRODUCT-DEP-002**
    - Status: Planned / housekeeping
    - Purpose: Continue dependency / toolchain alignment work (pre-commit
      tooling, ESPHome pin, Python tooling) without changing functional
      behavior.
    - Notes: Must not destabilize Release-One.

29. **CI-TOOLCHAIN-001**
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

- **S360-200-R4 BOM** — ingested by **HW-BOM-ASSETS-001** (this
  PR) as `b35d4654-S360200R4_BOM.xlsx` (11,177 bytes; SHA256
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
- **S360-210-R4 BOM** — ingested by **HW-BOM-ASSETS-001** (this
  PR) as `c551e467-S360210R4_BOM.xlsx` (11,966 bytes; SHA256
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
  (this PR): `df6da128-S360100R4_BOM.xlsx` (12,543 bytes;
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
- **Partial-batch deferral note (HW-BOM-ASSETS-001).** The
  HW-BOM-ASSETS-001 BOM batch is **partial**. Eight additional
  BOM `.xlsx` files (for `S360-211`, `S360-300`, `S360-310`,
  `S360-311`, `S360-312` (Fan_GP8403), `S360-320`, `S360-400`,
  and `S360-410`) are owed to a later `HW-BOM-ASSETS`
  follow-up PR. Until that follow-up lands, the per-board
  `BOM missing` / `BOM cross-check missing` blocker wording
  for those boards remains the explicit, honest gate.
  Notable still-BOM-bound items:
  `PACKAGE-POWER-400-001` (three-way `HLK-5M05` /
  `HLK-PM01 or similar` / `HLK-10M05` AC/DC part-identity
  disagreement), `PACKAGE-POE-410-001` (package-header
  `Ag9712M / Silvertel Ag9700 / or similar` vs
  schematic-shown discrete topology disagreement),
  `PACKAGE-DAC-001` (GP8403 / MT3608 BOM cross-check),
  `PACKAGE-PWM-001` (4-channel topology BOM cross-check),
  `PACKAGE-TRIAC-001` (BT136S-600D / MOC3023M BOM
  cross-check; **does not unblock COMPLIANCE-001 or HW-005**
  even when that BOM lands), `PACKAGE-RELAY-001` (`K1` BOM
  identity), and the LED stable promotion (S360-300 BOM
  evidence is one of several inputs to operator flash proof /
  bench behaviour — landing the BOM **does not** by itself
  promote LED stable).
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
  `RELEASE-POE-410-001` investigation pass (merged as this
  PR) re-checked every precondition and confirmed that none
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
  Core-facing connector), but this PR does **not** ingest
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

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

- **PWM-BLOCKER-REMOVAL-001** delivers, via **this PR** on 2026-05-25,
  the **audit / docs-only** S360-311 / FanPWM blocker sweep named as the
  next hardware blocker by `REPO-FRESHNESS-ROADMAP-AUDIT-001` / PR #582.
  Output: a [PWM-BLOCKER-REMOVAL-001 readiness / blocker table](docs/hardware/s360-311-r4-pwm.md#pwm-blocker-removal-001-readiness--blocker-table)
  and dated audit-log row in
  [`docs/hardware/s360-311-r4-pwm.md`](docs/hardware/s360-311-r4-pwm.md),
  plus addenda in
  [`docs/hardware/package-readiness-matrix.md`](docs/hardware/package-readiness-matrix.md),
  [`docs/product-readiness-matrix.md`](docs/product-readiness-matrix.md),
  and [`docs/repo-freshness-roadmap-audit.md`](docs/repo-freshness-roadmap-audit.md).
  **Key findings:** (1) a Google Drive folder `12vFan_PWM_PulseCounter`
  (= `S360-311` `old_name`; owner `neilmcrae@googlemail.com`) holds the
  full manufacturing artifact set the HW-ASSETS-003 index had recorded as
  `not provided in this upload` — BOM `.xlsx`, gerbers, CPL, STEP, and 3
  board renders; (2) the Drive BOM cross-checks the committed
  `S360-311-R4` schematic **1:1** (`U1` MT3608 boost; `Q1`–`Q4`
  `ME15N10-G` low-side N-FETs; `D1` SS34; `L1` SRN6045TA 22 µH; `R3` 38k
  / `R5` 2k divider; JST-SH `SM04B` ×5 / `SM13B` ×1), closing the
  BOM cross-check **at the part-identity layer**; (3) `CORE-ABSTRACT-BUS-001B-IMPLEMENT-001`
  already lifted the shared-I²C-bus blocker (`core_i2c`), and `001C`
  retired `expansion_gpio1..4` so the package's `${expansion_gpio*}`
  binding is now stale; (4) blocker rows 1 (hardware evidence), 2
  (schematic/BOM identity, part-identity layer), 5 (controlled-load
  type), 11 (no-mains compliance) are **CLOSED**, row 6 (output
  electrical) is **PARTIAL**, and rows 3/4/7/8/9/10 stay blocking. **Next
  PR:** `PACKAGE-PWM-001-IMPLEMENT-001` is **NOT READY** — gated on the
  minimum operator + bench set (single-vs-four-channel; SX1509-vs-direct-
  ESP32 routing; `J3`/`J6` 1-to-13 silkscreen; PWM polarity / tach
  pull-up / pulses-per-rev; per-fan current envelope; rev-stamp
  confirmation). **Audit-only — no blocker moves:** no `.xlsx` / gerber /
  CPL / STEP / PNG binary committed (retained-but-not-committed per
  `hardware-artifact-policy.md`); `S360-311` `schematic_status` stays
  `cataloged_unverified`; [`fan_pwm.yaml`](packages/expansions/fan_pwm.yaml)
  and [`sense360_fan_pwm.yaml`](packages/expansions/sense360_fan_pwm.yaml)
  unedited; no `config/**` edit (the `Ceiling-POE-FanPWM` compile-only
  candidate keeps `defer` + all blockers; its now-stale
  `CORE-ABSTRACT-BUS-001B-not-landed` label is flagged for a later
  refresh, not flipped); no `products/**`, `products/webflash/**`,
  `.github/workflows/**`, `components/**`, `include/**`, `firmware/**`,
  `manifest.json`, `firmware/sources.json`, or WebFlash-repo edit; no
  WebFlash / import / release / compliance / hardware-readiness claim.
  Release-One, the LED preview, and FanTRIAC (`blocked` / `HW-005`) are
  untouched.
- **SECURITY-AUDIT-FIX-001** closes, via **this PR** on 2026-05-25, the
  workflow-permissions hardening follow-up found by
  `REPO-FRESHNESS-ROADMAP-AUDIT-001` / PR #582 (security §5/§7 of
  [`docs/repo-freshness-roadmap-audit.md`](docs/repo-freshness-roadmap-audit.md)).
  **What was hardened:** all five workflows under `.github/workflows/`
  now declare an **explicit top-level `permissions:` block**. The three
  that previously declared none —
  [`validate.yml`](.github/workflows/validate.yml),
  [`compile-only.yml`](.github/workflows/compile-only.yml),
  [`ci-validate-configs.yml`](.github/workflows/ci-validate-configs.yml) —
  are pinned to least-privilege `permissions: contents: read`; and
  [`firmware-build-release.yml`](.github/workflows/firmware-build-release.yml)
  is narrowed from top-level `contents: write` to `contents: read`,
  keeping `contents: write` **only** on its `release` job (which attaches
  release assets via `softprops/action-gh-release`).
  [`release-notes-draft.yml`](.github/workflows/release-notes-draft.yml)
  already had `contents: read` and is unchanged. A new regression guard,
  [`tests/test_workflow_permissions.py`](tests/test_workflow_permissions.py),
  asserts: explicit top-level `permissions:` on every workflow, no
  `pull_request_target` trigger, no `permissions: write-all`, no
  unallowlisted `write` scope (only the `release` job's `contents: write`
  is allowlisted with a reason), and that every action `uses:` reference
  is SHA-pinned **or** in a documented mutable-major-tag allowlist. **What
  remains as follow-up:** GitHub Actions are still pinned to **mutable
  major tags** (`actions/checkout@v4`, `setup-python@v5`, `cache@v4`,
  `upload/download-artifact@v4`, `softprops/action-gh-release@v2`), **not**
  immutable commit SHAs; converting them (starting with the third-party
  `softprops/action-gh-release@v2`) is carried forward as
  **`SECURITY-ACTION-PINNING-001`**. The six actions are inventoried with
  the pinning policy in
  [`docs/workflow-security-hardening.md`](docs/workflow-security-hardening.md).
  **No security clean bill of health is claimed** — no Dependabot /
  code-scanning / secret-scanning **alert** feed was available, so no
  "no vulnerabilities" claim is made. **Hardening-only — no behaviour
  change:** token scopes were **tightened**, never widened or weakened; no
  validation step was removed or relaxed. Edits are confined to
  `.github/workflows/**` (security hardening only), `tests/**`, `docs/**`,
  and this file; **no** `packages/**`, `products/**`, `products/webflash/**`,
  `config/**`, `components/**`, `include/**`, `firmware/**`, `manifest.json`,
  `firmware/sources.json`, release artifact, checksum, or WebFlash-repo
  edit; **no** `webflash_build_matrix` flip, `artifact_name`, release
  artifact, or WebFlash-import / release / compliance / security
  clean-bill claim.
- **CONFIG-FRESHNESS-001** closes, via **this PR** on 2026-05-24, the
  single **`ACTIVE-STALE-RISK`** item found by
  `REPO-FRESHNESS-ROADMAP-AUDIT-001` / PR #582: the stale FanDAC
  full-compile narrative that still read `pending-ci` / `OWED` /
  "NOT full-compile-validated" (citing the superseded metadata-only run
  `26332462496`) in
  [`config/product-catalog.json`](config/product-catalog.json) (FanDAC
  `notes`) and
  [`products/sense360-ceiling-poe-fandac.yaml`](products/sense360-ceiling-poe-fandac.yaml)
  (header caveat + inline DAC-block comment). Both are reconciled to the
  canonical state already recorded by `FW-COMPILE-DAC-FULL-RESULT-001`
  (PR #580) and `COMPILE-STATUS-FLAGS-001` (PR #581): the full FanDAC
  ESPHome compile is **validated by run `26364679370`**
  (`workflow_dispatch` / `compile_mode=full`, 9 targets, conclusion
  `success`) and `compile_validation_status` is
  **`validated-full-compile`** in
  [`config/compile-only-targets.json`](config/compile-only-targets.json)
  (unchanged here — only asserted). The test that pinned the stale
  wording,
  `tests/test_dac_product_readiness.py::test_carries_full_compile_owed_caveat`,
  is replaced with `test_carries_full_compile_validated_caveat` (asserts
  `validated-full-compile` + run `26364679370`, and that the `pending-ci`
  token is gone), and
  [`docs/repo-freshness-roadmap-audit.md`](docs/repo-freshness-roadmap-audit.md)
  marks the two ACTIVE-STALE-RISK rows **RESOLVED**. **Narrative
  reconciliation only — no blocker moves:** the FanDAC product stays
  no-WebFlash / no-release / hardware-pending; `webflash_build_matrix`
  stays `false`; no `artifact_name`, no `products/webflash/` wrapper, no
  `config/webflash-builds.json` row, no release artifact; the catalog
  `status` enum stays `hardware-pending`; `WEBFLASH-DAC-001`,
  `RELEASE-DAC-001`, and `WF-IMPORT-DAC-001` stay **blocked**; `S360-312`
  `schematic_status` stays `cataloged_unverified`; the AirIQ-mutex /
  J3-silk / Cloudlift-S12 harness / single-range caveats are retained.
  No `packages/**`, `products/webflash/**`, `.github/workflows/**`,
  `components/**`, `include/**`, `firmware/**`, `manifest.json`,
  `firmware/sources.json`, or WebFlash-repo edit; no WebFlash-import /
  release / compliance / hardware-stable claim. FanRelay and Relay
  behaviour are untouched.
- **REPO-FRESHNESS-ROADMAP-AUDIT-001** delivers, via **this PR** on
  2026-05-24, an **audit / docs-only** sweep for stale config, old
  source-of-truth files, missed roadmap/feature/upgrade/security items, and
  cross-repo drift. Output:
  [`docs/repo-freshness-roadmap-audit.md`](docs/repo-freshness-roadmap-audit.md)
  (stale-files, source-of-truth, cross-repo-drift, roadmap-coverage,
  security/dependency, CI-coverage, and follow-up-queue tables). **Key
  findings:** (1) one logical stale active item — the FanDAC full-compile
  narrative still reads `pending-ci` / `OWED` in
  [`config/product-catalog.json`](config/product-catalog.json) and
  [`products/sense360-ceiling-poe-fandac.yaml`](products/sense360-ceiling-poe-fandac.yaml)
  (the exact narrative `COMPILE-STATUS-FLAGS-001` deferred above as "a
  separate follow-up", and **pinned** by
  `tests/test_dac_product_readiness.py::test_carries_full_compile_owed_caveat`)
  → **`CONFIG-FRESHNESS-001`**; (2) the WebFlash repo could **not** be read
  this session (access scoped to `esphome-public` / `esphome`), so cross-repo
  drift is `NEEDS-TOOLING` → **`WEBFLASH-DRIFT-001`**; (3) workflow hardening
  (no explicit `permissions:` on `validate.yml` / `compile-only.yml` /
  `ci-validate-configs.yml`; actions on mutable major tags) → **`SECURITY-AUDIT-FIX-001`**
  (no Dependabot/code-scanning alert feed available → **no** clean-bill
  claim); (4) PWM (`S360-311`) is the next hardware blocker now Relay/DAC
  full-compile are clean → **`PWM-BLOCKER-REMOVAL-001`**; (5) generated-matrix
  sync tests + full `unittest discover` are not auto-gated on PR →
  **`CI-GATE-HARDENING-001`**. **Audit-only — no real blocker moves:** the
  three readiness matrices were inspected and found **current at the headline
  level** and are left unedited; generated files
  ([`config/firmware-combination-matrix.json`](config/firmware-combination-matrix.json),
  [`docs/firmware-build-gap-report.md`](docs/firmware-build-gap-report.md))
  are verified in-sync (regeneration tests green). No `packages/**`,
  `products/**`, `products/webflash/**`, `config/**` behaviour,
  `.github/workflows/**`, `components/**`, `include/**`, `firmware/**`,
  `manifest.json`, `firmware/sources.json`, or WebFlash-repo edit; no
  `webflash_build_matrix` flip, no `artifact_name`, no release artifact, no
  WebFlash-import / release / compliance / security clean-bill claim.
  `S360-310` / `S360-312` `schematic_status` stays `cataloged_unverified`;
  `WEBFLASH-DAC-001` / `RELEASE-DAC-001` / `WF-IMPORT-DAC-001` stay blocked.
- **COMPILE-STATUS-FLAGS-001** reconciles, via **this PR** on 2026-05-24,
  the stale config-layer flag that `FW-COMPILE-DAC-FULL-RESULT-001`
  (PR #580) deferred as "a separate config-layer change". The FanDAC
  compile-only target's `compile_validation_status` in
  [`config/compile-only-targets.json`](config/compile-only-targets.json)
  is flipped `pending-ci` → **`validated-full-compile`** (the state proven
  green by the manual `workflow_dispatch` `compile_mode=full` run
  `26364679370`, 9 targets, conclusion `success`), its `reason` / `notes`
  wording is updated, and the two tests that pinned `pending-ci`
  ([`tests/test_compile_targets.py`](tests/test_compile_targets.py),
  [`tests/test_dac_product_readiness.py`](tests/test_dac_product_readiness.py))
  are updated to assert `validated-full-compile`. Docs that referenced the
  stale standing flag are reconciled
  ([`docs/compile-only-firmware-validation.md`](docs/compile-only-firmware-validation.md),
  [`docs/product-readiness-matrix.md`](docs/product-readiness-matrix.md),
  [`docs/webflash-exposure-readiness-matrix.md`](docs/webflash-exposure-readiness-matrix.md),
  [`docs/release-artifact-readiness-matrix.md`](docs/release-artifact-readiness-matrix.md),
  [`docs/hardware/s360-312-r4-fandac.md`](docs/hardware/s360-312-r4-fandac.md),
  this file). **Narrow status reconciliation only — no real blocker
  moves:** `PRODUCT-DAC-001` stays no-WebFlash / no-release;
  `WEBFLASH-DAC-001`, `RELEASE-DAC-001`, and `WF-IMPORT-DAC-001` stay
  **blocked**; `S360-310` / `S360-312` `schematic_status` stays
  `cataloged_unverified`; no `webflash_build_matrix` flip, no
  `artifact_name`, no release artifact, no compliance / safety claim. No
  `packages/**`, `products/**`, `products/webflash/**`, `.github/workflows/**`,
  `components/**`, `include/**`, `firmware/**`, `manifest.json`,
  `firmware/sources.json`, or WebFlash-repo edit;
  `config/product-catalog.json` and the product YAML are untouched (their
  full-compile-owed narrative is a separate follow-up). FanRelay carries no
  `compile_validation_status` field and is unchanged.
- **FW-COMPILE-DAC-FULL-RESULT-001** records, via **this PR** on
  2026-05-24 as a **docs-only** record, that the **successful manual
  full-compile run `26364679370`** — the same `workflow_dispatch`
  `compile_mode=full` run `FW-COMPILE-RELAY-FULL-RESULT-001` / PR #579
  recorded for FanRelay — **also validates the FanDAC compile-only
  target**. The run ran against post-#578 `main` (merge commit
  `4906a22`) and **passed** — Run ID `26364679370`, event
  `workflow_dispatch`, mode `compile_mode=full`, status `completed`,
  conclusion `success`, **9** compile-only targets (job `Compile-only
  Targets — Metadata Validation` `77606314361` `success` → `Compile-only
  Targets — Full ESPHome Compile` `77606324332` `success`). The
  `compile_mode=full` lane runs `esphome compile` against **every**
  [`config/compile-only-targets.json`](config/compile-only-targets.json)
  target via `scripts/validate_compile_targets.py --compile` and fails
  on the first failure, so the `success` conclusion proves all nine
  targets compiled — including the 9th,
  `ceiling-poe-fandac-compile-only` →
  [`products/compile-only/ceiling-poe-fandac.yaml`](products/compile-only/ceiling-poe-fandac.yaml)
  (`Ceiling-POE-FanDAC`), present in the manifest at `4906a22` with its
  YAML on disk. **This supersedes the full-compile concern left owed by
  `FW-COMPILE-DAC-RESULT-001` / PR #576** (which recorded only the green
  metadata lane — the full-compile job was `skipped` on PR #575's head),
  and **the GP8403 `voltage: 10V` enum fix is now compile-validated by
  ESPHome's own validator**. The `compile_validation_status: pending-ci`
  marker in
  [`config/compile-only-targets.json`](config/compile-only-targets.json)
  is satisfied by this run; flipping that literal config flag is a
  separate config-layer change outside this docs-only record (since done
  — see the `COMPILE-STATUS-FLAGS-001` bullet at the top of this queue).
  **`PRODUCT-DAC-001` has product YAML
  ([`products/sense360-ceiling-poe-fandac.yaml`](products/sense360-ceiling-poe-fandac.yaml),
  PR #577) but remains no-WebFlash / no-release**:
  `WEBFLASH-DAC-001`, `RELEASE-DAC-001`, and `WF-IMPORT-DAC-001` stay
  blocked; WebFlash import / release readiness is **not** claimed.
  **No** WebFlash wrapper; **no** `webflash_build_matrix` flip; **no**
  `artifact_name`; **no** entry in
  [`config/webflash-builds.json`](config/webflash-builds.json); **no**
  release artifact / checksum / build-info / `manifest.json` /
  `firmware/sources.json` / `.github/workflows/**` / `components/**` /
  `include/**` / `config/**` / `packages/**` / `products/**` /
  `scripts/**` / `tests/**` edit; **no** `schematic_status` /
  `schematic_file` promotion (`S360-312` stays `cataloged_unverified`);
  **no** `release_one_required_configs` change; **no** COMPLIANCE-001
  movement; **no** simultaneous per-output 0-5V + 0-10V on a single
  GP8403 claim; FanDAC / FanRelay code untouched. Compile success is
  necessary-but-insufficient for any shipment-readiness claim. Updates
  [`docs/compile-only-firmware-validation.md`](docs/compile-only-firmware-validation.md),
  [`docs/product-readiness-matrix.md`](docs/product-readiness-matrix.md),
  [`docs/webflash-exposure-readiness-matrix.md`](docs/webflash-exposure-readiness-matrix.md),
  [`docs/release-artifact-readiness-matrix.md`](docs/release-artifact-readiness-matrix.md),
  [`docs/hardware/s360-312-r4-fandac.md`](docs/hardware/s360-312-r4-fandac.md),
  and this `UPCOMING_PR.md`. The WebFlash repository
  (`sense360store/WebFlash`) is untouched. Validation: `python3
  tests/validate_configs.py`; `python3
  scripts/validate_compile_targets.py --metadata-only`; `python3
  tests/test_fandac_package.py`; `python3
  tests/test_dac_product_readiness.py`; `python3
  tests/test_compile_targets.py`; `python3
  tests/validate_webflash_builds.py`; `python3 -m unittest discover -s
  tests -p "test_*.py"`.
- **FW-COMPILE-RELAY-FULL-RESULT-001** records the **successful manual
  full-compile run** owed by `FW-COMPILE-RELAY-FULL-FIX-001` / PR #578 via
  **this PR** on 2026-05-24, as a **docs-only** record. A
  `workflow_dispatch` run of the `Compile-only Firmware Validation` lane
  with `compile_mode=full` ran against post-#578 `main` (merge commit
  `4906a22`) and **passed** — Run ID `26364679370`, event
  `workflow_dispatch`, mode `compile_mode=full`, status `completed`,
  conclusion `success`, **9** compile-only targets (job
  `Compile-only Targets — Metadata Validation` `77606314361` `success` →
  `Compile-only Targets — Full ESPHome Compile` `77606324332` `success`).
  **The previously failed full-compile run `26334334727` is superseded by
  this successful run `26364679370`** — the FanRelay target
  (`Ceiling-POE-VentIQ-FanRelay-RoomIQ`) now full-compiles green with the
  PR #578 shape-C single-owner fix (`relay_pin` unchanged at `GPIO3`).
  **The Relay product remains no-WebFlash / no-release**: `WEBFLASH-RELAY-001`,
  `RELEASE-RELAY-001`, and `WF-IMPORT-RELAY-001` stay blocked; WebFlash
  import / release readiness is **not** claimed. **No** WebFlash wrapper;
  **no** `webflash_build_matrix` flip; **no** `artifact_name`; **no** entry
  in [`config/webflash-builds.json`](config/webflash-builds.json); **no**
  release artifact / checksum / build-info / `manifest.json` /
  `firmware/sources.json` / `.github/workflows/**` / `components/**` /
  `include/**` / `config/**` / `packages/**` / `products/**` / `scripts/**` /
  `tests/**` edit; **no** `schematic_status` / `schematic_file` promotion
  (`S360-310` stays `cataloged_unverified`); **no** `release_one_required_configs`
  change; **no** COMPLIANCE-001 movement; FanDAC untouched. Compile success
  is necessary-but-insufficient for any shipment-readiness claim. Updates
  [`docs/compile-only-firmware-validation.md`](docs/compile-only-firmware-validation.md),
  [`docs/product-readiness-matrix.md`](docs/product-readiness-matrix.md),
  [`docs/webflash-exposure-readiness-matrix.md`](docs/webflash-exposure-readiness-matrix.md),
  [`docs/release-artifact-readiness-matrix.md`](docs/release-artifact-readiness-matrix.md),
  [`docs/hardware/s360-310-r4-relay.md`](docs/hardware/s360-310-r4-relay.md),
  and this `UPCOMING_PR.md`. The WebFlash repository
  (`sense360store/WebFlash`) is untouched. Validation: `python3
  tests/validate_configs.py`; `python3
  scripts/validate_compile_targets.py --metadata-only`; `python3
  tests/test_fan_relay_package.py`; `python3
  tests/test_relay_product_readiness.py`; `python3
  tests/test_compile_targets.py`; `python3
  tests/validate_webflash_builds.py`; `python3 -m unittest discover -s
  tests -p "test_*.py"`.
- **FW-COMPILE-RELAY-FULL-FIX-001** fixes the FanRelay `GPIO3`
  double-bind found by the full compile lane via **PR #578** on
  2026-05-24. The full-compile run **`26334334727`** **failed** on the
  FanRelay target (`Ceiling-POE-VentIQ-FanRelay-RoomIQ`); FanDAC
  validated cleanly and is **not** touched. Root cause: the parent Core
  abstract package
  [`packages/hardware/sense360_core_ceiling.yaml`](packages/hardware/sense360_core_ceiling.yaml)
  already declares the `main_relay` `switch.gpio` on `pin: ${relay_pin}`
  (`GPIO3` post-`CORE-ABSTRACT-BUS-001A`), and
  [`packages/expansions/fan_relay.yaml`](packages/expansions/fan_relay.yaml)
  declared a **second** `switch.gpio` (`id: fan_relay_switch`) on
  `pin: ${fan_relay_pin}` (default `${relay_pin}`), so composing both
  layers bound `GPIO3` twice. Fix (shape C — split ownership, no pin
  rebind): `fan_relay_switch` is now a `switch.template` that proxies
  the single Core `main_relay` GPIO owner; the package declares no
  `gpio` component and names no GPIO, the `fan_relay_pin` substitution
  is retired, and `${relay_pin}` stays abstract (`relay_pin` unchanged
  at `GPIO3`). Invariants pinned by the updated
  [`tests/test_fan_relay_package.py`](tests/test_fan_relay_package.py)
  (`FanRelaySwitchReusesMainRelayTests`, `FanRelayNoGpioPlatformTests`,
  `FanRelaySingleRelayGpioOwnerTests`, `FanDacCompileOnlyTargetUnchangedTests`).
  **The FanRelay readiness status is unchanged** —
  `advanced/manual-warning-only` + product-YAML-landed +
  WebFlash-blocked. **Full compile success is NOT claimed** — ESPHome
  was not available in the authoring environment, so `esphome config` /
  `scripts/validate_compile_targets.py --compile` were not run; a manual
  `workflow_dispatch` `compile_mode=full` rerun of the
  `Compile-only Firmware Validation` lane remains required to confirm
  the FanRelay target compiles green. This supersedes the
  FW-COMPILE-RELAY-RESULT-001 (2026-05-22) "successful full compile"
  claim, which run `26334334727` contradicted. **No** WebFlash wrapper;
  **no** `webflash_build_matrix` flip; **no** `artifact_name`; **no**
  entry in [`config/webflash-builds.json`](config/webflash-builds.json);
  **no** release artifact / checksum / build-info / `manifest.json` /
  `firmware/sources.json` / `.github/workflows/**` / `components/**` /
  `include/**` edit; **no** `schematic_status` / `schematic_file`
  promotion (`S360-310` stays `cataloged_unverified`); **no**
  `release_one_required_configs` change; **no** COMPLIANCE-001 movement;
  FanDAC package/product/target untouched. `WEBFLASH-RELAY-001`,
  `RELEASE-RELAY-001`, and `WF-IMPORT-RELAY-001` stay blocked; no
  WebFlash / release / import / compliance / competent-person sign-off
  claim is made. Updates
  [`packages/expansions/fan_relay.yaml`](packages/expansions/fan_relay.yaml),
  [`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`](products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml)
  (comments only),
  [`tests/test_fan_relay_package.py`](tests/test_fan_relay_package.py),
  [`docs/compile-only-firmware-validation.md`](docs/compile-only-firmware-validation.md),
  [`docs/product-readiness-matrix.md`](docs/product-readiness-matrix.md),
  [`docs/hardware/s360-310-r4-relay.md`](docs/hardware/s360-310-r4-relay.md)
  (new audit-log row), and this `UPCOMING_PR.md`. **Next recommended
  PR — now done:** the owed manual `workflow_dispatch` `compile_mode=full`
  rerun recording FanRelay full-compile green landed as
  `FW-COMPILE-RELAY-FULL-RESULT-001` (this PR; Run ID `26364679370`
  `success`), **not** WebFlash exposure. The WebFlash repository
  (`sense360store/WebFlash`) is untouched. Validation: `python3
  tests/validate_configs.py`; `python3
  scripts/validate_compile_targets.py --metadata-only`; `python3
  tests/test_core_abstract_bus.py`; `python3
  tests/test_fan_relay_package.py`; `python3
  tests/test_relay_product_readiness.py`; `python3
  tests/test_compile_targets.py`; `python3 -m unittest discover -s tests
  -p "test_*.py"`.
- **PRODUCT-DAC-001** advances the FanDAC chain to the **product layer**
  via **this PR** on 2026-05-23, as **product-YAML-only /
  no-WebFlash-exposure**. It adds the single canonical FanDAC product
  YAML [`products/sense360-ceiling-poe-fandac.yaml`](products/sense360-ceiling-poe-fandac.yaml)
  (config string `Ceiling-POE-FanDAC`) composing Core ceiling + PoE PSU +
  base/health with the canonical FanDAC alias
  [`packages/expansions/fan_dac.yaml`](packages/expansions/fan_dac.yaml)
  (→ `fan_gp8403.yaml`; two GP8403 DACs / four neutral outputs), plus a
  `hardware-pending`
  [`config/product-catalog.json`](config/product-catalog.json) row
  (`webflash_build_matrix: false`, no `artifact_name`, no
  `webflash_wrapper`). Outcome-first naming ("0-10V fan control" /
  "Cloudlift S12 fan control"); neutral package output IDs unchanged.
  **The full ESPHome `--compile` pass remains OWED** — only the
  compile-only **metadata** lane is green (FW-COMPILE-DAC-RESULT-001 /
  PR #576, Run ID `26332462496`); the manual `workflow_dispatch`
  `compile_mode=full` run is still owed and `compile_validation_status:
  pending-ci` stands (at PRODUCT-DAC-001 time; the run has since passed —
  `26364679370` — and the flag is now `validated-full-compile` per
  `COMPILE-STATUS-FLAGS-001`). The product YAML carries the
  full-compile-owed
  caveat, the `J3` `out0`/`out1` silkscreen transposition caveat, the
  Cloudlift S12 harness / product-bench caveat, the `FanDAC` ↔ `AirIQ`
  mutex (no AirIQ token), the per-chip (not per-output) output-range
  limitation, and the Nextion / `J7` out-of-scope note (no `uart:` /
  `display:` bound). The FW-COMPILE-DAC-001 compile-only skeleton
  [`products/compile-only/ceiling-poe-fandac.yaml`](products/compile-only/ceiling-poe-fandac.yaml)
  and its target are **unchanged** and stay separate. New
  [`tests/test_dac_product_readiness.py`](tests/test_dac_product_readiness.py)
  (44 cases) pins the non-WebFlash invariants + caveats; the superseded
  pre-PRODUCT-DAC-001 guards in
  [`tests/test_compile_targets.py`](tests/test_compile_targets.py) and
  [`tests/test_fandac_package.py`](tests/test_fandac_package.py) are
  updated to the landed-product reality. The regenerated
  [`config/firmware-combination-matrix.json`](config/firmware-combination-matrix.json)
  + [`docs/firmware-build-gap-report.md`](docs/firmware-build-gap-report.md)
  reclassify `Ceiling-POE-FanDAC` from `missing-product-yaml` to
  `blocked-hardware` (catalog `hardware-pending`, matching the FanRelay
  precedent). **No** WebFlash wrapper; **no** `webflash_build_matrix`
  flip; **no** `artifact_name`; **no** entry in
  [`config/webflash-builds.json`](config/webflash-builds.json) (the
  `FanDAC` token is absent there); **no** release artifact / checksum /
  build-info / `manifest.json` / `firmware/sources.json` /
  `.github/workflows/**` / `components/**` / `include/**` edit; **no**
  `schematic_status` / `schematic_file` promotion (`S360-312` stays
  `cataloged_unverified`); **no** `release_one_required_configs` change.
  **`WEBFLASH-DAC-001`, `RELEASE-DAC-001`, and `WF-IMPORT-DAC-001` remain
  blocked**; no full-compile-success, WebFlash, release, compliance, or
  hardware-stable readiness claim is made, and no simultaneous per-output
  0-5V + 0-10V on a single GP8403 is claimed. Updates
  [`docs/product-readiness-matrix.md`](docs/product-readiness-matrix.md),
  [`docs/webflash-exposure-readiness-matrix.md`](docs/webflash-exposure-readiness-matrix.md),
  [`docs/release-artifact-readiness-matrix.md`](docs/release-artifact-readiness-matrix.md),
  [`docs/kit-intent-matrix.md`](docs/kit-intent-matrix.md),
  [`docs/hardware/s360-312-r4-fandac.md`](docs/hardware/s360-312-r4-fandac.md)
  (new audit-log row), and this `UPCOMING_PR.md`. **Next recommended PR:**
  `FW-COMPILE-DAC-FULL-001` (record the still-owed manual
  `workflow_dispatch` `compile_mode=full` ESPHome compile before WebFlash
  planning) **or** `WEBFLASH-DAC-001-READINESS-REFRESH` (re-evaluate the
  WebFlash gate). The WebFlash repository (`sense360store/WebFlash`) is
  untouched. Validation: `python3 tests/validate_configs.py`; `python3
  scripts/validate_compile_targets.py --metadata-only`; `python3
  tests/test_dac_product_readiness.py`; `python3
  tests/test_fandac_package.py`; `python3
  tests/test_compile_targets.py`; `python3
  tests/test_firmware_combination_matrix.py`; `python3
  tests/test_firmware_build_gap_report.py`; `python3 -m unittest discover
  -s tests -p "test_*.py"`.
- **FW-COMPILE-DAC-RESULT-001** advances by a **docs-only record of the
  GitHub Actions compile-only validation result** via **this PR** on
  2026-05-23. It records the CI outcome for the FanDAC compile-only
  target added by `FW-COMPILE-DAC-001` / **PR #575**: the
  `Compile-only Firmware Validation` workflow ran against the expanded
  **nine-target** compile-only lane on the PR head and the
  **metadata-validation lane passed** — GitHub Actions Run ID
  `26332462496`, status `completed`, conclusion `success`, target count
  9; companion Quick Validation Run ID `26332462516` also succeeded.
  **Precise framing (recorded green, but honest):** the
  `Compile-only Targets — Full ESPHome Compile` job was **`skipped`** —
  it runs only on a manual `workflow_dispatch` with `compile_mode=full`
  ([`.github/workflows/compile-only.yml`](.github/workflows/compile-only.yml)
  line 103) — so **no `esphome config` / `esphome compile` ran against
  the FanDAC skeleton in CI**. The green result proves the metadata /
  structural lane (target shape, cross-references, count 9, guardrails,
  and the `voltage: 10V` enum pinned by
  [`tests/test_fandac_package.py`](tests/test_fandac_package.py) against
  ESPHome's **documented** `gp8403` schema), **not** a full ESPHome
  compile. `compile_validation_status: pending-ci` **stands** (at
  FW-COMPILE-DAC-RESULT-001 time; the full `--compile` pass has since
  passed in run `26364679370` and the flag is now
  `validated-full-compile` per `COMPILE-STATUS-FLAGS-001`). **DAC chain
  status refresh:** evidence done
  (PR #572); package done (PR #573); compile-only target done +
  voltage-enum fix done (PR #575); **compile-only (metadata) result
  passed** (this PR); next recommended PR **`PRODUCT-DAC-001`**, gated
  on the still-owed full `--compile` pass + `S360-312 schematic_status:
  verified`; WebFlash (`WEBFLASH-DAC-001`) / release (`RELEASE-DAC-001`)
  / import (`WF-IMPORT-DAC-001`) **still blocked**. Updates
  [`docs/compile-only-firmware-validation.md`](docs/compile-only-firmware-validation.md)
  (new `### 2026-05-23 — FW-COMPILE-DAC-RESULT-001` audit-log entry —
  workflow / run ID / conclusion / target count 9; jobs incl. the
  skipped full-compile; what it proves vs. does not prove),
  [`docs/product-readiness-matrix.md`](docs/product-readiness-matrix.md)
  (§FanDAC / S360-312 Status + compile-pass + next-PR bullets refreshed),
  [`docs/webflash-exposure-readiness-matrix.md`](docs/webflash-exposure-readiness-matrix.md)
  (§DAC / S360-312 posture note; `WEBFLASH-DAC-001` stays blocked),
  [`docs/release-artifact-readiness-matrix.md`](docs/release-artifact-readiness-matrix.md)
  (§DAC / S360-312 posture note; `RELEASE-DAC-001` stays blocked), and
  this `UPCOMING_PR.md` (this bullet + Completed / merged PRs row +
  active-queue items 14 / 15 refresh). **No** `packages/**` /
  `products/**` / `products/webflash/**` / `config/**` / `firmware/**` /
  `manifest.json` / `firmware/sources.json` / `scripts/**` /
  `.github/workflows/**` / `components/**` / `include/**` / `tests/**`
  edit; **no** release artifact / checksum / build-info; **no**
  `webflash_build_matrix` flip; **no** `artifact_name`; **no**
  `compile-only-targets.json` / `compile-only-candidates.json` edit
  (totals stay 9); **no** edit to `fan_gp8403.yaml` / `fan_dac.yaml`;
  **no** DAC product YAML; **no** WebFlash wrapper; **no**
  `schematic_status` promotion; **no** claim of compile success, DAC
  product / WebFlash / release readiness, compliance approval, or
  simultaneous per-output 0-5V + 0-10V on a single GP8403. The WebFlash
  repository (`sense360store/WebFlash`) is untouched. Validation:
  `python3 tests/validate_configs.py`; `python3
  scripts/validate_compile_targets.py --metadata-only`; `python3
  tests/test_core_abstract_bus.py`; `python3
  tests/test_fandac_alias_packages.py`; `python3
  tests/test_fandac_package.py`; `python3 tests/test_compile_targets.py`;
  `python3 tests/test_compile_expansion_candidates.py`; `python3
  tests/test_firmware_combination_matrix.py`; `python3
  tests/test_firmware_build_gap_report.py`; `python3
  tests/validate_webflash_builds.py`; `python3 -m unittest discover -s
  tests -p "test_*.py"`.
- **FW-COMPILE-DAC-001** advances by a **compile-only validation +
  package-fix** slice via **PR #575** on 2026-05-23. It adds
  compile-only / config-validation coverage for the FanDAC package
  after `PACKAGE-DAC-001` / PR #573 and `PRODUCT-DAC-001-READINESS-REFRESH`
  / PR #574, and **resolves the `gp8403:` `voltage:` enum concern
  (Option A)**: ESPHome's gp8403 component accepts only the bare enum
  `10V` / `5V` ([esphome.io/components/output/gp8403](https://esphome.io/components/output/gp8403)),
  so the package substitutions `fan_dac_1_output_range` /
  `fan_dac_2_output_range` in
  [`packages/expansions/fan_gp8403.yaml`](packages/expansions/fan_gp8403.yaml)
  are **fixed** from the invalid `0-10V` string to the valid `10V`
  (customer-facing 0-10V; the user-facing 0-10V / 0-5V labels stay in
  product / kit docs). This matches the default `10V` the output-range
  policy already implied (operator decision D3). A single compile-only
  target `ceiling-poe-fandac-compile-only`
  ([`products/compile-only/ceiling-poe-fandac.yaml`](products/compile-only/ceiling-poe-fandac.yaml),
  config string `Ceiling-POE-FanDAC`) is added under
  `products/compile-only/` (excluded from the product-catalog
  enumeration gate), composing Core ceiling + PoE PSU + base + health +
  the FanDAC alias `fan_dac.yaml`. **Compile success is NOT claimed
  until CI runs `scripts/validate_compile_targets.py --compile`**
  (ESPHome is not assumed present locally;
  `compile_validation_status: pending-ci` at FW-COMPILE-DAC-001 time —
  the CI `--compile` pass has since passed in run `26364679370` and the
  flag is now `validated-full-compile` per `COMPILE-STATUS-FLAGS-001`).
  The `--metadata-only` lane passes. **No DAC product YAML** at the top level of
  [`products/`](products/) and **no `config/product-catalog.json`
  entry** — `PRODUCT-DAC-001` stays gated (now on the CI compile pass +
  `S360-312 schematic_status: verified`). **No** WebFlash wrapper;
  **no** `config/webflash-builds.json` entry (the `FanDAC` token is
  absent there); **no** `webflash_build_matrix` flip; **no**
  `artifact_name`; **no** release artifact; **no**
  `firmware/**` / `manifest.json` / `firmware/sources.json` /
  `.github/workflows/**` / `components/**` / `include/**` edit; **no**
  `schematic_status` / `schematic_file` promotion; **no** claim of
  simultaneous per-output 0–5 V + 0–10 V on a single GP8403. Updates
  [`packages/expansions/fan_gp8403.yaml`](packages/expansions/fan_gp8403.yaml)
  (voltage enum fix),
  [`config/compile-only-targets.json`](config/compile-only-targets.json)
  (new target, totals 8→9),
  [`config/compile-only-candidates.json`](config/compile-only-candidates.json)
  (FanDAC row refresh + `currently_compile_only_config_strings`),
  [`tests/test_fandac_package.py`](tests/test_fandac_package.py) +
  [`tests/test_compile_targets.py`](tests/test_compile_targets.py)
  (enum + target coverage),
  [`docs/compile-only-firmware-validation.md`](docs/compile-only-firmware-validation.md),
  [`docs/product-readiness-matrix.md`](docs/product-readiness-matrix.md),
  [`docs/hardware/s360-312-r4-fandac.md`](docs/hardware/s360-312-r4-fandac.md),
  [`docs/webflash-exposure-readiness-matrix.md`](docs/webflash-exposure-readiness-matrix.md),
  [`docs/release-artifact-readiness-matrix.md`](docs/release-artifact-readiness-matrix.md),
  and this `UPCOMING_PR.md`. The WebFlash repository
  (`sense360store/WebFlash`) is untouched. Validation: `python3
  tests/validate_configs.py`; `python3
  scripts/validate_compile_targets.py --metadata-only`; `python3
  tests/test_core_abstract_bus.py`; `python3
  tests/test_fandac_alias_packages.py`; `python3
  tests/test_fandac_package.py`; `python3 tests/test_compile_targets.py`;
  `python3 tests/test_compile_expansion_candidates.py`; `python3
  tests/test_firmware_combination_matrix.py`; `python3
  tests/test_firmware_build_gap_report.py`; `python3
  tests/validate_webflash_builds.py`; `python3 -m unittest discover -s
  tests -p "test_*.py"`.
- **PRODUCT-DAC-001-READINESS-REFRESH** advances by a **docs /
  readiness-only** slice via **this PR** on 2026-05-23. It
  re-evaluates `PRODUCT-DAC-001` now that `PACKAGE-DAC-001` /
  **PR #573** implemented the FanDAC package at the package layer
  (two GP8403 chips, four neutral outputs, per-chip address + range
  substitutions, both ranges default `0-10V`). The refresh defines
  the **FanDAC product-layer gates** across the readiness matrices.
  Key finding: PR #573 feeds the `gp8403:` **`voltage:`** field the
  **neutral substitution value `0-10V`** rather than ESPHome's bare
  enum **`10V` / `5V`**; because **no FanDAC compile-only target
  exists**, this compile behaviour is **unvalidated** and must be
  treated as such. **Verdict: product YAML should wait on
  compile-only validation.** The recommended next PR is
  **`FW-COMPILE-DAC-001`** — a compile-only / config-validation slice
  that compiles the FanDAC package end-to-end and either confirms
  `0-10V` validates against the ESPHome enum or records the
  `0-10V` → `10V` fix (a `packages/**` edit) — **before**
  `PRODUCT-DAC-001` adds a product YAML (alternatively
  `PRODUCT-DAC-001` carries the `0-10V` → `10V` mapping itself).
  Product-layer gates recorded: the `J2` / `J3` board-level pin
  mapping is captured but the **Cloudlift S12 harness conductor
  trace** stays a product / bench item and the **`J3` `out0` / `out1`
  silkscreen transposition** must be carried into product docs /
  caveats; user-facing outputs map to **outcome-first** names
  (e.g. "0–10V fan control" / "Cloudlift S12 fan control"), not
  board-module jargon, while the package keeps its neutral output
  IDs; **Nextion / `J7` is out of scope** for the first DAC product
  unless that product drives a display; **WebFlash exposure
  (`WEBFLASH-DAC-001`) and release artifact (`RELEASE-DAC-001`)
  remain blocked**. Updates
  [`docs/product-readiness-matrix.md`](docs/product-readiness-matrix.md)
  (§FanDAC / S360-312 refreshed → `package-layer-implemented` +
  `compile-validation-pending`; candidate-table row; new
  `FW-COMPILE-DAC-001` + refreshed `PRODUCT-DAC-001` follow-up gate
  rows),
  [`docs/webflash-exposure-readiness-matrix.md`](docs/webflash-exposure-readiness-matrix.md)
  (§DAC / S360-312 WebFlash posture refresh-note + matrix row;
  exposure stays blocked),
  [`docs/release-artifact-readiness-matrix.md`](docs/release-artifact-readiness-matrix.md)
  (§DAC / S360-312 release posture refresh-note + matrix row;
  `RELEASE-DAC-001` stays blocked),
  [`docs/kit-intent-matrix.md`](docs/kit-intent-matrix.md)
  (`S360-KIT-DUCT-0-10V` status note; kit stays `future-expansion` /
  gated), and this `UPCOMING_PR.md` (this bullet + Completed / merged
  PRs row + active-queue `FW-COMPILE-DAC-001` entry + refreshed
  `PRODUCT-DAC-001` / `WEBFLASH-DAC-001` / `RELEASE-DAC-001` rows).
  **Docs / readiness only — no DAC product / WebFlash / release
  readiness is claimed and no compile validation is claimed (none was
  run).** **No** edit to
  [`packages/expansions/fan_gp8403.yaml`](packages/expansions/fan_gp8403.yaml)
  or [`packages/expansions/fan_dac.yaml`](packages/expansions/fan_dac.yaml);
  **no** DAC product YAML; **no** compile-only target; **no** WebFlash
  wrapper; **no** `webflash_build_matrix` flip; **no** `artifact_name`;
  **no** `products/**`, `products/webflash/**`, `config/**`,
  `scripts/**`, `.github/workflows/**`, `components/**`, `include/**`,
  `tests/**`, `firmware/**`, `manifest.json`, `firmware/sources.json`,
  release-artifact, checksum, or build-info edit; **no**
  `schematic_status` / `schematic_file` promotion (`S360-312` stays
  `cataloged_unverified`); **no** claim of simultaneous per-output
  0–5 V + 0–10 V on a single GP8403. The WebFlash repository
  (`sense360store/WebFlash`) is untouched. Validation: `python3
  tests/validate_configs.py`; `python3
  scripts/validate_compile_targets.py --metadata-only`; `python3
  tests/test_core_abstract_bus.py`; `python3
  tests/test_fandac_alias_packages.py`; `python3
  tests/test_fandac_package.py`; `python3 tests/test_compile_targets.py`;
  `python3 tests/test_compile_expansion_candidates.py`; `python3
  tests/test_firmware_combination_matrix.py`; `python3
  tests/test_firmware_build_gap_report.py`; `python3
  tests/validate_webflash_builds.py`; `python3 -m unittest discover -s
  tests -p "test_*.py"`.
- **PACKAGE-DAC-001-IMPLEMENT-001** advanced by a **package-layer
  implementation** slice via **PR #573** on 2026-05-23. It landed the
  YAML reconciliation that `HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001`
  (PR #572) marked implementation-plannable, applying operator
  decisions D1–D6 at the **package layer only**.
  [`packages/expansions/fan_gp8403.yaml`](packages/expansions/fan_gp8403.yaml)
  now binds **two** GP8403 chips (`fan_dac_1` / IC1, `fan_dac_2` /
  IC2) on the shared `${fan_dac_i2c_id}` (`core_i2c`) bus; exposes
  per-chip address substitutions `fan_dac_1_i2c_address` (`0x58`) /
  `fan_dac_2_i2c_address` (`0x59`); exposes per-chip output-range
  substitutions `fan_dac_1_output_range` / `fan_dac_2_output_range`
  (both default `0-10V`, independently overridable per chip via
  GP8403 register `0x01`); exposes **four** neutral outputs
  `fan_dac_1_vout0` / `fan_dac_1_vout1` / `fan_dac_2_vout0` /
  `fan_dac_2_vout1`; corrects the stale "(jumper selectable on
  hardware)" comment to firmware/register-driven; and records that a
  single GP8403 **cannot** mix 0–5 V / 0–10 V across its two outputs.
  The product-layer `fan:` / `sensor:` / `globals:` / `script:`
  blocks (hard-coded `${friendly_name}` fan names) were **removed** —
  they move to `PRODUCT-DAC-001`.
  [`packages/expansions/fan_dac.yaml`](packages/expansions/fan_dac.yaml)
  stays the canonical pure-wrapper `!include` (unchanged). Adds
  regression [`tests/test_fandac_package.py`](tests/test_fandac_package.py)
  (20 cases); [`tests/test_fandac_alias_packages.py`](tests/test_fandac_alias_packages.py)
  and the `fan_gp8403` case in
  [`tests/test_core_abstract_bus.py`](tests/test_core_abstract_bus.py)
  still pass. Refreshes
  [`docs/hardware/s360-312-r4-fandac.md`](docs/hardware/s360-312-r4-fandac.md)
  (new [§2026-05-23 — PACKAGE-DAC-001-IMPLEMENT-001](docs/hardware/s360-312-r4-fandac.md#2026-05-23--package-dac-001-implement-001)
  section + status line + audit-log row),
  [`docs/hardware/package-readiness-matrix.md`](docs/hardware/package-readiness-matrix.md)
  (`fan_gp8403.yaml` row + detail block → `package-layer-implemented`),
  [`docs/hardware/firmware-package-mapping-audit.md`](docs/hardware/firmware-package-mapping-audit.md)
  (cross-reference note), and this `UPCOMING_PR.md`. **Package layer
  only — product / WebFlash / release readiness remains blocked.**
  **No** DAC product YAML; **no** compile-only target; **no** WebFlash
  wrapper; **no** `webflash_build_matrix` flip; **no** `artifact_name`;
  **no** `products/**`, `products/webflash/**`, `config/**`,
  `scripts/**`, `.github/workflows/**`, `components/**`, `include/**`,
  `firmware/**`, `manifest.json`, `firmware/sources.json`,
  release-artifact, checksum, or build-info edit; **no**
  `schematic_status` / `schematic_file` promotion (`S360-312` stays
  `cataloged_unverified`); **no** claim of simultaneous per-output
  0–5 V + 0–10 V on a single GP8403; **no** DAC product / WebFlash /
  release / compliance readiness claim. Remaining product-level
  decisions move to `PRODUCT-DAC-001`. The WebFlash repository
  (`sense360store/WebFlash`) is untouched. Validation: `python3
  tests/validate_configs.py`; `python3
  scripts/validate_compile_targets.py --metadata-only`; `python3
  tests/test_core_abstract_bus.py`; `python3
  tests/test_fandac_alias_packages.py`; `python3
  tests/test_fandac_package.py`; `python3 tests/test_compile_targets.py`;
  `python3 tests/test_compile_expansion_candidates.py`; `python3
  tests/test_firmware_combination_matrix.py`; `python3
  tests/test_firmware_build_gap_report.py`; `python3
  tests/validate_webflash_builds.py`; `python3 -m unittest discover -s
  tests -p "test_*.py"`.
- **HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001** advanced by a **docs /
  evidence-only** slice via **PR #572** on 2026-05-22. That PR closed
  the `PACKAGE-DAC-001` rows that PR #571 left blocking (rows 3 / 6 /
  8) using two sources unavailable to PR #570 / PR #571: the **GP8403
  public datasheet** and the **`Fan_GP8403` (S360-312-R4) Google Drive
  layout assets** (KiCad PCB source, fabrication gerbers, board render
  images), plus the **operator design decisions** (two DAC chips /
  four outputs; per-DAC-chip range; both chips default 0–10 V;
  independent `IC1` / `IC2` override; expose address substitutions for
  both chips; do **not** claim per-output 0–5 V / 0–10 V mixing on a
  single GP8403). Findings: **row 3 (DIP-switch ↔ I²C-address truth
  table) CLOSED** — the datasheet fixes `A0` / `A1` / `A2` as address
  bits 0 / 1 / 2 (base `0x58`, span `0x58`–`0x5F`) and the KiCad PCB
  maps `SW1` → `A0` / `A1` / `A2` and `SW2` → `2A0` / `2A1` / `2A2`
  (opposite pole side to `GND`; closed = 0, open = 1), giving a full
  DIP-position → 7-bit-address truth table; **row 6 (output-range
  policy) CLOSED** — operator per-chip policy + datasheet register
  `0x01` (chip-level: write `0x00` → 0–5 V, `0x11` → 0–10 V), not
  per-output and not hardware-jumper; **row 8 (`J2` / `J3` silkscreen
  pin-1 identity) board-level CLOSED** — both connectors wire pin 1 =
  `VOUT0` / pin 2 = `GND` / pin 3 = `VOUT1`, `J2` silk matches the
  `IC1` channels while **`J3` silk `out0` / `out1` is transposed** vs
  the `IC2` channel nets (pin 1 silk `out1` = net `2vout0`). Verdict:
  **`PACKAGE-DAC-001` is now implementation-plannable**; the
  recommended next PR is **`PACKAGE-DAC-001-IMPLEMENT-001`** (bind two
  GP8403 devices with per-chip `${fan_dac_address}` /
  `${fan_dac_address_2}` and `${fan_dac_voltage_mode}` /
  `${fan_dac_voltage_mode_2}`; expose four outputs; correct the stale
  line-6 jumper comment). Residual **product / bench** items remain
  but do **not** block the package YAML: the harness conductor trace
  from `J2` / `J3` to the physical Cloudlift S12 fan (no fan / harness
  artifact exists in Drive); operator / bench confirmation of the `J3`
  `out0` / `out1` silk transposition; the as-shipped factory DIP
  positions; and the Module `J1` / Core `J7` `+3.3 V` / `+5 V` rail
  discrepancy (`S360-100-BENCH-001`). **Docs / evidence only.** Adds
  a [`docs/hardware/s360-312-r4-fandac.md` §2026-05-22 — HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001](docs/hardware/s360-312-r4-fandac.md#2026-05-22--hw-pinmap-312-followup-dac-evidence-001)
  section (operator-decision table; evidence-source provenance;
  GP8403 datasheet evidence; DIP-switch ↔ I²C-address truth table;
  output-range policy; `J2` / `J3` connector mapping; refreshed
  remaining-blocker table; verdict; recommended next PR) and a new
  2026-05-22 audit-log entry; refreshes
  [`docs/hardware/package-readiness-matrix.md`](docs/hardware/package-readiness-matrix.md)
  (`fan_gp8403.yaml` row + §`fan_gp8403.yaml` / S360-312 detail block
  + `PACKAGE-DAC-001-IMPLEMENT-001` follow-up PR row + per-slice
  gate-table row to mark rows 3 / 6 / 8 closed and the slice
  implementation-plannable); refreshes this `UPCOMING_PR.md` summary +
  the `PACKAGE-DAC-001-IMPLEMENT-001` queue entry. **No** `packages/**`
  edit (both
  [`packages/expansions/fan_gp8403.yaml`](packages/expansions/fan_gp8403.yaml)
  and
  [`packages/expansions/fan_dac.yaml`](packages/expansions/fan_dac.yaml)
  byte-identical). **No** `products/**`, `products/webflash/**`,
  `config/**`, `scripts/**`, `.github/workflows/**`, `components/**`,
  `include/**`, `firmware/**`, `manifest.json`, `firmware/sources.json`,
  `tests/**` edit. **No** `fan_gp8403.yaml` / `fan_dac.yaml` edit, **no**
  `PACKAGE-DAC-001` implementation, **no** DAC product YAML, **no**
  compile-only target, **no** WebFlash wrapper, **no**
  `webflash_build_matrix` flip, **no** `artifact_name`. **No**
  `schematic_status` / `schematic_file` promotion (`S360-312` stays
  `cataloged_unverified`). **No** DAC product / WebFlash / release
  readiness claim. **No** claim of simultaneous per-output 0–5 V +
  0–10 V on a single GP8403. The KiCad / gerber / image binaries stay
  **retained-but-not-committed** per the artifact policy (provenance +
  SHA256 of downloaded bytes recorded in the evidence section). **No**
  edit to the WebFlash repository (`sense360store/WebFlash`) — it is
  **read-only** for this PR. Validation: `python3
  tests/validate_configs.py`; `python3
  scripts/validate_compile_targets.py --metadata-only`; `python3
  tests/test_core_abstract_bus.py`; `python3
  tests/test_fandac_alias_packages.py`; `python3
  tests/test_compile_targets.py`; `python3
  tests/test_compile_expansion_candidates.py`; `python3
  tests/test_firmware_combination_matrix.py`; `python3
  tests/test_firmware_build_gap_report.py`; `python3
  tests/validate_webflash_builds.py`; `python3 -m unittest discover -s
  tests -p "test_*.py"`.
- **PACKAGE-DAC-001-READINESS-REFRESH** advanced by a **docs /
  readiness-only** slice via **PR #571** on 2026-05-22. That PR
  re-evaluated the 10 FanDAC-specific blockers enumerated in
  [`docs/hardware/s360-312-r4-fandac.md` Blockers remaining for PACKAGE-DAC-001](docs/hardware/s360-312-r4-fandac.md#blockers-remaining-for-package-dac-001)
  after `CORE-ABSTRACT-BUS-001B-IMPLEMENT-001` (PR #569) and
  `HW-PINMAP-312-FOLLOWUP` (PR #570) both landed on 2026-05-22.
  Adds a new
  [`docs/hardware/s360-312-r4-fandac.md` §PACKAGE-DAC-001 readiness refresh](docs/hardware/s360-312-r4-fandac.md#package-dac-001-readiness-refresh)
  section with a 10-row readiness table (blocker × previous state ×
  current state × evidence × still blocks `PACKAGE-DAC-001`? × what
  unblocks it), a verdict (`PACKAGE-DAC-001` is **not
  implementation-plannable yet**), and a recommended next PR
  (a DAC address / range / silkscreen evidence PR, provisionally
  `HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001` — **not**
  `PACKAGE-DAC-001-IMPLEMENT-001`). Rows 1 and 2 (shared-I²C-bus
  naming via PR #569; GP8403 BOM identity via PR #570) are
  **resolved**. Rows 5 and 7 (firmware/register-driven range
  mechanism; per-channel range mixing on a single GP8403 is **not**
  a hardware capability) are **evidence-captured**. Row 9 (Nextion
  / UART0) is **deferred out of `PACKAGE-DAC-001` scope** into a
  future product slice. Rows 3, 6, 8, and 10 **still block**: row 3
  (DIP-switch ↔ 7-bit I²C address truth table for `SW1` / `SW2`),
  row 6 (operator-requested firmware/product-selectable 0–5 V /
  0–10 V output-range policy decision), row 8 (`J2` / `J3` Cloudlift
  S12 silkscreen pin-1 identity + harness conductor trace), and
  row 10 (package YAML correctness — implementation-pending; gated
  on rows 3, 6, and 8). Refreshed cross-links in
  [`docs/hardware/package-readiness-matrix.md`](docs/hardware/package-readiness-matrix.md)
  (`fan_gp8403.yaml` row notes + §`fan_gp8403.yaml` / S360-312
  detail block + `PACKAGE-DAC-001-IMPLEMENT-001` follow-up PR row +
  per-slice gate-table row); refreshed the `PACKAGE-DAC-001` queue
  entry below. **No** `packages/**` edit (both
  [`packages/expansions/fan_gp8403.yaml`](packages/expansions/fan_gp8403.yaml)
  and
  [`packages/expansions/fan_dac.yaml`](packages/expansions/fan_dac.yaml)
  byte-identical). **No** `products/**` edit. **No**
  `products/webflash/**` edit. **No** `config/**` edit
  (`config/hardware-catalog.json`, `config/product-catalog.json`,
  `config/webflash-builds.json`, `config/webflash-compatibility.json`,
  `config/firmware-combination-matrix.json`,
  `config/kit-intent-matrix.json`, `config/compile-only-targets.json`,
  `config/compile-only-candidates.json` all byte-identical). **No**
  `scripts/**`, `.github/workflows/**`, `components/**`, `include/**`,
  `firmware/**`, `manifest.json`, `firmware/sources.json`, `tests/**`
  edit. **No** `webflash_build_matrix` flip. **No** `artifact_name`
  / `webflash_wrapper` / `config_string` /
  `release_one_required_configs` / `lifecycle_statuses` /
  `canonical_modules` / `canonical_power` / `forbidden_tokens` /
  `REQUIRED_CONFIGS` / kit change. **No** `schematic_status` /
  `schematic_file` promotion (`S360-312` stays
  `cataloged_unverified`; no `schematic_file` set). **No**
  COMPLIANCE-001 movement. **No** Release-One change
  (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`). **No** LED
  preview change (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`).
  **No** FanTRIAC change (`blocked` / `HW-005`). **No** compile-only
  target added. **No** firmware artifact built or attached. **No**
  release artifact / tag / checksum / build-info manifest / proof
  row. **No** WebFlash import readiness claim. **No** hardware
  release-readiness claim. **No** claim that `RELEASE-DAC-001`,
  `PRODUCT-DAC-001`, `WEBFLASH-DAC-001`, or `WF-IMPORT-DAC-001` are
  unblocked beyond what `CORE-ABSTRACT-BUS-001B-IMPLEMENT-001` and
  `HW-PINMAP-312-FOLLOWUP` already established. **No** claim of
  simultaneous one-channel-0–5 V and one-channel-0–10 V on a single
  GP8403 (the readiness refresh re-records this as a hard
  guardrail). **No** edit to the WebFlash repository
  (`sense360store/WebFlash`) — it is **read-only** for the purposes
  of this PR. Doc-side updates: refreshed
  [`docs/hardware/s360-312-r4-fandac.md`](docs/hardware/s360-312-r4-fandac.md)
  with the new §`PACKAGE-DAC-001 readiness refresh` section and a
  new 2026-05-22 audit-log entry for the readiness refresh;
  refreshed
  [`docs/hardware/package-readiness-matrix.md`](docs/hardware/package-readiness-matrix.md)
  (`fan_gp8403.yaml` row notes + §`fan_gp8403.yaml` / S360-312
  detail block + the `PACKAGE-DAC-001-IMPLEMENT-001` follow-up PR
  row + the per-slice gate-table row); refreshed this
  `UPCOMING_PR.md` queue summary and the `PACKAGE-DAC-001` queue
  entry. Validation: `python3 tests/validate_configs.py`;
  `python3 scripts/validate_compile_targets.py --metadata-only`;
  `python3 tests/test_core_abstract_bus.py`;
  `python3 tests/test_fandac_alias_packages.py`;
  `python3 tests/test_compile_targets.py`;
  `python3 tests/test_compile_expansion_candidates.py`;
  `python3 tests/test_firmware_combination_matrix.py`;
  `python3 tests/test_firmware_build_gap_report.py`;
  `python3 tests/validate_webflash_builds.py`;
  `python3 -m unittest discover -s tests -p "test_*.py"`.
- **HW-PINMAP-312-FOLLOWUP** advanced by a **docs / evidence /
  readiness-only** slice via **PR #570** on 2026-05-22.
  That PR added a new standalone schematic+BOM reference doc at
  [`docs/hardware/s360-312-r4-fandac.md`](docs/hardware/s360-312-r4-fandac.md)
  for the `S360-312-R4` Sense360 DAC (`Fan_GP8403`) board after the
  user supplied the same module-side schematic PDF (byte-identical
  to the already-committed schematic; SHA256
  `2888f626bfa0139d2190f154f9b02ecf4cb06f2522a5b5802eaf96e16de39e28`)
  plus a previously-not-recorded `Fan_GP8403.xlsx` BOM spreadsheet
  (SHA256
  `1886ecad5b9dd1a683b8c0ccebb770e5c02894854650b5a5553b19875f7e3a20`;
  12,744 bytes; 19 rows including header). The new reference doc
  follows the per-board pattern of
  [`s360-200-r4-roomiq.md`](docs/hardware/s360-200-r4-roomiq.md),
  [`s360-211-r4-ventiq.md`](docs/hardware/s360-211-r4-ventiq.md),
  and [`s360-300-r4-led.md`](docs/hardware/s360-300-r4-led.md), and
  it complements the broader HW-PINMAP-312 reconciliation audit at
  [`s360-312-r4-dac.md`](docs/hardware/s360-312-r4-dac.md). The doc
  consolidates: (i) the schematic+BOM-confirmed GP8403 variant
  (`GP8403-TC50-EW` from Guestgood — two chips `IC1` and `IC2`);
  (ii) the BOM-confirmed `219-3MSTR` 3-pole SPST DIP switches
  (`SW1` for `IC1`; `SW2` for `IC2`; CTS Electronic Components) and
  the six `4.7 kΩ` GP8403 address-pin pull-ups (`R3` / `R5` / `R7`
  for `IC1` `A0` / `A1` / `A2`; `R4` / `R6` / `R8` for `IC2` `2A0` /
  `2A1` / `2A2`); (iii) the MT3608 boost converter generating
  `+12V` from `+3.3V` for the GP8403 `V5V` rails (input cap `C1`,
  inductor `L1` `22 µH`, Schottky `D1 SS34`, output cap `C2`,
  feedback divider `R1 2 kΩ` / `R2 38 kΩ`); (iv) the `J1` 6-pin
  JST SH "From Core" connector (`SM06B-SRSS-TB(LF)(SN)`), the `J2`
  / `J3` 3-pin Phoenix-compatible terminal blocks
  (`MX350-3.5-03P-GN01-Cu-Y-A`), and the `J7` 4-pin JST PH Nextion
  connector (`B4B-PH-K-S(LF)(SN)`); (v) the
  schematic+BOM-grounded conclusion that GP8403 output-range
  selection (0–5 V vs 0–10 V) is **firmware/register-driven only**
  — there is no hardware jumper / solder bridge in the 19-row BOM,
  and the schematic ties each chip's `V5V` pin directly to the
  `+12V` MT3608 boost output, so the stale
  [`packages/expansions/fan_gp8403.yaml`](packages/expansions/fan_gp8403.yaml)
  header comment ("0-10V or 0-5V (jumper selectable on hardware)",
  file line 6) is not corroborated by visible hardware; (vi) the
  conservative finding that simultaneous one-channel-0–5 V and
  one-channel-0–10 V on a **single** GP8403 chip is **not** a
  hardware capability of this board (one `V5V` reference per chip),
  and that per-channel range mixing across the two DACs requires
  using one channel from each chip — no overclaim is made that the
  GP8403 supports per-channel range; (vii) the post-`CORE-ABSTRACT-
  BUS-001B-IMPLEMENT-001` (PR #569) bus state — `fan_gp8403.yaml`
  `${fan_dac_i2c_id}` default is `core_i2c`, resolving through the
  parent Core abstract package to the single shared bus on `GPIO48`
  / `GPIO45`; (viii) the BOM-confirmed observation that there is
  **no** `+5V` source on this board — the Nextion `J7` pin 1 `+5V`
  rail is an expected external supply, not a board-generated rail;
  (ix) a 10-row "Blockers remaining for `PACKAGE-DAC-001`" table
  enumerating what still gates the package slice; and (x) a
  10-row "What `CORE-ABSTRACT-BUS-001B` unblocked vs what remains
  blocked" table. **No** `packages/**` edit. **No** `products/**`
  edit. **No** `products/webflash/**` edit. **No** `config/**`
  edit (`config/hardware-catalog.json`, `config/product-catalog.json`,
  `config/webflash-builds.json`, `config/webflash-compatibility.json`,
  `config/firmware-combination-matrix.json`,
  `config/kit-intent-matrix.json`, `config/compile-only-targets.json`
  all byte-identical). **No** `scripts/**`, `.github/workflows/**`,
  `components/**`, `include/**`, `firmware/**`, `manifest.json`,
  `firmware/sources.json`, `tests/**` edit. **No**
  `webflash_build_matrix` flip. **No** `artifact_name`
  / `webflash_wrapper` / `config_string` /
  `release_one_required_configs` / `lifecycle_statuses` /
  `canonical_modules` / `canonical_power` / `forbidden_tokens` /
  `REQUIRED_CONFIGS` / kit change. **No** `schematic_status` /
  `schematic_file` promotion (`S360-312` stays
  `cataloged_unverified`; no `schematic_file` set). **No** COMPLIANCE-001
  movement. **No** Release-One change (`Ceiling-POE-VentIQ-RoomIQ`
  / `v1.0.0` / `stable`). **No** LED preview change
  (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`). **No** FanTRIAC
  change (`blocked` / `HW-005`). **No** edit to
  [`packages/expansions/fan_gp8403.yaml`](packages/expansions/fan_gp8403.yaml)
  or to its FanDAC alias
  [`packages/expansions/fan_dac.yaml`](packages/expansions/fan_dac.yaml).
  **No** compile-only target added. **No** firmware artifact built
  or attached. **No** release artifact / tag / checksum /
  build-info manifest / proof row. **No** WebFlash import readiness
  claim. **No** hardware release-readiness claim. **No** claim that
  `RELEASE-DAC-001`, `PRODUCT-DAC-001`, `WEBFLASH-DAC-001`, or
  `WF-IMPORT-DAC-001` are unblocked beyond what `CORE-ABSTRACT-BUS-001B-IMPLEMENT-001`
  already established. **No** edit to the WebFlash repository
  (`sense360store/WebFlash`) — it is **read-only** for the purposes
  of this PR. Doc-side updates: the new
  [`docs/hardware/s360-312-r4-fandac.md`](docs/hardware/s360-312-r4-fandac.md)
  file; refreshed notes on the `fan_gp8403.yaml` row in
  [`docs/hardware/package-readiness-matrix.md`](docs/hardware/package-readiness-matrix.md)
  (new 2026-05-22 evidence-consolidation paragraph; row-level
  evidence-source citation extended to the new reference doc;
  `§fan_gp8403.yaml / S360-312` detail block refreshed to point at
  the new reference doc and to record the schematic+BOM-grounded
  range-selection finding); refreshed FanDAC See-also entry in
  [`docs/hardware/firmware-package-mapping-audit.md`](docs/hardware/firmware-package-mapping-audit.md)
  (HW-009 still out-of-scope, but the FanDAC entry now points at
  the new reference doc and at the post-PR-#569 state); this
  `UPCOMING_PR.md` queue entry. Validation: `python3
  tests/validate_configs.py` (202 configs); `python3
  scripts/validate_compile_targets.py --metadata-only` (8 targets);
  `python3 tests/test_core_abstract_bus.py` (33 tests);
  `python3 tests/test_fandac_alias_packages.py` (12 tests);
  `python3 tests/test_compile_targets.py` (67 tests); `python3
  tests/test_compile_expansion_candidates.py` (37 tests); `python3
  tests/test_firmware_combination_matrix.py` (24 tests); `python3
  tests/test_firmware_build_gap_report.py` (27 tests); `python3
  tests/validate_webflash_builds.py` (2 builds); `python3 -m
  unittest discover -s tests -p "test_*.py"` (515 tests). All pass.
- **CORE-ABSTRACT-BUS-001B** has now **landed at the substitution
  layer** via **CORE-ABSTRACT-BUS-001B-IMPLEMENT-001 (PR #569)** on
  2026-05-22. The hard rename to the canonical shared `core_i2c` bus
  id (`GPIO48` SDA / `GPIO45` SCL / `400kHz`) is applied across the
  seven in-scope Core abstract packages
  (`sense360_core.yaml`, `sense360_core_ceiling.yaml`,
  `sense360_core_mapping.yaml`, `sense360_core_poe.yaml`,
  `sense360_core_wall.yaml`, `sense360_core_voice_ceiling.yaml`,
  `sense360_core_voice_wall.yaml`), the 10 in-scope expansion-package
  `*_i2c_id` consumer defaults (`airiq*.yaml`, `comfort*.yaml`,
  `airiq_bathroom*.yaml`, `fan_gp8403.yaml`,
  `gpio_expander_sx1509.yaml`), the hard-coded
  `i2c_id: halo_i2c` literal in `packages/features/ceiling_halo_leds.yaml`,
  the `tests/generate_test_configs.py` per-product override, and the
  new `SharedI2CBusTests` scaffold (13 cases) in
  `tests/test_core_abstract_bus.py`. The two S3-variant Core /
  expansion packages, the Mini family, the voice-variant Core
  `relay_pin: GPIO4`, every product YAML, every WebFlash wrapper,
  every JSON catalog, every release artifact, and every WebFlash
  exposure stay byte-for-byte unchanged. Static validation passes
  across all listed validators (515/515 stdlib tests pass; +13 vs
  the pre-001B baseline of 502). ESPHome was not available in the
  implementation environment, so the `esphome config`
  generated-config diff check against Release-One and the LED
  preview was not executed — the implementation relies on
  `tests/validate_configs.py` exits-0 across all 202 configs plus
  the new substitution-graph assertions. `PACKAGE-PWM-001` and
  `PACKAGE-DAC-001` are now unblocked **only at the shared-I²C-bus
  layer**; both still require `HW-PINMAP-311-FOLLOWUP` /
  `HW-PINMAP-312-FOLLOWUP` evidence and BOM cross-checks
  independently. No Release-One / LED preview / FanTRIAC / FanRelay
  / WebFlash / release identity changes. No compile-only target
  added. `S360-100-BENCH-001`, `HW-PINMAP-311-FOLLOWUP`,
  `HW-PINMAP-312-FOLLOWUP`, `HW-PINMAP-320-FOLLOWUP`, and
  `COMPLIANCE-001` are not closed by this PR.
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
- **PRODUCT-RELAY-001-READINESS-REFRESH** landed as **PR #563** and is
  a docs / readiness-only re-evaluation of the FanRelay
  **product-layer** disposition after `PACKAGE-RELAY-001` / PR #562
  implemented the package at the package layer only. It separated
  the package-layer implementation (landed) from the product-layer
  blockers that remained open: product onboarding; explicit
  installation / safety wording on any future FanRelay product
  YAML; explicit competent-person caveat (UK Building Regulations
  Part P-equivalent class — analogous to the FanTRIAC
  `advanced/manual-warning-only` long-term posture but at a
  lower-severity tier because the FanRelay product is on/off
  contact-side rather than phase-dimming); production-wide /
  multi-unit / oscilloscope-traced general ESP32-S3 `GPIO3`
  strap-pin boot-behaviour characterisation; board-level
  mains-safety / installation-approval / creepage / clearance /
  thermal / EMI evidence. The recommended product posture is
  recorded in `docs/product-readiness-matrix.md` §FanRelay /
  S360-310 as **`advanced/manual-warning-only`** +
  **product-YAML-allowed (no WebFlash exposure)** +
  **compile-only validation allowed** +
  **WebFlash exposure blocked**. `docs/webflash-exposure-readiness-matrix.md`
  §Relay / S360-310 WebFlash posture is refreshed to record that
  WebFlash Relay exposure remains **blocked** until
  `PRODUCT-RELAY-001` explicitly allows it (and even then a
  separate `WEBFLASH-RELAY-001` slice with its own
  production-wide / installation / competent-person gates is
  required); user-facing naming for any future Relay surface is
  outcome-first (e.g. "Relay fan control" or "Switched fan
  control"), not loose board / module naming.
  `docs/release-artifact-readiness-matrix.md` §Relay / S360-310
  release posture is refreshed to record that
  `RELEASE-RELAY-001` remains **blocked**; no release artifact
  exists; no release-proof row is added by this readiness refresh.
  `docs/kit-intent-matrix.md` §S360-KIT-BATH-RELAY narrative is
  refreshed to note that `PACKAGE-RELAY-001` has landed at the
  package layer while `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` /
  `RELEASE-RELAY-001` remain open; the kit stays
  `future-expansion` / `hardware-pending` /
  `webflash_exposure_allowed_now: false` /
  `stable_ready_now: false`; the default sellable kit remains
  `S360-KIT-BATH-POE` mapped to Release-One; Relay remains a
  fan-control option only when readiness permits. The
  recommended next PR is `PRODUCT-RELAY-001` implementation as a
  product-YAML-only / no-WebFlash-exposure slice (canonical
  FanRelay product YAML under `products/`; explicit advanced /
  manual-warning wording; installation / safety caveat;
  competent-person caveat; `docs/product-onboarding.md` safe
  sequence cleared; optional compile-only target under
  `config/compile-only-targets.json`), **not** a WebFlash
  wrapper / catalog flip / build-matrix entry / release artifact.
  No `packages/**`, `products/**`, `products/webflash/**`,
  `config/**`, `scripts/**`, `.github/workflows/**`,
  `components/**`, `include/**`, `firmware/**`, `manifest.json`,
  `firmware/sources.json`, `tests/**` edit; no
  `webflash_build_matrix` flip; no `artifact_name` /
  `webflash_wrapper` / `config_string` /
  `release_one_required_configs` / `lifecycle_statuses` /
  `canonical_modules` / `canonical_power` / `forbidden_tokens` /
  `REQUIRED_CONFIGS` / kit JSON change; no `schematic_status` /
  `schematic_file` promotion (`S360-310` stays
  `cataloged_unverified`); no COMPLIANCE-001 movement; no
  Release-One change (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` /
  `stable`); no LED preview change
  (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`); no FanTRIAC
  change (`blocked` / `HW-005`). **No claim of FanRelay
  product-readiness, WebFlash-readiness, release-readiness,
  compliance-clearance, board-level mains-safety certification,
  installation-approval, qualified-electrician sign-off, or
  production-wide / multi-unit hardware characterisation.** **No
  WebFlash import-readiness claim.** **No `RELEASE-RELAY-001`
  unblock claim.** **No `PACKAGE-RELAY-001` re-implementation.**
  No FanRelay product YAML. No WebFlash wrapper. No compile-only
  target for FanRelay. No release artifact / tag / checksum /
  build-info manifest. No hardware stable / release-readiness
  claim.
- **PRODUCT-RELAY-001** (this PR) implements the
  product-YAML-only / no-WebFlash-exposure slice the readiness
  refresh PR #563 recommended. Added the canonical FanRelay
  product YAML
  `products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`
  composing the Release-One PoE base stack (Core ceiling
  abstract + `packages/hardware/power_poe.yaml` + VentIQ +
  RoomIQ) plus `packages/expansions/fan_relay.yaml`. The
  FanRelay package inherits `${relay_pin}` from the parent Core
  abstract package binding (schematic-correct GPIO3 per
  `CORE-ABSTRACT-BUS-001A` / PR #558); the product YAML does
  NOT hard-code any GPIO. Header carries explicit advanced /
  manual-warning + installation / safety + competent-person
  caveat wording (mains switching / bathroom fan-control path;
  competent person where required; not WebFlash exposed; not
  default kit; not release artifact; not compliance
  certification; advanced / manual-warning only). Added a
  non-WebFlash row to `config/product-catalog.json`
  (`config_string: Ceiling-POE-VentIQ-FanRelay-RoomIQ`,
  `status: hardware-pending`, `webflash_build_matrix: false`,
  no `artifact_name`, no `webflash_wrapper`,
  `hardware_status: package-implemented-product-layer-pending`).
  Regenerated `config/firmware-combination-matrix.json`
  (one FanRelay row reclassifies from `missing-product-yaml` →
  `blocked-hardware`; 168-row total unchanged;
  `fanrelay-blocked-package-or-core-bus` lane count stays at
  36) and `docs/firmware-build-gap-report.md` via
  `scripts/generate_firmware_matrix.py` and
  `scripts/report_firmware_build_gaps.py`. Added new test
  `tests/test_relay_product_readiness.py` (42 stdlib-unittest
  cases) pinning: Relay product YAML exists; YAML composes
  FanRelay + Core ceiling + VentIQ + RoomIQ + PoE; YAML does
  NOT hard-code `GPIO3` (or any GPIO); catalog row carries
  `webflash_build_matrix: false`, no `artifact_name`, no
  `webflash_wrapper`; no FanRelay WebFlash wrapper file under
  `products/webflash/`; Relay config string is NOT in
  `config/webflash-builds.json` and NOT in
  `release_one_required_configs`; YAML carries the
  advanced / manual-warning + competent-person + installation /
  safety + not-WebFlash + not-default-kit + not-release-artifact +
  not-compliance-certified wording; the `S360-KIT-BATH-RELAY`
  kit stays `future-expansion` / `hardware-pending` /
  `webflash_exposure_allowed_now: false` /
  `stable_ready_now: false`; the default sellable bathroom kit
  remains `S360-KIT-BATH-POE` mapped to Release-One; and
  Release-One / LED preview / FanTRIAC catalog entries are
  unchanged. Tightened
  `tests/test_fan_relay_package.py`
  `PackageRelayDoesNotTouchWebFlashOrProductTests` to allow the
  single PRODUCT-RELAY-001 canonical FanRelay product YAML while
  still forbidding any additional FanRelay product YAML, any
  FanRelay wrapper under `products/webflash/`, and any
  `FanRelay` token in `config/webflash-builds.json`. Updated
  docs `docs/product-readiness-matrix.md` §FanRelay / S360-310
  (status + audit-log + Follow-up PR sequence row),
  `docs/webflash-exposure-readiness-matrix.md` §Relay / S360-310
  WebFlash posture (audit-log entry recording WebFlash exposure
  stays blocked even though product YAML landed),
  `docs/release-artifact-readiness-matrix.md` §Relay / S360-310
  release posture (audit-log entry recording release surface
  byte-identical; RELEASE-RELAY-001 stays blocked), and
  `docs/kit-intent-matrix.md` §S360-KIT-BATH-RELAY (kit narrative
  notes PRODUCT-RELAY-001 landed but kit remains
  `future-expansion` / `hardware-pending`; default sellable
  bathroom kit remains S360-KIT-BATH-POE on `stable`). **No
  `packages/**` edit (the FanRelay package is consumed as-is
  from PR #562 / PACKAGE-RELAY-001); no `products/webflash/**`
  edit; no `config/webflash-builds.json` edit; no
  `config/webflash-compatibility.json` edit; no
  `config/hardware-catalog.json` edit; no
  `config/kit-intent-matrix.json` edit; no `scripts/**` edit
  (only generator outputs refreshed); no `.github/workflows/**`,
  `components/**`, `include/**`, `firmware/**`, `manifest.json`,
  `firmware/sources.json` edit. No `webflash_build_matrix`
  flip; no `artifact_name`; no `webflash_wrapper`; no
  `release_one_required_configs` change; no
  `lifecycle_statuses` change; no `canonical_modules` /
  `canonical_power` / `forbidden_tokens` change; no
  `REQUIRED_CONFIGS` / kit JSON change; no `schematic_status` /
  `schematic_file` promotion (`S360-310` stays
  `cataloged_unverified`); no COMPLIANCE-001 movement.**
  Release-One stays `Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` /
  `stable`; LED preview stays `Ceiling-POE-VentIQ-RoomIQ-LED` /
  `preview`; FanTRIAC stays `blocked` / `HW-005`. **No claim of
  FanRelay WebFlash-readiness, release-readiness,
  compliance-clearance, board-level mains-safety certification,
  installation-approval, qualified-electrician sign-off, or
  production-wide / multi-unit hardware characterisation.** **No
  WebFlash import-readiness claim. No RELEASE-RELAY-001 unblock
  claim. No WEBFLASH-RELAY-001 unblock claim. No
  WF-IMPORT-RELAY-001 unblock claim.** No WebFlash wrapper / no
  compile-only target / no release artifact / no tag / no
  checksum / no build-info manifest. The recommended next Relay
  chain PR is `WEBFLASH-RELAY-001-READINESS-REFRESH` (docs-only
  readiness re-evaluation after PRODUCT-RELAY-001 lands), not
  immediate `WEBFLASH-RELAY-001` exposure work, unless the new
  product YAML fails compile-only validation in a later run.
- **WEBFLASH-RELAY-001-READINESS-REFRESH** (this PR) is a docs /
  readiness-only re-evaluation of the FanRelay **WebFlash-layer**
  disposition after `PRODUCT-RELAY-001` / PR #564 landed the
  canonical FanRelay product YAML
  `products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml` and a
  non-WebFlash catalog row (`config_string:
  Ceiling-POE-VentIQ-FanRelay-RoomIQ`, `status: hardware-pending`,
  `webflash_build_matrix: false`, no `artifact_name`, no
  `webflash_wrapper`) without any WebFlash wrapper / build-matrix
  row / release artifact. Re-verified against the live files: no
  FanRelay WebFlash wrapper under `products/webflash/` (only
  Release-One, LED preview, and the blocked FanTRIAC reference);
  no FanRelay row in `config/webflash-builds.json` (only
  Release-One stable + LED preview); `FanRelay` is reserved in
  `config/webflash-compatibility.json` `canonical_modules` (line
  11) with no `webflash_build_matrix: true` consumer
  (reservation-only, not exposure);
  `release_one_required_configs` stays
  `["Ceiling-POE-VentIQ-RoomIQ"]`; the PRODUCT-RELAY-001 catalog
  row is byte-identical and is **not** flipped; the
  `S360-KIT-BATH-RELAY` row in `config/kit-intent-matrix.json`
  stays `future-expansion` / `hardware-pending` /
  `webflash_exposure_allowed_now: false` /
  `stable_ready_now: false`. **WebFlash Relay exposure remains
  blocked.** The readiness refresh enumerates seven WebFlash
  gates that any future `WEBFLASH-RELAY-001` slice must clear
  (explicit `WEBFLASH-RELAY-001` implementation approval;
  advanced / manual-warning UI copy; competent-person /
  installation warning flow; product not default / not
  recommended; release artifact must exist before WebFlash
  import; no stable / preview promotion until explicit approval;
  production-wide / installation / safety caveats remain
  separate) and four possible exposure shapes
  `WEBFLASH-RELAY-001` could take (blocked entirely; advanced /
  manual-warning import only; hidden / manual mode only; or
  compile-only / no-runtime exposure under a future
  `FW-COMPILE-RELAY-001`). User-facing naming policy is
  reaffirmed as **outcome-first** (e.g. "Switched fan control"
  or "Relay fan control"), not loose board / module naming
  ("S360-310 board"); the cross-repo WebFlash UI already ships
  the outcome-first label "Fan relay control" in Step 4 and
  "Sense360 Bathroom Kit — Relay Fan Control" in the Stage 1
  bundle preset `S360-KIT-BATH-RELAY` (status `planned`,
  non-installable). WebFlash repo posture re-read read-only:
  `firmware/sources.json` has no FanRelay source; `manifest.json`
  carries no FanRelay build; `REQUIRED_CONFIGS` stays
  `["Ceiling-POE-VentIQ-RoomIQ", "Rescue"]`;
  `scripts/data/kits.json` stays Release-One-only;
  `scripts/utils/module-availability.js` keeps Sense360 Relay
  (S360-310) at `design-pending`; the WebFlash
  `WF-IMPORT-RELAY-001` queue item stays **blocked** behind
  upstream `RELEASE-RELAY-001`. **`RELEASE-RELAY-001` remains
  blocked**: no FanRelay release artifact exists, no
  release-proof row is added by this readiness refresh, the
  atomic `RELEASE-RELAY-001` slice (build / sign / attach the
  `.bin`, generate release notes, emit SHA256 + MD5 checksums,
  attach the build-info `manifest.json`, record the
  release-proof row, hand off to WebFlash-side import) remains
  owed. Updated `docs/webflash-exposure-readiness-matrix.md`
  §Relay / S360-310 WebFlash posture (top-table chain row
  refreshed; `WEBFLASH-RELAY-001-READINESS-REFRESH` audit-log
  entry appended; new "Remaining WebFlash gates" sub-section
  enumerates the seven gates; new "Possible exposure classes"
  sub-section enumerates the four eventual shapes);
  `docs/release-artifact-readiness-matrix.md` §Relay / S360-310
  release posture (new `WEBFLASH-RELAY-001-READINESS-REFRESH`
  audit-log entry recording `RELEASE-RELAY-001` remains
  blocked, no artifact exists, no release-proof row added);
  `docs/kit-intent-matrix.md` §S360-KIT-BATH-RELAY (new
  `WEBFLASH-RELAY-001-READINESS-REFRESH` status update
  recording that the kit has a product YAML upstream but still
  no WebFlash exposure and not default; default kit remains
  `S360-KIT-BATH-POE`); and `UPCOMING_PR.md` (this entry +
  Active / upcoming queue refresh). **No `packages/**`,
  `products/**`, `products/webflash/**`, `config/**`,
  `scripts/**`, `.github/workflows/**`, `components/**`,
  `include/**`, `firmware/**`, `manifest.json`,
  `firmware/sources.json`, `tests/**`, release-artifact,
  checksum, build-info manifest, or WebFlash-repo edit; no
  `webflash_build_matrix` flip; no `artifact_name`; no
  `webflash_wrapper`; no `config_string`; no
  `release_one_required_configs` change; no
  `lifecycle_statuses` change; no `canonical_modules` /
  `canonical_power` / `forbidden_tokens` change; no
  `REQUIRED_CONFIGS` / kit JSON change; no `schematic_status` /
  `schematic_file` promotion** (`S360-310` stays
  `cataloged_unverified`); **no COMPLIANCE-001 movement**.
  Release-One stays `Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` /
  `stable`; LED preview stays `Ceiling-POE-VentIQ-RoomIQ-LED` /
  `preview`; FanTRIAC stays `blocked` / `HW-005`. **No claim of
  FanRelay WebFlash import-readiness, release-readiness,
  compliance-clearance, board-level mains-safety
  certification, installation-approval, qualified-electrician
  sign-off, production-wide / multi-unit hardware
  characterisation, `RELEASE-RELAY-001` unblock,
  `WEBFLASH-RELAY-001` unblock, `WF-IMPORT-RELAY-001` unblock,
  kit-default-readiness, recommended-bundle readiness, or
  stable-channel readiness.** The recommended next Relay-chain
  PR is one of `WEBFLASH-RELAY-001` implementation plan /
  scaffold only (if allowed by the project lead),
  `RELEASE-RELAY-001` (blocked until artifact path exists), or
  `FW-COMPILE-RELAY-001` (if compile-only validation should
  happen first); **not** immediate `WEBFLASH-RELAY-001` wrapper
  / catalog / build-matrix work.
- **FW-COMPILE-RELAY-001** merged as **PR #566** on 2026-05-22 and
  added a single FanRelay compile-only validation target to
  `config/compile-only-targets.json` pointing at the
  PRODUCT-RELAY-001 / PR #564 canonical FanRelay product YAML
  `products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`.
  The target carries `shipment_status: compile-only`,
  `webflash_exposure_allowed_now: false`,
  `hardware_required_for_validation: true`,
  `advanced_manual_warning_only: true`,
  `hardware_pending: true`, and `blocked: false`. Totals updated
  from 7 → 8. Synchronised
  `config/compile-only-candidates.json`
  `currently_compile_only_config_strings` (the doc ledger that
  pins what is actually in the compile-only target file)
  extended by one entry to match. Added the new
  `FanRelayCompileOnlyCoverageTests` class to
  `tests/test_compile_targets.py` (22 stdlib-unittest cases
  pinning: FanRelay compile-only target exists; points at the
  PRODUCT-RELAY-001 product YAML; config string is
  `Ceiling-POE-VentIQ-FanRelay-RoomIQ`; present in
  `config/firmware-combination-matrix.json`;
  `shipment_status: compile-only`;
  `webflash_exposure_allowed_now: false`;
  `hardware_required_for_validation: true`;
  `advanced_manual_warning_only: true`; `hardware_pending: true`;
  `blocked: false`; no `webflash_build_matrix` / `artifact_name`
  / `webflash_wrapper` / `expected_channel` declarations; not in
  `config/webflash-builds.json`; no `FanRelay` token in
  `config/webflash-builds.json`; not in
  `release_one_required_configs`; product YAML does not live
  under `products/webflash/`; no FanRelay WebFlash wrapper file
  exists; Release-One and LED preview compile-only targets
  unchanged; totals match expected target count after add).
  Refactored the existing
  `PoeNonFanCompileOnlyCoverageTests` fan / PWR-token guardrails
  (`test_this_pr_introduces_no_fan_compile_only_target` /
  `test_this_pr_introduces_no_pwr_compile_only_target`) to scope
  to `products/compile-only/` (the FW-COMPILE-POE-NONFAN-001
  directory) and renamed them
  `test_poe_nonfan_lane_introduces_no_fan_compile_only_target` /
  `test_poe_nonfan_lane_introduces_no_pwr_compile_only_target`
  so the FW-COMPILE-RELAY-001 target (which lives at
  `products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`,
  not under `products/compile-only/`) no longer trips the lane
  guard. Added the new `RelayProductCompileOnlyTargetTests` class
  to `tests/test_relay_product_readiness.py` (17 cases pinning
  the same invariants from the product-readiness angle). Updated
  `docs/compile-only-firmware-validation.md` (new
  `### 2026-05-22 — FW-COMPILE-RELAY-001 FanRelay compile-only
  validation` audit-log entry — target table, lower-risk
  rationale referencing the closed CORE-ABSTRACT-BUS-001A / 001C
  / PACKAGE-RELAY-001 / S360-310-BENCH-EVIDENCE-001 /
  PRODUCT-RELAY-001 / WEBFLASH-RELAY-001-READINESS-REFRESH
  chain, what compile-only proves for the FanRelay target, what
  compile-only does **not** prove);
  `docs/webflash-exposure-readiness-matrix.md` §Relay / S360-310
  WebFlash posture (new 2026-05-22 `FW-COMPILE-RELAY-001`
  audit-log note explicitly recording WebFlash exposure remains
  blocked, the seven WebFlash gates not advanced, the four
  possible exposure shapes unchanged);
  `docs/release-artifact-readiness-matrix.md` §Relay / S360-310
  release posture (new 2026-05-22 `FW-COMPILE-RELAY-001`
  audit-log note explicitly recording `RELEASE-RELAY-001`
  remains blocked, no FanRelay release artifact exists, no
  release-proof row is added). **No `packages/**`, `products/**`,
  `products/webflash/**`, `config/webflash-builds.json`,
  `config/webflash-compatibility.json`,
  `config/hardware-catalog.json`,
  `config/kit-intent-matrix.json`,
  `config/firmware-combination-matrix.json`,
  `config/product-catalog.json`, `scripts/**`,
  `.github/workflows/**`, `components/**`, `include/**`,
  `firmware/**`, `manifest.json`, `firmware/sources.json`,
  release-artifact, checksum, build-info manifest, or
  WebFlash-repo edit; no `webflash_build_matrix` flip; no
  `artifact_name`; no `webflash_wrapper`; no `config_string`
  change; no `release_one_required_configs` change; no
  `lifecycle_statuses` change; no `canonical_modules` /
  `canonical_power` / `forbidden_tokens` change; no
  `REQUIRED_CONFIGS` / kit JSON change; no `schematic_status` /
  `schematic_file` promotion** (`S360-310` stays
  `cataloged_unverified`); **no COMPLIANCE-001 movement**.
  Release-One stays `Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` /
  `stable`; LED preview stays `Ceiling-POE-VentIQ-RoomIQ-LED` /
  `preview`; FanTRIAC stays `blocked` / `HW-005`; voice-variant
  Core packages stay at pre-001A `relay_pin: GPIO4`. **No claim
  of FanRelay WebFlash import-readiness, WebFlash exposure
  readiness, release-readiness, compliance-clearance,
  board-level mains-safety certification, installation-approval,
  competent-person sign-off, production-wide / multi-unit
  hardware characterisation, `RELEASE-RELAY-001` unblock,
  `WEBFLASH-RELAY-001` unblock, `WF-IMPORT-RELAY-001` unblock,
  kit-default-readiness, recommended-bundle readiness, or
  stable-channel readiness.** Compile-only validation is
  **necessary-but-insufficient** input to the broader
  preview-to-stable promotion process; it does **not** discharge
  any of the seven WebFlash gates owned by `WEBFLASH-RELAY-001`,
  and does **not** discharge any release-readiness gate owned by
  `RELEASE-RELAY-001`. The recommended next Relay-chain PR is
  one of `WEBFLASH-RELAY-001` implementation plan / scaffold
  only (if allowed by the project lead), `RELEASE-RELAY-001`
  (still blocked until artifact path exists), or, if any future
  ESPHome upgrade breaks compile, a targeted compile fix for the
  FanRelay compile-only target only; **not** immediate
  `WEBFLASH-RELAY-001` wrapper / catalog / build-matrix work.
- **FW-COMPILE-RELAY-RESULT-001** (this PR) records the
  **successful GitHub Actions compile-only validation result**
  for the FanRelay compile-only target added by
  `FW-COMPILE-RELAY-001` / PR #566. The
  `Compile-only Firmware Validation` workflow ran against the
  expanded eight-target compile-only lane and **passed** —
  GitHub Actions Run ID `26298089904`, status `completed`,
  conclusion `success`, PR/head validation for PR #566;
  companion Quick Validation Run ID `26298090061` also
  succeeded. **FanRelay compile-only validation now has a green
  CI result.** Relay-chain status refresh: **package done**
  (PR #562 `PACKAGE-RELAY-001`); **product YAML done** (PR #564
  `PRODUCT-RELAY-001`); **compile-only target done** (PR #566
  `FW-COMPILE-RELAY-001`); **compile-only result passed** (this
  PR); WebFlash / release / import **still blocked** (no
  FanRelay WebFlash wrapper under `products/webflash/`; no
  FanRelay row in `config/webflash-builds.json`; no FanRelay
  `.bin` / tag / checksum / build-info manifest / release-proof
  row; no WebFlash-side import). Updated
  `docs/compile-only-firmware-validation.md` (new
  `### 2026-05-22 — FW-COMPILE-RELAY-RESULT-001` audit-log entry
  recording the run ID, workflow completion, conclusion, target
  count of 8, what the run proves, and what it does not prove);
  `docs/webflash-exposure-readiness-matrix.md` §Relay / S360-310
  WebFlash posture (new 2026-05-22 `FW-COMPILE-RELAY-RESULT-001`
  audit-log note recording the green CI result while explicitly
  recording WebFlash exposure remains blocked; the seven
  WebFlash gates not advanced; the four possible exposure shapes
  unchanged); `docs/release-artifact-readiness-matrix.md` §Relay
  / S360-310 release posture (new 2026-05-22
  `FW-COMPILE-RELAY-RESULT-001` audit-log note recording the
  green CI result while explicitly recording `RELEASE-RELAY-001`
  remains blocked because no WebFlash wrapper / build matrix /
  artifact path exists; no release-proof row is added); and
  `UPCOMING_PR.md` (this entry + Completed / merged PRs row +
  Active / upcoming queue item #8 refresh). **No `packages/**`,
  `products/**`, `products/webflash/**`,
  `config/compile-only-targets.json`,
  `config/compile-only-candidates.json`,
  `config/webflash-builds.json`,
  `config/webflash-compatibility.json`,
  `config/hardware-catalog.json`,
  `config/kit-intent-matrix.json`,
  `config/firmware-combination-matrix.json`,
  `config/product-catalog.json`, `scripts/**`,
  `.github/workflows/**`, `components/**`, `include/**`,
  `firmware/**`, `manifest.json`, `firmware/sources.json`,
  `tests/**`, release-artifact, checksum, build-info manifest,
  or WebFlash-repo edit; no `webflash_build_matrix` flip; no
  `artifact_name`; no `webflash_wrapper`; no `config_string`
  change; no `release_one_required_configs` change; no
  `lifecycle_statuses` change; no `canonical_modules` /
  `canonical_power` / `forbidden_tokens` change; no
  `REQUIRED_CONFIGS` / kit JSON change; no `schematic_status` /
  `schematic_file` promotion** (`S360-310` stays
  `cataloged_unverified`); **no COMPLIANCE-001 movement**.
  Release-One stays `Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` /
  `stable`; LED preview stays `Ceiling-POE-VentIQ-RoomIQ-LED` /
  `preview`; FanTRIAC stays `blocked` / `HW-005`. **No claim of
  FanRelay WebFlash import-readiness, WebFlash exposure
  readiness, release-readiness, compliance-clearance,
  board-level mains-safety certification, installation-approval,
  competent-person sign-off, production-wide / multi-unit
  hardware characterisation, `RELEASE-RELAY-001` unblock,
  `WEBFLASH-RELAY-001` unblock, `WF-IMPORT-RELAY-001` unblock,
  kit-default-readiness, recommended-bundle readiness,
  hardware-stable readiness, or stable-channel readiness.** A
  green compile-only CI result is
  **necessary-but-insufficient** input to the broader
  preview-to-stable promotion process; it does **not** discharge
  any of the seven WebFlash gates owned by `WEBFLASH-RELAY-001`,
  and does **not** discharge any release-readiness gate owned by
  `RELEASE-RELAY-001`. The recommended next Relay-chain PR is
  one of `WEBFLASH-RELAY-001-SCAFFOLD-001` (if WebFlash Relay
  planning continues) or `CORE-ABSTRACT-BUS-001B` (if PWM / DAC
  blocker removal is prioritised instead); **not** immediate
  `WEBFLASH-RELAY-001` wrapper / catalog / build-matrix work.
- **CORE-ABSTRACT-BUS-001B-IMPLEMENT-001** (this PR) applies the
  schematic-correct hard rename to the canonical shared
  `core_i2c` bus id recorded by `CORE-ABSTRACT-BUS-001B-PLAN-001`
  (PR #568). The seven in-scope Core abstract packages
  (`packages/hardware/sense360_core.yaml`,
  `packages/hardware/sense360_core_ceiling.yaml`,
  `packages/hardware/sense360_core_mapping.yaml`,
  `packages/hardware/sense360_core_poe.yaml`,
  `packages/hardware/sense360_core_wall.yaml`,
  `packages/hardware/sense360_core_voice_ceiling.yaml`,
  `packages/hardware/sense360_core_voice_wall.yaml`) each replace
  the dual-bus block with the single shared
  `i2c: - id: core_i2c, sda: GPIO48, scl: GPIO45, frequency: 400kHz`
  block; the legacy `halo_i2c` / `expansion_i2c` / `i2c0` / `i2c1` /
  `i2c_primary` / `i2c_expander` ids and their `i2c0_*` / `i2c1_*` /
  `halo_i2c_*` / `expansion_i2c_*` pin substitutions are retired
  (hard rename only, no compatibility aliases). The 10 in-scope
  expansion-package `*_i2c_id` consumer defaults are rebound to
  `core_i2c` (`airiq.yaml`, `airiq_wall.yaml`, `airiq_ceiling.yaml`,
  `airiq_bathroom_base.yaml`, `airiq_bathroom_pro.yaml`,
  `comfort.yaml`, `comfort_wall.yaml`, `comfort_ceiling.yaml`,
  `fan_gp8403.yaml`, `gpio_expander_sx1509.yaml`); the FanDAC alias
  `packages/expansions/fan_dac.yaml` inherits the rebind via its
  `!include`. The hard-coded `i2c_id: halo_i2c` literal in
  `packages/features/ceiling_halo_leds.yaml` line 6 is rebound to
  `i2c_id: core_i2c` (the PCA9685 halo LED driver now binds the
  shared Core I²C bus). The `tests/generate_test_configs.py` per-product
  `fan_dac_i2c_id: expansion_i2c` override is removed — the new
  default at `fan_gp8403.yaml` already resolves to `core_i2c`
  directly. Extended `tests/test_core_abstract_bus.py` with a new
  `SharedI2CBusTests` class (13 cases) asserting: canonical
  `core_i2c` bus present in each in-scope Core package with
  `GPIO48` / `GPIO45` / `400kHz`; legacy bus ids absent in every
  in-scope Core package; each in-scope Core defines exactly one
  i2c bus; every in-scope `*_i2c_id` consumer default equals
  `core_i2c`; `ceiling_halo_leds.yaml` literal rebound; FanDAC /
  GP8403 bind `core_i2c` via substitution; FanDAC alias
  `!include`s the GP8403 implementation; SX1509 binds `core_i2c`
  via substitution; `generate_test_configs.py` no longer sets
  `expansion_i2c` override; ceiling_s3 retains `i2c_primary`; Mini
  retains `i2c0`; no legacy bus id appears on any active consumer
  line outside the documented out-of-scope set; no legacy pin
  substitutions survive in the seven in-scope Core packages. The
  two S3-variant Core / expansion packages
  (`sense360_core_ceiling_s3.yaml`, `airiq_ceiling_s3.yaml`,
  `comfort_ceiling_s3.yaml`) and the Mini family
  (`sense360_core_mini.yaml`, `mini_onboard_sensors.yaml`, the six
  `sense360-mini-*.yaml` products) are deliberately out of scope
  per operator decision #10 and stay byte-for-byte unchanged on the
  I²C bus axis. Voice-variant Core `relay_pin: GPIO4` stays
  deliberately out of scope for `001A`. Updated
  `docs/hardware/core-abstract-bus-reconciliation.md` with a new
  `### 2026-05-22 — CORE-ABSTRACT-BUS-001B implementation`
  audit-log entry recording the file-by-file rebind, the
  out-of-scope-preserved set, the validation result, and the
  status (all four preconditions enumerated by PR #519 now closed;
  `001B` moves from `implementation-plannable` to **implemented**).
  Refreshed the document Status header to reflect that all three
  001A / 001B / 001C slices have now landed at the substitution
  layer. Static validation: `python3 tests/validate_configs.py`
  PASS (202 / 202); `python3 scripts/validate_compile_targets.py
  --metadata-only` PASS (8 / 8); `python3
  tests/test_core_abstract_bus.py` PASS (33 / 33; 20 pre-existing +
  13 new `SharedI2CBusTests` cases); `python3 -m unittest discover
  -s tests -p "test_*.py"` PASS (515 / 515 — +13 vs the pre-001B
  baseline of 502). ESPHome was **not** available in the
  implementation environment, so the `esphome config`
  generated-config diff check against Release-One
  (`products/sense360-ceiling-poe-ventiq-roomiq.yaml`) and LED
  preview
  (`products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`) was
  **not** executed; the implementation relies on the static
  validators above plus the new `SharedI2CBusTests`
  substitution-graph assertions. The expected diff is bus-identity
  only — every I²C-bound sensor moves from `i2c_id: expansion_i2c`
  (or whichever legacy id its path resolved to) to
  `i2c_id: core_i2c`; the single bus block moves from
  `id: halo_i2c` + `id: expansion_i2c` to one `id: core_i2c` on
  `sda: GPIO48` / `scl: GPIO45` / `frequency: 400kHz`. No entity
  name change, no `config_string` change, no `artifact_name`
  change, no LED-ring pin change, no WebFlash exposure change, no
  release-channel change, no GPIO pin change unrelated to I²C.
  **`PACKAGE-PWM-001` and `PACKAGE-DAC-001` are now unblocked only
  at the shared-I²C-bus layer.** Both still require their own
  per-board evidence (`HW-PINMAP-311-FOLLOWUP` /
  `HW-PINMAP-312-FOLLOWUP`) and BOM cross-checks; this PR does
  **not** flip either to `complete`, does **not** add any
  compile-only target, and does **not** edit the catalog. The
  compile-only candidate rows for FanPWM (`S360-311`) and FanDAC
  (`S360-312`) in `config/compile-only-candidates.json` keep their
  remaining blockers. **No `products/**` or `products/webflash/**`
  edit; no `config/**` edit; no `scripts/**`,
  `.github/workflows/**`, `components/**`, `include/**`,
  `firmware/**`, `manifest.json`, `firmware/sources.json` edit; no
  WebFlash repo (`sense360store/WebFlash`) edit; no
  `webflash_build_matrix` flip; no `artifact_name`; no
  `webflash_wrapper`; no `config_string` change; no
  `release_one_required_configs` change; no `lifecycle_statuses` /
  `canonical_modules` / `canonical_power` / `forbidden_tokens` /
  `REQUIRED_CONFIGS` / kit change; no `schematic_status` /
  `schematic_file` promotion; no COMPLIANCE-001 movement.** No
  Release-One change (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` /
  `stable` / artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`). No LED
  preview change (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`). No
  FanTRIAC change (`blocked` / `HW-005`). No FanRelay /
  `PACKAGE-RELAY-001` / `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001`
  / `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001` advancement. No
  compile-only target added. No firmware artifact built or
  attached. No release artifact / tag / checksum / build-info
  manifest / proof row. No WebFlash import-readiness claim. No
  `S360-100-BENCH-001` closure. No board-level mains-safety /
  installation-approval / creepage / clearance / thermal / EMI
  certification claim. No production-wide / multi-unit /
  oscilloscope-traced general `GPIO3` strap-pin boot-behaviour
  characterisation claim.
- **CORE-ABSTRACT-BUS-001B-PLAN-001** (PR #568) recorded the
  operator-confirmed implementation plan for
  `CORE-ABSTRACT-BUS-001B` (the shared-I²C-bus consolidation
  slice) ahead of any YAML rebind. **Canonical I²C bus id is now
  decided: `core_i2c`.** Migration style is **hard rename only**;
  no compatibility aliases are added by default (aliases will only
  be considered if implementation tests later prove one
  unavoidable). All affected old bus ids
  (`halo_i2c` / `expansion_i2c` / `i2c0` / `i2c1` / `i2c_primary` /
  `i2c_expander`) must be **removed** from the in-scope Core
  abstract packages by the future implementation slice unless an
  explicitly-documented package-private exception is justified.
  The future implementation PR must update every known consumer
  atomically (seven in-scope Core packages, 11 expansion-package
  `*_i2c_id` consumer defaults, the hard-coded `i2c_id: halo_i2c`
  literal in `packages/features/ceiling_halo_leds.yaml`, the
  `tests/generate_test_configs.py` override, the
  `tests/test_core_abstract_bus.py` `SharedI2CBusTests` scaffold,
  and the Release-One + LED preview generated-config diff check
  plus the re-validation pass for every non-Release-One product
  YAML). Recorded the new
  §`### 2026-05-22 — CORE-ABSTRACT-BUS-001B core_i2c plan`
  audit-log entry in
  `docs/hardware/core-abstract-bus-reconciliation.md` (decision
  table; refreshed bus-definition inventory; consumer inventory
  organised into categories A–I — Core bus definitions, expansion
  `*_i2c_id` consumers, hard-coded literals, LED / halo-specific
  buses, GP8403 / FanDAC consumers, SX1509 expander consumers,
  RoomIQ / VentIQ / AirIQ sensor consumers, unused / dead / legacy
  references, tests and config catalogs; final desired mapping;
  implementation scope; non-goals; risk notes; test plan; status
  update; queue effect; do-not-do list). Refreshed the
  "Next audit-log trigger" section to drop the canonical-id-decision
  trigger and reword the implementation-slice trigger to reference
  the `core_i2c` rename target. Refreshed the
  `CORE-ABSTRACT-BUS-001B` entry in the Active / upcoming queue
  (item #1) so its status reads `Plan recorded 2026-05-22 —
  implementation-plannable; YAML rebind + test scaffold +
  non-Release-One product re-validation still pending`, the
  canonical id `core_i2c` is named, hard-rename-only is recorded,
  the seven in-scope Core packages are enumerated, the 11 in-scope
  expansion-package consumer defaults are enumerated, the
  `ceiling_halo_leds.yaml` literal rebind is recorded against the
  four product `!include`rs, and the two remaining preconditions
  (test scaffold and non-Release-One product re-validation, both
  of which land **with** the implementation slice) are recorded.
  **`PACKAGE-PWM-001` / `PACKAGE-DAC-001` blocker status is
  unchanged.** The canonical-id decision recorded here does **not**
  unblock either package — they remain blocked behind (a) `001B`
  implementation actually landing in YAML, (b) the underlying
  per-board pinmap evidence (`HW-PINMAP-311-FOLLOWUP` /
  `HW-PINMAP-312-FOLLOWUP`), and (c) BOM cross-checks. The PWM
  / DAC compile-only candidate rows in
  `config/compile-only-candidates.json` keep all of their existing
  blockers. **No `packages/**`, `products/**`,
  `products/webflash/**`, `config/**`, `scripts/**`,
  `.github/workflows/**`, `components/**`, `include/**`,
  `firmware/**`, `manifest.json`, `firmware/sources.json`,
  `tests/**`, release-artifact, checksum, build-info manifest, or
  WebFlash-repo edit; no I²C bus rename; no compatibility alias
  added; no `webflash_build_matrix` flip; no `artifact_name`; no
  `webflash_wrapper`; no `config_string` change; no
  `release_one_required_configs` change; no `lifecycle_statuses` /
  `canonical_modules` / `canonical_power` / `forbidden_tokens` /
  `REQUIRED_CONFIGS` / kit change; no `schematic_status` /
  `schematic_file` promotion; no COMPLIANCE-001 movement; no
  Release-One change (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` /
  `stable`); no LED preview change
  (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`); no FanTRIAC
  change (`blocked` / `HW-005`).** No `tests/test_core_abstract_bus.py`
  extension. No `SharedI2CBusTests` scaffold. No `S360-100-BENCH-001`
  closure. No PACKAGE-PWM-001 / PACKAGE-DAC-001 / PACKAGE-RELAY-001 /
  RELEASE-* unblock claim. No claim of WebFlash import-readiness.
  No claim of compliance evidence for any mains-switching product.
  Recommended next active-queue PR is
  `CORE-ABSTRACT-BUS-001B-IMPLEMENT-001` (the atomic YAML rebind +
  test scaffold + Release-One generated-config diff check +
  non-Release-One product re-validation), **not** a
  test-scaffold-only PR.
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
| PRODUCT-RELAY-001-READINESS-REFRESH | #563     | esphome-public  | Merged — docs / readiness-only product-layer re-evaluation after PACKAGE-RELAY-001 / PR #562 | Re-evaluated the FanRelay **product-layer** disposition after `PACKAGE-RELAY-001` / PR #562 implemented the package at the package layer. Refreshed [`docs/product-readiness-matrix.md` §FanRelay / S360-310](docs/product-readiness-matrix.md#fanrelay--s360-310) — Status moves from `needs-package-reconciliation` + `schematic-evidence-pending` to `package-implemented-at-package-layer` (upstream; PR #562) + `product-layer-blockers-open` + `advanced/manual-warning-only` + `blocked-from-standard-exposure` + `not-required-configs` + `not-recommended` + `not-kit-default` + `not-webflash-default` for the product-layer slice; product-layer blockers enumerated (product onboarding; installation / safety wording; competent-person caveat; production-wide / multi-unit `GPIO3` strap-pin boot characterisation; board-level mains-safety / installation-approval / creepage / clearance / thermal / EMI evidence); **recommended product posture** recorded as `advanced/manual-warning-only` + product-YAML-allowed (no WebFlash exposure) + compile-only validation allowed + WebFlash exposure blocked; standard `preview-candidate` exposure-ladder rung explicitly rejected as the default; 2026-05-22 dated update sub-section added; candidate row in the main product readiness table refreshed; Follow-up PR sequence row for `PRODUCT-RELAY-001` refreshed with the advanced / manual-warning wording + installation / safety caveat + competent-person caveat requirements. Refreshed [`docs/webflash-exposure-readiness-matrix.md` §Relay / S360-310 WebFlash posture](docs/webflash-exposure-readiness-matrix.md#relay--s360-310-webflash-posture) — candidate row refreshed with the post-PR #562 package-layer state and the product-layer disposition cross-reference; Future exposure class refreshed from `preview-candidate` to `advanced/manual-warning-only`; WebFlash Relay exposure recorded as **blocked** until `PRODUCT-RELAY-001` explicitly allows it (and even then a separate `WEBFLASH-RELAY-001` slice with its own production-wide / installation / competent-person gates is required); user-facing naming policy added (outcome-first — e.g. "Relay fan control" or "Switched fan control" — not loose board / module naming); REQUIRED_CONFIGS / kit / recommended posture restated as `never by default`; 2026-05-22 dated update sub-section added; Follow-up PR sequence row for `WEBFLASH-RELAY-001` refreshed with the advanced / manual-warning UX + production-wide / installation / competent-person sign-off + WebFlash-side manual-warning UX parity gates. Refreshed [`docs/release-artifact-readiness-matrix.md` §Relay / S360-310 release posture](docs/release-artifact-readiness-matrix.md#relay--s360-310-release-posture) — candidate row refreshed with the post-PR #562 package-layer state; release-class label refreshed from `preview-artifact-candidate` to `advanced/manual-warning-artifact-only` (long-term posture); `RELEASE-RELAY-001` recorded as **blocked**; no release artifact exists; **no release-proof row added by this readiness refresh** (a release-proof row would forward-reference an artifact that has never been built and would degrade the proof file's evidentiary integrity); stable-eligibility restated as `stable-not-approved — never by default`; REQUIRED_CONFIGS / kit / recommended posture restated as `never by default`; 2026-05-22 dated update sub-section added; Follow-up PR sequence row for `RELEASE-RELAY-001` refreshed with the advanced / manual-warning channel + WebFlash-side manual-warning UX parity gates. Refreshed [`docs/kit-intent-matrix.md` §S360-KIT-BATH-RELAY](docs/kit-intent-matrix.md#s360-kit-bath-relay--sense360-bathroom-kit--relay-fan-control) narrative — added 2026-05-22 status update sub-paragraph noting `CORE-ABSTRACT-BUS-001C` (PR #557) / `CORE-ABSTRACT-BUS-001A` (PR #558) / `PACKAGE-RELAY-001` (PR #562) have landed while `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` remain open; recorded that the blocker token list mirrors [`config/kit-intent-matrix.json`](config/kit-intent-matrix.json) verbatim and a config-edit PR refreshing the list is owed separately (this readiness-refresh PR is documentation-only and does not edit any [`config/`](config/) file); restated that the Relay Bathroom Kit remains `future-expansion` / `hardware-pending` / `webflash_exposure_allowed_now: false` / `stable_ready_now: false`; restated that the default sellable kit remains `S360-KIT-BATH-POE` mapped to Release-One `Ceiling-POE-VentIQ-RoomIQ`. Refreshed `UPCOMING_PR.md` Current queue summary (new bullet for this PR), Completed / merged PRs (this row), Active / upcoming queue (PRODUCT-RELAY-001 item #7 status refreshed with the readiness-refresh outcome, the recommended posture, and the recommended next PR as `PRODUCT-RELAY-001` implementation as a product-YAML-only / no-WebFlash-exposure slice — not a WebFlash wrapper / catalog flip / build-matrix entry / release artifact). | **No `packages/**` edit**; **no `products/**` or `products/webflash/**` edit**; **no `config/**` edit** (`config/hardware-catalog.json`, `config/product-catalog.json`, `config/webflash-builds.json`, `config/webflash-compatibility.json`, `config/firmware-combination-matrix.json`, `config/kit-intent-matrix.json`, `config/compile-only-targets.json`, `config/compile-only-candidates.json` all byte-identical); **no `scripts/**`, `.github/workflows/**`, `components/**`, `include/**`, `firmware/**`, `manifest.json`, `firmware/sources.json`, `tests/**` edit** (`tests/test_fan_relay_package.py` from PR #562 and `tests/test_core_abstract_bus.py` from 001A / 001C are preserved verbatim and not extended by this PR); **no `webflash_build_matrix` flip**; **no `artifact_name` / `webflash_wrapper` / `config_string` / `release_one_required_configs` / `lifecycle_statuses` / `canonical_modules` / `canonical_power` / `forbidden_tokens` / `REQUIRED_CONFIGS` / kit JSON change**; **no `schematic_status` / `schematic_file` promotion** (`S360-310` row in `config/hardware-catalog.json` stays byte-identical: `schematic_status: cataloged_unverified`, no `schematic_file`); **no COMPLIANCE-001 movement**; no Release-One change (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`); no LED preview change (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`); no FanTRIAC change (`blocked` / `HW-005`); voice-variant Core packages stay at pre-001A `relay_pin: GPIO4` (out of scope); no compile-only target added; no firmware artifact built or attached; no release artifact / tag / checksum / build-info manifest / proof row; **no WebFlash import-readiness claim**; **no hardware release-readiness claim**; **no `RELEASE-RELAY-001` unblock claim**; **no `PACKAGE-RELAY-001` re-implementation** (PR #562 stays as the package-layer landing point); **no claim that `PRODUCT-RELAY-001` is product-ready, WebFlash-ready, release-ready, compliance-cleared, safe for arbitrary mains installation, or verified across production batches**; no Relay product YAML; no WebFlash wrapper; no compile-only target for FanRelay; no PWM / FanDAC / FanTRIAC / LED stable promotion; no `CORE-ABSTRACT-BUS-001B` advancement; **no closure of `S360-100-BENCH-001`**; **no board-level mains-safety / installation-approval / creepage / clearance / thermal / EMI certification claim**; **no production-wide / multi-unit / oscilloscope-traced general `GPIO3` strap-pin boot-behaviour characterisation claim**; **no `docs/cleanup-audit.md` edit** (the readiness refresh is recorded in the four relevant matrix docs above plus this tracker; no parallel cleanup-audit row is added). | The product-layer disposition for FanRelay is now defined as **`advanced/manual-warning-only` + product-YAML-allowed (no WebFlash) + compile-only-allowed + WebFlash-blocked**. The recommended next active-queue item is `PRODUCT-RELAY-001` implementation as a product-YAML-only / no-WebFlash-exposure slice (canonical FanRelay product YAML under `products/`; explicit advanced / manual-warning wording; installation / safety caveat; competent-person caveat; `docs/product-onboarding.md` safe sequence cleared; optional compile-only target under `config/compile-only-targets.json`), **not** a WebFlash wrapper / catalog flip / build-matrix entry / release artifact. `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001` stay blocked. `CORE-ABSTRACT-BUS-001B` stays independent. `S360-100-BENCH-001`, `HW-PINMAP-311-FOLLOWUP`, `HW-PINMAP-312-FOLLOWUP`, `HW-PINMAP-320-FOLLOWUP`, and `COMPLIANCE-001` are **not** closed by this readiness refresh. |
| PRODUCT-RELAY-001            | #564      | esphome-public  | Merged — implementation slice (product-YAML-only / no-WebFlash-exposure) | Added the canonical FanRelay product YAML [`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`](products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml) as the product-YAML-only / no-WebFlash-exposure slice the readiness refresh PR #563 recommended. The YAML composes the Release-One PoE base stack (Core ceiling abstract + `packages/hardware/power_poe.yaml` + VentIQ + RoomIQ) plus `packages/expansions/fan_relay.yaml`; inherits `${relay_pin}` from the parent Core abstract package binding (schematic-correct GPIO3 per `CORE-ABSTRACT-BUS-001A` / PR #558) without hard-coding any GPIO; header carries explicit advanced / manual-warning + installation / safety + competent-person caveat wording (mains switching / bathroom fan-control path; competent person where required; not WebFlash exposed; not default kit; not release artifact; not compliance certification; advanced / manual-warning only). Added a non-WebFlash row to `config/product-catalog.json` (`config_string: Ceiling-POE-VentIQ-FanRelay-RoomIQ`, `status: hardware-pending`, `webflash_build_matrix: false`, no `artifact_name`, no `webflash_wrapper`, `hardware_status: package-implemented-product-layer-pending`) required by the [`tests/test_product_catalog.py`](tests/test_product_catalog.py) enumeration. Regenerated `config/firmware-combination-matrix.json` (one FanRelay row reclassifies from `missing-product-yaml` → `blocked-hardware`; 168-row total unchanged; `fanrelay-blocked-package-or-core-bus` lane count stays at 36) and `docs/firmware-build-gap-report.md` via `scripts/generate_firmware_matrix.py` and `scripts/report_firmware_build_gaps.py`. Added new test `tests/test_relay_product_readiness.py` (42 stdlib-unittest cases) pinning: Relay product YAML exists; YAML composes FanRelay + Core ceiling + VentIQ + RoomIQ + PoE; YAML does NOT hard-code `GPIO3` (or any GPIO); catalog row carries `webflash_build_matrix: false`, no `artifact_name`, no `webflash_wrapper`; no FanRelay WebFlash wrapper file under `products/webflash/`; Relay config string is NOT in `config/webflash-builds.json` and NOT in `release_one_required_configs`; YAML carries advanced / manual-warning + competent-person + installation / safety + not-WebFlash + not-default-kit + not-release-artifact + not-compliance-certified wording; the `S360-KIT-BATH-RELAY` kit stays `future-expansion` / `hardware-pending` / `webflash_exposure_allowed_now: false` / `stable_ready_now: false`; the default sellable bathroom kit remains `S360-KIT-BATH-POE` mapped to Release-One; Release-One / LED preview / FanTRIAC catalog entries are unchanged. Tightened `tests/test_fan_relay_package.py` `PackageRelayDoesNotTouchWebFlashOrProductTests` to allow the single PRODUCT-RELAY-001 canonical FanRelay product YAML while still forbidding any additional FanRelay product YAML, any FanRelay WebFlash wrapper under `products/webflash/`, and any `FanRelay` token in `config/webflash-builds.json`. Updated docs `docs/product-readiness-matrix.md` §FanRelay / S360-310 (status + audit-log + Follow-up PR sequence row), `docs/webflash-exposure-readiness-matrix.md` §Relay / S360-310 WebFlash posture (audit-log entry recording WebFlash exposure stays blocked even though product YAML landed), `docs/release-artifact-readiness-matrix.md` §Relay / S360-310 release posture (audit-log entry recording release surface byte-identical; RELEASE-RELAY-001 stays blocked), and `docs/kit-intent-matrix.md` §S360-KIT-BATH-RELAY (kit narrative notes PRODUCT-RELAY-001 landed but kit remains `future-expansion` / `hardware-pending`; default sellable bathroom kit remains S360-KIT-BATH-POE on `stable`). | **No `packages/**` edit** (the FanRelay package and the Core abstract packages are consumed as-is); **no `products/webflash/**` edit**; **no `config/webflash-builds.json` edit**; **no `config/webflash-compatibility.json` edit**; **no `config/hardware-catalog.json` edit**; **no `config/kit-intent-matrix.json` edit**; **no `scripts/**` edit** (only the outputs of `scripts/generate_firmware_matrix.py` and `scripts/report_firmware_build_gaps.py` are refreshed; the scripts themselves are byte-identical); **no `.github/workflows/**`, `components/**`, `include/**`, `firmware/**`, `manifest.json`, `firmware/sources.json` edit**; **no `webflash_build_matrix` flip**; **no `artifact_name`**; **no `webflash_wrapper`**; **no `release_one_required_configs` change**; **no `lifecycle_statuses` change**; **no `canonical_modules` / `canonical_power` / `forbidden_tokens` change**; **no `REQUIRED_CONFIGS` / kit JSON change**; **no `schematic_status` / `schematic_file` promotion** (`S360-310` stays `cataloged_unverified`); **no COMPLIANCE-001 movement**; no Release-One change (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`); no LED preview change (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`); no FanTRIAC change (`blocked` / `HW-005`); voice-variant Core packages stay at pre-001A `relay_pin: GPIO4` (out of scope); no compile-only target added; no firmware artifact built or attached; no release artifact / tag / checksum / build-info manifest / proof row; **no WebFlash import-readiness claim**; **no hardware release-readiness claim**; **no `RELEASE-RELAY-001` unblock claim**; **no `WEBFLASH-RELAY-001` unblock claim**; **no `WF-IMPORT-RELAY-001` unblock claim**; **no claim that PRODUCT-RELAY-001 is WebFlash-ready, release-ready, compliance-cleared, safe for arbitrary mains installation, or verified across production batches**; no Relay WebFlash wrapper; no compile-only target for FanRelay; no PWM / FanDAC / FanTRIAC / LED stable promotion; no `CORE-ABSTRACT-BUS-001B` advancement; **no closure of `S360-100-BENCH-001`**; **no board-level mains-safety / installation-approval / creepage / clearance / thermal / EMI certification claim**; **no production-wide / multi-unit / oscilloscope-traced general `GPIO3` strap-pin boot-behaviour characterisation claim**. | `PRODUCT-RELAY-001` is now **landed as a product-YAML-only / no-WebFlash-exposure slice**. The FanRelay product YAML exists under `products/`; the matching non-WebFlash catalog row exists in `config/product-catalog.json`; structural invariants are pinned by `tests/test_relay_product_readiness.py`. WebFlash exposure remains **blocked** until `WEBFLASH-RELAY-001` lands (with its production-wide hardware characterisation + installation / competent-person sign-off + WebFlash-side manual-warning UX parity gates). `RELEASE-RELAY-001` and `WF-IMPORT-RELAY-001` remain blocked behind `WEBFLASH-RELAY-001`. The recommended next Relay chain PR is `WEBFLASH-RELAY-001-READINESS-REFRESH` (docs-only readiness re-evaluation after PRODUCT-RELAY-001 lands), not immediate `WEBFLASH-RELAY-001` exposure work, unless the new product YAML fails compile-only validation in a later run. `CORE-ABSTRACT-BUS-001B` stays independent. `S360-100-BENCH-001`, `HW-PINMAP-311-FOLLOWUP`, `HW-PINMAP-312-FOLLOWUP`, `HW-PINMAP-320-FOLLOWUP`, and `COMPLIANCE-001` are **not** closed by this PR. |
| WEBFLASH-RELAY-001-READINESS-REFRESH | #565     | esphome-public  | Merged — docs / readiness-only WebFlash-layer re-evaluation after PRODUCT-RELAY-001 / PR #564 | Re-evaluated the FanRelay **WebFlash-layer** disposition after `PRODUCT-RELAY-001` / PR #564 landed the canonical FanRelay product YAML `products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml` and a non-WebFlash catalog row (`config_string: Ceiling-POE-VentIQ-FanRelay-RoomIQ`, `status: hardware-pending`, `webflash_build_matrix: false`, no `artifact_name`, no `webflash_wrapper`) without any WebFlash wrapper / build-matrix row / release artifact. Re-verified against the live files: no FanRelay WebFlash wrapper under `products/webflash/` (only Release-One, LED preview, and the blocked FanTRIAC reference); no FanRelay row in `config/webflash-builds.json` (only Release-One stable + LED preview); `FanRelay` reserved in `config/webflash-compatibility.json` `canonical_modules` (line 11) with no `webflash_build_matrix: true` consumer (reservation-only); `release_one_required_configs` stays `["Ceiling-POE-VentIQ-RoomIQ"]`; the PRODUCT-RELAY-001 catalog row is byte-identical; the `S360-KIT-BATH-RELAY` row in `config/kit-intent-matrix.json` stays `future-expansion` / `hardware-pending` / `webflash_exposure_allowed_now: false` / `stable_ready_now: false`. Refreshed [`docs/webflash-exposure-readiness-matrix.md` §Relay / S360-310 WebFlash posture](docs/webflash-exposure-readiness-matrix.md#relay--s360-310-webflash-posture) — top-table chain row refreshed (`PRODUCT-RELAY-001` now `*(landed PR #564)*` and `WEBFLASH-RELAY-001-READINESS-REFRESH` is now `*(this PR)*`); "Allowed WebFlash action now" sub-section extended with a new "Remaining WebFlash gates" enumeration (seven gates) and a new "Possible exposure classes the eventual `WEBFLASH-RELAY-001` could take" enumeration (four shapes: blocked entirely; advanced / manual-warning import only; hidden / manual mode only; or compile-only / no-runtime exposure under a future `FW-COMPILE-RELAY-001`); new 2026-05-22 `WEBFLASH-RELAY-001-READINESS-REFRESH` audit-log entry recording WebFlash Relay exposure remains blocked, the WebFlash repo posture re-read read-only (no FanRelay source / build, `REQUIRED_CONFIGS` unchanged, `scripts/data/kits.json` unchanged, `module-availability.js` keeps Relay at `design-pending`, Stage 1 `S360-KIT-BATH-RELAY` preset stays `planned`/non-installable, `WF-IMPORT-RELAY-001` still blocked behind upstream `RELEASE-RELAY-001`), and the WebFlash UI naming alignment confirmation (the WebFlash UI already ships outcome-first labels "Fan relay control" in Step 4 under WF-UX-007 and "Sense360 Bathroom Kit — Relay Fan Control" in Stage 1 bundle preset under WF-KIT-PRESETS-001). Refreshed [`docs/release-artifact-readiness-matrix.md` §Relay / S360-310 release posture](docs/release-artifact-readiness-matrix.md#relay--s360-310-release-posture) — new 2026-05-22 `WEBFLASH-RELAY-001-READINESS-REFRESH` audit-log entry recording `RELEASE-RELAY-001` remains blocked, no FanRelay release artifact exists, no release-proof row is added by this readiness refresh, the atomic `RELEASE-RELAY-001` slice remains owed to a later PR. Refreshed [`docs/kit-intent-matrix.md` §S360-KIT-BATH-RELAY](docs/kit-intent-matrix.md#s360-kit-bath-relay--sense360-bathroom-kit--relay-fan-control) narrative — new 2026-05-22 `WEBFLASH-RELAY-001-READINESS-REFRESH` status update recording the Relay Bathroom Kit has product YAML upstream but still no WebFlash exposure and not default; default kit remains `S360-KIT-BATH-POE`; cross-repo WebFlash Stage 1 bundle preset `S360-KIT-BATH-RELAY` stays `planned`; WebFlash UI naming alignment confirmed. Refreshed `UPCOMING_PR.md` Current queue summary (new bullet for this PR), Completed / merged PRs (this row), Active / upcoming queue (WEBFLASH-RELAY-001 item #8 status refreshed with the readiness-refresh outcome and the seven WebFlash gates + four possible exposure shapes; RELEASE-RELAY-001 item #9 status refreshed to record blockedness behind the seven WebFlash gates). | **No `packages/**` edit**; **no `products/**` or `products/webflash/**` edit**; **no `config/**` edit** (`config/hardware-catalog.json`, `config/product-catalog.json`, `config/webflash-builds.json`, `config/webflash-compatibility.json`, `config/firmware-combination-matrix.json`, `config/kit-intent-matrix.json`, `config/compile-only-targets.json`, `config/compile-only-candidates.json` all byte-identical); **no `scripts/**`, `.github/workflows/**`, `components/**`, `include/**`, `firmware/**`, `manifest.json`, `firmware/sources.json`, `tests/**` edit** (`tests/test_relay_product_readiness.py` from PR #564, `tests/test_fan_relay_package.py` from PR #562, and `tests/test_core_abstract_bus.py` from 001A / 001C are preserved verbatim and not extended by this PR); **no WebFlash repo (`sense360store/WebFlash`) edit** (this PR is one-repo scope; the WebFlash repo is re-read read-only); **no `webflash_build_matrix` flip**; **no `artifact_name`**; **no `webflash_wrapper`**; **no `config_string`**; **no `release_one_required_configs` change**; **no `lifecycle_statuses` change**; **no `canonical_modules` / `canonical_power` / `forbidden_tokens` change**; **no `REQUIRED_CONFIGS` / kit JSON change**; **no `schematic_status` / `schematic_file` promotion** (`S360-310` row in `config/hardware-catalog.json` stays byte-identical: `schematic_status: cataloged_unverified`, no `schematic_file`); **no COMPLIANCE-001 movement**; no Release-One change (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`); no LED preview change (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`); no FanTRIAC change (`blocked` / `HW-005`); voice-variant Core packages stay at pre-001A `relay_pin: GPIO4`; no compile-only target added; no firmware artifact built or attached; no release artifact / tag / checksum / build-info manifest / proof row; **no WebFlash import-readiness claim**; **no WebFlash exposure claim**; **no `RELEASE-RELAY-001` unblock claim**; **no `WEBFLASH-RELAY-001` unblock claim**; **no `WF-IMPORT-RELAY-001` unblock claim**; **no `PACKAGE-RELAY-001` re-implementation** (PR #562 stays as the package-layer landing point); **no `PRODUCT-RELAY-001` re-implementation** (PR #564 stays as the product-YAML landing point); **no claim that the FanRelay product or any future WebFlash surface is product-ready, WebFlash-ready, release-ready, compliance-cleared, kit-default-ready, recommended-bundle ready, safe for arbitrary mains installation, or verified across production batches**; no Relay WebFlash wrapper; no compile-only target for FanRelay; no PWM / FanDAC / FanTRIAC / LED stable promotion; no `CORE-ABSTRACT-BUS-001B` advancement; **no closure of `S360-100-BENCH-001`**; **no board-level mains-safety / installation-approval / creepage / clearance / thermal / EMI certification claim**; **no production-wide / multi-unit / oscilloscope-traced general `GPIO3` strap-pin boot-behaviour characterisation claim**. | The WebFlash-layer disposition for FanRelay is now defined: **WebFlash exposure remains blocked even though `PRODUCT-RELAY-001` landed the product YAML**. The seven remaining WebFlash gates (explicit `WEBFLASH-RELAY-001` implementation approval; advanced / manual-warning UI copy; competent-person / installation warning flow; product not default / not recommended; release artifact must exist before WebFlash import; no stable / preview promotion until explicit approval; production-wide / installation / safety caveats remain separate) are enumerated. The four possible exposure shapes a future `WEBFLASH-RELAY-001` slice could take are enumerated (blocked entirely; advanced / manual-warning import only; hidden / manual mode only; or compile-only / no-runtime exposure). The recommended next active-queue item is one of `WEBFLASH-RELAY-001` implementation plan / scaffold only (if allowed by the project lead), `RELEASE-RELAY-001` (blocked until artifact path exists), or `FW-COMPILE-RELAY-001` (if compile-only validation should happen first); **not** immediate `WEBFLASH-RELAY-001` wrapper / catalog / build-matrix work. The WebFlash repo's outcome-first user-facing naming ("Fan relay control" in Step 4 under WF-UX-007; "Sense360 Bathroom Kit — Relay Fan Control" in Stage 1 bundle preset `S360-KIT-BATH-RELAY` under WF-KIT-PRESETS-001) is already aligned with this matrix's user-facing-naming policy; no naming refresh is owed on either side. `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001` stay blocked. `CORE-ABSTRACT-BUS-001B` stays independent. `S360-100-BENCH-001`, `HW-PINMAP-311-FOLLOWUP`, `HW-PINMAP-312-FOLLOWUP`, `HW-PINMAP-320-FOLLOWUP`, and `COMPLIANCE-001` are **not** closed by this readiness refresh. |
| FW-COMPILE-RELAY-001         | #566      | esphome-public  | Merged — compile-only target add for the PRODUCT-RELAY-001 / PR #564 FanRelay product YAML | Added a single FanRelay compile-only validation target to [`config/compile-only-targets.json`](config/compile-only-targets.json) pointing at the PRODUCT-RELAY-001 / PR #564 canonical FanRelay product YAML [`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`](products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml). The target row carries `id: ceiling-poe-ventiq-fanrelay-roomiq-compile-only`, `config_string: Ceiling-POE-VentIQ-FanRelay-RoomIQ`, `shipment_status: compile-only`, `webflash_exposure_allowed_now: false`, `hardware_required_for_validation: true`, `advanced_manual_warning_only: true`, `hardware_pending: true`, and `blocked: false`. Totals updated from 7 → 8. Synchronised [`config/compile-only-candidates.json`](config/compile-only-candidates.json) `currently_compile_only_config_strings` (extended by one entry — the candidate ledger doc-mirror that `tests/test_compile_expansion_candidates.py::test_currently_compile_only_field_matches_compile_only_targets` cross-checks). Added the new `FanRelayCompileOnlyCoverageTests` class to [`tests/test_compile_targets.py`](tests/test_compile_targets.py) (22 stdlib-unittest cases pinning: FanRelay compile-only target exists; points at the PRODUCT-RELAY-001 product YAML; config string is `Ceiling-POE-VentIQ-FanRelay-RoomIQ`; present in `config/firmware-combination-matrix.json`; `shipment_status: compile-only`; `webflash_exposure_allowed_now: false`; `hardware_required_for_validation: true`; `advanced_manual_warning_only: true`; `hardware_pending: true`; `blocked: false`; no `webflash_build_matrix` / `artifact_name` / `webflash_wrapper` / `expected_channel` declarations; not in `config/webflash-builds.json`; no `FanRelay` token anywhere in `config/webflash-builds.json`; not in `release_one_required_configs`; product YAML does not live under `products/webflash/`; no FanRelay WebFlash wrapper file exists; Release-One and LED preview compile-only targets unchanged; totals match expected target count after add). Refactored the FW-COMPILE-POE-NONFAN-001 lane's `PoeNonFanCompileOnlyCoverageTests` fan / PWR-token guardrails (`test_this_pr_introduces_no_fan_compile_only_target` / `test_this_pr_introduces_no_pwr_compile_only_target`) to scope to targets whose `product_yaml` lives under `products/compile-only/` (the FW-COMPILE-POE-NONFAN-001 directory) and renamed them `test_poe_nonfan_lane_introduces_no_fan_compile_only_target` / `test_poe_nonfan_lane_introduces_no_pwr_compile_only_target` so the FW-COMPILE-RELAY-001 target — which reuses the canonical FanRelay product YAML under `products/`, not under `products/compile-only/` — no longer trips the lane guard. Added the new `RelayProductCompileOnlyTargetTests` class to [`tests/test_relay_product_readiness.py`](tests/test_relay_product_readiness.py) (17 cases pinning the same invariants from the product-readiness angle: target exists; points at the product YAML; correct `config_string`; `shipment_status: compile-only`; `advanced_manual_warning_only: true`; `hardware_pending: true`; `hardware_required_for_validation: true`; `webflash_exposure_allowed_now: false`; `blocked: false`; no `webflash_build_matrix` / `artifact_name` / `webflash_wrapper` / `expected_channel`; config string absent from `config/webflash-builds.json` and `release_one_required_configs`; Release-One and LED preview compile-only targets unchanged). Updated `docs/compile-only-firmware-validation.md` (new `### 2026-05-22 — FW-COMPILE-RELAY-001 FanRelay compile-only validation` audit-log entry — target table, rationale linking the closed `CORE-ABSTRACT-BUS-001A` / `001C` / `PACKAGE-RELAY-001` / `S360-310-BENCH-EVIDENCE-001` / `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001-READINESS-REFRESH` chain, what compile-only proves for the FanRelay target, and what compile-only does **not** prove); `docs/webflash-exposure-readiness-matrix.md` §Relay / S360-310 WebFlash posture (new 2026-05-22 `FW-COMPILE-RELAY-001` audit-log note explicitly recording WebFlash exposure remains blocked, the seven WebFlash gates not advanced, the four possible exposure shapes unchanged); `docs/release-artifact-readiness-matrix.md` §Relay / S360-310 release posture (new 2026-05-22 `FW-COMPILE-RELAY-001` audit-log note explicitly recording `RELEASE-RELAY-001` remains blocked, no FanRelay release artifact exists, no release-proof row is added). | **No `packages/**` edit**; **no `products/**` or `products/webflash/**` edit** (the FanRelay product YAML at `products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml` is consumed verbatim from PR #564); **no `config/webflash-builds.json` edit**; **no `config/webflash-compatibility.json` edit**; **no `config/hardware-catalog.json` edit**; **no `config/kit-intent-matrix.json` edit**; **no `config/firmware-combination-matrix.json` edit**; **no `config/product-catalog.json` edit**; **no `scripts/**`, `.github/workflows/**`, `components/**`, `include/**`, `firmware/**`, `manifest.json`, `firmware/sources.json` edit**; **no WebFlash repo (`sense360store/WebFlash`) edit** (this PR is one-repo scope); **no `webflash_build_matrix` flip**; **no `artifact_name`**; **no `webflash_wrapper`**; **no `config_string` change**; **no `release_one_required_configs` change**; **no `lifecycle_statuses` change**; **no `canonical_modules` / `canonical_power` / `forbidden_tokens` change**; **no `REQUIRED_CONFIGS` / kit JSON change**; **no `schematic_status` / `schematic_file` promotion** (`S360-310` stays `cataloged_unverified`); **no COMPLIANCE-001 movement**; no Release-One change (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`); no LED preview change (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`); no FanTRIAC change (`blocked` / `HW-005`); voice-variant Core packages stay at pre-001A `relay_pin: GPIO4`; no firmware artifact built or attached; no release artifact / tag / checksum / build-info manifest / proof row; **no WebFlash import-readiness claim**; **no WebFlash exposure claim**; **no `RELEASE-RELAY-001` unblock claim**; **no `WEBFLASH-RELAY-001` unblock claim**; **no `WF-IMPORT-RELAY-001` unblock claim**; **no claim that the FanRelay product is WebFlash-ready, release-ready, compliance-cleared, safe for arbitrary mains installation, kit-default-ready, recommended-bundle-ready, or verified across production batches**; no Relay WebFlash wrapper; no PWM / FanDAC / FanTRIAC / LED stable promotion; no `CORE-ABSTRACT-BUS-001B` advancement; **no closure of `S360-100-BENCH-001`**; **no board-level mains-safety / installation-approval / creepage / clearance / thermal / EMI certification claim**; **no production-wide / multi-unit / oscilloscope-traced general `GPIO3` strap-pin boot-behaviour characterisation claim**. | `FW-COMPILE-RELAY-001` is now landed as a **compile-only validation lane addition** pointing at the existing PRODUCT-RELAY-001 / PR #564 canonical FanRelay product YAML. The FanRelay product YAML is now CI-validated for YAML / package / ESPHome compile drift (necessary-but-insufficient for any shipment-readiness claim). **WebFlash exposure stays blocked** behind the seven WebFlash gates owned by `WEBFLASH-RELAY-001`. **`RELEASE-RELAY-001` stays blocked** behind those gates plus its own release-readiness gates. **`WF-IMPORT-RELAY-001` stays blocked** behind upstream `RELEASE-RELAY-001`. Compile success does **not** discharge any of the seven WebFlash gates, does **not** discharge any release-readiness gate, and does **not** discharge any compliance / installation / production-wide hardware characterisation gate. The recommended next Relay-chain PR is one of `WEBFLASH-RELAY-001` implementation plan / scaffold only (if allowed by the project lead), `RELEASE-RELAY-001` (still blocked until artifact path exists), or, if a future ESPHome upgrade breaks compile, a targeted compile fix for the FanRelay compile-only target only; **not** immediate `WEBFLASH-RELAY-001` wrapper / catalog / build-matrix work. `CORE-ABSTRACT-BUS-001B` stays independent. `S360-100-BENCH-001`, `HW-PINMAP-311-FOLLOWUP`, `HW-PINMAP-312-FOLLOWUP`, `HW-PINMAP-320-FOLLOWUP`, and `COMPLIANCE-001` are **not** closed by this PR. |
| PACKAGE-RELAY-001            | #562      | esphome-public  | Merged — implementation slice (test + readiness reconciliation; no YAML rebind) | Reconciled the FanRelay package after the package-evidence layer closed under PR #557 (`CORE-ABSTRACT-BUS-001C`), PR #558 (`CORE-ABSTRACT-BUS-001A`), PR #559 (`PACKAGE-RELAY-001-READINESS-REFRESH`), PR #560 (`S360-310-BENCH-001` evidence-capture checklist), and PR #561 (`S360-310-BENCH-EVIDENCE-001` evidence population). **No YAML edit required** on `packages/expansions/fan_relay.yaml`: the package was already structurally correct (`fan_relay_pin: ${relay_pin}` line 27 inherits the parent Core abstract package binding; post-001A `${relay_pin}` resolves to the schematic-correct `GPIO3` per S360-100-R4 `IO3 = Relay`); the override-hook comment block (lines 22–25), the `switch.platform: gpio` declaration with `pin: ${fan_relay_pin}` (line 38), `restore_mode: RESTORE_DEFAULT_OFF`, the `fan_auto_mode` global (lines 50–53), and the `fan_emergency_stop` script (lines 58–65) are preserved verbatim. The reconciliation is the addition of `tests/test_fan_relay_package.py` (12 stdlib-unittest cases) pinning the FanRelay package abstraction against future regression: the package exists and parses as YAML; `fan_relay_pin` defaults to `${relay_pin}` and is not a hardcoded GPIO; the package does not hard-code `GPIO3` / `GPIO4` / `GPIO10` or any other GPIO on an active (non-comment) line; the `fan_relay_switch` switch block uses platform `gpio` and binds `pin: ${fan_relay_pin}`; the five non-voice Core abstract packages bind `relay_pin: GPIO3` (cross-check against `tests/test_core_abstract_bus.py` `RelayPinRebindTests`); the voice-variant Core packages stay at the pre-001A `relay_pin: GPIO4` (deliberately out of scope); no FanRelay product YAML exists under `products/`; no `FanRelay` token exists in `config/webflash-builds.json`. Docs refreshed: `docs/hardware/s360-310-r4-relay.md` §Package YAML status PACKAGE-RELAY-001 investigation-outcome bullet extended with a PACKAGE-RELAY-001 implementation-outcome paragraph; new 2026-05-22 audit-log row appended to §HW-PINMAP-310-FOLLOWUP audit log recording the implementation. `docs/hardware/package-readiness-matrix.md` `fan_relay.yaml` row + §`fan_relay.yaml` / S360-310 detail section refreshed to `package-implemented` + `reconciled-at-package-layer` with Allowed-action-now and Follow-up-owner chain refreshed. `docs/hardware/firmware-package-mapping-audit.md` Release-One package-stack `relay_pin` bullet appended with a PACKAGE-RELAY-001 implementation sub-paragraph. `UPCOMING_PR.md` Current queue summary (new bullet), Completed / merged PRs (this row), Active / upcoming queue (PACKAGE-RELAY-001 item #6 moved from "Evidence-ready" to "Merged"), and Recently uploaded evidence (new 2026-05-22 bullet) refreshed. | **No `packages/**` edit** (`fan_relay.yaml`, the five non-voice Core abstract packages at post-001A `relay_pin: GPIO3`, and the voice-variant Core packages at pre-001A `relay_pin: GPIO4` all stay byte-identical); **no `products/**` or `products/webflash/**` edit**; **no `config/**` edit** (`config/hardware-catalog.json`, `config/product-catalog.json`, `config/webflash-builds.json`, `config/webflash-compatibility.json`, `config/firmware-combination-matrix.json`, `config/kit-intent-matrix.json`, `config/compile-only-targets.json`, `config/compile-only-candidates.json` all byte-identical); **no `scripts/**`, `.github/workflows/**`, `components/**`, `include/**`, `firmware/**`, `manifest.json`, or `firmware/sources.json` edit**. Only one `tests/**` addition: `tests/test_fan_relay_package.py` (new file). The `tests/test_core_abstract_bus.py` scaffold from 001A / 001C is preserved verbatim; no other test is edited. **No `webflash_build_matrix` flip**; **no `artifact_name` / `webflash_wrapper` / `config_string` / `release_one_required_configs` / `lifecycle_statuses` / `canonical_modules` / `canonical_power` / `forbidden_tokens` / `REQUIRED_CONFIGS` / kit change**; **no `schematic_status` / `schematic_file` promotion** (`S360-310` stays `cataloged_unverified`); **no COMPLIANCE-001 movement**; no Release-One change (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`); no LED preview change (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`); no FanTRIAC change (`blocked` / `HW-005`); no `HW-PINMAP-310-FOLLOWUP` top-line status promotion (stays `partial — schematic evidence available; package reconciliation pending`); no compile-only target added; no firmware artifact built or attached; no release artifact / tag / checksum / build-info manifest / proof row; **no WebFlash import-readiness claim**; **no hardware release-readiness claim**; **no `RELEASE-RELAY-001` unblock claim**; **no `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` / `WF-IMPORT-RELAY-001` advancement claim**; **no claim that `PACKAGE-RELAY-001` is product-ready, WebFlash-ready, release-ready, compliance-cleared, safe for arbitrary mains installation, or verified across production batches**; no Relay product YAML; no WebFlash wrapper; no compile-only target for FanRelay; no PWM / FanDAC / FanTRIAC / LED stable promotion; no `CORE-ABSTRACT-BUS-001B` advancement; **no closure of `S360-100-BENCH-001`**; **no board-level mains-safety / installation-approval / creepage / clearance / thermal / EMI certification claim**; **no production-wide / multi-unit / oscilloscope-traced general `GPIO3` strap-pin boot-behaviour characterisation claim**. | `PACKAGE-RELAY-001` is now **implemented / reconciled at the package layer only**. "Implemented / reconciled at the `PACKAGE-RELAY-001` package layer" does **not** mean product-ready, WebFlash-ready, release-ready, compliance-cleared, safe for arbitrary mains installation, or verified across production batches. The next Relay PR is `PRODUCT-RELAY-001`, which stays separately gated on product-layer compliance / mains-safety / installation / production-wide characterisation evidence. `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001` stay blocked behind PACKAGE-RELAY-001 → PRODUCT-RELAY-001. `S360-100-BENCH-001`, `HW-PINMAP-311-FOLLOWUP`, `HW-PINMAP-312-FOLLOWUP`, `HW-PINMAP-320-FOLLOWUP`, and `COMPLIANCE-001` are **not** closed by this PR. `CORE-ABSTRACT-BUS-001B` stays independent of 001A / 001C ordering. |
| FW-COMPILE-RELAY-RESULT-001  | (this PR) | esphome-public  | Merged — docs-only record of successful FanRelay compile-only CI result | Recorded the **successful GitHub Actions compile-only validation result** for the FanRelay compile-only target added by `FW-COMPILE-RELAY-001` / PR #566. The `Compile-only Firmware Validation` workflow ran against the expanded eight-target compile-only lane (the FanRelay compile-only target + the two WebFlash-current product YAMLs + the five POE non-fan compile-only skeletons) and **passed** — GitHub Actions Run ID `26298089904`, status `completed`, conclusion `success`, PR/head validation for PR #566; companion Quick Validation Run ID `26298090061` also succeeded. **FanRelay compile-only validation now has a green CI result.** Updated [`docs/compile-only-firmware-validation.md`](docs/compile-only-firmware-validation.md) (new `### 2026-05-22 — FW-COMPILE-RELAY-RESULT-001` audit-log entry recording the run ID, workflow completion, conclusion, target count of 8, what the run proves, and what it does not prove). Updated [`docs/webflash-exposure-readiness-matrix.md`](docs/webflash-exposure-readiness-matrix.md) §Relay / S360-310 WebFlash posture (new 2026-05-22 `FW-COMPILE-RELAY-RESULT-001` audit-log note recording the green CI result while explicitly recording WebFlash exposure remains blocked; the seven WebFlash gates not advanced; the four possible exposure shapes unchanged). Updated [`docs/release-artifact-readiness-matrix.md`](docs/release-artifact-readiness-matrix.md) §Relay / S360-310 release posture (new 2026-05-22 `FW-COMPILE-RELAY-RESULT-001` audit-log note recording the green CI result while explicitly recording `RELEASE-RELAY-001` remains blocked because no WebFlash wrapper / build matrix / artifact path exists; no release-proof row is added). Updated `UPCOMING_PR.md` Current queue summary (new bullet for this PR with refreshed Relay-chain status: package done; product YAML done; compile-only target done; compile-only result passed; WebFlash / release / import still blocked) and Active / upcoming queue (item #8 `WEBFLASH-RELAY-001` entry refreshed to reference this PR alongside `WEBFLASH-RELAY-001-READINESS-REFRESH` / PR #565 and `FW-COMPILE-RELAY-001` / PR #566; recommended next Relay-chain PR is `WEBFLASH-RELAY-001-SCAFFOLD-001` (if WebFlash Relay planning continues) or `CORE-ABSTRACT-BUS-001B` (if PWM / DAC blocker removal is prioritised instead)). | **No `packages/**` edit**; **no `products/**` or `products/webflash/**` edit**; **no `config/compile-only-targets.json` edit** (totals stay at 8 targets after PR #566); **no `config/compile-only-candidates.json` edit**; **no `config/webflash-builds.json` edit**; **no `config/webflash-compatibility.json` edit**; **no `config/hardware-catalog.json` edit**; **no `config/kit-intent-matrix.json` edit**; **no `config/firmware-combination-matrix.json` edit**; **no `config/product-catalog.json` edit**; **no `scripts/**`, `.github/workflows/**`, `components/**`, `include/**`, `firmware/**`, `manifest.json`, `firmware/sources.json`, `tests/**` edit** (test surface from PR #566 is preserved verbatim); **no WebFlash repo (`sense360store/WebFlash`) edit** (this PR is one-repo scope); **no `webflash_build_matrix` flip**; **no `artifact_name`**; **no `webflash_wrapper`**; **no `config_string` change**; **no `release_one_required_configs` change**; **no `lifecycle_statuses` change**; **no `canonical_modules` / `canonical_power` / `forbidden_tokens` change**; **no `REQUIRED_CONFIGS` / kit JSON change**; **no `schematic_status` / `schematic_file` promotion** (`S360-310` stays `cataloged_unverified`); **no COMPLIANCE-001 movement**; no Release-One change (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`); no LED preview change (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`); no FanTRIAC change (`blocked` / `HW-005`); no firmware artifact built or attached; no release artifact / tag / checksum / build-info manifest / proof row added; **no WebFlash import-readiness claim**; **no WebFlash exposure claim**; **no `RELEASE-RELAY-001` unblock claim**; **no `WEBFLASH-RELAY-001` unblock claim**; **no `WF-IMPORT-RELAY-001` unblock claim**; **no claim that the FanRelay product is WebFlash-ready, release-ready, compliance-cleared, safe for arbitrary mains installation, kit-default-ready, recommended-bundle-ready, hardware-stable, or verified across production batches**; **no closure of `S360-100-BENCH-001`**; **no board-level mains-safety / installation-approval / creepage / clearance / thermal / EMI certification claim**; **no production-wide / multi-unit / oscilloscope-traced general `GPIO3` strap-pin boot-behaviour characterisation claim**. | `FW-COMPILE-RELAY-RESULT-001` records the **green CI result** of the FanRelay compile-only validation introduced by PR #566. The Relay chain now stands: package done (PR #562); product YAML done (PR #564); compile-only target done (PR #566); **compile-only result passed (this PR)**; WebFlash / release / import still blocked. A green compile-only CI result is **necessary-but-insufficient** input to the broader preview-to-stable promotion process; it does **not** discharge any of the seven WebFlash gates owned by `WEBFLASH-RELAY-001`, and does **not** discharge any release-readiness gate owned by `RELEASE-RELAY-001`. The recommended next Relay-chain PR is one of `WEBFLASH-RELAY-001-SCAFFOLD-001` (if WebFlash Relay planning continues) or `CORE-ABSTRACT-BUS-001B` (if PWM / DAC blocker removal is prioritised instead); **not** immediate `WEBFLASH-RELAY-001` wrapper / catalog / build-matrix work. `CORE-ABSTRACT-BUS-001B` stays independent. `S360-100-BENCH-001`, `HW-PINMAP-311-FOLLOWUP`, `HW-PINMAP-312-FOLLOWUP`, `HW-PINMAP-320-FOLLOWUP`, and `COMPLIANCE-001` are **not** closed by this PR. |
| CORE-ABSTRACT-BUS-001B-PLAN-001 | #568      | esphome-public  | Merged — docs-only implementation plan (canonical id `core_i2c`; hard rename only) | Recorded the operator-confirmed implementation plan for `CORE-ABSTRACT-BUS-001B` (shared-I²C-bus consolidation slice) ahead of any YAML rebind. Canonical I²C bus id is now **decided: `core_i2c`**; migration style is **hard rename only**; no compatibility aliases by default (aliases will only be considered if implementation tests later prove one unavoidable). All affected old bus ids (`halo_i2c` / `expansion_i2c` / `i2c0` / `i2c1` / `i2c_primary` / `i2c_expander`) must be **removed** from the seven in-scope Core abstract packages by the future implementation slice unless an explicitly-documented package-private exception is justified. Added the new §`### 2026-05-22 — CORE-ABSTRACT-BUS-001B core_i2c plan` audit-log entry to [`docs/hardware/core-abstract-bus-reconciliation.md`](docs/hardware/core-abstract-bus-reconciliation.md) (decision table; refreshed bus-definition inventory listing the seven in-scope Core packages + two out-of-scope; consumer inventory organised into nine categories A–I — Core bus definitions, expansion `*_i2c_id` consumers (11 in-scope, two S3-variant out-of-scope, one Mini hardware-helper out-of-scope), hard-coded `i2c_id:` literals, LED / halo-specific buses (none survive the rename), GP8403 / FanDAC consumers (single consumer `fan_gp8403.yaml`), SX1509 expander consumers (single consumer `gpio_expander_sx1509.yaml`), RoomIQ / VentIQ / AirIQ sensor consumers (the same 11 expansion consumers), unused / dead / legacy references (none), tests and config catalogs; final desired mapping (single `i2c: - id: core_i2c, sda: GPIO48, scl: GPIO45, frequency: 400kHz` block per in-scope Core package); implementation scope (atomic slice: seven Core packages + 11 expansion consumers + one feature file literal + one `tests/generate_test_configs.py` override + one `SharedI2CBusTests` test class + Release-One generated-config diff check + non-Release-One product re-validation across ~25 product YAMLs); non-goals; risk notes (substitution-graph reach, hard-coded `halo_i2c` literal, out-of-scope ceiling_s3 and Mini lineages, frequency mismatch in mapping Core, pull-up evidence assumption, GP8403 / SX1509 shared-bus address space, voice-variant Cores, 001A / 001C ordering independence); test plan for implementation PR (10 assertions including canonical id present in each Core package, legacy bus ids absent, every `*_i2c_id` consumer default resolves to `core_i2c`, hard-coded literal rebound, package-specific private buses documented, FanDAC / SX1509 bind `core_i2c`, Release-One / LED preview products parse, WebFlash build rows unchanged, no product / catalog / release / WebFlash exposure changes); status update (canonical-id-decision precondition closed; downstream-consumer audit refreshed; two preconditions remain open at the implementation layer — test scaffold and non-Release-One product re-validation, both of which land **with** the implementation slice); queue effect; what-this-entry-does-not-do list). Refreshed the [§CORE-ABSTRACT-BUS-001B — Shared-I²C-bus consolidation slice](docs/hardware/core-abstract-bus-reconciliation.md#core-abstract-bus-001b--shared-i²c-bus-consolidation-slice) "next audit-log trigger" section to drop the canonical-id-decision trigger and reword the implementation-slice trigger to reference the `core_i2c` rename target. Refreshed `UPCOMING_PR.md` Current queue summary (new bullet for this PR), Completed / merged PRs (this row), Active / upcoming queue (item #1 `CORE-ABSTRACT-BUS-001B` entry refreshed: canonical id `core_i2c` named; hard-rename-only recorded; seven in-scope Core packages enumerated; 11 in-scope expansion-package consumer defaults enumerated; out-of-scope packages enumerated; rationale recorded; two remaining preconditions identified — test scaffold + non-Release-One product re-validation, both land **with** implementation slice). **`PACKAGE-PWM-001` / `PACKAGE-DAC-001` blocker status is unchanged** — they remain blocked behind (a) `001B` implementation actually landing in YAML, (b) the underlying per-board pinmap evidence (`HW-PINMAP-311-FOLLOWUP` / `HW-PINMAP-312-FOLLOWUP`), and (c) BOM cross-checks. The PWM / DAC compile-only candidate rows in `config/compile-only-candidates.json` keep all of their existing blockers. | **No `packages/**` edit**; **no `products/**` or `products/webflash/**` edit**; **no `config/**` edit** (`config/hardware-catalog.json`, `config/product-catalog.json`, `config/webflash-builds.json`, `config/webflash-compatibility.json`, `config/firmware-combination-matrix.json`, `config/kit-intent-matrix.json`, `config/compile-only-targets.json`, `config/compile-only-candidates.json` all byte-identical); **no `scripts/**`, `.github/workflows/**`, `components/**`, `include/**`, `firmware/**`, `manifest.json`, `firmware/sources.json`, `tests/**` edit** (no I²C bus is renamed; no `*_i2c_id` consumer default is changed; the hard-coded `i2c_id: halo_i2c` literal in `packages/features/ceiling_halo_leds.yaml` line 6 is **not** rebound; the `tests/generate_test_configs.py` `fan_dac_i2c_id: expansion_i2c` override at line 145 is **not** removed; no `SharedI2CBusTests` scaffold is added; `tests/test_core_abstract_bus.py` is unchanged from PR #558); **no WebFlash repo (`sense360store/WebFlash`) edit** (this PR is one-repo scope; the WebFlash repo is re-read read-only — `CORE-ABSTRACT-BUS-001` is referenced only as an upstream dependency, no WebFlash file changes); **no `webflash_build_matrix` flip**; **no `artifact_name`**; **no `webflash_wrapper`**; **no `config_string` change**; **no `release_one_required_configs` change**; **no `lifecycle_statuses` change**; **no `canonical_modules` / `canonical_power` / `forbidden_tokens` change**; **no `REQUIRED_CONFIGS` / kit JSON change**; **no `schematic_status` / `schematic_file` promotion**; **no COMPLIANCE-001 movement**; no Release-One change (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`); no LED preview change (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`); no FanTRIAC change (`blocked` / `HW-005`); no compile-only target added; no firmware artifact built or attached; no release artifact / tag / checksum / build-info manifest / proof row; **no WebFlash import-readiness claim**; **no `PACKAGE-PWM-001` unblock claim**; **no `PACKAGE-DAC-001` unblock claim**; **no `PACKAGE-RELAY-001` re-implementation claim**; **no claim that `CORE-ABSTRACT-BUS-001B` has advanced past the planning layer**; no claim of compliance evidence for any mains-switching product; no `S360-100-BENCH-001` closure. | `CORE-ABSTRACT-BUS-001B` moves from `confirmed deferred (Path A docs-only); four preconditions still open` (PR #519) to **implementation-plannable** at the planning layer. The canonical-id-decision precondition (#1 of the four enumerated by PR #519) is **closed** by this PR (chose `core_i2c`; recorded hard-rename-only + no-aliases policy). The downstream-consumer audit precondition (#4) is **refreshed** in this PR (extended with the four product `!include`rs that `packages/features/ceiling_halo_leds.yaml` gained since PR #519, the `tests/generate_test_configs.py` override, and the explicit out-of-scope classification for the Mini family and ceiling_s3 lineage). Two preconditions remain open at the implementation layer: (#2) extending [`tests/test_core_abstract_bus.py`](tests/test_core_abstract_bus.py) with a `SharedI2CBusTests` class — lands **with** the implementation slice; (#3) the re-validation pass for every non-Release-One product YAML consuming any affected Core / expansion package (~25 product YAMLs) — execution lands **with** the implementation slice. The implementation slice (`CORE-ABSTRACT-BUS-001B-IMPLEMENT-001`) must land all of the following as a single atomic PR: (1) the YAML rebind across the seven in-scope Core packages; (2) the 11 expansion-package consumer rebinds; (3) the `ceiling_halo_leds.yaml` literal rebind; (4) the `tests/generate_test_configs.py` override removal; (5) the `SharedI2CBusTests` scaffold; (6) the Release-One + LED preview generated-config diff check; (7) the re-validation pass for every non-Release-One product YAML. `PACKAGE-PWM-001` / `PRODUCT-PWM-001` / `WEBFLASH-PWM-001` / `RELEASE-PWM-001` stay blocked on the underlying `HW-PINMAP-311-FOLLOWUP` evidence **and** on `001B` implementation. `PACKAGE-DAC-001` / `PRODUCT-DAC-001` / `WEBFLASH-DAC-001` / `RELEASE-DAC-001` stay blocked on the underlying `HW-PINMAP-312-FOLLOWUP` evidence **and** on `001B` implementation. The canonical-id decision recorded here does **not** unblock either chain. `PACKAGE-RELAY-001` / `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001` stay blocked behind `PACKAGE-RELAY-001` bench / silkscreen / harness / `K1` BOM gates (independent of `001B`). `CORE-ABSTRACT-BUS-001A` (PR #558) and `CORE-ABSTRACT-BUS-001C` (PR #557) stay completed-merged. `S360-100-BENCH-001`, `HW-PINMAP-311-FOLLOWUP`, `HW-PINMAP-312-FOLLOWUP`, `HW-PINMAP-320-FOLLOWUP`, and `COMPLIANCE-001` are **not** closed by this PR. |
| CORE-ABSTRACT-BUS-001B-IMPLEMENT-001 | (this PR) | esphome-public  | Merged — implementation slice (hard rename of legacy I²C bus ids to `core_i2c` across seven Core abstract packages, 10 expansion-package consumer defaults, the hard-coded `ceiling_halo_leds.yaml` literal, the `generate_test_configs.py` override, and a 13-case `SharedI2CBusTests` scaffold) | Applied the schematic-correct hard rename to the canonical shared `core_i2c` bus id (`GPIO48` SDA / `GPIO45` SCL / `400kHz`) recorded by `CORE-ABSTRACT-BUS-001B-PLAN-001` / PR #568. Seven Core abstract packages updated: `packages/hardware/sense360_core.yaml`, `packages/hardware/sense360_core_ceiling.yaml`, `packages/hardware/sense360_core_mapping.yaml`, `packages/hardware/sense360_core_poe.yaml`, `packages/hardware/sense360_core_wall.yaml`, `packages/hardware/sense360_core_voice_ceiling.yaml`, `packages/hardware/sense360_core_voice_wall.yaml` — each dual-bus `i2c:` block (legacy `halo_i2c` / `expansion_i2c` / `i2c0` / `i2c1` / `i2c_primary` / `i2c_expander` ids on `GPIO39` / `GPIO40` / `GPIO21` / `GPIO18`) replaced with single `i2c: - id: core_i2c, sda: GPIO48, scl: GPIO45, frequency: 400kHz` block; `i2c0_*` / `i2c1_*` / `halo_i2c_*` / `expansion_i2c_*` pin / frequency substitutions retired (hard rename only, no compatibility aliases per operator decision #4). Ten expansion-package `*_i2c_id` consumer defaults rebound to `core_i2c`: `airiq.yaml`, `airiq_wall.yaml`, `airiq_ceiling.yaml`, `airiq_bathroom_base.yaml`, `airiq_bathroom_pro.yaml`, `comfort.yaml`, `comfort_wall.yaml`, `comfort_ceiling.yaml`, `fan_gp8403.yaml`, `gpio_expander_sx1509.yaml`; the FanDAC alias `packages/expansions/fan_dac.yaml` inherits via its `!include` of `fan_gp8403.yaml`. Hard-coded `i2c_id: halo_i2c` literal in `packages/features/ceiling_halo_leds.yaml` line 6 rebound to `i2c_id: core_i2c` (the PCA9685 halo LED driver now binds the shared Core I²C bus). `tests/generate_test_configs.py` per-product `fan_dac_i2c_id: expansion_i2c` override removed (new default at `fan_gp8403.yaml` resolves to `core_i2c` directly). `sense360_core_mapping.yaml` legacy `i2c_primary_healthy` / `i2c_expander_healthy` globals consolidated to a single `core_i2c_healthy` flag (both globals were internal-only; no consumer outside the package). Extended `tests/test_core_abstract_bus.py` with new `SharedI2CBusTests` class (13 cases) asserting: canonical `core_i2c` bus present in each in-scope Core package with `GPIO48` / `GPIO45` / `400kHz`; legacy bus ids absent in every in-scope Core package; each in-scope Core defines exactly one i2c bus; every in-scope `*_i2c_id` consumer default equals `core_i2c`; `ceiling_halo_leds.yaml` literal rebound; FanDAC / GP8403 bind `core_i2c` via substitution; FanDAC alias `!include`s the GP8403 implementation; SX1509 binds `core_i2c` via substitution; `generate_test_configs.py` no longer sets `expansion_i2c` override; ceiling_s3 retains `i2c_primary`; Mini retains `i2c0`; no legacy bus id appears on any active consumer line outside the documented out-of-scope set; no legacy pin substitutions survive in the seven in-scope Core packages. Out-of-scope packages stay byte-for-byte unchanged on the I²C bus axis per operator decision #10: `packages/hardware/sense360_core_ceiling_s3.yaml` (keeps `i2c_primary` on `GPIO17`/`GPIO18`), `packages/hardware/sense360_core_mini.yaml` (keeps `i2c0` on the already-schematic-correct `GPIO48`/`GPIO45`), `packages/expansions/airiq_ceiling_s3.yaml` and `packages/expansions/comfort_ceiling_s3.yaml` (S3 lineage), `packages/hardware/mini_onboard_sensors.yaml` (Mini baseline), and the six `products/sense360-mini-*.yaml` inline `i2c0` definitions (Mini baseline). Voice-variant Core `relay_pin: GPIO4` stays deliberately out of scope for `001A`. Updated `docs/hardware/core-abstract-bus-reconciliation.md` with a new `### 2026-05-22 — CORE-ABSTRACT-BUS-001B implementation` audit-log entry recording the file-by-file rebind, the out-of-scope-preserved set, the validation result, and the status (all four preconditions enumerated by PR #519 now closed; `001B` moves from `implementation-plannable` to **implemented**); refreshed the document Status header to reflect that all three 001A / 001B / 001C slices have now landed at the substitution layer; refreshed the "Next audit-log trigger" section to reference the still-uncaptured `esphome config` generated-config diff (ESPHome unavailable at implementation time) and the voice-variant Core `relay_pin` rebind as future triggers. Refreshed `UPCOMING_PR.md` Current queue summary (new bullet for this PR), Completed / merged PRs (this row), Active / upcoming queue (item #1 `CORE-ABSTRACT-BUS-001B` entry status moved from `Plan recorded 2026-05-22 — implementation-plannable` to `Implemented 2026-05-22 (this PR)`). Static validation: `python3 tests/validate_configs.py` PASS (202 / 202); `python3 scripts/validate_compile_targets.py --metadata-only` PASS (8 / 8); `python3 tests/test_core_abstract_bus.py` PASS (33 / 33 — 20 pre-existing 001A / 001C cases + 13 new `SharedI2CBusTests` cases); `python3 tests/test_fan_relay_package.py` PASS (12 / 12); `python3 tests/test_relay_product_readiness.py` PASS (59 / 59); `python3 tests/test_compile_targets.py` PASS (67 / 67); `python3 tests/test_compile_expansion_candidates.py` PASS (37 / 37); `python3 tests/test_firmware_combination_matrix.py` PASS (24 / 24); `python3 tests/test_firmware_build_gap_report.py` PASS (27 / 27); `python3 tests/test_product_substitutions.py` PASS; `python3 tests/test_release_one_entity_names.py` PASS (1 / 1); `python3 tests/validate_webflash_builds.py` PASS (2 / 2); `python3 -m unittest discover -s tests -p "test_*.py"` PASS (515 / 515 — +13 vs the pre-001B baseline of 502). ESPHome was **not** available in the implementation environment, so the `esphome config` generated-config diff check against Release-One (`products/sense360-ceiling-poe-ventiq-roomiq.yaml`) and the LED preview (`products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`) was **not** executed; the implementation relies on the static validators above plus the new `SharedI2CBusTests` substitution-graph assertions. The expected diff is bus-identity only — every I²C-bound sensor moves from `i2c_id: expansion_i2c` (or whichever legacy id its path resolved to) to `i2c_id: core_i2c`; the single bus block moves from `id: halo_i2c` + `id: expansion_i2c` to one `id: core_i2c` on `sda: GPIO48` / `scl: GPIO45` / `frequency: 400kHz`. No entity name change, no `config_string` change, no `artifact_name` change, no LED-ring pin change, no WebFlash exposure change, no release-channel change, no GPIO pin change unrelated to I²C. `PACKAGE-PWM-001` and `PACKAGE-DAC-001` are now unblocked **only at the shared-I²C-bus layer**; both still require their own per-board evidence (`HW-PINMAP-311-FOLLOWUP` / `HW-PINMAP-312-FOLLOWUP`) and BOM cross-checks. The compile-only candidate rows for FanPWM (`S360-311`) and FanDAC (`S360-312`) in `config/compile-only-candidates.json` keep their remaining blockers; this PR does **not** flip either to `complete`, does **not** add any compile-only target, and does **not** edit the catalog. | **No `products/**` or `products/webflash/**` edit**; **no `config/**` edit** (`config/hardware-catalog.json`, `config/product-catalog.json`, `config/webflash-builds.json`, `config/webflash-compatibility.json`, `config/firmware-combination-matrix.json`, `config/kit-intent-matrix.json`, `config/compile-only-targets.json`, `config/compile-only-candidates.json` all byte-identical); **no `scripts/**`, `.github/workflows/**`, `components/**`, `include/**`, `firmware/**`, `manifest.json`, `firmware/sources.json` edit**; **no WebFlash repo (`sense360store/WebFlash`) edit** (this PR is one-repo scope; the WebFlash repo is re-read read-only); **no `webflash_build_matrix` flip**; **no `artifact_name`**; **no `webflash_wrapper`**; **no `config_string` change**; **no `release_one_required_configs` change**; **no `lifecycle_statuses` change**; **no `canonical_modules` / `canonical_power` / `forbidden_tokens` change**; **no `REQUIRED_CONFIGS` / kit JSON change**; **no `schematic_status` / `schematic_file` promotion**; **no COMPLIANCE-001 movement**; no Release-One change (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`); no LED preview change (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`); no FanTRIAC change (`blocked` / `HW-005`); voice-variant Core `relay_pin` stays at pre-001A `GPIO4` (deliberately out of scope for 001A); the two S3-variant Core / expansion packages and the Mini family stay byte-for-byte unchanged on the I²C bus axis; no compile-only target added; no firmware artifact built or attached; no release artifact / tag / checksum / build-info manifest / proof row; **no WebFlash import-readiness claim**; **no claim that `PACKAGE-PWM-001` is complete**; **no claim that `PACKAGE-DAC-001` is complete**; **no `PACKAGE-RELAY-001` / `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001` advancement claim**; no claim of compliance evidence for any mains-switching product; **no `S360-100-BENCH-001` closure**. | `CORE-ABSTRACT-BUS-001B` moves from `implementation-plannable` (PR #568) to **implemented**. All four preconditions enumerated by PR #519 are now closed: (#1) canonical I²C bus-id decision (`core_i2c`, PR #568); (#2) `tests/test_core_abstract_bus.py` pin-pinning scaffold (`SharedI2CBusTests`, this PR); (#3) re-validation pass for every non-Release-One product YAML (`python3 tests/validate_configs.py` exits 0 across all 202 configs including the ~25 product YAMLs that transitively consume the affected packages, this PR); (#4) downstream-consumer audit (PR #519, refreshed PR #568, verified against post-rename live YAML this PR). `PACKAGE-PWM-001` and `PACKAGE-DAC-001` are now unblocked only at the shared-I²C-bus layer; both still require `HW-PINMAP-311-FOLLOWUP` / `HW-PINMAP-312-FOLLOWUP` evidence and BOM cross-checks. `PACKAGE-RELAY-001` / `PRODUCT-RELAY-001` / `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` / `WF-IMPORT-RELAY-001` stay blocked behind their own bench / silkscreen / harness / `K1` BOM gates (independent of `001B`). `CORE-ABSTRACT-BUS-001A` (PR #558) and `CORE-ABSTRACT-BUS-001C` (PR #557) stay completed-merged. `S360-100-BENCH-001`, `HW-PINMAP-311-FOLLOWUP`, `HW-PINMAP-312-FOLLOWUP`, `HW-PINMAP-320-FOLLOWUP`, and `COMPLIANCE-001` are **not** closed by this PR. |
| PACKAGE-DAC-001-IMPLEMENT-001 | #573      | esphome-public  | Merged — package-layer implementation slice (FanDAC dual-GP8403 reconciliation) | Reconciled [`packages/expansions/fan_gp8403.yaml`](packages/expansions/fan_gp8403.yaml) from the legacy single-DAC / two-channel form to the schematic-correct **two-DAC / four-output** form after `HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001` (PR #572) closed rows 3 / 6 / 8, applying operator decisions D1–D6: two `gp8403:` devices `fan_dac_1` (IC1) / `fan_dac_2` (IC2) on `${fan_dac_i2c_id}` (`core_i2c`); per-chip address substitutions `fan_dac_1_i2c_address` (`0x58`) / `fan_dac_2_i2c_address` (`0x59`); per-chip output-range substitutions `fan_dac_1_output_range` / `fan_dac_2_output_range` (both default `0-10V`, independently overridable, register `0x01` per chip); four neutral outputs `fan_dac_1_vout0` / `fan_dac_1_vout1` / `fan_dac_2_vout0` / `fan_dac_2_vout1`; corrected the stale "(jumper selectable on hardware)" line-6 comment to firmware/register-driven; recorded that a single GP8403 cannot mix 0–5 V / 0–10 V across its two outputs; and removed the product-layer `fan:` / `sensor:` / `globals:` / `script:` blocks (hard-coded `${friendly_name}` fan names → move to `PRODUCT-DAC-001`). [`packages/expansions/fan_dac.yaml`](packages/expansions/fan_dac.yaml) unchanged (canonical pure-wrapper). Added [`tests/test_fandac_package.py`](tests/test_fandac_package.py) (20 cases). Refreshed [`docs/hardware/s360-312-r4-fandac.md`](docs/hardware/s360-312-r4-fandac.md) (status line + new §2026-05-23 implementation section + audit-log row), [`docs/hardware/package-readiness-matrix.md`](docs/hardware/package-readiness-matrix.md) (`fan_gp8403.yaml` row + detail block → `package-layer-implemented`), [`docs/hardware/firmware-package-mapping-audit.md`](docs/hardware/firmware-package-mapping-audit.md) (cross-reference note), `UPCOMING_PR.md` (Current queue summary + queue entry 14 + this row). Validation: `python3 tests/validate_configs.py` PASS (202 / 202); `python3 scripts/validate_compile_targets.py --metadata-only` PASS; `python3 tests/test_core_abstract_bus.py` PASS (33 / 33); `python3 tests/test_fandac_alias_packages.py` PASS (12 / 12); `python3 tests/test_fandac_package.py` PASS (20 / 20); `python3 -m unittest discover -s tests -p "test_*.py"` PASS (535 / 535). | **No `products/**` or `products/webflash/**` edit; no DAC product YAML added; no compile-only target added; no WebFlash wrapper; no `config/**`, `scripts/**`, `.github/workflows/**`, `components/**`, `include/**`, `firmware/**`, `manifest.json`, `firmware/sources.json`, release-artifact, checksum, or build-info edit; no `webflash_build_matrix` flip; no `artifact_name`; no `schematic_status` / `schematic_file` promotion (`S360-312` stays `cataloged_unverified`); no claim of simultaneous per-output 0–5 V + 0–10 V on a single GP8403; no DAC product / WebFlash / release / compliance readiness claim; the WebFlash repo (`sense360store/WebFlash`) is untouched.** | `PACKAGE-DAC-001` is now **implemented at the package layer**; product / WebFlash / release readiness remains blocked. `PRODUCT-DAC-001-READINESS-REFRESH` (this PR) re-evaluates the product layer and finds the `gp8403:` `voltage:` field is fed the neutral `0-10V` value (not ESPHome's bare `10V` / `5V` enum) with no compile-only target, so the recommended next PR is `FW-COMPILE-DAC-001` (compile-only validation / `0-10V`→`10V` fix) **before** `PRODUCT-DAC-001`. Residual product / bench items (Cloudlift S12 harness trace, `J3` silk-transposition confirmation, as-shipped DIP default, `J1` / `J7` `+3.3 V` / `+5 V` rail discrepancy via `S360-100-BENCH-001`, and `S360-312` `schematic_status` promotion) do not block the package. |
| PRODUCT-DAC-001-READINESS-REFRESH | (this PR) | esphome-public  | Merged — docs / readiness-only refresh defining FanDAC product-layer gates after PACKAGE-DAC-001 / PR #573 | Re-evaluated `PRODUCT-DAC-001` after the package-layer landing (PR #573). Recorded the package as `package-layer-implemented` + `compile-validation-pending` across the readiness matrices; identified that the `gp8403:` `voltage:` field is fed the neutral `0-10V` value rather than ESPHome's bare `10V` / `5V` enum and that, with no FanDAC compile-only target, the compile is **unvalidated**. Verdict: product YAML waits on **`FW-COMPILE-DAC-001`** (compile-only validation; confirm `0-10V` validates or record the `0-10V` → `10V` fix) before `PRODUCT-DAC-001`. Recorded product-layer gates: `J2` / `J3` board-level pin mapping captured but the Cloudlift S12 harness conductor trace stays a product / bench item; the `J3` `out0` / `out1` silkscreen transposition must be carried into product docs / caveats; user-facing outputs map to outcome-first names ("0–10V fan control" / "Cloudlift S12 fan control") while the package keeps neutral output IDs; Nextion / `J7` is out of scope for the first DAC product unless it drives a display; `WEBFLASH-DAC-001` + `RELEASE-DAC-001` stay blocked. Updated [`docs/product-readiness-matrix.md`](docs/product-readiness-matrix.md) (§FanDAC / S360-312 + candidate-table row + new `FW-COMPILE-DAC-001` / refreshed `PRODUCT-DAC-001` gate rows), [`docs/webflash-exposure-readiness-matrix.md`](docs/webflash-exposure-readiness-matrix.md) (§DAC posture refresh-note + matrix row), [`docs/release-artifact-readiness-matrix.md`](docs/release-artifact-readiness-matrix.md) (§DAC posture refresh-note + matrix row), [`docs/kit-intent-matrix.md`](docs/kit-intent-matrix.md) (`S360-KIT-DUCT-0-10V` status note), and `UPCOMING_PR.md` (Current queue summary + this row + active-queue `FW-COMPILE-DAC-001` entry + refreshed `PRODUCT-DAC-001` row). Validation: `python3 tests/validate_configs.py`; `python3 scripts/validate_compile_targets.py --metadata-only`; `python3 tests/test_core_abstract_bus.py`; `python3 tests/test_fandac_alias_packages.py`; `python3 tests/test_fandac_package.py`; `python3 tests/test_compile_targets.py`; `python3 tests/test_compile_expansion_candidates.py`; `python3 tests/test_firmware_combination_matrix.py`; `python3 tests/test_firmware_build_gap_report.py`; `python3 tests/validate_webflash_builds.py`; `python3 -m unittest discover -s tests -p "test_*.py"`. | **Docs / readiness only. No edit to `packages/expansions/fan_gp8403.yaml` or `fan_dac.yaml`; no DAC product YAML; no compile-only target; no WebFlash wrapper; no `config/**`, `products/**`, `products/webflash/**`, `scripts/**`, `.github/workflows/**`, `components/**`, `include/**`, `tests/**`, `firmware/**`, `manifest.json`, `firmware/sources.json`, release-artifact, checksum, or build-info edit; no `webflash_build_matrix` flip; no `artifact_name`; no `schematic_status` / `schematic_file` promotion (`S360-312` stays `cataloged_unverified`); no claim of compile validation (none was run); no claim of simultaneous per-output 0–5 V + 0–10 V on a single GP8403; no DAC product / WebFlash / release readiness claim; the WebFlash repo (`sense360store/WebFlash`) is untouched.** | The recommended next PR is `FW-COMPILE-DAC-001` (compile-only validation of the `voltage:` binding) before `PRODUCT-DAC-001`. `WEBFLASH-DAC-001` / `RELEASE-DAC-001` / `WF-IMPORT-DAC-001` stay blocked behind it. |
| FW-COMPILE-DAC-001 | #575 | esphome-public  | Merged — compile-only validation + package voltage-enum fix (Option A) | Added compile-only / config-validation coverage for the FanDAC package after PR #573 / PR #574. **Fixed the `gp8403:` `voltage:` enum (Option A):** ESPHome's gp8403 accepts only `10V` / `5V`, so [`packages/expansions/fan_gp8403.yaml`](packages/expansions/fan_gp8403.yaml) `fan_dac_1_output_range` / `fan_dac_2_output_range` were corrected from the invalid `0-10V` string to `10V` (customer-facing 0-10V; user-facing 0-10V / 0-5V labels stay in product / kit docs), matching the default `10V` operator decision D3 implied. Added the compile-only target `ceiling-poe-fandac-compile-only` ([`config/compile-only-targets.json`](config/compile-only-targets.json), totals 8→9) pointing at the new skeleton [`products/compile-only/ceiling-poe-fandac.yaml`](products/compile-only/ceiling-poe-fandac.yaml) (config string `Ceiling-POE-FanDAC`; Core ceiling + PoE PSU + base + health + FanDAC alias). Refreshed the FanDAC row + `currently_compile_only_config_strings` in [`config/compile-only-candidates.json`](config/compile-only-candidates.json). Extended [`tests/test_fandac_package.py`](tests/test_fandac_package.py) (enum-validity) and [`tests/test_compile_targets.py`](tests/test_compile_targets.py) (`FanDACCompileOnlyCoverageTests`). Updated [`docs/compile-only-firmware-validation.md`](docs/compile-only-firmware-validation.md), [`docs/product-readiness-matrix.md`](docs/product-readiness-matrix.md), [`docs/hardware/s360-312-r4-fandac.md`](docs/hardware/s360-312-r4-fandac.md), [`docs/webflash-exposure-readiness-matrix.md`](docs/webflash-exposure-readiness-matrix.md), [`docs/release-artifact-readiness-matrix.md`](docs/release-artifact-readiness-matrix.md), `UPCOMING_PR.md`. Validation: `python3 -m unittest discover -s tests -p "test_*.py"` PASS (559 / 559); `python3 scripts/validate_compile_targets.py --metadata-only` PASS; `python3 tests/validate_configs.py` PASS. | **No DAC product YAML at the top level of `products/`; no `config/product-catalog.json` entry; no WebFlash wrapper; no `config/webflash-builds.json` entry (FanDAC token absent there); no `webflash_build_matrix` flip; no `artifact_name`; no release artifact; no `firmware/**`, `manifest.json`, `firmware/sources.json`, `.github/workflows/**`, `components/**`, `include/**` edit; no `schematic_status` / `schematic_file` promotion; no claim of compile success (CI `--compile` pending); no claim of simultaneous per-output 0–5 V + 0–10 V on a single GP8403; the WebFlash repo (`sense360store/WebFlash`) is untouched.** | The gp8403 voltage-enum concern is **resolved** (Option A). `PRODUCT-DAC-001` stays gated on the CI `--compile` pass (`compile_validation_status: pending-ci`) + `S360-312 schematic_status: verified`. `WEBFLASH-DAC-001` / `RELEASE-DAC-001` / `WF-IMPORT-DAC-001` stay blocked behind it. |
| FW-COMPILE-DAC-RESULT-001 | (this PR) | esphome-public  | Merged — docs-only record of FanDAC compile-only CI result (metadata lane green; full ESPHome compile skipped on PR) | Recorded the **GitHub Actions compile-only validation result** for the FanDAC compile-only target added by `FW-COMPILE-DAC-001` / PR #575. The `Compile-only Firmware Validation` workflow ran against the expanded nine-target compile-only lane on the PR head and the **metadata-validation lane passed** — Run ID `26332462496`, status `completed`, conclusion `success`, target count 9; companion Quick Validation Run ID `26332462516` also succeeded. **Recorded green, but precise:** the `Compile-only Targets — Full ESPHome Compile` job was **`skipped`** (it runs only on a manual `workflow_dispatch` with `compile_mode=full` per [`.github/workflows/compile-only.yml`](.github/workflows/compile-only.yml) line 103), so **no `esphome config` / `esphome compile` ran against the FanDAC skeleton in CI**. The green result proves the metadata / structural lane (target shape, cross-references, count 9, guardrails, and the `voltage: 10V` enum pinned by `tests/test_fandac_package.py` against ESPHome's documented `gp8403` schema), **not** a full ESPHome compile; `compile_validation_status: pending-ci` **stands**. Updated [`docs/compile-only-firmware-validation.md`](docs/compile-only-firmware-validation.md) (new `### 2026-05-23 — FW-COMPILE-DAC-RESULT-001` audit-log entry: workflow / run ID / conclusion / target count 9; jobs incl. the skipped full-compile; what it proves vs. does not prove), [`docs/product-readiness-matrix.md`](docs/product-readiness-matrix.md) (§FanDAC / S360-312 Status + compile-pass + next-PR bullets), [`docs/webflash-exposure-readiness-matrix.md`](docs/webflash-exposure-readiness-matrix.md) (§DAC / S360-312 posture note; `WEBFLASH-DAC-001` stays blocked), [`docs/release-artifact-readiness-matrix.md`](docs/release-artifact-readiness-matrix.md) (§DAC / S360-312 posture note; `RELEASE-DAC-001` stays blocked), and `UPCOMING_PR.md` (Current queue summary bullet + this row + active-queue items 14 / 15 refresh). | **No `packages/**` edit** (`fan_gp8403.yaml` / `fan_dac.yaml` byte-identical); **no `products/**` or `products/webflash/**` edit**; **no `config/compile-only-targets.json` / `config/compile-only-candidates.json` edit** (totals stay 9 after PR #575); **no `config/webflash-builds.json` / `config/webflash-compatibility.json` / `config/product-catalog.json` / `config/hardware-catalog.json` / `config/kit-intent-matrix.json` / `config/firmware-combination-matrix.json` edit**; **no `scripts/**`, `.github/workflows/**`, `components/**`, `include/**`, `firmware/**`, `manifest.json`, `firmware/sources.json`, `tests/**` edit**; **no WebFlash repo (`sense360store/WebFlash`) edit**; **no `webflash_build_matrix` flip**; **no `artifact_name`**; **no `webflash_wrapper`**; **no `config_string` change**; **no `release_one_required_configs` change**; **no `schematic_status` / `schematic_file` promotion** (`S360-312` stays `cataloged_unverified`); **no release artifact / tag / checksum / build-info manifest / proof row**; **no claim of compile success, DAC product / WebFlash / release readiness, harness / fan bench validation, compliance approval, or simultaneous per-output 0-5V + 0-10V on a single GP8403.** Release-One stays `Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`; LED preview stays `Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`; FanTRIAC stays `blocked` / `HW-005`. | `FW-COMPILE-DAC-RESULT-001` records the **green metadata CI result** of the FanDAC compile-only validation introduced by PR #575. The DAC chain now stands: evidence done (PR #572); package done (PR #573); compile-only target + voltage-enum fix done (PR #575); **compile-only (metadata) result passed (this PR)**; next recommended PR `PRODUCT-DAC-001`, gated on the still-owed full `--compile` pass (`workflow_dispatch` `compile_mode=full`) + `S360-312 schematic_status: verified`; `WEBFLASH-DAC-001` / `RELEASE-DAC-001` / `WF-IMPORT-DAC-001` stay blocked behind it. A green compile-only CI result is **necessary-but-insufficient** input to the broader preview-to-stable promotion process; it discharges no DAC product / WebFlash / release / hardware / compliance gate. |
| PRODUCT-DAC-001 | (this PR) | esphome-public | Merged — implementation slice (product-YAML-only / no-WebFlash-exposure) | Added the canonical FanDAC product YAML [`products/sense360-ceiling-poe-fandac.yaml`](products/sense360-ceiling-poe-fandac.yaml) (config string `Ceiling-POE-FanDAC`) as the product-YAML-only / no-WebFlash-exposure slice following PACKAGE-DAC-001 (PR #573) and the FW-COMPILE-DAC-001 / FW-COMPILE-DAC-RESULT-001 compile-only **metadata** lane (PR #575 / PR #576). The YAML composes Core ceiling abstract + `packages/hardware/power_poe.yaml` + base + `packages/features/device_health.yaml` + the canonical FanDAC alias `packages/expansions/fan_dac.yaml` (→ `fan_gp8403.yaml`; two GP8403 DACs / four neutral outputs); inherits `fan_dac_i2c_id: core_i2c` + per-chip address + per-chip `voltage: 10V` enum from the package without hard-coding them; header carries explicit caveats: full ESPHome compile still **owed** (`compile_validation_status: pending-ci`; only the compile-only metadata lane is green; manual `workflow_dispatch compile_mode=full` run owed), `J3` `out0`/`out1` silkscreen transposition, Cloudlift S12 harness / product-bench residual, FanDAC ↔ AirIQ mutex (no AirIQ token), per-chip (not per-output) output-range limitation, Nextion / `J7` out of scope (no `uart:` / `display:`), not WebFlash exposed, not a default / recommended kit, not a release artifact, not compliance-certified, not hardware-stable-ready. Outcome-first user-facing naming ("0-10V fan control" / "Cloudlift S12 fan control"); neutral package output IDs unchanged. Added a non-WebFlash row to `config/product-catalog.json` (`config_string: Ceiling-POE-FanDAC`, `status: hardware-pending`, `webflash_build_matrix: false`, no `artifact_name`, no `webflash_wrapper`, `hardware_status: package-implemented-product-layer-pending`) required by the [`tests/test_product_catalog.py`](tests/test_product_catalog.py) enumeration. Regenerated `config/firmware-combination-matrix.json` (the `Ceiling-POE-FanDAC` row reclassifies `missing-product-yaml` → `blocked-hardware`; 168-row total unchanged) and `docs/firmware-build-gap-report.md` via `scripts/generate_firmware_matrix.py` and `scripts/report_firmware_build_gaps.py`. Added new test `tests/test_dac_product_readiness.py` (44 stdlib-unittest cases) pinning the non-WebFlash invariants + caveats. Updated the superseded pre-PRODUCT-DAC-001 guards in `tests/test_compile_targets.py` (the `test_no_normal_fandac_product_yaml_added` guard replaced with landed-product / compile-only-separation / no-webflash-wrapper assertions) and `tests/test_fandac_package.py` (the "no top-level product includes the FanDAC package" guard replaced with an exactly-the-canonical-product-YAML assertion). Updated docs `docs/product-readiness-matrix.md` §FanDAC / S360-312 (Product YAML action + Status + sequence), `docs/webflash-exposure-readiness-matrix.md` §DAC / S360-312 (PRODUCT-DAC-001 posture note; `WEBFLASH-DAC-001` stays blocked), `docs/release-artifact-readiness-matrix.md` §DAC / S360-312 (posture note; `RELEASE-DAC-001` stays blocked), `docs/kit-intent-matrix.md` §S360-KIT-DUCT-0-10V (kit stays future-expansion / hardware-pending), `docs/hardware/s360-312-r4-fandac.md` (new audit-log row), and this `UPCOMING_PR.md`. | **No `packages/**` edit** (the FanDAC package and Core abstract packages are consumed as-is); **no `products/webflash/**` edit**; **no `config/webflash-builds.json` edit** (the `FanDAC` token stays absent there); **no `config/webflash-compatibility.json` edit** (`release_one_required_configs` stays `[Ceiling-POE-VentIQ-RoomIQ]`; the `FanDAC` ↔ `AirIQ` mutex is not relaxed); **no `config/hardware-catalog.json` / `config/kit-intent-matrix.json` / `config/compile-only-targets.json` / `config/compile-only-candidates.json` edit** (the FanDAC compile-only target stays unchanged at 9 targets); **no `scripts/**` edit** (only the outputs of `scripts/generate_firmware_matrix.py` and `scripts/report_firmware_build_gaps.py` are refreshed; the scripts are byte-identical); **no `.github/workflows/**`, `components/**`, `include/**`, `firmware/**`, `manifest.json`, `firmware/sources.json` edit**; **no `webflash_build_matrix` flip**; **no `artifact_name`**; **no `webflash_wrapper`**; **no `schematic_status` / `schematic_file` promotion** (`S360-312` stays `cataloged_unverified`); **no release artifact / tag / checksum / build-info manifest / proof row**; **no claim of full compile success, DAC WebFlash / release / import readiness, harness / fan bench validation, compliance approval, hardware-stable readiness, or simultaneous per-output 0-5V + 0-10V on a single GP8403.** Release-One stays `Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`; LED preview stays `Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`; FanTRIAC stays `blocked` / `HW-005`; FanRelay stays `hardware-pending`; the existing FanDAC compile-only target is unchanged. The WebFlash repository (`sense360store/WebFlash`) is untouched. | `PRODUCT-DAC-001` is now **landed as a product-YAML-only / no-WebFlash-exposure slice**. The FanDAC product YAML exists under `products/`; the matching non-WebFlash catalog row exists in `config/product-catalog.json`; structural invariants + caveats are pinned by `tests/test_dac_product_readiness.py`. The full ESPHome `--compile` pass remains **owed** (only the compile-only metadata lane is green). `WEBFLASH-DAC-001`, `RELEASE-DAC-001`, and `WF-IMPORT-DAC-001` remain **blocked**. Recommended next DAC chain PR: `FW-COMPILE-DAC-FULL-001` (record the owed manual `workflow_dispatch compile_mode=full` ESPHome compile before WebFlash planning) or `WEBFLASH-DAC-001-READINESS-REFRESH` (docs-only WebFlash-gate re-evaluation). `S360-100-BENCH-001`, `HW-PINMAP-312-FOLLOWUP`, and `COMPLIANCE-001` are **not** closed by this PR. |
| FW-COMPILE-RELAY-FULL-FIX-001 | #578 | esphome-public | Merged — package fix for FanRelay full-compile `GPIO3` double-bind | Fixed the FanRelay `GPIO3` double-bind that failed full-compile run `26334334727` on the `Ceiling-POE-VentIQ-FanRelay-RoomIQ` target. Root cause: the Core abstract package `packages/hardware/sense360_core_ceiling.yaml` already binds `main_relay` `switch.gpio` on `${relay_pin}` (`GPIO3` post-001A) and `packages/expansions/fan_relay.yaml` declared a second `switch.gpio` (`id: fan_relay_switch`) on `${fan_relay_pin}` (default `${relay_pin}`), so composing both bound `GPIO3` twice. Shape-C fix: `fan_relay_switch` became a `switch.template` proxying the Core `main_relay` (no second `gpio`, names no GPIO, `fan_relay_pin` retired, `relay_pin` unchanged at `GPIO3`); invariants pinned by the updated `tests/test_fan_relay_package.py`. Updated `packages/expansions/fan_relay.yaml`, `products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml` (comments only), `tests/test_fan_relay_package.py`, `docs/compile-only-firmware-validation.md`, `docs/product-readiness-matrix.md`, `docs/hardware/s360-310-r4-relay.md`, `UPCOMING_PR.md`. | No `products/webflash/**`, `config/**`, `firmware/**`, `manifest.json`, `firmware/sources.json`, `.github/workflows/**`, `components/**`, `include/**`, release-artifact, checksum, or WebFlash-repo edit; no `webflash_build_matrix` flip; no `artifact_name`; no `webflash_wrapper`; no `schematic_status` / `schematic_file` promotion (`S360-310` stays `cataloged_unverified`); no COMPLIANCE-001 movement; FanDAC untouched; `relay_pin` not changed. **Full compile success was not claimed by #578** — ESPHome was not run in the authoring environment; a manual `workflow_dispatch` `compile_mode=full` rerun remained owed. | The owed full-compile rerun is recorded by `FW-COMPILE-RELAY-FULL-RESULT-001` (this PR). `WEBFLASH-RELAY-001`, `RELEASE-RELAY-001`, and `WF-IMPORT-RELAY-001` stay blocked. |
| FW-COMPILE-RELAY-FULL-RESULT-001 | (this PR) | esphome-public | Merged — docs-only record of successful FanRelay full-compile result after #578 | Recorded the **successful manual full-compile run** owed by `FW-COMPILE-RELAY-FULL-FIX-001` / PR #578. A `workflow_dispatch` run of the `Compile-only Firmware Validation` lane with `compile_mode=full` ran against post-#578 `main` (merge commit `4906a22`) and **passed** — Run ID `26364679370`, event `workflow_dispatch`, mode `compile_mode=full`, status `completed`, conclusion `success`, **9** compile-only targets; job `Compile-only Targets — Metadata Validation` (`77606314361`, `success`) → `Compile-only Targets — Full ESPHome Compile` (`77606324332`, `success`; the "Run compile-only validator (full compile)" step completed successfully). **The previously failed full-compile run `26334334727` is superseded by this successful run `26364679370`** — the FanRelay target now full-compiles green with the PR #578 shape-C single-owner fix. Updated `docs/compile-only-firmware-validation.md` (new `### 2026-05-24 — FW-COMPILE-RELAY-FULL-RESULT-001` audit-log entry + forward-update note on the FW-COMPILE-RELAY-FULL-FIX-001 entry), `docs/product-readiness-matrix.md` (new 2026-05-24 FanRelay readiness bullet), `docs/webflash-exposure-readiness-matrix.md` (§Relay / S360-310 WebFlash posture note), `docs/release-artifact-readiness-matrix.md` (§Relay / S360-310 release posture note), `docs/hardware/s360-310-r4-relay.md` (new audit-log row), and this `UPCOMING_PR.md`. Validation: `python3 tests/validate_configs.py`; `python3 scripts/validate_compile_targets.py --metadata-only`; `python3 tests/test_fan_relay_package.py`; `python3 tests/test_relay_product_readiness.py`; `python3 tests/test_compile_targets.py`; `python3 tests/validate_webflash_builds.py`; `python3 -m unittest discover -s tests -p "test_*.py"`. | **Docs-only.** No `packages/**`, `products/**`, `products/webflash/**`, `config/**`, `scripts/**`, `.github/workflows/**`, `components/**`, `include/**`, `tests/**`, `firmware/**`, `manifest.json`, `firmware/sources.json`, release-artifact, checksum, build-info, or WebFlash-repo edit; no `webflash_build_matrix` flip; no `artifact_name`; no `webflash_wrapper`; no `config_string` / `release_one_required_configs` change; no `schematic_status` / `schematic_file` promotion (`S360-310` stays `cataloged_unverified`); no COMPLIANCE-001 movement; FanDAC untouched; the compile-only target count stays 9. Release-One stays `Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`; LED preview stays `Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`; FanTRIAC stays `blocked` / `HW-005`; FanRelay stays `hardware-pending`. **No claim of WebFlash exposure / import / release readiness, compliance approval, board-level mains-safety certification, installation-approval, competent-person sign-off, production-wide / multi-unit hardware characterisation, or hardware-stable readiness.** | The FanRelay full-compile lane is now green (necessary-but-insufficient for shipment readiness). `WEBFLASH-RELAY-001`, `RELEASE-RELAY-001`, and `WF-IMPORT-RELAY-001` stay **blocked**; `S360-100-BENCH-001`, `HW-PINMAP-310-FOLLOWUP`, and `COMPLIANCE-001` are **not** closed by this PR. |
| FW-COMPILE-DAC-FULL-RESULT-001 | (this PR) | esphome-public | Merged — docs-only record of FanDAC full-compile result in run 26364679370 | Recorded that the **successful manual full-compile run `26364679370`** — the same `workflow_dispatch` `compile_mode=full` run `FW-COMPILE-RELAY-FULL-RESULT-001` / PR #579 recorded for FanRelay — **also validates the FanDAC compile-only target**. The run ran against post-#578 `main` (merge commit `4906a22`) and **passed** — Run ID `26364679370`, event `workflow_dispatch`, mode `compile_mode=full`, status `completed`, conclusion `success`, **9** compile-only targets; job `Compile-only Targets — Metadata Validation` (`77606314361`, `success`) → `Compile-only Targets — Full ESPHome Compile` (`77606324332`, `success`; the "Run compile-only validator (full compile)" step completed successfully). The `compile_mode=full` lane runs `esphome compile` against **every** [`config/compile-only-targets.json`](config/compile-only-targets.json) target via `scripts/validate_compile_targets.py --compile` and fails on the first failure, so the `success` conclusion proves all nine compiled — including the 9th, `ceiling-poe-fandac-compile-only` → [`products/compile-only/ceiling-poe-fandac.yaml`](products/compile-only/ceiling-poe-fandac.yaml) (`config_string: Ceiling-POE-FanDAC`), present in the manifest at `4906a22` with its YAML on disk. **This supersedes the full-compile concern left owed by `FW-COMPILE-DAC-RESULT-001` / PR #576** (which recorded only the green metadata lane — the full-compile job was `skipped` on PR #575's head), and **the GP8403 `voltage: 10V` enum fix is now compile-validated by ESPHome's own validator**. Updated [`docs/compile-only-firmware-validation.md`](docs/compile-only-firmware-validation.md) (new `### 2026-05-24 — FW-COMPILE-DAC-FULL-RESULT-001` audit-log entry + forward-update note on the FW-COMPILE-DAC-RESULT-001 entry), [`docs/product-readiness-matrix.md`](docs/product-readiness-matrix.md) (§FanDAC / S360-312 audit bullet), [`docs/webflash-exposure-readiness-matrix.md`](docs/webflash-exposure-readiness-matrix.md) (§DAC / S360-312 WebFlash posture note), [`docs/release-artifact-readiness-matrix.md`](docs/release-artifact-readiness-matrix.md) (§DAC / S360-312 release posture note), [`docs/hardware/s360-312-r4-fandac.md`](docs/hardware/s360-312-r4-fandac.md) (new audit-log row), and this `UPCOMING_PR.md`. Validation: `python3 tests/validate_configs.py`; `python3 scripts/validate_compile_targets.py --metadata-only`; `python3 tests/test_fandac_package.py`; `python3 tests/test_dac_product_readiness.py`; `python3 tests/test_compile_targets.py`; `python3 tests/validate_webflash_builds.py`; `python3 -m unittest discover -s tests -p "test_*.py"`. | **Docs-only.** No `packages/**`, `products/**`, `products/webflash/**`, `config/**`, `scripts/**`, `.github/workflows/**`, `components/**`, `include/**`, `tests/**`, `firmware/**`, `manifest.json`, `firmware/sources.json`, release-artifact, checksum, build-info, or WebFlash-repo edit; no `webflash_build_matrix` flip; no `artifact_name`; no `webflash_wrapper`; no `config_string` / `release_one_required_configs` change; no `schematic_status` / `schematic_file` promotion (`S360-312` stays `cataloged_unverified`); no COMPLIANCE-001 movement; the `compile_validation_status: pending-ci` literal config flag is **not** flipped (the docs record that run `26364679370` satisfies it; the config-layer flip is a separate slice); FanDAC / FanRelay code untouched; the compile-only target count stays 9. Release-One stays `Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`; LED preview stays `Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`; FanTRIAC stays `blocked` / `HW-005`; FanRelay stays `hardware-pending`. **No claim of WebFlash exposure / import / release readiness, compliance or safety certification, hardware proof, or simultaneous per-output 0-5V + 0-10V on a single GP8403.** | FanDAC full compile passed in run `26364679370`; the full-compile concern from PR #576 is superseded and the GP8403 enum fix is compile-validated. `PRODUCT-DAC-001` has product YAML (PR #577) but stays no-WebFlash / no-release. `WEBFLASH-DAC-001`, `RELEASE-DAC-001`, and `WF-IMPORT-DAC-001` stay **blocked**; `S360-312 schematic_status: verified`, `HW-PINMAP-312-FOLLOWUP`, and `COMPLIANCE-001` are **not** closed by this PR. Recommended next DAC chain PR: `WEBFLASH-DAC-001-READINESS-REFRESH` (docs-only WebFlash-gate re-evaluation). |
| COMPILE-STATUS-FLAGS-001 | (this PR) | esphome-public | Merged — config/status reconciliation of the FanDAC compile-validation flag after the full compile | Reconciled the stale config-layer flag that `FW-COMPILE-DAC-FULL-RESULT-001` / PR #580 deferred as "a separate config-layer change". In [`config/compile-only-targets.json`](config/compile-only-targets.json) the FanDAC compile-only target `ceiling-poe-fandac-compile-only` has `compile_validation_status` flipped `pending-ci` → **`validated-full-compile`** (the state proven green by run `26364679370` — `workflow_dispatch` / `compile_mode=full`, 9 targets, conclusion `success`, recorded by PR #579 / PR #580), with its `reason` / `notes` wording reconciled accordingly. Updated the two tests that pinned `pending-ci` ([`tests/test_compile_targets.py`](tests/test_compile_targets.py) `test_fandac_compile_success_not_claimed_in_target` → `test_fandac_compile_validated_by_full_compile_run`; [`tests/test_dac_product_readiness.py`](tests/test_dac_product_readiness.py) `test_compile_only_target_compile_validation_pending_ci` → `test_compile_only_target_compile_validation_full_compile`). Reconciled the standing stale-flag wording in [`docs/compile-only-firmware-validation.md`](docs/compile-only-firmware-validation.md), [`docs/product-readiness-matrix.md`](docs/product-readiness-matrix.md), [`docs/webflash-exposure-readiness-matrix.md`](docs/webflash-exposure-readiness-matrix.md), [`docs/release-artifact-readiness-matrix.md`](docs/release-artifact-readiness-matrix.md), [`docs/hardware/s360-312-r4-fandac.md`](docs/hardware/s360-312-r4-fandac.md) (new audit-log row), and this `UPCOMING_PR.md`. Validation: `python3 tests/validate_configs.py`; `python3 scripts/validate_compile_targets.py --metadata-only`; `python3 tests/test_compile_targets.py`; `python3 tests/test_fandac_package.py`; `python3 tests/test_dac_product_readiness.py`; `python3 tests/validate_webflash_builds.py`; `python3 -m unittest discover -s tests -p "test_*.py"`. | **Narrow status reconciliation.** No `packages/**`, `products/**`, `products/webflash/**`, `.github/workflows/**`, `components/**`, `include/**`, `firmware/**`, `manifest.json`, `firmware/sources.json`, release-artifact, checksum, build-info, or WebFlash-repo edit; no `webflash_build_matrix` flip; no `artifact_name`; no `webflash_wrapper`; no `release_one_required_configs` change; no `schematic_status` / `schematic_file` promotion (`S360-310` / `S360-312` stay `cataloged_unverified`); no COMPLIANCE-001 movement; the compile-only target count stays 9; `config/product-catalog.json` and the product YAML are untouched (their full-compile-owed narrative is a separate follow-up); FanRelay carries no `compile_validation_status` field and is unchanged. Release-One stays `Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`; LED preview stays `Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`; FanTRIAC stays `blocked` / `HW-005`; FanRelay stays `hardware-pending`. **No claim of WebFlash exposure / import / release readiness, compliance or safety certification, or hardware proof.** | FanDAC `compile_validation_status` now reads `validated-full-compile`, matching the green full compile from run `26364679370`. `PRODUCT-DAC-001` stays no-WebFlash / no-release; `WEBFLASH-DAC-001`, `RELEASE-DAC-001`, and `WF-IMPORT-DAC-001` stay **blocked**. Follow-up (separate PR): reconcile the residual full-compile-owed narrative in `config/product-catalog.json` and `products/sense360-ceiling-poe-fandac.yaml`. |

## Active / upcoming esphome-public queue

Listed in working priority order. WebFlash-owned import PRs are kept out of
this table; see **Cross-repo dependencies**. The only `WF-`-prefixed entry
that appears below is **WF-TRIAC-001**, which is the in-repo
wrapper/catalog/build slice (not a WebFlash-runtime import).

1. **CORE-ABSTRACT-BUS-001B — Shared-I²C-bus consolidation
   (canonical id `core_i2c`, hard rename only)**
   - Status: **Implemented 2026-05-22 (this PR) —
     `CORE-ABSTRACT-BUS-001B-IMPLEMENT-001` landed the hard rename
     across the seven in-scope Core abstract packages, the 10
     in-scope expansion-package `*_i2c_id` consumer defaults, the
     hard-coded literal in `packages/features/ceiling_halo_leds.yaml`,
     the `tests/generate_test_configs.py` per-product override, and
     the new `SharedI2CBusTests` (13 cases) in
     `tests/test_core_abstract_bus.py`. Static validation passes
     across `tests/validate_configs.py` (202/202),
     `scripts/validate_compile_targets.py --metadata-only` (8/8),
     `tests/test_core_abstract_bus.py` (33/33), and the full
     `python3 -m unittest discover` (515/515). ESPHome unavailable
     in implementation env; `esphome config` generated-config diff
     against Release-One + LED preview deferred to a future
     evidence-capture pass.** Canonical I²C bus id is `core_i2c`,
     migration style is hard rename only, no compatibility aliases.
     Independent of `001A` / `001C` ordering (both completed-merged
     as PR #558 / PR #557); the shared-I²C-bus blocker on
     `PACKAGE-PWM-001` / `PACKAGE-DAC-001` is now lifted — those
     packages remain blocked behind their own per-board evidence
     gates (`HW-PINMAP-311-FOLLOWUP` / `HW-PINMAP-312-FOLLOWUP`)
     and BOM cross-checks.
   - Purpose: Hard-rename every in-scope Core abstract package's
     `halo_i2c` / `expansion_i2c` / `i2c0` / `i2c1` / `i2c_primary`
     / `i2c_expander` bus definitions down to a **single shared
     `core_i2c` bus** on `IO48` (SDA) / `IO45` (SCL) at `400 kHz` —
     the schematic-correct topology per `S360-100-R4`. Rebind every
     downstream `*_i2c_id` substitution default to `core_i2c` and
     rebind the hard-coded `i2c_id: halo_i2c` literal in
     `packages/features/ceiling_halo_leds.yaml` line 6 to
     `i2c_id: core_i2c` (the feature file now has four product
     `!include`rs — `sense360-core-ceiling.yaml`,
     `sense360-core-ceiling-bathroom.yaml`,
     `sense360-core-ceiling-presence.yaml`,
     `sense360-core-voice-ceiling.yaml`).
   - Notes: 2026-05-22 plan record (this PR) is **docs-only**.
     Closes the canonical-id-decision precondition (#1 of four
     enumerated by PR #519) and refreshes the downstream-consumer
     audit (#4). Two preconditions remain open at the
     implementation layer: (#2) extending
     `tests/test_core_abstract_bus.py` with a `SharedI2CBusTests`
     class asserting `core_i2c` in every affected Core package + on
     `GPIO48`/`GPIO45` + `400kHz` + every `*_i2c_id` consumer
     default resolving to `core_i2c` + the `ceiling_halo_leds.yaml`
     literal rebound; (#3) executing the re-validation pass for
     every non-Release-One product YAML consuming any affected Core
     / expansion package (~25 product YAMLs across the seven
     in-scope Core packages). Both land **with** the implementation
     slice, not before. **In-scope Core packages (seven):**
     `sense360_core.yaml`, `sense360_core_ceiling.yaml`,
     `sense360_core_mapping.yaml`, `sense360_core_poe.yaml`,
     `sense360_core_wall.yaml`, `sense360_core_voice_ceiling.yaml`,
     `sense360_core_voice_wall.yaml`. **Out-of-scope Core packages:**
     `sense360_core_ceiling_s3.yaml` (`i2c_primary` on
     `GPIO17`/`GPIO18`, different board layout) and
     `sense360_core_mini.yaml` (`i2c0` already on schematic-correct
     `GPIO48`/`GPIO45`). **In-scope expansion package `*_i2c_id`
     consumer defaults (11):** `airiq.yaml`, `airiq_wall.yaml`,
     `airiq_ceiling.yaml`, `airiq_bathroom_base.yaml`,
     `airiq_bathroom_pro.yaml`, `comfort.yaml`, `comfort_wall.yaml`,
     `comfort_ceiling.yaml`, `fan_gp8403.yaml`,
     `gpio_expander_sx1509.yaml`, plus the
     `packages/features/ceiling_halo_leds.yaml` hard-coded literal.
     **Out-of-scope expansion / hardware-helper consumers:**
     `airiq_ceiling_s3.yaml` (defaults to `i2c_primary`),
     `comfort_ceiling_s3.yaml` (defaults to `i2c_primary`), and
     `mini_onboard_sensors.yaml` (`mini_sensors_i2c_id: i2c0` Mini
     baseline). Six Mini product YAMLs
     (`sense360-mini-airiq-advanced.yaml`,
     `sense360-mini-airiq-basic.yaml`,
     `sense360-mini-full-ld2412.yaml`,
     `sense360-mini-presence-advanced.yaml`,
     `sense360-mini-presence-advanced-ld2412.yaml`,
     `sense360-mini-presence-basic.yaml`) define their own inline
     `i2c0` block on `GPIO48`/`GPIO45` and stay byte-identical.
     **Rationale** for choosing `core_i2c` over `shared_i2c` /
     `i2c0`: self-describing; not currently used anywhere in the
     repo (no collision with existing substitution defaults); does
     not silently re-bind the Mini family. Hard-rename-only keeps
     the substitution graph single-rooted and avoids alias
     maintenance debt. Plan recorded in
     `docs/hardware/core-abstract-bus-reconciliation.md`
     §`### 2026-05-22 — CORE-ABSTRACT-BUS-001B core_i2c plan`
     (decision table, refreshed bus-definition inventory, consumer
     inventory, final desired mapping, implementation scope,
     non-goals, risk notes, test plan). Earlier investigation pass
     log lives at
     `docs/hardware/core-abstract-bus-reconciliation.md`
     §`### 2026-05-19 — CORE-ABSTRACT-BUS-001B investigation pass`
     (PR #519) and `docs/cleanup-audit.md`
     §`CORE-ABSTRACT-BUS-001B update (2026-05-19 — docs-only
     investigation pass)`.

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
    - Status: **Merged (this PR, 2026-05-22) — implementation
      slice landed as product-YAML-only / no-WebFlash-exposure.**
      The canonical FanRelay product YAML
      [`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`](products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml)
      is committed; a non-WebFlash row was added to
      [`config/product-catalog.json`](config/product-catalog.json)
      (`config_string: Ceiling-POE-VentIQ-FanRelay-RoomIQ`,
      `status: hardware-pending`, `webflash_build_matrix: false`,
      no `artifact_name`, no `webflash_wrapper`); the YAML carries
      explicit advanced / manual-warning + installation / safety +
      competent-person caveat wording per the readiness refresh
      posture in
      [`docs/product-readiness-matrix.md` §FanRelay / S360-310](docs/product-readiness-matrix.md#fanrelay--s360-310);
      [`tests/test_relay_product_readiness.py`](tests/test_relay_product_readiness.py)
      (42 stdlib-unittest cases) pins the structural invariants.
      **WebFlash exposure remains blocked**; no WebFlash wrapper,
      no `webflash_build_matrix: true` flip, no build-matrix entry,
      no release artifact, no WebFlash import. The next Relay
      chain PR is `WEBFLASH-RELAY-001-READINESS-REFRESH`
      (docs-only readiness re-evaluation after PRODUCT-RELAY-001
      lands), not immediate `WEBFLASH-RELAY-001` exposure work.
      **Historical context:** previously gated until
      `PACKAGE-RELAY-001` implementation; **the prior readiness
      refresh landed (PR #563, 2026-05-22, docs-only) — confirmed
      gated; recommended posture is `advanced/manual-warning-only` +
      product-YAML-allowed (no WebFlash) + compile-only-allowed;
      implementation PR (this PR) followed and landed the product
      YAML accordingly.** `PACKAGE-RELAY-001` is **implemented at the
      package layer only** (PR #562 / 2026-05-22 — test +
      readiness reconciliation; no YAML rebind; added
      [`tests/test_fan_relay_package.py`](tests/test_fan_relay_package.py)
      pinning the FanRelay package abstraction). The
      `CORE-ABSTRACT-BUS-001A` substitution-layer precondition
      (`relay_pin → GPIO3` across the five non-voice Core
      abstract packages) is **resolved** by PR #558; the
      `GPIO3` collision precondition is **resolved** by
      `CORE-ABSTRACT-BUS-001C` / PR #557; the
      `PACKAGE-RELAY-001-READINESS-REFRESH` PR (PR #559,
      docs-only) consolidated the readiness table; the
      `S360-310-BENCH-001` checklist PR (PR #560) and the
      `S360-310-BENCH-EVIDENCE-001` evidence-population PR
      (PR #561, 2026-05-22) populated the ten hardware-evidence
      rows at the package-evidence layer. **Product-layer
      blockers remain open** (see
      [`docs/product-readiness-matrix.md` §FanRelay / S360-310](docs/product-readiness-matrix.md#fanrelay--s360-310)
      refreshed by this PR): (a) product onboarding per
      [`docs/product-onboarding.md`](docs/product-onboarding.md);
      (b) explicit installation / safety wording on any future
      FanRelay product YAML; (c) explicit competent-person caveat
      (UK Building Regulations Part P-equivalent class;
      analogous to the FanTRIAC advanced / manual-warning posture
      but at a lower-severity tier because the FanRelay product
      is on/off contact-side rather than phase-dimming); (d)
      production-wide / multi-unit / oscilloscope-traced general
      ESP32-S3 `GPIO3` strap-pin boot-behaviour characterisation
      (the `S360-310-BENCH-EVIDENCE-001` pair-scoped 10-cycle ×
      4-power-path boot evidence is operator-framed as pair-scoped
      sufficient for `PACKAGE-RELAY-001` implementation only —
      explicitly **not** a generic claim about any future relay /
      expansion module attached to `J4`); (e) board-level
      mains-safety / installation-approval / creepage / clearance
      / thermal / EMI evidence (the public-reference `K1` contact
      rating `10 A @ 250 VAC; 10 A @ 30 VDC` is contact-rating
      evidence only, **not** board-level compliance,
      installation approval, creepage / clearance, thermal,
      EMI, or mains-safety certification).
    - Purpose: Add the S360-310 Relay product YAML as a
      **product-YAML-only / no-WebFlash-exposure** slice —
      canonical FanRelay product YAML under
      [`products/`](products/); explicit advanced / manual-warning
      wording; installation / safety caveat; competent-person
      caveat;
      [`docs/product-onboarding.md`](docs/product-onboarding.md)
      safe sequence cleared; optional compile-only target under
      [`config/compile-only-targets.json`](config/compile-only-targets.json).
      **Does not** add a WebFlash wrapper under
      [`products/webflash/`](products/webflash/), **does not**
      flip `webflash_build_matrix: true` on any
      [`config/product-catalog.json`](config/product-catalog.json)
      row, **does not** add a
      [`config/webflash-builds.json`](config/webflash-builds.json)
      build-matrix entry, **does not** add a release artifact /
      tag / checksum / build-info manifest / release-proof row,
      **does not** add `release_one_required_configs` /
      `lifecycle_statuses` / kit / recommended membership.
      WebFlash exposure (if and when ever appropriate) is owned
      by a separate `WEBFLASH-RELAY-001` slice (item #8 below)
      with its own production-wide / installation /
      competent-person gates.
    - Notes: The recommended product posture is recorded in
      [`docs/product-readiness-matrix.md` §FanRelay / S360-310](docs/product-readiness-matrix.md#fanrelay--s360-310)
      as `advanced/manual-warning-only` +
      `product-YAML-allowed (no WebFlash)` +
      `compile-only-allowed`. The matrix's
      [Follow-up PR sequence](docs/product-readiness-matrix.md#follow-up-pr-sequence)
      row for `PRODUCT-RELAY-001` enumerates the gates the
      implementation PR must clear (advanced / manual-warning
      wording; installation / safety caveat; competent-person
      caveat; product-onboarding safe sequence; no WebFlash
      wrapper / catalog flip / build-matrix entry / release
      artifact). If the team prefers more guardrails first, the
      alternative next PR is a specific installation-safety /
      competent-person caveat scaffold PR for FanRelay-bearing
      products before any product YAML lands. The pair-scoped
      boot-OK observation in
      [`docs/hardware/core-abstract-bus-001c-rebind-plan.md`](docs/hardware/core-abstract-bus-001c-rebind-plan.md)
      decisions #16 / #17 and the `S360-310-BENCH-EVIDENCE-001`
      pair-scoped 10-cycle × 4-power-path boot evidence are
      **not** generic `GPIO3` strap-pin boot-behaviour claims and
      do **not** discharge the product-layer mains-safety /
      installation-approval / production-wide characterisation
      gates.

8. **WEBFLASH-RELAY-001** (preceded by **WEBFLASH-RELAY-001-READINESS-REFRESH** / PR #565 / 2026-05-22, docs-only; **FW-COMPILE-RELAY-001** / PR #566 / 2026-05-22 added compile-only validation; **FW-COMPILE-RELAY-RESULT-001** this PR / 2026-05-22 recorded successful CI result)
    - Status: **`WEBFLASH-RELAY-001-READINESS-REFRESH` merged as
      PR #565 (2026-05-22, docs-only); `FW-COMPILE-RELAY-001`
      merged as PR #566 (2026-05-22, compile-only target add);
      `FW-COMPILE-RELAY-RESULT-001` merged this PR (2026-05-22,
      docs-only record of successful CI result for the eight-
      target compile-only lane — GitHub Actions Run ID
      `26298089904`, status `completed`, conclusion `success`,
      with companion Quick Validation Run ID `26298090061` also
      successful); `WEBFLASH-RELAY-001` itself remains blocked**
      on (1) explicit `WEBFLASH-RELAY-001`
      implementation approval; (2) advanced / manual-warning UI
      copy; (3) competent-person / installation warning flow; (4)
      product not default / not recommended; (5) release artifact
      must exist before WebFlash import; (6) no stable / preview
      promotion until explicit approval; (7) production-wide /
      installation / safety / mains-safety / qualified-electrician
      sign-off remaining separate from any WebFlash surface — the
      seven WebFlash gates the readiness refresh recorded under
      [`docs/webflash-exposure-readiness-matrix.md` §Relay / S360-310 WebFlash posture](docs/webflash-exposure-readiness-matrix.md#relay--s360-310-webflash-posture).
      `PRODUCT-RELAY-001` has landed (PR #564) but WebFlash
      exposure remains a separate gate per the readiness refresh
      recommended posture (`advanced/manual-warning-only`, not the
      default `preview-candidate`). Relay-chain status:
      **package done** (PR #562); **product YAML done** (PR
      #564); **compile-only target done** (PR #566);
      **compile-only result passed** (this PR / PR #566 head
      validation passed in GitHub Actions); WebFlash / release /
      import **still blocked**. The recommended next Relay-chain
      PR is one of `WEBFLASH-RELAY-001-SCAFFOLD-001` (if WebFlash
      Relay planning continues) or `CORE-ABSTRACT-BUS-001B` (if
      PWM / DAC blocker removal is prioritised instead); neither
      of those is immediate `WEBFLASH-RELAY-001` wrapper /
      catalog / build-matrix work.
    - Purpose: Add the WebFlash wrapper, compatibility entry, and build
      matrix row for the Relay product on an advanced /
      manual-warning channel behind a manual-warning UX gate.
    - Notes: Pairs with WebFlash-side `WF-IMPORT-RELAY-001`. The
      `CORE-ABSTRACT-BUS-001A` substitution-layer precondition is
      **resolved**; the `GPIO3` collision precondition is
      **resolved**; the `PACKAGE-RELAY-001` evidence layer is
      satisfied (PR #561 / PR #562); `PRODUCT-RELAY-001`
      product YAML has landed (PR #564) under
      [`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`](products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml);
      `WEBFLASH-RELAY-001-READINESS-REFRESH` (this PR, 2026-05-22,
      docs-only) re-evaluated and recorded that WebFlash exposure
      remains blocked, enumerated the seven WebFlash gates, and
      enumerated four possible exposure shapes
      `WEBFLASH-RELAY-001` could take (blocked entirely; advanced /
      manual-warning import only; hidden / manual mode only; or
      compile-only / no-runtime exposure under a future
      `FW-COMPILE-RELAY-001`). Remaining gates are production-wide
      / multi-unit hardware characterisation; installation / safety
      / competent-person sign-off; WebFlash-side manual-warning UX
      parity; the WEBFLASH-RELAY-001 wrapper + catalog +
      build-matrix row itself. User-facing naming policy is
      **outcome-first** — e.g. "Switched fan control" or "Relay
      fan control" — and the cross-repo WebFlash UI already ships
      the outcome-first label "Fan relay control" in Step 4
      (WF-UX-007) and "Sense360 Bathroom Kit — Relay Fan Control"
      in the Stage 1 bundle preset `S360-KIT-BATH-RELAY` (status
      `planned`, non-installable; WF-KIT-PRESETS-001). The
      `PACKAGE-RELAY-001-READINESS-REFRESH` PR (PR #559, docs-only)
      consolidated the readiness table at
      [`docs/hardware/s360-310-r4-relay.md` §PACKAGE-RELAY-001 readiness refresh after CORE-ABSTRACT-BUS-001C / 001A](docs/hardware/s360-310-r4-relay.md#package-relay-001-readiness-refresh-after-core-abstract-bus-001c--001a);
      `S360-310-BENCH-EVIDENCE-001` (PR #561) populated the
      captured-evidence table; `PRODUCT-RELAY-001-READINESS-REFRESH`
      (PR #563) recorded the WebFlash exposure remains-blocked
      posture; `PRODUCT-RELAY-001` (PR #564) landed the product
      YAML without advancing WebFlash exposure;
      `WEBFLASH-RELAY-001-READINESS-REFRESH` (PR #565)
      re-evaluated WebFlash exposure post-PR-#564 and recorded
      that WebFlash Relay exposure remains blocked;
      `FW-COMPILE-RELAY-001` (PR #566) added the FanRelay
      compile-only validation target without changing any
      WebFlash exposure or release-readiness gate;
      `FW-COMPILE-RELAY-RESULT-001` (this PR) records the
      successful GitHub Actions compile-only validation result
      for that target (Run ID `26298089904`, status `completed`,
      conclusion `success`) without advancing any WebFlash
      exposure or release-readiness gate.

9. **RELEASE-RELAY-001**
    - Status: **Blocked** on `WEBFLASH-RELAY-001` and on the
      seven WebFlash gates enumerated by
      `WEBFLASH-RELAY-001-READINESS-REFRESH` (this PR, 2026-05-22,
      docs-only) under
      [`docs/release-artifact-readiness-matrix.md` §Relay / S360-310 release posture](docs/release-artifact-readiness-matrix.md#relay--s360-310-release-posture).
      **No FanRelay release artifact exists**; no
      `Sense360-Ceiling-*-FanRelay-*-v*.*-*.bin` has been built /
      signed / attached / imported; no FanRelay row in
      [`config/webflash-builds.json`](config/webflash-builds.json);
      no GitHub Release for any FanRelay tag; no SHA256 / MD5
      checksum files; no build-info `manifest.json` asset; no
      proof row in
      [`docs/webflash-release-proof.md`](docs/webflash-release-proof.md).
    - Purpose: Produce the release artifact + release-proof entries for
      the Relay product (build / sign / attach the `.bin`,
      generate release notes via the existing
      `scripts/generate_webflash_release_notes.py` /
      `scripts/validate-webflash-release-notes.py` flow, emit
      SHA256 + MD5 checksums via the existing release-assets
      validators, attach the build-info `manifest.json`, record the
      release-proof row, and hand off to WebFlash-side import).
    - Notes: The `CORE-ABSTRACT-BUS-001A` substitution-layer
      precondition is **resolved** (PR #558); the `GPIO3` collision
      precondition is **resolved** (PR #557); the
      `PACKAGE-RELAY-001` evidence layer is satisfied (2026-05-22,
      by `S360-310-BENCH-EVIDENCE-001` / PR #561); the package
      layer is implemented (PR #562); the product YAML is landed
      (PR #564); the compile-only target is added (PR #566) and
      its compile-only CI result passed (this PR, Run ID
      `26298089904`); `WEBFLASH-RELAY-001-READINESS-REFRESH`
      (PR #565, docs-only) recorded that `RELEASE-RELAY-001`
      remains blocked until at minimum the seven WebFlash gates
      clear and a Relay artifact path exists. Remaining gates
      inherit from `WEBFLASH-RELAY-001` implementation + product
      / compliance / release-readiness gates. **No
      `RELEASE-RELAY-001` unblock claim is made by
      `WEBFLASH-RELAY-001-READINESS-REFRESH`,
      `FW-COMPILE-RELAY-001`, or
      `FW-COMPILE-RELAY-RESULT-001`.**

10. **PACKAGE-PWM-001**
    - Status: Blocked on HW-PINMAP-311-FOLLOWUP returning sufficient evidence
    - Purpose: Stand up / re-stand up the S360-311 PWM package wiring once
      the pin/package audit is no longer partial.
    - Notes: Also affected by CORE-ABSTRACT-BUS-001B (shared I²C bus
      consolidation — **canonical id `core_i2c` decided 2026-05-22**
      per `CORE-ABSTRACT-BUS-001B-PLAN-001`; **hard rename only**,
      no compatibility aliases by default; YAML rebind still
      pending until the `001B` implementation slice lands; until
      then `PACKAGE-PWM-001` stays blocked behind both the
      `HW-PINMAP-311-FOLLOWUP` evidence and `001B` implementation
      actually landing in YAML) and CORE-ABSTRACT-BUS-001C
      (completed-merged as PR #557 — the generic `expansion_gpio*`
      substitutions were retired and the affected Core packages now
      expose schematic-named function-specific substitutions instead;
      `fan_pwm.yaml`'s `${fan_pwm_pin}` / `${fan_tach_pin}` defaults
      are independent of the 001C rebind and stay as-is until the
      `PACKAGE-PWM-001` slice re-aligns them against bench
      evidence).

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

14. **PACKAGE-DAC-001-IMPLEMENT-001** (was `PACKAGE-DAC-001` before
    the 2026-05-22 readiness refresh split out a docs-only
    `PACKAGE-DAC-001-READINESS-REFRESH` and recommended a DAC
    address / range / silkscreen evidence PR as the next step)
    - Status: **LANDED 2026-05-23 as PR #573 (package layer)** — the
      package YAML reconciliation is complete. The follow-up
      **`FW-COMPILE-DAC-001`** landed as **PR #575** (2026-05-23): it
      fixed the `gp8403:` `voltage:` substitutions from the invalid
      `0-10V` string to ESPHome's valid `10V` enum (Option A) and added
      the `Ceiling-POE-FanDAC` compile-only target. **`FW-COMPILE-DAC-RESULT-001`**
      (this PR, 2026-05-23) records the GitHub Actions result for
      PR #575: the `Compile-only Firmware Validation` workflow (Run ID
      `26332462496`, conclusion `success`, target count 9) passed its
      **metadata-validation lane**; the `Full ESPHome Compile` job was
      **`skipped`** (it runs only via `workflow_dispatch`
      `compile_mode=full`), so the actual `esphome config` / `--compile`
      pass is **still owed** and `compile_validation_status: pending-ci`
      stands. `PRODUCT-DAC-001` is next (gated on the still-owed CI
      compile pass + `S360-312 schematic_status: verified`). Product /
      WebFlash / release readiness remains blocked. The
      2026-05-22 `HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001`
      pass (see
      [`docs/hardware/s360-312-r4-fandac.md` §2026-05-22 — HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001](docs/hardware/s360-312-r4-fandac.md#2026-05-22--hw-pinmap-312-followup-dac-evidence-001))
      closed the rows that PR #571 left blocking: **row 3**
      (DIP-switch ↔ I²C-address truth table — GP8403 datasheet
      `A0` / `A1` / `A2` = bits 0 / 1 / 2, base `0x58`, span
      `0x58`–`0x5F`, + KiCad PCB pole→pin map), **row 6**
      (output-range policy — per-DAC-chip, both default 0–10 V,
      independent override, register `0x01` chip-level mechanism),
      and **row 8** (`J2` / `J3` silkscreen pin-1 identity — both
      connectors pin 1 = `VOUT0` / pin 2 = `GND` / pin 3 = `VOUT1`,
      with the **`J3` `out0` / `out1` silk transposition** flagged).
      Of the 10 FanDAC-specific blockers, rows 1 / 2 are resolved
      (PR #569 / #570), rows 3 / 4 / 6 / 8 are now closed, rows 5 / 7
      are evidence-captured constraints, row 9 is deferred out of
      scope, and **row 10** (the package YAML edit itself) is now
      **DONE** (this PR, 2026-05-23).
    - Purpose: Reconcile
      [`packages/expansions/fan_gp8403.yaml`](packages/expansions/fan_gp8403.yaml)
      against the now-verified schematic + BOM + datasheet + layout
      evidence, applying the operator design decisions: bind **two**
      GP8403 devices (`IC1` / `IC2`) with per-chip
      `${fan_dac_address}` (default `0x58`) /
      `${fan_dac_address_2}` (default `0x59`) — set against the
      DIP-switch ↔ I²C-address truth table (row 3); expose **four**
      outputs (two per chip — row 4); expose **per-chip** range
      substitutions `${fan_dac_voltage_mode}` /
      `${fan_dac_voltage_mode_2}` (both default `10V`, overridable
      independently — row 6), without claiming per-output 0–5 V /
      0–10 V mixing on a single GP8403; correct the stale
      `"(jumper selectable on hardware)"` comment at file line 6 to
      "firmware/register-driven (register `0x01`, per chip)" (row 5);
      and keep the
      [`packages/expansions/fan_dac.yaml`](packages/expansions/fan_dac.yaml)
      alias as a canonical pure-wrapper of `fan_gp8403.yaml`
      unless a separate `PACKAGE-DAC-SPLIT-001` slice argues
      otherwise. The `J2` / `J3` connector pin-1 identity
      (`VOUT0` / `GND` / `VOUT1`) is recorded in the evidence
      section (row 8); the harness conductor trace to the physical
      Cloudlift S12 fan stays a `PRODUCT-DAC-001` / installation-doc
      item. The active package YAML is already dual-channel and
      matches the schematic for `IC1`.
    - Notes: The evidence gate
      (`HW-PINMAP-312-FOLLOWUP-DAC-EVIDENCE-001`) **landed
      2026-05-22** (PR #572), closing rows 3 / 6 / 8 via the GP8403
      datasheet + the `Fan_GP8403` Google Drive layout assets (KiCad
      PCB source, gerbers, board renders) + the operator design
      decisions. **As-built shape (this PR, 2026-05-23):** two
      `gp8403:` devices — `fan_dac_1` (IC1) at
      `${fan_dac_1_i2c_address}` (default `0x58`) and `fan_dac_2`
      (IC2) at `${fan_dac_2_i2c_address}` (default `0x59`), both on
      `${fan_dac_i2c_id}` (`core_i2c`); **per-chip** neutral
      output-range substitutions `${fan_dac_1_output_range}` /
      `${fan_dac_2_output_range}` (both default `0-10V`, overridable
      independently); **four** neutral outputs `fan_dac_1_vout0` /
      `fan_dac_1_vout1` / `fan_dac_2_vout0` / `fan_dac_2_vout1`; the
      stale line-6 "(jumper selectable on hardware)" comment corrected
      to firmware/register-driven (register `0x01`, per chip); and the
      product-layer `fan:` / `sensor:` / `globals:` / `script:` blocks
      removed (they move to `PRODUCT-DAC-001`). The package does
      **not** claim per-output 0–5 V / 0–10 V mixing on a single
      GP8403. The following remain **product /
      bench** follow-ups and do **not** block this slice: the `J2` /
      `J3` → Cloudlift
      S12 fan harness conductor trace (needs the physical fan /
      harness; `PRODUCT-DAC-001` / installation docs); operator /
      bench confirmation of the **`J3` `out0` / `out1` silkscreen
      transposition**; the as-shipped factory DIP positions; and the
      Core `J7` pin-1 `+5V` vs Module `J1` pin-1 `+3.3V` voltage-rail
      discrepancy (parallel `S360-100-BENCH-001` track).
      `PACKAGE-DAC-001-IMPLEMENT-001` is also gated on `S360-312`
      `schematic_status` promotion (separate JSON PR). The
      shared-I²C-bus blocker is closed at the substitution layer:
      `${fan_dac_i2c_id}` already defaults to `core_i2c` at
      [`packages/expansions/fan_gp8403.yaml`](packages/expansions/fan_gp8403.yaml)
      line 27 after `CORE-ABSTRACT-BUS-001B-IMPLEMENT-001`
      (PR #569).

15. **PRODUCT-DAC-001** — **LANDED (this PR; product-YAML-only /
    no-WebFlash-exposure)** (preceded by
    **PRODUCT-DAC-001-READINESS-REFRESH** / PR #574,
    **FW-COMPILE-DAC-001** / PR #575, and **FW-COMPILE-DAC-RESULT-001** /
    PR #576)
    - Status: **Landed at the product layer.** Added the canonical FanDAC
      product YAML
      [`products/sense360-ceiling-poe-fandac.yaml`](products/sense360-ceiling-poe-fandac.yaml)
      (config string `Ceiling-POE-FanDAC`) + a `hardware-pending`
      [`config/product-catalog.json`](config/product-catalog.json) row
      (`webflash_build_matrix: false`, no `artifact_name`, no
      `webflash_wrapper`). It composes Core ceiling + PoE PSU +
      base/health with the canonical FanDAC alias
      [`packages/expansions/fan_dac.yaml`](packages/expansions/fan_dac.yaml).
      **The full ESPHome `--compile` pass is still OWED** — only the
      compile-only **metadata** lane is green
      (FW-COMPILE-DAC-RESULT-001 / PR #576, Run ID `26332462496`); the
      `Full ESPHome Compile` job runs only via `workflow_dispatch`
      `compile_mode=full` and `compile_validation_status: pending-ci`
      stands. The `gp8403:` `voltage:` enum concern was resolved by
      `FW-COMPILE-DAC-001` (`0-10V` → `10V`); `PACKAGE-DAC-001` landed at
      the package layer as **PR #573**. `S360-312 schematic_status` stays
      `cataloged_unverified` (separate JSON PR). New
      [`tests/test_dac_product_readiness.py`](tests/test_dac_product_readiness.py)
      (44 cases) pins the non-WebFlash invariants + caveats; superseded
      pre-PRODUCT-DAC-001 guards in `tests/test_compile_targets.py` and
      `tests/test_fandac_package.py` updated.
    - Purpose: Added the S360-312 DAC product YAML with outcome-first
      user-facing naming ("0-10V fan control" / "Cloudlift S12 fan
      control") while keeping the package's neutral output IDs; carried
      the full-compile-owed caveat, the `J2` / `J3` Cloudlift S12
      harness-trace / product-bench caveat, the `J3` `out0` / `out1`
      silkscreen-transposition caveat into the product / installation
      docs; treated Nextion / `J7` as out of scope (no `uart:` /
      `display:` bound); enforced the `fandac_conflicts_with_airiq` mutex
      (no AirIQ-bearing FanDAC product). **Does NOT** add a WebFlash
      wrapper, `webflash_build_matrix` flip, `config/webflash-builds.json`
      row, `artifact_name`, or release artifact;
      **`WEBFLASH-DAC-001` / `RELEASE-DAC-001` / `WF-IMPORT-DAC-001`
      remain blocked**.
    - Next recommended PR: **`FW-COMPILE-DAC-FULL-001`** (record the owed
      manual `workflow_dispatch` `compile_mode=full` ESPHome compile
      before WebFlash planning) **or**
      **`WEBFLASH-DAC-001-READINESS-REFRESH`** (re-evaluate the WebFlash
      gate).

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

- **WF-IMPORT-RELAY-001** — WebFlash-side import of the Relay
  product. Tracked in the WebFlash repo's `UPCOMING_PR.md` as queue
  item 4, currently **blocked** behind upstream
  `RELEASE-RELAY-001`. Cross-confirmed read-only by
  `WEBFLASH-RELAY-001-READINESS-REFRESH` (this PR, 2026-05-22,
  docs-only): WebFlash repo has no FanRelay source in
  `firmware/sources.json`, no FanRelay build in `manifest.json`,
  Relay (S360-310) stays at `design-pending` in
  `scripts/utils/module-availability.js`, Stage 1 preset
  `S360-KIT-BATH-RELAY` in `scripts/data/kit-presets.js` stays
  `status: planned` / `firmwareConfigString: null`, and the
  WebFlash UI ships outcome-first naming "Fan relay control" in
  Step 4 (WF-UX-007) and "Sense360 Bathroom Kit — Relay Fan
  Control" in the Stage 1 bundle preset (WF-KIT-PRESETS-001) ahead
  of any future import.
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

- **2026-05-22 — `WEBFLASH-RELAY-001-READINESS-REFRESH` defined the
  Relay WebFlash-layer disposition after `PRODUCT-RELAY-001` /
  PR #564 landed the FanRelay product YAML without WebFlash
  exposure (docs-only).** Re-evaluated the FanRelay WebFlash-layer
  disposition after the product-YAML landing. Refreshed
  [`docs/webflash-exposure-readiness-matrix.md` §Relay / S360-310 WebFlash posture](docs/webflash-exposure-readiness-matrix.md#relay--s360-310-webflash-posture)
  to record WebFlash Relay exposure remains **blocked** despite
  the product YAML landing; enumerated the seven WebFlash gates
  that a future `WEBFLASH-RELAY-001` slice must clear (explicit
  `WEBFLASH-RELAY-001` implementation approval; advanced /
  manual-warning UI copy; competent-person / installation warning
  flow; product not default / not recommended; release artifact
  must exist before WebFlash import; no stable / preview promotion
  until explicit approval; production-wide / installation / safety
  caveats remain separate from any WebFlash surface); enumerated
  the four possible exposure shapes a future `WEBFLASH-RELAY-001`
  could take (blocked entirely; advanced / manual-warning import
  only; hidden / manual mode only; or compile-only / no-runtime
  exposure under a future `FW-COMPILE-RELAY-001`). Refreshed
  [`docs/release-artifact-readiness-matrix.md` §Relay / S360-310 release posture](docs/release-artifact-readiness-matrix.md#relay--s360-310-release-posture)
  to record `RELEASE-RELAY-001` remains **blocked**; no FanRelay
  release artifact exists; no release-proof row is added. Refreshed
  [`docs/kit-intent-matrix.md` §S360-KIT-BATH-RELAY](docs/kit-intent-matrix.md#s360-kit-bath-relay--sense360-bathroom-kit--relay-fan-control)
  to record the Relay Bathroom Kit now has a product YAML upstream
  but still has no WebFlash exposure and is not default; the
  default sellable kit remains `S360-KIT-BATH-POE` mapped to
  Release-One. **WebFlash repo re-read read-only** (cross-repo,
  `sense360store/WebFlash`): `firmware/sources.json` has no
  FanRelay source; `manifest.json` carries no FanRelay build;
  `REQUIRED_CONFIGS` stays `["Ceiling-POE-VentIQ-RoomIQ",
  "Rescue"]`; `scripts/data/kits.json` stays Release-One-only;
  `scripts/utils/module-availability.js` keeps Sense360 Relay
  (S360-310) at `design-pending`; the Stage 1 bundle preset
  `S360-KIT-BATH-RELAY` in `scripts/data/kit-presets.js` stays
  `status: planned` (non-installable, `notAvailableReason:
  "Awaiting upstream RELEASE-RELAY-001 firmware import
  (WF-IMPORT-RELAY-001)."`); the WebFlash UPCOMING_PR queue item
  4 (`WF-IMPORT-RELAY-001`) stays **blocked** behind upstream
  `RELEASE-RELAY-001`. **WebFlash UI naming alignment confirmed**:
  the WebFlash repo already ships outcome-first labels — "Fan
  relay control" in Step 4 module cards under WF-UX-007 and
  "Sense360 Bathroom Kit — Relay Fan Control" in the Stage 1
  bundle preset under WF-KIT-PRESETS-001 — matching this readiness
  refresh's user-facing-naming policy. No `packages/**`,
  `products/**`, `products/webflash/**`, `config/**`, `scripts/**`,
  `.github/workflows/**`, `components/**`, `include/**`,
  `firmware/**`, `manifest.json`, `firmware/sources.json`,
  `tests/**`, release-artifact, checksum, build-info manifest, or
  WebFlash-repo edit. No `webflash_build_matrix` flip, no
  `artifact_name`, no `webflash_wrapper`, no
  `release_one_required_configs` change, no `lifecycle_statuses`
  change, no `canonical_modules` / `canonical_power` /
  `forbidden_tokens` change, no `REQUIRED_CONFIGS` / kit JSON
  change, no `schematic_status` / `schematic_file` promotion
  (`S360-310` stays `cataloged_unverified`), no COMPLIANCE-001
  movement. **No claim of FanRelay WebFlash import-readiness,
  release-readiness, compliance-clearance, board-level
  mains-safety certification, installation-approval,
  qualified-electrician sign-off, production-wide / multi-unit
  hardware characterisation, `RELEASE-RELAY-001` unblock,
  `WEBFLASH-RELAY-001` unblock, `WF-IMPORT-RELAY-001` unblock,
  kit-default readiness, recommended-bundle readiness, or
  stable-channel readiness.** The recommended next Relay-chain PR
  is one of `WEBFLASH-RELAY-001` implementation plan / scaffold
  only (if allowed by the project lead), `RELEASE-RELAY-001`
  (blocked until artifact path exists), or `FW-COMPILE-RELAY-001`
  (if compile-only validation should happen first).
- **2026-05-22 — `PRODUCT-RELAY-001-READINESS-REFRESH` defined the
  Relay product-layer disposition after `PACKAGE-RELAY-001` /
  PR #562 implemented the package at the package layer
  (docs-only).** Re-evaluated the FanRelay product-layer
  disposition after the package-layer landing. Refreshed
  [`docs/product-readiness-matrix.md` §FanRelay / S360-310](docs/product-readiness-matrix.md#fanrelay--s360-310)
  to record the post-PR #562 status as `package-implemented-at-package-layer`
  (upstream) + `product-layer-blockers-open` +
  `advanced/manual-warning-only` + `blocked-from-standard-exposure`
  + `not-required-configs` + `not-recommended` + `not-kit-default`
  + `not-webflash-default`. Recorded the recommended product
  posture as **`advanced/manual-warning-only`** +
  **product-YAML-allowed (no WebFlash exposure)** +
  **compile-only validation allowed** + **WebFlash exposure
  blocked**. The standard `preview-candidate` exposure-ladder
  rung is **explicitly rejected** as the default for FanRelay
  because a mains-switching driver without installation / safety
  wording or a competent-person caveat is not appropriate for
  standard preview surfacing. Five product-layer blockers
  enumerated: (1) product onboarding per
  [`docs/product-onboarding.md`](docs/product-onboarding.md); (2)
  explicit installation / safety wording on any future FanRelay
  product YAML (the populated bench evidence in
  `S360-310-BENCH-EVIDENCE-001` records a UK mains Manrose
  `MT100S`-class extractor fan; the on-board `K1` Songle
  `SRD-05VDC-SL-C` carries a public-reference contact rating of
  `10 A @ 250 VAC; 10 A @ 30 VDC`, but no user-facing
  installation / safety wording has been authored or signed off);
  (3) explicit competent-person caveat (UK Building Regulations
  Part P-equivalent class — analogous to the FanTRIAC
  `advanced/manual-warning-only` long-term posture but at a
  lower-severity tier because the FanRelay product is on/off
  contact-side rather than phase-dimming); (4) production-wide /
  multi-unit / oscilloscope-traced general ESP32-S3 `GPIO3`
  strap-pin boot-behaviour characterisation (the
  `S360-310-BENCH-EVIDENCE-001` pair-scoped 10-cycle ×
  4-power-path boot observation is operator-framed as pair-scoped
  sufficient for `PACKAGE-RELAY-001` implementation only —
  explicitly **not** a generic claim about any future relay /
  expansion module attached to `J4`); (5) board-level
  mains-safety / installation-approval / creepage / clearance /
  thermal / EMI evidence (the public-reference `K1` contact rating
  is contact-rating evidence only, **not** board-level compliance
  / installation approval / creepage / clearance / thermal / EMI
  / mains-safety certification). Refreshed
  [`docs/webflash-exposure-readiness-matrix.md` §Relay / S360-310 WebFlash posture](docs/webflash-exposure-readiness-matrix.md#relay--s360-310-webflash-posture)
  to record that **WebFlash Relay exposure remains blocked**
  until `PRODUCT-RELAY-001` explicitly allows it (and even then a
  separate `WEBFLASH-RELAY-001` slice with its own
  production-wide / installation / competent-person gates is
  required); recorded the **user-facing naming policy** as
  outcome-first (e.g. "Relay fan control" or "Switched fan
  control"), not loose board / module naming. Refreshed
  [`docs/release-artifact-readiness-matrix.md` §Relay / S360-310 release posture](docs/release-artifact-readiness-matrix.md#relay--s360-310-release-posture)
  to record that **`RELEASE-RELAY-001` remains blocked**; **no
  release artifact exists**; **no release-proof row is added** by
  this readiness refresh. Refreshed
  [`docs/kit-intent-matrix.md` §S360-KIT-BATH-RELAY](docs/kit-intent-matrix.md#s360-kit-bath-relay--sense360-bathroom-kit--relay-fan-control)
  narrative — added 2026-05-22 status update noting
  `CORE-ABSTRACT-BUS-001C` / `CORE-ABSTRACT-BUS-001A` /
  `PACKAGE-RELAY-001` have landed while `PRODUCT-RELAY-001` /
  `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001` remain open;
  recorded that the blocker token list above mirrors
  [`config/kit-intent-matrix.json`](config/kit-intent-matrix.json)
  verbatim and a config-edit PR refreshing the list to drop the
  landed blockers is owed separately; restated that the **Relay
  Bathroom Kit remains `future-expansion` / `hardware-pending` /
  `webflash_exposure_allowed_now: false` /
  `stable_ready_now: false`**, the **default sellable kit
  remains `S360-KIT-BATH-POE` mapped to Release-One
  `Ceiling-POE-VentIQ-RoomIQ`**, and **Relay remains a
  fan-control option only when readiness permits**. Refreshed
  `UPCOMING_PR.md` Current queue summary (new bullet for this PR),
  Completed / merged PRs (new row), Active / upcoming queue
  (PRODUCT-RELAY-001 item #7 status refreshed with the
  readiness-refresh outcome, the recommended posture, and the
  recommended next PR as `PRODUCT-RELAY-001` implementation as a
  product-YAML-only / no-WebFlash-exposure slice — not a WebFlash
  wrapper / catalog flip / build-matrix entry / release
  artifact). **No `packages/**` edit**; **no `products/**` or
  `products/webflash/**` edit**; **no `config/**` edit** (`config/hardware-catalog.json`,
  `config/product-catalog.json`, `config/webflash-builds.json`,
  `config/webflash-compatibility.json`,
  `config/firmware-combination-matrix.json`,
  `config/kit-intent-matrix.json`,
  `config/compile-only-targets.json`,
  `config/compile-only-candidates.json` all byte-identical);
  **no `scripts/**` / `.github/workflows/**` / `components/**` /
  `include/**` / `firmware/**` / `manifest.json` /
  `firmware/sources.json` / `tests/**` edit**
  (`tests/test_fan_relay_package.py` from PR #562 and
  `tests/test_core_abstract_bus.py` from 001A / 001C preserved
  verbatim); **no `webflash_build_matrix` flip**; **no
  `artifact_name` / `webflash_wrapper` / `config_string` /
  `release_one_required_configs` / `lifecycle_statuses` /
  `canonical_modules` / `canonical_power` / `forbidden_tokens` /
  `REQUIRED_CONFIGS` / kit JSON change**; **no `schematic_status`
  / `schematic_file` promotion** (`S360-310` stays
  `cataloged_unverified`); **no COMPLIANCE-001 movement**; no
  Release-One change (`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` /
  `stable`); no LED preview change
  (`Ceiling-POE-VentIQ-RoomIQ-LED` / `preview`); no FanTRIAC
  change (`blocked` / `HW-005`). **No production-wide /
  multi-unit / oscilloscope-traced general `GPIO3` strap-pin
  boot-behaviour characterisation claim.** **No board-level
  mains-safety / installation-approval / creepage / clearance /
  thermal / EMI certification claim.** **No WebFlash
  import-readiness claim.** **No hardware release-readiness
  claim.** **No `RELEASE-RELAY-001` unblock claim.** **No claim
  that `PRODUCT-RELAY-001` is product-ready, WebFlash-ready,
  release-ready, compliance-cleared, safe for arbitrary mains
  installation, or verified across production batches.** **No
  `PACKAGE-RELAY-001` re-implementation** (PR #562 stays as the
  package-layer landing point); no Relay product YAML; no
  WebFlash wrapper; no compile-only target for FanRelay; no
  release artifact / tag / checksum / build-info manifest. The
  recommended next active-queue item is `PRODUCT-RELAY-001`
  implementation as a product-YAML-only / no-WebFlash-exposure
  slice; if the team prefers more guardrails first, the
  alternative is a specific installation-safety /
  competent-person caveat scaffold PR before any product YAML
  lands.

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

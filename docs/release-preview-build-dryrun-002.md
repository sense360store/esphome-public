# Preview Release Build / Release Dry-Run — Re-Run (RELEASE-PREVIEW-BUILD-DRYRUN-002)

**Canonical id:** `RELEASE-PREVIEW-BUILD-DRYRUN-002`
**Date:** 2026-06-02
**Supersedes (as the current snapshot):** [`docs/release-preview-build-dryrun.md`](release-preview-build-dryrun.md) (`RELEASE-PREVIEW-BUILD-DRYRUN-001`), retained unchanged as the first-run record.
**Type:** Dry-run **report** doc only. This document re-runs the preview /
manual-preview / advanced-manual-preview release-target dry-run **after**
`RELEASE-PREVIEW-BUILD-FIXES-001` (#691, added the missing preview product YAMLs)
and `REPO-STRUCTURE-AUDIT-001` (#692, confirmed `components/`, `products/`, and
`products/bundles/**` active/keep). It **publishes no firmware**, creates **no**
GitHub Release / tag / checksum, commits **no** `.bin`, adds **no**
`config/webflash-builds.json` row, touches **no** WebFlash repo, writes **no**
`firmware/sources.json` / `manifest.json`, promotes **nothing** to stable, marks
**no** TRIAC recommended/default/stable, removes **neither** `components/` **nor**
`products/`, and claims **no** hardware / compliance / build proof.

Inputs inspected (read-only):
[`docs/release-preview-build-dryrun.md`](release-preview-build-dryrun.md),
[`docs/repo-structure.md`](repo-structure.md),
[`UPCOMING_PR.md`](../UPCOMING_PR.md),
[`config/preview-release-targets.json`](../config/preview-release-targets.json),
[`config/compile-only-targets.json`](../config/compile-only-targets.json),
[`config/product-catalog.json`](../config/product-catalog.json),
[`config/webflash-builds.json`](../config/webflash-builds.json),
[`config/release-channel-policy.json`](../config/release-channel-policy.json),
[`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json),
[`products/bundles/**`](../products/bundles),
[`products/webflash/**`](../products/webflash),
[`products/compile-only/**`](../products/compile-only),
[`products/sense360-*.yaml`](../products),
[`packages/**`](../packages),
[`scripts/validate_preview_release_targets.py`](../scripts/validate_preview_release_targets.py),
[`scripts/validate_compile_targets.py`](../scripts/validate_compile_targets.py).

---

## TL;DR

* **Metadata / config validation re-run: PASS.** All six required validation
  commands pass with exit code `0` (see [§Validation results](#validation-results)).
  Suite is now **217 files / 18 compile-only targets / 9 preview targets /
  1245 tests, 0 failures** (the `+4` files and `+2` compile-only targets vs
  `RELEASE-PREVIEW-BUILD-DRYRUN-001` are the #691 product YAMLs and their
  product-level compile-only registrations).
* **ESPHome compile dry-run: NOT ATTEMPTED — `esphome` CLI unavailable.** No
  `esphome` binary and no `esphome` Python module exist in this environment, so
  **no fresh compile/build pass was run and none is claimed or faked.** This is a
  **metadata-only** re-run.
* **The three previously `blocked-by-missing-yaml` targets are no longer blocked
  by missing YAML.** Their manifest `yaml_path`s now resolve to concrete product
  shims that `!include` real bundles composed only from existing packages, and
  `validate_configs.py` parses every one of those YAMLs (217/0). The
  missing-YAML blocker is **cleared** for all three.
* **They each have a recorded NEW blocker → reclassified `blocked-by-build`:** no
  recorded ESPHome compile (their product-level compile-only targets are
  `compile_validation_status: pending-ci`, and no CLI was available to produce a
  fresh one) **and** no `products/webflash` wrapper YAML yet, so no
  `config/webflash-builds.json` preview row can be cut. (This is the
  "buildable-but-unproven / wrapper-owed" flavour of `blocked-by-build`, distinct
  from FanTRIAC's HW-005 buildability **defect** — see [§3](#3-the-three-previously-missing-yaml-targets-detailed-ledger).)

### Outcome counts — `RELEASE-PREVIEW-BUILD-DRYRUN-001` → `-002`

| Classification | DRYRUN-001 | **DRYRUN-002** | Δ | Targets (DRYRUN-002) |
|---|---|---|---|---|
| `stable-only-existing` | 1 | **1** | — | `Ceiling-POE-VentIQ-RoomIQ` |
| `ready-for-preview-build` | 1 | **1** | — | `Ceiling-POE-VentIQ-RoomIQ-LED` (published preview) |
| `ready-for-manual-preview-build` | 3 | **3** | — | `Ceiling-POE-VentIQ-FanRelay-RoomIQ`, `Ceiling-POE-FanPWM`, `Ceiling-POE-FanDAC` |
| `blocked-by-missing-yaml` | 3 | **0** | **−3** ✅ | — (all three resolved) |
| `blocked-by-build` | 1 | **4** | **+3** | `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` (HW-005, defect) **+** `Ceiling-POE-AirIQ-RoomIQ`, `Ceiling-POE-RoomIQ`, `Ceiling-POE-RoomIQ-LED` (compile-unproven / wrapper-owed) |
| `blocked-by-policy` | 0 | **0** | — | — |
| **Total** | **9** | **9** | | |

> **Headline improvement:** `blocked-by-missing-yaml` went **3 → 0**. The three
> moved into `blocked-by-build` because a buildable composition now exists for
> each but cannot be cut without a recorded compile (`pending-ci`) and a
> `products/webflash` wrapper. **No new compile proof is claimed** (ESPHome still
> unavailable). The `ready-*` rows are unchanged and still owe a real compile
> before any artifact is cut.

---

## Method & environment

### What this re-run did

1. Re-inspected the policy + target configs, the bundle/shim/wrapper include
   chain, the compile-only registry, the catalog, and the two prior reports
   (`RELEASE-PREVIEW-BUILD-DRYRUN-001`, `REPO-STRUCTURE-AUDIT-001`).
2. Verified the three previously missing YAML target paths now exist and resolve.
3. Re-ran the full metadata / config validation suite and recorded **exact**
   results and exit codes.
4. Re-classified every target in `config/preview-release-targets.json` and, for
   any target with a new blocker, recorded the **exact** new blocker.

### What this re-run could not do — and did not fake

`esphome` is **not installed** in this environment:

```text
$ which esphome               → (not found)
$ python3 -c "import esphome"  → ModuleNotFoundError: No module named 'esphome'
```

Per the honesty requirement, the compile dry-run is recorded as:

* **compile not attempted / ESPHome CLI unavailable;**
* **metadata validation only;**
* **no build proof claimed** — for any target, including the three whose YAML
  blocker cleared. Where a target carries a `compile_validation_status`, that
  value is **cited from `config/compile-only-targets.json`**, not re-proven here.

`python3 tests/validate_configs.py` is a YAML-syntax / structure validator
(`yaml.safe_load` + structure checks); a `0-failed` result means each YAML parses
and the `!include` chain is well-formed — **not** that it ESPHome-compiles.

---

## Verification of the missing-YAML fixes (`RELEASE-PREVIEW-BUILD-FIXES-001`)

### 1. The three previously missing YAML target paths now exist

Each preview manifest `yaml_path` resolves to a real top-level product shim that
`!include`s a canonical bundle, which in turn `!include`s only existing packages.
All paths below were confirmed present on disk, and all are parsed clean by
`validate_configs.py` (217 files, 0 failed).

| Config string | manifest `yaml_path` (exists) | `!include` bundle (exists) | Bundle composes (all packages exist) |
|---|---|---|---|
| `Ceiling-POE-AirIQ-RoomIQ` | `products/sense360-ceiling-poe-airiq-roomiq.yaml` ✅ | `products/bundles/ceiling-poe-airiq-roomiq.yaml` ✅ | `boards/s360-100-core-ceiling` + `boards/s360-410-poe-psu` + `boards/s360-210-airiq` + `features/airiq_basic_profile` + `boards/s360-200-roomiq` + comfort/presence profiles + base/health |
| `Ceiling-POE-RoomIQ` | `products/sense360-ceiling-poe-roomiq.yaml` ✅ | `products/bundles/ceiling-poe-roomiq.yaml` ✅ | `hardware/sense360_core_ceiling` + `hardware/power_poe` + `expansions/comfort_ceiling` + `expansions/presence_ceiling` + comfort/presence profiles + base/health |
| `Ceiling-POE-RoomIQ-LED` | `products/sense360-ceiling-poe-roomiq-led.yaml` ✅ | `products/bundles/ceiling-poe-roomiq-led.yaml` ✅ | `boards/s360-100-core-ceiling` + `boards/s360-410-poe-psu` + **`boards/s360-300-led`** (LED token encoded) + `boards/s360-200-roomiq` + comfort/presence profiles + base/health |

### 2. Preview target manifest paths resolve

`scripts/validate_preview_release_targets.py --metadata-only` enforces
`(REPO_ROOT / yaml_path).is_file()` for every target and **passes** (9/9). It also
requires every **unpublished webflash-lane** target to carry a non-null
`build_blocker` — which is exactly why these three retain a `build_blocker`
string (the wording now records the cleared missing-YAML plus the residual
compile/wrapper blocker).

### 3. Compile-only metadata includes them

Each target now has a **product-level** compile-only registration in
`config/compile-only-targets.json` (in addition to the pre-existing
`products/compile-only/*` skeletons):

| Compile-only id | `product_yaml` | `compile_validation_status` |
|---|---|---|
| `ceiling-poe-airiq-roomiq-product-compile-only` | `products/sense360-ceiling-poe-airiq-roomiq.yaml` | `pending-ci` |
| `ceiling-poe-roomiq-product-compile-only` | `products/sense360-ceiling-poe-roomiq.yaml` | `pending-ci` |
| `ceiling-poe-roomiq-led-product-compile-only` | `products/sense360-ceiling-poe-roomiq-led.yaml` | `pending-ci` |

`pending-ci` is honest: **no full ESPHome compile has been recorded** for any of
the three, and none was produced here.

### 4. No stable / product status was promoted

`config/product-catalog.json` entries for all three remain **`status: blocked`**,
`webflash_build_matrix: false`, `blocker: PRODUCT-POE-410-001`
(AirIQ-RoomIQ + RoomIQ `target_channel: stable-candidate`; RoomIQ-LED
`target_channel: preview-candidate`). `config/webflash-builds.json` still has
exactly **2** rows (`Ceiling-POE-VentIQ-RoomIQ` stable, `Ceiling-POE-VentIQ-RoomIQ-LED`
preview) — the three targets are **absent**, as required for an unpublished
preview target. Nothing was promoted by this dry-run.

### 5. `components/` and `products/` directories remain intact

Per `REPO-STRUCTURE-AUDIT-001` (#692) both are **active / KEEP**. Confirmed
present and unmodified: `components/{ld2412,ld2450,ld24xx}` and
`products/{bundles,compile-only,webflash}/` + the 18 top-level `sense360-*.yaml`
shims. **This report removes nothing.**

---

## Validation results

All six commands required by the task were run from the repo root. Exact result
lines and exit codes:

| # | Command | Result | Exit |
|---|---|---|---|
| 1 | `python3 tests/validate_configs.py` | `Validation Summary: 217 files checked, 0 failed` → `✅ All configuration files are valid!` | `0` |
| 2 | `python3 scripts/validate_compile_targets.py --metadata-only` | `Read 18 compile-only target(s)` → `✅ Metadata validation passed.` | `0` |
| 3 | `python3 scripts/validate_preview_release_targets.py --metadata-only` | `Read 9 target(s)` → `✅ Preview release-target manifest validation passed.` | `0` |
| 4 | `python3 tests/test_product_catalog.py` | `Ran 41 tests` → `OK` | `0` |
| 5 | `python3 tests/validate_webflash_builds.py` | `WebFlash Build Matrix: 2 build(s) checked, 0 failed` → `✅ All WebFlash build entries are valid!` | `0` |
| 6 | `python3 -m unittest discover -s tests -p "test_*.py"` | `Ran 1245 tests in 2.910s` → `OK (skipped=3)` | `0` |

**Metadata / config validation: PASS (6/6, exit 0).** None of the six invokes
`esphome compile`; no build proof is produced by any of them.

---

## Per-target reclassification

**Lane** uses the task vocabulary; the manifest stores the stable baseline and
the SELV previews both under `delivery_lane: webflash`, split here by tier. For
all 9 targets: **metadata validation = PASS** and **compile attempted = NO /
ESPHome CLI unavailable**.

| # | Config string | Lane | Tier | DRYRUN-001 class | **DRYRUN-002 class** | Change |
|---|---|---|---|---|---|---|
| 1 | `Ceiling-POE-VentIQ-RoomIQ` | stable | stable | `stable-only-existing` | `stable-only-existing` | — |
| 2 | `Ceiling-POE-VentIQ-RoomIQ-LED` | webflash-preview | preview | `ready-for-preview-build` | `ready-for-preview-build` | — |
| 3 | `Ceiling-POE-AirIQ-RoomIQ` | webflash-preview | preview | `blocked-by-missing-yaml` | **`blocked-by-build`** | **YAML cleared; new blocker** |
| 4 | `Ceiling-POE-RoomIQ` | webflash-preview | preview | `blocked-by-missing-yaml` | **`blocked-by-build`** | **YAML cleared; new blocker** |
| 5 | `Ceiling-POE-RoomIQ-LED` | webflash-preview | preview | `blocked-by-missing-yaml` | **`blocked-by-build`** | **YAML cleared; new blocker** |
| 6 | `Ceiling-POE-VentIQ-FanRelay-RoomIQ` | manual-preview | preview | `ready-for-manual-preview-build` | `ready-for-manual-preview-build` | — |
| 7 | `Ceiling-POE-FanPWM` | manual-preview | preview | `ready-for-manual-preview-build` | `ready-for-manual-preview-build` | — |
| 8 | `Ceiling-POE-FanDAC` | manual-preview | preview | `ready-for-manual-preview-build` | `ready-for-manual-preview-build` | — |
| 9 | `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` | advanced-manual-preview | advanced-preview | `blocked-by-build` | `blocked-by-build` | — (HW-005 unchanged) |

### Why `blocked-by-build` and not still `blocked-by-missing-yaml`, nor `ready-*`

For each of targets 3–5:

* **Not `blocked-by-missing-yaml`** — the manifest `yaml_path` resolves to a real
  shim → bundle → packages composition; the validator's `is_file()` check passes;
  `validate_configs.py` parses all three product YAMLs and their bundles (217/0).
  A compilable artifact now exists.
* **Not `ready-for-preview-build`** — unlike the published LED preview (target 2,
  which has a `webflash-builds.json` row + a `products/webflash` wrapper) and
  unlike the manual-preview fans (targets 6–8, which carry a prior
  `validated-full-compile` and `build_blocker: null`), these three have
  `compile_validation_status: pending-ci` (**no** compile proof, not even prior),
  a **non-null** `build_blocker`, and **no** `products/webflash` wrapper. Calling
  them "ready" would overstate readiness.
* **Therefore `blocked-by-build`** — the gating, decision-relevant blocker is now
  on the build side: a real ESPHome compile must be run/recorded (couldn't here —
  CLI unavailable) and a thin `products/webflash` wrapper authored before a
  `config/webflash-builds.json` preview row can be cut.

> **Honest caveat on the residual missing wrapper.** A `products/webflash`
> wrapper is itself a (small) YAML, so a reader could argue targets 3–5 remain
> partly "missing-YAML (wrapper)". This report files them under `blocked-by-build`
> because (a) the substantive **buildable composition** — the part the original
> missing-YAML blocker was about — now exists and resolves, and (b) the wrapper is
> a publish-lane scaffold that `RELEASE-PREVIEW-BUILD-FIXES-001` explicitly
> deferred **behind** the compile proof, so it is not on the critical path to
> proving buildability. The exact residual (no wrapper + `pending-ci`) is recorded
> verbatim below so the classification can be audited either way.

---

## The three previously-missing-YAML targets — detailed ledger

### 3 — `Ceiling-POE-AirIQ-RoomIQ` (Kitchen / AirIQ preview)

* **Lane / tier:** `webflash-preview` / `preview`
* **YAML / product path:** `products/sense360-ceiling-poe-airiq-roomiq.yaml`
  → `products/bundles/ceiling-poe-airiq-roomiq.yaml` ✅ (resolves)
* **Expected artifact:** `Sense360-Ceiling-POE-AirIQ-RoomIQ-v1.0.0-preview.bin`
* **Metadata validation:** PASS  **Compile attempted:** no — ESPHome CLI unavailable
* **Compile result:** not available; `ceiling-poe-airiq-roomiq-product-compile-only`
  = `compile_validation_status: pending-ci` (**no compile proof recorded**)
* **DRYRUN-001 blocker (missing-YAML):** no catalog entry + no wrapper. **RESOLVED**
  — product YAML + bundle + catalog entry (`status: blocked`, `PRODUCT-POE-410-001`)
  now exist.
* **NEW exact blocker (`blocked-by-build`):** no recorded ESPHome compile
  (`pending-ci`; none produced this run) **and** no `products/webflash/ceiling-poe-airiq-roomiq.yaml`
  wrapper, so no `config/webflash-builds.json` row can be cut yet.
* **Warning copy:** `preview`
* **Stable blocker (unchanged):** S360-410 PoE-PSU schematic verification + AirIQ
  sensor-stack bench evidence.

### 4 — `Ceiling-POE-RoomIQ` (Bedroom / RoomIQ preview)

* **Lane / tier:** `webflash-preview` / `preview`
* **YAML / product path:** `products/sense360-ceiling-poe-roomiq.yaml`
  → `products/bundles/ceiling-poe-roomiq.yaml` ✅ (resolves; manifest repointed
  from the compile-only skeleton to the product YAML by #691)
* **Expected artifact:** `Sense360-Ceiling-POE-RoomIQ-v1.0.0-preview.bin`
* **Metadata validation:** PASS  **Compile attempted:** no — ESPHome CLI unavailable
* **Compile result:** not available; `ceiling-poe-roomiq-product-compile-only`
  = `compile_validation_status: pending-ci` (**no compile proof recorded**)
* **DRYRUN-001 blocker (missing-YAML):** no wrapper. **RESOLVED** for the product
  composition — product YAML + bundle + catalog entry already existed and the
  manifest now points at the product YAML.
* **NEW exact blocker (`blocked-by-build`):** no recorded ESPHome compile
  (`pending-ci`; none produced this run) **and** no `products/webflash/ceiling-poe-roomiq.yaml`
  wrapper, so no `config/webflash-builds.json` row can be cut yet.
* **Warning copy:** `preview`
* **Stable blocker (unchanged):** S360-410 PoE-PSU schematic verification
  (`PRODUCT-POE-410-001` / `PACKAGE-POE-410-001`).

### 5 — `Ceiling-POE-RoomIQ-LED` (Living / Corridor preview)

* **Lane / tier:** `webflash-preview` / `preview`
* **YAML / product path:** `products/sense360-ceiling-poe-roomiq-led.yaml`
  → `products/bundles/ceiling-poe-roomiq-led.yaml` ✅ (resolves; a **dedicated**
  YAML that encodes the LED token via `boards/s360-300-led`, no longer sharing the
  LED-less RoomIQ skeleton)
* **Expected artifact:** `Sense360-Ceiling-POE-RoomIQ-LED-v1.0.0-preview.bin`
* **Metadata validation:** PASS  **Compile attempted:** no — ESPHome CLI unavailable
* **Compile result:** not available; `ceiling-poe-roomiq-led-product-compile-only`
  = `compile_validation_status: pending-ci` (**no compile proof recorded**)
* **DRYRUN-001 blocker (missing-YAML):** no dedicated product/wrapper YAML, no
  catalog entry. **RESOLVED** — dedicated LED-bearing product YAML + bundle +
  catalog entry (`status: blocked`, `target_channel: preview-candidate`) now exist.
* **NEW exact blocker (`blocked-by-build`):** no recorded ESPHome compile
  (`pending-ci`; none produced this run) **and** no `products/webflash/ceiling-poe-roomiq-led.yaml`
  wrapper, so no `config/webflash-builds.json` row can be cut yet. **LED stays
  preview.**
* **Warning copy:** `preview`
* **Stable blocker (unchanged):** S360-410 PoE-PSU schematic verification + LED
  preview-to-stable gauntlet.

### Targets 1, 2, 6–9 — unchanged from `RELEASE-PREVIEW-BUILD-DRYRUN-001`

No facts changed for these six; their full ledgers stand in
[`docs/release-preview-build-dryrun.md`](release-preview-build-dryrun.md) §1–2,
§6–9. In brief:

* **1 `Ceiling-POE-VentIQ-RoomIQ`** — live `v1.0.0` stable; out of scope →
  `stable-only-existing`.
* **2 `Ceiling-POE-VentIQ-RoomIQ-LED`** — already-published preview (webflash row
  + wrapper present) → `ready-for-preview-build`.
* **6 `Ceiling-POE-VentIQ-FanRelay-RoomIQ`**, **7 `Ceiling-POE-FanPWM`**,
  **8 `Ceiling-POE-FanDAC`** — manual-preview lane, `build_blocker: null`, prior
  `validated-full-compile` cited (not re-proven) → `ready-for-manual-preview-build`.
  **A fresh ESPHome compile dry-run is still owed before a `.bin` is cut.**
* **9 `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`** — HW-005 **buildability defect**
  (S360-320 schematic uncommitted; placeholder GPIO5/GPIO6 collide with RoomIQ
  J10 nets; ESPHome `ac_dimmer` cannot run across the SX1509 expander) → not
  buildable end-to-end → `blocked-by-build`. TRIAC stays advanced-preview-only;
  never recommended / default / stable / WebFlash-exposed here.

---

## Outcome classification (DRYRUN-002)

| Classification | Targets |
|---|---|
| `stable-only-existing` | `Ceiling-POE-VentIQ-RoomIQ` — live `v1.0.0` baseline, out of scope. |
| `ready-for-preview-build` | `Ceiling-POE-VentIQ-RoomIQ-LED` — already-published preview. |
| `ready-for-manual-preview-build` | `Ceiling-POE-VentIQ-FanRelay-RoomIQ`, `Ceiling-POE-FanPWM`, `Ceiling-POE-FanDAC` — metadata-clean, no build blocker, manual-preview lane, prior `validated-full-compile`. **A fresh ESPHome compile dry-run is still owed.** |
| `blocked-by-build` | **`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`** (HW-005 buildability **defect**) **+** **`Ceiling-POE-AirIQ-RoomIQ`**, **`Ceiling-POE-RoomIQ`**, **`Ceiling-POE-RoomIQ-LED`** (buildable composition exists but **compile-unproven `pending-ci` + `products/webflash` wrapper owed**). |
| `blocked-by-missing-yaml` | **None** — all three DRYRUN-001 items resolved. ✅ |
| `blocked-by-policy` | **None** — no buildable target is blocked from preview by policy; lack of hardware proof blocks **stable only**. |

### Dry-run verdict

* **Metadata / config dry-run is clean** across all 9 targets (217 files, 18
  compile-only targets, 9 preview targets, 1245 tests; 0 failures).
* The expected improvement landed: **`blocked-by-missing-yaml` 3 → 0**.
* **No compile dry-run was performed** (ESPHome CLI unavailable) → **no build
  proof claimed**; the `ready-*` rows and the three reclassified rows all still
  owe a real compile.
* The three reclassified rows now sit behind a **single shared, concrete next
  step**: a real ESPHome compile + a `products/webflash` wrapper, after which a
  `config/webflash-builds.json` preview row can be cut.

---

## Follow-ups (queued in `UPCOMING_PR.md`)

* **`RELEASE-PREVIEW-COMPILE-DRYRUN-001`** (the real-compile follow-up, ESPHome
  required) — run `scripts/validate_compile_targets.py --compile` (or the
  `compile-only.yml` `workflow_dispatch` / `compile_mode=full` lane) for the
  three reclassified webflash previews **and** the three manual-preview fans;
  record exact pass/fail and flip `pending-ci` → `validated-full-compile` only on
  a real green. **Gating** for any artifact cut.
* **`RELEASE-PREVIEW-WEBFLASH-WRAPPERS-001`** — author the three
  `products/webflash/*.yaml` wrappers (AirIQ-RoomIQ, RoomIQ, RoomIQ-LED) once a
  real compile is recorded; still no `config/webflash-builds.json` row until the
  proof exists.
* **`RELEASE-PREVIEW-PUBLISH-PLAN-001`** (already queued) — plan the publish path
  for the metadata-clean previews; **blocked** until a real ESPHome compile
  records build proof.
* **FanTRIAC `HW-005`** — unchanged buildability defect; remains
  `blocked-by-build`; TRIAC policy untouched.

---

## Guardrails — what this dry-run did NOT do

This re-run / report did **not**, and must not be read as having done, any of:

* publish firmware;
* create a GitHub Release / tag / checksum;
* commit or generate any `.bin`;
* update the WebFlash repo;
* update `firmware/sources.json` or `manifest.json`;
* add or modify any `config/webflash-builds.json` row;
* flip any `config/product-catalog.json` status or `webflash_build_matrix`;
* mark anything stable;
* mark TRIAC recommended / default / stable;
* remove `components/` or `products/`;
* claim hardware / compliance proof;
* fake or claim a fresh compile proof.

It records **dry-run metadata + exact validation results** only. The only files
changed by the PR carrying this report are this document and `UPCOMING_PR.md`.

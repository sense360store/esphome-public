# Preview / Manual-Preview Compile Dry-Run — path + recorded GREEN run

**Canonical ids:** `RELEASE-PREVIEW-COMPILE-DRYRUN-001` (added the hosted lane) →
`RELEASE-PREVIEW-COMPILE-RESULTS-001` (records the green hosted run below).
**Date:** 2026-06-02
**Type:** Records the **successful hosted CI compile dry-run** of the preview /
manual-preview target matrix and flips the three formerly `pending-ci` webflash
previews to `validated-full-compile` (citing the run). It is **firmware-build
proof only**. It still **publishes no firmware**, creates **no** GitHub Release /
tag / checksum, commits **no** `.bin`, adds **no** `config/webflash-builds.json`
row, touches **no** WebFlash repo, writes **no** `firmware/sources.json` /
`manifest.json`, promotes **nothing** to stable, marks **no** TRIAC
recommended/default/stable, leaves **TRIAC excluded** (`HW-005`), and claims
**no** hardware / bench / compliance proof.

**Predecessors:**
[`docs/release-preview-build-dryrun.md`](release-preview-build-dryrun.md)
(`RELEASE-PREVIEW-BUILD-DRYRUN-001`, #690) ran the first metadata-only dry-run;
[`docs/release-preview-build-dryrun-002.md`](release-preview-build-dryrun-002.md)
(`RELEASE-PREVIEW-BUILD-DRYRUN-002`, #693) re-ran it after the missing-YAML fixes
(#691) and the structure audit (#692) and seeded the compile follow-up;
`RELEASE-PREVIEW-COMPILE-DRYRUN-001` (#694) added the scoped hosted compile lane
[`.github/workflows/preview-compile-dryrun.yml`](../.github/workflows/preview-compile-dryrun.yml)
+ the read-only scoping helper
[`scripts/list_preview_compile_targets.py`](../scripts/list_preview_compile_targets.py)
but recorded the compile as **not yet run** (a brand-new `workflow_dispatch`
workflow is not dispatchable until it lands on the default branch). **This update
records the run now that the lane has merged and been dispatched.**

---

## TL;DR

* **The hosted compile dry-run has now been RUN and is GREEN.** The
  `Preview Compile Dry-Run` workflow was dispatched on the default branch with
  `compile_mode=full`
  ([run `26821900127`](https://github.com/sense360store/esphome-public/actions/runs/26821900127),
  2026-06-02, ESPHome 2026.4.5). **All scope, all seven per-target compile, and
  the summary jobs completed successfully (conclusion `success`).**
* **All seven preview / manual-preview targets compiled PASS** — the three
  webflash previews (AirIQ-RoomIQ, RoomIQ, RoomIQ-LED), the three manual-preview
  fans (FanRelay, FanPWM, FanDAC), and the already-published LED preview. The
  **TRIAC target is excluded** (`HW-005` buildability blocker, reported by the
  Scope job, **not** compiled).
* **Metadata recorded (this PR, `RELEASE-PREVIEW-COMPILE-RESULTS-001`):** the
  three webflash previews flip `compile_validation_status` **`pending-ci` →
  `validated-full-compile`** in
  [`config/compile-only-targets.json`](../config/compile-only-targets.json),
  each citing run `26821900127` in a structured `compile_evidence` block; the
  three fans keep `validated-full-compile` and record the same run as **hosted
  corroboration**. **TRIAC is not touched. No stable status is touched.**
* **Logs only.** The run uploaded **only** the per-target compile *log*
  (`retention-days: 7`); **no firmware `.bin`, no checksum, no Release/tag** was
  produced, and **no** `config/webflash-builds.json` / `firmware/sources.json` /
  `manifest.json` was written.
* **A green compile here is firmware-build proof only** — **NOT** hardware proof,
  **NOT** bench evidence, **NOT** a compliance claim, and **NOT** a
  stable-promotion gate.

---

## 1. The hosted compile run (evidence)

| Field | Value |
|---|---|
| Workflow name | **`Preview Compile Dry-Run`** (`.github/workflows/preview-compile-dryrun.yml`) |
| Run id | **`26821900127`** (run #1, attempt 1) |
| Run URL | https://github.com/sense360store/esphome-public/actions/runs/26821900127 |
| Event / input | `workflow_dispatch`, **`compile_mode=full`** |
| Triggered by | `sense360store` |
| Branch / commit | `main` @ `0ff8d6c` (merge of #694) |
| Started → finished | 2026-06-02 13:10:16Z → 13:15:07Z (≈4m51s) |
| Runner / toolchain | `ubuntu-24.04`, Python 3.11.15, **ESPHome 2026.4.5**, `permissions: contents: read` |
| Jobs | **9 / 9 `success`** — 1 Scope + 7 compile + 1 Summary |
| Conclusion | **`success`** |

The Summary job reiterated the proof boundary verbatim: *"This is a DRY-RUN. A
green compile is FIRMWARE-BUILD proof only: NOT hardware proof, NOT bench
evidence, NOT a compliance claim, and NOT a stable-promotion gate. No firmware
was published, no GitHub Release or tag was created, no .bin / checksum was
uploaded, and no config/webflash-builds.json, firmware/sources.json, or
manifest.json was written."* and instructed exactly the metadata flip this PR
records (*"open a separate reviewed metadata PR that flips the cited target's
compile_validation_status pending-ci → validated-full-compile, referencing this
run."*).

---

## 2. Per-target dry-run ledger (PASS / FAIL / excluded)

Scope = the seven preview / manual-preview targets from
[`scripts/list_preview_compile_targets.py`](../scripts/list_preview_compile_targets.py)
(TRIAC excluded; see below). Every in-scope target's `esphome compile` dry-run
step finished with conclusion `success`.

| # | Config string | Lane | Compile job (run `26821900127`) | Compile step | Result |
|---|---|---|---|---|---|
| 1 | `Ceiling-POE-VentIQ-RoomIQ-LED` | webflash (published preview) | `79078546256` | ≈3m09s | ✅ **PASS** |
| 2 | `Ceiling-POE-AirIQ-RoomIQ` | webflash | `79078546308` | ≈3m10s | ✅ **PASS** |
| 3 | `Ceiling-POE-RoomIQ` | webflash | `79078546207` | ≈3m02s | ✅ **PASS** |
| 4 | `Ceiling-POE-RoomIQ-LED` | webflash | `79078546407` | ≈2m51s | ✅ **PASS** |
| 5 | `Ceiling-POE-VentIQ-FanRelay-RoomIQ` | manual-preview | `79078546242` | ≈3m06s | ✅ **PASS** |
| 6 | `Ceiling-POE-FanPWM` | manual-preview | `79078546303` | ≈3m30s | ✅ **PASS** |
| 7 | `Ceiling-POE-FanDAC` | manual-preview | `79078546268` | ≈2m41s | ✅ **PASS** |

> **All seven `PASS`.** "PASS" means the product YAML's `!include` chain resolves
> and ESPHome codegen + the PlatformIO/ESP-IDF toolchain build succeeded for the
> ESP32-S3 target — **firmware-build proof only** (see §4).

### Excluded (reported by the Scope job, not compiled)

| Config string | Lane | Why excluded |
|---|---|---|
| `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` | advanced-manual-preview | **`HW-005` buildability blocker** — S360-320 schematic uncommitted; placeholder GPIO5/GPIO6 collide with RoomIQ J10 nets; ESPHome `ac_dimmer` cannot run across the SX1509 expander. Not buildable end-to-end → **not** added to the compile matrix. TRIAC stays advanced-preview-only; never recommended/default/stable/WebFlash-exposed here. |

The stable baseline `Ceiling-POE-VentIQ-RoomIQ` is **not** a preview target and is
never in the compile-dryrun scope (the helper and
[`tests/test_preview_compile_dryrun.py`](../tests/test_preview_compile_dryrun.py)
enforce this).

---

## 3. Metadata recorded from the green run

Recorded in [`config/compile-only-targets.json`](../config/compile-only-targets.json)
(the authoritative home of `compile_validation_status`); **no** product-catalog
status, **no** WebFlash row, **no** stable status is flipped.

| Target's compile-only row | Before | After | Evidence |
|---|---|---|---|
| `ceiling-poe-airiq-roomiq-product-compile-only` | `pending-ci` | **`validated-full-compile`** | `compile_evidence` → run `26821900127` (primary) |
| `ceiling-poe-roomiq-product-compile-only` | `pending-ci` | **`validated-full-compile`** | `compile_evidence` → run `26821900127` (primary) |
| `ceiling-poe-roomiq-led-product-compile-only` | `pending-ci` | **`validated-full-compile`** | `compile_evidence` → run `26821900127` (primary) |
| `ceiling-poe-ventiq-fanrelay-roomiq-compile-only` | `validated-full-compile` | `validated-full-compile` (unchanged) | `compile_evidence` → run `26821900127` (hosted corroboration) |
| `ceiling-poe-fanpwm-product-compile-only` | `validated-full-compile` | `validated-full-compile` (unchanged) | `compile_evidence` → run `26821900127` (hosted corroboration) |
| `ceiling-poe-fandac-product-compile-only` | `validated-full-compile` | `validated-full-compile` (unchanged) | `compile_evidence` → run `26821900127` (hosted corroboration) |

* The published LED preview `Ceiling-POE-VentIQ-RoomIQ-LED` has **no
  product-level compile-only row** (its WebFlash wrapper row is a different
  file), so its cited status stays honestly `none`; it compiled green but no
  metadata row is flipped.
* `validated-full-compile` is the **existing repo-approved** validated status
  (required verbatim for the manual fan candidates by
  `scripts/validate_manual_firmware_artifacts.py`); using it keeps one
  consistent vocabulary, and the run id lives in the structured
  `compile_evidence` block on each row.
* The two USB compile-only targets (`ceiling-usb-*-product-compile-only`) are
  **not** preview targets, were **not** in this run, and stay `pending-ci`.

### Reclassification of the dry-run outcomes

* The three formerly **`pending-ci` + no-wrapper** webflash previews
  (AirIQ-RoomIQ, RoomIQ, RoomIQ-LED) are now **compile-validated**; their
  [`config/preview-release-targets.json`](../config/preview-release-targets.json)
  `build_blocker` at the time recorded **only `no products/webflash wrapper`** as
  the residual prerequisite before a WebFlash build row can be prepared. That
  wrapper has since been added by `RELEASE-PREVIEW-WEBFLASH-WRAPPERS-001` (see
  [`docs/release-preview-webflash-wrappers.md`](release-preview-webflash-wrappers.md)),
  so the residual prerequisite is now a reviewed `config/webflash-builds.json`
  build row.
* The three **manual-preview fans** are **compile-validated** (now hosted-CI
  corroborated as well as the prior local/CI proof).
* **TRIAC remains blocked-by-build / `HW-005`** and is absent from every
  release / import / compile surface.

---

## 4. Exact workflow name + command (reproduce)

**Workflow name:** `Preview Compile Dry-Run`
(`.github/workflows/preview-compile-dryrun.yml`).

**Re-run the hosted compile dry-run:**

* **GitHub UI:** Actions → **Preview Compile Dry-Run** → **Run workflow** → set
  `compile_mode` = `full`.
* **GitHub CLI:**

  ```bash
  gh workflow run "Preview Compile Dry-Run" -f compile_mode=full
  ```

* **Default dispatch is safe:** `compile_mode=metadata` (the default) validates
  the scope only and runs no ESPHome.

**Reproduce the scope locally (no ESPHome needed):**

```bash
python3 scripts/list_preview_compile_targets.py            # table (7 targets)
python3 scripts/list_preview_compile_targets.py --matrix   # the CI matrix
python3 scripts/list_preview_compile_targets.py --report-excluded   # TRIAC/HW-005
```

---

## 5. What a green compile here means (and does not)

* **Means:** the product YAML's `!include` chain resolves and ESPHome codegen +
  the PlatformIO/toolchain build succeed for the ESP32-S3 target — i.e.
  **firmware-build proof**.
* **Does NOT mean:** hardware works, the board is bench-verified, any electrical
  / mains-safety / EMC compliance is met, or the target may be promoted to
  stable. Those remain separately gated (e.g. `PRODUCT-POE-410-001` for the PoE
  PSU; mains-safety + competent-person sign-off for the fans;
  `HW-005` + `COMPLIANCE-001` for TRIAC).

Flipping `compile_validation_status` from `pending-ci` to
`validated-full-compile` is exactly this **separate, reviewed metadata PR** that
cites a specific green run of this lane (run `26821900127`) — never an automatic
side effect of the dry-run.

---

## Validation results

All six commands required by the task were run from the repo root. Exact result
lines and exit codes:

| # | Command | Result | Exit |
|---|---|---|---|
| 1 | `python3 tests/validate_configs.py` | `217 files checked, 0 failed` → `✅ All configuration files are valid!` | `0` |
| 2 | `python3 scripts/validate_compile_targets.py --metadata-only` | `Read 18 compile-only target(s)` → `✅ Metadata validation passed.` | `0` |
| 3 | `python3 scripts/validate_preview_release_targets.py --metadata-only` | `Read 9 target(s)` → `✅ Preview release-target manifest validation passed.` | `0` |
| 4 | `python3 tests/test_product_catalog.py` | `Ran 41 tests` → `OK` | `0` |
| 5 | `python3 tests/validate_webflash_builds.py` | `2 build(s) checked, 0 failed` → `✅ All WebFlash build entries are valid!` | `0` |
| 6 | `python3 -m unittest discover -s tests -p "test_*.py"` | `OK` | `0` |

**Metadata / config validation: PASS (6/6, exit 0).** None of the six invokes
`esphome compile`; the firmware-build proof comes solely from the recorded hosted
run `26821900127`. File / compile-only / preview / webflash-build **counts are
unchanged** (this PR records results into existing rows; it adds no target, no
product YAML, and no WebFlash build).

---

## Follow-ups (queued in `UPCOMING_PR.md`)

* **`RELEASE-PREVIEW-WEBFLASH-WRAPPERS-001` (DONE):** the three
  `products/webflash/*.yaml` wrappers (AirIQ-RoomIQ, RoomIQ, RoomIQ-LED) have now
  been authored — see
  [`docs/release-preview-webflash-wrappers.md`](release-preview-webflash-wrappers.md).
  The compile gate was satisfied by run `26821900127`; the wrapper was the only
  residual prerequisite, and each wrapper is now recorded in the per-target
  `webflash_wrapper` field of `config/preview-release-targets.json`. Still no
  `config/webflash-builds.json` row until a reviewed build-row PR.
* **`RELEASE-PREVIEW-PUBLISH-PLAN-001`** — plan the publish path; remains
  **gated** behind the wrappers + a reviewed metadata pass.
* **FanTRIAC `HW-005`** — unchanged buildability defect; remains excluded /
  `blocked-by-build`; TRIAC policy untouched.

> **Per-target fix PRs are NOT queued** because **no compile failure was
> observed** — all seven in-scope targets passed.

---

## Guardrails — what this PR did and did NOT do

This PR **records** a green hosted compile run and flips three compile statuses
(within the policy the Summary job itself prescribed). It did **not**, and must
not be read as having done, any of:

* publish firmware; create a GitHub Release / tag / checksum; commit any `.bin`;
* update the WebFlash repo; write `firmware/sources.json` or `manifest.json`;
* add or modify any `config/webflash-builds.json` row (stays 2);
* flip any `config/product-catalog.json` status or `webflash_build_matrix`;
* mark anything stable; mark TRIAC recommended / default / stable;
* unblock or compile TRIAC (`HW-005` unresolved → excluded);
* claim hardware, bench, or compliance proof.

The files changed by the PR carrying this record are this document,
[`config/compile-only-targets.json`](../config/compile-only-targets.json) (three
`pending-ci → validated-full-compile` flips + six `compile_evidence` blocks),
[`config/preview-release-targets.json`](../config/preview-release-targets.json)
(build-blocker reclassification prose), the regression test
[`tests/test_preview_compile_dryrun.py`](../tests/test_preview_compile_dryrun.py),
and `UPCOMING_PR.md`.

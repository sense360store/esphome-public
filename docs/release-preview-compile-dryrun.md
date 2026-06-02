# Preview / Manual-Preview Compile Dry-Run (RELEASE-PREVIEW-COMPILE-DRYRUN-001)

**Canonical id:** `RELEASE-PREVIEW-COMPILE-DRYRUN-001`
**Date:** 2026-06-02
**Type:** Adds a **hosted CI compile dry-run path** for the preview /
manual-preview target matrix, plus a read-only scoping helper and the honest
run record. It **publishes no firmware**, creates **no** GitHub Release / tag /
checksum, commits **no** `.bin`, adds **no** `config/webflash-builds.json` row,
touches **no** WebFlash repo, writes **no** `firmware/sources.json` /
`manifest.json`, promotes **nothing** to stable, marks **no** TRIAC
recommended/default/stable, flips **no** `compile_validation_status`, and claims
**no** hardware / compliance / compile proof.

**Predecessors:**
[`docs/release-preview-build-dryrun.md`](release-preview-build-dryrun.md)
(`RELEASE-PREVIEW-BUILD-DRYRUN-001`, #690) ran the first metadata-only dry-run;
[`docs/release-preview-build-dryrun-002.md`](release-preview-build-dryrun-002.md)
(`RELEASE-PREVIEW-BUILD-DRYRUN-002`, #693) re-ran it after the missing-YAML fixes
(#691) and the structure audit (#692) and seeded **this** follow-up: run a
**real** ESPHome compile for the preview targets so `pending-ci` can be replaced
with a recorded result before any preview artifact is cut.

Inputs inspected (read-only):
[`UPCOMING_PR.md`](../UPCOMING_PR.md),
[`docs/release-preview-build-dryrun.md`](release-preview-build-dryrun.md),
[`docs/release-preview-build-dryrun-002.md`](release-preview-build-dryrun-002.md),
[`config/preview-release-targets.json`](../config/preview-release-targets.json),
[`config/compile-only-targets.json`](../config/compile-only-targets.json),
[`config/webflash-builds.json`](../config/webflash-builds.json),
[`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json),
[`products/bundles/**`](../products/bundles),
[`products/compile-only/**`](../products/compile-only),
[`products/webflash/**`](../products/webflash),
[`.github/workflows/**`](../.github/workflows),
[`scripts/validate_compile_targets.py`](../scripts/validate_compile_targets.py),
[`scripts/validate_preview_release_targets.py`](../scripts/validate_preview_release_targets.py),
[`scripts/list_release_targets.py`](../scripts/list_release_targets.py),
[`tests/**`](../tests).

---

## TL;DR

* **A hosted compile dry-run path now exists and is scoped to preview targets
  only.** New `workflow_dispatch`-only workflow
  [`.github/workflows/preview-compile-dryrun.yml`](../.github/workflows/preview-compile-dryrun.yml)
  + new read-only scoping helper
  [`scripts/list_preview_compile_targets.py`](../scripts/list_preview_compile_targets.py)
  compile the **seven** preview / manual-preview targets and **exclude** the
  TRIAC target (`HW-005`, reported not compiled).
* **Was the compile actually run by hosted CI in this PR? NO — not yet.** Two
  honest reasons, recorded below: (1) the local environment has **no ESPHome
  CLI**, so no local proof was produced or faked; (2) a brand-new
  `workflow_dispatch` workflow is **not dispatchable until it lands on the
  default branch** (a GitHub Actions limitation), so the new scoped lane becomes
  runnable only after this PR merges. **No compile proof is claimed.**
* **Per-target result: all seven `pending` (compile not yet run).** Their
  current `compile_validation_status` is **cited** from
  `config/compile-only-targets.json`, not re-proven here: three webflash
  previews are `pending-ci`; three fans cite a prior `validated-full-compile`;
  the LED preview is the already-published preview.
* **Metadata / config validation: PASS (6/6, exit 0)** — now **217 files / 18
  compile-only / 9 preview / 1258 tests, 0 failures** (the `+13` tests are the
  new `tests/test_preview_compile_dryrun.py` guard).
* **A green compile on this lane is firmware-build proof only** — **NOT**
  hardware proof, **NOT** bench evidence, **NOT** a compliance claim, and
  **NOT** a stable-promotion gate.

---

## 1. The hosted compile path

### Chosen path — a new, scoped, manual dry-run workflow

The task allowed reusing an existing lane or adding a new `workflow_dispatch`
dry-run lane. The existing
[`.github/workflows/compile-only.yml`](../.github/workflows/compile-only.yml)
`compile_mode=full` lane **does** invoke `esphome compile`, but it compiles **all
18** `config/compile-only-targets.json` rows — it is **not scoped** to the
preview matrix the task requires. So this PR adds a dedicated, scoped lane:

* **Workflow:** `.github/workflows/preview-compile-dryrun.yml`
  (name: **`Preview Compile Dry-Run`**).
* **Trigger:** `workflow_dispatch` **only** (no `push` / `pull_request` /
  `release`), with a `compile_mode` input (`metadata` default → scope validation
  only, no ESPHome; `full` → the real hosted `esphome compile` dry-run).
* **Scope source of truth:** `scripts/list_preview_compile_targets.py` derives
  the matrix from `config/preview-release-targets.json` (every `preview` /
  `advanced-preview` target **except** the TRIAC target), so the in-scope set
  cannot silently drift from the manifest.
* **Token:** `permissions: contents: read` (least-privilege; no write anywhere).
* **Outputs:** uploads **only** the per-target compile **log** as an expiring
  (`retention-days: 7`) `actions/upload-artifact` output. The compiled `.bin`
  stays in the ephemeral build tree and is **never** uploaded.
* **Build hygiene:** provisions throwaway test secrets and rewrites
  `packages/base/external_components.yaml` to the **local** `components/` tree
  (workspace-only, never committed) — the same proven pattern used by
  `manual-firmware-artifacts.yml` — so a feature-branch build does not depend on
  a pushed `git` ref.

### Interim path that is dispatchable today

Until this workflow merges, the **existing**
`compile-only.yml` → `workflow_dispatch` → `compile_mode=full` lane is the only
hosted compile that can be dispatched now. It is un-scoped (all 18 targets) but
**does** include the preview product-level compile-only rows
(`ceiling-poe-airiq-roomiq-product-compile-only`,
`ceiling-poe-roomiq-product-compile-only`,
`ceiling-poe-roomiq-led-product-compile-only`, and the fan rows), so it can
surface a real compile result for them in the interim.

---

## 2. Was the compile actually run by hosted CI? — NO (and not faked)

Per the honesty requirement, this is recorded exactly:

**(a) No local ESPHome — no local proof produced or faked.**

```text
$ which esphome               → (not found)
$ python3 -c "import esphome"  → ModuleNotFoundError: No module named 'esphome'
$ pip show esphome            → WARNING: Package(s) not found: esphome
```

`scripts/validate_compile_targets.py --compile` is the lane that *would* invoke
`esphome compile`; by design it "exits non-zero with a clear error rather than
faking a pass" when ESPHome is absent. Only its `--metadata-only` mode was run.

**(b) The new `workflow_dispatch` lane is not dispatchable until it merges.**
GitHub Actions only exposes a `workflow_dispatch` workflow (the "Run workflow"
button / the `POST .../dispatches` API) once the workflow file exists on the
repository's **default branch**. A brand-new workflow on a feature branch
therefore cannot be dispatched from this PR. The scoped lane becomes runnable
the moment this PR merges to the default branch.

**Conclusion:** **no hosted compile was executed in this PR**, so **no compile
proof is claimed** and every in-scope target stays at its prior status. The
exact command to run once merged is in [§4](#4-exact-workflow-name--command).

---

## 3. Per-target dry-run ledger (pass / fail / pending)

Scope = the seven preview / manual-preview targets from
`scripts/list_preview_compile_targets.py` (TRIAC excluded; see below). For all
seven: **metadata validation = PASS**, **hosted compile attempted this PR = NO**
(see §2), so **compile result = pending (not yet run)**. The
`compile_validation_status` column is **cited** from
`config/compile-only-targets.json` — previously-recorded CI status only, not
re-proven here.

| # | Config string | Lane | Tier | Cited `compile_validation_status` | This-PR compile result |
|---|---|---|---|---|---|
| 1 | `Ceiling-POE-VentIQ-RoomIQ-LED` | webflash | preview | none (published preview; webflash row present) | **pending** |
| 2 | `Ceiling-POE-AirIQ-RoomIQ` | webflash | preview | `pending-ci` | **pending** |
| 3 | `Ceiling-POE-RoomIQ` | webflash | preview | `pending-ci` | **pending** |
| 4 | `Ceiling-POE-RoomIQ-LED` | webflash | preview | `pending-ci` | **pending** |
| 5 | `Ceiling-POE-VentIQ-FanRelay-RoomIQ` | manual-preview | preview | `validated-full-compile` (prior, cited) | **pending** (re-validation owed) |
| 6 | `Ceiling-POE-FanPWM` | manual-preview | preview | `validated-full-compile` (prior, cited) | **pending** (re-validation owed) |
| 7 | `Ceiling-POE-FanDAC` | manual-preview | preview | `validated-full-compile` (prior, cited) | **pending** (re-validation owed) |

> **No row is marked `pass` or `fail`** because no hosted compile ran in this PR.
> The fans' prior `validated-full-compile` is **cited, not re-proven**; the three
> webflash previews remain `pending-ci`. This dry-run flips **no**
> `compile_validation_status`.

### Excluded (reported, not compiled)

| Config string | Lane | Tier | Why excluded |
|---|---|---|---|
| `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` | advanced-manual-preview | advanced-preview | **`HW-005` buildability blocker** — S360-320 schematic uncommitted; placeholder GPIO5/GPIO6 collide with RoomIQ J10 nets; ESPHome `ac_dimmer` cannot run across the SX1509 expander. Not buildable end-to-end, so it is **not** added to the compile matrix. TRIAC stays advanced-preview-only; never recommended/default/stable/WebFlash-exposed here. |

The stable baseline `Ceiling-POE-VentIQ-RoomIQ` is **not** a preview target and
is never in the compile-dryrun scope (the helper and
`tests/test_preview_compile_dryrun.py` enforce this).

---

## 4. Exact workflow name + command

**Workflow name:** `Preview Compile Dry-Run`
(`.github/workflows/preview-compile-dryrun.yml`).

**Run the real hosted compile dry-run (after this PR merges to the default
branch):**

* **GitHub UI:** Actions → **Preview Compile Dry-Run** → **Run workflow** →
  set `compile_mode` = `full`.
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

**Interim (dispatchable today, un-scoped) — existing lane:**

```bash
gh workflow run "Compile-only Firmware Validation" -f compile_mode=full
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

Flipping a target's `compile_validation_status` from `pending-ci` to
`validated-full-compile` is a **separate, reviewed metadata PR** that cites a
specific green run of this lane — never an automatic side effect of the dry-run.

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
| 6 | `python3 -m unittest discover -s tests -p "test_*.py"` | `Ran 1258 tests in ~2.6s` → `OK (skipped=3)` | `0` |

**Metadata / config validation: PASS (6/6, exit 0).** None of the six invokes
`esphome compile`; no build proof is produced by any of them. The `+13` tests vs
`RELEASE-PREVIEW-BUILD-DRYRUN-002` are `tests/test_preview_compile_dryrun.py`
(scope + workflow-guardrail regression locks). File / compile-only / preview /
webflash-build counts are unchanged (the new workflow, script, and test are not
counted by `validate_configs.py`, which scans only product/package YAML).

---

## Follow-ups (queued in `UPCOMING_PR.md`)

* **Run the lane (post-merge):** dispatch `Preview Compile Dry-Run`
  (`compile_mode=full`), then record exact per-target pass/fail in this doc.
* **`RELEASE-PREVIEW-WEBFLASH-WRAPPERS-001`** — author the three
  `products/webflash/*.yaml` wrappers (AirIQ-RoomIQ, RoomIQ, RoomIQ-LED). **Still
  gated** on a real green compile from this lane; still no
  `config/webflash-builds.json` row until proof exists.
* **`RELEASE-PREVIEW-PUBLISH-PLAN-001`** (already queued) — plan the publish path;
  **blocked** until a real compile records build proof.
* **FanTRIAC `HW-005`** — unchanged buildability defect; remains excluded /
  `blocked-by-build`; TRIAC policy untouched.

> **Per-target fix PRs are NOT queued by this PR** because **no compile failure
> was observed** (no compile ran). They are queued only if/when the
> `compile_mode=full` run records an actual per-target failure.

---

## Guardrails — what this PR did NOT do

This PR adds a compile **path** + scoping helper + honest record. It did **not**,
and must not be read as having done, any of:

* run a hosted compile or claim any compile / build proof;
* publish firmware; create a GitHub Release / tag / checksum; commit any `.bin`;
* update the WebFlash repo; write `firmware/sources.json` or `manifest.json`;
* add or modify any `config/webflash-builds.json` row (stays 2);
* flip any `compile_validation_status` (the three webflash previews stay
  `pending-ci`), `config/product-catalog.json` status, or `webflash_build_matrix`;
* mark anything stable; mark TRIAC recommended / default / stable;
* unblock TRIAC (`HW-005` unresolved → excluded);
* claim hardware or compliance proof.

The only files changed by the PR carrying this report are the new workflow, the
new scoping script, the new regression test, this document, and `UPCOMING_PR.md`.

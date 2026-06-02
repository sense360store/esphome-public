# Preview Release Build / Release Dry-Run (RELEASE-PREVIEW-BUILD-DRYRUN-001)

**Canonical id:** `RELEASE-PREVIEW-BUILD-DRYRUN-001`
**Date:** 2026-06-02
**Type:** Dry-run **report** doc only. This document records a build/release
dry-run for the current preview / manual-preview / advanced-manual-preview target
matrix. It **publishes no firmware**, creates **no** GitHub Release / tag /
checksum, commits **no** `.bin`, adds **no** `config/webflash-builds.json` row,
touches **no** WebFlash repo, writes **no** `firmware/sources.json` /
`manifest.json`, promotes **nothing** to stable, marks **no** TRIAC
recommended/default/stable, and claims **no** hardware / compliance / build proof.

Inputs inspected (read-only):
[`UPCOMING_PR.md`](../UPCOMING_PR.md),
[`config/preview-release-targets.json`](../config/preview-release-targets.json),
[`config/release-channel-policy.json`](../config/release-channel-policy.json),
[`config/webflash-builds.json`](../config/webflash-builds.json),
[`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json),
[`config/compile-only-targets.json`](../config/compile-only-targets.json),
[`config/product-catalog.json`](../config/product-catalog.json),
[`.github/workflows/**`](../.github/workflows),
[`scripts/validate_preview_release_targets.py`](../scripts/validate_preview_release_targets.py),
[`scripts/validate_compile_targets.py`](../scripts/validate_compile_targets.py),
[`scripts/list_release_targets.py`](../scripts/list_release_targets.py),
[`docs/preview-release-targets.md`](preview-release-targets.md),
[`docs/release-channel-policy.md`](release-channel-policy.md).

---

## TL;DR

* **Metadata / config validation dry-run: PASS.** All six required validation
  commands pass with exit code `0` (see [§Validation results](#validation-results)).
* **ESPHome compile dry-run: NOT ATTEMPTED — `esphome` CLI unavailable.** No
  `esphome` binary and no `esphome` Python module exist in this environment, so
  no compile/build pass was run. **No build proof is claimed or faked here.**
  Where a target carries a prior `compile_validation_status`, that value is
  **cited from `config/compile-only-targets.json` as previously-recorded CI
  status only** — it is *not* re-proven by this dry-run.
* **Targets covered:** all **9** targets in
  `config/preview-release-targets.json` (1 stable baseline, 8 preview /
  advanced-preview).
* **Outcome counts** (see [§Outcome classification](#outcome-classification)):

  | Classification | Count | Targets |
  |---|---|---|
  | `stable-only-existing` | 1 | `Ceiling-POE-VentIQ-RoomIQ` |
  | `ready-for-preview-build` | 1 | `Ceiling-POE-VentIQ-RoomIQ-LED` (already published preview) |
  | `ready-for-manual-preview-build` | 3 | `Ceiling-POE-VentIQ-FanRelay-RoomIQ`, `Ceiling-POE-FanPWM`, `Ceiling-POE-FanDAC` |
  | `blocked-by-missing-yaml` | 3 | `Ceiling-POE-AirIQ-RoomIQ`, `Ceiling-POE-RoomIQ`, `Ceiling-POE-RoomIQ-LED` |
  | `blocked-by-build` | 1 | `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` (HW-005) |
  | `blocked-by-policy` | 0 | — (no target is blocked from preview by policy) |

  > The `ready-*` classifications mean **metadata-clean with no build blocker and
  > a delivery lane present** — they do **not** claim a fresh compile. A real
  > compile dry-run (ESPHome available) is still owed before any artifact is cut.

---

## Method & environment

### What this dry-run did

1. Inspected the policy + target configs, the workflows, the validators, and the
   docs listed above.
2. Ran the full metadata / config validation suite and recorded **exact**
   results and exit codes.
3. For every target in `config/preview-release-targets.json`, recorded the config
   string, delivery lane, YAML/product path, expected artifact name, metadata-
   validation result, compile attempt/result, exact blocker (if any), required
   warning copy, and stable blocker.
4. Classified each target's dry-run outcome.

### What this dry-run could not do — and did not fake

`esphome` is **not installed** in this environment:

```text
$ which esphome            → (not found)
$ python3 -c "import esphome"  → ModuleNotFoundError: No module named 'esphome'
```

Per the task's honesty requirement, the compile dry-run is therefore recorded as:

* **compile not attempted / ESPHome CLI unavailable;**
* **metadata validation only;**
* **no build proof claimed.**

`scripts/validate_compile_targets.py --compile` is the lane that *would* invoke
`esphome compile`; by design it "exits non-zero with a clear error rather than
faking a pass" when ESPHome is absent. We therefore ran only its
`--metadata-only` mode (the safe default).

### Note on `validate_configs.py`

`python3 tests/validate_configs.py` is a **YAML-syntax / structure** validator
(it `yaml.safe_load`s each file and checks structure); it is **not** an ESPHome
compile and produces **no** build proof. A `0-failed` result there means the
YAML parses and is structurally well-formed, nothing more.

### Existing dry-run lanes referenced (not invoked here)

* **`.github/workflows/firmware-build-release.yml`** — has an explicit,
  safe-by-default `dry_run` input (`RELEASE-WORKFLOW-DRYRUN-MODE-001`, defaults
  `true`). A dry-run dispatch exercises release-note planning + guardrails for the
  **release-eligible** builds only (`config/webflash-builds.json`:
  stable `Ceiling-POE-VentIQ-RoomIQ` + preview `Ceiling-POE-VentIQ-RoomIQ-LED`),
  creating **no** GitHub Release and uploading **no** asset. Its
  `release_target` picker is intentionally limited to those two config strings;
  FanRelay / FanPWM / FanDAC are deliberately **absent** (manual-candidate-only).
* **`.github/workflows/manual-firmware-artifacts.yml`** — `workflow_dispatch`-only
  lane that compiles the FanRelay / FanPWM / FanDAC manual-preview candidates and
  uploads only temporary, expiring GitHub Actions artifacts. Non-release by
  construction (no Release, no `sources.json` / `manifest.json`, no committed
  `.bin`, no WebFlash row). This is the **manual-preview** delivery lane.
* **`.github/workflows/compile-only.yml`** — push/PR metadata-only validation;
  full `esphome compile` only under `workflow_dispatch` with `compile_mode=full`.

Running any of these as a *live* GitHub Actions dry-run is **out of scope** for
this doc (this is a recorded local dry-run + report); the workflow lanes are
referenced so a follow-up can drive them once ESPHome is available.

---

## Validation results

All six commands required by the task were run from the repo root. Exact result
lines and exit codes:

| # | Command | Result | Exit |
|---|---|---|---|
| 1 | `python3 tests/validate_configs.py` | `Validation Summary: 213 files checked, 0 failed` → `✅ All configuration files are valid!` | `0` |
| 2 | `python3 scripts/validate_compile_targets.py --metadata-only` | `Read 16 compile-only target(s)` → `✅ Metadata validation passed.` | `0` |
| 3 | `python3 scripts/validate_preview_release_targets.py --metadata-only` | `Read 9 target(s)` → `✅ Preview release-target manifest validation passed.` | `0` |
| 4 | `python3 tests/test_product_catalog.py` | `Ran 41 tests` → `OK` | `0` |
| 5 | `python3 tests/validate_webflash_builds.py` | `WebFlash Build Matrix: 2 build(s) checked, 0 failed` → `✅ All WebFlash build entries are valid!` | `0` |
| 6 | `python3 -m unittest discover -s tests -p "test_*.py"` | `Ran 1245 tests in 2.237s` → `OK (skipped=3)` | `0` |

**Metadata / config validation: PASS (6/6, exit 0).** No compile was run in any
of these (none of the six invokes `esphome compile`).

---

## Per-target dry-run ledger

One entry per target in `config/preview-release-targets.json`. **Lane** uses the
task vocabulary (`stable` / `webflash-preview` / `manual-preview` /
`advanced-manual-preview`); the manifest stores the stable baseline and the SELV
previews both under `delivery_lane: webflash`, split here by channel tier.

For all 9 targets: **metadata validation = PASS** (covered by command #3 above,
which exits `0`), and **compile attempted = NO / ESPHome CLI unavailable**
(`compile result = not available`). Those two columns are therefore stated once
here and not repeated per row.

### Summary matrix

| # | Config string | Lane | Tier | Expected artifact | Warning copy | Cuttable now? | Classification |
|---|---|---|---|---|---|---|---|
| 1 | `Ceiling-POE-VentIQ-RoomIQ` | stable | stable | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` | none | already live | `stable-only-existing` |
| 2 | `Ceiling-POE-VentIQ-RoomIQ-LED` | webflash-preview | preview | `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` | `preview` | already published | `ready-for-preview-build` |
| 3 | `Ceiling-POE-AirIQ-RoomIQ` | webflash-preview | preview | `Sense360-Ceiling-POE-AirIQ-RoomIQ-v1.0.0-preview.bin` | `preview` | **no** | `blocked-by-missing-yaml` |
| 4 | `Ceiling-POE-RoomIQ` | webflash-preview | preview | `Sense360-Ceiling-POE-RoomIQ-v1.0.0-preview.bin` | `preview` | **no** | `blocked-by-missing-yaml` |
| 5 | `Ceiling-POE-RoomIQ-LED` | webflash-preview | preview | `Sense360-Ceiling-POE-RoomIQ-LED-v1.0.0-preview.bin` | `preview` | **no** | `blocked-by-missing-yaml` |
| 6 | `Ceiling-POE-VentIQ-FanRelay-RoomIQ` | manual-preview | preview | `Sense360-Ceiling-POE-VentIQ-FanRelay-RoomIQ-v1.0.0-preview.bin` | `preview` | metadata-clean¹ | `ready-for-manual-preview-build` |
| 7 | `Ceiling-POE-FanPWM` | manual-preview | preview | `Sense360-Ceiling-POE-FanPWM-v1.0.0-preview.bin` | `preview` | metadata-clean¹ | `ready-for-manual-preview-build` |
| 8 | `Ceiling-POE-FanDAC` | manual-preview | preview | `Sense360-Ceiling-POE-FanDAC-v1.0.0-preview.bin` | `preview` | metadata-clean¹ | `ready-for-manual-preview-build` |
| 9 | `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` | advanced-manual-preview | advanced-preview | `Sense360-Ceiling-POE-VentIQ-FanTRIAC-RoomIQ-v1.0.0-preview.bin` | `advanced-preview` (mains-risk) | **no** | `blocked-by-build` |

> ¹ **metadata-clean** = no `build_blocker` recorded, delivery lane present, all
> metadata validation green. It is **not** a fresh compile pass. A real ESPHome
> compile dry-run is still owed before a manual-preview `.bin` is cut.

---

### 1 — `Ceiling-POE-VentIQ-RoomIQ` (stable baseline)

* **Config string:** `Ceiling-POE-VentIQ-RoomIQ`
* **Lane:** `stable` (manifest `delivery_lane: webflash`, tier `stable`)
* **YAML / product path:** `products/sense360-ceiling-poe-ventiq-roomiq.yaml`
  (WebFlash wrapper `products/webflash/ceiling-poe-ventiq-roomiq.yaml`)
* **Expected artifact:** `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`
* **Metadata validation:** PASS
* **Compile attempted:** no — ESPHome CLI unavailable
* **Compile result:** not available (target is the **already-published live
  `v1.0.0` stable** release; no rebuild attempted or needed by this dry-run)
* **Blocker (cuttable now?):** none for preview purposes — already live stable;
  **out of scope** for this dry-run (stable stays evidence-gated and is not
  modified).
* **Warning copy required:** none (stable)
* **Stable blocker:** none (already stable / published)
* **Classification:** `stable-only-existing`

### 2 — `Ceiling-POE-VentIQ-RoomIQ-LED` (LED preview, published)

* **Config string:** `Ceiling-POE-VentIQ-RoomIQ-LED`
* **Lane:** `webflash-preview`
* **YAML / product path:** `products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`
  (WebFlash wrapper `products/webflash/ceiling-poe-ventiq-roomiq-led.yaml`)
* **Expected artifact:** `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`
* **Metadata validation:** PASS
* **Compile attempted:** no — ESPHome CLI unavailable
* **Compile result:** not available (already a published preview row in
  `config/webflash-builds.json`; no rebuild attempted by this dry-run)
* **Blocker (cuttable now?):** none — already published preview; serves as the
  reference proving the WebFlash matrix may carry a preview without stable
  promotion.
* **Warning copy required:** yes — `preview`
* **Stable blocker:** LED preview-to-stable gauntlet (operator flash proof, bench
  verification, stable promotion).
* **Classification:** `ready-for-preview-build` (already published)

### 3 — `Ceiling-POE-AirIQ-RoomIQ` (Kitchen / AirIQ preview)

* **Config string:** `Ceiling-POE-AirIQ-RoomIQ`
* **Lane:** `webflash-preview`
* **YAML / product path:** `products/compile-only/ceiling-poe-airiq-roomiq.yaml`
  (compile-only skeleton only)
* **Expected artifact:** `Sense360-Ceiling-POE-AirIQ-RoomIQ-v1.0.0-preview.bin`
* **Metadata validation:** PASS
* **Compile attempted:** no — ESPHome CLI unavailable
* **Compile result:** not available (prior `compile_validation_status` in
  `config/compile-only-targets.json` is unset/`None` for this skeleton — i.e. **no
  prior compile proof recorded** either)
* **Exact blocker (cuttable now? NO):** **no top-level product/catalog entry and
  no `products/webflash` wrapper.** Confirmed: `config/product-catalog.json` has
  **no entry** for `Ceiling-POE-AirIQ-RoomIQ`, and `products/webflash/` contains
  only the three `ventiq-*` wrappers. Buildable today **only** as the compile-only
  skeleton. A catalog preview entry + `products/webflash` wrapper + recorded build
  proof are required before a `config/webflash-builds.json` row is cut.
* **Warning copy required:** yes — `preview`
* **Stable blocker:** S360-410 PoE-PSU schematic verification + AirIQ sensor-stack
  bench evidence.
* **Classification:** `blocked-by-missing-yaml`

### 4 — `Ceiling-POE-RoomIQ` (Bedroom / RoomIQ preview)

* **Config string:** `Ceiling-POE-RoomIQ`
* **Lane:** `webflash-preview`
* **YAML / product path:** `products/compile-only/ceiling-poe-roomiq.yaml`
  (compile-only skeleton; top-level `products/sense360-ceiling-poe-roomiq.yaml`
  exists but is registered compile-only `pending-ci`)
* **Expected artifact:** `Sense360-Ceiling-POE-RoomIQ-v1.0.0-preview.bin`
* **Metadata validation:** PASS
* **Compile attempted:** no — ESPHome CLI unavailable
* **Compile result:** not available (prior status: skeleton unset/`None`; the
  top-level product compile-only target is `pending-ci` — **no green compile proof
  recorded**)
* **Exact blocker (cuttable now? NO):** **no `products/webflash` wrapper YAML.**
  Preview is **allowed** by policy (the catalog `status` gate is a *stable*
  /lifecycle gate, not a preview prohibition); what blocks an actual WebFlash row
  is the missing wrapper (buildable today only as the compile-only skeleton) plus
  the absence of a recorded compile.
* **Warning copy required:** yes — `preview`
* **Stable blocker:** S360-410 PoE-PSU schematic verification
  (PRODUCT-POE-410-001 / PACKAGE-POE-410-001).
* **Classification:** `blocked-by-missing-yaml`

### 5 — `Ceiling-POE-RoomIQ-LED` (Living / Corridor preview)

* **Config string:** `Ceiling-POE-RoomIQ-LED`
* **Lane:** `webflash-preview`
* **YAML / product path:** `products/compile-only/ceiling-poe-roomiq.yaml`
  (shared skeleton; does **not** encode the LED token)
* **Expected artifact:** `Sense360-Ceiling-POE-RoomIQ-LED-v1.0.0-preview.bin`
* **Metadata validation:** PASS
* **Compile attempted:** no — ESPHome CLI unavailable
* **Compile result:** not available (no dedicated YAML exists to compile; catalog
  has **no entry** for `Ceiling-POE-RoomIQ-LED`)
* **Exact blocker (cuttable now? NO):** **no dedicated product or
  `products/webflash` wrapper YAML** — it shares the compile-only RoomIQ skeleton,
  which does not carry the LED token, and has no catalog entry. A product +
  wrapper YAML and a recorded compile are required before a
  `config/webflash-builds.json` row is cut.
* **Warning copy required:** yes — `preview`
* **Stable blocker:** S360-410 PoE-PSU schematic verification + LED
  preview-to-stable gauntlet.
* **Classification:** `blocked-by-missing-yaml`

### 6 — `Ceiling-POE-VentIQ-FanRelay-RoomIQ` (FanRelay preview)

* **Config string:** `Ceiling-POE-VentIQ-FanRelay-RoomIQ`
* **Lane:** `manual-preview` (WebFlash one-click import gated follow-up:
  WEBFLASH-RELAY-001)
* **YAML / product path:** `products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`
  (manual-preview candidate `fanrelay` in `config/manual-firmware-artifacts.json`)
* **Expected artifact:** `Sense360-Ceiling-POE-VentIQ-FanRelay-RoomIQ-v1.0.0-preview.bin`
* **Metadata validation:** PASS (catalog `webflash_build_matrix=false` confirmed —
  fan-token guardrail intact)
* **Compile attempted:** no — ESPHome CLI unavailable
* **Compile result:** not available **this run**. *Prior* status cited from
  `config/compile-only-targets.json`:
  `ceiling-poe-ventiq-fanrelay-roomiq-compile-only` =
  `compile_validation_status: validated-full-compile` — **previously-recorded CI
  proof, not re-proven here.**
* **Blocker (cuttable now?):** `build_blocker: null` — **no build blocker.** The
  preview `.bin` is delivered via the manual-preview lane. Remaining gap for a cut
  this run is only the **absent ESPHome compile re-run** (no new proof claimed).
* **Warning copy required:** yes — `preview`
* **Stable blocker:** Mains-safety / installation-approval / creepage / clearance
  evidence + competent-person sign-off + GPIO3 strap-pin boot characterisation.
* **Classification:** `ready-for-manual-preview-build`

### 7 — `Ceiling-POE-FanPWM` (FanPWM preview)

* **Config string:** `Ceiling-POE-FanPWM`
* **Lane:** `manual-preview` (gated follow-up: WEBFLASH-PWM-001)
* **YAML / product path:** `products/sense360-ceiling-poe-fanpwm.yaml`
  (manual-preview candidate `fanpwm`)
* **Expected artifact:** `Sense360-Ceiling-POE-FanPWM-v1.0.0-preview.bin`
* **Metadata validation:** PASS (catalog `webflash_build_matrix=false` confirmed)
* **Compile attempted:** no — ESPHome CLI unavailable
* **Compile result:** not available **this run**. *Prior* status cited:
  `ceiling-poe-fanpwm-product-compile-only` =
  `validated-full-compile` (native ESP32-S3 GPIO PWM path) — **previously-recorded
  CI proof, not re-proven here.**
* **Blocker (cuttable now?):** `build_blocker: null` — **no build blocker.** Only
  the absent ESPHome compile re-run stands between metadata-clean and a cut.
* **Warning copy required:** yes — `preview`
* **Stable blocker:** Measured current / thermal evidence
  (S360-311-CURRENT-THERMAL-001). RPM / TachIO not claimed (`rpm_supported: false`).
* **Classification:** `ready-for-manual-preview-build`

### 8 — `Ceiling-POE-FanDAC` (FanDAC preview)

* **Config string:** `Ceiling-POE-FanDAC`
* **Lane:** `manual-preview` (gated follow-up: WEBFLASH-DAC-001)
* **YAML / product path:** `products/sense360-ceiling-poe-fandac.yaml`
  (manual-preview candidate `fandac`)
* **Expected artifact:** `Sense360-Ceiling-POE-FanDAC-v1.0.0-preview.bin`
* **Metadata validation:** PASS (catalog `webflash_build_matrix=false` confirmed)
* **Compile attempted:** no — ESPHome CLI unavailable
* **Compile result:** not available **this run**. *Prior* status cited:
  `ceiling-poe-fandac-product-compile-only` = `validated-full-compile` — **previously-recorded
  CI proof, not re-proven here.**
* **Blocker (cuttable now?):** `build_blocker: null` — **no build blocker.**
  Enforces the FanDAC↔AirIQ mutex. Only the absent ESPHome compile re-run stands
  between metadata-clean and a cut.
* **Warning copy required:** yes — `preview`
* **Stable blocker:** Cloudlift S12 / J3 harness + product-bench evidence;
  S360-312 schematic / BOM.
* **Classification:** `ready-for-manual-preview-build`

### 9 — `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` (FanTRIAC advanced-preview)

* **Config string:** `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`
* **Lane:** `advanced-manual-preview` (WebFlash import gated follow-up:
  WF-IMPORT-TRIAC-001)
* **YAML / product path:** `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`
  (WebFlash wrapper exists but is **not** import-enabled here)
* **Expected artifact:** `Sense360-Ceiling-POE-VentIQ-FanTRIAC-RoomIQ-v1.0.0-preview.bin`
* **Metadata validation:** PASS
* **Compile attempted:** no — ESPHome CLI unavailable
* **Compile result:** not available (and the target is **not buildable
  end-to-end** regardless — see blocker)
* **Exact blocker (cuttable now? NO):** **HW-005 buildability blocker** (a
  *buildability* blocker, **not** a stable-evidence gate and **not** a
  preview-policy block): S360-320 schematic uncommitted; placeholder GPIO5/GPIO6
  collide with RoomIQ J10 nets; ESPHome `ac_dimmer` cannot run across the SX1509
  expander. No advanced-preview artifact can be cut until HW-005 resolves.
* **Warning copy required:** yes — `advanced-preview` (**MAINS-VOLTAGE RISK**;
  competent-person manual install only).
* **Stable blocker:** HW-005 (S360-320 schematic; GPIO5/GPIO6 collision;
  `ac_dimmer` across SX1509) + PACKAGE-TRIAC-001 + COMPLIANCE-001 mains-voltage
  review.
* **Classification:** `blocked-by-build`
* **Guardrail:** TRIAC stays advanced-preview-only — never recommended, default,
  REQUIRED_CONFIG, stable, or WebFlash-exposed in this dry-run.

---

## Required warning copy (verbatim)

From `config/release-channel-policy.json` → `warning_copy` (reused verbatim by the
target manifest). These must appear in the release notes / acknowledgement gate
for any future cut:

**`preview`** (targets 2–8):

> PREVIEW FIRMWARE — buildable and installable for testers only. This build is NOT
> hardware verified, NOT stable, NOT recommended, and NOT a customer default. No
> bench evidence and no compliance is claimed. Flash at your own risk and expect
> to recover with the rescue/stable firmware.

**`advanced-preview`** (target 9, FanTRIAC):

> ADVANCED PREVIEW — MAINS-VOLTAGE RISK. This firmware drives mains-voltage
> hardware (e.g. TRIAC phase-control dimming) and is for competent persons
> performing a manual installation only. It is NOT hardware verified, NOT stable,
> NOT recommended, and is NEVER a default. No bench evidence and no
> electrical-safety / compliance certification is claimed. Incorrect installation
> can cause fire, electric shock, or death. Do not install unless you are
> qualified to work on mains wiring.

---

## Outcome classification

| Classification | Targets |
|---|---|
| `ready-for-preview-build` | `Ceiling-POE-VentIQ-RoomIQ-LED` — already published preview; the WebFlash-preview lane is proven by it. |
| `ready-for-manual-preview-build` | `Ceiling-POE-VentIQ-FanRelay-RoomIQ`, `Ceiling-POE-FanPWM`, `Ceiling-POE-FanDAC` — metadata-clean, no build blocker, manual-preview lane present, prior `validated-full-compile` recorded. **A fresh ESPHome compile dry-run is still owed before a `.bin` is cut.** |
| `blocked-by-missing-yaml` | `Ceiling-POE-AirIQ-RoomIQ` (no catalog entry + no wrapper), `Ceiling-POE-RoomIQ` (no wrapper), `Ceiling-POE-RoomIQ-LED` (no dedicated product/wrapper YAML, no catalog entry). |
| `blocked-by-build` | `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` — HW-005 buildability (not buildable end-to-end). |
| `blocked-by-policy` | **None.** No buildable target is blocked from preview by policy; lack of hardware proof blocks **stable only**. |
| `stable-only-existing` | `Ceiling-POE-VentIQ-RoomIQ` — live `v1.0.0` stable baseline, unchanged / out of scope. |

### Dry-run verdict

* The **metadata / config dry-run is clean** across all 9 targets and the whole
  test suite (1245 tests, 0 failures).
* **No compile dry-run was performed** (ESPHome CLI unavailable) → **no build
  proof is claimed**, and the `ready-*` rows remain pending a real compile.
* **Build blockers exist** (1 `blocked-by-build` + 3 `blocked-by-missing-yaml`)
  → a build-fixes follow-up is warranted.
* **Enough targets are metadata-clean** (3 manual-preview fan targets + the
  already-published LED preview) to warrant a publish **plan** — gated behind the
  still-owed real compile dry-run.

---

## Follow-ups (queued in `UPCOMING_PR.md`)

* **`RELEASE-PREVIEW-BUILD-FIXES-001`** — *queued (build blockers found).* Convert
  each recorded blocker into a scoped build-fix: FanTRIAC HW-005 buildability;
  AirIQ-RoomIQ catalog entry + wrapper; RoomIQ wrapper; RoomIQ-LED product +
  wrapper. Planning / decomposition only.
* **`RELEASE-PREVIEW-PUBLISH-PLAN-001`** — *queued (enough targets metadata-clean),
  gated.* Plan the publish path for the metadata-clean previews (3 manual-preview
  fan targets + the live LED preview). **Blocked** until a real ESPHome compile
  dry-run records build proof for the manual-preview targets; planning only,
  publishes nothing.

---

## Guardrails — what this dry-run did NOT do

This dry-run / report did **not**, and must not be read as having done, any of:

* publish firmware;
* create a GitHub Release;
* create a tag;
* commit any `.bin`;
* generate checksums for publication;
* update the WebFlash repo;
* update `firmware/sources.json`;
* update `manifest.json`;
* add or modify any `config/webflash-builds.json` row;
* flip any `config/product-catalog.json` status or `webflash_build_matrix`;
* mark anything stable;
* mark TRIAC recommended / default / stable;
* claim hardware proof;
* claim compliance proof;
* fake or claim a fresh compile proof.

It records **dry-run metadata + exact validation results** only.

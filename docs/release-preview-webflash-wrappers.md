# Preview WebFlash wrappers — readiness record

**Canonical id:** `RELEASE-PREVIEW-WEBFLASH-WRAPPERS-001`
**Date:** 2026-06-02
**Type:** Adds the three missing `products/webflash` wrapper YAMLs for the
compile-validated webflash-lane **preview** candidates so a later, reviewed
build-row PR can address them via the `products/webflash/` namespace. This PR
**publishes no firmware**, creates **no** GitHub Release / tag / checksum,
commits **no** `.bin`, adds **no** `config/webflash-builds.json` row, writes
**no** `firmware/sources.json` / `manifest.json`, flips **no**
`config/product-catalog.json` status, touches **no** WebFlash repo, marks
**nothing** stable, adds **no** TRIAC wrapper, adds **no** fan manual-preview
wrapper, and claims **no** hardware / bench / compliance proof.

**Predecessors:**
[`docs/release-preview-compile-dryrun.md`](release-preview-compile-dryrun.md)
(`RELEASE-PREVIEW-COMPILE-DRYRUN-001` added the hosted compile lane, #694;
`RELEASE-PREVIEW-COMPILE-RESULTS-001` recorded the green hosted run, #695)
flipped the three webflash previews to `validated-full-compile` and recorded
that their **only** residual WebFlash prerequisite was the `products/webflash`
wrapper. This PR authors those wrappers.

---

## TL;DR

* **The three `products/webflash` wrappers now exist.** Each is a thin
  WebFlash-namespaced wrapper that re-includes its canonical
  `products/sense360-*.yaml` shim (which in turn `!include`s the bundle under
  `products/bundles/`). No package wiring is duplicated.
* **Preview-only, no artifact metadata.** Each wrapper declares only a
  `packages:` block — **no** `version`, **no** `channel`, **no**
  `artifact_name`. None claims stable status or hardware verification.
* **No WebFlash build rows added.** `config/webflash-builds.json` stays at its
  existing **2** builds (the stable `Ceiling-POE-VentIQ-RoomIQ` and the preview
  `Ceiling-POE-VentIQ-RoomIQ-LED`). Those two rows — and the existing stable /
  LED preview / FanTRIAC-reference wrappers — are **unchanged**.
* **The manifest now records each wrapper.** Each of the three targets in
  [`config/preview-release-targets.json`](../config/preview-release-targets.json)
  gains a `webflash_wrapper` field, and its `build_blocker` is reclassified from
  "no `products/webflash` wrapper" to "needs a reviewed
  `config/webflash-builds.json` build row" (the blocker stays non-empty; the
  targets stay `eligible-unpublished`).
* **Import/publish stays gated.** Cutting an actual `config/webflash-builds.json`
  row — with recorded firmware-build proof — remains a separate, later,
  reviewed PR.

---

## 1. Wrappers added

Naming follows the existing convention: the wrapper basename is the lowercased
WebFlash config string, and the wrapper `!include`s the matching
`products/sense360-<config>.yaml` shim.

| WebFlash config string | Wrapper (this PR) | Canonical shim it re-includes | Bundle composition |
|---|---|---|---|
| `Ceiling-POE-AirIQ-RoomIQ` | `products/webflash/ceiling-poe-airiq-roomiq.yaml` | `products/sense360-ceiling-poe-airiq-roomiq.yaml` | `products/bundles/ceiling-poe-airiq-roomiq.yaml` |
| `Ceiling-POE-RoomIQ` | `products/webflash/ceiling-poe-roomiq.yaml` | `products/sense360-ceiling-poe-roomiq.yaml` | `products/bundles/ceiling-poe-roomiq.yaml` |
| `Ceiling-POE-RoomIQ-LED` | `products/webflash/ceiling-poe-roomiq-led.yaml` | `products/sense360-ceiling-poe-roomiq-led.yaml` | `products/bundles/ceiling-poe-roomiq-led.yaml` |

Each wrapper carries a header block that states, verbatim, that it is **not**
stable / production / recommended / a customer default, is **not** in the
WebFlash build matrix, has **no** firmware artifact, and is **not** hardware
verified — and that a green compile is firmware-build proof only.

`Ceiling-POE-RoomIQ-LED` is the **RoomIQ + LED** sibling shared by the
Living-room and Corridor room bundles; it is **distinct** from the
already-published LED preview `Ceiling-POE-VentIQ-RoomIQ-LED`, which is
unchanged.

---

## 2. Manifest changes (`config/preview-release-targets.json`)

For each of the three targets (`ceiling-poe-airiq-roomiq-preview`,
`ceiling-poe-roomiq-preview`, `ceiling-poe-roomiq-led-preview`):

* **`webflash_wrapper`** — new field recording the wrapper path from §1.
* **`build_blocker`** — reclassified. Before: "ONLY the `products/webflash`
  wrapper YAML does not exist yet." After: "the wrapper now EXISTS; the only
  thing still blocking an actual WebFlash row is a reviewed
  `config/webflash-builds.json` build row (with recorded firmware-build proof),
  which stays a separate, later PR." The blocker stays non-empty so the
  manifest's own validator (`scripts/validate_preview_release_targets.py`) keeps
  requiring an explicit build blocker for every unpublished webflash target.
* **`channel_tier` / `publication_status` / eligibility — unchanged.** Each
  target stays `preview`, `eligible-unpublished`, never recommended / default /
  required-config, and absent from `config/webflash-builds.json`.

The stable baseline (`Ceiling-POE-VentIQ-RoomIQ`) and the published LED preview
(`Ceiling-POE-VentIQ-RoomIQ-LED`) target rows are **not** modified.

---

## 3. What is proven (and what is not)

* **Proven (firmware-build only):** the canonical product YAML for each of the
  three targets compiled GREEN on hosted CI in the
  [`Preview Compile Dry-Run`](release-preview-compile-dryrun.md) run
  `26821900127` (2026-06-02, ESPHome 2026.4.5). The wrappers re-include exactly
  those canonical YAMLs.
* **Not proven / not claimed:** hardware operation, bench verification, verified
  schematic, electrical / mains-safety / EMC compliance, or any stable-promotion
  readiness. Stable additionally stays gated by `PRODUCT-POE-410-001` (S360-410
  PoE-PSU schematic verification) and, for the LED sibling, the LED
  preview-to-stable gauntlet.

---

## 4. Guardrails — what this PR did and did NOT do

This PR **adds three preview-only wrapper YAMLs** and records them in the preview
target manifest. It did **not**, and must not be read as having done, any of:

* publish firmware; create a GitHub Release / tag / checksum; commit any `.bin`;
* add or modify any `config/webflash-builds.json` row (stays 2);
* write `firmware/sources.json` or `manifest.json`; touch the WebFlash repo;
* flip any `config/product-catalog.json` status or `webflash_build_matrix`;
* mark anything stable; claim hardware, bench, or compliance proof;
* add a TRIAC wrapper (FanTRIAC stays `advanced-manual-preview`, blocked by
  `HW-005`, and is not referenced by a `webflash_wrapper`);
* add a fan manual-preview wrapper (FanRelay / FanPWM / FanDAC stay
  `manual-preview`, off the WebFlash lane, with no wrapper on disk).

---

## 5. Validation results

All six commands required by the task were run from the repo root:

| # | Command | Expected result |
|---|---|---|
| 1 | `python3 tests/validate_configs.py` | `✅ All configuration files are valid!` (file count rises by the 3 new wrappers) |
| 2 | `python3 scripts/validate_compile_targets.py --metadata-only` | `✅ Metadata validation passed.` (unchanged; this PR edits no compile-only target) |
| 3 | `python3 scripts/validate_preview_release_targets.py --metadata-only` | `✅ Preview release-target manifest validation passed.` (9 targets) |
| 4 | `python3 tests/test_product_catalog.py` | `OK` |
| 5 | `python3 tests/validate_webflash_builds.py` | `2 build(s) checked, 0 failed` → `✅ All WebFlash build entries are valid!` |
| 6 | `python3 -m unittest discover -s tests -p "test_*.py"` | `OK` (incl. the new `tests/test_preview_webflash_wrappers.py`) |

A regression guard, [`tests/test_preview_webflash_wrappers.py`](../tests/test_preview_webflash_wrappers.py),
locks the invariants above: the wrapper files exist, each resolves to a valid
product shim, the manifest references valid wrappers, the stable and LED preview
targets are unchanged, no TRIAC or fan wrapper was added, and no
`config/webflash-builds.json` row was added.

---

## 6. Follow-ups

* **Reviewed `config/webflash-builds.json` build-row PR (next):** prepare the
  WebFlash build rows for the three wrapped previews on a non-stable channel,
  with recorded firmware-build proof. WebFlash one-click import remains a
  separate, gated step after that.
* **FanTRIAC `HW-005`** — unchanged buildability defect; remains excluded;
  TRIAC policy untouched.

## Cross-references

- Compile dry-run record: [`docs/release-preview-compile-dryrun.md`](release-preview-compile-dryrun.md)
- Preview target manifest: [`config/preview-release-targets.json`](../config/preview-release-targets.json) · canonical doc [`docs/preview-release-targets.md`](preview-release-targets.md)
- Release-eligibility source of truth: [`config/webflash-builds.json`](../config/webflash-builds.json)
- WebFlash contract: [`docs/webflash-contract.md`](webflash-contract.md)
- Release matrix / WebFlash alignment: [`docs/release-matrix-webflash-alignment.md`](release-matrix-webflash-alignment.md)
- Detailed PR queue: [`UPCOMING_PR.md`](../UPCOMING_PR.md)

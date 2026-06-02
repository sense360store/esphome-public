# Preview WebFlash build rows — readiness record

**Canonical id:** `RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001`
**Date:** 2026-06-02
**Type:** Adds the three reviewed `config/webflash-builds.json` **preview** build
rows for the compile-validated room-bundle preview targets that already have
`products/webflash` wrappers, and flips their `config/product-catalog.json`
rows `blocked` → `preview` so the build-matrix ↔ catalog cross-check stays
consistent. This PR **publishes no firmware**, creates **no** GitHub Release /
tag / checksum, commits **no** `.bin`, writes **no** `firmware/sources.json` /
`manifest.json`, touches **no** WebFlash repo, marks **nothing** stable, adds
**no** TRIAC row, adds **no** fan manual-preview row, changes the launch SKU
away from **`S360-KIT-BATH-P`** **not at all**, and claims **no** hardware /
bench / compliance / commercial-availability proof.

**Predecessors:**

- `#695` `RELEASE-PREVIEW-COMPILE-RESULTS-001` recorded hosted compile run
  `26821900127` as GREEN firmware-build proof for the preview matrix.
- `#696` `RELEASE-PREVIEW-WEBFLASH-WRAPPERS-001` added the three
  `products/webflash` wrappers
  ([`docs/release-preview-webflash-wrappers.md`](release-preview-webflash-wrappers.md)).
- `#697` `SHOP-COMMERCIAL-SOURCE-OF-TRUTH-001` locked the commercial source of
  truth: launch SKU `S360-KIT-BATH-P`, candidate bundles hidden / not buyable,
  customer WebFlash URL `https://flash.sense360.com`
  ([`docs/shop-commercial-source-of-truth.md`](shop-commercial-source-of-truth.md)).

---

## TL;DR

* **Three preview build rows added** to
  [`config/webflash-builds.json`](../config/webflash-builds.json) — the sole
  WebFlash release-eligibility source of truth — taking the ledger from **2** to
  **5** builds (one stable, four preview). Each new row is on the **preview**
  (non-stable) channel and is addressed via its `products/webflash` wrapper.
* **Metadata only.** Each row records `release_state:
  metadata-ready-unpublished`. No firmware binary, GitHub Release, tag,
  `manifest.json`, or `firmware/sources.json` is produced. The consuming
  candidate bundles stay **hidden / not buyable**.
* **Evidence is firmware-build only.** Each row cites hosted Preview Compile
  Dry-Run run `26821900127` (`proof_class: firmware-build-only`). A green
  compile is **not** hardware proof, bench evidence, compliance, stable
  promotion, or commercial availability.
* **Catalog flipped `blocked` → `preview`** for the three configs (with
  `webflash_build_matrix: true`, `webflash_wrapper`, `artifact_name`), because
  `tests/test_product_catalog.py` requires every `webflash-builds.json` entry to
  map to a `production` / `preview` catalog row. Nothing is marked
  `production` / `stable` / hardware-verified.
* **Stable is untouched.** The only stable Release-One target remains
  `Ceiling-POE-VentIQ-RoomIQ`. The published VentIQ LED preview
  (`Ceiling-POE-VentIQ-RoomIQ-LED`) is unchanged.

---

## 1. Build rows added

| WebFlash config string | `product_yaml` (wrapper) | Channel | Artifact | Consuming candidate bundle(s) |
|---|---|---|---|---|
| `Ceiling-POE-AirIQ-RoomIQ` | `products/webflash/ceiling-poe-airiq-roomiq.yaml` | `preview` | `Sense360-Ceiling-POE-AirIQ-RoomIQ-v1.0.0-preview.bin` | `S360-KIT-KITCHEN-P` |
| `Ceiling-POE-RoomIQ` | `products/webflash/ceiling-poe-roomiq.yaml` | `preview` | `Sense360-Ceiling-POE-RoomIQ-v1.0.0-preview.bin` | `S360-KIT-BEDROOM-P` |
| `Ceiling-POE-RoomIQ-LED` | `products/webflash/ceiling-poe-roomiq-led.yaml` | `preview` | `Sense360-Ceiling-POE-RoomIQ-LED-v1.0.0-preview.bin` | `S360-KIT-LIVING-P`, `S360-KIT-CORRIDOR-P` |

Artifact names follow the contract pattern
`Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin` and round-trip through
`scripts/product_name_mapper.py` (the mapper gained explicit entries for the
three stems and an `"led" -> "LED"` acronym so the `RoomIQ-LED` artifact reads
`-RoomIQ-LED-`, not `-RoomIQ-Led-`). Each row carries the **preview**
`release_note_warning`, a `stable_blocker`, a `commercial_posture` block
(`hidden` / `candidate` / not buyable / not recommended / not default / not
stable), and a `compile_evidence` block pointing at run `26821900127`.

`Ceiling-POE-RoomIQ-LED` is the **RoomIQ + LED** sibling shared by the
Living-room and Corridor bundles; it is **distinct** from the already-published
LED preview `Ceiling-POE-VentIQ-RoomIQ-LED`, which is unchanged.

---

## 2. Catalog changes (`config/product-catalog.json`)

For each of the three configs the lifecycle entry moves from `status: blocked`
(blocker `PRODUCT-POE-410-001`) to:

* `status: preview`, `channel: preview`, `version: 1.0.0`;
* `webflash_build_matrix: true`, `webflash_wrapper` + `artifact_name` declared;
* `target_channel` preserved (`stable-candidate` for AirIQ-RoomIQ / RoomIQ,
  `preview-candidate` for RoomIQ-LED — LED stays preview);
* `hardware_status: authored-preview-unverified-s360-410-pending` (not
  verified);
* `blocker` / `reason` removed (no longer a `blocked` entry); the S360-410
  caveat is preserved in `stable_blocker` + `notes`.

This is the minimum required by the build-matrix ↔ catalog cross-check. No entry
is marked `production`, `stable`, hardware-verified, or buyable. S360-410
(`S360-410`) stays `cataloged_unverified` in
[`config/hardware-catalog.json`](../config/hardware-catalog.json).

---

## 3. Preview target manifest (`config/preview-release-targets.json`)

The three webflash-lane targets move from `publication_status:
eligible-unpublished` to **`webflash-preview-metadata-ready`** (the reviewed
build row now exists), and their `build_blocker` for "needs a reviewed
`config/webflash-builds.json` row" is **resolved** (`build_blocker: null`). They
stay `preview` / not recommended / not customer-default / not required-config,
keep their `stable_blocker`, and keep `webflash_import_eligibility.eligible`
behind the acknowledgement gate. `scripts/validate_preview_release_targets.py`
gained the `webflash-preview-metadata-ready` ledger-present status so a
metadata-ready target is cross-checked against the build row's channel +
artifact name without being treated as a published / exposed artifact.

---

## 4. What is proven (and what is not)

* **Proven (firmware-build only):** the canonical product YAML for each of the
  three targets compiled GREEN on hosted CI in Preview Compile Dry-Run run
  [`26821900127`](https://github.com/sense360store/esphome-public/actions/runs/26821900127)
  (2026-06-02, ESPHome 2026.4.5). The wrappers re-include exactly those YAMLs.
* **Not proven / not claimed:** hardware operation, bench verification, a
  verified schematic, electrical / mains-safety / EMC compliance, commercial
  availability, or any stable-promotion readiness. Stable stays gated by
  `PRODUCT-POE-410-001` (S360-410 PoE-PSU schematic verification), plus AirIQ
  sensor-stack bench evidence for the Kitchen firmware and the LED
  preview-to-stable gauntlet for the RoomIQ-LED firmware.

---

## 5. Guardrails — what this PR did and did NOT do

It did **not**: publish firmware; create a GitHub Release / tag / checksum;
commit any `.bin`; write `firmware/sources.json` or `manifest.json`; touch the
WebFlash repo; flip anything to `production` / `stable`; mark any candidate
bundle buyable; make any preview row recommended / default; change the launch
SKU away from `S360-KIT-BATH-P`; add a TRIAC row (FanTRIAC stays
`advanced-manual-preview`, blocked by `HW-005`); add a fan manual-preview row
(FanRelay / FanPWM / FanDAC stay on the `manual-preview` lane, off the WebFlash
build matrix); or claim hardware / compliance / commercial-availability proof.

---

## 6. Validation

All commands run from the repo root and pass:

| Command | Result |
|---|---|
| `python3 tests/validate_configs.py` | `✅ All configuration files are valid!` |
| `python3 scripts/validate_compile_targets.py --metadata-only` | `✅ Metadata validation passed.` |
| `python3 scripts/validate_preview_release_targets.py --metadata-only` | `✅ … validation passed.` (9 targets) |
| `python3 tests/test_product_catalog.py` | `OK` |
| `python3 tests/validate_webflash_builds.py` | `5 build(s) checked, 0 failed` → `✅ …valid!` |
| `python3 tests/test_preview_webflash_wrappers.py` | `OK` |
| `python3 tests/test_shop_commercial_source_of_truth.py` | `OK` |
| `python3 -m unittest discover -s tests -p "test_*.py"` | `OK` |

---

## Cross-references

- Preview WebFlash wrappers: [`docs/release-preview-webflash-wrappers.md`](release-preview-webflash-wrappers.md)
- Compile dry-run record: [`docs/release-preview-compile-dryrun.md`](release-preview-compile-dryrun.md)
- Release-eligibility source of truth: [`config/webflash-builds.json`](../config/webflash-builds.json)
- Preview target manifest: [`config/preview-release-targets.json`](../config/preview-release-targets.json)
- Commercial source of truth: [`docs/shop-commercial-source-of-truth.md`](shop-commercial-source-of-truth.md)
- Release matrix / WebFlash alignment: [`docs/release-matrix-webflash-alignment.md`](release-matrix-webflash-alignment.md)
- Canonical roadmap / status: [`docs/sense360-roadmap-status.md`](sense360-roadmap-status.md)

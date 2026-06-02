# Preview WebFlash release-note drafts — dry-run record

**Canonical id:** `RELEASE-PREVIEW-RELEASE-NOTES-DRYRUN-001`
**Date:** 2026-06-02
**Type:** Generates and validates **release-note drafts** for the three
metadata-ready preview WebFlash build rows. This PR is **release-note dry-run
only**: it **publishes no firmware**, creates **no** GitHub Release / tag /
checksum, commits **no** `.bin`, writes **no** `firmware/sources.json` /
`manifest.json`, touches **no** WebFlash repo, marks **nothing** stable, makes
**no** preview build recommended / default, exposes **no** candidate bundle as
buyable, adds **no** TRIAC row, adds **no** fan manual-preview row, changes the
launch SKU away from **`S360-KIT-BATH-P`** **not at all**, and claims **no**
hardware / bench / compliance / commercial-availability proof.

**Predecessors:**

- `#695` `RELEASE-PREVIEW-COMPILE-RESULTS-001` recorded hosted compile run
  `26821900127` as GREEN firmware-build proof for the preview matrix.
- `#696` `RELEASE-PREVIEW-WEBFLASH-WRAPPERS-001` added the three
  `products/webflash` wrappers.
- `#698` `RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001` added the three reviewed
  **preview** rows to
  [`config/webflash-builds.json`](../config/webflash-builds.json)
  ([`docs/release-preview-webflash-build-rows.md`](release-preview-webflash-build-rows.md)).

---

## TL;DR

* **Three release-note drafts added** under
  [`docs/release-notes/preview/`](release-notes/preview/) — one per
  metadata-ready preview build row — each **validated** against the WebFlash
  release-body contract with
  [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py)
  on the `preview` channel (four required H2 sections present and non-empty).
* **Drafts, not releases.** Each draft is explicitly a **DRY-RUN DRAFT** and is
  **not** attached to any GitHub Release. No firmware binary, GitHub Release,
  tag, `manifest.json`, or `firmware/sources.json` is produced.
* **Every draft states the preview posture in plain words:** PREVIEW firmware;
  **not** stable; **not** recommended; **not** a customer default; **not**
  hardware verified; **not** buyable as a public shop product; **firmware-build
  proof only**, citing hosted compile run
  [`26821900127`](https://github.com/sense360store/esphome-public/actions/runs/26821900127);
  **no** hardware / bench / compliance / commercial-availability proof claimed;
  and it points normal customers to the **stable Bathroom PoE release**
  (`S360-KIT-BATH-P` / `Ceiling-POE-VentIQ-RoomIQ`).
* **Validation guard added:**
  [`tests/test_preview_release_notes_drafts.py`](../tests/test_preview_release_notes_drafts.py)
  locks draft coverage, warning copy, the compile-evidence reference, the
  hidden / not-buyable commercial posture, and the absence of any
  stable / recommended / default language — for **every** preview build row.
* **Stable + published LED preview untouched.** The stable Bathroom release
  (`Ceiling-POE-VentIQ-RoomIQ`, `v1.0.0`) and the published VentIQ LED preview
  (`Ceiling-POE-VentIQ-RoomIQ-LED`, `v1.0.0-led-preview`) are **not** re-drafted;
  their published bodies / proof in
  [`docs/webflash-release-proof.md`](webflash-release-proof.md) are unchanged.

---

## 1. Drafts added

| WebFlash config string | Draft | Channel | Artifact (preview) | Consuming candidate bundle(s) |
|---|---|---|---|---|
| `Ceiling-POE-AirIQ-RoomIQ` | [`docs/release-notes/preview/ceiling-poe-airiq-roomiq.md`](release-notes/preview/ceiling-poe-airiq-roomiq.md) | `preview` | `Sense360-Ceiling-POE-AirIQ-RoomIQ-v1.0.0-preview.bin` | `S360-KIT-KITCHEN-P` |
| `Ceiling-POE-RoomIQ` | [`docs/release-notes/preview/ceiling-poe-roomiq.md`](release-notes/preview/ceiling-poe-roomiq.md) | `preview` | `Sense360-Ceiling-POE-RoomIQ-v1.0.0-preview.bin` | `S360-KIT-BEDROOM-P` |
| `Ceiling-POE-RoomIQ-LED` | [`docs/release-notes/preview/ceiling-poe-roomiq-led.md`](release-notes/preview/ceiling-poe-roomiq-led.md) | `preview` | `Sense360-Ceiling-POE-RoomIQ-LED-v1.0.0-preview.bin` | `S360-KIT-LIVING-P`, `S360-KIT-CORRIDOR-P` |

Each draft carries the four required H2 sections — `## Changelog`,
`## Known Issues`, `## Features`, `## Hardware Requirements` — so it passes the
WebFlash release-body contract, plus a prominent **PREVIEW** warning banner
above them. The `## Features` and `## Hardware Requirements` bullets mirror the
build matrix and product catalog (so a draft cannot drift from the build row).
`Ceiling-POE-RoomIQ-LED` is the **RoomIQ + LED** sibling shared by the
Living-room and Corridor bundles; it is **distinct** from the already-published
VentIQ LED preview `Ceiling-POE-VentIQ-RoomIQ-LED`, which is unchanged.

---

## 2. What every draft must say (and the guard that enforces it)

[`tests/test_preview_release_notes_drafts.py`](../tests/test_preview_release_notes_drafts.py)
asserts, for **every** preview WebFlash build row, that release-note coverage
exists and is honest:

| Requirement | How it is enforced |
|---|---|
| **Draft coverage** for every preview row | Metadata-ready rows (`release_state: metadata-ready-unpublished`) each have a `docs/release-notes/preview/<config>.md`; the published VentIQ LED preview is covered by its recorded release proof and is *not* re-drafted. |
| **Structural contract** | `scripts/validate-webflash-release-notes.py` `validate_body(..., channel="preview")` returns no errors; the four required H2 sections are present and non-empty. |
| **PREVIEW warning copy** | Whitespace-normalised body must contain: *preview firmware*, *not stable*, *not recommended*, *not a customer default*, *not hardware verified*, *not buyable as a public shop product*, *firmware-build proof only*, *no hardware, bench, compliance, or commercial-availability proof*, and *stable Bathroom PoE release*. |
| **Compile-evidence reference** | Each draft cites hosted compile run `26821900127`; each build row carries a `compile_evidence` block (`run_id: 26821900127`, `proof_class: firmware-build-only`, `result: success`). |
| **Hidden / not-buyable posture** | Each build row's `commercial_posture` is `hidden` / not buyable / not recommended / not customer-default / not stable. |
| **No stable/recommended/default language** | Every `recommended` mention is `not recommended`; every `default` mention is `not a customer default`; no affirmative stable/recommended/default claim appears; the draft's own artifact is the `-preview.bin` and the only `-stable.bin` it names is the Bathroom cross-reference. |
| **Customer redirect** | Each draft points normal customers to the stable Bathroom PoE release, and the pointer (`S360-KIT-BATH-P` / `Ceiling-POE-VentIQ-RoomIQ` / `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`) matches `config/shop-commercial-source-of-truth.json`. |

---

## 3. What is proven (and what is not)

* **Proven (firmware-build only):** the canonical product YAML for each of the
  three targets compiled GREEN on hosted CI in Preview Compile Dry-Run run
  [`26821900127`](https://github.com/sense360store/esphome-public/actions/runs/26821900127)
  (2026-06-02, ESPHome 2026.4.5), and each draft now validates structurally
  against the release-body contract on the `preview` channel.
* **Not proven / not claimed:** hardware operation, bench verification, a
  verified schematic, electrical / mains-safety / EMC compliance, commercial
  availability, or any stable-promotion readiness. Stable stays gated by
  `PRODUCT-POE-410-001` (S360-410 PoE-PSU schematic verification), plus AirIQ
  sensor-stack bench evidence for the Kitchen firmware and the LED
  preview-to-stable gauntlet for the RoomIQ-LED firmware. A validated draft is
  **not** a published release.

---

## 4. Guardrails — what this PR did and did NOT do

It did **not**: publish firmware; create a GitHub Release / tag / checksum;
commit any `.bin`; write `firmware/sources.json` or `manifest.json`; touch the
WebFlash repo; flip anything to `production` / `stable`; mark any candidate
bundle buyable; make any preview row recommended / default; change the launch
SKU away from `S360-KIT-BATH-P`; add a TRIAC row (FanTRIAC stays
`advanced-manual-preview`, blocked by `HW-005`); add a fan manual-preview row
(FanRelay / FanPWM / FanDAC stay on the `manual-preview` lane, off the WebFlash
build matrix); change the existing stable Bathroom release notes; change the
already-published Bathroom + LED preview release notes; or claim hardware /
bench / compliance / commercial-availability proof. It edits only the new
drafts, the new test, and docs.

---

## 5. Validation

All commands run from the repo root and pass:

| Command | Result |
|---|---|
| `python3 tests/validate_configs.py` | `✅ All configuration files are valid!` |
| `python3 scripts/validate_compile_targets.py --metadata-only` | `✅ Metadata validation passed.` |
| `python3 scripts/validate_preview_release_targets.py --metadata-only` | `✅ … validation passed.` (9 targets) |
| `python3 tests/test_product_catalog.py` | `OK` |
| `python3 tests/validate_webflash_builds.py` | `5 build(s) checked, 0 failed` → `✅ …valid!` |
| `python3 tests/test_shop_commercial_source_of_truth.py` | `OK` |
| `for f in docs/release-notes/preview/ceiling-poe-*.md; do python3 scripts/validate-webflash-release-notes.py "$f" --channel preview; done` | `validation passed (channel=preview)` (each of the 3 drafts) |
| `python3 tests/test_preview_release_notes_drafts.py` | `OK` (27 tests) |
| `python3 -m unittest discover -s tests -p "test_*.py"` | `OK` |

---

## Cross-references

- Preview release-note drafts: [`docs/release-notes/preview/`](release-notes/preview/)
- Preview WebFlash build rows: [`docs/release-preview-webflash-build-rows.md`](release-preview-webflash-build-rows.md)
- Preview WebFlash wrappers: [`docs/release-preview-webflash-wrappers.md`](release-preview-webflash-wrappers.md)
- Compile dry-run record: [`docs/release-preview-compile-dryrun.md`](release-preview-compile-dryrun.md)
- Release-eligibility source of truth: [`config/webflash-builds.json`](../config/webflash-builds.json)
- Release-note generator / validator: [`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py) · [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py)
- Published stable + LED preview release proof: [`docs/webflash-release-proof.md`](webflash-release-proof.md)
- Commercial source of truth: [`docs/shop-commercial-source-of-truth.md`](shop-commercial-source-of-truth.md)
- Release matrix / WebFlash alignment: [`docs/release-matrix-webflash-alignment.md`](release-matrix-webflash-alignment.md)
- Canonical roadmap / status: [`docs/sense360-roadmap-status.md`](sense360-roadmap-status.md)

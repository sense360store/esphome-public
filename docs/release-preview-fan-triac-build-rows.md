# Fan-control & TRIAC preview build rows — readiness record

**Canonical id:** `RELEASE-PREVIEW-FAN-TRIAC-BUILD-ROWS-001`
**Date:** 2026-06-03
**Type:** Adds the concrete **preview / advanced-preview build-row ledger** and
**release-note drafts** for the four remaining buildable fan-control and TRIAC
firmware targets, on the **non-WebFlash** preview lanes (`manual-preview` for
FanRelay / FanPWM / FanDAC, `advanced-manual-preview` for FanTRIAC). This PR
**publishes no firmware**, creates **no** GitHub Release / tag / checksum,
commits **no** `.bin`, writes **no** `firmware/sources.json` / `manifest.json`,
touches **no** WebFlash repo, adds **no** `config/webflash-builds.json` row,
flips **no** `config/product-catalog.json` status, marks **nothing** stable /
recommended / default / buyable, changes Simple install / the launch SKU
**`S360-KIT-BATH-P`** **not at all**, makes **no** TRIAC safety / compliance
claim, and claims **no** hardware / bench / compliance proof (and **no compile
proof for FanTRIAC**, which is build-blocked).

**Predecessors:**

- `#702` `RELEASE-PREVIEW-UNBLOCK-ALL-BUNDLES-001` made hardware / bench /
  compliance / commercial blockers **stable-only** so preview is allowed for
  every buildable target; only a genuine buildability blocker (HW-005 for TRIAC)
  can stop a preview cut
  ([`docs/release-channel-policy.md`](release-channel-policy.md),
  [`docs/preview-release-targets.md`](preview-release-targets.md)).
- `#695` `RELEASE-PREVIEW-COMPILE-RESULTS-001` recorded hosted compile run
  `26821900127` as GREEN firmware-build proof, including the three fan drivers
  ([`docs/release-preview-compile-dryrun.md`](release-preview-compile-dryrun.md)).

---

## TL;DR

* **A new build-row ledger** at
  [`config/preview-fan-triac-build-rows.json`](../config/preview-fan-triac-build-rows.json)
  enumerates **four** rows — the manual / advanced-manual analog of
  `config/webflash-builds.json`. `config/webflash-builds.json` stays the **sole
  WebFlash release-eligibility source of truth**; **no fan / TRIAC row is added
  there** (the fan-token guardrail keeps fan / TRIAC tokens off the WebFlash
  build matrix).
* **Four release-note drafts** under
  [`docs/release-notes/manual-preview/`](release-notes/manual-preview/), each
  validated on the **preview** channel against the WebFlash release-body
  contract, kept **separate** from the WebFlash preview drafts in
  [`docs/release-notes/preview/`](release-notes/preview/).
* **FanRelay / FanPWM / FanDAC** are **firmware-build proof only** (run
  `26821900127`, `proof_class: firmware-build-only`) and are delivered on the
  `manual-preview` lane (`config/manual-firmware-artifacts.json`). A green
  compile is **not** hardware proof, bench evidence, compliance, stable
  promotion, or commercial availability.
* **FanTRIAC** is **advanced-manual-preview only** and **build-blocked by
  `HW-005`** — not buildable end-to-end, so **no compile / firmware artifact
  exists** and **none is cut**. Its row claims **no compile proof**; its draft
  carries the mandatory **mains-voltage** / AC-load warning and the
  installer-only, advanced-manual posture, and it is **not** forced into the
  normal WebFlash preview path.
* **Nothing becomes stable / recommended / default / buyable.** Simple install
  stays the stable Bathroom PoE build (`Ceiling-POE-VentIQ-RoomIQ`,
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, `S360-KIT-BATH-P`).

---

## 1. Build rows added (`config/preview-fan-triac-build-rows.json`)

| Config string | Family | Lane | Channel | Expected artifact | Build status |
|---|---|---|---|---|---|
| `Ceiling-POE-VentIQ-FanRelay-RoomIQ` | FanRelay (S360-310) | `manual-preview` | preview | `Sense360-Ceiling-POE-VentIQ-FanRelay-RoomIQ-v1.0.0-preview.bin` | buildable — run `26821900127` |
| `Ceiling-POE-FanPWM` | FanPWM (S360-311) | `manual-preview` | preview | `Sense360-Ceiling-POE-FanPWM-v1.0.0-preview.bin` | buildable — run `26821900127` |
| `Ceiling-POE-FanDAC` | FanDAC (S360-312) | `manual-preview` | preview | `Sense360-Ceiling-POE-FanDAC-v1.0.0-preview.bin` | buildable — run `26821900127` |
| `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` | FanTRIAC (S360-320) | `advanced-manual-preview` | advanced-preview | `Sense360-Ceiling-POE-VentIQ-FanTRIAC-RoomIQ-v1.0.0-preview.bin` | **build-blocked — `HW-005`** |

Each row carries the policy `release_note_warning` + `warning_copy_key`, a
`release_note_draft` pointer, a `stable_blocker`, a `commercial_posture` block
(`hidden` / `candidate` / not buyable / not recommended / not customer-default /
not stable / not required-config), and `webflash_importable: false`. Artifact
names follow `Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin`. Each row
cross-references its `config/preview-release-targets.json` target (by
`preview_release_target_id`) and — for the three fan drivers — its
`config/manual-firmware-artifacts.json` candidate (by `manual_lane_candidate_id`).
The ledger validator
([`scripts/validate_preview_fan_triac_build_rows.py`](../scripts/validate_preview_fan_triac_build_rows.py))
enforces all of these cross-checks so the ledger can never drift from the
canonical sources.

The three fan drivers carry a `compile_evidence` block (run `26821900127`,
`proof_class: firmware-build-only`, `result: success`, with the per-target
compile sub-job id). The TRIAC row carries `compile_evidence: null`,
`build_blocker` (`HW-005`), `buildable_now: false`, and
`compile_status: build-blocked-no-compile-proof`.

---

## 2. Release-note drafts (`docs/release-notes/manual-preview/`)

| Config string | Draft |
|---|---|
| `Ceiling-POE-VentIQ-FanRelay-RoomIQ` | [`ceiling-poe-ventiq-fanrelay-roomiq.md`](release-notes/manual-preview/ceiling-poe-ventiq-fanrelay-roomiq.md) |
| `Ceiling-POE-FanPWM` | [`ceiling-poe-fanpwm.md`](release-notes/manual-preview/ceiling-poe-fanpwm.md) |
| `Ceiling-POE-FanDAC` | [`ceiling-poe-fandac.md`](release-notes/manual-preview/ceiling-poe-fandac.md) |
| `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` | [`ceiling-poe-ventiq-fantriac-roomiq.md`](release-notes/manual-preview/ceiling-poe-ventiq-fantriac-roomiq.md) |

Every draft has the four required H2 sections (`## Changelog`, `## Known
Issues`, `## Features`, `## Hardware Requirements`) and validates with
`scripts/validate-webflash-release-notes.py --channel preview`. Every draft
states, in plain words, that it is **PREVIEW** firmware — not stable, not
recommended, not a customer default, not hardware verified, not compliance
certified, and not buyable as a public shop product — and points normal
customers to the **stable Bathroom PoE release**. The fan drafts state
**firmware-build proof only** (run `26821900127`); the TRIAC draft states the
**mains-voltage / AC-load risk**, the **installer-only / advanced-manual**
posture, and that it is **not yet buildable** (`HW-005`) with **no compile,
hardware, bench, or compliance proof**.

---

## 3. What is proven (and what is not)

* **Proven (firmware-build only):** `products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`,
  `products/sense360-ceiling-poe-fanpwm.yaml`, and
  `products/sense360-ceiling-poe-fandac.yaml` compiled GREEN on hosted CI in
  Preview Compile Dry-Run run
  [`26821900127`](https://github.com/sense360store/esphome-public/actions/runs/26821900127)
  (2026-06-02, ESPHome 2026.4.5).
* **Not proven / not claimed:** any FanTRIAC compile (it is build-blocked by
  `HW-005`), hardware operation, bench verification, a verified schematic,
  electrical / mains-safety / EMC compliance, commercial availability, or any
  stable-promotion readiness. Stable stays gated per target — mains-safety /
  installation-approval + competent-person sign-off + GPIO3 strap-pin
  characterisation (FanRelay); measured current / thermal (FanPWM); Cloudlift
  S12 / J3 harness + S360-312 schematic (FanDAC); `HW-005` + `PACKAGE-TRIAC-001`
  + `COMPLIANCE-001` mains-voltage review (FanTRIAC).

---

## 4. Guardrails — what this PR did and did NOT do

It did **not**: publish firmware; create a GitHub Release / tag / checksum;
commit any `.bin`; write `firmware/sources.json` or `manifest.json`; touch the
WebFlash repo (including its `manifest.json` / `firmware/sources.json`); add a
`config/webflash-builds.json` row for any fan / TRIAC config; flip a
`config/product-catalog.json` status; mark any target stable / recommended /
default; expose any candidate bundle as buyable; change Simple install or the
launch SKU `S360-KIT-BATH-P`; make TRIAC stable / recommended / default; claim
TRIAC safety / compliance proof; make any fan-control product stable; or claim
hardware / bench / compliance proof (and no compile proof is claimed for the
build-blocked FanTRIAC).

---

## 5. Validation

All commands run from the repo root and pass:

| Command | Result |
|---|---|
| `python3 tests/validate_configs.py` | `✅ All configuration files are valid!` |
| `python3 scripts/validate_compile_targets.py --metadata-only` | `✅ Metadata validation passed.` |
| `python3 scripts/validate_preview_release_targets.py --metadata-only` | `✅ … validation passed.` |
| `python3 scripts/validate_preview_fan_triac_build_rows.py --metadata-only` | `✅ … ledger validation passed.` |
| `python3 tests/test_product_catalog.py` | `OK` |
| `python3 tests/validate_webflash_builds.py` | `✅ …valid!` (no fan / TRIAC row added) |
| `python3 tests/test_shop_commercial_source_of_truth.py` | `OK` |
| `python3 tests/test_preview_fan_triac_build_rows.py` | `OK` |
| `python3 -m unittest discover -s tests -p "test_*.py"` | `OK` |
| `scripts/validate-webflash-release-notes.py … --channel preview` (×4 drafts) | `passed` |

---

## Cross-references

- Build-row ledger: [`config/preview-fan-triac-build-rows.json`](../config/preview-fan-triac-build-rows.json)
- Release-note drafts: [`docs/release-notes/manual-preview/`](release-notes/manual-preview/)
- Preview target manifest: [`config/preview-release-targets.json`](../config/preview-release-targets.json) · [`docs/preview-release-targets.md`](preview-release-targets.md)
- Release-channel policy: [`config/release-channel-policy.json`](../config/release-channel-policy.json) · [`docs/release-channel-policy.md`](release-channel-policy.md)
- Manual fan lane: [`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json) · [`docs/manual-install-fan-candidates.md`](manual-install-fan-candidates.md)
- Compile dry-run record: [`docs/release-preview-compile-dryrun.md`](release-preview-compile-dryrun.md)
- WebFlash release-eligibility source of truth: [`config/webflash-builds.json`](../config/webflash-builds.json)
- Commercial source of truth: [`docs/shop-commercial-source-of-truth.md`](shop-commercial-source-of-truth.md)
- Release matrix / WebFlash alignment: [`docs/release-matrix-webflash-alignment.md`](release-matrix-webflash-alignment.md)

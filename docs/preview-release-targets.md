# Preview Release Targets — Concrete Targets for All Buildable Products (RELEASE-PREVIEW-TARGETS-ALL-PRODUCTS-001)

**Canonical id:** `RELEASE-PREVIEW-TARGETS-ALL-PRODUCTS-001`
**Date:** 2026-06-01
**Type:** Config + docs only. This document and its companion
`config/preview-release-targets.json` do **not** change firmware behaviour,
publish any firmware, build or attach any artifact, edit `manifest.json` /
`firmware/sources.json`, add any row to `config/webflash-builds.json`, flip any
`config/product-catalog.json` status, mark anything stable, mark any schematic
verified, claim any bench / compliance / hardware / build evidence, or touch the
WebFlash repo. It records **concrete target metadata** only.

Machine-readable source:
[`config/preview-release-targets.json`](../config/preview-release-targets.json)
→ guarded by
[`tests/test_preview_release_targets.py`](../tests/test_preview_release_targets.py)
and
[`scripts/validate_preview_release_targets.py`](../scripts/validate_preview_release_targets.py).

---

## Purpose

`RELEASE-PREVIEW-ALL-PRODUCTS-001` opened **preview** eligibility to every
buildable Sense360 firmware target and recorded the policy + eligibility matrix
in [`config/release-channel-policy.json`](../config/release-channel-policy.json).
That slice was deliberately *eligibility only* — it published nothing and added
no concrete, CI-consumable target.

This slice is the concrete follow-up. It enumerates **every buildable product**
as a concrete preview / advanced-preview release target carrying, per target:

1. the WebFlash **config string**;
2. the buildable **YAML path**;
3. the **channel** tier (`preview` / `advanced-preview`) and the **build
   channel** suffix (`preview`) the artifact actually uses;
4. the **expected artifact name**
   (`Sense360-{config}-v{version}-{build_channel}.bin`);
5. the **release-note warning text** (from the policy's `warning_copy`);
6. **WebFlash import eligibility** (and the exposure class / reason);
7. the **stable blocker** text; and
8. any **build blocker** that prevents cutting a preview artifact right now.

The driving rule is unchanged from the policy:

> **Lack of hardware proof blocks _stable only_. It does _not_ block preview
> artifact publication.**

`config/webflash-builds.json` remains the **sole release-eligibility source of
truth**. This manifest never adds a row to it; cutting an actual build row stays
a separate, proof-bearing, per-target step.

---

## What "concrete target" means — and does not mean

- **It means:** a buildable target is recorded with everything CI needs to know
  *which* channel, *which* artifact name, *which* warning, *which* lane, and
  *what* (if anything) is still blocking a preview cut.
- **It does *not* mean:** the target is built, published, WebFlash-imported,
  hardware verified, stable, recommended, a default, or a REQUIRED_CONFIG.
- **No build proof is claimed.** No `esphome` CLI was available in the
  environment that produced this manifest, so every target that cannot be cut
  now records an explicit `build_blocker`. `compile_validation_status` evidence
  is cited from the existing `config/compile-only-targets.json` lane only; it is
  not re-claimed here.

---

## Delivery lanes

> **`RELEASE-PREVIEW-WEBFLASH-ALL-BUILDABLE-001`:** every buildable product is a
> preview / advanced-preview **release** target. The fan and TRIAC targets are no
> longer framed as passive `manual-candidate-only` / `blocked` — they are real
> preview release targets delivered on the `manual-preview` /
> `advanced-manual-preview` lanes. **WebFlash one-click import** stays a separate,
> controlled follow-up; the preview **artifact** is releasable now.

| Lane | Meaning |
|---|---|
| `webflash` | Preview / advanced-preview artifact published as a WebFlash-importable build (`config/webflash-builds.json` row + `products/webflash` wrapper + recorded build proof) behind the acknowledgement gate. `config/webflash-builds.json` stays the sole WebFlash release-eligibility source of truth. |
| `manual-preview` | Buildable **preview** artifact released to testers via the manual-preview lane (`config/manual-firmware-artifacts.json`). A real preview release target, **not** a passive candidate. WebFlash import stays gated until the WebFlash warning UX supports fan preview exposure (separate follow-up); the preview artifact itself is releasable. |
| `advanced-manual-preview` | Advanced (mains-risk) preview lane for TRIAC: `manual-preview` plus the mandatory mains-risk warning and competent-person manual install. Preview is allowed in principle; only an explicit **build blocker** (HW-005 buildability) prevents an actual cut. WebFlash import gated behind the advanced acknowledgement UX (separate follow-up). |

Fan-driver firmware (FanRelay / FanPWM / FanDAC) is a **`manual-preview`** release
target. WebFlash one-click import is still gated by existing repo guardrails:
`scripts/list_release_targets.py` refuses a fan token in the release matrix and
the catalog keeps `webflash_build_matrix=false`, so fan drivers do **not** appear
in `config/webflash-builds.json` until the WebFlash warning UX is ready. FanTRIAC
is **advanced-preview** on the **`advanced-manual-preview`** lane — no longer
`blocked` from preview; only the `HW-005` *buildability* blocker prevents a cut.
Neither family is WebFlash-importable **yet**, so neither appears in
`config/webflash-builds.json`.

---

## Target matrix

| Config string | Tier | Lane | WebFlash import | Status |
|---|---|---|---|---|
| `Ceiling-POE-VentIQ-RoomIQ` | stable | webflash | yes | published-stable (baseline; unchanged) |
| `Ceiling-POE-VentIQ-RoomIQ-LED` | preview | webflash | yes | published-preview |
| `Ceiling-POE-AirIQ-RoomIQ` | preview | webflash | yes | eligible-unpublished |
| `Ceiling-POE-RoomIQ` | preview | webflash | yes | eligible-unpublished (preview allowed; **stable** blocked by S360-410) |
| `Ceiling-POE-RoomIQ-LED` | preview | webflash | yes once product YAML exists | eligible-needs-product-yaml |
| `Ceiling-POE-VentIQ-FanRelay-RoomIQ` | preview | manual-preview | gated follow-up | manual-preview-eligible |
| `Ceiling-POE-FanPWM` | preview | manual-preview | gated follow-up | manual-preview-eligible |
| `Ceiling-POE-FanDAC` | preview | manual-preview | gated follow-up | manual-preview-eligible |
| `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` | advanced-preview | advanced-manual-preview | gated follow-up | advanced-manual-preview-build-blocked (HW-005 buildability) |

Every buildable target is a preview / advanced-preview release target:

- The **WebFlash** lane targets are import-eligible; the LED preview is already
  published (proving the WebFlash matrix may carry a preview without stable
  promotion), and the others need a wrapper / product YAML before a row is cut.
- The **`manual-preview`** fan targets are releasable preview artifacts via the
  manual lane now; only their WebFlash one-click import is a gated follow-up.
- The **`advanced-manual-preview`** TRIAC target is preview-allowed; only the
  `HW-005` *buildability* blocker (not a lack of stable evidence) stops a cut.

No target is `blocked from preview`, and none claims hardware / bench /
compliance / verified-schematic evidence (see the JSON).

---

## TRIAC (advanced-preview)

`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` is **advanced-preview only**, on the
**`advanced-manual-preview`** lane:

- it carries the mandatory **mains-risk** warning copy
  (`warning_copy.advanced-preview`);
- it is **not recommended**, **not a default**, **not a REQUIRED_CONFIG**, and
  **not a customer-kit default**;
- it is **not stable** and **not (yet) WebFlash-importable** (WebFlash import is
  a gated follow-up, `WF-IMPORT-TRIAC-001`);
- it is **no longer `blocked` from preview** — preview is allowed in principle.
  The only thing preventing a cut is the **`HW-005` buildability blocker**
  (S360-320 schematic uncommitted; GPIO5/GPIO6 collision; `ac_dimmer` cannot run
  across the SX1509 expander), **not** a lack of stable evidence. Stable is
  additionally gated by `PACKAGE-TRIAC-001` and `COMPLIANCE-001`. An
  advanced-preview artifact can be cut on the advanced-manual-preview lane once
  `HW-005` resolves.

---

## Validation

```bash
python3 scripts/validate_preview_release_targets.py --metadata-only
python3 tests/test_preview_release_targets.py
```

The manifest is also covered by the repository-wide
`python3 -m unittest discover -s tests -p "test_*.py"` sweep, and it reuses the
policy's `build_channel_mapping` and `warning_copy` verbatim so the two files
can never drift.

---

## Relationship to the other config files

- [`config/release-channel-policy.json`](../config/release-channel-policy.json)
  — the eligibility **policy** this manifest makes concrete.
- [`config/webflash-builds.json`](../config/webflash-builds.json) — the **sole
  release-eligibility source of truth**; carries only the published stable +
  preview builds. A top-level pointer references this manifest.
- [`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json)
  — the **`manual-preview`** delivery lane that produces the FanRelay / FanPWM /
  FanDAC tester-facing preview artifacts; cross-referenced from this manifest. It
  stays non-release in the durable sense (no GitHub Release / WebFlash row), but
  the preview artifact it produces is the releasable fan preview.
- [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json)
  — the generated readiness view; regenerated and unchanged by this slice
  (no build/catalog status flipped).
- [`config/product-catalog.json`](../config/product-catalog.json) — the
  lifecycle layer; **not** modified here.

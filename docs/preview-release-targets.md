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

| Lane | Meaning |
|---|---|
| `webflash` | Permitted into `config/webflash-builds.json` (acknowledgement-gated WebFlash import) once a wrapper + recorded build proof exist. |
| `manual-candidate` | Buildable preview delivered **only** via the non-release manual lane (`config/manual-firmware-artifacts.json`); never WebFlash-exposed. |
| `blocked` | Buildable in principle, but no preview artifact may be cut until the recorded hardware / compliance build blocker clears. |

Fan-driver firmware (FanRelay / FanPWM / FanDAC) is **manual-candidate-only** by
existing repo guardrails: `scripts/list_release_targets.py` refuses a fan token
in the release matrix and the catalog keeps `webflash_build_matrix=false`.
FanTRIAC is **advanced-preview** and **blocked** under `HW-005`. Neither family
is WebFlash-importable, so neither appears in `config/webflash-builds.json`.

---

## Target matrix

| Config string | Tier | Lane | WebFlash import | Status |
|---|---|---|---|---|
| `Ceiling-POE-VentIQ-RoomIQ` | stable | webflash | yes | published-stable (baseline; unchanged) |
| `Ceiling-POE-VentIQ-RoomIQ-LED` | preview | webflash | yes | published-preview |
| `Ceiling-POE-AirIQ-RoomIQ` | preview | webflash | yes | eligible-unpublished |
| `Ceiling-POE-RoomIQ` | preview | webflash | yes | blocked-unpublished (S360-410) |
| `Ceiling-POE-RoomIQ-LED` | preview | webflash | yes | eligible-needs-product-yaml |
| `Ceiling-POE-VentIQ-FanRelay-RoomIQ` | preview | manual-candidate | no | manual-lane-only |
| `Ceiling-POE-FanPWM` | preview | manual-candidate | no | manual-lane-only |
| `Ceiling-POE-FanDAC` | preview | manual-candidate | no | manual-lane-only |
| `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` | advanced-preview | blocked | no | blocked-unpublished (HW-005) |

Only the LED preview is published today; it proves the WebFlash build matrix may
carry a preview target without stable promotion. Every other preview target is
recorded with an explicit `build_blocker` (see the JSON).

---

## TRIAC (advanced-preview)

`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` is **advanced-preview only**:

- it carries the mandatory **mains-risk** warning copy
  (`warning_copy.advanced-preview`);
- it is **not recommended**, **not a default**, **not a REQUIRED_CONFIG**, and
  **not a customer-kit default**;
- it is **not stable** and **not WebFlash-importable**; and
- it is recorded as a **build blocker** under `HW-005` (S360-320 schematic;
  GPIO5/GPIO6 collision; `ac_dimmer` cannot run across the SX1509 expander) plus
  `PACKAGE-TRIAC-001` and `COMPLIANCE-001`. No preview artifact may be cut until
  those clear.

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
  — the non-release lane that actually builds the FanRelay / FanPWM / FanDAC
  preview targets; cross-referenced from this manifest.
- [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json)
  — the generated readiness view; regenerated and unchanged by this slice
  (no build/catalog status flipped).
- [`config/product-catalog.json`](../config/product-catalog.json) — the
  lifecycle layer; **not** modified here.

# Feature & Entity Matrix (FEATURE-ENTITY-MATRIX-001)

> **Workstream C of `PRE-HARDWARE-PREP-PLAN-001` (feature and entity
> completeness).** This document and its companion source-of-truth
> [`config/feature-entity-matrix.json`](../config/feature-entity-matrix.json)
> establish, for the first time, a per-board / per-module record of which
> Home Assistant **sensor entities** and **product HA features** each
> Sense360 YAML is supposed to expose, and audit that record against the
> YAML that exists today.

## Purpose and scope

Beyond pin-map and firmware bring-up (Workstreams A/B), each board /
module YAML must expose the **correct sensors** and the **intended Home
Assistant features**. Until now there was **no** per-product
feature/entity source of truth in the repo:
[`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json) is
**module composition only** — it maps customer kits onto module SKUs and
firmware config strings, and says nothing about which entities or
features a given board exposes.

This document closes that gap. It:

1. names a new source of truth —
   [`config/feature-entity-matrix.json`](../config/feature-entity-matrix.json) —
   that lists, per board/module, the **required** sensor entities
   (derived from the BOM / schematic / pin-map) and the **required** HA
   features (modes, presets, the LED night-light, fan speed/preset
   controls, etc.);
2. **audits** each row as `present`, `partial`, or `missing` against the
   current YAML; and
3. **queues** the per-board implementation slices that will later fill
   each gap.

### What this document does NOT do

This is **planning and audit only**. It does **not**:

- add, remove, or modify **any entity or feature** in any board, feature,
  expansion, hardware, or product YAML under
  [`packages/`](../packages/) or [`products/`](../products/) — including
  the LED board [`packages/boards/s360-300-led.yaml`](../packages/boards/s360-300-led.yaml)
  used as the worked example below;
- add or change any WebFlash wrapper, `webflash_build_matrix`,
  `artifact_name`, firmware build, or release artifact;
- promote LED, any fan driver, `PWR` / `S360-400`, or `POE` / `S360-410`
  to stable;
- change [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json),
  [`config/hardware-catalog.json`](../config/hardware-catalog.json),
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
  or any other existing config;
- **invent an intended feature set.** Where product intent is not already
  obvious from existing YAML or product docs, the row is recorded as
  `needs-operator-confirm` for the operator to fill.

The actual addition of any missing entity or feature happens in the
**per-board implementation slices** named in each row's
`queued_fill_slice`, never in the PR that introduces this matrix.

## The two row sources (C2)

Every row carries a `derivation` so the two kinds of requirement are not
conflated:

| `derivation`     | Meaning                                                                                                                                                                                                                                          | When it can be filled |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------|
| `design-derived` | Derived from the board BOM / schematic / pin-map. A populated sensor is expected to surface an entity. Fillable **now** from the schematic; fully pinnable once the BOM/gerbers land.                                                            | Now (schematic)       |
| `product-intent` | Product behaviour (modes, presets, dedicated night-light, fan speed/preset UX, exposed comfort indices). **Not** derivable from the schematic. Marked `needs-operator-confirm` wherever intent is not already obvious. The matrix never invents it. | After operator confirm |

### Confirm flags

| `confirm`                  | Meaning                                                                                                                                                              |
|----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `none`                     | Unambiguous from the schematic BOM (design-derived) or already evidenced in YAML/product docs.                                                                        |
| `needs-operator-confirm`   | Product intent is not established — the operator must specify whether the feature/entity is intended before any fill slice may proceed. Do not fabricate it.          |
| `needs-schematic-reconcile`| A design-derived row whose final part/driver/pin is not yet locked (schematic `cataloged_unverified`, BOM/gerbers not landed, or live YAML driver differs from BOM).  |

### Row status (audit verdict)

| `status`  | Meaning                                                                                                                                                                                     |
|-----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `present` | An entity/feature satisfying the row exists in the current YAML (canonical base, or a named overlay where noted).                                                                          |
| `partial` | Partially satisfied: present only in an overlay variant, driver part differs from BOM, declared-but-unvalidated/compile-pending, or only a package-layer output with no user-facing entity. |
| `missing` | No entity/feature satisfying the row exists in any current YAML.                                                                                                                           |

## Audit summary

The full, machine-readable audit lives in
[`config/feature-entity-matrix.json`](../config/feature-entity-matrix.json).
Headline gaps per module:

| Module | SKU | Canonical board pkg | Notable `missing` / `partial` rows |
|--------|-----|---------------------|------------------------------------|
| Core | S360-100 | ✅ `s360-100-core.yaml` | — (relay + health entities present) |
| RoomIQ | S360-200 | ✅ `s360-200-roomiq.yaml` | **missing**: SEN0609 2nd radar, EKMC PIR, BMP581 pressure; **partial**: ALS part (VEML7700 in YAML vs LTR-303ALS in BOM); comfort indices are globals not entities |
| AirIQ | S360-210 | ✅ `s360-210-airiq.yaml` | **missing**: MICS-4514 gas, SFA40 HCHO (SFA40 is the newer Sensirion HCHO module superseding the SFA30; connector interface/address verify-pending) |
| VentIQ | S360-211 | ✅ `s360-211-ventiq.yaml` | **partial**: IR temp (MLX90614) and PM (SPS30) live only in the `-pro` overlay, not the base |
| LED | S360-300 | ✅ `s360-300-led.yaml` | **missing**: dedicated HA night-light light entity (worked example, C3); AQ halo is a layered feature |
| Relay | S360-310 | ❌ none | **partial**: relay proxy only in expansion; no board package |
| PWM | S360-311 | ❌ none | **partial**: fan/tach in expansion, compile-pending; no board package |
| DAC | S360-312 | ❌ none | **partial**: package-layer DAC outputs only, no user entity; no board package |
| TRIAC | S360-320 | ❌ none | **partial**: ac_dimmer BLOCKED (pins + compliance); no board package |
| 240v PSU | S360-400 | ❌ none | **partial**: diagnostics in `power_240v.yaml`; no board package; compliance-blocked |
| PoE PSU | S360-410 | ✅ `s360-410-poe-psu.yaml` | diagnostics present (synthetic values; schematic unverified) |

## Worked example: the LED night-light (C3)

[`packages/boards/s360-300-led.yaml`](../packages/boards/s360-300-led.yaml)
today exposes:

- a `light` **status ring** (`led_ring`, WS2812B) with effects,
- a **Night Mode** template `switch` (`led_night_mode_switch`) that dims
  the ring to 10 %, and
- an **LED Brightness** template `number` (`led_brightness_control`).

It does **not** expose a **dedicated HA night-light `light` entity**
distinct from the status ring. Whether a separate night-light is intended
is **product intent, not a schematic fact** — so the matrix records it as
`missing` with `confirm: needs-operator-confirm`
(`FEATURE-CONFIRM-300-NIGHTLIGHT-001`). It must not be fabricated; the
operator specifies whether a distinct night-light light is wanted before
the fill slice runs.

## How the fills are queued (C4)

Each `missing` / `partial` row names a `queued_fill_slice` (e.g.
`ENTITY-FILL-200-PRESSURE-001`,
`FEATURE-CONFIRM-300-NIGHTLIGHT-001`). Those slices are where the YAML
actually changes, in their own per-board PRs:

- **`design-derived` + `confirm: none`** — ready to fill now from the
  schematic.
- **`needs-schematic-reconcile`** — fill is blocked on the landed
  BOM/gerbers or on resolving a YAML-vs-BOM part mismatch, not on the
  operator.
- **`needs-operator-confirm`** — fill is blocked until the operator
  specifies the intended behaviour.

## Validation

[`tests/test_feature_entity_matrix.py`](../tests/test_feature_entity_matrix.py)
(stdlib `unittest`, matching this repo's no-pytest convention) pins the
matrix invariants: every catalog SKU is covered, enums are constrained,
every non-`present` row names a `queued_fill_slice`, every
`product-intent` gap is `needs-operator-confirm`, and the guardrail flags
stay set. Run it with:

```
python3 tests/test_feature_entity_matrix.py
```

## Related documents

- [`config/feature-entity-matrix.json`](../config/feature-entity-matrix.json) — the source of truth this document describes.
- [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json) / [`docs/kit-intent-matrix.md`](kit-intent-matrix.md) — module **composition** matrix (deliberately separate).
- [`config/hardware-catalog.json`](../config/hardware-catalog.json) / [`docs/hardware-catalog.md`](hardware-catalog.md) — canonical SKU / BOM source.
- [`docs/hardware/board-readiness-matrix.md` (archived)](archive-index.md) and [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md) — pin-map / package readiness gates feeding the `needs-schematic-reconcile` rows.
- Module pin-maps: [`docs/hardware/s360-200-module-pinmap.md`](hardware/s360-200-module-pinmap.md), [`docs/hardware/s360-210-module-pinmap.md`](hardware/s360-210-module-pinmap.md), [`docs/hardware/s360-211-module-pinmap.md`](hardware/s360-211-module-pinmap.md).

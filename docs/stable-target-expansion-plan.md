# Stable Target Expansion Plan (STABLE-TARGET-EXPANSION-PLAN-001)

## Purpose and scope

This document is an **actionable expansion plan** built on top of the
all-YAML release classification in
[`docs/all-yaml-release-matrix.md`](all-yaml-release-matrix.md)
(STABLE-RELEASE-MATRIX-ALL-YAML-001 / PR #629). It answers the
follow-up question that the all-YAML matrix surfaced but did not yet
schedule:

> *"Given the current stable-release matrix has exactly **one** stable
> target (`Ceiling-POE-VentIQ-RoomIQ`) and one preview target
> (`Ceiling-POE-VentIQ-RoomIQ-LED`), which **other** product /
> YAML combos are closest to a real stable promotion, what gates each
> one still needs, and what is the safe next-PR name for each?"*

The plan is deliberately conservative. Nothing here is promoted by
this PR — every row records the exact missing evidence and the
single follow-up PR that would own promotion. The stable matrix in
[`config/webflash-builds.json`](../config/webflash-builds.json) stays
verbatim. The classifier `(stable=1, preview=1, manual=3,
compile-only=7, blocked=1, not-a-product-entrypoint=35)` stays
verbatim.

### Hard guardrails

STABLE-TARGET-EXPANSION-PLAN-001 — this PR — does **not**:

- publish, build, or attach any firmware artifact, and creates no
  GitHub Release;
- commit any `.bin`, checksum, or build-info file;
- edit any YAML under [`products/`](../products/) or
  [`products/webflash/`](../products/webflash/) or
  [`products/compile-only/`](../products/compile-only/);
- add, remove, or modify any entry in
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  [`config/product-catalog.json`](../config/product-catalog.json),
  [`config/compile-only-targets.json`](../config/compile-only-targets.json),
  [`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json),
  or
  [`config/compile-only-candidates.json`](../config/compile-only-candidates.json);
- write [`firmware/sources.json`](../firmware/sources.json) or
  `manifest.json`;
- promote LED from `preview` to `stable`;
- promote FanRelay / FanPWM / FanDAC out of `manual-candidate-only`;
- add an `artifact_name` to any fan product;
- flip any `webflash_build_matrix` value;
- invent unsupported YAML / product combos;
- treat compile-only skeletons as release products;
- claim WebFlash / import / release / hardware-stable / compliance
  readiness for FanRelay / FanPWM / FanDAC / FanTRIAC.

---

## Inputs read

This plan reads from the committed catalogs and the read-only
classifier; nothing is asserted beyond what they record.

| Source | File |
|---|---|
| Release matrix (sole release-eligibility source) | [`config/webflash-builds.json`](../config/webflash-builds.json) |
| Product lifecycle / hardware status | [`config/product-catalog.json`](../config/product-catalog.json) |
| Manual (non-release) artifact lane | [`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json) |
| Compile-only validation lane (registered targets) | [`config/compile-only-targets.json`](../config/compile-only-targets.json) |
| Compile-only expansion candidates (planning ledger) | [`config/compile-only-candidates.json`](../config/compile-only-candidates.json) |
| All-YAML classifier | [`scripts/classify_all_yaml_release_matrix.py`](../scripts/classify_all_yaml_release_matrix.py) |
| Release-target enumerator | [`scripts/list_release_targets.py`](../scripts/list_release_targets.py) |
| Release-notes dry-run planner | [`scripts/plan_room_release_notes.py`](../scripts/plan_room_release_notes.py) |
| Release-notes generator | [`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py) |
| Release-notes validator | [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py) |
| Per-board / per-package readiness | [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md), [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md) |
| Product / WebFlash / Release readiness | [`docs/product-readiness-matrix.md`](product-readiness-matrix.md), [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md), [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md) |
| Preview-to-stable gauntlet | [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md) |
| LED preview decision | [`docs/product-led-preview-decision.md`](product-led-preview-decision.md) |

---

## Current stable / preview surface

For grounding — the verbatim state of the release-eligibility source
of truth on the day this plan is written:

| Config string | Channel | Version | Artifact name |
|---|---|---|---|
| `Ceiling-POE-VentIQ-RoomIQ` | `stable` | `1.0.0` | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` |
| `Ceiling-POE-VentIQ-RoomIQ-LED` | `preview` | `1.0.0` | `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` |

Per `python3 scripts/classify_all_yaml_release_matrix.py --summary`
the 48 product YAMLs classify as:

| Class | Count |
|---|---|
| `stable-release` | 1 |
| `preview-release` | 1 |
| `manual-candidate-only` | 3 |
| `compile-only` | 7 |
| `blocked` | 1 |
| `not-a-product-entrypoint` | 35 |

The expansion plan below proposes **no edits** to any of those counts.

---

## Stable-promotion gate checklist

For any candidate to move into the stable matrix, every row in this
checklist must pass before the corresponding `STABLE-TARGET-*` PR is
opened. The checklist is the operational form of the criteria in
[`docs/all-yaml-release-matrix.md` §Stable-promotion criteria](all-yaml-release-matrix.md#stable-promotion-criteria)
and the
[`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
gauntlet.

| # | Gate | Evidence location |
|---|---|---|
| G1 | **Top-level canonical product YAML exists** under [`products/`](../products/) as `sense360-<config-string-slug>.yaml` (a skeleton in [`products/compile-only/`](../products/compile-only/) does **not** count) | `products/sense360-*.yaml` on disk |
| G2 | **Product-catalog row exists** in [`config/product-catalog.json`](../config/product-catalog.json) with `status: production` (or, for a `preview` first step, `status: preview` + `channel: preview`), the matching `config_string`, `version`, `channel`, `artifact_name`, and `webflash_wrapper` | catalog entry |
| G3 | **Top-level full compile validated** — a [`config/compile-only-targets.json`](../config/compile-only-targets.json) target that points at the top-level product YAML carries `compile_validation_status: validated-full-compile` (not a skeleton-only result) | compile-only target |
| G4 | **WebFlash wrapper exists** under [`products/webflash/`](../products/webflash/) and the catalog row sets `webflash_wrapper` to it (if WebFlash exposure is required for the product) | wrapper YAML |
| G5 | **`artifact_name` is present** in both the catalog row and the matching [`config/webflash-builds.json`](../config/webflash-builds.json) row and matches the `Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin` shape that [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py) accepts | catalog + builds row |
| G6 | **`config/webflash-builds.json` row exists** for the config (`channel: stable` for a stable promotion, `channel: preview` for a preview-first step), referenced by the WebFlash wrapper | builds row |
| G7 | **Release notes can be generated without overrides** — [`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py) does not refuse and [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py) passes structurally; [`scripts/plan_room_release_notes.py`](../scripts/plan_room_release_notes.py) includes the new target with `Validation summary: PASSED` | dry-run output |
| G8 | **No blocking hardware / compliance caveat** — every relevant board carries `schematic_status: verified` (or the per-board readiness matrix records the caveat as `closed`), every relevant package carries `ready-for-package-change`, no [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md) / [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md) / [`docs/product-readiness-matrix.md`](product-readiness-matrix.md) row classifies the family as `not-ready` | per-board / per-package / per-family rows |
| G9 | **Not currently `manual-candidate-only`** — the candidate is not listed in [`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json) and the corresponding per-family slice (`WEBFLASH-RELAY-001` / `RELEASE-RELAY-001`, FanPWM / FanDAC analogues) has cleared first | manual-lane catalog |
| G10 | **Not currently `preview-only`** — if promotion is from `preview` to `stable`, the [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md) 17-row gauntlet has closed (preview-stage bench Open Questions resolved, regression-free preview soak, etc.) | gauntlet record |

---

## Candidate stable additions — actionable table

The candidates below are the **non-fan, non-LED, non-TRIAC room
combos** named by the
[`docs/all-yaml-release-matrix.md` §Candidate stable additions](all-yaml-release-matrix.md#candidate-stable-additions)
"Other room combos" row, plus the already-classified LED and fan
families re-listed for completeness so this table is a one-stop
expansion ledger. Each row records (a) the candidate, (b) the YAML
path, (c) what the source-of-truth catalogs say today, (d) the
desired classification, (e) which gates G1–G10 are missing, (f) the
owner / evidence still required, and (g) the **single safe next PR
name** that would own promotion. None is promoted by this PR.

### A. Non-fan / non-LED / non-TRIAC room combos (the in-scope expansion targets)

These five compile-only skeletons are the **closest** candidates to a
real stable promotion in the sense that every other dimension
(family token grammar, no fan / no LED / no TRIAC blocker, AirIQ ↔
VentIQ mutex respected) is already satisfied by the existing
compile-only skeleton. They are **not** close on the upstream PoE
PSU and per-stack hardware-evidence axis: every one carries the
shared `PRODUCT-POE-410-001` / `S360-410` schematic verification
chain that the existing stable RoomIQ build already inherits as a
Release-One PoE caveat. Promotion order is therefore deliberately
sequential — the smallest skeleton first (`Ceiling-POE`) so the
PoE-410 closure is amortised across the family.

| # | Candidate (config string) | YAML path (today) | Current classification | Desired classification | Missing G-gates (top of stack) | Owner / evidence needed | Safe next PR name |
|---|---|---|---|---|---|---|---|
| A1 | `Ceiling-POE` | [`products/compile-only/ceiling-poe.yaml`](../products/compile-only/ceiling-poe.yaml) | `compile-only` (skeleton; `hardware_required_for_validation: true`) | `stable-release` (after preview soak) | G1, G2, G3 (top-level YAML compile), G4, G5, G6, G7, G8 (`S360-410` `schematic_status: verified`, Release-One PoE caveat closure) | `PRODUCT-POE-410-001` (catalog promotion for an S360-410 PoE-410 explicit entry); `PACKAGE-POE-410-001`; per-board `S360-410-schematic-status-verified` + `S360-410-BOM-evidence` + Release-One PoE caveat closure | **`STABLE-TARGET-CORE-001`** — add the canonical top-level product YAML, catalog row, WebFlash wrapper, builds row, and the matching `compile-only-targets.json` top-level registration. Gated on the PoE-410 chain. |
| A2 | `Ceiling-POE-RoomIQ` | [`products/compile-only/ceiling-poe-roomiq.yaml`](../products/compile-only/ceiling-poe-roomiq.yaml) | `compile-only` (skeleton) | `stable-release` (after preview soak) | G1, G2, G3, G4, G5, G6, G7, G8 (`S360-410` + `S360-200` RoomIQ catalog verified) | `STABLE-TARGET-CORE-001` first (shared PoE-410 closure), then RoomIQ-only product onboarding | **`STABLE-TARGET-ROOMIQ-001`** — RoomIQ-only sibling of A1; depends on A1's PoE-410 closure landing first. |
| A3 | `Ceiling-POE-AirIQ` | [`products/compile-only/ceiling-poe-airiq.yaml`](../products/compile-only/ceiling-poe-airiq.yaml) | `compile-only` (skeleton; AirIQ ↔ VentIQ mutex; AirIQ uses `airiq_ceiling` + `airiq_basic_profile`) | `stable-release` (after preview soak) | G1, G2, G3, G4, G5, G6, G7, G8 (`S360-410` + AirIQ stack hardware evidence: SPS30 / SGP41 / SCD41 / BMP390) | AirIQ-stack hardware evidence (per [`config/compile-only-candidates.json`](../config/compile-only-candidates.json) blockers); `PRODUCT-POE-410-001`; AirIQ catalog onboarding | **`STABLE-TARGET-AIRIQ-001`** — first AirIQ-bearing release product; gated on AirIQ stack hardware evidence and the PoE-410 chain. |
| A4 | `Ceiling-POE-AirIQ-RoomIQ` | [`products/compile-only/ceiling-poe-airiq-roomiq.yaml`](../products/compile-only/ceiling-poe-airiq-roomiq.yaml) | `compile-only` (skeleton; AirIQ ↔ VentIQ mutex) | `stable-release` (after preview soak) | G1, G2, G3, G4, G5, G6, G7, G8 (same as A3 plus RoomIQ catalog verification) | `STABLE-TARGET-AIRIQ-001` first (shared AirIQ stack closure), then RoomIQ-bearing sibling | **`STABLE-TARGET-AIRIQ-ROOMIQ-001`** — AirIQ + RoomIQ sibling; depends on A3 landing first. |
| A5 | `Ceiling-POE-VentIQ` | [`products/compile-only/ceiling-poe-ventiq.yaml`](../products/compile-only/ceiling-poe-ventiq.yaml) | `compile-only` (skeleton; AirIQ ↔ VentIQ mutex; VentIQ uses `airiq_bathroom_base` + `bathroom_profile` — the same VentIQ subset the stable Release-One build already exercises) | `stable-release` (after preview soak) | G1, G2, G3, G4, G5, G6, G7, G8 (`S360-410` + `S360-211` VentIQ schematic verification) | `PRODUCT-POE-410-001`; `VentIQ-S360-211-schematic-verification`; VentIQ-only product onboarding | **`STABLE-TARGET-VENTIQ-001`** — VentIQ-only sibling of the stable Release-One config; the VentIQ subset is already proven by Release-One's catalog row, so the smallest stable-expansion delta in this group. |

**Note on classification today:** all five candidates above are
classified `compile-only` (not `manual-candidate-only`, not
`blocked`) because none has a top-level product YAML, a catalog row,
a WebFlash wrapper, an `artifact_name`, or a
`config/webflash-builds.json` row. That is the correct posture
recorded by the classifier today. The plan does not change it.

### B. Already-`preview` LED candidate (re-listed for completeness — separate slice)

| # | Candidate (config string) | YAML path (today) | Current classification | Desired classification | Missing G-gates | Owner / evidence needed | Safe next PR name |
|---|---|---|---|---|---|---|---|
| B1 | `Ceiling-POE-VentIQ-RoomIQ-LED` | [`products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq-led.yaml) | `preview-release` (channel `preview`, `webflash_build_matrix: true`, `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`) | `stable-release` (LED stable, eventually) | G10 (preview-to-stable gauntlet) — preview-stage S360-300 bench Open Questions still open (LED harness rail, LED count, harness identity); regression-free preview soak | `S360-300-BENCH-001`; `WF-HW-TEST-001`; `WF-HW-TEST-003`; `RELEASE-007`; the full 17-row [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md) gauntlet | **`LED-STABLE-PROMOTION-001`** (alias of the long-standing `PRODUCT-LED-STABLE-001` / `RELEASE-007` plan) — **only** if and when LED bench evidence supports it. Explicitly **not** approved by this PR; LED stays `preview` until the gauntlet closes. |

### C. Manual-fan candidates (re-listed for completeness — separate per-family slices)

These rows are intentionally short. Each fan family has its own
multi-PR chain documented elsewhere; this plan does not duplicate
that ownership.

| # | Candidate (config string) | YAML path (today) | Current classification | Desired classification | Missing G-gates | Owner / evidence needed | Safe next PR name |
|---|---|---|---|---|---|---|---|
| C1 | `Ceiling-POE-VentIQ-FanRelay-RoomIQ` | [`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml) | `manual-candidate-only` | (not in this plan's scope) | G4, G5, G6, G8, G9 — mains-safety / installation / competent-person sign-off; production-wide GPIO3 strap-pin boot characterisation; EMI / EMC; WebFlash manual-warning UX | `WEBFLASH-RELAY-001` then `RELEASE-RELAY-001` then `WF-IMPORT-RELAY-001` | `WEBFLASH-RELAY-001` → `RELEASE-RELAY-001`. **Not promoted by this PR.** Stays manual-candidate-only. |
| C2 | `Ceiling-POE-FanPWM` | [`products/sense360-ceiling-poe-fanpwm.yaml`](../products/sense360-ceiling-poe-fanpwm.yaml) | `manual-candidate-only` | (not in this plan's scope) | G4, G5, G6, G8, G9 — PWM polarity bench; per-fan / aggregate current + thermal envelope; product bench; `S360-311` schematic verification; RPM is `rpm_supported: false` | `WEBFLASH-PWM-001` then `RELEASE-PWM-001` then `WF-IMPORT-PWM-001` | `WEBFLASH-PWM-001` → `RELEASE-PWM-001`. **Not promoted by this PR.** Stays manual-candidate-only. No fan `artifact_name`; no `webflash_build_matrix` flip. |
| C3 | `Ceiling-POE-FanDAC` | [`products/sense360-ceiling-poe-fandac.yaml`](../products/sense360-ceiling-poe-fandac.yaml) | `manual-candidate-only` | (not in this plan's scope) | G4, G5, G6, G8, G9 — Cloudlift S12 harness / product-bench evidence; `S360-312` schematic / BOM verification; FanDAC ↔ AirIQ mutex stays enforced | `WEBFLASH-DAC-001` then `RELEASE-DAC-001` then `WF-IMPORT-DAC-001` | `WEBFLASH-DAC-001` → `RELEASE-DAC-001`. **Not promoted by this PR.** Stays manual-candidate-only. No fan `artifact_name`; no `webflash_build_matrix` flip. |

### D. Blocked TRIAC candidate (re-listed for completeness — long chain)

| # | Candidate (config string) | YAML path (today) | Current classification | Desired classification | Missing G-gates | Owner / evidence needed | Safe next PR name |
|---|---|---|---|---|---|---|---|
| D1 | `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` | [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml) | `blocked` (`HW-005`; reference-only WebFlash wrapper, `webflash_build_matrix: false`) | (not in this plan's scope) | G3, G4, G5, G6, G7, G8 — `HW-005` (S360-320 schematic uncommitted; GPIO5/GPIO6 collide with RoomIQ J10; `ac_dimmer` cannot run across SX1509) + `HW-PINMAP-320-FOLLOWUP` + `PACKAGE-TRIAC-001` + `COMPLIANCE-001` + WebFlash manual-warning UX | Full HW-005 unblock chain | `HW-005` → `PACKAGE-TRIAC-001` → `WEBFLASH-TRIAC-001` → `RELEASE-TRIAC-001`. **Not promoted by this PR.** Stays `blocked`. |

### E. Legacy YAMLs (out of scope)

The 31 `legacy-compatible` YAMLs under `products/sense360-core-*.yaml`,
`products/sense360-core-voice-*.yaml`, `products/sense360-mini-*.yaml`,
`products/sense360-poe.yaml`, and `products/sense360-fan-pwm.yaml`
are explicitly **out of scope** for this expansion plan. They are
pre-WebFlash YAMLs retained for manual / custom users and would
require full re-onboarding through `PRODUCT-GAP-001` /
`WEBFLASH-GAP-001` / `RELEASE-GAP-001`. No legacy YAML is approved
as a stable-expansion candidate by this PR.

---

## Recommended follow-up PR sequence

The follow-up PR names below are the **single owning slice** for each
candidate's promotion. None is approved or scoped by this PR. Each
PR has its own scope, review, and gate-evidence requirements;
landing one PR does not authorise the next.

| Rank | PR name | Scope | Gated on |
|---|---|---|---|
| 1 | **`STABLE-TARGET-VENTIQ-001`** | Promote `Ceiling-POE-VentIQ` from `compile-only` to `stable-release`. Smallest stable-expansion delta — VentIQ subset is already exercised by stable Release-One. Adds top-level `products/sense360-ceiling-poe-ventiq.yaml`, the catalog row, the WebFlash wrapper, the `compile-only-targets.json` top-level registration, the `config/webflash-builds.json` row with `version: 1.0.0` / `channel: stable` / `artifact_name: Sense360-Ceiling-POE-VentIQ-v1.0.0-stable.bin`. | G1–G8 closure: `PRODUCT-POE-410-001`; `S360-410-schematic-status-verified`; `S360-410-BOM-evidence`; Release-One PoE caveat closure; `VentIQ-S360-211-schematic-verification`; preview soak; product-onboarding approval. |
| 2 | **`STABLE-TARGET-CORE-001`** | Promote `Ceiling-POE` (Core-only / base ceiling PoE) from `compile-only` to `stable-release`. Adds the canonical YAML, catalog row, wrapper, top-level compile-only target, and builds row. Shares the PoE-410 closure with all subsequent rows. | G1–G8 closure: `PRODUCT-POE-410-001`; `PACKAGE-POE-410-001`; `S360-410-schematic-status-verified`; `S360-410-BOM-evidence`; Release-One PoE caveat closure; preview soak; product-onboarding approval. |
| 3 | **`STABLE-TARGET-ROOMIQ-001`** | Promote `Ceiling-POE-RoomIQ` (RoomIQ-only) from `compile-only` to `stable-release`. Same scope shape as rank 1/2; depends on `STABLE-TARGET-CORE-001` for the shared PoE-410 closure. | Inherits PoE-410 closure from rank 2; adds RoomIQ-only product-onboarding approval. |
| 4 | **`STABLE-TARGET-AIRIQ-001`** | Promote `Ceiling-POE-AirIQ` from `compile-only` to `stable-release`. First AirIQ-bearing release product. Adds the canonical YAML, catalog row, wrapper, top-level compile-only target, builds row. | Inherits PoE-410 closure; adds AirIQ-stack hardware evidence (SPS30 / SGP41 / SCD41 / BMP390). |
| 5 | **`STABLE-TARGET-AIRIQ-ROOMIQ-001`** | Promote `Ceiling-POE-AirIQ-RoomIQ` from `compile-only` to `stable-release`. AirIQ + RoomIQ sibling of rank 4. | Depends on `STABLE-TARGET-AIRIQ-001` (shared AirIQ stack closure). |
| 6 | **`LED-STABLE-PROMOTION-001`** *(alias of the long-standing `RELEASE-007` / `PRODUCT-LED-STABLE-001` plan)* | Promote `Ceiling-POE-VentIQ-RoomIQ-LED` from `preview-release` to `stable-release`. Updates `version` / `channel` / `artifact_name`; renames the artifact from `-preview.bin` to `-stable.bin`; promotes the catalog `channel` from `preview` to `stable`. | Full 17-row [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md) gauntlet closure, including `S360-300-BENCH-001`, `WF-HW-TEST-001`, `WF-HW-TEST-003`, `RELEASE-007`. **Only if and when LED bench evidence supports it.** |

Per-family fan / TRIAC follow-up PR sequences live in
[`docs/release-artifact-readiness-matrix.md` §Follow-up PR sequence](release-artifact-readiness-matrix.md#follow-up-pr-sequence)
and are not duplicated here.

### Rank 1 status (`STABLE-TARGET-VENTIQ-001`)

Rank 1 — `STABLE-TARGET-VENTIQ-001` — has been investigated against
the G1–G10 gate checklist on 2026-05-28 and the result is recorded in
[`docs/stable-target-ventiq-001-gate-closure.md`](stable-target-ventiq-001-gate-closure.md).
The gate audit finds **9 of 10 gates open today** (only G9 is
closed); the upstream blocker is G8 (`PACKAGE-POE-410-001` —
`S360-410` `schematic_status: cataloged_unverified` per
[`config/hardware-catalog.json`](../config/hardware-catalog.json),
Release-One PoE "schematic verification pending" caveat preserved
verbatim per HW-PINMAP-410-FOLLOWUP / PR #517).
`STABLE-TARGET-VENTIQ-001` therefore takes the gate-closure path
(option 3 in its task brief): it records the missing evidence per
gate and the owning follow-up slice; it does **not** promote
`Ceiling-POE-VentIQ` and it does **not** add a top-level product
YAML, catalog row, WebFlash wrapper, `artifact_name`,
`config/webflash-builds.json` row, or top-level compile-only target.
The compile-only skeleton at
[`products/compile-only/ceiling-poe-ventiq.yaml`](../products/compile-only/ceiling-poe-ventiq.yaml)
stays unchanged and stays classified `compile-only`. The classifier
counts stay verbatim. Resume conditions are listed in the
[gate-closure record](stable-target-ventiq-001-gate-closure.md#resume-conditions).

---

## What a single `STABLE-TARGET-*-001` PR will look like (template)

For orientation only; **no** action is taken here. Each PR in the
table above is expected to make the following — and only the
following — changes:

- Add the canonical top-level YAML at
  `products/sense360-<config-string-slug>.yaml` composing the
  package set that the matching `products/compile-only/<…>.yaml`
  skeleton already proves.
- Add a `config/product-catalog.json` row with `status: production`
  (or `status: preview` + `channel: preview` if going via preview
  first), the `config_string`, `version`, `channel`, `artifact_name`,
  `webflash_wrapper`, `webflash_build_matrix: true`, `modules`,
  `hardware`, and `hardware_status`.
- Add the WebFlash wrapper at
  `products/webflash/<config-string-slug>.yaml` re-including the
  canonical YAML.
- Add a `config/compile-only-targets.json` row pointing at the
  top-level product YAML (separate from the existing skeleton row),
  with `compile_validation_status: validated-full-compile` proven by
  an actual `scripts/validate_compile_targets.py --compile` run.
- Add a `config/webflash-builds.json` row with the matching
  `config_string`, `product_yaml` (= the wrapper), `artifact_name`,
  `channel`, `version`, `chip_family`, `hardware_requirements`, and
  `features`.
- Confirm `python3 scripts/list_release_targets.py` enumerates the
  new target.
- Confirm `python3 scripts/plan_room_release_notes.py
  --config-string <new>` plans the new target with
  `Validation summary: PASSED`.
- Add per-PR rows to
  [`docs/all-yaml-release-matrix.md`](all-yaml-release-matrix.md),
  [`docs/room-firmware-release-matrix.md`](room-firmware-release-matrix.md),
  [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md),
  and `UPCOMING_PR.md`.
- Re-run the full validation suite (see §Validation below).

Each PR explicitly does **not** publish a GitHub Release, does **not**
build or attach any firmware artifact, does **not** write
`firmware/sources.json` or `manifest.json`, does **not** commit any
`.bin` / checksum / build-info file. The first actual signed-artifact
production for any of these new targets is owned by a separate
`RELEASE-*-001` slice that the corresponding `STABLE-TARGET-*-001`
unblocks, mirroring the LED preview path (`PRODUCT-009` added the
catalog row + WebFlash wrapper + builds row; the LED preview release
artifact `v1.0.0-led-preview` was produced separately).

---

## Cross-cutting guardrails enforced by the existing CI

The plan does not weaken or change any existing CI guardrail. The
following are already locked in and will catch any future PR that
attempts to short-circuit the gates:

- **Release-selectable set equals `config/webflash-builds.json`** —
  asserted by
  [`tests/test_all_yaml_release_matrix.py`](../tests/test_all_yaml_release_matrix.py)
  (`test_release_selectable_matches_webflash_builds_json`).
- **Fan family tokens never appear in the release matrix** —
  asserted by the same test file, by
  [`scripts/plan_room_release_notes.py`](../scripts/plan_room_release_notes.py),
  [`scripts/list_release_targets.py`](../scripts/list_release_targets.py),
  and
  [`scripts/classify_all_yaml_release_matrix.py`](../scripts/classify_all_yaml_release_matrix.py).
- **LED preview is `preview`-only** — asserted by
  `test_led_artifact_carries_preview_suffix_not_stable` and
  `test_led_is_not_in_stable_targets`.
- **Exactly one stable / one preview target today** — asserted by
  `test_exactly_one_stable_target_today` and
  `test_exactly_one_preview_target_today`. A future
  `STABLE-TARGET-*-001` PR that lands the catalog + wrapper + builds
  row will update these tests in the same PR.
- **WebFlash wrappers are `not-a-product-entrypoint`** — asserted by
  `test_every_webflash_wrapper_is_not_entrypoint`.
- **Compile-only skeletons are `compile-only`** — asserted by
  `test_every_compile_only_skeleton_is_compile_only`.

---

## Validation

This document is reproduced and locked in by the same source-of-truth
checks the all-YAML matrix uses. None of the checks below requires a
firmware build, a GitHub Release, or any `.bin` artifact.

| Command | Expected result |
|---|---|
| `python3 scripts/classify_all_yaml_release_matrix.py --summary` | `stable=1, preview=1, manual=3, compile-only=7, blocked=1, not-a-product-entrypoint=35`; release-selectable = `Ceiling-POE-VentIQ-RoomIQ`, `Ceiling-POE-VentIQ-RoomIQ-LED` |
| `python3 scripts/list_release_targets.py` | Two rows: stable `Ceiling-POE-VentIQ-RoomIQ`, preview `Ceiling-POE-VentIQ-RoomIQ-LED`; `all-release-eligible` sentinel |
| `python3 scripts/plan_room_release_notes.py` | Two release-eligible builds; FanRelay / FanPWM / FanDAC excluded; FanTRIAC excluded / blocked; no `firmware/sources.json` or `manifest.json` written |
| `python3 tests/test_all_yaml_release_matrix.py` | 28 tests passed |
| `python3 tests/test_release_product_selection.py` | All passed (22 tests) |
| `python3 tests/validate_configs.py` | All YAMLs validate |
| `python3 scripts/validate_compile_targets.py --metadata-only` | 12 targets validated |
| `python3 tests/validate_webflash_builds.py` | 2 builds validated |
| `python3 tests/test_product_catalog.py` | All passed |
| `python3 -m unittest discover -s tests -p "test_*.py"` | Full suite passes; count unchanged from the prior baseline (no contract test added by this PR) |

---

## Cross-references

- Rank 1 gate-closure record: [`docs/stable-target-ventiq-001-gate-closure.md`](stable-target-ventiq-001-gate-closure.md) (STABLE-TARGET-VENTIQ-001) — per-gate G1–G10 audit for `Ceiling-POE-VentIQ`; documents the option-3 deferral and resume conditions; promotes nothing.
- All-YAML release matrix (upstream): [`docs/all-yaml-release-matrix.md`](all-yaml-release-matrix.md)
- Room-firmware release matrix: [`docs/room-firmware-release-matrix.md`](room-firmware-release-matrix.md)
- Release-artifact readiness gate: [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
- WebFlash-exposure readiness gate: [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md)
- Product readiness gate: [`docs/product-readiness-matrix.md`](product-readiness-matrix.md)
- Preview-to-stable gauntlet: [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
- LED preview decision: [`docs/product-led-preview-decision.md`](product-led-preview-decision.md)
- Compile-only expansion candidates ledger: [`docs/compile-only-expansion-candidates.md`](compile-only-expansion-candidates.md)
- Compile-only lane validation: [`docs/compile-only-firmware-validation.md`](compile-only-firmware-validation.md)
- Manual install path: [`docs/manual-install-fan-candidates.md`](manual-install-fan-candidates.md)
- **Sense360 PoE room bundle SKU matrix: [`docs/sense360-room-bundles.md`](sense360-room-bundles.md) (BUNDLE-SKU-MATRIX-001) — adds the sellable room bundle SKU layer (`S360-KIT-BATH-P`, `S360-KIT-KITCHEN-P`, `S360-KIT-LIVING-P`, `S360-KIT-BEDROOM-P`, `S360-KIT-CORRIDOR-P`) on top of this expansion plan. Each bundle's `Missing gates` column references the G1–G10 vocabulary defined here. The `STABLE-TARGET-AIRIQ-001` / `STABLE-TARGET-AIRIQ-ROOMIQ-001` follow-ups own the `S360-KIT-KITCHEN-P` likely firmware config target; `STABLE-TARGET-CORE-001` / `STABLE-TARGET-ROOMIQ-001` own `S360-KIT-BEDROOM-P`; `LED-STABLE-PROMOTION-001` (gauntlet-gated) covers the LED-bearing `S360-KIT-LIVING-P` / `S360-KIT-CORRIDOR-P`. No bundle promotion is approved by either PR.**
- Kit intent matrix (productized planning): [`docs/kit-intent-matrix.md`](kit-intent-matrix.md) (KIT-MATRIX-001)
- Shipping configuration: [`docs/release-one.md`](release-one.md)

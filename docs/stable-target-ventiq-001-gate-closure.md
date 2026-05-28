# STABLE-TARGET-VENTIQ-001 — Gate-closure record (no promotion)

## Purpose and scope

This document is the **gate-closure record** for the
`STABLE-TARGET-VENTIQ-001` slice named by
[`docs/stable-target-expansion-plan.md`](stable-target-expansion-plan.md)
(STABLE-TARGET-EXPANSION-PLAN-001 / PR #630). That plan asked the
question:

> *"Promote `Ceiling-POE-VentIQ` from `compile-only` to
> `stable-release` — smallest stable-expansion delta beyond the
> existing stable Release-One target
> (`Ceiling-POE-VentIQ-RoomIQ`)."*

This PR is the **next step** in that plan. It answers the question
*"can the G1–G10 stable-promotion gates be closed today without
inventing evidence?"* and the answer recorded here, derived from the
already-committed source-of-truth catalogs and readiness matrices, is
**no — promotion is not yet justified**. This PR therefore takes the
gate-closure path (option 3 in the task brief): it records the exact
missing evidence per gate and the owning follow-up slice; it does
**not** promote `Ceiling-POE-VentIQ` to `stable-release` and it does
**not** add a top-level product YAML, a catalog row, a WebFlash
wrapper, an `artifact_name`, a `config/webflash-builds.json` row, or
a top-level full-compile target.

`Ceiling-POE-VentIQ` stays classified `compile-only` exactly as
[`docs/all-yaml-release-matrix.md`](all-yaml-release-matrix.md)
records it today; the
[`scripts/classify_all_yaml_release_matrix.py --summary`](../scripts/classify_all_yaml_release_matrix.py)
counts stay verbatim at `stable=1, preview=1, manual=3,
compile-only=7, blocked=1, not-a-product-entrypoint=35`.

### Hard guardrails

STABLE-TARGET-VENTIQ-001 — this PR — does **not**:

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
  [`config/compile-only-candidates.json`](../config/compile-only-candidates.json),
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
  or [`config/hardware-catalog.json`](../config/hardware-catalog.json);
- write [`firmware/sources.json`](../firmware/sources.json) or
  `manifest.json`;
- promote `Ceiling-POE-VentIQ` from `compile-only` to
  `stable-candidate-after-promotion`, `preview-release`, or
  `stable-release`;
- promote LED from `preview` to `stable`;
- promote FanRelay / FanPWM / FanDAC out of `manual-candidate-only`;
- add an `artifact_name` to any fan product;
- flip any `webflash_build_matrix` value;
- promote `S360-410` (PoE PSU) `schematic_status` from
  `cataloged_unverified` to `verified` or set
  `schematic_file`;
- invent unsupported YAML / product combos;
- treat the existing
  [`products/compile-only/ceiling-poe-ventiq.yaml`](../products/compile-only/ceiling-poe-ventiq.yaml)
  skeleton as a release product;
- claim hardware / compliance evidence that is not already present.

---

## Inputs read

This record reads from the committed catalogs, readiness matrices,
and the read-only classifier; nothing is asserted beyond what they
already record.

| Source | File |
|---|---|
| Stable-target expansion plan (upstream) | [`docs/stable-target-expansion-plan.md`](stable-target-expansion-plan.md) |
| All-YAML release matrix | [`docs/all-yaml-release-matrix.md`](all-yaml-release-matrix.md) |
| Room-firmware release matrix | [`docs/room-firmware-release-matrix.md`](room-firmware-release-matrix.md) |
| Release matrix (sole release-eligibility source) | [`config/webflash-builds.json`](../config/webflash-builds.json) |
| Product lifecycle / hardware status | [`config/product-catalog.json`](../config/product-catalog.json) |
| Compile-only validation registry | [`config/compile-only-targets.json`](../config/compile-only-targets.json) |
| WebFlash compatibility grammar | [`config/webflash-compatibility.json`](../config/webflash-compatibility.json) |
| Hardware catalog (per-SKU `schematic_status`) | [`config/hardware-catalog.json`](../config/hardware-catalog.json) |
| All-YAML classifier | [`scripts/classify_all_yaml_release_matrix.py`](../scripts/classify_all_yaml_release_matrix.py) |
| Release-target enumerator | [`scripts/list_release_targets.py`](../scripts/list_release_targets.py) |
| Release-notes dry-run planner | [`scripts/plan_room_release_notes.py`](../scripts/plan_room_release_notes.py) |
| Per-board readiness matrix | [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md) |
| Product / WebFlash / Release readiness | [`docs/product-readiness-matrix.md`](product-readiness-matrix.md), [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md), [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md) |
| Preview-to-stable gauntlet | [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md) |
| Release-One hardware audit | [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md) |
| VentIQ board reference doc | [`docs/hardware/s360-211-r4-ventiq.md`](hardware/s360-211-r4-ventiq.md) |
| Product onboarding sequence | [`docs/product-onboarding.md`](product-onboarding.md) |

---

## Candidate identity

The candidate is the WebFlash config string `Ceiling-POE-VentIQ`
(Core ceiling + PoE PSU + VentIQ bathroom air-quality module; no
RoomIQ, no fan driver, no LED). The token grammar is already valid
under
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
(canonical mount `Ceiling`, canonical power `POE`, canonical module
`VentIQ`; AirIQ ↔ VentIQ mutex respected; no fan / LED token).

The YAML file that exists on disk today is the compile-only skeleton
[`products/compile-only/ceiling-poe-ventiq.yaml`](../products/compile-only/ceiling-poe-ventiq.yaml)
(FW-COMPILE-POE-NONFAN-001). It is registered in
[`config/compile-only-targets.json`](../config/compile-only-targets.json)
as target `ceiling-poe-ventiq-compile-only` and explicitly carries
`shipment_status: compile-only`, `webflash_exposure_allowed_now: false`,
and a `notes` line that calls out "compile success is not WebFlash
exposure, not a release artifact, and not product-catalog / stable /
preview promotion." This skeleton is **not** a release product and
its presence on disk does not satisfy any G1–G10 gate that requires a
top-level canonical YAML.

The existing stable target `Ceiling-POE-VentIQ-RoomIQ` (Release-One,
`v1.0.0`, `channel: stable`,
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`) is the closest
working precedent: it exercises the identical VentIQ subset
(`airiq_bathroom_base` + `bathroom_profile`) on top of the same Core
ceiling + PoE PSU base. That precedent is why `Ceiling-POE-VentIQ` is
the smallest stable-expansion delta in the
[`docs/stable-target-expansion-plan.md`](stable-target-expansion-plan.md)
table (row A5). It is **not** evidence that the new variant clears
the promotion gates on its own.

---

## G1–G10 gate audit (today)

This is the per-gate closure check derived directly from the
source-of-truth catalogs, readiness matrices, and audit documents
listed in [Inputs read](#inputs-read). Status keys: ✅ closed
(evidence present today), ❌ open (evidence missing today), ⚠️
inherited (would be inherited verbatim from the existing stable
Release-One row but is not independently closed).

| # | Gate | Evidence required | Status today | Owning follow-up to close |
|---|---|---|---|---|
| G1 | Top-level canonical product YAML exists at `products/sense360-ceiling-poe-ventiq.yaml` (the skeleton at `products/compile-only/ceiling-poe-ventiq.yaml` does **not** count) | A `sense360-ceiling-poe-ventiq.yaml` file is committed under `products/` | ❌ open — no such file exists; only the compile-only skeleton at [`products/compile-only/ceiling-poe-ventiq.yaml`](../products/compile-only/ceiling-poe-ventiq.yaml) is present | `STABLE-TARGET-VENTIQ-001` (this slice), once G2–G8 are clear |
| G2 | Product-catalog row in [`config/product-catalog.json`](../config/product-catalog.json) with `config_string: Ceiling-POE-VentIQ`, `status: production` (or `preview` + `channel: preview` if going preview first), `version`, `channel`, `artifact_name`, `webflash_wrapper`, `webflash_build_matrix: true`, `modules`, `hardware`, `hardware_status` | A new `Ceiling-POE-VentIQ` row in the catalog | ❌ open — no such row; catalog grep for `Ceiling-POE-VentIQ` returns only the existing `Ceiling-POE-VentIQ-RoomIQ` (production), `Ceiling-POE-VentIQ-RoomIQ-LED` (preview), `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` (blocked), and `Ceiling-POE-VentIQ-FanRelay-RoomIQ` (hardware-pending) entries; **none** is the VentIQ-only token | `STABLE-TARGET-VENTIQ-001` (this slice), once G1 + G8 are clear |
| G3 | Top-level full compile validated — a [`config/compile-only-targets.json`](../config/compile-only-targets.json) target that points at `products/sense360-ceiling-poe-ventiq.yaml` carries `compile_validation_status: validated-full-compile` (not a skeleton-only result) | A registered target with `compile_validation_status: validated-full-compile` for the top-level YAML | ❌ open — the only `Ceiling-POE-VentIQ` target registered is `ceiling-poe-ventiq-compile-only` and it points at the **skeleton** ([`products/compile-only/ceiling-poe-ventiq.yaml`](../products/compile-only/ceiling-poe-ventiq.yaml)), not a top-level product YAML, and it does **not** carry `compile_validation_status: validated-full-compile` (the FanRelay / FanPWM / FanDAC top-level pattern from FW-FULL-COMPILE-TOPLEVEL-FANS-001 / PR #616 is the precedent here) | `STABLE-TARGET-VENTIQ-001` after G1 lands (registers the top-level target separately from the skeleton, mirroring `ceiling-poe-fandac-product-compile-only` / `ceiling-poe-fanpwm-product-compile-only`) |
| G4 | WebFlash wrapper exists at `products/webflash/ceiling-poe-ventiq.yaml` (re-includes the canonical YAML) and the catalog row sets `webflash_wrapper` to it | A new wrapper YAML | ❌ open — no such file exists under [`products/webflash/`](../products/webflash/) (only `ceiling-poe-ventiq-roomiq.yaml`, `ceiling-poe-ventiq-roomiq-led.yaml`, and `ceiling-poe-ventiq-fantriac-roomiq.yaml`) | `STABLE-TARGET-VENTIQ-001` after G1 + G2 land |
| G5 | `artifact_name` present in both the catalog row and the matching [`config/webflash-builds.json`](../config/webflash-builds.json) row, matching the `Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin` shape that [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py) accepts | `Sense360-Ceiling-POE-VentIQ-v{VERSION}-{CHANNEL}.bin` declared in both rows | ❌ open — no `Ceiling-POE-VentIQ` row exists in either source today; the `Sense360-Ceiling-POE-VentIQ-…` artifact name string does not appear anywhere in `config/`, `products/`, or `docs/` | `STABLE-TARGET-VENTIQ-001` after G1 + G2 + G6 are scoped |
| G6 | [`config/webflash-builds.json`](../config/webflash-builds.json) row for the config (`channel: stable` for a stable promotion, `channel: preview` for a preview-first step), referenced by the WebFlash wrapper | A new `Ceiling-POE-VentIQ` row in the build matrix | ❌ open — current `config/webflash-builds.json` has exactly 2 rows (`Ceiling-POE-VentIQ-RoomIQ` stable, `Ceiling-POE-VentIQ-RoomIQ-LED` preview); the test `test_exactly_one_stable_target_today` / `test_exactly_one_preview_target_today` / `test_release_selectable_matches_webflash_builds_json` in [`tests/test_all_yaml_release_matrix.py`](../tests/test_all_yaml_release_matrix.py) actively asserts that count today | `STABLE-TARGET-VENTIQ-001` after G1 + G2 + G4 land (the same PR also updates the affected contract tests in lockstep) |
| G7 | Release notes can be generated without overrides — [`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py) does not refuse, [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py) passes structurally, and [`scripts/plan_room_release_notes.py --config-string Ceiling-POE-VentIQ`](../scripts/plan_room_release_notes.py) plans the new target with `Validation summary: PASSED` | A dry-run planner result for `Ceiling-POE-VentIQ` that prints `Validation summary: PASSED` | ❌ open — dry-run planner rejects any `config_string` not present in `config/webflash-builds.json`; G6 must land first | Downstream of G6 |
| G8 | No blocking hardware / compliance caveat — every relevant board carries `schematic_status: verified` (or the per-board readiness matrix records the caveat as `closed`), every relevant package carries `ready-for-package-change`, no [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md) / [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md) / [`docs/product-readiness-matrix.md`](product-readiness-matrix.md) row classifies the family as `not-ready` | All relevant boards (`S360-100`, `S360-211`, `S360-410`) at `schematic_status: verified` and the Release-One PoE caveat closed | ❌ open — see [§G8 detail — hardware / compliance evidence](#g8-detail--hardware--compliance-evidence) below. **`S360-100` and `S360-211` are `schematic_status: verified` today** (HW-007 / HW-008 for both Core and VentIQ); **`S360-410` (PoE PSU) is `schematic_status: cataloged_unverified` today** ([`config/hardware-catalog.json`](../config/hardware-catalog.json), line 120), and the Release-One PoE "schematic verification pending" caveat is preserved verbatim per HW-PINMAP-410-FOLLOWUP / PR #517. This is the same caveat the existing stable `Ceiling-POE-VentIQ-RoomIQ` row inherits — it is **not** independently closed for a new variant. ⚠️ inherited from Release-One in the sense that Release-One ships under it; not closed | `PACKAGE-POE-410-001` (per [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md) §`S360-410`) — blocked behind BOM cross-check, `S360-410 schematic_status: verified` JSON PR, `HW-002` `OQ#6`, `S360-100-BENCH-001` `J2`-harness closure, package-header reconciliation. Until that chain clears, **no new top-level product YAML that depends on `S360-410` should claim a verified PoE PSU lineage**. |
| G9 | Not currently `manual-candidate-only` — the candidate is not listed in [`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json) and the corresponding per-family slice has cleared first | Absence from the manual lane | ✅ closed — `Ceiling-POE-VentIQ` is **not** in `config/manual-firmware-artifacts.json` (the manual lane is FanRelay / FanPWM / FanDAC only); it is `compile-only`, not `manual-candidate-only` | n/a — gate already closed |
| G10 | Not currently `preview-only` — if promotion is from `preview` to `stable`, the [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md) 17-row gauntlet has closed (preview-stage bench Open Questions resolved, regression-free preview soak, etc.) | If going preview-first: preview soak / gauntlet closure | ❌ open — the expansion plan's recommended PR scope (rank 1 in [`docs/stable-target-expansion-plan.md` §Recommended follow-up PR sequence](stable-target-expansion-plan.md#recommended-follow-up-pr-sequence)) lands on `channel: stable` directly, but the [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md) gauntlet's operator-proof / bench-verification / WebFlash import / live preview deploy / human-approval rows must still be satisfied for a brand-new top-level YAML, even one that re-uses the Release-One package set verbatim. No preview soak has been executed for the VentIQ-only YAML because **no top-level YAML exists yet** (G1 ❌). | Downstream of G1–G8; closed by an explicit `STABLE-TARGET-VENTIQ-001-PREVIEW-SOAK` or absorbed into a phased `STABLE-TARGET-VENTIQ-001` if a `preview` first step is chosen |

**Gates closed today:** 1 of 10 (G9).
**Gates open today:** 9 of 10 (G1, G2, G3, G4, G5, G6, G7, G8, G10).

Because G8 (the hardware / compliance gate) is **not closed** and is
upstream-blocked by `PACKAGE-POE-410-001` (which is itself blocked
behind further BOM / schematic JSON / bench gates per
[`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
§`S360-410`), no amount of repository-only work in
`STABLE-TARGET-VENTIQ-001` can satisfy the full G1–G10 set today.
Promotion is therefore **not justified**.

---

## G8 detail — hardware / compliance evidence

This section makes the G8 evidence picture explicit so future
re-evaluation does not have to re-derive it. Nothing in this section
is **changed** by this PR; everything is **read** from the committed
sources cited inline.

### G8.a — Sense360 Core (`S360-100`)

- `schematic_status: verified` per
  [`config/hardware-catalog.json`](../config/hardware-catalog.json),
  with `schematic_file` set (HW-007 / HW-008).
- [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
  row: `verified` with the `S360-100-BENCH-001` bench gate still
  carried as an open follow-up
  ([`docs/release-one-hardware-audit.md` §Required follow-ups](release-one-hardware-audit.md#required-follow-ups)).
  This affects the J2 PoE harness identity that G8.c calls out and is
  the same caveat Release-One ships under.

### G8.b — Sense360 VentIQ (`S360-211`)

- `schematic_status: verified` per
  [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  with `schematic_file:
  docs/hardware/schematics/S360-211-R4.pdf` (HW-007 / HW-008).
- [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
  row: `verified` (BOM-asset deferral HW-ASSETS-005 carried as an
  open follow-up, but the schematic verification itself is closed).
- The package include path the existing stable build exercises —
  [`packages/expansions/airiq_bathroom_base.yaml`](../packages/expansions/airiq_bathroom_base.yaml)
  +
  [`packages/features/bathroom_profile.yaml`](../packages/features/bathroom_profile.yaml)
  — is the same path the compile-only skeleton
  [`products/compile-only/ceiling-poe-ventiq.yaml`](../products/compile-only/ceiling-poe-ventiq.yaml)
  uses. **VentIQ-specific hardware evidence is therefore present.**

### G8.c — Sense360 PoE PSU (`S360-410`)

- `schematic_status: cataloged_unverified` per
  [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  line 120 — **JSON promotion to `verified` has not landed**.
- [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
  row: schematic PDF committed under HW-ASSETS-410 / PR #516; the
  pin-map audit was promoted by HW-PINMAP-410-FOLLOWUP / PR #517 to
  *`partial — schematic evidence available; package reconciliation,
  PoE PD controller / magnetics / buck / isolated DC/DC / harness
  identity evidence pending`*. The Release-One PoE "schematic
  verification pending" caveat is preserved verbatim. Standalone
  reference-doc rewrite, BOM-backed part-identity reconciliation,
  silkscreen pin-1 on `J3`, isolation / Hi-pot / PoE link-up bench
  evidence, and `HW-002` `OQ#6` / `S360-100-BENCH-001` `J2`-harness
  closure all still owed.
- Existing stable target `Ceiling-POE-VentIQ-RoomIQ` ships under
  exactly this caveat — it is an inherited Release-One caveat, **not
  a closed gate**. The stable-target expansion plan
  ([`docs/stable-target-expansion-plan.md` §A. Non-fan / non-LED /
  non-TRIAC room combos](stable-target-expansion-plan.md#a-non-fan--non-led--non-triac-room-combos))
  is explicit that every A-row candidate (including A5 / VentIQ-only)
  carries this shared `PRODUCT-POE-410-001` / `S360-410` schematic
  verification chain and that "promotion order is therefore
  deliberately sequential — the smallest skeleton first
  (`Ceiling-POE`) so the PoE-410 closure is amortised across the
  family." Promotion of a brand-new `Ceiling-POE-VentIQ` row before
  PoE-410 closure would re-issue the same Release-One PoE caveat
  inside a NEW stable build, multiplying caveats rather than closing
  one — the opposite of what the expansion plan wants.
- **Conclusion:** G8 is `open` for `Ceiling-POE-VentIQ`. The owning
  follow-up is `PACKAGE-POE-410-001`, blocked behind BOM cross-check,
  `S360-410 schematic_status: verified` JSON PR, `HW-002` `OQ#6`,
  `S360-100-BENCH-001` `J2`-harness closure, package-header
  reconciliation.

### G8.d — Compliance

PoE is SELV / low-voltage; `COMPLIANCE-001` (mains-voltage UK / EU
assessment) does **not** gate `Ceiling-POE-VentIQ`. No additional
compliance row applies. This dimension is **not** the blocker — the
blocker is G8.c.

---

## Decision

Recorded decision for STABLE-TARGET-VENTIQ-001 in this PR:

> **Do not promote `Ceiling-POE-VentIQ` to `stable-release`,
> `preview-release`, or `stable-candidate-after-promotion` in this
> PR.** G8 (hardware / compliance) is open behind
> `PACKAGE-POE-410-001`; G1–G7 and G10 are structurally open behind
> G8's closure. The compile-only skeleton at
> [`products/compile-only/ceiling-poe-ventiq.yaml`](../products/compile-only/ceiling-poe-ventiq.yaml)
> stays unchanged and stays classified `compile-only`. No top-level
> product YAML is added. No catalog row is added. No WebFlash
> wrapper is added. No `config/webflash-builds.json` row is added.
> No `artifact_name` is declared. No `webflash_build_matrix` flip.
> No new compile-only target id is registered. The 48-YAML
> classification stays verbatim at `stable=1, preview=1, manual=3,
> compile-only=7, blocked=1, not-a-product-entrypoint=35`.

This is the option-3 outcome explicitly contemplated by the task
brief: *"If promotion is not yet justified: do not add fake product /
release rows. Produce a smaller gate-closure PR that records the
exact missing evidence or structural gap. Keep classification as
stable-candidate or compile-only."*

---

## Resume conditions

`STABLE-TARGET-VENTIQ-001` can resume actual promotion work (G1–G10
implementation) only when **all** of the following are independently
recorded by their own committed slice — none can be assumed,
fabricated, or rolled into the same PR. **Resume condition #1
(`PACKAGE-POE-410-001`) has been audited on 2026-05-28** per
[`docs/package-poe-410-001-audit.md`](package-poe-410-001-audit.md)
(option 4 — evidence insufficient for verification; precise
evidence-request record produced); see
[`docs/package-poe-410-001-audit.md` §Resume conditions](package-poe-410-001-audit.md#resume-conditions)
for the per-evidence-class closure list (E2 + E8 + E9 + E10 + E11 +
E12 + E14 + design-intent answers) that condition #1 below requires.

1. **`PACKAGE-POE-410-001` lands** with `S360-410 schematic_status:
   verified` JSON promotion, `schematic_file` set, BOM cross-check
   closed, and the `packages/hardware/power_poe.yaml` header
   reconciled against the schematic-shown discrete topology
   (`TPS2378DDAR / TX4138 / F0505S-2WR2 / RJP-003TC1(LPJ4112CNL)`).
2. **`S360-100-BENCH-001` `J2`-harness closure** lands, satisfying
   `HW-002` `OQ#6`, removing the Release-One PoE harness-identity
   caveat that `Ceiling-POE-VentIQ` would otherwise inherit.
3. **`COMPLIANCE-001` for the PoE path** — not strictly required
   (PoE is SELV), but the per-board readiness matrix's
   `compliance-gated` posture on `S360-410` (if any future row
   reclassifies it) must be `none` for the PoE family.
4. **Per-board readiness matrix flips `S360-410`** to schematic-and-
   package-verified in
   [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
   and the package-readiness matrix flips
   `packages/hardware/power_poe.yaml` to
   `ready-for-package-change` in
   [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md).
5. **Product-onboarding approval** per
   [`docs/product-onboarding.md`](product-onboarding.md) for the new
   `Ceiling-POE-VentIQ` lifecycle is recorded.

When all five resume conditions hold, the implementation PR will
follow the per-PR scope template in
[`docs/stable-target-expansion-plan.md` §What a single
`STABLE-TARGET-*-001` PR will look like (template)](stable-target-expansion-plan.md#what-a-single-stable-target-001-pr-will-look-like-template):
add `products/sense360-ceiling-poe-ventiq.yaml`; add the catalog
row; add the WebFlash wrapper at
`products/webflash/ceiling-poe-ventiq.yaml`; register the top-level
compile-only target (separate from the existing skeleton row, with
`compile_validation_status: validated-full-compile` proven by a real
`scripts/validate_compile_targets.py --compile` run, mirroring the
`ceiling-poe-fandac-product-compile-only` /
`ceiling-poe-fanpwm-product-compile-only` precedent); add the
`config/webflash-builds.json` row with the matching identity; update
the `test_exactly_one_stable_target_today` /
`test_exactly_one_preview_target_today` /
`test_release_selectable_matches_webflash_builds_json` contracts to
the new (n+1 stable, n preview) state; and re-run the full
validation suite.

That implementation PR is **not** approved or scoped by this
gate-closure PR.

---

## What stays exactly the same

The release surface is unchanged:

| Artifact | State after this PR |
|---|---|
| `config/webflash-builds.json` | Exactly 2 rows (`Ceiling-POE-VentIQ-RoomIQ` stable, `Ceiling-POE-VentIQ-RoomIQ-LED` preview) — unchanged |
| `config/product-catalog.json` | No new row; no status flip — unchanged |
| `config/compile-only-targets.json` | Exactly 12 targets — unchanged (no new `ceiling-poe-ventiq-product-compile-only` registered) |
| `config/manual-firmware-artifacts.json` | Unchanged |
| `config/compile-only-candidates.json` | Unchanged |
| `config/webflash-compatibility.json` | Unchanged (`Ceiling-POE-VentIQ` token grammar already valid; no `release_one_required_configs` change) |
| `config/hardware-catalog.json` | Unchanged (`S360-410` stays `cataloged_unverified`) |
| `products/sense360-ceiling-poe-ventiq.yaml` | Does not exist; not created by this PR |
| `products/webflash/ceiling-poe-ventiq.yaml` | Does not exist; not created by this PR |
| `products/compile-only/ceiling-poe-ventiq.yaml` | Unchanged (still the FW-COMPILE-POE-NONFAN-001 skeleton, still `compile-only`) |
| `firmware/sources.json` / `manifest.json` / `.bin` / checksum | None produced or committed |
| Release-One `Ceiling-POE-VentIQ-RoomIQ` (`v1.0.0` / `stable`) | Unchanged — Release-One ships verbatim |
| LED preview `Ceiling-POE-VentIQ-RoomIQ-LED` (`v1.0.0` / `preview`) | Unchanged — stays `preview` (`LED-STABLE-PROMOTION-001` separately gated) |
| FanRelay / FanPWM / FanDAC | Stay `manual-candidate-only` — no `artifact_name`, no `webflash_build_matrix` flip, no WebFlash wrapper, no release artifact |
| FanTRIAC | Stays `blocked` (`HW-005`) |
| Classifier counts (`scripts/classify_all_yaml_release_matrix.py --summary`) | `stable=1, preview=1, manual=3, compile-only=7, blocked=1, not-a-product-entrypoint=35` — verbatim |
| Release-selectable set | `{Ceiling-POE-VentIQ-RoomIQ, Ceiling-POE-VentIQ-RoomIQ-LED}` — verbatim |
| Contract tests in [`tests/test_all_yaml_release_matrix.py`](../tests/test_all_yaml_release_matrix.py) | Unchanged — `test_exactly_one_stable_target_today` / `test_exactly_one_preview_target_today` / `test_release_selectable_matches_webflash_builds_json` still pass without modification |

---

## Validation

This document is reproduced and locked in by the same source-of-truth
checks the all-YAML matrix and the expansion plan use. None of the
checks below requires a firmware build, a GitHub Release, or any
`.bin` artifact.

| Command | Expected result |
|---|---|
| `python3 scripts/classify_all_yaml_release_matrix.py --summary` | `stable=1, preview=1, manual=3, compile-only=7, blocked=1, not-a-product-entrypoint=35`; release-selectable = `Ceiling-POE-VentIQ-RoomIQ`, `Ceiling-POE-VentIQ-RoomIQ-LED` |
| `python3 scripts/list_release_targets.py` | Two rows: stable `Ceiling-POE-VentIQ-RoomIQ`, preview `Ceiling-POE-VentIQ-RoomIQ-LED`; `all-release-eligible` sentinel |
| `python3 scripts/plan_room_release_notes.py` | Two release-eligible builds; FanRelay / FanPWM / FanDAC excluded; FanTRIAC excluded / blocked; no `firmware/sources.json` or `manifest.json` written |
| `python3 tests/test_all_yaml_release_matrix.py` | 28 tests passed |
| `python3 tests/test_release_product_selection.py` | All passed |
| `python3 tests/test_release_dry_run_mode.py` | All passed |
| `python3 tests/validate_configs.py` | All YAMLs validate |
| `python3 scripts/validate_compile_targets.py --metadata-only` | 12 targets validated |
| `python3 tests/validate_webflash_builds.py` | 2 builds validated |
| `python3 tests/test_product_catalog.py` | All passed |
| `python3 tests/test_workflow_permissions.py` | All passed |
| `python3 -m unittest discover -s tests -p "test_*.py"` | Full suite passes; count unchanged from the prior baseline (no contract test added by this PR) |

---

## Cross-references

- Stable target expansion plan (upstream): [`docs/stable-target-expansion-plan.md`](stable-target-expansion-plan.md) (STABLE-TARGET-EXPANSION-PLAN-001 / PR #630)
- All-YAML release matrix: [`docs/all-yaml-release-matrix.md`](all-yaml-release-matrix.md) (STABLE-RELEASE-MATRIX-ALL-YAML-001 / PR #629)
- Room-firmware release matrix: [`docs/room-firmware-release-matrix.md`](room-firmware-release-matrix.md)
- Release-artifact readiness gate: [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
- WebFlash-exposure readiness gate: [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md)
- Product readiness gate: [`docs/product-readiness-matrix.md`](product-readiness-matrix.md)
- Preview-to-stable gauntlet: [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
- LED preview decision: [`docs/product-led-preview-decision.md`](product-led-preview-decision.md)
- Compile-only lane validation: [`docs/compile-only-firmware-validation.md`](compile-only-firmware-validation.md)
- Release-One hardware audit: [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)
- Per-board readiness: [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
- Per-package readiness: [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
- VentIQ board reference: [`docs/hardware/s360-211-r4-ventiq.md`](hardware/s360-211-r4-ventiq.md)
- Product onboarding: [`docs/product-onboarding.md`](product-onboarding.md)
- Shipping configuration: [`docs/release-one.md`](release-one.md)

# Pre-Hardware Room-Bundle Release-Handoff Matrix (PRE-HW-PREP-ROOM-BUNDLES-001)

> **Release status (`FIRST-RELEASE-DOCS-DRIFT-RECONCILE-001`).** The Bathroom
> first-release path (`S360-KIT-BATH-P` / `Ceiling-POE-VentIQ-RoomIQ` / stable)
> is **published and live** as GitHub Release **`v1.0.0`** (2026-05-12),
> imported/live in WebFlash — it is not pending. The other four bundles remain
> pre-hardware candidates as described below. Any future publish uses a **new
> version** (e.g. `1.0.1` / `1.1.0`); `v1.0.0` is not re-published. See
> [`docs/first-release-publish-readiness.md`](first-release-publish-readiness.md).

> **See also:** the per-bundle first-release view here is rolled up into the
> consolidated **first-release / expansion gate checklist**
> [`docs/first-release-gates.md`](first-release-gates.md)
> (`PRE-HW-PREP-FIRST-RELEASE-GATES-001`) — the canonical "what can ship now /
> what is blocked / what evidence is required" doc. This handoff matrix remains
> the detailed per-bundle source for the room-bundle column legend and audit
> findings.

## Purpose and scope

This document is the **pre-hardware release-handoff matrix** for the five
canonical Sense360 PoE room bundles
([`config/room-bundle-skus.json`](../config/room-bundle-skus.json) /
[`docs/sense360-room-bundles.md`](sense360-room-bundles.md),
`BUNDLE-SKU-MATRIX-001`): **Bathroom**, **Kitchen**, **Living Room**,
**Bedroom**, and **Landing / Corridor**.

It audits each bundle's docs / configs against the **current board
readiness** recorded in the repository and threads, per bundle, the
evidence dimensions that gate a **first release**:

- the bundle SKU,
- the boards the bundle ships,
- the firmware config target those boards produce,
- that config's release channel / status,
- its WebFlash exposure status,
- the blocking hardware evidence that stands between the bundle and a
  release,
- the release-note status,
- the bench task that owns the outstanding hardware evidence, and
- the bundle's first-release eligibility.

It exists so the eventual hardware / evidence handoff is a single
matrix to read down rather than a cross-walk of
[`config/room-bundle-skus.json`](../config/room-bundle-skus.json),
[`config/webflash-builds.json`](../config/webflash-builds.json),
[`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json),
[`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md),
[`docs/room-firmware-release-matrix.md`](room-firmware-release-matrix.md),
and [`docs/room-firmware-release-notes.md`](room-firmware-release-notes.md).
It threads the existing facts; it does not invent or move any of them.

### This document is documentation only

PRE-HW-PREP-ROOM-BUNDLES-001 — this PR — **promotes nothing, enables
nothing, and verifies nothing**. It does **not**:

- promote any bundle, or its likely firmware config target, to
  `preview`, `stable`, or `production`;
- enable any WebFlash exposure — it adds no row to
  [`config/webflash-builds.json`](../config/webflash-builds.json), sets
  no `artifact_name`, and flips no `webflash_build_matrix` value;
- add, publish, or attach any firmware artifact (`.bin`, checksum,
  build-info), and creates no GitHub Release; it writes no
  [`firmware/sources.json`](../firmware/sources.json) or `manifest.json`;
- edit any YAML under [`products/`](../products/),
  [`products/webflash/`](../products/webflash/), or
  [`products/compile-only/`](../products/compile-only/), or any
  `packages/**` file;
- change any `config/*.json` — not
  [`config/room-bundle-skus.json`](../config/room-bundle-skus.json),
  [`config/room-bundle-fan-variants.json`](../config/room-bundle-fan-variants.json),
  [`config/hardware-catalog.json`](../config/hardware-catalog.json),
  [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json),
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  [`config/product-catalog.json`](../config/product-catalog.json), or
  any other — and changes no config string, `artifact_name`,
  `lifecycle`, or `schematic_status`;
- mark `S360-410` (PoE PSU) `verified`; the
  `schematic_status: cataloged_unverified` value and the Release-One PoE
  "schematic verification pending" caveat are preserved verbatim;
- mark LED (`S360-300`) stable; LED stays `preview`;
- mark any fan variant (`S360-310` / `S360-311` / `S360-312` /
  `S360-320`) release-ready or stable; the fan-control variants are a
  **preview bundle plan at most** (the five buildable configs are
  `buildable-preview-compile-validated` after `ROOM-BUNDLE-FAN-CONFIGS-001` +
  `ROOM-BUNDLE-FAN-COMPILE-RESULTS-001` recorded the hosted full ESPHome
  compile, run `26913592989` — firmware-build proof only — and now also carry a
  published Advanced-install-only preview `.bin` after
  `ROOM-BUNDLE-FAN-PUBLISH-RESULTS-001` (run `26947595936`, firmware-build /
  release proof only; still not WebFlash-exposed, not stable, not buyable);
  advanced / manual only for TRIAC which stays build-blocked under `HW-005`)
  per
  [`config/room-bundle-fan-variants.json`](../config/room-bundle-fan-variants.json)
  (`ROOM-BUNDLE-FAN-VARIANTS-002`, revised by `ROOM-BUNDLE-FAN-CONFIGS-001`),
  and stable / full release stays hardware / evidence / compliance gated;
- add a fan bundle SKU, or treat a bundle SKU as a board SKU, firmware
  config string, or release artifact name.

The only file this PR adds is this document; the only other file it
edits is [`UPCOMING_PR.md`](../UPCOMING_PR.md).

---

## Column legend

| Column | Meaning / source of truth |
|---|---|
| **Bundle SKU** | Sellable room-kit identifier from [`config/room-bundle-skus.json`](../config/room-bundle-skus.json). Not a board SKU, config string, or artifact name. |
| **Included boards** | `included_board_skus` from [`config/room-bundle-skus.json`](../config/room-bundle-skus.json) (canonical board SKUs in [`config/hardware-catalog.json`](../config/hardware-catalog.json)). Every bundle ships Core (`S360-100`) + PoE PSU (`S360-410`). |
| **Firmware config target** | The bundle's `likely_firmware_config_target` — the config string the included boards produce. Source: [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json). |
| **Release channel / status** | The config target's status in [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json), with the bundle's `current_release_status` from [`config/room-bundle-skus.json`](../config/room-bundle-skus.json) in parentheses. |
| **WebFlash status** | Whether the config target has a row in [`config/webflash-builds.json`](../config/webflash-builds.json). `exposed (stable/preview)` = present; `not-exposed` = no build row. |
| **Blocking hardware evidence** | The hardware-evidence items (per [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)) that gate this bundle's first release. |
| **Release-note status** | Per [`docs/room-firmware-release-matrix.md`](room-firmware-release-matrix.md) / [`docs/room-firmware-release-notes.md`](room-firmware-release-notes.md): `eligible-stable` / `eligible-preview` = generable today; `not-generable` = no catalog row, refused without overrides. |
| **Bench task pointer** | The named bench / operator-evidence task that owns the outstanding hardware evidence. Forward pointers only — no evidence is claimed here. |
| **First-release eligibility** | `ELIGIBLE` = the config target is already release-eligible (a `webflash-builds` row exists); `NOT eligible` = a named follow-up owns promotion, not this PR. |

---

## Pre-hardware release-handoff matrix

| Bundle SKU | Included boards | Firmware config target | Release channel / status | WebFlash status | Blocking hardware evidence | Release-note status | Bench task pointer | First-release eligibility |
|---|---|---|---|---|---|---|---|---|
| `S360-KIT-BATH-P`<br>(Bathroom) | `S360-100` Core; `S360-200` RoomIQ; `S360-211` VentIQ; `S360-410` PoE PSU | `Ceiling-POE-VentIQ-RoomIQ` | `webflash-published` (`stable-release`, `v1.0.0` live) | **exposed (stable)** — `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` | S360-410 PoE "schematic verification pending" caveat **preserved** (Release-One ships under this caveat; not cleared here); Core J2 PoE-harness identity (HW-002 OQ#6) open under `S360-100-BENCH-001`. Neither blocks the existing stable build. | `eligible-stable` | `S360-100-BENCH-001` (Core / J2 PoE harness); `PRE-HW-PREP-POE-410-001` (PoE isolation / Hi-pot, downstream) | **PUBLISHED / LIVE** — the Release-One stable build, shipped as `v1.0.0`; **not promoted by this PR** (already published). |
| `S360-KIT-KITCHEN-P`<br>(Kitchen) | `S360-100` Core; `S360-200` RoomIQ; `S360-210` AirIQ; `S360-410` PoE PSU | `Ceiling-POE-AirIQ-RoomIQ` | `missing-product-yaml` (`stable-candidate`) | not-exposed — no `webflash-builds` row; compile-only skeleton [`products/compile-only/ceiling-poe-airiq-roomiq.yaml`](../products/compile-only/ceiling-poe-airiq-roomiq.yaml) validates the combination only | AirIQ-stack hardware evidence (SPS30 / SGP41 / SCD41 / BMP390) — `S360-210` is `hardware-evidenced / firmware-missing` with no active product YAML; shared S360-410 PoE-410 chain (`PRODUCT-POE-410-001` / `PACKAGE-POE-410-001`). | `not-generable` (no catalog row) | AirIQ sensor-stack bench under `STABLE-TARGET-AIRIQ-001`; `S360-100-BENCH-001`; `PRE-HW-PREP-POE-410-001` | **NOT eligible** — owned by `STABLE-TARGET-AIRIQ-001` → `STABLE-TARGET-AIRIQ-ROOMIQ-001` (after PoE-410 closure). |
| `S360-KIT-LIVING-P`<br>(Living Room) | `S360-100` Core; `S360-200` RoomIQ; `S360-300` LED; `S360-410` PoE PSU | `Ceiling-POE-RoomIQ-LED` | `missing-product-yaml` (`preview-candidate`) | not-exposed — no `webflash-builds` row. (The only exposed `preview` LED build is `Ceiling-POE-VentIQ-RoomIQ-LED`, a **different** config string with VentIQ.) | LED (`S360-300`) stays `preview` — bench evidence owed; operator flash proof `WF-HW-TEST-001` / `WF-HW-TEST-003`; shared S360-410 PoE-410 chain. | `not-generable` (no catalog row) | `S360-300-BENCH-001` (LED bench); `WF-HW-TEST-001` / `WF-HW-TEST-003`; `PRE-HW-PREP-POE-410-001` | **NOT eligible** — LED preview-gated; promotion owned by `LED-STABLE-PROMOTION-001` (alias `RELEASE-007`) + an unscoped no-VentIQ LED slice. |
| `S360-KIT-BEDROOM-P`<br>(Bedroom) | `S360-100` Core; `S360-200` RoomIQ; `S360-410` PoE PSU | `Ceiling-POE-RoomIQ` | `blocked-hardware` (`stable-candidate`) — see [audit finding](#audit-findings) | not-exposed — no `webflash-builds` row | Shared S360-410 PoE-410 chain (`PRODUCT-POE-410-001` / `PACKAGE-POE-410-001`); `S360-410` `schematic_status: cataloged_unverified`; Core review under `S360-100-BENCH-001`. | `not-generable` (no catalog row) | `S360-100-BENCH-001`; `PRE-HW-PREP-POE-410-001` | **NOT eligible** — owned by `STABLE-TARGET-CORE-001` → `STABLE-TARGET-ROOMIQ-001`. |
| `S360-KIT-CORRIDOR-P`<br>(Landing / Corridor) | `S360-100` Core; `S360-200` RoomIQ; `S360-300` LED; `S360-410` PoE PSU | `Ceiling-POE-RoomIQ-LED` | `missing-product-yaml` (`preview-candidate`) | not-exposed — no `webflash-builds` row | Same as `S360-KIT-LIVING-P` (shares board set + config target): LED stays `preview`; `WF-HW-TEST-001` / `WF-HW-TEST-003`; shared S360-410 PoE-410 chain. | `not-generable` (no catalog row) | `S360-300-BENCH-001`; `WF-HW-TEST-001` / `WF-HW-TEST-003`; `PRE-HW-PREP-POE-410-001` | **NOT eligible** — same as `S360-KIT-LIVING-P` until a corridor-specific config differentiates them. |

**Summary: 1 of 5 room bundles is published/live today**
(`S360-KIT-BATH-P`, the Release-One stable build, shipped as `v1.0.0`). The other
four remain candidates whose promotion is owned by named follow-up PRs,
none of which is approved or scoped here.

---

## Audit findings

The audit cross-walked
[`config/room-bundle-skus.json`](../config/room-bundle-skus.json) against
the current state of the source-of-truth configs and readiness docs.
Findings (reported, **not** resolved — no source file is changed by this
PR):

1. **Bathroom is the only WebFlash-exposed bundle.** Only
   `Ceiling-POE-VentIQ-RoomIQ` has a row in
   [`config/webflash-builds.json`](../config/webflash-builds.json)
   (stable channel). The four other bundles' config targets have no
   build row and are therefore not WebFlash-installable today. This
   matches [`docs/sense360-room-bundles.md`](sense360-room-bundles.md).

2. **Bedroom's config target is `blocked-hardware`, not just a
   stable-candidate.** [`config/room-bundle-skus.json`](../config/room-bundle-skus.json)
   records `S360-KIT-BEDROOM-P` as `stable-candidate` pointing at the
   compile-only skeleton, but
   [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json)
   now carries `Ceiling-POE-RoomIQ` as **`blocked-hardware`** with a
   top-level product YAML
   (`products/sense360-ceiling-poe-roomiq.yaml`) and an explicit
   `PRODUCT-POE-410-001` blocker. The firmware-combination-matrix is the
   more current view: a top-level RoomIQ-only product YAML now exists and
   is release-blocked on the shared S360-410 PoE schematic-verification
   chain. Both views agree the bundle is **not** first-release eligible;
   the matrix above flags the nuance. No source file is changed to
   reconcile this — reconciliation, if wanted, is owned by the
   `STABLE-TARGET-ROOMIQ-001` / `room-bundle-skus.json` maintainer, not
   by this audit.

3. **The S360-410 PoE PSU chain is the shared blocker under every
   non-Bathroom bundle.** Every PoE bundle ships `S360-410`, whose
   `schematic_status` is `cataloged_unverified` with the Release-One PoE
   "schematic verification pending" caveat preserved
   ([`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
   `S360-410` row). The Bathroom bundle ships under this caveat already;
   the others additionally need their own per-stack evidence (AirIQ
   sensors for Kitchen, LED bench for Living / Corridor). The caveat is
   **not** cleared here and `S360-410` is **not** marked `verified`.

4. **Fan variants are a preview bundle plan, not release-ready.** No room
   bundle in the **base matrix** includes a fan driver. The Bathroom /
   Kitchen fan-control variants in
   [`config/room-bundle-fan-variants.json`](../config/room-bundle-fan-variants.json)
   (`ROOM-BUNDLE-FAN-VARIANTS-002`, revised by `ROOM-BUNDLE-FAN-CONFIGS-001`)
   carry built full-composition configs for the five buildable variants
   (Bathroom PWM/DAC, Kitchen Relay/DAC/PWM are now
   `buildable-preview-compile-validated` — `ROOM-BUNDLE-FAN-COMPILE-RESULTS-001`
   recorded a successful hosted full ESPHome compile, run `26913592989`,
   firmware-build proof only; see
   [`docs/room-bundle-fan-compile-results.md`](room-bundle-fan-compile-results.md));
   all five now **also carry a published Advanced-install-only preview `.bin`**
   after `ROOM-BUNDLE-FAN-PUBLISH-RESULTS-001` (`Room-Bundle Fan Firmware
   Publish`, run `26947595936`, ref `main`, 2026-06-04; conclusion `success`) to
   the shared `v1.0.0-preview` prerelease — firmware-build / release proof only
   (per-variant publish evidence recorded in
   [`config/room-bundle-fan-variants.json`](../config/room-bundle-fan-variants.json));
   TRIAC stays advanced / manual-warning-only and
   build-blocked under `HW-005` (no build, no artifact). The two FanDAC configs additionally require
   the GP8403 IC2 `0x5A` address override + DIP switch — compiled with the
   `0x5A` override (compile-time only; **not** bench-verified, bench follow-up
   `FANDAC-I2C-ADDR-001` stays pending, checklist + evidence template at
   [`docs/hardware/fandac-i2c-address-verification.md`](hardware/fandac-i2c-address-verification.md)).
   The five published previews are now **preview WebFlash-import eligible**
   under `ROOM-BUNDLE-FAN-WEBFLASH-ELIGIBILITY-001` (each carries a
   `webflash_import_eligibility.eligible: true` block in
   [`config/room-bundle-fan-variants.json`](../config/room-bundle-fan-variants.json)
   and on its [`config/product-catalog.json`](../config/product-catalog.json)
   row), authorising an Advanced-install-only, acknowledgement-gated **preview
   import only** — the downstream WebFlash import / easy-mode exposure stays the
   separately queued `WF-IMPORT-FAN-BUNDLES-001` follow-up. Every variant still
   keeps `webflash_exposed: false` (no committed `config/webflash-builds.json`
   row), `webflash_easy_mode_eligible: false`, and `stable_status: blocked`,
   catalog `status` stays `hardware-pending` / `webflash_build_matrix: false`,
   and none is marked release-ready, stable, recommended, default, or buyable by
   this audit.

---

## Bench / evidence handoff (forward pointers only)

The bench tasks below own the outstanding hardware evidence for the
non-eligible bundles. They are **forward pointers** — no bench evidence
is claimed, run, or fabricated by this PR, and every task remains owed
until physical hardware exists.

| Bench task | Owns evidence for | Status (as recorded elsewhere) |
|---|---|---|
| `S360-100-BENCH-001` | Core bench / manufacturing review incl. J2 PoE-harness identity (HW-002 OQ#6) — every PoE bundle | `pending — bench/manufacturing evidence required` ([board-readiness-matrix](hardware/board-readiness-matrix.md)) |
| `S360-300-BENCH-001` | LED ring bench evidence — Living / Corridor | `pending — bench hardware evidence required` ([board-readiness-matrix](hardware/board-readiness-matrix.md)) |
| `WF-HW-TEST-001` / `WF-HW-TEST-003` | LED operator flash proof — Living / Corridor | preview-to-stable gauntlet rows ([preview-to-stable-promotion-gates.md](preview-to-stable-promotion-gates.md)) |
| AirIQ sensor-stack bench (under `STABLE-TARGET-AIRIQ-001`) | SPS30 / SGP41 / SCD41 / BMP390 evidence — Kitchen | owed ([stable-target-expansion-plan.md](stable-target-expansion-plan.md)) |
| `PRE-HW-PREP-POE-410-001` | S360-410 PoE isolation / Hi-pot / `PACKAGE-POE-410-001` — every PoE bundle | queued, ARTIFACT-gated ([pre-hardware-prep-plan.md](pre-hardware-prep-plan.md) §7) |
| `FANDAC-I2C-ADDR-001` | FanDAC GP8403 IC2 → `0x5A` I²C-address mapping vs VentIQ/AirIQ SGP41 @ `0x59` — Bathroom / Kitchen DAC variants | `pending — bench hardware evidence required` ([fandac-i2c-address-verification.md](hardware/fandac-i2c-address-verification.md)) |

---

## Guardrails (explicitly NOT changed)

- **No bundle promoted.** No `current_release_status` is changed in
  [`config/room-bundle-skus.json`](../config/room-bundle-skus.json); no
  config target is promoted to `preview` / `stable` / `production`.
- **No WebFlash enabled.** No row added to
  [`config/webflash-builds.json`](../config/webflash-builds.json); no
  `artifact_name` set; no `webflash_build_matrix` flipped; the WebFlash
  repo (`sense360store/webflash`) is untouched.
- **No artifacts added.** No `.bin`, checksum, build-info,
  [`firmware/sources.json`](../firmware/sources.json), or `manifest.json`;
  no GitHub Release / tag.
- **S360-410 not marked verified.** `schematic_status` stays
  `cataloged_unverified`; the Release-One PoE "schematic verification
  pending" caveat is preserved verbatim.
- **LED not marked stable.** `S360-300` stays `preview`; the Living /
  Corridor bundles stay `preview-candidate`.
- **Fan variants not release-ready.** The
  [`config/room-bundle-fan-variants.json`](../config/room-bundle-fan-variants.json)
  variants stay not release-ready and not WebFlash-exposed
  (`webflash_exposed: false`); no fan bundle SKU is introduced into the base
  matrix. (Later promoted to a preview bundle plan by
  `ROOM-BUNDLE-FAN-VARIANTS-002`, still non-stable / non-buyable.)
- **No `config/*.json` / `packages/**` / `products/**` edits.** This PR
  is a single new doc plus the `UPCOMING_PR.md` entry.

---

## Validation

This PR adds no new config or code, so the existing suite is unchanged:

- `python3 tests/test_room_bundle_skus.py` — unchanged.
- `python3 tests/test_room_bundle_fan_variants.py` — unchanged.
- `python3 tests/validate_configs.py` — unchanged.
- `python3 scripts/validate_compile_targets.py --metadata-only` —
  unchanged.
- `python3 tests/validate_webflash_builds.py` — unchanged.
- `python3 tests/test_product_catalog.py` — unchanged.
- `python3 -m unittest discover -s tests -p "test_*.py"` — full suite
  passes; no new test is required (documentation-only, no new
  machine-readable contract).

---

## Cross-references

- Room bundle SKU matrix:
  [`docs/sense360-room-bundles.md`](sense360-room-bundles.md) /
  [`config/room-bundle-skus.json`](../config/room-bundle-skus.json) —
  `BUNDLE-SKU-MATRIX-001`. Source of truth for the bundle SKUs, included
  boards, and likely firmware config targets audited here.
- Room-bundle fan variants:
  [`config/room-bundle-fan-variants.json`](../config/room-bundle-fan-variants.json)
  — `ROOM-BUNDLE-FAN-VARIANTS-002`. Preview bundle plan; not release-ready,
  non-stable, non-buyable.
- Board readiness matrix:
  [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
  — `HW-GAP-001`. Source of truth for the per-board hardware-evidence and
  bench / operator-proof state cited in the Blocking-hardware-evidence
  and Bench-task columns.
- Room firmware release matrix:
  [`docs/room-firmware-release-matrix.md`](room-firmware-release-matrix.md)
  — `RELEASE-PIPELINE-ROOM-MATRIX-001`. Source of truth for the per-config
  release channel, WebFlash, and release-note status.
- Room firmware release notes:
  [`docs/room-firmware-release-notes.md`](room-firmware-release-notes.md)
  — `RELEASE-NOTES-PIPELINE-001`. Source of truth for the release-note
  status column.
- Firmware combination matrix:
  [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json).
  Source of truth for each config target's status.
- WebFlash builds matrix:
  [`config/webflash-builds.json`](../config/webflash-builds.json). Sole
  source of WebFlash / release eligibility; unchanged by this PR.
- Stable target expansion plan:
  [`docs/stable-target-expansion-plan.md`](stable-target-expansion-plan.md)
  — source of truth for the `STABLE-TARGET-*-001` follow-up PR sequence
  that owns each non-eligible bundle's promotion.
- Preview-to-stable gauntlet:
  [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
  — `RELEASE-006`. Owns the LED `WF-HW-TEST-001` / `WF-HW-TEST-003` gates.
- Pre-hardware preparation plan:
  [`docs/pre-hardware-prep-plan.md`](pre-hardware-prep-plan.md) —
  `PRE-HARDWARE-PREP-PLAN-001`. Owns `PRE-HW-PREP-POE-410-001` and the
  driver/PSU design-complete program.

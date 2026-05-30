# Sense360 PoE Room Bundle SKU Matrix (BUNDLE-SKU-MATRIX-001)

## Purpose and scope

This document is the **canonical** Sense360 PoE room bundle SKU matrix.
A **room bundle SKU** is a sellable, customer-facing kit identifier
(for example `S360-KIT-BATH-P`) that names the physical Sense360 boards
shipped together as a single room kit. It sits **above** the board /
firmware layers and connects to the existing board SKU, YAML, and
release-target documentation.

It exists because the prior planning layers in this repo capture three
neighbouring but distinct identifier spaces and none was a canonical
commercial room-bundle layer:

- **Board SKU** — a physical PCB. Source of truth:
  [`config/hardware-catalog.json`](../config/hardware-catalog.json) /
  [`docs/hardware-catalog.md`](hardware-catalog.md).
- **Firmware config string** — a YAML / release target token sequence.
  Source of truth:
  [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json),
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  [`config/product-catalog.json`](../config/product-catalog.json).
- **Kit intent** — a productized planning record that groups boards by
  use case (`bathroom`, `kitchen-or-duct-fan`). Source of truth:
  [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json) /
  [`docs/kit-intent-matrix.md`](kit-intent-matrix.md).

This document and its data file
[`config/room-bundle-skus.json`](../config/room-bundle-skus.json) add a
**room-bundle SKU** layer that names the Release-One PoE room kits as a
sellable set and maps each onto (a) the boards shipped in the bundle and
(b) the **likely firmware config target** that those boards together
produce, along with the current release status of that firmware config
target and the missing stable-promotion gates.

### Identifier separation

Four identifier spaces are deliberately kept separate.

| Identifier space | Example | Source of truth |
|---|---|---|
| **Board SKU** | `S360-100`, `S360-200`, `S360-210`, `S360-211`, `S360-300`, `S360-410` | [`config/hardware-catalog.json`](../config/hardware-catalog.json) |
| **Firmware config string** | `Ceiling-POE-VentIQ-RoomIQ`, `Ceiling-POE-VentIQ-RoomIQ-LED` | [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json), [`config/webflash-builds.json`](../config/webflash-builds.json) |
| **Release artifact name** | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` | [`config/webflash-builds.json`](../config/webflash-builds.json), [`config/product-catalog.json`](../config/product-catalog.json) |
| **Room bundle SKU** *(this doc)* | `S360-KIT-BATH-P` | [`config/room-bundle-skus.json`](../config/room-bundle-skus.json) |

A bundle SKU is **not** a board SKU, **not** a firmware config string,
and **not** a release artifact name. A bundle SKU may map onto a
current release target, a preview target, a stable candidate, or a
blocked / missing target. A bundle's name and SKU **do not** become
the release artifact name automatically: the release artifact name is
derived from the firmware config string per
[`docs/all-yaml-release-matrix.md`](all-yaml-release-matrix.md) §
Stable-promotion criteria G5.

### Bundle SKU vs the YAML bundle layer (`products/bundles/`)

A **room bundle SKU** (this document — a sellable kit identifier such as
`S360-KIT-BATH-P`) must not be confused with the firmware **YAML bundle layer**
introduced by the board/bundle refactor
([`docs/arch-board-bundle-plan.md`](arch-board-bundle-plan.md) §2.2). The YAML
bundle layer lives under [`products/bundles/`](../products/bundles/) and holds
one YAML file **named 1:1 to a firmware config string** (e.g.
`products/bundles/ceiling-poe-ventiq-roomiq.yaml` for `Ceiling-POE-VentIQ-RoomIQ`),
each assembling `boards + expansions + base + profiles`. That YAML bundle is a
**firmware config string** artefact, not a room bundle SKU:

- A YAML bundle file name matches a **firmware config string**
  ([`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json) /
  [`config/webflash-builds.json`](../config/webflash-builds.json)), not a room
  bundle SKU in
  [`config/room-bundle-skus.json`](../config/room-bundle-skus.json).
- A room bundle SKU maps onto a **likely firmware config target** (the
  `likely_firmware_config_target` field), which in turn is the config string the
  matching `products/bundles/*.yaml` is named for. The SKU → config-string
  mapping is the same one tabulated in the canonical matrix below; this PR
  changes **no** SKU and adds **no** new bundle.
- The room bundle SKU stays the customer-facing kit identifier; the YAML bundle
  stays an esphome-public-internal composition file. Neither becomes a release
  artifact name — that is still derived from the firmware config string per
  [`docs/all-yaml-release-matrix.md`](all-yaml-release-matrix.md) §
  Stable-promotion criteria G5.

This document does **not** introduce, rename, or fan-out any
`products/bundles/*.yaml` file; it only cross-links the existing YAML bundle
layer so the two "bundle" meanings stay distinct.

### This document is documentation only

BUNDLE-SKU-MATRIX-001 — this PR — does **not**:

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
  [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json),
  [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json),
  [`config/hardware-catalog.json`](../config/hardware-catalog.json),
  or [`config/webflash-compatibility.json`](../config/webflash-compatibility.json);
- write [`firmware/sources.json`](../firmware/sources.json) or
  `manifest.json`;
- promote LED from `preview` to `stable`;
- promote FanRelay / FanPWM / FanDAC out of `manual-candidate-only`;
- add an `artifact_name` to any product;
- flip any `webflash_build_matrix` value;
- add a fan bundle SKU (fan bundles are **not** introduced by this PR);
- invent unsupported firmware configs;
- claim that every bundle already has stable firmware;
- treat a bundle SKU as a board SKU;
- treat a bundle SKU as a firmware artifact name.

---

## Board SKUs referenced

The bundle matrix references only the canonical board SKUs already in
[`config/hardware-catalog.json`](../config/hardware-catalog.json). For
self-containment, the boards in scope for the PoE room bundles defined
here are:

| Board SKU | Friendly name | Role |
|---|---|---|
| `S360-100` | Sense360 Core | Required hub board (ESP32-S3 + connectors). |
| `S360-200` | Sense360 RoomIQ | Presence + comfort sensor stack. |
| `S360-210` | Sense360 AirIQ | Full air-quality sensor stack (CO2 / VOC / gas / PM / HCHO connectors). |
| `S360-211` | Sense360 VentIQ | Smaller bathroom-grade air-quality stack. |
| `S360-300` | Sense360 LED | LED status ring (WS2812B). **Preview-only.** |
| `S360-410` | Sense360 PoE PSU | PoE to 5V power supply. |

Out-of-scope today (not referenced by any bundle in this PR):
`S360-310`, `S360-311`, `S360-312` (fan drivers — manual-candidate-only),
`S360-320` (TRIAC — blocked, HW-005), `S360-400` (240V PSU —
compliance-blocked).

---

## Canonical PoE room bundle SKU matrix

The five bundles below are the canonical Sense360 PoE room bundle
SKUs. Every bundle includes the Sense360 Core (`S360-100`) and the
Sense360 PoE PSU (`S360-410`) — these are the mandatory hub + power
spine for every PoE room kit.

The Sense360 Core (`S360-100`) is the **central Core / backplane
controller** for the module stack: every room module (RoomIQ, AirIQ,
VentIQ, LED, Relay, PWM, DAC, TRIAC) connects through a dedicated
connector on the Core, and the Core is the only board that carries
the MCU. Each bundle therefore derives from
**`S360-100` Core + room modules + `S360-410` PoE PSU**. This
architectural framing — including the per-connector module SKU
mapping on the new R4 schematic — is recorded in
[`docs/hardware/s360-100-core-architecture.md`](hardware/s360-100-core-architecture.md)
(S360-100-NATIVE-TACH-PULSE-001 — R4 refresh). The canonical
per-pin Core-to-module connector pin map (per-connector matrix +
per-connector pin tables with `Pin number` / `Core net` / `ESP32
GPIO` / `Module-side signal` / `Signal type` / `Voltage` /
`Status` columns) is recorded in
[`docs/hardware/s360-100-core-connector-pin-map.md`](hardware/s360-100-core-connector-pin-map.md)
(S360-100-CONNECTOR-PINMAP-001). The per-module **module-side**
view of the same pin map is recorded in one document per board
under MODULE-PINMAPS-GDRIVE-001:
[`s360-200-module-pinmap.md`](hardware/s360-200-module-pinmap.md),
[`s360-210-module-pinmap.md`](hardware/s360-210-module-pinmap.md),
[`s360-211-module-pinmap.md`](hardware/s360-211-module-pinmap.md),
[`s360-300-module-pinmap.md`](hardware/s360-300-module-pinmap.md),
[`s360-310-module-pinmap.md`](hardware/s360-310-module-pinmap.md),
[`s360-311-module-pinmap.md`](hardware/s360-311-module-pinmap.md),
[`s360-312-module-pinmap.md`](hardware/s360-312-module-pinmap.md),
[`s360-320-module-pinmap.md`](hardware/s360-320-module-pinmap.md),
[`s360-400-module-pinmap.md`](hardware/s360-400-module-pinmap.md),
[`s360-410-module-pinmap.md`](hardware/s360-410-module-pinmap.md).

| Bundle SKU | Bundle name | Included boards | Likely firmware config target | Current release status | Missing gates (top of stack) |
|---|---|---|---|---|---|
| `S360-KIT-BATH-P` | Sense360 Bathroom Bundle — PoE | `S360-100` Sense360 Core; `S360-200` Sense360 RoomIQ; `S360-211` Sense360 VentIQ; `S360-410` Sense360 PoE PSU | `Ceiling-POE-VentIQ-RoomIQ` | **`stable-release`** (already exists) | None — Release-One ships this. |
| `S360-KIT-KITCHEN-P` | Sense360 Kitchen Bundle — PoE | `S360-100` Sense360 Core; `S360-200` Sense360 RoomIQ; `S360-210` Sense360 AirIQ; `S360-410` Sense360 PoE PSU | `Ceiling-POE-AirIQ-RoomIQ` | `stable-candidate` (needs AirIQ promotion) | G1–G8; AirIQ-stack hardware evidence (SPS30 / SGP41 / SCD41 / BMP390); PoE-410 chain (`PRODUCT-POE-410-001`). Owned by `STABLE-TARGET-AIRIQ-001` → `STABLE-TARGET-AIRIQ-ROOMIQ-001`. |
| `S360-KIT-LIVING-P` | Sense360 Living Room Bundle — PoE | `S360-100` Sense360 Core; `S360-200` Sense360 RoomIQ; `S360-300` Sense360 LED; `S360-410` Sense360 PoE PSU | `Ceiling-POE-RoomIQ-LED` (or equivalent) | `preview-candidate` (LED remains preview) | G1–G8; PoE-410 chain; G10 preview-to-stable gauntlet. LED stays preview until `LED-STABLE-PROMOTION-001` closes. |
| `S360-KIT-BEDROOM-P` | Sense360 Bedroom Bundle — PoE | `S360-100` Sense360 Core; `S360-200` Sense360 RoomIQ; `S360-410` Sense360 PoE PSU | `Ceiling-POE-RoomIQ` | `stable-candidate` | G1–G8; PoE-410 chain. Owned by `STABLE-TARGET-ROOMIQ-001` (after `STABLE-TARGET-CORE-001` shared PoE-410 closure). |
| `S360-KIT-CORRIDOR-P` | Sense360 Landing / Corridor Bundle — PoE | `S360-100` Sense360 Core; `S360-200` Sense360 RoomIQ; `S360-300` Sense360 LED; `S360-410` Sense360 PoE PSU | `Ceiling-POE-RoomIQ-LED` (or equivalent) | `preview-candidate` (LED remains preview) | Same as `S360-KIT-LIVING-P`. Living and Corridor currently share the same included board set; a future room-specific default firmware (for example a corridor-specific LED pattern or presence profile) would differentiate them. |

Notes:

- **`stable-release`** means the bundle's likely firmware config target
  is **already** in [`config/webflash-builds.json`](../config/webflash-builds.json)
  with `channel: stable`. Only `S360-KIT-BATH-P` qualifies today.
- **`stable-candidate`** means every blocker is on the standard
  product-onboarding axis (no LED, no fan, no TRIAC, no 240V PSU) and
  promotion is owned by a named `STABLE-TARGET-*-001` follow-up PR;
  promotion is **not** approved by this PR.
- **`preview-candidate`** means the bundle's likely firmware config
  target carries the LED token and so is gated by the preview-to-stable
  gauntlet at
  [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md);
  promotion is **not** approved by this PR.
- **Living and Corridor currently have the same included board set**
  unless a future room-specific firmware / default config differentiates
  them. Both stay `preview-candidate` while LED remains preview.

---

## Missing-gate reference

The `Missing gates` column references the gate vocabulary defined in
[`docs/stable-target-expansion-plan.md` § Stable-promotion gate checklist](stable-target-expansion-plan.md#stable-promotion-gate-checklist).
The full vocabulary is summarised here for the reader's convenience;
the source of truth lives in
[`docs/stable-target-expansion-plan.md`](stable-target-expansion-plan.md)
and [`docs/all-yaml-release-matrix.md`](all-yaml-release-matrix.md).

| Gate | Meaning |
|---|---|
| G1 | Top-level canonical product YAML exists under `products/`. |
| G2 | Product-catalog row exists in `config/product-catalog.json`. |
| G3 | Top-level full compile validated in `config/compile-only-targets.json`. |
| G4 | WebFlash wrapper exists under `products/webflash/`. |
| G5 | `artifact_name` present in catalog and `config/webflash-builds.json`. |
| G6 | `config/webflash-builds.json` row exists for the config. |
| G7 | Release notes can be generated without overrides. |
| G8 | No blocking hardware / compliance caveat (per-board / per-package / per-family readiness rows). |
| G9 | Not currently `manual-candidate-only`. |
| G10 | Not currently `preview-only` (preview-to-stable gauntlet closed). |

Every bundle in this matrix (apart from `S360-KIT-BATH-P`) inherits
the shared `PRODUCT-POE-410-001` / `S360-410` schematic verification
chain (Release-One PoE caveat) as part of G8, because every PoE
bundle ships the Sense360 PoE PSU.

---

## Promotion ownership — bundle SKU vs follow-up PR

Adding a bundle SKU to this matrix **does not** authorise the
corresponding firmware config target's promotion to stable or
preview. Promotion is owned by the named follow-up PR in
[`docs/stable-target-expansion-plan.md`](stable-target-expansion-plan.md)
§ Recommended follow-up PR sequence.

| Bundle SKU | Owning follow-up PR (for firmware config promotion) |
|---|---|
| `S360-KIT-BATH-P` | None — `Ceiling-POE-VentIQ-RoomIQ` is already stable. |
| `S360-KIT-KITCHEN-P` | `STABLE-TARGET-AIRIQ-001` → `STABLE-TARGET-AIRIQ-ROOMIQ-001` (after PoE-410 closure). |
| `S360-KIT-LIVING-P` | `LED-STABLE-PROMOTION-001` (alias of `RELEASE-007` / `PRODUCT-LED-STABLE-001`), plus a separate `STABLE-TARGET-ROOMIQ-LED-001`-style slice (not yet scoped) for the no-VentIQ LED variant. Not approved by this PR. |
| `S360-KIT-BEDROOM-P` | `STABLE-TARGET-CORE-001` → `STABLE-TARGET-ROOMIQ-001`. |
| `S360-KIT-CORRIDOR-P` | Same as `S360-KIT-LIVING-P` until a corridor-specific firmware config differentiates them. |

These follow-up PRs are **not** approved or scoped by this PR.

---

## Hard guardrails

- **Bundle SKU is not a board SKU.** Bundle SKUs live in
  [`config/room-bundle-skus.json`](../config/room-bundle-skus.json) and
  reference board SKUs by their canonical
  [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  identifier. The bundle SKU itself is **not** added to the hardware
  catalog.
- **Bundle SKU is not a firmware config string.** Bundle SKUs do not
  appear in
  [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json)
  or
  [`config/webflash-builds.json`](../config/webflash-builds.json). The
  bundle's `likely_firmware_config_target` field points at the firmware
  config string that the included boards would produce; it is not the
  bundle SKU.
- **Bundle SKU is not a release artifact name.** Release artifact names
  follow the
  `Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin` shape derived
  from the firmware config string, not from the bundle SKU.
- **Every bundle includes Core and PoE PSU.** Every row's
  `included_board_skus` must contain `S360-100` and `S360-410`. The
  contract test asserts this.
- **LED bundles are not stable.** Any bundle whose
  `likely_firmware_config_target` contains the `LED` token (or whose
  `included_board_skus` contains `S360-300`) is `preview-candidate` or
  `preview-release` at most; never `stable-release` or
  `stable-candidate`. The contract test asserts this.
- **No fan bundles in this PR.** No bundle's `included_board_skus` may
  contain `S360-310`, `S360-311`, `S360-312`, or `S360-320`. The
  contract test asserts this. Fan bundles are owned by their own
  per-family follow-up PR sequences (`WEBFLASH-RELAY-001` /
  `WEBFLASH-PWM-001` / `WEBFLASH-DAC-001` / FanTRIAC HW-005 chain).
- **Bundle SKU names do not become release artifact names
  automatically.** The release artifact name is derived from the
  firmware config string per
  [`docs/all-yaml-release-matrix.md`](all-yaml-release-matrix.md) §
  Stable-promotion criteria G5; this PR adds no `artifact_name` to any
  product.
- **Bundle SKUs are unique.** The contract test asserts this.

---

## Relationship to the kit intent matrix

The earlier productized kit-intent matrix
([`docs/kit-intent-matrix.md`](kit-intent-matrix.md) /
[`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json),
KIT-MATRIX-001 / PR #542) groups boards by **use case** (`bathroom`,
`kitchen-or-duct-fan`) and uses the `S360-KIT-*-POE` / `S360-KIT-*-LED`
/ `S360-KIT-*-RELAY` / `S360-KIT-*-TRIAC` / `S360-KIT-DUCT-*` naming
convention for the planning-time kit-intent rows.

This document and
[`config/room-bundle-skus.json`](../config/room-bundle-skus.json) add
the **commercial room-bundle** layer that uses the `S360-KIT-{ROOM}-P`
naming convention (the `-P` suffix denotes the PoE-powered room
bundle). The two layers are complementary:

- **Kit intent matrix** (`config/kit-intent-matrix.json`) — planning /
  productization intent across the firmware combination matrix; six
  rows today including non-PoE / fan / TRIAC futures.
- **Room bundle SKU matrix** (`config/room-bundle-skus.json`, this PR)
  — sellable PoE-only room bundle SKUs; five rows today; restricted to
  the Core + RoomIQ + (optional VentIQ / AirIQ / LED) + PoE PSU
  combinations.

Neither layer implies WebFlash exposure or release readiness on its
own; both defer to
[`config/webflash-builds.json`](../config/webflash-builds.json) and
the WebFlash manifest for installability, and to
[`docs/stable-target-expansion-plan.md`](stable-target-expansion-plan.md)
for promotion ownership.

---

## Validation

The matrix is reproduced and locked in by:

- `python3 tests/test_room_bundle_skus.py` — bundle SKU contract tests
  (uniqueness; included boards reference valid known board SKUs; every
  bundle has at least Core and PoE PSU; LED bundles are not marked
  stable while LED remains preview; no fan bundle SKUs are introduced
  by this PR; bundle SKU names do not become release artifact names
  automatically).
- `python3 scripts/classify_all_yaml_release_matrix.py --summary` —
  unchanged: `stable=1, preview=1, manual=3, compile-only=7, blocked=1,
  not-a-product-entrypoint=35`.
- `python3 scripts/list_release_targets.py` — unchanged: two rows,
  stable `Ceiling-POE-VentIQ-RoomIQ`, preview
  `Ceiling-POE-VentIQ-RoomIQ-LED`.
- `python3 tests/test_all_yaml_release_matrix.py` — unchanged.
- `python3 tests/test_release_product_selection.py` — unchanged.
- `python3 tests/validate_configs.py` — unchanged.
- `python3 scripts/validate_compile_targets.py --metadata-only` —
  unchanged.
- `python3 tests/validate_webflash_builds.py` — unchanged.
- `python3 tests/test_product_catalog.py` — unchanged.
- `python3 -m unittest discover -s tests -p "test_*.py"` — full suite
  passes; bundle SKU contract tests added by this PR.

---

## Cross-references

- All-YAML release matrix:
  [`docs/all-yaml-release-matrix.md`](all-yaml-release-matrix.md) —
  STABLE-RELEASE-MATRIX-ALL-YAML-001. Source of truth for the release
  class (`stable-release` / `preview-release` / `manual-candidate-only`
  / `compile-only` / `blocked` / `not-a-product-entrypoint`) the
  bundle's likely firmware config target carries.
- Stable target expansion plan:
  [`docs/stable-target-expansion-plan.md`](stable-target-expansion-plan.md)
  — STABLE-TARGET-EXPANSION-PLAN-001. Source of truth for the G1–G10
  gate vocabulary and the named `STABLE-TARGET-*-001` follow-up PR
  sequence that owns each non-stable bundle's firmware config target
  promotion.
- Room firmware release matrix:
  [`docs/room-firmware-release-matrix.md`](room-firmware-release-matrix.md)
  — RELEASE-PIPELINE-ROOM-MATRIX-001. Source of truth for the
  per-room-firmware release pipeline status of each likely firmware
  config target.
- Kit intent matrix:
  [`docs/kit-intent-matrix.md`](kit-intent-matrix.md) — KIT-MATRIX-001.
  Sibling layer; productization / use-case planning rather than
  sellable room bundles.
- Product readiness gate:
  [`docs/product-readiness-matrix.md`](product-readiness-matrix.md) —
  PRODUCT-GAP-001. Product-layer readiness this matrix consults.
- WebFlash exposure gate:
  [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md)
  — WEBFLASH-GAP-001.
- Release artifact gate:
  [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
  — RELEASE-GAP-001.
- Preview-to-stable gauntlet:
  [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
  — RELEASE-006.
- LED preview decision:
  [`docs/product-led-preview-decision.md`](product-led-preview-decision.md).
- Hardware catalog:
  [`config/hardware-catalog.json`](../config/hardware-catalog.json) /
  [`docs/hardware-catalog.md`](hardware-catalog.md). Source of truth
  for the canonical board SKUs the bundles reference.
- Firmware combination matrix:
  [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json).
  Source of truth for the firmware config strings the bundles' likely
  firmware config target references.
- WebFlash builds matrix:
  [`config/webflash-builds.json`](../config/webflash-builds.json).
  Sole source of release eligibility; unchanged by this PR.
- Shipping configuration: [`docs/release-one.md`](release-one.md).

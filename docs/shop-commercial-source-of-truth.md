# Shop Commercial Source of Truth (SHOP-COMMERCIAL-SOURCE-OF-TRUTH-001)

**Canonical id:** `SHOP-COMMERCIAL-SOURCE-OF-TRUTH-001`
**Type:** Commercial policy / documentation only. This document and its data
file [`config/shop-commercial-source-of-truth.json`](../config/shop-commercial-source-of-truth.json)
**do not** change firmware behaviour, publish firmware, build or attach any
artifact, edit `manifest.json` / `firmware/sources.json`, add a
`config/webflash-builds.json` row, flip any `schematic_status`, change any
product-catalog lifecycle, or touch the WebFlash repo. They record the
commercial decisions that must be settled **before** customer-facing shop pages
are published, so that product naming, ecommerce copy, WebFlash links,
candidate-bundle visibility, and claims stay consistent.

## Purpose and scope

This is the **single canonical** commercial launch source of truth for the
first Sense360 shop. It answers the open shop-launch questions and pins them to
the existing repo sources of truth:

| Layer | Source of truth |
|---|---|
| Room bundle SKUs (sellable kit identifiers) | [`config/room-bundle-skus.json`](../config/room-bundle-skus.json) · [`docs/sense360-room-bundles.md`](sense360-room-bundles.md) |
| Product catalog (lifecycle) | [`config/product-catalog.json`](../config/product-catalog.json) · [`docs/release-one.md` (archived)](archive-index.md) |
| Board / module catalog | [`config/hardware-catalog.json`](../config/hardware-catalog.json) · [`docs/hardware-catalog.md`](hardware-catalog.md) |
| Shippable WebFlash builds | [`config/webflash-builds.json`](../config/webflash-builds.json) |
| Kit-intent planning layer | [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json) · [`docs/kit-intent-matrix.md`](kit-intent-matrix.md) |
| Repo status / roadmap | [`docs/sense360-roadmap-status.md`](sense360-roadmap-status.md) |

Where this document and a source-of-truth file ever disagree, **the
source-of-truth file wins** and this document is the one to fix.

---

## 1. Canonical shop SKU

| Field | Value |
|---|---|
| **Shop SKU** | `S360-KIT-BATH-P` |
| **Shop product title** | **Sense360 Bathroom Bundle — PoE** |
| Firmware config | `Ceiling-POE-VentIQ-RoomIQ` |
| Production artifact | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` |
| Boards | `S360-100` Core · `S360-200` RoomIQ · `S360-211` VentIQ · `S360-410` PoE PSU |
| Bundle status | `stable-release` (the only stable-release bundle today) |

- Use `S360-KIT-BATH-P` as the customer-facing shop SKU. It is the canonical
  room-bundle SKU in [`config/room-bundle-skus.json`](../config/room-bundle-skus.json)
  and **is not renamed** by this document.
- Treat **`S360-KIT-BATH-POE`** as a **legacy/alias spelling only**. It is the
  kit-intent `kit_id` in [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json)
  (and is mirrored by the WebFlash kit presets); resolve any external reference
  back to `S360-KIT-BATH-P`.
- **Do not** use `S360-KIT-CEILING-VENTIQ-ROOMIQ-POE` as a customer-facing SKU.
  It mirrors the firmware config string too closely (it appears only as a
  WebFlash `kits.json` kit id) and is **not** a shop SKU.

A bundle SKU is **not** a board SKU, a firmware config string, or a release
artifact name — see [`docs/sense360-room-bundles.md`](sense360-room-bundles.md)
§ Identifier separation.

---

## 2. Launch sale posture

- The **first shop product is the complete Bathroom PoE room bundle only**
  (`shop_posture: sellable-complete-room-bundle`).
- **Do not sell individual boards publicly at launch**
  (`individual_boards_public_sale: false`).
- Individual boards may still be documented as internal board SKUs, service
  parts, developer parts, or future add-ons — but **not** as the primary shop
  product line.

The shop sells one thing at launch: the complete room kit.

---

## 3. Bathroom PoE readiness wording

S360-410 (PoE PSU) remains `cataloged_unverified` in
[`config/hardware-catalog.json`](../config/hardware-catalog.json) (see
[`docs/sense360-roadmap-status.md` §6.1](sense360-roadmap-status.md#61-poe--s360-410-blocker)),
so commercial copy must not overclaim hardware certification, compliance, or
broad verification.

| Allowed readiness wording | Not allowed readiness wording |
|---|---|
| stable firmware available | hardware certified |
| Release-One firmware target | compliance certified |
| WebFlash install supported | verified PoE hardware |
| complete room kit | safety certified |
| | bench-proven for every installation |
| | prevents mold / detects mold |
| | guarantees condensation prevention |

---

## 4. Candidate bundle visibility

The four non-launch room bundles (`S360-KIT-KITCHEN-P`, `S360-KIT-LIVING-P`,
`S360-KIT-BEDROOM-P`, `S360-KIT-CORRIDOR-P`) are planning / preview /
stable-candidate records in [`config/room-bundle-skus.json`](../config/room-bundle-skus.json),
**not** public sale commitments.

- **Default:** hidden from normal shop navigation.
- **Waitlist / coming-soon pages** may exist **only if explicitly labelled**:
  - coming soon
  - not available to buy
  - firmware preview / stable-candidate where applicable
  - hardware gates not closed
- **No buy button** (`buy_button_allowed: false`).
- Do **not** imply availability, a delivery date, or production readiness.

---

## 5. Customer WebFlash URL

| Purpose | URL |
|---|---|
| **Customer-facing firmware flashing** | **`https://flash.sense360.com`** |
| Technical fallback / deployment origin | `https://sense360store.github.io/WebFlash/` |
| Reserved (future portal) | `https://mysense360.com` |

- Customer-facing browser flashing should point at **`https://flash.sense360.com`**.
- The GitHub Pages URL remains the technical fallback / deployment origin only.
- `mysense360.com` is **reserved** for a future customer portal, account, setup,
  or support experience — it is **not** the firmware flashing URL unless a
  future decision changes this.

This document does not change any URL inside the WebFlash repo, `manifest.json`,
or `firmware/sources.json`.

---

## 6. Approved ecommerce claims

**Allowed** (may be used in shop copy as-is):

- "Monitors bathroom environment"
- "Tracks humidity, temperature, presence, and bathroom air-quality signals"
- "Designed for Home Assistant / ESPHome users"
- "Supports browser-based firmware installation with WebFlash"
- "Can help inform automations such as ventilation reminders or alerts"
- "PoE-powered room sensing kit"
- "Includes Sense360 Core, RoomIQ, VentIQ, and PoE PSU"

**Not allowed** without separate legal/commercial approval and evidence:

- "Prevents mold" / "Detects mold"
- "Eliminates condensation" / "Prevents condensation"
- "Certified air-quality monitor"
- "Medical-grade"
- "Safety certified"
- "Controls extractor fans" (for the base Bathroom PoE kit)
- "Mains fan control" / "TRIAC fan control"
- "Guaranteed ventilation compliance"
- Any claim that implies a certified life-safety, building-code, medical, or
  compliance function.

---

## 7. Fan-control copy

- Fan-control products may be mentioned **only** as future / preview /
  installer / manual-candidate where already recorded
  ([`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json),
  [`docs/manual-install-fan-candidates.md` (archived)](archive-index.md),
  [`config/room-bundle-fan-variants.json`](../config/room-bundle-fan-variants.json)).
- **Do not** market fan control as part of the base Bathroom PoE kit — the base
  kit ships no fan driver.
- **Do not** add TRIAC (`S360-320`) as recommended, default, stable, or
  customer-facing. TRIAC remains blocked by `HW-005` (see
  [`docs/release-one.md` (archived)](archive-index.md) and
  [`docs/sense360-roadmap-status.md` §6](sense360-roadmap-status.md#6-hardware-blockers)).

---

## Hard guardrails

This document and its config must never:

- rename the canonical room-bundle SKU away from `S360-KIT-BATH-P`;
- claim the `S360-410` schematic is verified (it is `cataloged_unverified`);
- claim hardware / compliance certification;
- claim mold prevention or detection;
- claim condensation prevention or elimination;
- claim fan control for the base Bathroom PoE kit;
- expose candidate bundles as buyable;
- sell individual boards as primary launch products;
- add TRIAC to any customer-facing recommendation;
- publish firmware;
- touch the WebFlash repo.

---

## Validation

The commercial source of truth is locked in by:

- `python3 tests/test_shop_commercial_source_of_truth.py` — commercial
  source-of-truth contract tests (canonical launch SKU `S360-KIT-BATH-P`; SKU
  exists in `config/room-bundle-skus.json`; launch firmware config
  `Ceiling-POE-VentIQ-RoomIQ`; launch artifact matches the stable WebFlash
  build; customer WebFlash URL `https://flash.sense360.com`; GitHub Pages is
  fallback only; candidate bundles hidden and not buyable; individual-board
  public sale is false; forbidden claims include mold / condensation / safety
  certification / base-kit fan control; TRIAC never customer-facing /
  recommended / default).
- `python3 tests/validate_configs.py` — unchanged.
- `python3 tests/test_product_catalog.py` — unchanged.
- `python3 tests/validate_webflash_builds.py` — unchanged.
- `python3 scripts/validate_preview_release_targets.py --metadata-only` —
  unchanged.
- `python3 -m unittest discover -s tests -p "test_*.py"` — full suite passes;
  the commercial source-of-truth contract tests added by this PR.

---

## Cross-references

- Room bundle SKU matrix:
  [`docs/sense360-room-bundles.md`](sense360-room-bundles.md) /
  [`config/room-bundle-skus.json`](../config/room-bundle-skus.json) —
  BUNDLE-SKU-MATRIX-001. Canonical room-bundle SKUs the shop draws from.
- Release-One shipping configuration:
  [`docs/release-one.md` (archived)](archive-index.md). Pins the firmware config string,
  product YAML, and artifact name together.
- Product catalog:
  [`config/product-catalog.json`](../config/product-catalog.json). Records the
  Release-One firmware product as `production`.
- Hardware catalog:
  [`config/hardware-catalog.json`](../config/hardware-catalog.json) /
  [`docs/hardware-catalog.md`](hardware-catalog.md). Source of truth for
  `schematic_status` (S360-410 remains `cataloged_unverified`).
- WebFlash builds matrix:
  [`config/webflash-builds.json`](../config/webflash-builds.json). Sole source
  of release eligibility; unchanged by this document.
- Repo status / roadmap:
  [`docs/sense360-roadmap-status.md`](sense360-roadmap-status.md) —
  DOCS-CONSOLIDATION-ROADMAP-001.
- Preview WebFlash build rows:
  [`docs/release-preview-webflash-build-rows.md`](release-preview-webflash-build-rows.md)
  — RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001. Added preview
  `config/webflash-builds.json` rows for the Kitchen / Bedroom / Living /
  Corridor candidate-bundle firmware (`Ceiling-POE-AirIQ-RoomIQ`,
  `Ceiling-POE-RoomIQ`, `Ceiling-POE-RoomIQ-LED`). This **does not** change the
  commercial posture pinned here: the launch SKU stays `S360-KIT-BATH-P`, the
  candidate bundles (`S360-KIT-KITCHEN-P`, `S360-KIT-BEDROOM-P`,
  `S360-KIT-LIVING-P`, `S360-KIT-CORRIDOR-P`) stay hidden / not buyable, the
  customer WebFlash URL stays `https://flash.sense360.com`, and no firmware is
  published. The rows are release-eligibility metadata only.

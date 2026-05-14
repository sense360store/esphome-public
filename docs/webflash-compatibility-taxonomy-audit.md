# WebFlash Compatibility Taxonomy Audit (COMPAT-001)

## Purpose & scope

This document audits [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
against the rest of the repo's current Sense360 truth — the product catalog,
the WebFlash build matrix, the hardware catalog, the per-board documentation
audit, the mains-voltage compliance tracker, and the product onboarding
guide — and records, **per taxonomy token**, what the token means today,
where it lives, whether it is shippable today, and what would have to be
true before it could be added to the WebFlash build matrix in a future PR.

This audit is **documentation only**. It does not:

- change any value in
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  [`config/product-catalog.json`](../config/product-catalog.json), or
  [`config/hardware-catalog.json`](../config/hardware-catalog.json),
- change any product YAML, WebFlash wrapper, package YAML, workflow, script,
  component, or include file,
- promote any module, fan driver, mounting, power source, or token from one
  lifecycle status to another,
- change the Release-One shipping configuration `Ceiling-POE-VentIQ-RoomIQ`
  or the artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`,
- change the FanTRIAC HW-005 blocked status,
- change the Sense360 LED Release-One exclusion status,
- claim any future-token row is preview-ready, stable-ready, production-ready,
  or shippable.

It only records the **current state** of the taxonomy versus the rest of the
repo, the explicit policy that **listing a token in the compatibility
taxonomy does not imply shippability**, and a set of recommended follow-up
PRs that would each be its own scoped change.

If this audit and any source-of-truth document drift, the source-of-truth
document wins and this audit must be updated. The sources of truth this
audit reads from are in
[Source-of-truth separation](#source-of-truth-separation).

> **Note on schematic uploads — HW-007 + HW-008 have landed.** The
> module-side schematic PDFs for `S360-100`, `S360-200`, `S360-210`,
> `S360-211`, and `S360-300` are committed under
> [`docs/hardware/schematics/`](hardware/schematics/) (HW-007), and
> standalone per-board reference docs now exist for AirIQ
> ([`hardware/s360-210-r4-airiq.md`](hardware/s360-210-r4-airiq.md)),
> VentIQ ([`hardware/s360-211-r4-ventiq.md`](hardware/s360-211-r4-ventiq.md)),
> and Sense360 LED ([`hardware/s360-300-r4-led.md`](hardware/s360-300-r4-led.md)).
> HW-008 then aligned the machine-readable
> [`config/hardware-catalog.json`](../config/hardware-catalog.json) with
> that evidence: the five SKUs above are now
> `schematic_status: verified` with `schematic_file` pointing under
> `docs/hardware/schematics/`. The remaining hardware-catalog rows
> (`S360-310`, `S360-311`, `S360-312`, `S360-320`, `S360-400`,
> `S360-410`) stay `cataloged_unverified`. The per-token decision rows
> below are updated to record the new JSON state; **no shippability or
> Release-One verdict cell changes**. The "schematic verification
> pending" caveat for VentIQ in
> [`release-one-hardware-audit.md`](release-one-hardware-audit.md) and
> in COMPAT-001 is retired by HW-008. Promotion of any future `AirIQ`
> / `LED` / `FanTRIAC` / `FanRelay` / `FanPWM` / `FanDAC` / `PWR`
> config string still requires a catalog entry, a build-matrix entry,
> a release-notes draft, a build/release proof, and (for mains-voltage
> modules) a qualified compliance review per
> [`docs/product-onboarding.md`](product-onboarding.md). HW-007 and
> HW-008 together commit hardware-evidence only; they do **not** ship
> any new firmware, do **not** change FanTRIAC's HW-005 blocked
> status, do **not** change LED's Release-One exclusion, and do
> **not** clear the mains-voltage compliance gate for `S360-400` or
> `S360-320`. **Verified schematic evidence is not a
> WebFlash-shippability claim.**

## Source-of-truth separation

The repo splits the four concerns below across four JSON files. Each file
owns exactly one concern. Conflating them would weaken downstream decisions.

| Concern | Source of truth | Validators |
|---|---|---|
| **Taxonomy / grammar** (which tokens exist; how they combine; what is forbidden) | [`config/webflash-compatibility.json`](../config/webflash-compatibility.json) and the prose contract [`docs/webflash-contract.md`](webflash-contract.md). | [`tests/test_webflash_compatibility.py`](../tests/test_webflash_compatibility.py), [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py). |
| **Lifecycle / shippability** (status: `production` / `preview` / `compile-only` / `hardware-pending` / `blocked` / `legacy-compatible` / `deprecated` / `removed`; blocker; hardware SKUs; blocked modules per product) | [`config/product-catalog.json`](../config/product-catalog.json). | [`tests/test_product_catalog.py`](../tests/test_product_catalog.py), [`scripts/validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py), [`tests/test_product_catalog_consistency.py`](../tests/test_product_catalog_consistency.py). |
| **Build matrix** (which config strings this repo actually builds and publishes as WebFlash-compatible `.bin` assets) | [`config/webflash-builds.json`](../config/webflash-builds.json). | [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py), [`tests/test_validate_webflash_builds.py`](../tests/test_validate_webflash_builds.py). |
| **Hardware catalog** (canonical board / module name, SKU, revision, `old_name`, `schematic_status`, `schematic_file`) | [`config/hardware-catalog.json`](../config/hardware-catalog.json) and [`docs/hardware-catalog.md`](hardware-catalog.md). | The hardware catalog is consumed by [`scripts/validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py) and classified per board in [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md). |

The cross-references between these four files are one-way:

- Every entry in `config/webflash-builds.json` must appear in
  `config/product-catalog.json` with a WebFlash-eligible status
  (`production` or `preview`). Enforced by
  `tests/test_product_catalog.py::test_every_webflash_build_appears_in_catalog_with_eligible_status`.
- No entry in `config/product-catalog.json` with `status: blocked` may
  appear in `config/webflash-builds.json`. Enforced by
  `tests/test_product_catalog.py::test_no_blocked_entry_in_webflash_build_matrix`.
- Every `config_string` in `config/webflash-builds.json` must parse against
  the grammar declared in `config/webflash-compatibility.json` (allowed
  mounting / power / module tokens; forbidden tokens; mutual-exclusion;
  fan-driver max-one-of). Enforced by
  [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py).
- Every SKU referenced by a production catalog entry's `hardware` map must
  exist in `config/hardware-catalog.json`. Enforced by
  [`scripts/validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py).

## Taxonomy does not imply shippability

**Listing a token in `config/webflash-compatibility.json` does not, by
itself, make that token shippable.** The four files above are intentionally
layered:

- A token can be in the **taxonomy** (`canonical_modules` /
  `canonical_power` / `canonical_mounting`) and still be **not
  shippable today** because:
  - no entry in `config/product-catalog.json` carries it with a
    WebFlash-eligible status, or
  - the catalog entry that carries it is `blocked` / `hardware-pending` /
    `compile-only` / `legacy-compatible` / `deprecated` / `removed`, or
  - the hardware catalog row for the underlying SKU is
    `cataloged_unverified` and the per-board audit classifies it as
    `cataloged-unverified` / `blocked`, or
  - (for mains-voltage modules) the qualified electrical-safety /
    compliance review tracked in
    [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
    has not been completed.
- A token in the taxonomy is **shippable today** only if there is a
  matching `production` (or `preview` for non-`stable` channels) entry in
  the product catalog **and** that entry appears in the WebFlash build
  matrix **and** every preceding gate in
  [`docs/product-onboarding.md`](product-onboarding.md) has been cleared.

This is why the current taxonomy intentionally lists tokens that are not
currently shippable (`FanTRIAC`, `LED`, `AirIQ`, `FanRelay`, `FanPWM`,
`FanDAC`, `PWR`, `USB`): they are reserved names so the grammar of future
config strings is stable, **not** a claim that they are ready to ship.

## Per-token decision table

Each row covers one token currently in
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
plus the legacy concept `Voice` which is **not** a WebFlash taxonomy
token but is mentioned in legacy product YAMLs. The "Hardware evidence
state" column is read from the per-board classification in
[`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md#decision-table)
as committed today, including HW-007's per-board doc commits and HW-008's
JSON `schematic_status` refresh (see the note at the top of this
document).

| Token / concept | In compatibility taxonomy? | In product catalog? | Hardware evidence state (per HW-004 / HW-006) | Release-One status | WebFlash-stable-eligible today? | Recommendation |
|---|---|---|---|---|---|---|
| `Ceiling` | Yes — only entry in `canonical_mounting`. | Yes — every catalog entry mounts on Ceiling (`modules.mount = "Ceiling"` on the Release-One row; legacy / Mini entries are off-spec for WebFlash anyway). | `S360-100` Sense360 Core is `documented`. | In Release-One. | Yes (mounting slot for the only production entry). | Keep. Do not reintroduce `Wall` as a WebFlash mounting token without an upstream WebFlash change first (the contract notes a legacy `Wall` mount that is not active). |
| `POE` | Yes — `canonical_power`. | Yes — Release-One `modules.power = "POE"` and `hardware.poe = "S360-410"`. | `S360-410` Sense360 PoE PSU is `partially-documented` (Core-side J2 inlet captured; module-side schematic pending). | In Release-One. | Yes (power slot for the only production entry). | Keep. The "schematic verification pending" caveat must remain visible in the catalog `notes` and in the Release-One docs; do not promote that caveat away in this audit. |
| `PWR` | Yes — `canonical_power`. | Not in any current catalog entry. Mains-input module; `S360-400` is the SKU. | `S360-400` Sense360 240v PSU is `cataloged-unverified`, `not-needed-for-release-one`. | Not in Release-One. | **No.** | Keep as a future-token. A future `PWR`-bearing config requires: `S360-400` schematic; standalone pin/connector reference doc; a new catalog entry; a build-matrix entry; **and** a qualified mains-voltage compliance review per [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md) before preview or stable promotion. |
| `USB` | Yes — `canonical_power`. | Not in any current catalog entry (legacy `sense360-core-*-usb` YAMLs are `legacy-compatible`, off the WebFlash track). | USB-C input lives on Core; no separate SKU. No dedicated catalog row. | Not in Release-One. | **No.** | Keep as a future-token. A future `USB`-bearing config requires a new catalog entry (mapping a USB-input Ceiling product) and a build-matrix entry. Not gated by mains-voltage compliance, but still gated by hardware-evidence and onboarding-sequence gates in [`docs/product-onboarding.md`](product-onboarding.md). |
| `AirIQ` | Yes — `canonical_modules`. Mutually exclusive with `VentIQ` (`rules.airiq_and_ventiq_mutually_exclusive: true`). | Not in any current catalog entry. Legacy `sense360-core-*` YAMLs that include AirIQ-style sensors are `legacy-compatible`. | `S360-210` Sense360 AirIQ is `documented`, `not-needed-for-release-one`. *Per-board doc at [`hardware/s360-210-r4-airiq.md`](hardware/s360-210-r4-airiq.md); PDF committed under HW-007 at [`hardware/schematics/S360-210-R4.pdf`](hardware/schematics/S360-210-R4.pdf); JSON `schematic_status: verified` with `schematic_file: docs/hardware/schematics/S360-210-R4.pdf` under HW-008.* | Not in Release-One. | **No.** | Keep. A future `AirIQ`-bearing config still requires a new catalog entry (acknowledging AirIQ ↔ VentIQ mutual exclusion) and a build-matrix entry. HW-007 + HW-008 only commit hardware-evidence; they do **not** make AirIQ WebFlash-shippable. `FanDAC` is additionally forbidden alongside `AirIQ` by `rules.fandac_conflicts_with_airiq` — that rule already enforces the bus conflict for any future `AirIQ`-bearing build entry. |
| `VentIQ` | Yes — `canonical_modules`. | Yes — Release-One `modules.air_quality = "VentIQ"` and `hardware.ventiq = "S360-211"`. | `S360-211` Sense360 VentIQ is `documented`. *Per-board doc at [`hardware/s360-211-r4-ventiq.md`](hardware/s360-211-r4-ventiq.md); PDF committed under HW-007 at [`hardware/schematics/S360-211-R4.pdf`](hardware/schematics/S360-211-R4.pdf); JSON `schematic_status: verified` with `schematic_file: docs/hardware/schematics/S360-211-R4.pdf` under HW-008. The "schematic verification pending" caveat in [`release-one-hardware-audit.md`](release-one-hardware-audit.md) and in this audit has been retired by HW-008.* | In Release-One. | Yes (air-quality slot for the only production entry). | Keep. Release-One air-quality slot continues to be VentIQ. |
| `RoomIQ` | Yes — `canonical_modules`. | Yes — Release-One `modules.room_sense = "RoomIQ"` and `hardware.roomiq = "S360-200"`. | `S360-200` Sense360 RoomIQ is `documented`. | In Release-One. | Yes (room-sense slot for the only production entry). | Keep. Carries the Core J10 vs RoomIQ J6 pin-order open question already tracked in the hardware docs; no impact on the taxonomy. |
| `FanRelay` | Yes — `canonical_modules`. Subject to fan-driver max-one-of rule (`FAN_DRIVER_TOKENS` in [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py)). | Not in any current catalog entry. | `S360-310` Sense360 Relay is `partially-documented` (Core-side J4 nets captured; module-side schematic pending), `not-needed-for-release-one`. | Not in Release-One. | **No.** | Keep. A future `FanRelay`-bearing config requires `S360-310` schematic + pin/connector doc, catalog entry, and build-matrix entry. |
| `FanPWM` | Yes — `canonical_modules`. Subject to fan-driver max-one-of rule. | Not in any current catalog entry. Legacy `sense360-fan-pwm.yaml` is `legacy-compatible`. | `S360-311` Sense360 PWM is `partially-documented` (Core-side J6 nets captured with **verify** flag on pin order; module-side schematic pending), `not-needed-for-release-one`. | Not in Release-One. | **No.** | Keep. A future `FanPWM`-bearing config requires `S360-311` schematic + pin/connector doc (resolve the J6 1-to-13 pin-order **verify** flag), catalog entry, and build-matrix entry. |
| `FanDAC` | Yes — `canonical_modules`. Subject to fan-driver max-one-of rule. Additionally forbidden alongside `AirIQ` by `rules.fandac_conflicts_with_airiq`. | Not in any current catalog entry. | `S360-312` Sense360 DAC is `partially-documented` (Core-side J7 nets captured; module-side schematic pending), `not-needed-for-release-one`. | Not in Release-One. | **No.** | Keep. A future `FanDAC`-bearing config requires `S360-312` schematic + pin/connector doc, a catalog entry, and a build-matrix entry; the existing `fandac_conflicts_with_airiq` rule continues to forbid pairing it with `AirIQ`. |
| `FanTRIAC` | Yes — `canonical_modules`. Subject to fan-driver max-one-of rule. | Yes — `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` is in the catalog with `status: blocked`, `blocker: HW-005`. **Not** in `config/webflash-builds.json`. | `S360-320` Sense360 TRIAC is `blocked` (HW-005), `not-needed-for-release-one`. Mains-output module; additionally subject to the mains-voltage compliance tracker in [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md). | Excluded from Release-One. Release-One's `blocked_modules` list explicitly includes `FanTRIAC`. | **No.** | **Keep blocked.** Token stays in the taxonomy as a reserved future name. Unblocking requires the HW-005 missing-evidence checklist in [`docs/release-one-hardware-audit.md#fantriac-mapping-resolution`](release-one-hardware-audit.md#fantriac-mapping-resolution) to be fully satisfied **and** a qualified mains-voltage compliance review per COMPLIANCE-001. Neither happens in this audit. |
| `LED` | Yes — `canonical_modules`. | Not as its own catalog entry; appears in Release-One's `blocked_modules: ["FanTRIAC", "LED"]` because the Release-One `config_string` carries no `LED` token. | `S360-300` Sense360 LED is `documented`, `not-needed-for-release-one`. The `GPIO14` package vs `IO38` schematic discrepancy at the package level has been **resolved by HW-010** — [`packages/hardware/led_ring_ceiling.yaml`](../packages/hardware/led_ring_ceiling.yaml) now binds `led_data_pin: GPIO38`. *Per-board doc at [`hardware/s360-300-r4-led.md`](hardware/s360-300-r4-led.md); PDF committed under HW-007 at [`hardware/schematics/S360-300-R4.pdf`](hardware/schematics/S360-300-R4.pdf); JSON `schematic_status: verified` with `schematic_file: docs/hardware/schematics/S360-300-R4.pdf` under HW-008. HW-007 committed LED-board schematic evidence, HW-008 updated JSON status, and HW-010 landed the matching package-level pin edit (`GPIO14` → `GPIO38`). The wall LED package and the legacy S3 Core package remain unresolved at the package level — neither has Core-side schematic evidence proving the same `LED_DATA` path.* | Excluded from Release-One. The Release-One YAML omits LED package includes on purpose. | **No.** | **Keep excluded from Release-One.** Token stays in the taxonomy as a reserved future name. A future LED-bearing config (e.g. `Ceiling-POE-VentIQ-RoomIQ-LED`) is a separate product: it requires its own catalog entry, build-matrix entry, and release-notes draft. The package-level `LED_DATA` pin reconciliation is now done (HW-010); the remaining gates are product-level, not package-level. **HW-010 does not add `LED` to the Release-One config string. Sense360 LED remains excluded from Release-One.** The product-level decision about whether and when an LED-bearing preview catalog entry should be created is recorded in [`product-led-preview-decision.md`](product-led-preview-decision.md) (PRODUCT-005), which keeps LED documented-only for now and defers every catalog / wrapper / build-matrix change to the scoped follow-up sequence PRODUCT-006 / PRODUCT-007 / PRODUCT-008 / PRODUCT-009. |
| `Voice` (legacy concept) | **No.** Not in `canonical_mounting`, `canonical_power`, or `canonical_modules`. Not in `forbidden_tokens` either. | Several `sense360-core-v-*` YAMLs are catalogued as `legacy-compatible` (pre-WebFlash Core Voice variants requiring a LED+MIC ring). | No `Voice` SKU in `config/hardware-catalog.json`. `S360-LED-V-*` LED+MIC ring SKUs are referenced in legacy docs only. | Not in Release-One. Not a WebFlash token. | **No.** | Keep out of the taxonomy. A future Voice-bearing config string would require an upstream WebFlash change (taxonomy update upstream first, then mirror locally), a new SKU in `config/hardware-catalog.json`, a new catalog entry, and a new build-matrix entry. This audit does **not** add a `Voice` token to the local snapshot. |

### Forbidden / deprecated tokens

The taxonomy's `forbidden_tokens` list and the prose contract's §3
forbidden-token table also matter for this audit; they prevent legacy
names from leaking back into WebFlash config strings.

| Forbidden token | Status in local snapshot | Status in `docs/webflash-contract.md` §3 | Notes |
|---|---|---|---|
| `Bathroom` | In `forbidden_tokens`. | Listed (alias → `VentIQ`). | Correct. |
| `Comfort` | In `forbidden_tokens`. | Listed (alias → `RoomIQ`). | Correct. |
| `Presence` | In `forbidden_tokens`. | Listed (alias → `RoomIQ`). | Correct. |
| `Fan` (generic, no variant suffix) | In `forbidden_tokens`; rule `generic_fan_token_forbidden: true`. | Listed (alias → `FanRelay` / `FanPWM` / `FanDAC` / `FanTRIAC`). | Correct. |
| `FanAnalog` | In `forbidden_tokens`. | Listed (alias → `FanDAC`). | Correct. |
| `BathroomAirIQ`, `BathroomAirIQBase`, `BathroomAirIQPro`, `Base`, `Pro` | **Not** in `forbidden_tokens`. | Listed in §3's alias table (rejected upstream by WebFlash's `scripts/validate-naming-policy.js`). | **Non-blocking documentation observation.** The local snapshot intentionally tracks a smaller subset; upstream WebFlash actively rejects the longer list. Aligning the local snapshot is recommended as a future PR (see [Recommended follow-up PRs](#recommended-follow-up-prs)); this audit does not change the local snapshot. |
| `AirIQBase`, `AirIQPro`, `AirIQProv` | **Not** in `forbidden_tokens`. | Listed in §3's alias table. | Same observation as above. |

## Current Release-One mapping

| Slot | Token | SKU | Catalog field | Notes |
|---|---|---|---|---|
| Mounting | `Ceiling` | `S360-100` (Core) | `modules.mount = "Ceiling"`, `hardware.core = "S360-100"` | Core is `documented`. |
| Power | `POE` | `S360-410` (PoE PSU) | `modules.power = "POE"`, `hardware.poe = "S360-410"` | PoE PSU is `partially-documented` — schematic verification pending. |
| Air Quality | `VentIQ` | `S360-211` (VentIQ) | `modules.air_quality = "VentIQ"`, `hardware.ventiq = "S360-211"` | VentIQ is `partially-documented` — schematic verification pending. |
| Room Sense | `RoomIQ` | `S360-200` (RoomIQ) | `modules.room_sense = "RoomIQ"`, `hardware.roomiq = "S360-200"` | RoomIQ is `documented`. |
| Fan (slot empty) | (none) | (none) | `modules.fan = "none"` | Intentionally empty while HW-005 keeps FanTRIAC blocked and no other fan driver is in the Release-One scope. |
| LED (slot empty) | (none) | (none) | `modules.led = "none"`; LED is in `blocked_modules`. | LED token is not part of the Release-One config string. |

The Release-One config string is **`Ceiling-POE-VentIQ-RoomIQ`** and the
artifact is **`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`**.
Both are pinned in
[`docs/release-one.md`](release-one.md) and
[`docs/webflash-contract.md`](webflash-contract.md). This audit does not
change either.

## Blocked / excluded modules

Two modules are in the WebFlash taxonomy but **must not** appear in
production Release-One today. Both exclusions are upheld by this audit.

- **`FanTRIAC` — blocked under HW-005.** `S360-320` schematic is not
  committed, `TRI_GPIO1` / `TRI_GPIO2` are not traced to direct
  interrupt-capable ESP32 GPIOs (they appear to route via the SX1509
  expander), and ESPHome's `ac_dimmer` driver cannot run across the
  SX1509. Authoritative resolution and missing-evidence checklist:
  [`docs/release-one-hardware-audit.md#fantriac-mapping-resolution`](release-one-hardware-audit.md#fantriac-mapping-resolution).
  The FanTRIAC product YAML
  ([`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml))
  and WebFlash wrapper
  ([`products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml))
  are retained as blocked / reference files; the FanTRIAC catalog entry
  carries `status: blocked`, `blocker: HW-005`,
  `webflash_build_matrix: false`, and is **not** in
  [`config/webflash-builds.json`](../config/webflash-builds.json).
  FanTRIAC is also a mains-output module: any future unblock is
  additionally subject to the mains-voltage compliance review tracked
  in
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md).
- **`LED` — excluded from Release-One by config-string policy.** The
  Release-One config string `Ceiling-POE-VentIQ-RoomIQ` does not carry a
  `LED` token, so the binary built from the Release-One YAML must not
  bundle LED firmware. The Release-One YAML omits LED package includes
  on purpose. Authoritative explanation:
  [`docs/release-one-hardware-audit.md` Sense360 LED row and "Sense360 LED policy" section](release-one-hardware-audit.md).
  LED packages remain in the repo for legacy / non-Release-One products
  and for a future LED-bearing config string such as
  `Ceiling-POE-VentIQ-RoomIQ-LED`, which would be a **separate**
  product with its own catalog entry, build-matrix entry, and
  release-notes draft. Schematic evidence (`S360-300`) is committed
  (HW-007 / HW-008) and the package-level `GPIO14` (package) vs
  `IO38` (schematic) `LED_DATA` reconciliation is done (HW-010);
  the remaining gates for a future LED variant are product-level,
  not package-level.

Both exclusions are also enumerated in Release-One's `blocked_modules:
["FanTRIAC", "LED"]` field in
[`config/product-catalog.json`](../config/product-catalog.json), and
both are emitted as Known-Issues exclusions (never as Features) by
[`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py).

## Future-token policy

A token in the WebFlash taxonomy that is **not** currently in any
build-matrix entry is a **reserved name**, not a commitment to ship.
Moving a reserved token from "in the taxonomy" to "in the build matrix"
requires the full ordered onboarding sequence in
[`docs/product-onboarding.md`](product-onboarding.md):

1. Hardware evidence first (per-board audit row must be at least
   `partially-documented`; `cataloged-unverified` / `blocked` rows
   disqualify the token).
2. Mains-voltage compliance review if the token involves `S360-400`
   (mains input) or `S360-320` (mains output) — qualified review
   tracked in [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md).
3. Product YAML + (where applicable) WebFlash wrapper.
4. Product catalog entry with the correct lifecycle status.
5. `scripts/validate_product_catalog_consistency.py` passes.
6. Build-matrix entry added to `config/webflash-builds.json`; the rules
   in [`docs/webflash-contract.md`](webflash-contract.md) and
   [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py)
   apply.
7. Release-notes draft via
   [`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py)
   (the generator refuses blocked / legacy-compatible / deprecated /
   removed / unknown entries and refuses preview entries on `stable`).
8. Build/release proof recorded under
   [`docs/release-one.md` → Proof of build (recorded)](release-one.md#proof-of-build-recorded)
   pattern.
9. WebFlash handoff per
   [`docs/webflash-release-handoff.md`](webflash-release-handoff.md).

Reserved tokens are not "pre-approved" by this audit. Each one's
recommendation row in the [decision table](#per-token-decision-table)
spells out exactly what is missing today.

## Test coverage summary

### What is already locked in place

These tests exist and pass on the current branch; they prevent the
listed drift risks from sneaking in unnoticed.

| Drift risk | Test |
|---|---|
| Schema-version regression of the local taxonomy snapshot | `tests/test_webflash_compatibility.py::test_schema_version_is_one` |
| Snapshot file missing | `tests/test_webflash_compatibility.py::test_snapshot_file_exists` |
| Snapshot not JSON-parseable | `tests/test_webflash_compatibility.py::test_snapshot_parses_as_json` |
| `source` drift (no longer "WebFlash") | `tests/test_webflash_compatibility.py::test_source_is_webflash` |
| Loss of the only canonical mounting | `tests/test_webflash_compatibility.py::test_ceiling_is_allowed_mounting` |
| Loss of `POE` as a power token | `tests/test_webflash_compatibility.py::test_poe_is_allowed_power` |
| Silent drop of `FanTRIAC` from canonical_modules | `tests/test_webflash_compatibility.py::test_fantriac_is_allowed_module` |
| Silent allowance of the generic `Fan` token | `tests/test_webflash_compatibility.py::test_generic_fan_token_is_forbidden` |
| Silent allowance of `Bathroom` / `Comfort` / `Presence` aliases | `tests/test_webflash_compatibility.py::test_legacy_tokens_are_forbidden` |
| Loss of the Release-One required config string | `tests/test_webflash_compatibility.py::test_release_one_required_config_present` |
| Drift of the artifact-name pattern | `tests/test_webflash_compatibility.py::test_artifact_pattern_matches_contract` |
| Loss of the RoomIQ ↔ VentIQ pairing rule | `tests/test_webflash_compatibility.py::test_roomiq_can_pair_with_ventiq` |
| Loss of the AirIQ ↔ VentIQ mutex rule | `tests/test_webflash_compatibility.py::test_airiq_and_ventiq_are_mutually_exclusive` |
| Build-matrix entry that violates the grammar / fan-max-one-of / forbidden tokens / artifact name / channel | `tests/validate_webflash_builds.py` (full pipeline) |
| Blocked catalog entry leaking into the build matrix | `tests/test_product_catalog.py::test_no_blocked_entry_in_webflash_build_matrix` |
| Build-matrix entry without a catalog backing | `tests/test_product_catalog.py::test_every_webflash_build_appears_in_catalog_with_eligible_status` |
| Catalog ↔ builds ↔ compatibility ↔ hardware ↔ mapper drift | `scripts/validate_product_catalog_consistency.py` (and its `unittest` suite [`tests/test_product_catalog_consistency.py`](../tests/test_product_catalog_consistency.py)) |

### What this audit adds

To strengthen the future-token policy, this audit adds the following
drift-protection tests to
[`tests/test_webflash_compatibility.py`](../tests/test_webflash_compatibility.py).
Each new test passes against the current
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
**without** any change to that file; the tests only **lock current
invariants** so a later PR can't drop them silently.

| Drift risk locked | New test |
|---|---|
| `LED` silently dropped from `canonical_modules` (would weaken the future-token policy) | `test_led_is_canonical_module` |
| Any of `FanRelay` / `FanPWM` / `FanDAC` / `FanTRIAC` silently dropped (would break the fan-driver max-one-of policy and Sense360 driver coverage) | `test_all_four_fan_driver_tokens_are_canonical_modules` |
| Silent reintroduction of `Wall` (legacy mount) or any other non-`Ceiling` mount into the WebFlash taxonomy | `test_canonical_mounting_is_ceiling_only` |
| Silent drift of `canonical_power` away from exactly `["USB", "POE", "PWR"]` | `test_canonical_power_is_usb_poe_pwr_only` |
| `production_channel` drift away from `"stable"` | `test_production_channel_is_stable` |
| Silent removal of `FanAnalog` from `forbidden_tokens` (loss of an alias guard) | `test_fan_analog_is_forbidden` |

Each new test is also wired into the `_run_all()` script-mode runner so
`python3 tests/test_webflash_compatibility.py` keeps reporting the
PASS / FAIL line for each.

## Recommended follow-up PRs

The items below are **not** part of COMPAT-001. They are each a separate
scoped PR with its own gate, its own validation, and its own approval.
COMPAT-001 only records that they would each be a sensible next step.

1. **HW-007 — ingest the new schematic uploads.** *Landed.* HW-007
   committed `S360-100`, `S360-200`, `S360-210`, `S360-211`, and
   `S360-300` schematic PDFs under
   [`docs/hardware/schematics/`](hardware/schematics/) and three new
   standalone reference docs (AirIQ / VentIQ / LED). HW-007 was
   documentation only and did not change
   [`config/hardware-catalog.json`](../config/hardware-catalog.json).
2. **HW-008 — refresh hardware-catalog machine-readable status.**
   *Landed.* HW-008 aligned
   [`config/hardware-catalog.json`](../config/hardware-catalog.json)
   with HW-007's committed evidence: `S360-100`, `S360-200`,
   `S360-210`, `S360-211`, and `S360-300` flipped to
   `schematic_status: verified` with `schematic_file` paths under
   `docs/hardware/schematics/`. The
   [decision table](hardware/remaining-board-documentation-audit.md#decision-table)
   rows for AirIQ / VentIQ / LED were reclassified from
   `cataloged-unverified` / `partially-documented` to `documented`.
   HW-008 changed hardware-evidence JSON and prose only; it did
   **not** ship any firmware, did **not** change FanTRIAC's HW-005
   blocked status, did **not** add `LED` to the Release-One config
   string, and did **not** clear the mains-voltage compliance gate
   for `S360-400` or `S360-320`.
3. **LED variant (`Ceiling-POE-VentIQ-RoomIQ-LED`).** Pre-requisites
   landed: HW-007 (PDF + per-board doc), HW-008 (JSON `verified` for
   `S360-300`), and HW-010 (package-level reconciliation of `GPIO14`
   (package) vs `IO38` (schematic) for `LED_DATA` — the ceiling LED
   package now binds `GPIO38`). The variant PR itself still has to
   add a new product YAML, a new WebFlash wrapper, a new catalog
   entry, a new build-matrix entry, and a release-notes draft. It
   does **not** modify Release-One; it is a sibling product. HW-010
   alone does **not** make LED WebFlash-shippable. The
   product-level decision and the scoped follow-up PR sequence
   (PRODUCT-006 — product YAML; PRODUCT-007 — `compile-only` catalog
   entry; PRODUCT-008 — WebFlash wrapper + `preview` promotion;
   PRODUCT-009 — build-matrix entry + release proof + LED-test
   re-scope + release-notes generator change) are recorded in
   [`product-led-preview-decision.md`](product-led-preview-decision.md)
   (PRODUCT-005). PRODUCT-005 itself is documentation-only: no
   catalog entry, no product YAML, no WebFlash wrapper, no
   build-matrix entry, no release-notes draft.
4. **FanTRIAC unblock (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`).**
   Pre-requisites: (a) the full HW-005 missing-evidence checklist in
   [`release-one-hardware-audit.md#missing-evidence-checklist`](release-one-hardware-audit.md#missing-evidence-checklist)
   is resolved, **and** (b) the qualified mains-voltage compliance
   review tracked in
   [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
   has completed. Neither pre-requisite is satisfied by HW-007 or
   HW-008. `S360-320` stays `cataloged_unverified` after HW-008.
5. **AirIQ / FanRelay / FanPWM / FanDAC preview entries.** Each is a
   separate PR with its own per-board hardware evidence, catalog entry,
   build-matrix entry, and release-notes draft. They are mutually
   constrained by the existing `airiq_and_ventiq_mutually_exclusive`
   and `fandac_conflicts_with_airiq` rules; no taxonomy change needed.
6. **Mains-input (`PWR`-bearing) preview entry.** Pre-requisite:
   `S360-400` schematic + qualified mains-voltage compliance review.
7. **Optional: align local `forbidden_tokens` with `docs/webflash-contract.md` §3.**
   The local snapshot's `forbidden_tokens` is a strict subset of the
   alias list in
   [`docs/webflash-contract.md` §3](webflash-contract.md). Adding
   `BathroomAirIQ`, `BathroomAirIQBase`, `BathroomAirIQPro`, `Base`,
   `Pro`, `AirIQBase`, `AirIQPro`, and `AirIQProv` to the local
   snapshot would let
   [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py)
   reject those aliases locally without having to fetch WebFlash.
   This is a **JSON change** and is therefore out of scope for
   COMPAT-001 (audit-only). It would be its own PR with the same
   "taxonomy change in the same commit as the validator" discipline
   the WebFlash contract requires.

None of the above is approved by COMPAT-001. Each is its own future
decision.

## Do-not-change list

This audit does **not** change any of the following. If you are reading
this audit looking for justification to change one of them, look
elsewhere — this audit explicitly does not provide that justification.

- The Release-One shipping configuration `Ceiling-POE-VentIQ-RoomIQ`.
- The Release-One artifact name
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`.
- The WebFlash build matrix
  [`config/webflash-builds.json`](../config/webflash-builds.json) — no
  entries added, removed, or renamed.
- The WebFlash compatibility snapshot
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  — no values changed; the snapshot's semantics are unchanged.
- The product source-of-truth catalog
  [`config/product-catalog.json`](../config/product-catalog.json) — no
  lifecycle statuses changed; no blocked-modules lists changed.
- The hardware catalog
  [`config/hardware-catalog.json`](../config/hardware-catalog.json) — at
  the time COMPAT-001 was authored, no SKUs, friendly names, revisions,
  or `schematic_status` values were changed by this audit. HW-008 has
  since updated `schematic_status` / `schematic_file` for the five SKUs
  with committed module-side schematic PDFs (`S360-100`, `S360-200`,
  `S360-210`, `S360-211`, `S360-300`); that JSON refresh is owned by
  HW-008, not by COMPAT-001, and does not change any decision in this
  audit.
- Any product YAML under `products/` (including legacy / Mini / Voice
  legacy variants and the FanTRIAC blocked / reference YAML).
- Any WebFlash wrapper under `products/webflash/`.
- Any package under `packages/` (hardware, expansions, features, base).
- Any workflow under `.github/workflows/`.
- Any script under `scripts/`.
- Any component under `components/`.
- Any include under `include/`.
- The FanTRIAC HW-005 blocked status.
- The Sense360 LED Release-One exclusion status.
- The artifact-name grammar
  `Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin`.
- The allowed channels (`stable`, `beta`, `preview`, `dev`, `rescue`)
  or the production channel (`stable`).
- The fan-driver max-one-of rule, the AirIQ ↔ VentIQ mutex rule, the
  FanDAC ↔ AirIQ conflict rule, or the RoomIQ pairing rules.
- The forbidden-token list in
  `config/webflash-compatibility.json` (the optional alignment with
  `docs/webflash-contract.md` §3 is **deferred** to a separate PR per
  [Recommended follow-up PRs](#recommended-follow-up-prs)).
- Any test outside the six drift-protection tests added to
  [`tests/test_webflash_compatibility.py`](../tests/test_webflash_compatibility.py).

## See also

- [`docs/webflash-contract.md`](webflash-contract.md) — canonical
  WebFlash artifact / grammar / token contract.
- [`docs/release-one.md`](release-one.md) — Release-One configuration
  with full slot / file / binary mapping.
- [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)
  — Release-One firmware-vs-schematic audit, FanTRIAC HW-005
  resolution, and Sense360 LED policy.
- [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md)
  — per-board documentation-state classification (HW-004 / HW-006).
- [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
  — mains-voltage UK / EU compliance-assessment tracker
  (COMPLIANCE-001).
- [`docs/product-onboarding.md`](product-onboarding.md) — PRODUCT-004
  ordered safe sequence for adding a new product / config.
- [`docs/cleanup-audit.md`](cleanup-audit.md) — classification of
  stale / current / blocked-reference / legacy-compatible repo content.
- [`docs/product-led-preview-decision.md`](product-led-preview-decision.md)
  — PRODUCT-005 decision doc for the LED preview product path; the
  per-token `LED` recommendation row above defers every product-level
  next step to that document and the scoped PRODUCT-006 / PRODUCT-007 /
  PRODUCT-008 / PRODUCT-009 follow-up sequence.

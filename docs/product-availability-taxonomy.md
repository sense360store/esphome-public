# Product Availability Taxonomy (PRODUCT-AVAIL-001)

## Purpose and scope

This document is the canonical, cross-cutting **product availability
taxonomy** for this repository. It threads together the existing
hardware-evidence vocabulary (`docs/hardware/hardware-artifact-policy.md`,
`docs/hardware/remaining-board-documentation-audit.md`,
`docs/hardware/firmware-package-mapping-audit.md`,
`config/hardware-catalog.json`) with the product-lifecycle vocabulary
(`config/product-catalog.json`, `docs/product-onboarding.md`,
`docs/product-deprecation-removal-policy.md`,
`docs/preview-to-stable-promotion-gates.md`) and the WebFlash
availability vocabulary (`config/webflash-builds.json`,
`config/webflash-compatibility.json`,
`docs/webflash-contract.md`) into one named ladder of availability
states.

It exists so that downstream PRs — board readiness matrices, wizard
gating, stale-data cleanup, missing-package or missing-product work —
have a single vocabulary to refer to when describing "is this module
or product actually buildable / shippable / installable today?", and
so the taxonomy is consistent across docs, future validators, and
WebFlash-side surfaces.

This document is **documentation only**. PRODUCT-AVAIL-001 — this
PR — does not:

- add, remove, or modify any product YAML, WebFlash wrapper, or
  package YAML,
- add, remove, or modify any entry in
  [`config/product-catalog.json`](../config/product-catalog.json),
  [`config/hardware-catalog.json`](../config/hardware-catalog.json),
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  or [`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
- add any new JSON field or any new status value to any of those
  catalogs,
- change any value in
  [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  (`schematic_status` and `schematic_file` per row are left exactly
  as committed),
- change any value in
  [`config/product-catalog.json`](../config/product-catalog.json)
  (`lifecycle_statuses` and every per-product `status` are left
  exactly as committed),
- modify any workflow under `.github/workflows/`, any script under
  [`scripts/`](../scripts/), any test under [`tests/`](../tests/),
  any component under `components/`, or any include under
  `include/`,
- generate, regenerate, sign, import, deploy, or otherwise produce
  firmware,
- change the Release-One product `Ceiling-POE-VentIQ-RoomIQ`, its
  artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`,
  or its tag `v1.0.0`,
- change the LED preview entry `Ceiling-POE-VentIQ-RoomIQ-LED`
  (stays `status: preview`, `channel: preview`),
- unblock FanTRIAC (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays
  `status: blocked`, `blocker: HW-005`,
  `webflash_build_matrix: false`),
- add, remove, or modify any entry in WebFlash-side
  `REQUIRED_CONFIGS`, `scripts/data/kits.json`,
  `firmware/sources.json`, or `manifest.json` — those are
  WebFlash-owned.

The intended audience is maintainers preparing follow-up work
(HW-GAP-001 board readiness matrix; WF-WIZARD-AVAIL-001 wizard
gating for unavailable modules / configs; WF-STALE-001 /
PRODUCT-STALE-001 stale-data cleanup; PACKAGE-GAP-001 /
PRODUCT-GAP-001 missing-package / missing-product work; future
PRODUCT-AVAIL-002 machine-readable availability fields), reviewers
asked to sign off on availability claims, and WebFlash-side
operators wiring "this module exists in docs but is not buildable"
states into customer-facing UI.

If this document and any source-of-truth document drift, **the
source-of-truth document wins** and this document must be updated.
The sources of truth are listed in [See also](#see-also).

## Core rule

> **Hardware evidence does not equal firmware support, product
> support, or WebFlash availability.**

A board may have a committed schematic PDF, a `verified`
`schematic_status` in
[`config/hardware-catalog.json`](../config/hardware-catalog.json),
a standalone pin / connector reference doc under
[`docs/hardware/`](hardware/), and a per-board curated artifact
index under [`docs/hardware/artifacts/`](hardware/artifacts/), and
**still not be installable** through WebFlash. A product may have a
canonical YAML under [`products/`](../products/), a WebFlash
wrapper under [`products/webflash/`](../products/webflash/), and a
build-matrix entry in
[`config/webflash-builds.json`](../config/webflash-builds.json),
and **still not be on the customer-facing flasher** until WebFlash
imports the signed artifact and the deployed
`manifest.json` / `firmware-N.json` includes it.

This rule is the load-bearing premise of every state below. Any PR
that conflates two adjacent rungs of the [Concept
ladder](#concept-ladder) — for example, treating "schematic
verified" as if it implied "WebFlash-ready" — is breaking this
rule and must be rejected on first read.

## Concept ladder

Availability is an ordered ladder. A rung is reached only after
every lower rung is reached. The ladder is policy-only; it is not a
JSON enum and PRODUCT-AVAIL-001 does not add it as one.

1. **hardware-listed** — the SKU exists as a row in
   [`config/hardware-catalog.json`](../config/hardware-catalog.json)
   with `friendly_name`, `sku`, `rev`, and `old_name`. Nothing below
   the SKU level is yet evidenced.
2. **artifact-indexed** — a per-board curated artifact index doc
   exists under [`docs/hardware/artifacts/`](hardware/artifacts/)
   per HW-ASSETS-001. The index inventories what manufacturing /
   source evidence is present, what is retained-but-not-committed,
   and what is excluded.
3. **schematic-verified** — the module-side schematic PDF is
   committed under
   [`docs/hardware/schematics/`](hardware/schematics/), the JSON
   `schematic_status` is `verified`, the JSON `schematic_file`
   points at the PDF, and a standalone pin / connector reference
   doc exists under [`docs/hardware/`](hardware/).
4. **pin-map-ready** — the module's GPIO / connector net map is
   captured and reconciled against the schematic (the audit row in
   [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md)
   is `documented` or `partially-documented` with an explicitly
   retained caveat). All pin-level firmware questions can be
   answered against the doc.
5. **package-yaml-ready** — a package YAML under
   [`packages/`](../packages/) consumes the module and is
   reconciled against the verified schematic per
   [`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
   (`confirmed-ok`, or `confirmed-ok` with a retained legacy-naming
   caveat). Logical-only packages (no GPIO binding) are
   package-yaml-ready when the abstraction is consistent with the
   schematic at the bus / connector level.
6. **product-yaml-ready** — a canonical product YAML under
   [`products/`](../products/) composes the module's package(s)
   into a buildable configuration, passes
   [`tests/validate_configs.py`](../tests/validate_configs.py),
   passes [`tests/test_product_substitutions.py`](../tests/test_product_substitutions.py),
   and (if WebFlash-targeted) has a wrapper under
   [`products/webflash/`](../products/webflash/) whose basename
   matches the lower-cased `config_string`. A catalog entry in
   [`config/product-catalog.json`](../config/product-catalog.json)
   carries a lifecycle status that maps the readiness state
   (`compile-only` / `hardware-pending` / `preview` /
   `production` / `blocked` / `legacy-compatible` /
   `deprecated` / `removed`).
7. **build-matrix-ready** — the catalog entry is also in
   [`config/webflash-builds.json`](../config/webflash-builds.json)
   with matching `config_string`, `product_yaml`, `artifact_name`,
   `channel`, `version`, `chip_family`, `hardware_requirements`,
   and `features`. The entry passes
   [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py)
   and
   [`tests/test_webflash_compatibility.py`](../tests/test_webflash_compatibility.py).
   `blocked` / `legacy-compatible` / `deprecated` / `removed`
   entries never reach this rung.
8. **release-artifact-ready** — a GitHub Release `.bin` matching
   the declared `artifact_name` has been built by
   [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml),
   attached to the release, validated by `Attach to Release`'s
   release-body and release-asset gates, and recorded in
   [`docs/webflash-release-proof.md`](webflash-release-proof.md).
9. **webflash-imported** — WebFlash has run
   `scripts/sync-from-releases.py` against the release, produced
   the sidecar `*.meta.json`, generated `manifest.json` /
   `firmware-N.json` via `scripts/gen-manifests.py`, signed the
   firmware, and entered the build in `firmware/sources.json`. (The
   import is owned by the
   [`sense360store/WebFlash`](https://github.com/sense360store/WebFlash)
   repo, not by this repo.)
10. **webflash-live-preview** — the build is listed on
    [mysense360.com](https://mysense360.com) on a non-`stable`
    channel. The deployed `manifest.json` / `firmware-N.json`
    contains the build. Live preview deploy passes WebFlash-side
    `__tests__/github-pages-surface.test.js`.
11. **webflash-live-stable** — the build is listed at
    [mysense360.com](https://mysense360.com) on `channel: stable`.
    The catalog entry is `status: production`, the build-matrix
    entry is on `channel: stable`, and every row in
    [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
    is `done` or has a recorded, accepted waiver. Operator flash
    proof (WebFlash-side `WF-HW-TEST-001`) is recorded and hardware
    bench verification is closed.
12. **production-required** — the WebFlash-side `REQUIRED_CONFIGS`
    list contains the build's `config_string`. Absence from the
    deployed manifest fails a WebFlash deployment gate. **Not
    automatic.** A stable build does not enter `REQUIRED_CONFIGS`
    by side effect; see
    [`docs/preview-to-stable-promotion-gates.md` REQUIRED_CONFIGS policy](preview-to-stable-promotion-gates.md#required_configs-policy).
13. **kit-exposed** — the WebFlash-side `scripts/data/kits.json`
    includes a recommended SKU bundle that references the build.
    **Not automatic.** A stable build does not become a kit by side
    effect; see
    [`docs/preview-to-stable-promotion-gates.md` Kit policy](preview-to-stable-promotion-gates.md#kit-policy).

The ladder is one-way for any given board / product revision: a rung
can be lost only by deprecation / removal per
[`docs/product-deprecation-removal-policy.md`](product-deprecation-removal-policy.md),
or by a blocker that intentionally holds a module / product back
(HW-005 FanTRIAC; COMPLIANCE-001 mains; an outstanding bench
question). Skipping a rung is forbidden.

## Availability states

The ladder rungs in [Concept ladder](#concept-ladder) describe
**positions**. The states below are the **labels** PRs and docs use
to describe where a module or product currently sits, including the
"-pending" and exception forms. The Source column records where the
label comes from. `policy-only` means the label is defined by this
document or one of the cross-linked policy docs; it is **not** an
enum value in any JSON today and PRODUCT-AVAIL-001 does not make it
one.

### Hardware-side states

| State | Source | Meaning |
|---|---|---|
| `hardware-listed` | policy-only | SKU row exists in [`config/hardware-catalog.json`](../config/hardware-catalog.json). Nothing below SKU level is yet evidenced. |
| `artifact-indexed` | policy-only (HW-ASSETS-001) | A per-board artifact index doc exists under [`docs/hardware/artifacts/`](hardware/artifacts/). HW-ASSETS-002 has landed the first such index for `S360-100-R4`. |
| `schematic-verified` | `schematic_status: verified` in [`config/hardware-catalog.json`](../config/hardware-catalog.json) | Module-side schematic PDF committed; standalone reference doc exists; JSON `schematic_status` is `verified` and `schematic_file` points at the PDF. |
| `cataloged-unverified` (hyphenated form) | audit label in [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md) | Catalog row exists; no Core-side connector capture and no module-side schematic. Mirrors but is distinct from the JSON form `cataloged_unverified` (underscore). |
| `partially-documented` | audit label in [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md) | Core-side connector documented; module-side schematic still pending. Caveat must be visible in any consumer's notes. |
| `documented` | audit label in [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md) | Schematic-backed standalone reference doc committed; JSON is `verified`. Pin-level firmware questions can be checked against the doc. |
| `pin-map-pending` | policy-only | Hardware-listed but no pin / connector reference doc captures the module. Equivalent to `cataloged-unverified` for a SKU that has not gained any documentation. |
| `pin-map-ready` | policy-only | Pin / connector reference doc covers the module and reconciles against the schematic. Equivalent to `documented` or `partially-documented` (with the latter's caveat retained). |
| `package-yaml-pending` | policy-only | No package YAML in [`packages/`](../packages/) consumes the module yet, or an existing package binds GPIOs not yet reconciled with the schematic. |
| `package-yaml-ready` | mirrors HW-009 `confirmed-ok` | Package YAML exists and is `confirmed-ok` against the verified schematic (or `confirmed-ok` with a retained legacy-naming / abstract-bus caveat). |
| `product-yaml-pending` | policy-only | No product YAML in [`products/`](../products/) consumes the package(s) yet. |
| `product-yaml-ready` | policy-only | Product YAML exists, passes [`tests/validate_configs.py`](../tests/validate_configs.py), and has a catalog entry that matches its readiness state. |

### Product-lifecycle states (existing `config/product-catalog.json` enum)

| State | Source | Meaning |
|---|---|---|
| `production` | [`config/product-catalog.json` `lifecycle_statuses`](../config/product-catalog.json) | WebFlash-shippable on `stable`. Build matrix on `channel: stable`. Has `artifact_name`, `webflash_wrapper`, `version`, `hardware`, `modules`, `hardware_status`. Today only `Ceiling-POE-VentIQ-RoomIQ` (Release-One). |
| `preview` | [`config/product-catalog.json` `lifecycle_statuses`](../config/product-catalog.json) | WebFlash-eligible on a non-`stable` channel (typically `preview`). Must not be a Release-One required config. Today only `Ceiling-POE-VentIQ-RoomIQ-LED`. |
| `compile-only` | [`config/product-catalog.json` `lifecycle_statuses`](../config/product-catalog.json) | YAML exists and compiles in CI. Not promoted to WebFlash. `webflash_build_matrix: false`. Used during early bring-up. |
| `hardware-pending` | [`config/product-catalog.json` `lifecycle_statuses`](../config/product-catalog.json) | YAML / config exists but required hardware evidence is incomplete. Not WebFlash import / build eligible. `webflash_build_matrix: false`. Distinct from `blocked`: evidence is missing, not held back by a specific named blocker. |
| `blocked` | [`config/product-catalog.json` `lifecycle_statuses`](../config/product-catalog.json) | Held back by a named blocker (e.g. HW-005). Must carry `blocker` and `reason`. `webflash_build_matrix: false`. Today only `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`. |
| `legacy-compatible` | [`config/product-catalog.json` `lifecycle_statuses`](../config/product-catalog.json) | Pre-WebFlash product YAML retained for manual / custom / remote-package users. No `config_string`, no `artifact_name`, no `webflash_wrapper`. Never WebFlash-shippable. |
| `deprecated` | [`config/product-catalog.json` `lifecycle_statuses`](../config/product-catalog.json) | Previously WebFlash-shippable; phasing out. See [`docs/product-deprecation-removal-policy.md`](product-deprecation-removal-policy.md). Not WebFlash import / build eligible by default. |
| `removed` | [`config/product-catalog.json` `lifecycle_statuses`](../config/product-catalog.json) | Tombstone row. `config_string` is reserved; underlying YAML / wrapper / build-matrix / manifest entries are absent. Not WebFlash-shippable. |

These eight values are the **only** values legal in
`config/product-catalog.json` today. PRODUCT-AVAIL-001 does not add
to this enum.

### WebFlash-availability states

| State | Source | Meaning |
|---|---|---|
| `firmware-build-pending` | policy-only | Product YAML / wrapper / catalog / build-matrix entries are missing or inconsistent. `Attach to Release` will refuse a build. |
| `release-artifact-ready` | policy-only | Build-matrix entry has a corresponding GitHub Release `.bin` matching `artifact_name`, plus the release proof in [`docs/webflash-release-proof.md`](webflash-release-proof.md). |
| `webflash-ready` | policy-only | The release artifact exists and the WebFlash repo has imported, signed, manifested, and deployed it. Customer-installable via [mysense360.com](https://mysense360.com). |
| `preview-available` | policy-only | `webflash-ready` on a non-`stable` channel. Listed on the flasher; deliberately marked preview / beta. |
| `stable-available` | policy-only | `webflash-ready` on `channel: stable`. Catalog entry is `production`. |
| `production-required` | policy-only (RELEASE-006 [REQUIRED_CONFIGS policy](preview-to-stable-promotion-gates.md#required_configs-policy)) | Stable build whose `config_string` is in WebFlash's `REQUIRED_CONFIGS`. Absence from deployed manifest fails a WebFlash gate. |
| `kit-exposed` | policy-only (RELEASE-006 [Kit policy](preview-to-stable-promotion-gates.md#kit-policy)) | WebFlash `scripts/data/kits.json` includes a kit referencing the build. |
| `webflash-imported` | policy-only | WebFlash has ingested the release `.bin` and produced the `*.meta.json` sidecar. May or may not be on a deployed manifest yet. |

### Exception states

These describe modules / products that exist in docs, wizard
taxonomy, or compatibility language but are intentionally not
buildable / not shippable today.

| State | Source | Meaning |
|---|---|---|
| `design-pending` | policy-only | Module is named in docs, wizard taxonomy, or compatibility language but lacks any of: committed schematic, pin map, package YAML, product YAML, build-matrix entry. Wizard must show "design pending — not buildable today" rather than letting the customer pick this combination. |
| `firmware-missing` | policy-only | Hardware exists and is evidenced, but no product YAML / WebFlash wrapper / build-matrix entry consumes the module yet. Wizard must not imply installability. |
| `blocked` (cross-axis) | mirrors product-catalog `blocked` and audit `blocked` | Held by a named blocker (HW-005 for FanTRIAC; COMPLIANCE-001 for mains-voltage boards). Cannot be promoted from any axis without resolving the blocker. |
| `legacy-compatible` (cross-axis) | mirrors product-catalog `legacy-compatible` | Pre-WebFlash artifact retained for manual users; intentionally not WebFlash-shippable. |
| `deprecated` (cross-axis) | mirrors product-catalog `deprecated` | Previously WebFlash-shippable, now phasing out. Customer wording, kit eligibility, REQUIRED_CONFIGS membership all governed by [`docs/product-deprecation-removal-policy.md`](product-deprecation-removal-policy.md). |
| `removed` (cross-axis) | mirrors product-catalog `removed` | Tombstoned. Wizard, kit, manifest, REQUIRED_CONFIGS must not reference it. |

`design-pending` and `firmware-missing` are the two **new** terms
this document introduces. They are policy-only labels. They do
**not** become JSON values in this PR.

## Evidence required by state

The table below maps every state above to the evidence that must
exist before that state can be claimed. PRs that move a module or
product into a state must cite the matching row(s).

| State | Evidence required | Where the evidence lives |
|---|---|---|
| `hardware-listed` | Row exists in JSON catalog. | [`config/hardware-catalog.json`](../config/hardware-catalog.json) |
| `artifact-indexed` | Per-board artifact index doc per HW-ASSETS-001 schema. | [`docs/hardware/artifacts/<SKU>-<REV>.md`](hardware/artifacts/) |
| `schematic-verified` | Committed PDF; standalone reference doc; JSON `schematic_status: verified`. | [`docs/hardware/schematics/`](hardware/schematics/), [`docs/hardware/<sku>-<rev>-<role>.md`](hardware/) |
| `pin-map-ready` / `documented` / `partially-documented` | Per-board pin / connector tables sourced from the schematic. | [`docs/hardware/<sku>-<rev>-<role>.md`](hardware/), [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md) |
| `package-yaml-ready` | Package YAML reconciled against the verified schematic; HW-009 classification `confirmed-ok` (with any retained caveat). | [`packages/`](../packages/), [`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md) |
| `product-yaml-ready` | Canonical product YAML; passes [`tests/validate_configs.py`](../tests/validate_configs.py); catalog entry with the right lifecycle status. | [`products/`](../products/), [`config/product-catalog.json`](../config/product-catalog.json) |
| `build-matrix-ready` | Build-matrix entry; passes [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py) and [`tests/test_webflash_compatibility.py`](../tests/test_webflash_compatibility.py). | [`config/webflash-builds.json`](../config/webflash-builds.json) |
| `release-artifact-ready` | Release `.bin` matching `artifact_name`; build/release proof row. | GitHub Release, [`docs/webflash-release-proof.md`](webflash-release-proof.md) |
| `webflash-imported` | WebFlash-side ingest of the `.bin`; sidecar `*.meta.json`; entry in `firmware/sources.json`; signed firmware. | WebFlash repo |
| `webflash-live-preview` / `preview-available` | All preview-floor rows 1–8 of [RELEASE-006](preview-to-stable-promotion-gates.md#gate-summary) `done`. | this repo + WebFlash repo |
| `webflash-live-stable` / `stable-available` | All RELEASE-006 rows 1–17 `done` or with accepted waivers; operator flash proof; hardware bench verification closed. | this repo + WebFlash repo |
| `production-required` | Explicit WebFlash decision recorded in `__tests__/manifest-required-configs.test.js`. | WebFlash repo |
| `kit-exposed` | Explicit WebFlash decision recorded in `scripts/data/kits.json`. | WebFlash repo |
| `design-pending` | (No positive evidence required.) Any module named in docs / taxonomy / wizard language that lacks `schematic-verified` and lacks `package-yaml-ready` and lacks `product-yaml-ready`. | [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md), [`docs/webflash-compatibility-taxonomy-audit.md`](webflash-compatibility-taxonomy-audit.md) |
| `firmware-missing` | (No positive evidence required.) Any board that is `schematic-verified` and has packages but lacks a product YAML / WebFlash wrapper / build-matrix entry that consumes it as the customer surface. | as above |
| `blocked` | Named blocker ID (e.g. HW-005) plus written reason. | [`config/product-catalog.json`](../config/product-catalog.json), [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md), [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md) |
| `legacy-compatible` | Catalog entry with `status: legacy-compatible` and the legacy `product_yaml`. | [`config/product-catalog.json`](../config/product-catalog.json) |
| `deprecated` | Required metadata per [PRODUCT-DEP-001](product-deprecation-removal-policy.md#required-metadata-for-deprecation). | [`config/product-catalog.json`](../config/product-catalog.json), [`docs/product-deprecation-removal-policy.md`](product-deprecation-removal-policy.md) |
| `removed` | Required metadata per [PRODUCT-DEP-001](product-deprecation-removal-policy.md#required-metadata-for-removal). | [`config/product-catalog.json`](../config/product-catalog.json) |

## Existing status mappings

The taxonomy above is **policy-only**. The repo already carries
several enum / classification vocabularies. PRODUCT-AVAIL-001 maps
them; it does **not** redefine, rename, or extend them.

### Product-catalog lifecycle statuses

[`config/product-catalog.json`](../config/product-catalog.json)
declares the following enum under `lifecycle_statuses`:

```text
production
preview
compile-only
hardware-pending
blocked
legacy-compatible
deprecated
removed
```

These are the exact eight values legal today, enforced by
[`tests/test_product_catalog.py`](../tests/test_product_catalog.py)
and
[`scripts/validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py).
PRODUCT-AVAIL-001 reuses them verbatim; it does not add a ninth
value.

### Hardware-catalog schematic statuses

[`config/hardware-catalog.json`](../config/hardware-catalog.json)
declares two values for `schematic_status` (underscore form):

```text
verified
cataloged_unverified
```

`verified` is set for `S360-100`, `S360-200`, `S360-210`, `S360-211`,
and `S360-300`; the remaining six rows (`S360-310`, `S360-311`,
`S360-312`, `S360-320`, `S360-400`, `S360-410`) are
`cataloged_unverified`.
[`tests/test_hardware_catalog.py`](../tests/test_hardware_catalog.py)
enforces this. PRODUCT-AVAIL-001 reuses these values verbatim; it
does not add a third value.

### Remaining-board documentation-audit labels (HW-004 / HW-006 / HW-008)

[`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md)
classifies every catalog row using the hyphenated form:

```text
documented
partially-documented
cataloged-unverified
blocked
not-needed-for-release-one      (cross-axis modifier)
unknown                         (unused today)
```

`not-needed-for-release-one` is the Release-One axis; it is applied
alongside one of the primary labels. The hyphenated forms coexist
with the JSON `cataloged_unverified` (underscore) form on purpose:
the audit labels are taxonomy names, the JSON value is a
machine-readable status. PRODUCT-AVAIL-001 reuses both.

### Firmware-package-mapping-audit labels (HW-009 / HW-010)

[`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
classifies each package-vs-schematic reconciliation using:

```text
confirmed-ok
needs-package-change
needs-doc-fix
needs-silkscreen/bench-verification
blocked
unknown
```

PRODUCT-AVAIL-001 maps `package-yaml-ready` onto `confirmed-ok`
(possibly with a retained caveat), and `package-yaml-pending` onto
the remaining labels except `blocked` (which is its own axis).

### HW-ASSETS-001 per-board artifact index field schema

[`docs/hardware/hardware-artifact-policy.md`](hardware/hardware-artifact-policy.md)
already declares the following fields on a per-board artifact
index — they are **policy-only doc fields**, not JSON values:

```text
pin_map_status
package_yaml_status
product_yaml_status
webflash_status
```

with allowed values that mirror the per-source taxonomies cited
above. PRODUCT-AVAIL-001 reuses those field names as the **future
candidate names** for any machine-readable schema (see [Future
validator and schema work](#future-validator-and-schema-work)). It
does not promote them to JSON in this PR.

### WebFlash channels and lifecycle metadata

[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
enumerates the WebFlash release channels (`stable`, `beta`,
`preview`, `dev`, `rescue`).
[`config/webflash-builds.json`](../config/webflash-builds.json)
carries `config_string`, `product_yaml`, `artifact_name`, `channel`,
`version`, `chip_family`, `hardware_requirements`, `features`.
PRODUCT-AVAIL-001 maps `preview-available` onto `channel: preview`
(or any non-`stable` channel) and `stable-available` onto
`channel: stable`; it does not add a new channel value.

## Hardware evidence vs product support

The distinction between **hardware-evidenced** and **product-
supported** is:

- A board is **hardware-evidenced** when its module-side schematic
  is committed and `verified` in JSON, its standalone pin /
  connector reference doc is committed, and the relevant audit
  rows are `documented` or `partially-documented`.
- A board is **product-supported** when at least one product YAML
  under [`products/`](../products/) composes it into a buildable
  configuration, the corresponding catalog entry carries a
  WebFlash-eligible lifecycle status (`compile-only` / `preview` /
  `production`), and the relevant package YAMLs are
  `package-yaml-ready`.

These are independent axes. A board can be hardware-evidenced
without being product-supported (Sense360 LED was `schematic-verified`
under HW-007 / HW-008 well before PRODUCT-006 / PRODUCT-008 /
PRODUCT-009 produced a product-supported preview entry; Sense360
AirIQ is hardware-evidenced today and remains intentionally not
product-supported because it is mutually exclusive with VentIQ in
the only Release-One config). A board can be product-supported with
its schematic only `partially-documented` (PoE PSU `S360-410` is
consumed by Release-One despite a module-side schematic still
pending — the caveat is preserved in the catalog `notes` and in
[`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)).

PRs must not collapse the two axes. Any PR that argues "the
schematic is verified, therefore add this board to a product YAML"
without going through the
[`docs/product-onboarding.md`](product-onboarding.md) gate must be
rejected.

## Product support vs WebFlash support

The distinction between **product-supported** and **WebFlash-
supported** is:

- A product is **product-supported** when its YAML compiles, its
  catalog entry exists, and its lifecycle status is one of
  `compile-only` / `hardware-pending` / `preview` / `production`.
  `legacy-compatible` is **also** product-supported in the sense
  that the YAML is retained and validated by the broad CI sweep —
  but it is intentionally not WebFlash-supported.
- A product is **WebFlash-supported** when it is in the build
  matrix on a non-blocked channel, has a published `.bin` matching
  its declared `artifact_name`, has been imported by WebFlash,
  appears in the deployed `manifest.json` / `firmware-N.json`, and
  is reachable from the customer flasher.

The two axes are independent. The 30+ `sense360-core-*` /
`sense360-mini-*` / `sense360-poe` / `sense360-fan-pwm` YAMLs are
product-supported (legacy-compatible) and **not** WebFlash-supported
by design. `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` is product-supported
(blocked, but YAML / wrapper retained as reference) and **not**
WebFlash-supported (build matrix excludes it under HW-005). The
inverse direction — WebFlash-supported without being product-
supported — is **not allowed**: WebFlash builds only what
[`config/webflash-builds.json`](../config/webflash-builds.json)
declares, and every build-matrix entry must point at a product YAML
with a matching catalog entry.

## Preview vs stable / production

The distinction between **preview** and **stable / production**
follows
[`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
(RELEASE-006). The short form:

- **`preview` / `preview-available`** means rows 1–8 of the
  RELEASE-006 [Gate summary](preview-to-stable-promotion-gates.md#gate-summary)
  are done: product YAML, wrapper, catalog preview entry, build
  matrix preview entry, preview release artifact, preview release
  proof, WebFlash import, live preview deploy. The build is
  customer-installable on a non-`stable` channel and is **not** a
  Release-One required config.
- **`production` / `stable-available`** means rows 1–17 of the
  RELEASE-006 gate summary are done or have accepted waivers,
  including the operator flash proof (`WF-HW-TEST-001`), hardware
  bench verification, stable release notes, production catalog
  promotion, stable build artifact, stable WebFlash import, and the
  separate (and **non-automatic**) `REQUIRED_CONFIGS` decision and
  kit / UI decision.
- **`production-required`** is **above** `stable-available`. A
  stable build does not automatically enter `REQUIRED_CONFIGS`.
- **`kit-exposed`** is also **above** `stable-available`. A stable
  build does not automatically get a kit.

No row in the gate table can be skipped by appeal to another row.
A successful preview release does **not** substitute for bench
verification; a verified schematic does **not** substitute for an
operator flash proof; a deployed preview manifest does **not**
substitute for a stable build.

## Blocked, legacy-compatible, deprecated, and removed

These four exception lifecycles are defined by
[`config/product-catalog.json`](../config/product-catalog.json) and
detailed in
[`docs/product-deprecation-removal-policy.md`](product-deprecation-removal-policy.md).
PRODUCT-AVAIL-001 places them on the [Concept
ladder](#concept-ladder) as follows:

- **`blocked`** is a hold at the rung the entry currently occupies.
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` is at `product-yaml-ready`
  (YAML, wrapper, catalog entry, hardware catalog row all exist) and
  is held below `build-matrix-ready` by the HW-005 blocker. Promotion
  requires clearing the blocker first.
  [`S360-320`](../config/hardware-catalog.json) is at
  `hardware-listed` and is additionally held below `schematic-verified`
  by HW-005 (no committed schematic) and below any product /
  WebFlash work by COMPLIANCE-001.
- **`legacy-compatible`** is a **parallel track**, not a ladder
  rung. Legacy YAMLs are retained for manual / remote-package users.
  They have no `config_string`, no `artifact_name`, no
  `webflash_wrapper`, and `webflash_build_matrix: false`. They never
  enter the build matrix and never reach `webflash-ready`. Per
  [PRODUCT-DEP-001](product-deprecation-removal-policy.md#deprecated-vs-removed-vs-blocked-vs-legacy-compatible),
  `legacy-compatible` is distinct from `deprecated`:
  `legacy-compatible` entries **were never WebFlash-shippable**;
  `deprecated` entries **were WebFlash-shippable and are being
  phased out**.
- **`deprecated`** is a **descent** from `webflash-live-preview` or
  `webflash-live-stable`. Carries `deprecation_reason`,
  `deprecated_since`, and either `replacement_config_string` or
  `no_replacement_reason`, plus a `removal_target` or
  `removal_criteria`. Default `webflash_build_matrix: false`. No
  entry is `deprecated` today.
- **`removed`** is a **tombstone** below `deprecated`. The
  `config_string` is reserved; underlying YAML / wrapper /
  build-matrix / manifest entries are absent. No entry is `removed`
  today.

This document does not promote, demote, deprecate, or remove any
entry.

## Current board / product snapshot

The table below records the current availability state of every SKU
in [`config/hardware-catalog.json`](../config/hardware-catalog.json),
combining the hardware-evidence axis (HW-008 / HW-ASSETS-002 / the
HW-004 / HW-006 audit) with the product-support axis
([`config/product-catalog.json`](../config/product-catalog.json))
and the WebFlash-availability axis
([`config/webflash-builds.json`](../config/webflash-builds.json)).
This is a **snapshot**; the JSON files remain the source of truth
and win on drift.

| Board | Hardware evidence | Artifact index | Pin map | Package YAML | Product YAML | WebFlash | Notes |
|---|---|---|---|---|---|---|---|
| `S360-100` Sense360 Core | `schematic-verified` | `artifact-indexed` (HW-ASSETS-002) | `documented` | `package-yaml-ready` (Core stack carries a systemic abstract-bus mismatch flagged as `needs-package-change` and owned by [`release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups); package today is `confirmed-ok` against connector-level evidence) | `production` via Release-One; also consumed by the LED preview | `stable-available` (Release-One); `preview-available` (LED preview) | Used by `Ceiling-POE-VentIQ-RoomIQ` (stable) and `Ceiling-POE-VentIQ-RoomIQ-LED` (preview). Schematic-level Open Questions tracked in [`s360-100-r4-core.md`](hardware/s360-100-r4-core.md). |
| `S360-200` Sense360 RoomIQ | `schematic-verified` | `pin-map-pending` for an artifact index (HW-ASSETS-003 deferred) | `documented` | `package-yaml-ready` (`comfort_ceiling.yaml` / `presence_ceiling.yaml` target the abstract `expansion_i2c` / `uart_bus`; HW-009 row `confirmed-ok`) | `production` via Release-One; also consumed by the LED preview | `stable-available` (Release-One); `preview-available` (LED preview) | Core J10 vs RoomIQ J6 pin-order discrepancy remains `needs-silkscreen/bench-verification` per HW-009; package mappings do not depend on the pin number. |
| `S360-210` Sense360 AirIQ | `schematic-verified` | `pin-map-pending` for an artifact index (HW-ASSETS-004 deferred) | `documented`, `not-needed-for-release-one` | `package-yaml-ready` for AirIQ packages (`confirmed-ok`, legacy-naming caveat); mutex with VentIQ enforced by [`config/webflash-compatibility.json`](../config/webflash-compatibility.json) | No product YAML consumes AirIQ today (`firmware-missing` for any AirIQ-bearing config string) | `firmware-build-pending` for any AirIQ-bearing config string; mutually exclusive with VentIQ in current Release-One | A future AirIQ-bearing config requires its own catalog entry, build-matrix entry, and onboarding-gate clearance. `AirQ_Led` / `AirQ_Status_Led` reuse remains HW-002 Open Question #4. |
| `S360-211` Sense360 VentIQ | `schematic-verified` | `pin-map-pending` for an artifact index (HW-ASSETS-005 deferred) | `documented` | `package-yaml-ready` (legacy filename `airiq_bathroom_base.yaml` retained per [`docs/webflash-contract.md`](webflash-contract.md) §6) | `production` via Release-One; also consumed by the LED preview | `stable-available` (Release-One); `preview-available` (LED preview) | `AirQ_Led` / `AirQ_Status_Led` reuse remains HW-002 Open Question #4. Mains-side topology of the on-board relay is tracked under COMPLIANCE-001. |
| `S360-300` Sense360 LED | `schematic-verified` | `pin-map-pending` for an artifact index (HW-ASSETS-006 deferred) | `documented`, `not-needed-for-release-one` | `package-yaml-ready` for `led_ring_ceiling.yaml` after HW-010 (`led_data_pin: GPIO38`); `led_ring_wall.yaml` and `sense360_core_ceiling_s3.yaml` remain unresolved | `preview` via `Ceiling-POE-VentIQ-RoomIQ-LED` | `preview-available` (LED preview build attached at `v1.0.0-led-preview`; WebFlash import per WF-LED-001 / WF-LED-002; live preview deploy per WF-LED-003 / WF-DEPLOY-001) | Stable promotion blocked by [RELEASE-006](preview-to-stable-promotion-gates.md) rows 9–17: WebFlash flash proof (WF-HW-TEST-001), hardware bench verification (harness rail, LED count, harness identity per [`s360-300-r4-led.md`](hardware/s360-300-r4-led.md#open-questions--verification-needed)), stable release notes, production catalog promotion, stable build artifact, stable WebFlash import, separate REQUIRED_CONFIGS / kit decisions, human approval. **Stays `status: preview`, `channel: preview`.** |
| `S360-310` Sense360 Relay | `cataloged-unverified` JSON / `partially-documented` audit (Core-side `J4` connector captured) | `pin-map-pending` for an artifact index | `partially-documented`, `not-needed-for-release-one` | [`packages/expansions/fan_relay.yaml`](../packages/expansions/fan_relay.yaml) exists; `package-yaml-pending` against module-side schematic | No product YAML consumes this board today (`firmware-missing` for any FanRelay-bearing config) | `firmware-build-pending` / `design-pending` for any FanRelay-bearing config | Productization pending: module-side schematic, standalone pin/connector doc, pin-map reconciliation. HW-PINMAP-310 audit doc landed at [`hardware/s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md) with **status: `pending — schematic/design evidence required`**; records the `IO3` vs `GPIO4` vs `GPIO10` `relay_pin` disagreement as unresolved. Follow-ups: `HW-ASSETS-310`, `HW-PINMAP-310-FOLLOWUP`, `PACKAGE-GAP-001` FanRelay slice — per [`hardware/s360-310-r4-relay.md` Follow-up PRs](hardware/s360-310-r4-relay.md#follow-up-prs) and [HW-ASSETS-001 Follow-up PR sequence](hardware/hardware-artifact-policy.md#follow-up-pr-sequence). |
| `S360-311` Sense360 PWM | `cataloged-unverified` JSON / `partially-documented` audit (Core-side `J6` 13-pin connector captured; pin-order **verify**) | `pin-map-pending` for an artifact index | `partially-documented`, `not-needed-for-release-one` | [`packages/expansions/fan_pwm.yaml`](../packages/expansions/fan_pwm.yaml) exists; `package-yaml-pending` against module-side schematic | No product YAML consumes this board today (`firmware-missing` for any FanPWM-bearing config) | `firmware-build-pending` / `design-pending` for any FanPWM-bearing config | Productization pending; J6 pin-order **verify** must be resolved against silkscreen. Follow-up `HW-PINMAP-311`. |
| `S360-312` Sense360 DAC | `cataloged-unverified` JSON / `partially-documented` audit (Core-side `J7` 6-pin connector fully captured) | `pin-map-pending` for an artifact index | `partially-documented`, `not-needed-for-release-one` | [`packages/expansions/fan_gp8403.yaml`](../packages/expansions/fan_gp8403.yaml) exists; `package-yaml-pending` against module-side schematic | No product YAML consumes this board today (`firmware-missing` for any FanDAC-bearing config) | `firmware-build-pending` / `design-pending` for any FanDAC-bearing config | Productization pending; FanDAC ↔ AirIQ conflict enforced in [`config/webflash-compatibility.json`](../config/webflash-compatibility.json). Follow-up `HW-PINMAP-312`. |
| `S360-320` Sense360 TRIAC | `cataloged-unverified` JSON / `blocked` audit (HW-005 + COMPLIANCE-001) | `pin-map-pending` for an artifact index | `blocked` (HW-005); also gated by COMPLIANCE-001 | [`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml) retained as **blocked / reference**; `package-yaml-pending` against any verified schematic | `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` exists as `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`; YAML / wrapper retained as reference only | `firmware-build-pending` / `blocked` | **Stays blocked.** HW-005 missing-evidence checklist must be satisfied **and** COMPLIANCE-001 mains-voltage review must clear before any product / WebFlash work. The SX1509-only hypothesis is rejected; `ac_dimmer` requires direct interrupt-capable ESP32 GPIOs. |
| `S360-400` Sense360 240v PSU | `cataloged-unverified` JSON / `cataloged-unverified` audit | `pin-map-pending` for an artifact index | `pin-map-pending`, `not-needed-for-release-one`; also gated by COMPLIANCE-001 | [`packages/hardware/power_240v.yaml`](../packages/hardware/power_240v.yaml) is a logical-power package with no GPIO binding | No product YAML consumes this board today (`firmware-missing` for any PWR-bearing config) | `firmware-build-pending` / `design-pending` / mains-compliance-gated | Productization pending. Mains-voltage compliance gate per [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md). Release-One uses `S360-410` PoE instead. Follow-up `HW-PINMAP-400`. |
| `S360-410` Sense360 PoE PSU | `cataloged-unverified` JSON / `partially-documented` audit (Core-side `J2` `PoE_ACDC` inlet captured; module-side schematic pending) | `pin-map-pending` for an artifact index | `partially-documented` (`J2` harness identity remains HW-002 Open Question #6) | [`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml) is a logical PoE-power package emitting diagnostic sensors only; `package-yaml-ready` (logical, no GPIO binding) | `production` via Release-One — the "schematic verification pending" caveat is preserved in the catalog `notes` and in [`release-one-hardware-audit.md`](release-one-hardware-audit.md) | `stable-available` (consumed by Release-One); `preview-available` (consumed by the LED preview) | **In Release-One under a `partially-documented` evidence state.** Module-side schematic + standalone pin/connector doc are open work for `HW-PINMAP-410`. The caveat is not promoted away. |

The hardware-evidence axis is the
[`config/hardware-catalog.json`](../config/hardware-catalog.json)
`schematic_status` and the audit row in
[`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md).
The product axis is
[`config/product-catalog.json`](../config/product-catalog.json).
The WebFlash axis is
[`config/webflash-builds.json`](../config/webflash-builds.json) plus
the WebFlash-side import / manifest / deployment state owned by the
[`sense360store/WebFlash`](https://github.com/sense360store/WebFlash)
repo. PRODUCT-AVAIL-001 changes **none** of these values.

## How WebFlash should consume this taxonomy

This document is consumed by follow-up WebFlash-side work (today
WF-WIZARD-AVAIL-001; tomorrow WF-STALE-001 / PRODUCT-STALE-001 /
WF-PRODUCT-005). The required behaviours are:

- **Wizard must distinguish buildable from unbuildable.** A module
  named in [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  but currently in the `design-pending` or `firmware-missing` state
  must be shown as such in the wizard — explicitly **not** as
  installable. A combination that names such a module must be shown
  as "design pending — not buildable today" rather than letting the
  customer click flash.
- **WebFlash import readiness must reject `blocked`, `deprecated`,
  and `removed`.** The import / build-readiness gate must refuse
  any catalog entry whose lifecycle status is `blocked` /
  `deprecated` / `removed`, and must distinguish `preview` from
  `production`. The release-notes generator
  ([`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py))
  already enforces this.
- **Wizard must not imply installability** when any of the
  following are missing: product YAML; build-matrix entry; release
  `.bin`; WebFlash sidecar; deployed manifest entry. The wizard
  must surface a "this configuration is not available today"
  message instead of generating a flash button.
- **Kits must only reference WebFlash-ready products.** A kit in
  `scripts/data/kits.json` must reference a build that is
  `webflash-ready` on `stable` (or, by explicit decision, on a
  non-`stable` channel — see RELEASE-006 [Kit policy](preview-to-stable-promotion-gates.md#kit-policy)).
  Adding a kit for a `design-pending` / `firmware-missing` /
  `blocked` / `deprecated` / `removed` configuration is forbidden.
- **`REQUIRED_CONFIGS` must remain production / stable-only and
  intentionally chosen.** A stable build does not enter
  `REQUIRED_CONFIGS` by side effect. The decision is a separate
  WebFlash PR per RELEASE-006 [REQUIRED_CONFIGS policy](preview-to-stable-promotion-gates.md#required_configs-policy).
- **Wizard must surface the blocker name for `blocked` entries.**
  When `S360-320` / FanTRIAC is referenced, the wizard must cite
  HW-005 and COMPLIANCE-001 rather than rendering FanTRIAC as a
  selectable fan-driver option.
- **Wizard must respect mutex / "max one of" rules.** AirIQ ↔
  VentIQ mutex, fan-driver "max one of", FanDAC ↔ AirIQ conflict,
  and forbidden tokens are already enforced by
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  and
  [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py).
  PRODUCT-AVAIL-001 does not change them.

These behaviours are the **policy**. The actual wiring lives in
WF-WIZARD-AVAIL-001 (wizard gating), WF-STALE-001 /
PRODUCT-STALE-001 (stale-reference cleanup), and WF-PRODUCT-005
(import-readiness enforcement). None of those are in scope for this
PR.

## Future validator and schema work

The states above are documented today as **policy labels**. A
later PR — PRODUCT-AVAIL-002 — may promote some of them to
machine-readable fields. The candidate fields, mirroring the
HW-ASSETS-001 per-board artifact index schema, are:

```text
artifact_index_status
pin_map_status
package_yaml_status
product_yaml_status
webflash_status
availability_notes
missing_evidence
```

These names are **candidate names only**. PRODUCT-AVAIL-001 does
**not** add them to any JSON. They are recorded here so that a
future PR has a single vocabulary to start from.

The related backlog is:

- **PRODUCT-AVAIL-002** — add machine-readable availability fields
  to `config/product-catalog.json` and / or
  `config/hardware-catalog.json` if and only if a concrete consumer
  (a validator, a wizard gate, an import-readiness check) requires
  them. The default answer is "no fields added until needed".
- **HW-GAP-001** — board readiness matrix for S360 modules.
  Cross-board matrix recording, for every SKU, the current state on
  each axis (artifact index / pin map / package YAML / product YAML
  / WebFlash). Documentation-only follow-up.
- **PRODUCT-DEP-002** — `_validate_deprecated` / `_validate_removed`
  rule blocks in
  [`scripts/validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py)
  and matching tests. Already listed as backlog in
  [`docs/product-deprecation-removal-policy.md`](product-deprecation-removal-policy.md).
- **WF-PRODUCT-005** — WebFlash-side import-readiness enforcement
  for `blocked` / `deprecated` / `removed` catalog entries.
- **WF-WIZARD-AVAIL-001** — wizard gating for `design-pending` /
  `firmware-missing` / `blocked` modules and configs.
- **WF-STALE-001 / PRODUCT-STALE-001** — cleanup of stale
  references in docs / examples / wizard taxonomy that imply
  installability for modules / configs that are not buildable
  today.
- **PACKAGE-GAP-001 / PRODUCT-GAP-001** — add or reconcile package
  / product YAMLs where evidence exists; per the
  [HW-ASSETS-001 follow-up PR sequence](hardware/hardware-artifact-policy.md#follow-up-pr-sequence).

PRODUCT-AVAIL-001 itself adds **none** of these implementations.

## Follow-up PR sequence

The recommended sequence after PRODUCT-AVAIL-001 lands is:

1. **HW-GAP-001 — Board readiness matrix for S360 modules.** Uses
   the [current snapshot](#current-board--product-snapshot) above
   as its starting point and produces a single matrix doc that can
   be referenced by every downstream PR. Documentation-only.
   **Landed** at
   [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md).
2. **WF-WIZARD-AVAIL-001 — Gate unavailable modules / configs in
   wizard.** Implements the
   [WebFlash consumption](#how-webflash-should-consume-this-taxonomy)
   behaviours in the WebFlash wizard.
3. **WF-STALE-001 / PRODUCT-STALE-001 — Stale data cleanup.**
   Removes references that imply installability for combinations
   in the `design-pending` / `firmware-missing` state.
4. **PRODUCT-AVAIL-002 — Machine-readable availability fields.**
   Adds JSON fields only if a downstream consumer requires them.
5. **HW-PINMAP-310 / -311 / -312 / -320 / -400 / -410.** Per-board
   schematic ingest + standalone pin/connector doc, per the
   [HW-ASSETS-001 follow-up PR sequence](hardware/hardware-artifact-policy.md#follow-up-pr-sequence).
6. **PACKAGE-GAP-001 — Add / reconcile package YAMLs where
   evidence exists.** After the HW-PINMAP-* sequence.
7. **PRODUCT-GAP-001 — Add product YAMLs where packages and
   evidence exist.** After PACKAGE-GAP-001, goes through the
   [`docs/product-onboarding.md`](product-onboarding.md) gates and,
   for any stable promotion, the
   [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
   gates.

Each entry is its own PR, its own review, and its own scope. This
policy does not commit to a calendar.

## Do-not-change guardrails

PRODUCT-AVAIL-001 — this document — performs **none** of the
following. Anyone reading this document looking for justification
to change one of them must use a separate, scoped PR with its own
gate evidence.

- No edits to
  [`config/product-catalog.json`](../config/product-catalog.json),
  [`config/hardware-catalog.json`](../config/hardware-catalog.json),
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  or [`config/webflash-compatibility.json`](../config/webflash-compatibility.json).
- No new JSON fields added to any catalog; no new status / channel
  / lifecycle value added to any enum.
- No edits to any product YAML under [`products/`](../products/) or
  any WebFlash wrapper under
  [`products/webflash/`](../products/webflash/); no edits to any
  package YAML under [`packages/`](../packages/).
- No edits to any workflow under `.github/workflows/`, any script
  under [`scripts/`](../scripts/), any test under
  [`tests/`](../tests/), any component under `components/`, or any
  include under `include/`.
- No firmware regenerated; no GitHub Release created or modified;
  no manifest, no signing, no WebFlash import, no kit added.
- Release-One stays `Ceiling-POE-VentIQ-RoomIQ`, version `1.0.0`,
  channel `stable`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
  `v1.0.0`.
- The LED preview entry `Ceiling-POE-VentIQ-RoomIQ-LED` stays
  `status: preview`, `channel: preview`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`. No
  promotion to `production` / `stable`; no addition to
  `REQUIRED_CONFIGS`; no kit added.
- FanTRIAC stays `status: blocked`, `blocker: HW-005`,
  `webflash_build_matrix: false`. The HW-005 blocker is not
  resolved and COMPLIANCE-001 is not cleared.
- The mains-voltage compliance status for `S360-320` (FanTRIAC) and
  `S360-400` (240v PSU) is owned by COMPLIANCE-001 and is not
  changed.
- The Core J10 vs RoomIQ J6 pin-order discrepancy
  (`needs-silkscreen/bench-verification` per HW-009) is not
  resolved.
- The systemic Core abstract-bus mismatch in
  `packages/hardware/sense360_core_ceiling.yaml`
  (`needs-package-change`, owned by
  [`release-one-hardware-audit.md` Required follow-ups #2 / #3](release-one-hardware-audit.md#required-follow-ups))
  is not resolved.
- The 30+ `legacy-compatible` entries (Core `c-poe` / `c-pwr` /
  `c-usb` / `v-*` / `voice-*` / `ceiling` / `wall` / `presence` /
  `bathroom`; Mini `airiq` / `presence` variants; `sense360-poe`;
  `sense360-fan-pwm`) stay `legacy-compatible` and remain out of
  the WebFlash build matrix.
- No entry is added to or removed from WebFlash-side
  `REQUIRED_CONFIGS`, `scripts/data/kits.json`,
  `firmware/sources.json`, or `manifest.json` — those are
  WebFlash-owned and are not touched by this repo.

## See also

- [`README.md`](../README.md) — repo overview, Release-One quick
  reference, package reference.
- [`docs/product-onboarding.md`](product-onboarding.md) — PRODUCT-004
  ordered onboarding sequence; defines the eight lifecycle statuses
  in short form and orders the safe onboarding gates this taxonomy
  threads through.
- [`docs/product-deprecation-removal-policy.md`](product-deprecation-removal-policy.md)
  — PRODUCT-DEP-001 canonical cross-cutting deprecation / removal
  policy. Defines `deprecated` and `removed` and the required
  metadata; this taxonomy maps both states onto descent lower-than
  the live-stable rung.
- [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
  — RELEASE-006 canonical preview-to-stable promotion gate
  document. Defines the 17-row gate table that separates
  `preview-available` from `stable-available`, and the separate
  REQUIRED_CONFIGS and kit decision policies.
- [`docs/product-scaffold-generator.md`](product-scaffold-generator.md)
  — PRODUCT-010 read-only product scaffold generator. Cannot
  scaffold `production`, `deprecated`, `removed`, or
  `legacy-compatible`. Forces FanTRIAC-bearing scaffolds to
  `blocked` / HW-005.
- [`docs/product-led-preview-decision.md`](product-led-preview-decision.md)
  — PRODUCT-005 LED preview decision doc; PRODUCT-006 /
  PRODUCT-008 / PRODUCT-009 sequence that produced today's LED
  preview entry.
- [`docs/release-one.md`](release-one.md) — Release-One
  configuration; the only `production` entry today.
- [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)
  — Release-One firmware-vs-schematic audit, FanTRIAC HW-005
  resolution, Sense360 LED policy.
- [`docs/webflash-contract.md`](webflash-contract.md) — canonical
  WebFlash artifact / grammar / token contract; legacy package
  filenames retained on purpose; forbidden / future-token policy.
- [`docs/webflash-release-handoff.md`](webflash-release-handoff.md)
  — operational source-to-installer flow; the seam between
  `release-artifact-ready` and `webflash-imported`.
- [`docs/webflash-release-proof.md`](webflash-release-proof.md) —
  ESP-006 / ESP-007 Release-One proof record plus the RELEASE-003 /
  RELEASE-005 LED preview proof record.
- [`docs/webflash-compatibility-taxonomy-audit.md`](webflash-compatibility-taxonomy-audit.md)
  — COMPAT-001 per-token audit; the future-token policy that gates
  any new module name surfaced to WebFlash.
- [`docs/hardware/hardware-artifact-policy.md`](hardware/hardware-artifact-policy.md)
  — HW-ASSETS-001 canonical hardware source / manufacturing
  artifact policy. Defines the per-board artifact index schema
  whose `pin_map_status` / `package_yaml_status` /
  `product_yaml_status` / `webflash_status` fields are reused as
  policy-only vocabulary by this taxonomy.
- [`docs/hardware/artifacts/S360-100-R4.md`](hardware/artifacts/S360-100-R4.md)
  — HW-ASSETS-002 curated artifact index for Sense360 Core, the
  first board to apply HW-ASSETS-001.
- [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md)
  — HW-004 / HW-006 per-board documentation-state classification;
  source of the `documented` / `partially-documented` /
  `cataloged-unverified` / `blocked` / `not-needed-for-release-one`
  audit vocabulary.
- [`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
  — HW-009 / HW-010 firmware-package-vs-schematic audit; source of
  the `confirmed-ok` / `needs-package-change` / `needs-doc-fix` /
  `needs-silkscreen/bench-verification` / `blocked` / `unknown`
  classification vocabulary this taxonomy maps onto
  `package-yaml-ready` / `package-yaml-pending`.
- [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
  — HW-GAP-001 board-level readiness matrix. Expands the
  [Current board / product snapshot](#current-board--product-snapshot)
  above into a per-board × per-axis matrix (artifact index / pin map /
  package YAML / product YAML / WebFlash wrapper / build matrix /
  release artifact / WebFlash manifest / bench proof) and records the
  follow-up PR sequence for the six `cataloged_unverified` boards.
  Documentation only.
- [`docs/hardware-catalog.md`](hardware-catalog.md) — canonical
  Sense360 board / module names, SKUs, revisions; the naming
  source of truth this taxonomy quotes.
- [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  — machine-readable hardware catalog. `schematic_status` is
  `verified` for five SKUs and `cataloged_unverified` for the
  remaining six. PRODUCT-AVAIL-001 changes none of these values.
- [`config/product-catalog.json`](../config/product-catalog.json)
  — machine-readable product catalog. Declares the eight
  `lifecycle_statuses` reused verbatim by this taxonomy.
- [`config/webflash-builds.json`](../config/webflash-builds.json) —
  machine-readable WebFlash build matrix; source of truth for what
  this repo actually ships.
- [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  — machine-readable WebFlash taxonomy / token / mutex / forbidden
  rules.
- [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
  — COMPLIANCE-001 mains-voltage UK / EU compliance-assessment
  tracker; gate for any product / WebFlash work consuming
  `S360-320` (FanTRIAC) or `S360-400` (240v PSU).
- [`docs/cleanup-audit.md`](cleanup-audit.md) — classification of
  stale / current / blocked-reference / legacy-compatible repo
  content; carries the PRODUCT-AVAIL-001 registration row.

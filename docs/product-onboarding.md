# Product Onboarding Guide (PRODUCT-004)

## Purpose & scope

This guide is the single ordered checklist for safely adding a new Sense360
product configuration to this repository. It threads together the existing
guardrails — the hardware-documentation audit, the mains-voltage compliance
tracker, the product catalog, the consistency validator, the WebFlash build
matrix, the release-notes draft generator, and the WebFlash release-handoff
record — into one defined sequence with explicit "what evidence must exist
before this step" gates.

This guide is **documentation only**. It does not:

- add, remove, or modify any product YAML, WebFlash wrapper, or package
  YAML,
- add, remove, or modify any entry in
  [`config/product-catalog.json`](../config/product-catalog.json),
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
  or [`config/hardware-catalog.json`](../config/hardware-catalog.json),
- change any workflow, script, test, component, or include file,
- promote any module from `cataloged-unverified` /
  `partially-documented` / `blocked` to `preview` / `stable` /
  `production`,
- change the Release-One shipping configuration
  `Ceiling-POE-VentIQ-RoomIQ` or its artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`,
- change the FanTRIAC HW-005 blocked status,
- change the Sense360 LED Release-One exclusion status.

The source-of-truth documents this guide threads together are the ones in
[Where each source of truth lives](#where-each-source-of-truth-lives).
**If this guide and any of those source-of-truth documents drift, the
source-of-truth document wins** and this guide must be updated.

## Product lifecycle states

[`config/product-catalog.json`](../config/product-catalog.json) declares
the following lifecycle statuses. Every catalog entry carries exactly one.

| Status | Meaning |
|---|---|
| `production` | WebFlash-shippable, in the build matrix, has an artifact name, has a wrapper, has verified-for-its-release hardware status. Release-One is the only `production` entry today. |
| `preview` | WebFlash-eligible but not on the `stable` channel. Acceptable on `preview` / `beta`. Must not be a Release-One required config. |
| `compile-only` | Compiles in CI but is not promoted to WebFlash. Used during early bring-up. |
| `hardware-pending` | YAML and packages exist, but required hardware evidence is missing. Not WebFlash-eligible. |
| `blocked` | Intentionally not shippable because a named blocker (e.g. HW-005) is open. Must carry `blocker` and `reason`. Must not appear in `config/webflash-builds.json`. |
| `legacy-compatible` | Pre-WebFlash YAML kept for manual / custom users. No `config_string`, no `artifact_name`, no `webflash_wrapper`. `webflash_build_matrix: false`. Not WebFlash-shippable. |
| `deprecated` | Was shipped, now being phased out. Not WebFlash-shippable. |
| `removed` | Tombstone for a configuration that no longer exists in the repo. |

These eight values are enumerated in `product-catalog.json` under
`lifecycle_statuses` and enforced by
[`tests/test_product_catalog.py`](../tests/test_product_catalog.py) and
[`scripts/validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py).

## Safe onboarding sequence

Run these steps in this order. Each step has a gate; do not advance until
the gate passes.

1. **Hardware evidence first.** Confirm that the new module (or
   combination of modules) is `documented` or `partially-documented` in
   [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md#decision-table).
   If it is `cataloged-unverified` or `blocked`, stop — commit the
   missing schematic and a standalone pin/connector reference doc under
   `docs/hardware/` first, then update
   [`config/hardware-catalog.json`](../config/hardware-catalog.json) and
   the audit row in the same PR.
2. **Compliance check if mains voltage is involved.** If the
   configuration includes `S360-400` Sense360 240v PSU (mains input) or
   `S360-320` Sense360 TRIAC (mains output), an electrical-safety and
   compliance review is required before preview or stable. The
   structured tracker is
   [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md).
   That tracker is documentation only and makes no compliance claim;
   the actual review is out of scope for this repo. Do not advance to
   preview or stable until the tracker rows resolve to evidence-backed
   answers.
3. **Product YAML / package design.** Compose the new product YAML
   under `products/` and (if needed) a WebFlash wrapper under
   `products/webflash/` that `!include`s it. Reuse the existing
   package YAMLs under `packages/hardware/`, `packages/expansions/`,
   and `packages/features/`. Filenames keep the legacy form
   (`airiq_bathroom_*`, `comfort_*`, `presence_*`) per the WebFlash
   contract — the canonical names live in the config string, not on
   disk.
4. **Product catalog entry.** Add the entry to
   [`config/product-catalog.json`](../config/product-catalog.json) with
   the correct lifecycle status from
   [Product lifecycle states](#product-lifecycle-states). Declare the
   status before adding the build-matrix entry. For non-shippable
   states (`compile-only`, `hardware-pending`, `blocked`,
   `legacy-compatible`, `deprecated`, `removed`) set
   `webflash_build_matrix: false` and omit `artifact_name` /
   `webflash_wrapper` as required by the status's rule block in
   [`scripts/validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py).
5. **Product catalog consistency validator.** Run
   `python3 scripts/validate_product_catalog_consistency.py` until it
   exits zero. For a focused check on the new entry, use
   `--checklist <CONFIG_STRING_OR_LEGACY_ID>` or
   `--product <PATH>`. The validator never mutates a file and never
   generates a scaffold YAML.
6. **WebFlash compatibility / build matrix decision.** Only after the
   catalog entry validates, decide whether to add the entry to
   [`config/webflash-builds.json`](../config/webflash-builds.json). The
   rules in [`docs/webflash-contract.md`](webflash-contract.md) — token
   grammar, mutual-exclusion, fan-driver "max one of", forbidden
   tokens, channel membership — are enforced by
   [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py).
   Blocked, legacy-compatible, deprecated, and removed entries must
   never be added to the build matrix.
7. **Release notes draft.** Use
   [`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py)
   (or the manual `workflow_dispatch` workflow
   [`.github/workflows/release-notes-draft.yml`](../.github/workflows/release-notes-draft.yml))
   to draft the GitHub Release body. The generator refuses blocked /
   legacy-compatible / deprecated / removed entries, refuses `preview`
   entries on the `stable` channel, and emits FanTRIAC and Sense360
   LED as Known-Issues exclusions, never as Features. The
   `## Changelog` section is a TODO bullet — a human must replace it
   before publishing.
8. **Firmware build / release proof.** The build/release pipeline at
   [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)
   builds only the WebFlash build matrix and asserts the produced
   artifact name against the declared `artifact_name` via
   [`tests/check_webflash_build_output.py`](../tests/check_webflash_build_output.py).
   A successful run, with the GitHub Release tag, asset name, Actions
   run URL, and ESP-006 / ESP-007 proof, is recorded in
   [`docs/release-one.md`](release-one.md#proof-of-build-recorded) and
   [`docs/webflash-release-proof.md`](webflash-release-proof.md). A new
   `production` entry needs its own equivalent proof row.
9. **WebFlash import / publish.** WebFlash is the production signing /
   deployment authority. It ingests unsigned `.bin` assets attached to
   GitHub Releases via `scripts/sync-from-releases.py`, generates its
   own `manifest.json` / `firmware-N.json`, and publishes the result.
   See [`docs/webflash-release-handoff.md`](webflash-release-handoff.md)
   and [`docs/webflash-contract.md`](webflash-contract.md) for the
   handoff contract. This repo does not sign firmware, does not host
   firmware for end users, and does not generate manifests.

## Required evidence before preview

Before a catalog entry may be set to `status: preview`:

- Every module in the config string is at least
  `partially-documented` in the
  [decision table](hardware/remaining-board-documentation-audit.md#decision-table).
  `cataloged-unverified` and `blocked` modules disqualify the config.
- The Release-One hardware audit
  [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)
  does not flag the config as blocked. If a "schematic verification
  pending" caveat applies to a module (e.g. VentIQ, PoE PSU), the
  caveat must remain visible in the catalog `notes` and in any docs
  that reference the new entry — do not promote the caveat away.
- If the config includes any mains-voltage module
  (`S360-400` or `S360-320`), the
  [mains-voltage compliance tracker](compliance/mains-voltage-uk-eu-assessment.md)
  rows for that module resolve to evidence-backed answers, not
  `To be confirmed` or `Requires qualified review`.
- The product YAML and the WebFlash wrapper exist and pass
  [`tests/validate_configs.py`](../tests/validate_configs.py).
- The catalog entry carries `config_string`, `product_yaml`, and
  `hardware_status`. If `webflash_build_matrix: true`, it also
  carries `webflash_wrapper` and the wrapper file exists.
- The catalog entry's `channel` (where present) is **not** `stable`.
- The catalog entry's `config_string` is **not** in
  `release_one_required_configs` — preview is not a Release-One
  variant.
- [`scripts/validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py)
  passes for the new entry.

## Required evidence before production

Before a catalog entry may be set to `status: production`:

- Every module in the config string is `documented`, or
  `partially-documented` with the caveat explicitly retained in the
  catalog `notes` and accepted by the relevant audit doc (e.g.
  Release-One accepts VentIQ + PoE PSU as `partially-documented`
  because the Core-side connector captures and the
  "schematic verification pending" labels are committed). No module
  may be `cataloged-unverified` or `blocked`.
- If the config includes any mains-voltage module
  (`S360-400` or `S360-320`), the
  [mains-voltage compliance tracker](compliance/mains-voltage-uk-eu-assessment.md)
  rows resolve to evidence-backed answers and a qualified electrical
  safety / compliance review has been completed and recorded outside
  this repo. Documentation alone is not sufficient to ship mains
  hardware.
- The catalog entry carries every field required by the validator's
  production-rule block:
  `config_string`, `version`, `channel`, `artifact_name`,
  `webflash_wrapper`, `hardware_status`, `hardware` (non-empty map),
  `modules` (non-empty map), and `webflash_build_matrix: true`.
- The basename of `webflash_wrapper` (without `.yaml`) equals the
  `config_string` lower-cased.
- The entry appears in
  [`config/webflash-builds.json`](../config/webflash-builds.json) with
  the same `config_string`, `product_yaml`, `artifact_name`,
  `channel`, and `version`.
- The declared `artifact_name` equals
  `generate_webflash_filename(basename(product_yaml, .yaml), version, channel)`
  from
  [`scripts/product_name_mapper.py`](../scripts/product_name_mapper.py).
- Every SKU in `hardware` exists in
  [`config/hardware-catalog.json`](../config/hardware-catalog.json).
- A release-notes draft has been generated by
  [`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py)
  with `--validate`, and the `## Changelog` section has been replaced
  by a human-written, user-visible summary (the generator refuses
  filler placeholders for `stable` builds).
- A firmware build / release proof equivalent to the Release-One row
  in
  [`docs/release-one.md`](release-one.md#proof-of-build-recorded) has
  been recorded: GitHub Release tag, asset name, Actions run URL,
  workflow event, and ESP-006 / ESP-007 status.
- [`scripts/validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py),
  [`tests/test_product_catalog.py`](../tests/test_product_catalog.py),
  [`tests/test_product_catalog_consistency.py`](../tests/test_product_catalog_consistency.py),
  [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py),
  [`tests/test_webflash_compatibility.py`](../tests/test_webflash_compatibility.py),
  [`tests/test_webflash_artifact_naming.py`](../tests/test_webflash_artifact_naming.py),
  and
  [`tests/test_validate_webflash_release_notes.py`](../tests/test_validate_webflash_release_notes.py)
  all pass.

## Where each source of truth lives

| Concern | Source of truth |
|---|---|
| Product lifecycle (status, modules, blocked modules, hardware SKUs) | [`config/product-catalog.json`](../config/product-catalog.json) — validated by [`tests/test_product_catalog.py`](../tests/test_product_catalog.py). |
| WebFlash build matrix (what this repo actually ships) | [`config/webflash-builds.json`](../config/webflash-builds.json) — validated by [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py). |
| WebFlash contract snapshot (tokens, grammar, forbidden tokens, mutual-exclusion, conflicts, fan-driver "max one of") | [`config/webflash-compatibility.json`](../config/webflash-compatibility.json) and the prose contract [`docs/webflash-contract.md`](webflash-contract.md). |
| Canonical Sense360 board / module names, SKUs, revisions, `schematic_status` | [`config/hardware-catalog.json`](../config/hardware-catalog.json) and [`docs/hardware-catalog.md`](hardware-catalog.md). |
| Per-board documentation state (`documented` / `partially-documented` / `cataloged-unverified` / `blocked` / `not-needed-for-release-one`) | [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md). |
| Schematic-backed pin / connector references | [`docs/hardware/s360-100-r4-core.md`](hardware/s360-100-r4-core.md) and [`docs/hardware/s360-200-r4-roomiq.md`](hardware/s360-200-r4-roomiq.md). |
| Firmware-package-vs-schematic reconciliation classification (`confirmed-ok` / `needs-package-change` / `needs-doc-fix` / `needs-silkscreen/bench-verification` / `blocked` / `unknown`) | [`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md) (HW-009). Documentation only — does not change firmware, product YAML, package YAML, or JSON. |
| Release-One config / artifact / exclusions and FanTRIAC HW-005 + LED policy | [`docs/release-one.md`](release-one.md) and [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md). |
| Mains-voltage UK / EU compliance tracker (`S360-400`, `S360-320`) | [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md). Documentation only; not a compliance claim. |
| Catalog ↔ build matrix ↔ compatibility ↔ hardware ↔ mapper consistency | [`scripts/validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py), unit-tested by [`tests/test_product_catalog_consistency.py`](../tests/test_product_catalog_consistency.py). |
| Artifact-name generation (product YAML → WebFlash filename) | [`scripts/product_name_mapper.py`](../scripts/product_name_mapper.py), enforced at build time by [`tests/check_webflash_build_output.py`](../tests/check_webflash_build_output.py) and statically by [`tests/test_webflash_artifact_naming.py`](../tests/test_webflash_artifact_naming.py). |
| GitHub Release body format | [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py) and `docs/webflash-contract.md §8`. |
| Release-notes draft generator | [`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py), unit-tested by [`tests/test_generate_webflash_release_notes.py`](../tests/test_generate_webflash_release_notes.py). |
| Manual release-notes draft workflow | [`.github/workflows/release-notes-draft.yml`](../.github/workflows/release-notes-draft.yml), smoke-tested by [`tests/test_release_notes_draft_workflow.py`](../tests/test_release_notes_draft_workflow.py). |
| Build / release pipeline | [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml). |
| WebFlash handoff (source-to-installer flow, troubleshooting, release proof checklist) | [`docs/webflash-release-handoff.md`](webflash-release-handoff.md). |
| Audit / classification of stale / current / blocked-reference / legacy-compatible repo content | [`docs/cleanup-audit.md`](cleanup-audit.md). |

## Commands to run

All of these commands are **read-only**. None of them mutate files,
push to a remote, build firmware, or call any external service.

```text
python3 scripts/validate_product_catalog_consistency.py
python3 scripts/validate_product_catalog_consistency.py --checklist Ceiling-POE-VentIQ-RoomIQ
python3 tests/test_product_catalog.py
python3 tests/test_product_catalog_consistency.py
python3 tests/validate_webflash_builds.py
python3 tests/test_webflash_artifact_naming.py
python3 scripts/generate_webflash_release_notes.py --config-string Ceiling-POE-VentIQ-RoomIQ --version 1.0.0 --channel stable --output /tmp/release-notes.md --validate
```

When adding a new product, substitute its `config_string` (or
`legacy_config_id`) into the `--checklist` invocation and substitute
the new `config_string`, `version`, and `channel` into the
release-notes generator. Preview entries must use a non-`stable`
channel. Blocked, legacy-compatible, deprecated, and removed entries
will (correctly) be refused by the release-notes generator.

## What not to do

These guardrails apply to every onboarding PR. They are not optional.

- **Do not mark a product `production` just because YAML compiles.**
  A successful `validate_configs.py` run is necessary but not
  sufficient. Production also requires hardware evidence, compliance
  evidence (if mains), build-matrix entry, mapper agreement, a
  release-notes draft, and a recorded build / release proof.
- **Do not add blocked products to
  [`config/webflash-builds.json`](../config/webflash-builds.json).**
  The build matrix is the WebFlash-shippable set. Blocked,
  legacy-compatible, deprecated, and removed entries must remain out
  of it.
- **Do not add FanTRIAC until HW-005 evidence changes.** Sense360
  TRIAC (`S360-320`) stays `blocked` while
  [`docs/release-one-hardware-audit.md#fantriac-mapping-resolution`](release-one-hardware-audit.md#fantriac-mapping-resolution)
  records an open blocker (schematic uncommitted; `TRI_GPIO1` /
  `TRI_GPIO2` not traced to direct interrupt-capable ESP32 GPIOs;
  `ac_dimmer` over SX1509 expander is rejected). This guide does
  not promote FanTRIAC to preview or stable.
- **Do not add `LED` to Release-One without an LED token and hardware
  evidence.** The Release-One config string `Ceiling-POE-VentIQ-RoomIQ`
  does not carry a `LED` token; the Release-One YAML omits LED
  package includes on purpose. A future LED-bearing config (e.g.
  `Ceiling-POE-VentIQ-RoomIQ-LED`) requires its own `S360-300`
  schematic, reconciliation of the `GPIO14` (package) vs `IO38`
  (schematic) `LED_DATA` discrepancy, a new catalog entry, and a new
  build-matrix entry — not a modification of Release-One.
- **Do not treat `legacy-compatible` as WebFlash-shippable.**
  `legacy-compatible` entries are retained for manual / custom /
  remote-package users. They have no `config_string`, no
  `artifact_name`, no `webflash_wrapper`, and `webflash_build_matrix`
  is `false`. WebFlash builds are sourced exclusively from
  [`config/webflash-builds.json`](../config/webflash-builds.json).
- **Do not use mains-voltage boards before compliance review.**
  `S360-400` Sense360 240v PSU and `S360-320` Sense360 TRIAC are
  mains AC. Both require an electrical-safety / compliance review
  tracked in
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
  before any preview / stable promotion in any future config string.
- **Do not hand-edit generated manifests.** WebFlash's
  `scripts/gen-manifests.py` generates `manifest.json` /
  `firmware-N.json` from the binaries WebFlash ingests via
  `scripts/sync-from-releases.py`. This repo never authors those
  files, never edits them, and never authors WebFlash sidecar
  `*.meta.json` files directly. Drift between hand-edited manifests
  and the WebFlash importer will silently break customer flashing.

## Example: current Release-One

`Ceiling-POE-VentIQ-RoomIQ` walks through the
[Safe onboarding sequence](#safe-onboarding-sequence) like this — every
gate is already cleared today, so this is the canonical worked example
of a `production` entry.

1. **Hardware evidence first.** Core (`S360-100`) and RoomIQ
   (`S360-200`) are `documented`; VentIQ (`S360-211`) and PoE PSU
   (`S360-410`) are `partially-documented` with the "schematic
   verification pending" caveat preserved
   ([decision table](hardware/remaining-board-documentation-audit.md#decision-table)
   and [Release-One coverage summary](hardware/remaining-board-documentation-audit.md#release-one-coverage-summary)).
2. **Compliance check.** Release-One uses PoE (`S360-410`); no
   mains-voltage module is in the config string. The mains-voltage
   compliance tracker does not gate this config — but it is still
   linked from
   [`docs/release-one.md`](release-one.md) and
   [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md#mains-voltage-safety-and-compliance-note)
   so the separation stays visible.
3. **Product YAML / package design.** Canonical product YAML
   [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml)
   and WebFlash wrapper
   [`products/webflash/ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml).
   The product is composed from `packages/hardware/sense360_core_ceiling.yaml`,
   `packages/hardware/power_poe.yaml`,
   `packages/expansions/airiq_bathroom_base.yaml` (VentIQ; legacy
   filename retained per the WebFlash contract),
   `packages/expansions/comfort_ceiling.yaml`, and
   `packages/expansions/presence_ceiling.yaml`. FanTRIAC and LED
   packages are intentionally omitted.
4. **Product catalog entry.** Recorded as
   `status: production`, `version: 1.0.0`, `channel: stable`,
   `artifact_name: Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`,
   `webflash_build_matrix: true`, `hardware_status:
   verified-for-release-one`, with `blocked_modules: [FanTRIAC, LED]`.
5. **Product catalog consistency validator.**
   `python3 scripts/validate_product_catalog_consistency.py` and
   `--checklist Ceiling-POE-VentIQ-RoomIQ` both pass.
6. **WebFlash build matrix.** Entry in
   [`config/webflash-builds.json`](../config/webflash-builds.json)
   with the same `config_string`, `product_yaml`,
   `artifact_name`, `channel`, `version`, `chip_family`,
   `hardware_requirements`, and `features`.
   [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py)
   passes.
7. **Release notes draft.** Generated by
   [`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py)
   with FanTRIAC and Sense360 LED in `## Known Issues` (never in
   `## Features`). A human replaces the `## Changelog` TODO before
   tagging.
8. **Firmware build / release proof.** GitHub Release `v1.0.0`,
   asset `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`,
   Actions run `25763009641`, ESP-006 and ESP-007 proven — see
   [`docs/release-one.md` → Proof of build (recorded)](release-one.md#proof-of-build-recorded)
   and [`docs/webflash-release-proof.md`](webflash-release-proof.md).
9. **WebFlash import / publish.** WebFlash production signing, the
   WebFlash production-signed `manifest.json`, and WebFlash deploy
   remain WebFlash-owned per
   [`docs/webflash-release-handoff.md`](webflash-release-handoff.md)
   and [`docs/webflash-contract.md`](webflash-contract.md). This
   repo only publishes the unsigned `.bin` and the Release body.

## Example: blocked FanTRIAC

`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stops at step 1 today and is the
canonical worked example of a `blocked` entry. It is retained in the
repo as a reference, **not** as a shippable target.

1. **Hardware evidence first.** Sense360 TRIAC (`S360-320`) is
   `blocked` (HW-005,
   `not-needed-for-release-one`) in the
   [decision table](hardware/remaining-board-documentation-audit.md#decision-table).
   The Release-One hardware audit lays out the missing-evidence
   checklist at
   [`docs/release-one-hardware-audit.md#fantriac-mapping-resolution`](release-one-hardware-audit.md#fantriac-mapping-resolution):
   `S360-320` schematic uncommitted; `TRI_GPIO1` / `TRI_GPIO2` not
   traced to direct interrupt-capable ESP32 GPIOs; ESPHome's
   `ac_dimmer` over the SX1509 expander rejected on timing grounds.
   **The sequence stops here.** Steps 2 through 9 do not proceed
   until HW-005 evidence changes.
2. **Compliance check (also required).** Sense360 TRIAC is
   mains-output. Even if HW-005 resolved, the mains-voltage
   compliance tracker
   [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
   would be a separate, prior gate before preview or stable. HW-005
   does not substitute for compliance review and compliance review
   does not substitute for HW-005.
3-9. **Not reached.** The product YAML
   [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml)
   and the WebFlash wrapper
   [`products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml)
   are retained as blocked / reference files only.
   [`packages/expansions/fan_triac.yaml`](../packages/expansions/fan_triac.yaml)
   carries an explicit BLOCKED / UNVERIFIED banner. The catalog
   entry is `status: blocked`, `blocker: HW-005`,
   `webflash_build_matrix: false`, with no `artifact_name`. It is
   **not** in
   [`config/webflash-builds.json`](../config/webflash-builds.json).
   The release-notes generator refuses to draft a body for it. No
   firmware is built, no release tag is cut, no WebFlash import
   happens.

This guide does not unblock FanTRIAC, does not modify any FanTRIAC
file, and does not change the FanTRIAC HW-005 blocked status.

## Future WebFlash handoff

What this repo produces, per
[`docs/webflash-contract.md`](webflash-contract.md):

- An unsigned `.bin` file attached to a GitHub Release as an asset,
  with a filename matching
  `Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin` exactly.
- A GitHub Release body with the four required H2 sections in order
  (`## Changelog`, `## Known Issues`, `## Features`,
  `## Hardware Requirements`), each as a Markdown bullet list, with
  a human-authored `## Changelog`.

What WebFlash does, owned by the
[`sense360store/WebFlash`](https://github.com/sense360store/WebFlash)
repo:

- Pull the unsigned `.bin` from the GitHub Release via
  `scripts/sync-from-releases.py`.
- Parse the Release body into the `*.meta.json` sidecar.
- Generate `manifest.json` / `firmware-N.json` via
  `scripts/gen-manifests.py`.
- Production sign the firmware.
- Host and serve the customer-facing flasher at
  [mysense360.com](https://mysense360.com).

What this repo must **not** do:

- Sign firmware. WebFlash is the production signing authority.
- Host firmware for end users. WebFlash hosts the customer-facing
  catalog.
- Generate or hand-edit `manifest.json`, `firmware-N.json`, or any
  `*.meta.json` sidecar.
- Overwrite a previously published `.bin` in place. WebFlash caches
  binaries under `Cache-Control: max-age=31536000`. A new build
  always gets a new version bump and a new filename.

For the operational source-to-installer flow, troubleshooting steps,
and the per-release proof checklist, see
[`docs/webflash-release-handoff.md`](webflash-release-handoff.md).

## See also

- [`README.md`](../README.md) — repo overview, Release-One quick
  reference, package reference.
- [`docs/release-one.md`](release-one.md) — Release-One configuration
  with full slot / file / binary mapping and the recorded build /
  release proof row.
- [`docs/webflash-contract.md`](webflash-contract.md) — canonical
  WebFlash artifact / grammar / token contract.
- [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)
  — Release-One firmware-vs-schematic audit, FanTRIAC HW-005
  resolution, and Sense360 LED policy.
- [`docs/hardware-catalog.md`](hardware-catalog.md) — canonical
  Sense360 board / module names, SKUs, revisions.
- [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md)
  — per-board documentation-state classification (HW-004 / HW-006).
- [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
  — mains-voltage UK / EU compliance-assessment tracker
  (COMPLIANCE-001). Documentation only.
- [`docs/webflash-release-handoff.md`](webflash-release-handoff.md)
  — operational source-to-installer flow.
- [`docs/webflash-release-proof.md`](webflash-release-proof.md) —
  ESP-006 / ESP-007 proof record.
- [`docs/cleanup-audit.md`](cleanup-audit.md) — classification of
  stale / current / blocked-reference / legacy-compatible repo
  content.
- [`docs/webflash-compatibility-taxonomy-audit.md`](webflash-compatibility-taxonomy-audit.md)
  — COMPAT-001 per-token audit of the WebFlash taxonomy against the
  product catalog, hardware evidence, and future-token policy.

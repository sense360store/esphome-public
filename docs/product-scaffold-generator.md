# Product Scaffold Generator (PRODUCT-010)

## Purpose & scope

[`scripts/scaffold_product.py`](../scripts/scaffold_product.py) is a
conservative, **report-only** helper for future maintainers preparing a
new Sense360 product configuration. It is intended to reduce manual
mistakes (wrong grammar, missing hardware evidence, accidentally claiming
a Release-One required slot, accidentally requesting a build-matrix
entry on a non-shippable status) without bypassing human review.

This guide is **documentation only**. It explains how to invoke the
scaffold tool, what each lifecycle status requires, and what the tool
will refuse to do. It does not add a product, does not add a catalog
entry, does not add a build-matrix entry, does not generate firmware,
and does not promote anything to `production`.

The scaffold tool itself is documented inline at the top of
[`scripts/scaffold_product.py`](../scripts/scaffold_product.py).

## What the tool does

On a single invocation, the tool:

1. Parses a WebFlash config string against
   [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
   (mounting / power / modules / forbidden tokens / mutual-exclusion
   rules / fan-driver "max one of" / FanDAC↔AirIQ conflict).
2. Cross-references the proposed config string against the existing
   [`config/product-catalog.json`](../config/product-catalog.json) and
   [`config/webflash-builds.json`](../config/webflash-builds.json) to
   detect duplicates.
3. Validates every `--hardware slot=SKU` against
   [`config/hardware-catalog.json`](../config/hardware-catalog.json).
4. Reads the canonical artifact name from
   [`scripts/product_name_mapper.py`](../scripts/product_name_mapper.py)
   (read-only import). When `--version` and `--channel` are supplied,
   the report shows the derived artifact filename so a maintainer can
   compare it against what they intend to declare.
5. Enforces per-status lifecycle rules
   (see [Allowed statuses](#allowed-statuses)).
6. Refuses to scaffold `production`, `deprecated`, `removed`, or
   `legacy-compatible`. Production is reached via the gates documented
   in [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md),
   not by a scaffold.
7. Enforces the FanTRIAC HW-005 policy: any config string containing
   `FanTRIAC` is forced to `--status blocked --blocker HW-005`. The
   tool will not scaffold a FanTRIAC-bearing entry at any other status.
8. Emits a Markdown report to stdout with proposed JSON snippets and
   a human review checklist. The script never writes any file.

## What the tool does NOT do

- It does **not** write to `config/product-catalog.json`,
  `config/webflash-builds.json`,
  `config/webflash-compatibility.json`, or
  `config/hardware-catalog.json`.
- It does **not** create or modify any product YAML under
  `products/` or any WebFlash wrapper under `products/webflash/`.
- It does **not** edit
  [`scripts/product_name_mapper.py`](../scripts/product_name_mapper.py)
  or
  [`scripts/validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py).
- It does **not** edit any package, workflow, component, header, or
  test.
- It does **not** generate firmware, create GitHub Releases, draft
  release notes, or import anything into WebFlash.
- It does **not** scaffold a `production` entry. Production is reached
  via the preview-to-stable promotion gates.
- It does **not** unblock FanTRIAC. The HW-005 blocker stays open.
- It does **not** change the Release-One product
  (`Ceiling-POE-VentIQ-RoomIQ` on `stable`).
- It does **not** change the LED preview catalog entry
  (`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`,
  `channel: preview`).
- It does **not** change the mains-voltage compliance status for
  `S360-400` or `S360-320`.

## Allowed statuses

| Status | Required flags | Notes |
|---|---|---|
| `compile-only` | `--config-string`, `--status`, `--product-yaml`, `--hardware-status` | Compiles in CI but is not WebFlash-shippable. `--webflash-build-matrix` is rejected. |
| `hardware-pending` | `--config-string`, `--status`, `--product-yaml`, `--hardware-status`, `--missing-hardware-evidence` | Tracks an entry whose hardware evidence is still open. Not WebFlash-shippable. |
| `preview` | `--config-string`, `--status`, `--product-yaml`, `--hardware-status`, `--version`, `--channel` (non-`stable`) | If `--webflash-build-matrix` is supplied, additionally requires `--webflash-wrapper`, and the wrapper basename must equal the lower-cased `config_string`. Preview must not claim a `release_one_required_configs` slot. |
| `blocked` | `--config-string`, `--status`, `--product-yaml`, `--blocker`, `--reason` | `--webflash-build-matrix` is rejected. FanTRIAC scaffolds **must** use `--blocker HW-005`. |

Statuses **not** allowed: `production`, `deprecated`, `removed`,
`legacy-compatible`. The tool rejects them with an explanatory message.

## Example invocations

Compile-only scaffold for the LED-bearing sibling, with hardware
SKUs (does not match the live catalog because the live LED preview
entry is already at `status: preview`, so this would exit non-zero
against the real catalog — useful as a worked example only):

```bash
python3 scripts/scaffold_product.py \
  --config-string Ceiling-POE-VentIQ-RoomIQ-LED \
  --status compile-only \
  --product-yaml products/sense360-ceiling-poe-ventiq-roomiq-led.yaml \
  --hardware-status verified-led-candidate \
  --hardware core=S360-100 \
  --hardware ventiq=S360-211 \
  --hardware roomiq=S360-200 \
  --hardware poe=S360-410 \
  --hardware led=S360-300
```

Blocked scaffold for a FanTRIAC-bearing entry (forced to `blocked` /
`HW-005`):

```bash
python3 scripts/scaffold_product.py \
  --config-string Ceiling-POE-VentIQ-FanTRIAC-RoomIQ \
  --status blocked \
  --product-yaml products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml \
  --blocker HW-005 \
  --reason "S360-320 schematic uncommitted; ac_dimmer over SX1509 not viable."
```

Preview scaffold without a build-matrix entry (catalog-only):

```bash
python3 scripts/scaffold_product.py \
  --config-string Ceiling-POE-AirIQ \
  --status preview \
  --product-yaml products/sense360-ceiling-poe-airiq.yaml \
  --hardware-status verified-candidate \
  --version 0.1.0 \
  --channel preview \
  --hardware core=S360-100 \
  --hardware airiq=S360-210 \
  --hardware poe=S360-410
```

Preview scaffold with a build-matrix proposal (requires a wrapper
whose basename equals the lower-cased config string):

```bash
python3 scripts/scaffold_product.py \
  --config-string Ceiling-POE-AirIQ \
  --status preview \
  --product-yaml products/sense360-ceiling-poe-airiq.yaml \
  --webflash-wrapper products/webflash/ceiling-poe-airiq.yaml \
  --hardware-status verified-candidate \
  --version 0.1.0 \
  --channel preview \
  --webflash-build-matrix \
  --hardware core=S360-100 \
  --hardware airiq=S360-210 \
  --hardware poe=S360-410
```

## Report structure

The report is plain Markdown to stdout. Sections, in order:

```
# Product Scaffold Report
## Input
## Parsed config string
## Compatibility grammar check
## Existing repo state
## Hardware SKU check
## Proposed product-catalog entry
## Optional WebFlash build-matrix entry
## Required files
## Validation commands
## Human review checklist
## Do-not-change guardrails
## Next PR sequence
## Result
```

The "Proposed product-catalog entry" and "Optional WebFlash
build-matrix entry" sections include example JSON snippets. **Those
snippets are advisory only.** They are never written to disk and they
are not guaranteed to be a drop-in addition — a human reviewer must
verify each field against the live catalog before editing
`config/product-catalog.json` or `config/webflash-builds.json` by
hand.

## Exit codes

| Exit code | Meaning |
|---|---|
| `0` | Every validation passed. The report is advisory; no file was written. |
| `1` | One or more validation failures. The report lists the errors under `## Result`. |
| `2` | Fixture load failure (e.g. malformed JSON in an override path). |

## Where the scaffold fits in onboarding

1. Hardware evidence first (per
   [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md#decision-table)).
2. Mains-voltage compliance review if `S360-400` or `S360-320` is
   involved (per
   [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)).
3. **Run the scaffold tool to produce a checklist for the proposed
   entry.** Fix every reported error before opening a PR.
4. Add the product YAML and (if WebFlash-shippable) a wrapper.
5. Hand-edit
   [`config/product-catalog.json`](../config/product-catalog.json)
   in a separate PR. Run
   [`scripts/validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py).
6. For `preview` entries that will land in the build matrix:
   hand-edit
   [`config/webflash-builds.json`](../config/webflash-builds.json).
7. Production promotion is a separate process; see
   [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md).

## Tests and validation

The scaffold tool is tested by
[`tests/test_scaffold_product.py`](../tests/test_scaffold_product.py)
under stdlib `unittest`. The suite covers grammar errors, duplicate
detection, unknown hardware SKUs, production rejection, preview
stable-channel rejection, preview build-matrix-without-wrapper
rejection, the FanTRIAC HW-005 policy, hardware-pending evidence
requirement, the product-YAML path guard against `products/webflash/`,
and the read-only invariant (no fixture file is mutated by a run).

Run the suite with:

```bash
python3 tests/test_scaffold_product.py
```

After scaffolding a future product entry by hand, run the full
validation surface listed in
[`docs/product-onboarding.md`](product-onboarding.md#commands-to-run)
before opening a PR.

## See also

- [`docs/product-onboarding.md`](product-onboarding.md) — PRODUCT-004
  ordered onboarding sequence.
- [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
  — RELEASE-006 promotion gates. Production is reached via these
  gates, not via a scaffold.
- [`docs/product-led-preview-decision.md`](product-led-preview-decision.md)
  — PRODUCT-005 worked example of a preview product path (Sense360 LED).
- [`docs/webflash-contract.md`](webflash-contract.md) — canonical
  WebFlash artifact / grammar / token contract.
- [`scripts/validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py)
  — PRODUCT-003 read-only cross-file catalog validator. The scaffold
  tool complements this validator: the scaffold tool runs *before*
  editing the catalog; the validator runs *after*.
- [`docs/cleanup-audit.md`](cleanup-audit.md) — classification of
  stale / current / blocked-reference / legacy-compatible repo
  content; carries PRODUCT-010 entries.

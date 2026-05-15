# Product Deprecation and Removal Policy (PRODUCT-DEP-001)

## Purpose and scope

This document is the canonical, cross-cutting policy for **deprecating**
and **removing** Sense360 product configurations from this repository's
WebFlash track. It defines what each lifecycle state means, what
metadata is required, what gates must clear before a product moves
into `deprecated` or `removed`, and what implications that move has
for the product catalog, the WebFlash build matrix, GitHub Release
artifacts, release notes, and the downstream WebFlash surfaces
(manifest, `firmware/sources.json`, `REQUIRED_CONFIGS`, kits).

This document is **documentation only**. PRODUCT-DEP-001 — this PR —
does not:

- deprecate or remove any product,
- change any product's lifecycle status,
- modify any entry in
  [`config/product-catalog.json`](../config/product-catalog.json),
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
  or [`config/hardware-catalog.json`](../config/hardware-catalog.json),
- modify any product YAML under [`products/`](../products/), any
  WebFlash wrapper under [`products/webflash/`](../products/webflash/),
  or any package YAML under [`packages/`](../packages/),
- modify any workflow under `.github/workflows/`, any script under
  [`scripts/`](../scripts/), any test under [`tests/`](../tests/),
  any component under `components/`, or any include under `include/`,
- generate, regenerate, sign, import, deploy, or otherwise produce
  firmware,
- change the Release-One product `Ceiling-POE-VentIQ-RoomIQ`, its
  artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, or
  its tag `v1.0.0`,
- change the LED preview entry `Ceiling-POE-VentIQ-RoomIQ-LED` (stays
  `status: preview`, `channel: preview`),
- unblock FanTRIAC (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays
  `status: blocked`, `blocker: HW-005`,
  `webflash_build_matrix: false`),
- add, remove, or modify any entry in WebFlash-side
  `REQUIRED_CONFIGS`, `scripts/data/kits.json`,
  `firmware/sources.json`, or `manifest.json` — those are
  WebFlash-owned and are not touched by this repo.

The intended audience is maintainers preparing a future deprecation
or removal PR, reviewers asked to sign off on a deprecation, and
operators answering "why is this product still listed?" or "why did
this product disappear?".

If this document and any source-of-truth document drift, **the
source-of-truth document wins** and this document must be updated.
The sources of truth are listed in [See also](#see-also).

## Lifecycle definitions

[`config/product-catalog.json`](../config/product-catalog.json)
declares eight lifecycle statuses. Every catalog entry carries exactly
one. The short form is in
[`docs/product-onboarding.md` Product lifecycle states](product-onboarding.md#product-lifecycle-states);
the long-form definition for each, with deprecation-relevant
distinctions, is below.

### `production`

Stable, customer-default WebFlash product surface. Appears in the
WebFlash build matrix, has an `artifact_name`, has a
`webflash_wrapper`, has verified-for-its-release hardware status,
and (when selected by a deliberate WebFlash decision) may appear in
`REQUIRED_CONFIGS` or in a kit. Release-One
(`Ceiling-POE-VentIQ-RoomIQ`) is the only `production` entry today.

### `preview`

Non-stable WebFlash product surface. May appear in the WebFlash
build matrix and the WebFlash manifest on a non-`stable` channel.
Must **not** appear in `REQUIRED_CONFIGS`. Kit exposure for a
preview product requires a separate, deliberate UX / product
decision (see [Kit policy](#kit-policy)). Today only
`Ceiling-POE-VentIQ-RoomIQ-LED` is `preview`.

### `compile-only`

YAML exists and compiles in CI, but the entry is not WebFlash
import / build eligible. Used during early bring-up before a
preview promotion. `webflash_build_matrix: false`. No `artifact_name`,
no `webflash_wrapper`.

### `hardware-pending`

YAML / config exists but required hardware evidence
(schematic, per-board reference doc, firmware-package mapping) is
incomplete. Not WebFlash import / build eligible.
`webflash_build_matrix: false`. No `artifact_name`, no
`webflash_wrapper`. Distinct from `blocked`: `hardware-pending` means
evidence is missing, not that there is a specific known blocker.

### `blocked`

Known blocker prevents this product from being shipped or exposed.
Must carry a `blocker` ID (e.g. `HW-005`) and a written `reason`.
Must **not** appear in `config/webflash-builds.json`, in any
manifest, in `REQUIRED_CONFIGS`, or in a kit.
`webflash_build_matrix: false`. The canonical example is
`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`, blocked under HW-005. Distinct
from `deprecated`: `blocked` means "never shipped through WebFlash —
held back by an open blocker"; `deprecated` means "previously
shipped through WebFlash, now phasing out."

### `legacy-compatible`

Historical / pre-WebFlash product YAML retained for compatibility,
migration, or manual / remote-package users. **Never** an active
WebFlash product surface. Has no `config_string`, no `artifact_name`,
no `webflash_wrapper`, and `webflash_build_matrix: false`. Must not
appear in the WebFlash build matrix, the WebFlash manifest,
`REQUIRED_CONFIGS`, or kits. The 30 `sense360-core-*` /
`sense360-mini-*` / `sense360-poe` / `sense360-fan-pwm` entries are
`legacy-compatible` today. Distinct from `deprecated`:
`legacy-compatible` entries **were never WebFlash-shippable**;
`deprecated` entries **were WebFlash-shippable and are being phased
out of WebFlash**.

### `deprecated`

Previously WebFlash-shippable product (or, by exception, a
shippable-eligible product that is being permanently withdrawn
before first stable release) that remains documented for migration
or diagnostic continuity but should not be newly imported, newly
manifested, or newly added to a kit. Must carry
`deprecation_reason`, `deprecated_since`, and either
`replacement_config_string` or `no_replacement_reason`. Must also
carry a `removal_target` (target version / date) or
`removal_criteria` (conditions that, once met, escalate the entry
to `removed`). Default `webflash_build_matrix: false`; a temporary
exception requires a written rationale in `notes`. See
[Required metadata for deprecation](#required-metadata-for-deprecation)
and [Deprecation gates](#deprecation-gates).

### `removed`

No longer an active product surface. The catalog row remains as a
**tombstone** so the `config_string` is reserved, history is
queryable, and the entry cannot be silently re-introduced. The
underlying product YAML / WebFlash wrapper / build-matrix entry /
manifest entry / `REQUIRED_CONFIGS` membership / kit membership are
all absent. Must carry `removed_since`, `removal_reason`, and
either `replacement_config_string` or `no_replacement_reason`.
`webflash_build_matrix: false`. See
[Required metadata for removal](#required-metadata-for-removal) and
[Removal gates](#removal-gates). Tombstone retention is the
default; deletion of the tombstone row itself is only allowed if a
future PR records an explicit justification (see
[Tombstone retention](#tombstone-retention)).

## State transition model

Allowed transitions:

```text
compile-only       -> preview
hardware-pending   -> preview
preview            -> production
preview            -> deprecated
production         -> deprecated
deprecated         -> removed
legacy-compatible  -> removed       (intentional retirement only)
blocked            -> hardware-pending
blocked            -> preview        (only after the blocker is resolved)
```

Rejected or strongly discouraged transitions:

```text
blocked            -> production                  (must clear the blocker, then promote via the standard gates)
legacy-compatible  -> production                  (would require full onboarding; legacy entries are not WebFlash-shippable)
legacy-compatible  -> preview                     (use a new catalog entry; legacy ID and WebFlash config_string namespaces are disjoint)
deprecated         -> production                  (requires explicit reactivation review; not a routine transition)
removed            -> production                  (requires a fresh onboarding PR with a new catalog entry — the tombstone is not "un-removed")
deprecated         -> preview                     (allowed only by explicit reactivation review)
removed            -> deprecated / preview / production   (a removed entry is permanent; reactivation uses a new catalog row)
```

Reactivation. A `deprecated` entry may be returned to `production`
only via a deliberate reactivation review that re-runs every gate in
[`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
(hardware evidence, compliance, operator-proof, release notes,
build proof, etc.). Reactivation is not a side effect of cleanup
PRs.

## Deprecated vs removed vs blocked vs legacy-compatible

| Dimension | `blocked` | `legacy-compatible` | `deprecated` | `removed` |
|---|---|---|---|---|
| Was ever WebFlash-shippable? | No (held by blocker) | No (pre-WebFlash) | Yes (or eligible & withdrawn) | Yes (previously) |
| Has a `config_string`? | Yes | No | Yes | Yes (reserved by tombstone) |
| In WebFlash build matrix? | No | No | No (default; exception requires rationale) | No |
| In WebFlash manifest? | No | No | Existing entries may remain temporarily with deprecation copy + removal plan; never newly added | No |
| Import-eligible (new imports)? | No | No | No | No |
| Allowed in `REQUIRED_CONFIGS`? | No | No | No | No |
| Allowed in kits? | No | No | No | No |
| Required metadata | `blocker`, `reason` | none beyond catalog defaults | `deprecation_reason`, `deprecated_since`, replacement info, removal target/criteria | `removed_since`, `removal_reason`, replacement info |
| Catalog row retained? | Yes | Yes | Yes | Yes (tombstone) |
| Release-notes generator behaviour | Refused | Refused | Refused | Refused |

The four states are **not** interchangeable. Use the smallest applicable
distinction:

- "We can't ship this because a specific blocker is open." → `blocked`.
- "This was never a WebFlash product; we keep the YAML for manual
  users." → `legacy-compatible`.
- "We shipped this through WebFlash and are winding it down." →
  `deprecated`.
- "It's gone. The config string is now reserved by a tombstone row." →
  `removed`.

## Required metadata

The field names below are **policy / future schema** fields. The
current catalog schema does not enforce them. The validator updates
that would enforce them are listed under
[Test requirements](#test-requirements) as a future follow-up. This
document does **not** edit the validators in this PR.

### Required metadata for deprecation

A `deprecated` entry must carry the following:

- `status: deprecated`
- `deprecation_reason` — one to three sentences explaining why this
  product is being deprecated. References to upstream tickets,
  hardware audits, or compliance decisions are acceptable.
- `deprecated_since` — the version or ISO-8601 date at which the
  product moved to `deprecated`. If a release tag exists for the
  last shipped build, that tag is the preferred value.
- One of:
  - `replacement_config_string` — the canonical WebFlash
    `config_string` of the product that users should migrate to;
    must itself be `production` (or `preview` if the deprecation
    is itself a preview rollback); **or**
  - `no_replacement_reason` — written rationale explaining why
    there is intentionally no replacement (e.g. the use case is
    permanently retired). Implicit "no replacement" is not allowed.
- One of:
  - `removal_target` — the version or ISO-8601 date at which the
    deprecated entry is expected to be escalated to `removed`; or
  - `removal_criteria` — written conditions that, once met, will
    trigger removal (e.g. "all downstream kits referencing this
    config have been retired", "WebFlash manifest no longer
    contains this config for two consecutive deploys").
- `webflash_build_matrix: false`. A temporary exception (existing
  manifest entry retained for one release cycle to give customers
  time to migrate) must record:
  - the reason for the exception in `notes`, and
  - the version / date at which the exception ends.
- `notes` describing the migration path, the impact on existing
  installations, and any caveats reviewers should know about.

A `deprecated` entry must **not** carry:

- `artifact_name` — the deprecation marks the product as not building
  new artifacts. If a final last-available artifact exists, it is
  recorded in `notes`, not as the live `artifact_name` value.

### Required metadata for removal

A `removed` entry must carry the following:

- `status: removed`
- `removed_since` — the version or ISO-8601 date at which the
  product moved to `removed`.
- `removal_reason` — one to three sentences explaining why removal
  happened, including a reference to the prior `deprecation_reason`
  if applicable.
- One of `replacement_config_string` or `no_replacement_reason`,
  carried forward from the prior `deprecated` row.
- `webflash_build_matrix: false`.
- `notes` recording the last available version (if any), the
  expected last-deploy date on WebFlash, and any historical context
  needed to understand why the config string is reserved.

A `removed` entry must **not** carry:

- `artifact_name`
- `webflash_wrapper`
- `version` / `channel` of a current build
- a `product_yaml` path that still resolves to an active YAML file,
  unless the YAML is retained intentionally as `legacy-compatible`
  (in which case the `removed` tombstone row references the
  archival relationship explicitly in `notes`)

### Tombstone retention

The default for `removed` entries is **keep the catalog row** so:

- the `config_string` is reserved and cannot be silently re-used,
- history (who removed it, when, why, what the replacement was) is
  queryable from the catalog,
- downstream tooling (release-notes generator, scaffold tool,
  consistency validator) sees the removal and refuses to scaffold,
  ship, or release-note the same config under a different shape.

Deletion of a tombstone row is only allowed if a future PR records
an explicit justification (for example: the `config_string` was
never publicly released and the tombstone is creating ambiguity for
a new product). Deletion is **not** a routine cleanup operation.

## Deprecation gates

Before any product is moved to `status: deprecated`, the following
must be true. Each row is a gate; do not advance until the gate
passes. None of these gates is performed by PRODUCT-DEP-001.

- **Reason recorded.** A `deprecation_reason` exists and references
  the originating decision (hardware audit, compliance review,
  product strategy, security advisory, etc.). One-word reasons are
  not acceptable.
- **Replacement decided.** Either a `replacement_config_string`
  resolves to a `production` (or, for a preview-stage rollback, a
  `preview`) catalog entry, or a written `no_replacement_reason`
  is recorded.
- **Removal trajectory recorded.** Either a `removal_target` (a
  specific version / date) or a `removal_criteria` (conditions that
  will trigger escalation to `removed`).
- **Migration path documented.** Either inline in `notes`, or in a
  dedicated subsection of this policy doc if substantial (token
  swap, schema change, etc.). Customers must be able to find the
  migration path from the release notes for the next release.
- **WebFlash implications acknowledged.** See
  [WebFlash implications](#webflash-implications). Any temporary
  build-matrix or manifest exception is named, dated, and bounded.
- **REQUIRED_CONFIGS check.** The `config_string` is not in
  WebFlash's `REQUIRED_CONFIGS`, or a separate WebFlash PR is
  planned to remove it before this deprecation lands.
- **Kit check.** The `config_string` is not referenced from a
  WebFlash kit, or a separate WebFlash PR is planned to remove it.
- **Tests pass.** The standard validation surface (see
  [Test requirements](#test-requirements)) passes both before and
  after the catalog edit.
- **Human approval.** A named maintainer has reviewed the gate
  evidence and approved the deprecation. The release engineer is a
  separate signatory only if the deprecation affects an active
  release artifact.

## Removal gates

Before any deprecated product is escalated to `status: removed`,
the following must be true. None of these gates is performed by
PRODUCT-DEP-001.

- **Deprecation interval elapsed.** The entry has been
  `deprecated` for at least the `removal_target` window, or its
  `removal_criteria` have been met. Same-PR deprecate-and-remove
  is rejected.
- **No active manifest exposure.** WebFlash's `manifest.json` no
  longer surfaces the deprecated build for at least one full deploy
  cycle, confirmed against the WebFlash repo's deploy history.
- **No REQUIRED_CONFIGS reference.** WebFlash's
  `__tests__/manifest-required-configs.test.js` does not list this
  `config_string`.
- **No kit reference.** WebFlash's `scripts/data/kits.json` does
  not list this `config_string`.
- **No firmware/sources entry.** WebFlash's `firmware/sources.json`
  does not list this `config_string`.
- **Replacement is live.** If a `replacement_config_string` was
  recorded, the replacement is `production` on `stable` (or, for
  preview-stage rollback, the replacement is at least `preview` on
  a non-`stable` channel) at the time of removal.
- **Tombstone metadata complete.** Every field in
  [Required metadata for removal](#required-metadata-for-removal)
  is populated.
- **Release-note signposting prepared.** The next release's
  `## Changelog` for the **replacement** build (or, if no
  replacement, the next stable build of any related product) calls
  out the removal explicitly. The release-notes generator already
  refuses to draft a body for a `removed` entry, so the call-out
  lives on a different build's body.
- **Human approval.** A named maintainer has reviewed the gate
  evidence and approved the removal.

## WebFlash implications

The WebFlash repo is the customer-facing flasher; this repo
produces the unsigned `.bin` and the GitHub Release body, and
WebFlash signs, manifests, and deploys. The deprecation / removal
implications below describe what each state means on the WebFlash
side. No changes to any WebFlash file land in PRODUCT-DEP-001.

### Deprecated

- **Build matrix.** Default
  [`config/webflash-builds.json`](../config/webflash-builds.json)
  entry is absent. The deprecation PR removes the build-matrix
  entry as part of the same change unless a temporary exception is
  documented.
- **Manifest / firmware-N.json.** No new manifest entries are added
  for a deprecated build. If an entry already exists, WebFlash may
  keep it for one release cycle to support migration, with
  deprecation copy in the UI. A separate WebFlash PR removes the
  manifest entry by the `removal_target`.
- **`firmware/sources.json`.** No new sources are added for a
  deprecated build. Existing sources are pruned as part of the
  removal step, not the deprecation step.
- **REQUIRED_CONFIGS.** Deprecated configs are **never** allowed in
  `REQUIRED_CONFIGS`. If a deprecation targets a config that is
  currently in `REQUIRED_CONFIGS`, the WebFlash repo must remove the
  membership before (or atomically with) this repo's deprecation
  PR. A deprecation cannot land while
  `REQUIRED_CONFIGS` still references the config.
- **Kits.** Deprecated configs are **never** allowed in kits. Same
  ordering rule as REQUIRED_CONFIGS.
- **Import.** WebFlash's import pipeline
  (`scripts/sync-from-releases.py` + `scripts/gen-manifests.py`)
  should reject deprecated catalog entries as a new import. See
  [Test requirements](#test-requirements) for the future WebFlash
  follow-up.
- **UI copy.** Deprecated entries that remain temporarily in the
  manifest must show migration copy pointing at the replacement
  build, sourced from the
  [Migration / replacement guidance](#migration--replacement-guidance)
  section of this doc.

### Removed

- **Build matrix.** Absent.
- **Manifest / firmware-N.json.** Absent.
- **`firmware/sources.json`.** Absent.
- **REQUIRED_CONFIGS.** Absent.
- **Kits.** Absent.
- **GitHub Releases.** Existing release artifacts for the removed
  config are not republished and not back-edited. URLs may
  eventually 404 after WebFlash's cache expires (`Cache-Control:
  max-age=31536000`), unless deliberately retained in an archive
  release per WebFlash's archival policy.
- **No new release artifacts.** A `removed` entry never builds a
  new `.bin`; the WebFlash build matrix entry is absent and the
  release-notes generator refuses to draft a body for it.

### Blocked (re-stated for contrast)

- Never imported. Never manifested. Never in `REQUIRED_CONFIGS`.
  Never in a kit. The FanTRIAC entry under HW-005 is the canonical
  example.

### Legacy-compatible (re-stated for contrast)

- Retained for manual / remote-package users. May remain in the
  upstream product catalog with `webflash_build_matrix: false`,
  no `config_string`, no `artifact_name`, no `webflash_wrapper`.
  Must not leak into any WebFlash active surface.

## REQUIRED_CONFIGS policy

[`docs/preview-to-stable-promotion-gates.md` REQUIRED_CONFIGS policy](preview-to-stable-promotion-gates.md#required_configs-policy)
defines `REQUIRED_CONFIGS` as a WebFlash baseline-health invariant:
the list of WebFlash config strings whose presence in the deployed
`manifest.json` is enforced by
`__tests__/manifest-required-configs.test.js`.

`deprecated` and `removed` entries are **never** eligible for
`REQUIRED_CONFIGS`. If a config that is currently in
`REQUIRED_CONFIGS` is about to be deprecated, the WebFlash repo
must remove the `REQUIRED_CONFIGS` membership before (or atomically
with) this repo's deprecation PR.

The default for any newly-stable build is "not in REQUIRED_CONFIGS
until a deliberate WebFlash decision is recorded." The default for
any deprecated or removed build is **"definitely not in
REQUIRED_CONFIGS"** — this is an invariant, not a default.

## Kit policy

[`docs/preview-to-stable-promotion-gates.md` Kit policy](preview-to-stable-promotion-gates.md#kit-policy)
defines a "kit" as a WebFlash `scripts/data/kits.json` entry that
surfaces a recommended SKU bundle in the installer wizard.

`deprecated` and `removed` entries are **never** eligible for kits.
If a config currently referenced by a kit is about to be
deprecated, the WebFlash repo must remove the kit reference before
(or atomically with) this repo's deprecation PR. A deprecated
build appearing in a recommended-kit slot is a defect, not a
default.

## Catalog and build-matrix implications

| Surface | `deprecated` | `removed` |
|---|---|---|
| [`config/product-catalog.json`](../config/product-catalog.json) entry | Retained, with deprecation metadata. | Retained as tombstone, with removal metadata. Deletion only on explicit justification. |
| `config_string` reservation | Yes | Yes (the tombstone reserves the string). |
| `webflash_build_matrix` | `false` (temporary exception requires rationale + bounded date). | `false`. |
| [`config/webflash-builds.json`](../config/webflash-builds.json) entry | Absent (removed as part of the deprecation PR). | Absent. |
| `artifact_name` | Absent. Last-shipped artifact, if any, recorded in `notes`. | Absent. Final artifact, if any, recorded in `notes`. |
| `webflash_wrapper` | Optional; preferred absent. If retained for diagnostic reasons, the rationale is in `notes`. | Absent. |
| `product_yaml` | May be retained for manual users; the catalog row makes the deprecation explicit. | Absent, unless retained as a `legacy-compatible` archival row (the tombstone references the archive relationship). |
| Hardware SKU map | May be retained for historical reference. | Optional; default to omit. |
| `modules` map | May be retained for historical reference. | Optional; default to omit. |
| `blocked_modules` | Retained. | Optional; default to omit. |

## Release-note requirements

The release-notes generator
[`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py)
already refuses to draft a body for a `deprecated` or `removed`
catalog entry (`REFUSED_STATUSES`). That refusal is intentional and
must remain.

Deprecation / removal call-outs therefore land in the release notes
of a **different** build — typically the replacement build's next
release, or, if there is no replacement, the next stable build of a
related product. The wording rules:

- **On deprecation.** The replacement build's `## Changelog`
  bullet for the release that lands the deprecation must call the
  deprecation out by name, link to the migration path, and name the
  `removal_target` or `removal_criteria`. Example wording:
  "Deprecates `<config_string>`; migrate to
  `<replacement_config_string>` by `<removal_target>`. See
  [`docs/product-deprecation-removal-policy.md`](product-deprecation-removal-policy.md)."
- **On removal.** The next stable build's `## Changelog` for any
  product affected by the removal must record:
  - the removed `config_string`,
  - the `removed_since` value,
  - the last available version (if any),
  - the replacement (if any).
  Example wording: "Removes `<config_string>` (last available:
  `<last_version>`). Migrate to `<replacement_config_string>` or
  see migration notes."
- **No new artifacts.** A `deprecated` or `removed` entry does not
  receive a new release artifact. The
  [`Build & Release Firmware`](../.github/workflows/firmware-build-release.yml)
  workflow only builds the WebFlash build matrix, from which
  deprecated and removed entries are absent.

## Migration / replacement guidance

Every deprecation must produce one of two artifacts:

1. **A named replacement.** If the deprecation has a replacement,
   the `replacement_config_string` field points at the replacement
   catalog entry, and the `notes` field on the deprecated row
   summarises:
   - what the user needs to change in their installation (token
     swap, hardware swap, manifest re-flash, etc.),
   - whether the replacement is `production` on `stable` or
     `preview` on a non-`stable` channel,
   - any operator caveats (e.g. "the replacement reuses the same
     hardware SKU map; no kit change required").
2. **A documented absence.** If the deprecation has **no**
   replacement, the `no_replacement_reason` field records the
   written rationale, and the `notes` field summarises:
   - whether installations are expected to migrate to a different
     product family, a manual / legacy-compatible YAML, or to be
     retired,
   - whether the WebFlash UI should surface a "no replacement
     planned" message.

If the migration is substantial (config-string token swap, schema
change, breaking entity-naming change, mains-voltage compliance
change, etc.), this policy doc gains a new subsection under
[Migration / replacement guidance](#migration--replacement-guidance)
in the same PR that lands the deprecation, named for the
deprecated `config_string`. Customer-visible release notes link to
that subsection.

There are no migration subsections today because no product is
deprecated.

## Test requirements

The tests below already enforce parts of this policy. None of them
is added or modified by PRODUCT-DEP-001; they are listed so future
deprecation / removal PRs know exactly which surface a status flip
must clear, and so future enforcement work (also listed) has a
named target.

### Today's enforcement (already green)

- [`tests/test_product_catalog.py`](../tests/test_product_catalog.py)
  — accepts `deprecated` and `removed` in `EXPECTED_LIFECYCLE_STATUSES`;
  enforces `webflash_build_matrix=false` for every non-`production` /
  non-`preview` status via
  `test_non_eligible_statuses_have_webflash_build_matrix_false`.
- [`tests/test_product_catalog_consistency.py`](../tests/test_product_catalog_consistency.py)
  — unit tests for the read-only consistency validator. Locks in
  that the current repo passes `validate_all()` with zero errors.
- [`scripts/validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py)
  — accepts `deprecated` and `removed` in
  `EXPECTED_LIFECYCLE_STATUSES`; rejects them from
  `WEBFLASH_ELIGIBLE_STATUSES` (only `production` and `preview`).
- [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py)
  — validates the WebFlash build matrix against
  `config/webflash-compatibility.json`. A deprecated or removed
  catalog entry that erroneously appears in the build matrix would
  fail the existing cross-check in `test_product_catalog.py`.
- [`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py)
  — `REFUSED_STATUSES` includes `deprecated` and `removed`; the
  generator will not draft a body for either.
- [`scripts/scaffold_product.py`](../scripts/scaffold_product.py)
  — `REJECTED_STATUSES` includes `deprecated` and `removed`; the
  scaffold tool will not scaffold either.

### Recommended future enforcement (not added by PRODUCT-DEP-001)

These are recorded as a backlog. They are **not** added in this PR
because PRODUCT-DEP-001 is documentation only. A future scoped PR
should add them when the first real deprecation lands, so the
required-metadata fields are populated against a concrete row
rather than hypothetically:

- Add `_validate_deprecated` to
  [`scripts/validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py)
  to require `deprecation_reason`, `deprecated_since`, exactly one
  of `replacement_config_string` / `no_replacement_reason`,
  exactly one of `removal_target` / `removal_criteria`, and
  `webflash_build_matrix: false` (with an opt-out path for an
  explicit, dated exception).
- Add `_validate_removed` to the same script to require
  `removed_since`, `removal_reason`, exactly one of
  `replacement_config_string` / `no_replacement_reason`,
  `webflash_build_matrix: false`, no `artifact_name`, no
  `webflash_wrapper`, and absence from the WebFlash build matrix.
- Extend
  [`tests/test_product_catalog.py`](../tests/test_product_catalog.py)
  with parallel `test_deprecated_entries_have_required_fields` and
  `test_removed_entries_have_required_fields` cases.
- Extend
  [`tests/test_product_catalog_consistency.py`](../tests/test_product_catalog_consistency.py)
  with negative fixtures (an entry missing
  `deprecation_reason` should fail; an entry with both
  `replacement_config_string` and `no_replacement_reason` should
  fail; etc.).
- Update
  [`scripts/scaffold_product.py`](../scripts/scaffold_product.py)
  to print a pointer to this policy doc when refusing a
  `deprecated` / `removed` scaffold request.
- WebFlash repo follow-up: extend
  `sense360store/WebFlash:scripts/validate-product-import-readiness.js`
  to reject `deprecated` / `removed` catalog entries as import
  sources, with a dedicated error message pointing at this policy.
- WebFlash repo follow-up: extend manifest-health /
  github-pages-surface / product-catalog-alignment tests to flag
  any manifest / kit / `REQUIRED_CONFIGS` membership that
  references a `deprecated` or `removed` config string.

## Current repo status

A snapshot of repository state at the time PRODUCT-DEP-001 landed.
This section records that **no product is deprecated or removed by
this PR**.

| Catalog entry | Status today | Action by PRODUCT-DEP-001 |
|---|---|---|
| `Ceiling-POE-VentIQ-RoomIQ` (Release-One) | `production` | None. Release-One stays `production` on `stable`. |
| `Ceiling-POE-VentIQ-RoomIQ-LED` (LED preview) | `preview` | None. LED stays `preview` on `preview` channel. |
| `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` (FanTRIAC) | `blocked` (HW-005) | None. FanTRIAC stays `blocked` under HW-005. |
| All `legacy-compatible` entries (`sense360-core-*`, `sense360-mini-*`, `sense360-poe`, `sense360-fan-pwm`) | `legacy-compatible` | None. Stay `legacy-compatible`. |
| Any other entry | n/a | None. |

No `deprecated` row exists today. No `removed` row exists today.

## Do-not-change guardrails

PRODUCT-DEP-001 — this document — performs **none** of the
following. Anyone reading this document looking for justification
to change one of them must use a separate, scoped PR with its own
gate evidence (see [Deprecation gates](#deprecation-gates),
[Removal gates](#removal-gates), and the
[Follow-up PR sequence](#follow-up-pr-sequence)).

- No edits to
  [`config/product-catalog.json`](../config/product-catalog.json),
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
  or [`config/hardware-catalog.json`](../config/hardware-catalog.json).
- No edits to any product YAML under
  [`products/`](../products/) or any WebFlash wrapper under
  [`products/webflash/`](../products/webflash/).
- No edits to any package YAML under [`packages/`](../packages/).
- No edits to any workflow under `.github/workflows/`, any script
  under [`scripts/`](../scripts/), any test under
  [`tests/`](../tests/), any component under `components/`, or any
  include under `include/`.
- No firmware build, no firmware regeneration, no GitHub Release
  tag, no asset upload, no WebFlash import, no manifest
  regeneration, no signing.
- No edits to the Release-One product, the Release-One config
  string `Ceiling-POE-VentIQ-RoomIQ`, the Release-One artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, or the
  Release-One tag `v1.0.0`.
- No change to the LED preview catalog entry. LED stays `status:
  preview`, `channel: preview`.
- No unblock of FanTRIAC. The HW-005 blocker stays open. The
  FanTRIAC entry stays `status: blocked`,
  `webflash_build_matrix: false`.
- No edits to WebFlash-side `REQUIRED_CONFIGS`,
  `scripts/data/kits.json`, `firmware/sources.json`,
  `manifest.json`, or any test under WebFlash's `__tests__/`.
  PRODUCT-DEP-001 lives entirely in this repo's `docs/`.
- No deprecation of any product. No removal of any product. No
  lifecycle status flip in any catalog entry.
- No new tests. No script changes. No workflow changes.

## Follow-up PR sequence

When a future maintainer is ready to deprecate or remove a product,
the safe path below is a sequence of scoped PRs. Each step is its
own PR with its own evidence. Steps in this repo and steps in
WebFlash interleave; the dependency arrows are real.

1. **WebFlash REQUIRED_CONFIGS / kit cleanup PRs** (WebFlash repo,
   only if the config is currently referenced).
   Remove any `REQUIRED_CONFIGS` membership and any
   `scripts/data/kits.json` reference for the target
   `config_string`. Land **before** the deprecation in this repo so
   the catalog flip never coexists with a stale WebFlash reference.
2. **Deprecation PR** (this repo).
   Edit
   [`config/product-catalog.json`](../config/product-catalog.json)
   to set `status: deprecated`, populate every field required by
   [Required metadata for deprecation](#required-metadata-for-deprecation),
   and remove the entry from
   [`config/webflash-builds.json`](../config/webflash-builds.json)
   unless an explicit, dated exception is recorded. Update this
   policy doc with a new
   [Migration / replacement guidance](#migration--replacement-guidance)
   subsection if the migration is substantial. The next replacement
   build's release notes call out the deprecation per
   [Release-note requirements](#release-note-requirements). Validators
   listed in [Test requirements](#test-requirements) must pass.
3. **Validator / scaffold update PR** (this repo, only when the
   first real deprecation lands).
   Add `_validate_deprecated` / `_validate_removed` per the
   backlog in [Recommended future enforcement](#recommended-future-enforcement-not-added-by-product-dep-001).
   This PR is scoped to validator + tests only; no catalog edits.
4. **WebFlash deprecation copy / manifest cleanup PR** (WebFlash
   repo).
   If the deprecated build was previously manifested, update
   WebFlash UI copy to surface the migration path; or remove the
   manifest entry if no migration window is required. Update
   `firmware/sources.json` if the deprecation removes new imports.
5. **Removal PR** (this repo, when the `removal_target` /
   `removal_criteria` are met).
   Edit
   [`config/product-catalog.json`](../config/product-catalog.json)
   to flip the entry to `status: removed`, populate every field
   required by
   [Required metadata for removal](#required-metadata-for-removal),
   and remove `webflash_wrapper` / `product_yaml` references unless
   retained as an archival `legacy-compatible` relationship. The
   next stable build's release notes call out the removal per
   [Release-note requirements](#release-note-requirements).
6. **WebFlash final-cleanup PR** (WebFlash repo).
   Remove any remaining manifest / sources entries for the removed
   `config_string`. Confirm `__tests__/manifest-required-configs.test.js`
   and `__tests__/product-catalog-alignment.test.js` (or successors)
   stay green.
7. **(Optional) Tombstone deletion PR** (this repo).
   Only if a future maintainer records an explicit justification
   for deleting the `removed` tombstone row itself. Default:
   **skip**. See [Tombstone retention](#tombstone-retention).

FanTRIAC is **not** on this sequence. FanTRIAC stays `blocked`
under HW-005; deprecation / removal are separate from the blocked
state. Reactivation of a `deprecated` entry to `production` is also
not on this sequence; that path runs through
[`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md).

## See also

- [`README.md`](../README.md) — repo overview, Release-One quick
  reference, package reference.
- [`docs/product-onboarding.md`](product-onboarding.md) — PRODUCT-004
  ordered onboarding sequence; defines the eight lifecycle statuses
  in short form and orders the safe onboarding gates.
- [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
  — RELEASE-006 canonical preview-to-stable promotion gate
  document. Defines the opposite direction (preview → production)
  and is the source of truth for the REQUIRED_CONFIGS and kit
  policies inherited by this document.
- [`docs/product-scaffold-generator.md`](product-scaffold-generator.md)
  — PRODUCT-010 conservative product scaffold report generator. The
  scaffold tool already rejects `deprecated` / `removed` scaffolds;
  future scaffold updates point at this policy.
- [`docs/cleanup-audit.md`](cleanup-audit.md) — classification of
  stale / current / blocked-reference / legacy-compatible repo
  content. The "do-not-delete" list defends manual / public-API
  surfaces that are unrelated to WebFlash deprecation / removal.
- [`docs/release-one.md`](release-one.md) — Release-One
  configuration; the only `production` entry today.
- [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)
  — Release-One firmware-vs-schematic audit and FanTRIAC HW-005
  resolution.
- [`docs/webflash-contract.md`](webflash-contract.md) — canonical
  WebFlash artifact / grammar / token contract. The `Deprecated /
  forbidden tokens` section there is **token-level** (Bathroom →
  VentIQ, etc.) and is distinct from the **product-level**
  lifecycle states defined here.
- [`docs/webflash-release-handoff.md`](webflash-release-handoff.md)
  — operational source-to-installer flow. Notes the "build is
  marked deprecated" failure mode WebFlash can surface.
- [`docs/webflash-release-proof.md`](webflash-release-proof.md) —
  ESP-006 / ESP-007 release proof record. A deprecated or removed
  entry does not get a new proof row.
- [`scripts/validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py)
  — PRODUCT-003 read-only cross-file catalog validator. The future
  `_validate_deprecated` / `_validate_removed` rule blocks land
  here.
- [`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py)
  — RELEASE-001 release-notes draft generator. Already refuses
  `deprecated` / `removed` catalog entries via `REFUSED_STATUSES`.
- [`scripts/scaffold_product.py`](../scripts/scaffold_product.py)
  — PRODUCT-010 scaffold tool. Already refuses `deprecated` /
  `removed` via `REJECTED_STATUSES`.

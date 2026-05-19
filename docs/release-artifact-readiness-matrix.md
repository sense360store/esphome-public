# Release Artifact Readiness Matrix (RELEASE-GAP-001)

## Purpose and scope

This document is the canonical, **release-layer** readiness gate for
the candidate product families whose signed firmware artifacts,
release-channel choices, release notes, checksums, and operator-proof
records are not yet — and in most cases must not yet be — present in
this repo. It sits one layer downstream of the
[`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md)
WEBFLASH-GAP-001 gate, two layers downstream of the
[`docs/product-readiness-matrix.md`](product-readiness-matrix.md)
PRODUCT-GAP-001 gate, and three layers downstream of the
[`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
PACKAGE-GAP-001 gate. Where WEBFLASH-GAP-001 decides whether — and
how — a product YAML, once it exists, may be **exposed** through
WebFlash, this matrix decides whether — and how — a WebFlash-exposed
build, once it exists, may be **released as a signed firmware
artifact** through the existing
[`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)
flow, attached to a GitHub Release as a
`Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin` with
`checksums-sha256.txt`, `checksums-md5.txt`, and the build-info
`manifest.json`, validated against the artifact-naming /
release-notes / release-assets guards, and recorded in
[`docs/webflash-release-proof.md`](webflash-release-proof.md) for
WebFlash-side ingest.

RELEASE-GAP-001 exists because the upstream gates have already made
the release-layer answer clear and yet potentially confusing. Per
[`webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md),
every candidate family (FanRelay / FanPWM / FanDAC / FanTRIAC /
PWR-240V / PoE-410) carries `not-webflash-ready` today: no candidate
family has a WebFlash wrapper under [`products/webflash/`](../products/webflash/)
that this matrix could release. Per
[`product-readiness-matrix.md`](product-readiness-matrix.md), none of
the six candidate families carries `ready-for-product-yaml` today,
which is the upstream of WebFlash exposure. Per
[`hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md),
none of the six in-scope packages carries
`ready-for-package-change`. Per
[`hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md),
five of the six candidate boards carry `missing` or `partial`
hardware evidence and the sixth (`S360-320` TRIAC) is `blocked`
under HW-005 + COMPLIANCE-001. The downstream conclusion is
mechanical: no candidate family is eligible for any new release
artifact in this PR, no new GitHub Release is created or modified,
no firmware is built, no release notes are generated, no checksums
are recorded, and no WebFlash import is performed. This document
records that conclusion, classifies each candidate family against
the release-artifact axis, and names the per-family follow-up PRs
that would eventually take a family from "no release surface" to
either preview-artifact, advanced/manual-warning-artifact, or — only
after the full
[`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
17-row gauntlet — stable / production artifact.

This document is **documentation only**. It does **not**:

- build, sign, attach, regenerate, deploy, import, or otherwise
  produce any firmware artifact under any channel
  (`stable` / `beta` / `preview` / `dev` / `rescue`),
- create, update, retag, retitle, restamp, or modify any GitHub
  Release — the Release-One `v1.0.0` release with
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`,
  `checksums-sha256.txt`, `checksums-md5.txt`, and the build-info
  `manifest.json` stays verbatim; the LED preview prerelease
  `v1.0.0-led-preview` with
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` and
  matching checksums / build-info manifest (RELEASE-005) stays
  verbatim,
- edit any workflow under
  [`.github/workflows/`](../.github/workflows/) — neither the build
  / release flow
  [`firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)
  nor the release-notes drafter
  [`release-notes-draft.yml`](../.github/workflows/release-notes-draft.yml)
  nor the validate flow
  [`validate.yml`](../.github/workflows/validate.yml) nor the CI
  config-validation flow
  [`ci-validate-configs.yml`](../.github/workflows/ci-validate-configs.yml)
  changes,
- edit any release-time script under
  [`scripts/`](../scripts/) — neither the artifact-naming /
  version-channel deriver
  [`derive_release_version_channel.py`](../scripts/derive_release_version_channel.py),
  the release-notes generator
  [`generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py),
  the release-notes validator
  [`validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py),
  the release-assets validator
  [`check-webflash-release-assets.py`](../scripts/check-webflash-release-assets.py),
  the consistency validator
  [`validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py),
  the product-name mapper
  [`product_name_mapper.py`](../scripts/product_name_mapper.py),
  the conservative scaffold tool
  [`scaffold_product.py`](../scripts/scaffold_product.py), nor the
  tracked-secrets guard
  [`check-no-tracked-secrets.py`](../scripts/check-no-tracked-secrets.py)
  changes,
- edit any test under [`tests/`](../tests/) — every release-time
  validator (`test_webflash_artifact_naming.py`,
  `validate_webflash_builds.py`, `test_webflash_compatibility.py`,
  `test_validate_webflash_release_notes.py`,
  `test_generate_webflash_release_notes.py`,
  `test_derive_release_version_channel.py`,
  `test_release_notes_draft_workflow.py`,
  `test_product_catalog.py`, `test_product_catalog_consistency.py`,
  `test_hardware_catalog.py`, `test_product_substitutions.py`,
  `test_release_one_entity_names.py`,
  `test_led_package_mapping.py`, `validate_configs.py`, etc.) stays
  verbatim,
- add, remove, or modify any WebFlash wrapper under
  [`products/webflash/`](../products/webflash/) — the production
  Release-One wrapper
  [`ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml),
  the LED preview wrapper
  [`ceiling-poe-ventiq-roomiq-led.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq-led.yaml),
  and the blocked FanTRIAC reference wrapper
  [`ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml)
  all stay verbatim,
- add, remove, or modify any product YAML under
  [`products/`](../products/), including the production
  [`sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml),
  the LED preview
  [`sense360-ceiling-poe-ventiq-roomiq-led.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq-led.yaml),
  the blocked FanTRIAC reference
  [`sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml),
  and the 31 `legacy-compatible` Core / Core-Voice / Mini /
  FanPWM / PoE entries,
- add, remove, or modify any package YAML under
  [`packages/`](../packages/) — the six in-scope packages tracked by
  [`package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
  ([`fan_relay.yaml`](../packages/expansions/fan_relay.yaml),
  [`fan_pwm.yaml`](../packages/expansions/fan_pwm.yaml),
  [`fan_gp8403.yaml`](../packages/expansions/fan_gp8403.yaml),
  [`fan_triac.yaml`](../packages/expansions/fan_triac.yaml),
  [`power_240v.yaml`](../packages/hardware/power_240v.yaml),
  [`power_poe.yaml`](../packages/hardware/power_poe.yaml)) plus the
  Core abstract packages
  ([`sense360_core_ceiling.yaml`](../packages/hardware/sense360_core_ceiling.yaml),
  [`sense360_core.yaml`](../packages/hardware/sense360_core.yaml))
  stay verbatim,
- add, remove, or modify any entry or field in
  [`config/hardware-catalog.json`](../config/hardware-catalog.json),
  [`config/product-catalog.json`](../config/product-catalog.json),
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  or
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json) —
  no new product entry, no `lifecycle_statuses` value, no
  `canonical_modules` token, no `forbidden_tokens` change, no
  `release_one_required_configs` membership, no new build-matrix
  entry, no `webflash_build_matrix` flip, no `channel` change, no
  `version` bump, no `artifact_name` change,
- generate, regenerate, sign, deploy, or otherwise produce any
  WebFlash-side artifact — no edit of any WebFlash-side
  `REQUIRED_CONFIGS`, `scripts/data/kits.json`,
  `firmware/sources.json`, or `manifest.json` entry; those live in
  the WebFlash repo, not this repo, and are owned by
  `WF-IMPORT-GAP-001` / `WF-IMPORT-TRIAC-001`,
- promote any candidate product family to a release class beyond
  what its upstream gates have already authorised; no flip from
  `not-release-ready` to `preview-artifact-candidate`,
  `advanced/manual-warning-artifact-only`, or
  `stable-candidate-after-promotion` for any candidate row,
- promote the LED preview (`Ceiling-POE-VentIQ-RoomIQ-LED`) to
  `production` / `stable` — LED stable promotion is owned by the
  separate `RELEASE-007` slice (reference-only here; see
  [Follow-up PR sequence](#follow-up-pr-sequence)) and gated by
  the full 17-row
  [`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
  gauntlet, including the still-pending `WF-HW-TEST-002` operator
  proof and the still-pending
  [`S360-300-BENCH-001`](hardware/s360-300-r4-led.md#s360-300-bench-001-status)
  bench evidence,
- change the Release-One configuration `Ceiling-POE-VentIQ-RoomIQ`
  (`status: production`, `channel: stable`, version `1.0.0`,
  artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`,
  tag `v1.0.0`, `release_one_required_configs:
  ["Ceiling-POE-VentIQ-RoomIQ"]`),
- change the LED preview entry `Ceiling-POE-VentIQ-RoomIQ-LED`
  (stays `status: preview`, `channel: preview`, version `1.0.0`,
  artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`,
  tag `v1.0.0-led-preview`),
- change the FanTRIAC reference
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` (`status: blocked`,
  `blocker: HW-005`, `webflash_build_matrix: false`),
- change the mains-voltage compliance status of `S360-320` or
  `S360-400` (owned by COMPLIANCE-001;
  [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)),
- add any candidate family to `release_one_required_configs`, to
  any kit / default surface, to any recommended-product surface, or
  to Release-One.

If this matrix and any source-of-truth document drift, **the
source-of-truth document wins** and this matrix must be updated. The
sources of truth are listed in [See also](#see-also).

### Namespace note

The identifier `RELEASE-GAP-001` is owned by **this readiness
matrix**. It is the release-layer counterpart of the existing
`HW-GAP-001` / `PACKAGE-GAP-001` / `PRODUCT-GAP-001` /
`WEBFLASH-GAP-001` gates: a documentation-only readiness /
classification / policy doc, not an implementation slice. The actual
implementation work — building, signing, attaching, recording proof
for, and importing release artifacts — is split per family into
separate per-family slice PRs:

- **`RELEASE-RELAY-001`** — FanRelay (S360-310) preview-artifact
  slice. Builds the first FanRelay preview `.bin` on a non-`stable`
  channel after `WEBFLASH-RELAY-001` lands.
- **`RELEASE-PWM-001`** — FanPWM (S360-311) preview-artifact slice.
  Builds the first FanPWM preview `.bin` on a non-`stable` channel
  after `WEBFLASH-PWM-001` lands.
- **`RELEASE-DAC-001`** — FanDAC (S360-312) preview-artifact slice.
  Builds the first FanDAC preview `.bin` on a non-`stable` channel
  after `WEBFLASH-DAC-001` lands, honouring the
  `fandac_conflicts_with_airiq` mutex.
- **`RELEASE-TRIAC-001`** — FanTRIAC (S360-320)
  advanced/manual-warning-artifact slice. Builds the FanTRIAC
  artifact behind the manual-warning UX after `WF-TRIAC-001` lands
  and `COMPLIANCE-001` advanced / manual-warning sign-off is
  recorded. **Separate** from the standard `RELEASE-*-001` flow
  because of the advanced / manual-warning posture; never `stable`,
  never `release_one_required_configs`, never kit / default /
  recommended.
- **`RELEASE-POWER-400-001`** — PWR-240V (S360-400)
  preview-artifact slice. Builds the first PWR-240V `.bin` after
  `WEBFLASH-POWER-400-001` lands and `COMPLIANCE-001` `S360-400`
  slice closes. UX class (standard preview vs advanced /
  manual-warning) is decided by the upstream slice.
- **`RELEASE-POE-410-001`** — PoE-410 (S360-410) preview-artifact
  slice, **only if** `PRODUCT-POE-410-001` and
  `WEBFLASH-POE-410-001` together add a new PoE-410-explicit
  product entry. Often this slice is not required because the
  PoE-410 family closes by extending the Release-One caveat
  without adding a new product.
- **`RELEASE-007`** (LED stable) — reference-only here. LED stable
  promotion of `Ceiling-POE-VentIQ-RoomIQ-LED` from `preview` to
  `production` / `stable` is **out of scope** for RELEASE-GAP-001
  and **owned by**
  [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md).
  It is gated by the existing 17-row LED preview-to-stable gauntlet,
  the still-pending `WF-HW-TEST-002` operator-proof container, and
  the still-pending
  [`S360-300-BENCH-001`](hardware/s360-300-r4-led.md#s360-300-bench-001-status)
  bench-verification record. RELEASE-GAP-001 does **not** fold LED
  stable into its own scope.
- **`WF-IMPORT-GAP-001`** — Import the signed artifacts produced
  by the per-family slices above into the WebFlash repo's
  `manifest.json` / `firmware-N.json` per
  [`docs/webflash-release-handoff.md`](webflash-release-handoff.md).
  Owned by the WebFlash repo, not this repo.
- **`WF-IMPORT-TRIAC-001`** — Import the FanTRIAC artifact into
  the WebFlash repo behind the advanced / manual-warning UX.
  Separate from `WF-IMPORT-GAP-001` because of the advanced /
  manual-warning posture.

Historical references that name `RELEASE-GAP-001` as the PR that
"builds, signs, and releases firmware artifacts for the WebFlash
entries added by `WEBFLASH-GAP-001`" should be read as referring to
this readiness / gating matrix unless a later per-family slice
(`RELEASE-RELAY-001`, `RELEASE-PWM-001`, `RELEASE-DAC-001`,
`RELEASE-TRIAC-001`, `RELEASE-POWER-400-001`, `RELEASE-POE-410-001`)
is explicitly named. The existing follow-up tables in
[`product-readiness-matrix.md` Follow-up PR sequence row #9](product-readiness-matrix.md#follow-up-pr-sequence),
[`webflash-exposure-readiness-matrix.md` Follow-up PR sequence row #7](webflash-exposure-readiness-matrix.md#follow-up-pr-sequence),
[`hardware/board-readiness-matrix.md` Follow-up PR sequence row #10](hardware/board-readiness-matrix.md#follow-up-pr-sequence),
and
[`hardware/package-readiness-matrix.md` Follow-up PR sequence row #9](hardware/package-readiness-matrix.md#follow-up-pr-sequence)
remain valid by reference; they are not rewritten by this PR.

## Core rule

> **A release artifact may be produced only after every upstream
> gate — hardware evidence and pin / package mapping, package YAML
> readiness, product YAML existence and approval, WebFlash exposure
> class chosen, WebFlash wrapper existence, build-matrix entry
> approval, release-notes validity, artifact-naming rule
> conformance, SHA256 / MD5 checksum generation, release-proof
> record, and (where required) operator-proof record — is satisfied
> for the intended release class. A build-matrix entry does not
> automatically mean a stable release. A preview artifact does not
> automatically mean REQUIRED_CONFIGS. An advanced / manual-warning
> artifact does not imply compliance certification or
> recommended exposure. A release artifact is not automatically a
> kit or recommended path.**

This is the load-bearing premise of RELEASE-GAP-001. It is the
release-layer form of the
[`package-readiness-matrix.md` Core rule](hardware/package-readiness-matrix.md#core-rule)
("package YAML changes are allowed only when the target board has
verified pin-map evidence"), the
[`product-readiness-matrix.md` Core rule](product-readiness-matrix.md#core-rule)
("package readiness, product readiness, and WebFlash exposure are
three separate gates; product YAML existence does not itself
authorise WebFlash exposure"), and the
[`webflash-exposure-readiness-matrix.md` Core rule](webflash-exposure-readiness-matrix.md#core-rule)
("WebFlash exposure requires every upstream gate … for the intended
exposure class").

The full chain a release-published product must climb, in order:

1. **Hardware evidence and pin / package mapping** adequate for the
   intended release class. Verified per
   [`hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
   and the per-board `HW-PINMAP-*` audit docs.
2. **Package YAML readiness.** The product's required package(s)
   are `ready-for-package-change` per
   [`hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md),
   and the Core abstract-bus rebind (CORE-ABSTRACT-BUS-001) has
   landed where the product consumes the Ceiling Core abstract
   package.
3. **Product YAML existence and approval.** A canonical product
   YAML exists under [`products/`](../products/) and has cleared
   [`product-onboarding.md`](product-onboarding.md). Per
   [`product-readiness-matrix.md`](product-readiness-matrix.md) row
   classification.
4. **Product catalog status chosen intentionally.** The catalog
   `status` in
   [`config/product-catalog.json`](../config/product-catalog.json)
   is one of `production` / `preview` / `compile-only` /
   `hardware-pending` / `blocked` / `legacy-compatible`, chosen
   with reference to
   [`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md).
5. **WebFlash wrapper exists.** A thin wrapper YAML lives under
   [`products/webflash/`](../products/webflash/) and conforms to
   the WebFlash compatibility grammar in
   [`config/webflash-compatibility.json`](../config/webflash-compatibility.json).
6. **Build-matrix entry approved.** The product appears as a
   `webflash_build_matrix: true` row in the catalog with a matching
   row in
   [`config/webflash-builds.json`](../config/webflash-builds.json),
   validated by
   [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py)
   and
   [`tests/test_webflash_compatibility.py`](../tests/test_webflash_compatibility.py).
7. **Release notes valid for channel.** A release-notes body is
   generated by
   [`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py)
   and validated by
   [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py)
   for the target `(config_string, version, channel)`. The
   `## Changelog` section is replaced with a human-authored,
   user-visible summary before tagging when targeting `stable`.
   `blocked` / `legacy-compatible` / `deprecated` / `removed`
   entries are refused by the generator; `preview` entries on
   `stable` are refused.
8. **Artifact naming rule conformance.** The artifact name matches
   `Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin` per
   [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
   `artifact_pattern`, validated by
   [`tests/test_webflash_artifact_naming.py`](../tests/test_webflash_artifact_naming.py).
   The release tag matches `vX.Y.Z` on `stable` and `vX.Y.Z-{suffix}`
   on a prerelease channel, validated by
   [`scripts/derive_release_version_channel.py`](../scripts/derive_release_version_channel.py).
9. **Build succeeds.** The
   [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)
   workflow runs on `release.published` (or manual dispatch) and
   produces the declared `artifact_name` matching the build-matrix
   entry's `version` and `channel`.
10. **Checksums and build-info manifest attached.** The four assets
    are attached to the GitHub Release: the `.bin`,
    `checksums-sha256.txt`, `checksums-md5.txt`, and the build-info
    `manifest.json` (this is **not** the WebFlash production
    manifest; see
    [`docs/webflash-ci-alignment.md`](webflash-ci-alignment.md)).
    Validated by
    [`scripts/check-webflash-release-assets.py`](../scripts/check-webflash-release-assets.py).
11. **Release proof recorded.** A build / release proof row is
    written into
    [`docs/webflash-release-proof.md`](webflash-release-proof.md)
    with the GitHub Release URL, tag, workflow run URL, asset size,
    SHA256, and gate pass states.
12. **Operator proof recorded (where required).** For any
    `stable` promotion, the WebFlash-side `WF-HW-TEST-*`
    operator-proof container is filled by a human operator who
    flashed a real device and verified boot / Improv handoff /
    sensor smoke / module-specific indicators / rescue path. The
    [`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
    17-row gauntlet enumerates the LED-preview case (`WF-HW-TEST-002`)
    and the bench-verification record
    ([`S360-300-BENCH-001`](hardware/s360-300-r4-led.md#s360-300-bench-001-status)).
13. **WebFlash-side import readiness.** The artifact is importable
    into the WebFlash repo's `manifest.json` / `firmware-N.json` per
    [`docs/webflash-release-handoff.md`](webflash-release-handoff.md);
    the actual import is owned by `WF-IMPORT-GAP-001` /
    `WF-IMPORT-TRIAC-001` in the WebFlash repo.
14. **Release class is respected.** The artifact's channel and
    surfacing honour its declared release class — `none`,
    `docs-only / manual YAML only`, `preview-artifact-candidate`,
    `advanced/manual-warning-artifact-only`,
    `stable-candidate-after-promotion`, `production/stable`, or
    `legacy-only` (see [Release classes](#release-classes) below).
    REQUIRED_CONFIGS / kit / recommended membership is a strictly
    additional gate (see
    [REQUIRED_CONFIGS policy](#required_configs-policy) and
    [Kit / recommended release policy](#kit--recommended-release-policy)).

Three corollaries follow:

- **Skipping a gate is not allowed.** A future PR that, for
  example, attaches a `.bin` without first recording the
  release-notes generator output, or flips a preview artifact to
  `stable` without the 17-row gauntlet, must be rejected on first
  read.
- **Reaching a gate is not the same as reaching the next.** A
  product YAML that has cleared
  [`product-onboarding.md`](product-onboarding.md) has cleared step
  3 only; the wrapper / catalog / build-matrix / release-notes /
  build / checksums / release-proof / operator-proof /
  WebFlash-import / class decisions remain separately gated by this
  matrix and the per-family slice PRs.
- **A passing build is not a stable promotion.** Even a fully
  successful `preview`-channel build / checksums / attached release
  is **not** evidence that the entry should flip to `stable` /
  `production`. Stable promotion is a separately-gated decision
  owned by
  [`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md).

## Status value vocabulary (policy-only)

The candidate release table below uses a small set of cell values.
**All are policy-only labels** — they are not JSON enums, not
promoted to any schema, and not added to any validator by this PR.
They sit alongside the existing
[`config/product-catalog.json`](../config/product-catalog.json)
`lifecycle_statuses`
(`production` / `preview` / `compile-only` / `hardware-pending` /
`blocked` / `legacy-compatible` / `deprecated` / `removed`), the
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
`allowed_channels` (`stable` / `beta` / `preview` / `dev` /
`rescue`) with `production_channel: stable`, the
[`product-availability-taxonomy.md`](product-availability-taxonomy.md)
13-rung ladder, the
[`package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
package labels, the
[`product-readiness-matrix.md`](product-readiness-matrix.md)
product labels, and the
[`webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md)
exposure labels that this matrix consumes for the upstream-gate
columns.

| Cell value | Meaning |
|---|---|
| `not-release-ready` | The candidate family is **not** eligible for any new release artifact today. The cause is identified by one or more of the more specific labels below. Carried by every candidate row in this matrix as the primary "Allowed release action now" verdict. |
| `missing-build-matrix` | No `webflash_build_matrix: true` row exists for the family in [`config/webflash-builds.json`](../config/webflash-builds.json), and [`webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md) has not authorised one. The follow-up is the per-family `WEBFLASH-*-001` slice. Until that slice lands, no release artifact may be built. |
| `missing-webflash-wrapper` | No wrapper YAML exists for the family under [`products/webflash/`](../products/webflash/). The follow-up is the per-family `WEBFLASH-*-001` slice. Until that slice lands, no build-matrix entry can be approved, so no release artifact may be built. |
| `missing-product-yaml` | No canonical product YAML exists under [`products/`](../products/) for the family, and [`product-readiness-matrix.md`](product-readiness-matrix.md) has not marked the family `ready-for-product-yaml`. The follow-up is the per-family `PRODUCT-*-001` slice. Until that slice lands, no WebFlash wrapper / catalog entry / build-matrix entry / release artifact may be added. |
| `missing-package-readiness` | At least one required package for the family is **not** `ready-for-package-change` per [`hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md). The follow-up is the per-family `PACKAGE-*-001` slice. |
| `missing-hardware-evidence` | At least one required board carries `schematic-evidence-pending` or `hardware-evidence-pending` per [`hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md) and the per-board `HW-PINMAP-*` audit doc. The follow-up is the per-board `HW-ASSETS-*` supplier-delivery + `HW-PINMAP-*-FOLLOWUP` reconciliation. |
| `preview-artifact-candidate` | If and when the per-family WebFlash slice lands and the upstream `RELEASE-*-001` slice authors the build / proof, the eventual release class is `preview-artifact-candidate`: a non-`stable` channel `.bin` (typically `preview`) attached to a prerelease GitHub Release, validated by the existing release-notes / artifact-naming / release-assets guards, with the WebFlash-side import optional / staged. The first stable promotion would later require the full 17-row [`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md) gauntlet. |
| `advanced/manual-warning-artifact-only` | If and when the per-family WebFlash slice lands, the eventual release class is `advanced/manual-warning-artifact-only`: a `.bin` produced only behind the advanced / manual-warning UX, never on the standard landing list, never in `release_one_required_configs`, never kit / recommended / default, never compliance-certified by virtue of having a build artifact. Today this applies only to FanTRIAC; the long-term posture is documented in [`hardware/s360-320-r4-triac.md` Advanced / manual-warning product posture](hardware/s360-320-r4-triac.md#advanced--manual-warning-product-posture) and is now policy-recorded by `PRODUCT-TRIAC-001` as a notes-only catalog edit (JSON `status: blocked` / `blocker: HW-005` / `webflash_build_matrix: false` unchanged; no new lifecycle enum). A live advanced-channel artifact still requires HW-005 + COMPLIANCE-001 + `HW-PINMAP-320-FOLLOWUP` + `PACKAGE-TRIAC-001` + `PRODUCT-TRIAC-002` + `WF-TRIAC-001` + `RELEASE-TRIAC-001` to clear. |
| `stable-candidate-after-promotion` | If and when the per-family WebFlash slice lands **and** a preview release has been built, attached, and operator-proven, the family is **eligible** to enter the full 17-row [`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md) gauntlet. Reaching `stable-candidate-after-promotion` does **not** authorise a stable build; it authorises the start of the gauntlet. Today no candidate family is at `stable-candidate-after-promotion`; only the existing Release-One `Ceiling-POE-VentIQ-RoomIQ` is past it. |
| `stable-not-approved` | The family is **never** approved for a stable release artifact by default — irrespective of any future product YAML / wrapper / catalog / build-matrix / preview-artifact existence. Carried categorically by FanTRIAC; any future stable approval would be a separately-scoped explicit PR with COMPLIANCE-001 sign-off and is **not** authorised by this matrix. |
| `not-required-configs` | Even after a family has reached `preview-artifact-candidate` (or beyond), it is **not** added to `release_one_required_configs` by default. Any addition is a separately gated, explicit PR per [REQUIRED_CONFIGS policy](#required_configs-policy). |
| `not-recommended` | Even after a family has reached `preview-artifact-candidate` (or beyond), it is **not** added to recommended-product surfaces by default. See [Kit / recommended release policy](#kit--recommended-release-policy). |
| `not-kit-default` | Even after a family has reached `preview-artifact-candidate` (or beyond), it is **not** added to kit / default-bundle surfaces (WebFlash-side `scripts/data/kits.json` etc.) by default. See [Kit / recommended release policy](#kit--recommended-release-policy). |
| `operator-proof-required` | An operator / human-flash proof is required for the intended release class before any promotion to `stable`. For LED preview this is the WebFlash-side `WF-HW-TEST-002` container; for other families it would be the family-specific equivalent (and, for hardware-bench-dependent families, the corresponding `S360-NNN-BENCH-NNN` record). |
| `release-proof-required` | A release-proof row in [`docs/webflash-release-proof.md`](webflash-release-proof.md) (containing tag, run URL, asset size, SHA256, gate pass states) is required before the family's artifact is considered released, and before WebFlash-side import is authorised. |
| `legacy-only` | The family has a `legacy-compatible` product YAML under [`products/`](../products/) but no WebFlash wrapper / catalog `webflash_wrapper` / `webflash_build_matrix: true` and therefore no release artifact path through the standard flow. Carried today by the legacy four-channel [`products/sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml) and the legacy [`products/sense360-poe.yaml`](../products/sense360-poe.yaml). |
| `docs-only` | The family's release exposure is intentionally bounded to docs / manual YAML use only; the user installs by `esphome run` rather than via a WebFlash-flashable release artifact. Carried today by the 31 `legacy-compatible` entries. No new `docs-only` entry is added by this PR. |
| `blocked-from-standard-release` | The family must never be released on the standard `RELEASE-*-001` flow, regardless of any future product YAML existence. Carried by FanTRIAC. Applied as an additive qualifier alongside `advanced/manual-warning-artifact-only` and `stable-not-approved`. |
| `unknown` | Cannot be classified from currently committed evidence. Not used in this matrix today; every candidate family below is placeable under the labels above. |

A row may carry one primary "Allowed release action now" label
(typically `not-release-ready`) plus a future-class label
(`preview-artifact-candidate` /
`advanced/manual-warning-artifact-only` /
`stable-candidate-after-promotion`) plus any number of additive
qualifier labels (`not-required-configs` / `not-recommended` /
`not-kit-default` / `operator-proof-required` /
`release-proof-required` / `blocked-from-standard-release` /
`stable-not-approved`) and one or more cause labels
(`missing-build-matrix` / `missing-webflash-wrapper` /
`missing-product-yaml` / `missing-package-readiness` /
`missing-hardware-evidence`).

## Release classes

Release exposure is a discrete classification with seven values.
Every product / candidate family lands at exactly one class at any
given moment. Movement up the ladder requires the upstream gates
plus a named per-family slice PR (see
[Follow-up PR sequence](#follow-up-pr-sequence)).

| Class | Means | Used today by |
|---|---|---|
| `none` | No product YAML; no wrapper; no catalog entry; no build-matrix entry; no release artifact; not released in any form. | Every candidate family in this matrix (FanRelay / FanPWM / FanDAC / FanTRIAC release-side exposure / PWR-240V / PoE-410). Also the default state for any new product family that has not begun the product-onboarding flow. |
| `docs-only` / `manual YAML only` | A canonical YAML exists under [`products/`](../products/) but the catalog entry is `legacy-compatible` (no `config_string`, no `webflash_wrapper`, no `artifact_name`, `webflash_build_matrix: false`). The user installs by manual `esphome run`; no GitHub Release artifact exists for the entry. | The 31 `legacy-compatible` Core / Core-Voice / Mini / `sense360-fan-pwm.yaml` / `sense360-poe.yaml` entries in [`config/product-catalog.json`](../config/product-catalog.json). |
| `preview-artifact-candidate` | A WebFlash wrapper, catalog entry, and build-matrix entry exist on a non-`stable` channel (typically `preview`); the artifact is built, signed, and attached to a GitHub prerelease via [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml); release notes are valid for the channel; checksums and build-info `manifest.json` are attached; a release-proof row is recorded in [`docs/webflash-release-proof.md`](webflash-release-proof.md). The WebFlash-side import is optional / staged. The artifact is **not** stable and is **not** in `release_one_required_configs`. | `Ceiling-POE-VentIQ-RoomIQ-LED` only (RELEASE-005 prerelease `v1.0.0-led-preview`). Each additional `preview-artifact-candidate` requires a separate per-family `RELEASE-*-001` slice. |
| `advanced/manual-warning-artifact-only` | A WebFlash wrapper / catalog / build-matrix entry exists behind the advanced / manual-warning UX, never on the standard landing list, never in `release_one_required_configs`, never kit / recommended / default. The artifact is built only by the dedicated advanced-channel slice and is never compliance-certified by virtue of being releasable. The advanced / manual-warning posture is an exposure class, not a certification claim; `COMPLIANCE-001` sign-off runs in addition. | The intended long-term posture for FanTRIAC. Today the catalog `status` for `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` is `blocked` under HW-005 and `webflash_build_matrix: false`; no release artifact exists. Posture is `RELEASE-TRIAC-001` (after `WF-TRIAC-001`) responsibility, not realised here. |
| `stable-candidate-after-promotion` | Eligible to enter the full 17-row [`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md) gauntlet. Eligibility does not authorise a stable build; it authorises the start of the gauntlet. The gauntlet's seventeen rows (product YAML / wrapper / catalog preview / build matrix preview / preview release artifact / preview release proof / WebFlash import / live preview deploy / operator flash proof / hardware bench verification / stable-ready release notes / production catalog promotion / stable build artifact / stable WebFlash import / REQUIRED_CONFIGS decision / kit decision / human approval) must all be `done` or `accepted-waiver`. | Today: no candidate family. The LED preview `Ceiling-POE-VentIQ-RoomIQ-LED` has cleared rows 1–8 of the gauntlet (preview floor) but rows 9–17 remain `pending` or `decision needed`; per the LED preview decision the LED stable path is owned by `RELEASE-007`, **not** RELEASE-GAP-001. |
| `production/stable` | Catalog `status: production`, `channel: stable`, version `1.0.0`+; `webflash_build_matrix: true`; signed release artifact attached to a plain `vX.Y.Z` GitHub Release with valid release notes, SHA256 / MD5 checksums, build-info `manifest.json`, and a release-proof row in [`docs/webflash-release-proof.md`](webflash-release-proof.md); WebFlash-side import live; deployed manifest current; operator-proof container filled. Any new `production/stable` requires the full 17-row gauntlet. | `Ceiling-POE-VentIQ-RoomIQ` only (Release-One; tag `v1.0.0`; artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`). |
| `legacy-only` | The canonical YAML exists but is `legacy-compatible`; the family is not in the WebFlash build matrix, is not promoted by any per-family slice, and has no release-artifact path through the standard flow. | The legacy four-channel [`products/sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml) and [`products/sense360-poe.yaml`](../products/sense360-poe.yaml), plus the 29 `core-*` / `mini-*` legacy entries (which more precisely sit at `docs-only`; "legacy-only" is the additive qualifier that prevents non-legacy siblings being added). |

The rules:

> **An `advanced/manual-warning-artifact-only` artifact is an
> explicit release *class*, not a certification claim and not a
> compliance verdict.** A family classified
> `advanced/manual-warning-artifact-only` is buildable, signable,
> attachable to a GitHub Release, and installable only behind a
> manual-warning UX gate; any compliance / safety / regulatory
> certification (UK / EU mains-voltage in particular) is a separate
> `COMPLIANCE-001` gate that runs in addition.

> **A `preview-artifact-candidate` artifact is not a stable
> release.** A successful preview build, attached release, and
> recorded release proof do not constitute stable promotion.
> Stable promotion is owned by
> [`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
> and requires every one of the 17 gauntlet rows.

> **A `production/stable` artifact is not automatically
> REQUIRED_CONFIGS.** Membership in `release_one_required_configs`
> is a separately-gated decision per
> [REQUIRED_CONFIGS policy](#required_configs-policy). Release-One
> is in `release_one_required_configs` because Release-One has
> always been the WebFlash baseline-health entry; any additional
> stable promotion requires its own explicit PR.

> **A release artifact is not automatically a kit or recommended
> path.** Kit / default / recommended membership is a separately-gated
> decision per [Kit / recommended release policy](#kit--recommended-release-policy).

## Current release surface

The current release surface — taken verbatim from
[`config/product-catalog.json`](../config/product-catalog.json),
[`config/webflash-builds.json`](../config/webflash-builds.json),
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
the
[`docs/webflash-release-proof.md`](webflash-release-proof.md)
proof records, and the GitHub Releases on
[`sense360store/esphome-public`](https://github.com/sense360store/esphome-public/releases) —
and unchanged by this PR is as follows.

| Catalog `config_string` | Catalog `status` / `channel` | Release tag | Release artifact | Checksums | Build-info `manifest.json` | Release-proof row | Release class |
|---|---|---|---|---|---|---|---|
| `Ceiling-POE-VentIQ-RoomIQ` | `production` / `stable` | `v1.0.0` | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` | `checksums-sha256.txt`, `checksums-md5.txt` | attached (build-info) | recorded ([`docs/webflash-release-proof.md`](webflash-release-proof.md)) | `production/stable` (Release-One). |
| `Ceiling-POE-VentIQ-RoomIQ-LED` | `preview` / `preview` | `v1.0.0-led-preview` | `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` (1,135,904 bytes; SHA256 `93310d2cbc27355e399f36a232336b6b9075dacfc178d603c7a92aa1089182d3`) | `checksums-sha256.txt`, `checksums-md5.txt` | attached (build-info) | recorded ([`docs/webflash-release-proof.md`](webflash-release-proof.md) RELEASE-005 row) | `preview-artifact-candidate` (PRODUCT-009 / RELEASE-005). |
| `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` | `blocked` (`blocker: HW-005`) / — | — | — | — | — | — | Blocked reference. Posture intent: `advanced/manual-warning-artifact-only` once HW-005 + COMPLIANCE-001 + `WF-TRIAC-001` + `RELEASE-TRIAC-001` clear. |
| 31 `legacy-compatible` entries (Core / Core-Voice / Mini / `sense360-fan-pwm.yaml` / `sense360-poe.yaml`) | `legacy-compatible` / — | — | — | — | — | — | `docs-only` / `legacy-only`. |

Additional context:

- The
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  `allowed_channels` are `stable`, `beta`, `preview`, `dev`,
  `rescue` with `production_channel: stable` and
  `rescue_config_string: "Rescue"`. Today only `stable` and
  `preview` are used by released artifacts; the rescue channel is
  reserved by contract and no candidate family releases on `beta`
  / `dev` / `rescue` by this matrix.
- `release_one_required_configs` in
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  is the single entry `["Ceiling-POE-VentIQ-RoomIQ"]`. **No
  candidate family in this matrix is added to it.** The LED preview
  is explicitly **not** in `release_one_required_configs`;
  FanTRIAC is **never** added.
- The
  [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)
  workflow is the canonical build / release path: triggers on
  `release.published` (and supports `workflow_dispatch` for
  testing / preview), generates a build matrix from
  [`products/`](../products/), builds via ESPHome
  `2026.4.5`, renames binaries to the
  `Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin` pattern,
  validates assets against
  [`scripts/check-webflash-release-assets.py`](../scripts/check-webflash-release-assets.py)
  and release-notes body against
  [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py),
  and attaches the four assets (the `.bin`,
  `checksums-sha256.txt`, `checksums-md5.txt`, build-info
  `manifest.json`) to the GitHub Release.

## Candidate release table

The table below is the matrix's primary deliverable. Each row is a
candidate **product family** (not a candidate product YAML; this
matrix does not enumerate per-config-string variants because no
candidate family today carries a product YAML or WebFlash wrapper to
enumerate against). Every cell is a policy label as defined in
[Status value vocabulary](#status-value-vocabulary-policy-only) and
[Release classes](#release-classes) above.

| Candidate family | Required product / build gate | Current WebFlash readiness | Current build-matrix status | Current artifact status | Allowed release action now | Future release class | Stable eligibility | REQUIRED_CONFIGS eligibility | Kit / recommended eligibility | Follow-up owner |
|---|---|---|---|---|---|---|---|---|---|---|
| **FanRelay / S360-310** | none (no `sense360-*-fanrelay-*.yaml`; no `products/webflash/<…>-fanrelay-<…>.yaml`); `WEBFLASH-RELAY-001` not landed | `not-webflash-ready` per [`webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md#fanrelay--s360-310-webflash-posture) (module-side schematic now committed under HW-ASSETS-310 and consumed by HW-PINMAP-310-FOLLOWUP; package still `schematic-evidence-pending` + `needs-package-reconciliation` until `CORE-ABSTRACT-BUS-001` + silkscreen / harness / `K1` BOM evidence + `PACKAGE-RELAY-001` land) | none (no `webflash_build_matrix: true` row for any FanRelay config) | none | `not-release-ready` (`missing-build-matrix` + `missing-webflash-wrapper` + `missing-product-yaml` + `missing-package-readiness` + `missing-hardware-evidence`) | `preview-artifact-candidate` (after all upstream slices land and `RELEASE-RELAY-001` builds the first preview `.bin`) | `not-stable-by-default`; `operator-proof-required` + `release-proof-required` before any 17-row gauntlet entry | `not-required-configs` | `not-recommended` + `not-kit-default` | `HW-ASSETS-310` *(landed)* → `HW-PINMAP-310-FOLLOWUP` *(landed)* → silkscreen / harness / `K1` BOM evidence + `CORE-ABSTRACT-BUS-001` → `PACKAGE-RELAY-001` → `PRODUCT-RELAY-001` → `WEBFLASH-RELAY-001` → `RELEASE-RELAY-001` → `WF-IMPORT-GAP-001`. |
| **FanPWM / S360-311** | none (no non-legacy `sense360-*-fanpwm-*.yaml`; legacy [`products/sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml) is `legacy-compatible` only; no WebFlash wrapper); `WEBFLASH-PWM-001` not landed | `not-webflash-ready` per [`webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md#pwm--s360-311-webflash-posture) | none | none | `not-release-ready` (`missing-build-matrix` + `missing-webflash-wrapper` + `missing-product-yaml` + `missing-package-readiness`) | `preview-artifact-candidate` (after upstream slices + `RELEASE-PWM-001`) | `not-stable-by-default`; `operator-proof-required` + `release-proof-required` | `not-required-configs` | `not-recommended` + `not-kit-default` (legacy four-channel YAML retention / migration / removal decided by `PRODUCT-PWM-001`; legacy entry stays `legacy-only`) | `HW-PINMAP-311-FOLLOWUP` → `PACKAGE-PWM-001` (+ `CORE-ABSTRACT-BUS-001`) → `PRODUCT-PWM-001` → `WEBFLASH-PWM-001` → `RELEASE-PWM-001` → `WF-IMPORT-GAP-001`. |
| **FanDAC / S360-312** | none (no `sense360-*-fandac-*.yaml`; no WebFlash wrapper); future FanDAC product must respect the `fandac_conflicts_with_airiq` mutex | `not-webflash-ready` per [`webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md#dac--s360-312-webflash-posture) | none | none | `not-release-ready` (`missing-build-matrix` + `missing-webflash-wrapper` + `missing-product-yaml` + `missing-package-readiness`) | `preview-artifact-candidate` (after upstream slices + `RELEASE-DAC-001`; AirIQ-bearing FanDAC variants forbidden) | `not-stable-by-default`; `operator-proof-required` + `release-proof-required` | `not-required-configs` | `not-recommended` + `not-kit-default` (FanDAC ↔ AirIQ mutex narrows the eligible config-string space) | `HW-PINMAP-312-FOLLOWUP` → `PACKAGE-DAC-001` → `PRODUCT-DAC-001` → `WEBFLASH-DAC-001` → `RELEASE-DAC-001` → `WF-IMPORT-GAP-001`. |
| **FanTRIAC / S360-320** | blocked reference [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml) exists; catalog status `blocked`, blocker `HW-005`, `webflash_build_matrix: false`; `PRODUCT-TRIAC-001` has performed a **notes-only** catalog edit recording the advanced / manual-warning candidate posture without changing any structural field; the blocked WebFlash wrapper [`products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml) is retained as reference only | blocked reference; `not-webflash-ready` per [`webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md#triac--s360-320-webflash-posture); the long-term posture is `advanced/manual-warning-only`, policy-recorded by `PRODUCT-TRIAC-001` notes-only | not in build matrix; `webflash_build_matrix: false` | none | `not-release-ready` (`missing-build-matrix` + the blocked reference is not a release-candidate; `blocked-from-standard-release`) | `advanced/manual-warning-artifact-only` **only** (long-term posture; policy-recorded by `PRODUCT-TRIAC-001` notes-only; a live advanced-channel `.bin` still requires `WF-TRIAC-001` after `PACKAGE-TRIAC-001` + `PRODUCT-TRIAC-002` + `COMPLIANCE-001` advanced / manual-warning sign-off + WebFlash-side manual-warning UX; then `RELEASE-TRIAC-001` builds the advanced-channel `.bin`) | **`stable-not-approved` — never by default.** Stable promotion is not authorised by this matrix, by `RELEASE-TRIAC-001`, or by any future routine release-side PR. Any such promotion would be a separately-scoped, explicit PR with COMPLIANCE-001 sign-off. | **`not-required-configs` — never by default.** | **`not-recommended` + `not-kit-default` — never by default.** Mains-voltage advanced / manual-warning artifacts are categorically excluded from kit / default / recommended / Release-One surfaces, irrespective of any future product / wrapper / build / release / import existence. | `PRODUCT-TRIAC-001` (landed: notes-only catalog reclassification) → `HW-005` resolution → `HW-PINMAP-320-FOLLOWUP` → `PACKAGE-TRIAC-001` → `PRODUCT-TRIAC-002` → `COMPLIANCE-001` advanced / manual-warning sign-off → `WF-TRIAC-001` (advanced / manual-warning WebFlash slice) → `RELEASE-TRIAC-001` (advanced-channel release) → `WF-IMPORT-TRIAC-001` (advanced / manual-warning WebFlash import). |
| **PWR-240V / S360-400** | none (the four `legacy-compatible` `*-pwr` Core variants are pre-WebFlash YAMLs only; no WebFlash-shippable PWR-240V product entry; no wrapper); COMPLIANCE-001 `S360-400` slice in force; S360-400 module-side schematic committed under HW-ASSETS-400 (PR #514) at [`hardware/schematics/S360-400-R4.pdf`](hardware/schematics/S360-400-R4.pdf) with curated artifact index at [`hardware/artifacts/S360-400-R4.md`](hardware/artifacts/S360-400-R4.md); HW-PINMAP-400-FOLLOWUP consumed both and promoted [`hardware/s360-400-r4-power.md`](hardware/s360-400-r4-power.md) to `partial — schematic evidence available; package reconciliation, BOM, silkscreen, creepage/clearance, and COMPLIANCE-001 pending`; release-side gating is unchanged | `not-webflash-ready` per [`webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md#power--s360-400-webflash-posture) | none | none | `not-release-ready` (`missing-build-matrix` + `missing-webflash-wrapper` + `missing-product-yaml` + `missing-package-readiness`; HW-ASSETS-400 schematic + artifact index landed and HW-PINMAP-400-FOLLOWUP consumed them, but pin-map / package / product / WebFlash slices not in scope; COMPLIANCE-001 gate applies in addition) | `preview-artifact-candidate` (default; UX class — standard vs advanced / manual-warning — decided per `PRODUCT-POWER-400-001` / `WEBFLASH-POWER-400-001` compliance verdict) | `not-stable-by-default`; `operator-proof-required` + `release-proof-required`; mains-voltage compliance posture is gating-priority over stable promotion | `not-required-configs` | `not-recommended` + `not-kit-default` | `HW-ASSETS-400` *(landed at PR #514)* → `HW-PINMAP-400-FOLLOWUP` *(this PR; docs-only)* → BOM + silkscreen + creepage / clearance + bench / thermal / EMI evidence → `PACKAGE-POWER-400-001` → `COMPLIANCE-001` S360-400 slice closure → `PRODUCT-POWER-400-001` → `WEBFLASH-POWER-400-001` → `RELEASE-POWER-400-001` → `WF-IMPORT-GAP-001`. |
| **PoE-410 / S360-410** | none directly; the verified S360-410 PoE PSU is consumed only by Release-One (`Ceiling-POE-VentIQ-RoomIQ`) and the LED preview (`Ceiling-POE-VentIQ-RoomIQ-LED`) under their existing schematic-pending caveat per [`release-one-hardware-audit.md` Findings → PoE PSU](release-one-hardware-audit.md#findings); module-side schematic now committed under HW-ASSETS-410 / PR #516 and consumed by HW-PINMAP-410-FOLLOWUP (audit now `partial`); no new PoE-410-explicit product entry | `not-webflash-ready` for any **new** PoE-410 product entry per [`webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md#poe--s360-410-webflash-posture); existing Release-One PoE consumption unaffected | none new; existing Release-One row unchanged | **Release-One artifact unchanged**; the existing `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` and the LED preview `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` are not re-released, requalified, or modified by this matrix | `not-release-ready` for any **new** PoE-410 product entry; existing Release-One and LED preview artifacts stay verbatim | `preview-artifact-candidate` (only if `PRODUCT-POE-410-001` decides a new product entry is warranted; the default close is no-new-entry / caveat-closure-only and no new release artifact is produced) | `not-stable-by-default`; Release-One's existing stable membership unchanged | `not-required-configs` (Release-One's existing membership is not touched) | `not-recommended` + `not-kit-default` (no new product entry implies no new kit / recommended membership) | `HW-ASSETS-410` (PR #516) → `HW-PINMAP-410-FOLLOWUP` (this PR) → BOM cross-check → `S360-100-BENCH-001` update / `HW-002 OQ#6` closure → `S360-410` `schematic_status: verified` JSON PR → `PACKAGE-POE-410-001` → `PRODUCT-POE-410-001` (if warranted) → `WEBFLASH-POE-410-001` (if a new product entry is added) → `RELEASE-POE-410-001` (if a new artifact is warranted) → `WF-IMPORT-GAP-001`. |

No row in this table carries `preview-artifact-candidate`,
`advanced/manual-warning-artifact-only`,
`stable-candidate-after-promotion`, or `production/stable` as a
*current* class today; every row is `not-release-ready` at the
present moment. The future-class column records the **eventual**
class each family would reach if and only if the named upstream
gates close and the named per-family release slice lands.

## Relay / S360-310 release posture

**Current state.** No FanRelay product YAML under
[`products/`](../products/); no FanRelay WebFlash wrapper under
[`products/webflash/`](../products/webflash/); no FanRelay catalog
entry in
[`config/product-catalog.json`](../config/product-catalog.json); no
FanRelay build-matrix row in
[`config/webflash-builds.json`](../config/webflash-builds.json); no
FanRelay artifact has ever been built / signed / attached / imported.
The upstream gates per
[`webflash-exposure-readiness-matrix.md` §Relay / S360-310 WebFlash posture](webflash-exposure-readiness-matrix.md#relay--s360-310-webflash-posture)
all carry `not-webflash-ready`. **Module-side schematic PDF is
committed under HW-ASSETS-310** at
[`docs/hardware/schematics/S360-310-R4.pdf`](hardware/schematics/S360-310-R4.pdf)
+
[`docs/hardware/artifacts/S360-310-R4.md`](hardware/artifacts/S360-310-R4.md);
**HW-PINMAP-310-FOLLOWUP** has consumed the schematic and promoted
the audit doc at
[`hardware/s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md)
from `pending — schematic / design evidence required` to
`partial — schematic evidence available; package reconciliation
pending`. The audit records the schematic-backed module-`J2` ↔
Core-`J4` logical net match and the module-side relay coil-drive
topology, and inventories the silkscreen / harness / `K1` BOM /
bench / Core abstract-bus rebind gaps that still block downstream
work.
[`hardware/board-readiness-matrix.md` §S360-310](hardware/board-readiness-matrix.md#s360-310-sense360-relay)
records the post-FOLLOWUP `partially-documented` /
`package-yaml-pending` state;
[`hardware/package-readiness-matrix.md` §fan_relay.yaml](hardware/package-readiness-matrix.md#fan_relayyaml--s360-310)
records `schematic-evidence-pending` +
`needs-package-reconciliation`.

**Allowed release action now.** `not-release-ready`. No artifact
build, no signing, no GitHub Release, no checksums, no proof-record,
no WebFlash import. RELEASE-GAP-001 produces **none** of these for
the Relay family.

**Future release class (intent).** `preview-artifact-candidate` only
after the full upstream chain has closed:
`HW-ASSETS-310` *(landed; module-side schematic PDF + curated
artifact index committed)* → `HW-PINMAP-310-FOLLOWUP` *(landed;
schematic-backed reconciliation recorded in
[`hardware/s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md))*
→ silkscreen / harness / `K1` BOM evidence +
`CORE-ABSTRACT-BUS-001` (resolves the `relay_pin` `IO3` vs `GPIO4`
vs `GPIO10` disagreement) → `PACKAGE-RELAY-001` (FanRelay package
YAML reconciliation) → `PRODUCT-RELAY-001` (canonical product YAML
under [`products/`](../products/)) → `WEBFLASH-RELAY-001` (wrapper +
catalog entry + build-matrix entry on a non-`stable` channel) →
`RELEASE-RELAY-001` (build / sign / attach the preview `.bin`;
generate and validate release notes; record SHA256 + MD5 checksums
and the build-info `manifest.json`; record the proof row in
[`docs/webflash-release-proof.md`](webflash-release-proof.md)) →
`WF-IMPORT-GAP-001` (WebFlash-side import).

**Stable eligibility.** `not-stable-by-default`. After
`RELEASE-RELAY-001`, FanRelay enters
`preview-artifact-candidate`; the first stable promotion later
requires the full 17-row
[`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
gauntlet, including `operator-proof-required` (a future
`WF-HW-TEST-*` Relay container) and `release-proof-required`. No
shortcut.

**REQUIRED_CONFIGS posture.** `not-required-configs` by default.
After preview-artifact-candidate exposure, FanRelay is not added to
`release_one_required_configs`. Any such addition would be a
separate, explicit PR per
[REQUIRED_CONFIGS policy](#required_configs-policy).

**Kit / recommended posture.** `not-recommended` + `not-kit-default`
until `PRODUCT-RELAY-001` (and any later UX decision) makes an
explicit decision. Relay's inclusion in kit / default /
recommended bundles is not implied by `preview-artifact-candidate`.

**Cross-references.**
[`hardware/s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md),
[`hardware/board-readiness-matrix.md` §S360-310](hardware/board-readiness-matrix.md#s360-310-sense360-relay),
[`hardware/package-readiness-matrix.md` §fan_relay.yaml](hardware/package-readiness-matrix.md#fan_relayyaml--s360-310),
[`product-readiness-matrix.md` §FanRelay / S360-310](product-readiness-matrix.md#fanrelay--s360-310),
[`webflash-exposure-readiness-matrix.md` §Relay / S360-310 WebFlash posture](webflash-exposure-readiness-matrix.md#relay--s360-310-webflash-posture).

## PWM / S360-311 release posture

**Current state.** No non-legacy FanPWM product YAML under
[`products/`](../products/); no FanPWM WebFlash wrapper; no FanPWM
catalog entry on the WebFlash track; no FanPWM build-matrix row; no
FanPWM artifact. The legacy four-channel
[`products/sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml)
is `legacy-compatible` only and is **not** WebFlash-shippable; it
is `docs-only` / `legacy-only` and produces no release artifact.
The PWM board has its module-side schematic PDF committed at
[`hardware/schematics/S360-311-R4.pdf`](hardware/schematics/S360-311-R4.pdf)
under HW-ASSETS-003 but
[`hardware/s360-311-r4-pwm.md`](hardware/s360-311-r4-pwm.md) status
is `partial — schematic evidence available; package reconciliation
pending`; the SX1509-channel vs direct-ESP32-GPIO disagreement
remains unresolved (see
[`webflash-exposure-readiness-matrix.md` §PWM / S360-311 WebFlash posture](webflash-exposure-readiness-matrix.md#pwm--s360-311-webflash-posture)).

**Allowed release action now.** `not-release-ready`. No artifact
build, no signing, no GitHub Release, no checksums, no proof, no
WebFlash import. The legacy four-channel YAML stays
`legacy-compatible` and continues to produce no release artifact.

**Future release class (intent).** `preview-artifact-candidate`
only after: `HW-PINMAP-311-FOLLOWUP` (standalone schematic-backed
reference doc; Core `J6` pin-order verification; UART-on-`J3`
resolution; single- vs four-channel canonical-abstraction
decision) → `PACKAGE-PWM-001` (FanPWM package YAML reconciliation;
`CORE-ABSTRACT-BUS-001` rebind; legacy four-channel fate) →
`PRODUCT-PWM-001` (canonical product YAML; legacy retain / migrate
/ remove decision) → `WEBFLASH-PWM-001` (wrapper + catalog +
build-matrix on non-`stable`) → `RELEASE-PWM-001` (build / sign /
attach the preview `.bin`; release notes; checksums; proof row) →
`WF-IMPORT-GAP-001`.

**Stable eligibility.** `not-stable-by-default`; the 17-row
gauntlet applies in addition. `operator-proof-required` +
`release-proof-required`.

**REQUIRED_CONFIGS posture.** `not-required-configs` by default.

**Kit / recommended posture.** `not-recommended` +
`not-kit-default`. The legacy four-channel YAML retention /
migration / removal decision is owned by `PRODUCT-PWM-001`, not by
this matrix.

**Cross-references.**
[`hardware/s360-311-r4-pwm.md`](hardware/s360-311-r4-pwm.md),
[`hardware/board-readiness-matrix.md` §S360-311](hardware/board-readiness-matrix.md#s360-311-sense360-pwm),
[`hardware/package-readiness-matrix.md` §fan_pwm.yaml](hardware/package-readiness-matrix.md#fan_pwmyaml--s360-311),
[`product-readiness-matrix.md` §FanPWM / S360-311](product-readiness-matrix.md#fanpwm--s360-311),
[`webflash-exposure-readiness-matrix.md` §PWM / S360-311 WebFlash posture](webflash-exposure-readiness-matrix.md#pwm--s360-311-webflash-posture).

## DAC / S360-312 release posture

**Current state.** No FanDAC product YAML under
[`products/`](../products/); no FanDAC WebFlash wrapper; no FanDAC
catalog entry; no FanDAC build-matrix row; no FanDAC artifact. The
DAC board has its module-side schematic PDF committed at
[`hardware/schematics/S360-312-R4.pdf`](hardware/schematics/S360-312-R4.pdf)
under HW-ASSETS-003 but
[`hardware/s360-312-r4-dac.md`](hardware/s360-312-r4-dac.md) status
is `partial — schematic evidence available; package reconciliation
pending`; voltage-rail discrepancy, DIP-switch I²C address scheme,
UART-vs-Nextion arbitration, and a stale header-comment block on
[`packages/expansions/fan_gp8403.yaml`](../packages/expansions/fan_gp8403.yaml)
remain unresolved. The `fandac_conflicts_with_airiq` mutex in
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
constrains any future product YAML; no AirIQ-bearing FanDAC variant
is permitted.

**Allowed release action now.** `not-release-ready`. No artifact
build, no signing, no GitHub Release, no checksums, no proof, no
WebFlash import. The FanDAC ↔ AirIQ mutex is not relaxed.

**Future release class (intent).** `preview-artifact-candidate`
only after: `HW-PINMAP-312-FOLLOWUP` (voltage-rail / DIP-switch /
UART / Cloudlift / voltage-mode-jumper resolution) →
`PACKAGE-DAC-001` (FanDAC package YAML reconciliation; stale
header-comment cleanup; DIP-switch address scheme) →
`PRODUCT-DAC-001` (canonical product YAML; enforce mutex; no
AirIQ-bearing variant) → `WEBFLASH-DAC-001` (wrapper + catalog +
build-matrix on non-`stable`) → `RELEASE-DAC-001` (build / sign /
attach the preview `.bin`; release notes; checksums; proof row) →
`WF-IMPORT-GAP-001`.

**Stable eligibility.** `not-stable-by-default`; the 17-row
gauntlet applies in addition. `operator-proof-required` +
`release-proof-required`.

**REQUIRED_CONFIGS posture.** `not-required-configs` by default.
The mutex narrows the eligible config-string space; any future
REQUIRED_CONFIGS membership is a separate explicit PR.

**Kit / recommended posture.** `not-recommended` +
`not-kit-default`. The hardware-catalog `description` understates
the dual-DAC capacity recorded in the schematic; broadening the
description is a separate later PR and is not in scope for this
matrix.

**Cross-references.**
[`hardware/s360-312-r4-dac.md`](hardware/s360-312-r4-dac.md),
[`hardware/board-readiness-matrix.md` §S360-312](hardware/board-readiness-matrix.md#s360-312-sense360-dac),
[`hardware/package-readiness-matrix.md` §fan_gp8403.yaml](hardware/package-readiness-matrix.md#fan_gp8403yaml--s360-312),
[`product-readiness-matrix.md` §FanDAC / S360-312](product-readiness-matrix.md#fandac--s360-312),
[`webflash-exposure-readiness-matrix.md` §DAC / S360-312 WebFlash posture](webflash-exposure-readiness-matrix.md#dac--s360-312-webflash-posture).

## TRIAC / S360-320 release posture

**Current state.** The FanTRIAC reference product
[`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml)
and the blocked WebFlash wrapper
[`products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml)
both exist, but the catalog entry
`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` is `status: blocked`,
`blocker: HW-005`, `webflash_build_matrix: false`, with `notes`
edited by `PRODUCT-TRIAC-001` to record the advanced /
manual-warning candidate posture (notes-only; structural fields
unchanged; no new lifecycle enum). No FanTRIAC artifact has ever
been built, signed, attached, or imported. The TRIAC board has its
module-side schematic PDF committed at
[`hardware/schematics/S360-320-R4.pdf`](hardware/schematics/S360-320-R4.pdf)
under HW-ASSETS-003 but
[`hardware/s360-320-r4-triac.md`](hardware/s360-320-r4-triac.md)
status is `partial — schematic evidence available; package
reconciliation, timing validation, and compliance / certification
pending`. ESPHome `ac_dimmer` requires direct interrupt-capable
ESP32 GPIOs; the Core currently routes `TRI_GPIO1` / `TRI_GPIO2`
via the SX1509 expander, which the timing analysis rejects per
[`release-one-hardware-audit.md` §Timing constraint: `ac_dimmer` vs SX1509 expander](release-one-hardware-audit.md#timing-constraint-ac_dimmer-vs-sx1509-expander).
HW-005 is unresolved. COMPLIANCE-001 (mains-voltage UK / EU) is in
force.

**Allowed release action now.** `not-release-ready` +
`blocked-from-standard-release`. The blocked reference wrapper
stays exactly as it is. No promotion of the catalog entry off
`blocked`. No flip of `webflash_build_matrix` to `true`. No
build-matrix entry. **No release artifact.** No signing. No GitHub
Release. No checksums. No proof. No WebFlash import. No promotion
of FanTRIAC to `production` / `preview` / `compile-only` /
`hardware-pending` / `legacy-compatible` at any layer.

**`RELEASE-TRIAC-001` blocked after `PACKAGE-TRIAC-001`
deferral.** `RELEASE-TRIAC-001` is explicitly blocked while
`PACKAGE-TRIAC-001`, `PRODUCT-TRIAC-002`, and the in-repo
`WF-TRIAC-001` wrapper / catalog / build slice remain deferred.
No release artifact may be produced — no advanced-channel
`.bin`, no GitHub Release, no signing, no checksums, no
build-info `manifest.json`, no release-proof row — until those
upstream package / product / WebFlash gates clear. The runtime
advanced / manual-warning UX slice having landed in the
[`sense360store/WebFlash`](https://github.com/sense360store/WebFlash)
repo (also named `WF-TRIAC-001`) is UX-only; it does **not**
unblock release work in this repo. The next actionable FanTRIAC
work is evidence / compliance: `HW-005` direct-GPIO / timing
unblock, `HW-PINMAP-320-FOLLOWUP`, bench / waveform / real-load
proof, and `COMPLIANCE-001` advanced / manual-warning sign-off
— not release work. See
[`docs/cleanup-audit.md` §TRIAC-QUEUE-001 update](cleanup-audit.md#triac-queue-001-update-remaining-fantriac-chain-normalized-after-package-deferral).

**Future release class (policy-recorded by `PRODUCT-TRIAC-001`).**
`advanced/manual-warning-artifact-only` **only**. Reachable through
the release flow exclusively behind the advanced / manual-warning
UX gate (which is implemented in the WebFlash repo, not here, and
gated additionally by `COMPLIANCE-001`). **Never** stable. **Never**
on the standard WebFlash flasher landing list. **Never** in
`release_one_required_configs`. **Never** kit / default /
recommended. **Never** Release-One. **Not** compliance-certified —
the advanced / manual-warning posture is a release class, not a
certification claim; the COMPLIANCE-001 mains-voltage UK / EU
sign-off runs in addition.

The reach to a live `advanced/manual-warning-artifact-only`
artifact requires, in order: `PRODUCT-TRIAC-001` (**landed**:
notes-only catalog policy reclassification on
`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` recording the advanced /
manual-warning candidate posture; JSON `status: blocked` /
`blocker: HW-005` / `webflash_build_matrix: false` unchanged; no
new lifecycle enum) → `HW-005` unblock (S360-320 schematic-side
electrical / firmware-side timing reconciliation; per
[`release-one-hardware-audit.md` §FanTRIAC mapping resolution](release-one-hardware-audit.md#fantriac-mapping-resolution)) →
`HW-PINMAP-320-FOLLOWUP` (standalone schematic-backed reference
doc; J3 ↔ J15 reconciliation; `TRI_GPIO*` / `ESP_GPIO*` naming;
`ac_dimmer` ISR timing budget recomputation) → `PACKAGE-TRIAC-001`
(FanTRIAC package YAML reconciliation; timing-correctness verdict)
→ `PRODUCT-TRIAC-002` (FanTRIAC product YAML / catalog-entry
rework; preserve all mains-voltage warnings) → `COMPLIANCE-001`
advanced / manual-warning sign-off (UK / EU mains-voltage
compliance evidence; qualified-electrician acknowledgement; document
approval) → `WF-TRIAC-001` (advanced / manual-warning WebFlash
wrapper / catalog / build-matrix entry, behind the manual-warning
UX gate) → `RELEASE-TRIAC-001` (build the advanced-channel `.bin`;
sign;
attach to a dedicated advanced-warning-channel GitHub Release with
explicit non-standard release notes; record SHA256 + MD5 checksums
+ build-info `manifest.json`; record a separate advanced /
manual-warning proof row in
[`docs/webflash-release-proof.md`](webflash-release-proof.md)) →
`WF-IMPORT-TRIAC-001` (WebFlash-side import behind manual-warning
UX).

**Stable eligibility.** **`stable-not-approved` — never by
default.** Irrespective of any future product YAML existence,
catalog status flip, wrapper addition, build-matrix entry, release
artifact production, advanced / manual-warning sign-off, or
WebFlash import, FanTRIAC is **not** promoted to `production` /
`stable` by this matrix, by `RELEASE-TRIAC-001`, or by any future
routine release-side PR. Any future stable promotion would be a
separately scoped, explicit PR with explicit COMPLIANCE-001 stable
sign-off and the full
[`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
gauntlet; it is **not** authorised by this matrix.

**REQUIRED_CONFIGS posture.** **`not-required-configs` — never by
default.** Restated for clarity: irrespective of any future
product YAML existence, catalog status, wrapper, build-matrix
entry, release artifact, advanced / manual-warning sign-off, or
WebFlash import, FanTRIAC is not added to
`release_one_required_configs` by this matrix, by
`RELEASE-TRIAC-001`, or by `WF-TRIAC-001`. Any such addition is a
separate, explicit, scoped PR.

**Kit / recommended posture.** **`not-recommended` +
`not-kit-default` — never by default.** Mains-voltage advanced /
manual-warning products are categorically excluded from kit /
default / recommended surfaces, irrespective of any future product
/ wrapper / build / release / import existence.

**Cross-references.**
[`hardware/s360-320-r4-triac.md`](hardware/s360-320-r4-triac.md),
[`hardware/s360-320-r4-triac.md` Advanced / manual-warning product posture](hardware/s360-320-r4-triac.md#advanced--manual-warning-product-posture),
[`hardware/board-readiness-matrix.md` §S360-320](hardware/board-readiness-matrix.md#s360-320-sense360-triac),
[`hardware/package-readiness-matrix.md` §fan_triac.yaml](hardware/package-readiness-matrix.md#fan_triacyaml--s360-320),
[`product-readiness-matrix.md` §FanTRIAC / S360-320](product-readiness-matrix.md#fantriac--s360-320),
[`webflash-exposure-readiness-matrix.md` §TRIAC / S360-320 WebFlash posture](webflash-exposure-readiness-matrix.md#triac--s360-320-webflash-posture),
[`release-one-hardware-audit.md` §FanTRIAC mapping resolution](release-one-hardware-audit.md#fantriac-mapping-resolution),
[`compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md).

## Power / S360-400 release posture

**Current state.** No PWR-240V product YAML on the WebFlash track;
no PWR-240V WebFlash wrapper; no PWR-240V catalog entry; no
PWR-240V build-matrix row; no PWR-240V artifact. The four
`legacy-compatible` `*-pwr` Core variants
([`sense360-core-c-pwr.yaml`](../products/sense360-core-c-pwr.yaml),
[`sense360-core-v-c-pwr.yaml`](../products/sense360-core-v-c-pwr.yaml),
[`sense360-core-v-w-pwr.yaml`](../products/sense360-core-v-w-pwr.yaml),
[`sense360-core-w-pwr.yaml`](../products/sense360-core-w-pwr.yaml))
exist as pre-WebFlash YAMLs only and produce no release artifact;
they are `docs-only` / `legacy-only`. **The PWR-240V module-side
schematic PDF is committed under HW-ASSETS-400 (PR #514)** at
[`hardware/schematics/S360-400-R4.pdf`](hardware/schematics/S360-400-R4.pdf)
with curated artifact index at
[`hardware/artifacts/S360-400-R4.md`](hardware/artifacts/S360-400-R4.md).
HW-PINMAP-400-FOLLOWUP consumed both and promoted
[`hardware/s360-400-r4-power.md`](hardware/s360-400-r4-power.md)
from `pending — schematic / design evidence required` to
`partial — schematic evidence available; package reconciliation,
BOM, silkscreen, creepage/clearance, and COMPLIANCE-001 pending`;
release-side gating is **unchanged**.
COMPLIANCE-001 (mains-voltage UK / EU) is in force (last re-check
PR #506).

**Allowed release action now.** `not-release-ready`. No artifact
build, no signing, no GitHub Release, no checksums, no proof, no
WebFlash import. The four `legacy-compatible` `*-pwr` Core entries
stay `legacy-compatible` and continue to produce no release
artifact.

**Future release class (intent).** `preview-artifact-candidate` as
the default (advanced / manual-warning is **not** the default for
PWR-240V; `PRODUCT-POWER-400-001` / `WEBFLASH-POWER-400-001`
decide whether mains-voltage PWR-240V products are standard
preview-candidate, advanced / manual-warning-only, or both
depending on intended UX). Reach requires: `HW-ASSETS-400`
*(landed at PR #514)* → `HW-PINMAP-400-FOLLOWUP` *(this PR;
docs-only schematic-backed reconciliation; release row
unchanged)* → BOM cross-check + silkscreen + creepage / clearance
+ bench / load / thermal / EMI evidence (separate evidence-bearing
slices) → `PACKAGE-POWER-400-001` → `COMPLIANCE-001` S360-400
slice closure → `PRODUCT-POWER-400-001` → `WEBFLASH-POWER-400-001`
→ `RELEASE-POWER-400-001` (build / sign / attach the `.bin`;
release notes; checksums; proof row) → `WF-IMPORT-GAP-001`.

**Stable eligibility.** `not-stable-by-default`. Mains-voltage
compliance posture is gating-priority over any stable promotion;
the 17-row gauntlet applies in addition.
`operator-proof-required` + `release-proof-required`.

**REQUIRED_CONFIGS posture.** `not-required-configs` by default.

**Kit / recommended posture.** `not-recommended` +
`not-kit-default`. Compliance posture is gating-priority over the
exposure decision; kit / recommended membership is owned by
`PRODUCT-POWER-400-001`.

**Cross-references.**
[`hardware/s360-400-r4-power.md`](hardware/s360-400-r4-power.md),
[`hardware/board-readiness-matrix.md` §S360-400](hardware/board-readiness-matrix.md#s360-400-sense360-240v-psu),
[`hardware/package-readiness-matrix.md` §power_240v.yaml](hardware/package-readiness-matrix.md#power_240vyaml--s360-400),
[`product-readiness-matrix.md` §PWR-240V / S360-400](product-readiness-matrix.md#pwr-240v--s360-400),
[`webflash-exposure-readiness-matrix.md` §Power / S360-400 WebFlash posture](webflash-exposure-readiness-matrix.md#power--s360-400-webflash-posture),
[`compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md).

**2026-05-19 — `PRODUCT-POWER-400-001` investigation pass
(Path A docs-only deferral; release row unchanged).**
The upstream `PACKAGE-POWER-400-001` investigation pass merged as
**PR #520** on 2026-05-19 (docs-only Path A deferral) and the
downstream `PRODUCT-POWER-400-001` investigation pass ran on
2026-05-19 (this PR — docs-only Path A deferral). Re-verified
against the live files: no S360-400-explicit / `PWR`-bearing
WebFlash-shippable product YAML; no S360-400 product entry in
[`../config/product-catalog.json`](../config/product-catalog.json)
(four `legacy-compatible` `*-pwr` Core variants unchanged); no
`PWR` build in
[`../config/webflash-builds.json`](../config/webflash-builds.json);
no PWR-240V WebFlash wrapper, catalog entry, build-matrix entry,
artifact, or release tag. `RELEASE-POWER-400-001` stays
**blocked** behind `WEBFLASH-POWER-400-001` +
`PRODUCT-POWER-400-001` + `COMPLIANCE-001` `S360-400` slice
closure; `PRODUCT-POWER-400-001` itself stays blocked behind
`PACKAGE-POWER-400-001` implementation (PR #520 was docs-only
investigation only), BOM cross-check, `S360-400`
`schematic_status: verified` JSON PR, `COMPLIANCE-001` `S360-400`
slice, package / catalog reconciliation, and product-onboarding
approval. `not-release-ready` /
`missing-build-matrix` / `missing-webflash-wrapper` /
`missing-product-yaml` / `missing-package-readiness` all hold;
mains-voltage compliance posture is gating-priority over stable
promotion; `operator-proof-required` + `release-proof-required`
both apply. No package, product, WebFlash, build, release,
compliance, JSON catalog, test, script, workflow, component,
include, firmware, or manifest edits; no `schematic_status` /
`schematic_file` promotion; no `webflash_build_matrix` flip; no
artifact built / signed / attached; no release tag created; no
`REQUIRED_CONFIGS` / kit change. Release-One stays
`Ceiling-POE-VentIQ-RoomIQ` /
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` / tag
`v1.0.0`; LED preview stays
`Ceiling-POE-VentIQ-RoomIQ-LED` /
`Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`;
FanTRIAC stays `blocked` / `HW-005`. Investigation outcome
cross-recorded at
[`cleanup-audit.md` §`PRODUCT-POWER-400-001 update (2026-05-19 — docs-only investigation pass)`](cleanup-audit.md#product-power-400-001-update-2026-05-19--docs-only-investigation-pass),
[`product-readiness-matrix.md` §PWR-240V / S360-400](product-readiness-matrix.md#pwr-240v--s360-400),
and
[`webflash-exposure-readiness-matrix.md` §Power / S360-400 WebFlash posture](webflash-exposure-readiness-matrix.md#power--s360-400-webflash-posture).

## PoE / S360-410 release posture

**Current state.** No new PoE-410-explicit product YAML; no new
PoE-410-explicit WebFlash wrapper; no new PoE-410-explicit catalog
entry; no new PoE-410-explicit build-matrix row; no new PoE-410-explicit
artifact. Module-side schematic now **committed under HW-ASSETS-410
/ PR #516** at
[`docs/hardware/schematics/S360-410-R4.pdf`](hardware/schematics/S360-410-R4.pdf)
with curated artifact index at
[`docs/hardware/artifacts/S360-410-R4.md`](hardware/artifacts/S360-410-R4.md);
HW-PINMAP-410-FOLLOWUP has consumed both and promoted
[`docs/hardware/s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md) to
`partial — schematic evidence available; package reconciliation,
PoE PD controller / magnetics / buck / isolated DC/DC / harness
identity evidence pending`. The Release-One product
`Ceiling-POE-VentIQ-RoomIQ` and the LED preview
`Ceiling-POE-VentIQ-RoomIQ-LED` both consume S360-410 logically
under the existing schematic-pending caveat preserved in
[`release-one-hardware-audit.md` Findings → PoE PSU](release-one-hardware-audit.md#findings).
The Release-One stable artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` (tag
`v1.0.0`) and the LED preview artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` (tag
`v1.0.0-led-preview`) remain unchanged; this matrix does **not**
re-release, requalify, or re-stamp either artifact.

**Allowed release action now.** `not-release-ready` for any **new**
PoE-410 product entry. The existing Release-One and LED preview
release surface that consumes S360-410 is **not** affected:
Release-One catalog row stays `status: production`, `channel:
stable`, `webflash_build_matrix: true`, artifact unchanged, tag
`v1.0.0`. LED preview catalog row stays `status: preview`,
`channel: preview`, `webflash_build_matrix: true`, artifact
unchanged, tag `v1.0.0-led-preview`. No re-release. No
re-qualification.

**Future release class (intent).** `preview-artifact-candidate` as
the default **only if** a new PoE-410 product entry is warranted.
Per
[`product-readiness-matrix.md` §PoE-410 / S360-410](product-readiness-matrix.md#poe-410--s360-410),
the per-family `PRODUCT-POE-410-001` slice "often will close by
promoting Release-One's preserved schematic-pending caveat alone,
without adding a new product entry." If `PRODUCT-POE-410-001`
decides no new product entry is added, then
`WEBFLASH-POE-410-001` is not required, and `RELEASE-POE-410-001`
is not required, and the family closes at the existing Release-One
caveat without producing a new release artifact.

Reach to a new `preview-artifact-candidate`, if
`PRODUCT-POE-410-001` decides one is warranted, requires:
`HW-ASSETS-410` (PR #516) → `HW-PINMAP-410-FOLLOWUP` (this PR) →
BOM cross-check → `S360-100-BENCH-001` update /
`HW-002 OQ#6` closure → `S360-410` `schematic_status: verified`
JSON PR → `PACKAGE-POE-410-001` → `PRODUCT-POE-410-001` →
`WEBFLASH-POE-410-001` → `RELEASE-POE-410-001` →
`WF-IMPORT-GAP-001`.

**Stable eligibility.** Release-One's existing stable membership
is not touched. Any new PoE-410 product entry is
`not-stable-by-default`; the 17-row gauntlet applies in addition.

**REQUIRED_CONFIGS posture.** Release-One's existing
`release_one_required_configs: ["Ceiling-POE-VentIQ-RoomIQ"]`
membership is not touched. Any new PoE-410 product entry is
`not-required-configs` by default.

**Kit / recommended posture.** Release-One's existing kit /
recommended membership is not touched. Any new PoE-410 product
entry is `not-recommended` + `not-kit-default` by default; the
membership decision belongs to `PRODUCT-POE-410-001`.

**Cross-references.**
[`hardware/s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md),
[`hardware/board-readiness-matrix.md` §S360-410](hardware/board-readiness-matrix.md#s360-410-sense360-poe-psu),
[`hardware/package-readiness-matrix.md` §power_poe.yaml](hardware/package-readiness-matrix.md#power_poeyaml--s360-410),
[`product-readiness-matrix.md` §PoE-410 / S360-410](product-readiness-matrix.md#poe-410--s360-410),
[`webflash-exposure-readiness-matrix.md` §PoE / S360-410 WebFlash posture](webflash-exposure-readiness-matrix.md#poe--s360-410-webflash-posture),
[`release-one-hardware-audit.md` §Findings → PoE PSU](release-one-hardware-audit.md#findings).

## Release-One and LED preview safety

The Release-One production product and the LED preview product are
the two existing released artifacts in this repo (the Release-One
`v1.0.0` stable release and the RELEASE-005 `v1.0.0-led-preview`
prerelease). Both are explicitly preserved by this PR.

**Release-One — do not change.**

- Config string: `Ceiling-POE-VentIQ-RoomIQ`.
- Catalog entry: `status: production`, `channel: stable`,
  `version: 1.0.0`,
  `artifact_name: Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`,
  `webflash_wrapper: products/webflash/ceiling-poe-ventiq-roomiq.yaml`,
  `webflash_build_matrix: true`,
  `blocked_modules: ["FanTRIAC", "LED"]`,
  `hardware_status: verified-for-release-one`.
- Product YAML:
  [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml).
- WebFlash wrapper:
  [`products/webflash/ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml).
- Build-matrix row:
  [`config/webflash-builds.json`](../config/webflash-builds.json)
  Release-One entry (`channel: stable`, `version: 1.0.0`).
- `release_one_required_configs`:
  `["Ceiling-POE-VentIQ-RoomIQ"]`.
- GitHub Release tag: `v1.0.0`.
- Release artifact:
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`.
- Release-proof row:
  [`docs/webflash-release-proof.md`](webflash-release-proof.md)
  Release-One section.

RELEASE-GAP-001 does **not**:

- alter the Release-One product YAML, wrapper, catalog entry,
  build-matrix row, release artifact, checksums, release notes,
  release-proof row, or WebFlash-side import surface in any way,
- re-release, re-tag, re-stamp, or re-qualify Release-One,
- add any missing-module product (FanRelay / FanPWM / FanDAC /
  FanTRIAC / PWR-240V / PoE-410 new entry) to the Release-One
  config string,
- add any new `release_one_required_configs` member,
- change the `blocked_modules: ["FanTRIAC", "LED"]` list on the
  Release-One catalog entry,
- add a new kit / recommended bundle that references Release-One
  outside its current membership.

**LED preview — do not change.**

- Config string: `Ceiling-POE-VentIQ-RoomIQ-LED`.
- Catalog entry: `status: preview`, `channel: preview`,
  `version: 1.0.0`,
  `artifact_name: Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`,
  `webflash_wrapper: products/webflash/ceiling-poe-ventiq-roomiq-led.yaml`,
  `webflash_build_matrix: true`,
  `blocked_modules: ["FanTRIAC"]`,
  `hardware_status: verified-led-candidate`.
- Product YAML:
  [`products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq-led.yaml).
- WebFlash wrapper:
  [`products/webflash/ceiling-poe-ventiq-roomiq-led.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq-led.yaml).
- GitHub prerelease tag: `v1.0.0-led-preview` (marked
  `prerelease: true`; workflow derives `channel=preview`).
- Release artifact:
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`
  (1,135,904 bytes; SHA256
  `93310d2cbc27355e399f36a232336b6b9075dacfc178d603c7a92aa1089182d3`).
- Release-proof row:
  [`docs/webflash-release-proof.md`](webflash-release-proof.md)
  LED preview / RELEASE-005 section.

RELEASE-GAP-001 does **not**:

- promote the LED preview to `production` / `stable` — LED stable
  is owned by the separate `RELEASE-007` slice (reference-only in
  [Follow-up PR sequence](#follow-up-pr-sequence)) and gated by
  the 17-row
  [`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
  gauntlet,
- add LED to `release_one_required_configs`,
- add an LED-specific kit or recommended bundle entry,
- change the LED preview wrapper / catalog / build-matrix / release
  artifact / release notes / checksums / release-proof / WebFlash
  import surface in any way,
- re-release, re-tag, re-stamp, or re-qualify the LED preview
  artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`,
- add missing-module products (FanRelay / FanPWM / FanDAC /
  FanTRIAC) to the LED preview config string,
- close the bench-verification Open Questions in
  [`hardware/s360-300-r4-led.md`](hardware/s360-300-r4-led.md)
  (harness rail, LED count, harness identity, observed LED ring
  behaviour) or the bench-verification record
  [`S360-300-BENCH-001`](hardware/s360-300-r4-led.md#s360-300-bench-001-status) —
  these remain carried as preview-stage caveats and as the still
  -pending operator-proof / bench-evidence rows of the 17-row
  gauntlet.

LED's eventual promotion to `production` / `stable` is owned by
[`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
(17-row gauntlet, including row 9 `WF-HW-TEST-002` and row 10
`S360-300-BENCH-001`) plus the
[`product-led-preview-decision.md`](product-led-preview-decision.md)
record, and is explicitly **not** in scope for this matrix.

## Stable promotion policy

Stable promotion of any released artifact requires explicit
promotion gates. RELEASE-GAP-001 does **not** authorise any stable
promotion of any candidate family.

- **Preview-to-stable promotion is not automatic.** A successful
  preview build, attached release, recorded release-proof row, and
  even a recorded operator-proof container do **not** constitute
  stable promotion. Stable promotion requires every one of the 17
  gauntlet rows in
  [`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
  to be `done` or `accepted-waiver`. The gauntlet enumerates the
  upstream evidence (rows 1–4), preview floor (rows 5–8), and
  stable-only requirements (rows 9–17), and the production catalog
  / WebFlash diff that the eventual stable promotion PR applies.
- **LED stable promotion is owned by `RELEASE-007`, not by
  RELEASE-GAP-001.** LED's eventual promotion of
  `Ceiling-POE-VentIQ-RoomIQ-LED` from `preview` / `preview` to
  `production` / `stable` (artifact rename from
  `…-v1.0.0-preview.bin` to `…-v1.0.0-stable.bin`, tag bump from a
  `-led-preview` suffix to a plain `vX.Y.Z`, catalog flip from
  `preview` to `production`) is the responsibility of the separate
  `RELEASE-007` slice. Today rows 9–17 of the gauntlet remain
  `pending` or `decision needed`: `WF-HW-TEST-002` operator-proof
  container has not been filled by an operator; the
  [`S360-300-BENCH-001`](hardware/s360-300-r4-led.md#s360-300-bench-001-status)
  bench-verification record is `pending — bench hardware evidence
  required`; the three Open Questions in
  [`hardware/s360-300-r4-led.md`](hardware/s360-300-r4-led.md)
  (harness rail / LED count / harness identity) remain `verify`;
  no `channel=stable` LED release-notes draft has been generated;
  the production catalog promotion, stable build artifact, stable
  WebFlash import, REQUIRED_CONFIGS decision, kit / UI decision,
  and human approval rows are all `pending`. RELEASE-GAP-001 does
  **not** advance any of these. LED stable is **out-of-scope**.
- **Future Relay / PWM / DAC artifacts start as
  `preview-artifact-candidate`.** Each per-family `RELEASE-*-001`
  slice builds the family's first artifact on a non-`stable`
  channel (typically `preview`). The first stable promotion later
  requires the full 17-row gauntlet, including
  `operator-proof-required` and `release-proof-required`. No
  shortcut.
- **Advanced / manual-warning TRIAC artifacts must not become
  stable by default.** `RELEASE-TRIAC-001`, when it eventually
  lands, releases a `.bin` on a dedicated advanced /
  manual-warning channel — not on `stable`, not on `preview` for
  the standard landing list, not in `release_one_required_configs`,
  not in any kit / recommended / default surface. Any future
  stable promotion of FanTRIAC would be a separately-scoped,
  explicit PR with full COMPLIANCE-001 sign-off and the 17-row
  gauntlet; it is **not** authorised by this matrix.
- **PWR-240V stable promotion is gated additionally by
  COMPLIANCE-001.** Even after the upstream PRODUCT / WEBFLASH /
  RELEASE slices land for PWR-240V, the stable promotion requires
  the COMPLIANCE-001 mains-voltage UK / EU stable sign-off in
  addition to the 17-row gauntlet.
- **PoE-410 stable promotion is reserved for the existing
  Release-One caveat path.** Release-One's existing stable
  membership covers PoE-410 logically; any new PoE-410-explicit
  stable promotion requires its own PRODUCT / WEBFLASH / RELEASE
  slices to land first.

## REQUIRED_CONFIGS policy

`release_one_required_configs` in
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
is the WebFlash-side baseline site-health list. It is **not** the
list of every valid firmware artifact, **not** the list of every
WebFlash-shippable product, **not** the list of every released
artifact, and **not** the list of every recommended product. It is
the small set of configurations that WebFlash treats as required
for a fleet to count as healthy under the Release-One contract.

The policy (consistent with
[`webflash-exposure-readiness-matrix.md` §REQUIRED_CONFIGS policy](webflash-exposure-readiness-matrix.md#required_configs-policy)
and
[`preview-to-stable-promotion-gates.md` §REQUIRED_CONFIGS policy](preview-to-stable-promotion-gates.md#required_configs-policy)):

- **A release artifact does not imply REQUIRED_CONFIGS.**
  Producing a `.bin` for a configuration through the existing
  workflow does not add the configuration to
  `release_one_required_configs`. The two decisions are
  separately gated.
- **New preview artifacts are not REQUIRED_CONFIGS.** Adding a
  `preview-artifact-candidate` to the WebFlash build matrix and
  building / attaching the preview `.bin` does not add it to
  `release_one_required_configs`. Today this is enforced for
  `Ceiling-POE-VentIQ-RoomIQ-LED` (preview, in build matrix,
  artifact attached at `v1.0.0-led-preview`, **not** in
  `release_one_required_configs`).
- **Advanced / manual-warning artifacts are not REQUIRED_CONFIGS —
  ever by default.** Restated for clarity: irrespective of any
  future product YAML existence, wrapper, catalog status,
  build-matrix entry, signed release artifact, advanced /
  manual-warning sign-off, or WebFlash-side import, an advanced /
  manual-warning artifact is not added to
  `release_one_required_configs` by default. This applies
  categorically to FanTRIAC.
- **FanTRIAC is never REQUIRED_CONFIGS by default.** Restated
  again: irrespective of any future product / wrapper / catalog /
  build / release / import surface, FanTRIAC is not added to
  `release_one_required_configs` by this matrix, by
  `RELEASE-TRIAC-001`, by `WF-TRIAC-001`, or by
  `WF-IMPORT-TRIAC-001`. Any such addition is a separate,
  explicit, scoped PR with explicit COMPLIANCE-001 sign-off.
- **LED stable promotion is a separate decision.** Whether
  `Ceiling-POE-VentIQ-RoomIQ-LED`, after `RELEASE-007` eventually
  promotes it to stable, is ever added to
  `release_one_required_configs` is owned by
  [`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
  row 15 (REQUIRED_CONFIGS decision, separate) and the
  [`product-led-preview-decision.md`](product-led-preview-decision.md)
  record. RELEASE-GAP-001 does **not** move LED into
  `release_one_required_configs` and does not authorise such a
  move.
- **Any future REQUIRED_CONFIGS addition requires a separate
  explicit PR.** The PR must name the configuration, demonstrate
  stable-channel release-artifact existence + WebFlash-side
  import + 17-row gauntlet closure + (for mains-voltage products)
  COMPLIANCE-001 stable sign-off, and gate its membership on the
  explicit site-health argument. The PR is not implied by any
  preview-candidate addition, any advanced / manual-warning
  addition, any wrapper / catalog / build-matrix slice, or any
  release-artifact build.

## Kit / recommended release policy

Kit / recommended path exposure is **separate** from release
artifact existence and from WebFlash installability. A product can
have a release artifact without being kit / recommended; a product
can be kit / recommended without being in
`release_one_required_configs`. The three surfaces are
independent.

The policy (consistent with
[`webflash-exposure-readiness-matrix.md` §Kit / recommended path policy](webflash-exposure-readiness-matrix.md#kit--recommended-path-policy)
and
[`preview-to-stable-promotion-gates.md` §Kit policy](preview-to-stable-promotion-gates.md#kit-policy)):

- **Release artifact existence is separate from kit / recommended
  exposure.** A `preview-artifact-candidate` has a released `.bin`
  attached to a GitHub prerelease but is not added to kit /
  default / recommended surfaces by default.
- **A product can be released but not recommended.** The standard
  WebFlash flasher landing list, the recommended bundle, the kit
  list, and `release_one_required_configs` are four separate
  surfaces. Membership in one does not imply membership in any
  other.
- **Advanced / manual-warning artifacts must not be kit / default /
  recommended.** A family classified
  `advanced/manual-warning-artifact-only` is excluded from kit,
  default, and recommended surfaces categorically. This applies to
  FanTRIAC.
- **FanTRIAC must not be kit / default / recommended.** Restated
  for clarity: irrespective of any future product / wrapper /
  catalog / build / release / import surface, FanTRIAC is not
  added to kit / default / recommended surfaces (WebFlash-side
  `scripts/data/kits.json` etc.) by this matrix, by
  `RELEASE-TRIAC-001`, by `WF-TRIAC-001`, or by
  `WF-IMPORT-TRIAC-001`. Any such addition is a separate, explicit,
  scoped PR.
- **Relay / PWM / DAC need separate product / UX decisions before
  kit / recommended exposure.** Reaching
  `preview-artifact-candidate` does not authorise kit / recommended
  membership. The per-family slice PRs `PRODUCT-RELAY-001` /
  `PRODUCT-PWM-001` / `PRODUCT-DAC-001` decide kit / recommended
  exposure as a separate UX question, **after** the product YAML
  lands; the per-family release slices do not implicitly elevate
  kit / recommended membership.
- **PWR-240V kit / recommended decision is gated additionally by
  COMPLIANCE-001.** Even after `RELEASE-POWER-400-001` produces a
  PWR-240V artifact, kit / recommended membership requires the
  separate COMPLIANCE-001 mains-voltage UK / EU sign-off in
  addition to the PRODUCT-side UX decision.
- **Release-One's existing kit / recommended membership is not
  touched** by this matrix.
- **LED's kit / recommended decision is separate** and remains
  owned by
  [`product-led-preview-decision.md`](product-led-preview-decision.md)
  and the
  [`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
  row 16 (kit / UI decision, separate); this matrix does not move
  LED into a kit / default / recommended bundle.

## Release note / artifact / checksum gates

The release-time gates below sit inside the release-artifact axis
of the 14-step
[Core rule](#core-rule) chain. Each is a separate, named gate; no
per-family `RELEASE-*-001` slice may skip any of them.

| Sub-gate | What it adds | Where | Validated by |
|---|---|---|---|
| Product catalog entry | A row in [`config/product-catalog.json`](../config/product-catalog.json) with the chosen `status`, `channel`, `version`, `config_string`, `product_yaml`, `webflash_wrapper`, `artifact_name`, `webflash_build_matrix: true`, `modules` map, `blocked_modules` list where appropriate, `hardware` SKU map, and `hardware_status` label. Added by the upstream `WEBFLASH-*-001` slice. | [`config/product-catalog.json`](../config/product-catalog.json) | [`tests/test_product_catalog.py`](../tests/test_product_catalog.py), [`tests/test_product_catalog_consistency.py`](../tests/test_product_catalog_consistency.py), [`scripts/validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py). |
| Build-matrix entry | A row in [`config/webflash-builds.json`](../config/webflash-builds.json) with `config_string`, `product_yaml`, `artifact_name`, `channel`, `version`, `chip_family`, `hardware_requirements`, `features`. Added by the upstream `WEBFLASH-*-001` slice. | [`config/webflash-builds.json`](../config/webflash-builds.json) | [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py), [`tests/test_webflash_compatibility.py`](../tests/test_webflash_compatibility.py). |
| Artifact-name conformance | The build's `artifact_name` matches `Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin` per [`config/webflash-compatibility.json`](../config/webflash-compatibility.json) `artifact_pattern`. | The build matrix row's `artifact_name`. | [`tests/test_webflash_artifact_naming.py`](../tests/test_webflash_artifact_naming.py). |
| Release tag conformance | The release tag matches `vX.Y.Z` on `stable` and `vX.Y.Z-{suffix}` on a prerelease channel. | The GitHub Release tag. | [`scripts/derive_release_version_channel.py`](../scripts/derive_release_version_channel.py) (and [`tests/test_derive_release_version_channel.py`](../tests/test_derive_release_version_channel.py)). |
| Release notes generated | A draft release-notes body generated for the target `(config_string, version, channel)`; the `## Changelog` section human-edited when targeting `stable`; `blocked` / `legacy-compatible` / `deprecated` / `removed` entries refused; `preview` entries on `stable` refused. | The GitHub Release body. | [`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py), [`tests/test_generate_webflash_release_notes.py`](../tests/test_generate_webflash_release_notes.py). |
| Release notes valid | Four required H2 sections present (`## Overview`, `## Compatible Hardware`, `## What's in this build`, `## Changelog`), bullets present, filler text refused on `stable`. | The GitHub Release body. | [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py), [`tests/test_validate_webflash_release_notes.py`](../tests/test_validate_webflash_release_notes.py). |
| Artifact built | The `.bin` produced by ESPHome `2026.4.5` per the build matrix entry. | The release flow output. | [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml) build / rename / attach. |
| SHA256 + MD5 checksums attached | `checksums-sha256.txt` and `checksums-md5.txt` attached to the GitHub Release. | The GitHub Release assets. | [`scripts/check-webflash-release-assets.py`](../scripts/check-webflash-release-assets.py) (the four-asset gate). |
| Build-info `manifest.json` attached | The build-info manifest (this is **not** the WebFlash production manifest) attached as the fourth asset. | The GitHub Release assets. | [`scripts/check-webflash-release-assets.py`](../scripts/check-webflash-release-assets.py). |
| Release proof recorded | A proof row recorded in [`docs/webflash-release-proof.md`](webflash-release-proof.md) with tag, run URL, asset size, SHA256, gate pass states, WebFlash import source URL. | [`docs/webflash-release-proof.md`](webflash-release-proof.md). | Manual review by the slice's reviewer; cross-referenced from per-family slice PR description. |
| WebFlash import-readiness | The artifact is importable into the WebFlash repo's `manifest.json` / `firmware-N.json` per [`docs/webflash-release-handoff.md`](webflash-release-handoff.md). | WebFlash-side `firmware/sources.json`. | WebFlash-side validators; the release-handoff record is the proof. |

Compatibility-grammar conformance —
`canonical_mounting` / `canonical_power` / `canonical_modules` /
`forbidden_tokens` / mutex rules / fan-driver `max-one-of` /
`fandac_conflicts_with_airiq` — remains an additional gate,
validated by
[`tests/test_webflash_compatibility.py`](../tests/test_webflash_compatibility.py)
against
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json).
RELEASE-GAP-001 adds no new `canonical_modules` token, no new
`forbidden_tokens` entry, and no relaxation of any mutex /
`max-one-of` rule.

## Operator proof gates

Operator / human-flash proof is required before any stable
promotion of any family. It is **not** required for a
`preview-artifact-candidate` build; it **is** required for a
stable promotion via the
[`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
17-row gauntlet (row 9), in addition to the hardware bench
verification (row 10) where applicable.

| Family | Operator-proof container | Bench-verification record | Status today |
|---|---|---|---|
| Release-One (`Ceiling-POE-VentIQ-RoomIQ`) | Filled (per the original v1.0.0 release proof in [`docs/webflash-release-proof.md`](webflash-release-proof.md)) | Hardware-bench coverage carried by Release-One audit per [`release-one-hardware-audit.md`](release-one-hardware-audit.md) | **done** for stable. |
| LED preview (`Ceiling-POE-VentIQ-RoomIQ-LED`) | `WF-HW-TEST-002` (WebFlash repo) | [`S360-300-BENCH-001`](hardware/s360-300-r4-led.md#s360-300-bench-001-status) | **pending — bench hardware evidence required**; `WF-HW-TEST-002` container exists but has not been filled by an operator; required by `RELEASE-007` (not by RELEASE-GAP-001). |
| FanRelay / S360-310 | Family-specific `WF-HW-TEST-*` (future; created with `WEBFLASH-RELAY-001` / `RELEASE-RELAY-001`) | Family-specific `S360-310-BENCH-*` (future; required for stable promotion) | `not-applicable-yet`; family is `not-release-ready`. |
| FanPWM / S360-311 | Family-specific `WF-HW-TEST-*` (future) | Family-specific `S360-311-BENCH-*` (future) | `not-applicable-yet`; `not-release-ready`. |
| FanDAC / S360-312 | Family-specific `WF-HW-TEST-*` (future) | Family-specific `S360-312-BENCH-*` (future) | `not-applicable-yet`; `not-release-ready`. |
| FanTRIAC / S360-320 | Family-specific advanced / manual-warning `WF-HW-TEST-*` (future; created with `WF-TRIAC-001` / `RELEASE-TRIAC-001`); requires additional timing / real-load / compliance warnings | Family-specific `S360-320-BENCH-*` (future; required even for advanced / manual-warning release because of mains-voltage timing-correctness requirements) | `not-applicable-yet`; `not-release-ready` + `blocked-from-standard-release`. |
| PWR-240V / S360-400 | Family-specific `WF-HW-TEST-*` (future) | Family-specific `S360-400-BENCH-*` (future); COMPLIANCE-001 mains-voltage evidence required | `not-applicable-yet`; `not-release-ready`. |
| PoE-410 / S360-410 | Release-One's existing operator-proof coverage applies to the existing Release-One PoE consumption; any new PoE-410-explicit family-specific container is `future` | Family-specific `S360-410-BENCH-*` (future, if a new product entry is added) | `not-applicable-yet` for any new entry. |

The rules:

- **`operator-proof-required` is a stable-promotion gate, not a
  preview-build gate.** A `RELEASE-*-001` slice may build,
  attach, and prove a preview artifact without an operator-proof
  container. The container becomes mandatory when the slice
  attempts a stable promotion via the 17-row gauntlet.
- **TRIAC requires additional timing / real-load / compliance
  warnings.** Even the advanced / manual-warning release flow
  (which never reaches `stable`) requires bench-evidence of
  zero-cross detection, gate timing, real-load behaviour, and
  thermal / safety review per
  [`hardware/s360-320-r4-triac.md`](hardware/s360-320-r4-triac.md);
  the advanced / manual-warning UX must carry the qualified-electrician
  acknowledgement.
- **Operator proof is recorded in WebFlash, not here.** This repo
  only records (a) the release-side proof in
  [`docs/webflash-release-proof.md`](webflash-release-proof.md) and
  (b) the bench-verification record under
  [`docs/hardware/`](hardware/). The WebFlash-side operator-proof
  container is the WebFlash repo's responsibility.

## Follow-up PR sequence

Each entry below is a separate PR with its own scope, review, and
gate evidence. RELEASE-GAP-001 does not commit to a calendar and
does not order these beyond the dependencies recorded in
[`hardware/board-readiness-matrix.md` Follow-up PR sequence](hardware/board-readiness-matrix.md#follow-up-pr-sequence),
[`hardware/package-readiness-matrix.md` Follow-up PR sequence](hardware/package-readiness-matrix.md#follow-up-pr-sequence),
[`product-readiness-matrix.md` Follow-up PR sequence](product-readiness-matrix.md#follow-up-pr-sequence),
[`webflash-exposure-readiness-matrix.md` Follow-up PR sequence](webflash-exposure-readiness-matrix.md#follow-up-pr-sequence),
and the per-board audit docs.

| PR | Purpose | Gated on |
|---|---|---|
| **`RELEASE-RELAY-001`** (alias: `RELEASE-GAP-001` FanRelay slice) | Build, sign, attach, and record proof for the first FanRelay release artifact on a non-`stable` channel (typically `preview`). Uses the existing [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml) flow. Generates release notes via [`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py); validates against [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py); validates assets via [`scripts/check-webflash-release-assets.py`](../scripts/check-webflash-release-assets.py); records the proof row in [`docs/webflash-release-proof.md`](webflash-release-proof.md). Honours `preview-artifact-candidate` class; not `release_one_required_configs`, not kit / recommended. | `WEBFLASH-RELAY-001` landed (wrapper + catalog entry + build-matrix row added). |
| **`RELEASE-PWM-001`** (alias: `RELEASE-GAP-001` FanPWM slice) | Same as above for FanPWM. The legacy four-channel [`products/sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml) retention / migration / removal decision (decided in `PRODUCT-PWM-001`) stays separate; the legacy entry produces no new release artifact. | `WEBFLASH-PWM-001` landed. |
| **`RELEASE-DAC-001`** (alias: `RELEASE-GAP-001` FanDAC slice) | Same as above for FanDAC. Enforce the `fandac_conflicts_with_airiq` mutex; no AirIQ-bearing FanDAC artifact is built or released. | `WEBFLASH-DAC-001` landed. |
| **`RELEASE-TRIAC-001`** | Build, sign, attach, and record proof for the FanTRIAC artifact on a dedicated advanced / manual-warning channel — **not** `stable`, **not** the standard `preview` landing list. Requires explicit non-standard release notes carrying the qualified-electrician / mains-voltage / non-certified language. Records a separate advanced / manual-warning proof row in [`docs/webflash-release-proof.md`](webflash-release-proof.md). **Separate** from the standard `RELEASE-*-001` flow because of the advanced / manual-warning posture. Not `stable`, not `release_one_required_configs`, not kit / default / recommended, not compliance-certified by virtue of having a release artifact. | `WF-TRIAC-001` landed + `COMPLIANCE-001` advanced / manual-warning sign-off + WebFlash-side manual-warning UX implemented + explicit human approval per the per-family slice's review. |
| **`RELEASE-POWER-400-001`** (alias: `RELEASE-GAP-001` PWR-240V slice) | Same as above for PWR-240V. UX class (standard preview vs advanced / manual-warning) decided per the `PRODUCT-POWER-400-001` / `WEBFLASH-POWER-400-001` compliance verdict. Mains-voltage compliance posture is gating-priority over stable promotion. | `WEBFLASH-POWER-400-001` landed + `COMPLIANCE-001` `S360-400` slice closed. |
| **`RELEASE-POE-410-001`** (alias: `RELEASE-GAP-001` PoE-410 slice) | **If and only if** `PRODUCT-POE-410-001` and `WEBFLASH-POE-410-001` add a new PoE-410-explicit product entry, build the corresponding artifact. Often this slice is not required because the PoE-410 family closes by extending the Release-One caveat without adding a new product. | `WEBFLASH-POE-410-001` landed + new product entry added (else: not required). |
| **`RELEASE-007`** (reference-only here) | **Out-of-scope for RELEASE-GAP-001.** Owned by [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md). LED stable release-candidate prep: promote `Ceiling-POE-VentIQ-RoomIQ-LED` from `preview` / `preview` to `production` / `stable`; rename the artifact from `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` to `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-stable.bin`; tag a plain `vX.Y.Z` (no `-led-preview` suffix); promote the catalog `channel` from `preview` to `stable`. **Not folded into RELEASE-GAP-001.** | Full 17-row [`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md) gauntlet closure, including `WF-HW-TEST-002` operator proof, [`S360-300-BENCH-001`](hardware/s360-300-r4-led.md#s360-300-bench-001-status) bench verification, and the production-catalog / WebFlash-builds promotion diff in [`preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md). |
| **`WF-IMPORT-GAP-001`** | Import the signed artifacts produced by `RELEASE-RELAY-001` / `RELEASE-PWM-001` / `RELEASE-DAC-001` / `RELEASE-POWER-400-001` / `RELEASE-POE-410-001` into the WebFlash repo's `manifest.json` / `firmware-N.json` per [`docs/webflash-release-handoff.md`](webflash-release-handoff.md). Owned by the WebFlash repo, not this repo. | The relevant `RELEASE-*-001` slice landed and the proof row recorded. |
| **`WF-IMPORT-TRIAC-001`** | Import the FanTRIAC artifact produced by `RELEASE-TRIAC-001` into the WebFlash repo behind the advanced / manual-warning UX. Separate from `WF-IMPORT-GAP-001` because of the advanced / manual-warning posture. | `RELEASE-TRIAC-001` landed and the advanced / manual-warning proof row recorded. |

None of these PRs is approved or scoped by RELEASE-GAP-001 itself.
They are recorded so the matrix has a clear next-action chain.

## Do-not-change guardrails

RELEASE-GAP-001 — this matrix — performs **none** of the following.
Anyone reading this matrix looking for justification to change one
of them must use a separate, scoped PR with its own gate evidence.

- No firmware regenerated, signed, attached, or imported. No
  GitHub Release created, retitled, retagged, or modified. No
  re-release, re-qualification, or re-stamp of any existing
  release artifact, including the Release-One `v1.0.0` release and
  the LED preview `v1.0.0-led-preview` prerelease.
- No edits to any workflow under
  [`.github/workflows/`](../.github/workflows/) —
  [`firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml),
  [`release-notes-draft.yml`](../.github/workflows/release-notes-draft.yml),
  [`validate.yml`](../.github/workflows/validate.yml), and
  [`ci-validate-configs.yml`](../.github/workflows/ci-validate-configs.yml)
  all stay verbatim.
- No edits to any release-time script under
  [`scripts/`](../scripts/) —
  [`derive_release_version_channel.py`](../scripts/derive_release_version_channel.py),
  [`generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py),
  [`validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py),
  [`check-webflash-release-assets.py`](../scripts/check-webflash-release-assets.py),
  [`validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py),
  [`product_name_mapper.py`](../scripts/product_name_mapper.py),
  [`scaffold_product.py`](../scripts/scaffold_product.py), and
  [`check-no-tracked-secrets.py`](../scripts/check-no-tracked-secrets.py)
  all stay verbatim.
- No edits to any test under
  [`tests/`](../tests/) — every release-time validator stays
  verbatim.
- No edits to any WebFlash wrapper under
  [`products/webflash/`](../products/webflash/) — the production
  [`ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml),
  the LED preview
  [`ceiling-poe-ventiq-roomiq-led.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq-led.yaml),
  and the blocked reference
  [`ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml)
  all stay verbatim. **No new wrapper is added.**
- No edits to any product YAML under
  [`products/`](../products/) — including all three current
  catalog-tracked entries
  ([`sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml),
  [`sense360-ceiling-poe-ventiq-roomiq-led.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq-led.yaml),
  [`sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml))
  and all 31 `legacy-compatible` entries. **No new product YAML is
  added.**
- No edits to any package YAML under
  [`packages/`](../packages/). The six fan-driver / power packages,
  the Core abstract packages, the legacy four-channel package, and
  the SX1509 expander package all stay verbatim.
- No edits to
  [`config/hardware-catalog.json`](../config/hardware-catalog.json),
  [`config/product-catalog.json`](../config/product-catalog.json),
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  or
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json).
  No new product entry, no new `lifecycle_statuses` value, no new
  `canonical_modules` token, no new `forbidden_tokens` entry, no
  new `release_one_required_configs` membership, no new
  build-matrix entry, no `webflash_build_matrix` flip, no
  compatibility rule relaxation, no mutex change, no channel
  change, no version bump, no `artifact_name` change.
- No edits to any component under [`components/`](../components/),
  any include under [`include/`](../include/), or any firmware
  artifact under `firmware/` (including `firmware/sources.json`
  and `manifest.json`).
- No firmware regenerated, no firmware signed, no GitHub Release
  created or modified, no checksums recorded, no
  build-info `manifest.json` regenerated, no release-proof row
  added or modified in
  [`docs/webflash-release-proof.md`](webflash-release-proof.md),
  no WebFlash import performed, no WebFlash-side `manifest.json` /
  `firmware-N.json` / `scripts/data/kits.json` /
  `firmware/sources.json` edit attempted.
- No change to the Release-One configuration `Ceiling-POE-VentIQ-RoomIQ`
  (`status: production`, `channel: stable`, version `1.0.0`,
  artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`,
  tag `v1.0.0`,
  `release_one_required_configs: ["Ceiling-POE-VentIQ-RoomIQ"]`).
- No change to the LED preview `Ceiling-POE-VentIQ-RoomIQ-LED`
  (stays `status: preview`, `channel: preview`, version `1.0.0`,
  artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`,
  tag `v1.0.0-led-preview`,
  `blocked_modules: ["FanTRIAC"]`). No promotion to `production` /
  `stable`. No addition to `release_one_required_configs`. No kit
  added. **LED stable promotion is owned by `RELEASE-007`, not by
  RELEASE-GAP-001.**
- No change to the FanTRIAC reference
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` (stays `status: blocked`,
  `blocker: HW-005`, `webflash_build_matrix: false`). FanTRIAC
  stays `stable-not-approved` + `blocked-from-standard-release` +
  `not-required-configs` + `not-recommended` + `not-kit-default`.
- No change to the mains-voltage compliance status of `S360-320`
  or `S360-400` (owned by COMPLIANCE-001;
  [`compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)).
- No addition of any candidate family (FanRelay / FanPWM / FanDAC
  / FanTRIAC release-side / PWR-240V / PoE-410 new entry) to
  `release_one_required_configs`, to kit / default surfaces, to
  recommended surfaces, or to Release-One.
- No resolution of the Core J10 vs RoomIQ J6 pin-order open
  question (owned by HW-009 + the per-board audit follow-ups).
- No resolution of the systemic Core abstract-bus mismatch
  (`CORE-ABSTRACT-BUS-001`; owned by
  [`release-one-hardware-audit.md`](release-one-hardware-audit.md)
  Required follow-ups #2 / #3).
- No removal or deprecation of any `legacy-compatible` entry; the
  31 `legacy-compatible` entries stay `legacy-compatible`. Removal
  is owned by
  [`product-deprecation-removal-policy.md`](product-deprecation-removal-policy.md)
  and `PRODUCT-DEP-001`.
- No closure of the bench-verification Open Questions in
  [`hardware/s360-300-r4-led.md`](hardware/s360-300-r4-led.md)
  or the
  [`S360-300-BENCH-001`](hardware/s360-300-r4-led.md#s360-300-bench-001-status)
  record.
- No filling of the WebFlash-side `WF-HW-TEST-002` LED
  operator-proof container (owned by WebFlash, not by this repo).

## Validation

RELEASE-GAP-001 is documentation-only and runs only the docs-safe
validators. Every validator must continue to pass without any
configuration / product / package / wrapper / build / release /
workflow / script / test edit.

### Test commands

```text
python3 tests/test_hardware_catalog.py
python3 tests/test_product_catalog.py
python3 tests/test_product_catalog_consistency.py
python3 tests/validate_webflash_builds.py
python3 tests/test_webflash_compatibility.py
python3 tests/test_webflash_artifact_naming.py
python3 tests/test_validate_webflash_release_notes.py
python3 tests/test_generate_webflash_release_notes.py
python3 tests/test_product_substitutions.py
python3 tests/test_release_one_entity_names.py
python3 tests/validate_configs.py
python3 tests/test_led_package_mapping.py
```

### Diff expectations

```text
git diff products products/webflash packages config scripts tests \
        .github/workflows components include firmware
```

Expected: **empty**. RELEASE-GAP-001 changes none of these paths.

The full PR diff is limited to:

- `docs/release-artifact-readiness-matrix.md` (new file)
- `docs/product-readiness-matrix.md` (one See-also entry added)
- `docs/webflash-exposure-readiness-matrix.md` (one See-also
  entry added)
- `docs/preview-to-stable-promotion-gates.md` (one See-also entry
  added)
- `docs/cleanup-audit.md` (one classification row added)

### Sanity-grep expectations

```text
grep -RIn "RELEASE-GAP-001|release-artifact-readiness|not-release-ready|missing-build-matrix|preview-artifact-candidate|advanced/manual-warning-artifact-only|stable-not-approved|not-required-configs|not-recommended|not-kit-default|operator-proof-required|FanRelay|FanPWM|FanDAC|FanTRIAC|S360-310|S360-311|S360-312|S360-320|S360-400|S360-410" \
     docs config products products/webflash packages tests
```

Expected:

- `RELEASE-GAP-001` appears in
  `docs/release-artifact-readiness-matrix.md`,
  `docs/product-readiness-matrix.md`,
  `docs/webflash-exposure-readiness-matrix.md`,
  `docs/preview-to-stable-promotion-gates.md`,
  `docs/cleanup-audit.md`, plus the pre-existing references in
  `docs/hardware/board-readiness-matrix.md` and
  `docs/hardware/package-readiness-matrix.md`.
- `release-artifact-readiness` appears in
  `docs/release-artifact-readiness-matrix.md` and in cross-link
  destinations in
  `docs/product-readiness-matrix.md`,
  `docs/webflash-exposure-readiness-matrix.md`,
  `docs/preview-to-stable-promotion-gates.md`, and
  `docs/cleanup-audit.md`.
- The new policy labels (`not-release-ready`,
  `missing-build-matrix`, `preview-artifact-candidate`,
  `advanced/manual-warning-artifact-only`, `stable-not-approved`,
  `operator-proof-required`, `release-proof-required`) appear
  only in `docs/release-artifact-readiness-matrix.md` plus the
  pre-existing additive qualifier usage of
  `not-required-configs` / `not-recommended` / `not-kit-default`
  in `docs/product-readiness-matrix.md` and
  `docs/webflash-exposure-readiness-matrix.md`.
- `advanced/manual-warning` continues to appear in the existing
  docs (`docs/product-readiness-matrix.md`,
  `docs/hardware/s360-320-r4-triac.md`,
  `docs/webflash-exposure-readiness-matrix.md`, etc.) plus the new
  matrix.
- `FanRelay` / `FanPWM` / `FanDAC` / `FanTRIAC` and `S360-310` /
  `S360-311` / `S360-312` / `S360-320` / `S360-400` / `S360-410`
  continue to appear in the existing docs / configs / packages and
  in the new matrix.
- No new occurrences of any of the above tokens appear under
  `products`, `products/webflash`, `packages`, `config`,
  `scripts`, `tests`, or `.github/workflows`.

## See also

- [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md)
  — WEBFLASH-GAP-001 WebFlash-layer exposure readiness gate.
  Upstream of this matrix: classifies per-family WebFlash exposure
  (wrapper / catalog / build-matrix / release / import) for the
  same FanRelay / FanPWM / FanDAC / FanTRIAC / PWR-240V / PoE-410
  candidate families. Documentation only.
- [`docs/product-readiness-matrix.md`](product-readiness-matrix.md)
  — PRODUCT-GAP-001 product-level readiness gate. Two layers
  upstream. Source of truth for the per-family product YAML
  existence column. Documentation only.
- [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
  — PACKAGE-GAP-001 package-level readiness gate. Three layers
  upstream. Source of truth for the per-family package readiness
  column. Documentation only.
- [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
  — HW-GAP-001 board-level readiness matrix. Four layers
  upstream. Records the per-board hardware-evidence axis this
  matrix consumes for the "missing-hardware-evidence" cause label.
- [`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md)
  — PRODUCT-AVAIL-001 cross-cutting product availability taxonomy.
  Maps this matrix's release-class labels onto the cross-cutting
  13-rung ladder (`release-artifact-ready` / `webflash-imported` /
  `webflash-live-preview` / `webflash-live-stable` /
  `production-required` / `kit-exposed`) without changing any
  JSON enum.
- [`docs/product-onboarding.md`](product-onboarding.md) —
  PRODUCT-004 ordered safe sequence for adding any new product /
  config. Every future per-family `PRODUCT-*-001` slice must
  clear the onboarding gates before a `WEBFLASH-*-001` slice can
  add the wrapper / catalog / build-matrix, which in turn gates
  the matching `RELEASE-*-001` slice in this matrix.
- [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
  — RELEASE-006 canonical 17-row preview-to-stable promotion
  gate. Applies to any future stable promotion arising from a
  per-family `RELEASE-*-001` slice; not bypassed by RELEASE-GAP-001.
  Owns the `RELEASE-007` LED stable path that this matrix
  references-only.
- [`docs/product-led-preview-decision.md`](product-led-preview-decision.md)
  — PRODUCT-009 LED preview decision record. Owns any future
  stable promotion of `Ceiling-POE-VentIQ-RoomIQ-LED`; not
  bypassed by RELEASE-GAP-001.
- [`docs/product-deprecation-removal-policy.md`](product-deprecation-removal-policy.md)
  — PRODUCT-DEP-001 deprecation / removal policy. Owns any future
  retirement of `legacy-compatible` entries; RELEASE-GAP-001 does
  not deprecate or remove any entry.
- [`docs/release-one.md`](release-one.md) — Release-One overview.
  Source of truth for the Release-One configuration / artifact /
  tag that RELEASE-GAP-001 leaves unchanged.
- [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)
  — Release-One firmware-vs-schematic audit; source of truth for
  the HW-005 FanTRIAC blocker, the systemic Core abstract-bus
  rebind (CORE-ABSTRACT-BUS-001), and the `S360-410` PoE PSU
  schematic-pending caveat.
- [`docs/webflash-contract.md`](webflash-contract.md) — canonical
  WebFlash artifact / grammar / token contract; the
  `artifact_pattern`, `allowed_channels`, `production_channel`,
  and `rescue_config_string` values bound this matrix's
  release-class enumeration.
- [`docs/webflash-release-handoff.md`](webflash-release-handoff.md)
  — WebFlash-side import handoff record format. Owned by the
  WebFlash repo for `WF-IMPORT-GAP-001` / `WF-IMPORT-TRIAC-001`.
- [`docs/webflash-release-proof.md`](webflash-release-proof.md)
  — Release-One release-proof record plus RELEASE-005 LED preview
  proof. Reference shape for any future per-family release proof
  row produced by `RELEASE-RELAY-001` / `RELEASE-PWM-001` /
  `RELEASE-DAC-001` / `RELEASE-TRIAC-001` /
  `RELEASE-POWER-400-001` / `RELEASE-POE-410-001`.
- [`docs/webflash-ci-alignment.md`](webflash-ci-alignment.md) —
  CI ↔ WebFlash alignment record. Clarifies the build-info
  `manifest.json` (attached to GitHub Releases) vs the WebFlash
  production `manifest.json` (deployed by WebFlash) distinction.
- [`docs/webflash-compatibility-taxonomy-audit.md`](webflash-compatibility-taxonomy-audit.md)
  — Audit of the WebFlash compatibility taxonomy; bounds any
  future grammar / token changes that per-family release slices
  may need to request (which are out of scope for this matrix).
- [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
  — COMPLIANCE-001 mains-voltage UK / EU compliance tracker;
  additional gate for any release-side work consuming `S360-320`
  (FanTRIAC) or `S360-400` (240v PSU). PoE is SELV and is not in
  scope.
- [`docs/hardware/s360-310-r4-relay.md`](hardware/s360-310-r4-relay.md),
  [`docs/hardware/s360-311-r4-pwm.md`](hardware/s360-311-r4-pwm.md),
  [`docs/hardware/s360-312-r4-dac.md`](hardware/s360-312-r4-dac.md),
  [`docs/hardware/s360-320-r4-triac.md`](hardware/s360-320-r4-triac.md),
  [`docs/hardware/s360-400-r4-power.md`](hardware/s360-400-r4-power.md),
  [`docs/hardware/s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md)
  — per-board pin / package mapping audit docs; sources of truth
  for the per-family release posture sections.
- [`docs/hardware/s360-300-r4-led.md`](hardware/s360-300-r4-led.md)
  — Sense360 LED schematic-backed reference; carries the
  bench-verification record
  [`S360-300-BENCH-001`](hardware/s360-300-r4-led.md#s360-300-bench-001-status)
  that LED stable promotion (`RELEASE-007`) depends on.
- [`docs/cleanup-audit.md`](cleanup-audit.md) — classification of
  stale / current / blocked-reference / legacy-compatible repo
  content; carries the RELEASE-GAP-001 registration row.
- [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)
  — canonical build / release workflow. Existing implementation
  surface that future `RELEASE-*-001` slices reuse without
  modification.
- [`.github/workflows/release-notes-draft.yml`](../.github/workflows/release-notes-draft.yml)
  — release-notes drafter workflow. Existing implementation
  surface; not modified by this matrix.
- [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  — machine-readable hardware catalog. `schematic_status` stays
  `cataloged_unverified` for `S360-310`, `S360-311`, `S360-312`,
  `S360-320`, `S360-400`, `S360-410`. RELEASE-GAP-001 changes
  none of these values.
- [`config/product-catalog.json`](../config/product-catalog.json)
  — machine-readable product catalog. Release-One is
  `status: production`; LED preview is `status: preview`;
  FanTRIAC variant is `status: blocked`, `blocker: HW-005`; the
  31 `legacy-compatible` entries stay `legacy-compatible`.
- [`config/webflash-builds.json`](../config/webflash-builds.json)
  — WebFlash build matrix; contains the two existing builds
  (`Ceiling-POE-VentIQ-RoomIQ` stable;
  `Ceiling-POE-VentIQ-RoomIQ-LED` preview) only.
- [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  — WebFlash compatibility grammar; source of truth for the
  `artifact_pattern`, `allowed_channels`,
  `production_channel: stable`, `rescue_config_string: "Rescue"`,
  and `release_one_required_configs: ["Ceiling-POE-VentIQ-RoomIQ"]`
  values this matrix's release-class enumeration consumes.

# Preview-to-Stable Promotion Gates (RELEASE-006)

## Purpose and scope

This document is the canonical, cross-cutting policy for promoting a
**preview** WebFlash product/build to **stable / production** in this
repository's WebFlash track. It defines what evidence, tests, release
artefacts, WebFlash-side state, and human sign-offs must exist before a
preview entry is allowed to flip to `status: production` on `channel:
stable`.

This document is **documentation only**. It does not:

- promote any product to `production` or `stable`,
- modify any entry in
  [`config/product-catalog.json`](../config/product-catalog.json),
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
  or [`config/hardware-catalog.json`](../config/hardware-catalog.json),
- modify any product YAML, WebFlash wrapper, or package YAML,
- modify any workflow under `.github/workflows/`, any script under
  `scripts/`, any test under `tests/`, any component under
  `components/`, or any include under `include/`,
- generate, regenerate, sign, import, deploy, or otherwise produce
  firmware,
- change the lifecycle of `Ceiling-POE-VentIQ-RoomIQ-LED` (the LED
  preview catalog entry stays `status: preview`, `channel: preview`),
- change the Release-One product `Ceiling-POE-VentIQ-RoomIQ`, its
  artifact name `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`,
  or its tag `v1.0.0`,
- unblock FanTRIAC (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays
  `status: blocked`, `blocker: HW-005`,
  `webflash_build_matrix: false`),
- add or remove any entry from WebFlash-side
  `REQUIRED_CONFIGS`, `kits.json`, `firmware/sources.json`, or
  `manifest.json` — those are WebFlash-owned and are not touched by
  this repo,
- change the mains-voltage compliance status for `S360-400` /
  `S360-320`.

The intended audience is maintainers preparing a future preview
product for stable promotion (today this is the LED preview; tomorrow
it may be an AirIQ-bearing, FanRelay-bearing, or PWR-bearing variant),
and operators / reviewers asked to sign off on a stable promotion.

If this document and any source-of-truth document drift, **the
source-of-truth document wins** and this document must be updated.
The sources of truth are listed in [See also](#see-also).

## Definitions

| Term | Meaning |
|---|---|
| **Channel** | Build-matrix release channel as enumerated in [`config/webflash-compatibility.json`](../config/webflash-compatibility.json). Today: `stable`, `beta`, `preview`, `dev`, `rescue`. Stable promotion always lands on `stable`. |
| **Lifecycle status** | Catalog status per [`config/product-catalog.json`](../config/product-catalog.json) `lifecycle_statuses`: `production`, `preview`, `compile-only`, `hardware-pending`, `blocked`, `legacy-compatible`, `deprecated`, `removed`. Stable promotion means flipping the entry from `preview` (or another non-`production` status) to `production`. |
| **Preview build** | A catalog entry with `status: preview` and a build matrix entry on a non-`stable` channel (typically `preview`). Today: only `Ceiling-POE-VentIQ-RoomIQ-LED`. |
| **Stable build** | A catalog entry with `status: production` and a build matrix entry on `channel: stable`. Today: only `Ceiling-POE-VentIQ-RoomIQ` (Release-One). |
| **WebFlash-shippable** | The customer-facing flasher at [mysense360.com](https://mysense360.com) lists the firmware as installable. Requires: catalog entry, build matrix entry, GitHub Release `.bin`, WebFlash import, WebFlash-signed manifest, deployed `manifest.json` / `firmware-N.json`. Preview firmware can be WebFlash-shippable on the `preview` channel; that does **not** make it stable. |
| **Operator-proof container** | The structured "real hardware flashed and booted" record (the WebFlash-side `WF-HW-TEST-001` pattern) that a human operator fills in after flashing a real device via WebFlash and verifying boot / Improv handoff / sensor smoke / rescue path. Recorded in WebFlash, not here. |
| **REQUIRED_CONFIGS** | WebFlash-side list of config strings whose presence in the deployed `manifest.json` is treated as a baseline-health invariant by `__tests__/manifest-required-configs.test.js`. **Not** a lifecycle marker. Adding a stable build to `REQUIRED_CONFIGS` is a separate WebFlash decision. |
| **Kit** | WebFlash-side `scripts/data/kits.json` entry that surfaces a recommended SKU bundle in the installer wizard. **Not** a lifecycle marker. Stable firmware can exist without a kit; a kit can exist without stable firmware (though typical practice is to gate kits on a stable build). |

## Gate summary

A preview build is **not** eligible for stable promotion until every
row below is either `done` or has a recorded, accepted waiver. The
"Status for LED preview" column is the live punch list for
`Ceiling-POE-VentIQ-RoomIQ-LED`; for any other future preview product
the status starts at `not-started` and advances through the same
sequence.

| # | Gate | Required evidence | Owning repo | Status for LED preview |
|---|---|---|---|---|
| 1 | Product YAML exists and validates | A canonical product YAML under [`products/`](../products/) that loads under [`tests/validate_configs.py`](../tests/validate_configs.py) and [`tests/test_product_substitutions.py`](../tests/test_product_substitutions.py) | esphome-public | **done** — [`products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq-led.yaml) (PRODUCT-006) |
| 2 | WebFlash wrapper exists and validates | A wrapper under [`products/webflash/`](../products/webflash/) whose basename equals the lower-cased `config_string` per [`scripts/validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py) | esphome-public | **done** — [`products/webflash/ceiling-poe-ventiq-roomiq-led.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq-led.yaml) (PRODUCT-008) |
| 3 | Catalog preview entry exists | [`config/product-catalog.json`](../config/product-catalog.json) entry with `status: preview`, non-`stable` `channel`, `config_string`, `product_yaml`, `webflash_wrapper`, `hardware_status` | esphome-public | **done** — `status: preview`, `channel: preview` (PRODUCT-008 / PRODUCT-009) |
| 4 | Build matrix preview entry exists | [`config/webflash-builds.json`](../config/webflash-builds.json) entry with matching `config_string`, `product_yaml`, `artifact_name`, `channel`, `version`, `chip_family`, `hardware_requirements`, `features`; passes [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py) and [`tests/test_webflash_compatibility.py`](../tests/test_webflash_compatibility.py) | esphome-public | **done** — `channel: preview`, `version: 1.0.0`, `artifact_name: Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` (PRODUCT-009) |
| 5 | Preview release artifact exists | GitHub prerelease with the build's `.bin`, `checksums-sha256.txt`, `checksums-md5.txt`, and build-info `manifest.json` attached; `Attach to Release` job's release-body and release-asset gates passed | esphome-public | **done** — [`v1.0.0-led-preview`](https://github.com/sense360store/esphome-public/releases/tag/v1.0.0-led-preview), run [`25918422743`](https://github.com/sense360store/esphome-public/actions/runs/25918422743) (RELEASE-005) |
| 6 | Preview release proof recorded | [`docs/webflash-release-proof.md`](webflash-release-proof.md) backfilled with tag, run URL, asset size, SHA256, gate pass states, WebFlash import source URL | esphome-public | **done** — recorded by RELEASE-005 |
| 7 | WebFlash import complete | WebFlash-side ingest of the preview `.bin`; sidecar metadata generated; build entered into `firmware/sources.json`; signed firmware produced | WebFlash | **done** — per WF-LED-001 / WF-LED-002 |
| 8 | Live preview deploy current | WebFlash production `manifest.json` / `firmware-N.json` regenerated; deployment refreshed to GitHub Pages; post-deploy smoke green; `__tests__/github-pages-surface.test.js` aware of the preview entry | WebFlash | **done** — manifest-only exposure per WF-LED-003; WF-DEPLOY-001 fixed deployment drift |
| 9 | Real WebFlash flash proof recorded | Operator-proof container filled: a human flashed a real device via WebFlash; device booted; Improv / Wi-Fi handoff completed; sensors and the LED ring report sanely; rescue path verified | WebFlash | **pending** — WF-HW-TEST-001 operator-proof container exists but has not been filled by an operator |
| 10 | Hardware bench verification | Module-side Open Questions in the hardware reference doc are closed or explicitly accepted. For LED: harness rail (`J1` pin 2 `+5V` vs `+3.3V`), LED chain count, harness identity (direct mate vs cable) per [`docs/hardware/s360-300-r4-led.md`](hardware/s360-300-r4-led.md#open-questions--verification-needed); bench-side observations recorded against the tracking record **S360-300-BENCH-001** in [`docs/hardware/s360-300-r4-led.md`](hardware/s360-300-r4-led.md#s360-300-bench-001-status) | esphome-public | **pending** — S360-300-BENCH-001 status is `pending — bench hardware evidence required`; three Open Questions remain `verify`, observed LED ring behaviour not recorded |
| 11 | Stable-ready release notes | [`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py) output for the target `(config_string, version, channel=stable)`; `## Changelog` replaced with a human-authored, user-visible summary; [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py) accepts the body on `stable` (filler text rejected) | esphome-public | **pending** — no `channel=stable` draft generated yet |
| 12 | Production catalog promotion | [`config/product-catalog.json`](../config/product-catalog.json) entry flipped to `status: production`, `channel: stable`; per-field updates listed in [Required catalog changes](#required-catalog-changes); [`scripts/validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py) passes | esphome-public | **pending** |
| 13 | Stable build artifact | Plain semantic tag (`vX.Y.Z`, no suffix) published; [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml) builds the stable `.bin`; `Attach to Release` gates pass; assets attached | esphome-public | **pending** |
| 14 | Stable WebFlash import | WebFlash imports the stable `.bin`; production-signed manifest regenerated; deployment refreshed; stable build visible at [mysense360.com](https://mysense360.com) | WebFlash | **pending** |
| 15 | REQUIRED_CONFIGS decision (separate) | Explicit WebFlash decision: does the newly-stable build belong in the baseline-health `REQUIRED_CONFIGS` list? Recorded in the WebFlash repo's `__tests__/manifest-required-configs.test.js` only after a deliberate decision | WebFlash | **pending / decision needed** — not automatic |
| 16 | Kit / UI decision (separate) | Explicit WebFlash decision: does the newly-stable build get a recommended-kit entry in `scripts/data/kits.json` and/or a UI surface change? | WebFlash | **pending / decision needed** — not automatic |
| 17 | Human approval recorded | Sign-off captured per [Human approval checklist](#human-approval-checklist) | both | **pending** |

Rows 1–8 are the preview floor; rows 9–17 are the additional evidence
required for stable promotion. **No row in this table can be skipped
by appeal to another row.** A successful preview release does not
substitute for bench verification; a verified schematic does not
substitute for an operator flash proof; a deployed preview manifest
does not substitute for a stable build.

## Required upstream evidence

Before any stable promotion is considered:

- The module's hardware-catalog row in
  [`config/hardware-catalog.json`](../config/hardware-catalog.json) is
  `schematic_status: verified` with a `schematic_file` pointing at a
  committed PDF under [`docs/hardware/schematics/`](hardware/schematics/),
  validated by [`tests/test_hardware_catalog.py`](../tests/test_hardware_catalog.py).
- A standalone schematic-backed reference doc under
  [`docs/hardware/`](hardware/) covers the module's connectors, nets,
  and Open Questions, and the firmware-package mapping for the
  module's nets is `confirmed-ok` in
  [`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md).
- The board's per-board documentation state in
  [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md#decision-table)
  is `documented`, or `partially-documented` with the caveat
  explicitly retained in the catalog `notes` and in any downstream
  docs that reference the entry.
- If the configuration includes any mains-voltage module
  (`S360-400` or `S360-320` today), the
  [mains-voltage compliance tracker](compliance/mains-voltage-uk-eu-assessment.md)
  rows resolve to evidence-backed answers and a qualified
  electrical-safety / compliance review has been completed and
  recorded outside this repo. Documentation alone is not sufficient.

## Required firmware/release evidence

- The release tag is a plain semantic tag (`vX.Y.Z`); suffixed tags
  on a non-prerelease release are rejected by
  [`scripts/derive_release_version_channel.py`](../scripts/derive_release_version_channel.py).
- The [`Build & Release Firmware`](../.github/workflows/firmware-build-release.yml)
  workflow ran on `release.published` with `prerelease: false` and
  produced the declared `artifact_name` matching the build matrix
  entry's `version` and `channel: stable`.
- The `Attach to Release` job ran both gates and both passed:
  - [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py)
    on the release body — four required H2 sections, bullets, and
    no filler in `## Changelog` on `stable`.
  - [`scripts/check-webflash-release-assets.py`](../scripts/check-webflash-release-assets.py)
    on the asset list — `artifact_name` present, ≥ 100 KB.
- The four assets are attached: the stable `.bin`,
  `checksums-sha256.txt`, `checksums-md5.txt`, and the build-info
  `manifest.json` (this is **not** the WebFlash production
  `manifest.json`; see
  [`docs/webflash-ci-alignment.md`](webflash-ci-alignment.md)).
- A build / release proof row is recorded in
  [`docs/release-one.md`](release-one.md#proof-of-build-recorded) /
  [`docs/webflash-release-proof.md`](webflash-release-proof.md) with
  the GitHub Release URL, tag, workflow run URL, asset size, SHA256,
  and gate pass states.
- The release-notes draft for the target `(config_string, version,
  stable)` was generated by
  [`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py)
  (and validated by
  [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py)
  with `--channel stable`); the `## Changelog` section was replaced
  with a human-authored, user-visible summary before tagging. The
  generator's stable-channel guards apply: blocked / legacy-compatible
  / deprecated / removed entries are refused; preview entries on
  `stable` are refused.

## Required hardware evidence

- Every module in the config string has `schematic_status: verified`
  evidence at the SKU level (HW-007 / HW-008 pattern), with the
  per-board reference doc under `docs/hardware/` and the
  firmware-package mapping classified `confirmed-ok` in
  [`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md).
- Every Open Question in the relevant per-board reference doc is
  either **closed** (with evidence committed: silkscreen photo,
  scope capture, harness measurement, etc.) or **explicitly
  accepted** with a written rationale captured in the catalog
  `notes` for the promoted entry and in the relevant audit doc.
  Implicit acceptance is not allowed.
- For LED specifically, the three Open Questions in
  [`docs/hardware/s360-300-r4-led.md`](hardware/s360-300-r4-led.md#open-questions--verification-needed)
  must close or be accepted:
  - **Harness rail.** `J1` pin 2 (`+5V` vs `+3.3V` per Open
    Question 1) verified against silkscreen on both `S360-100`
    Core and `S360-300` LED boards.
  - **LED chain count.** Open Question 2 — exact count on the
    production `S360-300-R4` board, verified against silkscreen and
    PCB layout, written into either the per-board reference doc or
    the catalog `notes`.
  - **Harness identity.** Open Question 4 — direct mate vs short
    cable / pigtail between Core `J3` and LED `J1`.
- If new hardware evidence requires a package-level edit (pin
  rebind, RGB order, chipset), that edit lands in a separate
  scoped PR with its own test (e.g. the HW-010 + `tests/test_led_package_mapping.py`
  pattern) **before** stable promotion is considered.

## Required WebFlash evidence

Owned by [`sense360store/WebFlash`](https://github.com/sense360store/WebFlash);
this repo does not import, sign, regenerate manifests, deploy, or
modify any WebFlash-side state. The repo-side requirement is only that
each WebFlash gate below has a recorded artefact the WebFlash team can
point at.

- **Stable import.** The stable `.bin` was pulled from the GitHub
  Release via WebFlash's `scripts/sync-from-releases.py`; a sidecar
  `*.meta.json` was generated from the release body; the artifact is
  listed in WebFlash's `firmware/sources.json` with the WebFlash
  config string, version, channel (`stable`), and SHA256 matching
  this repo's `checksums-sha256.txt`.
- **Production signing.** The `.bin` is signed with the WebFlash
  production key. This repo neither holds the key nor signs
  firmware.
- **Production manifest.** WebFlash's `manifest.json` and
  `firmware-N.json` have been regenerated by WebFlash's
  `scripts/gen-manifests.py`. The stable build's `config_string`
  appears in the manifest.
- **Deploy current.** WebFlash's GitHub Pages deployment (or
  successor hosting target) serves the regenerated manifest;
  `__tests__/github-pages-surface.test.js` (and the equivalent
  WebFlash deploy gate per WF-DEPLOY-001) is green.
- **Operator-proof container filled (WF-HW-TEST-001).** The
  structured "real hardware test" record in WebFlash has been
  completed by a human operator. The container records, at minimum:
  - WebFlash version + commit SHA used to flash,
  - manifest source URL,
  - device flashed (chip family + board identifier),
  - flash succeeded,
  - device booted,
  - Improv / Wi-Fi handoff completed,
  - sensors report (per the build's `features` list),
  - module-specific indicators behave (e.g. for LED: ring shows
    expected boot pattern, count matches Open Question 2's
    resolution, brightness control reachable),
  - rescue path remains available,
  - timestamp + operator identity.
- **Post-deploy smoke test.** WebFlash's post-deploy smoke test
  passes after the stable build is live (per
  [`docs/webflash-release-handoff.md` Real hardware test](webflash-release-handoff.md)
  and the WebFlash deploy gates).

## Required user/operator validation

Stable promotion is gated on a real human flashing a real device. CI,
docs, and a deployed manifest are necessary but not sufficient.

The operator validation evidence (recorded in WebFlash, not here) must
include:

- Flash succeeded via the WebFlash installer (not via raw
  `esptool.py`).
- Device booted on first flash.
- Wi-Fi / Improv handoff completed; the device joined the configured
  network.
- Every entity listed in the build's `features` (per
  [`config/webflash-builds.json`](../config/webflash-builds.json))
  reports a plausible value.
- Module-specific indicators behave as documented for the promoted
  module (e.g. LED ring, fan driver, mains relay).
- The rescue / recovery flash path remains available.
- Any open caveat carried in the catalog `notes` for the entry is
  either resolved or explicitly accepted by the operator.

## Required catalog changes

When the gates above are met and stable promotion is performed (in a
**separate** future PR), the catalog entry in
[`config/product-catalog.json`](../config/product-catalog.json)
changes as follows. This table is the field-level promotion diff;
nothing in this table is performed by RELEASE-006.

| Field | Preview value (today) | Stable value (target) |
|---|---|---|
| `status` | `preview` | `production` |
| `channel` | `preview` | `stable` |
| `version` | `1.0.0` | bumped or carried; must match release tag and build matrix |
| `artifact_name` | `Sense360-{CONFIG_STRING}-v{VERSION}-preview.bin` | `Sense360-{CONFIG_STRING}-v{VERSION}-stable.bin` |
| `webflash_build_matrix` | `true` | `true` (unchanged) |
| `product_yaml` | unchanged | unchanged |
| `webflash_wrapper` | unchanged | unchanged |
| `modules` | unchanged | unchanged |
| `blocked_modules` | carries the blocked list (e.g. `["FanTRIAC"]`) | unchanged unless an unblock is recorded in a separate PR |
| `hardware` | SKU map | unchanged unless a new SKU joins the config |
| `hardware_status` | typically `verified-*-candidate` | promoted to a verified-for-release form (e.g. `verified-for-release-one` analogue) |
| `notes` | preview caveats | rewritten to record stable promotion, dropped caveats (only those genuinely resolved), and retained caveats |

Every field change must be backed by a row from
[Gate summary](#gate-summary). Promotion notes must cite the gate
evidence (tag, run URL, operator-proof container ID, accepted Open
Question rationale, etc.).

## Required WebFlash changes

The corresponding entry in
[`config/webflash-builds.json`](../config/webflash-builds.json)
changes as follows. This table is the field-level promotion diff;
nothing in this table is performed by RELEASE-006.

| Field | Preview value (today) | Stable value (target) |
|---|---|---|
| `config_string` | unchanged | unchanged |
| `product_yaml` | wrapper path unchanged | unchanged |
| `artifact_name` | `…-v{VERSION}-preview.bin` | `…-v{VERSION}-stable.bin` |
| `channel` | `preview` | `stable` |
| `version` | matches catalog | matches catalog |
| `chip_family` | unchanged | unchanged |
| `hardware_requirements` | preview-stage caveats included | unchanged unless an Open Question was closed in a way that changes a requirement |
| `features` | preview features list | stable features list — preview-only caveats removed only when the corresponding gate row in [Gate summary](#gate-summary) is `done` |

WebFlash-side `manifest.json`, `firmware-N.json`, `firmware/sources.json`,
`__tests__/manifest-required-configs.test.js`, and `scripts/data/kits.json`
are **WebFlash-owned**. Stable promotion in this repo does not edit any
WebFlash file. Those changes happen in WebFlash PRs and follow WebFlash's
own gates.

## Required tests

The following validators must remain green at every step from
preview-floor through stable promotion. None of them is added or
modified by RELEASE-006; they are listed so future promotion PRs know
exactly which surface a stable flip must clear.

- [`tests/validate_configs.py`](../tests/validate_configs.py)
- [`tests/test_product_substitutions.py`](../tests/test_product_substitutions.py)
- [`tests/test_product_catalog.py`](../tests/test_product_catalog.py)
- [`tests/test_product_catalog_consistency.py`](../tests/test_product_catalog_consistency.py)
- [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py)
- [`tests/test_webflash_compatibility.py`](../tests/test_webflash_compatibility.py)
- [`tests/test_webflash_artifact_naming.py`](../tests/test_webflash_artifact_naming.py)
- [`tests/test_validate_webflash_release_notes.py`](../tests/test_validate_webflash_release_notes.py)
- [`tests/test_generate_webflash_release_notes.py`](../tests/test_generate_webflash_release_notes.py)
- [`tests/test_release_one_entity_names.py`](../tests/test_release_one_entity_names.py)
- [`tests/test_hardware_catalog.py`](../tests/test_hardware_catalog.py)
- [`tests/test_led_package_mapping.py`](../tests/test_led_package_mapping.py)
  — the LED exclusion is scoped to **stable** Release-One only after
  PRODUCT-009; this stays correct after LED stable promotion provided
  the promotion does not add `LED` to Release-One's `Ceiling-POE-VentIQ-RoomIQ`
  config string (which would be a separate, rejected change).
- [`scripts/validate_product_catalog_consistency.py`](../scripts/validate_product_catalog_consistency.py)

The release-time guards used by the publish job:

- [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py)
- [`scripts/check-webflash-release-assets.py`](../scripts/check-webflash-release-assets.py)
- [`scripts/derive_release_version_channel.py`](../scripts/derive_release_version_channel.py)

## LED preview case study

`Ceiling-POE-VentIQ-RoomIQ-LED` is the first product to walk this
gate sequence end-to-end. Today it is at the **preview floor**: rows
1–8 in [Gate summary](#gate-summary) are `done`, rows 9–17 are
`pending` or `decision needed`.

### Done (rows 1–8)

- **Row 1 — product YAML.** [`products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq-led.yaml)
  (PRODUCT-006). Same Core ceiling + PoE PSU + VentIQ + RoomIQ
  package stack as Release-One plus
  [`packages/hardware/led_ring_ceiling.yaml`](../packages/hardware/led_ring_ceiling.yaml)
  (bound to `led_data_pin: GPIO38` after HW-010).
- **Row 2 — WebFlash wrapper.** [`products/webflash/ceiling-poe-ventiq-roomiq-led.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq-led.yaml)
  (PRODUCT-008). Basename matches `ceiling-poe-ventiq-roomiq-led`.
- **Row 3 — catalog preview entry.** `status: preview`,
  `channel: preview`, `hardware_status: verified-led-candidate`,
  `blocked_modules: ["FanTRIAC"]` (LED token carried by the entry,
  FanTRIAC remains blocked under HW-005) per PRODUCT-008 /
  PRODUCT-009.
- **Row 4 — build matrix preview entry.** `config_string: Ceiling-POE-VentIQ-RoomIQ-LED`,
  `version: 1.0.0`, `channel: preview`,
  `artifact_name: Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`
  in [`config/webflash-builds.json`](../config/webflash-builds.json)
  (PRODUCT-009).
- **Row 5 — preview release artifact.** Prerelease
  [`v1.0.0-led-preview`](https://github.com/sense360store/esphome-public/releases/tag/v1.0.0-led-preview);
  workflow run
  [`25918422743`](https://github.com/sense360store/esphome-public/actions/runs/25918422743);
  artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`
  (1,135,904 bytes; SHA256
  `93310d2cbc27355e399f36a232336b6b9075dacfc178d603c7a92aa1089182d3`);
  release-body and release-asset gates both passed (RELEASE-005).
  RELEASE-004 normalises the suffixed tag to `version=1.0.0`,
  `channel=preview` via
  [`scripts/derive_release_version_channel.py`](../scripts/derive_release_version_channel.py).
- **Row 6 — preview release proof recorded.** [`docs/webflash-release-proof.md` LED preview release proof](webflash-release-proof.md#led-preview-release-proof-release-003)
  backfilled by RELEASE-005.
- **Row 7 — WebFlash import.** Owned by WF-LED-001 / WF-LED-002 in
  the WebFlash repo; consumed the GitHub Release asset, the tag, and
  the SHA256.
- **Row 8 — live preview deploy.** Owned by WF-LED-003 (manifest-only
  exposure decision) and WF-DEPLOY-001 (Pages deployment drift fix).

### Pending (rows 9–17)

Each row below is **explicitly pending** for LED stable promotion. No
row is implied done by any other row.

- **Row 9 — Real WebFlash flash proof (WF-HW-TEST-001).** The
  operator-proof container exists in the WebFlash repo; a human
  operator has not yet flashed a real
  Sense360 Ceiling Bathroom LED via WebFlash and filled in the
  container. Until that record exists, stable promotion is
  not eligible.
- **Row 10 — S360-300 bench verification.** The three Open
  Questions in
  [`docs/hardware/s360-300-r4-led.md`](hardware/s360-300-r4-led.md#open-questions--verification-needed)
  remain `verify`:
  - harness rail (`J1` pin 2 `+5V` vs `+3.3V`),
  - LED chain count,
  - harness identity (direct mate vs cable).
  Each must close (silkscreen / scope / measurement evidence
  committed) or be explicitly accepted with a written rationale.
  Bench-side observations are tracked in
  [**S360-300-BENCH-001**](hardware/s360-300-r4-led.md#s360-300-bench-001-status),
  which today is `pending — bench hardware evidence required` (no
  operator, no date, no observed values supplied; observed LED ring
  behaviour also not recorded). The bench record can only flip away
  from `pending` when real evidence is committed — implicit
  acceptance is not allowed.
- **Row 11 — Stable-ready release notes.** No `channel=stable`
  release-notes draft has been generated for
  `Ceiling-POE-VentIQ-RoomIQ-LED`. The generator currently emits
  Sense360 LED in `## Features` / `## Hardware Requirements` for
  the LED preview; the same emission shape applies to a stable LED
  build, but the `## Changelog` must be human-authored before
  publishing.
- **Row 12 — Production catalog promotion.** The catalog entry
  stays at `status: preview`, `channel: preview` until rows 9–11 and
  14 are recorded.
- **Row 13 — Stable build artifact.** No stable tag has been cut for
  the LED-bearing build. A stable tag would be a plain semantic
  tag (e.g. `v1.0.1` or a successor) — not a `-led-preview` suffix
  and not the existing Release-One tag `v1.0.0` (which builds the
  LED-less Release-One).
- **Row 14 — Stable WebFlash import.** Not started; depends on
  row 13.
- **Row 15 — REQUIRED_CONFIGS decision.** *Decision needed,
  separate from stable promotion.* See
  [REQUIRED_CONFIGS policy](#required_configs-policy).
- **Row 16 — Kit / UI decision.** *Decision needed, separate from
  stable promotion.* See [Kit policy](#kit-policy).
- **Row 17 — Human approval recorded.** Sign-off per
  [Human approval checklist](#human-approval-checklist) — not yet
  collected.

### Hardware-evidence inheritance

Row 10 (bench verification) is **the** load-bearing row that the LED
preview cannot work around with more software, more tests, or more
documentation. Closing or accepting the harness rail, LED count, and
harness identity Open Questions is the prerequisite for advancing
rows 11–17.

## What is explicitly not enough

These statements are guardrails. Each is a real failure mode an
earlier PR or future PR could try to claim as sufficient. None of
them is.

- **A preview release artifact does not equal stable.** A successful
  prerelease build, with checksums, with the release-body and
  release-asset gates passed, with the SHA256 recorded, is the
  preview floor. It is row 5 in the gate summary — not the
  destination.
- **A WebFlash import does not equal stable.** Importing the `.bin`
  into WebFlash, generating sidecar metadata, and producing a
  signed firmware sets up the preview manifest. It is rows 7 and a
  precondition for rows 8 and 14 — not the destination.
- **A deployed `manifest.json` does not equal stable.** Refreshing
  the WebFlash production manifest so that the build appears in the
  installer is preview-channel publication. It is row 8 — not the
  destination.
- **A verified schematic does not equal stable.** HW-007 / HW-008
  flipped `schematic_status: verified` for `S360-300` and committed
  the PDF; HW-010 reconciled the ceiling LED package pin. None of
  those — individually or together — makes the LED preview
  WebFlash-stable. They are the entry conditions for row 10, not a
  substitute for it.
- **Compile-only or preview catalog status does not equal stable.**
  `status: preview` exists precisely so a product can ship on the
  `preview` channel without being claimed as stable. Moving to
  `production` requires the full row 9–17 chain.
- **CI green does not equal stable.** Every test in
  [Required tests](#required-tests) passing is a precondition, not
  a sign-off. Tests verify catalog and build-matrix self-consistency
  and contract conformance; they cannot verify that a real device
  boots and flashes a real LED ring.
- **No FanTRIAC inference.** Nothing in this document — and nothing
  in any stable promotion gated by this document — unblocks
  FanTRIAC. The FanTRIAC entry
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`,
  `blocker: HW-005`, `webflash_build_matrix: false`, with the
  missing-evidence checklist in
  [`docs/release-one-hardware-audit.md#fantriac-mapping-resolution`](release-one-hardware-audit.md#fantriac-mapping-resolution).
  FanTRIAC has its own gate path; the promotion of any LED, AirIQ,
  or other variant does not advance it.

## Human approval checklist

Tick each box only when the corresponding evidence is recorded and
named. A pre-checked or unnamed box is not approval.

- [ ] **Hardware lead sign-off.** Bench verification is recorded
      (every Open Question in the per-board reference doc closed or
      explicitly accepted with a written rationale captured in the
      catalog `notes`). Names the reviewer and the date.
- [ ] **Release engineer sign-off.** Stable tag cut on `main`;
      `Build & Release Firmware` workflow run succeeded with both
      `Attach to Release` gates green; release proof row recorded.
      Names the release URL, run URL, and tag.
- [ ] **WebFlash operator sign-off.** Operator-proof container
      filled in the WebFlash repo; flash succeeded; device booted;
      Improv / Wi-Fi handoff completed; module-specific indicators
      behave; rescue path verified. Names the operator, the
      WebFlash commit, and the device flashed.
- [ ] **Compliance sign-off (only if mains).** If the configuration
      includes any mains-voltage module (`S360-400` or `S360-320`),
      a qualified electrical-safety / compliance review has been
      completed and recorded outside this repo per
      [COMPLIANCE-001](compliance/mains-voltage-uk-eu-assessment.md).
      Names the reviewer and the artefact ID.
- [ ] **REQUIRED_CONFIGS decision (separate).** A deliberate
      decision has been recorded (in the WebFlash repo) about
      whether the newly-stable build is added to
      `REQUIRED_CONFIGS`. Default is **do not add**; see
      [REQUIRED_CONFIGS policy](#required_configs-policy).
- [ ] **Kit / UI decision (separate).** A deliberate decision has
      been recorded (in the WebFlash repo) about whether the
      newly-stable build gets a kit entry. Default is **do not
      add**; see [Kit policy](#kit-policy).
- [ ] **Release authority sign-off.** Names a single human who has
      reviewed the row-by-row evidence above and approves the
      flip to `status: production`, `channel: stable`.

Promotion PRs must include this checklist in the PR description
with each box's evidence cited inline. A promotion PR that
short-circuits the checklist — for example by claiming row 9
satisfied because the preview manifest is live — is rejected.

## REQUIRED_CONFIGS policy

`REQUIRED_CONFIGS` is a WebFlash-side concept: the list of WebFlash
config strings whose presence in the deployed
`manifest.json` is enforced by `__tests__/manifest-required-configs.test.js`
as a **baseline-site-health invariant**. A build in `REQUIRED_CONFIGS`
is one whose absence from the live deployment should fail a deployment
gate.

**A product becoming stable does not automatically add it to
`REQUIRED_CONFIGS`.** The two questions are independent:

- "Is this build production-quality?" → answered by the gate
  table above.
- "Should the absence of this build from the WebFlash deployment
  break the site?" → answered by a separate WebFlash decision.

Today, `Ceiling-POE-VentIQ-RoomIQ` (Release-One) is the only
WebFlash-stable build, and the WebFlash repo decides what its
`REQUIRED_CONFIGS` list contains. When the LED preview is eventually
promoted to stable, the WebFlash repo will make a separate decision
about whether `Ceiling-POE-VentIQ-RoomIQ-LED` joins
`REQUIRED_CONFIGS`. The default answer is **no**: a deployment
without LED firmware is still a valid baseline; adding LED to
`REQUIRED_CONFIGS` would mean that a missing LED build fails the
WebFlash deployment as a whole.

This policy applies to every future stable promotion (AirIQ-bearing
variants, FanRelay / FanPWM / FanDAC variants, PWR-bearing variants,
etc.). Each `REQUIRED_CONFIGS` addition is a separate WebFlash PR,
not an implicit side effect of stable promotion in this repo.

## Kit policy

A "kit" is a WebFlash-side `scripts/data/kits.json` entry that
surfaces a recommended SKU bundle in the installer wizard. Kits are
a **product / UX surface**, not a release-lifecycle marker.

**A product becoming stable does not automatically get a kit.** The
two questions are independent:

- "Is this firmware production-quality?" → answered by the gate
  table above.
- "Should the WebFlash installer recommend a hardware bundle for
  this configuration?" → answered by a separate WebFlash product
  decision, typically driven by SKU availability, pricing, and the
  customer journey.

A stable firmware can exist before it is exposed as a kit; a kit can
be added in a later WebFlash PR; a kit can also be deferred
indefinitely if the configuration is a maintainer / advanced-user
target rather than a recommended bundle. The default for any newly
stable build is **no kit until a deliberate decision is recorded
in the WebFlash repo**.

This policy applies to every future stable promotion.

## Do-not-change guardrails

RELEASE-006 — this document — performs **none** of the following.
Anyone reading this document looking for justification to change one
of them must use a separate, scoped PR with its own gate evidence.

- No edits to
  [`config/product-catalog.json`](../config/product-catalog.json),
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
  or [`config/hardware-catalog.json`](../config/hardware-catalog.json).
  LED stays `status: preview`, `channel: preview`; FanTRIAC stays
  `status: blocked`, `blocker: HW-005`,
  `webflash_build_matrix: false`; Release-One stays the only
  `production` entry on `stable`.
- No edits to any product YAML under
  [`products/`](../products/) or any WebFlash wrapper under
  [`products/webflash/`](../products/webflash/).
- No edits to any package YAML under
  [`packages/`](../packages/).
- No edits to any workflow under
  [`.github/workflows/`](../.github/workflows/), any script under
  [`scripts/`](../scripts/), any test under
  [`tests/`](../tests/), any component under
  [`components/`](../components/), or any include under
  [`include/`](../include/).
- No firmware build, no firmware regeneration, no GitHub Release
  tag, no asset upload, no WebFlash import, no manifest
  regeneration, no signing.
- No edits to the Release-One product, the Release-One config
  string `Ceiling-POE-VentIQ-RoomIQ`, the Release-One artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, or the
  Release-One tag [`v1.0.0`](https://github.com/sense360store/esphome-public/releases/tag/v1.0.0).
- No edits to WebFlash-side `REQUIRED_CONFIGS`, `kits.json`,
  `firmware/sources.json`, `manifest.json`, or any test under
  WebFlash's `__tests__/`. RELEASE-006 lives entirely in
  this repo's `docs/`.
- No promotion of any product to `status: production`. No
  `channel: preview → stable` flip in any build matrix entry.
- No unblock of FanTRIAC. No change to the mains-voltage
  compliance status for `S360-400` or `S360-320`.
- No new tests. No script changes. No workflow changes.

## Follow-up PR sequence

When a future maintainer is ready to promote a preview product to
stable, the sequence below is the safe path. Each step is its own
scoped PR with its own evidence. Steps in this repo and steps in
WebFlash interleave; the dependency arrows are real.

1. **Hardware bench verification PR** (this repo).
   Closes or accepts the per-board Open Questions for the promoted
   module. May land package-level edits with their own tests
   (HW-010 pattern). For LED: resolves S360-300 harness rail, LED
   count, harness identity. No catalog / build matrix change.
2. **Operator flash proof PR** (WebFlash repo).
   Fills in the operator-proof container (WF-HW-TEST-001 pattern)
   on a real device. Records flash, boot, Improv handoff, sensor
   smoke, module-indicator behaviour, and rescue path. No
   catalog / build matrix change in this repo.
3. **Stable release-notes draft + tag PR** (this repo).
   Generates the stable-channel release-notes body for the target
   `(config_string, version, stable)`; replaces `## Changelog` with
   the human-authored summary; opens a release-notes draft for
   review. After approval, the maintainer publishes a plain
   semantic tag (`vX.Y.Z`, no suffix) on `main`; the
   [`Build & Release Firmware`](../.github/workflows/firmware-build-release.yml)
   workflow runs, both `Attach to Release` gates pass, and the
   stable `.bin` is attached. The stable build / release proof row
   is recorded in
   [`docs/webflash-release-proof.md`](webflash-release-proof.md).
4. **Catalog + build-matrix promotion PR** (this repo).
   Flips the catalog entry per
   [Required catalog changes](#required-catalog-changes) and the
   build matrix entry per
   [Required WebFlash changes](#required-webflash-changes).
   References the stable release tag, the operator-proof container
   ID, the hardware-bench verification PR, and the
   [Human approval checklist](#human-approval-checklist). Both
   `tests/test_product_catalog.py` and
   `tests/test_product_catalog_consistency.py` must pass.
5. **WebFlash stable import PR** (WebFlash repo).
   Pulls the stable `.bin`; regenerates `manifest.json`;
   redeploys; runs post-deploy smoke. No catalog / build matrix
   change in this repo.
6. **(Optional) REQUIRED_CONFIGS PR** (WebFlash repo).
   Only if the stable build is to be added to the
   baseline-health list. Default: **skip**. See
   [REQUIRED_CONFIGS policy](#required_configs-policy).
7. **(Optional) Kit PR** (WebFlash repo).
   Only if a customer-facing kit bundle is desired. Default:
   **skip**. See [Kit policy](#kit-policy).

FanTRIAC is **not** on this sequence. FanTRIAC has its own gate
path under HW-005 — a separate hardware-evidence chain (committed
`S360-320` schematic, `TRI_GPIO1` / `TRI_GPIO2` traced to
direct interrupt-capable ESP32 GPIOs, a verified non-`ac_dimmer`
driver path or an accepted alternative), plus mains-voltage
compliance review per COMPLIANCE-001. Stable promotion of any
non-FanTRIAC variant does not advance the FanTRIAC unblock. The
HW-PINMAP-320 schematic-backed audit doc has landed at
[`docs/hardware/s360-320-r4-triac.md`](hardware/s360-320-r4-triac.md)
with **status: `partial — schematic evidence available; package
reconciliation, timing validation, and compliance/certification
pending`**, records the intended advanced / manual-warning
long-term product posture for FanTRIAC (visible / selectable,
buildable after package evidence, installable only through an
advanced / manual-warning path; **not** Release-One, **not**
REQUIRED_CONFIGS, **not** recommended, **not** kit / default,
**not** compliance-certified), and explicitly does **not** advance
any RELEASE-006 row, unblock HW-005, or clear COMPLIANCE-001.

`PRODUCT-TRIAC-001` has separately recorded the advanced /
manual-warning candidate posture as catalog policy via a
**notes-only** edit on `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` in
[`config/product-catalog.json`](../config/product-catalog.json);
the structural fields (`status: blocked`, `blocker: HW-005`,
`reason` unchanged, `webflash_build_matrix: false`, no
`artifact_name`) are preserved, and no new lifecycle enum value was
added. The `RELEASE-006` preview-to-stable promotion path does
**not** apply to FanTRIAC at any layer: the FanTRIAC release class
is `advanced/manual-warning-artifact-only` (advanced channel only)
rather than `preview-artifact-candidate` →
`stable-candidate-after-promotion`, and any future advanced-channel
artifact is owned by the separate `WF-TRIAC-001` /
`RELEASE-TRIAC-001` / `WF-IMPORT-TRIAC-001` chain — not by this
document.

## See also

- [`README.md`](../README.md) — repo overview, Release-One quick
  reference, package reference.
- [`docs/product-onboarding.md`](product-onboarding.md) — PRODUCT-004
  cross-doc product onboarding guide; orders the existing guardrails
  into a safe sequence for adding a new product / config.
- [`docs/product-led-preview-decision.md`](product-led-preview-decision.md)
  — PRODUCT-005 decision doc for the LED preview product path and
  the PRODUCT-006 / PRODUCT-008 / PRODUCT-009 / RELEASE-003 /
  RELEASE-004 / RELEASE-005 sequence.
- [`docs/release-one.md`](release-one.md) — Release-One configuration
  with full slot / file / binary mapping and the recorded build /
  release proof row.
- [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)
  — Release-One firmware-vs-schematic audit, FanTRIAC HW-005
  resolution, and Sense360 LED policy.
- [`docs/webflash-contract.md`](webflash-contract.md) — canonical
  WebFlash artifact / grammar / token contract.
- [`docs/webflash-release-handoff.md`](webflash-release-handoff.md)
  — operational source-to-installer flow.
- [`docs/webflash-release-proof.md`](webflash-release-proof.md) —
  ESP-006 / ESP-007 Release-One proof record plus the RELEASE-003 /
  RELEASE-005 LED preview proof section.
- [`docs/webflash-ci-alignment.md`](webflash-ci-alignment.md) —
  CI ↔ WebFlash alignment record.
- [`docs/webflash-compatibility-taxonomy-audit.md`](webflash-compatibility-taxonomy-audit.md)
  — COMPAT-001 per-token audit; carries the `LED` reserved-future-token
  recommendation row and the future-token policy.
- [`docs/hardware/s360-300-r4-led.md`](hardware/s360-300-r4-led.md)
  — Sense360 LED schematic-backed reference; carries the harness
  rail, LED count, and harness identity Open Questions that are
  still `verify`.
- [`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
  — HW-009 firmware-package-vs-schematic audit; carries the
  `confirmed-ok` row for `LED_DATA / Sense360 LED` after HW-010.
- [`docs/hardware/remaining-board-documentation-audit.md`](hardware/remaining-board-documentation-audit.md)
  — per-board documentation-state classification (HW-004 / HW-006 /
  HW-008).
- [`docs/hardware/hardware-artifact-policy.md`](hardware/hardware-artifact-policy.md)
  — HW-ASSETS-001 canonical policy for hardware source / manufacturing
  artifacts. Defines the per-board artifact index whose
  `webflash_status` field is sourced from the product catalog and
  whose finished-board inventory feeds the hardware-evidence side of
  the gate-summary table in this document.
- [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)
  — COMPLIANCE-001 mains-voltage UK / EU compliance tracker.
- [`docs/cleanup-audit.md`](cleanup-audit.md) — classification of
  stale / current / blocked-reference / legacy-compatible repo
  content.
- [`docs/product-scaffold-generator.md`](product-scaffold-generator.md)
  — PRODUCT-010 conservative product scaffold report generator. The
  scaffold tool cannot scaffold `production`; stable promotion is
  reached via the gates in this document, not via a scaffold.
- [`docs/product-deprecation-removal-policy.md`](product-deprecation-removal-policy.md)
  — PRODUCT-DEP-001 canonical cross-cutting deprecation / removal
  policy. Defines the opposite direction (production / preview →
  deprecated → removed), inherits the REQUIRED_CONFIGS and kit
  policies from this document, and records the future
  `_validate_deprecated` / `_validate_removed` enforcement work as
  a backlog. Documentation only; no entries are deprecated or
  removed by PRODUCT-DEP-001.
- [`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md)
  — PRODUCT-AVAIL-001 canonical product availability taxonomy.
  Names the ladder this gate document sits on:
  `preview-available` (rows 1–8 of the gate summary) →
  `stable-available` (rows 1–17 done) → `production-required`
  (separate REQUIRED_CONFIGS decision) → `kit-exposed` (separate
  kit / UI decision). Records the policy-only `design-pending` and
  `firmware-missing` exception labels for modules that exist in
  docs but are not buildable. Documentation only; no JSON fields
  added; no statuses changed.
- [`docs/product-readiness-matrix.md`](product-readiness-matrix.md)
  — PRODUCT-GAP-001 product-level readiness gate. Classifies the
  FanRelay / FanPWM / FanDAC / FanTRIAC / PWR-240V / PoE-410
  candidate product families against package readiness and the
  WebFlash compatibility grammar; records the per-family
  follow-up PRs (`PRODUCT-RELAY-001`, `PRODUCT-PWM-001`,
  `PRODUCT-DAC-001`, `PRODUCT-TRIAC-001`,
  `PRODUCT-POWER-400-001`, `PRODUCT-POE-410-001`) and the
  downstream `WEBFLASH-GAP-001` / `RELEASE-GAP-001` /
  `WF-IMPORT-GAP-001` chain; explicitly preserves Release-One,
  the LED preview, and the FanTRIAC blocked reference; any
  stable promotion arising from a future product slice goes
  through the 17-row gate in this document.
- [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
  — RELEASE-GAP-001 release-layer readiness gate. Records the
  per-family release-artifact eligibility (build / sign / attach
  / checksums / release-notes / release-proof / operator-proof /
  import) for FanRelay / FanPWM / FanDAC / FanTRIAC / PWR-240V /
  PoE-410 and the per-family release slices (`RELEASE-RELAY-001`,
  `RELEASE-PWM-001`, `RELEASE-DAC-001`, `RELEASE-TRIAC-001`,
  `RELEASE-POWER-400-001`, `RELEASE-POE-410-001`); treats
  `RELEASE-007` LED stable as reference-only and out-of-scope —
  any LED stable promotion goes through the 17-row gauntlet in
  this document (rows 9–17 still pending), including
  `WF-HW-TEST-002` and
  [`S360-300-BENCH-001`](hardware/s360-300-r4-led.md#s360-300-bench-001-status).
  Preserves Release-One, the LED preview, and the FanTRIAC blocked
  reference; FanTRIAC stays `stable-not-approved` and
  `blocked-from-standard-release`. Documentation only.

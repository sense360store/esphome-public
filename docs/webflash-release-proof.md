# WebFlash Release Asset Proof (ESP-006 / ESP-007)

ESP-006 (CI builds and uploads a WebFlash-compatible firmware artifact) and
ESP-007 (a real GitHub Release publishes the WebFlash-compatible firmware
assets) are **proven** for `esphome-public` as of the run recorded below.

This proof covers the repo-side responsibilities only: raw `.bin` build,
WebFlash-compatible artifact naming, GitHub Release asset publishing, and
the pre-upload release-notes and asset gates. It does **not** prove WebFlash
production signing, the WebFlash production-signed `manifest.json`, or
WebFlash deploy — those remain WebFlash-owned (see "What ESP-007 does NOT
do" below).

## Proof record

| Field | Value |
|-------|-------|
| GitHub Release URL | <https://github.com/sense360store/esphome-public/releases/tag/v1.0.0> |
| Release tag | `v1.0.0` |
| Workflow run URL | <https://github.com/sense360store/esphome-public/actions/runs/25763009641> |
| Workflow | `Build & Release Firmware` |
| Workflow event | `release` (not `workflow_dispatch`) |
| Matrix product | `ceiling-poe-ventiq-roomiq` |
| Build file | [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml) |
| WebFlash config string | `Ceiling-POE-VentIQ-RoomIQ` |
| Firmware asset | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` |
| Firmware asset size (release page) | `1.04 MB` |
| Release-body validation | passed |
| Checksums attached | `checksums-sha256.txt`, `checksums-md5.txt` |
| Build-info manifest attached | `manifest.json` |
| Status | ESP-006 and ESP-007 proven |

### Release assets present

- `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`
- `checksums-sha256.txt`
- `checksums-md5.txt`
- `manifest.json`

### Jobs that passed in the recorded run

Top-level jobs:

- `Generate Build Matrix`
- `Build: ceiling-poe-ventiq-roomiq`
- `Attach to Release`

Steps that passed inside `Attach to Release`:

- download firmware artifacts
- list downloaded firmware
- generate checksums
- create firmware manifest
- validate WebFlash release notes
- check WebFlash release assets
- upload release assets
- release summary

## What ESP-006 / ESP-007 enforce today

The release workflow
([`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml))
runs two gating steps in the `Attach to Release` job before any release asset
is uploaded for a `release.published` event:

1. **Release-notes validation** —
   [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py)
   reads the release body from `$GITHUB_EVENT_PATH` and asserts:
   - the four required H2 sections are present:
     `## Changelog`, `## Known Issues`, `## Features`, `## Hardware Requirements`
   - `## Changelog`, `## Features`, and `## Hardware Requirements` each
     contain at least one bullet
   - on `stable`, `## Changelog` is not filler text (`TBD`, `Placeholder`,
     `Initial release`, `No changes`, `N/A`, `See release notes`, `TODO`,
     `First release`, `Firmware release`, `Nothing to report`)
2. **Release-asset assertion** —
   [`scripts/check-webflash-release-assets.py`](../scripts/check-webflash-release-assets.py)
   loads [`config/webflash-builds.json`](../config/webflash-builds.json),
   filters to entries matching the release's `(version, channel)`, and asserts
   each `artifact_name` is present in the release-asset directory and is at
   least 100 KB. **Fail-closed**: if no matrix entries match, the release
   fails. A release with no matching matrix entry is drift, not a no-op.
   The bypass flag `--allow-no-matching-builds` exists for manual /
   dry-run flows only and is **not** passed by the release job.

Both gates passed in the recorded run above.

## What ESP-007 does NOT do

- Does not sign firmware (WebFlash is the production signing authority).
- Does not generate the WebFlash production-signed `manifest.json`. The
  `manifest.json` attached to the release is the build-info manifest
  (per-file SHA256 and size, build timestamp, git SHA, ESPHome version),
  not the WebFlash production-signed manifest.
- Does not deploy to WebFlash.
- Does not narrow the build matrix to "WebFlash-only"; the workflow still
  builds every YAML in `products/`. Narrowing scope is out of scope for
  ESP-007.

This proof therefore covers raw build + GitHub Release publishing only. Do
not edit this document to claim WebFlash signing, manifest generation, or
deploy are proven from this repo.

## LED preview release proof (RELEASE-003)

RELEASE-003 scaffolded the pending-proof record for the LED-bearing
preview sibling
[`Ceiling-POE-VentIQ-RoomIQ-LED`](../config/webflash-builds.json) added by
PRODUCT-009. **RELEASE-005 records the successful prerelease proof.** The
GitHub prerelease [`v1.0.0-led-preview`](https://github.com/sense360store/esphome-public/releases/tag/v1.0.0-led-preview)
was published; the
[`Build & Release Firmware`](../.github/workflows/firmware-build-release.yml)
workflow run
[`25918422743`](https://github.com/sense360store/esphome-public/actions/runs/25918422743)
built `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`, both
release-body validation and release-asset assertion passed, and the
`.bin`, `checksums-sha256.txt`, `checksums-md5.txt`, and `manifest.json`
assets were uploaded. The values in
[Proof record](#proof-record) below are the real recorded values, not
placeholders.

This section is **separate from** the ESP-006 / ESP-007 Release-One
proof above. The Release-One record (tag `v1.0.0`, artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, run
[`25763009641`](https://github.com/sense360store/esphome-public/actions/runs/25763009641))
is unchanged by RELEASE-003 or RELEASE-005.

### Proof record

The static values below come from
[`config/webflash-builds.json`](../config/webflash-builds.json) and
[`config/product-catalog.json`](../config/product-catalog.json) (both
populated by PRODUCT-009). The dynamic values are the real recorded
values from the successful workflow run on tag
[`v1.0.0-led-preview`](https://github.com/sense360store/esphome-public/releases/tag/v1.0.0-led-preview)
(run
[`25918422743`](https://github.com/sense360store/esphome-public/actions/runs/25918422743)),
backfilled by RELEASE-005.

| Field | Value |
|-------|-------|
| GitHub Release URL | <https://github.com/sense360store/esphome-public/releases/tag/v1.0.0-led-preview> |
| Release tag | `v1.0.0-led-preview` (marked `prerelease: true`; the workflow derives `channel=preview`) |
| Release title | `Sense360 LED Preview Firmware v1.0.0` |
| Workflow run URL | <https://github.com/sense360store/esphome-public/actions/runs/25918422743> |
| Workflow | `Build & Release Firmware` ([`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)) |
| Workflow event | `release` with `prerelease: true` (the run was triggered on `release.published`; not `workflow_dispatch`) |
| Git SHA | `4493e0c9b3914d5dfcf41f71b4129cf23cda75d2` |
| Matrix product | `ceiling-poe-ventiq-roomiq-led` |
| Build file | [`products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq-led.yaml) (compiled; the matrix entry's `product_yaml` is the wrapper [`products/webflash/ceiling-poe-ventiq-roomiq-led.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq-led.yaml), which `!include`s the canonical YAML) |
| WebFlash config string | `Ceiling-POE-VentIQ-RoomIQ-LED` |
| Channel | `preview` |
| Version | `1.0.0` |
| Firmware asset | `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` |
| Firmware asset size | `1135904` bytes |
| SHA256 | `93310d2cbc27355e399f36a232336b6b9075dacfc178d603c7a92aa1089182d3` |
| Firmware asset URL (WebFlash import source) | <https://github.com/sense360store/esphome-public/releases/download/v1.0.0-led-preview/Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin> |
| Checksums SHA256 URL | <https://github.com/sense360store/esphome-public/releases/download/v1.0.0-led-preview/checksums-sha256.txt> |
| Checksums MD5 URL | <https://github.com/sense360store/esphome-public/releases/download/v1.0.0-led-preview/checksums-md5.txt> |
| Release manifest URL | <https://github.com/sense360store/esphome-public/releases/download/v1.0.0-led-preview/manifest.json> |
| Release-body validation | **passed** (`validate WebFlash release notes` step in `Attach to Release`) |
| Release-asset assertion | **passed** (`check WebFlash release assets` step in `Attach to Release`) |
| Uploaded assets | `.bin`, `checksums-sha256.txt`, `checksums-md5.txt`, `manifest.json` |
| Status | **proven — RELEASE-005 records the LED preview prerelease proof; ready for WebFlash import planning** |

### Release assets present

The following assets are attached to the published prerelease
[`v1.0.0-led-preview`](https://github.com/sense360store/esphome-public/releases/tag/v1.0.0-led-preview)
and were uploaded by the `Attach to Release` job in workflow run
[`25918422743`](https://github.com/sense360store/esphome-public/actions/runs/25918422743):

- [`Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`](https://github.com/sense360store/esphome-public/releases/download/v1.0.0-led-preview/Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin) (1,135,904 bytes; SHA256 `93310d2cbc27355e399f36a232336b6b9075dacfc178d603c7a92aa1089182d3`)
- [`checksums-sha256.txt`](https://github.com/sense360store/esphome-public/releases/download/v1.0.0-led-preview/checksums-sha256.txt)
- [`checksums-md5.txt`](https://github.com/sense360store/esphome-public/releases/download/v1.0.0-led-preview/checksums-md5.txt)
- [`manifest.json`](https://github.com/sense360store/esphome-public/releases/download/v1.0.0-led-preview/manifest.json) (build-info, not the WebFlash production manifest)

### Operator runbook (applied for RELEASE-005; reusable for future preview releases)

The exact sequence an operator runs to back the
[Proof record](#proof-record) above with real evidence. RELEASE-005
executed this runbook against tag `v1.0.0-led-preview` (workflow run
[`25918422743`](https://github.com/sense360store/esphome-public/actions/runs/25918422743),
git SHA `4493e0c9b3914d5dfcf41f71b4129cf23cda75d2`); this PR is
documentation-only and does not re-run steps 3–4.

1. Generate and validate the release-notes draft from the catalog. The
   generator emits Sense360 LED in `## Features` and
   `## Hardware Requirements` (not `## Known Issues`) for this entry,
   and keeps FanTRIAC in `## Known Issues` with the HW-005 reference:

   ```bash
   python3 scripts/generate_webflash_release_notes.py \
       --config-string Ceiling-POE-VentIQ-RoomIQ-LED \
       --version 1.0.0 \
       --channel preview \
       --output release-notes.md \
       --validate
   ```

   Or dispatch the
   [`Draft WebFlash Release Notes`](../.github/workflows/release-notes-draft.yml)
   workflow with `config_string=Ceiling-POE-VentIQ-RoomIQ-LED`,
   `version=1.0.0`, `channel=preview` and download the
   `release-notes.md` artifact.

2. Replace the `## Changelog` TODO bullet in `release-notes.md` with
   the human-authored, user-visible summary of changes for the LED
   preview. Re-run the validator after editing:

   ```bash
   python3 scripts/validate-webflash-release-notes.py \
       release-notes.md \
       --channel preview
   ```

3. Tag a GitHub **prerelease** on `main` using the suffix form
   `v1.0.0-led-preview` (the generic `v1.0.0-preview` is also
   accepted). LED preview release tags use suffix form such as
   `v1.0.0-led-preview`. The workflow normalizes this to
   `version=1.0.0` and `channel=preview` via
   [`scripts/derive_release_version_channel.py`](../scripts/derive_release_version_channel.py),
   so the suffixed tag can coexist with the stable Release-One tag
   `v1.0.0`. Stable releases must use plain semantic tags such as
   `v1.0.0` — suffixed tags on a non-prerelease release are rejected.
   Paste the validated release-notes body. Publish the release.

4. The
   [`Build & Release Firmware`](../.github/workflows/firmware-build-release.yml)
   workflow runs automatically on `release.published`. It derives
   `channel=preview` from `release.prerelease == true`, normalizes the
   suffixed tag to `version=1.0.0`, filters
   [`config/webflash-builds.json`](../config/webflash-builds.json) by
   `(version=1.0.0, channel=preview)` so only the LED preview entry
   builds, compiles the canonical YAML, renames the binary via
   [`scripts/product_name_mapper.py`](../scripts/product_name_mapper.py),
   and the `Attach to Release` job runs
   [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py)
   and
   [`scripts/check-webflash-release-assets.py`](../scripts/check-webflash-release-assets.py)
   before uploading the `.bin`, checksums, and `manifest.json`.

5. Back-fill the [Proof record](#proof-record) table above with the
   real GitHub Release URL, tag, workflow run URL, asset size (from the
   release page), SHA256 (read from `checksums-sha256.txt`), and gate
   pass states. Tick every box in the
   [checklist](#ceiling-poe-ventiq-roomiq-led-preview-release-proof-checklist)
   only when the corresponding evidence is recorded. RELEASE-005
   completed this back-fill for tag `v1.0.0-led-preview`.

6. The follow-up WebFlash-side PR (`WF-LED-001 — Import and manifest
   LED preview firmware`) consumes the GitHub Release asset, the
   release tag, and the SHA256 to import the preview firmware into
   WebFlash. That PR lives in the WebFlash repo, not here.

### Ceiling-POE-VentIQ-RoomIQ-LED preview release proof checklist

Every item below has actual recorded evidence backfilled by RELEASE-005.

- [x] GitHub Release tag: `v1.0.0-led-preview`
      (<https://github.com/sense360store/esphome-public/releases/tag/v1.0.0-led-preview>).
- [x] Actions run URL: `Build & Release Firmware` run
      [`25918422743`](https://github.com/sense360store/esphome-public/actions/runs/25918422743).
- [x] Artifact filename equals
      `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`.
- [x] Artifact size on the release page: `1135904` bytes (≥ 100 KB
      threshold per
      [`scripts/check-webflash-release-assets.py`](../scripts/check-webflash-release-assets.py)).
- [x] SHA256 from `checksums-sha256.txt` recorded:
      `93310d2cbc27355e399f36a232336b6b9075dacfc178d603c7a92aa1089182d3`.
- [x] Release-body validation command run and passed:
      `python3 scripts/validate-webflash-release-notes.py release-notes.md --channel preview`
      (the `validate WebFlash release notes` step in `Attach to Release`
      passed in run `25918422743`).
- [x] Generated release-notes command run and passed:
      `python3 scripts/generate_webflash_release_notes.py --config-string Ceiling-POE-VentIQ-RoomIQ-LED --version 1.0.0 --channel preview --validate`.
- [x] WebFlash import source URL recorded:
      <https://github.com/sense360store/esphome-public/releases/download/v1.0.0-led-preview/Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin>
      (the `browser_download_url` of the `.bin` asset on the published
      GitHub prerelease).
- [x] Explicit statement preserved that stable Release-One
      (`Ceiling-POE-VentIQ-RoomIQ`,
      `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`,
      tag [`v1.0.0`](https://github.com/sense360store/esphome-public/releases/tag/v1.0.0))
      is unchanged by the LED preview release.

### What RELEASE-003 does NOT do

- Does **not** itself prove a build / release artifact exists.
  RELEASE-003 only scaffolded the pending-proof record, the operator
  runbook, and the checklist; the actual proof values were backfilled
  by RELEASE-005 from a real Actions run.
- Does **not** create, tag, or publish a GitHub Release. The
  `v1.0.0-led-preview` prerelease was tagged separately, outside the
  RELEASE-003 PR.
- Does **not** run the firmware build workflow. No `.bin` was built or
  committed by the RELEASE-003 PR.
- Does **not** commit firmware binaries to git. No `.bin` is in the
  RELEASE-003 diff.
- Does **not** import anything into WebFlash. The follow-up
  `WF-LED-001` PR in the
  [`sense360store/WebFlash`](https://github.com/sense360store/WebFlash)
  repo is responsible for ingest, sidecar metadata, production
  signing, manifest generation, and deploy — none of which this repo
  performs.
- Does **not** promote `Ceiling-POE-VentIQ-RoomIQ-LED` to
  `production` / `stable`. The catalog entry stays at
  `status: preview` on the `preview` channel; production promotion
  requires the bench-verification Open Questions in
  [`docs/hardware/s360-300-r4-led.md`](hardware/s360-300-r4-led.md#open-questions--verification-needed)
  (harness rail, LED count, harness identity) to resolve first.
- Does **not** alter stable Release-One. The Release-One config
  string `Ceiling-POE-VentIQ-RoomIQ`, the Release-One artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, the
  Release-One tag `v1.0.0`, and the ESP-006 / ESP-007 proof record
  above are all preserved.
- Does **not** unblock FanTRIAC. `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`
  stays `status: blocked` under HW-005;
  `webflash_build_matrix: false`; the LED preview catalog entry
  carries `blocked_modules: ["FanTRIAC"]` so the generator places
  FanTRIAC in `## Known Issues` with the HW-005 reference.
- Does **not** modify any `config/*`, `products/*`,
  `products/webflash/*`, `packages/*`, `.github/workflows/*`,
  `scripts/*`, `tests/*`, `components/*`, or `include/*` file.

### What RELEASE-005 does NOT do

- Does **not** generate firmware. No new build is run; no `.bin` is
  produced or committed. The recorded artifact came from the
  pre-existing `v1.0.0-led-preview` workflow run
  [`25918422743`](https://github.com/sense360store/esphome-public/actions/runs/25918422743).
- Does **not** modify or replace any release asset. The `.bin`,
  `checksums-sha256.txt`, `checksums-md5.txt`, and `manifest.json`
  already attached to the prerelease are unchanged.
- Does **not** change the artifact filename, version, or channel. The
  artifact remains
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` on
  `version=1.0.0`, `channel=preview`.
- Does **not** promote `Ceiling-POE-VentIQ-RoomIQ-LED` to
  `production` / `stable`. The catalog entry stays at
  `status: preview` on the `preview` channel; production promotion
  still requires the bench-verification Open Questions in
  [`docs/hardware/s360-300-r4-led.md`](hardware/s360-300-r4-led.md#open-questions--verification-needed)
  (harness rail, LED count, harness identity) to resolve.
- Does **not** add `LED` to the stable Release-One config string.
  Release-One stays `Ceiling-POE-VentIQ-RoomIQ`,
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
  [`v1.0.0`](https://github.com/sense360store/esphome-public/releases/tag/v1.0.0),
  unchanged.
- Does **not** import the LED preview into WebFlash. WebFlash-side
  ingest, sidecar metadata, production signing, manifest generation,
  and deploy remain owned by the follow-up `WF-LED-001` PR in the
  [`sense360store/WebFlash`](https://github.com/sense360store/WebFlash)
  repo. RELEASE-005 only records the evidence WebFlash will consume.
- Does **not** unblock FanTRIAC. `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`
  stays `status: blocked` under HW-005;
  `webflash_build_matrix: false`; the LED preview catalog entry still
  carries `blocked_modules: ["FanTRIAC"]`.
- Does **not** modify any `config/*`, `products/*`,
  `products/webflash/*`, `packages/*`, `.github/workflows/*`,
  `scripts/*`, `tests/*`, `components/*`, or `include/*` file. The
  RELEASE-005 diff is limited to
  [`docs/webflash-release-proof.md`](webflash-release-proof.md),
  [`docs/product-led-preview-decision.md`](product-led-preview-decision.md),
  [`docs/product-onboarding.md`](product-onboarding.md), and
  [`docs/cleanup-audit.md`](cleanup-audit.md).

## See also

- [`docs/webflash-contract.md`](./webflash-contract.md) — full WebFlash
  compatibility contract, including §8 release-body expectations.
- [`docs/webflash-ci-alignment.md`](./webflash-ci-alignment.md) — CI/build
  alignment overview and the ESP-006 / ESP-007 rows in §"Follow-up PR
  anchors".
- [`docs/release-one.md`](./release-one.md) — Release-One configuration and
  artifact name.
- [`docs/webflash-release-handoff.md`](./webflash-release-handoff.md) —
  operational handoff and Release Proof Checklist.
- [`docs/product-led-preview-decision.md`](./product-led-preview-decision.md)
  — PRODUCT-005 LED preview product path decision doc and the
  PRODUCT-009 outstanding-proof pointer that RELEASE-003 scaffolded
  and RELEASE-005 records.
- [`docs/product-onboarding.md`](./product-onboarding.md) — cross-doc
  product onboarding guide; covers the "build / release proof" gate
  for preview / production promotion.

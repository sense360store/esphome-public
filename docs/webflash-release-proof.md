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

RELEASE-003 records the build / release proof for the LED-bearing
preview sibling
[`Ceiling-POE-VentIQ-RoomIQ-LED`](../config/webflash-builds.json) added by
PRODUCT-009. **As of this PR no proof exists.** No GitHub Release or
Actions artifact currently exists for
`Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`. Every proof
field below is marked **pending** until an operator follows the
[Operator runbook](#operator-runbook-future) and back-fills the values
from a real Actions run.

This section is **separate from** the ESP-006 / ESP-007 Release-One
proof above. The Release-One record (tag `v1.0.0`, artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, run
[`25763009641`](https://github.com/sense360store/esphome-public/actions/runs/25763009641))
is unchanged by RELEASE-003.

### Pending proof record

The static values below are already known from
[`config/webflash-builds.json`](../config/webflash-builds.json) and
[`config/product-catalog.json`](../config/product-catalog.json) (both
populated by PRODUCT-009). The dynamic values become known only after
a successful workflow run on a real prerelease tag and must be
back-filled here at that time.

| Field | Value |
|-------|-------|
| GitHub Release URL | pending |
| Release tag | pending (operator's choice; the tag must be marked `prerelease: true` so the workflow derives `channel=preview`) |
| Workflow run URL | pending |
| Workflow | `Build & Release Firmware` ([`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)) |
| Workflow event | must be `release` with `prerelease: true` (not `workflow_dispatch`; `workflow_dispatch` does not attach assets) |
| Matrix product | `ceiling-poe-ventiq-roomiq-led` |
| Build file | [`products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq-led.yaml) (compiled; the matrix entry's `product_yaml` is the wrapper [`products/webflash/ceiling-poe-ventiq-roomiq-led.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq-led.yaml), which `!include`s the canonical YAML) |
| WebFlash config string | `Ceiling-POE-VentIQ-RoomIQ-LED` |
| Channel | `preview` |
| Version | `1.0.0` |
| Firmware asset | `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` |
| Firmware asset size (release page) | pending |
| SHA256 | pending (read from `checksums-sha256.txt` once the release is published) |
| Release-body validation | pending (`validate WebFlash release notes` step in `Attach to Release`) |
| Release-asset assertion | pending (`check WebFlash release assets` step in `Attach to Release`) |
| Checksums attached | pending (`checksums-sha256.txt`, `checksums-md5.txt`) |
| Build-info manifest attached | pending (`manifest.json`) |
| Status | **pending — RELEASE-003 not yet proven** |

### Expected release assets (once published)

When the prerelease is published and the workflow run succeeds, the
following assets must be present on the release page. Until then the
list is aspirational.

- `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`
- `checksums-sha256.txt`
- `checksums-md5.txt`
- `manifest.json` (build-info, not the WebFlash production manifest)

### Operator runbook (future)

The exact sequence an operator must run before this section can be
flipped from "pending" to "proven". Do **not** run steps 3–4 from this
PR; this PR is documentation only.

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

3. Tag a GitHub **prerelease** on `main` (e.g. a tag like
   `v1.0.0-led-preview`; the exact tag string is the operator's
   choice — only the `prerelease: true` flag is load-bearing). Paste
   the validated release-notes body. Publish the release.

4. The
   [`Build & Release Firmware`](../.github/workflows/firmware-build-release.yml)
   workflow runs automatically on `release.published`. It derives
   `channel=preview` from `release.prerelease == true`, filters
   [`config/webflash-builds.json`](../config/webflash-builds.json) by
   `(version=1.0.0, channel=preview)` so only the LED preview entry
   builds, compiles the canonical YAML, renames the binary via
   [`scripts/product_name_mapper.py`](../scripts/product_name_mapper.py),
   and the `Attach to Release` job runs
   [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py)
   and
   [`scripts/check-webflash-release-assets.py`](../scripts/check-webflash-release-assets.py)
   before uploading the `.bin`, checksums, and `manifest.json`.

5. Back-fill the [Pending proof record](#pending-proof-record) table
   above with the real GitHub Release URL, tag, workflow run URL,
   asset size (from the release page), SHA256 (read from
   `checksums-sha256.txt`), and gate pass states. Tick every box in
   the [checklist](#ceiling-poe-ventiq-roomiq-led-preview-release-proof-checklist)
   only when the corresponding evidence is recorded.

6. The follow-up WebFlash-side PR (`WF-LED-001 — Import and manifest
   LED preview firmware`) consumes the GitHub Release asset, the
   release tag, and the SHA256 to import the preview firmware into
   WebFlash. That PR lives in the WebFlash repo, not here.

### Ceiling-POE-VentIQ-RoomIQ-LED preview release proof checklist

Tick each box only when there is **actual recorded evidence** for it.
Do not pre-tick any item.

- [ ] GitHub Release tag (back-fill the exact tag string here).
- [ ] Actions run URL (`Build & Release Firmware` run that produced
      the artifact).
- [ ] Artifact filename equals
      `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`.
- [ ] Artifact size on the release page (must be at least 100 KB per
      [`scripts/check-webflash-release-assets.py`](../scripts/check-webflash-release-assets.py);
      a real ESPHome firmware is ~1 MB).
- [ ] SHA256 from `checksums-sha256.txt` recorded here.
- [ ] Release-body validation command run and passed:
      `python3 scripts/validate-webflash-release-notes.py release-notes.md --channel preview`.
- [ ] Generated release-notes command run and passed:
      `python3 scripts/generate_webflash_release_notes.py --config-string Ceiling-POE-VentIQ-RoomIQ-LED --version 1.0.0 --channel preview --validate`.
- [ ] WebFlash import source URL recorded (the
      `browser_download_url` of the `.bin` asset on the published
      GitHub Release).
- [ ] Explicit statement preserved that stable Release-One
      (`Ceiling-POE-VentIQ-RoomIQ`,
      `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`,
      tag [`v1.0.0`](https://github.com/sense360store/esphome-public/releases/tag/v1.0.0))
      is unchanged by the LED preview release.

### What RELEASE-003 does NOT do

- Does **not** prove a build / release artifact exists today. Every
  field above is `pending`; do not edit this section to claim
  otherwise without an Actions run URL and a release asset to back
  the claim.
- Does **not** create, tag, or publish a GitHub Release. The repo
  still has only one release (tag `v1.0.0`, stable, Release-One only).
- Does **not** run the firmware build workflow. No `.bin` is built or
  committed by this PR.
- Does **not** commit firmware binaries to git. No `.bin` is in the
  PR diff.
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
  PRODUCT-009 outstanding-proof pointer that RELEASE-003 fills in.
- [`docs/product-onboarding.md`](./product-onboarding.md) — cross-doc
  product onboarding guide; covers the "build / release proof" gate
  for preview / production promotion.

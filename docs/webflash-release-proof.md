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

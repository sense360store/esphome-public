# WebFlash Release Asset Proof (ESP-007)

Release validation hooks are in place.
Awaiting recorded release run proof.

## Status

| Field | Value |
|-------|-------|
| GitHub Release URL | `<pending>` |
| Release tag | `<pending>` |
| Workflow run URL | `<pending>` |
| Commit SHA | `<pending>` |
| Asset filename | `<pending>` |
| Asset size (bytes) | `<pending>` |
| Release-body validation result | `<pending>` |
| Checksum file present (`checksums-sha256.txt`) | `<pending>` |
| Date / time (UTC) | `<pending>` |

## What ESP-007 enforces today

The release workflow
([`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml))
now runs two gating steps in the `release` job before any release asset is
uploaded for a `release.published` event:

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

If either step fails, asset upload is skipped and the workflow run is marked
failed. WebFlash never sees the release.

## What ESP-007 does NOT do

- Does not sign firmware (WebFlash is the production signing authority).
- Does not generate the WebFlash production-signed `manifest.json`.
- Does not deploy to WebFlash.
- Does not narrow the build matrix to "WebFlash-only"; the workflow still
  builds every YAML in `products/`. Narrowing scope is out of scope for
  ESP-007.

## How to fill in this proof

After a real release tag is published and the workflow run finishes
successfully:

1. Capture the GitHub Release URL from the release page.
2. Capture the workflow run URL from the Actions tab.
3. Confirm the
   `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` asset is
   among the published assets, and read its size from the release page.
4. Confirm `checksums-sha256.txt` is also attached.
5. Read the workflow log for the "Validate WebFlash release notes" and
   "Check WebFlash release assets" steps to record the validation result.
6. Replace each `<pending>` value above with the recorded value, and commit
   the update.

Until the table above is filled in by hand based on a real run,
**ESP-007 is not yet end-to-end proven.** Do not edit this document to
claim otherwise.

## See also

- [`docs/webflash-contract.md`](./webflash-contract.md) — full WebFlash
  compatibility contract, including §8 release-body expectations.
- [`docs/webflash-ci-alignment.md`](./webflash-ci-alignment.md) — CI/build
  alignment overview and the ESP-007 row in §"Follow-up PR anchors".
- [`docs/release-one.md`](./release-one.md) — Release-One configuration and
  artifact name.

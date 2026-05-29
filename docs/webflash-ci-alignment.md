# WebFlash CI/Build Alignment

> **⚠️ Superseded for current-state status by [`docs/sense360-roadmap-status.md`](sense360-roadmap-status.md) (DOCS-CONSOLIDATION-ROADMAP-001).**
> For the canonical, up-to-date repo status / roadmap / blocker / upcoming-PR view —
> including release targets, bundle SKUs, board SKUs, WebFlash status, the S360-410 PoE
> blocker, the FanPWM native-path status, and LED preview status — see the canonical doc.
> The content below is retained as historical / provenance detail and is **not** the
> current-state source of truth.


This document defines the boundary between the `sense360store/esphome-public`
build pipeline and the WebFlash installer. It is the planning foundation for
the `ESP-001` work item and the entry point for the `ESP-002`…`ESP-009`
follow-up PR sequence. It introduces no new rules; it pins the existing
contract to the CI/build pipeline so future changes cannot quietly drift away
from what WebFlash will accept.

## Source of truth

**WebFlash is the source of truth** for customer-facing firmware config
strings, artifact names, release metadata expectations, and install
compatibility.

This repo is the source of truth for ESPHome YAML and the build that turns it
into raw `.bin` firmware. WebFlash imports those binaries and is responsible
for signing, manifesting, and deploying them.

## Repo boundary

`esphome-public` is responsible for:

- ESPHome YAML source.
- Build validation (YAML syntax, `esphome config`, module-combination checks).
- Raw `.bin` generation.
- WebFlash-compatible artifact names.
- GitHub Release assets.
- Release-notes metadata.

`esphome-public` is **not** responsible for:

- Storing WebFlash production signing keys.
- Signing production firmware.
- Generating the WebFlash production-signed `manifest.json`.
- Deploying the WebFlash installer.

WebFlash is responsible for:

- Production signing.
- Manifest generation.
- Sidecar metadata ingestion.
- GitHub Pages deployment.
- Runtime authenticity verification.
- Customer install UX.

A note on the in-repo `manifest.json` produced by
`.github/workflows/firmware-build-release.yml`: that file is a **build-info**
manifest (per-file SHA256 and size, build timestamp, git SHA, ESPHome version)
and is distinct from the **WebFlash production-signed** manifest. The
build-info manifest is for traceability of the raw build outputs; the
production manifest is owned by WebFlash and must not be produced here.

## WebFlash contract summary

The full machine-readable contract lives in
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
and the prose contract lives in
[`docs/webflash-contract.md`](./webflash-contract.md). The summary below
exists so CI authors do not have to re-derive the rules.

### Artifact name format

Every WebFlash-compatible firmware binary must use this exact format:

```
Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin
```

Release-One example:

```
Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin
```

### Release-One required config

```
Ceiling-POE-VentIQ-RoomIQ
```

Decoded:

- Mounting: `Ceiling`
- Power: `POE`
- Air-quality module: `VentIQ`
- Room module: `RoomIQ`

> **FanTRIAC excluded from production Release-One** while HW-005 is open
> (see
> [`docs/release-one-hardware-audit.md#fantriac-mapping-resolution`](release-one-hardware-audit.md#fantriac-mapping-resolution)).
> The FanTRIAC product YAML and WebFlash wrapper are retained as blocked /
> reference files but are NOT in the WebFlash build matrix.

The Release-One product YAML lives at
[`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml),
with a thin WebFlash wrapper at
[`products/webflash/ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml).

### Canonical config-string grammar

```
{Mounting}-{Power}-{Modules...}
```

Allowed mounting tokens: `Ceiling`.

Allowed power tokens: `USB`, `POE`, `PWR`.

Allowed module tokens: `AirIQ`, `VentIQ`, `RoomIQ`, `FanRelay`, `FanPWM`,
`FanDAC`, `FanTRIAC`, `LED`.

### Compatibility rules

- `AirIQ` and `VentIQ` are mutually exclusive.
- `RoomIQ` may be combined with `AirIQ`.
- `RoomIQ` may be combined with `VentIQ`.
- Fan variants are firmware-distinct (`FanRelay`, `FanPWM`, `FanDAC`,
  `FanTRIAC`).
- `FanDAC` conflicts with `AirIQ`, as encoded in
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json).
- Generic `Fan` is forbidden.
- `FanAnalog` is legacy and must not appear in new WebFlash artifacts.
- `Bathroom`, `Comfort`, and `Presence` are not WebFlash config tokens.

### Forbidden WebFlash config tokens

These must never appear in WebFlash config strings or artifact names:

- `Bathroom`
- `Comfort`
- `Presence`
- `Fan` (generic)
- `FanAnalog`

These tokens may still exist elsewhere in the repo to support manual/custom
ESPHome users (`packages/expansions/`, `packages/features/`, legacy `Wall` and
`Mini` product YAMLs, etc.). They must not leak into the WebFlash build matrix
or any artifact filename.

## CI/build alignment checklist

The future CI/build pipeline must perform these steps in order. Each step is
annotated with the file that owns it today, or with the follow-up PR ID where
the work is tracked.

1. **Define WebFlash compatibility snapshot.** Owns
   [`config/webflash-compatibility.json`](../config/webflash-compatibility.json).
   See `ESP-003`.
2. **Define WebFlash build matrix.** Owns
   [`config/webflash-builds.json`](../config/webflash-builds.json). One entry
   today (Release-One). Extended under `ESP-005`.
3. **Add release-one ESPHome product YAML.** Owns
   [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml)
   and the WebFlash wrapper. See `ESP-004`.
4. **Validate config strings and artifact names.** Owns
   [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py)
   and the matching pre-commit hook in
   [`.pre-commit-config.yaml`](../.pre-commit-config.yaml). See `ESP-005`.
5. **Compile mapped ESPHome YAML configs.** Owns
   [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml).
   See `ESP-006`.
6. **Rename or copy outputs to WebFlash artifact names.** Owns
   [`scripts/product_name_mapper.py`](../scripts/product_name_mapper.py),
   driven by the build job above. See `ESP-006`.
7. **Upload artifacts.** Owns the upload step inside
   `firmware-build-release.yml`. See `ESP-006`.
8. **Publish GitHub Release assets.** Owns the release-attach job inside
   `firmware-build-release.yml`. See `ESP-007`.
9. **Hand off to WebFlash for import, signing, manifest, and deploy.** Owned
   by WebFlash; documented under `ESP-008`.

## Release-notes drafting

The release body required by §8 of
[`docs/webflash-contract.md`](./webflash-contract.md) can be drafted from
the product catalog with the read-only generator added in RELEASE-001.
Local invocation:

```
python3 scripts/generate_webflash_release_notes.py \
    --config-string Ceiling-POE-VentIQ-RoomIQ \
    --version 1.0.0 \
    --channel stable \
    --output release-notes.md \
    --validate
```

RELEASE-002 also wires the same generator behind a manual GitHub Actions
workflow at
[`.github/workflows/release-notes-draft.yml`](../.github/workflows/release-notes-draft.yml).
The workflow is `workflow_dispatch` only: it accepts `config_string`,
`version`, `channel` (`stable` or `preview`), and an optional
`changelog` text input; runs the generator; runs
[`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py)
against the draft; and uploads `release-notes.md` as a workflow artifact.
It does **not** create a GitHub Release, publish firmware, commit the
draft, or change the existing release-publish gates in
[`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml).
Workflow shape is locked in by the smoke test at
[`tests/test_release_notes_draft_workflow.py`](../tests/test_release_notes_draft_workflow.py),
which runs in `.github/workflows/validate.yml` on every push / PR.

The generator
([`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py),
unit-tested by
[`tests/test_generate_webflash_release_notes.py`](../tests/test_generate_webflash_release_notes.py))
produces a Markdown draft that already passes
[`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py)
on every channel, lists FanTRIAC and Sense360 LED as Known-Issues
exclusions for Release-One, and refuses blocked / legacy-compatible /
deprecated / removed entries. Human review of the `## Changelog` section
is still required — the generator emits a TODO placeholder that the
release author must replace before tagging. The generator and the
RELEASE-002 workflow do not create releases, publish firmware, infer
changelog content from git history, or change the build matrix.

## Non-goals for this repo

This repo must not:

- Store WebFlash production signing keys.
- Sign production firmware.
- Generate the WebFlash production-signed `manifest.json`.
- Deploy the WebFlash installer.
- Modify WebFlash itself.

This document also does **not** authorize:

- Deleting legacy folders or product YAMLs.
- Renaming legacy ESPHome product files.
- Changing firmware build behavior.
- Changing release workflow behavior.
- Adding new secrets to the repo.
- Breaking legacy ESPHome package paths used by manual/custom users.

## Follow-up PR anchors

| ID | Title | Status | Reference |
|----|-------|--------|-----------|
| `ESP-002` | Add WebFlash compatibility contract doc | Existing | [`docs/webflash-contract.md`](./webflash-contract.md) |
| `ESP-003` | Add local WebFlash compatibility snapshot | Existing | [`config/webflash-compatibility.json`](../config/webflash-compatibility.json) |
| `ESP-004` | Add release-one product YAML | Existing | [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml), [`products/webflash/ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml) |
| `ESP-005` | Validate WebFlash firmware config matrix | Existing (partial) | [`tests/validate_webflash_builds.py`](../tests/validate_webflash_builds.py); coverage to expand |
| `ESP-006` | Build WebFlash-compatible `.bin` artifacts in CI | Proven / verified — release `v1.0.0`, run [`25763009641`](https://github.com/sense360store/esphome-public/actions/runs/25763009641) | [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml), [`scripts/product_name_mapper.py`](../scripts/product_name_mapper.py); recorded end-to-end run attached the correctly-named `.bin` — see [`docs/webflash-release-proof.md`](./webflash-release-proof.md) |
| `ESP-007` | Publish WebFlash-compatible GitHub Release assets | Proven / verified — release `v1.0.0`, run [`25763009641`](https://github.com/sense360store/esphome-public/actions/runs/25763009641) | release-attach job in `firmware-build-release.yml` with pre-upload guards in [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py) and [`scripts/check-webflash-release-assets.py`](../scripts/check-webflash-release-assets.py); see [`docs/webflash-release-proof.md`](./webflash-release-proof.md) |
| `ESP-006` | Build WebFlash-compatible `.bin` artifacts in CI | Proven / verified — release `v1.0.0`, run [`25763009641`](https://github.com/sense360store/esphome-public/actions/runs/25763009641) | [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml), [`scripts/product_name_mapper.py`](../scripts/product_name_mapper.py), [`tests/test_webflash_artifact_naming.py`](../tests/test_webflash_artifact_naming.py), [`tests/check_webflash_build_output.py`](../tests/check_webflash_build_output.py); see "ESP-006 build proof path" below |
| `ESP-007` | Publish WebFlash-compatible GitHub Release assets | Proven / verified — release `v1.0.0`, run [`25763009641`](https://github.com/sense360store/esphome-public/actions/runs/25763009641) | release-attach job in `firmware-build-release.yml`; assets recorded on release tag `v1.0.0` — see [`docs/webflash-release-proof.md`](./webflash-release-proof.md) |
| `ESP-008` | Document WebFlash handoff | Planned | This doc covers the boundary; a dedicated handoff page may follow |
| `ESP-009` | Audit and classify legacy repo paths | Planned | Inventory `Bathroom`, `Comfort`, `Presence`, `Wall`, `Mini` usage in `packages/` and `products/` before any cleanup |

If a follow-up PR finds that an "Existing" item no longer matches this
contract, that PR should update both the implementation and this table in
the same change.

## ESP-006 build proof path

The build/upload portion of ESP-006 is proved in three layers. The first
two are deterministic and run on every push or PR. The third is a recorded
end-to-end CI run that captures the actual `.bin` artifact uploaded by
[`firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml).

1. **Static naming proof.**
   [`tests/test_webflash_artifact_naming.py`](../tests/test_webflash_artifact_naming.py)
   loads every entry in
   [`config/webflash-builds.json`](../config/webflash-builds.json) and asserts
   that
   [`scripts/product_name_mapper.py`](../scripts/product_name_mapper.py)
   produces exactly the declared `artifact_name` for the entry's
   `product_yaml` basename, version, and channel. Three explicit assertions
   pin the Release-One filename
   `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` so that
   any drift in the mapper or the build matrix fails the test. This step
   is wired into the `quick-validate` job in
   [`.github/workflows/validate.yml`](../.github/workflows/validate.yml).

2. **Build-time output assertion.**
   [`tests/check_webflash_build_output.py`](../tests/check_webflash_build_output.py)
   runs inside the build job in
   [`firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml),
   immediately after the rename step. When `webflash-builds.json` declares
   an entry whose `version` and `channel` match the current build, the
   helper fails the job unless the renamed binary's basename equals the
   declared `artifact_name`. Dev/preview dispatches that intentionally use
   non-matrix version/channel values are skipped (exit 0), so they cannot
   accidentally trip the assertion.

3. **Recorded end-to-end CI run** *(proven)*. A `release` event for tag
   `v1.0.0` invoked
   [`firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)
   in run
   [`25763009641`](https://github.com/sense360store/esphome-public/actions/runs/25763009641).
   The build job uploaded an artifact named exactly
   `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` for the matrix
   product `ceiling-poe-ventiq-roomiq`, and the `Attach to Release` job
   then published it to the release. This proves the ESP-006 build path
   end-to-end; the release-attach proof under `ESP-007` was satisfied by
   the same run.

### Proof record

| Field | Value |
|-------|-------|
| Workflow run | <https://github.com/sense360store/esphome-public/actions/runs/25763009641> |
| Workflow event | `release` |
| GitHub Release | [`v1.0.0`](https://github.com/sense360store/esphome-public/releases/tag/v1.0.0) |
| Artifact | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` |
| Artifact size (release page) | `1.04 MB` |
| Matrix product | `ceiling-poe-ventiq-roomiq` |
| Build file | [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml) |
| Status | ESP-006 and ESP-007 proven (repo-side build + Release publish) |

See [`docs/webflash-release-proof.md`](./webflash-release-proof.md) for the
full proof record, including the asset set (`.bin`, `checksums-sha256.txt`,
`checksums-md5.txt`, `manifest.json`) and the validated `Attach to Release`
sub-steps. WebFlash production signing, the production-signed `manifest.json`,
and WebFlash deploy remain WebFlash-owned and are not claimed by this proof.

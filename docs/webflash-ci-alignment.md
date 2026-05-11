# WebFlash CI/Build Alignment

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
| `ESP-006` | Build WebFlash-compatible `.bin` artifacts in CI | Existing — needs end-to-end verification | [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml), [`scripts/product_name_mapper.py`](../scripts/product_name_mapper.py); confirm a real release attaches a correctly-named `.bin` |
| `ESP-007` | Publish WebFlash-compatible GitHub Release assets | Validation hooks landed; awaiting real release run proof | release-attach job in `firmware-build-release.yml` with pre-upload guards in [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py) and [`scripts/check-webflash-release-assets.py`](../scripts/check-webflash-release-assets.py); see [`docs/webflash-release-proof.md`](./webflash-release-proof.md) |
| `ESP-006` | Build WebFlash-compatible `.bin` artifacts in CI | Proof path added; awaiting recorded CI run | [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml), [`scripts/product_name_mapper.py`](../scripts/product_name_mapper.py), [`tests/test_webflash_artifact_naming.py`](../tests/test_webflash_artifact_naming.py), [`tests/check_webflash_build_output.py`](../tests/check_webflash_build_output.py); see "ESP-006 build proof path" below |
| `ESP-007` | Publish WebFlash-compatible GitHub Release assets | Existing — needs end-to-end verification | release-attach job in `firmware-build-release.yml`; confirm assets land on a real release tag |
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

3. **Recorded end-to-end CI run** *(pending)*. Once `firmware-build-release.yml`
   is dispatched against this branch with `single_product` set to
   `sense360-ceiling-poe-ventiq-roomiq`, `version` set to `1.0.0`, and
   `channel` set to `stable`, the build job uploads a CI artifact named
   exactly `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`. When
   that run is captured, fill in the proof record below and flip the
   ESP-006 row in the table above to "Verified".

   The release-attach proof (binary attached to a real GitHub Release) is
   tracked separately under `ESP-007`.

### Proof record

> *Pending* — awaiting a recorded `workflow_dispatch` of
> [`firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)
> with `single_product=sense360-ceiling-poe-ventiq-roomiq`,
> `version=1.0.0`, `channel=stable`.

When the run lands, replace the block above with:

| Field | Value |
|-------|-------|
| Workflow run | `<URL>` |
| Artifact | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` |
| Build date | `<YYYY-MM-DD>` |
| ESPHome version | `<from workflow env.ESPHOME_VERSION>` |
| Git SHA | `<commit SHA built>` |

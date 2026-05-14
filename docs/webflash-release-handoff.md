# WebFlash Release Handoff (ESP-008)

This document describes the **operational handoff** between
[`sense360store/esphome-public`](https://github.com/sense360store/esphome-public)
(this repo — ESPHome YAML source and raw `.bin` build) and
[`sense360store/WebFlash`](https://github.com/sense360store/WebFlash) (the
browser-based installer — signing, manifest, deploy, customer install UX).

This is **not** a compatibility contract. The compatibility contract already
exists:

- [`docs/webflash-contract.md`](./webflash-contract.md) — naming rules,
  config-string grammar, release-body format, allowed/forbidden tokens,
  compatibility rules.
- [`docs/webflash-ci-alignment.md`](./webflash-ci-alignment.md) — CI/build
  alignment checklist and the boundary between CI and WebFlash.
- [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  — machine-readable snapshot of the contract.

This document explains the **release flow**: how a YAML edit becomes a signed,
deployed installer that customers can use, and which repo is responsible for
each step. It is intended for maintainers and operators, not end users.

---

## Audience

This page is for the people who run the release. After reading it you should
know:

- where firmware source lives.
- where raw binaries are built.
- where release assets are published.
- where signing happens.
- what WebFlash imports.
- which repo owns which responsibility.
- how to verify the release worked.
- what to do when WebFlash does not show a firmware build.

End-user install instructions belong on
[mysense360.com](https://mysense360.com) and in WebFlash, not here.

---

## Repository boundary

### `esphome-public` owns

- ESPHome YAML source.
- ESPHome package structure.
- Config validation.
- WebFlash compatibility snapshot
  ([`config/webflash-compatibility.json`](../config/webflash-compatibility.json)).
- WebFlash build matrix
  ([`config/webflash-builds.json`](../config/webflash-builds.json)).
- Raw `.bin` compilation.
- GitHub Release asset publishing.
- The release-note sections that WebFlash consumes.

### `WebFlash` owns

- Release asset import.
- Sidecar metadata generation.
- Production signing.
- Production manifest generation.
- Installer deployment.
- Runtime firmware verification.
- Customer install UX.
- Post-deploy smoke testing.

### Never do this in `esphome-public`

- Store WebFlash production signing private keys.
- Sign production firmware.
- Generate the WebFlash production `manifest.json`.
- Deploy the WebFlash installer.
- Bypass WebFlash signing or verification.

If a change in this repo would require any of the above, stop and route the
change through WebFlash instead.

---

## End-to-end flow

```text
ESPHome YAML source
  → CI validates config and WebFlash matrix
  → CI builds raw .bin artifacts
  → operator drafts the release body from the catalog (RELEASE-002)
  → GitHub Release publishes WebFlash-compatible .bin assets
  → WebFlash imports release assets
  → WebFlash generates sidecar metadata
  → WebFlash signs firmware
  → WebFlash generates production manifest
  → WebFlash deploys installer
  → WebFlash smoke test verifies live manifest
  → real hardware test validates flash/boot
```

Steps 1–5 happen here. Steps 6–9 happen in WebFlash. Step 10 is a human
operator with a real device. Each step is detailed in
[Handoff flow, step by step](#handoff-flow-step-by-step) below.

---

## Release-One example

The Release-One configuration is what every part of the pipeline must agree on
end-to-end. See [`docs/release-one.md`](./release-one.md) for the full slot /
file / binary mapping.

| Field | Value |
|-------|-------|
| Config string | `Ceiling-POE-VentIQ-RoomIQ` |
| Source YAML | [`products/webflash/ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml) |
| Canonical product YAML | [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml) |
| GitHub Release asset | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` |
| Channel | `stable` |
| Version | `1.0.0` |
| Chip family | `ESP32-S3` |

> **FanTRIAC excluded from production Release-One** while HW-005 is open
> (see
> [`docs/release-one-hardware-audit.md#fantriac-mapping-resolution`](release-one-hardware-audit.md#fantriac-mapping-resolution)).
> The FanTRIAC product YAML and WebFlash wrapper remain in the repo as
> blocked / reference files but are NOT in the WebFlash build matrix.

The matching matrix entry is in
[`config/webflash-builds.json`](../config/webflash-builds.json); the contract
that constrains it is in
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json).

---

## Release body format

WebFlash's release importer parses the GitHub Release body into the sidecar
metadata it stores alongside each `.bin`. The body must contain these four
H2 sections, with these exact headings, in this order. The authoritative rules
live in [`docs/webflash-contract.md` §8](./webflash-contract.md#8-release-body-expectations-webflash-metadata-import);
this section is a copy for convenience and must not drift from the contract.

```markdown
## Changelog

- Human-authored release note.

## Known Issues

- None.

## Features

- Feature item.

## Hardware Requirements

- Hardware requirement item.
```

### Release-One example release body

```markdown
## Changelog

- Initial production stable release for Ceiling-POE-VentIQ-RoomIQ with PoE
  power, VentIQ bathroom air-quality sensing, and RoomIQ room sensing.
  FanTRIAC is excluded from production Release-One while HW-005 is open.

## Known Issues

- None.

## Features

- PoE-powered Sense360 Core configuration
- VentIQ bathroom air-quality sensing
- RoomIQ room sensing

## Hardware Requirements

- Sense360 Core R4 or newer
- Sense360 PoE PSU
- Sense360 VentIQ module
- Sense360 RoomIQ module
```

The `## Changelog` section must be human-authored; generic filler
(`Initial release`, `TBD`, `Placeholder`, `No changes`, etc.) is rejected by
[`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py)
on `stable` builds.

---

## Handoff flow, step by step

### 1. Edit ESPHome source

Source lives in:

- [`products/`](../products/) — ready-to-flash device YAML.
- [`packages/`](../packages/) — base / hardware / expansion / feature packages.
- [`components/`](../components/) — custom external components (C++).
- [`include/`](../include/) — header bundles consumed by components.

The Release-One entry is declared in:

- [`config/webflash-builds.json`](../config/webflash-builds.json) — binds a
  WebFlash `config_string` to a product YAML, version, channel, and artifact
  name.

The compatibility rules that constrain entries live in:

- [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  — filename pattern, allowed tokens, forbidden tokens, mutual-exclusion
  rules, allowed channels.

If you are adding or changing a build, edit `webflash-builds.json` and the
product YAML in the same change. If you are changing the rules themselves,
update `webflash-compatibility.json` and
[`docs/webflash-contract.md`](./webflash-contract.md) in the same PR.

### 2. Validate locally / in CI

Run these from the repo root before opening a PR. CI runs the same checks.

```bash
python3 tests/validate_webflash_builds.py
python3 tests/test_webflash_compatibility.py
python3 tests/validate_configs.py
```

The build matrix and artifact-name proof land here:

```bash
python3 tests/test_webflash_artifact_naming.py
python3 tests/test_validate_webflash_release_notes.py
```

The release-time guards used by the publish job (also runnable locally):

```bash
python3 scripts/validate-webflash-release-notes.py --help
python3 scripts/check-webflash-release-assets.py --help
```

If you have `pre-commit` installed:

```bash
pre-commit run --all-files
yamllint .
```

If `pre-commit` or `yamllint` are not installed locally, that is fine — the
same checks run in CI.

### 3. Build firmware in `esphome-public`

CI builds **raw unsigned `.bin`** artifacts. This repo never signs production
firmware.

Required filename pattern (enforced by
[`scripts/product_name_mapper.py`](../scripts/product_name_mapper.py) and
asserted by
[`tests/test_webflash_artifact_naming.py`](../tests/test_webflash_artifact_naming.py)):

```text
Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin
```

Release-One builds to:

```text
Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin
```

The build job lives in
[`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml).

### 4. Draft the release body (RELEASE-002)

Before tagging a release, draft the release body from the catalog. Either
run the read-only generator locally:

```bash
python3 scripts/generate_webflash_release_notes.py \
    --config-string Ceiling-POE-VentIQ-RoomIQ \
    --version 1.0.0 \
    --channel stable \
    --output release-notes.md \
    --validate
```

…or manually dispatch the
[`Draft WebFlash Release Notes`](../.github/workflows/release-notes-draft.yml)
workflow (`workflow_dispatch` only) and download the `release-notes.md`
workflow artifact. The workflow runs the generator, runs
[`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py)
against the draft, and uploads the result. It does **not** create a
GitHub Release, publish firmware, or commit the draft.

The generated `## Changelog` section starts as a TODO bullet that
deliberately survives structural validation; replace it with the actual
user-visible changes for the release before pasting the body into the
GitHub Release. Filler text (`TBD`, `Placeholder`, `Initial release`,
etc.) is still rejected at publish time on `stable`.

### 5. Publish GitHub Release assets

When a release tag is published, the workflow attaches:

- the `.bin` files matching the build matrix for `(version, channel)`.
- a checksums file, if generated.
- a release body containing the four required sections from
  [Release body format](#release-body-format).

Two pre-upload gates run before assets are attached:

- [`scripts/validate-webflash-release-notes.py`](../scripts/validate-webflash-release-notes.py)
  — checks the four H2 sections, bullet content, and rejects filler changelog
  text on `stable`.
- [`scripts/check-webflash-release-assets.py`](../scripts/check-webflash-release-assets.py)
  — for every matrix entry matching the release `(version, channel)`,
  verifies the declared `artifact_name` is present and is at least 100 KB.
  Fails closed if no matrix entry matches.

> **ESP-007 end-to-end release proof is recorded** for the repo-side publish
> path. Release [`v1.0.0`](https://github.com/sense360store/esphome-public/releases/tag/v1.0.0)
> attached `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` (1.04 MB)
> via run
> [`25763009641`](https://github.com/sense360store/esphome-public/actions/runs/25763009641)
> after the `validate-webflash-release-notes` and `check-webflash-release-assets`
> gates passed. See
> [`docs/webflash-release-proof.md`](./webflash-release-proof.md) for the
> full record. WebFlash import, sidecar generation, production signing,
> production manifest generation, deploy, and smoke test remain WebFlash-owned
> and are **not** proven by this record.

### 6. WebFlash imports release assets

WebFlash's release importer reads the new release's assets and the release
body, then generates the per-firmware sidecar metadata it needs to drive the
installer wizard. This step happens entirely in WebFlash; this repo only
needs to make the upstream artifacts and release body discoverable and
correctly named.

### 7. WebFlash signs firmware

Production signing runs **only inside WebFlash**, using WebFlash-controlled
secrets. The unsigned `.bin` published from this repo is the input; the
signed payload that ships to customers is the output, produced and stored in
WebFlash.

This repo must never hold the production signing private key, sign firmware,
or attempt to bypass signing.

### 8. WebFlash generates manifest and deploys

WebFlash builds the production installer manifest (`manifest.json` /
`firmware-N.json`) from the signed binaries and its own metadata, then
deploys to its hosting target (today: GitHub Pages on the WebFlash repo).

The build-info `manifest.json` produced inside this repo's release workflow
is **not** the WebFlash production manifest — see
[`docs/webflash-ci-alignment.md`](./webflash-ci-alignment.md) for the
distinction.

### 9. WebFlash smoke test validates live deployment

The post-deploy smoke test in WebFlash should confirm at minimum:

- the installer manifest is reachable from the live URL.
- the source commit referenced by the manifest is current.
- the Release-One `config_string` is present in the manifest.
- no placeholder / tiny firmware was published.
- the production signing key was used.
- a rescue firmware exists for recovery flows.

Smoke-test wiring lives in WebFlash. This repo cannot diagnose a smoke-test
failure on its own; it can only verify the upstream artifacts.

### 10. Real hardware test

CI is not enough. A human operator must still flash a real device and verify:

- firmware flashes successfully via WebFlash.
- the device boots.
- Wi-Fi setup / Improv handoff completes.
- RoomIQ and VentIQ behave sanely (sensors report).
- the rescue path remains available.

The Release Proof Checklist below is not "done" until this hardware step has
been performed and recorded.

---

## Troubleshooting

### WebFlash does not show the firmware

Likely causes:

- The asset name does not match the WebFlash artifact contract
  (`Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin`).
- The release was not picked up by WebFlash's release importer.
- The `config_string` is missing from WebFlash's manifest.
- The `config_string` is missing from the WebFlash kit / SKU mapping.
- The release body did not parse (a required H2 section is missing or
  reordered).
- WebFlash's sidecar metadata was not generated for the asset.
- WebFlash's manifest generation step failed.

Start by re-reading the failing release in WebFlash's importer logs; cross-
check the artifact name against
[`config/webflash-builds.json`](../config/webflash-builds.json).

### WebFlash shows the firmware but blocks install

Likely causes:

- The firmware was not signed by the WebFlash production key.
- WebFlash's manifest freshness check failed.
- Signature verification failed at install time.
- The artifact is a placeholder or is implausibly small.
- The config the user picked in the wizard does not match the artifact
  (e.g. wrong fan driver).
- The build is marked deprecated.
- The channel is `preview` or `beta` and the user has not acknowledged the
  channel warning.

These all point at WebFlash-side state. This repo cannot fix them by
republishing the `.bin`; the fix is in the WebFlash deployment.

### GitHub Release workflow fails

Likely causes:

- The ESPHome compile step failed (YAML / package error).
- The release notes are missing one of the four required H2 sections, or
  contain filler changelog text on `stable`.
- An expected WebFlash artifact was not produced for the target
  `(version, channel)`.
- An artifact came out implausibly small (under the 100 KB floor enforced
  by `scripts/check-webflash-release-assets.py`).
- [`scripts/product_name_mapper.py`](../scripts/product_name_mapper.py)
  drifted from the build matrix.
- [`config/webflash-builds.json`](../config/webflash-builds.json) drifted
  from the canonical product YAML in `products/`.

Reproduce locally with the validators in [step 2](#2-validate-locally--in-ci)
before re-running the workflow.

### Manual / custom users are confused

Likely causes:

- They should be using WebFlash, not raw ESPHome — point them at
  [mysense360.com](https://mysense360.com).
- They forgot to copy
  [`secrets.example.yaml`](../secrets.example.yaml) to `secrets.yaml`.
- They referenced `ref: main` instead of a release tag — production users
  must pin to a tag (e.g. `ref: v1.0.0`).
- They picked the wrong product YAML for their hardware (wrong mounting,
  power, fan driver, etc.).

The README "Quick Start" and "Configuration Approaches" sections cover the
manual path; route confused users there if WebFlash is genuinely not what
they want.

---

## Release Proof Checklist

Tick each box only when there is **actual recorded evidence** for it (workflow
run URL, release URL, hardware test record). Do not pre-check items.

- [x] `esphome-public` workflow completed successfully.
      (run [`25763009641`](https://github.com/sense360store/esphome-public/actions/runs/25763009641),
      event `release`, tag `v1.0.0`)
- [x] Release-One `.bin` artifact exists.
      (`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` attached to
      [`v1.0.0`](https://github.com/sense360store/esphome-public/releases/tag/v1.0.0))
- [x] Artifact name exactly matches the WebFlash contract.
- [x] Artifact size is plausible for ESPHome firmware. (1.04 MB on the
      release page)
- [x] Release body passed validation. (`validate WebFlash release notes`
      and `check WebFlash release assets` both passed in `Attach to Release`)
- [ ] WebFlash imported the release asset.
- [ ] WebFlash generated the metadata sidecar.
- [ ] WebFlash signed the firmware with the production key.
- [ ] WebFlash manifest includes the Release-One config string.
- [ ] WebFlash deployment smoke test passed.
- [ ] Real hardware flash test passed.

> Repo-side ESP-006 and ESP-007 are proven by release `v1.0.0` and run
> [`25763009641`](https://github.com/sense360store/esphome-public/actions/runs/25763009641);
> see [`docs/webflash-release-proof.md`](./webflash-release-proof.md). The
> remaining unchecked boxes cover WebFlash import, signing, manifest,
> deploy, smoke test, and real-hardware flash, all of which are owned
> outside this repo and have not been recorded here.

---

## See also

- [`docs/webflash-contract.md`](./webflash-contract.md) — WebFlash
  compatibility contract: artifact naming, config-string grammar, release-
  body expectations.
- [`docs/webflash-ci-alignment.md`](./webflash-ci-alignment.md) — CI/build
  alignment overview and the boundary between CI and WebFlash.
- [`docs/release-one.md`](./release-one.md) — Release-One configuration with
  full slot/file/binary mapping.
- [`docs/webflash-release-proof.md`](./webflash-release-proof.md) — open
  ESP-007 release proof record.
- [`docs/repo-structure-audit.md`](./repo-structure-audit.md) — top-level
  repo path classification.
- [`docs/manual-user-walkthrough.md`](./manual-user-walkthrough.md) — test
  plan and findings template for validating the manual / custom ESPHome
  path with a real tester.
- [`config/webflash-builds.json`](../config/webflash-builds.json) — declared
  build matrix.
- [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  — machine-readable contract snapshot.

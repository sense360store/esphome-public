# Dev workflow: bench testing repo configs before PR

This document codifies the supported path for developing and bench-testing
firmware changes on real hardware before they reach a PR. The YAML compiled
and flashed on the bench is the literal repo source on a feature branch —
there is no translation step between bench and PR.

The harness lives in [`dev/`](../dev/): a device template
([`dev/device-template.yaml`](../dev/device-template.yaml)), a scratch
overlay ([`dev/dev-overlay.yaml`](../dev/dev-overlay.yaml)), and a secrets
template ([`dev/secrets.yaml.example`](../dev/secrets.yaml.example)).
Nothing under `dev/` is ever release-eligible; see
[Guarantees](#guarantees) below.

## Prerequisites

- A Home Assistant install with the ESPHome add-on (dashboard).
- A bench device (e.g. a Sense360 Core S360-100 with the module set matching
  the entry point under test).
- Push access to a feature branch of this repository.

## The loop

1. **Branch.** Branch the repo from `main`
   (`git checkout -b feat/<change> origin/main`).

2. **Create the bench device.** In the Home Assistant ESPHome dashboard,
   create a device manually and paste in a copy of
   `dev/device-template.yaml` (this is the content of your
   `dev/<name>.local.yaml`). Set `ref:` to the feature branch and `files:`
   to the entry point config under test — a real `products/*.yaml` path,
   e.g. `products/sense360-ceiling-poe-ventiq-roomiq.yaml` (Release-One,
   the default in the template). Copy the keys from
   `dev/secrets.yaml.example` into the dashboard secrets editor and fill in
   real bench values. All seven keys are required: `wifi_ssid`,
   `wifi_password`, `fallback_ap_password`, `api_encryption_key`,
   `ota_password`, `web_username`, `web_password`.

3. **First flash over USB, then OTA.** The first flash on a blank board is
   over USB via the dashboard's web serial installer. Every subsequent
   flash is OTA (the `ota_password` secret authenticates it).

4. **Make the change.** Either edit the correct package layer directly on
   the branch (`packages/boards/`, `packages/base/`, `packages/features/`,
   or the bundle under `products/bundles/`), or — when the correct home for
   the change is not yet clear — sketch it in `dev/dev-overlay.yaml` first.
   The overlay is merged into the bench device by the template
   (`overlay: !include dev-overlay.yaml`) and is the only place where
   uncommitted experimentation belongs.

5. **Push, install, test.** Push the branch and hit Install in the
   dashboard. With `refresh: 0s` the add-on re-pulls the branch source on
   every compile, builds locally, and flashes OTA. Test the entities in
   Home Assistant.

6. **Promote and open the PR.** When the change is proven, promote anything
   still in `dev-overlay.yaml` into its proper package layer, return the
   overlay to its empty committed state (comments only), push, and open the
   PR. CI blocks merging while the overlay contains functional content
   (`scripts/check_dev_harness_guard.py`, run by `validate.yml`). Record
   bench evidence in the PR description: which device, which firmware entry
   point, and what was verified.

7. **CI and release are unchanged.** The existing gates (`validate.yml`
   quick validation, the compile-only lane) run on the PR as normal.
   Release proceeds through the existing GitHub Release pipeline
   (`firmware-build-release.yml`, driven by `config/webflash-builds.json`)
   unchanged — the dev harness adds nothing to it.

## Local clone variant (no push per iteration)

For fast iteration the template carries a commented-out alternative: clone
the repo into the ESPHome add-on's config directory and replace the remote
`sense360_source:` git block with a direct `!include` of the same entry
point (path relative to where the device YAML lives — from inside the
clone's `dev/` directory it is
`../products/sense360-ceiling-poe-ventiq-roomiq.yaml`). Edits to the clone
compile immediately, with no push per iteration.

When to use which:

- **Remote git method (default).** Use when you want the bench build to be
  exactly the pushed branch head — the state a reviewer and CI will see —
  and for any final verification pass before opening the PR. Also the only
  method available when the ESPHome add-on host has no clone of the repo.
- **Local clone method.** Use for tight edit-compile-flash cycles during
  active development, when a push per iteration is too slow. The bench
  diverges from the pushed branch between pushes, so always finish with at
  least one remote-method (or pushed-and-pulled) build before recording
  bench evidence in the PR.

## Guarantees

- **`dev/` is never built or released.** Every build, compile, and release
  matrix in this repo is declaration-driven: the release matrix comes from
  `config/webflash-builds.json` (ESP-007, `firmware-build-release.yml`),
  the compile-only lane from `config/compile-only-targets.json`, the
  preview dry-run lane from `config/preview-release-targets.json`, the
  manual-artifact lane from `config/manual-firmware-artifacts.json`, and
  the legacy manual sweep (`ci-validate-configs.yml`) globs `products/**`
  only. None of them can select `dev/`. The guard
  `scripts/check_dev_harness_guard.py` additionally fails any PR where a
  `config/*.json` declaration references a `dev/` path, so the guarantee is
  pinned, not just documented.
- **The committed overlay stays empty.** The same guard fails any PR where
  `dev/dev-overlay.yaml` contains anything other than comments and blank
  lines: promote overlay content into a package layer before merge.
- **No real secrets in the tree.** `dev/secrets.yaml` and
  `dev/*.local.yaml` are gitignored; the committed templates carry
  `REPLACE_ME_` placeholders only, none of which matches the release
  binary scanner's denylist
  (`scripts/check_firmware_default_credentials.py`).
- **Dev builds stay on the bench.** Firmware built from a `dev/` device
  file is a development build of an unreviewed branch. Never flash it on a
  device outside the bench.

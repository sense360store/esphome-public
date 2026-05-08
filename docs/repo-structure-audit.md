# Repo Structure Audit (ESP-009 / ESP-010)

This document classifies every major top-level path in `sense360-store/esphome-public`
and inspects `secrets.yaml` for safety in a public repository.

It is an **audit and classification document only**. No files are deleted,
renamed, or restructured by the PR that introduces this document. Recommended
follow-up changes are listed at the end.

## Audit method

For each top-level path I checked:

1. Whether it is referenced by current product YAML (`products/**/*.yaml`).
2. Whether it is referenced by package YAML (`packages/**/*.yaml`).
3. Whether it is referenced by examples (`examples/**/*.yaml`).
4. Whether it is referenced by docs (`docs/**/*.md`, `README.md`, `packages/README.md`).
5. Whether it is referenced by CI (`.github/workflows/**`), tests, or scripts.
6. Whether it is exposed as part of the public ESPHome remote-package surface
   (`packages:`, `external_components:`, or `includes:` with a
   `github://sense360store/esphome-public/...` URL).
7. Whether it is a compatibility alias / legacy shim.

Searches used (representative):

```
grep -rn "components/"     --include="*.yaml" --include="*.md" --include="*.py"
grep -rn "include/"        --include="*.yaml" --include="*.md" --include="*.cpp" --include="*.h"
grep -rn "packages/base"   --include="*.yaml" --include="*.md"
grep -rn "secrets.yaml"    --include="*.yaml" --include="*.md" --include="*.py" --include="*.yml"
grep -rn "github://"       --include="*.yaml" --include="*.md"
git ls-files | grep -i secret
readlink base features hardware products/secrets.yaml
```

Status vocabulary:

- `active` — currently referenced and required.
- `public-api` — referenced by external consumers via `github://` URL or
  `packages:` block; renaming or deleting would be a breaking change.
- `legacy-compatibility` — older path or alias that may still be referenced
  externally; keep until a documented migration window passes.
- `candidate-for-removal` — has no references and a replacement exists.
- `dead` — proven unused.
- `unknown` — could not classify confidently; keep.

## Top-level path classification

| Path | Status | Reason | Recommended Action |
| --- | --- | --- | --- |
| `components/` | public-api | Holds ESPHome external components `ld2412`, `ld2450`, `ld24xx`. Loaded at build time via `packages/base/external_components.yaml`, which uses a `git` source pointing at this repo and lists `components: [ld2412, ld2450, ld24xx]`. CI path filters in `.github/workflows/ci-validate-configs.yml` watch `components/**`. Renaming this path would break every product build and any external consumer pinned to a tag. | Keep. Treat as public API. |
| `include/` | public-api | Contains `include/sense360/{led_logic,thresholds,calibration,time_utils}.h`. Referenced as `github://sense360store/esphome-public/include/sense360/...@v2.0.0` from `examples/custom-with-remote-headers.yaml`, `include/README.md`, `tests/README.md`, and `tests/INTEGRATION_GUIDE.md`. Also referenced as `../include/sense360/...` from `packages/features/{ceiling_led_ring_air_quality,mini_four_leds_air_quality}.yaml` and from `tests/unit/test_*.cpp`. | Keep. Treat as public API. |
| `base/` | legacy-compatibility | Symlink → `packages/base`. Confirmed via `readlink base` → `packages/base`. Not a duplicate, not a stale copy. The pre-commit regex `^(products\|packages\|base\|features\|hardware)/.*\.yaml$` in `.pre-commit-config.yaml` and the bare-path uses in `tests/quick_check_duplicates.sh` rely on it being walkable. External users on older docs may still reference `base/wifi.yaml` directly. | Keep. Plan a deprecation in a separate PR. |
| `features/` | legacy-compatibility | Symlink → `packages/features`. Same situation as `base/`. `tests/quick_check_duplicates.sh` greps `features/` directly. `tests/INTEGRATION_GUIDE.md` and `docs/configuration.md` document feature files as `features/<name>.yaml`. | Keep. Plan a deprecation in a separate PR. |
| `hardware/` | legacy-compatibility | Symlink → `packages/hardware`. Same situation as `base/`. `tests/quick_check_duplicates.sh` greps `hardware/` directly. | Keep. Plan a deprecation in a separate PR. |
| `packages/` | active, public-api | Canonical home for `base/`, `features/`, `hardware/`, plus `expansions/`. All product YAML files in `products/` `!include` from `../packages/...`. `packages/README.md` and `docs/product-matrix.md` document this as the public package surface. CI workflows `sed`-rewrite `packages/base/external_components.yaml` for branch builds. | Keep. Treat `packages/{base,features,hardware,expansions}` as public API. |
| `products/` | active, public-api | 33 product YAML files, plus `webflash/` subdir, plus `products/secrets.yaml` symlink → `../secrets.yaml`. Products are the entry point users `!include` from a `packages:` block (see `packages/README.md`). | Keep. Treat as public API. |
| `examples/` | active | `customer-basic.yaml`, `custom-with-remote-headers.yaml`, `secrets.yaml.template`. Public-facing usage examples; `secrets.yaml.template` is the canonical user-copy source. | Keep. |
| `docs/` | active | Mix of `.md` (configuration, board-combinations, product-matrix, webflash-contract, etc.) and `.html` snapshots. `.md` files are referenced from `README.md` and `packages/README.md`. The `.html` files were not deeply audited here (out of scope). | Keep. Audit `.html` alignment with WebFlash taxonomy in a follow-up. |
| `tests/` | active | Validators that run in CI: `validate_configs.py`, `validate_webflash_builds.py`, `test_webflash_compatibility.py`. Generators: `generate_test_configs.py`, `batch_validate_esphome.py`. Unit tests under `tests/unit/`, ESPHome integration configs under `tests/esphome/`, helper script `quick_check_duplicates.sh`. | Keep. |
| `scripts/` | active | Single helper `product_name_mapper.py`. Not deeply traced; treat as helper tooling. | Keep. |
| `config/` | active | `webflash-builds.json`, `webflash-compatibility.json`. Watched by the pre-commit `validate-webflash-builds` hook (`files: ^(config/webflash-(builds\|compatibility)\.json\|tests/validate_webflash_builds\.py)$`) and consumed by `tests/validate_webflash_builds.py`. | Keep. |
| `.github/workflows/` | active | `ci-validate-configs.yml`, `firmware-build-release.yml`, `validate.yml`. Build, validate, and release flows. | Keep. Out of scope for this PR. |
| `requirements-dev.txt` | active | Pre-commit, yamllint, black, flake8, esphome, pytest. Referenced from `docs/development.md` and `CHANGELOG.md`. | Keep. |
| `.yamllint` | active | YAML lint config, consumed by `pre-commit` and `yamllint .`. | Keep. |
| `.pre-commit-config.yaml` | active | Pre-commit hook config; references `validate_configs.py` and `validate_webflash_builds.py`, and includes the legacy `(products\|packages\|base\|features\|hardware)` regex. | Keep. Update regex when the symlink aliases are removed in a follow-up PR. |
| `secrets.yaml` | legacy-compatibility / footgun | Tracked file with a header that explicitly states "placeholder values for CI/CD validation". `.gitignore` lists `secrets.yaml`, so the tracked copy was force-added; subsequent edits will not be picked up by `git add` without `-f`. CI workflows (`ci-validate-configs.yml`, `firmware-build-release.yml`) overwrite this file at runtime via heredoc, so the tracked copy is only effectively used for local validation runs. See dedicated section below. | Keep for now. Follow-up PR should rename to `secrets.example.yaml`. |
| `CHANGELOG.md`, `LICENSE`, `README.md`, `.gitignore` | active | Standard repo metadata. | Keep. |

## `components/` deep dive

```
components/
  ld2412/   __init__.py, binary_sensor.py, button/, ld2412.cpp, ld2412.h, number/, select/, sensor.py, switch/, text_sensor.py
  ld2450/   __init__.py, binary_sensor.py, button/, ld2450.cpp, ld2450.h, number/, select/, sensor.py, switch/, text_sensor.py
  ld24xx/   __init__.py, ld24xx.h
```

This is an ESPHome external-component tree (Python platform shims plus C++).
It is loaded by `packages/base/external_components.yaml`:

```
external_components:
  - source:
      type: git
      url: https://github.com/sense360store/esphome-public
      ref: main
    components: [ld2412, ld2450, ld24xx]
```

That file is `!include`d by every product YAML that needs radar support and is
patched to the build branch by CI before validation. Any rename or deletion of
`components/`, `components/ld2412`, `components/ld2450`, or `components/ld24xx`
is a breaking change for both this repo's own builds and any external consumer
pinned to a release tag.

**Conclusion: keep. Treat as public API.**

## `include/` deep dive

```
include/
  README.md
  sense360/
    calibration.h
    led_logic.h
    thresholds.h
    time_utils.h
```

Internal references (relative paths from `packages/features/*.yaml` and from
`tests/unit/test_*.cpp`) and external references
(`github://sense360store/esphome-public/include/sense360/<header>.h@v2.0.0` in
`examples/custom-with-remote-headers.yaml`, `include/README.md`, and
`tests/README.md`) prove this is part of the public consumption surface.

**Conclusion: keep. Treat as public API.**

## `base/`, `features/`, `hardware/` symlinks (not duplicates)

These three top-level entries are **symlinks**, not directories:

```
$ readlink base features hardware
packages/base
packages/features
packages/hardware
```

They are **not** stale copies, **not** duplicates, and **not** compatibility
shims that diverge from `packages/`. They are the same content reached by a
shorter path.

Why they still matter:

- `tests/quick_check_duplicates.sh` greps bare `features/`, `hardware/`, and
  `products/` directly:
  ```
  grep -rn "name:.*Restart" features/ hardware/ products/ --include="*.yaml"
  grep -q "platform: restart" features/device_health.yaml
  ```
  Removing the symlinks would break this script.
- `.pre-commit-config.yaml` regex `^(products\|packages\|base\|features\|hardware)/.*\.yaml$`
  walks them.
- `README.md` and `tests/INTEGRATION_GUIDE.md` document files using bare
  `features/<name>.yaml` and `hardware/<name>.yaml` notation.
- External users on older versions of `packages/README.md` may still reference
  bare paths in their own `packages:` blocks.

**Conclusion: classify as `legacy-compatibility`. Keep in this PR. Plan a
deprecation pass in a separate PR that:**

- Migrates `tests/quick_check_duplicates.sh` to `packages/features/`, `packages/hardware/`.
- Tightens the pre-commit regex to `^(products\|packages)/.*\.yaml$`.
- Updates `README.md` / `tests/INTEGRATION_GUIDE.md` / `docs/configuration.md` to use canonical paths.
- Adds a deprecation note in `packages/README.md` with a removal-version target.
- Only after a documented release, removes the symlinks.

## `secrets.yaml` deep dive

### What is in it

The tracked `secrets.yaml` is 53 lines. The header comment reads:

```
# This file contains placeholder values for CI/validation.
# For actual deployment, users should use the template in examples/secrets.yaml.template
```

Values:

- `wifi_ssid: "TestSSID"` — placeholder.
- `wifi_password: "TestPassword123"` — placeholder.
- `ota_password: "test_ota_password"` — placeholder.
- `fallback_ap_password: "test_fallback_password"` — placeholder.
- `web_username: "admin"`, `web_password: "test_web_password"` — placeholder.
- `mqtt_broker: "192.168.x.x"`, `mqtt_port: "1883"`, `mqtt_username: "test_mqtt_username"`, `mqtt_password: "test_mqtt_password"` — placeholders.
- `airiq_mqtt_*` — duplicates of the MQTT placeholders for the AirIQ profile.
- `api_encryption_key: "ApffT4MKmN2YvwNQ8yZonXafTHzAmCMhBq8Cjq+jEDQ="` — a syntactically valid 32-byte base64 key. The surrounding values strongly suggest this is an example key, but it is opaque and there is no way from outside to prove it has never been deployed to a real device.

### How it is used

- `git ls-files` shows `secrets.yaml`, `examples/secrets.yaml.template`, and
  `products/secrets.yaml` (a symlink → `../secrets.yaml`) are all tracked.
- `.gitignore` line 2 lists `secrets.yaml`. Because the tracked file pre-exists
  the ignore entry, git keeps tracking it; new contributors who would expect
  the ignore rule to apply may be surprised when changes to it cannot be
  staged with a normal `git add`.
- CI does **not** trust the tracked file. `.github/workflows/ci-validate-configs.yml`
  and `.github/workflows/firmware-build-release.yml` both write a fresh
  `secrets.yaml` via heredoc, then `rm -f products/secrets.yaml tests/secrets.yaml`
  and copy the freshly written file in place. So the tracked copy is only
  effectively used for local validation runs (`pre-commit`, `yamllint`,
  `python tests/validate_configs.py` from a clean checkout).

### Risk classification

- The header and the surrounding values mark this as **placeholder material**,
  not a live secrets file.
- It is nonetheless **publishing a complete-looking, syntactically valid
  set of credentials** — including a base64 API encryption key — from the
  default branch of a public repo. Any device that ever booted with this
  exact key would have a publicly known key.
- The `.gitignore`-but-tracked state is a footgun: a future contributor who
  accidentally pastes a real key into this file may not notice that
  `git status` still reports it (because it is already tracked).

### Recommended follow-up (do not do in this PR)

A separate PR should:

1. **Rename** the tracked file from `secrets.yaml` to `secrets.example.yaml`
   so the gitignore rule on `secrets.yaml` is honored for everyone.
2. **Keep `secrets.yaml` gitignored** so a developer's local fill-in never
   gets staged accidentally.
3. **Update local-dev instructions** in `README.md`, `docs/development.md`,
   and `examples/secrets.yaml.template` so they all consistently say:
   "copy `secrets.example.yaml` (or `examples/secrets.yaml.template`) to
   `secrets.yaml`".
4. **Update the `products/secrets.yaml` symlink** to point at the new
   `secrets.example.yaml`, or remove it and instead document the local-dev
   step.
5. **Update CI fallback behavior** in
   `.github/workflows/ci-validate-configs.yml` and
   `.github/workflows/firmware-build-release.yml` so that, if any flow
   currently relies on the tracked `secrets.yaml`, it falls back to
   `secrets.example.yaml` (or to its own heredoc, which it already does for
   most of the matrix).
6. **Rotate `api_encryption_key`** if there is any chance the value
   `ApffT4MKmN2YvwNQ8yZonXafTHzAmCMhBq8Cjq+jEDQ=` was ever reused on real
   hardware. The check is cheap, the failure mode is a publicly known
   encryption key on a deployed device, and the cost of rotating an unused
   placeholder is zero.
7. **Add a CI guard** that rejects commits introducing a top-level
   `secrets.yaml` containing values that are not on a known-placeholder
   list (extension of point 4 of the follow-up list below).

For this PR: **classified as `legacy-compatibility`. Not deleted. Not
edited. Recommendation captured here for a separate PR.**

## Recommended Follow-Up PRs

1. Rename tracked `secrets.yaml` to `secrets.example.yaml`; keep `secrets.yaml`
   gitignored; update local-dev instructions; update the
   `products/secrets.yaml` symlink and any CI fallback behavior; rotate the
   `api_encryption_key` if there is any chance it was reused on real
   hardware.
2. Remove confirmed dead duplicate folders if any are found by a deeper
   review (none were found at top level in this audit).
3. Add compatibility docs for legacy package paths
   (`base/`, `features/`, `hardware/`) explaining that they are symlinks into
   `packages/` and announcing a removal-version target.
4. Add a CI check preventing stale duplicate package copies (e.g., reject
   PRs that add a real directory at `base/`, `features/`, or `hardware/`
   instead of using `packages/...`).
5. Align remaining docs/examples (including the `docs/*.html` snapshots) to
   the WebFlash taxonomy documented in `docs/webflash-contract.md`.

## Out of scope for this PR

- No firmware build behavior changes.
- No WebFlash compatibility contract changes.
- No release workflow changes.
- No deletions, renames, or restructuring.
- No edits to `secrets.yaml`, `products/secrets.yaml`, `.gitignore`, CI
  workflows, product YAML, package YAML, symlinks, or `.pre-commit-config.yaml`.

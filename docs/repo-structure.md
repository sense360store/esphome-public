# Repository Structure & Reference Map

> **Scope.** This is the canonical **structural** reference for
> `sense360store/esphome-public`: what the top-level directories are, how they
> wire together, and the proof of which paths are active. For live **release /
> roadmap / blocker status** (preview vs stable, S360-410 PoE, LED preview,
> FanPWM bench gates) the single source of truth remains
> [`docs/sense360-roadmap-status.md`](sense360-roadmap-status.md). The older
> path-classification audit [`docs/repo-structure-audit.md`](repo-structure-audit.md)
> (ESP-009 / ESP-010) is retained as historical provenance; this document
> refreshes it for the current `products/` subfolder layout and the
> bundle / shim / wrapper include chain.

This document was produced by **REPO-STRUCTURE-AUDIT-001**. It is an
**audit / classification document only** — the PR that introduced it deletes,
renames, and restructures **nothing**. Its purpose is to prove, before the next
preview build-fix PR adds files under `products/bundles/`, whether the top-level
`components/` and `products/` directories are active, legacy, or removable.

## TL;DR — audit result

| Directory | Classification | Decision |
| --- | --- | --- |
| `components/` | **active** (build dependency + public ESPHome remote-package surface) | **KEEP.** Not legacy, not removable. No follow-up removal opened. |
| `products/` | **active** (release / build / test / config backbone) | **KEEP.** No obsolete subfolders found. |
| `products/bundles/` | **active** (canonical composition layer; preview targets resolve here) | **KEEP.** This is where the next functional PR adds files. |
| `products/compile-only/` | **active** (compile-only CI validation lane) | **KEEP.** |
| `products/webflash/` | **active** (WebFlash release namespace) | **KEEP.** |
| `products/secrets.yaml` | **active** (symlink → `../secrets.example.yaml`, used by CI compile + tests) | **KEEP.** |

No directory or file under `components/` or `products/` qualifies as
`legacy-unreferenced`, `empty/scaffold`, or `unknown`. **There is nothing to
remove and no `REMOVE-LEGACY-COMPONENTS-001` follow-up is warranted.**

## Top-level layout (in scope for this audit)

```
esphome-public/
├── components/          ESPHome external components (C++/Python): ld2412, ld2450, ld24xx
├── products/            Buildable product entrypoints (shims) + bundles + lanes
│   ├── bundles/         Canonical config-string-named compositions (BUNDLE-LAYER-001)
│   ├── compile-only/    Compile-only CI validation skeletons (not release products)
│   ├── webflash/        Thin WebFlash-namespace wrappers (config/webflash-builds.json targets)
│   ├── sense360-*.yaml  Customer-pinned compat shims that !include a bundle
│   └── secrets.yaml     Symlink → ../secrets.example.yaml (compile/test only)
├── packages/            Reusable YAML: base/, boards/, expansions/, features/, hardware/
├── config/              JSON sources of truth (catalog, matrices, release targets, policy)
├── scripts/             Validators / generators / release tooling
├── tests/               Python validators + unittest suite + C++ unit tests
└── docs/                Audits, hardware artifacts, matrices, policy
```

`base/ → packages/base`, `features/ → packages/features`,
`hardware/ → packages/hardware` are compatibility symlinks (classified in
[`docs/repo-structure-audit.md`](repo-structure-audit.md); out of scope here).

## The build / release include chain

The key to reading the `products/` reference map is the **3-layer include
chain** introduced by `BUNDLE-LAYER-001`
([`docs/arch-board-bundle-plan.md`](arch-board-bundle-plan.md) §3.2). A naive
"grep for the file path in config" understates how active the deeper layers are,
because each layer reaches the next via `!include`, not a config string:

```
config/webflash-builds.json
        │  (release-eligibility source of truth)
        ▼
products/webflash/<sku>.yaml            ← thin WebFlash-namespace wrapper
        │  !include ../sense360-<sku>.yaml
        ▼
products/sense360-<sku>.yaml            ← customer-pinned compat shim (immutable include contract)
        │  !include bundles/<sku>.yaml
        ▼
products/bundles/<sku>.yaml             ← CANONICAL composition (substitutions, packages, identity)
        │  !include ../../packages/boards|features|base/...
        ▼
packages/base/external_components.yaml  ← declares components: [ld2412, ld2450, ld24xx]
        ▼
components/ld2412 · ld2450 · ld24xx      ← ESPHome external components (this repo)
```

The other `config/*.json` sources address different rungs of the same ladder:

* [`config/preview-release-targets.json`](../config/preview-release-targets.json)
  → top-level `products/sense360-*.yaml` (9 preview targets; the blocker notes
  also name the `products/bundles/*` each shim resolves to).
* [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json)
  → `products/sense360-*.yaml` + `products/webflash/*.yaml`.
* [`config/compile-only-targets.json`](../config/compile-only-targets.json)
  → `products/compile-only/*.yaml`, `products/sense360-*.yaml`, and the two
  `products/bundles/ceiling-usb-*.yaml` USB variants.
* [`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json)
  → the three fan `products/sense360-*.yaml` (FanPWM / FanDAC / FanRelay).
* [`config/product-catalog.json`](../config/product-catalog.json)
  → documents each shim → bundle relationship.

On top of the explicit references, **two enumeration mechanisms consume every
YAML under `products/`**, so no product YAML is ever truly "unreferenced":

* `.github/workflows/ci-validate-configs.yml` —
  `find products/ -name "*.yaml" -type f ! -name "secrets.yaml" ! -path "products/webflash/*"`
  builds the per-product compile matrix.
* `tests/test_all_yaml_release_matrix.py` — `PRODUCTS_DIR.rglob("*.yaml")` and
  asserts the classifier "covers every YAML in `products/` exactly once."

## `components/` — deep dive (classification: ACTIVE / KEEP)

```
components/
├── ld2412/   __init__.py, binary_sensor.py, sensor.py, text_sensor.py, ld2412.{cpp,h},
│             button/, number/, select/, switch/   (HLK-LD2412 24GHz mmWave radar)
├── ld2450/   __init__.py, binary_sensor.py, sensor.py, text_sensor.py, ld2450.{cpp,h},
│             button/, number/, select/, switch/   (HLK-LD2450 24GHz mmWave radar)
└── ld24xx/   __init__.py, ld24xx.h                (shared LD24xx base)
```

62 files across 3 ESPHome external components. **This directory is a hard build
dependency and part of the public remote-package surface.** Proof it is active:

| Reference | Path | Why it matters |
| --- | --- | --- |
| Declared as remote source | `packages/base/external_components.yaml` (`type: git`, `url: …/esphome-public`, `ref: main`, `components: [ld2412, ld2450, ld24xx]`) | External consumers pinned to a tag fetch these components from this repo. Deleting/renaming = breaking change. |
| CI local-path override (build) | `.github/workflows/firmware-build-release.yml` rewrites to `path: ../components` | Release builds compile against the local `components/` tree. |
| CI local-path override (manual) | `.github/workflows/manual-firmware-artifacts.yml` | Manual-artifact builds use the local `components/` tree. |
| CI branch-ref rewrite (validate) | `.github/workflows/ci-validate-configs.yml` (`sed s|ref: main|ref: $BRANCH_NAME|`) | Per-product compile validation uses the branch's `components/`. |
| Test harness | `tests/generate_test_configs.py` inlines `path: ../../components` | Generated test configs compile against `components/`. |
| Release tooling | `scripts/plan_room_release_notes.py` reads the external_components git ref | Release notes pin the components ref. |
| Component **usage** | `ld2412:` / `ld2450:` platform blocks in 7 package files | Removing `components/` would make these packages fail to compile. |

Packages that instantiate the radar component platforms (so they require
`components/` at compile time):

```
packages/boards/s360-200-roomiq-radar.yaml
packages/boards/s360-200-roomiq-radar-wall.yaml
packages/expansions/presence_ld2412.yaml
packages/expansions/presence_ld2450.yaml
packages/features/presence_advanced_ld2412.yaml
packages/hardware/presence_ld2412.yaml
packages/hardware/presence_ld2450.yaml
```

These packages compose into RoomIQ / presence boards, which compose into
products via the include chain above. `.github/workflows/ci-validate-configs.yml`
also declares a `components/**` path filter, and
`config/product-catalog.json` / `config/feature-entity-matrix.json` enumerate
the `ld2412` / `ld2450` entities.

> The only `components/` "hit" in `config/` that is **not** a reference to this
> tree is an `https://esphome.io/components/output/gp8403` documentation URL in a
> `config/compile-only-targets.json` description — noted here so it is not
> mistaken for a local dependency.

**Conclusion:** `components/` is `active` / public-API. It is **not** legacy and
**not** removable. No `REMOVE-LEGACY-COMPONENTS-001` follow-up is opened.

## `products/` — deep dive (classification: ACTIVE / KEEP)

40 regular YAML files + 1 symlink. No obsolete subfolders.

### Subfolder classification

| Subpath | Files | Classification | Key references |
| --- | --- | --- | --- |
| `products/*.yaml` (top-level `sense360-*`) | 18 | **active** — customer-pinned compat shims; each `!include`s a bundle | preview-release-targets, firmware-combination-matrix, manual-firmware-artifacts, compile-only-targets, product-catalog |
| `products/bundles/` | 11 | **active** — canonical compositions; **all 11** are `!include`d by their top-level shim | shim include chain; preview-release-targets notes; product-catalog; compile-only-targets (USB) |
| `products/compile-only/` | 8 | **active** — compile-only CI validation skeletons | compile-only-targets.json; `test_compile_targets.py`; `test_all_yaml_release_matrix.py` |
| `products/webflash/` | 3 | **active** — WebFlash-namespace wrappers (release targets) | webflash-builds.json (2 live rows); firmware-combination-matrix; webflash tests |
| `products/secrets.yaml` | symlink | **active** — `→ ../secrets.example.yaml` | CI compile step; ESPHome config validation; tests |

### `products/bundles/` — every file is included by a shim

```
ceiling-poe-airiq-roomiq.yaml            ← sense360-ceiling-poe-airiq-roomiq.yaml
ceiling-poe-fandac.yaml                   ← sense360-ceiling-poe-fandac.yaml
ceiling-poe-fanpwm.yaml                   ← sense360-ceiling-poe-fanpwm.yaml
ceiling-poe-roomiq-led.yaml               ← sense360-ceiling-poe-roomiq-led.yaml
ceiling-poe-roomiq.yaml                   ← sense360-ceiling-poe-roomiq.yaml
ceiling-poe-ventiq-fanrelay-roomiq.yaml   ← sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml
ceiling-poe-ventiq-fantriac-roomiq.yaml   ← sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml
ceiling-poe-ventiq-roomiq-led.yaml        ← sense360-ceiling-poe-ventiq-roomiq-led.yaml
ceiling-poe-ventiq-roomiq.yaml            ← sense360-ceiling-poe-ventiq-roomiq.yaml
ceiling-usb-roomiq.yaml                   ← sense360-ceiling-usb-roomiq.yaml
ceiling-usb-ventiq-roomiq.yaml            ← sense360-ceiling-usb-ventiq-roomiq.yaml
```

Per the expected policy, **`products/` stays** (it contains active product /
bundle YAMLs) and **`products/bundles/**` stays active** because preview targets
resolve through it: `config/preview-release-targets.json` references
`products/bundles/ceiling-poe-airiq-roomiq.yaml`,
`products/bundles/ceiling-poe-roomiq.yaml`, and
`products/bundles/ceiling-poe-roomiq-led.yaml` directly in its blocker-resolution
notes, and the top-level preview-target shims `!include` their bundles. This is
exactly where the next functional PR is expected to add files, so **none of it is
removed.**

## Audit method

For each file under `components/` and `products/`, references were searched
across `config/`, `scripts/`, `tests/`, `.github/`, `packages/`, `docs/`, and
the root markdown files — by explicit path, by basename, and by the intra-
`products/` `!include` graph — and cross-checked against the two enumeration
mechanisms (CI `find`, release-matrix `rglob`). A reference was classified
`active` when consumed by release/build/test/config wiring, `historical` when
only mentioned in narrative docs, and `dead` when unreferenced anywhere. **No
file under `components/` or `products/` classified as `historical`-only or
`dead`.**

## Validation

All six required checks pass on the audit (docs-only) change set:

* `python3 tests/validate_configs.py` — 217 files, 0 failed.
* `python3 scripts/validate_compile_targets.py --metadata-only` — 18 targets, passed.
* `python3 scripts/validate_preview_release_targets.py --metadata-only` — 9 targets, passed.
* `python3 tests/test_product_catalog.py` — 41 tests OK.
* `python3 tests/validate_webflash_builds.py` — 2 builds, 0 failed.
* `python3 -m unittest discover -s tests -p "test_*.py"` — 1245 tests OK (3 skipped).

No ESPHome compile was run (the audit changes only documentation), so **no
compile / build / firmware proof is claimed.**

## Guardrails (explicitly NOT done)

No `products/` path removed; no `products/bundles/**` path removed; no
`components/` removal; no release policy change; no firmware published; no
WebFlash repo touched; no config / package / product YAML / workflow modified
(documentation only).

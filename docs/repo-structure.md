# Repository Structure & Reference Map

> **Scope.** This is the canonical **structural** reference for
> `sense360store/esphome-public`: what the top-level directories are, how they
> wire together, and the proof of which paths are active. For live **release /
> roadmap / blocker status** (preview vs stable, S360-410 PoE, LED preview,
> FanPWM bench gates) the single source of truth remains
> [`docs/sense360-roadmap-status.md`](sense360-roadmap-status.md). The older
> path-classification audit [`docs/repo-structure-audit.md` (archived)](archive-index.md)
> (ESP-009 / ESP-010) is retained as historical provenance; this document
> refreshes it for the current `products/` subfolder layout and the
> bundle / shim / wrapper include chain.

This document was produced by **REPO-STRUCTURE-AUDIT-001**. It is an
**audit / classification document only**. Its original purpose was to prove
whether the top-level `components/` and `products/` directories were active,
legacy, or removable.

> **Superseded in part by REPO-CONSOLIDATION-001 (2026-07-30).** The
> `products/bundles/` layer this audit classified KEEP was subsequently
> **folded into the customer-pinned `products/sense360-*.yaml` paths** and
> deleted, with the resolved compositions proven identical across the fold
> (the root paths had been thin one-include shims of their bundles).
> Release tags keep the historical `bundles/` paths. File counts below are
> the audit-time snapshot, not the current tree.

## TL;DR — audit result

| Directory | Classification | Decision |
| --- | --- | --- |
| `components/` | **active** (build dependency + public ESPHome remote-package surface) | **KEEP.** Not legacy, not removable. No follow-up removal opened. |
| `products/` | **active** (release / build / test / config backbone) | **KEEP.** No obsolete subfolders found. |
| `products/bundles/` | **superseded** (REPO-CONSOLIDATION-001) | **FOLDED** into `products/sense360-*.yaml`; directory deleted, tags keep history. |
| `products/compile-only/` | **active** (compile-only CI validation lane) | **KEEP.** |
| `products/webflash/` | **active** (WebFlash release namespace) | **KEEP.** |
| `products/secrets.example.yaml` | **active** (tracked placeholder template; SEC-ESP-SECRET-GUARD-001 replaced the `products/secrets.yaml` symlink). `products/secrets.yaml` is gitignored and created locally / by CI. | **KEEP.** |

No directory or file under `components/` or `products/` qualifies as
`legacy-unreferenced`, `empty/scaffold`, or `unknown`. **There is nothing to
remove and no `REMOVE-LEGACY-COMPONENTS-001` follow-up is warranted.**

## Top-level layout (in scope for this audit)

```
esphome-public/
├── components/          ESPHome external components: sense360 family + mics_stm8 + sfa40
├── products/            Buildable product entrypoints (canonical compositions) + lanes
│   ├── compile-only/    Compile-only CI validation skeletons (not release products)
│   ├── webflash/        Thin WebFlash-namespace wrappers (config/webflash-builds.json targets)
│   ├── sense360-*.yaml  Customer-pinned canonical compositions (bundle layer folded in)
│   └── secrets.example.yaml  Tracked placeholder template (secrets.yaml is gitignored, created locally/CI)
├── packages/            Reusable YAML: base/, boards/, expansions/, features/, hardware/
├── config/              JSON sources of truth (catalog, matrices, release targets, policy)
├── scripts/             Validators / generators / release tooling
├── tests/               Python validators + unittest suite + C++ unit tests
└── docs/                Audits, hardware artifacts, matrices, policy
```

`base/ → packages/base`, `features/ → packages/features`,
`hardware/ → packages/hardware` are compatibility symlinks (classified in
[`docs/repo-structure-audit.md` (archived)](archive-index.md); out of scope here).

## The build / release include chain

The key to reading the `products/` reference map is the include chain
(`BUNDLE-LAYER-001` introduced a 3-layer form;
REPO-CONSOLIDATION-001 collapsed it to 2 layers by folding the bundle into
the customer-pinned path):

```
config/webflash-builds.json
        │  (release-eligibility source of truth)
        ▼
products/webflash/<sku>.yaml            ← thin WebFlash-namespace wrapper
        │  !include ../sense360-<sku>.yaml
        ▼
products/sense360-<sku>.yaml            ← customer-pinned CANONICAL composition
        │  !include ../packages/boards|features|base/...
        ▼
packages/base/external_components.yaml  ← declares the sense360 component family (type: local)
        ▼
components/sense360*, mics_stm8, sfa40   ← ESPHome external components (this repo)
```

The other `config/*.json` sources address different rungs of the same ladder:

* [`config/preview-release-targets.json`](../config/preview-release-targets.json)
  → top-level `products/sense360-*.yaml` (every `yaml_path` is a root
  product path; no bundle paths).
* [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json)
  → `products/sense360-*.yaml` + `products/webflash/*.yaml`.
* [`config/compile-only-targets.json`](../config/compile-only-targets.json)
  → `products/compile-only/*.yaml` and `products/sense360-*.yaml` (the USB
  variants are root products like the rest).
* [`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json)
  → the three fan `products/sense360-*.yaml` (FanPWM / FanDAC / FanRelay).
* [`config/product-catalog.json`](../config/product-catalog.json)
  → declares every `product_yaml` (all root `products/sense360-*.yaml`).

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
├── mics_stm8/          MICS-4514 gas sensor behind its STM8 bridge (vendored driver)
├── sfa40/              SFA40 formaldehyde sensor (vendored driver)
├── sense360/           foundation component: shared logic engines, runtime contract,
│                       identity schema (SENSE360-CANONICALISATION-001 PR 08)
├── sense360_airiq/     AirIQ domain component
├── sense360_led/       LED domain component
├── sense360_presence/  presence domain component
├── sense360_roomiq/    RoomIQ domain component
└── sense360_ventiq/    VentIQ domain component
```

Every entry is declared with provenance in
`config/external-components.json` (guard:
`tests/test_external_components.py`). The former vendored radar trio
(`ld2412` / `ld2450` / `ld24xx`) was retired under SENSE360-CANONICALISATION-001
PR 10: the pinned ESPHome ships built-in drivers, every live composition
validates against them, and release tags keep the vendored trees for
tag-pinned consumers. The only radar platform instantiation left in the
package layer is the built-in `ld2450:` block in
`packages/boards/s360-200-roomiq-radar.yaml`.

**This directory is a hard build dependency.** Proof it is active:

| Reference | Path | Why it matters |
| --- | --- | --- |
| Declared as local source | `packages/base/external_components.yaml` (`type: local`, `path: ../components`, `components: [sense360, sense360_roomiq, sense360_presence, sense360_airiq, sense360_ventiq, sense360_led]`) | Every repository build lane compiles a branch's own component code. Remote consumers get these components from the git-sourced declarations in the `packages/remote/` wrappers. |
| CI local-path handling (build) | `.github/workflows/firmware-build-release.yml` | Release builds compile against the local `components/` tree. |
| CI local-path handling (manual) | `.github/workflows/manual-firmware-artifacts.yml` | Manual-artifact builds use the local `components/` tree. |
| CI branch-ref handling (validate) | `.github/workflows/ci-validate-configs.yml` | Per-product compile validation uses the branch's `components/`. |
| Release tooling | `scripts/plan_room_release_notes.py` reads the external_components declarations | Release notes pin the components provenance. |
| Component **usage** | `sense360*` platform blocks in the framework feature packages and board packages | Removing `components/` would make every framework-bearing product fail to compile. |

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
| `products/*.yaml` (top-level `sense360-*`) | audit-time 18 (now 24) | **active** — customer-pinned canonical compositions (REPO-CONSOLIDATION-001 folded the bundle layer in) | preview-release-targets, firmware-combination-matrix, manual-firmware-artifacts, compile-only-targets, product-catalog, core-framework |
| `products/bundles/` | audit-time 11 | **superseded** — folded into the root `sense360-*.yaml` paths and deleted (REPO-CONSOLIDATION-001); release tags keep the historical paths | (historical) |
| `products/compile-only/` | 8 | **active** — compile-only CI validation skeletons | compile-only-targets.json; `test_compile_targets.py`; `test_all_yaml_release_matrix.py` |
| `products/webflash/` | 3 | **active** — WebFlash-namespace wrappers (release targets) | webflash-builds.json (2 live rows); firmware-combination-matrix; webflash tests |
| `products/secrets.example.yaml` | template | **active** — tracked placeholder template (SEC-ESP-SECRET-GUARD-001; `products/secrets.yaml` is gitignored, created locally/CI) | CI compile step; ESPHome config validation; tests |

### `products/bundles/` — folded and deleted (REPO-CONSOLIDATION-001)

The audit-time table above recorded every bundle `!include`d by its
top-level shim, and the KEEP decision rested on the preview lane resolving
through the layer. REPO-CONSOLIDATION-001 re-established the evidence on
the then-current tree: every shipping-decision `config/*.json` addressed
the ROOT paths (zero structural bundle references outside
`config/core-framework.json` and `config/room-bundle-fan-variants.json`),
the release workflow compiled the root file, and each root file was a thin
one-include shim of its bundle. The bundle bodies were therefore folded
into the root paths (include paths rebased `../../packages/` →
`../packages/`), the directory deleted, the two config files repointed,
and the resolved composition of every webflash wrapper and root product
proven identical across the fold. Release tags keep every historical
`bundles/` path for tag-pinned users.

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

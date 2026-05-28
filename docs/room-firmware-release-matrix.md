# Room Firmware Release Matrix (RELEASE-PIPELINE-ROOM-MATRIX-001)

## Purpose and scope

This document is a **read-only inventory** of the room firmware release
pipeline. It enumerates every RoomIQ / VentIQ / LED / FanRelay / FanPWM /
FanDAC / FanTRIAC ceiling-PoE variant that exists as YAML in this repo and
records, for each, exactly where it sits in the release machinery: the
release build workflow, the WebFlash build matrix, the product catalog, the
compile-only validation lane, the manual (non-release) artifact lane, and
the release-notes generator.

It exists to answer one question — *"which room/product versions should be
available through release CI?"* — **without changing any of them**. It is
the room-firmware-family view that cross-cuts the existing layered gates:

- [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md) (PACKAGE-GAP-001)
- [`docs/product-readiness-matrix.md`](product-readiness-matrix.md) (PRODUCT-GAP-001)
- [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md) (WEBFLASH-GAP-001)
- [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md) (RELEASE-GAP-001)
- [`docs/release-one.md`](release-one.md) (shipping configuration)
- [`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md) (availability vocabulary)

### This document is documentation only

RELEASE-PIPELINE-ROOM-MATRIX-001 — this PR — does **not**:

- publish, build, or attach any firmware artifact;
- add, remove, or modify any product YAML or WebFlash wrapper;
- add or change any entry in
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  [`config/product-catalog.json`](../config/product-catalog.json),
  [`config/compile-only-targets.json`](../config/compile-only-targets.json),
  or [`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json);
- flip any `webflash_build_matrix` value;
- add an `artifact_name` to any product;
- add a WebFlash wrapper to any product;
- claim release readiness for any product that the source-of-truth catalogs
  do not already mark release-approved.

Every classification below is **read** from the committed catalogs and
workflows cited inline; nothing is asserted beyond what they already record.

---

## Source-of-truth files

| Layer | File |
|-------|------|
| Release build/publish workflow | [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml) |
| WebFlash build matrix (release driver) | [`config/webflash-builds.json`](../config/webflash-builds.json) |
| WebFlash grammar / channels | [`config/webflash-compatibility.json`](../config/webflash-compatibility.json) |
| Product lifecycle catalog | [`config/product-catalog.json`](../config/product-catalog.json) |
| Compile-only validation lane | [`config/compile-only-targets.json`](../config/compile-only-targets.json) + [`.github/workflows/compile-only.yml`](../.github/workflows/compile-only.yml) |
| Manual (non-release) artifact lane | [`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json) + [`.github/workflows/manual-firmware-artifacts.yml`](../.github/workflows/manual-firmware-artifacts.yml) |
| Release-notes draft helper | [`scripts/generate_webflash_release_notes.py`](../scripts/generate_webflash_release_notes.py) + [`.github/workflows/release-notes-draft.yml`](../.github/workflows/release-notes-draft.yml) |

**Key pipeline fact:** the release workflow's build matrix is generated
**exclusively** from `config/webflash-builds.json`, filtered by `version` +
`channel` (see `firmware-build-release.yml` job `generate-matrix`). A config
that is not in `webflash-builds.json` is **not** built or attached when a
GitHub Release is published, regardless of whether its YAML exists. The
WebFlash build matrix is the single source of truth for what release
publishing ships.

---

## Release matrix table

Column legend:

- **Release channel** — `stable` / `preview` / `none` (per catalog).
- **CI build status** — which workflow compiles it:
  `release-ci` (in `firmware-build-release.yml` matrix),
  `compile-only-ci` (in `compile-only.yml` validation lane),
  `manual-nonrelease-ci` (in `manual-firmware-artifacts.yml`, ephemeral),
  `no-ci-build`.
- **WebFlash status** — `webflash-matrix` (wrapper + builds.json row +
  `webflash_build_matrix: true`), `wrapper-reference-only` (wrapper exists
  but not in builds matrix), `no-webflash`.
- **Artifact status** — `release-artifact-name` (catalog/builds
  `artifact_name`), `ephemeral-manual-only` (expiring CI artifact, no
  release name), `none`.
- **Release-notes status** — whether `generate_webflash_release_notes.py`
  will emit notes: `eligible-stable`, `eligible-preview`, or `refused`.

| Product / config string | YAML path(s) | Release channel | CI build status | WebFlash status | Artifact status | Release-notes status | Blockers |
|---|---|---|---|---|---|---|---|
| **Ceiling-POE-VentIQ-RoomIQ** | `products/sense360-ceiling-poe-ventiq-roomiq.yaml` (canonical) + `products/webflash/ceiling-poe-ventiq-roomiq.yaml` (wrapper) | `stable` (production) | `release-ci` + `compile-only-ci` | `webflash-matrix` | `release-artifact-name`: `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` | `eligible-stable` | None (Release-One ships this). FanTRIAC/LED excluded by design, not blockers of this config |
| **Ceiling-POE-VentIQ-RoomIQ-LED** | `products/sense360-ceiling-poe-ventiq-roomiq-led.yaml` (canonical) + `products/webflash/ceiling-poe-ventiq-roomiq-led.yaml` (wrapper) | `preview` | `release-ci` + `compile-only-ci` | `webflash-matrix` | `release-artifact-name`: `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` | `eligible-preview` (refused on `stable`) | Preview-stage S360-300 bench Open Questions (harness rail, LED count, harness identity) before any stable promotion; FanTRIAC blocked |
| **Ceiling-POE-VentIQ-FanTRIAC-RoomIQ** | `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml` (canonical) + `products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml` (blocked/reference wrapper) | `none` (blocked) | `no-ci-build` | `wrapper-reference-only` (not in builds matrix; `webflash_build_matrix: false`) | `none` | `refused` (status `blocked`) | **HW-005** (S360-320 schematic uncommitted; GPIO5/GPIO6 collide with RoomIQ J10; `ac_dimmer` cannot run across SX1509) + HW-PINMAP-320-FOLLOWUP + PACKAGE-TRIAC-001 + COMPLIANCE-001 + WebFlash manual-warning UX gates |
| **Ceiling-POE-VentIQ-FanRelay-RoomIQ** | `products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml` (canonical; no wrapper) | `none` (manual-candidate) | `manual-nonrelease-ci` + `compile-only-ci` (`validated-full-compile`) | `no-webflash` (`webflash_build_matrix: false`) | `ephemeral-manual-only` (`{stem}-manual-{short_sha}-nonrelease`, 7-day retention); no `artifact_name` | `refused` (status `hardware-pending`) | GPIO3 strap-pin boot characterisation (production-wide/multi-unit); mains-safety / installation-approval / creepage / clearance / thermal / EMI / EMC evidence; competent-person sign-off. WEBFLASH-RELAY-001 / RELEASE-RELAY-001 / WF-IMPORT-RELAY-001 blocked |
| **Ceiling-POE-FanPWM** | `products/sense360-ceiling-poe-fanpwm.yaml` (canonical; no wrapper) + `products/compile-only/ceiling-poe-fanpwm.yaml` (CI skeleton) | `none` (manual-candidate) | `manual-nonrelease-ci` + `compile-only-ci` (top-level + skeleton, both `validated-full-compile`) | `no-webflash` (`webflash_build_matrix: false`) | `ephemeral-manual-only`; no `artifact_name` | `refused` (status `hardware-pending`) | PWM polarity bench; per-fan/aggregate current + thermal envelope; product bench incomplete; **no RPM/TachIO** (`rpm_supported: false`); S360-311 `cataloged_unverified`. WEBFLASH-PWM-001 / RELEASE-PWM-001 / WF-IMPORT-PWM-001 blocked |
| **Ceiling-POE-FanDAC** | `products/sense360-ceiling-poe-fandac.yaml` (canonical; no wrapper) + `products/compile-only/ceiling-poe-fandac.yaml` (CI skeleton) | `none` (manual-candidate) | `manual-nonrelease-ci` + `compile-only-ci` (top-level + skeleton, both `validated-full-compile`) | `no-webflash` (`webflash_build_matrix: false`) | `ephemeral-manual-only`; no `artifact_name` | `refused` (status `hardware-pending`) | Not Cloudlift-ready; J3/Cloudlift S12 harness + product-bench evidence; S360-312 schematic/BOM verification; enforces FanDAC↔AirIQ mutex. WEBFLASH-DAC-001 / RELEASE-DAC-001 / WF-IMPORT-DAC-001 blocked |
| **Ceiling-POE** | `products/compile-only/ceiling-poe.yaml` | `none` (compile-only) | `compile-only-ci` | `no-webflash` | `none` | `refused` (no catalog row) | CI validation subset only; `hardware_required_for_validation: true`; S360-410 schematic verification / Release-One PoE caveats out of scope |
| **Ceiling-POE-RoomIQ** | `products/compile-only/ceiling-poe-roomiq.yaml` | `none` (compile-only) | `compile-only-ci` | `no-webflash` | `none` | `refused` (no catalog row) | CI validation subset only; `hardware_required_for_validation: true` |
| **Ceiling-POE-VentIQ** | `products/compile-only/ceiling-poe-ventiq.yaml` | `none` (compile-only) | `compile-only-ci` | `no-webflash` | `none` | `refused` (no catalog row) | CI validation subset only; `hardware_required_for_validation: true` |
| **Ceiling-POE-AirIQ** | `products/compile-only/ceiling-poe-airiq.yaml` | `none` (compile-only) | `compile-only-ci` | `no-webflash` | `none` | `refused` (no catalog row) | CI validation subset only; AirIQ↔VentIQ mutex (uses AirIQ); `hardware_required_for_validation: true` |
| **Ceiling-POE-AirIQ-RoomIQ** | `products/compile-only/ceiling-poe-airiq-roomiq.yaml` | `none` (compile-only) | `compile-only-ci` | `no-webflash` | `none` | `refused` (no catalog row) | CI validation subset only; AirIQ↔VentIQ mutex (uses AirIQ); `hardware_required_for_validation: true` |

---

## Answers to the inventory questions

### 1. Which RoomIQ / VentIQ / LED / Relay / PWM / DAC variants exist as YAML?

**Top-level product YAMLs (`products/`) — 6 room-family products:**

- `products/sense360-ceiling-poe-ventiq-roomiq.yaml` (RoomIQ + VentIQ)
- `products/sense360-ceiling-poe-ventiq-roomiq-led.yaml` (RoomIQ + VentIQ + LED)
- `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml` (RoomIQ + VentIQ + FanTRIAC)
- `products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml` (RoomIQ + VentIQ + FanRelay)
- `products/sense360-ceiling-poe-fanpwm.yaml` (FanPWM)
- `products/sense360-ceiling-poe-fandac.yaml` (FanDAC)

**WebFlash wrappers (`products/webflash/`) — 3 (re-include the canonical YAML, not standalone products):**

- `products/webflash/ceiling-poe-ventiq-roomiq.yaml`
- `products/webflash/ceiling-poe-ventiq-roomiq-led.yaml`
- `products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml` (blocked/reference)

**Compile-only skeletons (`products/compile-only/`) — 7 CI validation files:**

- `products/compile-only/ceiling-poe.yaml`
- `products/compile-only/ceiling-poe-roomiq.yaml`
- `products/compile-only/ceiling-poe-ventiq.yaml`
- `products/compile-only/ceiling-poe-airiq.yaml`
- `products/compile-only/ceiling-poe-airiq-roomiq.yaml`
- `products/compile-only/ceiling-poe-fanpwm.yaml`
- `products/compile-only/ceiling-poe-fandac.yaml`

### 2. Which are currently in `firmware-build-release.yml`?

The release workflow does **not** name products directly — its matrix is
generated from `config/webflash-builds.json` filtered by `version` +
`channel`. The configs that the workflow will therefore build/attach today:

- **Ceiling-POE-VentIQ-RoomIQ** — v1.0.0 / `stable`
- **Ceiling-POE-VentIQ-RoomIQ-LED** — v1.0.0 / `preview`

No other room variant is reachable by the release workflow.

### 3. Which are in `config/webflash-builds.json`?

Only the two release-channel configs:

- Ceiling-POE-VentIQ-RoomIQ → `stable`, artifact `…-v1.0.0-stable.bin`
- Ceiling-POE-VentIQ-RoomIQ-LED → `preview`, artifact `…-v1.0.0-preview.bin`

### 4. Which have product-catalog rows?

The 6 top-level products each have a `config/product-catalog.json` row:

| Config string | Catalog status | `webflash_build_matrix` |
|---|---|---|
| Ceiling-POE-VentIQ-RoomIQ | `production` | `true` |
| Ceiling-POE-VentIQ-RoomIQ-LED | `preview` | `true` |
| Ceiling-POE-VentIQ-FanTRIAC-RoomIQ | `blocked` | `false` |
| Ceiling-POE-VentIQ-FanRelay-RoomIQ | `hardware-pending` | `false` |
| Ceiling-POE-FanPWM | `hardware-pending` | `false` |
| Ceiling-POE-FanDAC | `hardware-pending` | `false` |

The 7 `products/compile-only/` skeletons have **no** catalog row — that
subdirectory is deliberately excluded from the catalog enumeration gate, so
a compile-only target does not require (and does not get) a catalog entry.

### 5. Which have compile-only targets?

All 12 entries in `config/compile-only-targets.json` are room-PoE-family:

| Target id | Config string | `compile_validation_status` |
|---|---|---|
| `ceiling-poe-ventiq-roomiq-webflash` | Ceiling-POE-VentIQ-RoomIQ | webflash-current |
| `ceiling-poe-ventiq-roomiq-led-webflash` | Ceiling-POE-VentIQ-RoomIQ-LED | preview-current |
| `ceiling-poe-compile-only` | Ceiling-POE | compile-only |
| `ceiling-poe-roomiq-compile-only` | Ceiling-POE-RoomIQ | compile-only |
| `ceiling-poe-ventiq-compile-only` | Ceiling-POE-VentIQ | compile-only |
| `ceiling-poe-airiq-compile-only` | Ceiling-POE-AirIQ | compile-only |
| `ceiling-poe-airiq-roomiq-compile-only` | Ceiling-POE-AirIQ-RoomIQ | compile-only |
| `ceiling-poe-ventiq-fanrelay-roomiq-compile-only` | Ceiling-POE-VentIQ-FanRelay-RoomIQ | validated-full-compile |
| `ceiling-poe-fandac-compile-only` | Ceiling-POE-FanDAC (skeleton) | validated-full-compile |
| `ceiling-poe-fanpwm-compile-only` | Ceiling-POE-FanPWM (skeleton) | validated-full-compile |
| `ceiling-poe-fandac-product-compile-only` | Ceiling-POE-FanDAC (top-level) | validated-full-compile |
| `ceiling-poe-fanpwm-product-compile-only` | Ceiling-POE-FanPWM (top-level) | validated-full-compile |

**FanTRIAC has no compile-only target** (blocked from every lane).

### 6. Which have `artifact_name`?

Only the two release-channel configs, in both `webflash-builds.json` and the
catalog:

- Ceiling-POE-VentIQ-RoomIQ → `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`
- Ceiling-POE-VentIQ-RoomIQ-LED → `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`

FanTRIAC / FanRelay / FanPWM / FanDAC have **no** `artifact_name`. The manual
lane names its outputs `{stem}-manual-{short_sha}-nonrelease` — explicitly
**not** an `artifact_name` and never a release `vX.Y.Z`/`-stable`/`-preview`.

### 7. Which have WebFlash wrappers?

Three wrappers under `products/webflash/`:

- Ceiling-POE-VentIQ-RoomIQ — in build matrix (live)
- Ceiling-POE-VentIQ-RoomIQ-LED — in build matrix (live preview)
- Ceiling-POE-VentIQ-FanTRIAC-RoomIQ — **reference only**, not in the build
  matrix while HW-005 is open

FanRelay / FanPWM / FanDAC have **no** WebFlash wrapper.

### 8. Release-channel classification

| Classification | Configs |
|---|---|
| **release-ready (stable)** | Ceiling-POE-VentIQ-RoomIQ |
| **preview-only** | Ceiling-POE-VentIQ-RoomIQ-LED |
| **manual-candidate-only** | Ceiling-POE-VentIQ-FanRelay-RoomIQ, Ceiling-POE-FanPWM, Ceiling-POE-FanDAC |
| **blocked** | Ceiling-POE-VentIQ-FanTRIAC-RoomIQ (HW-005) |
| **compile-only (CI validation subset, no release path)** | Ceiling-POE, Ceiling-POE-RoomIQ, Ceiling-POE-VentIQ, Ceiling-POE-AirIQ, Ceiling-POE-AirIQ-RoomIQ |

### 9. Which YAMLs are available from GitHub for ESPHome remote-package / manual use?

`sense360store/esphome-public` is a public repo, so any committed YAML is
fetchable as a remote ESPHome package via `url` + `ref` + `files`. The
**intended entry points** for remote-package / manual install are the
top-level canonical product YAMLs under `products/`:

- `products/sense360-ceiling-poe-ventiq-roomiq.yaml` — production install path
- `products/sense360-ceiling-poe-ventiq-roomiq-led.yaml` — preview LED install path
- `products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml` — manual candidate
- `products/sense360-ceiling-poe-fanpwm.yaml` — manual candidate
- `products/sense360-ceiling-poe-fandac.yaml` — manual candidate

Notes:

- The `products/webflash/*` wrappers `!include` the canonical YAML; they are
  WebFlash-addressing shims, not separate remote-package entry points.
- The `products/compile-only/*` skeletons are **CI-validation files**, not
  installable products, and should not be advertised for manual use.
- The blocked FanTRIAC YAML is retained as a reference; it is installable in
  the mechanical sense but is **not** approved (HW-005) and carries no
  release/WebFlash exposure.
- Manual installation of the FanRelay/FanPWM/FanDAC candidates is documented
  as manual / no-WebFlash only in
  [`docs/manual-install-fan-candidates.md`](manual-install-fan-candidates.md);
  "compiles and can be installed manually" is **not** release readiness,
  WebFlash exposure, hardware stability, or compliance approval.

### 10. Which YAMLs should be tag-pinned when release notes are generated?

The release-notes generator only emits notes for the two release-channel
configs (it refuses `blocked` / `hardware-pending` / `compile-only` /
`legacy-compatible` and `preview`-on-`stable`). When notes are generated for
a tagged release, the install snippets and shared includes that a consumer
transitively pulls should be **pinned to the release tag** (e.g.
`ref: v1.0.0`), never `ref: main`:

- `products/sense360-ceiling-poe-ventiq-roomiq.yaml` (+ its wrapper) — its
  header install snippet already shows `ref: v1.0.0`.
- `products/sense360-ceiling-poe-ventiq-roomiq-led.yaml` (+ its wrapper) —
  pin to the matching preview tag.
- **`packages/base/external_components.yaml`** — the shared include every
  product transitively pulls. It currently declares `ref: main` for the
  `ld2412` / `ld2450` / `ld24xx` git source. For a reproducible tagged
  release this should be pinned to the release tag at release time. (CI/release
  builds rewrite this to a local source in-workspace, so the committed
  `ref: main` only affects end-user remote-package consumers — which is
  exactly the path release notes point people at.) This matches the guidance
  in [`packages/README.md`](../packages/README.md): *"Pin to a release tag —
  never use 'main' in production."*

The manual-candidate YAMLs (FanRelay/FanPWM/FanDAC) currently carry
`ref: main` in their header comments. They are **not** release-notes-eligible
and stay at `main` until they are release-approved; no tag-pin action is
required for them by this inventory.

---

## What would have to change to make a manual/blocked variant release-ready

This is recorded for orientation only; **no** action is taken here.

- **FanRelay / FanPWM / FanDAC** (manual-candidate → preview/stable): clear
  the per-family hardware/compliance gates in
  [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
  and [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md),
  then — in that order, in separate approved slices — add a WebFlash wrapper,
  promote the catalog row, set `version`/`channel`/`artifact_name`, flip
  `webflash_build_matrix: true`, and add the `config/webflash-builds.json`
  row. Only the last step makes the release workflow build it.
- **FanTRIAC** (blocked → anything): HW-005 and its dependent gates must
  clear first; it has no CI build of any kind today.

---

## RELEASE-CI-DRYRUN-001 — dry-run confirmation (2026-05-27)

RELEASE-CI-DRYRUN-001 ran the release-candidate dry-run over this inventory and
recorded the result (see
[`docs/room-firmware-release-notes.md` §RELEASE-CI-DRYRUN-001](room-firmware-release-notes.md#release-ci-dryrun-001--recorded-dry-run-of-the-release-pipeline-2026-05-27)).
It **changes no row** in the release matrix table above and publishes nothing.
The dry-run confirmed, against the source-of-truth files:

| Check | Result |
|---|---|
| Stable RoomIQ in the release matrix | included — `Ceiling-POE-VentIQ-RoomIQ` (`stable`), notes validate `PASSED` |
| Preview LED in the release matrix | included — `Ceiling-POE-VentIQ-RoomIQ-LED` (`preview`), notes validate `PASSED` |
| FanRelay / FanPWM / FanDAC | excluded — not in `config/webflash-builds.json`; manual-candidate-only |
| FanTRIAC | excluded / blocked (HW-005); no release build of any kind |
| GitHub Release / `.bin` / checksum / `firmware/sources.json` / `manifest.json` | none produced or committed |
| `firmware-build-release.yml` dry-run mode | none exists; next input defined in the release-notes doc |

Validation re-run clean: `plan_room_release_notes.py`,
`test_plan_room_release_notes.py`, `validate_configs.py` (208 files),
`validate_compile_targets.py --metadata-only` (12 targets),
`validate_webflash_builds.py` (2 builds), and
`python3 -m unittest discover -s tests -p "test_*.py"` (871 tests, 3 skipped).

---

## RELEASE-WORKFLOW-DRYRUN-MODE-001 — workflow dry-run mode added (2026-05-27)

The "next input" recorded by RELEASE-CI-DRYRUN-001 is now **implemented**.
[`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)
gained an explicit, **safe-by-default** dry-run mode. This **changes no row**
in the release matrix table above and publishes nothing.

| Aspect | Behaviour |
|---|---|
| New `workflow_dispatch` input | `dry_run` (boolean, **default `true`** = non-publishing) |
| New job | `release-dry-run` — read-only (`contents: read`), runs `scripts/plan_room_release_notes.py` + planner contract tests |
| Dry-run scope | confirms stable `Ceiling-POE-VentIQ-RoomIQ` + preview `Ceiling-POE-VentIQ-RoomIQ-LED` only; FanRelay / FanPWM / FanDAC excluded; FanTRIAC blocked (HW-005) |
| GitHub Release / assets / `firmware/sources.json` / `manifest.json` | none — the dry-run job has no publish step and writes nothing to the repo |
| Publish gate | **unchanged** — the `release` job stays `if: github.event_name == 'release'`; the `dry_run` input cannot publish |

Guardrails are locked in by
[`tests/test_release_dry_run_mode.py`](../tests/test_release_dry_run_mode.py)
and [`tests/test_workflow_permissions.py`](../tests/test_workflow_permissions.py).
See
[`docs/room-firmware-release-notes.md` §Release workflow dry-run mode](room-firmware-release-notes.md#release-workflow-dry-run-mode-implemented-by-release-workflow-dryrun-mode-001).

---

## RELEASE-WORKFLOW-DRYRUN-RESULT-001 — recorded successful dry-run dispatch (2026-05-28)

RELEASE-WORKFLOW-DRYRUN-RESULT-001 records the first **successful** manual
dispatch of the `dry_run=true` lane added by `RELEASE-WORKFLOW-DRYRUN-MODE-001`
and isolated end-to-end by `RELEASE-WORKFLOW-DRYRUN-GATE-FIX-001`. **It
changes no row** in the release matrix table above and publishes nothing.

| Aspect | Result |
|---|---|
| Workflow run | [`26558999495`](https://github.com/sense360store/esphome-public/actions/runs/26558999495/job/78237206588) |
| Workflow | `Build & Release Firmware` ([`firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)) |
| Trigger | `workflow_dispatch` with `dry_run=true` on `main` |
| `Release Dry-Run (no publish)` job | **success** — `Install dry-run test dependencies`, `Plan room release notes (dry-run, no publish)`, `Verify dry-run guardrails (planner contract tests)`, `Assert no release side effects were produced` all passed |
| `Generate Build Matrix` job | **skipped** (gated by `dry_run=false`) |
| Build jobs (per-product) | **skipped** |
| `Build Summary` job | **skipped** |
| `Attach to Release` job | **skipped** (still also gated `if: github.event_name == 'release'`) |
| GitHub Release / assets / `firmware/sources.json` / `manifest.json` / `.bin` / checksum | **none produced or committed** |
| FanRelay / FanPWM / FanDAC | excluded — not in `config/webflash-builds.json`; manual-candidate-only; no release lane participation |
| FanTRIAC | blocked (HW-005); no release build of any kind |

The dispatch proves the gates added by `RELEASE-WORKFLOW-DRYRUN-GATE-FIX-001`
work in CI: a `workflow_dispatch` with `dry_run=true` only exercises the
read-only `release-dry-run` job and the matrix / build / summary / release
jobs are all skipped. See
[`docs/room-firmware-release-notes.md` §RELEASE-WORKFLOW-DRYRUN-RESULT-001](room-firmware-release-notes.md#release-workflow-dryrun-result-001--recorded-successful-release-dry-run-2026-05-28).

---

## RELEASE-PRODUCT-SELECTION-001 — selectable release targets added (2026-05-28)

RELEASE-PRODUCT-SELECTION-001 makes the release-notes / dry-run / release
workflows **operator-selectable** by the agreed room / product config
(stable `Ceiling-POE-VentIQ-RoomIQ`, preview
`Ceiling-POE-VentIQ-RoomIQ-LED`) rather than silently defaulting every
dispatch to the stable RoomIQ. **It changes no row** in the release matrix
table above and publishes nothing.

| Aspect | Result |
|---|---|
| `release-notes-draft.yml` `config_string` | Now a `type: choice` picker; options mirrored from `config/webflash-builds.json` |
| `firmware-build-release.yml` `release_target` | New `type: choice` picker (default `all-release-eligible`); same option set |
| Picker source of truth | `config/webflash-builds.json` (the release matrix); `scripts/list_release_targets.py` enumerates / validates |
| FanRelay / FanPWM / FanDAC | **Never** selectable; manual-candidate-only (`config/manual-firmware-artifacts.json`) |
| FanTRIAC | **Never** selectable; blocked (HW-005) |
| Publish job gate | **Unchanged** — `if: github.event_name == 'release'`; the new input does not (and cannot) reach `softprops/action-gh-release` |
| `firmware/sources.json` / `manifest.json` / `.bin` / checksum | **None produced or committed** |

See
[`docs/room-firmware-release-notes.md` §RELEASE-PRODUCT-SELECTION-001](room-firmware-release-notes.md#release-product-selection-001--selectable-release-targets-2026-05-28)
for the operator-facing UX, tag → product mapping for the publish path, and
the LED / changelog wording reword (generator now product-aware; the stale
"Release-One firmware" phrasing is gone).

---

## STABLE-TARGET-EXPANSION-PLAN-001 — actionable stable-target expansion plan (2026-05-28)

STABLE-TARGET-EXPANSION-PLAN-001 turns this room-family inventory and the
broader all-YAML matrix
([`docs/all-yaml-release-matrix.md`](all-yaml-release-matrix.md) /
STABLE-RELEASE-MATRIX-ALL-YAML-001 / PR #629) into an explicit, actionable
expansion plan. **It changes no row** in the release matrix table above
and publishes nothing.

| Aspect | Result |
|---|---|
| New planning doc | [`docs/stable-target-expansion-plan.md`](stable-target-expansion-plan.md) |
| In-scope candidates (non-fan / non-LED / non-TRIAC room combos) | `Ceiling-POE`, `Ceiling-POE-RoomIQ`, `Ceiling-POE-VentIQ`, `Ceiling-POE-AirIQ`, `Ceiling-POE-AirIQ-RoomIQ` — all currently `compile-only` skeleton-only |
| Closest to stable today | `Ceiling-POE-VentIQ` (already exercised by the stable Release-One build's VentIQ subset, so smallest stable-expansion delta) |
| Recommended follow-up PR sequence | `STABLE-TARGET-VENTIQ-001` → `STABLE-TARGET-CORE-001` → `STABLE-TARGET-ROOMIQ-001` → `STABLE-TARGET-AIRIQ-001` → `STABLE-TARGET-AIRIQ-ROOMIQ-001` → `LED-STABLE-PROMOTION-001` (LED stable, gauntlet-gated, only if/when LED bench evidence supports it) |
| LED stable promotion | **Not approved** by this plan; stays `preview` until [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md) closes |
| FanRelay / FanPWM / FanDAC | **Not approved** by this plan; stay `manual-candidate-only` behind `WEBFLASH-RELAY-001` / `WEBFLASH-PWM-001` / `WEBFLASH-DAC-001` and their `RELEASE-*-001` follow-ups |
| FanTRIAC | **Not approved** by this plan; stays `blocked` (HW-005) |
| `config/webflash-builds.json` / `config/product-catalog.json` / `config/compile-only-targets.json` / `config/manual-firmware-artifacts.json` / `config/webflash-compatibility.json` | **None edited** — stable target count stays 1, preview target count stays 1 |
| GitHub Release / `.bin` / checksum / `firmware/sources.json` / `manifest.json` | **none produced or committed** |

The plan documents the per-candidate stable-promotion gate checklist
(G1 top-level YAML, G2 catalog row, G3 top-level full compile, G4
WebFlash wrapper, G5 `artifact_name`, G6 `config/webflash-builds.json`
row, G7 release-notes generation, G8 hardware / compliance, G9 not in
manual lane, G10 preview-to-stable gauntlet) and a per-PR scope
template for the `STABLE-TARGET-*-001` slices. None of these PRs is
approved or scoped by STABLE-TARGET-EXPANSION-PLAN-001 itself. See
[`docs/stable-target-expansion-plan.md`](stable-target-expansion-plan.md).

---

## STABLE-TARGET-VENTIQ-001 — gate-closure deferral (2026-05-28)

`STABLE-TARGET-VENTIQ-001` is the rank-1 follow-up in
[`docs/stable-target-expansion-plan.md` §Recommended follow-up PR sequence](stable-target-expansion-plan.md#recommended-follow-up-pr-sequence)
— the closest stable-expansion delta because the VentIQ subset is
already exercised by stable Release-One. **This PR investigates that
slice against the G1–G10 gate checklist and records the result as a
gate-closure deferral.** It changes no row in the table above and
publishes nothing.

| Aspect | Result |
|---|---|
| New gate-closure record | [`docs/stable-target-ventiq-001-gate-closure.md`](stable-target-ventiq-001-gate-closure.md) |
| `Ceiling-POE-VentIQ` classification | **stays `compile-only`** (compile-only skeleton only; no top-level product YAML; no catalog row; no WebFlash wrapper; no `artifact_name`; no `config/webflash-builds.json` row) |
| Gates closed today | 1 of 10 (G9 — not in manual lane) |
| Gates open today | 9 of 10 (G1, G2, G3, G4, G5, G6, G7, G8, G10) |
| Upstream blocker | G8 — `PACKAGE-POE-410-001`. `S360-410` `schematic_status: cataloged_unverified` per [`config/hardware-catalog.json`](../config/hardware-catalog.json); Release-One PoE "schematic verification pending" caveat preserved verbatim per HW-PINMAP-410-FOLLOWUP / PR #517 |
| Promotion outcome | **Not promoted.** No new top-level YAML, catalog row, wrapper, builds row, `artifact_name`, or top-level compile-only target is added by this PR |
| `config/webflash-builds.json` / `config/product-catalog.json` / `config/compile-only-targets.json` / `config/manual-firmware-artifacts.json` / `config/webflash-compatibility.json` / `config/hardware-catalog.json` | **None edited** — stable target count stays 1, preview target count stays 1, compile-only target count stays 12 |
| GitHub Release / `.bin` / checksum / `firmware/sources.json` / `manifest.json` | **none produced or committed** |
| Resume conditions | Listed in [`docs/stable-target-ventiq-001-gate-closure.md` §Resume conditions](stable-target-ventiq-001-gate-closure.md#resume-conditions) — primarily `PACKAGE-POE-410-001` landing, `S360-100-BENCH-001` `J2`-harness closure, `S360-410 schematic_status: verified` JSON PR, board / package readiness matrix flips, and product-onboarding approval. |

The gate-closure record threads the per-gate evidence picture
(`S360-100` and `S360-211` `verified`; `S360-410`
`cataloged_unverified` — the same caveat Release-One ships under) and
records that **no promotion is performed** until the resume
conditions hold. See
[`docs/stable-target-ventiq-001-gate-closure.md`](stable-target-ventiq-001-gate-closure.md).

---

## Cross-references

- Shipping configuration: [`docs/release-one.md`](release-one.md)
- Release-layer gate: [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
- WebFlash-layer gate: [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md)
- Product-layer gate: [`docs/product-readiness-matrix.md`](product-readiness-matrix.md)
- All-YAML release matrix: [`docs/all-yaml-release-matrix.md`](all-yaml-release-matrix.md)
- **Stable target expansion plan: [`docs/stable-target-expansion-plan.md`](stable-target-expansion-plan.md) (STABLE-TARGET-EXPANSION-PLAN-001)**
- **Stable target VentIQ gate-closure record: [`docs/stable-target-ventiq-001-gate-closure.md`](stable-target-ventiq-001-gate-closure.md) (STABLE-TARGET-VENTIQ-001)**
- **Sense360 PoE room bundle SKU matrix: [`docs/sense360-room-bundles.md`](sense360-room-bundles.md) (BUNDLE-SKU-MATRIX-001) — sellable PoE room bundle SKUs (`S360-KIT-BATH-P` already maps to the stable `Ceiling-POE-VentIQ-RoomIQ` release target in this matrix; `S360-KIT-KITCHEN-P` / `S360-KIT-LIVING-P` / `S360-KIT-BEDROOM-P` / `S360-KIT-CORRIDOR-P` map to non-stable firmware config targets that this matrix already classifies as `compile-only` / `missing-product-yaml`). Bundle SKU is not a firmware config string and is not a release artifact name.**
- Kit intent matrix (productized planning): [`docs/kit-intent-matrix.md`](kit-intent-matrix.md) (KIT-MATRIX-001)
- Manual install path: [`docs/manual-install-fan-candidates.md`](manual-install-fan-candidates.md)
- Compile-only lane: [`docs/compile-only-firmware-validation.md`](compile-only-firmware-validation.md)
- Availability vocabulary: [`docs/product-availability-taxonomy.md`](product-availability-taxonomy.md)

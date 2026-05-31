# First-Release Dry-Run Checklist (FIRST-RELEASE-DRYRUN-CHECKLIST-001)

**Canonical id:** `FIRST-RELEASE-DRYRUN-CHECKLIST-001`
**Type:** Docs only. This document is an **operator checklist**. It **publishes
nothing, builds no `.bin`, promotes nothing, and verifies no hardware.** It does
**not** create a GitHub Release, attach a release asset, edit `manifest.json` /
[`firmware/sources.json`](../firmware/sources.json), change
[`config/webflash-builds.json`](../config/webflash-builds.json) or any other
`config/*.json`, add an `artifact_name`, flip `webflash_build_matrix`, enable a
new WebFlash target, touch the `sense360store/webflash` repo, mark `S360-410`
verified, mark LED stable, or mark any fan variant release-ready.

## Purpose and scope

This is the **single concrete operator checklist for dry-running the current
first-release path** without publishing new firmware or changing WebFlash
exposure. It tells one operator, step by step, how to:

1. rehearse the first-release path end to end (release notes → build workflow →
   artifact naming → checksums) using only **non-publishing** lanes; and
2. confirm — with explicit checks — that the dry-run produced **no** release,
   **no** manifest change, and **no** `firmware/sources.json` change; and
3. capture the **publish-readiness** gates (human review, artifact/checksum
   review, GitHub release-note review, WebFlash handoff, and post-publish
   verification) that a future *real* release will have to satisfy.

It **threads** existing facts from the sources of truth below; it invents
nothing and changes no state. Where this doc and a source-of-truth file ever
disagree, **the source-of-truth file wins** and this doc is the one to fix.

### The one first-release-eligible stable path

Per [`docs/first-release-gates.md`](first-release-gates.md)
(`PRE-HW-PREP-FIRST-RELEASE-GATES-001`) the **only** first-release-eligible
stable path is:

| Field | Value |
|---|---|
| **Bundle SKU** | `S360-KIT-BATH-P` (Bathroom) |
| **Config string** | `Ceiling-POE-VentIQ-RoomIQ` |
| **Channel** | `stable` |
| **Version (current)** | `1.0.0` |
| **Product YAML** | [`products/webflash/ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml) |
| **Chip family** | `ESP32-S3` |
| **Artifact name pattern** | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v<x.y.z>-stable.bin` |
| **Artifact name (at v1.0.0)** | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` |

The artifact-name pattern is the WebFlash contract pattern
`Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin`
(`config/webflash-compatibility.json` → `artifact_pattern`) bound to this config
string and the `stable` channel. **No other config string is dry-run-eligible
for a stable first release.** The preview LED build
(`Ceiling-POE-VentIQ-RoomIQ-LED`,
`Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`) is **preview-only**
and is **not** part of this first-release stable dry-run except where it rides
along automatically in the `all-release-eligible` planner scope.

> **WebFlash first-release gate sync has already run/merged.** This checklist is
> the dry-run rehearsal that precedes any future real publish. It enables no new
> WebFlash target and mirrors nothing into the WebFlash repo.

### Sources of truth (do not duplicate, link instead)

| Layer | Source of truth |
|---|---|
| First-release / expansion gate checklist | [`docs/first-release-gates.md`](first-release-gates.md) (`PRE-HW-PREP-FIRST-RELEASE-GATES-001`) |
| Canonical roadmap / status / blocker view | [`docs/sense360-roadmap-status.md`](sense360-roadmap-status.md) (`DOCS-CONSOLIDATION-ROADMAP-001`) |
| Shippable WebFlash builds (config strings, versions, channels, `artifact_name`) | [`config/webflash-builds.json`](../config/webflash-builds.json) (validated by `tests/validate_webflash_builds.py`) |
| WebFlash grammar / artifact pattern / required configs | [`config/webflash-compatibility.json`](../config/webflash-compatibility.json) · [`docs/webflash-contract.md`](webflash-contract.md) |
| Operational release handoff (repo ↔ WebFlash) | [`docs/webflash-release-handoff.md`](webflash-release-handoff.md) |
| End-to-end pipeline + CI map | [`docs/ci-pipeline.md`](ci-pipeline.md) · [`docs/system-architecture.md`](system-architecture.md) |
| Release-note draft workflow (RELEASE-002) | [`.github/workflows/release-notes-draft.yml`](../.github/workflows/release-notes-draft.yml) |
| Build & release workflow (incl. dry-run mode) | [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml) (`RELEASE-WORKFLOW-DRYRUN-MODE-001`) |
| Recorded repo-side release proof | [`docs/webflash-release-proof.md`](webflash-release-proof.md) |
| Detailed PR working queue | [`UPCOMING_PR.md`](../UPCOMING_PR.md) |

---

## 1. What the dry-run rehearses (and what it must not do)

The first-release path has six observable stages. The dry-run exercises the
first four with **non-publishing** lanes and only *describes* the last two
(they are publish-time / WebFlash-owned and must not be exercised here):

| # | Stage | Dry-run lane | Produces a release? |
|---|---|---|---|
| 1 | Generate release notes | `scripts/generate_webflash_release_notes.py` **or** the `Draft WebFlash Release Notes` workflow | No |
| 2 | Validate release notes | `scripts/validate-webflash-release-notes.py` | No |
| 3 | Plan / rehearse the build | `Build & Release Firmware` workflow with `dry_run=true` (the safe default) | No |
| 4 | Inspect artifact naming + (optional) compile | `config/webflash-builds.json` assertion; optional non-publishing manual build (`dry_run=false`, dev version) | No |
| 5 | Publish GitHub Release + checksums + build-info manifest | **NOT exercised** — real `release: published` event only | Yes (future) |
| 6 | WebFlash import / sign / manifest / deploy | **NOT exercised** — WebFlash-owned, separate repo | Yes (future) |

**Publishing is gated to a real `release: published` GitHub event.** The
`dry_run` input **cannot** publish: the `release` job in
[`firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)
is gated on `if: github.event_name == 'release'` and ignores the input entirely
(`RELEASE-WORKFLOW-DRYRUN-MODE-001`).

---

## 2. Release-note generation (stage 1)

Two equivalent, read-only ways to produce the draft. Both run the **same
generator** and **neither** creates a release, publishes firmware, or commits
the draft.

### 2a. Local generator (fastest)

```bash
# List the canonical release targets first (read-only).
python3 scripts/list_release_targets.py

# Generate + validate the stable first-release draft in one step.
python3 scripts/generate_webflash_release_notes.py \
    --config-string Ceiling-POE-VentIQ-RoomIQ \
    --version 1.0.0 \
    --channel stable \
    --output release-notes.md \
    --validate
```

`release-notes.md` is a **local working file** — it is gitignored-by-intent
(never committed by this path) and is **not** a `.bin` artifact.

### 2b. `Draft WebFlash Release Notes` workflow (RELEASE-002)

Manually dispatch
[`.github/workflows/release-notes-draft.yml`](../.github/workflows/release-notes-draft.yml)
(`workflow_dispatch` only) with:

| Input | Value for the stable first-release dry-run |
|---|---|
| `config_string` | `Ceiling-POE-VentIQ-RoomIQ` |
| `version` | `1.0.0` |
| `channel` | `stable` |
| `changelog` | *(leave blank to get the TODO placeholder, or paste real bullets)* |

The workflow runs the generator, runs the validator, and uploads the result as
the **expiring workflow artifact** `release-notes-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable`
(retention 14 days). Per its own header it does **not** create a GitHub Release,
publish or compile firmware, upload a release asset, infer the changelog from
git history, or commit `release-notes.md`.

### 2c. Changelog expectations

The release body that WebFlash consumes has **four required `##` sections** (see
[`docs/webflash-release-handoff.md`](webflash-release-handoff.md) →
*Release body format*):

- `## Changelog`
- `## Known Issues`
- `## Features`
- `## Hardware Requirements`

Changelog rules to rehearse now and satisfy at publish time:

- When `changelog` is omitted, the generated `## Changelog` is a **TODO
  placeholder** that deliberately survives structural validation. It is a signal
  that the section **still needs human review** — it must be replaced with the
  real, user-visible changes before a real publish.
- On the **`stable`** channel, filler text (`TBD`, `Placeholder`,
  `Initial release`, and similar) is **rejected at publish time** by
  `scripts/validate-webflash-release-notes.py`. Rehearse with realistic bullets
  so the dry-run mirrors the real gate.
- The repo-level [`CHANGELOG.md`](../CHANGELOG.md) is the human history of the
  repository; the release-body `## Changelog` is what WebFlash surfaces to
  installers. Keep them consistent, but the release-body section is the one the
  publish-time gate checks.

---

## 3. Release-note validation (stage 2)

```bash
python3 scripts/validate-webflash-release-notes.py \
    release-notes.md \
    --channel stable
```

(The `--validate` flag in §2a already runs this inline; the draft workflow runs
it as a separate step.) On `stable` this enforces the four `##` sections, bullet
content, and the filler-changelog rejection. A green exit means the body would
pass the **same gate** that the real publish path runs at `release.published`
time inside `firmware-build-release.yml`.

---

## 4. Build workflow in dry-run / manual mode (stage 3)

Use the **`Build & Release Firmware`** workflow
([`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)),
`workflow_dispatch`. It has an explicit, **safe-by-default dry-run mode**
(`RELEASE-WORKFLOW-DRYRUN-MODE-001`).

### 4a. Safe dry-run (default; no compile, no publish)

| Input | Value |
|---|---|
| `version` | `1.0.0` |
| `channel` | `stable` |
| `release_target` | `Ceiling-POE-VentIQ-RoomIQ` |
| `dry_run` | `true` *(default)* |

With `dry_run=true` **only** the `release-dry-run` job runs; `generate-matrix`,
`build`, `release`, and `summary` are all skipped
(`RELEASE-WORKFLOW-DRYRUN-GATE-FIX-001`). That job is **read-only**
(`permissions: contents: read`) and:

- validates the selected target against `config/webflash-builds.json`
  (`scripts/list_release_targets.py --validate`);
- runs the release-note **planner** (`scripts/plan_room_release_notes.py`),
  which writes **nothing** to the repo;
- runs the dry-run guardrail contract tests
  (`tests/test_plan_room_release_notes.py`, `tests/test_release_dry_run_mode.py`);
- asserts **no** release side effects: no `firmware/sources.json`, no
  `manifest.json`, and no `*.bin` left in the repo root.

This lane **creates no GitHub Release, uploads no release asset, and writes no
`firmware/sources.json` or `manifest.json`.**

### 4b. Optional non-publishing compile (inspect a real binary, still no release)

If you want to inspect an **actual** compiled binary's name/size without
publishing, dispatch the same workflow with `dry_run=false` and a **dev**
version that is *not* in the published WebFlash matrix:

| Input | Value |
|---|---|
| `version` | `0.0.0-dev` |
| `channel` | `preview` |
| `single_product` | `sense360-ceiling-poe-ventiq-roomiq` *(optional, to scope to one build)* |
| `dry_run` | `false` |

On a `workflow_dispatch` event the `release` job is still skipped (it requires
`github.event_name == 'release'`), so **no release is created**. The `build`
job compiles with ESPHome `2026.4.5`, renames via
`scripts/product_name_mapper.py`, asserts the name against
`config/webflash-builds.json` (`tests/check_webflash_build_output.py`), and
uploads the result as the **expiring CI artifact** `firmware-<product>`
(retention 7 days). This is a temporary GitHub Actions artifact — **not** a
release asset and **not** a customer-visible build.

> Keep §4b on a **dev** version. Dispatching `dry_run=false` with a real matrix
> version (`1.0.0`/`stable`) still does not publish (no `release` event), but it
> muddies artifact provenance; the dev-version lane keeps the rehearsal clearly
> non-release.

---

## 5. Artifact naming + checksums (stage 4)

### 5a. Expected artifact name

The first-release stable artifact name is fixed by
[`config/webflash-builds.json`](../config/webflash-builds.json):

```
Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin
```

i.e. the pattern `Sense360-Ceiling-POE-VentIQ-RoomIQ-v<x.y.z>-stable.bin` at
`x.y.z = 1.0.0`. The mapping `(product, version, channel) → artifact_name` is
locked by `tests/test_webflash_artifact_naming.py` and re-asserted in CI by the
`Assert renamed binary matches WebFlash build matrix` step
(`tests/check_webflash_build_output.py`). Confirm any rehearsal binary's name
**exactly** matches this string — case, hyphens, the `v` prefix, and the
`-stable.bin` suffix all matter.

### 5b. Checksum expectations

Checksums are a **publish-time** product of the `release` job (real `release:
published` event only). The dry-run does **not** produce them. At real publish
the workflow generates, alongside the `.bin`:

- `checksums-sha256.txt` — `sha256sum *.bin` (the canonical integrity record);
- `checksums-md5.txt` — `md5sum *.bin` (compatibility only);
- a **build-info** `manifest.json` carrying `version`, `channel`, `build_date`,
  `git_sha`, `esphome_version`, `product_count`, and a `files[]` list with each
  binary's `name`, `sha256`, and `size`.

To *preview* a checksum during a §4b non-publishing compile, download the
expiring `firmware-<product>` CI artifact and run `sha256sum` locally — but the
**authoritative** checksum file only exists once a real release is published.
The build-info `manifest.json` is **not** the WebFlash production manifest
(§7.2).

---

## 6. What goes into `firmware/sources.json` *later*

[`firmware/sources.json`](../firmware/sources.json) is the (future) published
firmware **source-of-record** that downstream consumers read. **It does not
exist in this repo today, and this dry-run must not create or change it** — the
dry-run job explicitly fails if it appears.

When a *real* first release is eventually published, the entry for this path
would record (illustrative shape only — **not** written here):

- `config_string`: `Ceiling-POE-VentIQ-RoomIQ`
- `channel`: `stable`
- `version`: `1.0.0`
- `artifact_name`: `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`
- `sha256`: the published artifact's SHA-256 (from `checksums-sha256.txt`)
- `size`: the artifact byte size
- the GitHub release tag / asset URL the binary is attached to.

Writing that entry is a **future, real-publish** action, not part of any
dry-run.

---

## 7. What WebFlash must mirror *later*

WebFlash work is owned by `sense360store/webflash` and is **out of scope** for
this repo and this checklist. It is recorded here only so the handoff
expectation is visible (see
[`docs/webflash-release-handoff.md`](webflash-release-handoff.md)).

### 7.1 The coupling WebFlash mirrors

WebFlash couples to this repo **only** through release tags, config strings, and
artifact names. After a real publish it must mirror:

- the exact config string `Ceiling-POE-VentIQ-RoomIQ`;
- the exact artifact name `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`;
- the `(version, channel)` pair `1.0.0` / `stable`;
- the four required release-body sections.

### 7.2 WebFlash-owned steps (this repo never does these)

- import the release asset + body and generate per-firmware sidecar metadata;
- **sign** firmware with the production key (private key lives only in WebFlash);
- generate the **production** manifest (`manifest.json` / `firmware-N.json`) —
  distinct from this repo's build-info `manifest.json` (§5b);
- deploy the installer (today: GitHub Pages on the WebFlash repo);
- run the post-deploy smoke test.

**This checklist changes nothing in WebFlash and enables no new WebFlash
target.**

---

## 8. Rollback / no-publish safety checks

The dry-run is **inherently reversible** because it produces nothing persistent:

- **No tag is pushed.** A GitHub Release (and therefore the publish path) only
  starts when a maintainer publishes a release/tag. The dry-run never does this.
- **`dry_run` cannot publish.** The `release` job is gated on
  `github.event_name == 'release'` and ignores the `dry_run` input
  (`RELEASE-WORKFLOW-DRYRUN-MODE-001`).
- **No repo state changes.** The planner and the dry-run job are read-only and
  the dry-run asserts no `firmware/sources.json`, no `manifest.json`, and no
  root `*.bin` were produced.
- **Manual artifacts expire.** Any §2b / §4b CI artifact is a temporary GitHub
  Actions artifact (14-day / 7-day retention) — not a release asset.
- **If a real release is ever published by mistake** (out of dry-run scope), the
  rollback is to delete the GitHub Release **and** its tag and re-run the
  WebFlash sync; WebFlash will not import an absent release. That recovery path
  belongs to the real-publish runbook, not to this dry-run.

---

## 9. Dry-run checklist (operator)

Run top to bottom. Every box is a **non-publishing** action.

- [ ] **Generate release notes.** Run §2a (or dispatch §2b). `release-notes.md`
      exists locally / as an expiring workflow artifact.
- [ ] **Validate release notes.** Run §3 (or confirm the draft workflow's
      validate step is green). Exit code `0` on `--channel stable`.
- [ ] **Replace the changelog TODO** with realistic bullets and re-validate, to
      confirm the `stable` filler-rejection gate would pass.
- [ ] **Run the build workflow in dry-run mode.** Dispatch §4a
      (`dry_run=true`, `release_target=Ceiling-POE-VentIQ-RoomIQ`). Only the
      `release-dry-run` job runs and it is green.
- [ ] *(Optional)* **Compile without publishing.** Dispatch §4b
      (`dry_run=false`, `version=0.0.0-dev`) to inspect a real binary; the
      `release` job is skipped.
- [ ] **Inspect artifact naming.** Expected name is exactly
      `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` (§5a); the
      `Assert renamed binary matches WebFlash build matrix` step / artifact
      naming test agree.
- [ ] **Inspect checksums.** Understand that the canonical `checksums-sha256.txt`
      is **publish-time only** (§5b); if you compiled in §4b, you may `sha256sum`
      the expiring CI artifact locally as a preview.
- [ ] **Confirm no publish occurred.** The repo **Releases** page is unchanged;
      no new tag exists; the `release` job did not run.
- [ ] **Confirm no manifest update occurred.** No `manifest.json` was committed
      or left in the tree (the build-info manifest only exists transiently in a
      real `release` run).
- [ ] **Confirm no `firmware/sources.json` update occurred.**
      [`firmware/sources.json`](../firmware/sources.json) is still absent /
      unchanged; the dry-run guardrail asserts this.
- [ ] **Confirm WebFlash is untouched.** No change to
      `config/webflash-builds.json`, no new WebFlash target, no edit in the
      `sense360store/webflash` repo.

---

## 10. Publish-readiness checklist (for the *future* real release)

This is the gate a real publish must clear. It is recorded here for planning; no
box is ticked by this dry-run.

### 10.1 Human review requirements

- [ ] A named release author owns the publish.
- [ ] The `## Changelog` TODO placeholder is replaced with real, user-visible
      changes (no `TBD` / `Placeholder` / `Initial release` filler on `stable`).
- [ ] `version` / `channel` match `config/webflash-builds.json`
      (`1.0.0` / `stable`) and the chosen release tag follows RELEASE-004
      (`v1.0.0` for stable; suffix form only for preview).
- [ ] The first-release gates in [`docs/first-release-gates.md`](first-release-gates.md)
      still show `S360-KIT-BATH-P` / `Ceiling-POE-VentIQ-RoomIQ` / `stable` as the
      only eligible stable path.

### 10.2 Artifact review

- [ ] Exactly one stable `.bin` is attached:
      `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`.
- [ ] Name matches the WebFlash contract pattern exactly (§5a).
- [ ] Size is plausible for ESPHome firmware (≈1 MB; the `release`/build steps
      fail under 100 KB).

### 10.3 Checksum review

- [ ] `checksums-sha256.txt` is attached and lists the stable artifact.
- [ ] The recorded SHA-256 matches the attached `.bin`.
- [ ] `manifest.json` (build-info) `files[]` entry matches the artifact `name`,
      `sha256`, and `size`.

### 10.4 GitHub release-notes review

- [ ] All four `##` sections are present and non-empty.
- [ ] `scripts/validate-webflash-release-notes.py ... --channel stable` passes
      against the **actual** release body.
- [ ] `scripts/check-webflash-release-assets.py` passes (declared
      `artifact_name` present and ≥100 KB).

### 10.5 WebFlash handoff checklist (WebFlash-owned)

- [ ] WebFlash imported the release asset + body.
- [ ] WebFlash generated the metadata sidecar.
- [ ] WebFlash signed the firmware with the **production** key.
- [ ] The WebFlash production manifest includes the
      `Ceiling-POE-VentIQ-RoomIQ` config string.
- [ ] WebFlash deployment smoke test passed (manifest reachable; commit current;
      no placeholder/tiny firmware; rescue firmware exists).

### 10.6 Post-publish verification checklist

(Modelled on the *Release Proof Checklist* in
[`docs/webflash-release-handoff.md`](webflash-release-handoff.md); tick only with
**recorded evidence** — a run URL / release URL / hardware record.)

- [ ] `esphome-public` `Build & Release Firmware` workflow completed
      successfully on the `release` event.
- [ ] The Release-One `.bin` exists on the release and the name matches the
      contract.
- [ ] Release body passed both publish-time gates
      (`validate-webflash-release-notes` + `check-webflash-release-assets`).
- [ ] `firmware/sources.json` updated with the published artifact + sha256 +
      tag (future real-publish action — §6).
- [ ] WebFlash import / sign / manifest / deploy / smoke test recorded.
- [ ] Real-hardware flash test recorded (device flashes via WebFlash, boots,
      Wi-Fi/Improv completes, RoomIQ + VentIQ report, rescue path available).

---

## 11. Dry-run execution record (FIRST-RELEASE-WORKFLOW-DRYRUN-001)

This section records an **actual execution** of the dry-run lanes above against
the current eligible first-release path. It publishes nothing and changes no
state; it threads the real command output captured during the run.

### 11.1 Run metadata

| Field | Value |
|---|---|
| Dry-run id | `FIRST-RELEASE-WORKFLOW-DRYRUN-001` |
| Date | 2026-05-31 |
| Executor | Automated repo session (local, non-publishing lanes) |
| Commit SHA pinned | `6f4b7f748302d8cb600e2dd368076df548ed5f81` |
| Bundle SKU | `S360-KIT-BATH-P` |
| Config string | `Ceiling-POE-VentIQ-RoomIQ` |
| Channel | `stable` |
| Version | `1.0.0` |
| ESPHome version (from the build workflow) | `2026.4.5` |
| Hosted **workflow run URL / run ID** | **Not captured** — see §11.4 |

> **How this was run.** The hosted `Build & Release Firmware`
> (`firmware-build-release.yml`) and `Draft WebFlash Release Notes`
> (`release-notes-draft.yml`) workflows are `workflow_dispatch`-driven, and this
> automation environment has **no GitHub Actions dispatch capability** (no `gh`
> CLI and no Actions/run-workflow tool). So the dry-run was executed by running
> the **same non-publishing scripts and contract tests the `release-dry-run`
> job and the RELEASE-002 draft workflow run**, locally, pinned to the commit
> above. The local lanes are a faithful stand-in for the job steps; the only
> thing they cannot produce is a hosted **run URL / run ID** (§11.4).

### 11.2 Stage results

| # | Stage | Lane exercised | Result |
|---|---|---|---|
| 1 | List + validate target | `scripts/list_release_targets.py` / `--validate Ceiling-POE-VentIQ-RoomIQ` | **PASS** (target is release-eligible; exit 0) |
| 2 | Generate release notes (TODO placeholder) | `scripts/generate_webflash_release_notes.py … --channel stable` (no `--changelog`) | **PASS** — draft generated; the `## Changelog` TODO placeholder **survives** structural validation on `stable` (it is a human-review signal, not finished notes) |
| 3 | Generate release notes (realistic bullets) | `… --changelog "<real bullets>" --validate` | **PASS** — `WebFlash release-notes validation passed (channel=stable)`; exit 0 |
| 4 | Validate release notes (filler negative control) | `… --changelog "Initial release"` then `validate-webflash-release-notes.py … --channel stable` | **PASS (gate works)** — filler is **rejected** on `stable` (exit 1), confirming the publish-time changelog gate |
| 5 | Build workflow dry-run (planner) | `scripts/plan_room_release_notes.py --commit <sha> --config-string Ceiling-POE-VentIQ-RoomIQ` | **PASS** — plan rendered, structural validation `PASSED (structural, channel=stable)`, exit 0; writes nothing to the repo |
| 6 | Dry-run guardrail contract tests | `tests/test_plan_room_release_notes.py` (20) · `tests/test_release_dry_run_mode.py` (17) | **PASS** — 37 tests OK |
| 7 | No-side-effects assertion | check for `firmware/sources.json` / `manifest.json` / root `*.bin` | **PASS** — none present |
| 8 | Artifact naming | `scripts/product_name_mapper.py ceiling-poe-ventiq-roomiq 1.0.0 stable` vs `config/webflash-builds.json` | **PASS** — both equal `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` |

### 11.3 Recorded expectations (not produced by the dry-run)

- **Expected artifact name:** `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`
  (mapper output == `config/webflash-builds.json` `artifact_name`, byte-for-byte).
- **Checksum behavior:** the dry-run produced **no** checksums. `checksums-sha256.txt`,
  `checksums-md5.txt`, and the build-info `manifest.json` are **publish-time
  only** — generated by the `release` job on a real `release: published` event
  (§5b). This is correct/expected for a dry-run.
- **Artifact published:** **none.** No GitHub Release, no tag, no release asset,
  no `firmware/sources.json`, no `manifest.json`, no committed `.bin`. The repo
  working tree was clean after the run.

### 11.4 Outcome classification — `dry-run partial`

**Local dry-run lanes: all PASS.** Every lane that *can* be exercised from this
environment passed end to end, with no publish and no side effects. The pipeline
logic is ready.

The classification is **`dry-run partial`** (not `dry-run passed`) for one
honest reason: the task asks to record a hosted **workflow run URL / run ID**,
and this environment cannot dispatch GitHub Actions, so that hosted-run evidence
could not be captured. It is **not** the case that *"no safe dry-run mode
exists"* — the opposite is true:

- The `Build & Release Firmware` workflow already has a **safe-by-default
  dry-run mode** (`RELEASE-WORKFLOW-DRYRUN-MODE-001`): the `release-dry-run` job
  runs only on `workflow_dispatch && inputs.dry_run` (default `true`), is
  read-only (`permissions: contents: read`), and publishing stays gated on the
  `release` job's `if: github.event_name == 'release'`, which ignores the
  `dry_run` input.
- Because that safe mode **already exists**, the conditional follow-up
  `FIRST-RELEASE-WORKFLOW-DRYRUN-MODE-001` (which the task says to open only *if*
  no safe dry-run mode exists) is **not created** — opening it would fabricate a
  gap that the repo does not have.

### 11.5 Publish-readiness gaps (what a real publish still needs)

Recorded, not resolved — these are the exact gaps between this dry-run and a
real first publish:

1. **Hosted dry-run run evidence not captured.** An operator with GitHub Actions
   access must dispatch `Build & Release Firmware` with `dry_run=true`,
   `release_target=Ceiling-POE-VentIQ-RoomIQ` and record the **run URL / run
   ID** (and, optionally, dispatch RELEASE-002 to capture the expiring
   release-notes artifact). Tracked as
   **`FIRST-RELEASE-WORKFLOW-DRYRUN-CI-RUN-001`** (§14 / `UPCOMING_PR.md`).
2. **Changelog still a placeholder.** The default `## Changelog` is the TODO
   placeholder; it must be replaced with real, user-visible bullets before a
   real `stable` publish (filler is rejected — see Stage 4 above).
3. **`external_components` pin.** `packages/base/external_components.yaml`
   declares git `ref: main`; pin it to `v1.0.0` at release time for a
   reproducible tagged build (recorded by the planner's *Known limitations*).
4. **Publish-time artifacts unproven.** Checksums + build-info `manifest.json`
   only exist on a real `release` run; the §10.2–10.3 artifact/checksum review
   cannot be ticked until then.
5. **All §10 publish-readiness gates remain unticked** (human review,
   artifact/checksum review, GitHub release-note review, WebFlash handoff,
   post-publish verification) — as expected for a dry-run.

### 11.6 Reproduce this record

```bash
# Stage 1–2: release notes (TODO placeholder + realistic + filler negative control)
python3 scripts/list_release_targets.py --validate Ceiling-POE-VentIQ-RoomIQ
python3 scripts/generate_webflash_release_notes.py \
    --config-string Ceiling-POE-VentIQ-RoomIQ --version 1.0.0 --channel stable \
    --output /tmp/release-notes.md --validate            # realistic via --changelog

# Stage 3: build-workflow dry-run job, run locally (writes nothing to the repo)
python3 scripts/list_release_targets.py --validate Ceiling-POE-VentIQ-RoomIQ
python3 scripts/plan_room_release_notes.py \
    --commit "$(git rev-parse HEAD)" \
    --config-string Ceiling-POE-VentIQ-RoomIQ --output /tmp/plan.md
python3 tests/test_plan_room_release_notes.py
python3 tests/test_release_dry_run_mode.py

# Stage 4: artifact name
python3 scripts/product_name_mapper.py ceiling-poe-ventiq-roomiq 1.0.0 stable
```

> Keep generated `release-notes.md` / plan files **out of the repo** (write them
> to `/tmp` as above): they are working files, not committed artifacts, and
> `release-notes.md` is not currently in `.gitignore`.

---

### 11.7 Hosted CI dry-run dispatch attempt (FIRST-RELEASE-WORKFLOW-DRYRUN-CI-RUN-001)

`FIRST-RELEASE-WORKFLOW-DRYRUN-CI-RUN-001` is the residual follow-up from §11.4:
dispatch the hosted dry-run on GitHub Actions and capture the **run URL / run
ID** so the first-release dry-run can move `partial → passed`. This subsection
records that attempt.

**Result: the hosted dry-run could not be dispatched from this environment — the
first-release dry-run stays `partial` (hosted CI dry-run blocked, not passed).**

#### 11.7.1 Intended dispatch (what would have been run)

| Field | Value |
|---|---|
| Workflow name | `Build & Release Firmware` ([`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)) |
| Job that would run | `release-dry-run` (the only job a `workflow_dispatch` with `dry_run=true` runs) |
| Trigger | `workflow_dispatch` (non-publishing dry-run mode, `RELEASE-WORKFLOW-DRYRUN-MODE-001`) |
| Input `version` | `1.0.0` |
| Input `channel` | `stable` |
| Input `release_target` | `Ceiling-POE-VentIQ-RoomIQ` |
| Input `dry_run` | `true` (safe default; non-publishing) |
| Commit SHA (branch HEAD at attempt) | `ee1726b39c1e391d4d9a8f8da5dc4e1c82e8c2c2` |

#### 11.7.2 Recorded run results

| Item | Result |
|---|---|
| Workflow run URL | **None — not dispatched** (access/tooling blocker, §11.7.3) |
| Run ID | **None — not dispatched** |
| Release-note generation result | **N/A for a hosted run** (not dispatched). Re-verified only via the local lanes in §11.2 (stages 1–4 PASS). |
| Artifact naming result | **N/A for a hosted run.** Expected name unchanged: `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` (locally re-asserted in §11.2 stage 8, byte-for-byte vs [`config/webflash-builds.json`](../config/webflash-builds.json)). |
| Checksum behavior | **None produced.** `checksums-sha256.txt` / `checksums-md5.txt` and the build-info `manifest.json` are publish-time only (§5b); a dry-run never produces them and no run occurred. |
| Artifact published | **None.** Nothing was dispatched, built, or uploaded. |

#### 11.7.3 Access / tooling blocker (exact)

The hosted `Build & Release Firmware` and `Draft WebFlash Release Notes`
workflows are `workflow_dispatch`-driven, and **this automation environment has
no path to dispatch a GitHub Actions workflow**:

- **No `gh` CLI** — not installed (`gh: command not found`).
- **No GitHub token** — `GH_TOKEN` and `GITHUB_TOKEN` are both unset.
- **No Actions / run-workflow tool** — the available GitHub MCP tools cover
  files, branches, commits, PRs, issues, releases, tags and search, but expose
  **no** workflow-dispatch / workflow-run / job-log capability.
- **No GitHub API egress** — the only outbound network path is the git
  `local_proxy` remote (`http://local_proxy@127.0.0.1:.../git/...`) used for
  clone / fetch / push to the two allowed repos; `api.github.com` is not
  reachable.
- A branch push / PR **cannot** substitute: the dry-run job runs only on
  `workflow_dispatch` (not on `push` / `pull_request`), so opening this PR does
  **not** produce a `release-dry-run` run.

#### 11.7.4 Guardrail confirmations (all hold trivially — nothing was dispatched)

- ✅ **No GitHub Release created.**
- ✅ **No tag created.**
- ✅ **No release asset published.**
- ✅ **No committed `.bin`.**
- ✅ **No `firmware/sources.json` change** (file still absent).
- ✅ **No `manifest.json` change** (none committed / produced).
- ✅ **No `config/*.json`, `packages/**`, or `products/**` change**; no WebFlash
  repo change; no new WebFlash target.

#### 11.7.5 Disposition

`FIRST-RELEASE-WORKFLOW-DRYRUN-CI-RUN-001` is **blocked on GitHub Actions
access**, not on any repo defect: the safe dry-run mode already exists
(`RELEASE-WORKFLOW-DRYRUN-MODE-001`) and the local lanes all pass (§11.2). To
clear it, an operator — or a CI runner with Actions dispatch (a token + API
egress, or the `gh` CLI) — must dispatch the workflow with the §11.7.1 inputs and
paste the resulting **run URL / run ID** into §11.7.2 here and into
[`docs/first-release-gates.md`](first-release-gates.md) §0.1 and
[`docs/sense360-roadmap-status.md`](sense360-roadmap-status.md) §5. Only then
does the first-release dry-run become `passed`.

---

## 12. Guardrails (explicitly NOT changed)

This PR adds this checklist doc plus pointer rows / an `UPCOMING_PR.md` entry. It
does **not**:

- publish firmware, create a GitHub Release, or push a tag;
- create or commit any `.bin` artifact or checksum file;
- change [`firmware/sources.json`](../firmware/sources.json) (still absent) or
  `manifest.json`;
- change [`config/webflash-builds.json`](../config/webflash-builds.json) or any
  `config/*.json`;
- add an `artifact_name` or flip any `webflash_build_matrix` value;
- enable a new WebFlash target or touch the `sense360store/webflash` repo;
- promote any other bundle (`S360-KIT-KITCHEN-P` / `-LIVING-P` / `-BEDROOM-P` /
  `-CORRIDOR-P` stay candidates; no `current_release_status` change);
- mark `S360-410` verified (`schematic_status` stays `cataloged_unverified`; the
  Release-One PoE "schematic verification pending" caveat is preserved);
- mark LED (`S360-300`) stable (LED firmware stays `preview`; no LED-stable
  claim);
- mark any fan variant (`S360-310` / `S360-311` / `S360-312` / `S360-320`)
  release-ready;
- claim, run, or fabricate any bench / hardware evidence.

No `config/*.json`, `packages/**`, or `products/**` file is edited.

---

## 13. Validation

This PR adds docs only; the existing suite is unchanged:

- `python3 tests/validate_configs.py`
- `python3 tests/test_roadmap_status_doc.py`
- `python3 tests/test_product_catalog.py`
- `python3 tests/validate_webflash_builds.py`
- `python3 -m unittest discover -s tests -p "test_*.py"`

---

## 14. Cross-references

- First-release / expansion gates:
  [`docs/first-release-gates.md`](first-release-gates.md) —
  `PRE-HW-PREP-FIRST-RELEASE-GATES-001`.
- Roadmap / status / blocker view:
  [`docs/sense360-roadmap-status.md`](sense360-roadmap-status.md) —
  `DOCS-CONSOLIDATION-ROADMAP-001`.
- Operational release handoff:
  [`docs/webflash-release-handoff.md`](webflash-release-handoff.md).
- WebFlash grammar / artifact pattern:
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json) ·
  [`docs/webflash-contract.md`](webflash-contract.md).
- Shippable builds: [`config/webflash-builds.json`](../config/webflash-builds.json).
- Release-note draft workflow:
  [`.github/workflows/release-notes-draft.yml`](../.github/workflows/release-notes-draft.yml).
- Build & release workflow (dry-run mode):
  [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml).
- Recorded repo-side release proof:
  [`docs/webflash-release-proof.md`](webflash-release-proof.md).
- Dry-run execution record: §11 above — `FIRST-RELEASE-WORKFLOW-DRYRUN-001`
  (outcome: `dry-run partial`).
- Hosted CI dispatch attempt — **blocked** (access/tooling): §11.7 above —
  `FIRST-RELEASE-WORKFLOW-DRYRUN-CI-RUN-001` (see [`UPCOMING_PR.md`](../UPCOMING_PR.md)).

# Release Pipeline (cross-repo)

This is the end-to-end map of how a Sense360 firmware release travels from a
version bump in this repo
([`sense360store/esphome-public`](https://github.com/sense360store/esphome-public))
to a browser-flashable, signed build served by
[`sense360store/WebFlash`](https://github.com/sense360store/WebFlash). It names
every stage, says whether that stage is **dispatched by a human** or
**fires automatically**, lists its inputs, and calls out the one place the
chain can silently stall — the `GITHUB_TOKEN` recursion guard between "create
the Release" and "build the firmware."

For the *classification* of every workflow (gate vs. manual helper) see
[`ci-pipeline.md`](ci-pipeline.md); for the artifact-name / release-body
**contract** with WebFlash see [`webflash-contract.md`](webflash-contract.md).
This document is the **sequence**; those two are the rules.

> **Two repos, one chain.** Stages 1–4 live in this repo. Stages 5–7 live in
> WebFlash and are the authority for their own inputs and internals — the
> summaries here are a cross-repo orientation, not the WebFlash source of
> truth. When this document and WebFlash's `DEVELOPER.md` disagree, WebFlash
> wins.

---

## The chain at a glance

| # | Stage | Repo | Workflow | How it starts | Produces |
|---|-------|------|----------|---------------|----------|
| 1 | Bump Version | esphome-public | `bump-version.yml` — *Release 1: Bump Version* | **Manual dispatch** | A PR that rewrites the catalog `version` + `artifact_name` |
| — | *(merge the bump PR)* | esphome-public | — | **Human merge** | `main` now declares the new version |
| 2 | Create GitHub Release | esphome-public | `create-release.yml` — *Release: Create GitHub Release* | **Manual dispatch** | The tagged GitHub Release (fires stage 4) |
| 2a | Draft Notes *(optional)* | esphome-public | `release-notes-draft.yml` — *Release 2: Draft Notes* | **Manual dispatch** | A downloadable release-notes draft artifact |
| 3 | Build & Release | esphome-public | `firmware-build-release.yml` — *Release 3: Build & Release* | **Auto** on `release: published` | Signed `.bin` set + checksums attached to the Release |
| 4 | Add Firmware Source | WebFlash | `add-firmware-source.yml` — *Release 4: Add Source* | **Manual dispatch** | Registers this repo's Release as a firmware source |
| 5 | Import | WebFlash | release importer (`scripts/sync-from-releases.py`) | **Dispatch / scheduled** (WebFlash-side) | Pulls the `.bin` set + parses the release body into sidecar metadata |
| 6 | Publish / Deploy | WebFlash | site publish + deploy | **Auto** on merge to the WebFlash publish branch | Signed manifests + the live customer flasher site |

Numbering note: the workflow **display names** in this repo read "Release 1 /
Release 2 / Release 3." The *primary* order is **Bump (1) → Create Release →
Build (3)**; "Release 2: Draft Notes" is an **optional preview-only** helper
off to the side (stage 2a), because Create Release generates and validates the
same notes inline. The table above is in true execution order.

---

## Stage 1 — Release 1: Bump Version

- **Workflow:** [`.github/workflows/bump-version.yml`](../.github/workflows/bump-version.yml)
- **Starts:** manual `workflow_dispatch` only.
- **Inputs:**
  - `config_string` — dropdown of the release-eligible config strings (the
    single source is `config/webflash-builds.json`, listed by
    `scripts/list_release_targets.py`).
  - `version` — new `MAJOR.MINOR.PATCH`; a leading `v` is tolerated and
    normalized away.
- **What it does:** rewrites only the `version` and the version-bearing
  `artifact_name` for the chosen config in **both**
  `config/product-catalog.json` and `config/webflash-builds.json`, proves the
  two stay coherent, and **opens a PR**. It never merges, never tags, never
  builds. The channel is read from the catalog and reused — this step never
  changes it.
- **Then:** a human reviews and **merges** the bump PR. Until it is merged,
  `main` still carries the old version and stages 2/2a fail closed by design
  (with a message naming the pending bump PR).

## Stage 2 — Release: Create GitHub Release

- **Workflow:** [`.github/workflows/create-release.yml`](../.github/workflows/create-release.yml)
- **Starts:** manual `workflow_dispatch` only. Run it **after** the stage-1
  bump PR has merged.
- **Inputs:**
  - `config_string` — same release-eligible dropdown as stage 1.
  - `version` — must equal the catalog version for this config (i.e. the bump
    must be merged first); `plan_release.py` fails closed otherwise.
  - `changelog` — human changelog text (single-line; separate bullets with
    `;`). A real publish is refused if this is empty or left as the TODO
    placeholder.
  - `tag_suffix` — **dropdown**, not free text: blank (use the channel name),
    `led-preview`, or `experimental`. The blank default maps stable → `vX.Y.Z`,
    preview → `-preview`, experimental → `-experimental`.
  - `dry_run` — defaults to **true** (plan/validate/print only, create
    nothing). Set to `false` to actually create the Release.
- **What it does:** resolves the tag / channel / prerelease flag from the
  catalog, generates and validates the WebFlash release notes inline, and —
  when `dry_run=false` — creates the tagged GitHub Release. **Creating the
  Release is the event that fires stage 3.** It builds, signs, attaches, and
  deploys **nothing** itself; it never pushes a branch and never merges.

## Stage 2a — Release 2: Draft Notes *(optional, preview-only)*

- **Workflow:** [`.github/workflows/release-notes-draft.yml`](../.github/workflows/release-notes-draft.yml)
- **Starts:** manual `workflow_dispatch` only.
- **Inputs:** `config_string` (same dropdown), `version`, `channel`
  (`stable` | `preview`), optional `changelog`.
- **What it does:** produces a release-notes **draft**, validates it against
  the WebFlash release-body contract, and uploads it as a workflow artifact for
  preview/download before tagging. It is **not a required step** — Create
  Release (stage 2) generates and validates the same notes inline — and it
  creates no Release, publishes no firmware, and commits nothing. Like stage 2,
  it fails fast if the version is not yet declared in the catalog (the pending
  bump PR has not merged).

## Stage 3 — Release 3: Build & Release

- **Workflow:** [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)
- **Starts:** **automatically**, and **only**, on the GitHub `release:
  published` event. It has **no** `workflow_dispatch` trigger — there is no
  manual "Run workflow" button for this stage today. It derives version +
  channel from the release tag (`scripts/derive_release_version_channel.py`).
- **Inputs:** none (event-driven). The release tag + prerelease flag carry
  everything it needs.
- **What it does:**
  1. Generates the build matrix from `config/webflash-builds.json`, filtered by
     the tag's version + channel (declaration-driven per ESP-007 — **not** a
     `find products/` scan).
  2. Compiles each selected product with the pinned ESPHome version, applying
     the release credential posture (SEC-ESP-BUILD-GATES-001) so binaries ship
     unprovisioned rather than carrying shared default credentials.
  3. Renames each binary to `Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin`
     and scans it for default credentials.
  4. Generates checksums, **signs** `checksums-sha256.txt` with keyless cosign,
     and attaches the `.bin` set + checksums + signature + certificate +
     manifest to the GitHub Release.

  > **This repo publishes *unsigned* firmware `.bin` files.** The cosign
  > signature here is over the **checksums file**, for release-integrity
  > verification. WebFlash is the production **firmware**-signing authority
  > (stage 6). See [`webflash-contract.md`](webflash-contract.md) §7.

### ⚠️ The `GITHUB_TOKEN` cascade caveat (stage 2 → stage 3)

A GitHub Release created with the default `GITHUB_TOKEN` **does not trigger
other workflows** — GitHub's recursion guard suppresses the `on: release`
event when the actor is `GITHUB_TOKEN`. So if stage 2 runs with only
`GITHUB_TOKEN`, the Release is created but **stage 3 does not auto-fire** and
no firmware is built.

- **Recommended fix:** set a repo/org secret **`RELEASE_PAT`** — a fine-grained
  PAT or GitHub App token with `contents: write`. `create-release.yml` uses it
  when present and falls back to `GITHUB_TOKEN` otherwise. With `RELEASE_PAT`
  configured, the publish event fires stage 3 automatically, and the chain is
  truly one-button from stage 2.
- **If a Release was already cut without it:** because stage 3 has **no manual
  dispatch**, the recovery is to **re-emit a fresh `release: published`
  event** — configure `RELEASE_PAT`, then recreate the Release for the same tag
  under that token (e.g. delete the token-created Release and re-run
  `create-release.yml` with `dry_run=false`). Editing an existing Release fires
  `release: edited`, not `published`, so it will **not** wake stage 3. Always
  confirm stage 3 actually started after publishing.

## Stage 4 — WebFlash: Add Firmware Source *(WebFlash repo)*

- **Workflow:** WebFlash `add-firmware-source.yml` — *Release 4: Add Source*.
- **Starts:** manual `workflow_dispatch` in the **WebFlash** repo.
- **Role:** registers this repo's published GitHub Release as a firmware source
  WebFlash will import. Its `config_string` picker must stay in lock-step with
  the release-eligible set here; that parity is enforced by WebFlash's own
  tests (tracked as **P4b** in the CI-PIPELINE-CLARITY-001 programme).
- **Authority:** WebFlash owns this workflow's exact inputs and behaviour; the
  summary here is orientation only.

## Stage 5 — WebFlash: Import *(WebFlash repo)*

- **Tooling:** WebFlash's release importer, `scripts/sync-from-releases.py`.
- **Role:** pulls the unsigned `.bin` set from the GitHub Release and parses the
  Release **body** (the four required H2 sections — Changelog / Known Issues /
  Features / Hardware Requirements) into the sidecar metadata WebFlash stores
  alongside each binary. This is why the release-body contract in
  [`webflash-contract.md`](webflash-contract.md) §8 is load-bearing: a
  malformed body fails the importer.

## Stage 6 — WebFlash: Publish / Deploy *(WebFlash repo)*

- **Role:** WebFlash generates its signed manifests
  (`scripts/gen-manifests.py`) from the imported binaries and deploys the
  customer-facing flasher site. This is the point at which firmware becomes
  **signed** and **served** to customers.
- **Starts:** WebFlash-side publish + deploy (auto on merge to WebFlash's
  publish branch). Deploy status and hosting specifics are WebFlash's to
  report.

---

## Preconditions and fail-closed points

- **Merge before you cut.** Stage 2/2a read `main`; if the stage-1 bump PR is
  unmerged, they fail with an actionable message naming the pending PR.
- **Channel is read, never chosen at cut time.** `plan_release.py` takes the
  channel from `config/product-catalog.json`. Stage 3 filters the matrix on
  version **and** channel and exits non-zero on an empty match, so a stable
  config cut as a preview tag (or vice versa) is caught before the tag exists —
  Create Release re-runs stage 3's own tag normalizer as a preflight to prove
  the round-trip.
- **Only what is declared ships.** Stage 3's matrix is
  `config/webflash-builds.json` filtered by (version, channel). A product that
  is not release-eligible in that file is never built, regardless of dropdowns.
- **No false proof.** A preview/experimental artifact is firmware-build proof
  only — never a hardware, bench, compliance, safety, or commercial-
  availability claim (see [`standing-invariants.md`](standing-invariants.md)).

## See also

- [`ci-pipeline.md`](ci-pipeline.md) — gate-vs-manual classification of every
  workflow, plus the local validation commands.
- [`webflash-contract.md`](webflash-contract.md) — artifact-name grammar and
  the exact release-body sections WebFlash's importer requires.
- [`release-channels.md`](release-channels.md) — what stable / preview /
  experimental mean for a customer.
- [`system-architecture.md`](system-architecture.md) — the whole-pipeline
  architecture view (product YAML → artifact → import → device).
- WebFlash `DEVELOPER.md → Via GitHub Releases` — the authoritative WebFlash-
  side operator flow for stages 4–6.

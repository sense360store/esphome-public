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

> **Two repos, one chain.** Stages 1–4 live in this repo. Stages 5–6 (and the
> Release 4/5 manual recovery path) live in WebFlash and are the authority for
> their own inputs and internals — the summaries here are a cross-repo
> orientation, not the WebFlash source of truth. When this document and
> WebFlash's `DEVELOPER.md` disagree, WebFlash wins.

Since **CI-PIPELINE-CLARITY-002**
([tracking](ci-pipeline-clarity-002.md)) the normal path is:

> version bump PR → human merge → Create GitHub Release → **Release 3
> builds / signs / attaches** → **automatic WebFlash intake dispatch** →
> WebFlash creates **one reviewed intake PR** → human merge → existing
> WebFlash publish / deploy.

The WebFlash *Release 4: Add Source* and *Release 5: Import* workflows are
unchanged and remain the **manual recovery path**.

---

## The chain at a glance

| # | Stage | Repo | Workflow | How it starts | Produces |
|---|-------|------|----------|---------------|----------|
| 1 | Bump Version | esphome-public | `bump-version.yml` — *Release 1: Bump Version* | **Manual dispatch** | A PR that rewrites the catalog `version` + `artifact_name` |
| — | *(merge the bump PR)* | esphome-public | — | **Human merge** | `main` now declares the new version |
| 2 | Create GitHub Release | esphome-public | `create-release.yml` — *Release: Create GitHub Release* | **Manual dispatch** | The tagged GitHub Release (fires stage 3) |
| 2a | Draft Notes *(optional)* | esphome-public | `release-notes-draft.yml` — *Release 2: Draft Notes* | **Manual dispatch** | A downloadable release-notes draft artifact |
| 3 | Build & Release | esphome-public | `firmware-build-release.yml` — *Release 3: Build & Release* | **Auto** on `release: published` | Signed `.bin` set + checksums attached to the Release |
| 4 | WebFlash Intake Handoff | esphome-public | `firmware-build-release.yml` — `webflash-handoff` job | **Auto** after stage 3's attach job succeeds | A `workflow_dispatch` of the WebFlash combined intake (stable/preview only) |
| 5 | Combined Firmware Intake | WebFlash | `firmware-intake.yml` — *Release: Firmware Intake (combined source + import, one PR)* | **Auto** (dispatched by stage 4) or manual dispatch | **One reviewed intake PR** (source registration + import together) |
| — | *(merge the intake PR)* | WebFlash | — | **Human merge** | WebFlash now carries the imported firmware |
| 6 | Publish / Deploy | WebFlash | site publish + deploy | **Auto** on merge to the WebFlash publish branch | Signed manifests + the live customer flasher site |
| R | Add Firmware Source *(recovery)* | WebFlash | `add-firmware-source.yml` — *Release 4: Add Source* | **Manual dispatch** | Registers this repo's Release as a firmware source (manual path) |
| R | Import *(recovery)* | WebFlash | release importer (`scripts/sync-from-releases.py`) | **Dispatch / scheduled** (WebFlash-side) | Pulls the `.bin` set + parses the release body into sidecar metadata (manual path) |

Numbering note: the workflow **display names** in this repo read "Release 1 /
Release 2 / Release 3." The *primary* order is **Bump (1) → Create Release →
Build (3)**; "Release 2: Draft Notes" is an **optional preview-only** helper
off to the side (stage 2a), because Create Release generates and validates the
same notes inline. The table above is in true execution order. The WebFlash
*Release 4: Add Source* / *Release 5: Import* workflows are **retained as the
manual recovery path** (rows "R"): since CI-PIPELINE-CLARITY-002 the normal
path is stage 4's automatic handoff into the combined intake workflow, which
replaces the two manual dispatches with one reviewed WebFlash intake PR.

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
  5. After the attach job succeeds, the `webflash-handoff` job runs stage 4
     below (the automatic WebFlash intake dispatch).

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

## Stage 4 — WebFlash Intake Handoff *(automatic, CI-PIPELINE-CLARITY-002)*

- **Workflow:** the `webflash-handoff` job in
  [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml).
- **Starts:** **automatically**, only after stage 3's *Attach to Release* job
  has **succeeded** (built, verified, signed, attached). A failed or skipped
  attach never hands off.
- **What it does:**
  1. Parses the release event with **inline Python only** — no repository
     checkout, no repo-local scripts, and the release body/tag are treated as
     **untrusted input** (never interpolated into shell; validated against
     strict allowlisted regexes).
  2. Extracts the selected `Config string` / `Version` / `Channel` /
     `Artifact` from the generated release-notes preamble and requires the
     body's version/channel to equal the values stage 3 derived from the tag;
     any mismatch fails closed.
  3. Proves, via the GitHub API, that the **remote** Release now carries the
     selected artifact plus `checksums-sha256.txt` (+ `.sig` / `.pem`) and
     `manifest.json` — the `release: published` event fires before stage 3's
     upload, so the event's own assets array is never trusted for this.
     Nothing is downloaded or re-signed.
  4. For **stable / preview** releases, dispatches the WebFlash combined
     intake workflow (`firmware-intake.yml` on `main` in
     `sense360store/WebFlash`) with the minimum inputs: the release tag, the
     validated config string, `source_repo=sense360store/esphome-public`, and
     `dry_run=false`. Version/channel are deliberately omitted so WebFlash
     derives them from the tag.
  5. For **experimental** (a channel the WebFlash intake lanes do not serve),
     it exits **successfully without dispatching**, with a summary saying why.
- **Credential:** the `WEBFLASH_INTAKE_TOKEN` repository secret (fine-grained;
  target repository `sense360store/WebFlash` only; **Actions: write** only).
  It is exposed solely to the final dispatch step. If it is missing, the
  handoff fails loudly: the upstream release itself is already valid, and the
  manual recovery path below still works.
- **Authority boundary:** the handoff makes **no eligibility decision**.
  Upstream product/catalog status can neither grant nor deny WebFlash intake —
  WebFlash's committed eligibility lanes own the final import decision. A
  successful dispatch (HTTP 204) means only "**handoff accepted**", never
  "WebFlash import succeeded".
- **Contract tests:**
  [`tests/test_webflash_intake_handoff.py`](../tests/test_webflash_intake_handoff.py)
  locks the trust boundaries above (success-only dependency, no checkout, no
  script execution, injection safety, channel gating, remote asset proof,
  token scoping, exact dispatch target).

## Stage 5 — WebFlash: Combined Firmware Intake *(WebFlash repo)*

- **Workflow:** WebFlash `firmware-intake.yml` — *Release: Firmware Intake
  (combined source + import, one PR)*.
- **Starts:** automatically via stage 4's dispatch (normal path), or manual
  `workflow_dispatch` in the **WebFlash** repo.
- **Role:** combines source registration and import into **one reviewed
  intake PR**: it applies WebFlash's committed eligibility lanes, pulls the
  unsigned `.bin` set from the GitHub Release, and parses the Release **body**
  (the four required H2 sections — Changelog / Known Issues / Features /
  Hardware Requirements) into the sidecar metadata WebFlash stores alongside
  each binary. This is why the release-body contract in
  [`webflash-contract.md`](webflash-contract.md) §8 is load-bearing: a
  malformed body fails the importer. A human reviews and **merges** the
  intake PR; merging is what feeds stage 6.
- **Authority:** WebFlash owns this workflow's exact inputs, its eligibility
  decisions, and its internals; the summary here is orientation only.

## Manual recovery path — Release 4: Add Source / Release 5: Import *(WebFlash repo)*

Retained unchanged as the **recovery path** when the automatic handoff fails
(e.g. `WEBFLASH_INTAKE_TOKEN` missing/expired, dispatch refused) or when an
operator wants a hand-driven import:

- **Release 4: Add Source** — WebFlash `add-firmware-source.yml`, manual
  `workflow_dispatch` in the WebFlash repo. Registers this repo's published
  GitHub Release as a firmware source WebFlash will import. Its
  `config_string` picker must stay in lock-step with the release-eligible set
  here; that parity is enforced by WebFlash's own tests (tracked as **P4b** in
  the CI-PIPELINE-CLARITY-001 programme).
- **Release 5: Import** — WebFlash's release importer,
  `scripts/sync-from-releases.py` (dispatch / scheduled, WebFlash-side).
  Pulls the `.bin` set and parses the release body exactly as stage 5 does.
- **Authority:** WebFlash owns these workflows' exact inputs and behaviour;
  the summaries here are orientation only.

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
- **The handoff only follows a proven attach.** Stage 4 runs only when stage
  3's attach job succeeded, re-proves the required assets against the remote
  Release via the GitHub API, fails closed on any malformed or mismatched
  release metadata, and refuses to dispatch channels the WebFlash intake does
  not serve. A handoff failure never un-attaches or invalidates the release —
  the Release 4/5 manual path is the recovery.
- **Handoff ≠ import.** A successful stage-4 dispatch means only that WebFlash
  accepted the request. WebFlash's committed eligibility lanes decide the
  import, and upstream lifecycle status never grants or denies it.

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

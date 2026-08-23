# CI-PIPELINE-CLARITY-002 — execution tracking (esphome-public)

Release-pipeline simplification, phase 1 (upstream handoff). Goal: after
*Release 3: Build & Release* has successfully built, verified, signed and
attached the selected firmware release assets, **automatically dispatch the
combined WebFlash firmware-intake workflow** — replacing the two manual
WebFlash dispatches (Release 4: Add Source, Release 5: Import) on the normal
path with **one reviewed WebFlash intake PR**. Safety gates are not weakened;
Release 4/5 remain the manual recovery path.

The intended normal path after this phase:

> version bump PR → human merge → Create GitHub Release → Release 3
> builds/signs/attaches → **automatic WebFlash intake dispatch** → WebFlash
> creates one reviewed intake PR → human merge → existing WebFlash
> publish/deploy.

**Explicit non-goal (phase 2, not this change):** automating *Create GitHub
Release*. That follows only after this handoff has been proven in production.

## Downstream target (WebFlash-owned)

WebFlash `main` carries `.github/workflows/firmware-intake.yml` — *Release:
Firmware Intake (combined source + import, one PR)*. Its recommended
cross-repo entry point is the GitHub Actions `workflow_dispatch` API. WebFlash
owns all final import eligibility decisions; **upstream lifecycle status is
never treated as WebFlash authorisation**.

## Execution log

| Step | Repo | Status | Notes |
|------|------|--------|-------|
| Phase 1 | esphome-public | EXECUTED (this branch) | Added the `webflash-handoff` job to `firmware-build-release.yml` (runs only after the `release` attach job succeeds; every existing Release 3 build / credential / checksum / cosign / manifest / release-note / asset gate preserved byte-for-byte). The job: parses the release event with inline Python only (no checkout, no repo-local scripts; release body/tag treated as untrusted, strict allowlisted regexes); extracts the selected `Config string` / `Version` / `Channel` / `Artifact` from the generated release-notes preamble; cross-checks version/channel against the `generate-matrix` derived outputs AND requires the body's config string to be one of the configs `generate-matrix` actually built (new `built_config_strings` output); proves via the GitHub API that the **remote** Release carries the selected artifact + `checksums-sha256.txt` (+ `.sig`/`.pem`) + `manifest.json`; dispatches `firmware-intake.yml` @ `main` in `sense360store/WebFlash` for stable/preview (inputs: `release_tag`, `config_string`, `source_repo=sense360store/esphome-public`, `dry_run=false`; version/channel omitted so WebFlash derives them from the tag); exits successfully **without** dispatching for experimental. Both API-calling steps install a redirect-refusing urllib opener so a token-bearing request never follows a cross-host 30x. `WEBFLASH_INTAKE_TOKEN` is scoped to the single final dispatch step; a missing token fails loudly with the manual-intake recovery message. Contract tests: `tests/test_webflash_intake_handoff.py` (structural + behavioural, executing the workflow's actual inline Python against synthetic events and a loopback GitHub API stand-in). Docs: `RELEASE-PIPELINE.md` (normal path + Release 4/5 recovery), `ci-pipeline.md` §3, `workflow-security-hardening.md` §1. |
| Phase 2 | esphome-public | NOT EXECUTED | Automate *Create GitHub Release* — only after the phase-1 handoff is proven. |

## Adversarial security review

An adversarial review (shell injection, event-payload / release-body
manipulation, token exposure, arbitrary downstream dispatch) surfaced four
findings; all were fixed and locked by tests before this branch was
finalised:

1. **Multi-config smuggling (payload manipulation).** In a release that
   builds several configs at one (version, channel), the untrusted body
   could name a co-built-but-unselected config and pass the
   asset-existence check (every co-built binary is attached). Fixed:
   `generate-matrix` now emits `built_config_strings`, and the handoff
   requires the body's config string to be a member of that trusted set.
2. **Token leak via HTTP redirects (token exposure).** urllib's default
   opener follows 30x and re-sends the `Authorization` header to the
   redirect host. Fixed: both API-calling steps install a
   redirect-refusing opener; loopback tests prove the token is never
   re-sent to a second host.
3. **Test denylist gap (shell injection contract).** The "no subprocess"
   test denylist omitted `os.popen` and other spawners. Fixed: added an
   AST-based import/call allowlist that fails closed on any unknown
   spawner, plus an extended substring backstop.
4. **Step `if:` status-override gap (gate integrity).** Nothing forbade a
   future `always()` / `success()` on a step `if:` that would break the
   ordered success chain. Fixed: a test now exact-matches the two gated
   steps' `if:` and forbids status-override functions on every step.

## Owner action required (one-time secret setup)

Automation stays inert (fails loudly at the final step, with the manual
recovery path stated) until the owner creates the repository secret:

- **Name:** `WEBFLASH_INTAKE_TOKEN` (esphome-public repository secret)
- **Type:** fine-grained PAT or GitHub App installation token
- **Target repository:** `sense360store/WebFlash` **only**
- **Permission:** **Actions: write** only — no WebFlash *Contents* write is
  needed merely for this dispatch
- **Rotation:** on expiry the handoff fails loudly with the same actionable
  message; the upstream release itself is unaffected and Release 4/5 manual
  intake keeps working.

## Boundaries held by this phase

- No GitHub Release created, edited or published; nothing tagged; no WebFlash
  dispatch performed while developing/testing the change.
- No firmware binary altered; no product version/channel changed.
- No workflow permission broadened (the handoff job has no `permissions:`
  block; top-level stays `contents: read`).
- `RELEASE_PAT` untouched; `create-release.yml` and `bump-version.yml`
  behaviour unchanged.
- WebFlash Release 4/5 unchanged — retained as the manual recovery path.
- No WebFlash eligibility decision is made in esphome-public: the only
  upstream gate is the channel transport gate (stable/preview dispatch;
  experimental is not served by the intake lanes and skips successfully).

# SECURITY-AUDIT-2026-06 — esphome-public

- **Engagement:** SEC-AUDIT-2026-06 — full defensive security audit from an attacker's perspective.
- **Target:** `sense360store/esphome-public` (PUBLIC). Working tree, full git history (all local branches; remote refs fetched; 0 tags), and the GitHub Actions release/publish pipeline.
- **Date:** 2026-06-10. **Method:** manual source review + history scan. No runtime/penetration testing; no hardware exercised.
- **Status:** review branch `security/audit-2026-06`. **No fixes in this PR.**
- **Prior art cross-checked:** the internal [`security.md`](../../security.md) (2026-06-06) and [`docs/workflow-security-hardening.md`](../workflow-security-hardening.md). Status deltas vs. that audit are called out per finding (its #1 is now tree-remediated but history-resident; #2 is closed; #3/#4/#5 remain open).

## Finding counts by severity

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High     | 2 |
| Medium   | 1 |
| Low      | 4 |
| Info     | 4 |

This repo has **strong CI/supply-chain discipline** (all third-party actions SHA-pinned, no `pull_request_target`, least-privilege `permissions:` with write only in the release job, env-bound workflow inputs, `yaml.safe_load`, fail-closed tag→channel derivation, declaration-driven release matrix). The material risk is **not** the pipeline mechanics; it is that the pipeline **bakes a fixed, now-public credential set into every released firmware binary**, and that previously-hardcoded fallback credentials **remain in public history** even though the tree was fixed.

---

## HIGH

### H1 — Fixed, public credentials are compiled into every released firmware binary
- **Evidence:** [`.github/workflows/firmware-build-release.yml:245-252`](../../.github/workflows/firmware-build-release.yml) (the `secrets-content:` override, comment lines 241-244: *"Release builds bake their own default secrets into the firmware … Keep these bytes unchanged."*). Wiring: [`packages/base/api_encrypted.yaml:1-4`](../../packages/base/api_encrypted.yaml) (`key: !secret api_encryption_key`), [`packages/base/ota.yaml:1-4`](../../packages/base/ota.yaml) (`password: !secret ota_password`), [`packages/base/wifi.yaml`](../../packages/base/wifi.yaml) (`ap: password: !secret fallback_ap_password`), [`packages/base/logging.yaml`](../../packages/base/logging.yaml) (`web_server: auth: !secret web_username/web_password`).
- **Baked values (all public in the workflow + recoverable from the published `.bin`):**
  - `api_encryption_key: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa="` — the all-`a` placeholder; ESPHome native-API encryption is effectively void / publicly known.
  - `ota_password: "sense360-ota-default"`, `fallback_ap_password: "sense360fallback"`, `web_username: "admin"` / `web_password: "sense360admin"`, `wifi_ssid: "Sense360_Setup"` / `wifi_password: "sense360setup"`.
- **Independently extracted** from the downstream-served stable artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.4-stable.bin`: the strings `Sense360_Setup`, `sense360setup`, `sense360-ota-default`, `sense360admin`, `sense360fallback` are present in the binary (the API key is stored as decoded 32-byte key material, not the literal `aaaa…`). These are not throwaway CI-validation secrets — they ship.
- **Exploitation:** an attacker on the same LAN/Wi-Fi as a deployed device uses the public `api_encryption_key` to connect to the ESPHome native API (tcp/6053) and control the device — including mains-switching relay/TRIAC loads — then uses `sense360-ota-default` to push arbitrary replacement firmware (persistent compromise). The web UI on :80 is `admin` / `sense360admin`. If the device drops to its fallback AP, `sense360fallback` lets anyone in RF range join the captive portal and harvest the owner's real Wi-Fi credentials. Because the values are identical across all units, one public-repo read compromises every device still on defaults, and the prebuilt `.bin` cannot be re-keyed without recompiling (Improv only sets Wi-Fi, not the API/OTA/web/fallback secrets).
- **Cross-check:** internal `security.md` #4 rated only the placeholder API key as *Low / "could happen."* It is confirmed **actually shipped** alongside four more fixed credentials, so the real severity is higher.
- **Remediation (one line):** generate unique per-device `api_encryption_key` / `ota_password` / `fallback_ap_password` / `web_password` at provisioning (or via an Improv/first-boot flow) and fail the release build if any secret equals a known placeholder/CI literal.
- **Status (2026-06-10): REMEDIATED — SEC-ESP-BUILD-GATES-001.** Two layers, both PR-tested: (1) a permanent artifact-level gate ([`scripts/check_firmware_default_credentials.py`](../../scripts/check_firmware_default_credentials.py)) scans every produced binary after compile and again before release attachment for the denylisted credential classes (`api_encryption_key` placeholder as base64 literal *and* decoded 32-byte material, `ota_password` defaults, `web_password` defaults, `fallback_ap_password` defaults plus the H2 burned literals, CI-lane `wifi_ssid`/`wifi_password` test values) and fails the release naming artifact + class, failing closed on an empty artifact set; (2) the fixed secrets-content override is gone — release builds strip `api.encryption`, the OTA password, the `web_server` auth block, and the fallback-AP password ([`scripts/apply_release_secret_posture.py`](../../scripts/apply_release_secret_posture.py)), so released firmware ships **unprovisioned instead of falsely secured** (no first-boot flow exists in this tree that could set per-device secrets; Improv-style provisioning covers WiFi only). The intentionally-public setup-network `wifi_ssid`/`wifi_password` pair is the only documented exclusion. Fresh-flash posture, first-boot steps, and the per-device provisioning follow-up (`SEC-ESP-PROVISIONING-001`) are recorded in [`release-firmware-credential-posture.md`](release-firmware-credential-posture.md).

### H2 — Predictable fallback-AP passwords persist in public git history (no rotation for shipped units)
- **Evidence:** pre-remediation content at `e6a15dd^:packages/base/wifi.yaml:4` (`fallback_ap_password: "Sense360Fallback"`, consumed at `:16`) and `e6a15dd^:products/sense360-poe.yaml:52` (`fallback_ap_password: "sense360poe"`). Remediated in the tree by commit `e6a15dd` (SEC-ESP-FALLBACK-AP-001 → now `!secret`). Reach: the literals are live (non-comment, non-test) across **125 commits** reachable from `git rev-list --all`.
- **Exploitation:** the public repo's history is world-readable forever. An RF-range attacker reads `e6a15dd^` (or any of 125 commits), recovers `Sense360Fallback` / `sense360poe`, joins the fallback AP of any unit flashed before the fix, and reconfigures the device or harvests Wi-Fi credentials via the captive portal. The tree fix does not help already-shipped units or anyone reading history.
- **Cross-check:** internal `security.md` #1 was *Medium-High / Open* against the tree; the tree is now fixed but the **history dimension and the absence of a documented credential-rotation for shipped units are not addressed**.
- **Remediation (one line):** rotate the fallback-AP credential on shipped units and treat the historical literals as permanently burned (history rewrite is generally infeasible on a public repo — assume disclosed and rotate).
- **Status (2026-06-10): forward half ADDRESSED — SEC-ESP-BUILD-GATES-001; history dimension OPEN.** Both burned historical fallback-AP literals are on the release gate's denylist ([`scripts/check_firmware_default_credentials.py`](../../scripts/check_firmware_default_credentials.py)), so no future release artifact can ship them again; new release builds additionally carry no fallback-AP password at all (open setup AP, see [`release-firmware-credential-posture.md`](release-firmware-credential-posture.md)). The history dimension is **not** addressed and stays open: the literals remain world-readable in public git history forever — treat them as permanently burned and rotate (re-flash) already-shipped units; a history rewrite is out of scope and would not un-disclose them.

---

## MEDIUM

### M1 — Release checksums are unsigned and release assets are mutable (the June 10 narrowing class)
- **Evidence:** [`.github/workflows/firmware-build-release.yml:543-559`](../../.github/workflows/firmware-build-release.yml) generates `checksums-sha256.txt` / `checksums-md5.txt` in-job; lines 623-632 upload them with `softprops/action-gh-release` (SHA-pinned). No detached signature / cosign / attestation is produced. GitHub release assets are mutable by default.
- **Exploitation:** anyone who can alter a release asset (a compromised token, a re-run of a privileged workflow, or a maintainer account) can replace a `.bin` and rewrite `checksums-sha256.txt` to match — the checksum file proves integrity against corruption, not authenticity against tampering. This is the mechanism behind the recorded **June 10 incident** where `checksums-sha256.txt` was narrowed out from under downstream consumers. MD5 additionally must not be relied on.
- **Cross-check:** internal `security.md` #3 (*Medium / Open*) — still open. The downstream blast radius is partly contained by WebFlash pinning its own `expected_sha256` in `firmware/sources.json` plus the PR-time `validate-source-checksums.py` guard, but the upstream artifact itself remains unauthenticated.
- **Remediation (one line):** sign `checksums-sha256.txt` (cosign keyless via the workflow OIDC identity, or GPG detached) and/or enable immutable releases + build provenance attestation; drop or de-label MD5.
- **Status (2026-06-10): REMEDIATED (signing half) — SEC-ESP-CHECKSUM-SIGNING-001.** The release job now signs `checksums-sha256.txt` with keyless cosign (`cosign sign-blob` via the job's OIDC identity; `sigstore/cosign-installer` SHA-pinned at v3.9.2, cosign CLI pinned at v2.6.3) and publishes the `.sig` + `.pem` certificate as release assets alongside the checksums file. Ordering is enforced in-job: the SEC-ESP-BUILD-GATES-001 default-credential gate passes → checksums generate → cosign signs (then self-verifies with the exact consumer recipe) → all assets upload; any signing failure fails the release before upload, so an unsigned checksums file is never published. `id-token: write` is granted to the `release` job only — no other job or workflow gains it (allowlisted in `tests/test_workflow_permissions.py`). The consumer verification recipe — pinning certificate identity `https://github.com/sense360store/esphome-public/.github/workflows/firmware-build-release.yml@refs/tags/<TAG>` and OIDC issuer `https://token.actions.githubusercontent.com`, so verification proves WHO signed — is documented in [`checksums-verification.md`](checksums-verification.md). Release assets themselves remain **mutable at the platform level**: the platform-side complement is the Item 7 checklist line 9 below (enable immutable releases + artifact attestations), which only the owner can flip — until then the signature makes a swap detectable rather than impossible. `checksums-md5.txt` stays published for legacy compatibility only and is not signed.

---

## LOW

### L1 — The experimental (FanTRIAC mains) release channel has no mandated safety/compliance warning in its release notes
- **Evidence:** [`scripts/validate-webflash-release-notes.py`](../../scripts/validate-webflash-release-notes.py) `--channel` accepts any value (no `choices=`, `default="stable"`) and `REQUIRED_SECTIONS` is the four generic sections (`Changelog`/`Known Issues`/`Features`/`Hardware Requirements`); only `channel == "stable"` triggers extra human-authored-changelog/filler checks. `experimental` is a first-class build channel ([`config/webflash-compatibility.json:50-58`](../../config/webflash-compatibility.json) `allowed_channels`, emitted by [`scripts/derive_release_version_channel.py`](../../scripts/derive_release_version_channel.py)) used to publish the S360-320 mains-touching firmware. The policy's `explicit_warning_families` (FanTRIAC/LED/…) in [`config/release-channel-policy.json`](../../config/release-channel-policy.json) is eligibility metadata, not a release-notes safety gate.
- **Exploitation:** an `v1.0.0-experimental` prerelease can publish a directly-downloadable mains-control `.bin` whose release body carries no mandated "controls mains / not compliance-certified / never placed on market" warning, and CI passes. An advanced self-builder flashing it manually gets no enforced safety notice at the source. (Containment is otherwise strong: tag→channel derivation fails closed, stable/preview tags exclude experimental, and WebFlash refuses FanTRIAC via `block_tokens`.)
- **Remediation (one line):** require an explicit mains-safety/non-compliance warning section in the release-notes validator for `channel == "experimental"` (and restrict `--channel` to a known set).

### L2 — Operator's first name appears in public docs beyond the accepted bench-proof
- **Evidence:** `docs/cleanup-audit.md:11769,11772`; `docs/workflow-audit-2026-06.md:42,117,119,208`; `docs/product-config-audit-2026-06.md:219` — all name "Neil" as the decision-maker. The full name is correctly confined to the accepted `docs/package-triac-001-operator-bench-proof.md` (per scope, not flagged); these three are additional identity disclosures.
- **Exploitation:** minor PII aggregation — ties a named individual to the project's decision authority and (via the bench-proof) a UK residential mains install.
- **Remediation (one line):** replace casual first-name references in audit docs with a role label ("the operator"/"the owner").

### L3 — Release `manifest.json` is assembled by shell interpolation and uploaded without a JSON-validity gate
- **Evidence:** [`.github/workflows/firmware-build-release.yml:564-590`](../../.github/workflows/firmware-build-release.yml) builds `all-firmware/manifest.json` via a heredoc interpolating `version`/`channel`/`git_sha`/per-file loop output; no `python3 -m json.tool` parse check before upload (lines 623-632).
- **Exploitation:** low — values are derived from validated sources, but a future field or an unusual filename could emit invalid JSON that silently breaks downstream consumers; it is also a (review-gated) string-interpolation surface.
- **Cross-check:** internal `security.md` #5 (*Low / Open*) — still open.
- **Remediation (one line):** add `python3 -m json.tool all-firmware/manifest.json >/dev/null` immediately after generation.
- **Status (2026-06-10): REMEDIATED — SEC-ESP-BUILD-GATES-001.** The release job now parses `all-firmware/manifest.json` with `python3 -m json.tool` immediately after generation and before upload (closes internal `security.md` #5).

### L4 — `products/secrets.yaml` was tracked in history (symlink), now removed
- **Evidence:** added `f74dc4e` (2026-05-30, mode `120000`, blob `e50444e3` → `../secrets.example.yaml`), removed `59a3bf0` (2026-06-06, SEC-ESP-SECRET-GUARD-001); guard `scripts/check-no-tracked-secrets.py` broadened to all depths.
- **Exploitation:** none occurred — the tracked object was only a symlink to the example template (no secret material). Reported for completeness; it was a footgun (a developer dropping real creds at that path + `git add` would have committed them).
- **Cross-check:** internal `security.md` #2 (*Medium / Open*) — **now closed** in tree and guard.
- **Remediation (one line):** none required; keep the broadened guard.

---

## INFO

- **I1 — `${{ matrix.* }}` interpolated into `run:` blocks.** [`firmware-build-release.yml`](../../.github/workflows/firmware-build-release.yml) (e.g. `:326`, `:329`, `:430`) and [`ci-validate-configs.yml:221`](../../.github/workflows/ci-validate-configs.yml) interpolate `matrix.product` / `matrix.file` directly into shell. These derive from committed `config/webflash-builds.json` / a discovery glob, so injection requires merge access (branch-protection-gated) and the tokens are read-only. Defense-in-depth: bind to `env:` and reference `"$VAR"`. (Operator-facing `inputs.*` are already env-bound — good hygiene.)
- **I2 — `RELEASE_PAT` is a privilege-escalation-relevant secret.** [`create-release.yml:104`](../../.github/workflows/create-release.yml) uses `secrets.RELEASE_PAT || secrets.GITHUB_TOKEN` to create releases that trigger downstream build/publish. Its scope/expiry cannot be read from the tree → see checklist item. A classic over-scoped PAT here is the most valuable single secret in the org.
- **I3 — CI placeholder credentials are fixed and predictable** ([`.github/actions/setup-esphome-build/action.yml`](../../.github/actions/setup-esphome-build/action.yml) defaults; `manual-firmware-artifacts.yml:140-148`). Acceptable for compile/validate lanes provided they never reach real devices and are never logged (they are redirected to a file, not echoed). Keep strictly test-only.
- **I4 — Verified-good (no action):** every third-party action is SHA-pinned (complete); no `pull_request_target`; `pull_request`/`push` CI lanes run read-only with no secrets; least-privilege `permissions:` (top-level `contents: read`, `contents: write` only in `bump-version` / `create-release` / the `firmware-build-release` `release` job, `pull-requests: write` only where a PR is opened); tag→channel derivation fails closed on bad suffixes; the release matrix is declaration-driven (no broad `products/` scan). No `id-token: write` / OIDC was used here at audit time (it lived in the WebFlash Pages deploy). *(Update 2026-06-10: `SEC-ESP-CHECKSUM-SIGNING-001` introduced the repo's single `id-token: write` grant, scoped to the `firmware-build-release.yml` `release` job for keyless cosign signing of the checksums file — see M1.)*

---

## Item 7 — Manual repo-settings checklist for the owner (cannot be read from the tree)

> Verify each of the following in GitHub repo/org settings for `sense360store/esphome-public`. These govern whether the pipeline hardening above is actually enforced.

1. **Branch protection on `main`:** require PRs (no direct pushes), require the `CI: Quick Validation` (validate.yml) status check to pass, require ≥1 review, dismiss stale approvals, and require branches up to date before merge.
2. **Required status checks** include the catalog/build-matrix coherence checks and `CI: Quick Validation`; confirm they are *required*, not merely present.
3. **Force-push and deletion rules:** block force-push and block deletion of `main` (and of `security/*` review branches); enforce for admins.
4. **Actions permissions — default token:** set the workflow default `GITHUB_TOKEN` to **read-only** at the repo/org level (workflows opt up per-job, which they already do).
5. **Actions permissions — fork PR policy:** require approval to run workflows on PRs from first-time/all outside contributors; confirm forks cannot read secrets (they can't on `pull_request`, but verify "Send write tokens / secrets to workflows from fork PRs" is **off**).
6. **Allowed actions policy:** restrict to "actions by GitHub + selected/verified creators + pinned SHAs," matching the SHA-pinning already in the tree.
7. **`RELEASE_PAT` secret:** confirm it is a fine-grained PAT (or GitHub App token) scoped to **only this repo** with **only `contents: write`**, has an expiry, and is rotated; prefer a GitHub App over a classic PAT. (Referenced by `create-release.yml`.)
8. **Deploy/release environment protection:** if a `release`/build environment exists, add required reviewers and restrict which branches/tags can deploy; consider gating the `firmware-build-release` release job behind an environment with manual approval.
9. **Release immutability / provenance:** enable immutable releases (so published `.bin` + `checksums-sha256.txt` cannot be silently overwritten — the June 10 class) and turn on artifact attestations / build provenance.
10. **Dependabot:** enable Dependabot alerts + security updates, and `version-update`s for GitHub Actions pins (so SHA pins are bumped for CVEs).
11. **Secret scanning + push protection:** enable GitHub secret scanning **and** push protection org-wide (the in-repo guards only check the index, not history or arbitrary names — see H2/L4).
12. **Tag protection:** protect `v*` release tags so only the release workflow/maintainers can create/move them (prevents a forged `*-experimental` mains tag).

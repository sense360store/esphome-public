# REBUILD-CLEAN-CREDENTIALS-001 — programme plan of record and execution log

**Programme:** `REBUILD-CLEAN-CREDENTIALS-001` (this repo) +
`WF-H1-REIMPORT-CLEAN-001` (downstream
[`sense360store/WebFlash`](https://github.com/sense360store/WebFlash)).
**Audit basis:** [`docs/security/SECURITY-AUDIT-2026-06.md`](security/SECURITY-AUDIT-2026-06.md)
finding H1 (shared default control credentials compiled into every released
binary) plus the forward half of H2 (burned fallback-AP literals). The
pipeline fix is `SEC-ESP-BUILD-GATES-001` (PR #779, merged 2026-06-10);
this programme is the **field-distribution half**: every binary WebFlash
currently serves was built before that fix.

This file is the programme **tracking file** (plan of record + execution
log). The detailed policy rationale lives in the earlier plan document
[`docs/security/rebuild-clean-credentials-001.md`](security/rebuild-clean-credentials-001.md);
the recon below re-verified that plan against live release data on
2026-07-06 and found it still exact. Where the two files disagree, this
one is newer and wins.

Every PR in this programme is **HOLD FOR OWNER** — nothing merges on green
alone. The agent never dispatches a release workflow, pushes a tag, creates
a release, or modifies a workflow file; release execution is owner-only.

---

## Recon (read-only, 2026-07-06)

### Currently served WebFlash sources vs the credential gate

Source of truth read: `firmware/sources.json` on `sense360store/WebFlash`
`main` (raw URL). The credential gate (`SEC-ESP-BUILD-GATES-001`, commit
`9514803`) merged **2026-06-10 18:57 UTC**. Tag dates below are from this
repo's git history.

| # | config_string | release_tag | version | channel | Tag date | Predates gate? |
|---|---|---|---|---|---|---|
| 1 | `Ceiling-POE-VentIQ-RoomIQ` | `v1.0.4` | 1.0.4 | stable | 2026-06-07 | **YES** |
| 2 | `Ceiling-POE-RoomIQ` | `v1.0.5` | 1.0.5 | stable | 2026-06-08 | **YES** |
| 3 | `Ceiling-POE-AirIQ-RoomIQ` | `v1.0.6` | 1.0.6 | stable | 2026-06-09 | **YES** |
| 4 | `Ceiling-POE-VentIQ-RoomIQ-LED` | `v1.0.0-led-preview` | 1.0.0 | preview | 2026-05-15 | **YES** |
| 5 | `Ceiling-POE-VentIQ-FanPWM-RoomIQ` | `v1.0.0-preview` | 1.0.0 | preview | 2026-06-02 | **YES** |
| 6 | `Ceiling-POE-VentIQ-FanDAC-RoomIQ` | `v1.0.0-preview` | 1.0.0 | preview | 2026-06-02 | **YES** |
| 7 | `Ceiling-POE-AirIQ-FanRelay-RoomIQ` | `v1.0.0-preview` | 1.0.0 | preview | 2026-06-02 | **YES** |
| 8 | `Ceiling-POE-AirIQ-FanPWM-RoomIQ` | `v1.0.0-preview` | 1.0.0 | preview | 2026-06-02 | **YES** |
| 9 | `Ceiling-POE-AirIQ-FanDAC-RoomIQ` | `v1.0.0-preview` | 1.0.0 | preview | 2026-06-02 | **YES** |

**All nine served sources predate the credential gate.** No served binary
was built on the gated pipeline.

### Credential gate wiring (confirmed in-tree)

`scripts/check_firmware_default_credentials.py` gates the release build
path in [`firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)
("Release 3: Build & Release", the only workflow that publishes release
`.bin` assets, driven by [`config/webflash-builds.json`](../config/webflash-builds.json)
per ESP-007):

1. **Posture strip (before compile):** `scripts/apply_release_secret_posture.py`
   (workflow line ~275) removes API encryption, OTA password, web-server
   auth, and the fallback-AP password in the build workspace, fail-closed.
2. **Per-product gate (after compile):**
   `python3 scripts/check_firmware_default_credentials.py "$FIRMWARE_PATH"`
   (workflow line ~519) scans each compiled binary against the deny list.
3. **Release-set gate (before attach):**
   `python3 scripts/check_firmware_default_credentials.py --dir all-firmware`
   (workflow line ~592) re-scans the full artifact set, fail-closed on empty.
4. **Cosign signing (after the gates, before upload):** keyless cosign signs
   `checksums-sha256.txt` (workflow line ~629, `SEC-ESP-CHECKSUM-SIGNING-001`).

These steps run on **every** release event regardless of channel, so each
rebuild below either publishes clean and signed or fails before attach. The
scanner's own behaviour is locked by
`tests/test_check_firmware_default_credentials.py`, run per-push in
[`validate.yml`](../.github/workflows/validate.yml).

### Rescue build (R-D5) — confirmed clean, no rebuild

The WebFlash in-tree Rescue firmware
(`Sense360-Rescue-v1.0.0-rescue.bin`, served at
`https://sense360store.github.io/WebFlash/firmware/rescue/`) was fetched
read-only on 2026-07-06; its SHA-256 matched the served
`firmware/rescue/manifest.json`
(`feeae47feb8bf71549e018fc8028ca702edcd14c6f9888a2478c5d6d6d09d5c7`), and
this repo's deny-list scanner (`scripts/check_firmware_default_credentials.py`)
was run against the binary locally: **PASS** (exit 0, zero deny-list
matches). Per R-D5: the Rescue build is clean per the deny list and is
**not** rebuilt by this programme.

---

## Plan of record

### Group A — rebuild through the sanctioned pipeline (3 stables + 1 LED preview)

Patch-increment per product (R-D2). All four proposed tags verified **free**
against `origin` tags on 2026-07-06 (existing tags: `v1.0.0`–`v1.0.6`,
`v1.0.0-preview`, `v1.0.2-preview`, `v1.0.0-led-preview`; the bare `v1.0.1`
stable tag exists but is a different tag from `v1.0.1-led-preview`, exactly
mirroring the existing `v1.0.0` / `v1.0.0-led-preview` coexistence).

| # | config_string | Live tag (cred-bearing) | New version | New tag | New artifact name | Channel |
|---|---|---|---|---|---|---|
| 1 | `Ceiling-POE-VentIQ-RoomIQ` | `v1.0.4` | **1.0.7** | `v1.0.7` | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.7-stable.bin` | stable |
| 2 | `Ceiling-POE-RoomIQ` | `v1.0.5` | **1.0.8** | `v1.0.8` | `Sense360-Ceiling-POE-RoomIQ-v1.0.8-stable.bin` | stable |
| 3 | `Ceiling-POE-AirIQ-RoomIQ` | `v1.0.6` | **1.0.9** | `v1.0.9` | `Sense360-Ceiling-POE-AirIQ-RoomIQ-v1.0.9-stable.bin` | stable |
| 4 | `Ceiling-POE-VentIQ-RoomIQ-LED` | `v1.0.0-led-preview` | **1.0.1** | `v1.0.1-led-preview` | `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.1-preview.bin` | preview |

All four have live rows in `config/webflash-builds.json` (verified), so
Release 3 builds them with the posture strip, deny-list gates, and cosign
signing applied automatically. Out of scope: `Ceiling-POE-RoomIQ-LED`
(matrix row exists but not served) and `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`
(experimental row, not served, FanTRIAC standing invariant applies — no
change of any kind proposed here).

### Group B — the five fan previews: de-list downstream, do not rebuild (R-D1)

Served from `v1.0.0-preview`, all pre-gate, all cred-bearing. Exact config
strings to de-list in WebFlash (`WF-H1-REIMPORT-CLEAN-001` step W1):

1. `Ceiling-POE-VentIQ-FanPWM-RoomIQ`
2. `Ceiling-POE-VentIQ-FanDAC-RoomIQ`
3. `Ceiling-POE-AirIQ-FanRelay-RoomIQ`
4. `Ceiling-POE-AirIQ-FanPWM-RoomIQ`
5. `Ceiling-POE-AirIQ-FanDAC-RoomIQ`

They cannot be rebuilt on the sanctioned pipeline: the fan-token guardrail
keeps fan rows out of `config/webflash-builds.json` (verified: no fan row
today), Release 3 builds only what that file declares, and the release
workflows' choice lists contain no fan config. Per R-D1 each de-listed
preview gets a de-list reason in the WebFlash sources data and one line in
the advisory's affected section. They are Advanced-install-only,
acknowledgement-gated previews — never stable, recommended, default, or
buyable — so de-listing has no customer-baseline impact.

### Old releases (R-D3)

Superseded release assets are **left in place, never deleted**; the owner
annotates the old releases' notes with a one-line advisory link (owner
runbook step 9). Exposure control is WebFlash no longer serving them.

---

## Owner dispatch runbook (owner-only; the agent never dispatches)

Prerequisite: auto-trigger from a published release to Release 3 needs the
`RELEASE_PAT` repo/org secret (a release created with the default
`GITHUB_TOKEN` does not fire downstream workflows). Without it, run
"Release 3: Build & Release" manually via its `workflow_dispatch` after
each release is created.

For **each** Group A config, in order:

1. **Actions → "Release 1: Bump Version"** (`bump-version.yml`,
   `workflow_dispatch`): `config_string` = the config, `version` = the new
   version from the table below. This opens a PR bumping `version` +
   `artifact_name` in `config/product-catalog.json` and
   `config/webflash-builds.json`. **Review and merge that PR** before
   step 2 (`plan_release.py` fails closed otherwise).
2. **Actions → "Release: Create GitHub Release"** (`create-release.yml`,
   `workflow_dispatch`): `config_string` and `version` as in step 1;
   `tag_suffix` = blank for the three stables, `led-preview` for the LED
   config; `changelog` = a security-rebuild line, e.g.
   `Security rebuild on the unprovisioned build path; removes the previously baked default API, OTA, web, and fallback credentials; no functional firmware change from v<old>.`
   Run once with `dry_run=true`, review the planned tag and notes in the
   run summary, then re-run with `dry_run=false`.
3. **"Release 3: Build & Release"** fires on the published release (or is
   dispatched manually) and runs posture strip → compile → per-product
   deny-list gate → release-set deny-list gate → cosign signing → attach.
   **Watch each run: the credential gates must pass.** If any gate fails,
   stop and bring the log back for analysis.

| config_string | Release 1 `version` | Create Release `version` | `tag_suffix` | Resulting tag |
|---|---|---|---|---|
| `Ceiling-POE-VentIQ-RoomIQ` | `1.0.7` | `1.0.7` | _(blank)_ | `v1.0.7` |
| `Ceiling-POE-RoomIQ` | `1.0.8` | `1.0.8` | _(blank)_ | `v1.0.8` |
| `Ceiling-POE-AirIQ-RoomIQ` | `1.0.9` | `1.0.9` | _(blank)_ | `v1.0.9` |
| `Ceiling-POE-VentIQ-RoomIQ-LED` | `1.0.1` | `1.0.1` | `led-preview` | `v1.0.1-led-preview` |

After each Release 3 completes, the new `expected_sha256` values are read
from the published, cosign-verifiable `checksums-sha256.txt` per the
handoff procedure in
[`docs/security/rebuild-clean-credentials-001.md`](security/rebuild-clean-credentials-001.md)
and carried into the WebFlash re-import (W2).

---

## Decisions of record

| ID | Decision | Resolution |
|---|---|---|
| R-D1 | Fan preview users | De-list the five previews; one line each in the advisory's affected section; de-list reason recorded in WebFlash sources data. **Adopted.** |
| R-D2 | Version numbers | Patch increment per product: `1.0.7` / `1.0.8` / `1.0.9` stable, `1.0.1` LED preview (tags verified free). **Proposed here; ratified by merging this PR.** |
| R-D3 | Old release assets | Left in place, release notes annotated (owner runbook step 9), never deleted. **Adopted.** |
| R-D4 | Bench acceptance | Owner flashes one rebuilt stable; six-point checklist testing the **actual shipped (unprovisioned) posture**: (1) boot + sensors OK; (2) old shared default credential material **absent** (deny-list scanner `scripts/check_firmware_default_credentials.py` passes against the flashed binary); (3) native API **unencrypted** (Home Assistant adopts the device without an encryption key); (4) OTA **unauthenticated** (an `esphome upload` / OTA push needs no password); (5) web interface (`:80`) **unauthenticated**; (6) fallback/setup AP **open** (joins with no password). The checklist makes **no claim of unique credential generation** — the rebuilt binary is unprovisioned per [`docs/security/release-firmware-credential-posture.md`](security/release-firmware-credential-posture.md); per-device provisioning stays the unimplemented `SEC-ESP-PROVISIONING-001` follow-up. Attestation is owner-authored only and pasted on the W2 PR. **Adopted; checklist corrected by `RECON-UPSTREAM-CRED-CLAIMS-001` (the original four-point list wrongly assumed unique per-device credentials); never agent-authored.** |
| R-D5 | Rescue build | Confirmed clean per the deny list on 2026-07-06 (scanner PASS, checksum matched served manifest); no rebuild. **Confirmed.** |

---

## Execution log

Steps run one per session, lowest-numbered non-EXECUTED step for the
current repo next. WebFlash steps are tracked in that repo's copy of this
file (created at W1 from this plan of record).

| Step | Repo | Description | Status | PR |
|---|---|---|---|---|
| R1 | esphome-public | Recon + plan of record (this file) | **EXECUTED** | [#797](https://github.com/sense360store/esphome-public/pull/797) |
| Dispatch | esphome-public | Owner runs the dispatch runbook (4 rebuilds); credential gates must pass | **EXECUTED** (2026-07-06: `v1.0.7`, `v1.0.8`, `v1.0.9`, `v1.0.1-led-preview` published with assets + cosign-signed checksums). **Defect:** the release bodies were published with a false "provisioned uniquely per device" changelog claim — see *Release-body correction* below | — |
| R2 | esphome-public | `RECON-UPSTREAM-CRED-CLAIMS-001`: correct false per-device-credential claims in maintained docs/metadata; R-D4 checklist corrected to the shipped unprovisioned posture; owner instructions for release-body correction (below) | **EXECUTED** | this PR |
| Release-body fix | esphome-public | Owner replaces the `## Changelog` bullets of the four release bodies with the corrected wording below (release-note **text only** — no asset, tag, hash, or binary change) | OWNER ACTION — pending | — |
| Bench | hardware | Owner bench-flashes one rebuilt stable; **corrected** R-D4 checklist (unprovisioned-posture tests); owner-authored attestation | OWNER ACTION — pending | — |
| W1 | WebFlash | De-list the five fan previews (R-D1) | **EXECUTED** | WebFlash [#582](https://github.com/sense360store/WebFlash/pull/582) |
| W2 | WebFlash | Clean re-import of the four rebuilt releases; backstop assertions. The R-D4 owner bench attestation this step was to be gated on remains **pending** (see Bench row) | **EXECUTED** | WebFlash [#584](https://github.com/sense360store/WebFlash/pull/584), [#585](https://github.com/sense360store/WebFlash/pull/585), [#586](https://github.com/sense360store/WebFlash/pull/586), [#587](https://github.com/sense360store/WebFlash/pull/587) |
| W3 | WebFlash | Scanner verification of every served binary; resolve advisory DRAFT markers; mark the **automated / WebFlash execution** complete (see completion-scope note below) | **EXECUTED** | WebFlash [#592](https://github.com/sense360store/WebFlash/pull/592) (completion / correction) |
| Publish | WebFlash | Owner publishes the GitHub Security Advisory + user notice | OWNER ACTION — pending | — |
| Annotate | esphome-public | Owner annotates superseded release notes with the advisory link (R-D3) | OWNER ACTION — pending | — |

**Programme-completion scope.** The "COMPLETE" marker set at W3 covers the
**automated / WebFlash execution only** — the rebuilds, the fan-preview
de-listing, the clean re-import, and the served-binary scanner
verification. It does **not** cover, and must not be read as closing, the
still-open items above: the owner **release-body corrections** (the four
published release bodies still carry the false per-device-credential claim
until the owner applies the wording below), the owner **bench attestation**
(corrected R-D4 checklist; never agent-authored), the owner **advisory
publication** and superseded-release **annotation** (R-D3), and the
separate `SEC-ESP-PROVISIONING-001` follow-up, which remains planned and
**not implemented** — served firmware still ships unprovisioned per
[`docs/security/release-firmware-credential-posture.md`](security/release-firmware-credential-posture.md).

---

## Release-body correction (RECON-UPSTREAM-CRED-CLAIMS-001)

The four rebuilt releases were published on 2026-07-06 with a changelog
line stating "device credentials are now provisioned uniquely per device".
**That claim is false.** The rebuilt binaries ship **unprovisioned** per
[`docs/security/release-firmware-credential-posture.md`](security/release-firmware-credential-posture.md):
no credentials are generated or embedded, the native API is unencrypted,
OTA and the web interface are unauthenticated, and the fallback/setup AP is
open. Per-device provisioning is the planned, **not implemented**
`SEC-ESP-PROVISIONING-001` follow-up.

No repository workflow supports editing an already-published release body
(`create-release.yml` only creates new tags; `release-notes-draft.yml` only
uploads a preview artifact), so this correction is a **manual owner
action**. The W1–W3 WebFlash execution has since landed (see the execution
log above) without copying the false claim; until the bodies are
corrected, any **future** WebFlash import, refresh, or notes sync must
likewise **not** copy changelog / description text from the published
release bodies.

### Owner instructions (per release)

For each of the four releases, on
`https://github.com/sense360store/esphome-public/releases`:

1. Open the release (`v1.0.7`, `v1.0.8`, `v1.0.9`, `v1.0.1-led-preview`)
   and click **Edit release** (pencil icon).
2. In the body, replace **only the two bullets under `## Changelog`** with
   the corrected bullets for that release from the table below. Leave the
   HTML comment preamble and the `## Known Issues` / `## Features` /
   `## Hardware Requirements` sections exactly as they are.
3. Do **not** change the tag, the target commit, the pre-release flag, or
   any attached asset. Click **Update release**.

Equivalent CLI (uses a body file to avoid quoting mistakes; edit only the
Changelog bullets in the downloaded body):
`gh release view <tag> --repo sense360store/esphome-public --json body -q .body > body.md`,
edit `body.md`, then
`gh release edit <tag> --repo sense360store/esphome-public --notes-file body.md`.

### Exact replacement `## Changelog` bullets

**`v1.0.7`** (`Ceiling-POE-VentIQ-RoomIQ`):

```markdown
- Security rebuild: the shared published default credentials (API encryption key, OTA password, web username/password, fallback-AP password) baked into earlier releases were removed. This build ships unprovisioned: no credentials are generated or embedded — the native API is unencrypted, OTA and the web interface are unauthenticated, and the fallback/setup AP is open. Treat a device on this firmware as LAN-trusted only (see docs/security/release-firmware-credential-posture.md).
- Users requiring an encrypted API, an OTA password, web authentication, or a protected fallback AP must currently self-build with unique secrets (copy secrets.example.yaml to a private secrets.yaml). Per-device provisioning (SEC-ESP-PROVISIONING-001) is planned but not implemented.
- Supersedes v1.0.4. No functional changes. A security advisory will follow.
```

**`v1.0.8`** (`Ceiling-POE-RoomIQ`): same first two bullets as `v1.0.7`,
with the final bullet:

```markdown
- Supersedes v1.0.5. No functional changes. A security advisory will follow.
```

**`v1.0.9`** (`Ceiling-POE-AirIQ-RoomIQ`): same first two bullets as
`v1.0.7`, with the final bullet:

```markdown
- Supersedes v1.0.6. No functional changes. A security advisory will follow.
```

**`v1.0.1-led-preview`** (`Ceiling-POE-VentIQ-RoomIQ-LED`): same first two
bullets as `v1.0.7`, with the final bullet:

```markdown
- Supersedes v1.0.0-led-preview. No functional changes. Preview channel: not hardware verified. A security advisory will follow.
```

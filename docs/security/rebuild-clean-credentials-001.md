# REBUILD-CLEAN-CREDENTIALS-001 — re-cut live firmware on the unprovisioned build path

- **Audit basis:** [`SECURITY-AUDIT-2026-06.md`](SECURITY-AUDIT-2026-06.md) finding **H1** (fixed, shared default control credentials compiled into every released binary) and the forward half of **H2** (burned fallback-AP literals). This is the **field-distribution half** of H1: the pipeline was fixed by `SEC-ESP-BUILD-GATES-001` (#779), but the binaries already published and already served by WebFlash were built **before** that fix and still embed the defaults.
- **Posture target:** every rebuilt binary must match [`release-firmware-credential-posture.md`](release-firmware-credential-posture.md) (unprovisioned: unencrypted API, unauthenticated OTA/web, open setup AP; only the two intentionally-public setup-network values remain).
- **Scope of this document:** the re-release **policy**, the exact **tag / version / artifact plan**, the **dispatch runbook**, the **SHA-256 handoff** for the downstream WebFlash re-import, and the explicit handling of the firmware that cannot flow through the sanctioned pipeline.
- **What this PR does NOT do:** it does not cut any release tag, build any `.bin`, change any product YAML behaviour, or modify `config/webflash-builds.json` / `config/product-catalog.json`. The actual rebuilds are a manual owner dispatch (runbook below); this PR records the plan and the coordinates.

## Why a rebuild is needed

`SEC-ESP-BUILD-GATES-001` (#779) stops the release pipeline baking the shared
default `api_encryption_key` / `ota_password` / `web_password` /
`fallback_ap_password` into firmware, and `SEC-ESP-CHECKSUM-SIGNING-001`
(#780) signs the release checksums with keyless cosign. Both are forward
fixes: they govern every **future** release.

The binaries currently live on the WebFlash installer were all published
before those fixes landed (the security work merged 2026-06-10; the live
releases were cut 2026-06-07 through 2026-06-09 and 2026-05/06 for the
previews). They still embed the four shared control credentials. They must be
rebuilt on the post-#779 pipeline and re-released so WebFlash can re-import
clean ones.

## Re-release policy: append-only version bump (chosen)

**Decision: bump the patch version for every affected config and cut a new
tag. Do not re-cut an existing tag.**

Two options were considered:

| Option | Mechanics | Verdict |
|---|---|---|
| **(a) Version bump (CHOSEN)** | Each config gets the next free version and a new tag (e.g. `v1.0.4` clean becomes `v1.0.7`). Old and new releases coexist; nothing published is mutated. | **Chosen.** Append-only and reversible. WebFlash re-pins forward to the new tag + new `expected_sha256`. No published asset is deleted or overwritten. Matches the existing one-config-per-version convention (`v1.0.4`=VentIQ-RoomIQ, `v1.0.5`=RoomIQ, `v1.0.6`=AirIQ-RoomIQ). |
| (b) Re-cut the same tag with clean bytes | Delete/replace the assets on `v1.0.4` / `v1.0.5` / `v1.0.6` / `v1.0.0-led-preview`. | **Rejected.** Replacing published assets is a destructive, in-place mutation that the recommended *immutable releases* setting (audit Item 7, line 9) would forbid; it silently changes the bytes behind a tag WebFlash already pins (`expected_sha256` in `firmware/sources.json`), breaking the pin with no version signal; and it loses the audit trail of what shipped when. |

Rationale in one line: a version bump is **append-only and coordinated** — the
old cred-bearing release stays as the historical record, the new clean release
is a distinct artifact with a distinct hash, and the downstream re-import is an
explicit, reviewable pin change rather than a silent byte swap under a fixed
tag.

## Affected configs and the tag / version / artifact plan

Two groups. **Group A** rebuilds through the sanctioned pipeline in this plan.
**Group B** cannot and is handled by downstream de-listing (see below).

### Group A — rebuilt clean through Release 1 → Create Release → Release 3

These four configs have rows in `config/webflash-builds.json`, so
`firmware-build-release.yml` rebuilds them with the credential posture strip,
the default-credential gate, and cosign signing applied automatically.

| # | config_string | Live tag (cred-bearing) | New tag (clean) | New version | New artifact name | Channel |
|---|---|---|---|---|---|---|
| 1 | `Ceiling-POE-VentIQ-RoomIQ` (Release-One / Bathroom PoE) | `v1.0.4` | `v1.0.7` | `1.0.7` | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.7-stable.bin` | stable |
| 2 | `Ceiling-POE-RoomIQ` (Bedroom) | `v1.0.5` | `v1.0.8` | `1.0.8` | `Sense360-Ceiling-POE-RoomIQ-v1.0.8-stable.bin` | stable |
| 3 | `Ceiling-POE-AirIQ-RoomIQ` (Kitchen) | `v1.0.6` | `v1.0.9` | `1.0.9` | `Sense360-Ceiling-POE-AirIQ-RoomIQ-v1.0.9-stable.bin` | stable |
| 4 | `Ceiling-POE-VentIQ-RoomIQ-LED` (LED preview) | `v1.0.0-led-preview` | `v1.0.1-led-preview` | `1.0.1` | `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.1-preview.bin` | preview |

Notes:
- `v1.0.7` / `v1.0.8` / `v1.0.9` are the next free stable numbers above the
  current `v1.0.6`. `v1.0.1-led-preview` is free; the bare `v1.0.1` stable tag
  already exists but is a different tag on a different channel — this exactly
  mirrors the existing `v1.0.0` / `v1.0.0-led-preview` coexistence, and Create
  Release verifies the exact resolved tag is free before cutting it.
- Each stable config keeps its own version and its own tag/release (the
  established convention), so each release body stays per-config and the
  per-config notes generator and asset checks stay correct.
- `Ceiling-POE-RoomIQ-LED` (build-matrix row, `metadata-ready-unpublished`) and
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` (experimental, `metadata-ready-unpublished`)
  are **not** live on the installer and are **not** in scope. FanTRIAC stays
  out per its standing invariant.

### Group B — the 5 fan room-bundle previews (de-listed downstream, not rebuilt here)

Live on the installer from `v1.0.0-preview`, all built pre-#779, all
cred-bearing:

- `Ceiling-POE-VentIQ-FanPWM-RoomIQ`
- `Ceiling-POE-VentIQ-FanDAC-RoomIQ`
- `Ceiling-POE-AirIQ-FanRelay-RoomIQ`
- `Ceiling-POE-AirIQ-FanPWM-RoomIQ`
- `Ceiling-POE-AirIQ-FanDAC-RoomIQ`

These cannot be rebuilt through the sanctioned pipeline: the standing
invariant keeps fan rows **out** of `config/webflash-builds.json` (the
fan-token guardrail), `firmware-build-release.yml` builds only what that file
declares, `create-release.yml` has no fan configs in its choice list, and the
dedicated `preview-fan-publish.yml` workflow was retired.

**Decision: de-list, do not rebuild.** The downstream WebFlash re-import
(`WF-REIMPORT-CLEAN-001`) drops these five Advanced-install-only previews from
the installer rather than re-importing cred-bearing binaries. This removes the
cred-bearing fan firmware from distribution, keeps the upstream fan-token
guardrail intact, and reintroduces no retired machinery. The previews are
never stable, recommended, default, or buyable, so de-listing has no customer
baseline impact. They can return later via a dedicated, gated clean rebuild if
the owner decides to restore a fan-publish path.

## Guarantees by construction (Group A)

`firmware-build-release.yml` runs the same posture and gate steps on **every**
release event regardless of channel, so a Group A rebuild either produces a
clean, signed binary or fails the release before anything is published:

1. **Posture strip (before compile):** `scripts/apply_release_secret_posture.py`
   removes `api.encryption`, the OTA password, the `web_server` auth block, and
   the fallback-AP password in the build workspace (fail-closed if a base
   package no longer has the expected shape). The release lane provisions only
   the two intentionally-public setup-network values, so any surviving
   `!secret` reference fails the compile rather than baking a value.
2. **Per-product gate (after compile):** `scripts/check_firmware_default_credentials.py "$FIRMWARE_PATH"`
   scans the compiled binary against the default / placeholder / burned
   credential denylist (including the two H2 fallback-AP literals).
3. **Release-set gate (before attach):** `scripts/check_firmware_default_credentials.py --dir all-firmware`
   re-scans the full downloaded artifact set; fails closed on an empty set.
4. **Signing (after the gate, before upload):** keyless cosign signs
   `checksums-sha256.txt`, self-verifies the certificate identity, and
   publishes `.sig` + `.pem`; any signing failure fails the release before the
   upload step, so an unsigned checksums file is never published.

Therefore every rebuilt Group A binary is, by construction, free of the
denylisted default credentials, cosign-signed at the checksums level, and a
match for the unprovisioned posture document — or the release does not publish.

## No product YAML functional change

The rebuild changes no `packages/` or `products/` behaviour. The only edits in
the release path are the version-and-artifact-name bump performed by Release 1
(`scripts/bump_release_version.py` rewrites only `version` and the
version-bearing `artifact_name` in `config/product-catalog.json` and
`config/webflash-builds.json`, nothing else), and the workspace-only,
never-committed posture patch. The compiled image's only intended delta versus
the current live binary is the **absence of the baked default credentials**.

## Dispatch runbook (manual owner action)

Prerequisite: the auto-trigger from a published release to Release 3 requires a
`RELEASE_PAT` repo/org secret (a release created with the default
`GITHUB_TOKEN` does not fire downstream workflows because of GitHub's recursion
guard). Confirm `RELEASE_PAT` is present before starting, or be ready to
re-publish the release to fire Release 3.

For **each** Group A config, in order:

1. **Release 1: Bump Version** (`workflow_dispatch`)
   - `config_string` = the config (e.g. `Ceiling-POE-VentIQ-RoomIQ`)
   - `version` = the new version (e.g. `1.0.7`)
   - This opens a PR that bumps `version` + `artifact_name` in both catalog
     files. **Review and merge it** before step 2 (`plan_release.py` fails
     closed if the catalog version does not yet equal the requested version).
2. **Release: Create GitHub Release** (`workflow_dispatch`)
   - `config_string` = the same config
   - `version` = the same new version
   - `tag_suffix` = blank for the three stable configs; `led-preview` for
     `Ceiling-POE-VentIQ-RoomIQ-LED`
   - `changelog` = a security-rebuild line, e.g.
     `Security rebuild on the unprovisioned build path; removes the previously baked default API, OTA, web, and fallback credentials; no functional firmware change from v<old>.`
   - Run with `dry_run=true` first; review the planned tag and generated notes;
     then re-run with `dry_run=false` to create the release.
3. **Release 3: Build & Release** fires automatically on the published release
   and performs the posture strip → compile → per-product gate → rename →
   matrix-name assertion → release-set gate → cosign signing → attach
   (`.bin` + `checksums-sha256.txt` + `.sig` + `.pem` + `checksums-md5.txt` +
   `manifest.json`).

Suggested per-config dispatch inputs:

| config_string | Release 1 version | Create Release version | tag_suffix | Resulting tag |
|---|---|---|---|---|
| `Ceiling-POE-VentIQ-RoomIQ` | `1.0.7` | `1.0.7` | _(blank)_ | `v1.0.7` |
| `Ceiling-POE-RoomIQ` | `1.0.8` | `1.0.8` | _(blank)_ | `v1.0.8` |
| `Ceiling-POE-AirIQ-RoomIQ` | `1.0.9` | `1.0.9` | _(blank)_ | `v1.0.9` |
| `Ceiling-POE-VentIQ-RoomIQ-LED` | `1.0.1` | `1.0.1` | `led-preview` | `v1.0.1-led-preview` |

## SHA-256 handoff for the WebFlash re-import (WF-REIMPORT-CLEAN-001)

The new `expected_sha256` values are deterministic outputs of the Release 3
build and **cannot be produced in advance** — they exist only after each
release is cut. Once Release 3 finishes for a tag, read the hashes from the
published, cosign-verifiable `checksums-sha256.txt` (or `manifest.json`) and
hand them to the WebFlash re-import.

Fetch command per tag (example for `v1.0.7`):

```bash
gh release download v1.0.7 --repo sense360store/esphome-public \
  --pattern 'checksums-sha256.txt' --pattern 'checksums-sha256.txt.sig' \
  --pattern 'checksums-sha256.txt.pem'
# verify WHO signed (see docs/security/checksums-verification.md), then read the hash:
grep 'Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.7-stable.bin' checksums-sha256.txt
```

Handoff table (WebFlash updates `firmware/sources.json`: `release_tag`,
`asset_name`, `expected_sha256` — and drops the five Group B fan sources):

| WebFlash config_string | New release_tag | New asset_name | New expected_sha256 |
|---|---|---|---|
| `Ceiling-POE-VentIQ-RoomIQ` | `v1.0.7` | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.7-stable.bin` | _TBD — read from published `checksums-sha256.txt`_ |
| `Ceiling-POE-RoomIQ` | `v1.0.8` | `Sense360-Ceiling-POE-RoomIQ-v1.0.8-stable.bin` | _TBD — read from published `checksums-sha256.txt`_ |
| `Ceiling-POE-AirIQ-RoomIQ` | `v1.0.9` | `Sense360-Ceiling-POE-AirIQ-RoomIQ-v1.0.9-stable.bin` | _TBD — read from published `checksums-sha256.txt`_ |
| `Ceiling-POE-VentIQ-RoomIQ-LED` | `v1.0.1-led-preview` | `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.1-preview.bin` | _TBD — read from published `checksums-sha256.txt`_ |
| `Ceiling-POE-VentIQ-FanPWM-RoomIQ` | _(none — de-listed)_ | _(remove source)_ | _(remove)_ |
| `Ceiling-POE-VentIQ-FanDAC-RoomIQ` | _(none — de-listed)_ | _(remove source)_ | _(remove)_ |
| `Ceiling-POE-AirIQ-FanRelay-RoomIQ` | _(none — de-listed)_ | _(remove source)_ | _(remove)_ |
| `Ceiling-POE-AirIQ-FanPWM-RoomIQ` | _(none — de-listed)_ | _(remove source)_ | _(remove)_ |
| `Ceiling-POE-AirIQ-FanDAC-RoomIQ` | _(none — de-listed)_ | _(remove source)_ | _(remove)_ |

## Coordination and sequencing

1. This plan PR merges (review branch; human merges; target base `main`).
2. The owner runs the dispatch runbook for the four Group A configs, producing
   four new clean, signed releases.
3. The new hashes are filled into the handoff table above (or carried straight
   into the WebFlash PR).
4. WebFlash `WF-REIMPORT-CLEAN-001` re-imports the four clean Group A artifacts
   (new tag + new `expected_sha256`) and de-lists the five Group B fan
   previews, then regenerates and deploys its manifest.

**Until step 4 deploys, the live installer still serves the old cred-bearing
binaries.** Cutting the clean upstream releases (steps 2-3) does not by itself
change what WebFlash distributes; the distribution half closes only when the
WebFlash re-import lands.

## Not addressed here (unchanged)

- **H2 history dimension.** The burned fallback-AP literals remain world-readable
  in public git history; rebuilding firmware does not un-disclose them. Treat
  already-shipped units as compromised on those credentials and re-flash. This
  rebuild removes them from newly distributed binaries only.
- **Per-device provisioning.** Rebuilt binaries are unprovisioned, not
  per-device secured. Real per-device secrets remain the separate
  `SEC-ESP-PROVISIONING-001` follow-up; the self-build path with a private
  `secrets.yaml` stays the fully-secured option.
- **Rescue firmware.** WebFlash's in-tree Rescue build is not produced by this
  repo and is out of scope here; whether it carries any default credential is a
  WebFlash-side check, flagged to the re-import PR.
- **No hardware / bench / compliance / safety claim** is made by this rebuild.
  The only binary delta is the absence of the baked default credentials.

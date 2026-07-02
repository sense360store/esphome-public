# Upcoming PR

This file is the source-of-truth queue for the next planned change set in the
esphome-public repository. The **Next queue (actionable)** section is the only
genuinely open work. Everything below it is standing invariants, a condensed
record of the now-complete preview-release program, and a one-line history of
merged PRs.

> Note: this file was condensed in `DOCS-CLEANUP-001`. The long per-PR write-ups
> that used to live here were collapsed into the summaries below. Nothing was
> marked done that was not already merged; the merged PRs and the docs / tests
> they added remain in the tree as the authoritative detail.

---

## Next queue (actionable)

Two items are genuinely open — the per-device provisioning follow-up opened
by `SEC-ESP-BUILD-GATES-001`, and `REBUILD-CLEAN-CREDENTIALS-001` (the
field-distribution half of audit H1: re-cut the live cred-bearing releases
clean on the post-#779 pipeline). The checksum-signing finding
(`SEC-ESP-CHECKSUM-SIGNING-001`, security.md §3 / audit M1) is **implemented
on its review branch** (recorded in the closed items below the queue). The
FanTRIAC bench gate (`PACKAGE-TRIAC-001`) is
**complete and operator-attested**, and the FanTRIAC commissioning PR
(`TRIAC-COMMISSIONING-001`) is **implemented on its human-review branch** (both
recorded in the closed items below the queue and in the condensed history);
neither is open work any more. `COMPLIANCE-001` itself is **CLOSED — resolved
by posture** per
[`docs/decisions/COMPLIANCE-001-RESOLUTION-001.md`](docs/decisions/COMPLIANCE-001-RESOLUTION-001.md)
(see the closed item recorded below the queue).

1. **`SEC-ESP-PROVISIONING-001` (follow-up opened by `SEC-ESP-BUILD-GATES-001`).**
   Design and implement a real per-device provisioning flow for released
   firmware: set unique `api_encryption_key` / `ota_password` /
   `fallback_ap_password` / `web_password` on the user's own install
   (first-boot / WebFlash-assisted / Improv-extension — to be designed; no
   such flow exists in the tree today, and Improv-style provisioning covers
   WiFi only). Until this lands, released binaries ship UNPROVISIONED
   (unencrypted API, unauthenticated OTA/web, open setup AP) per
   [`docs/security/release-firmware-credential-posture.md`](docs/security/release-firmware-credential-posture.md);
   the self-build path with a private `secrets.yaml` remains the fully
   secured option. Must not weaken the `SEC-ESP-BUILD-GATES-001` denylist
   gate, which stays the permanent backstop regardless of mechanism.

2. **`REBUILD-CLEAN-CREDENTIALS-001` (field-distribution half of audit H1).**
   `SEC-ESP-BUILD-GATES-001` (#779) fixed the pipeline forward, but the
   binaries already published and already served by the WebFlash installer
   were built before #779 and still embed the four shared control
   credentials. The plan PR (`release/rebuild-clean-credentials-001`, review
   branch, human merges, target base `main`) stages the re-release: policy is
   an **append-only version bump** (never re-cut a tag — that would mutate a
   published asset and silently break WebFlash's pinned `expected_sha256`).
   The four pipeline-eligible configs are re-cut clean on the post-#779
   pipeline (which applies the posture strip + default-credential gate +
   cosign automatically): `Ceiling-POE-VentIQ-RoomIQ` → `v1.0.7`,
   `Ceiling-POE-RoomIQ` → `v1.0.8`, `Ceiling-POE-AirIQ-RoomIQ` → `v1.0.9`,
   `Ceiling-POE-VentIQ-RoomIQ-LED` → `v1.0.1-led-preview`. The five fan
   room-bundle previews (`Ceiling-POE-VentIQ-FanPWM-RoomIQ`,
   `Ceiling-POE-VentIQ-FanDAC-RoomIQ`, `Ceiling-POE-AirIQ-FanRelay-RoomIQ`,
   `Ceiling-POE-AirIQ-FanPWM-RoomIQ`, `Ceiling-POE-AirIQ-FanDAC-RoomIQ`) are
   **de-listed downstream**, not rebuilt — the fan-token guardrail keeps them
   off `config/webflash-builds.json`, so they cannot enter the
   declaration-driven matrix. The plan PR cuts no tag, builds no `.bin`, and
   changes no product YAML, `config/webflash-builds.json`, or
   `config/product-catalog.json`; the actual rebuild is the manual owner
   dispatch in the runbook
   ([`docs/security/rebuild-clean-credentials-001.md`](docs/security/rebuild-clean-credentials-001.md)).
   The distribution half closes only once those clean releases are cut **and**
   the paired WebFlash re-import (`WF-REIMPORT-CLEAN-001`, below) re-pins to
   the new tags + hashes and de-lists the fan previews; until then the live
   installer still serves the old cred-bearing binaries. Touches no FanTRIAC
   posture, no `release_one_required_configs`, no kit, and makes no
   hardware / bench / compliance claim.

The remaining security-audit item, finding #6 (`check-yaml --unsafe` in
pre-commit), is **accepted** — no action queued.

**Closed by resolution (no longer queue items):**

* **`SEC-ESP-CHECKSUM-SIGNING-001` — IMPLEMENTED (review branch, human
  merges; closes `SECURITY-AUDIT-2026-06` M1 / security.md §3, signing
  half).** The release job of
  [`firmware-build-release.yml`](.github/workflows/firmware-build-release.yml)
  now signs `checksums-sha256.txt` with **keyless cosign**
  (`sigstore/cosign-installer` SHA-pinned at v3.9.2, cosign CLI pinned at
  v2.6.3; `cosign sign-blob --yes` via the job's GitHub OIDC identity →
  Fulcio short-lived certificate + Rekor transparency-log entry) and
  publishes `checksums-sha256.txt.sig` + `checksums-sha256.txt.pem` as
  release assets alongside the checksums file. Ordering enforced in-job:
  the `SEC-ESP-BUILD-GATES-001` default-credential gate passes → checksums
  generate → cosign signs and self-verifies with the exact consumer recipe
  (pinning certificate identity
  `https://github.com/sense360store/esphome-public/.github/workflows/firmware-build-release.yml@refs/tags/<TAG>`
  and issuer `https://token.actions.githubusercontent.com`) → all assets
  upload (`fail_on_unmatched_files` backstops the `.sig`/`.pem`); any
  signing failure fails the release before upload, so an unsigned
  checksums file is never published. `id-token: write` is granted to the
  `release` job **only** (the repo's single OIDC grant; allowlisted with
  reason in
  [`tests/test_workflow_permissions.py`](tests/test_workflow_permissions.py),
  which also gained the cosign-installer SHA-pin inventory row). Consumer
  verification recipe documented at
  [`docs/security/checksums-verification.md`](docs/security/checksums-verification.md);
  audit M1 marked remediated (signing half) in
  [`docs/security/SECURITY-AUDIT-2026-06.md`](docs/security/SECURITY-AUDIT-2026-06.md).
  Platform-level asset mutability stays with the owner checklist (audit
  Item 7 line 9: immutable releases + artifact attestations).
  `checksums-md5.txt` stays legacy-compatibility-only and unsigned. In
  place **before** the FanTRIAC experimental release cut, so that release
  ships signed from day one. CI-validated by yamllint + the
  workflow-permissions guard suite; the signing path itself runs only on a
  real release event (not exercisable per-PR).

* **`SEC-ESP-BUILD-GATES-001` — IMPLEMENTED (review branch, human merges;
  widened to close `SECURITY-AUDIT-2026-06` H1 + the forward half of H2).**
  Originally queued as security.md findings #4 + #5; widened after
  [`docs/security/SECURITY-AUDIT-2026-06.md`](docs/security/SECURITY-AUDIT-2026-06.md)
  confirmed the five fixed credentials actually ship in released binaries.
  Delivered: (1) the permanent artifact-level default-credential gate
  ([`scripts/check_firmware_default_credentials.py`](scripts/check_firmware_default_credentials.py))
  runs in `firmware-build-release.yml` after each product compile and again
  over the full downloaded artifact set before release attachment — it
  denylists the placeholder `api_encryption_key` (base64 literal AND decoded
  32-byte material), the shipped + CI-lane `ota_password` / `web_password` /
  `fallback_ap_password` defaults, the two burned historical fallback-AP
  literals (the H2 forward half), and the CI-lane test WiFi values, failing
  closed on an empty artifact set; the two intentionally-public
  setup-network values are the only documented exclusion. (2) Released
  builds no longer bake shared secrets: the workflow's fixed secrets-content
  override is reduced to the setup-network pair, and
  [`scripts/apply_release_secret_posture.py`](scripts/apply_release_secret_posture.py)
  strips `api.encryption`, the OTA password, the `web_server` auth block,
  and the fallback-AP password in the release workspace (fail-closed,
  one-shot, never committed) — fresh-flash devices are unprovisioned rather
  than falsely secured (posture + first-boot doc:
  [`docs/security/release-firmware-credential-posture.md`](docs/security/release-firmware-credential-posture.md)).
  (3) `manifest.json` is JSON-validated before upload (security.md #5 /
  audit L3). Unit tests
  ([`tests/test_check_firmware_default_credentials.py`](tests/test_check_firmware_default_credentials.py),
  [`tests/test_apply_release_secret_posture.py`](tests/test_apply_release_secret_posture.py))
  run per-PR in `validate.yml`. No product YAML functional behaviour changed;
  self-builders still compile fully secured firmware from their own
  `secrets.yaml`. H2's history dimension stays OPEN (the burned literals
  remain world-readable in public git history; rotate already-shipped
  units). Follow-up opened: `SEC-ESP-PROVISIONING-001` (queued above). This
  gate precedes any FanTRIAC experimental release cut.

* **`PACKAGE-TRIAC-001` — COMPLETE and operator-attested.** The FanTRIAC
  operator bench protocol is finished and the signed operator attestation is
  committed to
  [`docs/package-triac-001-operator-bench-proof.md`](docs/package-triac-001-operator-bench-proof.md):
  Steps A–F PASS on the real Manrose fan-motor load (2026-06-08), the
  full-composition re-confirm PASS via closure path (a) (2026-06-10), and the
  six-cell operator attestation table is filled. This satisfied the
  experimental-lane entry preconditions of `COMPLIANCE-001-RESOLUTION-001`.

* **`TRIAC-COMMISSIONING-001` — IMPLEMENTED (human-review branch).** The
  commissioning PR cleared the `PACKAGE-TRIAC-001` half of the FanTRIAC blocker
  (citing the attested proof) and moved `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`
  into the `experimental_lane`
  ([`config/release-channel-policy.json`](config/release-channel-policy.json)).
  It flipped the catalog to `status: preview` / `channel: experimental` /
  `webflash_build_matrix: true`, added the `config/webflash-builds.json` row on
  the new **experimental** build channel (artifact
  `Sense360-Ceiling-POE-VentIQ-FanTRIAC-RoomIQ-v1.0.0-experimental.bin`),
  re-keyed `TRIAC-PUBLISH-ADVANCED-PREVIEW-001` to **executed**, drafted the
  experimental release notes
  ([`docs/release-notes/experimental/ceiling-poe-ventiq-fantriac-roomiq.md`](docs/release-notes/experimental/ceiling-poe-ventiq-fantriac-roomiq.md)),
  and rebaselined the #726-derived publish-gate tests (every never-stable /
  recommended / default / buyable / kit-exposed tooth preserved). It cuts **no
  release tag** (release-eligibility metadata only). It made **no `packages/`
  and no canonical / bundle product-YAML change**; the compile target stays the
  unchanged canonical product YAML. The branch is **human-review only — do NOT
  auto-merge**, and the reviewer confirms the two prerequisite slices (the SSOT
  refactor and the WebFlash add-source checksum guard) before merge. Downstream
  one-click WebFlash import `WF-IMPORT-TRIAC-001` is now **unblocked pending the
  experimental release cut** (and admits the experimental channel together with
  its warning UI in one reviewed WebFlash-repo PR).

* **`COMPLIANCE-001` — CLOSED, resolved by posture
  (`COMPLIANCE-001-RESOLUTION-001`, 2026-06-09).** The owner decision record
  [`docs/decisions/COMPLIANCE-001-RESOLUTION-001.md`](docs/decisions/COMPLIANCE-001-RESOLUTION-001.md)
  closed the mains-voltage UK/EU assessment gate by market posture: the
  mains-touching boards (S360-320 TRIAC, S360-310 Fan Relay, S360-400 240v
  PSU) are **never placed on the market by Sense360** (not sold assembled,
  not a kit of parts, not a populated PCB, never physically bundled); design
  files and firmware publish open-source under CERN-OHL-P for self-builders
  of their own devices at their own risk. Kits may be designated
  **expansion-ready** under the record's two binding conditions. An
  **experimental publish lane** is defined as policy metadata in
  [`config/release-channel-policy.json`](config/release-channel-policy.json)
  (no target assigned). **Reopen trigger:** any future market-placement act
  reopens `COMPLIANCE-001` and requires external safety + EMC assessment
  BEFORE that act (indicative path: pre-compliance scan, then test-house
  safety + EMC). No conformity is claimed; no checklist row of the tracker
  is promoted; no catalogue status, build row, wrapper, release artifact, or
  WebFlash surface changed.

---

## Standing invariants (do not regress)

These hold across every PR; the preview-release program below did **not** change
any of them.

* **Production stable Release-One is the customer baseline.** Config string
  `Ceiling-POE-VentIQ-RoomIQ` (current stable version per
  [`config/webflash-builds.json`](config/webflash-builds.json); v1.0.4 as of
  2026-06-07), launch shop SKU **`S360-KIT-BATH-P`**. Simple install resolves
  to the stable Bathroom PoE build only. The Bedroom (`Ceiling-POE-RoomIQ`,
  stable v1.0.5, 2026-06-08) and Kitchen (`Ceiling-POE-AirIQ-RoomIQ`, stable
  v1.0.6, 2026-06-09) bundles were later promoted to stable under owner
  risk-acceptance waivers (`HW-S360-410-WAIVER-2026-06`,
  `HW-AIRIQ-WAIVER-2026-06`) — owner waivers, not hardware verification — and
  their candidate / room bundles stay **hidden / not buyable / never the
  customer default**.
* **FanTRIAC is commissioned to the experimental self-build mains lane —
  never stable / recommended / default / buyable / kit-exposed.**
  `TRIAC-COMMISSIONING-001` (human-review only) cleared the `PACKAGE-TRIAC-001`
  half of the former blocker (operator-attested bench proof
  [`docs/package-triac-001-operator-bench-proof.md`](docs/package-triac-001-operator-bench-proof.md)),
  with `COMPLIANCE-001` closed by market posture
  ([`docs/decisions/COMPLIANCE-001-RESOLUTION-001.md`](docs/decisions/COMPLIANCE-001-RESOLUTION-001.md)),
  and moved `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` into the `experimental_lane`.
  It is now `status: preview` / `channel: experimental` /
  `webflash_build_matrix: true` with a `config/webflash-builds.json` row on the
  new **experimental** build channel (artifact
  `Sense360-Ceiling-POE-VentIQ-FanTRIAC-RoomIQ-v1.0.0-experimental.bin`). The
  permanent teeth stand: **never stable, never recommended, never a customer
  default, never buyable, never in any kit or kit picker, never in
  `release_one_required_configs`** — the S360-320 is a self-build, open-source
  (CERN-OHL-P) board Sense360 **never places on the market**. This commissioning
  cuts **no release tag** (release-eligibility metadata only) and makes **no
  electrical-safety / EMC / compliance claim**. `TRIAC-PUBLISH-ADVANCED-PREVIEW-001`
  is now **executed** by this commissioning; downstream one-click WebFlash import
  (`WF-IMPORT-TRIAC-001`) stays gated, unblocked only once the experimental
  release is cut. Any further FanTRIAC blocker / status change is **human-review
  only — do NOT auto-merge.**
* **Fans are preview-only.** FanRelay / FanPWM / FanDAC (and the five
  full-composition fan room-bundle configs) are `manual-preview`, published only
  on the shared `v1.0.0-preview` prerelease, and are preview WebFlash-import
  eligible (Advanced-install-only, acknowledgement-gated). **No fan row is added
  to `config/webflash-builds.json`** — the fan-token guardrail stays intact.
  Stable / full release stays blocked (`RELEASE-RELAY-001` / `RELEASE-PWM-001` /
  `RELEASE-DAC-001`); catalog `status` stays `hardware-pending`.
* **FanDAC I²C address requirement is pending bench.** GP8403 IC1 `0x58` /
  IC2 `0x5A`; `0x59` is forbidden when VentIQ/AirIQ is present (SGP41 collision).
  The DIP-switch mapping is compile-time only — `FANDAC-I2C-ADDR-001` stays
  **PENDING** (no FanDAC hardware verification claimed). See
  [`docs/hardware/fandac-i2c-address-verification.md`](docs/hardware/fandac-i2c-address-verification.md).
* **No false proof.** Preview / compile work is **firmware-build proof only** —
  no hardware / bench / compliance / safety / commercial-availability proof is
  claimed for any preview artifact.

---

## WebFlash-owned follow-ups (tracked in the WebFlash repo, not here)

The upstream work that *enables* these imports is done (preview artifacts are
published on `v1.0.0-preview` and marked preview WebFlash-import eligible). The
imports themselves live in the [`sense360store/WebFlash`](https://github.com/sense360store/WebFlash)
repo and are **queued separately** in **its** queue — they are not open work in
this repo and add no `config/webflash-builds.json` row here. Each fan-driver
committed WebFlash import is its own gated WebFlash-repo slice.

#### WF-REIMPORT-CLEAN-001 — re-import the clean rebuilt firmware + de-list the fan previews (queued — WebFlash repo)

The downstream half of `REBUILD-CLEAN-CREDENTIALS-001` (queue item 2 above).
Once the four clean releases are cut (`v1.0.7` / `v1.0.8` / `v1.0.9` /
`v1.0.1-led-preview`), WebFlash re-pins `firmware/sources.json` to the new
tags, asset names, and `expected_sha256` values (handoff table in
[`docs/security/rebuild-clean-credentials-001.md`](docs/security/rebuild-clean-credentials-001.md)),
**de-lists** the five cred-bearing fan room-bundle previews (`FanRelay` /
`FanPWM` / `FanDAC` × `VentIQ` / `AirIQ` on `v1.0.0-preview`), regenerates its
manifest + sidecars, and deploys. This is the step that actually removes the
default-credential firmware from the live installer; until it deploys, the
installer still serves the old binaries. WebFlash-repo slice — no change in
this repo. Should also verify the in-tree Rescue firmware carries no default
control credential.

#### WF-PREVIEW-IMPORT-FIRST-BATCH-001 — first batch of room-bundle preview artifacts (queued — WebFlash repo)

The first batch of published room-bundle preview artifacts. WebFlash-repo
follow-up only; no change in this repo.

#### WEBFLASH-RELAY-001 — import the FanRelay manual-preview artifact (queued — WebFlash repo)

Imported by `WF-IMPORT-RELAY-001`, behind the WebFlash fan-warning
acknowledgement UX. Not open work here.

#### WEBFLASH-PWM-001 — import the FanPWM manual-preview artifact (queued — WebFlash repo)

Imported by `WF-IMPORT-PWM-001`, behind the WebFlash fan-warning
acknowledgement UX. Not open work here.

#### WEBFLASH-DAC-001 — import the FanDAC manual-preview artifact (queued — WebFlash repo)

Imported by `WF-IMPORT-DAC-001`, behind the WebFlash fan-warning
acknowledgement UX. Not open work here.

#### WF-IMPORT-FAN-BUNDLES-001 — import the five full-composition fan room-bundle previews (queued — WebFlash repo)

The five full-composition fan room-bundle preview imports, behind the same
acknowledgement / warning UX. Not open work here.

**FanTRIAC** is now commissioned to the **experimental self-build mains lane**
(`TRIAC-COMMISSIONING-001`, human-review): a `config/webflash-builds.json` row
on the **experimental** channel lets the esphome-public release matrix build the
`.bin` on a `v1.0.0-experimental` tag. It is **not** one-click WebFlash-import
eligible — downstream import is the separate `WF-IMPORT-TRIAC-001` slice, which
admits the experimental channel together with its advanced warning UI in one
reviewed WebFlash-repo PR, unblocked only once the experimental release is cut.
The standalone manual-preview fan drivers (FanRelay / FanPWM / FanDAC) stay off
`config/webflash-builds.json` (the fan-token guardrail holds for them).
FanTRIAC stays **never stable / recommended / default / buyable / kit-exposed**;
the S360-320 is a self-build CERN-OHL-P board Sense360 never places on the
market, and the commissioning makes no electrical-safety / EMC / compliance
claim.

Upstream preview-import eligibility and presence on the shared `v1.0.0-preview`
release do **not** imply a committed WebFlash build row, Simple-install exposure,
stable status, recommendation, default selection, or commercial availability.

---

## Preview-release program — DONE (condensed)

The preview-release program is complete. The shared `v1.0.0-preview` prerelease
now hosts the room-bundle previews, the single-driver fan manual-preview
artifacts, and the five full-composition fan room-bundle previews. None of this
changed the stable production release or the invariants above.

* **Policy + targets + releasable metadata (#686 / #687 / #688).** Opened
  **preview** eligibility to every buildable product (`config/release-channel-policy.json`),
  enumerated every buildable product as a concrete preview / advanced-preview
  target (`config/preview-release-targets.json`), and made fans `manual-preview`
  / FanTRIAC `advanced-manual-preview`. Lack of hardware proof blocks **stable
  only**; `buildability` is the only preview blocker.
* **Metadata dry-runs + build fixes + repo audit (`RELEASE-PREVIEW-BUILD-DRYRUN-001`
  / `-002`, #691, #692).** Recorded per-target metadata dry-runs for all 9
  targets (compile pending an ESPHome environment, never faked), authored the
  three previously missing preview product YAMLs, and audited
  `components/` + `products/` (both ACTIVE / KEEP).
* **Hosted compile dry-run GREEN (#694 lane, #695 results).** Run
  [`26821900127`](https://github.com/sense360store/esphome-public/actions/runs/26821900127)
  (2026-06-02, ESPHome 2026.4.5) compiled the seven preview / manual-preview
  targets **PASS** and excluded FanTRIAC (`HW-005`). The three webflash previews
  flipped `compile_validation_status` to `validated-full-compile`. Logs only.
* **Room-bundle preview publish (#696 wrappers, #698 build rows, #699 notes,
  #700 plan, publish run).** Authored the three `products/webflash` wrappers, cut
  the reviewed preview build rows (`config/webflash-builds.json` ledger 2 → 5),
  generated + validated release-note drafts, planned the publish, and the publish
  run ([`26847702410`](https://github.com/sense360store/esphome-public/actions/runs/26847702410))
  attached **four** room-bundle preview `.bin`
  (`Ceiling-POE-AirIQ-RoomIQ`, `Ceiling-POE-RoomIQ`, `Ceiling-POE-RoomIQ-LED`,
  `Ceiling-POE-VentIQ-RoomIQ-LED`) to `v1.0.0-preview`.
* **Single-driver fan manual-preview publish (#703, #708, #709, #710, #711).**
  Added the fan / TRIAC build-row ledger + drafts, planned / added / ran the
  manual-preview fan publish workflow (run
  [`26878032103`](https://github.com/sense360store/esphome-public/actions/runs/26878032103))
  attaching FanRelay / FanPWM / FanDAC manual-preview `.bin` to the **shared**
  `v1.0.0-preview` release, hardened the tag guard, regenerated the combined
  release body, and marked the three fans preview WebFlash-import eligible.
* **Full-composition fan room bundles (#713, #716, #717, #718, #719, #720).**
  Built the five full-composition Bathroom / Kitchen fan room-bundle preview
  configs (`Ceiling-POE-VentIQ-FanPWM-RoomIQ`, `Ceiling-POE-VentIQ-FanDAC-RoomIQ`,
  `Ceiling-POE-AirIQ-FanRelay-RoomIQ`, `Ceiling-POE-AirIQ-FanPWM-RoomIQ`,
  `Ceiling-POE-AirIQ-FanDAC-RoomIQ`), recorded hosted full-compile proof (run
  [`26913592989`](https://github.com/sense360store/esphome-public/actions/runs/26913592989)),
  planned / added / ran the publish workflow (run
  [`26947595936`](https://github.com/sense360store/esphome-public/actions/runs/26947595936))
  attaching the five `.bin` to `v1.0.0-preview`, and marked them preview
  WebFlash-import eligible. The two FanDAC bundles built with the `0x5A` IC2
  override (compile-time only — `FANDAC-I2C-ADDR-001` stays PENDING). TRIAC stayed
  excluded throughout (`HW-005`).

---

## Completed / merged (one-line history)

Newest first. Full detail lives in the referenced docs / tests and the merged
PRs.

* **`DEV-HARNESS-001`** (`claude/dev-harness-esphome-3wt8hf`, 2026-07-02):
  bench dev harness so the YAML flashed on the bench is the literal repo
  source on a feature branch — `dev/` (device template targeting a
  `products/` entry point via remote git packages with `refresh: 0s`, empty
  scratch overlay, placeholder secrets template), `docs/DEV_WORKFLOW.md`
  (branch → dashboard device → USB-then-OTA → push → Install loop, plus the
  local-clone variant), gitignore rules for bench-local files, and the
  fail-closed CI guard `scripts/check_dev_harness_guard.py` in
  `validate.yml` (overlay must stay comments-only; no `config/*.json`
  declaration may reference `dev/`). No release / publish logic touched; no
  `config/webflash-builds.json` change; nothing under `dev/` is
  release-eligible.
* **`CLAUDE-MD-LEAN-001`** (`claude/claude-md-lean-restructure-kd93z5`,
  2026-07-02, human-review): made `CLAUDE.md` lean and drift-proof — replaced
  the *Standing gates* verbatim blockquote snapshot of this file's standing
  invariants (a drift liability; the file itself says `UPCOMING_PR.md` wins
  on drift, and the `PACKAGE-TRIAC-001` queue-item quote had already drifted)
  with one-line operative summaries per gate, each linking to *Standing
  invariants (do not regress)* here as the live authoritative text. Content-
  loss audit first confirmed every snapshot fact already lives here or in
  `docs/`; the three travel rules (FanTRIAC human-review only / never
  auto-merge, attestations never machine-written, ESP-007 declaration-driven
  release matrix — never a broad `products/` scan) stay in `CLAUDE.md` as
  short operative statements. Added `.github/CODEOWNERS` (`/CLAUDE.md`,
  `/UPCOMING_PR.md`, `/.github/` → `@sense360store`). Docs plus one additive
  governance file only — no code, config, workflow-logic, firmware, or test
  change; no gate's status, blocker, channel, or eligibility meaning changed.
* **`TRIAC-COMMISSIONING-001`** (`release/triac-commissioning-001`, 2026-06-10,
  human-review only — do NOT auto-merge): cleared the `PACKAGE-TRIAC-001` half
  of the FanTRIAC blocker (citing the operator-attested proof) and moved
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` into the `experimental_lane` — catalog
  `status: preview` / `channel: experimental` / `webflash_build_matrix: true`,
  a `config/webflash-builds.json` row on the new **experimental** build channel
  (`Sense360-…-FanTRIAC-RoomIQ-v1.0.0-experimental.bin`), `experimental` added
  to `config/webflash-compatibility.json` allowed_channels and to
  `scripts/derive_release_version_channel.py`, `TRIAC-PUBLISH-ADVANCED-PREVIEW-001`
  re-keyed to **executed**, an experimental release-notes draft, and a
  rebaseline of the #726-derived publish-gate tests (all never-stable /
  recommended / default / buyable / kit-exposed teeth preserved). No release
  tag cut, no `packages/` or canonical / bundle product-YAML change.
  `WF-IMPORT-TRIAC-001` unblocked pending the release cut.
* **`PACKAGE-TRIAC-001-ATTEST-CLOSE`** (#775,
  `bench/package-triac-001-attestation-close`, 2026-06-10, human-review):
  recorded the operator-reported bench-fact corrections — every bench run
  (including the Step F boot/reboot cycles previously dated 2026-06-09) ran
  on 2026-06-08; local logs WERE captured on the bench laptop but are not
  attached to the record (nothing implies they were reviewed or attached;
  the Step F evidence class re-worded accordingly) — and staged the final
  close-out: proof-doc status OPERATOR ATTESTATION RECORDED BELOW, next
  steps pointing solely at the commissioning PR
  (`TRIAC-COMMISSIONING-001`), and the designed-to-fail guard
  `test_attestation_operator_and_signature_cells_filled`, which holds the
  suite red until the operator himself fills the Operator and Signature
  cells (staged EMPTY; presence-only check; no attestation content
  machine-written). Doc + #728 guard test only. Suite at merge: 1726
  passed, 3 skipped, exactly the 1 designed failure.
* **`PACKAGE-TRIAC-001-RECONFIRM-001`** (#774,
  `bench/package-triac-001-reconfirm-close`, 2026-06-10, human-review):
  recorded the operator's closure of the full-composition re-confirm via
  closure path (a) — his explicit statement, 2026-06-10, that "the Step F
  image was the full Ceiling-POE-VentIQ-FanTRIAC-RoomIQ composition." The
  re-confirm row, close-out summary row, status line, and next steps moved to
  PASS / pending-attestation-only; the operator attestation block stays
  intentionally empty for the operator to complete on the branch before
  merge. Proof doc + guard-test rebaseline only (the NOT RECORDED pins moved
  to the recorded closure; blocked posture, never-published sentence, and
  attestation-structure pins untouched). Publish posture unchanged: FanTRIAC
  stays BLOCKED / reference-only pending `TRIAC-COMMISSIONING-001` and the
  `COMPLIANCE-001-RESOLUTION-001` experimental-lane preconditions — never
  stable, recommended, default, buyable, or WebFlash-exposed.
* **`ESP-HYGIENE-001`** (#773, 2026-06-10): repo hygiene — docs and test
  harness only.
  Added the root [`CLAUDE.md`](CLAUDE.md) agent guide (derived from the tree:
  project overview, canonical SKU catalog, repo layout, ESPHome conventions,
  commands, the standing gates quoted from this file's invariants plus the
  human-review-only / attestation / ESP-007 rules, and this file's
  maintenance rule). Downgraded [`docs/release-one.md`](docs/release-one.md)
  from "source of truth" to an explicit historical record of the first
  release, pointing at `config/` as the live catalog (content otherwise
  preserved). Fixed the `tests/test_room_bundle_fan_variants.py` harness
  quirk — the module-level `test_main()` invoking a nested `unittest.main()`
  raised `SystemExit: 1` under plain pytest; removed it (the
  `if __name__ == "__main__"` runner stays; what the tests validate is
  unchanged) so the full suite is green under plain pytest. No `config/`,
  workflow, `packages/`, or `products/` change; no gate, blocker, or queue
  item changed.
* **`PACKAGE-TRIAC-001-CLOSE`** (#771,
  `bench/package-triac-001-step-f-close`, 2026-06-10, human-review): recorded
  the operator-reported Step F results (cold boots / warm reboots / stability
  soak — PASS; evidence class: operator observation, no log capture) and
  marked Steps A–F all PASS on the real Manrose motor load (2026-06-08/09).
  The full-composition re-confirm stays NOT RECORDED (the Step F report did
  not state which image was flashed; parameters alone cannot prove the full
  composition; closes on operator statement or re-flash re-check), and the
  empty attestation block was added for the operator to complete before
  merge. Docs + the `fan_triac.yaml` status comment + the #728 guard-test
  rebaseline only. Publish posture unchanged: FanTRIAC stays BLOCKED /
  reference-only pending `TRIAC-COMMISSIONING-001` and the
  `COMPLIANCE-001-RESOLUTION-001` experimental-lane preconditions — never
  stable, recommended, default, buyable, or WebFlash-exposed.
* **`COMPLIANCE-001-RESOLUTION-001`** (`governance/compliance-001-resolution`,
  2026-06-09, human-review): closed `COMPLIANCE-001` by owner decision on
  market posture (mains-touching boards never placed on the market;
  open-source under CERN-OHL-P; expansion-ready kit rules; explicit reopen
  trigger requiring external safety + EMC assessment before any market
  placement), defined the experimental publish lane as policy metadata
  (`config/release-channel-policy.json` → `experimental_lane`, no target
  assigned), and re-pointed every current-state `COMPLIANCE-001`
  open-gate citation to the resolution record. Docs + policy/config metadata
  only — publish-gate behaviour identical; no catalogue status, build row,
  wrapper, release tag, or WebFlash surface changed. Commissioning PR
  (`TRIAC-COMMISSIONING-001`) queued behind the SSOT refactor and the
  WebFlash add-source checksum guard.
* **CI — remove `preview-fan-publish.yml`** (`ci/remove-preview-fan-publish`,
  2026-06-08): retired the never-run (0 runs) fan-publish workflow, superseded by
  Create Release + Release 3 (which published the live `v1.0.0-preview` fan builds
  on the release event) per the `WORKFLOW-AUDIT-2026-06` resolution. Deleted the
  workflow and its **dedicated-only** machinery — the
  `validate_manual_preview_fan_publish.py` / `validate_room_bundle_fan_publish.py`
  validators, the four `test_preview_fan_publish_*` + three
  `test_room_bundle_fan_publish_*` contract tests, and the six
  `release-preview-fan-publish-*.md` / `room-bundle-fan-publish-*.md` docs — and
  dropped the workflow's `tests/test_workflow_permissions.py` allowlist entry.
  Shared config (`preview-release-targets.json`, `room-bundle-fan-variants.json`,
  `webflash-builds.json`), the `preview-fan-triac-build-rows.json` ledger (kept
  validator/test/doc), the `preview-compile-dryrun.yml` lane, and the live
  `v1.0.0-preview` fan preview product are untouched.
* **#734 — `SEC-ESP-SECRET-GUARD-001`**: untracked `products/secrets.yaml` and
  broadened the secret guard (security finding #2).
* **#733 — `SEC-ESP-FALLBACK-AP-001`**: moved the fallback-AP password to
  `!secret` and dropped the product override (security finding #1).
* **#732 — CI**: added the Release-One Bump Version automation.
* **#731 — CI**: renamed workflows to the role-and-step scheme.
* **#730 — CI**: merged the two fan-publish workflows into `preview-fan-publish.yml`.
* **#729 — CI**: extracted the `setup-esphome-build` composite action.
* **#728 — `PACKAGE-TRIAC-001`**: authored the FanTRIAC operator-bench proof
  container (docs + guard test; **status stays PENDING**, no firmware change).
* **#727 — security audit**: added [`security.md`](security.md) (the six findings
  that seed the SEC-ESP-* queue).
* **#726 — `TRIAC-PUBLISH-GATE-HARDEN-001`**: reframed the FanTRIAC blocker as a
  `PACKAGE-TRIAC-001` + `COMPLIANCE-001` publish gate (not an acknowledgement
  gate); no publish, no `.bin`, no eligibility flip.
* **#725 — `TRIAC-PINMAP-CORRECT-001` buildability follow-up**: dropped
  `fan_control_profile.yaml` so the FanTRIAC composition actually compiles;
  recorded a fresh real compile. Stays `status: blocked`.
* **#724 — `TRIAC-PINMAP-CORRECT-001`**: corrected the FanTRIAC gate/zero-cross
  pins to the schematic-verified `GPIO14`/`GPIO13` mapping; moved the blocker off
  HW-005 to `PACKAGE-TRIAC-001` + `COMPLIANCE-001`. Stays `status: blocked`.
* **#723 — `TRIAC-REBLOCK-PINMAP-001`**: reverted #722's compile-only unblock back
  to `status: blocked`.
* **#721 / #722 — `TRIAC-UNBLOCK-BUILD-001`**: recorded the SX1509-free Core
  respin routing TRIAC to IO13/IO14 and a green local compile (later reconciled by
  #723/#724).
* **#720 — `ROOM-BUNDLE-FAN-WEBFLASH-ELIGIBILITY-001`**: marked the five
  full-composition fan room-bundle previews preview WebFlash-import eligible.
* **#719 — `ROOM-BUNDLE-FAN-PUBLISH-RESULTS-001` (DONE)**: recorded `ROOM-BUNDLE-FAN-PUBLISH-RUN-001` DONE — the successful publish (run `26947595936`) of the five full-composition fan room-bundle previews.
* **#718 — `ROOM-BUNDLE-FAN-PUBLISH-WORKFLOW-001` (DONE)** / **#717 — `ROOM-BUNDLE-FAN-PUBLISH-PLAN-001`**: added and planned the room-bundle fan publish lane.
* **#716 — `ROOM-BUNDLE-FAN-COMPILE-RESULTS-001`**: recorded hosted full-compile
  proof (run `26913592989`) for the five full-composition fan bundles.
* **#713 — `ROOM-BUNDLE-FAN-CONFIGS-001`**: built the five full-composition fan
  room-bundle preview configs (FanDAC IC2 → `0x5A`; `FANDAC-I2C-ADDR-001` PENDING).
* **#711 — `RELEASE-PREVIEW-FAN-WEBFLASH-ELIGIBILITY-001`**: marked the three
  single-driver fan previews preview WebFlash-import eligible.
* **#710 — `RELEASE-PREVIEW-COMBINED-RELEASE-NOTES-001` — DONE (this PR)**: regenerated the combined `v1.0.0-preview` release body at `docs/release-notes/preview/v1.0.0-preview.md` (room + fan previews). TRIAC excluded (`HW-005`).
* **#709 — `RELEASE-PREVIEW-FAN-PUBLISH-TAG-GUARD-001` (DONE)**: confirm-gated non-shared release tags on the fan publish workflow.
* **#708 — `RELEASE-PREVIEW-FAN-SHARED-TAG-001` (DONE)**: adopted the shared `v1.0.0-preview` release for the fan manual-preview artifacts.
* **`RELEASE-PREVIEW-PUBLISH-RUN-001` (DONE)** — recorded by `RELEASE-PREVIEW-PUBLISH-RESULTS-001`; run `26847702410` published the four room-bundle preview artifacts on `v1.0.0-preview`.
* **`RELEASE-PREVIEW-FAN-PUBLISH-RUN-001` (DONE)** — recorded by `RELEASE-PREVIEW-FAN-PUBLISH-RESULTS-001`; run `26878032103` published the FanRelay / FanPWM / FanDAC manual-preview artifacts on `v1.0.0-preview`.
* **#703 / #700 / #699 / #698 / #696 — preview WebFlash chain**: fan / TRIAC build rows (#703), publish plan (#700), release-note drafts (#699), preview build rows (#698; ledger 2 → 5), and the three `products/webflash` wrappers (#696).
* **#695 / #694 — `RELEASE-PREVIEW-COMPILE-RESULTS-001` / `-DRYRUN-001`**: hosted
  compile dry-run GREEN (run `26821900127`); seven preview targets PASS, TRIAC
  excluded.
* **#692 — `REPO-STRUCTURE-AUDIT-001`**: audited `components/` + `products/` (both
  ACTIVE / KEEP).
* **#691 — `RELEASE-PREVIEW-BUILD-FIXES-001`**: authored the three previously
  missing preview product YAMLs.
* **#688 / #687 / #686 — preview policy foundation**: all-buildable releasable
  metadata (#688), the preview target manifest (#687), and the channel-tier policy
  (#686).
* **#685 — `FIRST-RELEASE-DOCS-DRIFT-RECONCILE-001`**: reconciled the
  first-release docs with the live `v1.0.0` stable release.
* **#684 — `FIRST-RELEASE-PUBLISH-READINESS-001`**: assessed first stable release
  publish readiness (already published / no action). Earlier first-release and
  pre-hardware-prep work (`PRE-HW-PREP-*`, `S360-311` / `S360-312` firmware
  design-complete, `SX1509-RECONCILE-001`, `HW-SENSOR-SFA40-CORRECTION-001`,
  `PRODUCT-DEP-CORE-001`, `V1-R4-CREATE-004`, `ROOM-BUNDLE-FAN-VARIANTS-001` /
  `-002`) is merged; its detail lives in the corresponding `docs/` files.

---

## Future / not started

* **`FIRST-MAINTENANCE-RELEASE-PLAN-001`** — plan a future maintenance release
  (a new version after `v1.0.0`). Not started; runs only when a maintenance
  release is actually scheduled.

---

## Retained cross-references (maintenance)

The module-side pinmap ledger `MODULE-PINMAPS-GDRIVE-001` and the canonical Core
connector pin map [`docs/hardware/s360-100-core-connector-pin-map.md`](docs/hardware/s360-100-core-connector-pin-map.md)
remain the source of truth for the S360-100 ceiling Core bus and are unchanged.

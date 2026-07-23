# Sense360 Roadmap / Status (DOCS-CONSOLIDATION-ROADMAP-001)

**Canonical id:** `DOCS-CONSOLIDATION-ROADMAP-001`
**Type:** Docs only. This document does **not** change firmware behaviour,
publish firmware, edit `manifest.json` / `firmware/sources.json`, enable
WebFlash, promote any product, or move any readiness gate.

This is the **single canonical** repo status / roadmap / blocker /
upcoming-PR document for `sense360store/esphome-public`. It consolidates the
high-level state that used to be duplicated across several roadmap / audit /
status / handoff Markdown files. Those files now carry a short redirect
banner pointing back here (see [§10 Consolidated / redirected docs](#10-consolidated--redirected-docs)).

Every status statement below is sourced from a committed config or a
test-backed reference doc. Where this doc and a source-of-truth file ever
disagree, **the source-of-truth file wins** and this doc is the one to fix.

## Sources of truth (do not duplicate, link instead)

| Layer | Source of truth |
|---|---|
| Board / module catalog | [`config/hardware-catalog.json`](../config/hardware-catalog.json) · [`docs/hardware-catalog.md`](hardware-catalog.md) |
| WebFlash grammar | [`config/webflash-compatibility.json`](../config/webflash-compatibility.json) · [`docs/webflash-contract.md`](webflash-contract.md) |
| Shippable WebFlash builds | [`config/webflash-builds.json`](../config/webflash-builds.json) |
| Firmware combination matrix | [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json) |
| Product catalog | [`config/product-catalog.json`](../config/product-catalog.json) |
| Room bundle SKUs | [`config/room-bundle-skus.json`](../config/room-bundle-skus.json) · [`docs/sense360-room-bundles.md`](sense360-room-bundles.md) |
| Commercial / shop launch posture | [`config/shop-commercial-source-of-truth.json`](../config/shop-commercial-source-of-truth.json) (SHOP-COMMERCIAL-SOURCE-OF-TRUTH-001; narrative doc [moved private](archive-index.md)) |
| Manual (non-release) fan artifacts | [`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json) · [`docs/manual-install-fan-candidates.md` (archived)](archive-index.md) |
| Promotion gates | [`docs/preview-to-stable-promotion-gates.md` (archived)](archive-index.md) |
| Per-board hardware evidence | `docs/hardware/**` (pinmaps, schematics, artifacts — **preserved, not consolidated**) |
| Blocker burn-down detail | [`docs/blocker-burndown.md` (archived)](archive-index.md) |
| Detailed PR working queue | [`UPCOMING_PR.md` (retired)](archive-index.md) · standing gates: [`docs/standing-invariants.md`](standing-invariants.md) |
| Reconciled release-matrix / WebFlash / firmware-availability view | [`docs/release-matrix-webflash-alignment.md`](release-matrix-webflash-alignment.md) (WEBFLASH-RELEASE-MATRIX-ALIGNMENT-001) |
| Consolidated first-release / expansion gate checklist | [`docs/first-release-gates.md`](first-release-gates.md) (PRE-HW-PREP-FIRST-RELEASE-GATES-001) |
| Operator dry-run checklist for the first stable release | [`docs/first-release-dryrun-checklist.md`](first-release-dryrun-checklist.md) (FIRST-RELEASE-DRYRUN-CHECKLIST-001) |
| Whole-system architecture (two-repo pipeline + CI map) | [`docs/system-architecture.md`](system-architecture.md) · [`docs/ci-pipeline.md`](ci-pipeline.md) |
| Board / bundle / alias / shim YAML architecture | [`docs/arch-board-bundle-plan.md` (archived)](archive-index.md) · [`docs/system-architecture.md`](system-architecture.md#inside-esphome-public-board--bundle--alias--shim-layers) |

---

## 1. Current release targets

The shippable WebFlash build matrix is [`config/webflash-builds.json`](../config/webflash-builds.json)
(validated by `tests/validate_webflash_builds.py`). There are exactly
**fourteen** builds — three stable, eight preview, three experimental.
`HW-RELEASE-001` ([`docs/hw-release-001.md`](hw-release-001.md), owner
decision of record, 2026-07-09) retired the bench-proof documentation
requirement as a release gate (hardware readiness is declared by the owner
directly) and added nine owner-declared rows as release-eligibility
**metadata only** (`release_state: metadata-ready-unpublished` — no binary,
GitHub Release, tag, or manifest cut): `Ceiling-POE-RoomIQ-LED` re-listed on
preview (reversing the `CI-PIPELINE-CLARITY-001` P4a de-list), the six
FanPWM / FanDAC configs on preview, and the two FanRelay room bundles on the
experimental channel only (mains-adjacent lane per `COMPLIANCE-001`). Fan
configs are **never stable**; kit / customer visibility is unchanged:

| Config string | Channel | Version | Artifact | Notes |
|---|---|---|---|---|
| `Ceiling-POE-VentIQ-RoomIQ` | **stable** | 1.0.7 | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.7-stable.bin` | Release-One stable build (customer baseline / required config). Rebuilt as v1.0.7 (GitHub Release `v1.0.7`, 2026-07-06) by the shared-default-credential **removal** security rebuild (`REBUILD-CLEAN-CREDENTIALS-001`) — the rebuilt binary ships **unprovisioned** (no per-device credentials are generated; see [`docs/security/release-firmware-credential-posture.md`](security/release-firmware-credential-posture.md)); supersedes v1.0.4, no functional changes. |
| `Ceiling-POE-VentIQ-RoomIQ-LED` | **preview** | 1.0.1 | `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.1-preview.bin` | LED variant is **preview only** (see §7). Rebuilt as v1.0.1 (prerelease `v1.0.1-led-preview`, 2026-07-06) by the security rebuild; supersedes `v1.0.0-led-preview`. |
| `Ceiling-POE-AirIQ-RoomIQ` | **stable** | 1.0.9 | `Sense360-Ceiling-POE-AirIQ-RoomIQ-v1.0.9-stable.bin` | Kitchen firmware (`S360-KIT-KITCHEN-P`). Promoted to stable v1.0.6 (2026-06-09) under owner risk-acceptance waiver `HW-AIRIQ-WAIVER-2026-06` (AirIQ sensor stack not bench-verified; owner waiver, not hardware verification); rebuilt as v1.0.9 (GitHub Release `v1.0.9`, 2026-07-06) by the security rebuild. Bundle stays hidden / not buyable. |
| `Ceiling-POE-RoomIQ` | **stable** | 1.0.8 | `Sense360-Ceiling-POE-RoomIQ-v1.0.8-stable.bin` | Bedroom firmware (`S360-KIT-BEDROOM-P`). Promoted to stable v1.0.5 (2026-06-08) under owner risk-acceptance waiver `HW-S360-410-WAIVER-2026-06` (S360-410 stays cataloged_unverified; owner waiver, not hardware verification); rebuilt as v1.0.8 (GitHub Release `v1.0.8`, 2026-07-06) by the security rebuild. Bundle stays hidden / not buyable. |
| `Ceiling-POE-RoomIQ-LED` | **preview** | 1.0.0 | `Sense360-Ceiling-POE-RoomIQ-LED-v1.0.0-preview.bin` | Living / Corridor candidate firmware (`S360-KIT-LIVING-P` / `S360-KIT-CORRIDOR-P`); LED stays preview. RE-LISTED by `HW-RELEASE-001` (owner declaration), reversing the `CI-PIPELINE-CLARITY-001` P4a de-list; metadata-ready / unpublished, bundles hidden / not buyable. Distinct from the VentIQ LED preview above. |
| `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` | **experimental** | 1.0.0 | `Sense360-Ceiling-POE-VentIQ-FanTRIAC-RoomIQ-v1.0.0-experimental.bin` | **Experimental self-build mains** firmware (S360-320 TRIAC). Commissioned by `TRIAC-COMMISSIONING-001` into the experimental lane (`COMPLIANCE-001-RESOLUTION-001`); PACKAGE-TRIAC-001 operator-attested bench proof. **Never stable / recommended / default / buyable / kit-exposed**; self-build CERN-OHL-P board Sense360 never places on the market. Metadata-ready / unpublished (no tag cut); one-click WebFlash import gated by `WF-IMPORT-TRIAC-001`. |
| `Ceiling-POE-FanPWM` | **preview** | 1.0.0 | `Sense360-Ceiling-POE-FanPWM-v1.0.0-preview.bin` | FanPWM (S360-311, SELV). Owner-declared preview row (`HW-RELEASE-001`); metadata-ready / unpublished. `RELEASE-PWM-001` stays the stable blocker; RPM not supported. Never stable. |
| `Ceiling-POE-AirIQ-FanPWM-RoomIQ` | **preview** | 1.0.0 | `Sense360-Ceiling-POE-AirIQ-FanPWM-RoomIQ-v1.0.0-preview.bin` | Kitchen FanPWM room bundle. Owner-declared preview row (`HW-RELEASE-001`); metadata-ready / unpublished. Never stable. |
| `Ceiling-POE-VentIQ-FanPWM-RoomIQ` | **preview** | 1.0.0 | `Sense360-Ceiling-POE-VentIQ-FanPWM-RoomIQ-v1.0.0-preview.bin` | Bathroom FanPWM room bundle. Owner-declared preview row (`HW-RELEASE-001`); metadata-ready / unpublished. Never stable. |
| `Ceiling-POE-FanDAC` | **preview** | 1.0.0 | `Sense360-Ceiling-POE-FanDAC-v1.0.0-preview.bin` | FanDAC (S360-312, SELV). Owner-declared preview row (`HW-RELEASE-001`); metadata-ready / unpublished. `RELEASE-DAC-001` + `FANDAC-I2C-ADDR-001` (pending) stay the stable blockers. Never stable. |
| `Ceiling-POE-AirIQ-FanDAC-RoomIQ` | **preview** | 1.0.0 | `Sense360-Ceiling-POE-AirIQ-FanDAC-RoomIQ-v1.0.0-preview.bin` | Kitchen FanDAC room bundle — the documented **address-overridden exception** to the `fandac_conflicts_with_airiq` one-click mutex (IC2 relocated 0x59 → 0x5A; DIP switch SW2 must match). Owner-declared preview row (`HW-RELEASE-001`); metadata-ready / unpublished. `FANDAC-I2C-ADDR-001` stays pending. Never stable, never one-click. |
| `Ceiling-POE-VentIQ-FanDAC-RoomIQ` | **preview** | 1.0.0 | `Sense360-Ceiling-POE-VentIQ-FanDAC-RoomIQ-v1.0.0-preview.bin` | Bathroom FanDAC room bundle (IC2 0x5A override; DIP switch SW2 must match). Owner-declared preview row (`HW-RELEASE-001`); metadata-ready / unpublished. `FANDAC-I2C-ADDR-001` stays pending. Never stable. |
| `Ceiling-POE-AirIQ-FanRelay-RoomIQ` | **experimental** | 1.0.0 | `Sense360-Ceiling-POE-AirIQ-FanRelay-RoomIQ-v1.0.0-experimental.bin` | Kitchen FanRelay room bundle (S360-310, **mains-adjacent contact switching**). Owner-declared **experimental-only** row (`HW-RELEASE-001`; lane posture per `COMPLIANCE-001`); metadata-ready / unpublished. Competent-person installation where mains switching is in scope. **Never stable / recommended / default / buyable / kit-exposed.** |
| `Ceiling-POE-VentIQ-FanRelay-RoomIQ` | **experimental** | 1.0.0 | `Sense360-Ceiling-POE-VentIQ-FanRelay-RoomIQ-v1.0.0-experimental.bin` | Bathroom FanRelay room bundle (S360-310, **mains-adjacent contact switching**). Owner-declared **experimental-only** row (`HW-RELEASE-001`; lane posture per `COMPLIANCE-001`); metadata-ready / unpublished. Competent-person installation where mains switching is in scope. **Never stable / recommended / default / buyable / kit-exposed.** |

The two LED preview rows remain preview: the VentIQ LED preview is published
(rebuilt as prerelease `v1.0.1-led-preview` on 2026-07-06, superseding
`v1.0.0-led-preview`); the Living/Corridor LED row is
**release-eligibility metadata only** (no binary / GitHub Release published).
The Kitchen and Bedroom stable promotions ride owner risk-acceptance waivers,
not hardware verification: no hardware, bench, or compliance proof is claimed,
and the consuming candidate bundles stay hidden / not buyable / not customer
defaults. Firmware-build proof for the room-bundle rows is the hosted Preview
Compile Dry-Run (run `26821900127`).

The three **experimental** rows are the mains-adjacent lane.
`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` is the self-build mains TRIAC firmware,
commissioned by `TRIAC-COMMISSIONING-001` into the experimental lane defined by
[`docs/decisions/COMPLIANCE-001-RESOLUTION-001.md`](decisions/COMPLIANCE-001-RESOLUTION-001.md).
It is **release-eligibility metadata only** (no tag cut, no binary published),
backed by the operator-attested `PACKAGE-TRIAC-001` bench proof, and stays
**never stable / recommended / default / buyable / kit-exposed**: the S360-320
is an open-source CERN-OHL-P board Sense360 never places on the market.
One-click WebFlash import remains gated by `WF-IMPORT-TRIAC-001`. The two
FanRelay room bundles were promoted to the same experimental-only posture by
the `HW-RELEASE-001` owner declaration (S360-310 mains-adjacent contact
switching; `RELEASE-RELAY-001` stays the stable blocker; no
electrical-safety / EMC / compliance claim).

Release-One required configs (`config/webflash-compatibility.json` →
`release_one_required_configs`): **`Ceiling-POE-VentIQ-RoomIQ`** only — the four
preview rows are **not** Release-One required configs.

No other config string is release-eligible today. Under `HW-RELEASE-001` the
FanRelay / FanPWM / FanDAC / FanTRIAC configs above ARE in
`webflash-builds.json` on their non-stable lanes with `artifact_name` and
`webflash_build_matrix: true` — but a fan config on the **stable** channel
remains a guardrail violation (`scripts/list_release_targets.py`), and the
catalog status for every fan config is `preview`, never `production`.

| Release status field | Value |
|---|---|
| First stable release | **published / live** |
| Current release path | **`v1.0.7`** (GitHub Release, 2026-07-06; the 2026-07-06 `REBUILD-CLEAN-CREDENTIALS-001` security rebuild cut `v1.0.7` / `v1.0.8` / `v1.0.9` / `v1.0.1-led-preview`). First stable release was **`v1.0.0`** (GitHub Release, 2026-05-12; imported/live in WebFlash) |
| Next publish action | **none** unless a new version is planned |
| Next meaningful release task | maintenance-release planning (`FIRST-MAINTENANCE-RELEASE-PLAN-001`) or the next stable-bundle expansion gates (§6 / §8) |

The stable first release is **no longer pending**: the stable build above shipped
as GitHub Release **`v1.0.0`** and is imported/live in WebFlash — see
[`docs/first-release-publish-readiness.md` (archived)](archive-index.md)
(`FIRST-RELEASE-PUBLISH-READINESS-001`) and
[`docs/webflash-release-proof.md` (archived)](archive-index.md) (ESP-006/ESP-007).
Any future publish must use a **new version** (e.g. `1.0.1` / `1.1.0`); `v1.0.0`
is not re-published or re-tagged.

### 1.1 Rebuilt-release credential posture — release-body correction pending (RECON-UPSTREAM-CRED-CLAIMS-001)

The four `REBUILD-CLEAN-CREDENTIALS-001` releases (`v1.0.7` / `v1.0.8` /
`v1.0.9` / `v1.0.1-led-preview`, all cut 2026-07-06) were published with a
**factually wrong changelog line** — "device credentials are now provisioned
uniquely per device". That claim is false. The accurate posture (source of
truth: [`docs/security/release-firmware-credential-posture.md`](security/release-firmware-credential-posture.md)) is:

- the shared published default credentials were **removed**;
- the released prebuilt firmware ships **unprovisioned** — it does not
  generate an API encryption key or any OTA / web / fallback-AP password;
- the native API is **unencrypted**, OTA and the web interface are
  **unauthenticated**, and the fallback AP is **open**;
- users requiring authentication must currently **self-build** with unique
  secrets (`secrets.example.yaml` → private `secrets.yaml`);
- per-device provisioning is the planned, **not implemented**
  `SEC-ESP-PROVISIONING-001` follow-up.

No repository workflow supports editing an already-published release body,
so correcting the four release bodies is an **owner action** (exact
replacement wording and step-by-step instructions:
[`docs/rebuild-clean-credentials-001.md` §Release-body correction](rebuild-clean-credentials-001.md#release-body-correction-recon-upstream-cred-claims-001)).
The `WF-H1-REIMPORT-CLEAN-001` WebFlash execution (W1–W3) has landed
(WebFlash PRs [#582](https://github.com/sense360store/WebFlash/pull/582),
[#584](https://github.com/sense360store/WebFlash/pull/584)–[#587](https://github.com/sense360store/WebFlash/pull/587),
[#592](https://github.com/sense360store/WebFlash/pull/592)) without copying
the false claim; that completion covers the **automated / WebFlash
execution only** — the owner release-body corrections, the R-D4 bench
attestation, the advisory publication, the superseded-release annotation,
and `SEC-ESP-PROVISIONING-001` all remain **open**. Until the bodies are
corrected, any future WebFlash import or notes sync must **not** copy
changelog / description text from those release bodies. No firmware
binary, hash, tag, or release asset changes under this correction — it is
release-note text only.

---

## 2. Bundle SKUs

Customer-facing PoE room kit SKUs from [`config/room-bundle-skus.json`](../config/room-bundle-skus.json)
(validated by `tests/test_room_bundle_skus.py`). Bundle SKUs are **not** board
SKUs, **not** firmware artifact names, and **not** release artifact ids. This
file is planning/documentation only — it adds no product YAMLs, WebFlash
wrappers, builds, or releases.

| Bundle SKU | Room | Boards | Likely firmware target | Status |
|---|---|---|---|---|
| `S360-KIT-BATH-P` | bathroom | S360-100/200/211/410 | `Ceiling-POE-VentIQ-RoomIQ` | **stable-release** |
| `S360-KIT-KITCHEN-P` | kitchen | S360-100/200/210/410 | `Ceiling-POE-AirIQ-RoomIQ` | **stable-release** (promoted by the `HW-RELEASE-001` owner declaration; G8 gates cleared by owner declaration, HW-RELEASE-001; still hidden / not buyable) |
| `S360-KIT-LIVING-P` | living-room | S360-100/200/300/410 | `Ceiling-POE-RoomIQ-LED` | preview-candidate |
| `S360-KIT-BEDROOM-P` | bedroom | S360-100/200/410 | `Ceiling-POE-RoomIQ` | stable-candidate |
| `S360-KIT-CORRIDOR-P` | corridor | S360-100/200/300/410 | `Ceiling-POE-RoomIQ-LED` | preview-candidate |

`S360-KIT-BATH-P` and (per the `HW-RELEASE-001` owner declaration)
`S360-KIT-KITCHEN-P` map to shipped stable builds; the Kitchen promotion is
an owner decision, not hardware verification, and its kit / customer
visibility is unchanged (hidden / not buyable). The remaining bundles are
candidates gated behind their own promotion gates (LED gauntlet and/or the
S360-410 PoE evidence gate — see §6 / §7). No bundle is promoted by this doc.

**Shop posture:** for the first shop launch, `S360-KIT-BATH-P` (shop title
*Sense360 Bathroom Bundle — PoE*) is the **only** publicly buyable product. The
four candidate bundles above are **not publicly buyable**: they stay hidden from
shop navigation (waitlist / coming-soon only, never a buy button) until their
gates close. The customer-facing posture, claims, and WebFlash URL are pinned in
[`config/shop-commercial-source-of-truth.json`](../config/shop-commercial-source-of-truth.json)
(`SHOP-COMMERCIAL-SOURCE-OF-TRUTH-001`; its narrative doc is
[moved private](archive-index.md)); this doc neither sells nor lists any
bundle.

---

## 3. Board SKUs

Canonical board/module catalog from [`config/hardware-catalog.json`](../config/hardware-catalog.json)
(validated by `tests/test_hardware_catalog.py`). `schematic_status` is the
authoritative per-board flag.

| SKU | Friendly name | Group / type | `schematic_status` |
|---|---|---|---|
| S360-100 | Sense360 Core | Ceiling / Hub | verified |
| S360-200 | Sense360 RoomIQ | Ceiling / Sensor | verified |
| S360-210 | Sense360 AirIQ | Ceiling / Sensor | verified |
| S360-211 | Sense360 VentIQ | Ceiling / Sensor | verified |
| S360-300 | Sense360 LED | Ceiling / Indicator | verified |
| S360-310 | Sense360 Relay | Inline / Driver | cataloged_unverified |
| S360-311 | Sense360 PWM | Inline / Driver | cataloged_unverified |
| S360-312 | Sense360 DAC | Inline / Driver | cataloged_unverified |
| S360-320 | Sense360 TRIAC | Inline / Driver | cataloged_unverified |
| S360-400 | Sense360 240v PSU | Power / PSU | cataloged_unverified |
| S360-410 | Sense360 PoE PSU | Power / PSU | cataloged_unverified |

The four inline fan drivers and both PSUs remain `cataloged_unverified`. In
particular **S360-410 is NOT verified** (see §6).

---

## 4. Room firmware configs

Firmware config strings live in [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json).
The room-relevant PoE configs and their current state:

| Config string | State | Notes |
|---|---|---|
| `Ceiling-POE-VentIQ-RoomIQ` | **stable** (shipped) | Release-One stable build. |
| `Ceiling-POE-VentIQ-RoomIQ-LED` | **preview** (shipped) | LED preview build. |
| `Ceiling-POE-RoomIQ-LED` | missing-product-yaml | Living-room / corridor target; LED preview-gated. |
| `Ceiling-POE-AirIQ-RoomIQ` | compile-only skeleton | Kitchen target; `products/compile-only/ceiling-poe-airiq-roomiq.yaml`. |
| `Ceiling-POE-RoomIQ` | compile-only skeleton | Bedroom target; `products/compile-only/ceiling-poe-roomiq.yaml`. |

Only the two shipped configs are release-eligible. The others are
compile-only / planning targets owned by the stable-target expansion lanes and
the LED gauntlet; none is promoted here.

---

## 5. WebFlash / release status

- WebFlash exposes exactly the two builds in §1: one **stable**
  (`Ceiling-POE-VentIQ-RoomIQ`) and one **preview** (`...-LED`).
- No fan-driver firmware (Relay / PWM / DAC / TRIAC) is in the **committed**
  WebFlash build matrix: none appears in `config/webflash-builds.json`, none has
  an `artifact_name`, and none flips `webflash_build_matrix`.
- FanRelay / FanPWM / FanDAC are now **preview / manual-preview WebFlash-import
  eligible** (Advanced-install-only, acknowledgement-gated) under
  `RELEASE-PREVIEW-FAN-WEBFLASH-ELIGIBILITY-001` — this removes the upstream
  import block (`webflash_build_matrix: false` is no longer a preview-import
  blocker) but is **not** a committed build row, so the actual WebFlash one-click
  import stays the separately queued downstream `WF-IMPORT-RELAY-001` /
  `WF-IMPORT-PWM-001` / `WF-IMPORT-DAC-001` slice. Fan drivers stay **not stable,
  not recommended, not default, not buyable**; `RELEASE-{RELAY,PWM,DAC}-001`
  stable/full release stays blocked. **FanTRIAC stays excluded** (`HW-005`,
  separate TRIAC-specific PR).
- The `workflow_dispatch`-only manual-firmware-artifacts lane
  ([`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json),
  [`docs/manual-install-fan-candidates.md` (archived)](archive-index.md))
  compiles the FanRelay / FanPWM / FanDAC manual candidates and uploads only
  **temporary, expiring, non-release** GitHub Actions artifacts. It never
  creates a release, never writes `firmware/sources.json` / `manifest.json`,
  and never sets a release channel.
- Cross-repo WebFlash import/runtime work is owned by `sense360store/WebFlash`
  and tracked there; see §9.

### 5.1 First-release workflow dry-run (FIRST-RELEASE-WORKFLOW-DRYRUN-001)

The non-publishing first-release dry-run was executed on 2026-05-31 against the
only eligible stable path (`Ceiling-POE-VentIQ-RoomIQ` / `stable` / `1.0.0`,
bundle `S360-KIT-BATH-P`). It threads the existing dry-run lanes only and
**publishes nothing**: release-note generation + validation, the
`Build & Release Firmware` `release-dry-run` job steps (target validation,
`scripts/plan_room_release_notes.py`, the `tests/test_plan_room_release_notes.py`
+ `tests/test_release_dry_run_mode.py` guardrails, and the no-side-effects
assertion), and the artifact-name assertion all **passed**. Expected artifact:
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`. Checksums + build-info
`manifest.json` are publish-time only and were **not** produced; **no** release,
tag, `.bin`, `firmware/sources.json`, or `manifest.json` was created.

- **Outcome:** `dry-run passed` (upgraded from `partial`). Every local dry-run
  lane passed, and the hosted GitHub Actions **run URL / run ID** has since been
  captured and **passed** — see §5.2.
- The `Build & Release Firmware` workflow **already has a safe-by-default
  dry-run mode** (`RELEASE-WORKFLOW-DRYRUN-MODE-001`), so the conditional
  `FIRST-RELEASE-WORKFLOW-DRYRUN-MODE-001` is **not** opened.
- Full record + reproduction commands:
  [`docs/first-release-dryrun-checklist.md`](first-release-dryrun-checklist.md)
  §11 (`FIRST-RELEASE-WORKFLOW-DRYRUN-001`; §11.8 for the hosted pass). This is a
  status snapshot; it promotes nothing and flips no gate.

### 5.2 Hosted CI dry-run result — passed (FIRST-RELEASE-WORKFLOW-DRYRUN-CI-RESULT-001)

The hosted GitHub Actions dry-run for the only eligible stable path has been
dispatched on hosted CI by an operator and **passed**, upgrading the
first-release dry-run from `partial` to **`passed`** (hosted CI dry-run:
**passed**). Record only — nothing published, no `.bin`, no promotion, no
hardware verified.

| Field | Value |
|---|---|
| Workflow / job | `Build & Release Firmware` → `Release Dry-Run (no publish)` |
| Run URL | <https://github.com/sense360store/esphome-public/actions/runs/26723839261/job/78755574773> |
| Run ID / Job ID | `26723839261` / `78755574773` |
| Commit SHA | `b2cc9fd5054f62c18b63230c2b380bc749abf2f0` |
| Path | `S360-KIT-BATH-P` / `Ceiling-POE-VentIQ-RoomIQ` / `stable` / `1.0.0` |
| Expected artifact | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` |
| Result | **`passed`** — all dry-run guardrail steps passed |
| Artifacts | **none** (expected for a no-publish dry-run) |

All dry-run guardrail steps passed; the dry-run created **no** release, tag,
asset, committed `.bin`, `firmware/sources.json`, or `manifest.json`. This is
**workflow confidence evidence** (a rehearsal of the release *workflow*), not a
sign that `v1.0.0` is unpublished. The stable first release **`v1.0.0` is already
published and live** (§1) with real changelog bullets, checksums, build-info
`manifest.json`, and a WebFlash import — there is **no pending publish action**
for it. A *future* publish would be a separate human decision on a **new
version** (e.g. `1.0.1` / `1.1.0`) with its own changelog, optional
external-component ref/tag pin, publish-time checksums, and WebFlash handoff.
Full record:
[`docs/first-release-dryrun-checklist.md`](first-release-dryrun-checklist.md) §11.8
(`FIRST-RELEASE-WORKFLOW-DRYRUN-CI-RESULT-001`) and
[`docs/first-release-publish-readiness.md` (archived)](archive-index.md).

---

## 6. Hardware blockers

| Blocker | Status | Source |
|---|---|---|
| **S360-410 PoE PSU** `cataloged_unverified` | **Released under owner waiver** `HW-S360-410-WAIVER-2026-06` (block lifted; remaining E11/E12 evidence not performed, risk accepted) | [§6.1](#61-poe--s360-410-blocker) |
| Inline fan drivers (S360-310/311/312/320) `cataloged_unverified` | open | `config/hardware-catalog.json` |
| S360-400 240v PSU `cataloged_unverified` | open | `config/hardware-catalog.json` |
| Fan-driver current / thermal / safety bench | pending | [`docs/blocker-burndown.md` (archived)](archive-index.md) |
| Mains / compliance sign-off (Relay / TRIAC / 240v PSU) | pending | [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md) |

### 6.1 PoE / S360-410 blocker

**S360-410 remains `cataloged_unverified` — NOT verified.** It is now
**released under owner waiver `HW-S360-410-WAIVER-2026-06`** (2026-06-08): the
hardware-verification block is lifted on an owner **risk-acceptance** basis,
while the remaining E11/E12 bench and isolation evidence stays **unresolved
(not performed)** and the risk is **accepted**.

**Owner waiver (HW-S360-410-WAIVER-2026-06, 2026-06-08).** The owner decided to
release S360-410 **without** completing the remaining bench (E11 load / cold-start
inrush / thermal rise) and isolation (E12 Hi-pot / insulation resistance /
leakage / earth continuity) evidence, and **accepted the risk**. Those
measurements were **NOT performed, NOT tested, and NOT passed** — this is a
**risk-acceptance waiver, not verification**. `S360-410` keeps
`schematic_status: cataloged_unverified` (no `verified` flip, no `schematic_file`);
[`config/hardware-catalog.json`](../config/hardware-catalog.json) records the
waiver in a new `release_disposition` field only. The dependent PoE room bundles
(`S360-KIT-BEDROOM-P`, `S360-KIT-KITCHEN-P`, `S360-KIT-LIVING-P`,
`S360-KIT-CORRIDOR-P`) **no longer block on the S360-410 hardware-verification
basis** and proceed under this waiver; their non-S360-410 gates (the AirIQ stack;
the LED preview→stable gauntlet) are unaffected. The full waiver record is
[`docs/package-poe-410-evidence-result.md` §0.1 (archived)](archive-index.md).

Per [`docs/package-poe-410-001-audit.md` (archived)](archive-index.md)
(PACKAGE-POE-410-001), the evidence is **insufficient** to move S360-410 from
`cataloged_unverified` to `verified` and insufficient to close the package
header today (audit "option 4": evidence-request path). The remaining
schematic / silkscreen / bench / harness / compliance evidence is enumerated
there and in [`docs/hardware/s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md)
(HW-PINMAP-410). The consolidated evidence matrix, the per-bundle
stable-bundle impact assessment, and the operator/designer next-evidence
checklist are recorded at
[`docs/package-poe-410-evidence-result.md` (archived)](archive-index.md)
(PACKAGE-POE-410-EVIDENCE-RESULT-001, 2026-05-29; E13 PCB-source line moved
to on-file by HW-S360-410-GERBERS-E13, 2026-06-08; connector pin-1 polarity
E9 + J2-harness E10 recorded on file and the Release-One PoE caveat E15
closed by HW-S360-410-EVIDENCE-2026-06, 2026-06-08) — which records the
connector pin-1 polarity (E9, CAD-render + as-labeled-connector basis), the
J2-harness spec (E10), and the PCB-source / gerbers class (E13, gerber set
committed at `docs/hardware/gerbers/S360-410-R4/`) **on file**, and the PoE
bench (E11) as **partial** (link-up + 5 V confirmed; load / cold-start
inrush / thermal / EMI-EMC **not measured**) — while the **bench remainder
(E11) and the isolation / safety class (E12) stay missing**, none of which,
individually or together, verifies the board. It also records that
`S360-KIT-BEDROOM-P` is blocked by S360-410 alone while
`S360-KIT-KITCHEN-P` / `S360-KIT-LIVING-P` / `S360-KIT-CORRIDOR-P` are
partially blocked (S360-410 plus an AirIQ-stack or LED-gauntlet dependency)
and the already-shipping `S360-KIT-BATH-P` is unaffected. *(That is the
pre-waiver evidence assessment; the bundle-blocking disposition is superseded
by the owner waiver recorded above.)*

This blocker **previously** gated `PRODUCT-POE-410-001`, `RELEASE-POE-410-001`,
and the stable-candidate room bundles that include S360-410
(`S360-KIT-KITCHEN-P`, `S360-KIT-BEDROOM-P`, and the preview LED bundles). Under
owner waiver `HW-S360-410-WAIVER-2026-06` the **hardware-verification block is
lifted** on a risk-acceptance basis, so those bundles no longer block on the
S360-410 hardware-verification basis. The waiver lifts the block **only**: it
does **not** flip any `config/webflash-builds.json` channel, promote any bundle
to stable, or productize Bedroom (those stay separate, explicit steps), and it
makes **no S360-410 verified claim** — the board stays `cataloged_unverified`,
the E11/E12 evidence was **not measured**, and **no S360-410 verified claim is
made anywhere in this repo.** The Release-One PoE **documentation** caveat (E15)
remains **closed** (2026-06, HW-S360-410-EVIDENCE-2026-06, on the E9 + E10
basis).

### 6.2 FanPWM native path status

The Core-side fan path is **native ESP32-S3 GPIO**, not SX1509. Per
[`docs/hardware/s360-100-native-fan-gpio-map.md`](hardware/s360-100-native-fan-gpio-map.md)
(S360-100-NATIVE-FAN-GPIO-MAP-001) the SX1509 (`U3`) is removed from the
S360-100 fan signal path on the refreshed `S360-100-R4` schematic.

- **Native candidate:** [`packages/expansions/fan_pwm_native.yaml`](../packages/expansions/fan_pwm_native.yaml)
  binds FanPWM control to native GPIO (`TachPMW1..4` → `IO10`/`IO11`/`IO12`/`IO39`,
  four `output: platform: ledc`) and tach to native GPIO
  (`Pul_Cou1`/`Pul_Cou2`/`Pul_Cou4` → `IO17`/`IO18`/`IO9`, three
  `pulse_counter` diagnostics). Composed by the compile-only skeleton
  `products/compile-only/ceiling-poe-fanpwm-native.yaml`.
- **Compile-proven, bench-pending.** The native composition is
  `validated-full-compile` — a full `esphome compile` PASSED (rc=0,
  S360-311-NATIVE-FANPWM-COMPILE-001) and an operator **functional** PWM bench
  PASSED (S360-311-NATIVE-FANPWM-BENCH-001, operator-notes attestation). A
  green compile and a functional bench are **not** current/thermal or RPM
  validation: **current / thermal were NOT measured** and **tach / RPM were
  NOT measured**. Those stay owed to `S360-311-CURRENT-THERMAL-001`;
  `rpm_supported` stays `false`.
- **Legacy SX1509 path is superseded.** The legacy
  `packages/expansions/fan_pwm.yaml` / `fan_pwm_sx1509.yaml` are classified
  **legacy / superseded** and are manual-only, not release-selectable. The
  historical SX1509 pulse-counter proof
  (`tests/test_sx1509_tach_pulse_counter_proof.py`) is retained as evidence.
- **Excluded from release / WebFlash.** `Ceiling-POE-FanPWM` stays
  `hardware-pending`, no WebFlash token / artifact / build-matrix flip,
  `S360-311` stays `cataloged_unverified`.

---

## 7. LED preview status

The Sense360 LED ring (S360-300) is **preview only — not stable.** The
`Ceiling-POE-VentIQ-RoomIQ-LED` build ships on the **preview** channel
(§1), and the LED room bundles (`S360-KIT-LIVING-P`, `S360-KIT-CORRIDOR-P`)
are `preview-candidate`.

LED stays preview until the preview→stable gauntlet closes
([`docs/preview-to-stable-promotion-gates.md` (archived)](archive-index.md),
[`docs/product-led-preview-decision.md` (archived)](archive-index.md)):
`S360-300-BENCH-001`, `WF-HW-TEST-001`, `WF-HW-TEST-003`, `RELEASE-007`.
**No LED-stable claim is made anywhere in this repo.**

The customer LED firmware experience (Room Light, Night Mode, status /
identify overlays) is the LED framework — see **§14**. It is software
foundation only and changes none of the preview gating above.

---

## 8. Next PR queue

The detailed [`UPCOMING_PR.md` queue was retired](archive-index.md) under
`DOCS-DISPOSITION-001` Step 7 (its final open-queue snapshot is preserved in
the Step 7 PR description; the standing invariants moved verbatim to
[`docs/standing-invariants.md`](standing-invariants.md)). High-level
near-term lanes:

1. **Power / PoE lane** — `PRODUCT-POWER-400-001` → `RELEASE-POWER-400-001`;
   `RELEASE-POE-410-001` gated behind the S360-410 evidence blocker (§6.1).
2. **Fan-driver evidence lane** — `S360-311-CURRENT-THERMAL-001` (FanPWM
   measured current/thermal), `S360-312-BENCH-RESULT-001` (FanDAC),
   `S360-310-SAFETY-BENCH-RESULT-001` (FanRelay safety).
3. **Fan-driver release lanes** — Relay / PWM / DAC / TRIAC
   `PACKAGE-*` → `PRODUCT-*` → `WEBFLASH-*` → `RELEASE-*`, each behind its own
   per-board evidence + WebFlash live-check gate.
4. **LED promotion lane** — `S360-300-BENCH-001`, `RELEASE-007` (§7).
5. **WebFlash live-check lane** — `WEBFLASH-{PWM,DAC,RELAY}-LIVE-CHECK-001`
   (blocked on `sense360store/WebFlash` read access).
6. **Audit / drift lane** — `WEBFLASH-DRIFT-001`, `CI-TOOLCHAIN-001`.

No queue item is started, reordered, or unblocked by this doc; this is a
status snapshot, not a reprioritisation.

---

## Next Hardware Tasks (Blocked on Physical Hardware)

The next **real hardware** task — to be run **only when physical hardware
exists** — is recorded below. This is a forward pointer only; it claims no bench
evidence, promotes nothing, and flips no gate. The S360-312 DAC firmware is
design-complete (PR #674, deliverables D1–D6) but **no S360-312 board exists
yet**, so all of its bench evidence stays owed.

| Task | Board | Blocking | Evidence Owed |
|---|---|---|---|
| `S360-312-DAC-BENCH-001` | S360-312 R4 (DAC / dual GP8403) | No physical S360-312 board in hand (pre-hardware) | Measured 0–10 V output per channel; GP8403 detection + I²C address (SW1/SW2); output range/calibration; fan/controller response; current; thermal; harness/silkscreen confirmation |
| `PRESENCE-BENCH-001` | S360-200 R4 (RoomIQ tri-sensor Presence, §13) | Bench session with assembled S360-100 + S360-200 required | Operator checklist [`docs/hardware/presence-framework-bench-checklist.md`](hardware/presence-framework-bench-checklist.md): PIR latency/false triggers, LD2450 moving/still/count/coordinates, SEN0609 static presence, fusion scenarios, disconnect/recovery, startup/clear-delay/mode timing |
| `LED-FRAMEWORK-BENCH-001` | S360-300 R4 (LED framework, §14) | Bench session with assembled S360-100 + S360-300 + S360-200 required | Operator checklist [`docs/hardware/led-framework-bench-checklist.md`](hardware/led-framework-bench-checklist.md): colour/channel order, LED count, supply-rail identity (+5V vs +3.3V), min/max safe brightness, thermal, power draw, night-mode comfort, diffuser/flicker, restore after restart, identify/status visibility, Presence/lux automation, HA latency, failure/recovery |
| `BLOWER-FRAMEWORK-BENCH-001` | S360-100 R4 (on-board FAN net / J13, §18) | Bench session with an assembled S360-100 and a 5 V blower on J13 required | Operator checklist [`docs/hardware/blower-framework-bench-checklist.md`](hardware/blower-framework-bench-checklist.md): FAN-net drive vs relay/status-LED separation, Manual on/off, AirIQ-driven Auto, fail-safe on unknown demand, anti-short-cycle dwell, blower current draw vs Q4 rating, thermal |

## Evidence & Bench Logs

(no bench logs yet)

---

## 9. Cross-repo WebFlash follow-ups

Owned by `sense360store/WebFlash` and tracked in that repo's `UPCOMING_PR.md`.
Listed here only to keep cross-repo coupling visible (do **not** implement them
from this repo):

- `WF-IMPORT-RELAY-001` — blocked behind `RELEASE-RELAY-001`.
- `WF-IMPORT-PWM-001` — blocked behind `RELEASE-PWM-001`.
- `WF-IMPORT-DAC-001` — blocked behind `RELEASE-DAC-001`.
- `WF-IMPORT-POWER-400-001` — S360-400 power import.
- `WF-IMPORT-POE-410-001` — S360-410 PoE import (gated by §6.1).
- `WF-IMPORT-TRIAC-001` — FanTRIAC import.
- `WF-HW-TEST-002` — hardware test follow-up.
- `WF-LED-STABLE-001` — LED preview→stable promotion follow-up (§7).
- `WF-REQUIRED-001` — `REQUIRED_CONFIGS` reconciliation.
- `WF-KIT-LED-001` — LED kit follow-up.
- `WF-PRODUCT-005` — product follow-up.

Live WebFlash verification (`WEBFLASH-{PWM,DAC,RELAY}-LIVE-CHECK-001`) stays
blocked: this session's GitHub scope is `esphome-public` + `esphome` only, so
the WebFlash side is **prior-recorded, not re-verified** (`NEEDS-TOOLING`).

---

## 10. Consolidated / redirected docs

The following roadmap / status / audit / handoff docs are **superseded for
current-state status** by this canonical doc and now carry a redirect banner
at the top (their historical bodies are preserved for provenance):

- [`docs/repo-freshness-roadmap-audit.md` (archived)](archive-index.md)
- [`docs/repo-structure-audit.md` (archived)](archive-index.md)
- [`docs/cleanup-audit.md` (archived)](archive-index.md)
- [`docs/webflash-drift-audit.md` (archived)](archive-index.md)
- [`docs/webflash-ci-alignment.md` (archived)](archive-index.md)
- [`docs/webflash-release-handoff.md` (archived)](archive-index.md)
- [`docs/stable-target-expansion-plan.md` (archived)](archive-index.md)
- [`docs/stable-target-ventiq-001-gate-closure.md` (archived)](archive-index.md)

**Preserved, not consolidated** (source-of-truth, evidence, pinmap, catalog,
policy, or actively test-validated reference docs): everything under
`docs/hardware/**` (pinmaps, schematics, artifacts), `docs/compliance/**`,
`docs/hardware-catalog.md`, `docs/webflash-contract.md`, the
firmware/release matrices, and the user/developer guides. These keep their
own canonical ownership. (`docs/release-one.md`,
`docs/sense360-room-bundles.md`, `docs/preview-to-stable-promotion-gates.md`,
`docs/blocker-burndown.md`, `docs/product-readiness-matrix.md`, and the
readiness matrices were later archived under `DOCS-DISPOSITION-001`; see
[`docs/archive-index.md`](archive-index.md).)

---

## 11. Board / bundle architecture epic

The firmware YAML has been restructured into a SKU-aligned **board-package**
layer (`packages/boards/`), a config-string-named **bundle** layer
(`products/bundles/`), legacy **aliases**, and customer **compat shims**. This
is an internal-composition refactor; it changes **no** config string, artifact
name, lifecycle, `schematic_status`, WebFlash build, or release. Per the
sources-of-truth rule above, the detail is **not duplicated here** — it lives in
its own canonical docs:

| Layer of the epic | Source of truth (do not duplicate) |
|---|---|
| Target shape, rename/alias policy, ordered PR sequence | [`docs/arch-board-bundle-plan.md` (archived)](archive-index.md) |
| Whole-pipeline placement + cross-repo contract | [`docs/system-architecture.md`](system-architecture.md#inside-esphome-public-board--bundle--alias--shim-layers) |
| Per-workflow CI/gate parity across the refactor | [`docs/ci-pipeline.md`](ci-pipeline.md) |
| Per-PR queue state for the epic | [`UPCOMING_PR.md` (retired)](archive-index.md) |

Epic status (ownership lives in the plan §7 / the retired `UPCOMING_PR.md`,
not here):
`BOARD-PACKAGE-LAYER-001/002`, `BUNDLE-LAYER-001`,
`PACKAGE-RENAME-001..005` (LED, AirIQ, VentIQ, RoomIQ, PoE-PSU source-of-truth
flips), and `CI-REFACTOR-VERIFY-001` are landed; `DOCS-ARCH-REFRESH-001`
(this doc-refresh slice) is current; `WEBFLASH-ARCH-SYNC-001` (WebFlash repo)
remains, recording that the rename is invisible to the WebFlash contract.
The cross-repo contract is unchanged: WebFlash couples only through release
tags, config strings, and artifact names (§1, §5) — **no** board/bundle/alias
rename touches `config/webflash-builds.json`, `manifest.json`, or
`firmware/sources.json`, and the two release targets in §1 are unaffected.

---

## 12. Shared firmware framework (CORE-FRAMEWORK-001)

**Status: framework implemented** (structural foundation; landed on `main`
via PR [#825](https://github.com/sense360store/esphome-public/pull/825)).
`CORE-FRAMEWORK-001` adds the shared Sense360 device framework —
consistent Home Assistant naming, device/firmware information, compile-time
capability reporting, module presence/status, diagnostics policy, and a
device-health summary — as one reusable package
([`packages/base/device_framework.yaml`](../packages/base/device_framework.yaml))
composed exactly once by every bundle under `products/bundles/`. The
machine-readable contract is
[`config/core-framework.json`](../config/core-framework.json); the canonical
description is
[`docs/architecture/sense360-core-framework.md`](architecture/sense360-core-framework.md);
tests are `tests/test_core_framework.py` / `tests/test_core_framework_doc.py`
(TDD: contract tests landed failing-first, then the implementation).

Scope facts (do not overclaim):

* **Hardware verification is not required and not claimed** for this
  structural framework — firmware-composition / compile proof only (standing
  invariant: no false proof). Capability and module-status values are
  compile-time composition facts; **no runtime hardware autodetection** is
  performed or claimed.
* **Module-specific runtime health lands per module.** The runtime status
  vocabulary (Initialising / Available / Degraded / Unavailable / Fault) and
  the richer Device Health values (Degraded / Fault / Safe mode) are
  documented as **reserved**; LED / RoomIQ / AirIQ / VentIQ feature and
  health work lands in separate module PRs. **Presence is the first wired
  module** (`PRESENCE-FRAMEWORK-001`, §13): its module-status entity now
  carries the runtime vocabulary from a real LD2450 frame-freshness signal;
  Device Health aggregation itself is still unchanged.
* **This is a repository-local engineering foundation. SOT programme state
  is unchanged** — no SOT programme entry is created, moved or redefined by
  this work item, and no product lifecycle, commercial, WebFlash, release,
  tag, manifest or provisioning state changes. `config/webflash-builds.json`
  is untouched (fourteen builds, §1).
* **One declared gap:** `Ceiling-POE-FanPWM` defers the framework include
  (`framework_included: false` in the contract) because its bundle is
  pinned package-identical to the native full-compile-validated
  compile-only skeleton (`S360-311-NATIVE-FANPWM-COMPILE-001`); wiring it
  would invalidate that recorded compile evidence. The other 15 bundles
  compose the framework now. The exact follow-up (wire bundle + skeleton
  together, re-record via a green hosted `CI: Compile-Only` full run cited
  in `config/compile-only-targets.json`, then flip `framework_included`)
  is specified in
  [`docs/architecture/sense360-core-framework.md`](architecture/sense360-core-framework.md).
* **Compile status — recorded evidence.** All 16 bundle-backed products
  pass `esphome config` with the framework composed (config validation is
  not compile proof), and **six representative configurations have hosted
  `esphome compile` proof** (ESPHome 2026.4.5) from the targeted lane
  "CI: Core Framework Representative Compile"
  (`.github/workflows/core-framework-compile.yml`), hosted run
  `29237693726` at source head `cf7f95066a30abbf801dbc61671d1016d4b8c684`:
  `Ceiling-POE-RoomIQ`, `Ceiling-POE-AirIQ-RoomIQ`,
  `Ceiling-POE-VentIQ-RoomIQ`, `Ceiling-USB-RoomIQ`,
  `Ceiling-USB-VentIQ-RoomIQ`, `Ceiling-POE-VentIQ-RoomIQ-LED` — all six
  compiled successfully; zero artifacts uploaded, nothing published (no
  binary, release, tag, checksum, manifest or WebFlash asset).
  Firmware-build proof only — no hardware evidence is claimed. The
  deferred `Ceiling-POE-FanPWM` was deliberately not compiled by this
  lane (the framework gap above stands).

---

## 13. Presence framework (PRESENCE-FRAMEWORK-001)

**Status: software foundation implemented through the PRESENCE-FRAMEWORK-001
PR (draft) — compile/simulation proof only; physical tri-sensor validation
pending; customer tuning pending; SOT / kit-level bundle reconciliation
resolved by product authority (see below — product definition, not hardware
proof).**

The tri-sensor customer Presence experience for the S360-200 RoomIQ board:
PIR (immediate movement, IO15) + HLK-LD2450 (movement / target tracking /
radar target count, `roomiq_hi_link_uart` @ 256000) + DFRobot SEN0609
(static presence, digital output IO6), fused into one customer occupancy
capability. Canonical description:
[`docs/architecture/sense360-presence-framework.md`](architecture/sense360-presence-framework.md);
machine-readable runtime-status wiring:
[`config/core-framework.json`](../config/core-framework.json)
(`module_runtime_status.presence`); contract tests:
`tests/test_presence_framework.py`; deterministic fusion simulation:
`tests/unit/test_presence_fusion.cpp` against the single shared engine
`include/sense360/presence_fusion.h`.

Scope facts (do not overclaim):

* **Customer surface (default-enabled):** Occupancy, Presence Status,
  Radar Target Count, Presence Mode (Balanced / Responsive / Stable /
  Custom), Clear Delay (5–600 s, default 30 s, persisted, runtime-applied).
  No "Presence Sensitivity" (no honest common runtime sensitivity contract
  across the three sensors — mode-based tuning first) and no "People
  Count" (radar targets are not verified people); the multi-occupant
  status value is the factual **"Multiple targets"** — promotion to
  "Multiple people" wording is an explicit owner decision reserved until
  bench evidence exists. All mode presets, warm-up windows, stale windows
  and debounce values are **provisional engineering defaults** pending
  hardware validation. All per-sensor detail is diagnostic and/or disabled
  by default; the LD2450 per-target coordinate IDs stay a stable surface
  for future Sense360Zones work (no cross-repository Zones change in this
  work item).
* **Presence Module Status is the first runtime module status**: it uses
  the Core-Framework reserved vocabulary from a real LD2450
  frame-freshness signal. Honesty limits recorded in the contract
  (`available_definition`): **Available is service availability of the
  verifiable transport (LD2450 UART) only, not full tri-sensor hardware
  health** — PIR / SEN0609 GPIO levels cannot prove communication health
  and are never claimed healthy (on-device coverage statement: the
  "Presence Sensor Verification" diagnostic); Fault is never derived from
  ordinary stale data.
* **SEN0609 is GPIO-presence integration, phase 1** — not a complete
  SEN0609 integration. UART-based health/configuration/diagnostics is the
  tracked follow-up work item **`PRESENCE-SEN0609-UART-001`** (blocked on
  a supported ESPHome C4001 component + primary protocol documentation;
  ESPHome 2026.4.5 has none). Until it lands, the authoritative
  `roomiq_sen0609_uart` bus stays reserved and no UART parsing is invented.
* **Board vs kit reconciliation (resolved by product authority):** the
  verified S360-200-R4 schematic shows the **PIR (EKMC1601111) soldered
  on-board**, while the **LD2450 (J2) and SEN0609 (J3) are
  connector-attached modules**. Direct SOT inspection (performed after the
  original audit, which could not reach SOT) resolves the fitment
  question at the product-definition level: SOT `products.yaml` defines
  S360-200 RoomIQ as a **single product with no variant axis** whose
  defining capability is presence detection (legacy names *Comfort,
  Presence* — the Presence board carried the radars); SOT `bundles.yaml`
  composes every bundle from whole board SKUs (no bundle carves modules
  out of a board); SOT `roadmap.yaml` ships Zone Studio publicly as
  "LD2450 and SEN0609 radar zone configuration for Home Assistant"; and
  the canonical hardware catalog (`docs/hardware-catalog.md` /
  `config/hardware-catalog.json`) lists PIR, LD2450 and SEN0609 as
  S360-200 components — in deliberate contrast to its "Connectors for …"
  phrasing reserved for genuinely optional attachments (AirIQ: SPS30,
  SFA40; VentIQ: IR temp, SPS30). **Every RoomIQ-bearing bundle therefore
  includes the LD2450 and SEN0609 modules by product definition; no
  radar-less RoomIQ variant exists in SOT, this repository, or WebFlash.**
  This is product authority, **not hardware proof**: per-unit physical
  fitment and behaviour remain bench evidence under `PRESENCE-BENCH-001`.
  The fail-safe posture stays as defence-in-depth against assembly
  defects: an absent J3 module reads clear and cannot assert occupancy,
  block clearing, or fake health; an absent J2 module reports honest
  Degraded.
* **Fail-safe fusion rules** (simulation-tested): stale/unavailable data is
  unknown, never clear; any valid sensor asserts occupancy; clear needs
  unanimity of the usable sensor set plus the clear delay; a sensor failure
  never instantly clears an occupied room; degraded compositions fall back
  to a documented conservative timeout. The former synthetic radar
  confidence tiers (0.95/0.7/0.6) were removed.
* **Compile / simulation proof recorded separately from hardware proof:**
  the deterministic C++ simulation suite and the Python contract tests are
  logic proof; representative hosted compile evidence comes from the
  existing "CI: Core Framework Representative Compile" lane (path triggers
  extended to the presence surfaces; matrix, zero-artifact/no-publication
  guarantees and read-only permissions unchanged). **Hardware evidence is
  not claimed**: PIR, LD2450 and SEN0609 physical validation, sensitivity
  and timing tuning all remain pending — operator checklist:
  [`docs/hardware/presence-framework-bench-checklist.md`](hardware/presence-framework-bench-checklist.md)
  (see `PRESENCE-BENCH-001` in *Next Hardware Tasks*).
* **This is repository-local firmware engineering. SOT programme state is
  unchanged** — no SOT programme entry is created, moved or redefined; no
  product lifecycle, commercial, Shopify, WebFlash, release, tag, manifest
  or provisioning state changes; `config/webflash-builds.json` is untouched
  (fourteen builds, §1). Bundle/product authority note: the S360-200
  hardware catalog BOM already lists all three sensors, and
  `config/product-catalog.json` module declarations are unchanged — this
  work compiles firmware for sensors the board already carries; it does
  not alter commercial bundle contents.

---

## 14. LED framework (LED-FRAMEWORK-001)

**Status: software foundation implemented via the LED-FRAMEWORK-001 PR —
compile and simulation proof only; physical LED validation pending
(`LED-FRAMEWORK-BENCH-001`); safe brightness / colour / night-profile
tuning pending; no SOT or commercial state change.**

Customer-focused LED experience for the S360-300 WS2812B halo ring: one
**Room Light**, **Night Mode** (provisional low/warm profile),
**Night Mode Behaviour** (Manual / When dark / When dark and occupied),
**Status Indicator** (Off / Essential / Detailed), **Identify Device**,
and **Darkness Threshold** — arbitrated by one priority model
(Fault > Identify > Night Mode > Room Light > transient Status). Canonical
doc: [`docs/architecture/sense360-led-framework.md`](architecture/sense360-led-framework.md);
contract tests: [`tests/test_led_framework.py`](../tests/test_led_framework.py);
deterministic simulation: [`tests/unit/test_led_controller.cpp`](../tests/unit/test_led_controller.cpp)
over the shared engine
[`include/sense360/led_controller.h`](../include/sense360/led_controller.h)
(the same header production YAML compiles — no drift-prone second
implementation).

Scope facts (do not overclaim):

* **Customer surface** — default-enabled set is exactly: Room Light,
  Night Mode, Night Mode Behaviour, Status Indicator, Identify Device,
  Darkness Threshold. Everything else is diagnostic and disabled by
  default; no raw channels, no colour-temperature control (no CCT
  hardware), no customer Maximum Brightness control.
* **Brightness ceiling** — no verified electrical/thermal ceiling exists
  anywhere in this repository; the pre-existing 100% software limit is
  preserved as the documented provisional `led_max_brightness_pct`
  substitution, clamped by the engine on every layer. No brightness value
  is claimed physically safe.
* **Module status honesty** — the WS2812B data line is one-way; no
  runtime LED health is fabricated. "LED Module Status" stays the
  compile-time `Included`, and the `LED Output Verification` diagnostic
  states the limit on-device. The engine's fault layer has no production
  producer until a real signal exists.
* **Automation inputs** — the fused Presence Occupancy contract (never
  raw sensors) and the compiled RoomIQ lux path (LTR-303ALS-01 at 0x29 via
  the built-in `ltr_als_ps` platform). The lux-driver identity is now
  reconciled to the schematic/BOM part under
  `S360-200-R4-HARDWARE-RECONCILIATION-001` (the earlier VEML7700 @ 0x10 drift
  is removed); on-hardware sensor response is still pending bench — the board
  under test does not yet answer at 0x29, so lux reads nothing and darkness
  automation fails safe (reports Unknown, never toggles). Runtime confirmation
  is bench work (`LED-FRAMEWORK-BENCH-001` setup item).
* **Bundle authority** — only the two catalog-declared LED-bearing
  preview configs compose the framework (`Ceiling-POE-VentIQ-RoomIQ-LED`,
  `Ceiling-POE-RoomIQ-LED`); non-LED bundles gain nothing
  (test-enforced). SOT lists the S360-300 module as production, but no
  SOT bundle carries LED and both firmware configs stay preview — the
  module-status/firmware-channel reconciliation remains owner work; this
  repository changed no SOT, WebFlash, release or commercial state.
* **"Scheduled" night behaviour deferred** — only SNTP/HA time sources
  exist; neither is a reliable local-first scheduler.
* **Compile/simulation proof recorded separately from hardware proof** —
  the representative compile lane (§12) now covers both LED-bearing
  bundles plus LED-less regression targets; 47 deterministic simulation
  scenarios cover customer state, night mode, automation, hysteresis,
  overlays, priority and restore. None of this is hardware, bench,
  compliance or commercial proof.

---

## 15. RoomIQ framework (ROOMIQ-FRAMEWORK-001)

**Status: software foundation implemented via the ROOMIQ-FRAMEWORK-001 PR —
compile and simulation proof only; physical sensor validation pending
(`ROOMIQ-FRAMEWORK-BENCH-001`, checklist at
[`docs/hardware/roomiq-framework-bench-checklist.md`](hardware/roomiq-framework-bench-checklist.md));
calibration and comfort/brightness threshold tuning pending; the
ambient-light driver identity is reconciled to the schematic/BOM part
(LTR-303ALS-01 @ 0x29 via `ltr_als_ps`) under
`S360-200-R4-HARDWARE-RECONCILIATION-001`, with on-hardware sensor response
still pending bench; no SOT or commercial state change.**

Canonical local environmental service for the S360-200 RoomIQ climate
half: calibrated **Temperature / Humidity / Illuminance** with customer
calibration controls (Temperature Offset, Humidity Offset, Illuminance
Calibration multiplier — applied exactly once, persisted, clamped),
human-friendly **Comfort** (temperature + humidity only), one headline
**Environment State**, a **Brightness** category with hysteresis, honest
per-channel freshness, and the RoomIQ module runtime status (the second
wired module after Presence). Canonical doc:
[`docs/architecture/sense360-roomiq-framework.md`](architecture/sense360-roomiq-framework.md);
contract tests: [`tests/test_roomiq_framework.py`](../tests/test_roomiq_framework.py);
deterministic simulation: [`tests/unit/test_roomiq_engine.cpp`](../tests/unit/test_roomiq_engine.cpp)
over the shared engine
[`include/sense360/roomiq_engine.h`](../include/sense360/roomiq_engine.h)
(the same header production YAML compiles — no drift-prone second
implementation).

Scope facts (do not overclaim):

* **Customer surface** — default-enabled set is exactly: Temperature,
  Humidity, Illuminance, Comfort, Environment State, Brightness plus the
  three calibration controls. No customer-facing numeric comfort score
  (accepted owner decision); no sensor model name in any customer entity.
  All thresholds are provisional comfort heuristics — never medical,
  health, lighting-standard or regulatory claims.
* **Backwards compatibility** — every pre-framework published entity id
  (RoomIQ Temperature / Humidity / Light Level / Feels Like / Comfort
  Score, Comfort Status, Light Status, Temperature / Humidity Advice)
  remains available as a disabled-by-default compatibility entity driven
  by calibrated canonical values; legacy include paths
  (`comfort_basic_profile.yaml`, `roomiq_profile.yaml`,
  `comfort_ceiling.yaml`) keep resolving with pre-framework behaviour.
* **Platform reuse** — RoomIQ is the single environmental source: the LED
  framework now consumes the canonical darkness service (calibrated
  illuminance + staleness + hysteresis computed in the RoomIQ engine; LED
  keeps its customer Darkness Threshold control) and the duplicate
  lux-threshold engine in `led_controller.h` was removed (regression
  tested). Future VentIQ / AirIQ / Zones consumption is documented as a
  stable internal contract, not implemented.
* **Sensor identity (driver reconciled, runtime pending)** — schematic +
  BOM say the S360-200 light sensor is **LTR-303ALS-01** and the temp/humidity
  part is **SHT45** (`SHT45-AD1B-R3`, 0x44). `S360-200-R4-HARDWARE-RECONCILIATION-001`
  corrected the compiled firmware to drive LTR-303ALS-01 at its fixed 0x29
  via the built-in `ltr_als_ps` platform (ALS-only) — the earlier VEML7700 @
  0x10 drift is removed — so the driver identity now matches the schematic/BOM.
  On-hardware sensor response is **still unverified**: the board under test
  lists only the AirIQ sensors (0x59/0x60/0x62) on its I²C scan and does not
  yet answer at 0x29 or 0x44 (a physical population / connector / +3.3 V-rail
  question, not a firmware address error). The customer entity is named
  "Illuminance", the limit is stated on-device (RoomIQ Sensor Verification
  diagnostic), the failure mode is honest (unknown / Degraded, LED darkness
  fails safe), and runtime confirmation stays owner/bench work
  (`ENTITY-RECONCILE-200-ALS-001` + the bench checklist's sensor-identity
  section: confirm U1/U2 answer at 0x29 / 0x44 on real hardware).
* **Module-status honesty** — RoomIQ "Available" means strictly that
  every environmental channel delivered a valid update inside its stale
  window (`config/core-framework.json module_runtime_status.roomiq`);
  never accuracy, calibration correctness or hardware health. Fault has
  no production producer. Temperature and humidity share the SHT4x, so
  their shared failure is modelled honestly.
* **Bundle authority** — all 14 catalog-declared RoomIQ-bearing configs
  compose the framework exactly once and drop the legacy display profile;
  non-RoomIQ configs gain nothing (test-enforced plus the
  `Ceiling-POE-FanDAC` non-RoomIQ regression compile). No
  `config/webflash-builds.json` row, channel, version or artifact name
  changed.
* **Compile/simulation proof recorded separately from hardware proof** —
  the representative compile lane covers PoE/USB RoomIQ, AirIQ+RoomIQ,
  VentIQ+RoomIQ (Release-One), both LED-bearing bundles and the
  non-RoomIQ regression target; 50 deterministic simulation scenarios
  cover startup, calibration, comfort/brightness hysteresis, environment
  precedence, partial degradation, recovery and invalid values. None of
  this is hardware, bench, compliance or commercial proof.

Follow-ups created by this work item (tracked, not started): illuminance
sensor-identity reconciliation (bench + firmware/catalog alignment),
`ROOMIQ-FRAMEWORK-BENCH-001` physical validation, comfort/customer
threshold tuning from bench + customer feedback, future adaptive
brightness (needs bench lux data), future VentIQ environmental
consumption, future AirIQ combined environment state, and the
still-unexposed BMP581 pressure path (`ENTITY-FILL-200-PRESSURE-001`).
SOT programme-status propagation (RoomIQ software foundation implemented)
is an owner action in SOT, in a separate PR — never bundled here.

---

## 16. AirIQ framework (AIRIQ-FRAMEWORK-001)

**Status: software foundation implemented via the AIRIQ-FRAMEWORK-001 PR —
compile and simulation proof only; physical sensor validation pending
(`AIRIQ-FRAMEWORK-BENCH-001`, checklist at
[`docs/hardware/airiq-framework-bench-checklist.md`](hardware/airiq-framework-bench-checklist.md));
MICS-4514 calibration/promotion pending; the compiled BMP390 pressure
driver is recorded as firmware/catalog drift (pressure is not S360-210
product hardware) and SFA40 production population stays an unresolved
conflict (`HW-PINMAP-210-FOLLOWUP`); no SOT, release or commercial state
change.**

Canonical local indoor-air-quality service for the S360-210 AirIQ board:
honest pollutant measurements (**CO2** ppm, **VOC** and **NOx** as relative
indices — never concentrations, **PM2.5** µg/m³), ONE headline **Air
Quality** state (transparent worst-pollutant model — never a blended score,
never an AQI claim), ONE deterministic customer **Recommendation**,
independent per-sensor warm-up/freshness, and the AirIQ module runtime
status (the third wired module after Presence and RoomIQ). Canonical doc:
[`docs/architecture/sense360-airiq-framework.md`](architecture/sense360-airiq-framework.md);
contract tests: [`tests/test_airiq_framework.py`](../tests/test_airiq_framework.py);
deterministic simulation: [`tests/unit/test_airiq_engine.cpp`](../tests/unit/test_airiq_engine.cpp)
over the shared engine
[`include/sense360/airiq_engine.h`](../include/sense360/airiq_engine.h)
(the same header production YAML compiles — no drift-prone second
implementation).

Scope facts (do not overclaim):

* **Customer surface** — default-enabled set is exactly: CO2, VOC, NOx,
  Air Quality, Recommendation (the PCB-mounted compiled sensors). ALL PM
  entities (PM2.5/PM1/PM4/PM10) exist but ship disabled by default: the
  SPS30 is an external attachment whose commercial inclusion is unproven
  (see next bullet). There is NO pressure entity: pressure is absent
  from the verified S360-210 schematic, the R4 BOM and the hardware
  catalog, so the still-compiled BMP390 board driver is firmware/catalog
  drift — excluded from customer entities, severity, health and product
  claims pending reconciliation. All thresholds are provisional
  indoor-air-quality heuristics — never medical, health or regulatory
  claims; the PM2.5 bands derive from published US EPA breakpoints used
  as heuristics only, explicitly not a regulatory AQI.
* **No Base/Pro axis; layered fitment recorded** — the taxonomy is flat
  (one SKU, S360-210); expected-sensor membership is configuration-driven
  substitutions, with PCB-mounted sensors and external attachments kept
  separate in the machine-readable contract
  (`config/core-framework.json` `module_runtime_status.airiq`
  `pcb_mounted_sensors` / `external_attachments`). Per the verified
  schematic: SCD41/SGP41 and the not-compiled MICS-4514 + STM8 stage are
  PCB-mounted; the SPS30 is an external attachment (J2) whose kit/SOT
  inclusion is **unproven** (kit records enumerate board SKUs only, no
  SPS30 SKU exists, SOT never names it, WebFlash calls it optional), so
  it is `expected=false` by default, its absence never degrades health,
  and PM exposure is an explicit per-bundle opt-in
  (`AIRIQ-SPS30-INCLUSION-001` is the product/SOT declaration follow-up);
  formaldehyde (SFA40 — footprint present, production population an
  unresolved conflict, `HW-PINMAP-210-FOLLOWUP` /
  `ENTITY-FILL-210-HCHO-001`) and ozone (an external SEN0321 / ZE27-O3
  input into the STM8 stage, no driver) are inactive engine contract
  slots: no entity, no claim, never expected in any current composition.
* **MICS-4514 included honestly** — PCB-mounted with its STM8
  co-processor (verified schematic U4/U5 + BOM), but no driver exists
  and the readout interface is unverified (`ENTITY-FILL-210-MICS-001`),
  so the engine carries diagnostic-only MiCS channels, no customer
  CO/NO2 concentration is claimed anywhere, and promotion is gated on
  documented calibration evidence (recommended as a separate programme).
* **Backwards compatibility** — the placeholder `air_quality_state`
  entity keeps its id/name (semantic upgrade documented: real headline
  vocabulary instead of a hardcoded "unknown", disabled by default); the
  legacy MQTT block moved verbatim into the framework; legacy include
  paths keep resolving; board sensor ids unchanged; nothing removed.
* **Bundle authority** — all four catalog-declared AirIQ-bearing configs
  compose the framework exactly once and drop the legacy profile;
  non-AirIQ configs gain nothing (test-enforced plus the non-AirIQ
  regression compile target). No `config/webflash-builds.json` row,
  channel, version or artifact name changed.
* **Compile/simulation proof recorded separately from hardware proof** —
  the representative compile lane covers AirIQ+RoomIQ, Release-One
  VentIQ+RoomIQ, both LED-bearing bundles and the non-AirIQ regression
  target; 37 deterministic simulation scenarios cover startup, per-sensor
  warm-up, partial readiness, staleness, recovery, worst-pollutant
  selection, recommendations, boundary values, optional-sensor absence,
  MiCS diagnostics and invalid values. None of this is hardware, bench,
  compliance or commercial proof.

Follow-ups created by this work item (tracked, not started):
`AIRIQ-FRAMEWORK-BENCH-001` physical validation; the MICS-4514
calibration/promotion programme; `AIRIQ-SPS30-INCLUSION-001` (product/SOT
declaration of the external SPS30 attachment as an explicit kit/SOT line
item for any composition that ships it, then that bundle's opt-in flip —
PM2.5 default exposure returns only with that authority); the BMP390
firmware/catalog drift reconciliation (remove the drifted driver or
revise the hardware — owner decision); `HW-PINMAP-210-FOLLOWUP` (SFA40 population evidence, `J*`
connector mapping, SEN0321 attach path, and the directly evidenced
correction of the stale catalog/reference-doc SFA40 "connector" wording —
deliberately not edited in this PR); SFA40 driver work after fitment
resolves (`ENTITY-FILL-210-HCHO-001`); ozone (SEN0321 / ZE27-O3)
identity/unit confirmation before any productisation; customer threshold
tuning; VentIQ consumption of the canonical engine; Pure consumption. SOT
programme-status propagation (AirIQ software foundation implemented) is an
owner action in SOT, in a separate PR — never bundled here.

---

## 17. VentIQ framework (VENTIQ-FRAMEWORK-001)

**Status: software foundation implemented via the VENTIQ-FRAMEWORK-001 PR —
compile and simulation proof only; physical validation pending
(`VENTIQ-FRAMEWORK-BENCH-001`, checklist at
[`docs/hardware/ventiq-framework-bench-checklist.md`](hardware/ventiq-framework-bench-checklist.md));
the compiled SHT4x/BMP390 board drivers are recorded as firmware/schematic
drift (`VENTIQ-HW-DRIFT-001` — no such part on the verified S360-211
schematic, no BOM committed); the fan-relay stage population stays
unproven (`VENTIQ-RELAY-POPULATION-001` — components drawn crossed-out /
do-not-populate on the verified schematic); no SOT, release or commercial
state change.**

Canonical bathroom ventilation service for the S360-211 VentIQ board:
ONE deterministic customer **Recommendation** (Ventilate soon/now) with a
plain-language **Ventilation Reason** (shower, clearing moisture, damp too
long, odour, poor air, high humidity), **Ventilation Needed**, **Shower
Active**, **Mould Risk**, honest **VOC/NOx** indices and ONE **Air
Quality** headline, plus the VentIQ module runtime status — the fourth
wired module after Presence, RoomIQ and AirIQ. Canonical doc:
[`docs/architecture/sense360-ventiq-framework.md`](architecture/sense360-ventiq-framework.md);
contract tests: [`tests/test_ventiq_framework.py`](../tests/test_ventiq_framework.py);
deterministic simulation: [`tests/unit/test_ventiq_engine.cpp`](../tests/unit/test_ventiq_engine.cpp)
over the shared engine
[`include/sense360/ventiq_engine.h`](../include/sense360/ventiq_engine.h)
(the same header production YAML compiles — no drift-prone second
implementation).

Scope facts (do not overclaim):

* **Reuse, not duplication** — pollutant severity comes from an embedded
  canonical AirIQ engine (VOC/NOx expected; no band value re-declared —
  the odour signal is the canonical Fair boundary, which equals the
  legacy odour threshold); humidity/temperature come from the RoomIQ
  canonical calibrated service (`s360_humidity` / `s360_temperature`) —
  raw board sensors are never re-read and RoomIQ comfort thresholds are
  not duplicated (shower/damp values are ventilation dynamics RoomIQ
  does not own). "Is the ventilation hardware available?" stays with the
  Core framework's compile-time Fan Control Module Status entity.
* **Hardware authority recorded** — the verified S360-211-R4 schematic
  (single sheet) shows the SGP41 as the ONLY on-board sensor, the SPS30
  (J4) and IR-temperature (J3) connectors as genuinely optional external
  attachments (no compiled driver, no entity), and the inline fan-relay
  stage with its components crossed out (do-not-populate convention;
  population unproven, no driver, no runtime health — none invented).
  The compiled SHT4x @0x44 / BMP390 @0x77 are firmware/schematic drift
  (feature-entity-matrix CONFIRM flags already recorded it; no S360-211
  BOM artifact exists in-repo); in every current VentIQ composition the
  RoomIQ board's SHT4x shares address 0x44 on the same bus. The board
  package stays byte-compatible; reconciliation is `VENTIQ-HW-DRIFT-001`
  (owner decision with BOM/CPL evidence). The `S360-BATH-B` module-SKU
  diagnostic label (not a catalog SKU) is tracked as
  `VENTIQ-SKU-LABEL-001`.
* **Customer surface** — default-enabled set is exactly: VOC, NOx, Air
  Quality, Recommendation, Ventilation Reason, Ventilation Needed,
  Shower Active, Mould Risk, plus the three preserved threshold controls
  and the shower-detection switch / force-reset buttons. Pre-framework
  the three threshold Numbers were PLACEBO controls no logic read and
  "Auto Ventilation" only wrote a log line — the numbers are now
  genuinely wired into the engine (ids/names/ranges preserved) and the
  do-nothing switch left the default surface (id preserved, disabled by
  default). All ventilation thresholds are provisional heuristics —
  never medical, health, building-standard or regulatory claims.
* **Module health is honest and separable** — VentIQ module status
  attests SGP41 VOC/NOx data freshness ONLY; the RoomIQ-owned humidity
  input never participates (losing it quiets the shower/damp features
  honestly while advice continues on air quality alone — and vice
  versa). No runtime fan/ventilation-hardware health exists anywhere.
* **Backwards compatibility** — every pre-framework published entity id
  remains as a disabled-by-default compatibility entity (exact ids and
  names); climate displays now source the RoomIQ canonical calibrated
  values; derived/state displays now source the engine (documented
  semantic upgrades; the legacy "Excellent" band and ad-hoc formulas are
  retired); `bathroom_pressure_display` is the one documented exception
  that keeps its drifted pre-framework source pending
  `VENTIQ-HW-DRIFT-001`; `diagnostics.yaml` (previously nested in the
  profile) is now included directly by the bundles so the CPU Duty
  surface does not shrink; legacy include paths keep resolving and the
  legacy shim product keeps the profile unchanged.
* **Bundle authority** — all seven catalog-declared VentIQ-bearing
  configs compose the framework exactly once and drop the legacy
  profile; non-VentIQ configs gain nothing (test-enforced plus the
  non-VentIQ regression compile targets). No
  `config/webflash-builds.json` row, channel, version or artifact name
  changed; nothing in SOT, WebFlash, Shopify, provisioning or
  commercial state is touched.
* **Compile/simulation proof recorded separately from hardware proof** —
  the representative compile lane covers Release-One VentIQ+RoomIQ, the
  USB VentIQ bundle, the VentIQ LED preview bundle and the non-VentIQ
  regression targets; 40 deterministic simulation scenarios cover
  startup, warm-up, shower start/end/timeout, clearing, damp/mould
  accumulation and freezing, odour, air-quality escalation, priority
  ordering, manual actions, staleness, degraded service, recovery and
  invalid values. None of this is hardware, bench, compliance or
  commercial proof.

Follow-ups created by this work item (tracked, not started):
`VENTIQ-FRAMEWORK-BENCH-001` physical validation via the results-free
checklist; `VENTIQ-HW-DRIFT-001` (land the S360-211 BOM/CPL/board-photo
evidence, then decide with owner sign-off whether the drifted SHT4x/BMP390
drivers leave the board package — and what happens to the pressure
compatibility entity — or a hardware revision adds the parts; also owns
the matching feature-entity-matrix CONFIRM-flag closures);
`VENTIQ-RELAY-POPULATION-001` (fan-relay stage population/DNP evidence,
drive-signal source, COMPLIANCE-001 linkage for anything mains-facing);
`VENTIQ-SKU-LABEL-001` (the `S360-BATH-B` "AirIQ Module SKU" diagnostic
label vs the canonical S360-211 SKU — a board-layer published-entity
change needing its own compatibility decision); customer threshold tuning
from bench + customer feedback; a possible presence-aware ventilation
refinement (deliberately not consumed in this slice). The `J1`/`J9`
connector identity stays with S360-100-BENCH-001; the HW-007 doc's stale
schematic-status caveat stays with the hardware-doc chain. SOT
programme-status propagation (VentIQ software foundation implemented) is
an owner action in SOT, in a separate PR — never bundled here.

---

## 18. Blower framework (BLOWER-FRAMEWORK-001)

**Status: software foundation implemented via the BLOWER-FRAMEWORK-001 PR —
config-structure and native-simulation proof only; physical blower validation
pending (`BLOWER-FRAMEWORK-BENCH-001`, checklist at
[`docs/hardware/blower-framework-bench-checklist.md`](hardware/blower-framework-bench-checklist.md));
anti-short-cycle tuning pending; no SOT, WebFlash, release or commercial state
change. The blower is a fan output and ships COMPILE-ONLY — the *Fans are never
stable* standing gate applies (no stable claim).**

Customer-focused blower experience for the Sense360 Core's dedicated on-board
FAN net (schematic `IO21` → `Q4` SI2302S → `J13`, a two-wire binary 5 V blower
output): **Blower Mode** (Off / Auto / On, **default Auto**) as the authoritative
control, **Blower Auto Trigger** (Ventilate now / Ventilate soon), and a
read-only **Blower** state (no customer toggle — nothing contradicts the mode).
In Auto the blower follows the canonical AirIQ ventilation demand
(AIRIQ-FRAMEWORK-001) through a timing state machine (minimum-on, post-demand
purge, minimum-off restart lockout). Canonical doc:
[`docs/architecture/sense360-blower-framework.md`](architecture/sense360-blower-framework.md);
contract tests: [`tests/test_blower_framework.py`](../tests/test_blower_framework.py);
deterministic simulation:
[`tests/unit/test_blower_controller.cpp`](../tests/unit/test_blower_controller.cpp)
+ [`tests/unit/test_blower_airiq_coexist.cpp`](../tests/unit/test_blower_airiq_coexist.cpp)
over the shared engine
[`include/sense360/blower_controller.h`](../include/sense360/blower_controller.h)
(the same header production YAML compiles — no drift-prone second
implementation).

Scope facts (do not overclaim):

* **Hardware contract** — the blower is the Core's own `FAN` net (`IO21` → `Q4`
  SI2302S → `J13`), NOT a fan-driver module (no S360-311/312/310/320 SKU). J13
  is a two-wire binary 5 V output with **no** tach / speed-PWM / current /
  airflow / rotation feedback, so the framework commands only on/off and claims
  none. `GPIO46` (`GP_Fan_Status_Led`) is a Core status indicator and is never
  rotation feedback; the generic `GPIO3` relay (`J4`) is a separate control the
  blower never drives.
* **Optional AirIQ input** — the AirIQ air-quality service is the demand
  producer but not a hard dependency. `blower_has_airiq` (default `"false"`)
  is read through the shared engine singleton
  `sense360::airiq::global_engine().recommendation()` (never a hard `id()`; no
  duplicated pollutant thresholds). Without AirIQ, Auto has no actionable demand
  and the blower stays off; a missing / initialising / unavailable demand is
  UNKNOWN and never starts a stopped blower (fail-safe).
* **Auto timing state machine** — provisional `blower_min_on_ms` (60 s),
  `blower_purge_ms` (120 s), `blower_min_off_ms` (60 s): a cleared/stale demand
  triggers minimum-run completion + a post-demand purge before stopping, then a
  minimum-off restart lockout; the first start is never delayed. Rollover-safe
  timing. Values are software placeholders pending bench validation.
* **Gate posture** — the blower is a fan output and stays **compile-only** under
  the *Fans are never stable* gate: no `config/webflash-builds.json` row, no
  artifact, never stable / preview / customer-default / buyable / kit-exposed,
  not in `release_one_required_configs`. Release-One (`Ceiling-POE-VentIQ-RoomIQ`)
  is unchanged. Representative compile-only fixture:
  `products/sense360-core-ceiling-airiq-blower.yaml` (config string
  `Ceiling-Core-AirIQ-Blower`), cataloged `status: compile-only`,
  `webflash_build_matrix: false`, registered in
  `config/compile-only-targets.json` (`compile_validation_status: pending-ci`;
  esphome is not installed in the authoring environment, so a hosted CI
  `--compile` run is owed and no compile is fabricated).
* **Proof recorded separately from hardware proof** — the blower controller
  logic and the `blower_controller.h` + `airiq_engine.h` demand bridge are
  proven by the native C++ suite (21 controller scenarios incl. the full purge /
  timing state machine + millis rollover, plus the coexistence / enum-contract
  pin); `tests/validate_configs.py` passes on the fixture and packages. None of
  this is hardware, bench, airflow, compliance or commercial proof.

---

## Channel-tier policy (RELEASE-PREVIEW-ALL-PRODUCTS-001)

Preview eligibility is now open to **every buildable target**. The channel-tier
policy (stable / preview / advanced-preview), its guardrails, and the
preview-release eligibility matrix live in
[`docs/release-channel-policy.md` (archived)](archive-index.md) +
[`config/release-channel-policy.json`](../config/release-channel-policy.json).
Key rule: lack of hardware proof blocks **stable only** — it does not block
preview artifact publication. LED stays preview (no LED-stable claim) and
FanTRIAC is advanced-preview only (never stable, never recommended, never
default, mains-risk warning required). This is docs/config only: it adds no
`config/webflash-builds.json` rows and publishes no artifacts.

### Concrete preview targets + delivery lanes (RELEASE-PREVIEW-WEBFLASH-ALL-BUILDABLE-001)

The concrete preview target manifest
([`config/preview-release-targets.json`](../config/preview-release-targets.json),
doc [`docs/preview-release-targets.md` (archived)](archive-index.md)) now aligns
with the policy so that **every buildable product is a preview /
advanced-preview release target**, via three delivery lanes:

- **`webflash`** — SELV PoE targets only; the sole lane that can enter
  `config/webflash-builds.json` (unchanged: still just the two builds in §1,
  `Ceiling-POE-VentIQ-RoomIQ` stable + `Ceiling-POE-VentIQ-RoomIQ-LED` preview).
- **`manual-preview`** — `FanRelay` / `FanPWM` / `FanDAC`: releasable preview
  artifacts via the manual lane (§5.x). They stay `hardware-pending`, excluded
  from WebFlash / `config/webflash-builds.json` (fan-token guardrail), with no
  measured current/thermal and `rpm_supported: false` for FanPWM — but they are
  no longer framed as "not releasable". WebFlash import is a gated follow-up.
- **`advanced-manual-preview`** — `FanTRIAC`: advanced-preview only, no longer
  "blocked from preview"; only the `HW-005` buildability blocker stops a cut.

This is docs/config only. It flips no catalog status, marks nothing stable
(LED stays preview — **no LED-stable claim**), claims no hardware / bench /
compliance / verified-schematic evidence, adds no `config/webflash-builds.json`
row, and does not touch the WebFlash repo. S360-410 remains unresolved /
`cataloged_unverified` (**not verified**).

### Hardware blockers are stable-only for preview (RELEASE-PREVIEW-UNBLOCK-ALL-BUNDLES-001)

`RELEASE-PREVIEW-UNBLOCK-ALL-BUNDLES-001` makes the "lack of hardware proof
blocks **stable only**" rule machine-checkable per target. Every row of the
preview-release matrix and every concrete target now carries explicit
`preview_allowed` / `preview_warning_required` / `blocker_is_stable_only` flags:
`preview_allowed` is `true` for **every buildable product** (fan-control and
TRIAC included), and `blocker_is_stable_only` is `true` for every hardware /
bench / compliance / commercial blocker. **TRIAC** is the lone exception
(`blocker_is_stable_only: false`) because `HW-005` is a genuine *buildability*
blocker — `hardware_proof_blocks_preview: false`,
`preview_cut_gated_by_buildability: true` — and it stays **advanced-manual-preview
only** (never stable / recommended / default, mains-risk warning required, no
compliance claim). Fan drivers stay `manual-preview` only. **Simple install
stays the stable Bathroom PoE build only** (`Ceiling-POE-VentIQ-RoomIQ`), the
candidate room bundles stay **hidden / not buyable**, and **no stable / full
release unblock happens**. Docs/config only: publishes no firmware, adds no
`config/webflash-builds.json` row, flips no catalog status, and does not touch
the WebFlash repo. Guarded by
[`tests/test_release_preview_unblock_all_bundles.py`](../tests/test_release_preview_unblock_all_bundles.py).

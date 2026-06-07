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

Four items are genuinely open. The first two are **off-agent** gates (hardware
bench / mains sign-off); the last two are the remaining security-audit findings
from [`security.md`](security.md).

1. **`PACKAGE-TRIAC-001` — FanTRIAC operator bench (off-agent; PENDING).**
   The FanTRIAC gate/zero-cross mapping is schematic-verified — gate `GPIO14`
   = `TRI_GPIO1` → U1 MOC3023M; zero-cross `GPIO13` = `TRI_GPIO2` → OK1 EL814
   (`TRIAC-PINMAP-CORRECT-001`, traced from `S360-100-R4` + `S360-320-R4`), and
   the composition compiles. The remaining step is the real-mains-load operator
   bench (gate firing / zero-cross detection / timing / waveform / thermal +
   attestation), run by flashing the composition locally onto `S360-100-R4` +
   `S360-320-R4` — **no WebFlash publish is required to run it**. The proof
   container is [`docs/package-triac-001-operator-bench-proof.md`](docs/package-triac-001-operator-bench-proof.md).
   `PACKAGE-TRIAC-001-PARAMS` (#738, open, human-review) folded the
   bench-confirmed output parameters into
   [`packages/expansions/fan_triac.yaml`](packages/expansions/fan_triac.yaml)
   (`zero_cross_pin` `inverted: true`, `method: leading`,
   `fan_triac_min_power: "15"`) and recorded Steps A, B, C, E as **PASS** on the
   real Manrose fan motor; **Step F (boot/stability), the full-composition
   re-confirm, and the signed operator attestation are still outstanding**, so
   `PACKAGE-TRIAC-001` is **not** cleared and the proof stays **PENDING**. A PASS
   clears only the `PACKAGE-TRIAC-001` half (human-reviewed); `COMPLIANCE-001`
   stays separate. `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays
   `status: blocked` throughout — never stable, recommended, default, buyable, or
   WebFlash-exposed.
   - **`TRIAC-PUBLISH-ADVANCED-PREVIEW-001` stays BLOCKED** behind
     `PACKAGE-TRIAC-001` **and** `COMPLIANCE-001`. No FanTRIAC `.bin` is cut and
     no preview / advanced-preview row is added until both clear. Downstream
     `WF-IMPORT-TRIAC-001` stays blocked behind it. **Do NOT auto-merge** any
     FanTRIAC pin / blocker / status change — human-review only.

2. **`COMPLIANCE-001` — mains-voltage electrical-safety sign-off (off-agent).**
   The mains-voltage sign-off for the S360-320 TRIAC path (isolation / creepage
   / clearance / EMI / thermal). Independent of the bench; both must clear before
   any FanTRIAC publish. No code or config change is owed in this repo to "do"
   this — it is an external sign-off gate.

3. **`SEC-ESP-CHECKSUM-SIGNING-001` (security audit finding #3).** Release
   checksums are not signed. Sign them (cosign keyless preferred) so the
   published `checksums-sha256.txt` is verifiable. See
   [`security.md`](security.md) §3.

4. **`SEC-ESP-BUILD-GATES-001` (security audit findings #4 + #5).** Add two
   build gates: (#4) fail the build if the placeholder `api_encryption_key` would
   ship, and (#5) validate the generated `manifest.json` JSON before upload. See
   [`security.md`](security.md) §4–§5.

The remaining security-audit item, finding #6 (`check-yaml --unsafe` in
pre-commit), is **accepted** — no action queued.

---

## Standing invariants (do not regress)

These hold across every PR; the preview-release program below did **not** change
any of them.

* **Production stable Release-One is unchanged.** Config string
  `Ceiling-POE-VentIQ-RoomIQ`, artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, launch shop SKU
  **`S360-KIT-BATH-P`**. Simple install resolves to the stable Bathroom PoE
  build only; candidate / room bundles stay **hidden / not buyable**.
* **FanTRIAC stays blocked.** `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` is
  `status: blocked` (`blocker: PACKAGE-TRIAC-001 + COMPLIANCE-001`,
  `webflash_build_matrix: false`). HW-005 buildability was resolved by
  `TRIAC-PINMAP-CORRECT-001`, but no `.bin` is cut, it is not in
  `config/webflash-builds.json`, and it is never stable / recommended / default /
  buyable / WebFlash-exposed. The publish gate is a `PACKAGE-TRIAC-001` **AND**
  `COMPLIANCE-001` gate, **not** an acknowledgement gate.
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

**FanTRIAC preview work** must remain its own separate track and is **not**
WebFlash-import eligible: it stays build-blocked under `HW-005`
(advanced-manual-preview, mains-voltage) plus `COMPLIANCE-001`, owned by the
dedicated TRIAC track above. No TRIAC row is added to `config/webflash-builds.json`.

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

# WebFlash Drift Audit (WEBFLASH-DRIFT-001)

> **⚠️ Superseded for current-state status by [`docs/sense360-roadmap-status.md`](sense360-roadmap-status.md) (DOCS-CONSOLIDATION-ROADMAP-001).**
> For the canonical, up-to-date repo status / roadmap / blocker / upcoming-PR view —
> including release targets, bundle SKUs, board SKUs, WebFlash status, the S360-410 PoE
> blocker, the FanPWM native-path status, and LED preview status — see the canonical doc.
> The content below is retained as historical / provenance detail and is **not** the
> current-state source of truth.


**Audit id:** `WEBFLASH-DRIFT-001`
**Date:** 2026-05-26
**Scope repo:** `sense360store/esphome-public` (primary — verified this session)
**Companion repo:** `sense360store/WebFlash` (read-only target — **not directly
accessible this session**; see §0 Provenance)
**Type:** Audit / docs only. This PR makes **no** product, package,
config-behaviour, workflow, firmware, or WebFlash edit. It adds **no** WebFlash
wrapper, flips **no** `webflash_build_matrix`, adds **no** `artifact_name` or
release artifact, and exposes **no** Relay/DAC/PWM/TRIAC to WebFlash.

This document is the standing output of the cross-repo drift audit requested
before the Relay / DAC / PWM WebFlash-exposure work begins. It compares the
**esphome-public side of the WebFlash contract** (verified this session)
against the **WebFlash side** (recorded from prior in-repo readiness work and a
Drive planning artifact, both cited with provenance), classifies each axis, and
queues the recommended follow-up PRs. It does **not** flip any readiness gate
and makes **no** WebFlash-import / release / compliance / hardware-stable /
security clean-bill claim.

---

## 0. Methodology, provenance, and access limits

**What was verified directly this session (esphome-public):**

1. `config/product-catalog.json`, `config/webflash-builds.json`,
   `config/webflash-compatibility.json`, `config/firmware-combination-matrix.json`,
   `config/compile-only-targets.json`.
2. `products/**` and `products/webflash/**` (wrapper inventory).
3. `docs/webflash-contract.md` (the repo-local compatibility contract that names
   the WebFlash-side files this repo must satisfy).
4. The three readiness matrices and `docs/repo-freshness-roadmap-audit.md`.
5. The full validator / test suite (see §7).

**WebFlash repo access — limit (not a confirmed drift).** This session's GitHub
access is scoped to `sense360store/esphome-public` and `sense360store/esphome`
only. A direct read of `sense360store/WebFlash` returned **access denied**, and
there is no local WebFlash checkout (the second local clone `/home/user/esphome`
is an unrelated single-device config repo). **The WebFlash repo could not be
re-verified live this session.** Where a WebFlash-side value is asserted below it
is **prior-recorded** evidence, not a fresh read, and is labelled as such.

**Prior-recorded WebFlash evidence (provenance).** The WebFlash-side facts in
this audit are quoted from the in-repo record produced by
`WEBFLASH-RELAY-001-READINESS-REFRESH` (PR #565, 2026-05-22), which *did* have
read-only WebFlash access and recorded the WebFlash repo posture verbatim in
[`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md)
(§Relay / S360-310 WebFlash posture, "WebFlash repo posture (read-only review)")
and in [`UPCOMING_PR.md`](../UPCOMING_PR.md) (Cross-repo dependencies →
`WF-IMPORT-RELAY-001`). These are treated as **prior-recorded (2026-05-22), not
re-verified 2026-05-26**.

**Drive planning evidence (provenance).** A Drive planning spreadsheet
**"Current PRs.xlsx"** (file id `13Ed_JUlmIX5prHdVyoYoVr6Y3i1EOyX5`, owner
`neilmcrae@googlemail.com`, modified 2026-05-16) enumerates the WebFlash + 
esphome-public PR roadmap and references WebFlash-side concepts
(`firmware/sources.json`, a "current 3-build manifest", product-catalog fixture,
import-readiness validator, the `WEBFLASH-GAP-001 → RELEASE-GAP-001 →
WF-IMPORT-GAP-001` gate chain, and `WF-WIZARD-AVAIL-001` availability gating). It
is **planning intent**, not an export of the WebFlash repo, and is used only as
corroborating provenance — never as a substitute for the WebFlash repo state.

**No fabrication.** No WebFlash repo file content is invented. Axes that could
not be confirmed from either esphome-public (direct) or the prior-recorded /
Drive evidence (provenance) are marked `NEEDS-OPERATOR-INPUT`, and the
unavailability of live WebFlash tooling is recorded as `NEEDS-TOOLING`.

---

## 1. esphome-public WebFlash surface (verified this session)

WebFlash-shippable entries (`webflash_build_matrix: true`) — exactly **2**, both
in [`config/webflash-builds.json`](../config/webflash-builds.json):

| `config_string` | Catalog status | Channel | Wrapper | `artifact_name` |
|---|---|---|---|---|
| `Ceiling-POE-VentIQ-RoomIQ` | `production` | `stable` | `products/webflash/ceiling-poe-ventiq-roomiq.yaml` | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` |
| `Ceiling-POE-VentIQ-RoomIQ-LED` | `preview` | `preview` | `products/webflash/ceiling-poe-ventiq-roomiq-led.yaml` | `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` |

Fan-family entries — all **not** WebFlash-shippable (`webflash_build_matrix:
false`, no `artifact_name`, no build-matrix row):

| `config_string` | Catalog status | Wrapper | Compile evidence (`config/compile-only-targets.json`) |
|---|---|---|---|
| `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` | `blocked` (`HW-005`) | `products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml` (**blocked reference, not built**) | n/a (package missing) |
| `Ceiling-POE-VentIQ-FanRelay-RoomIQ` | `hardware-pending` | none | compile-only target present (`FW-COMPILE-RELAY-001`); **no `compile_validation_status` field set** |
| `Ceiling-POE-FanDAC` | `hardware-pending` | none | `compile_validation_status: validated-full-compile` (run `26364679370`) |
| `Ceiling-POE-FanPWM` | `hardware-pending` | none | `compile_validation_status: validated-full-compile` (run `26414398902`), `rpm_supported: false` |

Grammar / contract (`config/webflash-compatibility.json` +
`docs/webflash-contract.md`):

- `canonical_modules` reserves `FanRelay`, `FanPWM`, `FanDAC`, `FanTRIAC`, `LED`
  — **grammar reservation only**; reservation does not imply exposure.
- `artifact_pattern`: `Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin`.
- `allowed_channels`: `stable, beta, preview, dev, rescue`; production = `stable`;
  `rescue_config_string`: `Rescue`.
- `release_one_required_configs`: `["Ceiling-POE-VentIQ-RoomIQ"]`.
- `rules`: `fandac_conflicts_with_airiq: true`; fan variants firmware-distinct;
  AirIQ↔VentIQ mutually exclusive.
- **No `firmware/sources.json`, no `manifest.json`, no `firmware/**` directory
  exists in esphome-public** — these are WebFlash-owned by the contract
  (`docs/webflash-contract.md` §7: WebFlash generates `manifest.json` /
  `firmware-N.json` from the assets it pulls in).

---

## 2. WebFlash-side state (prior-recorded 2026-05-22; not re-verified this session)

Recorded by `WEBFLASH-RELAY-001-READINESS-REFRESH` (PR #565) from a read-only
WebFlash review:

| WebFlash artifact | Recorded value (2026-05-22) |
|---|---|
| `manifest.json` | **3 live builds**: Release-One (`Ceiling-POE-VentIQ-RoomIQ` v1.0.0 stable), LED preview (`Ceiling-POE-VentIQ-RoomIQ-LED` v1.0.0 preview), and **Rescue**. No FanRelay build. |
| `firmware/sources.json` | No FanRelay source declaration (Release-One + LED only). |
| `REQUIRED_CONFIGS` | `["Ceiling-POE-VentIQ-RoomIQ", "Rescue"]`. |
| `scripts/data/kits.json` | Release-One-only. |
| `scripts/utils/module-availability.js` | Sense360 Relay (`S360-310`) classified `design-pending`. (PWM / DAC / TRIAC classifications **not recorded** in this snapshot.) |
| `scripts/data/kit-presets.js` | Stage 1 `S360-KIT-BATH-RELAY` preset `status: planned`, non-installable, `notAvailableReason: "Awaiting upstream RELEASE-RELAY-001 firmware import (WF-IMPORT-RELAY-001)."` |
| WebFlash `UPCOMING_PR.md` queue item 4 | `WF-IMPORT-RELAY-001` **blocked** behind upstream `RELEASE-RELAY-001`. |
| UI naming | "Fan relay control" (Step 4 module card, `WF-UX-007`); "Sense360 Bathroom Kit — Relay Fan Control" (Stage 1 preset, `WF-KIT-PRESETS-001`). |

**The "3-build manifest" planning signal is resolved.** The Drive roadmap's
"current 3-build manifest" matches the prior-recorded WebFlash `manifest.json`:
the 3rd build is **Rescue**, a WebFlash-owned recovery image. esphome-public's
`config/webflash-builds.json` declares **2** product builds and intentionally
does **not** carry a Rescue build (`Rescue` exists only as
`rescue_config_string` in `config/webflash-compatibility.json`). This is a
**by-design structural difference, not drift.**

---

## 3. Drift table

Status legend: `MATCH` (consistent; "prior-recorded" = matched against the
2026-05-22 WebFlash snapshot, not a live read this session); `DRIFT` (mismatch);
`MISSING-IN-WEBFLASH`; `MISSING-IN-ESPHOME-PUBLIC`; `INTENTIONALLY-BLOCKED`
(absent on both sides by design); `NEEDS-OPERATOR-INPUT` (cannot be confirmed
without live WebFlash access / operator evidence).

| # | Item | esphome-public source | WebFlash source | Status | Recommended follow-up |
|---|---|---|---|---|---|
| 1 | `config_string` — Release-One + LED | `webflash-builds.json` (2 builds) | `manifest.json` (prior-recorded: 2 product builds + Rescue) | **MATCH** (prior-recorded) | none; re-confirm in each `WEBFLASH-*-001-READINESS` |
| 2 | `Rescue` config | `webflash-compatibility.json` `rescue_config_string` only (not a buildable product) | `manifest.json` carries Rescue build; in `REQUIRED_CONFIGS` | **MATCH** (by design — WebFlash-owned recovery) | none (Rescue is WebFlash-owned) |
| 3 | `artifact_name` (the 2 shippable builds) | `webflash-builds.json` | `manifest.json` (prior-recorded carries both) | **MATCH** (prior-recorded) | none |
| 4 | `artifact_pattern` | `webflash-compatibility.json` `Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin` | WebFlash `gen-manifests.py` / `state.js` (**not inspected**) | **NEEDS-OPERATOR-INPUT** (prior-recorded artifact names conform) | `WEBFLASH-DRIFT-001` re-run with live WebFlash access |
| 5 | Config-string grammar / forbidden tokens / mutex rules | `webflash-compatibility.json` + `webflash-contract.md` | WebFlash `module-requirements.js` / `state.js` / `validate-naming-policy.js` (**not inspected**) | **NEEDS-OPERATOR-INPUT** | `WEBFLASH-DRIFT-001` re-run; or operator-attested diff |
| 6 | Manifest entries for FanRelay/DAC/PWM/TRIAC | absent (`build_matrix: false`) | `manifest.json` (prior-recorded): no Fan builds | **INTENTIONALLY-BLOCKED** (aligned) | `WEBFLASH-RELAY/DAC/PWM-001` (gated) |
| 7 | `firmware/sources.json` | not present (WebFlash-owned) | prior-recorded: Release-One + LED only, no Fan sources | **MATCH** (prior-recorded / by design) | none |
| 8 | `manifest.json` / `firmware-N.json` | not present (WebFlash-owned, contract §7) | prior-recorded: 3 builds | **MATCH** (by design) | none |
| 9 | WebFlash wrappers (`products/webflash/**`) | 3: RoomIQ, RoomIQ-LED, FanTRIAC (**blocked reference**) | `firmware/sources.json` maps RoomIQ + LED only (prior-recorded) | **MATCH** for the 2 active; FanTRIAC wrapper = **INTENTIONALLY-BLOCKED** (not built, not in WebFlash) | `WF-TRIAC-001` (gated on HW-005 + COMPLIANCE-001) |
| 10 | WebFlash-visible products | 2 (`webflash_build_matrix: true`) | 3 live (the 2 + Rescue) | **MATCH** (prior-recorded) | none |
| 11 | Channels | `stable, beta, preview, dev, rescue` | observed: stable / preview / rescue (prior-recorded) | **NEEDS-OPERATOR-INPUT** (full list not confirmed; observed subset consistent) | `WEBFLASH-DRIFT-001` re-run |
| 12 | `REQUIRED_CONFIGS` | `release_one_required_configs = ["Ceiling-POE-VentIQ-RoomIQ"]` | `["Ceiling-POE-VentIQ-RoomIQ", "Rescue"]` | **MATCH** (by design — Rescue WebFlash-owned) | none |
| 13 | Default / recommended posture | default kit `S360-KIT-BATH-POE` (Release-One); Relay/DAC/PWM/TRIAC not exposed | `kits.json` Release-One-only; `S360-KIT-BATH-RELAY` `planned` | **MATCH** (prior-recorded) | none |
| 14 | Product labels / naming | outcome-first naming policy | "Fan relay control" / "Sense360 Bathroom Kit — Relay Fan Control" | **MATCH** (prior-recorded; aligned) | none |
| 15 | Relay module availability | catalog `hardware-pending`; not WebFlash-exposed | `module-availability.js`: `S360-310` = `design-pending` | **MATCH** (prior-recorded; aligned) | none |
| 16 | PWM module availability | catalog `hardware-pending`; not WebFlash-exposed | `module-availability.js`: `S360-311` **not recorded** in any snapshot | **NEEDS-OPERATOR-INPUT** | `WEBFLASH-PWM-001-READINESS` should record it |
| 17 | DAC module availability | catalog `hardware-pending`; not WebFlash-exposed | `module-availability.js`: `S360-312` **not recorded** in any snapshot | **NEEDS-OPERATOR-INPUT** | `WEBFLASH-DAC-001-READINESS` should record it |
| 18 | Release / import readiness (Relay/DAC/PWM/TRIAC) | all blocked; no artifact; no import | `WF-IMPORT-RELAY-001` blocked behind `RELEASE-RELAY-001` | **INTENTIONALLY-BLOCKED** (aligned) | per-family `WEBFLASH-*` / `RELEASE-*` / `WF-IMPORT-*` chains |
| 19 | Stale Relay/DAC/PWM "blocked/missing" references in esphome-public | catalog + matrices consistently mark blocked / hardware-pending | n/a (intra-repo) | **MATCH** (internally consistent) | none |
| 20 | Stale "FanPWM package/product missing" references | `product-readiness-matrix.md` §FanPWM `**Status.**` line + "Product YAML action now: None" headline, and `webflash-exposure-readiness-matrix.md` PWM "Current state" opening, still read **"no product YAML / needs-package-reconciliation"** — superseded by their own 2026-05-26 PRODUCT-PWM-001 addenda but headline not refreshed (FanRelay/FanDAC headlines *were* refreshed) | n/a (intra-repo) | **DRIFT** (intra-repo headline staleness) | corrected in this PR by a dated drift-audit pointer; no config/test change |
| 21 | FanRelay full-compile status flag | `config/compile-only-targets.json` FanRelay target carries **no** `compile_validation_status` (DAC/PWM carry `validated-full-compile`); `repo-freshness-roadmap-audit.md` §4 narrates "full compile #579" | n/a (intra-repo) | **NEEDS-OPERATOR-INPUT** (narrative vs config flag gap) | optional `FW-COMPILE-RELAY-RESULT-001` / status-flag PR (config edit out of scope here) |
| 22 | Release-One + LED preview "unchanged" expectation | catalog + `webflash-builds.json` verbatim, untouched | `manifest.json`: Release-One stable + LED preview live (prior-recorded) | **MATCH** | none — must stay unchanged |

**No confirmed cross-repo product/import drift was found.** Every Relay/DAC/PWM/
TRIAC axis is `INTENTIONALLY-BLOCKED` (aligned-absent on both sides) or
`NEEDS-OPERATOR-INPUT` (unverifiable without live WebFlash access). The only
`DRIFT` rows are **intra-repo doc-headline staleness** (#20) and a **narrative
vs config-flag gap** (#21) — neither is a WebFlash mismatch, and neither blocks
the readiness chain. There is therefore **no `WEBFLASH-DRIFT-FIX-001` cross-repo
fix prerequisite**; the per-family readiness PRs may proceed in order.

---

## 4. Recommended next PRs

The drift audit confirms the existing follow-up ladder in the three matrices is
the correct next step. Recommended, in priority order:

1. **`WEBFLASH-RELAY-001-READINESS`** — docs-only re-evaluation of FanRelay
   WebFlash exposure now that `PRODUCT-RELAY-001` (PR #564) landed the product
   YAML. Re-confirm against live WebFlash (`firmware/sources.json`,
   `manifest.json`, `module-availability.js`, `kit-presets.js`) and decide the
   `WEBFLASH-RELAY-001` exposure shape (still gated on production-wide GPIO3
   strap-pin characterisation + installation / competent-person sign-off +
   WebFlash-side manual-warning UX). **Not** an exposure flip.
2. **`WEBFLASH-DAC-001-READINESS`** — docs-only re-evaluation of FanDAC
   (`validated-full-compile`, run `26364679370`). Record the WebFlash
   `module-availability.js` `S360-312` classification (drift row #17). Enforce
   the `FanDAC ↔ AirIQ` mutex. **Not** an exposure flip.
3. **`WEBFLASH-PWM-001-READINESS`** — docs-only re-evaluation of FanPWM
   (`validated-full-compile`, run `26414398902`, **no RPM**). Record the
   WebFlash `module-availability.js` `S360-311` classification (drift row #16).
   Bench gates (PWM polarity; current / thermal envelope) stay open. **Not** an
   exposure flip.

A dedicated **`WEBFLASH-DRIFT-FIX-001`** is **not required** for cross-repo
reasons (no confirmed cross-repo mismatch). The two intra-repo items (#20, #21)
are minor: #20 is corrected by the dated pointers added in this PR, and #21 is
an optional config-flag follow-up outside this docs-only audit's scope.

A future re-run of **`WEBFLASH-DRIFT-001`** with live WebFlash access should
close drift rows #4, #5, #11, #16, #17 (currently `NEEDS-OPERATOR-INPUT` /
`NEEDS-TOOLING`).

---

## 4.1 Follow-up resolution log (updated 2026-05-26 by `WEBFLASH-RELAY-001-READINESS`)

The docs-only `WEBFLASH-RELAY-001-READINESS` re-evaluation (this follow-up;
recorded in full in
[`webflash-exposure-readiness-matrix.md` §Relay / S360-310 WebFlash posture](webflash-exposure-readiness-matrix.md#relay--s360-310-webflash-posture))
resolves the FanRelay follow-up tracked by this audit:

- **Drift row #21 (FanRelay narrative-vs-config compile-flag gap) —
  RESOLVED as a docs clarification; no config edit.** The narrative
  correctly records the FanRelay full compile as green (run `26364679370`;
  the full-compile lane runs `esphome compile` against every
  [`config/compile-only-targets.json`](../config/compile-only-targets.json)
  target and fails on the first failure, so `success` proves all nine
  targets including FanRelay — FW-COMPILE-RELAY-FULL-RESULT-001 / PR #579).
  The config target deliberately carries **no** `compile_validation_status`
  field: `COMPILE-STATUS-FLAGS-001` (2026-05-24) explicitly left FanRelay
  unchanged while flipping only FanDAC. No doc stale-says the FanRelay
  compile is unvalidated, and no test asserts the flag's presence or
  absence, so this is **not** drift and **not** a WebFlash blocker — it is
  an optional, non-blocking config-completeness item. Adding the explicit
  flag (to match FanDAC / FanPWM `validated-full-compile`) remains a
  separate optional `FW-COMPILE-RELAY-RESULT-001` config-only PR;
  `WEBFLASH-RELAY-001-READINESS` is docs-only and does not touch `config/`.
- **WebFlash-side axes stay `NEEDS-TOOLING`.** A live re-read of
  `sense360store/WebFlash` was again **denied** this session (GitHub scope
  is `sense360store/esphome-public` + `sense360store/esphome` only), so
  drift rows #4, #5, #11, #16, #17 stay open and the FanRelay WebFlash
  import / module-availability / manifest axes remain prior-recorded
  (2026-05-22, PR #565), not re-verified. The recommended next Relay step
  is **`WEBFLASH-RELAY-LIVE-CHECK-001`** (or a `WEBFLASH-DRIFT-001` re-run)
  once read access is restored — **not** a `WEBFLASH-RELAY-002-WRAPPER-PLAN`
  slice, because non-WebFlash gates (compliance / mains-safety,
  production-wide `GPIO3` characterisation, competent-person sign-off) are
  not all clean.

This follow-up makes **no** config / product / package / WebFlash / build /
release / workflow / test edit and **no** WebFlash exposure / import /
release / compliance / hardware-stable claim.

---

## 4.2 Follow-up resolution log (updated 2026-05-26 by `WEBFLASH-DAC-001-READINESS`)

The docs-only `WEBFLASH-DAC-001-READINESS` re-evaluation (this follow-up;
recorded in full in
[`webflash-exposure-readiness-matrix.md` §DAC / S360-312 WebFlash posture](webflash-exposure-readiness-matrix.md#dac--s360-312-webflash-posture))
addresses the FanDAC follow-up tracked by this audit (recommended next PR
#2 in §4):

- **No FanDAC compile-flag gap (contrast with FanRelay drift row #21).**
  The FanDAC compile-only target in
  [`config/compile-only-targets.json`](../config/compile-only-targets.json)
  already carries `compile_validation_status: validated-full-compile` and
  `voltage_enum_fixed: true` (flipped by `COMPILE-STATUS-FLAGS-001` after
  run `26364679370`; the full-compile lane runs `esphome compile` against
  every target and fails on the first failure, so `success` proves all
  nine including FanDAC — FW-COMPILE-DAC-FULL-RESULT-001 / PR #580). So
  the narrative-vs-config gap that applied to FanRelay (#21) does **not**
  apply to FanDAC; the DAC compile-status posture is `CLOSED`, not drift.
- **Drift row #17 (DAC module availability) — stays open, `NEEDS-TOOLING`;
  cannot be recorded this PR.** The recommended follow-up for row #17 was
  that `WEBFLASH-DAC-001-READINESS` "should record" the WebFlash
  `scripts/utils/module-availability.js` `S360-312` classification. A live
  re-read of `sense360store/WebFlash` was again **denied** this session
  (GitHub scope is `sense360store/esphome-public` + `sense360store/esphome`
  only), so `S360-312` remains **not recorded** in any module-availability
  snapshot and the classification cannot be captured here without
  fabricating evidence. Row #17 therefore stays `NEEDS-TOOLING`, deferred
  to **`WEBFLASH-DAC-LIVE-CHECK-001`** (or a `WEBFLASH-DRIFT-001` re-run)
  once read access is restored — **not** a `WEBFLASH-DAC-002-WRAPPER-PLAN`
  slice, because non-WebFlash gates (the `J3` silkscreen transposition and
  Cloudlift S12 harness / product-bench caveats, compliance / safety
  sign-off) are not all clean.
- **`FanDAC ↔ AirIQ` mutex re-confirmed.** `fandac_conflicts_with_airiq:
  true` in
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json);
  no AirIQ-bearing FanDAC combination exists in
  [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json)
  (24 FanDAC config strings, 0 with an `AirIQ` token). The mutex is not
  relaxed.

This follow-up makes **no** config / product / package / WebFlash / build /
release / workflow / test edit and **no** WebFlash exposure / import /
release / compliance / hardware-stable claim, and **fabricates no**
WebFlash evidence.

---

## 4.3 Follow-up resolution log (updated 2026-05-26 by `WEBFLASH-PWM-001-READINESS`)

The docs-only `WEBFLASH-PWM-001-READINESS` re-evaluation (this follow-up;
recorded in full in
[`webflash-exposure-readiness-matrix.md` §PWM / S360-311 WebFlash posture](webflash-exposure-readiness-matrix.md#pwm--s360-311-webflash-posture))
addresses the FanPWM follow-up tracked by this audit (recommended next PR
#3 in §4):

- **No FanPWM compile-flag gap (contrast with FanRelay drift row #21).**
  The FanPWM compile-only target in
  [`config/compile-only-targets.json`](../config/compile-only-targets.json)
  already carries `compile_validation_status: validated-full-compile` and
  `rpm_supported: false` (run `26414398902`, `compile_mode=full`, 10
  targets, `success`; the full-compile lane runs `esphome compile`
  against every target and fails on the first failure, so `success`
  proves all ten including FanPWM — FW-COMPILE-PWM-RESULT-001 / PR #592).
  So the narrative-vs-config gap that applied to FanRelay (#21) does
  **not** apply to FanPWM; the PWM compile-status posture is `CLOSED`,
  not drift. The product YAML composition was further validated as a
  byte-equivalent package-set parity against that skeleton
  (FW-COMPILE-PWM-PRODUCT-001 / PR #594), though a live `esphome config`
  of the product YAML itself stays pending (`NEEDS-TOOLING`; ESPHome not
  present this session).
- **Drift row #16 (PWM module availability) — stays open, `NEEDS-TOOLING`;
  cannot be recorded this PR.** The recommended follow-up for row #16 was
  that `WEBFLASH-PWM-001-READINESS` "should record" the WebFlash
  `scripts/utils/module-availability.js` `S360-311` classification. A
  live re-read of `sense360store/WebFlash` was again **denied** this
  session (GitHub scope is `sense360store/esphome-public` +
  `sense360store/esphome` only), so `S360-311` remains **not recorded**
  in any module-availability snapshot and the classification cannot be
  captured here without fabricating evidence. Row #16 therefore stays
  `NEEDS-TOOLING`, deferred to **`WEBFLASH-PWM-LIVE-CHECK-001`** (or a
  `WEBFLASH-DRIFT-001` re-run) once read access is restored — **not** a
  `WEBFLASH-PWM-002-WRAPPER-PLAN` slice, because the non-WebFlash bench
  gates (PWM polarity; per-fan / aggregate current + thermal envelope;
  product bench, owned by `S360-311-BENCH-001`) are not clean.
- **Drift row #20 (stale "FanPWM package/product missing" headline) —
  already reconciled in-repo; re-confirmed here.** The
  `product-readiness-matrix.md` §FanPWM headline carries the dated
  `WEBFLASH-DRIFT-001` headline-reconciliation note and the compound
  `product-yaml-landed` + `validated-full-compile` status; the historical
  "no product YAML / needs-package-reconciliation" prose is explicitly
  retained for the audit trail only. This re-evaluation adds its own
  dated audit-log entry to that section and does **not** rewrite the
  historical prose.
- **RPM stays unsupported; `TachIO` / `GPIO16` reserved.** The PWM-drive-only
  package wires no `pulse_counter` and no per-fan / aggregate RPM (an
  SX1509 expander pin is compile-proven invalid for an ESPHome
  `pulse_counter`, PWM-SX1509-TACH-PROOF-001 / PR #589). No RPM is added
  or claimed.

This follow-up makes **no** config / product / package / WebFlash / build /
release / workflow / test edit and **no** WebFlash exposure / import /
release / compliance / hardware-stable / RPM-support claim, and
**fabricates no** WebFlash evidence.

---

## 4.4 Follow-up resolution log (updated 2026-05-27 by `WEBFLASH-LIVE-CHECK-001`)

The docs-only `WEBFLASH-LIVE-CHECK-001` re-check (this follow-up) is the
consolidated live-WebFlash re-run that drift rows #4, #5, #11, #16, #17 and the
per-family `WEBFLASH-{RELAY,DAC,PWM}-LIVE-CHECK-001` items all point to. It was
queued to re-read `sense360store/WebFlash` once access was restored and to
record the `S360-310` / `S360-311` / `S360-312` `module-availability.js`
classifications.

- **Live WebFlash read re-attempted this session — again denied.** Three
  read-only GitHub access methods were tried against `sense360store/WebFlash`
  this session (2026-05-27): the repo root (`get_file_contents /`),
  `scripts/utils/module-availability.js` directly, and a branch listing
  (`list_branches`). **All three returned access denied** — *"repository
  `sense360store/webflash` is not configured for this session. Allowed
  repositories: sense360store/esphome-public, sense360store/esphome."* The
  session GitHub scope is still `sense360store/esphome-public` +
  `sense360store/esphome` only, and there is no local WebFlash checkout (the
  second local clone `/home/user/esphome` is the unrelated single-device config
  repo). **The WebFlash repo could not be re-verified live this session.**
- **Drift rows #4, #5, #11, #16, #17 stay open (`NEEDS-TOOLING`).** No WebFlash
  source (`artifact_pattern` generator, grammar/naming validators, full channel
  list, `scripts/utils/module-availability.js`) could be inspected, so none of
  these axes can be closed. The `S360-310` classification stays **prior-recorded
  `design-pending`** (2026-05-22, PR #565), and `S360-311` / `S360-312` stay
  **not recorded in any module-availability snapshot**. No classification is
  captured here, because doing so without a live read would fabricate evidence.
- **esphome-public side re-verified fresh this session — unchanged, no drift.**
  Direct reads this session confirm the esphome-public WebFlash surface is
  exactly as recorded in §1: [`config/webflash-builds.json`](../config/webflash-builds.json)
  carries the same **2** builds (`Ceiling-POE-VentIQ-RoomIQ` / stable,
  `Ceiling-POE-VentIQ-RoomIQ-LED` / preview); [`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
  carries the same grammar (`artifact_pattern`
  `Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin`; `allowed_channels`
  `stable, beta, preview, dev, rescue`; `release_one_required_configs`
  `["Ceiling-POE-VentIQ-RoomIQ"]`; `fandac_conflicts_with_airiq: true`;
  `canonical_modules` reserves `FanRelay`/`FanPWM`/`FanDAC`/`FanTRIAC`/`LED`);
  [`config/product-catalog.json`](../config/product-catalog.json) keeps
  `Ceiling-POE-VentIQ-FanRelay-RoomIQ`, `Ceiling-POE-FanDAC`, and
  `Ceiling-POE-FanPWM` all `status: hardware-pending`,
  `webflash_build_matrix: false`, no `artifact_name`; the
  [`products/webflash/`](../products/webflash/) inventory is still the 3
  wrappers (RoomIQ, RoomIQ-LED, and the **blocked** FanTRIAC reference); and no
  `firmware/sources.json`, `manifest.json`, or `firmware/**` exists (these stay
  WebFlash-owned by the contract). The module-code mapping is confirmed in
  [`config/hardware-catalog.json`](../config/hardware-catalog.json): `S360-310`
  Sense360 Relay, `S360-311` Sense360 PWM, `S360-312` Sense360 DAC — all
  `schematic_status: cataloged_unverified`. **No esphome-public-side drift was
  introduced or found.**
- **Nothing flips; visible/hidden product lists unchanged.** WebFlash-visible
  products stay the 2 shippable builds; Relay/DAC/PWM/TRIAC stay
  not-exposed/blocked. No stale Relay/DAC/PWM "missing/blocked" reference was
  found in the configs this session (drift row #20 was already reconciled
  in-repo; drift row #21 is the unchanged optional config-flag item).
- **Recommended next step — operator/tooling remediation, then re-run.** The
  only way to close rows #4/#5/#11/#16/#17 is to grant this session read access
  to `sense360store/WebFlash` (or supply an operator-attested
  `module-availability.js` / `manifest.json` / `firmware/sources.json` /
  `kit-presets.js` snapshot), then re-run `WEBFLASH-LIVE-CHECK-001` (or a
  `WEBFLASH-DRIFT-001` re-run). This is **not** a wrapper-plan slice — the
  per-family non-WebFlash gates (Relay `GPIO3` + safety + competent-person;
  DAC `J3` / Cloudlift S12 bench; PWM polarity + current / thermal + product
  bench) are not all clean.

This follow-up makes **no** config / product / package / WebFlash / build /
release / workflow / test edit and **no** WebFlash exposure / import /
release / compliance / hardware-stable / RPM-support claim, and
**fabricates no** WebFlash evidence. It only **re-attempts** the live read and
records the (still-denied) outcome. Release-One and the LED preview are
unchanged.

---

## 5. Guardrails honoured / non-claims

This PR does **not** edit `products/**`, `products/webflash/**`,
`config/webflash-builds.json`, `firmware/**`, `manifest.json`,
`firmware/sources.json`, release artifacts, checksums, build-info manifests, any
WebFlash repo file, `.github/workflows/**`, `components/**`, or `include/**`. It
adds **no** WebFlash wrapper, flips **no** `webflash_build_matrix`, adds **no**
`artifact_name` or release artifact, and exposes **no** Relay/DAC/PWM/TRIAC to
WebFlash. It makes **no** WebFlash-import-readiness, release-readiness,
compliance-approval, hardware-stable-readiness, or security clean-bill claim, and
fabricates **no** WebFlash evidence. Release-One (`Ceiling-POE-VentIQ-RoomIQ` /
stable) and the LED preview (`Ceiling-POE-VentIQ-RoomIQ-LED` / preview) are
unchanged.

---

## 6. Validation evidence (run for this audit, 2026-05-26)

| Command | Result |
|---|---|
| `python3 tests/validate_configs.py` | ✅ 208 files checked, 0 failed |
| `python3 scripts/validate_compile_targets.py --metadata-only` | ✅ 10 targets, metadata passed |
| `python3 tests/test_product_catalog.py` | ✅ 31 tests OK |
| `python3 tests/test_firmware_combination_matrix.py` | ✅ 24 tests OK |
| `python3 tests/test_firmware_build_gap_report.py` | ✅ 27 tests OK |
| `python3 tests/validate_webflash_builds.py` | ✅ 2 builds checked, 0 failed |
| `python3 -m unittest discover -s tests -p "test_*.py"` | ✅ 756 tests OK (3 skipped) |
| `npm test` / `npm audit` (WebFlash tooling) | ⚠️ **NEEDS-TOOLING** — no Node project in esphome-public; WebFlash repo inaccessible this session |

---

## 7. See also

- [`docs/webflash-contract.md`](webflash-contract.md) — repo-local compatibility
  contract (names the WebFlash-side files this audit must check).
- [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md)
  — per-family WebFlash exposure posture; source of the prior-recorded WebFlash
  facts in §2.
- [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
  — per-family release-artifact posture.
- [`docs/product-readiness-matrix.md`](product-readiness-matrix.md) — per-family
  product-YAML posture.
- [`docs/repo-freshness-roadmap-audit.md`](repo-freshness-roadmap-audit.md) §3
  (cross-repo drift table) and §7 (follow-up PR queue).
- [`UPCOMING_PR.md`](../UPCOMING_PR.md) — Cross-repo dependencies
  (`WF-IMPORT-RELAY-001`).

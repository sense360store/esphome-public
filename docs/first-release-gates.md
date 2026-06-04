# First-Release Gates (PRE-HW-PREP-FIRST-RELEASE-GATES-001)

**Canonical id:** `PRE-HW-PREP-FIRST-RELEASE-GATES-001`
**Type:** Docs only. This document **promotes nothing, enables nothing, and
verifies nothing.** It does **not** change firmware behaviour, publish
firmware, edit `manifest.json` / [`firmware/sources.json`](../firmware/sources.json),
enable WebFlash, add an `artifact_name`, flip `webflash_build_matrix`,
promote any bundle, change [`config/webflash-builds.json`](../config/webflash-builds.json)
or any other `config/*.json`, mark `S360-410` verified, mark LED stable, or
mark any fan variant release-ready.

## Purpose and scope

This is the **single canonical first-release gate checklist** for
`sense360store/esphome-public`. It answers three questions in one place:

1. **What can ship now** as the current first-release path;
2. **What is blocked** (every other room bundle, fan variant, driver, and PSU);
   and
3. **What exact evidence is required** to unblock each blocked path, and which
   named follow-up PR / bench task owns that evidence.

It consolidates the first-release / expansion gate view that was previously
spread across the room-bundle release-handoff matrix, the roadmap/status doc,
the pre-hardware prep plan, and the per-board readiness docs. It **threads**
the existing facts from the sources of truth below; it does not invent or move
any of them. Where this doc and a source-of-truth file ever disagree, **the
source-of-truth file wins** and this doc is the one to fix.

### Headline

> **`S360-KIT-BATH-P` (Bathroom, stable) is published and live** as the current
> first-release path — it is the Release-One stable WebFlash build
> `Ceiling-POE-VentIQ-RoomIQ`, shipped as GitHub Release **`v1.0.0`**
> (2026-05-12) and imported/live in WebFlash. **The first stable release is no
> longer pending — `v1.0.0` is the current release path.** Any future publish
> must use a **new version** (e.g. `1.0.1` / `1.1.0`); `v1.0.0` is not
> re-published. See
> [`docs/first-release-publish-readiness.md`](first-release-publish-readiness.md).
>
> **Kitchen / Bedroom / Living / Corridor are not first-release eligible yet.**
> Each is a candidate behind named gates (S360-410 PoE evidence and/or the LED
> preview→stable gauntlet and/or the AirIQ sensor-stack evidence).
>
> **Fan-control variants are planning-only.** **Hardware bench tasks are
> future-only** — they cannot run until physical hardware / bench equipment
> exists, and none is run or claimed here.

### Sources of truth (do not duplicate, link instead)

| Layer | Source of truth |
|---|---|
| Canonical roadmap / status / blocker view | [`docs/sense360-roadmap-status.md`](sense360-roadmap-status.md) (`DOCS-CONSOLIDATION-ROADMAP-001`) |
| Pre-hardware room-bundle handoff matrix | [`docs/pre-hardware-room-bundle-release-handoff.md`](pre-hardware-room-bundle-release-handoff.md) (`PRE-HW-PREP-ROOM-BUNDLES-001`) |
| Pre-hardware design-readiness program | [`docs/pre-hardware-prep-plan.md`](pre-hardware-prep-plan.md) (`PRE-HARDWARE-PREP-PLAN-001`) |
| Shippable WebFlash builds | [`config/webflash-builds.json`](../config/webflash-builds.json) (validated by `tests/validate_webflash_builds.py`) |
| Room bundle SKUs | [`config/room-bundle-skus.json`](../config/room-bundle-skus.json) · [`docs/sense360-room-bundles.md`](sense360-room-bundles.md) |
| Room-bundle fan variants (preview bundle plan) | [`config/room-bundle-fan-variants.json`](../config/room-bundle-fan-variants.json) (`ROOM-BUNDLE-FAN-VARIANTS-002`) |
| Board / module catalog | [`config/hardware-catalog.json`](../config/hardware-catalog.json) · [`docs/hardware-catalog.md`](hardware-catalog.md) |
| Firmware combination matrix | [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json) |
| Board readiness / hardware evidence | [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md) (`HW-GAP-001`) |
| Promotion gates (preview→stable gauntlet) | [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md) (`RELEASE-006`) |
| S360-410 PoE evidence audit | [`docs/package-poe-410-001-audit.md`](package-poe-410-001-audit.md) · [`docs/package-poe-410-evidence-result.md`](package-poe-410-evidence-result.md) |
| Operator dry-run checklist (first stable release) | [`docs/first-release-dryrun-checklist.md`](first-release-dryrun-checklist.md) (`FIRST-RELEASE-DRYRUN-CHECKLIST-001`) |
| Detailed PR working queue | [`UPCOMING_PR.md`](../UPCOMING_PR.md) |

> **Operator dry-run.** To *rehearse* this first-release path end to end
> (release notes → build workflow → artifact naming → checksums) without
> publishing or changing WebFlash exposure, follow
> [`docs/first-release-dryrun-checklist.md`](first-release-dryrun-checklist.md)
> (`FIRST-RELEASE-DRYRUN-CHECKLIST-001`). This gates doc says **what** ships; the
> dry-run checklist says **how to rehearse** it safely.

> **Dry-run executed and PASSED (`FIRST-RELEASE-WORKFLOW-DRYRUN-001` →
> `FIRST-RELEASE-WORKFLOW-DRYRUN-CI-RESULT-001`).** The non-publishing dry-run
> lanes were run against the only eligible stable path (`S360-KIT-BATH-P` /
> `Ceiling-POE-VentIQ-RoomIQ` / `stable` / `1.0.0`): release-note generation +
> validation, the build workflow's `release-dry-run` job steps (planner +
> guardrail contract tests + no-side-effects assertion), and artifact-name
> assertion all **passed**, expected artifact
> `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, **no** publish / tag /
> `.bin` / checksum / `manifest.json` / `firmware/sources.json`. The hosted
> GitHub Actions dry-run has since been dispatched by an operator and **passed**
> — `Build & Release Firmware` → `Release Dry-Run (no publish)`,
> [run 26723839261](https://github.com/sense360store/esphome-public/actions/runs/26723839261/job/78755574773),
> commit `b2cc9fd5054f62c18b63230c2b380bc749abf2f0`, **no artifacts** (expected).
> Outcome: **`dry-run passed`** (first-release workflow dry-run: passed; hosted
> CI dry-run: passed) — this is **workflow confidence evidence**, a rehearsal of
> the release *workflow*, not a sign that `v1.0.0` is unpublished. The stable
> first release **`v1.0.0` is already published and live**; there is **no pending
> publish action** for it, and a *future* publish would be a separate human
> decision on a **new version** (e.g. `1.0.1` / `1.1.0`) with its own real
> changelog, optional external-component tag pin, publish-time checksums, and
> WebFlash handoff. The safe dry-run mode **already exists**
> (`RELEASE-WORKFLOW-DRYRUN-MODE-001`), so the conditional
> `FIRST-RELEASE-WORKFLOW-DRYRUN-MODE-001` is **not** opened. Full record:
> [`docs/first-release-dryrun-checklist.md`](first-release-dryrun-checklist.md)
> §11 (§11.8 for the hosted pass). This changes **no gate** in this doc.

---

## 1. Current shippable release (first-release path)

The shippable WebFlash build matrix is [`config/webflash-builds.json`](../config/webflash-builds.json)
(validated by `tests/validate_webflash_builds.py`). There are exactly **two**
WebFlash-exposed builds; only the **stable** one is the first-release path.

| Config string | Channel | Version | Artifact | Bundle | First-release? |
|---|---|---|---|---|---|
| `Ceiling-POE-VentIQ-RoomIQ` | **stable** | 1.0.0 | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` | `S360-KIT-BATH-P` (Bathroom) | **YES — published/live (`v1.0.0`)** |
| `Ceiling-POE-VentIQ-RoomIQ-LED` | **preview** | 1.0.0 | `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` | (none — LED variant) | No (preview channel only; LED preview-gated, §3 / §7) |

Release-One required configs (`config/webflash-compatibility.json` →
`release_one_required_configs`): **`Ceiling-POE-VentIQ-RoomIQ`** only.

**The Bathroom stable release is already published and live** as the current
first-release path (GitHub Release `v1.0.0`, 2026-05-12; imported/live in
WebFlash). No other config string is release-eligible today; nothing here is
promoted. A future publish would use a **new version**, not `v1.0.0`.

---

## 2. Blocked bundle expansions

The five canonical PoE room bundles from [`config/room-bundle-skus.json`](../config/room-bundle-skus.json).
**1 of 5 is first-release eligible today** (`S360-KIT-BATH-P`); the other four
are blocked candidates owned by named follow-ups.

| Bundle SKU | Room | Boards | Firmware config target | Status | First-release eligibility | Blocking gate(s) |
|---|---|---|---|---|---|---|
| `S360-KIT-BATH-P` | bathroom | S360-100/200/211/410 | `Ceiling-POE-VentIQ-RoomIQ` | `stable-release` (published/live, `v1.0.0`) | **ELIGIBLE — published/live** | None (the live stable build; ships under the preserved S360-410 PoE "schematic verification pending" caveat) |
| `S360-KIT-KITCHEN-P` | kitchen | S360-100/200/210/410 | `Ceiling-POE-AirIQ-RoomIQ` | `stable-candidate` (missing-product-yaml) | **NOT eligible** | AirIQ sensor-stack evidence (SPS30 / SGP41 / SCD41 / BMP390) **plus** the shared S360-410 PoE chain (§4) |
| `S360-KIT-LIVING-P` | living-room | S360-100/200/300/410 | `Ceiling-POE-RoomIQ-LED` | `preview-candidate` (missing-product-yaml) | **NOT eligible** | LED preview→stable gauntlet (§7) **plus** the shared S360-410 PoE chain (§4) |
| `S360-KIT-BEDROOM-P` | bedroom | S360-100/200/410 | `Ceiling-POE-RoomIQ` | `stable-candidate` (`blocked-hardware`) | **NOT eligible** | Shared S360-410 PoE chain alone (§4); RoomIQ-only top-level YAML is `blocked-hardware` on `PRODUCT-POE-410-001` |
| `S360-KIT-CORRIDOR-P` | corridor | S360-100/200/300/410 | `Ceiling-POE-RoomIQ-LED` | `preview-candidate` (missing-product-yaml) | **NOT eligible** | Same as `S360-KIT-LIVING-P` (shares board set + config target) until a corridor-specific config differentiates them |

**Kitchen / Bedroom / Living / Corridor are not first-release eligible yet.**
No `current_release_status` is changed; no candidate is promoted by this doc.

### 2.1 Fan-control variants (preview bundle plan — not first-release)

The fan-control variants in [`config/room-bundle-fan-variants.json`](../config/room-bundle-fan-variants.json)
(`ROOM-BUNDLE-FAN-VARIANTS-002`) are **Bathroom / Kitchen add-ons only**.
`-002` promotes them from planning to a **preview bundle plan**: a variant
**may** appear in the future WebFlash easy-mode bundle picker as an
Advanced-install-only, acknowledgement-gated **preview** (with a warning)
**only** when its full-composition firmware config is built. **None is
first-release**, none is stable, none is recommended / default, none is
buyable, and no fan bundle SKU is added to the base matrix. **Stable / full
release of every variant stays blocked** behind its hardware / bench-evidence /
compliance gate (§4 / §5 / §8); preview eligibility does not weaken that gate.

| Variant SKU | Base bundle | Fan driver | Control | Firmware config today | WebFlash easy-mode | Stable |
|---|---|---|---|---|---|---|
| `S360-KIT-BATH-P-REL` | `S360-KIT-BATH-P` | S360-310 | relay | built + published preview | preview-eligible (ack-gated) | blocked |
| `S360-KIT-BATH-P-TRIAC` | `S360-KIT-BATH-P` | S360-320 | triac | build-blocked (HW-005) | advanced / manual only; not yet exposable | blocked |
| `S360-KIT-BATH-P-PWM` | `S360-KIT-BATH-P` | S360-311 | pwm | buildable-preview-compile-validated (ROOM-BUNDLE-FAN-CONFIGS-001; compile recorded by ROOM-BUNDLE-FAN-COMPILE-RESULTS-001, run 26913592989) | not eligible (compile-validated, not published) | blocked |
| `S360-KIT-BATH-P-DAC` | `S360-KIT-BATH-P` | S360-312 | 0-10V | buildable-preview-compile-validated; requires FanDAC IC2 → 0x5A | not eligible (compile-validated; advanced / manual switch) | blocked |
| `S360-KIT-KITCHEN-P-REL` | `S360-KIT-KITCHEN-P` | S360-310 | relay | buildable-preview-compile-validated | not eligible (compile-validated, not published) | blocked |
| `S360-KIT-KITCHEN-P-DAC` | `S360-KIT-KITCHEN-P` | S360-312 | 0-10V | buildable-preview-compile-validated; requires FanDAC IC2 → 0x5A; WebFlash-grammar-excluded | not eligible (compile-validated; mutex) | blocked |
| `S360-KIT-KITCHEN-P-PWM` | `S360-KIT-KITCHEN-P` | S360-311 | pwm | buildable-preview-compile-validated (policy-gated) | not eligible (compile-validated, not published) | blocked |

Bathroom TRIAC (S360-320) is an **advanced / manual-warning** preview only,
build-blocked by `HW-005`, never recommended / default / stable, with no
safety / compliance proof claimed. **Kitchen has no TRIAC variant.** No
Corridor / Living / Bedroom fan variant exists.

The two FanDAC variants (`S360-KIT-BATH-P-DAC` / `S360-KIT-KITCHEN-P-DAC`)
additionally require the FanDAC IC2 GP8403 to be relocated to `0x5A` (off the
`0x59` default that collides with the VentIQ/AirIQ SGP41). That DIP-switch →
I²C-address mapping is **required but not bench-verified**; the
`FANDAC-I2C-ADDR-001` bench checklist and evidence template own that gate at
[`docs/hardware/fandac-i2c-address-verification.md`](hardware/fandac-i2c-address-verification.md).
The two FanDAC configs compiled **with the `0x5A` override applied**, which is a
compile-time configuration only and does **not** bench-verify the physical
switch; `FANDAC-I2C-ADDR-001` stays **pending**.

All five fan-bundle configs above are now **compile-validated** (not just
compile-pending): `ROOM-BUNDLE-FAN-COMPILE-RESULTS-001` recorded a successful
hosted full ESPHome compile (Compile-only Firmware Validation, run
[`26913592989`](https://github.com/sense360store/esphome-public/actions/runs/26913592989),
ref `main`, 2026-06-04, ESPHome `2026.4.5`). A green compile is **firmware-build
proof only** — it does not change any first-release / stable / preview-exposure /
hardware / bench / compliance gate above. See
[`docs/room-bundle-fan-compile-results.md`](room-bundle-fan-compile-results.md).

---

## 3. Hardware blockers

Per-board catalog state from [`config/hardware-catalog.json`](../config/hardware-catalog.json)
(`schematic_status` is authoritative) and the design-readiness annotations from
[`docs/pre-hardware-prep-plan.md`](pre-hardware-prep-plan.md). `design-complete`
is a **prose annotation, never a JSON field**, and is explicitly **NOT**
`verified`.

| Board | Friendly | `schematic_status` | Design-readiness | Hardware blocker |
|---|---|---|---|---|
| S360-300 | Sense360 LED | `verified` | board verified; LED **product** preview-only | LED **stable** promotion gated by the preview→stable gauntlet (§7), not by the board schematic. **No LED-stable claim is made.** |
| S360-310 | Sense360 Relay | `cataloged_unverified` | SELV logic authorable; mains load-side **ARTIFACT-BLOCKED** | Mains contact-rating + load-side clearance/creepage review (needs gerbers + BOM); SELV switching bench |
| S360-311 | Sense360 PWM | `cataloged_unverified` | **design-complete** (compile-proven, bench-pending) | Current / thermal **not measured**; per-fan RPM not measured (`rpm_supported` stays `false`); `J3` silkscreen / `J6`↔`J3` harness owed to `HW-PINMAP-311` |
| S360-312 | Sense360 DAC | `cataloged_unverified` | **design-complete** (compile green, bench-pending) | 0-10 V output, GP8403 detection / I²C address, range/calibration, current, thermal, harness/silkscreen all owed to `S360-312-DAC-BENCH-001` (no physical board exists) |
| S360-320 | Sense360 TRIAC | `cataloged_unverified` | **BLOCKED (HW-005)** | `ac_dimmer` needs direct interrupt-capable ESP32 gate/zero-cross GPIO (placeholders provably wrong; I²C/SX1509 cannot meet timing); mains review + COMPLIANCE-001 |
| S360-400 | Sense360 240v PSU | `cataloged_unverified` | passive PSU; design-readiness reduces to D1 + D6 + D-Review | Mains isolation creepage/clearance (gerbers + BOM); Hi-pot / X-Y-cap class; COMPLIANCE-001; converter identity (`HLK-?`) |
| S360-410 | Sense360 PoE PSU | `cataloged_unverified` | passive PSU; design-readiness reduces to D1 + D6 + D-Review | **UNRESOLVED** — PoE link-up / load / inrush / thermal / EMI-EMC bench; isolation Hi-pot; isolation creepage/clearance (gerbers + BOM); J2-harness / silkscreen; PCB source. **S360-410 is NOT verified.** |

### 3.1 S360-410 PoE PSU — the shared blocker

**S360-410 remains `cataloged_unverified` — NOT verified, UNRESOLVED.** Per
[`docs/package-poe-410-001-audit.md`](package-poe-410-001-audit.md) and
[`docs/package-poe-410-evidence-result.md`](package-poe-410-evidence-result.md)
the bench (PoE link-up / load / inrush / thermal / EMI-EMC), isolation/safety
(Hi-pot), connector-silkscreen, J2-harness, and PCB-source evidence classes are
all still **missing**. S360-410 is the **shared blocker under every non-Bathroom
bundle**; the already-shipping `S360-KIT-BATH-P` ships under the preserved PoE
caveat and is unaffected. **No S360-410 verified claim is made anywhere in this
repo.**

---

## 4. Firmware blockers

Firmware config-target state from [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json).

| Config / driver | State | Firmware blocker |
|---|---|---|
| `Ceiling-POE-VentIQ-RoomIQ` | **stable** (shipped) | None — first-release path |
| `Ceiling-POE-VentIQ-RoomIQ-LED` | **preview** (shipped) | LED preview-gated (§7) |
| `Ceiling-POE-AirIQ-RoomIQ` (Kitchen) | compile-only skeleton | No top-level product YAML / catalog row / full compile yet; owned by `STABLE-TARGET-AIRIQ-001` |
| `Ceiling-POE-RoomIQ-LED` (Living / Corridor) | missing-product-yaml | No product YAML; LED preview-gated |
| `Ceiling-POE-RoomIQ` (Bedroom) | `blocked-hardware` | Top-level YAML exists; blocked on `PRODUCT-POE-410-001` |
| `Ceiling-POE-FanPWM` (S360-311) | `hardware-pending` | Native four-channel driver **design-complete / compile-proven**; current/thermal/RPM **not measured**; `rpm_supported` stays false. Legacy SX1509 path **superseded**. |
| `Ceiling-POE-FanDAC` (S360-312) | `hardware-pending` | Dual-GP8403 driver design-complete, compile green; all bench measurements owed to `S360-312-DAC-BENCH-001` |
| FanRelay (S360-310) | `hardware-pending` | SELV control logic authorable; mains load-side bench owed |
| FanTRIAC (S360-320) | `blocked` (HW-005) | `ac_dimmer` direct-GPIO gate/zero-cross routing unresolved; not authorable as-is |

No fan-driver firmware is published, released, or release-ready here.

---

## 5. WebFlash blockers

WebFlash eligibility is governed **solely** by a row in
[`config/webflash-builds.json`](../config/webflash-builds.json). Exactly the two
builds in §1 are exposed.

| Path | WebFlash status | Blocker to exposure |
|---|---|---|
| `S360-KIT-BATH-P` / `Ceiling-POE-VentIQ-RoomIQ` | **exposed (stable)** | None |
| LED variant `Ceiling-POE-VentIQ-RoomIQ-LED` | **exposed (preview)** | Stable exposure gated by the LED gauntlet (§7) |
| Kitchen / Bedroom / Living / Corridor targets | **not-exposed** | No `webflash-builds` row; no `artifact_name`; `webflash_build_matrix` not flipped — each gated on its §4 firmware + §3 hardware blockers |
| All fan drivers (Relay / PWM / DAC / TRIAC) | **not-exposed** | No `webflash-builds` row, no `artifact_name`, no `webflash_build_matrix` flip; token absent. Cross-repo `WF-IMPORT-{RELAY,PWM,DAC,TRIAC}-001` blocked behind each `RELEASE-*` |

**No WebFlash exposure is enabled by this doc.** The `workflow_dispatch`-only
manual-firmware-artifacts lane ([`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json))
uploads only temporary, expiring, **non-release** GitHub Actions artifacts and
never creates a release.

---

## 6. Release-note / artifact blockers

Per [`docs/room-firmware-release-matrix.md`](room-firmware-release-matrix.md) /
[`docs/room-firmware-release-notes.md`](room-firmware-release-notes.md).

| Path | Release-note status | Artifact status | Blocker |
|---|---|---|---|
| `S360-KIT-BATH-P` / `Ceiling-POE-VentIQ-RoomIQ` | `eligible-stable` | shipped: `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` | None |
| LED variant | `eligible-preview` | shipped (preview) | LED gauntlet for a **stable** note |
| Kitchen / Bedroom / Living / Corridor | `not-generable` (no catalog row) | **no `artifact_name`** | Refused without overrides until the §4 firmware blockers clear |
| Fan drivers (PWM / DAC / Relay / TRIAC) | not-generable | **no `artifact_name`** (templates only) | Design-complete D5 templates exist for PWM/DAC; no artifact, no release, no checksum, no `firmware/sources.json` / `manifest.json` entry |

**No `artifact_name` is added, no firmware is published, and no release/tag is
created by this doc.**

---

## 7. LED preview status

The Sense360 LED ring (S360-300) board is `schematic_status: verified`, but the
**LED firmware product is preview-only — not stable.** The
`Ceiling-POE-VentIQ-RoomIQ-LED` build ships on the **preview** channel (§1), and
the LED room bundles (`S360-KIT-LIVING-P`, `S360-KIT-CORRIDOR-P`) are
`preview-candidate`.

LED stays preview until the preview→stable gauntlet closes
([`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md),
[`docs/product-led-preview-decision.md`](product-led-preview-decision.md)):
`S360-300-BENCH-001`, `WF-HW-TEST-001`, `WF-HW-TEST-003`, `RELEASE-007`.
**No LED-stable claim is made anywhere in this repo.**

---

## 8. Exact evidence required (per blocked path)

Forward pointers only — **no evidence is claimed, run, or fabricated here, and
every bench task is future-only (blocked until physical hardware / bench
equipment exists).**

| Blocked path | Exact evidence required to unblock | Owning task |
|---|---|---|
| `S360-KIT-KITCHEN-P` (Kitchen) | AirIQ sensor-stack bench: SPS30 / SGP41 / SCD41 / BMP390 measured behaviour; top-level product YAML + catalog row + full compile; **plus** the S360-410 PoE chain (below) | `STABLE-TARGET-AIRIQ-001` → `STABLE-TARGET-AIRIQ-ROOMIQ-001` |
| `S360-KIT-BEDROOM-P` (Bedroom) | S360-410 PoE chain (below) only; then product YAML / catalog row / compile / WebFlash row | `STABLE-TARGET-CORE-001` → `STABLE-TARGET-ROOMIQ-001` |
| `S360-KIT-LIVING-P` / `S360-KIT-CORRIDOR-P` | LED gauntlet (below) **plus** the S360-410 PoE chain (below) | `LED-STABLE-PROMOTION-001` (alias `RELEASE-007`) + a no-VentIQ LED slice |
| **LED gauntlet** (S360-300) | `S360-300-BENCH-001` LED bench evidence; `WF-HW-TEST-001` / `WF-HW-TEST-003` operator flash proof; `RELEASE-007` | `LED-STABLE-PROMOTION-001` / `RELEASE-007` |
| **S360-410 PoE chain** | PoE link-up vs 802.3af/at PSE; output rail under load; inrush; thermal; EMI-EMC; isolation Hi-pot / insulation-resistance / leakage; isolation creepage/clearance (gerbers + BOM); `F0505S-2WR2` part rating; J2-harness + silkscreen; pre-/post-isolation `GND`≠`Earth` | `PRE-HW-PREP-POE-410-001` / `PACKAGE-POE-410-001` |
| **S360-311 PWM** | Silkscreen `J3` 1-to-13 order + `J6`↔`J3` harness; native PWM drive on `IO10/11/12/39`; per-fan + aggregate current; thermal envelope; per-fan RPM via native `pulse_counter`; resolve `"NINE 4pin FANs"` label + `J3` 11/12 UART routing | `S360-311-CURRENT-THERMAL-001` (current/thermal), `HW-PINMAP-311` |
| **S360-312 DAC** | 0-10 V output per channel; GP8403 detection + I²C address (`SW1`/`SW2`); output range/calibration; fan/controller response; current; thermal; harness/silkscreen; +5V-vs-+3.3V rail | `S360-312-DAC-BENCH-001` (blocked on physical board) |
| **S360-310 Relay** | SELV switching logic bench; contact bounce; mains contact-rating + load-side clearance (gerbers + BOM); SELV/mains domain separation on silkscreen | `PRE-HW-PREP-FW-310-001` (SELV) + `PRE-HW-PREP-GERBER-REVIEW-001` (load side) |
| **S360-320 TRIAC** | Direct-ESP32 gate/zero-cross mapping; zero-cross detection; phase-angle timing into mains load; opto isolation; **COMPLIANCE-001** UK/EU sign-off; creepage/clearance (gerbers) + EMC | `PRE-HW-PREP-TRIAC-320-001` (HW-005 / COMPLIANCE-001) |
| **S360-400 240v PSU** | Output rail under load; ripple; inrush; thermal; converter identity; **COMPLIANCE-001** sign-off; creepage/clearance (gerbers) + Hi-pot/insulation + X/Y-cap class | `PRE-HW-PREP-MAINS-400-001` (COMPLIANCE-001) |

> For the PoE board (S360-410) and the three mains boards (S360-310 / S360-320 /
> S360-400), **no design-derived artifact — including fully compiled
> `design-complete` firmware — moves the board to `verified`.** The
> safety-evidence is mandatory and bench/certification-sourced, and **the
> hardware bench tasks are future-only until physical hardware/equipment
> exists.**

---

## 9. Next PR owner / task

Working priority order is maintained in [`UPCOMING_PR.md`](../UPCOMING_PR.md).
The owning follow-ups for each blocked path (none started, reordered, or
unblocked here):

| Lane | Owning PR / task | Gate |
|---|---|---|
| Kitchen (AirIQ) | `STABLE-TARGET-AIRIQ-001` → `STABLE-TARGET-AIRIQ-ROOMIQ-001` | AirIQ sensor evidence + S360-410 chain |
| Bedroom (RoomIQ-only) | `STABLE-TARGET-CORE-001` → `STABLE-TARGET-ROOMIQ-001` | S360-410 chain |
| Living / Corridor (LED) | `LED-STABLE-PROMOTION-001` (`RELEASE-007`) + no-VentIQ LED slice | LED gauntlet + S360-410 chain |
| LED promotion | `S360-300-BENCH-001`, `WF-HW-TEST-001` / `WF-HW-TEST-003`, `RELEASE-007` | Preview→stable gauntlet |
| S360-410 PoE | `PRE-HW-PREP-POE-410-001` / `PACKAGE-POE-410-001` | Isolation / Hi-pot / gerber review (ARTIFACT-gated) |
| S360-311 PWM | `S360-311-CURRENT-THERMAL-001`, `HW-PINMAP-311` | Current/thermal/RPM bench (future-only) |
| S360-312 DAC | `S360-312-DAC-BENCH-001` | Physical board in hand (future-only) |
| S360-310 Relay | `PRE-HW-PREP-FW-310-001`, `PRE-HW-PREP-GERBER-REVIEW-001` | SELV logic now; mains review ARTIFACT-gated |
| S360-320 TRIAC | `PRE-HW-PREP-TRIAC-320-001` | HW-005 + COMPLIANCE-001 |
| S360-400 PSU | `PRE-HW-PREP-MAINS-400-001` | COMPLIANCE-001 + gerber review |
| Fan variants | preview bundle plan `ROOM-BUNDLE-FAN-VARIANTS-002`; stable owned by each fan-driver evidence gate | Each fan-driver evidence gate above |

---

## 10. Coverage checklist

Every item named in the consolidation request is covered above:

- **Bundles:** `S360-KIT-BATH-P` (§1, §2 — ships today), `S360-KIT-KITCHEN-P`,
  `S360-KIT-LIVING-P`, `S360-KIT-BEDROOM-P`, `S360-KIT-CORRIDOR-P` (§2 — blocked).
- **Fan variants:** Bathroom / Kitchen fan-control variants (§2.1 —
  planning-only).
- **Power:** `S360-410` PoE PSU (§3.1 — `cataloged_unverified`, UNRESOLVED, NOT
  verified), `S360-400` 240v PSU (§3, §8).
- **Drivers:** `S360-300` LED (§7 — preview-only, no stable claim), `S360-310`
  Relay (§3, §4), `S360-311` PWM (§3, §4 — design-complete / bench-pending),
  `S360-312` DAC (§3, §4 — design-complete / bench owed), `S360-320` TRIAC (§3,
  §4 — HW-005 blocked).

---

## 11. Guardrails (explicitly NOT changed)

This PR adds this doc plus pointer rows in the consolidated docs and a
`UPCOMING_PR.md` entry. It does **not**:

- promote any bundle (no `current_release_status` change; nothing moved to
  `preview` / `stable` / `production`);
- enable WebFlash (no row added to [`config/webflash-builds.json`](../config/webflash-builds.json));
- add any `artifact_name`;
- flip any `webflash_build_matrix` value;
- publish firmware, create a release / tag, or add a `.bin` / checksum /
  build-info;
- change [`firmware/sources.json`](../firmware/sources.json);
- change `manifest.json`;
- mark `S360-410` `verified` (`schematic_status` stays `cataloged_unverified`;
  the Release-One PoE "schematic verification pending" caveat is preserved
  verbatim);
- mark LED (`S360-300`) stable (LED firmware stays `preview`; no LED-stable
  claim);
- mark any fan variant (`S360-310` / `S360-311` / `S360-312` / `S360-320`)
  release-ready;
- claim, run, or fabricate any bench evidence — every bench task is future-only.

No `config/*.json`, `packages/**`, or `products/**` file is edited.

---

## 12. Validation

This PR adds no new config or code, so the existing suite is unchanged:

- `python3 tests/validate_configs.py`
- `python3 tests/test_roadmap_status_doc.py`
- `python3 tests/test_product_catalog.py`
- `python3 tests/test_room_bundle_skus.py`
- `python3 tests/test_room_bundle_fan_variants.py`
- `python3 tests/validate_webflash_builds.py`
- `python3 -m unittest discover -s tests -p "test_*.py"`

---

## 13. Cross-references

- Operator dry-run checklist for the first stable release:
  [`docs/first-release-dryrun-checklist.md`](first-release-dryrun-checklist.md) —
  `FIRST-RELEASE-DRYRUN-CHECKLIST-001`.
- Roadmap / status / blocker view:
  [`docs/sense360-roadmap-status.md`](sense360-roadmap-status.md) —
  `DOCS-CONSOLIDATION-ROADMAP-001`.
- Pre-hardware room-bundle handoff matrix:
  [`docs/pre-hardware-room-bundle-release-handoff.md`](pre-hardware-room-bundle-release-handoff.md)
  — `PRE-HW-PREP-ROOM-BUNDLES-001`.
- Pre-hardware design-readiness program:
  [`docs/pre-hardware-prep-plan.md`](pre-hardware-prep-plan.md) —
  `PRE-HARDWARE-PREP-PLAN-001`.
- Room bundle SKUs / fan variants:
  [`config/room-bundle-skus.json`](../config/room-bundle-skus.json) ·
  [`config/room-bundle-fan-variants.json`](../config/room-bundle-fan-variants.json).
- Board readiness matrix:
  [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md)
  — `HW-GAP-001`.
- Preview-to-stable gauntlet:
  [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
  — `RELEASE-006`.
- S360-410 PoE evidence:
  [`docs/package-poe-410-001-audit.md`](package-poe-410-001-audit.md) ·
  [`docs/package-poe-410-evidence-result.md`](package-poe-410-evidence-result.md).

---

## Channel-tier policy (RELEASE-PREVIEW-ALL-PRODUCTS-001)

These first-release gates remain the **stable** evidence gauntlet and are
unchanged. Preview eligibility for all buildable targets — and the rule that
lack of hardware proof blocks **stable only, not preview** — is defined in
[`docs/release-channel-policy.md`](release-channel-policy.md) +
[`config/release-channel-policy.json`](../config/release-channel-policy.json).
Reaching preview never satisfies any stable gate below.

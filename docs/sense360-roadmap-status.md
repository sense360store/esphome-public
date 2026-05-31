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
| Manual (non-release) fan artifacts | [`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json) · [`docs/manual-install-fan-candidates.md`](manual-install-fan-candidates.md) |
| Promotion gates | [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md) |
| Per-board hardware evidence | `docs/hardware/**` (pinmaps, schematics, artifacts — **preserved, not consolidated**) |
| Blocker burn-down detail | [`docs/blocker-burndown.md`](blocker-burndown.md) |
| Detailed PR working queue | [`UPCOMING_PR.md`](../UPCOMING_PR.md) |
| Reconciled release-matrix / WebFlash / firmware-availability view | [`docs/release-matrix-webflash-alignment.md`](release-matrix-webflash-alignment.md) (WEBFLASH-RELEASE-MATRIX-ALIGNMENT-001) |
| Consolidated first-release / expansion gate checklist | [`docs/first-release-gates.md`](first-release-gates.md) (PRE-HW-PREP-FIRST-RELEASE-GATES-001) |
| Whole-system architecture (two-repo pipeline + CI map) | [`docs/system-architecture.md`](system-architecture.md) · [`docs/ci-pipeline.md`](ci-pipeline.md) |
| Board / bundle / alias / shim YAML architecture | [`docs/arch-board-bundle-plan.md`](arch-board-bundle-plan.md) · [`docs/system-architecture.md`](system-architecture.md#inside-esphome-public-board--bundle--alias--shim-layers) |

---

## 1. Current release targets

The shippable WebFlash build matrix is [`config/webflash-builds.json`](../config/webflash-builds.json)
(validated by `tests/validate_webflash_builds.py`). There are exactly **two**
builds:

| Config string | Channel | Version | Artifact | Notes |
|---|---|---|---|---|
| `Ceiling-POE-VentIQ-RoomIQ` | **stable** | 1.0.0 | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` | Release-One stable build. |
| `Ceiling-POE-VentIQ-RoomIQ-LED` | **preview** | 1.0.0 | `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` | LED variant is **preview only** (see §7). |

Release-One required configs (`config/webflash-compatibility.json` →
`release_one_required_configs`): **`Ceiling-POE-VentIQ-RoomIQ`** only.

No other config string is release-eligible today. FanRelay / FanPWM / FanDAC /
FanTRIAC are **not** in `webflash-builds.json`, have no `artifact_name`, and do
not set `webflash_build_matrix`.

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
| `S360-KIT-KITCHEN-P` | kitchen | S360-100/200/210/410 | `Ceiling-POE-AirIQ-RoomIQ` | stable-candidate |
| `S360-KIT-LIVING-P` | living-room | S360-100/200/300/410 | `Ceiling-POE-RoomIQ-LED` | preview-candidate |
| `S360-KIT-BEDROOM-P` | bedroom | S360-100/200/410 | `Ceiling-POE-RoomIQ` | stable-candidate |
| `S360-KIT-CORRIDOR-P` | corridor | S360-100/200/300/410 | `Ceiling-POE-RoomIQ-LED` | preview-candidate |

Only `S360-KIT-BATH-P` maps to a shipped stable build. All other bundles are
candidates gated behind their own promotion gates (LED gauntlet and/or the
S360-410 PoE evidence gate — see §6 / §7). No bundle is promoted by this doc.

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
- No fan-driver firmware (Relay / PWM / DAC / TRIAC) is WebFlash-exposed:
  none appears in `config/webflash-builds.json`, none has an `artifact_name`,
  and none flips `webflash_build_matrix`.
- The `workflow_dispatch`-only manual-firmware-artifacts lane
  ([`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json),
  [`docs/manual-install-fan-candidates.md`](manual-install-fan-candidates.md))
  compiles the FanRelay / FanPWM / FanDAC manual candidates and uploads only
  **temporary, expiring, non-release** GitHub Actions artifacts. It never
  creates a release, never writes `firmware/sources.json` / `manifest.json`,
  and never sets a release channel.
- Cross-repo WebFlash import/runtime work is owned by `sense360store/WebFlash`
  and tracked there; see §9.

---

## 6. Hardware blockers

| Blocker | Status | Source |
|---|---|---|
| **S360-410 PoE PSU** `cataloged_unverified` | **UNRESOLVED** | [§6.1](#61-poe--s360-410-blocker) |
| Inline fan drivers (S360-310/311/312/320) `cataloged_unverified` | open | `config/hardware-catalog.json` |
| S360-400 240v PSU `cataloged_unverified` | open | `config/hardware-catalog.json` |
| Fan-driver current / thermal / safety bench | pending | [`docs/blocker-burndown.md`](blocker-burndown.md) |
| Mains / compliance sign-off (Relay / TRIAC / 240v PSU) | pending | [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md) |

### 6.1 PoE / S360-410 blocker

**S360-410 remains `cataloged_unverified` — NOT verified, UNRESOLVED.**

Per [`docs/package-poe-410-001-audit.md`](package-poe-410-001-audit.md)
(PACKAGE-POE-410-001), the evidence is **insufficient** to move S360-410 from
`cataloged_unverified` to `verified` and insufficient to close the package
header today (audit "option 4": evidence-request path). The remaining
schematic / silkscreen / bench / harness / compliance evidence is enumerated
there and in [`docs/hardware/s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md)
(HW-PINMAP-410). The consolidated evidence matrix, the per-bundle
stable-bundle impact assessment, and the operator/designer next-evidence
checklist are recorded at
[`docs/package-poe-410-evidence-result.md`](package-poe-410-evidence-result.md)
(PACKAGE-POE-410-EVIDENCE-RESULT-001, 2026-05-29) — which reconfirms the
bench (PoE link-up / load / inrush / thermal / EMI-EMC), isolation/safety,
connector-silkscreen, J2-harness, and PCB-source evidence classes are still
**missing**, and that `S360-KIT-BEDROOM-P` is blocked by S360-410 alone while
`S360-KIT-KITCHEN-P` / `S360-KIT-LIVING-P` / `S360-KIT-CORRIDOR-P` are
partially blocked (S360-410 plus an AirIQ-stack or LED-gauntlet dependency)
and the already-shipping `S360-KIT-BATH-P` is unaffected.

This blocker gates `PRODUCT-POE-410-001`, `RELEASE-POE-410-001`, the
Release-One PoE caveat closure, and the stable-candidate room bundles that
include S360-410 (`S360-KIT-KITCHEN-P`, `S360-KIT-BEDROOM-P`, and the
preview LED bundles). It is **not** resolved by this doc and **no S360-410
verified claim is made anywhere in this repo.**

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
([`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md),
[`docs/product-led-preview-decision.md`](product-led-preview-decision.md)):
`S360-300-BENCH-001`, `WF-HW-TEST-001`, `WF-HW-TEST-003`, `RELEASE-007`.
**No LED-stable claim is made anywhere in this repo.**

---

## 8. Next PR queue

Working priority order is maintained in [`UPCOMING_PR.md`](../UPCOMING_PR.md)
(the detailed queue). High-level near-term lanes:

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

- [`docs/repo-freshness-roadmap-audit.md`](repo-freshness-roadmap-audit.md)
- [`docs/repo-structure-audit.md`](repo-structure-audit.md)
- [`docs/cleanup-audit.md`](cleanup-audit.md)
- [`docs/webflash-drift-audit.md`](webflash-drift-audit.md)
- [`docs/webflash-ci-alignment.md`](webflash-ci-alignment.md)
- [`docs/webflash-release-handoff.md`](webflash-release-handoff.md)
- [`docs/stable-target-expansion-plan.md`](stable-target-expansion-plan.md)
- [`docs/stable-target-ventiq-001-gate-closure.md`](stable-target-ventiq-001-gate-closure.md)

**Preserved, not consolidated** (source-of-truth, evidence, pinmap, catalog,
policy, or actively test-validated reference docs): everything under
`docs/hardware/**` (pinmaps, schematics, artifacts, readiness matrices),
`docs/compliance/**`, `docs/hardware-catalog.md`, `docs/webflash-contract.md`,
`docs/release-one.md`, `docs/sense360-room-bundles.md`,
`docs/preview-to-stable-promotion-gates.md`, `docs/blocker-burndown.md`,
`docs/product-readiness-matrix.md`, the firmware/release matrices, and the
user/developer guides. These keep their own canonical ownership.

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
| Target shape, rename/alias policy, ordered PR sequence | [`docs/arch-board-bundle-plan.md`](arch-board-bundle-plan.md) |
| Whole-pipeline placement + cross-repo contract | [`docs/system-architecture.md`](system-architecture.md#inside-esphome-public-board--bundle--alias--shim-layers) |
| Per-workflow CI/gate parity across the refactor | [`docs/ci-pipeline.md`](ci-pipeline.md) |
| Per-PR queue state for the epic | [`UPCOMING_PR.md`](../UPCOMING_PR.md) |

Epic status (ownership lives in the plan §7 / `UPCOMING_PR.md`, not here):
`BOARD-PACKAGE-LAYER-001/002`, `BUNDLE-LAYER-001`,
`PACKAGE-RENAME-001..005` (LED, AirIQ, VentIQ, RoomIQ, PoE-PSU source-of-truth
flips), and `CI-REFACTOR-VERIFY-001` are landed; `DOCS-ARCH-REFRESH-001`
(this doc-refresh slice) is current; `WEBFLASH-ARCH-SYNC-001` (WebFlash repo)
remains, recording that the rename is invisible to the WebFlash contract.
The cross-repo contract is unchanged: WebFlash couples only through release
tags, config strings, and artifact names (§1, §5) — **no** board/bundle/alias
rename touches `config/webflash-builds.json`, `manifest.json`, or
`firmware/sources.json`, and the two release targets in §1 are unaffected.

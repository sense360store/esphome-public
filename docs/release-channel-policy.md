# Release-Channel Policy — Preview Eligibility for All Buildable Products (RELEASE-PREVIEW-ALL-PRODUCTS-001)

**Canonical id:** `RELEASE-PREVIEW-ALL-PRODUCTS-001`
**Date:** 2026-06-01
**Type:** Docs + config policy only. This document and its companion
`config/release-channel-policy.json` do **not** change firmware behaviour,
publish any firmware, build or attach any artifact, edit `manifest.json` /
`firmware/sources.json`, add any row to `config/webflash-builds.json`, flip any
`config/product-catalog.json` status, mark anything stable, mark any schematic
verified, claim any bench evidence or compliance, or touch the WebFlash repo.
It records **policy** and **eligibility** only.

Machine-readable source: [`config/release-channel-policy.json`](../config/release-channel-policy.json)
→ guarded by [`tests/test_release_channel_policy.py`](../tests/test_release_channel_policy.py).

---

## Purpose

The previous guardrails treated "no hardware proof" as a blocker for *every*
channel. That is too restrictive: it blocked meaningful, shippable-to-testers
progress on buildable firmware. This policy opens the gate so that **every
buildable Sense360 firmware target can be released as preview**, including the
fan-control and TRIAC targets, while keeping **stable / production promotion
evidence-gated**.

### What "preview" means — and does not mean

- **Preview means:** buildable and installable for testers.
- **Preview does *not* mean:** hardware verified.
- **Preview does *not* mean:** stable, recommended, production, or a customer
  default.
- **Stable remains evidence-gated.**
- **TRIAC may be preview**, but only as **advanced-preview**: it must carry
  advanced / manual / mains-risk warnings and must **never** be recommended, a
  default, or stable.

The driving rule of this policy:

> **Lack of hardware proof blocks _stable only_. It does _not_ block preview
> artifact publication.** A product can be exposed as preview without claiming
> any hardware proof.

---

## 1. Channel tiers

Three policy tiers. Note the distinction between a **policy tier** (how the
target is governed) and a **build channel** (the artifact suffix actually used
by the pipeline). `advanced-preview` is a policy tier layered on the `preview`
build channel — it does not introduce a new artifact-name suffix.

| Tier | Build channel | Hardware proof required | Evidence-gated | Recommended | Customer default | May be REQUIRED_CONFIG | WebFlash exposure | Warning required | May claim bench evidence |
|---|---|---|---|---|---|---|---|---|---|
| **stable** | `stable` | yes | yes | yes | yes | yes | default | no | yes (when verified) |
| **preview** | `preview` | **no** | no | no | no | no | acknowledgement-gated | **yes** | **no** |
| **advanced-preview** | `preview` | **no** | no | no | no | no | acknowledgement-gated-advanced | **yes (mains-risk)** | **no** |

Stable additionally requires `schematic_status: verified` and lifecycle
`production`. Preview and advanced-preview require **neither** — and must not
assert either falsely.

### Module channel ceiling

| Module | Channel ceiling | Channel floor |
|---|---|---|
| **FanTRIAC** | `advanced-preview` | `advanced-preview` |

FanTRIAC can be **advanced-preview only**: never stable, never recommended,
never default.

### Delivery lanes (RELEASE-PREVIEW-WEBFLASH-ALL-BUILDABLE-001)

Every buildable product is a preview / advanced-preview **release** target. The
concrete lane each target uses (recorded in
[`config/preview-release-targets.json`](../config/preview-release-targets.json)):

| Lane | Targets | Meaning |
|---|---|---|
| `webflash` | SELV PoE targets (Bathroom stable, LED preview, Kitchen/AirIQ, Bedroom/RoomIQ, Living/Corridor LED) | WebFlash-importable build behind the acknowledgement gate; a `config/webflash-builds.json` row + wrapper + recorded build proof. |
| `manual-preview` | FanRelay, FanPWM, FanDAC | Releasable preview artifact via the manual lane (`config/manual-firmware-artifacts.json`). **Not** a passive candidate. WebFlash one-click import gated until the WebFlash warning UX is ready (separate follow-up). |
| `advanced-manual-preview` | FanTRIAC | `manual-preview` + mandatory mains-risk warning + competent-person manual install. Preview-allowed; only the `HW-005` buildability blocker prevents a cut. WebFlash import gated behind the advanced acknowledgement UX. |

The fan / TRIAC matrix rows below carry `acknowledgement-gated` /
`acknowledgement-gated-advanced` as their **eventual** WebFlash exposure class.
That is the import *target*, not current state: WebFlash one-click import for fan
and TRIAC previews stays a separate, controlled follow-up. **No target is blocked
from preview for lacking stable evidence** — "blocked" only ever applies to
stable promotion, or (for TRIAC) to a genuine *buildability* blocker.

---

## 2. Policy rules (what this opens, what it keeps closed)

This policy updates the doc + config posture so that:

1. **Lack of hardware proof blocks stable only.** Preview / advanced-preview do
   not require hardware proof.
2. **Lack of hardware proof does not block preview artifact publication.** A
   buildable target is preview-eligible even with an open stable blocker.
3. **Preview releases must include warning text.** Every non-stable release
   must carry the relevant warning copy (see §4).
4. **Preview releases must not claim bench evidence.** No measured current /
   thermal / RPM / compliance claim is permitted on a preview release.
5. **Preview releases must not mark `schematic_status: verified`.**
6. **Preview releases must not mark lifecycle `production`** unless the product
   is *already* production (i.e. preview never promotes a product to
   production as a side effect).
7. **Preview releases must not be `REQUIRED_CONFIGS`.**
8. **Preview artifact release is allowed without WebFlash import.** SELV targets
   release via the `webflash` lane (acknowledgement-gated import). Fan drivers
   release via the `manual-preview` lane and TRIAC via the
   `advanced-manual-preview` lane; their WebFlash one-click import is a separate,
   controlled follow-up behind the (advanced) acknowledgement UX. Lack of WebFlash
   import never blocks a preview artifact.

Stable promotion is unchanged: it still requires the full evidence /
hardware-proof gauntlet (see [`docs/first-release-gates.md`](first-release-gates.md)
and [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)).

> **Pipeline fact (unchanged):** `config/webflash-builds.json` is still the
> sole source of release-eligibility. This policy makes targets *eligible* for
> a preview row; it does **not** add the rows. Publishing a given preview
> artifact (builds-row + wrapper + release tag) is a separate, explicitly
> scoped follow-up per target.

---

## 2a. RELEASE-PREVIEW-UNBLOCK-ALL-BUNDLES-001 — hardware blockers are stable-only

`RELEASE-PREVIEW-UNBLOCK-ALL-BUNDLES-001` formalises the split above into
machine-checkable, per-row metadata. The decision:

> A blocker that rests **only** on missing hardware proof, missing bench
> evidence, missing compliance evidence, or missing commercial availability
> gates **stable / full release only**. It does **not** block a preview artifact
> for a buildable target. The **only** thing that can stop an actual preview cut
> is a genuine **buildability** blocker (e.g. `HW-005` GPIO routing for TRIAC).

To make this checkable, every row of the preview-release matrix (and every
target in [`config/preview-release-targets.json`](../config/preview-release-targets.json))
now carries three explicit flags alongside its existing `stable_blocker`:

| Flag | Meaning |
|---|---|
| `preview_allowed` | The target is preview-eligible. **`true` for every buildable product**, including the fan-control and TRIAC paths. |
| `preview_warning_required` | A preview / advanced-preview cut of this target must carry the relevant warning copy. `true` everywhere. |
| `blocker_is_stable_only` | The recorded `stable_blocker` gates stable only and does **not** block preview. `true` for every hardware / bench / compliance / commercial blocker. (TRIAC is the lone `false`, because `HW-005` is a real *buildability* blocker — see below.) |

The decision block lives in `config/release-channel-policy.json` →
`unblock_all_bundles_decision`, with the classes spelled out:

- **stable-only blocker classes:** `hardware-proof`, `bench-evidence`,
  `compliance`, `commercial-availability`.
- **preview blocker class:** `buildability` (the only thing that can stop a
  preview cut).

What the decision explicitly does **not** do: nothing becomes stable,
recommended, default, or buyable; **Simple install stays the stable Bathroom
PoE build only** (`Ceiling-POE-VentIQ-RoomIQ`); the **advanced / manual preview
lane is the only exposure path** for the risky / unverified TRIAC build; and the
candidate room bundles stay hidden / not buyable. These are asserted by
[`tests/test_release_preview_unblock_all_bundles.py`](../tests/test_release_preview_unblock_all_bundles.py).

### TRIAC under this decision

TRIAC is `preview_allowed: true` and `preview_warning_required: true` with its
`stable_blocker` keeping `HW-005` + `PACKAGE-TRIAC-001` + `COMPLIANCE-001`. It is
the **only** target with `blocker_is_stable_only: false`, because `HW-005`
carries a genuine *buildability* component (S360-320 schematic uncommitted,
GPIO5/GPIO6 collision, `ac_dimmer` cannot run across the SX1509 expander). That
buildability blocker — **not** a lack of hardware proof — is what currently
prevents an actual advanced-preview cut (`hardware_proof_blocks_preview: false`,
`preview_cut_gated_by_buildability: true`). TRIAC stays **advanced-manual-preview
only**: never stable, never recommended, never default, never a customer-kit
default, and no safety / compliance certification is claimed.

### Concrete build rows (RELEASE-PREVIEW-FAN-TRIAC-BUILD-ROWS-001)

`RELEASE-PREVIEW-FAN-TRIAC-BUILD-ROWS-001` makes this decision concrete for the
four fan-control / TRIAC targets by adding a build-row ledger at
[`config/preview-fan-triac-build-rows.json`](../config/preview-fan-triac-build-rows.json)
— the **manual / advanced-manual analog of `config/webflash-builds.json`** — plus
release-note drafts under
[`docs/release-notes/manual-preview/`](release-notes/manual-preview/). FanRelay /
FanPWM / FanDAC are `manual-preview` build rows citing **firmware-build proof
only** (run `26821900127`); FanTRIAC is the `advanced-manual-preview` row,
**build-blocked by `HW-005`** with **no compile proof claimed**. It adds **no**
`config/webflash-builds.json` row (the fan-token guardrail is unchanged), flips
no catalog status, and promotes nothing to stable / recommended / default /
buyable. See
[`docs/release-preview-fan-triac-build-rows.md`](release-preview-fan-triac-build-rows.md).

---

## 3. Preview-release matrix (every buildable target)

One row per buildable target. `Intended channel` is the channel this policy
makes the target eligible for. `Publication status` records whether the
artifact is already live, eligible-but-not-yet-cut, or still needs a product
YAML. **No artifact is published by this PR.**

| Product / bundle | Config string | YAML path | Intended channel | Expected artifact | WebFlash exposure | Warning required | Stable blocker | Publication status |
|---|---|---|---|---|---|---|---|---|
| Bathroom PoE (`S360-KIT-BATH-P`) | `Ceiling-POE-VentIQ-RoomIQ` | `products/sense360-ceiling-poe-ventiq-roomiq.yaml` | **stable** | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` | default | no | — | published-stable |
| Kitchen PoE / AirIQ (`S360-KIT-KITCHEN-P`) | `Ceiling-POE-AirIQ-RoomIQ` | `products/compile-only/ceiling-poe-airiq-roomiq.yaml` | preview | `Sense360-Ceiling-POE-AirIQ-RoomIQ-v1.0.0-preview.bin` | acknowledgement-gated | yes | S360-410 + AirIQ-stack bench evidence | eligible-unpublished |
| Bedroom PoE / RoomIQ (`S360-KIT-BEDROOM-P`) | `Ceiling-POE-RoomIQ` | `products/compile-only/ceiling-poe-roomiq.yaml` | preview | `Sense360-Ceiling-POE-RoomIQ-v1.0.0-preview.bin` | acknowledgement-gated | yes | S360-410 | eligible-unpublished |
| Living PoE / LED (`S360-KIT-LIVING-P`) | `Ceiling-POE-RoomIQ-LED` | `products/compile-only/ceiling-poe-roomiq.yaml` | preview | `Sense360-Ceiling-POE-RoomIQ-LED-v1.0.0-preview.bin` | acknowledgement-gated | yes | S360-410 + LED preview→stable gauntlet | eligible-needs-product-yaml |
| Corridor PoE / LED (`S360-KIT-CORRIDOR-P`) | `Ceiling-POE-RoomIQ-LED` | `products/compile-only/ceiling-poe-roomiq.yaml` | preview | `Sense360-Ceiling-POE-RoomIQ-LED-v1.0.0-preview.bin` | acknowledgement-gated | yes | S360-410 + LED preview→stable gauntlet | eligible-needs-product-yaml |
| LED preview | `Ceiling-POE-VentIQ-RoomIQ-LED` | `products/sense360-ceiling-poe-ventiq-roomiq-led.yaml` | preview | `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` | acknowledgement-gated | yes | LED preview→stable gauntlet | published-preview |
| FanRelay preview | `Ceiling-POE-VentIQ-FanRelay-RoomIQ` | `products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml` | preview | `Sense360-Ceiling-POE-VentIQ-FanRelay-RoomIQ-v1.0.0-preview.bin` | acknowledgement-gated | yes | mains-safety / competent-person sign-off + GPIO3 strap-pin boot characterisation | eligible-unpublished |
| FanPWM preview | `Ceiling-POE-FanPWM` | `products/sense360-ceiling-poe-fanpwm.yaml` | preview | `Sense360-Ceiling-POE-FanPWM-v1.0.0-preview.bin` | acknowledgement-gated | yes | measured current / thermal (S360-311-CURRENT-THERMAL-001); RPM not claimed | eligible-unpublished |
| FanDAC preview | `Ceiling-POE-FanDAC` | `products/sense360-ceiling-poe-fandac.yaml` | preview | `Sense360-Ceiling-POE-FanDAC-v1.0.0-preview.bin` | acknowledgement-gated | yes | Cloudlift S12 / J3 harness + product-bench; S360-312 schematic / BOM | eligible-unpublished |
| **FanTRIAC advanced-preview** | `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` | `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml` | **advanced-preview** | `Sense360-Ceiling-POE-VentIQ-FanTRIAC-RoomIQ-v1.0.0-preview.bin` | acknowledgement-gated-advanced | yes (mains-risk) | HW-005 + PACKAGE-TRIAC-001 + COMPLIANCE-001 mains-voltage review | eligible-unpublished |

**Rescue** (`Rescue`) is WebFlash-owned and tracked separately. It is not a
Sense360 release-channel product and is out of scope for this policy.

Notes:

- The **Bathroom PoE stable path is unchanged** and remains the sole live
  stable release. A future preview successor is permitted under the preview
  tier but is not published here.
- **Living / Corridor** share the `Ceiling-POE-RoomIQ-LED` firmware and still
  need a dedicated product/wrapper YAML before a preview artifact can be cut.
- **FanTRIAC** is advanced-preview on the `advanced-manual-preview` lane — no
  longer "blocked from preview". It still has open hardware routing (HW-005); the
  policy records its advanced-preview *ceiling*, and a preview artifact can be cut
  on that lane once the build is buildable end-to-end. The remaining stopper is a
  *buildability* blocker (HW-005), not a lack of stable evidence.

---

## 4. Warning copy (required on preview releases)

These strings live in `config/release-channel-policy.json` → `warning_copy` and
must appear in the release notes / WebFlash acknowledgement gate for the
corresponding tier.

**preview:**

> PREVIEW FIRMWARE — buildable and installable for testers only. This build is
> NOT hardware verified, NOT stable, NOT recommended, and NOT a customer
> default. No bench evidence and no compliance is claimed. Flash at your own
> risk and expect to recover with the rescue/stable firmware.

**advanced-preview (TRIAC / mains-risk):**

> ADVANCED PREVIEW — MAINS-VOLTAGE RISK. This firmware drives mains-voltage
> hardware (e.g. TRIAC phase-control dimming) and is for competent persons
> performing a manual installation only. It is NOT hardware verified, NOT
> stable, NOT recommended, and is NEVER a default. No bench evidence and no
> electrical-safety / compliance certification is claimed. Incorrect
> installation can cause fire, electric shock, or death. Do not install unless
> you are qualified to work on mains wiring.

---

## 5. Hard guardrails (what this PR must never do)

This PR does **not**, and the policy forbids:

- marking unverified products stable;
- marking TRIAC stable, recommended, or a default;
- making preview products `REQUIRED_CONFIGS`;
- claiming bench evidence;
- claiming compliance;
- marking `schematic_status: verified`;
- publishing artifacts (no builds-row / wrapper / tag is added here);
- touching the WebFlash repo.

These are asserted by `tests/test_release_channel_policy.py`.

---

## 6. Sources of truth

| Layer | Source of truth |
|---|---|
| Release-eligibility (sole source) | [`config/webflash-builds.json`](../config/webflash-builds.json) |
| Channel-tier policy + eligibility matrix | [`config/release-channel-policy.json`](../config/release-channel-policy.json) (this doc) |
| Allowed build channels | [`config/webflash-compatibility.json`](../config/webflash-compatibility.json) |
| Product lifecycle / hardware status | [`config/product-catalog.json`](../config/product-catalog.json) |
| Stable promotion gates | [`docs/first-release-gates.md`](first-release-gates.md) · [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md) |
| Release matrix / WebFlash alignment | [`docs/release-matrix-webflash-alignment.md`](release-matrix-webflash-alignment.md) |

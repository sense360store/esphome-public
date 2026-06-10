# COMPLIANCE-001-RESOLUTION-001 — Owner Decision: Market Posture for Mains-Touching Boards and the Experimental Publish Lane

**Canonical id:** `COMPLIANCE-001-RESOLUTION-001`
**Type:** Owner decision record (governance). Docs and policy/config metadata only.
**Date:** 2026-06-09
**Decided by:** Sense360 owner
**Resolves:** `COMPLIANCE-001` — the mains-voltage UK / EU safety and compliance
assessment tracker at
[`../compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md)
— **status: CLOSED, resolved by posture** (no placing on the market). See §4
for the explicit reopen trigger.

**Boards in scope (the "mains-touching boards"):**

| Board | SKU | Mains role |
|---|---|---|
| Sense360 TRIAC | `S360-320` | Mains-output phase-cut dimmer |
| Sense360 Fan Relay | `S360-310` | Mains-switching relay (SELV control side, mains load side) |
| Sense360 240v PSU | `S360-400` | Mains-input PSU |

---

## 1. Market posture — never placed on the market

The mains-touching boards (`S360-320` Sense360 TRIAC, `S360-310` Sense360 Fan
Relay, `S360-400` Sense360 240v PSU) are **NEVER placed on the market by
Sense360**. Concretely:

- **Not sold assembled.** No assembled or partially assembled unit is sold,
  given away, or otherwise supplied.
- **Not sold as a kit of parts.** No parts kit, component bag, or
  build-it-yourself parcel for these boards is sold or supplied.
- **Not sold as a populated PCB.** No populated or part-populated PCB for
  these boards is sold or supplied.
- **Not physically bundled.** These boards are never physically included in
  any kit, order, bundle, or promotion, in any state of assembly.

**Design files and firmware are published open-source under CERN-OHL-P.**
Customers who build these boards do so **entirely from their own sourcing**, as
**self-builders of their own devices, at their own risk**. Sense360 supplies
the published design and firmware information only; it does not supply the
board, the parts, or the assembly, and it is not the manufacturer of any
self-built device for the purposes of UK / EU product regulation.

This posture is the resolution mechanism for `COMPLIANCE-001`: the conformity
obligations that the tracker enumerates (LVD / EESR, EMC, RED, RoHS, CE / UKCA
marking, technical file, Declaration of Conformity) attach to **placing a
product on the market**. Sense360 does not perform that act for these boards,
so no conformity-assessment obligation arises for Sense360 from the open
publication of the design files and firmware.

## 2. "Expansion-ready" kit designation

A Sense360 kit **may** be designated **"expansion-ready"** for a self-build
board. Expansion-ready means, and is limited to:

- **mechanical provision** (mounting position, aperture, enclosure space);
- a **connector** (the documented Core-side header, e.g. `J15` for the TRIAC
  module);
- **firmware compatibility** (the published firmware can drive the self-build
  board when the self-builder installs it); and
- **documentation linking the open design** (the published CERN-OHL-P design
  files).

Two **binding conditions** attach to every expansion-ready designation:

1. **The kit as sold is complete and functional without the self-build
   board.** The unsupplied board must not be required for any advertised
   function of the kit.
2. **No shop or kit copy positions the unsupplied board as included or as the
   kit's primary function.** Copy may state that the kit is expansion-ready
   and link the open design; it must not present the self-build board as part
   of the offer, as the headline capability, or as anything a customer
   receives.

Breach of either condition converts the bundle, in substance, into supplying
the board — which is a placing-on-the-market act and trips the §4 reopen
trigger.

## 3. Experimental firmware publish lane (self-build mains boards)

Self-build mains board firmware **may publish through an EXPERIMENTAL lane**,
defined as policy metadata in
[`../../config/release-channel-policy.json`](../../config/release-channel-policy.json)
(`experimental_lane`). The lane's binding constraints:

- **Hard-warned at every surface.** Every surface that names, lists, links,
  or installs an experimental build carries the experimental self-build mains
  warning copy. No warning-free surface is permitted.
- **Never stable-recommended.** An experimental build is never presented as
  stable, recommended, or equivalent to a stable build.
- **Never a default.** Never auto-selected, never a customer default, never a
  fallback.
- **Never in the kit picker.** No kit, bundle picker, easy-mode, or
  Simple-install surface ever lists an experimental build.
- **Never in `REQUIRED_CONFIGS`.** Experimental configs never enter
  `release_one_required_configs` / `REQUIRED_CONFIGS` on either repository.
- **Never presented as verified for purchase.** No copy may present an
  experimental build, or its target board, as tested-for-sale, verified for
  purchase, safety-approved, or compliance-certified. The lane exists for
  self-builders of their own devices.

**Precondition for lane entry:** completion of the functional bench protocol
for the target board — `PACKAGE-TRIAC-001` class — **with a signed operator
attestation committed to the bench-proof container**. Bench completion proves
function only (zero-cross lock, gate timing, load waveform, thermal soak,
boot/stability, full-composition re-confirm). It is **not** a safety, EMC,
CE / UKCA, or compliance claim of any kind.

*Status of the precondition at decision time:* the owner reports the
`S360-320` functional bench protocol complete and attested as of 2026-06-09.
The committed evidence container at
[`../package-triac-001-operator-bench-proof.md`](../package-triac-001-operator-bench-proof.md)
records Steps A, B, C and E as PASS on the real Manrose fan-motor load, with
Step F, the full-composition re-confirm, and the signed operator attestation
not yet committed. **Lane entry requires the committed, completed protocol
with the signed attestation** — landing that record (human-reviewed) is part
of the commissioning PR, not this decision record.

**No target is assigned to the experimental lane by this decision.** Moving
the first target (`FanTRIAC` / `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`) into the
lane — including any `channel_tiers` integration, build-channel suffix
decision, build row, wrapper, release tag, catalogue status change, or
WebFlash surface change — is the separate, human-reviewed **commissioning
PR**, queued in [`../../UPCOMING_PR.md`](../../UPCOMING_PR.md) behind the SSOT
refactor and the WebFlash add-source checksum guard. Lane reconciliation for
the existing `S360-310` FanRelay manual-preview publishes, and for any future
`S360-400`-bearing firmware, is likewise deferred to deliberate follow-up
PRs; nothing is re-laned here.

## 4. COMPLIANCE-001 disposition — CLOSED, resolved by posture, with reopen trigger

**`COMPLIANCE-001` is CLOSED, resolved by posture.** Because Sense360 never
places the mains-touching boards on the market (§1), the open
conformity-assessment question that `COMPLIANCE-001` tracked does not arise
for Sense360. The tracker document at
[`../compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md)
is retained in full as the technical checklist for the reopen path; its
evidence standards are unchanged and none of its checklist rows is promoted
by this closure. No safety, EMC, CE / UKCA, LVD, RED, or RoHS conformity is
claimed for any Sense360 board or product by this record.

**REOPEN TRIGGER (explicit and binding):** any future act of **placing any
mains-touching board on the market** — selling it assembled, selling it as a
kit of parts, selling it as a populated PCB, physically bundling it in any
kit, order, or promotion, or any other supply act that makes Sense360 the
manufacturer placing that board on the GB or EU market — **reopens
`COMPLIANCE-001` and requires an external safety and EMC assessment BEFORE
that act.** The assessment must be completed and recorded before the first
market placement, not after.

**Indicative scope and cost recorded for the reopen path** (order-of-magnitude
planning figures noted at decision time; indicative only, not quotations —
the actual scope and quote must be obtained from the chosen test house at
reopen time):

1. **Pre-compliance scan** — an emissions-focused pre-compliance EMC scan at
   a day-rate lab to find and fix gross failures before accredited testing;
   indicatively £1k–£2k per board family.
2. **Test-house safety + EMC** — accredited test-house assessment covering
   the applicable electrical-safety standard(s) (UK EESR / EU LVD scope) and
   full EMC (emissions + immunity) for the **finished product as placed on
   the market**, plus RED if a radio is in the finished product; indicatively
   £5k–£15k+ per finished product, plus the technical file, risk assessment,
   and Declaration of Conformity work (qualified-review effort).

## What this decision changes in this PR — and what it does not

Changes (docs and policy/config metadata only):

- This decision record is added.
- The experimental lane is defined as policy metadata in
  [`../../config/release-channel-policy.json`](../../config/release-channel-policy.json)
  (`experimental_lane`; **no target assigned**).
- Docs and config notes that cited `COMPLIANCE-001` as the **open** blocking
  gate for `S360-320` now cite this record and the experimental-lane
  preconditions instead.
- [`../../UPCOMING_PR.md`](../../UPCOMING_PR.md) records the closure and
  queues the commissioning PR.

Explicitly **not** changed by this PR:

- **No catalogue status flip.** `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays
  `status: blocked` / `webflash_build_matrix: false` / no `artifact_name` in
  [`../../config/product-catalog.json`](../../config/product-catalog.json);
  the blocked WebFlash wrapper stays reference-only.
- **No build row, wrapper, release tag, artifact, checksum, or WebFlash
  surface change.** `config/webflash-builds.json` is untouched; no FanTRIAC
  `.bin` is cut; nothing is published.
- **The publish-gate tests keep enforcing identical behaviour.** The
  `TRIAC-PUBLISH-ADVANCED-PREVIEW-001` gate (`gated_by: PACKAGE-TRIAC-001 +
  COMPLIANCE-001` in
  [`../../config/room-bundle-fan-variants.json`](../../config/room-bundle-fan-variants.json))
  is mechanically unchanged: still not published, still not buyable, still
  not kit-exposed. The `COMPLIANCE-001` element of that gate now resolves to
  this record's experimental-lane preconditions; re-keying the gate itself is
  the commissioning PR's reviewed change.
- **No hardware, bench, EMI, thermal, isolation, creepage, clearance,
  safety, or compliance evidence is claimed.** The
  `PACKAGE-TRIAC-001` proof container stays PENDING until the signed
  attestation is committed.
- **Shop posture is unchanged.** Mains-touching boards remain absent from
  every customer-facing, recommended, default, and buyable surface
  ([`../../config/shop-commercial-source-of-truth.json`](../../config/shop-commercial-source-of-truth.json)
  already enforces this; the "expansion-ready" copy rules in §2 bind any
  future shop change).

## Cross-references

- [`../compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md)
  — the `COMPLIANCE-001` tracker (retained as the reopen-path checklist; its
  closure entry cites this record).
- [`../package-triac-001-operator-bench-proof.md`](../package-triac-001-operator-bench-proof.md)
  — the `PACKAGE-TRIAC-001` bench-proof container (the lane-entry evidence
  container).
- [`../release-channel-policy.md`](../release-channel-policy.md) +
  [`../../config/release-channel-policy.json`](../../config/release-channel-policy.json)
  — channel tiers and the experimental-lane metadata.
- [`../hardware/s360-320-r4-triac.md`](../hardware/s360-320-r4-triac.md) —
  the S360-320 hardware audit.
- [`../../UPCOMING_PR.md`](../../UPCOMING_PR.md) — the commissioning PR queue
  entry and its ordering.

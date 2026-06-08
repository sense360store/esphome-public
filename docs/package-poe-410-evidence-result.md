# PACKAGE-POE-410-EVIDENCE-RESULT-001 — S360-410 PoE PSU evidence reconciliation & stable-bundle impact

## Purpose and scope

This document is the **evidence-result / reconciliation record** for
the `S360-410-R4` Sense360 PoE PSU board. It does one job: collect,
reconcile, and record every piece of S360-410 PoE-PSU evidence that is
**currently on file**, identify exactly what is **still missing**, and
determine which stable PoE room-bundle expansion blockers can be closed
versus which must remain open.

It is a **living evidence / reconciliation record** and changes **no**
hardware status (`S360-410` stays `cataloged_unverified`). The original
2026-05-29 pass added no new evidence; the **2026-06 evidence follow-up**
below (HW-S360-410-EVIDENCE-2026-06) records the S360-410 PoE evidence
gathered in 2026-06 (E9 connector pin-1 polarity, E10 J2 harness, E11
partial bench) and closes the single Release-One PoE documentation caveat
(E15) on the E9 + E10 basis, still **without verifying the board**. It
consolidates the per-evidence-class audit already recorded in
[`docs/package-poe-410-001-audit.md`](package-poe-410-001-audit.md)
(PACKAGE-POE-410-001, the E1–E15 audit) and the schematic / BOM
findings in
[`docs/hardware/s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md)
(HW-PINMAP-410) and
[`docs/hardware/artifacts/S360-410-R4.md`](hardware/artifacts/S360-410-R4.md)
(HW-ASSETS-410 / HW-BOM-ASSETS-002) into the task-brief verification
matrix, the stable-bundle impact assessment, and the next-evidence
checklist.

Where this doc and a source-of-truth file disagree, **the
source-of-truth file wins** and this doc is the one to fix.

### Hard guardrails

PACKAGE-POE-410-EVIDENCE-RESULT-001 — this PR — does **not**:

- promote `S360-410` `schematic_status` from `cataloged_unverified`
  to `verified` in
  [`config/hardware-catalog.json`](../config/hardware-catalog.json),
  set `schematic_file`, or change the `description` field;
- mark `S360-410` verified without schematic + PCB + silkscreen +
  bench + isolation + J2-harness evidence all on file;
- promote any stable release target, flip any
  `webflash_build_matrix` value, add a WebFlash build / wrapper /
  product-catalog row, or enable any WebFlash target;
- publish, build, or attach any firmware artifact, and creates no
  GitHub Release;
- write or edit [`firmware/sources.json`](../firmware/sources.json)
  or `manifest.json`;
- edit [`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml)
  or any YAML under [`products/`](../products/);
- fabricate any schematic, PCB, BOM, silkscreen, bench, isolation,
  safety, or compliance evidence;
- reword or remove the Release-One PoE
  `"schematic verification pending"` caveat at
  [`docs/release-one-hardware-audit.md` Findings → PoE PSU](release-one-hardware-audit.md#findings)
  — it was **preserved verbatim** by the original 2026-05-29 pass.
  *(Superseded for the flagship caveat by the 2026-06 evidence follow-up
  below: HW-S360-410-EVIDENCE-2026-06 closes E15 on the E9 + E10 basis.
  `S360-410` still stays `cataloged_unverified`, no `schematic_file` is
  set, and the flagship's existing stable status is unchanged.)*;
- resolve HW-002 Open Question #6 (J2 PoE harness identity) or
  change `S360-100-BENCH-001` status.

PoE is SELV. `S360-410` is **not** in scope for `COMPLIANCE-001`
(mains-voltage UK / EU assessment), which scopes `S360-320` FanTRIAC
and `S360-400` 240 V PSU only.

---

## 0. 2026-06 evidence follow-up — E9 / E10 recorded, E11 partial, E15 closed (HW-S360-410-EVIDENCE-2026-06, 2026-06-08)

This dated follow-up records the S360-410 PoE-PSU evidence gathered in
2026-06 and closes the single Release-One PoE documentation caveat (E15).
It is layered on top of the original PACKAGE-POE-410-EVIDENCE-RESULT-001
reconciliation (2026-05-29) and the HW-S360-410-GERBERS-E13 PCB-source
commit (2026-06-08). It records evidence **truthfully** and closes **one**
caveat; it does **not** verify the board.

**Recorded on file by this follow-up:**

- **E9 — `J3` connector pin-1 polarity → on file (CAD-render + as-labeled
  connector basis).** Pin-1 polarity is evidenced by (a) the `J3` header
  carrying explicit signal-name silkscreen `5V` and `GND`, which makes the
  connector self-documenting, and (b) KiCad 3D CAD renders (six views) of
  the assembled `S360-410-R4` that confirm the board matches the schematic
  and the BOM. Stated plainly: the evidence is a **CAD render plus an
  as-labeled connector**; a physical as-built pin-1 photograph and the
  `.kicad_pcb` net-map were **not** provided; pin-1 polarity is assured by
  the on-header signal labels **rather than by pin number**.
- **E10 — `J2` PoE harness identity (HW-002 OQ#6) → on file (spec).** A
  2-conductor lead from PSU `J3` (`SM02B-SRSS-TB`, 1×2) to Core `J2
  PoE_ACDC` 2-pin inlet, `+5VP`→`+5VP` and `GND`→`GND`. The polarized JST
  housing prevents reversed mating; both ends are silkscreen-labeled;
  retention is via the JST housing latch. The as-shipped wire-colour map is
  **not** documented and is recorded as **informational-only, not a safety
  gate**, because the keyed connector enforces correct mating regardless of
  wire colour.
- **E11 — bench → PARTIAL.** PoE link-up is confirmed (the board negotiated
  and powered from a PSE) and 5 V conversion is confirmed (output measured
  at 5 V with a multimeter). Load regulation, cold-start inrush, and thermal
  rise under sustained load were **not** measured. **E11 remains PARTIAL.**
- **E13 — PCB source / gerbers → on file (confirmed, no re-commit).** The
  complete 2-layer KiCad gerber set (13 files) is committed at
  [`docs/hardware/gerbers/S360-410-R4/`](hardware/gerbers/S360-410-R4/)
  (archive SHA256
  `e2fb70bbeaf635cce8b36e84abefa558a496e241256500d63d2686559ae93ac8`) by
  HW-S360-410-GERBERS-E13.

**Caveat closed by this follow-up:**

- **E15 — Release-One PoE "schematic verification pending" caveat →
  CLOSED.** Closed on the basis that its blockers **E9** (connector pin-1
  polarity) and **E10** (J2 harness identity) are now on file per the basis
  above. This removes the open PoE documentation caveat on the
  already-shipping flagship `Ceiling-POE-VentIQ-RoomIQ` / `S360-KIT-BATH-P`.
  It does **not** change the flagship's existing stable status and makes
  **no** new hardware claim about S360-410. The caveat row at
  [`release-one-hardware-audit.md` Findings → PoE PSU](release-one-hardware-audit.md#findings)
  is reworded to record the closure.

**Guardrails this follow-up preserves (it does NOT overclaim):**

- `S360-410` stays `cataloged_unverified` / UNRESOLVED everywhere.
  [`config/hardware-catalog.json`](../config/hardware-catalog.json) is
  **unchanged** — `schematic_status` stays `cataloged_unverified`, no
  `schematic_file` is added, and no `verified` claim is made.
- **E11 stays PARTIAL** — load regulation, cold-start inrush, and thermal
  rise are still **not measured**. **E12 (isolation: Hi-pot / insulation
  resistance / leakage / earth continuity) stays MISSING and untouched.**
  No load, thermal, inrush, EMI / EMC, or isolation evidence is claimed to
  exist.
- **No bundle is promoted.** `S360-KIT-BEDROOM-P` (`Ceiling-POE-RoomIQ`)
  stays **blocked by S360-410**; `S360-KIT-KITCHEN-P` stays partially
  blocked / stable-candidate. No
  [`config/webflash-builds.json`](../config/webflash-builds.json) channel
  or bundle status is changed.
- Closing E15 is a **documentation-caveat closure on an already-shipping
  flagship**, not board verification. E2 (the `schematic_status: verified`
  JSON flip), the E11 remainder (load / inrush / thermal / EMI-EMC), and
  E12 (isolation / safety) remain the open gates for `verified`.

The §1–§7 rows below are updated in place to reflect this follow-up; the
historical PACKAGE-POE-410-EVIDENCE-RESULT-001 framing is retained.

*(Superseded for the bundle-blocking disposition by §0.1 below: the owner
waiver HW-S360-410-WAIVER-2026-06 lifts the S360-410 hardware-verification
block on a risk-acceptance basis. The §0 evidence record itself — including
that E11's remainder and E12 were **not measured** — is unchanged; the waiver
does not add, perform, or pass any measurement.)*

---

## 0.1 Owner release waiver — remaining E11/E12 evidence WAIVED, NOT measured (HW-S360-410-WAIVER-2026-06, 2026-06-08)

> **This is an owner risk-acceptance WAIVER, not verification.** The remaining
> S360-410 bench and isolation evidence was **NOT measured, NOT performed, and
> NOT tested**. The owner reviewed the evidence state recorded in §0 / §2 and
> **decided to release S360-410 without completing that remaining evidence,
> explicitly accepting the associated risk**. The hardware-verification blocker
> is lifted **on the basis of that risk-acceptance waiver only** — it is **not**
> a verification, a bench result, or a pass.

| Field | Value |
|---|---|
| Waiver id | `HW-S360-410-WAIVER-2026-06` |
| Date | 2026-06-08 |
| Decided by | owner (risk accepted) |
| Basis | owner risk-acceptance, **not** hardware verification |
| Effect | lifts the S360-410 hardware-verification **block** for release purposes |

**Recorded as WAIVED (NOT measured, NOT performed, NOT passed):**

- **E11 bench remainder — WAIVED.** Load regulation across the rated 5 V
  `+5VP`, cold-start inrush, and thermal rise of `U1` / `U2` / `DCDC1` under
  sustained load were **NOT measured** (EMI/EMC was likewise not captured).
  These are **waived** by owner decision with risk accepted; they were **not**
  tested and are **not** claimed to pass.
- **E12 isolation / safety — WAIVED.** Hi-pot through the `F0505S-2WR2`
  isolation barrier, insulation resistance, leakage current, and `H1`–`H4` →
  RJ45-shield earth continuity were **NOT measured**. These are **waived** by
  owner decision with risk accepted; they were **not** tested and are **not**
  claimed to pass.

**Prior factual evidence is unchanged (NOT part of the waiver, NOT re-tested).**
The §0 bench note stands verbatim: PoE link-up was confirmed (the board
negotiated and powered from a PSE) and 5 V conversion was confirmed (output
measured at 5 V with a multimeter). The waiver records only that the
**still-missing** E11 remainder and E12 are waived rather than gathered; it adds
no new measurement.

**Effect of the waiver:**

- S360-410 is **released under owner waiver `HW-S360-410-WAIVER-2026-06`**; the
  remaining E11/E12 evidence was **not performed** and the risk is **accepted**.
  The hardware-verification **blocker is lifted** for release purposes on the
  owner-waiver basis.
- The dependent PoE room bundles (`S360-KIT-BEDROOM-P`, `S360-KIT-KITCHEN-P`,
  `S360-KIT-LIVING-P`, `S360-KIT-CORRIDOR-P`) **no longer block on the S360-410
  hardware-verification basis**; they proceed under this waiver. Their other,
  non-S360-410 gates are unaffected and stay in force — the AirIQ-stack chain
  for `S360-KIT-KITCHEN-P` and the LED preview→stable gauntlet for
  `S360-KIT-LIVING-P` / `S360-KIT-CORRIDOR-P`.

**What the waiver does NOT do (truth guardrails):**

- It does **not** verify S360-410. `config/hardware-catalog.json` keeps
  `schematic_status: cataloged_unverified` and sets **no** `schematic_file`; a
  new `release_disposition` field records the waiver only.
- It does **not** claim E11 or E12 were measured, performed, tested, or passed.
- It does **not** flip any `config/webflash-builds.json` channel, promote any
  bundle to stable, or productize Bedroom. Those remain separate, explicit
  steps; **this waiver lifts the hardware block only.**

---

## 1. Evidence inventory (what is on file today)

Every row is sourced from a committed file or a committed
retained-but-not-committed ingest record. Nothing below is asserted
beyond what those sources already record.

| Evidence class | On file? | Where | Notes |
|---|---|---|---|
| **Board SKU / R4 revision / canonical naming** | ✅ on file | [`config/hardware-catalog.json`](../config/hardware-catalog.json) lines 116–121 | `sku: S360-410`, `rev: R4`, `old_name: PoE Module`, `description: "PoE to 5V."`, `schematic_status: cataloged_unverified` (no `schematic_file`). Locked by [`tests/test_hardware_catalog.py`](../tests/test_hardware_catalog.py). |
| **Schematic reference (module-side PDF)** | ✅ on file | [`docs/hardware/schematics/S360-410-R4.pdf`](hardware/schematics/S360-410-R4.pdf) | 975,137 bytes; SHA256 `4a8b7a3b2a89006a9332eaa486743f687aaedc4b6bb807c6b25670f742ac2414`. Committed under HW-ASSETS-410 / PR #516. |
| **Schematic-shown discrete topology** | ✅ on file | [`docs/hardware/s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md) | `LAN_CON1 = RJP-003TC1(LPJ4112CNL)` magnetics/RJ45; `U1 = TPS2378DDAR(HSOIC-8)` PoE PD controller; `U2 = TX4138(ESOIC-8)` buck; `DCDC1 = F0505S-2WR2(SIP-7)` isolated DC/DC; `J3` 2-pin Core-facing output; `D3 Green` indicator; `H1`–`H4` `Earth` mounting holes; pre-/post-isolation net topology. |
| **BOM reference** | ✅ on file (retained-but-not-committed) | [`docs/hardware/artifacts/S360-410-R4.md` §HW-BOM-ASSETS-002 BOM ingest (2026-05-20)](hardware/artifacts/S360-410-R4.md#hw-bom-assets-002-bom-ingest-2026-05-20) | `S360-410-R4_BOM.xlsx` (11,980 bytes; SHA256 `b5f4bad842a930de03cd47327f477c21afcb82e4533a9d8be38b54990b38f285`). BOM-confirms the discrete `TPS2378DDAR` + `TX4138` + `F0505S-2WR2` + `RJP-003TC1(LPJ4112CNL)` stack; the schematic-annotated `AM1D-0505S-NZ` does **not** appear in the BOM. |
| **Connector definitions (schematic-side)** | ✅ on file | [`docs/hardware/s360-410-module-pinmap.md`](hardware/s360-410-module-pinmap.md) | `J3` pin 1 = `+5VP`, pin 2 = `GND`; mates Core `J2` `PoE_ACDC` 2-pin inlet; `J3 = JST SM02B-SRSS-TB(LF)(SN)` 1×2 horizontal (BOM). **E9** connector pin-1 polarity and **E10** J2 harness spec are now recorded on file (2026-06, HW-S360-410-EVIDENCE-2026-06) — see §0 and §4. |
| **Photos / renders (CAD)** | ✅ on file (CAD-render basis for E9) | Drive `S360-410-R4 / images`, `step_file`; KiCad 3D CAD renders (six views); committed silkscreen gerber layer `F_Silkscreen.gto` / `B_Silkscreen.gbo` | Per [`docs/hardware/hardware-artifact-policy.md`](hardware/hardware-artifact-policy.md). The **E9** connector pin-1 polarity record (2026-06, HW-S360-410-EVIDENCE-2026-06) rests on (a) the `J3` header's explicit signal-name silkscreen `5V` / `GND` (self-documenting connector) and (b) KiCad 3D CAD renders (six views) confirming the board matches the schematic + BOM. **No physical as-built pin-1 photograph** and **no `.kicad_pcb` net-map** were provided; pin-1 polarity is assured by the on-header signal labels **rather than by pin number**. |
| **PoE-to-5 V role topology** | ✅ on file | [`docs/hardware/s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md) | Detection signature `R1 24.9k`; classification `R2 1.27k` → `Class=0 (0.44–12.95 W)`; RTN sense `R5 0.03R`; buck FB divider `R7 10.5k` / `R8 56.2k` → design set-point ≈ 5.08 V; `F0505S-2WR2` 5 V→5 V isolated DC/DC to `+5VP` / `GND`. |
| **SELV classification** | ✅ on file | [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md) | PoE input 36–57 V DC SELV; post-isolation output low-voltage. Not in COMPLIANCE-001 mains scope. |
| **Test notes (bench / link-up / load / thermal / isolation / EMI)** | ⚠️ partial (E11) · ❌ E12 missing | §0 above (2026-06 bench note) | **E11 PARTIAL (2026-06, HW-S360-410-EVIDENCE-2026-06):** PoE link-up confirmed (board negotiated and powered from a PSE) and 5 V conversion confirmed (output measured at 5 V with a multimeter). **Load regulation, cold-start inrush, and thermal rise under sustained load were NOT measured;** no EMI/EMC report exists. **E12 still MISSING:** no Hi-pot, insulation-resistance, leakage, or earth-continuity report exists for `S360-410-R4`. |
| **PCB source / gerbers** | ✅ on file | [`docs/hardware/gerbers/S360-410-R4/`](hardware/gerbers/S360-410-R4/) | Complete 2-layer KiCad gerber set, 13 files (`F_Cu`/`B_Cu`, `F_Mask`/`B_Mask`, `F_Paste`/`B_Paste`, `F_Silkscreen`/`B_Silkscreen`, `Edge_Cuts`, PTH/NPTH drill + drill maps), extracted from `S360-410-R4_GERBERS.zip` (archive SHA256 `e2fb70bbeaf635cce8b36e84abefa558a496e241256500d63d2686559ae93ac8`) and committed under HW-S360-410-GERBERS-E13. Generated by KiCad Pcbnew 10.0.3, ProjectId `S360-410-R4`, units mm. Storage-backend decision (previously owed per [Hardware Artifact Policy §Future storage decision](hardware/hardware-artifact-policy.md#future-storage-decision)) is now **resolved: gerbers committed to the repo.** The editable `*.kicad_pcb` is not committed; the gerber set is sufficient for fabrication and PCB-geometry inspection. This is the granular E13 line only — it does **not** promote `S360-410` to `verified`. |
| **Prior PR evidence** | ✅ recorded | HW-ASSETS-410 / PR #516; HW-PINMAP-410-FOLLOWUP / PR #517; HW-BOM-ASSETS-002 / PR #535; PACKAGE-POE-410-001 docs-only PR #526; package-header cleanup PR #538; PRODUCT/WEBFLASH/RELEASE-POE-410-001 docs-only investigations PR #528 / #530 / #532 | The schematic, BOM, topology, and package-header-cleanup work is landed; the PCB-source gerbers (E13) are committed by HW-S360-410-GERBERS-E13; and the connector pin-1 polarity (E9, render basis) + J2-harness spec (E10) are recorded by HW-S360-410-EVIDENCE-2026-06. The `verified` JSON promotion (E2), the E11 bench remainder (load / cold-start inrush / thermal / EMI-EMC), and the isolation/safety class (E12) remain owed. |
| **Roadmap / readiness references** | ✅ on file | [`docs/sense360-roadmap-status.md` §6.1](sense360-roadmap-status.md#61-poe--s360-410-blocker); [`docs/blocker-burndown.md`](blocker-burndown.md); [`docs/product-readiness-matrix.md` §PoE-410 / S360-410](product-readiness-matrix.md#poe-410--s360-410); [`docs/release-artifact-readiness-matrix.md` §PoE / S360-410 release posture](release-artifact-readiness-matrix.md#poe--s360-410-release-posture); [`docs/webflash-exposure-readiness-matrix.md` §PoE / S360-410 WebFlash posture](webflash-exposure-readiness-matrix.md#poe--s360-410-webflash-posture) | All keep `S360-410` `cataloged_unverified` / UNRESOLVED; narrowed (2026-06, HW-S360-410-EVIDENCE-2026-06) to reflect E13 on file, E9 / E10 recorded, E11 partial, and the E15 caveat closed. |

---

## 2. Verification matrix

Status keys: ✅ **present** (evidence on file and closed) · ⚠️
**partial** (some evidence on file, not fully closed) · ❌ **missing**
(no evidence on file). The "blocking impact" column states what each
gap blocks; the dominant stable-bundle effect is summarised in §3.

| Verification area | Evidence present | Evidence missing | Status | Blocking impact |
|---|---|---|---|---|
| **Schematic completeness** | Module-side schematic PDF committed (HW-ASSETS-410); per-symbol pin maps + net topology captured (HW-PINMAP-410). | `schematic_status: verified` / `schematic_file` JSON promotion not landed (owed to a separate JSON-only PR after harness + silkscreen + bench close). | ⚠️ partial (E2/E3) | Blocks the `S360-410 schematic_status: verified` JSON PR → blocks every A-row stable target and the `verified`-gated bundles. |
| **PCB completeness** | Complete 2-layer KiCad gerber set (13 files) committed at [`docs/hardware/gerbers/S360-410-R4/`](hardware/gerbers/S360-410-R4/); archive SHA256 `e2fb70bbeaf635cce8b36e84abefa558a496e241256500d63d2686559ae93ac8`. | Editable `S360-410-R4.kicad_pcb` source not committed (not required — the gerber geometry covers isolation-barrier creepage/clearance and `H1`–`H4` bonding inspection). | ✅ on file (E13) | E13 artifact now on file; the isolation-geometry *verification* itself remains part of E12. Does **not** promote `verified` and does not by itself close any caveat. |
| **Connector orientation (`J3` pin-1)** | Schematic-side pin map (`J3` pin 1 = `+5VP`, pin 2 = `GND`); BOM connector identity (`SM02B-SRSS-TB`); **on-header signal-name silkscreen `5V` / `GND`** plus KiCad 3D CAD renders (six views), 2026-06. | Physical as-built pin-1 photograph and the `.kicad_pcb` net-map — not provided; not required (polarity assured by the on-header signal labels rather than by pin number). | ✅ on file (E9, render + as-labeled-connector basis) | **E9 recorded on file (2026-06).** With E10 also on file, closes the Release-One PoE caveat (E15). Does **not** by itself promote `verified`. |
| **J2 harness compatibility** | Core `J2 PoE_ACDC` 2-pin inlet captured; module `J3` 2-pin output captured; **harness spec on file (2026-06):** 2-conductor lead PSU `J3` (`SM02B-SRSS-TB`, 1×2) → Core `J2`, `+5VP`→`+5VP` / `GND`→`GND`; polarized JST housing prevents reversed mating; both ends silkscreen-labeled; retention via JST housing latch. | As-shipped **wire-colour map** — not documented; recorded **informational-only, not a safety gate** (the keyed connector enforces correct mating regardless of wire colour). `S360-100-BENCH-001` stays `pending` for any measured-harness row. | ✅ on file (E10, spec) | **E10 recorded on file (2026-06).** With E9 also on file, closes the Release-One PoE caveat (E15). Does **not** by itself promote `verified`. |
| **PoE negotiation / link-up** | Detection-signature `R1 24.9k` and classification `R2 1.27k` (Class 0) topology captured from schematic/BOM; **link-up confirmed on the bench (2026-06):** the board negotiated and powered from a PSE. | Recorded PSE class (802.3af vs 802.3at) and a signature/classification observation; design-intent (af-only vs af/at) still unresolved (E8). | ⚠️ partial (E11) | E11 PARTIAL — link-up confirmed; the load / inrush / thermal / EMI-EMC remainder is **not measured**, so `verified` stays blocked. |
| **5 V output validation** | Buck FB design set-point ≈ 5.08 V and `F0505S-2WR2` 5 V→5 V isolated DC/DC captured (design values); **5 V conversion confirmed on the bench (2026-06):** output measured at 5 V with a multimeter. | Measured **load regulation** across the rated `+5VP` range and **cold-start inrush** — both still **not measured**. | ⚠️ partial (E5 design / E11 bench) | 5 V output presence confirmed; load regulation + inrush still block `verified`. Output rating `or 3.3V DC` in package header is not evidenced (E8). |
| **Load testing** | None. | Per-output and aggregate load regulation; sustained-load behaviour on `+5VP`. | ❌ missing (E11) | Blocks `verified` and the production electrical-margin claim. |
| **Thermal observations** | None. | Measured thermal rise of `U1` (TPS2378), `U2` (TX4138), `DCDC1` (F0505S-2WR2) under sustained load. | ❌ missing (E11) | Blocks `verified`. |
| **Isolation / safety evidence** | `F0505S-2WR2` datasheet isolation rating only (not as-built). | Hi-pot through the isolation barrier; insulation resistance; leakage; earth continuity `H1`–`H4` → RJ45 shield / `Lan_earth`. | ❌ missing (E12) | Blocks `verified`; this is the augmented evidence class unique to S360-410 (galvanic-isolation boundary). |
| **EMI / EMC evidence** | None. | Conducted / radiated EMI/EMC against the relevant region's EN 55032 / 55035 / FCC Part 15 limits. | ❌ missing (E11) | Blocks `verified` (not a COMPLIANCE-001 mains claim; SELV). |
| **BOM cross-check (part identity)** | ✅ BOM-confirmed discrete stack (`TPS2378DDAR` + `TX4138` + `F0505S-2WR2` + `RJP-003TC1(LPJ4112CNL)`) at the part-identity layer (HW-BOM-ASSETS-002). | `F0505S-2WR2` vs `AM1D-0505S-NZ` populated-primary-vs-alternate intent (E14); package-header reconciliation decision (E8). | ✅ present (E4) / ⚠️ E8/E14 open | Does not block `verified`; E8/E14 block the `PACKAGE-POE-410-001` header-implementation PR. |
| **Manufacturing readiness** | Drive CAD/manufacturing sets present (sch_pdf / bom / cpl / gerbers / step / images); gerber set committed at [`docs/hardware/gerbers/S360-410-R4/`](hardware/gerbers/S360-410-R4/) (E13); **E9 connector pin-1 polarity recorded on file (2026-06)** via on-header silkscreen `5V` / `GND` + CAD renders. | `R4` silkscreen P/N / REV / date-code (tracker `G01` Waiting on logo SVG `N01`); PoE PSU rename (tracker `R11` To do); physical as-built pin-1 photograph (not provided). | ⚠️ partial (E9 on file; E13 on file) | E13 + E9 lines are on file; the remaining manufacturing-silkscreen P/N-REV stamp (`G01`) is still owed but does **not** block the E15 caveat closure. `verified` still gated on the E11 remainder + E12. |
| **SELV classification** | ✅ PoE input 36–57 V DC SELV; post-isolation LV output; not in COMPLIANCE-001 mains scope. | None. | ✅ present (E6/E7) | None — no mains caveat applies. |

**Closed:** board SKU/R4 (E1), schematic topology (E3), BOM part identity
(E4), PoE-to-5 V topology (E5), SELV classification (E6/E7).
**On file (2026-06, HW-S360-410-EVIDENCE-2026-06):** connector pin-1
polarity (E9, CAD-render + as-labeled-connector basis), J2 harness spec
(E10), PCB source / gerbers (E13, via HW-S360-410-GERBERS-E13 — archive
SHA256 `e2fb70bbeaf635cce8b36e84abefa558a496e241256500d63d2686559ae93ac8`).
**Caveat closed (2026-06):** Release-One PoE "schematic verification
pending" caveat (E15), on the E9 + E10 basis — flagship documentation
caveat only, **not** board verification.
**Partial:** schematic JSON promotion (E2), 5 V output (design set-point
plus a measured 5 V presence), PoE bench (E11 — link-up + 5 V confirmed;
**load regulation, cold-start inrush, thermal rise, and EMI/EMC NOT
measured**).
**Open / missing:** load (E11), cold-start inrush (E11), thermal (E11),
EMI/EMC (E11), **isolation/safety (E12 — Hi-pot / insulation / leakage /
earth continuity, untouched)**, package-header reconciliation (E8), DC/DC
alternate intent (E14), `schematic_status: verified` JSON flip (E2),
manufacturing silkscreen P/N-REV stamp (`G01`).

Because the **E11 remainder** (load + cold-start inrush + thermal +
EMI/EMC) and the **safety class E12** (isolation / Hi-pot / leakage /
earth continuity) are still **not on file**, **`S360-410` cannot be
promoted to `verified` today.** Promoting it without the E11 remainder +
E12 would be a fabricated verification. Closing the E15 **documentation**
caveat on the E9 + E10 basis does **not** change that: the flagship
already ships and `S360-410` stays `cataloged_unverified`.

---

## 3. Stable-bundle impact assessment

Per-bundle impact of the S360-410 evidence state. The five PoE room
bundles are sourced from
[`config/room-bundle-skus.json`](../config/room-bundle-skus.json) /
[`docs/sense360-room-bundles.md`](sense360-room-bundles.md). A bundle
is **blocked by S360-410** when S360-410 is the sole remaining
hardware-verification blocker; **partially blocked** when S360-410 is
one of two-or-more independent blockers; **not blocked** when the
bundle already ships (under its preserved caveat) and the S360-410
evidence gaps do not stop it shipping.

| Bundle SKU | Boards | Likely firmware target | S360-410 impact | Rationale |
|---|---|---|---|---|
| `S360-KIT-BATH-P` | S360-100/200/211/410 | `Ceiling-POE-VentIQ-RoomIQ` | **not blocked** (ships; PoE caveat now closed) | This is the Release-One stable build (`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`). It already ships. The Release-One PoE `"schematic verification pending"` caveat (E15) is now **closed** (2026-06, on the E9 + E10 basis); the flagship's stable status is unchanged and no new S360-410 hardware claim is made. Not requalified here. |
| `S360-KIT-BEDROOM-P` | S360-100/200/410 | `Ceiling-POE-RoomIQ` | **blocked by S360-410** | All included boards except `S360-410` are `verified` (S360-100 / S360-200). S360-410 is the **sole remaining hardware-verification blocker** for this bundle's `stable-candidate` promotion (G1–G8 + the PoE-410 chain). Owned by `STABLE-TARGET-ROOMIQ-001`. |
| `S360-KIT-KITCHEN-P` | S360-100/200/210/410 | `Ceiling-POE-AirIQ-RoomIQ` | **partially blocked** | S360-410 is one of two independent blockers; the other is the AirIQ-stack hardware-evidence chain (SPS30 / SGP41 / SCD41 / BMP390) plus the missing `Ceiling-POE-AirIQ-RoomIQ` product YAML. Both must close. Owned by `STABLE-TARGET-AIRIQ-001` → `STABLE-TARGET-AIRIQ-ROOMIQ-001`. |
| `S360-KIT-LIVING-P` | S360-100/200/300/410 | `Ceiling-POE-RoomIQ-LED` | **partially blocked** | S360-410 is one of two independent blockers; the other is the LED preview→stable gauntlet (`LED-STABLE-PROMOTION-001`, `S360-300-BENCH-001`). LED stays `preview` regardless of S360-410. |
| `S360-KIT-CORRIDOR-P` | S360-100/200/300/410 | `Ceiling-POE-RoomIQ-LED` | **partially blocked** | Same board set and same two independent blockers as `S360-KIT-LIVING-P` (S360-410 PoE chain + LED gauntlet). |

**Summary.** S360-410 PoE-PSU verification is the **single largest
blocker** to expanding stable PoE room bundles beyond the
already-shipping `S360-KIT-BATH-P`. Closing S360-410 alone would
directly unblock **`S360-KIT-BEDROOM-P`** (sole remaining hardware
blocker) and is a **necessary-but-not-sufficient** condition for
`S360-KIT-KITCHEN-P` (also AirIQ-stack), `S360-KIT-LIVING-P`, and
`S360-KIT-CORRIDOR-P` (also LED gauntlet). No bundle is promoted,
reclassified, or built by this PR. The 2026-06 follow-up closes the
Release-One PoE **documentation** caveat (E15) on the already-shipping
flagship `S360-KIT-BATH-P` but promotes, reclassifies, or builds **no**
bundle: `S360-KIT-BEDROOM-P` stays **blocked by S360-410** and
`S360-KIT-KITCHEN-P` stays **partially blocked / stable-candidate**,
because the E11 remainder and E12 keep S360-410 `cataloged_unverified`.

**Waiver update (HW-S360-410-WAIVER-2026-06, 2026-06-08).** The owner has since
**waived** the remaining E11/E12 evidence and **accepted the risk** (§0.1). On
that basis `S360-KIT-BEDROOM-P`, `S360-KIT-KITCHEN-P`, `S360-KIT-LIVING-P`, and
`S360-KIT-CORRIDOR-P` **no longer block on the S360-410 hardware-verification
basis** and may proceed under the waiver; their non-S360-410 gates (the AirIQ
stack for Kitchen, the LED preview→stable gauntlet for Living / Corridor) are
unaffected. The waiver does **not** measure E11/E12, does **not** verify
S360-410 (it stays `cataloged_unverified`), and does **not** by itself promote
any bundle to stable.

---

## 4. Precise remaining evidence requests & unblock conditions

No vague "needs verification" wording — each row names the exact
missing artefact and the exact condition that closes it. These mirror
the E-class rows in
[`docs/package-poe-410-001-audit.md` §Evidence-request record](package-poe-410-001-audit.md#evidence-request-record-precise);
this section is the reconciled, dependency-ordered view.

| Ref | Exact missing artefact | Exact unblock condition |
|---|---|---|
| **E9 — `J3` connector pin-1 polarity** | ✅ **On file (2026-06, HW-S360-410-EVIDENCE-2026-06).** Pin-1 polarity recorded from (a) the `J3` header's explicit signal-name silkscreen `5V` / `GND` (self-documenting connector) and (b) KiCad 3D CAD renders (six views) confirming the board matches the schematic + BOM. | Met on a **CAD-render + as-labeled-connector** basis. A physical as-built pin-1 photograph and the `.kicad_pcb` net-map were **not** provided; pin-1 polarity is assured by the on-header signal labels **rather than by pin number**. |
| **E10 — J2 harness identity (HW-002 OQ#6)** | ✅ **On file (spec, 2026-06, HW-S360-410-EVIDENCE-2026-06).** 2-conductor lead from PSU `J3` (`SM02B-SRSS-TB`, 1×2) to Core `J2 PoE_ACDC` 2-pin inlet, `+5VP`→`+5VP` / `GND`→`GND`; polarized JST housing prevents reversed mating; both ends silkscreen-labeled; retention via JST housing latch. | Met at the **spec** level. The as-shipped **wire-colour map** is **not** documented and is **informational-only, not a safety gate** (the keyed connector enforces correct mating regardless of wire colour). `S360-100-BENCH-001` stays `pending` for any measured-harness row, but the harness identity required for the E15 caveat closure is recorded. |
| **E11 — PoE link-up / load / thermal / EMI/EMC bench** | ⚠️ **PARTIAL (2026-06, HW-S360-410-EVIDENCE-2026-06).** Link-up confirmed (board negotiated and powered from a PSE) and 5 V conversion confirmed (output measured at 5 V with a multimeter). **Still owed:** (c) load regulation across the rated 5 V `+5VP`, (d) cold-start inrush, (e) thermal rise of `U1`/`U2`/`DCDC1` under sustained load, (f) conducted/radiated EMI/EMC, plus a recorded PSE class for (a)/(b). | **E11 remains PARTIAL** — the load / inrush / thermal / EMI-EMC sub-items are **not measured**. Design-intent (802.3af-only vs af/at-capable) stays unsettled until a recorded link-up class is filed. This PARTIAL state does **not** promote `verified`. |
| **E12 — isolation / safety** | A safety record documenting Hi-pot through the `F0505S-2WR2` barrier (`Sw_Vin_Poe` ↔ `+5VP`/`GND`), insulation resistance, leakage current, and earth continuity `H1`–`H4` → RJ45 shield / `Lan_earth`. | As-built isolation/leakage/earth-continuity measured and filed (datasheet rating alone is **not** sufficient). |
| **E13 — PCB source / gerbers** | ✅ **Resolved (HW-S360-410-GERBERS-E13).** Complete 2-layer KiCad gerber set (13 files) committed at [`docs/hardware/gerbers/S360-410-R4/`](hardware/gerbers/S360-410-R4/); archive SHA256 `e2fb70bbeaf635cce8b36e84abefa558a496e241256500d63d2686559ae93ac8`. Storage-backend decision now resolved: gerbers committed to the repo. | Met: isolation-barrier creepage/clearance and `H1`–`H4` PCB bonding are now inspectable from the committed gerber geometry. The geometry *verification* itself remains part of E12; the editable `*.kicad_pcb` is not required. |
| **E14 — `F0505S-2WR2` vs `AM1D-0505S-NZ`** | Either a `PACKAGE-POE-410-001` header note recording `F0505S-2WR2` populated-primary / `AM1D-0505S-NZ` alternate, or a schematic-side correction PR removing a stale annotation. | Populated-primary decision recorded. |
| **E8 — package-header reconciliation** | The `PACKAGE-POE-410-001` implementation PR editing [`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml) header to cite the BOM-confirmed discrete topology, the PoE-class declaration intent, the 5 V-only output rating, and the protection-claim decision. | Four design-intent answers recorded (see §5); header reconciled; package-readiness row reclassified to `ready-for-package-change`. |
| **E2 — `schematic_status: verified` JSON PR** | A JSON-only PR flipping the `S360-410` row to `verified` and setting `schematic_file: docs/hardware/schematics/S360-410-R4.pdf`. | E9 + E10 + E11 + E12 closed first; PR passes [`tests/test_hardware_catalog.py`](../tests/test_hardware_catalog.py). |
| **E15 — Release-One PoE caveat closure** | ✅ **CLOSED (2026-06, HW-S360-410-EVIDENCE-2026-06).** The `"schematic verification pending"` caveat at [`release-one-hardware-audit.md` Findings → PoE PSU](release-one-hardware-audit.md#findings) is reworded to record closure. | Closed on the basis that its blockers **E9** (connector pin-1 polarity) and **E10** (J2 harness) are now on file — a **flagship documentation-caveat closure**, not board verification. It does **not** promote `S360-410` to `verified` (still gated on E2 + the E11 remainder + E12) and makes no new S360-410 hardware claim. |

**Dependency order (2026-06 update).** The flagship **documentation**
caveat (E15) closes on **E9 + E10** (both now on file) — this is the
already-shipping `S360-KIT-BATH-P` and does not require board
verification. The board-`verified` path is separate and still runs E9 +
E10 + **E11 remainder** + **E12** (evidence) → E2 (`verified` JSON) and
E8/E14 (package header) → A-row stable-target G8 closure →
`S360-KIT-BEDROOM-P` and (with their own extra evidence) `KITCHEN-P` /
`LIVING-P` / `CORRIDOR-P`.

---

## 5. Next-evidence checklist (operator / designer requests)

Exact requests the hardware owner / designer must answer or supply to
close the remaining gaps. Each maps to an E-class above.

**Operator bench / fixture requests (close E9–E12):**

1. ✅ **E9 recorded (2026-06, HW-S360-410-EVIDENCE-2026-06 — render +
   as-labeled-connector basis).** `J3` pin-1 polarity is on file via the
   on-header signal-name silkscreen `5V` / `GND` plus KiCad 3D CAD renders
   (six views). A physical as-built pin-1 photograph (still nice-to-have
   for the full `verified` path) was **not** provided; the `.kicad_pcb`
   net-map was **not** provided. *(E9)*
2. ✅ **E10 recorded (2026-06, spec).** Core `J2` ↔ module `J3` harness on
   file as a spec: 2-conductor lead, PSU `J3` (`SM02B-SRSS-TB`, 1×2) → Core
   `J2`, `+5VP`→`+5VP` / `GND`→`GND`, polarized JST housing, both ends
   silkscreen-labeled, JST-latch retention. The as-shipped **wire-colour
   map** is **informational-only, not a safety gate** (keyed connector) and
   is **not** documented. *(E10)*
3. ⚠️ **E11 partial (2026-06).** Link-up confirmed (the board negotiated
   and powered from a PSE). **Still owed:** bench against **both** an
   802.3af PSE and an 802.3at PSE and record signature / classification /
   PSE class. *(E11)*
4. ⚠️ **Still owed (E11).** Measure load regulation across the rated 5 V
   `+5VP` output, plus cold-start inrush — **not measured** (5 V output
   presence is confirmed via multimeter; load regulation and inrush are
   not). *(E11)*
5. Measure thermal rise of `U1` (TPS2378DDAR), `U2` (TX4138), and
   `DCDC1` (F0505S-2WR2) under sustained load. *(E11)*
6. Capture conducted / radiated EMI/EMC vs EN 55032 / 55035 / FCC
   Part 15. *(E11)*
7. Hi-pot the `F0505S-2WR2` isolation barrier; measure insulation
   resistance, leakage current, and `H1`–`H4` → RJ45-shield earth
   continuity. *(E12)*
8. ✅ **Done (HW-S360-410-GERBERS-E13).** Gerbers supplied and committed
   at [`docs/hardware/gerbers/S360-410-R4/`](hardware/gerbers/S360-410-R4/)
   — complete 2-layer KiCad set, 13 files; archive SHA256 recorded in §1. *(E13)*

**Designer / design-intent questions (close E8 / E14):**

9. Is `S360-410-R4` intended as **802.3af-only** or **802.3af /
   802.3at-capable**? (Schematic/BOM `R2 1.27k` = Class 0 is
   consistent with af-only; the package header presently says "af or
   at" / "Class 0 or Class 1".) *(E8)*
10. Is the package-header `or 3.3V DC` output option **intentional or
    stale**? (FB divider + `F0505S-2WR2` evidence the 5 V output
    only.) *(E8)*
11. Keep or remove the `Overcurrent, overvoltage, short-circuit`
    protection claim — and which device is the source (TPS2378 OVT /
    TX4138 ILIM / F0505S-2WR2 datasheet) — pending bench evidence?
    *(E8)*
12. Is `AM1D-0505S-NZ` a purchasing-side alternate, a future-revision
    option, or a stale schematic annotation to remove? *(E14)*

When items 1–7 (and the answers to 9–12) are on file, the mechanical
`verified` JSON PR (E2), the package-header implementation PR (E8), and
the Release-One caveat closure (E15) can proceed in dependency order.

---

## 6. Decision

> **Do not promote `S360-410` to `schematic_status: verified`, do not
> promote any stable bundle or release target, and do not enable any
> WebFlash target.** The board-`verified` gates — the bench remainder
> (E11 load / cold-start inrush / thermal / EMI-EMC) and the
> isolation/safety class (E12) — are **not on file**. The connector pin-1
> polarity (E9) and J2-harness (E10) classes are now **on file** (2026-06,
> render + spec basis), the PoE bench (E11) is **partial** (link-up + 5 V
> confirmed), and the PCB-source class (E13) is **on file** (gerbers
> committed at
> [`docs/hardware/gerbers/S360-410-R4/`](hardware/gerbers/S360-410-R4/) by
> HW-S360-410-GERBERS-E13) — none of which, individually or together,
> verifies the board. On the strength of E9 + E10, the **2026-06 follow-up
> closes the single Release-One PoE documentation caveat (E15)** on the
> already-shipping flagship `S360-KIT-BATH-P`, without changing its stable
> status and without making any new S360-410 hardware claim. `S360-410`
> stays `cataloged_unverified`.

This stays the option-4 outcome for the board itself: bench + isolation
evidence is insufficient for verification, so **no verification is
fabricated** — only the documentation caveat that E9 + E10 actually
discharge is closed, and a precise remaining-evidence record is kept.

**Update — owner waiver (HW-S360-410-WAIVER-2026-06, 2026-06-08).** The owner
has since **waived** the remaining E11 (load / cold-start inrush / thermal) and
E12 (isolation / Hi-pot / insulation resistance / leakage / earth continuity)
evidence and **accepted the risk**, lifting the S360-410 hardware-verification
**block** for release purposes (see §0.1). This does **not** change the
verification facts above: E11's remainder and E12 were **not measured, not
tested, and not passed**; `S360-410` stays `cataloged_unverified` (no `verified`
flip, no `schematic_file`); and **no verification is fabricated**. The waiver
also does **not** by itself flip any `config/webflash-builds.json` channel or
promote any bundle to stable — Bedroom productization and stable promotion
remain separate, explicit steps. The "do not promote to `verified`" decision
above therefore still holds; what changed is only that the **block** is now
lifted on an owner risk-acceptance basis rather than waiting on the missing
E11/E12 measurements.

---

## 7. What stays exactly the same

| Artifact | State after this PR |
|---|---|
| [`config/hardware-catalog.json`](../config/hardware-catalog.json) | `S360-410` `schematic_status` stays `cataloged_unverified`, no `schematic_file`, no `verified` claim. (HW-S360-410-WAIVER-2026-06 adds a `release_disposition` waiver field recording the owner risk-acceptance — see §0.1 — but makes no verification claim and changes neither `schematic_status` nor `schematic_file`.) |
| [`config/webflash-builds.json`](../config/webflash-builds.json) | Exactly 2 builds (`Ceiling-POE-VentIQ-RoomIQ` stable, `Ceiling-POE-VentIQ-RoomIQ-LED` preview). |
| [`config/product-catalog.json`](../config/product-catalog.json), [`config/room-bundle-skus.json`](../config/room-bundle-skus.json) | Unchanged. |
| [`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml) | Byte-identical. |
| [`firmware/sources.json`](../firmware/sources.json) / `manifest.json` | Not written / not edited. |
| Release-One flagship stable status | Unchanged — `Ceiling-POE-VentIQ-RoomIQ` stays `production` / `stable`. The PoE `"schematic verification pending"` caveat (E15) is now **closed** by the 2026-06 follow-up on the E9 + E10 basis (flagship documentation-caveat closure only; no new S360-410 hardware claim). |
| HW-002 OQ#6 / `S360-100-BENCH-001` | Preserved; still `pending`. |

---

## 8. Validation

| Command | Expected |
|---|---|
| `python3 tests/validate_configs.py` | All configs valid |
| `python3 scripts/validate_compile_targets.py --metadata-only` | Metadata validation passed |
| `python3 tests/test_product_catalog.py` | OK |
| `python3 tests/test_hardware_catalog.py` | OK; `S360-410` stays `cataloged_unverified`, no `schematic_file` |
| `python3 tests/test_roadmap_status_doc.py` | OK |
| `python3 tests/validate_webflash_builds.py` | 2 builds validated |
| `python3 -m unittest discover -s tests -p "test_*.py"` | Full suite passes |

---

## Cross-references

- PACKAGE-POE-410-001 per-evidence-class audit (E1–E15): [`docs/package-poe-410-001-audit.md`](package-poe-410-001-audit.md)
- HW-PINMAP-410 audit + audit log: [`docs/hardware/s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md)
- HW-ASSETS-410 / HW-BOM-ASSETS-002 artefact index: [`docs/hardware/artifacts/S360-410-R4.md`](hardware/artifacts/S360-410-R4.md)
- Module-side pinmap: [`docs/hardware/s360-410-module-pinmap.md`](hardware/s360-410-module-pinmap.md)
- Schematic PDF: [`docs/hardware/schematics/S360-410-R4.pdf`](hardware/schematics/S360-410-R4.pdf)
- Blocker burn-down (§2J PoE / S360-410): [`docs/blocker-burndown.md`](blocker-burndown.md)
- Roadmap / status (§6.1): [`docs/sense360-roadmap-status.md`](sense360-roadmap-status.md)
- Product readiness (§PoE-410 / S360-410): [`docs/product-readiness-matrix.md`](product-readiness-matrix.md#poe-410--s360-410)
- Release-artifact readiness (§PoE / S360-410 release posture): [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md#poe--s360-410-release-posture)
- WebFlash exposure readiness (§PoE / S360-410 WebFlash posture): [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md#poe--s360-410-webflash-posture)
- Room bundles: [`docs/sense360-room-bundles.md`](sense360-room-bundles.md)
- Hardware artifact policy: [`docs/hardware/hardware-artifact-policy.md`](hardware/hardware-artifact-policy.md)
- Release-One audit (preserved PoE caveat): [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)

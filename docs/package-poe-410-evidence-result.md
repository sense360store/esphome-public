# PACKAGE-POE-410-EVIDENCE-RESULT-001 — S360-410 PoE PSU evidence reconciliation & stable-bundle impact

## Purpose and scope

This document is the **evidence-result / reconciliation record** for
the `S360-410-R4` Sense360 PoE PSU board. It does one job: collect,
reconcile, and record every piece of S360-410 PoE-PSU evidence that is
**currently on file**, identify exactly what is **still missing**, and
determine which stable PoE room-bundle expansion blockers can be closed
versus which must remain open.

It is **evidence / reconciliation only**. It does **not** add new
evidence, run a bench, or change any hardware status. It consolidates
the per-evidence-class audit already recorded in
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
  — it is **preserved verbatim**;
- resolve HW-002 Open Question #6 (J2 PoE harness identity) or
  change `S360-100-BENCH-001` status.

PoE is SELV. `S360-410` is **not** in scope for `COMPLIANCE-001`
(mains-voltage UK / EU assessment), which scopes `S360-320` FanTRIAC
and `S360-400` 240 V PSU only.

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
| **Connector definitions (schematic-side)** | ✅ on file | [`docs/hardware/s360-410-module-pinmap.md`](hardware/s360-410-module-pinmap.md) | `J3` pin 1 = `+5VP`, pin 2 = `GND`; mates Core `J2` `PoE_ACDC` 2-pin inlet; `J3 = JST SM02B-SRSS-TB(LF)(SN)` 1×2 horizontal (BOM). |
| **Photos / renders** | ⚠️ Drive-only (retained-but-not-committed) | Drive `S360-410-R4 / images`, `step_file` | Per [`docs/hardware/hardware-artifact-policy.md`](hardware/hardware-artifact-policy.md). No silkscreen / pin-1 photograph on file. |
| **PoE-to-5 V role topology** | ✅ on file | [`docs/hardware/s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md) | Detection signature `R1 24.9k`; classification `R2 1.27k` → `Class=0 (0.44–12.95 W)`; RTN sense `R5 0.03R`; buck FB divider `R7 10.5k` / `R8 56.2k` → design set-point ≈ 5.08 V; `F0505S-2WR2` 5 V→5 V isolated DC/DC to `+5VP` / `GND`. |
| **SELV classification** | ✅ on file | [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md) | PoE input 36–57 V DC SELV; post-isolation output low-voltage. Not in COMPLIANCE-001 mains scope. |
| **Test notes (bench / link-up / load / thermal / isolation / EMI)** | ❌ none on file | — | No PoE link-up, load regulation, inrush, thermal-rise, Hi-pot, insulation-resistance, leakage, earth-continuity, or EMI/EMC report exists for `S360-410-R4`. |
| **PCB source / gerbers** | ✅ on file | [`docs/hardware/gerbers/S360-410-R4/`](hardware/gerbers/S360-410-R4/) | Complete 2-layer KiCad gerber set, 13 files (`F_Cu`/`B_Cu`, `F_Mask`/`B_Mask`, `F_Paste`/`B_Paste`, `F_Silkscreen`/`B_Silkscreen`, `Edge_Cuts`, PTH/NPTH drill + drill maps), extracted from `S360-410-R4_GERBERS.zip` (archive SHA256 `e2fb70bbeaf635cce8b36e84abefa558a496e241256500d63d2686559ae93ac8`) and committed under HW-S360-410-GERBERS-E13. Generated by KiCad Pcbnew 10.0.3, ProjectId `S360-410-R4`, units mm. Storage-backend decision (previously owed per [Hardware Artifact Policy §Future storage decision](hardware/hardware-artifact-policy.md#future-storage-decision)) is now **resolved: gerbers committed to the repo.** The editable `*.kicad_pcb` is not committed; the gerber set is sufficient for fabrication and PCB-geometry inspection. This is the granular E13 line only — it does **not** promote `S360-410` to `verified`. |
| **Prior PR evidence** | ✅ recorded | HW-ASSETS-410 / PR #516; HW-PINMAP-410-FOLLOWUP / PR #517; HW-BOM-ASSETS-002 / PR #535; PACKAGE-POE-410-001 docs-only PR #526; package-header cleanup PR #538; PRODUCT/WEBFLASH/RELEASE-POE-410-001 docs-only investigations PR #528 / #530 / #532 | The schematic, BOM, topology, and package-header-cleanup work is landed; the `verified` JSON promotion and all bench / silkscreen / harness / PCB-isolation-geometry-verification (E12) evidence remain owed. The PCB-source gerbers (E13) are now committed by HW-S360-410-GERBERS-E13. |
| **Roadmap / readiness references** | ✅ on file | [`docs/sense360-roadmap-status.md` §6.1](sense360-roadmap-status.md#61-poe--s360-410-blocker); [`docs/blocker-burndown.md`](blocker-burndown.md); [`docs/product-readiness-matrix.md` §PoE-410 / S360-410](product-readiness-matrix.md#poe-410--s360-410); [`docs/release-artifact-readiness-matrix.md` §PoE / S360-410 release posture](release-artifact-readiness-matrix.md#poe--s360-410-release-posture); [`docs/webflash-exposure-readiness-matrix.md` §PoE / S360-410 WebFlash posture](webflash-exposure-readiness-matrix.md#poe--s360-410-webflash-posture) | All record `S360-410` `cataloged_unverified` / UNRESOLVED. |

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
| **Connector orientation (`J3` pin-1)** | Schematic-side pin map (`J3` pin 1 = `+5VP`, pin 2 = `GND`); BOM connector identity (`SM02B-SRSS-TB`). | As-built silkscreen pin-1 marker photograph or KiCad PCB source confirming physical pin-1 polarity. | ❌ missing (E9) | Blocks Release-One PoE caveat closure (E15) → blocks `verified`. |
| **J2 harness compatibility** | Core `J2 PoE_ACDC` 2-pin inlet captured; module `J3` 2-pin output captured. | HW-002 OQ#6 — as-shipped Core ↔ PoE-PSU cable/pigtail identity, wire-colour map, keying/retention; `S360-100-BENCH-001` stays `pending`. | ❌ missing (E10) | Blocks Release-One PoE caveat closure (E15) → blocks `verified`. |
| **PoE negotiation / link-up** | Detection-signature `R1 24.9k` and classification `R2 1.27k` (Class 0) topology captured from schematic/BOM. | Measured link-up against an 802.3af PSE and an 802.3at PSE; signature/classification observation in hardware. | ❌ missing (E11) | Blocks `verified` and the entire A-row stable-target chain; design-intent (af-only vs af/at) unresolved (E8). |
| **5 V output validation** | Buck FB design set-point ≈ 5.08 V and `F0505S-2WR2` 5 V→5 V isolated DC/DC captured (design values only). | Measured load regulation across the rated `+5VP` range; cold-start inrush. | ⚠️ partial (E5 design / E11 bench) | Design-only; measured rows block `verified`. Output rating `or 3.3V DC` in package header is not evidenced (E8). |
| **Load testing** | None. | Per-output and aggregate load regulation; sustained-load behaviour on `+5VP`. | ❌ missing (E11) | Blocks `verified` and the production electrical-margin claim. |
| **Thermal observations** | None. | Measured thermal rise of `U1` (TPS2378), `U2` (TX4138), `DCDC1` (F0505S-2WR2) under sustained load. | ❌ missing (E11) | Blocks `verified`. |
| **Isolation / safety evidence** | `F0505S-2WR2` datasheet isolation rating only (not as-built). | Hi-pot through the isolation barrier; insulation resistance; leakage; earth continuity `H1`–`H4` → RJ45 shield / `Lan_earth`. | ❌ missing (E12) | Blocks `verified`; this is the augmented evidence class unique to S360-410 (galvanic-isolation boundary). |
| **EMI / EMC evidence** | None. | Conducted / radiated EMI/EMC against the relevant region's EN 55032 / 55035 / FCC Part 15 limits. | ❌ missing (E11) | Blocks `verified` (not a COMPLIANCE-001 mains claim; SELV). |
| **BOM cross-check (part identity)** | ✅ BOM-confirmed discrete stack (`TPS2378DDAR` + `TX4138` + `F0505S-2WR2` + `RJP-003TC1(LPJ4112CNL)`) at the part-identity layer (HW-BOM-ASSETS-002). | `F0505S-2WR2` vs `AM1D-0505S-NZ` populated-primary-vs-alternate intent (E14); package-header reconciliation decision (E8). | ✅ present (E4) / ⚠️ E8/E14 open | Does not block `verified`; E8/E14 block the `PACKAGE-POE-410-001` header-implementation PR. |
| **Manufacturing readiness** | Drive CAD/manufacturing sets present (sch_pdf / bom / cpl / gerbers / step / images); gerber set now committed at [`docs/hardware/gerbers/S360-410-R4/`](hardware/gerbers/S360-410-R4/) (E13). | `R4` silkscreen P/N / REV / date-code (tracker `G01` Waiting on logo SVG `N01`); PoE PSU rename (tracker `R11` To do). | ⚠️ partial (E9 open; E13 on file) | E9 silkscreen evidence still blocks manufacturing-evidence closure and contributes to `verified` / Release-One caveat closure; the committed gerbers close the E13 PCB-source line only. |
| **SELV classification** | ✅ PoE input 36–57 V DC SELV; post-isolation LV output; not in COMPLIANCE-001 mains scope. | None. | ✅ present (E6/E7) | None — no mains caveat applies. |

**Closed today:** board SKU/R4 (E1), schematic topology (E3), BOM part
identity (E4), PoE-to-5 V topology (E5), SELV classification (E6/E7).
**Partial:** schematic JSON promotion (E2), 5 V output (design only).
**Moved to on file (HW-S360-410-GERBERS-E13, 2026-06-08):** PCB source /
gerbers (E13) — the complete 2-layer KiCad gerber set is committed at
[`docs/hardware/gerbers/S360-410-R4/`](hardware/gerbers/S360-410-R4/)
(archive SHA256
`e2fb70bbeaf635cce8b36e84abefa558a496e241256500d63d2686559ae93ac8`).
This moves **only** the granular E13 line; it does **not** promote
`S360-410` and does **not** move E9 / E10 / E11 / E12.
**Open / missing:** connector silkscreen (E9), J2
harness (E10), PoE link-up (E11), load (E11), thermal (E11),
isolation/safety (E12), EMI/EMC (E11), package-header reconciliation
(E8), DC/DC alternate intent (E14), Release-One caveat closure (E15),
manufacturing silkscreen (E9).

Because the bench classes (E11 PoE link-up + load + thermal + EMI/EMC)
and the safety class (E12 isolation / Hi-pot / leakage / earth
continuity) are **not** derivable from a schematic + BOM and are **not
on file**, **`S360-410` cannot be promoted to `verified` today.**
Promoting it without E11 + E12 would be a fabricated verification.

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
| `S360-KIT-BATH-P` | S360-100/200/211/410 | `Ceiling-POE-VentIQ-RoomIQ` | **not blocked** (ships under preserved caveat) | This is the Release-One stable build (`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`). It already ships; the S360-410 evidence gaps keep the Release-One `"schematic verification pending"` caveat open (E15) but do **not** stop the bundle shipping. Not requalified here. |
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
reclassified, or built by this PR.

---

## 4. Precise remaining evidence requests & unblock conditions

No vague "needs verification" wording — each row names the exact
missing artefact and the exact condition that closes it. These mirror
the E-class rows in
[`docs/package-poe-410-001-audit.md` §Evidence-request record](package-poe-410-001-audit.md#evidence-request-record-precise);
this section is the reconciled, dependency-ordered view.

| Ref | Exact missing artefact | Exact unblock condition |
|---|---|---|
| **E9 — `J3` silkscreen pin-1** | Silkscreen photograph of the `S360-410-R4` PCB showing the pin-1 marker on the JST `SM02B-SRSS-TB(LF)(SN)` `J3` connector, **or** the KiCad PCB source. | Artefact ingested (retained-but-not-committed) per the Hardware Artifact Policy; physical pin-1 confirmed consistent with schematic-side `J3` pin 1 = `+5VP`. |
| **E10 — J2 harness identity (HW-002 OQ#6)** | A bench/manufacturing record on [`s360-100-r4-core.md` §S360-100-BENCH-001 status](hardware/s360-100-r4-core.md#s360-100-bench-001-status) capturing the as-shipped Core `J2` ↔ module `J3` cable/pigtail identity, wire-colour map (`+5VP` / `GND`), and keying/retention. | `S360-100-BENCH-001` moves off `pending — bench/manufacturing evidence required`; harness identity recorded and confirmed consistent across the run. |
| **E11 — PoE link-up / load / thermal / EMI/EMC bench** | A bench record (may be filed as `S360-410-BENCH-001` on [`s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md)) documenting (a) link-up vs an 802.3af PSE and an 802.3at PSE, (b) signature/classification, (c) load regulation across the rated 5 V `+5VP`, (d) cold-start inrush, (e) thermal rise of `U1`/`U2`/`DCDC1`, (f) conducted/radiated EMI/EMC. | All six sub-items measured and filed; design-intent (802.3af-only vs af/at-capable) settled by the link-up result. |
| **E12 — isolation / safety** | A safety record documenting Hi-pot through the `F0505S-2WR2` barrier (`Sw_Vin_Poe` ↔ `+5VP`/`GND`), insulation resistance, leakage current, and earth continuity `H1`–`H4` → RJ45 shield / `Lan_earth`. | As-built isolation/leakage/earth-continuity measured and filed (datasheet rating alone is **not** sufficient). |
| **E13 — PCB source / gerbers** | ✅ **Resolved (HW-S360-410-GERBERS-E13).** Complete 2-layer KiCad gerber set (13 files) committed at [`docs/hardware/gerbers/S360-410-R4/`](hardware/gerbers/S360-410-R4/); archive SHA256 `e2fb70bbeaf635cce8b36e84abefa558a496e241256500d63d2686559ae93ac8`. Storage-backend decision now resolved: gerbers committed to the repo. | Met: isolation-barrier creepage/clearance and `H1`–`H4` PCB bonding are now inspectable from the committed gerber geometry. The geometry *verification* itself remains part of E12; the editable `*.kicad_pcb` is not required. |
| **E14 — `F0505S-2WR2` vs `AM1D-0505S-NZ`** | Either a `PACKAGE-POE-410-001` header note recording `F0505S-2WR2` populated-primary / `AM1D-0505S-NZ` alternate, or a schematic-side correction PR removing a stale annotation. | Populated-primary decision recorded. |
| **E8 — package-header reconciliation** | The `PACKAGE-POE-410-001` implementation PR editing [`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml) header to cite the BOM-confirmed discrete topology, the PoE-class declaration intent, the 5 V-only output rating, and the protection-claim decision. | Four design-intent answers recorded (see §5); header reconciled; package-readiness row reclassified to `ready-for-package-change`. |
| **E2 — `schematic_status: verified` JSON PR** | A JSON-only PR flipping the `S360-410` row to `verified` and setting `schematic_file: docs/hardware/schematics/S360-410-R4.pdf`. | E9 + E10 + E11 + E12 closed first; PR passes [`tests/test_hardware_catalog.py`](../tests/test_hardware_catalog.py). |
| **E15 — Release-One PoE caveat closure** | A docs-only PR rewording the `"schematic verification pending"` caveat at [`release-one-hardware-audit.md` Findings → PoE PSU](release-one-hardware-audit.md#findings). | E2 + E8 + E9 + E10 + E11 + E12 closed. Unblocks the G8 inherited-caveat axis for every Release-One-shape PoE stable target. |

**Dependency order:** E9 + E10 + E11 + E12 (evidence) → E2 (`verified`
JSON) and E8/E14 (package header) → E15 (caveat closure) → A-row
stable-target G8 closure → `S360-KIT-BEDROOM-P` and (with their own
extra evidence) `KITCHEN-P` / `LIVING-P` / `CORRIDOR-P`.

---

## 5. Next-evidence checklist (operator / designer requests)

Exact requests the hardware owner / designer must answer or supply to
close the remaining gaps. Each maps to an E-class above.

**Operator bench / fixture requests (close E9–E12):**

1. Photograph the `S360-410-R4` PCB silkscreen at connector `J3`,
   clearly showing the pin-1 marker. *(E9)*
2. Record the physical Core `J2` ↔ module `J3` harness used on a
   shipped unit: cable/pigtail type, wire-colour-to-`+5VP`/`GND` map,
   any keying/retention. *(E10)*
3. Bench the assembled board against **both** an 802.3af PSE and an
   802.3at PSE; record link-up, signature, and classification. *(E11)*
4. Measure load regulation across the rated 5 V `+5VP` output, plus
   cold-start inrush. *(E11)*
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
> promote any stable bundle or release target, do not enable any
> WebFlash target, and do not reword the Release-One PoE caveat in this
> PR.** The bench (E11), isolation/safety (E12), connector-silkscreen
> (E9), and J2-harness (E10) evidence classes are **not on file**. The
> PCB-source (E13) class is now **on file** — gerbers committed at
> [`docs/hardware/gerbers/S360-410-R4/`](hardware/gerbers/S360-410-R4/) by
> HW-S360-410-GERBERS-E13 — which records the artifact but does **not** by
> itself verify the board. This PR records the consolidated evidence matrix,
> the stable-bundle impact assessment, the precise remaining-evidence
> list, and the operator/designer next-evidence checklist, and keeps
> `S360-410` `cataloged_unverified`.

This is the option-4 outcome: evidence is insufficient for
verification, so no verification is fabricated and a precise
evidence-request record is produced instead.

---

## 7. What stays exactly the same

| Artifact | State after this PR |
|---|---|
| [`config/hardware-catalog.json`](../config/hardware-catalog.json) | `S360-410` row byte-identical (`cataloged_unverified`, no `schematic_file`). |
| [`config/webflash-builds.json`](../config/webflash-builds.json) | Exactly 2 builds (`Ceiling-POE-VentIQ-RoomIQ` stable, `Ceiling-POE-VentIQ-RoomIQ-LED` preview). |
| [`config/product-catalog.json`](../config/product-catalog.json), [`config/room-bundle-skus.json`](../config/room-bundle-skus.json) | Unchanged. |
| [`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml) | Byte-identical. |
| [`firmware/sources.json`](../firmware/sources.json) / `manifest.json` | Not written / not edited. |
| Release-One PoE caveat | Preserved verbatim. |
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

# PACKAGE-POE-410-001 — S360-410 PoE PSU package-readiness audit (no promotion)

## Purpose and scope

This document is the **package-readiness audit record** for the
`S360-410-R4` Sense360 PoE PSU board against the
`PACKAGE-POE-410-001` slice. It answers the question

> *"Can `S360-410` move from `schematic_status: cataloged_unverified`
> to `verified` today, can it close `PACKAGE-POE-410-001` today, and
> what is the precise evidence still missing for each remaining
> downstream slice (`PRODUCT-POE-410-001`, the Release-One PoE
> caveat closure, the stable expansion targets `Ceiling-POE`,
> `Ceiling-POE-RoomIQ`, `Ceiling-POE-VentIQ`, `Ceiling-POE-AirIQ`,
> `Ceiling-POE-AirIQ-RoomIQ`)?"*

The audit reads from the already-committed schematic
([`docs/hardware/schematics/S360-410-R4.pdf`](hardware/schematics/S360-410-R4.pdf),
HW-ASSETS-410 / PR #516), the BOM-evidence ingest record
([`docs/hardware/artifacts/S360-410-R4.md` §HW-BOM-ASSETS-002 BOM ingest (2026-05-20)](hardware/artifacts/S360-410-R4.md#hw-bom-assets-002-bom-ingest-2026-05-20)),
the HW-PINMAP-410 audit doc
([`docs/hardware/s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md),
HW-PINMAP-410-FOLLOWUP / PR #517 + HW-BOM-ASSETS-002 audit-log
addendum), the per-board / per-package / per-product / per-WebFlash /
per-release readiness matrices, the Release-One audit
([`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)),
and the stable-target expansion plan
([`docs/stable-target-expansion-plan.md`](stable-target-expansion-plan.md)
/ STABLE-TARGET-EXPANSION-PLAN-001 / PR #630) plus the gate-closure
record
([`docs/stable-target-ventiq-001-gate-closure.md`](stable-target-ventiq-001-gate-closure.md)
/ STABLE-TARGET-VENTIQ-001 / PR #632). Nothing is asserted beyond
what those sources already record.

The audit answers the question with **option 4** in the task brief:
**evidence is insufficient to move `S360-410` to `verified`** and
insufficient to land the `PACKAGE-POE-410-001` package-header
reconciliation today. The audit therefore takes the precise
evidence-request path: it records the exact remaining schematic /
silkscreen / bench / harness / compliance evidence still owed, names
the operator / designer question that drives each item, lists the
stable-expansion targets that remain blocked behind the slice, and
**keeps `S360-410` `cataloged_unverified`**.

### Hard guardrails

PACKAGE-POE-410-001 — this PR — does **not**:

- publish, build, or attach any firmware artifact, and creates no
  GitHub Release;
- commit any `.bin`, checksum, or build-info file;
- edit any YAML under [`products/`](../products/),
  [`products/webflash/`](../products/webflash/), or
  [`products/compile-only/`](../products/compile-only/);
- edit any package YAML under [`packages/`](../packages/) — in
  particular,
  [`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml)
  stays byte-identical to PR #517 / PR #526 (the stale
  `Ag9712M, Silvertel Ag9700, or similar` header at line 6, the
  `IEEE 802.3af (PoE) or 802.3at (PoE+)` standard line at line 7,
  the `Class 0 (0.44-12.95W) or Class 1 (0.44-3.84W)` class line at
  line 8, the `36-57V DC` input line at line 9, the
  `5V DC, 2A (10W) or 3.3V DC` output line at line 10, and the
  `Overcurrent, overvoltage, short-circuit` protection line at line
  11 are all **preserved**; comment-only cleanup is deferred to a
  later `PACKAGE-POE-410-001` implementation PR that also lands the
  Release-One PoE caveat closure);
- add, remove, or modify any entry in
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  [`config/product-catalog.json`](../config/product-catalog.json),
  [`config/compile-only-targets.json`](../config/compile-only-targets.json),
  [`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json),
  [`config/compile-only-candidates.json`](../config/compile-only-candidates.json),
  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json),
  or [`config/room-bundle-skus.json`](../config/room-bundle-skus.json);
- promote `S360-410` `schematic_status` from `cataloged_unverified`
  to `verified` in
  [`config/hardware-catalog.json`](../config/hardware-catalog.json),
  set `schematic_file` for `S360-410`, or change the `description`
  field;
- write [`firmware/sources.json`](../firmware/sources.json) or
  `manifest.json`;
- promote `Ceiling-POE-VentIQ`, `Ceiling-POE`, `Ceiling-POE-RoomIQ`,
  `Ceiling-POE-AirIQ`, or `Ceiling-POE-AirIQ-RoomIQ` from
  `compile-only` to `stable-candidate-after-promotion`,
  `preview-release`, or `stable-release`;
- promote LED from `preview` to `stable`;
- promote FanRelay / FanPWM / FanDAC out of `manual-candidate-only`;
- add an `artifact_name` to any fan product;
- flip any `webflash_build_matrix` value;
- add a WebFlash build row, a WebFlash wrapper, or any new product
  catalog row for a PoE-410-explicit product;
- reword or remove the Release-One PoE
  `"schematic verification pending"` caveat at
  [`docs/release-one-hardware-audit.md` Findings → PoE PSU](release-one-hardware-audit.md#findings)
  — the caveat is **preserved verbatim**;
- claim IEEE 802.3af / 802.3at compliance, isolation rating /
  Hi-pot / insulation resistance / earth-continuity / leakage,
  thermal / EMI / EMC qualification, or any PoE link-up / bench /
  load evidence;
- claim S360-410 verified unless schematic + BOM + silkscreen +
  bench + isolation + J2-harness evidence are all on file;
- fabricate any schematic, BOM, silkscreen, bench, or compliance
  evidence;
- change the mains-voltage compliance status of `S360-320` or
  `S360-400` (COMPLIANCE-001 unchanged; `S360-410` PoE PSU is **not**
  in scope because PoE is SELV);
- resolve HW-002 Open Question #6 (J2 PoE harness identity) or
  change `S360-100-BENCH-001` status away from
  `pending — bench/manufacturing evidence required`;
- advance `CORE-ABSTRACT-BUS-001A` / `001B` / `001C`, `HW-005`
  (FanTRIAC), `S360-300-BENCH-001` (LED), or any unrelated
  per-family slice.

---

## Inputs read

This audit reads from the committed catalogs, schematic / BOM /
audit-doc evidence, readiness matrices, and Release-One audit;
nothing is asserted beyond what they already record.

| Source | File |
|---|---|
| Hardware catalog (per-SKU `schematic_status`) | [`config/hardware-catalog.json`](../config/hardware-catalog.json) |
| Product catalog | [`config/product-catalog.json`](../config/product-catalog.json) |
| Release matrix (sole release-eligibility source) | [`config/webflash-builds.json`](../config/webflash-builds.json) |
| Room bundle SKUs | [`config/room-bundle-skus.json`](../config/room-bundle-skus.json) |
| WebFlash compatibility grammar | [`config/webflash-compatibility.json`](../config/webflash-compatibility.json) |
| Module-side schematic PDF | [`docs/hardware/schematics/S360-410-R4.pdf`](hardware/schematics/S360-410-R4.pdf) |
| Curated artifact index + BOM ingest record | [`docs/hardware/artifacts/S360-410-R4.md`](hardware/artifacts/S360-410-R4.md) |
| Pin / package mapping audit | [`docs/hardware/s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md) |
| Per-board readiness | [`docs/hardware/board-readiness-matrix.md`](hardware/board-readiness-matrix.md) |
| Per-package readiness | [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md) |
| Firmware-package mapping audit | [`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md) |
| Logical PoE package YAML | [`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml) |
| Core reference (Core `J2` `PoE_ACDC` capture) | [`docs/hardware/s360-100-r4-core.md`](hardware/s360-100-r4-core.md) |
| Release-One audit (PoE PSU findings + required follow-ups) | [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md) |
| Product readiness | [`docs/product-readiness-matrix.md`](product-readiness-matrix.md) |
| WebFlash exposure readiness | [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md) |
| Release-artifact readiness | [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md) |
| All-YAML release matrix | [`docs/all-yaml-release-matrix.md`](all-yaml-release-matrix.md) |
| Room-firmware release matrix | [`docs/room-firmware-release-matrix.md`](room-firmware-release-matrix.md) |
| Stable target expansion plan | [`docs/stable-target-expansion-plan.md`](stable-target-expansion-plan.md) |
| STABLE-TARGET-VENTIQ-001 gate-closure record | [`docs/stable-target-ventiq-001-gate-closure.md`](stable-target-ventiq-001-gate-closure.md) |
| Compliance tracker (mains only; PoE is SELV / out of scope) | [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md) |

---

## Board identity (read-only)

Mirrored verbatim from
[`config/hardware-catalog.json`](../config/hardware-catalog.json)
lines 112–121.

| Field | Value |
|---|---|
| `group` | `Power` |
| `type` | `PSU` |
| `friendly_name` | `Sense360 PoE PSU` |
| `sku` | `S360-410` |
| `rev` | `R4` |
| `old_name` | `PoE Module` |
| `description` | `PoE to 5V.` |
| `schematic_status` | `cataloged_unverified` (unchanged by this PR) |
| `schematic_file` | _(not set; unchanged by this PR)_ |

PoE is SELV. `S360-410` is **not** in scope for `COMPLIANCE-001`
(mains-voltage UK / EU assessment), which scopes `S360-320`
FanTRIAC and `S360-400` 240 V PSU only.

---

## Per-evidence-class audit

This is the per-evidence-class audit derived directly from the
committed sources cited in [Inputs read](#inputs-read). Status
keys: ✅ on file (evidence exists in repo or in retained-but-not-
committed BOM ingest); ⚠️ partial (some artefact exists but the
evidence class is not fully closed); ❌ missing (no evidence on
file).

| # | Evidence class | What this slice needs | Status today | Owning closure |
|---|---|---|---|---|
| E1 | **Board SKU canonical & R4 revision** | `S360-410` row with `rev: R4` and canonical naming present in [`config/hardware-catalog.json`](../config/hardware-catalog.json) | ✅ on file — row at lines 112–121 carries `sku: S360-410`, `rev: R4`, `friendly_name: Sense360 PoE PSU`, `group: Power`, `type: PSU`. Naming locked by [`tests/test_hardware_catalog.py`](../tests/test_hardware_catalog.py). | n/a — gate already closed |
| E2 | **Module-side schematic PDF committed** | A KiCad-exported PDF for `S360-410-R4` committed under [`docs/hardware/schematics/`](hardware/schematics/) and recorded in [`config/hardware-catalog.json`](../config/hardware-catalog.json) as `schematic_file` | ⚠️ partial — PDF committed at [`docs/hardware/schematics/S360-410-R4.pdf`](hardware/schematics/S360-410-R4.pdf) under HW-ASSETS-410 / PR #516 (975,137 bytes; SHA256 `4a8b7a3b2a89006a9332eaa486743f687aaedc4b6bb807c6b25670f742ac2414`) — **but the JSON `schematic_file` pointer has not been set and `schematic_status` has not been promoted**. The HW-PINMAP-410 audit doc at [`docs/hardware/s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md) consumed the PDF (HW-PINMAP-410-FOLLOWUP / PR #517) and reached `partial — schematic evidence available; package reconciliation, PoE PD controller / magnetics / buck / isolated DC/DC / harness identity evidence pending`. | A separate `S360-410-SCHEMATIC-STATUS-VERIFIED` JSON-only PR (after the remaining evidence rows close), which sets `schematic_file: docs/hardware/schematics/S360-410-R4.pdf` and flips `schematic_status` to `verified`. **Not this PR.** |
| E3 | **Schematic-shown discrete topology captured** | Per-symbol pin maps and net topology recorded against the PDF | ✅ on file — [`docs/hardware/s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md) captures `LAN_CON1 = RJP-003TC1(LPJ4112CNL)` magnetics / RJ45 module, `U1 = TPS2378DDAR(HSOIC-8)` PoE PD controller, `U2 = TX4138(ESOIC-8)` buck regulator, `DCDC1 = F0505S-2WR2(SIP-7)` isolated DC/DC, `J3` 2-pin "Connection to Cores" output, `D3 Green` indicator, `H1`–`H4` `Earth` mounting holes, and the pre-isolation / post-isolation net topology (`Spare1` / `Spare2` / `Lan_earth` / `PoE_Power` / `PoE_SW` / `Sw_Vin_Poe` / `Earth` → `+5VP` / `GND`). | n/a — already closed by HW-PINMAP-410-FOLLOWUP / PR #517 |
| E4 | **BOM cross-check** | Per-component manufacturer / part-number rows for every load-bearing schematic symbol, with footprints, to confirm the discrete-topology part identities | ✅ on file (retained-but-not-committed) — `S360-410-R4_BOM.xlsx` (11,980 bytes; SHA256 `b5f4bad842a930de03cd47327f477c21afcb82e4533a9d8be38b54990b38f285`) ingested under `HW-BOM-ASSETS-002` and inventoried at [`docs/hardware/artifacts/S360-410-R4.md` §HW-BOM-ASSETS-002 BOM ingest (2026-05-20)](hardware/artifacts/S360-410-R4.md#hw-bom-assets-002-bom-ingest-2026-05-20). BOM-confirms `U1 = TPS2378DDAR` (TI), `U2 = TX4138` (XDS), `DCDC1 = F0505S-2WR2` (EVISUN) **only** (the schematic-annotated `AM1D-0505S-NZ` does not appear in the BOM), `LAN_CON1 = LPJ4112CNL` (Link-PP) magnetics in `RJP-003TC1` footprint, `R1 = 24.9k` (EVER OHMS) DEN, `R2 = 1.27k` (PANASONIC) CLS-Class-0, `R3, R4 = 9.1k` (UNI-ROYAL) paired ILIM, `R5 = 0.03R` (YAGEO) RTN, `R6 = 4.7R` (FOJAN), `R7 = 10.5k` (KOA) Rd, `R8 = 56.2k` (FOJAN) Rc, `R9 = 1k` (UNI-ROYAL) bleed, `L1 = 33uH` (Yanchuang, Bourns SRN8040TA footprint), `D1 = SMAJ58A` (Littelfuse) TVS, `D2 = ss510` (MDD `SS510C`) catch, `D3 = Green` (Orient `ORH-G36G-B`) indicator, bulk / decoupling caps, and `J3 = JST SM02B-SRSS-TB(LF)(SN)` 1×2 horizontal. | n/a — already closed at the part-identity layer by `HW-BOM-ASSETS-002` |
| E5 | **PoE-to-5 V role topology** | Stage-by-stage capture: PoE PD signature / classification → PoE pass MOSFET drain → buck regulation to ~5 V → isolated DC/DC to Core-facing `+5VP` / `GND` | ✅ on file — captured in [`docs/hardware/s360-410-r4-poe.md` §PoE PD controller findings](hardware/s360-410-r4-poe.md#poe-pd-controller-findings), [§Buck stage findings](hardware/s360-410-r4-poe.md#buck-stage-findings), [§Isolated DC/DC findings](hardware/s360-410-r4-poe.md#isolated-dcdc-findings), and [§Output / +5VP / GND findings](hardware/s360-410-r4-poe.md#output--5vp--gnd-findings). PoE detection signature `R1 24.9k`; classification `R2 1.27k` → `Class=0 (0.44 to 12.95W)`; CBULK `C2 15uF` on TPS2378 input; RTN sense `R5 0.03R`; buck FB divider `R7 10.5k` (Rd) / `R8 56.2k` (Rc) → design set-point `Vout = 0.8 × (1 + Rc/Rd) ≈ 5.08 V` on `Sw_Vin_Poe`; isolated DC/DC `F0505S-2WR2` 5 V → 5 V to `+5VP` / `GND`. | n/a — closed at the topology layer by HW-PINMAP-410-FOLLOWUP / PR #517 |
| E6 | **SELV-side classification** | Confirmation that the entire board is SELV (no mains-voltage rail), so COMPLIANCE-001 does not apply | ✅ on file — PoE input is 36–57 V DC SELV from a PSE; post-isolation Core-facing output is `+5VP` / `GND` low-voltage. `S360-410` is **not** in scope for `COMPLIANCE-001` per [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md) (mains-voltage tracker scopes `S360-320` FanTRIAC and `S360-400` 240 V PSU only). | n/a — gate already closed |
| E7 | **Mains / compliance caveat** | Any caveat tying `S360-410` to mains-voltage compliance (would gate the slice if present) | ✅ none applies — PoE is SELV. No mains caveat to discharge. | n/a — gate already closed |
| E8 | **Package-header identity reconciliation** | The [`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml) header (`Ag9712M, Silvertel Ag9700, or similar` line 6; `IEEE 802.3af (PoE) or 802.3at (PoE+)` line 7; `Class 0 (0.44-12.95W) or Class 1 (0.44-3.84W)` line 8; `36-57V DC` line 9; `5V DC, 2A (10W) or 3.3V DC` line 10; `Overcurrent, overvoltage, short-circuit` line 11) must be reconciled against the schematic-shown / BOM-confirmed discrete topology | ❌ open — disagreement recorded by HW-PINMAP-410-FOLLOWUP / PR #517 and re-confirmed by `HW-BOM-ASSETS-002`. The whole-module hint `Ag9712M, Silvertel Ag9700, or similar` is **disproved** by the BOM (neither part appears anywhere in the BOM); the BOM-confirmed populated parts are the discrete `TPS2378DDAR` + `TX4138` + `F0505S-2WR2` + `RJP-003TC1(LPJ4112CNL)` stack. The package YAML has **not** been edited; comment-only cleanup is deferred to the `PACKAGE-POE-410-001` implementation PR. Also unresolved: PoE class declaration intent (the BOM-confirmed `R2 1.27k` is consistent with the schematic-recorded `Class=0 (0.44 to 12.95W)`, but whether the design is intended as 802.3af-only or 802.3af/at-capable is a design-intent question the BOM does not by itself settle); output rating (BOM and schematic evidence the 5 V output only; the `or 3.3V DC` package-header option is not evidenced); protection claim (the `Overcurrent, overvoltage, short-circuit` claim is not directly BOM-evidenced — qualifying the combined TPS2378 + TX4138 + F0505S-2WR2 stack against a specific PoE-load failure mode is bench evidence). | A future `PACKAGE-POE-410-001` implementation PR that lands the package-header comment cleanup + BOM citation + design-intent decision as a single coordinated slice, after the Release-One PoE caveat closure, HW-002 OQ#6 / S360-100-BENCH-001 J2-harness closure, and the `S360-410 schematic_status: verified` JSON PR are all in place. **Not this PR.** |
| E9 | **`J3` silkscreen pin-1 marker** | Module-side silkscreen pin-1 marker on the `J3` 2-pin Core-facing connector (BOM `MFR# = SM02B-SRSS-TB(LF)(SN)`) | ❌ open — silkscreen photo / KiCad PCB source for `S360-410-R4` not on file. The schematic-side pin map (`J3` pin 1 = `+5VP`, pin 2 = `GND`) is on file; the **as-built** pin-1 orientation must be confirmed against silkscreen evidence. Schematic-side capture lives at [`docs/hardware/s360-410-r4-poe.md` §J3 Core-facing output (2-pin)](hardware/s360-410-r4-poe.md#j3-core-facing-output-2-pin). | Silkscreen photographs or KiCad PCB source for `S360-410-R4`, ingested as a retained-but-not-committed evidence class per the [Hardware Artifact Policy](hardware/hardware-artifact-policy.md). |
| E10 | **HW-002 Open Question #6 / `S360-100-BENCH-001` J2-harness identity** | Definitive cable / pigtail identity between the off-board `S360-410` module-side `J3` 2-pin and Core-side `J2 PoE_ACDC` 2-pin | ❌ open — tracked at [`docs/hardware/s360-100-r4-core.md` Open questions](hardware/s360-100-r4-core.md#open-questions--verification-needed) (HW-002 OQ#6) and [§S360-100-BENCH-001 status](hardware/s360-100-r4-core.md#s360-100-bench-001-status) (`pending — bench/manufacturing evidence required`). | A bench / manufacturing evidence-bearing PR that observes the as-shipped Core ↔ PoE-PSU harness and records the result on `S360-100-BENCH-001`. **Not this PR.** |
| E11 | **Bench / load / PoE link-up / thermal / EMI / EMC evidence** | PoE link-up against an 802.3af PSE and an 802.3at PSE; signature / classification observation; load regulation across the rated 5 V `+5VP` output; cold-start inrush; thermal rise of `U1` / `U2` / `DCDC1` under sustained load; conducted / radiated EMI / EMC | ❌ open — no bench, load, link-up, thermal, or EMI / EMC reports on file. | A separate bench-evidence PR (or sequence) once test fixtures are available. **Not this PR.** PoE is SELV and is not in scope for `COMPLIANCE-001`; a future PoE-compliance evidence class (separate from `COMPLIANCE-001`) is owed if the slice ever needs an explicit PoE-compliance claim. |
| E12 | **Isolation / Hi-pot / earth-continuity / leakage evidence** | Insulation resistance / Hi-pot through the `F0505S-2WR2(SIP-7)` isolation barrier between `Sw_Vin_Poe` and `+5VP` / `GND`; earth continuity from `H1`–`H4` to the RJ45 shield / `Lan_earth` rail | ❌ open — `F0505S-2WR2` isolation rating is a datasheet claim only; as-built insulation resistance / Hi-pot / leakage and `H1`–`H4` PCB-level bonding to `Lan_earth` are bench evidence and are not on file. | A separate isolation / safety evidence PR once test fixtures are available. **Not this PR.** |
| E13 | **PCB-level evidence** | KiCad PCB source (`*.kicad_pcb`) and / or gerbers — required to verify isolation-barrier widths around `F0505S-2WR2` and PCB-level electrical bonding of `H1`–`H4` to `Lan_earth` / `Earth` / RJ45 shield | ❌ open — neither KiCad PCB source nor a gerbers archive for `S360-410-R4` is on file; storage-backend decision per the [Hardware Artifact Policy §Future storage decision](hardware/hardware-artifact-policy.md#future-storage-decision) still owed. | A future per-board manufacturing-evidence PR once a storage backend for KiCad PCB / gerbers is chosen. **Not this PR.** |
| E14 | **`F0505S-2WR2` vs `AM1D-0505S-NZ` primary-vs-alternate intent** | Whether the schematic-annotated `AM1D-0505S-NZ` (which does not appear in the BOM) is a purchasing-side alternate, a future-revision option, or stale schematic annotation | ❌ open — the BOM lists only `F0505S-2WR2` as the populated `DCDC1` part. Resolution is owed either to a `PACKAGE-POE-410-001` implementation PR (recording the populated-primary decision in the package header alongside the BOM citation) or to a schematic-side correction PR. | The next `PACKAGE-POE-410-001` implementation PR or a schematic-side correction PR. **Not this PR.** |
| E15 | **Release-One PoE `"schematic verification pending"` caveat closure** | Reword the caveat at [`docs/release-one-hardware-audit.md` Findings → PoE PSU](release-one-hardware-audit.md#findings) and [Required follow-ups #6](release-one-hardware-audit.md#required-follow-ups) once E2 + E8 + E9 + E10 + E11 + E12 close | ❌ open — caveat preserved verbatim by HW-ASSETS-410 / PR #516, HW-PINMAP-410-FOLLOWUP / PR #517, `HW-BOM-ASSETS-002`, and **this PR**. | A separate Release-One PoE caveat-closure PR once E2 / E8–E12 close. **Not this PR.** |

**Evidence-classes closed today:** 6 of 15 (E1, E3, E4, E5, E6, E7).
**Evidence-classes open today:** 7 of 15 (E2 partial pending JSON PR; E8, E9, E10, E11, E12, E13, E14, E15 open).

> **Update — `HW-S360-410-EVIDENCE-2026-06` (2026-06-08).** The two counts
> above are the original 2026-05-28 audit snapshot. The S360-410 PoE
> evidence gathered in 2026-06 (recorded in
> [`docs/package-poe-410-evidence-result.md` §0](package-poe-410-evidence-result.md))
> moves several rows **without promoting the board**:
> - **E13** PCB source / gerbers → **on file** (HW-S360-410-GERBERS-E13:
>   complete 2-layer KiCad gerber set committed at
>   [`docs/hardware/gerbers/S360-410-R4/`](hardware/gerbers/S360-410-R4/),
>   archive SHA256
>   `e2fb70bbeaf635cce8b36e84abefa558a496e241256500d63d2686559ae93ac8`).
> - **E9** `J3` connector pin-1 polarity → **on file** on a CAD-render +
>   as-labeled-connector basis (on-header signal-name silkscreen `5V` /
>   `GND` plus KiCad 3D CAD renders, six views). No physical as-built pin-1
>   photograph and no `.kicad_pcb` net-map were provided; pin-1 polarity is
>   assured by the on-header signal labels rather than by pin number.
> - **E10** J2 harness identity → **on file (spec)**: 2-conductor lead PSU
>   `J3` (`SM02B-SRSS-TB`, 1×2) → Core `J2 PoE_ACDC`, `+5VP`→`+5VP` /
>   `GND`→`GND`, polarized JST housing, both ends silkscreen-labeled,
>   JST-latch retention; the as-shipped wire-colour map is
>   informational-only, not a safety gate (keyed connector).
> - **E11** bench → **PARTIAL**: PoE link-up confirmed and 5 V conversion
>   confirmed (multimeter); load regulation, cold-start inrush, thermal
>   rise, and EMI/EMC **not measured**.
> - **E15** Release-One PoE caveat → **CLOSED** on the E9 + E10 basis — a
>   flagship documentation-caveat closure that changes no stable status and
>   makes no S360-410 `verified` claim.
>
> Still open / missing: **E2** (`verified` JSON flip), the **E11 bench
> remainder** (load + inrush + thermal + EMI/EMC), **E12** isolation /
> safety (Hi-pot / insulation / leakage / earth continuity, untouched), and
> **E8 / E14** package-header reconciliation. `S360-410` therefore **stays
> `cataloged_unverified`**; the row narratives below remain the 2026-05-28
> historical record.

Because E2 is still partial (the JSON `schematic_status: verified`
promotion has not landed), and because E8–E15 are open, **`S360-410`
cannot be promoted to `verified` today** and the `PACKAGE-POE-410-001`
implementation PR (package-header cleanup + BOM citation + design-
intent decision) cannot land today. The audit therefore takes
option 4: it records the precise evidence-request list above and
keeps `S360-410` `cataloged_unverified`.

---

## Evidence-request record (precise)

For each open / partial row above, the following is the precise
evidence request, the operator / designer question that drives it,
and the stable expansion targets that remain blocked behind it.

> **2026-06 status.** Several of these classes have since moved — E9 / E10
> are on file, E11 is partial, E13 is on file, and E15 is closed; see the
> `HW-S360-410-EVIDENCE-2026-06` update above and
> [`docs/package-poe-410-evidence-result.md` §0](package-poe-410-evidence-result.md).
> The per-class prose below is the 2026-05-28 snapshot kept for the
> historical evidence-request record. `S360-410` stays
> `cataloged_unverified` (E2 + the E11 bench remainder + E12 still open).

### E2 — `S360-410` `schematic_status: verified` JSON-only PR

- **Exact missing artefact.** A JSON-only PR against
  [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  that, after E8 + E9 + E10 close, flips the `S360-410` row at
  lines 112–121 from `schematic_status: cataloged_unverified` to
  `schematic_status: verified` and sets `schematic_file:
  docs/hardware/schematics/S360-410-R4.pdf`. Per the precedent set
  by HW-008 for `S360-100` / `S360-200` / `S360-210` / `S360-211` /
  `S360-300`, that PR must also pass
  [`tests/test_hardware_catalog.py`](../tests/test_hardware_catalog.py)
  (every `verified` entry must carry a non-empty `schematic_file`
  and the file must resolve under the repo root).
- **Operator / designer question.** None — this PR is mechanical
  once E8 + E9 + E10 close. The precondition gate is the closure
  of the upstream evidence rows, not a design question.
- **Stable expansion targets blocked.** All five A-row candidates
  in [`docs/stable-target-expansion-plan.md` §A. Non-fan / non-LED /
  non-TRIAC room combos](stable-target-expansion-plan.md#a-non-fan--non-led--non-triac-room-combos)
  (`Ceiling-POE`, `Ceiling-POE-RoomIQ`, `Ceiling-POE-VentIQ`,
  `Ceiling-POE-AirIQ`, `Ceiling-POE-AirIQ-RoomIQ`) — each row's G8
  (hardware / compliance) gate is open behind this JSON PR.

### E8 — Package-header identity reconciliation (`PACKAGE-POE-410-001` implementation)

- **Exact missing artefact.** A `PACKAGE-POE-410-001` implementation
  PR that edits
  [`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml)
  header lines 6–11 to (a) replace the `Ag9712M, Silvertel Ag9700,
  or similar` whole-module hint with a citation of the
  BOM-confirmed discrete `TPS2378DDAR` + `TX4138` + `F0505S-2WR2`
  + `RJP-003TC1(LPJ4112CNL)` topology, (b) record the PoE class
  declaration intent (802.3af-only vs 802.3af/at-capable),
  (c) align the output rating (the BOM and schematic evidence the
  5 V output only; the `or 3.3V DC` option is not evidenced), and
  (d) keep or remove the `Overcurrent, overvoltage, short-circuit`
  claim based on the design-intent decision. The PR must cite the
  BOM ingest at
  [`docs/hardware/artifacts/S360-410-R4.md` §HW-BOM-ASSETS-002 BOM ingest (2026-05-20)](hardware/artifacts/S360-410-R4.md#hw-bom-assets-002-bom-ingest-2026-05-20)
  inline and update
  [`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
  / [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md)
  to reclassify the package row from `schematic-evidence-pending` to
  `ready-for-package-change` (or its successor enum).
- **Operator / designer question.**
  1. *"Is the S360-410-R4 design intended as 802.3af-only, or
     802.3af / 802.3at-capable?"* The schematic-recorded / BOM-
     confirmed `R2 1.27k` (Class 0, 0.44 to 12.95 W) is consistent
     with 802.3af-only, but the package-header text presently says
     "802.3af (PoE) or 802.3at (PoE+)" and "Class 0 … or Class 1".
     The design-intent answer drives the header cleanup wording.
  2. *"Is the `or 3.3V DC` output option in the package header
     intentional, or stale?"* The schematic-recorded FB divider
     `R7 10.5k` / `R8 56.2k` → 5.08 V design set-point and the
     BOM-confirmed `F0505S-2WR2` (5 V → 5 V isolated DC/DC) evidence
     the 5 V output only. The header `or 3.3V DC` option is not
     evidenced.
  3. *"Should the `Overcurrent, overvoltage, short-circuit`
     protection claim be kept (and which device is the source —
     TPS2378 OVT, TX4138 ILIM, F0505S-2WR2 datasheet), or removed
     pending bench evidence?"*
  4. *"Should the schematic-annotated `AM1D-0505S-NZ` alternate be
     documented in the package header (`F0505S-2WR2` populated
     primary; `AM1D-0505S-NZ` purchasing-side alternate), or
     removed from the schematic by a separate correction PR (see
     E14)?"*
- **Stable expansion targets blocked.** The same five A-row
  candidates (`Ceiling-POE`, `Ceiling-POE-RoomIQ`,
  `Ceiling-POE-VentIQ`, `Ceiling-POE-AirIQ`,
  `Ceiling-POE-AirIQ-RoomIQ`) — each row's G8 gate requires the
  package to carry `ready-for-package-change` per
  [`docs/hardware/package-readiness-matrix.md` `power_poe.yaml` / S360-410](hardware/package-readiness-matrix.md#power_poeyaml--s360-410).

### E9 — `J3` silkscreen pin-1 marker evidence

- **Exact missing artefact.** Silkscreen photographs of the
  `S360-410-R4` PCB showing the pin-1 marker on the JST
  `SM02B-SRSS-TB(LF)(SN)` 1×2 horizontal connector at reference
  `J3`, **or** the KiCad PCB source (`S360-410-R4.kicad_pcb`)
  ingested as retained-but-not-committed evidence under the
  [Hardware Artifact Policy](hardware/hardware-artifact-policy.md).
- **Operator / designer question.** *"Which physical pin on the
  module-side `J3` connector is pin 1 (`+5VP`) as silkscreened on
  the board, and is the polarity consistent with the
  schematic-side capture (pin 1 = `+5VP`, pin 2 = `GND`)?"*
- **Stable expansion targets blocked.** Same five A-row
  candidates, indirectly — E9 must close before E15 (Release-One
  PoE caveat closure) can land.

### E10 — HW-002 OQ#6 / `S360-100-BENCH-001` J2-harness identity

- **Exact missing artefact.** A bench / manufacturing evidence
  record on
  [`docs/hardware/s360-100-r4-core.md` §S360-100-BENCH-001 status](hardware/s360-100-r4-core.md#s360-100-bench-001-status)
  that observes the as-shipped Core ↔ PoE-PSU harness and records
  (a) the cable / pigtail identity (e.g. JST SH 1×2 harness; molex
  pigtail; loose-wire), (b) the wire colour map (which conductor
  carries `+5VP`; which carries `GND`), and (c) any keying /
  retention features.
- **Operator / designer question.** *"Which physical harness is
  used between the off-board `S360-410` PoE PSU module (`J3` JST
  SH 1×2) and the Sense360 Core (`J2 PoE_ACDC` 2-pin inlet), and
  is the harness identity consistent across the manufactured
  run?"* — HW-002 Open Question #6 verbatim.
- **Stable expansion targets blocked.** Same five A-row
  candidates; required before E15 can land.

### E11 — Bench / load / PoE link-up / thermal / EMI / EMC evidence

- **Exact missing artefact.** A bench evidence record that
  documents (a) PoE link-up against an 802.3af PSE and an 802.3at
  PSE, (b) signature / classification observation, (c) load
  regulation across the rated 5 V `+5VP` output range, (d)
  cold-start inrush behaviour, (e) thermal rise of `U1`
  (TPS2378DDAR), `U2` (TX4138), and `DCDC1` (F0505S-2WR2) under
  sustained load, and (f) conducted / radiated EMI / EMC. May be
  filed as a new per-board bench record (`S360-410-BENCH-001`) on
  [`docs/hardware/s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md).
- **Operator / designer question.**
  1. *"Does the as-built S360-410-R4 link up against both an
     802.3af PSE and an 802.3at PSE? If only 802.3af, does the
     PoE class declaration intent stay 802.3af-only (driving the
     E8 header cleanup answer)?"*
  2. *"What is the measured load regulation across the rated 5 V
     `+5VP` output range, the cold-start inrush, and the thermal
     rise of U1 / U2 / DCDC1 under sustained load?"*
  3. *"Are conducted / radiated EMI / EMC measurements available,
     and do they meet the relevant region's EN 55032 / 55035 /
     FCC Part 15 limits?"*
- **Stable expansion targets blocked.** Same five A-row
  candidates; required before E15 can land.

### E12 — Isolation / Hi-pot / earth-continuity / leakage evidence

- **Exact missing artefact.** A safety-evidence record that
  documents (a) Hi-pot test result through the `F0505S-2WR2`
  isolation barrier between `Sw_Vin_Poe` (pre-isolation) and
  `+5VP` / `GND` (post-isolation), (b) insulation resistance, (c)
  leakage current, and (d) earth continuity from `H1`–`H4` to the
  RJ45 shield / `Lan_earth` rail. The `F0505S-2WR2` datasheet
  isolation rating alone is **not** as-built evidence.
- **Operator / designer question.** *"Does the as-built
  S360-410-R4 isolation barrier meet (a) the manufacturer's
  rated isolation, (b) any region-specific Hi-pot / insulation /
  leakage / earth-continuity requirements applicable to a SELV
  PoE PSU intended for ceiling-mount install?"*
- **Stable expansion targets blocked.** Same five A-row
  candidates; required before E15 can land.

### E13 — PCB-level evidence

- **Exact missing artefact.** KiCad PCB source
  (`S360-410-R4.kicad_pcb`) and / or gerbers archive for
  `S360-410-R4`, ingested as retained-but-not-committed evidence
  under the [Hardware Artifact Policy](hardware/hardware-artifact-policy.md)
  once a storage backend is chosen per
  [§Future storage decision](hardware/hardware-artifact-policy.md#future-storage-decision).
- **Operator / designer question.** *"Are the isolation-barrier
  widths around `F0505S-2WR2` consistent with the relevant
  insulation creepage / clearance standards (e.g. IPC-2221 for
  SELV-to-SELV across an isolated DC/DC, allowing for the PoE
  primary side's 36–57 V DC SELV input), and are `H1`–`H4`
  electrically bonded to `Lan_earth` / RJ45 shield through the
  PCB stack?"*
- **Stable expansion targets blocked.** Same five A-row
  candidates; required before E15 can land.

### E14 — `F0505S-2WR2` vs `AM1D-0505S-NZ` primary-vs-alternate

- **Exact missing artefact.** Either (a) a `PACKAGE-POE-410-001`
  header-cleanup PR that records the populated-primary decision
  (`F0505S-2WR2` populated; `AM1D-0505S-NZ` purchasing-side
  alternate or future-revision option), or (b) a schematic-side
  correction PR that removes the `AM1D-0505S-NZ` annotation if it
  is stale.
- **Operator / designer question.** *"Is `AM1D-0505S-NZ` (a) a
  purchasing-side alternate that the supplier may populate when
  `F0505S-2WR2` is unavailable, (b) a future-revision option, or
  (c) a stale schematic annotation that should be removed?"*
- **Stable expansion targets blocked.** Indirect — closes either
  inside the E8 `PACKAGE-POE-410-001` implementation PR or
  separately.

### E15 — Release-One PoE caveat closure

- **Exact missing artefact.** A documentation-only PR that
  rewords the
  `"schematic verification pending"` caveat at
  [`docs/release-one-hardware-audit.md` Findings → PoE PSU](release-one-hardware-audit.md#findings)
  and the matching
  [Required follow-ups #6](release-one-hardware-audit.md#required-follow-ups)
  row once E2, E8, E9, E10, E11, and E12 close.
- **Operator / designer question.** None — mechanical once the
  upstream evidence rows close.
- **Stable expansion targets blocked.** Closure of E15 unblocks
  the G8 inherited-caveat axis for every Release-One-shape
  PoE-based stable target.

---

## Why this PR does not promote `S360-410` to `verified`

The closest precedent is `S360-100` / `S360-200` / `S360-210` /
`S360-211` / `S360-300`, each of which moved to `schematic_status:
verified` only after (a) the module-side schematic PDF was committed
under the relevant HW-ASSETS slice, (b) the per-board pin / package
mapping audit closed against the schematic + BOM, and (c) a separate
JSON-only PR set `schematic_file` and flipped `schematic_status`. For
`S360-410`:

- (a) is **done** — the module-side schematic PDF has been
  committed under HW-ASSETS-410 / PR #516.
- (b) is **partial** — HW-PINMAP-410-FOLLOWUP / PR #517 promoted
  the audit doc to `partial — schematic evidence available;
  package reconciliation, PoE PD controller / magnetics / buck /
  isolated DC/DC / harness identity evidence pending`. The
  `HW-BOM-ASSETS-002` BOM ingest closed the BOM-cross-check axis
  at the part-identity layer (see [E4](#per-evidence-class-audit)),
  but E8 / E9 / E10 / E11 / E12 / E13 / E14 are open.
- (c) is **owed** to a separate JSON-only PR after E8 / E9 / E10
  close.

`S360-410` carries a **fundamentally different evidence profile**
from the verified peers. It is the only off-board PSU module that
also crosses a galvanic-isolation boundary (`F0505S-2WR2(SIP-7)`),
so its evidence chain is augmented by isolation / Hi-pot / leakage /
earth-continuity / PoE link-up classes that none of the digital /
sensor / LED siblings carry. Those classes are bench evidence and
are not derivable from a schematic + BOM alone. **Promoting
`S360-410` to `verified` while E11 (PoE link-up + load + thermal +
EMI / EMC) and E12 (isolation / Hi-pot / leakage / earth continuity)
remain open would be a fabricated verification.**

This PR therefore does not promote, does not edit
[`config/hardware-catalog.json`](../config/hardware-catalog.json),
does not edit
[`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml),
and does not reword the Release-One PoE caveat. It records the
precise evidence-request list above so the next owning PR can
discharge each row without re-deriving the audit.

---

## Decision

Recorded decision for `PACKAGE-POE-410-001` in this PR:

> **Do not promote `S360-410` to `schematic_status: verified`,
> do not land the `PACKAGE-POE-410-001` package-header
> reconciliation, and do not reword the Release-One PoE
> `"schematic verification pending"` caveat in this PR.** Evidence
> classes E2 (partial), E8, E9, E10, E11, E12, E13, E14, and E15
> remain open. The audit produces the precise evidence-request
> list above and keeps `S360-410` `cataloged_unverified`.
> [`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml)
> stays byte-identical to PR #517 / PR #526. No `config/**` file
> is edited.

This is the option-4 outcome explicitly contemplated by the task
brief: *"If evidence is not sufficient: do not fabricate
verification, create a precise evidence-request record (exact
missing schematic / board files; exact review needed; exact
operator / designer question; what stable targets remain blocked),
keep S360-410 cataloged_unverified."*

---

## Stable-expansion targets that remain blocked behind this slice

The following stable-expansion targets continue to carry the
upstream PoE-PSU caveat until this slice's evidence-request list
closes. None is promoted, reclassified, or built by this PR.

| Stable expansion target | Source-of-truth row | Blocked behind |
|---|---|---|
| `Ceiling-POE` (A1) | [`docs/stable-target-expansion-plan.md` §A. Non-fan / non-LED / non-TRIAC room combos](stable-target-expansion-plan.md#a-non-fan--non-led--non-triac-room-combos) row A1 | E2 + E8 + E9 + E10 + E11 + E12 + E15 (the entire residual chain) |
| `Ceiling-POE-RoomIQ` (A2) | [`docs/stable-target-expansion-plan.md` §A](stable-target-expansion-plan.md#a-non-fan--non-led--non-triac-room-combos) row A2 | Same as A1 |
| `Ceiling-POE-VentIQ` (A5) | [`docs/stable-target-expansion-plan.md` §A](stable-target-expansion-plan.md#a-non-fan--non-led--non-triac-room-combos) row A5; [`docs/stable-target-ventiq-001-gate-closure.md`](stable-target-ventiq-001-gate-closure.md) §G8 detail | Same as A1; this is the rank-1 follow-up — STABLE-TARGET-VENTIQ-001 has already recorded its option-3 deferral per PR #632 |
| `Ceiling-POE-AirIQ` (A3) | [`docs/stable-target-expansion-plan.md` §A](stable-target-expansion-plan.md#a-non-fan--non-led--non-triac-room-combos) row A3 | Same as A1, plus the independent AirIQ stack hardware-evidence chain |
| `Ceiling-POE-AirIQ-RoomIQ` (A4) | [`docs/stable-target-expansion-plan.md` §A](stable-target-expansion-plan.md#a-non-fan--non-led--non-triac-room-combos) row A4 | Same as A3 |
| `Ceiling-POE-VentIQ-RoomIQ` (Release-One; **already shipping**) | [`config/webflash-builds.json`](../config/webflash-builds.json); [`docs/release-one-hardware-audit.md` Findings → PoE PSU](release-one-hardware-audit.md#findings) | Ships **under the preserved `"schematic verification pending"` caveat**. The Release-One product / artifact / tag are not requalified by this PR. |
| `Ceiling-POE-VentIQ-RoomIQ-LED` (LED preview; **already shipping**) | [`config/webflash-builds.json`](../config/webflash-builds.json) | Same as Release-One — ships under the preserved caveat. The LED preview stays `preview-release`; LED stable promotion is gated by `LED-STABLE-PROMOTION-001` and the [preview-to-stable gauntlet](preview-to-stable-promotion-gates.md), **not** by this slice. |

The shared `PRODUCT-POE-410-001` / `S360-410` schematic-verification
chain is amortised across the five A-row candidates per the
[`docs/stable-target-expansion-plan.md` §A](stable-target-expansion-plan.md#a-non-fan--non-led--non-triac-room-combos)
"promotion order is therefore deliberately sequential" note.

---

## Resume conditions

`PACKAGE-POE-410-001` can resume actual package / catalog edit
work only when **all** of the following are independently recorded
by their own committed slice — none can be assumed, fabricated, or
rolled into the same PR:

1. **E9 closes** — silkscreen photographs or KiCad PCB source for
   `S360-410-R4` ingested as retained-but-not-committed evidence
   under the [Hardware Artifact Policy](hardware/hardware-artifact-policy.md).
2. **E10 closes** — HW-002 Open Question #6 / `S360-100-BENCH-001`
   J2 PoE harness identity recorded on
   [`docs/hardware/s360-100-r4-core.md` §S360-100-BENCH-001 status](hardware/s360-100-r4-core.md#s360-100-bench-001-status).
3. **E11 closes** — bench / load / PoE link-up / thermal /
   EMI / EMC evidence filed (may be filed as
   `S360-410-BENCH-001` on
   [`docs/hardware/s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md)).
4. **E12 closes** — isolation / Hi-pot / insulation resistance /
   earth-continuity / leakage evidence filed.
5. **E2 closes** — a separate JSON-only PR against
   [`config/hardware-catalog.json`](../config/hardware-catalog.json)
   flips `S360-410` `schematic_status: cataloged_unverified` →
   `verified` and sets `schematic_file: docs/hardware/schematics/S360-410-R4.pdf`,
   passing
   [`tests/test_hardware_catalog.py`](../tests/test_hardware_catalog.py).
6. **E14 closes** — `F0505S-2WR2` vs `AM1D-0505S-NZ` populated-
   primary decision recorded (in the `PACKAGE-POE-410-001`
   implementation PR header cleanup, or in a separate
   schematic-side correction PR).
7. **Design-intent answers recorded** — the four E8 operator /
   designer questions (802.3af-only vs 802.3af/at-capable; 5 V
   only vs 5 V or 3.3 V output; protection claim; alternate-DC/DC
   header treatment) are recorded before the `PACKAGE-POE-410-001`
   implementation PR opens.

When the seven conditions hold, the implementation PR will:

- edit
  [`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml)
  header lines 6–11 to reflect the BOM-confirmed discrete topology
  and the design-intent decisions, citing the BOM ingest at
  [`docs/hardware/artifacts/S360-410-R4.md` §HW-BOM-ASSETS-002 BOM ingest (2026-05-20)](hardware/artifacts/S360-410-R4.md#hw-bom-assets-002-bom-ingest-2026-05-20)
  inline;
- update
  [`docs/hardware/package-readiness-matrix.md` `power_poe.yaml` / S360-410](hardware/package-readiness-matrix.md#power_poeyaml--s360-410)
  to reclassify the package row from `schematic-evidence-pending`
  to `ready-for-package-change` (or its successor enum);
- update
  [`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
  for the now-reconciled discrete topology;
- record the audit-log row on
  [`docs/hardware/s360-410-r4-poe.md` §HW-PINMAP-410-FOLLOWUP audit log](hardware/s360-410-r4-poe.md#hw-pinmap-410-followup-audit-log);
- coordinate (via a same-PR companion or an immediate-follow-up PR)
  the Release-One PoE caveat closure at E15;
- run the full validation suite (`python3 tests/validate_configs.py`,
  `python3 tests/test_hardware_catalog.py`,
  `python3 tests/test_product_catalog.py`,
  `python3 tests/test_all_yaml_release_matrix.py`,
  `python3 tests/validate_webflash_builds.py`,
  `python3 scripts/list_release_targets.py`,
  `python3 scripts/classify_all_yaml_release_matrix.py --summary`,
  `python3 -m unittest discover -s tests -p "test_*.py"`).

That implementation PR is **not** approved or scoped by this
evidence-audit PR.

---

## What stays exactly the same

The release surface is unchanged:

| Artifact | State after this PR |
|---|---|
| [`config/hardware-catalog.json`](../config/hardware-catalog.json) | `S360-410` row at lines 112–121 stays byte-identical (`schematic_status: cataloged_unverified`, no `schematic_file`); every other row stays byte-identical. |
| [`config/webflash-builds.json`](../config/webflash-builds.json) | Exactly 2 rows (`Ceiling-POE-VentIQ-RoomIQ` stable, `Ceiling-POE-VentIQ-RoomIQ-LED` preview) — unchanged. |
| [`config/product-catalog.json`](../config/product-catalog.json) | No new row; no status flip — unchanged. |
| [`config/compile-only-targets.json`](../config/compile-only-targets.json) | Exactly 12 targets — unchanged. |
| [`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json) | Unchanged. |
| [`config/compile-only-candidates.json`](../config/compile-only-candidates.json) | Unchanged. |
| [`config/webflash-compatibility.json`](../config/webflash-compatibility.json) | Unchanged. |
| [`config/room-bundle-skus.json`](../config/room-bundle-skus.json) | Unchanged. |
| [`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml) | Byte-identical to PR #517 / PR #526 (header lines 6–11 preserved). |
| [`docs/hardware/schematics/S360-410-R4.pdf`](hardware/schematics/S360-410-R4.pdf) | Byte-identical to HW-ASSETS-410 / PR #516. |
| `products/sense360-ceiling-poe-ventiq-roomiq.yaml` (Release-One) | Byte-identical; `Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable` ships under the preserved caveat. |
| `products/sense360-ceiling-poe-ventiq-roomiq-led.yaml` (LED preview) | Byte-identical; `Ceiling-POE-VentIQ-RoomIQ-LED` / `v1.0.0` / `preview` stays preview. |
| `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml` (FanTRIAC blocked) | Byte-identical; stays `blocked` / `HW-005`. |
| LED preview / FanRelay / FanPWM / FanDAC / FanTRIAC | All unchanged. |
| Release-One PoE caveat at [`docs/release-one-hardware-audit.md` Findings → PoE PSU](release-one-hardware-audit.md#findings) | Preserved verbatim. |
| HW-002 Open Question #6 / `S360-100-BENCH-001` | Preserved; both still `pending — bench/manufacturing evidence required`. |
| Classifier counts (`scripts/classify_all_yaml_release_matrix.py --summary`) | `stable=1, preview=1, manual=3, compile-only=7, blocked=1, not-a-product-entrypoint=35` — verbatim. |
| Release-selectable set | `{Ceiling-POE-VentIQ-RoomIQ, Ceiling-POE-VentIQ-RoomIQ-LED}` — verbatim. |

---

## Validation

This document is reproduced and locked in by the same source-of-
truth checks the per-board, per-package, per-product, and
per-release matrices use. None of the checks below requires a
firmware build, a GitHub Release, or any `.bin` artefact.

| Command | Expected result |
|---|---|
| `python3 tests/validate_configs.py` | All YAMLs validate |
| `python3 tests/test_hardware_catalog.py` | All passed; `S360-410` stays `cataloged_unverified` and carries no `schematic_file`; new pin in `EXPECTED_STILL_UNVERIFIED_SKUS` |
| `python3 tests/test_product_catalog.py` | All passed |
| `python3 scripts/classify_all_yaml_release_matrix.py --summary` | `stable=1, preview=1, manual=3, compile-only=7, blocked=1, not-a-product-entrypoint=35` |
| `python3 scripts/list_release_targets.py` | Two rows (`Ceiling-POE-VentIQ-RoomIQ` stable, `Ceiling-POE-VentIQ-RoomIQ-LED` preview) |
| `python3 tests/test_all_yaml_release_matrix.py` | All passed |
| `python3 tests/validate_webflash_builds.py` | 2 builds validated |
| `python3 -m unittest discover -s tests -p "test_*.py"` | Full suite passes; count unchanged from the STABLE-TARGET-VENTIQ-001 / PR #632 baseline of 978 tests, 3 skipped, plus the new `S360-410` `cataloged_unverified` pin in `tests/test_hardware_catalog.py` |

---

## Cross-references

- HW-PINMAP-410 audit doc + audit log: [`docs/hardware/s360-410-r4-poe.md`](hardware/s360-410-r4-poe.md)
- HW-ASSETS-410 / HW-BOM-ASSETS-002 artefact index: [`docs/hardware/artifacts/S360-410-R4.md`](hardware/artifacts/S360-410-R4.md)
- Schematic PDF: [`docs/hardware/schematics/S360-410-R4.pdf`](hardware/schematics/S360-410-R4.pdf)
- Per-board readiness: [`docs/hardware/board-readiness-matrix.md` §S360-410](hardware/board-readiness-matrix.md#s360-410-sense360-poe-psu)
- Per-package readiness: [`docs/hardware/package-readiness-matrix.md` §power_poe.yaml / S360-410](hardware/package-readiness-matrix.md#power_poeyaml--s360-410)
- Firmware-package mapping audit: [`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md)
- Logical PoE package: [`packages/hardware/power_poe.yaml`](../packages/hardware/power_poe.yaml)
- Core reference (Core `J2` `PoE_ACDC` capture; HW-002 OQ#6; S360-100-BENCH-001): [`docs/hardware/s360-100-r4-core.md`](hardware/s360-100-r4-core.md)
- Release-One audit (preserved PoE caveat): [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md)
- Product readiness: [`docs/product-readiness-matrix.md` §PoE-410 / S360-410](product-readiness-matrix.md#poe-410--s360-410)
- WebFlash exposure readiness: [`docs/webflash-exposure-readiness-matrix.md` §PoE / S360-410 WebFlash posture](webflash-exposure-readiness-matrix.md#poe--s360-410-webflash-posture)
- Release-artifact readiness: [`docs/release-artifact-readiness-matrix.md` §PoE / S360-410 release posture](release-artifact-readiness-matrix.md#poe--s360-410-release-posture)
- All-YAML release matrix: [`docs/all-yaml-release-matrix.md`](all-yaml-release-matrix.md)
- Room-firmware release matrix: [`docs/room-firmware-release-matrix.md`](room-firmware-release-matrix.md)
- Stable target expansion plan: [`docs/stable-target-expansion-plan.md`](stable-target-expansion-plan.md)
- STABLE-TARGET-VENTIQ-001 gate-closure record: [`docs/stable-target-ventiq-001-gate-closure.md`](stable-target-ventiq-001-gate-closure.md)
- Sense360 room bundles: [`docs/sense360-room-bundles.md`](sense360-room-bundles.md)
- Hardware artifact policy: [`docs/hardware/hardware-artifact-policy.md`](hardware/hardware-artifact-policy.md)
- Compliance tracker (mains only; PoE is SELV / out of scope): [`docs/compliance/mains-voltage-uk-eu-assessment.md`](compliance/mains-voltage-uk-eu-assessment.md)

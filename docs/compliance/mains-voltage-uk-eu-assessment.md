# Mains-voltage Safety and Compliance Assessment — UK / EU (COMPLIANCE-001)

> **STATUS (2026-06-09): CLOSED — resolved by posture.**
> `COMPLIANCE-001` was closed by the owner decision record
> [`../decisions/COMPLIANCE-001-RESOLUTION-001.md`](../decisions/COMPLIANCE-001-RESOLUTION-001.md):
> the mains-touching boards (`S360-320` TRIAC, `S360-310` Fan Relay,
> `S360-400` 240v PSU) are **never placed on the market by Sense360** — not
> sold assembled, not as a kit of parts, not as a populated PCB, not
> physically bundled in any kit, order, or promotion. Design files and
> firmware publish open-source under CERN-OHL-P for self-builders of their
> own devices, at their own risk, via the experimental lane defined in
> [`../../config/release-channel-policy.json`](../../config/release-channel-policy.json)
> (`experimental_lane`).
>
> **REOPEN TRIGGER:** any future act of placing any mains-touching board on
> the market **reopens `COMPLIANCE-001`** and requires an external safety and
> EMC assessment **before** that act (indicative path: pre-compliance scan,
> then test-house safety + EMC — see the resolution record for the indicative
> scope and cost). This document is retained **in full, unchanged below the
> closure entries**, as the technical checklist for that reopen path. The
> closure promotes **no** checklist row: every `Not proven by this
> repository` / `To be confirmed` / `Requires qualified review` value below
> stands, and no safety, EMC, CE / UKCA, LVD, RED, or RoHS conformity is
> claimed for any Sense360 board or product.

## Purpose

This document is a **compliance assessment tracker** for Sense360 boards and
modules that operate on UK / EU mains AC voltage (nominally 230 V AC, with
the colloquial UK descriptor "240 V" used in the repo elsewhere). It exists
so that downstream work — preview gates, stable / shipping gates, and any
future technical-file build-up — has a single, evidence-citable answer to
"what must be proven before a mains-voltage Sense360 board can be marked
preview-ready, stable, CE-marked, UKCA-marked, or shippable?".

This document is the companion to the safety/compliance note already
recorded in
[`../hardware/remaining-board-documentation-audit.md`](../hardware/remaining-board-documentation-audit.md#mains-voltage-safety-and-compliance-note).
That note flagged that an electrical safety / compliance review is required
before either mains module can be promoted to preview or stable; this
document expands that note into a structured checklist.

> **This is a tracker. It is not a compliance declaration.**
>
> Nothing in this document asserts that any Sense360 board or product is
> CE-marked, UKCA-marked, LVD-compliant, EMC-compliant, RED-compliant,
> RoHS-compliant, safe for mains, or approved for mains. Every regulatory
> statement is framed as `Likely applicable`, `To be confirmed`,
> `Requires qualified review`, or `Not proven by this repository`.

## Scope

In scope:

- The two Sense360 boards/modules in
  [`../../config/hardware-catalog.json`](../../config/hardware-catalog.json)
  that operate on mains AC: **`S360-400` Sense360 240v PSU** (mains-input)
  and **`S360-320` Sense360 TRIAC** (mains-output phase-cut dimmer).
- The questions, classification axes, and evidence checklists that must be
  resolved before either of those modules can be marked preview-ready or
  stable-ready in any future config string.

Out of scope:

- Schematic / layout review (no `S360-400` or `S360-320` schematic is
  committed to this repository — see
  [`../hardware/remaining-board-documentation-audit.md`](../hardware/remaining-board-documentation-audit.md#decision-table)).
- Any electrical-safety, EMC, or compliance **conclusion**. Those require
  a qualified review (schematic + layout + sample + test-lab) which this
  repository cannot perform on its own.
- Any change to firmware, product YAML, package YAML, workflow, script,
  test, build matrix, hardware SKU, catalog status, lifecycle status, or
  artifact name.
- Production Release-One (`Ceiling-POE-VentIQ-RoomIQ`), which uses the
  `S360-410` PoE PSU and is therefore separate from this assessment.

## Non-goals

- **No compliance claim.** This document does not declare CE, UKCA, LVD,
  EMC, RED, or RoHS compliance for any Sense360 board, module, or product.
- **No promotion.** No board is promoted from `cataloged-unverified` /
  `blocked` to `preview` / `stable` / `production` by this document.
- **No firmware, hardware, or workflow change.** No `.yaml`, `.json`,
  `.py`, workflow, component, or include file is modified.
- **No FanTRIAC unblock.** `S360-320` Sense360 TRIAC stays blocked under
  HW-005. See
  [`../release-one-hardware-audit.md#fantriac-mapping-resolution`](../release-one-hardware-audit.md#fantriac-mapping-resolution).
- **No change to LED Release-One status.** Sense360 LED stays excluded
  from production Release-One because the WebFlash config string
  `Ceiling-POE-VentIQ-RoomIQ` does not contain a `LED` token.

## Affected boards / modules

Two rows of [`../../config/hardware-catalog.json`](../../config/hardware-catalog.json)
operate on mains AC voltage:

- **`S360-400` Sense360 240v PSU** — `Mains to 5V using HLK-5M05`
  (catalog description). This is the **mains-input** module. It is not
  used by production Release-One; Release-One ships with `S360-410`
  Sense360 PoE PSU instead.
- **`S360-320` Sense360 TRIAC** — `Phase dimmer for mains fan or lamp`
  (catalog description). This is the **mains-output** module. It is
  additionally HW-005 blocked
  ([`../release-one-hardware-audit.md#fantriac-mapping-resolution`](../release-one-hardware-audit.md#fantriac-mapping-resolution)).

Every other row in the hardware catalog is either low-voltage,
PoE-powered, USB-powered, or signal-only and therefore not in scope for
this assessment. The full per-row evidence inventory lives in
[`../hardware/remaining-board-documentation-audit.md`](../hardware/remaining-board-documentation-audit.md#decision-table).

### Release-One separation

Production Release-One ships the WebFlash config string
`Ceiling-POE-VentIQ-RoomIQ` and the artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`. The four modules in
that config (`S360-100` Core, `S360-410` PoE PSU, `S360-211` VentIQ,
`S360-200` RoomIQ) are **all low-voltage**. The PoE path uses an IEEE
802.3af PD architecture; mains voltage never enters the Sense360 product
enclosure on the Release-One path.

**The Release-One PoE path does not exercise, validate, or provide any
evidence for `S360-400` or `S360-320`.** Any future product variant that
introduces a mains-input slot (`PWR`) or a mains-output slot
(`FanTRIAC`) is a separate product and requires this assessment to be
completed before preview or stable.

## Board table

| Board / module | SKU | Mains role | Current repo evidence | Compliance status | Required next evidence |
|---|---|---|---|---|---|
| Sense360 240v PSU | `S360-400` | **Mains-input** PSU (HLK-5M05 based; mains → 5 V isolated DC) | `cataloged-unverified` in [`../../config/hardware-catalog.json`](../../config/hardware-catalog.json); only a logical firmware package at [`../../packages/hardware/power_240v.yaml`](../../packages/hardware/power_240v.yaml) (no GPIO binding); **no `S360-400` schematic committed**; HLK-5M05 module datasheet is third-party and not committed to this repo | **Not proven by this repository.** No safety, EMC, or compliance evidence exists in-repo. `Requires qualified review` before any promotion. | Commit `S360-400` schematic + BOM + layout / clearance evidence + finished-product context (intended enclosure, intended installation, intended UK/EU market) and obtain a qualified electrical-safety review. See the checklists below. |
| Sense360 TRIAC | `S360-320` | **Mains-output** phase-cut dimmer (intended for mains-driven fans or lamps) | `cataloged-unverified` in JSON; **HW-005 blocked** ([`../release-one-hardware-audit.md#fantriac-mapping-resolution`](../release-one-hardware-audit.md#fantriac-mapping-resolution)); driver package [`../../packages/expansions/fan_triac.yaml`](../../packages/expansions/fan_triac.yaml) carries a `BLOCKED / UNVERIFIED — must not ship as FanTRIAC-capable` banner; Core-side connector `J15` (`+3.3V`, `TRI_GPIO1`, `TRI_GPIO2`, `GND`) is the only documented interface, captured in [`../hardware/s360-100-r4-core.md`](../hardware/s360-100-r4-core.md#j15--triac-fan-module-connector-4-pin); **no `S360-320` schematic committed**. | **Not proven by this repository; additionally HW-005 blocked.** No safety, EMC, or compliance evidence exists in-repo. `Requires qualified review` before any promotion, and HW-005 must be resolved separately. | Resolve HW-005 (commit `S360-320` schematic and prove a working direct-ESP32 or on-board-controller drive path); commit BOM + layout / isolation evidence; obtain a qualified electrical-safety review covering phase-cut dimming of the intended load type. See the checklists below. |

### Release-One footnote

| Module | SKU | Voltage class | Used by Release-One? | Mains-evidence relevance |
|---|---|---|---|---|
| Sense360 PoE PSU | `S360-410` | Low-voltage (PoE PD output) | Yes — `Ceiling-POE-VentIQ-RoomIQ` | **None.** PoE is not mains AC; the Release-One product enclosure does not contain a mains rail. The PoE path is not evidence for either mains module. |

## Product classification — questions

Before any of the questions in the following sections can be answered,
the **product classification** under UK / EU regulation must be
established. None of these answers can be derived from the current
repository alone; each is `To be confirmed` by the product owner and
`Requires qualified review` if the answer affects safety scope.

- Is the offering a **finished product** (a fully enclosed CE/UKCA-marked
  appliance shipped to an end user), a **subassembly** sold to a
  professional integrator, a **module** sold to an OEM, or a
  **fixed-installation accessory** (intended for permanent installation
  by a competent person)?
- Is the offering placed on the market in **Great Britain (UKCA scope)**,
  in the **EU (CE scope)**, in both, or in another regime entirely?
- Who is the **manufacturer** for the purposes of the relevant
  regulation, and who holds the technical file and Declaration of
  Conformity?
- Is the device intended for **household / general-public** use, or for
  **professional / restricted** use? This affects which harmonised
  standards are likely applicable.
- Is the device intended to be **plugged into a standard mains outlet**,
  to be **wired in by a qualified electrician**, or to be **embedded
  inside a larger appliance**?
- Does the offering bundle the mains module (`S360-400`) inside an
  enclosure that also contains low-voltage electronics, or is the mains
  module sold separately?
- Does the offering drive an **external mains load** (the `S360-320`
  case)? If so, what load types are supported (resistive, inductive,
  motor, electronic ballast, LED dimmer-compatible, etc.)?

None of the above is answered here. They are listed so that a qualified
review starts from a complete classification.

## Protection class — decision tree

The intended protection class drives almost every subsequent question.
This decision tree is a checklist, not a conclusion. Every leaf is
`To be confirmed` and `Requires qualified review`.

1. Is the design intended to be **Class I** (basic insulation plus a
   protective-earth conductor that bonds exposed conductive parts)?
   - If yes: what specifically is bonded to protective earth, and how is
     PE continuity verified? `Requires qualified review`.
   - If yes: what is the prospective fault path on a basic-insulation
     failure, and is the upstream protective device (fuse / MCB / RCD)
     guaranteed to operate within the standard's disconnection time?
     `Requires qualified review`.
2. Is the design intended to be **Class II** (reinforced or double
   insulation between mains and accessible parts; no PE conductor)?
   - If yes: where exactly is the reinforced / double insulation
     boundary, and what evidence demonstrates the required insulation
     coordination (creepage, clearance, distance through insulation,
     CTI)? `Requires qualified review`.
   - If yes: is every accessible conductive part either non-conductive
     or behind reinforced insulation from mains? `Requires qualified
     review`.
3. Is the **low-voltage section** intended to be **SELV** (Safety Extra
   Low Voltage — galvanically isolated from mains, no earth reference
   required) or **PELV** (earth-referenced)?
   - If yes: what isolation barrier separates mains from the SELV / PELV
     section, and what is the rated working voltage, transient voltage,
     and pollution degree of that barrier? `Requires qualified review`.
   - If yes: do all accessible signal interfaces (USB, Ethernet,
     I²C/UART connectors to Sense360 modules) remain inside the
     SELV / PELV envelope? `Requires qualified review`.
4. Is the design intended to be something else (functional insulation
   only, hazardous-touch-allowed, etc.)? If so, that classification must
   itself be justified against the applicable standard and is
   `Requires qualified review`.

`S360-400` Sense360 240v PSU and `S360-320` Sense360 TRIAC may have
**different** protection classes from each other, and the Sense360 Core
that hosts them is a SELV-side board. The boundary location and the
class of each side of that boundary is a per-product decision that is
not made in this repository.

## Standards and regulations — applicability checklist

Each row is a question about applicability under UK / EU regulation.
None of these rows asserts compliance. Every entry's status column is
one of:

- `Likely applicable` — historical practice / scope suggests this
  applies and should be confirmed first.
- `To be confirmed` — applicability is plausible but depends on the
  product classification above.
- `Requires qualified review` — only a qualified party can answer.
- `Not proven by this repository` — no evidence in this repo addresses
  this row.

| Regime / regulation | Scope question | Status |
|---|---|---|
| UK Electrical Equipment Safety Regulations 2016 (EESR) | Does the finished product fall within "electrical equipment designed for use with a voltage rating of between 50 and 1000 V for alternating current" placed on the GB market? | `Likely applicable` for any finished product containing `S360-400`. `Likely applicable` for any finished product driving mains loads via `S360-320`. `Requires qualified review`. |
| EU Low Voltage Directive 2014/35/EU (LVD) | Does the finished product fall within the LVD voltage range placed on the EU market? | `Likely applicable` for the equivalent EU placements of either mains module. `Requires qualified review`. |
| UK Electromagnetic Compatibility Regulations 2016 | Does the finished product fall within UK EMC scope on the GB market? | `Likely applicable`. `Requires qualified review`. |
| EU EMC Directive 2014/30/EU | Does the finished product fall within EU EMC scope on the EU market? | `Likely applicable`. `Requires qualified review`. |
| UK Radio Equipment Regulations 2017 / EU Radio Equipment Directive (RED) 2014/53/EU | Does the finished product contain a radio transmitter (e.g. Wi-Fi or Bluetooth on the Sense360 Core ESP32-S3)? If yes, RED / UK RER applies and supersedes LVD/EMC for the radio module. | `Likely applicable` because the Sense360 Core ESP32-S3 carries Wi-Fi / Bluetooth radios. `Requires qualified review` for the finished-product placement. |
| UK RoHS Regulations 2012 (as amended) | Does the finished product fall within RoHS scope on the GB market? | `Likely applicable`. `Requires qualified review`. |
| EU RoHS Directive 2011/65/EU (as amended) | Does the finished product fall within RoHS scope on the EU market? | `Likely applicable`. `Requires qualified review`. |
| CE marking | What harmonised standards underpin the CE Declaration of Conformity for the finished product? | `To be confirmed`. The standards set depends on product classification and on the regime rows above. `Requires qualified review`. |
| UKCA marking | What designated standards underpin the UKCA Declaration of Conformity for the finished product? | `To be confirmed`. `Requires qualified review`. |
| WEEE / packaging / other product-stewardship regimes | Do WEEE, packaging waste, or other product-stewardship regimes apply? | `To be confirmed`. Out of the safety/compliance scope of this tracker but flagged so a qualified review does not miss them. |

The exact harmonised / designated standards lists (e.g. for LVD: the
EN 60335 family for household appliances, EN 61010 for measurement /
control / laboratory equipment, EN 62368-1 for ICT / audio-video; for
EMC: the EN 55014 / EN 55032 / EN 61000 families; for RED: the EN
300 328 / EN 301 489 / EN 62311 / EN 62479 families) are **not
enumerated as applicable here**. Picking the correct standard for the
product is itself a qualified-review decision and depends on the
product classification above. `Not proven by this repository`.

## Electrical-safety topics — checklist

Each topic is a question that a qualified review must answer for both
`S360-400` and `S360-320` before either can be marked preview-ready or
stable-ready. All rows are `Not proven by this repository`.

### Isolation and barriers

- Where is the **mains-to-low-voltage isolation barrier** physically
  located on `S360-400`? What is its rated working voltage, transient
  voltage, pollution degree, and insulation type (functional / basic /
  reinforced / double)? `Requires qualified review`.
- Where is the **mains-to-control isolation barrier** on `S360-320`
  (TRIAC gate drive and zero-cross detection paths)? Is the
  zero-cross / gate drive optocoupled, transformer-isolated, or some
  other isolation method? `Requires qualified review`.
- Does any Sense360 inter-module connector (`J*` on the Core) cross
  the isolation barrier? If so, what is the barrier rating at that
  connector? `Requires qualified review`.

### Creepage, clearance, distance through insulation

- What pollution degree and material group are assumed for the PCB and
  for the enclosure? `Requires qualified review`.
- Do the PCB creepage and clearance values at every mains-to-low-voltage
  boundary meet the applicable standard for the chosen working voltage
  and pollution degree? `Requires qualified review`.
- Are there any reduced-clearance features (slots, V-cuts, milled
  separations) and is each one justified? `Requires qualified review`.

### Over-current, surge, and thermal protection

- What **mains fuse** (or PTC, MCB, or other over-current protective
  device) is fitted upstream of `S360-400`? What is its rating, breaking
  capacity, and standards conformity? `Requires qualified review`.
- What **MOV / TVS / surge-suppression** is fitted? What is its energy
  rating relative to the expected installation surge category?
  `Requires qualified review`.
- What **thermal protection** (thermal fuse, NTC, PTC, thermal cut-out)
  protects against fault-condition heating? `Requires qualified review`.
- For `S360-320`: what protects against **load short-circuit**, **load
  inrush**, and **load disconnection during phase-cut conduction**?
  `Requires qualified review`.
- What **PCB flame rating** (UL94 class) does the bare PCB carry, and
  what flame rating do the safety-critical plastic parts carry?
  `Requires qualified review`.

### Terminals, strain relief, accessibility

- What **terminal block** is used at the mains input of `S360-400` (and
  at the mains output of `S360-320`)? What is its voltage rating,
  current rating, wire range, torque spec, and certification (UL / VDE
  / TUV / IEC)? `Requires qualified review`.
- What **strain relief** is provided for incoming and outgoing mains
  cables? `Requires qualified review`.
- Is there any **accessible conductive part** that could become live
  under a single-fault condition? `Requires qualified review`.

### Enclosure

- What **enclosure** contains the mains module in the finished product?
  What are its IP rating, IK rating, flame rating, and temperature
  rating? `Requires qualified review`.
- What is the **installation method** — plug-in, screw-terminal, DIN
  rail, ceiling-mount, in-wall — and what standard governs that
  installation? `Requires qualified review`.

### TRIAC-specific topics (`S360-320` only)

- What **load types** are supported (resistive, inductive, motor,
  electronic ballast, LED-driver-compatible)? `Requires qualified
  review`.
- What is the **snubber** (RC across the TRIAC) sized for, and is it
  rated for the worst-case dV/dt of the expected loads?
  `Requires qualified review`.
- What is the **TRIAC dV/dt and dI/dt rating**, and does it cover the
  worst-case switching scenario including transient line conditions?
  `Requires qualified review`.
- How is **zero-cross detection** isolated from the low-voltage side,
  and what timing accuracy does it provide? `Requires qualified
  review`.
- HW-005 must be resolved before this section is meaningful — see
  [`../release-one-hardware-audit.md#fantriac-mapping-resolution`](../release-one-hardware-audit.md#fantriac-mapping-resolution).

## EMC topics — checklist

All rows `Not proven by this repository` and `Requires qualified
review`.

- **Conducted emissions** on the mains port (`S360-400`) and on the
  load port (`S360-320`): which standard's limits apply, and does the
  design include the necessary common-mode and differential-mode mains
  filtering?
- **Radiated emissions** of the finished product across the relevant
  frequency range.
- **Immunity** — ESD, EFT/burst, surge, conducted RF immunity, power-
  frequency magnetic field immunity, voltage dips and short
  interruptions on the mains port — to the applicable EN 61000-4-x
  series.
- **Harmonics and flicker** (EN 61000-3-2 / EN 61000-3-3 or successors)
  on the mains port, if the finished product's input current exceeds
  the standard's scope thresholds.
- **Radio coexistence** when a Wi-Fi / Bluetooth ESP32-S3 is in the
  finished product (RED Article 3.2 / 3.3 considerations).

## Evidence required before any "preview" promotion

A mains-voltage Sense360 board may only be promoted from
`cataloged-unverified` / `blocked` to a preview status when, at minimum,
the following evidence is committed to this repository and reviewed by
a qualified party. Documentation alone is not sufficient.

- **Schematic** for the specific SKU (`S360-400-R?.pdf` or
  `S360-320-R?.pdf`), and a corresponding standalone pin / connector /
  isolation reference doc under `docs/hardware/` (mirroring the
  structure of [`../hardware/s360-100-r4-core.md`](../hardware/s360-100-r4-core.md)
  and [`../hardware/s360-200-r4-roomiq.md`](../hardware/s360-200-r4-roomiq.md)).
- **BOM** with every safety-critical part called out (mains fuse, MOV,
  isolation transformer / optocoupler, X / Y capacitors, terminal
  blocks, PCB material, isolating slot machining if any).
- **Layout / clearance evidence** demonstrating mains-to-low-voltage
  creepage and clearance at every boundary, including PCB net colouring
  or annotated layout, against the assumed pollution degree.
- **Product classification statement** answering the questions in the
  "Product classification — questions" section above.
- **Protection-class decision** (Class I / Class II / SELV / PELV /
  other), with the boundary identified.
- **Qualified review** of all of the above by a competent electrical-
  safety engineer (internal or external). The review's scope and
  findings should be recorded; the review need not be a full type test
  to permit a preview-channel build.
- For `S360-320`: **HW-005 resolution** (see
  [`../release-one-hardware-audit.md#fantriac-mapping-resolution`](../release-one-hardware-audit.md#fantriac-mapping-resolution)).

Preview is **not** shippable. Preview firmware on a mains-voltage SKU
remains explicitly for evaluation by qualified parties only, with a
documented intended-use limitation, until the stable / shipping
evidence below is satisfied.

## Evidence required before any "stable" / shipping promotion

Beyond the preview evidence:

- **Accredited test-lab report(s)** covering the applicable LVD / EESR
  safety standard(s), the applicable EMC standard(s), and (if a radio
  is present in the finished product) the applicable RED / UK RER
  standards, for the **finished product** as placed on the market.
  `Requires qualified review` and `Not proven by this repository`.
- **Technical file** (see below).
- **Declaration of Conformity** (see below).
- **Marking artwork** — CE and/or UKCA mark, manufacturer details,
  ratings plate, conformity-marking placement compliant with the
  applicable regulation. `Requires qualified review`.
- **Production-control plan** demonstrating that every shipped unit is
  built to the same configuration as the type-tested unit, with
  appropriate end-of-line safety tests (hipot / leakage / PE continuity
  for Class I, etc.). `Requires qualified review`.

A stable / shipping promotion of any product containing a mains-voltage
Sense360 board without each of the above being satisfied is out of
scope for this repository.

## Technical-file checklist

The technical file for a finished product containing `S360-400` and/or
`S360-320` is `Required` under UK EESR / EU LVD (and the corresponding
EMC / RED regulations, if applicable). The repository does **not**
host the technical file itself; this checklist records what a qualified
party must assemble outside this repository.

| Item | Status |
|---|---|
| General description of the product and intended use | `Required`; `Not in this repository` |
| Schematic, layout, BOM | `Required`; **partially present** for Core / RoomIQ only, **`Not in this repository`** for `S360-400` and `S360-320` |
| List of harmonised / designated standards applied (or other technical solution adopted) | `Required`; `To be confirmed`; `Requires qualified review` |
| Risk assessment | `Required`; `Requires qualified review`; `Not in this repository` |
| Test reports (LVD / EMC / RED, as applicable) | `Required` before stable / shipping; `Not in this repository` |
| Calculations and analyses (isolation coordination, thermal, fault) | `Required`; `Requires qualified review`; `Not in this repository` |
| Production-quality plan / type-test correspondence | `Required`; `Requires qualified review`; `Not in this repository` |
| Instructions and safety information for the user | `Required`; `To be confirmed`; `Not in this repository` |
| Marking, label artwork, packaging notices | `Required`; `Requires qualified review`; `Not in this repository` |
| EU / UK Declaration of Conformity (signed) | `Required`; `Not in this repository`. See the dedicated section below. |
| Authorised Representative appointment (if manufacturer is outside GB / EU as required) | `To be confirmed`; `Not in this repository` |
| Record retention plan for the regulation's required period | `Required`; `Not in this repository` |

## Declaration of Conformity — checklist

A Declaration of Conformity (DoC) is `Required` before any product
containing `S360-400` or `S360-320` can be CE-marked or UKCA-marked.
The DoC itself is **not** part of this repository.

- Identity of the manufacturer (and Authorised Representative, if any).
- Product identification (model / SKU / batch / serial range covered).
- Statement that the DoC is issued under the sole responsibility of the
  manufacturer.
- List of relevant Union / UK legislation and the **harmonised /
  designated standards** applied (specific versions and dated
  references).
- Reference to any notified / approved body involved (if applicable).
- Signed and dated by an authorised representative of the manufacturer.

Every bullet is `Required`, `Requires qualified review`, and `Not
proven by this repository`.

## Open questions for compliance engineer / test lab

These questions cannot be answered by this repository alone. They are
listed so that an external review begins from a complete set of
unknowns.

1. Will `S360-400` be sold as a **bare module** to integrators, as part
   of a **finished Sense360 product**, or both? The technical-file
   owner and the marking obligations differ by case.
2. Will `S360-320` be sold separately from `S360-400`? If so, what is
   the assumed upstream protection and the assumed mains supply
   characteristic?
3. What **load types** must `S360-320` support? (Resistive, inductive,
   universal-motor, capacitive-input-supply, LED-driver dimming, etc.)
4. What is the **intended installation method** for any finished
   product carrying these modules? (Plug-in appliance, hard-wired by a
   competent person, fixed-installation accessory, etc.)
5. What is the **target market** — GB only, EU only, both, plus any
   other regimes (US / CA / AU / NZ / IN / ...)? Each regime layers its
   own scheme on top.
6. What **enclosure** carries the mains modules in the finished
   product? Is it Sense360-supplied or third-party? Has its flame /
   IP / IK rating been verified?
7. Is the Sense360 Core's **Wi-Fi / Bluetooth radio** active in any
   product variant that contains `S360-400` or `S360-320`? If yes,
   RED / UK RER applies and the radio-module pre-certification status
   must be confirmed.
8. Who is the **designated manufacturer** for the purposes of UKCA /
   CE? Where will the technical file be retained, by whom, and for
   how long?
9. What is the **production-test plan** for shipped units? (End-of-line
   hipot, leakage, earth continuity, functional?)
10. What is the **incident / field-failure / serious-incident reporting
    procedure** required by the applicable regulation?

## Release blockers

Until each of the items above is satisfied:

- `S360-400` Sense360 240v PSU **must not** be marked preview-ready,
  stable-ready, CE-ready, UKCA-ready, "safe for mains", or
  "approved for mains" in any file in this repository.
- `S360-320` Sense360 TRIAC **must not** be marked preview-ready,
  stable-ready, CE-ready, UKCA-ready, "safe for mains", or
  "approved for mains" in any file in this repository. HW-005 is a
  separate, additional blocker on this module.
- Any future config string that introduces a mains-input slot (`PWR`)
  or a mains-output slot (`FanTRIAC`) inherits both blockers above and
  is itself not preview-ready / stable-ready until those blockers are
  cleared.
- Production Release-One (`Ceiling-POE-VentIQ-RoomIQ`) is unaffected,
  because Release-One uses `S360-410` PoE PSU and does not include
  either mains module.

## Do-not-change / do-not-claim

This document **does not** change, and **must not be read as
changing**, any of the following:

- The Sense360 hardware catalog (`config/hardware-catalog.json`) — every
  `schematic_status` value is left as committed.
- The product catalog (`config/product-catalog.json`) — every lifecycle
  status is left as committed.
- The WebFlash build matrix (`config/webflash-builds.json`) and
  compatibility list (`config/webflash-compatibility.json`).
- Any product YAML under `products/` or any WebFlash wrapper under
  `products/webflash/`.
- Any package YAML under `packages/**`, including
  [`packages/hardware/power_240v.yaml`](../../packages/hardware/power_240v.yaml)
  and [`packages/expansions/fan_triac.yaml`](../../packages/expansions/fan_triac.yaml).
- Any workflow under `.github/workflows/`, any script under `scripts/`,
  any test under `tests/`, any component under `components/`, or any
  header under `include/`.
- Production Release-One (`Ceiling-POE-VentIQ-RoomIQ`), its artifact
  name, its build matrix, its compatibility entry, its product YAML,
  or its WebFlash wrapper.
- The HW-005 blocked status of `S360-320` / FanTRIAC.
- The Release-One exclusion status of Sense360 LED (`S360-300`).

This document **does not claim** any of the following, anywhere, for
any Sense360 board or product:

- CE-marked / CE-ready
- UKCA-marked / UKCA-ready
- LVD-compliant
- EMC-compliant
- RED-compliant
- RoHS-compliant
- "safe for mains"
- "approved for mains"
- shippable
- production-ready (for any mains-voltage SKU)

Any such claim must be made outside this repository by a qualified
party with the technical file and test reports in hand. No such claim
is made here.

## References (informational, official entry points only)

These are entry points to the **official** regulatory sources. They are
listed so that a qualified review knows where to start; they are
**not** summarised, paraphrased, or interpreted here, and inclusion
does **not** indicate that the linked regime applies to any Sense360
product. Each link is an official-source entry point only.

- UK UKCA marking — GOV.UK guidance landing page
  (https://www.gov.uk/guidance/using-the-ukca-marking).
- UK Electrical Equipment (Safety) Regulations 2016 — full text on
  legislation.gov.uk
  (https://www.legislation.gov.uk/uksi/2016/1101/contents/made).
- UK Electromagnetic Compatibility Regulations 2016 — full text on
  legislation.gov.uk
  (https://www.legislation.gov.uk/uksi/2016/1091/contents/made).
- UK Radio Equipment Regulations 2017 — full text on legislation.gov.uk
  (https://www.legislation.gov.uk/uksi/2017/1206/contents/made).
- EU Low Voltage Directive 2014/35/EU — European Commission page
  (https://single-market-economy.ec.europa.eu/sectors/electrical-and-electronic-engineering-industries-eei/low-voltage-directive-lvd_en).
- EU Electromagnetic Compatibility Directive 2014/30/EU — European
  Commission page
  (https://single-market-economy.ec.europa.eu/sectors/electrical-and-electronic-engineering-industries-eei/electromagnetic-compatibility-emc-directive_en).
- EU Radio Equipment Directive 2014/53/EU — European Commission page
  (https://single-market-economy.ec.europa.eu/sectors/electrical-and-electronic-engineering-industries-eei/radio-equipment-directive-red_en).
- EU CE marking — European Commission page
  (https://single-market-economy.ec.europa.eu/single-market/ce-marking_en).
- EU RoHS Directive 2011/65/EU — European Commission page
  (https://environment.ec.europa.eu/topics/waste-and-recycling/rohs-directive_en).

Inclusion of these links is informational only and `Not proven by this
repository`. Blog summaries, vendor white-papers, and unofficial
commentary are deliberately excluded.

## Files changed by this assessment

This assessment is intentionally minimal. It adds **one** new doc and
applies **three** small cross-link edits so the tracker is
discoverable.

- **New** — `docs/compliance/mains-voltage-uk-eu-assessment.md`
  (this document).
- **Edited (cross-link only)** —
  [`../hardware/remaining-board-documentation-audit.md`](../hardware/remaining-board-documentation-audit.md)
  gains a one-line "See" pointer to this document in the existing
  "Mains-voltage safety and compliance note" section, and the
  `S360-320` and `S360-400` rows in the Decision table gain a one-line
  "Tracked in" pointer.
- **Edited (audit row only)** —
  [`../cleanup-audit.md`](../cleanup-audit.md) gains a single row in
  the Findings table for this new doc, classified as `current`.
- **Edited (one bullet)** —
  [`../hardware-catalog.md`](../hardware-catalog.md) gains a bullet
  under "Companion file" pointing at this document.

No other file is changed.

## Validation

The following commands were run against the working tree after writing
this document. None of them should be affected by the addition of this
docs-only assessment, and all current tests continue to pass.

```text
python3 tests/test_product_catalog.py
python3 tests/test_product_catalog_consistency.py
python3 tests/validate_webflash_builds.py
python3 tests/test_webflash_compatibility.py
python3 tests/test_webflash_artifact_naming.py
python3 tests/test_validate_webflash_release_notes.py
python3 tests/test_generate_webflash_release_notes.py
python3 tests/test_product_substitutions.py
python3 tests/test_release_one_entity_names.py
python3 tests/validate_configs.py
```

Sanity greps:

```text
grep -RIn "CE-ready\|UKCA-ready\|LVD-compliant\|safe for mains\|approved for mains" docs config products packages
grep -RIn "S360-400\|S360-320\|240v\|240V\|230v\|230V\|mains\|earth\|Class I\|Class II\|SELV" docs config products packages
```

The first grep must continue to return zero hits in any non-warning
context — the only occurrences introduced by this document are inside
"must not" / "does not claim" / "Not proven by this repository"
framing.

## COMPLIANCE-001 audit log

This section is the dated investigation log for **COMPLIANCE-001** —
the mains-voltage UK / EU assessment tracker authored by this
document. Each row records a documentation-only re-check of the
committed mains-voltage / safety / compliance evidence available in
this repository against the
[Board table](#board-table),
[Product classification — questions](#product-classification--questions),
[Protection class — decision tree](#protection-class--decision-tree),
[Standards and regulations — applicability checklist](#standards-and-regulations--applicability-checklist),
[Electrical-safety topics — checklist](#electrical-safety-topics--checklist),
[EMC topics — checklist](#emc-topics--checklist),
[Evidence required before any "preview" promotion](#evidence-required-before-any-preview-promotion),
[Evidence required before any "stable" / shipping promotion](#evidence-required-before-any-stable--shipping-promotion),
[Technical-file checklist](#technical-file-checklist),
[Declaration of Conformity — checklist](#declaration-of-conformity--checklist),
[Open questions for compliance engineer / test lab](#open-questions-for-compliance-engineer--test-lab),
[Release blockers](#release-blockers), and
[Do-not-change / do-not-claim](#do-not-change--do-not-claim) sections
above. An audit-log entry **does not** by itself promote any row of
this tracker from `Not proven by this repository` / `To be confirmed`
/ `Requires qualified review` / `Likely applicable` to anything
stronger, produce a CE / UKCA / FCC / UL / LVD / RED / EMC / RoHS
conformity claim, produce a limited advanced / manual-warning
sign-off (which requires committed qualified-electrician / safety-
review evidence the repository does not have), mark COMPLIANCE-001
resolved or cleared for `S360-320` or `S360-400`, flip
`schematic_status` of `S360-320` or `S360-400` in
[`../../config/hardware-catalog.json`](../../config/hardware-catalog.json),
promote any board to `preview` / `stable` / `production`, remove
the BLOCKED / UNVERIFIED banner or the mains-voltage /
qualified-electrician warnings from
[`../../packages/expansions/fan_triac.yaml`](../../packages/expansions/fan_triac.yaml),
add a `FanTRIAC`- or `PWR`-bearing entry to
[`../../config/webflash-builds.json`](../../config/webflash-builds.json),
move any downstream follow-up PR (`HW-005`, `HW-PINMAP-320-FOLLOWUP`,
`HW-CATALOG-320`, `PACKAGE-TRIAC-001`, `PRODUCT-TRIAC-001`,
`PRODUCT-TRIAC-002`, in-repo `WF-TRIAC-001`, `RELEASE-TRIAC-001`,
`WF-IMPORT-TRIAC-001`, `HW-ASSETS-400`, `HW-PINMAP-400-FOLLOWUP`,
`PACKAGE-POWER-400-001`) off its current state, realise the
intended advanced / manual-warning long-term product posture for
FanTRIAC per
[`../hardware/s360-320-r4-triac.md` Advanced / manual-warning product posture](../hardware/s360-320-r4-triac.md#advanced--manual-warning-product-posture)
beyond the wording-only `PRODUCT-TRIAC-001` notes-edit already
landed, change Release-One
(`Ceiling-POE-VentIQ-RoomIQ` / `v1.0.0` / `stable`,
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`), change
the LED preview path (`Ceiling-POE-VentIQ-RoomIQ-LED` /
`status: preview` / `channel: preview`), advance
CORE-ABSTRACT-BUS-001 (alias for
[`../release-one-hardware-audit.md` Required follow-ups #2 / #3](../release-one-hardware-audit.md#required-follow-ups)),
or claim that any qualified electrical-safety review,
isolation-barrier measurement, creepage / clearance measurement,
fusing / over-current / surge / thermal-protection decision,
PCB-finger / connector-rating decision, enclosure / IP / IK /
flame-rating decision, conducted / radiated EMI capture, immunity
test, harmonics / flicker test, or accredited test-lab report has
been performed. The only way to move any row of this tracker off
its current value is to land the evidence enumerated in
[Evidence required before any "preview" promotion](#evidence-required-before-any-preview-promotion)
and / or
[Evidence required before any "stable" / shipping promotion](#evidence-required-before-any-stable--shipping-promotion)
together with the qualified-review attribution required by each
checklist row.

| Audit date | Scope | Files inspected | Outcome |
|---|---|---|---|
| 2026-05-18 | COMPLIANCE-001 / `S360-320` mains-voltage advanced / manual-warning sign-off evidence-pass investigation (per the [`../cleanup-audit.md`](../cleanup-audit.md) follow-up PR list, after the 2026-05-18 [`S360-100-BENCH-001` evidence-pass re-check](../cleanup-audit.md#s360-100-bench-001-update-2026-05-18-evidence-pass-investigation), the [`TRIAC-QUEUE-001` normalization](../cleanup-audit.md#triac-queue-001-update-remaining-fantriac-chain-normalized-after-package-deferral), the [`PACKAGE-TRIAC-001` deferral](../cleanup-audit.md#package-triac-001-update-deferred--hw-005--hw-pinmap-320-followup--compliance-001-not-landed), the [`PRODUCT-TRIAC-002` deferral](../cleanup-audit.md#product-triac-002-update-deferred--package-triac-001-not-landed), the [`PRODUCT-TRIAC-001` notes-only reclassification](../cleanup-audit.md#product-triac-001-update-reclassify-fantriac-as-advancedmanual-warning), and the 2026-05-18 [`HW-PINMAP-320-FOLLOWUP` evidence-pass re-check](../cleanup-audit.md#hw-pinmap-320-followup-update-2026-05-18-evidence-pass-investigation)). Re-check whether any new committed evidence supports (i) **standard-exposure clearance** for `S360-320` under COMPLIANCE-001 (CE / UKCA / FCC / UL / LVD / RED / EMC / RoHS conformity for the finished product placed on the market); (ii) a **limited advanced / manual-warning sign-off** that records, by named qualified party and date, the scope of an advanced / manual-warning posture distinct from compliance certification; or (iii) **formal compliance certification** evidence (accredited test-lab report, signed Declaration of Conformity, marking artwork, production-control plan) for any S360-320-bearing finished product. The re-check evaluates committed evidence only against the strict evidence standards in this tracker (a schematic identifies components and nets but does **not** prove compliance; an artifact index identifies missing files but does **not** prove compliance; PCB / Gerber / KiCad / layout is needed for creepage / clearance and isolation geometry; BOM / CPL is needed for component ratings and assembly review; bench / thermal / EMI / real-load data is needed for operating behaviour; formal certification requires actual certification / test evidence; advanced / manual-warning sign-off can be a policy decision but must clearly say it is **not** compliance certification; compliance must not be inferred from "advanced / manual-warning UX exists" nor from "schematic exists"). | [`../hardware/schematics/S360-320-R4.pdf`](../hardware/schematics/S360-320-R4.pdf) (HW-ASSETS-003 module-side schematic, byte-identical to upload; SHA256 `4cd0685251dcdbc7aa8933cbfa92008df46940b6349f0dea91d32e1028c2911f`; 54,565 bytes — identifies `Q1 BT136S-600D,118` TRIAC, `U1 MOC3023M` optotriac driver, `OK1 EL814` zero-cross optocoupler, gate-resistor `R1 1 kΩ`, snubber-return `R2 100 Ω`, optotriac LED-side current limit `R3 220 Ω`, zero-cross pull-up `R4 10 kΩ`, symmetric AC-side bias `R5 33 kΩ` / `R6 33 kΩ`, 3-pin AC LINE input `J1`, 2-pin LOAD output `J2`, 4-pin "From Core" connector `J3`; **does not** establish any creepage / clearance value, any component rating, any isolation-barrier rating, any L / N / PE assignment on `J1`, any fusing / over-current decision, any thermal envelope, any EMI behaviour, or any compliance claim); [`../hardware/artifacts/S360-320-R4.md`](../hardware/artifacts/S360-320-R4.md) (HW-ASSETS-003 curated artifact index — confirms KiCad schematic source, KiCad PCB source, KiCad project metadata, BOM, CPL / pick-and-place, Gerbers, drill files, STEP, and board images are all `not provided in this upload` per [§Files NOT provided in this upload](../hardware/artifacts/S360-320-R4.md#files-not-provided-in-this-upload), and that the AC LINE `J1` 3-pin function and PCB-level creepage / clearance and component voltage / power ratings are all COMPLIANCE-001-adjacent per [§Open questions / verification needed](../hardware/artifacts/S360-320-R4.md#open-questions--verification-needed)); [`../hardware/s360-320-r4-triac.md`](../hardware/s360-320-r4-triac.md) (HW-PINMAP-320 audit doc — §[Compliance / safety status](../hardware/s360-320-r4-triac.md#compliance--safety-status), §[Advanced / manual-warning product posture](../hardware/s360-320-r4-triac.md#advanced--manual-warning-product-posture), §[Known unresolved issues](../hardware/s360-320-r4-triac.md#known-unresolved-issues), §[Required evidence before implementation](../hardware/s360-320-r4-triac.md#required-evidence-before-implementation), §[HW-PINMAP-320-FOLLOWUP audit log](../hardware/s360-320-r4-triac.md#hw-pinmap-320-followup-audit-log) — confirms no COMPLIANCE-001 sign-off recorded, advanced / manual-warning posture remains intent-only); [`../hardware/s360-100-r4-core.md`](../hardware/s360-100-r4-core.md) §[J15 — TRIAC fan module connector (4-pin)](../hardware/s360-100-r4-core.md#j15--triac-fan-module-connector-4-pin) (Core-side `J15` 4-pin connector capture — low-voltage interface only; not in COMPLIANCE-001 scope on its own); [`../../packages/expansions/fan_triac.yaml`](../../packages/expansions/fan_triac.yaml) (header BLOCKED / UNVERIFIED banner intact; `output: ac_dimmer` topology intact; `fan_triac_gate_pin` / `fan_triac_zc_pin` substitutions intact; `method: leading`, `init_with_half_cycle: true`, default `fan_triac_line_frequency: "50"`, `fan_triac_min_power: "10"` intact; SX1509-rejection clause intact; the `IMPORTANT:` block stating "**The fan load is mains AC. Wiring must be done by a qualified electrician and only with a TRIAC dimmer module rated for the load.**" intact; mains-voltage / qualified-electrician warnings preserved); [`../../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml) (blocked-reference product YAML; placeholder `fan_triac_gate_pin: GPIO5` / `fan_triac_zc_pin: GPIO6` intact; **provably disagrees** with the `S360-100-R4` schematic per HW-PINMAP-320); [`../../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml`](../../products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml) (blocked WebFlash wrapper; retained as reference only; not in any build matrix); [`../../config/hardware-catalog.json`](../../config/hardware-catalog.json) `S360-320` row (`schematic_status: cataloged_unverified`; no `schematic_file`) and `S360-400` row (`schematic_status: cataloged_unverified`; no `schematic_file`); [`../../config/product-catalog.json`](../../config/product-catalog.json) `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` entry (`status: blocked`, `blocker: HW-005`, `reason` unchanged, `webflash_build_matrix: false`, no `artifact_name`, advanced / manual-warning candidate posture recorded notes-only by [PRODUCT-TRIAC-001](../cleanup-audit.md#product-triac-001-update-reclassify-fantriac-as-advancedmanual-warning)); [`../../config/webflash-builds.json`](../../config/webflash-builds.json) (no FanTRIAC- and no PWR-bearing build; only `Ceiling-POE-VentIQ-RoomIQ` stable and `Ceiling-POE-VentIQ-RoomIQ-LED` preview); [`../../config/webflash-compatibility.json`](../../config/webflash-compatibility.json) (`FanTRIAC` reserved in `canonical_modules` subject to the fan-driver `max-one-of` rule; `FanTRIAC` carried in Release-One and LED preview `blocked_modules`); [`../hardware/board-readiness-matrix.md`](../hardware/board-readiness-matrix.md) §[`S360-320` Sense360 TRIAC](../hardware/board-readiness-matrix.md#s360-320-sense360-triac) (`blocked` + `compliance-gated`) and §[`S360-400` Sense360 240v PSU](../hardware/board-readiness-matrix.md#s360-400-sense360-240v-psu) (`cataloged_unverified / compliance-gated`); [`../hardware/package-readiness-matrix.md`](../hardware/package-readiness-matrix.md) `fan_triac.yaml` row (`timing/compliance-pending` + `needs-package-reconciliation` + `blocked-from-standard-exposure`) and `power_240v.yaml` row (`schematic-evidence-pending` + `needs-package-reconciliation` + `timing/compliance-pending`); [`../hardware/remaining-board-documentation-audit.md`](../hardware/remaining-board-documentation-audit.md) Sense360 TRIAC / Sense360 240v PSU sub-sections (`blocked` / `cataloged-unverified`, `not-needed-for-release-one`); [`../hardware/firmware-package-mapping-audit.md`](../hardware/firmware-package-mapping-audit.md) FanTRIAC placeholder-GPIOs row (`blocked`); [`../product-availability-taxonomy.md`](../product-availability-taxonomy.md) `S360-320 Sense360 TRIAC` and `S360-400 Sense360 240v PSU` snapshot rows (`blocked` + `compliance-gated` / `design-pending` + `compliance-gated`); [`../release-one-hardware-audit.md`](../release-one-hardware-audit.md) §[FanTRIAC mapping resolution](../release-one-hardware-audit.md#fantriac-mapping-resolution), §[Missing evidence checklist](../release-one-hardware-audit.md#missing-evidence-checklist), §[Timing constraint](../release-one-hardware-audit.md#timing-constraint-ac_dimmer-vs-sx1509-expander), §[Required follow-ups](../release-one-hardware-audit.md#required-follow-ups); [`../cleanup-audit.md`](../cleanup-audit.md) §[PRODUCT-TRIAC-001 update](../cleanup-audit.md#product-triac-001-update-reclassify-fantriac-as-advancedmanual-warning), §[PRODUCT-TRIAC-002 update](../cleanup-audit.md#product-triac-002-update-deferred--package-triac-001-not-landed), §[PACKAGE-TRIAC-001 update](../cleanup-audit.md#package-triac-001-update-deferred--hw-005--hw-pinmap-320-followup--compliance-001-not-landed), §[TRIAC-QUEUE-001 update](../cleanup-audit.md#triac-queue-001-update-remaining-fantriac-chain-normalized-after-package-deferral), §[S360-100-BENCH-001 update](../cleanup-audit.md#s360-100-bench-001-update-2026-05-18-evidence-pass-investigation), §[HW-PINMAP-320-FOLLOWUP update](../cleanup-audit.md#hw-pinmap-320-followup-update-2026-05-18-evidence-pass-investigation); the [`sense360store/WebFlash`](https://github.com/sense360store/WebFlash) repository's runtime advanced / manual-warning UX `WF-TRIAC-001` slice (out-of-repo reference only — runtime UX gate; **does not** import firmware, **does not** add a manifest build, **does not** flip `webflash_build_matrix`, **does not** change `release_one_required_configs` / REQUIRED_CONFIGS or kits, and **does not** constitute compliance evidence, qualified electrical-safety review, or formal certification of any kind). | **Status remains open / not cleared.** **COMPLIANCE-001 remains open for `S360-320`** under all three evaluation paths: (i) **standard-exposure clearance** is not achievable (no schematic-side compliance evidence beyond component identification; no PCB / KiCad / Gerbers / BOM / CPL / drill / STEP / board images committed to permit a creepage / clearance / isolation-coordination / component-rating review; no fusing / over-current / surge / thermal protection analysis on file; no `J1` / `J2` connector voltage / current / wire-range / torque / UL or VDE or TUV or IEC certification record; no enclosure / IP / IK / flame-rating evidence; no thermal characterisation of `Q1 BT136S-600D` at the rated load; no conducted / radiated EMI capture, no immunity test, no harmonics / flicker test; no UKCA / CE / FCC / UL applicability decision or accredited test-lab report; no qualified-electrician / safety-review sign-off; no real-load test evidence; no phase-cut dimming standards analysis; AC LINE `J1` 3-pin function — L / N / PE / doubled-line — remains `not recorded` and silkscreen-evidence-required; product-classification questions in [§Product classification — questions](#product-classification--questions) remain `To be confirmed`; protection-class decision in [§Protection class — decision tree](#protection-class--decision-tree) remains `Requires qualified review`; every standards-applicability row in [§Standards and regulations — applicability checklist](#standards-and-regulations--applicability-checklist) stays `Likely applicable` / `To be confirmed` / `Requires qualified review` / `Not proven by this repository`; every electrical-safety topic in [§Electrical-safety topics — checklist](#electrical-safety-topics--checklist) stays `Not proven by this repository`; every EMC topic in [§EMC topics — checklist](#emc-topics--checklist) stays `Not proven by this repository`); (ii) **limited advanced / manual-warning sign-off** is not achievable today either — sign-off requires a committed scope and a named qualified party (qualified-electrician / safety-review record) plus an explicit "**this is not compliance certification**" framing for the recorded scope, and the repository carries none of these inputs (no operator / reviewer / sign-off identity, no review date, no observed `S360-320-R4` board serial / batch, no scope-of-sign-off statement, no acknowledged load-type matrix, no acknowledged installation-method statement, no acknowledged target-market statement, no qualified-electrician acknowledgement of the AC LINE `J1` 3-pin function); the long-term advanced / manual-warning posture recorded in [`../hardware/s360-320-r4-triac.md` Advanced / manual-warning product posture](../hardware/s360-320-r4-triac.md#advanced--manual-warning-product-posture) is therefore confirmed as **intent only** and remains unrealised by any committed compliance evidence — the only realised piece is the wording-only [`PRODUCT-TRIAC-001`](../cleanup-audit.md#product-triac-001-update-reclassify-fantriac-as-advancedmanual-warning) catalog-notes edit, which is a policy-direction record and **not** a compliance sign-off; (iii) **formal compliance certification** is not achievable — no accredited test-lab report, no signed Declaration of Conformity, no marking artwork, no production-control plan, and no Authorised Representative appointment is present in the repository for any `S360-320`-bearing finished product, and per [§Non-goals](#non-goals) this repository deliberately cannot host the technical file or the signed DoC. The [Board table](#board-table) row for `S360-320` therefore stays **`Not proven by this repository; additionally HW-005 blocked.`** with `Requires qualified review` next-evidence framing. The Board table row for `S360-400` stays **`Not proven by this repository.`** with the same framing (this re-check inspected `S360-400` row evidence in parallel because the COMPLIANCE-001 tracker applies to both mains-voltage modules, and confirms `HW-ASSETS-400` / module-side schematic + BOM + layout + finished-product context all remain owed; no formal `S360-400` slice work is initiated by this re-check). The [Release blockers](#release-blockers) section stays in force for both `S360-320` and `S360-400`. **No package, product, catalog, WebFlash, release, or import state changes** as a result of this re-check. The [`packages/expansions/fan_triac.yaml`](../../packages/expansions/fan_triac.yaml) BLOCKED / UNVERIFIED banner and the mains-voltage / qualified-electrician warnings stay in place; the `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` entry in [`../../config/product-catalog.json`](../../config/product-catalog.json) stays `status: blocked`, `blocker: HW-005`, `reason` unchanged, `webflash_build_matrix: false`, no `artifact_name`; `FanTRIAC` stays carried in Release-One and LED preview `blocked_modules` in [`../../config/webflash-compatibility.json`](../../config/webflash-compatibility.json) and reserved in `canonical_modules` subject to the fan-driver `max-one-of` rule; `S360-320` `schematic_status` stays `cataloged_unverified` with no `schematic_file` in [`../../config/hardware-catalog.json`](../../config/hardware-catalog.json); `S360-400` `schematic_status` stays `cataloged_unverified` with no `schematic_file`; the HW-PINMAP-320 audit doc at [`../hardware/s360-320-r4-triac.md`](../hardware/s360-320-r4-triac.md) stays `partial — schematic evidence available; package reconciliation, timing validation, and compliance/certification pending`; HW-005 stays `blocked`; HW-PINMAP-320-FOLLOWUP stays outstanding; PACKAGE-TRIAC-001 stays **deferred**; PRODUCT-TRIAC-002, in-repo WF-TRIAC-001, RELEASE-TRIAC-001, and WF-IMPORT-TRIAC-001 stay **blocked**; HW-ASSETS-400 / HW-PINMAP-400-FOLLOWUP / PACKAGE-POWER-400-001 stay outstanding for `S360-400`. Release-One stays `Ceiling-POE-VentIQ-RoomIQ`, version `1.0.0`, channel `stable`, artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag [`v1.0.0`](https://github.com/sense360store/esphome-public/releases/tag/v1.0.0). The LED preview path stays `Ceiling-POE-VentIQ-RoomIQ-LED`, `status: preview`, `channel: preview`, artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`. The Sense360 LED Release-One exclusion is unchanged. The Core J10 vs RoomIQ J6 pin-order open question is not resolved. CORE-ABSTRACT-BUS-001 (alias for [`../release-one-hardware-audit.md` Required follow-ups #2 / #3](../release-one-hardware-audit.md#required-follow-ups)) is not advanced. The runtime advanced / manual-warning UX `WF-TRIAC-001` slice already landed in the [`sense360store/WebFlash`](https://github.com/sense360store/WebFlash) repository is **not** affected and does **not** satisfy any row of this tracker — it is a runtime UX gate only and **does not** constitute compliance certification, qualified electrical-safety review, accredited test-lab evidence, a Declaration of Conformity, or a limited advanced / manual-warning sign-off as defined by this tracker. |
| 2026-06-09 | **Closure by owner decision — COMPLIANCE-001-RESOLUTION-001.** Not an evidence pass: no checklist row is re-evaluated and no new technical evidence is claimed. The owner decision record [`../decisions/COMPLIANCE-001-RESOLUTION-001.md`](../decisions/COMPLIANCE-001-RESOLUTION-001.md) resolves COMPLIANCE-001 **by posture**: Sense360 never places `S360-320`, `S360-310`, or `S360-400` on the market (not sold assembled, not a kit of parts, not a populated PCB, not physically bundled in any kit, order, or promotion); design files and firmware publish open-source under CERN-OHL-P for self-builders of their own devices at their own risk; an EXPERIMENTAL publish lane (hard-warned everywhere, never stable-recommended / default / kit-picker / REQUIRED_CONFIGS / verified-for-purchase, gated on a PACKAGE-TRIAC-001-class bench protocol with committed signed attestation) is defined as policy metadata with **no target assigned**. | [`../decisions/COMPLIANCE-001-RESOLUTION-001.md`](../decisions/COMPLIANCE-001-RESOLUTION-001.md); [`../../config/release-channel-policy.json`](../../config/release-channel-policy.json) (`experimental_lane`); [`../../config/product-catalog.json`](../../config/product-catalog.json) (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `status: blocked`, `webflash_build_matrix: false`, no `artifact_name`); [`../../config/room-bundle-fan-variants.json`](../../config/room-bundle-fan-variants.json) (`TRIAC-PUBLISH-ADVANCED-PREVIEW-001` `gated_by` tokens mechanically unchanged). | **Status: CLOSED — resolved by posture (no placing on the market).** Every technical checklist row below stays at its committed value (`Not proven by this repository` / `To be confirmed` / `Requires qualified review`); nothing is promoted; no conformity is claimed. **Reopen trigger:** any future act of placing any mains-touching board on the market reopens COMPLIANCE-001 and requires an external safety and EMC assessment BEFORE that act (indicative path and order-of-magnitude costs recorded in the resolution record: pre-compliance scan, then test-house safety + EMC). The publish-gate behaviour for FanTRIAC is unchanged in the resolution PR — still not published, not buyable, not kit-exposed — until the separate, human-reviewed commissioning PR moves FanTRIAC into the experimental lane. |

This audit log is **closed** with the 2026-06-09 entry above. A further
audit-log entry is owed only if the §reopen trigger fires (any act of
placing a mains-touching board on the market), at which point the
re-opened assessment resumes against the unchanged checklist sections
above — beginning with the evidence classes the 2026-05-18 entry
enumerated: a qualified-electrician / electrical-safety reviewer's
signed scope-and-finding record; committed KiCad PCB source, Gerbers,
BOM, CPL, drill files, STEP, or board images supporting a creepage /
clearance / isolation / component-rating / fusing / thermal / EMI
review; silkscreen / board-image evidence resolving the AC LINE `J1`
3-pin function; an accredited test-lab report covering the applicable
LVD / EESR safety standard(s), the applicable EMC standard(s), and (if
the finished product carries a radio) the applicable RED / UK RER
standards; a signed Declaration of Conformity; marking artwork; a
production-control plan; and a CE / UKCA applicability decision with
its standards set. None of that evidence exists in this repository
today, and the closure above does not create it.

## See also

- [Sense360 Hardware Catalog](../hardware-catalog.md) — canonical board /
  module names, SKUs, revisions, and legacy names.
- [`config/hardware-catalog.json`](../../config/hardware-catalog.json) —
  machine-readable mirror of the catalog with `schematic_status` per
  row.
- [Remaining Board Documentation Audit (HW-004 / HW-006)](../hardware/remaining-board-documentation-audit.md)
  — every catalog row's documentation state, including the existing
  mains-voltage safety and compliance note this document extends.
- [Release-One Hardware Audit](../release-one-hardware-audit.md) — the
  firmware-vs-schematic audit, the HW-005 FanTRIAC blocker, and the
  LED policy.
- [Release-One Configuration](../release-one.md) — the
  `Ceiling-POE-VentIQ-RoomIQ` shipping configuration (PoE, no mains
  inside the product).
- [Cleanup Audit](../cleanup-audit.md) — companion classification of
  stale / current / blocked-reference / legacy-compatible repo
  content; this document is recorded there as `current`.

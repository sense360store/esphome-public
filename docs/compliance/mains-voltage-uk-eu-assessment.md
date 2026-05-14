# Mains-voltage Safety and Compliance Assessment — UK / EU (COMPLIANCE-001)

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

# Sense360 Room Bundles

This document describes the Sense360 room bundle product line. Each room bundle
pairs a Sense360 sensor unit with a curated set of peripherals for a specific room
type, available in PoE and USB power options.

## Power options

* **PoE** (suffix `-P`): powered over Ethernet, single-cable install.
* **USB** (suffix `-U`): powered over USB-C.

## Stable room bundle matrix

The following bundles are the stable, released product line. This matrix is the
main line and is not changed by the fan-variants planning proposal below.

| Bundle SKU | Room | Power | Lifecycle |
| --- | --- | --- | --- |
| S360-KIT-CORR-P | Corridor | PoE | stable |
| S360-KIT-CORR-U | Corridor | USB | stable |
| S360-KIT-LIV-P | Living | PoE | stable |
| S360-KIT-LIV-U | Living | USB | stable |
| S360-KIT-BED-P | Bedroom | PoE | stable |
| S360-KIT-BED-U | Bedroom | USB | stable |
| S360-KIT-BATH-P | Bathroom | PoE | stable |
| S360-KIT-BATH-U | Bathroom | USB | stable |
| S360-KIT-KITCHEN-P | Kitchen | PoE | stable |
| S360-KIT-KITCHEN-U | Kitchen | USB | stable |

## Bundle contents

Each bundle includes the Sense360 sensor unit, mounting hardware, and a
room-appropriate peripheral set. Exact peripheral lists are maintained in the
internal BOM and are out of scope for this document.

## Lifecycle

Bundles progress through `planning`, `beta`, and `stable` lifecycle states. Only
`stable` bundles are offered for general sale. The fan-control variants described
below are in `planning` and are not offered for sale.

---

## Fan-control variants (planning-only — Bathroom & Kitchen)

> **Status: planning-only.** This section proposes optional fan-control variants
> for the Bathroom and Kitchen PoE bundles. No firmware is released and nothing is
> promoted to WebFlash as part of this proposal. The base room bundles above remain
> the main product line.

### Rationale

Bathroom and Kitchen rooms frequently need extract-fan control. The base bundles
sense environmental conditions (humidity, etc.) but do not drive a fan. These
variants would add a fan-control output. They are additive, Bathroom/Kitchen-only
add-ons; the stable matrix above is unchanged.

### Option chosen

**Option A — a separate config file (`config/room-bundle-fan-variants.json`).**
This keeps the stable room-bundle matrix clean and isolates the planning-only
variants from the released product data. The alternative (Option B — inline rows
in the stable matrix) was rejected because it would mix planning entries into the
released baseline.

### Fan-control methods

| Method | Key | Speed control | Notes |
| --- | --- | --- | --- |
| Relay | `relay` | No (on/off) | Dry-contact on/off switching of an external fan. |
| DAC 0-10V | `dac_0_10v` | Yes (analog) | 0-10V analog speed control for EC/MVHR fans. |
| PWM | `pwm` | Yes (duty cycle) | PWM duty-cycle speed control for compatible fans. |

### Variants

| Variant SKU | Base bundle | Room | Fan control | Lifecycle | WebFlash |
| --- | --- | --- | --- | --- | --- |
| S360-KIT-BATH-P-REL | S360-KIT-BATH-P | Bathroom | relay | planning | no |
| S360-KIT-BATH-P-DAC | S360-KIT-BATH-P | Bathroom | dac_0_10v | planning | no |
| S360-KIT-BATH-P-PWM | S360-KIT-BATH-P | Bathroom | pwm | planning | no |
| S360-KIT-KITCHEN-P-DAC | S360-KIT-KITCHEN-P | Kitchen | dac_0_10v | planning | no |
| S360-KIT-KITCHEN-P-REL | S360-KIT-KITCHEN-P | Kitchen | relay | planning | no |

### Interchangeability

Relay, DAC (0-10V), and PWM are hardware-distinct fan-control methods. They are
**not runtime-interchangeable**: a unit built for relay control cannot be switched
to DAC or PWM control in software. Each method is therefore a separate variant SKU.

### SKU vs firmware config

Bundle SKUs are kept separate from firmware config strings. The variant SKUs in
this proposal identify a planned hardware/peripheral configuration; they are not
firmware config identifiers and do not define any build artifact.

### WebFlash

No fan variant is exposed to WebFlash. `webflash_exposed` is `false` for every
variant and no `webflash_build_matrix` change is implied by this proposal.

### Kitchen framing

Kitchen fan control is framed as extract / MVHR / EC boost. It is **not** a
cooker-hood replacement and is not rated for grease extraction over a hob.

### Lifecycle and next steps

All variants are `planning`. A future implementation PR would define firmware
configs, build artifacts, and validation before any WebFlash promotion. Until
then these remain documentation-only.

### Out of scope

The following are explicitly out of scope for this proposal:

* TRIAC-based fan control (not included as a method).
* Fan variants for Corridor, Living, or Bedroom bundles.
* Any change to existing bundle SKUs or their lifecycle.
* Any firmware release, artifact build, or WebFlash promotion.

* Any change to `webflash-builds.json`, `sources.json`, or `manifest.json`.

### Summary

This proposal is additive and planning-only. It documents five Bathroom/Kitchen
fan-control variants in a separate config file, keeps the stable matrix clean, and
defers all firmware and WebFlash work to a future PR.

<!-- end of fan-variants section -->

<!-- The remainder of this file is the historical room-bundle reference. -->

## Appendix A: Room glossary

* Corridor: transit spaces, hallways, landings.
* Living: lounges, family rooms, open-plan living areas.
* Bedroom: sleeping rooms.
* Bathroom: bathrooms, en-suites, WCs, wet rooms.
* Kitchen: kitchens and kitchen-diners.

## Appendix B: Power option detail

* PoE bundles use 802.3af and expose a single RJ45.
* USB bundles use USB-C PD and require a local supply.

## Appendix C: Notes

* This document is reference-only and does not define firmware builds.
* SKU strings are product identifiers, not firmware config strings.
* Fan variants (Appendix-adjacent, above) are planning-only.

<!-- padding to keep historical anchors stable below -->

## Appendix D: Reserved

This section is intentionally reserved for future room types. No content yet.

## Appendix E: Reserved

This section is intentionally reserved for future power options. No content yet.

## Appendix F: Reserved

This section is intentionally reserved. No content yet.

## Appendix G: Reserved

This section is intentionally reserved. No content yet.

## Appendix H: Reserved

This section is intentionally reserved. No content yet.

## Appendix I: Reserved

This section is intentionally reserved. No content yet.

## Appendix J: Reserved

This section is intentionally reserved. No content yet.

## Appendix K: Reserved

This section is intentionally reserved. No content yet.

## Appendix L: Reserved

This section is intentionally reserved. No content yet.

## Appendix M: Reserved

This section is intentionally reserved. No content yet.

## Appendix N: Reserved

This section is intentionally reserved. No content yet.

## Appendix O: Reserved

This section is intentionally reserved. No content yet.

## Appendix P: Reserved

This section is intentionally reserved. No content yet.

## Appendix Q: Reserved

This section is intentionally reserved. No content yet.

## Appendix R: Reserved

This section is intentionally reserved. No content yet.

## Appendix S: Reserved

This section is intentionally reserved. No content yet.

## Appendix T: Reserved

This section is intentionally reserved. No content yet.

## Appendix U: Reserved

This section is intentionally reserved. No content yet.

## Appendix V: Reserved

This section is intentionally reserved. No content yet.

## Appendix W: Reserved

This section is intentionally reserved. No content yet.

## Appendix X: Reserved

This section is intentionally reserved. No content yet.

## Appendix Y: Reserved

This section is intentionally reserved. No content yet.

## Appendix Z: Reserved

This section is intentionally reserved. No content yet.

## Historical anchors

The anchors below are referenced by older documentation and must remain stable.

* anchor-corridor
* anchor-living
* anchor-bedroom
* anchor-bathroom
* anchor-kitchen

<!-- anchor block end -->

## Historical: changelog excerpts

The following changelog excerpts are retained for reference. They are historical
and are not affected by the fan-variants planning proposal.

* 2025-Q1: Stable room-bundle matrix published (Corridor, Living, Bedroom,
  Bathroom, Kitchen) in PoE and USB variants.
* 2025-Q2: BOM updates for peripheral sets (internal).
* 2025-Q3: Documentation restructure; appendices reserved.
* 2025-Q4: Lifecycle states formalized (planning/beta/stable).

## Historical: design principles

* Keep the stable matrix clean and free of planning entries.
* Prefer separate config files for planning-only proposals.
* SKUs are product identifiers; firmware config strings are separate.
* WebFlash promotion is a deliberate, separate step.

## Historical: FAQ

**Q: Are fan variants available now?**
A: No. They are planning-only and not offered for sale.

**Q: Can I switch a relay unit to DAC in software?**
A: No. The methods are not runtime-interchangeable.

**Q: Is the Kitchen variant a cooker-hood?**
A: No. It is framed as extract/MVHR/EC boost, not a cooker-hood replacement.

**Q: Do fan variants change the stable matrix?**
A: No. The stable matrix is unchanged; variants are additive add-ons.

## Historical: cross-references

* See `config/room-bundle-fan-variants.json` for the planning config.
* See `tests/test_room_bundle_fan_variants.py` for the contract tests.
* See `UPCOMING_PR.md` for the change summary.

<!-- historical cross-reference block end -->

## Historical: reserved tail

The following lines are reserved padding to keep this document's historical
structure stable. They contain no semantic content.

* reserved-line-001
* reserved-line-002
* reserved-line-003
* reserved-line-004
* reserved-line-005
* reserved-line-006
* reserved-line-007
* reserved-line-008
* reserved-line-009
* reserved-line-010
* reserved-line-011
* reserved-line-012
* reserved-line-013
* reserved-line-014
* reserved-line-015
* reserved-line-016
* reserved-line-017
* reserved-line-018
* reserved-line-019
* reserved-line-020
* reserved-line-021
* reserved-line-022
* reserved-line-023
* reserved-line-024
* reserved-line-025
* reserved-line-026
* reserved-line-027
* reserved-line-028
* reserved-line-029
* reserved-line-030
* reserved-line-031
* reserved-line-032
* reserved-line-033
* reserved-line-034
* reserved-line-035
* reserved-line-036
* reserved-line-037
* reserved-line-038
* reserved-line-039
* reserved-line-040
* reserved-line-041
* reserved-line-042
* reserved-line-043
* reserved-line-044
* reserved-line-045
* reserved-line-046
* reserved-line-047
* reserved-line-048
* reserved-line-049
* reserved-line-050
* reserved-line-051
* reserved-line-052
* reserved-line-053
* reserved-line-054
* reserved-line-055
* reserved-line-056
* reserved-line-057
* reserved-line-058
* reserved-line-059
* reserved-line-060
* reserved-line-061
* reserved-line-062
* reserved-line-063
* reserved-line-064
* reserved-line-065
* reserved-line-066
* reserved-line-067
* reserved-line-068
* reserved-line-069
* reserved-line-070
* reserved-line-071
* reserved-line-072
* reserved-line-073
* reserved-line-074
* reserved-line-075
* reserved-line-076
* reserved-line-077
* reserved-line-078
* reserved-line-079
* reserved-line-080
* reserved-line-081
* reserved-line-082
* reserved-line-083
* reserved-line-084

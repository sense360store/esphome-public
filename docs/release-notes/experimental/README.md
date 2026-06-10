# Experimental self-build mains release-note drafts

**Canonical id:** `TRIAC-COMMISSIONING-001`

This directory holds release-note **drafts** for firmware published on the
**experimental** build channel — the self-build mains experimental lane
(`EXPERIMENTAL-SELF-BUILD-MAINS-LANE`) defined by
[`docs/decisions/COMPLIANCE-001-RESOLUTION-001.md`](../../decisions/COMPLIANCE-001-RESOLUTION-001.md)
and recorded as policy metadata in
[`config/release-channel-policy.json`](../../../config/release-channel-policy.json)
(`experimental_lane`).

| Config string | Channel | Draft | Target board |
|---|---|---|---|
| `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` | experimental | [`ceiling-poe-ventiq-fantriac-roomiq.md`](ceiling-poe-ventiq-fantriac-roomiq.md) | Sense360 TRIAC (`S360-320`) |

## What the experimental lane is — and is not

The experimental lane publishes firmware whose target hardware is a
**mains-touching board that Sense360 never places on the market** (e.g. the
`S360-320` Sense360 TRIAC). The board is an open-source CERN-OHL-P design;
builders source the parts and assemble it themselves, **as self-builders of
their own devices, entirely at their own risk**.

An experimental-channel build is **never stable, never recommended, never a
customer default, never buyable, never in any kit or kit picker, and never in
`REQUIRED_CONFIGS`**. Functional bench completion (e.g. `PACKAGE-TRIAC-001`,
operator-attested) is **firmware-build + functional bench proof only** and is
**not** an electrical-safety, EMC, or compliance certification. Mains wiring
must only be performed by a competent person, to local regulations.

## These are drafts, not releases

Each draft is **validated structurally** against the WebFlash release-body
contract with
`python3 scripts/validate-webflash-release-notes.py <draft> --channel experimental`
(the four required H2 sections: `## Changelog`, `## Known Issues`,
`## Features`, `## Hardware Requirements`). They are **not** attached to any
GitHub Release by the commissioning PR; cutting the experimental release tag is
a separate, deliberate step. Downstream one-click WebFlash import stays gated by
`WF-IMPORT-TRIAC-001`.

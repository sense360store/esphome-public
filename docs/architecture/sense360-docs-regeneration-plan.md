# Generated documentation and GitHub Pages (SENSE360-CANONICALISATION-001 PR 16)

**Canonical id:** `SENSE360-CANONICALISATION-001` PR 16
**Type:** Migration plan of record, committed before implementation. Charter
scope: *regenerate customer product and technical board documentation; use
room names for customer products and board names for technical hardware
content; remove obsolete terms and duplicated tables; clearly separate
commercial status, firmware lifecycle, WebFlash exposure and hardware
evidence.* Repository: `sense360store/esphome-public`, branched from merged
`main` (PRs 05–11). The charter dependency on PR 15 governs merge order
only: this PR merges after esphome-public #861 and WebFlash #601–#603.

## Starting truth

The published documentation is the `site/` mkdocs tree deployed to GitHub
Pages by the docs-site workflow on merge to `main` (an existing automatic
lane, not a release workflow), plus the generated customer entity tables
(`scripts/generate_product_entity_tables.py`, freshness-gated in CI over
`SERVED_CONFIG_STRINGS`) and the product guides whose titles were aligned
to the canonical bundle names under PRODUCT-KITS-CONSISTENCY-001 N3. The
`docs/` tree carries the technical reference (hardware evidence under
`docs/hardware/`, architecture records, the canonical roadmap).

Naming truth for this PR: customer products are room-named bundles
(`config/room-bundle-skus.json`, names owned commercially by SOT);
technical hardware content is board-named (`config/hardware-catalog.json`
friendly names + SKUs). Four distinct fact axes exist in the declarations
and must never blend in a rendered page: commercial status (SOT's, never
authored here), firmware lifecycle (`config/product-catalog.json`
status/channel), WebFlash exposure (`config/webflash-builds.json` rows),
and hardware evidence (`schematic_status`, bench records).

## Contracts that survive unchanged

1. **Docs describe; `config/` decides.** No declaration, channel,
   lifecycle, matrix row, or commercial state changes; every rendered
   claim traces to a declaration or a recorded owner decision.
2. **No false proof.** Pages state the exact evidence level a fact has
   (compile proof, schematic-backed, bench-attested, operator-pending);
   nothing gains hardware, bench, compliance, or commercial proof by
   being re-rendered.
3. **The Pages deploy lane is untouched** — regenerated content rides the
   normal merge; no workflow dispatch, no publish action by the agent.
4. **Historical records stay verbatim** (archived docs, bench records,
   attestations, execution logs).

## Slices

1. **Audit.** Inventory the rendered site nav and the `docs/` tree:
   which pages are customer product content, which are technical board
   content; every obsolete term occurrence (legacy board names outside
   legacy-reference columns, Base/Pro and Model/Variant language, the
   `Celling` typo class, retired internal IDs in customer-visible pages);
   every duplicated table (the same facts maintained by hand in more
   than one rendered place) with its single-source disposition. Findings
   table recorded here.
2. **Regenerate and retitle.** Customer product pages keyed by room
   names with board names as technical contents beneath (mirroring the
   WebFlash Step 1 model); technical hardware pages keyed by board
   friendly names + SKUs; duplicated tables replaced by the one
   generated or declared source each fact already has; obsolete terms
   corrected or clearly marked legacy-reference-only.
3. **Four-axis separation.** Each customer product page carries four
   distinct, labelled sections — commercial status (mirrored SOT fact,
   never authored here; today nothing is available or buyable), firmware
   lifecycle, WebFlash exposure, hardware evidence — each traced to its
   declaration; a guard pins the axes' presence and prevents cross-axis
   claims (for example a stable channel never implying buyability).
4. Docs, execution notes here, generator freshness + full suite +
   validator pass, PR. The strict mkdocs build gate proves the site
   still renders.

## Honesty limits

Documentation only: no firmware, YAML composition, declaration, release,
channel, lifecycle, commercial or workflow change. Regeneration is not
proof of anything beyond what the source declarations already prove.
Release-One (`Ceiling-POE-VentIQ-RoomIQ`) remains the production stable
customer baseline.

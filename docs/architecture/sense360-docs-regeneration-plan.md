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

1. **Audit.** Executed 2026-07-29. Findings:

   | Item | Finding | Disposition |
   |---|---|---|
   | Site nav customer/technical split | Already correct: the nav is room-led ("Bedroom Bundle (RoomIQ)" etc., D-G2 curated) and engineer docs stay out of it behind the single technical-reference page. | No change. |
   | Room names for customer products | Already satisfied: every product page title leads with the room bundle name and lists board names beneath as technical contents. | No change; pinned by the new guard. |
   | Base/Pro, Model/Variant language | Zero occurrences on rendered customer pages. | Verified clean. |
   | Legacy board names, retired internal IDs on customer pages | Zero occurrences in rendered prose (one internal ID in a CSS comment, not rendered). | Verified clean. |
   | `Celling` typo class | 14 occurrences, all legitimate: rule statements ("never Celling"), evidence-literal KiCad folder paths quoted verbatim, the taxonomy audit record, and this plan. Zero live typos. | Verified clean; evidence literals stay verbatim. |
   | Duplicated tables | One class found: the `docs/product-taxonomy.md` board table restates SKU + friendly-name facts owned by `config/hardware-catalog.json` (its config-token axis is a projection the catalog does not carry, so physical merging would lose it). | Machine-guarded instead of merged: the new guard pins its SKU and friendly-name columns to the JSON catalog, so hand-duplication can no longer drift. |
   | Four-axis separation | Missing: pages carried a channel badge and note but no labelled separation of the four fact axes. | Implemented in slices 2–3. |

2. **Regenerate and retitle.** Executed 2026-07-29 as verification, not
   rewriting: the room-over-board structure already holds on every page
   and the generated entity tables are fresh, so no page was retitled and
   no table moved; the taxonomy board table gained the machine guard
   above instead of a merge.
3. **Four-axis separation.** Executed 2026-07-29. Every served product
   page now carries a labelled "Product status" section with the four
   axes and an explicit independence statement: commercial availability
   (bundles are not currently sold; names and availability are managed in
   the Sense360 product catalogue — no internal IDs in customer copy),
   firmware lifecycle and installer availability (channel words pinned to
   `config/product-catalog.json` per config string by
   `tests/test_product_guide_status_axes.py`), and hardware evidence (a
   pointer to the per-board evidence records, never a restated status —
   avoiding a new duplication class). The guard also bans commerce
   language on every product page, so a stable channel can never read as
   buyability.
4. Docs, execution notes here, generator freshness + full suite +
   validator pass, PR. The strict mkdocs build gate proves the site
   still renders. Executed 2026-07-29; results in the PR body.

## Honesty limits

Documentation only: no firmware, YAML composition, declaration, release,
channel, lifecycle, commercial or workflow change. Regeneration is not
proof of anything beyond what the source declarations already prove.
Release-One (`Ceiling-POE-VentIQ-RoomIQ`) remains the production stable
customer baseline.

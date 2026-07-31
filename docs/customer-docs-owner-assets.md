# Customer docs — Phase 4 owner asset shot list

**Programme:** SENSE360-CUSTOMER-DOCS-001 (Phase 4 preparation)
**Status:** work list only — every asset below is produced by the owner.
Agents maintain this list and the page placeholders; they never supply,
stage, or describe-as-existing any photograph, and this document carries
no attestation, date, or evidence claim.

## How this list works

Each customer page that needs an owner-produced asset carries an HTML
placeholder comment `<!-- owner-asset:<id> -->` at the exact insertion
point. This document is the companion work list: one row per
placeholder. The drift gate in `tests/test_customer_docs_site.py` fails
CI if a placeholder exists on a page without a row here, so the list
cannot silently fall behind the pages.

When an asset is delivered, it replaces its placeholder in the same PR
that adds the image file; the row moves to a "delivered" table only
then, in that PR, with the image path as the evidence link.

## Requested assets (Bathroom — the published room)

| Placeholder id | Page | Shot |
|---|---|---|
| `bathroom-hero-photo` | `site/docs/rooms/bathroom.md` (top) | The assembled ceiling unit mounted in a real bathroom, photographed from below at an angle that shows it in context (ceiling + a hint of the room). One image, landscape. |
| `bathroom-box-contents-flatlay` | `site/docs/rooms/bathroom.md` (What's in the box) | Flat-lay of exactly the boards the Bathroom preset ships: Sense360 Core, Sense360 RoomIQ, Sense360 VentIQ, Sense360 PoE PSU — matching the generated box-contents table on the page. Neutral background, boards labelled or arranged in table order. Radar attachment modules must NOT appear (they are not included). |
| `bathroom-mounting-sequence` | `site/docs/rooms/bathroom.md` (Mount it) | Step sequence (3-6 frames): ceiling position chosen, bracket/base fixed, unit attached, network cable connected, mounted result. Frames will be captioned in the Mount it narrative when they land. |

## Queued for later publication (no placeholders yet)

The Bedroom and Kitchen pages are built ready but deliberately
unpublished; their placeholders are added when the owner changes bundle
visibility. Expect the same three shots per room (hero, box-contents
flat-lay matching that room's preset, mounting sequence — mounting may
be shared if the hardware mounts identically).

## Capture notes (apply to all shots)

- Photograph real production hardware only; no renders presented as
  photographs.
- Box-contents shots must match the room's preset component list at the
  time of capture — the generated table on the page is the checklist.
- No packaging, pricing, or shop-context in frame (nothing is
  commercially available).

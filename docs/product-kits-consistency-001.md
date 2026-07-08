# PRODUCT-KITS-CONSISTENCY-001 — tracking (esphome-public)

Programme tracking file (session guardrail). The lowest non-EXECUTED step for
this repo is the next step a session executes. Scope in esphome-public is
**docs only** — product-guide titles and index. No firmware YAML, no release
surface, no served-data or manifest changes.

**Cross-repo note.** N1 and N2 run in the WebFlash checkout and are tracked by
that repo's copy of this file. This repo owns N3 only.

## SAFETY RULE (non-negotiable)

The 9 `hardware-pending` configs (8 mains/relay fan variants + RoomIQ-LED) all
carry `bench_proof: NONE` and MUST NOT be surfaced as installable kits or
ready products by any step. Kit/product visibility is limited to release-ready
configs (production, or preview with an explicit preview badge). No step in
this programme promotes, unblocks, or displays a hardware-pending or
compile-only config as installable. N3 is a title/name alignment only and
changes no config's installability.

## Step status (esphome-public)

| Step | Scope | Status |
|---|---|---|
| N3 | Align product-guide H1 titles + index with the canonical consumer bundle names in `config/room-bundle-skus.json`, keeping the descriptive module subtitle | **EXECUTED** (this PR) |

## What N3 changed

Product-guide titles, nav, and index links now lead with the canonical
consumer bundle name from
[`config/room-bundle-skus.json`](../config/room-bundle-skus.json), so a
customer moving between these guides and the flasher sees the same product
name. The descriptive module subtitle is retained in parentheses. Every name
traces to a `bundle_name` in `room-bundle-skus.json`:

| Config string | Guide title | Canonical bundle (`room-bundle-skus.json`) |
|---|---|---|
| `Ceiling-POE-RoomIQ` | Bedroom Bundle (RoomIQ) | S360-KIT-BEDROOM-P — Sense360 Bedroom Bundle — PoE |
| `Ceiling-POE-AirIQ-RoomIQ` | Kitchen Bundle (AirIQ + RoomIQ) | S360-KIT-KITCHEN-P — Sense360 Kitchen Bundle — PoE |
| `Ceiling-POE-VentIQ-RoomIQ` | Bathroom Bundle (VentIQ + RoomIQ) | S360-KIT-BATH-P — Sense360 Bathroom Bundle — PoE |
| `Ceiling-POE-VentIQ-RoomIQ-LED` | Bathroom Bundle + LED ring (VentIQ + RoomIQ + LED) | Bathroom Bundle + LED (LED-only bundle SKUs are RoomIQ-LED, so the traceable portion is the Bathroom Bundle base) |

Files touched: `site/docs/products/*.md`, `site/docs/index.md`,
`site/mkdocs.yml`, and a comment-only clarification in
`scripts/generate_product_entity_tables.py` (the comparison-matrix column
labels are the module descriptor from each title). No generated entity table
or matrix cell changed; channel badges are unchanged and remain
channel-accurate. The LED guide keeps its preview badge and preview-channel
warning.

Gate: `python3 scripts/generate_product_entity_tables.py --check`,
`mkdocs build --strict -f site/mkdocs.yml`, `python3 -m yamllint site/mkdocs.yml`,
and the full `pytest tests/` suite all pass.

# PRODUCT-GUIDES-001 — customer product guides on GitHub Pages (tracking)

Programme tracking file (guardrail 7). The lowest non-EXECUTED step is the
next step a session executes. Scope: docs and one deploy workflow only — no
firmware YAML changes, no release surface, no existing-workflow changes, no
application source.

**Goal.** A customer-grade docs site for the four served products, hosted
from this repo via mkdocs-material, with entity tables derived mechanically
from the firmware YAML and gated for freshness.

## Step status

| Step | Repo | Scope | Status |
|---|---|---|---|
| G1 | esphome-public | Scaffold: `site/` mkdocs tree, derivation script, Pages deploy workflow, CONTRIBUTING gate line, this tracking file | **EXECUTED** (this PR) |
| G2 | esphome-public | The four product guides + generated comparison matrix | PENDING |
| G3 | WebFlash | Post-install "next steps" guide links, README/SUPPORT links, shell docs link | PENDING (runs in the WebFlash checkout; requires G2 EXECUTED on this file's main) |

## Decisions of record (ratified by merging G1)

- **D-G1** Hosting: esphome-public repo, GitHub Pages via Actions; the
  guides version alongside the YAML they are derived from.
- **D-G2** Site source: a dedicated `site/` directory with an explicitly
  curated nav. Engineer docs stay out of the customer nav; the site links
  to them only from a single "Technical reference" page.
- **D-G3** Custom domain: later, console action (Pages settings CNAME).
- **D-G4** Placement and LED facts: guides ship with clearly marked
  "guidance being finalised" blocks rather than blocking on owner input.
- **D-G5** The LED preview product gets a guide with the preview channel
  warning prominent.

## What G1 created

- [`site/mkdocs.yml`](../site/mkdocs.yml) — mkdocs-material config: strict
  curated nav (D-G2), no external font/script requests, brand styling in
  [`site/docs/assets/extra.css`](../site/docs/assets/extra.css) mirroring
  the WebFlash brand tokens (brand green `#00bf63`, Murecho with
  system-stack fallback, matching button + channel-badge styling).
- `site/docs/` — Home, product-guide placeholder pages (one per served
  config, each already embedding its derived entity table and carrying the
  D-G4 placeholder blocks; the LED page carries the D-G5 preview warning),
  compare placeholder, and the single Technical reference page.
- [`scripts/generate_product_entity_tables.py`](../scripts/generate_product_entity_tables.py)
  — derives, per served config (`Ceiling-POE-RoomIQ`,
  `Ceiling-POE-AirIQ-RoomIQ`, `Ceiling-POE-VentIQ-RoomIQ`,
  `Ceiling-POE-VentIQ-RoomIQ-LED`), the Home Assistant entities exposed
  (name, type, unit, notes) by resolving the product's package includes
  from its `config/webflash-builds.json` row; writes markdown includes
  under `site/generated/`; `--check` freshness mode. Entities marked
  `internal: true` never reach Home Assistant and are excluded. Tests:
  [`tests/test_generate_product_entity_tables.py`](../tests/test_generate_product_entity_tables.py).
- [`.github/workflows/docs-site.yml`](../.github/workflows/docs-site.yml)
  — the ONE new workflow this programme is allowed: freshness check +
  `mkdocs build --strict` validation on PRs touching the site or the YAML
  it derives from; Pages deploy on pushes to main.
- [`CONTRIBUTING.md`](../CONTRIBUTING.md) — the documented local gate now
  includes `python3 scripts/generate_product_entity_tables.py --check`.

## Deviations / notes of record

- **Guide file location.** The manifest sketches guides at
  `site/products/`; mkdocs requires the page tree inside `docs_dir`, so
  guides live at `site/docs/products/` (`site/mkdocs.yml` sets
  `docs_dir: docs`). Generated includes live at `site/generated/` exactly
  as manifested (outside `docs_dir` so they render only where embedded).
- **`.gitignore` repoint.** The pre-existing `site/` ignore rule (aimed at
  mkdocs' default *output* directory) would have ignored the new tracked
  source tree; it now ignores only the build output
  `site/.site-build/`.
- **`site/requirements.txt`** pins `mkdocs-material` for the workflow so
  the Pages build changes behaviour only via an explicit PR.
- **Owner action pending (runbook step 2).** GitHub Pages must be enabled
  once: Settings → Pages → Source: **GitHub Actions**. Until then the
  deploy job fails while validation stays green.
- **Observation for G2 (no firmware change made — out of scope).** The
  AirIQ board package keeps every air-quality measurement
  `internal: true` and `packages/features/airiq_basic_profile.yaml`
  exposes only a placeholder "Air Quality State" text sensor, so the
  derived `Ceiling-POE-AirIQ-RoomIQ` table legitimately lists no CO2 / PM
  / VOC entities. The G2 guide text must not claim otherwise; exposing
  those entities would be a separate firmware slice outside this
  programme.

## Log

- 2026-07-07 — G1 executed: scaffold, derivation script + tests, deploy
  workflow, CONTRIBUTING gate line, tracking file created. One held PR;
  HOLD FOR OWNER.

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
| G1 | esphome-public | Scaffold: `site/` mkdocs tree, derivation script, Pages deploy workflow, CONTRIBUTING gate line, this tracking file | **EXECUTED** (PR #802) |
| G2 | esphome-public | The four product guides + generated comparison matrix | **EXECUTED** (this PR) |
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

## What G2 created

- **The four product guides** (`site/docs/products/*.md`), replacing the
  G1 placeholders. Each covers: what the product does (plain language,
  every claim traceable to the derived entity set, a catalog field, or a
  board doc); hardware in the configuration; installation via the
  canonical flasher at
  <https://sense360store.github.io/WebFlash/> with the channel note (stable
  support pointer / preview acknowledgement-gate warning per D-G5);
  first-boot Wi-Fi (the `Sense360_Setup` setup network and the per-product
  fallback-AP captive portal, per
  `docs/security/release-firmware-credential-posture.md`); Home Assistant
  adoption via ESPHome discovery (consistent with
  `docs/getting-started.md` / `docs/installation.md`), including the
  honest unprovisioned-firmware security note with the self-build
  pointer; the derived entity table; updating; factory reset / recovery
  (the firmware's Restart / Safe Mode / Factory Reset buttons plus the
  flasher's rescue flow); and specifications linking the board reference
  docs on GitHub (link, don't duplicate pinouts). D-G4 placement /
  LED-meaning placeholder blocks retained.
- **The comparison matrix** —
  [`scripts/generate_product_entity_tables.py`](../scripts/generate_product_entity_tables.py)
  now also generates `site/generated/compare-matrix.md`: module
  composition + hardware SKUs from `config/product-catalog.json`,
  channel + version from `config/webflash-builds.json`, and every
  capability cell a mechanical membership test against the same derived
  entity sets as the tables, under the same `--check` freshness gate (now
  5 files). `site/docs/products/compare.md` embeds it. Tests extended in
  [`tests/test_generate_product_entity_tables.py`](../tests/test_generate_product_entity_tables.py).

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

- **G2 corrections of record.** (a) The G1 placeholder pages described
  the PoE PSU as "IEEE 802.3af"; `docs/hardware/s360-410-r4-poe.md`
  explicitly makes no 802.3af/at compliance claim, so the guides now say
  "powered over Ethernet" without naming the standard. (b) The AirIQ
  profile's `Air Quality State` text sensor is a placeholder that always
  reads `unknown` (`packages/features/airiq_basic_profile.yaml`), so the
  comparison matrix deliberately excludes it from the "Air-quality
  summary" capability row and the AirIQ guide states plainly that the
  module's air-quality measurements are not yet exposed as entities
  (carrying forward the G1 observation; no firmware change made — out of
  scope).

## Log

- 2026-07-07 — G1 executed: scaffold, derivation script + tests, deploy
  workflow, CONTRIBUTING gate line, tracking file created. One held PR;
  HOLD FOR OWNER.
- 2026-07-07 — G2 executed: the four product guides, the generated
  comparison matrix (derivation-script extension + tests), compare page.
  One held PR; HOLD FOR OWNER. G3 (WebFlash) unblocks once this merges to
  main.

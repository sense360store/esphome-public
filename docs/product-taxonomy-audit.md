# Product Taxonomy Audit — PRODUCT-TAXONOMY-AUDIT-001

Cross-repository terminology audit record. This PR corrects
`sense360store/esphome-public` only; findings for the other repositories are
recorded here for the follow-up PRs listed at the end. Programme-level
acceptance of the cross-repo items belongs to
[`sense360store/SOT`](https://github.com/sense360store/SOT) per
`CLAUDE-OPERATING-MODEL.md`.

**Audit date:** 2026-07-15.
**Repositories actually inspected:** `esphome-public`, `SOT`, `WebFlash`,
`sense360zones` (all at their current default-branch heads).
**Not inspected (no repository access identified):** website/documentation
site sources, Shopify/theme/product content (Shopify is a presentation
surface, not a repo-backed source of truth, per the SOT operating model),
mobile-app records. **No claim of cleanliness is made for uninspected
surfaces**; SOT's `messaging.yaml` `known_drift_2026_07` already logs live
customer-facing drift on the Shopify/Pure pages (Comfort/Presence/Wall Core
tiles, Coming-Soon tiles).

## Classification key

| Class | Meaning | Action in this programme |
|-------|---------|--------------------------|
| A | Current and correct | None |
| B | Historical / archive only | Never rewrite |
| C | Compatibility alias required | Keep; never drives new design |
| D | Stale customer-facing text | Fix (this PR for esphome-public) |
| E | Stale technical documentation | Fix (this PR for esphome-public) |
| F | Stale code/config declaration | Fix only when safe; else track |
| G | Ambiguous — owner decision required | Escalate, do not guess |

## Authority model (verified)

Per SOT `CLAUDE-OPERATING-MODEL.md`, esphome-public `CLAUDE.md`, and
WebFlash `CLAUDE.md` / `docs/webflash-contract.md` — these were checked
against each other and are **consistent** (no authority contradiction
found):

| Domain | Owner |
|--------|-------|
| Commercial product / bundle truth, public naming & messaging, programme status | **SOT** (`products.yaml`, `bundles.yaml`, `messaging.yaml`) |
| Physical board identity (SKU, friendly name, sensors, connectors) | **esphome-public** (`config/hardware-catalog.json` / `docs/hardware-catalog.md`) |
| Firmware implementation, product YAML, lifecycle catalog, release matrix | **esphome-public** (`config/product-catalog.json`, `config/webflash-builds.json`) |
| Config-string grammar, artifact naming, signing, distribution | **WebFlash** (mirrored locally in `config/webflash-compatibility.json` / `docs/webflash-contract.md`) |
| Zone configuration tooling | **sense360zones** (no product-taxonomy footprint) |
| Website / Shopify | Presentation surface only — never a source of truth |

One **scope seam** needs an owner decision (G-1 below): SOT approves the
public names "Fan Relay / Fan PWM / Fan DAC" while the hardware catalog's
canonical friendly names are "Sense360 Relay / Sense360 PWM / Sense360 DAC".
Both repos are acting inside their declared authority (public messaging vs
hardware naming), so this is a reconciliation decision, not a broken model.

## Canonical board/SKU taxonomy (verified against `config/hardware-catalog.json`)

S360-100 Core · S360-200 RoomIQ · S360-210 AirIQ · S360-211 VentIQ ·
S360-300 LED · S360-310 Relay (`FanRelay` token) · S360-311 PWM (`FanPWM`) ·
S360-312 DAC (`FanDAC`) · S360-320 TRIAC (`FanTRIAC`) · S360-400 240v PSU
(`PWR`) · S360-410 PoE PSU (`POE`). The list in the audit brief matched the
catalog; no missing or extra SKUs found. There is **no Base/Pro,
Basic/Advanced, Mini, Wall, or Model/Variant axis** in the current line.

## Key decisions applied in this PR

- **Release-One** = the name of the initial release programme and its
  shipped configuration (`Ceiling-POE-VentIQ-RoomIQ`). Preserved in
  historical records, standing invariants, examples that reference the
  v1.0.0 tag, and programme prose. No longer used as the structural frame
  of the taxonomy documentation (`docs/product-taxonomy.md` rewritten;
  enforced by `test_release_one_is_not_a_heading`).
- **Base/Pro**: no current product axis. Legacy filenames
  (`airiq_bathroom_base/pro.yaml`) and read-time aliases stay; new
  authoritative/customer text is forbidden from using the axis (enforced by
  `tests/test_taxonomy_terminology.py` +
  `config/legacy-term-allowlist.json`).
- **Connector vs fitted**: SPS30 / SFA40 / MLX90614(IR temp) are
  connector-supported external attachments, never described as fitted
  board hardware in current docs (enforced).
- **Compiled-driver drift** (BMP390, VEML7700) is documented as tracked
  drift only, never as physical hardware (enforced; firmware itself
  unchanged — dispositions are owner-only items
  `ENTITY-RECONCILE-200-ALS-001` and the BMP390 roadmap record).

---

## Findings: esphome-public (corrected in this PR)

Inventory sweep counts (raw occurrences): Release-One ≈867 across 162 files
(class A — programme name; no misuse found); Comfort/Presence ≈607 across
124 files (overwhelmingly C alias filenames/entity ids + A prose); Base/Pro
variant text, BMP390, VEML7700, HLK-PM01 concentrated in five live docs
(D/E) and three board packages (F, tracked drift annotations in-file).

| # | File | Stale content | Fix | Class |
|---|------|---------------|-----|-------|
| 1 | `docs/product-taxonomy.md` | Release-One as taxonomy frame; VentIQ Base/Pro variant table; BMP390 under AirIQ; VEML7700 as RoomIQ light part; HLK-PM01; RoomIQ sensor list missing PIR/SEN0609/BMP581; "maps 1:1 … published `.bin`" release claim; stale FanTRIAC HW-005 note | Rewritten as a navigation document anchored to the machine-readable authorities | E |
| 2 | `docs/getting-started.md` | "VentIQ Base" / "VentIQ Pro" labels | Relabelled as legacy alias filenames of the single S360-211 board | D |
| 3 | `docs/configuration.md` | VentIQ described as "SHT4x, BMP390, SGP41, optionally MLX90614 + SPS30" | Corrected to catalog truth (SGP41 on board; IR temp + SPS30 connectors) | E |
| 4 | `docs/ci-pipeline.md` | Removed Mini range presented as "validated by CI"; "CI automatically includes it" add-product flow | Marked historical (PRODUCT-DEP-MINI-001); replaced with the declaration-driven (ESP-007) add-product checklist | E |
| 5 | `docs/product-matrix.md` | Mini/Wall/Desk, Comfort/Presence boards, Bathroom Base/Pro tables, Basic/Advanced tiers presented as current | Demoted with an explicit legacy-reference status banner; content retained as historical hardware detail (not deleted) | E→B |
| 6 | `docs/webflash-contract.md` §4 | FanTRIAC note claimed "NOT in `config/webflash-builds.json` … while HW-005 is open" — contradicts `TRIAC-COMMISSIONING-001` / standing invariants (experimental-channel row exists) | Note updated to the current experimental-lane state; all "never stable/buyable/kit" teeth restated. **FanTRIAC doc change — human review required, never auto-merge** | E |

### Deliberately retained (do not "fix")

- `packages/expansions/*`, `packages/hardware/*` legacy alias filenames —
  customer-pinned include paths (C).
- `packages/boards/s360-210-airiq.yaml`, `s360-211-ventiq.yaml`
  (BMP390 compiled), `s360-200-roomiq-climate.yaml` (VEML7700 compiled) —
  tracked firmware drift with in-file annotations; changing compiled
  drivers is firmware behaviour and out of audit scope (F, owner-tracked).
- `docs/hardware/**` evidence records quoting HLK-PM01/BMP390 footprints
  verbatim, `docs/decisions/`, `docs/release-notes/`, `CHANGELOG.md`,
  archived docs — historical evidence (B).
- Release-One in `docs/standing-invariants.md`, `CLAUDE.md`, `README.md`,
  `docs/installation.md`, `examples/*` — programme-name usage referencing
  the shipped baseline (A).
- Mini/Wall tombstones in `config/product-catalog.json`
  (`removal_reason`), Mini/Wall/Basic/Advanced mappings in
  `scripts/product_name_mapper.py` — serve tag-pinned legacy releases (A/C).
- `packages/features/*basic*/*advanced*` profile filenames — behaviour
  profiles, not product tiers (C).
- `Celling` quotes in hardware evidence (literal legacy KiCad folder name)
  (B).

### Safeguards added

- `config/legacy-term-allowlist.json` — machine-readable forbidden-term
  policy + path/reason classification of legitimate legacy locations. Not a
  second product catalog: it points at the existing authorities.
- `tests/test_taxonomy_terminology.py` (19 tests) — forbidden legacy terms
  in current authoritative files (marker/exception aware); AirIQ/VentIQ
  mutual exclusion and RoomIQ independence pinned against
  `config/webflash-compatibility.json` and every `config/webflash-builds.json`
  row; generic `Fan` token ban; max-one-fan-driver; taxonomy doc anchored to
  the catalogs (every SKU + friendly name present, authority links present,
  lifecycle section present, no "all configs released" claim, Release-One
  not a heading, connector parts always in attachment context); bundle
  filenames round-trip the catalog config strings.

---

## Findings: SOT (follow-up PR 1 — no changes made here)

SOT's lifecycle hedging is largely correct ("no invented Base/Pro axis",
programme states `implemented` not `verified`). Items:

| # | Location | Finding | Recommended | Class | Safe automated change? | Owner decision? |
|---|----------|---------|-------------|-------|------------------------|-----------------|
| S-1 | `bundles.yaml` L49 | `webflash_config: Ceiling-POE-AirIQ` does not exist in the build matrix (real config: `Ceiling-POE-AirIQ-RoomIQ`); bundle marked `shipped` | Correct config string or bundle contents | F | Yes, once owner confirms intended contents | Confirm bundle contents |
| S-2 | `products.yaml` L87/99/112, `messaging.yaml` L65 | "Fan Relay / Fan PWM / Fan DAC" approved names vs catalog "Sense360 Relay/PWM/DAC" | Owner picks one public naming; loser becomes alias | G | No | **Yes (G-1)** |
| S-3 | `products.yaml` L69 vs `hardware-catalog.json` | VentIQ legacy name recorded as "AirIQ Bathroom" in SOT but "Bathroom Pro" in the catalog | Record both as old names | E | Yes | No |
| S-4 | `bundles.yaml` L36, roadmap "on sale" | `shipped` bundles with placeholder `shop_url` (CONFIRM) | Resolve CONFIRM before "shipped/on sale" stands | G | No | **Yes** |
| S-5 | `messaging.yaml` L79 | "Wall Core" banned-term CONFIRM still open | Close the CONFIRM | G | No | **Yes** |

## Findings: WebFlash (follow-up PR 2 — no changes made here)

No Base/Pro, BMP390, VEML7700, or HLK-PM01 anywhere; alias/migration
machinery (url-config, naming-policy validator, test fixtures) is correct
category C. Items:

| # | Location | Finding | Recommended | Class | Safe automated change? | Owner decision? |
|---|----------|---------|-------------|-------|------------------------|-----------------|
| W-1 | `scripts/data/module-requirements.js`, `docs/user-guide.md`, `DEVELOPER.md` | AirIQ HCHO connector named **SFA30**; catalog says **SFA40** | Reconcile with hardware catalog (SFA40), noting SFA40 fitment itself is under `HW-PINMAP-210-FOLLOWUP` | G/D | After owner confirms part identity | Yes (part identity) |
| W-2 | `scripts/state.js` `MODULE_LABELS.led='LED Ring'`, `POWER_LABELS` "PoE module"/"PWR module" | Rendered labels use catalog **old names** instead of "Sense360 LED / PoE PSU / 240v PSU" | Switch rendered labels to friendly names | D | Yes | No |
| W-3 | `module-requirements.js` L271, `data.js` L96 | "Integrated I2S microphone (voice models)" — references a Voice model/variant with no SKU | Remove or reword to actual hardware | D/G | After owner confirms | Yes (Voice axis) |
| W-4 | `DEVELOPER.md` vs `validate-naming-policy.js` | Doc says `AirIQProv→AirIQPro`, `BathroomAirIQ→Bathroom`; code maps `→AirIQ`, `→VentIQ`; `VentIQBase/Pro` cited but absent from the table | Align doc to code | E | Yes | No |
| W-5 | `DEVELOPER.md` L121/L143 | Generic `Fan` and `Voice` listed among usable tokens | Align to current token policy | E | Yes | No |
| W-6 | `firmware/sources.json` | `Ceiling-POE-VentIQ-RoomIQ` pinned v1.0.7 while sibling stables are v1.0.8/v1.0.9 | Confirm intended pin | F/G | No | Confirm |

## Findings: sense360zones (no follow-up needed)

Inspected at head `50a8ecb`. **No product-taxonomy footprint at all** — the
repo names only the radar parts it configures (LD2450, SEN0609/C4001);
"Wall/Ceiling" are radar mount orientations, "fan.*" strings are generic
Home Assistant test decoys. Clean.

## Findings: website / commerce (not repo-inspected)

Recorded from SOT `messaging.yaml` `known_drift_2026_07` (drift SOT has
already logged, on external properties): Comfort/Presence/Wall Core wording
on the Pure page; Voice & Bathroom "Coming Soon" tiles; homepage leads with
the Bathroom Bundle. These belong to follow-up PR 4 / owner web tasks.

## Unresolved owner decisions (G items)

1. **G-1 Fan-driver public naming**: "Fan Relay/PWM/DAC" (SOT messaging)
   vs "Sense360 Relay/PWM/DAC" (hardware catalog). One must become the
   public name, the other an alias.
2. **G-2 SFA30 vs SFA40** (WebFlash copy vs catalog) — and the underlying
   SFA40 on-board-vs-connector fitment conflict (`HW-PINMAP-210-FOLLOWUP`).
3. **G-3 VEML7700 vs LTR-303ALS** compiled-driver disposition
   (`ENTITY-RECONCILE-200-ALS-001`) and **BMP390 driver removal** — owner
   inspection of physical boards required; docs now present catalog truth
   with drift notes either way.
4. **G-4 Voice axis** (WebFlash `voice`/"Core Type"/microphone copy) — real
   future product or retired concept?
5. **G-5 SOT CONFIRM backlog**: Air Quality Starter config string /
   `firmware_release`, shipped-bundle shop URLs, "Wall Core", S360-211 SKU
   carry-over note.

## Recommended follow-up PR sequence

1. **SOT** — commercial/programme taxonomy reconciliation (S-1…S-5; owner
   closes G-1, G-5).
2. **WebFlash** — naming, module descriptions, compatibility snapshot
   (W-1…W-6; W-1 depends on G-2, so it can trail).
3. **sense360zones** — none required (verified clean).
4. **Website/docs/commerce** — customer wording per SOT
   `known_drift_2026_07` (owner-driven; not repo-backed here).
5. **Generated cross-repo consistency validation** — extend SOT
   `scripts/validate.py` (or a scheduled workflow) to cross-check SOT
   `bundles.yaml` `webflash_config` values against
   `esphome-public/config/webflash-builds.json`, which would have caught
   S-1 automatically.

No evidence surfaced that requires reordering this sequence.

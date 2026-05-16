# Hardware Artifact Policy (HW-ASSETS-001)

## Purpose

This document defines what hardware-related artifacts (schematics, KiCad
sources, BOMs, pick-and-place files, gerbers, STEP models, board images,
vendor exports) may live in this repository, in what form, and at what
review level. It exists so that downstream PRs can ingest hardware
evidence for individual boards without re-litigating the same questions
each time, and so that `git`-tracked content stays narrow, reviewable,
and free of vendor / OS scratch.

This policy is **documentation only**. It does not:

- change any firmware, product YAML, package YAML, workflow, script,
  test, build matrix, or component code,
- change any value in `config/hardware-catalog.json`,
  `config/product-catalog.json`, `config/webflash-builds.json`, or
  `config/webflash-compatibility.json`,
- introduce Git LFS, a binary artifact store, a release-asset
  convention, or any new CI step,
- promote or demote any module's Release-One status,
- unblock FanTRIAC (HW-005 stays a separate gate),
- change Sense360 LED's exclusion from production Release-One,
- create per-board reference docs, pin tables, or schematic ingest
  beyond what is already committed.

The Release-One shipping configuration remains
`Ceiling-POE-VentIQ-RoomIQ` with artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`. Nothing in this
policy changes that.

## Scope

In scope:

- What artifact classes are recognised (schematic PDFs, schematic
  source, PCB source, project metadata, BOM, CPL / pick-and-place,
  gerbers, STEP / mechanical, board images, vendor exports).
- Which of those classes may be committed to `git` today, which are
  retained-but-not-committed, and which are excluded outright.
- Per-board curated artifact indexes under
  [`docs/hardware/artifacts/`](artifacts/).
- The relationship between **artifact availability** and **firmware /
  WebFlash availability**.

Out of scope (deliberately):

- Choosing a long-term storage backend for large binary artifacts
  (Git LFS, separate hardware-only repo, GitHub Releases, supplier
  archive, etc.). That decision is deferred — see
  [Future storage decision](#future-storage-decision).
- Adding any new board's curated artifact index. Per-board indexes are
  added by their own scoped PRs (HW-ASSETS-002 for S360-100-R4 and
  successor PRs for other boards).
- Any change to YAML, JSON, workflow, script, test, component, header,
  or example file.
- Any compliance / safety claim about mains-voltage hardware. Those
  are tracked under COMPLIANCE-001
  ([`../compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md)).

## Definitions

| Term | Meaning |
|---|---|
| Hardware artifact | Any file produced by or about a physical board: schematic PDF, schematic source (`.kicad_sch` etc.), PCB source (`.kicad_pcb`), KiCad project metadata (`.kicad_pro`, `.kicad_prl`, `fp-lib-table`, `sym-lib-table`), BOM, CPL / pick-and-place CSV, gerbers, drill files, STEP model, board photo / render, vendor scratch export. |
| Raw upload | An archive (typically a ZIP) delivered by hardware engineering as-is, before any curation or review. May contain OS noise, history folders, embedded `.git`, vendor scratch, or private supplier data. |
| Curated artifact index | A per-board Markdown document under [`docs/hardware/artifacts/`](artifacts/) that inventories what artifacts exist for the board, where they came from, what is committed vs. excluded, and what remains open. Documentation only. |
| Committed | Tracked by `git` in the working tree of this repository. |
| Retained-but-not-committed | Acknowledged as useful and recorded in a curated artifact index, but **not** added to the `git` tree under this policy. Storage of these files is the [future storage decision](#future-storage-decision). |
| Excluded | Must never be committed under any current rule of this policy. |

## Artifact classes and commit status

The table below is the canonical rule set. Per-board artifact indexes
must classify every observed file against one of these rows.

| Class | Examples | Current commit status | Notes |
|---|---|---|---|
| Schematic PDF | `S360-100-R4.pdf` | **May be committed** under `docs/hardware/schematics/` after review (per HW-007). | The five Release-One-relevant boards already have their PDFs committed. New PDFs follow the same review path. |
| Per-board hardware reference doc | `docs/hardware/s360-100-r4-core.md` | **May be committed** under `docs/hardware/`. | Created only when an underlying schematic PDF is committed. Does not invent pins. |
| Per-board artifact index | `docs/hardware/artifacts/S360-100-R4.md` | **May be committed** under `docs/hardware/artifacts/`. | This document class. Docs only, no binaries. |
| KiCad schematic source | `*.kicad_sch` | **Retained-but-not-committed** in this PR. | Candidate for a future hardware-source storage decision. |
| KiCad PCB source | `*.kicad_pcb` | **Retained-but-not-committed** in this PR. | Same as above. |
| KiCad project metadata | `*.kicad_pro`, `*.kicad_prl`, `fp-lib-table`, `sym-lib-table` | **Retained-but-not-committed** in this PR. | Only meaningful when committed together with the KiCad source. |
| BOM | `*_BOM.xlsx`, `*_BOM.csv` | **Retained-but-not-committed** in this PR. | Procurement / manufacturing artifact. Candidate for a future manufacturing archive. |
| CPL / pick-and-place | `*-pos.csv` | **Retained-but-not-committed** in this PR. | Assembly artifact. Candidate for a future manufacturing archive. |
| Gerbers | `*-gerbers.zip`, raw `.gbr` / `.drl` / `.gbrjob` | **Retained-but-not-committed** in this PR. | Fabrication artifact. **Raw gerber `*.zip` dumps are not committed as opaque blobs**; per-board indexes may record their existence, naming, and checksum. |
| Drill files | `*-PTH.drl`, `*-NPTH.drl` | **Retained-but-not-committed** in this PR. | Shipped with the gerbers package. Same rule as gerbers. |
| STEP / mechanical | `*.step`, `*.stp` | **Retained-but-not-committed** in this PR. | Enclosure / mechanical artifact. Candidate for a future mechanical archive. |
| Board images / renders | `images/*.png`, `*.jpg` | **Not committed** in this PR. | Selected, compressed, reviewed images may be added by a later PR when there is a documentation use case. Unreviewed PNG dumps are not committed. |
| Mac OS metadata | `__MACOSX/`, `.DS_Store`, `Icon\r` files, AppleDouble resource forks | **Excluded.** Never commit. | Must not enter the tree under any circumstance. |
| Editor / IDE history | `.history/`, `*.bak`, `*.orig`, `*~`, `*.tmp`, KiCad backup folders (`*-backups/`), KiCad cache (`fp-info-cache`) | **Excluded.** Never commit. | Same as above. |
| Embedded `.git/` from a nested archive | `.git/`, `.gitignore` inside a vendor ZIP | **Excluded.** Never commit. | If a raw archive contains a nested `.git/`, do not extract it into this tree. |
| Vendor scratch exports | Random `.zip`, `.tar.gz`, `.7z` dumps with no curation | **Excluded.** Never commit. | The raw archive itself is excluded from `git`; only a curated index of its useful contents may be committed. |
| Private supplier / customer data | Quotes, NDAs, pricing, customer correspondence, supplier contacts | **Excluded.** Never commit. | Belongs in a private channel, not in this public repo. |

### No raw ZIP dumps

A **raw, unreviewed ZIP** (or `.tar.gz`, `.7z`, or equivalent) of a
hardware export must **not** be committed to this repository as a
single opaque blob. The supported pattern is:

1. The ZIP (or equivalent) is delivered to a curating PR's task
   environment, where its inventory is inspected.
2. Files inside the ZIP are classified against the table above.
3. A curated artifact index under
   [`docs/hardware/artifacts/`](artifacts/) records what exists, what
   is useful, what is excluded, and what remains open.
4. Files in the **may be committed** rows go to their canonical
   locations after review.
5. Files in the **retained-but-not-committed** rows are recorded in
   the index but not added to the `git` tree under this policy.
6. Files in the **excluded** rows never enter the tree.

The raw ZIP itself is not committed under any of these steps.

### No Git LFS in this PR

This policy intentionally does **not** introduce Git LFS, a binary
artifact store, or a release-asset convention for hardware artifacts.
Per-board indexes therefore must not assume any of those exist. They
must instead record retained-but-not-committed artifacts as
inventory-only entries with size and checksum.

### Future storage decision

The long-term home of retained-but-not-committed artifacts (KiCad
source, BOM, CPL, gerbers, drill files, STEP, curated images) is an
**open decision** at the time of this policy. Candidate options
include:

- A separate, possibly private, hardware-only repository.
- Git LFS within this repository (with all the cost / lock-in /
  CI implications that follow).
- GitHub Releases (per-board or per-revision asset bundles).
- A supplier / cloud archive linked from per-board indexes.

Per-board artifact indexes record each retained-but-not-committed
artifact's filename, size, and SHA256 so that whichever storage
decision is later taken can be verified against the inventory written
here.

## Curated per-board artifact indexes

The canonical location is
[`docs/hardware/artifacts/`](artifacts/). One Markdown file per board
revision, named `<SKU>-<REV>.md` (for example,
`S360-100-R4.md`). Each index must, at minimum:

- State its **purpose and scope**, the **artifact source** (which task
  / upload / archive it inventories), and a **policy reference** to
  this document.
- Mirror the **board identity** row from
  `config/hardware-catalog.json` without modifying it.
- List the **current committed evidence** for the board.
- Inventory the **uploaded archive** contents (filenames, sizes,
  notes about ZIP vs. loose files).
- Provide a **curated artifact table** classifying every observed
  file against the [artifact classes table](#artifact-classes-and-commit-status).
- List **excluded files** explicitly, even if none were present in
  the current upload — the exclusion list is policy, not just
  inventory.
- Record **checksums and file sizes** for every artifact actually
  present in the upload. Files **not** present in the upload must be
  marked `not provided in this upload`. **Do not fabricate
  checksums.** **Do not mark missing files `pending` unless they are
  genuinely expected to arrive later.**
- Document **relationships** to `config/hardware-catalog.json`,
  firmware package mapping (`firmware-package-mapping-audit.md`), and
  product / WebFlash availability.
- List **open questions / verification needed** and **follow-up
  PRs**.
- Carry a **do-not-change guardrails** section restating the
  policy-level "do not" list relevant to that PR.
- End with a **see also** section cross-linking this policy, the
  per-board hardware reference doc (if any), the remaining-board
  documentation audit, the firmware-package-mapping audit, the
  release-one hardware audit, and the cleanup audit.

## Hardware evidence ≠ firmware ≠ WebFlash

This is a load-bearing rule of this policy. State it explicitly in
every per-board index.

- A committed schematic PDF, a `verified` `schematic_status` in
  `config/hardware-catalog.json`, or a curated artifact index does
  **not** by itself make a board:
  - WebFlash-shippable,
  - eligible for the WebFlash build matrix
    (`config/webflash-builds.json`),
  - eligible for the WebFlash compatibility list
    (`config/webflash-compatibility.json`),
  - an entry in the WebFlash hardware-requirements text of any
    config string,
  - a `production`, `preview`, or `compile-only` entry in
    `config/product-catalog.json`,
  - the target of any product YAML under `products/**` or any
    WebFlash wrapper under `products/webflash/**`,
  - covered by any package YAML under `packages/**`.
- Conversely, the absence of a curated artifact index does not by
  itself demote a board's current Release-One / WebFlash status.
  Release-One status is owned by
  [`docs/release-one.md`](../release-one.md),
  [`docs/release-one-hardware-audit.md`](../release-one-hardware-audit.md),
  `config/product-catalog.json`, and `config/webflash-builds.json` —
  not by anything in
  [`docs/hardware/artifacts/`](artifacts/).
- Sense360 TRIAC / FanTRIAC stays `blocked` under HW-005. Sense360
  LED stays excluded from production Release-One because the
  WebFlash config string `Ceiling-POE-VentIQ-RoomIQ` does not carry
  an `LED` token. This policy does not change either status.

## Relationship to existing hardware docs

- [`docs/hardware-catalog.md`](../hardware-catalog.md) — canonical
  friendly-name / SKU / revision / `old_name` table. The artifact
  policy quotes this catalog; it does not modify it.
- [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  — machine-readable mirror. Per-board indexes mirror but do not
  modify rows.
- [`docs/hardware/s360-100-r4-core.md`](s360-100-r4-core.md),
  [`s360-200-r4-roomiq.md`](s360-200-r4-roomiq.md),
  [`s360-210-r4-airiq.md`](s360-210-r4-airiq.md),
  [`s360-211-r4-ventiq.md`](s360-211-r4-ventiq.md),
  [`s360-300-r4-led.md`](s360-300-r4-led.md) — schematic-backed
  per-board reference docs. Per-board indexes cross-link these; they
  do not replace them.
- [`docs/hardware/remaining-board-documentation-audit.md`](remaining-board-documentation-audit.md)
  — HW-004 / HW-006 audit. Per-board indexes do not alter its
  classifications.
- [`docs/hardware/firmware-package-mapping-audit.md`](firmware-package-mapping-audit.md)
  — HW-009 firmware-vs-schematic mapping audit. Per-board indexes
  may cite its reconciliation flags; they do not change them.
- [`docs/release-one-hardware-audit.md`](../release-one-hardware-audit.md)
  — Release-One firmware-vs-schematic audit, FanTRIAC HW-005
  resolution, LED policy. Untouched by this policy.
- [`docs/cleanup-audit.md`](../cleanup-audit.md) — gains a `current`
  finding row per new artifact-policy / artifact-index doc.

## What this policy explicitly does NOT do

- **No `config/hardware-catalog.json` edit.** No
  `schematic_status` change, no `schematic_file` change, no row
  added, no row removed.
- **No `config/product-catalog.json` edit.** No lifecycle status
  change. Release-One stays `production`; FanTRIAC stays `blocked`
  under HW-005; LED preview stays `preview` (or whatever it is at
  the time of any future per-board PR).
- **No `config/webflash-builds.json` edit.** No new build, no
  removed build, no version / channel / artifact change.
- **No `config/webflash-compatibility.json` edit.** No taxonomy
  change.
- **No `products/**` edit.** No product YAML created, modified, or
  deleted. No WebFlash wrapper under `products/webflash/**` created,
  modified, or deleted.
- **No `packages/**` edit.** No package YAML created or modified.
- **No `scripts/**`, `tests/**`, `.github/workflows/**`,
  `components/**`, `include/**`, or `.gitignore` edit.**
- **No firmware regeneration.** No `.bin` artifact created or
  modified.
- **No release created.** No GitHub Release, no tag, no asset push.
- **No FanTRIAC unblock.** HW-005 stays a separate gate.
- **No LED Release-One promotion.** The Release-One WebFlash config
  string remains `Ceiling-POE-VentIQ-RoomIQ` with no `LED` token.
- **No Git LFS adoption.** No `.gitattributes` change. No binary
  storage backend introduced.
- **No raw ZIP committed.** Hardware-export ZIPs are inspected in
  task environments, never added to the `git` tree.

## Validation

This policy doc is text-only and adds no test. The repo-wide
docs-safe validation that every artifact-policy / artifact-index PR
must still pass is:

```text
python3 tests/test_hardware_catalog.py
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

Sanity grep:

```text
grep -RIn "HW-ASSETS-001\|hardware-artifact-policy\|raw ZIP\|__MACOSX\|.DS_Store\|.history" docs config packages products
```

Expected: the policy doc is discoverable; per-board indexes that
follow the policy resolve through their `See also` blocks; no JSON,
YAML, workflow, script, test, component, or header is changed by
the policy or by an artifact-index PR that follows it.

## Follow-up PRs

| PR | Purpose | Gated on |
|---|---|---|
| **HW-ASSETS-002** | Curated S360-100-R4 (Sense360 Core) artifact index. | Lands together with this policy (Option C). |
| **HW-ASSETS-003** | Curated S360-200-R4 (Sense360 RoomIQ) artifact index. | Expected only if an artifact source (ZIP / loose files) is provided for S360-200-R4. |
| **HW-ASSETS-004** | Curated S360-210-R4 (Sense360 AirIQ) artifact index. | Expected only if an artifact source is provided for S360-210-R4. |
| **HW-ASSETS-005** | Curated S360-211-R4 (Sense360 VentIQ) artifact index. | Expected only if an artifact source is provided for S360-211-R4. |
| **HW-ASSETS-006** | Curated S360-300-R4 (Sense360 LED) artifact index. | Expected only if an artifact source is provided for S360-300-R4. |
| **HW-GAP-001** | Board readiness matrix across all S360 modules (per-board, evidence vs. shippability). | Independent of artifact ingest cadence. |
| **S360-100-BENCH-001** | Core board bench / manufacturing evidence pass. | Independent of artifact ingest cadence. |

A future, separate PR is required before any retained-but-not-committed
artifact class graduates to **may be committed**. That PR must
choose a storage backend, justify the trade-off against this policy,
and update the [Artifact classes table](#artifact-classes-and-commit-status).

## See also

- [Sense360 Hardware Catalog](../hardware-catalog.md) — canonical
  board / module names, SKUs, revisions, and legacy names.
- [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  — machine-readable mirror; `schematic_status` per row.
- [S360-100-R4 Core Hardware Reference](s360-100-r4-core.md) —
  schematic-backed Core pin / connector reference.
- [S360-100-R4 Hardware Artifact Index](artifacts/S360-100-R4.md) —
  curated per-board artifact index for the Core board (HW-ASSETS-002,
  the first board to apply this policy).
- [Remaining Board Documentation Audit](remaining-board-documentation-audit.md)
  — HW-004 / HW-006 / HW-007 / HW-008 per-board documentation-state
  classification.
- [Firmware Package Mapping Audit](firmware-package-mapping-audit.md)
  — HW-009 firmware-vs-schematic mapping audit; the reconciliation
  flags cited by per-board indexes.
- [Release-One Hardware Audit](../release-one-hardware-audit.md) —
  HW-005 FanTRIAC blocker, Sense360 LED policy, Release-One source of
  truth.
- [Release-One Configuration](../release-one.md) — the
  `Ceiling-POE-VentIQ-RoomIQ` shipping configuration.
- [Cleanup Audit](../cleanup-audit.md) — companion classification of
  stale / current / blocked-reference / legacy-compatible repo
  content.
- [Mains-voltage Safety and Compliance Assessment — UK / EU (COMPLIANCE-001)](../compliance/mains-voltage-uk-eu-assessment.md)
  — separate compliance tracker for `S360-400` and `S360-320`; not
  cleared by this policy.

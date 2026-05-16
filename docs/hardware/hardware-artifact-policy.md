# Hardware Source and Manufacturing Artifact Policy (HW-ASSETS-001)

## Purpose and scope

This document is the canonical policy for **hardware source and
manufacturing artifacts** — schematic PDFs, KiCad schematic / PCB
source, BOM spreadsheets, CPL / pick-and-place files, Gerbers, STEP
models, board images, vendor / fab export ZIPs, and the assorted
operating-system, IDE, and version-control noise that ships inside
those exports — in this repository. It defines:

- which artifact classes may be committed directly,
- which artifact classes must not be committed,
- where curated hardware artifacts live in the repo,
- how raw vendor / manufacturing ZIPs are handled,
- how each finished or evidenced board is indexed,
- and how hardware artifact availability relates to firmware
  packaging, product catalog status, and WebFlash availability.

This policy applies to every Sense360 board / module SKU listed in
[`config/hardware-catalog.json`](../../config/hardware-catalog.json)
and to every future board / module added to the catalog.

This document is **documentation only**. It does not:

- add, remove, or modify any hardware source / manufacturing
  artifact (no KiCad source, no BOM spreadsheet, no CPL, no
  Gerbers ZIP, no STEP model, no vendor export, no board image),
- add, remove, or modify any entry in
  [`config/hardware-catalog.json`](../../config/hardware-catalog.json),
  [`config/product-catalog.json`](../../config/product-catalog.json),
  [`config/webflash-builds.json`](../../config/webflash-builds.json),
  or
  [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json),
- add, remove, or modify any product YAML, WebFlash wrapper, or
  package YAML,
- add, remove, or modify any workflow under `.github/workflows/`,
  any script under `scripts/`, any test under `tests/`, any
  component under `components/`, or any include under `include/`,
- change `.gitignore`, `.gitattributes`, or any pre-commit
  configuration (any actual exclusion-rule additions are deferred
  to the first PR that introduces a curated artifact tree —
  HW-ASSETS-002),
- promote any module from `cataloged-unverified` /
  `partially-documented` / `blocked` to `preview` / `stable` /
  `production`,
- change the Release-One shipping configuration
  `Ceiling-POE-VentIQ-RoomIQ` or its artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`,
- change the FanTRIAC HW-005 blocked status,
- change the Sense360 LED preview / Release-One exclusion status,
- introduce Git LFS to this repository (Git LFS is listed below
  as a *future decision option* for large binary artifacts; this
  PR does not enable it),
- create any board artifact index — including the S360-100-R4
  index, which is the scope of HW-ASSETS-002.

If this document and any source-of-truth document drift, **the
source-of-truth document wins** and this document must be updated.
The sources of truth are listed in [See also](#see-also).

## Artifact classes

This policy recognises the following artifact classes. Storage and
commit rules per class are defined in
[Storage locations](#storage-locations), [What may be
committed](#what-may-be-committed), and [What must not be
committed](#what-must-not-be-committed).

| Class | Examples | Typical origin | Default commit treatment |
|---|---|---|---|
| **Schematic PDF** | `S360-100-R4.pdf` | Exported from KiCad | Commit directly when curated |
| **KiCad project** | `*.kicad_pro` | KiCad source tree | Decide per-board; usually commit if small and reviewed |
| **KiCad schematic source** | `*.kicad_sch`, `Sense360_Core_R4.kicad_sch` | KiCad source tree | Decide per-board; usually commit if small and reviewed |
| **KiCad PCB layout source** | `*.kicad_pcb` | KiCad source tree | Decide per-board; size-sensitive |
| **BOM spreadsheet** | `BOM.xlsx`, `BOM.csv` | KiCad BOM export / vendor | Commit `.csv` when small; treat `.xlsx` per [What may be committed](#what-may-be-committed) |
| **CPL / pick-and-place** | `CPL.csv`, `pick-and-place.csv` | Fab export | Commit `.csv` when small |
| **Gerbers** | `gerbers.zip`, `*.gbr`, `*.gtl` | KiCad fab export / fab house | Either curated commit or attach to GitHub Release |
| **Drill files** | `*.drl`, `*.xln` | KiCad fab export | Same treatment as Gerbers |
| **STEP / 3D model** | `*.step`, `*.stp` | KiCad 3D export / CAD | Size-sensitive; consider GitHub Release or external |
| **Board images / renders** | `top.png`, `bottom.png`, `render.jpg` | Photographs / KiCad renders | Commit when small and curated |
| **Raw vendor ZIP** | `S360-100-R4.zip` (vendor export) | Fab house / supplier hand-off | **Do not commit directly** — extract, curate, then commit selectively |
| **Mac / IDE / SCM noise** | `__MACOSX/`, `.DS_Store`, `Icon\r`, `.history/`, embedded `.git/`, KiCad `-backup`, `*.kicad_pcb-bak` | OS / editor / SCM byproducts inside vendor exports | **Never commit** |
| **Markdown reference doc** | `s360-100-r4-core.md`, `s360-100-r4.md` (future artifact index) | Hand-authored | Commit directly |

The boundary between "small and reviewed" and "size-sensitive" is
intentionally not fixed in this document. The artifact index for
each board (see [Board artifact index
requirement](#board-artifact-index-requirement)) records the per-file
decision and the reason.

## Storage locations

| Artifact | Canonical location in this repo |
|---|---|
| Schematic PDF | [`docs/hardware/schematics/`](schematics/) |
| Standalone per-board hardware reference doc | [`docs/hardware/<sku>-<rev>-<role>.md`](.) — e.g. `s360-100-r4-core.md` |
| Per-board artifact index doc | `docs/hardware/artifacts/<SKU>-<REV>.md` — e.g. `docs/hardware/artifacts/S360-100-R4.md` (directory created by HW-ASSETS-002) |
| Hardware-catalog source of truth (machine-readable) | [`config/hardware-catalog.json`](../../config/hardware-catalog.json) |
| Hardware-catalog narrative source of truth | [`docs/hardware-catalog.md`](../hardware-catalog.md) |
| Per-board curated hardware source (when committed): KiCad project / schematic / PCB | `docs/hardware/sources/<SKU>-<REV>/` (directory deferred — created by HW-ASSETS-002 only if the per-board decision is to commit directly) |
| Per-board curated manufacturing files (when committed): BOM, CPL, Gerbers ZIP, drill, STEP | `docs/hardware/manufacturing/<SKU>-<REV>/` (directory deferred — same rule) |
| Per-board curated board images | `docs/hardware/images/<SKU>-<REV>/` (directory deferred — same rule) |
| Raw uncurated vendor ZIP | **Not in this repo.** Held outside the repository tree (operator workstation, secure file store, or a dedicated hardware repo). Indexed in the per-board artifact index by checksum and external path. |
| Large / generated / binary artefacts whose per-board decision is "do not commit directly" | Decision options listed in [Manufacturing evidence handling](#manufacturing-evidence-handling). |

The five currently-committed schematic PDFs under
[`docs/hardware/schematics/`](schematics/) (`S360-100-R4.pdf`,
`S360-200-R4.pdf`, `S360-210-R4.pdf`, `S360-211-R4.pdf`,
`S360-300-R4.pdf`) are the *de facto* current practice for the
"Schematic PDF" class; this policy codifies that practice and
extends it to the other artifact classes.

## What may be committed

Subject to the per-board decision recorded in the board artifact
index, the following may be committed directly:

- **Schematic PDFs**, when curated (single combined PDF per board
  revision; sourced from the authoritative KiCad export; not the
  raw vendor ZIP). Already committed for the five finished
  boards.
- **Per-board Markdown reference docs** (e.g.
  [`docs/hardware/s360-100-r4-core.md`](s360-100-r4-core.md)).
- **Per-board Markdown artifact index docs** under
  `docs/hardware/artifacts/` (see [Board artifact index
  requirement](#board-artifact-index-requirement)).
- **Small text / CSV manufacturing metadata** when it is useful for
  human review — typically a curated BOM `.csv` and a curated CPL
  `.csv`. "Small" means single-digit MB; larger or binary forms
  follow [Manufacturing evidence
  handling](#manufacturing-evidence-handling).
- **Small board images / renders** used inline in docs (PNG / JPG /
  WebP). Prefer pre-compressed / resized assets; do not commit
  full-resolution camera originals.

The following classes are **potentially allowed** to be committed
directly, but only when the per-board decision in the board artifact
index explicitly says yes and the file is small enough for code
review:

- **KiCad project file** (`*.kicad_pro`).
- **KiCad schematic source** (`*.kicad_sch`).
- **KiCad PCB layout source** (`*.kicad_pcb`).
- **BOM spreadsheet** (`*.xlsx`) — prefer `.csv` over `.xlsx`
  whenever both are available.
- **CPL / pick-and-place CSV** (`*.csv`).
- **Gerbers ZIP** (`gerbers.zip` or fab-named equivalent).
- **STEP / 3D model** (`*.step`, `*.stp`).

Where any of these are not committed directly, record the chosen
alternative (Git LFS / GitHub Release / external) and the access
location in the board artifact index. The default per this policy is
**do not commit large binary or generated artifacts directly**; an
explicit "yes" must be recorded.

## What must not be committed

The following must never appear under `docs/hardware/`,
`packages/`, `products/`, `components/`, `include/`, `config/`,
`scripts/`, `tests/`, `.github/`, or anywhere else in this
repository, regardless of which artifact bundle they arrived in:

- **Raw, unreviewed vendor / fab / supplier ZIP dumps** (e.g. the
  bare `S360-100-R4.zip` that triggered this policy). See [Raw ZIP
  policy](#raw-zip-policy).
- **macOS Finder metadata** — `__MACOSX/`, `.DS_Store`,
  `.AppleDouble/`, `.AppleDB/`, `._*` resource forks, `Icon\r`
  (Icon files with a trailing carriage return).
- **Spotlight / Trash sidecars** — `.Spotlight-V100/`,
  `.Trashes/`.
- **KiCad editor noise** — `-backup/` directories, `*.kicad_pcb-bak`,
  `*.kicad_sch-bak`, `*-backup.kicad_*`, `*.000`, `*.001` numeric
  backups, autosave / lock files.
- **Editor / IDE noise** — `.history/`, `.vscode/`, `.idea/`,
  `*.swp`, `*.swo`, `*~`, `*.orig`, `*.bak`, `*.old`, `*.tmp`.
- **Embedded version-control trees** that arrived inside a vendor
  ZIP — `.git/`, `.gitmodules`, `.hg/`, `.svn/`.
- **Windows / Office sidecars** — `Thumbs.db`, `ehthumbs.db`,
  `desktop.ini`, `~$*.xlsx`, `~$*.docx`.
- **Vendor export scratch / temporary files** — anything obviously
  named `*temp*`, `*tmp*`, `*scratch*`, or sitting in a `Trash` /
  `_old` subtree.
- **Private supplier quotes**, RFQ correspondence, NDA-covered
  vendor information, costed BOMs containing supplier pricing,
  customer / installer private data.
- **Credentials, API keys, signing keys**, private certificates,
  WiFi / installer passwords, or any other secret. The
  repository-wide `.gitignore` already covers `secrets.yaml`,
  `*.secret`, `*.key`, `*.pem`, `*.crt`; this policy reinforces
  that these must not be added to a hardware artifact tree even
  if they arrived inside the vendor ZIP.

`.gitignore` is **not** modified by this PR. Actual exclusion-rule
additions to `.gitignore` are deferred to HW-ASSETS-002, which is
the first PR that will land a curated artifact tree and therefore
the first PR where Git can be asked to enforce these exclusions.
Until then, the policy is enforced by reviewer attention.

## Raw ZIP policy

Raw vendor / fab / supplier ZIPs (e.g. `S360-100-R4.zip` as
delivered by a fab house) must **not** be committed to this
repository as-is. The reasons are:

1. They carry the OS, IDE, and version-control noise enumerated in
   [What must not be committed](#what-must-not-be-committed).
2. They typically include large binary or generated artefacts
   (Gerbers, drill files, STEP, KiCad source) whose commit-vs-
   external decision is per-board and per-file and cannot be made
   by bulk extraction.
3. They obscure provenance: a single opaque ZIP is not reviewable
   in `git diff`, and a future reader cannot tell which file came
   from which supplier, which revision, or which export run.
4. They cannot be cleanly de-noised by `.gitignore` once committed
   — `git` tracks the file inside the archive, not its expansion.

The required workflow when a raw vendor ZIP is received is:

1. **Extract outside the repository** (operator workstation or
   secure scratch directory). Do not extract inside the
   repository working tree.
2. **Compute a SHA-256 checksum of the original ZIP**, and record
   it in the per-board artifact index (`checksums` field; see
   [Required index fields](#required-index-fields)).
3. **Inventory the expansion** against the artifact classes in
   [Artifact classes](#artifact-classes). Identify each file's
   class and either:
   - select it for curated commit (per the per-board decision
     recorded in the artifact index), or
   - select it as "external only" (recorded in the artifact
     index with checksum and external path), or
   - mark it as noise to exclude (recorded in the artifact
     index `excluded_files` field).
4. **Curate the selected commits** — rename to the canonical
   layout (`docs/hardware/manufacturing/<SKU>-<REV>/...`, etc.),
   strip any embedded credentials / supplier quotes / private
   data, and remove any of the noise classes from [What must not
   be committed](#what-must-not-be-committed).
5. **Commit through the normal review process**, with the artifact
   index as the human-readable map of what came from where.

The raw ZIP itself is retained externally (operator workstation,
secure file store, or a dedicated hardware repo). It is referenced
in the artifact index by checksum and external path; it is not
referenced by a relative path inside this repository.

This workflow is documentation only in HW-ASSETS-001. The first PR
to actually execute it for `S360-100-R4` is HW-ASSETS-002.

## Board artifact index requirement

Each finished or hardware-evidenced board must eventually have a
single per-board artifact index document at:

```
docs/hardware/artifacts/<SKU>-<REV>.md
```

For example: `docs/hardware/artifacts/S360-100-R4.md`.

The artifact index is the human-readable answer to:

- which hardware artifacts exist for this board revision,
- where each one lives (committed path, GitHub Release URL, Git
  LFS pointer, or external path),
- which artifacts were intentionally excluded (and why),
- which artifacts are still missing,
- and what the relationship is to the pin map, package YAML,
  product YAML, and WebFlash status.

The `docs/hardware/artifacts/` directory does **not** exist yet.
It is created by HW-ASSETS-002 (which lands the first index, for
`S360-100-R4`). This PR (HW-ASSETS-001) only defines the
requirement and the field schema.

The artifact index does not replace:

- the per-board standalone hardware reference doc
  ([`s360-100-r4-core.md`](s360-100-r4-core.md) and siblings),
  which is the pin / connector / net reference,
- the firmware-package-mapping audit
  ([`firmware-package-mapping-audit.md`](firmware-package-mapping-audit.md)),
  which is the reconciliation between schematics and package YAML,
- the remaining-board documentation audit
  ([`remaining-board-documentation-audit.md`](remaining-board-documentation-audit.md)),
  which is the cross-board documentation-state matrix.

The artifact index complements those documents by recording the
manufacturing-evidence side specifically.

## Required index fields

Every per-board artifact index doc must carry the following fields.
Fields whose answer is "not available" or "not yet decided" must be
explicit; an empty field is not equivalent to "no artifact
exists".

| Field | Meaning |
|---|---|
| `board_sku` | Catalog SKU, e.g. `S360-100`. Must match an entry in [`config/hardware-catalog.json`](../../config/hardware-catalog.json). |
| `revision` | Board revision, e.g. `R4`. Must match the catalog `rev` field for this SKU. |
| `artifact_source` | Origin of the artifact bundle (fab house name, supplier name, internal export run identifier). |
| `artifact_date` | Date the artifact bundle was received / exported, ISO-8601 (`YYYY-MM-DD`). |
| `schematic_pdf` | Path inside the repo, or external reference. For the five finished boards today this is `docs/hardware/schematics/<SKU>-<REV>.pdf`. |
| `kicad_project` | Path or external reference for the KiCad project (`*.kicad_pro`). Record `not committed — external only` plus external path when the per-board decision is not to commit. |
| `kicad_schematic` | Path or external reference for the KiCad schematic source (`*.kicad_sch`). |
| `kicad_pcb` | Path or external reference for the KiCad PCB layout source (`*.kicad_pcb`). |
| `bom` | Path or external reference for the curated BOM. Prefer `.csv` over `.xlsx` when both exist. |
| `cpl` | Path or external reference for the curated CPL / pick-and-place file. |
| `gerbers` | Path or external reference for the curated Gerbers (ZIP or directory). |
| `drill_files` | Path or external reference for the curated drill files. |
| `step_file` | Path or external reference for the curated STEP model. |
| `images` | List of paths or external references for committed board images / renders. |
| `excluded_files` | List of files that were present in the source bundle but intentionally not committed, with one-line reason per file (`Mac metadata`, `IDE noise`, `KiCad backup`, `embedded .git/`, `private supplier quote`, etc.). |
| `checksums` | SHA-256 checksums for the original source bundle and for each large external-only artifact. Allows future reviewers to confirm the external file matches the index. |
| `known_open_questions` | Free-form list of hardware open questions for this revision. Mirrors / cross-links to the corresponding standalone hardware reference doc's "Open questions" section. |
| `pin_map_status` | One of: `documented`, `partially-documented`, `cataloged-unverified`, `blocked`, `not-yet-attempted`. Mirrors the classification in [`remaining-board-documentation-audit.md`](remaining-board-documentation-audit.md). |
| `package_yaml_status` | One of: `confirmed-ok`, `needs-package-change`, `needs-doc-fix`, `needs-silkscreen/bench-verification`, `blocked`, `unknown`, `none-yet`. Mirrors the classification taxonomy in [`firmware-package-mapping-audit.md`](firmware-package-mapping-audit.md). |
| `product_yaml_status` | One of: `production`, `preview`, `compile-only`, `hardware-pending`, `blocked`, `legacy-compatible`, `deprecated`, `removed`, `none-yet`. Mirrors the lifecycle statuses in [`config/product-catalog.json`](../../config/product-catalog.json). |
| `webflash_status` | One of: `shippable-stable`, `shippable-preview`, `not-shippable`, `not-applicable`. Records the WebFlash availability of any product that consumes this board; does not promote the board itself. |
| `reviewer_notes` | Free-form reviewer commentary, including the rationale for any "not committed — external only" or "intentionally excluded" decision. |

The artifact index is a Markdown document; the fields above are
the *schema*, but the rendering is conventional Markdown (front-
matter, table, or sectioned headings — chosen by HW-ASSETS-002 and
followed by subsequent indices). No machine-readable schema is
introduced by this PR.

## Relationship to hardware-catalog.json

[`config/hardware-catalog.json`](../../config/hardware-catalog.json)
remains the **machine-readable source of truth** for board / module
SKU, revision, friendly name, legacy name, schematic status, and
the canonical schematic-file pointer. This policy does not change
that contract.

The relationship is:

- The artifact index `board_sku` and `revision` fields must match
  the corresponding `sku` and `rev` in the JSON catalog. The JSON
  wins on drift.
- The artifact index `schematic_pdf` field, when committed,
  should equal the JSON `schematic_file` for that SKU. The JSON
  wins on drift.
- The artifact index `pin_map_status` mirrors but does **not**
  drive the JSON `schematic_status` value. The JSON
  `schematic_status` is still owned by HW-007 (PDF commit) and
  HW-008 (JSON refresh) on the schematic side, and the artifact
  index is a parallel human-readable record on the
  manufacturing-evidence side. Hardware-catalog status flips are
  not in scope for HW-ASSETS-001 or HW-ASSETS-002.
- The artifact index does not introduce any new JSON fields. If
  future work needs machine-readable manufacturing-evidence
  status, that is a separate PR and a separate schema decision.

## Relationship to product availability

The single most important rule in this document is:

> **Hardware artifact availability does not equal firmware support
> or WebFlash availability.**

A board can be hardware-evidenced (schematic PDF committed, KiCad
source reviewed, BOM and CPL curated, Gerbers archived) without
being WebFlash-shippable. A WebFlash-shippable product additionally
requires every gate already defined elsewhere in this repository:

- a product YAML under [`products/`](../../products/) that
  compiles cleanly,
- a WebFlash wrapper YAML under
  [`products/webflash/`](../../products/webflash/) when the
  product is intended for the customer-facing flasher,
- a catalog entry in
  [`config/product-catalog.json`](../../config/product-catalog.json)
  with a WebFlash-eligible lifecycle status,
- a build-matrix entry in
  [`config/webflash-builds.json`](../../config/webflash-builds.json),
- a published GitHub Release `.bin` and a recorded build / release
  proof per
  [`docs/webflash-release-proof.md`](../webflash-release-proof.md),
- a manifest entry imported into WebFlash and a deployed
  `manifest.json` / `firmware-N.json`,
- and, for stable promotion, the full RELEASE-006 gate list per
  [`docs/preview-to-stable-promotion-gates.md`](../preview-to-stable-promotion-gates.md),
  including operator flash proof and hardware bench verification.

Committing a curated artifact bundle for a board does not
substitute for any of the above. In particular:

- It does **not** add the board to any product YAML.
- It does **not** unblock FanTRIAC (HW-005 remains the canonical
  blocker for `S360-320`).
- It does **not** promote Sense360 LED into the Release-One config
  string `Ceiling-POE-VentIQ-RoomIQ`.
- It does **not** change any module's `cataloged_unverified` /
  `verified` status in the hardware catalog JSON.
- It does **not** add or remove anything from WebFlash-side
  `REQUIRED_CONFIGS`, `kits.json`, `firmware/sources.json`, or
  `manifest.json`.

The artifact index distinguishes hardware-evidenced from
WebFlash-ready by carrying both `pin_map_status` and
`webflash_status` as separate fields, with `webflash_status`
sourced from the product catalog rather than from the artifact
bundle.

## Relationship to pin maps / package YAML / product YAML

The recommended ordering for any new board going through this
repository is:

1. **Artifact bundle reviewed and curated.** Per-board artifact
   index doc exists under `docs/hardware/artifacts/` with at
   minimum `schematic_pdf` populated (committed PDF) and the
   noise / private data excluded.
2. **Standalone hardware reference doc exists**
   (`docs/hardware/<sku>-<rev>-<role>.md`) carrying the pin /
   connector / net / rail tables sourced from the schematic. This
   is the input to the pin map.
3. **Hardware-catalog JSON entry** carries `schematic_status:
   verified` and a `schematic_file` pointing at the committed
   PDF. (This step is owned by the HW-007 / HW-008 PR family for
   each board; it is not driven by the artifact index.)
4. **Pin map / package YAML decision** can now be made on
   evidence rather than guess. The firmware-package-mapping audit
   ([`firmware-package-mapping-audit.md`](firmware-package-mapping-audit.md))
   is the canonical reconciliation between the schematic and the
   package YAML.
5. **Package YAML** is added or reconciled under [`packages/`](../../packages/).
6. **Product YAML** is added under [`products/`](../../products/)
   (and a WebFlash wrapper under
   [`products/webflash/`](../../products/webflash/) when
   applicable). Catalog entry, build matrix, release artefact,
   and WebFlash import follow per
   [`docs/product-onboarding.md`](../product-onboarding.md) and
   [`docs/preview-to-stable-promotion-gates.md`](../preview-to-stable-promotion-gates.md).

Steps 5 and 6 are gated on steps 1–4. Doing 5 or 6 without 1–4
re-introduces the "package guessed against an absent schematic"
risk that HW-005 (FanTRIAC `GPIO5` / `GPIO6` placeholder) is the
running example of.

This policy is the ordering rule. It does not by itself execute
any step beyond step 1, and even step 1 is deferred to
HW-ASSETS-002 for `S360-100-R4`.

## Manufacturing evidence handling

For artifacts whose per-board decision is **not** "commit
directly", the artifact index must record the chosen alternative
and the access location. Permitted alternatives are:

| Option | When to use | What the artifact index records |
|---|---|---|
| **Commit directly** | Small, reviewable, useful in `git diff`, no private data | Repository path under `docs/hardware/manufacturing/<SKU>-<REV>/` (or the equivalent directory per [Storage locations](#storage-locations)). |
| **Git LFS** | Large binary or generated artefact (Gerbers, STEP, full-resolution images) that still needs to ship with the repo | Repository path plus the note that the file is an LFS pointer. **Git LFS is not currently in use in this repository**; this option must not be exercised before a separate PR enables LFS. This policy lists it as a future decision option only. |
| **GitHub Release attachment** | Snapshot of fab output associated with a tagged release | GitHub Release URL plus tag. The release artefact must have a SHA-256 checksum recorded in the artifact index `checksums` field. |
| **Dedicated hardware repository** | Full vendor / fab export trees that are too large or too noisy for this repo | Repository name and path. The artifact index records the repository URL, the commit hash referenced, and the SHA-256 checksum where applicable. |
| **External-only with checksum** | Vendor ZIP held on operator workstation or secure file store; not in any repository | External path (descriptive, not a link) plus SHA-256 checksum. The artifact is recoverable from supplier records if lost. |

The default for any large binary or generated artefact is **either
GitHub Release or external-only with checksum**. Direct commit and
Git LFS each require an explicit per-board decision recorded in the
artifact index.

For every external-only artefact, the artifact index must carry
enough information for a future reviewer to confirm the external
file matches what the index describes — at minimum the SHA-256
checksum and the artefact source (fab house, supplier, internal
export run).

## Versioning and revision naming

Hardware artifact bundles are tied to a board revision, not to a
firmware release. The naming convention is:

- Each artifact bundle is keyed by `<SKU>-<REV>`, e.g.
  `S360-100-R4`. The `<REV>` segment must match the `rev` field
  in [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  for the corresponding SKU.
- A new board revision (e.g. a hypothetical future `S360-100-R5`)
  is a new artifact bundle with its own artifact index doc; it
  does **not** overwrite the previous revision's index. Both
  index docs coexist under `docs/hardware/artifacts/`.
- The standalone hardware reference doc filename uses lowercase
  with hyphens (`s360-100-r4-core.md`); the artifact index doc
  filename uses the catalog form
  (`docs/hardware/artifacts/S360-100-R4.md`). This mirrors the
  existing schematic PDF filename convention.
- Patch-level changes to an existing bundle (e.g. fab supplied a
  corrected CPL) are recorded inside the existing artifact index
  with an updated `artifact_date` and `checksums` row; the file
  paths and `<REV>` do not change.

This policy does not retire or rename any existing hardware doc.
The existing per-board reference docs ([`s360-100-r4-core.md`](s360-100-r4-core.md)
and siblings) continue to exist and to own the pin / connector /
net tables; the artifact index is a separate, complementary
document.

## Finished board inventory

The following boards are currently hardware-evidenced. All five
carry a committed schematic PDF under
[`docs/hardware/schematics/`](schematics/) and a `verified`
`schematic_status` in
[`config/hardware-catalog.json`](../../config/hardware-catalog.json):

| SKU | Revision | Friendly name | Schematic PDF | Standalone reference doc |
|---|---|---|---|---|
| `S360-100` | R4 | Sense360 Core | [`schematics/S360-100-R4.pdf`](schematics/S360-100-R4.pdf) | [`s360-100-r4-core.md`](s360-100-r4-core.md) |
| `S360-200` | R4 | Sense360 RoomIQ | [`schematics/S360-200-R4.pdf`](schematics/S360-200-R4.pdf) | [`s360-200-r4-roomiq.md`](s360-200-r4-roomiq.md) |
| `S360-210` | R4 | Sense360 AirIQ | [`schematics/S360-210-R4.pdf`](schematics/S360-210-R4.pdf) | [`s360-210-r4-airiq.md`](s360-210-r4-airiq.md) |
| `S360-211` | R4 | Sense360 VentIQ | [`schematics/S360-211-R4.pdf`](schematics/S360-211-R4.pdf) | [`s360-211-r4-ventiq.md`](s360-211-r4-ventiq.md) |
| `S360-300` | R4 | Sense360 LED | [`schematics/S360-300-R4.pdf`](schematics/S360-300-R4.pdf) | [`s360-300-r4-led.md`](s360-300-r4-led.md) |

These boards may be indexed as **hardware-evidenced** under the
artifact-index workflow once HW-ASSETS-002 (and its
per-board follow-ups) lands. **Hardware evidence alone does not
imply WebFlash availability** — see [Relationship to product
availability](#relationship-to-product-availability). In particular:

- `S360-100` (Sense360 Core) is consumed by the Release-One
  product `Ceiling-POE-VentIQ-RoomIQ`, which is WebFlash-shippable
  on `channel: stable`.
- `S360-200` (Sense360 RoomIQ), `S360-211` (Sense360 VentIQ), and
  the PoE PSU (`S360-410`, not on this list — see below) are
  consumed by the same Release-One product.
- `S360-210` (Sense360 AirIQ) is hardware-evidenced but is
  mutually exclusive with VentIQ and is not in Release-One.
- `S360-300` (Sense360 LED) is hardware-evidenced and is consumed
  by the LED-bearing preview product
  `Ceiling-POE-VentIQ-RoomIQ-LED` (`status: preview`); the WebFlash
  preview import is still outstanding and stable promotion is
  gated by RELEASE-006.

## Missing / design-pending board inventory

The following boards are listed in
[`config/hardware-catalog.json`](../../config/hardware-catalog.json)
with `schematic_status: cataloged_unverified`. They do not yet
have a committed schematic PDF, a standalone hardware reference
doc, or any other curated hardware evidence in this repository:

| SKU | Revision | Friendly name | Role |
|---|---|---|---|
| `S360-310` | R4 | Sense360 Relay | On/off relay for bathroom fans |
| `S360-311` | R4 | Sense360 PWM | 12V PWM fan driver (up to 4 fans with tach feedback) |
| `S360-312` | R4 | Sense360 DAC | 0–10V analog fan driver |
| `S360-320` | R4 | Sense360 TRIAC | Phase dimmer for mains fan or lamp — blocked under **HW-005**; additionally gated by COMPLIANCE-001 |
| `S360-400` | R4 | Sense360 240v PSU | Mains-to-5V — gated by COMPLIANCE-001 |
| `S360-410` | R4 | Sense360 PoE PSU | PoE-to-5V |

Before any of these boards is consumed by a new package YAML, a
new product YAML, a new catalog entry, a new build-matrix entry,
or a new WebFlash build, this repository requires — at minimum —
the evidence listed in the per-board pin-map follow-up PRs
(`HW-PINMAP-310` / `-311` / `-312` / `-320` / `HW-PINMAP-400` /
`-410`; see [Follow-up PR sequence](#follow-up-pr-sequence)):

- a committed schematic PDF under
  [`docs/hardware/schematics/`](schematics/) (HW-007-equivalent
  ingest),
- a pin / net map sourced from that schematic (standalone
  hardware reference doc, HW-007-equivalent standalone doc),
- a connector / rail evidence record (Core-side mating table when
  the board plugs into `S360-100`),
- an explicit package YAML decision (add, reconcile, or defer),
- an explicit product YAML decision (add, defer, or "no product
  consumes this board yet"),
- and an explicit build / WebFlash decision (compile-only,
  preview, or "not on the WebFlash track").

`S360-320` (FanTRIAC) additionally requires the HW-005 blocker to
be resolved and the COMPLIANCE-001 mains-voltage gate to be
satisfied before any product-side work. `S360-320` and `S360-400`
are both in scope for
[`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md).

This policy does not unblock, promote, or reclassify any of these
boards. The follow-up PR sequence below is documentation of the
recommended ordering; each entry is its own PR and its own review.

## Follow-up PR sequence

The recommended sequence after HW-ASSETS-001 lands is:

1. **HW-ASSETS-002 — Add curated S360-100-R4 hardware artifact
   index.** Creates `docs/hardware/artifacts/` and lands the first
   per-board artifact index doc for `S360-100-R4`. Adds the
   first concrete `.gitignore` exclusion-rule additions for the
   noise classes enumerated in [What must not be
   committed](#what-must-not-be-committed). Curates whichever
   subset of the `S360-100-R4.zip` contents are selected for
   commit per the per-board decision; the remainder are recorded
   as `external-only with checksum` or `excluded_files`.
2. **HW-GAP-001 — Board readiness matrix for S360 modules.**
   Cross-board matrix recording, for every SKU in the hardware
   catalog, the current state of artifact index, standalone
   hardware reference doc, hardware-catalog JSON status, package
   YAML, product YAML, and WebFlash availability. Documentation
   only.
3. **HW-PINMAP-310 — S360-310 pin/package mapping audit.**
   Schematic ingest, standalone reference doc, and pin / package
   classification for `S360-310` (Sense360 Relay).
4. **HW-PINMAP-311 — S360-311 pin/package mapping audit.** Same
   for `S360-311` (Sense360 PWM).
5. **HW-PINMAP-312 — S360-312 pin/package mapping audit.** Same
   for `S360-312` (Sense360 DAC).
6. **HW-PINMAP-320 — S360-320 FanTRIAC pin/package mapping
   audit.** Same for `S360-320` (Sense360 TRIAC). Does not unblock
   HW-005 by itself; HW-005 resolution and COMPLIANCE-001
   mains-voltage sign-off remain prerequisites for any product /
   WebFlash work on this board.
7. **HW-PINMAP-400 — S360-400 power board mapping audit.** Same
   for `S360-400` (Sense360 240v PSU). Gated by COMPLIANCE-001
   for any product / WebFlash work.
8. **HW-PINMAP-410 — S360-410 PoE PSU mapping audit.** Same for
   `S360-410` (Sense360 PoE PSU). Sense360 PoE PSU is consumed by
   the current Release-One product but its module-side schematic
   is still uncommitted; this PR closes that gap.
9. **PACKAGE-GAP-001 — Add / reconcile package YAMLs where
   evidence exists.** After the HW-PINMAP-* sequence, adds or
   reconciles
   [`packages/`](../../packages/) entries for boards that have
   gained schematic evidence. Per-board scope; does not promote
   any product.
10. **PRODUCT-GAP-001 — Add product YAMLs where packages and
    evidence exist.** After PACKAGE-GAP-001, adds
    [`products/`](../../products/) entries (and WebFlash wrappers
    where applicable) for any new product configuration whose
    underlying packages have landed. Goes through the
    [`docs/product-onboarding.md`](../product-onboarding.md)
    gates and, for any stable promotion, the
    [`docs/preview-to-stable-promotion-gates.md`](../preview-to-stable-promotion-gates.md)
    gates.

Each entry is its own PR, its own review, and its own scope. This
policy does not commit to a calendar or to a particular ordering
beyond "1 before 2", "HW-PINMAP-* before PACKAGE-GAP-001", and
"PACKAGE-GAP-001 before PRODUCT-GAP-001". A given HW-PINMAP-* PR
may land out of numeric order if hardware evidence becomes
available for that SKU first.

## Do-not-change guardrails

This PR (HW-ASSETS-001) is policy / documentation only. It does
**not** modify any of the following:

- [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
- [`config/product-catalog.json`](../../config/product-catalog.json)
- [`config/webflash-builds.json`](../../config/webflash-builds.json)
- [`config/webflash-compatibility.json`](../../config/webflash-compatibility.json)
- Anything under [`products/`](../../products/) (including
  [`products/webflash/`](../../products/webflash/))
- Anything under [`packages/`](../../packages/)
- Anything under [`scripts/`](../../scripts/)
- Anything under [`tests/`](../../tests/)
- Anything under `.github/workflows/`
- Anything under [`components/`](../../components/)
- Anything under [`include/`](../../include/)
- `.gitignore`, `.gitattributes`, or any pre-commit configuration

This PR also does **not**:

- add any raw vendor / fab ZIP contents,
- add any KiCad source, BOM spreadsheet, CPL / pick-and-place
  file, Gerbers ZIP, drill files, STEP model, or board image,
- add the per-board artifact index for `S360-100-R4` (that is the
  scope of HW-ASSETS-002),
- change any hardware-catalog `schematic_status` value or
  `schematic_file` pointer,
- change any product-catalog lifecycle status,
- change any package YAML,
- change any product YAML or WebFlash wrapper,
- change the WebFlash build matrix or the WebFlash compatibility
  taxonomy,
- regenerate, sign, import, deploy, or otherwise produce
  firmware,
- create or modify any GitHub Release,
- unblock FanTRIAC (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays
  `status: blocked`, `blocker: HW-005`,
  `webflash_build_matrix: false`),
- change the Sense360 LED preview / stable status
  (`Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: preview`,
  `channel: preview`),
- change the Release-One shipping configuration
  `Ceiling-POE-VentIQ-RoomIQ` or its artifact
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`,
- change the mains-voltage compliance status for `S360-400` /
  `S360-320` (those remain owned by COMPLIANCE-001),
- introduce Git LFS (listed as a future decision option only),
- add anything to or remove anything from WebFlash-side
  `REQUIRED_CONFIGS`, `kits.json`, `firmware/sources.json`, or
  `manifest.json`.

## See also

- [`docs/hardware-catalog.md`](../hardware-catalog.md) — canonical
  Sense360 board / module names, SKUs, revisions, and legacy
  names. Narrative source of truth for the hardware catalog.
- [`config/hardware-catalog.json`](../../config/hardware-catalog.json)
  — machine-readable mirror of the hardware catalog. The
  `schematic_status` and `schematic_file` fields are the JSON
  pointers that the artifact index mirrors.
- [`docs/hardware/schematics/`](schematics/) — currently-committed
  schematic PDFs for the five finished boards (`S360-100-R4.pdf`,
  `S360-200-R4.pdf`, `S360-210-R4.pdf`, `S360-211-R4.pdf`,
  `S360-300-R4.pdf`).
- [`docs/hardware/s360-100-r4-core.md`](s360-100-r4-core.md) —
  Sense360 Core schematic-backed pin / connector / net reference.
- [`docs/hardware/s360-200-r4-roomiq.md`](s360-200-r4-roomiq.md)
  — Sense360 RoomIQ schematic-backed reference.
- [`docs/hardware/s360-210-r4-airiq.md`](s360-210-r4-airiq.md) —
  Sense360 AirIQ schematic-backed reference.
- [`docs/hardware/s360-211-r4-ventiq.md`](s360-211-r4-ventiq.md)
  — Sense360 VentIQ schematic-backed reference.
- [`docs/hardware/s360-300-r4-led.md`](s360-300-r4-led.md) —
  Sense360 LED schematic-backed reference.
- [`docs/hardware/remaining-board-documentation-audit.md`](remaining-board-documentation-audit.md)
  — HW-004 / HW-006 per-board documentation-state classification,
  with HW-007 schematic ingest and HW-008 JSON refresh
  subsections. The artifact index `pin_map_status` field mirrors
  this audit's classification.
- [`docs/hardware/firmware-package-mapping-audit.md`](firmware-package-mapping-audit.md)
  — HW-009 / HW-010 firmware-package-vs-schematic audit. The
  artifact index `package_yaml_status` field mirrors this audit's
  classification taxonomy.
- [`docs/product-onboarding.md`](../product-onboarding.md) —
  PRODUCT-004 ordered safe sequence for adding any new product /
  config. Any new product YAML derived from a newly-evidenced
  board must go through these gates.
- [`docs/preview-to-stable-promotion-gates.md`](../preview-to-stable-promotion-gates.md)
  — RELEASE-006 cross-cutting preview-to-stable promotion gate
  document. Stable promotion of any product consuming a
  newly-evidenced board still requires the full gate list.
- [`docs/product-deprecation-removal-policy.md`](../product-deprecation-removal-policy.md)
  — PRODUCT-DEP-001 cross-cutting deprecation / removal policy.
  Defines the opposite direction (production / preview →
  deprecated → removed); a board revision retirement would
  interact with this policy when the corresponding products are
  deprecated.
- [`docs/release-one.md`](../release-one.md) — Release-One
  configuration; the product that today consumes Sense360 Core,
  RoomIQ, VentIQ, and PoE PSU.
- [`docs/release-one-hardware-audit.md`](../release-one-hardware-audit.md)
  — Release-One firmware-vs-schematic audit; the source of
  truth for the FanTRIAC HW-005 blocker and the Sense360 LED
  Release-One policy.
- [`docs/compliance/mains-voltage-uk-eu-assessment.md`](../compliance/mains-voltage-uk-eu-assessment.md)
  — COMPLIANCE-001 mains-voltage UK / EU compliance-assessment
  tracker. Additional gate for any product / WebFlash work
  consuming `S360-320` (FanTRIAC) or `S360-400` (240v PSU).
- [`docs/webflash-contract.md`](../webflash-contract.md) —
  canonical WebFlash artifact / grammar / token contract.
- [`docs/webflash-compatibility-taxonomy-audit.md`](../webflash-compatibility-taxonomy-audit.md)
  — COMPAT-001 per-token taxonomy audit; carries the future-token
  policy that gates any new module name surfaced to WebFlash.
- [`docs/cleanup-audit.md`](../cleanup-audit.md) — classification
  of stale / current / blocked-reference / legacy-compatible repo
  content; carries the HW-ASSETS-001 registration entry.

# Cleanup Audit (CLEANUP-001)

This document classifies stale or misleading repo content against the current
Release-One / WebFlash source of truth. It is an **audit and classification
document only**. No files are deleted, renamed, or otherwise changed by the PR
that introduces it. Concrete cleanup work is deferred to follow-up PRs listed
at the end.

## Current source of truth

The Release-One shipping configuration is pinned by the following artifacts
and is the basis for every classification in this document:

| Field | Value |
|---|---|
| WebFlash config string | `Ceiling-POE-VentIQ-RoomIQ` |
| Product YAML | [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml) |
| WebFlash wrapper | [`products/webflash/ceiling-poe-ventiq-roomiq.yaml`](../products/webflash/ceiling-poe-ventiq-roomiq.yaml) |
| Firmware artifact | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` |
| GitHub Release tag | `v1.0.0` |
| Release proof run | <https://github.com/sense360store/esphome-public/actions/runs/25763009641> |
| WebFlash compatibility | [`config/webflash-compatibility.json`](../config/webflash-compatibility.json) |
| WebFlash build matrix | [`config/webflash-builds.json`](../config/webflash-builds.json) |
| WebFlash contract | [`docs/webflash-contract.md`](webflash-contract.md) |
| Release-One overview | [`docs/release-one.md`](release-one.md) |
| Hardware audit | [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md) |
| Release proof record | [`docs/webflash-release-proof.md`](webflash-release-proof.md) |

Workflow roles:

- `.github/workflows/firmware-build-release.yml` — Release-One build/release
  gate. Builds only the WebFlash matrix (excludes `products/webflash/*`
  wrappers from matrix discovery; the matrix runs the canonical product
  YAMLs).
- `.github/workflows/ci-validate-configs.yml` — broad legacy / manual sweep.
  Validates every YAML in `products/` (including legacy
  `sense360-core-*`, `sense360-mini-*`, `sense360-poe.yaml`,
  `sense360-fan-pwm.yaml`) and the generated module-combination configs from
  `tests/generate_test_configs.py`. **Not** the Release-One PR gate.
- `.github/workflows/validate.yml` — ~30s YAML-syntax pre-flight, runs on
  every push/PR.

Exclusions retained pending hardware verification:

- **Sense360 TRIAC / FanTRIAC** is excluded from production Release-One
  pending HW-005 (S360-320 schematic uncommitted, GPIO5 / GPIO6 collide
  with RoomIQ J10 nets, ESPHome `ac_dimmer` requires direct
  interrupt-capable ESP32 GPIOs that the SX1509 expander cannot provide).
  The FanTRIAC product YAML, the FanTRIAC WebFlash wrapper, and
  `packages/expansions/fan_triac.yaml` are retained in the repo as
  blocked / reference files.
- **Sense360 LED** is excluded because the WebFlash config string
  `Ceiling-POE-VentIQ-RoomIQ` does not contain the `LED` token. The LED
  packages remain in the repo for non-Release-One products and for a future
  LED-bearing config string (e.g. `Ceiling-POE-VentIQ-RoomIQ-LED`).

## Audit method

Statuses applied below use the definitions from the task:

| Status | Definition |
|---|---|
| `current` | Matches current Release-One / WebFlash truth. |
| `legacy-compatible` | Old, but may be public API or manual-user path; keep. |
| `blocked-reference` | Intentionally retained, not production-ready (e.g. FanTRIAC). |
| `stale` | Wording or docs contradict current truth; doc-only fix needed. |
| `candidate-for-removal` | Likely removable, needs a separate PR. |
| `dead` | Proven unused, safe to delete later. |
| `unknown` | Cannot prove either way; treat conservatively. |

Search terms run from the repo root (representative):

```text
grep -RIn "FanTRIAC"
grep -RIn "TRIAC"
grep -RIn "LED Ring"
grep -RIn "Sense360 LED"
grep -RIn "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"
grep -RIn "Ceiling-POE-VentIQ-RoomIQ"
grep -RIn "release-one"
grep -RIn "webflash"
grep -RIn "Bathroom Pro"
grep -RIn "AirIQ"
grep -RIn "Celling"
grep -RIn "ci-validate-configs"
grep -RIn "31+ products"
grep -RIn "all products"
grep -RIn "v3\\.0\\.0|v2\\.2\\.0|v2\\.0\\.0"
grep -Rl "github://sense360store/esphome-public"
find . -name "*.bak" -o -name "*.orig" -o -name "*~" -o -name "*.tmp"
```

Inspected paths: `README.md`, `CHANGELOG.md`, `docs/**`, `examples/**`,
`products/**`, `products/webflash/**`, `packages/**`, `config/**`,
`.github/workflows/**`, `tests/**`, `scripts/**`, `components/**`,
`include/**`, and the top-level `base/`, `features/`, `hardware/` symlinks
(which resolve into `packages/base/`, `packages/features/`,
`packages/hardware/`).

## Findings summary

| Path | Status | Finding | Recommended action |
|---|---|---|---|
| `products/sense360-ceiling-poe-ventiq-roomiq.yaml` | `current` | Canonical Release-One YAML; builds `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`. | Keep. |
| `products/webflash/ceiling-poe-ventiq-roomiq.yaml` | `current` | Thin WebFlash wrapper for Release-One. | Keep. |
| `config/webflash-builds.json` | `current` | WebFlash build matrix. Carries the Release-One stable build `Ceiling-POE-VentIQ-RoomIQ` (channel=`stable`, version=`1.0.0`, artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`) and, after PRODUCT-009, the LED-bearing preview sibling `Ceiling-POE-VentIQ-RoomIQ-LED` (channel=`preview`, version=`1.0.0`, artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`, `product_yaml: products/webflash/ceiling-poe-ventiq-roomiq-led.yaml`, `chip_family: ESP32-S3`, hardware-requirements and features lists carry the Sense360 LED entries). FanTRIAC stays out of the build matrix under HW-005. | Keep. |
| `config/webflash-compatibility.json` | `current` | Canonical module / forbidden-token list; `release_one_required_configs: ["Ceiling-POE-VentIQ-RoomIQ"]`. | Keep. |
| `config/hardware-catalog.json` | `current` | Canonical SKU → friendly-name table; carries `old_name` entries for `LED Ring` (S360-300) and `Bathroom Pro` (S360-211), which is correct. | Keep. |
| `config/product-catalog.json` | `current` | Product source-of-truth catalog (PRODUCT-001). Records lifecycle status for each Sense360 product configuration; Release-One `Ceiling-POE-VentIQ-RoomIQ` is `production` on `stable`, FanTRIAC `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` is `blocked` (HW-005), and after PRODUCT-009 the LED-bearing sibling `Ceiling-POE-VentIQ-RoomIQ-LED` is `preview` with `webflash_build_matrix: true`, `version: 1.0.0`, `channel: preview`, `artifact_name: Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`, `blocked_modules: ["FanTRIAC"]` (LED omitted because this entry carries the `LED` token), `hardware` SKU map (Core / VentIQ / RoomIQ / PoE / LED), and `modules` map. Lifecycle layer on top of `config/webflash-builds.json`. | Keep. |
| `tests/test_product_catalog.py` | `current` | Validates `config/product-catalog.json`: schema, required fields per status, path existence, config-string uniqueness, artifact-name pattern, and one-way cross-check against `config/webflash-builds.json` (blocked entries must not appear in the build matrix; build entries must appear in the catalog with a WebFlash-eligible status). | Keep. |
| `scripts/validate_product_catalog_consistency.py` | `current` | PRODUCT-003 read-only catalog consistency validator. Cross-checks `config/product-catalog.json` against `config/webflash-builds.json`, `config/webflash-compatibility.json`, `config/hardware-catalog.json`, `scripts/product_name_mapper.py`, product YAML paths, and WebFlash wrapper paths. Provides `--checklist` and `--product` modes for the add-product workflow. Read-only; no mutation, no scaffold generation. | Keep. |
| `tests/test_product_catalog_consistency.py` | `current` | Stdlib `unittest` suite covering `scripts/validate_product_catalog_consistency.py`: current-repo-state pass, Release-One production checks, FanTRIAC blocked checks, legacy-compatible non-shippability sweep, mapper agreement, wrapper basename agreement, and checklist mode. | Keep. |
| `.github/workflows/firmware-build-release.yml` | `current` | Release-One build/release gate; excludes `products/webflash/*` from matrix discovery; runs `tests/check_webflash_build_output.py`. RELEASE-004 delegates the version/channel derivation in the `Determine version and channel` step to `scripts/derive_release_version_channel.py` so preview release tags can carry a suffix (`v1.0.0-led-preview` or `v1.0.0-preview`) while still resolving to the semver in `config/webflash-builds.json`; stable releases must use plain semantic tags (`vX.Y.Z`) and any suffixed stable tag or unrecognized prerelease suffix is rejected with a clear error. | Keep. |
| `scripts/derive_release_version_channel.py` | `current` | RELEASE-004 tag-normalization helper. Maps a GitHub release tag plus the release's `prerelease` flag to the `(version, channel)` pair the build matrix filters on. Allowed prerelease suffixes: `-led-preview`, `-preview`. Stable releases must use plain semantic tags (`vX.Y.Z`); any suffix on a non-prerelease tag is rejected. Unknown prerelease suffixes are rejected with an explicit error so operator typos fail fast at the derive step instead of later in the matrix filter. Env-driven CLI (`GITHUB_REF_NAME`, `PRERELEASE`); writes `version=` / `channel=` lines to stdout and, when set, to `$GITHUB_OUTPUT`. Does **not** build firmware, tag releases, change the LED preview version, mark LED stable, commit `.bin` files, or unblock FanTRIAC. | Keep. |
| `tests/test_derive_release_version_channel.py` | `current` | RELEASE-004 stdlib `unittest` suite for `scripts/derive_release_version_channel.py`. Covers stable plain tag, stable tag without `v` prefix, preview `-led-preview` suffix, preview `-preview` suffix, prerelease plain tag, stable suffixed tag rejection, prerelease unknown / typo suffix rejection, nested-dash rejection, empty tag rejection, and a CLI smoke section that runs the script via `subprocess` to confirm exit codes, stdout, and `$GITHUB_OUTPUT` writes. | Keep. |
| `.github/workflows/validate.yml` | `current` | Quick YAML syntax pre-flight; also runs the WebFlash builds / catalog / release-notes generator / RELEASE-002 release-notes-draft-workflow smoke tests. | Keep. |
| `.github/workflows/release-notes-draft.yml` | `current` | RELEASE-002 manual release-notes draft workflow (`workflow_dispatch` only). Inputs: `config_string`, `version`, `channel` (`stable`/`preview`), optional `changelog`. Runs `scripts/generate_webflash_release_notes.py`, then `scripts/validate-webflash-release-notes.py`, then uploads `release-notes.md` as a workflow artifact. Does not create a GitHub Release, does not publish firmware, does not commit the draft, does not infer changelog content from git history, does not pass `--require-changelog`, and does not modify the release-publish gates in `firmware-build-release.yml`. | Keep. |
| `scripts/product_name_mapper.py` | `current` | Maps product YAML basenames → WebFlash artifact names; explicit comment retains FanTRIAC mapping as legacy reference. | Keep. |
| `scripts/check-webflash-release-assets.py` | `current` | Asset-existence gate. | Keep. |
| `scripts/validate-webflash-release-notes.py` | `current` | Release-body format gate. | Keep. |
| `scripts/generate_webflash_release_notes.py` | `current` | RELEASE-001 read-only release-notes draft generator. Produces a Markdown draft body matching the format enforced by `scripts/validate-webflash-release-notes.py`, sourcing lifecycle / SKU data from `config/product-catalog.json`, feature bullets from `config/webflash-builds.json`, and friendly hardware names from `config/hardware-catalog.json`. Refuses blocked / legacy-compatible / deprecated / removed entries; refuses preview entries on the stable channel; emits FanTRIAC and Sense360 LED as Known-Issues exclusions when listed in the catalog entry's `blocked_modules`. For the Release-One catalog entry both FanTRIAC and LED stay in `blocked_modules` so the Release-One body lists them as Known Issues; for the LED preview catalog entry only FanTRIAC is in `blocked_modules`, so the LED preview body places Sense360 LED in `## Features` and `## Hardware Requirements` while keeping FanTRIAC in `## Known Issues` with the HW-005 reference. PRODUCT-009 softened the FanTRIAC Known-Issues wording from "this Release-One firmware" to "this firmware" so the bullet is accurate for both Release-One and the LED preview. Read-only: does not create releases, publish firmware, infer changelog content from git history, or call any external service. | Keep. |
| `tests/test_generate_webflash_release_notes.py` | `current` | Stdlib `unittest` suite covering `scripts/generate_webflash_release_notes.py`: Release-One generation, validator pass, config-string / artifact / SKU presence, FanTRIAC / LED as exclusions, blocked / legacy-compatible / unknown-config refusal, stable-channel requires production status, custom changelog text and file, `--output` file write, `--validate` shell-out to the existing release-notes validator. | Keep. |
| `tests/test_release_notes_draft_workflow.py` | `current` | RELEASE-002 stdlib `unittest` smoke test for `.github/workflows/release-notes-draft.yml`. Asserts the workflow file exists, declares `workflow_dispatch:` and no other triggers, references the generator and validator scripts, uploads an artifact, and does not pass `--require-changelog`. Intentionally a substring smoke check rather than a YAML schema parse. | Keep. |
| `tests/validate_webflash_builds.py` | `current` | Validates `config/webflash-builds.json` against `config/webflash-compatibility.json`. | Keep. |
| `tests/test_webflash_compatibility.py` | `current` | Asserts canonical-module / Release-One required-config invariants. | Keep. |
| `tests/test_webflash_artifact_naming.py` | `current` | Pins Release-One artifact filename. | Keep. |
| `tests/test_validate_webflash_builds.py` | `current` | Unit tests for build-matrix validator. | Keep. |
| `tests/test_validate_webflash_release_notes.py` | `current` | Unit tests for release-notes validator. | Keep. |
| `tests/test_release_one_entity_names.py` | `current` | Pins Release-One entity names against legacy drift. | Keep. |
| `tests/test_product_substitutions.py` | `current` | Substitutions invariants for Release-One. | Keep. |
| `tests/check_webflash_build_output.py` | `current` | Build-time artifact-name assertion. | Keep. |
| `tests/validate_configs.py` | `current` | Repo-wide YAML/syntax validator. | Keep. |
| `docs/release-one.md` | `current` | Source of truth for Release-One config string / artifact / exclusions. | Keep. |
| `docs/release-one-hardware-audit.md` | `current` | HW-005 / FanTRIAC mapping resolution; LED policy. | Keep. |
| `docs/hardware/remaining-board-documentation-audit.md` | `current` | HW-004 / HW-006 audit classifying every `config/hardware-catalog.json` row by documentation state (`documented` / `partially-documented` / `cataloged-unverified` / `blocked` / `not-needed-for-release-one`); records evidence available vs. missing per board; preserves FanTRIAC blocked and LED Release-One-excluded statuses; no firmware / product / workflow / build-matrix change. | Keep. |
| `docs/compliance/mains-voltage-uk-eu-assessment.md` | `current` | COMPLIANCE-001 mains-voltage UK / EU compliance-assessment tracker for `S360-400` Sense360 240v PSU and `S360-320` Sense360 TRIAC; expands the mains-voltage safety / compliance note in `docs/hardware/remaining-board-documentation-audit.md` into a per-board evidence checklist (product classification, protection-class decision tree, standards / regulations applicability, electrical-safety topics, EMC topics, preview-vs-stable evidence, technical-file checklist, DoC checklist, open questions for compliance engineer / test lab, release blockers); documentation only; makes no CE / UKCA / LVD / EMC / RED / RoHS / "safe for mains" / "approved for mains" claim and uses `Likely applicable` / `To be confirmed` / `Requires qualified review` / `Not proven by this repository` framing throughout; preserves the FanTRIAC HW-005 blocked status, the Sense360 LED Release-One-excluded status, every `config/hardware-catalog.json` `schematic_status` value, every `config/product-catalog.json` lifecycle status, and the Release-One PoE-only config string `Ceiling-POE-VentIQ-RoomIQ`; no firmware / product / config / workflow / build-matrix change. | Keep. |
| `docs/product-onboarding.md` (PRODUCT-005 cross-link refresh; RELEASE-005 LED proof refresh) | `current` | PRODUCT-004 cross-doc product onboarding guide. Orders the existing guardrails (hardware audit, mains-voltage compliance tracker, product catalog, consistency validator, WebFlash build matrix, release-notes generator, build / release proof, WebFlash handoff) into a safe sequence for adding a new product / config; lists preview-vs-production evidence gates, where each source of truth lives, the read-only commands to run, the explicit guardrails ("do not mark `production` just because YAML compiles", "do not add blocked products to the build matrix", "do not add FanTRIAC until HW-005 evidence changes", "do not add `LED` to Release-One without an LED token and hardware evidence", "do not treat `legacy-compatible` as WebFlash-shippable", "do not use mains-voltage boards before compliance review", "do not hand-edit generated manifests"), a Release-One worked example and a blocked-FanTRIAC worked example, and the future WebFlash handoff contract; documentation only; preserves the Release-One product / artifact / build matrix / compatibility JSON / hardware SKUs / catalog statuses / FanTRIAC HW-005 blocked status / Sense360 LED Release-One-excluded status. PRODUCT-005 refreshes the LED guardrail and the See-also list with a pointer to `docs/product-led-preview-decision.md` and the PRODUCT-006 / PRODUCT-007 / PRODUCT-008 / PRODUCT-009 follow-up PR sequence. RELEASE-005 updates the LED guardrail and the `docs/webflash-release-proof.md` See-also entry to record that the LED preview build / release proof is now recorded (tag `v1.0.0-led-preview`, run `25918422743`, artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` (1,135,904 bytes; SHA256 `93310d2cbc27355e399f36a232336b6b9075dacfc178d603c7a92aa1089182d3`), validators passed); the LED catalog entry stays `preview`; Release-One stays unchanged; FanTRIAC stays blocked; WebFlash-side import remains the only outstanding step before LED becomes WebFlash-shippable. | Keep. |
| `docs/product-led-preview-decision.md` (RELEASE-005 LED proof refresh) | `current` | PRODUCT-005 LED preview product path decision doc. Records that verified Sense360 LED schematic evidence (HW-007 / HW-008) plus the ceiling LED package pin fix (HW-010) do not by themselves make Sense360 LED WebFlash-shippable; enumerates the current evidence, the canonical LED-bearing config string `Ceiling-POE-VentIQ-RoomIQ-LED`, the catalog status options against the consistency validator's lifecycle rule blocks, and the product YAML / WebFlash wrapper / build-matrix entry / release-notes draft / build-release proof artefacts that would still be required. Decision table covers Options A–E (documented only / `compile-only` catalog entry / `preview` entry without build matrix / `preview` entry with wrapper + build matrix / Release-One `production` edit) and picks **Option A for this PR, with Option C later**. Defines the scoped follow-up PR sequence: PRODUCT-006 (add LED-bearing product YAML), PRODUCT-007 (add `compile-only` catalog entry), PRODUCT-008 (add WebFlash wrapper and promote to `preview`), PRODUCT-009 (add `preview` build to the build matrix + record a build / release proof + re-scope `tests/test_led_package_mapping.py` LED-exclusion to the Release-One build only + update `scripts/generate_webflash_release_notes.py` so the LED-bearing build emits Sense360 LED as a Feature). States the guardrails: verified LED schematic + fixed package pin mapping does not equal shippable product; LED is still not in current Release-One; WebFlash must not expose LED until there is a catalog-eligible product, artifact, and manifest; FanTRIAC remains unrelated and blocked. Documentation only; preserves the Release-One product / artifact / build matrix / compatibility JSON / hardware-catalog statuses / product-catalog statuses / FanTRIAC HW-005 blocked status / mains-voltage compliance status / Sense360 LED Release-One-excluded status; PRODUCT-005 adds no product YAML, no WebFlash wrapper, no catalog entry, no build-matrix entry, no release-notes draft, no tests, no scripts, no workflow change. RELEASE-005 updates the PRODUCT-009 outstanding-proof paragraph and the "Current evidence" no-artifact bullet to reflect that the LED preview build / release proof is now recorded (tag `v1.0.0-led-preview`, run `25918422743`, artifact `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` (1,135,904 bytes; SHA256 `93310d2cbc27355e399f36a232336b6b9075dacfc178d603c7a92aa1089182d3`)), and updates the See-also pointer to `docs/webflash-release-proof.md` to mention the RELEASE-005 backfill; the LED catalog entry stays `preview`, Release-One stays unchanged, FanTRIAC stays blocked, and WebFlash-side import remains the only outstanding step. | Keep. |
| `docs/preview-to-stable-promotion-gates.md` (RELEASE-006) | `current` | RELEASE-006 canonical, cross-cutting preview-to-stable promotion gate document. Defines, for any future preview product (today the LED preview; tomorrow AirIQ-bearing / FanRelay-bearing / FanPWM-bearing / FanDAC-bearing / PWR-bearing variants), what evidence + sign-offs are required to promote a preview build to `status: production` / `channel: stable`. Includes: a 17-row gate summary table (product YAML, WebFlash wrapper, catalog preview entry, build-matrix preview entry, preview release artifact, preview release proof recorded, WebFlash import, live preview deploy, real WebFlash flash proof (WF-HW-TEST-001), hardware bench verification, stable release notes, production catalog promotion, stable build artifact, stable WebFlash import, REQUIRED_CONFIGS decision, kit / UI decision, human approval) with an owning-repo column and a live LED-preview status column; required upstream / firmware / hardware / WebFlash / operator evidence; per-field promotion diffs for `config/product-catalog.json` and `config/webflash-builds.json`; the human approval checklist (hardware, release engineer, WebFlash operator, compliance if mains, REQUIRED_CONFIGS decision, kit decision, release authority); the explicit "preview artifact + WebFlash import + deployed manifest do not equal stable" guardrails; the separate `REQUIRED_CONFIGS` policy (a stable build is **not** automatically added to baseline-health REQUIRED_CONFIGS — that is a separate WebFlash decision); the separate kit policy (a stable build does **not** automatically get a kit — that is a separate WebFlash product decision); a six-PR follow-up sequence for a future stable promotion (hardware bench verification → operator flash proof → stable release-notes + tag → catalog + build-matrix promotion → WebFlash stable import → optional REQUIRED_CONFIGS / kit PRs); and an LED preview case study marking rows 1–8 (preview floor) `done` and rows 9–17 explicitly `pending` / `decision needed` (operator flash proof WF-HW-TEST-001, S360-300 bench verification of harness rail / LED count / harness identity per `docs/hardware/s360-300-r4-led.md`, stable release notes, production catalog promotion, stable build artifact, stable WebFlash import, REQUIRED_CONFIGS decision, kit decision, recorded human approval). RELEASE-006 itself is documentation only: no `config/*`, `products/*`, `products/webflash/*`, `packages/*`, `scripts/*`, `tests/*`, `.github/workflows/*`, `components/*`, or `include/*` change; no firmware regenerated; no LED promotion (LED catalog stays `status: preview`, `channel: preview`); no Release-One change (`Ceiling-POE-VentIQ-RoomIQ`, `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag `v1.0.0`); no FanTRIAC unblock (HW-005 stays open; FanTRIAC is called out as the canonical blocked-module example and is explicitly **not** on the stable promotion path); no `REQUIRED_CONFIGS` or kit additions in the WebFlash repo. Cross-linked from `docs/product-onboarding.md`, `docs/product-led-preview-decision.md`, `docs/webflash-release-proof.md`, `docs/webflash-release-handoff.md`, and `docs/hardware/s360-300-r4-led.md` (Open Questions section). | Keep. |
| `docs/webflash-compatibility-taxonomy-audit.md` | `current` | COMPAT-001 per-token audit of `config/webflash-compatibility.json` against `config/product-catalog.json`, `config/webflash-builds.json`, `config/hardware-catalog.json`, `docs/hardware/remaining-board-documentation-audit.md`, `docs/compliance/mains-voltage-uk-eu-assessment.md`, and `docs/product-onboarding.md`. Records the source-of-truth separation (taxonomy / lifecycle / build matrix / hardware), the explicit "taxonomy != shippability" policy, a full per-token decision table (Ceiling, POE, PWR, USB, AirIQ, VentIQ, RoomIQ, FanRelay, FanPWM, FanDAC, FanTRIAC, LED, Voice) with hardware-evidence and follow-up columns, the current Release-One mapping, the blocked / excluded modules summary (FanTRIAC per HW-005, LED per Release-One config-string policy), the future-token policy, a test-coverage summary (existing tests + the six drift-protection tests added in the same PR), recommended follow-up PRs (HW-007 schematic ingest, future LED variant, FanTRIAC unblock, AirIQ / FanRelay / FanPWM / FanDAC preview entries, future PWR-bearing entry, optional forbidden-token alignment with `docs/webflash-contract.md` §3), and an explicit do-not-change list; flags that new schematic PDFs for `S360-100`, `S360-200`, `S360-210`, `S360-211`, and `S360-300` are deferred to HW-007 and do not change COMPAT-001 decisions; documentation only; preserves the Release-One product / artifact / build matrix / compatibility JSON / hardware SKUs / catalog statuses / FanTRIAC HW-005 blocked status / Sense360 LED Release-One-excluded status. HW-007 has now landed: the HW-007 note block is refreshed to record that the PDFs and per-board AirIQ / VentIQ / LED docs are committed and that the JSON `schematic_status` refresh is deferred to HW-008 (per-token cells for AirIQ / VentIQ / LED gain inline pointers to the new docs; no verdict / shippability cell changes; the VentIQ "schematic verification pending" caveat is retained until HW-008). | Keep. |
| `docs/hardware/schematics/` | `current` | HW-007 schematic evidence directory. Contains the committed module-side schematic PDFs: `S360-100-R4.pdf` (Core), `S360-200-R4.pdf` (RoomIQ), `S360-210-R4.pdf` (AirIQ), `S360-211-R4.pdf` (VentIQ), `S360-300-R4.pdf` (Sense360 LED). Each PDF is the authoritative source of truth for its corresponding standalone reference doc under `docs/hardware/`. The PDFs do not include FanTRIAC (`S360-320`), Relay (`S360-310`), PWM (`S360-311`), DAC (`S360-312`), 240v PSU (`S360-400`), or PoE PSU (`S360-410`) — those module-side schematics are still uncommitted post-HW-007. | Keep. |
| `docs/hardware/s360-210-r4-airiq.md` | `current` | HW-007 standalone pin / connector reference doc for `S360-210-R4` Sense360 AirIQ. Mirrors the structure of `docs/hardware/s360-100-r4-core.md` / `docs/hardware/s360-200-r4-roomiq.md`: board identity, schematic source (citing `schematics/S360-210-R4.pdf`), main components visible on the sheet (SGP41, SCD41, SFA40 connector, SPS30 connector, MICS-4514 + STM8 I²C-bridge sub-sheet), Core-side J9 mating table, I²C bus, Open Questions, firmware-mapping notes, and an explicit HW-007 scope / non-scope block. Explicitly states AirIQ remains mutually exclusive with VentIQ, not in Release-One, and not WebFlash-shippable — HW-007 only improves legacy / manual hardware documentation. JSON `schematic_status` flip is now refreshed by HW-008 (`verified`, `schematic_file: docs/hardware/schematics/S360-210-R4.pdf`); HW-008 does not change AirIQ's WebFlash-shippability, mutex, or Release-One status. | Keep. |
| `docs/hardware/s360-211-r4-ventiq.md` | `current` | HW-007 standalone pin / connector reference doc for `S360-211-R4` Sense360 VentIQ. Same template as the AirIQ doc. Captures SGP41 on board, IR-temperature connector, SPS30 connector, on-board fan-relay drive circuitry, and Core-side J9 mating. Explicitly records: Release-One config string remains `Ceiling-POE-VentIQ-RoomIQ`; package filename `airiq_bathroom_base.yaml` retained per WebFlash contract §6; mains-side topology, contact rating, and creepage / clearance for the on-board relay are tracked separately under COMPLIANCE-001 — HW-007 makes no compliance claim. JSON `schematic_status` and the "schematic verification pending" caveat in `release-one-hardware-audit.md` / `webflash-compatibility-taxonomy-audit.md` are now refreshed by HW-008 (JSON: `verified`, `schematic_file: docs/hardware/schematics/S360-211-R4.pdf`; the caveat is retired). HW-008 does not change Release-One config / build matrix / artifact / lifecycle / mains compliance. | Keep. |
| `docs/hardware/s360-300-r4-led.md` (HW-010 refresh) | `current` | HW-007 standalone reference doc for `S360-300-R4` Sense360 LED. Captures J1 (3-pin: LED_DATA / +5V / GND) and the on-board WS2812B LED chain. Explicitly records: Sense360 LED is **not** in Release-One; the Release-One config string `Ceiling-POE-VentIQ-RoomIQ` carries no `LED` token; the Release-One YAML omits LED package includes on purpose. JSON `schematic_status` flip refreshed by HW-008 (`verified`, `schematic_file: docs/hardware/schematics/S360-300-R4.pdf`); HW-008 did **not** add `LED` to the Release-One config string. The `GPIO14` (package) vs `IO38` (Core schematic) `LED_DATA` discrepancy at the package level has since been **resolved by HW-010** — the ceiling LED package now binds `led_data_pin: GPIO38`. HW-010 did not add `LED` to the Release-One config string, did not add a WebFlash LED build, did not add a product-catalog LED entry, did not promote Sense360 LED to WebFlash-shippable, and did not change the FanTRIAC HW-005 blocker. The wall LED and legacy S3 Core packages remain unresolved at the package level. | Keep. |
| `docs/hardware/s360-100-r4-core.md` (HW-007 cross-link refresh) | `current` | Existing Core hardware reference doc; HW-007 changes the `Schematic source` table to point at `[`schematics/S360-100-R4.pdf`](schematics/S360-100-R4.pdf)` and adds a one-line `HW-007 — PDF committed` admonition. No pin tables, Open Questions, or reconciliation flags changed. | Keep. |
| `docs/hardware/s360-200-r4-roomiq.md` (HW-007 cross-link refresh) | `current` | Existing RoomIQ hardware reference doc; HW-007 changes the `Schematic source` table to point at `[`schematics/S360-200-R4.pdf`](schematics/S360-200-R4.pdf)` and adds a one-line `HW-007 — PDF committed` admonition. The Core J10 vs RoomIQ J6 pin-order discrepancy remains an Open Question and is not resolved by HW-007. | Keep. |
| `docs/hardware/remaining-board-documentation-audit.md` (HW-007 ingest + HW-008 refresh) | `current` | HW-004 / HW-006 per-board documentation audit. HW-007 refreshed the AirIQ / VentIQ / LED decision-table and evidence rows to point at the newly committed PDFs and standalone docs, and added an `HW-007 schematic ingest` subsection. HW-008 then reclassified those rows from `cataloged-unverified` / `partially-documented` to `documented` (with `not-needed-for-release-one` retained for AirIQ and LED), updated the Release-One coverage summary (VentIQ moves to `documented`; PoE PSU stays `partially-documented`), and added an `HW-008 schematic-status refresh` subsection recording what HW-008 commits and what it does **not** change (no Release-One config / build matrix / artifact / lifecycle change; no FanTRIAC unblock; no LED Release-One promotion; no mains-compliance change). What remains unproven after HW-008: FanTRIAC (`S360-320`), Relay / PWM / DAC / 240v PSU / PoE PSU module-side schematics, Core J10 vs RoomIQ J6 pin order, `GPIO14` vs `IO38` LED_DATA discrepancy, `AirQ_Led` / `AirQ_Status_Led` reuse on AirIQ vs VentIQ, mains-voltage compliance for COMPLIANCE-001 boards. HW-009 adds the firmware-package-mapping classification on top: see `docs/hardware/firmware-package-mapping-audit.md`. | Keep. |
| `docs/hardware/firmware-package-mapping-audit.md` (HW-009 + HW-010 refresh) | `current` | HW-009 docs-only audit reconciling firmware package YAMLs against the now-`verified` HW-007 / HW-008 schematics (`S360-100`, `S360-200`, `S360-210`, `S360-211`, `S360-300`). Classifies each mapping using a six-label taxonomy (`confirmed-ok`, `needs-package-change`, `needs-doc-fix`, `needs-silkscreen/bench-verification`, `blocked`, `unknown`). HW-010 has since reclassified the LED_DATA / Sense360 LED row from `needs-package-change` (deferred) to `confirmed-ok` — the ceiling LED package now binds `led_data_pin: GPIO38`. The remaining rows are unchanged: Core J10 vs RoomIQ J6 pin-order discrepancy (`needs-silkscreen/bench-verification`); VentIQ J9 `AirQ_Led` / `AirQ_Status_Led` reuse (`confirmed-ok` with legacy-naming caveat — package does not bind those nets); AirIQ J9 `AirQ_Led` / `AirQ_Status_Led` reuse (`confirmed-ok` with legacy-naming caveat); VentIQ legacy package filename `airiq_bathroom_base.yaml` (`confirmed-ok`, retained per WebFlash contract §6); Release-One product YAML package stack systemic Core abstract-bus mismatch (`needs-package-change` — explicit out-of-scope; owned by `release-one-hardware-audit.md` Required follow-ups #2 / #3); FanTRIAC `GPIO5` / `GPIO6` placeholders (`blocked` under HW-005; additionally gated by COMPLIANCE-001). Records recommended follow-up PRs (HW-010 LED pin fix — **resolved**; J10/J6 silkscreen reconciliation; `AirQ_*` indicator-line bench verification; systemic Core abstract-bus rebind; HW-005 remains blocked separately). HW-009 itself was documentation only. HW-010 is the scoped one-package follow-up: it edits `packages/hardware/led_ring_ceiling.yaml` (`GPIO14` → `GPIO38`) and adds `tests/test_led_package_mapping.py`; it does **not** edit any product YAML, WebFlash wrapper, JSON config, workflow, script, component, or include; it does **not** rename any package filename, change any hardware-catalog `schematic_status`, change any product-catalog lifecycle status, add a `LED` token to the Release-One config string, add a WebFlash LED build, add an LED product-catalog entry, or change the FanTRIAC HW-005 blocked status. Preserves the Release-One config string `Ceiling-POE-VentIQ-RoomIQ`, the Release-One artifact name `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, the WebFlash build matrix, the WebFlash compatibility snapshot, and the mains-voltage compliance status for `S360-400` and `S360-320`. The wall LED package (`led_ring_wall.yaml`, `GPIO48`) and the legacy S3 Core package (`sense360_core_ceiling_s3.yaml`, `GPIO14`) are intentionally not changed by HW-010 — neither has Core-side schematic evidence proving the same `LED_DATA` path; both remain documented as unresolved. Validated by the existing test suite (`tests/test_hardware_catalog.py`, `tests/test_product_catalog.py`, `tests/test_product_catalog_consistency.py`, `tests/validate_webflash_builds.py`, `tests/test_webflash_compatibility.py`, `tests/test_webflash_artifact_naming.py`, `tests/test_validate_webflash_release_notes.py`, `tests/test_generate_webflash_release_notes.py`, `tests/test_product_substitutions.py`, `tests/test_release_one_entity_names.py`, `tests/validate_configs.py`, `scripts/validate_product_catalog_consistency.py`) plus the new `tests/test_led_package_mapping.py`. | Keep. |
| `packages/hardware/led_ring_ceiling.yaml` (HW-010 pin fix) | `current` | Ceiling LED ring package. HW-010 changes `led_data_pin` from `GPIO14` to `GPIO38` so the package matches the verified `S360-100-R4` schematic (`IO38 = LED_DATA → U2A 74LVC1G07 buffer → R8 330 Ω → J3 → S360-300 J1`). Pin substitution is consumed by `esp32_rmt_led_strip` via `pin: ${led_data_pin}`; the rest of the package (LED count, RGB order, chipset, effects, brightness / night-mode controls, SKU text sensor) is unchanged. Filename retained per WebFlash contract §6 (legacy package filenames are public API). Consumers are `legacy-compatible` products only (`sense360-core-ceiling.yaml`, `sense360-core-ceiling-bathroom.yaml`, `sense360-core-ceiling-presence.yaml`); Release-One does **not** `!include` this package and HW-010 does not add it. | Keep. |
| `tests/test_led_package_mapping.py` | `current` | HW-010 stdlib `unittest` validator for the ceiling LED package pin mapping and PRODUCT-009 stable-channel LED exclusion. Locks in: `packages/hardware/led_ring_ceiling.yaml` contains `led_data_pin: GPIO38` and no `GPIO14`; the Release-One YAML `products/sense360-ceiling-poe-ventiq-roomiq.yaml` does not `!include` `led_ring_ceiling.yaml`; the Release-One build `Ceiling-POE-VentIQ-RoomIQ` remains in `config/webflash-builds.json` on `channel: stable` with no `LED` token in its `config_string` or `artifact_name`; every `stable`-channel build is LED-less; every LED-bearing build is non-stable and points at the LED WebFlash wrapper `products/webflash/ceiling-poe-ventiq-roomiq-led.yaml`; the FanTRIAC entry `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` in `config/product-catalog.json` remains `status: blocked`, `blocker: HW-005`, `webflash_build_matrix: false`; the Release-One catalog entry keeps `LED` and `FanTRIAC` in `blocked_modules`. PRODUCT-009 re-scoped the previous "no LED token in any build" assertion to the stable channel and added the LED-preview-shape assertions. Read-only file-content checks; no ESPHome compile required. | Keep. |
| `products/sense360-ceiling-poe-ventiq-roomiq-led.yaml` (PRODUCT-006) | `current` | LED-bearing sibling-candidate product YAML for the WebFlash config string `Ceiling-POE-VentIQ-RoomIQ-LED`. Same Core ceiling + PoE PSU + VentIQ + RoomIQ package stack as the Release-One YAML `products/sense360-ceiling-poe-ventiq-roomiq.yaml`, plus `packages/hardware/led_ring_ceiling.yaml` (which binds `led_data_pin: GPIO38` after HW-010). Differs from Release-One only in: `device_name` (`s360-ceil-poe-ventiq-rm-led`), `friendly_name` (`Sense360 Ceiling Bathroom LED`), `fallback_ssid` (`S360 VentIQ RoomIQ LED`), and the `WebFlash Config` text-sensor return value (`Ceiling-POE-VentIQ-RoomIQ-LED`). FanTRIAC is intentionally omitted (HW-005 blocker unchanged). PRODUCT-006 added the YAML plus the **minimum** `status: compile-only` entry in `config/product-catalog.json` needed to satisfy the existing PRODUCT-002 enumeration gate at `tests/test_product_catalog.py::test_every_top_level_product_yaml_is_in_catalog`. **PRODUCT-008 has since added the WebFlash wrapper `products/webflash/ceiling-poe-ventiq-roomiq-led.yaml` and promoted the catalog entry from `compile-only` to `preview` with `webflash_build_matrix: false`, `hardware_status: verified-led-candidate`, and a `webflash_wrapper` pointer.** PRODUCT-006/008 do **not** edit the Release-One YAML; do **not** add a `config/webflash-builds.json` build (deferred to PRODUCT-009); do **not** declare an `artifact_name` / `version` / `channel`; do **not** generate or release any firmware; do **not** change `tests/test_led_package_mapping.py` (the Release-One YAML still does not `!include` the LED package, no WebFlash build carries an `LED` token, and FanTRIAC stays `status: blocked` / `blocker: HW-005` / `webflash_build_matrix: false`); do **not** change `config/webflash-compatibility.json`, `config/hardware-catalog.json`, the Release-One config string, the Release-One artifact name, the WebFlash build matrix, or the mains-voltage compliance status for `S360-400` / `S360-320`. PRODUCT-007 remains a no-op absorbed by PRODUCT-006; next active work is PRODUCT-009 (build-matrix entry + release proof). Decision-doc record: `docs/product-led-preview-decision.md` (PRODUCT-005, Option A → C). Validated by the existing surface: `tests/validate_configs.py`, `tests/test_product_substitutions.py`, `tests/test_product_catalog.py`, `tests/test_product_catalog_consistency.py`, `tests/test_led_package_mapping.py`, plus `scripts/validate_product_catalog_consistency.py`. | Keep. |
| `products/webflash/ceiling-poe-ventiq-roomiq-led.yaml` (PRODUCT-008 / PRODUCT-009) | `current` | LED-bearing **preview** WebFlash wrapper for the config string `Ceiling-POE-VentIQ-RoomIQ-LED`. Thin wrapper that `!include`s the canonical product YAML `products/sense360-ceiling-poe-ventiq-roomiq-led.yaml`, in the same pattern as the Release-One wrapper `products/webflash/ceiling-poe-ventiq-roomiq.yaml`. Basename (`ceiling-poe-ventiq-roomiq-led`) equals the lower-cased config string per the validator rule in `scripts/validate_product_catalog_consistency.py`. Referenced both by the catalog entry's `webflash_wrapper` field (PRODUCT-008) and by the new LED preview build entry in `config/webflash-builds.json` (PRODUCT-009) as the build's `product_yaml`. After PRODUCT-009 the LED preview build declares `channel: preview`, `version: 1.0.0`, `artifact_name: Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin`, `chip_family: ESP32-S3`. RELEASE-005 records the corresponding build / release proof in `docs/webflash-release-proof.md` (tag `v1.0.0-led-preview`, run `25918422743`, artifact built and attached at 1,135,904 bytes; SHA256 `93310d2cbc27355e399f36a232336b6b9075dacfc178d603c7a92aa1089182d3`). **NOT** Release-One stable (Release-One stays `Ceiling-POE-VentIQ-RoomIQ`, LED-less, on `stable`); **NOT** yet imported or published by WebFlash (WebFlash-side ingest, sign, manifest, and publish are owned by the follow-up `WF-LED-001` PR in the WebFlash repo). FanTRIAC stays blocked under HW-005. Decision-doc record: `docs/product-led-preview-decision.md` (PRODUCT-005, Option C → D landed via PRODUCT-008 / PRODUCT-009; LED-preview build / release proof recorded by RELEASE-005). | Keep. |
| `docs/hardware-catalog.md` (HW-007 + HW-008 cross-link refresh) | `current` | Hardware catalog naming source-of-truth. HW-007 expanded the "Verified schematics currently available" section from two boards to five (Core, RoomIQ, AirIQ, VentIQ, LED) with links to the PDFs under `docs/hardware/schematics/` and the standalone per-board docs. HW-008 then rewrote the HW-007 / HW-008 ingest paragraph to record that the machine-readable JSON has now been refreshed (the five SKUs are `schematic_status: verified` with `schematic_file` paths under `docs/hardware/schematics/`), kept the six unverified SKUs explicit, and reiterated the guardrails: verified schematic evidence is not WebFlash-shippability, not Release-One inclusion, not FanTRIAC unblock, not mains compliance. No changes to the canonical naming table, naming rules, or `old_name` entries. | Keep. |
| `docs/release-one-hardware-audit.md` (HW-007 cross-link refresh) | `current` | Release-One hardware audit; HW-007 refreshes the `Source hardware references` table to add rows for AirIQ / VentIQ / LED with pointers to the committed PDFs and new standalone docs. The VentIQ "schematic verification pending" caveat was retained at HW-007 time and has since been retired by HW-008. FanTRIAC findings, the HW-005 missing-evidence checklist, the timing constraint, the re-verification record, and the LED policy section are all unchanged. | Keep. |
| `config/hardware-catalog.json` (HW-008 schematic_status refresh) | `current` | HW-008 aligns the machine-readable hardware catalog with the module-side schematic PDFs HW-007 committed under `docs/hardware/schematics/`. Five rows flip to `schematic_status: verified` with `schematic_file` paths under `docs/hardware/schematics/`: `S360-100` (Core), `S360-200` (RoomIQ), `S360-210` (AirIQ), `S360-211` (VentIQ), `S360-300` (LED). The remaining six rows (`S360-310` Relay, `S360-311` PWM, `S360-312` DAC, `S360-320` TRIAC, `S360-400` 240v PSU, `S360-410` PoE PSU) stay `cataloged_unverified`. HW-008 is JSON + doc cross-link only: it does **not** edit any product YAML, WebFlash wrapper, package YAML, workflow, component, header, or script; it does **not** change the Release-One config string `Ceiling-POE-VentIQ-RoomIQ`, the Release-One artifact name, the WebFlash build matrix, the WebFlash compatibility snapshot, or any product-catalog lifecycle status; it does **not** unblock FanTRIAC (HW-005 still applies; `S360-320` stays `cataloged_unverified`); it does **not** add a `LED` token to the Release-One config string (`S360-300` flips to `verified` but Sense360 LED stays excluded from Release-One); it does **not** clear the mains-voltage compliance gate (`S360-400` stays `cataloged_unverified` under COMPLIANCE-001); it does **not** resolve the Core J10 vs RoomIQ J6 pin-order discrepancy or the `GPIO14` (package) vs `IO38` (schematic) `LED_DATA` discrepancy. Validated by the new `tests/test_hardware_catalog.py`. | Keep. |
| `tests/test_hardware_catalog.py` | `current` | HW-008 stdlib `unittest` validator for `config/hardware-catalog.json`. Locks in: JSON parses; every entry has `sku` / `friendly_name` / `schematic_status`; every status is one of `verified` / `cataloged_unverified`; every `verified` entry has a `schematic_file`; every `schematic_file` path exists on disk under the repo root; `S360-100`, `S360-200`, `S360-210`, `S360-211`, `S360-300` are `verified`; `S360-320` remains not `verified` (HW-005 still blocked); `S360-400` remains not `verified` (COMPLIANCE-001 still applies); entries that are not `verified` may omit `schematic_file`. Read-only; no firmware / product / workflow change. | Keep. |
| `docs/webflash-contract.md` | `current` | Canonical WebFlash artifact/grammar/token contract. | Keep. |
| `docs/webflash-ci-alignment.md` | `current` | CI ↔ WebFlash alignment record. | Keep. |
| `docs/webflash-release-handoff.md` | `current` | Release-handoff record. | Keep. |
| `docs/webflash-release-proof.md` | `current` | ESP-006 / ESP-007 Release-One proof record (run `25763009641`) plus the LED preview proof section seeded by RELEASE-003 and backfilled by RELEASE-005. RELEASE-003 originally landed the "LED preview release proof (RELEASE-003)" section with a pending-proof table, operator runbook, and proof checklist whose dynamic fields (tag, run URL, asset size, SHA256, validator/asset-check pass states) were marked `pending`. **RELEASE-005 replaced the `pending` values with the real recorded values from the successful prerelease run:** GitHub Release <https://github.com/sense360store/esphome-public/releases/tag/v1.0.0-led-preview> (tag `v1.0.0-led-preview`, title `Sense360 LED Preview Firmware v1.0.0`, `prerelease: true`); workflow `Build & Release Firmware` run [`25918422743`](https://github.com/sense360store/esphome-public/actions/runs/25918422743) (event `release`, git SHA `4493e0c9b3914d5dfcf41f71b4129cf23cda75d2`); firmware asset `Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin` (1,135,904 bytes; SHA256 `93310d2cbc27355e399f36a232336b6b9075dacfc178d603c7a92aa1089182d3`); uploaded asset set `.bin`, `checksums-sha256.txt`, `checksums-md5.txt`, `manifest.json`; release-body validation passed; release-asset assertion passed; WebFlash-import source URL recorded; checklist boxes ticked; status flipped from "pending — RELEASE-003 not yet proven" to "proven — RELEASE-005 records the LED preview prerelease proof; ready for WebFlash import planning". A new "What RELEASE-005 does NOT do" guardrail block sits alongside the original RELEASE-003 guardrails: RELEASE-005 is documentation-only — it does **not** generate firmware, modify any release asset, change the artifact filename / version / channel, promote `Ceiling-POE-VentIQ-RoomIQ-LED` to `production` / `stable`, add `LED` to stable Release-One (`Ceiling-POE-VentIQ-RoomIQ`, `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag `v1.0.0`), import into WebFlash (owned by the follow-up `WF-LED-001` PR in the WebFlash repo), unblock FanTRIAC (HW-005 stays open; `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays `blocked`; the LED preview catalog entry still carries `blocked_modules: ["FanTRIAC"]`), or modify any `config/*`, `products/*`, `products/webflash/*`, `packages/*`, `.github/workflows/*`, `scripts/*`, `tests/*`, `components/*`, or `include/*` file. Cross-linked from `docs/product-led-preview-decision.md` (PRODUCT-009 outstanding-proof paragraph now reads "recorded by RELEASE-005") and `docs/product-onboarding.md` (LED guardrail bullet). | Keep. |
| `docs/installation.md` | `current` | Manual/custom install path, pinned to `Ceiling-POE-VentIQ-RoomIQ`. Contains legacy Mini snippet (see "Legacy docs/examples"). | Keep; tweak the Mini snippet in CLEANUP-005. |
| `docs/product-matrix.md` | `current` | Frames `Ceiling-POE-VentIQ-RoomIQ` as the Release-One config but still includes a `Bathroom Pro` row at line 357 and "Bathroom Pro (additional)" header at line 366. | Reword in CLEANUP-003. |
| `docs/hardware-catalog.md` | `current` | Maps `Sense360 LED` (canonical) / `LED Ring` (old_name), and `Sense360 VentIQ` (canonical) / `Bathroom Pro` (old_name). | Keep. |
| `docs/manual-user-walkthrough.md` | `current` | Explicitly states "Sense360 LED is excluded from Release-One firmware." | Keep. |
| `docs/configuration.md` | `current` | Customer snippets pin `ref: v1.0.0`. Mini AirIQ/Presence variants described as "Product Variants" without a Release-One pointer. | Keep; add a Release-One pointer in CLEANUP-005. |
| `docs/development.md` | `current` | Lists Mini variants as locally testable; legacy-compatible. | Keep. |
| `docs/repo-structure-audit.md` | `current` | Companion classification doc (ESP-009 / ESP-010); already flags `docs/*.html` as "audit follow-up". | Keep. |
| `README.md` | `current` | Header, Release-One section, WebFlash taxonomy, FanTRIAC-excluded callout. | Keep. |
| `CHANGELOG.md` | `current` (with one `stale` paragraph) | The `Unreleased / Changed` REL-001 bullet is correct. The `Unreleased / Added` "WebFlash compatibility contract" bullet at lines 25–34 still names `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` as the release-one config, contradicting REL-001 above it. | Record only — do **not** fix in this PR. Defer to CLEANUP-002. |
| `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml` | `blocked-reference` | FanTRIAC product YAML; not in build matrix; retained per HW-005. | Keep. |
| `products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml` | `blocked-reference` | FanTRIAC WebFlash wrapper; retained per HW-005. | Keep. |
| `packages/expansions/fan_triac.yaml` | `blocked-reference` | FanTRIAC driver package, BLOCKED / UNVERIFIED banner. | Keep. |
| `config/hardware-catalog.json` (Sense360 TRIAC row) | `blocked-reference` | Cataloged row for S360-320 (`old_name: TRIAC_Board`); retained. | Keep. |
| FanTRIAC explainer paragraphs in `README.md`, `docs/release-one.md`, `docs/release-one-hardware-audit.md`, `docs/webflash-contract.md`, `docs/webflash-ci-alignment.md`, `docs/webflash-release-handoff.md`, `docs/product-matrix.md`, `docs/installation.md` | `blocked-reference` | Explicitly call FanTRIAC excluded / blocked. | Keep. |
| `products/sense360-core-*.yaml` (15 files: c-poe, c-pwr, c-usb, v-c-poe, v-c-pwr, v-c-usb, v-w-poe, v-w-pwr, v-w-usb, w-poe, w-pwr, w-usb, ceiling, ceiling-bathroom, ceiling-presence, voice-ceiling, voice-wall, wall, wall-presence) | `legacy-compatible` | Pre-WebFlash product YAMLs; still referenced by `ci-validate-configs.yml` matrix discovery and `docs/development.md`. Inline `ref: v2.2.0` / `ref: v3.0.0` comments are stale (lines 21, 24, 26, 28, 29, 103). | Keep YAMLs. Defer doc-comment fix to CLEANUP-002. |
| `products/sense360-mini-*.yaml` (10 files) | `legacy-compatible` | Pre-WebFlash Mini product YAMLs; still referenced by `ci-validate-configs.yml` and `docs/development.md`. `ref: v3.0.0` comments at lines 145, 258, 358, 474 are stale. | Keep YAMLs. Defer doc-comment fix to CLEANUP-002. |
| `products/sense360-poe.yaml`, `products/sense360-fan-pwm.yaml` | `legacy-compatible` | Legacy single-purpose YAMLs; still validated by the broad sweep. | Keep. |
| `packages/base/**` | `legacy-compatible` | Loaded by every product; reachable as `github://sense360store/esphome-public/packages/base/...` from customer ESPHome configs. | Keep. Treat as public API. |
| `packages/features/**` | `legacy-compatible` | Includes `ceiling_halo_leds.yaml`, `ceiling_led_ring_air_quality.yaml`, `airiq_*`, `bathroom_*`, `comfort_*`, `presence_*`, fan-control profiles. Used by both Release-One and legacy products, and reachable as remote packages. | Keep. Treat as public API. |
| `packages/hardware/**` | `legacy-compatible` | Includes `led_ring_ceiling.yaml`, `led_ring_mic_*.yaml`, `led_ring_wall.yaml`, `sense360_core_*.yaml`, `power_*.yaml`, `presence_*.yaml`, `mini_onboard_sensors.yaml`. Used by Release-One and legacy products. | Keep. Treat as public API. |
| `packages/expansions/**` (excluding `fan_triac.yaml`) | `legacy-compatible` | Includes `airiq_*`, `bathroom.yaml`, `comfort_*`, `fan_*`, `gpio_expander_sx1509.yaml`, `presence_*`. | Keep. Treat as public API. |
| `packages/README.md` | `legacy-compatible` | Token list aligned with WebFlash; legacy section headers (Comfort/Presence/Bathroom/Fan) flagged with WebFlash equivalents. | Keep. |
| `packages/SENSE360_MODULES.md` | `legacy-compatible` / `candidate-for-removal` | Long Mini/AirIQ inventory; only referenced by `packages/README.md`. Not part of WebFlash flow. | Keep for now; revisit in CLEANUP-006 after the user-facing docs sweep lands. |
| `base/`, `features/`, `hardware/` (top-level symlinks) | `legacy-compatible` | Symlinks to `packages/base`, `packages/features`, `packages/hardware`. Likely targeted by remote-package URLs that omit the `packages/` prefix. | Keep. Do not remove without first auditing remote-package URL shapes. |
| `components/ld2412/`, `components/ld2450/`, `components/ld24xx/` | `legacy-compatible` | ESPHome external components, loaded via `packages/base/external_components.yaml` (a `github://` source pinned to this repo). | Keep. Treat as public API. |
| `include/sense360/` (+ `include/README.md`) | `legacy-compatible` | C++ headers consumed via `github://sense360store/esphome-public/include/sense360/*` (see `examples/custom-with-remote-headers.yaml:22-24`, `tests/INTEGRATION_GUIDE.md:32-38`). | Keep. Treat as public API. |
| `tests/generate_test_configs.py`, `tests/batch_validate_esphome.py`, `tests/find_duplicate_entities.py`, `tests/quick_check_duplicates.sh`, `tests/unit/**`, `tests/esphome/**`, `tests/README.md`, `tests/INTEGRATION_GUIDE.md`, `tests/Makefile` | `legacy-compatible` | Broad-sweep test infrastructure used by `ci-validate-configs.yml`. Not Release-One-specific but still load-bearing for the manual sweep. | Keep. |
| `examples/customer-basic.yaml` | `legacy-compatible` | Customer config example; already pinned to `ref: v1.0.0`. Long AirIQ-centric phrasing without a VentIQ/Release-One pointer. | Keep; refresh wording in CLEANUP-005. |
| `examples/custom-with-remote-headers.yaml` | `legacy-compatible` | Documents the `github://...` headers usage pattern (currently pinned `@v2.0.0`). | Keep. Consider pinning to a Release-One tag in CLEANUP-006 once the C++ header API is confirmed in `v1.0.0`. |
| `examples/secrets.yaml.template` | `legacy-compatible` | Example secrets file. | Keep. |
| `secrets.example.yaml` | `legacy-compatible` (with `stale` comments) | Lines 42 and 50 still describe MQTT as "required for AirIQ MQTT publishing" / "AirIQ-specific MQTT substitutions". Does not mention VentIQ/RoomIQ. | Keep file; reword comments in CLEANUP-002. |
| `.github/workflows/ci-validate-configs.yml` | `legacy-compatible` (header `stale`) | Workflow itself is fine as the broad legacy sweep, but the file header at lines 10 ("Test all existing product configurations (31+ products)") presents it as a production gate. | Keep workflow; reword header in CLEANUP-002. |
| `docs/ci-pipeline.md` | `stale` | Line 3 "ensures all products can be compiled successfully before release". Line 110 "Complete ESPHome validation of all products". Line 125 "automatically discovers all products". Lines 27–84 frame the Mini board as the primary CI surface. Reads like the legacy-sweep workflow gates production releases. | Reword in CLEANUP-002. |
| `docs/modular-combinations.md` | `stale` | Uses `Bathroom Pro` and `LED Ring` as current-tense names across ~30 lines (50, 53, 92, 107, 171, 184, 204–207, 227–230, 253–257, 276–280, 294–295, 306–307, 419–469, 515–553, 667). `release-one-hardware-audit.md:191` explicitly forbids reusing "Bathroom Pro" in user-facing material. | Reword in CLEANUP-003. |
| `docs/product-matrix.md` | `stale` (one row + section) | Line 357 row `Sense360_Module_Bathroom_Pro` / "Sense 360 Bathroom Pro". Line 366 "Bathroom Pro (additional)" sub-header. (Rest of the doc is `current`.) | Reword in CLEANUP-003. |
| `docs/product-release-matrix.md` | `stale` | Whole doc framed at v3.0.0 / 2025-12-05. Lines 51 ("S360-LED-C / LED Ring Ceiling") and 53 ("S360-LED-W / LED Ring Wall") and 62–63 ("LED Ring Optional") use the old name. Does not mention Release-One config string or `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`. | Reword in CLEANUP-003 (apply `LED Ring` → `Sense360 LED`; add Release-One header banner). |
| `docs/board-combinations.md` | `stale` | Same family as `modular-combinations.md`: section 5 "LED Rings" (line 98), ASCII diagram (line 358), power-budget row (line 377), package-reference table (line 388) all use `LED Ring`. Bathroom Pro / AirIQ as current modules. Does not mention WebFlash config strings. | Reword in CLEANUP-003. |
| `docs/configuration.md` (Mini sections) | `stale` framing | Lines 48–89 frame Mini AirIQ / Presence variants as the primary "Product Variants" without a Release-One pointer. Lines 315–349 describe a Mini night-brightness flow. | Add a Release-One pointer / "this is a legacy-compatible Mini path" admonition in CLEANUP-005. |
| `docs/development.md` (Mini list) | `stale` framing | Lines 60, 141–148 list Mini variants as canonical local-test surface. | Add a Release-One pointer in CLEANUP-005. |
| `docs/installation.md:280-281` | `stale` framing | Mini snippet at lines 280–281 in the "Option / advanced" walkthrough. The doc header already pins Release-One, so this is minor. | Reword in CLEANUP-005. |
| `docs/architecture.html` | `stale` | References `LED Ring Ceiling` (`S360-LED-C`), `LED Ring Wall` (`S360-LED-W`); does not name Release-One config string. | See CLEANUP-004 — pick from: regenerate from Markdown, add a legacy banner, or remove only after confirming nothing serves/links these. |
| `docs/configuration.html` | `stale` | HTML snapshot whose Markdown twin (`docs/configuration.md`) has been updated; HTML still says "Mini core board" without Release-One framing. | CLEANUP-004 decision. |
| `docs/index.html` | `stale` | HTML landing snapshot, not linked from any `*.md`, `*.yaml`, `*.py`, or workflow inside the repo (confirmed by grep). | CLEANUP-004 decision. |
| `docs/installation.html` | `stale` | HTML twin of an updated Markdown (`docs/installation.md`). | CLEANUP-004 decision. |
| `docs/product-guide.html` | `stale` | References Sense360 Mini as the primary product. | CLEANUP-004 decision. |
| `docs/technical-reference.html` | `stale` | "LED Rings" section (lines 313, 439, 452, 458, 728). | CLEANUP-004 decision. |
| `tests/INTEGRATION_GUIDE.md` | `stale` framing | Pins `@v2.0.0` and `ref: v2.0.0` for the C++ header API. Header API is still legacy-compatible, but the version reference is older than `v1.0.0` Release-One. | Pin to a Release-One-aware tag in CLEANUP-006. |
| `scripts/scaffold_product.py` (PRODUCT-010) | `current` | PRODUCT-010 conservative product scaffold report generator. Read-only / dry-run: emits a Markdown report to stdout and never writes any file. Parses the proposed config string against `config/webflash-compatibility.json` (mounting / power / modules / forbidden tokens / mutex / fan-driver "max one of" / FanDAC↔AirIQ); cross-references `config/product-catalog.json` and `config/webflash-builds.json` for duplicate detection; validates every `--hardware slot=SKU` against `config/hardware-catalog.json`; derives the canonical WebFlash artifact name via `scripts/product_name_mapper.py` (read-only import). Allowed scaffold statuses: `compile-only`, `hardware-pending`, `preview`, `blocked`. Rejects `production`, `deprecated`, `removed`, `legacy-compatible`. Forces any FanTRIAC-bearing config to `--status blocked --blocker HW-005`. Does **not** write `config/product-catalog.json`, `config/webflash-builds.json`, `config/webflash-compatibility.json`, `config/hardware-catalog.json`, any product YAML, any WebFlash wrapper, any package, any workflow, any component, any header, or any test. Does **not** generate firmware, draft release notes, create GitHub releases, or import into WebFlash. Does **not** scaffold a production entry, unblock FanTRIAC, change LED status, change Release-One, or change mains-voltage compliance. | Keep. |
| `tests/test_scaffold_product.py` (PRODUCT-010) | `current` | Stdlib `unittest` suite for `scripts/scaffold_product.py`. Covers: valid compile-only happy path; validation-commands section present; do-not-change-guardrails section present; invalid module / mounting tokens; AirIQ vs VentIQ mutex; future tokens (LED / FanRelay / FanPWM / FanDAC / AirIQ) parse cleanly; duplicate catalog entry; unknown hardware SKU; `production` / `legacy-compatible` status rejection; preview with `--channel stable` rejection; preview `--webflash-build-matrix` without `--webflash-wrapper` rejection; preview must not claim a Release-One required config; preview catalog-only happy path; FanTRIAC compile-only rejection / FanTRIAC blocked with `HW-005` accepted / FanTRIAC blocked with wrong blocker rejected; compile-only must not request build matrix; hardware-pending requires `--missing-hardware-evidence`; `products/webflash/*` rejected as `--product-yaml`; read-only invariant (no fixture file is mutated by a run). Uses synthetic JSON fixtures via the script's `--catalog` / `--builds` / `--compat` / `--hardware-catalog` override flags so the real catalog state cannot influence the assertions. | Keep. |
| `docs/product-scaffold-generator.md` (PRODUCT-010) | `current` | PRODUCT-010 workflow doc for `scripts/scaffold_product.py`. Explains the conservative-by-default principle (dry-run, no production, no build-matrix by default, no firmware, no release artifacts, no WebFlash import, human review required); enumerates the allowed scaffold statuses and per-status required flags; gives worked invocations for compile-only / blocked-FanTRIAC / preview-catalog-only / preview-with-build-matrix; documents the Markdown report structure and exit codes; states explicitly that the tool does not write `config/*.json`, product YAML, wrapper YAML, `product_name_mapper.py`, `validate_product_catalog_consistency.py`, packages, workflows, components, headers, or tests; does not generate firmware or release notes; does not unblock FanTRIAC; does not change Release-One or the LED preview catalog entry or the mains-voltage compliance status. Cross-linked from `docs/product-onboarding.md` (step 4) and `docs/preview-to-stable-promotion-gates.md` (See also). | Keep. |
| Backup / tmp files | `dead` (none found) | `find . -name '*.bak' -o -name '*.orig' -o -name '*~' -o -name '*.tmp'` returns no matches. | None. |

## Stale Release-One references

These are repo locations whose wording contradicts the current Release-One
source of truth. Every entry in this section is **doc-only** — none of them
require firmware or workflow logic changes.

- `CHANGELOG.md` lines 25–34 (`Unreleased / Added` "WebFlash compatibility
  contract" bullet). Still says the release-one config is
  `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`, contradicting the REL-001 Changed
  bullet at lines 11–22 immediately above which pins
  `Ceiling-POE-VentIQ-RoomIQ`. Also lines 32–34 ("Release-One product YAML…
  matches `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`…") and line 46
  ("`Sense360-Ceiling-POE-VentIQ-FanTRIAC-RoomIQ-v1.0.0-stable.bin`").
  *Per user instruction, this PR records the issue only and does not fix
  it. Resolution belongs to CLEANUP-002.*
- `.github/workflows/ci-validate-configs.yml:10` — header bullet "Test all
  existing product configurations (31+ products)" presents this workflow
  as the Release-One gate. It is in fact the broad legacy sweep.
- `docs/ci-pipeline.md:3` — "ensures all products can be compiled
  successfully before release". `docs/ci-pipeline.md:110` — "Complete
  ESPHome validation of all products". `docs/ci-pipeline.md:125` — "The
  CI automatically discovers all products". Same framing problem as the
  workflow header.
- `secrets.example.yaml:42` and `secrets.example.yaml:50` — describes
  MQTT as "required for AirIQ MQTT publishing" / "AirIQ-specific MQTT
  substitutions". Release-One is VentIQ, not AirIQ; these comments need
  to either drop the "AirIQ" framing or call out that the same vars are
  used for VentIQ too.
- `products/sense360-core-*.yaml` and `products/sense360-mini-*.yaml`
  comment headers — pinned `ref: v2.2.0` / `ref: v3.0.0` examples
  (lines 21, 24, 26, 28, 29, 103, 145, 258, 358, 474 across the affected
  files). Current Release-One tag is `v1.0.0`. Comments only; no code
  effect.

## FanTRIAC / TRIAC references

> **HW-005 re-verified: still blocked — missing evidence.** No new schematic,
> pin map, or driver evidence has landed; the `S360-320` schematic is still
> uncommitted, no SX1509 channel is assigned to `TRI_GPIO1` / `TRI_GPIO2`,
> and the placeholder GPIO5/GPIO6 substitutions still collide with RoomIQ
> J10. See
> [`docs/release-one-hardware-audit.md#fantriac-mapping-resolution`](release-one-hardware-audit.md#fantriac-mapping-resolution)
> for the full verdict, the missing-evidence checklist, and the
> re-verification record.

FanTRIAC is intentionally excluded from production Release-One while HW-005
is open. Every FanTRIAC reference in the repo is **`blocked-reference`** —
retained on purpose so the slot can be re-armed once the
`S360-320` schematic is committed and a direct-ESP32 mapping (or a
replacement non-`ac_dimmer` driver) is verified.

Authoritative explanation: see
[`docs/release-one-hardware-audit.md#fantriac-mapping-resolution`](release-one-hardware-audit.md).

Retained files:

- `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml` (carries
  `BLOCKED / UNVERIFIED — must not ship as FanTRIAC-capable` banner;
  `fallback_ssid: "S360 TRIAC BLOCKED"`; explicit comment that fixing the
  hostname was a cosmetic 31-char fix, not an unblock).
- `products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml` (explicit
  "retained in the repo for future use only" banner; not in the build
  matrix).
- `packages/expansions/fan_triac.yaml` (BLOCKED / UNVERIFIED banner and
  pin caveats; resolution pointer to the hardware audit).
- `config/hardware-catalog.json` (Sense360 TRIAC row, `friendly_name`
  + `old_name: TRIAC_Board`).
- `config/webflash-compatibility.json` (FanTRIAC remains in
  `canonical_modules`; this is correct — the token is still a valid
  WebFlash module, just not part of Release-One's required configs).

Retained docs that explain the exclusion (each clearly states FanTRIAC is
**not** in Release-One):

- `README.md` ("FanTRIAC excluded from production Release-One" callout).
- `docs/release-one.md` (top-of-doc admonition + Files table).
- `docs/release-one-hardware-audit.md` (full HW-005 row, FanTRIAC mapping
  resolution section).
- `docs/webflash-contract.md` (FanTRIAC token remains valid; production
  exclusion called out).
- `docs/webflash-ci-alignment.md` (FanTRIAC admonition).
- `docs/webflash-release-handoff.md` (FanTRIAC admonition).
- `docs/product-matrix.md`, `docs/installation.md` (FanTRIAC admonitions).

Test-side anchors that hold this contract in place:

- `tests/test_webflash_compatibility.py` (asserts `FanTRIAC` is in
  `canonical_modules`).
- `tests/test_validate_webflash_release_notes.py:30,137` (release-body
  text asserts "FanTRIAC is excluded from production Release-One while
  HW-005 is open").
- `tests/test_webflash_artifact_naming.py:21-23` (commentary that
  FanTRIAC is retained as a blocked/reference file).
- `tests/validate_webflash_builds.py` (FanTRIAC is one of the four
  permitted `FAN_DRIVER_TOKENS`).
- `scripts/product_name_mapper.py:35-36,46,173,176` (FanTRIAC mapping
  kept with explicit "intentionally excluded" comment).

**Recommendation: keep all FanTRIAC artifacts and references untouched.**
No FanTRIAC cleanup belongs in this audit-only PR or in CLEANUP-002 /
CLEANUP-003. FanTRIAC is unblocked only by HW-005, not by repo cleanup.

## LED / LED Ring references

Two distinct things to keep straight:

1. **Sense360 LED (S360-300)** is the canonical name. `LED Ring` is the
   **old name**, preserved as `old_name` in
   `config/hardware-catalog.json:55` and as a labelled column in
   `docs/hardware-catalog.md:30`. `docs/release-one-hardware-audit.md`
   (Sense360 LED row, lines 131–132 and 155+) explicitly applies "Option A":
   remove the LED package includes from Release-One YAML so the binary
   matches the LED-less WebFlash config string. The LED packages remain in
   the repo for other products and for a future LED-bearing config string
   such as `Ceiling-POE-VentIQ-RoomIQ-LED`.
2. **LED token** is not in the Release-One WebFlash config string
   `Ceiling-POE-VentIQ-RoomIQ`. It is still a valid WebFlash module per
   `config/webflash-compatibility.json:14` (`canonical_modules` includes
   `LED`).

Status per location:

| Path | Status | Notes |
|---|---|---|
| `packages/hardware/led_ring_ceiling.yaml`, `led_ring_wall.yaml`, `led_ring_mic_ceiling.yaml`, `led_ring_mic_wall.yaml` | `legacy-compatible` | LED package YAMLs; consumed by non-Release-One products and reachable as remote packages. The filenames themselves use the old `led_ring_*` naming, but renaming would break customer remote-package URLs. Keep filenames. |
| `packages/features/ceiling_led_ring_air_quality.yaml`, `packages/features/ceiling_halo_leds.yaml` | `legacy-compatible` | Feature-side LED packages used by Core ceiling products. Keep. |
| `features/`, `hardware/` symlinks (resolve into `packages/...`) | `legacy-compatible` | Same LED files surfaced via the short-form path. Keep. |
| `products/sense360-core-ceiling.yaml`, `sense360-core-ceiling-presence.yaml`, `sense360-core-ceiling-bathroom.yaml`, `sense360-core-wall.yaml`, `sense360-core-wall-presence.yaml`, `sense360-core-voice-ceiling.yaml` | `legacy-compatible` | Headers describe "LED Ring: Halo LED for visual feedback" using the legacy name. Acceptable as YAML-internal comments. |
| `products/sense360-ceiling-poe-ventiq-roomiq.yaml` | `current` | Comment block at lines 121–146 explicitly notes Sense360 LED is **not** included and explains the policy. Aligned. |
| `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml` | `blocked-reference` | Same LED-not-included comment block; aligned. |
| `config/hardware-catalog.json` (Sense360 LED row, lines 52–55) | `current` | Canonical name + `old_name: LED Ring`; correct. |
| `docs/hardware-catalog.md:30` | `current` | Canonical-name table; calls `LED Ring` "old name". Correct. |
| `docs/release-one-hardware-audit.md` (Sense360 LED row, "Sense360 LED policy" section) | `current` | Authoritative explanation of the Option-A removal. |
| `docs/release-one.md:51-110-205` | `current` | Reiterates the LED exclusion. |
| `docs/manual-user-walkthrough.md:181` | `current` | Plain statement that Sense360 LED is excluded from Release-One firmware. |
| `docs/modular-combinations.md` (LED Ring sections), `docs/board-combinations.md` (Section 5, line 98 etc.), `docs/product-release-matrix.md` (S360-LED-C / S360-LED-W rows) | `stale` | Use `LED Ring` as the current-tense product name and do not flag Release-One LED exclusion. |
| `docs/product-matrix.md` (LED Rings section, lines 50, 65, 95, 261, 270, 280, 284, 684, 722) | `stale` framing | Heading "LED Rings" / "Standard LED Ring (Ceiling)" — same canonical-name issue. |
| `docs/configuration.md:317` | `stale` framing | Calls the Mini LED package "the Mini LED package" — Mini-specific, not a Release-One claim, but the surrounding section frames Mini as primary. |
| `docs/architecture.html`, `docs/product-guide.html`, `docs/technical-reference.html` | `stale` | HTML snapshots that still call out `LED Ring Ceiling`/`LED Ring Wall`. |
| `CHANGELOG.md:151` ("Ceiling LED Ring: Air quality visualization for ceiling-mounted devices") | `legacy-compatible` | Historical changelog entry; should not be rewritten. |

**Recommendation:** in CLEANUP-003, replace "LED Ring" → "Sense360 LED" in
user-facing docs (`modular-combinations.md`, `product-matrix.md`,
`board-combinations.md`, `product-release-matrix.md`) and add a sentence
explaining Release-One does not carry an LED. **Do not rename**
`led_ring_*.yaml` package filenames, the canonical-name table column in
`docs/hardware-catalog.md`, or the `old_name` field in
`config/hardware-catalog.json`.

## Legacy product YAMLs

These predate the WebFlash matrix but are still load-bearing:

- They are validated by `.github/workflows/ci-validate-configs.yml` via
  dynamic product discovery (`find products/ -name "*.yaml" -type f !
  -name "secrets.yaml"`).
- They are exercised by `tests/generate_test_configs.py` and the broader
  unit/integration tests.
- They are listed by name in `docs/development.md` and `docs/ci-pipeline.md`
  as Mini-board references.
- They may be referenced by external customers via
  `github://sense360store/esphome-public/products/...` URLs.

Files in scope:

```
products/sense360-core-c-poe.yaml
products/sense360-core-c-pwr.yaml
products/sense360-core-c-usb.yaml
products/sense360-core-v-c-poe.yaml
products/sense360-core-v-c-pwr.yaml
products/sense360-core-v-c-usb.yaml
products/sense360-core-v-w-poe.yaml
products/sense360-core-v-w-pwr.yaml
products/sense360-core-v-w-usb.yaml
products/sense360-core-w-poe.yaml
products/sense360-core-w-pwr.yaml
products/sense360-core-w-usb.yaml
products/sense360-core-ceiling.yaml
products/sense360-core-ceiling-bathroom.yaml
products/sense360-core-ceiling-presence.yaml
products/sense360-core-voice-ceiling.yaml
products/sense360-core-voice-wall.yaml
products/sense360-core-wall.yaml
products/sense360-core-wall-presence.yaml
products/sense360-mini-airiq.yaml
products/sense360-mini-airiq-basic.yaml
products/sense360-mini-airiq-advanced.yaml
products/sense360-mini-airiq-ld2412.yaml
products/sense360-mini-full-ld2412.yaml
products/sense360-mini-presence.yaml
products/sense360-mini-presence-basic.yaml
products/sense360-mini-presence-advanced.yaml
products/sense360-mini-presence-ld2412.yaml
products/sense360-mini-presence-advanced-ld2412.yaml
products/sense360-poe.yaml
products/sense360-fan-pwm.yaml
```

**Recommendation:** classify all of these as `legacy-compatible`. Keep
files as-is. Only the inline `ref: v2.2.0` / `ref: v3.0.0` comment hints
are stale; fix those in CLEANUP-002 alongside the other doc-only rewords.
**Do not** rename, restructure, or delete these YAMLs in any of the
follow-up cleanup PRs without first auditing customer remote-package
URLs.

**Status:** PRODUCT-002 has applied this classification in
[`config/product-catalog.json`](../config/product-catalog.json) — every
top-level product YAML listed above now has a `status: legacy-compatible`
catalog entry with `webflash_build_matrix: false`, no `config_string`, no
`artifact_name`, and a `legacy_config_id` equal to the YAML basename
(without `.yaml`).
[`tests/test_product_catalog.py`](../tests/test_product_catalog.py) now
enforces that every top-level product YAML is cataloged, that no catalog
`product_yaml` points at a `products/webflash/*` wrapper, that
`legacy_config_id` values are unique and disjoint from WebFlash
`config_string` values, and that `legacy-compatible` and `blocked`
entries carry no `artifact_name`. `legacy-compatible` does **not** mean
WebFlash-shippable: [`config/webflash-builds.json`](../config/webflash-builds.json)
remains the authoritative WebFlash build matrix, and PRODUCT-002 does not
add any product to it. Release-One remains the only `production` entry;
FanTRIAC (`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`) remains `blocked` per
HW-005; Sense360 LED remains excluded from Release-One.

## Legacy docs/examples

| Path | Issue | Recommended action |
|---|---|---|
| `docs/modular-combinations.md` | `Bathroom Pro` and `LED Ring` as current product names across ~30 lines. Does not mention WebFlash config strings or Release-One. | CLEANUP-003: replace with `Sense360 VentIQ` / `Sense360 LED`; add a Release-One header banner. Keep the combination tables. |
| `docs/board-combinations.md` | Section 5 "LED Rings", `Bathroom AirIQ Pro` / "Bathroom Pro" in module tables, no WebFlash framing. | CLEANUP-003. |
| `docs/product-release-matrix.md` | Pinned to release `3.0.0` / `2025-12-05`; uses `LED Ring Ceiling` / `LED Ring Wall`; no Release-One framing. | CLEANUP-003: update release header to v1.0.0, replace `LED Ring` with `Sense360 LED`. |
| `docs/product-matrix.md` lines 357, 366 | Single `Bathroom Pro` row in the SKU table and "Bathroom Pro (additional)" sub-section. (Rest of the doc is current.) | CLEANUP-003: replace with `Sense360 VentIQ`. |
| `docs/configuration.md` lines 48–89, 315–349 | Frames the Mini AirIQ / Presence variants as the primary "Product Variants" without a Release-One pointer. | CLEANUP-005: add a "Production Release-One ships `Ceiling-POE-VentIQ-RoomIQ`; this section documents legacy-compatible Mini variants" admonition; keep content. |
| `docs/development.md` lines 60, 141–148 | Lists Mini product YAMLs as the canonical local-test surface. | CLEANUP-005: add a Release-One pointer; keep the Mini list. |
| `docs/installation.md` lines 280–281 | Mini snippet in the advanced walkthrough; doc header already pins Release-One. | CLEANUP-005: minor reword. |
| `docs/ci-pipeline.md` | Repeatedly frames the broad sweep as the production release gate (see "Stale Release-One references"). | CLEANUP-002: reword. |
| `examples/customer-basic.yaml` | Long AirIQ-centric template; does not mention VentIQ or Release-One. `ref: v1.0.0` is correct. | CLEANUP-005: add a banner pointing to Release-One; keep the template body. |
| `examples/custom-with-remote-headers.yaml` | Pinned `@v2.0.0` for the C++ header API. Still legacy-compatible, but older than `v1.0.0`. | CLEANUP-006: pin to a Release-One-aware tag after verifying header API in `v1.0.0`. |
| `secrets.example.yaml` lines 42, 50 | "Required for AirIQ MQTT publishing" / "AirIQ-specific MQTT substitutions". | CLEANUP-002: reword (Release-One is VentIQ; the same vars apply). |
| `tests/INTEGRATION_GUIDE.md` lines 32–38 | Pins `@v2.0.0` / `ref: v2.0.0` for the C++ header example. | CLEANUP-006: same as `custom-with-remote-headers.yaml`. |
| `CHANGELOG.md` historical entries (3.0.0 / older) | Use legacy terminology (`Ceiling LED Ring`, `AirIQ 4-LED Status`, `Bathroom Pro`, generic `Fan`). | **No action.** Historical CHANGELOG entries describe the state at the time of release and should not be rewritten. |
| `packages/SENSE360_MODULES.md` | Mini-centric module inventory; not part of the WebFlash flow. | Defer. Revisit in CLEANUP-006. |

## Workflow/CI wording

| Path | Issue | Recommended action |
|---|---|---|
| `.github/workflows/ci-validate-configs.yml:10` | Header bullet "Test all existing product configurations (31+ products)" presents the workflow as the production gate. | CLEANUP-002: doc-only reword inside the workflow header comment; **do not** touch the workflow logic, triggers, jobs, or path filters. |
| `.github/workflows/ci-validate-configs.yml:32,40` | Path filters reference the workflow file itself — fine, leave as-is. | None. |
| `.github/workflows/validate.yml:13` | Comment "For full ESPHome compilation tests, see ci-validate-configs.yml" — accurate. | None. |
| `.github/workflows/firmware-build-release.yml` | Header comments describe the Release-One build/release flow accurately. | None. |
| README badge for `ci-validate-configs.yml` | Badge label "CI - Validate Firmware Configs" is accurate but currently implies it gates production releases. | CLEANUP-002: relabel badge or add a one-line caption ("broad legacy sweep — not the Release-One gate"). |
| `docs/ci-pipeline.md` | Whole-document framing — see "Stale Release-One references". | CLEANUP-002: reframe as "broad legacy sweep + Mini-board QA companion to `firmware-build-release.yml`". |

**Do not** in any follow-up PR:

- Change `.github/workflows/firmware-build-release.yml` job logic, build
  matrix, artifact naming, or release-asset attachment steps.
- Change `.github/workflows/ci-validate-configs.yml` job logic, dynamic
  product discovery (`find products/ -name '*.yaml' …`), path filters,
  or workflow triggers.
- Change `.github/workflows/validate.yml`.
- Remove or rename `ci-validate-configs.yml`.

## Public API / remote package risk

The following paths are reachable from customer ESPHome configurations via
`github://sense360store/esphome-public/...` URLs (or expected to be, based on
the public examples that demonstrate the pattern). They must be treated as
public API.

| Path | Evidence |
|---|---|
| `packages/base/**` | Required by every Release-One and legacy product; loaded by `external_components.yaml`. |
| `packages/features/**` | Loaded by every product YAML; example feature paths appear in `packages/README.md` snippets pinned `ref: v1.0.0`. |
| `packages/hardware/**` | Same. |
| `packages/expansions/**` | Same. |
| `base/`, `features/`, `hardware/` (top-level symlinks) | Provide a `github://.../base/...` short-form path. Likely already linked from customer configs. |
| `components/ld2412/`, `components/ld2450/`, `components/ld24xx/` | Loaded as ESPHome external components via `packages/base/external_components.yaml` (a `git` source pinning this repo). Documented in `docs/repo-structure-audit.md:51` as public API. |
| `include/sense360/**` | Consumed via `github://sense360store/esphome-public/include/sense360/*` — proven by `examples/custom-with-remote-headers.yaml:22-24` and `tests/INTEGRATION_GUIDE.md:32-38`. |
| `products/sense360-core-*.yaml`, `products/sense360-mini-*.yaml`, `products/sense360-poe.yaml`, `products/sense360-fan-pwm.yaml` | May be referenced as `github://sense360store/esphome-public/products/...` by manual users. |
| `scripts/product_name_mapper.py` | Used by `firmware-build-release.yml`. Public-ish: removing a mapping breaks unmapped-product fallback. |

Treat all of these as **do not rename / do not delete** in any cleanup PR
without a separate deprecation cycle and a release-note callout.

## Recommended cleanup PRs

Sequenced so the lowest-risk doc-wording fixes land first and the
content-change PRs land after:

1. **CLEANUP-002 — Doc-wording sync to Release-One.** Pure wording fixes,
   no logic changes.
   - `CHANGELOG.md` lines 25–34 and 46: replace
     `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` mentions in the
     `Unreleased / Added` block with `Ceiling-POE-VentIQ-RoomIQ`, or
     re-attribute those Added bullets as historical-context entries.
   - `.github/workflows/ci-validate-configs.yml` header comment (lines
     1–21): reword to "broad legacy sweep + Mini-board QA companion",
     drop "(31+ products)" framing as a release gate.
   - `docs/ci-pipeline.md` lines 3, 110, 125, 27–84: reframe so it does
     not imply the broad sweep gates production releases.
   - `secrets.example.yaml` lines 42, 50: replace AirIQ-only framing
     with a VentIQ/AirIQ-shared note.
   - `products/sense360-core-*.yaml`, `products/sense360-mini-*.yaml`
     comment headers: replace stale `ref: v2.2.0` / `ref: v3.0.0`
     example pins with `ref: v1.0.0`. Comments only — do not touch
     `substitutions` or `packages` blocks.
   - README badge caption for `ci-validate-configs.yml`.

2. **CLEANUP-003 — Legacy-naming docs sweep.** Apply the
   canonical → old-name mapping in user-facing docs.
   - `docs/modular-combinations.md`, `docs/board-combinations.md`,
     `docs/product-matrix.md` (line 357 + line 366),
     `docs/product-release-matrix.md`: replace `Bathroom Pro` →
     `Sense360 VentIQ` and `LED Ring (Ceiling|Wall)` →
     `Sense360 LED (Ceiling|Wall)`. Add a Release-One header banner
     stating that none of these docs override
     `Ceiling-POE-VentIQ-RoomIQ`.
   - Keep the canonical-name table column in
     `docs/hardware-catalog.md:30`, the `old_name` field in
     `config/hardware-catalog.json`, and the `led_ring_*` filenames in
     `packages/hardware/`. These are part of public API or public
     reference.

3. **CLEANUP-004 — `docs/*.html` decision.** Six files:
   `docs/architecture.html`, `docs/configuration.html`,
   `docs/index.html`, `docs/installation.html`,
   `docs/product-guide.html`, `docs/technical-reference.html`.
   These are stale snapshots whose Markdown twins (`configuration.md`,
   `installation.md`) have been updated. Recommended decision matrix:
   - If an HTML pipeline exists outside this repo that regenerates these
     from the Markdown, regenerate.
   - Otherwise, prepend a one-line legacy banner to each HTML head
     section pointing to the Markdown source-of-truth.
   - Only consider removal after confirming the files are not served by
     a Pages / docs site and not linked from any external resource. No
     internal `*.md`, `*.yaml`, `*.py`, or workflow inside the repo
     links these HTML files (the only references are inside the HTML
     files themselves, plus a follow-up note in
     `docs/repo-structure-audit.md`).

4. **CLEANUP-005 — Examples / Mini section refresh.** Doc framing only.
   - `examples/customer-basic.yaml`: add a "this is a customer template;
     production Release-One ships `Ceiling-POE-VentIQ-RoomIQ`" banner.
   - `docs/configuration.md` lines 48–89, 315–349: add a Release-One
     pointer to the Mini section; keep content.
   - `docs/development.md` lines 60, 141–148: add a Release-One pointer
     to the Mini-test list.
   - `docs/installation.md:280-281`: minor reword.

5. **CLEANUP-006 — Header / version refresh.** Lowest priority.
   - `examples/custom-with-remote-headers.yaml` and
     `tests/INTEGRATION_GUIDE.md`: pin to a Release-One-aware tag after
     verifying the C++ header API is published in `v1.0.0`.
   - Consider trimming `packages/SENSE360_MODULES.md` after CLEANUP-002
     – CLEANUP-005 land.

## Do-not-delete list

These paths must **not** be deleted by any of the cleanup PRs above
without a separate, explicit deprecation cycle. Many are public-API or
remote-package surfaces, blocked-reference files retained pending
HW-005, or load-bearing for the broad legacy CI sweep.

```
products/sense360-ceiling-poe-ventiq-roomiq.yaml
products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml    # blocked-reference
products/webflash/ceiling-poe-ventiq-roomiq.yaml
products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml    # blocked-reference
products/sense360-core-*.yaml                                # legacy-compatible
products/sense360-mini-*.yaml                                # legacy-compatible
products/sense360-poe.yaml                                   # legacy-compatible
products/sense360-fan-pwm.yaml                               # legacy-compatible
packages/base/**
packages/features/**
packages/hardware/**
packages/expansions/**                                       # incl. fan_triac.yaml (blocked-reference)
packages/README.md
packages/SENSE360_MODULES.md
base/, features/, hardware/                                  # top-level symlinks (public-API short form)
components/ld2412/, components/ld2450/, components/ld24xx/
include/sense360/**, include/README.md
config/webflash-builds.json
config/webflash-compatibility.json
config/hardware-catalog.json
.github/workflows/firmware-build-release.yml
.github/workflows/ci-validate-configs.yml
.github/workflows/validate.yml
scripts/check-webflash-release-assets.py
scripts/check-no-tracked-secrets.py
scripts/product_name_mapper.py
scripts/validate-webflash-release-notes.py
tests/**                                                     # tests + generators + Makefile + READMEs
examples/customer-basic.yaml
examples/custom-with-remote-headers.yaml
examples/secrets.yaml.template
secrets.example.yaml
README.md
CHANGELOG.md
docs/release-one.md
docs/release-one-hardware-audit.md
docs/webflash-contract.md
docs/webflash-ci-alignment.md
docs/webflash-release-handoff.md
docs/webflash-release-proof.md
docs/installation.md
docs/configuration.md
docs/development.md
docs/product-matrix.md
docs/hardware-catalog.md
docs/manual-user-walkthrough.md
docs/repo-structure-audit.md
docs/hardware/s360-100-r4-core.md
docs/hardware/s360-200-r4-roomiq.md
```

## Validation

The following commands were run against the working tree after writing
this document. None of them should be affected by the addition of a
docs-only audit file, and all `current`-classified tests continue to
pass.

```
python3 tests/validate_webflash_builds.py
python3 tests/test_webflash_compatibility.py
python3 tests/test_webflash_artifact_naming.py
python3 tests/test_validate_webflash_release_notes.py
python3 tests/test_product_substitutions.py
python3 tests/test_release_one_entity_names.py
python3 tests/validate_configs.py
pre-commit run --all-files   # if available
yamllint .                   # if available
```

Results are captured in the commit body for the PR that introduces this
document.

## What this PR does NOT change

- No WebFlash config strings, artifact names, or build-matrix entries.
- No release workflow behavior, no firmware behavior, no signing or
  manifest changes.
- No edits to `products/*.yaml`, `packages/**`, `config/*.json`,
  `.github/workflows/*`, `scripts/*`, or `tests/*`.
- No FanTRIAC unblock; FanTRIAC remains excluded from production
  Release-One pending HW-005.
- No removal of LED packages or `led_ring_*.yaml` filenames; LED remains
  excluded from Release-One because the config string does not contain
  the `LED` token.
- No deletion of `docs/*.html`. The HTML decision is deferred to
  CLEANUP-004.
- No `CHANGELOG.md` edits — the stale `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`
  mention in the `Unreleased / Added` block is recorded above and
  deferred to CLEANUP-002.

## CLEANUP-003 update (legacy naming docs sweep)

This section records what CLEANUP-003 actually swept. It does **not**
rewrite the audit above. Findings and recommendations recorded earlier
in this document remain accurate; the entries below summarise the
applied changes.

### Files swept (docs/comments only)

| Path | Sweep |
|---|---|
| `docs/modular-combinations.md` | Added Release-One scope banner + legacy-naming banner. Replaced `Bathroom Pro` → `Sense360 VentIQ` in current-tense tables. Tagged `Bathroom Base` as `*(legacy, retired)*` in definition tables. Replaced LED-Ring section heading + per-row product labels with `Sense360 LED`. |
| `docs/board-combinations.md` | Added Release-One + legacy-naming banner. Replaced `Bathroom AirIQ Pro` → `Sense360 VentIQ` and tagged `Bathroom AirIQ Base` as `*(legacy, retired)*`. Replaced section 5 heading `LED Rings` → `Sense360 LED`; updated ASCII decision tree, power-budget row, and file-reference table to use `Sense360 LED` / `Sense360 VentIQ`. Updated the Example 3 `Bathroom AirIQ Pro Module` comment to call out the canonical name. |
| `docs/product-matrix.md` | Updated TOC + section heading `LED Rings` → `Sense360 LED` (anchor `#sense360-led`). Updated Step 3 heading, ASCII assembly diagram, YAML example comment, and SKU → Package mapping label. Renamed the `Bathroom Module` heading to `Sense360 VentIQ (Bathroom) Module`; renamed the SKU-row entry `Sense360_Module_Bathroom_Pro` / "Sense 360 Bathroom Pro" to `Sense360_Module_VentIQ` / "Sense360 VentIQ"; flagged `Sense360_Module_Bathroom_Base` row as `*(legacy, retired)*`. |
| `docs/product-release-matrix.md` | Refreshed the stale `v3.0.0 / 2025-12-05` release header to current Release-One v1.0.0 framing (with explicit "not a historical release matrix" caveat). Section 3 heading `LED Attachments` → `Sense360 LED Attachments`; product labels `LED Ring Ceiling/Wall` → `Sense360 LED (Ceiling)/(Wall)`. Refreshed install example refs from `v3.0.0` to `v1.0.0` and the canonical Release-One product YAML. Flagged the `S360-BATH-C` row as a legacy SKU pending a separate SKU / catalog audit. |

### Legacy aliases intentionally preserved

The following references are **clearly labelled legacy / old_name /
schematic / compatibility references** and are preserved on purpose. No
sweep was applied to them.

- `config/hardware-catalog.json` — `old_name` JSON fields (e.g.
  `"Bathroom Pro"` for `S360-211`, `"LED Ring"` for `S360-300`).
- `docs/hardware-catalog.md` — canonical-name table with "Old name"
  column (`LED Ring` / `Bathroom Pro`).
- `docs/hardware/s360-100-r4-core.md` — explicit `Old name: LED Ring`
  rows tied to schematic-level discussion.
- `docs/release-one-hardware-audit.md` — explicit "Old name: `Bathroom
  Pro`. Do not reuse `Bathroom Pro` in new user-facing material" guidance
  (and surrounding context).
- `docs/webflash-contract.md` — legacy → WebFlash mapping table
  (`Bathroom` → `VentIQ`, `LED` → S360-300, etc.).
- `docs/webflash-ci-alignment.md` — legacy-token discussion (the
  ESP-009 inventory bullet).
- `packages/README.md` — `### Bathroom (legacy → WebFlash VentIQ)`
  section header and adjacent legacy-mapping commentary.
- `docs/manual-user-walkthrough.md` — "Sense360 LED (ceiling LED ring)
  is excluded from Release-One firmware" framing.
- `CHANGELOG.md` — historical entries (3.0.0 and earlier) that mention
  `Ceiling LED Ring`, `LED ring`, `Bathroom Pro`. Historical changelog
  entries describe the state at the time of release and were not
  rewritten.
- `packages/SENSE360_MODULES.md` — register-map context (`0x59 |
  GP8403 alt, SGP40 (Bathroom)`).
- `docs/architecture.html`, `docs/configuration.html`,
  `docs/product-guide.html`, `docs/technical-reference.html` —
  HTML doc snapshots; decision deferred to CLEANUP-004.
- Package and product YAML filenames + YAML-internal comments
  (`packages/hardware/led_ring_*.yaml`,
  `packages/features/ceiling_led_ring_air_quality.yaml`,
  `packages/expansions/airiq_bathroom_*.yaml`,
  `products/sense360-core-ceiling*.yaml`, etc.) — preserved as public
  API / remote-package surface per the recommendation above.

### Bathroom Base treatment

`Bathroom Base` (`S360-BATH-B`) has **no canonical successor** in
`docs/hardware-catalog.md`. Per CLEANUP-003 decision, the term was
**not** silently collapsed into `Sense360 VentIQ`. Where it appears as a
current-tense product label in user-facing docs, it is now annotated as
a retired legacy bathroom SKU (`*(legacy, retired)*`) in the relevant
definition tables. A separate SKU / catalog audit is needed to decide
whether `Bathroom Base` should be removed from the docs entirely or
formally cataloged.

### Out of scope (unchanged by CLEANUP-003)

CLEANUP-003 is docs/comments only. The following remain untouched:

- `products/*.yaml`, `products/webflash/*.yaml`, `packages/*.yaml`.
- `config/webflash-builds.json`, `config/webflash-compatibility.json`,
  `config/hardware-catalog.json` (including `old_name` fields).
- `.github/workflows/*`, `scripts/*`, `tests/*`, `components/*`,
  `include/*`.
- File renames (none performed).
- WebFlash config strings, artifact names, build matrix, firmware
  package IDs, hardware SKUs.
- FanTRIAC blocked status (remains blocked pending HW-005).
- LED exclusion status (remains excluded from Release-One).
- HTML doc snapshots in `docs/*.html` (deferred to CLEANUP-004).

### Validation run for CLEANUP-003

The commands at the top of this document, plus the sanity greps below,
were re-run after the sweep. Results are captured in the commit body
for the CLEANUP-003 PR.

```text
grep -RIn "Celling"      README.md CHANGELOG.md docs examples packages products config tests scripts
grep -RIn "AirlQ"        README.md CHANGELOG.md docs examples packages products config tests scripts
grep -RIn "Bathroom Pro" README.md CHANGELOG.md docs examples packages products config tests scripts
grep -RIn "LED Ring"     README.md CHANGELOG.md docs examples packages products config tests scripts
```

Any remaining `Bathroom Pro` / `LED Ring` hits after the sweep are
clearly framed as legacy / old_name / schematic / compatibility /
historical references in the locations listed under "Legacy aliases
intentionally preserved" above.

## CLEANUP-004 update (HTML docs decision)

This section records what CLEANUP-004 actually did. As with the
CLEANUP-003 update above, it does **not** rewrite the audit earlier in
this document. The "Findings summary" rows at lines 169–174, the
"Recommended cleanup PRs" item at lines 476–491, the "What this PR does
NOT change" bullet at lines 602–603, the "Out of scope" bullet at
line 688, and the "Legacy aliases intentionally preserved" entry at
lines 653–655 (four HTML files deferred to CLEANUP-004) all remain
accurate as historical records; the entry below summarises the applied
change and supersedes those `CLEANUP-004 decision` placeholders.

### Decision: remove

All six `docs/*.html` files were **deleted**:

- `docs/architecture.html`
- `docs/configuration.html`
- `docs/index.html`
- `docs/installation.html`
- `docs/product-guide.html`
- `docs/technical-reference.html`

### Rationale

The "preferred — remove unused stale HTML" branch of the CLEANUP-004
decision policy applied cleanly. All four conditions held simultaneously:

1. **Not generated by any repo pipeline.** No `mkdocs.yml`,
   `_config.yml`, `package.json`, `Gemfile`, or `conf.py` exists in the
   repo. No workflow under `.github/workflows/` references `.html`, and
   no entry in `scripts/` does either.
2. **Not linked from `README.md` or any current Markdown doc.** The
   only inbound references in the repo were the HTML cluster's own
   internal cross-links (`index.html` ↔ `product-guide.html` ↔ etc.)
   and the audit-narrative mentions inside this file and
   `docs/repo-structure-audit.md`. `README.md:411-412` only links the
   Markdown twins (`docs/installation.md`, `docs/configuration.md`).
3. **Not served by any GitHub Pages / docs workflow from this repo.**
   The HTML cluster was added in a single commit titled "Add GitHub
   Pages documentation site", but GitHub Pages was never wired up here:
   no Pages config in `.github/`, no `gh-pages` branch, no deploy
   workflow. The lone `sense360store.github.io/...` link in the HTML
   pointed to the *WebFlash* repo's Pages site, not this repo's.
4. **Contradicted current Release-One Markdown.** The HTML files
   predated the Release-One framing entirely — no `Release-One` /
   `Ceiling-POE-VentIQ-RoomIQ` string in any of them; they still framed
   `Sense360 Mini` as the primary product
   (`architecture.html`, `technical-reference.html`,
   `product-guide.html`) and used the retired `LED Ring` / `S360-LED-*`
   SKU names (`architecture.html`, `technical-reference.html`).

Adding a legacy banner was the runner-up option but would have left six
stale documents in the tree and a half-broken HTML cluster pointing to
a Pages site that does not exist. Regeneration was not considered: no
generator pipeline exists in this repo, and the task explicitly
forbids inventing one in this PR.

### Markdown links repaired

None. No `.md`, `.yaml`, `.py`, or workflow file inside the repo linked
the deleted HTML files, so no Markdown link repair was required.
`README.md` and the Markdown twins (`docs/installation.md`,
`docs/configuration.md`, etc.) are unchanged. `docs/cleanup-audit.md`
(this file) and `docs/repo-structure-audit.md` retain their historical
mentions of the HTML filenames as audit-narrative; that is the intended
record of the CLEANUP-004 decision and was not rewritten.

### Out of scope (unchanged by CLEANUP-004)

CLEANUP-004 is HTML-doc removal only. The following remain untouched:

- `products/*.yaml`, `products/webflash/*.yaml`, `packages/*.yaml`.
- `config/webflash-builds.json`, `config/webflash-compatibility.json`,
  `config/hardware-catalog.json` (including `old_name` fields).
- `.github/workflows/*`, `scripts/*`, `tests/*`, `components/*`,
  `include/*`.
- WebFlash config strings, artifact names, build matrix, firmware
  package IDs, hardware SKUs.
- FanTRIAC blocked status (remains blocked pending HW-005).
- LED exclusion status (remains excluded from Release-One).
- `README.md`, current Release-One Markdown docs, and
  `docs/repo-structure-audit.md`.

### Validation run for CLEANUP-004

After the deletions the test suite listed at the top of this document
was re-run, together with the sanity greps below. Results are captured
in the commit body for the CLEANUP-004 PR.

```text
find docs -maxdepth 1 -name "*.html" -print
grep -RIn "\.html" README.md docs .github scripts package.json mkdocs.yml _config.yml 2>/dev/null || true
```

After the sweep, the `find` returns nothing and the `grep` returns only
unrelated `.html` mentions (the SemVer URL at
`docs/webflash-contract.md:53`, the googletest URL at
`tests/README.md:383`) plus the audit-narrative mentions inside this
file and `docs/repo-structure-audit.md` that record the CLEANUP-004
decision history.

## CLEANUP-005 update (examples refresh)

This section records what CLEANUP-005 actually swept. As with the
CLEANUP-003 and CLEANUP-004 updates above, it does **not** rewrite the
audit earlier in this document. The "Findings summary" rows for the
files listed below remain accurate as historical records; the entry
below summarises the applied changes and supersedes the
`Reword in CLEANUP-005` / `refresh wording in CLEANUP-005` placeholders.

### Goal

Refresh user-facing examples and Mini-centric doc sections so that
production Release-One (`Ceiling-POE-VentIQ-RoomIQ`) is the leading
default, while preserving legacy-compatible Mini / AirIQ / custom
examples as clearly-labelled alternatives.

### Files swept (docs / examples only)

| Path | Sweep |
|---|---|
| `examples/customer-basic.yaml` | Restructured: replaced the Mini-centric header with a Release-One-leading banner; flipped the active default include to `products/sense360-ceiling-poe-ventiq-roomiq.yaml` (OPTION 0); demoted the four Mini variants to commented-out alternatives (OPTIONS 1–4) explicitly labelled `legacy`; bumped `min_version` `2024.11.0` → `2025.10.0` to match Release-One; reworded the MQTT/Required-for-AirIQ framing to AirIQ / VentIQ; refreshed the bottom "Quick Start" guide so STEP 1 explains OPTION 0 vs the Mini options. Body and threshold-customisation examples preserved. |
| `examples/custom-with-remote-headers.yaml` | Prepended a top-of-file banner: "Advanced / custom example — NOT the Release-One path." Points readers at `examples/customer-basic.yaml` and `docs/release-one.md`. The `@v2.0.0` C++ header pin is **not** changed (deferred to CLEANUP-006 per the audit); the banner explains why it predates the Release-One firmware tag `v1.0.0`. |
| `examples/secrets.yaml.template` | No change. Already a 9-line pointer to `secrets.example.yaml`. |
| `secrets.example.yaml` | Reworded line-42 "MQTT CREDENTIALS (required for AirIQ MQTT publishing)" → "(required for AirIQ / VentIQ MQTT publishing)", and the line-50 "AirIQ-specific MQTT substitutions" comment → "AirIQ / VentIQ MQTT substitutions" with a Release-One note that the same vars cover both modules. No variable names changed. (This was assigned to CLEANUP-002 in the audit; bringing it forward keeps the secrets template consistent with the customer-basic example.) |
| `docs/configuration.md` | Inserted a Release-One pointer admonition before `### Product Variants`, plus a new `#### Release-One — Ceiling-POE-VentIQ-RoomIQ (Recommended)` sub-section that points at the canonical product YAML. Suffixed the four Mini/Ceiling sub-headings with `— _legacy-compatible_`. Inserted a Sense360-LED-excluded admonition before `### Night Mode and LED Controls` and suffixed `#### Mini Night Brightness` with `— _legacy-compatible (Mini board only)_`. Suffixed `#### Mini Board Default Pins` similarly and added a pointer to `docs/hardware/s360-100-r4-core.md` for Release-One pin reference. Added a "this is not the Release-One path" preamble to `### Component-Level Customization` and tagged its `sense360_core_mini.yaml` hardware line accordingly. Content (thresholds, automations, scenarios) preserved. |
| `docs/development.md` | Replaced the canonical `esphome config products/sense360-mini-airiq.yaml` example with a two-snippet pair: Release-One first (`sense360-ceiling-poe-ventiq-roomiq.yaml`), Mini second (labelled legacy). Above the "Matrix testing" list, inserted a banner clarifying that `firmware-build-release.yml` is the Release-One gate and the matrix below is the broad legacy sweep run by `ci-validate-configs.yml`. Added the Release-One YAML as the first entry in the matrix list and suffixed each Mini / Ceiling-presence entry with `— _legacy-compatible_`. List itself preserved. |
| `docs/installation.md` | Reworded the "Change Product Variant" snippet so the active uncommented file is `sense360-ceiling-poe-ventiq-roomiq.yaml` (Release-One) and the three Mini / Ceiling-presence YAMLs become commented-out alternatives flagged as legacy. Reworded the "MQTT Credentials (required for AirIQ MQTT publishing)" comment line and the matching "AirIQ-enabled product" sentence to mention `AirIQ / VentIQ`. |
| `packages/README.md` | Inserted a Release-One pointer at the top (above the existing WebFlash-compatibility note) so the package README leads with `Ceiling-POE-VentIQ-RoomIQ`. Reworded the "Using Pre-Built Products" example so the active product is `sense360-ceiling-poe-ventiq-roomiq.yaml`. Added a "this is a legacy-compatible custom build" preamble to the "Custom Module Combinations" example and inline-tagged the `airiq_ceiling.yaml` / `led_ring_ceiling.yaml` lines to call out that AirIQ + LED are not in Release-One. Section bodies preserved. |
| `packages/SENSE360_MODULES.md` | Prepended a top-of-file admonition labelling the whole document as a legacy / advanced module inventory and pointing at `docs/release-one.md` and `docs/hardware-catalog.md`. Body content (pin reference, module descriptions, examples) preserved. Defer fuller content revisit to CLEANUP-006. |

### Files not touched

- `README.md` — already leads with Release-One, the FanTRIAC-excluded
  callout, and a "Legacy Terminology" table. No CLEANUP-005-shaped edit
  needed.
- `docs/manual-user-walkthrough.md` — already pinned to Release-One with
  explicit FanTRIAC / LED exclusion language.

### Legacy aliases intentionally preserved

The following references remain on purpose, in line with the
"Legacy aliases intentionally preserved" lists for CLEANUP-003 /
CLEANUP-004:

- The four legacy Mini OPTION blocks in `examples/customer-basic.yaml`
  are kept (commented out) so users with older Mini hardware still have
  a working manual-flash template.
- The Mini sub-sections in `docs/configuration.md` and the Mini matrix
  entries in `docs/development.md` are kept (with `_legacy-compatible_`
  labels) so customers running Mini hardware can still find their docs.
- The `@v2.0.0` header pin in `examples/custom-with-remote-headers.yaml`
  is intentionally retained; the C++ header API is stable across
  `v2.0.0` and the Release-One `v1.0.0` firmware tag. Re-pinning is
  deferred to CLEANUP-006 (audit row at lines 388, 390, 503–505).
- `packages/SENSE360_MODULES.md` body content is not restructured;
  fuller revisit is deferred to CLEANUP-006 (audit row at lines 392, 506–507).
- Legacy filenames (`comfort_*.yaml`, `airiq_bathroom_*.yaml`,
  `led_ring_*.yaml`, `sense360_core_mini.yaml`, etc.) remain unchanged —
  these are public API / remote-package surfaces.

### Out of scope (unchanged by CLEANUP-005)

CLEANUP-005 is docs / examples wording only. The following remain
untouched:

- `products/*.yaml`, `products/webflash/*.yaml`, `packages/*.yaml`.
- `config/webflash-builds.json`, `config/webflash-compatibility.json`,
  `config/hardware-catalog.json` (including `old_name` fields).
- `.github/workflows/*`, `scripts/*`, `tests/*`, `components/*`,
  `include/*`.
- File renames (none performed).
- WebFlash config strings, artifact names, build matrix, firmware
  package IDs, hardware SKUs.
- FanTRIAC blocked status (remains blocked pending HW-005).
- LED exclusion status (remains excluded from Release-One).

### Validation run for CLEANUP-005

The commands at the top of this document, plus the sanity greps below,
were re-run after the sweep. Results are captured in the commit body
for the CLEANUP-005 PR.

```text
python3 tests/validate_webflash_builds.py
python3 tests/test_webflash_compatibility.py
python3 tests/test_webflash_artifact_naming.py
python3 tests/test_validate_webflash_release_notes.py
python3 tests/test_product_substitutions.py
python3 tests/test_release_one_entity_names.py
python3 tests/validate_configs.py

grep -RIn "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ" examples README.md docs packages secrets.example.yaml
grep -RIn "FanTRIAC"                            examples README.md docs packages secrets.example.yaml
grep -RIn "LED Ring"                            examples README.md docs packages secrets.example.yaml
grep -RIn "Bathroom Pro"                        examples README.md docs packages secrets.example.yaml
grep -RIn "customer-basic"                      examples README.md docs packages secrets.example.yaml
```

After the sweep, any remaining hits for `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`,
`FanTRIAC`, `LED Ring`, or `Bathroom Pro` are clearly framed as
blocked-reference, legacy / old_name, schematic, historical-context, or
compatibility references in the locations listed under "Legacy aliases
intentionally preserved" (CLEANUP-003 + CLEANUP-005) above.

## CLEANUP-006 update (remote header / pinned version refresh)

This section records what CLEANUP-006 actually swept. As with the
CLEANUP-003, CLEANUP-004, and CLEANUP-005 updates above, it does **not**
rewrite the audit earlier in this document. The "Findings summary" rows
at lines 157, 175, 388, 390, and the "Recommended cleanup PRs" entry at
lines 502–507 remain accurate as historical records; the entry below
summarises the applied changes and supersedes the
`pin to a Release-One-aware tag in CLEANUP-006` placeholders for the
files that were actually in scope for this PR.

### Goal

Audit the remote-package / external-header examples in user-facing
docs and examples, and decide whether each pinned version reference
should be re-pinned to current Release-One (`v1.0.0`), kept as an
explicit legacy example, replaced with a `<release-tag>` placeholder,
or carry a clearer pinning warning. The goal is to prevent users from
copying stale remote-package examples without understanding they are
advanced / legacy paths.

Before any edits, the C++ header API at `v1.0.0` was verified to
contain every symbol used in
`examples/custom-with-remote-headers.yaml`
(`compute_level`, `color_for_severity`, `LEVEL_POOR`,
`compute_pulse_multiplier`, `scale_color`, `classify_value`,
`PM25_GOOD` / `PM25_MODERATE` / `PM25_UNHEALTHY`, `AirQualityStatus`,
`status_to_string`, `CalibrationResult`,
`compute_single_point_calibration`, `Time`, `is_within_night_mode`),
confirmed via `git show v1.0.0:include/sense360/*.h`. Re-pinning the
example to `@v1.0.0` therefore does not break the lambda body.

### Files swept (docs / examples only)

| Path | Sweep |
|---|---|
| `examples/custom-with-remote-headers.yaml` | Re-pinned the three `includes:` lines from `@v2.0.0` to `@v1.0.0` so the example matches the Release-One firmware tag. Inserted a guidance comment block above the `includes:` list explaining how to substitute another tag for future releases, with a `@<release-tag>` placeholder shape. Updated the top-of-file banner (the "predates the Release-One firmware tag `v1.0.0`" sentence) to reflect the new pin. No lambda, sensor, package, or `min_version` changes — the `min_version: 2025.10.0` already matches Release-One. |
| `docs/product-matrix.md` | Inserted a "Legacy examples" admonition immediately above `### Example 1: Core Ceiling with Full Monitoring` (the start of the three "Configuration Examples" snippets that pin `ref: v2.2.0`). The admonition explains that the snippets intentionally pin to the historical `v2.2.0` tag for legacy Core/Wall/Bathroom package examples, that current Release-One WebFlash firmware is `Ceiling-POE-VentIQ-RoomIQ` at `v1.0.0`, and that custom / manual users should pin to a known-compatible release tag and never use `ref: main` for production. The three `ref: v2.2.0` lines themselves are **not changed** — Release-One `v1.0.0` has not been proven as the baseline for those legacy package paths, so re-pinning would be misleading. |
| `docs/installation.md` | Replaced the "Wireless Updates → Update your configuration" placeholder `ref: v2.2.0  # Change to the new version number` with `ref: <new-release-tag>  # Example: v1.0.0. Replace with the release tag you are updating to.`. This block is an update-to-future-tag instruction, not a working copy-paste, so a generic placeholder is more appropriate than a concrete pin that would re-stale next release. |

### Files not touched

The following files were inspected and confirmed to need no
CLEANUP-006-shaped edit:

- `examples/customer-basic.yaml` — `ref: v1.0.0` is already current
  Release-One; banner / structure already refreshed in CLEANUP-005.
- `README.md` — every `ref:` snippet (lines 24, 269, 303, 317, 344)
  already pins `v1.0.0`; the production-vs-`main` warning is already
  present.
- `docs/configuration.md` — every `ref:` snippet (lines 71, 93, 443,
  607) already pins `v1.0.0`; the `ref: main` development-only example
  at line 622 is explicitly framed as "Development only — never for
  production devices".
- `docs/release-one.md` — `ref: v1.0.0` snippet at line 193 already
  current.
- `docs/manual-user-walkthrough.md` — "Suggested ref / tag: `v1.0.0`"
  scope table at line 36 already current.
- `docs/development.md` — no remote-package pins in the doc body
  (only the `git clone` URL); nothing to re-pin.
- `docs/product-release-matrix.md` — `ref: v1.0.0` snippets at lines
  261 and 309 already current.
- `packages/README.md` — `ref: v1.0.0` snippets at lines 91 and 121
  already current after CLEANUP-005.
- `packages/SENSE360_MODULES.md` — no `ref:` or `@vX` pins to audit.
  The deeper "Mini-centric module inventory revisit" deferred at the
  end of CLEANUP-005 remains deferred; the task scope here was
  remote-package pins, not module-inventory rewording.
- `CHANGELOG.md` — every `ref: vX` / `ref: main` mention is historical
  narrative ("`ref: v3.0.0` with `ref: main`", etc.) describing past
  releases. Historical changelog entries are not rewritten.
- `docs/repo-structure-audit.md` — the `@v2.0.0` mentions at lines 52
  and 113 are descriptive prose recording the public-API surface at
  the time the audit was written. Historical-snapshot doc; not
  rewritten, mirroring the CLEANUP-005 pattern of leaving earlier
  audit rows intact.

### Legacy pins intentionally preserved

The following references remain on purpose, in line with the
"Legacy aliases intentionally preserved" lists for CLEANUP-003 /
CLEANUP-004 / CLEANUP-005:

- The three `ref: v2.2.0` snippets in `docs/product-matrix.md` lines
  601, 631, 661 (`Example 1: Core Ceiling with Full Monitoring`,
  `Example 2: Core Wall with All Sensors`,
  `Example 3: Core Ceiling Bathroom Installation`). Re-pinning to
  `v1.0.0` would imply Release-One `v1.0.0` has been proven against
  the legacy Core / Wall / Bathroom product YAML set, which it has
  not. Instead, a "Legacy examples" admonition was added above them.
- The `ref: main` development-only example in `docs/configuration.md`
  line 622 is intentionally retained as a maintainer-testing example,
  with the explicit "Never for production devices" warning preserved
  above it.
- The `ref: main` internal-loader references in
  `packages/base/external_components.yaml:26` and
  `products/sense360-mini-full-ld2412.yaml:99` are internal
  self-references inside the repo, not user copy-paste examples, and
  are out of CLEANUP-006 scope (`packages/*.yaml` and
  `products/*.yaml` are in the "do not edit" list).

### Deferred / out of scope

The following `@v2.0.0` / `ref: v2.0.0` references are still in the
repo after CLEANUP-006. They are recorded here as a deferred follow-up
rather than fixed in this PR, because the directories that contain
them are in the CLEANUP-006 task's explicit "do not change" list:

- `include/README.md` lines 79–80 — Header API usage example showing
  `@v2.0.0`. Out of scope: `include/*` is reserved. A future PR with
  scope for `include/*` should re-pin these to `@v1.0.0` to match
  `examples/custom-with-remote-headers.yaml`.
- `tests/INTEGRATION_GUIDE.md` lines 32–38 — Integration guide for
  the C++ header API, pinning `@v2.0.0` / `ref: v2.0.0`. Out of
  scope: `tests/*` is reserved. The original audit row paired this
  file with `custom-with-remote-headers.yaml` for CLEANUP-006; only
  the example file was actually in scope this round.
- `products/sense360-core-*.yaml` and `products/sense360-mini-*.yaml`
  comment-block `ref: v2.2.0` / `ref: v3.0.0` example pins (lines 21,
  24, 26, 28, 29, 103, 145, 258, 358, 474 across the affected files).
  Already tracked under CLEANUP-002 in the audit rows at lines 143,
  144, and 207–209; `products/*.yaml` is out of CLEANUP-006 scope.

### Out of scope (unchanged by CLEANUP-006)

CLEANUP-006 is docs / examples wording and example-pin alignment only.
The following remain untouched:

- `products/*.yaml`, `products/webflash/*.yaml`, `packages/*.yaml`.
- `config/webflash-builds.json`, `config/webflash-compatibility.json`,
  `config/hardware-catalog.json` (including `old_name` fields).
- `.github/workflows/*`, `scripts/*`, `tests/*`, `components/*`,
  `include/*`.
- File renames (none performed).
- WebFlash config strings, artifact names, build matrix, firmware
  package IDs, hardware SKUs.
- FanTRIAC blocked status (remains blocked pending HW-005).
- LED exclusion status (remains excluded from Release-One).

### Validation run for CLEANUP-006

The commands at the top of this document, plus the sanity greps below,
were re-run after the sweep. Results are captured in the commit body
for the CLEANUP-006 PR.

```text
python3 tests/validate_webflash_builds.py
python3 tests/test_webflash_compatibility.py
python3 tests/test_webflash_artifact_naming.py
python3 tests/test_validate_webflash_release_notes.py
python3 tests/test_product_substitutions.py
python3 tests/test_release_one_entity_names.py
python3 tests/validate_configs.py

grep -RIn "@v[0-9]"                              README.md docs examples packages products include components CHANGELOG.md
grep -RIn "ref: main"                            README.md docs examples packages products include components CHANGELOG.md
grep -RIn "ref: v"                               README.md docs examples packages products include components CHANGELOG.md
grep -RIn "github://sense360store/esphome-public" README.md docs examples packages products include components CHANGELOG.md
```

After the sweep, the remaining `@v[0-9]`, `ref: v`, and `ref: main`
hits are clearly framed as one of:

- current Release-One pins (`@v1.0.0` / `ref: v1.0.0`) in
  `examples/custom-with-remote-headers.yaml`, `examples/customer-basic.yaml`,
  `README.md`, `docs/configuration.md`, `docs/installation.md`,
  `docs/release-one.md`, `docs/product-release-matrix.md`,
  `docs/manual-user-walkthrough.md`, `packages/README.md`;
- intentionally-legacy pins (`ref: v2.2.0` in `docs/product-matrix.md`
  Examples 1–3) under the new "Legacy examples" admonition;
- deferred follow-ups (`@v2.0.0` in `include/README.md` and
  `tests/INTEGRATION_GUIDE.md`; stale `ref: v2.2.0` / `ref: v3.0.0`
  comment headers in `products/sense360-core-*.yaml` and
  `products/sense360-mini-*.yaml`) explicitly listed above;
- historical audit / changelog prose (`docs/cleanup-audit.md`,
  `docs/repo-structure-audit.md`, `CHANGELOG.md`) which is not
  rewritten;
- production-warning text in `README.md`, `docs/configuration.md`,
  `docs/webflash-release-handoff.md`, and `CHANGELOG.md` that
  explicitly cautions against `ref: main` in production; the
  maintainer-only `ref: main` example at `docs/configuration.md:622`;
  and the in-repo `ref: main` self-references in
  `packages/base/external_components.yaml:26` and
  `products/sense360-mini-full-ld2412.yaml:99` (internal loader
  paths, not user copy-paste examples).

## PRODUCT-003 update (add-product validator)

PRODUCT-003 adds a read-only product-catalog consistency validator and a
companion unit-test suite. It does not change any product, wrapper, package,
build matrix, compatibility JSON, hardware catalog, artifact name, mapper,
Release-One config, FanTRIAC blocked status, or LED exclusion status.

### Files added

- `scripts/validate_product_catalog_consistency.py` — read-only validator.
  Cross-checks `config/product-catalog.json` against
  `config/webflash-builds.json`, `config/webflash-compatibility.json`,
  `config/hardware-catalog.json`, `scripts/product_name_mapper.py`, and the
  product / wrapper YAML paths. Supports `--checklist
  <CONFIG_STRING_OR_LEGACY_ID>` and `--product <PATH>` modes for the
  add-product workflow.
- `tests/test_product_catalog_consistency.py` — stdlib `unittest` suite that
  asserts: the current repo state passes; Release-One passes every
  production-specific check; FanTRIAC passes every blocked-specific check;
  every legacy-compatible entry stays non-WebFlash-shippable; the mapper
  agrees with every production entry's declared `artifact_name`; every
  WebFlash-eligible entry's wrapper basename equals lowercased
  `config_string`; and the checklist mode resolves real entries cleanly.

### CI wiring

`.github/workflows/validate.yml` runs both new commands after the existing
`Validate product catalog` step:

```text
python3 scripts/validate_product_catalog_consistency.py
python3 tests/test_product_catalog_consistency.py
```

### Out of scope (unchanged by PRODUCT-003)

- `products/*.yaml`, `products/webflash/*.yaml`, `packages/**`
- `config/webflash-builds.json`, `config/webflash-compatibility.json`,
  `config/hardware-catalog.json`, `config/product-catalog.json`
- `scripts/product_name_mapper.py`
- `tests/test_product_catalog.py` (kept as-is; new validator is additive)
- Release-One config string, artifact name, build matrix, hardware SKUs
- FanTRIAC blocked status, LED exclusion status

## PRODUCT-DEP-001 update (deprecation / removal policy)

PRODUCT-DEP-001 adds a canonical cross-cutting deprecation / removal
policy at
[`docs/product-deprecation-removal-policy.md`](product-deprecation-removal-policy.md).
Documentation only. No catalog row is set to `deprecated` or
`removed`; no entry is reclassified; no product, wrapper, package,
build-matrix entry, manifest, kit, or `REQUIRED_CONFIGS` membership
is touched. Release-One stays `production`, LED stays `preview`,
FanTRIAC stays `blocked` under HW-005, every `legacy-compatible`
entry stays `legacy-compatible`. Cross-linked from
[`docs/product-onboarding.md`](product-onboarding.md),
[`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md),
and [`docs/product-scaffold-generator.md`](product-scaffold-generator.md).

## HW-ASSETS-001 update (hardware artifact policy)

HW-ASSETS-001 adds a canonical hardware source and manufacturing
artifact policy at
[`docs/hardware/hardware-artifact-policy.md`](hardware/hardware-artifact-policy.md).
The policy defines the artifact classes (schematic PDF, KiCad
project / schematic / PCB source, BOM, CPL / pick-and-place,
Gerbers, drill files, STEP, board images, raw vendor ZIPs, and
the OS / IDE / SCM noise classes); the storage locations
(`docs/hardware/schematics/` for PDFs today; future
`docs/hardware/artifacts/`, `docs/hardware/sources/<SKU>-<REV>/`,
`docs/hardware/manufacturing/<SKU>-<REV>/`, and
`docs/hardware/images/<SKU>-<REV>/` directories deferred to
HW-ASSETS-002); the commit-vs-exclude rules; the raw-ZIP
workflow (extract outside the repo, checksum the original,
inventory the expansion, curate selected commits, retain the raw
ZIP externally); the per-board artifact index requirement
(`docs/hardware/artifacts/<SKU>-<REV>.md`) and its 22-field
schema (`board_sku`, `revision`, `artifact_source`,
`artifact_date`, `schematic_pdf`, `kicad_project`,
`kicad_schematic`, `kicad_pcb`, `bom`, `cpl`, `gerbers`,
`drill_files`, `step_file`, `images`, `excluded_files`,
`checksums`, `known_open_questions`, `pin_map_status`,
`package_yaml_status`, `product_yaml_status`, `webflash_status`,
`reviewer_notes`); the relationship to
`config/hardware-catalog.json` (JSON wins on drift; the artifact
index does not introduce any new JSON fields); the relationship
to product availability (the key rule: *hardware artifact
availability does not equal firmware support or WebFlash
availability*); the relationship to pin maps / package YAML /
product YAML (the recommended ordering); the manufacturing-
evidence handling options (commit directly / Git LFS / GitHub
Release / dedicated hardware repo / external-only with
checksum); the versioning and revision naming convention; the
finished-board inventory (`S360-100`, `S360-200`, `S360-210`,
`S360-211`, `S360-300`, all R4); the design-pending board
inventory (`S360-310`, `S360-311`, `S360-312`, `S360-320`,
`S360-400`, `S360-410`, all R4) with the per-board evidence
required before package / product / WebFlash work; the
follow-up PR sequence (HW-ASSETS-002, HW-GAP-001, HW-PINMAP-310
/ -311 / -312 / -320 / HW-PINMAP-400 / -410, PACKAGE-GAP-001,
PRODUCT-GAP-001); and the explicit do-not-change guardrails.
Documentation only. No raw vendor / fab ZIP contents are
added; no KiCad / BOM / CPL / Gerbers / drill / STEP / image
files are added; the per-board artifact index for
`S360-100-R4` is **not** added (that is the scope of
HW-ASSETS-002); no entry in `config/hardware-catalog.json`,
`config/product-catalog.json`, `config/webflash-builds.json`,
or `config/webflash-compatibility.json` is changed; no product
YAML, WebFlash wrapper, or package YAML is changed; no script,
test, workflow, component, or include is changed;
`.gitignore` / `.gitattributes` / pre-commit configuration are
not changed (actual exclusion-rule additions are deferred to
HW-ASSETS-002, which is the first PR to land a curated
artifact tree); Git LFS is **not** introduced (it is listed in
the policy as a future decision option only); no firmware is
regenerated; no GitHub Release is created or modified;
Release-One (`Ceiling-POE-VentIQ-RoomIQ`,
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, tag
`v1.0.0`) stays unchanged; the Sense360 LED preview catalog
entry stays `status: preview`, `channel: preview`; FanTRIAC
stays `blocked` under HW-005; the mains-voltage compliance
status for `S360-320` / `S360-400` (COMPLIANCE-001) is not
changed. Cross-linked from
[`docs/hardware/firmware-package-mapping-audit.md`](hardware/firmware-package-mapping-audit.md),
[`docs/product-onboarding.md`](product-onboarding.md),
[`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md),
[`docs/hardware/s360-100-r4-core.md`](hardware/s360-100-r4-core.md),
and [`docs/hardware/s360-300-r4-led.md`](hardware/s360-300-r4-led.md).

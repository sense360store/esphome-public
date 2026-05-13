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
| `config/webflash-builds.json` | `current` | Build matrix, single Release-One entry. | Keep. |
| `config/webflash-compatibility.json` | `current` | Canonical module / forbidden-token list; `release_one_required_configs: ["Ceiling-POE-VentIQ-RoomIQ"]`. | Keep. |
| `config/hardware-catalog.json` | `current` | Canonical SKU → friendly-name table; carries `old_name` entries for `LED Ring` (S360-300) and `Bathroom Pro` (S360-211), which is correct. | Keep. |
| `.github/workflows/firmware-build-release.yml` | `current` | Release-One build/release gate; excludes `products/webflash/*` from matrix discovery; runs `tests/check_webflash_build_output.py`. | Keep. |
| `.github/workflows/validate.yml` | `current` | Quick YAML syntax pre-flight. | Keep. |
| `scripts/product_name_mapper.py` | `current` | Maps product YAML basenames → WebFlash artifact names; explicit comment retains FanTRIAC mapping as legacy reference. | Keep. |
| `scripts/check-webflash-release-assets.py` | `current` | Asset-existence gate. | Keep. |
| `scripts/validate-webflash-release-notes.py` | `current` | Release-body format gate. | Keep. |
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
| `docs/webflash-contract.md` | `current` | Canonical WebFlash artifact/grammar/token contract. | Keep. |
| `docs/webflash-ci-alignment.md` | `current` | CI ↔ WebFlash alignment record. | Keep. |
| `docs/webflash-release-handoff.md` | `current` | Release-handoff record. | Keep. |
| `docs/webflash-release-proof.md` | `current` | ESP-006 / ESP-007 proof record (run `25763009641`). | Keep. |
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

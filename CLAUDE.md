# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository. Every fact here is derived from the tree; where this
file and a source-of-truth file disagree, the source-of-truth file wins and
this file is the one to fix.

## Project overview

This repository is the ESPHome firmware **source** for Sense360 environmental
monitoring devices (ESP32-S3 ceiling hubs plus sensor / driver / PSU modules).
It holds the product YAML compositions, builds and publishes the **unsigned**
release `.bin` artifacts via GitHub Actions, and is the manual / custom
firmware path for advanced users. It sits **upstream** of
[`sense360store/WebFlash`](https://github.com/sense360store/WebFlash) — the
production signing / manifest / flash authority — and the cross-repo contract
is exactly three stable surfaces: release **tags**, WebFlash **config-string**
values (e.g. `Ceiling-POE-VentIQ-RoomIQ`), and **artifact names**
(`Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin`). This repo does **not**
sign firmware. The production stable customer baseline is Release-One, config
string `Ceiling-POE-VentIQ-RoomIQ`. The single canonical status / roadmap /
blocker document is
[`docs/sense360-roadmap-status.md`](docs/sense360-roadmap-status.md); the
standing gates live in
[`docs/standing-invariants.md`](docs/standing-invariants.md).

## Cross-repository operating model

Before any cross-repository work, Claude Code must read
[`sense360store/SOT/CLAUDE-OPERATING-MODEL.md`](https://github.com/sense360store/SOT/blob/main/CLAUDE-OPERATING-MODEL.md).

- **SOT owns programme-level truth**: accepted cross-repository decisions,
  programme IDs, cross-repository status, and owner actions.
- **This repository owns** firmware architecture, implementation, ADRs,
  tests, validation, hardware-facing behaviour, release mechanics, and
  detailed technical execution records.
- This repository must reference SOT programme IDs but must not
  independently redefine programme-level status.
- When implementation evidence materially changes programme state, the SOT
  update must be made in a separate PR.
- Repository-local `CLAUDE.md` and
  [`docs/standing-invariants.md`](docs/standing-invariants.md) remain
  authoritative for repository-internal engineering rules.

### Bounded agent autonomy (AGENT-BOUNDED-AUTONOMY-001)

This repository **adopts AGENT-BOUNDED-AUTONOMY-001**, the bounded agent
autonomy contract defined in the *AGENT-BOUNDED-AUTONOMY-001: bounded
autonomy* section of
[`sense360store/SOT/CLAUDE-OPERATING-MODEL.md`](https://github.com/sense360store/SOT/blob/main/CLAUDE-OPERATING-MODEL.md).
SOT owns the contract and all programme-level authority. Adoption
provenance: verified against SOT `main` commit
[`387cabf44a79dfe03d6c7959ec4e3d012c295647`](https://github.com/sense360store/SOT/commit/387cabf44a79dfe03d6c7959ec4e3d012c295647)
(contract present; `programme_status: implemented`; esphome-public recorded
as not yet adopted pending this adoption). The canonical link stays pointed
at SOT `main`; the contract text is **not duplicated here**, and future
tasks invoke it with the **canonical SOT invocation block** rather than
restating its rules.

This `CLAUDE.md` and
[`docs/standing-invariants.md`](docs/standing-invariants.md) provide
**repository-local tightening** on top of the SOT contract. Local rules may
**tighten but never loosen** the SOT contract; where rules differ, the
**stricter safety rule wins**; an authority conflict the SOT precedence
rules cannot resolve ends the run as `BLOCKED_AUTHORITY_CONFLICT`, never a
judgement call. Within an explicitly authorised task, agents **continue
autonomously through routine repository-local engineering** until exactly
one of the five named SOT terminal states is reached.

**Autonomous within an authorised task** (the firmware-scoped instantiation
of the SOT autonomous permissions): inspect source, configuration
declarations, history, PRs, and CI; add or update source, documentation,
and tests inside this repository's authority; run static validation, unit
and contract tests; run deterministic simulation where authorised; run
local compilation where authorised and available; inspect hosted compile
results and existing release / distribution evidence; remediate every
branch-caused test or CI failure; create and maintain one draft PR; and
prepare a separate SOT reconciliation recommendation when implementation
evidence materially changes programme state.

**Never autonomous in this repository** (firmware tightening — each line
restates or narrows, never widens, the SOT owner reservations; the standing
gates below and `docs/standing-invariants.md` apply unchanged, and in
particular Release-One (`Ceiling-POE-VentIQ-RoomIQ`) remains the production
stable customer baseline):

- merge any PR (including the agent's own draft PR);
- create or publish a tag or GitHub Release;
- dispatch any workflow that can publish, release, attach, or deploy
  firmware — in particular `Release 3: Build & Release`
  (`firmware-build-release.yml`) and the create-release workflow
  (`create-release.yml`);
- alter production release / channel / lifecycle posture merely because a
  build compiles;
- weaken or bypass provenance, checksum, secret, credential, signing,
  compatibility, release, or install gates;
- broaden firmware release discovery beyond the declaration-driven
  [`config/webflash-builds.json`](config/webflash-builds.json) model
  (ESP-007);
- make Kitchen or Bedroom customer-default, buyable, or commercially
  available;
- make any fan configuration stable;
- expose FanTRIAC as stable, recommended, default, buyable, or one-click;
- author or amend operator attestations, dates, signatures, or physical
  bench claims;
- infer hardware population, sensor identity, pin correctness, supplied
  attachments, or accuracy without the required evidence;
- treat source inspection, simulation, or compilation as physical hardware,
  customer, compliance, safety, or commercial proof;
- change SOT programme status in this repository.

**Read-only observation stays allowed**: agents may verify existing
releases, tags, artifacts, served binaries, owner-authored decisions, and
bench records. Observation never authorises mutation and never raises the
evidence level; when reporting existing external evidence, cite its
provenance and name the exact evidence level it proves.

**Workflow distinction**: routine PR CI and validation inspection is
autonomous; branch-caused CI remediation is autonomous; a non-publishing
compile validation workflow may be dispatched only when the task explicitly
authorises it and the workflow has no release or deployment side effect;
any publishing or release-capable workflow remains owner-reserved.

**Terminal states**: the five SOT terminal states apply exactly as defined
in the SOT contract — `READY_FOR_OWNER_REVIEW`, `BLOCKED_OWNER_DECISION`,
`BLOCKED_EXTERNAL_ACCESS`, `BLOCKED_AUTHORITY_CONFLICT`,
`UNSAFE_TO_PROCEED` — and this repository defines no sixth local state. The
conjunctive escalation rule is preserved unchanged: the owner may be
interrupted only when **all four** SOT threshold conditions hold
simultaneously.

This adoption is governance text and its regression tests only: it changes
no firmware, product YAML, configuration declaration, release workflow,
version, manifest, binary, hardware record, product status, or commercial
state.

## Sense360 hardware reference (canonical SKUs)

The naming source of truth is
[`docs/hardware-catalog.md`](docs/hardware-catalog.md) with the
machine-readable mirror at
[`config/hardware-catalog.json`](config/hardware-catalog.json) (which also
carries `schematic_status` per entry). **Friendly names are canonical**; old
names exist only for legacy reference and must not be used in new YAML, docs,
or artifacts. Use `Ceiling`, never `Celling` (legacy typo).

| Group   | Type      | Friendly name      | SKU      | Rev | Old name                        | What it does |
|---------|-----------|--------------------|----------|-----|---------------------------------|--------------|
| Ceiling | Hub       | Sense360 Core      | S360-100 | R4  | 360Core_Ceiling_V3_R            | Main board. Has the ESP32-S3 and connectors for all other modules. |
| Ceiling | Sensor    | Sense360 RoomIQ    | S360-200 | R4  | Presence + Comfort (two boards) | Merged board. PIR, LD2450, SEN0609, LTR-303ALS light, SHT4x temp/humidity, BMP581 pressure. |
| Ceiling | Sensor    | Sense360 AirIQ     | S360-210 | R4  | AirIQ Ceiling                   | Air quality board. CO2 SCD41, VOC SGP41, HCHO SFA40, gas MICS-4514 with STM8 (all PCB-mounted). Connector for external SPS30 PM. |
| Ceiling | Sensor    | Sense360 VentIQ    | S360-211 | R4  | Bathroom Pro                    | Smaller bathroom air-quality board. SGP41 on board. Connectors for IR temp and SPS30. |
| Ceiling | Indicator | Sense360 LED       | S360-300 | R4  | LED Ring                        | Ring of WS2812B LEDs. |
| Inline  | Driver    | Sense360 Relay     | S360-310 | R4  | S360-Relay-C                    | On/off relay for bathroom fans. |
| Inline  | Driver    | Sense360 PWM       | S360-311 | R4  | 12vFan_PWM_PulseCounter         | 12V PWM fan driver, up to 4 fans with tach feedback. |
| Inline  | Driver    | Sense360 DAC       | S360-312 | R4  | Fan_GP8403                      | 0 to 10V analog fan driver, for example Cloudlift S12. |
| Inline  | Driver    | Sense360 TRIAC     | S360-320 | R4  | TRIAC_Board                     | Phase dimmer for mains fan or lamp. |
| Power   | PSU       | Sense360 240v PSU  | S360-400 | R4  | PWR Module                      | Mains to 5V using HLK-5M05. |
| Power   | PSU       | Sense360 PoE PSU   | S360-410 | R4  | PoE Module                      | PoE to 5V. |

## Repo layout

The YAML is a **board / bundle / alias / shim** layered composition (see
[`docs/system-architecture.md`](docs/system-architecture.md) and
[`docs/arch-board-bundle-plan.md` (archived)](docs/archive-index.md)); the
declaration layer that governs what ships lives in `config/`.

- **`products/sense360-*.yaml`** — customer include paths. Thin compat
  **shims** that do nothing but `!include` the matching bundle. Customers pin
  these exact paths at a release tag (`ref: v1.0.0`), so they are never
  deleted or renamed.
- **`products/bundles/`** — one YAML per WebFlash config string; the
  **canonical composition** (board packages + base infrastructure + feature
  profiles) for that config.
- **`products/webflash/`** — release-gate **wrappers**. Thin re-exports of the
  canonical product YAML so [`config/webflash-builds.json`](config/webflash-builds.json)
  can address builds via the `products/webflash/` namespace the release
  workflow consumes.
- **`products/compile-only/`** — compile-only validation **skeletons** for the
  pre-hardware buildability lane (listed in
  [`config/compile-only-targets.json`](config/compile-only-targets.json)).
  Deliberately outside top-level catalog scanning; never WebFlash-exposed,
  never a release artifact, never hardware proof.
- **`packages/`** — composition layers: `packages/boards/` (SKU-aligned
  **authoritative** board packages, e.g. `s360-211-ventiq.yaml`),
  `packages/base/` (WiFi, encrypted API, OTA, logging, time, external
  components), `packages/hardware/` and `packages/expansions/` (legacy
  functional paths retained as thin `!include` **aliases** of the board
  packages, plus drivers not yet flipped into the board layer),
  `packages/features/` (behaviour profiles / automations). The S360-100 Core
  mount paths are the inverse today: the board overlay still wraps the legacy
  `packages/hardware/sense360_core_*.yaml` source until Core's
  source-of-truth flip lands.
- **`config/`** — the **catalog source of truth** (machine-readable
  declarations; JSON, validated by `scripts/` + `tests/`):
  [`product-catalog.json`](config/product-catalog.json) (product lifecycle /
  status / blockers), [`webflash-builds.json`](config/webflash-builds.json)
  (the release/build matrix — what release publishing ships, per ESP-007),
  [`hardware-catalog.json`](config/hardware-catalog.json),
  [`webflash-compatibility.json`](config/webflash-compatibility.json)
  (contract snapshot), [`preview-release-targets.json`](config/preview-release-targets.json),
  [`release-channel-policy.json`](config/release-channel-policy.json),
  [`room-bundle-skus.json`](config/room-bundle-skus.json),
  [`room-bundle-fan-variants.json`](config/room-bundle-fan-variants.json),
  [`compile-only-targets.json`](config/compile-only-targets.json), and
  companions. Docs describe; `config/` decides.
- **`components/`** — external ESPHome C++ components (`ld2412`, `ld2450`,
  `ld24xx`). **`include/sense360/`** — extracted C++ logic headers
  (`led_logic.h`, `calibration.h`, `thresholds.h`, `time_utils.h`) unit-tested
  natively from `tests/unit/`.
- **`scripts/`** — release / validation / planning tooling (each with a
  `tests/test_*.py` counterpart). **`tests/`** — Python test suite +
  validators + C++ test Makefile. **`docs/`** — reference docs; canonical
  roadmap at [`docs/sense360-roadmap-status.md`](docs/sense360-roadmap-status.md);
  hardware evidence under `docs/hardware/`. **`examples/`** — customer
  configuration templates.

## ESPHome conventions used here

- **Full configs, not snippets.** Every `products/` entry resolves (shim →
  bundle → packages) to a complete, standalone ESPHome config: bundles include
  the base packages (`wifi`, `api_encrypted`, `ota`, `logging`, `time`,
  `external_components`) plus board and feature packages, so
  `esphome config products/<file>.yaml` validates each product directly.
  Customers override only `device_name` / `friendly_name` substitutions.
- **List syntax for component blocks.** `script:`, `sensor:`, `switch:`,
  `binary_sensor:` (and other multi-entry component blocks) are written in
  ESPHome list form (`- id: …` / `- platform: …`), because ESPHome merges
  packages by concatenating lists — map-form blocks would collide across
  packages.
- **Composition via `packages:` + `!include`.** Products never duplicate
  package wiring; they include it. Legacy `packages/hardware/*` and
  `packages/expansions/*` paths must keep resolving (alias files), since
  customers pin them.
- **Secrets only via `!secret`.** Copy
  [`secrets.example.yaml`](secrets.example.yaml) to `secrets.yaml` (gitignored
  — never commit it; `scripts/check-no-tracked-secrets.py` and the fallback-AP
  password guard enforce this). CI generates placeholder secrets for builds.
- **YAML style** (`.yamllint`): 2-space indent, indented sequences, max line
  length 120 (warning), no `---` document start. ESPHome custom tags
  (`!secret`, `!include`, `!lambda`, `!extend`, `!remove`) are why pre-commit's
  `check-yaml` runs with `--unsafe` (syntax-only parse) — do not remove that
  flag, and do not mirror unsafe loading into real config-loading code (use
  `yaml.safe_load` with registered tag constructors, as
  `tests/validate_configs.py` does).
- **Python tests are stdlib `unittest` modules** (no pytest-specific APIs),
  runnable individually (`python3 tests/test_x.py`) and as a suite under
  plain pytest. Do not add module-level `test_*` functions that invoke
  `unittest.main()` — pytest collects them and they raise `SystemExit`.

## Commands

```bash
# Python test suite — full suite must stay green under plain pytest
python3 -m pytest tests/
python3 -m pytest tests/test_room_bundle_fan_variants.py     # one file
python3 tests/test_product_catalog.py                        # files also run directly
python3 -m unittest tests.test_room_bundle_fan_variants -v   # or via unittest

# YAML lint (uses .yamllint at the repo root)
yamllint .

# Repo validators (the per-PR CI gate, validate.yml, runs these and more)
python3 tests/validate_configs.py                        # YAML syntax/structure of products+packages
python3 tests/validate_webflash_builds.py                # build matrix vs contract snapshot
python3 scripts/validate_product_catalog_consistency.py  # catalog cross-file consistency
python3 scripts/generate_firmware_matrix.py --check      # generated-matrix freshness
python3 scripts/report_firmware_build_gaps.py --check    # generated-gap-report freshness

# ESPHome config validation (needs esphome installed; pin: requirements-dev.txt)
esphome config products/sense360-ceiling-poe-ventiq-roomiq.yaml

# Compile lanes (hosted CI; the full-compile passes are workflow_dispatch only)
python3 scripts/validate_compile_targets.py --metadata-only   # compile-only lane, no ESPHome
python3 scripts/validate_compile_targets.py --compile         # full `esphome compile` pass
#   CI lanes: validate.yml ("CI: Quick Validation" — the per-push/PR gate)
#   · compile-only.yml ("CI: Compile-Only") and preview-compile-dryrun.yml
#     ("CI: Preview Compile Dry-Run") — manual dispatch, metadata or full compile
#   · ci-validate-configs.yml ("CI: Validate Configs") — manual broad legacy sweep
#   · firmware-build-release.yml ("Release 3: Build & Release") — builds and
#     publishes the release .bin set on release publish, driven by
#     config/webflash-builds.json (ESP-007)

# C++ unit tests for the extracted logic headers
cd tests && make test

# Pre-commit hooks (yamllint, black, flake8, clang-format, secret guards)
pre-commit run --all-files
```

## Standing gates (do not regress)

[`docs/standing-invariants.md`](docs/standing-invariants.md) is the **live,
authoritative text** for every gate below — read it before touching anything
a gate covers. The lines here are one-line operative summaries only; on any
difference, `docs/standing-invariants.md` wins.

- **Release-One is the customer baseline** — production stable is
  `Ceiling-POE-VentIQ-RoomIQ`; Simple install resolves
  to it alone, and the waiver-promoted Bedroom / Kitchen bundles stay hidden /
  not buyable / never the customer default
  ([live text](docs/standing-invariants.md)).
- **FanTRIAC is experimental-lane only** — never stable / recommended /
  default / buyable / kit-exposed / in `release_one_required_configs`; no
  electrical-safety / EMC / compliance claim
  ([live text](docs/standing-invariants.md)).
- **Fans are never stable** — under owner declaration `HW-RELEASE-001`
  ([`docs/hw-release-001.md`](docs/hw-release-001.md)) FanPWM / FanDAC configs
  carry `config/webflash-builds.json` rows on the **preview** channel and
  FanRelay configs on the **experimental** channel only; **no fan config ever
  ships on the stable channel** and fan stable release stays blocked
  ([live text](docs/standing-invariants.md)).
- **FanDAC I²C addressing is pending bench** — `FANDAC-I2C-ADDR-001` stays
  PENDING; `0x59` is forbidden when VentIQ/AirIQ is present
  ([live text](docs/standing-invariants.md)).
- **No false proof** — preview / compile work is firmware-build proof only;
  never claim hardware / bench / compliance / safety /
  commercial-availability proof for a preview artifact
  ([live text](docs/standing-invariants.md)).

Three standing rules travel with the gates (live text:
[`docs/standing-invariants.md`](docs/standing-invariants.md)):

- **FanTRIAC changes are human-review only.** Do NOT auto-merge any FanTRIAC
  pin / blocker / status change.
- **Attestations are never machine-written.** Operator attestation /
  bench-evidence blocks are completed by the human operator only; agents may
  scaffold an intentionally empty block but must never fill in attestation
  content, dates, signatures, or evidence claims (source:
  [`docs/package-triac-001-operator-bench-proof.md` (archived)](docs/archive-index.md)).
- **The release matrix is declaration-driven (ESP-007).** Releases ship only
  what [`config/webflash-builds.json`](config/webflash-builds.json) declares;
  never reintroduce a broad `products/` scan in
  [`.github/workflows/firmware-build-release.yml`](.github/workflows/firmware-build-release.yml).

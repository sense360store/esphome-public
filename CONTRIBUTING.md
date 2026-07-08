# Contributing to Sense360 ESPHome firmware

Thanks for helping improve Sense360 firmware. This guide covers how to file
issues, how to open a pull request, the local gate every change must pass,
and the documentation conventions this repository enforces.

## How to file an issue

Use the [issue templates](https://github.com/sense360store/esphome-public/issues/new/choose):

- **Flashing problem** — a build or flash that fails or a device that won't
  boot after flashing.
- **Hardware fault** — a sensor or board misbehaving on known-good firmware.
- **Configuration question** — consider
  [GitHub Discussions](https://github.com/sense360store/esphome-public/discussions)
  first; use the issue template if you believe the documentation or YAML is
  wrong.
- **Feature request** — new sensors, automations, or product combinations.

Include the exact firmware artifact name
(`Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin`) or the pinned release
tag + product YAML path when reporting firmware behaviour. See
[SUPPORT.md](SUPPORT.md) for where non-defect matters route.

## How to open a pull request

1. Fork and branch from `main`.
2. Keep the change scoped — one concern per PR.
3. Run the **local gate** (below) and make it pass.
4. Fill in the pull request template, including the required local gate
   statement (which commands you ran and their result).
5. PRs are gated by CI "Quick Validation" (`validate.yml`); a green local
   gate is the fastest way to a green CI run.

Customer-pinned paths are load-bearing: never delete or rename
`products/sense360-*.yaml`, `packages/hardware/*`, or
`packages/expansions/*` — customers pin those exact paths at release tags.

## The local gate

Run from the repository root; all of it must pass before you open a PR:

```bash
python3 -m pytest tests/                                 # full Python test suite
yamllint .                                               # YAML lint (.yamllint at repo root)
python3 tests/validate_configs.py                        # YAML syntax/structure of products+packages
python3 tests/validate_webflash_builds.py                # build matrix vs contract snapshot
python3 scripts/validate_product_catalog_consistency.py  # catalog cross-file consistency
python3 scripts/generate_firmware_matrix.py --check      # generated-matrix freshness
python3 scripts/report_firmware_build_gaps.py --check    # generated-gap-report freshness
python3 scripts/generate_product_entity_tables.py --check  # docs-site entity-table freshness
```

If you touched product or package YAML, also validate the resolved config
(requires ESPHome, pinned in `requirements-dev.txt`):

```bash
esphome config products/sense360-ceiling-poe-ventiq-roomiq.yaml
```

If you touched the extracted C++ headers under `include/sense360/`:

```bash
cd tests && make test
```

Pre-commit hooks (yamllint, black, flake8, clang-format, secret guards) are
configured — `pre-commit run --all-files` catches most style issues early.

## Repository conventions

- **`config/` decides; docs describe.** The machine-readable declarations
  under `config/` are the catalog source of truth. Never edit a doc to
  contradict them — fix the doc to match, or change the config through the
  proper gate.
- **Composition, not duplication.** Products compose via `packages:` +
  `!include`; component blocks use ESPHome **list syntax** (`- platform: …`)
  so packages merge without collisions.
- **Secrets only via `!secret`.** Never commit `secrets.yaml`; CI generates
  placeholder secrets for builds.
- **Python tests are stdlib `unittest` modules** — runnable individually and
  under plain pytest; no pytest-specific APIs, no module-level `test_*`
  functions that call `unittest.main()`.

## Documentation conventions and standing gates

[`docs/standing-invariants.md`](docs/standing-invariants.md) is the live,
authoritative text for the repository's standing gates — **read it before
touching anything a gate covers** (release channels, fan/TRIAC status,
Release-One baseline, the build matrix). Non-negotiables for contributors:

- **FanTRIAC changes are human-review only.** No auto-merge of any FanTRIAC
  pin / blocker / status change.
- **Attestations are never machine-written.** Operator attestation and
  bench-evidence blocks are completed by the human operator only.
- **The release matrix is declaration-driven (ESP-007).** Releases ship only
  what [`config/webflash-builds.json`](config/webflash-builds.json)
  declares.
- **No false proof.** Preview / compile work is firmware-build proof only —
  never claim hardware, bench, compliance, safety, or
  commercial-availability proof for a preview artifact.
- The canonical status / roadmap / blocker document is
  [`docs/sense360-roadmap-status.md`](docs/sense360-roadmap-status.md);
  where a doc and a source-of-truth file disagree, the source-of-truth file
  wins and the doc is what gets fixed.

## Releasing

The end-to-end release sequence — how a version bump in this repo becomes a
signed, browser-flashable build in WebFlash, and which stages dispatch vs.
auto-fire — is documented in
[`docs/RELEASE-PIPELINE.md`](docs/RELEASE-PIPELINE.md). Read it before cutting a
release; it also covers the `GITHUB_TOKEN` recursion caveat that can silently
stall the auto build.

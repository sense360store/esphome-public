# Summary

<!-- What this PR changes and why. One concern per PR. -->

## Scope

<!-- Files/areas touched. Call out anything customer-pinned (products/sense360-*.yaml,
     packages/hardware/*, packages/expansions/*) or gate-covered
     (docs/standing-invariants.md) that this PR affects. -->

## Local gate statement (required)

<!-- State which of the local gate commands you ran and their result. A PR without
     this statement is not ready for review. See CONTRIBUTING.md for the full gate. -->

- [ ] `python3 -m pytest tests/` — passes
- [ ] `yamllint .` — passes
- [ ] `python3 tests/validate_configs.py` — passes
- [ ] `python3 tests/validate_webflash_builds.py` — passes
- [ ] `python3 scripts/validate_product_catalog_consistency.py` — passes
- [ ] `python3 scripts/generate_firmware_matrix.py --check` — passes
- [ ] `python3 scripts/report_firmware_build_gaps.py --check` — passes
- [ ] `esphome config <touched product YAML>` — passes / not applicable
- [ ] `cd tests && make test` (C++ headers) — passes / not applicable

Result summary:

<!-- e.g. "All gate commands pass locally; esphome config n/a (docs-only change)." -->

## Standing invariants

- [ ] I read [`docs/standing-invariants.md`](../docs/standing-invariants.md) and this PR
      does not regress any standing gate (Release-One baseline, fan/TRIAC posture,
      declaration-driven release matrix, no false proof, no machine-written attestations).

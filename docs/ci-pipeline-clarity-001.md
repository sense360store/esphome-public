# CI-PIPELINE-CLARITY-001 — execution tracking (esphome-public)

Pipeline clarity + product-state correction. Six steps across two repos,
mostly CI/docs, with two product-state changes held for owner sign-off. One
session, one step, one PR, HOLD FOR OWNER stated in the PR description, then
stop.

## Decisions folded in (owner, 2026-07-08)

- **FanTRIAC is ready to release** — wire it in fully (P3). Making it releasable
  on the experimental channel is a PRODUCT-STATE CHANGE and requires the
  owner's explicit sign-off that its firmware is genuinely ready to ship.
- **RoomIQ-LED (`Ceiling-POE-RoomIQ-LED`) was never built or served** — 404
  upstream, not in the served set, not delisted. It is de-listed from the
  release-eligible config (P4), not rebuilt. The catalog entry is preserved so
  it can be built properly later; only its release-eligibility changes.

## Execution log

| Step | Repo | Status | PR | Notes |
|------|------|--------|----|-------|
| P1 | esphome-public | EXECUTED | (this PR) | `tag_suffix` in `create-release.yml` converted from `type: string` to `type: choice` (options: blank, `led-preview`, `experimental`). Contract test `tests/test_create_release_tag_suffix.py` locks the dropdown to the supported non-stable suffixes and ties every non-blank option to `derive_release_version_channel.py`. |
| P2 | esphome-public | EXECUTED | (this PR) | Single-source product picker. Generating `type: choice` options in-workflow is impractical (GitHub Actions choice options are static), so the lock-step branch was taken: `tests/test_release_product_selection.py` gains `ReleasePickerLockStepTests`, locking the Bump / Create / Draft-notes `config_string` pickers to the one canonical source (`config/webflash-builds.json` via `scripts/list_release_targets.py`). Adding a release-eligible build now fails the gate unless every picker is updated too. Membership unchanged (P3's job): the Bump/Create FanTRIAC gap is the documented, tested `PENDING_BUMP_CREATE_PICKER_ADDITIONS` carve-out that P3 closes. Each picker's options list is headed by a comment naming the single source. WebFlash `add-firmware-source.yml` lives in the WebFlash repo (not vendored here), so its parity is enforced by WebFlash's own tests (P4b), out of single-repo scope for this step. |
| P3 | esphome-public | EXECUTED | (this PR) | Wire FanTRIAC in fully. **PRODUCT-STATE CHANGE — HOLD FOR OWNER SIGN-OFF.** `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` (channel experimental) added to the Bump (`bump-version.yml`) and Create (`create-release.yml`) `config_string` dropdowns in canonical last position; the Draft-notes (`release-notes-draft.yml`) picker already listed it. Its `config/webflash-builds.json` row was already complete/consistent (verified by `tests/validate_webflash_builds.py`), so no matrix change was needed. The lock-step contract test (`tests/test_release_product_selection.py`) `PENDING_BUMP_CREATE_PICKER_ADDITIONS` carve-out was emptied so Bump/Create must now offer every release-eligible target with no gap. WebFlash `add-firmware-source.yml` is the fourth picker but lives in the WebFlash repo (not vendored here), so its FanTRIAC parity is out of single-repo scope and enforced WebFlash-side. Merging makes FanTRIAC releasable on the experimental channel — requires the owner's explicit confirmation the firmware is ready to ship. |
| P4a | esphome-public | EXECUTED | (this PR) | De-list RoomIQ-LED from release-eligible set. **PRODUCT-STATE CHANGE.** `Ceiling-POE-RoomIQ-LED` was never built or served (no upstream binary, not in the served set), so it is removed from the release-eligible set: its build row was deleted from `config/webflash-builds.json`; it was removed from all three `config_string` pickers (`bump-version.yml`, `create-release.yml`, `release-notes-draft.yml`); its `config/product-catalog.json` entry was demoted from `preview` (webflash_build_matrix true, version/channel/artifact_name) to `hardware-pending` (webflash_build_matrix false, no version/channel/artifact_name). The catalog entry, its `product_yaml`, and its `products/webflash` wrapper are PRESERVED so the config can be built and re-listed later; only its release-eligibility changed. The distinct published VentIQ LED preview (`Ceiling-POE-VentIQ-RoomIQ-LED`) is untouched. Derived artifacts were propagated: `config/firmware-combination-matrix.json` + `docs/firmware-build-gap-report.md` regenerated, `config/preview-release-targets.json` RoomIQ-LED target reverted to `eligible-unpublished` with a build_blocker, `config/compile-only-candidates.json` `currently_shipping_config_strings` trimmed. Contract tests updated: `tests/test_release_product_selection.py` and `tests/test_product_catalog.py` gained explicit de-listing guards (RoomIQ-LED must not be release-eligible / in any picker / carry an artifact), and the preview-publish/notes/targets/wrappers regression tests were reconciled to the five-build ledger. Full gate green. |
| P4b | WebFlash | NOT EXECUTED | | RoomIQ-LED picker parity (WebFlash repo, separate tracking file). |
| P5 | esphome-public | NOT EXECUTED | | `docs/RELEASE-PIPELINE.md`. |
| P6 | esphome-public | NOT EXECUTED | | Consolidate redundant CI + tighten release-workflow triggers. |

## Notes

- Tracking file per repo. This file (esphome-public) is created by P1, the
  repo's first executed step.
- Steps P3 and P4a change what is releasable/served and especially need owner
  review before merge.

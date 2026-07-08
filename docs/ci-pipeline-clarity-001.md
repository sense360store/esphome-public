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
| P3 | esphome-public | NOT EXECUTED | | Wire FanTRIAC in fully. PRODUCT-STATE CHANGE — HOLD FOR OWNER SIGN-OFF. |
| P4a | esphome-public | NOT EXECUTED | | De-list RoomIQ-LED from release-eligible set. PRODUCT-STATE CHANGE. |
| P4b | WebFlash | NOT EXECUTED | | RoomIQ-LED picker parity (WebFlash repo, separate tracking file). |
| P5 | esphome-public | NOT EXECUTED | | `docs/RELEASE-PIPELINE.md`. |
| P6 | esphome-public | NOT EXECUTED | | Consolidate redundant CI + tighten release-workflow triggers. |

## Notes

- Tracking file per repo. This file (esphome-public) is created by P1, the
  repo's first executed step.
- Steps P3 and P4a change what is releasable/served and especially need owner
  review before merge.

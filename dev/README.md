# dev/ — bench development harness

This directory is for **bench development only**. Nothing under `dev/` is
ever release-eligible: no build, compile, or release matrix selects files
here, and CI enforces that (`scripts/check_dev_harness_guard.py`, run by
`validate.yml` on every push/PR).

Contents:

- `device-template.yaml` — copy to `dev/<name>.local.yaml` (gitignored) for
  each bench unit; points the ESPHome add-on at a repo entry point on a
  feature branch.
- `dev-overlay.yaml` — scratch layer for bench experiments. Committed empty;
  CI blocks merging while it contains functional content.
- `secrets.yaml.example` — placeholder secrets template; copy to
  `dev/secrets.yaml` (gitignored) and fill in real bench values.

The full workflow is documented in
[`docs/DEV_WORKFLOW.md`](../docs/DEV_WORKFLOW.md).

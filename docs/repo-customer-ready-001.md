# REPO-CUSTOMER-READY-001 — execution tracking (esphome-public)

This file carries the ratified owner decisions for the
REPO-CUSTOMER-READY-001 programme and the local execution log for
**this repository** (`sense360store/esphome-public`). The sibling file in
[`sense360store/WebFlash`](https://github.com/sense360store/WebFlash) tracks
the WebFlash-side steps. Each programme session executes exactly one step in
exactly one repo, opens exactly one PR, marks its step EXECUTED here, then
stops.

## Ratified owner decisions (2026-07-05)

- **D1:** WebFlash is licensed MIT (© 2026 Sense360), byte identical to the
  standard MIT text. The README "device owners and authorized distributors"
  sentence is removed and replaced with the licence statement.
- **D2:** A NOTICE section (in the WebFlash README §License and a NOTICE
  file) states that binaries under `firmware/` are build artifacts of
  sense360store/esphome-public distributed under its MIT terms, integrity
  assured by ed25519 signing, and are not relicensed by this repository's
  licence.
- **D3:** Support routing: GitHub Issues for defects on both repos;
  community Q&A via GitHub Discussions on esphome-public (owner enables in
  console); order and warranty matters route to the mysense360.com contact
  page.
- **D4:** The default credential advisory is authored as an in-tree DRAFT
  only; publication is an owner action gated on WF-H1-REIMPORT-CLEAN-001
  landing.
- **D5:** Both READMEs become front doors under 100 lines: what this is,
  flash or adopt in three steps, where to get help. Displaced content moves
  under docs/ with every inbound reference repointed in the same PR.
- **D6:** esphome-public LICENSE copyright year updated; its README gains a
  licence split statement: firmware configurations MIT, hardware designs
  CERN-OHL-P, experimental lane posture per COMPLIANCE-001.

## Step sequence (programme-wide)

| Step | Repo           | Scope |
|------|----------------|-------|
| S1   | esphome-public | Additive bundle: this file, D6 (LICENSE year + README licence split), SUPPORT.md, CONTRIBUTING.md, issue templates, PR template, `docs/release-channels.md` |
| S2   | WebFlash       | Additive bundle: tracking file, D1 + D2 (LICENSE, NOTICE, README §License), SUPPORT.md, CONTRIBUTING.md, extended issue templates, PR template |
| S3   | esphome-public | README front door per D5; displaced content under docs/ with `docs/README.md` index; every inbound reference repointed |
| S4   | WebFlash       | README front door per D5; link esphome-public `docs/release-channels.md` and TROUBLESHOOTING.md prominently |
| S5   | esphome-public | Link checker CI: one new workflow over kept docs, ignore list for byte-stable evidence documents and archive index paths |
| S6   | WebFlash       | Link checker CI: as S5; ignore list covers the two release gate records and archive index paths |
| S7   | WebFlash       | `docs/security/advisory-default-credentials-DRAFT.md` per D4; DRAFT in title and body; not linked from any user-facing surface |

## Execution log (esphome-public steps)

| Step | Status   | PR | Notes |
|------|----------|----|-------|
| S1   | EXECUTED | [#794](https://github.com/sense360store/esphome-public/pull/794) | Additive bundle: tracking file, D6, SUPPORT.md, CONTRIBUTING.md, issue templates, PR template, `docs/release-channels.md` |
| S3   | PENDING  | —  | |
| S5   | PENDING  | —  | |

WebFlash steps (S2, S4, S6, S7) are tracked in the WebFlash repository's
copy of this file.

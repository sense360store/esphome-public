# SENSE360-CANONICALISATION-001 PR 05 — failure triage and board audit

Programme: `SENSE360-CANONICALISATION-001` (authority: `sense360store/SOT`).
Recorded against `sense360store/esphome-public` main
`301a2ffc49d80f44244f4cd0ad56dbcf90cfe4ad`.

This is PR 05's **first deliverable**, required by the charter's
`upstream_ci_baseline.triage_rule` before anything is changed. Every
pre-existing failure is classified before any test is edited, because
silencing a test that is detecting real drift destroys the evidence
instead of resolving it.

Evidence level of everything below: **static inspection, test execution
and diff comparison only**. No hardware, bench, compliance or release
claim is made or implied, and no evidence classification in
`config/hardware-catalog.json` is upgraded.

## 1. Count reconciliation — the 17-vs-16 discrepancy

Resolved: **16 is correct**.

| Source | Count | Why |
|---|---|---|
| `unittest` tally | `failures=16, errors=0` | authoritative |
| PR #851 body | 16 | correct |
| Prior session report | 17 | **wrong** |

The 17th line was a grep artefact, not a failure.
`scripts/check_fallback_ap_password.py` line 128 prints a string beginning
`ERROR: banned fallback-AP password literal(s) found`. A **passing** unit
test exercises that detection path, so the string reaches stdout, and a
`grep '^(FAIL|ERROR):'` over the suite output matched it as though it were
a unittest error.

**There is no fallback-AP credential failure**, and there was never one:

- the guard run standalone reports `OK: no banned fallback-AP password
  literals` and exits `0`;
- it also exits `0` at `9324338` and at `8609144`, so it was not failing
  before #851 either.

Reported under the charter's `credential_check_rule`, which applies
"whether or not the check turns out to be genuinely failing". Nothing was
touched. The lesson recorded: use the runner's own tally, not a grep over
its output.

## 2. Triage of the 16 real failures

### Class (a) — test correctly detecting real drift · 15 failures · mapped to PR 06

All fifteen concern one config string, `Ceiling-POE-AirIQ-RoomIQ`, across
`test_preview_publish_plan`, `test_preview_release_notes_drafts`,
`test_preview_publish_results`, `test_preview_release_targets`,
`test_release_preview_unblock_all_bundles` and `test_roadmap_status_doc`.

Representative evidence:

```
test_catalog_publish_rows_match_promotion_state
  AssertionError: 'preview' != 'production'
test_rows_are_hidden_candidate_not_buyable
  AssertionError: False != True
```

The tests hold a `PROMOTED_CONFIGS` constant that includes this config and
assert `status: production` with stable posture; the catalogue declares
`preview`. One side is stale and the tests are correctly detecting it.

**Preserved, not silenced. Mapped to PR 06**, whose scope is reconciling
configuration catalogues and build declarations.

**Boundary note.** Both repair directions are constrained, which is why
this is not resolved here:

- moving the **catalogue** to `production` is a release/channel promotion
  — **owner-only** under the absolute boundaries;
- moving the **tests** to expect `preview` is editing a failing test green,
  which the triage rule forbids without classification and which would
  destroy the drift evidence.

PR 06 determines the authoritative side from the build declarations and
the WebFlash manifest, and brings the owner a promotion decision **only if
the catalogue is the side that must move**.

### Class (b) — test stale on its own terms · 1 failure · fixed in PR 05

`test_every_in_scope_consumer_default_resolves_to_core_i2c`
(`package='airiq.yaml'`, `substitution='airiq_i2c_id'`).

```
AssertionError: None != 'core_i2c'
```

The test's own comment asserted that `packages/expansions/airiq.yaml`
"is the generic base driver … and stays authoritative here". That stopped
being true when AIRIQ-HW-RECONCILE-001 converted the file to a **thin
alias**: its header now records that it has no live binder and resolves to
`packages/boards/s360-210-airiq.yaml`, which declares
`airiq_i2c_id: core_i2c`. The default was correct; the test was asserting
against a premise the tree no longer held.

Fixed by **relocating the coverage, not deleting it**. Re-declaring
`airiq_i2c_id` in the alias would have satisfied the assertion while
recreating exactly the duplicate truth the reconciliation removed. Instead:

- the alias entry is removed from `SHARED_I2C_CONSUMER_DEFAULTS`, with the
  reason recorded inline;
- the board package entry — which owns the value — remains;
- a new guard, `test_alias_only_consumers_do_not_redeclare_the_default`,
  pins that the alias must **not** declare the substitution, **must**
  include the board package, and that the board package owns it as
  `core_i2c`. So the assertion cannot be "restored" by adding a duplicate.

### Class (c) — unrelated to the programme · 0 failures

None. Every failure fell into (a) or (b).

## 3. Board audit

Eleven board SKUs in `config/hardware-catalog.json`; sixteen files in
`packages/boards/` after this PR.

### 3.1 Non-canonical board SKU inventory — the confirmed PR 05 target

The SOT identity schema admits a board SKU only as `^S360-[0-9]{3}$`.
Five substitutions declared values outside it. All are corrected to the
catalog identity, which is authoritative for board identity:

| File | Substitution | Was | Now |
|---|---|---|---|
| `s360-200-roomiq-radar.yaml` | `roomiq_presence_module_sku` | `S360-PRES-C` | **`S360-200`** |
| `s360-210-airiq.yaml` | `airiq_module_sku` | `S360-AIR-C` | **`S360-210`** |
| `s360-211-ventiq.yaml` | `ventiq_module_sku` | `S360-BATH-B` | **`S360-211`** |
| `s360-300-led.yaml` | `led_ring_sku` | `S360-LED-C` | **`S360-300`** |
| `s360-300-led-mic-ceiling.yaml` | `led_voice_ring_sku` | `S360-LED-V-C` | **`S360-300`** |

`S360-BATH-B` additionally carried banned Base/Pro tier terminology.

**This changes customer-visible diagnostic values.** The Module SKU
entities will report the canonical SKU instead of the legacy variant
string. That is the intended effect of "remove unsupported variant
terminology", and it is a correction of identity, not a change of
behaviour, entity name, or entity id. Flagged explicitly because a device
in Home Assistant will show a different value after reflash.

### 3.2 Recorded for PR 06 — not decided here

`S360-LED-V-C` named a board with **no entry in the hardware catalog**.
The file is SKU-aligned to `s360-300-*`, so the board identity is
`S360-300` and the value is corrected accordingly. Whether a distinct
voice/mic ring board should exist at all is an **unowned-configuration
question recorded for PR 06 classification**. It is not decided here, and
no hardware inference was made: the catalog is the authority for what
boards exist, and it lists only `S360-300`.

### 3.3 Orphan board packages removed

Two files had **zero references of any kind** — no YAML, test, doc,
config, or workflow — and are absent from the `v1.0.0` release tag, so
they are internal, unreleased and unreferenced under the charter's
deletion policy:

- `packages/boards/s360-100-core-ceiling-s3.yaml`
- `packages/boards/s360-100-core-poe.yaml`

`packages/boards/s360-210-airiq-no-sfa40.yaml` was **not** removed despite
having no YAML consumer: two test modules reference it, so it is not
unreferenced. It also touches OD-SOT-008 (SFA40 fitment, open on hardware
evidence); removing it is deferred, and nothing here decides SFA40
fitment either way.

### 3.4 Packages per SKU — the remaining consolidation

| SKU | Files | Note |
|---|---|---|
| S360-100 | 2 | was 4; two orphans removed |
| S360-200 | 6 | composition sub-layers, not duplicates |
| S360-210 | 4 | includes the SFA40 variant retained above |
| S360-211 | 1 | canonical |
| S360-300 | 2 | base + mic-ceiling (see 3.2) |
| S360-410 | 1 | canonical |
| S360-310/311/312/320/400 | 0 | **no board package exists** |

The S360-200 and S360-210 multiplicities are composition sub-layers
included by the canonical package, not competing board definitions; the
include graph was traced to confirm this rather than inferred from
filenames.

**Five catalogued board SKUs have no board package at all** — the four fan
drivers and the 240V PSU. That is recorded as a PR 06 input: a catalogued
board with no active package is the inverse of the duplicate problem, and
classifying it needs the firmware-configuration contract, not the board
contract.

## 4. Interim CI baseline result

| | |
|---|---|
| Baseline | main `301a2ff`, 16 failures |
| This branch | 15 failures |
| **Introduced** | **0** |
| Fixed | 1 (the class-(b) i2c test) |

Measured by running the full suite on both and diffing sorted failure
sets, per the charter's `interim_baseline` rule. The interim baseline is
temporary and expires at PR 06, where a genuinely green suite is an exit
condition.

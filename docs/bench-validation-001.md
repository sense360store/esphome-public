# BENCH-VALIDATION-001 — bench proofs for the four pending boards

**Goal:** unlock all 9 `hardware-pending` configs the proper way — one bench
proof per physical board, following the `PACKAGE-TRIAC-001` precedent
([archived](archive-index.md); guard tests live on in
`tests/test_package_triac_001_operator_bench_proof.py`).

**Bench order (easiest → most serious):** S360-300 LED → S360-312 Fan DAC →
S360-311 Fan PWM → S360-310 Fan Relay. Boards are independent; any order and
one board per sitting is fine.

**Channel posture on promotion (mirrors `COMPLIANCE-001`):** LED, Fan DAC,
and Fan PWM promote to **preview** (low-voltage boards). Fan Relay promotes
to **experimental only** (mains-adjacent contact switching, same lane as
FanTRIAC; never stable).

## Rules that never bend

- **Attestations are owner-authored only** — written by the owner, at the
  bench, in their own words. Agents never author, edit, complete, or
  summarise attestation content or any capture-table measurement. Templates
  ship with those cells empty
  ([`docs/standing-invariants.md`](standing-invariants.md)).
- **A board's configs promote only when its proof shows every step A–E
  recorded PASS and a non-empty owner attestation in section F.**
- **Authorship is verified before promotion.** The commits that filled the
  capture tables and attestation must not be agent-authored; if authorship
  is ambiguous, the loop STOPs and asks the owner to confirm on the PR.
- **Promotion PRs are held for owner review** — never auto-merged.
- **No kit entries.** Kit visibility is a separate owner decision guarded by
  the kit-served-consistency tests. Promotion makes configs buildable and
  releasable; releasing is the normal pipeline
  ([`docs/RELEASE-PIPELINE.md`](RELEASE-PIPELINE.md)), and configs surface
  to customers only when the owner also gives them kit entries.

## Board → proof → configs

| Board | Proof file (docs/hardware/) | Configs promoted | Channel |
|---|---|---|---|
| S360-300 LED | [`PACKAGE-LED-300-001-operator-bench-proof.md`](hardware/PACKAGE-LED-300-001-operator-bench-proof.md) | `Ceiling-POE-RoomIQ-LED` | preview |
| S360-312 Fan DAC | [`PACKAGE-FANDAC-312-001-operator-bench-proof.md`](hardware/PACKAGE-FANDAC-312-001-operator-bench-proof.md) | `Ceiling-POE-FanDAC`, `Ceiling-POE-VentIQ-FanDAC-RoomIQ`, `Ceiling-POE-AirIQ-FanDAC-RoomIQ` | preview |
| S360-311 Fan PWM | [`PACKAGE-FANPWM-311-001-operator-bench-proof.md`](hardware/PACKAGE-FANPWM-311-001-operator-bench-proof.md) | `Ceiling-POE-FanPWM`, `Ceiling-POE-VentIQ-FanPWM-RoomIQ`, `Ceiling-POE-AirIQ-FanPWM-RoomIQ` | preview |
| S360-310 Fan Relay | [`PACKAGE-FANRELAY-310-001-operator-bench-proof.md`](hardware/PACKAGE-FANRELAY-310-001-operator-bench-proof.md) | `Ceiling-POE-VentIQ-FanRelay-RoomIQ`, `Ceiling-POE-AirIQ-FanRelay-RoomIQ` | experimental |

The room-bundle FanDAC promotions additionally owe the `FANDAC-I2C-ADDR-001`
I²C address bench evidence
([`docs/hardware/fandac-i2c-address-verification.md`](hardware/fandac-i2c-address-verification.md))
— completed at the same bench sitting, recorded in its own template.

## Step ledger

| Step | What | Status |
|---|---|---|
| T1 | Create the four proof templates (empty capture tables, empty attestations) + this tracking file. One held PR. | **EXECUTED** — this PR |
| T2 | Promote S360-300 LED (proof complete → configs `hardware-pending` → release-ready, channel preview; contract tests + derived matrices updated; held PR) | PENDING — awaiting bench |
| T3 | Promote S360-312 Fan DAC (as T2, channel preview; `FANDAC-I2C-ADDR-001` evidence also required for the room bundles) | PENDING — awaiting bench |
| T4 | Promote S360-311 Fan PWM (as T2, channel preview) | PENDING — awaiting bench |
| T5 | Promote S360-310 Fan Relay (as T2, channel **experimental** only) | PENDING — awaiting bench |
| T6 | Closure — verify all four proofs + promotions, all gates green, mark programme COMPLETE | PENDING |

T2–T5 run one board per session, in any order, only when that board's proof
is ready (detection: every step A–E marked PASS + non-empty owner-authored
section F + owner authorship verified + board not yet promoted). Per-board
promotion edits: `config/product-catalog.json` and
`config/webflash-builds.json` status/rows, release-dropdown exposure via the
single-source mechanism (`config/webflash-builds.json`, listed by
`scripts/list_release_targets.py`), lock-step contract tests, and derived
matrices regenerated via their scripts (`scripts/generate_firmware_matrix.py`,
`scripts/report_firmware_build_gaps.py`).

**Standing-invariants interaction (flagged for owner review at T3–T5):** the
"Fans are preview-only … no fan row in `config/webflash-builds.json`"
gate in [`docs/standing-invariants.md`](standing-invariants.md) (the
fan-token guardrail) currently forbids exactly the build-matrix rows the fan
promotions add. Each fan promotion PR must therefore also revise that
invariant's live text for the promoted board — an owner decision, which is
why every promotion PR is held for owner review, never auto-merged.

## Session protocol

Pull main. If this tracking file is absent → T1. Else if any
completed-but-unpromoted proof exists → promote that board (T2–T5). Else if
all four boards are promoted → T6. Else STOP and report which proofs are
still awaiting bench work (normal between bench sessions, not an error).

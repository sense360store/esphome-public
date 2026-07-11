# SPIKE-PROVISIONING-BENCH-001 — validation record

**Programme:** `SEC-ESP-PROVISIONING-001` (proposed ADR:
[`docs/adr/ADR-SEC-ESP-PROVISIONING-001.md` on draft PR #821](https://github.com/sense360store/esphome-public/pull/821)).
Procedure of record:
[`SPIKE-PROVISIONING-BENCH-001-procedure.md`](SPIKE-PROVISIONING-BENCH-001-procedure.md)
— run the checks exactly as written there; this file is the capture side
only.

**Status: PENDING — awaiting bench. No step has been run; no evidence has
been recorded. Every capture cell, every result line, the spike
disposition table, and the operator attestation below are intentionally
empty.**

**Rules (from [`docs/standing-invariants.md`](../standing-invariants.md)
and the procedure):**

- Capture cells and result lines are filled **at the bench, by the
  operator** — never machine-written, never reconstructed afterwards.
- Section G (attestation) is **owner-authored only**, in the owner's own
  words. Agents never author, edit, complete, or summarise it.
- A FAIL is recorded as a FAIL and routed per procedure §2 — never
  reinterpreted as a qualified pass.
- This record proves firmware/platform mechanism behaviour on the pinned
  build and bare bench hardware only. It makes no safety / EMC /
  compliance / commercial claim, closes nothing of SPIKE-P6, and does not
  substitute for the implementation-stage test tiers (ADR §16) or the
  pending R-D4 attestation.

---

## A. Identity and environment

| Capture | Value |
|---|---|
| Operator | |
| Date(s) of bench work | |
| Unit A — S360-100 R4 serial / marking | |
| Unit B — S360-100 R4 serial / marking | |
| PSU used (S360-410 serial / marking) | |
| Repo SHA the bench composition was based on | |
| ESPHome version (pinned) | |
| aioesphomeapi version | |
| esptool version | |
| Browser + version (WebFlash checks) | |
| Released artifact + version flashed for W1 legs | |
| Home Assistant version (test instance) | |
| `bench-spike.yaml` attached as evidence (path/hash) | |
| Evidence archive location | |

## B. Check results

Fill each Observed cell and each result line at the bench. Expected / pass
/ fail definitions live in the procedure — do not restate or reinterpret
them here.

### V-01 — First claim (stock set-key claim flow)

| Capture | Observed |
|---|---|
| Plaintext connect before set-key (accepted?) | |
| Set-key request outcome | |
| Serial log shows PSK save/activate path | |
| Noise connect with set key (established?) | |
| Entities readable over noise session | |

**V-01 result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

### V-02 — API runtime key: persistence, plaintext lockout, reset clear

| Capture | Observed |
|---|---|
| Unit A: plaintext refused after set-key, boot 1 | |
| Unit A: plaintext refused after set-key, boot 2 | |
| Unit A: wrong key refused | |
| Unit A: correct key accepted, both boots | |
| Unit B: full V-01 + lockout sequence outcome | |
| Unit A key ≠ unit B key | |
| Unit A: factory reset (SW3) → plaintext accepted again | |

**V-02 result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

### V-03 — Ownership record / UUID persistence substrate

| Capture | Observed |
|---|---|
| Marker value written | |
| Read-back after software reset | |
| Read-back after power cycle 1 | |
| Read-back after power cycle 2 | |
| Read-back after power cycle 3 | |
| Read-back after power cycle 4 | |

**V-03 result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

### V-04 — OTA password: runtime application and enforcement

| Capture | Observed |
|---|---|
| Harness applied bench OTA password (serial line) | |
| Unit A: OTA with no password | |
| Unit A: OTA with wrong password | |
| Unit A: OTA with correct password | |
| Unit A: repeat of the three attempts after OTA + reboot | |
| Unit B: three attempts (different password) | |
| Unit A password ≠ unit B password | |

**V-04 result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

### V-05 — Fallback AP behaviour

| Capture | Observed |
|---|---|
| Open-join attempts (per cycle, count + outcomes) | |
| Wrong-password join attempts (outcomes) | |
| Correct-password join (outcome) | |
| Captive portal reachable after join | |
| Cycles tested (≥ 5) | |
| Open-AP window observed before password effective (duration, if any) | |
| Station reconnection after bench WiFi restored | |

**V-05 result:** _PENDING — to be recorded by the operator (PASS / FAIL —
a FAIL here routes to the OD-07 contingency per procedure §2)._

### V-06 — Ownership persistence after normal reflash

| Capture | Observed |
|---|---|
| Leg 1: exact no-erase flash command used | |
| Leg 1: PSK still enforced after reflash | |
| Leg 1: OTA password still enforced after reflash | |
| Leg 1: NVS marker intact after reflash | |
| Leg 2: WebFlash path used + exact dialog wording / erase-option state | |
| Leg 2: saved WiFi credentials survived (rejoined without re-provisioning?) | |
| Leg 2: non-erase path exists at all? (verbatim finding) | |

**V-06 result:** _PENDING — to be recorded by the operator (PASS / FAIL /
UNDETERMINED for leg 2 per procedure)._

### V-07 — Ownership removal after erase

| Capture | Observed |
|---|---|
| Leg 1 (esptool erase): plaintext accepted, marker default, no saved WiFi | |
| Leg 2: WebFlash erase path used + exact dialog wording / erase-option state | |
| Leg 2: WiFi credentials destroyed (no rejoin; setup surface up) | |
| Leg 3: power-cycle factory reset fired | |
| Leg 3: post-reset state clean (plaintext accepted, marker default, no saved WiFi) | |

**V-07 result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

### V-08 — Boot behaviour after update

| Capture | Observed |
|---|---|
| Pre-update image SHA-256 | |
| Post-update image SHA-256 | |
| OTA with correct password (outcome) | |
| Post-update boot: plaintext probe outcomes (loop) | |
| Post-update boot: unauthenticated-OTA probe outcomes (loop) | |
| Marker value unchanged | |
| Correct key + correct OTA password still accepted (incl. after one more power cycle) | |

**V-08 result:** _PENDING — to be recorded by the operator (PASS / FAIL)._

### V-09 — Fail-closed OTA: boot-window measurement

| Capture | Observed |
|---|---|
| `on_boot` priority used for password application | |
| Boots probed (count; cold/warm split) | |
| Probe cadence / max gap around boot moment | |
| Attempts classified: refused / accepted-then-auth-rejected / proceeded past auth | |
| Worst-case unauthenticated window (ms), or "none observed in N boots" | |
| Clock-alignment method (probe log ↔ serial log) | |

**V-09 result:** _PENDING — to be recorded by the operator (CONCLUSIVE /
INCONCLUSIVE, and if conclusive: window / no-window). A measured window
routes to the OD-08 contingency per procedure §2._

### V-10 — Physical-presence mechanisms (bare board)

| Capture | Observed |
|---|---|
| SW3 press/release events visible in log | |
| Normal SW3 press does not reset device | |
| Boot-time SW3 hold behaviour (recorded) | |
| Single power cycle → no factory reset | |
| Two spaced power blips → no factory reset | |
| Deliberate pattern (params: N = __, interval = __) → reset fired, unit A | |
| Deliberate pattern → reset fired, unit B | |

**V-10 result:** _PENDING — to be recorded by the operator (PASS / FAIL).
This check closes nothing of SPIKE-P6 (enclosure ergonomics, PSU-variant
power-cycle reliability remain open)._

## C. Spike disposition

To be filled by the operator only after Section B is complete. This table
records bench outcomes; any programme-status change is carried to SOT by
the owner in a separate action per the operating model — never from this
file.

| Spike | Fed by | Bench outcome | Notes |
|---|---|---|---|
| SPIKE-P1 | V-01, V-02 | | |
| SPIKE-P2 | V-04, V-05, V-09 | | |
| SPIKE-W1 (bench remainder) | V-06, V-07 | | |
| SPIKE-P6 | — not covered — | **remains OPEN** | Pre-marked: nothing in this record may close it. |

## D. Contingency outcomes (only if invoked)

| Contingency | Invoked? | Evidence reference |
|---|---|---|
| OD-07 — fallback AP disabled on owned devices (V-05 fail / open window) | | |
| OD-08 — network OTA fail-closed until owned (V-09 measured window) | | |

## E. Evidence index

List every captured file (serial logs, shell transcripts, screenshots,
photos/video, probe outputs, `bench-spike.yaml`) with its check ID and a
hash or storage reference.

| Check | File | Hash / reference |
|---|---|---|
| | | |

## F. Deviations from the procedure

Any step run differently from the procedure text is recorded here by the
operator (what changed, why, effect on validity). An empty table with a
completed Section B means "no deviations".

| Check / step | Deviation | Impact |
|---|---|---|
| | | |

---

## G. Operator attestation

> **To be completed by the owner only, at the bench, in their own words:**
> what was run, what was observed, which spike outcomes they stand behind,
> and whether the results are consistent with the ADR direction. The entry
> cells below are intentionally empty — no attestation content is
> machine-written, ever. This record supports ADR acceptance only when
> Sections A–F are complete and this section contains non-empty
> owner-authored text.

| Field | Entry |
|---|---|
| Operator | |
| Date | |
| Units under test | |
| Statement | |
| Signature | |

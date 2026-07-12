# SPIKE-PROVISIONING-BENCH-001 — bench spike harness

**TEST-ONLY — NOT FOR RELEASE OR CUSTOMER USE**

Programme: `SEC-ESP-PROVISIONING-001`
(ADR: draft [PR #821](https://github.com/sense360store/esphome-public/pull/821) — status **Proposed**).
Procedure of record: `docs/hardware/SPIKE-PROVISIONING-BENCH-001-procedure.md`
on draft [PR #822](https://github.com/sense360store/esphome-public/pull/822)
— **this README does not duplicate it; run the checks exactly as written
there.** Results are entered **manually by the owner** into the intentionally
empty validation record
(`docs/hardware/SPIKE-PROVISIONING-BENCH-001-validation-record.md`, PR #822).
Nothing in this directory records, claims, or implies any bench outcome.

This harness is the committed form of the "bench spike image" procedure §3
defines. It exercises **stock ESPHome mechanisms only** (ADR Appendix D
E-1…E-8): runtime API set-key, runtime OTA/AP password setters, NVS
persistence, stock factory reset. It is **not** the production provisioning
architecture — no ownership state machine, no claim-window gating, no
bootstrap invalidation, no production UUID/credential generation, no
recovery/transfer. Guard tests
(`tests/test_spike_provisioning_bench_harness.py`) prove it cannot enter
product compositions, release matrices, WebFlash declarations, or the
publication workflows.

## Contents

| File | Purpose |
|---|---|
| `bench-spike.yaml` | The bench harness ESPHome config (S360-100 R4 / ESP32-S3) |
| `secrets.example.yaml` | Template for the local, gitignored bench `secrets.yaml` |
| `bench_host.py` | Bench-only host helper (stock aioesphomeapi operations) |
| `README.md` | This file |

## Hardware connection

- Sense360 Core **S360-100 R4** (bare board, per procedure §3), powered via
  the S360-410 PoE PSU or bench 5 V.
- USB to **UART0** for the first flash and for serial evidence capture
  (`V-XX-serial.log`).
- SW3 = Boot / IO0 tactile switch (V-10); GPIO46 fan-status LED blinks
  100 ms every second as the liveness confirmation (H-07).
- Isolated bench WiFi network; a second WiFi client device for the V-05
  AP-join checks.

## Build

Pinned toolchain: **ESPHome 2026.6.5** — the exact version the ADR desk
evidence inspected. Record the exact version used in the validation record.

```bash
pip install "esphome==2026.6.5"

cd tests/bench/sec_esp_provisioning_001
cp secrets.example.yaml secrets.yaml   # fill in ISOLATED bench WiFi values

esphome config bench-spike.yaml        # must report "Configuration is valid!"
esphome -s bench_git_sha "$(git rev-parse --short=12 HEAD)" \
    compile bench-spike.yaml
```

The built image stays local (`.esphome/` is gitignored). **Never publish,
release, or WebFlash-distribute this image.**

## Flash

First flash on a blank board, over USB, after the full erase the procedure
requires (V-01 step 1):

```bash
esptool --port /dev/ttyACM0 erase_flash
esphome -s bench_git_sha "$(git rev-parse --short=12 HEAD)" \
    run bench-spike.yaml --device /dev/ttyACM0
```

Serial log capture for evidence:

```bash
esphome logs bench-spike.yaml --device /dev/ttyACM0 | tee V-XX-serial.log
```

## Throwaway test credentials

Every credential in a bench run is a **throwaway value supplied at
execution time** — nothing is committed, nothing is logged:

- **API noise key** — `python3 bench_host.py gen-key` prints a fresh
  32-byte base64 key (record it as evidence per V-01 step 3; it is
  throwaway). Apply with `set-api-key`.
- **OTA / AP passwords** — supplied at a no-echo prompt, or via an
  environment variable you set for that run
  (`--value-env BENCH_OTA_PW` style). Generate e.g. with
  `python3 -c 'import secrets; print(secrets.token_urlsafe(18))'`.
- **Bench WiFi** — local `secrets.yaml` only (gitignored at every depth).

## Harness actions ↔ procedure checks (V-01…V-10, PR #822)

| Harness capability | Procedure check(s) |
|---|---|
| H-01 empty-key API (`encryption:` with no key); `bench_host.py set-api-key` | V-01, V-02 (SPIKE-P1) |
| H-04 synthetic record; `set-record` / `clear-record`; `Bench Record Valid/Present` | V-03 (AD-01 substrate only) |
| H-02 OTA runtime password; `set-ota-password`; boot re-apply lambda | V-04, V-09 (SPIKE-P2 OTA leg) |
| H-03 AP runtime password; `set-ap-password`; boot re-apply lambda | V-05 (SPIKE-P2 AP leg, OD-07 evidence) |
| H-04 persisted globals + H-01 native PSK persistence | V-06 leg 1 & leg 2 read-back (SPIKE-W1 bench half) |
| H-06 stock factory reset (`reset-test`, SW3 long-hold) | V-02 step 6, V-07 legs 1/3 |
| H-02 enforcement across OTA (`esphome upload` with the throwaway password) | V-08 |
| H-02 boot-window probing target (`on_boot` priority 800 — record it) | V-09 |
| H-07 SW3 events, power-cycle-count reset (N=5 within 10 s — record params), GPIO46 LED | V-10 (bare board only; **SPIKE-P6 stays open**) |
| H-05 diagnostics (`inspect`, `reboot-test`) | evidence capture in every check |

**Steps that must run through production WebFlash instead of this
harness:** the V-06 leg 2/leg 3 ordinary installs ("Erase device"
unchecked), the V-07 leg 2 erase-checked install and leg 4 rescue path —
those checks interrogate the real installer against the current published
release artifacts, which this harness cannot and must not stand in for.
Only the before/after NVS read-back around those legs uses this image.

**Bench assertions (not unit-testable here, results never pre-claimed):**
actual NVS erasure on factory reset, plaintext lockout after set-key,
boot-window timing, AP pre-enforcement, marker survival across reflash.
Each is recorded PASS/FAIL by the operator in the validation record only.

## Host helper

```bash
python3 bench_host.py gen-key
python3 bench_host.py --host <ip> set-api-key
python3 bench_host.py --host <ip> --prompt-key inspect
python3 bench_host.py --host <ip> --prompt-key set-ota-password
python3 bench_host.py --host <ip> --prompt-key set-ap-password
python3 bench_host.py --host <ip> --prompt-key set-record --uuid "BENCH-0000-SYNTHETIC"
python3 bench_host.py --host <ip> --prompt-key reboot-test
python3 bench_host.py --host <ip> --prompt-key reset-test   # typed confirmation
```

Bench-only; stock `aioesphomeapi` operations exclusively; no cloud, no
telemetry, no credential output (the deliberate exception: `gen-key`
prints the fresh throwaway key it generated, per V-01 step 3).

## Clean-up (after the bench, procedure §3)

```bash
rm -f tests/bench/sec_esp_provisioning_001/secrets.yaml   # bench WiFi values
rm -rf tests/bench/sec_esp_provisioning_001/.esphome      # build artifacts
unset BENCH_OTA_PW BENCH_AP_PW                            # any run-time env values
```

Then factory-reset / fully erase the bench units so no throwaway credential
outlives the session, and hand the captured evidence to the owner for
manual entry into the validation record (owner-authored attestation only —
never machine-written).

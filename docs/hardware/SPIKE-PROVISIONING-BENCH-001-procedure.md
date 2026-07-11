# SPIKE-PROVISIONING-BENCH-001 — combined provisioning spike bench procedure

**Programme:** `SEC-ESP-PROVISIONING-001` (proposed ADR:
[`docs/adr/ADR-SEC-ESP-PROVISIONING-001.md` on draft PR #821](https://github.com/sense360store/esphome-public/pull/821)
— the ADR file exists only on that unmerged draft branch; all `§` references
below cite that document at its PR-821 revision, v3).

**Status: PROCEDURE ONLY — no bench work has been performed. No step has
been run; no result, measurement, or observation is recorded or implied
anywhere in this file. The companion record
([`SPIKE-PROVISIONING-BENCH-001-validation-record.md`](SPIKE-PROVISIONING-BENCH-001-validation-record.md))
ships with every capture cell and the operator attestation intentionally
empty.**

| Field | Value |
|---|---|
| Covers | **SPIKE-P1** (full bench scope) · **SPIKE-P2** (full bench scope) · **SPIKE-W1** (remaining **bench** portion only — the desk/source portion is treated as complete per ADR §10) |
| Does NOT cover | **SPIKE-P6** (enclosure ergonomics on assembled hardware, PoE and 240 V PSU power-cycle reliability) — remains a separate pending spike. Check V-10 below touches bare-board presence mechanisms only and closes nothing of SPIKE-P6. |
| Device under test | Sense360 Core, SKU **S360-100**, rev R4 ([`s360-100-r4-core.md`](s360-100-r4-core.md)); PoE via S360-410 |
| Bench firmware | Locally compiled **bench spike image** (defined below) at a recorded repo SHA and pinned ESPHome version ([`requirements-dev.txt`](../../requirements-dev.txt)) — plus, for the SPIKE-W1 checks, the current published release artifacts flashed through production WebFlash |
| Attestation rule | The record's attestation section is **owner-authored only**. Agents never author, edit, complete, or summarise attestation content or any capture-table measurement ([`docs/standing-invariants.md`](../standing-invariants.md)). |
| Execution rule | Bench checks are **owner-run or owner-observed** (ADR §10, SPIKE-P1 row). |

**Type:** bench procedure. Docs only. This file asserts no firmware,
catalog, manifest, release, or WebFlash change, and makes no safety / EMC /
compliance / commercial claim. It implements nothing: the ADR remains
**Proposed**, implementation must not begin before acceptance
(operating-model rule, ADR §18), and nothing in this procedure or its
record creates, claims, or substitutes for the implementation-stage test
tiers (contract tests CT-01…CT-15, multi-device bench, ADR §16) or for the
separate pending **R-D4** attestation
([`docs/rebuild-clean-credentials-001.md`](../rebuild-clean-credentials-001.md)).

---

## 1. What this bench proves — and what it cannot

The provisioning **gating component does not exist yet** (correct and
required: the ADR is Proposed). This bench therefore validates the **stock
ESPHome mechanisms and platform semantics that ADR Option F depends on**,
on the pinned build and real S360-100 R4 hardware — exactly the evidence
ADR §10 defines as the remaining acceptance blockers for SPIKE-P1,
SPIKE-P2, and SPIKE-W1.

Where a checklist claim names behaviour the future gating component will
own (first-claim *gating*, UUID *generation logic*, fail-closed *policy
enforcement*), this bench validates the **underlying platform mechanism
and persistence substrate** and says so explicitly in that check. Final
proof of component behaviour happens at implementation stage (ADR §16)
and is not claimed here — per the no-false-proof standing invariant.

Claim-to-check map:

| Claim to prove | Check | Level proven by this bench |
|---|---|---|
| First claim | V-01 | Stock runtime set-key claim flow end-to-end (SPIKE-P1). Claim-*gating* (window, presence) = implementation stage. |
| API runtime key generation | V-02 | Runtime-set key, NVS persistence, plaintext lockout, factory-reset clear (SPIKE-P1). |
| UUID generation | V-03 | NVS persistence substrate for the AD-01 ownership record/UUID. UUID *generation logic* = implementation stage. |
| OTA password generation | V-04 | Runtime `set_auth_password()` path, enforcement, persistence (SPIKE-P2). On-device RNG generation recipe = implementation stage (CT-15). |
| Fallback AP behaviour | V-05 | Runtime AP password applied before AP starts; protected join semantics (SPIKE-P2 AP fold-in, OD-07 evidence). |
| Ownership persistence after normal reflash | V-06 | NVS survival across serial app-reflash and WebFlash non-erase paths (SPIKE-W1 bench + §13 matrix). |
| Ownership removal after erase | V-07 | NVS destruction by full erase and by WebFlash erase paths (SPIKE-W1 bench + §13 matrix). |
| Boot behaviour after update | V-08 | Credential + record survival and enforcement across an OTA update (§12/§13, CT-09 precursor). |
| Fail-closed OTA behaviour | V-09 | Boot-window measurement for the OD-08 decision: does any unauthenticated OTA acceptance window exist at boot, and how large. |
| Physical-presence requirement | V-10 | Bare-board presence mechanisms (SW3, stock power-cycle-count factory reset) work and are deliberate-action-guarded. SPIKE-P6 stays open. |

## 2. Result routing

- **All checks PASS consistently with the ADR direction** → the owner may
  record SPIKE-P1, SPIKE-P2, and the SPIKE-W1 bench remainder as complete
  in the validation record; ADR acceptance then follows the ADR §18 path
  (owner accepts; **SOT records the acceptance**; SPIKE-P6 must still
  complete first). This repo never independently updates programme status.
- **V-05 fails (AP password not enforceable before the AP accepts)** →
  accepted contingency **OD-07** applies: fallback AP is disabled on owned
  devices. Not an ADR-direction failure; record the evidence.
- **V-09 finds an unauthenticated OTA boot window** → accepted contingency
  **OD-08** applies: network OTA fail-closed (disabled until owned). Not an
  ADR-direction failure; record the window measurement.
- **V-01/V-02 fail (set-key mechanism does not work on the pinned
  build/board)** → STOP; ADR §17 step 2 applies (ADR amended, back to the
  owner). Do not improvise an alternative mechanism at the bench.
- Any other FAIL → record it, stop the affected check, and route to the
  owner. Never reinterpret a FAIL as a qualified pass.

## 3. Hardware, tooling, and bench-image prerequisites

**Hardware**

- 2 × S360-100 R4 Core (two units: credential values established in
  V-02/V-04/V-05 must differ across units — a uniqueness sanity check
  foreshadowing CT-01, not a substitute for it). Record serials.
- 1 × S360-410 PoE PSU (bench power) + USB access to UART0.
- Bench WiFi network (isolated LAN; no internet required after downloads —
  OD-01 posture) and a second client device with WiFi (phone or laptop)
  for AP-join checks.
- Bench host: Chromium-based desktop browser (Web Serial, for the
  WebFlash checks), Python 3, `esptool`, ESPHome CLI at the pinned
  version, `aioesphomeapi` 45.6.0 (the version the ADR's desk evidence
  inspected), Home Assistant test instance.

**Bench spike image (local, throwaway — never committed, never released)**

The operator composes a local `bench-spike.yaml` for the S360-100 R4
(ESP32-S3), compiled with the pinned ESPHome version. It is bench harness
material, not product firmware: it must not be added to `products/`,
`packages/`, the build matrix, or any release, and it is deleted after the
bench. Required surfaces:

1. `api:` with an `encryption:` block and **no key** — the exact
   noise-capable-no-key shape the ADR's desk evidence verified (E-1).
2. `ota:` platform `esphome` with an **empty `password: ""`** — compiles
   the auth path so `set_auth_password()` is callable at runtime (E-4).
3. `wifi:` with bench credentials and an `ap:` fallback block +
   `captive_portal:`. For V-05, an `on_boot` harness lambda (earliest
   practical priority) that applies a bench AP password via the runtime
   `set_ap` setter (E-8), so pre-AP enforcement can be measured.
4. For V-04/V-09, an `on_boot` harness lambda that applies a bench OTA
   password via `set_auth_password()` (E-4/E-5), simulating the
   NVS-loaded credential the future component will apply.
5. A persisted NVS marker for V-03/V-06/V-07/V-08: a `globals` entry with
   `restore_value: true` holding a bench-chosen value (the
   ownership-record/UUID persistence surrogate), plus a service or
   template control to set it at the bench.
6. `factory_reset` components per the pinned ESPHome version's
   documentation: the button/switch platform bound to **SW3 (Boot/IO0)**
   and the stock power-cycle-count trigger (E-6/E-7). Configure the
   power-cycle trigger exactly as documented upstream — do not invent
   parameters.
7. `logger:` at `DEBUG`, serial output available on UART0 for capture.

Record in the validation record: the repo SHA the composition was based
on, the exact ESPHome version, the full `bench-spike.yaml` (as an evidence
attachment — it contains only bench-network and throwaway values, never
production credentials), and both units' serials.

**Release artifacts for SPIKE-W1 checks**

The WebFlash-path checks (V-06 W1 legs, V-07 W1 legs) run against the
current published release artifacts through the production WebFlash site,
because SPIKE-W1's question is about the real installer paths. Note the
released binaries carry the unprovisioned posture
([`docs/security/release-firmware-credential-posture.md`](../security/release-firmware-credential-posture.md)):
no API encryption block, no OTA auth. On those legs the NVS marker is the
**saved WiFi credentials** (entered via captive portal), which the ADR's
desk evidence places in the same NVS store (§5.5) — the procedure states
per leg which marker applies.

**General evidence rules (apply to every check)**

- Serial log captured continuously (`esphome logs` or a serial terminal
  with timestamps) into one file per check: `V-XX-serial.log`.
- Terminal transcripts (commands + full output) saved as `V-XX-shell.txt`.
- Screenshots named `V-XX-<step>-<short-desc>.png`; photos of physical
  actions (button press, power cycling) `V-XX-<step>-photo-*.jpg`.
- Every capture cell in the record is filled at the bench, by the
  operator, or left empty — never reconstructed afterwards.

---

## 4. Checks

### V-01 — First claim (stock set-key claim flow, SPIKE-P1 core)

**ADR sections validated:** §3 (problem), §8.2–8.3 (claim mechanism),
§10 SPIKE-P1 row, §18 acceptance item 1, Appendix D E-1/E-2/E-3/E-9.

**Objective.** Prove on the pinned build/board that a device shipped
noise-capable-with-no-key accepts a key from a plaintext client and
switches to encrypted operation — the end-to-end "first claim" mechanism
Option F builds on. (The presence-gated claim *window* is future
component behaviour and is not claimed here.)

**Steps**

1. Flash unit A with the bench spike image over USB after a full
   `esptool erase_flash`. Boot; join bench WiFi.
2. From the bench host, connect with a **plaintext** aioesphomeapi client
   and confirm the connection is accepted (device is unowned-equivalent:
   no PSK stored).
3. Generate a 32-byte key on the bench host, base64-encode it (bench
   value — record it in the evidence; it is throwaway).
4. Send `noise_encryption_set_key` with that key over the plaintext
   session (aioesphomeapi 45.6.0, per E-3/E-9).
5. Observe the device response and serial log; reconnect **with** the key
   over noise and confirm an encrypted session establishes.

**Expected result.** The set-key request is accepted; the device persists
and activates the PSK (serial log shows the save/activate path per E-2);
a subsequent noise connection with the key succeeds.

**Pass criteria.** All of: plaintext connect succeeded before set-key;
set-key acknowledged; noise session with the set key established and
entities readable.

**Fail criteria.** Any of: set-key rejected or ignored on the pinned
build; device crash/reboot-loop during set-key; noise session with the
set key fails. (FAIL here routes per §2 — STOP, back to owner.)

**Evidence to capture.** `V-01-serial.log`; `V-01-shell.txt` (client
script transcript incl. the set-key call and both connect attempts);
screenshot of the successful encrypted session; the bench key value used.

### V-02 — API runtime key: persistence, plaintext lockout, reset clear (SPIKE-P1 completion)

**ADR sections validated:** §5.2 (constraint 2), §8 robustness row 1,
§10 SPIKE-P1 row ("verify persistence across reboot, verify plaintext
refused after key set, verify factory reset clears"), §11 API-key row,
§12 OWNED boot row, Appendix D E-1/E-2/E-6.

**Objective.** Complete SPIKE-P1: the runtime-set key survives reboot,
plaintext is disabled once a key is set, wrong keys are refused, and only
factory reset removes the key.

**Steps** (continues from V-01 on unit A)

1. Power-cycle unit A. After boot, attempt a **plaintext** API
   connection.
2. Attempt a noise connection with a deliberately **wrong** key.
3. Connect with the correct key; confirm normal operation.
4. Repeat steps 1–3 after a second power cycle (persistence is not a
   one-boot artefact).
5. Repeat V-01 steps 1–5 and this check's steps 1–3 on unit B with a
   **freshly generated** key; confirm the two units' keys differ
   (uniqueness sanity, CT-01 foreshadow).
6. On unit A, trigger factory reset via the SW3-bound `factory_reset`
   button. After reboot, attempt a plaintext connection.

**Expected result.** After a key is set: plaintext refused, wrong key
refused, correct key works, across multiple power cycles. After factory
reset: plaintext accepted again (key cleared with the full NVS erase,
E-6).

**Pass criteria.** All of: plaintext refused on every post-set boot;
wrong key refused; correct key accepted on every post-set boot; unit A
and unit B keys differ; post-factory-reset plaintext connection succeeds.

**Fail criteria.** Any of: plaintext accepted after a key was set (claim
race stays fully open even post-claim — direction-critical FAIL); key
lost across reboot; wrong key accepted; factory reset does not clear the
key.

**Evidence to capture.** `V-02-serial.log` (both units, boots
timestamped); `V-02-shell.txt` (each connect attempt and its outcome);
screenshot of refused-plaintext and refused-wrong-key errors; photo of
the SW3 press for the reset step.

### V-03 — Ownership record / UUID persistence substrate (AD-01 substrate)

**ADR sections validated:** §9 AD-01, §11 Device-UUID row, §12 per-state
rules (persisted ownership record), §13 reset-matrix rows 1–2.

**Objective.** Prove the NVS persistence substrate the AD-01 device UUID
and the §12 ownership record will live in: a persisted preference written
once ("at claim") is stable across reboot and power cycles, and is
destroyed only by the §13 destruction paths (checked in V-07). UUID
*generation* logic is implementation-stage and not claimed.

**Steps**

1. On unit A (re-claimed after V-02 step 6: repeat V-01 so the unit is
   again in an owned-equivalent state), set the bench NVS marker
   (`globals` surrogate) to a recorded bench value via the harness
   control.
2. Reboot (software reset). Read the marker.
3. Power-cycle (full power removal ≥ 10 s). Read the marker.
4. Repeat step 3 three times; read the marker each boot.

**Expected result.** The marker value is identical on every boot.

**Pass criteria.** Marker read-back matches the written value on all ≥ 5
boots, with no re-initialisation to default.

**Fail criteria.** Any boot where the marker is missing, default, or
altered.

**Evidence to capture.** `V-03-serial.log` showing the marker value
logged at each boot; `V-03-shell.txt`; the written bench value.

### V-04 — OTA password: runtime application and enforcement (SPIKE-P2, OTA leg)

**ADR sections validated:** §9 OD-08 (first sentence — OTA enabled only
under the unique runtime password), §10 SPIKE-P2 row, §11 OTA-password
row, Appendix D E-4/E-5.

**Objective.** Prove the runtime OTA password path on the pinned build:
an empty compiled password plus a runtime `set_auth_password()` value
results in an OTA endpoint that rejects unauthenticated and
wrong-password attempts and accepts the correct password. (On-device RNG
generation of the value is implementation-stage, CT-15; the bench applies
a host-generated throwaway value via the harness lambda.)

**Steps**

1. Confirm the bench spike image's `on_boot` harness applied the bench
   OTA password (serial log line from the harness).
2. From the bench host, attempt an OTA upload with **no** password.
3. Attempt an OTA upload with a **wrong** password.
4. Attempt an OTA upload with the **correct** bench password (upload the
   identical bench spike image).
5. After the successful OTA, reboot and repeat steps 2–4 once
   (enforcement persists across the update — precursor to V-08).
6. Run steps 1–4 on unit B with a **different** bench password; confirm
   the two units enforce different values.

**Expected result.** No-password and wrong-password attempts fail
authentication; the correct password authenticates and the upload
completes; behaviour identical after the OTA.

**Pass criteria.** All of: both bad attempts rejected with an auth
failure (not a timeout/other error) on both units and on both sides of
the OTA; correct password succeeds each time.

**Fail criteria.** Any unauthenticated or wrong-password upload
proceeding past authentication; password not enforced after reboot or
after OTA.

**Evidence to capture.** `V-04-serial.log`; `V-04-shell.txt` (all upload
attempts with full CLI output); the two bench password values.

### V-05 — Fallback AP behaviour (SPIKE-P2, AP leg; OD-07 evidence)

**ADR sections validated:** §9 OD-07, §10 SPIKE-P2 row ("also covers the
AP password path"), §11 fallback-AP row, §8 robustness row 6, Appendix D
E-8.

**Objective.** Prove the fallback-AP password can be applied at runtime
**before the AP starts accepting connections** — the OD-07 condition. If
this cannot be proven, the accepted contingency is AP-disabled-on-owned,
not a design failure.

**Steps**

1. Configure unit A's bench image so the fallback AP will activate
   (e.g. bench WiFi SSID made unavailable), with the harness applying
   the bench AP password at boot.
2. Power-cycle. From the second client device, continuously scan for and
   attempt to join the AP **as an open network** from the earliest moment
   the SSID appears.
3. Attempt to join with a **wrong** password.
4. Join with the **correct** bench AP password; load the captive portal.
5. Repeat steps 2–4 across ≥ 5 power cycles (window behaviour must be
   consistent, not lucky).
6. Restore bench WiFi; confirm normal station reconnection.

**Expected result.** The AP is never joinable open or with a wrong
password; the correct password joins; the captive portal functions.

**Pass criteria.** Across all cycles: zero successful open joins, zero
successful wrong-password joins, correct-password join succeeds, captive
portal reachable after join.

**Fail criteria — routes to OD-07 contingency, not to STOP.** Any open
or wrong-password join succeeding, or any interval in which the AP
beacons as open before the password takes effect (record the interval if
measurable).

**Evidence to capture.** `V-05-serial.log`; screenshots/photos of the
client's join attempts and outcomes per cycle; the bench AP password;
scan logs if the client tooling provides them; measured open-window
duration if any was observed.

### V-06 — Ownership persistence after normal reflash (SPIKE-W1 bench + §13 matrix)

**ADR sections validated:** §5.5 (constraint), §10 SPIKE-P4 row (NVS
survival, "WebFlash/ESP Web Tools erase semantics remain to verify") and
SPIKE-W1 row, §13 rows 1–3 (survive matrix), §15 WebFlash row
(erase-semantics documentation input), §16 CT-10 vocabulary.

**Objective.** Prove which reflash paths **preserve** NVS (ownership
record, PSK, WiFi) on real hardware: serial app-reflash without erase,
and the WebFlash/ESP Web Tools non-erase path. This is the "reflash
preserving ownership" half of SPIKE-W1's bench remainder.

**Steps**

*Leg 1 — serial app-reflash, bench spike image (full marker set: PSK from
V-01/V-02, OTA password from V-04, NVS marker from V-03 all present on
unit A).*

1. Reflash unit A over USB with the identical bench spike image using
   the normal no-erase app upload (`esphome upload` / `esptool
   write_flash` of the app image only — record the exact command).
2. Boot. Verify: plaintext API still refused / key still accepted; OTA
   password still enforced; NVS marker still present.

*Leg 2 — WebFlash / ESP Web Tools non-erase path, released artifact
(marker: saved WiFi credentials).*

3. Flash unit B with the current published release via production
   WebFlash **with the erase option unticked / the update path** (record
   the exact UI state and installer dialog wording — this observed
   wording is SPIKE-W1 evidence).
4. Before flashing: provision bench WiFi via captive portal so saved
   credentials exist in NVS. After flashing: observe whether the device
   rejoins bench WiFi without re-provisioning.

**Expected result.** Leg 1: all three markers survive. Leg 2: saved WiFi
credentials survive the non-erase installer path (or the installer
demonstrably offers no non-erase path — itself a recordable SPIKE-W1
answer).

**Pass criteria.** Leg 1: PSK enforced, OTA password enforced, NVS
marker intact after reflash. Leg 2: the installer's non-erase behaviour
is determined unambiguously (credentials survived, or no such path
exists) and recorded verbatim.

**Fail criteria.** Leg 1: any marker lost after a no-erase app reflash
(contradicts §5.5/§13 — direction-relevant, route to owner). Leg 2 has
no fail state for the device — only an undetermined outcome (installer
behaviour could not be established), which blocks SPIKE-W1 closure.

**Evidence to capture.** `V-06-serial.log` (both legs);
`V-06-shell.txt` (exact flash commands); screenshots of every WebFlash
dialog step including erase-option state and wording; post-boot serial
evidence of marker survival/loss.

### V-07 — Ownership removal after erase (SPIKE-W1 bench + §13 matrix)

**ADR sections validated:** §9 OD-10 / AD-04, §12 final row (full flash
erase → FACTORY_UNOWNED), §13 rows 4–5 and factory-reset scope, §10
SPIKE-W1 row, Appendix D E-6.

**Objective.** Prove which paths **destroy** NVS on real hardware: full
`esptool` erase, the WebFlash/ESP Web Tools erase-install path, and the
stock factory reset — returning the device to the unowned-equivalent
state with nothing surviving.

**Steps**

*Leg 1 — esptool full erase, bench spike image (unit A, full marker set
present).*

1. `esptool erase_flash`, then flash the bench spike image.
2. Boot. Verify: plaintext API accepted (PSK gone); OTA accepts the
   empty-password state per the image's pre-harness baseline (record
   exactly what is enforced); NVS marker at default; no saved WiFi.

*Leg 2 — WebFlash erase-install path, released artifact (unit B, saved
WiFi credentials present).*

3. Flash via production WebFlash **with the erase option ticked / the
   full-install path** (record exact UI state and wording).
4. Boot. Verify the device does **not** rejoin bench WiFi (credentials
   destroyed) and starts its setup surface.

*Leg 3 — stock factory reset (unit A, re-establish markers first by
re-running V-01/V-03/V-04 quickly).*

5. Trigger factory reset via the power-cycle-count mechanism (per the
   pinned ESPHome documentation, as configured in the bench image).
6. Boot. Verify all markers gone as in step 2.

**Expected result.** All three erase paths return the device to the
unowned-equivalent state: no PSK, no OTA password, no marker, no saved
WiFi.

**Pass criteria.** After each leg: plaintext API accepted, NVS marker at
default, no automatic WiFi rejoin. Leg 2 additionally: the erase-path
behaviour recorded unambiguously.

**Fail criteria.** Any marker surviving any erase path (an ownership
remnant after "erase" contradicts OD-10/AD-04 semantics — route to
owner); factory reset failing to erase (contradicts E-6/E-7).

**Evidence to capture.** `V-07-serial.log` (all legs);
`V-07-shell.txt`; WebFlash dialog screenshots (erase state + wording);
photo/video of the power-cycle reset sequence; first-boot serial output
after each erase showing the clean state.

### V-08 — Boot behaviour after update (OTA update while owned-equivalent)

**ADR sections validated:** §12 OWNED boot/OTA row ("credentials verified
present"), §13 row 2 (OTA update: credentials and ownership survive),
§16 CT-09 vocabulary, §18 migration paragraph.

**Objective.** Prove an OTA update leaves the owned-equivalent state
fully intact and enforced from the first post-update boot: key still
required, OTA password still required, record still present, no
credential-free window introduced by the update reboot.

**Steps**

1. Unit A in owned-equivalent state (PSK + OTA password + NVS marker).
2. Build a trivially modified bench spike image (e.g. bumped
   `project.version` string only — no surface changes) at the same
   pinned ESPHome version; record both image hashes.
3. OTA-upload it using the correct OTA password.
4. From the moment the device reboots into the new image, run the V-02
   plaintext-refusal probe and the V-04 no-password OTA probe
   immediately and repeatedly during boot (tight loop, per V-09
   method).
5. Verify marker value unchanged; correct key and correct OTA password
   both still work; repeat across one further power cycle.

**Expected result.** New image boots with all credentials enforced from
first acceptance of any connection; marker unchanged.

**Pass criteria.** All of: OTA with correct password succeeded;
post-update plaintext refused; post-update unauthenticated OTA refused;
marker identical; correct credentials accepted.

**Fail criteria.** Any credential or the marker lost or unenforced at
any point after the update, including transiently during the first boot.

**Evidence to capture.** `V-08-serial.log` (spanning the update and both
post-update boots); `V-08-shell.txt` (upload + probes); both image
SHA-256 hashes; probe-loop timing output.

### V-09 — Fail-closed OTA: boot-window measurement (OD-08 decision evidence)

**ADR sections validated:** §9 OD-08 (second sentence — the fail-closed
trigger condition), §10 SPIKE-P2 row ("measure the window if any"), §8
robustness row 4, Appendix D E-5.

**Objective.** Determine, on the pinned build/board, whether **any**
window exists during boot in which the OTA endpoint accepts an
unauthenticated session before the runtime password takes effect — and
measure it if so. This check produces the evidence on which the owner
applies or waives the OD-08 fail-closed contingency; either measured
outcome is a valid spike result.

**Steps**

1. Unit A with the harness applying the bench OTA password at the
   earliest practical `on_boot` priority (record the priority used).
2. On the bench host, run a tight-loop probe that repeatedly initiates
   the OTA handshake **without** a password against the device IP
   (static lease recommended), timestamped, from before power-on until
   ≥ 30 s after boot completes.
3. Power-cycle the device ≥ 20 times with the probe running (cold and
   warm boots; record counts).
4. For every probe attempt, classify: connection refused / TCP accepted
   then auth-rejected / **proceeded past authentication**.
5. If any attempt proceeds past authentication, compute the window:
   time from first TCP acceptance to first auth-enforced rejection, per
   boot, worst case across all boots.

**Expected result.** Either zero attempts proceed past authentication
across all boots (no window), or a bounded window is measured and
recorded. Both are valid results; the second invokes OD-08.

**Pass criteria (as a spike).** The question is answered decisively:
≥ 20 boots probed, every attempt classified, and either no-window shown
or the worst-case window quantified in milliseconds.

**Fail criteria (as a spike).** Inconclusive instrumentation: probe
gaps > 100 ms around the boot moment, unclassifiable attempts, or fewer
than 20 boots — the check must then be re-run, not interpreted.

**Evidence to capture.** `V-09-shell.txt` (probe tool source + full
timestamped output); `V-09-serial.log` time-correlated with the probe
log (record how clocks were aligned); per-boot classification table;
worst-case window value (or explicit "none observed in N boots").

### V-10 — Physical-presence mechanisms (bare board; SPIKE-P6 explicitly NOT closed)

**ADR sections validated:** §9 OD-02 / OD-10 (power-cycle reset as
universal baseline), §12 (deliberate-action guard rows), §13
accidental-reset guard paragraph, §10 SPIKE-P6 row (partial input only),
Appendix D E-6/E-7/E-11.

**Objective.** Prove on the bare S360-100 R4 that the two candidate
physical-presence mechanisms function and are deliberate-action-guarded:
SW3 is firmware-readable as a distinct user action, and the stock
power-cycle-count factory reset triggers on the deliberate pattern but
**never** on a single reboot or power blip. Enclosure accessibility and
PSU-variant power-cycle reliability remain **SPIKE-P6, not covered
here** — no SPIKE-P6 closure may be recorded from this check.

**Steps**

1. With a `binary_sensor` on SW3 (IO0) in the bench image, press SW3
   with the device running; confirm the press/release events in the
   serial log and that normal presses do not reset the device.
2. Hold SW3 through a power-on; confirm the device's boot behaviour is
   recorded (IO0 is the strapping/boot pin — the record must state what
   a boot-time hold does on this board).
3. Single power cycle: confirm NO factory reset occurs (markers intact).
4. Two isolated power blips ≥ 1 minute apart: confirm NO factory reset.
5. Execute the documented power-cycle-count pattern exactly (N cycles
   within the bounded interval, as configured): confirm factory reset
   fires (markers erased — this is V-07 leg 3 when run combined).
6. Repeat step 5 once on unit B (mechanism not unit-specific).

**Expected result.** SW3 events are cleanly detectable; single cycles
and spaced blips never reset; the deliberate pattern reliably resets on
both units.

**Pass criteria.** All of: SW3 press/release visible in logs; zero
resets from steps 3–4; reset fired on the deliberate pattern on both
units; boot-time SW3 behaviour recorded.

**Fail criteria.** Reset triggered by a single cycle or spaced blips
(guard failure — direction-relevant, route to owner); deliberate pattern
failing to reset; SW3 not readable.

**Evidence to capture.** `V-10-serial.log` (all steps, both units);
photos/video of the press and the power-cycle sequences with timing;
the exact configured power-cycle parameters (N, interval); explicit
note in the record that SPIKE-P6 remains open.

---

## 5. Completion

A check is complete only when its result line in the validation record is
recorded PASS or FAIL **by the operator** with the listed evidence
attached. The spike-disposition table in the record maps check outcomes
to SPIKE-P1 / SPIKE-P2 / SPIKE-W1 status; the owner (not this repo, not
an agent) carries any resulting programme-status change to SOT per the
operating model. The attestation section is owner-authored only and this
procedure never pre-fills any part of it.

# ADR-SEC-ESP-PROVISIONING-001 — Secure per-device credential provisioning

## 1. Status and authority

| Field | Value |
|---|---|
| **Status** | **Proposed** — NOT accepted. Final ADR acceptance is an owner-only action per the [SOT operating model](https://github.com/sense360store/SOT/blob/main/CLAUDE-OPERATING-MODEL.md). |
| **Programme ID** | `SEC-ESP-PROVISIONING-001` |
| **Programme authority** | [`sense360store/SOT`](https://github.com/sense360store/SOT) (`roadmap.yaml` → `sec-esp-provisioning-001`, status **planned**) |
| **Implementation repo** | `sense360store/esphome-public` (this repo) |
| **Distribution repo** | [`sense360store/WebFlash`](https://github.com/sense360store/WebFlash) |
| **Drafted / revised** | 2026-07-11 (v1 broad proposal; v2 decision-ready revision same day) |
| **Scope** | Architecture analysis and documentation **only**. No implementation, no runtime code, no credentials, no firmware-behaviour change, no WebFlash change, no SOT change, no release-metadata change. |

**How to approve this document.** The decision path is §2 → §8 → §9 → §10:
verify the starting posture, review the preferred direction and its
robustness matrix, answer the ten decisions in the **Owner decision pack**
(§9), and note the four narrow technical spikes (§10) that remain before
acceptance. Everything else is supporting specification. Appendix A
classifies every owner question from the v1 draft into: decidable now (A),
blocked by technical evidence (B), implementation-time detail (C), or
already constrained by existing policy (D). Feasibility statements in this
revision are backed by primary-source inspection of ESPHome **2026.6.5**
and aioesphomeapi **45.6.0** (evidence quotes and file references:
Appendix D); the repo pins `esphome>=2026.4.5`
([`requirements-dev.txt`](../../requirements-dev.txt)), and pinned-build
confirmation on real hardware is exactly what the remaining spikes cover.

## 2. Verified current posture (starting point — do not reinterpret)

Recorded in
[`docs/security/release-firmware-credential-posture.md`](../security/release-firmware-credential-posture.md)
(authoritative posture statement),
[`docs/rebuild-clean-credentials-001.md`](../rebuild-clean-credentials-001.md)
(programme plan of record), the
[`docs/security/SECURITY-AUDIT-2026-06.md`](../security/SECURITY-AUDIT-2026-06.md)
audit (H1/H2), and the SOT programme entry (verified 2026-07-10 in SOT):

- **Shared published default credentials were removed** from the rebuilt
  releases (`v1.0.7` / `v1.0.8` / `v1.0.9` / `v1.0.1-led-preview`,
  2026-07-06), enforced by the deny-list scanner
  ([`scripts/check_firmware_default_credentials.py`](../../scripts/check_firmware_default_credentials.py)).
- **Released prebuilt firmware ships unprovisioned** — the release lane
  strips the credential surfaces before compile
  ([`scripts/apply_release_secret_posture.py`](../../scripts/apply_release_secret_posture.py)).
- **The native API is unencrypted. OTA is unauthenticated. The web
  interface (`:80`) is unauthenticated. The fallback/setup AP is open**
  (captive portal enabled).
- **Users requiring authentication must self-build** with unique secrets
  ([`secrets.example.yaml`](../../secrets.example.yaml) → private
  `secrets.yaml`).
- **`SEC-ESP-PROVISIONING-001` is planned and not implemented.** No
  first-boot flow, Improv component, or factory-reset component exists in
  any product composition in this tree.
- **R-D4 physical bench attestation** of the current unprovisioned posture
  remains a separate, pending, owner-authored action
  ([`docs/rebuild-clean-credentials-001.md`](../rebuild-clean-credentials-001.md),
  R-D4). This ADR does not perform, claim, or substitute for it.

A build with no credentials is **unprovisioned, not secure** (SOT evidence
rule). Nothing here weakens that.

Current in-tree credential surfaces (self-build path keeps `!secret`
wiring; release builds strip it):
[`packages/base/api_encrypted.yaml`](../../packages/base/api_encrypted.yaml)
(Noise PSK), [`packages/base/ota.yaml`](../../packages/base/ota.yaml)
(OTA password), [`packages/base/logging.yaml`](../../packages/base/logging.yaml)
(web auth), [`packages/base/wifi.yaml`](../../packages/base/wifi.yaml)
(fallback-AP password + captive portal). The setup-network pair
`Sense360_Setup` / `sense360setup` is intentionally public setup-only UX
(documented in the posture doc) and is out of scope here.

## 3. Problem

> **Each physical device must establish device-unique credentials without
> publishing shared secrets, while preserving a workable onboarding,
> recovery, reflashing, and ownership-transfer path.**

A prebuilt `.bin` is immutable and identical for every downloader, so
unique material can only enter a unit at one of five distinct times —
**manufacturing-time** (injected before sale), **build-time** (unique
image per unit), **flash-time** (injected during the flashing session,
outside the binary), **first-boot** (device self-establishes in a
constrained setup state), or **owner-driven post-boot** (an owner tool
claims the device on the network). The architecture must pick a
composition of these that survives onboarding, recovery, reflash,
ownership transfer, RMA, and offline use — designed together, not per-flow
(a flash-time-only design with no recovery story produces lockout; a
first-boot design with no presence proof produces a claim race).

## 4. Goals and non-goals

**Goals** (each maps to a contract test, §16):

1. Unique API encryption material per physical device.
2. Unique OTA authentication material per physical device.
3. Authenticated **or disabled** web interface on owned devices.
4. Protected fallback/setup AP after ownership; open setup surfaces exist
   only in explicitly unowned/bootstrap states.
5. No shared production credential across devices, ever.
6. No credential exposure via public repos, release assets, manifests,
   logs, URLs, browser storage/history, analytics, or support bundles.
7. Compatible with normal Home Assistant onboarding.
8. Recoverable owner experience (defined local recovery for every loss
   scenario, §13).
9. Deterministic factory-reset semantics.
10. Clear device-ownership transfer (new owner gets fresh credentials;
    old owner keeps nothing).
11. Offline-capable provisioning.
12. Testable and auditable behaviour.
13. Production WebFlash delivery without false security claims.

**Non-goals:** a cloud account platform; full PKI (no consumer among
ESPHome's symmetric-key/password surfaces today; re-enter only if a spike
proves need); remote fleet management; automatic secret escrow by Sense360
(permanent owner credentials never cross to Sense360); silent recovery of
lost owner secrets (recovery is the explicit physical mechanism in §13,
never a backdoor); changing unrelated sensor behaviour; Shopify/commercial
workflows; immediate implementation in this PR.

## 5. Constraints

1. **ESP32-S3 / ESPHome.** Provisioning logic beyond stock ESPHome lands
   as an external component under `components/` (existing repo pattern);
   no ESPHome fork.
2. **Verified platform capabilities (2026.6.5; Appendix D).** The native
   API supports shipping **noise-capable with no key** and accepting a
   key at runtime, persisted to NVS, with plaintext disabled thereafter
   and only factory reset removing it. OTA supports an **empty compiled
   password deliberately enabling runtime `set_auth_password()`**. Web
   auth requires non-empty YAML literals (unusable for us — literals would
   be shared); disabling web is fully supported. The fallback-AP password
   has a public runtime setter. These replace the v1 draft's "unknown —
   Spike S1" posture.
3. **Browser Web Serial is Chromium-desktop only** — not iOS Safari, not
   most mobile browsers. Flashing is desktop-bound; claim/recovery must
   not be.
4. **Home Assistant expectations.** HA adopts unencrypted or
   Noise-PSK-encrypted devices; the key is entered at adoption. Official
   ESPHome docs state HA-side *on-the-fly key configuration* is a future
   HA release — today the stock path is manual key entry (Appendix D,
   E-9). Key changes after adoption require updating the HA config entry.
5. **Persistence.** ESPHome preferences, the saved noise PSK, and saved
   WiFi credentials live in NVS: survive OTA and normal serial app
   reflash; destroyed by full flash erase; NVS is readable over USB unless
   flash encryption is enabled (an eFuse-irreversible step — deferred
   decision, Appendix A Q15).
6. **Factory reset.** Stock ESPHome provides a `factory_reset` component
   (button/switch platforms **and** a power-cycle-count trigger) whose
   action erases the entire NVS partition and reboots (Appendix D, E-6/E-7)
   — a deterministic return-to-unowned exists upstream.
7. **Power-loss resilience.** Claim must be atomic-or-retryable; a unit
   power-cycled mid-claim returns to a defined pre-claim state.
8. **No-internet assumption.** The core flow completes on an isolated LAN.
9. **Prebuilt binary immutability.** Artifacts are hash-pinned and
   cosign-signed (checksums); per-device material lives in NVS or is
   generated on-device — never in the image.
10. **No per-device rebuild requirement** (Option B rejected for
    production, §7).
11. **SOT visibility.** The SOT programme entry is internal until the
    advisory publishes; this public ADR carries architecture only.
12. **Support/RMA.** Support guides but cannot unlock; no master key
    class exists. RMA returns to clean unowned state.
13. **Standing invariants untouched**
    ([`docs/standing-invariants.md`](../standing-invariants.md)).

## 6. Threat model

**Assets:** A1 API key (full device control) · A2 OTA credential
(persistent compromise via firmware replacement) · A3 web credential ·
A4 setup/fallback-AP surface (WiFi-credential harvesting) · A5 owner's
home WiFi credentials (in NVS) · A6 bootstrap/claim material · A7
ownership state itself.

**Actors:** legitimate owner/household · LAN-resident or RF-range
attacker · opportunistic first-claimer · physical-access attacker ·
second-hand buyer / RMA recipient · support/Sense360 (trusted for
firmware, **untrusted for owner secrets**) · public observer of
repos/assets/manifests.

**Trust boundaries (explicit):**

1. Public internet/repo/release assets ↔ everything: nothing secret on
   the public side (deny-list gate enforces; provisioning keeps it true).
2. LAN ↔ device: untrusted in OWNED state; conditionally trusted in
   bootstrap states only (time-boxed, physical-presence-anchored).
3. Browser flashing session ↔ device: trusted for the USB session only;
   anything it learns must be transient.
4. Home Assistant ↔ device: trusted after key handover; HA holds A1.
5. Physical possession ↔ device: the root of trust for claim, recovery,
   reset. Without flash encryption, physical USB access also reads NVS —
   stated honestly; see Appendix A Q15.
6. Sense360 ↔ owner secrets: hard boundary; permanent owner credentials
   never cross it.

**Principal threats** (full enumeration T1–T14 with required properties:
Appendix C): credential reuse across devices; secrets in public
binaries/metadata/logs/URLs/browser state; malicious LAN user during the
unowned window; **claim race** (someone claims before the owner — the
decisive threat that stock ESPHome's set-key flow does *not* mitigate,
because any plaintext client may set the key first; closing it is the
custom-gating work at the heart of this design); OTA downgrade to
unprovisioned firmware; factory-reset abuse; stolen/resold devices; weak
randomness; interrupted provisioning; HA key desynchronisation;
recovery-path abuse.

## 7. Options considered

Six options were scored against thirteen criteria (security, operational
complexity, manufacturing complexity, UX, offline, recovery, RMA/support,
WebFlash compatibility, HA compatibility, secret-exposure risk,
scalability, testability, downgrade behaviour). Full scoring: Appendix B.

| Option | Summary | Verdict |
|---|---|---|
| **A — Manufacturing-time injection** | Unique secrets injected per unit before sale (label/QR/order record) | Rejected as primary (permanent secrets in third-party artefacts; heavy process; dies on erase); optional **bootstrap-code delivery channel** inside F, owner decision |
| **B — Per-device build-time firmware** | Unique image per unit | Rejected for production (breaks immutable signed artifacts, hash pinning, declaration-driven matrix; makes Sense360 a credential custodian); **remains the supported self-build path** |
| **C — Flash-time browser-generated credentials** | Browser generates and injects during Web Serial session | Rejected as backbone (desktop-only, §5.3; highest browser exposure; no device-side recovery); optional bootstrap seeding inside F, owner decision |
| **D — First-boot local provisioning** | Device boots unowned, self-establishes via local flow | Strongest foundation but leaves the claim race open → folded into F |
| **E — Home Assistant-driven claim** | HA claims via temporary local bootstrap channel | Preferred *transport* on top of D/F; **stock HA cannot drive it today** (§5.4) — phases in when upstream lands; a non-HA local path is required regardless |
| **F — Hybrid bootstrap model** | Presence-proof-gated claim; device-held unique credentials; one-way transition; physical reset to unowned | **Preferred direction** (§8) |

## 8. Preferred direction (direction, not acceptance)

**Option F — hybrid bootstrap on the first-boot foundation — is retained
and strengthened by the feasibility evidence.** What the v1 draft treated
as its riskiest unknown (runtime credential activation) is the documented,
intended upstream mechanism: ESPHome's own codegen comment describes
shipping with `encryption:` and no key so "a plaintext client [can]
provide a noise key, send it to the device, and then switch to noise. The
key will be saved in flash … and plaintext disabled. Only a factory reset
can remove it" (Appendix D, E-1). The custom work is therefore **not**
credential mechanics — it is the **claim gating**: stock behaviour accepts
a key from *any* plaintext client at *any* time, which is exactly the
claim race (§6). The Sense360 component constrains *when* that stock
mechanism is reachable.

Proposed shape:

1. **Explicit unowned state.** Provisioning-capable releases boot into
   `FACTORY_UNOWNED`, honestly labelled, behaviour-constrained (§12).
2. **Physical-presence-gated claim window.** A physical action (SW3
   boot-button press and/or power-cycle pattern — SPIKE-P6 fixes which)
   opens a time-boxed `BOOTSTRAP_AVAILABLE` window; only inside it does
   the device accept the API set-key exchange / claim flow.
3. **Unique credentials at claim.** API key set via the stock runtime
   set-key mechanism (claimant-generated) or device-generated and
   displayed by the local claim page — OD-05 decides the v1 stance; OTA
   password and AP password are **device-generated** (hardware RNG) at
   claim and applied via the verified runtime setters; web server is
   disabled (OD-06).
4. **One-way transition** to `OWNED`, committed atomically in NVS;
   bootstrap access invalidated before the claim response completes.
5. **Physical-only reversal.** Factory reset (stock `factory_reset`
   semantics: full NVS erase) is the only path back to unowned.
6. **No permanent secrets in public firmware or WebFlash metadata** — by
   construction; the deny-list artifact gate remains as backstop.

### Robustness under each possible spike outcome

The direction was re-challenged against every capability result the
spikes could return. Verified results are marked; Option F does not
depend on any single optimistic outcome:

| Capability result | Architectural consequence | Status |
|---|---|---|
| Dynamic API key supported | Continue: runtime set-key is the claim mechanism | **Verified in source (E-1…E-3); bench confirmation = SPIKE-P1** |
| Dynamic API key requires custom component | Would need owner sign-off on security-critical custom crypto path | Not required — stock mechanism exists; custom code is gating-only (OD-09) |
| Dynamic API key requires upstream ESPHome change | Programme phased behind upstream work | Not the case per source evidence |
| Dynamic OTA password unsupported | Disable network OTA until owned; recovery via serial only | Not the case — runtime setter is deliberate upstream API (E-4/E-5); boot-ordering proof = SPIKE-P2; contingency stands if SPIKE-P2 fails (OD-08) |
| Dynamic web auth unsupported | **Disable web after ownership** | Confirmed unusable for us (auth literals must be non-empty YAML values, E-8) → web disabled is the proposed default (OD-06) |
| Dynamic fallback-AP password unsupported | Disable fallback AP after ownership or reset-only setup mode | Not the case — public runtime setter (E-8); boot-ordering proof folds into SPIKE-P2; contingency stands (OD-07) |
| Stock HA claim unsupported | Explicit local setup flow + manual key entry for v1; HA-driven claim phases in when upstream lands | **Confirmed: stock HA = manual entry today** (E-9); OD-05 asks the owner to accept this for v1 |
| No suitable physical-presence mechanism | Manufacturing bootstrap code, USB claim, or hardware revision required | Unlikely to bind: SW3/SW4 exist on S360-100 R4 and the stock power-cycle-count reset needs no button (E-6/E-10); enclosure accessibility = SPIKE-P6 |

If SPIKE-P1 or SPIKE-P2 fails on real hardware, the fallbacks above keep
Option F viable in reduced form (e.g. OTA disabled until owned). Only a
combined failure of the set-key mechanism *and* all presence mechanisms
would force reconsideration toward Option A bootstrap codes — no current
evidence points there.

## 9. Owner decision pack

Ten decisions. Each is a policy choice the owner can make now; none
requires implementation first. Where a decision consumes spike evidence,
that evidence is already gathered at source level and the residual bench
confirmation is noted. (Category B/C/D questions from the v1 draft are
deliberately *not* in this pack — see Appendix A.)

---

**Decision OD-01 — Offline / local-first requirement**

**Recommendation:** Provisioning must work with no internet and no
Sense360 cloud dependency; internet may enhance but never gate the flow.

**Owner choice:** Accept / Reject / Amend

**Why this matters:** Fixes the architecture class — every option that
phones home is excluded permanently; support and documentation can promise
local-first onboarding.

**Blocked by spike:** No.

---

**Decision OD-02 — Physical presence required for claim and recovery**

**Recommendation:** A physical action on the unit is mandatory both to
open the claim window and to perform recovery/reset. No network-only path
may claim, re-key, or unown a device.

**Owner choice:** Accept / Reject / Amend

**Why this matters:** This is the mitigation for the claim race and for
recovery abuse — the two attacks stock mechanisms do not stop. Rejecting
it means accepting first-come-first-served claiming on the LAN.

**Blocked by spike:** No (the policy). Which physical mechanism ships is
SPIKE-P6 (implementation detail, not policy).

---

**Decision OD-03 — No escrow of permanent owner credentials**

**Recommendation:** Sense360 never stores, receives, or can recover any
permanent owner credential. Lost credentials are recovered only by the
physical re-key/reset path. (If bootstrap codes are ever adopted, they are
single-use and dead after claim; that separate question stays out of v1 —
Appendix A Q1/Q3/Q17.)

**Owner choice:** Accept / Reject / Amend

**Why this matters:** Hard trust boundary; shapes support ("we cannot
unlock your device — by design"), privacy posture, and breach blast
radius. Aligns with the operating model's owner-secret discipline; owner
ratification makes it programme policy of record.

**Blocked by spike:** No.

---

**Decision OD-04 — Home Assistant primary, but not sole, owner surface**

**Recommendation:** HA is the primary owner experience; a generic local
claim/recovery flow (phone-browser reachable, no HA required) must also
exist. Claim and recovery must work from a mobile browser; only *flashing*
is desktop-bound (Web Serial platform fact).

**Owner choice:** Accept / Reject / Amend

**Why this matters:** Determines whether non-HA users are supported and
guarantees a recovery path when HA itself is what was lost. Mobile-capable
claim keeps the ceiling-mounted install workflow realistic.

**Blocked by spike:** No.

---

**Decision OD-05 — Manual API-key entry is acceptable for v1**

**Recommendation:** Accept manual key entry into HA for v1 (the key is
presented once by the local claim flow, or generated by the claimant and
set to the device). Adopt HA-driven automatic key handover when the
documented upstream HA feature ships ("Support for configuring the
encryption key on-the-fly will be implemented in a future release of Home
Assistant" — official ESPHome docs, Appendix D E-9). Do not build a custom
HA integration for v1.

**Owner choice:** Accept / Reject / Amend

**Why this matters:** Removes the only unbounded external dependency from
v1 scope. Rejecting means either building/maintaining a custom HA
integration or blocking the programme on upstream HA timing.

**Blocked by spike:** No (stock-HA behaviour verified from official docs;
nothing further to learn before deciding).

---

**Decision OD-06 — Web server disabled on owned devices**

**Recommendation:** Disable the web interface in provisioning-capable
releases (at minimum in OWNED state; recommended entirely). Runtime web
auth is not viable without baking shared literals (verified, Appendix D
E-8), and an unauthenticated web UI on an owned device violates Goal 3.

**Owner choice:** Accept / Reject / Amend

**Why this matters:** Removes a whole credential class and its lifecycle;
customers lose the local web page (HA remains the interface). The
self-build path keeps web auth via `!secret` regardless.

**Blocked by spike:** No.

---

**Decision OD-07 — Fallback AP protected after ownership**

**Recommendation:** After claim, the fallback AP is protected with a
device-generated password delivered to the owner during claim (recovery
value); contingency if boot-ordering proof fails (SPIKE-P2): disable the
fallback AP on owned devices and make recovery reset-based only.

**Owner choice:** Accept / Reject / Amend

**Why this matters:** The open AP + captive portal is today's
WiFi-credential-harvesting surface (audit H2 class). Protecting it
preserves "fix my WiFi without a ladder"; disabling it is safer but makes
network changes require physical reset.

**Blocked by spike:** Partially — SPIKE-P2 confirms the AP password is
applied before the AP can start; the *policy* (protect vs disable) is
decidable now.

---

**Decision OD-08 — Network OTA posture on owned devices**

**Recommendation:** Keep network OTA enabled with the device-generated
runtime password (upstream-supported mechanism, Appendix D E-4/E-5),
subject to SPIKE-P2 proving the password is enforced before the OTA
endpoint accepts connections. Contingency if that proof fails: network
OTA is disabled until owned (serial-only recovery), which is accepted as
a v1 posture rather than shipping an unauthenticated OTA window.

**Owner choice:** Accept / Reject / Amend

**Why this matters:** OTA is the persistent-compromise surface (audit H1
exploitation path). This decision sets the fail-safe: no capability is
worth an unauthenticated OTA window on an owned device.

**Blocked by spike:** Partially — SPIKE-P2 (boot-ordering enforcement);
the policy and its contingency are decidable now.

---

**Decision OD-09 — Custom security-critical ESPHome component is acceptable**

**Recommendation:** Accept that Sense360 maintains a small external
component in this repo implementing the state machine and claim gating
(window control, presence input, atomic NVS ownership record, bootstrap
invalidation). It gates *when* stock mechanisms are reachable; it does
**not** implement cryptography, key exchange, or transport (those remain
stock ESPHome). Contract tests (§16) pin its behaviour.

**Owner choice:** Accept / Reject / Amend

**Why this matters:** This is a standing maintenance and review burden on
every ESPHome version bump. Rejecting it means stock-only behaviour — and
stock behaviour cannot close the claim race (first plaintext client wins).

**Blocked by spike:** No.

---

**Decision OD-10 — Recovery/reset UX baseline**

**Recommendation:** Factory reset = stock `factory_reset` semantics (full
NVS erase → FACTORY_UNOWNED), triggered by a deliberate physical action
with an accidental-trigger guard; the power-cycle-count mechanism (stock,
works on ceiling-mounted units without touching the board) is the
universal baseline, with the SW3 button variant added if SPIKE-P6 finds it
enclosure-accessible. Recovery (re-key without full reset) uses the same
presence gate as claim. Full flash erase over USB is documented as
equivalent to factory reset.

**Owner choice:** Accept / Reject / Amend

**Why this matters:** Fixes deterministic reset semantics (Goal 9), the
ownership-transfer story (Goal 10), and what support may advise. The
power-cycle baseline means no hardware change and no enclosure dependency.

**Blocked by spike:** Partially — SPIKE-P6 settles the button variant and
the exact guard values (implementation detail); the semantics are
decidable now.

---

## 10. Required technical spikes

The v1 draft listed six spikes (S1–S6). This revision executed the
desk/source phase of all six against ESPHome 2026.6.5, aioesphomeapi
45.6.0, official ESPHome documentation, and the S360-100 R4 hardware
record (results and citations: Appendix D). The evaluation:

| v1 spike | Desk result | Remaining before acceptance? |
|---|---|---|
| SPIKE-P1 runtime API encryption | **Supported today** in stock ESPHome: ship `encryption:` with no key → runtime set-key, NVS-persisted, plaintext then disabled, factory reset clears (E-1…E-3). Requires no custom component, upstream change, or fork for the mechanism itself. | **Yes — narrowed to bench confirmation** on the pinned build/board |
| SPIKE-P2 runtime OTA authentication | **Supported today**: empty compiled `password:` exists expressly so `set_auth_password()` can be called at runtime; rotation is the documented use; enforcement occurs whenever the stored password is non-empty (E-4/E-5). OTA state survives OTA (NVS). | **Yes — narrowed to boot-ordering proof** (credential applied before any network endpoint accepts) — also covers the AP password path |
| SPIKE-P3 web + fallback AP | **Resolved at source level**: runtime web auth not viable without non-empty YAML literals → web disabled (OD-06); AP password has a public runtime setter; captive portal / WiFi provisioning unaffected (E-8). | **No** (AP boot-ordering folds into SPIKE-P2) |
| SPIKE-P4 persistence & reset | **Resolved at source level**: NVS survives OTA and normal serial app reflash; full erase wipes it; stock `factory_reset` erases the entire NVS partition deterministically; single-blob ownership record gives atomic commit; interrupted claim rolls back by never persisting partial state (E-6/E-7). NVS/flash encryption practical-but-irreversible → deferred decision (Appendix A Q15). | **Partially — WebFlash/ESP Web Tools erase semantics** remain to verify (which installer paths erase NVS) → SPIKE-W1 |
| SPIKE-P5 HA claim & key handover | **Resolved from primary docs/source**: protocol + client library support exists (`noise_encryption_set_key`, aioesphomeapi 45.6.0); stock HA cannot yet drive it — manual key entry is the stock path today; Improv (serial/BLE) sets WiFi only; the BLE `esp32_improv` `authorizer` is upstream precedent for button-gated provisioning (E-9/E-10). No custom HA integration required if OD-05 accepted. | **No** (upstream HA feature is a watch item, not a blocker) |
| SPIKE-P6 physical-presence mechanism | **Partially resolved**: S360-100 R4 carries SW3 (boot/IO0) and SW4 (reset/EN) tactile switches per [`docs/hardware/s360-100-r4-core.md`](../hardware/s360-100-r4-core.md); the stock power-cycle-count factory-reset mechanism requires no button access at all. No user-accessible button is *assumed* — enclosure accessibility is unverified. | **Yes — bench item**: confirm mechanism ergonomics/accessibility on assembled hardware |

**Final reduced pre-acceptance spike list (4, down from 6):**

| ID | Question | Type |
|---|---|---|
| **SPIKE-P1** | On the pinned release build/board: empty-key noise flow end-to-end — set key from plaintext client, verify persistence across reboot, verify plaintext refused after key set, verify factory reset clears | Bench (owner-run or owner-observed; results recorded, attestation owner-authored only) |
| **SPIKE-P2** | Boot-ordering enforcement: NVS-loaded OTA and AP passwords are active before the OTA endpoint / fallback AP accept any connection; measure the window if any | Bench + source trace |
| **SPIKE-W1** | WebFlash / ESP Web Tools install paths: which erase NVS (full install vs update), and can/should the installer offer "reflash preserving ownership" | Desk, WebFlash repo (documentation-level; no WebFlash change in this programme phase) |
| **SPIKE-P6** | Physical-presence ergonomics on assembled S360-100 R4: SW3 accessibility in the enclosure; power-cycle-pattern reliability on PoE and 240 V PSUs | Bench |

Dropped as acceptance blockers: entropy verification (ESP32-S3 TRNG with
RF active is the documented platform RNG; the generation recipe is pinned
by contract test CT-15 at implementation time); flash/NVS encryption
(deferred decision, Appendix A Q15); HA auto-claim (upstream watch item).

## 11. Credential lifecycle

Per-class summary (full phase-by-phase table unchanged in substance from
v1; the mechanisms are now the verified ones):

| Credential | Origin | Storage | Invalidated by | Notes |
|---|---|---|---|---|
| **API key (Noise PSK)** | Set at claim via stock runtime set-key (claimant-generated) or device-generated + displayed by claim flow — OD-05 | Device NVS (stock `SavedNoisePsk` preference) + HA config entry | Factory reset; authenticated re-key (rotation) | Stock semantics: once set, plaintext disabled; only factory reset removes |
| **OTA password** | Device-generated at claim (hardware RNG) | Device NVS + owner records | Factory reset; rotation via authenticated session | Applied at boot via runtime setter; enforcement-before-network = SPIKE-P2; contingency OD-08 |
| **Web credential** | **None — web disabled** (OD-06) | — | — | Self-build path keeps `!secret` web auth |
| **Fallback-AP password** | Device-generated at claim | Device NVS | Factory reset | Delivered to owner at claim as the recovery value; contingency OD-07 |
| **Bootstrap material** | Physical action (baseline); optional code channels not in v1 | RAM window state only | Single use; window timeout; claim commit | Never persisted, never a permanent credential |

Lifecycle rules: generation on-device from the hardware RNG (recipe pinned
by CT-15); ≥128-bit effective entropy; nothing derived from MAC, serial,
or time. Rotation is owner-initiated from an authenticated session only.
OTA updates and normal serial reflash preserve all of the above (NVS);
full erase and factory reset destroy all of it. Ownership transfer = reset
then re-claim (credentials are destroyed, never handed over). Support/RMA
never receives or recovers credentials. Decommissioning = factory reset
(wipes stored WiFi too). Loss scenarios: HA config lost → re-enter key or
physical re-key; all owner credentials lost → physical recovery generates
new ones — values are never *revealed*, only replaced.

## 12. State machine

States: `FACTORY_UNOWNED` · `BOOTSTRAP_AVAILABLE` · `CLAIM_IN_PROGRESS` ·
`OWNED` · `RECOVERY` · `FACTORY_RESET_PENDING`.

| From | Event | To | Guard |
|---|---|---|---|
| *(fresh flash / post-erase boot)* | boot, no ownership record | FACTORY_UNOWNED | — |
| FACTORY_UNOWNED | physical presence proof | BOOTSTRAP_AVAILABLE | window timer starts |
| BOOTSTRAP_AVAILABLE | window timeout / reboot | FACTORY_UNOWNED | nothing persisted |
| BOOTSTRAP_AVAILABLE | claimant opens claim channel | CLAIM_IN_PROGRESS | single claimant; others rejected |
| CLAIM_IN_PROGRESS | credentials established, delivered, acknowledged | OWNED | atomic single-blob NVS commit; bootstrap invalidated before ack |
| CLAIM_IN_PROGRESS | timeout / power loss / abandon | FACTORY_UNOWNED | partial material discarded |
| OWNED | boot / OTA / capable reflash | OWNED | credentials verified present |
| OWNED | physical recovery action | RECOVERY | presence required |
| RECOVERY | timeout / cancel | OWNED | unchanged |
| RECOVERY | owner completes re-key | OWNED | new credentials committed atomically; old invalidated |
| OWNED | reset action armed | FACTORY_RESET_PENDING | deliberate-action guard |
| FACTORY_RESET_PENDING | confirmation window expires | OWNED | unchanged |
| FACTORY_RESET_PENDING | reset confirmed | FACTORY_UNOWNED | full NVS erase (stock semantics) before reboot |
| *(any)* | full flash erase (USB) | FACTORY_UNOWNED | physical access by definition |

Per-state rules: in `FACTORY_UNOWNED` the device claims no security,
exposes setup surfaces only (API set-key **not** reachable — that is the
gating component), and constrains actuators where feasible (Appendix A
Q18); in `OWNED` every surface is authenticated or disabled; a boot with a
corrupt credential record fails **closed** into a recovery-safe halt,
never silently open (contract test). Exact timeout/hold values are
implementation-time details (Appendix A, Category C).

## 13. Recovery and reset policy

| Action | Credentials survive? | Ownership survives? |
|---|---|---|
| Reboot / power cycle | Yes | Yes |
| OTA update | Yes | Yes |
| Normal serial reflash (no erase), provisioning-capable image | Yes | Yes |
| Normal serial reflash, older non-capable image | Record persists in NVS but is not honoured (device behaves unprovisioned); restored by flashing a capable image | Latent |
| Full flash erase | No | No → FACTORY_UNOWNED |
| Factory reset (in-band physical action) | No | No → FACTORY_UNOWNED |

Ownership transfer: reset (departing owner, or new owner with physical
access) then fresh claim. Recovery after HA loss: re-enter retained key,
else physical re-key (RECOVERY state) — new credentials generated, old
invalidated, nothing revealed. Return to unowned: physical paths only.
Accidental-reset guard: deliberate gesture + confirmation window
(`FACTORY_RESET_PENDING`); a bare reboot or power blip never resets —
note the stock power-cycle-count trigger requires N deliberate cycles
within a bounded interval, which is the guard. Support advises reset only
after confirming possession, observable device state, and that re-key
recovery does not apply; support has no override capability by design.

## 14. Downgrade and release policy

1. **Owned device + older unprovisioned image over serial:** legitimate
   (physical access); behaviour per §13 row 4.
2. **OTA downgrade to a non-capable image while OWNED: refused** by a
   version/capability floor (mechanism scoped at implementation;
   Appendix A Q16). OTA is authenticated in OWNED, so this defends
   against a compromised-but-not-owner client, not the owner.
3. **A release without provisioning support never claims it.** Claims are
   per-release facts.
4. **WebFlash stable vs preview:** capability lands preview-first (§17);
   WebFlash presents capability from declared upstream metadata only.
5. **Self-builds:** unaffected; static-`!secret` builds remain supported
   and documented as distinct.

**Release gates** (extending the existing deny-list pattern):
**G-P1** — release metadata may declare `provisioning: true` only when the
contract tests (§16) ran against that artifact lineage in CI; fails
closed. **G-P2** — the existing deny-list artifact scan, extended with any
new placeholder/bootstrap literals. **G-P3** — WebFlash imports the
capability flag only from signed upstream release metadata (defined in the
WebFlash repo when that separate PR happens). **G-P4** — no
**stable**-channel release carries `provisioning: true` before the
multi-device physical bench pass; preview may, with compile/emulation
evidence, labelled per the no-false-proof invariant.

## 15. Cross-repository responsibilities

| Repo | Owns |
|---|---|
| **esphome-public** | This ADR; the gating component, state machine, persistence record; unit/contract/integration tests; release gates G-P1/G-P2/G-P4 and their pinned tests; release evidence; bench-evidence records (owner-attested only) |
| **WebFlash** | Installer/manifest truthfulness (capability flags from upstream metadata only); erase-semantics documentation (SPIKE-W1); **no credential logging or analytics**; safe transient handling if any browser-side role is ever adopted (not in v1); distribution gate G-P3 |
| **SOT** | Programme status (**planned** today — unchanged by this PR); the accepted-decision record when the owner accepts; open gates; owner decisions of record; cross-repo evidence links |

Sequencing (operating model): architecture (this PR) → spikes → failing
contract tests → firmware implementation → WebFlash (if any) → SOT status
reconciliation — each in its owning repo, each a separate PR.

## 16. Test strategy

Failing contract tests land **before** implementation. Vocabulary = §12
state names. No implementation tests are added in this ADR PR (no ADR
schema/test convention exists in-tree).

Contract tests CT-01…CT-15 (unchanged in substance from v1):
uniqueness across devices (CT-01); API encryption required after claim
(CT-02); OTA auth required after claim (CT-03); web authenticated-or-
absent (CT-04); fallback AP protected-or-unavailable after ownership
(CT-05); bootstrap single-use (CT-06); interrupted claim persists nothing
(CT-07); no secret in tracked files, build logs, manifests, metadata,
URLs, or browser persistence (CT-08); OTA preserves ownership (CT-09);
reflash matrix per §13 (CT-10); factory reset requires the defined
physical action, no network path (CT-11); transfer invalidates prior owner
(CT-12); downgrade policy per §14 (CT-13); recovery completes with
physical presence and existing hardware only (CT-14); generated-credential
entropy/format recipe (CT-15).

Tier mapping — **unit** (host, stdlib `unittest`, mirroring the existing
`scripts/ ↔ tests/` pattern): state machine, NVS record codec, gate
scripts; **contract**: CT-01…15 against a host-simulated core, the merge
gate for implementation PRs; **integration**: compiled firmware — HA
adoption with the set key, OTA flows, desync recovery; **browser**
(WebFlash repo, only if a browser role is ever adopted): no-persistence /
no-analytics assertions; **two-device uniqueness**: CT-01 on ≥2 physical
units within the bench plan; **physical bench** (owner-attested, never
machine-written): claim UX, reset gesture, RF surfaces, SPIKE-P1/P2/P6
confirmations; **release gates**: G-P1…G-P4 with pinned tests.

## 17. Rollout

1. Owner resolves the decision pack (§9); ADR accepted (SOT records it).
2. Spikes SPIKE-P1, SPIKE-P2, SPIKE-W1, SPIKE-P6 (§10); ADR amended if
   any result contradicts the direction (back to owner if so).
3. Failing contract tests CT-01…15 land (red).
4. Firmware implementation to green, staged: state machine → generation →
   claim → recovery/reset.
5. WebFlash documentation/gate work if required (separate repo/PR).
6. Multi-device bench verification (owner-attested).
7. Preview release with `provisioning: true` under G-P1/G-P2 labelling.
8. Stable release after bench evidence (G-P4) and preview soak.
9. Advisory/update messaging (owner publishes); migration guidance (§18).
10. SOT reconciliation at each material change (planned → active →
    implemented → verified), evidence-linked, separate PRs.

**Rollback criteria:** contract-test regression, any CT-08-class exposure
in a shipped artifact, unrecoverable-lockout reports from preview, or
bench failure of reset/recovery gestures → halt promotions, pull the
capability flag from channel metadata (append-only supersede, never mutate
binaries), publish honest notes, return to stage 4.

## 18. Migration impact and acceptance criteria

**Migration:** current unprovisioned rebuilt devices (v1.0.7/8/9,
v1.0.1-led-preview) are unchanged until reflashed with a capable release,
then claimable; self-builders keep the `!secret` path untouched; users on
old shared-credential releases remain covered by the (pending) advisory —
provisioning does not retroactively protect un-reflashed units and no
claim may imply it does; devices already adopted unencrypted in HA that
are later claimed switch to an encrypted API — the HA config entry must be
updated (documented; desync covered by integration tests); replacement/RMA
units ship unowned; preview users get the capability first.

**This ADR moves from Proposed to Accepted only when:** every OD in §9 is
resolved and recorded; SPIKE-P1/P2/W1/P6 are complete and consistent with
the direction; the security review of the concrete design (threat model
§6/Appendix C revisited) is complete; recovery (§13) and downgrade (§14)
semantics are final and contract-covered; the test plan (§16) is agreed;
WebFlash responsibilities (§15) are agreed; no false security claim exists
anywhere in the proposal or metadata plan; and SOT records the acceptance
— the SOT update *is* the acceptance. Implementation must not begin before
that (operating-model rule).

---

## 19. Appendices

### Appendix A — Classification of all v1 owner questions

The v1 draft posed 19 owner questions (Q1–Q19). Classification: **A** =
owner-decidable now (policy; no implementation evidence needed) — these
feed the §9 pack; **B** = blocked by technical evidence (named spike);
**C** = implementation-time detail (removed from ADR-acceptance blockers);
**D** = already constrained by existing policy or platform fact (not put
to the owner as an open choice).

| v1 Q | Question | Cat. | Disposition |
|---|---|---|---|
| Q1 | Manufacturing-time secret injection acceptable? | A | Not needed for v1 baseline (presence proof requires no injection). Policy stance folded into OD-03's no-escrow boundary; revisit only if SPIKE-P6 fails on all mechanisms. No pack slot. |
| Q2 | Zero-internet provisioning mandatory? | A | **OD-01.** |
| Q3 | Printed/QR bootstrap acceptable? | A | Deferred out of v1 (same rationale as Q1); not an acceptance blocker; no pack slot. |
| Q4 | Permanent credentials device-generated? | A | Evidence-informed nuance: the stock API set-key flow is **claimant**-generated; OTA/AP values are device-generated. **OD-05** carries the API-key stance; device-generation for OTA/AP is design baseline (§11). |
| Q5 | Web authenticated or disabled? | A | **OD-06** (evidence: runtime web auth unusable without shared literals). |
| Q6 | OTA password vs another mechanism? | D | Platform-constrained: the stock `esphome` OTA platform offers challenge-based password auth only; runtime rotation is supported (E-4). Stock password for v1; stronger schemes = future programme. |
| Q7 | What survives normal reflash? | D | Platform fact: NVS survives app reflash and OTA; full erase wipes. Policy simply adopts the platform semantics (§13); no owner choice remains. |
| Q8 | What exactly constitutes factory reset? | C | Semantics fixed by **OD-10** (full NVS erase, physical, guarded); the exact gesture/hold/counts are implementation details after SPIKE-P6. |
| Q9 | Physical presence mandatory for claim and recovery? | A | **OD-02.** |
| Q10 | How should RMA/support work? | D | Already governed by no-escrow + owner-only attestation rules (operating model) and OD-03/OD-10; support runbooks are implementation-stage documents. |
| Q11 | Browser-based secret display / flash-time seeding acceptable? | A | Not in v1 (Option C rejected as backbone; no browser role adopted). If a browser role is ever proposed, it returns as its own owner decision with WebFlash scope. No pack slot. |
| Q12 | Is HA the only supported owner? | A | **OD-04.** |
| Q13 | Acceptable mobile UX given Web Serial limits? | A/D | Web Serial desktop-only is a platform fact (D); the policy half (claim/recovery must be phone-browser-capable) is folded into **OD-04**. |
| Q14 | Bootstrap window always-open vs triggered? | C | Principle settled by OD-02 (presence-triggered, time-boxed); exact windowing = implementation. |
| Q15 | Flash/NVS encryption in scope? | B | Blocked by a dedicated evidence item (eFuse irreversibility, OTA/erase interplay, support cost). **Deferred decision — explicitly NOT an acceptance blocker**; until decided, all posture claims carry the physical-USB-reads-NVS caveat (§6 boundary 5). |
| Q16 | OTA downgrade refusal while OWNED required for MVP? | B | Policy recommended yes (§14.2); the *mechanism* needs implementation-time evidence (no stock version floor in the OTA protocol). Scoped with the implementation PR; contract test CT-13 pins the behaviour. |
| Q17 | Retention of bootstrap code↔unit records? | C | Conditional on Q1/Q3 adoption, which is out of v1. If ever adopted: none-post-claim is the standing recommendation. |
| Q18 | Constrain actuators while unowned? | A | Policy yes-where-feasible (design baseline, §12); per-board feasibility is implementation detail. Not a pack slot — no meaningful owner alternative exists (leaving actuators open while unowned contradicts Goal 4's spirit). |
| Q19 | API/web/OTA availability while FACTORY_UNOWNED? | A | Superseded by the concrete design: the gating component keeps the API set-key unreachable outside the claim window (§8.2), web is disabled (OD-06), OTA posture is OD-08. No separate pack slot. |

Count: **A = 11** (Q1–Q5, Q9, Q11–Q13, Q18, Q19), **B = 2** (Q15, Q16),
**C = 3** (Q8, Q14, Q17), **D = 3** (Q6, Q7, Q10). The 19 open questions
reduce to **10 packaged decisions** (§9) plus 2 explicitly deferred
evidence-blocked items and implementation-stage detail.

### Appendix B — Option scoring detail

Criteria: security / operational complexity / manufacturing complexity /
UX / offline / recovery / RMA-support / WebFlash compatibility / HA
compatibility / secret-exposure risk / scalability / testability /
downgrade behaviour.

**A — Manufacturing-time injection.** Strong uniqueness; secrets predate
network exposure. But permanent credentials exist outside owner control
(label/order record = long-lived exposure surface; a photographed card is
full compromise until reset); heaviest ongoing per-unit process (secure
injection + label↔unit integrity in assembly); full flash erase orphans
the label (dead artefact, support trap); hostile to WebFlash reflash;
hard to CI-test end-to-end. Not rejected for complexity — rejected because
even executed perfectly it leaves permanent credentials in third-party
artefacts. Viable only as an optional single-use *bootstrap-code* channel.

**B — Per-device builds.** Unique by construction, but the pipeline
becomes custodian of every customer's credentials (violates the no-escrow
boundary); destroys the one-artifact-per-config contract (immutable tagged
assets, `expected_sha256` pinning, cosign signing, ESP-007
declaration-driven matrix); requires an online build service (fails
offline goal); version management per unit. Retained solely as the
existing self-build path under the user's own control.

**C — Flash-time browser generation.** Unique per flash; born in-session.
Concentrates the highest browser-side exposure (memory, extensions,
clipboard, screenshots — the CT-08 class); excludes iOS/mobile entirely
(Web Serial); no device-side recovery (lost key ⇒ desktop reflash
dependency); moves security-critical code into WebFlash, raising that
repo's assurance burden. Structural objections, not complexity ones.
Possible future bootstrap-seeding accelerator only.

**D — First-boot local provisioning.** Firmware-only; fully offline;
binary stays immutable; natural reset-to-unowned recovery; host-testable.
Sole weakness: the unauthenticated setup window — whoever reaches the
setup surface first becomes owner (the claim race). Exactly what F's
presence gate fixes.

**E — HA-driven claim.** Best possible UX; key lands directly in HA
config (shrinks human-copy exposure). Verified limitation: stock HA
cannot yet drive the set-key flow (E-9) — the transport exists in
aioesphomeapi but the config-flow feature is documented as future. Also
requires a non-HA path regardless (recovery; non-HA owners). Layered
transport, not a standalone architecture.

**F — Hybrid bootstrap.** Composite of D's mechanics + presence gating +
one-way ownership + physical-only reversal. Scores strongest on every
security criterion; its only structural costs are the small gating
component (OD-09) and one added physical action in onboarding UX.
Downgrade behaviour identical to D (NVS record latent under non-capable
images, §13). Preferred.

### Appendix C — Extended threat enumeration

| # | Threat | Required property (test) |
|---|---|---|
| T1 | Credential reuse across devices | Per-unit generation; no shared value possible by construction (CT-01) |
| T2 | Credentials embedded in public binaries | No baked secret; deny-list gate G-P2 (CT-08) |
| T3 | Credentials in WebFlash metadata/JS | No browser role in v1; manifests carry capability flags only, never material (CT-08, G-P3) |
| T4 | Secrets in URLs, logs, browser storage, clipboard, screenshots, analytics | No secret in any URL/log at any level; one-time explicit display only where OD-05 path requires it (CT-08) |
| T5 | Malicious LAN user during unowned window | Constrained FACTORY_UNOWNED (actuators limited, set-key unreachable outside window); time-boxed bootstrap; presence gate (CT-06/CT-11 preconditions) |
| T6 | Claim race — attacker claims first | **The decisive threat.** Stock set-key accepts any plaintext client; the gating component makes claim impossible—not just unlikely—without the physical action (OD-02, CT-06) |
| T7 | Downgrade/reflash to unprovisioned firmware | OTA downgrade refused while OWNED (CT-13); serial reflash = physical access = legitimate (§13) |
| T8 | Factory-reset abuse | Reset requires the deliberate guarded physical action; result is a blank device, never the owner's secrets (CT-11) |
| T9 | Stolen or resold device | As T8: reset wipes A1–A6; nothing recoverable post-reset (subject to the flash-encryption caveat, Q15) (CT-12) |
| T10 | Support/RMA access abuse | No support credential, master key, or serial-derived secret exists (CT-14) |
| T11 | Weak randomness | Hardware RNG only; recipe pinned (CT-15); nothing MAC/serial/time-derived |
| T12 | Interrupted provisioning | Atomic single-blob commit; partials never persisted (CT-07) |
| T13 | HA key desynchronisation | Rotation/reset fails visibly and recoverably (re-adopt path); integration-tested |
| T14 | Rollback/recovery abuse | Recovery needs the same presence gate as claim; always replaces, never reveals (CT-14) |

### Appendix D — Feasibility evidence (primary sources)

Inspected: **ESPHome 2026.6.5** (installed package source; repo pins
`esphome>=2026.4.5`), **aioesphomeapi 45.6.0**, official ESPHome
documentation (esphome.io), and this repo's hardware records. Paths are
relative to the ESPHome package root. Pinned-build/on-device confirmation
is SPIKE-P1/P2.

- **E-1 — API: ship noise-capable with no key; client sets it; flash-
  persisted; plaintext then disabled; factory reset clears.**
  `components/api/__init__.py` codegen: an `encryption:` block without a
  key adds `USE_API_NOISE` + `USE_API_PLAINTEXT` with the comment: *"No
  key provided, but encryption desired. This will allow a plaintext client
  to provide a noise key, send it to the device, and then switch to noise.
  The key will be saved in flash and used for future connections and
  plaintext disabled. Only a factory reset can remove it."* A YAML-set key
  instead defines `USE_API_NOISE_PSK_FROM_YAML`, under which runtime
  changes are rejected (self-build static path unaffected).
- **E-2 — Runtime set/clear/persist/activate.**
  `components/api/api_server.cpp`: `APIServer::save_noise_psk(psk,
  make_active)` and `clear_noise_psk()` persist via a `SavedNoisePsk`
  preference with an immediate `global_preferences->sync()`, then reload
  and apply the PSK and disconnect all clients; the saved PSK is loaded
  and applied in `setup()`.
- **E-3 — Protocol message.** `components/api/api_connection.cpp`:
  `NoiseEncryptionSetKeyRequest` handler decodes a base64 32-byte PSK,
  saves-and-activates; `key_len == 0` clears (reachable only over an
  established session — post-claim that means an encrypted, authenticated
  one).
- **E-4 — OTA runtime password is a deliberate upstream API.**
  `components/esphome/ota/__init__.py`: *"Compile the auth path whenever
  `password:` is present in YAML, even if empty. An empty password opts in
  to the auth code path so `set_auth_password()` can be called at runtime
  (e.g. to rotate the password from a lambda)."*
- **E-5 — OTA enforcement condition.**
  `components/esphome/ota/ota_esphome.cpp`: the auth phase runs whenever
  the stored password is non-empty — hence the SPIKE-P2 boot-ordering
  proof (value must be applied before the endpoint accepts connections),
  and the OD-08 contingency if that proof fails.
- **E-6 — Deterministic full wipe.** `components/esp32/preferences.cpp`:
  `ESP32Preferences::reset()` calls `nvs_flash_erase()` — the entire
  default NVS partition (saved PSK, saved WiFi credentials, all
  preferences), invalidating the handle until restart.
- **E-7 — Stock factory-reset component with a buttonless physical
  trigger.** `components/factory_reset/`: button and switch platforms plus
  a power-cycle counter (N power-on resets within a bounded interval →
  `global_preferences->reset()` + safe reboot; counter self-clears after
  the interval). Physical-presence-anchored reset with no enclosure
  dependency.
- **E-8 — Web auth vs AP password.** `components/web_server/__init__.py`:
  the `auth:` schema requires non-empty (`Length(min=1)`) YAML strings and
  only then compiles `USE_WEBSERVER_AUTH` — runtime population without
  baked literals is not available, so OD-06 proposes disabling web.
  `components/wifi/wifi_component.h`: `void set_ap(const WiFiAP &ap)` is
  public — the fallback-AP password is runtime-settable before the AP
  starts; captive portal and WiFi provisioning are unaffected.
- **E-9 — Home Assistant / client library.** aioesphomeapi 45.6.0
  `client.py` exposes `noise_encryption_set_key()`. Official ESPHome API
  documentation (esphome.io, fetched 2026-07-11): the encryption key *"If
  not provided … may be set at runtime, but encryption will not be used
  until it is set"*, and *"Support for configuring the encryption key
  on-the-fly will be implemented in a future release of Home Assistant"*
  — stock HA today = manual key entry; the ESPHome Device Builder
  (dashboard) is the existing consumer of the set-key flow.
- **E-10 — Improv and presence precedent.** `components/improv_serial/`
  and `components/esp32_improv/` exist upstream and provision **WiFi
  only** (consistent with the audit's H1 note); `esp32_improv` supports a
  required `authorizer` (e.g. a physical button) gating BLE provisioning —
  upstream precedent for presence-gated setup.
- **E-11 — Sense360 hardware presence mechanisms.**
  [`docs/hardware/s360-100-r4-core.md`](../hardware/s360-100-r4-core.md):
  SW3 = Boot/IO0 tactile switch, SW4 = Reset (EN) tactile switch on
  S360-100 R4; enclosure accessibility unverified (no bench claim) —
  SPIKE-P6. USB (UART0) presence is desktop-bound. The E-7 power-cycle
  mechanism needs no board access.

### Appendix E — References

- [`docs/security/release-firmware-credential-posture.md`](../security/release-firmware-credential-posture.md) — authoritative shipped-posture statement
- [`docs/security/SECURITY-AUDIT-2026-06.md`](../security/SECURITY-AUDIT-2026-06.md) — audit findings H1/H2
- [`docs/rebuild-clean-credentials-001.md`](../rebuild-clean-credentials-001.md) — rebuild programme plan of record; R-D4 (pending, owner-authored only)
- [`docs/sense360-roadmap-status.md`](../sense360-roadmap-status.md) — canonical repo status doc
- [`docs/standing-invariants.md`](../standing-invariants.md) — standing gates (unchanged)
- [`docs/system-architecture.md`](../system-architecture.md) — two-repo pipeline / cross-repo contract
- [SOT `CLAUDE-OPERATING-MODEL.md`](https://github.com/sense360store/SOT/blob/main/CLAUDE-OPERATING-MODEL.md) — authority model, ADR rules, evidence rules
- SOT `roadmap.yaml` → `sec-esp-provisioning-001` — programme entry (**planned**)
- [`packages/base/api_encrypted.yaml`](../../packages/base/api_encrypted.yaml) · [`packages/base/ota.yaml`](../../packages/base/ota.yaml) · [`packages/base/logging.yaml`](../../packages/base/logging.yaml) · [`packages/base/wifi.yaml`](../../packages/base/wifi.yaml) — current credential surfaces
- [`scripts/apply_release_secret_posture.py`](../../scripts/apply_release_secret_posture.py) · [`scripts/check_firmware_default_credentials.py`](../../scripts/check_firmware_default_credentials.py) — posture strip + deny-list gate
- [`config/webflash-builds.json`](../../config/webflash-builds.json) — declaration-driven release matrix (ESP-007)
- [`secrets.example.yaml`](../../secrets.example.yaml) — self-build template
- [`docs/hardware/s360-100-r4-core.md`](../hardware/s360-100-r4-core.md) — S360-100 R4 hardware record (SW3/SW4)

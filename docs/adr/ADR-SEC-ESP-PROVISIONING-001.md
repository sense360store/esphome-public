# ADR-SEC-ESP-PROVISIONING-001 — Secure per-device credential provisioning

| Field | Value |
|---|---|
| **Status** | **Proposed** — NOT accepted. Final ADR acceptance is an owner-only action per the [SOT operating model](https://github.com/sense360store/SOT/blob/main/CLAUDE-OPERATING-MODEL.md). |
| **Programme ID** | `SEC-ESP-PROVISIONING-001` |
| **Programme authority** | [`sense360store/SOT`](https://github.com/sense360store/SOT) (`roadmap.yaml`, entry `sec-esp-provisioning-001`, status **planned**) |
| **Implementation repo** | `sense360store/esphome-public` (this repo) |
| **Distribution repo** | [`sense360store/WebFlash`](https://github.com/sense360store/WebFlash) |
| **Date drafted** | 2026-07-11 |
| **Scope of this document** | Architecture and test planning **only**. No implementation, no runtime code, no credentials, no firmware-behaviour change, no WebFlash change, no SOT change, no release-metadata change. |

This ADR proposes an architecture for establishing **device-unique
credentials** on Sense360 devices that are flashed with prebuilt release
firmware, without publishing shared secrets. It follows the ADR section
requirements of the SOT operating model (context, problem, goals,
non-goals, constraints, options, decision, rejected alternatives, security
and operational implications, recovery, migration, testing, rollout, open
questions).

---

## 0. Verified current posture (starting point — do not reinterpret)

This ADR starts from the verified current state recorded in
[`docs/security/release-firmware-credential-posture.md`](../security/release-firmware-credential-posture.md)
(the authoritative posture statement),
[`docs/rebuild-clean-credentials-001.md`](../rebuild-clean-credentials-001.md)
(programme plan of record and execution log), the
[`docs/security/SECURITY-AUDIT-2026-06.md`](../security/SECURITY-AUDIT-2026-06.md)
audit (findings H1/H2), and the SOT programme entry
(`roadmap.yaml` → `sec-esp-provisioning-001`, verified 2026-07-10 in SOT):

- **Shared published default credentials were removed** from the rebuilt
  releases (`v1.0.7` / `v1.0.8` / `v1.0.9` / `v1.0.1-led-preview`,
  2026-07-06), enforced by the deny-list scanner gate
  ([`scripts/check_firmware_default_credentials.py`](../../scripts/check_firmware_default_credentials.py))
  on every produced binary.
- **Released prebuilt firmware ships unprovisioned.** The release lane
  strips the credential surfaces before compile
  ([`scripts/apply_release_secret_posture.py`](../../scripts/apply_release_secret_posture.py));
  no credentials are generated or embedded.
- **The native API is unencrypted** (no key configured; Home Assistant
  adopts the device and shows it as unencrypted).
- **OTA is unauthenticated.**
- **The web interface (`:80`) is unauthenticated.**
- **The fallback/setup AP is open** (no password), with the captive portal
  enabled.
- **Users requiring authentication must currently self-build** with unique
  secrets ([`secrets.example.yaml`](../../secrets.example.yaml) → private
  `secrets.yaml`); the committed packages keep their `!secret` references
  so the self-build path produces fully secured firmware.
- **`SEC-ESP-PROVISIONING-001` is planned and not implemented.** No
  first-boot or provisioning flow exists in this tree; there is no Improv
  component, no first-boot credential generator, and no factory-reset
  component in any product composition.
- **R-D4 physical bench attestation** of the current *unprovisioned*
  posture remains a separate, pending, owner-authored action
  ([`docs/rebuild-clean-credentials-001.md`](../rebuild-clean-credentials-001.md),
  decision R-D4). This ADR does not perform, claim, or substitute for it.

A build with no credentials is **unprovisioned, not secure** (SOT evidence
rule). Nothing in this ADR weakens that statement; the whole point of the
programme is to replace "unprovisioned" with "provisioned uniquely per
device" — with evidence — before any security claim is made.

### Current in-tree credential surfaces (behaviour evidence)

| Surface | Committed source (self-build path) | Release-binary posture today |
|---|---|---|
| Native API (tcp/6053) | [`packages/base/api_encrypted.yaml`](../../packages/base/api_encrypted.yaml) — Noise PSK via `!secret api_encryption_key` | Encryption block stripped; API unencrypted |
| OTA (`esphome` platform) | [`packages/base/ota.yaml`](../../packages/base/ota.yaml) — `password: !secret ota_password` | Password stripped; OTA unauthenticated |
| Web UI (`:80`) | [`packages/base/logging.yaml`](../../packages/base/logging.yaml) — `web_server.auth` via `!secret web_username` / `web_password` | Auth block stripped; web unauthenticated |
| Fallback/setup AP + captive portal | [`packages/base/wifi.yaml`](../../packages/base/wifi.yaml) — `ap.password: !secret fallback_ap_password`, `captive_portal:` | Password stripped; open AP |
| Setup-network join | `wifi_ssid` / `wifi_password` secrets = `Sense360_Setup` / `sense360setup` — **intentionally public setup-only UX**, documented in the posture doc | Unchanged (deliberate; the only deny-list exclusions) |

---

## 1. Context

### 1.1 Why shared defaults were unsafe

Audit finding **H1**
([`SECURITY-AUDIT-2026-06.md`](../security/SECURITY-AUDIT-2026-06.md))
showed the release pipeline compiled a fixed, world-readable credential
set into every published binary: a placeholder API encryption key, one
shared OTA password, one shared web login, and one shared fallback-AP
password. One public-repo read yielded control of **every** device still
on defaults — including OTA overwrite (persistent compromise) and, in
fan-driver configurations, mains-adjacent switching. Finding **H2** added
that historical fallback-AP literals are burned into public git history
forever. Shared credentials convert a single disclosure into a fleet-wide
compromise; that class must never return.

### 1.2 Why "no credentials" is unprovisioned, not provisioned

The remediation (`SEC-ESP-BUILD-GATES-001`, then
`REBUILD-CLEAN-CREDENTIALS-001`) removed the false assurance, it did not
add protection: a freshly flashed device is open on every control surface
to anyone on the LAN or in RF range. That is an honest posture — the
firmware no longer claims security it does not have — but it is a
temporary one. The SOT evidence rules are explicit: *"a build with no
credentials is unprovisioned, not secure."* This programme exists to close
that gap correctly rather than by re-introducing baked secrets.

### 1.3 Why prebuilt firmware needs a first-use / ownership process

A prebuilt `.bin` is immutable and identical for every downloader —
per-device secrets **cannot** be compiled into it without either a
per-device build (Option B) or an injection step outside the binary. The
only ways a fleet of identical binaries can end up with unique credentials
are: inject at manufacturing, inject at flash time, generate at first
boot, or establish during an owner-driven claim. Every one of those is an
*ownership-establishment* process: the device must learn, exactly once and
verifiably, who its owner is, and derive or receive credentials only that
owner holds.

### 1.4 Why all the journeys must be designed together

Provisioning is not a single flow; it is a lifecycle that must stay
coherent across:

- **Browser flashing** (WebFlash / Web Serial): the production install
  path; whatever the architecture is, it must work when the user's only
  tool is a browser.
- **Home Assistant adoption**: the primary (possibly only) consumer of the
  native API; the credential the device holds must reach HA without being
  published.
- **Recovery**: owners lose HA databases, phones, and printed cards; a
  device that cannot be recovered locally becomes e-waste or a support
  burden.
- **Replacement boards / RMA**: a replacement Core must be claimable by
  the same owner without Sense360 holding the owner's secrets.
- **Factory reset**: must exist, must be deterministic, and must not be a
  remote-attack primitive.
- **Offline use**: local-first is a product value; provisioning that
  requires a cloud round-trip contradicts it.

Designing any one flow in isolation (e.g. flash-time injection with no
recovery story) produces either lockout or a silent security hole
(e.g. "factory reset reopens everything forever with no owner
notification"). This ADR therefore specifies the state machine and
lifecycle before any implementation.

### 1.5 Repository responsibilities

Per the [SOT operating model](https://github.com/sense360store/SOT/blob/main/CLAUDE-OPERATING-MODEL.md)
and [`docs/system-architecture.md`](../system-architecture.md):

- **esphome-public** (this repo) owns the firmware architecture, this ADR,
  the device state machine, persistence, firmware tests, release
  mechanics, and hardware-facing behaviour.
- **WebFlash** owns browser flashing, manifests, installer UX and
  truthfulness, distribution gates, and any browser-side provisioning
  surface.
- **SOT** owns programme status, the accepted decision record, open gates,
  and owner decisions. Programme status changes land in SOT first.

The cross-repo contract remains exactly three stable surfaces: release
tags, config strings, artifact names. Provisioning must not add hidden
coupling beyond an explicitly versioned provisioning capability flag (see
§12, §13).

---

## 2. Problem statement

> **Each physical device must establish device-unique credentials without
> publishing shared secrets, while preserving a workable onboarding,
> recovery, reflashing, and ownership-transfer path.**

Precisely: given an immutable public binary served to anyone, produce, per
physical unit, (a) a unique API encryption key, (b) unique OTA
authentication material, (c) an authenticated-or-disabled web interface,
and (d) a protected-or-time-limited setup surface — such that only the
person with legitimate ownership of the physical unit ever holds those
credentials, and such that losing any single artefact (HA config, printed
card, browser session) does not permanently brick or permanently expose
the device.

The problem decomposes by **when** unique material can enter the device.
These five provisioning times are distinct and are used throughout this
document:

| Provisioning time | Definition | Who acts |
|---|---|---|
| **Manufacturing-time** | Secrets injected into the unit (flash/eFuse/label) before sale | Sense360 / assembler |
| **Build-time** | A unique firmware image compiled per unit | Release pipeline |
| **Flash-time** | Secrets generated/injected during the flashing session, outside the binary | WebFlash (browser) or CLI tool |
| **First-boot** | Device self-generates or accepts secrets in a constrained setup state on first power-up | Firmware |
| **Owner-driven post-boot** | An owner tool (HA, browser, app) claims the device after it is on a network | Owner + firmware |

These are not mutually exclusive; the preferred direction (§8) composes
first-boot self-generation with an owner-driven claim, optionally
bootstrapped by flash-time or manufacturing-time material.

---

## 3. Goals

1. **Unique API encryption material per physical device** — no two units
   ever share a native-API key.
2. **Unique OTA authentication material per physical device.**
3. **Authenticated or disabled web interface** — never an open control
   surface on an owned device.
4. **Protected fallback/setup AP** — open setup surfaces exist only in
   explicitly unowned/bootstrap states, time-boxed where feasible.
5. **No shared production credential across devices**, ever, of any class.
6. **No credential exposure** through public repositories, release assets,
   manifests, build logs, device logs, URLs, browser history/storage,
   analytics, or support bundles.
7. **Compatible with normal Home Assistant onboarding** — the happy path
   must remain "flash, power, adopt in HA" with at most one extra
   claim step.
8. **Recoverable owner experience** — a defined, local, physical-presence
   recovery path for every credential-loss scenario in §9.
9. **Deterministic factory-reset semantics** — one defined physical
   action, one defined result, no ambiguity about what survives.
10. **Clear device-ownership transfer** — sale/gift/RMA results in the new
    owner holding fresh credentials and the old owner holding nothing.
11. **Offline-capable provisioning where practical** — no cloud or
    internet dependency for the core flow.
12. **Testable and auditable behaviour** — every security property in this
    list maps to a contract test in §14 before implementation.
13. **Production WebFlash delivery without false security claims** — the
    installer and manifests state exactly what the firmware provides, per
    the SOT security-claims rules; no claim ships before its evidence.

## 4. Non-goals

1. **A cloud account platform.** No Sense360 accounts, no cloud broker.
2. **Full public-key infrastructure** (per-device certificates, CA
   hierarchy, attestation chains) — not unless a spike proves a concrete
   need the simpler design cannot meet; ESPHome's native surfaces are
   symmetric-key/password shaped today.
3. **Remote fleet management.** Out of scope entirely.
4. **Automatic secret escrow by Sense360.** Sense360 must not silently
   hold customers' device credentials. (Whether *manufacturing bootstrap*
   material may be retained in order records is an explicit owner
   decision, §20 Q1/Q17 — retention of *permanent owner credentials* is a
   non-goal regardless.)
5. **Silently recovering lost owner secrets.** If an owner loses
   everything, recovery goes through the explicit, physical-presence
   recovery mechanism (§11) — never a hidden backdoor.
6. **Changing unrelated sensor behaviour.** Provisioning must be additive;
   sensor/automation behaviour is untouched.
7. **Solving Shopify or commercial workflows.** Order-record delivery of
   bootstrap material (if chosen) is a commercial-surface follow-up owned
   elsewhere; this ADR only defines what the firmware would consume.
8. **Immediate implementation.** This PR contains no implementation; the
   TDD sequence in §14/§15 governs when code lands.

## 5. Constraints

1. **ESP32-S3 / ESPHome platform.** Sense360 Core is an ESP32-S3 running
   ESPHome (pinned per `requirements-dev.txt`). Provisioning logic beyond
   stock ESPHome must land as an external component under `components/`
   (the repo already maintains C++ components there) — forking ESPHome is
   not on the table.
2. **ESPHome credential surfaces are compile-time configured today.** In
   the current tree, `api.encryption.key`, `ota.password`,
   `web_server.auth`, and `wifi.ap.password` are static YAML values baked
   at compile. Whether each can be sourced at runtime from NVS (via lambda,
   component patch, or upstream feature) is **Spike S1** (§8.3) — the
   single most decision-relevant unknown. No option in §7 may be selected
   as final until S1 answers this per credential class.
3. **Browser Web Serial limitations.** Web Serial is available in
   Chromium-desktop browsers only; **not on iOS Safari and not in most
   mobile browsers**. Flash-time-only provisioning therefore excludes
   mobile-only users; any flash-time step needs a device-side fallback.
4. **Home Assistant API expectations.** HA's ESPHome integration supports
   unencrypted and Noise-PSK-encrypted connections; the key is entered (or
   discovered) at adoption time. A key that changes after adoption
   requires the user to update the HA config entry — credential
   desynchronisation is a real failure mode (§6, §9.15).
5. **ESPHome OTA capabilities.** The `esphome` OTA platform supports a
   password (challenge-based). There is no bearer-token or
   per-session-credential OTA mechanism in stock ESPHome; anything
   stronger is custom work (Q6 in §20).
6. **Persistence / NVS behaviour.** ESPHome preferences and WiFi
   credentials persist in NVS on the ESP32. NVS survives OTA and normal
   app reflash; it is destroyed by full flash erase (`esptool
   erase_flash`, or an installer's "erase device" path). Any
   credential-persistence design inherits exactly these semantics — and
   the NVS partition is **readable by anyone with physical USB access**
   unless flash encryption is enabled (an eFuse-burning, effectively
   irreversible step — Spike S4).
7. **Flash erase and factory reset.** There is currently **no factory-reset
   component in any product composition** — today "factory reset" means
   "full flash erase over USB". The ADR must define reset semantics
   (§10, §11) that do not depend on hidden behaviour.
8. **Power-loss resilience.** First-boot generation and claim flows must
   be atomic-or-retryable: a unit power-cycled mid-provisioning must come
   back in a defined state (never half-owned, never credential-less but
   marked owned).
9. **No-internet assumption.** The core flow must complete on an isolated
   LAN (local-first onboarding). Internet may enhance (e.g. fetching a
   nicer UI) but never gate provisioning.
10. **Prebuilt binary immutability.** Release artifacts are
    content-hashed, cosign-signed (checksums), and pinned by WebFlash
    `expected_sha256`. Nothing may mutate a published binary; per-device
    material must live outside the signed image (NVS, separate flash
    region, or generated on-device).
11. **No per-device rebuild requirement** unless explicitly chosen and
    justified (Option B is assessed and currently disfavoured, §7/§19).
12. **SOT visibility versus public docs.** SOT's programme entry is
    `visibility: internal` until the security advisory publishes. This
    public ADR must not disclose SOT-internal commercial details; it
    contains architecture only.
13. **Support and RMA implications.** Support must be able to guide
    recovery **without** the ability to remotely unlock devices (no
    support backdoor), and RMA units must be returnable to a clean unowned
    state (§11, §18).
14. **Standing invariants are untouched.** Nothing here changes release
    channels, fan-lane posture, FanTRIAC rules, or the declaration-driven
    release matrix ([`docs/standing-invariants.md`](../standing-invariants.md)).

## 6. Threat model

### 6.1 Assets

- **A1** — API encryption key (full device control via native API).
- **A2** — OTA credential (arbitrary firmware replacement → persistent
  compromise).
- **A3** — Web UI credential (device control + config visibility).
- **A4** — Fallback-AP/setup surface (LAN credential harvesting via
  captive portal; device reconfiguration).
- **A5** — Owner's home WiFi credentials (entered during setup; stored in
  device NVS).
- **A6** — Bootstrap/claim material (whatever proves the right to become
  owner).
- **A7** — Ownership state itself (who the device obeys).

### 6.2 Actors

- **Legitimate owner** (and household members).
- **LAN-resident attacker** — malware on a laptop/phone/IoT device on the
  same network; RF-range attacker for AP surfaces.
- **Opportunistic first-claimer** — a neighbour/guest racing the owner to
  claim an unowned device.
- **Physical-access attacker** — has the unit in hand (burglar, buyer of a
  stolen unit, malicious housemate).
- **Second-hand buyer / RMA recipient** — legitimate future owner of a
  previously owned unit.
- **Support/Sense360** — must be *unable* to access owner credentials
  (trusted for firmware authorship, untrusted for owner secrets).
- **Public observer** — anyone reading the repo, release assets,
  manifests, WebFlash JS, or network captures of public surfaces.

### 6.3 Trust boundaries (explicit)

1. **Public internet / repo / release assets ↔ everything** — nothing
   secret may exist on the public side. (Enforced today by the deny-list
   gate; provisioning must keep it true.)
2. **LAN ↔ device** — the LAN is **untrusted** in OWNED state (all
   surfaces authenticated) and only *conditionally* trusted in
   bootstrap states (time-boxed, physical-presence-anchored).
3. **Browser flashing session ↔ device** — trusted only for the duration
   of the physical USB session; anything it learns must be transient
   (§13 WebFlash rules).
4. **Home Assistant ↔ device** — trusted after key exchange during claim;
   HA holds A1 thereafter.
5. **Physical possession ↔ device** — physical access is the ultimate
   root of trust for claim, recovery, and reset. Without flash encryption
   (Spike S4) physical access also means NVS read access; the model must
   be honest that a physical attacker with USB tools defeats stored-secret
   confidentiality on the current hardware posture.
6. **Sense360 ↔ owner secrets** — a hard boundary: permanent owner
   credentials never cross to Sense360 (non-goal 4).

### 6.4 Attack surfaces and failure modes (each maps to §14 tests)

| # | Threat | Notes / required property |
|---|---|---|
| T1 | Reuse of one device's credentials on another device | Impossible by construction: credentials generated per unit, never shared. Two-device uniqueness test. |
| T2 | Credentials embedded in public binaries | Deny-list gate stays; provisioning adds no baked secret. Binary-scan test. |
| T3 | Credentials in WebFlash metadata or JavaScript | WebFlash must never persist or transmit generated material; manifests carry no secrets. Browser test + WebFlash review gate. |
| T4 | Credentials visible in URLs, logs, browser storage, clipboard, screenshots, analytics | No secret ever appears in a URL/query string, device log line, or persisted browser state; display of a secret (if UX requires it) is explicit, one-time, and user-acknowledged. Log/URL-scan tests. |
| T5 | Malicious LAN user during first boot | Unowned device is a race window (T6) and an open surface; mitigations: constrained setup state (no relay/actuator control pre-claim where feasible — Q18), time-boxed bootstrap window, physical-presence proof for claim. |
| T6 | Claim race — attacker claims before owner | Physical-presence proof (button press / power-cycle pattern / label secret) required to enter CLAIM_IN_PROGRESS; claim without it must be impossible, not just unlikely. |
| T7 | Downgrade/reflash to unprovisioned firmware | An attacker with OTA credentials can flash anything (that is ownership); an attacker *without* credentials must not be able to push an older unprovisioned image OTA. Serial reflash = physical access = legitimate reset path. §12 policy. |
| T8 | Factory-reset abuse | Reset must require the defined physical action; a reset device returns to FACTORY_UNOWNED with **all owner secrets erased** (safe default: attacker gains a blank device, not the owner's WiFi/API keys). |
| T9 | Stolen or resold device | Same as T8: reset wipes A1–A6; prior owner's credentials never recoverable from the unit post-reset (subject to the flash-encryption caveat, boundary 5). |
| T10 | Support/RMA access | No support credential, no master key, no serial-number-derived secret. RMA = factory reset by owner or documented physical procedure. |
| T11 | Weak randomness | Device-generated secrets must use the ESP32 hardware RNG with entropy adequacy verified (Spike S3); no time-seeded or serial-derived material. Entropy contract test. |
| T12 | Interrupted provisioning | Power loss mid-claim → state machine re-enters a defined pre-claim state; partial credentials are discarded, never half-applied. Fault-injection test. |
| T13 | Credential desynchronisation with HA | Key rotation/reset while HA holds the old key must fail visibly and recoverably (re-adopt path), not brick the integration silently. Integration test. |
| T14 | Rollback/recovery abuse | The recovery path must not be a cheaper attack than the front door: recovery requires the same physical-presence proof as claim, and always destroys existing credentials rather than revealing them. |

## 7. Options considered

Assessment key: each option is scored against the thirteen criteria
required by the programme (security; operational complexity;
manufacturing complexity; user experience; offline support; recovery;
RMA/support; WebFlash compatibility; Home Assistant compatibility; secret
exposure risk; scalability; testability; downgrade behaviour).

### Option A — Manufacturing-time injection

Unique secrets injected per unit before sale (NVS pre-write or
label/QR/secure card/order record delivering the values to the owner).

- **Security:** strong uniqueness; secrets exist before the device ever
  meets a network. But the full permanent credential set exists *outside*
  the owner's control (label, order system) — a lost/photographed card is
  full compromise until reset.
- **Operational/manufacturing complexity:** highest of all options —
  requires a per-unit flashing/labelling step, secure handling in
  assembly, and label↔unit integrity. Sense360's current model ships
  boards without a per-unit firmware personalisation step.
- **UX:** good (credentials on a card) until the card is lost.
- **Offline:** excellent.
- **Recovery:** re-read the card; lost card ⇒ needs a reset path anyway.
- **RMA/support:** replacement unit ⇒ new card; straightforward but
  logistics-heavy.
- **WebFlash compatibility:** poor fit — a user reflashing via WebFlash
  gets a binary that knows nothing of the label secrets unless firmware
  reads them from a preserved NVS region; a full erase (§5.6) destroys
  injected material and the label becomes a dead artefact.
- **HA compatibility:** fine (user types the key from the card).
- **Secret exposure risk:** manufacturing records + physical label are new
  long-lived exposure surfaces (§17).
- **Scalability:** linear cost per unit; acceptable at Sense360 volume but
  a standing process burden.
- **Testability:** hard to test end-to-end in CI (needs manufacturing
  simulation).
- **Downgrade:** reflash/erase destroys injected secrets → device falls
  back to whatever the binary's unowned behaviour is; the label can no
  longer be trusted to match the device.
- **Verdict:** viable *only* as a delivery channel for **bootstrap**
  material (a claim code), not for permanent credentials. Kept as an
  optional input to Option F; rejected as the standalone answer (§19).

### Option B — Per-device build-time firmware

The pipeline compiles a unique image (or secret overlay) per unit.

- **Security:** unique, but the pipeline (and its logs/artifacts) becomes
  a custodian of every customer's credentials — directly violating
  non-goal 4 and trust boundary 6.
- **Operational complexity:** breaks the entire release model: immutable
  tagged artifacts, `expected_sha256` pinning, cosign signing, the
  declaration-driven matrix (ESP-007), and WebFlash's static manifest all
  assume *one* artifact per config string. Per-device builds are
  incompatible with "browser downloads a published release asset".
- **Manufacturing:** none, but replaced by build-infrastructure burden.
- **UX:** terrible for WebFlash (per-user build queue), fine for
  self-builders (this **is** today's self-build path, and it remains
  supported).
- **Offline:** poor (build service required).
- **Recovery/RMA:** requires re-issuing builds; Sense360 again holds
  secrets.
- **WebFlash compatibility:** fundamentally incompatible as production
  path.
- **Testability:** the *mechanism* is testable, but the artifact-integrity
  contract (same hash for all) is destroyed.
- **Downgrade:** each unit's image is unique; version management explodes.
- **Verdict:** rejected as the production path; explicitly retained as the
  **self-build** path users already have (§0, §16).

### Option C — Browser/WebFlash-generated credentials at flash time

The browser generates secrets during the Web Serial session and injects
them (e.g. writing an NVS blob after flashing, as ESPHome's own web
installer does for WiFi via Improv Serial).

- **Security:** unique per flash; secrets born in the session. But they
  exist in browser memory, and any bug (analytics, logging, extension
  access) exposes them — T3/T4 concentrate here. The user must also be
  shown/handed the API key for HA, creating clipboard/screenshot surface.
- **Operational complexity:** moderate; needs a WebFlash NVS-writing
  capability and a firmware NVS-consuming capability (Spike S1/S2).
- **Manufacturing:** none.
- **UX:** good on desktop Chromium; **unavailable on iOS/mobile** (§5.3) —
  cannot be the only path.
- **Offline:** WebFlash itself is a web page; a cached/PWA session can
  work, but this is not truly offline-first.
- **Recovery:** re-flash regenerates; but losing the displayed key with no
  device-side recovery = re-flash dependency on a desktop browser.
- **RMA/support:** clean (reflash = new credentials).
- **WebFlash compatibility:** by definition; but it moves security-critical
  code into WebFlash, raising that repo's assurance burden (§13).
- **HA compatibility:** user copies the key from browser to HA — workable,
  fiddly, exposure-prone.
- **Secret exposure risk:** the highest browser-side risk of all options.
- **Scalability/testability:** good; browser tests possible (Playwright).
- **Downgrade:** flashing an older image leaves the NVS blob unread —
  device silently unprovisioned unless §12 gates apply.
- **Verdict:** not the backbone. Retained as a *possible accelerator*
  (pre-seeding bootstrap material at flash time) inside Option F, decided
  by Q3/Q11.

### Option D — First-boot local provisioning

The device boots unowned in a constrained setup state and establishes
credentials through a local flow (captive portal / setup web page):
device **self-generates** permanent secrets on first boot, then hands
them to the owner over the setup channel.

- **Security:** permanent secrets are device-generated (T11 hardware RNG),
  never exist off-device until the owner retrieves them. The weak point is
  the *unauthenticated setup window*: whoever reaches the setup surface
  first is treated as owner (T5/T6) unless a physical-presence proof is
  added — which is exactly what Option F adds.
- **Operational/manufacturing complexity:** none off-device; firmware-only.
- **UX:** matches the existing flow (open AP + captive portal today);
  adds "note down / accept the API key" during setup.
- **Offline:** excellent — fully local.
- **Recovery:** natural: physical reset returns to first-boot state.
- **RMA/support:** clean — reset = new identity.
- **WebFlash compatibility:** perfect — binary stays immutable and
  identical; WebFlash changes nothing (or merely documents the flow).
- **HA compatibility:** good; key displayed at setup, entered at adoption
  (or delivered via the claim channel in Option E/F).
- **Secret exposure risk:** low off-device; on-device NVS caveat
  (boundary 5).
- **Scalability:** perfect (nothing per-unit off-device).
- **Testability:** strong — host-simulated state machine tests + bench.
- **Downgrade:** older binaries simply lack the flow; §12 policy governs
  claims.
- **Verdict:** the strongest single foundation, but incomplete against
  T5/T6 without a presence proof → folded into Option F.

### Option E — Home Assistant-driven claim

HA discovers an unowned device and claims it over a temporary local
bootstrap channel (e.g. unencrypted API used exactly once to negotiate a
key, or an mDNS-advertised claim endpoint).

- **Security:** as D, plus the credential lands directly in HA config
  (no human copying — T4 shrinks). Race window identical to D without
  presence proof.
- **Operational complexity:** depends on HA-side behaviour we do not
  control; whether stock HA can drive any claim handshake without a
  custom integration is **Spike S5**.
- **UX:** the best possible ("device appears in HA, click Configure,
  press the device button").
- **Offline:** excellent (HA is local).
- **Recovery:** needs a non-HA fallback anyway (HA lost = §9.15).
- **WebFlash compatibility:** unaffected.
- **HA compatibility:** by definition — but *only* HA (Q12: is HA the only
  supported owner? If yes this is acceptable as primary, still not sole,
  channel).
- **Secret exposure risk:** low.
- **Testability:** integration tests against the ESPHome/HA protocols;
  more moving parts than D.
- **Downgrade:** as D.
- **Verdict:** highly desirable **claim transport** layered on D/F, not a
  standalone architecture (a non-HA local path must exist regardless).

### Option F — Hybrid bootstrap model

A short-lived bootstrap secret or **physical-presence proof** gates entry
to a claim flow; the device **generates** permanent credentials
(hardware RNG) at claim time; bootstrap access is invalidated immediately
and irreversibly on successful claim; recovery = physical factory reset
back to the bootstrap-capable state.

- **Security:** best composite: unique device-generated permanent secrets
  (T1/T2/T11), no permanent secret ever off-device before the owner holds
  it, claim gated on physical presence (T5/T6), bootstrap one-way
  invalidation (T14), reset-to-blank semantics (T8/T9).
- **Operational complexity:** firmware state machine + claim endpoint;
  optional label/flash-time bootstrap inputs can be added later without
  rearchitecting.
- **Manufacturing:** zero *required* (presence-proof variant); optional QR
  bootstrap variant adds label logistics (owner decision Q1/Q3).
- **UX:** "flash → power → join setup surface or wait for HA discovery →
  press the device button when asked → done." One physical action added
  to today's flow.
- **Offline:** fully local.
- **Recovery:** defined and local (§11).
- **RMA/support:** reset-to-unowned covers it (§18).
- **WebFlash compatibility:** binary immutable; WebFlash optionally gains
  a *documentation* role only (or a flash-time bootstrap seeding role if
  Q3 says yes).
- **HA compatibility:** claim via captive-portal/web flow always works;
  HA-driven claim (Option E transport) added if Spike S5 succeeds.
- **Secret exposure risk:** lowest overall; residual = NVS physical-read
  (Spike S4) and the one-time key handover to HA.
- **Scalability:** perfect.
- **Testability:** state machine is host-testable; uniqueness, one-way
  transition, and reset semantics all contract-testable; bench tests for
  the physical action.
- **Downgrade:** unowned/owned state lives in NVS; an older binary that
  ignores it reverts the *behaviour* to unprovisioned — §12 policy defines
  the required gates and honest claims.
- **Verdict:** **preferred direction** (§8), pending owner decisions and
  spikes.

## 8. Proposed decision (direction, not acceptance)

The repository evidence supports a clear *direction* but not a final
selection: the decisive unknowns (runtime credential sourcing in ESPHome —
Spike S1; HA claim transport — S5; flash-encryption posture — S4) are
unresolved, and several choices are owner decisions (§20). **This ADR
therefore selects no final architecture.** Status remains **Proposed**.

### 8.1 Preferred direction

**Option F (hybrid bootstrap), built on Option D's first-boot foundation,
with Option E as a preferred claim transport where feasible:**

1. **Explicit unowned/bootstrap state.** A device flashed with a
   provisioning-capable release boots into `FACTORY_UNOWNED`; its
   behaviour there is constrained and honest (it claims no security).
2. **Physical-presence proof or one-time bootstrap material** gates the
   claim. Baseline proposal: a physical action on the unit (boot-button
   press / defined power-cycle pattern — hardware-confirmed in Spike S2).
   Optional additive channels (owner decisions): QR/label one-time claim
   code (Q3), flash-time-seeded bootstrap token (Q11).
3. **Device-generated, cryptographically strong permanent credentials**
   (ESP32 hardware RNG; entropy verified in Spike S3): API key, OTA
   secret, web credential, AP password — generated on-device at claim,
   delivered once over the claim channel to the owner/HA.
4. **One-way transition** `FACTORY_UNOWNED → OWNED` through
   `CLAIM_IN_PROGRESS`; the only reverse path is the physical factory
   reset (§10/§11).
5. **Immediate bootstrap invalidation:** on claim success, all bootstrap
   access (open AP, claim endpoint, any bootstrap token) is invalidated
   before the claim response completes, atomically with the ownership
   commit (T12: commit is all-or-nothing in NVS).
6. **Clear local recovery / factory-reset path:** one defined physical
   action wipes all credentials and ownership and returns the unit to
   `FACTORY_UNOWNED` (§11).
7. **No permanent secrets in public firmware or WebFlash metadata** —
   preserved by construction; the existing deny-list artifact gate remains
   as the enforcement backstop.

### 8.2 Required owner decisions before final ADR

The full table is §20. The blocking subset: Q1 (manufacturing injection
acceptable?), Q2 (zero-internet mandatory? — recommended yes), Q3
(printed/QR bootstrap acceptable?), Q4 (device-generated permanent
credentials mandatory? — recommended yes), Q5 (web server authenticated
vs disabled default), Q7 (what survives normal reflash), Q8 (exact
factory-reset action), Q9 (physical presence mandatory for claim —
recommended yes), Q12 (is HA the only supported owner surface).

### 8.3 Unresolved technical spikes (pre-implementation)

| Spike | Question | Blocks |
|---|---|---|
| **S1** | Can `api.encryption.key`, `ota.password`, `web_server.auth`, and `wifi.ap.password` each be sourced at runtime from NVS in the pinned ESPHome version (lambda/component/upstream patch)? Per-class answer required. | Everything — the architecture's core mechanism |
| **S2** | Which physical-presence signal is available and reliable on S360-100 R4 (boot button exposure in ceiling mount? power-cycle pattern? touch of an existing sensor?) | Claim UX; §10 physical-presence column |
| **S3** | Entropy adequacy of the ESP32-S3 hardware RNG at first-boot time (RF calibration state), and the generation recipe (key sizes, encoding) | Credential generation (T11) |
| **S4** | Cost/benefit of ESP32 flash encryption + secure boot for NVS confidentiality (eFuse irreversibility, OTA implications, WebFlash erase implications) | Physical-attacker posture claim (boundary 5) |
| **S5** | Can stock Home Assistant drive a claim handshake (adopt-then-encrypt, or a custom-integration-free flow)? | Option E transport |
| **S6** | ESP Web Tools / WebFlash erase semantics: which install paths erase NVS, and can WebFlash offer "reflash preserving ownership" safely? | §11/§12 reflash matrix |

### 8.4 Acceptance criteria before this ADR can move to Accepted

Listed in §21; in short — owner decisions resolved, S1–S6 answered,
security review done, recovery and downgrade semantics final, test plan
agreed, WebFlash responsibilities agreed, no false claim anywhere, SOT
records the acceptance.

## 9. Credential lifecycle

### 9.1 Lifecycle phases (applies per credential class; deviations noted)

| Phase | Proposed behaviour |
|---|---|
| **Generation** | On-device, at claim time (not at first boot of the flash — avoids generating secrets nobody will ever retrieve), from the ESP32 hardware RNG (S3 recipe). Never derived from MAC/serial/time. |
| **Entropy requirements** | ≥128-bit effective entropy per secret; API key = 32-byte Noise PSK (base64); passwords generated to ESPHome-accepted charset/length (S3 fixes exact recipe). |
| **Temporary bootstrap** | Whatever gates the claim (physical press, one-time code). Never reusable, never a permanent credential, invalidated at claim commit. |
| **Owner claim** | The one-time handover: device transmits generated credentials over the claim channel (captive-portal page / claim endpoint / HA transport per S5) exactly once, then marks them delivered. |
| **Storage** | Device: NVS, under a dedicated namespace, atomically committed with the ownership flag (T12). Owner: HA config entry (API key), user's password manager (others) — documented guidance, §18. |
| **Use** | Standard ESPHome surfaces: Noise-encrypted API, password-checked OTA, authenticated web, protected AP. |
| **Rotation** | Owner-initiated only, from an authenticated session; device generates the replacement, old value invalid on commit. Rotation of the API key requires HA re-entry (T13 warning in UX). Not part of MVP unless owner requires (Q6). |
| **OTA update** | Credentials and ownership persist (NVS untouched by OTA). Contract test: post-OTA, same credentials work. |
| **Normal reflash (serial, no erase)** | NVS persists → ownership persists **if** the new image is provisioning-capable. Owner decision Q7 confirms this is the desired semantic. |
| **Full flash erase** | NVS destroyed → device returns to `FACTORY_UNOWNED` with no credentials. This **is** the out-of-band factory reset (physical access by definition). |
| **Factory reset (in-band)** | The defined physical action (Q8) wipes the credential namespace + ownership flag and reboots into `FACTORY_UNOWNED`. Deterministic; §11. |
| **Ownership transfer** | Factory reset by the departing owner (or by the new owner with physical access), then a fresh claim by the new owner. Old credentials are destroyed, not handed over. |
| **Support/RMA** | Support instructs reset; Sense360 never receives or recovers owner credentials. RMA outbound replacements ship unowned. |
| **Device replacement** | New unit = new claim = new credentials; HA re-adoption required (documented). No credential cloning between units — ever (T1). |
| **Loss of HA configuration** | Device still owned + owner still has credentials → re-enter key in HA. Owner lost credentials too → §9 "lost owner credentials". |
| **Lost owner credentials** | No recovery of the *values* (non-goal 5). Recovery = physical factory reset → re-claim → new credentials (§11). |
| **Decommissioning** | Factory reset (wipes A1–A6 including stored WiFi) before disposal/sale; documented as the required step. |

### 9.2 Per-credential-type ownership and lifecycle

| Credential | Holder(s) | Generated | Invalidated by | Notes |
|---|---|---|---|---|
| **HA API encryption key (Noise PSK)** | Device NVS + HA config entry | At claim, on-device | Factory reset; rotation | The only credential that must be *shared with* another system routinely; claim channel should deliver it to HA directly where S5 allows (minimises T4). |
| **OTA password/token** | Device NVS + owner records | At claim, on-device | Factory reset; rotation | Owner needs it only for manual `esphome upload`; HA OTA via the device's update mechanism is out of MVP scope. Q6 covers stronger-than-password mechanisms. |
| **Web authentication** | Device NVS + owner records | At claim, on-device | Factory reset; rotation | Or web server disabled by default in OWNED state (owner decision Q5) — disabling removes the credential class entirely. |
| **Fallback/setup AP protection** | Device NVS | At claim, on-device | Factory reset | In `FACTORY_UNOWNED` the AP is open **by definition** (it is the setup surface) but constrained + time-boxed; in OWNED it is password-protected with the generated value (or disabled — Q5 companion decision). |
| **Bootstrap/claim secret (if Q3/Q11 adopt one)** | Label/QR/order record or flash-session, + device | Pre-claim (manufacturing or flash time) | Single use; claim commit; expiry timer | Never grants control by itself — only the right to *start* a claim. Its delivery channel privacy is §17. |

## 10. Device state machine

States (proposal — names become contract-test vocabulary):

- **`FACTORY_UNOWNED`** — no credentials, no owner. Setup surfaces
  available; control surfaces constrained.
- **`BOOTSTRAP_AVAILABLE`** — sub-state of unowned where a claim window is
  open (after physical trigger, or always-on while unowned — owner
  decision Q9 nuance; time-boxed if triggered).
- **`CLAIM_IN_PROGRESS`** — a claimant passed the bootstrap gate; device
  is generating/handing over credentials. Single claimant; short timeout.
- **`OWNED`** — credentials active on all surfaces; setup surfaces closed
  or authenticated.
- **`RECOVERY`** — owner-initiated recovery window (physical action) on an
  owned device; allows re-delivery of *new* credentials without full
  reset if the owner chooses (§11.4), else exits back to OWNED.
- **`FACTORY_RESET_PENDING`** — the defined reset action has been armed
  (e.g. button held; confirmation window running) but not yet executed —
  the accidental-reset guard (§11.6).

### State-transition table

| From | Event | To | Guard |
|---|---|---|---|
| *(fresh flash / post-erase boot)* | boot, no ownership record | FACTORY_UNOWNED | — |
| FACTORY_UNOWNED | physical presence proof (or valid one-time bootstrap code) | BOOTSTRAP_AVAILABLE | Q9; window timer starts |
| BOOTSTRAP_AVAILABLE | window timeout / reboot | FACTORY_UNOWNED | discard nothing (no secrets exist yet) |
| BOOTSTRAP_AVAILABLE | claimant opens claim channel | CLAIM_IN_PROGRESS | one claimant; others rejected |
| CLAIM_IN_PROGRESS | claim completes: credentials generated, delivered, acknowledged | OWNED | atomic NVS commit (ownership flag + credentials together); bootstrap invalidated pre-ack (T12, §8.1.5) |
| CLAIM_IN_PROGRESS | timeout / power loss / claimant abandons | FACTORY_UNOWNED | partial material discarded; nothing persisted (T12) |
| OWNED | boot / OTA / normal reflash (capable image) | OWNED | credentials verified present in NVS |
| OWNED | physical recovery action | RECOVERY | physical presence required (T14) |
| RECOVERY | timeout / cancel | OWNED | no change |
| RECOVERY | owner completes re-key | OWNED | new credentials committed atomically; old invalidated |
| OWNED | physical reset action armed | FACTORY_RESET_PENDING | §11.6 guard (hold time / confirmation) |
| FACTORY_RESET_PENDING | confirmation window expires unconfirmed | OWNED | no change |
| FACTORY_RESET_PENDING | reset confirmed | FACTORY_UNOWNED | credential namespace wiped before reboot |
| *(any)* | full flash erase (external, USB) | FACTORY_UNOWNED | physical access by definition |

### Per-state specification

| State | Interfaces available | Auth required | Time limit | Persisted data | Failure behaviour | Physical presence |
|---|---|---|---|---|---|---|
| FACTORY_UNOWNED | WiFi setup (open AP + captive portal, setup-network join); claim trigger; **no actuator control where feasible (Q18)**; API/web/OTA per Q19 (recommend: disabled or read-only until owned) | None (honest: no security claimed) | None (persistent state) | None (plus non-secret state flag) | Reboot → same state | Not required to *be* in state |
| BOOTSTRAP_AVAILABLE | As above + claim endpoint advertised (mDNS/portal) | Bootstrap gate already passed | **Yes** — short window (e.g. minutes; S2/UX fixes value) | Window state (RAM only) | Timeout → FACTORY_UNOWNED | **Yes** (the gate) |
| CLAIM_IN_PROGRESS | Claim channel only; other setup surfaces frozen | Claim-session binding | Yes — short | Nothing until final commit | Any failure → FACTORY_UNOWNED, material discarded | Already proven |
| OWNED | Encrypted API, authenticated OTA, authenticated-or-disabled web, protected-or-disabled fallback AP | **All surfaces authenticated** | None | Credentials + ownership + WiFi (NVS) | Boot with corrupt credential record → RECOVERY-equivalent safe halt, never silent-open (fail closed; exact behaviour a §14 contract test) | For state changes only |
| RECOVERY | Recovery channel (local, constrained) | Physical action + (existing credential where available) | Yes — short | Unchanged until commit | Timeout → OWNED unchanged | **Yes** |
| FACTORY_RESET_PENDING | Confirmation surface only | Physical action | Yes — short confirmation window | Unchanged until confirmed | Expire → OWNED unchanged | **Yes** |

## 11. Recovery and reset semantics

### 11.1 Action → effect matrix (proposed; Q7/Q8 finalise)

| Action | What it is | Credentials survive? | Ownership survives? |
|---|---|---|---|
| **Reboot / power cycle** | Normal restart | Yes | Yes |
| **OTA update** | New app image over authenticated OTA | Yes (NVS untouched) | Yes |
| **Normal reflash** (serial, app write, no erase) | New image over USB without flash erase | Yes, **if** the new image is provisioning-capable (Q7); older image → §12 | Record survives in NVS; honoured only by capable firmware |
| **Full flash erase** (`esptool erase_flash`, installer "erase device") | All flash including NVS wiped | **No** | **No** → FACTORY_UNOWNED |
| **Factory reset** (in-band, the defined physical action) | Firmware wipes credential namespace + ownership | **No** | **No** → FACTORY_UNOWNED |

### 11.2 Ownership transfer

Departing owner performs factory reset (or new owner does, having
physical access). Device returns to FACTORY_UNOWNED; new owner claims
normally. **Transfer never copies credentials**; previous owner's access
is destroyed by the reset (contract test §14).

### 11.3 Owner lost Home Assistant configuration

Device is OWNED and healthy. If the owner still holds the API key
(password manager, printed record): re-add in HA — no device action. If
not: physical **RECOVERY** action → device re-keys (generates *new*
credentials, delivers over the recovery channel, invalidates old) →
re-adopt in HA. No values are ever *revealed* — only replaced (T14).

### 11.4 Whether recovery requires physical access

**Yes — recommended and assumed throughout (Q9).** Remote recovery is
indistinguishable from attack (T14).

### 11.5 Returning to unowned

Only via factory reset or full flash erase — both physical. No network
path may reach FACTORY_UNOWNED (contract test).

### 11.6 Accidental-reset prevention

The reset action must be deliberate: long-hold plus confirmation window
(FACTORY_RESET_PENDING), with the exact gesture fixed by S2 hardware
findings. A bare reboot, power blip, or short press must never reset.

### 11.7 Evidence before support advises a reset

Support asks the owner to confirm: (a) physical possession, (b) the
device's observable state (LED pattern / AP name / HA status), (c) that
recovery (11.3) does not apply. Reset advice destroys credentials, so it
is the last resort, and the checklist becomes a support document (§18).
Support has no override capability by design (T10).

## 12. Downgrade and release policy

1. **Owned device flashed with an older unprovisioned binary** (serial):
   the old image ignores the NVS ownership record → device behaves
   unprovisioned (open surfaces). This is physical-access reflash =
   legitimate. The record persists; reflashing a capable image restores
   OWNED. **OTA downgrade to an unprovisioned image must be refused**
   while OWNED (version/capability floor — contract test; exact mechanism
   is part of Spike S1/S6 scope).
2. **User erases flash:** clean FACTORY_UNOWNED; documented as equivalent
   to factory reset.
3. **A release lacks provisioning support:** it must never *claim*
   provisioning. Claims are per-release facts, gated in-release-pipeline
   (see gate below).
4. **WebFlash stable vs preview:** provisioning capability lands per
   §15 staging (preview first). WebFlash must present per-build
   capability truthfully from declared metadata, never inferring it
   (operating-model rule: no claiming firmware behaviour not proven
   upstream).
5. **Self-build users:** unaffected; the `!secret` path remains. A
   self-build with static secrets and the provisioning flow disabled
   remains a supported configuration; docs must state the difference
   plainly.

**Proposed release gates (extending the existing pattern of
[`check_firmware_default_credentials.py`](../../scripts/check_firmware_default_credentials.py)):**

- **G-P1 — no-claim-without-capability:** release metadata may declare
  `provisioning: true` for a build only when the provisioning contract
  tests (§14) ran against that artifact lineage in CI; the release
  workflow fails closed otherwise.
- **G-P2 — no-shared-secret backstop (existing, retained):** deny-list
  scan of every artifact; extended with any new placeholder/bootstrap
  literals the implementation introduces.
- **G-P3 — capability honesty downstream:** WebFlash imports the
  capability flag only from signed upstream release metadata (WebFlash
  repo work, §13; gate defined there when that PR happens).
- **G-P4 — bench evidence before stable:** the multi-device physical
  bench pass (§14, §15) is required before any **stable**-channel release
  carries `provisioning: true`. Preview may carry it with
  compile+emulation evidence only if labelled per the no-false-proof
  invariant.

## 13. Cross-repository responsibilities

| Repo | Owns |
|---|---|
| **esphome-public** | This architecture and ADR; the firmware implementation (state machine, generation, claim, recovery, reset); NVS persistence layout; unit/contract/integration tests; release-gate scripts and their tests; release evidence; hardware bench evidence records (owner-attested). |
| **WebFlash** | Any browser-side provisioning UX (only if Q3/Q11 adopt flash-time seeding); safe handling of transient material (in-memory only, no persistence, no transmission); **no credential logging or analytics**; manifest and installer truthfulness (capability flags from upstream metadata only); distribution gates (G-P3); erase-vs-preserve install semantics (S6). |
| **SOT** | Programme status (`planned` today — unchanged by this PR); recording the accepted architecture decision when the owner accepts; open gates; owner decisions of record; cross-repo evidence links. |

**Sequencing rule (operating model):** this ADR PR is architecture only.
Implementation (esphome-public), distribution changes (WebFlash), and the
SOT status/decision updates are each **separate PRs** in their owning
repositories, in the §15 order. Nothing in this PR changes WebFlash or
SOT.

## 14. Test-driven delivery plan

Failing **contract tests are written before implementation** (SOT TDD
sequence). Contract vocabulary = the state names in §10. No
implementation tests are added in this ADR PR — the repo has no
ADR-schema test convention, and adding runtime tests now would violate
the architecture-only scope.

### 14.1 Contract tests to write first (all failing until implementation)

| ID | Contract |
|---|---|
| CT-01 | Two devices (or two simulated provisioning runs) never receive the same permanent credentials — any class, any pair. |
| CT-02 | After successful claim, the native API requires the generated Noise key (unencrypted connection refused). |
| CT-03 | After successful claim, OTA without the generated credential is refused. |
| CT-04 | After successful claim, the web interface is authenticated (or absent, per Q5) — never open. |
| CT-05 | After ownership, the fallback AP is protected or unavailable — never open. |
| CT-06 | Bootstrap material cannot be reused after claim (replay of the claim exchange fails; second claimant fails). |
| CT-07 | Interrupted provisioning (power loss at any injected point in CLAIM_IN_PROGRESS) yields FACTORY_UNOWNED with zero persisted partial secrets. |
| CT-08 | No secret appears in tracked files, build logs, release manifests/metadata, URLs, or (browser tests) browser persistence — automated scans, extending the existing deny-list approach. |
| CT-09 | Normal OTA preserves ownership and credentials (same key works after update). |
| CT-10 | Reflash modes preserve/reset ownership exactly per the §11.1 matrix. |
| CT-11 | Factory reset requires the defined physical action; no network-only path reaches FACTORY_UNOWNED. |
| CT-12 | Ownership transfer (reset + re-claim) invalidates all previous-owner credentials. |
| CT-13 | Downgrade behaviour matches §12 (incl. OTA downgrade refusal while OWNED). |
| CT-14 | Recovery path completes with physical presence and existing hardware only — no support/backdoor access exists to fabricate. |
| CT-15 | Generated credentials meet the S3 entropy/format recipe (statistical + format checks). |

### 14.2 Test-tier mapping

- **Unit tests** (host, stdlib `unittest` per repo convention): state
  machine transitions, NVS-record encoding, generation recipe (CT-15
  format half), gate scripts (G-P1/G-P2) — mirroring the existing
  `scripts/ ↔ tests/test_*.py` pattern.
- **Contract tests**: CT-01…CT-15 against a host-simulated device core
  where possible; these are the merge gate for implementation PRs.
- **Integration tests**: ESPHome-compiled firmware in emulation/on-bench:
  HA adoption with generated key (CT-02, T13 desync), OTA flows
  (CT-03/09/13).
- **Browser tests** (WebFlash repo, only if flash-time seeding is
  adopted): no-persistence/no-analytics assertions (CT-08 browser half).
- **Two-device uniqueness tests**: CT-01 on ≥2 physical units — part of
  the bench plan.
- **Physical bench tests** (owner-attested, never agent-authored, per the
  standing attestation rule): claim UX on real hardware, reset gesture,
  RF surfaces (open-AP window, protected AP), multi-device uniqueness.
- **Release gates**: G-P1…G-P4 wired into the release workflow with their
  own pinned tests.

## 15. Rollout plan (staged; each stage its own PR/evidence)

1. **Architecture approval** — owner resolves §20, accepts this ADR
   (SOT records it).
2. **Technical spikes S1–S6** — findings recorded in-repo; ADR updated if
   any spike invalidates the direction (back to owner if so).
3. **Failing contract tests** (CT-01…CT-15) land — red.
4. **Firmware implementation** — smallest change to green, staged
   (state machine → generation → claim → recovery/reset).
5. **WebFlash implementation if required** (Q3/Q11) — separate repo/PR,
   after firmware contract is stable.
6. **Multi-device bench verification** — owner-attested; includes CT-01
   physical run.
7. **Preview release** carrying `provisioning: true` under G-P1/G-P2
   (+G-P4 labelling rules) — preview channel only.
8. **Stable release** — only after bench evidence (G-P4) and soak on
   preview.
9. **Advisory/update messaging** — owner publishes; existing-device
   guidance (§16).
10. **SOT status reconciliation** — separate SOT PRs at each material
    change (planned → active → implemented → verified), evidence-linked.

**Rollback criteria:** any contract-test regression, any credential
exposure (CT-08 class) in a shipped artifact, unrecoverable-lockout
reports from preview, or bench failure of the reset/recovery gestures →
halt promotions, pull the capability flag from affected channel metadata
(never mutate binaries; supersede per the append-only release policy),
publish honest notes, return to stage 4.

## 16. Migration impact

| Population | Impact |
|---|---|
| **Currently unprovisioned rebuilt devices** (v1.0.7/8/9, v1.0.1-led-preview) | Unchanged until reflashed with a provisioning-capable release; then they boot FACTORY_UNOWNED and can be claimed. Messaging (§15.9) invites the upgrade. |
| **Self-built devices with unique secrets** | Zero forced change; `!secret` path remains first-class. They may later opt in by flashing release firmware and claiming. |
| **Devices on old shared-credential releases** | Already urged to reflash by the (pending) advisory; the provisioning release becomes the recommended target. Their burned credentials stay burned (H2) — provisioning does not retroactively protect un-reflashed units and no claim may imply it does. |
| **New devices** | Flash → claim → done; the intended primary path. |
| **Existing HA integrations** | An unprovisioned device later claimed changes from unencrypted to encrypted API — HA config entry must be updated (documented; T13 test). |
| **Preview firmware users** | Get the capability first (§15.7) with honest preview labelling. |
| **Replacement / RMA devices** | Ship unowned; standard claim; old unit reset per §11 before return. |

## 17. Security and privacy implications

- **No cloud dependency by default** — the core flow is local; nothing
  phones home.
- **No secret telemetry** — firmware and WebFlash transmit no credential
  material anywhere, ever; there is no analytics channel for it to leak
  into (WebFlash must keep it that way — §13).
- **Support boundaries** — support can guide but never access; no
  master-key class exists to steal or subpoena.
- **Logging rules** — generated secrets never appear in device logs at
  any log level, in claim-channel server logs, or in CI logs (CT-08);
  logger redaction is part of the implementation contract.
- **Data retention** — Sense360 retains no permanent owner credentials
  (non-goal 4); if Q1/Q3 adopt bootstrap codes via order records, those
  are single-use, claim-invalidated, with retention defined by the owner
  decision (Q17 impact column).
- **Browser storage** — no credential in localStorage/IndexedDB/history;
  transient memory only, if WebFlash participates at all.
- **QR/label privacy (if adopted)** — a label on the device ceiling-mount
  is readable by anyone with physical access; acceptable only because the
  bootstrap code grants a *claim attempt*, not control, and dies at first
  use; labels must never carry permanent credentials.
- **Manufacturing records (if adopted)** — bootstrap-code ↔ unit mappings
  are sensitive-but-not-credential data; scope, storage, and retention go
  to the owner (Q1) before any adoption.
- **Residual risks stated honestly:** physical NVS read without flash
  encryption (S4); the open setup surface while FACTORY_UNOWNED (bounded
  by constrained-state design and claim gating); RF-range attacker
  hosting the public setup network name (unchanged, documented in the
  posture doc).

## 18. Operational implications

- **Manufacturing:** none for the baseline presence-proof design;
  label/QR variant adds a per-unit print step (owner decision).
- **Support:** new runbooks — claim walkthrough, recovery (11.3), reset
  evidence checklist (11.7); support cannot unlock devices and docs must
  say so plainly.
- **Documentation:** getting-started and first-boot docs
  (currently describing the open, unprovisioned flow in
  [`release-firmware-credential-posture.md`](../security/release-firmware-credential-posture.md))
  gain the claim step; self-build docs state the two supported postures.
- **Customer onboarding:** one added physical action; measured against Q13
  (mobile UX) since captive-portal claim must work from a phone.
- **Lost credentials:** deterministic answer (11.3/§9); no case-by-case
  support archaeology.
- **Returns:** reset-before-return instruction; inbound RMA verification
  = device boots FACTORY_UNOWNED.
- **Replacement boards:** claim-again semantics; HA re-adoption note.
- **QA:** bench checklist grows the claim/reset/recovery gestures and the
  two-device uniqueness run (owner-attested).
- **Release management:** new gates G-P1–G-P4 in the release workflow;
  capability flag in release metadata; channel staging per §15.

## 19. Rejected alternatives (at this stage)

| Option | Disposition | Reason |
|---|---|---|
| **A — manufacturing-time injection as the primary mechanism** | Rejected as primary; **retained** as optional bootstrap-delivery channel inside F (owner decision Q1/Q3) | Permanent secrets born outside owner control; label/record exposure surface; heaviest ongoing process cost; dies on full erase; hostile to WebFlash reflash. Not rejected for complexity — rejected because even executed perfectly it still leaves permanent credentials in third-party artefacts. |
| **B — per-device build-time firmware as the production path** | Rejected for production; **retained** as the existing self-build path | Incompatible with immutable signed artifacts, hash-pinned WebFlash distribution, and the declaration-driven release matrix; makes Sense360 infrastructure a credential custodian (non-goal 4). |
| **C — browser-generated credentials as the sole/backbone mechanism** | Rejected as backbone; **unresolved** as optional flash-time bootstrap seeding (Q11) — not rejected outright | Excludes iOS/mobile users entirely (§5.3); concentrates highest secret-exposure risk in the browser; leaves no device-side recovery. These are structural, not complexity, objections to it being the *only* path. |
| **D standalone (first-boot, no presence proof)** | Superseded by F | Leaves the T5/T6 first-claimer race open; F is D plus the missing gate. |
| **E standalone (HA-only claim)** | Superseded by F transport option | Requires a non-HA local path regardless (recovery, non-HA owners — Q12); feasibility unproven (S5). Remains a candidate transport, not an architecture. |
| **Full PKI / per-device certificates** | Not pursued now (non-goal 2) | No consumer among ESPHome's surfaces today; revisit only if a spike shows Noise-PSK + passwords cannot meet a goal. Not rejected forever — parked with a named re-entry condition. |

Options with open owner decisions (A-as-bootstrap, C-as-seeding, E-as-
transport) are **not** rejected merely for complexity; they are held open
in §20 with recommendations.

## 20. Open questions and owner decisions

| # | Question | Options | Recommendation | Owner decision required | Impact if deferred |
|---|---|---|---|---|---|
| Q1 | Is manufacturing-time secret injection acceptable at all? | (a) never; (b) bootstrap-code only; (c) full injection | **(b)** at most — bootstrap only, if ever | Yes | F baseline (presence-proof) proceeds; label channel stays closed |
| Q2 | Must provisioning work with zero internet access? | yes / no | **Yes** (local-first is a product value) | Yes | Design assumes yes; deferring risks rework if no |
| Q3 | Is a printed/QR bootstrap secret acceptable? | yes / no / later | **Later** — ship presence-proof first, add QR if UX data demands | Yes | None immediately; UX fallback options narrow |
| Q4 | Must permanent credentials be device-generated? | device-generated / externally supplied / either | **Device-generated** (T11, non-goal 4) | Yes | Blocks final ADR — core property |
| Q5 | Web server: authenticated or disabled by default in OWNED? | authenticated / disabled / owner-toggle | **Disabled by default, owner-enableable with auth** (smallest surface) | Yes | Blocks CT-04 final wording |
| Q6 | Must OTA remain password-based, or consider another mechanism? | stock password / custom stronger mechanism | **Stock password for MVP**; revisit after S1 | Yes | MVP proceeds on password; stronger scheme becomes 002 follow-up |
| Q7 | What must survive normal (no-erase) reflash? | ownership+credentials / nothing / configurable | **Ownership + credentials survive** (matches NVS reality; least surprise) | Yes | Blocks §11.1 finalisation and CT-10 |
| Q8 | What exactly constitutes factory reset? | button-hold gesture / power-cycle pattern / erase-only | **Button-hold + confirmation** pending S2 hardware findings | Yes | Blocks CT-11 and bench checklist |
| Q9 | Is physical presence mandatory for claim and recovery? | yes / claim-only / no | **Yes, both** (T6, T14) | Yes | Blocks state machine finalisation |
| Q10 | How should RMA/support work? | reset-based, no support access (as §11/§18) / some support capability | **Reset-based, zero support access** | Yes | Support docs blocked; design default stands |
| Q11 | Is browser-based secret display acceptable (and flash-time seeding at all)? | yes / no / bootstrap-token-only | **Bootstrap-token-only at most**; never display permanent secrets in-browser if the claim channel can deliver directly | Yes | WebFlash scope unknown → its PR blocked (firmware path unaffected) |
| Q12 | Is Home Assistant the only supported owner? | HA-only / HA-primary + generic local flow | **HA-primary + generic local claim flow** (recovery needs it anyway) | Yes | S5 priority unclear if deferred |
| Q13 | What UX is acceptable on mobile, given Web Serial limits? | desktop-only flashing with device-side claim on any phone / require desktop for everything | **Flashing desktop-only (status quo); claim/recovery must work from any phone browser** | Yes | Blocks claim-channel UI design |
| Q14 | Bootstrap window: always-open-while-unowned vs physical-trigger-opened? | always / triggered | **Triggered** (shrinks T5 exposure) | Yes | State table nuance (§10) |
| Q15 | Flash encryption / secure boot (S4) in scope for this programme? | in / out / later | **Later** — separate decision after S4 evidence (eFuse irreversibility) | Yes | Posture claims must keep the §6.3(5) caveat |
| Q16 | OTA downgrade refusal while OWNED (§12.1) — required for MVP? | yes / advisory-only | **Yes** (closes T7 remotely) | Yes | CT-13 scope |
| Q17 | If Q1(b)/Q3 adopt codes: retention and storage of code↔unit records? | none post-claim / bounded / indefinite | **None post-claim** | Yes (only if Q1/Q3 adopt) | §17 manufacturing-records section stays hypothetical |
| Q18 | Constrain actuators (relay/fan outputs) while unowned? | yes / no | **Yes where feasible** (limits T5 blast radius; needs per-board feasibility check) | Yes | §10 FACTORY_UNOWNED row stays provisional |
| Q19 | API/web/OTA availability while FACTORY_UNOWNED? | all off until claim / current open behaviour | **Off (or read-only) until claim** — the claim channel is the only setup surface | Yes | Determines whether the unowned posture improves on today's; blocks CT-02..05 preconditions |

## 21. Acceptance criteria for moving this ADR to Accepted

All of the following, none waivable silently:

1. Every owner decision in §20 is resolved and recorded (SOT owner
   decisions of record).
2. Spikes S1–S6 are complete and the chosen architecture is demonstrated
   technically feasible on the pinned ESPHome/ESP32-S3 stack (S1
   especially).
3. Security review of the final design (threat model §6 revisited against
   the concrete mechanism) is complete.
4. Recovery semantics (§11) are explicit, final, and covered by CT tests.
5. Downgrade policy (§12) is explicit, final, and covered by CT tests.
6. The test plan (§14) is agreed, with contract tests enumerated and the
   bench checklist scoped (owner-attested execution reserved to the
   owner).
7. WebFlash responsibilities (§13) are agreed with that repo's plan
   (even if the agreed answer is "WebFlash changes nothing").
8. No false security claim exists anywhere in the proposal, docs, or
   metadata plan (no-false-proof invariant).
9. SOT records the accepted decision — the SOT update **is** the
   acceptance; this document then flips to Accepted referencing it.

Until then: **Status: Proposed.** Implementation must not begin
(operating-model rule: no implementation while required architecture
decisions remain unresolved).

---

## References

- [`docs/security/release-firmware-credential-posture.md`](../security/release-firmware-credential-posture.md) — authoritative shipped-posture statement (SEC-ESP-BUILD-GATES-001)
- [`docs/security/SECURITY-AUDIT-2026-06.md`](../security/SECURITY-AUDIT-2026-06.md) — audit findings H1/H2 (origin of the programme)
- [`docs/rebuild-clean-credentials-001.md`](../rebuild-clean-credentials-001.md) — rebuild programme plan of record; R-D4 owner bench attestation (pending)
- [`docs/sense360-roadmap-status.md`](../sense360-roadmap-status.md) — canonical repo status doc (§1.1 credential posture)
- [`docs/standing-invariants.md`](../standing-invariants.md) — standing gates (unchanged by this ADR)
- [`docs/system-architecture.md`](../system-architecture.md) — two-repo pipeline and cross-repo contract
- [SOT `CLAUDE-OPERATING-MODEL.md`](https://github.com/sense360store/SOT/blob/main/CLAUDE-OPERATING-MODEL.md) — authority model, ADR requirements, evidence rules
- SOT `roadmap.yaml` → `sec-esp-provisioning-001` — programme entry (status: **planned**; authority: SOT)
- [`packages/base/api_encrypted.yaml`](../../packages/base/api_encrypted.yaml), [`packages/base/ota.yaml`](../../packages/base/ota.yaml), [`packages/base/logging.yaml`](../../packages/base/logging.yaml), [`packages/base/wifi.yaml`](../../packages/base/wifi.yaml) — current credential surfaces
- [`scripts/apply_release_secret_posture.py`](../../scripts/apply_release_secret_posture.py), [`scripts/check_firmware_default_credentials.py`](../../scripts/check_firmware_default_credentials.py) — release posture strip + deny-list artifact gate
- [`config/webflash-builds.json`](../../config/webflash-builds.json) — declaration-driven release matrix (ESP-007)
- [`secrets.example.yaml`](../../secrets.example.yaml) — self-build secret template

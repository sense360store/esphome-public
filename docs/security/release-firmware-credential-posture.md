# Release firmware credential posture — SEC-ESP-BUILD-GATES-001

- **Audit basis:** [`SECURITY-AUDIT-2026-06.md`](SECURITY-AUDIT-2026-06.md) finding **H1** (fixed, public credentials compiled into every released binary) and the **forward half of H2** (historical fallback-AP literals burned in public git history).
- **Scope:** every binary produced by the release pipeline ([`.github/workflows/firmware-build-release.yml`](../../.github/workflows/firmware-build-release.yml)) on every channel — stable, preview, and experimental. Self-builds from source are unaffected.
- **Status:** active. Enforced by two committed, PR-tested scripts (see *Enforcement* below).

## What changed

Release builds used to provision a fixed `secrets.yaml` whose values compiled
identically into every published binary: the placeholder API encryption key,
a shared OTA password, a shared web username/password, and a shared
fallback-AP password. All five values were world-readable in the workflow
file, so one public-repo read controlled every device still on defaults —
including OTA overwrite (persistent compromise) and any mains-switching
loads. That is finding H1.

A prebuilt `.bin` cannot carry per-device secrets, and **no first-boot flow
exists in this tree that could set them on the user's own install** — the
only provisioning surface is the WiFi captive portal, and Improv-style
flows (not present here) set WiFi only, not the API/OTA/web/fallback
secrets. Until a real provisioning flow lands (queue item
`SEC-ESP-PROVISIONING-001` in [`UPCOMING_PR.md`](../../UPCOMING_PR.md)),
released firmware therefore ships **unprovisioned instead of falsely
secured**.

## Fresh-flash auth posture (what a just-flashed device actually is)

A device freshly flashed with a released binary has:

| Surface | Posture | Previous posture |
|---|---|---|
| ESPHome native API (tcp/6053) | **Unencrypted, no key configured.** Home Assistant adopts it without a key and shows it as unencrypted. | "Encrypted" with a publicly known placeholder key. |
| OTA (esphome platform) | **Unauthenticated.** | "Protected" by a publicly known shared password. |
| Web UI (:80) | **No authentication.** | "Protected" by publicly known shared credentials. |
| Fallback/setup AP + captive portal | **Open hotspot** (SSID from `fallback_ssid`). | "Protected" by a publicly known shared password. |
| Setup-network join | Unchanged — joins the intentionally-public setup network (see below). | Same. |

Attacker capability on the local network is **unchanged** — every removed
credential was already public, so both postures amount to "anyone on the
LAN / in RF range can control the device". What changed is honesty and
blast radius: the firmware no longer asserts security it does not have, and
there is no longer a shared credential class whose single public value
"unlocks" the entire installed fleet, nor any false assurance that the
native API is encrypted. Devices on defaults should be treated as
unprotected on the local network until provisioned or re-flashed from a
self-build — exactly as they should have been treated before.

**Users who want real authentication today must self-build:** copy
[`secrets.example.yaml`](../../secrets.example.yaml) to `secrets.yaml` with
unique strong values and compile the same product YAML. The committed
packages keep their `!secret` references precisely so the self-build path
produces fully secured firmware.

## First-boot steps (released binary)

1. Flash via WebFlash (or `esptool`).
2. Either create a hotspot named after the setup network (below) for the
   device to join, or wait for the device's open fallback AP and use the
   captive portal to enter your real WiFi credentials.
3. Adopt the device in Home Assistant. The API is unencrypted; treat the
   device as LAN-trusted only.
4. For an encrypted API, OTA password, web auth, or a protected fallback
   AP: self-build with your own `secrets.yaml` and flash that binary.

## Intentionally-public setup-network credentials

Released binaries deliberately keep trying to join the fixed setup network
`Sense360_Setup` / `sense360setup` (the `wifi_ssid` / `wifi_password`
secrets), so a user can bring a fresh device online by creating a hotspot
with that name. These two values are **setup-only UX, documented as
public**:

- they are the name/password of a network the *user temporarily creates*,
  not credentials to anything the user owns persistently;
- knowing them grants **no control over the device's API / OTA / web
  surfaces** (those postures are listed above);
- residual risk: a nearby attacker can host a network with this name and
  attract an unprovisioned device (or a provisioned one whose primary
  network is down) onto their LAN. That is inherent to any fixed
  setup-network UX and is unchanged from the previous posture; the
  mitigation is the provisioning follow-up, not a secret SSID.

For this reason **only these two values** are excluded from the release
gate's denylist. The four device-control credential classes —
`api_encryption_key`, `ota_password`, web auth, `fallback_ap_password` —
are never excluded.

## Enforcement

Two committed scripts, both pinned by unit tests that run on every push/PR
(`validate.yml`) and in the full pytest suite:

1. **Posture patch — [`scripts/apply_release_secret_posture.py`](../../scripts/apply_release_secret_posture.py)**
   (test: [`tests/test_apply_release_secret_posture.py`](../../tests/test_apply_release_secret_posture.py)).
   Runs in the release build job only, before compile. Rewrites the four
   `packages/base/` files in the workspace (never committed) to remove
   `api.encryption`, the OTA password, the `web_server` auth block, and the
   fallback-AP password. Exact one-shot transforms; **fails closed** if a
   base package no longer has the committed shape. The release lane's
   `secrets.yaml` now contains only the two setup-network values, so any
   surviving `!secret` reference to another key fails the ESPHome compile
   instead of baking a value.

2. **Artifact gate — [`scripts/check_firmware_default_credentials.py`](../../scripts/check_firmware_default_credentials.py)**
   (test: [`tests/test_check_firmware_default_credentials.py`](../../tests/test_check_firmware_default_credentials.py)).
   The permanent backstop, independent of how build secrets are sourced. It
   scans every produced `.bin` — once per product after compile, and again
   over the full downloaded artifact set in the release job before anything
   is attached to the GitHub Release — for a denylist of known default /
   placeholder / burned credential byte-strings, and fails the release
   naming the artifact and the credential class. The denylist covers, by
   credential class: the placeholder `api_encryption_key` (as the base64
   literal **and** as its decoded 32-byte key material), the shipped and
   CI-lane `ota_password` defaults, the shipped and CI-lane `web_password`
   defaults, the shipped and CI-lane `fallback_ap_password` defaults plus
   the two **burned historical fallback-AP literals from audit H2**, and
   the CI-lane `wifi_ssid` / `wifi_password` test values. It fails closed
   (non-zero) when there is nothing to scan.

H2's history dimension — the burned literals remaining readable in public
git history, and rotation for already-shipped units — is **not** addressed
by this gate and stays open in the audit document.

## Non-claims

This posture change is a security-honesty fix only. It makes released
devices no harder to attack on the local network than they already were; it
claims no hardware, bench, compliance, or safety proof; and it does not
implement per-device provisioning — that is `SEC-ESP-PROVISIONING-001`.

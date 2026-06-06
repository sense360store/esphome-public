# Security Audit — esphome-public

Audit date: 2026-06-06
Scope: full repository (ESPHome YAML packages/products, Python build/release
scripts, GitHub Actions that compile and publish firmware `.bin` artifacts and
checksums, secrets handling, pre-commit/CI config).
Method: manual source review. No runtime/penetration testing was performed and
no hardware was exercised.

## Overall assessment

The repository shows **strong CI and supply-chain discipline**: GitHub Actions
are pinned to commit SHAs, no `pull_request_target` is used, workflows default
to `contents: read` with write scope only in the release job, Python uses
`yaml.safe_load` and list-form `subprocess` (no `shell=True`), and there are no
`eval`/`exec` or `verify=False` network calls. The real `secrets.yaml` is
gitignored and a pre-commit guard backs it up.

The findings are mostly **operational secret hygiene** rather than systemic
vulnerabilities. The two worth fixing are the **predictable fallback-AP
passwords baked into firmware** and a **gap in the tracked-secrets guard**.

| # | Severity | Area | Status |
|---|----------|------|--------|
| 1 | Medium-High | Predictable fallback-AP passwords hardcoded as substitution defaults | Open |
| 2 | Medium | `products/secrets.yaml` is tracked and the secret guard only checks the root `secrets.yaml` | Open |
| 3 | Medium | Release checksums are unsigned (no GPG/cosign) | Open |
| 4 | Low | `api_encryption_key` placeholder has no "reject default before flashing" guard | Open |
| 5 | Low | `manifest.json` is not JSON-validated before upload | Open |
| 6 | Low | `check-yaml --unsafe` in pre-commit | Accepted (ESPHome requirement) |

---

## 1. Medium-High — Predictable fallback-AP passwords hardcoded in firmware

**Where:**
- `packages/base/wifi.yaml:4` — `fallback_ap_password: "Sense360Fallback"` (substitution default), consumed at `packages/base/wifi.yaml:16` (`ap: password: "${fallback_ap_password}"`).
- `products/sense360-poe.yaml:52` — `fallback_ap_password: "sense360poe"` (overrides the default with another hardcoded literal).

**Issue:** Main WiFi correctly uses `!secret wifi_ssid` / `!secret
wifi_password`, but the **fallback access-point** password is a plaintext
literal in committed YAML, so it is compiled into the shipped firmware. The
fallback AP plus `captive_portal` activates whenever the device cannot join
WiFi (first boot, network change, outage). An attacker within RF range who
reads this public repo knows the password, can join the AP, and reach the
captive portal to reconfigure the device or harvest the WiFi credentials the
owner enters. The password is identical across all units of a product, so it is
not a per-device secret.

**Path to fix:**
1. Replace the literals with a secret reference, mirroring the WiFi block:
   ```yaml
   # packages/base/wifi.yaml
   ap:
     ssid: "${fallback_ssid}"
     password: !secret fallback_ap_password
   ```
   and remove the hardcoded override in `products/sense360-poe.yaml:52`.
2. Add `fallback_ap_password` to `secrets.example.yaml` (already present there)
   with guidance to generate a unique, strong value per build.
3. Optionally add a build-time check that rejects the known literals
   (`Sense360Fallback`, `sense360poe`) so they cannot ship by accident.

---

## 2. Medium — `products/secrets.yaml` is tracked and bypasses the secret guard

**Where:** `products/secrets.yaml` (tracked); guard at `scripts/check-no-tracked-secrets.py`.

**Issue:** A file literally named `secrets.yaml` is committed under `products/`.
Today it contains only placeholders, but two facts make it a footgun:
- The guard `scripts/check-no-tracked-secrets.py` only checks the **root**
  path: `git ls-files --error-unmatch secrets.yaml`. It does **not** catch
  `products/secrets.yaml`.
- Because the file is already tracked, `.gitignore`'s `secrets.yaml` rule does
  not protect it (`git check-ignore products/secrets.yaml` returns nothing —
  it is tracked). ESPHome resolves `!secret` from a `secrets.yaml` adjacent to
  the config, so a developer is naturally tempted to put **real** credentials
  here, and a subsequent `git add` would silently commit them.

**Path to fix:**
1. Rename the tracked file to a template, e.g. `products/secrets.example.yaml`
   (or delete it and rely on the root `secrets.example.yaml`), and `git rm`
   `products/secrets.yaml`.
2. Broaden the guard to catch any tracked `secrets.yaml` at any depth:
   ```python
   tracked = subprocess.run(
       ["git", "ls-files", "secrets.yaml", "**/secrets.yaml"],
       capture_output=True, text=True).stdout.split()
   if tracked:
       sys.exit("ERROR: tracked secrets.yaml found: " + ", ".join(tracked))
   ```
3. Confirm `.gitignore` ignores `secrets.yaml` at every level (an unanchored
   `secrets.yaml` pattern matches nested paths only for *untracked* files, so
   step 1 is what actually closes the hole).

---

## 3. Medium — Release checksums are not signed

**Where:** `.github/workflows/firmware-build-release.yml` (the step that produces `checksums-sha256.txt` / `checksums-md5.txt` and uploads release assets).

**Issue:** Firmware integrity is published as plaintext SHA-256/MD5 checksum
files with no signature. A party who can alter a release asset can also rewrite
the checksum file, so the checksums prove integrity against accidental
corruption but not authenticity against tampering. (MD5 additionally should not
be relied on for integrity.) Downstream, WebFlash verifies the `.bin` against
this checksum file, so the trust anchor is the release, not a key.

**Path to fix:**
- Sign `checksums-sha256.txt` in the release job and publish the signature +
  public key. GPG (`gpg --armor --detach-sign`) or, preferably, keyless
  Sigstore `cosign sign-blob` with the workflow OIDC identity.
- Keep the signing key in GitHub Actions secrets (or use cosign keyless so
  there is no long-lived key), and document verification for consumers.
- Drop MD5, or clearly label it non-security.

---

## 4. Low — No guard against shipping the placeholder `api_encryption_key`

**Where:** `secrets.example.yaml` (`api_encryption_key: "aaaa…="` placeholder) and CI-generated build secrets in the workflows.

**Issue:** The example file is correctly an obvious placeholder, but nothing
prevents a real build from compiling with the all-`a` key or other example
values, which would leave the API encryption effectively public.

**Path to fix:** add a pre-build validation step that fails if
`api_encryption_key` matches the known placeholder (or any of the CI test
literals) when building a **release/production** artifact, while still allowing
them for `compile-only` / preview validation. Document per-device key
regeneration in `README.md`.

---

## 5. Low — Generated `manifest.json` is not validated before upload

**Where:** `.github/workflows/firmware-build-release.yml` (the heredoc that writes `all-firmware/manifest.json` from shell variables).

**Issue:** `manifest.json` is assembled via shell interpolation and uploaded
without a JSON parse check. `version`/`channel` are validated upstream by
`derive_release_version_channel.py`, but a future field could produce invalid
JSON that breaks downstream consumers silently.

**Path to fix:** add a validation gate right after generation:
```bash
python3 -m json.tool all-firmware/manifest.json > /dev/null
```

---

## 6. Low — `check-yaml --unsafe` in pre-commit (accepted)

**Where:** `.pre-commit-config.yaml` (`check-yaml` with `args: ['--unsafe']`).

**Assessment:** `--unsafe` is required because ESPHome YAML uses custom tags
that the safe loader rejects; it relaxes pre-commit YAML *linting*, not runtime
parsing. Acceptable, but add a short comment explaining why so future readers
do not "fix" it into a false sense of safety or, worse, mirror `--unsafe` into
real config-loading code.

---

## Note on a candidate finding that did NOT hold up

The CI workflows create a throwaway `secrets.yaml` via
`cat > secrets.yaml << 'EOF' … EOF`. This redirects into the file and does
**not** echo the credentials to the build log, and the values are
disposable test credentials, so this is not a leak. Keep these literals
strictly test-only and never reuse them on real devices.

## Verified-good (no action needed)

- All third-party GitHub Actions are pinned to commit SHAs.
- No `pull_request_target`; release/publish run on `release` / `workflow_dispatch`.
- Least-privilege `permissions:` (top-level `contents: read`; write only in the
  release job).
- Python scripts use `yaml.safe_load`, list-form `subprocess` (no `shell=True`),
  no `eval`/`exec`, no `requests(..., verify=False)`.
- The real `secrets.yaml` is gitignored; `!secret` is used for WiFi, API, OTA,
  web-server, and MQTT credentials.
- No risky ESPHome components found (no untrusted `shell_command` / `http_request`
  / `exec`).

## Suggested fix order

1. (#1) Move fallback-AP passwords to `!secret`; drop the product override.
2. (#2) Untrack `products/secrets.yaml` and broaden the secret guard.
3. (#3) Sign release checksums (cosign keyless preferred).
4. (#4, #5) Add placeholder-key and JSON-validation build gates.
5. (#6) Comment the `--unsafe` rationale.

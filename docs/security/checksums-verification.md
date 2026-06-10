# Verifying the signed release checksums

- **Owner id:** `SEC-ESP-CHECKSUM-SIGNING-001`
- **Date:** 2026-06-10
- **Closes:** [`SECURITY-AUDIT-2026-06.md`](SECURITY-AUDIT-2026-06.md) finding
  **M1** (release checksums unsigned — the June 10 narrowing class) /
  internal [`security.md`](../../security.md) §3.

Every GitHub Release cut by
[`.github/workflows/firmware-build-release.yml`](../../.github/workflows/firmware-build-release.yml)
publishes, alongside the firmware `.bin` assets:

| Asset | What it is |
|---|---|
| `checksums-sha256.txt` | SHA-256 checksums of every published `.bin` (the canonical integrity record) |
| `checksums-sha256.txt.sig` | Keyless cosign signature over `checksums-sha256.txt` (base64-encoded) |
| `checksums-sha256.txt.pem` | The short-lived Fulcio signing certificate (base64-encoded PEM) |

The signature is produced **keyless** with [Sigstore
cosign](https://docs.sigstore.dev/): the release job exchanges its
job-scoped GitHub OIDC token for a short-lived certificate from Fulcio
that is cryptographically bound to **this repository and this workflow
file at the release tag**, and the signature is recorded in the public
Rekor transparency log. There is no long-lived signing key to leak or
rotate. Verification therefore proves **who** signed (this repo's release
workflow, on that tag) — not merely that *something* produced a valid
signature.

## Verification recipe

Prerequisites: [cosign](https://docs.sigstore.dev/cosign/system_config/installation/)
v2.x (the workflow pins v2.6.3) and network access to the Sigstore
infrastructure (`rekor.sigstore.dev` and the TUF trust-root CDN) — with
only the `.sig` + `.pem` published, cosign looks the signature's
transparency-log entry up online.

Download `checksums-sha256.txt`, `checksums-sha256.txt.sig`, and
`checksums-sha256.txt.pem` from the release, then run (substituting the
release tag you downloaded from):

```bash
TAG="v1.0.4"   # the release tag the assets came from

cosign verify-blob \
  --certificate checksums-sha256.txt.pem \
  --signature checksums-sha256.txt.sig \
  --certificate-identity "https://github.com/sense360store/esphome-public/.github/workflows/firmware-build-release.yml@refs/tags/${TAG}" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  checksums-sha256.txt
```

Expected output: `Verified OK`.

Then verify the firmware binaries against the now-authenticated
checksums file (run in the directory holding the downloaded `.bin`
files; the header lines are comments and are ignored):

```bash
sha256sum -c checksums-sha256.txt
```

### What the two pinned values mean

- `--certificate-identity` pins the Fulcio certificate's SAN to **this
  repo + this workflow file + the release tag ref**:
  `https://github.com/sense360store/esphome-public/.github/workflows/firmware-build-release.yml@refs/tags/<TAG>`.
  This is GitHub's `job_workflow_ref` OIDC claim as embedded by Fulcio —
  only a run of `firmware-build-release.yml` inside
  `sense360store/esphome-public` on that tag can obtain a certificate
  with this identity. A signature made by any other repo, workflow, user
  account, or local machine fails this check even if it is otherwise a
  valid Sigstore signature.
- `--certificate-oidc-issuer` pins the identity provider to GitHub
  Actions (`https://token.actions.githubusercontent.com`), so a
  same-looking identity asserted by a different OIDC provider is
  rejected.

If you do not want to pin the exact tag (e.g. scripting across
releases), pin everything except the tag with the regexp form — keep the
anchor on the tags namespace:

```bash
  --certificate-identity-regexp '^https://github\.com/sense360store/esphome-public/\.github/workflows/firmware-build-release\.yml@refs/tags/' \
```

### Notes

- The `.sig` and `.pem` files are base64-encoded, exactly as
  `cosign sign-blob` emits them; `cosign verify-blob` consumes them
  as published. To inspect the certificate manually:
  `base64 -d checksums-sha256.txt.pem | openssl x509 -text -noout`.
- The release job runs this exact `verify-blob` invocation as a
  self-check immediately after signing; a release cannot publish with a
  signature that does not verify against this identity.
- `checksums-md5.txt` is published for legacy compatibility only. It is
  **not** signed and must not be relied on for integrity or authenticity.

## What this does and does not prove

**Proves:** the `checksums-sha256.txt` you downloaded is byte-identical
to the one produced by this repo's release workflow on that tag, and any
`.bin` matching its checksum is the byte-identical artifact that workflow
uploaded. If an attacker replaces a `.bin` and rewrites
`checksums-sha256.txt` to match (the M1 / June 10 class), the signature
no longer verifies; if they replace all three files with a signature of
their own, the certificate identity no longer matches this repo +
workflow; if they delete the `.sig`/`.pem`, the absence is the tamper
signal — **treat a release whose checksums file is missing its signature
or fails verification as compromised, and do not flash from it.**

**Does not prove:**

- **Platform-level asset immutability.** GitHub release assets remain
  mutable to credentialed writers until immutable releases are enabled —
  that platform-side complement is owner checklist **Item 7, line 9** in
  [`SECURITY-AUDIT-2026-06.md`](SECURITY-AUDIT-2026-06.md) (enable
  immutable releases + artifact attestations). Signing makes a swap
  *detectable*; immutability makes it *impossible*.
- **Firmware signing.** This repo still publishes **unsigned** `.bin`
  artifacts and is not the production firmware-signing authority — that
  is downstream [`sense360store/WebFlash`](https://github.com/sense360store/WebFlash),
  which additionally pins per-source `expected_sha256` values at import
  time. This signature authenticates the checksums *file's provenance*.
- **Workflow compromise.** A signature from a genuinely compromised run
  of this workflow would still verify; the Rekor transparency log makes
  every signing event publicly auditable after the fact.

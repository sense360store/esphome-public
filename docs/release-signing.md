# Release checksum signing (SEC-ESP-CHECKSUM-SIGNING-001)

security.md finding #3: firmware integrity used to be published only as
plaintext SHA-256/MD5 checksum files. Those prove integrity against accidental
corruption but **not authenticity against tampering** — a party who can rewrite
a release asset can rewrite the checksum file too.

The release workflow (`.github/workflows/firmware-build-release.yml`, the
`release` job) now signs `checksums-sha256.txt` with **keyless Sigstore
cosign** using the workflow's GitHub OIDC identity. There is no long-lived
signing key: cosign mints a short-lived certificate from Fulcio bound to the
workflow identity and records the signature in the Rekor transparency log.

## Release assets

| Asset | Purpose |
|---|---|
| `checksums-sha256.txt` | SHA-256 of every `.bin` (the signed integrity anchor) |
| `checksums-sha256.txt.cosign.bundle` | self-contained cosign bundle (signature + certificate + Rekor proof) |
| `checksums-sha256.txt.sig` | detached base64 signature |
| `checksums-sha256.txt.pem` | signing certificate (Fulcio) |
| `checksums-md5.txt` | **NON-SECURITY**, legacy compatibility only — MD5 is broken; do not use it for integrity or authenticity |

## Verifying a release as a consumer

Install cosign (<https://docs.sigstore.dev/cosign/system_config/installation/>),
download `checksums-sha256.txt`, the firmware `.bin`, and the signing material
from the GitHub release, then:

**1. Verify the checksum file is authentic (signed by this repo's workflow).**

Using the bundle:

```bash
cosign verify-blob \
  --bundle checksums-sha256.txt.cosign.bundle \
  --certificate-identity-regexp '^https://github\.com/sense360store/esphome-public/\.github/workflows/firmware-build-release\.yml@' \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
  checksums-sha256.txt
```

Or using the detached signature + certificate:

```bash
cosign verify-blob \
  --signature checksums-sha256.txt.sig \
  --certificate checksums-sha256.txt.pem \
  --certificate-identity-regexp '^https://github\.com/sense360store/esphome-public/\.github/workflows/firmware-build-release\.yml@' \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
  checksums-sha256.txt
```

`cosign verify-blob` prints `Verified OK` only when the signature is valid
**and** the signing certificate's identity matches the workflow above and was
issued by GitHub Actions OIDC. The `--certificate-identity-regexp` matches the
workflow path across release refs/tags.

**2. Verify the firmware binary against the now-authenticated checksums.**

```bash
sha256sum -c checksums-sha256.txt --ignore-missing
```

A binary is trustworthy only if **both** steps pass: step 1 authenticates the
checksum file, step 2 ties the `.bin` to it. Do not rely on `checksums-md5.txt`.

## Scope

This documents the **producer-side** signing and the generic consumer
verification flow. Wiring this signature into the downstream WebFlash installer
is a separate cross-repo change and is intentionally not part of this work.

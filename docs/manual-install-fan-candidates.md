# Manual Install — Fan Firmware Candidates (FanRelay / FanPWM / FanDAC)

Operator / advanced-user handoff for **manually** installing the three
no-WebFlash fan firmware candidates. This is a manual-install-only path. It
publishes **no** release artifact and enables **no** WebFlash exposure.

> **This is not the WebFlash path and not a release.** WebFlash at
> [mysense360.com](https://mysense360.com) remains the recommended production
> path for official, signed firmware. The product YAMLs below are **manual /
> no-WebFlash firmware candidates** only — see
> [What "candidate" means](#what-candidate-means-and-what-it-does-not) before
> installing or planning a build.

---

## What "candidate" means (and what it does not)

`MANUAL-FIRMWARE-CANDIDATE-001` (PR #617) marked FanRelay, FanPWM, and FanDAC
as **manual / no-WebFlash firmware candidates**. A product YAML is a candidate
when, and only when, all three of the following already hold:

- **top-level product YAML exists** under `products/`;
- **structurally validated** — its per-product readiness suite passes;
- **full-compile validated** — its registered compile-only target carries
  `compile_validation_status: validated-full-compile`.

"Candidate" therefore means exactly: *this YAML exists, validates, compiles,
and can be installed manually.* Nothing more.

Candidate does **NOT** mean any of the following, and this handoff claims none
of them:

- **not** WebFlash exposure or WebFlash import;
- **not** a release artifact (no `.bin`, no checksum, no tag, no release proof);
- **not** hardware-stable / bench / harness proof;
- **not** compliance / mains-safety / competent-person approval;
- **not** RPM support for FanPWM;
- **not** Cloudlift-ready for FanDAC;
- **not** kit / default / recommended readiness for FanRelay.

Canonical definition, per-family evidence, and provenance live in the
references below.

---

## Candidate product YAMLs

| Family | Product YAML | Product-specific caveat |
| --- | --- | --- |
| **FanRelay / S360-310** | [`products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml) | mains / safety / competent-person sign-off still required; not kit / default / recommended |
| **FanPWM / S360-311** | [`products/sense360-ceiling-poe-fanpwm.yaml`](../products/sense360-ceiling-poe-fanpwm.yaml) | no RPM / TachIO claim; measured current / thermal still required |
| **FanDAC / S360-312** | [`products/sense360-ceiling-poe-fandac.yaml`](../products/sense360-ceiling-poe-fandac.yaml) | not Cloudlift-ready; J3 / Cloudlift evidence still required; no compliance claim |

---

## Pinning the candidate (`ref:`)

There is **no release tag** for these candidates. Do **not** pin to `v1.0.0` —
that is the Release-One stable product, which does **not** include any fan
driver. Do **not** track `main`, which moves.

Pin `ref:` to a specific reviewed commit SHA. The examples below use the
candidate-status commit `cca77c22b835e7735eaa40e322464f5aa1af8c5d` (PR #617);
replace it with whatever reviewed commit you are installing from.

---

## Secrets

All three candidates inherit the standard base stack, so they need the same
`secrets.yaml` as any other manual install. Standalone ESPHome users copy the
shipped example and edit it locally:

```bash
cp secrets.example.yaml secrets.yaml
```

`secrets.yaml` is gitignored — never commit it. See the
[Installation Guide](installation.md#step-2-configure-secrets) for the full
list of required keys (WiFi, API key, OTA, and MQTT for VentIQ-bearing
products such as FanRelay).

---

## FanRelay / S360-310

> **Mains / safety / sign-off still required.** FanRelay drives a mains-side
> relay (K1). It is **not** kit / default / recommended, **not** compliance- or
> mains-safety-approved, and **not** hardware-stable. Installation requires a
> competent person; the candidate status does not waive any safety,
> installation, or competent-person sign-off requirement.

### Remote-package include

```yaml
substitutions:
  device_name: sense360-bath-relay  # Change this
  friendly_name: "Bathroom Sense360 Relay"  # Change this

esphome:
  name: ${device_name}
  friendly_name: ${friendly_name}
  min_version: 2025.10.0

packages:
  sense360_firmware:
    url: https://github.com/sense360store/esphome-public
    ref: cca77c22b835e7735eaa40e322464f5aa1af8c5d  # reviewed commit; no release tag — never 'main', never v1.0.0
    files:
      - products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml
    refresh: 1d

# wifi:, api:, and ota: are wired up by the package via secrets.yaml.
# Do NOT redeclare them here.
```

### Local ESPHome commands

```bash
esphome config products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml
esphome compile products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml
esphome upload products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml
```

---

## FanPWM / S360-311

> **No RPM / TachIO claim.** The PWM-drive-only package wires no
> `pulse_counter`; `TachIO` / `GPIO16` is reserved. There is no per-fan or
> aggregate RPM sensor. Measured per-channel and aggregate current, MT3608
> ceiling / inrush, and thermal characterisation are still required before any
> WebFlash / release / hardware-stable claim.

### Remote-package include

```yaml
substitutions:
  device_name: sense360-pwm-fan  # Change this
  friendly_name: "PWM Fan Sense360"  # Change this

esphome:
  name: ${device_name}
  friendly_name: ${friendly_name}
  min_version: 2025.10.0

packages:
  sense360_firmware:
    url: https://github.com/sense360store/esphome-public
    ref: cca77c22b835e7735eaa40e322464f5aa1af8c5d  # reviewed commit; no release tag — never 'main', never v1.0.0
    files:
      - products/sense360-ceiling-poe-fanpwm.yaml
    refresh: 1d

# wifi:, api:, and ota: are wired up by the package via secrets.yaml.
# Do NOT redeclare them here.
```

### Local ESPHome commands

```bash
esphome config products/sense360-ceiling-poe-fanpwm.yaml
esphome compile products/sense360-ceiling-poe-fanpwm.yaml
esphome upload products/sense360-ceiling-poe-fanpwm.yaml
```

---

## FanDAC / S360-312

> **Not Cloudlift-ready; no compliance claim.** The 0-10V (GP8403) candidate is
> **not** Cloudlift-ready. The J2 / J3 board-level pin-1 identity, the harness
> conductor-by-conductor trace to the Cloudlift S12 fan input, and the J3
> `out0` / `out1` silkscreen transposition remain unresolved. J3 / Cloudlift
> evidence is still required, and no compliance approval is claimed.

### Remote-package include

```yaml
substitutions:
  device_name: sense360-duct-fan  # Change this
  friendly_name: "Duct Fan Sense360"  # Change this

esphome:
  name: ${device_name}
  friendly_name: ${friendly_name}
  min_version: 2025.10.0

packages:
  sense360_firmware:
    url: https://github.com/sense360store/esphome-public
    ref: cca77c22b835e7735eaa40e322464f5aa1af8c5d  # reviewed commit; no release tag — never 'main', never v1.0.0
    files:
      - products/sense360-ceiling-poe-fandac.yaml
    refresh: 1d

# wifi:, api:, and ota: are wired up by the package via secrets.yaml.
# Do NOT redeclare them here.
```

### Local ESPHome commands

```bash
esphome config products/sense360-ceiling-poe-fandac.yaml
esphome compile products/sense360-ceiling-poe-fandac.yaml
esphome upload products/sense360-ceiling-poe-fandac.yaml
```

---

## References

- [Product Readiness Matrix §MANUAL-FIRMWARE-CANDIDATE-001](product-readiness-matrix.md#manual-firmware-candidate-001--fanrelay--fanpwm--fandac-marked-as-manual--no-webflash-firmware-candidates-2026-05-27)
  — canonical candidate definition, per-family evidence table, and honest
  provenance.
- [Blocker Burndown §3F](blocker-burndown.md#3f-fanrelay--fanpwm--fandac-marked-as-manual--no-webflash-firmware-candidates-manual-firmware-candidate-001-2026-05-27)
  — cross-lane view of the candidate rollup and what it does / does not prove.
- [Manual / Custom User Walkthrough](manual-user-walkthrough.md) — QA test plan
  template for the manual ESPHome path.
- [Installation Guide](installation.md) — full step-by-step manual setup,
  secrets, and USB / OTA flashing.

# Manual / Custom User Walkthrough

A QA checklist for validating the manual ESPHome path in this repo with a real
tester. The goal is to find places where the docs are technically correct but
confusing — not to verify code.

> **This is not the WebFlash path.** WebFlash at
> [mysense360.com](https://mysense360.com) is the recommended production path
> for official, signed firmware. This walkthrough only exercises the
> manual/custom YAML path that lives in this repo.

---

## Who This Walkthrough Is For

The intended tester is:

- Comfortable with Home Assistant (installing add-ons, editing YAML in the HA UI)
- Comfortable copying files and running a shell command
- **Not** previously familiar with this repository
- **Not** previously familiar with Sense360 internal module names
  (RoomIQ, VentIQ, AirIQ, FanTRIAC, etc.)

The tester does **not** need to understand:

- WebFlash internals
- CI workflows or build pipelines
- Firmware signing
- WebFlash manifests or release automation

If you are deeply familiar with this repo already, you are not the right tester
— ask someone else to run through this and record their answers.

---

## What You Need

- A computer with a terminal
- Git installed
- A clone of this repo (manual download is fine too)
- Optional: ESPHome 2025.10 or newer installed locally
  (steps 5 and 6 are skipped without it)
- Optional: a Sense360 device on hand

You do **not** need to flash hardware to complete this walkthrough.

Estimated time: 30–60 minutes.

---

## How To Use This Document

Work top to bottom. After each step, write your answers in the
[Findings Template](#findings-template) at the bottom of this document. If
something confused you, note it — that is the point of the walkthrough.

There are no wrong answers; "I could not find this" is the most useful kind of
finding.

---

## Step 1 — Start at the README

Open [`README.md`](../README.md) at the repo root. Read the top of the file
through to the "Which Path Should I Use?" table.

**Answer in your findings:**

- Do you understand that **WebFlash is the recommended path** for normal
  production installs?
- Do you understand that **this repo is for manual / custom ESPHome users**,
  not the average buyer?
- Can you find the link to the Release-One product YAML from the README?
- Can you find the section that explains how to set this up manually
  ("Quick Start (Custom / Manual Flash)")?

If any of those answers is "no" or "I had to guess", capture it.

---

## Step 2 — Identify the Release-One Config

The Release-One shipping configuration is:

```text
Ceiling-POE-VentIQ-FanTRIAC-RoomIQ
```

The matching product YAML in this repo is:

```text
products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml
```

Open that file directly:
[`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml).

The expected firmware artifact name (when CI publishes it) is:

```text
Sense360-Ceiling-POE-VentIQ-FanTRIAC-RoomIQ-v1.0.0-stable.bin
```

**Answer in your findings:**

- Could you find the Release-One product YAML from the README without
  searching the file tree?
- Looking only at the YAML's top comment block, can you tell what hardware it
  is for?
- Was the link between the **config string**, the **product YAML filename**,
  and the **published `.bin` name** clear?

---

## Step 3 — Understand the Hardware Requirements

The Release-One configuration assumes the following physical hardware:

- **Sense360 Core R4** (or newer ceiling-mount core board)
- **Sense360 PoE PSU** (IEEE 802.3af Power-over-Ethernet)
- **Sense360 VentIQ module** (bathroom-focused air quality)
- **Sense360 TRIAC fan board** (AC phase-cut fan dimming)
- **Sense360 RoomIQ module** (comfort + presence)

Reference: [`docs/release-one.md`](release-one.md) and the
[Sensor & Driver Modules](../README.md#sensor--driver-modules) section of the
README.

**Answer in your findings:**

- Could you tell whether your hardware matches this configuration? (If you
  don't have hardware, answer based on whether the docs make it possible to
  check.)
- Were **RoomIQ**, **VentIQ**, and **TRIAC** explained clearly enough that you
  understood what each one is for?
- Was the difference between **AirIQ** and **VentIQ** clear, including that
  they are mutually exclusive?
- Was it clear that **FanTRIAC is not interchangeable** with FanRelay,
  FanPWM, or FanDAC, and that flashing the wrong one is a bad idea?

---

## Step 4 — Set Up Local Secrets

Copy the example secrets file to a local `secrets.yaml`:

```bash
cp secrets.example.yaml secrets.yaml
```

The example file is at
[`secrets.example.yaml`](../secrets.example.yaml). Open both `secrets.example.yaml`
and your new `secrets.yaml` and look at them.

**Answer in your findings:**

- Was it clear that `secrets.yaml` is **local-only and must not be committed
  to git** (it is gitignored)?
- Did you notice that the `api_encryption_key` in the example is an
  obviously-fake placeholder (all `a` characters)?
- Did you understand that you need to **generate your own real key** before
  flashing a real device, and could you find at least one suggested way to
  do so (e.g. `esphome wizard`, `openssl rand -base64 32`)?

You do **not** need to fill in real WiFi credentials for this walkthrough —
the placeholders are fine for the validation step below.

---

## Step 5 — Validate the ESPHome Config

This step requires ESPHome installed locally. If you do not have ESPHome
installed, skip the command and answer the doc-finding question instead.

**With ESPHome installed**, from the repo root run:

```bash
esphome config products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml
```

This should print the rendered configuration and exit successfully. It does
**not** flash anything and does **not** require hardware.

**Without ESPHome installed**, find the install instructions in the repo:

- Try [`docs/installation.md`](installation.md)
- Try [`docs/development.md`](development.md)

**Answer in your findings:**

- If ESPHome is installed: did `esphome config …` succeed? If not, was the
  error understandable?
- If ESPHome is not installed: could you find the install instructions
  starting from the README, without searching the web?

---

## Step 6 — Optional Build

This step is optional. It compiles the firmware locally; it does **not** flash
hardware.

```bash
esphome compile products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml
```

This will take a few minutes and download toolchains the first time.

**Answer in your findings:**

- Could you tell where the compiled firmware output ended up on disk?
- Was it clear that this **local build is not the same as the official
  WebFlash production-signed binary**?
- Was it clear that **WebFlash signs firmware elsewhere** and this repo
  itself does not sign anything?

If any of those answers are "no", that is a finding.

---

## Step 7 — Customization Path

This repo splits configuration across several directories. From the repo root,
look at:

- [`products/`](../products/) — ready-to-use device configurations
  (start here)
- [`packages/`](../packages/) — base / hardware / expansions / features
  (the building blocks the products import)
- [`components/`](../components/) — C++ external components (advanced)
- [`include/`](../include/) — shared C++ headers (advanced)

Reference reading: the
[Configuration Approaches](../README.md#configuration-approaches) section of
the README.

**Answer in your findings:**

- Could you tell which of these directories are **safe for a normal user to
  customize** vs. which are **internals best left alone**?
- Could you tell the difference between a **product YAML** (in `products/`)
  and a **package YAML** (in `packages/`)? Could you describe it in your own
  words?
- If you wanted to change something small (e.g. the bathroom humidity
  threshold), would you know whether to edit the product file, a package
  file, or your own device YAML?

---

## Step 8 — Stop Conditions

The manual path is **not** the right path for everyone. Stop here and use
[WebFlash](https://mysense360.com) instead if any of the following are true:

- "I just want to install official Sense360 firmware."
- "I do not want to write or modify any YAML."
- "I am not familiar with ESPHome and don't want to learn it right now."
- "I am not sure which Sense360 modules I have."
- "I need production-signed firmware."

**Answer in your findings:**

- Was it clear from the README and from this walkthrough **when you should
  stop and switch to WebFlash**?
- Did you ever feel like you were being pushed down the manual path when you
  would have been better served by WebFlash?

---

## Reference Links

Existing docs in this repo that the walkthrough touches:

- [`README.md`](../README.md) — top-level overview, WebFlash vs. manual
- [`docs/installation.md`](installation.md) — step-by-step setup
- [`docs/development.md`](development.md) — dev environment, validation,
  pre-commit
- [`docs/release-one.md`](release-one.md) — Release-One configuration
- [`docs/webflash-contract.md`](webflash-contract.md) — WebFlash artifact
  naming and grammar
- [`docs/webflash-release-handoff.md`](webflash-release-handoff.md) — release
  flow and troubleshooting
- [`secrets.example.yaml`](../secrets.example.yaml) — local secrets template
- [`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml)
  — Release-One product YAML

---

## Findings Template

Copy this section into your tester report (or fill it in directly in a
working copy of this file — do not commit your filled-in copy back to the
repo).

```markdown
# Tester Findings — Manual / Custom User Walkthrough

## Tester profile

- Home Assistant experience:
- ESPHome experience:
- Hardware used:
- OS:
- Browser:
- Date:

## Tasks

| Task | Pass / Fail / Partial | Notes |
| --- | --- | --- |
| Understood WebFlash vs manual path |  |  |
| Found Release-One YAML |  |  |
| Understood hardware requirements |  |  |
| Set up secrets.yaml |  |  |
| Ran esphome config |  |  |
| Ran esphome compile |  |  |
| Understood output artifact |  |  |
| Understood when to use WebFlash instead |  |  |

## Confusing terms

- RoomIQ:
- VentIQ:
- AirIQ:
- FanTRIAC:
- WebFlash:
- ESPHome package:
- Product YAML:

## Blocking issues

1.
2.
3.

## Suggested fixes

1.
2.
3.
```

---

## Notes for Reviewers

This walkthrough is a test harness, not proof. After it lands, a real tester
must actually run through it and file concrete findings; only then do we know
whether the manual path is usable. The walkthrough does **not** assert that
the manual path is correct — it only gives someone a structured way to find
out.

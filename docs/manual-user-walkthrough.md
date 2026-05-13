# Manual / Custom ESPHome User Walkthrough

A QA checklist for validating the manual ESPHome path in this repo with a real
tester. The goal is to find places where the docs are technically correct but
confusing — not to verify code.

> **This is not the WebFlash path.** WebFlash at
> [mysense360.com](https://mysense360.com) is the recommended production path
> for official, signed firmware. This walkthrough only exercises the
> manual/custom YAML path that lives in this repo.

---

## Purpose

This document is the **test plan and findings template** that Sense360 uses to
validate whether a non-internal user can follow the manual / custom ESPHome
path end-to-end using only the docs in this repo.

It is **not**:

- A proof that the manual path works. The plan landing here only means a real
  tester now has somewhere to record what they found.
- A firmware test. It does not exercise sensor accuracy, regulatory behavior,
  or production WebFlash signing.
- A replacement for [WebFlash](https://mysense360.com). WebFlash remains the
  recommended path for the average user.

## Scope

| Item | Value |
| --- | --- |
| Target config | `Ceiling-POE-VentIQ-RoomIQ` |
| Target product YAML | [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml) |
| Target artifact | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` |
| Suggested ref / tag | `v1.0.0` (never `main` in production) |
| Minimum ESPHome | `2025.10.0` |
| Path under test | Manual / custom ESPHome YAML (this repo) |
| Path **not** under test | WebFlash signing, manifest, deploy, install UX |

The walkthrough covers reading the README, identifying the Release-One
product YAML, understanding hardware requirements, setting up local secrets,
running `esphome config` (and optionally `esphome compile`), and recognising
when to stop and switch to WebFlash instead.

---

## Who should use this path

The intended tester is:

- Comfortable with Home Assistant (installing add-ons, editing YAML in the HA UI).
- Comfortable copying files and running a shell command.
- **Not** previously familiar with this repository.
- **Not** previously familiar with Sense360 internal module names
  (RoomIQ, VentIQ, AirIQ, FanTRIAC, etc.).

If you are deeply familiar with this repo already, you are not the right tester
— ask someone else to run through this and record their answers.

## Who should not use this path

Stop here and use [WebFlash](https://mysense360.com) instead if any of the
following are true:

- "I just want to install official Sense360 firmware."
- "I do not want to write or modify any YAML."
- "I am not familiar with ESPHome and don't want to learn it right now."
- "I am not sure which Sense360 modules I have."
- "I need production-signed firmware."

The tester does **not** need to understand:

- WebFlash internals.
- CI workflows or build pipelines.
- Firmware signing.
- WebFlash manifests or release automation.

---

## Prerequisites

- A computer with a terminal.
- Git installed.
- A clone of this repo (manual download is fine too).
- Optional: ESPHome 2025.10 or newer installed locally
  (steps 5 and 6 are skipped without it).
- Optional: a Sense360 device on hand.

You do **not** need to flash hardware to complete this walkthrough.

Estimated time: 30–60 minutes.

---

## Test scenario

A tester who has never seen this repo before clones it at tag `v1.0.0`,
follows the README and this walkthrough top-to-bottom, and tries to reach the
point where they could compile (and optionally flash) the Release-One
`Ceiling-POE-VentIQ-RoomIQ` configuration.

Two stop points are acceptable:

1. **Read-only** — stop after `esphome config` succeeds. No build, no flash.
   This is the minimum bar for "manual path is discoverable".
2. **Optional build** — continue to `esphome compile` to produce a local,
   unsigned `.bin`. This is **not** the same as the signed WebFlash artifact.

A real hardware flash is **out of scope** for this template; if the tester
has hardware on hand, they may flash, but the pass/fail criteria below treat
that as a bonus.

---

## Step-by-step walkthrough

Work top to bottom. After each step, write your answers in the
[Issue log template](#issue-log-template) at the bottom of this document. If
something confused you, note it — that is the point of the walkthrough.

There are no wrong answers; "I could not find this" is the most useful kind of
finding.

### Step 1 — Start at the README

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

### Step 2 — Identify the Release-One Config

The Release-One shipping configuration is:

```text
Ceiling-POE-VentIQ-RoomIQ
```

The matching product YAML in this repo is:

```text
products/sense360-ceiling-poe-ventiq-roomiq.yaml
```

Open that file directly:
[`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml).

The expected firmware artifact name (when CI publishes it) is:

```text
Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin
```

#### What is in Release-One

- `Ceiling` mount, `POE` power, `VentIQ` air quality, `RoomIQ` room sensing.

#### What is NOT in Release-One — do not assume these are production-ready

- **Sense360 TRIAC / FanTRIAC is excluded** from production Release-One while
  HW-005 is open. The FanTRIAC product YAML
  ([`products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml))
  remains in the repo as a **blocked / reference file only**. It is **not**
  in the WebFlash build matrix, **not** shipped, and **not** signed. Do not
  flash it to real hardware expecting Sense360 production behaviour — the
  fan output is not validated. See
  [`release-one-hardware-audit.md#fantriac-mapping-resolution`](release-one-hardware-audit.md#fantriac-mapping-resolution).
- **Sense360 LED (ceiling LED ring) is excluded** from Release-One firmware.
  The WebFlash config string `Ceiling-POE-VentIQ-RoomIQ` has no `LED` slot,
  so the Release-One artifact does not bundle LED-ring driver behaviour.
  The package
  [`packages/hardware/led_ring_ceiling.yaml`](../packages/hardware/led_ring_ceiling.yaml)
  exists in the repo for custom builds, but it is **not** part of the
  production Release-One build matrix. Do not assume an LED ring will light
  up under stock Release-One firmware.
- **Legacy fan / mini / wall variants** still exist in `packages/expansions/`
  and `products/` for backwards compatibility, but they are **not**
  Release-One production targets. See the
  [Legacy Terminology](../README.md#legacy-terminology) section of the README.

**Answer in your findings:**

- Could you find the Release-One product YAML from the README without
  searching the file tree?
- Looking only at the YAML's top comment block, can you tell what hardware it
  is for?
- Was the link between the **config string**, the **product YAML filename**,
  and the **published `.bin` name** clear?
- Was the exclusion of FanTRIAC and LED from production Release-One clearly
  signalled, or did you have to deduce it from package filenames?

---

### Step 3 — Understand the Hardware Requirements

The Release-One configuration assumes the following physical hardware:

- **Sense360 Core R4** (or newer ceiling-mount core board).
- **Sense360 PoE PSU** (IEEE 802.3af Power-over-Ethernet).
- **Sense360 VentIQ module** (bathroom-focused air quality).
- **Sense360 RoomIQ module** (comfort + presence).

> The Sense360 TRIAC (`S360-320`, FanTRIAC) board is **not** part of
> production Release-One while HW-005 is open. If you have one on hand,
> production Release-One firmware will not drive it.

> The Sense360 ceiling LED ring is **not** included in the Release-One
> WebFlash artifact. If you have one on hand, stock Release-One firmware
> will not light it up.

Reference: [`docs/release-one.md`](release-one.md) and the
[Sensor & Driver Modules](../README.md#sensor--driver-modules) section of the
README.

**Answer in your findings:**

- Could you tell whether your hardware matches this configuration? (If you
  don't have hardware, answer based on whether the docs make it possible to
  check.)
- Were **RoomIQ** and **VentIQ** explained clearly enough that you
  understood what each one is for?
- Was the difference between **AirIQ** and **VentIQ** clear, including that
  they are mutually exclusive?
- Was it clear that **FanTRIAC is currently excluded** from production
  Release-One while HW-005 is open, and where to find the audit doc that
  explains why?
- Was it clear that **the LED ring is not in the Release-One firmware** even
  if the hardware is present?

---

### Step 4 — Set Up Local Secrets

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

### Step 5 — Validate the ESPHome Config

This step requires ESPHome installed locally. If you do not have ESPHome
installed, skip the command and answer the doc-finding question instead.

**With ESPHome installed**, from the repo root run:

```bash
esphome config products/sense360-ceiling-poe-ventiq-roomiq.yaml
```

This should print the rendered configuration and exit successfully. It does
**not** flash anything and does **not** require hardware.

**Without ESPHome installed**, find the install instructions in the repo:

- Try [`docs/installation.md`](installation.md).
- Try [`docs/development.md`](development.md).

**Answer in your findings:**

- If ESPHome is installed: did `esphome config …` succeed? If not, was the
  error understandable?
- If ESPHome is not installed: could you find the install instructions
  starting from the README, without searching the web?

---

### Step 6 — Optional Build

This step is optional. It compiles the firmware locally; it does **not** flash
hardware.

```bash
esphome compile products/sense360-ceiling-poe-ventiq-roomiq.yaml
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

### Step 7 — Customization Path

This repo splits configuration across several directories. From the repo root,
look at:

- [`products/`](../products/) — ready-to-use device configurations
  (start here).
- [`packages/`](../packages/) — base / hardware / expansions / features
  (the building blocks the products import).
- [`components/`](../components/) — C++ external components (advanced).
- [`include/`](../include/) — shared C++ headers (advanced).

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

### Step 8 — Stop Conditions

The manual path is **not** the right path for everyone. Stop here and use
[WebFlash](https://mysense360.com) instead if any of the conditions in
[Who should not use this path](#who-should-not-use-this-path) apply to you.

**Answer in your findings:**

- Was it clear from the README and from this walkthrough **when you should
  stop and switch to WebFlash**?
- Did you ever feel like you were being pushed down the manual path when you
  would have been better served by WebFlash?

---

## What the tester should verify

By the end of the walkthrough, the tester should be able to answer "yes" to
each of these without guessing:

- I found the README and the "Which Path Should I Use?" table.
- I understand that **WebFlash** is the production path and **this repo** is
  the manual / custom path.
- I found the Release-One product YAML
  (`products/sense360-ceiling-poe-ventiq-roomiq.yaml`) from the README.
- I understand which physical Sense360 modules Release-One assumes
  (Core R4, PoE PSU, VentIQ, RoomIQ).
- I understand that **FanTRIAC is excluded** from production Release-One
  while HW-005 is open.
- I understand that **the LED ring is not part of the Release-One artifact**
  because the WebFlash config string has no `LED` slot.
- I copied `secrets.example.yaml` to `secrets.yaml` and understand it is
  gitignored.
- I ran (or could have run) `esphome config` on the Release-One product YAML.
- I understand that a local `esphome compile` produces an **unsigned** `.bin`
  that is **not** the same as the WebFlash production artifact.
- I know when to stop and use WebFlash instead.

Each "no" or "had to guess" answer is a finding.

---

## Pass / Fail criteria

| Outcome | Definition |
| --- | --- |
| **Pass** | Tester completed all eight steps without external help, and answered "yes" to every item in [What the tester should verify](#what-the-tester-should-verify). |
| **Pass with minor help** | Tester completed all eight steps but needed a clarification on one or two items (record which). |
| **Partial** | Tester completed the read-only steps (1–4) but was blocked on validate / compile (5–6) or on understanding the customization path (7–8). |
| **Blocked** | Tester could not reach `esphome config` (or its doc-finding fallback) using only this repo's docs. |
| **Abandoned** | Tester gave up before reaching Step 4. |

A "Pass" outcome does **not** assert that the manual path is bug-free for
every config; it only asserts that the docs successfully guided one tester
through `Ceiling-POE-VentIQ-RoomIQ` end-to-end.

---

## Follow-up actions

After a tester records their findings:

1. **Open issues** for each blocking or partial-blocking finding. Tag with
   the step number (e.g. `walkthrough:step-2`).
2. **Open doc PRs** for each "had to guess" finding that points at unclear
   README / installation / release-one wording.
3. **Re-run the walkthrough** with a second, independent tester once the
   first round's blockers have been fixed. Two clean passes from two
   different testers is the bar for closing ESP-011 as proven.
4. **Do not modify firmware, workflows, or product YAML** based on
   walkthrough findings without a separate readiness-list item — this
   walkthrough is a docs-usability test, not a firmware test.

---

## Issue log template

Copy this section into your tester report (or fill it in directly in a
working copy of this file — **do not commit your filled-in copy back to the
repo**).

```markdown
## Walkthrough Findings

Date:
Tester:
Experience level:
Path tested:
Repo ref/tag:
Device/config tested:

### Result

- [ ] Completed without help
- [ ] Completed with minor help
- [ ] Blocked
- [ ] Abandoned

### Steps completed

- [ ] Found the correct documentation
- [ ] Understood WebFlash vs manual/custom path
- [ ] Found the correct product YAML
- [ ] Understood secrets setup
- [ ] Understood what not to use
- [ ] Compiled in ESPHome
- [ ] Flashed device
- [ ] Device booted
- [ ] Device joined Wi-Fi
- [ ] Device appeared in Home Assistant

### Issues found

| Step | What happened | Severity | Suggested fix |
| --- | --- | --- | --- |
|      |               |          |               |

### Notes

```

Severity guide for the table:

- **Blocker** — tester could not continue without external help.
- **Major** — tester completed the step but with significant confusion.
- **Minor** — wording or link nit that a reader would still notice.
- **Nit** — typo, formatting, style.

---

## See also

Existing docs in this repo that the walkthrough touches:

- [`README.md`](../README.md) — top-level overview, WebFlash vs. manual.
- [`docs/installation.md`](installation.md) — step-by-step setup.
- [`docs/development.md`](development.md) — dev environment, validation,
  pre-commit.
- [`docs/release-one.md`](release-one.md) — Release-One configuration.
- [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md) —
  FanTRIAC HW-005 audit and Release-One hardware decisions.
- [`docs/webflash-contract.md`](webflash-contract.md) — WebFlash artifact
  naming and grammar.
- [`docs/webflash-release-handoff.md`](webflash-release-handoff.md) — release
  flow and troubleshooting (includes a "Manual / custom users are confused"
  section).
- [`secrets.example.yaml`](../secrets.example.yaml) — local secrets template.
- [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml)
  — Release-One product YAML (FanTRIAC excluded while HW-005 is open).

---

## Notes for Reviewers

This walkthrough is a test harness, not proof. After it lands, a real tester
must actually run through it and file concrete findings; only then do we know
whether the manual path is usable. The walkthrough does **not** assert that
the manual path is correct — it only gives someone a structured way to find
out.

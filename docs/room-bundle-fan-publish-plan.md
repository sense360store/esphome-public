# Room-bundle fan-control preview publish plan — pre-run record

> **Workflow merged:** the publication path planned here is now part of the
> merged [`preview-fan-publish.yml`](../.github/workflows/preview-fan-publish.yml)
> workflow (`fan_set: room-bundle`); the standalone `room-bundle-fan-publish.yml`
> file was removed when the two fan-publish workflows were merged. This pre-run
> record is unchanged.

**Canonical id:** `ROOM-BUNDLE-FAN-PUBLISH-PLAN-001`
**Date:** 2026-06-04
**Type:** Plans the preview-artifact publication of the **five full-composition
Bathroom / Kitchen fan-control room-bundle** firmware configs that now carry
hosted full ESPHome compile proof, **before** any release workflow is run or any
artifact is published. This PR **records the per-target publish metadata, decides
the publish lane, and queues the workflow extension + run**. It is **planning /
metadata only**: it **publishes no firmware**, runs **no** workflow, creates
**no** GitHub Release / tag / checksum, commits **no** `.bin`, writes **no**
`manifest.json` / `firmware/sources.json`, touches **no** WebFlash repo, adds
**no** `config/webflash-builds.json` row, marks **nothing** stable / recommended
/ default / buyable, claims **no** hardware / bench / compliance / safety /
commercial proof, does **not** mark FanDAC hardware-verified, and **excludes
TRIAC**.

> **Update — the queued workflow has now landed (`ROOM-BUNDLE-FAN-PUBLISH-WORKFLOW-001`).**
> The additive publish path planned in §4.3 / §8 is now in the tree as
> [`.github/workflows/room-bundle-fan-publish.yml`](../.github/workflows/room-bundle-fan-publish.yml)
> + [`scripts/validate_room_bundle_fan_publish.py`](../scripts/validate_room_bundle_fan_publish.py),
> documented at
> [`docs/room-bundle-fan-publish-workflow.md`](room-bundle-fan-publish-workflow.md).
> It is `workflow_dispatch` only, defaults to `dry_run: true`, reads
> `config/room-bundle-fan-variants.json` + `config/compile-only-targets.json`
> (never `config/webflash-builds.json`), excludes TRIAC, reuses the shared
> `v1.0.0-preview` release + the `RELEASE-PREVIEW-FAN-PUBLISH-TAG-GUARD-001`
> confirm-gate, and leaves the single-driver
> `scripts/validate_manual_preview_fan_publish.py` lane untouched. **The workflow
> PR still publishes no firmware** — the actual run stays queued as
> `ROOM-BUNDLE-FAN-PUBLISH-RUN-001` (§8).

> **Sibling of `RELEASE-PREVIEW-FAN-PUBLISH-PLAN-001`.** That plan covered the
> **three single-driver** manual-preview fan artifacts
> (`Ceiling-POE-VentIQ-FanRelay-RoomIQ`, `Ceiling-POE-FanPWM`,
> `Ceiling-POE-FanDAC`) compiled by run `26821900127`, and its publish path is
> now live ([`.github/workflows/manual-preview-fan-publish.yml`](../.github/workflows/manual-preview-fan-publish.yml)
> + [`scripts/validate_manual_preview_fan_publish.py`](../scripts/validate_manual_preview_fan_publish.py)).
> **This** plan covers a **different, non-overlapping set** — the **five
> full-composition room-bundle** fan configs (room sensing **plus** a fan driver)
> compiled by run **`26913592989`**. The two sets share the same shared
> `v1.0.0-preview` release vehicle and the same "advanced / manual preview, no
> WebFlash build row, TRIAC excluded" posture, but they are distinct config
> strings on distinct compile runs and live in distinct source files (§4).

**Predecessors:**

- `#713` `ROOM-BUNDLE-FAN-CONFIGS-001` authored the five full-composition
  room-bundle fan-control product YAMLs (a `products/sense360-*.yaml` shim over a
  `products/bundles/*.yaml` composition), each with a
  [`config/product-catalog.json`](../config/product-catalog.json)
  `hardware-pending` row and a
  [`config/compile-only-targets.json`](../config/compile-only-targets.json)
  target.
- `#716` `ROOM-BUNDLE-FAN-COMPILE-RESULTS-001` recorded the **hosted full ESPHome
  compile** result for all five — [run `26913592989`](https://github.com/sense360store/esphome-public/actions/runs/26913592989)
  (`Compile-only Firmware Validation`, `workflow_dispatch` / `compile_mode=full`,
  ref `main`, 2026-06-04, ESPHome `2026.4.5`; Metadata Validation **success**,
  Full ESPHome Compile **success**) — and promoted the five from
  `buildable-preview-compile-pending` to `buildable-preview-compile-validated`
  in [`config/room-bundle-fan-variants.json`](../config/room-bundle-fan-variants.json)
  ([`docs/room-bundle-fan-compile-results.md`](room-bundle-fan-compile-results.md)).
- `#715` `FANDAC-I2C-ADDR-001` added the FanDAC I²C address bench verification
  checklist ([`docs/hardware/fandac-i2c-address-verification.md`](hardware/fandac-i2c-address-verification.md));
  it stays **pending** (§3).

---

## TL;DR

* **Scope is exactly five full-composition room-bundle fan previews**, all
  compile-validated by run **`26913592989`**:
  `Ceiling-POE-VentIQ-FanPWM-RoomIQ`, `Ceiling-POE-VentIQ-FanDAC-RoomIQ`,
  `Ceiling-POE-AirIQ-FanRelay-RoomIQ`, `Ceiling-POE-AirIQ-FanDAC-RoomIQ`, and
  `Ceiling-POE-AirIQ-FanPWM-RoomIQ`. Each carries the bundle's room-sensing
  modules **plus** a fan driver — a correct full-bundle composition, **not** a
  fan-only substitution.
* **TRIAC is out of scope.** `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` is
  **build-blocked by `HW-005`** — not buildable end-to-end, no compile proof, no
  `.bin`, and **none is planned here**. Kitchen has no TRIAC variant by policy.
* **The two FanDAC configs require the GP8403 IC2 `0x5A` override** and a matching
  installer DIP switch; the DIP-position → address mapping is **not bench
  verified** and stays owed by `FANDAC-I2C-ADDR-001` (§3). No bench proof is
  claimed.
* **Publish-lane decision (§4): the existing manual-preview fan publish workflow
  cannot publish these five as-is, so a small additive workflow extension is
  queued.** The existing workflow + validator are hard-scoped to the **three
  single-driver** manual-preview rows in
  [`config/preview-fan-triac-build-rows.json`](../config/preview-fan-triac-build-rows.json)
  and cite the **other** compile run (`26821900127`). The five room-bundle
  configs are not in that ledger, sit on a different delivery lane, and cite run
  `26913592989`. Reusing the existing workflow would conflate two compile runs and
  two ledgers, so this plan **queues** the additive extension
  (`ROOM-BUNDLE-FAN-PUBLISH-WORKFLOW-001`) and the eventual run
  (`ROOM-BUNDLE-FAN-PUBLISH-RUN-001`) instead of overloading the existing
  validator or hacking fans into `config/webflash-builds.json`.
* **Nothing becomes stable / recommended / default / buyable.** Simple install
  stays the stable Bathroom PoE build (`Ceiling-POE-VentIQ-RoomIQ`,
  `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`, launch SKU
  `S360-KIT-BATH-P`). WebFlash one-click import stays a strictly later,
  separately gated, post-publication WebFlash-repo follow-up (§7).

---

## 1. The five compile-validated room-bundle fan targets

Every field below is read from
[`config/room-bundle-fan-variants.json`](../config/room-bundle-fan-variants.json)
(the canonical source-of-truth) and
[`config/compile-only-targets.json`](../config/compile-only-targets.json) (the
compile-evidence ledger). Nothing is hand-invented. Artifact names follow the
contract `Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin`.

Common to all five:

| Field | Value |
|---|---|
| Version | `1.0.0` |
| Build channel | `preview` |
| Publish delivery lane | `manual-preview` (Advanced-install-only preview) |
| Source delivery lane today | `room-bundle-preview-compile-validated` (compile-validated, not yet published) |
| Compile evidence | hosted **Compile-only Firmware Validation** run [`26913592989`](https://github.com/sense360store/esphome-public/actions/runs/26913592989) (`workflow_dispatch` / `compile_mode=full`, ref `main`, 2026-06-04, ESPHome `2026.4.5`; Metadata Validation `success`, Full ESPHome Compile `success`; `proof_scope: firmware-build-only`) |
| Commercial posture | **hidden / candidate / not buyable**; not recommended; not a customer default; not stable; not a required config; `commercial_availability: waitlist-only` |
| Hardware / bench / compliance / safety / commercial proof | **none claimed** — firmware-build (compile) proof only |
| Pre-publication warning copy | *"PREVIEW (COMPILE-VALIDATED) — the full room-bundle firmware config EXISTS (product YAML authored) and its hosted ESPHome compile has PASSED (Compile-only Firmware Validation run 26913592989; full ESPHome compile success), but NO preview .bin is published. This build is NOT hardware verified, NOT stable, NOT recommended, NOT a customer default, and NOT buyable. No bench evidence and no compliance is claimed. It is NOT exposed in WebFlash."* |
| Post-publication warning copy (release body / installer) | *"PREVIEW FIRMWARE — buildable and installable for testers only. This build is NOT hardware verified, NOT stable, NOT recommended, and NOT a customer default. No bench evidence and no compliance is claimed. Flash at your own risk and expect to recover with the rescue/stable firmware."* |

### 1.1 `Sense360-Ceiling-POE-VentIQ-FanPWM-RoomIQ-v1.0.0-preview.bin`

| Field | Value |
|---|---|
| Config string | `Ceiling-POE-VentIQ-FanPWM-RoomIQ` |
| Room / bundle SKU | Bathroom / `S360-KIT-BATH-P-PWM` |
| Fan driver SKU | `S360-311` (PWM, low-voltage / DC) |
| Product YAML | `products/sense360-ceiling-poe-ventiq-fanpwm-roomiq.yaml` |
| Bundle YAML | `products/bundles/ceiling-poe-ventiq-fanpwm-roomiq.yaml` |
| Compile-only target id | `ceiling-poe-ventiq-fanpwm-roomiq-compile-only` |
| Compile evidence | run `26913592989` (`firmware-build-only`) |
| Room modules | VentIQ + RoomIQ (full-bundle composition; not a fan-only substitution) |
| Release-target / workflow selector | `Ceiling-POE-VentIQ-FanPWM-RoomIQ` (or `all-room-bundle-fan-previews`) on the queued `ROOM-BUNDLE-FAN-PUBLISH-WORKFLOW-001` |
| Stable blockers | compile-validated but **not published / not WebFlash-exposed / not hardware verified** — stable additionally requires hardware, bench evidence, and compliance sign-off; measured current / thermal evidence (`S360-311-CURRENT-THERMAL-001`, RPM / TachIO not claimed); shared `S360-410` PoE PSU schematic verification (`PRODUCT-POE-410-001`). |
| WebFlash import eligibility after publication | **post-publication only**, separately gated (§7); not auto-imported; no `config/webflash-builds.json` row |
| Expected output file name | `Sense360-Ceiling-POE-VentIQ-FanPWM-RoomIQ-v1.0.0-preview.bin` |

### 1.2 `Sense360-Ceiling-POE-VentIQ-FanDAC-RoomIQ-v1.0.0-preview.bin`

| Field | Value |
|---|---|
| Config string | `Ceiling-POE-VentIQ-FanDAC-RoomIQ` |
| Room / bundle SKU | Bathroom / `S360-KIT-BATH-P-DAC` |
| Fan driver SKU | `S360-312` (0-10V / DAC) |
| Product YAML | `products/sense360-ceiling-poe-ventiq-fandac-roomiq.yaml` |
| Bundle YAML | `products/bundles/ceiling-poe-ventiq-fandac-roomiq.yaml` |
| Compile-only target id | `ceiling-poe-ventiq-fandac-roomiq-compile-only` |
| Compile evidence | run `26913592989` (`firmware-build-only`); compiled **with** the FanDAC IC2 `0x5A` override (§3) |
| Room modules | VentIQ + RoomIQ (full-bundle composition; not a fan-only substitution) |
| FanDAC I²C address requirement | GP8403 IC1 `0x58`, IC2 `0x5A`; `0x59` **forbidden** (collides with SGP41 @ `0x59`); `FANDAC-I2C-ADDR-001` **pending** (§3) |
| Release-target / workflow selector | `Ceiling-POE-VentIQ-FanDAC-RoomIQ` (or `all-room-bundle-fan-previews`) on the queued `ROOM-BUNDLE-FAN-PUBLISH-WORKFLOW-001` |
| Stable blockers | compile-validated but **not published / not WebFlash-exposed / not hardware verified** — stable additionally requires hardware, bench evidence, and compliance sign-off; `FANDAC-I2C-ADDR-001` (bench-verify the S360-312 DIP-position → I²C address mapping, IC1=`0x58` / IC2=`0x5A`, on the shared `core_i2c` bus with SGP41 @ `0x59` present); Cloudlift S12 / J3 harness + product-bench evidence + S360-312 schematic / BOM; shared `S360-410` PoE PSU schematic verification (`PRODUCT-POE-410-001`). |
| WebFlash import eligibility after publication | **post-publication only**, separately gated, **Advanced / manual only** — the `fandac_conflicts_with_airiq` mutex does not apply (VentIQ here), but the one-click surface still cannot set the IC2 DIP switch, so any import stays behind the documented `0x5A` switch requirement (§7); no `config/webflash-builds.json` row |
| Expected output file name | `Sense360-Ceiling-POE-VentIQ-FanDAC-RoomIQ-v1.0.0-preview.bin` |

### 1.3 `Sense360-Ceiling-POE-AirIQ-FanRelay-RoomIQ-v1.0.0-preview.bin`

| Field | Value |
|---|---|
| Config string | `Ceiling-POE-AirIQ-FanRelay-RoomIQ` |
| Room / bundle SKU | Kitchen / `S360-KIT-KITCHEN-P-REL` |
| Fan driver SKU | `S360-310` (Relay) |
| Product YAML | `products/sense360-ceiling-poe-airiq-fanrelay-roomiq.yaml` |
| Bundle YAML | `products/bundles/ceiling-poe-airiq-fanrelay-roomiq.yaml` |
| Compile-only target id | `ceiling-poe-airiq-fanrelay-roomiq-compile-only` |
| Compile evidence | run `26913592989` (`firmware-build-only`) |
| Room modules | AirIQ + RoomIQ (full-bundle composition; not a fan-only substitution) |
| Release-target / workflow selector | `Ceiling-POE-AirIQ-FanRelay-RoomIQ` (or `all-room-bundle-fan-previews`) on the queued `ROOM-BUNDLE-FAN-PUBLISH-WORKFLOW-001` |
| Stable blockers | compile-validated but **not published / not WebFlash-exposed / not hardware verified** — stable additionally requires hardware, bench evidence, and compliance sign-off; base Kitchen bundle (`Ceiling-POE-AirIQ-RoomIQ`) is preview / stable-candidate, not yet stable (AirIQ-stack hardware evidence: SPS30 / SGP41 / SCD41 / BMP390); mains-safety / installation-approval / creepage / clearance evidence + competent-person sign-off (`S360-310`); shared `S360-410` PoE PSU schematic verification (`PRODUCT-POE-410-001`). |
| WebFlash import eligibility after publication | **post-publication only**, separately gated (§7); not auto-imported; no `config/webflash-builds.json` row |
| Expected output file name | `Sense360-Ceiling-POE-AirIQ-FanRelay-RoomIQ-v1.0.0-preview.bin` |

### 1.4 `Sense360-Ceiling-POE-AirIQ-FanDAC-RoomIQ-v1.0.0-preview.bin`

| Field | Value |
|---|---|
| Config string | `Ceiling-POE-AirIQ-FanDAC-RoomIQ` |
| Room / bundle SKU | Kitchen / `S360-KIT-KITCHEN-P-DAC` |
| Fan driver SKU | `S360-312` (0-10V / DAC) |
| Product YAML | `products/sense360-ceiling-poe-airiq-fandac-roomiq.yaml` |
| Bundle YAML | `products/bundles/ceiling-poe-airiq-fandac-roomiq.yaml` |
| Compile-only target id | `ceiling-poe-airiq-fandac-roomiq-compile-only` |
| Compile evidence | run `26913592989` (`firmware-build-only`); compiled **with** the FanDAC IC2 `0x5A` override (§3) |
| Room modules | AirIQ + RoomIQ (full-bundle composition; not a fan-only substitution) |
| FanDAC I²C address requirement | GP8403 IC1 `0x58`, IC2 `0x5A`; `0x59` **forbidden** (collides with the AirIQ SGP41 @ `0x59`); `FANDAC-I2C-ADDR-001` **pending** (§3) |
| WebFlash one-click grammar | **excluded** (`webflash_grammar_excluded: true`, `fandac_conflicts_with_airiq`) — AirIQ + FanDAC stays out of the WebFlash one-click firmware-combination grammar because the one-click surface cannot set the required IC2 DIP switch to `0x5A`; this is the documented address-overridden exception |
| Release-target / workflow selector | `Ceiling-POE-AirIQ-FanDAC-RoomIQ` (or `all-room-bundle-fan-previews`) on the queued `ROOM-BUNDLE-FAN-PUBLISH-WORKFLOW-001` |
| Stable blockers | compile-validated but **not published / not WebFlash-exposed / not hardware verified** — stable additionally requires hardware, bench evidence, and compliance sign-off; `FANDAC-I2C-ADDR-001` (bench-verify the S360-312 DIP-position → I²C address mapping, IC1=`0x58` / IC2=`0x5A`, on the shared `core_i2c` bus with SGP41 @ `0x59` present); base Kitchen bundle (`Ceiling-POE-AirIQ-RoomIQ`) preview / stable-candidate, not yet stable; Cloudlift S12 / J3 harness + product-bench evidence + S360-312 schematic / BOM; shared `S360-410` PoE PSU schematic verification (`PRODUCT-POE-410-001`). |
| WebFlash import eligibility after publication | **post-publication only**, separately gated, **Advanced / manual only** — stays out of the one-click WebFlash grammar (`fandac_conflicts_with_airiq`); any import is behind the documented `0x5A` IC2 DIP-switch requirement (§7); no `config/webflash-builds.json` row |
| Expected output file name | `Sense360-Ceiling-POE-AirIQ-FanDAC-RoomIQ-v1.0.0-preview.bin` |

### 1.5 `Sense360-Ceiling-POE-AirIQ-FanPWM-RoomIQ-v1.0.0-preview.bin`

| Field | Value |
|---|---|
| Config string | `Ceiling-POE-AirIQ-FanPWM-RoomIQ` |
| Room / bundle SKU | Kitchen / `S360-KIT-KITCHEN-P-PWM` |
| Fan driver SKU | `S360-311` (PWM, low-voltage / custom) |
| Product YAML | `products/sense360-ceiling-poe-airiq-fanpwm-roomiq.yaml` |
| Bundle YAML | `products/bundles/ceiling-poe-airiq-fanpwm-roomiq.yaml` |
| Compile-only target id | `ceiling-poe-airiq-fanpwm-roomiq-compile-only` |
| Compile evidence | run `26913592989` (`firmware-build-only`) |
| Room modules | AirIQ + RoomIQ (full-bundle composition; not a fan-only substitution) |
| Policy note | `policy_gated: true` — Kitchen PWM is an optional low-voltage / custom kitchen-extract variant only (not a typical mains kitchen-extract control); it makes no recommendation / commercial claim and can be dropped if policy does not approve low-voltage / custom kitchen extract use |
| Release-target / workflow selector | `Ceiling-POE-AirIQ-FanPWM-RoomIQ` (or `all-room-bundle-fan-previews`) on the queued `ROOM-BUNDLE-FAN-PUBLISH-WORKFLOW-001` |
| Stable blockers | compile-validated but **not published / not WebFlash-exposed / not hardware verified** — stable additionally requires hardware, bench evidence, and compliance sign-off; policy approval for low-voltage / custom kitchen extract use (`policy_gated`); base Kitchen bundle (`Ceiling-POE-AirIQ-RoomIQ`) preview / stable-candidate, not yet stable; measured current / thermal evidence (`S360-311-CURRENT-THERMAL-001`, RPM / TachIO not claimed); shared `S360-410` PoE PSU schematic verification (`PRODUCT-POE-410-001`). |
| WebFlash import eligibility after publication | **post-publication only**, separately gated (§7); not auto-imported; no `config/webflash-builds.json` row |
| Expected output file name | `Sense360-Ceiling-POE-AirIQ-FanPWM-RoomIQ-v1.0.0-preview.bin` |

---

## 2. Expected artifacts

The publish run (once the workflow path exists — see §4) must produce **exactly**
these five durable preview binaries and **no others** from this plan:

1. `Sense360-Ceiling-POE-VentIQ-FanPWM-RoomIQ-v1.0.0-preview.bin`
2. `Sense360-Ceiling-POE-VentIQ-FanDAC-RoomIQ-v1.0.0-preview.bin`
3. `Sense360-Ceiling-POE-AirIQ-FanRelay-RoomIQ-v1.0.0-preview.bin`
4. `Sense360-Ceiling-POE-AirIQ-FanDAC-RoomIQ-v1.0.0-preview.bin`
5. `Sense360-Ceiling-POE-AirIQ-FanPWM-RoomIQ-v1.0.0-preview.bin`

No `Sense360-…-FanTRIAC-…-preview.bin` is in scope (TRIAC is build-blocked by
`HW-005`; see §6). The stable Simple-install artifact
`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` is **unchanged** and is
**not** re-published by this plan. The three single-driver manual-preview fan
artifacts already published by `RELEASE-PREVIEW-FAN-PUBLISH-RUN-001` are **out of
scope here** (different config strings, different compile run).

---

## 3. FanDAC IC2 `0x5A` address requirement (`FANDAC-I2C-ADDR-001` stays pending)

The two FanDAC room-bundle configs — `Ceiling-POE-VentIQ-FanDAC-RoomIQ`
(Bathroom DAC) and `Ceiling-POE-AirIQ-FanDAC-RoomIQ` (Kitchen DAC) — compiled
**with the FanDAC IC2 address override** `fan_dac_2_i2c_address: "0x5A"`.

| Address | Role |
|---|---|
| GP8403 IC1 | `0x58` (package default; unchanged) |
| GP8403 IC2 | `0x5A` (relocated off the `0x59` package default by the firmware override) |
| GP8403 `0x59` | **Forbidden** with VentIQ / AirIQ — it collides with the air-quality SGP41 at `0x59` on the shared `core_i2c` bus |
| SGP41 | `0x59` (VentIQ / AirIQ air-quality VOC/NOx sensor) |

This is a **compile-time configuration only**:

- The physical IC2 DIP-switch (SW2) → I²C address mapping is **NOT bench
  verified**. The installer **must** set the S360-312 IC2 DIP switch so IC2 reports
  `0x5A` (not the `0x59` default). The DIP-position → address truth table remains
  owed by `FANDAC-I2C-ADDR-001`, which stays **pending hardware verification**.
- A successful compile does **not** prove the installer's switch setting; it only
  proves the firmware composes with the `0x5A` override applied. **No FanDAC bench
  proof is claimed by this plan.**

The `fandac_conflicts_with_airiq` mutex in `config/webflash-compatibility.json`
**stays in force** for the WebFlash one-click surface; the AirIQ + FanDAC config
stays out of the one-click grammar (§1.4). These DAC configs are
advanced / manual previews behind the documented switch requirement, not
one-click WebFlash builds.

---

## 4. Publish-lane decision — and the GAP

The task asks: *can the existing manual-preview fan publish workflow safely
publish these five full-composition room-bundle configs?* The answer, verified
against the live config + workflow + validator, is **no — not without a small
additive extension** — and this section documents exactly why and what the fix is.

### 4.1 The existing manual-preview fan publish workflow is hard-scoped to the three single-driver rows

[`.github/workflows/manual-preview-fan-publish.yml`](../.github/workflows/manual-preview-fan-publish.yml)
(`RELEASE-PREVIEW-FAN-PUBLISH-WORKFLOW-001`) drives its matrix from
[`scripts/validate_manual_preview_fan_publish.py`](../scripts/validate_manual_preview_fan_publish.py),
which reads
[`config/preview-fan-triac-build-rows.json`](../config/preview-fan-triac-build-rows.json)
+ [`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json)
(never `config/webflash-builds.json`). That validator's `FAN_CONFIGS` is **hard-coded**
to the three single-driver manual-preview configs, and the `release_target` choice
input offers only those three plus `all-manual-preview-fans`. So:

| Claim | Result |
|---|---|
| The five room-bundle configs are in `config/preview-fan-triac-build-rows.json` | ❌ **No.** That ledger holds 4 rows — the three single-driver fans + the build-blocked TRIAC row; none of the five room-bundle configs. |
| The five room-bundle configs are in `config/manual-firmware-artifacts.json` | ❌ **No.** That lane holds only the `fanrelay` / `fanpwm` / `fandac` single-driver candidates. |
| The existing workflow's `release_target` picker can scope to a room-bundle config | ❌ **No.** Its options are only the three single-driver configs + `all-manual-preview-fans`; the five room-bundle config strings are rejected. |
| The existing validator's per-row checks pass for the five | ❌ **No.** The five carry `delivery_lane: room-bundle-preview-compile-validated` (not `manual-preview`) and have no `manual_lane_candidate_id` / release-note draft in the manual lane. |
| The existing release body cites the right compile run | ❌ **No.** It hard-codes run `26821900127`; the five cite run `26913592989`. |
| Therefore the existing workflow can publish the five room-bundle `-preview.bin` | ❌ **No — this is the gap.** |

### 4.2 The compile lane is not a publish lane

[`.github/workflows/compile-only.yml`](../.github/workflows/compile-only.yml)
*compiled* the five (run `26913592989`) but is a **compile-only validator**: it
runs `esphome config` / `compile` for proof, produces **no** durable release
artifact, creates **no** Release / tag, and explicitly records
`proof_scope: firmware-build-only`. Compile success is **not** publication.

### 4.3 Decision: queue a small additive workflow extension (do not overload the existing validator, do not hack `config/webflash-builds.json`)

The existing manual-preview fan publish workflow is the **right family** — it
publishes preview fan artifacts to the shared `v1.0.0-preview` release, adds no
WebFlash build row, excludes TRIAC, and claims no hardware proof. But it **cannot
publish these five as-is** (§4.1). Two safe paths exist; both are *extensions*, not
a no-op reuse:

* **This plan does NOT add room-bundle rows to `config/webflash-builds.json`.**
  That file stays the sole WebFlash release-eligibility source of truth, and the
  fan-token guardrail stays intact.
* **This plan does NOT overload the existing 3-target manual-preview validator**
  by mixing the five room-bundle configs (run `26913592989`) into the single-driver
  ledger (run `26821900127`). Conflating two compile runs and two delivery lanes
  in one validator / release body would be scope drift.
* **A small additive workflow extension is queued: `ROOM-BUNDLE-FAN-PUBLISH-WORKFLOW-001`.**
  It adds a **room-bundle preview target group** to the manual-preview fan publish
  family, reading the five compile-validated room-bundle configs from
  `config/room-bundle-fan-variants.json` (+ `config/compile-only-targets.json` for
  the compile evidence — **not** `config/webflash-builds.json`), building each
  `products/sense360-*-roomiq.yaml`, renaming each output to its expected
  `-v1.0.0-preview.bin`, and attaching the five durable artifacts to the **same
  shared `v1.0.0-preview` preview release** (`RELEASE-PREVIEW-FAN-SHARED-TAG-001`),
  reusing the existing tag confirm-gate (`RELEASE-PREVIEW-FAN-PUBLISH-TAG-GUARD-001`).
  The two FanDAC artifacts carry the `0x5A` requirement + `FANDAC-I2C-ADDR-001`
  pending note in the release body. TRIAC stays excluded (`HW-005`).
* **Then `ROOM-BUNDLE-FAN-PUBLISH-RUN-001`** executes that workflow.

### 4.4 Version / channel / tag / source expectations for the queued workflow

| Expectation | Value |
|---|---|
| Version | `1.0.0` |
| Channel / build channel | `preview` / `preview` |
| Publish delivery lane | `manual-preview` (Advanced-install-only; the five room-bundle fan previews) |
| Artifact names | the five `-v1.0.0-preview.bin` values in §1 / §2 |
| Release-target / workflow selector | `all-room-bundle-fan-previews` (group) or one of the five config strings |
| Source of truth for the matrix | `config/room-bundle-fan-variants.json` (+ `config/compile-only-targets.json`), **not** `config/webflash-builds.json` and **not** the single-driver `config/preview-fan-triac-build-rows.json` |
| Release vehicle | the shared `v1.0.0-preview` preview release (`RELEASE-PREVIEW-FAN-SHARED-TAG-001`); reuse the tag confirm-gate (`RELEASE-PREVIEW-FAN-PUBLISH-TAG-GUARD-001`); **must not** add a WebFlash build row or imply WebFlash one-click import |
| Excluded | `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` (`HW-005`); the stable Bathroom build; every WebFlash one-click import |

---

## 5. What is proven (and what is not)

* **Proven (firmware-build / compile only):** the canonical product YAML for each
  of the five room-bundle fan configs composed / substituted / included /
  generated code cleanly under ESPHome `2026.4.5` on hosted CI — Compile-only
  Firmware Validation run [`26913592989`](https://github.com/sense360store/esphome-public/actions/runs/26913592989)
  (2026-06-04), Metadata Validation `success` + Full ESPHome Compile `success`;
  and each artifact name follows the `Sense360-{config}-v{version}-{channel}.bin`
  contract.
* **Not proven / not claimed:** any FanTRIAC compile (build-blocked by `HW-005`),
  the FanDAC IC2 DIP-switch → address mapping (`FANDAC-I2C-ADDR-001` pending),
  hardware operation, bench verification, a verified schematic, electrical /
  mains-safety / EMC compliance, commercial availability, or any
  stable-promotion readiness. A green compile is **not** hardware, bench, safety,
  or compliance evidence, and a validated plan is **not** a published artifact.

---

## 6. Out of scope (explicit)

| Item | Status / reason |
|---|---|
| `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` (TRIAC) | **Excluded** — build-blocked by `HW-005` (S360-320 schematic uncommitted; placeholder GPIO5/GPIO6 collide with RoomIQ J10 nets; ESPHome `ac_dimmer` cannot run across the SX1509 expander). No compile / firmware artifact exists; none is planned. Kitchen has no TRIAC variant by policy. |
| Any stable / full release | **Excluded** — nothing here is promoted to stable; the stable channel stays evidence-gated. |
| Stable / recommended / default / buyable status | **Excluded** — every one of the five stays not stable, not recommended, not a customer default, not buyable, not a required config. |
| FanDAC hardware verification | **Excluded** — `FANDAC-I2C-ADDR-001` stays pending; no FanDAC bench proof is claimed (§3). |
| Any WebFlash one-click import / `config/webflash-builds.json` row | **Excluded** — import is a strictly later, separately gated, post-publication WebFlash-repo follow-up (§7); no fan row is added to `config/webflash-builds.json`; this PR does not touch the WebFlash repo. |
| Any Simple-install exposure | **Excluded** — Simple install stays the stable Bathroom PoE build only (`Ceiling-POE-VentIQ-RoomIQ`, `S360-KIT-BATH-P`). |

---

## 7. WebFlash import eligibility — after publication only

WebFlash one-click import is **never** implied by, or simultaneous with,
publication. The sequence is strictly ordered:

1. **Today (this plan):** the five are compile-validated only. They are **not**
   importable — no published `.bin`, `webflash_build_matrix: false`,
   `webflash_exposed: false`, not in `config/webflash-builds.json`, and not in any
   WebFlash repo surface. This PR sets **no** `webflash_import_eligibility` flag and
   touches **no** WebFlash repo.
2. **After `ROOM-BUNDLE-FAN-PUBLISH-RUN-001` publishes the five `-preview.bin`:**
   each durable artifact *becomes a candidate* for a **separate, later,
   downstream WebFlash-repo import follow-up** (the WebFlash-side `WF-IMPORT-*`
   family), gated by WebFlash import policy and the WebFlash fan-preview
   acknowledgement UX. Presence in the shared `v1.0.0-preview` release does **not**
   make any of them a WebFlash one-click import, a Simple-install option, stable,
   recommended, default, or buyable.
3. **`Ceiling-POE-AirIQ-FanDAC-RoomIQ` is additionally grammar-excluded** from the
   WebFlash one-click surface (`fandac_conflicts_with_airiq`); even after
   publication it can only ever be an Advanced / manual import behind the
   documented IC2 `0x5A` DIP-switch requirement (§3), never a one-click build.

So: **WebFlash import is only after artifact publication**, and even then only via
a separate WebFlash-repo PR — never as a side effect of this plan or of the
queued publish run.

---

## 8. Queued follow-ups

1. **`ROOM-BUNDLE-FAN-PUBLISH-WORKFLOW-001`** — **DONE** (the additive room-bundle
   preview publish lane is now in the tree:
   [`.github/workflows/room-bundle-fan-publish.yml`](../.github/workflows/room-bundle-fan-publish.yml)
   + [`scripts/validate_room_bundle_fan_publish.py`](../scripts/validate_room_bundle_fan_publish.py)
   + [`docs/room-bundle-fan-publish-workflow.md`](room-bundle-fan-publish-workflow.md)).
   It reads `config/room-bundle-fan-variants.json` +
   `config/compile-only-targets.json` (**not** `config/webflash-builds.json`),
   excludes TRIAC, cites run `26913592989`, and publishes to the shared
   `v1.0.0-preview` release. See §4.3 / §4.4. **Publishes no firmware** — the run
   stays queued below.
2. **`ROOM-BUNDLE-FAN-PUBLISH-RUN-001`** — run the room-bundle preview publication
   for the five artifacts named in §1 / §2, on `version=1.0.0`, `channel=preview`,
   keeping the stable Bathroom build, TRIAC, and every WebFlash one-click import out.
3. **WebFlash-repo import follow-up (`WF-IMPORT-*`)** — the WebFlash-side one-click
   import, strictly after publication and only once the WebFlash fan-preview
   acknowledgement UX supports it. Not started; not implied by this plan (§7).
4. **FanTRIAC `HW-005`** — unchanged buildability defect; FanTRIAC stays
   build-blocked, excluded from every publish surface, and never gets a `.bin` here.
5. **`FANDAC-I2C-ADDR-001`** — FanDAC IC2 DIP-position → address bench verification;
   stays pending; gates FanDAC stable promotion, not this preview publish plan.

---

## 9. Guardrails — what this PR did and did NOT do

It did **not**: publish firmware; create a GitHub Release / tag / checksum;
commit any `.bin`; write `manifest.json` or `firmware/sources.json`; run any
workflow; modify any workflow or the existing
`scripts/validate_manual_preview_fan_publish.py`; touch the WebFlash repo
(including its `manifest.json` / `firmware/sources.json`); add a
`config/webflash-builds.json` row for any fan / TRIAC config; add a fan target to
Simple install; include TRIAC in the publish scope; mark any target stable /
recommended / default / buyable; mark FanDAC hardware-verified; change Simple
install or the launch SKU `S360-KIT-BATH-P`; or claim hardware / bench /
compliance / safety / commercial proof. It edits only this plan doc, the new test
[`tests/test_room_bundle_fan_publish_plan.py`](../tests/test_room_bundle_fan_publish_plan.py),
and `UPCOMING_PR.md`.

---

## 10. Validation

All commands run from the repo root and pass:

| Command | Result |
|---|---|
| `python3 tests/validate_configs.py` | `✅ All configuration files are valid!` |
| `python3 scripts/validate_compile_targets.py --metadata-only` | `✅ Metadata validation passed.` (23 targets) |
| `python3 scripts/validate_preview_release_targets.py --metadata-only` | `✅ … validation passed.` (9 targets) |
| `python3 scripts/validate_manual_preview_fan_publish.py --metadata-only` | `… metadata validated (3 target(s)…)` — the existing single-driver lane is **unchanged** |
| `python3 tests/test_room_bundle_fan_publish_plan.py` | `OK` (this PR's guard) |
| `python3 -m unittest discover -s tests -p "test_*.py"` | `OK` |

---

## Cross-references

- Canonical source-of-truth: [`config/room-bundle-fan-variants.json`](../config/room-bundle-fan-variants.json)
- Compile-evidence ledger: [`config/compile-only-targets.json`](../config/compile-only-targets.json) · compile result doc [`docs/room-bundle-fan-compile-results.md`](room-bundle-fan-compile-results.md)
- Product lifecycle catalog: [`config/product-catalog.json`](../config/product-catalog.json) (the five stay `hardware-pending`)
- FanDAC I²C address verification (pending): [`docs/hardware/fandac-i2c-address-verification.md`](hardware/fandac-i2c-address-verification.md)
- Sibling single-driver fan publish plan: [`docs/release-preview-fan-publish-plan.md`](release-preview-fan-publish-plan.md)
- Existing manual-preview fan publish workflow + validator: [`.github/workflows/manual-preview-fan-publish.yml`](../.github/workflows/manual-preview-fan-publish.yml) · [`scripts/validate_manual_preview_fan_publish.py`](../scripts/validate_manual_preview_fan_publish.py)
- Single-driver fan / TRIAC build-row ledger: [`config/preview-fan-triac-build-rows.json`](../config/preview-fan-triac-build-rows.json) · [`docs/release-preview-fan-triac-build-rows.md`](release-preview-fan-triac-build-rows.md)
- Manual (non-release) firmware lane: [`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json)
- Preview target manifest: [`config/preview-release-targets.json`](../config/preview-release-targets.json) · [`docs/preview-release-targets.md`](preview-release-targets.md)
- WebFlash release-eligibility source of truth: [`config/webflash-builds.json`](../config/webflash-builds.json)
- Room bundles overview: [`docs/sense360-room-bundles.md`](sense360-room-bundles.md)

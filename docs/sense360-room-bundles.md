# Sense360 PoE Room Bundle SKU Matrix (BUNDLE-SKU-MATRIX-001)

## Purpose and scope

This document is the **canonical** Sense360 PoE room bundle SKU matrix.
A **room bundle SKU** is a sellable, customer-facing kit identifier
(for example `S360-KIT-BATH-P`) that names the physical Sense360 boards
shipped together as a single room kit. It sits **above** the board /
firmware layers and connects to the existing board SKU, YAML, and
release-target documentation.

It exists because the prior planning layers in this repo capture three
neighbouring but distinct identifier spaces and none was a canonical
commercial room-bundle layer:

- **Board SKU** — a physical PCB. Source of truth:
  [`config/hardware-catalog.json`](../config/hardware-catalog.json) /
  [`docs/hardware-catalog.md`](hardware-catalog.md).
- **Firmware config string** — a YAML / release target token sequence.
  Source of truth:
  [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json),
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  [`config/product-catalog.json`](../config/product-catalog.json).
- **Kit intent** — a productized planning record that groups boards by
  use case (`bathroom`, `kitchen-or-duct-fan`). Source of truth:
  [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json) /
  [`docs/kit-intent-matrix.md`](kit-intent-matrix.md).

This document and its data file
[`config/room-bundle-skus.json`](../config/room-bundle-skus.json) add a
**room-bundle SKU** layer that names the Release-One PoE room kits as a
sellable set and maps each onto (a) the boards shipped in the bundle and
(b) the **likely firmware config target** that those boards together
produce, along with the current release status of that firmware config
target and the missing stable-promotion gates.

> **Commercial / shop layer.** Which of these bundle SKUs is sellable at the
> first shop launch, the customer-facing shop title, candidate-bundle
> visibility, the customer WebFlash URL, and the approved / forbidden ecommerce
> claims are decided in the commercial source of truth
> [`docs/shop-commercial-source-of-truth.md`](shop-commercial-source-of-truth.md)
> / [`config/shop-commercial-source-of-truth.json`](../config/shop-commercial-source-of-truth.json)
> (`SHOP-COMMERCIAL-SOURCE-OF-TRUTH-001`). The launch shop product is the
> complete `S360-KIT-BATH-P` Bathroom PoE bundle **only**; the other bundles in
> this matrix are candidates that stay hidden from shop navigation and are
> **not** buyable. This matrix remains the canonical SKU layer; the commercial
> doc adds the shop-posture / claims layer on top of it.

### Identifier separation

Four identifier spaces are deliberately kept separate.

| Identifier space | Example | Source of truth |
|---|---|---|
| **Board SKU** | `S360-100`, `S360-200`, `S360-210`, `S360-211`, `S360-300`, `S360-410` | [`config/hardware-catalog.json`](../config/hardware-catalog.json) |
| **Firmware config string** | `Ceiling-POE-VentIQ-RoomIQ`, `Ceiling-POE-VentIQ-RoomIQ-LED` | [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json), [`config/webflash-builds.json`](../config/webflash-builds.json) |
| **Release artifact name** | `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` | [`config/webflash-builds.json`](../config/webflash-builds.json), [`config/product-catalog.json`](../config/product-catalog.json) |
| **Room bundle SKU** *(this doc)* | `S360-KIT-BATH-P` | [`config/room-bundle-skus.json`](../config/room-bundle-skus.json) |

A bundle SKU is **not** a board SKU, **not** a firmware config string,
and **not** a release artifact name. A bundle SKU may map onto a
current release target, a preview target, a stable candidate, or a
blocked / missing target. A bundle's name and SKU **do not** become
the release artifact name automatically: the release artifact name is
derived from the firmware config string per
[`docs/all-yaml-release-matrix.md`](all-yaml-release-matrix.md) §
Stable-promotion criteria G5.

### Bundle SKU vs the YAML bundle layer (`products/bundles/`)

A **room bundle SKU** (this document — a sellable kit identifier such as
`S360-KIT-BATH-P`) must not be confused with the firmware **YAML bundle layer**
introduced by the board/bundle refactor
([`docs/arch-board-bundle-plan.md`](arch-board-bundle-plan.md) §2.2). The YAML
bundle layer lives under [`products/bundles/`](../products/bundles/) and holds
one YAML file **named 1:1 to a firmware config string** (e.g.
`products/bundles/ceiling-poe-ventiq-roomiq.yaml` for `Ceiling-POE-VentIQ-RoomIQ`),
each assembling `boards + expansions + base + profiles`. That YAML bundle is a
**firmware config string** artefact, not a room bundle SKU:

- A YAML bundle file name matches a **firmware config string**
  ([`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json) /
  [`config/webflash-builds.json`](../config/webflash-builds.json)), not a room
  bundle SKU in
  [`config/room-bundle-skus.json`](../config/room-bundle-skus.json).
- A room bundle SKU maps onto a **likely firmware config target** (the
  `likely_firmware_config_target` field), which in turn is the config string the
  matching `products/bundles/*.yaml` is named for. The SKU → config-string
  mapping is the same one tabulated in the canonical matrix below; this PR
  changes **no** SKU and adds **no** new bundle.
- The room bundle SKU stays the customer-facing kit identifier; the YAML bundle
  stays an esphome-public-internal composition file. Neither becomes a release
  artifact name — that is still derived from the firmware config string per
  [`docs/all-yaml-release-matrix.md`](all-yaml-release-matrix.md) §
  Stable-promotion criteria G5.

This document does **not** introduce, rename, or fan-out any
`products/bundles/*.yaml` file; it only cross-links the existing YAML bundle
layer so the two "bundle" meanings stay distinct.

### This document is documentation only

BUNDLE-SKU-MATRIX-001 — this PR — does **not**:

- publish, build, or attach any firmware artifact, and creates no
  GitHub Release;
- commit any `.bin`, checksum, or build-info file;
- edit any YAML under [`products/`](../products/) or
  [`products/webflash/`](../products/webflash/) or
  [`products/compile-only/`](../products/compile-only/);
- add, remove, or modify any entry in
  [`config/webflash-builds.json`](../config/webflash-builds.json),
  [`config/product-catalog.json`](../config/product-catalog.json),
  [`config/compile-only-targets.json`](../config/compile-only-targets.json),
  [`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json),
  [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json),
  [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json),
  [`config/hardware-catalog.json`](../config/hardware-catalog.json),
  or [`config/webflash-compatibility.json`](../config/webflash-compatibility.json);
- write [`firmware/sources.json`](../firmware/sources.json) or
  `manifest.json`;
- promote LED from `preview` to `stable`;
- promote FanRelay / FanPWM / FanDAC out of `manual-candidate-only`;
- add an `artifact_name` to any product;
- flip any `webflash_build_matrix` value;
- add a fan bundle SKU (fan bundles are **not** introduced by this PR);
- invent unsupported firmware configs;
- claim that every bundle already has stable firmware;
- treat a bundle SKU as a board SKU;
- treat a bundle SKU as a firmware artifact name.

---

## Board SKUs referenced

The bundle matrix references only the canonical board SKUs already in
[`config/hardware-catalog.json`](../config/hardware-catalog.json). For
self-containment, the boards in scope for the PoE room bundles defined
here are:

| Board SKU | Friendly name | Role |
|---|---|---|
| `S360-100` | Sense360 Core | Required hub board (ESP32-S3 + connectors). |
| `S360-200` | Sense360 RoomIQ | Presence + comfort sensor stack. |
| `S360-210` | Sense360 AirIQ | Full air-quality sensor stack (CO2 / VOC / gas / PM / HCHO connectors). |
| `S360-211` | Sense360 VentIQ | Smaller bathroom-grade air-quality stack. |
| `S360-300` | Sense360 LED | LED status ring (WS2812B). **Preview-only.** |
| `S360-410` | Sense360 PoE PSU | PoE to 5V power supply. |

Out-of-scope today (not referenced by any bundle in this PR):
`S360-310`, `S360-311`, `S360-312` (fan drivers — manual-candidate-only),
`S360-320` (TRIAC — blocked, HW-005), `S360-400` (240V PSU —
compliance-blocked).

---

## Canonical PoE room bundle SKU matrix

The five bundles below are the canonical Sense360 PoE room bundle
SKUs. Every bundle includes the Sense360 Core (`S360-100`) and the
Sense360 PoE PSU (`S360-410`) — these are the mandatory hub + power
spine for every PoE room kit.

The Sense360 Core (`S360-100`) is the **central Core / backplane
controller** for the module stack: every room module (RoomIQ, AirIQ,
VentIQ, LED, Relay, PWM, DAC, TRIAC) connects through a dedicated
connector on the Core, and the Core is the only board that carries
the MCU. Each bundle therefore derives from
**`S360-100` Core + room modules + `S360-410` PoE PSU**. This
architectural framing — including the per-connector module SKU
mapping on the new R4 schematic — is recorded in
[`docs/hardware/s360-100-core-architecture.md`](hardware/s360-100-core-architecture.md)
(S360-100-NATIVE-TACH-PULSE-001 — R4 refresh). The canonical
per-pin Core-to-module connector pin map (per-connector matrix +
per-connector pin tables with `Pin number` / `Core net` / `ESP32
GPIO` / `Module-side signal` / `Signal type` / `Voltage` /
`Status` columns) is recorded in
[`docs/hardware/s360-100-core-connector-pin-map.md`](hardware/s360-100-core-connector-pin-map.md)
(S360-100-CONNECTOR-PINMAP-001). The per-module **module-side**
view of the same pin map is recorded in one document per board
under MODULE-PINMAPS-GDRIVE-001:
[`s360-200-module-pinmap.md`](hardware/s360-200-module-pinmap.md),
[`s360-210-module-pinmap.md`](hardware/s360-210-module-pinmap.md),
[`s360-211-module-pinmap.md`](hardware/s360-211-module-pinmap.md),
[`s360-300-module-pinmap.md`](hardware/s360-300-module-pinmap.md),
[`s360-310-module-pinmap.md`](hardware/s360-310-module-pinmap.md),
[`s360-311-module-pinmap.md`](hardware/s360-311-module-pinmap.md),
[`s360-312-module-pinmap.md`](hardware/s360-312-module-pinmap.md),
[`s360-320-module-pinmap.md`](hardware/s360-320-module-pinmap.md),
[`s360-400-module-pinmap.md`](hardware/s360-400-module-pinmap.md),
[`s360-410-module-pinmap.md`](hardware/s360-410-module-pinmap.md).

| Bundle SKU | Bundle name | Included boards | Likely firmware config target | Current release status | Missing gates (top of stack) |
|---|---|---|---|---|---|
| `S360-KIT-BATH-P` | Sense360 Bathroom Bundle — PoE | `S360-100` Sense360 Core; `S360-200` Sense360 RoomIQ; `S360-211` Sense360 VentIQ; `S360-410` Sense360 PoE PSU | `Ceiling-POE-VentIQ-RoomIQ` | **`stable-release`** (already exists) | None — Release-One ships this. |
| `S360-KIT-KITCHEN-P` | Sense360 Kitchen Bundle — PoE | `S360-100` Sense360 Core; `S360-200` Sense360 RoomIQ; `S360-210` Sense360 AirIQ; `S360-410` Sense360 PoE PSU | `Ceiling-POE-AirIQ-RoomIQ` | `stable-candidate` (needs AirIQ promotion) | G1–G8; AirIQ-stack hardware evidence (SPS30 / SGP41 / SCD41 / BMP390); PoE-410 chain (`PRODUCT-POE-410-001`). Owned by `STABLE-TARGET-AIRIQ-001` → `STABLE-TARGET-AIRIQ-ROOMIQ-001`. |
| `S360-KIT-LIVING-P` | Sense360 Living Room Bundle — PoE | `S360-100` Sense360 Core; `S360-200` Sense360 RoomIQ; `S360-300` Sense360 LED; `S360-410` Sense360 PoE PSU | `Ceiling-POE-RoomIQ-LED` (or equivalent) | `preview-candidate` (LED remains preview) | G1–G8; PoE-410 chain; G10 preview-to-stable gauntlet. LED stays preview until `LED-STABLE-PROMOTION-001` closes. |
| `S360-KIT-BEDROOM-P` | Sense360 Bedroom Bundle — PoE | `S360-100` Sense360 Core; `S360-200` Sense360 RoomIQ; `S360-410` Sense360 PoE PSU | `Ceiling-POE-RoomIQ` | `stable-candidate` | G1–G8; PoE-410 chain. Owned by `STABLE-TARGET-ROOMIQ-001` (after `STABLE-TARGET-CORE-001` shared PoE-410 closure). |
| `S360-KIT-CORRIDOR-P` | Sense360 Landing / Corridor Bundle — PoE | `S360-100` Sense360 Core; `S360-200` Sense360 RoomIQ; `S360-300` Sense360 LED; `S360-410` Sense360 PoE PSU | `Ceiling-POE-RoomIQ-LED` (or equivalent) | `preview-candidate` (LED remains preview) | Same as `S360-KIT-LIVING-P`. Living and Corridor currently share the same included board set; a future room-specific default firmware (for example a corridor-specific LED pattern or presence profile) would differentiate them. |

Notes:

- **`stable-release`** means the bundle's likely firmware config target
  is **already** in [`config/webflash-builds.json`](../config/webflash-builds.json)
  with `channel: stable`. Only `S360-KIT-BATH-P` qualifies today.
- **`stable-candidate`** means every blocker is on the standard
  product-onboarding axis (no LED, no fan, no TRIAC, no 240V PSU) and
  promotion is owned by a named `STABLE-TARGET-*-001` follow-up PR;
  promotion is **not** approved by this PR.
- **`preview-candidate`** means the bundle's likely firmware config
  target carries the LED token and so is gated by the preview-to-stable
  gauntlet at
  [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md);
  promotion is **not** approved by this PR.
- **Living and Corridor currently have the same included board set**
  unless a future room-specific firmware / default config differentiates
  them. Both stay `preview-candidate` while LED remains preview.

---

## Room-bundle fan-control PREVIEW variants (`ROOM-BUNDLE-FAN-VARIANTS-002`)

The base room bundle SKUs above **remain the main product line**, and the
**stable Bathroom sensing-only bundle (`S360-KIT-BATH-P` →
`Ceiling-POE-VentIQ-RoomIQ`) stays the default product**. The fan-control
variants below are **optional add-ons for the Bathroom and Kitchen bundles
only** — no other room bundle (Corridor / Landing, Living Room, Bedroom)
has a fan-control variant. To keep the stable room-bundle matrix above
clean, these variants live in a separate file
[`config/room-bundle-fan-variants.json`](../config/room-bundle-fan-variants.json)
(`ROOM-BUNDLE-FAN-VARIANTS-002`, OPTION A — separate file). `-002`
**promotes** the `-001` planning rows into an explicit **preview bundle
plan**.

### Easy mode becomes a bundle picker

The plan is that **WebFlash easy mode becomes a bundle picker**. In that
picker a fan-control variant **may appear as an Advanced-install-only,
acknowledgement-gated PREVIEW bundle product, shown with a warning** — but
only when its full-composition firmware config is actually built. The
stable Bathroom sensing-only bundle remains the recommended default; a
preview fan variant is never auto-selected, never recommended, and never a
customer default.

This document and its data file are still **source-of-truth metadata
only**. They perform **no firmware release and no WebFlash promotion**:
they add no product YAML, no firmware config string, no `artifact_name`, no
`config/webflash-builds.json` row, flip no `webflash_build_matrix`, and
**do not touch the WebFlash repo**. Actual WebFlash exposure of any
preview-eligible variant is a separately queued downstream WebFlash-repo
follow-up (for example `WF-IMPORT-RELAY-001`).

### Preview is allowed; stable stays hardware-gated

Per `RELEASE-PREVIEW-UNBLOCK-ALL-BUNDLES-001`, **a preview artifact does
not require hardware proof** — missing hardware / bench-evidence /
compliance evidence gates **stable / full release only**, never the preview
of a buildable target. The **only** thing that can stop a preview is a
genuine buildability blocker (today only the TRIAC target carries one,
under `HW-005`). Every variant below therefore keeps `stable_status:
blocked` with its hardware / evidence / compliance blockers recorded, even
when it is preview-eligible.

| Variant SKU | Base Bundle | Driver | Control | Intended firmware config | Config exists today? | WebFlash easy-mode | Preview / stable |
|---|---|---|---|---|---|---|---|
| `S360-KIT-BATH-P-REL` | `S360-KIT-BATH-P` | `S360-310` | relay | `Ceiling-POE-VentIQ-FanRelay-RoomIQ` | **Yes** — built + published preview | **Preview-eligible** (Advanced-install-only, acknowledgement-gated) | preview / stable **blocked** |
| `S360-KIT-BATH-P-TRIAC` | `S360-KIT-BATH-P` | `S360-320` | triac | `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` | Defined but **build-blocked** (`HW-005`) | **Advanced / manual only**, not easy-mode; build-blocked → not exposable yet | advanced-preview (blocked) / stable **blocked** |
| `S360-KIT-BATH-P-PWM` | `S360-KIT-BATH-P` | `S360-311` | pwm | `Ceiling-POE-VentIQ-FanPWM-RoomIQ` | **Yes** — built + `buildable-preview-compile-validated` (`ROOM-BUNDLE-FAN-CONFIGS-001`; compile recorded by `ROOM-BUNDLE-FAN-COMPILE-RESULTS-001`) | Not eligible (preview `.bin` published; not WebFlash-exposed) | compile-validated preview / stable **blocked** |
| `S360-KIT-BATH-P-DAC` | `S360-KIT-BATH-P` | `S360-312` | 0-10V | `Ceiling-POE-VentIQ-FanDAC-RoomIQ` | **Yes** — built + `buildable-preview-compile-validated`; **requires FanDAC IC2 → 0x5A** (see below) | Not eligible (compile-validated; advanced / manual switch) | compile-validated preview / stable **blocked** |
| `S360-KIT-KITCHEN-P-REL` | `S360-KIT-KITCHEN-P` | `S360-310` | relay | `Ceiling-POE-AirIQ-FanRelay-RoomIQ` | **Yes** — built + `buildable-preview-compile-validated` | Not eligible (preview `.bin` published; not WebFlash-exposed) | compile-validated preview / stable **blocked** |
| `S360-KIT-KITCHEN-P-DAC` | `S360-KIT-KITCHEN-P` | `S360-312` | 0-10V | `Ceiling-POE-AirIQ-FanDAC-RoomIQ` | **Yes** — built + `buildable-preview-compile-validated`; **requires FanDAC IC2 → 0x5A**; WebFlash-grammar-excluded (`fandac_conflicts_with_airiq`) | Not eligible (compile-validated; advanced / manual switch; mutex) | compile-validated preview / stable **blocked** |
| `S360-KIT-KITCHEN-P-PWM` | `S360-KIT-KITCHEN-P` | `S360-311` | pwm | `Ceiling-POE-AirIQ-FanPWM-RoomIQ` | **Yes** — built + `buildable-preview-compile-validated` (policy-gated) | Not eligible (preview `.bin` published; not WebFlash-exposed) | compile-validated preview / stable **blocked** |

Only **`S360-KIT-BATH-P-REL`** has a built **and published** full-composition
preview firmware config today (`Ceiling-POE-VentIQ-FanRelay-RoomIQ`, on the
manual-preview lane — see
[`config/preview-release-targets.json`](../config/preview-release-targets.json)
and
[`config/preview-fan-triac-build-rows.json`](../config/preview-fan-triac-build-rows.json)).
It is the one variant that is WebFlash-easy-mode preview-eligible now.

### Full configs now exist and are compile-validated — `ROOM-BUNDLE-FAN-CONFIGS-001` + `ROOM-BUNDLE-FAN-COMPILE-RESULTS-001`

`ROOM-BUNDLE-FAN-CONFIGS-001` built the **five** previously-missing
full-composition firmware configs — Bathroom PWM / DAC and Kitchen Relay /
DAC / PWM — where the firmware packages already exist. Each has a real
`products/` shim + `products/bundles/` composition + a
[`config/product-catalog.json`](../config/product-catalog.json)
`hardware-pending` row + a
[`config/compile-only-targets.json`](../config/compile-only-targets.json)
target.

`ROOM-BUNDLE-FAN-COMPILE-RESULTS-001` then **recorded the hosted full ESPHome
compile result** for all five and promoted them from
`buildable-preview-compile-pending` to
**`buildable-preview-compile-validated`**. The **Compile-only Firmware
Validation** workflow (run
[`26913592989`](https://github.com/sense360store/esphome-public/actions/runs/26913592989),
`workflow_dispatch` / `compile_mode=full`, ref `main`, 2026-06-04, ESPHome
`2026.4.5`) passed both **Metadata Validation** and the **Full ESPHome
Compile**, so each target's `compile_validation_status` is now
**`validated-full-compile`** with a `compile_evidence` block (no compile is
fabricated). See
[`docs/room-bundle-fan-compile-results.md`](room-bundle-fan-compile-results.md)
for the full result record. A **fan-only** firmware config (for example
`Ceiling-POE-FanPWM` / `Ceiling-POE-FanDAC`, which omit the room-sensing
modules) is still **deliberately not substituted**: every variant config
carries the bundle's room modules (Bathroom = VentIQ + RoomIQ; Kitchen =
AirIQ + RoomIQ) **plus** the fan driver.

A green compile is **firmware-build proof only**. Each of these five configs
is now also published as an Advanced-install-only **preview `.bin`** (see the
next section), but they stay otherwise gated: no
`config/webflash-builds.json` row, **not** WebFlash-exposed, not stable, not
recommended, not a customer default, not buyable. **TRIAC stays build-blocked
(`HW-005`)**, **Bathroom Relay is unchanged**, the FanDAC IC2 DIP-switch
mapping stays **bench-pending under `FANDAC-I2C-ADDR-001`**, and **no
hardware / bench / compliance / safety proof is claimed.**

### Preview `.bin` now published — `ROOM-BUNDLE-FAN-PUBLISH-RESULTS-001`

`ROOM-BUNDLE-FAN-PUBLISH-RESULTS-001` records the **successful** `Room-Bundle
Fan Firmware Publish` run
([run `26947595936`](https://github.com/sense360store/esphome-public/actions/runs/26947595936),
`workflow_dispatch` / `dry_run=false`, ref `main`, commit `ad1d957`,
2026-06-04; conclusion **`success`**) that built and attached the five
full-composition room-bundle fan **preview** artifacts —
`Sense360-Ceiling-POE-VentIQ-FanPWM-RoomIQ-v1.0.0-preview.bin`,
`Sense360-Ceiling-POE-VentIQ-FanDAC-RoomIQ-v1.0.0-preview.bin`,
`Sense360-Ceiling-POE-AirIQ-FanRelay-RoomIQ-v1.0.0-preview.bin`,
`Sense360-Ceiling-POE-AirIQ-FanDAC-RoomIQ-v1.0.0-preview.bin`, and
`Sense360-Ceiling-POE-AirIQ-FanPWM-RoomIQ-v1.0.0-preview.bin` — to the shared
`v1.0.0-preview` prerelease (the single preview release for every preview
artifact). See
[`docs/room-bundle-fan-publish-results.md`](room-bundle-fan-publish-results.md)
for the full record (per-asset SHA256 + size, job/step results).

This is **firmware-build / release proof only**. The two FanDAC artifacts were
built **with the IC2 `0x5A` override** — a compile-time configuration only; the
physical S360-312 DIP-switch → I²C address mapping is **not bench verified** and
`FANDAC-I2C-ADDR-001` stays **pending** (see the verification gate
[`docs/hardware/fandac-i2c-address-verification.md`](hardware/fandac-i2c-address-verification.md)).
Publishing a preview `.bin` does **not** make any of the five WebFlash-exposed,
WebFlash-importable, stable, recommended, a customer default, or buyable;
**TRIAC stays excluded under `HW-005`** (no build, no artifact); the stable
Bathroom PoE build (`Ceiling-POE-VentIQ-RoomIQ`) and Simple install are
unchanged; and **no hardware / bench / compliance / safety / commercial proof
is claimed.**

### FanDAC ↔ air-quality I²C address requirement (the two DAC variants)

The S360-312 FanDAC board carries two GP8403 DACs (package defaults IC1 @
`0x58`, IC2 @ `0x59`). Both air-quality modules — **VentIQ (S360-211)** and
**AirIQ (S360-210)** — carry an **SGP41** VOC/NOx sensor at I²C **`0x59`** on
the shared `core_i2c` bus, so the FanDAC default IC2 @ `0x59` **collides**
with the SGP41 in any VentIQ/AirIQ + FanDAC bundle. The
`fandac_conflicts_with_airiq` rule in
[`config/webflash-compatibility.json`](../config/webflash-compatibility.json)
records that collision for AirIQ.

The conflict is **not relaxed** — it is refined to a documented
hardware-address requirement (see `fan_dac_i2c_address_policy` in
[`config/room-bundle-fan-variants.json`](../config/room-bundle-fan-variants.json)):

- **Precise rule:** AirIQ/VentIQ conflict with FanDAC **only** when the
  GP8403 uses `0x59`. With IC2 relocated to `0x5A`, they coexist.
- Both DAC room-bundle bundles set the firmware override
  `fan_dac_2_i2c_address: "0x5A"` (IC1 stays `0x58`). The installer **must**
  set the S360-312 IC2 DIP switch (SW2) so IC2 reports `0x5A` to match.
- **WebFlash one-click stays excluded:** the one-click surface cannot set the
  DIP switch, so AirIQ + FanDAC stays out of the WebFlash
  firmware-combination grammar (`Ceiling-POE-AirIQ-FanDAC-RoomIQ` is
  `webflash_grammar_excluded`); these DAC configs are advanced / manual
  previews only.
- The DIP-position → I²C-address mapping is **not yet bench-verified**;
  `FANDAC-I2C-ADDR-001` owns that follow-up. Its bench verification checklist
  and evidence template live at
  [`docs/hardware/fandac-i2c-address-verification.md`](hardware/fandac-i2c-address-verification.md)
  (see also [`docs/hardware/s360-312-r4-fandac.md`](hardware/s360-312-r4-fandac.md)).

### TRIAC: Bathroom advanced / manual only; no Kitchen TRIAC

`S360-KIT-BATH-P-TRIAC` (`S360-320`, mains phase-cut control) is offered
**only** as an **advanced / manual-warning** preview — never a normal easy /
recommended / default option. It is currently **build-blocked** by `HW-005`
(S360-320 schematic uncommitted; GPIO5/GPIO6 collide with RoomIQ J10 nets;
`ac_dimmer` cannot run across the SX1509 expander), so no preview artifact
can be cut and it is not WebFlash-easy-mode-eligible today. When `HW-005`
resolves it would be delivered only on the advanced-manual-preview lane
behind an explicit mains-risk acknowledgement gate. Stable additionally
requires `PACKAGE-TRIAC-001` + `COMPLIANCE-001`. **No safety / compliance
proof is claimed.** **Kitchen has no TRIAC variant** — kitchen extract
TRIAC is not offered as a recommended / easy option by policy.

### Control types are not interchangeable

Relay, PWM, DAC (0-10V), and TRIAC fan control are electrically distinct
fan-drive methods. A variant built for one control type **cannot be
switched to another at runtime**: the fan-driver board (`S360-310` relay /
`S360-311` PWM / `S360-312` 0-10V / `S360-320` TRIAC) and the firmware must
match the installed fan hardware.

### Identifiers stay separate

Firmware config strings and bundle SKUs **remain separate identifiers**. A
fan-variant bundle SKU (for example `S360-KIT-BATH-P-REL`) names what the
customer would buy; it is **not** a firmware config string and does **not**
imply a committed `config/webflash-builds.json` row. No fan variant is
buyable — every variant is `waitlist-only` (hidden / not buyable), per
[`docs/shop-commercial-source-of-truth.md`](shop-commercial-source-of-truth.md)
§4. The manual-install fan firmware candidates remain tracked in
[`config/manual-firmware-artifacts.json`](../config/manual-firmware-artifacts.json)
/ [`docs/manual-install-fan-candidates.md`](manual-install-fan-candidates.md).

### Kitchen framing

The Kitchen fan variants are framed as **extract / MVHR / EC boost
control** (continuous-extract, heat-recovery boost, or EC-fan speed
control), **not** generic cooker-hood control. The optional Kitchen PWM
variant is policy-gated for **low-voltage / custom** extract use only.

---

## Missing-gate reference

The `Missing gates` column references the gate vocabulary defined in
[`docs/stable-target-expansion-plan.md` § Stable-promotion gate checklist](stable-target-expansion-plan.md#stable-promotion-gate-checklist).
The full vocabulary is summarised here for the reader's convenience;
the source of truth lives in
[`docs/stable-target-expansion-plan.md`](stable-target-expansion-plan.md)
and [`docs/all-yaml-release-matrix.md`](all-yaml-release-matrix.md).

| Gate | Meaning |
|---|---|
| G1 | Top-level canonical product YAML exists under `products/`. |
| G2 | Product-catalog row exists in `config/product-catalog.json`. |
| G3 | Top-level full compile validated in `config/compile-only-targets.json`. |
| G4 | WebFlash wrapper exists under `products/webflash/`. |
| G5 | `artifact_name` present in catalog and `config/webflash-builds.json`. |
| G6 | `config/webflash-builds.json` row exists for the config. |
| G7 | Release notes can be generated without overrides. |
| G8 | No blocking hardware / compliance caveat (per-board / per-package / per-family readiness rows). |
| G9 | Not currently `manual-candidate-only`. |
| G10 | Not currently `preview-only` (preview-to-stable gauntlet closed). |

Every bundle in this matrix (apart from `S360-KIT-BATH-P`) inherits
the shared `PRODUCT-POE-410-001` / `S360-410` schematic verification
chain (Release-One PoE caveat) as part of G8, because every PoE
bundle ships the Sense360 PoE PSU.

---

## Promotion ownership — bundle SKU vs follow-up PR

Adding a bundle SKU to this matrix **does not** authorise the
corresponding firmware config target's promotion to stable or
preview. Promotion is owned by the named follow-up PR in
[`docs/stable-target-expansion-plan.md`](stable-target-expansion-plan.md)
§ Recommended follow-up PR sequence.

| Bundle SKU | Owning follow-up PR (for firmware config promotion) |
|---|---|
| `S360-KIT-BATH-P` | None — `Ceiling-POE-VentIQ-RoomIQ` is already stable. |
| `S360-KIT-KITCHEN-P` | `STABLE-TARGET-AIRIQ-001` → `STABLE-TARGET-AIRIQ-ROOMIQ-001` (after PoE-410 closure). |
| `S360-KIT-LIVING-P` | `LED-STABLE-PROMOTION-001` (alias of `RELEASE-007` / `PRODUCT-LED-STABLE-001`), plus a separate `STABLE-TARGET-ROOMIQ-LED-001`-style slice (not yet scoped) for the no-VentIQ LED variant. Not approved by this PR. |
| `S360-KIT-BEDROOM-P` | `STABLE-TARGET-CORE-001` → `STABLE-TARGET-ROOMIQ-001`. |
| `S360-KIT-CORRIDOR-P` | Same as `S360-KIT-LIVING-P` until a corridor-specific firmware config differentiates them. |

These follow-up PRs are **not** approved or scoped by this PR.

---

## Hard guardrails

- **Bundle SKU is not a board SKU.** Bundle SKUs live in
  [`config/room-bundle-skus.json`](../config/room-bundle-skus.json) and
  reference board SKUs by their canonical
  [`config/hardware-catalog.json`](../config/hardware-catalog.json)
  identifier. The bundle SKU itself is **not** added to the hardware
  catalog.
- **Bundle SKU is not a firmware config string.** Bundle SKUs do not
  appear in
  [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json)
  or
  [`config/webflash-builds.json`](../config/webflash-builds.json). The
  bundle's `likely_firmware_config_target` field points at the firmware
  config string that the included boards would produce; it is not the
  bundle SKU.
- **Bundle SKU is not a release artifact name.** Release artifact names
  follow the
  `Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin` shape derived
  from the firmware config string, not from the bundle SKU.
- **Every bundle includes Core and PoE PSU.** Every row's
  `included_board_skus` must contain `S360-100` and `S360-410`. The
  contract test asserts this.
- **LED bundles are not stable.** Any bundle whose
  `likely_firmware_config_target` contains the `LED` token (or whose
  `included_board_skus` contains `S360-300`) is `preview-candidate` or
  `preview-release` at most; never `stable-release` or
  `stable-candidate`. The contract test asserts this.
- **No fan bundles in this PR.** No bundle's `included_board_skus` may
  contain `S360-310`, `S360-311`, `S360-312`, or `S360-320`. The
  contract test asserts this. Fan bundles are owned by their own
  per-family follow-up PR sequences (`WEBFLASH-RELAY-001` /
  `WEBFLASH-PWM-001` / `WEBFLASH-DAC-001` / FanTRIAC HW-005 chain).
- **Bundle SKU names do not become release artifact names
  automatically.** The release artifact name is derived from the
  firmware config string per
  [`docs/all-yaml-release-matrix.md`](all-yaml-release-matrix.md) §
  Stable-promotion criteria G5; this PR adds no `artifact_name` to any
  product.
- **Bundle SKUs are unique.** The contract test asserts this.

---

## Relationship to the kit intent matrix

The earlier productized kit-intent matrix
([`docs/kit-intent-matrix.md`](kit-intent-matrix.md) /
[`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json),
KIT-MATRIX-001 / PR #542) groups boards by **use case** (`bathroom`,
`kitchen-or-duct-fan`) and uses the `S360-KIT-*-POE` / `S360-KIT-*-LED`
/ `S360-KIT-*-RELAY` / `S360-KIT-*-TRIAC` / `S360-KIT-DUCT-*` naming
convention for the planning-time kit-intent rows.

This document and
[`config/room-bundle-skus.json`](../config/room-bundle-skus.json) add
the **commercial room-bundle** layer that uses the `S360-KIT-{ROOM}-P`
naming convention (the `-P` suffix denotes the PoE-powered room
bundle). The two layers are complementary:

- **Kit intent matrix** (`config/kit-intent-matrix.json`) — planning /
  productization intent across the firmware combination matrix; six
  rows today including non-PoE / fan / TRIAC futures.
- **Room bundle SKU matrix** (`config/room-bundle-skus.json`, this PR)
  — sellable PoE-only room bundle SKUs; five rows today; restricted to
  the Core + RoomIQ + (optional VentIQ / AirIQ / LED) + PoE PSU
  combinations.

Neither layer implies WebFlash exposure or release readiness on its
own; both defer to
[`config/webflash-builds.json`](../config/webflash-builds.json) and
the WebFlash manifest for installability, and to
[`docs/stable-target-expansion-plan.md`](stable-target-expansion-plan.md)
for promotion ownership.

---

## Validation

The matrix is reproduced and locked in by:

- `python3 tests/test_room_bundle_skus.py` — bundle SKU contract tests
  (uniqueness; included boards reference valid known board SKUs; every
  bundle has at least Core and PoE PSU; LED bundles are not marked
  stable while LED remains preview; no fan bundle SKUs are introduced
  by this PR; bundle SKU names do not become release artifact names
  automatically).
- `python3 scripts/classify_all_yaml_release_matrix.py --summary` —
  unchanged: `stable=1, preview=1, manual=3, compile-only=7, blocked=1,
  not-a-product-entrypoint=35`.
- `python3 scripts/list_release_targets.py` — unchanged: two rows,
  stable `Ceiling-POE-VentIQ-RoomIQ`, preview
  `Ceiling-POE-VentIQ-RoomIQ-LED`.
- `python3 tests/test_all_yaml_release_matrix.py` — unchanged.
- `python3 tests/test_release_product_selection.py` — unchanged.
- `python3 tests/validate_configs.py` — unchanged.
- `python3 scripts/validate_compile_targets.py --metadata-only` —
  unchanged.
- `python3 tests/validate_webflash_builds.py` — unchanged.
- `python3 tests/test_product_catalog.py` — unchanged.
- `python3 -m unittest discover -s tests -p "test_*.py"` — full suite
  passes; bundle SKU contract tests added by this PR.

---

## Cross-references

- All-YAML release matrix:
  [`docs/all-yaml-release-matrix.md`](all-yaml-release-matrix.md) —
  STABLE-RELEASE-MATRIX-ALL-YAML-001. Source of truth for the release
  class (`stable-release` / `preview-release` / `manual-candidate-only`
  / `compile-only` / `blocked` / `not-a-product-entrypoint`) the
  bundle's likely firmware config target carries.
- Stable target expansion plan:
  [`docs/stable-target-expansion-plan.md`](stable-target-expansion-plan.md)
  — STABLE-TARGET-EXPANSION-PLAN-001. Source of truth for the G1–G10
  gate vocabulary and the named `STABLE-TARGET-*-001` follow-up PR
  sequence that owns each non-stable bundle's firmware config target
  promotion.
- Room firmware release matrix:
  [`docs/room-firmware-release-matrix.md`](room-firmware-release-matrix.md)
  — RELEASE-PIPELINE-ROOM-MATRIX-001. Source of truth for the
  per-room-firmware release pipeline status of each likely firmware
  config target.
- Kit intent matrix:
  [`docs/kit-intent-matrix.md`](kit-intent-matrix.md) — KIT-MATRIX-001.
  Sibling layer; productization / use-case planning rather than
  sellable room bundles.
- Product readiness gate:
  [`docs/product-readiness-matrix.md`](product-readiness-matrix.md) —
  PRODUCT-GAP-001. Product-layer readiness this matrix consults.
- WebFlash exposure gate:
  [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md)
  — WEBFLASH-GAP-001.
- Release artifact gate:
  [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md)
  — RELEASE-GAP-001.
- Preview-to-stable gauntlet:
  [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md)
  — RELEASE-006.
- LED preview decision:
  [`docs/product-led-preview-decision.md`](product-led-preview-decision.md).
- Hardware catalog:
  [`config/hardware-catalog.json`](../config/hardware-catalog.json) /
  [`docs/hardware-catalog.md`](hardware-catalog.md). Source of truth
  for the canonical board SKUs the bundles reference.
- Firmware combination matrix:
  [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json).
  Source of truth for the firmware config strings the bundles' likely
  firmware config target references.
- WebFlash builds matrix:
  [`config/webflash-builds.json`](../config/webflash-builds.json).
  Sole source of release eligibility; unchanged by this PR.
- Shipping configuration: [`docs/release-one.md`](release-one.md).
- Commercial / shop source of truth:
  [`docs/shop-commercial-source-of-truth.md`](shop-commercial-source-of-truth.md)
  / [`config/shop-commercial-source-of-truth.json`](../config/shop-commercial-source-of-truth.json)
  — SHOP-COMMERCIAL-SOURCE-OF-TRUTH-001. Launch SKU, shop posture,
  candidate-bundle visibility, customer WebFlash URL, and approved claims.

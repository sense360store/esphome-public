# R4 v1 Product Matrix and Gap Analysis (V1-R4-PRODUCT-GAP-001)

## Purpose and scope

This document establishes **what the Sense360 R4 v1 product line should
be**, measures that target against **what exists today**, and produces
the **authoring queue** for the gap. It does three things and nothing
more:

1. Derives the **target R4 v1 firmware config-string matrix** from the
   sellable-kit sources — [`config/room-bundle-skus.json`](../config/room-bundle-skus.json),
   [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json),
   and [`config/hardware-catalog.json`](../config/hardware-catalog.json).
2. Gap-analyses each target config string against the existing
   [`config/product-catalog.json`](../config/product-catalog.json),
   [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json),
   and [`config/webflash-builds.json`](../config/webflash-builds.json),
   classifies the gap action, and flags which of the 21 surviving
   `legacy-compatible` `sense360-core-*` / `sense360-fan-pwm` /
   `sense360-poe` YAMLs are usable as authoring templates.
3. Sets the `core-c` / `core-v` / `core-w` disposition and orders the
   `V1-R4-CREATE-*` authoring queue.

### This document is documentation only

V1-R4-PRODUCT-GAP-001 — this PR — **does not**:

- create or edit any product YAML under [`products/`](../products/),
  any WebFlash wrapper under [`products/webflash/`](../products/webflash/),
  or any compile-only skeleton under
  [`products/compile-only/`](../products/compile-only/);
- add any config string to, or otherwise modify,
  [`config/product-catalog.json`](../config/product-catalog.json);
- add or modify any entry in
  [`config/webflash-builds.json`](../config/webflash-builds.json), any
  `artifact_name`, or any `webflash_build_matrix` value;
- change any board `schematic_status` in
  [`config/hardware-catalog.json`](../config/hardware-catalog.json);
- change any product lifecycle status — including the 21 surviving
  `legacy-compatible` entries and the 10 `removed` Mini tombstones;
- remove any product, promote anything, mark `S360-410` verified, or
  close any fan blocker;
- modify `manifest.json` or [`firmware/sources.json`](../firmware/sources.json);
- fabricate any combination, readiness, or evidence.

Every config JSON stays byte-identical. The only files this PR writes
are this document and [`UPCOMING_PR.md`](../UPCOMING_PR.md).

## Method

### Sellable-kit sources

| Source | Layer | What it grounds |
|---|---|---|
| [`config/room-bundle-skus.json`](../config/room-bundle-skus.json) | Commercial **room-bundle SKU** (PoE-only, `-P` suffix) | The five sellable PoE room kits and each kit's `likely_firmware_config_target`. |
| [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json) | Productization **kit intent** (use-case) | Per-kit module composition, including the bathroom LED preview kit and the fan futures. |
| [`config/hardware-catalog.json`](../config/hardware-catalog.json) | **Board SKU** | Per-board `schematic_status`. |

### Enumeration axes

For each sellable kit the target config strings are enumerated across:

- **Power option** — `POE` (the kit-default; every room bundle ships the
  Sense360 PoE PSU `S360-410`) and `USB` (the power-axis variant of the
  same Core + sensor stack, self-powered over the Core's ESP32-S3 USB-C
  with no PSU board — the `Ceiling-USB-*` lane is grammar-valid in
  [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json)
  and is the R4 successor of the legacy `sense360-core-c-usb` YAML).
- **Sensor module** — `VentIQ` (`S360-211`), `AirIQ` (`S360-210`),
  `RoomIQ` (`S360-200`), and `LED` (`S360-300`).

**The sensor composition of every row is grounded in a kit.** No sensor
combination that no kit requires is invented. The `PWR` (mains/240V)
power token and the fan tokens (`FanRelay` / `FanPWM` / `FanDAC` /
`FanTRIAC`) are deliberately **excluded** — see
[Out of v1 scope](#out-of-v1-scope).

### Power-axis honesty note

The commercial room-bundle layer is **PoE-only** (every bundle includes
`S360-410`; see [`docs/sense360-room-bundles.md`](sense360-room-bundles.md)).
There is **no USB room bundle**. The `USB` rows below are therefore
enumerated as the requested power-axis variant of each kit's
kit-grounded sensor stack; their **sensor composition** is kit-grounded,
but their **power token** is not backed by a sellable bundle SKU. They
are flagged accordingly and their `target v1 channel` is
**manual / custom**, not a kit channel.

### Kit → sensor-stack derivation

| Sellable kit | Source | Sensor stack | PoE config string | USB config string |
|---|---|---|---|---|
| `S360-KIT-BATH-P` / `S360-KIT-BATH-POE` | room-bundle + kit-intent | VentIQ + RoomIQ | `Ceiling-POE-VentIQ-RoomIQ` | `Ceiling-USB-VentIQ-RoomIQ` |
| `S360-KIT-BATH-POE-LED` | kit-intent (preview kit) | VentIQ + RoomIQ + LED | `Ceiling-POE-VentIQ-RoomIQ-LED` | `Ceiling-USB-VentIQ-RoomIQ-LED` |
| `S360-KIT-KITCHEN-P` | room-bundle | AirIQ + RoomIQ | `Ceiling-POE-AirIQ-RoomIQ` | `Ceiling-USB-AirIQ-RoomIQ` |
| `S360-KIT-LIVING-P` + `S360-KIT-CORRIDOR-P` | room-bundle | RoomIQ + LED | `Ceiling-POE-RoomIQ-LED` | `Ceiling-USB-RoomIQ-LED` |
| `S360-KIT-BEDROOM-P` | room-bundle | RoomIQ | `Ceiling-POE-RoomIQ` | `Ceiling-USB-RoomIQ` |

Living and Corridor share the same board set (`RoomIQ + LED`) and the
same config string until a future room-specific default differentiates
them; they are one target row here.

All R4 boards are **ceiling-group** (`group: Ceiling` in the hardware
catalog) and every kit mounts the Core on the ceiling, so every target
row carries the `Ceiling` mount token.

## Target-vs-existing gap matrix

`schematic_status` is shown per underlying board. The only
not-`verified` board in the entire target set is the PoE PSU `S360-410`
(`cataloged_unverified`); USB rows carry no PSU board.

| Target config string | Source kit(s) | Required modules (boards) | Per-board `schematic_status` | mains / SELV / blocked | Exists today | Gap action | Target v1 channel | Authoring PR |
|---|---|---|---|---|---|---|---|---|
| `Ceiling-POE-VentIQ-RoomIQ` | `S360-KIT-BATH-P` | Core `S360-100`, VentIQ `S360-211`, RoomIQ `S360-200`, PoE `S360-410` | 100✅ 211✅ 200✅ 410⚠️`cataloged_unverified` | SELV | **yes** — `production` / `stable` (`webflash-shipping`) | **already-shipping** (Release-One) | `stable` (live) | n/a |
| `Ceiling-POE-VentIQ-RoomIQ-LED` | `S360-KIT-BATH-POE-LED` | Core, VentIQ, RoomIQ, LED `S360-300`, PoE `S360-410` | 100✅ 211✅ 200✅ 300✅ 410⚠️ | SELV | **yes** — `preview` / `preview` (`webflash-preview`) | **promote-existing** — product exists; stable promotion is LED-gauntlet-owned, not an authoring task | `preview` (live); stable = LED gauntlet | n/a |
| `Ceiling-POE-AirIQ-RoomIQ` | `S360-KIT-KITCHEN-P` | Core, AirIQ `S360-210`, RoomIQ, PoE `S360-410` | 100✅ 210✅ 200✅ 410⚠️ | SELV | **no** — `missing-product-yaml`; compile-only skeleton [`ceiling-poe-airiq-roomiq.yaml`](../products/compile-only/ceiling-poe-airiq-roomiq.yaml) exists | **AUTHOR-NEW** + **blocked-by-evidence** (`S360-410` schematic / `PRODUCT-POE-410-001`; AirIQ-stack hardware evidence SPS30/SGP41/SCD41/BMP390) | `stable-candidate` (owned `STABLE-TARGET-AIRIQ-ROOMIQ-001`) | **V1-R4-CREATE-002** |
| `Ceiling-POE-RoomIQ-LED` | `S360-KIT-LIVING-P`, `S360-KIT-CORRIDOR-P` | Core, RoomIQ, LED `S360-300`, PoE `S360-410` | 100✅ 200✅ 300✅ 410⚠️ | SELV | **no** — `missing-product-yaml`; no compile-only skeleton | **AUTHOR-NEW** + **blocked-by-evidence** (`S360-410`); LED preview-gated | `preview-candidate` (LED gauntlet / `STABLE-TARGET-ROOMIQ-LED-001`) | **V1-R4-CREATE-003** |
| `Ceiling-POE-RoomIQ` | `S360-KIT-BEDROOM-P` | Core, RoomIQ, PoE `S360-410` | 100✅ 200✅ 410⚠️ | SELV | **no** — `missing-product-yaml`; compile-only skeleton [`ceiling-poe-roomiq.yaml`](../products/compile-only/ceiling-poe-roomiq.yaml) exists | **AUTHOR-NEW** + **blocked-by-evidence** (`S360-410`) | `stable-candidate` (owned `STABLE-TARGET-ROOMIQ-001`) | **V1-R4-CREATE-001** |
| `Ceiling-USB-VentIQ-RoomIQ` | `S360-KIT-BATH-P` (USB power-variant) | Core, VentIQ `S360-211`, RoomIQ | 100✅ 211✅ 200✅ | SELV (USB-C) | **yes** — **authored** by V1-R4-CREATE-004 (`status: compile-only`, `target_channel: manual-custom`) | **AUTHORED** (all boards verified; no evidence blocker) | manual / custom (no USB bundle) | **V1-R4-CREATE-004** ✅ |
| `Ceiling-USB-RoomIQ` | `S360-KIT-BEDROOM-P` (USB power-variant) | Core, RoomIQ | 100✅ 200✅ | SELV (USB-C) | **yes** — **authored** by V1-R4-CREATE-004 (`status: compile-only`, `target_channel: manual-custom`) | **AUTHORED** (all boards verified) | manual / custom (no USB bundle) | **V1-R4-CREATE-004** ✅ |
| `Ceiling-USB-AirIQ-RoomIQ` | `S360-KIT-KITCHEN-P` (USB power-variant) | Core, AirIQ `S360-210`, RoomIQ | 100✅ 210✅ 200✅ | SELV (USB-C) | **no** — `missing-product-yaml` | **AUTHOR-NEW** + **blocked-by-evidence** (AirIQ-stack hardware evidence; **not** `S360-410`) | manual / custom (no USB bundle) | **V1-R4-CREATE-005** |
| `Ceiling-USB-VentIQ-RoomIQ-LED` | `S360-KIT-BATH-POE-LED` (USB power-variant) | Core, VentIQ, RoomIQ, LED `S360-300` | 100✅ 211✅ 200✅ 300✅ | SELV (USB-C) | **no** — `missing-product-yaml` | **AUTHOR-NEW**; LED preview-gated | manual / custom (no USB bundle); LED preview | **V1-R4-CREATE-006** |
| `Ceiling-USB-RoomIQ-LED` | `S360-KIT-LIVING-P`, `S360-KIT-CORRIDOR-P` (USB power-variant) | Core, RoomIQ, LED `S360-300` | 100✅ 200✅ 300✅ | SELV (USB-C) | **no** — `missing-product-yaml`; no compile-only skeleton | **AUTHOR-NEW**; LED preview-gated | manual / custom (no USB bundle); LED preview | **V1-R4-CREATE-006** |

Legend: ✅ = `verified`; ⚠️ = `cataloged_unverified`. SELV = safety
extra-low voltage (PoE delivers an isolated 5 V SELV rail; USB-C is 5 V
SELV). **No** target row is mains-powered and **no** target row is
`blocked` — the fan and 240V-PSU tokens that carry the mains / HW-005 /
compliance blockers are out of v1 scope.

### Gap-action tally

- **already-shipping:** 1 (`Ceiling-POE-VentIQ-RoomIQ`).
- **promote-existing:** 1 (`Ceiling-POE-VentIQ-RoomIQ-LED`, LED-gauntlet
  owned — no authoring needed).
- **AUTHOR-NEW:** 8 config strings (3 PoE sellable-kit + 5 USB
  power-variant), batched into **6** `V1-R4-CREATE-*` authoring PRs.
- **blocked-by-evidence** (overlay on the above): every PoE AUTHOR-NEW
  row needs the `S360-410` schematic-verification chain
  (`PRODUCT-POE-410-001`); the two AirIQ rows additionally need the
  AirIQ-stack hardware evidence. `Ceiling-POE-VentIQ-RoomIQ` is the one
  PoE config that already cleared its `S360-410` caveat through the
  Release-One hardware audit.

The `S360-410` schematic-verification gate is shared by **every** PoE
row (the Release-One PoE caveat). Authoring a top-level product YAML +
catalog row + compile-only validation can proceed for these rows, but
**stable/preview promotion** is held behind the evidence gate and is
owned by the named `STABLE-TARGET-*` / LED-gauntlet follow-ups — not by
the `V1-R4-CREATE-*` authoring slices.

## AUTHOR-NEW set — template-source flags

For each AUTHOR-NEW row, the 21 surviving `legacy-compatible` YAMLs were
checked for a usable authoring template (same **mount** + **power** +
**sensor intent**). The legacy ceiling Core YAMLs are the reusable set;
the R4-native compile-only skeletons under
[`products/compile-only/`](../products/compile-only/) are the preferred
primary reference where one already exists.

| AUTHOR-NEW config string | Legacy template-source (mount/power) | Legacy template-source (sensor intent) | R4 compile-only reference | Notes |
|---|---|---|---|---|
| `Ceiling-POE-AirIQ-RoomIQ` | [`sense360-core-c-poe.yaml`](../products/sense360-core-c-poe.yaml) (ceiling + PoE) | [`sense360-core-ceiling.yaml`](../products/sense360-core-ceiling.yaml) (AirIQ + Comfort + Presence) | [`ceiling-poe-airiq-roomiq.yaml`](../products/compile-only/ceiling-poe-airiq-roomiq.yaml) ✅ | RoomIQ = the R4 merge of legacy Comfort + Presence. |
| `Ceiling-POE-RoomIQ-LED` | `sense360-core-c-poe.yaml` (ceiling + PoE) | [`sense360-core-ceiling-presence.yaml`](../products/sense360-core-ceiling-presence.yaml) (presence + LED ring) | — (none; author skeleton too) | No compile-only skeleton exists yet; LED preview-gated. |
| `Ceiling-POE-RoomIQ` | `sense360-core-c-poe.yaml` (ceiling + PoE) | `sense360-core-ceiling-presence.yaml` (drop LED) | [`ceiling-poe-roomiq.yaml`](../products/compile-only/ceiling-poe-roomiq.yaml) ✅ | Smallest RoomIQ-only stack. |
| `Ceiling-USB-VentIQ-RoomIQ` | [`sense360-core-c-usb.yaml`](../products/sense360-core-c-usb.yaml) (ceiling + USB) | [`sense360-core-ceiling-bathroom.yaml`](../products/sense360-core-ceiling-bathroom.yaml) (bathroom air-quality = VentIQ intent) | [`ceiling-poe-ventiq.yaml`](../products/compile-only/ceiling-poe-ventiq.yaml) (power differs) | Legacy "Bathroom" module is VentIQ in the WebFlash taxonomy. |
| `Ceiling-USB-RoomIQ` | `sense360-core-c-usb.yaml` (ceiling + USB) | `sense360-core-ceiling-presence.yaml` (drop LED) | `ceiling-poe-roomiq.yaml` (power differs) | All boards verified. |
| `Ceiling-USB-AirIQ-RoomIQ` | `sense360-core-c-usb.yaml` (ceiling + USB) | `sense360-core-ceiling.yaml` (AirIQ) | `ceiling-poe-airiq-roomiq.yaml` (power differs) | AirIQ-stack hardware evidence gate carries over. |
| `Ceiling-USB-VentIQ-RoomIQ-LED` | `sense360-core-c-usb.yaml` (ceiling + USB) | `sense360-core-ceiling-bathroom.yaml` (+ LED ring) | — | LED preview-gated. |
| `Ceiling-USB-RoomIQ-LED` | `sense360-core-c-usb.yaml` (ceiling + USB) | `sense360-core-ceiling-presence.yaml` (presence + LED) | — | LED preview-gated; no compile-only skeleton. |

**Template caveat.** A legacy template-source is a *starting shape for
authoring* (mount + power + sensor intent), **not** a drop-in: the
legacy YAMLs predate the R4 module taxonomy (RoomIQ merge, VentIQ /
AirIQ rename) and the canonical `core_i2c` bus. Each `V1-R4-CREATE-*`
slice owns the actual reconciliation against the current packages.

## `core-c` / `core-v` / `core-w` disposition

All 21 surviving `legacy-compatible` entries, mapped to YAML, with a
**recommendation** (this PR changes **no** status). Any retirement runs
through the [`PRODUCT-DEP-001`](product-deprecation-removal-policy.md)
`legacy-compatible -> removed` (intentional-retirement) transition —
these were never WebFlash-shippable, so no `deprecated` step is required
(the same path PRODUCT-DEP-MINI-001 used for the Mini range). The
recommended removals are pointed at the follow-up
**`PRODUCT-DEP-CORE-001`** (already queued; the deprecation-series
sibling of `PRODUCT-DEP-MINI-001`, **distinct** from the unrelated
toolchain item `PRODUCT-DEP-002`).

### Ceiling Core family (6) — `PRODUCT-DEP-CORE-001` scope

| Entry | YAML | Recommendation | Rationale |
|---|---|---|---|
| `sense360-core-c-poe` | [`sense360-core-c-poe.yaml`](../products/sense360-core-c-poe.yaml) | **keep-as-template** | Ceiling + PoE base; template for the PoE AUTHOR-NEW rows. |
| `sense360-core-c-usb` | [`sense360-core-c-usb.yaml`](../products/sense360-core-c-usb.yaml) | **keep-as-template** | Ceiling + USB base; template for the USB AUTHOR-NEW rows. |
| `sense360-core-ceiling` | [`sense360-core-ceiling.yaml`](../products/sense360-core-ceiling.yaml) | **keep-as-template** | Full AirIQ ceiling stack; template for `*-AirIQ-RoomIQ`. |
| `sense360-core-ceiling-bathroom` | [`sense360-core-ceiling-bathroom.yaml`](../products/sense360-core-ceiling-bathroom.yaml) | **keep-as-template** | Bathroom (VentIQ-intent) ceiling stack; template for `*-VentIQ-RoomIQ(-LED)`. |
| `sense360-core-ceiling-presence` | [`sense360-core-ceiling-presence.yaml`](../products/sense360-core-ceiling-presence.yaml) | **keep-as-template** | Presence (+LED) ceiling stack; template for `*-RoomIQ(-LED)`. |
| `sense360-core-c-pwr` | [`sense360-core-c-pwr.yaml`](../products/sense360-core-c-pwr.yaml) | **retire** (→ `PRODUCT-DEP-CORE-001`) | Ceiling **mains/240V**; no v1 reuse — `PWR` is compliance-blocked and `S360-400` is `cataloged_unverified`; no mains v1 kit. |

### Wall Core family (5) — `PRODUCT-DEP-CORE-001` scope

R4 v1 is **ceiling-only** (every room bundle mounts the Core on the
ceiling). No v1 kit is wall-mounted, so none of these has a v1-R4 reuse.

| Entry | YAML | Recommendation | Rationale |
|---|---|---|---|
| `sense360-core-w-poe` | [`sense360-core-w-poe.yaml`](../products/sense360-core-w-poe.yaml) | **retire** (→ `PRODUCT-DEP-CORE-001`) | Wall mount; no v1 ceiling reuse. |
| `sense360-core-w-pwr` | [`sense360-core-w-pwr.yaml`](../products/sense360-core-w-pwr.yaml) | **retire** (→ `PRODUCT-DEP-CORE-001`) | Wall + mains; no v1 reuse. |
| `sense360-core-w-usb` | [`sense360-core-w-usb.yaml`](../products/sense360-core-w-usb.yaml) | **retire** (→ `PRODUCT-DEP-CORE-001`) | Wall mount; no v1 ceiling reuse. |
| `sense360-core-wall` | [`sense360-core-wall.yaml`](../products/sense360-core-wall.yaml) | **retire** (→ `PRODUCT-DEP-CORE-001`) | Full wall stack; no v1 ceiling reuse. |
| `sense360-core-wall-presence` | [`sense360-core-wall-presence.yaml`](../products/sense360-core-wall-presence.yaml) | **retire** (→ `PRODUCT-DEP-CORE-001`) | Presence-only wall; no v1 ceiling reuse. |

If an R4 wall product line is ever scoped, these revive as templates;
that is a future decision, not a v1-R4 reuse.

### Core Voice family (8) — `PRODUCT-DEP-CORE-001` scope

R4 has **no voice module** in the hardware catalog (Core / RoomIQ /
AirIQ / VentIQ / LED / fan drivers / PSU only) and **no voice kit**.
None has a v1-R4 reuse.

| Entry | YAML | Recommendation | Rationale |
|---|---|---|---|
| `sense360-core-v-c-poe` | [`sense360-core-v-c-poe.yaml`](../products/sense360-core-v-c-poe.yaml) | **retire** (→ `PRODUCT-DEP-CORE-001`) | Voice ceiling + PoE; no R4 voice module. |
| `sense360-core-v-c-pwr` | [`sense360-core-v-c-pwr.yaml`](../products/sense360-core-v-c-pwr.yaml) | **retire** (→ `PRODUCT-DEP-CORE-001`) | Voice ceiling + mains; no R4 voice module. |
| `sense360-core-v-c-usb` | [`sense360-core-v-c-usb.yaml`](../products/sense360-core-v-c-usb.yaml) | **retire** (→ `PRODUCT-DEP-CORE-001`) | Voice ceiling + USB; no R4 voice module. |
| `sense360-core-v-w-poe` | [`sense360-core-v-w-poe.yaml`](../products/sense360-core-v-w-poe.yaml) | **retire** (→ `PRODUCT-DEP-CORE-001`) | Voice wall + PoE; no R4 voice module. |
| `sense360-core-v-w-pwr` | [`sense360-core-v-w-pwr.yaml`](../products/sense360-core-v-w-pwr.yaml) | **retire** (→ `PRODUCT-DEP-CORE-001`) | Voice wall + mains; no R4 voice module. |
| `sense360-core-v-w-usb` | [`sense360-core-v-w-usb.yaml`](../products/sense360-core-v-w-usb.yaml) | **retire** (→ `PRODUCT-DEP-CORE-001`) | Voice wall + USB; no R4 voice module. |
| `sense360-core-voice-ceiling` | [`sense360-core-voice-ceiling.yaml`](../products/sense360-core-voice-ceiling.yaml) | **retire** (→ `PRODUCT-DEP-CORE-001`) | Full voice ceiling (LED+MIC ring); no R4 voice module. |
| `sense360-core-voice-wall` | [`sense360-core-voice-wall.yaml`](../products/sense360-core-voice-wall.yaml) | **retire** (→ `PRODUCT-DEP-CORE-001`) | Full voice wall (LED+MIC ring); no R4 voice module. |

### Standalone legacy (2) — **outside** `PRODUCT-DEP-CORE-001` scope

These are not `sense360-core-*` and `PRODUCT-DEP-CORE-001` is scoped to
the core family only. They also have a dedicated disposition in
[`docs/product-readiness-matrix.md`](product-readiness-matrix.md)
(`legacy-only`).

| Entry | YAML | Recommendation | Rationale |
|---|---|---|---|
| `sense360-fan-pwm` | [`sense360-fan-pwm.yaml`](../products/sense360-fan-pwm.yaml) | **keep `legacy-compatible`** (no v1 template) | The R4 FanPWM is the separate `Ceiling-POE-FanPWM` product YAML (`hardware-pending`); the legacy 4-channel accessory stays `legacy-compatible` per the readiness matrix and is **not** the FanPWM candidate. Any future retirement is its own slice, not `PRODUCT-DEP-CORE-001`. |
| `sense360-poe` | [`sense360-poe.yaml`](../products/sense360-poe.yaml) | **keep `legacy-compatible`** (no v1 template) | Legacy single-purpose PoE network controller; superseded by R4 PoE handling but kept for manual users per the readiness matrix. Disposition separate from `PRODUCT-DEP-CORE-001`. |

### Disposition summary

- **keep-as-template (5):** the ceiling Core PoE/USB bases + the three
  ceiling sensor-stack configs.
- **retire via `PRODUCT-DEP-CORE-001` (14):** `core-c-pwr` + the 5 wall
  + the 8 voice entries (no ceiling-v1 reuse).
- **keep `legacy-compatible`, outside scope (2):** `sense360-fan-pwm`,
  `sense360-poe`.

`PRODUCT-DEP-CORE-001` governs the 19 `sense360-core-*` entries (5 keep
+ 14 retire). It changes no status here; the retirements run through the
`PRODUCT-DEP-001` gates.

## Ordered authoring queue

The `V1-R4-CREATE-*` series authors the AUTHOR-NEW set, batched
review-sized. Each slice produces the **top-level product YAML + catalog
row + compile-only validation only**; channel **promotion** stays owned
by the named `STABLE-TARGET-*` / LED-gauntlet follow-ups and is held
behind the relevant evidence gate.

| Order | Authoring PR | Config string(s) | Required modules | Template source | Target v1 channel |
|---|---|---|---|---|---|
| 1 | **V1-R4-CREATE-001** ✅ **authored** (2026-05-29) | `Ceiling-POE-RoomIQ` | Core + RoomIQ + PoE | `core-c-poe` + `core-ceiling-presence`; compile-only `ceiling-poe-roomiq.yaml` | `stable-candidate` (`STABLE-TARGET-ROOMIQ-001`; `S360-410`-gated) |
| 2 | **V1-R4-CREATE-002** | `Ceiling-POE-AirIQ-RoomIQ` | Core + AirIQ + RoomIQ + PoE | `core-c-poe` + `core-ceiling`; compile-only `ceiling-poe-airiq-roomiq.yaml` | `stable-candidate` (`STABLE-TARGET-AIRIQ-ROOMIQ-001`; `S360-410` + AirIQ-stack-gated) |
| 3 | **V1-R4-CREATE-003** | `Ceiling-POE-RoomIQ-LED` | Core + RoomIQ + LED + PoE | `core-c-poe` + `core-ceiling-presence` (no compile-only skeleton yet) | `preview-candidate` (LED gauntlet; `S360-410`-gated) |
| 4 | **V1-R4-CREATE-004** ✅ **authored** (2026-05-30) | `Ceiling-USB-VentIQ-RoomIQ`, `Ceiling-USB-RoomIQ` | Core + RoomIQ (+ VentIQ) | `core-c-usb` + `core-ceiling-bathroom` / `core-ceiling-presence`; board packages + `power_usb` | manual / custom (all boards verified; no evidence blocker) |
| 5 | **V1-R4-CREATE-005** | `Ceiling-USB-AirIQ-RoomIQ` | Core + AirIQ + RoomIQ | `core-c-usb` + `core-ceiling` | manual / custom (AirIQ-stack-gated) |
| 6 | **V1-R4-CREATE-006** | `Ceiling-USB-VentIQ-RoomIQ-LED`, `Ceiling-USB-RoomIQ-LED` | Core + RoomIQ + LED (+ VentIQ) | `core-c-usb` + `core-ceiling-bathroom` / `core-ceiling-presence` | manual / custom; LED preview-gated |

**Ordering rationale.** The three PoE sellable-kit gaps (CREATE-001..003)
come first because they directly back the Kitchen / Living / Corridor /
Bedroom room bundles; the smallest RoomIQ-only stack is authored first so
the AirIQ and LED stacks build on a validated base. The USB
power-variants (CREATE-004..006) follow because no sellable USB bundle
exists; within them the unblocked non-LED pair leads, the AirIQ
evidence-gated row is next, and the LED preview-gated pair is last.

### Authoring status (updates)

- **2026-05-29 — `V1-R4-CREATE-001` authored.** The `Ceiling-POE-RoomIQ`
  product (the `S360-KIT-BEDROOM-P` firmware) is now authored as a full,
  complete product config at
  [`products/sense360-ceiling-poe-roomiq.yaml`](../products/sense360-ceiling-poe-roomiq.yaml)
  (Core ceiling `S360-100` + canonical `core_i2c` bus + PoE PSU `S360-410`
  + RoomIQ `S360-200` = `comfort_ceiling` + `presence_ceiling`; no AirIQ, no
  VentIQ, no fan, no LED — matching the structure of the working
  [`sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml)
  with VentIQ removed). A matching catalog row exists in
  [`config/product-catalog.json`](../config/product-catalog.json)
  (`status: blocked`, `blocker: PRODUCT-POE-410-001`,
  `webflash_build_matrix: false`, no `artifact_name`, no `webflash_wrapper`,
  `target_channel: stable-candidate`) and the top-level product YAML is
  registered as the compile-only target `ceiling-poe-roomiq-product-compile-only`
  in [`config/compile-only-targets.json`](../config/compile-only-targets.json)
  (`compile_validation_status: pending-ci` — ESPHome was unavailable in the
  authoring environment, so no full compile was run and none is fabricated; a
  CI `--compile` run is owed). The product is **authored and release-blocked**,
  nothing more: it is **not** WebFlash-exposed, **not** production / preview /
  verified / release-ready; `S360-410` stays `cataloged_unverified` and the
  Release-One PoE caveat (`PRODUCT-POE-410-001`) is unchanged; stable promotion
  stays owned by `STABLE-TARGET-ROOMIQ-001` behind the shared `S360-410`
  evidence gate. **CREATE-002..006 stay queued.** `S360-410` remains the
  release gate for every PoE author-new row.

- **2026-05-30 — `V1-R4-CREATE-004` authored the two USB sensor configs.**
  The two unblocked R4 USB sensor configs — `Ceiling-USB-VentIQ-RoomIQ` (the
  `S360-KIT-BATH-P` USB power-variant) and `Ceiling-USB-RoomIQ` (the
  `S360-KIT-BEDROOM-P` USB power-variant) — are now authored as full, complete
  product configs, each as a config-string-named bundle
  ([`products/bundles/ceiling-usb-ventiq-roomiq.yaml`](../products/bundles/ceiling-usb-ventiq-roomiq.yaml),
  [`products/bundles/ceiling-usb-roomiq.yaml`](../products/bundles/ceiling-usb-roomiq.yaml))
  composed from the `packages/boards/` layer (Core ceiling `S360-100` + VentIQ
  `S360-211` + RoomIQ `S360-200` board packages) plus the USB-C power package
  [`packages/hardware/power_usb.yaml`](../packages/hardware/power_usb.yaml) (NOT
  a PSU board — **no `S360-410`**) plus the base tier and the same behaviour
  profiles the PoE sensor bundle uses, with a thin compat shim
  ([`products/sense360-ceiling-usb-ventiq-roomiq.yaml`](../products/sense360-ceiling-usb-ventiq-roomiq.yaml),
  [`products/sense360-ceiling-usb-roomiq.yaml`](../products/sense360-ceiling-usb-roomiq.yaml))
  that does nothing but `!include` its bundle. Each carries a
  [`config/product-catalog.json`](../config/product-catalog.json) row with
  `status: compile-only` / `target_channel: manual-custom` /
  `webflash_build_matrix: false` / no `artifact_name` / no `webflash_wrapper` /
  no kit preset, and is registered as a top-level compile-only target
  (`ceiling-usb-ventiq-roomiq-product-compile-only`,
  `ceiling-usb-roomiq-product-compile-only`) in
  [`config/compile-only-targets.json`](../config/compile-only-targets.json) with
  `compile_validation_status: pending-ci` (ESPHome was unavailable in the
  authoring environment, so **no full compile was run and none is fabricated**;
  a CI `--compile` run is owed). All boards (`S360-100`, `S360-211`, `S360-200`)
  are `verified` and there is **no evidence blocker** — USB rows carry no
  `S360-410` PoE caveat. The configs are **manual / custom** (available for
  manual ESPHome / GitHub use), **not** WebFlash-exposed: no
  `config/webflash-builds.json` entry; not production / preview / verified /
  release-ready; not in `release_one_required_configs`. No board
  `schematic_status` is changed; `manifest.json` / `firmware/sources.json` are
  untouched; Release-One and the LED preview are unchanged. **CREATE-002 / 003 /
  005 / 006 stay queued behind their gates.** See
  [`docs/product-readiness-matrix.md`](product-readiness-matrix.md) and
  [`docs/all-yaml-release-matrix.md`](all-yaml-release-matrix.md).

## Out of v1 scope

Deliberately **not** target rows, with the honest reason each is excluded:

- **Fan config strings** — `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ`
  (`blocked` / HW-005), `Ceiling-POE-VentIQ-FanRelay-RoomIQ`,
  `Ceiling-POE-FanDAC`, `Ceiling-POE-FanPWM` (all `hardware-pending`).
  Their kits (`S360-KIT-BATH-RELAY`, `S360-KIT-BATH-TRIAC`,
  `S360-KIT-DUCT-PWM`, `S360-KIT-DUCT-0-10V`) are `future-expansion` /
  `blocked` with **null** `default_config_string`, and the room-bundle
  matrix introduces **no fan bundle**. The fan products already have
  their own R4 YAMLs and follow-up chains.
- **Mains / `PWR` / 240V (`S360-400`)** — compliance-blocked; no v1 kit
  ships mains power; `S360-400` is `cataloged_unverified`.
- **Wall and Voice mounts** — R4 v1 is ceiling-only; no wall or voice
  kit exists, and R4 has no voice module.

## Validation

```text
python3 tests/validate_configs.py
python3 tests/test_product_catalog.py
python3 tests/test_room_bundle_skus.py
python3 tests/test_kit_intent_matrix.py
python3 tests/test_all_yaml_release_matrix.py
python3 tests/test_roadmap_status_doc.py
python3 -m unittest discover -s tests -p "test_*.py"
```

All pass unchanged: this PR edits no config JSON, no product YAML, and
no test. Every config file stays byte-identical.

## Cross-references

- Room bundle SKU matrix: [`docs/sense360-room-bundles.md`](sense360-room-bundles.md) /
  [`config/room-bundle-skus.json`](../config/room-bundle-skus.json) — sellable PoE room kits.
- Kit intent matrix: [`docs/kit-intent-matrix.md`](kit-intent-matrix.md) /
  [`config/kit-intent-matrix.json`](../config/kit-intent-matrix.json) — use-case kit composition.
- Hardware catalog: [`config/hardware-catalog.json`](../config/hardware-catalog.json) /
  [`docs/hardware-catalog.md`](hardware-catalog.md) — per-board `schematic_status`.
- Firmware combination matrix: [`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json) — config-string grammar / status.
- Product catalog: [`config/product-catalog.json`](../config/product-catalog.json) — the 6 R4 + 21 legacy + 10 removed Mini entries.
- WebFlash builds: [`config/webflash-builds.json`](../config/webflash-builds.json) — the two live builds (stable + LED preview).
- Product readiness gate: [`docs/product-readiness-matrix.md`](product-readiness-matrix.md) — PRODUCT-GAP-001; legacy `legacy-only` disposition.
- Deprecation / removal policy: [`docs/product-deprecation-removal-policy.md`](product-deprecation-removal-policy.md) — PRODUCT-DEP-001; the gates `PRODUCT-DEP-CORE-001` runs through.
- Stable-target expansion plan: [`docs/stable-target-expansion-plan.md`](stable-target-expansion-plan.md) — G1–G10 gate vocabulary and `STABLE-TARGET-*` promotion ownership.
- Preview-to-stable gauntlet: [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md) — RELEASE-006; the LED gate.
- Working queue: [`UPCOMING_PR.md`](../UPCOMING_PR.md) — `V1-R4-CREATE-*` authoring queue and `PRODUCT-DEP-CORE-001` follow-up.

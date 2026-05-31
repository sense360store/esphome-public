# Upcoming PR

This file tracks the next planned change set for the esphome-public repository.

## PRE-HARDWARE-PREP-PLAN-001 — plan the design-derived readiness program

**Status:** docs-only / planning (promotes nothing, verifies nothing, resolves
nothing; no gate closed; no `schematic_status` flipped)

### Summary

Authors [`docs/pre-hardware-prep-plan.md`](docs/pre-hardware-prep-plan.md), the
design-derived readiness program that brings the six driver / PSU boards
(`S360-310` / `S360-311` / `S360-312` / `S360-320` / `S360-400` / `S360-410`)
to a **design-complete** state from the schematic PDFs the repo already holds,
**ahead of hardware**, so the eventual bench session is pure test-and-record.
The plan defines a `design-complete` status concept that is explicitly distinct
from `verified` (firmware authored + compile-validated from design artifacts,
recorded as a doc/metadata annotation — never a `config/*.json` field — and
which **never flips `schematic_status` on its own**), enumerates the six
per-board deliverables, flags every gerber/BOM-dependent item as
**ARTIFACT-BLOCKED**, captures the operator-stated **SX1509 deprecation** as
its own early reconcile slice, fixes the per-board hardware-verification
handoff, and emits the ordered slice sequence.

### What changed

* New [`docs/pre-hardware-prep-plan.md`](docs/pre-hardware-prep-plan.md) —
  the program: `design-complete` policy + non-flip rule, per-board D1–D6
  deliverable tables, ARTIFACT-BLOCKED flags (clearance/creepage for the
  PoE `S360-410` and mains `S360-310`/`S360-320`/`S360-400` boards), the
  SX1509 reference inventory + native-GPIO resolution targets, the
  `design-complete → verified` bench handoff per board, and the ordered
  slice sequence.
* This `UPCOMING_PR.md` entry.

### Ordered slice sequence (queued; this PR authors none of them)

1. `PRE-HW-PREP-SX1509-RECONCILE-001` — re-bind the fan path to native
   ESP32-S3 GPIO; mark residual SX1509 fan refs legacy/superseded
   (coordinates with `CORE-ABSTRACT-BUS-001` + the native fan GPIO map).
2. `PRE-HW-PREP-FW-312-001` — `S360-312` DAC (native I²C, no SX1509 dep).
3. `PRE-HW-PREP-FW-311-001` — `S360-311` PWM (native re-bind; `PACKAGE-PWM-001`).
4. `PRE-HW-PREP-FW-310-001` — `S360-310` Relay (SELV logic side).
5. `PRE-HW-PREP-TESTMATRIX-SELV-001` — finalise the SELV bench matrices.
6. `PRE-HW-PREP-GERBER-REVIEW-001` *(ARTIFACT-BLOCKED)* — clearance/creepage
   reviews; **gated on gerbers + BOM being committed**.
7. `PRE-HW-PREP-TRIAC-320-001` *(HW-005 / COMPLIANCE-001)*.
8. `PRE-HW-PREP-MAINS-400-001` *(COMPLIANCE-001)*.
9. `PRE-HW-PREP-POE-410-001` *(isolation / Hi-pot; `PACKAGE-POE-410-001`)*.

### Guardrails (explicitly NOT changed)

* No YAML, package, board, bundle, expansion, or product file edited.
* No `config/*.json` changed — `S360-310/311/312/320/400/410` stay
  `cataloged_unverified`, no `schematic_file`, no config string, artifact
  name, or lifecycle touched.
* No `schematic_status` flip; nothing marked `verified` or
  design-complete-as-verified; nothing promoted.
* No WebFlash exposure / release; no edit to
  [`firmware/sources.json`](firmware/sources.json) or `manifest.json`.
* The SX1509 reconciliation is **planned only**, not performed; no GPIO
  numbers invented beyond schematic-printed values.
* No gerbers / BOM / measurement fabricated; the WebFlash repo is untouched.

### Validation

* `python3 tests/validate_configs.py`
* `python3 tests/test_roadmap_status_doc.py`
* `python3 -m unittest discover -s tests -p "test_*.py"`

---

## HW-PINMAP-311-FOLLOWUP — standalone schematic-backed reference doc for S360-311 PWM

**Status:** docs-only (records, resolves nothing; no gate closed; board package still gated)

### Summary

Authors the standalone schematic-backed hardware reference doc for the
Sense360 PWM board (`S360-311-R4`) at
[`docs/hardware/s360-311-r4-fanpwm.md`](docs/hardware/s360-311-r4-fanpwm.md),
sourced **only** from the already-committed module-side schematic PDF
[`docs/hardware/schematics/S360-311-R4.pdf`](docs/hardware/schematics/S360-311-R4.pdf)
(HW-ASSETS-003; SHA256 `c910b3364be1d58fc44d12b5a189dade47efddf6cae158a86577ec7501e48006`).
It transcribes the connector and pin map exactly as the schematic shows
(`J3` 13-pin "From Core"; the four fan outputs `J1` / `J2` / `J4` / `J5`;
the Nextion `J6`; mounting holes `H1..H4`; the MT3608 boost) and records
every open reconciliation question as **STILL OWED**. Per
[`docs/cleanup-audit.md`](docs/cleanup-audit.md) the reconciliation itself
needs silkscreen, harness, and bench evidence plus the systemic Core
abstract-bus resolution, none of which this PR performs.

### What changed

* New `docs/hardware/s360-311-r4-fanpwm.md` — the standalone reference doc.
* `docs/hardware/s360-311-r4-pwm.md` — added a See-also cross-link to the
  new reference doc (no other section rewritten; status row unchanged).
* `docs/hardware/board-readiness-matrix.md` — replaced the "still no
  standalone reference doc" note in the `S360-311` subsection with a link
  to the new doc, and added a See-also entry. `S360-311` classification
  (`partially-documented`, `not-needed-for-release-one`,
  `package-yaml-pending`) is unchanged.
* This `UPCOMING_PR.md` update.

### Open reconciliation questions recorded as STILL OWED (resolved: none)

1. SX1509-expander-vs-direct-ESP32-GPIO mapping disagreement → owned by
   `CORE-ABSTRACT-BUS-001` /
   [`docs/release-one-hardware-audit.md` Required follow-ups #2 / #3](docs/release-one-hardware-audit.md).
2. UART on `J3` pins 11 / 12 (module-side labels not in the Core `J6`
   capture).
3. `"NINE 4pin FANs"` section title vs four visible outputs
   (`J1` / `J2` / `J4` / `J5`).
4. Single-channel-vs-four-channel canonical abstraction for the `FanPWM`
   token (`PACKAGE-PWM-001`).

Each records the evidence (silkscreen, harness, bench waveforms) that
would close it. The reconciliation and the S360-311 board-package
promotion **remain gated** on that owed evidence.

### Guardrails (explicitly NOT changed)

* No edit to `config/hardware-catalog.json` (`S360-311` stays
  `cataloged_unverified`, no `schematic_file`),
  `config/product-catalog.json`, `config/webflash-builds.json`, or
  `config/webflash-compatibility.json`.
* No `schematic_status` flip; no `verified` / `pin-map-confirmed` mark.
* No package YAML edited (`fan_pwm.yaml`, `sense360_fan_pwm.yaml`,
  `gpio_expander_sx1509.yaml`, `sense360_core*.yaml` all unchanged).
* No product YAML, WebFlash wrapper, build entry, release, tag, or import
  added; no firmware regenerated.
* Release-One, the LED preview path, and FanTRIAC (`blocked` / `HW-005`)
  are unchanged; `S360-320` / `S360-400` compliance is unchanged.
* The schematic PDF and the curated artifact index
  (`docs/hardware/artifacts/S360-311-R4.md`) are not edited.
* The WebFlash repo (`sense360store/webflash`) is untouched.

### Validation

* `python3 tests/validate_configs.py`
* `python3 tests/test_roadmap_status_doc.py`
* `python3 -m unittest discover -s tests -p "test_*.py"`

---

## PRODUCT-DEP-CORE-001 — retire non-template legacy core-c/v/w configs

**Status:** retired (14 legacy `sense360-core-*` configs moved to `removed`; 5 kept as live authoring templates)

### Summary

Executes the `core-c` / `core-v` / `core-w` disposition recommended in
[`docs/v1-r4-product-gap.md`](docs/v1-r4-product-gap.md) (§"`core-c` / `core-v`
/ `core-w` disposition"), the deprecation-series sibling of
`PRODUCT-DEP-MINI-001`. Of the 19 legacy `sense360-core-*` `legacy-compatible`
entries, the **14** with no R4-v1 reuse are retired through the
`PRODUCT-DEP-001` `legacy-compatible -> removed` (intentional-retirement)
transition — the same path the Mini range used; no `deprecated` step is needed
because these were never WebFlash-shippable and never appeared in
`config/webflash-builds.json`. The **5** ceiling Core bases / sensor stacks that
the gap doc flags as authoring templates for not-yet-authored `V1-R4-CREATE-*`
configs stay `legacy-compatible`; their retirement is **deferred** to land with
the CREATE config they template.

### KEEP / RETIRE split (from the gap-doc template-source table)

**KEEP-as-template (5, stay `legacy-compatible`, annotated; retirement deferred):**

* `sense360-core-c-poe` — ceiling + PoE base → templates V1-R4-CREATE-002 / 003.
* `sense360-core-c-usb` — ceiling + USB base → templates V1-R4-CREATE-005 / 006.
* `sense360-core-ceiling` — full AirIQ stack → templates V1-R4-CREATE-002 / 005.
* `sense360-core-ceiling-bathroom` — VentIQ-intent stack → templates V1-R4-CREATE-006
  (V1-R4-CREATE-004 already authored).
* `sense360-core-ceiling-presence` — presence(+LED) stack → templates
  V1-R4-CREATE-003 / 006 (V1-R4-CREATE-001 / 004 already authored).

**RETIRE (14, moved to `removed` tombstones; product YAMLs deleted):**

* mains: `sense360-core-c-pwr`.
* wall (5): `sense360-core-w-poe`, `-w-pwr`, `-w-usb`, `sense360-core-wall`,
  `sense360-core-wall-presence`.
* voice (8): `sense360-core-v-c-poe`, `-v-c-pwr`, `-v-c-usb`, `-v-w-poe`,
  `-v-w-pwr`, `-v-w-usb`, `sense360-core-voice-ceiling`,
  `sense360-core-voice-wall`.

The two standalone legacy entries (`sense360-fan-pwm`, `sense360-poe`) are
**outside** `PRODUCT-DEP-CORE-001` scope and stay `legacy-compatible`.

### What changed

* `config/product-catalog.json`: the 14 RETIRE rows flip
  `legacy-compatible -> removed` with `removed_since: 2026-05-30`,
  `removal_reason` ("Superseded by R4 product line; not an R4 config and not a
  live authoring template." + the `legacy-compatible -> removed` transition
  note), a per-family `no_replacement_reason`, and tombstone `notes`; each drops
  `product_yaml` (tombstone contract, exactly as the Mini entries). The 5 KEEP
  rows keep `status: legacy-compatible` and gain a template-retention annotation
  in `notes`.
* `products/`: the 14 RETIRE `sense360-core-*.yaml` files are removed.

### Guardrails (explicitly NOT changed)

* No KEEP-as-template config retired; their lifecycle is unchanged.
* No shared package under `packages/` deleted — the legacy core configs
  referenced core/board/expansion packages that R4 still uses; only the legacy
  product YAMLs and their catalog rows are retired.
* No touch to the 6 R4 configs, the 2 USB configs, or the 10 Mini tombstones.
* No edits to `config/webflash-builds.json`, `manifest.json`, or
  `firmware/sources.json`; no board `schematic_status` change; nothing promoted.
* `v1.0.0` is untouched — it keeps the legacy files for tag-pinned field units.
* No new tests and no test assertions weakened: the `packages/`-level package
  tests (`test_core_abstract_bus.py`) and the auto-discovering
  `test_product_substitutions.py` / `generate_test_configs.py` reference shared
  packages (which survive) and discover product YAMLs dynamically, so the suite
  passes with the RETIRE set gone with no test edits.

### Deferred work

The KEEP-as-template set's retirement is **deferred**: each of the 5 retained
configs is retired in the PR that authors its last templated `V1-R4-CREATE-*`
config (CREATE-002 / 003 / 005 / 006), through the same
`legacy-compatible -> removed` transition used here.

### Validation

* `python3 tests/validate_configs.py`
* `python3 tests/test_product_catalog.py`
* `python3 tests/test_product_substitutions.py`
* `python3 tests/test_core_abstract_bus.py`
* `python3 tests/test_all_yaml_release_matrix.py`
* `python3 -m unittest discover -s tests -p "test_*.py"`

---

## V1-R4-CREATE-004 — author USB sensor variants (Ceiling-USB-VentIQ-RoomIQ, Ceiling-USB-RoomIQ)

**Status:** authored (manual / custom channel; compile-validation pending-ci; no WebFlash promotion)

### Summary

This change authors the two unblocked R4 USB sensor configs from
[`docs/v1-r4-product-gap.md`](docs/v1-r4-product-gap.md) (V1-R4-CREATE-004),
each as a config-string-named bundle + thin compat shim + catalog row composed
from the `packages/boards/` layer:

* `Ceiling-USB-VentIQ-RoomIQ` — Core(ceiling) + USB-C power + S360-211 VentIQ +
  S360-200 RoomIQ (the USB power-axis variant of the WebFlash-shipping
  `Ceiling-POE-VentIQ-RoomIQ`, PoE PSU board swapped for the USB-C power package).
* `Ceiling-USB-RoomIQ` — Core(ceiling) + USB-C power + S360-200 RoomIQ (the USB
  power-axis variant of the authored `Ceiling-POE-RoomIQ`).

These are **manual / custom** firmwares available for manual ESPHome / GitHub
use, **NOT** WebFlash-exposed. USB variants carry **no PoE PSU board** (no
S360-410); all three boards (S360-100, S360-211, S360-200) are
`schematic_status: verified` and there is **no evidence blocker**.

### What changed

* New bundles `products/bundles/ceiling-usb-ventiq-roomiq.yaml` and
  `products/bundles/ceiling-usb-roomiq.yaml` (full configs composed from the
  board packages + `packages/hardware/power_usb.yaml` + base tier + the same
  behaviour profiles the PoE sensor bundle uses).
* New compat shims `products/sense360-ceiling-usb-ventiq-roomiq.yaml` and
  `products/sense360-ceiling-usb-roomiq.yaml` (each does nothing but `!include`
  its bundle, per §3.2).
* `config/product-catalog.json`: two rows, `status: compile-only`,
  `target_channel: manual-custom`, `webflash_build_matrix: false`, no
  `artifact_name`, no `webflash_wrapper`, no kit preset.
* `config/compile-only-targets.json`: two top-level targets
  (`ceiling-usb-ventiq-roomiq-product-compile-only`,
  `ceiling-usb-roomiq-product-compile-only`), `compile_validation_status:
  pending-ci`.
* `config/compile-only-candidates.json`,
  `config/firmware-combination-matrix.json` (regenerated;
  `compile-only-candidate`), `docs/firmware-build-gap-report.md` (regenerated),
  `docs/product-readiness-matrix.md`, `docs/all-yaml-release-matrix.md`, and
  `docs/v1-r4-product-gap.md` (CREATE-004 marked authored) updated to match.

### Guardrails (explicitly NOT changed)

* No edits to `config/webflash-builds.json`, `firmware/sources.json`, or
  `manifest.json`.
* No `artifact_name`; no `webflash_build_matrix` flip; no kit preset; no
  WebFlash wrapper / exposure.
* No PoE PSU (no S360-410) in these USB variants.
* No board `schematic_status` change; LED not marked stable; S360-410 not marked
  verified; nothing preview-promoted or claimed as a kit.
* No compile result fabricated (ESPHome unavailable in the authoring
  environment; a CI `--compile` run is owed).

### Queue status (maintenance rule)

`V1-R4-CREATE-004` delivers the unblocked non-LED USB pair. The remaining
`V1-R4-CREATE-*` slices stay **queued behind their gates**:

* **V1-R4-CREATE-002** — `Ceiling-POE-AirIQ-RoomIQ` (S360-410 + AirIQ-stack
  evidence-gated).
* **V1-R4-CREATE-003** — `Ceiling-POE-RoomIQ-LED` (LED preview gauntlet;
  S360-410-gated).
* **V1-R4-CREATE-005** — `Ceiling-USB-AirIQ-RoomIQ` (AirIQ-stack evidence-gated).
* **V1-R4-CREATE-006** — `Ceiling-USB-VentIQ-RoomIQ-LED`,
  `Ceiling-USB-RoomIQ-LED` (LED preview-gated).

### Validation

* `python3 tests/validate_configs.py`
* `python3 scripts/validate_compile_targets.py --metadata-only`
* `python3 tests/test_product_catalog.py`
* `python3 tests/test_all_yaml_release_matrix.py`
* `python3 tests/test_product_substitutions.py`
* `python3 tests/test_release_one_entity_names.py`
* `python3 tests/validate_webflash_builds.py`
* `python3 -m unittest discover -s tests -p "test_*.py"`

### Retained cross-references (maintenance)

The module-side pinmap ledger `MODULE-PINMAPS-GDRIVE-001` and the canonical Core
connector pin map [`docs/hardware/s360-100-core-connector-pin-map.md`](docs/hardware/s360-100-core-connector-pin-map.md)
are unchanged by this slice and remain the source of truth for the S360-100
ceiling Core bus that the USB variants bind.

---

## ROOM-BUNDLE-FAN-VARIANTS-001 — Planning-only fan-control variants (Bathroom & Kitchen)

**Status:** planning-only (no firmware release, no WebFlash promotion)

### Summary

This change adds a planning-only proposal for optional fan-control variants of the
Bathroom and Kitchen PoE room bundles. The base room bundles remain the primary
product line. The fan variants are Bathroom/Kitchen-only add-ons and are captured
in a separate config file (Option A) so the stable room-bundle matrix stays clean.

### What changed

* New `config/room-bundle-fan-variants.json` describing five planning variants:
  * `S360-KIT-BATH-P-REL` (relay)
  * `S360-KIT-BATH-P-DAC` (0-10V DAC)
  * `S360-KIT-BATH-P-PWM` (PWM)
  * `S360-KIT-KITCHEN-P-DAC` (0-10V DAC)
  * `S360-KIT-KITCHEN-P-REL` (relay)
* New docs section in `docs/sense360-room-bundles.md` with the variant table and prose.
* New contract test `tests/test_room_bundle_fan_variants.py`.
* This `UPCOMING_PR.md` update.

### Guardrails (explicitly NOT changed)

* No edits to `webflash-builds.json`, `sources.json`, or `manifest.json`.
* No `artifact_name` fields anywhere.
* No `webflash_build_matrix` flip.
* No LED/fan-driver stable promotion.
* No TRIAC variant.
* No Corridor/Living/Bedroom fan variant.
* No existing bundle SKU or lifecycle changed.

### Validation

* `python3 -m unittest discover -s tests -p "test_*.py"` (1163 tests, 3 skipped).
* `validate_configs.py`.
* Per-test scripts for the new contract test.

### Variants

| Variant SKU | Base bundle | Room | Fan control |
| --- | --- | --- | --- |
| S360-KIT-BATH-P-REL | S360-KIT-BATH-P | Bathroom | relay |
| S360-KIT-BATH-P-DAC | S360-KIT-BATH-P | Bathroom | dac_0_10v |
| S360-KIT-BATH-P-PWM | S360-KIT-BATH-P | Bathroom | pwm |
| S360-KIT-KITCHEN-P-DAC | S360-KIT-KITCHEN-P | Kitchen | dac_0_10v |
| S360-KIT-KITCHEN-P-REL | S360-KIT-KITCHEN-P | Kitchen | relay |

### Notes

* relay vs DAC(0-10V) vs PWM are not runtime-interchangeable; each is a separate SKU.
* Bundle SKUs are kept separate from firmware config strings.
* Kitchen fan control is framed as extract/MVHR/EC boost, not a cooker-hood replacement.
* No variant is exposed to WebFlash.

### Next steps

* A future implementation PR would define firmware configs, build artifacts, and
  validation before any WebFlash promotion.

---

_Previous entries below this line are historical and unchanged._

## (historical placeholder)

Earlier planning notes are intentionally omitted from this excerpt.

(end)

## Historical: ROOM-BUNDLE-MATRIX baseline

The room-bundle matrix (Corridor, Living, Bedroom, Bathroom, Kitchen) across PoE and
USB power options remains the stable, released baseline. This planning entry does not
modify that matrix; it only proposes additive Bathroom/Kitchen fan variants for a
future PR.

* Corridor: S360-KIT-CORR-P / S360-KIT-CORR-U
* Living: S360-KIT-LIV-P / S360-KIT-LIV-U
* Bedroom: S360-KIT-BED-P / S360-KIT-BED-U
* Bathroom: S360-KIT-BATH-P / S360-KIT-BATH-U
* Kitchen: S360-KIT-KITCHEN-P / S360-KIT-KITCHEN-U

* Base bundles remain the main product line; fan variants are add-ons.
* No bundle SKU or lifecycle is changed by this planning entry.

(end of file)

<!-- planning-only; no firmware release implied -->

<!-- ROOM-BUNDLE-FAN-VARIANTS-001 -->

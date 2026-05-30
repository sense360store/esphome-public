# Upcoming PR

This file tracks the next planned change set for the esphome-public repository.

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

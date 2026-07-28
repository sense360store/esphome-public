# SENSE360-CANONICALISATION-001 PR 07 — zero-alias inventory

Programme: `SENSE360-CANONICALISATION-001`. Recorded against
`sense360store/esphome-public` main `6e6ae3fd` (post PR 06), the base the
owner named for PR 07. This is PR 07's **mandatory first deliverable**: every
package, product, remote, expansion, hardware and wrapper YAML path is
classified with a disposition and a basis **before anything is deleted**, per
the charter's `before_deletion_prove_one_of` rule.

Method: derived mechanically from the tree — the include graph resolved with
the PR 06 contract loader, presence at all 14 release tags checked against
the tags themselves, reachability computed from every declared
configuration's canonical YAML, and non-YAML references counted across
tests, config, docs and workflows. Evidence level: static inspection only.

## Totals

- **decide**: 0 (resolved 2026-07-28: 4 keep-protected, 1 deleted)
- **delete**: 12
- **delete-and-repoint**: 8
- **delete-if-orphan**: 21
- **delete-if-undeclared**: 8
- **flip**: 6
- **fold**: 2
- **keep**: 103
- **keep-with-reason**: 4

Total paths: 169.

## Execution log (updated in place as slices land)

- **2026-07-28, slice 1 — packages/remote resolution.** Four documented
  entrypoints kept as protected canonical entrypoints;
  `blower-framework.yaml` deleted as the unpublished remainder.
- **2026-07-28, slice 2 — zero-alias sweep.** 22 hardware/feature-layer
  paths deleted (12 expansion aliases, `power_poe` / `led_ring_ceiling`,
  both halves of the undocumented led-mic pair under the owner evidence
  test, 7 feature-profile aliases) after re-pointing 23 consumer files to
  the authoritative board packages. The PR 06 contract gate proved all 20
  board compositions byte-identical across the removal. The four
  alias-pinning test modules were replaced by the inverted ledger guard
  `tests/test_zero_alias.py`; CLAUDE.md's alias-retention rule was corrected
  (the tree is the source of truth it must follow).
- **2026-07-28, slice 3 — orphan sweep under the evidence test.** 16 more
  paths deleted: six pre-R4 expansion drivers/composers (`comfort`,
  `comfort_ceiling_s3`, `presence_ceiling_s3`, `presence_module_ceiling`,
  the superseded `presence_ld2450` radar primitive, `fan_12v_pwm`), three
  hardware orphans (`presence_dfrobot_c4001`, `presence_ld2450`,
  `power_management`), and seven orphan feature profiles (the advanced
  presence/comfort/fan set, `ceiling_led_ring_air_quality`, and the LD2412
  advanced cascade). Each had no live consumer and no publication as a
  customer entrypoint. Kept against the same test, with reasons:
  `gpio_expander_sx1509` (recorded SX1509-RECONCILE-001 retention),
  `power_240v` (sole S360-400 implementation, documented),
  the LD2412 set (`expansions/presence_ld2412`, `hardware/presence_ld2412`,
  `features/presence_basic_profile_ld2412` — documented in
  docs/product-matrix.md / docs/configuration.md), and the
  `sense360_core_*` family plus `power_usb` (deferred to the Core flip
  slice). Compositions again byte-identical; suite green.
- **2026-07-28, slice 3b — wrapper candidates resolved.** All eight
  `delete-if-undeclared` `products/webflash/` rows resolve to **keep**:
  every one of the fourteen wrapper files is the `product_yaml` address of a
  committed `config/webflash-builds.json` row (verified 14/14), so each is
  declared release-gate infrastructure under ESP-007, not an orphan.
  Remaining execution: the Core source-of-truth flip (`sense360_core_*`,
  `power_usb`, `s360-100-core*`), the `device_sku` identifier, and the
  final full-suite / validator pass before the acceptance request.
- **2026-07-28, slice 4 — Core source-of-truth flip.** The S360-100 ceiling
  Core content moved verbatim (one stale comment cross-reference retargeted)
  from `packages/hardware/sense360_core_ceiling.yaml` into
  `packages/boards/s360-100-core-ceiling.yaml`; the former overlay it
  replaced was a pure single-`!include` wrapper declaring nothing of its
  own, so every consumer's resolved composition is unchanged (PR 06
  contract gate: byte-identical, again). 20 consumer files re-pointed
  (bundles, compile-only skeletons, legacy products). Deleted with the
  flip: the legacy `hardware/sense360_core_ceiling.yaml` path and the
  never-wired `boards/s360-100-core.yaml` prototype (its substitution-layer
  idea lands with PR 08); the zero-alias ledger now pins 41 paths. Kept
  with reasons: `hardware/sense360_core.yaml` / `sense360_core_poe.yaml` /
  `sense360_core_voice.yaml` (implementations of catalogued
  legacy-compatible products), `sense360_core_mapping.yaml` (pin-map
  contract read by four test modules), `sense360_core_ceiling_s3.yaml`
  (CORE-ABSTRACT-BUS-001 guard input; retires with PR 08), `power_usb`
  (consumed by legacy USB products). Test fallout repaired by retargeting
  path constants in seven test modules (content assertions unchanged);
  stale "wraps the legacy path" / pending-flip claims corrected in
  `docs/system-architecture.md`, `docs/hardware-catalog.md`,
  `packages/README.md`, `packages/SENSE360_MODULES.md`,
  `docs/feature-entity-matrix.md`, `docs/hardware/s360-100-r4-core.md` and
  live YAML comments. The owner-authored bench record
  `docs/hardware/CORE-BENCH-RUNTIME-EVIDENCE-001.md` keeps its recorded
  path strings verbatim (dead links converted to plain literals only);
  its pinning test is untouched. Entity tables regenerated
  (include-source lists only; no entity change). Full suite green
  (2456 tests) and all validators pass.
- **Correction recorded:** `packages/expansions/fan_pwm.yaml` was initially
  misclassified `delete-and-repoint`. It composes the sx1509 binding layer
  AND declares the four fan speed controllers, so it is authoritative, not
  an alias. The deletion was caught by its content guards and fully
  reverted before commit; its row below is corrected to **keep-with-reason**
  (preserved legacy SX1509 composition consumed by the historical
  compile-proof skeleton).

## Disposition vocabulary

- **keep** — protected canonical entrypoint, canonical composition, declared
  skeleton/wrapper, base tier, or authoritative-and-consumed content.
- **keep-with-reason** — retained under a recorded prior disposition or an
  open owner decision (OD-SOT-008); each row names the reason.
- **delete** — obsolete alias or orphan with nothing resolving through it.
- **delete-and-repoint** — alias with live consumers: every `!include` is
  re-pointed to the board package it resolves to, then the alias goes. The
  PR 06 contract freshness gate is the proof: every resolved composition
  must come out **byte-identical**.
- **delete-if-orphan / delete-if-undeclared** — deletion candidate pending
  the named per-file verification during execution.
- **flip** — Core source-of-truth flip: the board overlay stops wrapping the
  legacy `packages/hardware/sense360_core_*` source; content moves into
  `packages/boards/s360-100-core*` and the legacy path goes.
- **fold** — the `S360-LED-V-C` pair: one surviving path, decided in
  execution with the PR 06 status proof carried forward.
- **decide** — `packages/remote/`: RESOLVED by the owner decision of
  2026-07-28. The evidence test ("was any path ever documented, advertised
  or published as a customer or third-party entrypoint?") selected the SPLIT
  branch: `docs/remote-package-consumption.md` at HEAD is an explicitly
  customer-facing guide ("the supported way to build Sense360 firmware
  remotely… the manual / custom path for advanced users") in a public
  repository, and it documents exactly four entrypoints —
  `ceiling-airiq.yaml`, `ceiling-roomiq-presence.yaml`,
  `led-framework.yaml`, `sense360-shared-engines.yaml` — which are therefore
  **protected canonical entrypoints** and KEPT with this recorded reason.
  `blower-framework.yaml` appears in no customer documentation (only an
  internal architecture doc), no tag, no generated Pages nav, no WebFlash
  file and no release note: it is the unpublished remainder and is DELETED
  in this PR with a migration note in
  `docs/architecture/sense360-blower-framework.md`. The same evidence test
  resolves every delete-if-orphan / delete-if-undeclared candidate during
  execution.

Three standing inputs from PR 06 are in scope and marked above: the
`S360-LED-V-C` fold, the dangling wall/voice documentation references, and
the `device_sku` substitution (`S360-CORE-C-POE` / `-USB` / `S360-CORE-C`) —
a second, non-canonical configuration-layer identifier published as a
customer-visible Product SKU diagnostic, resolved during execution.

Deletion never touches: release tags and published binaries (immutable),
`products/sense360-*.yaml` canonical entrypoints, the declaration layer in
`config/`, or anything a standing gate protects. Nothing here builds,
publishes, promotes or changes any channel.

### `packages/base/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `api_encrypted.yaml` | authoritative | 14 | 32 | y | **keep** | Base infrastructure tier. |
| `bluetooth_proxy.yaml` | authoritative | 14 | 2 | — | **keep** | Base infrastructure tier. |
| `complete.yaml` | composer | 14 | 1 | — | **keep** | Base infrastructure tier. |
| `complete_ethernet.yaml` | composer | 14 | 1 | — | **keep** | Base infrastructure tier. |
| `device_framework.yaml` | authoritative | 0 | 16 | y | **keep** | Base infrastructure tier. |
| `external_components.yaml` | authoritative | 14 | 28 | y | **keep** | Base infrastructure tier. |
| `logging.yaml` | authoritative | 14 | 32 | y | **keep** | Base infrastructure tier. |
| `ota.yaml` | authoritative | 14 | 32 | y | **keep** | Base infrastructure tier. |
| `time.yaml` | authoritative | 14 | 32 | y | **keep** | Base infrastructure tier. |
| `wifi.yaml` | authoritative | 14 | 31 | y | **keep** | Base infrastructure tier. |

### `packages/boards/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `s360-100-core-ceiling.yaml` | alias | 12 | 10 | y | **delete-and-repoint** | Alias with 10 live consumer(s): re-point each include to the board package it resolves to, then delete; compositions must come out byte-identical (contract gate). |
| `s360-100-core.yaml` | authoritative | 12 | 0 | — | **delete-if-orphan** | Published historically but no live consumer; charter aggressive posture applies — verify no legacy catalogued product resolves through it, then delete. |
| `s360-200-roomiq-climate.yaml` | authoritative | 12 | 2 | y | **keep** | Authoritative and consumed. |
| `s360-200-roomiq-pir.yaml` | authoritative | 0 | 15 | y | **keep** | Authoritative and consumed. |
| `s360-200-roomiq-radar.yaml` | authoritative | 12 | 2 | y | **keep** | Authoritative and consumed. |
| `s360-200-roomiq-sen0609.yaml` | authoritative | 0 | 15 | y | **keep** | Authoritative and consumed. |
| `s360-200-roomiq-uart.yaml` | authoritative | 0 | 1 | y | **keep** | Authoritative and consumed. |
| `s360-200-roomiq.yaml` | composer | 12 | 10 | y | **keep** | Authoritative and consumed. |
| `s360-210-airiq-ceiling-s3.yaml` | authoritative | 12 | 1 | — | **keep** | Authoritative and consumed. |
| `s360-210-airiq-no-sfa40.yaml` | authoritative | 0 | 0 | — | **keep-with-reason** | Touches OD-SOT-008 (SFA40 fitment, open); referenced by two test modules. Not decided by PR 07. |
| `s360-210-airiq-sps30.yaml` | authoritative | 0 | 0 | — | **keep-with-reason** | Opt-in external-SPS30 overlay; the documented composition path for the optional attachment (core-framework contract names it). |
| `s360-210-airiq.yaml` | authoritative | 12 | 8 | y | **keep** | Authoritative and consumed. |
| `s360-211-ventiq.yaml` | authoritative | 12 | 5 | y | **keep** | Authoritative and consumed. |
| `s360-300-led-mic-ceiling.yaml` | authoritative | 12 | 1 | — | **fold** | PR 06 carried input: internal board file whose published alias packages/hardware/led_ring_mic_ceiling.yaml is at v1.0.0; content folds into one surviving path and the other goes. |
| `s360-300-led.yaml` | authoritative | 12 | 3 | y | **keep** | Authoritative and consumed. |
| `s360-410-poe-psu.yaml` | authoritative | 12 | 8 | y | **keep** | Authoritative and consumed. |

### `packages/expansions/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `airiq.yaml` | alias | 14 | 0 | — | **delete** | Alias with zero YAML consumers; delete outright. |
| `airiq_bathroom_base.yaml` | alias | 14 | 7 | y | **delete-and-repoint** | Alias with 7 live consumer(s): re-point each include to the board package it resolves to, then delete; compositions must come out byte-identical (contract gate). |
| `airiq_ceiling.yaml` | alias | 14 | 3 | y | **delete-and-repoint** | Alias with 3 live consumer(s): re-point each include to the board package it resolves to, then delete; compositions must come out byte-identical (contract gate). |
| `airiq_ceiling_s3.yaml` | alias | 14 | 0 | — | **delete** | Alias with zero YAML consumers; delete outright. |
| `bathroom.yaml` | composer | 14 | 0 | — | **delete-if-orphan** | Published historically but no live consumer; charter aggressive posture applies — verify no legacy catalogued product resolves through it, then delete. |
| `comfort.yaml` | authoritative | 14 | 0 | — | **delete-if-orphan** | Published historically but no live consumer; charter aggressive posture applies — verify no legacy catalogued product resolves through it, then delete. |
| `comfort_ceiling.yaml` | alias | 14 | 9 | y | **delete-and-repoint** | Alias with 9 live consumer(s): re-point each include to the board package it resolves to, then delete; compositions must come out byte-identical (contract gate). |
| `comfort_ceiling_s3.yaml` | authoritative | 14 | 0 | — | **delete-if-orphan** | Published historically but no live consumer; charter aggressive posture applies — verify no legacy catalogued product resolves through it, then delete. |
| `fan_12v_pwm.yaml` | authoritative | 14 | 0 | — | **delete-if-orphan** | Published historically but no live consumer; charter aggressive posture applies — verify no legacy catalogued product resolves through it, then delete. |
| `fan_dac.yaml` | alias | 12 | 4 | y | **delete-and-repoint** | Alias with 4 live consumer(s): re-point each include to the board package it resolves to, then delete; compositions must come out byte-identical (contract gate). |
| `fan_gp8403.yaml` | authoritative | 14 | 1 | y | **keep** | Authoritative and consumed. |
| `fan_pwm.yaml` | authoritative-with-includes | 14 | 1 | — | **keep** | Authoritative and consumed. |
| `fan_pwm_native.yaml` | authoritative | 12 | 4 | y | **keep** | Authoritative and consumed. |
| `fan_pwm_sx1509.yaml` | authoritative | 12 | 1 | — | **keep-with-reason** | Superseded SX1509 fan path still composed by the preserved legacy compile-only skeleton products/compile-only/ceiling-poe-fanpwm.yaml (historical compile proof). |
| `fan_relay.yaml` | authoritative | 14 | 2 | y | **keep** | Authoritative and consumed. |
| `fan_triac.yaml` | authoritative | 14 | 1 | y | **keep** | Authoritative and consumed. |
| `gpio_expander_sx1509.yaml` | authoritative | 14 | 0 | — | **keep-with-reason** | SX1509-RECONCILE-001 retained-with-reason: read directly by tests/test_core_abstract_bus.py (CORE-ABSTRACT-BUS-001C interrupt-pin guard); S360-100-NATIVE-FAN-GPIO-MAP-001 forbids removing the SX1509 globally. |
| `presence_ceiling.yaml` | alias | 14 | 11 | y | **delete-and-repoint** | Alias with 11 live consumer(s): re-point each include to the board package it resolves to, then delete; compositions must come out byte-identical (contract gate). |
| `presence_ceiling_s3.yaml` | authoritative | 14 | 0 | — | **delete-if-orphan** | Published historically but no live consumer; charter aggressive posture applies — verify no legacy catalogued product resolves through it, then delete. |
| `presence_ld2412.yaml` | authoritative | 14 | 0 | — | **delete-if-orphan** | Published historically but no live consumer; charter aggressive posture applies — verify no legacy catalogued product resolves through it, then delete. |
| `presence_ld2450.yaml` | authoritative | 14 | 0 | — | **delete-if-orphan** | Published historically but no live consumer; charter aggressive posture applies — verify no legacy catalogued product resolves through it, then delete. |
| `presence_module_ceiling.yaml` | authoritative | 14 | 0 | — | **delete-if-orphan** | Published historically but no live consumer; charter aggressive posture applies — verify no legacy catalogued product resolves through it, then delete. |
| `roomiq.yaml` | alias | 12 | 0 | — | **delete** | Alias with zero YAML consumers; delete outright. |
| `roomiq_radar.yaml` | alias | 12 | 0 | — | **delete** | Alias with zero YAML consumers; delete outright. |
| `sense360_fan_pwm.yaml` | authoritative | 14 | 1 | — | **keep** | Authoritative and consumed. |
| `ventiq.yaml` | alias | 12 | 0 | — | **delete** | Alias with zero YAML consumers; delete outright. |

### `packages/features/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `airiq_advanced.yaml` | authoritative-with-includes | 14 | 1 | — | **keep** | Live feature layer. |
| `airiq_advanced_profile.yaml` | authoritative-with-includes | 14 | 1 | — | **keep** | Live feature layer. |
| `airiq_auto_ventilation_profile.yaml` | alias | 12 | 0 | — | **delete** | Feature alias with no live consumer; resolved composition proven unchanged by the contract freshness gate. |
| `airiq_basic.yaml` | authoritative | 14 | 2 | — | **keep** | Live feature layer. |
| `airiq_basic_profile.yaml` | authoritative | 14 | 5 | y | **keep** | Live feature layer. |
| `airiq_extended_profile.yaml` | alias | 12 | 0 | — | **delete** | Feature alias with no live consumer; resolved composition proven unchanged by the contract freshness gate. |
| `airiq_framework.yaml` | authoritative | 0 | 6 | y | **keep** | Live feature layer. |
| `airiq_mqtt_profile.yaml` | alias | 12 | 0 | — | **delete** | Feature alias with no live consumer; resolved composition proven unchanged by the contract freshness gate. |
| `airiq_profile.yaml` | alias | 12 | 0 | — | **delete** | Feature alias with no live consumer; resolved composition proven unchanged by the contract freshness gate. |
| `bathroom_profile.yaml` | authoritative-with-includes | 14 | 4 | y | **keep** | Live feature layer. |
| `blower_framework.yaml` | authoritative | 0 | 2 | y | **keep** | Live feature layer. |
| `ceiling_halo_leds.yaml` | authoritative | 14 | 3 | — | **keep** | Live feature layer. |
| `ceiling_led_ring_air_quality.yaml` | authoritative | 14 | 0 | — | **delete-if-orphan** | Feature profile with no YAML consumer and unreachable from any declared configuration; delete unless a legacy catalogued product resolves through it (verify per file). |
| `comfort_advanced_profile.yaml` | authoritative-with-includes | 14 | 0 | — | **delete-if-orphan** | Feature profile with no YAML consumer and unreachable from any declared configuration; delete unless a legacy catalogued product resolves through it (verify per file). |
| `comfort_basic_profile.yaml` | authoritative-with-includes | 14 | 5 | — | **keep** | Live feature layer. |
| `device_health.yaml` | authoritative | 14 | 33 | y | **keep** | Live feature layer. |
| `diagnostics.yaml` | authoritative | 14 | 13 | y | **keep** | Live feature layer. |
| `fan_control_advanced_profile.yaml` | authoritative-with-includes | 14 | 0 | — | **delete-if-orphan** | Feature profile with no YAML consumer and unreachable from any declared configuration; delete unless a legacy catalogued product resolves through it (verify per file). |
| `fan_control_profile.yaml` | authoritative-with-includes | 14 | 1 | — | **keep** | Live feature layer. |
| `led_framework.yaml` | authoritative | 0 | 3 | y | **keep** | Live feature layer. |
| `led_presence_bridge.yaml` | authoritative | 0 | 2 | y | **keep** | Live feature layer. |
| `presence_advanced.yaml` | authoritative-with-includes | 14 | 0 | — | **delete-if-orphan** | Feature profile with no YAML consumer and unreachable from any declared configuration; delete unless a legacy catalogued product resolves through it (verify per file). |
| `presence_advanced_ld2412.yaml` | authoritative-with-includes | 14 | 1 | — | **keep** | Live feature layer. |
| `presence_advanced_profile.yaml` | authoritative-with-includes | 14 | 0 | — | **delete-if-orphan** | Feature profile with no YAML consumer and unreachable from any declared configuration; delete unless a legacy catalogued product resolves through it (verify per file). |
| `presence_advanced_profile_ld2412.yaml` | composer | 14 | 0 | — | **delete-if-orphan** | Feature profile with no YAML consumer and unreachable from any declared configuration; delete unless a legacy catalogued product resolves through it (verify per file). |
| `presence_basic.yaml` | authoritative | 14 | 3 | — | **keep** | Live feature layer. |
| `presence_basic_profile.yaml` | authoritative-with-includes | 14 | 7 | — | **keep** | Live feature layer. |
| `presence_basic_profile_ld2412.yaml` | composer | 14 | 0 | — | **delete-if-orphan** | Feature profile with no YAML consumer and unreachable from any declared configuration; delete unless a legacy catalogued product resolves through it (verify per file). |
| `presence_framework.yaml` | authoritative | 0 | 15 | y | **keep** | Live feature layer. |
| `roomiq_framework.yaml` | authoritative | 0 | 15 | y | **keep** | Live feature layer. |
| `roomiq_profile.yaml` | alias | 12 | 0 | — | **delete** | Feature alias with no live consumer; resolved composition proven unchanged by the contract freshness gate. |
| `roomiq_radar_profile.yaml` | alias | 12 | 0 | — | **delete** | Feature alias with no live consumer; resolved composition proven unchanged by the contract freshness gate. |
| `ventiq_framework.yaml` | authoritative | 0 | 7 | y | **keep** | Live feature layer. |
| `ventiq_profile.yaml` | alias | 12 | 0 | — | **delete** | Feature alias with no live consumer; resolved composition proven unchanged by the contract freshness gate. |

### `packages/hardware/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `led_ring_ceiling.yaml` | alias | 14 | 3 | — | **delete-and-repoint** | Alias with 3 live consumer(s): re-point each include to the board package it resolves to, then delete; compositions must come out byte-identical (contract gate). |
| `led_ring_mic_ceiling.yaml` | alias | 14 | 0 | — | **fold** | Published half of the S360-LED-V-C fold pair. |
| `power_240v.yaml` | authoritative | 14 | 0 | — | **delete-if-orphan** | Published historically but no live consumer; charter aggressive posture applies — verify no legacy catalogued product resolves through it, then delete. |
| `power_management.yaml` | authoritative | 14 | 0 | — | **delete-if-orphan** | Published historically but no live consumer; charter aggressive posture applies — verify no legacy catalogued product resolves through it, then delete. |
| `power_poe.yaml` | alias | 14 | 18 | y | **delete-and-repoint** | Alias with 18 live consumer(s): re-point each include to the board package it resolves to, then delete; compositions must come out byte-identical (contract gate). |
| `power_usb.yaml` | authoritative | 14 | 3 | y | **keep** | Authoritative and consumed. |
| `presence_dfrobot_c4001.yaml` | authoritative | 14 | 0 | — | **delete-if-orphan** | Published historically but no live consumer; charter aggressive posture applies — verify no legacy catalogued product resolves through it, then delete. |
| `presence_ld2412.yaml` | authoritative | 14 | 0 | — | **delete-if-orphan** | Published historically but no live consumer; charter aggressive posture applies — verify no legacy catalogued product resolves through it, then delete. |
| `presence_ld2450.yaml` | authoritative | 14 | 0 | — | **delete-if-orphan** | Published historically but no live consumer; charter aggressive posture applies — verify no legacy catalogued product resolves through it, then delete. |
| `sense360_core.yaml` | authoritative | 14 | 1 | — | **flip** | Core source-of-truth flip: content moves into packages/boards/s360-100-core*, this path goes; the one remaining inverse wrap named in CLAUDE.md. |
| `sense360_core_ceiling.yaml` | authoritative | 14 | 21 | y | **flip** | Core source-of-truth flip: content moves into packages/boards/s360-100-core*, this path goes; the one remaining inverse wrap named in CLAUDE.md. |
| `sense360_core_ceiling_s3.yaml` | authoritative | 14 | 0 | — | **flip** | Core source-of-truth flip: content moves into packages/boards/s360-100-core*, this path goes; the one remaining inverse wrap named in CLAUDE.md. |
| `sense360_core_mapping.yaml` | authoritative | 14 | 0 | — | **flip** | Core source-of-truth flip: content moves into packages/boards/s360-100-core*, this path goes; the one remaining inverse wrap named in CLAUDE.md. |
| `sense360_core_poe.yaml` | authoritative | 14 | 1 | — | **flip** | Core source-of-truth flip: content moves into packages/boards/s360-100-core*, this path goes; the one remaining inverse wrap named in CLAUDE.md. |
| `sense360_core_voice.yaml` | authoritative-with-includes | 14 | 1 | — | **flip** | Core source-of-truth flip: content moves into packages/boards/s360-100-core*, this path goes; the one remaining inverse wrap named in CLAUDE.md. |

### `packages/remote/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `blower-framework.yaml` | authoritative-with-includes | 0 | 0 | — | **deleted** | Remote-consumption wrapper (docs/remote-package-consumption.md): absent from every tag, so consumers can only pin @main; deleting breaks a documented surface. Needs an owner-visible call or fold into the documented canonical paths. |
| `ceiling-airiq.yaml` | authoritative-with-includes | 0 | 0 | — | **keep-protected** | Remote-consumption wrapper (docs/remote-package-consumption.md): absent from every tag, so consumers can only pin @main; deleting breaks a documented surface. Needs an owner-visible call or fold into the documented canonical paths. |
| `ceiling-roomiq-presence.yaml` | authoritative-with-includes | 0 | 0 | — | **keep-protected** | Remote-consumption wrapper (docs/remote-package-consumption.md): absent from every tag, so consumers can only pin @main; deleting breaks a documented surface. Needs an owner-visible call or fold into the documented canonical paths. |
| `led-framework.yaml` | authoritative-with-includes | 0 | 0 | — | **keep-protected** | Remote-consumption wrapper (docs/remote-package-consumption.md): absent from every tag, so consumers can only pin @main; deleting breaks a documented surface. Needs an owner-visible call or fold into the documented canonical paths. |
| `sense360-shared-engines.yaml` | authoritative | 0 | 0 | — | **keep-protected** | Remote-consumption wrapper (docs/remote-package-consumption.md): absent from every tag, so consumers can only pin @main; deleting breaks a documented surface. Needs an owner-visible call or fold into the documented canonical paths. |

### `products/bundles/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `ceiling-poe-airiq-fandac-roomiq.yaml` | authoritative-with-includes | 11 | 1 | y | **keep** | Canonical composition for its config string. |
| `ceiling-poe-airiq-fanpwm-roomiq.yaml` | authoritative-with-includes | 11 | 1 | y | **keep** | Canonical composition for its config string. |
| `ceiling-poe-airiq-fanrelay-roomiq.yaml` | authoritative-with-includes | 11 | 1 | y | **keep** | Canonical composition for its config string. |
| `ceiling-poe-airiq-roomiq.yaml` | authoritative-with-includes | 12 | 1 | y | **keep** | Canonical composition for its config string. |
| `ceiling-poe-fandac.yaml` | authoritative-with-includes | 12 | 1 | y | **keep** | Canonical composition for its config string. |
| `ceiling-poe-fanpwm.yaml` | authoritative-with-includes | 12 | 1 | y | **keep** | Canonical composition for its config string. |
| `ceiling-poe-roomiq-led.yaml` | authoritative-with-includes | 12 | 1 | y | **keep** | Canonical composition for its config string. |
| `ceiling-poe-roomiq.yaml` | authoritative-with-includes | 12 | 1 | y | **keep** | Canonical composition for its config string. |
| `ceiling-poe-ventiq-fandac-roomiq.yaml` | authoritative-with-includes | 11 | 1 | y | **keep** | Canonical composition for its config string. |
| `ceiling-poe-ventiq-fanpwm-roomiq.yaml` | authoritative-with-includes | 11 | 1 | y | **keep** | Canonical composition for its config string. |
| `ceiling-poe-ventiq-fanrelay-roomiq.yaml` | authoritative-with-includes | 12 | 1 | y | **keep** | Canonical composition for its config string. |
| `ceiling-poe-ventiq-fantriac-roomiq.yaml` | authoritative-with-includes | 12 | 1 | y | **keep** | Canonical composition for its config string. |
| `ceiling-poe-ventiq-roomiq-led.yaml` | authoritative-with-includes | 12 | 1 | y | **keep** | Canonical composition for its config string. |
| `ceiling-poe-ventiq-roomiq.yaml` | authoritative-with-includes | 12 | 1 | y | **keep** | Canonical composition for its config string. |
| `ceiling-usb-roomiq.yaml` | authoritative-with-includes | 12 | 1 | y | **keep** | Canonical composition for its config string. |
| `ceiling-usb-ventiq-roomiq.yaml` | authoritative-with-includes | 12 | 1 | y | **keep** | Canonical composition for its config string. |

### `products/compile-only/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `ceiling-poe-airiq-roomiq.yaml` | authoritative-with-includes | 12 | 0 | — | **keep** | Compile-only skeleton declared in config/compile-only-targets.json. |
| `ceiling-poe-airiq.yaml` | authoritative-with-includes | 12 | 0 | y | **keep** | Compile-only skeleton declared in config/compile-only-targets.json. |
| `ceiling-poe-fandac.yaml` | authoritative-with-includes | 12 | 0 | — | **keep** | Compile-only skeleton declared in config/compile-only-targets.json. |
| `ceiling-poe-fanpwm-native.yaml` | authoritative-with-includes | 12 | 0 | — | **keep** | Compile-only skeleton declared in config/compile-only-targets.json. |
| `ceiling-poe-fanpwm.yaml` | authoritative-with-includes | 12 | 0 | — | **keep** | Compile-only skeleton declared in config/compile-only-targets.json. |
| `ceiling-poe-roomiq.yaml` | authoritative-with-includes | 12 | 0 | — | **keep** | Compile-only skeleton declared in config/compile-only-targets.json. |
| `ceiling-poe-ventiq.yaml` | authoritative-with-includes | 12 | 0 | y | **keep** | Compile-only skeleton declared in config/compile-only-targets.json. |
| `ceiling-poe.yaml` | authoritative-with-includes | 12 | 0 | y | **keep** | Compile-only skeleton declared in config/compile-only-targets.json. |

### `products/secrets.example.yaml/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `secrets.example.yaml` | authoritative | 11 | 0 | — | **keep** | Customer include path (protected canonical entrypoint or catalogued legacy template). |

### `products/sense360-ceiling-poe-airiq-fandac-roomiq.yaml/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `sense360-ceiling-poe-airiq-fandac-roomiq.yaml` | alias | 11 | 1 | y | **keep** | Customer include path (protected canonical entrypoint or catalogued legacy template). |

### `products/sense360-ceiling-poe-airiq-fanpwm-roomiq.yaml/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `sense360-ceiling-poe-airiq-fanpwm-roomiq.yaml` | alias | 11 | 1 | y | **keep** | Customer include path (protected canonical entrypoint or catalogued legacy template). |

### `products/sense360-ceiling-poe-airiq-fanrelay-roomiq.yaml/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `sense360-ceiling-poe-airiq-fanrelay-roomiq.yaml` | alias | 11 | 1 | y | **keep** | Customer include path (protected canonical entrypoint or catalogued legacy template). |

### `products/sense360-ceiling-poe-airiq-roomiq.yaml/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `sense360-ceiling-poe-airiq-roomiq.yaml` | alias | 12 | 1 | y | **keep** | Customer include path (protected canonical entrypoint or catalogued legacy template). |

### `products/sense360-ceiling-poe-fandac.yaml/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `sense360-ceiling-poe-fandac.yaml` | alias | 12 | 1 | y | **keep** | Customer include path (protected canonical entrypoint or catalogued legacy template). |

### `products/sense360-ceiling-poe-fanpwm.yaml/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `sense360-ceiling-poe-fanpwm.yaml` | alias | 12 | 1 | y | **keep** | Customer include path (protected canonical entrypoint or catalogued legacy template). |

### `products/sense360-ceiling-poe-roomiq-led.yaml/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `sense360-ceiling-poe-roomiq-led.yaml` | alias | 12 | 1 | y | **keep** | Customer include path (protected canonical entrypoint or catalogued legacy template). |

### `products/sense360-ceiling-poe-roomiq.yaml/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `sense360-ceiling-poe-roomiq.yaml` | alias | 12 | 1 | y | **keep** | Customer include path (protected canonical entrypoint or catalogued legacy template). |

### `products/sense360-ceiling-poe-ventiq-fandac-roomiq.yaml/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `sense360-ceiling-poe-ventiq-fandac-roomiq.yaml` | alias | 11 | 1 | y | **keep** | Customer include path (protected canonical entrypoint or catalogued legacy template). |

### `products/sense360-ceiling-poe-ventiq-fanpwm-roomiq.yaml/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `sense360-ceiling-poe-ventiq-fanpwm-roomiq.yaml` | alias | 11 | 1 | y | **keep** | Customer include path (protected canonical entrypoint or catalogued legacy template). |

### `products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml` | alias | 12 | 1 | y | **keep** | Customer include path (protected canonical entrypoint or catalogued legacy template). |

### `products/sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `sense360-ceiling-poe-ventiq-fantriac-roomiq.yaml` | alias | 14 | 1 | y | **keep** | Customer include path (protected canonical entrypoint or catalogued legacy template). |

### `products/sense360-ceiling-poe-ventiq-roomiq-led.yaml/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `sense360-ceiling-poe-ventiq-roomiq-led.yaml` | alias | 13 | 1 | y | **keep** | Customer include path (protected canonical entrypoint or catalogued legacy template). |

### `products/sense360-ceiling-poe-ventiq-roomiq.yaml/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `sense360-ceiling-poe-ventiq-roomiq.yaml` | alias | 14 | 1 | y | **keep** | Customer include path (protected canonical entrypoint or catalogued legacy template). |

### `products/sense360-ceiling-usb-roomiq.yaml/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `sense360-ceiling-usb-roomiq.yaml` | alias | 12 | 0 | y | **keep** | Customer include path (protected canonical entrypoint or catalogued legacy template). |

### `products/sense360-ceiling-usb-ventiq-roomiq.yaml/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `sense360-ceiling-usb-ventiq-roomiq.yaml` | alias | 12 | 0 | y | **keep** | Customer include path (protected canonical entrypoint or catalogued legacy template). |

### `products/sense360-core-c-poe.yaml/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `sense360-core-c-poe.yaml` | authoritative-with-includes | 14 | 0 | — | **keep** | Customer include path (protected canonical entrypoint or catalogued legacy template). |

### `products/sense360-core-c-usb.yaml/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `sense360-core-c-usb.yaml` | authoritative-with-includes | 14 | 0 | — | **keep** | Customer include path (protected canonical entrypoint or catalogued legacy template). |

### `products/sense360-core-ceiling-airiq-blower.yaml/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `sense360-core-ceiling-airiq-blower.yaml` | authoritative-with-includes | 0 | 0 | y | **keep** | Customer include path (protected canonical entrypoint or catalogued legacy template). |

### `products/sense360-core-ceiling-bathroom.yaml/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `sense360-core-ceiling-bathroom.yaml` | authoritative-with-includes | 14 | 0 | — | **keep** | Customer include path (protected canonical entrypoint or catalogued legacy template). |

### `products/sense360-core-ceiling-presence.yaml/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `sense360-core-ceiling-presence.yaml` | authoritative-with-includes | 14 | 0 | — | **keep** | Customer include path (protected canonical entrypoint or catalogued legacy template). |

### `products/sense360-core-ceiling.yaml/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `sense360-core-ceiling.yaml` | authoritative-with-includes | 14 | 0 | — | **keep** | Customer include path (protected canonical entrypoint or catalogued legacy template). |

### `products/sense360-fan-pwm.yaml/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `sense360-fan-pwm.yaml` | authoritative-with-includes | 14 | 0 | — | **keep** | Customer include path (protected canonical entrypoint or catalogued legacy template). |

### `products/sense360-poe.yaml/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `sense360-poe.yaml` | authoritative-with-includes | 14 | 0 | — | **keep** | Customer include path (protected canonical entrypoint or catalogued legacy template). |

### `products/webflash/`

| Path | Role | Tags | Consumers | Reach | Disposition | Basis |
|---|---|---|---|---|---|---|
| `ceiling-poe-airiq-fandac-roomiq.yaml` | alias | 0 | 0 | — | **keep (declared build address)** | Release-gate wrapper never published at any tag; keep only if a config declaration (webflash-builds / preview-release-targets / catalog webflash_wrapper) addresses it, else delete. |
| `ceiling-poe-airiq-fanpwm-roomiq.yaml` | alias | 0 | 0 | — | **keep (declared build address)** | Release-gate wrapper never published at any tag; keep only if a config declaration (webflash-builds / preview-release-targets / catalog webflash_wrapper) addresses it, else delete. |
| `ceiling-poe-airiq-fanrelay-roomiq.yaml` | alias | 0 | 0 | — | **keep (declared build address)** | Release-gate wrapper never published at any tag; keep only if a config declaration (webflash-builds / preview-release-targets / catalog webflash_wrapper) addresses it, else delete. |
| `ceiling-poe-airiq-roomiq.yaml` | alias | 12 | 0 | — | **keep** | Release-gate wrapper addressed by the declaration layer. |
| `ceiling-poe-fandac.yaml` | alias | 0 | 0 | — | **keep (declared build address)** | Release-gate wrapper never published at any tag; keep only if a config declaration (webflash-builds / preview-release-targets / catalog webflash_wrapper) addresses it, else delete. |
| `ceiling-poe-fanpwm.yaml` | alias | 0 | 0 | — | **keep (declared build address)** | Release-gate wrapper never published at any tag; keep only if a config declaration (webflash-builds / preview-release-targets / catalog webflash_wrapper) addresses it, else delete. |
| `ceiling-poe-roomiq-led.yaml` | alias | 12 | 0 | — | **keep** | Release-gate wrapper addressed by the declaration layer. |
| `ceiling-poe-roomiq.yaml` | alias | 12 | 0 | — | **keep** | Release-gate wrapper addressed by the declaration layer. |
| `ceiling-poe-ventiq-fandac-roomiq.yaml` | alias | 0 | 0 | — | **keep (declared build address)** | Release-gate wrapper never published at any tag; keep only if a config declaration (webflash-builds / preview-release-targets / catalog webflash_wrapper) addresses it, else delete. |
| `ceiling-poe-ventiq-fanpwm-roomiq.yaml` | alias | 0 | 0 | — | **keep (declared build address)** | Release-gate wrapper never published at any tag; keep only if a config declaration (webflash-builds / preview-release-targets / catalog webflash_wrapper) addresses it, else delete. |
| `ceiling-poe-ventiq-fanrelay-roomiq.yaml` | alias | 0 | 0 | — | **keep (declared build address)** | Release-gate wrapper never published at any tag; keep only if a config declaration (webflash-builds / preview-release-targets / catalog webflash_wrapper) addresses it, else delete. |
| `ceiling-poe-ventiq-fantriac-roomiq.yaml` | alias | 14 | 0 | — | **keep** | Release-gate wrapper addressed by the declaration layer. |
| `ceiling-poe-ventiq-roomiq-led.yaml` | alias | 13 | 0 | — | **keep** | Release-gate wrapper addressed by the declaration layer. |
| `ceiling-poe-ventiq-roomiq.yaml` | alias | 14 | 0 | — | **keep** | Release-gate wrapper addressed by the declaration layer. |

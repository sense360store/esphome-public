# sense360_led component migration plan (SENSE360-CANONICALISATION-001 PR 12)

**Canonical id:** `SENSE360-CANONICALISATION-001` PR 12
**Type:** Migration plan of record, committed before implementation. Charter
scope: *introduce `sense360_led`; reconcile the Relay / PWM / DAC advanced
paths; keep TRIAC isolated and experimental; remove obsolete blower and fan
wrappers with no valid consumer.* Two carried inputs from PR 07 land here:
the LED framework's `esphome: includes:` mechanism (twice recorded as
PR 12's to replace) and the Blower-surface / `Core`-token decisions.

## Starting truth

The LED behaviour model is already extracted and natively tested
(`components/sense360/led_controller.h` + `led_logic.h`); the glue lives in
`packages/features/led_framework.yaml` — the PR 09/10/11 shape, including
the LED framework's direct read of `sense360::roomiq::global_engine()` for
its darkness service (LED-FRAMEWORK-002), which must keep working with and
without the RoomIQ framework composed.

## Contracts that survive unchanged

1. **Entity contract.** Every entity id and name preserved; equivalence
   bar: composition contract and entity tables byte-identical.
2. **Singleton contracts.** The component wraps
   `sense360::led::global_engine()` (exact namespace confirmed at
   implementation) and keeps the darkness service's direct RoomIQ
   singleton read semantics: with no lux input the engine reports
   darkness-unknown — it never invents darkness.
3. **LED stays preview.** No LED-stable claim, no Release-One change, no
   WebFlash exposure change. The LED includes mechanism is replaced by
   component delivery (the co-location hazard class disappears
   structurally).
4. **TRIAC isolated and experimental — verified, not touched.** The
   FanTRIAC pins, blockers and status are human-review-only by standing
   rule; PR 12 changes none of them and only verifies the existing gates
   still hold (catalog status, no WebFlash row beyond the experimental
   lane, the import-block downstream).

## Advanced fan paths (Relay / PWM / DAC) — reconciliation posture

These are driver-output packages behind hardware-evidence gates, not
engine-glue frameworks: there is no extracted engine to migrate, and their
respective bundles compile in the hosted lane. Reconciliation here means:
each path's composition against the component world is verified (FanRelay
proxies the Core `main_relay` through substitution; FanPWM native and
FanDAC bind the shared `core_i2c`), their dispositions are recorded, and
any wrapper with **no valid consumer** is removed under the PR 07 owner
evidence test. `FANDAC-I2C-ADDR-001` stays PENDING and `0x59` stays
forbidden with VentIQ/AirIQ present — unchanged.

## Blower surface and the `Core` token (carried decisions)

- **Blower framework and its compile-only fixture STAY.** The charter
  removes blower wrappers *with no valid consumer*; the framework's
  consumer is the declared compile-only fixture
  (`Ceiling-Core-AirIQ-Blower`, registered in
  `config/compile-only-targets.json` — the pre-hardware buildability lane
  for the real S360-100-R4 FAN net, bench pending). The unconsumed remote
  wrapper was already deleted in PR 07. The blower framework's own
  component migration is deliberately deferred (no charter PR owns it; it
  ships nothing).
- **The non-canonical `Core` / `Blower` tokens** in that compile-only
  config string are resolved during execution against the SOT grammar
  facts: a compile-only-lane rename is repository-internal; if the
  canonical grammar cannot express the fixture, the tokens are recorded as
  compile-only-lane-only with a guard, never silently left as drift.

## Component boundary (settled against the pinned APIs, 2026-07-28)

The pinned light API (`remote_values` / `make_call` / `get_effect_name`)
supports full component ownership of the customer-intent arbitration and
the arbitrated apply. The engine's `input_occupancy` stores state without
timestamps, so event-driven feeding is semantically identical to the old
per-tick global reads. Therefore:

- **Component owns**: the 250 ms tick; engine configuration from the bound
  night-behaviour / status-indicator selects and darkness-threshold number
  plus config scalars; the darkness service (RoomIQ singleton read,
  unchanged semantics); customer-intent arbitration and the arbitrated
  light apply (light bound by id; effect names unchanged); the diagnostics
  switchboard; a `mark_booted()` gate the YAML restore hook calls.
- **YAML keeps**: every persisted global and the boot-restore hook (NVS
  identity protected; it calls `mark_booted()` then the bridge script);
  the api/wifi notify hooks and the identify button (engine-action
  one-liners); the night-mode switch (engine-truth lambda); a 1 s
  stable-state persistence lambda mirroring `customer_state()` into the
  saved globals (idempotent; replaces the in-evaluate writes with the same
  values and the same NVS cadence).
- **`led_presence_bridge.yaml` feeds the controller directly** on its
  Occupancy callbacks (`input_occupancy`), retiring the two transient
  `s360_led_occupied` / `s360_led_occupancy_valid` globals nothing else
  reads — same physical signal, one hop earlier, no globals binding
  machinery needed.

## Slices

1. `sense360_led` component + `led_framework.yaml` rewrite (includes
   mechanism replaced by component delivery) + equivalence proof + guard
   retargeting. **Executed 2026-07-29.** Execution notes: the component
   binds the Room Light, both selects and the darkness-threshold number by
   id and re-evaluates on their callbacks (the YAML `on_value` hooks
   retired with the tick and the evaluate script's switchboard); the boot
   gate is component-owned (`mark_booted()` called by the restore hook,
   queried by the new 1 s YAML persistence mirror so unrestored state can
   never overwrite NVS); the presence bridge feeds `input_occupancy`
   directly via `!extend` hooks on the fused contract entities, retiring
   the two RAM-only copy globals; the core-framework composition walker
   learned to skip `!extend` patches (they reference, never declare).
   Equivalence: composition contract, firmware matrix and entity tables
   all byte-identical; hosted compile lane green on the restacked head
   (all eight representatives including both LED products), first attempt.

2. Fan-path reconciliation records + wrapper evidence pass + TRIAC gate
   verification; the Blower / `Core`-token resolution. **Executed
   2026-07-29.** Reconciliation record (dispositions, all KEEP — no fan
   surface qualified for removal under the PR 07 owner evidence test):
   - **FanRelay** (`packages/expansions/fan_relay.yaml`): proxies the Core
     `main_relay` abstraction through a template switch, exactly as before
     the component migrations; consumed by both FanRelay bundles;
     `config/webflash-builds.json` rows on the **experimental** channel
     only. Unchanged.
   - **FanPWM** (`fan_pwm.yaml` + `fan_pwm_native.yaml` +
     `fan_pwm_sx1509.yaml` + `sense360_fan_pwm.yaml` +
     `gpio_expander_sx1509.yaml`): every file has live composers (bundles,
     compile-only skeletons, feature profiles, the catalogued legacy
     `products/sense360-fan-pwm.yaml`); rows on the **preview** channel.
     Unchanged.
   - **FanDAC** (`fan_gp8403.yaml`): binds the shared `core_i2c` bus via
     the `fan_dac_i2c_id` substitution; consumed by all three FanDAC
     bundles plus catalogued legacy products; rows on the **preview**
     channel. `FANDAC-I2C-ADDR-001` stays PENDING and `0x59` stays
     forbidden with VentIQ/AirIQ present — untouched.
   - **FanTRIAC** (`fan_triac.yaml`): exactly one consumer (the FanTRIAC
     bundle) — isolation verified. Gate verification (verify only, no pin
     / blocker / status change): catalog row carries the full
     experimental-self-build-mains posture with every `never_*` pin true
     and `webflash_one_click_import_eligible: false`; the build-matrix row
     is **experimental** channel only; read-only observation of the
     WebFlash working tree shows all four `firmware/sources.json` entries
     carry `FanTRIAC` in `block_tokens` (source-inspection evidence of the
     distribution declaration only — not a runtime or release claim). The
     human-review-only standing rule is respected: nothing TRIAC changed.
   - **Wrapper evidence pass**: all nine fan `products/webflash/` wrappers
     are the `product_yaml` addresses of committed build-matrix rows
     (ESP-007 declared infrastructure); the unconsumed blower remote
     wrapper was already deleted in PR 07; no wrapper is removable under
     the evidence test.
   - **Blower / `Core`-token resolution**: the canonical grammar cannot
     express the fixture — `Blower` is not in `canonical_modules` and
     `Core` is not in `canonical_power` — so the tokens are recorded as
     **compile-only-lane-only** with a guard
     (`tests/test_blower_framework.py::LaneOnlyTokenTests`): the
     non-canonical facts, the string's absence from every release surface,
     and the target's null `config_string` are all pinned, so
     canonicalising either token or surfacing the string forces a
     deliberate owner-visible revisit instead of drift. The blower
     framework and its compile-only fixture stay (declared consumer:
     `products/sense360-core-ceiling-airiq-blower.yaml`, target
     `ceiling-core-airiq-blower-compile-only`); its own component
     migration stays deliberately deferred.

3. Docs, execution notes here, final suite / validator pass, PR. Hosted
   compile lane gates each slice.

## Honesty limits

Nothing builds, publishes, tags, promotes, or changes channel / lifecycle /
commercial state. LED stays preview with no LED-stable claim; FanTRIAC
stays blocked/experimental with no electrical-safety / EMC / compliance
claim; fans are never stable (HW-RELEASE-001). Compile / simulation success
is buildability proof only. Release-One stays the production stable
customer baseline.

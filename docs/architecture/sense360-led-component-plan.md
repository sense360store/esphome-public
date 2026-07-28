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

## Slices

1. `sense360_led` component + `led_framework.yaml` rewrite (includes
   mechanism replaced by component delivery) + equivalence proof + guard
   retargeting.
2. Fan-path reconciliation records + wrapper evidence pass + TRIAC gate
   verification; the Blower / `Core`-token resolution.
3. Docs, execution notes here, final suite / validator pass, PR. Hosted
   compile lane gates each slice.

## Honesty limits

Nothing builds, publishes, tags, promotes, or changes channel / lifecycle /
commercial state. LED stays preview with no LED-stable claim; FanTRIAC
stays blocked/experimental with no electrical-safety / EMC / compliance
claim; fans are never stable (HW-RELEASE-001). Compile / simulation success
is buildability proof only. Release-One stays the production stable
customer baseline.

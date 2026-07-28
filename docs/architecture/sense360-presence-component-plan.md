# sense360_presence component migration plan (SENSE360-CANONICALISATION-001 PR 10)

**Canonical id:** `SENSE360-CANONICALISATION-001` PR 10
**Type:** Migration plan of record, committed before implementation. Charter
scope: *introduce `sense360_presence`; migrate PIR and radar fusion;
preserve the evidence distinction between the PCB-mounted PIR and the
connector-attached radars (OD-SOT-004 stays open).* The manifest
(`config/external-components.json`) also assigns the vendored radar trio's
disposition to PR 10.

## Starting truth

The tri-sensor fusion model (PIR + LD2450 radar + SEN0609 static, mode
arbitration, freshness, module health PD-07) already lives in the natively
tested header engine
[`components/sense360/presence_fusion.h`](../../components/sense360/presence_fusion.h)
(PRESENCE-FRAMEWORK-001). What remains in YAML is the glue in
[`packages/features/presence_framework.yaml`](../../packages/features/presence_framework.yaml):
the `s360_presence_evaluate` script, input feeding, template entities and
per-number `on_value` hooks — the same shape PR 09 migrated for RoomIQ, and
this plan replays that playbook.

## Contracts that survive unchanged

1. **Entity contract.** Every entity id and name in the framework is
   preserved exactly. Equivalence bar: regenerated entity tables and the
   composition contract byte-identical (the PR 09 standard).
2. **Singleton contract.** The component wraps and feeds the SAME
   `sense360::presence::global_engine()` fusion singleton — never a private
   instance.
3. **Adapter contract.** The PIR and SEN0609 board adapters
   (`packages/boards/s360-200-roomiq-pir.yaml`, `…-sen0609.yaml`) call
   `script.execute: s360_presence_evaluate` on their sensor edges and are
   NOT modified by this PR: the framework keeps a one-line compatibility
   script of the same id that bridges into the component's evaluate. That
   script is live glue (the adapters' documented layering contract), not a
   dead path.
4. **Evidence distinction (OD-SOT-004, stays open).** The PCB-mounted PIR
   versus connector-attached radar distinction is encoded in the framework's
   honesty diagnostics and the engine's health model; the migration moves
   mechanics only and changes no evidence claim, no health vocabulary and
   no diagnostic wording.

## Radar driver disposition (the no-fork rule applied)

The pinned ESPHome (2026.4.5) ships **built-in** `ld2412`, `ld2450` and
`ld24xx` components. Local evidence (2026-07-28, this container, pinned
version): with the vendored git entry removed, `esphome config` passes for
**every live composition** — all seven representative compile-lane products,
the FanRelay / FanDAC / FanPWM bundles, and the three legacy products that
compose the LD2412-documented path. Therefore PR 10 retires the vendored
trio per the manifest's assigned disposition and the no-fork rule:

- delete `components/ld2412`, `components/ld2450`, `components/ld24xx`;
- remove the radar git entry from `packages/base/external_components.yaml`
  and the radar names from the CI override heredocs (the delivery-axis
  guard forces both to track the manifest);
- remove the manifest rows (the completeness guard forces this with the
  directory deletions);
- record in `docs/` where the radars now come from (built-in ESPHome ≥ the
  pinned version; remote consumers get them natively — a min-version note
  goes in the remote consumption guide);
- release tags keep the vendored trees for tag-pinned consumers.

Hosted compile proof gates the retirement: schema validation is local
evidence only; the compile lane must build the radar-bearing
representatives against the built-in drivers before the acceptance request
names a head. If the compile lane rejects the built-ins, the fallback is
recorded here in the execution notes: keep the vendored trio with refreshed
provenance and a named blocker — never a silent retention.

## Component shape (PR 09 playbook)

`components/sense360_presence/` — hub `__init__.py` (source bindings for
the PIR / radar-target / static inputs and the tuning numbers, windows and
mode defaults equal to today's substitution defaults verbatim),
`sense360_presence.h/.cpp` glue (feed callbacks, evaluate tick, publish
switchboard, module-status binding by id — the Core Framework owns that
entity), `sensor.py` / `text_sensor.py` / `binary_sensor.py` platform
modules as the entity surface requires. Manifest row `delivery: base`;
CI heredocs updated (guard-forced). The framework YAML shrinks onto the
component with the superseded glue deleted in the same commit.

## Slices

1. Radar retirement (built-in flip) with hosted compile proof.
2. Component skeleton + platforms.
3. Framework rewrite + equivalence proof + guard retargeting.
4. Docs, execution notes here, final suite / validator pass, PR.

## Honesty limits

Nothing builds, publishes, tags, promotes, or changes channel / lifecycle /
commercial state. OD-SOT-004 and every bench-pending question stay open;
compile / config / simulation success is buildability proof only. Release-One
stays the production stable customer baseline.

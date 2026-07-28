# sense360_roomiq component migration plan (SENSE360-CANONICALISATION-001 PR 09)

**Canonical id:** `SENSE360-CANONICALISATION-001` PR 09
**Type:** Migration plan of record, committed before implementation so every
slice executes against a written contract. Charter scope: *introduce
`sense360_roomiq`; move compensation, vapour-pressure logic, freshness,
calibration and canonical publication out of large YAML lambdas; preserve
stable customer entities; remove duplicate implementations only after
equivalence tests. Current SHT45 compensation constants stay provisional
engineering values.*

## Starting truth (what is already migrated, what is not)

The environmental model itself — compensation
(`S360_200_R4_CLIMATE_PROFILE_V1`), the vapour-pressure-preserving
psychrometric humidity model, freshness/pair-coherence, calibration
clamping, comfort/brightness/environment classification — ALREADY lives in
the header-only engines
[`components/sense360/roomiq_engine.h`](../../components/sense360/roomiq_engine.h)
and
[`components/sense360/roomiq_climate_compensation.h`](../../components/sense360/roomiq_climate_compensation.h),
natively tested by `tests/unit/test_roomiq_engine.cpp` and
`test_roomiq_climate_compensation.cpp` (ROOMIQ-FRAMEWORK-001,
S360-200-R4-CLIMATE-COMPENSATION-001). What still lives in YAML lambdas in
[`packages/features/roomiq_framework.yaml`](../../packages/features/roomiq_framework.yaml)
is the **glue**: threshold/window pushing from substitutions, input feeding
from the three copy sensors, the single-owner publication switchboard
(`s360_roomiq_evaluate`), the calibration-schema migration block, and the
legacy compatibility lambdas. PR 09 replaces that glue with a real ESPHome
component; it does NOT rewrite the engines.

## Two contracts that must survive unchanged

1. **Entity contract.** Every entity id and name in the framework today is
   preserved exactly (canonical `s360_temperature` / `s360_humidity` /
   `s360_illuminance`, the state text sensors, the diagnostics, the three
   calibration numbers, the `comfort_*` legacy set). VentIQ consumes RoomIQ
   through the `s360_humidity` / `s360_temperature` entity ids
   (`packages/features/ventiq_framework.yaml` substitutions) and Home
   Assistant installs pin the ids. Equivalence is proven by
   `tests/test_roomiq_framework.py` (updated to read the new declaration
   shape but asserting the same ids / names / units / classes / categories /
   disabled flags) and the regenerated entity tables showing an identical
   entity surface.
2. **Singleton contract.** The LED framework reads
   `sense360::roomiq::global_engine()` directly
   (`packages/features/led_framework.yaml`). The component therefore wraps
   and feeds the SAME `global_engine()` singleton — it never holds a private
   engine instance. Cross-framework consumers keep reading exactly what they
   read today.

## Component shape

`components/sense360_roomiq/` (new; manifest row required — the PR 08
manifest guard forces it):

- `__init__.py` — `sense360_roomiq:` hub schema: the three source sensor
  IDs (`temperature_source` / `humidity_source` / `illuminance_source`),
  freshness windows, pair skew, comfort / humidity / brightness bands and
  hysteresis, calibration schema version. Defaults equal the current
  substitution defaults verbatim. Codegen registers the hub component.
- `sense360_roomiq.h/.cpp` — `Sense360RoomIQ : public esphome::Component`:
  subscribes to the three sources via `add_on_state_callback`, feeds
  `global_engine()`, owns the 5 s evaluation tick (`set_interval`), the
  single-owner publish-on-change switchboard into registered entities, and
  the calibration-schema one-time migration (reads the persisted global via
  an ESPHome `globals` binding preserved in YAML, or a component-owned
  preference — decided in implementation with the same
  never-guess-from-values rule).
- `sensor.py` / `text_sensor.py` / `number.py` — platform modules declaring
  the component-owned entities by `type:` (e.g. `type: temperature`,
  `type: comfort`, `type: temperature_offset`), each preserving today's id,
  name, unit, device class, state class, icon, category and
  disabled-by-default flag through the framework YAML declarations.
- The foundation boundary is unchanged: `components/sense360/` stays
  logic-and-schema only (its no-platform guard is untouched);
  `sense360_roomiq` is where platforms belong.

`packages/features/roomiq_framework.yaml` shrinks to: the component config
block, the entity declarations on the new platforms (same ids/names), the
raw copy diagnostics (plain `copy` sensors, unchanged), and the honesty
text that is compile-time static. The `s360_roomiq_evaluate` script, the
input copy-sensor lambdas, the `on_boot` engine lambdas and the migration
block are DELETED in the same slice their replacement lands (no dead
simulated paths).

## Slices

1. Component skeleton: hub `__init__.py` + C++ component wrapping
   `global_engine()`, manifest row, guard updates. Compile-lane proof.
   **Executed 2026-07-28.**
2. Platform modules + entity registration; framework YAML rewritten onto
   the component; superseded glue deleted in the same commit; equivalence
   proof (entity surface identical; `test_roomiq_framework.py` updated;
   entity tables regenerated with zero entity-surface diff).
   **Executed 2026-07-28.** Execution notes: the calibration numbers and
   the persisted schema-migration block stayed in YAML exactly as this
   plan's contract section requires (entity ids and NVS restore identity
   preserved); the illuminance median filter survives on the internal
   sample the component binds; component delivery for repository builds
   is a LOCAL `../components` source appended to
   `packages/base/external_components.yaml` (every build lane compiles
   with `products/` as the config directory, so a PR branch compiles its
   own component code, never main's), while the remote wrapper's git
   source gained `sense360_roomiq`; the deleted internal
   temperature/humidity sample copies were internal-only (no visible
   entity change). Equivalence result: the regenerated entity tables and
   the composition contract both came out byte-identical.
3. Docs (`sense360-roomiq-framework.md` needed no change — it describes
   outputs, not mechanics; this plan marked executed), final suite /
   validator pass, PR. The hosted compile lane is the remaining proof
   gate for the codegen + C++ glue.

## Honesty limits

The SHT45 compensation constants stay provisional engineering values — the
migration moves no constant and changes no value. Compile / simulation
success is buildability proof only. No entity value semantics change; the
only permitted diffs are declaration mechanics (template-plus-lambda →
component-owned publication). Nothing here builds, publishes, tags,
promotes, or changes channel / lifecycle / commercial state; Release-One
stays the production stable customer baseline.

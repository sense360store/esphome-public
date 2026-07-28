# sense360_airiq / sense360_ventiq component migration plan (SENSE360-CANONICALISATION-001 PR 11)

**Canonical id:** `SENSE360-CANONICALISATION-001` PR 11
**Type:** Migration plan of record, committed before implementation. Charter
scope: *introduce separate AirIQ and VentIQ components; preserve S360-210
and S360-211 as separate physical boards; remove obsolete or unsupported
inherited drivers; preserve the unresolved SFA40 status (OD-SOT-008);
enforce AirIQ / VentIQ mutual exclusion.*

## Starting truth

Both air-quality models are already extracted and natively tested:
[`components/sense360/airiq_engine.h`](../../components/sense360/airiq_engine.h)
(AIRIQ-FRAMEWORK-001) and
[`components/sense360/ventiq_engine.h`](../../components/sense360/ventiq_engine.h)
(VENTIQ-FRAMEWORK-001, which embeds the canonical AirIQ engine for its
headline — one pollutant-truth implementation). What remains in YAML is the
glue in `packages/features/airiq_framework.yaml` and
`packages/features/ventiq_framework.yaml` — the PR 09/10 shape, migrated
with the same playbook, one component per framework.

## Contracts that survive unchanged

1. **Entity contract.** Every entity id and name in both frameworks
   preserved exactly; equivalence bar: composition contract and entity
   tables byte-identical.
2. **Singleton contracts.** `sense360::airiq::global_engine()` is the
   blower framework's demand producer (BLOWER-FRAMEWORK-001 reads it
   directly) and the VentIQ engine's embedded pollutant truth;
   `sense360::ventiq::global_engine()` is the VentIQ framework's own
   engine. Both components wrap the same singletons — never private
   instances.
3. **Separate boards, separate components.** S360-210 (AirIQ) and S360-211
   (VentIQ) stay separate physical boards with separate domain components;
   nothing merges them. VentIQ keeps consuming RoomIQ humidity /
   temperature through the `s360_humidity` / `s360_temperature` entity ids
   (never the drifted on-board drivers, VENTIQ-HW-DRIFT-001).
4. **OD-SOT-008 stays open.** The SFA40 fitment question is owner-reserved.
   The `sfa40` driver's disposition is decided by evidence: if any live
   composition uses `platform: sfa40`, it stays vendored with refreshed
   provenance; the manifest row and honesty text move nowhere without that
   evidence. Same test for `mics_stm8`. "Remove obsolete or unsupported
   inherited drivers" applies only to drivers with zero live composers AND
   no documented customer entrypoint (the PR 07 owner evidence test).
5. **Mutual exclusion, machine-enforced.** AirIQ and VentIQ are mutually
   exclusive per composition. Today that rule lives in documentation and
   the WebFlash wizard; PR 11 adds a repository guard asserting no bundle
   or product composes both the S360-210 and S360-211 board packages.

## Slices

1. `sense360_airiq` component + `airiq_framework.yaml` rewrite +
   equivalence proof + guard retargeting. **Executed 2026-07-28.**
2. `sense360_ventiq` component + `ventiq_framework.yaml` rewrite +
   equivalence proof + guard retargeting. **Executed 2026-07-28.**
   Execution notes: the manual-action buttons stay YAML engine-action
   lambdas on their preserved legacy entities, re-evaluating through the
   bridge; the three wired customer numbers and the shower-detection
   switch stay persisted template entities bound by id; component
   delivery removed the ventiq/airiq header co-location concern entirely
   (the whole component directory ships, so the sibling include always
   resolves).
3. Mutual-exclusion guard; inherited-driver evidence pass; docs and
   execution notes; final suite / validator pass; PR. **Executed
   2026-07-28.** The guard (`tests/test_airiq_ventiq_exclusion.py`) pins
   the exclusion against the generated contract's `board_composition`
   AND the raw bundle sources. Driver evidence: `sfa40` is live
   (`platform: sfa40` in `packages/boards/s360-210-airiq.yaml`) and
   `mics_stm8` is live (its hub block in the same board package) — both
   retained with their manifest provenance unchanged; OD-SOT-008 stays
   open and owner-reserved; nothing qualified as an obsolete inherited
   driver under the evidence test. The hosted compile lane is the
   remaining proof gate.

## Honesty limits

Nothing builds, publishes, tags, promotes, or changes channel / lifecycle /
commercial state. OD-SOT-008 stays open; the MiCS-4514 stays uncalibrated
in copy; every threshold stays a provisional engineering value. Compile /
simulation success is buildability proof only. Release-One stays the
production stable customer baseline.

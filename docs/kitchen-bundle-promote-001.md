# KITCHEN-BUNDLE-PROMOTE-001 — surface the Kitchen Bundle (AirIQ)

**Goal:** the `Ceiling-POE-AirIQ-RoomIQ` firmware is already served (stable)
but hidden as a kit. This programme records the AirIQ sensor-stack bench
evidence, clears the stale G8 evidence gate, restores the canonical
"Kitchen Bundle" guide naming, and surfaces the Kitchen Bundle as the third
kit in WebFlash.

**Owner decisions (2026-07-08):** the AirIQ sensor hardware is
bench-validated (the G8 evidence gates are stale); the canonical
**"Kitchen Bundle"** name (per
[`config/room-bundle-skus.json`](../config/room-bundle-skus.json),
`S360-KIT-KITCHEN-P`) wins over the guides' interim "Air Quality Bundle"
naming; all steps run together with the owner filling the AirIQ proof.

## Rules that never bend

- **Attestations are owner-authored only** — written by the owner, at the
  bench, in their own words. Agents never author, fill, or summarise the
  AirIQ bench proof's capture tables or attestation. The template ships with
  those cells empty
  ([`docs/standing-invariants.md`](standing-invariants.md)).
- **Kitchen promotes to stable-release only when its proof is complete** —
  every step A–E recorded PASS and a non-empty owner-authored section F in
  [`PACKAGE-AIRIQ-001-operator-bench-proof.md`](hardware/PACKAGE-AIRIQ-001-operator-bench-proof.md).
- **Authorship is verified before promotion.** The commits that filled the
  capture tables and attestation must not be agent-authored; if authorship
  is ambiguous, the loop STOPs and asks the owner to confirm.
- **All PRs are held for owner review** — never auto-merged.
- **K4 kit scope is tight.** The WebFlash kit add must not surface any
  hardware-pending config as a kit and must keep the served LED variant
  (`Ceiling-POE-VentIQ-RoomIQ-LED`) hidden (no canonical bundle home).
- **PoE-PSU gates are separate.** The AirIQ proof clears
  `G8-AirIQ-stack-hardware-evidence-SPS30-SGP41-SCD41-BMP390` only; the two
  S360-410 PoE-PSU evidence gates (`G8-PRODUCT-POE-410-001`,
  `G8-S360-410-schematic-status-verified`) are cleared at K2 only if the
  proof or existing evidence covers them — otherwise they stay, noted in
  the K2 PR.

## Step ledger

| Step | Repo | What | Status |
|---|---|---|---|
| K1 | esphome-public | AirIQ bench proof template ([`docs/hardware/PACKAGE-AIRIQ-001-operator-bench-proof.md`](hardware/PACKAGE-AIRIQ-001-operator-bench-proof.md), empty capture tables + empty attestation) + this tracking file. Held PR. | **EXECUTED** — this PR |
| K2 | esphome-public | Promote Kitchen bundle `S360-KIT-KITCHEN-P` stable-candidate → stable-release in `config/room-bundle-skus.json`, clearing the covered G8 evidence gate(s); align catalog/build status fields for `Ceiling-POE-AirIQ-RoomIQ`; contract tests updated. Gated on the completed, owner-attested proof. Held PR. | **SUPERSEDED** — executed under owner declaration HW-RELEASE-001 ([`docs/hw-release-001.md`](hw-release-001.md)): the bench-proof precondition is retired as a release gate; the G8 gates were cleared by owner declaration, HW-RELEASE-001, and the promotion landed in that PR |
| K3 | esphome-public | Revert guide naming to canonical: "Air Quality Bundle (AirIQ + RoomIQ)" → "Kitchen Bundle (AirIQ + RoomIQ)" across the product-guides site (H1, products index, home table, compare list, mkdocs nav). Docs only; independent of the proof. | **EXECUTED** — this PR |
| K4 | WebFlash | Add "Sense360 Kitchen Bundle — PoE" (config target `Ceiling-POE-AirIQ-RoomIQ`, channel stable, version from served sources.json) as the third kit in `scripts/data/kits.json`; kit-served-consistency drift guard extended to all three kits; LED variant stays hidden. Held PR. | PENDING — runs once K1/K3 are merged (does not require K2) |
| K5 | both | Closure — verify Kitchen served + kitted + gates cleared; mark programme COMPLETE. | PENDING |

## Session protocol

Pull main. If this tracking file is absent: esphome-public → K1 + K3;
WebFlash → K4 only if this file exists on esphome-public main showing K1/K3
done, else STOP and report. Else run the lowest non-EXECUTED step for the
current repo, with K2 gated on the completed proof (detection: every step
A–E marked PASS + non-empty owner-authored section F + owner authorship
verified). If K2 is next but the proof is not yet filled, STOP and report
that the AirIQ bench proof awaits owner completion (normal, not an error).
One session, one step, one held PR, full gate green before opening, then
stop.

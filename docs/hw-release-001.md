# HW-RELEASE-001 — owner declaration: hardware readiness by owner decision

**Decision of record (owner, 2026-07-09):** the bench-proof documentation
requirement is **retired as a release gate**, effective immediately.
Hardware readiness is declared by the owner directly. The owner declares
that **all boards are bench-working**.

This is an owner risk-acceptance decision, not hardware, bench-evidence,
compliance, safety, or commercial-availability *proof*: no capture table
was filled, no attestation was written, and no evidence document was
fabricated. The five operator bench-proof templates are retained as
**RETIRED — informational only** (header-marked in each file):

- [`docs/hardware/PACKAGE-LED-300-001-operator-bench-proof.md`](hardware/PACKAGE-LED-300-001-operator-bench-proof.md)
- [`docs/hardware/PACKAGE-FANDAC-312-001-operator-bench-proof.md`](hardware/PACKAGE-FANDAC-312-001-operator-bench-proof.md)
- [`docs/hardware/PACKAGE-FANPWM-311-001-operator-bench-proof.md`](hardware/PACKAGE-FANPWM-311-001-operator-bench-proof.md)
- [`docs/hardware/PACKAGE-FANRELAY-310-001-operator-bench-proof.md`](hardware/PACKAGE-FANRELAY-310-001-operator-bench-proof.md)
- [`docs/hardware/PACKAGE-AIRIQ-001-operator-bench-proof.md`](hardware/PACKAGE-AIRIQ-001-operator-bench-proof.md)

The standing rule that **attestations are never machine-written** is
untouched: retiring the gate removes the requirement for the documents; it
does not authorise anyone but the owner to author evidence content, ever.

## Promotions executed under this declaration

All promotions are release-eligibility metadata in
[`config/product-catalog.json`](../config/product-catalog.json) and
[`config/webflash-builds.json`](../config/webflash-builds.json); no firmware
binary, GitHub Release, tag, manifest, or WebFlash exposure change is cut by
this PR. Kit / customer visibility is **unchanged** — kits remain a separate
owner decision.

### Preview channel (low-voltage boards)

| Config string | Board(s) covered by the declaration |
|---|---|
| `Ceiling-POE-RoomIQ-LED` | S360-300 LED |
| `Ceiling-POE-FanPWM` | S360-311 PWM |
| `Ceiling-POE-AirIQ-FanPWM-RoomIQ` | S360-311 PWM, S360-210 AirIQ |
| `Ceiling-POE-VentIQ-FanPWM-RoomIQ` | S360-311 PWM |
| `Ceiling-POE-FanDAC` | S360-312 DAC |
| `Ceiling-POE-AirIQ-FanDAC-RoomIQ` | S360-312 DAC, S360-210 AirIQ |
| `Ceiling-POE-VentIQ-FanDAC-RoomIQ` | S360-312 DAC |

### Experimental channel (mains-adjacent lane per COMPLIANCE-001 — never stable)

| Config string | Board(s) covered by the declaration |
|---|---|
| `Ceiling-POE-AirIQ-FanRelay-RoomIQ` | S360-310 Relay (mains-adjacent contact switching), S360-210 AirIQ |
| `Ceiling-POE-VentIQ-FanRelay-RoomIQ` | S360-310 Relay (mains-adjacent contact switching) |

The FanRelay configs take the same experimental-lane posture as FanTRIAC
(mirroring [`docs/decisions/COMPLIANCE-001-RESOLUTION-001.md`](decisions/COMPLIANCE-001-RESOLUTION-001.md)):
never stable, never recommended, never a customer default, never buyable,
never in any kit or kit picker, never in `release_one_required_configs`, and
no electrical-safety / EMC / compliance claim is made.

### Kitchen bundle

`S360-KIT-KITCHEN-P` moves `stable-candidate` → `stable-release` in
[`config/room-bundle-skus.json`](../config/room-bundle-skus.json); its
remaining G8 evidence gates are cleared with the note
**"cleared by owner declaration, HW-RELEASE-001"**. Step K2 of
[`docs/kitchen-bundle-promote-001.md`](kitchen-bundle-promote-001.md) is
marked **SUPERSEDED** by this decision. Kit visibility (WebFlash kit
picker, shop) is unchanged and stays guarded by the kit drift-guard tests.

## Gates that stand

- **FanTRIAC** posture is untouched: experimental-lane only, human-review
  only, never stable / recommended / default / buyable / kit-exposed.
- **FANDAC-I2C-ADDR-001 stays PENDING** — the GP8403 DIP-switch → address
  mapping remains compile-time only; `0x59` stays forbidden when
  VentIQ/AirIQ is present. The FanDAC room bundles ship the `0x5A` override.
- **Release-One remains the customer baseline** (`Ceiling-POE-VentIQ-RoomIQ`
  stable); Simple install resolves to it alone.
- **No false proof:** every artifact promoted here is firmware-build proof
  only, released under this owner declaration.

## Supersessions

- `BENCH-VALIDATION-001` steps T2–T6 (per-board bench-proof promotions) are
  **superseded** by this decision ([`docs/bench-validation-001.md`](bench-validation-001.md)).
- `KITCHEN-BUNDLE-PROMOTE-001` step K2's bench-proof precondition is
  **superseded**; the promotion itself is executed by this PR
  ([`docs/kitchen-bundle-promote-001.md`](kitchen-bundle-promote-001.md)).
- The standing-invariants **fan-token guardrail** ("no fan row in
  `config/webflash-builds.json`") is revised by the owner in
  [`docs/standing-invariants.md`](standing-invariants.md): FanPWM / FanDAC
  rows are now allowed on **preview**, FanRelay rows on **experimental**
  only; fan stable release stays blocked.

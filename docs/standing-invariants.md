# Standing invariants (do not regress)

This file is the **live, authoritative text** for the repository's standing
gates. It carries, verbatim, the *Standing invariants (do not regress)*
section of the retired `UPCOMING_PR.md` working queue (retired under
`DOCS-DISPOSITION-001` Step 7; the full queue file remains recoverable from
the SHA indexed in [`docs/archive-index.md`](archive-index.md) — only the
relative link paths below were adjusted for this file's location under
`docs/`). [`CLAUDE.md`](../CLAUDE.md) summarises these gates and defers to
this file; on any difference, this file wins.

These hold across every PR.

* **Production stable Release-One is the customer baseline.** Config string
  `Ceiling-POE-VentIQ-RoomIQ` (current stable version per
  [`config/webflash-builds.json`](../config/webflash-builds.json); v1.0.4 as of
  2026-06-07), launch shop SKU **`S360-KIT-BATH-P`**. Simple install resolves
  to the stable Bathroom PoE build only. The Bedroom (`Ceiling-POE-RoomIQ`,
  stable v1.0.5, 2026-06-08) and Kitchen (`Ceiling-POE-AirIQ-RoomIQ`, stable
  v1.0.6, 2026-06-09) bundles were later promoted to stable under owner
  risk-acceptance waivers (`HW-S360-410-WAIVER-2026-06`,
  `HW-AIRIQ-WAIVER-2026-06`) — owner waivers, not hardware verification — and
  their candidate / room bundles stay **hidden / not buyable / never the
  customer default**.
* **FanTRIAC is commissioned to the experimental self-build mains lane —
  never stable / recommended / default / buyable / kit-exposed.**
  `TRIAC-COMMISSIONING-001` (human-review only) cleared the `PACKAGE-TRIAC-001`
  half of the former blocker (operator-attested bench proof
  [`docs/package-triac-001-operator-bench-proof.md` (archived)](archive-index.md)),
  with `COMPLIANCE-001` closed by market posture
  ([`docs/decisions/COMPLIANCE-001-RESOLUTION-001.md`](decisions/COMPLIANCE-001-RESOLUTION-001.md)),
  and moved `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` into the `experimental_lane`.
  It is now `status: preview` / `channel: experimental` /
  `webflash_build_matrix: true` with a `config/webflash-builds.json` row on the
  new **experimental** build channel (artifact
  `Sense360-Ceiling-POE-VentIQ-FanTRIAC-RoomIQ-v1.0.0-experimental.bin`). The
  permanent teeth stand: **never stable, never recommended, never a customer
  default, never buyable, never in any kit or kit picker, never in
  `release_one_required_configs`** — the S360-320 is a self-build, open-source
  (CERN-OHL-P) board Sense360 **never places on the market**. This commissioning
  cuts **no release tag** (release-eligibility metadata only) and makes **no
  electrical-safety / EMC / compliance claim**. `TRIAC-PUBLISH-ADVANCED-PREVIEW-001`
  is now **executed** by this commissioning; downstream one-click WebFlash import
  (`WF-IMPORT-TRIAC-001`) stays gated, unblocked only once the experimental
  release is cut. Any further FanTRIAC blocker / status change is **human-review
  only — do NOT auto-merge.**
* **Fans are never stable.** Under owner declaration `HW-RELEASE-001`
  ([`docs/hw-release-001.md`](hw-release-001.md), 2026-07-09) the former
  fan-token guardrail ("no fan row in `config/webflash-builds.json`") was
  revised by the owner: FanPWM / FanDAC configs (and their room-bundle
  compositions) are promoted to the **preview** channel with
  `config/webflash-builds.json` rows, and FanRelay configs are promoted to
  the **experimental** channel only (mains-adjacent lane per
  `COMPLIANCE-001`; same posture as FanTRIAC — never stable / recommended /
  default / buyable / kit-exposed). The teeth that remain: **no fan config
  ever ships on the stable channel** (`RELEASE-RELAY-001` /
  `RELEASE-PWM-001` / `RELEASE-DAC-001` stay the stable blockers), no fan
  config enters `release_one_required_configs`, and promotion is
  release-eligibility metadata under the owner declaration — firmware-build
  proof only, no hardware / bench / compliance claim.
* **The on-board Blower (J13 FAN net) is compile-only and never stable.**
  `BLOWER-FRAMEWORK-001`
  ([`docs/architecture/sense360-blower-framework.md`](architecture/sense360-blower-framework.md))
  drives the Core's dedicated `FAN` net (schematic `IO21` → `Q4` SI2302S →
  `J13`, a two-wire binary 5 V blower output) as a customer ventilation
  actuator, optionally following the canonical AirIQ demand contract. It is a
  fan output, so the *Fans are never stable* gate above applies unchanged: the
  framework ships **compile-only** — no `config/webflash-builds.json` row, no
  artifact, never stable / preview / customer-default / buyable / kit-exposed,
  not in `release_one_required_configs`. J13 exposes **no** tach / speed-PWM /
  current / airflow / rotation feedback, so the framework claims none; `GPIO46`
  (`GP_Fan_Status_Led`) is a Core-side indicator and is **never** treated as
  rotation feedback; the generic `GPIO3` relay (`J4`) stays a separate control
  and is never driven by the blower path. Firmware-build proof only — no
  hardware / bench / airflow / compliance claim.
* **FanDAC I²C address requirement is pending bench.** GP8403 IC1 `0x58` /
  IC2 `0x5A`; `0x59` is forbidden when VentIQ/AirIQ is present (SGP41 collision).
  The DIP-switch mapping is compile-time only — `FANDAC-I2C-ADDR-001` stays
  **PENDING** (no FanDAC hardware verification claimed). See
  [`docs/hardware/fandac-i2c-address-verification.md`](hardware/fandac-i2c-address-verification.md).
* **No false proof.** Preview / compile work is **firmware-build proof only** —
  no hardware / bench / compliance / safety / commercial-availability proof is
  claimed for any preview artifact.

## Standing rules that travel with the gates

- **FanTRIAC changes are human-review only.** Do NOT auto-merge any FanTRIAC
  pin / blocker / status change.
- **Attestations are never machine-written.** Operator attestation /
  bench-evidence blocks are completed by the human operator only; agents may
  scaffold an intentionally empty block but must never fill in attestation
  content, dates, signatures, or evidence claims (source:
  [`docs/package-triac-001-operator-bench-proof.md` (archived)](archive-index.md)).
  `HW-RELEASE-001` retired the bench-proof *documents* as a release gate
  (hardware readiness is declared by the owner directly); it did NOT relax
  this rule — the retired templates stay intentionally empty.
- **The release matrix is declaration-driven (ESP-007).** Releases ship only
  what [`config/webflash-builds.json`](../config/webflash-builds.json) declares;
  never reintroduce a broad `products/` scan in
  [`.github/workflows/firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml).

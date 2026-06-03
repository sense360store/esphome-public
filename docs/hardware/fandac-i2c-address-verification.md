# FANDAC-I2C-ADDR-001 — FanDAC I²C address hardware verification

## Status

**Status: required but NOT bench-verified — PENDING hardware evidence.**

This document is the dedicated bench verification checklist and evidence
template for the **FanDAC (S360-312) GP8403 I²C address switch requirement**
introduced by `ROOM-BUNDLE-FAN-CONFIGS-001` (#713) for the full-composition
room-bundle FanDAC preview configs:

- `Ceiling-POE-VentIQ-FanDAC-RoomIQ`
- `Ceiling-POE-AirIQ-FanDAC-RoomIQ`

It is **documentation / evidence-gate only**. It changes no firmware config,
no compile target, no release metadata, no WebFlash metadata, and publishes
nothing. It claims **no hardware, bench, compliance, safety, stable, or
commercial-availability proof**. Until the bench scan below is run and
recorded, the FanDAC address mapping remains **required but not
bench-verified**, and the two room-bundle FanDAC configs stay advanced /
manual preview, compile-pending — not stable, not recommended, not a customer
default, not buyable.

See also:

- [`docs/hardware/s360-312-r4-fandac.md`](s360-312-r4-fandac.md) — the per-board
  FanDAC hardware reference, including the GP8403 address-selection evidence and
  the derived DIP-switch → I²C-address truth table.
- [`config/room-bundle-fan-variants.json`](../../config/room-bundle-fan-variants.json)
  — `fan_dac_i2c_address_policy` (`FANDAC-ROOM-BUNDLE-ADDRESS-POLICY`), the
  source-of-truth metadata for this requirement.
- [`docs/sense360-room-bundles.md`](../sense360-room-bundles.md) — the
  customer-facing room-bundle catalog and the FanDAC ↔ air-quality address
  requirement narrative.

---

## Why this gate exists

The S360-312 FanDAC board carries **two GP8403 dual-channel 12-bit I²C DACs**
with **hardware-selectable I²C addresses** (per-DAC DIP switches `SW1` / `SW2`
and 4.7 kΩ address-pin pull-ups). The GP8403 part supports the address span
`0x58`–`0x5F` via its `A0` / `A1` / `A2` address pins.

Both Sense360 air-quality modules — **VentIQ (S360-211)** and
**AirIQ (S360-210)** — include an **SGP41** VOC/NOx sensor at I²C **`0x59`** on
the shared `core_i2c` bus.

The FanDAC package default places **IC2 at `0x59`**, which **collides** with
the air-quality SGP41 at `0x59` in any VentIQ/AirIQ + FanDAC bundle. The
conflict is resolved by a **hardware address switch / strap** (plus a matching
firmware override) — **not** by silently ignoring the bus collision.

---

## Required addresses

When a FanDAC board is used **with** an air-quality module (VentIQ or AirIQ):

| Device | Required I²C address | Notes |
|---|---|---|
| GP8403 **IC1** (FanDAC, `SW1`) | **`0x58`** | unchanged from package default |
| GP8403 **IC2** (FanDAC, `SW2`) | **`0x5A`** | relocated off the `0x59` default |
| **SGP41** (VentIQ **and** AirIQ) | **`0x59`** | fixed; owned by the air-quality module |
| GP8403 at `0x59` | **FORBIDDEN** | must not occur with VentIQ/AirIQ present |

**The FanDAC must not leave any GP8403 at `0x59` when used with VentIQ or
AirIQ.**

### Required hardware action

- Set the **FanDAC IC2 address switch / DIP switch / strap (`SW2`)** so IC2
  reports **`0x5A`**, **not** the `0x59` default. Leave IC1 (`SW1`) at `0x58`.
- The matching firmware override `fan_dac_2_i2c_address: "0x5A"` is already set
  in the room-bundle product YAML by `ROOM-BUNDLE-FAN-CONFIGS-001`; the DIP
  switch must be set to **match** it.

### Expected switch positions (derived — NOT bench-verified)

The DIP-position → 7-bit-address mapping derived from the GP8403 datasheet bit
ordering plus the PCB pole→pin mapping is recorded in
[`docs/hardware/s360-312-r4-fandac.md`](s360-312-r4-fandac.md#dip-switch--ic-address-truth-table--row-3-closed).
From that table (pole **closed/ON** = logic 0, pole **open/OFF** = logic 1):

| Target | DIP | Pole 1 (`A0`) | Pole 2 (`A1`) | Pole 3 (`A2`) | Address |
|---|---|---|---|---|---|
| IC1 = `0x58` | `SW1` | ON (0) | ON (0) | ON (0) | `0x58` |
| IC2 = `0x5A` | `SW2` | ON (0) | OFF (1) | ON (0) | `0x5A` |

> **These positions are derived from the datasheet + PCB mapping, not from a
> populated board.** The exact switch positions **must be confirmed and filled
> in from the physical board / silkscreen or board manual** during the bench
> run below. The as-shipped factory DIP positions are **not** evidenced. Until
> measured on hardware, this mapping remains **required but not
> bench-verified**.

---

## Bench verification checklist

Run on a populated `S360-100-R4` Core + `S360-312-R4` FanDAC pair. Tick each
item and record the measured values in the evidence template below.

- [ ] **Visual inspection** of the FanDAC board revision (silkscreen, IC1/IC2,
      `SW1`/`SW2` location and ON-direction arrow).
- [ ] **Record board revision** (e.g. `S360-312-R4`) and the
      **serial / prototype identifier** of the physical unit.
- [ ] **Record IC1 switch setting** (`SW1` pole 1/2/3 ON/OFF) and the silkscreen
      label observed.
- [ ] **Record IC2 switch setting** (`SW2` pole 1/2/3 ON/OFF) and the silkscreen
      label observed.
- [ ] **Scan I²C bus with FanDAC only** (no air-quality module attached).
      - Expected addresses: **`0x58`** and **`0x5A`**.
- [ ] **Scan I²C bus with VentIQ + FanDAC** attached.
      - Expected: **SGP41 at `0x59`**, **FanDAC at `0x58` and `0x5A`**.
- [ ] **Scan I²C bus with AirIQ + FanDAC** attached.
      - Expected: **SGP41 at `0x59`**, **FanDAC at `0x58` and `0x5A`**.
- [ ] **Confirm no duplicate `0x59` device** originates from the FanDAC (only the
      air-quality SGP41 may answer at `0x59`; no bus contention).
- [ ] **Capture logs / screenshots** of each I²C scan (logic-analyser trace or
      ESPHome `i2c` scan output).
- [ ] **Record pass / fail** and the **tester name + date**.

---

## Evidence template

Copy this block per physical unit tested and fill it in at the bench. Leave
fields blank (or `pending`) until measured — do **not** pre-fill measured
results.

```
FANDAC-I2C-ADDR-001 — FanDAC I²C address bench evidence

Board revision:            __________ (e.g. S360-312-R4)
Serial / prototype ID:     __________
Tester:                    __________
Date:                      __________

Switch positions (as read from the physical board / silkscreen):
  IC1 / SW1:  pole1(A0)=__  pole2(A1)=__  pole3(A2)=__   (target 0x58)
  IC2 / SW2:  pole1(A0)=__  pole2(A1)=__  pole3(A2)=__   (target 0x5A)
  Silkscreen / board-manual reference: __________

Connected modules for each scan:
  Scan A:  FanDAC only
  Scan B:  VentIQ + FanDAC
  Scan C:  AirIQ + FanDAC

Firmware / YAML used for scan:
  __________ (config string + commit / version)

Bus scan output (paste / attach per scan):
  Scan A (FanDAC only) — expected 0x58, 0x5A:
    __________
  Scan B (VentIQ + FanDAC) — expected SGP41 0x59, FanDAC 0x58 + 0x5A:
    __________
  Scan C (AirIQ + FanDAC) — expected SGP41 0x59, FanDAC 0x58 + 0x5A:
    __________

No duplicate 0x59 from FanDAC confirmed:  YES / NO
Logs / screenshots attached:              YES / NO  (path/links: ______)

Result:                    PASS / FAIL
Notes:                     __________
Reviewer sign-off:         __________ (name + date)
```

---

## Guardrails

This document and its associated metadata test:

- do **not** change any YAML firmware config;
- do **not** change `config/compile-only-targets.json`,
  `config/preview-release-targets.json`, or `config/webflash-builds.json`;
- do **not** add or change manual firmware artifacts;
- publish no firmware, run no workflows, and create no release / tag;
- do **not** touch the WebFlash repository;
- mark nothing stable, recommended, or default;
- do **not** mark FanDAC hardware verified;
- claim no safety / compliance proof;
- do **not** change TRIAC status (TRIAC stays build-blocked under `HW-005`);
- do **not** change the stable Bathroom PoE bundle.

Until the bench checklist above is completed and an evidence record is filled
in, the FanDAC I²C address requirement remains **required but not
bench-verified**, and `FANDAC-I2C-ADDR-001` stays **PENDING**.

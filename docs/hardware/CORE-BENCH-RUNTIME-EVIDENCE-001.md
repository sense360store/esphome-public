# CORE-BENCH-RUNTIME-EVIDENCE-001 — Sense360 Core physical runtime initialisation evidence

## Scope and evidence classification

**Programme:** `CORE-BENCH-RUNTIME-EVIDENCE-001`

**Evidence class: machine-recorded runtime initialisation evidence.** This is
the first physical-bench runtime evidence record for the **Sense360 Core**
(SKU `S360-100`, rev `R4`) running the canonical repository Core package. It
is an evidence-recording document only:

- It is **not** an operator attestation. No attestation, signature, date
  block, or bench measurement is authored or completed here (standing rule:
  attestations are never machine-written).
- It is **not** hardware verification. It closes **no** open `verify`
  question in [`s360-100-r4-core.md`](s360-100-r4-core.md), changes no
  `schematic_status`, no product lifecycle, no release channel, and no
  commercial state.
- It makes **no release, electrical-safety, EMC, compliance, customer,
  reliability, or commercial claim** of any kind.

The overall Core hardware evidence state after this record remains
**PARTIAL / OPEN**.

## Hardware and firmware identity (as evidenced)

| Field | Value | Basis |
|---|---|---|
| Board under evidence | Sense360 Core bench unit, described by the owner as `S360-100-R4` | owner statement |
| Chip (from runtime log) | ESP32-S3 rev0.2, two cores | runtime log |
| PSRAM (from runtime log) | available, **8192 KB** | runtime log |
| Flash capacity | not independently visible in the supplied evidence — **not recorded** | evidence ceiling |
| Firmware source package | [`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml) (which the board layer wraps via [`packages/boards/s360-100-core.yaml`](../../packages/boards/s360-100-core.yaml)) | owner statement |
| ESPHome version | 2026.7.0 | runtime log |
| Compile timestamp | 2026-07-19 (capture date) | runtime log |
| Project identity | `sense360.ceiling` version `1.0.0` | runtime log |
| Bench device name | `sense360-core-bench` | runtime log |
| Flash / connection method | flashed from Home Assistant ESPHome; connected over the ESPHome encrypted native API via Wi-Fi | owner statement / runtime log |

## Evidence source and sanitisation

The evidence source is an **owner-supplied ESPHome runtime log** captured
from the physical unit. The raw log is **not committed** to this repository
because it contains local network identifiers. This record stores **no
repository-stored credentials and no network-identifying data**: no SSID,
no BSSID, no MAC address, no device IP address, no encryption key, and no
password value is recorded here (the log confirmed only that an OTA password
and API encryption key were *configured*, not their values).

## Observed runtime facts (sanitised)

1. ESPHome resolved the device, connected, and completed the encrypted
   native-API handshake.
2. The canonical project identified itself as `sense360.ceiling` version
   `1.0.0`.
3. The ESP32-S3 booted and remained reachable.
4. PSRAM initialised: available, size **8192 KB**.
5. Shared Core I²C bus initialised: SDA **GPIO48**, SCL **GPIO45**,
   400000 Hz; **bus recovery successful**; no I²C devices found — expected,
   as no expansion modules were attached.
6. Hi-Link UART initialised: TX **GPIO2**, RX **GPIO1**, 256000 baud.
7. SEN0609 UART initialised: TX **GPIO5**, RX **GPIO4**, 115200 baud.
8. Status LED **component** initialised on **GPIO46** (runtime component
   initialisation only — physical LED identity/polarity not observed).
9. Relay **switch component** initialised on **GPIO3** with restore mode
   `RESTORE_DEFAULT_OFF` (configuration acceptance only — no physical
   actuation observed).
10. Wi-Fi connected successfully (network identifiers redacted).
11. OTA service initialised with a password configured.
12. Native API server initialised with Noise encryption enabled.
13. Home Assistant-facing entities were created for status, relay, uptime,
    internal temperature, Wi-Fi information, restart, safe mode, and factory
    reset.

These runtime pin values match the canonical package declarations in
[`packages/hardware/sense360_core_ceiling.yaml`](../../packages/hardware/sense360_core_ceiling.yaml).

## Proven by this evidence

- The canonical Core package compiled and ran on one physical ESP32-S3 Core
  unit.
- ESPHome boot and runtime initialisation succeeded.
- 8 MB (8192 KB) PSRAM was detected and usable.
- The configured I²C controller (GPIO48/GPIO45) and both UART controllers
  (GPIO2/GPIO1 @ 256000; GPIO5/GPIO4 @ 115200) were accepted and
  initialised, with successful I²C bus recovery.
- The GPIO46 status-LED component and the GPIO3 relay switch component were
  accepted and initialised.
- Wi-Fi, the encrypted native API, and OTA services operated.

## Not proven by this evidence

This evidence does **not** prove:

- that GPIO3 physically actuates the relay — **physical relay actuation is
  not proven**;
- relay continuity, load capability, or mains safety;
- that GPIO46 drives the intended physical LED or has correct polarity;
- electrical continuity from ESP GPIOs to expansion connectors —
  **connector continuity is not proven**;
- UART communication with a real RoomIQ radar;
- I²C communication with a real expansion module;
- PoE operation — **PoE is not proven**;
- 240 V PSU operation;
- flash capacity (not independently visible in the evidence);
- schematic correctness;
- connector pin order;
- EMC, electrical safety, or compliance;
- reliability or soak stability;
- customer readiness, release readiness, or commercial availability;
- complete Core hardware verification.

## Remaining physical bench checks (open)

The following remain open and are **not** addressed by this record:

1. Relay click and multimeter continuity across the relay contacts.
2. Relay default-off after a cold power cycle.
3. Physical GPIO46 LED identity and polarity.
4. I²C test with a known expansion module attached.
5. UART test with actual supported radar hardware.
6. Connector voltage and continuity checks.
7. PoE test (separately, with the S360-410 PSU).
8. Soak and reboot monitoring.

## Attached S360-300 LED functional evidence

**Evidence class: machine-recorded runtime facts plus owner-observed
physical behaviour**, captured 2026-07-20 on the same physical Core bench
unit, after the owner extended the Home Assistant ESPHome bench YAML with
the canonical LED board package
[`packages/boards/s360-300-led.yaml`](../../packages/boards/s360-300-led.yaml)
(Sense360 LED, SKU `S360-300`, rev `R4`). The evidence source is a second
owner-supplied ESPHome runtime log; as with the Core log, the raw log is
**not committed** (it contains local network identifiers) and no SSID,
BSSID, MAC address, IP address, key, or password value is recorded here.

### Machine-visible runtime facts (from the ESPHome log)

1. ESPHome 2026.7.0, project `sense360.ceiling` version `1.0.0`, compiled
   2026-07-20; the physical Core remained connected through the encrypted
   ESPHome API throughout.
2. The canonical LED Ring SKU diagnostic entity was created.
3. The ESP32 RMT LED strip driver initialised with data pin **GPIO38**,
   RGB order **GRB**, **12 LEDs**, 192 RMT symbols — matching the
   `s360-300-led.yaml` package declarations (`led_data_pin: GPIO38`,
   `led_count: 12`, `led_rgb_order: GRB`).
4. The Home Assistant light entity **Room Light** was created.
5. Room Light accepted ON and OFF commands; the log records ON at
   brightness 100%, red 100%, green 100%, blue 100%, no effect, and
   contains **two successful logged ON/OFF command cycles**.
6. No reboot, exception, watchdog, RMT, LED, or API error was observed in
   the supplied log during the test.
7. PSRAM remained available at 8192 KB; Wi-Fi, OTA, and the encrypted API
   remained operational.

The 100% brightness command in the log proves only that the command was
accepted and the owner observed operation. **It is not a thermal or
electrical-safety conclusion**, and it does not establish a maximum safe
brightness.

### Owner-observed physical behaviour (owner-supplied observation)

Recorded verbatim as owner-supplied observation, not machine evidence:

- the attached physical LED ring illuminated;
- all LEDs appeared operational;
- Home Assistant on/off control worked;
- brightness control worked;
- owner reports RGB colour control worked;
- the owner reports the LED as "fully working".

No per-channel (red-only / green-only / blue-only) observations were
supplied, and none is claimed.

### LED facts still not proven

This evidence does **not** prove:

- LED supply-rail identity;
- full connector pin-order proof;
- electrical current draw (not measured);
- that 100% brightness is thermally or electrically safe;
- long-duration full-brightness safety;
- instrument-verified RGB channel order (GRB is the configured firmware
  order; the owner observation is visual only);
- colour accuracy (not measured);
- an established maximum safe brightness;
- thermal performance;
- soak reliability;
- EMC, safety, or compliance;
- release readiness or stable-channel eligibility;
- commercial availability;
- complete Core hardware verification.

### LED evidence result

**PASS — canonical S360-300 LED package physical functional operation
observed.**

## Result

- **Evidence result: PASS — Core package physical runtime initialisation.**
- **S360-300 LED package physical functional operation: PASS** (see
  [Attached S360-300 LED functional evidence](#attached-s360-300-led-functional-evidence)).
- **Overall hardware result: PARTIAL / OPEN — physical functions and
  interfaces not yet proven** (overall Core hardware verification remains
  partial / open; supply rail, current, thermal, soak, connector,
  compliance, and all other Core checks stay open).

This record raises the Core evidence level to *runtime initialisation
evidence* only. The `S360-100-BENCH-001` record in
[`s360-100-r4-core.md`](s360-100-r4-core.md) and its open questions remain
pending and unchanged.

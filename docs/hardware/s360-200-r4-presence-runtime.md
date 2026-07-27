# S360-200-R4 Presence runtime

This document records the verified runtime wiring and intended production behaviour of the S360-200-R4 RoomIQ presence system.

## Bench findings (S360-200-R4, firmware 2.14.25112412)

The latest S360-200-R4 bench run confirmed the UART wiring fix and exposed additional runtime defects. These are firmware-build / bench observations on the prototype under test — not production, compliance, safety or accuracy proof.

### LD2450 radar

- **UART communication is confirmed.** ESP TX `GPIO1` → Hi-Link RX, ESP RX `GPIO2` ← Hi-Link TX, `GPIO2` input with internal pull-up, 256000 baud 8N1, 1024-byte RX buffer.
- **Native firmware is detected:** `2.14.25112412`. Live target coordinates, distance, angle, speed and moving/still counts update correctly; Radar Presence and the moving/still binary sensors track.
- **A missing MAC at startup is not, on its own, a radar failure.** Live frame data can be flowing while the MAC is still unknown; do not treat an unknown MAC alone as a fault.
- **Target-count-only freshness was invalid (now fixed).** The bench proved the failure symptom directly: Radar Data Age climbed past the 5 s stale window, Presence Module Status went Degraded and Radar Target Count went NAN/Unknown **while** live coordinates and moving/still counts kept updating. Root cause: freshness was refreshed only from `ld2450_target_count.on_value`, and the native target-count sensor does not necessarily republish while the count is unchanged (a person held at target count 1 while still moving). Freshness is now recorded by the board-local `s360_radar_mark_frame` script from the union of the target-count, moving-target-count and still-target-count component callbacks — at least one of these updates on the frame transitions the bench proves continue. See "Radar frame freshness" below.

### Climate (SHT45 thermal bias)

Bench reference: room ≈ 28.3 °C / ≈ 42 %RH. S360-200-R4 readings:

| Channel | Reading |
| --- | --- |
| Raw SHT45 temperature | ≈ 35.96–36.00 °C |
| Public (calibrated) temperature | stuck at 31.0 °C |
| Raw SHT45 humidity | ≈ 24.8 %RH |
| Public humidity | ≈ 25 %RH |
| BMP581 die temperature | ≈ 34.3 °C |
| ESP32 internal temperature | ≈ 35–36 °C |

The public temperature sitting at exactly 31.0 °C showed the former Temperature Offset had hit its −5 °C lower limit. The raw SHT45 reads ≈ 7.7 °C high and humidity ≈ 17 points low versus the reference — a significant **prototype thermal self-heating bias**, not a normal calibration gap. The BMP581 die temperature is a diagnostic, heat-biased reading and is **not** used as the customer temperature source.

> **Superseded (S360-200-R4-CLIMATE-COMPENSATION-001).** The hand-entered bench corrections recorded here — Temperature Offset −7.7 °C and Humidity Offset +17.0/+17.5 % — are **no longer to be entered**. They were a temporary manual workaround for exactly the board error that firmware now corrects **built in**, so entering them today would double-correct the device. The historical numbers are retained above only as the observation that motivated the built-in profile.

The compensation is now a named, versioned board profile applied inside the RoomIQ engine, with all customer calibration controls neutral at zero:

- built-in temperature compensation: **−5.80 °C**
- built-in humidity residual: **+4.52 %RH**, applied after a vapour-pressure-preserving psychrometric recalculation at the corrected temperature
- customer **Temperature Offset** and **Humidity Offset**: **leave at 0** unless a trusted reference disagrees, and then only by a small amount

The full model, its worked vectors and its evidence level live in [`docs/architecture/sense360-roomiq-framework.md` §3](../architecture/sense360-roomiq-framework.md). Upgrading a device that stored the old manual offsets resets customer Temperature/Humidity calibration to 0/0 exactly once (persisted schema migration; no factory reset needed).

**This is still not proof the production thermal design is acceptable.** A board that needs a correction this large has a thermal-placement characteristic that remains a hardware item; the built-in profile makes the product usable and is validated on **one** tested board only. Compensation and calibration remain applied exactly once, inside the RoomIQ engine — no second correction layer or filter is added to the raw SHT45 sensors, which stay raw for diagnostics.

### MQTT

The test consumer config attempted `mqtt: null`, but MQTT stayed present and repeatedly tried to connect to `192.168.150.4`. ESPHome package removal requires `mqtt: !remove`, not `mqtt: null`. The copy-paste hardware test config below uses `mqtt: !remove`.

## Sensor roles

The board combines three complementary sensors into one customer-facing occupancy result:

- **PIR on GPIO15** provides the fastest movement trigger. It is a non-verifiable GPIO channel and cannot detect a completely still occupant reliably.
- **HLK-LD2450 on the Hi-Link UART** provides moving/still target state, target count and per-target tracking. It is the only presence channel with a real transport-freshness signal.
- **DFRobot SEN0609 on GPIO6** provides independent static-presence retention for seated, sleeping or otherwise very still occupants. The current integration consumes only its digital output; its UART remains reserved.

Any usable sensor may assert occupancy. Occupancy clears only after every currently usable sensor reports clear and the configured clear delay expires. Missing or stale LD2450 data is unknown, never a synthetic clear vote.

## Verified HLK-LD2450 wiring

The schematic net labels are from the Hi-Link radar perspective:

- ESP32-S3 **GPIO1** drives `Hi-Link_RX` and is therefore the ESPHome UART `tx_pin`.
- ESP32-S3 **GPIO2** reads `Hi-Link_TX` and is therefore the ESPHome UART `rx_pin`.

Production UART configuration:

```yaml
uart:
  - id: roomiq_hi_link_uart
    tx_pin: GPIO1
    rx_pin:
      number: GPIO2
      mode:
        input: true
        pullup: true
    baud_rate: 256000
    data_bits: 8
    parity: NONE
    stop_bits: 1
    rx_buffer_size: 1024
```

The internal pull-up on the ESP receive line is required for reliable operation with the tested S360-100-R4/S360-200-R4 assembly. The transmit pin remains an output; it must not be configured as an input.

## Startup and health

Current framework defaults:

- PIR warm-up: 30 seconds
- LD2450 warm-up: 10 seconds; the first real frame ends initialisation early
- SEN0609 warm-up: 15 seconds
- LD2450 stale threshold: 5 seconds
- Fusion evaluation: every 500 ms, plus immediate evaluation on PIR and SEN0609 GPIO edges

Only the LD2450 can prove live communication. PIR and SEN0609 are bare GPIO channels: a low level may mean clear, disconnected or failed. The Presence Module Status therefore describes service availability based primarily on fresh LD2450 frames and must not be interpreted as proof that all three physical sensors are healthy.

### Radar frame freshness

`s360_radar_last_frame_ms` / `s360_radar_frame_seen` are the freshness evidence the fusion engine consumes. They are written **only** by the board-local `s360_radar_mark_frame` script, which runs from the `on_value` hooks of three LD2450 component sensors:

- `target_count`
- `moving_target_count`
- `still_target_count`

`target_count` alone is not a valid per-frame proxy — the bench proved it can stay unchanged while the target keeps moving. Using the union of the three count callbacks is the strongest evidence-backed signal available: ESPHome's `ld2450` platform exposes **no single callback guaranteed to fire on every received frame**, so this is a supported component-callback signal, **not** an exact per-frame guarantee, and it is not claimed as one. The 1 s legacy-compatibility interval re-reads cached sensor states and deliberately never touches the freshness globals, so a disconnected/stopped UART correctly ages out to stale (Radar Target Count → Unknown). A valid zero-target frame still keeps the radar healthy because the count sensors publish the zero transition; a disconnected radar publishes nothing and goes stale.

### Calibration range

The RoomIQ runtime calibration ranges were widened for prototype bench use, back when the whole board error had to be entered by hand:

| Control | Range | Step |
| --- | --- | --- |
| Temperature Offset | −15 … +15 °C | 0.1 |
| Humidity Offset | −30 … +30 %RH | 0.5 |

These ranges are **retained as a compatibility contract, not narrowed** — but they are no longer an expected magnitude. With the built-in S360-200 R4 compensation applied (S360-200-R4-CLIMATE-COMPENSATION-001), normal customer calibration against a trusted reference should be **small**; a large value now indicates an unusual installation or a hardware question. The UI control limits and the `roomiq_engine.h` clamps are kept in agreement (test-guarded). Neutral defaults remain 0 / 0, and are **not** universal SHT45 accuracy claims.

## Customer-facing entities

Enabled by default:

- `Occupancy` — fused result; use this for automations
- `Presence Status` — Initialising, Clear, Movement detected, Still presence, Multiple targets, Sensor degraded or Unavailable
- `Radar Target Count` — instantaneous radar target count; unknown while LD2450 data is stale
- `Presence Mode` — Balanced, Responsive, Stable or Custom
- `Clear Delay` — runtime-adjustable clear delay

Raw PIR, SEN0609 and LD2450 entities remain diagnostic/disabled by default. They should be enabled during commissioning and fault investigation.

## Reliability bench checks

Before release, verify at minimum:

1. Firmware version populates through the native LD2450 component (an unknown MAC alone is not a failure).
2. Radar Data Age remains below the 5-second stale threshold during continuous operation, specifically across the freshness scenarios that previously failed:
   - one stationary target for longer than five seconds;
   - one moving target where the reported target count stays 1;
   - switching between moving and still;
   - zero targets with continuing valid LD2450 frames (stays healthy);
   - disconnected/stopped UART data becoming stale (Radar Target Count → Unknown).
3. PIR gives immediate entry/movement response after warm-up.
4. SEN0609 retains occupancy for a motionless seated occupant.
5. A fresh LD2450 zero-target frame contributes a clear vote; a disconnected UART does not.
6. A new detection cancels a pending clear delay.
7. Radar ghost/reflection targets clear correctly in the intended enclosure and mounting position.
8. Disconnecting each sensor while occupied does not cause an immediate false clear.
9. Restore power with a person already sitting still and verify occupancy after sensor warm-up.
10. Exercise Responsive, Balanced and Stable modes and verify their documented holds and clear delays.

### Climate calibration bench

11. With Temperature Offset and Humidity Offset left at **0**, confirm the public Temperature and Humidity track the reference within the profile's expected error (the built-in −5.80 °C / +4.52 %RH compensation is applied by the firmware). Confirm the correction is applied exactly once and that the Raw Temperature / Raw Humidity diagnostics stay **uncompensated**. Record the reference-versus-public deviation for each unit tested — this is the multi-unit evidence the profile still lacks.
12. Confirm the BMP581 die temperature is not used as the customer temperature, and that the Factory Compensated Temperature / Factory Compensated Humidity diagnostics equal the public values while customer calibration is 0/0.
13. On a device upgraded from firmware that stored the old manual offsets, confirm Temperature Offset and Humidity Offset are reset to 0/0 once on the first boot after the upgrade (the RoomIQ Calibration Schema diagnostic and the boot log record it), that no factory reset was needed, and that a value entered afterwards persists across a restart.

The temperature bias itself remains a **hardware** item: the SHT45 thermal self-heating / placement problem is unresolved and software calibration is not a substitute for a production thermal-design fix.

### Copy-paste hardware test configuration

S360-100 Core host from `main` + the S360-200 RoomIQ + Presence package from the fix branch. No AirIQ, no MICS, no LED, no blower, no local UART override. API enabled; MQTT removed with `mqtt: !remove` (`mqtt: null` leaves MQTT active — the bench saw it retry `192.168.150.4`). LD2450 / UART / I2C debug logging is enabled to watch frames.

Replace `<FIX_BRANCH>` with the branch carrying this change (or a release tag once merged) and keep `sense360_remote_ref` matched to it so the shared engine headers are fetched from the same ref.

```yaml
substitutions:
  device_name: sense360-roomiq-bench
  friendly_name: "Sense360 RoomIQ Bench"
  timezone: "Europe/London"
  device_version: "s360-200-bench"

  # Core Framework identity (compile-time facts).
  s360_config_string: "Ceiling-Core-RoomIQ-Presence"
  s360_hardware_model: "S360-100"
  s360_hardware_revision: "R4"
  s360_capabilities: "core,roomiq,presence"
  s360_capabilities_human: "Core, RoomIQ, Presence"

  # Fetch the shared engine headers from the same ref as the packages below.
  sense360_remote_ref: <FIX_BRANCH>

packages:
  core:
    url: https://github.com/sense360store/esphome-public
    ref: main
    files: [packages/hardware/sense360_core_ceiling.yaml]
    refresh: 1d
  core_framework:
    url: https://github.com/sense360store/esphome-public
    ref: main
    files: [packages/base/device_framework.yaml]
    refresh: 1d
  roomiq_presence:
    url: https://github.com/sense360store/esphome-public
    ref: <FIX_BRANCH>
    files: [packages/remote/ceiling-roomiq-presence.yaml]
    refresh: 1d

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_encryption_key

ota:
  - platform: esphome
    password: !secret ota_password

# Watch LD2450 frames, UART traffic and the I2C bus during the bench run.
logger:
  level: DEBUG
  logs:
    ld2450: DEBUG
    uart: DEBUG
    i2c: DEBUG

# ESPHome package removal requires !remove; `mqtt: null` does NOT remove a
# package-composed MQTT client (the bench proved it kept connecting).
mqtt: !remove
```

After flashing, leave the RoomIQ calibration controls at their neutral defaults: **Temperature Offset 0 °C** and **Humidity Offset 0 %**. The board correction is built into the firmware (S360-200-R4-CLIMATE-COMPENSATION-001); the earlier instruction to enter −7.7 °C / +17 % is superseded and would double-correct. Only add a small offset if a trusted reference disagrees with the compensated reading, and record what you entered and why.

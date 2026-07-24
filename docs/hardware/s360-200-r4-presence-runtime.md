# S360-200-R4 Presence runtime

This document records the verified runtime wiring and intended production behaviour of the S360-200-R4 RoomIQ presence system.

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

1. Firmware version and MAC populate through the native LD2450 component.
2. Radar Data Age remains below the 5-second stale threshold during continuous operation.
3. PIR gives immediate entry/movement response after warm-up.
4. SEN0609 retains occupancy for a motionless seated occupant.
5. A fresh LD2450 zero-target frame contributes a clear vote; a disconnected UART does not.
6. A new detection cancels a pending clear delay.
7. Radar ghost/reflection targets clear correctly in the intended enclosure and mounting position.
8. Disconnecting each sensor while occupied does not cause an immediate false clear.
9. Restore power with a person already sitting still and verify occupancy after sensor warm-up.
10. Exercise Responsive, Balanced and Stable modes and verify their documented holds and clear delays.

# Customer entity surface (SENSE360-REVIEW-RELEASE-001)

Programme: `SENSE360-REVIEW-RELEASE-001` (SOT charter
`programmes/sense360-review-release-001.yaml`), Gate B — firmware customer
experience. Issue: [#874](https://github.com/sense360store/esphome-public/issues/874).

This record defines **which entities a customer sees by default** in Home
Assistant, and the rules that keep engineering information and
evidence-uncertain capability out of that surface. It is a presentation
contract only: it deletes no capability, changes no measurement, no
threshold, no automation, no entity id and no state.

## The three layers

Home Assistant renders an ESPHome device in three places. The distinction
this record depends on is the *effective* entity category:

| Layer | Rule | Where it appears |
|---|---|---|
| **Customer default** | enabled by default **and** no effective `entity_category` | the device's main controls/sensors panel |
| **Advanced** | effective `entity_category` of `diagnostic` or `config` | the device's Diagnostic / Configuration panels |
| **Opt-in** | `disabled_by_default: true` | hidden until the user enables the entity |

**Effective** category means the `entity_category` declared in YAML *or*
the default the ESPHome platform applies when YAML declares none. Ten of
this repository's device-health entities never declared a category because
their ESPHome platform already supplies one — `status`, `wifi_signal`,
`wifi_info`, `version`, `uptime`, `internal_temperature` are
`diagnostic`, and `restart`, `safe_mode`, `factory_reset` are `config`.
They were already correct in Home Assistant; only the generated
documentation misread them, because it read YAML alone.
`scripts/generate_product_entity_tables.py` now carries those platform
defaults in `PLATFORM_DEFAULT_ENTITY_CATEGORY`, exactly as it already
carried `PLATFORM_DEFAULT_UNITS`, so the derived tables describe what
Home Assistant actually shows.

## The customer-default surface

For the review composition `Ceiling-POE-AirIQ-RoomIQ` (Core + RoomIQ +
AirIQ), the customer-default surface is these entities and nothing else:

| Group | Entities |
|---|---|
| Presence | Occupancy |
| Room climate | Temperature, Humidity, Pressure |
| Light | Illuminance, Brightness |
| Derived room state | Comfort, Environment State |
| Air quality | CO2, VOC, NOx, Air Quality, Recommendation |

That is the whole product proposition — occupancy, comfort, light and air
quality — with no engineering information competing for attention.

## Rules

1. **Device health is never customer-default.** Network identity and
   signal, uptime, firmware version, chip temperature, supply voltage,
   power source and connection status are `diagnostic`. They stay
   available; they do not lead.
2. **Device management is `config`.** Restart, safe mode and factory
   reset are controls, not readings.
3. **Evidence-uncertain capability is never customer-default.** An entity
   whose hardware fitment or attachment is an unresolved owner decision
   is `diagnostic` **and** `disabled_by_default`, so it is discoverable
   and enable-able without being presented as a shipped capability.
   Recategorising such an entity asserts nothing about the hardware in
   either direction, and resolves no owner decision.
4. **Controls for hardware that is not part of the composition are not
   customer-default.** A drive line to a connector no module in the
   composition populates is advanced functionality.
5. **Nothing is deleted to shorten the list.** Every entity above the
   line before this record still exists; the change is which panel it
   appears in.

## Entities this record moved, and why

| Entity | Now | Reason |
|---|---|---|
| Supply Voltage, Power Source, PoE Power Connected | `diagnostic` | Device health. Declared on `template` platforms, so no ESPHome default applied and they rendered as customer-default. Rule 1. |
| Relay | `config` + `disabled_by_default` | The Core `main_relay` is the GPIO drive line for connector `J4`, documented in `docs/hardware/s360-100-core-connector-pin-map.md` as the Sense360 Relay (`S360-310`) module connector. No `S360-310` is in the review composition, no package in it drives `main_relay`, and its only consumer, `packages/expansions/fan_relay.yaml`, exposes its own customer-facing `Fan` switch that proxies it. Rule 4. |
| Formaldehyde | `diagnostic` + `disabled_by_default` | SFA40 (`U2`) production population is an open bench item (`docs/hardware/airiq-framework-bench-checklist.md`), tracked as SOT `OD-SOT-008`. Rule 3. |
| Radar Target Count | `diagnostic` + `disabled_by_default` | Whether the connector-attached radar modules ship is SOT `OD-SOT-004`. Every other radar-derived entity in this framework was already `diagnostic` + `disabled_by_default`; this one was the sole exception. Rule 3. |
| Presence Status | `diagnostic` + `disabled_by_default` | Also `OD-SOT-004`, for a subtler reason recorded below. Rule 3. |

### Why `Presence Status` is gated but `Occupancy` is not

The canonical package expects all three presence channels
(`presence_pir_expected`, `presence_radar_expected`,
`presence_sen0609_expected` are all `"true"`), because whether the radar
modules are supplied is unresolved. On a unit whose radar connector is
unpopulated, the radar channel is both *expected* and *verifiable*, so
once its warm-up expires it counts as a **failed** channel. PIR keeps the
module usable, so health settles at `Degraded` — permanently. The PD-02
precedence places `HEALTH_DEGRADED` above `STATUS_CLEAR`, so with the room
genuinely empty the customer-facing status reads **"Sensor degraded"**,
never "Clear".

That is proven against the shared engine, not inferred from YAML:
`tests/unit/test_presence_fusion.cpp` drives `FusionEngine` with no radar
frames and asserts the outcome
(`missing_radar_reports_degraded_not_clear_when_room_empties`). The same
suite records that an absent SEN0609 alone does **not** degrade health —
it is a non-verifiable GPIO channel and can never be proven failed — so
radar is the channel responsible.

`Occupancy` stays customer-default because it stays correct: the fusion
asserts occupancy from **any** valid sensor, so a PIR-only unit tracks the
room properly through assert and clear
(`occupancy_remains_trustworthy_across_the_degraded_cycle`). Occupancy is
the presence signal a customer sees; the status string is the one that
misleads while `OD-SOT-004` is open.

The fix is presentation only. Expected-sensor membership is deliberately
**not** changed: setting `presence_radar_expected` to `"false"` would make
the status read correctly, but it would assert that radar is absent, and
setting it `"true"` asserts the opposite. Either would resolve
`OD-SOT-004` by inference, which is forbidden. The fusion, precedence and
health logic are untouched, and enabling the entity restores it in full.

## What this record does not decide

It does not resolve `OD-SOT-004` (radar attachment inclusion) or
`OD-SOT-008` (SFA40 fitment); both stay open in SOT `decisions.yaml`, and
nothing here claims a sensor is present or absent. It makes no hardware,
bench, compliance or commercial claim, changes no release channel,
version, artifact or product status, and creates no Zone Studio
dependency.

## Guard

`tests/test_customer_entity_surface.py` pins this contract: the
customer-default surface of each served configuration, the exclusion of
device-health and management entities, the exclusion of
evidence-uncertain capability across every served configuration, and the
fact that no entity was deleted.

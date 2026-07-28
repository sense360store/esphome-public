"""sense360_presence — the Presence domain component (SENSE360-CANONICALISATION-001 PR 10).

Wraps the canonical tri-sensor fusion engine singleton
(``sense360::presence::global_engine()`` from
``components/sense360/presence_fusion.h``) as a real ESPHome component,
per the plan of record
``docs/architecture/sense360-presence-component-plan.md``. It owns what
used to be YAML glue in ``packages/features/presence_framework.yaml``:
input feeding (PIR / SEN0609 edges, radar frames from the bound radar
sensors' real update callbacks), the runtime mode/clear-delay control
interplay (preset application and the switch-to-Custom rule), the 500 ms
evaluation tick and the publish-on-change switchboard.

The fusion model itself (fail-safe rules, status precedence, module
health PD-07) stays in the natively tested engine header — this component
is glue only, with no model logic and no raw hardware I/O. The
PCB-mounted-PIR versus connector-attached-radar evidence distinction
(OD-SOT-004, open) is unchanged: GPIO-level channels stay non-verifiable
and the health vocabulary is untouched.

Defaults below equal the pre-component substitution defaults verbatim.
"""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import binary_sensor, number, select, sensor, text_sensor
from esphome.const import CONF_ID

CODEOWNERS = ["@sense360store"]
AUTO_LOAD = ["sense360", "binary_sensor", "sensor", "text_sensor", "number", "select"]

sense360_presence_ns = cg.esphome_ns.namespace("sense360_presence")
Sense360Presence = sense360_presence_ns.class_("Sense360Presence", cg.Component)

CONF_PIR_SENSOR = "pir_sensor"
CONF_STATIC_SENSOR = "static_sensor"
CONF_RADAR_TARGET_COUNT = "radar_target_count_sensor"
CONF_RADAR_MOVING_COUNT = "radar_moving_count_sensor"
CONF_RADAR_STILL_COUNT = "radar_still_count_sensor"
CONF_MODE_SELECT = "mode_select"
CONF_CLEAR_DELAY_NUMBER = "clear_delay_number"
CONF_MODULE_STATUS_ID = "module_status_id"
CONF_PIR_EXPECTED = "pir_expected"
CONF_RADAR_EXPECTED = "radar_expected"
CONF_STATIC_EXPECTED = "static_expected"
CONF_PIR_WARMUP = "pir_warmup"
CONF_RADAR_WARMUP = "radar_warmup"
CONF_STATIC_WARMUP = "static_warmup"
CONF_RADAR_STALE = "radar_stale"

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(Sense360Presence),
        # Adapter-owned inputs, bound by id (the adapters and their layering
        # contract are untouched; their script.execute hook re-evaluates
        # through the same-id bridge script kept in the framework YAML).
        cv.Optional(CONF_PIR_SENSOR): cv.use_id(binary_sensor.BinarySensor),
        cv.Optional(CONF_STATIC_SENSOR): cv.use_id(binary_sensor.BinarySensor),
        cv.Optional(CONF_RADAR_TARGET_COUNT): cv.use_id(sensor.Sensor),
        cv.Optional(CONF_RADAR_MOVING_COUNT): cv.use_id(sensor.Sensor),
        cv.Optional(CONF_RADAR_STILL_COUNT): cv.use_id(sensor.Sensor),
        # Runtime customer controls stay persisted template entities in YAML
        # (entity ids and restore identity are protected contracts).
        cv.Optional(CONF_MODE_SELECT): cv.use_id(select.Select),
        cv.Optional(CONF_CLEAR_DELAY_NUMBER): cv.use_id(number.Number),
        # Owned by the Core Framework (CORE-FRAMEWORK-001); fed, never
        # re-declared.
        cv.Optional(CONF_MODULE_STATUS_ID): cv.use_id(text_sensor.TextSensor),
        # Expected-sensor membership (PD-08) — configuration-driven; an
        # intentionally absent sensor is never a fault.
        cv.Optional(CONF_PIR_EXPECTED, default=True): cv.boolean,
        cv.Optional(CONF_RADAR_EXPECTED, default=True): cv.boolean,
        cv.Optional(CONF_STATIC_EXPECTED, default=True): cv.boolean,
        # Sensor-specific startup windows — engineering defaults pending
        # bench validation, identical to the pre-component substitutions.
        cv.Optional(
            CONF_PIR_WARMUP, default="30s"
        ): cv.positive_time_period_milliseconds,
        cv.Optional(
            CONF_RADAR_WARMUP, default="10s"
        ): cv.positive_time_period_milliseconds,
        cv.Optional(
            CONF_STATIC_WARMUP, default="15s"
        ): cv.positive_time_period_milliseconds,
        cv.Optional(
            CONF_RADAR_STALE, default="5s"
        ): cv.positive_time_period_milliseconds,
    }
).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    for key, setter in (
        (CONF_PIR_SENSOR, var.set_pir_sensor),
        (CONF_STATIC_SENSOR, var.set_static_sensor),
        (CONF_RADAR_TARGET_COUNT, var.set_radar_target_count_sensor),
        (CONF_RADAR_MOVING_COUNT, var.set_radar_moving_count_sensor),
        (CONF_RADAR_STILL_COUNT, var.set_radar_still_count_sensor),
        (CONF_MODE_SELECT, var.set_mode_select),
        (CONF_CLEAR_DELAY_NUMBER, var.set_clear_delay_number),
        (CONF_MODULE_STATUS_ID, var.set_module_status_text_sensor),
    ):
        if key in config:
            bound = await cg.get_variable(config[key])
            cg.add(setter(bound))

    cg.add(
        var.set_channel_expectations(
            config[CONF_PIR_EXPECTED],
            config[CONF_RADAR_EXPECTED],
            config[CONF_STATIC_EXPECTED],
        )
    )
    cg.add(
        var.set_warmups(
            config[CONF_PIR_WARMUP],
            config[CONF_RADAR_WARMUP],
            config[CONF_STATIC_WARMUP],
            config[CONF_RADAR_STALE],
        )
    )

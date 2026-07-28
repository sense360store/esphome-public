"""sense360_ventiq — the VentIQ domain component (SENSE360-CANONICALISATION-001 PR 11).

Wraps the canonical VentIQ ventilation engine singleton
(``sense360::ventiq::global_engine()`` from
``components/sense360/ventiq_engine.h``, which embeds the canonical AirIQ
engine for pollutant truth — one implementation, no duplicated thresholds)
as a real ESPHome component, per
``docs/architecture/sense360-airiq-ventiq-component-plan.md``. It owns what
used to be YAML glue in ``packages/features/ventiq_framework.yaml``: input
feeding (RoomIQ canonical humidity/temperature by entity id, the board's
SGP41 VOC/NOx), the expected-channel / freshness / heuristic configuration,
the genuinely wired customer controls (thresholds, durations, the shower
detection switch), the 10 s tick and the publish switchboard.

The manual-action buttons (force ventilation / reset shower / reset mould)
stay as YAML engine-action lambdas on their preserved legacy entities and
re-evaluate through the framework's same-id bridge script. S360-211 stays
its own board and component — nothing merges it with AirIQ. Every default
equals the pre-component substitution defaults verbatim; heuristics stay
provisional engineering values.
"""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import number, sensor, switch, text_sensor
from esphome.const import CONF_ID

CODEOWNERS = ["@sense360store"]
AUTO_LOAD = ["sense360", "sensor", "text_sensor", "binary_sensor", "number", "switch"]

sense360_ventiq_ns = cg.esphome_ns.namespace("sense360_ventiq")
Sense360VentIQ = sense360_ventiq_ns.class_("Sense360VentIQ", cg.Component)

CONF_HUMIDITY_SOURCE = "humidity_source"
CONF_TEMPERATURE_SOURCE = "temperature_source"
CONF_VOC_SOURCE = "voc_source"
CONF_NOX_SOURCE = "nox_source"
CONF_SHOWER_THRESHOLD_NUMBER = "shower_threshold_number"
CONF_CLEARING_NUMBER = "clearing_number"
CONF_MOULD_THRESHOLD_NUMBER = "mould_threshold_number"
CONF_SHOWER_DETECTION_SWITCH = "shower_detection_switch"
CONF_MODULE_STATUS_ID = "module_status_id"
CONF_EXPECTED_VOC = "expected_voc"
CONF_EXPECTED_NOX = "expected_nox"

_WINDOWS = (
    "humidity_warmup", "humidity_stale",
    "temperature_warmup", "temperature_stale",
    "voc_warmup", "voc_stale",
    "nox_warmup", "nox_stale",
)
_HEURISTICS = (
    "shower_rate_threshold", "shower_end_delta", "shower_max_minutes",
    "mould_duration_minutes", "humidity_high_threshold", "humidity_hysteresis",
)

_schema = {
    cv.GenerateID(): cv.declare_id(Sense360VentIQ),
    cv.Optional(CONF_HUMIDITY_SOURCE): cv.use_id(sensor.Sensor),
    cv.Optional(CONF_TEMPERATURE_SOURCE): cv.use_id(sensor.Sensor),
    cv.Optional(CONF_VOC_SOURCE): cv.use_id(sensor.Sensor),
    cv.Optional(CONF_NOX_SOURCE): cv.use_id(sensor.Sensor),
    # Genuinely wired customer controls stay persisted template entities in
    # YAML (entity ids and restore identity are protected contracts).
    cv.Optional(CONF_SHOWER_THRESHOLD_NUMBER): cv.use_id(number.Number),
    cv.Optional(CONF_CLEARING_NUMBER): cv.use_id(number.Number),
    cv.Optional(CONF_MOULD_THRESHOLD_NUMBER): cv.use_id(number.Number),
    cv.Optional(CONF_SHOWER_DETECTION_SWITCH): cv.use_id(switch.Switch),
    cv.Optional(CONF_MODULE_STATUS_ID): cv.use_id(text_sensor.TextSensor),
    cv.Optional(CONF_EXPECTED_VOC, default=True): cv.boolean,
    cv.Optional(CONF_EXPECTED_NOX, default=True): cv.boolean,
}
for _key in _WINDOWS:
    _schema[cv.Required(_key)] = cv.positive_time_period_milliseconds
for _key in _HEURISTICS:
    _schema[cv.Required(_key)] = cv.float_

CONFIG_SCHEMA = cv.Schema(_schema).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    for key, setter in (
        (CONF_HUMIDITY_SOURCE, var.set_humidity_source),
        (CONF_TEMPERATURE_SOURCE, var.set_temperature_source),
        (CONF_VOC_SOURCE, var.set_voc_source),
        (CONF_NOX_SOURCE, var.set_nox_source),
        (CONF_SHOWER_THRESHOLD_NUMBER, var.set_shower_threshold_number),
        (CONF_CLEARING_NUMBER, var.set_clearing_number),
        (CONF_MOULD_THRESHOLD_NUMBER, var.set_mould_threshold_number),
        (CONF_SHOWER_DETECTION_SWITCH, var.set_shower_detection_switch),
        (CONF_MODULE_STATUS_ID, var.set_module_status_text_sensor),
    ):
        if key in config:
            bound = await cg.get_variable(config[key])
            cg.add(setter(bound))

    cg.add(var.set_expected(config[CONF_EXPECTED_VOC], config[CONF_EXPECTED_NOX]))
    cg.add(
        var.set_windows(
            config["humidity_warmup"], config["humidity_stale"],
            config["temperature_warmup"], config["temperature_stale"],
            config["voc_warmup"], config["voc_stale"],
            config["nox_warmup"], config["nox_stale"],
        )
    )
    cg.add(
        var.set_heuristics(
            config["shower_rate_threshold"], config["shower_end_delta"],
            config["shower_max_minutes"], config["mould_duration_minutes"],
            config["humidity_high_threshold"], config["humidity_hysteresis"],
        )
    )

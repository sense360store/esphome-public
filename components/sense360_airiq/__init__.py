"""sense360_airiq — the AirIQ domain component (SENSE360-CANONICALISATION-001 PR 11).

Wraps the canonical AirIQ engine singleton
(``sense360::airiq::global_engine()`` from
``components/sense360/airiq_engine.h`` — the SAME instance the blower
framework reads for its ventilation demand and the VentIQ engine embeds for
pollutant truth) as a real ESPHome component, per
``docs/architecture/sense360-airiq-ventiq-component-plan.md``. It owns what
used to be YAML glue in ``packages/features/airiq_framework.yaml``: input
feeding from the fitted base sensors (CO2 / VOC / NOx / HCHO), the
expected-sensor and freshness/threshold configuration, the 10 s tick and
the publish switchboard (fresh engine values on input, NAN on stale —
a stale reading is never left standing as if it were live).

The PM path stays externally fed: the opt-in SPS30 overlay
(``packages/boards/s360-210-airiq-sps30.yaml``) feeds the engine's PM
channels directly and re-evaluates through the framework's same-id bridge
script; this component owns the PM entities' NAN-on-stale half only.

The pollutant model (severity, hysteresis, headline, recommendation,
module health) stays in the natively tested engine header — glue only, no
model logic, no raw hardware I/O. Every default equals the pre-component
substitution defaults verbatim; thresholds stay provisional engineering
values.
"""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor, text_sensor
from esphome.const import CONF_ID

CODEOWNERS = ["@sense360store"]
AUTO_LOAD = ["sense360", "sensor", "text_sensor"]

sense360_airiq_ns = cg.esphome_ns.namespace("sense360_airiq")
Sense360AirIQ = sense360_airiq_ns.class_("Sense360AirIQ", cg.Component)

CONF_CO2_SOURCE = "co2_source"
CONF_VOC_SOURCE = "voc_source"
CONF_NOX_SOURCE = "nox_source"
CONF_HCHO_SOURCE = "hcho_source"
CONF_MODULE_STATUS_ID = "module_status_id"
CONF_LEGACY_AIR_QUALITY_ID = "legacy_air_quality_id"

# (expected, warmup, stale) per configurable pollutant channel; HCHO and O3
# carry expectation flags only (no dedicated windows in the glue today).
CONF_EXPECTED_CO2 = "expected_co2"
CONF_EXPECTED_VOC = "expected_voc"
CONF_EXPECTED_NOX = "expected_nox"
CONF_EXPECTED_PM = "expected_pm"
CONF_EXPECTED_HCHO = "expected_hcho"
CONF_EXPECTED_O3 = "expected_o3"

_WINDOW_KEYS = []
for _p in ("co2", "voc", "nox", "pm"):
    _WINDOW_KEYS.append((f"{_p}_warmup", f"{_p}_stale"))

_THRESHOLD_KEYS = {}
for _p in ("co2", "voc", "nox", "pm25"):
    _THRESHOLD_KEYS[_p] = (f"{_p}_fair", f"{_p}_poor", f"{_p}_very_poor", f"{_p}_hysteresis")

_schema = {
    cv.GenerateID(): cv.declare_id(Sense360AirIQ),
    cv.Optional(CONF_CO2_SOURCE): cv.use_id(sensor.Sensor),
    cv.Optional(CONF_VOC_SOURCE): cv.use_id(sensor.Sensor),
    cv.Optional(CONF_NOX_SOURCE): cv.use_id(sensor.Sensor),
    cv.Optional(CONF_HCHO_SOURCE): cv.use_id(sensor.Sensor),
    cv.Optional(CONF_MODULE_STATUS_ID): cv.use_id(text_sensor.TextSensor),
    cv.Optional(CONF_LEGACY_AIR_QUALITY_ID): cv.use_id(text_sensor.TextSensor),
    cv.Optional(CONF_EXPECTED_CO2, default=True): cv.boolean,
    cv.Optional(CONF_EXPECTED_VOC, default=True): cv.boolean,
    cv.Optional(CONF_EXPECTED_NOX, default=True): cv.boolean,
    cv.Optional(CONF_EXPECTED_PM, default=False): cv.boolean,
    cv.Optional(CONF_EXPECTED_HCHO, default=True): cv.boolean,
    cv.Optional(CONF_EXPECTED_O3, default=False): cv.boolean,
}
for _warmup, _stale in _WINDOW_KEYS:
    _schema[cv.Required(_warmup)] = cv.positive_time_period_milliseconds
    _schema[cv.Required(_stale)] = cv.positive_time_period_milliseconds
for _fair, _poor, _very_poor, _hyst in _THRESHOLD_KEYS.values():
    _schema[cv.Required(_fair)] = cv.float_
    _schema[cv.Required(_poor)] = cv.float_
    _schema[cv.Required(_very_poor)] = cv.float_
    _schema[cv.Required(_hyst)] = cv.float_

CONFIG_SCHEMA = cv.Schema(_schema).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    for key, setter in (
        (CONF_CO2_SOURCE, var.set_co2_source),
        (CONF_VOC_SOURCE, var.set_voc_source),
        (CONF_NOX_SOURCE, var.set_nox_source),
        (CONF_HCHO_SOURCE, var.set_hcho_source),
        (CONF_MODULE_STATUS_ID, var.set_module_status_text_sensor),
        (CONF_LEGACY_AIR_QUALITY_ID, var.set_legacy_air_quality_text_sensor),
    ):
        if key in config:
            bound = await cg.get_variable(config[key])
            cg.add(setter(bound))

    cg.add(
        var.set_expected(
            config[CONF_EXPECTED_CO2],
            config[CONF_EXPECTED_VOC],
            config[CONF_EXPECTED_NOX],
            config[CONF_EXPECTED_PM],
            config[CONF_EXPECTED_HCHO],
            config[CONF_EXPECTED_O3],
        )
    )
    cg.add(
        var.set_windows(
            config["co2_warmup"], config["co2_stale"],
            config["voc_warmup"], config["voc_stale"],
            config["nox_warmup"], config["nox_stale"],
            config["pm_warmup"], config["pm_stale"],
        )
    )
    cg.add(
        var.set_co2_thresholds(
            config["co2_fair"], config["co2_poor"],
            config["co2_very_poor"], config["co2_hysteresis"],
        )
    )
    cg.add(
        var.set_voc_thresholds(
            config["voc_fair"], config["voc_poor"],
            config["voc_very_poor"], config["voc_hysteresis"],
        )
    )
    cg.add(
        var.set_nox_thresholds(
            config["nox_fair"], config["nox_poor"],
            config["nox_very_poor"], config["nox_hysteresis"],
        )
    )
    cg.add(
        var.set_pm25_thresholds(
            config["pm25_fair"], config["pm25_poor"],
            config["pm25_very_poor"], config["pm25_hysteresis"],
        )
    )

"""sense360_ventiq binary_sensor platform (SENSE360-CANONICALISATION-001 PR 11).

Component-owned ventilation / shower / mould-risk outputs.
"""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import binary_sensor
from esphome.const import (
    CONF_TYPE,
    DEVICE_CLASS_MOISTURE,
    DEVICE_CLASS_PROBLEM,
)

from . import Sense360VentIQ

CONF_SENSE360_VENTIQ_ID = "sense360_ventiq_id"

TYPES = {
    "ventilation_needed": {
        "schema": binary_sensor.binary_sensor_schema(
            device_class=DEVICE_CLASS_PROBLEM,
            icon="mdi:fan-alert",
        ),
        "setter": "set_ventilation_needed_binary_sensor",
    },
    "shower": {
        "schema": binary_sensor.binary_sensor_schema(
            device_class=DEVICE_CLASS_MOISTURE,
            icon="mdi:shower-head",
        ),
        "setter": "set_shower_binary_sensor",
    },
    "mould_risk": {
        "schema": binary_sensor.binary_sensor_schema(
            device_class=DEVICE_CLASS_PROBLEM,
            icon="mdi:mushroom",
        ),
        "setter": "set_mould_risk_binary_sensor",
    },
}


def _base_schema(type_key):
    # NOTE: cv.typed_schema POPS the `type` key before validating against
    # the selected inner schema (and re-adds it afterwards), so the inner
    # schema must NOT declare `type` itself.
    return TYPES[type_key]["schema"].extend(
        {
            cv.GenerateID(CONF_SENSE360_VENTIQ_ID): cv.use_id(Sense360VentIQ),
        }
    )


CONFIG_SCHEMA = cv.typed_schema(
    {key: _base_schema(key) for key in TYPES},
    lower=True,
)


async def to_code(config):
    hub = await cg.get_variable(config[CONF_SENSE360_VENTIQ_ID])
    var = await binary_sensor.new_binary_sensor(config)
    cg.add(getattr(hub, TYPES[config[CONF_TYPE]]["setter"])(var))

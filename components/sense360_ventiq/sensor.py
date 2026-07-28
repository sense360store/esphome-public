"""sense360_ventiq sensor platform (SENSE360-CANONICALISATION-001 PR 11).

Component-owned SGP41 relative indices — deliberately unitless, never
presented as concentrations.
"""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor
from esphome.const import CONF_TYPE, STATE_CLASS_MEASUREMENT

from . import Sense360VentIQ

CONF_SENSE360_VENTIQ_ID = "sense360_ventiq_id"

TYPES = {
    "voc": {
        "schema": sensor.sensor_schema(
            state_class=STATE_CLASS_MEASUREMENT,
            accuracy_decimals=0,
            icon="mdi:air-filter",
        ),
        "setter": "set_voc_sensor",
    },
    "nox": {
        "schema": sensor.sensor_schema(
            state_class=STATE_CLASS_MEASUREMENT,
            accuracy_decimals=0,
            icon="mdi:smog",
        ),
        "setter": "set_nox_sensor",
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
    var = await sensor.new_sensor(config)
    cg.add(getattr(hub, TYPES[config[CONF_TYPE]]["setter"])(var))

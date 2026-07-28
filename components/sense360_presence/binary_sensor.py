"""sense360_presence binary_sensor platform (SENSE360-CANONICALISATION-001 PR 10).

Declares the component-owned fused occupancy output. Schema defaults equal
the pre-component template declaration verbatim; the framework YAML pins
the id and name, so the resolved entity surface is identical.
"""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import binary_sensor
from esphome.const import CONF_TYPE, DEVICE_CLASS_OCCUPANCY

from . import Sense360Presence

CONF_SENSE360_PRESENCE_ID = "sense360_presence_id"

TYPES = {
    "occupancy": {
        "schema": binary_sensor.binary_sensor_schema(
            device_class=DEVICE_CLASS_OCCUPANCY,
            icon="mdi:home-account",
        ),
        "setter": "set_occupancy_binary_sensor",
    },
}


def _base_schema(type_key):
    # NOTE: cv.typed_schema POPS the `type` key before validating against
    # the selected inner schema (and re-adds it afterwards), so the inner
    # schema must NOT declare `type` itself.
    return TYPES[type_key]["schema"].extend(
        {
            cv.GenerateID(CONF_SENSE360_PRESENCE_ID): cv.use_id(Sense360Presence),
        }
    )


CONFIG_SCHEMA = cv.typed_schema(
    {key: _base_schema(key) for key in TYPES},
    lower=True,
)


async def to_code(config):
    hub = await cg.get_variable(config[CONF_SENSE360_PRESENCE_ID])
    var = await binary_sensor.new_binary_sensor(config)
    cg.add(getattr(hub, TYPES[config[CONF_TYPE]]["setter"])(var))

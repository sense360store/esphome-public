"""sense360_presence text_sensor platform (SENSE360-CANONICALISATION-001 PR 10).

Declares the component-owned customer status output. The Core-Framework
"Presence Module Status" entity is deliberately NOT a type here — the hub
feeds it by id (CORE-FRAMEWORK-001 owns that entity).
"""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import text_sensor
from esphome.const import CONF_TYPE

from . import Sense360Presence

CONF_SENSE360_PRESENCE_ID = "sense360_presence_id"

TYPES = {
    "presence_status": {
        "schema": text_sensor.text_sensor_schema(icon="mdi:motion-sensor"),
        "setter": "set_status_text_sensor",
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
    var = await text_sensor.new_text_sensor(config)
    cg.add(getattr(hub, TYPES[config[CONF_TYPE]]["setter"])(var))

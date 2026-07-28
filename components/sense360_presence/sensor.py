"""sense360_presence sensor platform (SENSE360-CANONICALISATION-001 PR 10).

Declares the component-owned numeric outputs. Schema defaults equal the
pre-component template declarations verbatim ("Radar Target Count", never
"People Count" — radar targets are not verified people, PD-09; NAN while
stale, never a fake 0).
"""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor
from esphome.const import CONF_TYPE, STATE_CLASS_MEASUREMENT

from . import Sense360Presence

CONF_SENSE360_PRESENCE_ID = "sense360_presence_id"

TYPES = {
    "radar_target_count": {
        "schema": sensor.sensor_schema(
            state_class=STATE_CLASS_MEASUREMENT,
            accuracy_decimals=0,
            icon="mdi:radar",
        ),
        "setter": "set_radar_target_count_output",
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
    var = await sensor.new_sensor(config)
    cg.add(getattr(hub, TYPES[config[CONF_TYPE]]["setter"])(var))

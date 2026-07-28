"""sense360_ventiq text_sensor platform (SENSE360-CANONICALISATION-001 PR 11).

Component-owned headline / recommendation / reason / diagnostic outputs.
The Core-Framework "VentIQ Module Status" entity is fed by id, never
re-declared here.
"""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import text_sensor
from esphome.const import CONF_TYPE, ENTITY_CATEGORY_DIAGNOSTIC

from . import Sense360VentIQ

CONF_SENSE360_VENTIQ_ID = "sense360_ventiq_id"

TYPES = {
    "air_quality": {
        "schema": text_sensor.text_sensor_schema(icon="mdi:air-purifier"),
        "setter": "set_air_quality_text_sensor",
    },
    "recommendation": {
        "schema": text_sensor.text_sensor_schema(icon="mdi:lightbulb-outline"),
        "setter": "set_recommendation_text_sensor",
    },
    "reason": {
        "schema": text_sensor.text_sensor_schema(icon="mdi:head-question-outline"),
        "setter": "set_reason_text_sensor",
    },
    "state_detail": {
        "schema": text_sensor.text_sensor_schema(
            icon="mdi:text-search",
            entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ),
        "setter": "set_state_detail_text_sensor",
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
    var = await text_sensor.new_text_sensor(config)
    cg.add(getattr(hub, TYPES[config[CONF_TYPE]]["setter"])(var))

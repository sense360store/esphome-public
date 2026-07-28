"""sense360_airiq text_sensor platform (SENSE360-CANONICALISATION-001 PR 11).

Declares the component-owned headline / recommendation / diagnostic
outputs. The Core-Framework "AirIQ Module Status" entity and the legacy
`air_quality_state` compatibility entity are NOT types here — the hub feeds
both by id (CORE-FRAMEWORK-001 owns the former; the framework YAML keeps
the latter's declaration shape).
"""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import text_sensor
from esphome.const import CONF_TYPE, ENTITY_CATEGORY_DIAGNOSTIC

from . import Sense360AirIQ

CONF_SENSE360_AIRIQ_ID = "sense360_airiq_id"

TYPES = {
    "air_quality": {
        "schema": text_sensor.text_sensor_schema(icon="mdi:air-purifier"),
        "setter": "set_air_quality_text_sensor",
    },
    "recommendation": {
        "schema": text_sensor.text_sensor_schema(icon="mdi:lightbulb-outline"),
        "setter": "set_recommendation_text_sensor",
    },
    "state_detail": {
        "schema": text_sensor.text_sensor_schema(
            icon="mdi:text-search",
            entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ),
        "setter": "set_state_detail_text_sensor",
    },
    "recommendation_reason": {
        "schema": text_sensor.text_sensor_schema(
            icon="mdi:head-question-outline",
            entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ),
        "setter": "set_recommendation_reason_text_sensor",
    },
}


def _base_schema(type_key):
    # NOTE: cv.typed_schema POPS the `type` key before validating against
    # the selected inner schema (and re-adds it afterwards), so the inner
    # schema must NOT declare `type` itself.
    return TYPES[type_key]["schema"].extend(
        {
            cv.GenerateID(CONF_SENSE360_AIRIQ_ID): cv.use_id(Sense360AirIQ),
        }
    )


CONFIG_SCHEMA = cv.typed_schema(
    {key: _base_schema(key) for key in TYPES},
    lower=True,
)


async def to_code(config):
    hub = await cg.get_variable(config[CONF_SENSE360_AIRIQ_ID])
    var = await text_sensor.new_text_sensor(config)
    cg.add(getattr(hub, TYPES[config[CONF_TYPE]]["setter"])(var))

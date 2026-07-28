"""sense360_roomiq text_sensor platform (SENSE360-CANONICALISATION-001 PR 09).

Declares the component-owned state and diagnostic text outputs. Schema
defaults (icon, category) equal the pre-component template declarations
verbatim; the framework YAML pins ids and names explicitly, so the
resolved entity surface is identical. The Core-Framework-owned
"RoomIQ Module Status" entity is deliberately NOT a type here — the hub
binds it by id (CORE-FRAMEWORK-001 owns that entity; this component only
feeds it).
"""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import text_sensor
from esphome.const import CONF_TYPE, ENTITY_CATEGORY_DIAGNOSTIC

from . import Sense360RoomIQ

CONF_SENSE360_ROOMIQ_ID = "sense360_roomiq_id"

TYPES = {
    "comfort": {
        "schema": text_sensor.text_sensor_schema(icon="mdi:home-thermometer"),
        "setter": "set_comfort_text_sensor",
    },
    "environment_state": {
        "schema": text_sensor.text_sensor_schema(icon="mdi:home-analytics"),
        "setter": "set_environment_text_sensor",
    },
    "brightness": {
        "schema": text_sensor.text_sensor_schema(icon="mdi:brightness-6"),
        "setter": "set_brightness_text_sensor",
    },
    "environment_detail": {
        "schema": text_sensor.text_sensor_schema(
            icon="mdi:text-search",
            entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ),
        "setter": "set_environment_detail_text_sensor",
    },
    "calibration_state": {
        "schema": text_sensor.text_sensor_schema(
            icon="mdi:tune-vertical",
            entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ),
        "setter": "set_calibration_state_text_sensor",
    },
    "climate_profile": {
        "schema": text_sensor.text_sensor_schema(
            icon="mdi:tune-variant",
            entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ),
        "setter": "set_climate_profile_text_sensor",
    },
}


def _base_schema(type_key):
    # NOTE: cv.typed_schema POPS the `type` key before validating against
    # the selected inner schema (and re-adds it afterwards), so the inner
    # schema must NOT declare `type` itself.
    return TYPES[type_key]["schema"].extend(
        {
            cv.GenerateID(CONF_SENSE360_ROOMIQ_ID): cv.use_id(Sense360RoomIQ),
        }
    )


CONFIG_SCHEMA = cv.typed_schema(
    {key: _base_schema(key) for key in TYPES},
    lower=True,
)


async def to_code(config):
    hub = await cg.get_variable(config[CONF_SENSE360_ROOMIQ_ID])
    var = await text_sensor.new_text_sensor(config)
    cg.add(getattr(hub, TYPES[config[CONF_TYPE]]["setter"])(var))

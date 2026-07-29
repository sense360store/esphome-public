"""sense360_led text_sensor platform (SENSE360-CANONICALISATION-001 PR 12).

Declares the component-owned diagnostic text outputs. Schema defaults
(icon, category) equal the pre-component template declarations verbatim;
the framework YAML pins ids, names and disabled_by_default explicitly, so
the resolved entity surface is identical. The honesty companion
"LED Output Verification" is deliberately NOT a type here — it is a static
compile-time diagnostic that stays a YAML template entity published once at
boot (STATIC-DIAGNOSTIC-PUBLISH-001).
"""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import text_sensor
from esphome.const import CONF_TYPE, ENTITY_CATEGORY_DIAGNOSTIC

from . import Sense360Led

CONF_SENSE360_LED_ID = "sense360_led_id"

TYPES = {
    "active_layer": {
        "schema": text_sensor.text_sensor_schema(
            icon="mdi:layers-triple-outline",
            entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ),
        "setter": "set_active_layer_text_sensor",
    },
    "last_status_event": {
        "schema": text_sensor.text_sensor_schema(
            icon="mdi:message-alert-outline",
            entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ),
        "setter": "set_last_status_event_text_sensor",
    },
    "darkness_state": {
        "schema": text_sensor.text_sensor_schema(
            icon="mdi:theme-light-dark",
            entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ),
        "setter": "set_darkness_state_text_sensor",
    },
    "night_behaviour_status": {
        "schema": text_sensor.text_sensor_schema(
            icon="mdi:tune-variant",
            entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ),
        "setter": "set_night_behaviour_status_text_sensor",
    },
}


def _base_schema(type_key):
    # NOTE: cv.typed_schema POPS the `type` key before validating against
    # the selected inner schema (and re-adds it afterwards), so the inner
    # schema must NOT declare `type` itself.
    return TYPES[type_key]["schema"].extend(
        {
            cv.GenerateID(CONF_SENSE360_LED_ID): cv.use_id(Sense360Led),
        }
    )


CONFIG_SCHEMA = cv.typed_schema(
    {key: _base_schema(key) for key in TYPES},
    lower=True,
)


async def to_code(config):
    hub = await cg.get_variable(config[CONF_SENSE360_LED_ID])
    var = await text_sensor.new_text_sensor(config)
    cg.add(getattr(hub, TYPES[config[CONF_TYPE]]["setter"])(var))

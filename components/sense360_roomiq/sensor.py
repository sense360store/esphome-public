"""sense360_roomiq sensor platform (SENSE360-CANONICALISATION-001 PR 09).

Declares the component-owned numeric outputs. Every schema default below
(name, unit, device class, state class, accuracy, icon, category,
disabled-by-default) equals the pre-component template declaration in
``packages/features/roomiq_framework.yaml`` verbatim — the entity contract
in ``docs/architecture/sense360-roomiq-component-plan.md`` — and the
framework YAML pins ids and names explicitly, so the resolved entity
surface is identical.
"""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor
from esphome.const import (
    CONF_ID,
    CONF_TYPE,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_ILLUMINANCE,
    DEVICE_CLASS_TEMPERATURE,
    ENTITY_CATEGORY_DIAGNOSTIC,
    STATE_CLASS_MEASUREMENT,
    UNIT_CELSIUS,
    UNIT_LUX,
    UNIT_PERCENT,
)

from . import Sense360RoomIQ

CONF_SENSE360_ROOMIQ_ID = "sense360_roomiq_id"

TYPES = {
    "temperature": {
        "schema": sensor.sensor_schema(
            unit_of_measurement=UNIT_CELSIUS,
            device_class=DEVICE_CLASS_TEMPERATURE,
            state_class=STATE_CLASS_MEASUREMENT,
            accuracy_decimals=1,
            icon="mdi:thermometer",
        ),
        "setter": "set_temperature_sensor",
    },
    "humidity": {
        "schema": sensor.sensor_schema(
            unit_of_measurement=UNIT_PERCENT,
            device_class=DEVICE_CLASS_HUMIDITY,
            state_class=STATE_CLASS_MEASUREMENT,
            accuracy_decimals=1,
            icon="mdi:water-percent",
        ),
        "setter": "set_humidity_sensor",
    },
    "illuminance": {
        "schema": sensor.sensor_schema(
            unit_of_measurement=UNIT_LUX,
            device_class=DEVICE_CLASS_ILLUMINANCE,
            state_class=STATE_CLASS_MEASUREMENT,
            accuracy_decimals=0,
            icon="mdi:brightness-5",
        ),
        "setter": "set_illuminance_sensor",
    },
    "factory_temperature": {
        "schema": sensor.sensor_schema(
            unit_of_measurement=UNIT_CELSIUS,
            device_class=DEVICE_CLASS_TEMPERATURE,
            state_class=STATE_CLASS_MEASUREMENT,
            accuracy_decimals=2,
            icon="mdi:thermometer-check",
            entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ),
        "setter": "set_factory_temperature_sensor",
    },
    "factory_humidity": {
        "schema": sensor.sensor_schema(
            unit_of_measurement=UNIT_PERCENT,
            device_class=DEVICE_CLASS_HUMIDITY,
            state_class=STATE_CLASS_MEASUREMENT,
            accuracy_decimals=2,
            icon="mdi:water-check",
            entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ),
        "setter": "set_factory_humidity_sensor",
    },
}


def _base_schema(type_key):
    return TYPES[type_key]["schema"].extend(
        {
            cv.GenerateID(CONF_SENSE360_ROOMIQ_ID): cv.use_id(Sense360RoomIQ),
            cv.Required(CONF_TYPE): cv.one_of(type_key, lower=True),
        }
    )


CONFIG_SCHEMA = cv.typed_schema(
    {key: _base_schema(key) for key in TYPES},
    lower=True,
)


async def to_code(config):
    hub = await cg.get_variable(config[CONF_SENSE360_ROOMIQ_ID])
    var = await sensor.new_sensor(config)
    cg.add(getattr(hub, TYPES[config[CONF_TYPE]]["setter"])(var))

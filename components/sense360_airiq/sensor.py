"""sense360_airiq sensor platform (SENSE360-CANONICALISATION-001 PR 11).

Declares the component-owned pollutant outputs. Schema defaults equal the
pre-component template declarations verbatim; the framework YAML pins ids,
names and full metadata explicitly, so the resolved entity surface is
identical. VOC and NOx are deliberately unitless relative indices — never
concentrations; the headline is deliberately NOT an AQI.
"""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor
from esphome.const import (
    CONF_TYPE,
    DEVICE_CLASS_CARBON_DIOXIDE,
    DEVICE_CLASS_PM1,
    DEVICE_CLASS_PM10,
    DEVICE_CLASS_PM25,
    STATE_CLASS_MEASUREMENT,
)

from . import Sense360AirIQ

CONF_SENSE360_AIRIQ_ID = "sense360_airiq_id"

UNIT_MICROGRAMS_PER_CUBIC_METER = "µg/m³"

TYPES = {
    "co2": {
        "schema": sensor.sensor_schema(
            unit_of_measurement="ppm",
            device_class=DEVICE_CLASS_CARBON_DIOXIDE,
            state_class=STATE_CLASS_MEASUREMENT,
            accuracy_decimals=0,
            icon="mdi:molecule-co2",
        ),
        "setter": "set_co2_sensor",
    },
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
    "hcho": {
        "schema": sensor.sensor_schema(
            unit_of_measurement="ppb",
            state_class=STATE_CLASS_MEASUREMENT,
            accuracy_decimals=1,
            icon="mdi:molecule",
        ),
        "setter": "set_hcho_sensor",
    },
    "pm2_5": {
        "schema": sensor.sensor_schema(
            unit_of_measurement=UNIT_MICROGRAMS_PER_CUBIC_METER,
            device_class=DEVICE_CLASS_PM25,
            state_class=STATE_CLASS_MEASUREMENT,
            accuracy_decimals=1,
            icon="mdi:blur",
        ),
        "setter": "set_pm2_5_sensor",
    },
    "pm1": {
        "schema": sensor.sensor_schema(
            unit_of_measurement=UNIT_MICROGRAMS_PER_CUBIC_METER,
            device_class=DEVICE_CLASS_PM1,
            state_class=STATE_CLASS_MEASUREMENT,
            accuracy_decimals=1,
            icon="mdi:blur",
        ),
        "setter": "set_pm1_sensor",
    },
    "pm4": {
        "schema": sensor.sensor_schema(
            unit_of_measurement=UNIT_MICROGRAMS_PER_CUBIC_METER,
            state_class=STATE_CLASS_MEASUREMENT,
            accuracy_decimals=1,
            icon="mdi:blur",
        ),
        "setter": "set_pm4_sensor",
    },
    "pm10": {
        "schema": sensor.sensor_schema(
            unit_of_measurement=UNIT_MICROGRAMS_PER_CUBIC_METER,
            device_class=DEVICE_CLASS_PM10,
            state_class=STATE_CLASS_MEASUREMENT,
            accuracy_decimals=1,
            icon="mdi:blur",
        ),
        "setter": "set_pm10_sensor",
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
    var = await sensor.new_sensor(config)
    cg.add(getattr(hub, TYPES[config[CONF_TYPE]]["setter"])(var))

# ============================================================================
# SFA40 formaldehyde sensor — ESPHome sensor platform
# ============================================================================
# Usage (S360-210-R4 AirIQ, shared Core I2C bus @ 0x5D):
#
#   sensor:
#     - platform: sfa40
#       i2c_id: ${airiq_i2c_id}
#       address: 0x5D
#       update_interval: 30s
#       formaldehyde:
#         id: airiq_hcho
#       humidity:
#         id: airiq_sfa40_humidity
#       temperature:
#         id: airiq_sfa40_temperature
#
# Mirrors ESPHome's core `sfa30` sensor platform (Sensirion CRC-8 via
# sensirion_common) but drives the SFA40 command set. See __init__.py for the
# hardware/evidence context.
# ============================================================================
import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import i2c, sensor
from esphome.const import (
    CONF_FORMALDEHYDE,
    CONF_HUMIDITY,
    CONF_ID,
    CONF_TEMPERATURE,
    DEVICE_CLASS_GAS,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_TEMPERATURE,
    ICON_RADIATOR,
    ICON_THERMOMETER,
    ICON_WATER_PERCENT,
    STATE_CLASS_MEASUREMENT,
    UNIT_CELSIUS,
    UNIT_PARTS_PER_BILLION,
    UNIT_PERCENT,
)

from . import SFA40Component, sfa40_ns  # noqa: F401

DEPENDENCIES = ["i2c"]
AUTO_LOAD = ["sensirion_common"]

CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(SFA40Component),
            cv.Optional(CONF_FORMALDEHYDE): sensor.sensor_schema(
                unit_of_measurement=UNIT_PARTS_PER_BILLION,
                icon=ICON_RADIATOR,
                accuracy_decimals=1,
                device_class=DEVICE_CLASS_GAS,
                state_class=STATE_CLASS_MEASUREMENT,
            ),
            cv.Optional(CONF_HUMIDITY): sensor.sensor_schema(
                unit_of_measurement=UNIT_PERCENT,
                icon=ICON_WATER_PERCENT,
                accuracy_decimals=2,
                device_class=DEVICE_CLASS_HUMIDITY,
                state_class=STATE_CLASS_MEASUREMENT,
            ),
            cv.Optional(CONF_TEMPERATURE): sensor.sensor_schema(
                unit_of_measurement=UNIT_CELSIUS,
                icon=ICON_THERMOMETER,
                accuracy_decimals=2,
                device_class=DEVICE_CLASS_TEMPERATURE,
                state_class=STATE_CLASS_MEASUREMENT,
            ),
        }
    )
    .extend(cv.polling_component_schema("30s"))
    .extend(i2c.i2c_device_schema(0x5D))
)

SENSOR_MAP = {
    CONF_FORMALDEHYDE: "set_formaldehyde_sensor",
    CONF_HUMIDITY: "set_humidity_sensor",
    CONF_TEMPERATURE: "set_temperature_sensor",
}


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await i2c.register_i2c_device(var, config)

    for key, func_name in SENSOR_MAP.items():
        if sensor_config := config.get(key):
            sens = await sensor.new_sensor(sensor_config)
            cg.add(getattr(var, func_name)(sens))

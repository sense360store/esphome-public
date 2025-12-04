# Stub component for bme680_bsec to enable validation in network-restricted environments.
# This mimics the interface of github://boschsensortec/BSEC2-ESPHome but does not
# provide actual sensor functionality. For production use, the external component
# from Bosch should be used instead.
#
# To use the real component, set the substitution:
#   airiq_bsec2_git_credentials: ""  (or your credentials if needed)
# and ensure network access to GitHub is available.

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import i2c
from esphome.const import CONF_ID, CONF_ADDRESS

CODEOWNERS = ["@sense360store"]
DEPENDENCIES = ["i2c"]
AUTO_LOAD = ["sensor"]

CONF_BME680_BSEC_ID = "bme680_bsec_id"

bme680_bsec_ns = cg.esphome_ns.namespace("bme680_bsec")
BME680BSECComponent = bme680_bsec_ns.class_(
    "BME680BSECComponent", cg.PollingComponent, i2c.I2CDevice
)

CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(BME680BSECComponent),
        }
    )
    .extend(cv.polling_component_schema("60s"))
    .extend(i2c.i2c_device_schema(0x77))
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await i2c.register_i2c_device(var, config)

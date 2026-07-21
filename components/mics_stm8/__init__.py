# ============================================================================
# MICS-4514 + STM8 I2C bridge — external ESPHome component (hub)
# ============================================================================
# The MICS-4514 multi-gas sensor (S360-210-R4 U4) is digitised by an STM8S003F3U
# co-processor (U5) that exposes a fixed 24-byte register block plus a command
# register (0xFE) over the shared Core I2C bus at address 0x60. This hub reads
# and validity-gates that block; the individual entities (RED/OX ADC, baselines,
# ratios, status bits, fault detail, error counters, recalibrate button, ...)
# are declared as native `template` entities in the AirIQ board package, each
# reading a getter on this hub (e.g. `id(airiq_mics).red_ratio()`).
#
# The register map, I2C address (0x60), protocol version (1), identity ("M4")
# and current firmware (0x24) are per the owner-provided STM8 firmware
# specification. This component makes NO customer CO / NO2 concentration claim
# and NO hardware/bench/compliance claim; on-hardware verification of the fitted
# MICS/STM8 stage remains pending
# (docs/hardware/airiq-framework-bench-checklist.md).
# ============================================================================
import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import i2c
from esphome.const import CONF_ID

CODEOWNERS = ["@sense360store"]
DEPENDENCIES = ["i2c"]

mics_stm8_ns = cg.esphome_ns.namespace("mics_stm8")
MICSSTM8Component = mics_stm8_ns.class_(
    "MICSSTM8Component", cg.PollingComponent, i2c.I2CDevice
)

CONF_MICS_STM8_ID = "mics_stm8_id"

CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(MICSSTM8Component),
        }
    )
    .extend(cv.polling_component_schema("30s"))
    .extend(i2c.i2c_device_schema(0x60))
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await i2c.register_i2c_device(var, config)

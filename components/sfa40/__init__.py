# ============================================================================
# Sensirion SFA40 formaldehyde sensor — external ESPHome component
# ============================================================================
# The SFA40 (S360-210-R4 U2, Sensirion `SFA40-D-R`) is fitted on every AirIQ
# board on the shared Core I2C bus. It is the next-generation successor to the
# SFA30: it shares the SFA30's 0x5D I2C address and Sensirion CRC-8 but uses a
# DIFFERENT command set (start 0x00AC, read 0xC0EB, 12-byte / 4-word response)
# so ESPHome's native `sfa30` platform cannot read it. This scoped external
# component implements the SFA40 I2C protocol exactly per the Sensirion SFA40
# datasheet (D1 v1.1, April 2026, §3 "Interface Specifications").
#
# Evidence level: datasheet-derived protocol + compile proof only. This module
# makes NO hardware, bench, calibration, compliance, safety or commercial
# claim. On-hardware verification of the fitted SFA40 remains pending
# (docs/hardware/airiq-framework-bench-checklist.md).
# ============================================================================
import esphome.codegen as cg
from esphome.components import sensirion_common

CODEOWNERS = ["@sense360store"]
DEPENDENCIES = ["i2c"]
AUTO_LOAD = ["sensirion_common"]

sfa40_ns = cg.esphome_ns.namespace("sfa40")
SFA40Component = sfa40_ns.class_(
    "SFA40Component", cg.PollingComponent, sensirion_common.SensirionI2CDevice
)

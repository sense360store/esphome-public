"""sense360_roomiq — the RoomIQ domain component (SENSE360-CANONICALISATION-001 PR 09).

Wraps the canonical header-only RoomIQ engine
(``components/sense360/roomiq_engine.h`` — the SAME
``sense360::roomiq::global_engine()`` singleton the LED framework reads, per
the singleton contract in
``docs/architecture/sense360-roomiq-component-plan.md``) as a real ESPHome
component. It owns what used to be YAML glue in
``packages/features/roomiq_framework.yaml``: input feeding from the three
raw sources, threshold/window configuration, the 5 s evaluation tick, the
single-owner publish-on-change switchboard, and the persisted
calibration-schema migration.

The environmental model itself (compensation, psychrometric humidity,
freshness, calibration clamping, classification) stays in the natively
tested engine headers — this component contains glue only, no model logic
and no raw hardware I/O (the sources are ordinary ESPHome sensors composed
by the board package).

Every default below equals the pre-component substitution default verbatim;
the SHT45 compensation constants live in the engine profile and are not
restated (provisional engineering values, unchanged by PR 09).
"""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import number, sensor
from esphome.const import CONF_ID

CODEOWNERS = ["@sense360store"]
# The foundation component delivers the engine headers this component
# compiles against; auto-loading it keeps single-source delivery without
# requiring a bare `sense360:` block in every config. The entity base
# components are auto-loaded because the glue references their headers
# unconditionally (the standard ESPHome hub idiom).
AUTO_LOAD = ["sense360", "sensor", "text_sensor", "number"]

sense360_roomiq_ns = cg.esphome_ns.namespace("sense360_roomiq")
Sense360RoomIQ = sense360_roomiq_ns.class_("Sense360RoomIQ", cg.Component)

CONF_TEMPERATURE_SOURCE = "temperature_source"
CONF_HUMIDITY_SOURCE = "humidity_source"
CONF_ILLUMINANCE_SOURCE = "illuminance_source"
CONF_TEMPERATURE_OFFSET_NUMBER = "temperature_offset_number"
CONF_HUMIDITY_OFFSET_NUMBER = "humidity_offset_number"
CONF_ILLUMINANCE_SCALE_NUMBER = "illuminance_scale_number"
CONF_CALIBRATION_SCHEMA_VERSION = "calibration_schema_version"
CONF_CLIMATE_WARMUP = "climate_warmup"
CONF_CLIMATE_STALE = "climate_stale"
CONF_ILLUMINANCE_WARMUP = "illuminance_warmup"
CONF_ILLUMINANCE_STALE = "illuminance_stale"
CONF_CLIMATE_PAIR_SKEW = "climate_pair_skew"
CONF_TEMP_COLD = "temperature_cold"
CONF_TEMP_COOL = "temperature_cool"
CONF_TEMP_WARM = "temperature_warm"
CONF_TEMP_HOT = "temperature_hot"
CONF_TEMP_HYSTERESIS = "temperature_hysteresis"
CONF_HUMIDITY_DRY = "humidity_dry"
CONF_HUMIDITY_HUMID = "humidity_humid"
CONF_HUMIDITY_HYSTERESIS = "humidity_hysteresis"
CONF_LUX_DIM = "lux_dim"
CONF_LUX_NORMAL = "lux_normal"
CONF_LUX_BRIGHT = "lux_bright"
CONF_LUX_VERY_BRIGHT = "lux_very_bright"
CONF_BRIGHTNESS_HYSTERESIS_PCT = "brightness_hysteresis_pct"

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(Sense360RoomIQ),
        cv.Required(CONF_TEMPERATURE_SOURCE): cv.use_id(sensor.Sensor),
        cv.Required(CONF_HUMIDITY_SOURCE): cv.use_id(sensor.Sensor),
        cv.Required(CONF_ILLUMINANCE_SOURCE): cv.use_id(sensor.Sensor),
        # Customer calibration controls stay ordinary persisted template
        # numbers in YAML (their entity ids AND their NVS restore identity
        # are protected compatibility contracts); the component reads them.
        cv.Optional(CONF_TEMPERATURE_OFFSET_NUMBER): cv.use_id(number.Number),
        cv.Optional(CONF_HUMIDITY_OFFSET_NUMBER): cv.use_id(number.Number),
        cv.Optional(CONF_ILLUMINANCE_SCALE_NUMBER): cv.use_id(number.Number),
        # The persisted schema marker and its one-time migration stay in
        # YAML for this slice (same global id, same stored preference, so
        # the one-time calibration reset can never re-fire on upgrade);
        # slice 2 decides its final home against the compile lane.
        cv.Optional(CONF_CALIBRATION_SCHEMA_VERSION, default=2): cv.positive_int,
        # Freshness windows — provisional engineering defaults, identical to
        # the pre-component substitution defaults.
        cv.Optional(
            CONF_CLIMATE_WARMUP, default="60s"
        ): cv.positive_time_period_milliseconds,
        cv.Optional(
            CONF_CLIMATE_STALE, default="90s"
        ): cv.positive_time_period_milliseconds,
        cv.Optional(
            CONF_ILLUMINANCE_WARMUP, default="30s"
        ): cv.positive_time_period_milliseconds,
        cv.Optional(
            CONF_ILLUMINANCE_STALE, default="60s"
        ): cv.positive_time_period_milliseconds,
        cv.Optional(
            CONF_CLIMATE_PAIR_SKEW, default="5s"
        ): cv.positive_time_period_milliseconds,
        # Comfort thresholds (°C / %RH) — provisional comfort heuristics,
        # never medical/health thresholds.
        cv.Optional(CONF_TEMP_COLD, default=16.0): cv.float_,
        cv.Optional(CONF_TEMP_COOL, default=18.0): cv.float_,
        cv.Optional(CONF_TEMP_WARM, default=24.0): cv.float_,
        cv.Optional(CONF_TEMP_HOT, default=27.0): cv.float_,
        cv.Optional(CONF_TEMP_HYSTERESIS, default=0.3): cv.float_,
        cv.Optional(CONF_HUMIDITY_DRY, default=30.0): cv.float_,
        cv.Optional(CONF_HUMIDITY_HUMID, default=60.0): cv.float_,
        cv.Optional(CONF_HUMIDITY_HYSTERESIS, default=2.0): cv.float_,
        # Brightness bands (lx) — provisional room-ambience categories.
        cv.Optional(CONF_LUX_DIM, default=10.0): cv.float_,
        cv.Optional(CONF_LUX_NORMAL, default=50.0): cv.float_,
        cv.Optional(CONF_LUX_BRIGHT, default=300.0): cv.float_,
        cv.Optional(CONF_LUX_VERY_BRIGHT, default=1000.0): cv.float_,
        cv.Optional(CONF_BRIGHTNESS_HYSTERESIS_PCT, default=20.0): cv.float_,
    }
).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    for key, setter in (
        (CONF_TEMPERATURE_SOURCE, var.set_temperature_source),
        (CONF_HUMIDITY_SOURCE, var.set_humidity_source),
        (CONF_ILLUMINANCE_SOURCE, var.set_illuminance_source),
    ):
        source = await cg.get_variable(config[key])
        cg.add(setter(source))

    for key, setter in (
        (CONF_TEMPERATURE_OFFSET_NUMBER, var.set_temperature_offset_number),
        (CONF_HUMIDITY_OFFSET_NUMBER, var.set_humidity_offset_number),
        (CONF_ILLUMINANCE_SCALE_NUMBER, var.set_illuminance_scale_number),
    ):
        if key in config:
            bound = await cg.get_variable(config[key])
            cg.add(setter(bound))

    cg.add(var.set_climate_windows(config[CONF_CLIMATE_WARMUP], config[CONF_CLIMATE_STALE]))
    cg.add(
        var.set_illuminance_windows(
            config[CONF_ILLUMINANCE_WARMUP], config[CONF_ILLUMINANCE_STALE]
        )
    )
    cg.add(var.set_climate_pair_skew(config[CONF_CLIMATE_PAIR_SKEW]))
    cg.add(
        var.set_temperature_bands(
            config[CONF_TEMP_COLD],
            config[CONF_TEMP_COOL],
            config[CONF_TEMP_WARM],
            config[CONF_TEMP_HOT],
            config[CONF_TEMP_HYSTERESIS],
        )
    )
    cg.add(
        var.set_humidity_bands(
            config[CONF_HUMIDITY_DRY],
            config[CONF_HUMIDITY_HUMID],
            config[CONF_HUMIDITY_HYSTERESIS],
        )
    )
    cg.add(
        var.set_brightness_bands(
            config[CONF_LUX_DIM],
            config[CONF_LUX_NORMAL],
            config[CONF_LUX_BRIGHT],
            config[CONF_LUX_VERY_BRIGHT],
            config[CONF_BRIGHTNESS_HYSTERESIS_PCT],
        )
    )
    cg.add(var.set_calibration_schema_version(config[CONF_CALIBRATION_SCHEMA_VERSION]))

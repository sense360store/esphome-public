"""sense360_led — the LED domain component (SENSE360-CANONICALISATION-001 PR 12).

Wraps the canonical LED customer-experience controller singleton
(``sense360::ledfw::global_controller()`` from
``components/sense360/led_controller.h``) as a real ESPHome component, per
``docs/architecture/sense360-led-component-plan.md``. It owns what used to
be YAML glue in ``packages/features/led_framework.yaml``: engine
configuration from the bound customer controls, the darkness service (a
direct read of the canonical RoomIQ environmental engine singleton — ONE
lux-threshold implementation, LED-FRAMEWORK-002), customer-intent
arbitration against the bound Room Light, the arbitrated light apply, the
250 ms tick and the diagnostics switchboard.

The YAML keeps: the persisted customer-state globals and the boot-restore
hook (NVS identity is a protected contract; the hook calls
``mark_booted()``), the api/wifi status notify hooks and the identify
button (engine-action one-liners), the night-mode switch (engine-truth
lambda) and the 1 s stable-state persistence mirror. The presence bridge
feeds the controller's occupancy input directly (LED-04: the fused
contract, never raw sensors). Every default and timing stays a provisional
software-defined engineering value pending bench validation; LED stays
preview and nothing here claims hardware proof.
"""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import light, number, select
from esphome.const import CONF_ID

CODEOWNERS = ["@sense360store"]
AUTO_LOAD = ["sense360", "light", "select", "number", "text_sensor"]

sense360_led_ns = cg.esphome_ns.namespace("sense360_led")
Sense360Led = sense360_led_ns.class_("Sense360Led", cg.Component)

CONF_LIGHT_ID = "light_id"
CONF_NIGHT_BEHAVIOUR_SELECT = "night_behaviour_select"
CONF_STATUS_INDICATOR_SELECT = "status_indicator_select"
CONF_DARKNESS_THRESHOLD_NUMBER = "darkness_threshold_number"
CONF_MAX_BRIGHTNESS_PCT = "max_brightness_pct"
CONF_NIGHT_BRIGHTNESS_PCT = "night_brightness_pct"
CONF_NIGHT_RED = "night_red"
CONF_NIGHT_GREEN = "night_green"
CONF_NIGHT_BLUE = "night_blue"
CONF_DARKNESS_HYSTERESIS = "darkness_hysteresis"
CONF_NIGHT_AUTO_OFF = "night_auto_off"
CONF_IDENTIFY_DURATION = "identify_duration"
CONF_STATUS_DURATION = "status_duration"
CONF_HAS_ROOMIQ = "has_roomiq"
CONF_HAS_PRESENCE = "has_presence"

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(Sense360Led),
        # The single customer Room Light (owned by the LED board package).
        cv.Required(CONF_LIGHT_ID): cv.use_id(light.LightState),
        # Customer controls stay persisted template entities in YAML (entity
        # ids and restore identity are protected contracts); the hub binds
        # them and re-evaluates on change.
        cv.Required(CONF_NIGHT_BEHAVIOUR_SELECT): cv.use_id(select.Select),
        cv.Required(CONF_STATUS_INDICATOR_SELECT): cv.use_id(select.Select),
        cv.Required(CONF_DARKNESS_THRESHOLD_NUMBER): cv.use_id(number.Number),
        # Provisional software-defined values (framework substitutions flow
        # through verbatim; never a physical-safety claim).
        cv.Required(CONF_MAX_BRIGHTNESS_PCT): cv.float_,
        cv.Required(CONF_NIGHT_BRIGHTNESS_PCT): cv.float_,
        cv.Required(CONF_NIGHT_RED): cv.float_,
        cv.Required(CONF_NIGHT_GREEN): cv.float_,
        cv.Required(CONF_NIGHT_BLUE): cv.float_,
        cv.Required(CONF_DARKNESS_HYSTERESIS): cv.float_,
        cv.Required(CONF_NIGHT_AUTO_OFF): cv.positive_time_period_milliseconds,
        cv.Required(CONF_IDENTIFY_DURATION): cv.positive_time_period_milliseconds,
        cv.Required(CONF_STATUS_DURATION): cv.positive_time_period_milliseconds,
        # Compile-time composition capabilities (LED-FRAMEWORK-002): an
        # automatic behaviour whose required framework is absent is honestly
        # downgraded to Manual inside the engine.
        cv.Required(CONF_HAS_ROOMIQ): cv.boolean,
        cv.Required(CONF_HAS_PRESENCE): cv.boolean,
    }
).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    for key, setter in (
        (CONF_LIGHT_ID, var.set_light),
        (CONF_NIGHT_BEHAVIOUR_SELECT, var.set_night_behaviour_select),
        (CONF_STATUS_INDICATOR_SELECT, var.set_status_indicator_select),
        (CONF_DARKNESS_THRESHOLD_NUMBER, var.set_darkness_threshold_number),
    ):
        bound = await cg.get_variable(config[key])
        cg.add(setter(bound))

    cg.add(
        var.set_profiles(
            config[CONF_MAX_BRIGHTNESS_PCT],
            config[CONF_NIGHT_BRIGHTNESS_PCT],
            config[CONF_NIGHT_RED],
            config[CONF_NIGHT_GREEN],
            config[CONF_NIGHT_BLUE],
        )
    )
    cg.add(var.set_darkness_hysteresis(config[CONF_DARKNESS_HYSTERESIS]))
    cg.add(
        var.set_timings(
            config[CONF_NIGHT_AUTO_OFF],
            config[CONF_IDENTIFY_DURATION],
            config[CONF_STATUS_DURATION],
        )
    )
    cg.add(var.set_capabilities(config[CONF_HAS_ROOMIQ], config[CONF_HAS_PRESENCE]))

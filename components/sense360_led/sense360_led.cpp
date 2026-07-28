#include "sense360_led.h"

#include <cmath>

#include "esphome/components/sense360/roomiq_engine.h"
#include "esphome/core/hal.h"
#include "esphome/core/log.h"

namespace esphome {
namespace sense360_led {

static const char *const TAG = "sense360_led";

static constexpr uint32_t EVALUATE_INTERVAL_MS = 250;

// Two float channel values count as one customer intent when within this
// band — light hardware quantises brightness/colour, so an exact compare
// would misread every engine apply as a manual change.
static constexpr float CHANNEL_EPSILON = 0.02f;

static bool differs(float a, float b) {
  return std::fabs(a - b) > CHANNEL_EPSILON;
}

float Sense360Led::get_setup_priority() const { return setup_priority::DATA; }

void Sense360Led::setup() {
  // Control changes re-evaluate immediately (the controls stay persisted
  // template entities in YAML; their values are read in evaluate()).
  if (this->night_behaviour_select_ != nullptr) {
    this->night_behaviour_select_->add_on_state_callback(
        [this](size_t) { this->evaluate(); });
  }
  if (this->status_indicator_select_ != nullptr) {
    this->status_indicator_select_->add_on_state_callback(
        [this](size_t) { this->evaluate(); });
  }
  if (this->darkness_threshold_number_ != nullptr) {
    this->darkness_threshold_number_->add_on_state_callback(
        [this](float) { this->evaluate(); });
  }

  // No evaluation before the YAML restore hook opens the boot gate.
  this->set_interval("s360_led_evaluate", EVALUATE_INTERVAL_MS,
                     [this]() { this->evaluate(); });
}

sense360::ledfw::LightState Sense360Led::read_light_() const {
  sense360::ledfw::LightState seen;
  auto values = this->light_->remote_values;
  seen.on = values.is_on();
  seen.brightness = values.get_brightness();
  seen.red = values.get_red();
  seen.green = values.get_green();
  seen.blue = values.get_blue();
  seen.effect = 0;
  const std::string effect = this->light_->get_effect_name();
  if (effect == "Gentle Pulse") {
    seen.effect = 1;
  } else if (effect == "Night Glow") {
    seen.effect = 2;
  }
  return seen;
}

void Sense360Led::publish_changed_(text_sensor::TextSensor *target,
                                   const std::string &value) {
  if (target == nullptr)
    return;
  if (target->state != value)
    target->publish_state(value);
}

void Sense360Led::evaluate() {
  using namespace sense360::ledfw;
  auto &controller = global_controller();
  if (!this->booted_)
    return;
  const uint32_t now = millis();

  // Runtime configuration (customer controls + config; no recompilation
  // needed for the customer-facing values).
  controller.set_max_brightness(this->max_brightness_pct_ / 100.0f);
  controller.set_night_profile(this->night_brightness_pct_ / 100.0f,
                               this->night_red_, this->night_green_,
                               this->night_blue_);
  // Compile-time composition capabilities (LED-FRAMEWORK-002): an automatic
  // behaviour whose input is not composed is downgraded to Manual inside the
  // engine (single source of truth for the honest select fallback).
  controller.set_capabilities(this->has_roomiq_, this->has_presence_);
  controller.set_night_behaviour(night_behaviour_from_string(
      this->night_behaviour_select_->current_option().c_str()));
  controller.set_status_level(status_level_from_string(
      this->status_indicator_select_->current_option().c_str()));
  controller.set_night_auto_off_ms(this->night_auto_off_ms_);
  controller.set_identify_duration_ms(this->identify_ms_);
  controller.set_status_duration_ms(this->status_ms_);

  // Darkness input (LED-05, ROOMIQ-FRAMEWORK-001): the canonical RoomIQ
  // darkness service computes the decision (calibrated illuminance,
  // staleness, hysteresis — ONE implementation). The LED customer Darkness
  // Threshold parameterises it; UNKNOWN (missing/stale/invalid lux) fails
  // safe downstream.
  {
    auto &environment = sense360::roomiq::global_engine();
    const float threshold = this->darkness_threshold_number_->state;
    if (!std::isnan(threshold) && threshold > 0.0f) {
      environment.set_darkness_threshold(threshold);
    }
    environment.set_darkness_hysteresis(this->darkness_hysteresis_);
    environment.evaluate(now);
    Darkness darkness = DARKNESS_UNKNOWN;
    if (environment.darkness() == sense360::roomiq::DARKNESS_DARK) {
      darkness = DARKNESS_DARK;
    } else if (environment.darkness() == sense360::roomiq::DARKNESS_NOT_DARK) {
      darkness = DARKNESS_NOT_DARK;
    }
    controller.input_darkness(now, darkness);
  }

  // Occupancy is fed by the presence bridge on the fused contract's own
  // callbacks (LED-04) — the engine stores the state, so nothing is read
  // here. On a Presence-less device it stays not-occupied / not-valid and
  // any occupancy-gated automation freezes (never invented).

  // Ownership detection: the light's current target vs the engine's last
  // arbitrated output. A difference the engine did not command is
  // customer/manual intent — customer intent always wins (it cancels
  // overlays and disengages Night Mode).
  {
    const sense360::ledfw::LightState seen = this->read_light_();
    const sense360::ledfw::LightState &expected = controller.output();
    // While an approved effect the engine commanded is running, the effect
    // owns brightness/colour — only on/effect changes count.
    const bool effect_running =
        expected.effect != 0 && seen.effect == expected.effect;
    bool customer_change =
        seen.on != expected.on || seen.effect != expected.effect;
    if (!customer_change && seen.on && !effect_running) {
      customer_change = differs(seen.brightness, expected.brightness) ||
                        differs(seen.red, expected.red) ||
                        differs(seen.green, expected.green) ||
                        differs(seen.blue, expected.blue);
    }
    if (customer_change) {
      controller.input_customer_command(now, seen);
    }
  }

  controller.evaluate(now);

  // Apply the arbitrated output when the light differs from it.
  {
    const sense360::ledfw::LightState &out = controller.output();
    const sense360::ledfw::LightState seen = this->read_light_();
    const bool effect_running = out.effect != 0 && seen.effect == out.effect;
    bool apply = seen.on != out.on || seen.effect != out.effect;
    if (!apply && out.on && !effect_running) {
      apply = differs(seen.brightness, out.brightness) ||
              differs(seen.red, out.red) || differs(seen.green, out.green) ||
              differs(seen.blue, out.blue);
    }
    if (apply) {
      auto call = this->light_->make_call();
      call.set_state(out.on);
      bool effect_set = false;
      if (out.on) {
        call.set_brightness(out.brightness);
        call.set_rgb(out.red, out.green, out.blue);
        if (out.effect == 1) {
          call.set_effect("Gentle Pulse");
          effect_set = true;
        } else if (out.effect == 2) {
          call.set_effect("Night Glow");
          effect_set = true;
        } else if (seen.effect != 0) {
          call.set_effect("none");
          effect_set = true;
        }
      }
      // A light call cannot carry an effect AND a transition.
      if (!effect_set)
        call.set_transition_length(250);
      call.perform();
    }
  }

  // Diagnostics (publish on change only). The stable-state persistence
  // mirror stays in YAML — the restore globals' NVS identity is a protected
  // contract this component never touches.
  this->publish_changed_(this->active_layer_text_sensor_,
                         layer_to_string(controller.active_layer()));
  this->publish_changed_(this->darkness_state_text_sensor_,
                         darkness_to_string(controller.darkness()));
  // Honest Night Mode Behaviour fallback (LED-FRAMEWORK-002): when the
  // customer selects an automatic mode this composition cannot support (no
  // RoomIQ / no Presence), the engine has already downgraded it to Manual.
  // State that plainly and persistently (with which absent framework caused
  // it) — the selection is kept, but the mode is never silently pretended
  // active.
  this->publish_changed_(this->night_behaviour_status_text_sensor_,
                         controller.behaviour_status());
  if (controller.has_status_event()) {
    std::string event = event_to_string(controller.last_status_event());
    if (controller.last_status_suppressed()) {
      event += " (suppressed)";
    }
    this->publish_changed_(this->last_status_event_text_sensor_, event);
  }
}

void Sense360Led::dump_config() {
  ESP_LOGCONFIG(TAG, "Sense360 LED (glue over the canonical customer LED "
                     "controller singleton; the arbitration model lives in "
                     "components/sense360/led_controller.h)");
  ESP_LOGCONFIG(TAG,
                "  Capabilities: roomiq=%s presence=%s (composition facts; an "
                "automatic behaviour without its input downgrades to Manual)",
                YESNO(this->has_roomiq_), YESNO(this->has_presence_));
}

} // namespace sense360_led
} // namespace esphome

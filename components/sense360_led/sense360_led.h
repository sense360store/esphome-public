#pragma once
// ============================================================================
// sense360_led — LED domain component (SENSE360-CANONICALISATION-001 PR 12)
// ============================================================================
// Glue only: configures, feeds and applies the canonical LED
// customer-experience controller singleton
// (sense360::ledfw::global_controller() from
// components/sense360/led_controller.h). The arbitration model — priority
// layers, state ownership, fail-safe rules, the restore contract — lives in
// the natively tested engine header and is never duplicated here. See
// docs/architecture/sense360-led-component-plan.md.
//
// The darkness decision is a direct read of the canonical RoomIQ
// environmental engine singleton (LED-FRAMEWORK-002): the customer threshold
// parameterises that ONE lux implementation, and with no lux input the
// engine reports DARKNESS_UNKNOWN — darkness is never invented. Occupancy
// arrives from the presence bridge as the fused contract (LED-04), never a
// raw sensor. The boot gate (mark_booted()) keeps every output silent until
// the YAML restore hook has re-applied the persisted customer state, so an
// interrupted transient overlay can never replay after a restart.
//
// Every brightness, colour and timing value is a PROVISIONAL,
// software-defined engineering default pending bench validation. LED stays
// preview; nothing here claims hardware, bench, compliance or commercial
// proof.
// ============================================================================

#include "esphome/components/light/light_state.h"
#include "esphome/components/number/number.h"
#include "esphome/components/select/select.h"
#include "esphome/components/sense360/led_controller.h"
#include "esphome/components/text_sensor/text_sensor.h"
#include "esphome/core/component.h"

namespace esphome {
namespace sense360_led {

class Sense360Led : public Component {
public:
  void set_light(light::LightState *l) { light_ = l; }
  void set_night_behaviour_select(select::Select *s) {
    night_behaviour_select_ = s;
  }
  void set_status_indicator_select(select::Select *s) {
    status_indicator_select_ = s;
  }
  void set_darkness_threshold_number(number::Number *n) {
    darkness_threshold_number_ = n;
  }

  void set_profiles(float max_brightness_pct, float night_brightness_pct,
                    float night_red, float night_green, float night_blue) {
    max_brightness_pct_ = max_brightness_pct;
    night_brightness_pct_ = night_brightness_pct;
    night_red_ = night_red;
    night_green_ = night_green;
    night_blue_ = night_blue;
  }
  void set_darkness_hysteresis(float factor) { darkness_hysteresis_ = factor; }
  void set_timings(uint32_t night_auto_off_ms, uint32_t identify_ms,
                   uint32_t status_ms) {
    night_auto_off_ms_ = night_auto_off_ms;
    identify_ms_ = identify_ms;
    status_ms_ = status_ms;
  }
  void set_capabilities(bool has_roomiq, bool has_presence) {
    has_roomiq_ = has_roomiq;
    has_presence_ = has_presence;
  }

  // --- output entities (platform-registered; nullptr = not composed) ---
  void set_active_layer_text_sensor(text_sensor::TextSensor *t) {
    active_layer_text_sensor_ = t;
  }
  void set_last_status_event_text_sensor(text_sensor::TextSensor *t) {
    last_status_event_text_sensor_ = t;
  }
  void set_darkness_state_text_sensor(text_sensor::TextSensor *t) {
    darkness_state_text_sensor_ = t;
  }
  void set_night_behaviour_status_text_sensor(text_sensor::TextSensor *t) {
    night_behaviour_status_text_sensor_ = t;
  }

  void setup() override;
  void dump_config() override;
  float get_setup_priority() const override;

  // Boot gate (LED-11): the framework's on_boot restore hook calls this
  // AFTER re-applying the persisted customer state to the engine, so no
  // evaluation ever runs against unrestored state. Queried by the YAML
  // persistence mirror too — nothing is written back to the restore globals
  // before restore itself has run.
  void mark_booted() { booted_ = true; }
  bool booted() const { return booted_; }

  // The single evaluation owner. Public for the framework's same-id bridge
  // script (the boot hook, api/wifi status notifies, the night-mode switch,
  // the identify button and the presence bridge all re-evaluate through it).
  void evaluate();

protected:
  sense360::ledfw::LightState read_light_() const;
  void publish_changed_(text_sensor::TextSensor *target,
                        const std::string &value);

  light::LightState *light_{nullptr};
  select::Select *night_behaviour_select_{nullptr};
  select::Select *status_indicator_select_{nullptr};
  number::Number *darkness_threshold_number_{nullptr};

  text_sensor::TextSensor *active_layer_text_sensor_{nullptr};
  text_sensor::TextSensor *last_status_event_text_sensor_{nullptr};
  text_sensor::TextSensor *darkness_state_text_sensor_{nullptr};
  text_sensor::TextSensor *night_behaviour_status_text_sensor_{nullptr};

  float max_brightness_pct_{100.0f};
  float night_brightness_pct_{5.0f};
  float night_red_{1.0f};
  float night_green_{0.58f};
  float night_blue_{0.16f};
  float darkness_hysteresis_{1.5f};
  uint32_t night_auto_off_ms_{60000};
  uint32_t identify_ms_{4000};
  uint32_t status_ms_{1500};
  bool has_roomiq_{false};
  bool has_presence_{false};

  bool booted_{false};
};

} // namespace sense360_led
} // namespace esphome

#pragma once
// ============================================================================
// sense360_presence — Presence domain component (SENSE360-CANONICALISATION-001
// PR 10)
// ============================================================================
// Glue only: feeds and publishes the canonical tri-sensor fusion singleton
// (sense360::presence::global_engine() — the fusion model, fail-safe rules,
// status precedence and PD-07 health live in the natively tested engine
// header, not here). See docs/architecture/sense360-presence-component-plan.md.
//
// The OD-SOT-004 evidence distinction is preserved unchanged: GPIO-level
// channels (PIR, SEN0609 digital out) are configured non-verifiable — they
// can never be proven fresh nor proven failed — and only the LD2450's
// frame-driven freshness carries a real health signal.
//
// Publication follows the pre-component single-owner contract: one evaluate
// path, publish on change only, radar target count honest about freshness
// (NAN while stale, never a fake 0). Output entity pointers are optional so
// partial compositions stay valid.
// ============================================================================

#include "esphome/components/binary_sensor/binary_sensor.h"
#include "esphome/components/number/number.h"
#include "esphome/components/select/select.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/text_sensor/text_sensor.h"
#include "esphome/components/sense360/presence_fusion.h"
#include "esphome/core/component.h"

namespace esphome {
namespace sense360_presence {

class Sense360Presence : public Component {
 public:
  // --- adapter-owned inputs (bound by id; adapters untouched) ---
  void set_pir_sensor(binary_sensor::BinarySensor *s) { pir_sensor_ = s; }
  void set_static_sensor(binary_sensor::BinarySensor *s) { static_sensor_ = s; }
  void set_radar_target_count_sensor(sensor::Sensor *s) { radar_target_count_sensor_ = s; }
  void set_radar_moving_count_sensor(sensor::Sensor *s) { radar_moving_count_sensor_ = s; }
  void set_radar_still_count_sensor(sensor::Sensor *s) { radar_still_count_sensor_ = s; }

  // --- runtime customer controls (persisted template entities in YAML) ---
  void set_mode_select(select::Select *s) { mode_select_ = s; }
  void set_clear_delay_number(number::Number *n) { clear_delay_number_ = n; }

  // --- configuration (defaults equal the pre-component substitutions) ---
  void set_channel_expectations(bool pir, bool radar, bool sen0609) {
    pir_expected_ = pir;
    radar_expected_ = radar;
    static_expected_ = sen0609;
  }
  void set_warmups(uint32_t pir_ms, uint32_t radar_ms, uint32_t static_ms,
                   uint32_t radar_stale_ms) {
    pir_warmup_ms_ = pir_ms;
    radar_warmup_ms_ = radar_ms;
    static_warmup_ms_ = static_ms;
    radar_stale_ms_ = radar_stale_ms;
  }

  // --- output entities (platform-registered; nullptr = not composed) ---
  void set_occupancy_binary_sensor(binary_sensor::BinarySensor *b) { occupancy_binary_sensor_ = b; }
  void set_status_text_sensor(text_sensor::TextSensor *t) { status_text_sensor_ = t; }
  void set_module_status_text_sensor(text_sensor::TextSensor *t) { module_status_text_sensor_ = t; }
  void set_radar_target_count_output(sensor::Sensor *s) { radar_target_count_output_ = s; }

  void setup() override;
  void dump_config() override;
  float get_setup_priority() const override;

  // The single evaluation owner. Public so the framework's same-id bridge
  // script (the PIR / SEN0609 adapters' documented re-evaluation hook) can
  // trigger it.
  void evaluate();

  // Seconds since the last real radar frame (NAN before the first frame) —
  // read by the framework's stale-data diagnostic.
  float radar_data_age_s() const;

 protected:
  binary_sensor::BinarySensor *pir_sensor_{nullptr};
  binary_sensor::BinarySensor *static_sensor_{nullptr};
  sensor::Sensor *radar_target_count_sensor_{nullptr};
  sensor::Sensor *radar_moving_count_sensor_{nullptr};
  sensor::Sensor *radar_still_count_sensor_{nullptr};
  select::Select *mode_select_{nullptr};
  number::Number *clear_delay_number_{nullptr};

  binary_sensor::BinarySensor *occupancy_binary_sensor_{nullptr};
  text_sensor::TextSensor *status_text_sensor_{nullptr};
  text_sensor::TextSensor *module_status_text_sensor_{nullptr};
  sensor::Sensor *radar_target_count_output_{nullptr};

  bool pir_expected_{true};
  bool radar_expected_{true};
  bool static_expected_{true};
  uint32_t pir_warmup_ms_{30000};
  uint32_t radar_warmup_ms_{10000};
  uint32_t static_warmup_ms_{15000};
  uint32_t radar_stale_ms_{5000};

  // Radar frame bookkeeping: any real update callback from the bound radar
  // sensors is a frame (the same component-callback signal the retired
  // adapter globals recorded).
  bool radar_frame_seen_{false};
  uint32_t radar_last_frame_ms_{0};

  // Guard so mode presets applying the Clear Delay preset do not bounce the
  // mode select to Custom (the former transient YAML global, internalised).
  bool applying_mode_{false};

  void on_mode_changed_(const std::string &value);
  void on_clear_delay_changed_(float value);
};

}  // namespace sense360_presence
}  // namespace esphome

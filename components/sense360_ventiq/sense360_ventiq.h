#pragma once
// ============================================================================
// sense360_ventiq — VentIQ domain component (SENSE360-CANONICALISATION-001
// PR 11)
// ============================================================================
// Glue only: feeds and publishes the canonical VentIQ ventilation engine
// singleton (sense360::ventiq::global_engine(), which embeds the canonical
// AirIQ engine for pollutant truth — thresholds are never duplicated here).
// The ventilation model (shower detection, clearing, mould risk, demand,
// module health) lives in the natively tested engine header. See
// docs/architecture/sense360-airiq-ventiq-component-plan.md.
//
// Module health comes from real SGP41 freshness evidence only; the
// RoomIQ-owned humidity input NEVER participates. The manual-action buttons
// stay YAML engine-action lambdas re-evaluating through the framework's
// bridge script. Output entity pointers are optional so partial
// compositions stay valid.
// ============================================================================

#include "esphome/components/binary_sensor/binary_sensor.h"
#include "esphome/components/number/number.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/switch/switch.h"
#include "esphome/components/text_sensor/text_sensor.h"
#include "esphome/components/sense360/ventiq_engine.h"
#include "esphome/core/component.h"

namespace esphome {
namespace sense360_ventiq {

class Sense360VentIQ : public Component {
 public:
  void set_humidity_source(sensor::Sensor *s) { humidity_source_ = s; }
  void set_temperature_source(sensor::Sensor *s) { temperature_source_ = s; }
  void set_voc_source(sensor::Sensor *s) { voc_source_ = s; }
  void set_nox_source(sensor::Sensor *s) { nox_source_ = s; }
  void set_shower_threshold_number(number::Number *n) { shower_threshold_number_ = n; }
  void set_clearing_number(number::Number *n) { clearing_number_ = n; }
  void set_mould_threshold_number(number::Number *n) { mould_threshold_number_ = n; }
  void set_shower_detection_switch(switch_::Switch *s) { shower_detection_switch_ = s; }
  void set_module_status_text_sensor(text_sensor::TextSensor *t) { module_status_text_sensor_ = t; }

  void set_expected(bool voc, bool nox) {
    expected_voc_ = voc;
    expected_nox_ = nox;
  }
  void set_windows(uint32_t humidity_warmup, uint32_t humidity_stale,
                   uint32_t temperature_warmup, uint32_t temperature_stale,
                   uint32_t voc_warmup, uint32_t voc_stale, uint32_t nox_warmup,
                   uint32_t nox_stale) {
    humidity_warmup_ms_ = humidity_warmup;
    humidity_stale_ms_ = humidity_stale;
    temperature_warmup_ms_ = temperature_warmup;
    temperature_stale_ms_ = temperature_stale;
    voc_warmup_ms_ = voc_warmup;
    voc_stale_ms_ = voc_stale;
    nox_warmup_ms_ = nox_warmup;
    nox_stale_ms_ = nox_stale;
  }
  void set_heuristics(float shower_rate_threshold, float shower_end_delta,
                      float shower_max_minutes, float mould_duration_minutes,
                      float humidity_high, float humidity_hysteresis) {
    shower_rate_threshold_ = shower_rate_threshold;
    shower_end_delta_ = shower_end_delta;
    shower_max_minutes_ = shower_max_minutes;
    mould_duration_minutes_ = mould_duration_minutes;
    humidity_high_ = humidity_high;
    humidity_hysteresis_ = humidity_hysteresis;
  }

  // --- output entities (platform-registered; nullptr = not composed) ---
  void set_voc_sensor(sensor::Sensor *s) { voc_sensor_ = s; }
  void set_nox_sensor(sensor::Sensor *s) { nox_sensor_ = s; }
  void set_air_quality_text_sensor(text_sensor::TextSensor *t) { air_quality_text_sensor_ = t; }
  void set_recommendation_text_sensor(text_sensor::TextSensor *t) {
    recommendation_text_sensor_ = t;
  }
  void set_reason_text_sensor(text_sensor::TextSensor *t) { reason_text_sensor_ = t; }
  void set_state_detail_text_sensor(text_sensor::TextSensor *t) { state_detail_text_sensor_ = t; }
  void set_ventilation_needed_binary_sensor(binary_sensor::BinarySensor *b) {
    ventilation_needed_binary_sensor_ = b;
  }
  void set_shower_binary_sensor(binary_sensor::BinarySensor *b) { shower_binary_sensor_ = b; }
  void set_mould_risk_binary_sensor(binary_sensor::BinarySensor *b) {
    mould_risk_binary_sensor_ = b;
  }

  void setup() override;
  void dump_config() override;
  float get_setup_priority() const override;

  // The single evaluation owner. Public for the framework's same-id bridge
  // script (the manual-action buttons' documented re-evaluation hook).
  void evaluate();

 protected:
  void publish_changed_(text_sensor::TextSensor *target, const std::string &value);
  void publish_changed_(binary_sensor::BinarySensor *target, bool value);

  sensor::Sensor *humidity_source_{nullptr};
  sensor::Sensor *temperature_source_{nullptr};
  sensor::Sensor *voc_source_{nullptr};
  sensor::Sensor *nox_source_{nullptr};
  number::Number *shower_threshold_number_{nullptr};
  number::Number *clearing_number_{nullptr};
  number::Number *mould_threshold_number_{nullptr};
  switch_::Switch *shower_detection_switch_{nullptr};

  sensor::Sensor *voc_sensor_{nullptr};
  sensor::Sensor *nox_sensor_{nullptr};
  text_sensor::TextSensor *air_quality_text_sensor_{nullptr};
  text_sensor::TextSensor *recommendation_text_sensor_{nullptr};
  text_sensor::TextSensor *reason_text_sensor_{nullptr};
  text_sensor::TextSensor *module_status_text_sensor_{nullptr};
  text_sensor::TextSensor *state_detail_text_sensor_{nullptr};
  binary_sensor::BinarySensor *ventilation_needed_binary_sensor_{nullptr};
  binary_sensor::BinarySensor *shower_binary_sensor_{nullptr};
  binary_sensor::BinarySensor *mould_risk_binary_sensor_{nullptr};

  bool expected_voc_{true};
  bool expected_nox_{true};
  uint32_t humidity_warmup_ms_{90000};
  uint32_t humidity_stale_ms_{90000};
  uint32_t temperature_warmup_ms_{90000};
  uint32_t temperature_stale_ms_{90000};
  uint32_t voc_warmup_ms_{120000};
  uint32_t voc_stale_ms_{60000};
  uint32_t nox_warmup_ms_{120000};
  uint32_t nox_stale_ms_{60000};
  float shower_rate_threshold_{5};
  float shower_end_delta_{10};
  float shower_max_minutes_{60};
  float mould_duration_minutes_{30};
  float humidity_high_{60};
  float humidity_hysteresis_{2};
};

}  // namespace sense360_ventiq
}  // namespace esphome

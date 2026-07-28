#pragma once
// ============================================================================
// sense360_roomiq — RoomIQ domain component (SENSE360-CANONICALISATION-001
// PR 09)
// ============================================================================
// Glue only: this component feeds and publishes the canonical RoomIQ engine
// singleton (sense360::roomiq::global_engine() — the SAME instance the LED
// framework reads; see docs/architecture/sense360-roomiq-component-plan.md,
// "singleton contract"). The environmental model — compensation,
// psychrometric humidity, freshness, calibration clamping, classification —
// lives in the natively tested engine headers and is not restated here.
//
// Publication follows the pre-component single-owner contract exactly: one
// evaluate path owns every engine exchange; outputs publish on change only;
// a stale channel publishes NAN (never a frozen reading). Output entity
// pointers are optional (nullptr = not composed), so the component skeleton
// compiles before the platform slices land and partial compositions stay
// valid.
// ============================================================================

#include "esphome/components/number/number.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/text_sensor/text_sensor.h"
#include "esphome/components/sense360/roomiq_engine.h"
#include "esphome/core/component.h"

namespace esphome {
namespace sense360_roomiq {

class Sense360RoomIQ : public Component {
 public:
  // --- raw input sources (composed by the board package) ---
  void set_temperature_source(sensor::Sensor *s) { temperature_source_ = s; }
  void set_humidity_source(sensor::Sensor *s) { humidity_source_ = s; }
  void set_illuminance_source(sensor::Sensor *s) { illuminance_source_ = s; }

  // --- customer calibration controls (persisted template numbers in YAML;
  //     entity ids and NVS restore identity are protected contracts) ---
  void set_temperature_offset_number(number::Number *n) { temperature_offset_number_ = n; }
  void set_humidity_offset_number(number::Number *n) { humidity_offset_number_ = n; }
  void set_illuminance_scale_number(number::Number *n) { illuminance_scale_number_ = n; }

  // --- configuration (defaults equal the pre-component substitutions) ---
  void set_climate_windows(uint32_t warmup_ms, uint32_t stale_ms) {
    climate_warmup_ms_ = warmup_ms;
    climate_stale_ms_ = stale_ms;
  }
  void set_illuminance_windows(uint32_t warmup_ms, uint32_t stale_ms) {
    lux_warmup_ms_ = warmup_ms;
    lux_stale_ms_ = stale_ms;
  }
  void set_climate_pair_skew(uint32_t skew_ms) { climate_pair_skew_ms_ = skew_ms; }
  void set_temperature_bands(float cold_c, float cool_c, float warm_c, float hot_c,
                             float hysteresis_c) {
    temp_cold_c_ = cold_c;
    temp_cool_c_ = cool_c;
    temp_warm_c_ = warm_c;
    temp_hot_c_ = hot_c;
    temp_hysteresis_c_ = hysteresis_c;
  }
  void set_humidity_bands(float dry_pct, float humid_pct, float hysteresis_pct) {
    humidity_dry_pct_ = dry_pct;
    humidity_humid_pct_ = humid_pct;
    humidity_hysteresis_pct_ = hysteresis_pct;
  }
  void set_brightness_bands(float dim_lx, float normal_lx, float bright_lx,
                            float very_bright_lx, float hysteresis_pct) {
    lux_dim_lx_ = dim_lx;
    lux_normal_lx_ = normal_lx;
    lux_bright_lx_ = bright_lx;
    lux_very_bright_lx_ = very_bright_lx;
    brightness_hysteresis_pct_ = hysteresis_pct;
  }
  void set_calibration_schema_version(int version) { calibration_schema_version_ = version; }

  // --- output entities (registered by the platform modules; nullptr = not
  //     composed) ---
  void set_temperature_sensor(sensor::Sensor *s) { temperature_sensor_ = s; }
  void set_humidity_sensor(sensor::Sensor *s) { humidity_sensor_ = s; }
  void set_illuminance_sensor(sensor::Sensor *s) { illuminance_sensor_ = s; }
  void set_factory_temperature_sensor(sensor::Sensor *s) { factory_temperature_sensor_ = s; }
  void set_factory_humidity_sensor(sensor::Sensor *s) { factory_humidity_sensor_ = s; }
  void set_comfort_text_sensor(text_sensor::TextSensor *t) { comfort_text_sensor_ = t; }
  void set_environment_text_sensor(text_sensor::TextSensor *t) { environment_text_sensor_ = t; }
  void set_brightness_text_sensor(text_sensor::TextSensor *t) { brightness_text_sensor_ = t; }
  void set_module_status_text_sensor(text_sensor::TextSensor *t) { module_status_text_sensor_ = t; }
  void set_environment_detail_text_sensor(text_sensor::TextSensor *t) {
    environment_detail_text_sensor_ = t;
  }
  void set_calibration_state_text_sensor(text_sensor::TextSensor *t) {
    calibration_state_text_sensor_ = t;
  }
  void set_climate_profile_text_sensor(text_sensor::TextSensor *t) {
    climate_profile_text_sensor_ = t;
  }

  void setup() override;
  void dump_config() override;
  float get_setup_priority() const override;

  // The single evaluation owner (public so YAML-side triggers retained
  // during the migration window can re-evaluate through the component
  // rather than around it).
  void evaluate();

 protected:
  void publish_changed_(sensor::Sensor *target, float value);
  void publish_changed_(text_sensor::TextSensor *target, const std::string &value);

  sensor::Sensor *temperature_source_{nullptr};
  sensor::Sensor *humidity_source_{nullptr};
  sensor::Sensor *illuminance_source_{nullptr};
  number::Number *temperature_offset_number_{nullptr};
  number::Number *humidity_offset_number_{nullptr};
  number::Number *illuminance_scale_number_{nullptr};

  sensor::Sensor *temperature_sensor_{nullptr};
  sensor::Sensor *humidity_sensor_{nullptr};
  sensor::Sensor *illuminance_sensor_{nullptr};
  sensor::Sensor *factory_temperature_sensor_{nullptr};
  sensor::Sensor *factory_humidity_sensor_{nullptr};
  text_sensor::TextSensor *comfort_text_sensor_{nullptr};
  text_sensor::TextSensor *environment_text_sensor_{nullptr};
  text_sensor::TextSensor *brightness_text_sensor_{nullptr};
  text_sensor::TextSensor *module_status_text_sensor_{nullptr};
  text_sensor::TextSensor *environment_detail_text_sensor_{nullptr};
  text_sensor::TextSensor *calibration_state_text_sensor_{nullptr};
  text_sensor::TextSensor *climate_profile_text_sensor_{nullptr};

  uint32_t climate_warmup_ms_{60000};
  uint32_t climate_stale_ms_{90000};
  uint32_t lux_warmup_ms_{30000};
  uint32_t lux_stale_ms_{60000};
  uint32_t climate_pair_skew_ms_{5000};
  float temp_cold_c_{16.0f};
  float temp_cool_c_{18.0f};
  float temp_warm_c_{24.0f};
  float temp_hot_c_{27.0f};
  float temp_hysteresis_c_{0.3f};
  float humidity_dry_pct_{30.0f};
  float humidity_humid_pct_{60.0f};
  float humidity_hysteresis_pct_{2.0f};
  float lux_dim_lx_{10.0f};
  float lux_normal_lx_{50.0f};
  float lux_bright_lx_{300.0f};
  float lux_very_bright_lx_{1000.0f};
  float brightness_hysteresis_pct_{20.0f};
  int calibration_schema_version_{2};
};

}  // namespace sense360_roomiq
}  // namespace esphome

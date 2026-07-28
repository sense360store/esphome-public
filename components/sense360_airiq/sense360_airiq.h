#pragma once
// ============================================================================
// sense360_airiq — AirIQ domain component (SENSE360-CANONICALISATION-001
// PR 11)
// ============================================================================
// Glue only: feeds and publishes the canonical AirIQ engine singleton
// (sense360::airiq::global_engine() — the same instance the blower framework
// reads for ventilation demand and the VentIQ engine embeds for pollutant
// truth). The pollutant model lives in the natively tested engine header.
// See docs/architecture/sense360-airiq-ventiq-component-plan.md.
//
// Publication contract (unchanged from the YAML glue): fresh engine values
// publish from the input callbacks; a channel that is no longer fresh
// publishes NAN — a stale reading is never left standing as if it were
// live. The PM channels are externally fed by the opt-in SPS30 overlay
// through the framework's bridge script; this component owns their
// NAN-on-stale half only. Output entity pointers are optional so partial
// compositions stay valid.
// ============================================================================

#include "esphome/components/sensor/sensor.h"
#include "esphome/components/text_sensor/text_sensor.h"
#include "esphome/components/sense360/airiq_engine.h"
#include "esphome/core/component.h"

namespace esphome {
namespace sense360_airiq {

class Sense360AirIQ : public Component {
 public:
  void set_co2_source(sensor::Sensor *s) { co2_source_ = s; }
  void set_voc_source(sensor::Sensor *s) { voc_source_ = s; }
  void set_nox_source(sensor::Sensor *s) { nox_source_ = s; }
  void set_hcho_source(sensor::Sensor *s) { hcho_source_ = s; }
  void set_module_status_text_sensor(text_sensor::TextSensor *t) { module_status_text_sensor_ = t; }
  void set_legacy_air_quality_text_sensor(text_sensor::TextSensor *t) {
    legacy_air_quality_text_sensor_ = t;
  }

  void set_expected(bool co2, bool voc, bool nox, bool pm, bool hcho, bool o3) {
    expected_co2_ = co2;
    expected_voc_ = voc;
    expected_nox_ = nox;
    expected_pm_ = pm;
    expected_hcho_ = hcho;
    expected_o3_ = o3;
  }
  void set_windows(uint32_t co2_warmup, uint32_t co2_stale, uint32_t voc_warmup,
                   uint32_t voc_stale, uint32_t nox_warmup, uint32_t nox_stale,
                   uint32_t pm_warmup, uint32_t pm_stale) {
    co2_warmup_ms_ = co2_warmup;
    co2_stale_ms_ = co2_stale;
    voc_warmup_ms_ = voc_warmup;
    voc_stale_ms_ = voc_stale;
    nox_warmup_ms_ = nox_warmup;
    nox_stale_ms_ = nox_stale;
    pm_warmup_ms_ = pm_warmup;
    pm_stale_ms_ = pm_stale;
  }
  void set_co2_thresholds(float fair, float poor, float very_poor, float hysteresis) {
    co2_thresholds_ = {fair, poor, very_poor, hysteresis};
  }
  void set_voc_thresholds(float fair, float poor, float very_poor, float hysteresis) {
    voc_thresholds_ = {fair, poor, very_poor, hysteresis};
  }
  void set_nox_thresholds(float fair, float poor, float very_poor, float hysteresis) {
    nox_thresholds_ = {fair, poor, very_poor, hysteresis};
  }
  void set_pm25_thresholds(float fair, float poor, float very_poor, float hysteresis) {
    pm25_thresholds_ = {fair, poor, very_poor, hysteresis};
  }

  // --- output entities (platform-registered; nullptr = not composed) ---
  void set_co2_sensor(sensor::Sensor *s) { co2_sensor_ = s; }
  void set_voc_sensor(sensor::Sensor *s) { voc_sensor_ = s; }
  void set_nox_sensor(sensor::Sensor *s) { nox_sensor_ = s; }
  void set_hcho_sensor(sensor::Sensor *s) { hcho_sensor_ = s; }
  void set_pm2_5_sensor(sensor::Sensor *s) { pm2_5_sensor_ = s; }
  void set_pm1_sensor(sensor::Sensor *s) { pm1_sensor_ = s; }
  void set_pm4_sensor(sensor::Sensor *s) { pm4_sensor_ = s; }
  void set_pm10_sensor(sensor::Sensor *s) { pm10_sensor_ = s; }
  void set_air_quality_text_sensor(text_sensor::TextSensor *t) { air_quality_text_sensor_ = t; }
  void set_recommendation_text_sensor(text_sensor::TextSensor *t) {
    recommendation_text_sensor_ = t;
  }
  void set_state_detail_text_sensor(text_sensor::TextSensor *t) { state_detail_text_sensor_ = t; }
  void set_recommendation_reason_text_sensor(text_sensor::TextSensor *t) {
    recommendation_reason_text_sensor_ = t;
  }

  void setup() override;
  void dump_config() override;
  float get_setup_priority() const override;

  // The single evaluation owner. Public for the framework's same-id bridge
  // script (the SPS30 overlay's documented re-evaluation hook).
  void evaluate();

 protected:
  struct Thresholds {
    float fair;
    float poor;
    float very_poor;
    float hysteresis;
  };

  void publish_nan_if_stale_(sense360::airiq::Pollutant pollutant, sensor::Sensor *target);
  void publish_changed_(text_sensor::TextSensor *target, const std::string &value);

  sensor::Sensor *co2_source_{nullptr};
  sensor::Sensor *voc_source_{nullptr};
  sensor::Sensor *nox_source_{nullptr};
  sensor::Sensor *hcho_source_{nullptr};

  sensor::Sensor *co2_sensor_{nullptr};
  sensor::Sensor *voc_sensor_{nullptr};
  sensor::Sensor *nox_sensor_{nullptr};
  sensor::Sensor *hcho_sensor_{nullptr};
  sensor::Sensor *pm2_5_sensor_{nullptr};
  sensor::Sensor *pm1_sensor_{nullptr};
  sensor::Sensor *pm4_sensor_{nullptr};
  sensor::Sensor *pm10_sensor_{nullptr};
  text_sensor::TextSensor *air_quality_text_sensor_{nullptr};
  text_sensor::TextSensor *legacy_air_quality_text_sensor_{nullptr};
  text_sensor::TextSensor *recommendation_text_sensor_{nullptr};
  text_sensor::TextSensor *module_status_text_sensor_{nullptr};
  text_sensor::TextSensor *state_detail_text_sensor_{nullptr};
  text_sensor::TextSensor *recommendation_reason_text_sensor_{nullptr};

  bool expected_co2_{true};
  bool expected_voc_{true};
  bool expected_nox_{true};
  bool expected_pm_{false};
  bool expected_hcho_{true};
  bool expected_o3_{false};
  uint32_t co2_warmup_ms_{60000};
  uint32_t co2_stale_ms_{180000};
  uint32_t voc_warmup_ms_{60000};
  uint32_t voc_stale_ms_{180000};
  uint32_t nox_warmup_ms_{60000};
  uint32_t nox_stale_ms_{180000};
  uint32_t pm_warmup_ms_{60000};
  uint32_t pm_stale_ms_{180000};
  Thresholds co2_thresholds_{800, 1200, 2000, 50};
  Thresholds voc_thresholds_{150, 250, 400, 10};
  Thresholds nox_thresholds_{150, 250, 400, 10};
  Thresholds pm25_thresholds_{12, 35, 55, 2};
};

}  // namespace sense360_airiq
}  // namespace esphome

#include "sense360_airiq.h"

#include <cmath>

#include "esphome/core/hal.h"
#include "esphome/core/log.h"

namespace esphome {
namespace sense360_airiq {

static const char *const TAG = "sense360_airiq";

// One evaluation clock, one publish owner — the cadence the YAML interval
// carried.
static constexpr uint32_t EVALUATE_INTERVAL_MS = 10000;

float Sense360AirIQ::get_setup_priority() const { return setup_priority::DATA; }

void Sense360AirIQ::setup() {
  using namespace sense360::airiq;
  auto &engine = global_engine();
  engine.begin(millis());

  // The freshness signal is the real update callback: each fitted base
  // sensor feeds the engine, re-evaluates, and publishes the engine's
  // (calibrated) value to the canonical entity while the sample is valid.
  if (this->co2_source_ != nullptr) {
    this->co2_source_->add_on_state_callback([this](float x) {
      auto &e = sense360::airiq::global_engine();
      e.input_co2(millis(), x);
      this->evaluate();
      if (!std::isnan(x) && this->co2_sensor_ != nullptr)
        this->co2_sensor_->publish_state(e.co2());
    });
  }
  if (this->voc_source_ != nullptr) {
    this->voc_source_->add_on_state_callback([this](float x) {
      auto &e = sense360::airiq::global_engine();
      e.input_voc(millis(), x);
      this->evaluate();
      if (!std::isnan(x) && this->voc_sensor_ != nullptr)
        this->voc_sensor_->publish_state(e.voc());
    });
  }
  if (this->nox_source_ != nullptr) {
    this->nox_source_->add_on_state_callback([this](float x) {
      auto &e = sense360::airiq::global_engine();
      e.input_nox(millis(), x);
      this->evaluate();
      if (!std::isnan(x) && this->nox_sensor_ != nullptr)
        this->nox_sensor_->publish_state(e.nox());
    });
  }
  if (this->hcho_source_ != nullptr) {
    this->hcho_source_->add_on_state_callback([this](float x) {
      auto &e = sense360::airiq::global_engine();
      e.input_hcho(millis(), x);
      this->evaluate();
      if (!std::isnan(x) && this->hcho_sensor_ != nullptr)
        this->hcho_sensor_->publish_state(e.hcho());
    });
  }

  this->set_interval("s360_airiq_evaluate", EVALUATE_INTERVAL_MS,
                     [this]() { this->evaluate(); });
  this->evaluate();
}

void Sense360AirIQ::publish_nan_if_stale_(sense360::airiq::Pollutant pollutant,
                                          sensor::Sensor *target) {
  if (target == nullptr)
    return;
  if (!sense360::airiq::global_engine().pollutant_fresh(pollutant) &&
      !std::isnan(target->state)) {
    target->publish_state(NAN);
  }
}

void Sense360AirIQ::publish_changed_(text_sensor::TextSensor *target,
                                     const std::string &value) {
  if (target == nullptr)
    return;
  if (target->state != value)
    target->publish_state(value);
}

void Sense360AirIQ::evaluate() {
  using namespace sense360::airiq;
  auto &engine = global_engine();
  const uint32_t now = millis();

  // Composition (expected-sensor membership; NO Base/Pro axis).
  engine.set_expected(POLLUTANT_CO2, this->expected_co2_);
  engine.set_expected(POLLUTANT_VOC, this->expected_voc_);
  engine.set_expected(POLLUTANT_NOX, this->expected_nox_);
  engine.set_expected(POLLUTANT_PM25, this->expected_pm_);
  engine.set_expected(POLLUTANT_HCHO, this->expected_hcho_);
  engine.set_expected(POLLUTANT_O3, this->expected_o3_);

  // Per-sensor freshness windows (provisional engineering values).
  engine.set_warmup_ms(POLLUTANT_CO2, this->co2_warmup_ms_);
  engine.set_stale_ms(POLLUTANT_CO2, this->co2_stale_ms_);
  engine.set_warmup_ms(POLLUTANT_VOC, this->voc_warmup_ms_);
  engine.set_stale_ms(POLLUTANT_VOC, this->voc_stale_ms_);
  engine.set_warmup_ms(POLLUTANT_NOX, this->nox_warmup_ms_);
  engine.set_stale_ms(POLLUTANT_NOX, this->nox_stale_ms_);
  engine.set_warmup_ms(POLLUTANT_PM25, this->pm_warmup_ms_);
  engine.set_stale_ms(POLLUTANT_PM25, this->pm_stale_ms_);

  // Provisional severity thresholds (centralised contract).
  engine.set_thresholds(POLLUTANT_CO2, this->co2_thresholds_.fair,
                        this->co2_thresholds_.poor, this->co2_thresholds_.very_poor);
  engine.set_hysteresis(POLLUTANT_CO2, this->co2_thresholds_.hysteresis);
  engine.set_thresholds(POLLUTANT_VOC, this->voc_thresholds_.fair,
                        this->voc_thresholds_.poor, this->voc_thresholds_.very_poor);
  engine.set_hysteresis(POLLUTANT_VOC, this->voc_thresholds_.hysteresis);
  engine.set_thresholds(POLLUTANT_NOX, this->nox_thresholds_.fair,
                        this->nox_thresholds_.poor, this->nox_thresholds_.very_poor);
  engine.set_hysteresis(POLLUTANT_NOX, this->nox_thresholds_.hysteresis);
  engine.set_thresholds(POLLUTANT_PM25, this->pm25_thresholds_.fair,
                        this->pm25_thresholds_.poor, this->pm25_thresholds_.very_poor);
  engine.set_hysteresis(POLLUTANT_PM25, this->pm25_thresholds_.hysteresis);

  engine.evaluate(now);

  // Honest numeric outputs: when a channel is no longer fresh its canonical
  // entity goes unknown — a stale reading is never left standing.
  this->publish_nan_if_stale_(POLLUTANT_CO2, this->co2_sensor_);
  this->publish_nan_if_stale_(POLLUTANT_VOC, this->voc_sensor_);
  this->publish_nan_if_stale_(POLLUTANT_NOX, this->nox_sensor_);
  this->publish_nan_if_stale_(POLLUTANT_HCHO, this->hcho_sensor_);
  this->publish_nan_if_stale_(POLLUTANT_PM25, this->pm2_5_sensor_);
  this->publish_nan_if_stale_(POLLUTANT_PM25, this->pm1_sensor_);
  this->publish_nan_if_stale_(POLLUTANT_PM25, this->pm4_sensor_);
  this->publish_nan_if_stale_(POLLUTANT_PM25, this->pm10_sensor_);

  // Customer state outputs (publish on change only). The legacy entity
  // carries the same canonical headline (documented semantic upgrade).
  const std::string headline = air_quality_to_string(engine.air_quality());
  this->publish_changed_(this->air_quality_text_sensor_, headline);
  this->publish_changed_(this->legacy_air_quality_text_sensor_, headline);
  this->publish_changed_(this->recommendation_text_sensor_,
                         recommendation_to_string(engine.recommendation()));

  // Module health — real freshness evidence driving the Core-Framework
  // reserved runtime vocabulary.
  this->publish_changed_(this->module_status_text_sensor_,
                         health_to_string(engine.health()));

  // Diagnostics (publish on change only).
  if (this->state_detail_text_sensor_ != nullptr) {
    char buffer[192];
    snprintf(buffer, sizeof(buffer), "co2=%s voc=%s nox=%s hcho=%s pm2.5=%s",
             severity_to_string(engine.severity(POLLUTANT_CO2)),
             severity_to_string(engine.severity(POLLUTANT_VOC)),
             severity_to_string(engine.severity(POLLUTANT_NOX)),
             severity_to_string(engine.severity(POLLUTANT_HCHO)),
             severity_to_string(engine.severity(POLLUTANT_PM25)));
    this->publish_changed_(this->state_detail_text_sensor_, std::string(buffer));
  }
  if (this->recommendation_reason_text_sensor_ != nullptr) {
    char buffer[160];
    if (engine.worst_pollutant() < POLLUTANT_COUNT) {
      snprintf(buffer, sizeof(buffer), "worst pollutant: %s (%s) -> %s",
               pollutant_to_string(engine.worst_pollutant()),
               severity_to_string(engine.severity(engine.worst_pollutant())),
               recommendation_to_string(engine.recommendation()));
    } else {
      snprintf(buffer, sizeof(buffer), "no pollutant above Good -> %s",
               recommendation_to_string(engine.recommendation()));
    }
    this->publish_changed_(this->recommendation_reason_text_sensor_,
                           std::string(buffer));
  }
}

void Sense360AirIQ::dump_config() {
  ESP_LOGCONFIG(TAG, "Sense360 AirIQ (glue over the canonical engine "
                     "singleton; model logic lives in "
                     "components/sense360/airiq_engine.h)");
  ESP_LOGCONFIG(TAG,
                "  Expected: co2=%s voc=%s nox=%s pm=%s hcho=%s o3=%s "
                "(composition facts, never hardware autodetection)",
                YESNO(this->expected_co2_), YESNO(this->expected_voc_),
                YESNO(this->expected_nox_), YESNO(this->expected_pm_),
                YESNO(this->expected_hcho_), YESNO(this->expected_o3_));
}

}  // namespace sense360_airiq
}  // namespace esphome

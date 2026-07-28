#include "sense360_ventiq.h"

#include <cmath>

#include "esphome/core/hal.h"
#include "esphome/core/log.h"

namespace esphome {
namespace sense360_ventiq {

static const char *const TAG = "sense360_ventiq";

static constexpr uint32_t EVALUATE_INTERVAL_MS = 10000;

float Sense360VentIQ::get_setup_priority() const { return setup_priority::DATA; }

void Sense360VentIQ::setup() {
  using namespace sense360::ventiq;
  auto &engine = global_engine();
  engine.begin(millis());

  // The freshness signal is the real update callback. Humidity and
  // temperature are the RoomIQ CANONICAL calibrated entities (an invalid
  // upstream sample never refreshes this engine's channel either); VOC and
  // NOx are the board's SGP41, whose canonical publication this component
  // owns (fresh engine value on input).
  if (this->humidity_source_ != nullptr) {
    this->humidity_source_->add_on_state_callback([this](float x) {
      sense360::ventiq::global_engine().input_humidity(millis(), x);
      this->evaluate();
    });
  }
  if (this->temperature_source_ != nullptr) {
    this->temperature_source_->add_on_state_callback([this](float x) {
      sense360::ventiq::global_engine().input_temperature(millis(), x);
      this->evaluate();
    });
  }
  if (this->voc_source_ != nullptr) {
    this->voc_source_->add_on_state_callback([this](float x) {
      auto &e = sense360::ventiq::global_engine();
      e.input_voc(millis(), x);
      this->evaluate();
      if (!std::isnan(x) && this->voc_sensor_ != nullptr)
        this->voc_sensor_->publish_state(e.voc());
    });
  }
  if (this->nox_source_ != nullptr) {
    this->nox_source_->add_on_state_callback([this](float x) {
      auto &e = sense360::ventiq::global_engine();
      e.input_nox(millis(), x);
      this->evaluate();
      if (!std::isnan(x) && this->nox_sensor_ != nullptr)
        this->nox_sensor_->publish_state(e.nox());
    });
  }

  // Control changes re-evaluate immediately (the controls stay persisted
  // template entities in YAML; their values are read in evaluate()).
  for (number::Number *n : {this->shower_threshold_number_, this->clearing_number_,
                            this->mould_threshold_number_}) {
    if (n != nullptr) {
      n->add_on_state_callback([this](float) { this->evaluate(); });
    }
  }
  if (this->shower_detection_switch_ != nullptr) {
    this->shower_detection_switch_->add_on_state_callback(
        [this](bool) { this->evaluate(); });
  }

  this->set_interval("s360_ventiq_evaluate", EVALUATE_INTERVAL_MS,
                     [this]() { this->evaluate(); });
  this->evaluate();
}

void Sense360VentIQ::publish_changed_(text_sensor::TextSensor *target,
                                      const std::string &value) {
  if (target == nullptr)
    return;
  if (target->state != value)
    target->publish_state(value);
}

void Sense360VentIQ::publish_changed_(binary_sensor::BinarySensor *target, bool value) {
  if (target == nullptr)
    return;
  if (!target->has_state() || target->state != value)
    target->publish_state(value);
}

void Sense360VentIQ::evaluate() {
  using namespace sense360::ventiq;
  auto &engine = global_engine();
  const uint32_t now = millis();

  // Composition (expected-channel membership; NO Base/Pro axis).
  engine.set_pollutant_expected(sense360::airiq::POLLUTANT_VOC, this->expected_voc_);
  engine.set_pollutant_expected(sense360::airiq::POLLUTANT_NOX, this->expected_nox_);

  // Per-channel freshness windows (provisional engineering values).
  engine.set_humidity_warmup_ms(this->humidity_warmup_ms_);
  engine.set_humidity_stale_ms(this->humidity_stale_ms_);
  engine.set_temperature_warmup_ms(this->temperature_warmup_ms_);
  engine.set_temperature_stale_ms(this->temperature_stale_ms_);
  engine.set_voc_warmup_ms(this->voc_warmup_ms_);
  engine.set_voc_stale_ms(this->voc_stale_ms_);
  engine.set_nox_warmup_ms(this->nox_warmup_ms_);
  engine.set_nox_stale_ms(this->nox_stale_ms_);

  // Ventilation heuristics: the preserved customer controls are genuinely
  // applied; invalid/unrestored number states are ignored by the engine's
  // setters (defaults hold).
  if (this->shower_threshold_number_ != nullptr)
    engine.set_shower_threshold_pct(this->shower_threshold_number_->state);
  if (this->clearing_number_ != nullptr)
    engine.set_clearing_minutes(this->clearing_number_->state);
  if (this->mould_threshold_number_ != nullptr)
    engine.set_mould_threshold_pct(this->mould_threshold_number_->state);
  engine.set_shower_rate_threshold(this->shower_rate_threshold_);
  engine.set_shower_end_delta_pct(this->shower_end_delta_);
  engine.set_shower_max_minutes(this->shower_max_minutes_);
  engine.set_mould_duration_minutes(this->mould_duration_minutes_);
  engine.set_humidity_high_pct(this->humidity_high_);
  engine.set_humidity_hysteresis_pct(this->humidity_hysteresis_);
  if (this->shower_detection_switch_ != nullptr)
    engine.set_shower_detection_enabled(this->shower_detection_switch_->state);

  engine.evaluate(now);

  // Honest numeric outputs: a stale channel goes unknown — never a frozen
  // reading.
  if (this->voc_sensor_ != nullptr && !engine.voc_fresh() &&
      !std::isnan(this->voc_sensor_->state)) {
    this->voc_sensor_->publish_state(NAN);
  }
  if (this->nox_sensor_ != nullptr && !engine.nox_fresh() &&
      !std::isnan(this->nox_sensor_->state)) {
    this->nox_sensor_->publish_state(NAN);
  }

  // Customer state outputs (publish on change only).
  this->publish_changed_(this->air_quality_text_sensor_,
                         sense360::airiq::air_quality_to_string(engine.air_quality()));
  this->publish_changed_(this->recommendation_text_sensor_,
                         demand_to_string(engine.demand()));
  this->publish_changed_(this->reason_text_sensor_, reason_to_string(engine.reason()));
  this->publish_changed_(this->ventilation_needed_binary_sensor_,
                         engine.ventilation_needed());
  this->publish_changed_(this->shower_binary_sensor_, engine.shower_active());
  this->publish_changed_(this->mould_risk_binary_sensor_, engine.mould_warning());

  // Module health — real SGP41 freshness evidence driving the
  // Core-Framework reserved runtime vocabulary. The RoomIQ-owned humidity
  // input NEVER participates.
  this->publish_changed_(this->module_status_text_sensor_,
                         sense360::airiq::health_to_string(engine.health()));

  // Diagnostics (publish on change only).
  if (this->state_detail_text_sensor_ != nullptr) {
    char buffer[200];
    snprintf(buffer, sizeof(buffer),
             "demand=%s reason=%s shower=%s clearing=%.1fmin "
             "mould=%d humidity=%s voc=%s nox=%s",
             demand_to_string(engine.demand()), reason_to_string(engine.reason()),
             engine.shower_active() ? "yes" : "no",
             engine.clearing_minutes_remaining(), engine.mould_risk(),
             engine.humidity_fresh() ? "fresh" : "not-fresh",
             engine.voc_fresh() ? "fresh" : "not-fresh",
             engine.nox_fresh() ? "fresh" : "not-fresh");
    this->publish_changed_(this->state_detail_text_sensor_, std::string(buffer));
  }
}

void Sense360VentIQ::dump_config() {
  ESP_LOGCONFIG(TAG, "Sense360 VentIQ (glue over the canonical ventilation "
                     "engine singleton; model logic lives in "
                     "components/sense360/ventiq_engine.h)");
  ESP_LOGCONFIG(TAG,
                "  Expected channels: voc=%s nox=%s (composition facts; the "
                "RoomIQ humidity input never drives module health)",
                YESNO(this->expected_voc_), YESNO(this->expected_nox_));
}

}  // namespace sense360_ventiq
}  // namespace esphome

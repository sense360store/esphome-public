#include "sense360_roomiq.h"

#include <cmath>

#include "esphome/core/hal.h"
#include "esphome/core/log.h"

namespace esphome {
namespace sense360_roomiq {

static const char *const TAG = "sense360_roomiq";

// One evaluation clock, one publish owner — the exact contract the YAML
// evaluate script carried (docs/architecture/sense360-roomiq-component-plan.md).
static constexpr uint32_t EVALUATE_INTERVAL_MS = 5000;

float Sense360RoomIQ::get_setup_priority() const {
  // After hardware sensors and number entities have set up (and restored
  // their persisted values), before late boot hooks — matching the
  // pre-component ordering (HARDWARE components first, engine begin later).
  return setup_priority::DATA;
}

void Sense360RoomIQ::setup() {
  auto &engine = sense360::roomiq::global_engine();
  engine.begin(millis());

  // The freshness signal is the real update callback: each raw sample feeds
  // the engine and re-evaluates immediately, so either SHT45 callback order
  // publishes the right values (a temperature sample completing a humidity
  // pair publishes humidity too).
  if (this->temperature_source_ != nullptr) {
    this->temperature_source_->add_on_state_callback([this](float x) {
      sense360::roomiq::global_engine().input_temperature(millis(), x);
      this->evaluate();
    });
  }
  if (this->humidity_source_ != nullptr) {
    this->humidity_source_->add_on_state_callback([this](float x) {
      sense360::roomiq::global_engine().input_humidity(millis(), x);
      this->evaluate();
    });
  }
  if (this->illuminance_source_ != nullptr) {
    this->illuminance_source_->add_on_state_callback([this](float x) {
      sense360::roomiq::global_engine().input_lux(millis(), x);
      this->evaluate();
    });
  }

  // A calibration change recalculates immediately from the latest raw pair
  // while it is still fresh (the temperature offset legitimately moves
  // humidity too: relative humidity is recomputed at the corrected
  // temperature, preserving the measured vapour pressure).
  for (number::Number *n : {this->temperature_offset_number_,
                            this->humidity_offset_number_,
                            this->illuminance_scale_number_}) {
    if (n != nullptr) {
      n->add_on_state_callback([this](float) { this->evaluate(); });
    }
  }

  // Compile-time static: which built-in board climate profile is compiled
  // in, and exactly what it proves (published once — the profile is
  // constant).
  if (this->climate_profile_text_sensor_ != nullptr) {
    const auto &profile = engine.climate_profile();
    char buffer[200];
    snprintf(buffer, sizeof(buffer),
             "%s (%s %s): temperature %+.2f C, humidity residual "
             "%+.2f %%RH, evidence %s (one tested board; multi-unit "
             "validation outstanding)",
             profile.id, profile.board_sku, profile.board_revision,
             profile.temperature_correction_c, profile.humidity_residual_pct,
             sense360::roomiq::climate_evidence_to_string(profile.evidence));
    this->climate_profile_text_sensor_->publish_state(buffer);
  }

  this->set_interval("s360_roomiq_evaluate", EVALUATE_INTERVAL_MS,
                     [this]() { this->evaluate(); });
  this->evaluate();
}

void Sense360RoomIQ::publish_changed_(sensor::Sensor *target, float value) {
  if (target == nullptr)
    return;
  const float current = target->state;
  const bool unchanged =
      (std::isnan(current) && std::isnan(value)) || current == value;
  if (!unchanged)
    target->publish_state(value);
}

void Sense360RoomIQ::publish_changed_(text_sensor::TextSensor *target,
                                      const std::string &value) {
  if (target == nullptr)
    return;
  if (target->state != value)
    target->publish_state(value);
}

void Sense360RoomIQ::evaluate() {
  using namespace sense360::roomiq;
  auto &engine = global_engine();
  const uint32_t now = millis();

  // Freshness windows and provisional thresholds.
  engine.set_climate_warmup_ms(this->climate_warmup_ms_);
  engine.set_climate_stale_ms(this->climate_stale_ms_);
  engine.set_lux_warmup_ms(this->lux_warmup_ms_);
  engine.set_lux_stale_ms(this->lux_stale_ms_);
  engine.set_temperature_bands(this->temp_cold_c_, this->temp_cool_c_,
                               this->temp_warm_c_, this->temp_hot_c_);
  engine.set_temperature_hysteresis(this->temp_hysteresis_c_);
  engine.set_humidity_bands(this->humidity_dry_pct_, this->humidity_humid_pct_);
  engine.set_humidity_hysteresis(this->humidity_hysteresis_pct_);
  engine.set_brightness_bands(this->lux_dim_lx_, this->lux_normal_lx_,
                              this->lux_bright_lx_, this->lux_very_bright_lx_);
  engine.set_brightness_hysteresis_pct(this->brightness_hysteresis_pct_);
  engine.set_climate_pair_skew_ms(this->climate_pair_skew_ms_);

  // Customer calibration — applied EXACTLY ONCE, inside the engine, on top
  // of the built-in board profile; the engine clamps to safe bounds and
  // treats invalid values as neutral.
  if (this->temperature_offset_number_ != nullptr)
    engine.set_temperature_offset(this->temperature_offset_number_->state);
  if (this->humidity_offset_number_ != nullptr)
    engine.set_humidity_offset(this->humidity_offset_number_->state);
  if (this->illuminance_scale_number_ != nullptr)
    engine.set_illuminance_scale(this->illuminance_scale_number_->state);

  engine.evaluate(now);

  // Canonical numeric outputs — publish on change only; a stale channel
  // publishes NAN, never a frozen reading.
  this->publish_changed_(this->temperature_sensor_, engine.temperature());
  this->publish_changed_(this->humidity_sensor_, engine.humidity());
  this->publish_changed_(this->illuminance_sensor_, engine.illuminance());

  // Factory-only support diagnostics: the built-in board profile applied
  // WITHOUT customer calibration.
  this->publish_changed_(this->factory_temperature_sensor_,
                         engine.factory_temperature());
  this->publish_changed_(this->factory_humidity_sensor_,
                         engine.factory_humidity());

  // Customer state outputs.
  this->publish_changed_(this->comfort_text_sensor_,
                         comfort_to_string(engine.comfort()));
  this->publish_changed_(this->brightness_text_sensor_,
                         brightness_to_string(engine.brightness()));
  this->publish_changed_(this->environment_text_sensor_,
                         environment_to_string(engine.environment()));

  // Module health — real freshness evidence driving the Core-Framework
  // reserved runtime vocabulary.
  this->publish_changed_(this->module_status_text_sensor_,
                         health_to_string(engine.health()));

  // Diagnostics.
  if (this->environment_detail_text_sensor_ != nullptr) {
    char buffer[120];
    snprintf(buffer, sizeof(buffer),
             "comfort=%s brightness=%s climate_fresh=%s light_fresh=%s",
             comfort_to_string(engine.comfort()),
             brightness_to_string(engine.brightness()),
             (engine.temperature_fresh() && engine.humidity_fresh()) ? "yes"
                                                                     : "no",
             engine.illuminance_fresh() ? "yes" : "no");
    this->publish_changed_(this->environment_detail_text_sensor_,
                           std::string(buffer));
  }
  if (this->calibration_state_text_sensor_ != nullptr) {
    const auto &profile = engine.climate_profile();
    char buffer[220];
    snprintf(buffer, sizeof(buffer),
             "factory %s %+.2f °C / %+.2f %%; customer temperature "
             "%+.1f °C, customer humidity %+.1f %%, illuminance x%.2f",
             profile.id, profile.temperature_correction_c,
             profile.humidity_residual_pct, engine.temperature_offset(),
             engine.humidity_offset(), engine.illuminance_scale());
    this->publish_changed_(this->calibration_state_text_sensor_,
                           std::string(buffer));
  }
}

void Sense360RoomIQ::dump_config() {
  ESP_LOGCONFIG(TAG, "Sense360 RoomIQ (glue over the canonical engine "
                     "singleton; model logic lives in "
                     "components/sense360/roomiq_engine.h)");
  ESP_LOGCONFIG(TAG, "  Climate windows: warmup %ums stale %ums",
                this->climate_warmup_ms_, this->climate_stale_ms_);
  ESP_LOGCONFIG(TAG, "  Illuminance windows: warmup %ums stale %ums",
                this->lux_warmup_ms_, this->lux_stale_ms_);
  ESP_LOGCONFIG(TAG, "  Calibration schema version: %d",
                this->calibration_schema_version_);
}

}  // namespace sense360_roomiq
}  // namespace esphome

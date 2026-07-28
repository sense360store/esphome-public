#include "sense360_presence.h"

#include <cmath>

#include "esphome/core/hal.h"
#include "esphome/core/log.h"

namespace esphome {
namespace sense360_presence {

static const char *const TAG = "sense360_presence";

// One evaluation clock, one publish owner — the exact cadence the YAML
// interval carried.
static constexpr uint32_t EVALUATE_INTERVAL_MS = 500;

float Sense360Presence::get_setup_priority() const { return setup_priority::DATA; }

void Sense360Presence::setup() {
  // PIR / SEN0609 edges re-evaluate immediately (the adapters' documented
  // behaviour; their script.execute hook lands here through the framework's
  // same-id bridge script as well — evaluate() is idempotent per tick).
  if (this->pir_sensor_ != nullptr) {
    this->pir_sensor_->add_on_state_callback([this](bool) { this->evaluate(); });
  }
  if (this->static_sensor_ != nullptr) {
    this->static_sensor_->add_on_state_callback([this](bool) { this->evaluate(); });
  }

  // Any real update callback from the radar sensors is a frame — the same
  // component-callback signal the retired adapter globals recorded.
  for (sensor::Sensor *s : {this->radar_target_count_sensor_,
                            this->radar_moving_count_sensor_,
                            this->radar_still_count_sensor_}) {
    if (s != nullptr) {
      s->add_on_state_callback([this](float) {
        this->radar_frame_seen_ = true;
        this->radar_last_frame_ms_ = millis();
      });
    }
  }

  // Runtime control interplay (PD-04 / PD-10): preset application and the
  // switch-to-Custom rule, formerly the select/number on_value lambdas.
  if (this->mode_select_ != nullptr) {
    // The pinned ESPHome's select state callback carries the option INDEX
    // (LazyCallbackManager<void(size_t)>); the option string is read back
    // from the select, which has already committed the new state.
    this->mode_select_->add_on_state_callback([this](size_t) {
      this->on_mode_changed_(this->mode_select_->current_option().c_str());
    });
  }
  if (this->clear_delay_number_ != nullptr) {
    this->clear_delay_number_->add_on_state_callback(
        [this](float value) { this->on_clear_delay_changed_(value); });
  }

  this->set_interval("s360_presence_evaluate", EVALUATE_INTERVAL_MS,
                     [this]() { this->evaluate(); });
}

void Sense360Presence::on_mode_changed_(const std::string &value) {
  using namespace sense360::presence;
  Mode mode = mode_from_string(value.c_str());
  if (mode != MODE_CUSTOM && this->clear_delay_number_ != nullptr) {
    // Apply the mode's clear-delay preset to the customer control (guarded
    // so this does not bounce the mode to Custom). Custom never overwrites
    // the user's value.
    this->applying_mode_ = true;
    auto call = this->clear_delay_number_->make_call();
    call.set_value(mode_params(mode).clear_delay_ms / 1000.0f);
    call.perform();
    this->applying_mode_ = false;
  }
  this->evaluate();
}

void Sense360Presence::on_clear_delay_changed_(float value) {
  using namespace sense360::presence;
  // A manual edit away from the active preset switches the mode to Custom
  // (which preserves user values, PD-10).
  if (!this->applying_mode_ && this->mode_select_ != nullptr) {
    Mode mode = mode_from_string(this->mode_select_->current_option().c_str());
    if (mode != MODE_CUSTOM &&
        (uint32_t) (value * 1000.0f) != mode_params(mode).clear_delay_ms) {
      auto call = this->mode_select_->make_call();
      call.set_option("Custom");
      call.perform();
    }
  }
  this->evaluate();
}

void Sense360Presence::evaluate() {
  using namespace sense360::presence;
  auto &engine = global_engine();
  const uint32_t now = millis();

  // Configuration-driven expected-sensor membership (PD-08) and per-sensor
  // warm-up windows. GPIO-level channels (PIR, SEN0609 digital out) are
  // non-verifiable: they can never be proven fresh nor proven failed
  // (documented limitation; OD-SOT-004 stays open).
  engine.configure_pir(ChannelConfig{this->pir_expected_, false, this->pir_warmup_ms_, 0});
  engine.configure_radar(ChannelConfig{this->radar_expected_, true,
                                       this->radar_warmup_ms_, this->radar_stale_ms_});
  engine.configure_static(
      ChannelConfig{this->static_expected_, false, this->static_warmup_ms_, 0});

  // Runtime controls (no recompilation needed, PD-04/PD-10).
  if (this->mode_select_ != nullptr) {
    engine.set_mode(mode_from_string(this->mode_select_->current_option().c_str()));
  }
  if (this->clear_delay_number_ != nullptr) {
    float delay_s = this->clear_delay_number_->state;
    if (!std::isnan(delay_s) && delay_s > 0.0f) {
      engine.set_clear_delay_ms((uint32_t) (delay_s * 1000.0f));
    }
  }

  // Sensor inputs. The radar input carries the timestamp of the last REAL
  // frame; stale frames age out inside the engine.
  if (this->radar_frame_seen_) {
    float tc = this->radar_target_count_sensor_ != nullptr
                   ? this->radar_target_count_sensor_->state
                   : NAN;
    float mc = this->radar_moving_count_sensor_ != nullptr
                   ? this->radar_moving_count_sensor_->state
                   : NAN;
    float sc = this->radar_still_count_sensor_ != nullptr
                   ? this->radar_still_count_sensor_->state
                   : NAN;
    engine.input_radar_frame(this->radar_last_frame_ms_,
                             std::isnan(tc) ? 0 : (int) tc,
                             std::isnan(mc) ? 0 : (int) mc,
                             std::isnan(sc) ? 0 : (int) sc);
  }
  if (this->pir_sensor_ != nullptr) {
    engine.input_pir(now, this->pir_sensor_->state);
  }
  if (this->static_sensor_ != nullptr) {
    engine.input_static(now, this->static_sensor_->state);
  }

  engine.evaluate(now);

  // Publish outputs on change only.
  if (this->occupancy_binary_sensor_ != nullptr) {
    bool occ = engine.occupancy();
    if (!this->occupancy_binary_sensor_->has_state() ||
        this->occupancy_binary_sensor_->state != occ) {
      this->occupancy_binary_sensor_->publish_state(occ);
    }
  }
  if (this->status_text_sensor_ != nullptr) {
    std::string status = status_to_string(engine.status());
    if (this->status_text_sensor_->state != status) {
      this->status_text_sensor_->publish_state(status);
    }
  }
  if (this->module_status_text_sensor_ != nullptr) {
    std::string health = health_to_string(engine.health());
    if (this->module_status_text_sensor_->state != health) {
      this->module_status_text_sensor_->publish_state(health);
    }
  }
  // Radar Target Count is honest about freshness: while radar data is
  // stale/unavailable the value is unknown (NAN), never a fake 0.
  if (this->radar_target_count_output_ != nullptr) {
    float count = engine.radar_fresh() ? (float) engine.radar_target_count() : NAN;
    float prev = this->radar_target_count_output_->state;
    bool both_nan = std::isnan(count) && std::isnan(prev);
    if (!this->radar_target_count_output_->has_state() || (!both_nan && count != prev)) {
      this->radar_target_count_output_->publish_state(count);
    }
  }
}

float Sense360Presence::radar_data_age_s() const {
  if (!this->radar_frame_seen_)
    return NAN;
  return (millis() - this->radar_last_frame_ms_) / 1000.0f;
}

void Sense360Presence::dump_config() {
  ESP_LOGCONFIG(TAG, "Sense360 Presence (glue over the canonical fusion "
                     "singleton; model logic lives in "
                     "components/sense360/presence_fusion.h)");
  ESP_LOGCONFIG(TAG,
                "  Expected channels: pir=%s radar=%s sen0609=%s (PD-08; an "
                "intentionally absent sensor is never a fault)",
                YESNO(this->pir_expected_), YESNO(this->radar_expected_),
                YESNO(this->static_expected_));
}

}  // namespace sense360_presence
}  // namespace esphome

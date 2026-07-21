#include "sfa40.h"
#include "esphome/core/log.h"

namespace esphome {
namespace sfa40 {

static const char *const TAG = "sfa40";

// SFA40 I2C command words (Sensirion SFA40 datasheet D1 v1.1, Table 9).
static const uint16_t SFA40_CMD_START_CONTINUOUS_MEASUREMENT = 0x00AC;
static const uint16_t SFA40_CMD_READ_MEASUREMENT = 0xC0EB;
static const uint16_t SFA40_CMD_READ_SERIAL_NUMBER = 0x02CE;

void SFA40Component::setup() {
  ESP_LOGCONFIG(TAG, "Setting up SFA40...");

  // Serial number must be read in the idle state (before continuous
  // measurement starts). A read failure is not fatal — only diagnostic.
  uint16_t serial[3];
  if (this->get_register(SFA40_CMD_READ_SERIAL_NUMBER, serial, 3, 2)) {
    this->serial_number_ = (static_cast<uint64_t>(serial[0]) << 32) |
                           (static_cast<uint64_t>(serial[1]) << 16) |
                           static_cast<uint64_t>(serial[2]);
  } else {
    ESP_LOGW(TAG, "Could not read SFA40 serial number");
  }

  // Enter continuous measurement mode (autonomous update every 0.5 s).
  if (!this->write_command(SFA40_CMD_START_CONTINUOUS_MEASUREMENT)) {
    ESP_LOGE(TAG, "Failed to start SFA40 continuous measurement");
    this->error_code_ = MEASUREMENT_INIT_FAILED;
    this->mark_failed();
    return;
  }
}

void SFA40Component::dump_config() {
  ESP_LOGCONFIG(TAG, "SFA40:");
  LOG_I2C_DEVICE(this);
  if (this->is_failed()) {
    switch (this->error_code_) {
      case MEASUREMENT_INIT_FAILED:
        ESP_LOGE(TAG, "  Measurement initialization failed");
        break;
      case SERIAL_NUMBER_IDENTIFICATION_FAILED:
        ESP_LOGE(TAG, "  Unable to read serial number");
        break;
      default:
        ESP_LOGE(TAG, "  Communication with SFA40 failed");
        break;
    }
  } else {
    ESP_LOGCONFIG(TAG, "  Serial number: 0x%08X%08X", static_cast<uint32_t>(this->serial_number_ >> 32),
                  static_cast<uint32_t>(this->serial_number_ & 0xFFFFFFFF));
  }
  LOG_UPDATE_INTERVAL(this);
  LOG_SENSOR("  ", "Formaldehyde", this->formaldehyde_sensor_);
  LOG_SENSOR("  ", "Humidity", this->humidity_sensor_);
  LOG_SENSOR("  ", "Temperature", this->temperature_sensor_);
}

void SFA40Component::update() {
  if (!this->write_command(SFA40_CMD_READ_MEASUREMENT)) {
    this->status_set_warning();
    ESP_LOGW(TAG, "Failed to send SFA40 read command");
    return;
  }

  // read_measurement returns four CRC-checked words: HCHO, RH, temperature and
  // the status word. Data is available immediately; a short delay mirrors the
  // conservative timing used by the Sensirion reference flow.
  this->set_timeout(5, [this]() {
    uint16_t words[4];
    if (!this->read_data(words, 4)) {
      this->status_set_warning();
      ESP_LOGW(TAG, "Failed to read SFA40 measurement (CRC/I2C error)");
      return;
    }

    const uint16_t hcho_ticks = words[0];
    const uint16_t rh_ticks = words[1];
    const uint16_t t_ticks = words[2];
    const uint8_t status = static_cast<uint8_t>(words[3] >> 8);

    const bool not_ready = (status & 0x01) != 0;  // < 1 min after power-up

    // Formaldehyde: ppb = ticks / 10 (datasheet §3.6). During warm-up the
    // sensor deliberately outputs 0 and flags "not ready" — publish unknown in
    // that window rather than a spurious 0.
    if (this->formaldehyde_sensor_ != nullptr) {
      if (not_ready) {
        this->formaldehyde_sensor_->publish_state(NAN);
      } else {
        this->formaldehyde_sensor_->publish_state(hcho_ticks / 10.0f);
      }
    }

    // Humidity: %RH = -6 + 125 * ticks / 65535, clamped to [0, 100].
    if (this->humidity_sensor_ != nullptr) {
      float rh = -6.0f + 125.0f * rh_ticks / 65535.0f;
      if (rh < 0.0f)
        rh = 0.0f;
      if (rh > 100.0f)
        rh = 100.0f;
      this->humidity_sensor_->publish_state(rh);
    }

    // Temperature: degC = -45 + 175 * ticks / 65535.
    if (this->temperature_sensor_ != nullptr) {
      const float t = -45.0f + 175.0f * t_ticks / 65535.0f;
      this->temperature_sensor_->publish_state(t);
    }

    this->status_clear_warning();
  });
}

}  // namespace sfa40
}  // namespace esphome

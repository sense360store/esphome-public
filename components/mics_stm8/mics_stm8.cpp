#include "mics_stm8.h"
#include "esphome/core/log.h"

namespace esphome {
namespace mics_stm8 {

static const char *const TAG = "mics_stm8";

void MICSSTM8Component::setup() {
  ESP_LOGCONFIG(TAG, "Setting up MICS-4514/STM8 bridge...");
  // A first read establishes identity/protocol; a failure here is not fatal —
  // the STM8 may still be booting. update() keeps retrying and the online
  // getters report the transport state honestly.
  this->read_block_();
}

void MICSSTM8Component::update() { this->read_block_(); }

bool MICSSTM8Component::read_block_() {
  uint8_t buf[MICS_STM8_REG_BLOCK_LEN];
  if (this->read_register(MICS_STM8_REG_BLOCK_BASE, buf, MICS_STM8_REG_BLOCK_LEN) != i2c::ERROR_OK) {
    // Never retain stale "ready" values across a failed read.
    this->online_ = false;
    this->identity_ok_ = false;
    this->protocol_ok_ = false;
    this->status_set_warning();
    ESP_LOGW(TAG, "MICS/STM8 read failed");
    return false;
  }

  this->status_ = buf[0x00];
  this->warmup_remaining_ = (static_cast<uint16_t>(buf[0x01]) << 8) | buf[0x02];
  this->red_adc_ = (static_cast<uint16_t>(buf[0x03]) << 8) | buf[0x04];
  this->ox_adc_ = (static_cast<uint16_t>(buf[0x05]) << 8) | buf[0x06];
  this->red_baseline_ = (static_cast<uint16_t>(buf[0x07]) << 8) | buf[0x08];
  this->ox_baseline_ = (static_cast<uint16_t>(buf[0x09]) << 8) | buf[0x0A];
  this->firmware_ = buf[0x0B];
  this->protocol_ = buf[0x0C];
  this->identity_[0] = buf[0x0D];
  this->identity_[1] = buf[0x0E];
  this->fault_flags_ = buf[0x0F];
  this->adc_error_count_ = buf[0x10];
  this->i2c_error_count_ = buf[0x11];
  this->calibration_samples_ = buf[0x12];
  this->red_cal_spread_ = buf[0x13];
  this->ox_cal_spread_ = buf[0x14];
  this->last_command_ = buf[0x15];
  this->last_command_result_ = buf[0x16];
  this->reset_reason_ = buf[0x17];

  this->identity_ok_ = (this->identity_[0] == MICS_STM8_IDENTITY_0) && (this->identity_[1] == MICS_STM8_IDENTITY_1);
  this->protocol_ok_ = (this->protocol_ == MICS_STM8_PROTOCOL_VERSION);
  this->online_ = this->identity_ok_ && this->protocol_ok_;

  if (!this->online_) {
    ESP_LOGW(TAG, "MICS/STM8 identity/protocol mismatch (id=%c%c proto=%u fw=0x%02X)", this->identity_[0],
             this->identity_[1], this->protocol_, this->firmware_);
    this->status_set_warning();
    return false;
  }

  this->status_clear_warning();
  return true;
}

bool MICSSTM8Component::values_valid() const {
  // Gas ratios are trustworthy only when the full STM8 readiness contract
  // holds. Note: lifetime error counters (0x10/0x11) are deliberately NOT part
  // of this gate — only the active fault flags (0x0F) are.
  return this->online_ && (this->status_ & MICS_STM8_STATUS_WARMING) == 0 &&
         (this->status_ & MICS_STM8_STATUS_CALIBRATED) != 0 && (this->status_ & MICS_STM8_STATUS_HEATER_ON) != 0 &&
         this->red_baseline_ != 0 && this->ox_baseline_ != 0 && this->fault_flags_ == 0;
}

float MICSSTM8Component::red_ratio() const {
  if (!this->values_valid() || this->red_baseline_ == 0)
    return NAN;
  return static_cast<float>(this->red_adc_) / static_cast<float>(this->red_baseline_);
}

float MICSSTM8Component::ox_ratio() const {
  if (!this->values_valid() || this->ox_baseline_ == 0)
    return NAN;
  return static_cast<float>(this->ox_adc_) / static_cast<float>(this->ox_baseline_);
}

std::string MICSSTM8Component::identity_string() const {
  if (!this->online_)
    return "offline";
  return std::string(1, static_cast<char>(this->identity_[0])) + std::string(1, static_cast<char>(this->identity_[1]));
}

std::string MICSSTM8Component::protocol_status() const {
  if (!this->identity_ok_)
    return "offline";
  if (!this->protocol_ok_)
    return "unsupported protocol";
  return "OK";
}

std::string MICSSTM8Component::fault_detail() const {
  if (!this->online_)
    return "offline";
  if (this->fault_flags_ == 0)
    return "none";
  char buf[24];
  snprintf(buf, sizeof(buf), "flags 0x%02X", this->fault_flags_);
  return buf;
}

std::string MICSSTM8Component::last_command_result() const {
  if (!this->online_)
    return "offline";
  char buf[40];
  snprintf(buf, sizeof(buf), "cmd 0x%02X -> 0x%02X", this->last_command_, this->last_command_result_);
  return buf;
}

std::string MICSSTM8Component::reset_reason() const {
  if (!this->online_)
    return "offline";
  char buf[16];
  snprintf(buf, sizeof(buf), "0x%02X", this->reset_reason_);
  return buf;
}

void MICSSTM8Component::recalibrate() {
  const uint8_t cmd = MICS_STM8_CMD_RECALIBRATE;
  if (this->write_register(MICS_STM8_REG_COMMAND, &cmd, 1) != i2c::ERROR_OK) {
    ESP_LOGW(TAG, "MICS/STM8 recalibrate command failed");
  } else {
    ESP_LOGI(TAG, "MICS/STM8 recalibrate requested");
  }
}

void MICSSTM8Component::heater_on() {
  const uint8_t cmd = MICS_STM8_CMD_HEATER_ON;
  if (this->write_register(MICS_STM8_REG_COMMAND, &cmd, 1) != i2c::ERROR_OK) {
    ESP_LOGW(TAG, "MICS/STM8 heater-on command failed");
  }
}

void MICSSTM8Component::heater_off() {
  const uint8_t cmd = MICS_STM8_CMD_HEATER_OFF;
  if (this->write_register(MICS_STM8_REG_COMMAND, &cmd, 1) != i2c::ERROR_OK) {
    ESP_LOGW(TAG, "MICS/STM8 heater-off command failed");
  }
}

void MICSSTM8Component::dump_config() {
  ESP_LOGCONFIG(TAG, "MICS-4514/STM8 bridge:");
  LOG_I2C_DEVICE(this);
  LOG_UPDATE_INTERVAL(this);
  ESP_LOGCONFIG(TAG, "  Expected identity: M4, protocol v%u, firmware >= 0x%02X", MICS_STM8_PROTOCOL_VERSION,
                MICS_STM8_MIN_FIRMWARE);
}

}  // namespace mics_stm8
}  // namespace esphome

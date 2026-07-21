#pragma once

// ============================================================================
// MICS-4514 + STM8 I2C bridge driver (S360-210-R4 U4 + U5)
// ============================================================================
// The MICS-4514 multi-gas sensor (U4) is driven by an STM8S003F3U co-processor
// (U5) whose analog front end (U6 LMV358) it digitises. The ESP32-S3 talks to
// the STM8 bridge over the shared Core I2C bus; the STM8 exposes a fixed 24-byte
// register block (0x00..0x17) plus a single command register (0xFE).
//
// This driver reads the register block, exposes every field through getters,
// and enforces the STM8 validity contract: a reducing/oxidising ratio is a real
// value ONLY when the bridge is online with identity "M4", a supported protocol
// version, warm-up complete, the sensor calibrated, the heater on, both
// baselines non-zero and no active fault flag. Otherwise ratios report unknown
// (NaN) — a stale "ready" value is never retained across a failed read or a
// reboot. Raw ADC / status / diagnostic fields are published whenever a read
// succeeds (including during warm-up).
//
// NO customer CO / NO2 concentration is derived or claimed here: the MICS stage
// is a diagnostic reducing/oxidising ratio surface only. Register-map, address
// (0x60), protocol version (1), identity ("M4") and current firmware (0x24) are
// per the owner-provided STM8 firmware specification; on-hardware bench
// verification of the fitted MICS/STM8 stage remains pending
// (docs/hardware/airiq-framework-bench-checklist.md). Nothing here claims
// hardware validation.
// ============================================================================

#include "esphome/components/i2c/i2c.h"
#include "esphome/core/component.h"

#include <string>

namespace esphome {
namespace mics_stm8 {

// STM8 register block layout (24 bytes, base register 0x00).
static const uint8_t MICS_STM8_REG_BLOCK_BASE = 0x00;
static const uint8_t MICS_STM8_REG_BLOCK_LEN = 24;
static const uint8_t MICS_STM8_REG_COMMAND = 0xFE;

// Command register (0xFE) values.
static const uint8_t MICS_STM8_CMD_RECALIBRATE = 0x01;
static const uint8_t MICS_STM8_CMD_HEATER_OFF = 0x02;
static const uint8_t MICS_STM8_CMD_HEATER_ON = 0x03;

// Expected identity / protocol.
static const uint8_t MICS_STM8_IDENTITY_0 = 'M';  // register 0x0D
static const uint8_t MICS_STM8_IDENTITY_1 = '4';  // register 0x0E
static const uint8_t MICS_STM8_PROTOCOL_VERSION = 1;
static const uint8_t MICS_STM8_MIN_FIRMWARE = 0x24;  // v2.4 (current tested)

// Status byte (register 0x00) bit masks.
static const uint8_t MICS_STM8_STATUS_WARMING = 0x80;     // bit 7
static const uint8_t MICS_STM8_STATUS_HEATER_ON = 0x02;   // bit 1
static const uint8_t MICS_STM8_STATUS_CALIBRATED = 0x01;  // bit 0

class MICSSTM8Component : public PollingComponent, public i2c::I2CDevice {
 public:
  void setup() override;
  void update() override;
  void dump_config() override;
  float get_setup_priority() const override { return setup_priority::DATA; }

  // --- commands (written to register 0xFE) ---------------------------------
  void recalibrate();
  void heater_on();
  void heater_off();

  // --- transport / identity ------------------------------------------------
  // online: last read succeeded AND identity is "M4" AND the protocol version
  // is supported. A lifetime I2C error count of 1 at startup is NOT a fault
  // (that decision uses the active fault flags at 0x0F, never the counters).
  bool online() const { return online_; }
  bool identity_ok() const { return identity_ok_; }
  bool protocol_ok() const { return protocol_ok_; }
  std::string identity_string() const;
  std::string protocol_status() const;

  // --- status bits ---------------------------------------------------------
  bool warming() const { return online_ && (status_ & MICS_STM8_STATUS_WARMING) != 0; }
  bool calibrated() const { return online_ && (status_ & MICS_STM8_STATUS_CALIBRATED) != 0; }
  bool heater_on_state() const { return online_ && (status_ & MICS_STM8_STATUS_HEATER_ON) != 0; }

  // --- diagnostic values (NaN / empty when offline) ------------------------
  float firmware_version() const { return online_ ? static_cast<float>(firmware_) : NAN; }
  float warmup_remaining() const { return online_ ? static_cast<float>(warmup_remaining_) : NAN; }
  float red_adc() const { return online_ ? static_cast<float>(red_adc_) : NAN; }
  float ox_adc() const { return online_ ? static_cast<float>(ox_adc_) : NAN; }
  float red_baseline() const { return online_ ? static_cast<float>(red_baseline_) : NAN; }
  float ox_baseline() const { return online_ ? static_cast<float>(ox_baseline_) : NAN; }
  float fault_flags() const { return online_ ? static_cast<float>(fault_flags_) : NAN; }
  float adc_error_count() const { return online_ ? static_cast<float>(adc_error_count_) : NAN; }
  float i2c_error_count() const { return online_ ? static_cast<float>(i2c_error_count_) : NAN; }
  float calibration_samples() const { return online_ ? static_cast<float>(calibration_samples_) : NAN; }
  float red_calibration_spread() const { return online_ ? static_cast<float>(red_cal_spread_) : NAN; }
  float ox_calibration_spread() const { return online_ ? static_cast<float>(ox_cal_spread_) : NAN; }
  std::string fault_detail() const;
  std::string last_command_result() const;
  std::string reset_reason() const;

  // --- gas ratios (validity-gated; NaN unless the full contract holds) ------
  // Ratio = raw ADC / baseline (a normalised reducing/oxidising surface, NOT a
  // gas concentration). Published only when values_valid().
  bool values_valid() const;
  float red_ratio() const;
  float ox_ratio() const;

 protected:
  bool read_block_();

  bool online_{false};
  bool identity_ok_{false};
  bool protocol_ok_{false};

  uint8_t status_{0};
  uint16_t warmup_remaining_{0};
  uint16_t red_adc_{0};
  uint16_t ox_adc_{0};
  uint16_t red_baseline_{0};
  uint16_t ox_baseline_{0};
  uint8_t firmware_{0};
  uint8_t protocol_{0};
  uint8_t identity_[2]{0, 0};
  uint8_t fault_flags_{0};
  uint8_t adc_error_count_{0};
  uint8_t i2c_error_count_{0};
  uint8_t calibration_samples_{0};
  uint8_t red_cal_spread_{0};
  uint8_t ox_cal_spread_{0};
  uint8_t last_command_{0};
  uint8_t last_command_result_{0};
  uint8_t reset_reason_{0};
};

}  // namespace mics_stm8
}  // namespace esphome

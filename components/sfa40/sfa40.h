#pragma once

// ============================================================================
// Sensirion SFA40 formaldehyde sensor driver (S360-210-R4 U2)
// ============================================================================
// Implements the SFA40 I2C protocol per the Sensirion SFA40 datasheet
// (D1 v1.1, April 2026). The SFA40 shares the SFA30's 0x5D address and
// Sensirion CRC-8 but uses a distinct command set, so it needs its own driver
// rather than ESPHome's native `sfa30` platform:
//
//   start_continuous_measurement : 0x00AC
//   read_measurement             : 0xC0EB  (4 words / 12 bytes)
//   stop_continuous_measurement  : 0x50D2
//   read_serial_number           : 0x02CE  (3 words, idle state only)
//
// read_measurement response (each word is 2 data bytes + CRC):
//   word0 = formaldehyde ticks   -> ppb   = ticks / 10
//   word1 = humidity ticks       -> %RH   = -6  + 125 * ticks / 65535 (clamp 0..100)
//   word2 = temperature ticks    -> deg C = -45 + 175 * ticks / 65535
//   word3 = status (high byte) + reserved(0) (low byte)
//     status bit0 = sensor not ready (< 1 min after power-up; HCHO output is 0)
//     status bit1 = sensor not yet within specifications (< 10 min)
//
// Nothing here claims hardware validation.
// ============================================================================

#include "esphome/components/sensirion_common/i2c_sensirion.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/core/component.h"

namespace esphome {
namespace sfa40 {

class SFA40Component : public PollingComponent, public sensirion_common::SensirionI2CDevice {
 public:
  void setup() override;
  void update() override;
  void dump_config() override;
  float get_setup_priority() const override { return setup_priority::DATA; }

  void set_formaldehyde_sensor(sensor::Sensor *sensor) { formaldehyde_sensor_ = sensor; }
  void set_humidity_sensor(sensor::Sensor *sensor) { humidity_sensor_ = sensor; }
  void set_temperature_sensor(sensor::Sensor *sensor) { temperature_sensor_ = sensor; }

 protected:
  enum ErrorCode {
    NONE = 0,
    SERIAL_NUMBER_IDENTIFICATION_FAILED,
    MEASUREMENT_INIT_FAILED,
    UNKNOWN,
  } error_code_{NONE};

  uint64_t serial_number_{0};

  sensor::Sensor *formaldehyde_sensor_{nullptr};
  sensor::Sensor *humidity_sensor_{nullptr};
  sensor::Sensor *temperature_sensor_{nullptr};
};

}  // namespace sfa40
}  // namespace esphome

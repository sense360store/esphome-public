#pragma once

#include <cmath>
#include <algorithm>

namespace sense360 {
namespace calibration {

// Calibration result structure
struct CalibrationResult {
  float temperature_offset;  // °C
  float humidity_offset;     // %RH
  bool valid;

  CalibrationResult() : temperature_offset(0.0f), humidity_offset(0.0f), valid(false) {}
  CalibrationResult(float temp_offset, float hum_offset, bool is_valid = true)
    : temperature_offset(temp_offset), humidity_offset(hum_offset), valid(is_valid) {}
};

/**
 * Compute single-point calibration offsets for SHT30 sensor
 *
 * @param reference_temp Reference temperature from calibrated source (°C)
 * @param reference_humidity Reference humidity from calibrated source (%RH)
 * @param raw_temp Raw temperature reading from SHT30 (°C)
 * @param raw_humidity Raw humidity reading from SHT30 (%RH)
 * @return CalibrationResult with clamped offsets
 *
 * Offset calculation:
 *   temp_offset = reference_temp - raw_temp
 *   humidity_offset = reference_humidity - raw_humidity
 *
 * Clamping:
 *   Temperature offset: [-30.0, +30.0] °C
 *   Humidity offset: [-50.0, +50.0] %RH
 */
inline CalibrationResult compute_single_point_calibration(
    float reference_temp,
    float reference_humidity,
    float raw_temp,
    float raw_humidity) {

  // Check for NaN values
  if (std::isnan(reference_temp) || std::isnan(reference_humidity) ||
      std::isnan(raw_temp) || std::isnan(raw_humidity)) {
    return CalibrationResult();  // Invalid result
  }

  // Compute offsets
  float temp_offset = reference_temp - raw_temp;
  float humidity_offset = reference_humidity - raw_humidity;

  // Clamp temperature offset to safe range [-30, +30] °C
  temp_offset = std::max(-30.0f, std::min(30.0f, temp_offset));

  // Clamp humidity offset to safe range [-50, +50] %RH
  humidity_offset = std::max(-50.0f, std::min(50.0f, humidity_offset));

  return CalibrationResult(temp_offset, humidity_offset, true);
}

/**
 * Apply calibration offset to raw temperature reading
 *
 * @param raw_temp Raw temperature from sensor (°C)
 * @param offset Calibration offset (°C)
 * @return Calibrated temperature (°C), or NaN if input is NaN
 */
inline float apply_temperature_calibration(float raw_temp, float offset) {
  if (std::isnan(raw_temp)) {
    return NAN;
  }
  return raw_temp + offset;
}

/**
 * Apply calibration offset to raw humidity reading
 *
 * @param raw_humidity Raw humidity from sensor (%RH)
 * @param offset Calibration offset (%RH)
 * @return Calibrated humidity (%RH), or NaN if input is NaN
 */
inline float apply_humidity_calibration(float raw_humidity, float offset) {
  if (std::isnan(raw_humidity)) {
    return NAN;
  }
  float calibrated = raw_humidity + offset;

  // Clamp to physically valid range [0, 100] %RH
  return std::max(0.0f, std::min(100.0f, calibrated));
}

/**
 * Validate calibration offsets are within acceptable ranges
 *
 * @param temp_offset Temperature offset (°C)
 * @param humidity_offset Humidity offset (%RH)
 * @return true if offsets are within valid ranges
 */
inline bool validate_calibration_offsets(float temp_offset, float humidity_offset) {
  // Check for NaN
  if (std::isnan(temp_offset) || std::isnan(humidity_offset)) {
    return false;
  }

  // Check temperature offset range
  if (temp_offset < -30.0f || temp_offset > 30.0f) {
    return false;
  }

  // Check humidity offset range
  if (humidity_offset < -50.0f || humidity_offset > 50.0f) {
    return false;
  }

  return true;
}

/**
 * Check if calibration is needed based on error magnitude
 * Recommends calibration if error exceeds thresholds:
 *   Temperature: ±2.0°C
 *   Humidity: ±5.0%RH
 *
 * @param reference_temp Reference temperature (°C)
 * @param reference_humidity Reference humidity (%RH)
 * @param raw_temp Raw temperature (°C)
 * @param raw_humidity Raw humidity (%RH)
 * @return true if calibration is recommended
 */
inline bool should_calibrate(
    float reference_temp,
    float reference_humidity,
    float raw_temp,
    float raw_humidity) {

  // Check for NaN
  if (std::isnan(reference_temp) || std::isnan(reference_humidity) ||
      std::isnan(raw_temp) || std::isnan(raw_humidity)) {
    return false;
  }

  const float temp_error = std::abs(reference_temp - raw_temp);
  const float humidity_error = std::abs(reference_humidity - raw_humidity);

  const float TEMP_THRESHOLD = 2.0f;      // °C
  const float HUMIDITY_THRESHOLD = 5.0f;  // %RH

  return (temp_error > TEMP_THRESHOLD) || (humidity_error > HUMIDITY_THRESHOLD);
}

} // namespace calibration
} // namespace sense360

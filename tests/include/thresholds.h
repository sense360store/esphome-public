#pragma once

#include <cmath>
#include <string>

namespace sense360 {
namespace thresholds {

// Air quality status levels
enum AirQualityStatus {
  STATUS_UNKNOWN = -1,
  STATUS_GOOD = 0,
  STATUS_MODERATE = 1,
  STATUS_UNHEALTHY = 2,
  STATUS_POOR = 3
};

/**
 * Convert status enum to human-readable string
 */
inline const char* status_to_string(AirQualityStatus status) {
  switch (status) {
    case STATUS_GOOD:       return "Good";
    case STATUS_MODERATE:   return "Moderate";
    case STATUS_UNHEALTHY:  return "Unhealthy";
    case STATUS_POOR:       return "Poor";
    case STATUS_UNKNOWN:
    default:                return "Unknown";
  }
}

/**
 * Classify sensor value into air quality status based on thresholds
 *
 * @param value Sensor reading (PM, VOC, NOx, CO2, etc.)
 * @param good_threshold Upper limit for "Good" status
 * @param moderate_threshold Upper limit for "Moderate" status
 * @param unhealthy_threshold Upper limit for "Unhealthy" status
 * @return AirQualityStatus
 *
 * Logic:
 *   value < good_threshold          -> Good
 *   value < moderate_threshold      -> Moderate
 *   value < unhealthy_threshold     -> Unhealthy
 *   value >= unhealthy_threshold    -> Poor
 *   value is NaN                    -> Unknown
 */
inline AirQualityStatus classify_value(
    float value,
    float good_threshold,
    float moderate_threshold,
    float unhealthy_threshold) {

  // Check for invalid/unknown value
  if (std::isnan(value)) {
    return STATUS_UNKNOWN;
  }

  // Classify based on thresholds (strict less-than comparisons)
  if (value < good_threshold) {
    return STATUS_GOOD;
  } else if (value < moderate_threshold) {
    return STATUS_MODERATE;
  } else if (value < unhealthy_threshold) {
    return STATUS_UNHEALTHY;
  } else {
    return STATUS_POOR;
  }
}

/**
 * Get worst (maximum) air quality status among multiple readings
 */
inline AirQualityStatus get_worst_status(AirQualityStatus s1, AirQualityStatus s2) {
  // Unknown doesn't affect worst calculation
  if (s1 == STATUS_UNKNOWN) return s2;
  if (s2 == STATUS_UNKNOWN) return s1;

  return static_cast<AirQualityStatus>(std::max(
    static_cast<int>(s1),
    static_cast<int>(s2)
  ));
}

/**
 * Get worst status among three readings
 */
inline AirQualityStatus get_worst_status(AirQualityStatus s1, AirQualityStatus s2, AirQualityStatus s3) {
  return get_worst_status(get_worst_status(s1, s2), s3);
}

/**
 * Get worst status among four readings
 */
inline AirQualityStatus get_worst_status(AirQualityStatus s1, AirQualityStatus s2, AirQualityStatus s3, AirQualityStatus s4) {
  return get_worst_status(get_worst_status(s1, s2), get_worst_status(s3, s4));
}

/**
 * Preserve last valid sensor reading when current reading is NaN
 * Used for CO2 sensor during "heating up" phase
 *
 * @param current_value Current sensor reading (may be NaN)
 * @param last_valid_value Previously stored valid reading
 * @param fallback_value Value to return if no valid reading exists
 * @return Valid sensor value or fallback
 */
inline float preserve_last_valid(float current_value, float last_valid_value, float fallback_value = NAN) {
  // If current value is valid, use it
  if (!std::isnan(current_value)) {
    return current_value;
  }

  // Otherwise, return last valid value if available
  if (!std::isnan(last_valid_value)) {
    return last_valid_value;
  }

  // No valid reading available
  return fallback_value;
}

/**
 * Update last valid value tracker
 * Returns the new value to store
 */
inline float update_last_valid(float current_value, float last_valid_value) {
  if (!std::isnan(current_value)) {
    return current_value;
  }
  return last_valid_value;
}

// Default threshold values for various sensors (µg/m³, ppm, or index)

// PM1.0 thresholds (µg/m³)
constexpr float PM1_GOOD = 10.0f;
constexpr float PM1_MODERATE = 20.0f;
constexpr float PM1_UNHEALTHY = 35.0f;

// PM2.5 thresholds (µg/m³)
constexpr float PM25_GOOD = 10.0f;
constexpr float PM25_MODERATE = 25.0f;
constexpr float PM25_UNHEALTHY = 50.0f;

// PM4.0 thresholds (µg/m³)
constexpr float PM40_GOOD = 20.0f;
constexpr float PM40_MODERATE = 40.0f;
constexpr float PM40_UNHEALTHY = 75.0f;

// PM10 thresholds (µg/m³)
constexpr float PM10_GOOD = 20.0f;
constexpr float PM10_MODERATE = 50.0f;
constexpr float PM10_UNHEALTHY = 100.0f;

// VOC Index thresholds (index 0-500)
constexpr float VOC_GOOD = 80.0f;
constexpr float VOC_MODERATE = 150.0f;
constexpr float VOC_UNHEALTHY = 250.0f;

// NOx Index thresholds (index 0-500)
constexpr float NOX_GOOD = 80.0f;
constexpr float NOX_MODERATE = 150.0f;
constexpr float NOX_UNHEALTHY = 250.0f;

// CO2 thresholds (ppm)
constexpr float CO2_GOOD = 750.0f;
constexpr float CO2_MODERATE = 1000.0f;
constexpr float CO2_UNHEALTHY = 1500.0f;

} // namespace thresholds
} // namespace sense360

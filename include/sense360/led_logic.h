#pragma once

#include <cstdint>
#include <cmath>
#include <algorithm>

namespace sense360 {
namespace led {

// RGB Color structure
struct Color {
  uint8_t red;
  uint8_t green;
  uint8_t blue;

  Color(uint8_t r, uint8_t g, uint8_t b) : red(r), green(g), blue(b) {}

  bool operator==(const Color& other) const {
    return red == other.red && green == other.green && blue == other.blue;
  }
};

// Severity levels
enum SeverityLevel {
  LEVEL_UNKNOWN = -1,
  LEVEL_GOOD = 0,
  LEVEL_MODERATE = 1,
  LEVEL_UNHEALTHY = 2,
  LEVEL_POOR = 3
};

/**
 * Map severity level to color
 * Unknown -> dim blue/gray
 * Good -> Green
 * Moderate -> Orange
 * Unhealthy -> Red
 * Poor -> Purple
 */
inline Color color_for_severity(int level) {
  switch (level) {
    case LEVEL_UNKNOWN:   return Color(24, 32, 64);    // Unknown (dim blue/gray)
    case LEVEL_GOOD:      return Color(0, 255, 0);     // Green
    case LEVEL_MODERATE:  return Color(255, 128, 0);   // Orange
    case LEVEL_UNHEALTHY: return Color(255, 0, 0);     // Red
    case LEVEL_POOR:      return Color(128, 0, 255);   // Purple
    default:              return Color(128, 0, 255);   // Purple (fallback)
  }
}

/**
 * Scale color by brightness factor (0.0 - 1.0)
 */
inline Color scale_color(const Color& c, float scale) {
  // Clamp scale to valid range
  if (scale < 0.0f) scale = 0.0f;
  if (scale > 1.0f) scale = 1.0f;

  return Color(
    static_cast<uint8_t>(c.red * scale),
    static_cast<uint8_t>(c.green * scale),
    static_cast<uint8_t>(c.blue * scale)
  );
}

/**
 * Compute severity level for a sensor value based on thresholds
 * Returns LEVEL_UNKNOWN if value is NaN or invalid
 * Returns LEVEL_GOOD if value < good_threshold
 * Returns LEVEL_MODERATE if value < moderate_threshold
 * Returns LEVEL_UNHEALTHY if value < unhealthy_threshold
 * Returns LEVEL_POOR otherwise
 */
inline int compute_level(float value, float good_threshold, float moderate_threshold, float unhealthy_threshold) {
  // Check for NaN or invalid value
  if (std::isnan(value)) {
    return LEVEL_UNKNOWN;
  }

  // Classify based on thresholds
  if (value < good_threshold) {
    return LEVEL_GOOD;
  } else if (value < moderate_threshold) {
    return LEVEL_MODERATE;
  } else if (value < unhealthy_threshold) {
    return LEVEL_UNHEALTHY;
  } else {
    return LEVEL_POOR;
  }
}

/**
 * Compute brightness scale factor based on maximum severity level
 * Good (0) -> 40%
 * Moderate (1) -> 60%
 * Unhealthy (2) -> 80%
 * Poor (3+) -> 100%
 */
inline float brightness_scale_for_level(int max_level) {
  switch (max_level) {
    case LEVEL_GOOD:      return 0.40f;
    case LEVEL_MODERATE:  return 0.60f;
    case LEVEL_UNHEALTHY: return 0.80f;
    default:              return 1.00f;  // Poor or Unknown
  }
}

/**
 * Compute pulsing brightness multiplier for poor air quality
 * Uses sine wave with 5-second period
 * Returns value between 0.90 and 1.00
 */
inline float compute_pulse_multiplier(unsigned long millis) {
  const float phase = static_cast<float>(millis % 5000) / 5000.0f;
  const float pulse = 0.90f + 0.10f * (0.5f + 0.5f * std::sin(phase * 2.0f * 3.14159265f));
  return std::min(1.0f, pulse);
}

/**
 * Compute aggregate severity level across multiple PM sensors
 * Takes worst (maximum) level among all provided sensors
 */
inline int aggregate_pm_levels(int pm1_level, int pm25_level, int pm40_level, int pm10_level) {
  return std::max(std::max(pm1_level, pm25_level), std::max(pm40_level, pm10_level));
}

/**
 * Compute overall worst severity across all sensor types
 */
inline int compute_overall_severity(int pm_level, int voc_level, int nox_level, int co2_level) {
  return std::max(std::max(pm_level, voc_level), std::max(nox_level, co2_level));
}

} // namespace led
} // namespace sense360

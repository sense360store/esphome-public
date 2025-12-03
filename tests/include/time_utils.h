#pragma once

#include <cstdint>

namespace sense360 {
namespace time_utils {

/**
 * Time structure (hour and minute)
 */
struct Time {
  int hour;    // 0-23
  int minute;  // 0-59

  Time() : hour(0), minute(0) {}
  Time(int h, int m) : hour(h), minute(m) {}

  /**
   * Convert to minutes since midnight (0-1439)
   */
  int to_minutes() const {
    return hour * 60 + minute;
  }

  /**
   * Create Time from minutes since midnight
   */
  static Time from_minutes(int minutes) {
    // Ensure minutes is in valid range [0, 1439]
    minutes = minutes % 1440;
    if (minutes < 0) minutes += 1440;

    return Time(minutes / 60, minutes % 60);
  }

  bool operator==(const Time& other) const {
    return hour == other.hour && minute == other.minute;
  }
};

/**
 * Check if current time is within night mode period
 * Handles time ranges that cross midnight (e.g., 22:00 - 07:00)
 *
 * @param current_time Current time
 * @param start_time Night mode start time
 * @param end_time Night mode end time
 * @return true if current time is within night mode period
 *
 * Examples:
 *   Same-day range (08:00 - 17:00): True if current >= start AND current < end
 *   Cross-midnight range (22:00 - 07:00): True if current >= start OR current < end
 */
inline bool is_within_night_mode(const Time& current_time, const Time& start_time, const Time& end_time) {
  const int current_minutes = current_time.to_minutes();
  const int start_minutes = start_time.to_minutes();
  const int end_minutes = end_time.to_minutes();

  // Same-day range (start <= end)
  if (start_minutes <= end_minutes) {
    return (current_minutes >= start_minutes) && (current_minutes < end_minutes);
  }
  // Cross-midnight range (start > end)
  else {
    return (current_minutes >= start_minutes) || (current_minutes < end_minutes);
  }
}

/**
 * Compute next night mode state change time
 * Returns the next time when night mode will activate or deactivate
 *
 * @param current_time Current time
 * @param start_time Night mode start time
 * @param end_time Night mode end time
 * @param currently_night Whether currently in night mode
 * @return Next state change time
 */
inline Time next_state_change(const Time& current_time, const Time& start_time, const Time& end_time, bool currently_night) {
  if (currently_night) {
    // Currently night mode, next change is end_time
    return end_time;
  } else {
    // Currently day mode, next change is start_time
    return start_time;
  }
}

/**
 * Calculate minutes until next state change
 *
 * @param current_time Current time
 * @param target_time Target time
 * @return Minutes until target time (always positive)
 */
inline int minutes_until(const Time& current_time, const Time& target_time) {
  int current_minutes = current_time.to_minutes();
  int target_minutes = target_time.to_minutes();

  if (target_minutes >= current_minutes) {
    return target_minutes - current_minutes;
  } else {
    // Target is tomorrow
    return (1440 - current_minutes) + target_minutes;
  }
}

/**
 * Validate time is in valid range
 */
inline bool is_valid_time(int hour, int minute) {
  return (hour >= 0 && hour <= 23) && (minute >= 0 && minute <= 59);
}

inline bool is_valid_time(const Time& time) {
  return is_valid_time(time.hour, time.minute);
}

/**
 * Night mode override options
 */
enum NightModeOverride {
  OVERRIDE_AUTO = 0,       // Use time-based logic
  OVERRIDE_FORCE_OFF = 1,  // Always day mode
  OVERRIDE_FORCE_ON = 2    // Always night mode
};

/**
 * Determine if night mode should be active based on time and override
 *
 * @param current_time Current time
 * @param start_time Night mode start time
 * @param end_time Night mode end time
 * @param night_mode_enabled Whether night mode feature is enabled
 * @param override Override setting (auto, force off, force on)
 * @param time_valid Whether time source is valid
 * @return true if night mode should be active
 */
inline bool should_be_night_mode(
    const Time& current_time,
    const Time& start_time,
    const Time& end_time,
    bool night_mode_enabled,
    NightModeOverride override,
    bool time_valid) {

  // Check override first
  if (override == OVERRIDE_FORCE_ON) {
    return true;
  }
  if (override == OVERRIDE_FORCE_OFF) {
    return false;
  }

  // Override is AUTO, check if night mode is enabled
  if (!night_mode_enabled) {
    return false;
  }

  // Check if time is valid
  if (!time_valid) {
    return false;  // Default to day mode if time unavailable
  }

  // Use time-based logic
  return is_within_night_mode(current_time, start_time, end_time);
}

} // namespace time_utils
} // namespace sense360

#include "../include/time_utils.h"
#include <cassert>
#include <iostream>

using namespace sense360::time_utils;

// Test utilities
#define TEST_CASE(name) void test_##name()
#define ASSERT_EQ(a, b) assert((a) == (b))
#define ASSERT_TRUE(a) assert(a)
#define ASSERT_FALSE(a) assert(!(a))

int test_count = 0;
int passed_count = 0;

void run_test(void (*test_func)(), const char* name) {
  test_count++;
  try {
    test_func();
    passed_count++;
    std::cout << "[PASS] " << name << std::endl;
  } catch (const std::exception& e) {
    std::cout << "[FAIL] " << name << ": " << e.what() << std::endl;
  } catch (...) {
    std::cout << "[FAIL] " << name << ": assertion failed" << std::endl;
  }
}

// Test cases

TEST_CASE(time_to_minutes_midnight) {
  Time t(0, 0);
  ASSERT_EQ(t.to_minutes(), 0);
}

TEST_CASE(time_to_minutes_noon) {
  Time t(12, 0);
  ASSERT_EQ(t.to_minutes(), 720);
}

TEST_CASE(time_to_minutes_end_of_day) {
  Time t(23, 59);
  ASSERT_EQ(t.to_minutes(), 1439);
}

TEST_CASE(time_to_minutes_arbitrary) {
  Time t(14, 30);
  ASSERT_EQ(t.to_minutes(), 870);  // 14*60 + 30
}

TEST_CASE(time_from_minutes_midnight) {
  Time t = Time::from_minutes(0);
  ASSERT_EQ(t.hour, 0);
  ASSERT_EQ(t.minute, 0);
}

TEST_CASE(time_from_minutes_noon) {
  Time t = Time::from_minutes(720);
  ASSERT_EQ(t.hour, 12);
  ASSERT_EQ(t.minute, 0);
}

TEST_CASE(time_from_minutes_arbitrary) {
  Time t = Time::from_minutes(870);  // 14:30
  ASSERT_EQ(t.hour, 14);
  ASSERT_EQ(t.minute, 30);
}

TEST_CASE(time_from_minutes_wraps_around) {
  Time t = Time::from_minutes(1440);  // Should wrap to 00:00
  ASSERT_EQ(t.hour, 0);
  ASSERT_EQ(t.minute, 0);
}

TEST_CASE(time_from_minutes_negative_wraps) {
  Time t = Time::from_minutes(-60);  // Should wrap to 23:00
  ASSERT_EQ(t.hour, 23);
  ASSERT_EQ(t.minute, 0);
}

TEST_CASE(is_within_night_mode_same_day_range_inside) {
  Time current(10, 0);
  Time start(8, 0);
  Time end(17, 0);
  ASSERT_TRUE(is_within_night_mode(current, start, end));
}

TEST_CASE(is_within_night_mode_same_day_range_before) {
  Time current(7, 0);
  Time start(8, 0);
  Time end(17, 0);
  ASSERT_FALSE(is_within_night_mode(current, start, end));
}

TEST_CASE(is_within_night_mode_same_day_range_after) {
  Time current(18, 0);
  Time start(8, 0);
  Time end(17, 0);
  ASSERT_FALSE(is_within_night_mode(current, start, end));
}

TEST_CASE(is_within_night_mode_same_day_range_at_start) {
  Time current(8, 0);
  Time start(8, 0);
  Time end(17, 0);
  ASSERT_TRUE(is_within_night_mode(current, start, end));  // Inclusive start
}

TEST_CASE(is_within_night_mode_same_day_range_at_end) {
  Time current(17, 0);
  Time start(8, 0);
  Time end(17, 0);
  ASSERT_FALSE(is_within_night_mode(current, start, end));  // Exclusive end
}

// CRITICAL: Cross-midnight tests
TEST_CASE(is_within_night_mode_cross_midnight_evening) {
  Time current(23, 0);
  Time start(22, 0);
  Time end(7, 0);
  ASSERT_TRUE(is_within_night_mode(current, start, end));  // Evening (after start)
}

TEST_CASE(is_within_night_mode_cross_midnight_morning) {
  Time current(6, 0);
  Time start(22, 0);
  Time end(7, 0);
  ASSERT_TRUE(is_within_night_mode(current, start, end));  // Morning (before end)
}

TEST_CASE(is_within_night_mode_cross_midnight_day) {
  Time current(12, 0);
  Time start(22, 0);
  Time end(7, 0);
  ASSERT_FALSE(is_within_night_mode(current, start, end));  // Daytime
}

TEST_CASE(is_within_night_mode_cross_midnight_at_start) {
  Time current(22, 0);
  Time start(22, 0);
  Time end(7, 0);
  ASSERT_TRUE(is_within_night_mode(current, start, end));  // At start time
}

TEST_CASE(is_within_night_mode_cross_midnight_at_end) {
  Time current(7, 0);
  Time start(22, 0);
  Time end(7, 0);
  ASSERT_FALSE(is_within_night_mode(current, start, end));  // At end time (exclusive)
}

TEST_CASE(is_within_night_mode_cross_midnight_just_before_end) {
  Time current(6, 59);
  Time start(22, 0);
  Time end(7, 0);
  ASSERT_TRUE(is_within_night_mode(current, start, end));
}

TEST_CASE(is_within_night_mode_midnight_itself) {
  Time current(0, 0);
  Time start(22, 0);
  Time end(7, 0);
  ASSERT_TRUE(is_within_night_mode(current, start, end));  // Midnight is in range
}

TEST_CASE(minutes_until_same_hour) {
  Time current(10, 30);
  Time target(10, 45);
  ASSERT_EQ(minutes_until(current, target), 15);
}

TEST_CASE(minutes_until_next_hour) {
  Time current(10, 30);
  Time target(11, 30);
  ASSERT_EQ(minutes_until(current, target), 60);
}

TEST_CASE(minutes_until_next_day) {
  Time current(23, 30);
  Time target(1, 30);
  ASSERT_EQ(minutes_until(current, target), 120);  // 30 min to midnight + 90 min
}

TEST_CASE(minutes_until_target_is_now) {
  Time current(10, 30);
  Time target(10, 30);
  ASSERT_EQ(minutes_until(current, target), 0);
}

TEST_CASE(is_valid_time_valid) {
  ASSERT_TRUE(is_valid_time(0, 0));
  ASSERT_TRUE(is_valid_time(12, 30));
  ASSERT_TRUE(is_valid_time(23, 59));
}

TEST_CASE(is_valid_time_invalid_hour) {
  ASSERT_FALSE(is_valid_time(24, 0));
  ASSERT_FALSE(is_valid_time(-1, 0));
}

TEST_CASE(is_valid_time_invalid_minute) {
  ASSERT_FALSE(is_valid_time(12, 60));
  ASSERT_FALSE(is_valid_time(12, -1));
}

TEST_CASE(is_valid_time_struct) {
  Time valid(12, 30);
  ASSERT_TRUE(is_valid_time(valid));

  Time invalid(25, 0);
  ASSERT_FALSE(is_valid_time(invalid));
}

TEST_CASE(should_be_night_mode_force_on) {
  Time current(12, 0);  // Noon (daytime)
  Time start(22, 0);
  Time end(7, 0);

  bool result = should_be_night_mode(current, start, end, true, OVERRIDE_FORCE_ON, true);
  ASSERT_TRUE(result);  // Forced on regardless of time
}

TEST_CASE(should_be_night_mode_force_off) {
  Time current(23, 0);  // Evening (should be night time)
  Time start(22, 0);
  Time end(7, 0);

  bool result = should_be_night_mode(current, start, end, true, OVERRIDE_FORCE_OFF, true);
  ASSERT_FALSE(result);  // Forced off regardless of time
}

TEST_CASE(should_be_night_mode_auto_disabled) {
  Time current(23, 0);  // Evening (would be night time)
  Time start(22, 0);
  Time end(7, 0);

  bool result = should_be_night_mode(current, start, end, false, OVERRIDE_AUTO, true);
  ASSERT_FALSE(result);  // Night mode disabled
}

TEST_CASE(should_be_night_mode_auto_time_invalid) {
  Time current(23, 0);
  Time start(22, 0);
  Time end(7, 0);

  bool result = should_be_night_mode(current, start, end, true, OVERRIDE_AUTO, false);
  ASSERT_FALSE(result);  // Default to day mode when time invalid
}

TEST_CASE(should_be_night_mode_auto_enabled_in_range) {
  Time current(23, 0);  // Evening
  Time start(22, 0);
  Time end(7, 0);

  bool result = should_be_night_mode(current, start, end, true, OVERRIDE_AUTO, true);
  ASSERT_TRUE(result);  // Should be night mode
}

TEST_CASE(should_be_night_mode_auto_enabled_out_of_range) {
  Time current(12, 0);  // Noon
  Time start(22, 0);
  Time end(7, 0);

  bool result = should_be_night_mode(current, start, end, true, OVERRIDE_AUTO, true);
  ASSERT_FALSE(result);  // Should be day mode
}

// Integration test: Full 24-hour cycle
TEST_CASE(integration_full_24_hour_cycle) {
  Time start(22, 0);  // Night starts at 22:00
  Time end(7, 0);     // Night ends at 07:00

  // Test every hour of the day
  bool expected_night[24] = {
    true,  // 00:00 - in range
    true,  // 01:00
    true,  // 02:00
    true,  // 03:00
    true,  // 04:00
    true,  // 05:00
    true,  // 06:00
    false, // 07:00 - end of night (exclusive)
    false, // 08:00
    false, // 09:00
    false, // 10:00
    false, // 11:00
    false, // 12:00
    false, // 13:00
    false, // 14:00
    false, // 15:00
    false, // 16:00
    false, // 17:00
    false, // 18:00
    false, // 19:00
    false, // 20:00
    false, // 21:00
    true,  // 22:00 - start of night
    true   // 23:00
  };

  for (int hour = 0; hour < 24; hour++) {
    Time current(hour, 0);
    bool is_night = is_within_night_mode(current, start, end);
    if (is_night != expected_night[hour]) {
      std::cout << "FAIL at hour " << hour << ": expected " << expected_night[hour] << " got " << is_night << std::endl;
      assert(false);
    }
  }
}

// Integration test: Same-day range
TEST_CASE(integration_same_day_range) {
  Time start(8, 0);   // Range: 08:00 to 17:00
  Time end(17, 0);

  ASSERT_FALSE(is_within_night_mode(Time(7, 59), start, end));
  ASSERT_TRUE(is_within_night_mode(Time(8, 0), start, end));
  ASSERT_TRUE(is_within_night_mode(Time(12, 0), start, end));
  ASSERT_TRUE(is_within_night_mode(Time(16, 59), start, end));
  ASSERT_FALSE(is_within_night_mode(Time(17, 0), start, end));
  ASSERT_FALSE(is_within_night_mode(Time(18, 0), start, end));
}

int main() {
  std::cout << "Running time utils tests..." << std::endl;
  std::cout << "=====================================" << std::endl;

  // Time conversion tests
  run_test(test_time_to_minutes_midnight, "time_to_minutes_midnight");
  run_test(test_time_to_minutes_noon, "time_to_minutes_noon");
  run_test(test_time_to_minutes_end_of_day, "time_to_minutes_end_of_day");
  run_test(test_time_to_minutes_arbitrary, "time_to_minutes_arbitrary");
  run_test(test_time_from_minutes_midnight, "time_from_minutes_midnight");
  run_test(test_time_from_minutes_noon, "time_from_minutes_noon");
  run_test(test_time_from_minutes_arbitrary, "time_from_minutes_arbitrary");
  run_test(test_time_from_minutes_wraps_around, "time_from_minutes_wraps_around");
  run_test(test_time_from_minutes_negative_wraps, "time_from_minutes_negative_wraps");

  // Same-day range tests
  run_test(test_is_within_night_mode_same_day_range_inside, "is_within_night_mode_same_day_range_inside");
  run_test(test_is_within_night_mode_same_day_range_before, "is_within_night_mode_same_day_range_before");
  run_test(test_is_within_night_mode_same_day_range_after, "is_within_night_mode_same_day_range_after");
  run_test(test_is_within_night_mode_same_day_range_at_start, "is_within_night_mode_same_day_range_at_start");
  run_test(test_is_within_night_mode_same_day_range_at_end, "is_within_night_mode_same_day_range_at_end");

  // Cross-midnight tests (CRITICAL)
  run_test(test_is_within_night_mode_cross_midnight_evening, "is_within_night_mode_cross_midnight_evening");
  run_test(test_is_within_night_mode_cross_midnight_morning, "is_within_night_mode_cross_midnight_morning");
  run_test(test_is_within_night_mode_cross_midnight_day, "is_within_night_mode_cross_midnight_day");
  run_test(test_is_within_night_mode_cross_midnight_at_start, "is_within_night_mode_cross_midnight_at_start");
  run_test(test_is_within_night_mode_cross_midnight_at_end, "is_within_night_mode_cross_midnight_at_end");
  run_test(test_is_within_night_mode_cross_midnight_just_before_end, "is_within_night_mode_cross_midnight_just_before_end");
  run_test(test_is_within_night_mode_midnight_itself, "is_within_night_mode_midnight_itself");

  // Minutes until tests
  run_test(test_minutes_until_same_hour, "minutes_until_same_hour");
  run_test(test_minutes_until_next_hour, "minutes_until_next_hour");
  run_test(test_minutes_until_next_day, "minutes_until_next_day");
  run_test(test_minutes_until_target_is_now, "minutes_until_target_is_now");

  // Validation tests
  run_test(test_is_valid_time_valid, "is_valid_time_valid");
  run_test(test_is_valid_time_invalid_hour, "is_valid_time_invalid_hour");
  run_test(test_is_valid_time_invalid_minute, "is_valid_time_invalid_minute");
  run_test(test_is_valid_time_struct, "is_valid_time_struct");

  // Override tests
  run_test(test_should_be_night_mode_force_on, "should_be_night_mode_force_on");
  run_test(test_should_be_night_mode_force_off, "should_be_night_mode_force_off");
  run_test(test_should_be_night_mode_auto_disabled, "should_be_night_mode_auto_disabled");
  run_test(test_should_be_night_mode_auto_time_invalid, "should_be_night_mode_auto_time_invalid");
  run_test(test_should_be_night_mode_auto_enabled_in_range, "should_be_night_mode_auto_enabled_in_range");
  run_test(test_should_be_night_mode_auto_enabled_out_of_range, "should_be_night_mode_auto_enabled_out_of_range");

  // Integration tests
  run_test(test_integration_full_24_hour_cycle, "integration_full_24_hour_cycle");
  run_test(test_integration_same_day_range, "integration_same_day_range");

  std::cout << "=====================================" << std::endl;
  std::cout << "Results: " << passed_count << "/" << test_count << " tests passed" << std::endl;

  return (passed_count == test_count) ? 0 : 1;
}

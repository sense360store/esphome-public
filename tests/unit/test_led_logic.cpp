#include "../include/led_logic.h"
#include <cassert>
#include <cmath>
#include <iostream>
#include <sstream>

using namespace sense360::led;

// Test utilities
#define TEST_CASE(name) void test_##name()
#define ASSERT_EQ(a, b) assert((a) == (b))
#define ASSERT_TRUE(a) assert(a)
#define ASSERT_FALSE(a) assert(!(a))
#define ASSERT_NEAR(a, b, epsilon) assert(std::abs((a) - (b)) < (epsilon))

// Helper to print test results
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

TEST_CASE(color_for_severity_unknown) {
  Color c = color_for_severity(LEVEL_UNKNOWN);
  ASSERT_EQ(c.red, 24);
  ASSERT_EQ(c.green, 32);
  ASSERT_EQ(c.blue, 64);
}

TEST_CASE(color_for_severity_good) {
  Color c = color_for_severity(LEVEL_GOOD);
  ASSERT_EQ(c.red, 0);
  ASSERT_EQ(c.green, 255);
  ASSERT_EQ(c.blue, 0);
}

TEST_CASE(color_for_severity_moderate) {
  Color c = color_for_severity(LEVEL_MODERATE);
  ASSERT_EQ(c.red, 255);
  ASSERT_EQ(c.green, 128);
  ASSERT_EQ(c.blue, 0);
}

TEST_CASE(color_for_severity_unhealthy) {
  Color c = color_for_severity(LEVEL_UNHEALTHY);
  ASSERT_EQ(c.red, 255);
  ASSERT_EQ(c.green, 0);
  ASSERT_EQ(c.blue, 0);
}

TEST_CASE(color_for_severity_poor) {
  Color c = color_for_severity(LEVEL_POOR);
  ASSERT_EQ(c.red, 128);
  ASSERT_EQ(c.green, 0);
  ASSERT_EQ(c.blue, 255);
}

TEST_CASE(scale_color_full_brightness) {
  Color c = Color(255, 128, 64);
  Color scaled = scale_color(c, 1.0f);
  ASSERT_EQ(scaled.red, 255);
  ASSERT_EQ(scaled.green, 128);
  ASSERT_EQ(scaled.blue, 64);
}

TEST_CASE(scale_color_half_brightness) {
  Color c = Color(200, 100, 50);
  Color scaled = scale_color(c, 0.5f);
  ASSERT_EQ(scaled.red, 100);
  ASSERT_EQ(scaled.green, 50);
  ASSERT_EQ(scaled.blue, 25);
}

TEST_CASE(scale_color_zero_brightness) {
  Color c = Color(255, 128, 64);
  Color scaled = scale_color(c, 0.0f);
  ASSERT_EQ(scaled.red, 0);
  ASSERT_EQ(scaled.green, 0);
  ASSERT_EQ(scaled.blue, 0);
}

TEST_CASE(scale_color_clamps_negative) {
  Color c = Color(100, 50, 25);
  Color scaled = scale_color(c, -0.5f);  // Should clamp to 0.0
  ASSERT_EQ(scaled.red, 0);
  ASSERT_EQ(scaled.green, 0);
  ASSERT_EQ(scaled.blue, 0);
}

TEST_CASE(scale_color_clamps_over_one) {
  Color c = Color(100, 50, 25);
  Color scaled = scale_color(c, 2.0f);  // Should clamp to 1.0
  ASSERT_EQ(scaled.red, 100);
  ASSERT_EQ(scaled.green, 50);
  ASSERT_EQ(scaled.blue, 25);
}

TEST_CASE(compute_level_good) {
  int level = compute_level(5.0f, 10.0f, 25.0f, 50.0f);
  ASSERT_EQ(level, LEVEL_GOOD);
}

TEST_CASE(compute_level_moderate) {
  int level = compute_level(15.0f, 10.0f, 25.0f, 50.0f);
  ASSERT_EQ(level, LEVEL_MODERATE);
}

TEST_CASE(compute_level_unhealthy) {
  int level = compute_level(30.0f, 10.0f, 25.0f, 50.0f);
  ASSERT_EQ(level, LEVEL_UNHEALTHY);
}

TEST_CASE(compute_level_poor) {
  int level = compute_level(60.0f, 10.0f, 25.0f, 50.0f);
  ASSERT_EQ(level, LEVEL_POOR);
}

TEST_CASE(compute_level_nan) {
  int level = compute_level(NAN, 10.0f, 25.0f, 50.0f);
  ASSERT_EQ(level, LEVEL_UNKNOWN);
}

// CRITICAL: Test boundary conditions (off-by-one errors)
TEST_CASE(compute_level_exactly_at_good_threshold) {
  int level = compute_level(10.0f, 10.0f, 25.0f, 50.0f);
  ASSERT_EQ(level, LEVEL_MODERATE);  // value >= threshold is not good
}

TEST_CASE(compute_level_exactly_at_moderate_threshold) {
  int level = compute_level(25.0f, 10.0f, 25.0f, 50.0f);
  ASSERT_EQ(level, LEVEL_UNHEALTHY);  // value >= threshold is not moderate
}

TEST_CASE(compute_level_exactly_at_unhealthy_threshold) {
  int level = compute_level(50.0f, 10.0f, 25.0f, 50.0f);
  ASSERT_EQ(level, LEVEL_POOR);  // value >= threshold is poor
}

TEST_CASE(compute_level_just_below_good_threshold) {
  int level = compute_level(9.99f, 10.0f, 25.0f, 50.0f);
  ASSERT_EQ(level, LEVEL_GOOD);
}

TEST_CASE(brightness_scale_for_level_good) {
  float scale = brightness_scale_for_level(LEVEL_GOOD);
  ASSERT_NEAR(scale, 0.40f, 0.01f);
}

TEST_CASE(brightness_scale_for_level_moderate) {
  float scale = brightness_scale_for_level(LEVEL_MODERATE);
  ASSERT_NEAR(scale, 0.60f, 0.01f);
}

TEST_CASE(brightness_scale_for_level_unhealthy) {
  float scale = brightness_scale_for_level(LEVEL_UNHEALTHY);
  ASSERT_NEAR(scale, 0.80f, 0.01f);
}

TEST_CASE(brightness_scale_for_level_poor) {
  float scale = brightness_scale_for_level(LEVEL_POOR);
  ASSERT_NEAR(scale, 1.00f, 0.01f);
}

TEST_CASE(brightness_scale_for_level_unknown) {
  float scale = brightness_scale_for_level(LEVEL_UNKNOWN);
  ASSERT_NEAR(scale, 1.00f, 0.01f);  // Default to full brightness
}

TEST_CASE(compute_pulse_multiplier_at_zero) {
  float pulse = compute_pulse_multiplier(0);
  ASSERT_TRUE(pulse >= 0.90f && pulse <= 1.00f);
}

TEST_CASE(compute_pulse_multiplier_at_half_cycle) {
  float pulse = compute_pulse_multiplier(2500);  // Half of 5000ms
  ASSERT_TRUE(pulse >= 0.90f && pulse <= 1.00f);
}

TEST_CASE(compute_pulse_multiplier_bounds) {
  // Test various points in the cycle
  for (unsigned long t = 0; t < 10000; t += 100) {
    float pulse = compute_pulse_multiplier(t);
    ASSERT_TRUE(pulse >= 0.89f && pulse <= 1.01f);  // Allow small float error
  }
}

TEST_CASE(aggregate_pm_levels_all_good) {
  int level = aggregate_pm_levels(LEVEL_GOOD, LEVEL_GOOD, LEVEL_GOOD, LEVEL_GOOD);
  ASSERT_EQ(level, LEVEL_GOOD);
}

TEST_CASE(aggregate_pm_levels_one_moderate) {
  int level = aggregate_pm_levels(LEVEL_GOOD, LEVEL_MODERATE, LEVEL_GOOD, LEVEL_GOOD);
  ASSERT_EQ(level, LEVEL_MODERATE);
}

TEST_CASE(aggregate_pm_levels_worst_case) {
  int level = aggregate_pm_levels(LEVEL_GOOD, LEVEL_MODERATE, LEVEL_UNHEALTHY, LEVEL_POOR);
  ASSERT_EQ(level, LEVEL_POOR);
}

TEST_CASE(aggregate_pm_levels_with_unknown) {
  int level = aggregate_pm_levels(LEVEL_UNKNOWN, LEVEL_MODERATE, LEVEL_GOOD, LEVEL_UNKNOWN);
  ASSERT_EQ(level, LEVEL_MODERATE);  // Should take worst non-unknown
}

TEST_CASE(compute_overall_severity_all_good) {
  int level = compute_overall_severity(LEVEL_GOOD, LEVEL_GOOD, LEVEL_GOOD, LEVEL_GOOD);
  ASSERT_EQ(level, LEVEL_GOOD);
}

TEST_CASE(compute_overall_severity_mixed) {
  int level = compute_overall_severity(LEVEL_MODERATE, LEVEL_GOOD, LEVEL_UNHEALTHY, LEVEL_GOOD);
  ASSERT_EQ(level, LEVEL_UNHEALTHY);
}

TEST_CASE(compute_overall_severity_worst_case) {
  int level = compute_overall_severity(LEVEL_POOR, LEVEL_MODERATE, LEVEL_UNHEALTHY, LEVEL_GOOD);
  ASSERT_EQ(level, LEVEL_POOR);
}

// Main test runner
int main() {
  std::cout << "Running LED logic tests..." << std::endl;
  std::cout << "=====================================" << std::endl;

  // Color mapping tests
  run_test(test_color_for_severity_unknown, "color_for_severity_unknown");
  run_test(test_color_for_severity_good, "color_for_severity_good");
  run_test(test_color_for_severity_moderate, "color_for_severity_moderate");
  run_test(test_color_for_severity_unhealthy, "color_for_severity_unhealthy");
  run_test(test_color_for_severity_poor, "color_for_severity_poor");

  // Color scaling tests
  run_test(test_scale_color_full_brightness, "scale_color_full_brightness");
  run_test(test_scale_color_half_brightness, "scale_color_half_brightness");
  run_test(test_scale_color_zero_brightness, "scale_color_zero_brightness");
  run_test(test_scale_color_clamps_negative, "scale_color_clamps_negative");
  run_test(test_scale_color_clamps_over_one, "scale_color_clamps_over_one");

  // Level computation tests
  run_test(test_compute_level_good, "compute_level_good");
  run_test(test_compute_level_moderate, "compute_level_moderate");
  run_test(test_compute_level_unhealthy, "compute_level_unhealthy");
  run_test(test_compute_level_poor, "compute_level_poor");
  run_test(test_compute_level_nan, "compute_level_nan");

  // Boundary condition tests (CRITICAL)
  run_test(test_compute_level_exactly_at_good_threshold, "compute_level_exactly_at_good_threshold");
  run_test(test_compute_level_exactly_at_moderate_threshold, "compute_level_exactly_at_moderate_threshold");
  run_test(test_compute_level_exactly_at_unhealthy_threshold, "compute_level_exactly_at_unhealthy_threshold");
  run_test(test_compute_level_just_below_good_threshold, "compute_level_just_below_good_threshold");

  // Brightness scaling tests
  run_test(test_brightness_scale_for_level_good, "brightness_scale_for_level_good");
  run_test(test_brightness_scale_for_level_moderate, "brightness_scale_for_level_moderate");
  run_test(test_brightness_scale_for_level_unhealthy, "brightness_scale_for_level_unhealthy");
  run_test(test_brightness_scale_for_level_poor, "brightness_scale_for_level_poor");
  run_test(test_brightness_scale_for_level_unknown, "brightness_scale_for_level_unknown");

  // Pulse tests
  run_test(test_compute_pulse_multiplier_at_zero, "compute_pulse_multiplier_at_zero");
  run_test(test_compute_pulse_multiplier_at_half_cycle, "compute_pulse_multiplier_at_half_cycle");
  run_test(test_compute_pulse_multiplier_bounds, "compute_pulse_multiplier_bounds");

  // Aggregation tests
  run_test(test_aggregate_pm_levels_all_good, "aggregate_pm_levels_all_good");
  run_test(test_aggregate_pm_levels_one_moderate, "aggregate_pm_levels_one_moderate");
  run_test(test_aggregate_pm_levels_worst_case, "aggregate_pm_levels_worst_case");
  run_test(test_aggregate_pm_levels_with_unknown, "aggregate_pm_levels_with_unknown");

  // Overall severity tests
  run_test(test_compute_overall_severity_all_good, "compute_overall_severity_all_good");
  run_test(test_compute_overall_severity_mixed, "compute_overall_severity_mixed");
  run_test(test_compute_overall_severity_worst_case, "compute_overall_severity_worst_case");

  std::cout << "=====================================" << std::endl;
  std::cout << "Results: " << passed_count << "/" << test_count << " tests passed" << std::endl;

  return (passed_count == test_count) ? 0 : 1;
}

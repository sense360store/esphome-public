#include "../../include/sense360/thresholds.h"
#include <cassert>
#include <cmath>
#include <iostream>
#include <cstring>

using namespace sense360::thresholds;

// Test utilities
#define TEST_CASE(name) void test_##name()
#define ASSERT_EQ(a, b) assert((a) == (b))
#define ASSERT_TRUE(a) assert(a)
#define ASSERT_FALSE(a) assert(!(a))
#define ASSERT_NEAR(a, b, epsilon) assert(std::abs((a) - (b)) < (epsilon))
#define ASSERT_STR_EQ(a, b) assert(std::strcmp((a), (b)) == 0)

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

TEST_CASE(status_to_string_conversions) {
  ASSERT_STR_EQ(status_to_string(STATUS_GOOD), "Good");
  ASSERT_STR_EQ(status_to_string(STATUS_MODERATE), "Moderate");
  ASSERT_STR_EQ(status_to_string(STATUS_UNHEALTHY), "Unhealthy");
  ASSERT_STR_EQ(status_to_string(STATUS_POOR), "Poor");
  ASSERT_STR_EQ(status_to_string(STATUS_UNKNOWN), "Unknown");
}

TEST_CASE(classify_value_good) {
  AirQualityStatus status = classify_value(5.0f, 10.0f, 25.0f, 50.0f);
  ASSERT_EQ(status, STATUS_GOOD);
}

TEST_CASE(classify_value_moderate) {
  AirQualityStatus status = classify_value(15.0f, 10.0f, 25.0f, 50.0f);
  ASSERT_EQ(status, STATUS_MODERATE);
}

TEST_CASE(classify_value_unhealthy) {
  AirQualityStatus status = classify_value(30.0f, 10.0f, 25.0f, 50.0f);
  ASSERT_EQ(status, STATUS_UNHEALTHY);
}

TEST_CASE(classify_value_poor) {
  AirQualityStatus status = classify_value(60.0f, 10.0f, 25.0f, 50.0f);
  ASSERT_EQ(status, STATUS_POOR);
}

TEST_CASE(classify_value_nan) {
  AirQualityStatus status = classify_value(NAN, 10.0f, 25.0f, 50.0f);
  ASSERT_EQ(status, STATUS_UNKNOWN);
}

// CRITICAL: Boundary condition tests
TEST_CASE(classify_value_exactly_at_good_threshold) {
  // value == good_threshold should be MODERATE, not GOOD
  AirQualityStatus status = classify_value(10.0f, 10.0f, 25.0f, 50.0f);
  ASSERT_EQ(status, STATUS_MODERATE);
}

TEST_CASE(classify_value_exactly_at_moderate_threshold) {
  // value == moderate_threshold should be UNHEALTHY, not MODERATE
  AirQualityStatus status = classify_value(25.0f, 10.0f, 25.0f, 50.0f);
  ASSERT_EQ(status, STATUS_UNHEALTHY);
}

TEST_CASE(classify_value_exactly_at_unhealthy_threshold) {
  // value == unhealthy_threshold should be POOR, not UNHEALTHY
  AirQualityStatus status = classify_value(50.0f, 10.0f, 25.0f, 50.0f);
  ASSERT_EQ(status, STATUS_POOR);
}

TEST_CASE(classify_value_just_below_good_threshold) {
  AirQualityStatus status = classify_value(9.99f, 10.0f, 25.0f, 50.0f);
  ASSERT_EQ(status, STATUS_GOOD);
}

TEST_CASE(classify_value_just_above_good_threshold) {
  AirQualityStatus status = classify_value(10.01f, 10.0f, 25.0f, 50.0f);
  ASSERT_EQ(status, STATUS_MODERATE);
}

// Test with real sensor thresholds
TEST_CASE(classify_pm25_with_real_thresholds) {
  // PM2.5: Good < 10, Moderate < 25, Unhealthy < 50
  ASSERT_EQ(classify_value(5.0f, PM25_GOOD, PM25_MODERATE, PM25_UNHEALTHY), STATUS_GOOD);
  ASSERT_EQ(classify_value(15.0f, PM25_GOOD, PM25_MODERATE, PM25_UNHEALTHY), STATUS_MODERATE);
  ASSERT_EQ(classify_value(35.0f, PM25_GOOD, PM25_MODERATE, PM25_UNHEALTHY), STATUS_UNHEALTHY);
  ASSERT_EQ(classify_value(75.0f, PM25_GOOD, PM25_MODERATE, PM25_UNHEALTHY), STATUS_POOR);
}

TEST_CASE(classify_voc_with_real_thresholds) {
  // VOC: Good < 80, Moderate < 150, Unhealthy < 250
  ASSERT_EQ(classify_value(50.0f, VOC_GOOD, VOC_MODERATE, VOC_UNHEALTHY), STATUS_GOOD);
  ASSERT_EQ(classify_value(100.0f, VOC_GOOD, VOC_MODERATE, VOC_UNHEALTHY), STATUS_MODERATE);
  ASSERT_EQ(classify_value(200.0f, VOC_GOOD, VOC_MODERATE, VOC_UNHEALTHY), STATUS_UNHEALTHY);
  ASSERT_EQ(classify_value(300.0f, VOC_GOOD, VOC_MODERATE, VOC_UNHEALTHY), STATUS_POOR);
}

TEST_CASE(classify_co2_with_real_thresholds) {
  // CO2: Good < 750, Moderate < 1000, Unhealthy < 1500
  ASSERT_EQ(classify_value(600.0f, CO2_GOOD, CO2_MODERATE, CO2_UNHEALTHY), STATUS_GOOD);
  ASSERT_EQ(classify_value(850.0f, CO2_GOOD, CO2_MODERATE, CO2_UNHEALTHY), STATUS_MODERATE);
  ASSERT_EQ(classify_value(1200.0f, CO2_GOOD, CO2_MODERATE, CO2_UNHEALTHY), STATUS_UNHEALTHY);
  ASSERT_EQ(classify_value(2000.0f, CO2_GOOD, CO2_MODERATE, CO2_UNHEALTHY), STATUS_POOR);
}

TEST_CASE(get_worst_status_two_good) {
  AirQualityStatus worst = get_worst_status(STATUS_GOOD, STATUS_GOOD);
  ASSERT_EQ(worst, STATUS_GOOD);
}

TEST_CASE(get_worst_status_two_mixed) {
  AirQualityStatus worst = get_worst_status(STATUS_GOOD, STATUS_MODERATE);
  ASSERT_EQ(worst, STATUS_MODERATE);
}

TEST_CASE(get_worst_status_two_with_unknown) {
  // Unknown should not affect worst calculation
  AirQualityStatus worst = get_worst_status(STATUS_UNKNOWN, STATUS_MODERATE);
  ASSERT_EQ(worst, STATUS_MODERATE);
}

TEST_CASE(get_worst_status_two_both_unknown) {
  AirQualityStatus worst = get_worst_status(STATUS_UNKNOWN, STATUS_UNKNOWN);
  ASSERT_EQ(worst, STATUS_UNKNOWN);
}

TEST_CASE(get_worst_status_three_all_good) {
  AirQualityStatus worst = get_worst_status(STATUS_GOOD, STATUS_GOOD, STATUS_GOOD);
  ASSERT_EQ(worst, STATUS_GOOD);
}

TEST_CASE(get_worst_status_three_one_poor) {
  AirQualityStatus worst = get_worst_status(STATUS_GOOD, STATUS_MODERATE, STATUS_POOR);
  ASSERT_EQ(worst, STATUS_POOR);
}

TEST_CASE(get_worst_status_four_all_different) {
  AirQualityStatus worst = get_worst_status(STATUS_GOOD, STATUS_MODERATE, STATUS_UNHEALTHY, STATUS_POOR);
  ASSERT_EQ(worst, STATUS_POOR);
}

TEST_CASE(get_worst_status_four_with_unknowns) {
  AirQualityStatus worst = get_worst_status(STATUS_UNKNOWN, STATUS_MODERATE, STATUS_UNKNOWN, STATUS_UNHEALTHY);
  ASSERT_EQ(worst, STATUS_UNHEALTHY);
}

TEST_CASE(preserve_last_valid_current_valid) {
  float result = preserve_last_valid(25.0f, 20.0f, 15.0f);
  ASSERT_NEAR(result, 25.0f, 0.01f);  // Should use current value
}

TEST_CASE(preserve_last_valid_current_nan_use_last) {
  float result = preserve_last_valid(NAN, 20.0f, 15.0f);
  ASSERT_NEAR(result, 20.0f, 0.01f);  // Should use last valid
}

TEST_CASE(preserve_last_valid_both_nan_use_fallback) {
  float result = preserve_last_valid(NAN, NAN, 15.0f);
  ASSERT_NEAR(result, 15.0f, 0.01f);  // Should use fallback
}

TEST_CASE(preserve_last_valid_all_nan) {
  float result = preserve_last_valid(NAN, NAN, NAN);
  ASSERT_TRUE(std::isnan(result));  // Should return NaN
}

TEST_CASE(update_last_valid_with_valid_current) {
  float new_last = update_last_valid(25.0f, 20.0f);
  ASSERT_NEAR(new_last, 25.0f, 0.01f);  // Should update to current
}

TEST_CASE(update_last_valid_with_nan_current) {
  float new_last = update_last_valid(NAN, 20.0f);
  ASSERT_NEAR(new_last, 20.0f, 0.01f);  // Should keep last valid
}

TEST_CASE(update_last_valid_both_nan) {
  float new_last = update_last_valid(NAN, NAN);
  ASSERT_TRUE(std::isnan(new_last));  // Should remain NaN
}

// Integration test: CO2 sensor heating up scenario
TEST_CASE(integration_co2_heating_up_scenario) {
  // Simulate CO2 sensor lifecycle:
  // 1. Heating up (returns NaN)
  // 2. First valid reading
  // 3. Continues normal operation
  // 4. Temporary glitch (NaN)
  // 5. Recovery

  float last_valid = NAN;
  float fallback = 400.0f;  // Outdoor ambient CO2

  // Step 1: Heating up - use fallback
  float display = preserve_last_valid(NAN, last_valid, fallback);
  ASSERT_NEAR(display, 400.0f, 0.01f);
  last_valid = update_last_valid(NAN, last_valid);

  // Step 2: First valid reading
  float current = 650.0f;
  display = preserve_last_valid(current, last_valid, fallback);
  ASSERT_NEAR(display, 650.0f, 0.01f);
  last_valid = update_last_valid(current, last_valid);

  // Step 3: Normal operation
  current = 720.0f;
  display = preserve_last_valid(current, last_valid, fallback);
  ASSERT_NEAR(display, 720.0f, 0.01f);
  last_valid = update_last_valid(current, last_valid);

  // Step 4: Temporary glitch - preserve last valid
  display = preserve_last_valid(NAN, last_valid, fallback);
  ASSERT_NEAR(display, 720.0f, 0.01f);  // Should show last valid, not fallback
  last_valid = update_last_valid(NAN, last_valid);

  // Step 5: Recovery
  current = 740.0f;
  display = preserve_last_valid(current, last_valid, fallback);
  ASSERT_NEAR(display, 740.0f, 0.01f);
}

int main() {
  std::cout << "Running threshold tests..." << std::endl;
  std::cout << "=====================================" << std::endl;

  // Status string tests
  run_test(test_status_to_string_conversions, "status_to_string_conversions");

  // Classification tests
  run_test(test_classify_value_good, "classify_value_good");
  run_test(test_classify_value_moderate, "classify_value_moderate");
  run_test(test_classify_value_unhealthy, "classify_value_unhealthy");
  run_test(test_classify_value_poor, "classify_value_poor");
  run_test(test_classify_value_nan, "classify_value_nan");

  // Boundary condition tests (CRITICAL)
  run_test(test_classify_value_exactly_at_good_threshold, "classify_value_exactly_at_good_threshold");
  run_test(test_classify_value_exactly_at_moderate_threshold, "classify_value_exactly_at_moderate_threshold");
  run_test(test_classify_value_exactly_at_unhealthy_threshold, "classify_value_exactly_at_unhealthy_threshold");
  run_test(test_classify_value_just_below_good_threshold, "classify_value_just_below_good_threshold");
  run_test(test_classify_value_just_above_good_threshold, "classify_value_just_above_good_threshold");

  // Real threshold tests
  run_test(test_classify_pm25_with_real_thresholds, "classify_pm25_with_real_thresholds");
  run_test(test_classify_voc_with_real_thresholds, "classify_voc_with_real_thresholds");
  run_test(test_classify_co2_with_real_thresholds, "classify_co2_with_real_thresholds");

  // Worst status tests
  run_test(test_get_worst_status_two_good, "get_worst_status_two_good");
  run_test(test_get_worst_status_two_mixed, "get_worst_status_two_mixed");
  run_test(test_get_worst_status_two_with_unknown, "get_worst_status_two_with_unknown");
  run_test(test_get_worst_status_two_both_unknown, "get_worst_status_two_both_unknown");
  run_test(test_get_worst_status_three_all_good, "get_worst_status_three_all_good");
  run_test(test_get_worst_status_three_one_poor, "get_worst_status_three_one_poor");
  run_test(test_get_worst_status_four_all_different, "get_worst_status_four_all_different");
  run_test(test_get_worst_status_four_with_unknowns, "get_worst_status_four_with_unknowns");

  // Last valid value tests
  run_test(test_preserve_last_valid_current_valid, "preserve_last_valid_current_valid");
  run_test(test_preserve_last_valid_current_nan_use_last, "preserve_last_valid_current_nan_use_last");
  run_test(test_preserve_last_valid_both_nan_use_fallback, "preserve_last_valid_both_nan_use_fallback");
  run_test(test_preserve_last_valid_all_nan, "preserve_last_valid_all_nan");
  run_test(test_update_last_valid_with_valid_current, "update_last_valid_with_valid_current");
  run_test(test_update_last_valid_with_nan_current, "update_last_valid_with_nan_current");
  run_test(test_update_last_valid_both_nan, "update_last_valid_both_nan");

  // Integration test
  run_test(test_integration_co2_heating_up_scenario, "integration_co2_heating_up_scenario");

  std::cout << "=====================================" << std::endl;
  std::cout << "Results: " << passed_count << "/" << test_count << " tests passed" << std::endl;

  return (passed_count == test_count) ? 0 : 1;
}

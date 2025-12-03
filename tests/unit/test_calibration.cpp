#include "../../include/sense360/calibration.h"
#include <cassert>
#include <cmath>
#include <iostream>

using namespace sense360::calibration;

// Test utilities
#define TEST_CASE(name) void test_##name()
#define ASSERT_EQ(a, b) assert((a) == (b))
#define ASSERT_TRUE(a) assert(a)
#define ASSERT_FALSE(a) assert(!(a))
#define ASSERT_NEAR(a, b, epsilon) assert(std::abs((a) - (b)) < (epsilon))

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

TEST_CASE(compute_calibration_simple_positive_offset) {
  // Reference is 25°C, raw is 23°C -> offset = +2°C
  // Reference is 60%RH, raw is 55%RH -> offset = +5%RH
  CalibrationResult result = compute_single_point_calibration(25.0f, 60.0f, 23.0f, 55.0f);

  ASSERT_TRUE(result.valid);
  ASSERT_NEAR(result.temperature_offset, 2.0f, 0.01f);
  ASSERT_NEAR(result.humidity_offset, 5.0f, 0.01f);
}

TEST_CASE(compute_calibration_simple_negative_offset) {
  // Reference is 20°C, raw is 22°C -> offset = -2°C
  // Reference is 50%RH, raw is 58%RH -> offset = -8%RH
  CalibrationResult result = compute_single_point_calibration(20.0f, 50.0f, 22.0f, 58.0f);

  ASSERT_TRUE(result.valid);
  ASSERT_NEAR(result.temperature_offset, -2.0f, 0.01f);
  ASSERT_NEAR(result.humidity_offset, -8.0f, 0.01f);
}

TEST_CASE(compute_calibration_zero_offset) {
  // Reference equals raw -> offset = 0
  CalibrationResult result = compute_single_point_calibration(22.5f, 45.0f, 22.5f, 45.0f);

  ASSERT_TRUE(result.valid);
  ASSERT_NEAR(result.temperature_offset, 0.0f, 0.01f);
  ASSERT_NEAR(result.humidity_offset, 0.0f, 0.01f);
}

TEST_CASE(compute_calibration_clamps_temp_high) {
  // Offset would be +40°C, should clamp to +30°C
  CalibrationResult result = compute_single_point_calibration(60.0f, 50.0f, 20.0f, 50.0f);

  ASSERT_TRUE(result.valid);
  ASSERT_NEAR(result.temperature_offset, 30.0f, 0.01f);  // Clamped
  ASSERT_NEAR(result.humidity_offset, 0.0f, 0.01f);
}

TEST_CASE(compute_calibration_clamps_temp_low) {
  // Offset would be -40°C, should clamp to -30°C
  CalibrationResult result = compute_single_point_calibration(-20.0f, 50.0f, 20.0f, 50.0f);

  ASSERT_TRUE(result.valid);
  ASSERT_NEAR(result.temperature_offset, -30.0f, 0.01f);  // Clamped
  ASSERT_NEAR(result.humidity_offset, 0.0f, 0.01f);
}

TEST_CASE(compute_calibration_clamps_humidity_high) {
  // Offset would be +70%RH, should clamp to +50%RH
  CalibrationResult result = compute_single_point_calibration(25.0f, 90.0f, 25.0f, 20.0f);

  ASSERT_TRUE(result.valid);
  ASSERT_NEAR(result.temperature_offset, 0.0f, 0.01f);
  ASSERT_NEAR(result.humidity_offset, 50.0f, 0.01f);  // Clamped
}

TEST_CASE(compute_calibration_clamps_humidity_low) {
  // Offset would be -70%RH, should clamp to -50%RH
  CalibrationResult result = compute_single_point_calibration(25.0f, 10.0f, 25.0f, 80.0f);

  ASSERT_TRUE(result.valid);
  ASSERT_NEAR(result.temperature_offset, 0.0f, 0.01f);
  ASSERT_NEAR(result.humidity_offset, -50.0f, 0.01f);  // Clamped
}

TEST_CASE(compute_calibration_nan_reference_temp) {
  CalibrationResult result = compute_single_point_calibration(NAN, 50.0f, 22.0f, 45.0f);
  ASSERT_FALSE(result.valid);
}

TEST_CASE(compute_calibration_nan_reference_humidity) {
  CalibrationResult result = compute_single_point_calibration(22.0f, NAN, 22.0f, 45.0f);
  ASSERT_FALSE(result.valid);
}

TEST_CASE(compute_calibration_nan_raw_temp) {
  CalibrationResult result = compute_single_point_calibration(22.0f, 50.0f, NAN, 45.0f);
  ASSERT_FALSE(result.valid);
}

TEST_CASE(compute_calibration_nan_raw_humidity) {
  CalibrationResult result = compute_single_point_calibration(22.0f, 50.0f, 22.0f, NAN);
  ASSERT_FALSE(result.valid);
}

TEST_CASE(apply_temperature_calibration_normal) {
  float calibrated = apply_temperature_calibration(20.0f, 2.5f);
  ASSERT_NEAR(calibrated, 22.5f, 0.01f);
}

TEST_CASE(apply_temperature_calibration_negative_offset) {
  float calibrated = apply_temperature_calibration(25.0f, -3.0f);
  ASSERT_NEAR(calibrated, 22.0f, 0.01f);
}

TEST_CASE(apply_temperature_calibration_nan) {
  float calibrated = apply_temperature_calibration(NAN, 2.0f);
  ASSERT_TRUE(std::isnan(calibrated));
}

TEST_CASE(apply_humidity_calibration_normal) {
  float calibrated = apply_humidity_calibration(45.0f, 5.0f);
  ASSERT_NEAR(calibrated, 50.0f, 0.01f);
}

TEST_CASE(apply_humidity_calibration_clamps_at_100) {
  float calibrated = apply_humidity_calibration(95.0f, 10.0f);
  ASSERT_NEAR(calibrated, 100.0f, 0.01f);  // Should clamp to 100
}

TEST_CASE(apply_humidity_calibration_clamps_at_0) {
  float calibrated = apply_humidity_calibration(5.0f, -10.0f);
  ASSERT_NEAR(calibrated, 0.0f, 0.01f);  // Should clamp to 0
}

TEST_CASE(apply_humidity_calibration_nan) {
  float calibrated = apply_humidity_calibration(NAN, 5.0f);
  ASSERT_TRUE(std::isnan(calibrated));
}

TEST_CASE(validate_calibration_valid) {
  ASSERT_TRUE(validate_calibration_offsets(5.0f, 10.0f));
  ASSERT_TRUE(validate_calibration_offsets(-5.0f, -10.0f));
  ASSERT_TRUE(validate_calibration_offsets(0.0f, 0.0f));
}

TEST_CASE(validate_calibration_temp_out_of_range) {
  ASSERT_FALSE(validate_calibration_offsets(31.0f, 10.0f));
  ASSERT_FALSE(validate_calibration_offsets(-31.0f, 10.0f));
}

TEST_CASE(validate_calibration_humidity_out_of_range) {
  ASSERT_FALSE(validate_calibration_offsets(5.0f, 51.0f));
  ASSERT_FALSE(validate_calibration_offsets(5.0f, -51.0f));
}

TEST_CASE(validate_calibration_nan) {
  ASSERT_FALSE(validate_calibration_offsets(NAN, 10.0f));
  ASSERT_FALSE(validate_calibration_offsets(5.0f, NAN));
}

TEST_CASE(validate_calibration_at_boundaries) {
  ASSERT_TRUE(validate_calibration_offsets(30.0f, 50.0f));   // Max valid
  ASSERT_TRUE(validate_calibration_offsets(-30.0f, -50.0f)); // Min valid
}

TEST_CASE(should_calibrate_temp_error_large) {
  // Temperature error > 2°C
  ASSERT_TRUE(should_calibrate(25.0f, 50.0f, 22.0f, 50.0f));
}

TEST_CASE(should_calibrate_humidity_error_large) {
  // Humidity error > 5%RH
  ASSERT_TRUE(should_calibrate(25.0f, 60.0f, 25.0f, 50.0f));
}

TEST_CASE(should_calibrate_both_errors_large) {
  ASSERT_TRUE(should_calibrate(25.0f, 60.0f, 22.0f, 50.0f));
}

TEST_CASE(should_calibrate_errors_small) {
  // Errors within threshold: temp < 2°C, humidity < 5%RH
  ASSERT_FALSE(should_calibrate(25.0f, 50.0f, 24.5f, 48.0f));
}

TEST_CASE(should_calibrate_exactly_at_temp_threshold) {
  // Exactly 2°C error
  ASSERT_FALSE(should_calibrate(25.0f, 50.0f, 23.0f, 50.0f));
}

TEST_CASE(should_calibrate_exactly_at_humidity_threshold) {
  // Exactly 5%RH error
  ASSERT_FALSE(should_calibrate(25.0f, 55.0f, 25.0f, 50.0f));
}

TEST_CASE(should_calibrate_just_over_temp_threshold) {
  // Slightly over 2°C error
  ASSERT_TRUE(should_calibrate(25.0f, 50.0f, 22.9f, 50.0f));
}

TEST_CASE(should_calibrate_with_nan) {
  ASSERT_FALSE(should_calibrate(NAN, 50.0f, 22.0f, 50.0f));
  ASSERT_FALSE(should_calibrate(25.0f, NAN, 22.0f, 50.0f));
  ASSERT_FALSE(should_calibrate(25.0f, 50.0f, NAN, 50.0f));
  ASSERT_FALSE(should_calibrate(25.0f, 50.0f, 22.0f, NAN));
}

// Integration test: Full calibration workflow
TEST_CASE(integration_full_calibration_workflow) {
  // Scenario: Raw sensor reads 22°C, 45%RH
  // Reference instrument reads 24.5°C, 52%RH
  float raw_temp = 22.0f;
  float raw_humidity = 45.0f;
  float ref_temp = 24.5f;
  float ref_humidity = 52.0f;

  // Step 1: Check if calibration needed
  ASSERT_TRUE(should_calibrate(ref_temp, ref_humidity, raw_temp, raw_humidity));

  // Step 2: Compute calibration
  CalibrationResult cal = compute_single_point_calibration(ref_temp, ref_humidity, raw_temp, raw_humidity);
  ASSERT_TRUE(cal.valid);
  ASSERT_NEAR(cal.temperature_offset, 2.5f, 0.01f);
  ASSERT_NEAR(cal.humidity_offset, 7.0f, 0.01f);

  // Step 3: Validate offsets
  ASSERT_TRUE(validate_calibration_offsets(cal.temperature_offset, cal.humidity_offset));

  // Step 4: Apply calibration to new raw readings
  float new_raw_temp = 21.0f;
  float new_raw_humidity = 48.0f;

  float calibrated_temp = apply_temperature_calibration(new_raw_temp, cal.temperature_offset);
  float calibrated_humidity = apply_humidity_calibration(new_raw_humidity, cal.humidity_offset);

  ASSERT_NEAR(calibrated_temp, 23.5f, 0.01f);
  ASSERT_NEAR(calibrated_humidity, 55.0f, 0.01f);
}

int main() {
  std::cout << "Running calibration tests..." << std::endl;
  std::cout << "=====================================" << std::endl;

  // Calibration computation tests
  run_test(test_compute_calibration_simple_positive_offset, "compute_calibration_simple_positive_offset");
  run_test(test_compute_calibration_simple_negative_offset, "compute_calibration_simple_negative_offset");
  run_test(test_compute_calibration_zero_offset, "compute_calibration_zero_offset");

  // Clamping tests
  run_test(test_compute_calibration_clamps_temp_high, "compute_calibration_clamps_temp_high");
  run_test(test_compute_calibration_clamps_temp_low, "compute_calibration_clamps_temp_low");
  run_test(test_compute_calibration_clamps_humidity_high, "compute_calibration_clamps_humidity_high");
  run_test(test_compute_calibration_clamps_humidity_low, "compute_calibration_clamps_humidity_low");

  // NaN handling tests
  run_test(test_compute_calibration_nan_reference_temp, "compute_calibration_nan_reference_temp");
  run_test(test_compute_calibration_nan_reference_humidity, "compute_calibration_nan_reference_humidity");
  run_test(test_compute_calibration_nan_raw_temp, "compute_calibration_nan_raw_temp");
  run_test(test_compute_calibration_nan_raw_humidity, "compute_calibration_nan_raw_humidity");

  // Application tests
  run_test(test_apply_temperature_calibration_normal, "apply_temperature_calibration_normal");
  run_test(test_apply_temperature_calibration_negative_offset, "apply_temperature_calibration_negative_offset");
  run_test(test_apply_temperature_calibration_nan, "apply_temperature_calibration_nan");
  run_test(test_apply_humidity_calibration_normal, "apply_humidity_calibration_normal");
  run_test(test_apply_humidity_calibration_clamps_at_100, "apply_humidity_calibration_clamps_at_100");
  run_test(test_apply_humidity_calibration_clamps_at_0, "apply_humidity_calibration_clamps_at_0");
  run_test(test_apply_humidity_calibration_nan, "apply_humidity_calibration_nan");

  // Validation tests
  run_test(test_validate_calibration_valid, "validate_calibration_valid");
  run_test(test_validate_calibration_temp_out_of_range, "validate_calibration_temp_out_of_range");
  run_test(test_validate_calibration_humidity_out_of_range, "validate_calibration_humidity_out_of_range");
  run_test(test_validate_calibration_nan, "validate_calibration_nan");
  run_test(test_validate_calibration_at_boundaries, "validate_calibration_at_boundaries");

  // Should calibrate tests
  run_test(test_should_calibrate_temp_error_large, "should_calibrate_temp_error_large");
  run_test(test_should_calibrate_humidity_error_large, "should_calibrate_humidity_error_large");
  run_test(test_should_calibrate_both_errors_large, "should_calibrate_both_errors_large");
  run_test(test_should_calibrate_errors_small, "should_calibrate_errors_small");
  run_test(test_should_calibrate_exactly_at_temp_threshold, "should_calibrate_exactly_at_temp_threshold");
  run_test(test_should_calibrate_exactly_at_humidity_threshold, "should_calibrate_exactly_at_humidity_threshold");
  run_test(test_should_calibrate_just_over_temp_threshold, "should_calibrate_just_over_temp_threshold");
  run_test(test_should_calibrate_with_nan, "should_calibrate_with_nan");

  // Integration test
  run_test(test_integration_full_calibration_workflow, "integration_full_calibration_workflow");

  std::cout << "=====================================" << std::endl;
  std::cout << "Results: " << passed_count << "/" << test_count << " tests passed" << std::endl;

  return (passed_count == test_count) ? 0 : 1;
}

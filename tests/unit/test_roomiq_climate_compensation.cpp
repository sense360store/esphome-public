// S360-200-R4-CLIMATE-COMPENSATION-001 — deterministic native tests for the
// pure RoomIQ climate compensation model
// (include/sense360/roomiq_climate_compensation.h).
//
// This exercises the SAME header the production firmware compiles (through the
// RoomIQ engine), with no ESPHome dependency, so the tested model and the
// shipped model cannot drift. It covers the profile constants and their signs,
// the Magnus / psychrometric humidity model, customer calibration in both
// directions, the physical 0-100 %RH clamps, non-finite inputs, and the SHT45
// sample-coherence rule (callback order, skew, unpaired humidity, millisecond
// rollover).
//
// IMPORTANT: a green run here is LOGIC/SIMULATION proof only. It is never
// hardware validation. The profile constants come from a multi-day comparison
// run on ONE physical S360-200 R4 board (validated provisional); multi-unit
// production validation remains outstanding.
//
// Compile via tests/Makefile (auto-discovered):  cd tests && make test

#include "../../include/sense360/roomiq_climate_compensation.h"

#include <cassert>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <exception>

using namespace sense360::roomiq;

// Simple test framework (repo convention — see test_led_logic.cpp)
#define TEST_CASE(name) void test_##name()
#define ASSERT_TRUE(cond) assert(cond)
#define ASSERT_FALSE(cond) assert(!(cond))
#define ASSERT_EQ(a, b) assert((a) == (b))
#define ASSERT_STREQ(a, b) assert(std::strcmp((a), (b)) == 0)
#define ASSERT_NEAR(a, b, eps) assert(std::fabs((a) - (b)) <= (eps))
#define ASSERT_NAN(a) assert(std::isnan(a))

static int test_count = 0;
static int passed_count = 0;

void run_test(void (*test_func)(), const char *test_name) {
  test_count++;
  try {
    test_func();
    passed_count++;
    printf("[PASS] %s\n", test_name);
  } catch (const std::exception &e) {
    printf("[FAIL] %s: %s\n", test_name, e.what());
  } catch (...) {
    printf("[FAIL] %s: unknown error\n", test_name);
  }
}

// Float tolerance for the model outputs. The expected values below are the
// exact single-precision results of the documented formula, so a tight
// tolerance is appropriate and catches a changed constant immediately.
static const float EPS = 0.001f;

static const ClimateProfile &PROFILE() {
  return S360_200_R4_CLIMATE_PROFILE_V1();
}

// ---------------------------------------------------------------------------
// Board profile — the constants, their SIGNS, and the evidence posture that
// travels with them.
// ---------------------------------------------------------------------------

TEST_CASE(profile_identifies_the_board_and_revision) {
  ASSERT_STREQ(PROFILE().id, "S360_200_R4_CLIMATE_PROFILE_V1");
  ASSERT_STREQ(PROFILE().board_sku, "S360-200");
  ASSERT_STREQ(PROFILE().board_revision, "R4");
}

TEST_CASE(profile_constants_and_signs_are_exact) {
  // The temperature correction is NEGATIVE (the board reads hot) and the
  // humidity residual is POSITIVE. A sign flip here is the single most
  // damaging silent regression possible, so both are pinned exactly.
  ASSERT_NEAR(PROFILE().temperature_correction_c, -5.80f, 1e-6f);
  ASSERT_TRUE(PROFILE().temperature_correction_c < 0.0f);
  ASSERT_NEAR(PROFILE().humidity_residual_pct, 4.52f, 1e-6f);
  ASSERT_TRUE(PROFILE().humidity_residual_pct > 0.0f);
}

TEST_CASE(profile_carries_its_evidence_level) {
  // Validated provisional: one tested board, not multi-unit / production /
  // compliance evidence. The string is single-sourced so a diagnostic can
  // never quote the constants without the posture.
  ASSERT_EQ(PROFILE().evidence, CLIMATE_EVIDENCE_VALIDATED_PROVISIONAL);
  ASSERT_STREQ(climate_evidence_to_string(PROFILE().evidence),
               "validated-provisional");
  ASSERT_STREQ(climate_evidence_to_string(CLIMATE_EVIDENCE_NONE), "none");
}

// ---------------------------------------------------------------------------
// Magnus saturation vapour pressure
// ---------------------------------------------------------------------------

TEST_CASE(saturation_vapour_pressure_matches_magnus) {
  // 6.112 * exp(17.62 * T / (243.12 + T)) — at 0 C the exponent is 0.
  ASSERT_NEAR(saturation_vapour_pressure_hpa(0.0f), 6.112f, EPS);
  ASSERT_NEAR(saturation_vapour_pressure_hpa(20.0f), 23.325964f, EPS);
  ASSERT_NEAR(saturation_vapour_pressure_hpa(24.2f), 30.125174f, EPS);
  ASSERT_NEAR(saturation_vapour_pressure_hpa(30.0f), 42.337246f, EPS);
  // Saturation vapour pressure rises monotonically with temperature.
  ASSERT_TRUE(saturation_vapour_pressure_hpa(30.0f) >
              saturation_vapour_pressure_hpa(24.2f));
}

TEST_CASE(saturation_vapour_pressure_rejects_impossible_inputs) {
  ASSERT_NAN(saturation_vapour_pressure_hpa(NAN));
  ASSERT_NAN(saturation_vapour_pressure_hpa(INFINITY));
  ASSERT_NAN(saturation_vapour_pressure_hpa(-243.12f));  // the Magnus pole
  ASSERT_NAN(saturation_vapour_pressure_hpa(-300.0f));
}

// ---------------------------------------------------------------------------
// The model with neutral customer calibration — the documented vectors.
// ---------------------------------------------------------------------------

TEST_CASE(zero_customer_calibration_reference_vector_a) {
  ClimateResult r = compensate_climate(PROFILE(), 30.0f, 40.0f, 0.0f, 0.0f);
  ASSERT_TRUE(r.valid);
  ASSERT_NEAR(r.temperature_c, 24.2f, EPS);      // 30.0 - 5.80
  ASSERT_NEAR(r.humidity_pct, 60.7351f, EPS);    // psychrometric + 4.52
  // With neutral calibration the customer value IS the factory value.
  ASSERT_NEAR(r.factory_temperature_c, 24.2f, EPS);
  ASSERT_NEAR(r.factory_humidity_pct, 60.7351f, EPS);
}

TEST_CASE(zero_customer_calibration_reference_vector_b) {
  ClimateResult r = compensate_climate(PROFILE(), 36.0f, 24.8f, 0.0f, 0.0f);
  ASSERT_TRUE(r.valid);
  ASSERT_NEAR(r.temperature_c, 30.2f, EPS);      // 36.0 - 5.80
  ASSERT_NEAR(r.humidity_pct, 38.8673f, EPS);
}

TEST_CASE(humidity_preserves_raw_vapour_pressure) {
  // The model is not an additive humidity fudge: it holds the RAW pair's
  // vapour pressure constant and re-expresses it at the corrected
  // temperature. Recomputing the vapour pressure from the compensated pair
  // (after removing the factory residual) must return the raw one.
  const float raw_t = 30.0f, raw_h = 40.0f;
  ClimateResult r = compensate_climate(PROFILE(), raw_t, raw_h, 0.0f, 0.0f);
  const float raw_vp =
      (raw_h / 100.0f) * saturation_vapour_pressure_hpa(raw_t);
  const float psychrometric = r.humidity_pct - PROFILE().humidity_residual_pct;
  const float final_vp = (psychrometric / 100.0f) *
                         saturation_vapour_pressure_hpa(r.temperature_c);
  ASSERT_NEAR(final_vp, raw_vp, 0.005f);
  // Cooling the reading raises relative humidity — the physical direction.
  ASSERT_TRUE(r.humidity_pct > raw_h);
}

TEST_CASE(temperature_only_path_needs_no_humidity) {
  // The temperature channel stays independently usable: no humidity sample is
  // required to compensate a temperature.
  ASSERT_NEAR(compensate_temperature_c(PROFILE(), 30.0f, 0.0f), 24.2f, EPS);
  ASSERT_NEAR(compensate_temperature_c(PROFILE(), 21.0f, 0.0f), 15.2f, EPS);
  ASSERT_NAN(compensate_temperature_c(PROFILE(), NAN, 0.0f));
}

// ---------------------------------------------------------------------------
// Customer calibration — additional fine calibration AFTER the board profile.
// ---------------------------------------------------------------------------

TEST_CASE(positive_customer_temperature_calibration_moves_both_channels) {
  ClimateResult r = compensate_climate(PROFILE(), 30.0f, 40.0f, 1.0f, 0.0f);
  ASSERT_NEAR(r.temperature_c, 25.2f, EPS);      // 30.0 - 5.80 + 1.0
  // Warming the calibrated temperature LOWERS relative humidity, because the
  // same vapour pressure is a smaller fraction of a larger saturation
  // pressure. This is the model working, never a second correction.
  ASSERT_NEAR(r.humidity_pct, 57.4761f, EPS);
  ASSERT_TRUE(r.humidity_pct < 60.7351f);
}

TEST_CASE(negative_customer_temperature_calibration_moves_both_channels) {
  ClimateResult r = compensate_climate(PROFILE(), 30.0f, 40.0f, -1.0f, 0.0f);
  ASSERT_NEAR(r.temperature_c, 23.2f, EPS);      // 30.0 - 5.80 - 1.0
  ASSERT_NEAR(r.humidity_pct, 64.2215f, EPS);
  ASSERT_TRUE(r.humidity_pct > 60.7351f);
}

TEST_CASE(customer_humidity_calibration_is_applied_once_at_the_end) {
  ClimateResult plus = compensate_climate(PROFILE(), 30.0f, 40.0f, 0.0f, 5.0f);
  ASSERT_NEAR(plus.temperature_c, 24.2f, EPS);   // humidity offset never
                                                 // touches temperature
  ASSERT_NEAR(plus.humidity_pct, 65.7351f, EPS);  // exactly +5.00, once

  ClimateResult minus =
      compensate_climate(PROFILE(), 30.0f, 40.0f, 0.0f, -5.0f);
  ASSERT_NEAR(minus.humidity_pct, 55.7351f, EPS);  // exactly -5.00, once
  ASSERT_NEAR(plus.humidity_pct - minus.humidity_pct, 10.0f, EPS);
}

TEST_CASE(both_customer_calibrations_compose_without_double_applying) {
  ClimateResult r = compensate_climate(PROFILE(), 30.0f, 40.0f, 1.0f, 5.0f);
  ASSERT_NEAR(r.temperature_c, 25.2f, EPS);
  // The +1.0 C recalculation (57.4761) plus exactly one +5.00 %RH.
  ASSERT_NEAR(r.humidity_pct, 62.4761f, EPS);
}

TEST_CASE(factory_values_exclude_customer_calibration) {
  // The support diagnostic must show the built-in profile ALONE, whatever the
  // customer has entered.
  ClimateResult r = compensate_climate(PROFILE(), 30.0f, 40.0f, 1.0f, 5.0f);
  ASSERT_NEAR(r.factory_temperature_c, 24.2f, EPS);
  ASSERT_NEAR(r.factory_humidity_pct, 60.7351f, EPS);
}

// ---------------------------------------------------------------------------
// Physical clamps and invalid inputs
// ---------------------------------------------------------------------------

TEST_CASE(humidity_is_clamped_to_the_upper_physical_bound) {
  // A large cooling correction on already-damp air oversaturates the
  // arithmetic; relative humidity can never exceed 100 %.
  ClimateResult r = compensate_climate(PROFILE(), 10.0f, 99.0f, 0.0f, 0.0f);
  ASSERT_TRUE(r.valid);
  ASSERT_NEAR(r.humidity_pct, 100.0f, EPS);
  ASSERT_NEAR(r.factory_humidity_pct, 100.0f, EPS);
  // The temperature is NOT clamped — 4.2 C is a perfectly valid reading.
  ASSERT_NEAR(r.temperature_c, 4.2f, EPS);
}

TEST_CASE(humidity_is_clamped_to_the_lower_physical_bound) {
  ClimateResult r = compensate_climate(PROFILE(), 30.0f, 1.0f, 0.0f, -10.0f);
  ASSERT_TRUE(r.valid);
  ASSERT_NEAR(r.humidity_pct, 0.0f, EPS);
  // The factory-only view is unclamped by the customer offset and stays a
  // real number.
  ASSERT_NEAR(r.factory_humidity_pct, 5.9254f, EPS);
}

TEST_CASE(non_finite_inputs_are_never_a_value) {
  const float bad[] = {NAN, INFINITY, -INFINITY};
  for (float value : bad) {
    ClimateResult t = compensate_climate(PROFILE(), value, 40.0f, 0.0f, 0.0f);
    ASSERT_FALSE(t.valid);
    ASSERT_NAN(t.temperature_c);
    ASSERT_NAN(t.humidity_pct);
    ASSERT_NAN(t.factory_temperature_c);
    ASSERT_NAN(t.factory_humidity_pct);

    ClimateResult h = compensate_climate(PROFILE(), 30.0f, value, 0.0f, 0.0f);
    ASSERT_FALSE(h.valid);
    ASSERT_NAN(h.humidity_pct);

    ASSERT_NAN(compensate_temperature_c(PROFILE(), value, 0.0f));
  }
}

TEST_CASE(non_finite_customer_calibration_is_neutral_not_a_correction) {
  // An invalid persisted calibration value must never poison a good reading.
  ClimateResult r = compensate_climate(PROFILE(), 30.0f, 40.0f, NAN, NAN);
  ASSERT_TRUE(r.valid);
  ASSERT_NEAR(r.temperature_c, 24.2f, EPS);
  ASSERT_NEAR(r.humidity_pct, 60.7351f, EPS);
  ASSERT_NEAR(compensate_temperature_c(PROFILE(), 30.0f, INFINITY), 24.2f, EPS);
  ASSERT_NEAR(sanitise_customer_offset(NAN), 0.0f, EPS);
  ASSERT_NEAR(sanitise_customer_offset(-2.5f), -2.5f, EPS);
}

TEST_CASE(a_different_profile_drives_a_different_result) {
  // Proof that the CONSTANTS drive the model — not a hidden literal.
  const ClimateProfile neutral = {"TEST_NEUTRAL", "TEST", "R0",
                                  0.0f,           0.0f,   CLIMATE_EVIDENCE_NONE};
  ClimateResult r = compensate_climate(neutral, 30.0f, 40.0f, 0.0f, 0.0f);
  ASSERT_NEAR(r.temperature_c, 30.0f, EPS);
  ASSERT_NEAR(r.humidity_pct, 40.0f, EPS);
}

// ---------------------------------------------------------------------------
// Sample coherence — one SHT45 conversion, two ESPHome callbacks.
// ---------------------------------------------------------------------------

TEST_CASE(temperature_first_callback_order_forms_a_pair) {
  ClimateSamplePairer pairer;
  ASSERT_FALSE(pairer.input_temperature(1000, 30.0f));  // no counterpart yet
  ASSERT_FALSE(pairer.pair_valid());
  ASSERT_TRUE(pairer.input_humidity(1002, 40.0f));      // completes the pair
  ASSERT_TRUE(pairer.pair_valid());
  ASSERT_NEAR(pairer.pair_temperature(), 30.0f, EPS);
  ASSERT_NEAR(pairer.pair_humidity(), 40.0f, EPS);
  ASSERT_EQ(pairer.pair_ms(), 1002u);  // the LATER half
}

TEST_CASE(humidity_first_callback_order_forms_a_pair) {
  ClimateSamplePairer pairer;
  ASSERT_FALSE(pairer.input_humidity(1000, 40.0f));     // unpaired humidity
  ASSERT_FALSE(pairer.pair_valid());
  ASSERT_TRUE(pairer.input_temperature(1002, 30.0f));   // completes the pair
  ASSERT_TRUE(pairer.pair_valid());
  ASSERT_NEAR(pairer.pair_temperature(), 30.0f, EPS);
  ASSERT_NEAR(pairer.pair_humidity(), 40.0f, EPS);
  ASSERT_EQ(pairer.pair_ms(), 1002u);
}

TEST_CASE(excessive_pair_skew_is_refused) {
  ClimateSamplePairer pairer;
  pairer.set_max_pair_skew_ms(5000);
  pairer.input_temperature(1000, 30.0f);
  // 5001 ms apart: beyond the documented maximum for one conversion.
  ASSERT_FALSE(pairer.input_humidity(6001, 40.0f));
  ASSERT_FALSE(pairer.pair_valid());
  // Exactly at the limit is still one conversion.
  ASSERT_TRUE(pairer.input_humidity(6000, 40.0f));
  ASSERT_TRUE(pairer.pair_valid());
}

TEST_CASE(a_stale_counterpart_cannot_pair_with_the_next_cycle) {
  // The 30 s S360-200 R4 polling cycle is far outside the 5 s skew window, so
  // last cycle's humidity can never pair with this cycle's temperature.
  ClimateSamplePairer pairer;
  pairer.input_humidity(1000, 40.0f);
  ASSERT_FALSE(pairer.input_temperature(31000, 30.0f));
  ASSERT_FALSE(pairer.pair_valid());
}

TEST_CASE(non_finite_samples_never_pair_and_never_overwrite) {
  ClimateSamplePairer pairer;
  ASSERT_TRUE(pairer.input_temperature(1000, 30.0f) == false);
  ASSERT_TRUE(pairer.input_humidity(1000, 40.0f));
  // A NaN sample is an INVALID update: it neither pairs nor replaces the last
  // good value.
  ASSERT_FALSE(pairer.input_temperature(2000, NAN));
  ASSERT_FALSE(pairer.input_humidity(2000, NAN));
  ASSERT_NEAR(pairer.raw_temperature(), 30.0f, EPS);
  ASSERT_NEAR(pairer.raw_humidity(), 40.0f, EPS);
  ASSERT_EQ(pairer.pair_ms(), 1000u);
}

TEST_CASE(the_same_sample_combination_pairs_at_most_once) {
  // A repeated callback must not re-freshen humidity from an already-consumed
  // sample — that would fabricate freshness the sensor never provided.
  ClimateSamplePairer pairer;
  pairer.input_temperature(1000, 30.0f);
  ASSERT_TRUE(pairer.input_humidity(1000, 40.0f));
  ASSERT_FALSE(pairer.input_temperature(1000, 30.0f));
  ASSERT_FALSE(pairer.input_humidity(1000, 40.0f));
  // A genuinely NEW sample does pair again.
  ASSERT_TRUE(pairer.input_temperature(1500, 30.5f));
  ASSERT_EQ(pairer.pair_ms(), 1500u);
}

TEST_CASE(raw_samples_stay_raw_and_available_before_pairing) {
  ClimateSamplePairer pairer;
  ASSERT_FALSE(pairer.temperature_valid());
  ASSERT_NAN(pairer.raw_temperature());
  ASSERT_NAN(pairer.raw_humidity());
  ASSERT_NAN(pairer.pair_temperature());
  ASSERT_NAN(pairer.pair_humidity());

  pairer.input_humidity(1000, 40.0f);
  // Unpaired, but the RAW diagnostic value is still honestly available.
  ASSERT_TRUE(pairer.humidity_valid());
  ASSERT_NEAR(pairer.raw_humidity(), 40.0f, EPS);
  ASSERT_FALSE(pairer.pair_valid());
  ASSERT_NAN(pairer.pair_humidity());
}

TEST_CASE(millisecond_rollover_is_handled) {
  const uint32_t before_wrap = 0xFFFFFFF0u;  // 16 ms before rollover
  // Circular distance must not explode across the wrap.
  ASSERT_EQ(ClimateSamplePairer::skew_ms(before_wrap, 10u), 26u);
  ASSERT_EQ(ClimateSamplePairer::skew_ms(10u, before_wrap), 26u);
  ASSERT_EQ(ClimateSamplePairer::later_ms(before_wrap, 10u), 10u);
  ASSERT_EQ(ClimateSamplePairer::later_ms(10u, before_wrap), 10u);

  ClimateSamplePairer pairer;
  pairer.input_temperature(before_wrap, 30.0f);
  ASSERT_TRUE(pairer.input_humidity(10u, 40.0f));  // 26 ms apart across wrap
  ASSERT_EQ(pairer.pair_ms(), 10u);                // the post-wrap timestamp
  ASSERT_NEAR(pairer.pair_temperature(), 30.0f, EPS);

  // A genuine 30 s gap across the wrap is still refused.
  ClimateSamplePairer wide;
  wide.input_temperature(0xFFFFFFF0u, 30.0f);
  ASSERT_FALSE(wide.input_humidity(0xFFFFFFF0u + 30000u, 40.0f));
}

TEST_CASE(default_pair_skew_is_the_documented_window) {
  ClimateSamplePairer pairer;
  ASSERT_EQ(pairer.max_pair_skew_ms(), DEFAULT_CLIMATE_PAIR_SKEW_MS);
  ASSERT_EQ(DEFAULT_CLIMATE_PAIR_SKEW_MS, 5000u);
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

int main() {
  printf("\nS360-200-R4-CLIMATE-COMPENSATION-001 model tests\n");
  printf("=================================================\n");
  printf("LOGIC/SIMULATION PROOF ONLY — never hardware validation.\n");
  printf("Profile evidence: validated provisional, ONE tested board.\n\n");

  run_test(test_profile_identifies_the_board_and_revision,
           "profile_identifies_the_board_and_revision");
  run_test(test_profile_constants_and_signs_are_exact,
           "profile_constants_and_signs_are_exact");
  run_test(test_profile_carries_its_evidence_level,
           "profile_carries_its_evidence_level");
  run_test(test_saturation_vapour_pressure_matches_magnus,
           "saturation_vapour_pressure_matches_magnus");
  run_test(test_saturation_vapour_pressure_rejects_impossible_inputs,
           "saturation_vapour_pressure_rejects_impossible_inputs");
  run_test(test_zero_customer_calibration_reference_vector_a,
           "zero_customer_calibration_reference_vector_a");
  run_test(test_zero_customer_calibration_reference_vector_b,
           "zero_customer_calibration_reference_vector_b");
  run_test(test_humidity_preserves_raw_vapour_pressure,
           "humidity_preserves_raw_vapour_pressure");
  run_test(test_temperature_only_path_needs_no_humidity,
           "temperature_only_path_needs_no_humidity");
  run_test(test_positive_customer_temperature_calibration_moves_both_channels,
           "positive_customer_temperature_calibration_moves_both_channels");
  run_test(test_negative_customer_temperature_calibration_moves_both_channels,
           "negative_customer_temperature_calibration_moves_both_channels");
  run_test(test_customer_humidity_calibration_is_applied_once_at_the_end,
           "customer_humidity_calibration_is_applied_once_at_the_end");
  run_test(test_both_customer_calibrations_compose_without_double_applying,
           "both_customer_calibrations_compose_without_double_applying");
  run_test(test_factory_values_exclude_customer_calibration,
           "factory_values_exclude_customer_calibration");
  run_test(test_humidity_is_clamped_to_the_upper_physical_bound,
           "humidity_is_clamped_to_the_upper_physical_bound");
  run_test(test_humidity_is_clamped_to_the_lower_physical_bound,
           "humidity_is_clamped_to_the_lower_physical_bound");
  run_test(test_non_finite_inputs_are_never_a_value,
           "non_finite_inputs_are_never_a_value");
  run_test(test_non_finite_customer_calibration_is_neutral_not_a_correction,
           "non_finite_customer_calibration_is_neutral_not_a_correction");
  run_test(test_a_different_profile_drives_a_different_result,
           "a_different_profile_drives_a_different_result");
  run_test(test_temperature_first_callback_order_forms_a_pair,
           "temperature_first_callback_order_forms_a_pair");
  run_test(test_humidity_first_callback_order_forms_a_pair,
           "humidity_first_callback_order_forms_a_pair");
  run_test(test_excessive_pair_skew_is_refused,
           "excessive_pair_skew_is_refused");
  run_test(test_a_stale_counterpart_cannot_pair_with_the_next_cycle,
           "a_stale_counterpart_cannot_pair_with_the_next_cycle");
  run_test(test_non_finite_samples_never_pair_and_never_overwrite,
           "non_finite_samples_never_pair_and_never_overwrite");
  run_test(test_the_same_sample_combination_pairs_at_most_once,
           "the_same_sample_combination_pairs_at_most_once");
  run_test(test_raw_samples_stay_raw_and_available_before_pairing,
           "raw_samples_stay_raw_and_available_before_pairing");
  run_test(test_millisecond_rollover_is_handled,
           "millisecond_rollover_is_handled");
  run_test(test_default_pair_skew_is_the_documented_window,
           "default_pair_skew_is_the_documented_window");

  printf("\n=================================================\n");
  printf("Results: %d/%d tests passed\n", passed_count, test_count);
  if (passed_count == test_count) {
    printf("All RoomIQ climate compensation tests passed.\n");
    return 0;
  }
  printf("SOME TESTS FAILED\n");
  return 1;
}

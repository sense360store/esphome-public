// AIRIQ-FRAMEWORK-001 — deterministic simulation tests for the canonical
// AirIQ indoor-air-quality engine (include/sense360/airiq_engine.h).
//
// This is the test-only simulation layer required by the accepted product
// decisions: it feeds synthetic, timestamped pollutant samples into the SAME
// header-only engine the production YAML compiles (no second implementation
// that can drift) and asserts deterministic per-pollutant severities, the
// worst-pollutant Air Quality headline, the customer Recommendation and the
// module-health outputs for startup, independent per-sensor warm-up, partial
// readiness, fresh data, stale data, failure and recovery, expected-sensor
// composition, optional-sensor absence, MiCS diagnostic-only posture,
// invalid values and threshold boundaries.
//
// IMPORTANT: a green run here is LOGIC/SIMULATION proof only. It is never
// hardware validation — the SCD41 / SGP41 / SPS30 / BMP390 paths remain
// physically unverified until the bench checklist
// (docs/hardware/airiq-framework-bench-checklist.md) is executed by the
// operator. All thresholds are provisional indoor-air-quality heuristics,
// never medical, health or regulatory claims.
//
// Compile via tests/Makefile (auto-discovered):  cd tests && make test

#include "../../include/sense360/airiq_engine.h"

#include <cassert>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <exception>

using namespace sense360::airiq;

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

// ---------------------------------------------------------------------------
// Fixture helpers — production engineering defaults (provisional, pending
// bench validation; mirror packages/features/airiq_framework.yaml).
// ---------------------------------------------------------------------------

// Timestamps (ms). Warm-up defaults: CO2 60 s, VOC/NOx 120 s, PM 60 s.
static const uint32_t T0 = 1000;
static const uint32_t AFTER_ALL_WARMUPS = T0 + 200000;  // beyond every window

// Feed one good sample on every expected default channel at time t.
static void feed_all_good(AirIQEngine &e, uint32_t t) {
  e.input_co2(t, 600.0f);      // Good (< 800 ppm)
  e.input_voc(t, 80.0f);       // Good (< 150 index)
  e.input_nox(t, 10.0f);       // Good (< 100 index)
  e.input_pm2_5(t, 5.0f);      // Good (< 12 µg/m³)
}

// A default engine that has begun at T0.
static AirIQEngine started_engine() {
  AirIQEngine e;
  e.begin(T0);
  return e;
}

// ---------------------------------------------------------------------------
// Startup / warm-up honesty
// ---------------------------------------------------------------------------

TEST_CASE(startup_is_initialising_never_a_fault) {
  AirIQEngine e = started_engine();
  e.evaluate(T0 + 1000);
  ASSERT_EQ(e.air_quality(), AIR_QUALITY_INITIALISING);
  ASSERT_EQ(e.recommendation(), RECOMMENDATION_INITIALISING);
  ASSERT_EQ(e.health(), HEALTH_INITIALISING);
  ASSERT_STREQ(air_quality_to_string(e.air_quality()), "Initialising");
  ASSERT_STREQ(recommendation_to_string(e.recommendation()),
               "Sensor initialising");
}

TEST_CASE(all_values_unknown_before_first_sample) {
  AirIQEngine e = started_engine();
  e.evaluate(T0 + 1000);
  ASSERT_NAN(e.co2());
  ASSERT_NAN(e.voc());
  ASSERT_NAN(e.nox());
  ASSERT_NAN(e.pm2_5());
  ASSERT_NAN(e.pressure());
}

TEST_CASE(per_sensor_warmup_windows_are_independent) {
  // CO2 (60 s) and PM (60 s) expire before VOC/NOx (120 s): after 90 s
  // without data, CO2/PM are missing while VOC/NOx are still initialising.
  AirIQEngine e = started_engine();
  const uint32_t t = T0 + 90000;
  e.evaluate(t);
  ASSERT_EQ(e.severity(POLLUTANT_CO2), SEVERITY_UNAVAILABLE);
  ASSERT_EQ(e.severity(POLLUTANT_PM25), SEVERITY_UNAVAILABLE);
  ASSERT_EQ(e.severity(POLLUTANT_VOC), SEVERITY_INITIALISING);
  ASSERT_EQ(e.severity(POLLUTANT_NOX), SEVERITY_INITIALISING);
  // Some channels are still inside warm-up: the headline stays honest.
  ASSERT_EQ(e.air_quality(), AIR_QUALITY_INITIALISING);
}

TEST_CASE(first_valid_sample_ends_initialisation_early) {
  AirIQEngine e = started_engine();
  feed_all_good(e, T0 + 5000);
  e.evaluate(T0 + 6000);
  ASSERT_EQ(e.air_quality(), AIR_QUALITY_GOOD);
  ASSERT_EQ(e.health(), HEALTH_AVAILABLE);
  ASSERT_NEAR(e.co2(), 600.0f, 0.01f);
}

TEST_CASE(partial_readiness_gives_honest_partial_headline) {
  // CO2 arrives, the rest are still warming: the headline reports the
  // usable data honestly while health stays Initialising (no outage).
  AirIQEngine e = started_engine();
  e.input_co2(T0 + 5000, 1200.0f);  // Poor
  e.evaluate(T0 + 6000);
  ASSERT_EQ(e.severity(POLLUTANT_CO2), SEVERITY_POOR);
  ASSERT_EQ(e.air_quality(), AIR_QUALITY_POOR);
  ASSERT_EQ(e.health(), HEALTH_INITIALISING);
}

// ---------------------------------------------------------------------------
// Severity bands and boundaries (worst-pollutant model)
// ---------------------------------------------------------------------------

TEST_CASE(co2_severity_boundary_values) {
  AirIQEngine e = started_engine();
  const uint32_t t = T0 + 5000;
  e.input_co2(t, 799.9f);
  e.evaluate(t);
  ASSERT_EQ(e.severity(POLLUTANT_CO2), SEVERITY_GOOD);
  e.input_co2(t + 1000, 800.0f);  // boundary: at the fair threshold
  e.evaluate(t + 1000);
  ASSERT_EQ(e.severity(POLLUTANT_CO2), SEVERITY_FAIR);
  e.input_co2(t + 2000, 1000.0f);
  e.evaluate(t + 2000);
  ASSERT_EQ(e.severity(POLLUTANT_CO2), SEVERITY_POOR);
  e.input_co2(t + 3000, 1500.0f);
  e.evaluate(t + 3000);
  ASSERT_EQ(e.severity(POLLUTANT_CO2), SEVERITY_VERY_POOR);
}

TEST_CASE(voc_and_nox_severity_boundaries) {
  AirIQEngine e = started_engine();
  const uint32_t t = T0 + 5000;
  e.input_voc(t, 149.0f);
  e.input_nox(t, 99.0f);
  e.evaluate(t);
  ASSERT_EQ(e.severity(POLLUTANT_VOC), SEVERITY_GOOD);
  ASSERT_EQ(e.severity(POLLUTANT_NOX), SEVERITY_GOOD);
  e.input_voc(t + 1000, 400.0f);
  e.input_nox(t + 1000, 300.0f);
  e.evaluate(t + 1000);
  ASSERT_EQ(e.severity(POLLUTANT_VOC), SEVERITY_VERY_POOR);
  ASSERT_EQ(e.severity(POLLUTANT_NOX), SEVERITY_VERY_POOR);
}

TEST_CASE(pm25_severity_boundaries) {
  AirIQEngine e = started_engine();
  const uint32_t t = T0 + 5000;
  e.input_pm2_5(t, 11.9f);
  e.evaluate(t);
  ASSERT_EQ(e.severity(POLLUTANT_PM25), SEVERITY_GOOD);
  e.input_pm2_5(t + 1000, 12.0f);
  e.evaluate(t + 1000);
  ASSERT_EQ(e.severity(POLLUTANT_PM25), SEVERITY_FAIR);
  e.input_pm2_5(t + 2000, 35.5f);
  e.evaluate(t + 2000);
  ASSERT_EQ(e.severity(POLLUTANT_PM25), SEVERITY_POOR);
  e.input_pm2_5(t + 3000, 55.5f);
  e.evaluate(t + 3000);
  ASSERT_EQ(e.severity(POLLUTANT_PM25), SEVERITY_VERY_POOR);
}

TEST_CASE(severity_worsens_immediately_but_improves_with_hysteresis) {
  // Worsening air must show immediately; improvement only after the value
  // clears the boundary by the hysteresis margin (no flapping).
  AirIQEngine e = started_engine();
  uint32_t t = T0 + 5000;
  e.input_co2(t, 850.0f);  // Fair
  e.evaluate(t);
  ASSERT_EQ(e.severity(POLLUTANT_CO2), SEVERITY_FAIR);
  t += 1000;
  e.input_co2(t, 790.0f);  // below 800 but within the 50 ppm hysteresis
  e.evaluate(t);
  ASSERT_EQ(e.severity(POLLUTANT_CO2), SEVERITY_FAIR);
  t += 1000;
  e.input_co2(t, 749.0f);  // clears 800 - 50
  e.evaluate(t);
  ASSERT_EQ(e.severity(POLLUTANT_CO2), SEVERITY_GOOD);
}

TEST_CASE(worst_pollutant_wins_never_averaged_away) {
  // One severe pollutant against three good ones: the headline is the
  // worst severity, never a blended average.
  AirIQEngine e = started_engine();
  const uint32_t t = T0 + 5000;
  feed_all_good(e, t);
  e.input_pm2_5(t, 80.0f);  // Very poor
  e.evaluate(t);
  ASSERT_EQ(e.air_quality(), AIR_QUALITY_VERY_POOR);
  ASSERT_EQ(e.worst_pollutant(), POLLUTANT_PM25);
  ASSERT_STREQ(pollutant_to_string(e.worst_pollutant()), "PM2.5");
}

TEST_CASE(worst_pollutant_tie_break_is_deterministic) {
  // Two pollutants at the same worst severity: the driver is chosen by
  // fixed priority order (CO2, VOC, NOx, PM2.5, Formaldehyde, Ozone).
  AirIQEngine e = started_engine();
  const uint32_t t = T0 + 5000;
  feed_all_good(e, t);
  e.input_co2(t, 1200.0f);   // Poor
  e.input_pm2_5(t, 40.0f);   // Poor
  e.evaluate(t);
  ASSERT_EQ(e.air_quality(), AIR_QUALITY_POOR);
  ASSERT_EQ(e.worst_pollutant(), POLLUTANT_CO2);
}

// ---------------------------------------------------------------------------
// Stale data honesty
// ---------------------------------------------------------------------------

TEST_CASE(stale_values_do_not_count_as_good) {
  AirIQEngine e = started_engine();
  feed_all_good(e, T0 + 5000);
  e.evaluate(T0 + 6000);
  ASSERT_EQ(e.air_quality(), AIR_QUALITY_GOOD);
  // 10 minutes later with no updates: every channel is stale — the
  // headline must become Unavailable, never a frozen "Good".
  const uint32_t later = T0 + 600000;
  e.evaluate(later);
  ASSERT_EQ(e.air_quality(), AIR_QUALITY_UNAVAILABLE);
  ASSERT_EQ(e.recommendation(), RECOMMENDATION_UNAVAILABLE);
  ASSERT_EQ(e.health(), HEALTH_UNAVAILABLE);
  ASSERT_NAN(e.co2());
  ASSERT_NAN(e.pm2_5());
}

TEST_CASE(one_stale_expected_sensor_degrades_but_service_remains) {
  AirIQEngine e = started_engine();
  uint32_t t = T0 + 5000;
  feed_all_good(e, t);
  // Keep everything except PM fresh for 4 more minutes.
  for (int i = 1; i <= 8; i++) {
    t = T0 + 5000 + i * 30000;
    e.input_co2(t, 600.0f);
    e.input_voc(t, 80.0f);
    e.input_nox(t, 10.0f);
  }
  e.evaluate(t + 1000);
  ASSERT_EQ(e.severity(POLLUTANT_PM25), SEVERITY_UNAVAILABLE);
  ASSERT_EQ(e.health(), HEALTH_DEGRADED);
  // Honest partial headline from the remaining usable pollutants.
  ASSERT_EQ(e.air_quality(), AIR_QUALITY_GOOD);
  ASSERT_NAN(e.pm2_5());
  ASSERT_NEAR(e.co2(), 600.0f, 0.01f);
}

TEST_CASE(failure_and_recovery_round_trip) {
  AirIQEngine e = started_engine();
  feed_all_good(e, T0 + 5000);
  e.evaluate(T0 + 6000);
  ASSERT_EQ(e.health(), HEALTH_AVAILABLE);
  e.evaluate(T0 + 600000);  // everything stale
  ASSERT_EQ(e.health(), HEALTH_UNAVAILABLE);
  feed_all_good(e, T0 + 610000);  // sensors come back
  e.evaluate(T0 + 611000);
  ASSERT_EQ(e.health(), HEALTH_AVAILABLE);
  ASSERT_EQ(e.air_quality(), AIR_QUALITY_GOOD);
}

// ---------------------------------------------------------------------------
// Composition-driven expected sensors (no Base/Pro axis; optional absence)
// ---------------------------------------------------------------------------

TEST_CASE(optional_absent_sensors_never_degrade_health) {
  // Formaldehyde and ozone are not expected in any current composition:
  // their absence must not degrade a healthy device.
  AirIQEngine e = started_engine();
  feed_all_good(e, T0 + 5000);
  e.evaluate(AFTER_ALL_WARMUPS);  // hcho/o3 never arrived — irrelevant
  ASSERT_EQ(e.severity(POLLUTANT_HCHO), SEVERITY_UNAVAILABLE);
  ASSERT_EQ(e.severity(POLLUTANT_O3), SEVERITY_UNAVAILABLE);
  // Health considers expected channels only... but the feed above is
  // stale by AFTER_ALL_WARMUPS; refresh first for a clean assertion.
  feed_all_good(e, AFTER_ALL_WARMUPS);
  e.evaluate(AFTER_ALL_WARMUPS + 1000);
  ASSERT_EQ(e.health(), HEALTH_AVAILABLE);
  ASSERT_EQ(e.air_quality(), AIR_QUALITY_GOOD);
}

TEST_CASE(expected_sensor_membership_is_configuration_driven) {
  // A future authoritative composition can expect formaldehyde: then a
  // missing formaldehyde channel DOES affect health.
  AirIQEngine e = started_engine();
  e.set_expected(POLLUTANT_HCHO, true);
  feed_all_good(e, T0 + 5000);
  e.evaluate(T0 + 200000);  // hcho warm-up long expired, no data
  ASSERT_EQ(e.health(), HEALTH_UNAVAILABLE);  // everything else stale too
  feed_all_good(e, T0 + 200000);
  e.evaluate(T0 + 201000);
  ASSERT_EQ(e.health(), HEALTH_DEGRADED);  // hcho expected but missing
}

TEST_CASE(hcho_participates_in_severity_only_when_expected) {
  AirIQEngine e = started_engine();
  const uint32_t t = T0 + 5000;
  feed_all_good(e, t);
  // Not expected: even a delivered severe formaldehyde sample must not
  // silently drive the headline of a composition that does not claim the
  // sensor (no phantom Pro sensor in a product that never fitted one).
  e.evaluate(t + 1000);
  ASSERT_EQ(e.air_quality(), AIR_QUALITY_GOOD);
  // Expected (future composition): severe formaldehyde drives the
  // worst-pollutant headline.
  e.set_expected(POLLUTANT_HCHO, true);
  e.input_hcho(t + 2000, 300.0f);  // Very poor (>= 250 ppb provisional)
  e.evaluate(t + 2000);
  ASSERT_EQ(e.air_quality(), AIR_QUALITY_VERY_POOR);
  ASSERT_EQ(e.worst_pollutant(), POLLUTANT_HCHO);
}

TEST_CASE(ozone_slot_behaves_like_hcho) {
  AirIQEngine e = started_engine();
  const uint32_t t = T0 + 5000;
  feed_all_good(e, t);
  e.set_expected(POLLUTANT_O3, true);
  e.input_o3(t, 130.0f);  // Very poor (>= 120 ppb provisional)
  e.evaluate(t);
  ASSERT_EQ(e.air_quality(), AIR_QUALITY_VERY_POOR);
  ASSERT_EQ(e.worst_pollutant(), POLLUTANT_O3);
  ASSERT_STREQ(pollutant_to_string(POLLUTANT_O3), "Ozone");
}

TEST_CASE(unexpected_channels_still_report_severity_for_diagnostics) {
  // Diagnostic honesty: a not-expected channel that HAS fresh data still
  // classifies (visible in diagnostics), it just never drives headline
  // or health.
  AirIQEngine e = started_engine();
  const uint32_t t = T0 + 5000;
  feed_all_good(e, t);
  e.input_hcho(t, 300.0f);
  e.evaluate(t);
  ASSERT_EQ(e.severity(POLLUTANT_HCHO), SEVERITY_VERY_POOR);
  ASSERT_EQ(e.air_quality(), AIR_QUALITY_GOOD);
  ASSERT_EQ(e.health(), HEALTH_AVAILABLE);
}

// ---------------------------------------------------------------------------
// Pressure: tracked value, never a pollutant
// ---------------------------------------------------------------------------

TEST_CASE(pressure_is_excluded_from_severity_and_health) {
  AirIQEngine e = started_engine();
  const uint32_t t = T0 + 5000;
  feed_all_good(e, t);
  // No pressure sample ever arrives (the BMP390-vs-BOM identity conflict
  // means the part may genuinely be absent): headline and health must be
  // completely unaffected.
  e.evaluate(t + 1000);
  ASSERT_EQ(e.air_quality(), AIR_QUALITY_GOOD);
  ASSERT_EQ(e.health(), HEALTH_AVAILABLE);
  ASSERT_NAN(e.pressure());
  // With data, the value is reported (freshness-gated) — still never a
  // severity contributor.
  e.input_pressure(t + 2000, 1013.2f);
  e.evaluate(t + 2000);
  ASSERT_NEAR(e.pressure(), 1013.2f, 0.01f);
  ASSERT_EQ(e.air_quality(), AIR_QUALITY_GOOD);
}

TEST_CASE(pressure_goes_unknown_when_stale) {
  AirIQEngine e = started_engine();
  e.input_pressure(T0 + 5000, 1013.2f);
  e.evaluate(T0 + 6000);
  ASSERT_NEAR(e.pressure(), 1013.2f, 0.01f);
  e.evaluate(T0 + 5000 + 200000);  // beyond the 180 s pressure stale window
  ASSERT_NAN(e.pressure());
}

// ---------------------------------------------------------------------------
// MiCS-4514 — diagnostic-only posture (no driver, no calibration evidence)
// ---------------------------------------------------------------------------

TEST_CASE(mics_channels_are_diagnostic_only) {
  // The MiCS reducing/oxidising channels are part of the architecture but
  // NEVER a pollutant: no severity, no headline, no health effect, no
  // concentration claim. Promotion requires calibration evidence
  // (documented in the architecture doc).
  AirIQEngine e = started_engine();
  const uint32_t t = T0 + 5000;
  feed_all_good(e, t);
  e.input_mics_reducing(t, 123456.0f);   // raw/derived units unverified
  e.input_mics_oxidising(t, 6543.0f);
  e.evaluate(t);
  ASSERT_NEAR(e.mics_reducing(), 123456.0f, 0.01f);
  ASSERT_NEAR(e.mics_oxidising(), 6543.0f, 0.01f);
  ASSERT_EQ(e.air_quality(), AIR_QUALITY_GOOD);
  ASSERT_EQ(e.health(), HEALTH_AVAILABLE);
}

TEST_CASE(mics_values_go_unknown_when_stale) {
  AirIQEngine e = started_engine();
  e.input_mics_reducing(T0 + 5000, 100.0f);
  e.evaluate(T0 + 6000);
  ASSERT_NEAR(e.mics_reducing(), 100.0f, 0.01f);
  e.evaluate(T0 + 600000);
  ASSERT_NAN(e.mics_reducing());
  ASSERT_NAN(e.mics_oxidising());
}

// ---------------------------------------------------------------------------
// Recommendation model (deterministic, explainable, conservative)
// ---------------------------------------------------------------------------

TEST_CASE(good_air_gives_no_action_needed) {
  AirIQEngine e = started_engine();
  feed_all_good(e, T0 + 5000);
  e.evaluate(T0 + 6000);
  ASSERT_EQ(e.recommendation(), RECOMMENDATION_NO_ACTION);
  ASSERT_STREQ(recommendation_to_string(e.recommendation()),
               "No action needed");
}

TEST_CASE(fair_air_gives_no_action_needed) {
  AirIQEngine e = started_engine();
  const uint32_t t = T0 + 5000;
  feed_all_good(e, t);
  e.input_co2(t, 900.0f);  // Fair
  e.evaluate(t);
  ASSERT_EQ(e.air_quality(), AIR_QUALITY_FAIR);
  ASSERT_EQ(e.recommendation(), RECOMMENDATION_NO_ACTION);
}

TEST_CASE(elevated_co2_gives_ventilate_soon_then_now) {
  AirIQEngine e = started_engine();
  uint32_t t = T0 + 5000;
  feed_all_good(e, t);
  e.input_co2(t, 1200.0f);  // Poor
  e.evaluate(t);
  ASSERT_EQ(e.recommendation(), RECOMMENDATION_VENTILATE_SOON);
  t += 1000;
  e.input_co2(t, 1800.0f);  // Very poor
  e.evaluate(t);
  ASSERT_EQ(e.recommendation(), RECOMMENDATION_VENTILATE_NOW);
}

TEST_CASE(severe_voc_or_nox_gives_ventilation_recommendation) {
  AirIQEngine e = started_engine();
  const uint32_t t = T0 + 5000;
  feed_all_good(e, t);
  e.input_voc(t, 450.0f);  // Very poor
  e.evaluate(t);
  ASSERT_EQ(e.recommendation(), RECOMMENDATION_VENTILATE_NOW);
  ASSERT_EQ(e.worst_pollutant(), POLLUTANT_VOC);
}

TEST_CASE(particulate_pollution_gives_conservative_source_check) {
  // Outdoor air quality is unknown: ventilating against particulates may
  // help or worsen conditions, so PM drives "Check pollution source",
  // never an unconditional ventilation instruction.
  AirIQEngine e = started_engine();
  const uint32_t t = T0 + 5000;
  feed_all_good(e, t);
  e.input_pm2_5(t, 80.0f);  // Very poor
  e.evaluate(t);
  ASSERT_EQ(e.recommendation(), RECOMMENDATION_CHECK_SOURCE);
  ASSERT_STREQ(recommendation_to_string(e.recommendation()),
               "Check pollution source");
}

TEST_CASE(ventilation_pollutant_outranks_pm_at_equal_severity) {
  // CO2 and PM both Poor: ventilation demonstrably reduces CO2, so the
  // deterministic rule prefers the ventilation recommendation and the
  // reason names CO2 (fixed priority order).
  AirIQEngine e = started_engine();
  const uint32_t t = T0 + 5000;
  feed_all_good(e, t);
  e.input_co2(t, 1200.0f);
  e.input_pm2_5(t, 40.0f);
  e.evaluate(t);
  ASSERT_EQ(e.recommendation(), RECOMMENDATION_VENTILATE_SOON);
}

TEST_CASE(pm_very_poor_outranks_co2_poor) {
  // The recommendation follows the WORST pollutant, not the pollutant
  // class: PM Very poor vs CO2 Poor → source check.
  AirIQEngine e = started_engine();
  const uint32_t t = T0 + 5000;
  feed_all_good(e, t);
  e.input_co2(t, 1200.0f);   // Poor
  e.input_pm2_5(t, 80.0f);   // Very poor
  e.evaluate(t);
  ASSERT_EQ(e.air_quality(), AIR_QUALITY_VERY_POOR);
  ASSERT_EQ(e.recommendation(), RECOMMENDATION_CHECK_SOURCE);
}

TEST_CASE(expected_hcho_recommendation_is_source_check) {
  AirIQEngine e = started_engine();
  const uint32_t t = T0 + 5000;
  feed_all_good(e, t);
  e.set_expected(POLLUTANT_HCHO, true);
  e.input_hcho(t, 300.0f);
  e.evaluate(t);
  ASSERT_EQ(e.recommendation(), RECOMMENDATION_CHECK_SOURCE);
}

TEST_CASE(unavailable_data_gives_unavailable_recommendation) {
  AirIQEngine e = started_engine();
  e.evaluate(AFTER_ALL_WARMUPS);  // nothing ever arrived
  ASSERT_EQ(e.air_quality(), AIR_QUALITY_UNAVAILABLE);
  ASSERT_EQ(e.recommendation(), RECOMMENDATION_UNAVAILABLE);
}

// ---------------------------------------------------------------------------
// Invalid values
// ---------------------------------------------------------------------------

TEST_CASE(invalid_samples_never_refresh_or_classify) {
  AirIQEngine e = started_engine();
  const uint32_t t = T0 + 5000;
  e.input_co2(t, NAN);        // invalid: not an update
  e.input_pm2_5(t, -4.0f);    // invalid: negative concentration
  e.input_voc(t, NAN);
  e.evaluate(t + 1000);
  ASSERT_NAN(e.co2());
  ASSERT_NAN(e.pm2_5());
  ASSERT_EQ(e.air_quality(), AIR_QUALITY_INITIALISING);
  // A NaN sample after valid data must not mask staleness either.
  feed_all_good(e, t + 2000);
  e.evaluate(t + 3000);
  ASSERT_EQ(e.air_quality(), AIR_QUALITY_GOOD);
  e.input_co2(t + 400000, NAN);  // invalid sample long after staleness
  e.evaluate(t + 400000);
  ASSERT_EQ(e.air_quality(), AIR_QUALITY_UNAVAILABLE);
}

// ---------------------------------------------------------------------------
// Health model details
// ---------------------------------------------------------------------------

TEST_CASE(health_fault_is_reserved_with_no_ordinary_producer) {
  // Fault is an explicit engine contract only: ordinary staleness never
  // produces it, and production YAML wires no fault input today.
  AirIQEngine e = started_engine();
  e.evaluate(AFTER_ALL_WARMUPS);
  ASSERT_EQ(e.health(), HEALTH_UNAVAILABLE);  // never Fault from staleness
  e.set_fault(true);
  e.evaluate(AFTER_ALL_WARMUPS + 1000);
  ASSERT_EQ(e.health(), HEALTH_FAULT);
  ASSERT_STREQ(health_to_string(e.health()), "Fault");
  e.set_fault(false);
  e.evaluate(AFTER_ALL_WARMUPS + 2000);
  ASSERT_EQ(e.health(), HEALTH_UNAVAILABLE);
}

TEST_CASE(data_age_diagnostics_report_seconds) {
  AirIQEngine e = started_engine();
  const uint32_t t = T0 + 5000;
  ASSERT_NAN(e.pollutant_data_age_s(POLLUTANT_CO2, t));
  e.input_co2(t, 600.0f);
  e.evaluate(t);
  ASSERT_NEAR(e.pollutant_data_age_s(POLLUTANT_CO2, t + 30000), 30.0f, 0.01f);
  ASSERT_NAN(e.pressure_data_age_s(t));
  e.input_pressure(t, 1000.0f);
  ASSERT_NEAR(e.pressure_data_age_s(t + 10000), 10.0f, 0.01f);
}

TEST_CASE(pm_fractions_share_the_pm_freshness_channel) {
  // PM1/PM4/PM10 come from the same SPS30 measurement as PM2.5: their
  // values are gated by the shared particulate freshness.
  AirIQEngine e = started_engine();
  const uint32_t t = T0 + 5000;
  e.input_pm2_5(t, 5.0f);
  e.input_pm1(t, 3.0f);
  e.input_pm4(t, 6.0f);
  e.input_pm10(t, 8.0f);
  e.evaluate(t);
  ASSERT_NEAR(e.pm1(), 3.0f, 0.01f);
  ASSERT_NEAR(e.pm4(), 6.0f, 0.01f);
  ASSERT_NEAR(e.pm10(), 8.0f, 0.01f);
  e.evaluate(t + 300000);  // stale
  ASSERT_NAN(e.pm1());
  ASSERT_NAN(e.pm4());
  ASSERT_NAN(e.pm10());
}

// ---------------------------------------------------------------------------
// Vocabulary single-sourcing
// ---------------------------------------------------------------------------

TEST_CASE(state_strings_match_the_customer_contract) {
  ASSERT_STREQ(severity_to_string(SEVERITY_GOOD), "Good");
  ASSERT_STREQ(severity_to_string(SEVERITY_FAIR), "Fair");
  ASSERT_STREQ(severity_to_string(SEVERITY_POOR), "Poor");
  ASSERT_STREQ(severity_to_string(SEVERITY_VERY_POOR), "Very poor");
  ASSERT_STREQ(severity_to_string(SEVERITY_UNAVAILABLE), "Unavailable");
  ASSERT_STREQ(severity_to_string(SEVERITY_INITIALISING), "Initialising");
  ASSERT_STREQ(air_quality_to_string(AIR_QUALITY_VERY_POOR), "Very poor");
  ASSERT_STREQ(recommendation_to_string(RECOMMENDATION_VENTILATE_SOON),
               "Ventilate soon");
  ASSERT_STREQ(health_to_string(HEALTH_DEGRADED), "Degraded");
  ASSERT_STREQ(pollutant_to_string(POLLUTANT_CO2), "CO2");
  ASSERT_STREQ(pollutant_to_string(POLLUTANT_VOC), "VOC");
  ASSERT_STREQ(pollutant_to_string(POLLUTANT_NOX), "NOx");
  ASSERT_STREQ(pollutant_to_string(POLLUTANT_HCHO), "Formaldehyde");
}

// ---------------------------------------------------------------------------

int main() {
  printf("\n=== AIRIQ-FRAMEWORK-001 engine simulation tests ===\n\n");

  run_test(test_startup_is_initialising_never_a_fault,
           "startup_is_initialising_never_a_fault");
  run_test(test_all_values_unknown_before_first_sample,
           "all_values_unknown_before_first_sample");
  run_test(test_per_sensor_warmup_windows_are_independent,
           "per_sensor_warmup_windows_are_independent");
  run_test(test_first_valid_sample_ends_initialisation_early,
           "first_valid_sample_ends_initialisation_early");
  run_test(test_partial_readiness_gives_honest_partial_headline,
           "partial_readiness_gives_honest_partial_headline");
  run_test(test_co2_severity_boundary_values, "co2_severity_boundary_values");
  run_test(test_voc_and_nox_severity_boundaries,
           "voc_and_nox_severity_boundaries");
  run_test(test_pm25_severity_boundaries, "pm25_severity_boundaries");
  run_test(test_severity_worsens_immediately_but_improves_with_hysteresis,
           "severity_worsens_immediately_but_improves_with_hysteresis");
  run_test(test_worst_pollutant_wins_never_averaged_away,
           "worst_pollutant_wins_never_averaged_away");
  run_test(test_worst_pollutant_tie_break_is_deterministic,
           "worst_pollutant_tie_break_is_deterministic");
  run_test(test_stale_values_do_not_count_as_good,
           "stale_values_do_not_count_as_good");
  run_test(test_one_stale_expected_sensor_degrades_but_service_remains,
           "one_stale_expected_sensor_degrades_but_service_remains");
  run_test(test_failure_and_recovery_round_trip,
           "failure_and_recovery_round_trip");
  run_test(test_optional_absent_sensors_never_degrade_health,
           "optional_absent_sensors_never_degrade_health");
  run_test(test_expected_sensor_membership_is_configuration_driven,
           "expected_sensor_membership_is_configuration_driven");
  run_test(test_hcho_participates_in_severity_only_when_expected,
           "hcho_participates_in_severity_only_when_expected");
  run_test(test_ozone_slot_behaves_like_hcho, "ozone_slot_behaves_like_hcho");
  run_test(test_unexpected_channels_still_report_severity_for_diagnostics,
           "unexpected_channels_still_report_severity_for_diagnostics");
  run_test(test_pressure_is_excluded_from_severity_and_health,
           "pressure_is_excluded_from_severity_and_health");
  run_test(test_pressure_goes_unknown_when_stale,
           "pressure_goes_unknown_when_stale");
  run_test(test_mics_channels_are_diagnostic_only,
           "mics_channels_are_diagnostic_only");
  run_test(test_mics_values_go_unknown_when_stale,
           "mics_values_go_unknown_when_stale");
  run_test(test_good_air_gives_no_action_needed,
           "good_air_gives_no_action_needed");
  run_test(test_fair_air_gives_no_action_needed,
           "fair_air_gives_no_action_needed");
  run_test(test_elevated_co2_gives_ventilate_soon_then_now,
           "elevated_co2_gives_ventilate_soon_then_now");
  run_test(test_severe_voc_or_nox_gives_ventilation_recommendation,
           "severe_voc_or_nox_gives_ventilation_recommendation");
  run_test(test_particulate_pollution_gives_conservative_source_check,
           "particulate_pollution_gives_conservative_source_check");
  run_test(test_ventilation_pollutant_outranks_pm_at_equal_severity,
           "ventilation_pollutant_outranks_pm_at_equal_severity");
  run_test(test_pm_very_poor_outranks_co2_poor,
           "pm_very_poor_outranks_co2_poor");
  run_test(test_expected_hcho_recommendation_is_source_check,
           "expected_hcho_recommendation_is_source_check");
  run_test(test_unavailable_data_gives_unavailable_recommendation,
           "unavailable_data_gives_unavailable_recommendation");
  run_test(test_invalid_samples_never_refresh_or_classify,
           "invalid_samples_never_refresh_or_classify");
  run_test(test_health_fault_is_reserved_with_no_ordinary_producer,
           "health_fault_is_reserved_with_no_ordinary_producer");
  run_test(test_data_age_diagnostics_report_seconds,
           "data_age_diagnostics_report_seconds");
  run_test(test_pm_fractions_share_the_pm_freshness_channel,
           "pm_fractions_share_the_pm_freshness_channel");
  run_test(test_state_strings_match_the_customer_contract,
           "state_strings_match_the_customer_contract");

  printf("\n=== %d/%d tests passed ===\n", passed_count, test_count);
  return (passed_count == test_count) ? 0 : 1;
}

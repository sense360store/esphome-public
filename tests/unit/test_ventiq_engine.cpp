// VENTIQ-FRAMEWORK-001 — deterministic simulation tests for the canonical
// VentIQ bathroom ventilation engine (include/sense360/ventiq_engine.h).
//
// This is the test-only simulation layer required by the accepted product
// decisions: it feeds synthetic, timestamped samples into the SAME
// header-only engine the production YAML compiles (no second implementation
// that can drift) and asserts the deterministic shower state machine,
// moisture clearing, damp/mould accumulation, odour detection, the
// air-quality consumption of the embedded canonical AirIQ engine (VOC/NOx
// severity — thresholds are never duplicated), the customer Recommendation /
// Ventilation Reason ladder, the fan-percent compatibility mapping and the
// module-health outputs for startup, warm-up, partial readiness, staleness,
// failure and recovery, invalid values and manual actions.
//
// IMPORTANT: a green run here is LOGIC/SIMULATION proof only. It is
// never hardware validation — the SGP41 path and every ventilation heuristic
// remain physically unverified until the bench checklist
// (docs/hardware/ventiq-framework-bench-checklist.md) is executed by the
// operator. All thresholds are provisional heuristics, never medical,
// health or regulatory claims.
//
// Compile via tests/Makefile (auto-discovered):  cd tests && make test

#include <cassert>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <exception>

#include "../../include/sense360/ventiq_engine.h"

using namespace sense360::ventiq;
using sense360::airiq::AIR_QUALITY_GOOD;
using sense360::airiq::AIR_QUALITY_INITIALISING;
using sense360::airiq::AIR_QUALITY_POOR;
using sense360::airiq::AIR_QUALITY_UNAVAILABLE;
using sense360::airiq::AIR_QUALITY_VERY_POOR;
using sense360::airiq::HEALTH_AVAILABLE;
using sense360::airiq::HEALTH_DEGRADED;
using sense360::airiq::HEALTH_INITIALISING;
using sense360::airiq::HEALTH_UNAVAILABLE;

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
// bench validation; mirror packages/features/ventiq_framework.yaml).
// Defaults: shower threshold 75 %RH, shower rate 5 %/min, shower end delta
// 10 %, clearing 15 min, mould threshold 65 %RH for 30 min (medium),
// humidity-high 60 %RH with 2 % hysteresis, humidity warm-up/stale 90 s,
// VOC/NOx warm-up 120 s / stale 60 s.
// ---------------------------------------------------------------------------

static const uint32_t T0 = 1000;
static const uint32_t MIN = 60000;  // one minute in ms

static VentIQEngine started_engine() {
  VentIQEngine e;
  e.begin(T0);
  return e;
}

// Feed calm, fresh inputs at time t: humidity 45 %RH, VOC/NOx Good.
static void feed_all_calm(VentIQEngine &e, uint32_t t) {
  e.input_humidity(t, 45.0f);
  e.input_temperature(t, 22.0f);
  e.input_voc(t, 80.0f);  // Good (< 150 index — AirIQ engine bands)
  e.input_nox(t, 10.0f);  // Good (< 100 index)
}

// Bring an engine to a calm, fully fresh steady state at time t.
static VentIQEngine calm_engine(uint32_t t) {
  VentIQEngine e = started_engine();
  feed_all_calm(e, t - 30000);
  feed_all_calm(e, t);
  e.evaluate(t);
  return e;
}

// ---------------------------------------------------------------------------
// Startup / warm-up honesty
// ---------------------------------------------------------------------------

TEST_CASE(startup_is_initialising_never_a_fault) {
  VentIQEngine e = started_engine();
  e.evaluate(T0 + 1000);
  ASSERT_EQ(e.demand(), DEMAND_INITIALISING);
  ASSERT_EQ(e.reason(), REASON_INITIALISING);
  ASSERT_STREQ(demand_to_string(e.demand()), "Sensor initialising");
  ASSERT_STREQ(reason_to_string(e.reason()), "Sensor initialising");
  ASSERT_EQ(e.health(), HEALTH_INITIALISING);
  ASSERT_FALSE(e.ventilation_needed());
  ASSERT_EQ(e.fan_percent(), 0);
}

TEST_CASE(startup_values_are_unknown_during_warmup) {
  VentIQEngine e = started_engine();
  e.evaluate(T0 + 1000);
  ASSERT_NAN(e.humidity());
  ASSERT_NAN(e.voc());
  ASSERT_NAN(e.nox());
  ASSERT_NAN(e.dew_point());
}

TEST_CASE(warmup_expiry_without_data_is_unavailable) {
  VentIQEngine e = started_engine();
  // Beyond every warm-up window (humidity 90 s, VOC/NOx 120 s).
  e.evaluate(T0 + 300000);
  ASSERT_EQ(e.demand(), DEMAND_UNAVAILABLE);
  ASSERT_EQ(e.reason(), REASON_UNAVAILABLE);
  ASSERT_STREQ(demand_to_string(e.demand()), "Unavailable");
  ASSERT_EQ(e.health(), HEALTH_UNAVAILABLE);
}

TEST_CASE(calm_state_needs_no_ventilation) {
  VentIQEngine e = calm_engine(T0 + 300000);
  ASSERT_EQ(e.demand(), DEMAND_NONE);
  ASSERT_EQ(e.reason(), REASON_NONE);
  ASSERT_STREQ(demand_to_string(e.demand()), "No action needed");
  ASSERT_STREQ(reason_to_string(e.reason()), "No ventilation needed");
  ASSERT_FALSE(e.ventilation_needed());
  ASSERT_EQ(e.fan_percent(), 0);
  ASSERT_NEAR(e.humidity(), 45.0f, 0.01f);
}

// ---------------------------------------------------------------------------
// Shower detection (rate and absolute triggers)
// ---------------------------------------------------------------------------

TEST_CASE(shower_starts_on_rapid_humidity_rise) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  // +6 %RH in 30 s = 12 %/min — far above the 5 %/min default.
  e.input_humidity(t + 30000, 51.0f);
  e.input_humidity(t + 60000, 57.0f);
  e.evaluate(t + 60000);
  ASSERT_TRUE(e.shower_active());
  ASSERT_EQ(e.demand(), DEMAND_NOW);
  ASSERT_EQ(e.reason(), REASON_SHOWER);
  ASSERT_STREQ(reason_to_string(e.reason()), "Shower in progress");
  ASSERT_TRUE(e.ventilation_needed());
  ASSERT_EQ(e.fan_percent(), 100);
}

TEST_CASE(shower_starts_on_absolute_humidity) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  e.input_humidity(t + 30000, 80.0f);  // >= 75 default threshold
  e.evaluate(t + 30000);
  ASSERT_TRUE(e.shower_active());
  ASSERT_EQ(e.reason(), REASON_SHOWER);
}

TEST_CASE(slow_drift_below_threshold_is_not_a_shower) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  // +1 %RH per minute, staying below 75: never a shower.
  for (int i = 1; i <= 10; i++) {
    e.input_humidity(t + i * MIN, 45.0f + i);
    e.evaluate(t + i * MIN);
  }
  ASSERT_FALSE(e.shower_active());
}

TEST_CASE(shower_ends_when_humidity_falls_and_clearing_starts) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  e.input_humidity(t + 30000, 85.0f);
  e.evaluate(t + 30000);
  ASSERT_TRUE(e.shower_active());
  // Falling humidity, below (75 - 10) with a negative rate: shower over.
  uint32_t t2 = t + 10 * MIN;
  e.input_humidity(t2, 70.0f);
  e.input_humidity(t2 + 30000, 63.0f);
  e.evaluate(t2 + 30000);
  ASSERT_FALSE(e.shower_active());
  ASSERT_EQ(e.reason(), REASON_CLEARING);
  ASSERT_STREQ(reason_to_string(e.reason()), "Clearing shower moisture");
  ASSERT_EQ(e.demand(), DEMAND_SOON);
  ASSERT_EQ(e.fan_percent(), 70);
  ASSERT_TRUE(e.clearing_minutes_remaining() > 14.0f);
}

TEST_CASE(clearing_expires_back_to_calm) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  e.input_humidity(t + 30000, 85.0f);
  e.evaluate(t + 30000);
  uint32_t t2 = t + 10 * MIN;
  e.input_humidity(t2, 70.0f);
  e.input_humidity(t2 + 30000, 55.0f);
  e.evaluate(t2 + 30000);
  ASSERT_EQ(e.reason(), REASON_CLEARING);
  // 16 minutes later (clearing default 15 min), humidity calm again.
  uint32_t t3 = t2 + 30000 + 16 * MIN;
  e.input_humidity(t3 - 30000, 48.0f);
  e.input_humidity(t3, 48.0f);
  e.evaluate(t3);
  ASSERT_EQ(e.demand(), DEMAND_NONE);
  ASSERT_NEAR(e.clearing_minutes_remaining(), 0.0f, 0.01f);
}

TEST_CASE(shower_timeout_ends_a_stuck_shower) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  e.input_humidity(t + 30000, 85.0f);
  e.evaluate(t + 30000);
  ASSERT_TRUE(e.shower_active());
  // Humidity stays high for 61+ minutes (> 60 min default max): the
  // shower state must not be claimed forever — it times out into the
  // sustained-damp story (mould accumulation continues).
  uint32_t last = t + 30000;
  for (int i = 1; i <= 62; i++) {
    last = t + 30000 + i * MIN;
    e.input_humidity(last, 85.0f);
    e.evaluate(last);
  }
  ASSERT_FALSE(e.shower_active());
  ASSERT_TRUE(e.demand() == DEMAND_NOW || e.demand() == DEMAND_SOON);
}

TEST_CASE(shower_detection_disable_switch_is_honoured) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  e.set_shower_detection_enabled(false);
  e.input_humidity(t + 30000, 85.0f);
  e.evaluate(t + 30000);
  ASSERT_FALSE(e.shower_active());
  // Absolute humidity still drives the honest humidity story instead.
  ASSERT_TRUE(e.demand() == DEMAND_SOON || e.demand() == DEMAND_NOW);
  ASSERT_TRUE(e.reason() == REASON_HUMIDITY || e.reason() == REASON_MOULD);
}

TEST_CASE(shower_threshold_is_runtime_adjustable) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  e.set_shower_threshold_pct(90.0f);
  // Suppress the (independent) rate trigger so this test isolates the
  // absolute-threshold control the customer number adjusts.
  e.set_shower_rate_threshold(500.0f);
  e.input_humidity(t + 30000, 85.0f);  // below the raised threshold
  e.evaluate(t + 30000);
  ASSERT_FALSE(e.shower_active());
  // At the default threshold (75) the same humidity WOULD have started
  // a shower via the absolute trigger.
  VentIQEngine e2 = calm_engine(t);
  e2.set_shower_rate_threshold(500.0f);
  e2.input_humidity(t + 30000, 85.0f);
  e2.evaluate(t + 30000);
  ASSERT_TRUE(e2.shower_active());
}

// ---------------------------------------------------------------------------
// Damp / mould accumulation
// ---------------------------------------------------------------------------

TEST_CASE(mould_risk_accumulates_with_sustained_damp) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  e.set_shower_detection_enabled(false);  // isolate the damp story
  ASSERT_EQ(e.mould_risk(), 0);
  uint32_t last = t;
  for (int i = 1; i <= 16; i++) {  // 16 min >= 30/2 -> low
    last = t + i * MIN;
    e.input_humidity(last, 68.0f);
    e.evaluate(last);
  }
  ASSERT_EQ(e.mould_risk(), 1);
  for (int i = 17; i <= 31; i++) {  // >= 30 min -> medium
    last = t + i * MIN;
    e.input_humidity(last, 68.0f);
    e.evaluate(last);
  }
  ASSERT_EQ(e.mould_risk(), 2);
  ASSERT_TRUE(e.mould_warning());
  ASSERT_EQ(e.demand(), DEMAND_SOON);
  ASSERT_EQ(e.reason(), REASON_MOULD);
  ASSERT_STREQ(reason_to_string(e.reason()), "Damp for a long time");
  for (int i = 32; i <= 61; i++) {  // >= 60 min -> high
    last = t + i * MIN;
    e.input_humidity(last, 68.0f);
    e.evaluate(last);
  }
  ASSERT_EQ(e.mould_risk(), 3);
  ASSERT_EQ(e.demand(), DEMAND_NOW);
  ASSERT_EQ(e.fan_percent(), 100);
}

TEST_CASE(mould_risk_resets_when_dry) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  e.set_shower_detection_enabled(false);
  uint32_t last = t;
  for (int i = 1; i <= 31; i++) {
    last = t + i * MIN;
    e.input_humidity(last, 68.0f);
    e.evaluate(last);
  }
  ASSERT_EQ(e.mould_risk(), 2);
  e.input_humidity(last + MIN, 50.0f);
  e.evaluate(last + MIN);
  ASSERT_EQ(e.mould_risk(), 0);
}

TEST_CASE(mould_accumulator_freezes_without_data) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  e.set_shower_detection_enabled(false);
  uint32_t last = t;
  for (int i = 1; i <= 20; i++) {
    last = t + i * MIN;
    e.input_humidity(last, 68.0f);
    e.evaluate(last);
  }
  ASSERT_EQ(e.mould_risk(), 1);
  // Humidity goes silent for 30 minutes: no data means no accumulation
  // AND no reset — the accumulator freezes (no claim either way).
  e.evaluate(last + 30 * MIN);
  ASSERT_EQ(e.mould_risk(), 1);
}

TEST_CASE(mould_reset_action) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  e.set_shower_detection_enabled(false);
  uint32_t last = t;
  for (int i = 1; i <= 31; i++) {
    last = t + i * MIN;
    e.input_humidity(last, 68.0f);
    e.evaluate(last);
  }
  ASSERT_TRUE(e.mould_warning());
  e.reset_mould();
  e.evaluate(last + 1000);
  ASSERT_EQ(e.mould_risk(), 0);
  ASSERT_FALSE(e.mould_warning());
}

// ---------------------------------------------------------------------------
// Humidity-high advice and hysteresis
// ---------------------------------------------------------------------------

// Raise humidity slowly (2 %RH per minute — below the 5 %/min shower
// rate trigger) so these tests isolate the high-humidity tier.
static uint32_t feed_slow_rise(VentIQEngine &e, uint32_t t, float from,
                               float to) {
  uint32_t now = t;
  for (float h = from; h <= to; h += 2.0f) {
    now += MIN;
    e.input_humidity(now, h);
    e.evaluate(now);
  }
  return now;
}

TEST_CASE(high_humidity_recommends_ventilating_soon) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  uint32_t now = feed_slow_rise(e, t, 47.0f, 62.0f);  // ends >= 60 default
  e.evaluate(now);
  ASSERT_EQ(e.demand(), DEMAND_SOON);
  ASSERT_EQ(e.reason(), REASON_HUMIDITY);
  ASSERT_STREQ(reason_to_string(e.reason()), "High humidity");
  ASSERT_EQ(e.fan_percent(), 30);
}

TEST_CASE(humidity_hysteresis_prevents_flapping) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  uint32_t now = feed_slow_rise(e, t, 47.0f, 62.0f);
  ASSERT_EQ(e.reason(), REASON_HUMIDITY);
  // 59.5 is below 60 but NOT below 60 - 2: state holds.
  e.input_humidity(now + MIN, 59.5f);
  e.evaluate(now + MIN);
  ASSERT_EQ(e.reason(), REASON_HUMIDITY);
  // Clearing the hysteresis margin releases it.
  e.input_humidity(now + 2 * MIN, 57.0f);
  e.evaluate(now + 2 * MIN);
  ASSERT_EQ(e.demand(), DEMAND_NONE);
}

// ---------------------------------------------------------------------------
// Air quality consumption (canonical AirIQ engine — no duplicate thresholds)
// ---------------------------------------------------------------------------

TEST_CASE(odour_recommends_ventilating_soon) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  // VOC index 180 = Fair per the CANONICAL AirIQ bands (150/250/400):
  // the legacy odour threshold (150) is exactly the Fair boundary.
  e.input_voc(t + 30000, 180.0f);
  e.input_humidity(t + 30000, 45.0f);
  e.evaluate(t + 30000);
  ASSERT_TRUE(e.odour());
  ASSERT_EQ(e.demand(), DEMAND_SOON);
  ASSERT_EQ(e.reason(), REASON_ODOUR);
  ASSERT_STREQ(reason_to_string(e.reason()), "Odour detected");
  ASSERT_EQ(e.fan_percent(), 50);
}

TEST_CASE(poor_air_quality_recommends_ventilating_soon) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  e.input_voc(t + 30000, 300.0f);  // Poor (>= 250 canonical band)
  e.evaluate(t + 30000);
  ASSERT_EQ(e.air_quality(), AIR_QUALITY_POOR);
  ASSERT_EQ(e.demand(), DEMAND_SOON);
  ASSERT_EQ(e.reason(), REASON_AIR_QUALITY);
  ASSERT_STREQ(reason_to_string(e.reason()), "Poor air quality");
}

TEST_CASE(very_poor_air_quality_recommends_ventilating_now) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  e.input_nox(t + 30000, 350.0f);  // Very poor (>= 300 canonical band)
  e.evaluate(t + 30000);
  ASSERT_EQ(e.air_quality(), AIR_QUALITY_VERY_POOR);
  ASSERT_EQ(e.demand(), DEMAND_NOW);
  ASSERT_EQ(e.reason(), REASON_AIR_QUALITY);
  ASSERT_EQ(e.fan_percent(), 100);
}

TEST_CASE(default_expected_pollutants_are_voc_and_nox_only) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  // No CO2 / PM producer exists on the S360-211 board: their absence
  // must never degrade anything.
  ASSERT_EQ(e.health(), HEALTH_AVAILABLE);
  ASSERT_EQ(e.air_quality(), AIR_QUALITY_GOOD);
}

// ---------------------------------------------------------------------------
// Priority ladder
// ---------------------------------------------------------------------------

TEST_CASE(priority_shower_over_air_quality) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  e.input_voc(t + 30000, 300.0f);      // Poor air
  e.input_humidity(t + 30000, 85.0f);  // and a shower
  e.evaluate(t + 30000);
  ASSERT_EQ(e.reason(), REASON_SHOWER);
  ASSERT_EQ(e.demand(), DEMAND_NOW);
}

TEST_CASE(priority_very_poor_air_over_clearing) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  e.input_humidity(t + 30000, 85.0f);
  e.evaluate(t + 30000);
  uint32_t t2 = t + 10 * MIN;
  e.input_humidity(t2, 70.0f);
  e.input_humidity(t2 + 30000, 55.0f);
  e.evaluate(t2 + 30000);
  ASSERT_EQ(e.reason(), REASON_CLEARING);
  e.input_voc(t2 + 60000, 500.0f);  // Very poor air trumps clearing
  e.input_humidity(t2 + 60000, 55.0f);
  e.evaluate(t2 + 60000);
  ASSERT_EQ(e.reason(), REASON_AIR_QUALITY);
  ASSERT_EQ(e.demand(), DEMAND_NOW);
}

// ---------------------------------------------------------------------------
// Manual actions
// ---------------------------------------------------------------------------

TEST_CASE(force_ventilation_action) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  e.force_ventilation(t + 1000, 15.0f);
  e.evaluate(t + 1000);
  ASSERT_EQ(e.demand(), DEMAND_NOW);
  ASSERT_EQ(e.reason(), REASON_REQUESTED);
  ASSERT_STREQ(reason_to_string(e.reason()), "Ventilation requested");
  ASSERT_EQ(e.fan_percent(), 100);
  // Expires after the requested window.
  feed_all_calm(e, t + 17 * MIN);
  e.evaluate(t + 17 * MIN);
  ASSERT_EQ(e.demand(), DEMAND_NONE);
}

TEST_CASE(force_ventilation_works_even_without_sensor_data) {
  VentIQEngine e = started_engine();
  e.force_ventilation(T0 + 1000, 15.0f);
  e.evaluate(T0 + 2000);
  // A manual customer request is honoured regardless of sensor state.
  ASSERT_EQ(e.demand(), DEMAND_NOW);
  ASSERT_EQ(e.reason(), REASON_REQUESTED);
}

TEST_CASE(reset_shower_action) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  e.input_humidity(t + 30000, 85.0f);
  e.evaluate(t + 30000);
  ASSERT_TRUE(e.shower_active());
  e.reset_shower(t + 60000);
  e.input_humidity(t + 60000, 45.0f);
  e.evaluate(t + 60000);
  ASSERT_FALSE(e.shower_active());
  ASSERT_NEAR(e.clearing_minutes_remaining(), 0.0f, 0.01f);
  ASSERT_EQ(e.demand(), DEMAND_NONE);
}

// ---------------------------------------------------------------------------
// Freshness honesty: stale data, degraded service, recovery
// ---------------------------------------------------------------------------

TEST_CASE(stale_humidity_goes_unknown_and_service_continues_on_air) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  // Humidity silent past its 90 s stale window; VOC/NOx keep updating.
  uint32_t t2 = t + 4 * MIN;
  e.input_voc(t2, 300.0f);
  e.input_nox(t2, 10.0f);
  e.evaluate(t2);
  ASSERT_NAN(e.humidity());
  ASSERT_FALSE(e.humidity_fresh());
  ASSERT_FALSE(e.shower_active());
  // The service stays honestly useful on the remaining fresh channel.
  ASSERT_EQ(e.demand(), DEMAND_SOON);
  ASSERT_EQ(e.reason(), REASON_AIR_QUALITY);
  // Humidity is a RoomIQ-owned input: its loss NEVER degrades the
  // VentIQ module status (the SGP41 is fresh -> Available).
  ASSERT_EQ(e.health(), HEALTH_AVAILABLE);
}

TEST_CASE(stale_voc_degrades_module_status_not_the_humidity_service) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  // VOC/NOx silent past their stale window; humidity keeps updating.
  uint32_t t2 = t + 4 * MIN;
  e.input_humidity(t2 - 30000, 62.0f);
  e.input_humidity(t2, 62.0f);
  e.evaluate(t2);
  ASSERT_NAN(e.voc());
  ASSERT_NAN(e.nox());
  ASSERT_EQ(e.health(), HEALTH_UNAVAILABLE);  // both expected channels lost
  // The humidity ventilation service keeps working.
  ASSERT_EQ(e.demand(), DEMAND_SOON);
  ASSERT_EQ(e.reason(), REASON_HUMIDITY);
}

TEST_CASE(one_stale_pollutant_channel_is_degraded) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  uint32_t t2 = t + 4 * MIN;
  e.input_voc(t2, 80.0f);  // VOC fresh; NOx silent since t
  e.input_humidity(t2, 45.0f);
  e.evaluate(t2);
  ASSERT_EQ(e.health(), HEALTH_DEGRADED);
}

TEST_CASE(everything_stale_is_unavailable) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  e.evaluate(t + 10 * MIN);  // all channels silent
  ASSERT_EQ(e.demand(), DEMAND_UNAVAILABLE);
  ASSERT_EQ(e.reason(), REASON_UNAVAILABLE);
  ASSERT_EQ(e.health(), HEALTH_UNAVAILABLE);
  ASSERT_FALSE(e.ventilation_needed());
}

TEST_CASE(recovery_after_staleness) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  e.evaluate(t + 10 * MIN);
  ASSERT_EQ(e.demand(), DEMAND_UNAVAILABLE);
  feed_all_calm(e, t + 11 * MIN);
  e.evaluate(t + 11 * MIN);
  ASSERT_EQ(e.demand(), DEMAND_NONE);
  ASSERT_EQ(e.health(), HEALTH_AVAILABLE);
}

TEST_CASE(invalid_samples_never_refresh_a_channel) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  uint32_t t2 = t + 4 * MIN;
  e.input_humidity(t2, NAN);
  e.input_humidity(t2, -5.0f);
  e.input_humidity(t2, 130.0f);  // impossible %RH
  e.input_voc(t2, NAN);
  e.input_voc(t2, -1.0f);
  e.evaluate(t2);
  ASSERT_NAN(e.humidity());
  ASSERT_NAN(e.voc());
}

// ---------------------------------------------------------------------------
// Derived values
// ---------------------------------------------------------------------------

TEST_CASE(dew_point_from_canonical_inputs) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  // Magnus formula at 22 °C / 45 %RH gives roughly 9.5 °C.
  ASSERT_NEAR(e.dew_point(), 9.5f, 0.8f);
  // Stale inputs make it unknown, never frozen.
  e.evaluate(t + 10 * MIN);
  ASSERT_NAN(e.dew_point());
}

TEST_CASE(humidity_rate_is_computed_from_timestamps) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  // Samples: 45 @ t-30 s, 45 @ t, 51 @ t+60 s. The rate uses the oldest
  // retained sample inside the 3-minute window: +6 %RH over 90 s
  // = 4 %/min (deliberately smoothed against cadence jitter).
  e.input_humidity(t + 60000, 51.0f);
  e.evaluate(t + 60000);
  ASSERT_NEAR(e.humidity_rate(), 4.0f, 0.2f);
}

TEST_CASE(fan_percent_mapping_preserves_legacy_semantics) {
  uint32_t t = T0 + 300000;
  // Legacy mapping: shower 100, clearing 70, odour 50, humidity 30.
  VentIQEngine e = calm_engine(t);
  e.input_humidity(t + 30000, 85.0f);
  e.evaluate(t + 30000);
  ASSERT_EQ(e.fan_percent(), 100);  // shower
  VentIQEngine e2 = calm_engine(t);
  e2.input_voc(t + 30000, 180.0f);
  e2.evaluate(t + 30000);
  ASSERT_EQ(e2.fan_percent(), 50);  // odour
  VentIQEngine e3 = calm_engine(t);
  feed_slow_rise(e3, t, 47.0f, 62.0f);  // below the shower rate trigger
  ASSERT_EQ(e3.fan_percent(), 30);      // elevated humidity
}

// ---------------------------------------------------------------------------
// Legacy compatibility strings (semantic upgrade — documented)
// ---------------------------------------------------------------------------

TEST_CASE(legacy_status_strings) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  ASSERT_STREQ(e.legacy_status(), "Normal");
  e.input_humidity(t + 30000, 85.0f);
  e.evaluate(t + 30000);
  ASSERT_STREQ(e.legacy_status(), "Shower in progress");
}

TEST_CASE(legacy_mould_status_strings) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  ASSERT_STREQ(e.legacy_mould_status(), "No risk");
}

TEST_CASE(legacy_ventilation_advice_strings) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  ASSERT_STREQ(e.legacy_ventilation_advice(), "No ventilation needed");
  e.input_humidity(t + 30000, 85.0f);
  e.evaluate(t + 30000);
  ASSERT_STREQ(e.legacy_ventilation_advice(), "Maximum ventilation needed");
}

TEST_CASE(legacy_air_quality_status_uses_canonical_severity) {
  uint32_t t = T0 + 300000;
  VentIQEngine e = calm_engine(t);
  ASSERT_STREQ(e.legacy_air_quality_status(), "Good");
  e.input_voc(t + 30000, 300.0f);
  e.evaluate(t + 30000);
  ASSERT_STREQ(e.legacy_air_quality_status(), "Poor");
}

// ---------------------------------------------------------------------------
// Runner
// ---------------------------------------------------------------------------

int main() {
  printf(
      "\n=== VENTIQ-FRAMEWORK-001 engine simulation (logic proof only) "
      "===\n\n");

#define RUN(name) run_test(test_##name, #name)
  RUN(startup_is_initialising_never_a_fault);
  RUN(startup_values_are_unknown_during_warmup);
  RUN(warmup_expiry_without_data_is_unavailable);
  RUN(calm_state_needs_no_ventilation);
  RUN(shower_starts_on_rapid_humidity_rise);
  RUN(shower_starts_on_absolute_humidity);
  RUN(slow_drift_below_threshold_is_not_a_shower);
  RUN(shower_ends_when_humidity_falls_and_clearing_starts);
  RUN(clearing_expires_back_to_calm);
  RUN(shower_timeout_ends_a_stuck_shower);
  RUN(shower_detection_disable_switch_is_honoured);
  RUN(shower_threshold_is_runtime_adjustable);
  RUN(mould_risk_accumulates_with_sustained_damp);
  RUN(mould_risk_resets_when_dry);
  RUN(mould_accumulator_freezes_without_data);
  RUN(mould_reset_action);
  RUN(high_humidity_recommends_ventilating_soon);
  RUN(humidity_hysteresis_prevents_flapping);
  RUN(odour_recommends_ventilating_soon);
  RUN(poor_air_quality_recommends_ventilating_soon);
  RUN(very_poor_air_quality_recommends_ventilating_now);
  RUN(default_expected_pollutants_are_voc_and_nox_only);
  RUN(priority_shower_over_air_quality);
  RUN(priority_very_poor_air_over_clearing);
  RUN(force_ventilation_action);
  RUN(force_ventilation_works_even_without_sensor_data);
  RUN(reset_shower_action);
  RUN(stale_humidity_goes_unknown_and_service_continues_on_air);
  RUN(stale_voc_degrades_module_status_not_the_humidity_service);
  RUN(one_stale_pollutant_channel_is_degraded);
  RUN(everything_stale_is_unavailable);
  RUN(recovery_after_staleness);
  RUN(invalid_samples_never_refresh_a_channel);
  RUN(dew_point_from_canonical_inputs);
  RUN(humidity_rate_is_computed_from_timestamps);
  RUN(fan_percent_mapping_preserves_legacy_semantics);
  RUN(legacy_status_strings);
  RUN(legacy_mould_status_strings);
  RUN(legacy_ventilation_advice_strings);
  RUN(legacy_air_quality_status_uses_canonical_severity);
#undef RUN

  printf("\n%d/%d tests passed\n", passed_count, test_count);
  return passed_count == test_count ? 0 : 1;
}

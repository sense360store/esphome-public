// ROOMIQ-FRAMEWORK-001 — deterministic simulation tests for the canonical
// RoomIQ environmental engine (include/sense360/roomiq_engine.h).
//
// This is the test-only simulation layer required by the accepted product
// decisions: it feeds synthetic, timestamped sensor samples into the SAME
// header-only engine the production YAML compiles (no second implementation
// that can drift) and asserts deterministic calibrated values, comfort,
// brightness, environment-state, darkness and module-health outputs for
// startup, valid updates, stale channels, calibration, hysteresis, partial
// degradation, recovery and invalid values.
//
// IMPORTANT: a green run here is LOGIC/SIMULATION proof only. It is never
// hardware validation — the SHT4x climate path and the ambient-light path
// (compiled VEML7700 vs catalog LTR-303ALS, identity unresolved) remain
// physically unverified until the bench checklist
// (docs/hardware/roomiq-framework-bench-checklist.md) is executed by the
// operator. All thresholds are provisional comfort heuristics, never
// medical, health or regulatory claims.
//
// Compile via tests/Makefile (auto-discovered):  cd tests && make test

#include "../../include/sense360/roomiq_engine.h"

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

// ---------------------------------------------------------------------------
// Fixture helpers — production engineering defaults (provisional, pending
// bench validation; mirror packages/features/roomiq_framework.yaml).
// ---------------------------------------------------------------------------

static const uint32_t T0 = 100000;
static const uint32_t CLIMATE_WARMUP = 60000;
static const uint32_t CLIMATE_STALE = 90000;
static const uint32_t LUX_WARMUP = 30000;
static const uint32_t LUX_STALE = 60000;

static RoomIQEngine make_engine() {
  RoomIQEngine engine;
  engine.set_climate_warmup_ms(CLIMATE_WARMUP);
  engine.set_climate_stale_ms(CLIMATE_STALE);
  engine.set_lux_warmup_ms(LUX_WARMUP);
  engine.set_lux_stale_ms(LUX_STALE);
  engine.set_temperature_bands(16.0f, 18.0f, 24.0f, 27.0f);
  engine.set_temperature_hysteresis(0.3f);
  engine.set_humidity_bands(30.0f, 60.0f);
  engine.set_humidity_hysteresis(2.0f);
  engine.set_brightness_bands(10.0f, 50.0f, 300.0f, 1000.0f);
  engine.set_brightness_hysteresis_pct(20.0f);
  engine.set_darkness_threshold(20.0f);
  engine.set_darkness_hysteresis(1.5f);
  engine.begin(T0);
  return engine;
}

// Feed a full set of fresh, valid samples at `t`.
static void feed_all(RoomIQEngine &engine, uint32_t t, float temp, float hum,
                     float lux) {
  engine.input_temperature(t, temp);
  engine.input_humidity(t, hum);
  engine.input_lux(t, lux);
  engine.evaluate(t);
}

// ---------------------------------------------------------------------------
// Startup / initialising
// ---------------------------------------------------------------------------

TEST_CASE(startup_is_initialising_everywhere) {
  RoomIQEngine engine = make_engine();
  engine.evaluate(T0 + 1000);
  ASSERT_EQ(engine.comfort(), COMFORT_INITIALISING);
  ASSERT_EQ(engine.brightness(), BRIGHTNESS_INITIALISING);
  ASSERT_EQ(engine.environment(), ENV_INITIALISING);
  ASSERT_EQ(engine.health(), HEALTH_INITIALISING);
  ASSERT_NAN(engine.temperature());
  ASSERT_NAN(engine.humidity());
  ASSERT_NAN(engine.illuminance());
}

TEST_CASE(first_valid_data_ends_initialising_early) {
  RoomIQEngine engine = make_engine();
  feed_all(engine, T0 + 2000, 21.0f, 45.0f, 120.0f);
  ASSERT_EQ(engine.health(), HEALTH_AVAILABLE);
  ASSERT_EQ(engine.comfort(), COMFORT_COMFORTABLE);
  ASSERT_EQ(engine.brightness(), BRIGHTNESS_NORMAL);
}

TEST_CASE(warmup_expiry_without_data_is_unavailable) {
  RoomIQEngine engine = make_engine();
  engine.evaluate(T0 + CLIMATE_WARMUP + LUX_WARMUP + 1000);
  ASSERT_EQ(engine.health(), HEALTH_UNAVAILABLE);
  ASSERT_EQ(engine.comfort(), COMFORT_UNAVAILABLE);
  ASSERT_EQ(engine.brightness(), BRIGHTNESS_UNAVAILABLE);
  ASSERT_EQ(engine.environment(), ENV_UNAVAILABLE);
}

TEST_CASE(partial_startup_lux_first_stays_initialising) {
  RoomIQEngine engine = make_engine();
  engine.input_lux(T0 + 1000, 120.0f);
  engine.evaluate(T0 + 2000);
  // Climate still inside warm-up with no data: module is initialising,
  // never degraded/unavailable during startup.
  ASSERT_EQ(engine.health(), HEALTH_INITIALISING);
  ASSERT_EQ(engine.comfort(), COMFORT_INITIALISING);
  ASSERT_EQ(engine.brightness(), BRIGHTNESS_NORMAL);
}

// ---------------------------------------------------------------------------
// Calibrated values
// ---------------------------------------------------------------------------

TEST_CASE(zero_offsets_pass_values_through) {
  RoomIQEngine engine = make_engine();
  feed_all(engine, T0 + 1000, 21.5f, 47.0f, 200.0f);
  ASSERT_NEAR(engine.temperature(), 21.5f, 0.001f);
  ASSERT_NEAR(engine.humidity(), 47.0f, 0.001f);
  ASSERT_NEAR(engine.illuminance(), 200.0f, 0.001f);
}

TEST_CASE(positive_and_negative_offsets_apply_once) {
  RoomIQEngine engine = make_engine();
  engine.set_temperature_offset(1.5f);
  engine.set_humidity_offset(-4.0f);
  feed_all(engine, T0 + 1000, 20.0f, 50.0f, 100.0f);
  ASSERT_NEAR(engine.temperature(), 21.5f, 0.001f);
  ASSERT_NEAR(engine.humidity(), 46.0f, 0.001f);
}

TEST_CASE(illuminance_scale_applies_once) {
  RoomIQEngine engine = make_engine();
  engine.set_illuminance_scale(2.0f);
  feed_all(engine, T0 + 1000, 21.0f, 45.0f, 100.0f);
  ASSERT_NEAR(engine.illuminance(), 200.0f, 0.001f);
}

TEST_CASE(offsets_are_clamped_to_safe_bounds) {
  RoomIQEngine engine = make_engine();
  engine.set_temperature_offset(50.0f);   // clamped to +15
  engine.set_humidity_offset(-80.0f);     // clamped to -30
  feed_all(engine, T0 + 1000, 20.0f, 50.0f, 100.0f);
  ASSERT_NEAR(engine.temperature(), 35.0f, 0.001f);
  ASSERT_NEAR(engine.humidity(), 20.0f, 0.001f);
}

// The calibration range must reach the S360-200-R4 provisional bench values
// (temperature ~-7.7 °C, humidity ~+17.0/+17.5 %RH). These are per-device
// prototype corrections applied through the runtime controls, never shared
// defaults. The engine clamp must not truncate them, and must agree with the
// UI number-control limits in packages/features/roomiq_framework.yaml
// (±15 °C, ±30 %RH), which tests/test_roomiq_framework.py pins.
TEST_CASE(calibration_range_reaches_bench_values) {
  RoomIQEngine engine = make_engine();
  engine.set_temperature_offset(-7.7f);
  engine.set_humidity_offset(17.5f);
  feed_all(engine, T0 + 1000, 36.0f, 25.0f, 100.0f);
  ASSERT_NEAR(engine.temperature(), 28.3f, 0.001f);   // 36.0 - 7.7
  ASSERT_NEAR(engine.humidity(), 42.5f, 0.001f);      // 25.0 + 17.5
}

// The UI limits (±15 °C, ±30 %RH) are exactly reachable — the clamp uses the
// same bounds, so a value at the edge passes through unchanged.
TEST_CASE(calibration_clamp_matches_ui_limits) {
  RoomIQEngine warm = make_engine();
  warm.set_temperature_offset(15.0f);
  warm.set_humidity_offset(30.0f);
  feed_all(warm, T0 + 1000, 10.0f, 5.0f, 100.0f);
  ASSERT_NEAR(warm.temperature(), 25.0f, 0.001f);     // 10 + 15
  ASSERT_NEAR(warm.humidity(), 35.0f, 0.001f);        // 5 + 30

  RoomIQEngine cool = make_engine();
  cool.set_temperature_offset(-15.0f);
  cool.set_humidity_offset(-30.0f);
  feed_all(cool, T0 + 1000, 30.0f, 60.0f, 100.0f);
  ASSERT_NEAR(cool.temperature(), 15.0f, 0.001f);     // 30 - 15
  ASSERT_NEAR(cool.humidity(), 30.0f, 0.001f);        // 60 - 30

  // Neutral defaults remain neutral (no calibration applied by default).
  RoomIQEngine neutral = make_engine();
  feed_all(neutral, T0 + 1000, 22.0f, 48.0f, 100.0f);
  ASSERT_NEAR(neutral.temperature(), 22.0f, 0.001f);
  ASSERT_NEAR(neutral.humidity(), 48.0f, 0.001f);
}

TEST_CASE(invalid_calibration_values_recover_safely) {
  RoomIQEngine engine = make_engine();
  engine.set_temperature_offset(NAN);      // invalid -> neutral 0
  engine.set_humidity_offset(NAN);         // invalid -> neutral 0
  engine.set_illuminance_scale(NAN);       // invalid -> neutral 1
  feed_all(engine, T0 + 1000, 20.0f, 50.0f, 100.0f);
  ASSERT_NEAR(engine.temperature(), 20.0f, 0.001f);
  ASSERT_NEAR(engine.humidity(), 50.0f, 0.001f);
  ASSERT_NEAR(engine.illuminance(), 100.0f, 0.001f);
}

TEST_CASE(zero_or_negative_scale_recovers_to_neutral) {
  RoomIQEngine engine = make_engine();
  engine.set_illuminance_scale(0.0f);
  feed_all(engine, T0 + 1000, 20.0f, 50.0f, 100.0f);
  ASSERT_NEAR(engine.illuminance(), 100.0f, 0.001f);
  engine.set_illuminance_scale(-3.0f);
  engine.evaluate(T0 + 2000);
  ASSERT_NEAR(engine.illuminance(), 100.0f, 0.001f);
}

TEST_CASE(scale_is_clamped_to_safe_bounds) {
  RoomIQEngine engine = make_engine();
  engine.set_illuminance_scale(50.0f);  // clamped to 5x
  feed_all(engine, T0 + 1000, 20.0f, 50.0f, 100.0f);
  ASSERT_NEAR(engine.illuminance(), 500.0f, 0.001f);
}

TEST_CASE(calibrated_humidity_is_clamped_to_physical_range) {
  RoomIQEngine engine = make_engine();
  engine.set_humidity_offset(10.0f);
  feed_all(engine, T0 + 1000, 20.0f, 95.0f, 100.0f);
  ASSERT_NEAR(engine.humidity(), 100.0f, 0.001f);
}

TEST_CASE(calibration_affects_comfort) {
  RoomIQEngine engine = make_engine();
  engine.set_temperature_offset(2.0f);
  feed_all(engine, T0 + 1000, 23.0f, 45.0f, 100.0f);  // calibrated 25.0
  ASSERT_EQ(engine.comfort(), COMFORT_WARM);
}

TEST_CASE(calibration_affects_brightness) {
  RoomIQEngine engine = make_engine();
  engine.set_illuminance_scale(2.0f);
  feed_all(engine, T0 + 1000, 21.0f, 45.0f, 8.0f);  // calibrated 16 lx
  ASSERT_EQ(engine.brightness(), BRIGHTNESS_DIM);
}

TEST_CASE(calibration_affects_darkness) {
  RoomIQEngine engine = make_engine();
  engine.set_illuminance_scale(0.5f);
  feed_all(engine, T0 + 1000, 21.0f, 45.0f, 30.0f);  // calibrated 15 lx
  ASSERT_EQ(engine.darkness(), DARKNESS_DARK);
}

// ---------------------------------------------------------------------------
// Comfort model (provisional heuristics; never medical/health claims)
// ---------------------------------------------------------------------------

TEST_CASE(comfortable_band) {
  RoomIQEngine engine = make_engine();
  feed_all(engine, T0 + 1000, 21.0f, 45.0f, 100.0f);
  ASSERT_EQ(engine.comfort(), COMFORT_COMFORTABLE);
  ASSERT_STREQ(comfort_to_string(engine.comfort()), "Comfortable");
}

TEST_CASE(cold_cool_warm_hot_bands) {
  RoomIQEngine cold = make_engine();
  feed_all(cold, T0 + 1000, 14.0f, 45.0f, 100.0f);
  ASSERT_EQ(cold.comfort(), COMFORT_COLD);

  RoomIQEngine cool = make_engine();
  feed_all(cool, T0 + 1000, 17.0f, 45.0f, 100.0f);
  ASSERT_EQ(cool.comfort(), COMFORT_COOL);

  RoomIQEngine warm = make_engine();
  feed_all(warm, T0 + 1000, 25.0f, 45.0f, 100.0f);
  ASSERT_EQ(warm.comfort(), COMFORT_WARM);

  RoomIQEngine hot = make_engine();
  feed_all(hot, T0 + 1000, 28.5f, 45.0f, 100.0f);
  ASSERT_EQ(hot.comfort(), COMFORT_HOT);
}

TEST_CASE(dry_and_humid_bands) {
  RoomIQEngine dry = make_engine();
  feed_all(dry, T0 + 1000, 21.0f, 22.0f, 100.0f);
  ASSERT_EQ(dry.comfort(), COMFORT_DRY);

  RoomIQEngine humid = make_engine();
  feed_all(humid, T0 + 1000, 21.0f, 70.0f, 100.0f);
  ASSERT_EQ(humid.comfort(), COMFORT_HUMID);
}

TEST_CASE(warm_and_humid_combined_state) {
  RoomIQEngine engine = make_engine();
  feed_all(engine, T0 + 1000, 25.5f, 70.0f, 100.0f);
  ASSERT_EQ(engine.comfort(), COMFORT_WARM_HUMID);
  ASSERT_STREQ(comfort_to_string(engine.comfort()), "Warm and humid");

  RoomIQEngine hot_humid = make_engine();
  feed_all(hot_humid, T0 + 1000, 29.0f, 75.0f, 100.0f);
  ASSERT_EQ(hot_humid.comfort(), COMFORT_WARM_HUMID);
}

TEST_CASE(temperature_discomfort_outranks_humidity) {
  RoomIQEngine engine = make_engine();
  feed_all(engine, T0 + 1000, 14.0f, 75.0f, 100.0f);
  // Combined severe is warm/hot + humid only; cold + humid reports the
  // temperature problem (documented precedence).
  ASSERT_EQ(engine.comfort(), COMFORT_COLD);
}

TEST_CASE(comfort_temperature_hysteresis_prevents_flapping) {
  RoomIQEngine engine = make_engine();
  feed_all(engine, T0 + 1000, 23.0f, 45.0f, 100.0f);
  ASSERT_EQ(engine.comfort(), COMFORT_COMFORTABLE);
  // Slightly over the boundary but within hysteresis: hold Comfortable.
  feed_all(engine, T0 + 2000, 24.1f, 45.0f, 100.0f);
  ASSERT_EQ(engine.comfort(), COMFORT_COMFORTABLE);
  // Clearly over the boundary + hysteresis: Warm.
  feed_all(engine, T0 + 3000, 24.4f, 45.0f, 100.0f);
  ASSERT_EQ(engine.comfort(), COMFORT_WARM);
  // Slightly under the boundary but within hysteresis: hold Warm.
  feed_all(engine, T0 + 4000, 23.8f, 45.0f, 100.0f);
  ASSERT_EQ(engine.comfort(), COMFORT_WARM);
  // Clearly under: Comfortable again.
  feed_all(engine, T0 + 5000, 23.6f, 45.0f, 100.0f);
  ASSERT_EQ(engine.comfort(), COMFORT_COMFORTABLE);
}

TEST_CASE(comfort_humidity_hysteresis_prevents_flapping) {
  RoomIQEngine engine = make_engine();
  feed_all(engine, T0 + 1000, 21.0f, 59.0f, 100.0f);
  ASSERT_EQ(engine.comfort(), COMFORT_COMFORTABLE);
  feed_all(engine, T0 + 2000, 21.0f, 61.0f, 100.0f);  // within +2 hysteresis
  ASSERT_EQ(engine.comfort(), COMFORT_COMFORTABLE);
  feed_all(engine, T0 + 3000, 21.0f, 62.5f, 100.0f);
  ASSERT_EQ(engine.comfort(), COMFORT_HUMID);
  feed_all(engine, T0 + 4000, 21.0f, 58.5f, 100.0f);  // within -2 hysteresis
  ASSERT_EQ(engine.comfort(), COMFORT_HUMID);
  feed_all(engine, T0 + 5000, 21.0f, 57.5f, 100.0f);
  ASSERT_EQ(engine.comfort(), COMFORT_COMFORTABLE);
}

TEST_CASE(comfort_requires_both_climate_channels) {
  RoomIQEngine engine = make_engine();
  feed_all(engine, T0 + 1000, 21.0f, 45.0f, 100.0f);
  // Humidity goes stale (temperature keeps updating): comfort is honest
  // about the missing input instead of computing from stale data.
  uint32_t t = T0 + 1000 + CLIMATE_STALE + 5000;
  engine.input_temperature(t, 21.0f);
  engine.input_lux(t, 100.0f);
  engine.evaluate(t);
  ASSERT_EQ(engine.comfort(), COMFORT_UNAVAILABLE);
  ASSERT_EQ(engine.health(), HEALTH_DEGRADED);
}

// ---------------------------------------------------------------------------
// Brightness model
// ---------------------------------------------------------------------------

TEST_CASE(brightness_categories) {
  struct Case {
    float lux;
    Brightness expected;
  } cases[] = {
      {5.0f, BRIGHTNESS_DARK},        {30.0f, BRIGHTNESS_DIM},
      {100.0f, BRIGHTNESS_NORMAL},    {500.0f, BRIGHTNESS_BRIGHT},
      {1500.0f, BRIGHTNESS_VERY_BRIGHT},
  };
  for (const Case &c : cases) {
    RoomIQEngine engine = make_engine();
    feed_all(engine, T0 + 1000, 21.0f, 45.0f, c.lux);
    ASSERT_EQ(engine.brightness(), c.expected);
  }
}

TEST_CASE(brightness_hysteresis_prevents_flapping) {
  RoomIQEngine engine = make_engine();
  feed_all(engine, T0 + 1000, 21.0f, 45.0f, 55.0f);
  ASSERT_EQ(engine.brightness(), BRIGHTNESS_NORMAL);
  // Dropping just below the boundary holds (20% falling margin: 40 lx).
  feed_all(engine, T0 + 2000, 21.0f, 45.0f, 45.0f);
  ASSERT_EQ(engine.brightness(), BRIGHTNESS_NORMAL);
  // Dropping clearly below the margin moves to Dim.
  feed_all(engine, T0 + 3000, 21.0f, 45.0f, 39.0f);
  ASSERT_EQ(engine.brightness(), BRIGHTNESS_DIM);
  // Rising crosses the plain boundary immediately.
  feed_all(engine, T0 + 4000, 21.0f, 45.0f, 51.0f);
  ASSERT_EQ(engine.brightness(), BRIGHTNESS_NORMAL);
}

TEST_CASE(stale_lux_is_unavailable_never_dark) {
  RoomIQEngine engine = make_engine();
  feed_all(engine, T0 + 1000, 21.0f, 45.0f, 100.0f);
  uint32_t t = T0 + 1000 + LUX_STALE + 5000;
  engine.input_temperature(t, 21.0f);
  engine.input_humidity(t, 45.0f);
  engine.evaluate(t);
  ASSERT_EQ(engine.brightness(), BRIGHTNESS_UNAVAILABLE);
  ASSERT_EQ(engine.darkness(), DARKNESS_UNKNOWN);
  ASSERT_NAN(engine.illuminance());
  // Climate stays usable: comfort remains available, module degraded.
  ASSERT_EQ(engine.comfort(), COMFORT_COMFORTABLE);
  ASSERT_EQ(engine.health(), HEALTH_DEGRADED);
}

TEST_CASE(invalid_lux_is_not_a_valid_update_and_never_dark) {
  RoomIQEngine engine = make_engine();
  engine.input_lux(T0 + 1000, NAN);
  engine.evaluate(T0 + 2000);
  ASSERT_EQ(engine.brightness(), BRIGHTNESS_INITIALISING);
  ASSERT_EQ(engine.darkness(), DARKNESS_UNKNOWN);
}

TEST_CASE(brightness_recovers_after_stale) {
  RoomIQEngine engine = make_engine();
  feed_all(engine, T0 + 1000, 21.0f, 45.0f, 100.0f);
  uint32_t t = T0 + 1000 + LUX_STALE + 5000;
  engine.evaluate(t);
  ASSERT_EQ(engine.brightness(), BRIGHTNESS_UNAVAILABLE);
  feed_all(engine, t + 1000, 21.0f, 45.0f, 100.0f);
  ASSERT_EQ(engine.brightness(), BRIGHTNESS_NORMAL);
  ASSERT_EQ(engine.health(), HEALTH_AVAILABLE);
}

// ---------------------------------------------------------------------------
// Darkness service (consumed by the LED framework — LED semantics preserved)
// ---------------------------------------------------------------------------

TEST_CASE(darkness_threshold_and_hysteresis) {
  RoomIQEngine engine = make_engine();
  feed_all(engine, T0 + 1000, 21.0f, 45.0f, 19.0f);
  ASSERT_EQ(engine.darkness(), DARKNESS_DARK);
  // Between threshold (20) and threshold*1.5 (30): hold dark.
  feed_all(engine, T0 + 2000, 21.0f, 45.0f, 25.0f);
  ASSERT_EQ(engine.darkness(), DARKNESS_DARK);
  feed_all(engine, T0 + 3000, 21.0f, 45.0f, 31.0f);
  ASSERT_EQ(engine.darkness(), DARKNESS_NOT_DARK);
  feed_all(engine, T0 + 4000, 21.0f, 45.0f, 25.0f);
  ASSERT_EQ(engine.darkness(), DARKNESS_NOT_DARK);
  feed_all(engine, T0 + 5000, 21.0f, 45.0f, 19.0f);
  ASSERT_EQ(engine.darkness(), DARKNESS_DARK);
}

TEST_CASE(darkness_threshold_is_runtime_configurable) {
  RoomIQEngine engine = make_engine();
  feed_all(engine, T0 + 1000, 21.0f, 45.0f, 60.0f);
  ASSERT_EQ(engine.darkness(), DARKNESS_NOT_DARK);
  engine.set_darkness_threshold(100.0f);
  feed_all(engine, T0 + 2000, 21.0f, 45.0f, 60.0f);
  ASSERT_EQ(engine.darkness(), DARKNESS_DARK);
}

TEST_CASE(darkness_unknown_before_first_sample) {
  RoomIQEngine engine = make_engine();
  engine.evaluate(T0 + 1000);
  ASSERT_EQ(engine.darkness(), DARKNESS_UNKNOWN);
}

// ---------------------------------------------------------------------------
// Environment State (deterministic precedence)
// ---------------------------------------------------------------------------

TEST_CASE(environment_comfortable_normal_light) {
  RoomIQEngine engine = make_engine();
  feed_all(engine, T0 + 1000, 21.0f, 45.0f, 100.0f);
  ASSERT_EQ(engine.environment(), ENV_COMFORTABLE);
}

TEST_CASE(environment_reports_climate_discomfort_first) {
  RoomIQEngine hot = make_engine();
  feed_all(hot, T0 + 1000, 29.0f, 45.0f, 5.0f);  // hot AND dark
  ASSERT_EQ(hot.environment(), ENV_HOT);  // severe outranks light

  RoomIQEngine combined = make_engine();
  feed_all(combined, T0 + 1000, 26.0f, 72.0f, 5.0f);
  ASSERT_EQ(combined.environment(), ENV_WARM_HUMID);
}

TEST_CASE(environment_elevates_notable_light_when_comfortable) {
  RoomIQEngine dark = make_engine();
  feed_all(dark, T0 + 1000, 21.0f, 45.0f, 5.0f);
  ASSERT_EQ(dark.environment(), ENV_DARK);

  RoomIQEngine bright = make_engine();
  feed_all(bright, T0 + 1000, 21.0f, 45.0f, 2000.0f);
  ASSERT_EQ(bright.environment(), ENV_BRIGHT);

  // Dim / Normal / Bright bands are unremarkable — Comfortable stays the
  // headline (no duplication of the Brightness entity).
  RoomIQEngine dim = make_engine();
  feed_all(dim, T0 + 1000, 21.0f, 45.0f, 30.0f);
  ASSERT_EQ(dim.environment(), ENV_COMFORTABLE);
}

TEST_CASE(environment_partial_data_is_honest) {
  // Climate stale + fresh dark lux -> the light condition is still a true,
  // useful headline.
  RoomIQEngine engine = make_engine();
  feed_all(engine, T0 + 1000, 21.0f, 45.0f, 5.0f);
  uint32_t t = T0 + 1000 + CLIMATE_STALE + 5000;
  engine.input_lux(t, 5.0f);
  engine.evaluate(t);
  ASSERT_EQ(engine.environment(), ENV_DARK);

  // Climate stale + unremarkable light -> Unavailable (never a fabricated
  // climate statement).
  RoomIQEngine engine2 = make_engine();
  feed_all(engine2, T0 + 1000, 21.0f, 45.0f, 100.0f);
  engine2.input_lux(t, 100.0f);
  engine2.evaluate(t);
  ASSERT_EQ(engine2.environment(), ENV_UNAVAILABLE);
}

TEST_CASE(environment_all_stale_is_unavailable) {
  RoomIQEngine engine = make_engine();
  feed_all(engine, T0 + 1000, 21.0f, 45.0f, 100.0f);
  uint32_t t = T0 + 1000 + CLIMATE_STALE + LUX_STALE + 5000;
  engine.evaluate(t);
  ASSERT_EQ(engine.environment(), ENV_UNAVAILABLE);
  ASSERT_EQ(engine.health(), HEALTH_UNAVAILABLE);
}

TEST_CASE(environment_never_contradicts_comfort) {
  // For every fresh climate state, the environment either equals the
  // comfort statement or adds light information on top of Comfortable.
  struct Case {
    float temp, hum;
  } cases[] = {{14.0f, 45.0f}, {17.0f, 45.0f}, {21.0f, 45.0f},
               {25.0f, 45.0f}, {29.0f, 45.0f}, {21.0f, 20.0f},
               {21.0f, 75.0f}, {26.0f, 75.0f}};
  for (const Case &c : cases) {
    RoomIQEngine engine = make_engine();
    feed_all(engine, T0 + 1000, c.temp, c.hum, 100.0f);
    if (engine.comfort() != COMFORT_COMFORTABLE) {
      ASSERT_STREQ(environment_to_string(engine.environment()),
                   comfort_to_string(engine.comfort()));
    } else {
      ASSERT_EQ(engine.environment(), ENV_COMFORTABLE);
    }
  }
}

// ---------------------------------------------------------------------------
// Module health
// ---------------------------------------------------------------------------

TEST_CASE(health_all_fresh_is_available) {
  RoomIQEngine engine = make_engine();
  feed_all(engine, T0 + 1000, 21.0f, 45.0f, 100.0f);
  ASSERT_EQ(engine.health(), HEALTH_AVAILABLE);
  ASSERT_STREQ(health_to_string(engine.health()), "Available");
}

TEST_CASE(health_lux_stale_climate_fresh_is_degraded) {
  RoomIQEngine engine = make_engine();
  feed_all(engine, T0 + 1000, 21.0f, 45.0f, 100.0f);
  uint32_t t = T0 + 1000 + LUX_STALE + 5000;
  engine.input_temperature(t, 21.0f);
  engine.input_humidity(t, 45.0f);
  engine.evaluate(t);
  ASSERT_EQ(engine.health(), HEALTH_DEGRADED);
  ASSERT_EQ(engine.comfort(), COMFORT_COMFORTABLE);
}

TEST_CASE(health_climate_stale_lux_fresh_is_degraded) {
  RoomIQEngine engine = make_engine();
  feed_all(engine, T0 + 1000, 21.0f, 45.0f, 100.0f);
  uint32_t t = T0 + 1000 + CLIMATE_STALE + 5000;
  engine.input_lux(t, 100.0f);
  engine.evaluate(t);
  ASSERT_EQ(engine.health(), HEALTH_DEGRADED);
  ASSERT_EQ(engine.comfort(), COMFORT_UNAVAILABLE);
  ASSERT_EQ(engine.brightness(), BRIGHTNESS_NORMAL);
}

TEST_CASE(health_everything_stale_is_unavailable) {
  RoomIQEngine engine = make_engine();
  feed_all(engine, T0 + 1000, 21.0f, 45.0f, 100.0f);
  uint32_t t = T0 + 1000 + CLIMATE_STALE + LUX_STALE + 10000;
  engine.evaluate(t);
  ASSERT_EQ(engine.health(), HEALTH_UNAVAILABLE);
}

TEST_CASE(health_recovers_after_fresh_data) {
  RoomIQEngine engine = make_engine();
  feed_all(engine, T0 + 1000, 21.0f, 45.0f, 100.0f);
  uint32_t t = T0 + 1000 + CLIMATE_STALE + LUX_STALE + 10000;
  engine.evaluate(t);
  ASSERT_EQ(engine.health(), HEALTH_UNAVAILABLE);
  feed_all(engine, t + 1000, 21.0f, 45.0f, 100.0f);
  ASSERT_EQ(engine.health(), HEALTH_AVAILABLE);
}

TEST_CASE(explicit_fault_is_reported_only_when_set) {
  RoomIQEngine engine = make_engine();
  feed_all(engine, T0 + 1000, 21.0f, 45.0f, 100.0f);
  // No composed component exposes a supported fault signal today; the
  // engine contract exists for a future real signal.
  ASSERT_EQ(engine.health(), HEALTH_AVAILABLE);
  engine.set_fault(true);
  engine.evaluate(T0 + 2000);
  ASSERT_EQ(engine.health(), HEALTH_FAULT);
  engine.set_fault(false);
  engine.evaluate(T0 + 3000);
  ASSERT_EQ(engine.health(), HEALTH_AVAILABLE);
}

TEST_CASE(stale_values_are_never_reported_as_real) {
  RoomIQEngine engine = make_engine();
  feed_all(engine, T0 + 1000, 21.0f, 45.0f, 100.0f);
  uint32_t t = T0 + 1000 + CLIMATE_STALE + LUX_STALE + 10000;
  engine.evaluate(t);
  ASSERT_NAN(engine.temperature());
  ASSERT_NAN(engine.humidity());
  ASSERT_NAN(engine.illuminance());
  ASSERT_NAN(engine.heat_index());
}

TEST_CASE(invalid_climate_sample_is_ignored) {
  RoomIQEngine engine = make_engine();
  engine.input_temperature(T0 + 1000, NAN);
  engine.input_humidity(T0 + 1000, NAN);
  engine.evaluate(T0 + 2000);
  ASSERT_EQ(engine.comfort(), COMFORT_INITIALISING);
  ASSERT_NAN(engine.temperature());
}

// ---------------------------------------------------------------------------
// Legacy compatibility outputs (pre-framework entity semantics)
// ---------------------------------------------------------------------------

TEST_CASE(legacy_heat_index_matches_formula) {
  RoomIQEngine engine = make_engine();
  feed_all(engine, T0 + 1000, 30.0f, 70.0f, 100.0f);
  // Rothfusz regression at 30 C / 70 %RH is approximately 35 C.
  ASSERT_NEAR(engine.heat_index(), 35.0f, 1.5f);

  RoomIQEngine mild = make_engine();
  feed_all(mild, T0 + 1000, 21.0f, 45.0f, 100.0f);
  ASSERT_NEAR(mild.heat_index(), 21.0f, 0.001f);  // below activation: temp
}

TEST_CASE(legacy_comfort_score_matches_formula) {
  RoomIQEngine engine = make_engine();
  feed_all(engine, T0 + 1000, 22.0f, 50.0f, 100.0f);
  ASSERT_NEAR(engine.legacy_comfort_score(), 100.0f, 0.001f);

  RoomIQEngine chilly = make_engine();
  feed_all(chilly, T0 + 1000, 16.0f, 50.0f, 100.0f);
  // temp_score 80, humidity_score 100 -> 90.
  ASSERT_NEAR(chilly.legacy_comfort_score(), 90.0f, 0.001f);
  ASSERT_STREQ(chilly.legacy_comfort_status(), "Excellent");
}

TEST_CASE(legacy_light_status_maps_canonical_brightness) {
  RoomIQEngine engine = make_engine();
  feed_all(engine, T0 + 1000, 21.0f, 45.0f, 1500.0f);
  // Very bright maps onto the legacy 4-value vocabulary as "Bright".
  ASSERT_STREQ(engine.legacy_light_status(), "Bright");
  RoomIQEngine dark = make_engine();
  feed_all(dark, T0 + 1000, 21.0f, 45.0f, 5.0f);
  ASSERT_STREQ(dark.legacy_light_status(), "Dark");
}

TEST_CASE(legacy_advice_strings_preserved) {
  RoomIQEngine cold = make_engine();
  feed_all(cold, T0 + 1000, 17.0f, 50.0f, 100.0f);
  ASSERT_STREQ(cold.legacy_temperature_advice(), "Too cold - consider heating");

  RoomIQEngine ideal = make_engine();
  feed_all(ideal, T0 + 1000, 22.0f, 50.0f, 100.0f);
  ASSERT_STREQ(ideal.legacy_temperature_advice(), "Ideal temperature");
  ASSERT_STREQ(ideal.legacy_humidity_advice(), "Ideal humidity");

  RoomIQEngine damp = make_engine();
  feed_all(damp, T0 + 1000, 22.0f, 75.0f, 100.0f);
  ASSERT_STREQ(damp.legacy_humidity_advice(),
               "Too humid - consider dehumidifier");

  RoomIQEngine offline = make_engine();
  offline.evaluate(T0 + 1000);
  ASSERT_STREQ(offline.legacy_temperature_advice(), "Sensor unavailable");
}

// ---------------------------------------------------------------------------
// String vocabularies
// ---------------------------------------------------------------------------

TEST_CASE(state_strings_are_customer_wording) {
  ASSERT_STREQ(comfort_to_string(COMFORT_INITIALISING), "Initialising");
  ASSERT_STREQ(comfort_to_string(COMFORT_COLD), "Cold");
  ASSERT_STREQ(comfort_to_string(COMFORT_COOL), "Cool");
  ASSERT_STREQ(comfort_to_string(COMFORT_WARM), "Warm");
  ASSERT_STREQ(comfort_to_string(COMFORT_HOT), "Hot");
  ASSERT_STREQ(comfort_to_string(COMFORT_DRY), "Dry");
  ASSERT_STREQ(comfort_to_string(COMFORT_HUMID), "Humid");
  ASSERT_STREQ(comfort_to_string(COMFORT_UNAVAILABLE), "Unavailable");
  ASSERT_STREQ(brightness_to_string(BRIGHTNESS_DARK), "Dark");
  ASSERT_STREQ(brightness_to_string(BRIGHTNESS_DIM), "Dim");
  ASSERT_STREQ(brightness_to_string(BRIGHTNESS_NORMAL), "Normal");
  ASSERT_STREQ(brightness_to_string(BRIGHTNESS_BRIGHT), "Bright");
  ASSERT_STREQ(brightness_to_string(BRIGHTNESS_VERY_BRIGHT), "Very bright");
  ASSERT_STREQ(environment_to_string(ENV_DARK), "Dark");
  ASSERT_STREQ(environment_to_string(ENV_BRIGHT), "Bright");
  ASSERT_STREQ(health_to_string(HEALTH_INITIALISING), "Initialising");
  ASSERT_STREQ(health_to_string(HEALTH_DEGRADED), "Degraded");
  ASSERT_STREQ(darkness_to_string(DARKNESS_UNKNOWN), "Unknown");
  ASSERT_STREQ(darkness_to_string(DARKNESS_DARK), "Dark");
  ASSERT_STREQ(darkness_to_string(DARKNESS_NOT_DARK), "Not dark");
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

int main() {
  printf("\nROOMIQ-FRAMEWORK-001 engine simulation tests\n");
  printf("=============================================\n");
  printf("LOGIC/SIMULATION PROOF ONLY — never hardware validation.\n\n");

  run_test(test_startup_is_initialising_everywhere,
           "startup_is_initialising_everywhere");
  run_test(test_first_valid_data_ends_initialising_early,
           "first_valid_data_ends_initialising_early");
  run_test(test_warmup_expiry_without_data_is_unavailable,
           "warmup_expiry_without_data_is_unavailable");
  run_test(test_partial_startup_lux_first_stays_initialising,
           "partial_startup_lux_first_stays_initialising");
  run_test(test_zero_offsets_pass_values_through,
           "zero_offsets_pass_values_through");
  run_test(test_positive_and_negative_offsets_apply_once,
           "positive_and_negative_offsets_apply_once");
  run_test(test_illuminance_scale_applies_once,
           "illuminance_scale_applies_once");
  run_test(test_offsets_are_clamped_to_safe_bounds,
           "offsets_are_clamped_to_safe_bounds");
  run_test(test_calibration_range_reaches_bench_values,
           "calibration_range_reaches_bench_values");
  run_test(test_calibration_clamp_matches_ui_limits,
           "calibration_clamp_matches_ui_limits");
  run_test(test_invalid_calibration_values_recover_safely,
           "invalid_calibration_values_recover_safely");
  run_test(test_zero_or_negative_scale_recovers_to_neutral,
           "zero_or_negative_scale_recovers_to_neutral");
  run_test(test_scale_is_clamped_to_safe_bounds,
           "scale_is_clamped_to_safe_bounds");
  run_test(test_calibrated_humidity_is_clamped_to_physical_range,
           "calibrated_humidity_is_clamped_to_physical_range");
  run_test(test_calibration_affects_comfort, "calibration_affects_comfort");
  run_test(test_calibration_affects_brightness,
           "calibration_affects_brightness");
  run_test(test_calibration_affects_darkness,
           "calibration_affects_darkness");
  run_test(test_comfortable_band, "comfortable_band");
  run_test(test_cold_cool_warm_hot_bands, "cold_cool_warm_hot_bands");
  run_test(test_dry_and_humid_bands, "dry_and_humid_bands");
  run_test(test_warm_and_humid_combined_state,
           "warm_and_humid_combined_state");
  run_test(test_temperature_discomfort_outranks_humidity,
           "temperature_discomfort_outranks_humidity");
  run_test(test_comfort_temperature_hysteresis_prevents_flapping,
           "comfort_temperature_hysteresis_prevents_flapping");
  run_test(test_comfort_humidity_hysteresis_prevents_flapping,
           "comfort_humidity_hysteresis_prevents_flapping");
  run_test(test_comfort_requires_both_climate_channels,
           "comfort_requires_both_climate_channels");
  run_test(test_brightness_categories, "brightness_categories");
  run_test(test_brightness_hysteresis_prevents_flapping,
           "brightness_hysteresis_prevents_flapping");
  run_test(test_stale_lux_is_unavailable_never_dark,
           "stale_lux_is_unavailable_never_dark");
  run_test(test_invalid_lux_is_not_a_valid_update_and_never_dark,
           "invalid_lux_is_not_a_valid_update_and_never_dark");
  run_test(test_brightness_recovers_after_stale,
           "brightness_recovers_after_stale");
  run_test(test_darkness_threshold_and_hysteresis,
           "darkness_threshold_and_hysteresis");
  run_test(test_darkness_threshold_is_runtime_configurable,
           "darkness_threshold_is_runtime_configurable");
  run_test(test_darkness_unknown_before_first_sample,
           "darkness_unknown_before_first_sample");
  run_test(test_environment_comfortable_normal_light,
           "environment_comfortable_normal_light");
  run_test(test_environment_reports_climate_discomfort_first,
           "environment_reports_climate_discomfort_first");
  run_test(test_environment_elevates_notable_light_when_comfortable,
           "environment_elevates_notable_light_when_comfortable");
  run_test(test_environment_partial_data_is_honest,
           "environment_partial_data_is_honest");
  run_test(test_environment_all_stale_is_unavailable,
           "environment_all_stale_is_unavailable");
  run_test(test_environment_never_contradicts_comfort,
           "environment_never_contradicts_comfort");
  run_test(test_health_all_fresh_is_available,
           "health_all_fresh_is_available");
  run_test(test_health_lux_stale_climate_fresh_is_degraded,
           "health_lux_stale_climate_fresh_is_degraded");
  run_test(test_health_climate_stale_lux_fresh_is_degraded,
           "health_climate_stale_lux_fresh_is_degraded");
  run_test(test_health_everything_stale_is_unavailable,
           "health_everything_stale_is_unavailable");
  run_test(test_health_recovers_after_fresh_data,
           "health_recovers_after_fresh_data");
  run_test(test_explicit_fault_is_reported_only_when_set,
           "explicit_fault_is_reported_only_when_set");
  run_test(test_stale_values_are_never_reported_as_real,
           "stale_values_are_never_reported_as_real");
  run_test(test_invalid_climate_sample_is_ignored,
           "invalid_climate_sample_is_ignored");
  run_test(test_legacy_heat_index_matches_formula,
           "legacy_heat_index_matches_formula");
  run_test(test_legacy_comfort_score_matches_formula,
           "legacy_comfort_score_matches_formula");
  run_test(test_legacy_light_status_maps_canonical_brightness,
           "legacy_light_status_maps_canonical_brightness");
  run_test(test_legacy_advice_strings_preserved,
           "legacy_advice_strings_preserved");
  run_test(test_state_strings_are_customer_wording,
           "state_strings_are_customer_wording");

  printf("\n=============================================\n");
  printf("Results: %d/%d tests passed\n", passed_count, test_count);
  if (passed_count == test_count) {
    printf("All RoomIQ engine simulation tests passed.\n");
    return 0;
  }
  printf("SOME TESTS FAILED\n");
  return 1;
}

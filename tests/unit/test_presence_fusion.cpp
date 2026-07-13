// PRESENCE-FRAMEWORK-001 — deterministic simulation tests for the tri-sensor
// Presence fusion engine (include/sense360/presence_fusion.h).
//
// This is the test-only simulation layer required by the accepted product
// decisions: it feeds synthetic, timestamped sensor events into the SAME
// header-only engine the production YAML compiles (no second implementation
// that can drift) and asserts deterministic occupancy / customer status /
// module-health outputs for startup, movement, static presence, multiple
// targets, stale data, sensor failure and recovery.
//
// IMPORTANT: a green run here is LOGIC/SIMULATION proof only. It is never
// hardware validation — PIR, LD2450 and SEN0609 physical behaviour remains
// unverified until the bench checklist
// (docs/hardware/presence-framework-bench-checklist.md) is executed by the
// operator.
//
// Compile via tests/Makefile (auto-discovered):  cd tests && make test

#include "../../include/sense360/presence_fusion.h"

#include <cassert>
#include <cstdio>
#include <cstring>
#include <exception>

using namespace sense360::presence;

// Simple test framework (repo convention — see test_led_logic.cpp)
#define TEST_CASE(name) void test_##name()
#define ASSERT_TRUE(cond) assert(cond)
#define ASSERT_FALSE(cond) assert(!(cond))
#define ASSERT_EQ(a, b) assert((a) == (b))
#define ASSERT_STREQ(a, b) assert(std::strcmp((a), (b)) == 0)

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
// Fixture helpers
// ---------------------------------------------------------------------------

// Warm-up windows used by the production package (engineering defaults,
// pending bench tuning): PIR 30 s, LD2450 10 s, SEN0609 15 s. Radar frames
// are considered stale after 5 s without an update.
static const uint32_t PIR_WARMUP = 30000;
static const uint32_t RADAR_WARMUP = 10000;
static const uint32_t STATIC_WARMUP = 15000;
static const uint32_t RADAR_STALE = 5000;

// A time safely past every warm-up window.
static const uint32_t T_READY = 60000;

// Tri-sensor RoomIQ composition: PIR + LD2450 + SEN0609 all expected.
// PIR and the SEN0609 digital output are GPIO levels: usable as presence
// triggers, but they carry no communication signal, so they are configured
// as non-verifiable (they can never be proven fresh OR proven failed).
FusionEngine tri_engine() {
  FusionEngine engine;
  engine.configure_pir(ChannelConfig{true, false, PIR_WARMUP, 0});
  engine.configure_radar(ChannelConfig{true, true, RADAR_WARMUP, RADAR_STALE});
  engine.configure_static(ChannelConfig{true, false, STATIC_WARMUP, 0});
  engine.evaluate(0);  // boot
  return engine;
}

// Radar-only composition (e.g. a future radar-only product): the expected
// sensor set is configuration-driven; PIR / SEN0609 absence is not a fault.
FusionEngine radar_only_engine() {
  FusionEngine engine;
  engine.configure_pir(ChannelConfig{false, false, PIR_WARMUP, 0});
  engine.configure_radar(ChannelConfig{true, true, RADAR_WARMUP, RADAR_STALE});
  engine.configure_static(ChannelConfig{false, false, STATIC_WARMUP, 0});
  engine.evaluate(0);
  return engine;
}

// Synthetic composition where the static channel is verifiable too — used
// to exercise the generic health state machine (two verifiable sensors).
FusionEngine dual_verifiable_engine(bool pir_expected) {
  FusionEngine engine;
  engine.configure_pir(ChannelConfig{pir_expected, false, PIR_WARMUP, 0});
  engine.configure_radar(ChannelConfig{true, true, RADAR_WARMUP, RADAR_STALE});
  engine.configure_static(ChannelConfig{true, true, STATIC_WARMUP, RADAR_STALE});
  engine.evaluate(0);
  return engine;
}

// Drive an engine to T_READY with everything quiet but the radar healthy
// (frames every second reporting an empty room).
void settle_clear(FusionEngine &engine, uint32_t until = T_READY) {
  for (uint32_t t = 1000; t <= until; t += 1000) {
    engine.input_radar_frame(t, 0, 0, 0);
    engine.evaluate(t);
  }
}

// ---------------------------------------------------------------------------
// Fusion: occupancy assertion
// ---------------------------------------------------------------------------

TEST_CASE(pir_alone_asserts_occupancy_immediately) {
  FusionEngine engine = tri_engine();
  settle_clear(engine);
  ASSERT_FALSE(engine.occupancy());
  engine.input_pir(T_READY + 100, true);
  engine.evaluate(T_READY + 100);
  ASSERT_TRUE(engine.occupancy());
}

TEST_CASE(radar_moving_target_asserts_occupancy) {
  FusionEngine engine = tri_engine();
  settle_clear(engine);
  engine.input_radar_frame(T_READY + 1000, 1, 1, 0);
  engine.evaluate(T_READY + 1000);
  ASSERT_TRUE(engine.occupancy());
}

TEST_CASE(radar_still_target_asserts_occupancy) {
  FusionEngine engine = tri_engine();
  settle_clear(engine);
  engine.input_radar_frame(T_READY + 1000, 1, 0, 1);
  engine.evaluate(T_READY + 1000);
  ASSERT_TRUE(engine.occupancy());
}

TEST_CASE(sen0609_static_presence_asserts_occupancy) {
  FusionEngine engine = tri_engine();
  settle_clear(engine);
  engine.input_static(T_READY + 100, true);
  engine.evaluate(T_READY + 100);
  ASSERT_TRUE(engine.occupancy());
}

TEST_CASE(any_sensor_combination_asserts_occupancy) {
  FusionEngine engine = tri_engine();
  settle_clear(engine);
  engine.input_pir(T_READY + 100, true);
  engine.input_static(T_READY + 100, true);
  engine.input_radar_frame(T_READY + 100, 2, 1, 1);
  engine.evaluate(T_READY + 100);
  ASSERT_TRUE(engine.occupancy());
}

TEST_CASE(occupancy_asserts_during_startup_from_valid_radar_data) {
  // Startup rule: occupancy MAY assert during warm-up when a sensor
  // produces valid data (the radar's first frame is valid data).
  FusionEngine engine = tri_engine();
  engine.input_radar_frame(2000, 1, 1, 0);
  engine.evaluate(2000);
  ASSERT_TRUE(engine.occupancy());
  // ... while the customer status still reports Initialising (PD-02).
  ASSERT_EQ(engine.status(), STATUS_INITIALISING);
}

TEST_CASE(pir_level_is_ignored_during_pir_warmup) {
  // PIR outputs are unreliable while the sensor stabilises after power-on;
  // a high level inside the PIR warm-up window must not assert occupancy.
  FusionEngine engine = tri_engine();
  engine.input_radar_frame(1000, 0, 0, 0);
  engine.input_pir(1000, true);
  engine.evaluate(1000);
  ASSERT_FALSE(engine.occupancy());
  engine.input_pir(1500, false);
  engine.evaluate(1500);
  ASSERT_FALSE(engine.occupancy());
}

// ---------------------------------------------------------------------------
// Fusion: clear behaviour (fail-safe rules)
// ---------------------------------------------------------------------------

TEST_CASE(occupancy_does_not_clear_until_all_usable_sensors_clear) {
  FusionEngine engine = tri_engine();
  settle_clear(engine);
  engine.input_static(T_READY + 100, true);
  engine.evaluate(T_READY + 100);
  ASSERT_TRUE(engine.occupancy());
  // Radar keeps reporting an empty room, but SEN0609 still asserts:
  // the clear timer must never start.
  for (uint32_t t = T_READY + 1000; t <= T_READY + 120000; t += 1000) {
    engine.input_radar_frame(t, 0, 0, 0);
    engine.evaluate(t);
    ASSERT_TRUE(engine.occupancy());
  }
}

TEST_CASE(clear_delay_is_honoured) {
  FusionEngine engine = tri_engine();
  settle_clear(engine);
  engine.input_static(T_READY + 100, true);
  engine.evaluate(T_READY + 100);
  ASSERT_TRUE(engine.occupancy());
  // Everything reports clear from t0.
  uint32_t t0 = T_READY + 1000;
  engine.input_static(t0, false);
  for (uint32_t t = t0; t < t0 + 30000; t += 1000) {
    engine.input_radar_frame(t, 0, 0, 0);
    engine.evaluate(t);
    ASSERT_TRUE(engine.occupancy());  // still held inside the delay
  }
  engine.input_radar_frame(t0 + 30500, 0, 0, 0);
  engine.evaluate(t0 + 30500);
  ASSERT_FALSE(engine.occupancy());
}

TEST_CASE(new_detection_cancels_pending_clear) {
  FusionEngine engine = tri_engine();
  settle_clear(engine);
  engine.input_pir(T_READY + 100, true);
  engine.evaluate(T_READY + 100);
  engine.input_pir(T_READY + 200, false);
  // Clear pending... then a new detection arrives mid-delay.
  uint32_t t_pending = T_READY + 25000;  // past the PIR hold window
  for (uint32_t t = T_READY + 1000; t <= t_pending; t += 1000) {
    engine.input_radar_frame(t, 0, 0, 0);
    engine.evaluate(t);
  }
  ASSERT_TRUE(engine.occupancy());
  engine.input_radar_frame(t_pending + 500, 1, 1, 0);
  engine.evaluate(t_pending + 500);
  ASSERT_TRUE(engine.occupancy());
  // The timer restarted: 29 s of clear later we are still occupied.
  uint32_t t1 = t_pending + 1000;
  for (uint32_t t = t1; t < t1 + 29000; t += 1000) {
    engine.input_radar_frame(t, 0, 0, 0);
    engine.evaluate(t);
    ASSERT_TRUE(engine.occupancy());
  }
}

TEST_CASE(stale_radar_data_is_never_interpreted_as_clear) {
  // Radar-only composition: the radar asserts presence, then its frames
  // stop. Stale data is unknown — occupancy must NOT clear after the
  // ordinary clear delay; only the documented conservative degraded
  // fallback may eventually release it.
  FusionEngine engine = radar_only_engine();
  settle_clear(engine);
  engine.input_radar_frame(T_READY + 1000, 1, 0, 1);
  engine.evaluate(T_READY + 1000);
  ASSERT_TRUE(engine.occupancy());
  // No more frames. Ordinary clear delay (30 s) passes: still occupied.
  uint32_t t_last = T_READY + 1000;
  engine.evaluate(t_last + 31000);
  ASSERT_TRUE(engine.occupancy());
  // The conservative fallback (Balanced: 60 s with no usable sensor)
  // eventually releases the latch so a dead radar cannot hold occupancy
  // forever.
  engine.evaluate(t_last + 200000);
  ASSERT_FALSE(engine.occupancy());
}

TEST_CASE(sensor_failure_does_not_turn_occupancy_off) {
  FusionEngine engine = tri_engine();
  settle_clear(engine);
  // SEN0609 holds presence; radar then dies.
  engine.input_static(T_READY + 100, true);
  engine.evaluate(T_READY + 100);
  ASSERT_TRUE(engine.occupancy());
  for (uint32_t t = T_READY + 1000; t <= T_READY + 90000; t += 1000) {
    // no radar frames at all — radar is stale/failed
    engine.evaluate(t);
    ASSERT_TRUE(engine.occupancy());
  }
}

TEST_CASE(remaining_usable_sensors_clear_normally_after_a_failure) {
  // Radar dies while occupied; PIR and SEN0609 (usable) report clear:
  // the normal clear delay applies to the usable subset.
  FusionEngine engine = tri_engine();
  settle_clear(engine);
  engine.input_static(T_READY + 100, true);
  engine.evaluate(T_READY + 100);
  uint32_t t0 = T_READY + 1000;
  engine.input_static(t0, false);  // SEN0609 clear; radar silent from here
  for (uint32_t t = t0; t < t0 + 30000; t += 1000) {
    engine.evaluate(t);
    ASSERT_TRUE(engine.occupancy());
  }
  engine.evaluate(t0 + 30500);
  ASSERT_FALSE(engine.occupancy());
}

// ---------------------------------------------------------------------------
// Customer status precedence
// ---------------------------------------------------------------------------

TEST_CASE(multiple_people_outranks_movement_and_still) {
  FusionEngine engine = tri_engine();
  settle_clear(engine);
  engine.input_pir(T_READY + 100, true);
  engine.input_radar_frame(T_READY + 100, 2, 1, 1);
  engine.evaluate(T_READY + 100);
  ASSERT_EQ(engine.status(), STATUS_MULTIPLE);
  // "Multiple targets": radar targets, not verified people (promotion to
  // "Multiple people" wording is an owner decision after bench evidence).
  ASSERT_STREQ(status_to_string(engine.status()), "Multiple targets");
}

TEST_CASE(movement_outranks_still_presence) {
  FusionEngine engine = tri_engine();
  settle_clear(engine);
  engine.input_static(T_READY + 100, true);
  engine.input_radar_frame(T_READY + 100, 1, 1, 0);
  engine.evaluate(T_READY + 100);
  ASSERT_EQ(engine.status(), STATUS_MOVEMENT);
  ASSERT_STREQ(status_to_string(engine.status()), "Movement detected");
}

TEST_CASE(still_presence_when_occupied_without_movement) {
  FusionEngine engine = tri_engine();
  settle_clear(engine);
  engine.input_static(T_READY + 100, true);
  engine.evaluate(T_READY + 100);
  ASSERT_EQ(engine.status(), STATUS_STILL);
  ASSERT_STREQ(status_to_string(engine.status()), "Still presence");
}

TEST_CASE(initialising_does_not_falsely_show_unavailable) {
  FusionEngine engine = tri_engine();
  engine.evaluate(1000);  // no data from any sensor yet — that is normal
  ASSERT_EQ(engine.status(), STATUS_INITIALISING);
  ASSERT_EQ(engine.health(), HEALTH_INITIALISING);
  ASSERT_STREQ(status_to_string(engine.status()), "Initialising");
}

TEST_CASE(clear_appears_only_after_the_clear_delay) {
  FusionEngine engine = tri_engine();
  settle_clear(engine);
  engine.input_static(T_READY + 100, true);
  engine.evaluate(T_READY + 100);
  uint32_t t0 = T_READY + 1000;
  engine.input_static(t0, false);
  // During the pending-clear window the room is still reported occupied.
  for (uint32_t t = t0; t < t0 + 30000; t += 1000) {
    engine.input_radar_frame(t, 0, 0, 0);
    engine.evaluate(t);
    ASSERT_EQ(engine.status(), STATUS_STILL);
  }
  uint32_t t_done = t0 + 31000;
  engine.input_radar_frame(t_done, 0, 0, 0);
  engine.evaluate(t_done);
  ASSERT_EQ(engine.status(), STATUS_CLEAR);
  ASSERT_STREQ(status_to_string(engine.status()), "Clear");
}

TEST_CASE(degraded_module_keeps_showing_occupancy_activity) {
  // Customer-clarity decision (documented): while occupied, Presence
  // Status keeps showing activity; Presence Module Status carries the
  // degradation.
  FusionEngine engine = tri_engine();
  settle_clear(engine);
  engine.input_pir(T_READY + 100, true);
  engine.evaluate(T_READY + 100);
  // Radar dies (no frames for > stale timeout).
  uint32_t t = T_READY + 20000;
  engine.input_pir(t, true);
  engine.evaluate(t);
  ASSERT_TRUE(engine.occupancy());
  ASSERT_EQ(engine.health(), HEALTH_DEGRADED);
  ASSERT_EQ(engine.status(), STATUS_MOVEMENT);
}

TEST_CASE(sensor_degraded_shown_when_not_occupied) {
  FusionEngine engine = tri_engine();
  settle_clear(engine);
  // Not occupied; radar goes stale.
  engine.evaluate(T_READY + 20000);
  ASSERT_FALSE(engine.occupancy());
  ASSERT_EQ(engine.health(), HEALTH_DEGRADED);
  ASSERT_EQ(engine.status(), STATUS_DEGRADED);
  ASSERT_STREQ(status_to_string(engine.status()), "Sensor degraded");
}

TEST_CASE(unavailable_when_no_usable_sensor_remains) {
  FusionEngine engine = radar_only_engine();
  settle_clear(engine);
  engine.evaluate(T_READY + 20000);  // radar stale, nothing else expected
  ASSERT_EQ(engine.health(), HEALTH_UNAVAILABLE);
  ASSERT_EQ(engine.status(), STATUS_UNAVAILABLE);
  ASSERT_STREQ(status_to_string(engine.status()), "Unavailable");
}

// ---------------------------------------------------------------------------
// Module health (PD-07)
// ---------------------------------------------------------------------------

TEST_CASE(all_verifiable_sensors_fresh_is_available) {
  FusionEngine engine = tri_engine();
  settle_clear(engine);
  ASSERT_EQ(engine.health(), HEALTH_AVAILABLE);
  ASSERT_STREQ(health_to_string(engine.health()), "Available");
}

TEST_CASE(one_stale_sensor_is_degraded) {
  FusionEngine engine = dual_verifiable_engine(true);
  settle_clear(engine);
  // Keep the static channel fresh but let the radar go stale.
  for (uint32_t t = T_READY + 1000; t <= T_READY + 20000; t += 1000) {
    engine.input_static(t, false);
    engine.evaluate(t);
  }
  ASSERT_EQ(engine.health(), HEALTH_DEGRADED);
}

TEST_CASE(two_failed_but_one_usable_is_degraded) {
  // Both verifiable channels fail; the PIR trigger channel remains
  // expected, so the module is Degraded (documented: a GPIO-only sensor
  // can never be proven dead, so it keeps the module usable as a trigger).
  FusionEngine engine = dual_verifiable_engine(true);
  settle_clear(engine);
  engine.evaluate(T_READY + 20000);  // no frames from either UART sensor
  ASSERT_EQ(engine.health(), HEALTH_DEGRADED);
}

TEST_CASE(all_unusable_is_unavailable) {
  FusionEngine engine = dual_verifiable_engine(false);
  settle_clear(engine);
  engine.evaluate(T_READY + 20000);
  ASSERT_EQ(engine.health(), HEALTH_UNAVAILABLE);
}

TEST_CASE(explicit_fault_reports_fault) {
  FusionEngine engine = tri_engine();
  settle_clear(engine);
  engine.set_module_fault(true);
  engine.evaluate(T_READY + 1000);
  ASSERT_EQ(engine.health(), HEALTH_FAULT);
  ASSERT_STREQ(health_to_string(engine.health()), "Fault");
  engine.set_module_fault(false);
  engine.input_radar_frame(T_READY + 2000, 0, 0, 0);
  engine.evaluate(T_READY + 2000);
  ASSERT_EQ(engine.health(), HEALTH_AVAILABLE);
}

TEST_CASE(absent_optional_sensor_is_not_a_fault) {
  FusionEngine engine = radar_only_engine();
  settle_clear(engine);
  ASSERT_EQ(engine.health(), HEALTH_AVAILABLE);
}

TEST_CASE(warmup_without_data_is_not_a_fault) {
  FusionEngine engine = tri_engine();
  engine.evaluate(RADAR_WARMUP - 1000);
  ASSERT_EQ(engine.health(), HEALTH_INITIALISING);
}

TEST_CASE(recovery_returns_to_available) {
  FusionEngine engine = tri_engine();
  settle_clear(engine);
  engine.evaluate(T_READY + 20000);  // radar stale
  ASSERT_EQ(engine.health(), HEALTH_DEGRADED);
  // UART recovers: frames resume.
  engine.input_radar_frame(T_READY + 21000, 0, 0, 0);
  engine.evaluate(T_READY + 21000);
  ASSERT_EQ(engine.health(), HEALTH_AVAILABLE);
}

// ---------------------------------------------------------------------------
// Modes (PD-10) and clear-delay control (PD-04)
// ---------------------------------------------------------------------------

TEST_CASE(balanced_is_the_default_mode) {
  FusionEngine engine = tri_engine();
  ASSERT_EQ(engine.mode(), MODE_BALANCED);
  ASSERT_EQ(mode_params(MODE_BALANCED).clear_delay_ms, 30000u);
}

TEST_CASE(mode_presets_change_only_documented_fusion_settings) {
  // Responsive / Stable adjust only the documented runtime fusion
  // parameters (clear delay preset, PIR movement hold, degraded fallback).
  ModeParams balanced = mode_params(MODE_BALANCED);
  ModeParams responsive = mode_params(MODE_RESPONSIVE);
  ModeParams stable = mode_params(MODE_STABLE);
  ASSERT_TRUE(responsive.clear_delay_ms < balanced.clear_delay_ms);
  ASSERT_TRUE(stable.clear_delay_ms > balanced.clear_delay_ms);
  ASSERT_TRUE(responsive.pir_hold_ms < balanced.pir_hold_ms);
  ASSERT_TRUE(stable.degraded_hold_ms > balanced.degraded_hold_ms);
}

TEST_CASE(custom_mode_preserves_user_clear_delay) {
  ModeParams custom = mode_params(MODE_CUSTOM);
  ModeParams balanced = mode_params(MODE_BALANCED);
  // Custom keeps the Balanced fusion internals; the clear delay itself is
  // owned by the user-adjustable number entity.
  ASSERT_EQ(custom.pir_hold_ms, balanced.pir_hold_ms);
  ASSERT_EQ(custom.degraded_hold_ms, balanced.degraded_hold_ms);
  FusionEngine engine = tri_engine();
  engine.set_mode(MODE_CUSTOM);
  engine.set_clear_delay_ms(45000);
  ASSERT_EQ(engine.clear_delay_ms(), 45000u);
  engine.set_mode(MODE_CUSTOM);  // reselecting Custom must not reset it
  ASSERT_EQ(engine.clear_delay_ms(), 45000u);
}

TEST_CASE(clear_delay_change_applies_at_runtime) {
  FusionEngine engine = tri_engine();
  settle_clear(engine);
  engine.set_clear_delay_ms(10000);
  engine.input_pir(T_READY + 100, true);
  engine.evaluate(T_READY + 100);
  engine.input_pir(T_READY + 200, false);
  // PIR hold (10 s Balanced) + 10 s clear delay: occupied at 15 s...
  uint32_t t0 = T_READY + 1000;
  for (uint32_t t = t0; t <= t0 + 15000; t += 1000) {
    engine.input_radar_frame(t, 0, 0, 0);
    engine.evaluate(t);
  }
  ASSERT_TRUE(engine.occupancy());
  // ... and clear once hold + delay have both expired.
  for (uint32_t t = t0 + 16000; t <= t0 + 25000; t += 1000) {
    engine.input_radar_frame(t, 0, 0, 0);
    engine.evaluate(t);
  }
  ASSERT_FALSE(engine.occupancy());
}

TEST_CASE(mode_strings_round_trip) {
  ASSERT_EQ(mode_from_string("Balanced"), MODE_BALANCED);
  ASSERT_EQ(mode_from_string("Responsive"), MODE_RESPONSIVE);
  ASSERT_EQ(mode_from_string("Stable"), MODE_STABLE);
  ASSERT_EQ(mode_from_string("Custom"), MODE_CUSTOM);
  ASSERT_EQ(mode_from_string("garbage"), MODE_BALANCED);  // safe default
}

// ---------------------------------------------------------------------------
// Radar target count output (PD-09)
// ---------------------------------------------------------------------------

TEST_CASE(radar_target_count_is_valid_only_when_fresh) {
  FusionEngine engine = tri_engine();
  settle_clear(engine);
  engine.input_radar_frame(T_READY + 1000, 2, 1, 1);
  engine.evaluate(T_READY + 1000);
  ASSERT_TRUE(engine.radar_fresh());
  ASSERT_EQ(engine.radar_target_count(), 2);
  // Frames stop: the count is no longer trustworthy.
  engine.evaluate(T_READY + 1000 + RADAR_STALE + 2000);
  ASSERT_FALSE(engine.radar_fresh());
}

TEST_CASE(global_engine_is_a_single_shared_instance) {
  // The production YAML shares one engine via this accessor (an ESPHome
  // globals: entry cannot carry a custom class type in 2026.4.5).
  FusionEngine &a = global_engine();
  FusionEngine &b = global_engine();
  ASSERT_TRUE(&a == &b);
  a.set_clear_delay_ms(45000);
  ASSERT_EQ(b.clear_delay_ms(), 45000u);
}

TEST_CASE(pir_hold_keeps_movement_after_edge) {
  FusionEngine engine = tri_engine();
  settle_clear(engine);
  engine.input_pir(T_READY + 100, true);
  engine.evaluate(T_READY + 100);
  engine.input_pir(T_READY + 300, false);
  uint32_t t_mid = T_READY + 5000;  // inside the Balanced 10 s PIR hold
  engine.input_radar_frame(t_mid, 0, 0, 0);
  engine.evaluate(t_mid);
  ASSERT_TRUE(engine.occupancy());
  ASSERT_EQ(engine.status(), STATUS_MOVEMENT);
}

// ---------------------------------------------------------------------------
// Runner
// ---------------------------------------------------------------------------

int main() {
  printf("=== PRESENCE-FRAMEWORK-001 fusion simulation tests ===\n");
  printf("(logic/simulation proof only — never hardware validation)\n\n");

  run_test(test_pir_alone_asserts_occupancy_immediately,
           "pir_alone_asserts_occupancy_immediately");
  run_test(test_radar_moving_target_asserts_occupancy,
           "radar_moving_target_asserts_occupancy");
  run_test(test_radar_still_target_asserts_occupancy,
           "radar_still_target_asserts_occupancy");
  run_test(test_sen0609_static_presence_asserts_occupancy,
           "sen0609_static_presence_asserts_occupancy");
  run_test(test_any_sensor_combination_asserts_occupancy,
           "any_sensor_combination_asserts_occupancy");
  run_test(test_occupancy_asserts_during_startup_from_valid_radar_data,
           "occupancy_asserts_during_startup_from_valid_radar_data");
  run_test(test_pir_level_is_ignored_during_pir_warmup,
           "pir_level_is_ignored_during_pir_warmup");
  run_test(test_occupancy_does_not_clear_until_all_usable_sensors_clear,
           "occupancy_does_not_clear_until_all_usable_sensors_clear");
  run_test(test_clear_delay_is_honoured, "clear_delay_is_honoured");
  run_test(test_new_detection_cancels_pending_clear,
           "new_detection_cancels_pending_clear");
  run_test(test_stale_radar_data_is_never_interpreted_as_clear,
           "stale_radar_data_is_never_interpreted_as_clear");
  run_test(test_sensor_failure_does_not_turn_occupancy_off,
           "sensor_failure_does_not_turn_occupancy_off");
  run_test(test_remaining_usable_sensors_clear_normally_after_a_failure,
           "remaining_usable_sensors_clear_normally_after_a_failure");
  run_test(test_multiple_people_outranks_movement_and_still,
           "multiple_people_outranks_movement_and_still");
  run_test(test_movement_outranks_still_presence,
           "movement_outranks_still_presence");
  run_test(test_still_presence_when_occupied_without_movement,
           "still_presence_when_occupied_without_movement");
  run_test(test_initialising_does_not_falsely_show_unavailable,
           "initialising_does_not_falsely_show_unavailable");
  run_test(test_clear_appears_only_after_the_clear_delay,
           "clear_appears_only_after_the_clear_delay");
  run_test(test_degraded_module_keeps_showing_occupancy_activity,
           "degraded_module_keeps_showing_occupancy_activity");
  run_test(test_sensor_degraded_shown_when_not_occupied,
           "sensor_degraded_shown_when_not_occupied");
  run_test(test_unavailable_when_no_usable_sensor_remains,
           "unavailable_when_no_usable_sensor_remains");
  run_test(test_all_verifiable_sensors_fresh_is_available,
           "all_verifiable_sensors_fresh_is_available");
  run_test(test_one_stale_sensor_is_degraded, "one_stale_sensor_is_degraded");
  run_test(test_two_failed_but_one_usable_is_degraded,
           "two_failed_but_one_usable_is_degraded");
  run_test(test_all_unusable_is_unavailable, "all_unusable_is_unavailable");
  run_test(test_explicit_fault_reports_fault, "explicit_fault_reports_fault");
  run_test(test_absent_optional_sensor_is_not_a_fault,
           "absent_optional_sensor_is_not_a_fault");
  run_test(test_warmup_without_data_is_not_a_fault,
           "warmup_without_data_is_not_a_fault");
  run_test(test_recovery_returns_to_available, "recovery_returns_to_available");
  run_test(test_balanced_is_the_default_mode, "balanced_is_the_default_mode");
  run_test(test_mode_presets_change_only_documented_fusion_settings,
           "mode_presets_change_only_documented_fusion_settings");
  run_test(test_custom_mode_preserves_user_clear_delay,
           "custom_mode_preserves_user_clear_delay");
  run_test(test_clear_delay_change_applies_at_runtime,
           "clear_delay_change_applies_at_runtime");
  run_test(test_mode_strings_round_trip, "mode_strings_round_trip");
  run_test(test_radar_target_count_is_valid_only_when_fresh,
           "radar_target_count_is_valid_only_when_fresh");
  run_test(test_global_engine_is_a_single_shared_instance,
           "global_engine_is_a_single_shared_instance");
  run_test(test_pir_hold_keeps_movement_after_edge,
           "pir_hold_keeps_movement_after_edge");

  printf("\n=== Results: %d/%d passed ===\n", passed_count, test_count);
  return (passed_count == test_count) ? 0 : 1;
}

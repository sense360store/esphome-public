// BLOWER-FRAMEWORK-001 — deterministic simulation tests for the canonical
// blower controller (include/sense360/blower_controller.h).
//
// This is the test-only simulation layer: it feeds synthetic, timestamped mode
// / demand inputs into the SAME header-only controller the production YAML
// compiles (no second implementation that can drift) and asserts the Off / Auto
// / On mode surface, the AirIQ demand mapping, the fail-safe on UNKNOWN demand,
// and the Auto timing state machine (minimum on, post-demand PURGE, minimum-off
// restart lockout, stale-data wind-down, and millis rollover).
//
// IMPORTANT: a green run here is LOGIC/SIMULATION proof only. It is NEVER
// hardware validation. The J13 FAN net exposes no tach / speed / current /
// airflow / rotation feedback, so nothing here asserts a physical blower state;
// all timing values are provisional engineering defaults pending the bench
// checklist (docs/hardware/blower-framework-bench-checklist.md).
//
// Compile via tests/Makefile (auto-discovered):  cd tests && make test

#include "../../include/sense360/blower_controller.h"

#include <cassert>
#include <cstdio>
#include <cstring>
#include <exception>

using namespace sense360::blower;

// Simple test framework (repo convention — see test_roomiq_engine.cpp)
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
// Fixtures — mirror packages/features/blower_framework.yaml but with short,
// distinct dwell windows so the timing state machine is exercised
// deterministically. PURGE (20 s) > MIN_ON (10 s) here so purge normally
// dominates the wind-down.
// ---------------------------------------------------------------------------

static const uint32_t T0 = 100000;
static const uint32_t MIN_ON = 10000;
static const uint32_t MIN_OFF = 10000;
static const uint32_t PURGE = 20000;

// AirIQ present, Auto mode, TRIGGER_NOW.
static BlowerController make_controller() {
  BlowerController c;
  c.set_has_airiq(true);
  c.set_mode(MODE_AUTO);
  c.set_trigger(TRIGGER_NOW);
  c.set_min_on_ms(MIN_ON);
  c.set_min_off_ms(MIN_OFF);
  c.set_purge_ms(PURGE);
  c.begin(T0);
  return c;
}

// Variant with a SHORT purge (< MIN_ON) so the minimum-on requirement dominates
// the wind-down — used to prove min-on completion outlasts a finished purge.
static BlowerController make_controller_short_purge(uint32_t start) {
  BlowerController c;
  c.set_has_airiq(true);
  c.set_mode(MODE_AUTO);
  c.set_trigger(TRIGGER_NOW);
  c.set_min_on_ms(MIN_ON);
  c.set_min_off_ms(MIN_OFF);
  c.set_purge_ms(2000);
  c.begin(start);
  return c;
}

static void drive(BlowerController &c, uint32_t t, Demand demand) {
  c.input_demand(t, demand);
  c.evaluate(t);
}

// ---------------------------------------------------------------------------
// Demand mapping (pinned against the AirIQ enum in test_blower_airiq_coexist).
// ---------------------------------------------------------------------------

TEST_CASE(demand_mapping_matches_airiq_recommendation) {
  ASSERT_EQ(demand_from_airiq_recommendation(0), DEMAND_UNKNOWN);   // INITIALISING
  ASSERT_EQ(demand_from_airiq_recommendation(1), DEMAND_NONE);      // NO_ACTION
  ASSERT_EQ(demand_from_airiq_recommendation(2), DEMAND_ELEVATED);  // VENTILATE_SOON
  ASSERT_EQ(demand_from_airiq_recommendation(3), DEMAND_HIGH);      // VENTILATE_NOW
  ASSERT_EQ(demand_from_airiq_recommendation(4), DEMAND_NONE);      // CHECK_SOURCE
  ASSERT_EQ(demand_from_airiq_recommendation(5), DEMAND_UNKNOWN);   // UNAVAILABLE
  ASSERT_EQ(demand_from_airiq_recommendation(99), DEMAND_UNKNOWN);
}

// ---------------------------------------------------------------------------
// Mode surface: Off / Auto / On, default Auto
// ---------------------------------------------------------------------------

TEST_CASE(default_mode_is_auto) {
  BlowerController c;
  ASSERT_EQ(c.mode(), MODE_AUTO);
}

TEST_CASE(off_mode_always_commands_off) {
  BlowerController c = make_controller();
  c.set_mode(MODE_OFF);
  drive(c, T0 + 1000, DEMAND_HIGH);  // even a HIGH demand cannot start it
  ASSERT_FALSE(c.output_on());
  ASSERT_EQ(c.state(), STATE_OFF);
}

TEST_CASE(on_mode_always_commands_on) {
  BlowerController c = make_controller();
  c.set_mode(MODE_ON);
  drive(c, T0 + 1000, DEMAND_NONE);  // even No-demand keeps it on
  ASSERT_TRUE(c.output_on());
  ASSERT_EQ(c.state(), STATE_ON);
}

TEST_CASE(auto_without_airiq_stays_off) {
  BlowerController c = make_controller();
  c.set_has_airiq(false);
  drive(c, T0 + 1000, DEMAND_HIGH);
  ASSERT_FALSE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_NO_AIRIQ);
}

TEST_CASE(auto_unknown_demand_never_starts) {
  BlowerController c = make_controller();
  drive(c, T0 + 1000, DEMAND_UNKNOWN);
  ASSERT_FALSE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_OFF_UNKNOWN);
}

TEST_CASE(auto_no_demand_off) {
  BlowerController c = make_controller();
  drive(c, T0 + 1000, DEMAND_NONE);
  ASSERT_FALSE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_OFF_OK);
}

TEST_CASE(trigger_now_starts_only_on_ventilate_now) {
  BlowerController c = make_controller();
  drive(c, T0 + 1000, DEMAND_ELEVATED);
  ASSERT_FALSE(c.output_on());
  drive(c, T0 + 2000, DEMAND_HIGH);
  ASSERT_TRUE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_VENTILATING);
}

TEST_CASE(trigger_soon_starts_on_ventilate_soon) {
  BlowerController c = make_controller();
  c.set_trigger(TRIGGER_SOON);
  drive(c, T0 + 1000, DEMAND_ELEVATED);
  ASSERT_TRUE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_VENTILATING);
}

TEST_CASE(first_auto_start_not_delayed_by_min_off) {
  BlowerController c = make_controller();
  drive(c, T0, DEMAND_HIGH);  // no prior run -> immediate start
  ASSERT_TRUE(c.output_on());
}

// ---------------------------------------------------------------------------
// Post-demand purge
// ---------------------------------------------------------------------------

TEST_CASE(purge_begins_after_demand_clears) {
  BlowerController c = make_controller();
  drive(c, T0, DEMAND_HIGH);
  ASSERT_TRUE(c.output_on());
  // Demand clears after min-on has elapsed: enter purge, keep running.
  drive(c, T0 + 12000, DEMAND_NONE);
  ASSERT_TRUE(c.output_on());
  ASSERT_TRUE(c.purging());
  ASSERT_EQ(c.state(), STATE_AUTO_PURGE);
}

TEST_CASE(purge_runs_for_the_configured_duration_then_stops) {
  BlowerController c = make_controller();
  drive(c, T0, DEMAND_HIGH);
  const uint32_t clear = T0 + 12000;  // min-on (10s) already satisfied
  drive(c, clear, DEMAND_NONE);
  // Still purging just before the purge window elapses.
  drive(c, clear + PURGE - 1, DEMAND_NONE);
  ASSERT_TRUE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_PURGE);
  // Stops once the purge window elapses (min-on already done).
  drive(c, clear + PURGE + 1, DEMAND_NONE);
  ASSERT_FALSE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_OFF_OK);
}

TEST_CASE(demand_clears_before_min_on_completes_holds_on_through_min_on) {
  // Short purge (< min-on) so completing min-on outlasts a finished purge.
  BlowerController c = make_controller_short_purge(T0);
  drive(c, T0, DEMAND_HIGH);
  drive(c, T0 + 3000, DEMAND_NONE);  // clears before min-on (10s)
  // Purge (2s) elapses but min-on has NOT — the blower must stay on.
  drive(c, T0 + 3000 + 2000 + 1, DEMAND_NONE);
  ASSERT_TRUE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_PURGE);
  // Once min-on completes, it stops.
  drive(c, T0 + MIN_ON + 1, DEMAND_NONE);
  ASSERT_FALSE(c.output_on());
}

TEST_CASE(demand_returns_during_purge_resumes_ventilating) {
  BlowerController c = make_controller();
  drive(c, T0, DEMAND_HIGH);
  drive(c, T0 + 12000, DEMAND_NONE);  // purge
  ASSERT_TRUE(c.purging());
  drive(c, T0 + 13000, DEMAND_HIGH);  // demand returns
  ASSERT_TRUE(c.output_on());
  ASSERT_FALSE(c.purging());
  ASSERT_EQ(c.state(), STATE_AUTO_VENTILATING);
}

TEST_CASE(stale_demand_while_running_winds_down_and_stops) {
  BlowerController c = make_controller();
  drive(c, T0, DEMAND_HIGH);
  // Demand goes UNKNOWN (stale/unavailable) while running: purge, do not run
  // forever, complete min-on + purge, then stop.
  drive(c, T0 + 12000, DEMAND_UNKNOWN);
  ASSERT_TRUE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_PURGE);
  drive(c, T0 + 12000 + PURGE + 1, DEMAND_UNKNOWN);
  ASSERT_FALSE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_OFF_UNKNOWN);
  // And it stays off far into the future on stale data (never forever).
  drive(c, T0 + 500000, DEMAND_UNKNOWN);
  ASSERT_FALSE(c.output_on());
}

TEST_CASE(off_during_purge_stops_immediately) {
  BlowerController c = make_controller();
  drive(c, T0, DEMAND_HIGH);
  drive(c, T0 + 12000, DEMAND_NONE);  // purge
  ASSERT_TRUE(c.output_on());
  c.set_mode(MODE_OFF);
  c.evaluate(T0 + 13000);
  ASSERT_FALSE(c.output_on());
  ASSERT_EQ(c.state(), STATE_OFF);
}

TEST_CASE(on_during_purge_keeps_running) {
  BlowerController c = make_controller();
  drive(c, T0, DEMAND_HIGH);
  drive(c, T0 + 12000, DEMAND_NONE);  // purge
  c.set_mode(MODE_ON);
  c.evaluate(T0 + 13000);
  ASSERT_TRUE(c.output_on());
  ASSERT_EQ(c.state(), STATE_ON);
}

TEST_CASE(restart_inhibited_by_min_off_after_purge) {
  BlowerController c = make_controller();
  drive(c, T0, DEMAND_HIGH);
  drive(c, T0 + 12000, DEMAND_NONE);
  const uint32_t stop = T0 + 12000 + PURGE + 1;
  drive(c, stop, DEMAND_NONE);
  ASSERT_FALSE(c.output_on());
  // Demand returns before min-off elapses -> restart held off.
  drive(c, stop + MIN_OFF - 1, DEMAND_HIGH);
  ASSERT_FALSE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_MIN_OFF);
  // After min-off, it may restart.
  drive(c, stop + MIN_OFF + 1, DEMAND_HIGH);
  ASSERT_TRUE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_VENTILATING);
}

TEST_CASE(on_mode_then_auto_winds_down_via_purge) {
  BlowerController c = make_controller();
  c.set_mode(MODE_ON);
  c.evaluate(T0);  // forced on
  ASSERT_TRUE(c.output_on());
  // Switch to Auto with no demand: the running blower winds down via purge
  // (it has "run", so it does not just snap off).
  c.set_mode(MODE_AUTO);
  drive(c, T0 + 1000, DEMAND_NONE);
  ASSERT_TRUE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_PURGE);
  drive(c, T0 + 1000 + PURGE + 1, DEMAND_NONE);
  ASSERT_FALSE(c.output_on());
}

TEST_CASE(millis_rollover_timing_is_correct) {
  // Start near the uint32 wrap so elapsed() crosses the boundary.
  const uint32_t start = 0xFFFFFF00u;  // 256 ms before wrap
  BlowerController c = make_controller_short_purge(start);
  drive(c, start, DEMAND_HIGH);
  ASSERT_TRUE(c.output_on());
  const uint32_t wrapped = 0x00000100u;  // elapsed since start = 512 ms
  drive(c, wrapped, DEMAND_NONE);        // purge begins (min-on not yet done)
  ASSERT_TRUE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_PURGE);
  // min-on (10 s) elapses across the wrap -> stops.
  const uint32_t later = wrapped + 12000u;
  drive(c, later, DEMAND_NONE);
  ASSERT_FALSE(c.output_on());
}

// ---------------------------------------------------------------------------
// Vocabulary
// ---------------------------------------------------------------------------

TEST_CASE(string_helpers_are_customer_wording) {
  ASSERT_STREQ(mode_to_string(MODE_OFF), "Off");
  ASSERT_STREQ(mode_to_string(MODE_AUTO), "Auto");
  ASSERT_STREQ(mode_to_string(MODE_ON), "On");
  ASSERT_EQ(mode_from_string("Off"), MODE_OFF);
  ASSERT_EQ(mode_from_string("On"), MODE_ON);
  ASSERT_EQ(mode_from_string("Auto"), MODE_AUTO);
  ASSERT_EQ(mode_from_string(nullptr), MODE_AUTO);  // default

  ASSERT_STREQ(trigger_to_string(TRIGGER_NOW), "Ventilate now");
  ASSERT_STREQ(trigger_to_string(TRIGGER_SOON), "Ventilate soon");
  ASSERT_EQ(trigger_from_string("Ventilate soon"), TRIGGER_SOON);

  ASSERT_STREQ(demand_to_string(DEMAND_UNKNOWN), "Unknown");
  ASSERT_STREQ(demand_to_string(DEMAND_HIGH), "Ventilate now");
}

int main() {
  printf("\n=== BLOWER-FRAMEWORK-001 blower controller simulation tests ===\n\n");

  run_test(test_demand_mapping_matches_airiq_recommendation,
           "demand_mapping_matches_airiq_recommendation");
  run_test(test_default_mode_is_auto, "default_mode_is_auto");
  run_test(test_off_mode_always_commands_off, "off_mode_always_commands_off");
  run_test(test_on_mode_always_commands_on, "on_mode_always_commands_on");
  run_test(test_auto_without_airiq_stays_off, "auto_without_airiq_stays_off");
  run_test(test_auto_unknown_demand_never_starts,
           "auto_unknown_demand_never_starts");
  run_test(test_auto_no_demand_off, "auto_no_demand_off");
  run_test(test_trigger_now_starts_only_on_ventilate_now,
           "trigger_now_starts_only_on_ventilate_now");
  run_test(test_trigger_soon_starts_on_ventilate_soon,
           "trigger_soon_starts_on_ventilate_soon");
  run_test(test_first_auto_start_not_delayed_by_min_off,
           "first_auto_start_not_delayed_by_min_off");
  run_test(test_purge_begins_after_demand_clears,
           "purge_begins_after_demand_clears");
  run_test(test_purge_runs_for_the_configured_duration_then_stops,
           "purge_runs_for_the_configured_duration_then_stops");
  run_test(test_demand_clears_before_min_on_completes_holds_on_through_min_on,
           "demand_clears_before_min_on_completes_holds_on_through_min_on");
  run_test(test_demand_returns_during_purge_resumes_ventilating,
           "demand_returns_during_purge_resumes_ventilating");
  run_test(test_stale_demand_while_running_winds_down_and_stops,
           "stale_demand_while_running_winds_down_and_stops");
  run_test(test_off_during_purge_stops_immediately,
           "off_during_purge_stops_immediately");
  run_test(test_on_during_purge_keeps_running, "on_during_purge_keeps_running");
  run_test(test_restart_inhibited_by_min_off_after_purge,
           "restart_inhibited_by_min_off_after_purge");
  run_test(test_on_mode_then_auto_winds_down_via_purge,
           "on_mode_then_auto_winds_down_via_purge");
  run_test(test_millis_rollover_timing_is_correct,
           "millis_rollover_timing_is_correct");
  run_test(test_string_helpers_are_customer_wording,
           "string_helpers_are_customer_wording");

  printf("\n=============================================\n");
  printf("Results: %d/%d tests passed\n", passed_count, test_count);
  if (passed_count == test_count) {
    printf("All blower controller simulation tests passed.\n");
    return 0;
  }
  printf("SOME TESTS FAILED\n");
  return 1;
}

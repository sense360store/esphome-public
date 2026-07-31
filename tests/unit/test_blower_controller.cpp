// BLOWER-FRAMEWORK-001 — deterministic simulation tests for the canonical
// circulation-fan controller (components/sense360/blower_controller.h).
//
// This is the test-only simulation layer: it feeds synthetic, timestamped mode
// / demand inputs into the SAME header-only controller the production YAML
// compiles (no second implementation that can drift) and asserts the Off /
// Auto / On mode surface, the AirIQ demand mapping, the duty-cycle circulation
// behaviour (run / rest windows), the air-quality boost (including the
// fail-safe: UNKNOWN demand never boosts), the boost wind-down, mode-change
// reseeding, and millis rollover.
//
// IMPORTANT: a green run here is LOGIC/SIMULATION proof only. It is NEVER
// hardware validation. The J13 FAN net exposes no tach / speed / current /
// airflow / rotation feedback, so nothing here asserts a physical fan state;
// all timing values are provisional engineering defaults pending the bench
// checklist (docs/hardware/blower-framework-bench-checklist.md).
//
// Compile via tests/Makefile (auto-discovered):  cd tests && make test

#include "../../components/sense360/blower_controller.h"

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
// distinct duty-cycle windows so the cycle is exercised deterministically.
// ---------------------------------------------------------------------------

static const uint32_t T0 = 100000;
static const uint32_t CIRC_ON = 10000;   // run window
static const uint32_t CIRC_OFF = 30000;  // rest window

// AirIQ present, Auto mode, TRIGGER_NOW (the production defaults, short
// windows).
static BlowerController make_controller(uint32_t start = T0) {
  BlowerController c;
  c.set_has_airiq(true);
  c.set_mode(MODE_AUTO);
  c.set_trigger(TRIGGER_NOW);
  c.set_circulate_on_ms(CIRC_ON);
  c.set_circulate_off_ms(CIRC_OFF);
  c.begin(start);
  return c;
}

static void drive(BlowerController &c, uint32_t t, Demand demand) {
  c.input_demand(t, demand);
  c.evaluate(t);
}

// ---------------------------------------------------------------------------
// Vocabulary / mapping
// ---------------------------------------------------------------------------

TEST_CASE(default_mode_is_auto) {
  BlowerController c;
  ASSERT_EQ(c.mode(), MODE_AUTO);
}

TEST_CASE(mode_strings_round_trip) {
  ASSERT_STREQ(mode_to_string(MODE_OFF), "Off");
  ASSERT_STREQ(mode_to_string(MODE_AUTO), "Auto");
  ASSERT_STREQ(mode_to_string(MODE_ON), "On");
  ASSERT_EQ(mode_from_string("Off"), MODE_OFF);
  ASSERT_EQ(mode_from_string("Auto"), MODE_AUTO);
  ASSERT_EQ(mode_from_string("On"), MODE_ON);
  // Unknown / null selections resolve to the default Auto.
  ASSERT_EQ(mode_from_string("garbage"), MODE_AUTO);
  ASSERT_EQ(mode_from_string(nullptr), MODE_AUTO);
}

TEST_CASE(trigger_strings_round_trip) {
  ASSERT_STREQ(trigger_to_string(TRIGGER_NOW), "Ventilate now");
  ASSERT_STREQ(trigger_to_string(TRIGGER_SOON), "Ventilate soon");
  ASSERT_EQ(trigger_from_string("Ventilate soon"), TRIGGER_SOON);
  ASSERT_EQ(trigger_from_string("Ventilate now"), TRIGGER_NOW);
  ASSERT_EQ(trigger_from_string(nullptr), TRIGGER_NOW);
}

TEST_CASE(demand_mapping_matches_airiq_recommendation) {
  // The single interpretation of the AirIQ demand contract (values pinned by
  // tests/unit/test_blower_airiq_coexist.cpp against the real AirIQ enum).
  ASSERT_EQ(demand_from_airiq_recommendation(0), DEMAND_UNKNOWN);   // INITIALISING
  ASSERT_EQ(demand_from_airiq_recommendation(1), DEMAND_NONE);      // NO_ACTION
  ASSERT_EQ(demand_from_airiq_recommendation(2), DEMAND_ELEVATED);  // VENTILATE_SOON
  ASSERT_EQ(demand_from_airiq_recommendation(3), DEMAND_HIGH);      // VENTILATE_NOW
  ASSERT_EQ(demand_from_airiq_recommendation(4), DEMAND_NONE);      // CHECK_SOURCE
  ASSERT_EQ(demand_from_airiq_recommendation(5), DEMAND_UNKNOWN);   // UNAVAILABLE
  ASSERT_EQ(demand_from_airiq_recommendation(99), DEMAND_UNKNOWN);  // out of range
}

// ---------------------------------------------------------------------------
// Forced modes
// ---------------------------------------------------------------------------

TEST_CASE(off_mode_forces_output_off) {
  BlowerController c = make_controller();
  c.set_mode(MODE_OFF);
  drive(c, T0, DEMAND_HIGH);  // even a high demand never overrides Off
  ASSERT_FALSE(c.output_on());
  ASSERT_EQ(c.state(), STATE_OFF);
}

TEST_CASE(on_mode_forces_output_on) {
  BlowerController c = make_controller();
  c.set_mode(MODE_ON);
  drive(c, T0, DEMAND_UNKNOWN);
  ASSERT_TRUE(c.output_on());
  ASSERT_EQ(c.state(), STATE_ON);
  ASSERT_FALSE(c.boosting());
}

// ---------------------------------------------------------------------------
// Auto duty cycle (circulation)
// ---------------------------------------------------------------------------

TEST_CASE(auto_entry_starts_a_run_immediately) {
  BlowerController c = make_controller();
  drive(c, T0, DEMAND_UNKNOWN);
  // Circulation is enclosure sampling, independent of AirIQ data: the first
  // evaluation of an Auto session starts a run even with UNKNOWN demand.
  ASSERT_TRUE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_CIRCULATING);
  ASSERT_FALSE(c.boosting());
}

TEST_CASE(run_ends_after_on_window_then_rests) {
  BlowerController c = make_controller();
  drive(c, T0, DEMAND_NONE);
  ASSERT_TRUE(c.output_on());
  // Still inside the run window.
  drive(c, T0 + CIRC_ON - 1, DEMAND_NONE);
  ASSERT_TRUE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_CIRCULATING);
  // Run window elapsed: rest.
  drive(c, T0 + CIRC_ON, DEMAND_NONE);
  ASSERT_FALSE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_RESTING);
}

TEST_CASE(cycle_repeats_run_rest_run) {
  BlowerController c = make_controller();
  drive(c, T0, DEMAND_NONE);            // run 1 starts
  drive(c, T0 + CIRC_ON, DEMAND_NONE);  // rest starts
  ASSERT_FALSE(c.output_on());
  // Still resting just before the rest window elapses.
  drive(c, T0 + CIRC_ON + CIRC_OFF - 1, DEMAND_NONE);
  ASSERT_FALSE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_RESTING);
  // Rest window elapsed: run 2 starts.
  drive(c, T0 + CIRC_ON + CIRC_OFF, DEMAND_NONE);
  ASSERT_TRUE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_CIRCULATING);
  // And run 2 ends after its own on window.
  drive(c, T0 + CIRC_ON + CIRC_OFF + CIRC_ON, DEMAND_NONE);
  ASSERT_FALSE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_RESTING);
}

TEST_CASE(duty_cycle_runs_without_airiq) {
  // The base cycle is deliberately independent of AirIQ composition.
  BlowerController c = make_controller();
  c.set_has_airiq(false);
  drive(c, T0, DEMAND_UNKNOWN);
  ASSERT_TRUE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_CIRCULATING);
  drive(c, T0 + CIRC_ON, DEMAND_UNKNOWN);
  ASSERT_FALSE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_RESTING);
}

// ---------------------------------------------------------------------------
// Air-quality boost
// ---------------------------------------------------------------------------

TEST_CASE(high_demand_boosts_to_continuous) {
  BlowerController c = make_controller();
  drive(c, T0, DEMAND_HIGH);
  ASSERT_TRUE(c.output_on());
  ASSERT_TRUE(c.boosting());
  ASSERT_EQ(c.state(), STATE_AUTO_BOOST);
  // Far beyond the on window the fan is STILL running: boost overrides the
  // duty cycle.
  drive(c, T0 + CIRC_ON * 5, DEMAND_HIGH);
  ASSERT_TRUE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_BOOST);
}

TEST_CASE(boost_starts_from_the_rest_phase_too) {
  BlowerController c = make_controller();
  drive(c, T0, DEMAND_NONE);
  drive(c, T0 + CIRC_ON, DEMAND_NONE);  // resting
  ASSERT_FALSE(c.output_on());
  drive(c, T0 + CIRC_ON + 1000, DEMAND_HIGH);
  ASSERT_TRUE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_BOOST);
}

TEST_CASE(elevated_demand_boosts_only_with_soon_trigger) {
  // TRIGGER_NOW (default): "Ventilate soon" does NOT boost.
  BlowerController c = make_controller();
  drive(c, T0, DEMAND_ELEVATED);
  ASSERT_FALSE(c.boosting());
  ASSERT_EQ(c.state(), STATE_AUTO_CIRCULATING);  // just the normal cycle run

  // TRIGGER_SOON: it does.
  BlowerController d = make_controller();
  d.set_trigger(TRIGGER_SOON);
  drive(d, T0, DEMAND_ELEVATED);
  ASSERT_TRUE(d.boosting());
  ASSERT_EQ(d.state(), STATE_AUTO_BOOST);
}

TEST_CASE(unknown_demand_never_boosts) {
  // FAIL-SAFE: missing / initialising / unavailable AirIQ data never changes
  // the fan's behaviour — the cycle runs as normal, no boost.
  BlowerController c = make_controller();
  drive(c, T0, DEMAND_UNKNOWN);
  ASSERT_FALSE(c.boosting());
  drive(c, T0 + CIRC_ON, DEMAND_UNKNOWN);  // cycle proceeds to rest as normal
  ASSERT_FALSE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_RESTING);
  // Still no boost while resting on UNKNOWN.
  drive(c, T0 + CIRC_ON + 1000, DEMAND_UNKNOWN);
  ASSERT_FALSE(c.output_on());
  ASSERT_FALSE(c.boosting());
}

TEST_CASE(no_airiq_means_no_boost_even_on_high_demand) {
  // Without the AirIQ contract composed a demand value can only be noise:
  // it must never boost.
  BlowerController c = make_controller();
  c.set_has_airiq(false);
  drive(c, T0, DEMAND_HIGH);
  ASSERT_FALSE(c.boosting());
  ASSERT_EQ(c.state(), STATE_AUTO_CIRCULATING);
}

TEST_CASE(boost_end_resumes_cycle_with_a_full_rest) {
  BlowerController c = make_controller();
  drive(c, T0, DEMAND_HIGH);
  ASSERT_EQ(c.state(), STATE_AUTO_BOOST);
  // Demand clears: the fan has been running, so the cycle resumes with a
  // full rest period.
  const uint32_t t_clear = T0 + 5000;
  drive(c, t_clear, DEMAND_NONE);
  ASSERT_FALSE(c.output_on());
  ASSERT_FALSE(c.boosting());
  ASSERT_EQ(c.state(), STATE_AUTO_RESTING);
  // The rest is a FULL off window measured from the boost end.
  drive(c, t_clear + CIRC_OFF - 1, DEMAND_NONE);
  ASSERT_FALSE(c.output_on());
  drive(c, t_clear + CIRC_OFF, DEMAND_NONE);
  ASSERT_TRUE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_CIRCULATING);
}

TEST_CASE(boost_end_on_stale_data_also_rests) {
  // Data going stale/unavailable mid-boost ends the boost exactly like a
  // cleared demand: rest, then resume the cycle. It never runs forever on
  // stale data.
  BlowerController c = make_controller();
  drive(c, T0, DEMAND_HIGH);
  ASSERT_EQ(c.state(), STATE_AUTO_BOOST);
  drive(c, T0 + 3000, DEMAND_UNKNOWN);
  ASSERT_FALSE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_RESTING);
}

// ---------------------------------------------------------------------------
// Mode transitions
// ---------------------------------------------------------------------------

TEST_CASE(off_interrupts_a_run_and_auto_reentry_reseeds) {
  BlowerController c = make_controller();
  drive(c, T0, DEMAND_NONE);
  ASSERT_TRUE(c.output_on());
  // Customer selects Off mid-run: output drops immediately.
  c.set_mode(MODE_OFF);
  drive(c, T0 + 1000, DEMAND_NONE);
  ASSERT_FALSE(c.output_on());
  ASSERT_EQ(c.state(), STATE_OFF);
  // Back to Auto: a fresh circulation run starts immediately.
  c.set_mode(MODE_AUTO);
  drive(c, T0 + 2000, DEMAND_NONE);
  ASSERT_TRUE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_CIRCULATING);
  // And that fresh run gets its own full on window.
  drive(c, T0 + 2000 + CIRC_ON - 1, DEMAND_NONE);
  ASSERT_TRUE(c.output_on());
  drive(c, T0 + 2000 + CIRC_ON, DEMAND_NONE);
  ASSERT_FALSE(c.output_on());
}

TEST_CASE(on_mode_then_auto_reseeds_a_run) {
  BlowerController c = make_controller();
  c.set_mode(MODE_ON);
  drive(c, T0, DEMAND_NONE);
  ASSERT_TRUE(c.output_on());
  c.set_mode(MODE_AUTO);
  drive(c, T0 + 1000, DEMAND_NONE);
  // Auto entry seeds a run phase (the fan simply stays on into it).
  ASSERT_TRUE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_CIRCULATING);
  drive(c, T0 + 1000 + CIRC_ON, DEMAND_NONE);
  ASSERT_FALSE(c.output_on());
}

TEST_CASE(boot_default_is_auto_and_output_starts_off) {
  // Mirrors the boot contract: the GPIO boots OFF; the first evaluate after
  // begin() applies the restored (default Auto) mode.
  BlowerController c;
  c.set_circulate_on_ms(CIRC_ON);
  c.set_circulate_off_ms(CIRC_OFF);
  ASSERT_EQ(c.mode(), MODE_AUTO);
  ASSERT_FALSE(c.output_on());  // nothing commanded before evaluate()
  c.begin(T0);
  ASSERT_FALSE(c.output_on());
  c.evaluate(T0);
  ASSERT_TRUE(c.output_on());  // Auto's first circulation run
}

// ---------------------------------------------------------------------------
// Rollover
// ---------------------------------------------------------------------------

TEST_CASE(cycle_survives_millis_rollover) {
  // Start a run 5 s before the uint32 clock wraps; the on window completes
  // 5 s after the wrap.
  const uint32_t t_start = 0xFFFFFFFFu - 5000u + 1u;  // 5000 ms before wrap
  BlowerController c = make_controller(t_start);
  drive(c, t_start, DEMAND_NONE);
  ASSERT_TRUE(c.output_on());
  // 1 ms before the on window elapses (post-wrap timestamp).
  drive(c, t_start + CIRC_ON - 1, DEMAND_NONE);  // wraps
  ASSERT_TRUE(c.output_on());
  drive(c, t_start + CIRC_ON, DEMAND_NONE);  // wraps
  ASSERT_FALSE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_RESTING);
}

// ---------------------------------------------------------------------------
// Status strings (single-sourced diagnostics vocabulary)
// ---------------------------------------------------------------------------

TEST_CASE(status_strings_are_honest) {
  ASSERT_STREQ(state_to_string(STATE_OFF), "Off — fan commanded off");
  ASSERT_STREQ(state_to_string(STATE_ON), "On — fan commanded on");
  ASSERT_STREQ(state_to_string(STATE_AUTO_CIRCULATING),
               "Auto: circulating — fan running");
  ASSERT_STREQ(state_to_string(STATE_AUTO_RESTING),
               "Auto: resting between circulation runs — fan off");
  ASSERT_STREQ(state_to_string(STATE_AUTO_BOOST),
               "Auto: boosted — air-quality demand active");
  ASSERT_STREQ(demand_to_string(DEMAND_UNKNOWN), "Unknown");
  ASSERT_STREQ(demand_to_string(DEMAND_NONE), "None");
  ASSERT_STREQ(demand_to_string(DEMAND_ELEVATED), "Ventilate soon");
  ASSERT_STREQ(demand_to_string(DEMAND_HIGH), "Ventilate now");
}

int main() {
  printf("\n=== BLOWER-FRAMEWORK-001 circulation-fan controller tests ===\n");

  run_test(test_default_mode_is_auto, "default_mode_is_auto");
  run_test(test_mode_strings_round_trip, "mode_strings_round_trip");
  run_test(test_trigger_strings_round_trip, "trigger_strings_round_trip");
  run_test(test_demand_mapping_matches_airiq_recommendation,
           "demand_mapping_matches_airiq_recommendation");
  run_test(test_off_mode_forces_output_off, "off_mode_forces_output_off");
  run_test(test_on_mode_forces_output_on, "on_mode_forces_output_on");
  run_test(test_auto_entry_starts_a_run_immediately,
           "auto_entry_starts_a_run_immediately");
  run_test(test_run_ends_after_on_window_then_rests,
           "run_ends_after_on_window_then_rests");
  run_test(test_cycle_repeats_run_rest_run, "cycle_repeats_run_rest_run");
  run_test(test_duty_cycle_runs_without_airiq, "duty_cycle_runs_without_airiq");
  run_test(test_high_demand_boosts_to_continuous,
           "high_demand_boosts_to_continuous");
  run_test(test_boost_starts_from_the_rest_phase_too,
           "boost_starts_from_the_rest_phase_too");
  run_test(test_elevated_demand_boosts_only_with_soon_trigger,
           "elevated_demand_boosts_only_with_soon_trigger");
  run_test(test_unknown_demand_never_boosts, "unknown_demand_never_boosts");
  run_test(test_no_airiq_means_no_boost_even_on_high_demand,
           "no_airiq_means_no_boost_even_on_high_demand");
  run_test(test_boost_end_resumes_cycle_with_a_full_rest,
           "boost_end_resumes_cycle_with_a_full_rest");
  run_test(test_boost_end_on_stale_data_also_rests,
           "boost_end_on_stale_data_also_rests");
  run_test(test_off_interrupts_a_run_and_auto_reentry_reseeds,
           "off_interrupts_a_run_and_auto_reentry_reseeds");
  run_test(test_on_mode_then_auto_reseeds_a_run,
           "on_mode_then_auto_reseeds_a_run");
  run_test(test_boot_default_is_auto_and_output_starts_off,
           "boot_default_is_auto_and_output_starts_off");
  run_test(test_cycle_survives_millis_rollover,
           "cycle_survives_millis_rollover");
  run_test(test_status_strings_are_honest, "status_strings_are_honest");

  printf("\n=============================================\n");
  printf("Results: %d/%d tests passed\n", passed_count, test_count);
  if (passed_count == test_count) {
    printf("All circulation-fan controller simulation tests passed.\n");
    return 0;
  }
  printf("SOME TESTS FAILED\n");
  return 1;
}

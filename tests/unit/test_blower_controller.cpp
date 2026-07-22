// BLOWER-FRAMEWORK-001 — deterministic simulation tests for the canonical
// blower controller (include/sense360/blower_controller.h).
//
// This is the test-only simulation layer: it feeds synthetic, timestamped mode
// / demand inputs into the SAME header-only controller the production YAML
// compiles (no second implementation that can drift) and asserts deterministic
// mode arbitration, the AirIQ demand mapping, the fail-safe on UNKNOWN demand,
// the Auto->Manual honest downgrade when AirIQ is absent, and the
// anti-short-cycle min-on / min-off dwell windows.
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
// Fixture helpers — mirror packages/features/blower_framework.yaml provisional
// defaults but with short dwell windows so the anti-short-cycle behaviour is
// exercised deterministically.
// ---------------------------------------------------------------------------

static const uint32_t T0 = 100000;
static const uint32_t MIN_ON = 10000;
static const uint32_t MIN_OFF = 10000;

// AirIQ present, Auto mode, TRIGGER_NOW by default.
static BlowerController make_controller() {
  BlowerController c;
  c.set_has_airiq(true);
  c.set_mode(MODE_AUTO);
  c.set_trigger(TRIGGER_NOW);
  c.set_min_on_ms(MIN_ON);
  c.set_min_off_ms(MIN_OFF);
  c.begin(T0);
  return c;
}

// Feed a demand and evaluate at t.
static void drive(BlowerController &c, uint32_t t, Demand demand) {
  c.input_demand(t, demand);
  c.evaluate(t);
}

// ---------------------------------------------------------------------------
// Demand mapping — the single interpretation of the AirIQ recommendation
// contract (pinned against the AirIQ enum values in
// test_blower_airiq_coexist.cpp).
// ---------------------------------------------------------------------------

TEST_CASE(demand_mapping_matches_airiq_recommendation) {
  ASSERT_EQ(demand_from_airiq_recommendation(0), DEMAND_UNKNOWN);   // INITIALISING
  ASSERT_EQ(demand_from_airiq_recommendation(1), DEMAND_NONE);      // NO_ACTION
  ASSERT_EQ(demand_from_airiq_recommendation(2), DEMAND_ELEVATED);  // VENTILATE_SOON
  ASSERT_EQ(demand_from_airiq_recommendation(3), DEMAND_HIGH);      // VENTILATE_NOW
  ASSERT_EQ(demand_from_airiq_recommendation(4), DEMAND_NONE);      // CHECK_SOURCE
  ASSERT_EQ(demand_from_airiq_recommendation(5), DEMAND_UNKNOWN);   // UNAVAILABLE
  // An out-of-range value is treated conservatively as UNKNOWN.
  ASSERT_EQ(demand_from_airiq_recommendation(99), DEMAND_UNKNOWN);
}

// ---------------------------------------------------------------------------
// Mode arbitration
// ---------------------------------------------------------------------------

TEST_CASE(manual_mode_never_owns_the_output) {
  BlowerController c = make_controller();
  c.set_mode(MODE_MANUAL);
  drive(c, T0 + 1000, DEMAND_HIGH);  // even a HIGH demand does not drive Manual
  ASSERT_FALSE(c.auto_owns());
  ASSERT_EQ(c.effective_mode(), MODE_MANUAL);
  ASSERT_EQ(c.state(), STATE_MANUAL);
}

TEST_CASE(auto_without_airiq_downgrades_to_manual) {
  BlowerController c = make_controller();
  c.set_has_airiq(false);          // AirIQ demand contract not composed
  drive(c, T0 + 1000, DEMAND_HIGH);
  ASSERT_FALSE(c.auto_owns());      // engine does not own the output
  ASSERT_TRUE(c.auto_unsupported());
  ASSERT_EQ(c.effective_mode(), MODE_MANUAL);
  ASSERT_EQ(c.state(), STATE_AUTO_UNSUPPORTED);
  ASSERT_STREQ(c.status_string(), "Auto needs AirIQ (not composed) — using Manual");
}

// ---------------------------------------------------------------------------
// Fail-safe — UNKNOWN demand never starts the blower
// ---------------------------------------------------------------------------

TEST_CASE(unknown_demand_never_starts_blower) {
  BlowerController c = make_controller();
  drive(c, T0 + 1000, DEMAND_UNKNOWN);
  ASSERT_TRUE(c.auto_owns());
  ASSERT_FALSE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_UNKNOWN);
}

TEST_CASE(no_demand_keeps_blower_off) {
  BlowerController c = make_controller();
  drive(c, T0 + 1000, DEMAND_NONE);
  ASSERT_TRUE(c.auto_owns());
  ASSERT_FALSE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_OFF);
}

// ---------------------------------------------------------------------------
// Trigger threshold
// ---------------------------------------------------------------------------

TEST_CASE(trigger_now_starts_only_on_ventilate_now) {
  BlowerController c = make_controller();  // TRIGGER_NOW
  drive(c, T0 + 1000, DEMAND_ELEVATED);    // "Ventilate soon" is below the trigger
  ASSERT_FALSE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_OFF);
  drive(c, T0 + 2000, DEMAND_HIGH);        // "Ventilate now" starts it
  ASSERT_TRUE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_ON);
}

TEST_CASE(trigger_soon_starts_on_ventilate_soon) {
  BlowerController c = make_controller();
  c.set_trigger(TRIGGER_SOON);
  drive(c, T0 + 1000, DEMAND_ELEVATED);
  ASSERT_TRUE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_ON);
  drive(c, T0 + 2000, DEMAND_HIGH);        // still on
  ASSERT_TRUE(c.output_on());
}

// ---------------------------------------------------------------------------
// Anti-short-cycle dwell windows
// ---------------------------------------------------------------------------

TEST_CASE(min_on_holds_blower_on_after_demand_clears) {
  BlowerController c = make_controller();
  drive(c, T0 + 1000, DEMAND_HIGH);         // ON at t=1000
  ASSERT_TRUE(c.output_on());
  // Demand clears well before MIN_ON elapses -> held ON.
  drive(c, T0 + 1000 + MIN_ON - 1, DEMAND_NONE);
  ASSERT_TRUE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_MIN_ON);
  // After MIN_ON elapses the blower is finally allowed off.
  drive(c, T0 + 1000 + MIN_ON + 1, DEMAND_NONE);
  ASSERT_FALSE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_OFF);
}

TEST_CASE(first_start_is_never_delayed_by_min_off) {
  BlowerController c = make_controller();
  // Boot OFF, then demand rises: the very first start is immediate (there is no
  // prior run to short-cycle against).
  drive(c, T0, DEMAND_NONE);
  ASSERT_FALSE(c.output_on());
  drive(c, T0 + 100, DEMAND_HIGH);
  ASSERT_TRUE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_ON);
}

TEST_CASE(min_off_blocks_a_quick_restart_after_a_real_run) {
  BlowerController c = make_controller();
  // A real run: ON, then (after min-on) OFF.
  drive(c, T0, DEMAND_HIGH);
  ASSERT_TRUE(c.output_on());
  const uint32_t off_t = T0 + MIN_ON + 1;
  drive(c, off_t, DEMAND_NONE);
  ASSERT_FALSE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_OFF);
  // Demand returns before MIN_OFF elapses -> the restart is held off.
  drive(c, off_t + MIN_OFF - 1, DEMAND_HIGH);
  ASSERT_FALSE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_MIN_OFF);
  // After MIN_OFF elapses the blower may restart.
  drive(c, off_t + MIN_OFF + 1, DEMAND_HIGH);
  ASSERT_TRUE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_ON);
}

TEST_CASE(unknown_demand_during_min_on_finishes_run_then_off) {
  BlowerController c = make_controller();
  drive(c, T0 + 1000, DEMAND_HIGH);  // ON
  ASSERT_TRUE(c.output_on());
  // Demand becomes UNKNOWN mid-run: fail-safe never turns ON from unknown, but
  // the minimum run time is still honoured (motor-friendly) before turning off.
  drive(c, T0 + 1000 + MIN_ON - 1, DEMAND_UNKNOWN);
  ASSERT_TRUE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_MIN_ON);
  drive(c, T0 + 1000 + MIN_ON + 1, DEMAND_UNKNOWN);
  ASSERT_FALSE(c.output_on());
  ASSERT_EQ(c.state(), STATE_AUTO_UNKNOWN);
}

// ---------------------------------------------------------------------------
// Ownership transitions
// ---------------------------------------------------------------------------

TEST_CASE(switching_auto_to_manual_releases_ownership) {
  BlowerController c = make_controller();
  drive(c, T0 + 1000, DEMAND_HIGH);
  ASSERT_TRUE(c.auto_owns());
  ASSERT_TRUE(c.output_on());
  // Customer switches to Manual: the engine stops owning the output.
  c.set_mode(MODE_MANUAL);
  c.evaluate(T0 + 2000);
  ASSERT_FALSE(c.auto_owns());
  ASSERT_EQ(c.state(), STATE_MANUAL);
  // Re-engaging Auto starts fresh (min-off does not spuriously block the first
  // real transition because commit tracking was reset on the Manual pass).
  c.set_mode(MODE_AUTO);
  drive(c, T0 + 3000, DEMAND_HIGH);
  ASSERT_TRUE(c.output_on());
}

// ---------------------------------------------------------------------------
// Vocabulary
// ---------------------------------------------------------------------------

TEST_CASE(string_helpers_are_customer_wording) {
  ASSERT_STREQ(mode_to_string(MODE_MANUAL), "Manual");
  ASSERT_STREQ(mode_to_string(MODE_AUTO), "Auto");
  ASSERT_EQ(mode_from_string("Auto"), MODE_AUTO);
  ASSERT_EQ(mode_from_string("Manual"), MODE_MANUAL);
  ASSERT_EQ(mode_from_string(nullptr), MODE_MANUAL);

  ASSERT_STREQ(trigger_to_string(TRIGGER_NOW), "Ventilate now");
  ASSERT_STREQ(trigger_to_string(TRIGGER_SOON), "Ventilate soon");
  ASSERT_EQ(trigger_from_string("Ventilate soon"), TRIGGER_SOON);
  ASSERT_EQ(trigger_from_string("Ventilate now"), TRIGGER_NOW);

  ASSERT_STREQ(demand_to_string(DEMAND_UNKNOWN), "Unknown");
  ASSERT_STREQ(demand_to_string(DEMAND_HIGH), "Ventilate now");
}

int main() {
  printf("\n=== BLOWER-FRAMEWORK-001 blower controller simulation tests ===\n\n");

  run_test(test_demand_mapping_matches_airiq_recommendation,
           "demand_mapping_matches_airiq_recommendation");
  run_test(test_manual_mode_never_owns_the_output,
           "manual_mode_never_owns_the_output");
  run_test(test_auto_without_airiq_downgrades_to_manual,
           "auto_without_airiq_downgrades_to_manual");
  run_test(test_unknown_demand_never_starts_blower,
           "unknown_demand_never_starts_blower");
  run_test(test_no_demand_keeps_blower_off, "no_demand_keeps_blower_off");
  run_test(test_trigger_now_starts_only_on_ventilate_now,
           "trigger_now_starts_only_on_ventilate_now");
  run_test(test_trigger_soon_starts_on_ventilate_soon,
           "trigger_soon_starts_on_ventilate_soon");
  run_test(test_min_on_holds_blower_on_after_demand_clears,
           "min_on_holds_blower_on_after_demand_clears");
  run_test(test_first_start_is_never_delayed_by_min_off,
           "first_start_is_never_delayed_by_min_off");
  run_test(test_min_off_blocks_a_quick_restart_after_a_real_run,
           "min_off_blocks_a_quick_restart_after_a_real_run");
  run_test(test_unknown_demand_during_min_on_finishes_run_then_off,
           "unknown_demand_during_min_on_finishes_run_then_off");
  run_test(test_switching_auto_to_manual_releases_ownership,
           "switching_auto_to_manual_releases_ownership");
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

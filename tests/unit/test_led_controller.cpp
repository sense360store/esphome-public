// LED-FRAMEWORK-001 — deterministic simulation tests for the customer LED
// controller engine (include/sense360/led_controller.h).
//
// This is the test-only simulation layer for the Sense360 LED customer
// experience: it feeds synthetic, timestamped inputs (customer commands,
// Night Mode requests, occupancy, lux samples, identify requests, status
// events, fault flags) into the SAME header-only engine the production YAML
// compiles (no second implementation that can drift) and asserts
// deterministic light output, layer arbitration, state ownership and
// restore behaviour.
//
// IMPORTANT: a green run here is LOGIC/SIMULATION proof only. It is never
// hardware validation — WS2812B colour order, emitted light, brightness
// perception, thermal and power behaviour remain unverified until the bench
// checklist (docs/hardware/led-framework-bench-checklist.md) is executed by
// the operator.
//
// Compile via tests/Makefile (auto-discovered):  cd tests && make test

#include <cassert>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <exception>

#include "../../include/sense360/led_controller.h"

using namespace sense360::ledfw;

// Simple test framework (repo convention — see test_led_logic.cpp)
#define TEST_CASE(name) void test_##name()
#define ASSERT_TRUE(cond) assert(cond)
#define ASSERT_FALSE(cond) assert(!(cond))
#define ASSERT_EQ(a, b) assert((a) == (b))
#define ASSERT_STREQ(a, b) assert(std::strcmp((a), (b)) == 0)
#define ASSERT_NEAR(a, b, eps) assert(std::fabs((a) - (b)) <= (eps))

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

// Provisional engineering defaults mirrored from the production package
// (packages/features/led_framework.yaml). Pending bench validation.
static const uint32_t IDENTIFY_MS = 4000;
static const uint32_t STATUS_MS = 1500;
static const uint32_t AUTO_OFF_MS = 60000;
static const uint32_t LUX_STALE_MS = 60000;

static const uint32_t T0 = 100000;  // an arbitrary steady-state time

LedController fresh_controller() {
  LedController controller;
  controller.set_identify_duration_ms(IDENTIFY_MS);
  controller.set_status_duration_ms(STATUS_MS);
  controller.set_night_auto_off_ms(AUTO_OFF_MS);
  controller.set_lux_stale_ms(LUX_STALE_MS);
  controller.set_darkness_threshold(20.0f);
  controller.set_darkness_hysteresis(1.5f);
  controller.evaluate(T0);
  return controller;
}

LightState customer_on(float brightness) {
  LightState state;
  state.on = true;
  state.brightness = brightness;
  state.red = 1.0f;
  state.green = 1.0f;
  state.blue = 1.0f;
  state.effect = 0;
  return state;
}

LightState customer_off() {
  LightState state;
  state.on = false;
  state.brightness = 0.5f;
  state.red = 1.0f;
  state.green = 1.0f;
  state.blue = 1.0f;
  state.effect = 0;
  return state;
}

// ---------------------------------------------------------------------------
// Customer Room Light layer
// ---------------------------------------------------------------------------

TEST_CASE(boot_output_is_off_by_default) {
  LedController controller = fresh_controller();
  ASSERT_FALSE(controller.output().on);
  ASSERT_EQ(controller.active_layer(), LAYER_CUSTOMER);
}

TEST_CASE(customer_command_is_reflected) {
  LedController controller = fresh_controller();
  controller.input_customer_command(T0, customer_on(0.6f));
  controller.evaluate(T0);
  ASSERT_TRUE(controller.output().on);
  ASSERT_NEAR(controller.output().brightness, 0.6f, 0.001f);
  ASSERT_EQ(controller.active_layer(), LAYER_CUSTOMER);
}

TEST_CASE(brightness_is_clamped_to_max) {
  LedController controller = fresh_controller();
  controller.set_max_brightness(0.5f);
  controller.input_customer_command(T0, customer_on(1.0f));
  controller.evaluate(T0);
  ASSERT_TRUE(controller.output().brightness <= 0.5f + 0.001f);
  // The persisted customer state is clamped too — no out-of-limit state is
  // ever stored or restored.
  ASSERT_TRUE(controller.customer_state().brightness <= 0.5f + 0.001f);
}

TEST_CASE(invalid_customer_values_are_sanitised) {
  LedController controller = fresh_controller();
  LightState bad = customer_on(NAN);
  bad.red = NAN;
  bad.blue = 7.0f;
  controller.input_customer_command(T0, bad);
  controller.evaluate(T0);
  // NaN brightness falls back to a safe mid value, never full brightness.
  ASSERT_NEAR(controller.output().brightness, 0.5f, 0.001f);
  ASSERT_TRUE(controller.output().red >= 0.0f &&
              controller.output().red <= 1.0f);
  ASSERT_TRUE(controller.output().blue >= 0.0f &&
              controller.output().blue <= 1.0f);
}

// ---------------------------------------------------------------------------
// Night Mode (LED-02)
// ---------------------------------------------------------------------------

TEST_CASE(night_mode_applies_low_warm_profile) {
  LedController controller = fresh_controller();
  controller.input_customer_command(T0, customer_on(0.8f));
  controller.set_night_mode(T0 + 1000, true, false);
  controller.evaluate(T0 + 1000);
  ASSERT_TRUE(controller.night_mode());
  ASSERT_EQ(controller.active_layer(), LAYER_NIGHT);
  ASSERT_TRUE(controller.output().on);
  // Provisional night profile: low (default 5%) and warm (red-dominant, low
  // blue) — never full brightness, never blue-heavy.
  ASSERT_TRUE(controller.output().brightness <= 0.10f);
  ASSERT_TRUE(controller.output().red > controller.output().blue);
}

TEST_CASE(night_mode_off_restores_previous_customer_state) {
  LedController controller = fresh_controller();
  controller.input_customer_command(T0, customer_on(0.8f));
  controller.set_night_mode(T0 + 1000, true, false);
  controller.evaluate(T0 + 1000);
  controller.set_night_mode(T0 + 2000, false, false);
  controller.evaluate(T0 + 2000);
  ASSERT_FALSE(controller.night_mode());
  ASSERT_TRUE(controller.output().on);
  ASSERT_NEAR(controller.output().brightness, 0.8f, 0.001f);
}

TEST_CASE(night_mode_preserves_stored_customer_state) {
  LedController controller = fresh_controller();
  controller.input_customer_command(T0, customer_on(0.8f));
  controller.set_night_mode(T0 + 1000, true, false);
  controller.evaluate(T0 + 1000);
  ASSERT_NEAR(controller.customer_state().brightness, 0.8f, 0.001f);
  ASSERT_TRUE(controller.customer_state().on);
}

TEST_CASE(night_mode_restores_off_state) {
  LedController controller = fresh_controller();
  controller.input_customer_command(T0, customer_off());
  controller.set_night_mode(T0 + 1000, true, false);
  controller.evaluate(T0 + 1000);
  controller.set_night_mode(T0 + 2000, false, false);
  controller.evaluate(T0 + 2000);
  ASSERT_FALSE(controller.output().on);
}

TEST_CASE(manual_light_change_during_night_mode_wins) {
  LedController controller = fresh_controller();
  controller.set_night_mode(T0, true, false);
  controller.evaluate(T0);
  ASSERT_TRUE(controller.night_mode());
  controller.input_customer_command(T0 + 1000, customer_on(0.7f));
  controller.evaluate(T0 + 1000);
  // Customer intent wins cleanly: Night Mode disengages and the light
  // follows the customer's command.
  ASSERT_FALSE(controller.night_mode());
  ASSERT_NEAR(controller.output().brightness, 0.7f, 0.001f);
  ASSERT_EQ(controller.active_layer(), LAYER_CUSTOMER);
}

TEST_CASE(night_profile_respects_max_brightness) {
  LedController controller = fresh_controller();
  controller.set_max_brightness(0.03f);
  controller.set_night_mode(T0, true, false);
  controller.evaluate(T0);
  ASSERT_TRUE(controller.output().brightness <= 0.03f + 0.001f);
}

TEST_CASE(night_mode_never_forces_full_brightness) {
  LedController controller = fresh_controller();
  controller.set_night_mode(T0, true, false);
  controller.evaluate(T0);
  ASSERT_TRUE(controller.output().brightness < 0.5f);
}

// ---------------------------------------------------------------------------
// Night Mode Behaviour — darkness / occupancy automation (LED-03/04/05)
// ---------------------------------------------------------------------------

TEST_CASE(manual_behaviour_ignores_occupancy_and_lux) {
  LedController controller = fresh_controller();
  controller.set_night_behaviour(NIGHT_MANUAL);
  controller.input_lux(T0, 2.0f);
  controller.input_occupancy(T0, true, true);
  controller.evaluate(T0);
  ASSERT_FALSE(controller.night_mode());
}

TEST_CASE(when_dark_activates_night_mode) {
  LedController controller = fresh_controller();
  controller.set_night_behaviour(NIGHT_WHEN_DARK);
  controller.input_lux(T0, 5.0f);
  controller.evaluate(T0);
  ASSERT_TRUE(controller.night_mode());
  ASSERT_TRUE(controller.night_automation_owned());
}

TEST_CASE(when_dark_deactivates_only_automation_owned) {
  LedController controller = fresh_controller();
  controller.set_night_behaviour(NIGHT_WHEN_DARK);
  controller.input_lux(T0, 5.0f);
  controller.evaluate(T0);
  ASSERT_TRUE(controller.night_mode());
  controller.input_lux(T0 + 1000, 100.0f);
  controller.evaluate(T0 + 1000);
  ASSERT_FALSE(controller.night_mode());

  // A manually enabled Night Mode is never reversed by brightness.
  controller.set_night_mode(T0 + 2000, true, false);
  controller.input_lux(T0 + 3000, 100.0f);
  controller.evaluate(T0 + 3000);
  ASSERT_TRUE(controller.night_mode());
}

TEST_CASE(darkness_hysteresis_prevents_oscillation) {
  LedController controller = fresh_controller();
  // Threshold 20 lx, hysteresis factor 1.5 -> not-dark above 30 lx.
  controller.input_lux(T0, 19.0f);
  controller.evaluate(T0);
  ASSERT_EQ(controller.darkness(), DARKNESS_DARK);
  controller.input_lux(T0 + 1000, 25.0f);  // between 20 and 30: hold dark
  controller.evaluate(T0 + 1000);
  ASSERT_EQ(controller.darkness(), DARKNESS_DARK);
  controller.input_lux(T0 + 2000, 31.0f);
  controller.evaluate(T0 + 2000);
  ASSERT_EQ(controller.darkness(), DARKNESS_NOT_DARK);
  controller.input_lux(T0 + 3000, 25.0f);  // between: hold not-dark
  controller.evaluate(T0 + 3000);
  ASSERT_EQ(controller.darkness(), DARKNESS_NOT_DARK);
}

TEST_CASE(stale_lux_is_unknown_never_dark) {
  LedController controller = fresh_controller();
  controller.set_night_behaviour(NIGHT_WHEN_DARK);
  controller.input_lux(T0, 100.0f);
  controller.evaluate(T0);
  ASSERT_EQ(controller.darkness(), DARKNESS_NOT_DARK);
  // No lux updates past the stale window: darkness is UNKNOWN, and unknown
  // darkness never activates Night Mode.
  controller.evaluate(T0 + LUX_STALE_MS + 1000);
  ASSERT_EQ(controller.darkness(), DARKNESS_UNKNOWN);
  ASSERT_FALSE(controller.night_mode());
}

TEST_CASE(stale_lux_holds_active_night_mode_without_toggling) {
  LedController controller = fresh_controller();
  controller.set_night_behaviour(NIGHT_WHEN_DARK);
  controller.input_lux(T0, 5.0f);
  controller.evaluate(T0);
  ASSERT_TRUE(controller.night_mode());
  // Lux goes stale: fail safe — hold the current state, never flap.
  for (uint32_t t = T0 + LUX_STALE_MS + 1000; t < T0 + LUX_STALE_MS + 20000;
       t += 1000) {
    controller.evaluate(t);
    ASSERT_TRUE(controller.night_mode());
  }
}

TEST_CASE(nan_lux_is_unknown) {
  LedController controller = fresh_controller();
  controller.input_lux(T0, NAN);
  controller.evaluate(T0);
  ASSERT_EQ(controller.darkness(), DARKNESS_UNKNOWN);
}

TEST_CASE(dark_and_occupied_requires_both) {
  LedController controller = fresh_controller();
  controller.set_night_behaviour(NIGHT_WHEN_DARK_AND_OCCUPIED);
  controller.input_lux(T0, 5.0f);
  controller.input_occupancy(T0, false, true);
  controller.evaluate(T0);
  ASSERT_FALSE(controller.night_mode());
  controller.input_occupancy(T0 + 1000, true, true);
  controller.evaluate(T0 + 1000);
  ASSERT_TRUE(controller.night_mode());
  ASSERT_TRUE(controller.night_automation_owned());
}

TEST_CASE(occupancy_clear_reverses_only_automation_after_delay) {
  LedController controller = fresh_controller();
  controller.set_night_behaviour(NIGHT_WHEN_DARK_AND_OCCUPIED);
  controller.input_lux(T0, 5.0f);
  controller.input_occupancy(T0, true, true);
  controller.evaluate(T0);
  ASSERT_TRUE(controller.night_mode());
  // Occupancy clears: night mode holds during the auto-off delay... (the
  // lux sensor keeps updating, as the real VEML7700 does every 10 s — a
  // stale lux would fail safe and freeze the automation instead)
  controller.input_occupancy(T0 + 1000, false, true);
  controller.input_lux(T0 + 1000, 5.0f);
  controller.evaluate(T0 + 1000);
  ASSERT_TRUE(controller.night_mode());
  controller.input_lux(T0 + 1000 + AUTO_OFF_MS / 2, 5.0f);
  controller.evaluate(T0 + 1000 + AUTO_OFF_MS / 2);
  ASSERT_TRUE(controller.night_mode());
  // ...then turns off.
  controller.input_lux(T0 + 1000 + AUTO_OFF_MS + 1000, 5.0f);
  controller.evaluate(T0 + 1000 + AUTO_OFF_MS + 1000);
  ASSERT_FALSE(controller.night_mode());
}

TEST_CASE(manual_night_mode_is_never_cleared_by_occupancy) {
  LedController controller = fresh_controller();
  controller.set_night_behaviour(NIGHT_WHEN_DARK_AND_OCCUPIED);
  controller.set_night_mode(T0, true, false);  // manual
  controller.input_lux(T0, 5.0f);
  controller.input_occupancy(T0, false, true);
  controller.evaluate(T0);
  controller.input_lux(T0 + AUTO_OFF_MS + 5000, 5.0f);
  controller.evaluate(T0 + AUTO_OFF_MS + 5000);
  ASSERT_TRUE(controller.night_mode());
}

TEST_CASE(fresh_occupancy_cancels_pending_auto_off) {
  LedController controller = fresh_controller();
  controller.set_night_behaviour(NIGHT_WHEN_DARK_AND_OCCUPIED);
  controller.input_lux(T0, 5.0f);
  controller.input_occupancy(T0, true, true);
  controller.evaluate(T0);
  controller.input_occupancy(T0 + 1000, false, true);
  controller.input_lux(T0 + 1000, 5.0f);
  controller.evaluate(T0 + 1000);
  // Reoccupied before the auto-off delay expires: the pending off is
  // cancelled...
  controller.input_occupancy(T0 + 5000, true, true);
  controller.input_lux(T0 + 5000, 5.0f);
  controller.evaluate(T0 + 5000);
  // ...even long past the original deadline (with live inputs throughout).
  controller.input_lux(T0 + 1000 + AUTO_OFF_MS + 5000, 5.0f);
  controller.evaluate(T0 + 1000 + AUTO_OFF_MS + 5000);
  ASSERT_TRUE(controller.night_mode());
}

TEST_CASE(invalid_occupancy_freezes_automation) {
  LedController controller = fresh_controller();
  controller.set_night_behaviour(NIGHT_WHEN_DARK_AND_OCCUPIED);
  controller.input_lux(T0, 5.0f);
  controller.input_occupancy(T0, true, true);
  controller.evaluate(T0);
  ASSERT_TRUE(controller.night_mode());
  // Presence degraded to invalid: hold the current state — no flashing, no
  // repeated toggles, no auto-off from unknown data.
  for (uint32_t t = T0 + 1000; t < T0 + 2 * AUTO_OFF_MS; t += 5000) {
    controller.input_occupancy(t, false, false);
    controller.input_lux(t, 5.0f);
    controller.evaluate(t);
    ASSERT_TRUE(controller.night_mode());
  }
  // And invalid occupancy never activates Night Mode either.
  LedController other = fresh_controller();
  other.set_night_behaviour(NIGHT_WHEN_DARK_AND_OCCUPIED);
  other.input_lux(T0, 5.0f);
  other.input_occupancy(T0, true, false);
  other.evaluate(T0);
  ASSERT_FALSE(other.night_mode());
}

TEST_CASE(automation_never_dims_an_in_use_room_light) {
  LedController controller = fresh_controller();
  controller.set_night_behaviour(NIGHT_WHEN_DARK);
  controller.input_customer_command(T0, customer_on(0.8f));
  controller.input_lux(T0 + 1000, 5.0f);
  controller.evaluate(T0 + 1000);
  // The room light is in use: automation must not pre-empt it (Presence /
  // darkness never turns the normal Room Light output down unexpectedly).
  ASSERT_FALSE(controller.night_mode());
  ASSERT_NEAR(controller.output().brightness, 0.8f, 0.001f);
}

TEST_CASE(manual_night_off_suppresses_reactivation_until_rearm) {
  LedController controller = fresh_controller();
  controller.set_night_behaviour(NIGHT_WHEN_DARK);
  controller.input_lux(T0, 5.0f);
  controller.evaluate(T0);
  ASSERT_TRUE(controller.night_mode());
  // Customer turns Night Mode off while it is still dark: automation must
  // not fight the customer.
  controller.set_night_mode(T0 + 1000, false, false);
  controller.input_lux(T0 + 2000, 5.0f);
  controller.evaluate(T0 + 2000);
  ASSERT_FALSE(controller.night_mode());
  // The trigger re-arms only after the condition resets (bright again)...
  controller.input_lux(T0 + 3000, 100.0f);
  controller.evaluate(T0 + 3000);
  // ...so the next darkness re-activates.
  controller.input_lux(T0 + 4000, 5.0f);
  controller.evaluate(T0 + 4000);
  ASSERT_TRUE(controller.night_mode());
}

// ---------------------------------------------------------------------------
// Identify (LED-08)
// ---------------------------------------------------------------------------

TEST_CASE(identify_overrides_and_restores_customer_state) {
  LedController controller = fresh_controller();
  controller.input_customer_command(T0, customer_on(0.8f));
  controller.request_identify(T0 + 1000);
  controller.evaluate(T0 + 1000);
  ASSERT_EQ(controller.active_layer(), LAYER_IDENTIFY);
  ASSERT_TRUE(controller.output().on);
  // Non-disruptive: the identify pulse stays well below full brightness.
  ASSERT_TRUE(controller.output().brightness <= 0.45f);
  // After the identify window the previous customer state returns exactly.
  controller.evaluate(T0 + 1000 + IDENTIFY_MS + 100);
  ASSERT_EQ(controller.active_layer(), LAYER_CUSTOMER);
  ASSERT_NEAR(controller.output().brightness, 0.8f, 0.001f);
}

TEST_CASE(identify_respects_max_brightness) {
  LedController controller = fresh_controller();
  controller.set_max_brightness(0.2f);
  controller.request_identify(T0);
  controller.evaluate(T0 + 500);
  ASSERT_TRUE(controller.output().brightness <= 0.2f + 0.001f);
}

TEST_CASE(identify_returns_to_night_mode) {
  LedController controller = fresh_controller();
  controller.set_night_mode(T0, true, false);
  controller.evaluate(T0);
  controller.request_identify(T0 + 1000);
  controller.evaluate(T0 + 1000);
  ASSERT_EQ(controller.active_layer(), LAYER_IDENTIFY);
  controller.evaluate(T0 + 1000 + IDENTIFY_MS + 100);
  ASSERT_EQ(controller.active_layer(), LAYER_NIGHT);
  ASSERT_TRUE(controller.night_mode());
}

TEST_CASE(repeated_identify_requests_do_not_stick) {
  LedController controller = fresh_controller();
  controller.input_customer_command(T0, customer_off());
  controller.request_identify(T0 + 1000);
  controller.evaluate(T0 + 1000);
  controller.request_identify(T0 + 2000);  // restart while running
  controller.evaluate(T0 + 2000);
  ASSERT_EQ(controller.active_layer(), LAYER_IDENTIFY);
  controller.evaluate(T0 + 2000 + IDENTIFY_MS + 100);
  ASSERT_EQ(controller.active_layer(), LAYER_CUSTOMER);
  ASSERT_FALSE(controller.output().on);
}

TEST_CASE(customer_command_cancels_identify) {
  LedController controller = fresh_controller();
  controller.request_identify(T0);
  controller.evaluate(T0 + 500);
  ASSERT_EQ(controller.active_layer(), LAYER_IDENTIFY);
  controller.input_customer_command(T0 + 1000, customer_on(0.6f));
  controller.evaluate(T0 + 1000);
  ASSERT_EQ(controller.active_layer(), LAYER_CUSTOMER);
  ASSERT_NEAR(controller.output().brightness, 0.6f, 0.001f);
}

// ---------------------------------------------------------------------------
// Status indication (LED-06 / LED-07)
// ---------------------------------------------------------------------------

TEST_CASE(status_blip_shows_when_idle_then_restores) {
  LedController controller = fresh_controller();
  controller.set_status_level(STATUS_LEVEL_ESSENTIAL);
  controller.input_customer_command(T0, customer_off());
  controller.notify_status(T0 + 1000, EVENT_STARTUP);
  controller.evaluate(T0 + 1000);
  ASSERT_EQ(controller.active_layer(), LAYER_STATUS);
  ASSERT_TRUE(controller.output().on);
  controller.evaluate(T0 + 1000 + STATUS_MS + 100);
  ASSERT_EQ(controller.active_layer(), LAYER_CUSTOMER);
  ASSERT_FALSE(controller.output().on);
}

TEST_CASE(status_never_interrupts_an_on_room_light) {
  LedController controller = fresh_controller();
  controller.set_status_level(STATUS_LEVEL_ESSENTIAL);
  controller.input_customer_command(T0, customer_on(0.8f));
  controller.notify_status(T0 + 1000, EVENT_CONNECTED);
  controller.evaluate(T0 + 1000);
  // Transient informational status is subordinate to the customer light.
  ASSERT_EQ(controller.active_layer(), LAYER_CUSTOMER);
  ASSERT_NEAR(controller.output().brightness, 0.8f, 0.001f);
}

TEST_CASE(status_level_off_suppresses_everything) {
  LedController controller = fresh_controller();
  controller.set_status_level(STATUS_LEVEL_OFF);
  controller.input_customer_command(T0, customer_off());
  controller.notify_status(T0 + 1000, EVENT_STARTUP);
  controller.evaluate(T0 + 1000);
  ASSERT_EQ(controller.active_layer(), LAYER_CUSTOMER);
  ASSERT_FALSE(controller.output().on);
}

TEST_CASE(detail_events_show_only_in_detailed) {
  LedController essential = fresh_controller();
  essential.set_status_level(STATUS_LEVEL_ESSENTIAL);
  essential.input_customer_command(T0, customer_off());
  essential.notify_status(T0 + 1000, EVENT_DETAIL_INFO);
  essential.evaluate(T0 + 1000);
  ASSERT_EQ(essential.active_layer(), LAYER_CUSTOMER);

  LedController detailed = fresh_controller();
  detailed.set_status_level(STATUS_LEVEL_DETAILED);
  detailed.input_customer_command(T0, customer_off());
  detailed.notify_status(T0 + 1000, EVENT_DETAIL_INFO);
  detailed.evaluate(T0 + 1000);
  ASSERT_EQ(detailed.active_layer(), LAYER_STATUS);
}

TEST_CASE(status_suppressed_during_night_mode) {
  LedController controller = fresh_controller();
  controller.set_status_level(STATUS_LEVEL_ESSENTIAL);
  controller.set_night_mode(T0, true, false);
  controller.evaluate(T0);
  controller.notify_status(T0 + 1000, EVENT_CONNECTED);
  controller.evaluate(T0 + 1000);
  // Night Mode outranks transient status: no blinking at a dark room.
  ASSERT_EQ(controller.active_layer(), LAYER_NIGHT);
}

TEST_CASE(repeated_status_events_do_not_stick) {
  LedController controller = fresh_controller();
  controller.set_status_level(STATUS_LEVEL_ESSENTIAL);
  controller.input_customer_command(T0, customer_off());
  controller.notify_status(T0 + 1000, EVENT_STARTUP);
  controller.evaluate(T0 + 1000);
  controller.notify_status(T0 + 1200, EVENT_CONNECTED);
  controller.evaluate(T0 + 1200);
  controller.evaluate(T0 + 1200 + STATUS_MS + 100);
  ASSERT_EQ(controller.active_layer(), LAYER_CUSTOMER);
  ASSERT_FALSE(controller.output().on);
}

TEST_CASE(status_respects_max_brightness) {
  LedController controller = fresh_controller();
  controller.set_max_brightness(0.15f);
  controller.set_status_level(STATUS_LEVEL_ESSENTIAL);
  controller.input_customer_command(T0, customer_off());
  controller.notify_status(T0 + 1000, EVENT_WARNING);
  controller.evaluate(T0 + 1000);
  ASSERT_TRUE(controller.output().brightness <= 0.15f + 0.001f);
}

// ---------------------------------------------------------------------------
// Fault layer (LED-07 priority 1; producer reserved — engine contract only)
// ---------------------------------------------------------------------------

TEST_CASE(fault_overrides_everything_and_persists) {
  LedController controller = fresh_controller();
  controller.input_customer_command(T0, customer_on(0.8f));
  controller.request_identify(T0 + 1000);
  controller.set_fault(true);
  controller.evaluate(T0 + 1000);
  ASSERT_EQ(controller.active_layer(), LAYER_FAULT);
  // Persistent: still fault long past every transient duration.
  controller.evaluate(T0 + 1000 + IDENTIFY_MS + STATUS_MS + 10000);
  ASSERT_EQ(controller.active_layer(), LAYER_FAULT);
}

TEST_CASE(fault_clear_restores_customer_state) {
  LedController controller = fresh_controller();
  controller.input_customer_command(T0, customer_on(0.8f));
  controller.set_fault(true);
  controller.evaluate(T0 + 1000);
  controller.set_fault(false);
  controller.evaluate(T0 + 2000);
  ASSERT_EQ(controller.active_layer(), LAYER_CUSTOMER);
  ASSERT_NEAR(controller.output().brightness, 0.8f, 0.001f);
  // An error never destroys the customer's chosen state.
  ASSERT_NEAR(controller.customer_state().brightness, 0.8f, 0.001f);
}

TEST_CASE(identify_does_not_preempt_fault) {
  LedController controller = fresh_controller();
  controller.set_fault(true);
  controller.evaluate(T0);
  controller.request_identify(T0 + 1000);
  controller.evaluate(T0 + 1000);
  ASSERT_EQ(controller.active_layer(), LAYER_FAULT);
}

// ---------------------------------------------------------------------------
// Restart / restore contract (LED-11)
// ---------------------------------------------------------------------------

TEST_CASE(restore_reapplies_stable_customer_state) {
  LedController controller = fresh_controller();
  controller.restore(customer_on(0.6f), false, false);
  controller.evaluate(T0);
  ASSERT_TRUE(controller.output().on);
  ASSERT_NEAR(controller.output().brightness, 0.6f, 0.001f);
  ASSERT_EQ(controller.active_layer(), LAYER_CUSTOMER);
}

TEST_CASE(restore_reapplies_night_mode_and_ownership) {
  LedController controller = fresh_controller();
  controller.set_night_behaviour(NIGHT_WHEN_DARK_AND_OCCUPIED);
  controller.restore(customer_off(), true, true);
  controller.evaluate(T0);
  ASSERT_TRUE(controller.night_mode());
  ASSERT_TRUE(controller.night_automation_owned());
  ASSERT_EQ(controller.active_layer(), LAYER_NIGHT);
  // Ownership survived the restart, so a later valid clear still reverses
  // the automation's own activation (after the auto-off delay, with live
  // inputs throughout).
  controller.input_lux(T0 + 1000, 5.0f);
  controller.input_occupancy(T0 + 1000, false, true);
  controller.evaluate(T0 + 1000);
  ASSERT_TRUE(controller.night_mode());
  controller.input_lux(T0 + 1000 + AUTO_OFF_MS + 1000, 5.0f);
  controller.evaluate(T0 + 1000 + AUTO_OFF_MS + 1000);
  ASSERT_FALSE(controller.night_mode());
}

TEST_CASE(restore_sanitises_invalid_stored_state) {
  LedController controller = fresh_controller();
  LightState corrupt = customer_on(NAN);
  corrupt.red = -3.0f;
  corrupt.green = NAN;
  controller.restore(corrupt, false, false);
  controller.evaluate(T0);
  // Safe fallback: mid brightness, in-range colour — never an unexpected
  // full-brightness boot.
  ASSERT_TRUE(controller.output().brightness <= 0.5f + 0.001f);
  ASSERT_TRUE(controller.output().red >= 0.0f &&
              controller.output().red <= 1.0f);
  ASSERT_TRUE(controller.output().green >= 0.0f &&
              controller.output().green <= 1.0f);
}

TEST_CASE(restore_never_resumes_transient_layers) {
  LedController controller = fresh_controller();
  controller.restore(customer_on(0.6f), false, false);
  controller.evaluate(T0);
  // The restore API has no transient inputs by design: after a restart the
  // active layer is always Night Mode or Room Light, never Identify/Status.
  ASSERT_TRUE(controller.active_layer() == LAYER_CUSTOMER ||
              controller.active_layer() == LAYER_NIGHT);
}

// ---------------------------------------------------------------------------
// Effects interaction (LED-10)
// ---------------------------------------------------------------------------

TEST_CASE(customer_effect_is_preserved_across_overlays) {
  LedController controller = fresh_controller();
  LightState with_effect = customer_on(0.6f);
  with_effect.effect = 1;  // Gentle Pulse
  controller.input_customer_command(T0, with_effect);
  controller.evaluate(T0);
  ASSERT_EQ(controller.output().effect, 1);
  // Overlays run without effects...
  controller.request_identify(T0 + 1000);
  controller.evaluate(T0 + 1000);
  ASSERT_EQ(controller.output().effect, 0);
  // ...and the customer's effect returns afterwards.
  controller.evaluate(T0 + 1000 + IDENTIFY_MS + 100);
  ASSERT_EQ(controller.output().effect, 1);
}

TEST_CASE(night_mode_runs_without_effects) {
  LedController controller = fresh_controller();
  LightState with_effect = customer_on(0.6f);
  with_effect.effect = 1;
  controller.input_customer_command(T0, with_effect);
  controller.set_night_mode(T0 + 1000, true, false);
  controller.evaluate(T0 + 1000);
  ASSERT_EQ(controller.output().effect, 0);
  controller.set_night_mode(T0 + 2000, false, false);
  controller.evaluate(T0 + 2000);
  ASSERT_EQ(controller.output().effect, 1);
}

// ---------------------------------------------------------------------------
// String contracts (single-sourced customer wording)
// ---------------------------------------------------------------------------

TEST_CASE(string_tables_are_single_sourced) {
  ASSERT_STREQ(layer_to_string(LAYER_FAULT), "Fault");
  ASSERT_STREQ(layer_to_string(LAYER_IDENTIFY), "Identify");
  ASSERT_STREQ(layer_to_string(LAYER_NIGHT), "Night Mode");
  ASSERT_STREQ(layer_to_string(LAYER_CUSTOMER), "Room Light");
  ASSERT_STREQ(layer_to_string(LAYER_STATUS), "Status");

  ASSERT_STREQ(darkness_to_string(DARKNESS_UNKNOWN), "Unknown");
  ASSERT_STREQ(darkness_to_string(DARKNESS_DARK), "Dark");
  ASSERT_STREQ(darkness_to_string(DARKNESS_NOT_DARK), "Not dark");

  ASSERT_EQ(night_behaviour_from_string("Manual"), NIGHT_MANUAL);
  ASSERT_EQ(night_behaviour_from_string("When dark"), NIGHT_WHEN_DARK);
  ASSERT_EQ(night_behaviour_from_string("When dark and occupied"),
            NIGHT_WHEN_DARK_AND_OCCUPIED);
  // Unknown wording falls back to the safe default (Manual — no automation).
  ASSERT_EQ(night_behaviour_from_string("garbage"), NIGHT_MANUAL);
  ASSERT_EQ(night_behaviour_from_string(nullptr), NIGHT_MANUAL);

  ASSERT_EQ(status_level_from_string("Off"), STATUS_LEVEL_OFF);
  ASSERT_EQ(status_level_from_string("Essential"), STATUS_LEVEL_ESSENTIAL);
  ASSERT_EQ(status_level_from_string("Detailed"), STATUS_LEVEL_DETAILED);
  ASSERT_EQ(status_level_from_string("garbage"), STATUS_LEVEL_ESSENTIAL);
}

// ---------------------------------------------------------------------------

int main() {
  printf("\n=== LED-FRAMEWORK-001 controller simulation tests ===\n");
  printf("(logic/simulation proof only — never hardware validation)\n\n");

  run_test(test_boot_output_is_off_by_default, "boot_output_is_off_by_default");
  run_test(test_customer_command_is_reflected, "customer_command_is_reflected");
  run_test(test_brightness_is_clamped_to_max, "brightness_is_clamped_to_max");
  run_test(test_invalid_customer_values_are_sanitised,
           "invalid_customer_values_are_sanitised");

  run_test(test_night_mode_applies_low_warm_profile,
           "night_mode_applies_low_warm_profile");
  run_test(test_night_mode_off_restores_previous_customer_state,
           "night_mode_off_restores_previous_customer_state");
  run_test(test_night_mode_preserves_stored_customer_state,
           "night_mode_preserves_stored_customer_state");
  run_test(test_night_mode_restores_off_state, "night_mode_restores_off_state");
  run_test(test_manual_light_change_during_night_mode_wins,
           "manual_light_change_during_night_mode_wins");
  run_test(test_night_profile_respects_max_brightness,
           "night_profile_respects_max_brightness");
  run_test(test_night_mode_never_forces_full_brightness,
           "night_mode_never_forces_full_brightness");

  run_test(test_manual_behaviour_ignores_occupancy_and_lux,
           "manual_behaviour_ignores_occupancy_and_lux");
  run_test(test_when_dark_activates_night_mode,
           "when_dark_activates_night_mode");
  run_test(test_when_dark_deactivates_only_automation_owned,
           "when_dark_deactivates_only_automation_owned");
  run_test(test_darkness_hysteresis_prevents_oscillation,
           "darkness_hysteresis_prevents_oscillation");
  run_test(test_stale_lux_is_unknown_never_dark,
           "stale_lux_is_unknown_never_dark");
  run_test(test_stale_lux_holds_active_night_mode_without_toggling,
           "stale_lux_holds_active_night_mode_without_toggling");
  run_test(test_nan_lux_is_unknown, "nan_lux_is_unknown");
  run_test(test_dark_and_occupied_requires_both,
           "dark_and_occupied_requires_both");
  run_test(test_occupancy_clear_reverses_only_automation_after_delay,
           "occupancy_clear_reverses_only_automation_after_delay");
  run_test(test_manual_night_mode_is_never_cleared_by_occupancy,
           "manual_night_mode_is_never_cleared_by_occupancy");
  run_test(test_fresh_occupancy_cancels_pending_auto_off,
           "fresh_occupancy_cancels_pending_auto_off");
  run_test(test_invalid_occupancy_freezes_automation,
           "invalid_occupancy_freezes_automation");
  run_test(test_automation_never_dims_an_in_use_room_light,
           "automation_never_dims_an_in_use_room_light");
  run_test(test_manual_night_off_suppresses_reactivation_until_rearm,
           "manual_night_off_suppresses_reactivation_until_rearm");

  run_test(test_identify_overrides_and_restores_customer_state,
           "identify_overrides_and_restores_customer_state");
  run_test(test_identify_respects_max_brightness,
           "identify_respects_max_brightness");
  run_test(test_identify_returns_to_night_mode,
           "identify_returns_to_night_mode");
  run_test(test_repeated_identify_requests_do_not_stick,
           "repeated_identify_requests_do_not_stick");
  run_test(test_customer_command_cancels_identify,
           "customer_command_cancels_identify");

  run_test(test_status_blip_shows_when_idle_then_restores,
           "status_blip_shows_when_idle_then_restores");
  run_test(test_status_never_interrupts_an_on_room_light,
           "status_never_interrupts_an_on_room_light");
  run_test(test_status_level_off_suppresses_everything,
           "status_level_off_suppresses_everything");
  run_test(test_detail_events_show_only_in_detailed,
           "detail_events_show_only_in_detailed");
  run_test(test_status_suppressed_during_night_mode,
           "status_suppressed_during_night_mode");
  run_test(test_repeated_status_events_do_not_stick,
           "repeated_status_events_do_not_stick");
  run_test(test_status_respects_max_brightness,
           "status_respects_max_brightness");

  run_test(test_fault_overrides_everything_and_persists,
           "fault_overrides_everything_and_persists");
  run_test(test_fault_clear_restores_customer_state,
           "fault_clear_restores_customer_state");
  run_test(test_identify_does_not_preempt_fault,
           "identify_does_not_preempt_fault");

  run_test(test_restore_reapplies_stable_customer_state,
           "restore_reapplies_stable_customer_state");
  run_test(test_restore_reapplies_night_mode_and_ownership,
           "restore_reapplies_night_mode_and_ownership");
  run_test(test_restore_sanitises_invalid_stored_state,
           "restore_sanitises_invalid_stored_state");
  run_test(test_restore_never_resumes_transient_layers,
           "restore_never_resumes_transient_layers");

  run_test(test_customer_effect_is_preserved_across_overlays,
           "customer_effect_is_preserved_across_overlays");
  run_test(test_night_mode_runs_without_effects,
           "night_mode_runs_without_effects");

  run_test(test_string_tables_are_single_sourced,
           "string_tables_are_single_sourced");

  printf("\n%d/%d tests passed\n", passed_count, test_count);
  return passed_count == test_count ? 0 : 1;
}

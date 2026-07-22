// LED-FRAMEWORK-002 — the LED controller and the canonical RoomIQ engine
// headers must COEXIST in a single translation unit and cooperate.
//
// The production LED framework (packages/features/led_framework.yaml) compiles
// BOTH include/sense360/led_controller.h AND include/sense360/roomiq_engine.h
// into the build, then its evaluate lambda maps the RoomIQ darkness decision
// into the LED controller. This test compiles the exact cross-namespace
// pattern that lambda emits, so a C++ regression (a clashing enum, a namespace
// slip) is caught by the native suite rather than only by a full
// `esphome compile` (whose ESP toolchain download is not available offline).
//
// A green run here is LOGIC/COMPILATION proof only — never hardware validation.
//
// Compile via tests/Makefile (auto-discovered):  cd tests && make test

#include <cassert>
#include <cstdint>
#include <cstdio>

#include "../../include/sense360/led_controller.h"
#include "../../include/sense360/roomiq_engine.h"

using namespace sense360::ledfw;

// Mirror of the led_framework darkness bridge: consult the canonical RoomIQ
// engine and inject its decision as the LED controller's darkness input.
static Darkness roomiq_darkness_bridge(sense360::roomiq::RoomIQEngine &env,
                                       uint32_t now) {
  env.evaluate(now);
  if (env.darkness() == sense360::roomiq::DARKNESS_DARK) return DARKNESS_DARK;
  if (env.darkness() == sense360::roomiq::DARKNESS_NOT_DARK)
    return DARKNESS_NOT_DARK;
  return DARKNESS_UNKNOWN;
}

int main() {
  printf("\n=== LED-FRAMEWORK-002 header-coexistence test ===\n");

  LedController controller;
  sense360::roomiq::RoomIQEngine environment;
  const uint32_t now = 1000;

  // AirIQ-only device: no RoomIQ, no Presence composed.
  controller.set_capabilities(false, false);

  // Darkness bridge with no lux ever fed -> Unknown (never invented).
  environment.set_darkness_threshold(20.0f);
  environment.set_darkness_hysteresis(1.5f);
  controller.input_darkness(now, roomiq_darkness_bridge(environment, now));
  controller.input_occupancy(now, false, false);
  controller.set_night_behaviour(NIGHT_WHEN_DARK);
  controller.evaluate(now);

  // Fail-safe: Unknown darkness + no RoomIQ capability -> no automatic night.
  assert(controller.darkness() == DARKNESS_UNKNOWN);
  assert(!controller.night_mode());
  assert(controller.effective_behaviour() == NIGHT_MANUAL);

  // With RoomIQ present and real dark lux, the SAME bridge activates it.
  LedController capable;
  capable.set_capabilities(true, false);
  sense360::roomiq::RoomIQEngine dark_env;
  dark_env.set_darkness_threshold(20.0f);
  dark_env.set_darkness_hysteresis(1.5f);
  dark_env.input_lux(now, 5.0f);  // below threshold -> dark
  capable.input_darkness(now, roomiq_darkness_bridge(dark_env, now));
  capable.set_night_behaviour(NIGHT_WHEN_DARK);
  capable.evaluate(now);
  assert(capable.darkness() == DARKNESS_DARK);
  assert(capable.night_mode());

  printf("[PASS] led_controller.h + roomiq_engine.h coexist and cooperate\n");
  printf("\n1/1 tests passed\n");
  return 0;
}

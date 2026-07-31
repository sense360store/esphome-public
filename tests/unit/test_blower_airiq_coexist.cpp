// BLOWER-FRAMEWORK-001 — the blower controller and the canonical AirIQ engine
// headers must COEXIST in a single translation unit and cooperate.
//
// The production blower framework (packages/features/blower_framework.yaml)
// compiles BOTH components/sense360/blower_controller.h AND
// components/sense360/airiq_engine.h into the build, then its evaluate lambda maps
// the canonical AirIQ recommendation into a blower Demand:
//
//     Demand d = demand_from_airiq_recommendation(
//         (int) sense360::airiq::global_engine().recommendation());
//
// This test compiles the exact cross-namespace pattern that lambda emits, so a
// C++ regression (a clashing enum, a namespace slip) is caught by the native
// suite rather than only by a full `esphome compile` (whose ESP toolchain
// download is not available offline). It ALSO pins the integer contract the
// mapping relies on: demand_from_airiq_recommendation() takes an int, so if the
// AirIQ Recommendation enum values ever change, these asserts fail loudly.
//
// A green run here is LOGIC/COMPILATION proof only — never hardware validation.
//
// Compile via tests/Makefile (auto-discovered):  cd tests && make test

#include <cassert>
#include <cstdint>
#include <cstdio>

#include "../../components/sense360/airiq_engine.h"
#include "../../components/sense360/blower_controller.h"

using namespace sense360::blower;

// Mirror of the blower_framework demand bridge: read the canonical AirIQ
// recommendation and map it to a blower Demand.
static Demand airiq_demand_bridge(sense360::airiq::AirIQEngine &airiq) {
  return demand_from_airiq_recommendation((int) airiq.recommendation());
}

int main() {
  printf("\n=== BLOWER-FRAMEWORK-001 header-coexistence test ===\n");

  // 1) The integer contract the mapping depends on: the AirIQ Recommendation
  //    enum values must match the constants baked into
  //    demand_from_airiq_recommendation(). This is the anti-drift pin.
  assert((int) sense360::airiq::RECOMMENDATION_INITIALISING == 0);
  assert((int) sense360::airiq::RECOMMENDATION_NO_ACTION == 1);
  assert((int) sense360::airiq::RECOMMENDATION_VENTILATE_SOON == 2);
  assert((int) sense360::airiq::RECOMMENDATION_VENTILATE_NOW == 3);
  assert((int) sense360::airiq::RECOMMENDATION_CHECK_SOURCE == 4);
  assert((int) sense360::airiq::RECOMMENDATION_UNAVAILABLE == 5);

  assert(demand_from_airiq_recommendation(
             (int) sense360::airiq::RECOMMENDATION_VENTILATE_NOW) == DEMAND_HIGH);
  assert(demand_from_airiq_recommendation(
             (int) sense360::airiq::RECOMMENDATION_VENTILATE_SOON) ==
         DEMAND_ELEVATED);
  assert(demand_from_airiq_recommendation(
             (int) sense360::airiq::RECOMMENDATION_CHECK_SOURCE) == DEMAND_NONE);
  assert(demand_from_airiq_recommendation(
             (int) sense360::airiq::RECOMMENDATION_INITIALISING) ==
         DEMAND_UNKNOWN);

  const uint32_t t = 100000;

  // 2) An unfed AirIQ engine (framework not composed / no samples) stays
  //    INITIALISING -> demand UNKNOWN -> the fan NEVER boosts (fail-safe).
  //    The base circulation duty cycle still runs — circulation is enclosure
  //    sampling, deliberately independent of AirIQ data.
  {
    sense360::airiq::AirIQEngine airiq;
    airiq.begin(t);
    airiq.evaluate(t + 1000);  // still warming up, no samples
    BlowerController fan;
    fan.set_has_airiq(true);
    fan.set_mode(MODE_AUTO);
    fan.begin(t);
    fan.input_demand(t + 1000, airiq_demand_bridge(airiq));
    fan.evaluate(t + 1000);
    assert(fan.demand() == DEMAND_UNKNOWN);
    assert(!fan.boosting());  // UNKNOWN never boosts
    assert(fan.output_on());  // ...but the normal cycle run proceeds
    assert(fan.state() == STATE_AUTO_CIRCULATING);
  }

  // 3) A real "Ventilate now" from the AirIQ engine (CO2 in the very-poor band)
  //    drives the same bridge to boost the fan to continuous circulation.
  {
    sense360::airiq::AirIQEngine airiq;
    airiq.begin(t);
    airiq.input_co2(t, 1600.0f);  // >= very-poor threshold (1500 ppm)
    airiq.evaluate(t);
    assert(airiq.recommendation() ==
           sense360::airiq::RECOMMENDATION_VENTILATE_NOW);

    BlowerController fan;
    fan.set_has_airiq(true);
    fan.set_mode(MODE_AUTO);
    fan.set_trigger(TRIGGER_NOW);
    fan.begin(t);
    fan.input_demand(t, airiq_demand_bridge(airiq));
    fan.evaluate(t);
    assert(fan.demand() == DEMAND_HIGH);
    assert(fan.output_on());
    assert(fan.boosting());
    assert(fan.state() == STATE_AUTO_BOOST);
  }

  printf("[PASS] blower_controller.h + airiq_engine.h coexist and cooperate\n");
  printf("\n1/1 tests passed\n");
  return 0;
}

#pragma once

// ============================================================================
// BLOWER-FRAMEWORK-001 — canonical Sense360 circulation-fan controller
// (header-only)
// ============================================================================
// The single implementation of the Sense360 enclosure circulation-fan
// behaviour for the Core's dedicated on-board FAN net. It is compiled BOTH
// into production firmware (via the blower framework package) and into the
// deterministic simulation tests (tests/unit/test_blower_controller.cpp) so
// the tested logic and the shipped logic can never drift.
//
// Purpose (owner decision, 2026-07-31): the J13 blower is an ENCLOSURE AIR
// CIRCULATION fan — it moves room air through the Sense360 enclosure so the
// on-board sensors sample representative air. It is NOT a room-ventilation
// output and this engine claims no room-air-change effect.
//
// Hardware contract (verified against docs/hardware/s360-100-r4-core.md and the
// owner-provided S360-100-R4 schematic — this engine encodes no more than the
// contract proves):
//   * The fan is the Core's dedicated `FAN` net: schematic `IO21` (ESP32-S3
//     GPIO21) drives Q4 (SI2302S low-side MOSFET) which switches the 5 V blower
//     on the J13 connector. J13 is a two-wire binary 5 V output.
//   * There is NO J13 tach, speed-PWM, current, airflow or physical-rotation
//     feedback of any kind. This engine therefore commands only on / off and
//     NEVER reports, infers or claims fan speed, airflow or rotation.
//   * `GPIO46` (`GP_Fan_Status_Led`) is a Core-side status indicator and is
//     NEVER treated as rotation feedback; the generic `GPIO3` relay (J4) is a
//     SEPARATE control and is never part of the fan path. This engine touches
//     neither.
//
// Customer mode surface: `Off / Auto / On`, default Auto.
//   * Off  — always command the fan output OFF.
//   * On   — always command the fan output ON (continuous circulation).
//   * Auto — periodic duty-cycle circulation (run for `circulate_on_ms`, rest
//            for `circulate_off_ms`, repeating), BOOSTED to continuous while
//            the canonical AirIQ demand is at/above the boost trigger.
// The mode is the authoritative control; the engine owns the output in every
// mode, so there is no separate toggle that can transiently contradict the
// selected mode.
//
// Auto behaviour (all windows PROVISIONAL engineering defaults pending bench
// validation):
//   * Entering Auto starts a circulation run immediately, then the duty cycle
//     repeats: on for `circulate_on_ms`, off for `circulate_off_ms`.
//   * BOOST: while the AirIQ demand contract is composed AND reports a demand
//     at/above the boost trigger, the fan runs continuously so sampling stays
//     fresh while air quality is changing. When the boost ends the cycle
//     resumes with a full rest period (the fan has just been running).
//   * FAIL-SAFE: an UNKNOWN demand (AirIQ initialising / unavailable / not
//     composed) NEVER boosts the fan. The base duty cycle is deliberately
//     independent of AirIQ — circulation is an enclosure-sampling function,
//     not a response to air quality — so it runs with or without AirIQ.
//
// Honesty rules baked into this engine:
//   * The FAN net is a one-way binary drive: firmware commands ON/OFF but can
//     never verify the fan physically spun (no J13 feedback exists). This
//     engine reports only what it COMMANDED, never a measured fan state, and
//     makes NO airflow / rotation / current / RPM claim.
//   * All timing values are PROVISIONAL engineering defaults pending bench
//     validation (docs/hardware/blower-framework-bench-checklist.md). They are
//     never electrical-safety, thermal or compliance claims.
//
// Nothing in this header claims hardware validation.
// ============================================================================

#include <cstdint>
#include <cstring>

namespace sense360 {
namespace blower {

// Customer mode (select vocabulary; strings single-sourced). Default Auto.
enum Mode {
  MODE_OFF = 0,
  MODE_AUTO = 1,
  MODE_ON = 2,
};

inline const char *mode_to_string(Mode mode) {
  switch (mode) {
    case MODE_OFF:
      return "Off";
    case MODE_AUTO:
      return "Auto";
    case MODE_ON:
      return "On";
  }
  return "Auto";
}

// Unknown / unspecified selections resolve to the default Auto.
inline Mode mode_from_string(const char *s) {
  if (s != nullptr && std::strcmp(s, "Off") == 0) return MODE_OFF;
  if (s != nullptr && std::strcmp(s, "On") == 0) return MODE_ON;
  return MODE_AUTO;
}

// Canonical air-quality demand, derived from the AirIQ recommendation
// contract. UNKNOWN is a first-class state (missing / initialising /
// AirIQ absent) distinct from NONE — it never boosts the fan.
enum Demand {
  DEMAND_UNKNOWN = 0,
  DEMAND_NONE = 1,      // no ventilation action needed
  DEMAND_ELEVATED = 2,  // ventilate soon
  DEMAND_HIGH = 3,      // ventilate now
};

inline const char *demand_to_string(Demand demand) {
  switch (demand) {
    case DEMAND_UNKNOWN:
      return "Unknown";
    case DEMAND_NONE:
      return "None";
    case DEMAND_ELEVATED:
      return "Ventilate soon";
    case DEMAND_HIGH:
      return "Ventilate now";
  }
  return "Unknown";
}

// Map the canonical AirIQ recommendation (the integer value of
// sense360::airiq::Recommendation) to a Demand. Taken as an int so this header
// stays self-contained (standard library only, no cross-include); the
// framework passes (int) sense360::airiq::global_engine().recommendation().
// This is the fan's SINGLE interpretation of the AirIQ demand contract and is
// pinned against the AirIQ enum by tests/unit/test_blower_airiq_coexist.cpp.
//
// sense360::airiq::Recommendation values (AIRIQ-FRAMEWORK-001):
//   0 INITIALISING, 1 NO_ACTION, 2 VENTILATE_SOON, 3 VENTILATE_NOW,
//   4 CHECK_SOURCE, 5 UNAVAILABLE.
// "Check pollution source" is deliberately NOT a boost demand: outdoor air
// quality is unknown, so the AirIQ contract does not recommend ventilation
// for it, and the fan does not boost for it either.
inline Demand demand_from_airiq_recommendation(int recommendation) {
  switch (recommendation) {
    case 2:  // VENTILATE_SOON
      return DEMAND_ELEVATED;
    case 3:  // VENTILATE_NOW
      return DEMAND_HIGH;
    case 1:  // NO_ACTION
    case 4:  // CHECK_SOURCE (ventilation is not the recommended action)
      return DEMAND_NONE;
    case 0:  // INITIALISING
    case 5:  // UNAVAILABLE
    default:
      return DEMAND_UNKNOWN;
  }
}

// Boost threshold (customer select): at what AirIQ demand level Auto switches
// from the duty cycle to continuous circulation.
enum Trigger {
  TRIGGER_NOW = 0,   // only "Ventilate now" boosts (conservative default)
  TRIGGER_SOON = 1,  // "Ventilate soon" or higher boosts
};

inline const char *trigger_to_string(Trigger trigger) {
  switch (trigger) {
    case TRIGGER_NOW:
      return "Ventilate now";
    case TRIGGER_SOON:
      return "Ventilate soon";
  }
  return "Ventilate now";
}

inline Trigger trigger_from_string(const char *s) {
  if (s != nullptr && std::strcmp(s, "Ventilate soon") == 0) return TRIGGER_SOON;
  return TRIGGER_NOW;
}

// What the circulation-fan control is doing (diagnostics; single-sourced
// vocabulary and honest human-readable status strings).
enum State {
  STATE_OFF = 0,               // Off mode — fan commanded off
  STATE_ON = 1,                // On mode — fan commanded on
  STATE_AUTO_CIRCULATING = 2,  // Auto, duty-cycle run phase — fan on
  STATE_AUTO_RESTING = 3,      // Auto, duty-cycle rest phase — fan off
  STATE_AUTO_BOOST = 4,        // Auto, continuous — air-quality boost active
};

inline const char *state_to_string(State state) {
  switch (state) {
    case STATE_OFF:
      return "Off — fan commanded off";
    case STATE_ON:
      return "On — fan commanded on";
    case STATE_AUTO_CIRCULATING:
      return "Auto: circulating — fan running";
    case STATE_AUTO_RESTING:
      return "Auto: resting between circulation runs — fan off";
    case STATE_AUTO_BOOST:
      return "Auto: boosted — air-quality demand active";
  }
  return "Off — fan commanded off";
}

class BlowerController {
 public:
  // --- composition capability (compile-time fact; substitution-driven) -------
  // Is the canonical AirIQ demand contract composed on this device? Without it
  // there is never an air-quality boost; the base duty cycle is unaffected.
  void set_has_airiq(bool has) { has_airiq_ = has; }
  bool has_airiq() const { return has_airiq_; }

  // --- customer controls (runtime) -------------------------------------------
  void set_mode(Mode mode) { mode_ = mode; }
  Mode mode() const { return mode_; }

  void set_trigger(Trigger trigger) { trigger_ = trigger; }
  Trigger trigger() const { return trigger_; }

  // --- timing windows (provisional engineering defaults, ms) -----------------
  void set_circulate_on_ms(uint32_t ms) { circulate_on_ms_ = ms; }
  void set_circulate_off_ms(uint32_t ms) { circulate_off_ms_ = ms; }

  // --- lifecycle -------------------------------------------------------------
  void begin(uint32_t now_ms) {
    started_ = true;
    start_ms_ = now_ms;
  }

  // --- inputs ----------------------------------------------------------------
  // The canonical AirIQ demand. UNKNOWN never boosts the fan.
  void input_demand(uint32_t now_ms, Demand demand) {
    ensure_started(now_ms);
    demand_ = demand;
  }

  // --- evaluation ------------------------------------------------------------
  void evaluate(uint32_t now_ms) {
    ensure_started(now_ms);

    // Forced modes own the output directly and bypass the Auto cycle.
    if (mode_ == MODE_OFF) {
      set_output(false);
      boosting_ = false;
      auto_entered_ = false;
      state_ = STATE_OFF;
      return;
    }
    if (mode_ == MODE_ON) {
      set_output(true);
      boosting_ = false;
      auto_entered_ = false;
      state_ = STATE_ON;
      return;
    }

    // --- MODE_AUTO ---
    // Entering Auto (from boot restore or a mode change) starts a circulation
    // run immediately — a commanded run, independent of any sensor input.
    if (!auto_entered_) {
      auto_entered_ = true;
      boosting_ = false;
      phase_since_ = now_ms;
      set_output(true);
    }

    // Air-quality boost: only a REAL demand at/above the trigger boosts.
    // UNKNOWN (AirIQ initialising / unavailable / not composed) never does.
    bool boost = false;
    if (has_airiq_) {
      if (demand_ == DEMAND_HIGH) {
        boost = true;
      } else if (demand_ == DEMAND_ELEVATED && trigger_ == TRIGGER_SOON) {
        boost = true;
      }
    }

    if (boost) {
      boosting_ = true;
      set_output(true);
      state_ = STATE_AUTO_BOOST;
      return;
    }

    if (boosting_) {
      // Boost just ended: the fan has been running, so resume the cycle with
      // a full rest period.
      boosting_ = false;
      set_output(false);
      phase_since_ = now_ms;
      state_ = STATE_AUTO_RESTING;
      return;
    }

    // Base duty cycle: run circulate_on_ms, rest circulate_off_ms, repeat.
    if (out_on_) {
      if (elapsed(phase_since_, now_ms) >= circulate_on_ms_) {
        set_output(false);
        phase_since_ = now_ms;
        state_ = STATE_AUTO_RESTING;
      } else {
        state_ = STATE_AUTO_CIRCULATING;
      }
    } else {
      if (elapsed(phase_since_, now_ms) >= circulate_off_ms_) {
        set_output(true);
        phase_since_ = now_ms;
        state_ = STATE_AUTO_CIRCULATING;
      } else {
        state_ = STATE_AUTO_RESTING;
      }
    }
  }

  // --- outputs ---------------------------------------------------------------
  // The commanded fan state. The framework applies this to the FAN-net GPIO
  // and publishes it as the read-only "Circulation Fan" state in every mode.
  bool output_on() const { return out_on_; }
  bool boosting() const { return boosting_; }

  Demand demand() const { return demand_; }
  State state() const { return state_; }
  const char *status_string() const { return state_to_string(state_); }

 private:
  static uint32_t elapsed(uint32_t since_ms, uint32_t now_ms) {
    return now_ms - since_ms;  // unsigned arithmetic handles wrap-around
  }

  void ensure_started(uint32_t now_ms) {
    if (!started_) begin(now_ms);
  }

  void set_output(bool on) { out_on_ = on; }

  // customer controls
  Mode mode_ = MODE_AUTO;
  Trigger trigger_ = TRIGGER_NOW;

  // composition capability
  bool has_airiq_ = false;

  // timing windows (provisional engineering defaults, ms): run 1 minute,
  // rest 4 minutes (a 20% duty cycle).
  uint32_t circulate_on_ms_ = 60000;
  uint32_t circulate_off_ms_ = 240000;

  // lifecycle
  bool started_ = false;
  uint32_t start_ms_ = 0;

  // input
  Demand demand_ = DEMAND_UNKNOWN;

  // committed output + cycle bookkeeping
  bool out_on_ = false;
  bool boosting_ = false;      // Auto: air-quality boost active
  bool auto_entered_ = false;  // has the Auto cycle been (re)seeded?
  uint32_t phase_since_ = 0;   // start of the current duty-cycle phase

  // output
  State state_ = STATE_OFF;
};

// Accessor for the firmware's single controller instance. ESPHome emits
// `esphome: includes:` headers AFTER the globals storage declarations in the
// generated main.cpp, so a custom-class `globals:` entry cannot name this type;
// production lambdas share this function-local static instead (constructed on
// first use). Tests instantiate their own BlowerController objects directly.
inline BlowerController &global_controller() {
  static BlowerController controller;
  return controller;
}

}  // namespace blower
}  // namespace sense360

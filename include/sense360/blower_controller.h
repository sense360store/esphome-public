#pragma once

// ============================================================================
// BLOWER-FRAMEWORK-001 — canonical Sense360 blower controller (header-only)
// ============================================================================
// The single implementation of the Sense360 blower behaviour for the Core's
// dedicated on-board FAN net. It is compiled BOTH into production firmware
// (via `esphome: includes:` in packages/features/blower_framework.yaml) and
// into the deterministic simulation tests (tests/unit/test_blower_controller.cpp)
// so the tested logic and the shipped logic can never drift.
//
// Hardware contract (verified against docs/hardware/s360-100-r4-core.md and the
// owner-provided S360-100-R4 schematic — this engine encodes no more than the
// contract proves):
//   * The blower is the Core's dedicated `FAN` net: schematic `IO21` (ESP32-S3
//     GPIO21) drives Q4 (SI2302S low-side MOSFET) which switches the 5 V blower
//     on the J13 connector. J13 is a two-wire binary 5 V blower output.
//   * There is NO J13 tach, speed-PWM, current, airflow or physical-rotation
//     feedback of any kind. This engine therefore commands only on / off and
//     NEVER reports, infers or claims blower speed, airflow or rotation.
//   * `GPIO46` (`GP_Fan_Status_Led`) is a Core-side status indicator and is
//     NEVER treated as rotation feedback; the generic `GPIO3` relay (J4) is a
//     SEPARATE control and is never part of the blower path. This engine
//     touches neither.
//
// Customer mode surface (owner decision): `Off / Auto / On`, default Auto.
//   * Off  — always command the blower output OFF.
//   * On   — always command the blower output ON.
//   * Auto — follow the canonical AirIQ ventilation demand through the timing
//            state machine (min-on, post-demand purge, min-off restart lockout).
// The mode is the authoritative control; the engine owns the output in every
// mode, so there is no separate toggle that can transiently contradict the
// selected mode.
//
// Auto timing state machine (all windows PROVISIONAL engineering defaults
// pending bench validation):
//   * A ventilation demand at/above the trigger starts the blower (subject to
//     the min-off restart lockout, which never delays the first start of an
//     Auto session).
//   * When a valid demand clears (or goes stale/unavailable) while running, the
//     blower does NOT stop immediately: it completes its minimum run time AND a
//     post-demand PURGE period, then stops.
//   * After stopping it enforces a minimum off time before it may restart.
//   * FAIL-SAFE: an UNKNOWN demand (AirIQ initialising / unavailable / not
//     composed) NEVER starts a stopped blower. A blower already running from a
//     previously valid demand completes min-on + purge and then stops — it
//     never runs forever on stale data.
//
// Honesty rules baked into this engine:
//   * The FAN net is a one-way binary drive: firmware commands ON/OFF but can
//     never verify the blower physically spun (no J13 feedback exists). This
//     engine reports only what it COMMANDED, never a measured blower state, and
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

// Canonical ventilation demand, derived from the AirIQ recommendation
// contract. UNKNOWN is a first-class state (missing / initialising /
// AirIQ absent) distinct from NONE — it never starts the blower.
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
// sense360::airiq::Recommendation) to a ventilation Demand. Taken as an int so
// this header stays self-contained (standard library only, no cross-include);
// the framework passes (int) sense360::airiq::global_engine().recommendation().
// This is the blower's SINGLE interpretation of the AirIQ demand contract and
// is pinned against the AirIQ enum by tests/unit/test_blower_airiq_coexist.cpp.
//
// sense360::airiq::Recommendation values (AIRIQ-FRAMEWORK-001):
//   0 INITIALISING, 1 NO_ACTION, 2 VENTILATE_SOON, 3 VENTILATE_NOW,
//   4 CHECK_SOURCE, 5 UNAVAILABLE.
// "Check pollution source" is deliberately NOT a ventilation demand: outdoor
// air quality is unknown, so the AirIQ contract does not recommend ventilation
// for it, and neither does the blower.
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

// Auto activation threshold (customer select): at what demand level does Auto
// start the blower.
enum Trigger {
  TRIGGER_NOW = 0,   // only "Ventilate now" starts the blower (conservative default)
  TRIGGER_SOON = 1,  // "Ventilate soon" or higher starts the blower
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

// What the blower control is doing (diagnostics; single-sourced vocabulary and
// honest human-readable status strings).
enum State {
  STATE_OFF = 0,               // Off mode — blower commanded off
  STATE_ON = 1,                // On mode — blower commanded on
  STATE_AUTO_NO_AIRIQ = 2,     // Auto, but AirIQ is not composed — blower off
  STATE_AUTO_OFF_OK = 3,       // Auto, off, air quality OK (demand None)
  STATE_AUTO_OFF_UNKNOWN = 4,  // Auto, off, demand unavailable (fail-safe)
  STATE_AUTO_MIN_OFF = 5,      // Auto, off, restart inhibited by min-off
  STATE_AUTO_VENTILATING = 6,  // Auto, on, active ventilation demand
  STATE_AUTO_PURGE = 7,        // Auto, on, purging after demand cleared/stale
};

inline const char *state_to_string(State state) {
  switch (state) {
    case STATE_OFF:
      return "Off — blower commanded off";
    case STATE_ON:
      return "On — blower commanded on";
    case STATE_AUTO_NO_AIRIQ:
      return "Auto: AirIQ not composed — blower off";
    case STATE_AUTO_OFF_OK:
      return "Auto: air quality OK — blower off";
    case STATE_AUTO_OFF_UNKNOWN:
      return "Auto: air-quality demand unavailable — blower off";
    case STATE_AUTO_MIN_OFF:
      return "Auto: minimum off time — blower held off";
    case STATE_AUTO_VENTILATING:
      return "Auto: ventilating (air-quality demand)";
    case STATE_AUTO_PURGE:
      return "Auto: purging after demand cleared — blower running";
  }
  return "Off — blower commanded off";
}

class BlowerController {
 public:
  // --- composition capability (compile-time fact; substitution-driven) -------
  // Is the canonical AirIQ demand contract composed on this device? Without it
  // Auto never has a real ventilation demand, so the blower stays off
  // (fail-safe) and the status names the missing input.
  void set_has_airiq(bool has) { has_airiq_ = has; }
  bool has_airiq() const { return has_airiq_; }

  // --- customer controls (runtime) -------------------------------------------
  void set_mode(Mode mode) { mode_ = mode; }
  Mode mode() const { return mode_; }

  void set_trigger(Trigger trigger) { trigger_ = trigger; }
  Trigger trigger() const { return trigger_; }

  // --- timing windows (provisional engineering defaults, ms) -----------------
  void set_min_on_ms(uint32_t ms) { min_on_ms_ = ms; }
  void set_min_off_ms(uint32_t ms) { min_off_ms_ = ms; }
  void set_purge_ms(uint32_t ms) { purge_ms_ = ms; }

  // --- lifecycle -------------------------------------------------------------
  void begin(uint32_t now_ms) {
    started_ = true;
    start_ms_ = now_ms;
    off_since_ = now_ms;
  }

  // --- inputs ----------------------------------------------------------------
  // The canonical AirIQ ventilation demand. UNKNOWN never starts the blower.
  void input_demand(uint32_t now_ms, Demand demand) {
    ensure_started(now_ms);
    demand_ = demand;
  }

  // --- evaluation ------------------------------------------------------------
  void evaluate(uint32_t now_ms) {
    ensure_started(now_ms);

    // Forced modes own the output directly and bypass the Auto timing machine.
    if (mode_ == MODE_OFF) {
      set_output(false, now_ms);
      purging_ = false;
      state_ = STATE_OFF;
      prev_mode_ = mode_;
      return;
    }
    if (mode_ == MODE_ON) {
      set_output(true, now_ms);
      purging_ = false;
      state_ = STATE_ON;
      prev_mode_ = mode_;
      return;
    }

    // --- MODE_AUTO ---
    // On entry into Auto, seed the cycle bookkeeping from the current output:
    // a blower already on (e.g. from On mode) has "run" (so min-off applies to a
    // later restart); a blower off starts a fresh session (first start is not
    // delayed by min-off).
    if (mode_ != prev_mode_) {
      ever_on_ = out_on_;
      purging_ = false;
    }
    prev_mode_ = mode_;

    // A real, actionable ventilation demand (UNKNOWN is never actionable, and
    // without AirIQ composed there is never an actionable demand).
    bool active = false;
    if (has_airiq_) {
      if (demand_ == DEMAND_HIGH) {
        active = true;
      } else if (demand_ == DEMAND_ELEVATED && trigger_ == TRIGGER_SOON) {
        active = true;
      }
    }

    if (out_on_) {
      if (active) {
        // Active demand: keep ventilating.
        purging_ = false;
        state_ = STATE_AUTO_VENTILATING;
      } else {
        // Demand cleared or went stale/unavailable while running: purge.
        if (!purging_) {
          purging_ = true;
          purge_since_ = now_ms;
        }
        const bool min_on_done = elapsed(on_since_, now_ms) >= min_on_ms_;
        const bool purge_done = elapsed(purge_since_, now_ms) >= purge_ms_;
        if (min_on_done && purge_done) {
          set_output(false, now_ms);  // stop; off-state resolved below
          purging_ = false;
        } else {
          state_ = STATE_AUTO_PURGE;
        }
      }
    }

    if (!out_on_) {
      if (active) {
        // Start only after the min-off restart lockout (which never delays the
        // first start of an Auto session, tracked by ever_on_).
        const bool min_off_done =
            !ever_on_ || elapsed(off_since_, now_ms) >= min_off_ms_;
        if (min_off_done) {
          set_output(true, now_ms);
          purging_ = false;
          state_ = STATE_AUTO_VENTILATING;
        } else {
          state_ = STATE_AUTO_MIN_OFF;
        }
      } else {
        // Off with no actionable demand.
        if (!has_airiq_) {
          state_ = STATE_AUTO_NO_AIRIQ;
        } else if (demand_ == DEMAND_UNKNOWN) {
          state_ = STATE_AUTO_OFF_UNKNOWN;
        } else {
          state_ = STATE_AUTO_OFF_OK;
        }
      }
    }
  }

  // --- outputs ---------------------------------------------------------------
  // The commanded blower state. The framework applies this to the FAN-net GPIO
  // and publishes it as the read-only "Blower" state in every mode.
  bool output_on() const { return out_on_; }
  bool purging() const { return purging_; }

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

  // Commit an output state, stamping the on/off transition time (used by the
  // min-on / min-off / purge windows). A no-op when the state is unchanged.
  void set_output(bool on, uint32_t now_ms) {
    if (on == out_on_) return;
    out_on_ = on;
    if (on) {
      on_since_ = now_ms;
      ever_on_ = true;
    } else {
      off_since_ = now_ms;
    }
  }

  // customer controls
  Mode mode_ = MODE_AUTO;
  Trigger trigger_ = TRIGGER_NOW;

  // composition capability
  bool has_airiq_ = false;

  // timing windows (provisional engineering defaults, ms)
  uint32_t min_on_ms_ = 60000;
  uint32_t min_off_ms_ = 60000;
  uint32_t purge_ms_ = 120000;

  // lifecycle
  bool started_ = false;
  uint32_t start_ms_ = 0;

  // input
  Demand demand_ = DEMAND_UNKNOWN;

  // committed output + timers
  bool out_on_ = false;
  bool ever_on_ = false;  // has the blower run? (gates the min-off restart lockout)
  bool purging_ = false;  // Auto: running out the post-demand purge
  uint32_t on_since_ = 0;
  uint32_t off_since_ = 0;
  uint32_t purge_since_ = 0;

  // mode-transition detection
  Mode prev_mode_ = MODE_AUTO;

  // output
  State state_ = STATE_AUTO_OFF_UNKNOWN;
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

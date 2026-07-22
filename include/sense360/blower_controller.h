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
// owner-provided S360-100-R4 schematic — this engine encodes NO more than the
// contract proves):
//   * The blower is the Core's dedicated `FAN` net: schematic `IO21` (ESP32-S3
//     GPIO21) drives Q4 (SI2302S low-side MOSFET) which switches the 5 V blower
//     on the J13 connector. J13 is a two-wire binary 5 V blower output.
//   * There is NO J13 tach, speed-PWM, current, airflow or physical-rotation
//     feedback of any kind. This engine therefore commands only ON / OFF and
//     NEVER reports, infers or claims blower speed, airflow or rotation.
//   * `GPIO46` (`GP_Fan_Status_Led`) is a Core-side status indicator and is
//     NEVER treated as rotation feedback; the generic `GPIO3` relay (J4) is a
//     SEPARATE control and is never part of the blower path. This engine
//     touches neither.
//
// What it owns (the platform's single source of blower-command truth):
//   * Mode arbitration — Manual (the customer owns the blower) vs Auto
//     (ventilation-driven). Auto is honestly downgraded to Manual when its
//     required input (the canonical AirIQ demand contract) is not composed;
//     the engine, not the YAML, is the single source of that fallback.
//   * Demand mapping — the ONE interpretation of the canonical AirIQ
//     recommendation contract (AIRIQ-FRAMEWORK-001,
//     sense360::airiq::Recommendation) as a ventilation Demand. Pollutant
//     thresholds are NOT duplicated here — the AirIQ engine owns pollutant
//     truth; this engine consumes its published demand only.
//   * Fail-safe — an UNKNOWN demand (AirIQ initialising / unavailable / not
//     composed) NEVER starts the blower. Missing air-quality data is never a
//     reason to ventilate.
//   * Anti-short-cycle — minimum on-time and minimum off-time dwell windows so
//     a demand hovering at the trigger cannot chatter the blower motor. These
//     are PROVISIONAL engineering defaults pending bench validation.
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

// Blower operating mode (customer select vocabulary; strings single-sourced).
enum Mode {
  MODE_MANUAL = 0,
  MODE_AUTO = 1,
};

inline const char *mode_to_string(Mode mode) {
  switch (mode) {
    case MODE_MANUAL:
      return "Manual";
    case MODE_AUTO:
      return "Auto";
  }
  return "Manual";
}

inline Mode mode_from_string(const char *s) {
  if (s != nullptr && std::strcmp(s, "Auto") == 0) return MODE_AUTO;
  return MODE_MANUAL;
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
  STATE_MANUAL = 0,            // Manual mode — the customer owns the blower
  STATE_AUTO_OFF = 1,          // Auto — demand below trigger, blower off
  STATE_AUTO_ON = 2,           // Auto — demand at/above trigger, blower on
  STATE_AUTO_MIN_ON = 3,       // Auto — demand cleared but min-on-time holding blower on
  STATE_AUTO_MIN_OFF = 4,      // Auto — demand present but min-off-time holding blower off
  STATE_AUTO_UNKNOWN = 5,      // Auto — demand unavailable, blower off (fail-safe)
  STATE_AUTO_UNSUPPORTED = 6,  // Auto selected but AirIQ not composed — using Manual
};

inline const char *state_to_string(State state) {
  switch (state) {
    case STATE_MANUAL:
      return "Manual — blower controlled directly";
    case STATE_AUTO_OFF:
      return "Auto: air quality OK — blower off";
    case STATE_AUTO_ON:
      return "Auto: ventilating (air-quality demand)";
    case STATE_AUTO_MIN_ON:
      return "Auto: minimum run time — blower held on";
    case STATE_AUTO_MIN_OFF:
      return "Auto: minimum off time — blower held off";
    case STATE_AUTO_UNKNOWN:
      return "Auto: air-quality demand unavailable — blower off";
    case STATE_AUTO_UNSUPPORTED:
      return "Auto needs AirIQ (not composed) — using Manual";
  }
  return "Manual — blower controlled directly";
}

class BlowerController {
 public:
  // --- composition capability (compile-time fact; substitution-driven) -------
  // Is the canonical AirIQ demand contract composed on this device? Without it
  // the Auto behaviour is honestly downgraded to Manual (the engine is the
  // single source of that fallback), never inventing a demand.
  void set_has_airiq(bool has) { has_airiq_ = has; }
  bool has_airiq() const { return has_airiq_; }

  // --- customer controls (runtime) -------------------------------------------
  void set_mode(Mode mode) { mode_ = mode; }
  Mode mode() const { return mode_; }

  void set_trigger(Trigger trigger) { trigger_ = trigger; }
  Trigger trigger() const { return trigger_; }

  // --- anti-short-cycle windows (provisional engineering defaults) -----------
  void set_min_on_ms(uint32_t ms) { min_on_ms_ = ms; }
  void set_min_off_ms(uint32_t ms) { min_off_ms_ = ms; }

  // --- lifecycle -------------------------------------------------------------
  void begin(uint32_t now_ms) {
    started_ = true;
    start_ms_ = now_ms;
    last_change_ms_ = now_ms;
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

    // Effective mode: Auto requires the AirIQ demand contract; otherwise the
    // engine honestly downgrades to Manual and does NOT own the output.
    const bool auto_supported = (mode_ == MODE_AUTO && has_airiq_);
    if (!auto_supported) {
      auto_owns_ = false;
      output_on_ = false;
      state_ = (mode_ == MODE_AUTO && !has_airiq_) ? STATE_AUTO_UNSUPPORTED
                                                   : STATE_MANUAL;
      // Reset commit tracking so a later Auto engagement starts fresh.
      committed_valid_ = false;
      return;
    }

    auto_owns_ = true;

    // Raw desired state from demand vs trigger. UNKNOWN never turns on.
    bool want_on;
    if (demand_ == DEMAND_UNKNOWN) {
      want_on = false;
    } else if (trigger_ == TRIGGER_SOON) {
      want_on = (demand_ == DEMAND_ELEVATED || demand_ == DEMAND_HIGH);
    } else {  // TRIGGER_NOW
      want_on = (demand_ == DEMAND_HIGH);
    }

    // Initialise committed state on the first Auto evaluation.
    if (!committed_valid_) {
      committed_on_ = want_on;
      committed_valid_ = true;
      last_change_ms_ = now_ms;
    }

    // Anti-short-cycle: a transition is blocked until the minimum dwell in the
    // current state has elapsed (protects the blower motor; avoids chatter when
    // the air-quality demand hovers at the trigger). The min-off dwell only
    // gates a RESTART — it never delays the first-ever start, because there is
    // no prior run to short-cycle against at boot.
    bool blocked = false;
    if (want_on != committed_on_) {
      const uint32_t held = elapsed(last_change_ms_, now_ms);
      if (committed_on_ && held < min_on_ms_) {
        blocked = true;  // ON, want OFF, min-on not elapsed -> hold ON
      } else if (!committed_on_ && ever_on_ && held < min_off_ms_) {
        blocked = true;  // OFF (after a real run), want ON, min-off not elapsed
      }
      if (!blocked) {
        committed_on_ = want_on;
        last_change_ms_ = now_ms;
      }
    }

    if (committed_on_) ever_on_ = true;
    output_on_ = committed_on_;

    // Deterministic diagnostic classification.
    if (blocked) {
      state_ = committed_on_ ? STATE_AUTO_MIN_ON : STATE_AUTO_MIN_OFF;
    } else if (demand_ == DEMAND_UNKNOWN) {
      state_ = STATE_AUTO_UNKNOWN;
    } else if (output_on_) {
      state_ = STATE_AUTO_ON;
    } else {
      state_ = STATE_AUTO_OFF;
    }
  }

  // --- outputs ---------------------------------------------------------------
  // True when Auto actively owns the blower output; the framework applies
  // output_on() ONLY then. In Manual (or Auto downgraded to Manual) the
  // customer's Blower control is authoritative and is never overridden.
  bool auto_owns() const { return auto_owns_; }
  bool output_on() const { return output_on_; }

  Mode effective_mode() const {
    return (mode_ == MODE_AUTO && has_airiq_) ? MODE_AUTO : MODE_MANUAL;
  }
  bool auto_unsupported() const { return mode_ == MODE_AUTO && !has_airiq_; }

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

  // customer controls
  Mode mode_ = MODE_MANUAL;
  Trigger trigger_ = TRIGGER_NOW;

  // composition capability
  bool has_airiq_ = false;

  // anti-short-cycle windows (provisional engineering defaults, ms)
  uint32_t min_on_ms_ = 60000;
  uint32_t min_off_ms_ = 60000;

  // lifecycle
  bool started_ = false;
  uint32_t start_ms_ = 0;

  // input
  Demand demand_ = DEMAND_UNKNOWN;

  // committed output state + dwell tracking
  bool committed_on_ = false;
  bool committed_valid_ = false;
  bool ever_on_ = false;  // has the blower actually run? (gates the min-off restart dwell)
  uint32_t last_change_ms_ = 0;

  // outputs
  bool auto_owns_ = false;
  bool output_on_ = false;
  State state_ = STATE_MANUAL;
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

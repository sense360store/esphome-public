#pragma once

// ============================================================================
// LED-FRAMEWORK-001 — customer LED controller engine (header-only)
// ============================================================================
// The single implementation of the Sense360 LED customer-experience state
// machine for the S360-300 WS2812B halo ring. It is compiled BOTH into
// production firmware (via `esphome: includes:` in
// packages/features/led_framework.yaml) and into the deterministic
// simulation tests (tests/unit/test_led_controller.cpp) so the tested logic
// and the shipped logic can never drift.
//
// What it arbitrates (accepted customer decisions LED-01..LED-12):
//   * Room Light   — the customer's normal light state (stored, restored).
//   * Night Mode   — a low, warm profile that never overwrites the
//                    customer's previous state; Manual / When dark /
//                    When dark and occupied behaviours.
//   * Identify     — a short, recognisable, non-disruptive pulse that
//                    restores the previous state automatically.
//   * Status       — brief, discreet indications from REAL signals only
//                    (startup, API connect/disconnect, WiFi events),
//                    subordinate to the Room Light.
//   * Fault        — persistent indication reserved for an explicit fault
//                    signal; no producer exists today (engine contract only).
//
// Priority (LED-07, high to low):
//   Fault > Identify > Night Mode > Room Light > transient Status.
//
// State-ownership rules baked into this engine:
//   * Customer/manual intent always wins: a manual light change cancels
//     overlays and disengages Night Mode; a manual Night Mode off
//     suppresses re-activation until the trigger condition resets.
//   * Automation reverses ONLY its own activations (night_automation_owned).
//   * Stale or missing lux data is UNKNOWN — never interpreted as dark;
//     invalid occupancy freezes the automation (no flapping, no toggles).
//   * A transient overlay restores the exact prior state; an error never
//     destroys the customer's chosen colour or brightness.
//   * Every output is clamped to the software maximum brightness. The cap
//     is PROVISIONAL and software-defined: no verified electrical/thermal
//     ceiling exists for the S360-300 anywhere in this repository, so no
//     brightness value is claimed physically safe.
//
// All colour/brightness/timing values are provisional engineering defaults
// pending bench validation (docs/hardware/led-framework-bench-checklist.md).
// Nothing in this header claims hardware validation.
// ============================================================================

#include <cmath>
#include <cstdint>
#include <cstring>

namespace sense360 {
namespace ledfw {

// Output-arbitration layers, highest priority first (LED-07). The strings
// are the exact diagnostic wording ("LED Active Layer" entity).
enum Layer {
  LAYER_FAULT = 0,
  LAYER_IDENTIFY = 1,
  LAYER_NIGHT = 2,
  LAYER_CUSTOMER = 3,
  LAYER_STATUS = 4,
};

inline const char *layer_to_string(Layer layer) {
  switch (layer) {
    case LAYER_FAULT:
      return "Fault";
    case LAYER_IDENTIFY:
      return "Identify";
    case LAYER_NIGHT:
      return "Night Mode";
    case LAYER_CUSTOMER:
      return "Room Light";
    case LAYER_STATUS:
      return "Status";
  }
  return "Room Light";
}

// Night Mode Behaviour options (LED-03). "Scheduled" is deliberately
// deferred: only SNTP (internet) and Home Assistant time sources exist in
// the base packages — neither is a reliable local-first scheduler.
enum NightBehaviour {
  NIGHT_MANUAL = 0,
  NIGHT_WHEN_DARK = 1,
  NIGHT_WHEN_DARK_AND_OCCUPIED = 2,
};

inline NightBehaviour night_behaviour_from_string(const char *value) {
  if (value != nullptr) {
    if (std::strcmp(value, "When dark") == 0) return NIGHT_WHEN_DARK;
    if (std::strcmp(value, "When dark and occupied") == 0)
      return NIGHT_WHEN_DARK_AND_OCCUPIED;
  }
  return NIGHT_MANUAL;  // safe default: no automation
}

// Status Indicator levels (LED-06).
enum StatusLevel {
  STATUS_LEVEL_OFF = 0,
  STATUS_LEVEL_ESSENTIAL = 1,
  STATUS_LEVEL_DETAILED = 2,
};

inline StatusLevel status_level_from_string(const char *value) {
  if (value != nullptr) {
    if (std::strcmp(value, "Off") == 0) return STATUS_LEVEL_OFF;
    if (std::strcmp(value, "Detailed") == 0) return STATUS_LEVEL_DETAILED;
  }
  return STATUS_LEVEL_ESSENTIAL;
}

// Status events. Every event maps to a REAL supported firmware signal
// (LED-06: no claimed status without a real signal):
//   EVENT_STARTUP        — boot completed (on_boot).
//   EVENT_CONNECTED      — Home Assistant API client connected.
//   EVENT_WARNING        — recoverable warning (API client disconnected).
//   EVENT_DETAIL_INFO    — network-level info (WiFi connected); Detailed only.
//   EVENT_DETAIL_WARNING — network-level warning (WiFi lost); Detailed only.
enum StatusEvent {
  EVENT_STARTUP = 0,
  EVENT_CONNECTED = 1,
  EVENT_WARNING = 2,
  EVENT_DETAIL_INFO = 3,
  EVENT_DETAIL_WARNING = 4,
};

inline const char *event_to_string(StatusEvent event) {
  switch (event) {
    case EVENT_STARTUP:
      return "Startup";
    case EVENT_CONNECTED:
      return "Connected";
    case EVENT_WARNING:
      return "Warning";
    case EVENT_DETAIL_INFO:
      return "Network info";
    case EVENT_DETAIL_WARNING:
      return "Network warning";
  }
  return "Warning";
}

// Darkness decision (LED-05). Computed by the canonical RoomIQ
// environmental engine (include/sense360/roomiq_engine.h — the single
// lux-threshold implementation, ROOMIQ-FRAMEWORK-001) and injected here via
// input_darkness(). UNKNOWN (missing/stale/NaN lux) is a first-class state
// distinct from darkness — it never activates anything.
enum Darkness {
  DARKNESS_UNKNOWN = 0,
  DARKNESS_DARK = 1,
  DARKNESS_NOT_DARK = 2,
};

inline const char *darkness_to_string(Darkness darkness) {
  switch (darkness) {
    case DARKNESS_UNKNOWN:
      return "Unknown";
    case DARKNESS_DARK:
      return "Dark";
    case DARKNESS_NOT_DARK:
      return "Not dark";
  }
  return "Unknown";
}

// A light target: on/off, master brightness (0..1), RGB (0..1 each; the
// WS2812B ring is RGB only — no white/CCT channel exists) and the approved
// customer effect (0 = none, 1 = Gentle Pulse, 2 = Night Glow).
struct LightState {
  bool on = false;
  float brightness = 0.5f;
  float red = 1.0f;
  float green = 1.0f;
  float blue = 1.0f;
  uint8_t effect = 0;
};

class LedController {
 public:
  // --- configuration --------------------------------------------------------
  // Software brightness ceiling (0..1). PROVISIONAL: preserves the
  // pre-framework 100% software limit because no verified electrical or
  // thermal ceiling exists; physical validation pending. Never a safety claim.
  void set_max_brightness(float max) { max_brightness_ = clamp01(max); }

  // Provisional low/warm night profile (default 5% brightness, warm
  // red-dominant mix — avoids blue-heavy light; pending bench validation).
  void set_night_profile(float brightness, float red, float green, float blue) {
    night_brightness_ = clamp01(brightness);
    night_red_ = clamp01(red);
    night_green_ = clamp01(green);
    night_blue_ = clamp01(blue);
  }

  void set_night_behaviour(NightBehaviour behaviour) { behaviour_ = behaviour; }
  void set_status_level(StatusLevel level) { status_level_ = level; }

  // Compile-time composition capabilities (LED-FRAMEWORK-002): whether the
  // optional RoomIQ (darkness) and Presence (occupancy) frameworks are
  // actually composed alongside the LED framework. The LED framework works on
  // its own (Core + LED) and degrades cleanly: an automatic Night Mode
  // Behaviour whose required input is absent is downgraded to Manual, so the
  // engine never runs — or claims — an automation it has no honest input for.
  // Defaults false: a dependency is treated as absent unless a composition
  // proves it present, so a missing input can never be read as dark/occupied.
  void set_capabilities(bool has_roomiq, bool has_presence) {
    has_roomiq_ = has_roomiq;
    has_presence_ = has_presence;
  }
  bool has_roomiq() const { return has_roomiq_; }
  bool has_presence() const { return has_presence_; }

  // The behaviour actually in force after the capability downgrade. "When
  // dark" needs RoomIQ; "When dark and occupied" needs RoomIQ AND Presence. A
  // request the composition cannot support collapses to Manual — the single
  // source of truth for both the automation and the honest select fallback.
  NightBehaviour effective_behaviour() const {
    if (behaviour_ == NIGHT_WHEN_DARK && !has_roomiq_) return NIGHT_MANUAL;
    if (behaviour_ == NIGHT_WHEN_DARK_AND_OCCUPIED &&
        !(has_roomiq_ && has_presence_))
      return NIGHT_MANUAL;
    return behaviour_;
  }

  // True when the customer-selected behaviour is unsupported by this
  // composition and has been downgraded (drives the visible select fallback
  // to Manual and the on-device diagnostic — the mode is never silently
  // pretended to be active).
  bool behaviour_unsupported() const {
    return effective_behaviour() != behaviour_;
  }

  // Honest on-device explanation of the current behaviour: "OK" when the
  // selected mode is supported, otherwise which absent framework forced the
  // Manual fallback.
  const char *behaviour_status() const {
    if (behaviour_ == NIGHT_WHEN_DARK && !has_roomiq_)
      return "When dark needs RoomIQ (not composed) — using Manual";
    if (behaviour_ == NIGHT_WHEN_DARK_AND_OCCUPIED && !has_roomiq_)
      return "When dark and occupied needs RoomIQ (not composed) — using Manual";
    if (behaviour_ == NIGHT_WHEN_DARK_AND_OCCUPIED && !has_presence_)
      return "When dark and occupied needs Presence (not composed) — using Manual";
    return "OK";
  }

  void set_night_auto_off_ms(uint32_t delay_ms) { auto_off_ms_ = delay_ms; }
  void set_identify_duration_ms(uint32_t duration_ms) {
    identify_ms_ = duration_ms;
  }
  void set_status_duration_ms(uint32_t duration_ms) {
    status_ms_ = duration_ms;
  }

  // --- inputs ----------------------------------------------------------------
  // A customer/manual light change: customer intent always wins — it cancels
  // transient overlays and disengages Night Mode (suppressing automation
  // re-activation until the trigger condition resets).
  void input_customer_command(uint32_t now_ms, const LightState &state) {
    (void)now_ms;
    customer_ = sanitise(state);
    identify_active_ = false;
    status_active_ = false;
    if (night_on_) {
      if (night_auto_) auto_suppressed_ = true;
      night_on_ = false;
      night_auto_ = false;
    }
    auto_off_pending_ = false;
  }

  // Night Mode switch (automation=false) or automation (automation=true).
  void set_night_mode(uint32_t now_ms, bool on, bool automation) {
    (void)now_ms;
    if (automation) {
      night_on_ = on;
      night_auto_ = on;
      auto_off_pending_ = false;
      return;
    }
    if (on) {
      night_on_ = true;
      night_auto_ = false;  // manual ownership: automation never reverses it
      auto_suppressed_ = false;
      auto_off_pending_ = false;
    } else {
      // Manual off while the trigger condition may still hold: suppress
      // automation re-activation until the condition resets.
      night_on_ = false;
      night_auto_ = false;
      auto_suppressed_ = true;
      auto_off_pending_ = false;
    }
  }

  // Fused Occupancy input (LED-04): the unified Presence contract, never raw
  // sensors. `valid` reflects the Presence module runtime status — invalid
  // occupancy freezes the automation instead of toggling it.
  void input_occupancy(uint32_t now_ms, bool occupied, bool valid) {
    (void)now_ms;
    occupied_ = occupied;
    occupancy_valid_ = valid;
  }

  // Darkness decision from the canonical RoomIQ environmental engine
  // (ROOMIQ-FRAMEWORK-001): threshold, hysteresis and lux staleness are
  // computed there — ONE implementation. UNKNOWN never activates anything
  // and never toggles an active automation (fail-safe holds).
  void input_darkness(uint32_t now_ms, Darkness darkness) {
    (void)now_ms;
    darkness_ = darkness;
  }

  void request_identify(uint32_t now_ms) {
    identify_active_ = true;
    identify_started_ms_ = now_ms;
  }

  void notify_status(uint32_t now_ms, StatusEvent event) {
    last_event_ = event;
    last_event_valid_ = true;
    const bool allowed = event_allowed(event);
    // Transient status is the LOWEST priority (LED-07): it never pre-empts
    // a fault, an identify pulse, Night Mode, or an ON Room Light.
    const bool free =
        !fault_ && !identify_active_ && !night_on_ && !customer_.on;
    if (allowed && free) {
      status_active_ = true;
      status_started_ms_ = now_ms;
      status_event_ = event;
      last_event_suppressed_ = false;
    } else {
      last_event_suppressed_ = true;
    }
  }

  // Explicit persistent fault input. RESERVED: no composed component exposes
  // a supported LED fault signal today, so production YAML never sets this;
  // the engine contract exists (and is tested) for a future real signal.
  void set_fault(bool fault) { fault_ = fault; }

  // Restart restore (LED-11): re-applies the persisted stable customer state
  // and Night Mode ownership. Deliberately NO transient inputs — an
  // interrupted identify/status overlay is never restored. Invalid stored
  // values are sanitised (safe fallback, never an unexpected full-brightness
  // boot).
  void restore(const LightState &customer, bool night_on,
               bool night_automation_owned) {
    customer_ = sanitise(customer);
    night_on_ = night_on;
    night_auto_ = night_on && night_automation_owned;
    auto_suppressed_ = false;
    identify_active_ = false;
    status_active_ = false;
    auto_off_pending_ = false;
  }

  // --- evaluation
  // --------------------------------------------------------------
  void evaluate(uint32_t now_ms) {
    // Expire transient overlays.
    if (identify_active_ &&
        elapsed(identify_started_ms_, now_ms) >= identify_ms_) {
      identify_active_ = false;
    }
    if (status_active_ && elapsed(status_started_ms_, now_ms) >= status_ms_) {
      status_active_ = false;
    }

    run_night_automation(now_ms);

    // Compose the output from the highest-priority active layer (LED-07).
    if (fault_) {
      layer_ = LAYER_FAULT;
      output_ = fault_state();
    } else if (identify_active_) {
      layer_ = LAYER_IDENTIFY;
      output_ = identify_state(now_ms);
    } else if (night_on_) {
      layer_ = LAYER_NIGHT;
      output_ = night_state();
    } else if (status_active_) {
      layer_ = LAYER_STATUS;
      output_ = status_state();
    } else {
      layer_ = LAYER_CUSTOMER;
      output_ = clamped(customer_);
    }
  }

  // --- outputs
  // -------------------------------------------------------------------
  const LightState &output() const { return output_; }
  Layer active_layer() const { return layer_; }
  bool night_mode() const { return night_on_; }
  bool night_automation_owned() const { return night_auto_; }
  Darkness darkness() const { return darkness_; }
  const LightState &customer_state() const { return customer_; }
  bool has_status_event() const { return last_event_valid_; }
  StatusEvent last_status_event() const { return last_event_; }
  bool last_status_suppressed() const { return last_event_suppressed_; }

 private:
  static float clamp01(float value) {
    if (std::isnan(value)) return 0.0f;
    if (value < 0.0f) return 0.0f;
    if (value > 1.0f) return 1.0f;
    return value;
  }

  static uint32_t elapsed(uint32_t since_ms, uint32_t now_ms) {
    return now_ms - since_ms;  // unsigned arithmetic handles wrap-around
  }

  // Invalid values fall back to safe defaults: NaN brightness becomes a mid
  // value (never full brightness), colours clamp into range, and every
  // brightness obeys the software ceiling.
  LightState sanitise(const LightState &state) const {
    LightState out = state;
    if (std::isnan(out.brightness)) out.brightness = 0.5f;
    out.brightness = clamp01(out.brightness);
    if (out.brightness > max_brightness_) out.brightness = max_brightness_;
    out.red = std::isnan(out.red) ? 1.0f : clamp01(out.red);
    out.green = std::isnan(out.green) ? 1.0f : clamp01(out.green);
    out.blue = std::isnan(out.blue) ? 1.0f : clamp01(out.blue);
    if (out.effect > 2) out.effect = 0;
    return out;
  }

  LightState clamped(const LightState &state) const {
    LightState out = state;
    if (out.brightness > max_brightness_) out.brightness = max_brightness_;
    return out;
  }

  float capped(float brightness) const {
    return brightness > max_brightness_ ? max_brightness_ : brightness;
  }

  bool event_allowed(StatusEvent event) const {
    switch (status_level_) {
      case STATUS_LEVEL_OFF:
        return false;
      case STATUS_LEVEL_ESSENTIAL:
        return event == EVENT_STARTUP || event == EVENT_CONNECTED ||
               event == EVENT_WARNING;
      case STATUS_LEVEL_DETAILED:
        return true;
    }
    return false;
  }

  void run_night_automation(uint32_t now_ms) {
    // Capability downgrade (LED-FRAMEWORK-002): an automatic behaviour whose
    // required framework is not composed collapses to Manual, so automation
    // never runs off an absent input.
    const NightBehaviour behaviour = effective_behaviour();
    if (behaviour == NIGHT_MANUAL) {
      auto_off_pending_ = false;
      return;
    }

    // Decide whether the trigger condition is knowable and wanted.
    bool known = false;
    bool want = false;
    if (behaviour == NIGHT_WHEN_DARK) {
      known = darkness_ != DARKNESS_UNKNOWN;
      want = darkness_ == DARKNESS_DARK;
    } else {  // NIGHT_WHEN_DARK_AND_OCCUPIED
      known = darkness_ != DARKNESS_UNKNOWN && occupancy_valid_;
      want = darkness_ == DARKNESS_DARK && occupied_;
    }

    if (!known) {
      // Fail safe: unknown inputs freeze the automation — the current state
      // holds, nothing toggles, and no pending auto-off fires from unknown
      // data.
      auto_off_pending_ = false;
      return;
    }

    if (want) {
      // A fresh trigger (e.g. re-occupancy) cancels any pending auto-off.
      auto_off_pending_ = false;
      if (night_on_) return;
      if (auto_suppressed_) return;  // customer said no; wait for a reset
      // Never pre-empt an in-use Room Light: automation must not dim or
      // change a light the customer has on (LED-04).
      if (customer_.on) return;
      night_on_ = true;
      night_auto_ = true;
    } else {
      // Condition reset re-arms a manual-off suppression.
      auto_suppressed_ = false;
      if (!(night_on_ && night_auto_)) {
        auto_off_pending_ = false;
        return;
      }
      if (behaviour == NIGHT_WHEN_DARK_AND_OCCUPIED &&
          darkness_ == DARKNESS_DARK) {
        // Occupancy-clear path: delayed off so brief absences do not flap
        // the light; a fresh occupancy event cancels the pending off.
        if (!auto_off_pending_) {
          auto_off_pending_ = true;
          auto_off_started_ms_ = now_ms;
        }
        if (elapsed(auto_off_started_ms_, now_ms) >= auto_off_ms_) {
          night_on_ = false;
          night_auto_ = false;
          auto_off_pending_ = false;
        }
      } else {
        // Brightness-driven off (hysteresis already prevents flapping).
        night_on_ = false;
        night_auto_ = false;
        auto_off_pending_ = false;
      }
    }
  }

  LightState night_state() const {
    LightState out;
    out.on = true;
    out.brightness = capped(night_brightness_);
    out.red = night_red_;
    out.green = night_green_;
    out.blue = night_blue_;
    out.effect = 0;
    return out;
  }

  // Short, recognisable, non-disruptive identify pulse: gentle 1 s cycles
  // between 10% and 40% in a soft warm white. Provisional pattern pending
  // bench validation of perceived output.
  LightState identify_state(uint32_t now_ms) const {
    const uint32_t t = elapsed(identify_started_ms_, now_ms);
    const float phase = static_cast<float>(t % 1000u) / 1000.0f;
    const float wave = 0.5f * (1.0f - std::cos(phase * 2.0f * 3.14159265f));
    LightState out;
    out.on = true;
    out.brightness = capped(0.10f + 0.30f * wave);
    out.red = 1.0f;
    out.green = 0.85f;
    out.blue = 0.60f;
    out.effect = 0;
    return out;
  }

  // Brief, discreet status indications (provisional colours, software
  // definitions pending bench validation of perceived output).
  LightState status_state() const {
    LightState out;
    out.on = true;
    out.effect = 0;
    switch (status_event_) {
      case EVENT_STARTUP:
        out.brightness = capped(0.20f);
        out.red = 1.0f;
        out.green = 1.0f;
        out.blue = 1.0f;
        break;
      case EVENT_CONNECTED:
        out.brightness = capped(0.25f);
        out.red = 0.20f;
        out.green = 1.0f;
        out.blue = 0.20f;
        break;
      case EVENT_DETAIL_INFO:
        out.brightness = capped(0.20f);
        out.red = 0.30f;
        out.green = 0.50f;
        out.blue = 1.0f;
        break;
      case EVENT_WARNING:
      case EVENT_DETAIL_WARNING:
        out.brightness = capped(0.30f);
        out.red = 1.0f;
        out.green = 0.45f;
        out.blue = 0.0f;
        break;
    }
    return out;
  }

  // Persistent fault indication: steady dim red (reserved for a real,
  // explicit fault signal — see set_fault()).
  LightState fault_state() const {
    LightState out;
    out.on = true;
    out.brightness = capped(0.30f);
    out.red = 1.0f;
    out.green = 0.0f;
    out.blue = 0.0f;
    out.effect = 0;
    return out;
  }

  // configuration
  float max_brightness_ = 1.0f;
  float night_brightness_ = 0.05f;
  float night_red_ = 1.0f;
  float night_green_ = 0.58f;
  float night_blue_ = 0.16f;
  NightBehaviour behaviour_ = NIGHT_MANUAL;
  StatusLevel status_level_ = STATUS_LEVEL_ESSENTIAL;
  // Compile-time composition capabilities (LED-FRAMEWORK-002). Default false:
  // the optional RoomIQ / Presence inputs are absent unless a composition
  // proves them present.
  bool has_roomiq_ = false;
  bool has_presence_ = false;
  uint32_t auto_off_ms_ = 60000;
  uint32_t identify_ms_ = 4000;
  uint32_t status_ms_ = 1500;

  // customer state (persisted by the framework globals)
  LightState customer_;

  // night mode state
  bool night_on_ = false;
  bool night_auto_ = false;
  bool auto_suppressed_ = false;
  bool auto_off_pending_ = false;
  uint32_t auto_off_started_ms_ = 0;

  // automation inputs
  bool occupied_ = false;
  bool occupancy_valid_ = false;
  Darkness darkness_ = DARKNESS_UNKNOWN;

  // transient overlays
  bool identify_active_ = false;
  uint32_t identify_started_ms_ = 0;
  bool status_active_ = false;
  uint32_t status_started_ms_ = 0;
  StatusEvent status_event_ = EVENT_STARTUP;
  StatusEvent last_event_ = EVENT_STARTUP;
  bool last_event_valid_ = false;
  bool last_event_suppressed_ = false;

  // fault (reserved)
  bool fault_ = false;

  // output
  LightState output_;
  Layer layer_ = LAYER_CUSTOMER;
};

// Accessor for the firmware's single controller instance. ESPHome emits
// `esphome: includes:` headers AFTER the globals storage declarations in the
// generated main.cpp, so a custom-class `globals:` entry cannot name this
// type; production lambdas share this function-local static instead
// (constructed on first use). Tests instantiate their own LedController
// objects directly.
inline LedController &global_controller() {
  static LedController controller;
  return controller;
}

}  // namespace ledfw
}  // namespace sense360

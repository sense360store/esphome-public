#pragma once

// ============================================================================
// PRESENCE-FRAMEWORK-001 — tri-sensor Presence fusion engine (header-only)
// ============================================================================
// The single implementation of the Sense360 RoomIQ Presence fusion state
// machine. It is compiled BOTH into production firmware (via
// `esphome: includes:` in packages/features/presence_framework.yaml) and
// into the deterministic simulation tests (tests/unit/test_presence_fusion.cpp)
// so the tested logic and the shipped logic can never drift.
//
// Sensor roles (accepted product decisions PD-01..PD-10):
//   * PIR      — immediate movement trigger (GPIO level, schematic IO15).
//   * LD2450   — movement, still targets, target count, position (UART,
//                256000 baud). The ONLY channel with a real freshness signal
//                (frame-driven update timestamps).
//   * SEN0609  — static-presence hold (digital output line, schematic IO6).
//
// Honesty rules baked into this engine:
//   * Stale or missing data is UNKNOWN — never interpreted as "clear".
//   * A GPIO-level channel (PIR, SEN0609 digital out) is "non-verifiable":
//     it can assert presence and vote clear, but it can never be proven
//     fresh or proven failed, so it never qualifies the module as fully
//     Available on its own and never drives it Unavailable.
//   * Occupancy clears only when every currently usable sensor reports
//     clear AND the configured clear delay has expired; if no usable sensor
//     remains while occupied, a documented conservative fallback timeout
//     (degraded hold) eventually releases the latch.
//   * No synthetic confidence numbers: outputs are states, not invented
//     probabilities.
//
// Timing values are engineering defaults pending bench validation
// (docs/hardware/presence-framework-bench-checklist.md). Nothing in this
// header claims hardware validation.
// ============================================================================

#include <cstdint>
#include <cstring>

namespace sense360 {
namespace presence {

// Customer-facing Presence Status values (PD-02). The strings below are the
// exact accepted customer wording; they are single-sourced here.
enum Status {
  STATUS_INITIALISING = 0,
  STATUS_CLEAR = 1,
  STATUS_MOVEMENT = 2,
  STATUS_STILL = 3,
  STATUS_MULTIPLE = 4,
  STATUS_DEGRADED = 5,
  STATUS_UNAVAILABLE = 6,
};

// Module-health values (PD-07) — the Core-Framework reserved runtime
// vocabulary (config/core-framework.json module_status.reserved_values).
enum Health {
  HEALTH_INITIALISING = 0,
  HEALTH_AVAILABLE = 1,
  HEALTH_DEGRADED = 2,
  HEALTH_UNAVAILABLE = 3,
  HEALTH_FAULT = 4,
};

// Customer modes (PD-10).
enum Mode {
  MODE_BALANCED = 0,
  MODE_RESPONSIVE = 1,
  MODE_STABLE = 2,
  MODE_CUSTOM = 3,
};

inline const char *status_to_string(Status status) {
  switch (status) {
    case STATUS_INITIALISING:
      return "Initialising";
    case STATUS_CLEAR:
      return "Clear";
    case STATUS_MOVEMENT:
      return "Movement detected";
    case STATUS_STILL:
      return "Still presence";
    case STATUS_MULTIPLE:
      return "Multiple people";
    case STATUS_DEGRADED:
      return "Sensor degraded";
    case STATUS_UNAVAILABLE:
      return "Unavailable";
  }
  return "Unavailable";
}

inline const char *health_to_string(Health health) {
  switch (health) {
    case HEALTH_INITIALISING:
      return "Initialising";
    case HEALTH_AVAILABLE:
      return "Available";
    case HEALTH_DEGRADED:
      return "Degraded";
    case HEALTH_UNAVAILABLE:
      return "Unavailable";
    case HEALTH_FAULT:
      return "Fault";
  }
  return "Unavailable";
}

inline Mode mode_from_string(const char *mode) {
  if (mode != nullptr) {
    if (std::strcmp(mode, "Responsive") == 0) return MODE_RESPONSIVE;
    if (std::strcmp(mode, "Stable") == 0) return MODE_STABLE;
    if (std::strcmp(mode, "Custom") == 0) return MODE_CUSTOM;
  }
  return MODE_BALANCED;  // safe default
}

// Documented runtime fusion parameters each mode controls (PD-10). Modes
// deliberately change ONLY genuinely runtime-configurable fusion settings:
// no unsupported dynamic sensor commands are issued to PIR / LD2450 /
// SEN0609. Values are engineering defaults pending bench tuning.
struct ModeParams {
  uint32_t clear_delay_ms;    // preset applied to the Clear Delay control
  uint32_t pir_hold_ms;       // movement retention after a PIR edge
  uint32_t degraded_hold_ms;  // conservative fallback when nothing usable
};

inline ModeParams mode_params(Mode mode) {
  switch (mode) {
    case MODE_RESPONSIVE:
      return ModeParams{10000, 5000, 30000};
    case MODE_STABLE:
      return ModeParams{120000, 20000, 300000};
    case MODE_BALANCED:
    case MODE_CUSTOM:  // Custom keeps Balanced fusion internals; the clear
                       // delay itself is owned by the user-facing control.
      break;
  }
  return ModeParams{30000, 10000, 60000};
}

// Per-channel compile/configuration facts (configuration-driven expected
// sensor membership, PD-08). `verifiable` means the channel carries a real
// data-freshness signal (frame-driven update timestamps); GPIO-level
// channels must set it false.
struct ChannelConfig {
  bool expected;
  bool verifiable;
  uint32_t warmup_ms;
  uint32_t stale_ms;  // only meaningful when verifiable
};

class FusionEngine {
 public:
  // --- configuration --------------------------------------------------------
  void configure_pir(const ChannelConfig &config) { pir_cfg_ = config; }
  void configure_radar(const ChannelConfig &config) { radar_cfg_ = config; }
  void configure_static(const ChannelConfig &config) { static_cfg_ = config; }

  void set_mode(Mode mode) { mode_ = mode; }
  Mode mode() const { return mode_; }

  // Runtime-adjustable clear delay (PD-04): changing it never requires a
  // recompile — the next evaluation uses the new value.
  void set_clear_delay_ms(uint32_t delay_ms) { clear_delay_ms_ = delay_ms; }
  uint32_t clear_delay_ms() const { return clear_delay_ms_; }

  // Explicit module-level fault input (reserved: no composed sensor exposes
  // a supported fault signal today — see the framework doc).
  void set_module_fault(bool fault) { module_fault_ = fault; }

  // --- sensor inputs ---------------------------------------------------------
  void input_pir(uint32_t now_ms, bool level) {
    begin_if_needed(now_ms);
    pir_level_ = level;
    if (level) pir_last_high_ms_ = now_ms;
    pir_seen_ = true;
  }

  void input_radar_frame(uint32_t now_ms, int targets, int moving, int still) {
    begin_if_needed(now_ms);
    radar_last_update_ms_ = now_ms;
    radar_seen_ = true;
    radar_targets_ = targets;
    radar_moving_ = moving;
    radar_still_ = still;
  }

  void input_static(uint32_t now_ms, bool level) {
    begin_if_needed(now_ms);
    static_level_ = level;
    static_last_update_ms_ = now_ms;
    static_seen_ = true;
  }

  // --- evaluation -------------------------------------------------------------
  void evaluate(uint32_t now_ms) {
    begin_if_needed(now_ms);
    const ModeParams params = mode_params(mode_);

    // ---- per-channel views -------------------------------------------------
    const bool pir_ready = past_warmup(now_ms, pir_cfg_);
    const bool radar_fresh = channel_fresh(now_ms, radar_cfg_, radar_seen_, radar_last_update_ms_);
    const bool static_fresh =
        channel_fresh(now_ms, static_cfg_, static_seen_, static_last_update_ms_);
    // A non-verifiable channel's level is a live reading once past warm-up.
    const bool static_ready =
        static_cfg_.expected &&
        (static_cfg_.verifiable ? static_fresh : past_warmup(now_ms, static_cfg_));

    // Assertions (presence claims).
    const bool pir_active = pir_cfg_.expected && pir_ready && pir_seen_ &&
                            (pir_level_ || elapsed(pir_last_high_ms_, now_ms) <= params.pir_hold_ms) &&
                            pir_last_high_ms_ != NEVER;
    const bool radar_presence = radar_cfg_.expected && radar_fresh && radar_targets_ > 0;
    const bool radar_movement = radar_cfg_.expected && radar_fresh && radar_moving_ > 0;
    const bool static_active = static_ready && static_level_;

    const bool asserting = pir_active || radar_presence || static_active;

    // Clear voters: a channel may vote "clear" ONLY while it is usable —
    // fresh (verifiable) or past warm-up (non-verifiable live level).
    // Stale or initialising channels are UNKNOWN and vote nothing.
    int voters = 0;
    int clear_votes = 0;
    if (radar_cfg_.expected && radar_fresh) {
      voters++;
      if (radar_targets_ == 0) clear_votes++;
    }
    if (pir_cfg_.expected && pir_ready) {
      voters++;
      if (!pir_active) clear_votes++;
    }
    if (static_ready) {
      voters++;
      if (!static_level_) clear_votes++;
    }

    // ---- occupancy latch (fail-safe rules) ----------------------------------
    if (asserting) {
      occupied_ = true;
      clear_pending_ = false;
      unconfirmed_pending_ = false;
    } else if (occupied_) {
      if (voters > 0 && clear_votes == voters) {
        unconfirmed_pending_ = false;
        if (!clear_pending_) {
          clear_pending_ = true;
          clear_started_ms_ = now_ms;
        }
        if (elapsed(clear_started_ms_, now_ms) >= clear_delay_ms_) {
          occupied_ = false;
          clear_pending_ = false;
        }
      } else if (voters == 0) {
        // No usable sensor can confirm anything: hold conservatively, then
        // release after the documented degraded fallback so a dead sensor
        // set cannot latch occupancy forever.
        clear_pending_ = false;
        if (!unconfirmed_pending_) {
          unconfirmed_pending_ = true;
          unconfirmed_started_ms_ = now_ms;
        }
        if (elapsed(unconfirmed_started_ms_, now_ms) >= params.degraded_hold_ms) {
          occupied_ = false;
          unconfirmed_pending_ = false;
        }
      }
    } else {
      clear_pending_ = false;
      unconfirmed_pending_ = false;
    }

    // ---- module health (PD-07) ----------------------------------------------
    health_ = compute_health(now_ms, radar_fresh, static_fresh);

    // ---- customer status (PD-02 precedence, documented deviation: while
    // occupied the status keeps showing activity and the module-status
    // entity carries the degradation) ----------------------------------------
    if (health_ == HEALTH_UNAVAILABLE || health_ == HEALTH_FAULT) {
      status_ = STATUS_UNAVAILABLE;
    } else if (health_ == HEALTH_INITIALISING) {
      status_ = STATUS_INITIALISING;
    } else if (occupied_) {
      if (radar_cfg_.expected && radar_fresh && radar_targets_ >= 2) {
        status_ = STATUS_MULTIPLE;
      } else if (pir_active || radar_movement) {
        status_ = STATUS_MOVEMENT;
      } else {
        status_ = STATUS_STILL;
      }
    } else if (health_ == HEALTH_DEGRADED) {
      status_ = STATUS_DEGRADED;
    } else {
      status_ = STATUS_CLEAR;
    }

    radar_fresh_out_ = radar_fresh;
  }

  // --- outputs -----------------------------------------------------------------
  bool occupancy() const { return occupied_; }
  Status status() const { return status_; }
  Health health() const { return health_; }
  bool radar_fresh() const { return radar_fresh_out_; }
  int radar_target_count() const { return radar_targets_; }

 private:
  enum : uint32_t { NEVER = 0xFFFFFFFFu };

  static uint32_t elapsed(uint32_t since_ms, uint32_t now_ms) {
    if (since_ms == NEVER) return NEVER;
    return now_ms - since_ms;  // unsigned arithmetic handles wrap-around
  }

  void begin_if_needed(uint32_t now_ms) {
    if (!begun_) {
      begun_ = true;
      boot_ms_ = now_ms;
    }
  }

  bool past_warmup(uint32_t now_ms, const ChannelConfig &config) const {
    return config.expected && elapsed(boot_ms_, now_ms) >= config.warmup_ms;
  }

  bool channel_fresh(uint32_t now_ms, const ChannelConfig &config, bool seen,
                     uint32_t last_update_ms) const {
    if (!config.expected || !config.verifiable || !seen) return false;
    return elapsed(last_update_ms, now_ms) <= config.stale_ms;
  }

  // A verifiable channel has FAILED once its warm-up window has elapsed and
  // it is not fresh. Non-verifiable (GPIO-level) channels can never be
  // proven failed — and never proven healthy (documented limitation).
  bool channel_failed(uint32_t now_ms, const ChannelConfig &config, bool fresh) const {
    return config.expected && config.verifiable && past_warmup(now_ms, config) && !fresh;
  }

  // A channel is still initialising while inside its warm-up window and,
  // for verifiable channels, no valid update has arrived yet (a real update
  // ends initialisation early).
  bool channel_initialising(uint32_t now_ms, const ChannelConfig &config, bool seen) const {
    if (!config.expected) return false;
    if (past_warmup(now_ms, config)) return false;
    return !(config.verifiable && seen);
  }

  Health compute_health(uint32_t now_ms, bool radar_fresh, bool static_fresh) {
    if (module_fault_) return HEALTH_FAULT;

    const bool radar_failed = channel_failed(now_ms, radar_cfg_, radar_fresh);
    const bool static_failed = channel_failed(now_ms, static_cfg_, static_fresh);
    const int failed = (radar_failed ? 1 : 0) + (static_failed ? 1 : 0);

    // "Usable" = can still contribute a live opinion: a fresh verifiable
    // channel, or a non-verifiable trigger channel past its warm-up.
    const bool radar_usable = radar_cfg_.expected && radar_fresh;
    const bool static_usable =
        static_cfg_.expected &&
        (static_cfg_.verifiable ? static_fresh : past_warmup(now_ms, static_cfg_));
    const bool pir_usable = pir_cfg_.expected && past_warmup(now_ms, pir_cfg_);
    const bool any_usable = radar_usable || static_usable || pir_usable;

    if (failed > 0) return any_usable ? HEALTH_DEGRADED : HEALTH_UNAVAILABLE;

    const bool any_initialising = channel_initialising(now_ms, pir_cfg_, false) ||
                                  channel_initialising(now_ms, radar_cfg_, radar_seen_) ||
                                  channel_initialising(now_ms, static_cfg_, static_seen_);
    if (any_initialising) return HEALTH_INITIALISING;

    return HEALTH_AVAILABLE;
  }

  // configuration
  ChannelConfig pir_cfg_{false, false, 0, 0};
  ChannelConfig radar_cfg_{false, true, 0, 0};
  ChannelConfig static_cfg_{false, false, 0, 0};
  Mode mode_ = MODE_BALANCED;
  uint32_t clear_delay_ms_ = 30000;  // PD-04 default
  bool module_fault_ = false;

  // lifecycle
  bool begun_ = false;
  uint32_t boot_ms_ = 0;

  // channel state
  bool pir_level_ = false;
  bool pir_seen_ = false;
  uint32_t pir_last_high_ms_ = NEVER;
  bool radar_seen_ = false;
  uint32_t radar_last_update_ms_ = NEVER;
  int radar_targets_ = 0;
  int radar_moving_ = 0;
  int radar_still_ = 0;
  bool static_level_ = false;
  bool static_seen_ = false;
  uint32_t static_last_update_ms_ = NEVER;

  // fusion state
  bool occupied_ = false;
  bool clear_pending_ = false;
  uint32_t clear_started_ms_ = 0;
  bool unconfirmed_pending_ = false;
  uint32_t unconfirmed_started_ms_ = 0;
  Status status_ = STATUS_INITIALISING;
  Health health_ = HEALTH_INITIALISING;
  bool radar_fresh_out_ = false;
};

// Accessor for the firmware's single fusion-engine instance. ESPHome
// 2026.4.5 emits `esphome: includes:` headers AFTER the globals storage
// declarations in the generated main.cpp, so a custom-class `globals:`
// entry cannot name this type; production lambdas share this
// function-local static instead (constructed on first use). Tests may
// still instantiate their own FusionEngine objects directly.
inline FusionEngine &global_engine() {
  static FusionEngine engine;
  return engine;
}

}  // namespace presence
}  // namespace sense360

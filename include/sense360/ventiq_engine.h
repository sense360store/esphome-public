#pragma once

// ============================================================================
// VENTIQ-FRAMEWORK-001 — canonical VentIQ bathroom ventilation engine
// ============================================================================
// The single implementation of the Sense360 VentIQ ventilation service.
// It is compiled BOTH into production firmware (via `esphome: includes:` in
// packages/features/ventiq_framework.yaml) and into the deterministic
// simulation tests (tests/unit/test_ventiq_engine.cpp) so the tested logic
// and the shipped logic can never drift.
//
// What it owns — the VentIQ-specific ventilation behaviour ONLY:
//   * The shower state machine (rate-of-rise OR absolute humidity start;
//     falling-humidity end; a maximum-duration timeout so a stuck-humid
//     bathroom is never claimed to be "showering" forever).
//   * The post-shower moisture-clearing window.
//   * The sustained-damp (mould-risk) accumulator with honest no-data
//     freezing (no data means no accumulation AND no reset).
//   * The high-humidity advice state with release hysteresis.
//   * ONE deterministic customer ventilation Recommendation and ONE
//     plain-language Ventilation Reason, from a fixed priority ladder:
//     manual request > shower > clearing > very poor air > damp (high) >
//     damp (medium) > poor air > odour > high humidity > nothing.
//   * The legacy fan-percent mapping (compatibility surface only).
//   * VentIQ module health over the board's own verifiable channels.
//
// What it deliberately does NOT own (consumed, never duplicated):
//   * Pollutant severity. VOC/NOx classification comes from an EMBEDDED
//     canonical AirIQ engine (include/sense360/airiq_engine.h — the
//     platform's single source of pollutant truth). No VOC/NOx band
//     value is re-declared here; the AirIQ defaults are the values.
//     The odour signal is defined as "VOC or NOx at Fair or worse" —
//     the canonical Fair boundary (VOC index 150) is exactly the legacy
//     VentIQ odour threshold, so no second threshold exists.
//   * Environmental measurement. Humidity and temperature inputs are the
//     RoomIQ CANONICAL calibrated values (s360_humidity /
//     s360_temperature published by ROOMIQ-FRAMEWORK-001) — never raw
//     board sensors. Comfort classification stays RoomIQ's; this engine
//     only applies VENTILATION semantics (shower dynamics, damp
//     accumulation) that RoomIQ does not own.
//   * Compile-time module presence. "Is the ventilation hardware
//     available?" is answered by the Core framework's Fan Control
//     Module Status entity — never duplicated here.
//
// Honesty rules baked into this engine:
//   * The S360-211's ONLY schematic-proven on-board sensor is the SGP41
//     (verified schematic S360-211-R4.pdf, single sheet). Module health
//     therefore attests the SGP41 VOC/NOx freshness ONLY. The humidity
//     input is RoomIQ-owned: its loss degrades the ventilation SERVICE
//     (shower/damp features go quiet, honestly) but NEVER the VentIQ
//     module status — a healthy VentIQ board must not be blamed for a
//     RoomIQ outage, and vice versa.
//   * The compiled SHT4x/BMP390 drivers in the VentIQ board package are
//     FIRMWARE/SCHEMATIC DRIFT (no such part on the verified schematic;
//     no BOM committed). This engine takes NO input from them.
//   * The board's fan-relay stage is drawn crossed-out (do-not-populate
//     convention) on the verified schematic and has no bound driver: no
//     runtime fan health exists, so none is invented or reported.
//   * A value is usable only after a real, valid update inside its stale
//     window; stale channels read unknown (NAN), never frozen.
//   * Startup is Initialising, never a fault. Fault is a reserved
//     contract with NO production producer today.
//   * All thresholds are PROVISIONAL engineering heuristics pending
//     bench and customer validation — never medical, health, building-
//     standard or regulatory claims.
//
// Nothing in this header claims hardware validation.
// ============================================================================

#include <cmath>
#include <cstdint>

#include "airiq_engine.h"

namespace sense360 {
namespace ventiq {

// The customer ventilation demand (drives the ONE Recommendation entity).
// String vocabulary matches the platform's AirIQ recommendation wording.
enum Demand {
  DEMAND_INITIALISING = 0,
  DEMAND_NONE = 1,
  DEMAND_SOON = 2,
  DEMAND_NOW = 3,
  DEMAND_UNAVAILABLE = 4,
};

inline const char *demand_to_string(Demand demand) {
  switch (demand) {
    case DEMAND_INITIALISING:
      return "Sensor initialising";
    case DEMAND_NONE:
      return "No action needed";
    case DEMAND_SOON:
      return "Ventilate soon";
    case DEMAND_NOW:
      return "Ventilate now";
    case DEMAND_UNAVAILABLE:
      return "Unavailable";
  }
  return "Unavailable";
}

// The plain-language driver behind the current demand (the customer
// "why" — one reason, the highest-priority active one).
enum Reason {
  REASON_INITIALISING = 0,
  REASON_NONE = 1,
  REASON_REQUESTED = 2,
  REASON_SHOWER = 3,
  REASON_CLEARING = 4,
  REASON_AIR_QUALITY = 5,
  REASON_MOULD = 6,
  REASON_ODOUR = 7,
  REASON_HUMIDITY = 8,
  REASON_UNAVAILABLE = 9,
};

inline const char *reason_to_string(Reason reason) {
  switch (reason) {
    case REASON_INITIALISING:
      return "Sensor initialising";
    case REASON_NONE:
      return "No ventilation needed";
    case REASON_REQUESTED:
      return "Ventilation requested";
    case REASON_SHOWER:
      return "Shower in progress";
    case REASON_CLEARING:
      return "Clearing shower moisture";
    case REASON_AIR_QUALITY:
      return "Poor air quality";
    case REASON_MOULD:
      return "Damp for a long time";
    case REASON_ODOUR:
      return "Odour detected";
    case REASON_HUMIDITY:
      return "High humidity";
    case REASON_UNAVAILABLE:
      return "Unavailable";
  }
  return "Unavailable";
}

class VentIQEngine {
 public:
  VentIQEngine() {
    // The embedded canonical pollutant engine expects ONLY the S360-211's
    // schematic-proven sensor channels: SGP41 VOC + NOx. CO2 / PM /
    // formaldehyde / ozone have no producer on this board and must never
    // degrade anything. (The AirIQ engine's own defaults expect CO2 —
    // correct for the S360-210 board, overridden here for S360-211.)
    pollutants_.set_expected(airiq::POLLUTANT_CO2, false);
    pollutants_.set_expected(airiq::POLLUTANT_VOC, true);
    pollutants_.set_expected(airiq::POLLUTANT_NOX, true);
    pollutants_.set_expected(airiq::POLLUTANT_PM25, false);
    pollutants_.set_expected(airiq::POLLUTANT_HCHO, false);
    pollutants_.set_expected(airiq::POLLUTANT_O3, false);
    // The compiled VentIQ SGP41 updates every 10 s (vs AirIQ's 30 s), so
    // the stale window tightens to six missed updates. PROVISIONAL.
    pollutants_.set_stale_ms(airiq::POLLUTANT_VOC, 60000);
    pollutants_.set_stale_ms(airiq::POLLUTANT_NOX, 60000);
    // VOC/NOx severity thresholds are deliberately NOT set here: the
    // canonical AirIQ engine defaults are the platform's single source
    // of pollutant truth.
  }

  // --- composition configuration (substitution-driven) -----------------------
  // Ventilation heuristics — PROVISIONAL defaults pending bench and
  // customer validation. Runtime-adjustable via the preserved customer
  // number entities (which pre-framework were placebo controls).
  void set_shower_threshold_pct(float pct) {
    if (valid_pct(pct)) shower_threshold_pct_ = pct;
  }
  void set_shower_rate_threshold(float pct_per_min) {
    if (!std::isnan(pct_per_min) && pct_per_min > 0.0f)
      shower_rate_threshold_ = pct_per_min;
  }
  void set_shower_end_delta_pct(float pct) {
    if (!std::isnan(pct) && pct >= 0.0f) shower_end_delta_pct_ = pct;
  }
  void set_shower_max_minutes(float minutes) {
    if (!std::isnan(minutes) && minutes > 0.0f) shower_max_minutes_ = minutes;
  }
  void set_clearing_minutes(float minutes) {
    if (!std::isnan(minutes) && minutes >= 0.0f) clearing_minutes_ = minutes;
  }
  void set_mould_threshold_pct(float pct) {
    if (valid_pct(pct)) mould_threshold_pct_ = pct;
  }
  void set_mould_duration_minutes(float minutes) {
    if (!std::isnan(minutes) && minutes > 0.0f)
      mould_duration_minutes_ = minutes;
  }
  void set_humidity_high_pct(float pct) {
    if (valid_pct(pct)) humidity_high_pct_ = pct;
  }
  void set_humidity_hysteresis_pct(float pct) {
    if (!std::isnan(pct) && pct >= 0.0f) humidity_hysteresis_pct_ = pct;
  }

  // Freshness windows (per input channel, independent; provisional).
  void set_humidity_warmup_ms(uint32_t ms) { humidity_warmup_ms_ = ms; }
  void set_humidity_stale_ms(uint32_t ms) { humidity_stale_ms_ = ms; }
  void set_temperature_warmup_ms(uint32_t ms) { temperature_warmup_ms_ = ms; }
  void set_temperature_stale_ms(uint32_t ms) { temperature_stale_ms_ = ms; }
  void set_voc_warmup_ms(uint32_t ms) {
    pollutants_.set_warmup_ms(airiq::POLLUTANT_VOC, ms);
  }
  void set_voc_stale_ms(uint32_t ms) {
    pollutants_.set_stale_ms(airiq::POLLUTANT_VOC, ms);
  }
  void set_nox_warmup_ms(uint32_t ms) {
    pollutants_.set_warmup_ms(airiq::POLLUTANT_NOX, ms);
  }
  void set_nox_stale_ms(uint32_t ms) {
    pollutants_.set_stale_ms(airiq::POLLUTANT_NOX, ms);
  }

  // Expected-channel passthrough for a future composition that declares
  // a real external attachment (configuration-driven; no Base/Pro axis).
  void set_pollutant_expected(airiq::Pollutant pollutant, bool expected) {
    pollutants_.set_expected(pollutant, expected);
  }

  // Customer control: pause shower detection (preserved legacy switch).
  void set_shower_detection_enabled(bool enabled) {
    shower_detection_enabled_ = enabled;
    if (!enabled) shower_active_ = false;
  }

  // Explicit persistent fault input. RESERVED: no composed component
  // exposes a supported VentIQ fault signal today, so production YAML
  // never sets this. Ordinary staleness NEVER produces Fault.
  void set_fault(bool fault) { pollutants_.set_fault(fault); }

  // --- lifecycle
  // ---------------------------------------------------------------
  void begin(uint32_t now_ms) {
    started_ = true;
    start_ms_ = now_ms;
    last_accum_ms_ = now_ms;
    pollutants_.begin(now_ms);
  }

  // --- inputs (real update callbacks — the freshness signal)
  // -------------------- Humidity/temperature are the RoomIQ CANONICAL
  // calibrated values (s360_humidity / s360_temperature). A NaN or out-of-range
  // sample is an INVALID update: it never refreshes the channel.
  void input_humidity(uint32_t now_ms, float pct) {
    ensure_started(now_ms);
    if (!valid_pct(pct)) return;
    humidity_ = pct;
    humidity_seen_ = true;
    humidity_last_ms_ = now_ms;
    push_humidity_sample(now_ms, pct);
  }
  void input_temperature(uint32_t now_ms, float celsius) {
    ensure_started(now_ms);
    if (std::isnan(celsius) || celsius < -40.0f || celsius > 85.0f) return;
    temperature_ = celsius;
    temperature_seen_ = true;
    temperature_last_ms_ = now_ms;
  }
  // SGP41 relative indices from the board's own sensor (the freshness
  // evidence behind VentIQ module health).
  void input_voc(uint32_t now_ms, float index) {
    ensure_started(now_ms);
    pollutants_.input_voc(now_ms, index);
  }
  void input_nox(uint32_t now_ms, float index) {
    ensure_started(now_ms);
    pollutants_.input_nox(now_ms, index);
  }

  // --- manual customer actions
  // --------------------------------------------------- A manual request is
  // honoured regardless of sensor state (the customer asked; no sensor evidence
  // is required to run a fan).
  void force_ventilation(uint32_t now_ms, float minutes) {
    ensure_started(now_ms);
    if (std::isnan(minutes) || minutes <= 0.0f) return;
    forced_until_ms_ = now_ms + (uint32_t)(minutes * 60000.0f);
    forced_active_ = true;
  }
  void reset_shower(uint32_t now_ms) {
    ensure_started(now_ms);
    shower_active_ = false;
    clearing_until_ms_ = 0;
    clearing_active_ = false;
    forced_active_ = false;
  }
  void reset_mould() { wet_ms_ = 0; }

  // --- evaluation
  // ------------------------------------------------------------------
  void evaluate(uint32_t now_ms) {
    ensure_started(now_ms);
    pollutants_.evaluate(now_ms);

    humidity_state_ = channel_state(now_ms, humidity_seen_, humidity_last_ms_,
                                    humidity_warmup_ms_, humidity_stale_ms_);
    temperature_state_ =
        channel_state(now_ms, temperature_seen_, temperature_last_ms_,
                      temperature_warmup_ms_, temperature_stale_ms_);

    update_rate();
    update_shower(now_ms);
    update_clearing(now_ms);
    update_mould(now_ms);
    update_humidity_high();
    update_forced(now_ms);
    update_demand();
  }

  // --- value outputs (NAN unless the channel is fresh)
  // ------------------------------
  float humidity() const {
    return humidity_state_ == CHANNEL_FRESH ? humidity_ : NAN;
  }
  float temperature() const {
    return temperature_state_ == CHANNEL_FRESH ? temperature_ : NAN;
  }
  float voc() const { return pollutants_.voc(); }
  float nox() const { return pollutants_.nox(); }

  // Dew point (Magnus formula) from the canonical calibrated inputs;
  // unknown (never frozen) when either input is not fresh.
  float dew_point() const {
    if (humidity_state_ != CHANNEL_FRESH || temperature_state_ != CHANNEL_FRESH)
      return NAN;
    const float a = 17.27f;
    const float b = 237.7f;
    const float alpha = ((a * temperature_) / (b + temperature_)) +
                        std::log(humidity_ / 100.0f);
    return (b * alpha) / (a - alpha);
  }

  // Humidity rate of rise (%/min) over the recent sample window; NAN
  // until two sufficiently spaced samples exist or when humidity is not
  // fresh.
  float humidity_rate() const {
    return humidity_state_ == CHANNEL_FRESH ? rate_pct_per_min_ : NAN;
  }

  bool humidity_fresh() const { return humidity_state_ == CHANNEL_FRESH; }
  bool temperature_fresh() const { return temperature_state_ == CHANNEL_FRESH; }
  bool voc_fresh() const {
    return pollutants_.pollutant_fresh(airiq::POLLUTANT_VOC);
  }
  bool nox_fresh() const {
    return pollutants_.pollutant_fresh(airiq::POLLUTANT_NOX);
  }

  float humidity_data_age_s(uint32_t now_ms) const {
    if (!humidity_seen_) return NAN;
    return elapsed(humidity_last_ms_, now_ms) / 1000.0f;
  }
  float voc_data_age_s(uint32_t now_ms) const {
    return pollutants_.pollutant_data_age_s(airiq::POLLUTANT_VOC, now_ms);
  }

  // --- state outputs
  // -------------------------------------------------------------------
  bool shower_active() const { return shower_active_; }
  float clearing_minutes_remaining() const { return clearing_remaining_min_; }
  int mould_risk() const { return mould_risk_; }
  bool mould_warning() const { return mould_risk_ >= 2; }
  bool odour() const {
    return (voc_fresh() &&
            pollutants_.severity(airiq::POLLUTANT_VOC) >=
                airiq::SEVERITY_FAIR &&
            pollutants_.severity(airiq::POLLUTANT_VOC) <=
                airiq::SEVERITY_VERY_POOR) ||
           (nox_fresh() &&
            pollutants_.severity(airiq::POLLUTANT_NOX) >=
                airiq::SEVERITY_FAIR &&
            pollutants_.severity(airiq::POLLUTANT_NOX) <=
                airiq::SEVERITY_VERY_POOR);
  }
  airiq::AirQuality air_quality() const { return pollutants_.air_quality(); }
  Demand demand() const { return demand_; }
  Reason reason() const { return reason_; }
  bool ventilation_needed() const {
    return demand_ == DEMAND_SOON || demand_ == DEMAND_NOW;
  }
  int fan_percent() const { return fan_percent_; }

  // VentIQ module health: the embedded canonical engine over the
  // board's own verifiable channels (SGP41 VOC/NOx) ONLY. The
  // RoomIQ-owned humidity/temperature inputs NEVER participate — their
  // loss degrades the ventilation service, not this module.
  airiq::Health health() const { return pollutants_.health(); }

  // --- legacy compatibility strings (semantic upgrade — documented)
  // --------------------- Drive the preserved pre-framework text entities from
  // the canonical model instead of duplicated ad-hoc formulas.
  const char *legacy_status() const {
    if (shower_active_) return "Shower in progress";
    if (clearing_active_) return "Post-shower ventilation";
    if (humidity_state_ != CHANNEL_FRESH && !voc_fresh() && !nox_fresh())
      return "Waiting for sensor...";
    if (odour()) return "Odor detected";
    if (mould_risk_ >= 2) return "Mold risk - ventilate!";
    if (humidity_high_) return "Elevated humidity";
    return "Normal";
  }
  const char *legacy_mould_status() const {
    switch (mould_risk_) {
      case 0:
        return "No risk";
      case 1:
        return "Low risk";
      case 2:
        return "Medium risk - ventilate";
      default:
        return "High risk - action needed";
    }
  }
  const char *legacy_ventilation_advice() const {
    if (fan_percent_ == 0) return "No ventilation needed";
    if (fan_percent_ <= 30) return "Light ventilation recommended";
    if (fan_percent_ <= 50) return "Moderate ventilation recommended";
    if (fan_percent_ <= 70) return "Good ventilation needed";
    return "Maximum ventilation needed";
  }
  const char *legacy_air_quality_status() const {
    // Canonical severity vocabulary mapped onto the legacy entity
    // (documented semantic upgrade; the legacy "Excellent" band and its
    // duplicated ad-hoc thresholds are retired).
    airiq::Severity worst = airiq::SEVERITY_INITIALISING;
    bool any_fresh = false;
    if (voc_fresh()) {
      worst = pollutants_.severity(airiq::POLLUTANT_VOC);
      any_fresh = true;
    }
    if (nox_fresh()) {
      const airiq::Severity nox_severity =
          pollutants_.severity(airiq::POLLUTANT_NOX);
      if (!any_fresh || nox_severity > worst) worst = nox_severity;
      any_fresh = true;
    }
    if (!any_fresh) {
      return pollutants_.air_quality() == airiq::AIR_QUALITY_INITIALISING
                 ? "Waiting for sensor..."
                 : "Unavailable";
    }
    switch (worst) {
      case airiq::SEVERITY_GOOD:
        return "Good";
      case airiq::SEVERITY_FAIR:
        return "Fair";
      case airiq::SEVERITY_POOR:
        return "Poor";
      case airiq::SEVERITY_VERY_POOR:
        return "Very Poor";
      default:
        return "Waiting for sensor...";
    }
  }

 private:
  enum ChannelState {
    CHANNEL_INIT = 0,
    CHANNEL_FRESH = 1,
    CHANNEL_MISSING = 2,
  };

  static uint32_t elapsed(uint32_t since_ms, uint32_t now_ms) {
    return now_ms - since_ms;  // unsigned arithmetic handles wrap-around
  }
  static bool valid_pct(float value) {
    return !std::isnan(value) && value >= 0.0f && value <= 100.0f;
  }
  void ensure_started(uint32_t now_ms) {
    if (!started_) begin(now_ms);
  }

  ChannelState channel_state(uint32_t now_ms, bool seen, uint32_t last_ms,
                             uint32_t warmup_ms, uint32_t stale_ms) const {
    if (!seen) {
      return elapsed(start_ms_, now_ms) < warmup_ms ? CHANNEL_INIT
                                                    : CHANNEL_MISSING;
    }
    return elapsed(last_ms, now_ms) <= stale_ms ? CHANNEL_FRESH
                                                : CHANNEL_MISSING;
  }

  // Recent humidity samples for the rate-of-rise calculation.
  void push_humidity_sample(uint32_t now_ms, float pct) {
    sample_t_[sample_head_] = now_ms;
    sample_v_[sample_head_] = pct;
    sample_head_ = (sample_head_ + 1) % SAMPLE_SLOTS;
    if (sample_count_ < SAMPLE_SLOTS) sample_count_++;
  }

  void update_rate() {
    if (humidity_state_ != CHANNEL_FRESH || sample_count_ < 2) {
      rate_pct_per_min_ = NAN;
      return;
    }
    // Compare the newest sample against the OLDEST retained sample that
    // is still inside the rate window and at least MIN_SPAN old —
    // deterministic and robust against sample-cadence jitter.
    const int newest = (sample_head_ + SAMPLE_SLOTS - 1) % SAMPLE_SLOTS;
    const uint32_t t_new = sample_t_[newest];
    const float v_new = sample_v_[newest];
    bool found = false;
    uint32_t t_ref = 0;
    float v_ref = 0.0f;
    for (int i = 1; i < sample_count_; i++) {
      const int idx = (newest + SAMPLE_SLOTS - i) % SAMPLE_SLOTS;
      const uint32_t age = elapsed(sample_t_[idx], t_new);
      if (age > RATE_WINDOW_MS) break;
      if (age >= RATE_MIN_SPAN_MS) {
        t_ref = sample_t_[idx];
        v_ref = sample_v_[idx];
        found = true;  // keep going: the oldest in-window sample wins
      }
    }
    if (!found) {
      rate_pct_per_min_ = NAN;
      return;
    }
    const float span_min = elapsed(t_ref, t_new) / 60000.0f;
    rate_pct_per_min_ = (v_new - v_ref) / span_min;
  }

  void update_shower(uint32_t now_ms) {
    if (!shower_detection_enabled_) {
      shower_active_ = false;
      return;
    }
    if (humidity_state_ != CHANNEL_FRESH) {
      // No humidity evidence: an active shower claim cannot be
      // maintained honestly.
      shower_active_ = false;
      return;
    }
    if (!shower_active_) {
      // Re-arm the absolute trigger only after humidity has fallen back
      // below the start threshold — a timed-out (still saturated)
      // bathroom must not immediately re-claim "shower".
      if (!absolute_trigger_armed_ && humidity_ < shower_threshold_pct_)
        absolute_trigger_armed_ = true;
      const bool rate_trigger = !std::isnan(rate_pct_per_min_) &&
                                rate_pct_per_min_ >= shower_rate_threshold_;
      const bool absolute_trigger =
          absolute_trigger_armed_ && humidity_ >= shower_threshold_pct_;
      if (rate_trigger || absolute_trigger) {
        shower_active_ = true;
        shower_start_ms_ = now_ms;
        absolute_trigger_armed_ = false;
      }
      return;
    }
    // Active shower: end on falling humidity, or time out (a bathroom
    // that stays saturated for longer than the max window is a
    // sustained-damp situation, not an hour-long shower claim).
    const bool fallen =
        humidity_ < (shower_threshold_pct_ - shower_end_delta_pct_) &&
        !std::isnan(rate_pct_per_min_) && rate_pct_per_min_ < 0.0f;
    const bool timed_out = elapsed(shower_start_ms_, now_ms) >
                           (uint32_t)(shower_max_minutes_ * 60000.0f);
    if (fallen || timed_out) {
      shower_active_ = false;
      clearing_until_ms_ = now_ms + (uint32_t)(clearing_minutes_ * 60000.0f);
    }
  }

  void update_clearing(uint32_t now_ms) {
    if (clearing_until_ms_ != 0 && (int32_t)(clearing_until_ms_ - now_ms) > 0) {
      clearing_active_ = true;
      clearing_remaining_min_ = (clearing_until_ms_ - now_ms) / 60000.0f;
    } else {
      clearing_active_ = false;
      clearing_remaining_min_ = 0.0f;
      clearing_until_ms_ = 0;
    }
  }

  void update_mould(uint32_t now_ms) {
    // Honest accumulation: only fresh humidity evidence moves the
    // accumulator (in either direction). No data = frozen, no claim.
    const uint32_t dt = elapsed(last_accum_ms_, now_ms);
    last_accum_ms_ = now_ms;
    if (humidity_state_ == CHANNEL_FRESH) {
      if (humidity_ >= mould_threshold_pct_) {
        wet_ms_ += dt;
      } else {
        wet_ms_ = 0;
      }
    }
    const float dur_ms = mould_duration_minutes_ * 60000.0f;
    if (wet_ms_ >= (uint32_t)(2.0f * dur_ms)) {
      mould_risk_ = 3;
    } else if (wet_ms_ >= (uint32_t)dur_ms) {
      mould_risk_ = 2;
    } else if (wet_ms_ >= (uint32_t)(0.5f * dur_ms)) {
      mould_risk_ = 1;
    } else {
      mould_risk_ = 0;
    }
  }

  void update_humidity_high() {
    if (humidity_state_ != CHANNEL_FRESH) {
      humidity_high_ = false;  // no data, no claim
      return;
    }
    if (humidity_high_) {
      if (humidity_ < humidity_high_pct_ - humidity_hysteresis_pct_)
        humidity_high_ = false;
    } else {
      if (humidity_ >= humidity_high_pct_) humidity_high_ = true;
    }
  }

  void update_forced(uint32_t now_ms) {
    if (forced_active_ && (int32_t)(forced_until_ms_ - now_ms) <= 0)
      forced_active_ = false;
  }

  void update_demand() {
    // Fixed priority ladder — deterministic and explainable. One reason,
    // the highest-priority active one.
    if (forced_active_) {
      set_demand(DEMAND_NOW, REASON_REQUESTED);
      fan_percent_ = 100;
      return;
    }
    const airiq::AirQuality aq = pollutants_.air_quality();
    const bool aq_usable =
        aq == airiq::AIR_QUALITY_GOOD || aq == airiq::AIR_QUALITY_FAIR ||
        aq == airiq::AIR_QUALITY_POOR || aq == airiq::AIR_QUALITY_VERY_POOR;
    const bool humidity_usable = humidity_state_ == CHANNEL_FRESH;
    if (!aq_usable && !humidity_usable) {
      const bool initialising = humidity_state_ == CHANNEL_INIT ||
                                aq == airiq::AIR_QUALITY_INITIALISING;
      if (initialising) {
        set_demand(DEMAND_INITIALISING, REASON_INITIALISING);
      } else {
        set_demand(DEMAND_UNAVAILABLE, REASON_UNAVAILABLE);
      }
      fan_percent_ = 0;
      return;
    }
    if (shower_active_) {
      set_demand(DEMAND_NOW, REASON_SHOWER);
      fan_percent_ = 100;
      return;
    }
    if (clearing_active_) {
      // Very poor air still outranks the clearing window.
      if (aq == airiq::AIR_QUALITY_VERY_POOR) {
        set_demand(DEMAND_NOW, REASON_AIR_QUALITY);
        fan_percent_ = 100;
        return;
      }
      set_demand(DEMAND_SOON, REASON_CLEARING);
      fan_percent_ = 70;
      return;
    }
    if (aq == airiq::AIR_QUALITY_VERY_POOR) {
      set_demand(DEMAND_NOW, REASON_AIR_QUALITY);
      fan_percent_ = 100;
      return;
    }
    if (mould_risk_ >= 3) {
      set_demand(DEMAND_NOW, REASON_MOULD);
      fan_percent_ = 100;
      return;
    }
    if (mould_risk_ >= 2) {
      set_demand(DEMAND_SOON, REASON_MOULD);
      fan_percent_ = 50;
      return;
    }
    if (aq == airiq::AIR_QUALITY_POOR) {
      set_demand(DEMAND_SOON, REASON_AIR_QUALITY);
      fan_percent_ = 50;
      return;
    }
    if (odour()) {
      set_demand(DEMAND_SOON, REASON_ODOUR);
      fan_percent_ = 50;
      return;
    }
    if (humidity_high_) {
      set_demand(DEMAND_SOON, REASON_HUMIDITY);
      fan_percent_ = 30;
      return;
    }
    set_demand(DEMAND_NONE, REASON_NONE);
    fan_percent_ = 0;
  }

  void set_demand(Demand demand, Reason reason) {
    demand_ = demand;
    reason_ = reason;
  }

  // The embedded canonical pollutant engine (single source of VOC/NOx
  // severity truth — see the header notes above).
  airiq::AirIQEngine pollutants_;

  // ventilation heuristics (PROVISIONAL defaults; substitution/number-driven)
  float shower_threshold_pct_ = 75.0f;
  float shower_rate_threshold_ = 5.0f;  // %/min
  float shower_end_delta_pct_ = 10.0f;  // end below threshold - delta
  float shower_max_minutes_ = 60.0f;
  float clearing_minutes_ = 15.0f;
  float mould_threshold_pct_ = 65.0f;
  float mould_duration_minutes_ = 30.0f;
  float humidity_high_pct_ = 60.0f;
  float humidity_hysteresis_pct_ = 2.0f;

  // freshness windows (canonical inputs arrive ~30 s apart; provisional)
  uint32_t humidity_warmup_ms_ = 90000;
  uint32_t humidity_stale_ms_ = 90000;
  uint32_t temperature_warmup_ms_ = 90000;
  uint32_t temperature_stale_ms_ = 90000;

  // lifecycle
  bool started_ = false;
  uint32_t start_ms_ = 0;

  // canonical environmental inputs (RoomIQ-owned)
  float humidity_ = NAN;
  bool humidity_seen_ = false;
  uint32_t humidity_last_ms_ = 0;
  int humidity_state_ = CHANNEL_INIT;
  float temperature_ = NAN;
  bool temperature_seen_ = false;
  uint32_t temperature_last_ms_ = 0;
  int temperature_state_ = CHANNEL_INIT;

  // humidity rate-of-rise window
  static const int SAMPLE_SLOTS = 12;
  static const uint32_t RATE_WINDOW_MS = 180000;   // consider samples <= 3 min
  static const uint32_t RATE_MIN_SPAN_MS = 20000;  // need >= 20 s of span
  uint32_t sample_t_[SAMPLE_SLOTS] = {};
  float sample_v_[SAMPLE_SLOTS] = {};
  int sample_head_ = 0;
  int sample_count_ = 0;
  float rate_pct_per_min_ = NAN;

  // shower / clearing state
  bool shower_detection_enabled_ = true;
  bool absolute_trigger_armed_ = true;
  bool shower_active_ = false;
  uint32_t shower_start_ms_ = 0;
  uint32_t clearing_until_ms_ = 0;
  bool clearing_active_ = false;
  float clearing_remaining_min_ = 0.0f;

  // damp / mould accumulation
  uint32_t wet_ms_ = 0;
  uint32_t last_accum_ms_ = 0;
  int mould_risk_ = 0;

  // humidity-high advice state (with release hysteresis)
  bool humidity_high_ = false;

  // manual request
  bool forced_active_ = false;
  uint32_t forced_until_ms_ = 0;

  // outputs
  Demand demand_ = DEMAND_INITIALISING;
  Reason reason_ = REASON_INITIALISING;
  int fan_percent_ = 0;
};

// Accessor for the firmware's single engine instance. ESPHome emits
// `esphome: includes:` headers AFTER the globals storage declarations in
// the generated main.cpp, so a custom-class `globals:` entry cannot name
// this type; production lambdas share this function-local static instead
// (constructed on first use). Tests instantiate their own VentIQEngine
// objects directly.
inline VentIQEngine &global_engine() {
  static VentIQEngine engine;
  return engine;
}

}  // namespace ventiq
}  // namespace sense360

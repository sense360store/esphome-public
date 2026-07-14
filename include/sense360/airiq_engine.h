#pragma once

// ============================================================================
// AIRIQ-FRAMEWORK-001 — canonical AirIQ indoor-air-quality engine
// ============================================================================
// The single implementation of the Sense360 AirIQ air-quality service.
// It is compiled BOTH into production firmware (via `esphome: includes:` in
// packages/features/airiq_framework.yaml) and into the deterministic
// simulation tests (tests/unit/test_airiq_engine.cpp) so the tested logic
// and the shipped logic can never drift.
//
// What it owns (the platform's single source of pollutant truth — VentIQ,
// Pure, Zones, Home Assistant and future mobile applications consume these
// outputs instead of duplicating pollutant threshold logic):
//   * Individual pollutant values with honest units — CO2 in ppm (SCD41),
//     VOC and NOx as RELATIVE indices (SGP41 — an index is NEVER presented
//     as a ppm/ppb concentration), PM2.5/PM1/PM4/PM10 in µg/m³ (SPS30).
//   * Per-channel freshness — a value is usable only after a real, valid
//     update inside its stale window; stale or missing data is never
//     interpreted as a current reading.
//   * Independent per-sensor warm-up windows — one arbitrary shared
//     warm-up period is deliberately NOT used.
//   * Per-pollutant severity (Good / Fair / Poor / Very poor) from
//     PROVISIONAL indoor-air-quality heuristics, worsening immediately
//     and improving with hysteresis so states never flap.
//   * The headline Air Quality state — a transparent WORST-pollutant
//     model (accepted owner decision): one severe pollutant is never
//     averaged away; no blended proprietary score; no AQI claim (no
//     recognised AQI standard is implemented).
//   * The customer Recommendation — deterministic and explainable:
//     ventilation-responsive pollutants (CO2, VOC, NOx) drive Ventilate
//     soon/now; particulates and the gas slots drive the conservative
//     "Check pollution source" (outdoor air quality is unknown, so
//     unconditional ventilation advice for PM would be dishonest).
//   * Module health — Initialising / Available / Degraded / Unavailable
//     from real freshness evidence over the EXPECTED pollutant channels
//     only (configuration-driven; an intentionally absent optional sensor
//     never degrades anything). Fault is an engine contract with NO
//     production producer today.
//
// Honesty rules baked into this engine:
//   * There is NO "AirIQ Base" / "AirIQ Pro" product axis (the taxonomy is
//     flat, one SKU per product). Expected-channel membership comes from
//     set_expected(), driven by composition substitutions.
//   * Pressure is NOT S360-210 product hardware: no pressure part exists
//     on the verified R4 schematic, the BOM or the hardware catalog. The
//     BMP390 @0x77 still compiled by the board package is FIRMWARE /
//     CATALOG drift, so the pressure channel here is an UNWIRED contract
//     only — no production input, no customer entity, and NEVER a
//     participant in Air Quality severity, recommendation or health.
//   * The MiCS-4514 (PCB-mounted, schematic U4 with its STM8 bridge U5)
//     reducing / oxidising channels are part of the architecture as
//     DIAGNOSTIC-ONLY inputs: they never classify, never drive the
//     headline, never affect health, and no CO / NO2 concentration is
//     ever claimed. Promotion to a customer pollutant requires the
//     calibration evidence documented in
//     docs/architecture/sense360-airiq-framework.md; no confidence value
//     is fabricated here.
//   * The formaldehyde slot (SFA40 — footprint present on the verified
//     schematic as U2; production population an unresolved conflict,
//     HW-PINMAP-210-FOLLOWUP) and the ozone slot (SEN0321 / ZE27-O3 — an
//     EXTERNAL sensor/interface into the STM8 stage per the verified
//     schematic; no driver) exist as contract channels with
//     expected=false everywhere today: a composition that never fitted
//     them can never be degraded — or alarmed — by them.
//   * All thresholds are PROVISIONAL engineering heuristics pending bench
//     and customer validation. They are never medical, health or
//     regulatory claims; the PM2.5 bands are derived from published US
//     EPA breakpoints used as indoor heuristics only — this is NOT a
//     regulatory AQI implementation.
//
// Nothing in this header claims hardware validation.
// ============================================================================

#include <cmath>
#include <cstdint>

namespace sense360 {
namespace airiq {

// Pollutants that can participate in the worst-pollutant model. Pressure
// is deliberately NOT a pollutant; the MiCS channels are deliberately NOT
// pollutants until calibration evidence justifies promotion.
enum Pollutant {
  POLLUTANT_CO2 = 0,
  POLLUTANT_VOC = 1,
  POLLUTANT_NOX = 2,
  POLLUTANT_PM25 = 3,
  POLLUTANT_HCHO = 4,
  POLLUTANT_O3 = 5,
  POLLUTANT_COUNT = 6,
};

inline const char *pollutant_to_string(Pollutant pollutant) {
  switch (pollutant) {
    case POLLUTANT_CO2:
      return "CO2";
    case POLLUTANT_VOC:
      return "VOC";
    case POLLUTANT_NOX:
      return "NOx";
    case POLLUTANT_PM25:
      return "PM2.5";
    case POLLUTANT_HCHO:
      return "Formaldehyde";
    case POLLUTANT_O3:
      return "Ozone";
    case POLLUTANT_COUNT:
      break;
  }
  return "Unknown";
}

// Per-pollutant severity (customer vocabulary, single-sourced here).
enum Severity {
  SEVERITY_INITIALISING = 0,
  SEVERITY_GOOD = 1,
  SEVERITY_FAIR = 2,
  SEVERITY_POOR = 3,
  SEVERITY_VERY_POOR = 4,
  SEVERITY_UNAVAILABLE = 5,
};

inline const char *severity_to_string(Severity severity) {
  switch (severity) {
    case SEVERITY_INITIALISING:
      return "Initialising";
    case SEVERITY_GOOD:
      return "Good";
    case SEVERITY_FAIR:
      return "Fair";
    case SEVERITY_POOR:
      return "Poor";
    case SEVERITY_VERY_POOR:
      return "Very poor";
    case SEVERITY_UNAVAILABLE:
      return "Unavailable";
  }
  return "Unavailable";
}

// The ONE headline Air Quality state (worst valid pollutant severity).
enum AirQuality {
  AIR_QUALITY_INITIALISING = 0,
  AIR_QUALITY_GOOD = 1,
  AIR_QUALITY_FAIR = 2,
  AIR_QUALITY_POOR = 3,
  AIR_QUALITY_VERY_POOR = 4,
  AIR_QUALITY_UNAVAILABLE = 5,
};

inline const char *air_quality_to_string(AirQuality state) {
  switch (state) {
    case AIR_QUALITY_INITIALISING:
      return "Initialising";
    case AIR_QUALITY_GOOD:
      return "Good";
    case AIR_QUALITY_FAIR:
      return "Fair";
    case AIR_QUALITY_POOR:
      return "Poor";
    case AIR_QUALITY_VERY_POOR:
      return "Very poor";
    case AIR_QUALITY_UNAVAILABLE:
      return "Unavailable";
  }
  return "Unavailable";
}

// The ONE customer Recommendation. Deterministic, explainable, local-only
// and conservative: outdoor air quality is unknown, so no absolute health
// advice is ever produced.
enum Recommendation {
  RECOMMENDATION_INITIALISING = 0,
  RECOMMENDATION_NO_ACTION = 1,
  RECOMMENDATION_VENTILATE_SOON = 2,
  RECOMMENDATION_VENTILATE_NOW = 3,
  RECOMMENDATION_CHECK_SOURCE = 4,
  RECOMMENDATION_UNAVAILABLE = 5,
};

inline const char *recommendation_to_string(Recommendation recommendation) {
  switch (recommendation) {
    case RECOMMENDATION_INITIALISING:
      return "Sensor initialising";
    case RECOMMENDATION_NO_ACTION:
      return "No action needed";
    case RECOMMENDATION_VENTILATE_SOON:
      return "Ventilate soon";
    case RECOMMENDATION_VENTILATE_NOW:
      return "Ventilate now";
    case RECOMMENDATION_CHECK_SOURCE:
      return "Check pollution source";
    case RECOMMENDATION_UNAVAILABLE:
      return "Unavailable";
  }
  return "Unavailable";
}

// Module-health values — the Core-Framework reserved runtime vocabulary
// (config/core-framework.json module_status.reserved_values).
enum Health {
  HEALTH_INITIALISING = 0,
  HEALTH_AVAILABLE = 1,
  HEALTH_DEGRADED = 2,
  HEALTH_UNAVAILABLE = 3,
  HEALTH_FAULT = 4,
};

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

class AirIQEngine {
 public:
  AirIQEngine() {
    // Expected-channel defaults mirror the PCB-MOUNTED compiled S360-210
    // sensors only: SCD41 CO2 + SGP41 VOC/NOx. EXTERNAL attachments are
    // opt-in per composition: the SPS30 PM module (J2) has a compiled
    // driver but NO authoritative kit/SOT record declares it as supplied
    // — an undeclared absent module must never degrade health — and the
    // formaldehyde / ozone slots have no driver and unresolved fitment.
    // A composition that declares an attachment calls set_expected().
    expected_[POLLUTANT_CO2] = true;
    expected_[POLLUTANT_VOC] = true;
    expected_[POLLUTANT_NOX] = true;
    expected_[POLLUTANT_PM25] = false;
    expected_[POLLUTANT_HCHO] = false;
    expected_[POLLUTANT_O3] = false;

    // PROVISIONAL severity thresholds (fair / poor / very poor lower
    // bounds) and improvement hysteresis — indoor-air-quality heuristics
    // pending bench + customer validation, never medical or regulatory
    // values. Sources are documented in the architecture doc:
    //   CO2  : accepted owner comfort/ventilation bands (800/1000/1500).
    //   VOC  : relative-index heuristic informed by Sensirion's guidance
    //          that 100 is the conditioning average (150/250/400).
    //   NOx  : relative-index heuristic; the NOx index baseline is 1 and
    //          values above ~100 indicate elevated NOx (100/200/300).
    //   PM2.5: derived from published US EPA PM2.5 breakpoints, used as
    //          provisional indoor heuristics only (12/35.5/55.5).
    //   HCHO : provisional ppb bands referencing the WHO indoor guideline
    //          magnitude (~81 ppb) — contract slot only (80/120/250).
    //   O3   : provisional ppb bands — contract slot only (50/70/120).
    set_thresholds(POLLUTANT_CO2, 800.0f, 1000.0f, 1500.0f);
    set_hysteresis(POLLUTANT_CO2, 50.0f);
    set_thresholds(POLLUTANT_VOC, 150.0f, 250.0f, 400.0f);
    set_hysteresis(POLLUTANT_VOC, 10.0f);
    set_thresholds(POLLUTANT_NOX, 100.0f, 200.0f, 300.0f);
    set_hysteresis(POLLUTANT_NOX, 10.0f);
    set_thresholds(POLLUTANT_PM25, 12.0f, 35.5f, 55.5f);
    set_hysteresis(POLLUTANT_PM25, 3.0f);
    set_thresholds(POLLUTANT_HCHO, 80.0f, 120.0f, 250.0f);
    set_hysteresis(POLLUTANT_HCHO, 10.0f);
    set_thresholds(POLLUTANT_O3, 50.0f, 70.0f, 120.0f);
    set_hysteresis(POLLUTANT_O3, 5.0f);

    // PROVISIONAL per-sensor freshness windows (ms). Warm-up = how long
    // after boot the first valid sample may honestly take (data
    // availability only — NEVER an accuracy claim; the SGP41 index keeps
    // adapting its baseline for much longer, which is documented, not
    // hidden). Stale = three missed update intervals of the compiled
    // sensor configuration.
    set_warmup_ms(POLLUTANT_CO2, 60000);
    set_stale_ms(POLLUTANT_CO2, 90000);
    set_warmup_ms(POLLUTANT_VOC, 120000);
    set_stale_ms(POLLUTANT_VOC, 90000);
    set_warmup_ms(POLLUTANT_NOX, 120000);
    set_stale_ms(POLLUTANT_NOX, 90000);
    set_warmup_ms(POLLUTANT_PM25, 60000);
    set_stale_ms(POLLUTANT_PM25, 90000);
    set_warmup_ms(POLLUTANT_HCHO, 60000);
    set_stale_ms(POLLUTANT_HCHO, 90000);
    set_warmup_ms(POLLUTANT_O3, 120000);
    set_stale_ms(POLLUTANT_O3, 90000);
  }

  // --- composition configuration (substitution-driven; no Base/Pro axis) ----
  void set_expected(Pollutant pollutant, bool expected) {
    if (pollutant < POLLUTANT_COUNT) expected_[pollutant] = expected;
  }
  bool expected(Pollutant pollutant) const {
    return pollutant < POLLUTANT_COUNT && expected_[pollutant];
  }

  // --- provisional thresholds (centralised here; no downstream duplicates) --
  void set_thresholds(Pollutant pollutant, float fair, float poor,
                      float very_poor) {
    if (pollutant >= POLLUTANT_COUNT) return;
    fair_[pollutant] = fair;
    poor_[pollutant] = poor;
    very_poor_[pollutant] = very_poor;
  }
  // Improvement hysteresis: worsening classifies immediately; improving
  // requires clearing the band boundary by this margin (no flapping).
  void set_hysteresis(Pollutant pollutant, float margin) {
    if (pollutant >= POLLUTANT_COUNT) return;
    hysteresis_[pollutant] =
        (std::isnan(margin) || margin < 0.0f) ? 0.0f : margin;
  }

  // --- per-sensor freshness windows (independent; provisional) --------------
  void set_warmup_ms(Pollutant pollutant, uint32_t ms) {
    if (pollutant < POLLUTANT_COUNT) warmup_ms_[pollutant] = ms;
  }
  void set_stale_ms(Pollutant pollutant, uint32_t ms) {
    if (pollutant < POLLUTANT_COUNT) stale_ms_[pollutant] = ms;
  }
  void set_pressure_warmup_ms(uint32_t ms) { pressure_warmup_ms_ = ms; }
  void set_pressure_stale_ms(uint32_t ms) { pressure_stale_ms_ = ms; }
  void set_mics_stale_ms(uint32_t ms) { mics_stale_ms_ = ms; }

  // Explicit persistent fault input. RESERVED: no composed component
  // exposes a supported AirIQ fault signal today, so production YAML
  // never sets this; the engine contract exists (and is tested) for a
  // future real signal. Ordinary staleness NEVER produces Fault.
  void set_fault(bool fault) { fault_ = fault; }

  // --- lifecycle -------------------------------------------------------------
  void begin(uint32_t now_ms) {
    started_ = true;
    start_ms_ = now_ms;
  }

  // --- inputs (real sensor update callbacks — the freshness signal) ----------
  // A NaN or negative sample is an INVALID update: it never refreshes the
  // channel and never becomes a value.
  void input_co2(uint32_t now_ms, float ppm) {
    input_pollutant(POLLUTANT_CO2, now_ms, ppm);
  }
  // SGP41 outputs are RELATIVE indices (dimensionless); they are consumed
  // and re-published as indices, never converted into concentrations.
  void input_voc(uint32_t now_ms, float index) {
    input_pollutant(POLLUTANT_VOC, now_ms, index);
  }
  void input_nox(uint32_t now_ms, float index) {
    input_pollutant(POLLUTANT_NOX, now_ms, index);
  }
  void input_pm2_5(uint32_t now_ms, float ugm3) {
    input_pollutant(POLLUTANT_PM25, now_ms, ugm3);
  }
  void input_hcho(uint32_t now_ms, float ppb) {
    input_pollutant(POLLUTANT_HCHO, now_ms, ppb);
  }
  void input_o3(uint32_t now_ms, float ppb) {
    input_pollutant(POLLUTANT_O3, now_ms, ppb);
  }

  // Extra PM fractions ride the shared SPS30 particulate freshness
  // channel (same physical measurement as PM2.5).
  void input_pm1(uint32_t now_ms, float ugm3) {
    ensure_started(now_ms);
    if (invalid(ugm3)) return;
    pm1_ = ugm3;
    pm1_seen_ = true;
  }
  void input_pm4(uint32_t now_ms, float ugm3) {
    ensure_started(now_ms);
    if (invalid(ugm3)) return;
    pm4_ = ugm3;
    pm4_seen_ = true;
  }
  void input_pm10(uint32_t now_ms, float ugm3) {
    ensure_started(now_ms);
    if (invalid(ugm3)) return;
    pm10_ = ugm3;
    pm10_seen_ = true;
  }

  // Pressure: an UNWIRED contract channel — NEVER a pollutant, never in
  // health, and no production YAML feeds it today (the compiled BMP390 is
  // firmware/catalog drift; see the header notes above).
  void input_pressure(uint32_t now_ms, float hpa) {
    ensure_started(now_ms);
    if (std::isnan(hpa) || hpa <= 0.0f) return;
    pressure_ = hpa;
    pressure_seen_ = true;
    pressure_last_ms_ = now_ms;
  }

  // MiCS-4514 diagnostic-only channels (units unverified — raw/derived
  // values from a future STM8 readout path). They never classify and
  // never touch headline or health; promotion requires calibration
  // evidence (see the architecture doc).
  void input_mics_reducing(uint32_t now_ms, float value) {
    ensure_started(now_ms);
    if (std::isnan(value)) return;
    mics_red_ = value;
    mics_red_seen_ = true;
    mics_red_last_ms_ = now_ms;
  }
  void input_mics_oxidising(uint32_t now_ms, float value) {
    ensure_started(now_ms);
    if (std::isnan(value)) return;
    mics_ox_ = value;
    mics_ox_seen_ = true;
    mics_ox_last_ms_ = now_ms;
  }

  // --- evaluation
  // -------------------------------------------------------------
  void evaluate(uint32_t now_ms) {
    ensure_started(now_ms);

    for (int i = 0; i < POLLUTANT_COUNT; i++) {
      channel_state_[i] = channel_state(now_ms, seen_[i], last_ms_[i],
                                        warmup_ms_[i], stale_ms_[i]);
      update_severity(static_cast<Pollutant>(i));
    }
    pressure_state_ = channel_state(now_ms, pressure_seen_, pressure_last_ms_,
                                    pressure_warmup_ms_, pressure_stale_ms_);
    mics_red_fresh_ =
        mics_red_seen_ && elapsed(mics_red_last_ms_, now_ms) <= mics_stale_ms_;
    mics_ox_fresh_ =
        mics_ox_seen_ && elapsed(mics_ox_last_ms_, now_ms) <= mics_stale_ms_;

    update_air_quality();
    update_recommendation();
    update_health();
  }

  // --- value outputs (NAN unless the channel is fresh)
  // --------------------------
  float co2() const { return pollutant_value(POLLUTANT_CO2); }
  float voc() const { return pollutant_value(POLLUTANT_VOC); }
  float nox() const { return pollutant_value(POLLUTANT_NOX); }
  float pm2_5() const { return pollutant_value(POLLUTANT_PM25); }
  float hcho() const { return pollutant_value(POLLUTANT_HCHO); }
  float o3() const { return pollutant_value(POLLUTANT_O3); }

  float pm1() const {
    return (pm1_seen_ && channel_state_[POLLUTANT_PM25] == CHANNEL_FRESH) ? pm1_
                                                                          : NAN;
  }
  float pm4() const {
    return (pm4_seen_ && channel_state_[POLLUTANT_PM25] == CHANNEL_FRESH) ? pm4_
                                                                          : NAN;
  }
  float pm10() const {
    return (pm10_seen_ && channel_state_[POLLUTANT_PM25] == CHANNEL_FRESH)
               ? pm10_
               : NAN;
  }

  float pressure() const {
    return pressure_state_ == CHANNEL_FRESH ? pressure_ : NAN;
  }

  // MiCS diagnostics (freshness-gated on their own stale window, computed
  // by evaluate(); a stale raw channel is never left standing either).
  float mics_reducing() const { return mics_red_fresh_ ? mics_red_ : NAN; }
  float mics_oxidising() const { return mics_ox_fresh_ ? mics_ox_ : NAN; }

  bool pollutant_fresh(Pollutant pollutant) const {
    return pollutant < POLLUTANT_COUNT &&
           channel_state_[pollutant] == CHANNEL_FRESH;
  }
  bool pressure_fresh() const { return pressure_state_ == CHANNEL_FRESH; }

  // Seconds since the last valid update (diagnostics; NAN if never seen).
  float pollutant_data_age_s(Pollutant pollutant, uint32_t now_ms) const {
    if (pollutant >= POLLUTANT_COUNT || !seen_[pollutant]) return NAN;
    return elapsed(last_ms_[pollutant], now_ms) / 1000.0f;
  }
  float pressure_data_age_s(uint32_t now_ms) const {
    if (!pressure_seen_) return NAN;
    return elapsed(pressure_last_ms_, now_ms) / 1000.0f;
  }

  // --- state outputs
  // --------------------------------------------------------------
  Severity severity(Pollutant pollutant) const {
    return pollutant < POLLUTANT_COUNT ? severity_[pollutant]
                                       : SEVERITY_UNAVAILABLE;
  }
  AirQuality air_quality() const { return air_quality_; }
  Recommendation recommendation() const { return recommendation_; }
  Health health() const { return health_; }

  // The pollutant driving the current headline (worst severity; ties
  // broken by the fixed priority order CO2, VOC, NOx, PM2.5,
  // Formaldehyde, Ozone). POLLUTANT_COUNT when no pollutant drives the
  // headline (Initialising / Unavailable / all Good).
  Pollutant worst_pollutant() const { return worst_pollutant_; }

 private:
  enum ChannelState {
    CHANNEL_INIT = 0,
    CHANNEL_FRESH = 1,
    CHANNEL_MISSING = 2,
  };

  static uint32_t elapsed(uint32_t since_ms, uint32_t now_ms) {
    return now_ms - since_ms;  // unsigned arithmetic handles wrap-around
  }

  static bool invalid(float value) { return std::isnan(value) || value < 0.0f; }

  void ensure_started(uint32_t now_ms) {
    if (!started_) begin(now_ms);
  }

  void input_pollutant(Pollutant pollutant, uint32_t now_ms, float value) {
    ensure_started(now_ms);
    if (pollutant >= POLLUTANT_COUNT || invalid(value)) return;
    value_[pollutant] = value;
    seen_[pollutant] = true;
    last_ms_[pollutant] = now_ms;
  }

  float pollutant_value(Pollutant pollutant) const {
    if (pollutant >= POLLUTANT_COUNT) return NAN;
    if (channel_state_[pollutant] != CHANNEL_FRESH) return NAN;
    return value_[pollutant];
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

  // Band 0=Good, 1=Fair, 2=Poor, 3=Very poor. Worsening is immediate (a
  // severe pollutant must show at once); improving requires clearing the
  // band's lower boundary by the hysteresis margin.
  int raw_band(Pollutant p, float v) const {
    if (v < fair_[p]) return 0;
    if (v < poor_[p]) return 1;
    if (v < very_poor_[p]) return 2;
    return 3;
  }

  float band_lower(Pollutant p, int band) const {
    switch (band) {
      case 1:
        return fair_[p];
      case 2:
        return poor_[p];
      case 3:
        return very_poor_[p];
    }
    return fair_[p];
  }

  void update_severity(Pollutant p) {
    if (channel_state_[p] == CHANNEL_INIT) {
      severity_[p] = SEVERITY_INITIALISING;
      band_valid_[p] = false;
      return;
    }
    if (channel_state_[p] == CHANNEL_MISSING) {
      severity_[p] = SEVERITY_UNAVAILABLE;
      band_valid_[p] = false;
      return;
    }
    const float v = value_[p];
    const int raw = raw_band(p, v);
    if (!band_valid_[p]) {
      band_[p] = raw;
      band_valid_[p] = true;
    } else if (raw > band_[p]) {
      band_[p] = raw;  // worsening classifies immediately
    } else {
      while (raw < band_[p] && v < band_lower(p, band_[p]) - hysteresis_[p]) {
        band_[p]--;
      }
    }
    switch (band_[p]) {
      case 0:
        severity_[p] = SEVERITY_GOOD;
        return;
      case 1:
        severity_[p] = SEVERITY_FAIR;
        return;
      case 2:
        severity_[p] = SEVERITY_POOR;
        return;
    }
    severity_[p] = SEVERITY_VERY_POOR;
  }

  void update_air_quality() {
    // The headline considers EXPECTED pollutants only: a composition is
    // never judged by a sensor it does not claim to have.
    int fresh = 0, init = 0, expected_count = 0;
    Severity worst = SEVERITY_GOOD;
    Pollutant worst_p = POLLUTANT_COUNT;
    for (int i = 0; i < POLLUTANT_COUNT; i++) {
      if (!expected_[i]) continue;
      expected_count++;
      if (channel_state_[i] == CHANNEL_INIT) init++;
      if (channel_state_[i] != CHANNEL_FRESH) continue;
      fresh++;
      // Fixed priority order = enum order: the FIRST pollutant at the
      // worst severity is the deterministic driver.
      if (severity_[i] > worst) {
        worst = severity_[i];
        worst_p = static_cast<Pollutant>(i);
      }
    }
    if (expected_count == 0) {
      air_quality_ = AIR_QUALITY_UNAVAILABLE;
      worst_pollutant_ = POLLUTANT_COUNT;
      return;
    }
    if (fresh == 0) {
      // No usable pollutant data: still warming counts as Initialising
      // (a channel may yet arrive); otherwise honestly Unavailable.
      air_quality_ =
          init > 0 ? AIR_QUALITY_INITIALISING : AIR_QUALITY_UNAVAILABLE;
      worst_pollutant_ = POLLUTANT_COUNT;
      return;
    }
    switch (worst) {
      case SEVERITY_GOOD:
        air_quality_ = AIR_QUALITY_GOOD;
        break;
      case SEVERITY_FAIR:
        air_quality_ = AIR_QUALITY_FAIR;
        break;
      case SEVERITY_POOR:
        air_quality_ = AIR_QUALITY_POOR;
        break;
      case SEVERITY_VERY_POOR:
        air_quality_ = AIR_QUALITY_VERY_POOR;
        break;
      default:
        air_quality_ = AIR_QUALITY_UNAVAILABLE;
        break;
    }
    // The driver is reported for Fair and worse (explainability); for an
    // all-Good headline there is nothing to explain.
    worst_pollutant_ = (worst >= SEVERITY_FAIR) ? worst_p : POLLUTANT_COUNT;
  }

  void update_recommendation() {
    switch (air_quality_) {
      case AIR_QUALITY_INITIALISING:
        recommendation_ = RECOMMENDATION_INITIALISING;
        return;
      case AIR_QUALITY_UNAVAILABLE:
        recommendation_ = RECOMMENDATION_UNAVAILABLE;
        return;
      case AIR_QUALITY_GOOD:
      case AIR_QUALITY_FAIR:
        recommendation_ = RECOMMENDATION_NO_ACTION;
        return;
      default:
        break;
    }
    // Poor / Very poor: deterministic worst-driver rule. If ANY
    // ventilation-responsive pollutant (CO2 / VOC / NOx — ventilation
    // demonstrably reduces these) sits at the worst severity, recommend
    // ventilation (soon for Poor, now for Very poor). Otherwise the worst
    // driver is a particulate or gas slot, where outdoor air is unknown
    // and the conservative advice is to check the pollution source.
    const Severity worst =
        air_quality_ == AIR_QUALITY_POOR ? SEVERITY_POOR : SEVERITY_VERY_POOR;
    bool ventilation_driver = false;
    for (int i = 0; i < POLLUTANT_COUNT; i++) {
      if (!expected_[i] || channel_state_[i] != CHANNEL_FRESH) continue;
      if (severity_[i] != worst) continue;
      if (i == POLLUTANT_CO2 || i == POLLUTANT_VOC || i == POLLUTANT_NOX) {
        ventilation_driver = true;
        break;
      }
    }
    if (ventilation_driver) {
      recommendation_ = (air_quality_ == AIR_QUALITY_POOR)
                            ? RECOMMENDATION_VENTILATE_SOON
                            : RECOMMENDATION_VENTILATE_NOW;
    } else {
      recommendation_ = RECOMMENDATION_CHECK_SOURCE;
    }
  }

  void update_health() {
    if (fault_) {
      health_ = HEALTH_FAULT;
      return;
    }
    // Health considers the EXPECTED pollutant channels only. Pressure is
    // excluded while its part identity stays unresolved (a missing
    // never-fitted part must not degrade every device); the MiCS
    // diagnostic channels are excluded until promotion.
    int fresh = 0, init = 0, missing = 0;
    for (int i = 0; i < POLLUTANT_COUNT; i++) {
      if (!expected_[i]) continue;
      switch (channel_state_[i]) {
        case CHANNEL_FRESH:
          fresh++;
          break;
        case CHANNEL_INIT:
          init++;
          break;
        default:
          missing++;
          break;
      }
    }
    if (init > 0 && missing == 0) {
      // Startup is never reported as a fault or an outage.
      health_ = HEALTH_INITIALISING;
      return;
    }
    if (missing == 0 && fresh > 0) {
      health_ = HEALTH_AVAILABLE;
      return;
    }
    if (fresh > 0) {
      health_ = HEALTH_DEGRADED;
      return;
    }
    health_ = HEALTH_UNAVAILABLE;
  }

  // composition
  bool expected_[POLLUTANT_COUNT] = {};

  // provisional thresholds + hysteresis
  float fair_[POLLUTANT_COUNT] = {};
  float poor_[POLLUTANT_COUNT] = {};
  float very_poor_[POLLUTANT_COUNT] = {};
  float hysteresis_[POLLUTANT_COUNT] = {};

  // per-sensor freshness windows (independent, provisional)
  uint32_t warmup_ms_[POLLUTANT_COUNT] = {};
  uint32_t stale_ms_[POLLUTANT_COUNT] = {};
  uint32_t pressure_warmup_ms_ = 90000;
  uint32_t pressure_stale_ms_ = 180000;
  uint32_t mics_stale_ms_ = 90000;

  // lifecycle
  bool started_ = false;
  uint32_t start_ms_ = 0;

  // pollutant channel data
  float value_[POLLUTANT_COUNT] = {};
  bool seen_[POLLUTANT_COUNT] = {};
  uint32_t last_ms_[POLLUTANT_COUNT] = {};
  int channel_state_[POLLUTANT_COUNT] = {};

  // hysteresis band memory
  int band_[POLLUTANT_COUNT] = {};
  bool band_valid_[POLLUTANT_COUNT] = {};

  // extra PM fractions (shared SPS30 freshness)
  float pm1_ = NAN;
  bool pm1_seen_ = false;
  float pm4_ = NAN;
  bool pm4_seen_ = false;
  float pm10_ = NAN;
  bool pm10_seen_ = false;

  // pressure (never a pollutant)
  float pressure_ = NAN;
  bool pressure_seen_ = false;
  uint32_t pressure_last_ms_ = 0;
  int pressure_state_ = CHANNEL_INIT;

  // MiCS diagnostic channels (never a pollutant; promotion gated on
  // calibration evidence)
  float mics_red_ = NAN;
  bool mics_red_seen_ = false;
  uint32_t mics_red_last_ms_ = 0;
  float mics_ox_ = NAN;
  bool mics_ox_seen_ = false;
  uint32_t mics_ox_last_ms_ = 0;
  bool mics_red_fresh_ = false;
  bool mics_ox_fresh_ = false;

  // fault (reserved — no production producer)
  bool fault_ = false;

  // outputs
  Severity severity_[POLLUTANT_COUNT] = {};
  AirQuality air_quality_ = AIR_QUALITY_INITIALISING;
  Recommendation recommendation_ = RECOMMENDATION_INITIALISING;
  Health health_ = HEALTH_INITIALISING;
  Pollutant worst_pollutant_ = POLLUTANT_COUNT;
};

// Accessor for the firmware's single engine instance. ESPHome emits
// `esphome: includes:` headers AFTER the globals storage declarations in
// the generated main.cpp, so a custom-class `globals:` entry cannot name
// this type; production lambdas share this function-local static instead
// (constructed on first use). Tests instantiate their own AirIQEngine
// objects directly.
inline AirIQEngine &global_engine() {
  static AirIQEngine engine;
  return engine;
}

}  // namespace airiq
}  // namespace sense360

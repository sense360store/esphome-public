#pragma once

// ============================================================================
// ROOMIQ-FRAMEWORK-001 — canonical RoomIQ environmental engine (header-only)
// ============================================================================
// The single implementation of the Sense360 RoomIQ environmental service.
// It is compiled BOTH into production firmware (via `esphome: includes:` in
// packages/features/roomiq_framework.yaml) and into the deterministic
// simulation tests (tests/unit/test_roomiq_engine.cpp) so the tested logic
// and the shipped logic can never drift.
//
// What it owns (the platform's single source of environmental truth):
//   * Calibrated temperature / humidity / illuminance — customer offsets
//     (temperature, humidity) and a multiplier (illuminance), applied
//     EXACTLY ONCE, clamped to safe bounds; invalid calibration values
//     recover to neutral.
//   * Per-channel freshness — a value is usable only after a real, valid
//     (non-NaN) update inside the stale window; stale or missing data is
//     never interpreted as a real value.
//   * Comfort — human-friendly comfort states from calibrated temperature
//     and humidity only (accepted owner decision), with hysteresis.
//   * Brightness — human-friendly room-ambience category from calibrated
//     illuminance, with hysteresis to prevent category flapping.
//   * Environment State — one deterministic headline: severe combined
//     climate states outrank temperature discomfort, which outranks
//     humidity discomfort; notable light conditions (Dark / very bright)
//     surface only when the climate is comfortable.
//   * Darkness service — the threshold/hysteresis/staleness darkness
//     decision consumed by the LED framework (which passes its customer
//     Darkness Threshold in at runtime). One implementation; the LED
//     controller consumes the decision and never re-implements it.
//   * Module health — Initialising / Available / Degraded / Unavailable
//     from real freshness evidence only; Fault is an engine contract with
//     NO production producer (no composed component exposes a supported
//     explicit fault signal today).
//   * Legacy compatibility outputs — the pre-framework RoomIQ display
//     values (heat index, 0-100 comfort score, comfort/light status and
//     advice strings) so published Home Assistant entity ids keep working,
//     now driven by calibrated values.
//
// Honesty rules baked into this engine:
//   * All thresholds are PROVISIONAL engineering defaults / comfort
//     heuristics pending customer and bench validation. They are never
//     medical, health, lighting-standard or regulatory claims.
//   * Freshness comes from real update callbacks; a NaN sample is not a
//     valid update. Startup is Initialising, never a fault.
//   * Temperature and humidity share one physical sensor (SHT4x): their
//     shared failure shows honestly as both channels going stale together;
//     the engine still tracks them independently.
//   * The ambient-light driver is reconciled to the schematic/BOM part
//     (LTR-303ALS-01 @ 0x29 via ltr_als_ps;
//     S360-200-R4-HARDWARE-RECONCILIATION-001). This engine consumes lux
//     samples without claiming a sensor model; on-hardware measurement
//     validity remains bench work.
//
// Nothing in this header claims hardware validation.
// ============================================================================

#include <cmath>
#include <cstdint>
#include <cstring>

namespace sense360 {
namespace roomiq {

// Customer-facing Comfort values (accepted owner decision: human-friendly
// states, never a customer-facing numeric score). Strings single-sourced.
enum Comfort {
  COMFORT_INITIALISING = 0,
  COMFORT_COMFORTABLE = 1,
  COMFORT_COOL = 2,
  COMFORT_COLD = 3,
  COMFORT_WARM = 4,
  COMFORT_HOT = 5,
  COMFORT_DRY = 6,
  COMFORT_HUMID = 7,
  COMFORT_WARM_HUMID = 8,
  COMFORT_UNAVAILABLE = 9,
};

inline const char *comfort_to_string(Comfort comfort) {
  switch (comfort) {
    case COMFORT_INITIALISING:
      return "Initialising";
    case COMFORT_COMFORTABLE:
      return "Comfortable";
    case COMFORT_COOL:
      return "Cool";
    case COMFORT_COLD:
      return "Cold";
    case COMFORT_WARM:
      return "Warm";
    case COMFORT_HOT:
      return "Hot";
    case COMFORT_DRY:
      return "Dry";
    case COMFORT_HUMID:
      return "Humid";
    case COMFORT_WARM_HUMID:
      return "Warm and humid";
    case COMFORT_UNAVAILABLE:
      return "Unavailable";
  }
  return "Unavailable";
}

// Customer-facing Brightness category (room-ambience wording, never a
// lighting-standard compliance claim).
enum Brightness {
  BRIGHTNESS_INITIALISING = 0,
  BRIGHTNESS_DARK = 1,
  BRIGHTNESS_DIM = 2,
  BRIGHTNESS_NORMAL = 3,
  BRIGHTNESS_BRIGHT = 4,
  BRIGHTNESS_VERY_BRIGHT = 5,
  BRIGHTNESS_UNAVAILABLE = 6,
};

inline const char *brightness_to_string(Brightness brightness) {
  switch (brightness) {
    case BRIGHTNESS_INITIALISING:
      return "Initialising";
    case BRIGHTNESS_DARK:
      return "Dark";
    case BRIGHTNESS_DIM:
      return "Dim";
    case BRIGHTNESS_NORMAL:
      return "Normal";
    case BRIGHTNESS_BRIGHT:
      return "Bright";
    case BRIGHTNESS_VERY_BRIGHT:
      return "Very bright";
    case BRIGHTNESS_UNAVAILABLE:
      return "Unavailable";
  }
  return "Unavailable";
}

// Environment State — ONE deterministic headline. It never contradicts
// Comfort: any climate discomfort IS the headline; light conditions
// surface only when the climate is comfortable (Dark, or Bright for the
// very-bright band) or when the climate is unavailable but a notable,
// fresh light condition remains true.
enum Environment {
  ENV_INITIALISING = 0,
  ENV_COMFORTABLE = 1,
  ENV_COOL = 2,
  ENV_COLD = 3,
  ENV_WARM = 4,
  ENV_HOT = 5,
  ENV_DRY = 6,
  ENV_HUMID = 7,
  ENV_WARM_HUMID = 8,
  ENV_DARK = 9,
  ENV_BRIGHT = 10,
  ENV_UNAVAILABLE = 11,
};

inline const char *environment_to_string(Environment environment) {
  switch (environment) {
    case ENV_INITIALISING:
      return "Initialising";
    case ENV_COMFORTABLE:
      return "Comfortable";
    case ENV_COOL:
      return "Cool";
    case ENV_COLD:
      return "Cold";
    case ENV_WARM:
      return "Warm";
    case ENV_HOT:
      return "Hot";
    case ENV_DRY:
      return "Dry";
    case ENV_HUMID:
      return "Humid";
    case ENV_WARM_HUMID:
      return "Warm and humid";
    case ENV_DARK:
      return "Dark";
    case ENV_BRIGHT:
      return "Bright";
    case ENV_UNAVAILABLE:
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

// Darkness decision (the LED framework's night-automation input). UNKNOWN
// (missing / stale / NaN lux) is a first-class state distinct from
// darkness — it never activates anything.
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

class RoomIQEngine {
 public:
  // --- calibration (applied exactly once, inside this engine) --------------
  // Customer temperature offset in °C. Clamped to a safe band; NaN (an
  // invalid stored value) recovers to neutral 0.
  void set_temperature_offset(float offset_c) {
    temperature_offset_ = sanitise_offset(offset_c, 5.0f);
  }

  // Customer humidity offset in %RH. Clamped; NaN recovers to neutral 0.
  void set_humidity_offset(float offset_pct) {
    humidity_offset_ = sanitise_offset(offset_pct, 10.0f);
  }

  // Customer illuminance multiplier. Ambient-light error is dominated by
  // multiplicative effects (gain, diffuser attenuation, mounting), so a
  // scale factor is the least misleading calibration model. Clamped to
  // [0.2, 5]; NaN or non-positive values recover to neutral 1.
  void set_illuminance_scale(float scale) {
    if (std::isnan(scale) || scale <= 0.0f) {
      illuminance_scale_ = 1.0f;
      return;
    }
    if (scale < 0.2f) scale = 0.2f;
    if (scale > 5.0f) scale = 5.0f;
    illuminance_scale_ = scale;
  }

  float temperature_offset() const { return temperature_offset_; }
  float humidity_offset() const { return humidity_offset_; }
  float illuminance_scale() const { return illuminance_scale_; }

  // --- freshness windows (provisional engineering defaults) -----------------
  void set_climate_warmup_ms(uint32_t ms) { climate_warmup_ms_ = ms; }
  void set_climate_stale_ms(uint32_t ms) { climate_stale_ms_ = ms; }
  void set_lux_warmup_ms(uint32_t ms) { lux_warmup_ms_ = ms; }
  void set_lux_stale_ms(uint32_t ms) { lux_stale_ms_ = ms; }

  // --- comfort thresholds (provisional comfort heuristics — never medical,
  // health or regulatory thresholds) -----------------------------------------
  void set_temperature_bands(float cold, float cool, float warm, float hot) {
    temp_cold_ = cold;
    temp_cool_ = cool;
    temp_warm_ = warm;
    temp_hot_ = hot;
  }
  void set_temperature_hysteresis(float c) {
    temp_hysteresis_ = std::isnan(c) || c < 0.0f ? 0.0f : c;
  }
  void set_humidity_bands(float dry, float humid) {
    humidity_dry_ = dry;
    humidity_humid_ = humid;
  }
  void set_humidity_hysteresis(float pct) {
    humidity_hysteresis_ = std::isnan(pct) || pct < 0.0f ? 0.0f : pct;
  }

  // --- brightness bands (provisional room-ambience categories) --------------
  void set_brightness_bands(float dim, float normal, float bright,
                            float very_bright) {
    lux_dim_ = dim;
    lux_normal_ = normal;
    lux_bright_ = bright;
    lux_very_bright_ = very_bright;
  }
  // Falling margin in percent: a category only drops once lux falls below
  // boundary * (1 - pct/100); rising crosses the plain boundary.
  void set_brightness_hysteresis_pct(float pct) {
    if (std::isnan(pct) || pct < 0.0f) pct = 0.0f;
    if (pct > 90.0f) pct = 90.0f;
    brightness_hysteresis_pct_ = pct;
  }

  // --- darkness service (consumed by the LED framework) ---------------------
  // Dark below the threshold; not-dark above threshold * factor; in
  // between, the previous decision holds. The LED framework passes its
  // customer Darkness Threshold value in at runtime.
  void set_darkness_threshold(float lux) {
    if (!std::isnan(lux) && lux > 0.0f) darkness_threshold_ = lux;
  }
  void set_darkness_hysteresis(float factor) {
    darkness_hysteresis_ = factor < 1.0f ? 1.0f : factor;
  }

  // Explicit persistent fault input. RESERVED: no composed component
  // exposes a supported RoomIQ fault signal today, so production YAML
  // never sets this; the engine contract exists (and is tested) for a
  // future real signal.
  void set_fault(bool fault) { fault_ = fault; }

  // --- lifecycle -------------------------------------------------------------
  // Boot reference for the warm-up windows.
  void begin(uint32_t now_ms) {
    started_ = true;
    start_ms_ = now_ms;
  }

  // --- inputs (real sensor update callbacks) ---------------------------------
  // A NaN sample is an INVALID update: it never refreshes the channel and
  // never becomes a value.
  void input_temperature(uint32_t now_ms, float celsius) {
    ensure_started(now_ms);
    if (std::isnan(celsius)) return;
    temp_raw_ = celsius;
    temp_seen_ = true;
    temp_last_ms_ = now_ms;
  }

  void input_humidity(uint32_t now_ms, float percent) {
    ensure_started(now_ms);
    if (std::isnan(percent)) return;
    humidity_raw_ = percent;
    humidity_seen_ = true;
    humidity_last_ms_ = now_ms;
  }

  void input_lux(uint32_t now_ms, float lux) {
    ensure_started(now_ms);
    if (std::isnan(lux) || lux < 0.0f) return;
    lux_raw_ = lux;
    lux_seen_ = true;
    lux_last_ms_ = now_ms;
  }

  // --- evaluation --------------------------------------------------------------
  void evaluate(uint32_t now_ms) {
    ensure_started(now_ms);

    temp_state_ = channel_state(now_ms, temp_seen_, temp_last_ms_,
                                climate_warmup_ms_, climate_stale_ms_);
    humidity_state_ = channel_state(now_ms, humidity_seen_, humidity_last_ms_,
                                    climate_warmup_ms_, climate_stale_ms_);
    lux_state_ = channel_state(now_ms, lux_seen_, lux_last_ms_,
                               lux_warmup_ms_, lux_stale_ms_);

    update_comfort();
    update_brightness();
    update_darkness();
    update_environment();
    update_health();
  }

  // --- calibrated value outputs ------------------------------------------------
  // NAN unless the channel is fresh: a stale value is never reported as a
  // real value.
  float temperature() const {
    if (temp_state_ != CHANNEL_FRESH) return NAN;
    return temp_raw_ + temperature_offset_;
  }

  float humidity() const {
    if (humidity_state_ != CHANNEL_FRESH) return NAN;
    float value = humidity_raw_ + humidity_offset_;
    if (value < 0.0f) value = 0.0f;
    if (value > 100.0f) value = 100.0f;
    return value;
  }

  float illuminance() const {
    if (lux_state_ != CHANNEL_FRESH) return NAN;
    float value = lux_raw_ * illuminance_scale_;
    return value < 0.0f ? 0.0f : value;
  }

  // Raw (uncalibrated) values for diagnostics only.
  float raw_temperature() const { return temp_seen_ ? temp_raw_ : NAN; }
  float raw_humidity() const { return humidity_seen_ ? humidity_raw_ : NAN; }
  float raw_illuminance() const { return lux_seen_ ? lux_raw_ : NAN; }

  bool temperature_fresh() const { return temp_state_ == CHANNEL_FRESH; }
  bool humidity_fresh() const { return humidity_state_ == CHANNEL_FRESH; }
  bool illuminance_fresh() const { return lux_state_ == CHANNEL_FRESH; }

  // Seconds since the last valid update (diagnostics; NAN if never seen).
  float climate_data_age_s(uint32_t now_ms) const {
    if (!temp_seen_ && !humidity_seen_) return NAN;
    uint32_t age_t = temp_seen_ ? elapsed(temp_last_ms_, now_ms) : 0;
    uint32_t age_h = humidity_seen_ ? elapsed(humidity_last_ms_, now_ms) : 0;
    uint32_t age = age_t > age_h ? age_t : age_h;
    return age / 1000.0f;
  }

  float illuminance_data_age_s(uint32_t now_ms) const {
    if (!lux_seen_) return NAN;
    return elapsed(lux_last_ms_, now_ms) / 1000.0f;
  }

  // --- state outputs -------------------------------------------------------------
  Comfort comfort() const { return comfort_; }
  Brightness brightness() const { return brightness_; }
  Environment environment() const { return environment_; }
  Health health() const { return health_; }
  Darkness darkness() const { return darkness_; }

  // --- legacy compatibility outputs ------------------------------------------------
  // Pre-framework RoomIQ display semantics, preserved so published Home
  // Assistant entity ids keep working — now computed from CALIBRATED
  // values and honest about missing data (NAN / "Unavailable" instead of
  // silently freezing on stale readings; documented semantic upgrade).

  // Heat index ("Feels Like") — simplified Rothfusz regression, valid when
  // temp >= 26.7 °C and humidity >= 40 %; otherwise the temperature.
  float heat_index() const {
    const float t = temperature();
    const float h = humidity();
    if (std::isnan(t) || std::isnan(h)) return NAN;
    if (t < 26.7f || h < 40.0f) return t;
    return -8.784695f + 1.61139411f * t + 2.338549f * h - 0.14611605f * t * h -
           0.012308094f * t * t - 0.016424828f * h * h +
           0.002211732f * t * t * h + 0.00072546f * t * h * h -
           0.000003582f * t * t * h * h;
  }

  // Legacy 0-100 comfort score (kept for compatibility only; the customer
  // surface is the human-friendly Comfort state).
  float legacy_comfort_score() const {
    const float t = temperature();
    const float h = humidity();
    if (std::isnan(t) || std::isnan(h)) return NAN;
    float temp_score = 100.0f;
    if (t < 18.0f) {
      temp_score = 100.0f - (18.0f - t) * 10.0f;
    } else if (t > 26.0f) {
      temp_score = 100.0f - (t - 26.0f) * 10.0f;
    } else if (t < 20.0f || t > 24.0f) {
      temp_score = 90.0f;
    }
    if (temp_score < 0.0f) temp_score = 0.0f;

    float hum_score = 100.0f;
    if (h < 30.0f) {
      hum_score = 100.0f - (30.0f - h) * 2.0f;
    } else if (h > 70.0f) {
      hum_score = 100.0f - (h - 70.0f) * 2.0f;
    } else if (h < 40.0f || h > 60.0f) {
      hum_score = 90.0f;
    }
    if (hum_score < 0.0f) hum_score = 0.0f;

    return temp_score * 0.5f + hum_score * 0.5f;
  }

  const char *legacy_comfort_status() const {
    const float score = legacy_comfort_score();
    if (std::isnan(score)) return "Unavailable";
    if (score >= 90.0f) return "Excellent";
    if (score >= 75.0f) return "Good";
    if (score >= 50.0f) return "Fair";
    if (score >= 25.0f) return "Poor";
    return "Uncomfortable";
  }

  // Legacy light status (4-value vocabulary) mapped from the canonical
  // Brightness category — one threshold implementation, no duplicate.
  const char *legacy_light_status() const {
    switch (brightness_) {
      case BRIGHTNESS_DARK:
        return "Dark";
      case BRIGHTNESS_DIM:
        return "Dim";
      case BRIGHTNESS_NORMAL:
        return "Normal";
      case BRIGHTNESS_BRIGHT:
      case BRIGHTNESS_VERY_BRIGHT:
        return "Bright";
      case BRIGHTNESS_INITIALISING:
      case BRIGHTNESS_UNAVAILABLE:
        break;
    }
    return "Unknown";
  }

  const char *legacy_temperature_advice() const {
    const float t = temperature();
    if (std::isnan(t)) return "Sensor unavailable";
    if (t < 18.0f) return "Too cold - consider heating";
    if (t < 20.0f) return "Slightly cool";
    if (t <= 24.0f) return "Ideal temperature";
    if (t <= 26.0f) return "Slightly warm";
    return "Too warm - consider cooling";
  }

  const char *legacy_humidity_advice() const {
    const float h = humidity();
    if (std::isnan(h)) return "Sensor unavailable";
    if (h < 30.0f) return "Too dry - consider humidifier";
    if (h < 40.0f) return "Slightly dry";
    if (h <= 60.0f) return "Ideal humidity";
    if (h <= 70.0f) return "Slightly humid";
    return "Too humid - consider dehumidifier";
  }

 private:
  // Per-channel freshness state. INIT: no valid data yet, warm-up still
  // running (never a fault). FRESH: valid data inside the stale window.
  // MISSING: warm-up expired with no data, or data went stale — the value
  // is unusable either way.
  enum ChannelState {
    CHANNEL_INIT = 0,
    CHANNEL_FRESH = 1,
    CHANNEL_MISSING = 2,
  };

  static uint32_t elapsed(uint32_t since_ms, uint32_t now_ms) {
    return now_ms - since_ms;  // unsigned arithmetic handles wrap-around
  }

  static float sanitise_offset(float offset, float bound) {
    if (std::isnan(offset)) return 0.0f;  // invalid stored value -> neutral
    if (offset < -bound) return -bound;
    if (offset > bound) return bound;
    return offset;
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

  // Temperature band indices (0 = cold .. 4 = hot) with symmetric
  // hysteresis: leaving the current band requires crossing the boundary by
  // the hysteresis margin, so noise at a boundary never flaps the state.
  int raw_temp_band(float t) const {
    if (t < temp_cold_) return 0;
    if (t < temp_cool_) return 1;
    if (t < temp_warm_) return 2;
    if (t < temp_hot_) return 3;
    return 4;
  }

  float temp_band_lower(int band) const {
    switch (band) {
      case 1:
        return temp_cold_;
      case 2:
        return temp_cool_;
      case 3:
        return temp_warm_;
      case 4:
        return temp_hot_;
    }
    return temp_cold_;
  }

  int raw_humidity_band(float h) const {
    if (h < humidity_dry_) return 0;
    if (h < humidity_humid_) return 1;
    return 2;
  }

  float humidity_band_lower(int band) const {
    return band == 2 ? humidity_humid_ : humidity_dry_;
  }

  void update_comfort() {
    const bool climate_fresh =
        temp_state_ == CHANNEL_FRESH && humidity_state_ == CHANNEL_FRESH;
    if (!climate_fresh) {
      const bool climate_initialising =
          (temp_state_ == CHANNEL_INIT || humidity_state_ == CHANNEL_INIT) &&
          temp_state_ != CHANNEL_MISSING && humidity_state_ != CHANNEL_MISSING;
      comfort_ = climate_initialising ? COMFORT_INITIALISING
                                      : COMFORT_UNAVAILABLE;
      temp_band_valid_ = false;
      humidity_band_valid_ = false;
      return;
    }

    const float t = temperature();
    const float h = humidity();

    // Band classification with hysteresis (state-holding at boundaries).
    const int raw_t = raw_temp_band(t);
    if (!temp_band_valid_) {
      temp_band_ = raw_t;
      temp_band_valid_ = true;
    } else {
      while (raw_t > temp_band_ &&
             t >= temp_band_lower(temp_band_ + 1) + temp_hysteresis_) {
        temp_band_++;
      }
      while (raw_t < temp_band_ &&
             t < temp_band_lower(temp_band_) - temp_hysteresis_) {
        temp_band_--;
      }
    }

    const int raw_h = raw_humidity_band(h);
    if (!humidity_band_valid_) {
      humidity_band_ = raw_h;
      humidity_band_valid_ = true;
    } else {
      while (raw_h > humidity_band_ &&
             h >= humidity_band_lower(humidity_band_ + 1) +
                      humidity_hysteresis_) {
        humidity_band_++;
      }
      while (raw_h < humidity_band_ &&
             h < humidity_band_lower(humidity_band_) - humidity_hysteresis_) {
        humidity_band_--;
      }
    }

    // Documented precedence: combined severe (warm/hot AND humid) >
    // temperature discomfort > humidity discomfort > comfortable.
    if (temp_band_ >= 3 && humidity_band_ == 2) {
      comfort_ = COMFORT_WARM_HUMID;
      return;
    }
    switch (temp_band_) {
      case 0:
        comfort_ = COMFORT_COLD;
        return;
      case 1:
        comfort_ = COMFORT_COOL;
        return;
      case 3:
        comfort_ = COMFORT_WARM;
        return;
      case 4:
        comfort_ = COMFORT_HOT;
        return;
    }
    if (humidity_band_ == 0) {
      comfort_ = COMFORT_DRY;
      return;
    }
    if (humidity_band_ == 2) {
      comfort_ = COMFORT_HUMID;
      return;
    }
    comfort_ = COMFORT_COMFORTABLE;
  }

  int raw_brightness_band(float lux) const {
    if (lux < lux_dim_) return 0;         // Dark
    if (lux < lux_normal_) return 1;      // Dim
    if (lux < lux_bright_) return 2;      // Normal
    if (lux < lux_very_bright_) return 3; // Bright
    return 4;                             // Very bright
  }

  float brightness_band_lower(int band) const {
    switch (band) {
      case 1:
        return lux_dim_;
      case 2:
        return lux_normal_;
      case 3:
        return lux_bright_;
      case 4:
        return lux_very_bright_;
    }
    return lux_dim_;
  }

  void update_brightness() {
    if (lux_state_ == CHANNEL_INIT) {
      brightness_ = BRIGHTNESS_INITIALISING;
      brightness_band_valid_ = false;
      return;
    }
    if (lux_state_ == CHANNEL_MISSING) {
      brightness_ = BRIGHTNESS_UNAVAILABLE;
      brightness_band_valid_ = false;
      return;
    }

    const float lux = illuminance();
    const int raw = raw_brightness_band(lux);
    if (!brightness_band_valid_) {
      brightness_band_ = raw;
      brightness_band_valid_ = true;
    } else if (raw > brightness_band_) {
      // Rising crosses the plain boundary immediately.
      brightness_band_ = raw;
    } else {
      // Falling drops only below boundary * (1 - margin) — hysteresis
      // prevents category flapping near a boundary.
      const float margin = 1.0f - brightness_hysteresis_pct_ / 100.0f;
      while (raw < brightness_band_ &&
             lux < brightness_band_lower(brightness_band_) * margin) {
        brightness_band_--;
      }
    }

    switch (brightness_band_) {
      case 0:
        brightness_ = BRIGHTNESS_DARK;
        return;
      case 1:
        brightness_ = BRIGHTNESS_DIM;
        return;
      case 2:
        brightness_ = BRIGHTNESS_NORMAL;
        return;
      case 3:
        brightness_ = BRIGHTNESS_BRIGHT;
        return;
    }
    brightness_ = BRIGHTNESS_VERY_BRIGHT;
  }

  void update_darkness() {
    if (lux_state_ != CHANNEL_FRESH) {
      darkness_ = DARKNESS_UNKNOWN;
      return;
    }
    const float lux = illuminance();
    const float dark_below = darkness_threshold_;
    const float clear_above = darkness_threshold_ * darkness_hysteresis_;
    switch (darkness_) {
      case DARKNESS_DARK:
        if (lux >= clear_above) darkness_ = DARKNESS_NOT_DARK;
        break;
      case DARKNESS_NOT_DARK:
        if (lux < dark_below) darkness_ = DARKNESS_DARK;
        break;
      case DARKNESS_UNKNOWN:
        darkness_ = lux < dark_below ? DARKNESS_DARK : DARKNESS_NOT_DARK;
        break;
    }
  }

  void update_environment() {
    // Climate available: any discomfort IS the headline; notable light
    // conditions surface only on top of a comfortable climate.
    if (comfort_ != COMFORT_INITIALISING && comfort_ != COMFORT_UNAVAILABLE) {
      switch (comfort_) {
        case COMFORT_COOL:
          environment_ = ENV_COOL;
          return;
        case COMFORT_COLD:
          environment_ = ENV_COLD;
          return;
        case COMFORT_WARM:
          environment_ = ENV_WARM;
          return;
        case COMFORT_HOT:
          environment_ = ENV_HOT;
          return;
        case COMFORT_DRY:
          environment_ = ENV_DRY;
          return;
        case COMFORT_HUMID:
          environment_ = ENV_HUMID;
          return;
        case COMFORT_WARM_HUMID:
          environment_ = ENV_WARM_HUMID;
          return;
        default:
          break;
      }
      if (brightness_ == BRIGHTNESS_DARK) {
        environment_ = ENV_DARK;
        return;
      }
      if (brightness_ == BRIGHTNESS_VERY_BRIGHT) {
        environment_ = ENV_BRIGHT;
        return;
      }
      environment_ = ENV_COMFORTABLE;
      return;
    }

    if (comfort_ == COMFORT_INITIALISING) {
      environment_ = ENV_INITIALISING;
      return;
    }

    // Climate unavailable: a fresh, NOTABLE light condition is still an
    // honest partial headline; anything else is Unavailable — never a
    // fabricated climate statement.
    if (lux_state_ == CHANNEL_FRESH) {
      if (brightness_ == BRIGHTNESS_DARK) {
        environment_ = ENV_DARK;
        return;
      }
      if (brightness_ == BRIGHTNESS_VERY_BRIGHT) {
        environment_ = ENV_BRIGHT;
        return;
      }
    }
    environment_ = ENV_UNAVAILABLE;
  }

  void update_health() {
    if (fault_) {
      health_ = HEALTH_FAULT;
      return;
    }
    const int states[3] = {temp_state_, humidity_state_, lux_state_};
    int fresh = 0, init = 0, missing = 0;
    for (int s : states) {
      if (s == CHANNEL_FRESH) fresh++;
      else if (s == CHANNEL_INIT) init++;
      else missing++;
    }
    if (init > 0 && missing == 0) {
      // Required sensors are still warming up / awaiting first valid data:
      // startup is never reported as a fault or an outage.
      health_ = HEALTH_INITIALISING;
      return;
    }
    if (missing == 0) {
      health_ = HEALTH_AVAILABLE;
      return;
    }
    if (fresh > 0) {
      health_ = HEALTH_DEGRADED;
      return;
    }
    health_ = HEALTH_UNAVAILABLE;
  }

  // calibration (customer-adjustable at runtime; persisted by the YAML
  // number entities, re-applied on every evaluation)
  float temperature_offset_ = 0.0f;
  float humidity_offset_ = 0.0f;
  float illuminance_scale_ = 1.0f;

  // freshness windows (provisional engineering defaults)
  uint32_t climate_warmup_ms_ = 60000;
  uint32_t climate_stale_ms_ = 90000;
  uint32_t lux_warmup_ms_ = 30000;
  uint32_t lux_stale_ms_ = 60000;

  // comfort thresholds (provisional comfort heuristics)
  float temp_cold_ = 16.0f;
  float temp_cool_ = 18.0f;
  float temp_warm_ = 24.0f;
  float temp_hot_ = 27.0f;
  float temp_hysteresis_ = 0.3f;
  float humidity_dry_ = 30.0f;
  float humidity_humid_ = 60.0f;
  float humidity_hysteresis_ = 2.0f;

  // brightness bands (provisional room-ambience categories)
  float lux_dim_ = 10.0f;
  float lux_normal_ = 50.0f;
  float lux_bright_ = 300.0f;
  float lux_very_bright_ = 1000.0f;
  float brightness_hysteresis_pct_ = 20.0f;

  // darkness service (LED semantics preserved)
  float darkness_threshold_ = 20.0f;
  float darkness_hysteresis_ = 1.5f;

  // lifecycle
  bool started_ = false;
  uint32_t start_ms_ = 0;

  // channel data
  float temp_raw_ = NAN;
  bool temp_seen_ = false;
  uint32_t temp_last_ms_ = 0;
  float humidity_raw_ = NAN;
  bool humidity_seen_ = false;
  uint32_t humidity_last_ms_ = 0;
  float lux_raw_ = NAN;
  bool lux_seen_ = false;
  uint32_t lux_last_ms_ = 0;

  // channel states (post-evaluate)
  int temp_state_ = CHANNEL_INIT;
  int humidity_state_ = CHANNEL_INIT;
  int lux_state_ = CHANNEL_INIT;

  // hysteresis band memory
  int temp_band_ = 2;
  bool temp_band_valid_ = false;
  int humidity_band_ = 1;
  bool humidity_band_valid_ = false;
  int brightness_band_ = 2;
  bool brightness_band_valid_ = false;

  // fault (reserved — no production producer)
  bool fault_ = false;

  // outputs
  Comfort comfort_ = COMFORT_INITIALISING;
  Brightness brightness_ = BRIGHTNESS_INITIALISING;
  Environment environment_ = ENV_INITIALISING;
  Health health_ = HEALTH_INITIALISING;
  Darkness darkness_ = DARKNESS_UNKNOWN;
};

// Accessor for the firmware's single engine instance. ESPHome emits
// `esphome: includes:` headers AFTER the globals storage declarations in
// the generated main.cpp, so a custom-class `globals:` entry cannot name
// this type; production lambdas share this function-local static instead
// (constructed on first use). Tests instantiate their own RoomIQEngine
// objects directly.
inline RoomIQEngine &global_engine() {
  static RoomIQEngine engine;
  return engine;
}

}  // namespace roomiq
}  // namespace sense360

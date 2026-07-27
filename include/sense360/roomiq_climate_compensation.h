#pragma once

// ============================================================================
// S360-200-R4-CLIMATE-COMPENSATION-001 — RoomIQ climate compensation (pure)
// ============================================================================
// The ONE implementation of the Sense360 RoomIQ temperature / humidity
// compensation model. It is compiled BOTH into production firmware (via the
// RoomIQ engine, which packages/features/roomiq_framework.yaml includes) and
// into the deterministic native tests
// (tests/unit/test_roomiq_climate_compensation.cpp), so the tested model and
// the shipped model cannot drift.
//
// Deliberately ESPHome-free: no ESPHome headers, no Arduino, no I/O, no
// hidden state beyond the explicit sample pairer below. Hardware
// communication stays the job of ESPHome's built-in `sht4x` / `bmp581_i2c`
// drivers (never forked); Sense360-specific INTERPRETATION lives here, above
// those drivers. That separation is what lets this file later move behind a
// `sense360_roomiq` external component without any behaviour change.
//
// ----------------------------------------------------------------------------
// The model
// ----------------------------------------------------------------------------
// Inputs are the raw SHT45 (U2 @ 0x44) temperature/humidity pair. The BMP581
// (U4 @ 0x47) die temperature is diagnostic ONLY and is never an input here.
//
//   final_temperature_c = raw_temperature_c
//                       + profile.temperature_correction_c
//                       + customer_temperature_offset_c
//
//   svp(T)              = 6.112 * exp((17.62 * T) / (243.12 + T))   [Magnus]
//   actual_vp           = (raw_relative_humidity / 100) * svp(raw_temperature_c)
//   psychrometric_rh    = 100 * actual_vp / svp(final_temperature_c)
//
//   final_humidity      = psychrometric_rh
//                       + profile.humidity_residual_pct
//                       + customer_humidity_offset_pct           (clamped 0-100)
//
// Humidity is therefore NOT a fixed additive fudge: the raw measurement's
// vapour pressure is preserved and relative humidity is recalculated at the
// corrected temperature. That is why the customer TEMPERATURE offset also
// moves relative humidity by a small, scientifically correct amount. Each
// correction is applied EXACTLY ONCE.
//
// Explicitly NOT modelled (accepted scope): no dynamic SHT45/BMP581 delta, no
// ambient-response curve, no startup-correction curve, no runtime external
// reference, and no smoothing added to flatter a comparison metric.
//
// ----------------------------------------------------------------------------
// Evidence posture (read before quoting any number from this file)
// ----------------------------------------------------------------------------
// The S360_200_R4_CLIMATE_PROFILE_V1 constants come from an owner-supplied
// multi-day comparison run against a reference instrument on ONE physical
// S360-200 R4 board (~42 h; reference 21.0-26.9 °C and 45.3-52.6 %RH; daytime
// warming, overnight cooling, restart and settling behaviour included).
//
// That makes the profile a VALIDATED PROVISIONAL profile for the tested
// S360-200 R4 design: strong evidence for the tested board, enclosure and
// operating arrangement. It is NOT proof of unit-to-unit production variation,
// NOT a universal SHT45 correction, and NOT manufacturing, compliance,
// certification, safety or commercial evidence. Multi-unit validation remains
// outstanding. Nothing in this header claims otherwise.
// ============================================================================

#include <cmath>
#include <cstdint>

namespace sense360 {
namespace roomiq {

// ---------------------------------------------------------------------------
// Evidence level of a board climate profile — carried WITH the constants so a
// diagnostic or a document can never quote the numbers without the posture.
// ---------------------------------------------------------------------------
enum ClimateEvidence {
  // No comparison run behind the constants (a placeholder / neutral profile).
  CLIMATE_EVIDENCE_NONE = 0,
  // Multi-day comparison against a reference instrument on ONE physical board
  // of this design. Strong for that board; not multi-unit, not production,
  // not compliance evidence.
  CLIMATE_EVIDENCE_VALIDATED_PROVISIONAL = 1,
};

inline const char *climate_evidence_to_string(ClimateEvidence evidence) {
  switch (evidence) {
    case CLIMATE_EVIDENCE_NONE:
      return "none";
    case CLIMATE_EVIDENCE_VALIDATED_PROVISIONAL:
      return "validated-provisional";
  }
  return "none";
}

// ---------------------------------------------------------------------------
// A named, versioned board climate profile. Constants NEVER appear as bare
// literals in the engine, the YAML or a product: they live here, attached to
// the SKU / revision / evidence level that earned them.
// ---------------------------------------------------------------------------
struct ClimateProfile {
  const char *id;                  // e.g. "S360_200_R4_CLIMATE_PROFILE_V1"
  const char *board_sku;           // e.g. "S360-200"
  const char *board_revision;      // e.g. "R4"
  float temperature_correction_c;  // factory temperature correction (°C)
  float humidity_residual_pct;     // factory humidity residual (percentage pts)
  ClimateEvidence evidence;
};

// The S360-200 (Sense360 RoomIQ) revision R4 profile, version 1.
//
//   factory temperature correction : -5.80 °C
//   factory humidity residual      : +4.52 percentage points RH
//   evidence                       : validated-provisional (one board)
//
// Observed on the tested board over the ~42 h comparison run: temperature mean
// error ~ +0.025 °C, MAE ~ 0.112 °C, 95th-percentile absolute error ~ 0.294 °C;
// humidity mean error ~ -0.014 %RH, MAE ~ 0.237 %RH, 95th-percentile absolute
// error ~ 0.670 %RH. Those are the tested board's numbers, not a production
// specification.
//
// Exposed as a function (not a variable) so the header stays header-only and
// C++11-clean while keeping the requested identifier verbatim.
inline const ClimateProfile &S360_200_R4_CLIMATE_PROFILE_V1() {
  static const ClimateProfile profile = {
      "S360_200_R4_CLIMATE_PROFILE_V1",
      "S360-200",
      "R4",
      -5.80f,
      4.52f,
      CLIMATE_EVIDENCE_VALIDATED_PROVISIONAL,
  };
  return profile;
}

// ---------------------------------------------------------------------------
// Magnus saturation vapour pressure, hPa. NAN for physically impossible
// temperatures (at or below the -243.12 °C pole) rather than a fabricated
// number.
// ---------------------------------------------------------------------------
inline float saturation_vapour_pressure_hpa(float temperature_c) {
  if (!std::isfinite(temperature_c)) return NAN;
  const float denominator = 243.12f + temperature_c;
  if (denominator <= 0.0f) return NAN;
  return 6.112f * std::exp((17.62f * temperature_c) / denominator);
}

// A non-finite customer calibration value (an invalid persisted state) is
// neutral, never a correction.
inline float sanitise_customer_offset(float offset) {
  return std::isfinite(offset) ? offset : 0.0f;
}

// ---------------------------------------------------------------------------
// One fully-resolved compensation result.
//
//   factory_*  : the board profile applied, BEFORE customer calibration —
//                the support diagnostic that separates "what the built-in
//                profile did" from "what the customer added".
//   temperature_c / humidity_pct : the canonical customer values.
// ---------------------------------------------------------------------------
struct ClimateResult {
  bool valid;
  float temperature_c;
  float humidity_pct;
  float factory_temperature_c;
  float factory_humidity_pct;
};

inline ClimateResult invalid_climate_result() {
  ClimateResult result;
  result.valid = false;
  result.temperature_c = NAN;
  result.humidity_pct = NAN;
  result.factory_temperature_c = NAN;
  result.factory_humidity_pct = NAN;
  return result;
}

// Temperature-only path: valid whenever a raw temperature is valid, with no
// humidity sample required (the temperature channel stays independently
// usable).
inline float compensate_temperature_c(const ClimateProfile &profile,
                                      float raw_temperature_c,
                                      float customer_temperature_offset_c) {
  if (!std::isfinite(raw_temperature_c)) return NAN;
  return raw_temperature_c + profile.temperature_correction_c +
         sanitise_customer_offset(customer_temperature_offset_c);
}

inline float clamp_relative_humidity(float humidity_pct) {
  if (!std::isfinite(humidity_pct)) return NAN;
  if (humidity_pct < 0.0f) return 0.0f;
  if (humidity_pct > 100.0f) return 100.0f;
  return humidity_pct;
}

// The full model. `raw_temperature_c` / `raw_humidity_pct` MUST be a coherent
// pair from one physical SHT45 conversion (see ClimateSamplePairer) — feeding
// a humidity value with an unrelated temperature would silently invent a
// vapour pressure.
inline ClimateResult compensate_climate(const ClimateProfile &profile,
                                        float raw_temperature_c,
                                        float raw_humidity_pct,
                                        float customer_temperature_offset_c,
                                        float customer_humidity_offset_pct) {
  if (!std::isfinite(raw_temperature_c) || !std::isfinite(raw_humidity_pct)) {
    return invalid_climate_result();
  }

  const float temperature_offset =
      sanitise_customer_offset(customer_temperature_offset_c);
  const float humidity_offset =
      sanitise_customer_offset(customer_humidity_offset_pct);

  const float factory_temperature_c =
      raw_temperature_c + profile.temperature_correction_c;
  const float final_temperature_c = factory_temperature_c + temperature_offset;

  const float raw_svp = saturation_vapour_pressure_hpa(raw_temperature_c);
  const float factory_svp = saturation_vapour_pressure_hpa(factory_temperature_c);
  const float final_svp = saturation_vapour_pressure_hpa(final_temperature_c);
  if (!std::isfinite(raw_svp) || !std::isfinite(factory_svp) ||
      !std::isfinite(final_svp) || factory_svp <= 0.0f || final_svp <= 0.0f) {
    return invalid_climate_result();
  }

  // Vapour pressure is preserved from the RAW measurement pair; relative
  // humidity is then recalculated at the corrected temperature.
  const float actual_vapour_pressure = (raw_humidity_pct / 100.0f) * raw_svp;

  const float factory_humidity_pct =
      100.0f * actual_vapour_pressure / factory_svp + profile.humidity_residual_pct;
  const float final_humidity_pct =
      100.0f * actual_vapour_pressure / final_svp + profile.humidity_residual_pct +
      humidity_offset;

  ClimateResult result;
  result.valid = true;
  result.temperature_c = final_temperature_c;
  result.humidity_pct = clamp_relative_humidity(final_humidity_pct);
  result.factory_temperature_c = factory_temperature_c;
  result.factory_humidity_pct = clamp_relative_humidity(factory_humidity_pct);
  return result;
}

// ---------------------------------------------------------------------------
// Sample coherence
// ---------------------------------------------------------------------------
// The SHT45 produces temperature AND humidity from ONE physical conversion,
// but ESPHome surfaces them through two separate sensor callbacks. The
// humidity model above is only meaningful on a coherent pair, so the pairing
// rule lives here — one authoritative implementation, shared by the engine and
// the native tests.
//
// Rules:
//   * either callback order is accepted; whichever sample completes the pair
//     forms it;
//   * a sample is only usable when finite — a NaN sample never refreshes
//     anything;
//   * a pair is only accepted when the two sample timestamps are within
//     `max_pair_skew_ms`;
//   * a given (temperature timestamp, humidity timestamp) combination forms a
//     pair at most ONCE, so a repeated callback can never re-freshen humidity
//     from an already-consumed sample;
//   * the pair timestamp is the LATER of the two samples (the conservative
//     choice for freshness);
//   * an unpaired humidity value never marks humidity fresh, while a valid
//     temperature sample stays independently usable.
//
// All timestamp arithmetic is unsigned-millisecond-rollover safe.
// ---------------------------------------------------------------------------

// Default maximum accepted skew between the two halves of one SHT45
// conversion. The two callbacks are emitted microseconds apart inside a single
// `sht4x` poll, so 5 s is generous for a real pair while staying far below the
// 30 s S360-200 R4 polling cycle — an old sample can therefore never pair with
// the next cycle's counterpart.
static const uint32_t DEFAULT_CLIMATE_PAIR_SKEW_MS = 5000;

class ClimateSamplePairer {
 public:
  void set_max_pair_skew_ms(uint32_t ms) { max_pair_skew_ms_ = ms; }
  uint32_t max_pair_skew_ms() const { return max_pair_skew_ms_; }

  // Returns true when this sample completed a NEW coherent pair.
  bool input_temperature(uint32_t now_ms, float celsius) {
    if (!std::isfinite(celsius)) return false;
    temperature_raw_ = celsius;
    temperature_ms_ = now_ms;
    temperature_valid_ = true;
    return try_pair_();
  }

  // Returns true when this sample completed a NEW coherent pair. A humidity
  // sample with no coherent temperature counterpart is retained (it may pair
  // when the counterpart lands) but reports false — it must NOT mark the
  // humidity channel fresh.
  bool input_humidity(uint32_t now_ms, float percent) {
    if (!std::isfinite(percent)) return false;
    humidity_raw_ = percent;
    humidity_ms_ = now_ms;
    humidity_valid_ = true;
    return try_pair_();
  }

  // --- last valid RAW samples (diagnostics stay raw) -----------------------
  bool temperature_valid() const { return temperature_valid_; }
  float raw_temperature() const { return temperature_valid_ ? temperature_raw_ : NAN; }
  uint32_t temperature_ms() const { return temperature_ms_; }

  bool humidity_valid() const { return humidity_valid_; }
  float raw_humidity() const { return humidity_valid_ ? humidity_raw_ : NAN; }
  uint32_t humidity_ms() const { return humidity_ms_; }

  // --- the latest coherent pair --------------------------------------------
  bool pair_valid() const { return pair_valid_; }
  float pair_temperature() const { return pair_valid_ ? pair_temperature_ : NAN; }
  float pair_humidity() const { return pair_valid_ ? pair_humidity_ : NAN; }
  // Timestamp of the later half of the pair.
  uint32_t pair_ms() const { return pair_ms_; }

  // Rollover-safe circular distance between two millisecond timestamps.
  static uint32_t skew_ms(uint32_t a_ms, uint32_t b_ms) {
    const uint32_t forward = a_ms - b_ms;
    const uint32_t backward = b_ms - a_ms;
    return forward < backward ? forward : backward;
  }

  // Rollover-safe "which timestamp is later" (correct while the two are less
  // than ~24.8 days apart, which every pairing decision is by construction).
  static uint32_t later_ms(uint32_t a_ms, uint32_t b_ms) {
    return static_cast<int32_t>(a_ms - b_ms) >= 0 ? a_ms : b_ms;
  }

 private:
  bool try_pair_() {
    if (!temperature_valid_ || !humidity_valid_) return false;
    if (skew_ms(temperature_ms_, humidity_ms_) > max_pair_skew_ms_) return false;
    // Each (temperature, humidity) sample combination pairs at most once.
    if (pair_valid_ && pair_temperature_ms_ == temperature_ms_ &&
        pair_humidity_ms_ == humidity_ms_) {
      return false;
    }
    pair_temperature_ = temperature_raw_;
    pair_humidity_ = humidity_raw_;
    pair_temperature_ms_ = temperature_ms_;
    pair_humidity_ms_ = humidity_ms_;
    pair_ms_ = later_ms(temperature_ms_, humidity_ms_);
    pair_valid_ = true;
    return true;
  }

  uint32_t max_pair_skew_ms_ = DEFAULT_CLIMATE_PAIR_SKEW_MS;

  float temperature_raw_ = NAN;
  uint32_t temperature_ms_ = 0;
  bool temperature_valid_ = false;

  float humidity_raw_ = NAN;
  uint32_t humidity_ms_ = 0;
  bool humidity_valid_ = false;

  float pair_temperature_ = NAN;
  float pair_humidity_ = NAN;
  uint32_t pair_temperature_ms_ = 0;
  uint32_t pair_humidity_ms_ = 0;
  uint32_t pair_ms_ = 0;
  bool pair_valid_ = false;
};

}  // namespace roomiq
}  // namespace sense360

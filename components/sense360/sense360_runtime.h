#pragma once
// ============================================================================
// Sense360 shared runtime contract (SENSE360-CANONICALISATION-001 PR 08)
// ============================================================================
// The one written-down, unit-tested statement of the runtime rules every
// Sense360 logic engine in this directory already follows, and that every
// PR 09..12 domain component must follow. The engines predate this header;
// this header canonicalises their common contract so new code composes with
// them instead of re-inventing (or subtly diverging from) the rules.
//
// THE CONTRACT
// ------------
// 1. One clock. All engine timing is driven by a caller-supplied
//    ``uint32_t now_ms`` millisecond timestamp (ESPHome ``millis()``).
//    Engines never read a clock themselves — that is what makes the native
//    deterministic simulations in tests/unit/ possible.
// 2. Rollover safety. ``millis()`` wraps every ~49.7 days. All interval
//    arithmetic is unsigned 32-bit subtraction (``now - since``), which
//    stays correct across a single wrap. Never compare raw timestamps with
//    ``<`` / ``>``; compare elapsed durations.
// 3. Explicit begin. An engine is inert until ``begin(now_ms)`` seeds its
//    time base. Evaluation before begin must be safe (fail-safe outputs).
// 4. Fail-safe defaults. Missing, stale or not-yet-warmed-up inputs never
//    escalate an output: an unknown input reads as the conservative state
//    (see the AirIQ / blower fail-safe rules).
// 5. Header-only, standard-library-only engines, exercised natively by
//    tests/unit/ and compiled unchanged into production firmware via the
//    ``sense360`` component — one implementation, no drift.
//
// This header provides the shared helpers for rules 1–2 so domain code does
// not hand-roll them. It declares no entities, pins, buses or platforms.
// ============================================================================

#include <cstdint>

namespace sense360 {
namespace runtime {

// Milliseconds elapsed from `since_ms` to `now_ms`, correct across a single
// uint32 millis() wrap (unsigned subtraction).
inline uint32_t elapsed_ms(uint32_t now_ms, uint32_t since_ms) {
  return now_ms - since_ms;
}

// True once at least `interval_ms` has elapsed from `since_ms` to `now_ms`,
// rollover-safe. `interval_ms == 0` is immediately true.
inline bool interval_elapsed(uint32_t now_ms, uint32_t since_ms,
                             uint32_t interval_ms) {
  return elapsed_ms(now_ms, since_ms) >= interval_ms;
}

}  // namespace runtime
}  // namespace sense360

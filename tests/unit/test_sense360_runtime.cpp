// Native deterministic tests for the shared runtime contract helpers
// (components/sense360/sense360_runtime.h) — SENSE360-CANONICALISATION-001
// PR 08. The helpers canonicalise the rollover-safe interval arithmetic the
// engines already use (rule 2 of the runtime contract); these tests pin the
// wrap-around behaviour so the contract cannot silently regress.

#include "../../components/sense360/sense360_runtime.h"

#include <cassert>
#include <cstdint>
#include <cstdio>

using sense360::runtime::elapsed_ms;
using sense360::runtime::interval_elapsed;

static int tests_run = 0;

#define RUN_TEST(fn)                  \
  do {                                \
    fn();                             \
    ++tests_run;                      \
    std::printf("  ok: %s\n", #fn);   \
  } while (0)

static void test_elapsed_simple() {
  assert(elapsed_ms(1000, 0) == 1000);
  assert(elapsed_ms(1000, 1000) == 0);
  assert(elapsed_ms(60000, 250) == 59750);
}

static void test_elapsed_across_rollover() {
  // since just before the uint32 wrap, now just after: unsigned subtraction
  // must report the true short interval, not a ~49.7-day nonsense value.
  const uint32_t max = 0xFFFFFFFFu;
  assert(elapsed_ms(5, max - 4) == 10);
  assert(elapsed_ms(0, max) == 1);
  assert(elapsed_ms(1234, max - 765) == 2000);
}

static void test_interval_elapsed_boundaries() {
  assert(interval_elapsed(1000, 0, 1000));   // exactly reached
  assert(!interval_elapsed(999, 0, 1000));   // one short
  assert(interval_elapsed(1001, 0, 1000));   // past
  assert(interval_elapsed(0, 0, 0));         // zero interval: immediate
}

static void test_interval_elapsed_across_rollover() {
  const uint32_t max = 0xFFFFFFFFu;
  const uint32_t since = max - 500;          // 500 ms before the wrap
  assert(!interval_elapsed(max, since, 1000));       // 500 elapsed
  assert(!interval_elapsed(498, since, 1000));       // 999 elapsed
  assert(interval_elapsed(499, since, 1000));        // exactly 1000
  assert(interval_elapsed(60000, since, 1000));      // long past
}

static void test_matches_engine_idiom() {
  // The blower controller's private elapsed(since, now) == now - since is
  // the pre-existing engine idiom; the shared helper must agree with it on
  // representative values, including a wrap.
  const uint32_t cases[][2] = {
      {0, 0}, {123456, 123000}, {0xFFFFFFF0u, 0x10u}, {5, 0xFFFFFFFBu}};
  for (const auto &c : cases) {
    const uint32_t since = c[0], now = c[1];
    assert(elapsed_ms(now, since) == static_cast<uint32_t>(now - since));
  }
}

int main() {
  std::printf("sense360_runtime contract tests\n");
  RUN_TEST(test_elapsed_simple);
  RUN_TEST(test_elapsed_across_rollover);
  RUN_TEST(test_interval_elapsed_boundaries);
  RUN_TEST(test_interval_elapsed_across_rollover);
  RUN_TEST(test_matches_engine_idiom);
  std::printf("%d tests passed\n", tests_run);
  return 0;
}

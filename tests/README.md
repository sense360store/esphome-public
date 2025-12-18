# ESPHome Test Suite

Comprehensive unit testing for ESPHome firmware logic extracted from YAML configurations.

## Overview

This test suite implements **Phase 1** of the testing strategy, providing:
- ✅ Extracted C++ header files with reusable logic
- ✅ Comprehensive unit tests (150+ test cases)
- ✅ Native C++ compilation and execution
- ✅ Integration examples for ESPHome YAML configs
- ✅ CI/CD ready

## Directory Structure

```
esphome-public/
├── include/                    # C++ header files
│   └── sense360/               # Extracted header files
│       ├── led_logic.h         # LED color mapping, brightness, aggregation
│       ├── calibration.h       # SHT30 temperature/humidity calibration
│       ├── thresholds.h        # Air quality threshold classification
│       └── time_utils.h        # Night mode time calculations
└── tests/
    ├── unit/                   # Unit test files
    │   ├── test_led_logic.cpp
    │   ├── test_calibration.cpp
    │   ├── test_thresholds.cpp
    │   └── test_time_utils.cpp
    ├── esphome/                # ESPHome integration tests
    │   └── test_led_logic.yaml
    ├── Makefile                # Test build system
    ├── README.md               # This file
    └── INTEGRATION_GUIDE.md    # Guide for using headers in YAML
```

## Quick Start

### Prerequisites

- **C++ Compiler**: g++ (C++11 or later)
- **Make**: Build automation tool
- **Git**: For repository access

### Running Tests

```bash
# Navigate to tests directory
cd tests

# Run all tests
make test

# Run specific test
make run_test_led_logic
make run_test_calibration
make run_test_thresholds
make run_test_time_utils

# Quick compile + run
make quick

# Clean build artifacts
make clean

# Show help
make help
```

### Expected Output

```
Running All Tests
=========================================

Running bin/test_led_logic...
Running LED logic tests...
=====================================
[PASS] color_for_severity_good
[PASS] scale_color_half_brightness
[PASS] compute_level_exactly_at_good_threshold
...
=====================================
Results: 36/36 tests passed
✓ bin/test_led_logic PASSED

...

=========================================
All tests passed!
=========================================
```

## Test Coverage

### LED Logic (36 tests)
**File**: `unit/test_led_logic.cpp`
**Header**: `include/sense360/led_logic.h`

- ✅ Color mapping for all severity levels
- ✅ Brightness scaling with clamping
- ✅ Threshold classification (including boundary conditions)
- ✅ PM sensor aggregation
- ✅ Overall severity computation
- ✅ Pulse animation for poor air quality

**Critical Tests**:
- `compute_level_exactly_at_good_threshold` - Catches off-by-one errors
- `scale_color_clamps_negative` - Prevents color overflow
- `aggregate_pm_levels_with_unknown` - Handles NaN sensors

### Calibration Logic (34 tests)
**File**: `unit/test_calibration.cpp`
**Header**: `include/sense360/calibration.h`

- ✅ Single-point offset calibration
- ✅ Clamping to safe ranges (±30°C, ±50%RH)
- ✅ NaN handling
- ✅ Application of calibration offsets
- ✅ Validation of offset ranges
- ✅ Calibration recommendation logic

**Critical Tests**:
- `compute_calibration_clamps_temp_high` - Prevents unsafe offsets
- `apply_humidity_calibration_clamps_at_100` - Ensures physical validity
- `integration_full_calibration_workflow` - End-to-end verification

### Threshold Classification (36 tests)
**File**: `unit/test_thresholds.cpp`
**Header**: `include/sense360/thresholds.h`

- ✅ Classification for all air quality levels
- ✅ Boundary condition testing
- ✅ Real sensor threshold validation (PM2.5, VOC, CO2)
- ✅ Worst-case aggregation
- ✅ Last valid value preservation (CO2 sensor heating)

**Critical Tests**:
- `classify_value_exactly_at_good_threshold` - Boundary precision
- `integration_co2_heating_up_scenario` - Sensor lifecycle handling
- `get_worst_status_four_with_unknowns` - Multi-sensor robustness

### Time Utils (46 tests)
**File**: `unit/test_time_utils.cpp`
**Header**: `include/sense360/time_utils.h`

- ✅ Time conversion (hours/minutes ↔ minutes since midnight)
- ✅ Same-day time range checking
- ✅ **Cross-midnight time range checking** (22:00 → 07:00)
- ✅ Night mode override logic
- ✅ Time validation

**Critical Tests**:
- `is_within_night_mode_cross_midnight_evening` - Midnight wraparound
- `integration_full_24_hour_cycle` - Comprehensive 24-hour validation
- `should_be_night_mode_auto_time_invalid` - Graceful degradation

## Key Features

### 1. Boundary Condition Testing

Many bugs occur at threshold boundaries. Our tests explicitly check:

```cpp
// Value exactly at threshold
TEST_CASE(compute_level_exactly_at_good_threshold) {
  int level = compute_level(10.0f, 10.0f, 25.0f, 50.0f);
  ASSERT_EQ(level, LEVEL_MODERATE);  // NOT GOOD
}
```

### 2. NaN Handling

Sensors return NaN during initialization or errors:

```cpp
TEST_CASE(compute_level_nan) {
  int level = compute_level(NAN, 10.0f, 25.0f, 50.0f);
  ASSERT_EQ(level, LEVEL_UNKNOWN);
}
```

### 3. Cross-Midnight Logic

Night mode often spans midnight (22:00 → 07:00):

```cpp
TEST_CASE(is_within_night_mode_cross_midnight_morning) {
  Time current(6, 0);
  Time start(22, 0);
  Time end(7, 0);
  ASSERT_TRUE(is_within_night_mode(current, start, end));
}
```

### 4. Integration Tests

Simulate real-world scenarios:

```cpp
TEST_CASE(integration_full_calibration_workflow) {
  // 1. Check if calibration needed
  // 2. Compute offsets
  // 3. Validate offsets
  // 4. Apply to new readings
  // 5. Verify correctness
}
```

## Using in ESPHome YAML

Headers can be included directly in ESPHome configurations:

```yaml
esphome:
  name: my-device
  includes:
    - include/sense360/led_logic.h
    - include/sense360/thresholds.h

# Use tested functions
lambda: |-
  using namespace sense360::led;
  int level = compute_level(value, good, moderate, unhealthy);
  Color color = color_for_severity(level);
```

For remote packages, use GitHub URLs:
```yaml
esphome:
  includes:
    - github://sense360store/esphome-public/include/sense360/led_logic.h@main
    - github://sense360store/esphome-public/include/sense360/thresholds.h@main
```

See `INTEGRATION_GUIDE.md` for complete integration instructions.

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test ESPHome Logic
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install dependencies
        run: sudo apt-get install -y build-essential

      - name: Run unit tests
        run: |
          cd tests
          make test

      - name: Validate YAML configs
        uses: esphome/build-action@v1
        with:
          yaml_file: products/*.yaml
```

## Test Metrics

| Metric | Value |
|--------|-------|
| Total Tests | 152 |
| Header Files | 4 |
| Test Files | 4 |
| Lines of Test Code | ~2,500 |
| Code Coverage | ~95% (estimated) |
| Boundary Tests | 24 |
| Integration Tests | 4 |

## Development Workflow

### Adding New Tests

1. **Identify logic** in YAML files that needs testing
2. **Extract to header** in `include/sense360/` directory
3. **Write tests** in `tests/unit/test_*.cpp`
4. **Run tests** with `make test`
5. **Update YAML** to use extracted functions (optional)

### Test-Driven Development

```bash
# 1. Write failing test
vim tests/unit/test_new_feature.cpp

# 2. Implement feature
vim include/sense360/new_feature.h

# 3. Run tests until passing
cd tests && make run_test_new_feature

# 4. Integrate into YAML
vim packages/features/my_feature.yaml
```

## Troubleshooting

### Compilation Errors

```bash
# Check compiler version (need C++11+)
g++ --version

# Verbose compilation
make CXXFLAGS="-std=c++11 -Wall -Wextra -v"
```

### Test Failures

```bash
# Run specific test with debugging
./bin/test_led_logic

# Check assertions
# Tests use assert() which prints line numbers on failure
```

### ESPHome Integration Issues

```bash
# Verify include paths
esphome config your-device.yaml

# Check compilation logs
esphome compile your-device.yaml
```

## Future Enhancements

### Phase 2: Hardware Mocks (Planned)
- Mock sensor frameworks (SEN55, SCD4x, SHT30)
- End-to-end scenario testing
- State machine validation

### Phase 3: CI/CD Pipeline (Planned)
- Automated GitHub Actions workflow
- YAML validation for all configs
- Coverage reporting

### Phase 4: Hardware-in-Loop (Planned)
- Physical test rig
- Automated environmental control
- Regression testing before releases

## Contributing

### Guidelines

1. **Write tests first** (TDD approach)
2. **Test boundaries** - Values exactly at thresholds
3. **Test edge cases** - NaN, negative values, overflow
4. **Document assumptions** - Comment complex test logic
5. **Run all tests** before committing

### Test Template

```cpp
#include "../../include/sense360/my_module.h"
#include <cassert>

TEST_CASE(feature_normal_case) {
  float result = my_function(valid_input);
  ASSERT_NEAR(result, expected_value, 0.01f);
}

TEST_CASE(feature_edge_case) {
  float result = my_function(NAN);
  ASSERT_TRUE(std::isnan(result));
}
```

## Resources

- **ESPHome Documentation**: https://esphome.io
- **C++ Testing Best Practices**: https://google.github.io/googletest/primer.html
- **Integration Guide**: See `INTEGRATION_GUIDE.md`
- **Original Analysis**: See project root for test coverage analysis

## License

This test suite is part of the sense360store/esphome-public repository and follows the same MIT license.

## Questions?

- Check `INTEGRATION_GUIDE.md` for YAML integration
- Run `make help` for available commands
- Review test files for usage examples
- Open an issue on GitHub for bugs or questions

---

**Status**: ✅ Phase 1 Complete
**Test Coverage**: 152 tests across 4 modules
**Last Updated**: 2025-12-03
**Maintained By**: sense360store

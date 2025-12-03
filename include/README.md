# Sense360 C++ Headers

Reusable, tested C++ headers for ESPHome air quality monitoring logic.

## Overview

These headers contain extracted and tested logic from the Sense360 ESPHome firmware. All functions are **fully unit-tested** with 133 passing tests (see `tests/` directory).

## Headers

### `sense360/led_logic.h`

LED color mapping, brightness scaling, and air quality level computation.

**Functions:**
- `color_for_severity()` - Map severity level to RGB color
- `scale_color()` - Scale color by brightness factor
- `compute_level()` - Classify sensor value into severity level
- `brightness_scale_for_level()` - Get brightness multiplier for level
- `compute_pulse_multiplier()` - Pulsing animation for poor air quality
- `aggregate_pm_levels()` - Combine multiple PM sensor readings
- `compute_overall_severity()` - Get worst severity across all sensors

**Test Coverage:** 34 tests

### `sense360/calibration.h`

Temperature and humidity sensor calibration logic (SHT30).

**Functions:**
- `compute_single_point_calibration()` - Calculate offset calibration
- `apply_temperature_calibration()` - Apply offset to temperature reading
- `apply_humidity_calibration()` - Apply offset to humidity reading (with clamping)
- `validate_calibration_offsets()` - Check if offsets are in safe ranges
- `should_calibrate()` - Determine if calibration is needed

**Test Coverage:** 32 tests

### `sense360/thresholds.h`

Air quality threshold classification and sensor state management.

**Functions:**
- `classify_value()` - Classify sensor reading into air quality status
- `status_to_string()` - Convert status enum to human-readable string
- `get_worst_status()` - Find worst status among multiple sensors
- `preserve_last_valid()` - Maintain last valid reading when sensor returns NaN
- `update_last_valid()` - Update last valid value tracker

**Constants:**
- Default thresholds for PM1.0, PM2.5, PM4.0, PM10, VOC, NOx, CO2

**Test Coverage:** 30 tests

### `sense360/time_utils.h`

Night mode time calculations with midnight wraparound support.

**Functions:**
- `is_within_night_mode()` - Check if current time is in night mode range
- `should_be_night_mode()` - Determine night mode with override support
- `minutes_until()` - Calculate minutes until target time
- `is_valid_time()` - Validate time values
- `Time::to_minutes()` - Convert time to minutes since midnight
- `Time::from_minutes()` - Create time from minutes since midnight

**Test Coverage:** 37 tests

## Usage

### In ESPHome Remote Packages

**Recommended for production devices:**

```yaml
esphome:
  name: my-device
  includes:
    - github://sense360store/esphome-public/include/sense360/led_logic.h@v2.0.0
    - github://sense360store/esphome-public/include/sense360/thresholds.h@v2.0.0

packages:
  sense360_firmware:
    url: https://github.com/sense360store/esphome-public
    ref: v2.0.0
    files:
      - products/sense360-mini-airiq.yaml
```

### In Custom Configurations

```yaml
lambda: |-
  using namespace sense360::led;
  using namespace sense360::thresholds;

  // Classify PM2.5 reading
  int level = compute_level(id(pm25_sensor).state,
                           PM25_GOOD,
                           PM25_MODERATE,
                           PM25_UNHEALTHY);

  // Get appropriate color
  Color status_color = color_for_severity(level);

  // Scale brightness based on severity
  float brightness = brightness_scale_for_level(level);

  // Apply to LED
  Color final_color = scale_color(status_color, brightness);
  it[0] = final_color;
```

## Benefits

✅ **Tested** - All functions have comprehensive unit tests
✅ **Reliable** - Handles edge cases (NaN, boundaries, wraparound)
✅ **Maintainable** - Single source of truth for complex logic
✅ **Reusable** - Use in custom configurations without copy-paste
✅ **Remote-ready** - Compatible with ESPHome GitHub packages

## Examples

- **Complete example**: `examples/custom-with-remote-headers.yaml`
- **Test integration**: `tests/esphome/test_led_logic.yaml`
- **Integration guide**: `tests/INTEGRATION_GUIDE.md`

## Testing

All headers are tested with:
- **133 unit tests** (100% passing)
- Boundary condition testing
- NaN and edge case handling
- Integration scenario validation

To run tests:
```bash
cd tests
make test
```

See `tests/README.md` for complete testing documentation.

## Version Compatibility

- **Minimum ESPHome version**: 2025.10.0
- **Platform**: ESP32 (Arduino framework)
- **C++ Standard**: C++11

## API Stability

These headers are considered **stable** as of v2.0.0. Breaking changes will result in a major version bump.

## Documentation

- **Integration Guide**: `tests/INTEGRATION_GUIDE.md`
- **Test Documentation**: `tests/README.md`
- **API Reference**: See inline documentation in each header file

## Support

For questions, issues, or contributions:
- **GitHub Issues**: https://github.com/sense360store/esphome-public/issues
- **Discussions**: https://github.com/sense360store/esphome-public/discussions

## License

MIT License - See repository LICENSE file

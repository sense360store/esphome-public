# Integration Guide: Using Extracted Headers in ESPHome YAML

This guide explains how to integrate the extracted C++ header files into your ESPHome YAML configurations.

## Overview

The test suite extracts complex lambda functions into reusable C++ header files that can be:
1. Unit tested independently
2. Included in ESPHome YAML configurations
3. Maintained in a single location

## Header Files

Located in `tests/include/`:
- `led_logic.h` - LED color mapping, brightness scaling, level computation
- `calibration.h` - SHT30 calibration logic
- `thresholds.h` - Air quality threshold classification
- `time_utils.h` - Night mode time calculations

## Using Headers in YAML

### 1. Include the Header File

Add the header file to your ESPHome configuration:

```yaml
esphome:
  name: my-device
  includes:
    - tests/include/led_logic.h
    - tests/include/thresholds.h
```

### 2. Use Functions in Lambda Expressions

Replace inline lambda logic with function calls:

**Before (inline logic):**
```yaml
lambda: |-
  int level = -1;
  if (value < good_threshold) {
    level = 0;
  } else if (value < moderate_threshold) {
    level = 1;
  } else if (value < unhealthy_threshold) {
    level = 2;
  } else {
    level = 3;
  }
```

**After (using extracted function):**
```yaml
lambda: |-
  using namespace sense360::led;
  int level = compute_level(value, good_threshold, moderate_threshold, unhealthy_threshold);
```

## Example: Updating LED Logic

### Original YAML (features/mini_four_leds_addr.yaml)

```yaml
lambda: |-
  auto color_for = [&](int level) -> Color {
    switch (level) {
      case -1: return Color(24, 32, 64);
      case 0:  return Color(0, 255, 0);
      case 1:  return Color(255, 128, 0);
      case 2:  return Color(255, 0, 0);
      default: return Color(128, 0, 255);
    }
  };

  auto scale_color = [&](Color c, float scale) -> Color {
    return Color(uint8_t(c.red * scale),
                 uint8_t(c.green * scale),
                 uint8_t(c.blue * scale));
  };

  // ... 50+ more lines of logic
```

### Updated YAML (using extracted headers)

```yaml
esphome:
  includes:
    - tests/include/led_logic.h
    - tests/include/thresholds.h

# ... configuration ...

lambda: |-
  using namespace sense360::led;
  using namespace sense360::thresholds;

  // Compute severity levels (tested function)
  int pm_level = compute_level(id(pm_2_5).state,
                                id(g_pm25_good),
                                id(g_pm25_moderate),
                                id(g_pm25_unhealthy));

  int voc_level = compute_level(id(voc_index).state,
                                 id(g_voc_good),
                                 id(g_voc_moderate),
                                 id(g_voc_unhealthy));

  // Get worst severity
  int overall = compute_overall_severity(pm_level, voc_level, nox_level, co2_level);

  // Get color and brightness
  Color base_color = color_for_severity(overall);
  float brightness = brightness_scale_for_level(overall);

  // Apply pulsing for poor air quality
  if (overall == LEVEL_POOR) {
    brightness *= compute_pulse_multiplier(millis());
  }

  // Set LED color
  Color final_color = scale_color(base_color, brightness);
  it[0] = final_color;
```

## Benefits

1. **Testability**: Logic is tested independently before deployment
2. **Maintainability**: Single source of truth for complex logic
3. **Readability**: YAML files are cleaner and easier to understand
4. **Reliability**: Unit tests catch bugs before they reach production

## Migration Strategy

### Phase 1: Keep Both Versions (Recommended)
- Keep original inline logic
- Add extracted header includes
- Use extracted functions in parallel
- Verify identical behavior

### Phase 2: Replace Inline Logic
- Remove inline lambda definitions
- Use extracted functions exclusively
- Run tests to verify correctness

### Phase 3: Optimization
- Remove redundant code
- Simplify YAML structure
- Add documentation

## Testing Integration

After updating YAML files:

1. **Run unit tests**: `cd tests && make test`
2. **Compile ESPHome config**: `esphome config your-device.yaml`
3. **Flash and verify**: Test on actual hardware
4. **Monitor logs**: Check for any runtime issues

## Example: Complete Integration

See `tests/esphome/test_led_logic.yaml` for a complete working example.

## Notes

- **Path Resolution**: Ensure include paths are relative to your ESPHome config directory
- **Namespace**: Always use `using namespace sense360::<module>` to access functions
- **Compatibility**: Headers use standard C++11, compatible with ESP32 Arduino framework
- **Performance**: Inline functions have zero overhead compared to lambda expressions

## Need Help?

- Check unit tests for usage examples
- Review `tests/esphome/test_led_logic.yaml` for integration examples
- Run `make help` in the tests directory for available commands

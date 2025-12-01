# Sense360 Configuration Reference

Complete guide to customizing your Sense360 device.

## Table of Contents

- [Substitution Reference](#substitution-reference)
- [Air Quality Thresholds](#air-quality-thresholds)
- [Product Variants](#product-variants)
- [Custom Automations](#custom-automations)
- [Advanced Configuration](#advanced-configuration)

---

## Substitution Reference

All configurable values in Sense360 firmware use substitutions. You can override any of these in your main config file.

### Required Substitutions

These MUST be defined in your config:

```yaml
substitutions:
  device_name: "your-device-name"      # Unique ID (lowercase, no spaces)
  friendly_name: "Your Device Name"    # Display name in Home Assistant
```

### Hardware Pins (Mini Board)

Default pin assignments (only override if you have custom hardware):

```yaml
substitutions:
  # I2C Bus
  i2c_sda_pin: GPIO48
  i2c_scl_pin: GPIO45

  # LD2450 UART (default presence sensor)
  ld2450_tx_pin: GPIO12
  ld2450_rx_pin: GPIO13
  ld2450_baud: "256000"

  # LEDs
  led_data_pin: GPIO11
  led_count: "4"
  led_chipset: WS2812
  led_rgb_order: GRB

```

If you are using the LD2412 radar, apply these substitutions instead:

```yaml
substitutions:
  # LD2412 UART
  ld2412_tx_pin: GPIO12
  ld2412_rx_pin: GPIO13
  ld2412_baud: "115200"
```

---

## Air Quality Thresholds

Customize when sensors trigger "Good", "Moderate", "Unhealthy", or "Poor" states.

### CO2 (Carbon Dioxide) - ppm

```yaml
substitutions:
  co2_good_limit: "750"        # Below this = Good
  co2_moderate_limit: "950"    # 750-950 = Moderate
  co2_unhealthy_limit: "1400"  # 950-1400 = Unhealthy, >1400 = Poor
```

**Recommendations:**
- **Good**: <800 ppm (excellent indoor air)
- **Moderate**: 800-1000 ppm (acceptable)
- **Unhealthy**: 1000-1400 ppm (ventilation recommended)
- **Poor**: >1400 ppm (immediate action needed)

### PM2.5 (Particulate Matter) - µg/m³

```yaml
substitutions:
  sen55_pm2_5_good_limit: "10"      # WHO guideline
  sen55_pm2_5_moderate_limit: "25"
  sen55_pm2_5_unhealthy_limit: "55"
```

**WHO Guidelines:**
- **Good**: <10 µg/m³ (safe)
- **Moderate**: 10-25 µg/m³ (acceptable short-term)
- **Unhealthy**: 25-55 µg/m³ (sensitive groups affected)
- **Poor**: >55 µg/m³ (everyone affected)

### PM1.0, PM4.0, PM10

```yaml
substitutions:
  # PM1.0
  sen55_pm1_good_limit: "5"
  sen55_pm1_moderate_limit: "12"
  sen55_pm1_unhealthy_limit: "35"
  
  # PM4.0
  sen55_pm4_0_good_limit: "15"
  sen55_pm4_0_moderate_limit: "30"
  sen55_pm4_0_unhealthy_limit: "60"
  
  # PM10
  sen55_pm10_good_limit: "20"
  sen55_pm10_moderate_limit: "50"
  sen55_pm10_unhealthy_limit: "100"
```

### VOC & NOx Indices (0-500 scale)

```yaml
substitutions:
  # VOC (Volatile Organic Compounds)
  sen55_voc_good_limit: "80"
  sen55_voc_moderate_limit: "120"
  sen55_voc_unhealthy_limit: "180"
  
  # NOx (Nitrogen Oxides)
  sen55_nox_good_limit: "80"
  sen55_nox_moderate_limit: "120"
  sen55_nox_unhealthy_limit: "180"
```

**Note**: These are index values (0-500), not concentration measurements.

---

## Product Variants

Choose which product configuration to use:

### Sense360 Mini + AirIQ (Full Features)

```yaml
packages:
  sense360_firmware:
    url: https://github.com/sense360store/esphome-public
    ref: v2.0.0
    files: 
      - products/sense360-mini-airiq.yaml
```

**Includes:**
- ✅ All air quality sensors
- ✅ Presence detection
- ✅ LED indicators
- ✅ Device health monitoring

### Sense360 Mini + Presence Only

```yaml
packages:
  sense360_firmware:
    files: 
      - products/sense360-mini-presence.yaml
```

**Includes:**
- ✅ Presence detection only
- ✅ No air quality sensors
- ✅ Device health monitoring
- Ideal for: Occupancy sensing, lighting automation

### Sense360 Mini + Presence (LD2412)

```yaml
packages:
  sense360_firmware:
    files:
      - products/sense360-mini-presence-ld2412.yaml
```

**Includes:**
- ✅ Presence detection (LD2412 basic profile)
- ✅ LD2412 UART defaults documented in substitutions
- ✅ Device health monitoring
- Ideal for: Occupancy sensing, lighting automation

Note: The LD2412 component does not expose a target count sensor. This basic
profile only adds the supported presence-related binary sensors (the same
applies to the ceiling variant below).

### Sense360 Ceiling + Presence

```yaml
packages:
  sense360_firmware:
    files: 
      - products/sense360-ceiling-presence.yaml
```

**Includes:**
- ✅ Presence detection (Pro profile)
- ✅ Ceiling-specific hardware config
- ✅ Device health monitoring
- Ideal for: Ceiling-mounted installations

### Sense360 Ceiling + Presence (LD2412)

```yaml
packages:
  sense360_firmware:
    files:
      - products/sense360-ceiling-presence-ld2412.yaml
```

**Includes:**
- ✅ Presence detection (LD2412 basic profile)
- ✅ Ceiling-specific hardware config
- ✅ Device health monitoring
- Ideal for: Ceiling-mounted installations with LD2412

---

## Custom Automations

Add custom logic to your Sense360 device.

### Example: High CO2 Alert

Trigger when CO2 exceeds a threshold:

```yaml
binary_sensor:
  - platform: template
    name: "${friendly_name} High CO2 Alert"
    id: high_co2_alert
    device_class: safety
    lambda: |-
      return id(scd4x_co2).state > 1200;
```

### Example: Room Occupancy

Create a simple occupancy sensor:

```yaml
binary_sensor:
  - platform: template
    name: "${friendly_name} Occupied"
    device_class: occupancy
    lambda: |-
      return id(ld2450_zone1_target_count).state > 0;
```

### Example: Air Quality Category

Text sensor showing overall air quality:

```yaml
text_sensor:
  - platform: template
    name: "${friendly_name} Air Quality"
    lambda: |-
      float co2 = id(scd4x_co2).state;
      float pm25 = id(sen55_pm_2_5).state;
      
      if (co2 > 1400 || pm25 > 55) return {"Poor"};
      if (co2 > 950 || pm25 > 25) return {"Unhealthy"};
      if (co2 > 750 || pm25 > 10) return {"Moderate"};
      return {"Good"};
    update_interval: 60s
```

### Example: Ventilation Automation

Trigger external fan based on air quality:

```yaml
switch:
  - platform: template
    name: "${friendly_name} Auto Ventilation"
    id: auto_vent
    optimistic: true
    turn_on_action:
      - logger.log: "Auto ventilation enabled"
    turn_off_action:
      - logger.log: "Auto ventilation disabled"

# Check every minute
interval:
  - interval: 60s
    then:
      - if:
          condition:
            and:
              - switch.is_on: auto_vent
              - lambda: 'return id(scd4x_co2).state > 1000;'
          then:
            - logger.log: "CO2 high - would trigger ventilation"
            # Add your fan control here
```

### Example: Custom LED Pattern

Override LED behavior:

```yaml
light:
  - platform: neopixelbus
    id: status_leds
    # Custom effects
    effects:
      - pulse:
          name: "Alert Pulse"
          update_interval: 1s
      - strobe:
          name: "Warning Strobe"
          colors:
            - state: true
              brightness: 100%
              red: 100%
              green: 0%
              blue: 0%
              duration: 500ms
```

---

## Advanced Configuration

### Mix and Match Components

For advanced users who want specific components only:

```yaml
packages:
  sense360_custom:
    url: https://github.com/sense360store/esphome-public
    ref: v2.0.0
    files:
      # Base (required)
      - base/wifi.yaml
      - base/api_encrypted.yaml
      - base/ota.yaml
      - base/time.yaml
      
      # Choose hardware
      - hardware/sense360_core_mini.yaml

      # Pick features
      # Presence (choose one)
      - features/presence_basic_profile.yaml           # HLK-LD2450
      # - features/presence_basic_profile_ld2412.yaml  # HLK-LD2412
      - features/device_health.yaml
      # Omit features/airiq_mini_profile.yaml for no air quality
    refresh: 1d
```

> **Tip:** Target-count sensors are defined only in the LD2450 profile
> (`features/presence_basic_profile.yaml`). Using the LD2450 profile with
> an LD2412 radar will raise an error like `target_count is an invalid option`
> because that hardware does not expose target-count data.

### Override Sensor Names

Change sensor entity names in Home Assistant:

```yaml
sensor:
  - platform: template
    name: "Living Room CO2"  # Override default name
    lambda: 'return id(scd4x_co2).state;'
    unit_of_measurement: "ppm"
    device_class: carbon_dioxide
```

### Disable Specific Features

Example: Disable Bluetooth proxy:

```yaml
# In your main config, omit or comment out:
# packages:
#   base_bluetooth: !include base/bluetooth_proxy.yaml
```

Or create a custom product config without it.

### Change Update Intervals

Modify how often sensors update:

```yaml
# This would need to be in a custom package override
sensor:
  - platform: scd4x
    # ... existing config ...
    update_interval: 30s  # Default is usually 60s
```

**Note**: Faster updates = more power consumption and wear on sensors.

### WiFi Static IP Configuration

If your network needs static addressing (for example, to avoid repeated reconnect errors), add a `manual_ip` block to the WiFi section of your main config. This overrides the DHCP assignment used in `base/wifi.yaml`.

```yaml
wifi:
  # ... existing config ...
  manual_ip:
    static_ip: 192.168.10.27
    gateway: 192.168.10.1
    subnet: 255.255.255.0
    dns1: 192.168.10.1  # Optional but recommended
```

### WiFi Fallback Configuration

Customize the fallback access point:

```yaml
wifi:
  # ... existing config ...
  ap:
    ssid: "Sense360-Setup"
    password: "MyCustomPassword"
```

---

## Configuration Tips

### 1. Start Simple
Begin with default values, then customize based on your needs.

### 2. Test Changes Incrementally
Change one thing at a time, flash, and verify it works before adding more.

### 3. Document Your Changes
Add comments to your config explaining why you changed values:

```yaml
substitutions:
  # Set lower threshold because bedroom needs better air quality
  co2_good_limit: "600"
```

### 4. Back Up Working Configs
Before major changes, save a copy of your working configuration.

### 5. Use Secrets for Sensitive Data
Never put passwords or keys directly in config files:

```yaml
# Good
api:
  encryption:
    key: !secret api_encryption_key

# Bad - NEVER DO THIS
api:
  encryption:
    key: "abc123def456..."
```

---

## Firmware Version Control

### Stick to Stable Versions

```yaml
packages:
  sense360_firmware:
    ref: v2.0.0  # Specific stable version
```

### Testing Latest Features

```yaml
packages:
  sense360_firmware:
    ref: main  # ⚠️ Latest development version (may be unstable)
```

**Recommendation**: Use version tags (v2.0.0) for production devices.

---

## Common Customization Scenarios

### Home Office
Focus on CO2 for productivity:

```yaml
substitutions:
  co2_good_limit: "600"      # Stricter for focus
  co2_moderate_limit: "800"
```

### Bedroom
Prioritize sleep quality:

```yaml
substitutions:
  co2_good_limit: "600"
  sen55_pm2_5_good_limit: "8"  # Stricter PM limits
```

### Workshop
Focus on VOC and particles from projects:

```yaml
substitutions:
  sen55_voc_good_limit: "60"      # More sensitive
  sen55_pm2_5_good_limit: "8"
```

### Kitchen
Detect cooking-related air quality changes:

```yaml
substitutions:
  sen55_pm2_5_good_limit: "15"    # Expect higher baseline
  sen55_voc_good_limit: "100"     # Cooking creates VOCs
```

---

## Next Steps

- 📖 [Installation Guide](installation.md) - Set up your device
- 🔧 [Troubleshooting](troubleshooting.md) - Fix issues
- 📘 [API Reference](api-reference.md) - Sensor details
- 💬 [Get Support](https://github.com/sense360store/esphome-public/issues) - Ask questions

---

## Need Help?

If you need assistance with configuration:

1. Check [Troubleshooting Guide](troubleshooting.md)
2. Search [GitHub Issues](https://github.com/sense360store/esphome-public/issues)
3. Post your question with:
   - Your config file (remove secrets!)
   - What you're trying to achieve
   - Error messages (if any)

**Support**: support@mysense360.com

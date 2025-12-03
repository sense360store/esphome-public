# Sense360 Configuration Reference

Complete guide to customizing your Sense360 device.

## Table of Contents

- [Basic Configuration](#basic-configuration)
  - [Required Settings](#required-settings)
  - [Product Variants](#product-variants)
  - [Air Quality Thresholds](#air-quality-thresholds)
- [Intermediate Configuration](#intermediate-configuration)
  - [Custom Automations](#custom-automations)
  - [Night Mode and LED Controls](#night-mode-and-led-controls)
- [Advanced Configuration](#advanced-configuration)
  - [Hardware Pin Configuration](#hardware-pin-configuration)
  - [Component-Level Customization](#component-level-customization)
  - [Network Configuration](#network-configuration)

---

## Basic Configuration

### Required Settings

Every Sense360 configuration must include these two values:

```yaml
substitutions:
  device_name: "your-device-name"      # Unique identifier (lowercase, no spaces)
  friendly_name: "Your Device Name"    # Display name in Home Assistant
```

**Example:**
```yaml
substitutions:
  device_name: "sense360-bedroom"
  friendly_name: "Bedroom Sense360"
```

---

### Product Variants

Choose the configuration that matches your device and intended use.

#### Sense360 Mini + AirIQ (Full Features)

Complete air quality monitoring with presence detection (recommended for most users).

```yaml
packages:
  sense360_firmware:
    url: https://github.com/sense360store/esphome-public
    ref: v2.1.0
    files:
      - products/sense360-mini-airiq.yaml
```

**Includes:**
- All air quality sensors
- Presence detection
- LED indicators
- Device health monitoring

#### Sense360 Mini + Presence Only

Presence detection without air quality sensors. Ideal for occupancy sensing and lighting automation.

```yaml
packages:
  sense360_firmware:
    files:
      - products/sense360-mini-presence.yaml
```

#### Sense360 Mini + Presence (LD2412)

Presence detection using the LD2412 sensor. Uses a basic profile that provides presence detection without target counting.

```yaml
packages:
  sense360_firmware:
    files:
      - products/sense360-mini-presence-ld2412.yaml
```

Note: The LD2412 component does not provide target count sensors. It provides only presence-related binary sensors.

#### Sense360 Ceiling + Presence

Ceiling-mounted presence detection with the standard LD2450 sensor.

```yaml
packages:
  sense360_firmware:
    files:
      - products/sense360-ceiling-presence.yaml
```

#### Sense360 Ceiling + Presence (LD2412)

Ceiling-mounted presence detection using the LD2412 sensor.

```yaml
packages:
  sense360_firmware:
    files:
      - products/sense360-ceiling-presence-ld2412.yaml
```

---

### Air Quality Thresholds

Customize when your device indicates good, moderate, or unhealthy air quality. The device uses four levels indicated by bar symbols in the interface.

#### CO2 (Carbon Dioxide) - Measured in ppm

```yaml
substitutions:
  co2_good_limit: "750"        # Below this = excellent
  co2_moderate_limit: "950"    # 750-950 = acceptable
  co2_unhealthy_limit: "1400"  # 950-1400 = needs ventilation, above 1400 = urgent
```

**Recommended values:**
- Excellent: Below 800 ppm
- Acceptable: 800-1000 ppm
- Needs ventilation: 1000-1400 ppm
- Urgent action needed: Above 1400 ppm

#### PM2.5 (Fine Particulate Matter) - Measured in µg/m³

```yaml
substitutions:
  sen55_pm2_5_good_limit: "10"      # WHO guideline
  sen55_pm2_5_moderate_limit: "25"
  sen55_pm2_5_unhealthy_limit: "55"
```

**WHO Guidelines:**
- Safe: Below 10 µg/m³
- Acceptable short-term: 10-25 µg/m³
- Sensitive groups affected: 25-55 µg/m³
- Everyone affected: Above 55 µg/m³

#### Other Particulate Matter (PM1.0, PM4.0, PM10)

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

#### VOC and NOx Indices (Scale 0-500)

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

Note: These are index values (0-500), not direct concentration measurements.

---

### Common Threshold Scenarios

#### Home Office

Focus on CO2 levels for productivity:

```yaml
substitutions:
  co2_good_limit: "600"      # Stricter for better focus
  co2_moderate_limit: "800"
```

#### Bedroom

Prioritize sleep quality with stricter limits:

```yaml
substitutions:
  co2_good_limit: "600"
  sen55_pm2_5_good_limit: "8"
```

#### Workshop

More sensitive to VOCs and particles from projects:

```yaml
substitutions:
  sen55_voc_good_limit: "60"
  sen55_pm2_5_good_limit: "8"
```

#### Kitchen

Expect higher baseline due to cooking:

```yaml
substitutions:
  sen55_pm2_5_good_limit: "15"
  sen55_voc_good_limit: "100"
```

---

## Intermediate Configuration

### Custom Automations

Add custom logic to your Sense360 device.

#### High CO2 Alert

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

#### Room Occupancy Sensor

Create a simple occupancy indicator:

```yaml
binary_sensor:
  - platform: template
    name: "${friendly_name} Occupied"
    device_class: occupancy
    lambda: |-
      return id(ld2450_zone1_target_count).state > 0;
```

#### Air Quality Text Sensor

Display overall air quality status:

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

#### Ventilation Control

Trigger external fan based on air quality (requires additional hardware):

```yaml
switch:
  - platform: template
    name: "${friendly_name} Auto Ventilation"
    id: auto_vent
    optimistic: true

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

---

### Night Mode and LED Controls

#### Mini Night Brightness

The Mini LED package stores night brightness as a persisted value that survives reboots. You can adjust it through Home Assistant.

The `Night Brightness` number entity controls the LED brightness during night mode. If you previously set `night_brightness` in substitutions, that value serves as the default, but the number entity is the active control.

#### Night Light Feature

Enable the `Night Light` switch to activate a dim white night-light when presence is detected. The light turns off after the `Night Inactivity Timeout` (measured in seconds) elapses with no motion.

The `Night Mode` switch controls when LEDs dim. The night-light feature works only when night mode is active, so daytime LED behavior remains unchanged.

#### LD2412 Presence Behavior

When using LD2412 packages, the presence-driven LED behaviors (night-light activation and inactivity shutoff) follow the LD2412 `presence_occupied` state, matching the experience of the LD2450 but without target counts.

#### PM LED Logic

The PM LED displays the worst severity across PM1.0, PM2.5, PM4.0, and PM10. Even if fine dust levels are acceptable, coarse particles can raise the PM indicator.

New text sensors provide the LED mode, most valuable pollutant information (name and severity), and human-friendly particulate status strings alongside the existing VOC, NOx, and CO2 status displays.

---

## Advanced Configuration

This section is for users with technical knowledge of ESPHome and the firmware architecture.

### Hardware Pin Configuration

#### Mini Board Default Pins

Only modify these if you have custom hardware:

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

#### LD2412 Pin Configuration

If using the LD2412 radar:

```yaml
substitutions:
  # LD2412 UART
  ld2412_tx_pin: GPIO12
  ld2412_rx_pin: GPIO13
  ld2412_baud: "115200"
```

---

### Component-Level Customization

For advanced users who want to load specific components only:

```yaml
packages:
  sense360_custom:
    url: https://github.com/sense360store/esphome-public
    ref: v2.1.0
    files:
      # Base (required)
      - base/wifi.yaml
      - base/api_encrypted.yaml
      - base/ota.yaml
      - base/time.yaml

      # Choose hardware
      - hardware/sense360_core_mini.yaml

      # Select features
      # Presence (choose one)
      - features/presence_basic_profile.yaml           # HLK-LD2450
      # - features/presence_basic_profile_ld2412.yaml  # HLK-LD2412
      - features/device_health.yaml
      # Omit features/airiq_mini_profile.yaml if air quality is not needed
    refresh: 1d
```

**Important:** Target-count sensors are defined only in the LD2450 profile (`features/presence_basic_profile.yaml`). Using the LD2450 profile with an LD2412 radar will cause an error because the LD2412 hardware does not provide target-count data.

---

### Network Configuration

#### Static IP Address

If your network requires static IP addressing:

```yaml
wifi:
  # ... existing config ...
  manual_ip:
    static_ip: 192.168.10.27
    gateway: 192.168.10.1
    subnet: 255.255.255.0
    dns1: 192.168.10.1  # Optional but recommended
```

#### Fallback Access Point

Customize the fallback access point that activates if WiFi connection fails:

```yaml
wifi:
  # ... existing config ...
  ap:
    ssid: "Sense360-Setup"
    password: "MyCustomPassword"
```

---

### Custom LED Patterns

Override LED behavior with custom effects:

```yaml
light:
  - platform: neopixelbus
    id: status_leds
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

### Sensor Update Intervals

Modify how frequently sensors update (requires custom package override):

```yaml
sensor:
  - platform: scd4x
    # ... existing config ...
    update_interval: 30s  # Default is usually 60s
```

**Warning:** Faster updates increase power consumption and may reduce sensor lifespan.

---

### Override Sensor Names

Change how sensor entities appear in Home Assistant:

```yaml
sensor:
  - platform: template
    name: "Living Room CO2"  # Custom name
    lambda: 'return id(scd4x_co2).state;'
    unit_of_measurement: "ppm"
    device_class: carbon_dioxide
```

---

## Configuration Best Practices

### Start Simple

Begin with default values and customize based on your specific needs after observing device behavior.

### Test Changes Incrementally

Change one setting at a time, flash the device, and verify it works before making additional changes.

### Document Your Changes

Add comments to your configuration explaining why you changed values:

```yaml
substitutions:
  # Lower threshold because bedroom needs better air quality for sleep
  co2_good_limit: "600"
```

### Back Up Working Configurations

Before making major changes, save a copy of your current working configuration.

### Use Secrets for Sensitive Data

Never put passwords or encryption keys directly in configuration files:

```yaml
# Correct approach
api:
  encryption:
    key: !secret api_encryption_key

# Incorrect - NEVER DO THIS
api:
  encryption:
    key: "abc123def456..."
```

---

## Firmware Version Control

### Stable Versions (Recommended)

Use specific version tags for production devices:

```yaml
packages:
  sense360_firmware:
    ref: v2.1.0  # Specific stable version
```

### Development Versions

Test the latest features (may be unstable):

```yaml
packages:
  sense360_firmware:
    ref: main  # Latest development version - use with caution
```

**Recommendation:** Always use version tags (such as v2.1.0) for devices in regular use.

---

## Need Help?

If you need assistance with configuration:

1. Review the [Installation Guide](installation.md)
2. Search [GitHub Issues](https://github.com/sense360store/esphome-public/issues)
3. Create a new issue with:
   - Your configuration file (remove secrets)
   - What you are trying to achieve
   - Any error messages

**Support**: support@mysense360.com

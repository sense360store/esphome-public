# Sense360 Installation Guide

Complete instructions for setting up your Sense360 device with ESPHome.

## Before You Begin

Ensure you have the following items ready:

- Sense360 device (purchased from [mysense360.com](https://mysense360.com))
- Home Assistant with ESPHome add-on installed (recommended), OR standalone ESPHome installation
- USB-C cable that supports data transfer (not just charging)
- WiFi network using 2.4GHz frequency (5GHz is not supported)
- Computer with Chrome, Edge, or Opera browser

## Installation Steps Overview

1. Prepare configuration file
2. Configure secrets
3. Initial USB flash
4. Verify connection
5. Set up wireless updates (optional)

Estimated time: 15-20 minutes for first device

---

## Step 1: Prepare Your Configuration

### Option A: Using Home Assistant ESPHome Dashboard (Recommended)

1. **Open ESPHome Dashboard**
   - In Home Assistant, navigate to Settings, then Add-ons
   - Open the ESPHome dashboard

2. **Create New Device**
   - Click "New Device"
   - Click "Skip this step" (you will use the provided template instead)
   - Enter a name such as `sense360-living-room` or choose your own room name

3. **Edit Configuration**
   - Click "Edit" on your newly created device
   - Delete all default content
   - Copy and paste this template:

```yaml
# Sense360 Configuration
substitutions:
  device_name: sense360-living-room  # Change this
  friendly_name: "Living Room Sense360"  # Change this

esphome:
  name: ${device_name}
  friendly_name: ${friendly_name}
  min_version: 2025.10.0

packages:
  sense360_firmware:
    url: https://github.com/sense360store/esphome-public
    ref: v2.2.0
    files:
      - products/sense360-mini-airiq.yaml
    refresh: 1d

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_encryption_key

ota:
  - platform: esphome
    password: !secret ota_password
```

4. **Customize Device Name**
   - Change `device_name` to match your device (use lowercase letters with no spaces)
   - Change `friendly_name` to your preferred display name
   - Click "Save"

### Option B: Using Standalone ESPHome

1. Create a file named `sense360-living-room.yaml` in your ESPHome configuration directory
2. Copy the template shown above into the file
3. Customize the device names as needed
4. Save the file

---

## Step 2: Configure Secrets

Secrets keep your sensitive information secure and separate from your main configuration.

### In Home Assistant ESPHome

1. Click the "Secrets" button in the top right of the ESPHome dashboard
2. Add these lines if they are not already present:

```yaml
# WiFi Credentials
wifi_ssid: "YourNetworkName"
wifi_password: "YourWiFiPassword"

# API Encryption Key (will be generated in next step)
api_encryption_key: "WILL_BE_GENERATED"

# OTA Password
ota_password: "ChooseASecurePassword123"

# MQTT Credentials (required for AirIQ MQTT publishing)
mqtt_username: "YourMQTTUsername"
mqtt_password: "YourMQTTPassword"
```

3. Update the WiFi credentials with your actual network name and password
4. Set a secure OTA password
5. Add MQTT credentials if you are using an AirIQ-enabled product (required for air quality MQTT publishing)
6. Leave the API key as-is for now (it will be generated automatically)
6. Click "Save"

### Generate API Encryption Key

1. Return to your device in the ESPHome dashboard
2. Click the "Install" button
3. ESPHome will detect the missing API key and offer to generate one
4. Click "Generate encryption key"
5. Copy the generated key
6. Go back to "Secrets" and paste it as the value for `api_encryption_key`
7. Save the secrets file

---

## Step 3: Initial Flash via USB

The first time you flash your Sense360 device, it must be done via USB connection. After this initial setup, all future updates can be done wirelessly.

### Connect Device

1. Plug your Sense360 device into your computer using a USB-C cable
2. Wait a few seconds for the device to be recognized by your computer

### Flash Firmware

**In Home Assistant ESPHome:**

1. Click "Install" on your device
2. Select "Plug into this computer"
3. Your browser will display available serial ports
4. Select your Sense360 device (usually labeled as "USB Serial" or similar)
5. Click "Connect"
6. ESPHome will now:
   - Download firmware from GitHub
   - Compile the firmware
   - Flash it to your device
   - This process takes 3-5 minutes

7. Monitor the logs for these messages:
   ```
   INFO Successfully compiled program
   INFO Connecting to device...
   INFO Uploading...
   INFO Upload successful
   ```

### Troubleshooting Flash Issues

**Device not appearing in browser?**
- Verify that your USB cable supports data transfer (not just power)
- Try a different USB port on your computer
- Install CP210x or CH340 drivers depending on your board
- If your device has a BOOT button, hold it while connecting

**Compilation failed?**
- Check your internet connection (GitHub packages must be downloaded)
- Verify that secrets.yaml contains all required keys
- Try again (GitHub may temporarily rate-limit requests)

**Upload failed?**
- Try a different USB cable
- Check that the USB port connection is secure
- Restart the ESPHome dashboard
- Power cycle the device by unplugging and reconnecting it

---

## Step 4: Verify Connection

### Check Device Status

After successful flash:

1. The device will reboot automatically
2. Watch the logs in ESPHome for these messages:
   ```
   INFO WiFi: Connecting...
   INFO WiFi: Connected
   INFO Home Assistant API: Connected
   ```

3. In the ESPHome dashboard, the device should show "Online" with a green indicator

### Add to Home Assistant

If using Home Assistant:

1. You should see a notification about a new device being discovered
2. Click "Check it out"
3. Click "Configure"
4. The device will be added automatically
5. Navigate to Settings, then Devices and Services, then ESPHome
6. Your Sense360 device should be listed

### Verify Sensors

1. Open your device page in Home Assistant
2. You should see multiple sensors including:
   - CO2 (measured in ppm)
   - PM2.5 (measured in µg/m³)
   - VOC Index
   - NOx Index
   - Temperature
   - Humidity
   - And additional sensors

3. Wait 2-3 minutes for sensors to initialize
4. Values should begin appearing

Note: Some sensors such as CO2 may require additional time to stabilize and provide accurate readings.

---

## Step 5: Wireless Updates (Future)

After the initial USB flash, all future updates can be done wirelessly.

### To Update Firmware:

1. **Check for new version**:
   - Visit the [Releases](https://github.com/sense360store/esphome-public/releases) page
   - Review the changelog for new features and fixes

2. **Update your configuration**:
   ```yaml
   packages:
     sense360_firmware:
       ref: v2.2.0  # Change to the new version number
   ```

3. **Flash wirelessly**:
   - Click "Install" in ESPHome
   - Select "Wirelessly"
   - The device will update in approximately 1 minute

---

## Advanced Configuration

### Change Product Variant

Edit your configuration to use a different product:

```yaml
packages:
  sense360_firmware:
    files:
      # Choose ONE:
      - products/sense360-mini-airiq.yaml     # Full sensors
      # - products/sense360-mini-presence.yaml  # Presence only
      # - products/sense360-ceiling-presence.yaml  # Ceiling mount
```

### Override Thresholds

Add custom thresholds to your substitutions section:

```yaml
substitutions:
  device_name: my-sense360
  friendly_name: "My Sense360"

  # Custom thresholds
  co2_good_limit: "800"
  co2_moderate_limit: "1000"
  sen55_pm2_5_good_limit: "12"
```

### Add Custom Automations

Add custom logic at the end of your configuration file:

```yaml
# Custom high CO2 alert
binary_sensor:
  - platform: template
    name: "High CO2 Alert"
    lambda: |-
      return id(scd4x_co2).state > 1200;
```

---

## Multiple Devices

To add more Sense360 devices:

1. Repeat the installation process for each device
2. Use unique device names for each one:
   - `sense360-living-room`
   - `sense360-bedroom`
   - `sense360-office`
3. All devices can use the same `secrets.yaml` file
4. Flash each device via USB once, then maintain wirelessly

---

## Backup Your Configuration

Important: Back up these files regularly:

- Your device configuration files (such as `sense360-*.yaml`)
- Your `secrets.yaml` file

Store backups securely, ideally in an encrypted format.

---

## Next Steps

- [Configuration Guide](configuration.md) - Learn how to customize your device
- [GitHub Issues](https://github.com/sense360store/esphome-public/issues) - Report problems or ask questions

---

## Quick Reference

### ESPHome Commands

```bash
# Validate config
esphome config sense360-living-room.yaml

# Compile only
esphome compile sense360-living-room.yaml

# Flash via USB
esphome run sense360-living-room.yaml

# View logs
esphome logs sense360-living-room.yaml
```

### File Locations

- **Home Assistant Add-on**: `/config/esphome/`
- **Standalone ESPHome**: `~/.esphome/` or your chosen directory

### Support

- Email: support@mysense360.com
- Issues: [GitHub](https://github.com/sense360store/esphome-public/issues)
- Documentation: [Full Documentation](https://github.com/sense360store/esphome-public/tree/main/docs)

---

**Your Sense360 device is now set up and monitoring your environment.**

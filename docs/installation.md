# Sense360 Installation Guide

Complete step-by-step guide to set up your Sense360 device with ESPHome.

## Prerequisites

Before you begin, ensure you have:

- ✅ **Sense360 device** (purchased from [mysense360.com](https://mysense360.com))
- ✅ **Home Assistant** with ESPHome add-on installed (recommended)
  - OR standalone ESPHome installation
- ✅ **USB-C cable** for initial flash (must support data, not just charging)
- ✅ **WiFi network** (2.4GHz - 5GHz is not supported)
- ✅ **Computer** with Chrome, Edge, or Opera browser

## Installation Overview

1. Prepare configuration file
2. Configure secrets
3. Initial USB flash
4. Verify connection
5. (Optional) Wireless updates

**Estimated Time**: 15-20 minutes for first device

---

## Step 1: Prepare Your Configuration

### Option A: Using Home Assistant ESPHome Dashboard (Recommended)

1. **Open ESPHome Dashboard**
   - In Home Assistant, go to **Settings** → **Add-ons**
   - Open **ESPHome** dashboard

2. **Create New Device**
   - Click **"+ New Device"**
   - Click **"Skip this step"** (we'll use our template)
   - Name it: `sense360-living-room` (or your room name)

3. **Edit Configuration**
   - Click **"Edit"** on your new device
   - **Delete** all default content
   - **Copy and paste** this template:

```yaml
# Sense360 Configuration
substitutions:
  device_name: sense360-living-room  # CHANGE THIS
  friendly_name: "Living Room Sense360"  # CHANGE THIS

esphome:
  name: ${device_name}
  friendly_name: ${friendly_name}
  min_version: 2025.10.0

packages:
  sense360_firmware:
    url: https://github.com/sense360store/esphome-public
    ref: v1.1.7
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
   - Change `device_name` to match your device (lowercase, no spaces)
   - Change `friendly_name` to your preferred display name
   - Click **"Save"**

### Option B: Using Standalone ESPHome

1. Create a file `sense360-living-room.yaml` in your ESPHome config directory
2. Copy the template above into the file
3. Customize device names
4. Save the file

---

## Step 2: Configure Secrets

Secrets keep your sensitive information secure and out of your main configuration.

### In Home Assistant ESPHome

1. Click **"Secrets"** button (top right of ESPHome dashboard)
2. Add these lines (if not already present):

```yaml
# WiFi Credentials
wifi_ssid: "YourNetworkName"
wifi_password: "YourWiFiPassword"

# API Encryption Key (we'll generate this next)
api_encryption_key: "WILL_BE_GENERATED"

# OTA Password
ota_password: "ChooseASecurePassword123!"
```

3. **Update WiFi credentials** with your actual network name and password
4. **Set OTA password** (choose something secure)
5. **Leave API key as-is** for now (we'll generate it)
6. Click **"Save"**

### Generate API Encryption Key

1. Go back to your device in ESPHome dashboard
2. Click **"Install"** button
3. ESPHome will detect missing API key and offer to generate one
4. Click **"Generate encryption key"**
5. **Copy** the generated key
6. Go back to **"Secrets"** and **paste** it for `api_encryption_key`
7. **Save** secrets

---

## Step 3: Initial Flash via USB

The first time you flash your Sense360, it must be done via USB. After that, all updates are wireless!

### 3.1 Connect Device

1. **Plug in** your Sense360 device via USB-C cable to your computer
2. **Wait** a few seconds for the device to be recognized

### 3.2 Flash Firmware

**In Home Assistant ESPHome:**

1. Click **"Install"** on your device
2. Select **"Plug into this computer"**
3. Browser will show available serial ports
4. **Select** your Sense360 device (usually shows as "USB Serial" or similar)
5. Click **"Connect"**
6. ESPHome will:
   - Download firmware from GitHub
   - Compile it
   - Flash to device
   - **This takes 3-5 minutes** - be patient!

7. Watch the logs for:
   ```
   INFO Successfully compiled program
   INFO Connecting to device...
   INFO Uploading...
   INFO Upload successful
   ```

### 3.3 Troubleshooting Flash Issues

**Device not showing in browser?**
- Ensure USB cable supports data (not just charging)
- Try a different USB port
- Install CP210x or CH340 drivers (depends on your board)
- Hold BOOT button while connecting (if device has one)

**Compilation failed?**
- Check internet connection (needs to fetch packages)
- Verify secrets.yaml has all required keys
- Try again (sometimes GitHub rate limits)

**Upload failed?**
- Try a different USB cable
- Check USB port isn't loose
- Restart ESPHome dashboard
- Power cycle the device

---

## Step 4: Verify Connection

### 4.1 Check Device Status

After successful flash:

1. Device will **reboot** automatically
2. **Watch the logs** in ESPHome (should show):
   ```
   INFO WiFi: Connecting...
   INFO WiFi: Connected
   INFO Home Assistant API: Connected
   ```

3. In ESPHome dashboard, device should show **"Online"** (green dot)

### 4.2 Add to Home Assistant

If using Home Assistant:

1. You should see a **notification** about new device discovered
2. Click **"Check it out"**
3. Click **"Configure"**
4. Device will be added automatically
5. Check **Settings** → **Devices & Services** → **ESPHome**
6. Your Sense360 should be listed

### 4.3 Verify Sensors

1. Go to your device page in Home Assistant
2. You should see many sensors:
   - CO2 (ppm)
   - PM2.5 (µg/m³)
   - VOC Index
   - NOx Index
   - Temperature
   - Humidity
   - And more!

3. **Wait 2-3 minutes** for sensors to initialize
4. Values should start appearing

**Note**: Some sensors (like CO2) may take longer to stabilize.

---

## Step 5: Wireless Updates (Future)

After initial USB flash, ALL future updates are wireless! 🎉

### To Update Firmware:

1. **Check for new version**:
   - Visit [Releases](https://github.com/sense360store/esphome-public/releases)
   - See what's new

2. **Update your config**:
   ```yaml
   packages:
     sense360_firmware:
       ref: v1.1.7  # Change from v1.0.0 to new version
   ```

3. **Flash wirelessly**:
   - Click **"Install"** in ESPHome
   - Select **"Wirelessly"**
   - Device updates in ~1 minute!

---

## Advanced Configuration

### Change Product Variant

Edit your config to use different product:

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

Add to your substitutions:

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

Add at the end of your config:

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

1. Repeat installation for each device
2. Use **unique device names**:
   - `sense360-living-room`
   - `sense360-bedroom`
   - `sense360-office`
3. All can use same `secrets.yaml`
4. Flash each device via USB once, then maintain wirelessly

---

## Backup Your Configuration

**Important**: Back up these files regularly:

- ✅ `sense360-*.yaml` (your device configs)
- ✅ `secrets.yaml` (your credentials)

Store securely, ideally encrypted backup.

---

## Next Steps

- 📖 [Configuration Guide](configuration.md) - Customize your device
- 🔧 [Troubleshooting](troubleshooting.md) - Fix common issues
- 💬 [Get Support](https://github.com/sense360store/esphome-public/issues) - Ask questions

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

- 📧 Email: support@mysense360.com
- 💬 Issues: [GitHub](https://github.com/sense360store/esphome-public/issues)
- 📖 Docs: [Full Documentation](https://github.com/sense360store/esphome-public/tree/main/docs)

---

**Congratulations! Your Sense360 is now set up and monitoring your environment! 🎉**
